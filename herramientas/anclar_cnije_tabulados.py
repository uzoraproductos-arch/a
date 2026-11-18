#!/usr/bin/env python3
"""El rezago civil, familiar y mercantil de cada estado y lo que tardan los
juzgados federales, de los tabulados básicos del censo judicial (18-11-2026).

Pendientes `judicial-rezago-civil` y `judicial-tiempos-juzgados`. El reporte
de resultados del CNIJF-E 2025 (el que lee gestion_judicial.py) no los trae;
sus tabulados básicos, sí:

- cuadro 16: causas penales y expedientes **pendientes de concluir** en
  primera instancia al 31-12-2024, por entidad, sistema y materia;
- cuadro 13: duración promedio, en días naturales, de los asuntos que
  egresaron de los órganos del Consejo de la Judicatura Federal en 2024.

Uso (se corre a mano, con el libro bajado del INEGI):

    python3 herramientas/anclar_cnije_tabulados.py <cnije2025_imp_just.xlsx>

El libro está en
https://www.inegi.org.mx/contenidos/programas/cnije/2025/tabulados/cnije2025_imp_just.xlsx
y escribe docs/estadistica/cnije-2025-tabulados.json con su huella SHA-256.
Se detiene si:
  - el cuadro 16 no trae a las 32 entidades en el orden de sus claves;
  - una materia no suma, entre las entidades que la reportaron, lo que el
    INEGI da para el país (su nota: «los totales corresponden a la suma de
    las cifras de los casos en los que se contó con datos»);
  - el total de una materia no es la suma de sus dos sistemas, donde los dos
    se conocen;
  - el cuadro 13 no trae sus cuatro grupos de órganos.

«-» quiere decir que el poder judicial no lo sabe (así lo dice el INEGI) y se
guarda como null; «NA», que no aplica, como "NA".
"""
import hashlib
import json
import os
import sys

import openpyxl

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'estadistica', 'cnije-2025-tabulados.json')
URL = 'https://www.inegi.org.mx/contenidos/programas/cnije/2025/tabulados/cnije2025_imp_just.xlsx'
CLAVES = ['AGS', 'BC', 'BCS', 'CAM', 'COAH', 'COL', 'CHIS', 'CHIH', 'CDMX', 'DGO', 'GTO', 'GRO', 'HGO', 'JAL', 'MÉX', 'MICH',
          'MOR', 'NAY', 'NL', 'OAX', 'PUE', 'QRO', 'QROO', 'SLP', 'SIN', 'SON', 'TAB', 'TAM', 'TLAX', 'VER', 'YUC', 'ZAC']
MAT = ['pen', 'ado', 'civ', 'fam', 'mer']
# Columnas del cuadro 16: total (3-8), sistema tradicional o escrito (10-15) y
# sistema acusatorio u oral (17-22); en cada bloque, total y las cinco materias.
COL = {'tot': 4, 'trad': 11, 'oral': 18}
GRUPOS = ['Tribunales Colegiados de Circuito', 'Tribunales Colegiados de Apelación', 'Juzgados de Distrito',
          'Centros de Justicia Penal Federal']


def alto(m):
    raise SystemExit('anclar_cnije_tabulados: ' + m)


def val(v):
    if v == '-':
        return None
    if v == 'NA':
        return 'NA'
    if isinstance(v, (int, float)):
        return int(v) if float(v).is_integer() else round(float(v), 1)
    alto('valor inesperado %r' % (v,))


def num(v):
    return v if isinstance(v, int) else 0


def cuadro16(ws):
    filas = list(ws.iter_rows(values_only=True))
    pais = next(r for r in filas if r[2] == 'Estados Unidos Mexicanos')
    ent = [r for r in filas if r[1] and str(r[1]).isdigit() and len(str(r[1])) == 2]
    if [int(r[1]) for r in ent] != list(range(1, 33)):
        alto('el cuadro 16 no trae a las 32 entidades en orden')
    est = {}
    for clave, r in zip(CLAVES, ent):
        est[clave] = {b: {m: val(r[c + i]) for i, m in enumerate(MAT)} for b, c in COL.items()}
    nac = {b: {m: val(pais[c + i]) for i, m in enumerate(MAT)} for b, c in COL.items()}
    for b in COL:
        for m in MAT:
            s = sum(num(est[k][b][m]) for k in CLAVES)
            if s != num(nac[b][m]):
                alto('%s/%s: las entidades suman %s y el país dice %s' % (b, m, s, nac[b][m]))
    for k in CLAVES:
        for m in MAT:
            t, a, o = est[k]['tot'][m], est[k]['trad'][m], est[k]['oral'][m]
            if isinstance(t, int) and isinstance(a, int) and isinstance(o, int) and t != a + o:
                alto('%s/%s: el total %s no es %s + %s' % (k, m, t, a, o))
    notas = [r[0] for r in filas if isinstance(r[0], str) and (r[0].startswith('Nota') or r[0][:2] in ('8 ', '9 '))]
    # Las llamadas 8 y 9 van pegadas al nombre de la entidad («Coahuila de Zaragoza8»).
    llamada = {}
    for clave, r in zip(CLAVES, ent):
        n = str(r[2]).rstrip()
        if n[-1:] in '89':
            llamada[clave] = next(x for x in notas if x.startswith(n[-1] + ' '))
    if sorted(llamada) != ['CDMX', 'COAH']:
        alto('las llamadas del cuadro 16 cambiaron: %s' % sorted(llamada))
    return {'pais': nac, 'estados': est, 'nota': notas[0], 'llamadas': llamada}


def cuadro13(ws):
    grupos, actual = {}, None
    for r in ws.iter_rows(values_only=True):
        c = [x for x in r if x is not None]
        if not c or not isinstance(c[0], str):
            continue
        if c[0].startswith('Nota'):
            nota = c[0]
            break
        if len(c) == 1 and c[0].strip() in GRUPOS:
            actual = c[0].strip()
            grupos[actual] = []
        elif actual and len(c) == 4:
            grupos[actual].append([c[0].strip()] + [val(x) for x in c[1:]])
    if list(grupos) != GRUPOS or not all(grupos.values()):
        alto('el cuadro 13 no trae sus cuatro grupos: %s' % list(grupos))
    return {'grupos': grupos, 'nota': nota}


def main():
    if len(sys.argv) != 2:
        alto('uso: anclar_cnije_tabulados.py <cnije2025_imp_just.xlsx>')
    ruta = sys.argv[1]
    huella = hashlib.sha256(open(ruta, 'rb').read()).hexdigest()
    wb = openpyxl.load_workbook(ruta, read_only=True)
    out = {
        'fuente': {'tx': 'INEGI, Censo Nacional de Impartición de Justicia Federal y Estatal (CNIJF-E) 2025, tabulados básicos de impartición de justicia',
                   'url': URL, 'sha256': huella, 'archivo': os.path.basename(ruta)},
        'c16': cuadro16(wb['16']),
        'c13': cuadro13(wb['13']),
    }
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write('\n')
    p = out['c16']['pais']['tot']
    print('anclar_cnije_tabulados: %s (%s…). Pendientes civiles %s, familiares %s, mercantiles %s.' % (
        os.path.relpath(SALIDA, RAIZ), huella[:12], p['civ'], p['fam'], p['mer']))


if __name__ == '__main__':
    main()
