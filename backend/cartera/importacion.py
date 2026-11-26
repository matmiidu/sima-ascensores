"""Importar la cartera desde la planilla actual de la empresa (H02, requisito RF-09).

La planilla es la que revisó la acción A03 (riesgo R3): una fila por equipo con las columnas Edificio,
Dirección, Comuna, Equipo, Marca, Tipo, Paradas, Vence certificación, Técnico y Observación. Llega como CSV
(separado por punto y coma o por coma) o como Excel (.xlsx).

La importación tiene dos pasos (decisión D20): primero se revisa y se muestra qué pasaría con cada fila, sin
guardar nada; después, si el usuario confirma, se guarda todo junto o nada.

Qué pasa con cada fila:
- nuevo: el equipo no está en la cartera; se crea (y su edificio, si tampoco está).
- actualiza: el equipo ya está y la planilla trae otra marca, tipo, paradas o vencimiento; se corrigen.
- igual: el equipo ya está con los mismos datos; no se toca. Importar dos veces no duplica nada.
- rechazada: no se importa. Motivos: le falta un dato obligatorio, repite un equipo de otra fila (aunque esté
  escrito distinto) o está marcado como retirado o dado de baja.
Además, una fila importable puede traer avisos: comuna corregida a su forma oficial, sin fecha de
certificación (aparecerá en Certificaciones como "sin fecha"), fecha ilegible, paradas o tipo no reconocidos,
técnico desconocido.
"""
import csv
import io
import re
import unicodedata
from datetime import date, datetime

from django.db import transaction

from .models import Ascensor, Edificio, Tecnico

COMUNAS = ["Providencia", "Ñuñoa", "Las Condes", "Santiago", "San Miguel", "La Cisterna", "La Florida", "Macul"]
OBLIGATORIAS = ["Edificio", "Dirección", "Comuna", "Equipo"]
OPCIONALES = ["N°", "Marca", "Tipo", "Paradas", "Vence certificación", "Técnico", "Observación"]
MAX_FILAS = 2000


class PlanillaInvalida(ValueError):
    pass


def normalizar(texto):
    """Para comparar sin importar tildes, mayúsculas, espacios ni 'Avenida' contra 'Av.' (igual que A03)."""
    t = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode().lower()
    t = t.replace("avenida", "av").replace("asc.", "a").replace("ascensor", "a")
    return re.sub(r"[^a-z0-9]", "", t)


def identificador_limpio(texto):
    """'Asc. 1' o 'ascensor 1' se guarda como 'A1'; lo demás, tal cual sin espacios de sobra."""
    t = " ".join(str(texto or "").split())
    m = re.fullmatch(r"(?i)(asc\.?|ascensor)\s*(\w+)", t)
    return f"A{m.group(2)}" if m else t


def leer_fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    texto = str(valor or "").strip()
    for formato in ("%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            pass
    return None


def _celda(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return v if isinstance(v, (date, datetime)) else str(v).strip()


def leer_planilla(contenido, nombre):
    """Lee un CSV o un .xlsx y devuelve una lista de diccionarios con las columnas de la planilla."""
    if nombre.lower().endswith(".xlsx"):
        from openpyxl import load_workbook  # se importa aquí: solo se necesita al importar

        try:
            hoja = load_workbook(io.BytesIO(contenido), read_only=True, data_only=True).worksheets[0]
        except Exception:
            raise PlanillaInvalida("No se pudo leer el archivo de Excel. Guárdalo de nuevo como .xlsx o como CSV.")
        filas = [[_celda(c) for c in fila] for fila in hoja.iter_rows(values_only=True)]
    elif nombre.lower().endswith((".csv", ".txt")):
        try:
            texto = contenido.decode("utf-8-sig")
        except UnicodeDecodeError:
            texto = contenido.decode("latin-1")  # CSV guardado desde Excel en Windows
        separador = ";" if texto.split("\n", 1)[0].count(";") >= texto.split("\n", 1)[0].count(",") else ","
        filas = [[c.strip() for c in f] for f in csv.reader(io.StringIO(texto), delimiter=separador)]
    else:
        raise PlanillaInvalida("La planilla debe ser un archivo .csv o .xlsx.")

    filas = [f for f in filas if any(str(c).strip() for c in f)]
    if not filas:
        raise PlanillaInvalida("La planilla está vacía.")
    encabezado = filas[0]
    columnas = {}
    for i, titulo in enumerate(encabezado):
        for esperada in OBLIGATORIAS + OPCIONALES:
            if normalizar(titulo) == normalizar(esperada) and esperada not in columnas:
                columnas[esperada] = i
    faltan = [c for c in OBLIGATORIAS if c not in columnas]
    if faltan:
        raise PlanillaInvalida(f"A la planilla le falta la columna {', '.join(faltan)}. "
                               f"La primera fila debe tener los títulos: {', '.join(OBLIGATORIAS)}.")
    if len(filas) - 1 > MAX_FILAS:
        raise PlanillaInvalida(f"La planilla tiene más de {MAX_FILAS} filas; divídela en partes.")
    datos = []
    for n, fila in enumerate(filas[1:], start=2):
        d = {c: (fila[i] if i < len(fila) else "") for c, i in columnas.items()}
        d["fila"] = n  # número de fila en la planilla, contando el encabezado
        datos.append(d)
    return datos


TIPOS = {"electrico": "electrico", "electricodetraccion": "electrico", "traccion": "electrico",
         "hidraulico": "hidraulico"}


def _tecnico(nombre, tecnicos):
    clave = normalizar(nombre)
    if not clave:
        return None
    candidatos = [t for t in tecnicos if normalizar(t.nombre).startswith(clave) or normalizar(t.nombre) == clave]
    return candidatos[0] if len(candidatos) == 1 else None


def revisar(filas, tipo_uso=Edificio.TipoUso.RESIDENCIAL):
    """Qué pasaría con cada fila si se importa. No guarda nada."""
    oficiales = {normalizar(c): c for c in COMUNAS}
    tecnicos = list(Tecnico.objects.filter(activo=True))
    edificios = {(normalizar(e.direccion), normalizar(e.comuna)): e for e in Edificio.objects.all()}
    existentes = {}
    for a in Ascensor.objects.select_related("edificio"):
        existentes[(normalizar(a.edificio.direccion), normalizar(a.edificio.comuna), normalizar(a.identificador))] = a
    vistos = {}
    resultado = []
    for f in filas:
        r = {"fila": f["fila"], "edificio": str(f.get("Edificio", "")).strip(), "direccion": str(f.get("Dirección", "")).strip(),
             "comuna": str(f.get("Comuna", "")).strip(), "equipo": identificador_limpio(f.get("Equipo")),
             "estado": "", "motivos": [], "avisos": [], "cambios": []}
        resultado.append(r)
        falta = [c for c in OBLIGATORIAS if not str(f.get(c, "")).strip()]
        if falta:
            r["estado"], r["motivos"] = "rechazada", [f"falta {', '.join(c.lower() for c in falta)}"]
            continue
        comuna = oficiales.get(normalizar(r["comuna"]))
        if comuna is None:
            r["avisos"].append(f"comuna «{r['comuna']}» no está entre las comunas de la empresa; se guarda tal cual")
        elif comuna != r["comuna"]:
            r["avisos"].append(f"comuna corregida: «{r['comuna']}» pasa a «{comuna}»")
            r["comuna"] = comuna
        clave = (normalizar(r["direccion"]), normalizar(r["comuna"]), normalizar(r["equipo"]))
        if clave in vistos:
            r["estado"], r["motivos"] = "rechazada", [f"repite el equipo de la fila {vistos[clave]}"]
            continue
        vistos[clave] = r["fila"]
        observacion = str(f.get("Observación", "")).lower()
        if "retirad" in observacion or "baja" in observacion:
            r["estado"], r["motivos"] = "rechazada", [f"marcado como retirado («{f.get('Observación')}»)"]
            continue

        # Datos del equipo que trae la planilla.
        crudo = f.get("Vence certificación", "")
        vence = leer_fecha(crudo)
        if not str(crudo).strip():
            r["avisos"].append("sin fecha de certificación: quedará en Certificaciones como «sin fecha»")
        elif vence is None:
            r["avisos"].append(f"fecha de certificación ilegible («{crudo}»): se importa sin fecha")
        tipo = TIPOS.get(normalizar(f.get("Tipo", "")))
        if str(f.get("Tipo", "")).strip() and tipo is None:
            r["avisos"].append(f"tipo «{f.get('Tipo')}» no reconocido: se deja como eléctrico de tracción")
        paradas = None
        if str(f.get("Paradas", "")).strip():
            try:
                paradas = int(float(str(f.get("Paradas")).replace(",", ".")))
                if not 2 <= paradas <= 200:
                    raise ValueError
            except ValueError:
                r["avisos"].append(f"paradas «{f.get('Paradas')}» no válidas: se deja en 2")
                paradas = None
        r["datos"] = {"marca": str(f.get("Marca", "")).strip(), "tipo": tipo, "paradas": paradas, "vence": vence}

        existente = existentes.get(clave)
        if existente:
            cambios = []
            if r["datos"]["marca"] and r["datos"]["marca"] != existente.marca:
                cambios.append(f"marca: {existente.marca or 'vacía'} → {r['datos']['marca']}")
            if tipo and tipo != existente.tipo:
                cambios.append(f"tipo: {existente.get_tipo_display()} → {dict(Ascensor.Tipo.choices)[tipo]}")
            if paradas and paradas != existente.paradas:
                cambios.append(f"paradas: {existente.paradas} → {paradas}")
            if vence and vence != existente.vencimiento_certificacion:
                antes = existente.vencimiento_certificacion.strftime("%d-%m-%Y") if existente.vencimiento_certificacion else "sin fecha"
                cambios.append(f"vence: {antes} → {vence:%d-%m-%Y}")
            r["estado"], r["cambios"], r["ascensor_id"] = ("actualiza" if cambios else "igual"), cambios, existente.id
        else:
            r["estado"] = "nuevo"
            edificio = edificios.get(clave[:2])
            r["edificio_existente"] = edificio.id if edificio else None
            if edificio is None:
                t = _tecnico(f.get("Técnico", ""), tecnicos)
                r["tecnico_id"] = t.id if t else None
                if str(f.get("Técnico", "")).strip() and t is None:
                    r["avisos"].append(f"técnico «{f.get('Técnico')}» no reconocido: el edificio queda sin técnico asignado")
    resumen = {e: sum(1 for r in resultado if r["estado"] == e) for e in ("nuevo", "actualiza", "igual", "rechazada")}
    resumen["con_avisos"] = sum(1 for r in resultado if r["avisos"] and r["estado"] != "rechazada")
    resumen["filas"] = len(resultado)
    nuevos_edificios = {(normalizar(r["direccion"]), normalizar(r["comuna"])) for r in resultado
                        if r["estado"] == "nuevo" and not r.get("edificio_existente")}
    resumen["edificios_nuevos"] = len(nuevos_edificios)
    resumen["tipo_uso"] = tipo_uso
    return {"resumen": resumen, "filas": resultado}


@transaction.atomic
def importar(revision):
    """Guarda lo revisado: crea los equipos nuevos (y sus edificios) y corrige los que cambian. Todo o nada."""
    creados_edificios = {}
    tipo_uso = revision["resumen"]["tipo_uso"]
    for r in revision["filas"]:
        d = r.get("datos")
        if r["estado"] == "actualiza":
            a = Ascensor.objects.select_for_update().get(pk=r["ascensor_id"])
            a.marca = d["marca"] or a.marca
            a.tipo = d["tipo"] or a.tipo
            a.paradas = d["paradas"] or a.paradas
            a.vencimiento_certificacion = d["vence"] or a.vencimiento_certificacion
            a.save()
        elif r["estado"] == "nuevo":
            clave = (normalizar(r["direccion"]), normalizar(r["comuna"]))
            edificio = (Edificio.objects.get(pk=r["edificio_existente"]) if r.get("edificio_existente")
                        else creados_edificios.get(clave))
            if edificio is None:
                edificio = Edificio.objects.create(
                    nombre=r["edificio"], direccion=r["direccion"], comuna=r["comuna"], tipo_uso=tipo_uso,
                    tecnico_asignado_id=r.get("tecnico_id"))
                creados_edificios[clave] = edificio
            Ascensor.objects.create(
                edificio=edificio, identificador=r["equipo"], tipo=d["tipo"] or Ascensor.Tipo.ELECTRICO,
                marca=d["marca"], paradas=d["paradas"] or 2, vencimiento_certificacion=d["vence"])
    r = revision["resumen"]
    return {"equipos_nuevos": r["nuevo"], "equipos_actualizados": r["actualiza"], "edificios_nuevos": len(creados_edificios),
            "sin_cambios": r["igual"], "rechazadas": r["rechazada"]}
