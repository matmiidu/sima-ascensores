from rest_framework import serializers

from .models import ChecklistPrueba


class ChecklistPruebaSerializer(serializers.ModelSerializer):
    demora_segundos = serializers.IntegerField(read_only=True)

    class Meta:
        model = ChecklistPrueba
        fields = ["id", "id_local", "ascensor", "respuestas", "observaciones", "guardado_en_dispositivo",
                  "recibido", "demora_segundos"]
        read_only_fields = ["recibido"]
        # La unicidad de id_local se resuelve en la vista (envío repetido = 200).
        extra_kwargs = {"id_local": {"validators": []}}
