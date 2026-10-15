"""Prueba de concepto sin conexión (S01).

Guarda los checklists que el celular registró sin señal y envía al recuperarla.
Es un modelo provisorio: el checklist definitivo es la historia H06 (Entrega 2).
"""
import uuid

from django.conf import settings
from django.db import models

from cartera.models import Ascensor


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
