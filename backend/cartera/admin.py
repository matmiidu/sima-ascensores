from django.contrib import admin

from .models import Ascensor, Edificio, Tecnico


class AscensorInline(admin.TabularInline):
    model = Ascensor
    extra = 1
    fields = ["identificador", "tipo", "uso", "marca", "paradas", "vencimiento_certificacion", "activo"]


@admin.register(Edificio)
class EdificioAdmin(admin.ModelAdmin):
    list_display = ["nombre", "comuna", "tipo_uso", "tecnico_asignado", "activo"]
    list_filter = ["tipo_uso", "comuna", "tecnico_asignado", "activo"]
    search_fields = ["nombre", "direccion", "comuna", "administrador_nombre"]
    inlines = [AscensorInline]


@admin.register(Ascensor)
class AscensorAdmin(admin.ModelAdmin):
    list_display = ["__str__", "tipo", "uso", "vencimiento_certificacion", "activo"]
    list_filter = ["tipo", "uso", "activo", "edificio__comuna"]
    search_fields = ["identificador", "edificio__nombre", "numero_serie"]


@admin.register(Tecnico)
class TecnicoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "telefono", "capacidad_diaria", "usuario", "activo"]
