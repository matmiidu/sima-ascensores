from datetime import date

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from cartera.models import Tecnico
from config.permisos import LecturaOJefe, es_jefe, tecnico_de

from .calendario import CalendarioError, cobertura, dias_habiles, generar_calendario
from .models import Feriado, GeneracionCalendario, Visita
from .serializers import (
    FeriadoSerializer,
    GenerarSerializer,
    GeneracionSerializer,
    VisitaDelDiaSerializer,
    VisitaSerializer,
)


def _mes_param(request):
    """Lee ?mes=AAAA-MM; si falta, usa el mes actual."""
    valor = request.query_params.get("mes")
    if not valor:
        hoy = date.today()
        return hoy.year, hoy.month
    try:
        anio, mes = (int(x) for x in valor.split("-"))
        date(anio, mes, 1)
    except ValueError:
        raise CalendarioError("El parámetro mes debe tener la forma AAAA-MM.")
    return anio, mes


class VisitaViewSet(viewsets.ModelViewSet):
    serializer_class = VisitaSerializer
    permission_classes = [LecturaOJefe]

    def get_queryset(self):
        qs = Visita.objects.select_related("ascensor", "ascensor__edificio", "tecnico")
        if "mes" in self.request.query_params:
            anio, mes = _mes_param(self.request)
            qs = qs.filter(mes=date(anio, mes, 1))
        tecnico = self.request.query_params.get("tecnico")
        if tecnico:
            qs = qs.filter(tecnico_id=tecnico)
        fecha = self.request.query_params.get("fecha")
        if fecha:
            qs = qs.filter(fecha=fecha)
        return qs

    def handle_exception(self, exc):
        if isinstance(exc, CalendarioError):
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)


class FeriadoViewSet(viewsets.ModelViewSet):
    queryset = Feriado.objects.all()
    serializer_class = FeriadoSerializer
    permission_classes = [LecturaOJefe]


@api_view(["POST"])
@permission_classes([LecturaOJefe])
def generar(request):
    datos = GenerarSerializer(data=request.data)
    datos.is_valid(raise_exception=True)
    try:
        resultado = generar_calendario(usuario=request.user, **datos.validated_data)
    except CalendarioError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    anio, mes = datos.validated_data["anio"], datos.validated_data["mes"]
    return Response({**resultado.como_dict(), "cobertura": cobertura(anio, mes)}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def resumen(request):
    """Cobertura del mes, días hábiles y carga por técnico y día."""
    try:
        anio, mes = _mes_param(request)
    except CalendarioError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    inicio = date(anio, mes, 1)
    carga = {}
    for v in Visita.objects.filter(mes=inicio).select_related("tecnico"):
        t = carga.setdefault(v.tecnico_id, {"tecnico": v.tecnico.nombre, "capacidad": v.tecnico.capacidad_diaria, "total": 0, "por_dia": {}})
        t["total"] += 1
        clave = v.fecha.isoformat()
        t["por_dia"][clave] = t["por_dia"].get(clave, 0) + 1
    ultima = GeneracionCalendario.objects.filter(mes=inicio).first()
    return Response({
        **cobertura(anio, mes),
        "dias_habiles": [d.isoformat() for d in dias_habiles(anio, mes)],
        "carga": list(carga.values()),
        "ultima_generacion": GeneracionSerializer(ultima).data if ultima else None,
    })


@api_view(["GET"])
def mis_visitas(request):
    """Visitas de un técnico para un día (H04).

    El técnico ve solo las suyas: se sabe quién es por su usuario. El jefe
    técnico puede mirar las de cualquier técnico con ?tecnico=ID. Sin ?fecha se
    usa el día de hoy. Además devuelve las visitas atrasadas: las programadas
    para un día anterior del mes en curso que siguen sin hacerse.
    """
    hoy = timezone.localdate()
    tecnico = tecnico_de(request.user)
    if tecnico is None:
        if not es_jefe(request.user):
            return Response(
                {"detail": "Tu usuario no está asociado a un técnico. Pide al jefe técnico que lo asocie."},
                status=status.HTTP_403_FORBIDDEN,
            )
        pedido = request.query_params.get("tecnico", "")
        tecnico = Tecnico.objects.filter(pk=pedido).first() if pedido.isdigit() else None
        if tecnico is None:
            return Response({"detail": "Indica de qué técnico son las visitas."}, status=status.HTTP_400_BAD_REQUEST)

    valor = request.query_params.get("fecha")
    try:
        fecha = date.fromisoformat(valor) if valor else hoy
    except ValueError:
        return Response({"detail": "El parámetro fecha debe tener la forma AAAA-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

    suyas = (
        Visita.objects.filter(tecnico=tecnico)
        .select_related("ascensor", "ascensor__edificio", "tecnico")
        .order_by("fecha", "ascensor__edificio__comuna", "ascensor__edificio__nombre", "ascensor__edificio_id",
                  "ascensor__identificador")
    )
    atrasadas = suyas.filter(mes=hoy.replace(day=1), fecha__lt=hoy, estado=Visita.Estado.PROGRAMADA)
    # Si el día consultado no tiene visitas, sirve saber cuándo es la siguiente.
    proxima = suyas.filter(fecha__gt=fecha, estado=Visita.Estado.PROGRAMADA).values_list("fecha", flat=True).first()
    return Response({
        "tecnico": {"id": tecnico.id, "nombre": tecnico.nombre},
        "hoy": hoy.isoformat(),
        "fecha": fecha.isoformat(),
        "visitas": VisitaDelDiaSerializer(suyas.filter(fecha=fecha), many=True).data,
        "atrasadas": VisitaDelDiaSerializer(atrasadas, many=True).data,
        "proxima_fecha": proxima.isoformat() if proxima else None,
    })
