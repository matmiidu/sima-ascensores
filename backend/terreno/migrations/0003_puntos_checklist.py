"""Puntos del checklist de mantención mensual (H06).

Los propuso el equipo y se revisaron en la sesión de prueba A02 (SIMULACIÓN:
acuerdo no validado con un interesado real). El jefe técnico puede ajustarlos
desde el panel sin tocar el código.
"""
from django.db import migrations

PUNTOS = [
    ("P01", "Motor, freno y reductor en la sala de máquinas"),
    ("P02", "Cables de tracción y limitador de velocidad"),
    ("P03", "Paracaídas y amortiguadores"),
    ("P04", "Puertas de piso y de cabina, con sus enclavamientos"),
    ("P05", "Botoneras, señalización e iluminación de la cabina"),
    ("P06", "Alarma, citófono y luz de emergencia"),
    ("P07", "Foso y finales de carrera"),
    ("P08", "Nivelación de la cabina en cada parada"),
]


def cargar(apps, schema_editor):
    PuntoChecklist = apps.get_model("terreno", "PuntoChecklist")
    for orden, (codigo, descripcion) in enumerate(PUNTOS, start=1):
        PuntoChecklist.objects.get_or_create(codigo=codigo, defaults={"descripcion": descripcion, "orden": orden})


def borrar(apps, schema_editor):
    apps.get_model("terreno", "PuntoChecklist").objects.filter(codigo__in=[c for c, _ in PUNTOS]).delete()


class Migration(migrations.Migration):
    dependencies = [("terreno", "0002_registro_mantencion")]
    operations = [migrations.RunPython(cargar, borrar)]
