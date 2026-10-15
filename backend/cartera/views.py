from django.db.models import Prefetch, Q
from rest_framework import viewsets

from .models import Ascensor, Edificio, Tecnico
from .serializers import AscensorSerializer, EdificioSerializer, TecnicoSerializer


class TecnicoViewSet(viewsets.ModelViewSet):
    queryset = Tecnico.objects.all()
    serializer_class = TecnicoSerializer


class EdificioViewSet(viewsets.ModelViewSet):
    serializer_class = EdificioSerializer

    def get_queryset(self):
        qs = Edificio.objects.select_related("tecnico_asignado").prefetch_related(
            Prefetch("ascensores", queryset=Ascensor.objects.order_by("identificador"))
        )
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(direccion__icontains=q) | Q(comuna__icontains=q))
        tipo_uso = self.request.query_params.get("tipo_uso")
        if tipo_uso:
            qs = qs.filter(tipo_uso=tipo_uso)
        return qs


class AscensorViewSet(viewsets.ModelViewSet):
    serializer_class = AscensorSerializer

    def get_queryset(self):
        qs = Ascensor.objects.select_related("edificio")
        edificio = self.request.query_params.get("edificio")
        if edificio:
            qs = qs.filter(edificio_id=edificio)
        return qs
