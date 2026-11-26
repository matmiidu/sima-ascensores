"""Informe mensual de mantención de un edificio (H09, requisito RF-07).

El formato lo fijó la acción A05 (docs/entrega3/a05/acta_A05.md) contra el
artículo 5.9.5 de la OGUC: el mantenedor entrega un informe en cada mantención
con las tareas revisadas, las acciones hechas y las fallas. SIMA programa una
sola mantención al mes por ascensor (H03), así que el informe es mensual, por
edificio, y trae una sección completa por cada ascensor.

Reglas:
- Entran los ascensores activos del edificio y los que tuvieron visita en el mes.
- Si a algún ascensor le falta la mantención del mes, el informe es parcial y
  dice cuándo está programada su visita.
- Los equipos detenidos se nombran en el resumen, además de en su sección.
- El registro del año junta, por ascensor, la fecha y el técnico de cada
  mantención del año hasta el mes del informe (el cuadro anual de la cabina).
"""
from datetime import date, timedelta
from io import BytesIO

from django.conf import settings
from django.db.models import Count, Q
from django.template.loader import render_to_string
from django.utils import timezone

from cartera.models import Ascensor, Edificio
from planificacion.models import Visita

from .models import PuntoChecklist, RegistroMantencion
from .registro import MESES

NOMBRE_CHECKLIST = "checklist de mantención mensual de Ascensores Altavía"
DIAS_POR_VENCER = 60


class MesInvalido(ValueError):
    pass


def leer_mes(texto, hoy):
    """'2026-11' -> date(2026, 11, 1). Sin texto, el mes en curso."""
    if not texto:
        return hoy.replace(day=1)
    try:
        anio, mes = (int(p) for p in texto.split("-"))
        return date(anio, mes, 1)
    except (TypeError, ValueError):
        raise MesInvalido("El mes debe escribirse como AAAA-MM, por ejemplo 2026-11.")


def nombre_mes(mes):
    return f"{MESES[mes.month - 1]} de {mes.year}"


def periodicidad_certificacion(tipo_uso):
    """Cada cuánto se certifica según el destino del edificio (OGUC 5.9.5, numeral 4)."""
    if tipo_uso == Edificio.TipoUso.RESIDENCIAL:
        return "cada 2 años (destino vivienda)"
    if tipo_uso == Edificio.TipoUso.MIXTO:
        return "según el destino predominante del edificio"
    return "cada 1 año (destino equipamiento)"


def estado_certificacion(vencimiento, hoy):
    if vencimiento is None:
        return "sin fecha registrada"
    if vencimiento < hoy:
        return "vencida"
    if vencimiento <= hoy + timedelta(days=DIAS_POR_VENCER):
        return "por vencer"
    return "vigente"


def _ascensores_del_mes(edificio, mes):
    return (Ascensor.objects.filter(edificio=edificio)
            .filter(Q(activo=True) | Q(visitas__mes=mes)).distinct()
            .order_by("identificador"))


def _registro(r):
    return {
        "codigo": r.codigo,
        "fecha": timezone.localtime(r.guardado_en_dispositivo).date(),
        "tecnico": r.tecnico.nombre,
        "operativo": r.operativo,
        "falla": r.falla_descripcion,
        "observaciones": r.observaciones,
        "respuestas": [
            {"codigo": x.punto.codigo, "punto": x.punto.descripcion, "resultado": x.get_resultado_display(),
             "observacion": x.resultado == x.Resultado.OBSERVACION, "comentario": x.comentario}
            for x in r.respuestas.select_related("punto")
        ],
    }


def datos_del_informe(edificio, mes, hoy):
    """Todo lo que lleva el informe del edificio en el mes. None si el edificio no tuvo visitas ese mes."""
    if not Visita.objects.filter(ascensor__edificio=edificio, mes=mes).exists():
        return None
    secciones = []
    for a in _ascensores_del_mes(edificio, mes):
        visita = Visita.objects.filter(ascensor=a, mes=mes).select_related("tecnico").first()
        registro = getattr(visita, "registro", None) if visita else None
        anteriores = (RegistroMantencion.objects
                      .filter(visita__ascensor=a, visita__mes__year=mes.year, visita__mes__lte=mes)
                      .select_related("tecnico", "visita").order_by("visita__mes"))
        secciones.append({
            "ascensor": a,
            "tipo": a.get_tipo_display(),
            "uso": a.get_uso_display(),
            "visita": visita,
            "registro": _registro(registro) if registro else None,
            "certificacion": {
                "vencimiento": a.vencimiento_certificacion,
                "estado": estado_certificacion(a.vencimiento_certificacion, hoy),
            },
            "anio": [
                {"mes": MESES[r.visita.mes.month - 1], "fecha": timezone.localtime(r.guardado_en_dispositivo).date(),
                 "tecnico": r.tecnico.nombre}
                for r in anteriores
            ],
        })
    registradas = [s for s in secciones if s["registro"]]
    detenidos = [s for s in registradas if not s["registro"]["operativo"]]
    faltan = [s for s in secciones if not s["registro"]]
    return {
        "edificio": edificio,
        "tipo_uso": edificio.get_tipo_uso_display(),
        "periodicidad": periodicidad_certificacion(edificio.tipo_uso),
        "mes": mes,
        "nombre_mes": nombre_mes(mes),
        "emitido": hoy,
        "mantenedor": settings.SIMA_MANTENEDOR,
        "checklist": NOMBRE_CHECKLIST,
        "puntos": PuntoChecklist.objects.filter(activo=True).count(),
        "secciones": secciones,
        "registradas": registradas,
        "detenidos": detenidos,
        "faltan": faltan,
        "parcial": bool(faltan),
    }


def generar_pdf(datos):
    """El informe en PDF, desde la plantilla HTML terreno/informe_mensual.html."""
    from xhtml2pdf import pisa  # se importa aquí para que el resto de la API no cargue la biblioteca de PDF

    html = render_to_string("terreno/informe_mensual.html", datos)
    salida = BytesIO()
    resultado = pisa.CreatePDF(html, dest=salida, encoding="utf-8")
    if resultado.err:
        raise RuntimeError("No se pudo generar el PDF del informe.")
    return salida.getvalue()


def nombre_archivo(edificio, mes):
    limpio = "".join(c if c.isalnum() else "_" for c in edificio.nombre).strip("_")
    return f"Informe_{limpio}_{mes:%Y-%m}.pdf"


def informes_del_mes(mes):
    """Lista de edificios con visitas en el mes y cuánto les falta para tener el informe completo."""
    edificios = (Edificio.objects.filter(ascensores__visitas__mes=mes).distinct()
                 .annotate(
                     visitas=Count("ascensores__visitas", filter=Q(ascensores__visitas__mes=mes), distinct=True),
                     registradas=Count("ascensores__visitas__registro",
                                       filter=Q(ascensores__visitas__mes=mes), distinct=True),
                     detenidos=Count("ascensores__visitas__registro",
                                     filter=Q(ascensores__visitas__mes=mes,
                                              ascensores__visitas__registro__operativo=False), distinct=True),
                 )
                 .select_related("tecnico_asignado")
                 .order_by("comuna", "nombre"))
    lista = [
        {
            "id": e.id,
            "nombre": e.nombre,
            "direccion": e.direccion,
            "comuna": e.comuna,
            "tecnico": e.tecnico_asignado.nombre if e.tecnico_asignado else "",
            "administrador": {"nombre": e.administrador_nombre, "correo": e.administrador_correo},
            "visitas": e.visitas,
            "registradas": e.registradas,
            "detenidos": e.detenidos,
            "faltan": e.visitas - e.registradas,
            "completo": e.visitas == e.registradas,
            "archivo": nombre_archivo(e, mes),
        }
        for e in edificios
    ]
    # Primero los informes completos, después los que ya tienen mantenciones y al final los que no tienen ninguna.
    lista.sort(key=lambda x: (not x["completo"], x["registradas"] == 0))
    return {"mes": f"{mes:%Y-%m}", "nombre_mes": nombre_mes(mes), "edificios": lista}
