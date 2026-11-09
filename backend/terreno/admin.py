from django.contrib import admin

from .models import ChecklistPrueba, PuntoChecklist, RegistroMantencion, RespuestaPunto


@admin.register(ChecklistPrueba)
class ChecklistPruebaAdmin(admin.ModelAdmin):
    list_display = ["id_local", "ascensor", "guardado_en_dispositivo", "recibido", "demora_segundos"]
    readonly_fields = ["recibido"]


@admin.register(PuntoChecklist)
class PuntoChecklistAdmin(admin.ModelAdmin):
    list_display = ["codigo", "descripcion", "orden", "activo"]
    list_editable = ["orden", "activo"]


class RespuestaPuntoInline(admin.TabularInline):
    model = RespuestaPunto
    extra = 0
    can_delete = False
    readonly_fields = ["punto", "resultado", "comentario"]


@admin.register(RegistroMantencion)
class RegistroMantencionAdmin(admin.ModelAdmin):
    list_display = ["codigo", "visita", "tecnico", "operativo", "guardado_en_dispositivo", "recibido"]
    list_filter = ["operativo", "tecnico"]
    readonly_fields = ["visita", "tecnico", "id_local", "guardado_en_dispositivo", "recibido", "registrado_por"]
    inlines = [RespuestaPuntoInline]
