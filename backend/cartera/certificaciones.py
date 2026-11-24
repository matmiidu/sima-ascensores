"""Alertas de certificación (H10, requisito RF-06).

La certificación de un ascensor vence (Ley 20.296: cada dos años en edificios
residenciales y cada año en los demás). El jefe técnico necesita saber con
anticipación cuáles vencen para avisar al administrador del edificio, que es
quien contrata la certificación.

Reglas:
- Solo cuentan los ascensores activos de edificios activos.
- Vencida: la fecha de vencimiento ya pasó.
- Por vencer: vence hoy o dentro del plazo (60 días por omisión, el mismo umbral
  que usa la ficha del edificio para marcar "por vencer").
- Sin fecha: el ascensor no tiene el vencimiento registrado (riesgo R3 del plan:
  la planilla traía fechas sin registrar); se muestra aparte para completarlo.
"""
from datetime import timedelta

from .models import Ascensor

PLAZO_DIAS = 60


def _alerta(a, hoy):
    e = a.edificio
    return {
        "ascensor_id": a.id,
        "identificador": a.identificador,
        "edificio_id": e.id,
        "edificio": e.nombre,
        "direccion": e.direccion,
        "comuna": e.comuna,
        "vencimiento": a.vencimiento_certificacion.isoformat() if a.vencimiento_certificacion else None,
        "dias_restantes": (a.vencimiento_certificacion - hoy).days if a.vencimiento_certificacion else None,
        "administrador": {
            "nombre": e.administrador_nombre,
            "correo": e.administrador_correo,
            "telefono": e.administrador_telefono,
        },
    }


def alertas_de_certificacion(hoy, dias=PLAZO_DIAS):
    """Devuelve las vencidas, las que vencen dentro de `dias` y las que no tienen fecha."""
    activos = Ascensor.objects.filter(activo=True, edificio__activo=True).select_related("edificio")
    limite = hoy + timedelta(days=dias)
    vencidas = activos.filter(vencimiento_certificacion__lt=hoy).order_by("vencimiento_certificacion", "edificio__nombre")
    por_vencer = activos.filter(vencimiento_certificacion__gte=hoy, vencimiento_certificacion__lte=limite).order_by(
        "vencimiento_certificacion", "edificio__nombre")
    sin_fecha = activos.filter(vencimiento_certificacion__isnull=True).order_by(
        "edificio__comuna", "edificio__nombre", "identificador")
    return {
        "hoy": hoy.isoformat(),
        "dias": dias,
        "vencidas": [_alerta(a, hoy) for a in vencidas],
        "por_vencer": [_alerta(a, hoy) for a in por_vencer],
        "sin_fecha": [_alerta(a, hoy) for a in sin_fecha],
    }
