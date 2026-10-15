"""Feriados legales de Chile en 2026. Los años siguientes se agregan desde el panel."""
from datetime import date

from django.db import migrations

FERIADOS_2026 = [
    (date(2026, 1, 1), "Año Nuevo"),
    (date(2026, 4, 3), "Viernes Santo"),
    (date(2026, 4, 4), "Sábado Santo"),
    (date(2026, 5, 1), "Día Nacional del Trabajo"),
    (date(2026, 5, 21), "Día de las Glorias Navales"),
    (date(2026, 6, 21), "Día Nacional de los Pueblos Indígenas"),
    (date(2026, 6, 29), "San Pedro y San Pablo"),
    (date(2026, 7, 16), "Día de la Virgen del Carmen"),
    (date(2026, 8, 15), "Asunción de la Virgen"),
    (date(2026, 9, 18), "Independencia Nacional"),
    (date(2026, 9, 19), "Día de las Glorias del Ejército"),
    (date(2026, 10, 12), "Encuentro de Dos Mundos"),
    (date(2026, 10, 31), "Día de las Iglesias Evangélicas y Protestantes"),
    (date(2026, 11, 1), "Día de Todos los Santos"),
    (date(2026, 12, 8), "Inmaculada Concepción"),
    (date(2026, 12, 25), "Navidad"),
]


def cargar(apps, schema_editor):
    Feriado = apps.get_model("planificacion", "Feriado")
    for fecha, nombre in FERIADOS_2026:
        Feriado.objects.get_or_create(fecha=fecha, defaults={"nombre": nombre})


def quitar(apps, schema_editor):
    Feriado = apps.get_model("planificacion", "Feriado")
    Feriado.objects.filter(fecha__in=[f for f, _ in FERIADOS_2026]).delete()


class Migration(migrations.Migration):
    dependencies = [("planificacion", "0001_initial")]
    operations = [migrations.RunPython(cargar, quitar)]
