from rest_framework import serializers

from .models import Ascensor, Edificio, Tecnico


class TecnicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tecnico
        fields = ["id", "nombre", "telefono", "correo", "activo", "capacidad_diaria"]


class AscensorSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    uso_display = serializers.CharField(source="get_uso_display", read_only=True)
    edificio_nombre = serializers.CharField(source="edificio.nombre", read_only=True)

    class Meta:
        model = Ascensor
        fields = [
            "id", "edificio", "edificio_nombre", "identificador", "tipo", "tipo_display", "uso", "uso_display",
            "marca", "numero_serie", "paradas", "capacidad_kg", "fecha_instalacion",
            "vencimiento_certificacion", "activo",
        ]

    def validate_paradas(self, valor):
        if valor < 2:
            raise serializers.ValidationError("Un ascensor tiene al menos dos paradas.")
        return valor


class EdificioSerializer(serializers.ModelSerializer):
    tipo_uso_display = serializers.CharField(source="get_tipo_uso_display", read_only=True)
    tecnico_nombre = serializers.CharField(source="tecnico_asignado.nombre", read_only=True, default=None)
    ascensores = AscensorSerializer(many=True, read_only=True)
    total_ascensores = serializers.SerializerMethodField()

    class Meta:
        model = Edificio
        fields = [
            "id", "nombre", "direccion", "comuna", "tipo_uso", "tipo_uso_display",
            "administrador_nombre", "administrador_correo", "administrador_telefono",
            "tecnico_asignado", "tecnico_nombre", "activo", "total_ascensores", "ascensores",
        ]

    def get_total_ascensores(self, obj):
        return sum(1 for a in obj.ascensores.all() if a.activo)
