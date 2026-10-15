from datetime import date

from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .calendario import CalendarioError, cobertura, dias_habiles, generar_calendario
from .models import Feriado, GeneracionCalendario, Visita
from .serializers import FeriadoSerializer, GenerarSerializer, GeneracionSerializer, VisitaSerializer


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


@api_view(["POST"])
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
