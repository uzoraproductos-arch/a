#!/usr/bin/env python3
"""Baja los Indicadores Estadísticos Judiciales de la DGEJ órgano por órgano.

Debajo de cada tabla por circuito (`dgej-indicadores-circuito.json`, que escribe
`actualizar_indicadores_dgej.py`), el sistema da el mismo indicador para cada
juzgado o tribunal del circuito (`IndicadoresJudicialesOrgano.asp?circuito=N`).
Este script pide esa página para cada cuadro con datos de litigiosidad (nivel 3)
y productividad (nivel 5), cada circuito y cada año, y escribe
`docs/estadistica/dgej-indicadores-organo.json`.

El sistema no da una clave por órgano: da su nombre como lo publica ese año.
Se guarda tal cual; un órgano que cambió de nombre o de materia sale como otro.

Uso:
    python3 herramientas/actualizar_indicadores_organo.py --certs bundle.pem --cache DIR
    python3 herramientas/actualizar_indicadores_organo.py --desde DIR      # solo copias

`--cache` guarda cada página (y la reusa si ya está): la descarga se puede
cortar y retomar. Son unas 12 mil consultas; van de a pocas y con pausa.
"""
import argparse
import concurrent.futures as cf
import hashlib
import html
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ENTRADA = os.path.join(AQUI, '..', 'docs', 'estadistica', 'dgej-indicadores-circuito.json')
SALIDA = os.path.join(AQUI, '..', 'docs', 'estadistica', 'dgej-indicadores-organo.json')
BASE = 'https://www.dgej.cjf.gob.mx/Indicadores/'
NIVELES = ('3', '5')
FILA = re.compile(r'<font[^>]*>\s*(\d+)\s*</font>\s*</div>\s*</td>\s*<td[^>]*>\s*<div[^>]*>\s*<font[^>]*>(.*?)</font>\s*</div>\s*</td>\s*'
                  r'<td[^>]*>\s*<div[^>]*>\s*<font[^>]*>\s*([-\d.,]+)\s*</font>', re.S)


def url_organo(x, circ):
    q = dict(urllib.parse.parse_qsl(x['url'].split('?', 1)[1], encoding='latin-1'))
    q = {'circuito': circ, **q}
    return BASE + 'IndicadoresJudicialesOrgano.asp?' + urllib.parse.urlencode(q, encoding='latin-1')


def lee_organos(raw):
    s = raw.decode('latin-1')
    s = re.sub(r'<script.*?</script>', '', s, flags=re.S)
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    out = []
    for m in FILA.finditer(s):
        nom = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', m.group(2)))).strip()
        out.append((nom, float(m.group(3).replace(',', ''))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--certs', help='paquete de certificados con la raíz ISRG Root YR')
    ap.add_argument('--cache', help='carpeta donde se guarda (y se reusa) cada página')
    ap.add_argument('--desde', help='leer solo copias de esta carpeta, sin red')
    ap.add_argument('--hilos', type=int, default=3)
    a = ap.parse_args()
    ctx = ssl.create_default_context(cafile=a.certs) if a.certs else ssl.create_default_context()
    carpeta = a.desde or a.cache
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    with open(ENTRADA, encoding='utf-8') as f:
        circ = json.load(f)
    tareas = []
    for x in circ['datos']:
        if str(x['niv']) in NIVELES:
            for c in sorted(x['c'], key=int):
                tareas.append((x, c, '%s_%s_%s_%s_%s.html' % (x['ano'], x['org'], x['niv'], x['ind'], c)))

    def baja(t):
        x, c, local = t
        ruta = os.path.join(carpeta, local) if carpeta else None
        if ruta and os.path.exists(ruta):
            with open(ruta, 'rb') as f:
                return t, f.read()
        if a.desde:
            return t, None
        url = url_organo(x, c)
        for intento in range(4):
            try:
                time.sleep(0.4)
                with urllib.request.urlopen(url, context=ctx, timeout=90) as r:
                    raw = r.read()
                break
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                if intento == 3:
                    return t, None
                time.sleep(5 * (intento + 1))
        if ruta:
            with open(ruta, 'wb') as f:
                f.write(raw)
        return t, raw

    nombres, idx, datos, faltan, descuadres = [], {}, [], [], []
    hechos = 0
    with cf.ThreadPoolExecutor(max_workers=max(1, a.hilos)) as ex:
        for (x, c, local), raw in ex.map(baja, tareas):
            hechos += 1
            if hechos % 500 == 0:
                print('  %d de %d' % (hechos, len(tareas)), flush=True)
            if raw is None:
                faltan.append(local)
                continue
            filas = lee_organos(raw)
            v = []
            for nom, val in filas:
                if nom not in idx:
                    idx[nom] = len(nombres)
                    nombres.append(nom)
                v.append([idx[nom], val])
            datos.append({'ano': x['ano'], 'org': x['org'], 'niv': str(x['niv']), 'ind': x['ind'], 'circ': c, 'v': v,
                          'sha256': hashlib.sha256(raw).hexdigest()})
            # Cotejo: en los conteos, la suma de los órganos es la cifra del circuito.
            if filas and x['nac'] is not None and abs(sum(circ_v for circ_v in x['c'].values()) - x['nac']) < 0.5:
                suma = sum(val for _, val in filas)
                if abs(suma - x['c'][c]) > 0.5 and all(float(val).is_integer() for _, val in filas):
                    descuadres.append({'ano': x['ano'], 'org': x['org'], 'niv': str(x['niv']), 'ind': x['ind'], 'circ': c,
                                       'circuito': x['c'][c], 'suma': suma})
    datos.sort(key=lambda d: (d['org'], d['niv'], d['ind'], d['ano'], int(d['circ'])))
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump({'fuente': BASE + 'acuerd_nal_ini.asp', 'consulta': time.strftime('%d-%m-%Y'),
                   'nota': 'Cada renglón de v es [índice en nombres, valor]. El sistema no da clave de órgano: el nombre es el que publica ese año.',
                   'nombres': nombres, 'datos': datos, 'faltan': sorted(faltan), 'descuadres': descuadres},
                  f, ensure_ascii=False, separators=(',', ':'))
        f.write('\n')
    print('detalle por órgano: %d páginas de %d (%d órganos con nombre distinto), %d sin bajar, %d descuadres -> %s'
          % (len(datos), len(tareas), len(nombres), len(faltan), len(descuadres), os.path.relpath(SALIDA)))


if __name__ == '__main__':
    sys.exit(main())
