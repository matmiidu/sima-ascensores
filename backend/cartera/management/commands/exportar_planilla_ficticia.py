"""Arma la «planilla actual» ficticia de la empresa a partir de la cartera de
demostración, con los defectos que describe el riesgo R3: equipos duplicados
escritos de otra forma, fechas de certificación sin registrar, comunas mal
escritas y un equipo dado de baja que sigue en la lista.

Sirve para la acción A03 (validar una muestra contra terreno) y, más adelante,
para probar la importación H02. Uso:

    python manage.py exportar_planilla_ficticia ../docs/entrega1/a03/planilla_actual.csv
"""
import csv
import random

from django.core.management.base import BaseCommand

from cartera.models import Ascensor

COLUMNAS = ["N°", "Edificio", "Dirección", "Comuna", "Equipo", "Marca", "Tipo", "Paradas",
            "Vence certificación", "Técnico", "Observación"]


def formato_planilla(fecha, rng):
    # En la planilla real las fechas se escriben de varias formas.
    if fecha is None:
        return ""
    return rng.choice([fecha.strftime("%d-%m-%Y"), fecha.strftime("%d/%m/%Y"), fecha.strftime("%d-%m-%y")])


class Command(BaseCommand):
    help = "Exporta la planilla ficticia con defectos para la acción A03."

    def add_arguments(self, parser):
        parser.add_argument("destino")

    def handle(self, destino, **opts):
        rng = random.Random(303)
        # Solo los 140 equipos de la carga de demostración (A1… con número de serie).
        equipos = list(
            Ascensor.objects.exclude(numero_serie="").select_related("edificio", "edificio__tecnico_asignado")
            .order_by("edificio__comuna", "edificio__nombre", "identificador")[:140]
        )
        filas = []
        for a in equipos:
            e = a.edificio
            filas.append({
                "Edificio": e.nombre, "Dirección": e.direccion, "Comuna": e.comuna, "Equipo": a.identificador,
                "Marca": a.marca, "Tipo": a.get_tipo_display(), "Paradas": a.paradas,
                "Vence certificación": formato_planilla(a.vencimiento_certificacion, rng),
                "Técnico": e.tecnico_asignado.nombre.split()[0] if e.tecnico_asignado else "",
                "Observación": "",
            })

        # Defecto 1: 9 fechas de certificación sin registrar.
        for f in rng.sample(filas, 9):
            f["Vence certificación"] = ""
        # Defecto 2: 4 equipos repetidos, escritos de otra forma.
        for f in rng.sample(filas, 4):
            copia = dict(f)
            copia["Edificio"] = copia["Edificio"].upper()
            copia["Dirección"] = copia["Dirección"].replace("Av. ", "Avenida ").replace(" ", "  ", 1)
            copia["Equipo"] = copia["Equipo"].replace("A", "Asc. ")
            copia["Observación"] = "agregado por J.T."
            filas.insert(rng.randrange(len(filas)), copia)
        # Defecto 3: comunas mal escritas.
        for f in rng.sample(filas, 5):
            f["Comuna"] = f["Comuna"].replace("ñ", "n").lower()
        # Defecto 4: un equipo dado de baja que sigue en la lista.
        baja = rng.choice(filas)
        baja["Observación"] = "retirado en remodelación 2025"

        with open(destino, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=COLUMNAS, delimiter=";")
            w.writeheader()
            for i, f in enumerate(filas, 1):
                w.writerow({"N°": i, **f})
        self.stdout.write(f"Planilla ficticia con {len(filas)} filas en {destino}")
