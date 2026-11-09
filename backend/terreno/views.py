from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

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
