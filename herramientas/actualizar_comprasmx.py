#!/usr/bin/env python3
"""Regenera los catalogos de contratos de ComprasMX (assets/auditor/data/comprasmx/).

Pedido del autor (26-10-2026): integrar los contratos de ComprasMX para que el
Auditor pueda «resolver el seguimiento del dinero»: a quien le paga el
gobierno, cuanto, por que procedimiento y donde esta cada contrato.

Uso:
    python3 herramientas/actualizar_comprasmx.py Contratos_ComprasMX_2025.csv Contratos_ComprasMX_2026.csv

Los archivos se descargan, con su boton, de la seccion Datos Abiertos de
ComprasMX («Contratos de la Plataforma Integral Compras MX <año>»):
https://comprasmx.buengobierno.gob.mx/datos-abiertos
Van en Latin-1, un renglon por contrato (Datos Relevantes del Contrato), y el
año del archivo es el del expediente, no el del pago. El diccionario de datos
esta en la misma pagina («Diccionario de datos Compras MX»).

Lo que se escribe (todo se carga en el navegador solo cuando se pregunta):
  indice.js     nombre y RFC de cada persona moral con contratos (buscador).
  p-XX.js       la ficha de cada proveedor, repartida por las dos primeras
                letras de su RFC: contratos, importe, procedimientos, a que
                instituciones les vende, sus 5 contratos mayores con su liga, y
                su situacion en la lista 69-B del SAT si aparece.
  inst.js       por institucion: contratos, importe, adjudicaciones directas
                y sus 10 proveedores mayores.

Reglas de la plataforma (AGENTS.md, §2):
  - El importe de cada contrato es «oficial»: es el «Importe DRC», antes de
    impuestos, tal como lo reporto la institucion. Las sumas y porcentajes
    son «derivado» y lo dicen. No se convierten monedas: lo que no es en
    pesos se suma aparte, por moneda.
  - En un contrato abierto el importe reportado suele ser el maximo, no lo
    pagado: ComprasMX no publica pagos. Lo pagado vive en la Cuenta Publica.
  - Las personas fisicas (RFC de 13 caracteres) no se publican con nombre ni
    RFC: su RFC es un dato personal. Solo cuentan en los totales de cada
    institucion, como «personas fisicas».

Tras regenerar, sube el sello: python3 herramientas/sello.py AAAAMMDDx
"""
import collections
import csv
import datetime
import hashlib
import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'comprasmx')
SAT = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'sat-69b.js')
PAGINA = 'https://comprasmx.buengobierno.gob.mx/datos-abiertos'
DETALLE = 'https://comprasmx.buengobierno.gob.mx/sitiopublico/#/sitiopublico/detalle/%s/procedimiento'
MAX_CONTRATOS = 5
MAX_INST = 5
MAX_PROV_INST = 10

# Columnas del archivo (diccionario de datos Compras MX, 73 columnas).
C = {'orden': 0, 'ramo': 2, 'clave_inst': 4, 'siglas': 5, 'inst': 6, 'tipo_proc': 14, 'codigo': 35,
     'titulo': 37, 'pub': 32, 'importe': 44, 'moneda': 45, 'rfc': 64, 'prov': 65, 'estrato': 70, 'url': 72}


def tipo(t):
    t = t.strip().upper()
    if t.startswith('LICITACI'):
        return 'LP'
    if t.startswith('INVITACI'):
        return 'I3'
    if t.startswith('ADJUDICACI'):
        return 'AD'
    return 'OT'


def num(s):
    try:
        return float(s or 0)
    except ValueError:
        return 0.0


def url_id(u):
    m = re.search(r'/detalle/([0-9a-f]{20,})/', u or '')
    return m.group(1) if m else ''


def sat69b():
    s = open(SAT, encoding='utf-8').read()
    filas = json.loads(s[s.index('"r": [') + 5:].rstrip().rstrip(';').rstrip('}').rstrip())
    return {r[0]: [r[2], r[3], r[4]] for r in filas}


def js(var, clave, datos):
    cuerpo = json.dumps(datos, ensure_ascii=False, separators=(',', ':'))
    if clave is None:
        return '/* Generado por herramientas/actualizar_comprasmx.py. No editar a mano. */\nwindow.%s = %s;\n' % (var, cuerpo)
    return ('/* Generado por herramientas/actualizar_comprasmx.py. No editar a mano. */\n'
            'window.%s = window.%s || {};\nwindow.%s[%s] = %s;\n' % (var, var, var, json.dumps(clave), cuerpo))


def main(rutas):
    if not rutas:
        raise SystemExit(__doc__)
    sat = sat69b()
    prov = {}
    inst = {}
    archivos = []
    vistos = set()
    for ruta in rutas:
        raw = open(ruta, 'rb').read()
        m = re.search(r'(\d{4})', os.path.basename(ruta))
        anio = m.group(1) if m else '?'
        filas = list(csv.reader(io.StringIO(raw.decode('latin-1'), newline='')))
        cab, filas = filas[0], filas[1:]
        if len(cab) != 73 or cab[C['rfc']].lower() != 'rfc' or not cab[C['importe']].startswith('Importe'):
            raise SystemExit('%s: el archivo no trae las 73 columnas del diccionario de ComprasMX' % ruta)
        archivos.append({'archivo': os.path.basename(ruta), 'anio': anio, 'contratos': len(filas),
                         'sha256': hashlib.sha256(raw).hexdigest()})
        for x in filas:
            if len(x) != 73:
                continue
            rfc = x[C['rfc']].strip().upper()
            llave = (x[C['codigo']], rfc)
            if llave in vistos:  # el mismo contrato repetido en el archivo
                continue
            vistos.add(llave)
            imp, mon, tp = num(x[C['importe']]), (x[C['moneda']] or 'MXN').strip().upper(), tipo(x[C['tipo_proc']])
            ci = x[C['clave_inst']].strip()
            i = inst.setdefault(ci, {'s': x[C['siglas']].strip() or ci, 'n': x[C['inst']].strip(), 'o': x[C['orden']].strip(),
                                     'r': x[C['ramo']].strip(), 'c': 0, 'm': 0.0, 'ad': 0, 'mad': 0.0, 'otras': collections.Counter(),
                                     'pf': 0, 'mpf': 0.0, 'pv': collections.defaultdict(lambda: [0, 0.0, ''])})
            i['c'] += 1
            if mon == 'MXN':
                i['m'] += imp
            else:
                i['otras'][mon] += imp
            if tp == 'AD':
                i['ad'] += 1
                if mon == 'MXN':
                    i['mad'] += imp
            if len(rfc) == 13:  # persona fisica: solo cuenta en los totales
                i['pf'] += 1
                if mon == 'MXN':
                    i['mpf'] += imp
                continue
            if len(rfc) != 12:
                continue
            pv = i['pv'][rfc]
            pv[0] += 1
            pv[2] = x[C['prov']].strip()
            if mon == 'MXN':
                pv[1] += imp
            p = prov.setdefault(rfc, {'n': x[C['prov']].strip(), 'c': 0, 'm': 0.0, 'otras': collections.Counter(),
                                      'tp': collections.Counter(), 'mtp': collections.Counter(), 'anios': collections.Counter(),
                                      'inst': collections.defaultdict(lambda: [0, 0.0]), 'k': [], 'e': x[C['estrato']].strip()})
            p['c'] += 1
            p['anios'][anio] += 1
            p['tp'][tp] += 1
            if mon == 'MXN':
                p['m'] += imp
                p['mtp'][tp] += imp
            else:
                p['otras'][mon] += imp
            p['inst'][ci][0] += 1
            if mon == 'MXN':
                p['inst'][ci][1] += imp
            p['k'].append((imp if mon == 'MXN' else 0, x[C['codigo']], ci, x[C['titulo']].strip()[:90], round(imp, 2), mon, tp,
                           x[C['pub']][:10], url_id(x[C['url']])))

    os.makedirs(SALIDA, exist_ok=True)
    for f in os.listdir(SALIDA):
        if f.endswith('.js'):
            os.remove(os.path.join(SALIDA, f))
    hoy = datetime.date.today().isoformat()
    meta = {'fuente': 'ComprasMX, Datos Abiertos: Datos Relevantes de los Contratos (Secretaría Anticorrupción y Buen Gobierno)',
            'url': PAGINA, 'detalle': DETALLE, 'archivos': archivos, 'descarga': hoy,
            'proveedores': len(prov), 'instituciones': len(inst),
            'nota': 'Importe antes de impuestos tal como lo reportó cada institución («Importe DRC»). En contratos abiertos suele ser el máximo; ComprasMX no publica pagos.'}

    # Indice: nombre y RFC de las personas morales.
    idx = sorted([[rfc, p['n']] for rfc, p in prov.items()], key=lambda r: r[1])
    open(os.path.join(SALIDA, 'indice.js'), 'w', encoding='utf-8').write(js('CMX_IDX', None, {'meta': meta, 'r': idx}))

    # Fichas de proveedor, por las dos primeras letras del RFC.
    lotes = collections.defaultdict(dict)
    cruce = []
    for rfc, p in prov.items():
        k = sorted(p['k'], key=lambda t: -t[0])[:MAX_CONTRATOS]
        ins = sorted(p['inst'].items(), key=lambda t: (-t[1][1], -t[1][0]))[:MAX_INST]
        d = {'n': p['n'], 'c': p['c'], 'm': round(p['m'], 2), 'e': p['e'],
             'tp': dict(p['tp']), 'mtp': {a: round(b, 2) for a, b in p['mtp'].items()},
             'a': dict(p['anios']), 'ni': len(p['inst']),
             'i': [[ci, inst[ci]['s'], inst[ci]['n'], v[0], round(v[1], 2)] for ci, v in ins],
             'k': [list(t[1:]) for t in k]}
        if p['otras']:
            d['o'] = {a: round(b, 2) for a, b in p['otras'].items()}
        if rfc in sat:
            d['sat'] = sat[rfc]
            cruce.append([rfc, p['n'], sat[rfc][0], p['c'], round(p['m'], 2)])
        lotes[rfc[:2]][rfc] = d
    for pre, datos in lotes.items():
        nombre = 'p-%s.js' % re.sub(r'[^A-Z0-9]', '_', pre)
        open(os.path.join(SALIDA, nombre), 'w', encoding='utf-8').write(js('CMX_P', pre, datos))

    # Instituciones.
    ins = {}
    for ci, i in inst.items():
        top = sorted(i['pv'].items(), key=lambda t: (-t[1][1], -t[1][0]))[:MAX_PROV_INST]
        d = {'s': i['s'], 'n': i['n'], 'o': i['o'], 'r': i['r'], 'c': i['c'], 'm': round(i['m'], 2),
             'ad': i['ad'], 'mad': round(i['mad'], 2), 'pf': i['pf'], 'mpf': round(i['mpf'], 2),
             'np': len(i['pv']), 'p': [[rfc, v[2], v[0], round(v[1], 2)] for rfc, v in top]}
        if i['otras']:
            d['ot'] = {a: round(b, 2) for a, b in i['otras'].items()}
        ins[ci] = d
    cruce.sort(key=lambda r: -r[4])
    open(os.path.join(SALIDA, 'inst.js'), 'w', encoding='utf-8').write(js('CMX_INST', None, {'meta': meta, 'i': ins, 'sat': cruce}))

    tam = sum(os.path.getsize(os.path.join(SALIDA, f)) for f in os.listdir(SALIDA))
    print('comprasmx: %d contratos, %d personas morales, %d instituciones, %d archivos (%.1f MB), %d proveedores en la lista 69-B'
          % (sum(a['contratos'] for a in archivos), len(prov), len(inst), len(os.listdir(SALIDA)), tam / 1e6, len(cruce)))


if __name__ == '__main__':
    main(sys.argv[1:])
