#!/usr/bin/env python3
"""Ancla la única cifra oficial de cuánto facturaron las empresas de la lista
69-B (EFOS) para «El fraude en números» (pedido del autor, 07-11-2026:
«continúa con el monto de las EFOS»).

Se corre a mano:

    python3 -I herramientas/anclar_sat_efos.py <comunicado.html>

El archivo es la página del comunicado del SAT del 25-06-2019 en gob.mx
(`URL`, abajo), guardada tal cual. La página cambia en cada descarga (trae
fichas de sesión), así que la huella SHA-256 se toma del **texto del
comunicado** (el cuerpo de la nota, sin etiquetas y con los espacios juntados),
que es lo que no cambia. Se detiene si el texto ya no dice la fecha o alguna de
las cinco cifras que se toman de él:

- 8 mil 204 empresas que facturan operaciones simuladas, de 2014 a la fecha;
- 8 millones 827 mil 390 facturas falsas;
- «un monto aproximado de 1.6 billones de pesos»;
- una evasión de 354 mil 512 millones de pesos, el 1.4 % del PIB.

Lo que el comunicado **no** dice, y por eso no se escribe: si las 8,204 son
las definitivas de la lista o todas las identificadas, el monto exacto, ni
cómo cambió después de junio de 2019. El SAT no ha publicado otra cifra del
monto desde entonces (revisado el 07-11-2026 en su sala de prensa y en el
Informe Tributario y de Gestión del primer trimestre de 2024).

Escribe docs/seguridad/sat-efos-2019.json.
"""
import hashlib
import html
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'seguridad', 'sat-efos-2019.json')
URL = 'https://www.gob.mx/sat/prensa/sat-combate-la-evasion-fiscal-por-operaciones-simuladas_com035'
CIFRAS = [('efos', r'(\d+) mil (\d{3}) empresas que facturan operaciones simuladas'),
          ('facturas', r'(\d+) millones (\d{3}) mil (\d{3}) facturas falsas'),
          ('monto_billones', r'monto aproximado de ([\d.]+) billones de pesos'),
          ('evasion_mdp', r'evasión fiscal de (\d+) mil (\d{3}) millones de pesos'),
          ('evasion_pib', r'representa ([\d.]+)% del Producto Interno Bruto')]


def texto(ruta):
    with open(ruta, encoding='utf-8') as f:
        t = f.read()
    m = re.search(r'class="article-body"[^>]*>(.*?)</div>', t, re.S)
    if not m:
        sys.exit('La página ya no trae el cuerpo del comunicado (article-body)')
    if '25 de junio de 2019' not in t:
        sys.exit('La página ya no dice la fecha del comunicado (25 de junio de 2019)')
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(1)))).strip()


def main(ruta):
    t = texto(ruta)
    d = {}
    for clave, rx in CIFRAS:
        m = re.search(rx, t)
        if not m:
            sys.exit('El comunicado ya no dice la cifra «%s»' % clave)
        d[clave] = float(m.group(1)) if len(m.groups()) == 1 else int(''.join(m.groups()))
    i = t.index('de 2014 a la fecha')
    cita = t[t.rindex('.', 0, i) + 1:t.index('.', t.index('Producto Interno Bruto')) + 1].strip()
    doc = {'fuente': 'SAT, comunicado «SAT combate la evasión fiscal por operaciones simuladas», 25-06-2019',
           'url': URL, 'fecha': '2019-06-25', 'periodo': 'de 2014 al 25-06-2019',
           'sha_texto': hashlib.sha256(t.encode('utf-8')).hexdigest(),
           'cita': cita, **d}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('EFOS: %s; facturas: %s; monto: %s billones; evasión: %s millones (%s %% del PIB)'
          % (format(d['efos'], ','), format(d['facturas'], ','), d['monto_billones'], format(d['evasion_mdp'], ','), d['evasion_pib']))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
