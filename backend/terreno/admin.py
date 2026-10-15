from django.contrib import admin

from .models import ChecklistPrueba


@admin.register(ChecklistPrueba)
class ChecklistPruebaAdmin(admin.ModelAdmin):
    list_display = ["id_local", "ascensor", "guardado_en_dispositivo", "recibido", "demora_segundos"]
    readonly_fields = ["recibido"]
