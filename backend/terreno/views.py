from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cartera.models import Edificio
from config.permisos import es_jefe

from .informe import MesInvalido, datos_del_informe, generar_pdf, informes_del_mes, leer_mes, nombre_archivo, nombre_mes

from .models import ChecklistPrueba, PuntoChecklist, RegistroMantencion
from .registro import Rechazo, registrar_mantencion
from .serializers import (
    ChecklistPruebaSerializer,
    NuevoRegistroSerializer,
    PuntoChecklistSerializer,
    RegistroMantencionSerializer,
)


class ChecklistPruebaViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Prueba de concepto S01 (Entrega 1). Se conserva como evidencia."""

    queryset = ChecklistPrueba.objects.all()
    serializer_class = ChecklistPruebaSerializer

    def create(self, request, *args, **kwargs):
        existente = ChecklistPrueba.objects.filter(id_local=request.data.get("id_local")).first()
        if existente:
            # Reenvío del mismo registro: se confirma sin duplicarlo.
            return Response(self.get_serializer(existente).data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(enviado_por=self.request.user)


class PuntoChecklistViewSet(viewsets.ReadOnlyModelViewSet):
    """Puntos que el técnico revisa en la mantención. El jefe técnico los ajusta en el panel."""

    queryset = PuntoChecklist.objects.filter(activo=True)
    serializer_class = PuntoChecklistSerializer
    pagination_class = None


class RegistroMantencionViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    """Registrar la mantención de una visita (POST) y consultar lo registrado
    (GET, con filtros ?visita=, ?ascensor=, ?edificio=, ?mes=AAAA-MM y
    ?detenidos=1 para ver solo los equipos que quedaron detenidos)."""

    serializer_class = RegistroMantencionSerializer

    def get_queryset(self):
        qs = RegistroMantencion.objects.select_related(
            "tecnico", "visita__ascensor__edificio"
        ).prefetch_related("respuestas__punto")
        p = self.request.query_params
        if p.get("ascensor"):
            qs = qs.filter(visita__ascensor_id=p["ascensor"])
        if p.get("edificio"):
            qs = qs.filter(visita__ascensor__edificio_id=p["edificio"])
        if p.get("visita"):
            qs = qs.filter(visita_id=p["visita"])
        if p.get("detenidos"):
            qs = qs.filter(operativo=False)
        if p.get("mes"):
            try:
                anio, mes = (int(x) for x in p["mes"].split("-"))
                qs = qs.filter(visita__mes__year=anio, visita__mes__month=mes)
            except ValueError:
                qs = qs.none()
        return qs

    def create(self, request, *args, **kwargs):
        datos = NuevoRegistroSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        d = datos.validated_data
        try:
            registro, creado = registrar_mantencion(
                visita_id=d["visita"],
                respuestas=d["respuestas"],
                operativo=d["operativo"],
                falla_descripcion=d["falla_descripcion"],
                observaciones=d["observaciones"],
                id_local=d.get("id_local"),
                guardado_en_dispositivo=d["guardado_en_dispositivo"],
                usuario=request.user,
            )
        except Rechazo as r:
            return Response(r.como_dict(), status=r.estado)
        registro = self.get_queryset().get(pk=registro.pk)
        return Response(
            self.get_serializer(registro).data,
            status=status.HTTP_201_CREATED if creado else status.HTTP_200_OK,
        )


SOLO_JEFE_INFORMES = "Solo el jefe técnico descarga los informes mensuales."


@api_view(["GET"])
def informes(request):
    """Edificios con visitas en el mes y si su informe está completo (H09). ?mes=AAAA-MM, por omisión el mes en curso."""
    if not es_jefe(request.user):
        return Response({"detail": SOLO_JEFE_INFORMES}, status=status.HTTP_403_FORBIDDEN)
    try:
        mes = leer_mes(request.query_params.get("mes"), timezone.localdate())
    except MesInvalido as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(informes_del_mes(mes))


@api_view(["GET"])
def informe_pdf(request, edificio_id):
    """Informe mensual de mantención del edificio en PDF (H09). ?mes=AAAA-MM, por omisión el mes en curso."""
    if not es_jefe(request.user):
        return Response({"detail": SOLO_JEFE_INFORMES}, status=status.HTTP_403_FORBIDDEN)
    hoy = timezone.localdate()
    try:
        mes = leer_mes(request.query_params.get("mes"), hoy)
    except MesInvalido as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    edificio = get_object_or_404(Edificio, pk=edificio_id)
    datos = datos_del_informe(edificio, mes, hoy)
    if datos is None:
        return Response(
            {"detail": f"{edificio.nombre} no tiene mantenciones programadas en {nombre_mes(mes)}."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    respuesta = HttpResponse(generar_pdf(datos), content_type="application/pdf")
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre_archivo(edificio, mes)}"'
    return respuesta
