#!/usr/bin/env python3
"""La serie larga de la fiscalización superior: «Estadísticas de la
Fiscalización Superior de la Cuenta Pública en México 2002–2024», de la
Auditoría Superior de la Federación (Dirección General de Informes, Control y
Registro), con corte al 31 de marzo de 2026.

Pedido del autor (04-11-2026): «la serie de la ASF desde la Cuenta Pública
2000». El documento oficial que la reúne empieza en la Cuenta Pública 2002;
2000 y 2001 quedan pendientes con su ficha (pendientes.py, «asf-cp-2000-2001»).

Uso:
    python3 herramientas/extraer_estadisticas_asf.py ESTADISTICAS.pdf

El PDF se descarga de FUENTE['url'] y se verifica contra su sha256. Se leen dos
tablas:
  - p. 10, «Auditorías, Recomendaciones y Acciones por cuenta pública»:
    auditorías, observaciones, recomendaciones y acciones de cada CP.
  - p. 12, «Recomendaciones y Acciones por tipo de acción y cuenta pública»:
    R, PRAS, PO, RD, SA, FRR, PEFCF, DH y PIIC de cada CP.
Se detiene si (1) los tipos no suman el «Total» de cada año, (2) los años no
suman el total de cada tipo, (3) R + RD no es igual a «Recomendaciones» de la
p. 10, o (4) las auditorías no suman 30,600, como dice el texto de la p. 5.
Ojo: el renglón «Acciones» de la p. 10 no es la suma de los tipos de acción de
la p. 12 en todos los años (solo cuadra en las CP 2023 y 2024). El
documento no lo explica; aquí se guardan las dos tal como vienen y la página
lo dice.

Escribe investigaciones/asf-estadisticas-2002-2024.json; lo lee
herramientas/cruce_contratos.py.
"""
import hashlib
import json
import logging
import pathlib
import re
import sys

import pypdf

logging.disable(logging.WARNING)
RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'investigaciones' / 'asf-estadisticas-2002-2024.json'
FUENTE = {
    'doc': 'ASF, Estadísticas de la Fiscalización Superior de la Cuenta Pública en México 2002–2024 (corte al 31 de marzo de 2026)',
    'url': ('https://www.asf.gob.mx/uploads/217_transp_fraccion30/'
            'Estad%C3%ADsticas%20de%20Fiscalizacion%20Superior%20Corte%20al%2031%20de%20marzo%202026_VF.pdf'),
    'sha256': '6dde3582b485dfe9902ae96988085743e6504764e5f6837e6f40ee35894b7f2d',
    'corte': '2026-03-31',
    'emisor': 'Auditoría Superior de la Federación, Secretaría General de Fiscalización Superior, Dirección General de Informes, Control y Registro',
}
ANIOS = list(range(2002, 2025))
TIPOS = ['R', 'PRAS', 'PO', 'RD', 'SA', 'FRR', 'PEFCF', 'DH', 'PIIC']
TOTAL_AUDITORIAS = 30600


def n(t):
    return 0 if t == '-' else int(t.replace(',', ''))


def tabla_grupos(txt):
    filas = {}
    for linea in txt.split('\n'):
        tk = linea.split()
        if len(tk) == 8 and re.match(r'^20\d\d$', tk[0]):
            a = int(tk[0])
            filas[a] = {'auditorias': n(tk[1]), 'observaciones': n(tk[2]),
                        'recomendaciones': n(tk[4]), 'acciones': n(tk[6])}
    if sorted(filas) != ANIOS:
        sys.exit('p. 10: no encontré los 23 años (%s)' % sorted(filas))
    return filas


def tabla_tipos(txt):
    filas = {}
    for linea in txt.split('\n'):
        tk = linea.split()
        if tk and tk[0] in TIPOS + ['Total'] and len(tk) == 25:
            filas[tk[0]] = [n(x) for x in tk[1:]]
    if sorted(filas) != sorted(TIPOS + ['Total']):
        sys.exit('p. 12: faltan renglones (%s)' % sorted(filas))
    for t in TIPOS + ['Total']:
        if sum(filas[t][:23]) != filas[t][23]:
            sys.exit('p. 12: los años de %s no suman su total' % t)
    for i, a in enumerate(ANIOS):
        if sum(filas[t][i] for t in TIPOS) != filas['Total'][i]:
            sys.exit('p. 12: los tipos de %d no suman el total del año' % a)
    return filas


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pdf = pathlib.Path(sys.argv[1])
    raw = pdf.read_bytes()
    h = hashlib.sha256(raw).hexdigest()
    if h != FUENTE['sha256']:
        sys.exit('%s: sha256 distinto (%s); el documento cambió: revísalo y actualiza FUENTE' % (pdf.name, h))
    r = pypdf.PdfReader(str(pdf))
    if 'Corte al 31 de marzo de 2026' not in r.pages[0].extract_text():
        sys.exit('la portada no dice el corte esperado')
    g = tabla_grupos(r.pages[9].extract_text())
    t = tabla_tipos(r.pages[11].extract_text())
    if sum(x['auditorias'] for x in g.values()) != TOTAL_AUDITORIAS:
        sys.exit('las auditorías no suman %d' % TOTAL_AUDITORIAS)
    serie = []
    for i, a in enumerate(ANIOS):
        d = {'cp': a}
        d.update(g[a])
        d.update({k: t[k][i] for k in TIPOS})
        d['totalTipos'] = t['Total'][i]
        if d['R'] + d['RD'] != d['recomendaciones']:
            sys.exit('CP %d: R + RD no es igual a las recomendaciones de la p. 10' % a)
        d['accionesCuadran'] = d['totalTipos'] - d['recomendaciones'] == d['acciones']
        serie.append(d)
    doc = dict(FUENTE)
    doc.update({'paginas': {'grupos': 10, 'tipos': 12},
                'nota': ('«Acciones» (p. 10) y la suma de los tipos de acción (p. 12) solo cuadran en las CP 2023 y 2024; '
                         'en las demás difieren y el documento no explica por qué. Se guardan las dos como vienen.'),
                'serie': serie})
    SALIDA.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('escrito %s: CP %d a %d, %d auditorías' % (SALIDA.relative_to(RAIZ), ANIOS[0], ANIOS[-1], TOTAL_AUDITORIAS))
    print('acciones que no cuadran con los tipos:', [d['cp'] for d in serie if not d['accionesCuadran']])


if __name__ == '__main__':
    main()
