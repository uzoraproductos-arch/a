#!/usr/bin/env python3
"""El Auditor calcula al vuelo (Ola 4, entrega A, Ronda 41).

El chat lee los montos de una pregunta («¿cuánto pago de ISR si cobro
$80,000 al mes en RESICO?») y hace la cuenta en el navegador con las
fórmulas del simulador (assets/auditor/js/fiscal-simulador.js, FiscalSim).
La lectura de la pregunta y el armado de la respuesta viven en
assets/auditor/js/fiscal-calculo.js (FiscalCalc); este módulo le entrega,
desde docs/fiscal-2027/, lo único que recibe: los datos del simulador
(`K`), el fundamento y las fuentes de cada cuenta.

  * Ninguna fórmula se duplica: FiscalCalc llama a FiscalSim.
  * Ninguna cifra fiscal se escribe aquí ni en el JavaScript.
  * Los montos de la pregunta no salen del navegador: la respuesta
    calculada va sin ficha, así que no ofrece dictamen (su enlace llevaría
    la pregunta en la dirección).
  * El mismo archivo trae el anonimizador del buzón de aprendizaje.

    python3 herramientas/fiscal_calculo.py --prueba

La prueba (corre en revision.py) lee los números escritos en el JavaScript,
revisa el anonimizador y compara cada cuenta del chat con la de Python.
"""
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fiscal_simulador as fs  # noqa: E402
import fiscal_temas as ft  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'fiscal-calculo.js')
HASTA = 'Hasta el 31 de diciembre de 2026 valen las cifras de 2026.'
NO = ('Es una cuenta auditada con las tasas y los topes oficiales. No es tu declaración ni una asesoría fiscal: '
      'tu caso puede tener particularidades que aquí no se ven.')


def _dato(i, tx, n=0):
    return '%s (%s) %s' % (tx, ft.liga(i, n), ft.chip(i))


def _pend(i, tx):
    return '%s %s' % (tx, ft.chip(i))


def _m(tit, mod, ids, sug, partes):
    fuentes = []
    for i in ids:
        fuentes += ft.fu(i)
    return {'tit': tit, 'ir': [ft.SIMULADOR + '#' + mod, ft.SIM_TITULO], 'fu': fuentes, 'sug': sug,
            'fund': '<p class="pa-chico fc-fund"><b>De dónde sale cada tasa:</b> %s.</p>' % '; '.join(partes)}


def chat():
    """D.fis.calc del chat: los datos del simulador y el fundamento de cada cuenta."""
    T, P, N = ft.T, ft.P, ft.N
    m = {
        'iva': _m('Tu IVA y tu ISR del RESICO, con tus números', 'resico',
                  ['sin-cambio-iva-general', 'iva-opcional-resico-7', 'iva-opcional-resico-sin-acreditamiento', 'iva-opcional-resico-equilibrio',
                   'resico-pf-mensual-2026', 'resico-pf-mensual-2027', 'resico-pf-tope-2026', 'rmf-2027'],
                  ['¿Me pueden regresar IVA si estoy en RESICO?', '¿Qué es el IVA opcional del 7 % para RESICO?', '¿Qué régimen fiscal me conviene?'],
                  [_dato('sin-cambio-iva-general', 'IVA general de %s' % T('sin-cambio-iva-general')),
                   _dato('iva-opcional-resico-7', 'opción de %s, definitiva y sin acreditamiento' % T('iva-opcional-resico-7')),
                   _dato('iva-opcional-resico-equilibrio', 'punto de equilibrio de %s' % T('iva-opcional-resico-equilibrio')),
                   _dato('resico-pf-mensual-2026', 'tabla mensual del RESICO'),
                   _pend('rmf-2027', 'las reglas de la opción dependen de la RMF 2027, que sigue')]),
        'resico': _m('Tu ISR en el RESICO, con tus números', 'resico',
                     ['resico-pf-mensual-2026', 'resico-pf-anual-2026', 'resico-pf-mensual-2027', 'resico-pf-anual-2027', 'resico-pf-tope-2026', 'resico-pf-tope-2027',
                      'resico-pf-sin-deducciones'],
                     ['¿Me conviene el IVA de 7 % o el de 16 %?', '¿Cuál es el tope del RESICO en 2027?', '¿Qué régimen fiscal me conviene?'],
                     [_dato('resico-pf-mensual-2026', 'tabla mensual del RESICO de 2026'), _dato('resico-pf-anual-2026', 'tabla anual de 2026'),
                      _dato('resico-pf-mensual-2027', 'tablas desde 2027'),
                      _dato('resico-pf-tope-2026', 'tope de %s en 2026' % P('resico-pf-tope-2026')), _dato('resico-pf-tope-2027', 'y de %s desde 2027' % P('resico-pf-tope-2027')),
                      _dato('resico-pf-sin-deducciones', 'la tasa va sobre lo cobrado, sin deducciones')]),
        'anual': _m('Tu declaración anual de 2026, con tus números', 'anual',
                    ['isr-tarifa-anual-2026', 'tope-deducciones-personales', 'tope-aportaciones-retiro', 'tope-gastos-funerales', 'colegiaturas-fuera-del-tope',
                     'anual-asalariados-obligados', 'isr-tarifas-2027'],
                    ['¿Qué puedo deducir en mi declaración anual?', '¿Quién presenta declaración anual?', '¿Cuándo vence la declaración anual?'],
                    [_dato('isr-tarifa-anual-2026', 'tarifa anual de 2026'),
                     _dato('tope-deducciones-personales', 'tope global de deducciones: lo menor entre %s veces la UMA anual y el %s de tus ingresos'
                           % (N('tope-deducciones-personales', 'veces_uma_anual'), T('tope-deducciones-personales', 'porcentaje_ingresos'))),
                     _dato('tope-aportaciones-retiro', 'aportaciones de retiro, aparte'), _dato('tope-gastos-funerales', 'gastos funerarios'),
                     _dato('anual-asalariados-obligados', 'quién está obligado por el monto de sus sueldos'),
                     _pend('isr-tarifas-2027', 'las tarifas de 2027 siguen')]),
        'reg': _m('Tu régimen, comparado con tus números', 'regimenes',
                  ['isr-utilidad-actividades', 'isr-tarifa-anual-2026', 'resico-pf-sin-deducciones', 'resico-pf-anual-2026', 'resico-pf-anual-2027', 'resico-pf-tope-2026',
                   'deduccion-ciega-arrendamiento', 'retencion-plataformas-ley', 'retencion-plataformas-lif', 'plataformas-pago-definitivo', 'resico-plataformas'],
                  ['¿Me conviene el IVA de 7 % o el de 16 %?', '¿Cuál es el tope del RESICO en 2027?', '¿Qué cambia en 2027?'],
                  [_dato('isr-utilidad-actividades', 'actividad empresarial y servicios profesionales: tarifa anual sobre la utilidad'),
                   _dato('isr-tarifa-anual-2026', 'tarifa anual de 2026'), _dato('resico-pf-anual-2026', 'tabla anual del RESICO'),
                   _dato('deduccion-ciega-arrendamiento', 'arrendamiento: deducción de %s sin comprobantes' % T('deduccion-ciega-arrendamiento')),
                   _dato('retencion-plataformas-ley', 'retenciones de plataformas'), _dato('plataformas-pago-definitivo', 'su pago definitivo'),
                   _pend('resico-plataformas', 'el RESICO para quien cobra por plataformas sigue')]),
    }
    return {'K': fs.datos(), 'm': m, 'no': NO, 'hasta': HASTA}


# ---------------------------------------------------------------- la prueba
PERMITIDOS = {'0', '1', '2', '12'}   # aritmética y gramática: «mil» y «millones» se escriben 1e3 y 1e6; doce meses

# Lo que entra y lo que debe salir del navegador hacia el buzón de aprendizaje.
ANONIMOS = [
    ('Mi RFC es XAXX010101000 y cobro $80,000 al mes', 'Mi RFC es [RFC] y cobro [MONTO] al mes'),
    ('la empresa EKU9003173C9 me retuvo 5500 pesos', 'la empresa [RFC] me retuvo [MONTO]'),
    ('mi curp es BADD110313HCMLNS09, ¿puedo estar en RESICO?', 'mi curp es [CURP], ¿puedo estar en RESICO?'),
    ('escríbanme a nombre.apellido+sat@correo.com.mx por favor', 'escríbanme a [CORREO] por favor'),
    ('mi cel es 55 1234 5678 y gano 30 mil', 'mi cel es [TELEFONO] y gano [MONTO]'),
    ('llámame al +52 (33) 1234-5678', 'llámame al [TELEFONO]'),
    ('tel 5512345678, facturo 1.5 millones al año', 'tel [TELEFONO], facturo [MONTO] al año'),
    ('gané $360,000.50, me retuvieron 55000 y gasté 35 mil pesos', 'gané [MONTO], me retuvieron [MONTO] y gasté [MONTO]'),
    ('¿me conviene el 7 % o el 16 % de IVA en 2027 según el art. 25?', '¿me conviene el 7 % o el 16 % de IVA en 2027 según el art. 25?'),
    ('¿qué dice el artículo 69-B del CFF y el 113-E de la LISR?', '¿qué dice el artículo 69-B del CFF y el 113-E de la LISR?'),
    ('cobro 80k   mensuales', 'cobro [MONTO] mensuales'),
    ('gano 100000 por mes y mi RFC es XAXX-010101-000', 'gano [MONTO] por mes y mi RFC es [RFC]'),
]

# Preguntas con montos: la cuenta que piden y lo que el chat debe leer de ellas.
CASOS = [
    ('¿Cuánto pago de ISR si cobro $80,000 al mes en RESICO?', 'resico', {'c': 80000, 'mensual': True}),
    ('en resico facturo 1.2 millones al año, cuánto es de ISR', 'resico', {'c': 100000, 'mensual': False}),
    ('Estoy en RESICO y gano 25 mil por quincena, ¿cuánto pago?', 'resico', {'c': 50000, 'mensual': True}),
    ('¿Me conviene el 7 % si facturo $100,000 y gasto $30,000 con IVA?', 'iva', {'c': 100000, 'g': 30000}),
    ('IVA de 7 o de 16 si cobro 60 mil al mes', 'iva', {'c': 60000, 'g': None}),
    ('cobro 50,000 mensuales y compro 45,000 con iva, ¿me conviene el iva opcional?', 'iva', {'c': 50000, 'g': 45000}),
    ('¿Cuánto me devuelve el SAT si gané $360,000, me retuvieron $55,000 y tuve $35,000 de gastos médicos?', 'anual', {'i': 360000, 'ret': 55000, 'g': 35000, 'f': 0, 'ap': 0}),
    ('saldo a favor: sueldo de 30 mil al mes, me retuvieron 48,000 en el año, 20 mil de retiro y 9,000 de funeral', 'anual', {'i': 360000, 'ret': 48000, 'g': 0, 'f': 9000, 'ap': 20000}),
    ('en mi declaración anual gané 500 mil pesos y tuve 120,000 de gastos médicos', 'anual', {'i': 500000, 'ret': None, 'g': 120000, 'f': 0, 'ap': 0}),
    ('¿Qué régimen me conviene si gano 50 mil al mes y gasto 20 mil?', 'reg', {'m': 50000, 'g': 20000, 'perfil': 'servicios', 'sub': ''}),
    ('qué régimen fiscal me conviene si rento un local en $18,000 al mes', 'reg', {'m': 18000, 'g': None, 'perfil': 'arrendamiento', 'sub': ''}),
    ('manejo Uber y gano 22 mil al mes, ¿qué régimen me conviene?', 'reg', {'m': 22000, 'g': None, 'perfil': 'plataformas', 'sub': 'transporte_y_entrega'}),
    ('¿me conviene el RESICO si facturo 4 millones al año y gasto 100 mil al mes?', 'reg', {'m': round(4000000 / 12, 2), 'g': 100000, 'perfil': 'servicios', 'sub': ''}),
]
# Lo que no es una cuenta del chat: sin montos contesta el tema; el sueldo es de la Calculadora Cívica; el predial, de su simulador.
NULOS = ['¿Cuál es el tope del RESICO en 2027?', 'Gano 15 mil al mes, ¿cuánto me retienen?', '¿Cuánto pago de predial por una casa de 2 millones en resico?',
         '¿Qué es el IVA opcional del 7 % para RESICO?', '¿Cuánto costó el Tren Maya?', '¿Cuánto gana un diputado? dicen que 150 mil al mes en resico']
# Piden una cuenta, pero falta lo indispensable: el chat contesta la regla y dice qué falta.
FALTAN = [('¿Cuánto me devuelve el SAT si tuve $35,000 de gastos médicos?', 'sim_anual'), ('¿me conviene el iva de 7 si gasto 30 mil al mes?', 'sim_iva')]


def _literales_js():
    return fs._literales_js(JS)


def _py(mod, a, K):
    """La misma cuenta, hecha por las fórmulas de Python."""
    if mod == 'iva':
        return {'iva': fs.iva(K, a['c'], a['g'] or 0, 0), 'a': fs.resico(K, '2026', a['c'], 0), 'b': fs.resico(K, '2027', a['c'], 0)}
    if mod == 'resico':
        return {'a': fs.resico(K, '2026', a['c'], 0), 'b': fs.resico(K, '2027', a['c'], 0)}
    if mod == 'anual':
        return fs.anual(K, a['i'], a['ret'] or 0, a['g'], a['f'], a['ap'], [])
    return fs.compara(K, a['perfil'], a['sub'], a['m'], a['g'] or 0)


def _igual(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(_igual(a[k], b[k]) for k in a)
    if isinstance(a, bool) or isinstance(b, bool) or a is None or b is None or isinstance(a, str):
        return a == b
    return abs(a - b) < 0.006


def _pesos(n):
    return '$' + format(n, ',.2f')


def prueba():
    errores = []
    C = chat()
    K = C['K']
    # 1. Lo que escribe este módulo sale de la base.
    for k, m in C['m'].items():
        for x in ft._sueltos(m['tit'] + ' ' + m['fund']):
            errores.append('cuenta %s: un número que no sale de la base: «…%s…»' % (k, x))
        if not m['fu']:
            errores.append('cuenta %s: sin fuentes' % k)
        if not os.path.exists(os.path.join(RAIZ, ft.SIMULADOR)) or 'id="%s"' % m['ir'][0].split('#')[1] not in open(os.path.join(RAIZ, ft.SIMULADOR), encoding='utf-8').read():
            errores.append('cuenta %s: su módulo del simulador (%s) no existe' % (k, m['ir'][0]))
    for t in [f[1] for f in FALTAN] + ['resico_pf']:
        if t not in ft.ORDEN:
            errores.append('el tema %s, al que se remite cuando falta un dato, no existe' % t)
    # 2. El JavaScript no escribe un número ni repite una fórmula.
    for n in sorted(set(_literales_js()) - PERMITIDOS):
        errores.append('fiscal-calculo.js: el número %s está escrito a mano; todo dato fiscal llega en D.fis.calc' % n)
    src = open(JS, encoding='utf-8').read()
    for f in ('tarifa', 'tasaResico'):
        if re.search(r'function %s\b' % f, src):
            errores.append('fiscal-calculo.js repite la fórmula %s: las fórmulas viven solo en fiscal-simulador.js' % f)
    if 'fetch(' in src or 'XMLHttpRequest' in src or 'localStorage' in src or 'sessionStorage' in src:
        errores.append('fiscal-calculo.js no envía ni guarda nada: los montos de la pregunta se quedan en la página')
    # 3. El navegador: el anonimizador, la lectura de cada pregunta y la cuenta.
    if not shutil.which('node'):
        errores.append('falta node para probar fiscal-calculo.js')
    else:
        guion = ('const F=require(%s);const C=%s;const E=%s;'
                 'const r=q=>{const x=F.responde(C,q);return x&&{mod:x.mod,args:x.args,x:x.x,html:x.html,calc:x.calc,falta:x.falta,tema:x.tema,fu:(x.fu||[]).length,ir:x.ir};};'
                 'process.stdout.write(JSON.stringify({a:E.a.map(F.anonimiza),c:E.c.map(r),n:E.n.map(r),f:E.f.map(r)}));'
                 ) % (json.dumps(JS), json.dumps(C), json.dumps({'a': [a for a, _ in ANONIMOS], 'c': [c[0] for c in CASOS], 'n': NULOS, 'f': [f[0] for f in FALTAN]}))
        r = subprocess.run(['node', '-e', guion], capture_output=True, text=True)
        if r.returncode:
            errores.append('fiscal-calculo.js no corre en node: %s' % r.stderr.strip()[:400])
        else:
            R = json.loads(r.stdout)
            for (entra, sale), js in zip(ANONIMOS, R['a']):
                if js != sale:
                    errores.append('anonimizador: «%s» debía salir «%s» y salió «%s»' % (entra, sale, js))
                if re.search(r'@|\d{5,}|\$', js):
                    errores.append('anonimizador: «%s» todavía trae un dato' % js)
            for (q, mod, args), js in zip(CASOS, R['c']):
                if not js or js.get('falta'):
                    errores.append('«%s»: el chat no hizo la cuenta' % q)
                    continue
                if js['mod'] != mod or not _igual(args, js['args']):
                    errores.append('«%s»: debía leerse %s %s y se leyó %s %s' % (q, mod, args, js['mod'], js['args']))
                    continue
                py = _py(mod, args, K)
                if not _igual(py, js['x']):
                    errores.append('«%s»: Python y el navegador no dan lo mismo: %s contra %s' % (q, py, js['x']))
                clave = {'iva': lambda: py['iva']['opcion'], 'resico': lambda: py['a']['isr'] if args['mensual'] else py['a']['isrA'],
                         'anual': lambda: py['isr'], 'reg': lambda: py['general']}[mod]()
                if _pesos(clave) not in js['html']:
                    errores.append('«%s»: la respuesta no enseña %s' % (q, _pesos(clave)))
                if not js['calc'] or not js['fu'] or 'fc-fund' not in js['html'] or 'est-derivado' not in js['html'] or 'est-oficial' not in js['html']:
                    errores.append('«%s»: la respuesta calculada va sin ficha, con sus fuentes, su fundamento y sus chips' % q)
                if 'no se envían' not in js['html'] or NO[:30] not in js['html']:
                    errores.append('«%s»: la respuesta dice que los montos no se envían y que no es una asesoría' % q)
                if mod != 'anual' and '2027' in js['html'] and 'valen las cifras de 2026' not in js['html']:
                    errores.append('«%s»: lo de 2027 se dice sin mover las cifras de 2026' % q)
            for q, js in zip(NULOS, R['n']):
                if js:
                    errores.append('«%s» no es una cuenta del chat y se contestó como %s' % (q, js.get('mod')))
            for (q, tema), js in zip(FALTAN, R['f']):
                if not js or not js.get('falta') or js.get('tema') != tema:
                    errores.append('«%s»: debía decir qué dato falta y remitir al tema %s' % (q, tema))
    if errores:
        for x in errores:
            print('fiscal_calculo: ERROR:', x)
        return 1
    print('fiscal_calculo: %d cuentas del chat iguales en Python y en el navegador, %d preguntas que no son cuenta, %d con un dato faltante y %d casos del anonimizador; ningún número escrito a mano'
          % (len(CASOS), len(NULOS), len(FALTAN), len(ANONIMOS)))
    return 0


if __name__ == '__main__':
    if '--prueba' in sys.argv:
        sys.exit(prueba())
    print(__doc__)
