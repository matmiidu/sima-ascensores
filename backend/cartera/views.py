from django.db.models import Prefetch, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from config.permisos import LecturaOJefe, es_jefe

from .certificaciones import PLAZO_DIAS, alertas_de_certificacion
from .importacion import PlanillaInvalida, importar, leer_planilla, revisar
from .models import Ascensor, Edificio, Tecnico
from .serializers import AscensorSerializer, EdificioSerializer, TecnicoSerializer


class TecnicoViewSet(viewsets.ModelViewSet):
    queryset = Tecnico.objects.all()
    serializer_class = TecnicoSerializer
    permission_classes = [LecturaOJefe]


class EdificioViewSet(viewsets.ModelViewSet):
    serializer_class = EdificioSerializer
    permission_classes = [LecturaOJefe]

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
    permission_classes = [LecturaOJefe]

    def get_queryset(self):
        qs = Ascensor.objects.select_related("edificio")
        edificio = self.request.query_params.get("edificio")
        if edificio:
            qs = qs.filter(edificio_id=edificio)
        return qs


@api_view(["GET"])
def certificaciones(request):
    """Certificaciones vencidas, por vencer y sin fecha, para el jefe técnico (H10).

    ?dias=N cambia el plazo de anticipación (1 a 365; 60 por omisión).
    """
    if not es_jefe(request.user):
        return Response({"detail": "Solo el jefe técnico revisa las certificaciones."}, status=status.HTTP_403_FORBIDDEN)
    valor = request.query_params.get("dias", str(PLAZO_DIAS))
    if not valor.isdigit() or not 1 <= int(valor) <= 365:
        return Response({"detail": "El plazo debe ser un número de días entre 1 y 365."}, status=status.HTTP_400_BAD_REQUEST)
    return Response(alertas_de_certificacion(timezone.localdate(), int(valor)))


MAX_BYTES_PLANILLA = 2 * 1024 * 1024


@api_view(["POST"])
@parser_classes([MultiPartParser])
def importar_planilla(request):
    """Importar la cartera desde la planilla (H02). Solo el personal (jefe técnico o asistente administrativa).

    Recibe el archivo (`archivo`, .csv o .xlsx), el tipo de uso de los edificios nuevos (`tipo_uso`) y
    `confirmar`. Sin confirmar solo revisa y devuelve qué pasaría con cada fila; con `confirmar=1` revisa de
    nuevo y guarda todo junto.
    """
    if not es_jefe(request.user):
        return Response({"detail": "Solo el personal de la oficina importa la planilla."}, status=status.HTTP_403_FORBIDDEN)
    archivo = request.FILES.get("archivo")
    if archivo is None:
        return Response({"detail": "Elige el archivo de la planilla."}, status=status.HTTP_400_BAD_REQUEST)
    if archivo.size > MAX_BYTES_PLANILLA:
        return Response({"detail": "La planilla pesa más de 2 MB."}, status=status.HTTP_400_BAD_REQUEST)
    tipo_uso = request.data.get("tipo_uso") or Edificio.TipoUso.RESIDENCIAL
    if tipo_uso not in Edificio.TipoUso.values:
        return Response({"detail": "Tipo de uso no válido."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        revision = revisar(leer_planilla(archivo.read(), archivo.name), tipo_uso)
    except PlanillaInvalida as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    if request.data.get("confirmar") in ("1", "true", "si"):
        return Response({"importado": importar(revision), **revision}, status=status.HTTP_201_CREATED)
    return Response(revision)
