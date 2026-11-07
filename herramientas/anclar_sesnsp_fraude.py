#!/usr/bin/env python3
"""Ancla las carpetas de investigación por fraude del SESNSP para la dimensión
penal del Planisferio y «El fraude en números» (pedido del autor, 07-11-2026:
«integra las carpetas de fraude del SESNSP»).

Se corre a mano:

    python3 herramientas/anclar_sesnsp_fraude.py <Estatal-Delitos-2015-2025_<corte>.zip>

El ZIP es «2015 - 2025 (Fuero Común - Delitos). Incidencia delictiva estatal»
de la página de datos abiertos del Secretariado Ejecutivo del Sistema Nacional
de Seguridad Pública (PAGINA, abajo), que lo sirve desde su SharePoint. Trae un
CSV (latin-1) con un renglón por año, entidad, tipo, subtipo y modalidad, y una
columna por mes: son las carpetas de investigación que las fiscalías y
procuradurías de los estados reportaron al SESNSP (metodología 2015).

De ahí se suman, por entidad y por año, los renglones del tipo «Fraude». Se
detiene si el CSV no trae sus columnas, si falta una entidad o un mes, si una
entidad no se llama como su clave del INEGI, o si el tipo «Fraude» trae otro
subtipo que «Fraude» (la suma dejaría de ser lo que decimos).

Escribe docs/seguridad/sesnsp-fraude-estatal.json con la huella SHA-256 del ZIP.
"""
import csv
import hashlib
import io
import json
import os
import re
import sys
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'seguridad', 'sesnsp-fraude-estatal.json')
PAGINA = 'https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva'
ENLACE = 'https://sspcgob-my.sharepoint.com/:u:/g/personal/cni_sspc_gob_mx/IQDORskgZaqcSox3W83-KLHZAeTct2NCwzncsRTgnZTBRus?e=xq0UDc'
# Clave del INEGI → (nombre en el CSV del SESNSP, clave de la plataforma).
ENT = {1: ('Aguascalientes', 'AGS'), 2: ('Baja California', 'BC'), 3: ('Baja California Sur', 'BCS'), 4: ('Campeche', 'CAM'),
       5: ('Coahuila de Zaragoza', 'COAH'), 6: ('Colima', 'COL'), 7: ('Chiapas', 'CHIS'), 8: ('Chihuahua', 'CHIH'),
       9: ('Ciudad de México', 'CDMX'), 10: ('Durango', 'DGO'), 11: ('Guanajuato', 'GTO'), 12: ('Guerrero', 'GRO'),
       13: ('Hidalgo', 'HGO'), 14: ('Jalisco', 'JAL'), 15: ('México', 'MÉX'), 16: ('Michoacán de Ocampo', 'MICH'),
       17: ('Morelos', 'MOR'), 18: ('Nayarit', 'NAY'), 19: ('Nuevo León', 'NL'), 20: ('Oaxaca', 'OAX'), 21: ('Puebla', 'PUE'),
       22: ('Querétaro', 'QRO'), 23: ('Quintana Roo', 'QROO'), 24: ('San Luis Potosí', 'SLP'), 25: ('Sinaloa', 'SIN'),
       26: ('Sonora', 'SON'), 27: ('Tabasco', 'TAB'), 28: ('Tamaulipas', 'TAM'), 29: ('Tlaxcala', 'TLAX'),
       30: ('Veracruz de Ignacio de la Llave', 'VER'), 31: ('Yucatán', 'YUC'), 32: ('Zacatecas', 'ZAC')}
MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
COLS = ['Año', 'Clave_Ent', 'Entidad', 'Bien jurídico afectado', 'Tipo de delito', 'Subtipo de delito', 'Modalidad'] + MESES


def main(ruta):
    with open(ruta, 'rb') as f:
        crudo = f.read()
    with zipfile.ZipFile(io.BytesIO(crudo)) as z:
        csvs = [n for n in z.namelist() if n.lower().endswith('.csv')]
        if len(csvs) != 1:
            sys.exit('El ZIP debía traer un solo CSV y trae %d' % len(csvs))
        nombre = csvs[0]
        filas = list(csv.reader(io.StringIO(z.read(nombre).decode('latin-1'))))
    if filas[0] != COLS:
        sys.exit('El CSV cambió de columnas: %s' % filas[0])
    m = re.search(r'Estatal-Delitos-(\d{4})-(\d{4})_(\w+)\.csv$', nombre)
    if not m:
        sys.exit('No reconozco el nombre del archivo: %s' % nombre)
    anios = list(range(int(m.group(1)), int(m.group(2)) + 1))
    est = {a: {} for _, a in ENT.values()}
    for r in filas[1:]:
        cve = int(r[1])
        if cve not in ENT or ENT[cve][0] != r[2]:
            sys.exit('Entidad desconocida o mal nombrada: %s %s' % (r[1], r[2]))
        if r[4] != 'Fraude':
            continue
        if (r[5], r[6]) != ('Fraude', 'Fraude'):
            sys.exit('El tipo «Fraude» trae otro subtipo o modalidad: %s / %s' % (r[5], r[6]))
        if any(v.strip() == '' for v in r[7:]):
            sys.exit('%s %s: le falta un mes de fraude' % (r[0], r[2]))
        a = ENT[cve][1]
        est[a][r[0]] = est[a].get(r[0], 0) + sum(int(v) for v in r[7:])
    for a, x in est.items():
        if sorted(x) != [str(y) for y in anios]:
            sys.exit('%s no trae todos los años: %s' % (a, sorted(x)))
    nac = {str(y): sum(x[str(y)] for x in est.values()) for y in anios}
    doc = {'fuente': ('Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP), incidencia delictiva del fuero común, '
                      'metodología 2015, estatal: carpetas de investigación por fraude que reportaron las fiscalías y procuradurías de los estados'),
           'pagina': PAGINA, 'enlace': ENLACE, 'archivo': os.path.basename(ruta), 'csv': nombre, 'corte': m.group(3),
           'sha': hashlib.sha256(crudo).hexdigest(), 'nacional': nac, 'estados': est}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write('\n')
    u = str(anios[-1])
    print('32 entidades, %d-%d; carpetas por fraude en %s: %s (corte %s)' % (anios[0], anios[-1], u, format(nac[u], ','), m.group(3)))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
