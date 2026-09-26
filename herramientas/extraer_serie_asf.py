#!/usr/bin/env python3
"""Serie histórica de la fiscalización superior: el renglón «Total» de la
Matriz de Datos Básicos (MDB) consolidada de cada Cuenta Pública, de 2019 a
2023. La de 2024 ya la lee extraer_mdb_asf.py.

Uso:
    python3 herramientas/extraer_serie_asf.py CARPETA_CON_LOS_PDF

La carpeta debe contener mdb2019.pdf ... mdb2023.pdf, descargados de las
ligas de FUENTES (cada uno se verifica contra su sha256).

Dos formatos:
  - CP 2019 a 2022: tras las acciones vienen tres montos, «Montos
    observados», «Recuperaciones totales» y «Montos por aclarar».
  - CP 2023 (como la 2024): sólo «Recuperaciones» y «Montos por aclarar».
    El observado se deriva como su suma y se marca así.
Los montos vienen en miles de pesos; aquí se guardan en pesos. Si las seis
acciones no suman el total, u observado no es recuperado + por aclarar, el
programa se detiene: una fila mal leída no llega a la base.
Escribe investigaciones/asf-mdb-serie.json; integrar_cuenta_publica.py lo lee.
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
SALIDA = RAIZ / 'investigaciones' / 'asf-mdb-serie.json'
ASF = 'https://www.asf.gob.mx/Trans/Informes/'

FUENTES = {
    2019: {'url': ASF + 'IR2019c/Documentos/Matriz/IR2019b.pdf', 'pagina': 9,
           'sha256': '0367910412bd729089ce4a632b7414a8ef88bf8a708cd9e7ac6b1d3fb84319a9'},
    2020: {'url': ASF + 'IR2020c/Documentos/Matriz/MDB_Consolidado.pdf', 'pagina': 9,
           'sha256': 'c425e450a96c5fc6d13429f18420a8cdaa3edb7d0b1f15fb8615a13a62492d1e'},
    2021: {'url': ASF + 'IR2021c/Documentos/Matriz/MDB_Consolidado.pdf', 'pagina': 13,
           'sha256': '513145012d27125a0bf23ef565a61a5090ccecc97b223da5ae599fba7790110c'},
    2022: {'url': ASF + 'IR2022c/Documentos/Matriz/MDB_Consolidado.pdf', 'pagina': 13,
           'sha256': '97002cffa4f73b98ed3f8c5f78fc10ef365829ae142ae11b6dec304be99bdedc'},
    2023: {'url': ASF + 'IR2023c/Documentos/Matriz/MDB_Consolidado.pdf', 'pagina': 13,
           'sha256': '8c77465b147545c513c474292dc6352d8a0f45a638d214a41b7dca8eb45493e9'},
}
ACC = ['R', 'RD', 'PEFCF', 'SA', 'PRAS', 'PO']


def num(t):
    return float(t.replace(',', '').rstrip('%'))


def total(pdf, pagina, anio):
    txt = pypdf.PdfReader(str(pdf)).pages[pagina - 1].extract_text()
    for linea in txt.split('\n'):
        tk = linea.split()
        if not tk or tk[0] != 'Total' or not re.match(r'^[\d,]+$', tk[1] if len(tk) > 1 else ''):
            continue
        v = tk[1:]
        if not re.search(r'CUENTA PÚBLICA %d' % anio, txt):
            sys.exit('%d: la página %d no es de la Cuenta Pública %d' % (anio, pagina, anio))
        if len(v) == 19:      # 2019-2022
            d = {'auditorias': int(num(v[0])), 'universo': num(v[1]) * 1000, 'muestra': num(v[2]) * 1000,
                 'representatividad': num(v[3])}
            d.update(dict(zip(ACC, (int(num(x)) for x in v[8:14]))))
            d['acciones'] = int(num(v[14]))
            d['observado'] = round(num(v[16]) * 1000, 2)
            d['recuperaciones'] = round(num(v[17]) * 1000, 2)
            d['porAclarar'] = round(num(v[18]) * 1000, 2)
            d['observadoEstado'] = 'oficial'
        elif len(v) == 16:    # 2023 en adelante
            d = {'auditorias': int(num(v[0])), 'universo': num(v[1]) * 1000, 'muestra': num(v[2]) * 1000,
                 'representatividad': num(v[3])}
            d.update(dict(zip(ACC, (int(num(x)) for x in v[6:12]))))
            d['acciones'] = int(num(v[12]))
            d['recuperaciones'] = round(num(v[14]) * 1000, 2)
            d['porAclarar'] = round(num(v[15]) * 1000, 2)
            d['observado'] = round(d['recuperaciones'] + d['porAclarar'], 2)
            d['observadoEstado'] = 'derivado'
        else:
            sys.exit('%d: el renglón Total trae %d columnas, se esperaban 16 o 19' % (anio, len(v)))
        if sum(d[k] for k in ACC) != d['acciones']:
            sys.exit('%d: las seis acciones no suman el total (%d)' % (anio, d['acciones']))
        if abs(d['observado'] - d['recuperaciones'] - d['porAclarar']) > 200:
            sys.exit('%d: observado no es recuperado + por aclarar' % anio)
        return d
    sys.exit('%d: no se encontró el renglón Total en la página %d' % (anio, pagina))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    carpeta = pathlib.Path(sys.argv[1])
    serie = []
    for anio, f in FUENTES.items():
        pdf = carpeta / ('mdb%d.pdf' % anio)
        h = hashlib.sha256(pdf.read_bytes()).hexdigest()
        if h != f['sha256']:
            sys.exit('%s: sha256 distinto (%s); el documento cambió' % (pdf.name, h))
        d = total(pdf, f['pagina'], anio)
        d.update({'cp': anio, 'url': f['url'], 'pagina': f['pagina'], 'sha256': h})
        serie.append(d)
        print('CP %d: %d auditorías · observado %.1f mdp · recuperado %.1f · por aclarar %.1f · PO %d'
              % (anio, d['auditorias'], d['observado'] / 1e6, d['recuperaciones'] / 1e6, d['porAclarar'] / 1e6, d['PO']))
    SALIDA.write_text(json.dumps({'serie': serie}, ensure_ascii=False, indent=1), encoding='utf-8')
    print('escrito', SALIDA.relative_to(RAIZ))


if __name__ == '__main__':
    main()
