#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ancla las carpetas de investigación por fraude de cada municipio de México
(2025 completo y enero-octubre 2026) desde los archivos oficiales municipales
del Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP).

Genera assets/auditor/js/municipios-fraude.js (window.AUDIT_MUN_FRAUDE) en LF
puro, siguiendo la misma estructura de municipios-poblacion.js:
  por clave INEGI de 5 dígitos: [carpetas_2025, carpetas_2026_ene_oct].

Cuadre estricto (AGENTS.md §2):
- La suma de los municipios (incluidos los «No Especificado» xx998 reportados
  por el SESNSP) debe coincidir exactamente con el total nacional de cada año
  (108,736 en 2025; 103,830 en enero-octubre 2026).

Uso:
    python3 herramientas/anclar_fraude_municipios.py sesnsp_mun_2015_2025.zip sesnsp_mun_2026.zip
"""
import collections
import csv
import hashlib
import io
import json
import pathlib
import sys
import zipfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'assets' / 'auditor' / 'js' / 'municipios-fraude.js'
PAGINA = 'https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva'
MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


def leer_fraude(zpath, csv_name, anio=None):
    b = zpath.read_bytes()
    sha = hashlib.sha256(b).hexdigest()
    por_mun = collections.Counter()
    por_ent = collections.Counter()
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        with z.open(csv_name) as f:
            rdr = csv.DictReader(io.TextIOWrapper(f, encoding='latin-1'))
            for row in rdr:
                if anio is not None and (row.get('Año') or '').strip() != str(anio):
                    continue
                if (row.get('Tipo de delito') or '').strip().lower() != 'fraude':
                    continue
                cve = str(row.get('Cve. Municipio') or '').strip().zfill(5)
                s = sum(int(float(row.get(m) or 0)) for m in MESES if m in row)
                por_mun[cve] += s
                por_ent[cve[:2]] += s
    return por_mun, por_ent, sha, len(b)


def main():
    if len(sys.argv) < 3:
        raise SystemExit('Uso: python3 herramientas/anclar_fraude_municipios.py <zip_2015_2025> <zip_2026>')
    z25 = pathlib.Path(sys.argv[1])
    z26 = pathlib.Path(sys.argv[2])

    m25, e25, sha25, b25 = leer_fraude(z25, 'Municipal-Delitos-2015-2025_oct2026.csv', anio=2025)
    m26, e26, sha26, b26 = leer_fraude(z26, 'RNID-Delitos_Municipal-2026-oct2026.csv', anio=None)

    tot25 = sum(m25.values())
    tot26 = sum(m26.values())
    if tot25 != sum(e25.values()) or tot26 != sum(e26.values()):
        raise SystemExit('anclar_fraude_municipios: la suma por entidad no cuadra con la suma municipal')
    if tot25 != 108736:
        raise SystemExit('anclar_fraude_municipios: el total 2025 (%d) no coincide con el corte estatal oficial (108,736)' % tot25)

    # Separar claves territoriales vs «No Especificado» (terminación >= 990)
    claves = sorted(set(m25.keys()) | set(m26.keys()))
    mun = {}
    no_esp = {}
    for c in claves:
        v25, v26 = int(m25.get(c, 0)), int(m26.get(c, 0))
        if int(c[2:]) >= 990:
            if v25 or v26:
                no_esp[c] = [v25, v26]
        else:
            mun[c] = [v25, v26]

    # Verificación de cuadre total
    if sum(v[0] for v in mun.values()) + sum(v[0] for v in no_esp.values()) != tot25:
        raise SystemExit('anclar_fraude_municipios: descuadre interno en 2025')
    if sum(v[1] for v in mun.values()) + sum(v[1] for v in no_esp.values()) != tot26:
        raise SystemExit('anclar_fraude_municipios: descuadre interno en 2026')

    meta = {
        'fuente': 'SESNSP, Datos Abiertos de Incidencia Delictiva Municipal del Fuero Común (corte octubre de 2026)',
        'pagina': PAGINA,
        'delito': 'Fraude',
        'corte2025': 'enero-diciembre 2025',
        'corte2026': 'enero-octubre 2026',
        'sha256_2025': sha25,
        'sha256_2026': sha26,
        'bytes_2025': b25,
        'bytes_2026': b26,
        'nacional': [tot25, tot26],
        'ent': {k: [int(e25.get(k, 0)), int(e26.get(k, 0))] for k in sorted(set(e25.keys()) | set(e26.keys()))},
        'noEspecificado': no_esp,
    }
    cab = (
        '/* ===================================================================\n'
        '   AUDITAVISION - Carpetas por fraude en cada municipio (SESNSP)\n'
        '   -------------------------------------------------------------------\n'
        '   Generado por herramientas/anclar_fraude_municipios.py. No se edita\n'
        '   a mano. SESNSP, Incidencia Delictiva Municipal del Fuero Comun.\n'
        '   Por clave INEGI de cinco digitos: [carpetas 2025, ene-oct 2026].\n'
        '   =================================================================== */\n'
        'window.AUDIT_MUN_FRAUDE = {\n'
    )
    meta_lines = ', '.join('"%s": %s' % (k, json.dumps(v, ensure_ascii=False)) for k, v in meta.items())
    mun_lines = ',\n'.join('    "%s": [%d, %d]' % (c, v[0], v[1]) for c, v in mun.items())
    out = cab + '  ' + meta_lines + ',\n  "mun": {\n' + mun_lines + '\n  }\n};\n'
    SALIDA.write_bytes(out.encode('utf-8'))
    print('municipios-fraude.js: %d municipios + %d noEspecificado | 2025=%s | ene-oct 2026=%s | LF puro' % (
        len(mun), len(no_esp), format(tot25, ','), format(tot26, ',')))


if __name__ == '__main__':
    main()
