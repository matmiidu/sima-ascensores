from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .models import ChecklistPrueba
from .serializers import ChecklistPruebaSerializer


class ChecklistPruebaViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
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
