"""Registro de la mantención de una visita (H06, requisitos RF-02 y RF-03).

Reglas que se comprueban antes de guardar, en este orden:
1. Si el celular repite un envío que ya llegó (mismo id_local), se devuelve el
   registro existente sin duplicarlo (RNF-01).
2. La visita es del técnico que la registra.
3. La visita todavía está programada: una visita ya registrada no se registra
   otra vez, y se avisa cuándo se registró (RF-02, CA-04).
4. La visita no es de una fecha futura. Una visita atrasada sí se puede
   registrar, mientras siga siendo su mes (RF-02 versión 3).
5. Cada punto activo del checklist tiene respuesta: bien, con observación o no
   aplica. Un punto con observación lleva la observación escrita (CA-01, CA-03).
6. Se indicó si el equipo quedó operativo. Si quedó detenido, hay que describir
   la falla (RF-03).

Si algo falla no se guarda nada y la visita sigue programada.
"""
from django.db import transaction
from django.utils import timezone

from config.permisos import tecnico_de
from planificacion.models import Visita

from .models import PuntoChecklist, RegistroMantencion, RespuestaPunto

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]


class Rechazo(Exception):
    """El registro no cumple una regla. `errores` dice qué corregir y dónde."""

    def __init__(self, mensaje, errores=None, estado=400):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.errores = errores or {}
        self.estado = estado

    def como_dict(self):
        return {"detail": self.mensaje, **self.errores}


def _plural(n, uno, varios):
    return f"{n} {uno if n == 1 else varios}"


def revisar_checklist(puntos, respuestas, operativo, falla_descripcion):
    """Revisa lo respondido contra las reglas 5 y 6. Devuelve (mensaje, errores, respuestas por punto);
    el mensaje viene vacío si todo está en orden."""
    por_punto = {}
    for r in respuestas or []:
        try:
            por_punto[int(r.get("punto"))] = r
        except (AttributeError, TypeError, ValueError):
            continue

    validos = set(RespuestaPunto.Resultado.values)
    errores_puntos = {}
    sin_responder = sin_observacion = 0
    for p in puntos:
        r = por_punto.get(p.id)
        if not r or r.get("resultado") not in validos:
            errores_puntos[str(p.id)] = f"Falta responder: {p.descripcion}."
            sin_responder += 1
        elif r["resultado"] == RespuestaPunto.Resultado.OBSERVACION and not (r.get("comentario") or "").strip():
            errores_puntos[str(p.id)] = f"Escribe la observación de: {p.descripcion}."
            sin_observacion += 1

    errores, motivos = {}, []
    if errores_puntos:
        errores["puntos"] = errores_puntos
    if sin_responder:
        motivos.append(f"falta responder {_plural(sin_responder, 'punto', 'puntos')} del checklist")
    if sin_observacion:
        motivos.append(f"falta escribir la observación de {_plural(sin_observacion, 'punto', 'puntos')}")
    if operativo is None:
        errores["operativo"] = "Indica si el equipo quedó operativo."
        motivos.append("falta indicar si el equipo quedó operativo")
    elif operativo is False and not (falla_descripcion or "").strip():
        errores["falla_descripcion"] = "Describe la falla: el equipo quedó detenido."
        motivos.append("el equipo quedó detenido, describe la falla")

    mensaje = f"No se guardó: {'; '.join(motivos)}." if motivos else ""
    return mensaje, errores, por_punto


@transaction.atomic
def registrar_mantencion(*, visita_id, respuestas, operativo, falla_descripcion="", observaciones="",
                         id_local=None, guardado_en_dispositivo=None, usuario=None):
    """Valida y guarda. Devuelve (registro, creado)."""
    if id_local:
        existente = RegistroMantencion.objects.filter(id_local=id_local).first()
        if existente:
            return existente, False

    visita = (
        Visita.objects.select_for_update()
        .select_related("ascensor__edificio", "tecnico")
        .filter(pk=visita_id)
        .first()
    )
    if visita is None:
        raise Rechazo("La visita no existe.", estado=404)

    tecnico = tecnico_de(usuario)
    if tecnico is None or tecnico.id != visita.tecnico_id:
        raise Rechazo(
            f"Esta visita está asignada a {visita.tecnico.nombre}. Solo el técnico de la visita registra la mantención.",
            estado=403,
        )

    if visita.estado == Visita.Estado.REALIZADA:
        previo = RegistroMantencion.objects.filter(visita=visita).first()
        if previo and id_local and previo.id_local == id_local:
            # El mismo envío llegó dos veces casi a la vez: no es un segundo registro.
            return previo, False
        cuando = f" el {timezone.localtime(previo.guardado_en_dispositivo):%d-%m-%Y a las %H:%M}" if previo else ""
        raise Rechazo(f"Esta visita ya fue registrada{cuando}. No se puede registrar dos veces.", estado=409)
    if visita.estado != Visita.Estado.PROGRAMADA:
        raise Rechazo("Solo se registran visitas programadas.", estado=409)

    # La hora vale la del celular, que es cuando se hizo la mantención (puede
    # llegar después si no había señal), pero nunca una hora que aún no llega.
    ahora = timezone.now()
    momento = min(guardado_en_dispositivo or ahora, ahora)
    dia = timezone.localtime(momento).date()
    if visita.fecha > dia:
        raise Rechazo(
            f"La visita está programada para el {visita.fecha:%d-%m-%Y}; no se puede registrar antes de esa fecha."
        )
    if (dia.year, dia.month) != (visita.mes.year, visita.mes.month):
        raise Rechazo(
            f"Esta visita era de {MESES[visita.mes.month - 1]} de {visita.mes.year} y ese mes ya terminó. "
            "Avisa al jefe técnico para que la reprograme."
        )

    puntos = list(PuntoChecklist.objects.filter(activo=True))
    mensaje, errores, por_punto = revisar_checklist(puntos, respuestas, operativo, falla_descripcion)
    if mensaje:
        raise Rechazo(mensaje, errores)

    registro = RegistroMantencion.objects.create(
        visita=visita,
        tecnico=visita.tecnico,
        operativo=operativo,
        falla_descripcion=(falla_descripcion or "").strip() if operativo is False else "",
        observaciones=(observaciones or "").strip(),
        guardado_en_dispositivo=momento,
        registrado_por=usuario,
        **({"id_local": id_local} if id_local else {}),
    )
    RespuestaPunto.objects.bulk_create([
        RespuestaPunto(
            registro=registro,
            punto=p,
            resultado=por_punto[p.id]["resultado"],
            comentario=(por_punto[p.id].get("comentario") or "").strip()[:300]
            if por_punto[p.id]["resultado"] == RespuestaPunto.Resultado.OBSERVACION else "",
        )
        for p in puntos
    ])
    visita.estado = Visita.Estado.REALIZADA
    visita.save(update_fields=["estado"])
    return registro, True
