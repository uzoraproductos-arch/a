#!/usr/bin/env python3
"""Regenera assets/data/sat-69b.js desde el listado oficial del SAT.

Uso:
    python3 herramientas/actualizar_69b.py              # descarga el CSV
    python3 herramientas/actualizar_69b.py archivo.csv  # usa un CSV local

El SAT publica el «Listado completo de contribuyentes (Artículo 69-B del
CFF)», que reúne a quienes presuntamente facturan operaciones inexistentes
(EFOS). El archivo va en Latin-1, con dos renglones de encabezado antes de
los nombres de columna. Aquí se conserva, por contribuyente, lo que un
ciudadano necesita para citarlo: RFC, nombre, situación y el oficio y la
fecha de publicación en el DOF de esa situación.

Tras regenerar, sube el sello: python3 herramientas/sello.py AAAAMMDDx
"""
import csv
import datetime
import hashlib
import io
import json
import os
import re
import sys
import urllib.request

URL_CSV = "http://omawww.sat.gob.mx/cifras_sat/Documents/Listado_Completo_69-B.csv"
URL_PAGINA = ("https://www.gob.mx/sat/acciones-y-programas/notificacion-a-contribuyentes-"
              "con-operaciones-presuntamente-inexistentes-y-listados-definitivos-333336")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "assets", "data", "sat-69b.js")

# Columna (base cero) donde empieza cada etapa: oficio y fecha en la página
# del SAT, luego oficio y fecha en el DOF. Se prefiere el DOF; si la etapa
# aún no sale publicada ahí, se usa la página del SAT y se dice.
ETAPAS = {
    "Presunto": ("P", 4),
    "Desvirtuado": ("D", 8),
    "Definitivo": ("F", 12),
    "Sentencia Favorable": ("S", 16),
}


def leer(ruta):
    if ruta:
        with open(ruta, "rb") as f:
            return f.read()
    with urllib.request.urlopen(URL_CSV, timeout=120) as r:
        return r.read()


def main():
    raw = leer(sys.argv[1] if len(sys.argv) > 1 else None)
    texto = raw.decode("latin-1")
    filas = list(csv.reader(io.StringIO(texto)))
    corte = re.search(r"actualizada al ([^;]+);", filas[0][0])
    cab = filas[2]
    if cab[1] != "RFC" or cab[3] != "Situación del contribuyente":
        sys.exit("El SAT cambió el formato del CSV: revisa las columnas antes de seguir.")

    registros, cuenta = [], {}
    for f in filas[3:]:
        if len(f) < 20 or not f[1].strip():
            continue
        sit = f[3].strip()
        if sit not in ETAPAS:
            sys.exit("Situación desconocida: %r" % sit)
        clave, c = ETAPAS[sit]
        medio = "DOF" if f[c + 3].strip() else "SAT"
        o, d = (c + 2, c + 3) if medio == "DOF" else (c, c + 1)
        oficio = f[o].split(" de fecha")[0].strip()
        registros.append([f[1].strip().upper(), " ".join(f[2].split()), clave, oficio, f[d].strip(), medio])
        cuenta[sit] = cuenta.get(sit, 0) + 1

    meta = {
        "fuente": "SAT, Listado completo de contribuyentes (Artículo 69-B del CFF)",
        "url": URL_PAGINA,
        "csv": URL_CSV,
        "corte": corte.group(1).strip() if corte else "",
        "descarga": datetime.date.today().isoformat(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "total": len(registros),
        "porSituacion": cuenta,
        "situaciones": {
            "P": "Presunto", "D": "Desvirtuado", "F": "Definitivo", "S": "Sentencia Favorable",
        },
    }
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    cuerpo = ("/* Generado por herramientas/actualizar_69b.py. No editar a mano. */\r\n"
              "window.SAT_69B = {\"meta\": " + json.dumps(meta, ensure_ascii=False) + ",\r\n"
              "\"r\": [\r\n" +
              ",\r\n".join(json.dumps(r, ensure_ascii=False) for r in registros) +
              "\r\n]};\r\n")
    with open(SALIDA, "wb") as f:
        f.write(cuerpo.encode("utf-8"))
    print("%d contribuyentes, corte %s, %s bytes" % (len(registros), meta["corte"], os.path.getsize(SALIDA)))
    print(cuenta)


if __name__ == "__main__":
    main()
