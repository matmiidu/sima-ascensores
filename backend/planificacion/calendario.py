"""Generación del calendario mensual de mantenciones (H03).

Reglas:
- Cada ascensor activo de un edificio activo recibe una mantención al mes.
- Los ascensores de un mismo edificio se visitan el mismo día y con el mismo
  técnico, salvo que superen su capacidad diaria; entonces siguen al día hábil
  siguiente.
- Solo se programan días hábiles: lunes a viernes que no sean feriado.
- El técnico es el asignado al edificio. Si el edificio no tiene uno activo, se
  le da al técnico con menos carga ese mes y se avisa.
- La carga de cada técnico se reparte en forma pareja entre los días hábiles,
  agrupando los edificios por comuna para acortar los traslados.
- Si la carga no cabe en la capacidad, igual se programa (ningún equipo queda
  sin visita) y se informa la sobrecarga para que el jefe técnico decida.
- Generar dos veces el mismo mes no duplica visitas: solo agrega los equipos
  que todavía no tienen. Con reemplazar=True se borran antes las visitas
  programadas (no las realizadas) y se vuelve a repartir.
"""
import calendar
import math
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta

from django.db import transaction

from cartera.models import Ascensor, Tecnico

from .models import Feriado, GeneracionCalendario, Visita


class CalendarioError(Exception):
    pass


@dataclass
class Resultado:
    mes: date
    creadas: int = 0
    ya_programadas: int = 0
    advertencias: list = field(default_factory=list)

    def como_dict(self):
        return {
            "mes": self.mes.isoformat(),
            "creadas": self.creadas,
            "ya_programadas": self.ya_programadas,
            "advertencias": self.advertencias,
        }


def dias_habiles(anio, mes):
    feriados = set(
        Feriado.objects.filter(fecha__year=anio, fecha__month=mes).values_list("fecha", flat=True)
    )
    _, ultimo = calendar.monthrange(anio, mes)
    dias = []
    for d in range(1, ultimo + 1):
        f = date(anio, mes, d)
        if f.weekday() < 5 and f not in feriados:
            dias.append(f)
    return dias


@transaction.atomic
def generar_calendario(anio, mes, reemplazar=False, usuario=None):
    if not 1 <= mes <= 12:
        raise CalendarioError("El mes debe estar entre 1 y 12.")
    inicio = date(anio, mes, 1)
    dias = dias_habiles(anio, mes)
    if not dias:
        raise CalendarioError("El mes no tiene días hábiles.")

    tecnicos = list(Tecnico.objects.filter(activo=True))
    if not tecnicos:
        raise CalendarioError("No hay técnicos activos para asignar visitas.")

    if reemplazar:
        Visita.objects.filter(mes=inicio, estado=Visita.Estado.PROGRAMADA).delete()

    resultado = Resultado(mes=inicio)
    ya = set(Visita.objects.filter(mes=inicio).values_list("ascensor_id", flat=True))
    resultado.ya_programadas = len(ya)

    pendientes = (
        Ascensor.objects.filter(activo=True, edificio__activo=True)
        .exclude(id__in=ya)
        .select_related("edificio", "edificio__tecnico_asignado")
        .order_by("edificio__comuna", "edificio__nombre", "identificador")
    )

    # Carga que cada técnico ya tiene este mes (visitas existentes).
    carga = {t.id: 0 for t in tecnicos}
    ocupacion = {t.id: defaultdict(int) for t in tecnicos}
    for v in Visita.objects.filter(mes=inicio, tecnico_id__in=carga):
        carga[v.tecnico_id] += 1
        ocupacion[v.tecnico_id][v.fecha] += 1

    # Agrupar por edificio y decidir el técnico de cada uno.
    por_edificio = OrderedDict()
    for a in pendientes:
        por_edificio.setdefault(a.edificio, []).append(a)

    tecnicos_por_id = {t.id: t for t in tecnicos}
    bloques = defaultdict(list)  # tecnico_id -> [(edificio, [ascensores])]
    for edificio, ascensores in por_edificio.items():
        t = edificio.tecnico_asignado
        if t is None or t.id not in tecnicos_por_id:
            t = min(tecnicos, key=lambda x: (carga[x.id], x.nombre))
            motivo = "no tiene técnico asignado" if edificio.tecnico_asignado is None else "tiene un técnico inactivo"
            resultado.advertencias.append(
                f"{edificio.nombre} {motivo}; sus visitas quedaron con {t.nombre}."
            )
        carga[t.id] += len(ascensores)
        bloques[t.id].append((edificio, ascensores))

    nuevas = []
    for tecnico_id, lista in bloques.items():
        tecnico = tecnicos_por_id[tecnico_id]
        cap = max(1, tecnico.capacidad_diaria)
        meta = min(cap, math.ceil(carga[tecnico_id] / len(dias)))
        ocup = ocupacion[tecnico_id]
        i = 0
        for edificio, ascensores in lista:
            restantes = list(ascensores)
            while restantes:
                # Avanza al primer día que no haya alcanzado la meta pareja.
                while i < len(dias) - 1 and ocup[dias[i]] >= meta:
                    i += 1
                dia = dias[i]
                if ocup[dia] >= cap:
                    # Todos los días están llenos: el menos cargado del mes.
                    dia = min(dias, key=lambda d: (ocup[d], d))
                    espacio = 1
                else:
                    # El edificio completo va ese día si cabe en la capacidad;
                    # si no, se llena el día y el resto pasa al siguiente.
                    espacio = cap - ocup[dia]
                for a in restantes[:espacio]:
                    nuevas.append(Visita(ascensor=a, tecnico=tecnico, mes=inicio, fecha=dia))
                ocup[dia] += len(restantes[:espacio])
                restantes = restantes[espacio:]

        excedidos = [d for d in dias if ocup[d] > cap]
        if excedidos:
            resultado.advertencias.append(
                f"{tecnico.nombre} supera su capacidad de {cap} equipos diarios en {len(excedidos)} día(s); "
                f"conviene reasignar edificios."
            )

    Visita.objects.bulk_create(nuevas)
    resultado.creadas = len(nuevas)
    GeneracionCalendario.objects.create(
        mes=inicio,
        generado_por=usuario if usuario and usuario.is_authenticated else None,
        visitas_creadas=resultado.creadas,
        advertencias=resultado.advertencias,
    )
    return resultado


def cobertura(anio, mes):
    """Cuántos equipos activos tienen visita en el mes y cuáles no."""
    inicio = date(anio, mes, 1)
    activos = Ascensor.objects.filter(activo=True, edificio__activo=True)
    con_visita = set(Visita.objects.filter(mes=inicio).values_list("ascensor_id", flat=True))
    sin_visita = [a for a in activos.select_related("edificio") if a.id not in con_visita]
    return {
        "mes": inicio.isoformat(),
        "equipos_activos": activos.count(),
        "con_visita": activos.filter(id__in=con_visita).count(),
        "sin_visita": [{"id": a.id, "nombre": str(a)} for a in sin_visita],
    }


def siguiente_mes(hoy=None):
    hoy = hoy or date.today()
    primero = hoy.replace(day=1)
    return (primero + timedelta(days=32)).replace(day=1)
