#!/usr/bin/env python3
"""Señales de fraccionamiento en las adjudicaciones directas por monto (ComprasMX).

Pedido del autor (03-11-2026, Fase 1, punto 3 del plan B2B): un algoritmo que
detecte contratos partidos para no pasar del tope de la adjudicación directa.

Uso:
    python3 herramientas/fraccionamiento.py CONTRATOS_COMPRASMX_2025.CSV CONTRATOS_COMPRASMX_2026.CSV
    python3 herramientas/fraccionamiento.py ... --dof PEF_2025.html PEF_2026.html   # coteja el Anexo 9

Los CSV son los mismos de actualizar_comprasmx.py (Datos Abiertos de
ComprasMX). Las páginas del DOF son las del decreto de cada año
(https://dof.gob.mx/2024/SHCP/PEF_2025.html y https://dof.gob.mx/2025/SHCP/PEF_2026.html):
con --dof, el script lee su Anexo 9 y se detiene si no es la tabla de ANEXO9.

Lo que dice la ley:
  - LAASSP, art. 55: se puede adjudicar directo «cuando el importe de cada
    operación no exceda los montos máximos» del PEF, «siempre que las
    operaciones no se fraccionen».
  - Reglamento de la LAASSP (DOF 18-12-2025), art. 111: hay fraccionamiento
    cuando (I) todas se fundan en el art. 55 y su suma supera el monto máximo
    del PEF, (II) los bienes o servicios son exactamente los mismos, (III) es
    un solo ejercicio fiscal, (IV) se pudieron prever en un solo procedimiento
    y (V) las pide la misma área requirente.
  - PEF 2025 y 2026, art. 3, fr. X y Anexo 9: el monto máximo depende del
    presupuesto de adquisiciones de cada dependencia (14 escalones), y el
    Comité de cada una fija su escalón (Reglamento, art. 41, apartado A).

La regla (criterio nuestro, decidido por el autor el 03-11-2026):
  Se juntan las adjudicaciones directas «por montos máximos» de la LAASSP con
  la misma unidad compradora, la misma empresa y la misma partida específica,
  en el mismo año (cada contrato, por debajo del tope más alto), y se busca la ventana de 90 días con la suma mayor (dos o
  más contratos). La suma se compara contra los topes del Anexo 9:
    A  rebasa el tope más alto (el de la dependencia más grande): es señal
       sea cual sea el escalón de la dependencia;
    B  rebasa el tope más bajo, no el más alto: depende del escalón de la
       dependencia, que la plataforma aún no tiene (pendiente);
    C  no rebasa ni el más bajo: sin señal.
  La partida es un sustituto de la fr. II (no dice que sean «exactamente los
  mismos» bienes), la unidad compradora lo es de la fr. V (el archivo no trae
  el área requirente) y la fr. IV no se puede medir con datos: por eso es una
  SEÑAL para revisar, nunca una irregularidad ni un dictamen.
  Un contrato «por monto» que por sí solo rebasa el tope más alto no es pieza
  de nada: se cuenta aparte («solos»), porque puede ser un error de captura o
  un procedimiento mal clasificado en ComprasMX.

Se excluyen: las personas físicas (no se publican, AGENTS.md §2 bis), los
contratos marco, las compras consolidadas, los contratos que no son en pesos
(no se convierten monedas) y la obra pública (la LOPSRM tiene su propio
reglamento; queda para otra entrega). El importe es el «Importe DRC», antes de
impuestos, como el Anexo 9. La fecha es la de firma; si falta, la de
publicación, y se cuenta cuántas veces pasó.

Escribe assets/auditor/data/fraccionamiento.js (window.CMX_FRACC), que leen
contratos-publicos.html#fraccionamiento (apartados.py) y el chat
(fraccCmx() de asistente.js). Tras regenerar, sube el sello.
"""
import collections
import csv
import datetime
import hashlib
import html
import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'fraccionamiento.js')
DETALLE = 'https://comprasmx.buengobierno.gob.mx/sitiopublico/#/sitiopublico/detalle/%s/procedimiento'
VENTANA = 90  # días; criterio de la plataforma, no de la ley (la ley dice «un solo ejercicio fiscal»)

# Anexo 9 del PEF, adquisiciones, arrendamientos y servicios, en miles de pesos
# sin IVA: (presupuesto de adquisiciones «mayor de», «hasta», monto máximo de
# cada operación por adjudicación directa, por invitación a cuando menos tres).
ANEXO9 = {
    '2025': {
        'doc': 'Decreto de Presupuesto de Egresos de la Federación para el Ejercicio Fiscal 2025, art. 3, fr. X, y Anexo 9',
        'url': 'https://dof.gob.mx/2024/SHCP/PEF_2025.html', 'ley': 'art. 42 de la LAASSP anterior',
        'sha256': '53ccd6d56f97e7fd23f578b4e0022f0b7791a2620b6847b6f6ee80e79e1d0df5',
        'filas': [(0, 15000, 297, 2178), (15000, 30000, 329, 2540), (30000, 50000, 361, 2860), (50000, 100000, 375, 3129),
                  (100000, 150000, 472, 4171), (150000, 250000, 532, 4952), (250000, 350000, 599, 5884), (350000, 450000, 658, 6776),
                  (450000, 600000, 669, 7239), (600000, 750000, 745, 8513), (750000, 1000000, 758, 9070),
                  (1000000, 1250000, 865, 11069), (1250000, 1500000, 981, 13172), (1500000, None, 1098, 15420)]},
    '2026': {
        'doc': 'Decreto de Presupuesto de Egresos de la Federación para el Ejercicio Fiscal 2026, art. 3, fr. X, y Anexo 9',
        'url': 'https://dof.gob.mx/2025/SHCP/PEF_2026.html', 'ley': 'art. 55 de la LAASSP',
        'sha256': 'c648b151313dfcdb0b4611429154edc1d417191cb32f1af2913eeab107da5655',
        'filas': [(0, 15000, 309, 2272), (15000, 30000, 343, 2649), (30000, 50000, 376, 2983), (50000, 100000, 391, 3264),
                  (100000, 150000, 492, 4351), (150000, 250000, 554, 5165), (250000, 350000, 624, 6138), (350000, 450000, 686, 7068),
                  (450000, 600000, 697, 7551), (600000, 750000, 777, 8880), (750000, 1000000, 790, 9461),
                  (1000000, 1250000, 902, 11547), (1250000, 1500000, 1023, 13741), (1500000, None, 1145, 16086)]},
}
LEY = {'texto': 'Ley de Adquisiciones, Arrendamientos y Servicios del Sector Público, art. 55 (DOF 16-04-2025)',
       'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LAASSP.pdf'}
REGLAMENTO = {'texto': 'Reglamento de la LAASSP (DOF 18-12-2025), arts. 41, apartado A, y 111',
              'url': 'https://www.diputados.gob.mx/LeyesBiblio/regley/Reg_LAASSP_orig_18dic25.doc',
              'sha256': '48a0a46a304fd8c7a64ffa2187be60e2d41469cc0696473858da8056131ce5f5'}

# Columnas del diccionario de ComprasMX (las mismas de actualizar_comprasmx.py).
C = {'clave_inst': 4, 'siglas': 5, 'inst': 6, 'uc': 7, 'uc_n': 8, 'partida': 12, 'ley': 13, 'tipo_proc': 14,
     'marco': 17, 'consolidada': 18, 'pub': 32, 'codigo': 35, 'firma': 43, 'importe': 44, 'moneda': 45,
     'firma2': 49, 'rfc': 64, 'url': 72}


def topes(anio):
    f = ANEXO9[anio]['filas']
    return f[0][2] * 1000.0, f[-1][2] * 1000.0


def revisar_tabla():
    """La tabla escrita aquí tiene que ser continua y creciente, como la del DOF."""
    for anio, d in ANEXO9.items():
        f = d['filas']
        if len(f) != 14:
            raise SystemExit('Anexo 9 %s: deben ser 14 escalones' % anio)
        for a, b in zip(f, f[1:]):
            if a[1] != b[0] or b[2] <= a[2] or b[3] <= a[3]:
                raise SystemExit('Anexo 9 %s: los escalones no son continuos o no crecen (%s → %s)' % (anio, a, b))


def cotejar_dof(anio, ruta):
    """Lee el Anexo 9 de la página del DOF y lo compara contra ANEXO9."""
    raw = open(ruta, 'rb').read()
    s = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', raw.decode('utf-8', 'replace'))))
    i = s.find('ANEXO 9. MONTOS M')
    j = s.find('Obras Públicas y Servicios Relacionados', i)
    if i < 0 or j < 0:
        raise SystemExit('%s: no encontré el Anexo 9 en la página del DOF' % ruta)
    nums = [int(x.replace(',', '')) for x in re.findall(r'\d[\d,]*', s[s.find('Mayor de Hasta', i):j])]
    filas = ANEXO9[anio]['filas']
    esperado = [filas[0][1], filas[0][2], filas[0][3]]
    for a, b, ad, i3 in filas[1:]:
        esperado += [a] + ([b] if b else []) + [ad, i3]
    if nums != esperado:
        raise SystemExit('%s: el Anexo 9 del DOF no coincide con ANEXO9[%s]\n DOF: %s\n aquí: %s' % (ruta, anio, nums, esperado))
    h = hashlib.sha256(raw).hexdigest()
    if h != ANEXO9[anio]['sha256']:
        print('aviso: la página del DOF %s cambió de huella (%s); la tabla sí coincide' % (anio, h[:12]))
    print('Anexo 9 %s: coincide con el DOF' % anio)


def num(s):
    try:
        return float((s or '').replace(',', '').strip())
    except ValueError:
        return None


def fecha(s):
    try:
        return datetime.date.fromisoformat((s or '').strip()[:10])
    except ValueError:
        return None


def url_id(u):
    m = re.search(r'/detalle/([0-9a-f]{20,})/', u or '')
    return m.group(1) if m else ''


def mejor_ventana(L):
    """La ventana de VENTANA días con la suma mayor y al menos dos contratos."""
    L.sort(key=lambda t: t[0])
    best, bi, bj, i, s = 0.0, 0, -1, 0, 0.0
    for j in range(len(L)):
        s += L[j][1]
        while (L[j][0] - L[i][0]).days > VENTANA:
            s -= L[i][1]
            i += 1
        if j > i and s > best:
            best, bi, bj = s, i, j
    return best, L[bi:bj + 1] if bj >= 0 else []


def main(args):
    dof = []
    if '--dof' in args:
        k = args.index('--dof')
        dof, args = args[k + 1:], args[:k]
    if not args:
        raise SystemExit(__doc__)
    revisar_tabla()
    for ruta in dof:
        m = re.search(r'(2025|2026)', os.path.basename(ruta))
        if not m:
            raise SystemExit('%s: el nombre debe decir el año (2025 o 2026)' % ruta)
        cotejar_dof(m.group(1), ruta)

    archivos, vistos = [], set()
    excl = collections.Counter()
    grupos = collections.defaultdict(list)
    inst = {}
    solos = collections.Counter()
    for ruta in args:
        raw = open(ruta, 'rb').read()
        filas = list(csv.reader(io.StringIO(raw.decode('latin-1'), newline='')))
        cab, filas = filas[0], filas[1:]
        if len(cab) != 73 or cab[C['rfc']].lower() != 'rfc' or not cab[C['importe']].startswith('Importe') \
                or not cab[C['marco']].startswith('Contrato marco') or not cab[C['consolidada']].startswith('Compra consolidada'):
            raise SystemExit('%s: el archivo no trae las 73 columnas del diccionario de ComprasMX' % ruta)
        m = re.search(r'(\d{4})', os.path.basename(ruta))
        archivos.append({'archivo': os.path.basename(ruta), 'anio': m.group(1) if m else '?', 'contratos': len(filas),
                         'sha256': hashlib.sha256(raw).hexdigest()})
        for x in filas:
            if len(x) != 73:
                continue
            tp = x[C['tipo_proc']].strip().upper()
            if not (tp.startswith('ADJUDICACI') and 'MONTOS M' in tp):
                continue
            rfc = x[C['rfc']].strip().upper()
            llave = (x[C['codigo']], rfc)
            if llave in vistos:
                continue
            vistos.add(llave)
            excl['ad_monto'] += 1
            if x[C['ley']].strip() != 'LAASSP':
                excl['obra pública u otra ley'] += 1
                continue
            if len(rfc) == 13:
                excl['persona física'] += 1
                continue
            if len(rfc) != 12:
                excl['sin RFC válido'] += 1
                continue
            if x[C['marco']].strip():
                excl['contrato marco'] += 1
                continue
            if x[C['consolidada']].strip().upper() == 'SI':
                excl['compra consolidada'] += 1
                continue
            if (x[C['moneda']] or 'MXN').strip().upper() != 'MXN':
                excl['otra moneda'] += 1
                continue
            v = num(x[C['importe']])
            if not v or v <= 0:
                excl['sin importe'] += 1
                continue
            d = fecha(x[C['firma']]) or fecha(x[C['firma2']])
            if not d:
                d = fecha(x[C['pub']])
                excl['fecha de publicación en lugar de firma'] += 1
            if not d or str(d.year) not in ANEXO9:
                excl['fecha fuera de 2025 y 2026'] += 1
                continue
            anio = str(d.year)
            excl['revisadas'] += 1
            ci = x[C['clave_inst']].strip()
            inst.setdefault(ci, (x[C['siglas']].strip() or ci, x[C['inst']].strip()))
            if v > topes(anio)[1]:  # por sí solo rebasa el tope más alto: no es una pieza de un contrato partido
                solos[(anio, ci)] += 1
                continue
            grupos[(anio, ci, x[C['uc']].strip(), rfc, x[C['partida']].strip())].append(
                (d, v, x[C['codigo']].strip(), url_id(x[C['url']]), x[C['uc_n']].strip()))

    tot = {a: {'A': [0, 0, 0.0], 'B': [0, 0, 0.0], 'C': [0, 0, 0.0], 'ejercicio': [0, 0, 0.0], 'solos': 0} for a in ANEXO9}
    por_inst = collections.defaultdict(lambda: {a: {'A': [0, 0, 0.0], 'B': [0, 0, 0.0], 'g': []} for a in ANEXO9})
    for (anio, ci, uc, rfc, partida), L in grupos.items():
        if len(L) < 2:
            continue
        lo, hi = topes(anio)
        anual = sum(t[1] for t in L)
        if anual > hi:
            e = tot[anio]['ejercicio']
            e[0] += 1
            e[1] += len(L)
            e[2] += anual
        s, V = mejor_ventana(L)
        if len(V) < 2:
            continue
        cl = 'A' if s > hi else 'B' if s > lo else 'C'
        t = tot[anio][cl]
        t[0] += 1
        t[1] += len(V)
        t[2] += s
        if cl == 'C':
            continue
        p = por_inst[ci][anio][cl]
        p[0] += 1
        p[1] += len(V)
        p[2] += s
        if cl == 'A':
            por_inst[ci][anio]['g'].append([V[0][4][:90], partida, round(s, 2), V[0][0].isoformat(), V[-1][0].isoformat(),
                                            [[c, round(v, 2), d.isoformat(), u] for d, v, c, u, _ in V]])
    for (anio, ci), n in solos.items():
        tot[anio]['solos'] += n

    lista = []
    for ci, d in por_inst.items():
        fila = {'k': ci, 's': inst[ci][0], 'n': inst[ci][1]}
        for a in ANEXO9:
            x = d[a]
            fila[a] = {'A': [x['A'][0], x['A'][1], round(x['A'][2], 2)], 'B': [x['B'][0], x['B'][1], round(x['B'][2], 2)],
                       'solos': solos.get((a, ci), 0), 'g': sorted(x['g'], key=lambda g: -g[2])}
        if any(fila[a]['A'][0] or fila[a]['B'][0] for a in ANEXO9):
            lista.append(fila)
    lista.sort(key=lambda f: -sum(f[a]['A'][2] for a in ANEXO9))
    for a in ANEXO9:
        for k in ('A', 'B', 'C', 'ejercicio'):
            tot[a][k][2] = round(tot[a][k][2], 2)
        if sum(f[a]['A'][0] for f in lista) != tot[a]['A'][0]:
            raise SystemExit('%s: los grupos A por institución no suman el total' % a)

    meta = {'fuente': 'ComprasMX, Datos Abiertos: Datos Relevantes de los Contratos (Secretaría Anticorrupción y Buen Gobierno)',
            'url': 'https://comprasmx.buengobierno.gob.mx/datos-abiertos', 'detalle': DETALLE, 'archivos': archivos,
            'generado': datetime.date.today().isoformat(), 'ventana': VENTANA,
            'anexo9': {a: {'doc': d['doc'], 'url': d['url'], 'ley': d['ley'], 'sha256': d['sha256'],
                           'min': d['filas'][0][2] * 1000, 'max': d['filas'][-1][2] * 1000, 'filas': d['filas']} for a, d in ANEXO9.items()},
            'ley': LEY, 'reglamento': REGLAMENTO, 'conteo': dict(excl)}
    cuerpo = json.dumps({'meta': meta, 'tot': tot, 'i': lista}, ensure_ascii=False, separators=(',', ':'))
    open(SALIDA, 'w', encoding='utf-8', newline='\n').write(
        '/* Generado por herramientas/fraccionamiento.py. No editar a mano. */\nwindow.CMX_FRACC = %s;\n' % cuerpo)
    for a in ANEXO9:
        t = tot[a]
        print('%s: A %d grupos (%d contratos, $%.1f M) · B %d · C %d · ejercicio %d · solos %d'
              % (a, t['A'][0], t['A'][1], t['A'][2] / 1e6, t['B'][0], t['C'][0], t['ejercicio'][0], t['solos']))
    print('conteo:', dict(excl))
    print('%s: %d instituciones, %.0f KB' % (os.path.relpath(SALIDA, RAIZ), len(lista), os.path.getsize(SALIDA) / 1e3))


# --- La sección de contratos-publicos.html (la llama apartados.contratos_publicos()). ---
PEND = 'fracc-escalon'


def datos():
    t = open(SALIDA, encoding='utf-8').read()
    return json.loads(t[t.index('{'):t.rindex('}') + 1])


def _n(x):
    return format(int(x), ',')


def _mdp(v):
    return '$%s mdp' % format(round(v / 1e6, 1), ',.1f')


def _miles(v):
    return '$%s' % format(int(v), ',')


def seccion():
    d = datos()
    M, T = d['meta'], d['tot']
    of = '<span class="est-chip est-oficial">oficial</span>'
    de = '<span class="est-chip est-derivado">calculada</span>'
    pe = '<span class="est-chip est-pendiente" data-pend="%s">pendiente</span>' % PEND
    anios = sorted(T)
    cifras = ''.join(
        '<div><b>%s grupos</b><span>%s: suman más que el tope más alto en %d días (%s contratos, %s)</span>%s</div>'
        % (_n(T[a]['A'][0]), a, M['ventana'], _n(T[a]['A'][1]), _mdp(T[a]['A'][2]), de) for a in anios)
    cifras += ''.join(
        '<div><b>%s grupos</b><span>%s: rebasan el tope más bajo pero no el más alto. Depende del escalón de cada dependencia</span>%s</div>'
        % (_n(T[a]['B'][0]), a, pe) for a in anios)
    topes_li = ''.join(
        '<li><b>%s</b>: entre <b>%s</b> (dependencia con presupuesto de adquisiciones de hasta $15 millones) y <b>%s</b> '
        '(más de $1,500 millones) por cada operación, sin IVA %s. <a href="%s" target="_blank" rel="noopener">%s ↗</a> (remite al %s).</li>'
        % (a, _miles(M['anexo9'][a]['min']), _miles(M['anexo9'][a]['max']), of, M['anexo9'][a]['url'], M['anexo9'][a]['doc'], M['anexo9'][a]['ley'])
        for a in anios)
    top = []
    for f in d['i']:
        g = sum(f[a]['A'][0] for a in anios)
        if not g:
            continue
        top.append('<li><b>%s</b> <small>(%s)</small>: %s · <span>pregúntale al Auditor «señales de fraccionamiento de %s»</span></li>' % (
            html.escape(f['n']), html.escape(f['s']),
            '; '.join('%s, %s grupo%s (%s)' % (a, _n(f[a]['A'][0]), '' if f[a]['A'][0] == 1 else 's', _mdp(f[a]['A'][2])) for a in anios if f[a]['A'][0]),
            html.escape(f['s'])))
        if len(top) == 10:
            break
    k = M['conteo']
    arch = ''.join('<li><b>%s</b> <small>(sha256 %s…)</small></li>' % (a['archivo'], a['sha256'][:12]) for a in M['archivos'])
    return {
        'id': 'fraccionamiento', 'titulo': 'Contratos partidos: señales de fraccionamiento',
        'texto': ('La ley prohíbe partir una compra en varias adjudicaciones directas para no pasar del tope. '
                  'Buscamos los grupos que lo parecen. Es una señal para revisar, no una irregularidad.'),
        'tarjetas': [],
        'bloque': (
            '<div class="cmx-metodo">\n'
            '          <div class="cmx-cifras">%s</div>\n'
            '          <h3>Qué dice la ley</h3>\n'
            '          <ul>\n'
            '            <li>Se puede adjudicar directo «cuando el importe de cada operación no exceda los montos máximos» del Presupuesto de Egresos, '
            '«siempre que las operaciones no se fraccionen» (<a href="%s" target="_blank" rel="noopener">%s ↗</a>).</li>\n'
            '            <li>El <a href="%s" target="_blank" rel="noopener">%s ↗</a> dice cuándo hay fraccionamiento: (I) todas son adjudicaciones por monto y su suma supera el tope; '
            '(II) los bienes o servicios son exactamente los mismos; (III) es un solo ejercicio fiscal; (IV) se pudieron prever en un solo procedimiento; '
            'y (V) las pide la misma área.</li>\n'
            '            <li>El tope depende del tamaño de la dependencia (14 escalones del Anexo 9 del PEF), y el Comité de cada una fija en cuál está:</li>\n'
            '          </ul>\n'
            '          <ul>%s</ul>\n'
            '          <h3>Cómo lo buscamos</h3>\n'
            '          <ul>\n'
            '            <li>Tomamos las adjudicaciones directas «por montos máximos» de la ley de adquisiciones (%s revisadas, solo empresas) y juntamos las de la '
            '<b>misma unidad compradora, la misma empresa y la misma partida</b>, en el mismo año.</li>\n'
            '            <li>Buscamos la ventana de <b>%d días</b> con la suma mayor y la comparamos contra el tope. Los %d días son criterio nuestro, más estricto que la ley, '
            'que mira todo el ejercicio: en el año completo, los grupos que rebasan el tope más alto son %s.</li>\n'
            '            <li>Rebasar el tope más alto es señal sea cual sea el tamaño de la dependencia. Entre el más bajo y el más alto, '
            'falta saber el escalón de cada una %s.</li>\n'
            '            <li>Aparte: %s contratos registrados «por monto» que <b>por sí solos</b> rebasan el tope más alto %s. No son piezas de nada: '
            'pueden ser un error de captura o un procedimiento mal clasificado en ComprasMX.</li>\n'
            '          </ul>\n'
            '          <h3>Dónde aparecen más señales</h3>\n'
            '          <ol class="cmx-lista">%s</ol>\n'
            '          <h3>Lo que esta señal no dice</h3>\n'
            '          <ul>\n'
            '            <li><b>No es una irregularidad.</b> La partida junta bienes parecidos, no «exactamente los mismos»; el archivo no trae el área que los pidió; '
            'y si se pudieron prever juntos (fr. IV) no se ve en los datos. Puede haber explicación: entregas distintas o necesidades que no se podían prever.</li>\n'
            '            <li><b>No se nombra a las empresas.</b> Cada grupo lleva las ligas de sus contratos a ComprasMX, donde se pueden revisar.</li>\n'
            '            <li><b>Fuera de la cuenta:</b> personas físicas (%s, no se publican), contratos marco, compras consolidadas (%s), contratos en otra moneda (%s) '
            'y obra pública (%s; su ley tiene otro reglamento y queda para otra entrega).</li>\n'
            '            <li><b>Fechas:</b> %s contratos no traen fecha de firma; en esos usamos la de publicación.</li>\n'
            '            <li><b>El importe</b> es el «Importe DRC», antes de impuestos, como el tope. En un contrato abierto suele ser el máximo, no lo pagado.</li>\n'
            '          </ul>\n'
            '          <p class="cmx-nota">Archivos: %s Lo calcula <code>herramientas/fraccionamiento.py</code>, que coteja su tabla contra el Anexo 9 del DOF y se detiene si no coincide.</p>\n'
            '        </div>') % (
                cifras, LEY['url'], LEY['texto'], REGLAMENTO['url'], REGLAMENTO['texto'], topes_li,
                _n(k.get('revisadas', 0)), M['ventana'], M['ventana'],
                ' y '.join('%s en %s %s' % (_n(T[a]['ejercicio'][0]), a, de) for a in anios), pe,
                ' y '.join('%s en %s' % (_n(T[a]['solos']), a) for a in anios), de,
                ''.join(top), _n(k.get('persona física', 0)), _n(k.get('compra consolidada', 0)), _n(k.get('otra moneda', 0)),
                _n(k.get('obra pública u otra ley', 0)), _n(k.get('fecha de publicación en lugar de firma', 0)), arch)}


if __name__ == '__main__':
    main(sys.argv[1:])
