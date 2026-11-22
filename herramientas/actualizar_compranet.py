#!/usr/bin/env python3
"""El histórico de contratos de CompraNet, cruzado con la lista 69-B del SAT.

Pedido del autor (04-11-2026): «integra el histórico de contratos de CompraNet
(upcp-compranet.hacienda.gob.mx)». CompraNet fue la plataforma de compras del
gobierno federal hasta abril de 2025, cuando la sustituyó ComprasMX (que ya
integra actualizar_comprasmx.py). Sus Datos Abiertos traen un archivo de
contratos por año.

Uso:
    python3 herramientas/actualizar_compranet.py Contratos2019.zip Contratos2020.csv ...

Acepta CSV o ZIP con CSV dentro (UTF-8 o Latin-1). El año de cada archivo sale
de su nombre. Las columnas se reconocen por su encabezado (COLUMNAS, sin
acentos ni mayúsculas): los archivos de CompraNet cambiaron de diccionario con
los años, y los más viejos no traen RFC. Si falta el proveedor, el importe o
una fecha, el programa se detiene: no se adivina una columna.

Qué se escribe: assets/auditor/data/compranet/cruce.js (window.CNET_CRUCE).
No es el catálogo completo (pesaría cientos de MB): son
  - por año, cuántos contratos trae el archivo y su importe en pesos
    (suma derivada; lo que no es en pesos se cuenta aparte, sin convertir);
  - los contratos de las personas morales que aparecen en la lista 69-B, con
    su fecha de firma (si falta, la de inicio), para compararla contra la
    fecha del DOF en herramientas/cruce_contratos.py.

Cómo se cruza (AGENTS.md §2 y §2 bis):
  - Con RFC en el archivo, por RFC: la coincidencia es exacta.
  - Sin RFC (archivos viejos), por el nombre normalizado, y solo si en la lista
    69-B hay una sola persona moral con ese nombre. Se marca «nombre»: es una
    coincidencia más débil y la página lo dice.
  - Las personas físicas no se publican (su RFC es dato personal): un RFC de 13
    caracteres no entra, y sin RFC solo se compara contra personas morales.

Tras regenerar: python3 herramientas/sello.py --siguiente
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
import unicodedata
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'compranet')
SAT = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'sat-69b.js')
PORTAL = 'https://upcp-compranet.hacienda.gob.mx/'

# Encabezados aceptados para cada dato, ya normalizados (norm_cab).
COLUMNAS = {
    'rfc': ['rfc', 'rfc_proveedor', 'rfc_del_proveedor'],
    'prov': ['proveedor_contratista', 'proveedor_o_contratista', 'razon_social', 'nombre_del_proveedor'],
    'importe': ['importe_contrato', 'importe_del_contrato', 'importe_drc', 'importe'],
    'moneda': ['moneda', 'moneda_del_contrato'],
    'firma': ['fecha_de_firma_del_contrato', 'fecha_firma_contrato', 'fecha_firma', 'fecha_celebracion',
              'fecha_de_celebracion', 'fecha_de_celebracion_del_contrato'],
    'inicio': ['fecha_inicio', 'fecha_de_inicio_del_contrato', 'fecha_inicio_contrato'],
    'codigo': ['codigo_contrato', 'codigo_del_contrato', 'numero_de_contrato', 'num_contrato'],
    'siglas': ['siglas', 'siglas_de_la_institucion', 'siglas_dependencia'],
    'inst': ['dependencia', 'institucion', 'nombre_de_la_institucion', 'dependencia_entidad'],
    'tipo': ['tipo_procedimiento', 'tipo_de_procedimiento'],
    'titulo': ['titulo_contrato', 'titulo_del_contrato', 'descripcion_contrato'],
    'url': ['anuncio', 'direccion_del_anuncio', 'url_anuncio'],
}
OBLIGATORIAS = ['prov', 'importe']
SUFIJOS = re.compile(r'\b(S ?A ?P ?I|S ?A ?B|S ?A|S ?C|S ?DE ?R ?L|S ?R ?L|S ?DE ?S ?S|S ?A ?S|A ?C|DE|C ?V|MI|S ?P ?R|I ?A ?P)\b')


def sin_acentos(t):
    return ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')


def norm_cab(t):
    return re.sub(r'[^a-z0-9]+', '_', sin_acentos(t.strip().lower())).strip('_')


def norm_nombre(t):
    t = re.sub(r'[^A-Z0-9 ]+', ' ', sin_acentos(t.upper()))
    t = SUFIJOS.sub(' ', ' '.join(t.split()))
    return ' '.join(t.split())


def fecha(s):
    s = (s or '').strip()
    for f in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y'):
        try:
            return datetime.datetime.strptime(s[:10], f).date().isoformat()
        except ValueError:
            pass
    return ''


def num(s):
    try:
        return float(re.sub(r'[,$\s]', '', s or '') or 0)
    except ValueError:
        return None


def tipo(t):
    t = sin_acentos(t or '').strip().upper()
    if t.startswith('LICITACI'):
        return 'LP'
    if t.startswith('INVITACI'):
        return 'I3'
    if t.startswith('ADJUDICACI'):
        return 'AD'
    return 'OT'


def sat69b():
    s = open(SAT, encoding='utf-8').read()
    filas = json.loads(s[s.index('"r": [') + 5:].rstrip().rstrip(';').rstrip('}').rstrip())
    morales = {r[0]: r for r in filas if len(r[0]) == 12}
    por_nombre = collections.defaultdict(list)
    for r in morales.values():
        por_nombre[norm_nombre(r[1])].append(r[0])
    return morales, {k: v[0] for k, v in por_nombre.items() if len(v) == 1 and k}


def textos(ruta):
    """(nombre, bytes) de cada CSV: el archivo mismo o los que trae el ZIP."""
    raw = open(ruta, 'rb').read()
    if zipfile.is_zipfile(ruta):
        with zipfile.ZipFile(ruta) as z:
            for n in z.namelist():
                if n.lower().endswith('.csv'):
                    yield n, z.read(n), raw
    else:
        yield os.path.basename(ruta), raw, raw


def decodifica(b):
    try:
        return b.decode('utf-8-sig')
    except UnicodeDecodeError:
        return b.decode('latin-1')


def columnas(cab):
    nc = [norm_cab(c) for c in cab]
    idx = {}
    for k, alias in COLUMNAS.items():
        for a in alias:
            if a in nc:
                idx[k] = nc.index(a)
                break
    faltan = [k for k in OBLIGATORIAS if k not in idx]
    if 'firma' not in idx and 'inicio' not in idx:
        faltan.append('fecha de firma o de inicio')
    return idx, faltan


def leer(rutas, morales, por_nombre):
    anios, archivos, cruce = {}, [], collections.defaultdict(lambda: {'k': []})
    for ruta in rutas:
        m = re.search(r'(20\d\d)', os.path.basename(ruta))
        if not m:
            raise SystemExit('%s: el nombre del archivo debe decir el año' % ruta)
        anio = m.group(1)
        for nombre, b, raw in textos(ruta):
            filas = csv.reader(io.StringIO(decodifica(b), newline=''))
            cab = next(filas)
            idx, faltan = columnas(cab)
            if faltan:
                raise SystemExit('%s: no reconozco las columnas de %s. Encabezados: %s'
                                 % (nombre, ', '.join(faltan), '; '.join(cab)))
            a = anios.setdefault(anio, {'c': 0, 'm': 0.0, 'otras': collections.Counter(), 'rfc': 'rfc' in idx,
                                        'sinFecha': 0, 'conInicio': 0})
            vistos, n = set(), 0
            for x in filas:
                if len(x) < len(cab):
                    continue
                g = lambda k: x[idx[k]].strip() if k in idx else ''
                llave = (g('codigo'), g('rfc'), g('prov'))
                if g('codigo') and llave in vistos:
                    continue
                vistos.add(llave)
                n += 1
                imp, mon = num(g('importe')) or 0.0, (g('moneda') or 'MXN').upper()
                mon = 'MXN' if mon in ('MXN', 'PESO MEXICANO', 'PESOS', 'MN') else mon
                a['c'] += 1
                if mon == 'MXN':
                    a['m'] += imp
                else:
                    a['otras'][mon] += imp
                rfc = g('rfc').upper()
                if rfc:
                    if len(rfc) != 12 or rfc not in morales:
                        continue
                    por = 'rfc'
                else:
                    rfc = por_nombre.get(norm_nombre(g('prov')))
                    if not rfc:
                        continue
                    por = 'nombre'
                f = fecha(g('firma'))
                if not f and fecha(g('inicio')):
                    f = fecha(g('inicio'))
                    a['conInicio'] += 1
                if not f:
                    a['sinFecha'] += 1
                c = cruce[rfc]
                c['n'] = morales[rfc][1]
                c['k'].append([g('codigo'), g('siglas') or g('inst')[:40], g('titulo')[:90], round(imp, 2), mon,
                               tipo(g('tipo')), f, anio, por, g('url')])
            archivos.append({'archivo': nombre, 'anio': anio, 'contratos': n, 'sha256': hashlib.sha256(raw).hexdigest()})
    return anios, archivos, cruce


def main(rutas):
    if not rutas:
        raise SystemExit(__doc__)
    morales, por_nombre = sat69b()
    anios, archivos, cruce = leer(rutas, morales, por_nombre)
    meta = {'fuente': 'CompraNet (Secretaría de Hacienda), Datos Abiertos: contratos por año', 'url': PORTAL,
            'archivos': archivos, 'descarga': datetime.date.today().isoformat(),
            'anios': {k: {'c': v['c'], 'm': round(v['m'], 2), 'otras': {a: round(b, 2) for a, b in v['otras'].items()},
                          'rfc': v['rfc'], 'sinFecha': v['sinFecha'], 'conInicio': v['conInicio']} for k, v in sorted(anios.items())},
            'nota': ('Importe como lo reportó cada institución en CompraNet; en contratos abiertos suele ser el máximo. '
                     'CompraNet no publica pagos.')}
    p = {rfc: {'n': c['n'], 'k': sorted(c['k'], key=lambda t: t[6] or t[7])} for rfc, c in cruce.items()}
    os.makedirs(SALIDA, exist_ok=True)
    cuerpo = json.dumps({'meta': meta, 'p': p}, ensure_ascii=False, separators=(',', ':'))
    open(os.path.join(SALIDA, 'cruce.js'), 'w', encoding='utf-8').write(
        '/* Generado por herramientas/actualizar_compranet.py. No editar a mano. */\nwindow.CNET_CRUCE = %s;\n' % cuerpo)
    print('compranet: %d contratos en %d años; %d personas morales de la lista 69-B con contratos (%d contratos)'
          % (sum(v['c'] for v in anios.values()), len(anios), len(p), sum(len(v['k']) for v in p.values())))


if __name__ == '__main__':
    main(sys.argv[1:])
