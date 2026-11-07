# -*- coding: utf-8 -*-
"""Lector de estado de resultados (pedido del autor, 05-11-2026: «que el
usuario pueda subir un estado de resultados… y nosotros evaluarlo, sin
retener información privada», con el molde de su plataforma Fortuvision:
varias dimensiones y horizontes de 3 y 5 años).

Es la versión de Python de la aplicación «Revisa tu estado de resultados» del
Modo Inspector (herramienta-inspector-resultados.html), que hace lo mismo en el
navegador con assets/auditor/js/insp-resultados.js. **Las dos aplican las mismas
reglas**: si cambias una, cambia la otra (la prueba de abajo corre en
revision.py con el ejemplo ficticio de docs/ejemplos/).

    python3 herramientas/lector_resultados.py mi-estado.csv
    python3 herramientas/lector_resultados.py --prueba

El archivo: un CSV (o lo que copias de Excel y pegas) con los conceptos en la
primera columna y un año por columna, por ejemplo «Concepto,2023,2024,2025».

Las seis dimensiones:
1. Cuadre: ¿las restas dan lo que el estado dice? (utilidad bruta = ventas −
   costo; de operación = bruta − gastos de operación; antes de impuestos = de
   operación − gastos financieros + productos financieros; neta = antes de
   impuestos − ISR).
2. Estructura (análisis vertical): cada renglón como parte de cada $100 vendidos.
3. Rentabilidad: margen bruto, de operación y neto.
4. Tendencia (análisis horizontal): cuánto cambió cada año y la tasa de
   crecimiento anual compuesta de las ventas en 3 y 5 años.
5. Impuestos: la tasa efectiva del ISR (ISR ÷ utilidad antes de impuestos)
   frente a la tasa de 30 % de las personas morales (LISR, art. 9).
6. Deuda: cuántas veces la utilidad de operación paga los gastos financieros.

Reglas (AGENTS.md §2): todo lo que sale de aquí es «derivado» (una cuenta con
las cifras que el lector trae) y lo que llama la atención se dice «señal para
revisar», nunca «irregularidad»: una tasa de ISR baja puede deberse a pérdidas
de años anteriores, y un margen que cae, a una mala racha. No es un dictamen ni
una auditoría. Nada se manda a ningún lado: el script solo lee tu archivo.
"""
import csv
import io
import os
import re
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EJEMPLO = os.path.join(RAIZ, 'docs', 'ejemplos', 'estado-de-resultados-ficticio.csv')
TASA_ISR = 30.0  # personas morales, LISR art. 9 (primer párrafo)

# Cómo se reconoce cada renglón (el texto ya en minúsculas y sin acentos). El
# orden importa: «utilidad antes de impuestos» empieza como «utilidad», así que
# se prueba antes que las demás utilidades.
CONCEPTOS = [
    ('uai', 'Utilidad antes de impuestos', r'antes de (impuestos|isr)'),
    ('ub', 'Utilidad bruta', r'^(utilidad|perdida) bruta|^resultado bruto|^margen bruto'),
    ('uo', 'Utilidad de operación', r'^(utilidad|perdida|resultado) (de operacion|operativa|operativo)'),
    ('un', 'Utilidad neta', r'^(utilidad|perdida|resultado) (neta|neto|del ejercicio)'),
    ('isr', 'ISR', r'^(isr|impuestos? a la utilidad|impuestos? sobre la renta)'),
    ('pfin', 'Productos financieros', r'^(productos|ingresos) financieros|^intereses (ganados|a favor)'),
    ('fin', 'Gastos financieros', r'^gastos? financieros?|^intereses (pagados|a cargo)|^costo financiero'),
    ('cos', 'Costo de ventas', r'^costos? de (lo vendido|ventas?|(los )?servicios)'),
    ('gop', 'Gastos de operación', r'^gastos (de operacion|de ventas?|de administracion|de venta y administracion|generales)'),
    ('ing', 'Ventas o ingresos', r'^(ventas|ingresos)( (netas|netos|totales|de operacion|por ventas|por servicios))?$|^total de ingresos$'),
]
NOMBRE = {c: n for c, n, _ in CONCEPTOS}
SUMAN = {'gop'}  # gastos de venta + de administración: se suman


def normal(t):
    t = unicodedata.normalize('NFD', t.lower())
    t = ''.join(ch for ch in t if unicodedata.category(ch) != 'Mn')
    t = re.sub(r'^[\s\d.)\-]+', '', t)          # «1. Ventas» o «- Ventas»
    t = re.sub(r'[:*]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def concepto(etiqueta):
    e = normal(etiqueta)
    for c, _n, rx in CONCEPTOS:
        if re.search(rx, e):
            return c
    return None


def numero(t):
    """«$1,234,567», «(1,000)» o «-1000» a número; vacío o «-» es None."""
    t = (t or '').strip().replace('$', '').replace(' ', '').replace(',', '')
    if t in ('', '-', '—'):
        return None
    neg = t.startswith('(') and t.endswith(')')
    t = t.strip('()')
    try:
        v = float(t)
    except ValueError:
        return None
    return -v if neg else v


def filas(texto):
    linea = texto.lstrip('﻿').split('\n', 1)[0]
    sep = '\t' if '\t' in linea else (';' if linea.count(';') > linea.count(',') else ',')
    return [f for f in csv.reader(io.StringIO(texto.lstrip('﻿')), delimiter=sep) if any(x.strip() for x in f)]


def leer(texto):
    """De texto a {años, v: {concepto: {año: valor}}, sin: [renglones no reconocidos]}."""
    fs = filas(texto)
    if not fs:
        raise ValueError('El archivo está vacío.')
    cols = []
    for i, x in enumerate(fs[0]):
        m = re.search(r'(19|20)\d{2}', x)
        if i > 0 and m:
            cols.append((int(m.group(0)), i))
    if not cols:
        raise ValueError('No encontramos los años: la primera fila debe decir, por ejemplo, «Concepto, 2023, 2024, 2025».')
    cols = sorted(cols)[-6:]
    v, sin = {}, []
    for f in fs[1:]:
        if not f or not f[0].strip():
            continue
        c = concepto(f[0])
        if not c:
            sin.append(f[0].strip())
            continue
        for a, i in cols:
            x = numero(f[i]) if i < len(f) else None
            if x is None:
                continue
            d = v.setdefault(c, {})
            if c in SUMAN:
                d[a] = d.get(a, 0) + x
            elif a not in d:
                d[a] = x
    return {'anios': [a for a, _ in cols], 'v': v, 'sin': sin}


def _r1(x):
    return round(x + 0.0, 1)


def _pct(a, b):
    return None if a is None or not b else _r1(100.0 * a / b)


def _var(a, b):
    """Cambio de b (antes) a a (después), en %. Solo si b es positivo."""
    return None if a is None or b is None or b <= 0 else _r1(100.0 * (a - b) / b)


def analizar(texto):
    e = leer(texto)
    anios, v = e['anios'], e['v']
    g = lambda c, a: v.get(c, {}).get(a)
    senales, cuadre, deriv = [], [], {}
    otros = (' Puede deberse a renglones que no reconocimos (%s).' % ', '.join(e['sin'][:4])) if e['sin'] else ''

    def tol(base):
        return max(1.0, 0.005 * abs(base or 0))

    # 1. Cuadre: rehacer las restas; si un subtotal falta, se calcula (derivado).
    for a in anios:
        ing, cos, gop, fin, pfin, isr = g('ing', a), g('cos', a), g('gop', a), g('fin', a), g('pfin', a) or 0, g('isr', a)
        pasos = [('ub', 'la utilidad bruta', ing - cos if ing is not None and cos is not None else None)]
        ub = g('ub', a) if g('ub', a) is not None else pasos[0][2]
        pasos.append(('uo', 'la utilidad de operación', ub - gop if ub is not None and gop is not None else None))
        uo = g('uo', a) if g('uo', a) is not None else pasos[1][2]
        pasos.append(('uai', 'la utilidad antes de impuestos', uo - fin + pfin if uo is not None and fin is not None else None))
        uai = g('uai', a) if g('uai', a) is not None else pasos[2][2]
        pasos.append(('un', 'la utilidad neta', uai - isr if uai is not None and isr is not None else None))
        for c, nom, calc in pasos:
            if calc is None:
                continue
            dice = g(c, a)
            if dice is None:
                deriv.setdefault(c, {})[a] = calc
                continue
            dif = dice - calc
            ok = abs(dif) <= tol(ing)
            cuadre.append({'anio': a, 'c': c, 'dice': dice, 'calc': calc, 'ok': ok})
            if not ok:
                senales.append({'dim': 'Cuadre', 'anio': a,
                                'txt': 'En %d %s dice %s, pero la resta da %s (diferencia de %s).%s'
                                       % (a, nom, fmt(dice), fmt(calc), fmt(dif), otros)})
    val = lambda c, a: g(c, a) if g(c, a) is not None else deriv.get(c, {}).get(a)

    # 2 y 3. Estructura y rentabilidad, año por año.
    estructura, rent, imp, deuda = {}, {}, {}, {}
    for a in anios:
        ing = g('ing', a)
        estructura[a] = {c: _pct(val(c, a), ing) for c in ('cos', 'gop', 'fin', 'isr')}
        rent[a] = {'bruto': _pct(val('ub', a), ing), 'operacion': _pct(val('uo', a), ing), 'neto': _pct(val('un', a), ing)}
        if rent[a]['operacion'] is not None and rent[a]['operacion'] < 0:
            senales.append({'dim': 'Rentabilidad', 'anio': a,
                            'txt': 'En %d hubo pérdida de operación: por cada $100 vendidos, se perdieron $%s antes de intereses e impuestos.'
                                   % (a, fmt_p(-rent[a]['operacion']))})
        uai, isr = val('uai', a), g('isr', a)
        if uai is not None and uai > 0 and isr is not None:
            t = _pct(isr, uai)
            imp[a] = t
            if t < TASA_ISR - 10 or t > TASA_ISR + 10:
                senales.append({'dim': 'Impuestos', 'anio': a,
                                'txt': 'En %d el ISR fue el %s %% de la utilidad antes de impuestos; la tasa de las personas morales es %d %% '
                                       '(LISR, art. 9). Puede tener explicación (pérdidas de años anteriores, partidas no deducibles, '
                                       'diferencias entre lo contable y lo fiscal), pero conviene preguntar.' % (a, fmt_p(t), TASA_ISR)})
        uo, fin = val('uo', a), g('fin', a)
        if fin is not None and fin > 0 and uo is not None:
            cob = round(uo / fin, 2)
            deuda[a] = cob
            if cob < 1:
                senales.append({'dim': 'Deuda', 'anio': a,
                                'txt': 'En %d la utilidad de operación (%s) no alcanzó para pagar los gastos financieros (%s): '
                                       'los cubrió %s veces.' % (a, fmt(uo), fmt(fin), fmt_x(cob))})

    # 4. Tendencia: cambio anual y crecimiento compuesto de las ventas.
    tendencia = {}
    for i in range(1, len(anios)):
        a, b = anios[i], anios[i - 1]
        t = {c: _var(val(c, a), val(c, b)) for c in ('ing', 'cos', 'gop', 'un')}
        tendencia[a] = t
        if t['ing'] is not None:
            for c, nom, pl in (('cos', 'el costo de ventas', False), ('gop', 'los gastos de operación', True)):
                if t[c] is not None and t[c] > t['ing'] + 2:
                    senales.append({'dim': 'Tendencia', 'anio': a,
                                    'txt': 'En %d %s %s y las ventas %s: cada peso vendido deja menos.'
                                           % (a, nom, mov(t[c], pl), mov(t['ing'], True))})
            if t['ing'] < -10:
                senales.append({'dim': 'Tendencia', 'anio': a, 'txt': 'En %d las ventas cayeron %s %%.' % (a, fmt_p(-t['ing']))})
            if t['un'] is not None and t['un'] > 0 and t['ing'] < 0:
                senales.append({'dim': 'Tendencia', 'anio': a,
                                'txt': 'En %d la utilidad neta subió %s %% mientras las ventas bajaron %s %%: conviene ver de dónde salió.'
                                       % (a, fmt_p(t['un']), fmt_p(-t['ing']))})
    compuesto = []
    ult = anios[-1]
    for h in sorted({3, 5, ult - anios[0]}):
        ini = ult - h
        x0, x1 = val('ing', ini), val('ing', ult)
        if h >= 2 and x0 and x1 and x0 > 0 and x1 > 0:
            compuesto.append({'anios': h, 'de': ini, 'a': ult, 'tasa': _r1(((x1 / x0) ** (1.0 / h) - 1) * 100)})
    return {'anios': anios, 'v': v, 'deriv': deriv, 'sin': e['sin'], 'cuadre': cuadre, 'estructura': estructura,
            'rentabilidad': rent, 'tendencia': tendencia, 'compuesto': compuesto, 'impuestos': imp, 'deuda': deuda, 'senales': senales}


def mov(x, plural=False):
    """«subió 8.0 %», «bajaron 5.6 %», «no cambió»."""
    if x == 0:
        return 'no cambiaron' if plural else 'no cambió'
    v = ('subieron' if plural else 'subió') if x > 0 else ('bajaron' if plural else 'bajó')
    return '%s %s %%' % (v, fmt_p(abs(x)))


def fmt(x):
    return ('-$' if x < 0 else '$') + format(abs(round(x)), ',.0f')


def fmt_p(x):
    return format(x, '.1f')


def fmt_x(x):
    return format(x, '.2f')


def prueba():
    """La corre revision.py: el estado ficticio cuadra, da las señales que se
    esperan, y un subtotal alterado deja de cuadrar."""
    texto = open(EJEMPLO, encoding='utf-8').read()
    r = analizar(texto)
    fallas = []
    if r['anios'] != [2021, 2022, 2023, 2024, 2025] or r['sin']:
        fallas.append('lectura: %r %r' % (r['anios'], r['sin']))
    if r['v']['gop'][2025] != 3500000:
        fallas.append('los gastos de venta y de administración deberían sumarse: %r' % r['v']['gop'])
    if not r['cuadre'] or not all(x['ok'] for x in r['cuadre']):
        fallas.append('el ejemplo debería cuadrar: %r' % [x for x in r['cuadre'] if not x['ok']])
    dims = sorted({(s['dim'], s['anio']) for s in r['senales']})
    espera = [('Deuda', 2025), ('Impuestos', 2024), ('Tendencia', 2024), ('Tendencia', 2025)]
    for x in espera:
        if x not in dims:
            fallas.append('falta la señal %r; salieron %r' % (x, dims))
    if ('Impuestos', 2021) in dims:
        fallas.append('una tasa de 30 %% no es señal: %r' % dims)
    comp = {c['anios']: c['tasa'] for c in r['compuesto']}
    if comp.get(3) != 2.4 or comp.get(4) != 4.2 or 5 in comp:
        fallas.append('crecimiento compuesto: %r' % comp)
    if r['rentabilidad'][2021] != {'bruto': 40.0, 'operacion': 15.0, 'neto': 9.1}:
        fallas.append('márgenes 2021: %r' % r['rentabilidad'][2021])
    malo = texto.replace('Utilidad bruta,4000000', 'Utilidad bruta,4100000')
    if not any(s['dim'] == 'Cuadre' and s['anio'] == 2021 for s in analizar(malo)['senales']):
        fallas.append('una utilidad bruta alterada debería no cuadrar')
    # Lo que se copia de Excel llega separado por tabuladores, con $ y comas.
    tab = 'Concepto\t2024\t2025\nVentas\t$1,000\t$1,200\nCosto de ventas\t(600)\t700\n'
    t = leer(tab)
    if t['v'].get('ing') != {2024: 1000.0, 2025: 1200.0} or t['v'].get('cos') != {2024: -600.0, 2025: 700.0}:
        fallas.append('pegado de Excel: %r' % t['v'])
    if fallas:
        print('lector de estado de resultados: FALLA\n  ' + '\n  '.join(fallas))
        return 1
    print('lector de estado de resultados: prueba bien (%d señales en el ejemplo)' % len(r['senales']))
    return 0


def main():
    args = sys.argv[1:]
    if '--prueba' in args:
        return prueba()
    if not args:
        print(__doc__)
        return 1
    r = analizar(open(args[0], encoding='utf-8-sig').read())
    print('Años: %s' % ', '.join(map(str, r['anios'])))
    for a in r['anios']:
        m = r['rentabilidad'][a]
        print('%d · márgenes bruto %s, de operación %s, neto %s (derivado)' % (a, m['bruto'], m['operacion'], m['neto']))
    for c in r['compuesto']:
        print('Ventas %d→%d: %s %% al año en %d años (derivado)' % (c['de'], c['a'], c['tasa'], c['anios']))
    print('\nSeñales para revisar (no son irregularidades):' if r['senales'] else '\nSin señales.')
    for s in r['senales']:
        print('- [%s] %s' % (s['dim'], s['txt']))
    if r['sin']:
        print('\nNo reconocimos: %s' % ', '.join(r['sin']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
