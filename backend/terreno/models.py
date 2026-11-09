"""Trabajo en terreno (EP3).

- ChecklistPrueba: prueba de concepto sin conexión (S01), se conserva como evidencia.
- PuntoChecklist, RegistroMantencion y RespuestaPunto: el registro de la
  mantención mensual de una visita (H06, requisitos RF-02 y RF-03).
"""
import uuid

from django.conf import settings
from django.db import models

from cartera.models import Ascensor, Tecnico
from planificacion.models import Visita


class ChecklistPrueba(models.Model):
    # Lo genera el celular al guardar. Si el envío se repite (por ejemplo, la
    # respuesta se perdió al cortarse la señal), el servidor no lo duplica.
    id_local = models.UUIDField(unique=True, default=uuid.uuid4)
    ascensor = models.ForeignKey(Ascensor, null=True, blank=True, on_delete=models.SET_NULL)
    respuestas = models.JSONField(default=dict)
    observaciones = models.TextField(blank=True)
    guardado_en_dispositivo = models.DateTimeField()
    recibido = models.DateTimeField(auto_now_add=True)
    enviado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-recibido"]
        verbose_name = "checklist de prueba"
        verbose_name_plural = "checklists de prueba"

    @property
    def demora_segundos(self):
        return round((self.recibido - self.guardado_en_dispositivo).total_seconds())


class PuntoChecklist(models.Model):
    """Cada punto que el técnico revisa en la mantención mensual. Es una tabla y
    no una lista fija en el código para que el jefe técnico pueda ajustarla."""

    codigo = models.CharField("código", max_length=10, unique=True)
    descripcion = models.CharField("descripción", max_length=150)
    orden = models.PositiveSmallIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden", "codigo"]
        verbose_name = "punto del checklist"
        verbose_name_plural = "puntos del checklist"

    def __str__(self):
        return f"{self.codigo} {self.descripcion}"


class RegistroMantencion(models.Model):
    """La mantención hecha en una visita: una visita tiene a lo más un registro."""

    visita = models.OneToOneField(Visita, on_delete=models.PROTECT, related_name="registro")
    tecnico = models.ForeignKey(Tecnico, on_delete=models.PROTECT, related_name="registros", verbose_name="técnico")
    # Generado en el celular: si el envío se repite, no se duplica (RNF-01).
    id_local = models.UUIDField(unique=True, default=uuid.uuid4)
    operativo = models.BooleanField("el equipo quedó operativo")
    falla_descripcion = models.TextField("descripción de la falla", blank=True)
    observaciones = models.TextField(blank=True)
    guardado_en_dispositivo = models.DateTimeField()
    recibido = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-guardado_en_dispositivo"]
        verbose_name = "registro de mantención"
        verbose_name_plural = "registros de mantención"

    @property
    def codigo(self):
        return f"M-{self.pk:04d}"

    def __str__(self):
        return f"{self.codigo} {self.visita.ascensor}"


class RespuestaPunto(models.Model):
    class Resultado(models.TextChoices):
        BIEN = "bien", "Bien"
        OBSERVACION = "observacion", "Con observación"
        NO_APLICA = "no_aplica", "No aplica"

    registro = models.ForeignKey(RegistroMantencion, on_delete=models.CASCADE, related_name="respuestas")
    punto = models.ForeignKey(PuntoChecklist, on_delete=models.PROTECT, related_name="respuestas")
    resultado = models.CharField(max_length=20, choices=Resultado.choices)
    comentario = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["punto__orden", "punto__codigo"]
        verbose_name = "respuesta"
        constraints = [
            models.UniqueConstraint(fields=["registro", "punto"], name="una_respuesta_por_punto"),
        ]
