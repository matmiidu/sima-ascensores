from rest_framework import serializers

from .models import ChecklistPrueba, PuntoChecklist, RegistroMantencion, RespuestaPunto


class ChecklistPruebaSerializer(serializers.ModelSerializer):
    demora_segundos = serializers.IntegerField(read_only=True)

    class Meta:
        model = ChecklistPrueba
        fields = ["id", "id_local", "ascensor", "respuestas", "observaciones", "guardado_en_dispositivo",
                  "recibido", "demora_segundos"]
        read_only_fields = ["recibido"]
        # La unicidad de id_local se resuelve en la vista (envío repetido = 200).
        extra_kwargs = {"id_local": {"validators": []}}


class PuntoChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuntoChecklist
        fields = ["id", "codigo", "descripcion", "orden"]


class RespuestaPuntoSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(source="punto.codigo", read_only=True)
    descripcion = serializers.CharField(source="punto.descripcion", read_only=True)
    resultado_display = serializers.CharField(source="get_resultado_display", read_only=True)

    class Meta:
        model = RespuestaPunto
        fields = ["punto", "codigo", "descripcion", "resultado", "resultado_display", "comentario"]


class RegistroMantencionSerializer(serializers.ModelSerializer):
    """Lectura de un registro ya guardado (consulta)."""

    codigo = serializers.CharField(read_only=True)
    tecnico_nombre = serializers.CharField(source="tecnico.nombre", read_only=True)
    ascensor = serializers.IntegerField(source="visita.ascensor_id", read_only=True)
    ascensor_identificador = serializers.CharField(source="visita.ascensor.identificador", read_only=True)
    edificio_id = serializers.IntegerField(source="visita.ascensor.edificio_id", read_only=True)
    edificio_nombre = serializers.CharField(source="visita.ascensor.edificio.nombre", read_only=True)
    direccion = serializers.CharField(source="visita.ascensor.edificio.direccion", read_only=True)
    comuna = serializers.CharField(source="visita.ascensor.edificio.comuna", read_only=True)
    fecha_programada = serializers.DateField(source="visita.fecha", read_only=True)
    respuestas = RespuestaPuntoSerializer(many=True, read_only=True)

    class Meta:
        model = RegistroMantencion
        fields = [
            "id", "codigo", "id_local", "visita", "fecha_programada", "ascensor", "ascensor_identificador",
            "edificio_id", "edificio_nombre", "direccion", "comuna", "tecnico", "tecnico_nombre", "operativo",
            "falla_descripcion", "observaciones", "guardado_en_dispositivo", "recibido", "respuestas",
        ]


class NuevoRegistroSerializer(serializers.Serializer):
    """Lo que manda el celular. Solo revisa la forma de los datos; las reglas
    del negocio están en registro.py para que se lean juntas."""

    visita = serializers.IntegerField()
    id_local = serializers.UUIDField(required=False, allow_null=True)
    respuestas = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField(allow_blank=True, allow_null=True)),
        required=False, default=list,
    )
    operativo = serializers.BooleanField(required=False, allow_null=True, default=None)
    falla_descripcion = serializers.CharField(required=False, allow_blank=True, default="")
    observaciones = serializers.CharField(required=False, allow_blank=True, default="")
    guardado_en_dispositivo = serializers.DateTimeField(required=False, allow_null=True, default=None)
