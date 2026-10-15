"""Planificación de visitas (EP2, historia H03)."""
from django.conf import settings
from django.db import models

from cartera.models import Ascensor, Tecnico


class Feriado(models.Model):
    """Días en que no se programan mantenciones. Se cargan los feriados legales
    de Chile y el jefe técnico puede agregar otros desde el panel."""

    fecha = models.DateField(unique=True)
    nombre = models.CharField(max_length=120)

    class Meta:
        ordering = ["fecha"]

    def __str__(self):
        return f"{self.fecha:%d-%m-%Y} {self.nombre}"


class Visita(models.Model):
    class Estado(models.TextChoices):
        PROGRAMADA = "programada", "Programada"
        REALIZADA = "realizada", "Realizada"
        NO_REALIZADA = "no_realizada", "No realizada"

    ascensor = models.ForeignKey(Ascensor, on_delete=models.CASCADE, related_name="visitas")
    tecnico = models.ForeignKey(Tecnico, on_delete=models.PROTECT, related_name="visitas", verbose_name="técnico")
    # Primer día del mes al que corresponde la mantención mensual.
    mes = models.DateField()
    fecha = models.DateField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PROGRAMADA)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha", "tecnico", "ascensor__edificio__nombre", "ascensor__identificador"]
        constraints = [
            # Una mantención preventiva por ascensor y por mes.
            models.UniqueConstraint(fields=["ascensor", "mes"], name="una_visita_por_ascensor_y_mes"),
        ]

    def __str__(self):
        return f"{self.fecha:%d-%m} {self.ascensor} · {self.tecnico}"


class GeneracionCalendario(models.Model):
    """Registro de cada vez que se generó un calendario, para la trazabilidad."""

    mes = models.DateField()
    generado = models.DateTimeField(auto_now_add=True)
    generado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    visitas_creadas = models.PositiveIntegerField()
    advertencias = models.JSONField(default=list)

    class Meta:
        ordering = ["-generado"]
