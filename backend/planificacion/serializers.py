from rest_framework import serializers

from .models import Feriado, GeneracionCalendario, Visita


class VisitaSerializer(serializers.ModelSerializer):
    ascensor_identificador = serializers.CharField(source="ascensor.identificador", read_only=True)
    edificio_id = serializers.IntegerField(source="ascensor.edificio_id", read_only=True)
    edificio_nombre = serializers.CharField(source="ascensor.edificio.nombre", read_only=True)
    direccion = serializers.CharField(source="ascensor.edificio.direccion", read_only=True)
    comuna = serializers.CharField(source="ascensor.edificio.comuna", read_only=True)
    tecnico_nombre = serializers.CharField(source="tecnico.nombre", read_only=True)

    class Meta:
        model = Visita
        fields = [
            "id", "ascensor", "ascensor_identificador", "edificio_id", "edificio_nombre", "direccion", "comuna",
            "tecnico", "tecnico_nombre", "mes", "fecha", "estado",
        ]
        read_only_fields = ["mes"]

    def validate(self, datos):
        fecha = datos.get("fecha", getattr(self.instance, "fecha", None))
        mes = getattr(self.instance, "mes", None) or (fecha.replace(day=1) if fecha else None)
        if fecha and mes and (fecha.year, fecha.month) != (mes.year, mes.month):
            raise serializers.ValidationError({"fecha": "La visita debe quedar dentro de su mes."})
        return datos

    def create(self, datos):
        datos["mes"] = datos["fecha"].replace(day=1)
        return super().create(datos)


class VisitaDelDiaSerializer(serializers.ModelSerializer):
    """Lo que el técnico necesita ver de una visita en el celular (H04): a qué
    edificio va, qué equipo es y a quién llamar."""

    ascensor_identificador = serializers.CharField(source="ascensor.identificador", read_only=True)
    marca = serializers.CharField(source="ascensor.marca", read_only=True)
    paradas = serializers.IntegerField(source="ascensor.paradas", read_only=True)
    tipo_display = serializers.CharField(source="ascensor.get_tipo_display", read_only=True)
    edificio_id = serializers.IntegerField(source="ascensor.edificio_id", read_only=True)
    edificio_nombre = serializers.CharField(source="ascensor.edificio.nombre", read_only=True)
    direccion = serializers.CharField(source="ascensor.edificio.direccion", read_only=True)
    comuna = serializers.CharField(source="ascensor.edificio.comuna", read_only=True)
    administrador_nombre = serializers.CharField(source="ascensor.edificio.administrador_nombre", read_only=True)
    administrador_telefono = serializers.CharField(source="ascensor.edificio.administrador_telefono", read_only=True)
    tecnico_nombre = serializers.CharField(source="tecnico.nombre", read_only=True)

    class Meta:
        model = Visita
        fields = [
            "id", "fecha", "mes", "estado", "ascensor", "ascensor_identificador", "marca", "paradas", "tipo_display",
            "edificio_id", "edificio_nombre", "direccion", "comuna", "administrador_nombre", "administrador_telefono",
            "tecnico", "tecnico_nombre",
        ]
        read_only_fields = fields


class GenerarSerializer(serializers.Serializer):
    anio = serializers.IntegerField(min_value=2020, max_value=2100)
    mes = serializers.IntegerField(min_value=1, max_value=12)
    reemplazar = serializers.BooleanField(default=False)


class FeriadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feriado
        fields = ["id", "fecha", "nombre"]


class GeneracionSerializer(serializers.ModelSerializer):
    generado_por = serializers.CharField(source="generado_por.username", default=None, read_only=True)

    class Meta:
        model = GeneracionCalendario
        fields = ["id", "mes", "generado", "generado_por", "visitas_creadas", "advertencias"]
