from django.utils import timezone
from rest_framework import serializers

from .models import Feriado, GeneracionCalendario, Visita


def ultima_mantencion(visita):
    """La mantención anterior del mismo ascensor (H07): lo que el técnico necesita saber al llegar al equipo,
    también sin señal, porque viaja en la copia de la jornada. None si el equipo no tiene mantenciones previas."""
    from terreno.models import RegistroMantencion  # terreno depende de planificación; se importa aquí

    previo = (RegistroMantencion.objects.filter(visita__ascensor_id=visita.ascensor_id)
              .exclude(visita_id=visita.id).filter(visita__fecha__lte=visita.fecha)
              .select_related("tecnico").prefetch_related("respuestas__punto")
              .order_by("-guardado_en_dispositivo").first())
    if previo is None:
        return None
    return {
        "codigo": previo.codigo,
        "fecha": timezone.localtime(previo.guardado_en_dispositivo).date().isoformat(),
        "tecnico": previo.tecnico.nombre,
        "operativo": previo.operativo,
        "falla": previo.falla_descripcion,
        "observaciones": previo.observaciones,
        "puntos_con_observacion": [
            {"codigo": r.punto.codigo, "descripcion": r.punto.descripcion, "comentario": r.comentario}
            for r in previo.respuestas.all() if r.resultado == r.Resultado.OBSERVACION
        ],
    }


def resumen_del_registro(visita):
    """Lo esencial de la mantención registrada en una visita (H06), o None si todavía no se hizo."""
    registro = getattr(visita, "registro", None)
    if registro is None:
        return None
    return {
        "id": registro.id,
        "codigo": registro.codigo,
        "operativo": registro.operativo,
        "guardado_en_dispositivo": registro.guardado_en_dispositivo,
    }


class VisitaSerializer(serializers.ModelSerializer):
    ascensor_identificador = serializers.CharField(source="ascensor.identificador", read_only=True)
    edificio_id = serializers.IntegerField(source="ascensor.edificio_id", read_only=True)
    edificio_nombre = serializers.CharField(source="ascensor.edificio.nombre", read_only=True)
    direccion = serializers.CharField(source="ascensor.edificio.direccion", read_only=True)
    comuna = serializers.CharField(source="ascensor.edificio.comuna", read_only=True)
    tecnico_nombre = serializers.CharField(source="tecnico.nombre", read_only=True)
    registro = serializers.SerializerMethodField()

    class Meta:
        model = Visita
        fields = [
            "id", "ascensor", "ascensor_identificador", "edificio_id", "edificio_nombre", "direccion", "comuna",
            "tecnico", "tecnico_nombre", "mes", "fecha", "estado", "registro",
        ]
        read_only_fields = ["mes"]

    def get_registro(self, obj):
        return resumen_del_registro(obj)

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
    registro = serializers.SerializerMethodField()
    ultima_mantencion = serializers.SerializerMethodField()

    class Meta:
        model = Visita
        fields = [
            "id", "fecha", "mes", "estado", "ascensor", "ascensor_identificador", "marca", "paradas", "tipo_display",
            "edificio_id", "edificio_nombre", "direccion", "comuna", "administrador_nombre", "administrador_telefono",
            "tecnico", "tecnico_nombre", "registro", "ultima_mantencion",
        ]
        read_only_fields = fields

    def get_registro(self, obj):
        return resumen_del_registro(obj)

    def get_ultima_mantencion(self, obj):
        return ultima_mantencion(obj)


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
