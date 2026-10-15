from django.contrib import admin

from .models import Feriado, GeneracionCalendario, Visita


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ["fecha", "ascensor", "tecnico", "estado"]
    list_filter = ["mes", "tecnico", "estado"]
    date_hierarchy = "fecha"


@admin.register(Feriado)
class FeriadoAdmin(admin.ModelAdmin):
    list_display = ["fecha", "nombre"]


@admin.register(GeneracionCalendario)
class GeneracionCalendarioAdmin(admin.ModelAdmin):
    list_display = ["mes", "generado", "generado_por", "visitas_creadas"]
