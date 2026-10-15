"""Acción A03 (riesgo R3): revisa la planilla actual de la empresa y elige la
muestra de 20 equipos que se valida contra terreno.

Detecta, sin modificar la planilla:
- equipos repetidos (misma dirección y equipo, aunque estén escritos distinto),
- fechas de certificación vacías o ilegibles,
- comunas que no coinciden con la forma oficial,
- equipos marcados como retirados.

La muestra toma hasta 10 filas sospechosas, primero las de mayor impacto
(repetidos y retirados, que generan visitas de más; luego fechas vacías), y
completa con filas al azar hasta 20, para estimar también el error de las
filas "limpias".

Uso:
    python validar_planilla.py planilla_actual.csv carpeta_salida/
"""
import csv
import random
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

COMUNAS = ["Providencia", "Ñuñoa", "Las Condes", "Santiago", "San Miguel", "La Cisterna", "La Florida", "Macul"]
TAMANO_MUESTRA = 20


def normalizar(texto):
    t = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()
    t = t.replace("avenida", "av").replace("asc.", "a")
    return re.sub(r"[^a-z0-9]", "", t)


def leer_fecha(valor):
    for formato in ("%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y"):
        try:
            return datetime.strptime(valor.strip(), formato).date()
        except ValueError:
            pass
    return None


def revisar(filas):
    oficiales = {normalizar(c): c for c in COMUNAS}
    vistos = {}
    hallazgos = []
    for f in filas:
        problemas = []
        clave = (normalizar(f["Dirección"]), normalizar(f["Equipo"]))
        if clave in vistos:
            problemas.append(f"repetido de la fila {vistos[clave]}")
        else:
            vistos[clave] = f["N°"]
        if not f["Vence certificación"].strip():
            problemas.append("sin fecha de certificación")
        elif leer_fecha(f["Vence certificación"]) is None:
            problemas.append("fecha ilegible")
        comuna = oficiales.get(normalizar(f["Comuna"]))
        if comuna is None:
            problemas.append("comuna desconocida")
        elif comuna != f["Comuna"]:
            problemas.append(f"comuna mal escrita (es {comuna})")
        if "retirad" in f["Observación"].lower() or "baja" in f["Observación"].lower():
            problemas.append("marcado como retirado")
        hallazgos.append(problemas)
    return hallazgos


def main(origen, salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    with open(origen, encoding="utf-8-sig", newline="") as fh:
        filas = list(csv.DictReader(fh, delimiter=";"))
    hallazgos = revisar(filas)

    def prioridad(i):
        texto = " ".join(hallazgos[i])
        return (0 if "repetido" in texto or "retirado" in texto else 1 if "sin fecha" in texto else 2, i)

    sospechosas = sorted((i for i, h in enumerate(hallazgos) if h), key=prioridad)
    limpias = [i for i, h in enumerate(hallazgos) if not h]
    rng = random.Random(20261019)
    elegidas = sospechosas[:10]
    elegidas += rng.sample(limpias, TAMANO_MUESTRA - len(elegidas))
    elegidas.sort(key=lambda i: (filas[i]["Comuna"].lower(), filas[i]["Edificio"].lower()))

    columnas = ["N°", "Edificio", "Dirección", "Comuna", "Equipo", "Vence certificación",
                "Hallazgo en planilla", "¿Existe en terreno?", "Identificador en terreno",
                "Vencimiento según placa", "Comentario"]
    with open(salida / "muestra_terreno.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for i in elegidas:
            w.writerow({**filas[i], "Hallazgo en planilla": "; ".join(hallazgos[i]) or "sin observaciones"})

    tipos = {}
    for h in hallazgos:
        for p in h:
            tipo = p.split(" (")[0].split(" de la fila")[0]
            tipos[tipo] = tipos.get(tipo, 0) + 1
    with open(salida / "resumen_planilla.txt", "w", encoding="utf-8") as fh:
        fh.write(f"Filas en la planilla: {len(filas)}\n")
        fh.write(f"Filas con al menos un problema: {len(sospechosas)}\n")
        for tipo, n in sorted(tipos.items(), key=lambda x: -x[1]):
            fh.write(f"  {tipo}: {n}\n")
        fh.write(f"Muestra para terreno: {len(elegidas)} filas "
                 f"({min(10, len(sospechosas))} sospechosas y {TAMANO_MUESTRA - min(10, len(sospechosas))} al azar)\n")
    print((salida / "resumen_planilla.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
