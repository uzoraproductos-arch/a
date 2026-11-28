#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El Simulador y Blindaje Fiscal 2027 · Cero CIEC (Ola 3, Ronda 40).

La página `fiscal-simulador-2027.html` (Planisferio › Financiera) hace cuatro
cuentas en el navegador, sin subir nada: el decisor del RESICO (IVA opcional
contra el régimen general, ISR y tope), la declaración anual de quien tiene
sueldo, el comparador de regímenes y la lista de blindaje con el calendario.

Aquí no se escribe ninguna cifra fiscal. `datos()` arma, desde
docs/fiscal-2027/ (con los lectores de fiscal_temas.py), lo único que el
navegador recibe; las fórmulas de este módulo y las de
assets/auditor/js/fiscal-simulador.js son gemelas, y la prueba las compara.

    python3 herramientas/fiscal_simulador.py --prueba

La prueba (corre en revision.py) revisa que ningún número de la página salga
de fuera de la base, que ni este módulo ni el JavaScript traigan un número
escrito a mano, los casos conocidos (punto de equilibrio del IVA opcional,
tope global de deducciones, saltos de tramo de las tarifas) y que Python y el
navegador den lo mismo.
"""
import html
import io
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tokenize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fiscal_temas as ft   # noqa: E402

ARCHIVO = 'fiscal-simulador-2027.html'
TITULO = 'Simulador y Blindaje Fiscal 2027'
JS = os.path.join(ft.RAIZ, 'assets', 'auditor', 'js', 'fiscal-simulador.js')
LLAVE = 'av-fiscal-blindaje'   # la lista de blindaje, solo en el navegador (aviso de privacidad: _AV_NAVEGADOR)
NIVELES = [('preescolar', 'Preescolar'), ('primaria', 'Primaria'), ('secundaria', 'Secundaria'), ('profesional_tecnico', 'Profesional técnico'),
           ('bachillerato', 'Bachillerato o equivalente')]
PLATAFORMAS = [('transporte_y_entrega', 'Transporte de pasajeros o entrega de bienes'), ('hospedaje', 'Hospedaje'),
               ('enajenacion_y_servicios', 'Venta de bienes o prestación de servicios')]
NO_ASESORIA = ('Es una cuenta aproximada con el texto oficial: no es tu declaración ni una asesoría fiscal, y no sustituye a tu contador. '
               'Nada de lo que escribes sale de tu navegador.')
D, P, T, N, F = ft.D, ft.P, ft.T, ft.N, ft.F
e = html.escape


# ---------------------------------------------------------------- los datos que recibe el navegador
def datos():
    """Todo lo que el simulador calcula sale de aquí, y esto sale de la base."""
    v = ft._v
    tabla = lambda i: [[f['hasta'], f['tasa']] for f in D(i)['tabla']]
    num, den = (int(x) for x in v('retencion-iva-dos-terceras').split('/'))
    ded, ret = D('tope-deducciones-personales')['valor'], D('tope-aportaciones-retiro')['valor']
    return {
        'iva': {'gen': v('sin-cambio-iva-general'), 'op': v('iva-opcional-resico-7'), 'eq': v('iva-opcional-resico-equilibrio'), 'ret': [num, den]},
        'resico': {a: {'tope': v('resico-pf-tope-' + a), 'men': tabla('resico-pf-mensual-' + a), 'anu': tabla('resico-pf-anual-' + a)} for a in ('2026', '2027')},
        'retPm': v('retencion-resico-pm'),
        'isr': [{'inf': f['inferior'], 'sup': f['superior'], 'cuota': f['cuota'], 'tasa': f['tasa']} for f in D('isr-tarifa-anual-2026')['tabla']],
        'uma': v('uma-2026', 'anual'),
        'ded': {'veces': ded['veces_uma_anual'], 'pct': ded['porcentaje_ingresos'], 'retPct': ret['porcentaje_ingresos'], 'retVeces': ret['veces_uma_anual'],
                'funVeces': v('tope-gastos-funerales', 'veces_uma_anual')},
        'col': dict(D('colegiaturas')['valor']),
        'anualDesde': v('anual-asalariados-obligados'),
        'ciega': v('deduccion-ciega-arrendamiento'),
        'plat': {'transporte_y_entrega': v('retencion-plataformas-ley', 'transporte_y_entrega'), 'hospedaje': v('retencion-plataformas-ley', 'hospedaje'),
                 'enajenacion_y_servicios': v('retencion-plataformas-lif'), 'definitivo': v('plataformas-pago-definitivo')},
        'cal': [[f['periodo_de_pago'], f['vence']] for f in D('calendario-dia-17')['fechas']],
        'rige': ft.RIGE, 'llave': LLAVE,
    }


# ---------------------------------------------------------------- las fórmulas (gemelas de fiscal-simulador.js)
def r2(x):
    return math.floor(x * 100 + 0.5) / 100


def tarifa(K, base):
    """El ISR de la tarifa anual del art. 152: cuota fija más la tasa sobre el excedente del límite inferior."""
    if base <= 0:
        return 0
    for f in K['isr']:
        if f['sup'] is None or base <= f['sup']:
            return r2(f['cuota'] + (base - f['inf']) * f['tasa'] / 100)


def tasa_resico(tabla, monto):
    """La tasa del RESICO: la del primer renglón cuyo «hasta» alcanza al monto; fuera de la tabla, ninguna."""
    for hasta, tasa in tabla:
        if monto <= hasta:
            return tasa
    return None


def resico(K, anio, cobros, pm):
    R = K['resico'][anio]
    ing = r2(cobros * 12)
    tm, ta = tasa_resico(R['men'], cobros), tasa_resico(R['anu'], ing)
    ret = r2(cobros * pm / 100 * K['retPm'] / 100)
    isr = None if tm is None else r2(cobros * tm / 100)
    return {'tasa': tm, 'isr': isr, 'ret': ret, 'pagar': None if isr is None else r2(max(0, isr - ret)), 'ing': ing, 'tasaA': ta,
            'isrA': None if ta is None else r2(ing * ta / 100), 'tope': R['tope'], 'dentro': ing <= R['tope']}


def iva(K, cobros, gastos, pm):
    g, o = K['iva']['gen'], K['iva']['op']
    tras, acred = r2(cobros * g / 100), r2(gastos * g / 100)
    general, opcion = r2(tras - acred), r2(cobros * o / 100)
    dif = r2(general - opcion)   # positivo: con la opción se paga menos
    return {'tras': tras, 'acred': acred, 'general': general, 'opcion': opcion, 'dif': dif, 'difA': r2(dif * 12),
            'prop': r2(acred / tras * 100) if tras else 0, 'eq': K['iva']['eq'], 'conviene': 'opcion' if dif > 0 else ('general' if dif < 0 else 'igual'),
            'retPm': r2(cobros * pm / 100 * g / 100 * K['iva']['ret'][0] / K['iva']['ret'][1])}


def anual(K, ingreso, retenido, generales, funerales, retiro, colegiaturas):
    d, uma = K['ded'], K['uma']
    tope = r2(min(d['veces'] * uma, ingreso * d['pct'] / 100))
    fun = r2(min(funerales, d['funVeces'] * uma))
    glob = r2(min(generales + fun, tope))
    ret = r2(min(retiro, ingreso * d['retPct'] / 100, d['retVeces'] * uma))
    col = r2(sum(min(m, K['col'][n]) for n, m in colegiaturas))
    base = r2(max(0, ingreso - glob - ret - col))
    isr = tarifa(K, base)
    return {'tope': tope, 'fun': fun, 'glob': glob, 'ret': ret, 'col': col, 'base': base, 'isr': isr, 'saldo': r2(isr - retenido)}


def obligado(K, ingreso, casos):
    return ingreso > K['anualDesde'] or casos > 0


def compara(K, perfil, sub, mensual, gastos):
    ing = r2(mensual * 12)
    util = r2(max(0, (mensual - gastos) * 12))
    out = {'ing': ing, 'util': util, 'general': tarifa(K, util)}
    if perfil == 'plataformas':
        out['ret'] = r2(ing * K['plat'][sub] / 100)
        out['definitivo'] = ing <= K['plat']['definitivo']
        out['saldo'] = r2(out['general'] - out['ret'])
        return out
    for a in ('2026', '2027'):
        R = K['resico'][a]
        t = tasa_resico(R['anu'], ing)
        out['resico' + a] = None if t is None else r2(ing * t / 100)
    if perfil == 'arrendamiento':
        out['baseCiega'] = r2(ing * (100 - K['ciega']) / 100)
        out['ciega'] = tarifa(K, out['baseCiega'])
    return out


# ---------------------------------------------------------------- la página
def ico(nombre, tam=26):
    import auditor_bento
    return auditor_bento.ico(nombre, tam, 'fsim-ico')


def campo(i, etq, ayuda='', ej=''):
    return ('<label class="fsim-campo" for="%s"><span class="fsim-etq">%s</span><input class="fsim-inp" id="%s" type="text" inputmode="decimal" autocomplete="off" '
            'placeholder="%s"%s>%s</label>') % (i, etq, i, ej or '$', ' aria-describedby="%s-a"' % i if ayuda else '',
                                               '<small class="fsim-ayuda" id="%s-a">%s</small>' % (i, ayuda) if ayuda else '')


def casilla(i, tx, grupo):
    return '<label class="fsim-casilla"><input type="checkbox" id="%s" data-fs="%s"><span>%s</span></label>' % (i, grupo, tx)


def botones(ej):
    return ('<p class="fsim-botones"><button type="submit" class="fsim-pri">Calcular</button> '
            '<button type="button" class="fsim-sec" data-fs-ej="%s">Probar con un ejemplo ficticio</button> '
            '<button type="reset" class="fsim-sec">Limpiar</button></p>') % e(json.dumps(ej), quote=True)


def li(i):
    """Un dato en lista: con su valor si es una cifra; si su valor es texto, basta su concepto."""
    v = D(i).get('valor') or {}
    return ft._li(i, e(D(i)['concepto']) if any(isinstance(x, str) for x in v.values()) else None)


def fundamento(ids, pend=()):
    """Las citas de lo que usa un módulo y, con su nombre, lo que sigue pendiente."""
    h = ''.join(ft.textual(i) for i in ids)
    if pend:
        h += '<p><b>Lo que todavía no se publica o no se cotejó:</b></p><ul class="pa-lista">%s</ul>' % ''.join(ft.pend(i) for i in pend)
    return '<details class="fis-notas fsim-fund"><summary>El fundamento de esta cuenta, con su cita</summary><div class="fsim-fund-c">%s</div></details>' % h


def oficial_auditada():
    return ('<p class="pa-chico fsim-leyenda"><span class="est-chip est-oficial">oficial</span> son las tasas, las tarifas y los topes, tal como están en su documento. '
            '<span class="est-chip est-derivado">auditada</span> es la cuenta que el simulador hace con ellos y con lo que tú escribes. %s</p>' % NO_ASESORIA)


def _m_resico():
    rige = '<p class="fis-rige"><b>Ojo con la fecha:</b> el IVA opcional y el tope nuevo %s. Hasta el 31 de diciembre de 2026 valen las cifras de 2026.</p>' % ft.RIGE
    eq = D('iva-opcional-resico-equilibrio')
    form = '<form class="fsim-form" id="fsF1" novalidate><div class="fsim-campos">%s%s%s</div>%s</form>' % (
        campo('fs1c', 'Lo que cobras al mes, sin IVA', 'Tus ingresos efectivamente cobrados en un mes típico.'),
        campo('fs1g', 'Tus compras y gastos del mes con IVA de %s, sin el IVA' % T('sin-cambio-iva-general'), 'Solo los que te trasladan IVA y podrías acreditar.'),
        campo('fs1p', '¿Qué parte de lo que cobras te la pagan personas morales? (%)', 'De 0 a 100. A esa parte le retienen ISR.', '%'),
        botones({'fs1c': '60000', 'fs1g': '20000', 'fs1p': '50'}))
    return (rige + form + '<div class="fsim-res" id="fsR1" aria-live="polite"></div>' +
            '<p class="fis-op"><b>El punto de equilibrio</b> %s: <b>%s</b> del IVA que trasladas. %s. %s</p>'
            % (ft.chip('iva-opcional-resico-equilibrio'), T('iva-opcional-resico-equilibrio'), e(ft._e(eq['operacion'])), e(eq['nota'])) +
            '<ul class="fis-lista">%s%s%s%s</ul>' % (
                li('iva-opcional-resico-aviso'), li('iva-opcional-resico-sin-acreditamiento'), li('retencion-resico-pm'), li('resico-pf-sin-deducciones')) +
            fundamento(['iva-opcional-resico-7', 'iva-opcional-resico-sin-acreditamiento', 'iva-opcional-resico-aviso', 'iva-opcional-resico-equilibrio', 'retencion-iva-dos-terceras',
                        'resico-pf-tope-2027', 'resico-pf-salida-2027', 'retencion-resico-pm'], ['rmf-2027', 'isr-tarifas-2027']) +
            ft._tarifa('resico-pf-mensual-2026', False) + ft._tarifa('resico-pf-mensual-2027', False) + oficial_auditada())


def _m_anual():
    casos = [('fs2o1', 'Tuve otros ingresos acumulables además de mi sueldo'), ('fs2o2', 'Trabajé para dos o más patrones a la vez'),
             ('fs2o3', 'Dejé de trabajar antes del 31 de diciembre'), ('fs2o4', 'Mis ingresos vienen del extranjero o de quien no está obligado a retener'),
             ('fs2o5', 'Avisé por escrito a mi patrón que presentaría la declaración')]
    niveles = ''.join('<option value="%s">%s (hasta %s)</option>' % (k, n, P('colegiaturas', k)) for k, n in NIVELES)
    form = ('<form class="fsim-form" id="fsF2" novalidate><div class="fsim-campos">%s%s</div>'
            '<fieldset class="fsim-grupo"><legend>¿Estoy obligado a presentarla? Marca lo que te pasó en 2026</legend>%s</fieldset>'
            '<fieldset class="fsim-grupo"><legend>Tus deducciones del año</legend><div class="fsim-campos">%s%s%s</div>'
            '<div id="fs2cols" data-niveles="%s"></div><p><button type="button" class="fsim-sec" id="fs2mas">Agregar una colegiatura</button></p></fieldset>%s</form>') % (
        campo('fs2i', 'Tu ingreso gravable del año por sueldos', 'El de tu constancia o tus recibos de nómina, ya sin la parte exenta.'),
        campo('fs2r', 'El ISR que te retuvieron en el año', 'La suma de todos tus patrones.'),
        ''.join(casilla(i, tx, 'caso') for i, tx in casos),
        campo('fs2g', 'Deducciones que entran al tope global', 'Honorarios médicos, dentales y hospitalarios, primas de gastos médicos, intereses reales de tu crédito hipotecario.'),
        campo('fs2f', 'Gastos funerarios', 'Hasta %s veces la UMA anual: %s.' % (N('tope-gastos-funerales', 'veces_uma_anual'), P('tope-gastos-funerales', 'pesos'))),
        campo('fs2a', 'Aportaciones complementarias de retiro', 'Van aparte del tope global, con su propio límite.'),
        e('<option value="">Nivel educativo</option>' + niveles, quote=True),
        botones({'fs2i': '480000', 'fs2r': '82000', 'fs2g': '45000', 'fs2f': '0', 'fs2a': '20000'}))
    return ('<p>Es la declaración anual de 2026, que se presenta en 2027: vence el <b>%s</b> %s (%s).</p>'
            % (F('calendario-anual-pf-2026', 'vence'), ft.chip('calendario-anual-pf-2026'), ft.liga('calendario-anual-pf-2026')) +
            form + '<div class="fsim-res" id="fsR2" aria-live="polite"></div>' +
            '<ul class="fis-lista">%s%s%s%s%s</ul>' % (li('anual-asalariados-obligados'), li('tope-deducciones-personales'), li('tope-aportaciones-retiro'),
                                                     li('colegiaturas-fuera-del-tope'), li('tope-gastos-funerales')) +
            '<p class="pa-chico">%s Lo que el simulador no considera: el subsidio para el empleo, los donativos y el %s de «todos tus ingresos» cuando además tienes ingresos exentos '
            '(aquí se toma sobre el ingreso que escribes).</p>' % (e(D('anual-asalariados-obligados')['nota']), T('tope-deducciones-personales', 'porcentaje_ingresos')) +
            fundamento(['anual-asalariados-obligados', 'tope-deducciones-personales', 'tope-aportaciones-retiro', 'colegiaturas', 'colegiaturas-fuera-del-tope', 'isr-tarifa-anual-2026'],
                       ['isr-tarifas-2027', 'uma-2027']) +
            ft._tarifa('isr-tarifa-anual-2026', True) + oficial_auditada())


def _m_regimenes():
    perf = ''.join('<option value="%s">%s</option>' % x for x in (('servicios', 'Actividad empresarial o servicios profesionales'), ('arrendamiento', 'Arrendamiento de inmuebles'),
                                                                 ('plataformas', 'Plataformas digitales')))
    sub = ''.join('<option value="%s">%s (retención de %s)</option>' % (k, n, T('retencion-plataformas-lif') if k == 'enajenacion_y_servicios' else T('retencion-plataformas-ley', k))
                  for k, n in PLATAFORMAS)
    form = ('<form class="fsim-form" id="fsF3" novalidate><div class="fsim-campos">'
            '<label class="fsim-campo" for="fs3p"><span class="fsim-etq">¿De qué son tus ingresos?</span><select class="fsim-inp" id="fs3p">%s</select></label>'
            '<label class="fsim-campo" for="fs3s" id="fs3sCaja" hidden><span class="fsim-etq">¿Qué haces en la plataforma?</span><select class="fsim-inp" id="fs3s">%s</select></label>'
            '%s%s</div><fieldset class="fsim-grupo"><legend>Los candados del RESICO</legend>%s</fieldset>%s</form>') % (
        perf, sub, campo('fs3m', 'Lo que cobras al mes, sin IVA'), campo('fs3g', 'Tus gastos deducibles del mes', 'Los que tienes con factura y son de tu actividad.'),
        casilla('fs3x', 'Estoy en alguno de estos casos: soy socio, accionista o integrante de una persona moral, resido en el extranjero con establecimiento permanente en el país, '
                        'tengo ingresos en regímenes fiscales preferentes o cobro ingresos asimilados a salarios', 'excl'),
        botones({'fs3m': '45000', 'fs3g': '15000'}))
    return (form + '<div class="fsim-res" id="fsR3" aria-live="polite"></div>' +
            '<ul class="fis-lista">%s%s%s%s%s%s</ul>' % (li('resico-pf-exclusiones'), li('resico-pf-sin-deducciones'), li('isr-utilidad-actividades'),
                                                       li('deduccion-ciega-arrendamiento'), li('plataformas-pago-definitivo'), li('sin-cambio-plataformas')) +
            '<p class="pa-chico">%s %s La comparación es solo del ISR del año: no incluye el IVA, las cuotas de seguridad social ni los impuestos locales.</p>'
            % (e(D('resico-pf-exclusiones')['nota']), e(D('plataformas-pago-definitivo')['nota'])) +
            fundamento(['resico-pf-exclusiones', 'resico-pf-sin-deducciones', 'isr-utilidad-actividades', 'deduccion-ciega-arrendamiento', 'retencion-plataformas-ley',
                        'retencion-plataformas-lif', 'plataformas-pago-definitivo'], ['resico-plataformas', 'isr-tarifas-2027']) +
            ft._tarifa('resico-pf-anual-2026', False) + ft._tarifa('resico-pf-anual-2027', False) + oficial_auditada())


def _punto(i, titulo, cuerpo, ids, pend=()):
    fu = ' · '.join(ft.liga(x) for x in ids)
    p = ''.join('<p class="pa-chico"><b>Pendiente</b> %s: %s Quién lo debe: %s.</p>' % (ft.chip(x), e(D(x)['motivo']), e(D(x)['quien'])) for x in pend)
    return ('<li class="fsim-punto"><label class="fsim-casilla"><input type="checkbox" data-fs-punto="%s"><span><b>%s</b></span></label>'
            '<div class="fsim-punto-c"><p>%s</p>%s<p class="pa-chico">%s</p></div></li>') % (i, titulo, cuerpo, p, fu)


def _m_blindaje():
    cal = [s for s in ft.pagina()['secciones'] if s['id'] in ('calendario', 'pendientes')]
    puntos = [
        _punto('buzon', 'Tengo habilitado mi buzón tributario y mis medios de contacto al día',
               'La multa por no habilitarlo o no actualizar tus medios de contacto va de <b>%s</b> a <b>%s</b> y se aplica desde el <b>%s</b>. %s'
               % (P('multa-buzon-tributario', 'minima'), P('multa-buzon-tributario', 'maxima'), F('multa-buzon-desde'), e(D('buzon-opcion-asalariados')['concepto']) + '.'),
               ['multa-buzon-tributario', 'multa-buzon-desde', 'buzon-opcion-asalariados', 'buzon-tributario-que-es'], ['buzon-excepcion-resico']),
        _punto('proveedores', 'Revisé a mis proveedores contra la lista 69-B del SAT',
               'Si un proveedor tuyo queda en la lista definitiva, tienes <b>%s días</b> para acreditar que la operación fue real o corregir tu situación. '
               'Revísalos con el <a href="herramienta-inspector-padron.html">padrón de contrapartes</a> o con el <a href="herramienta-inspector-factura.html">Lector de facturas</a>: '
               'tus XML se leen en tu navegador, sin subirlos y sin tu Contraseña del SAT.' % N('lista-69b-receptor'), ['lista-69b-receptor']),
        _punto('visita', 'Sé qué hacer ante una visita por comprobantes presuntamente falsos',
               'El procedimiento dura a lo más <b>%s días hábiles</b>, y %s. Si te restringen el sello digital, tienes <b>%s días hábiles</b> para pedir la aclaración.'
               % (N('visita-cfdi-falsos-plazo'), e(D('visita-cfdi-falsos-suspension')['concepto'][0].lower() + D('visita-cfdi-falsos-suspension')['concepto'][1:]),
                  N('csd-restriccion-aclaracion')), ['visita-cfdi-falsos-plazo', 'visita-cfdi-falsos-suspension', 'csd-restriccion-aclaracion'], ['visita-cfdi-falsos-pruebas']),
        _punto('pagos', 'Si estoy en RESICO, presento todos mis pagos mensuales y la anual',
               '%s. Los pagos mensuales vencen el día 17, recorrido al siguiente día hábil: las fechas de 2027 están abajo.' % e(D('resico-salida-por-omision')['concepto']),
               ['resico-salida-por-omision', 'calendario-dia-17']),
        _punto('aviso', 'Si voy a tomar el IVA opcional de %s, presento el aviso a tiempo' % T('iva-opcional-resico-7'),
               '%s. %s' % (e(D('iva-opcional-resico-aviso')['concepto']), e(D('iva-opcional-resico-aviso')['nota'])), ['iva-opcional-resico-aviso', 'iva-opcional-resico-sin-acreditamiento'], ['rmf-2027']),
        _punto('estimulo', 'Si tengo adeudos de %s o anteriores, revisé el estímulo de regularización' % N('estimulo-regularizacion-100', 'adeudos_hasta_ejercicio'),
               'Condona el <b>%s</b> de multas, recargos y gastos de ejecución si pagas a más tardar el <b>%s</b>; quien tiene créditos firmes pide su aplicación a más tardar el <b>%s</b>. '
               'El <b>%s</b> es solo para créditos firmes de multas por obligaciones distintas a las de pago. %s.'
               % (T('estimulo-regularizacion-100', 'porcentaje'), F('estimulo-regularizacion-100', 'pago_a_mas_tardar'), F('estimulo-regularizacion-solicitud'), T('estimulo-regularizacion-90'),
                  e(D('estimulo-regularizacion-exclusiones')['concepto'])),
               ['estimulo-regularizacion-100', 'estimulo-regularizacion-90', 'estimulo-regularizacion-solicitud', 'estimulo-regularizacion-exclusiones']),
        _punto('depositos', 'Puedo explicar mis depósitos en efectivo y mis gastos del año',
               '%s. %s %s.' % (e(D('depositos-efectivo-informe')['concepto']), e(D('depositos-efectivo-informe')['nota']), e(D('discrepancia-fiscal')['concepto'])),
               ['depositos-efectivo-informe', 'discrepancia-fiscal']),
        _punto('anual', 'Tengo en la agenda mi declaración anual de 2026',
               'La de personas físicas vence el <b>%s</b> y la de personas morales, el <b>%s</b>.' % (F('calendario-anual-pf-2026', 'vence'), F('calendario-anual-pm-2026', 'vence')),
               ['calendario-anual-pf-2026', 'calendario-anual-pm-2026']),
    ]
    return ('<p>Marca lo que ya tienes resuelto. La lista se guarda solo en este navegador, si tú quieres: nunca guarda montos ni datos tuyos, y la borras con su botón.</p>'
            '<p class="fsim-avance" id="fsAvance" aria-live="polite"></p><ul class="fsim-lista">%s</ul>'
            '<p class="fsim-botones"><button type="button" class="fsim-sec" id="fsBorra">Borrar mi lista de este navegador</button></p>'
            '<h3 class="fsim-h3">Calendario fiscal 2027</h3><p class="fsim-prox" id="fsProx" aria-live="polite"></p>%s'
            '<h3 class="fsim-h3">Lo que falta por publicar (pendiente)</h3><p>Nada de esto se da por cerrado: cada renglón dice quién lo debe y dónde debe aparecer.</p>%s%s') % (
        ''.join(puntos), cal[0]['bloque'], cal[1]['bloque'], oficial_auditada())


def pagina():
    aud = 'herramienta-inspector-pregunta.html?q=%s'
    secc = [
        {'id': 'resico', 'pestana': (ico('factura'), 'Decisor RESICO 2027', 'IVA opcional o régimen general, tu ISR y el tope'),
         'titulo': 'Decisor RESICO 2027: IVA opcional o régimen general',
         'texto': 'Escribe lo que cobras y lo que gastas en un mes típico. El simulador compara el IVA del régimen general con la opción de %s, calcula tu ISR del RESICO y te dice si cabes en el tope.'
                  % T('iva-opcional-resico-7'), 'tarjetas': [], 'bloque': _m_resico()},
        {'id': 'anual', 'pestana': (ico('documento'), 'Declaración anual 2026', 'Sueldos: ¿estoy obligado? y saldo a favor o a cargo'),
         'titulo': 'Declaración anual 2026 de quien tiene sueldo',
         'texto': 'Dos cuentas: si estás obligado a presentarla, y cuánto ISR resulta con tus deducciones personales, para saber si queda saldo a favor o a cargo.',
         'tarjetas': [], 'bloque': _m_anual()},
        {'id': 'regimenes', 'pestana': (ico('panel'), 'Comparador de regímenes', 'El ISR del año en cada régimen, lado a lado'),
         'titulo': 'Comparador de regímenes',
         'texto': 'El ISR de un año con los mismos ingresos y gastos en cada régimen que la ley te deja elegir, lado a lado.', 'tarjetas': [], 'bloque': _m_regimenes()},
        {'id': 'blindaje', 'pestana': (ico('escudo'), 'Blindaje SAT 2027', 'Lista de pendientes tuyos y calendario'),
         'titulo': 'Lista de blindaje ante el SAT 2027 y calendario',
         'texto': 'Lo que conviene tener en orden antes y durante 2027, cada punto con su artículo, y las fechas del año.', 'tarjetas': [], 'bloque': _m_blindaje()},
    ]
    cero = ('<div class="fsim-cero">%s<p><b>Cero CIEC.</b> Todo se calcula en tu navegador: no pedimos tu Contraseña del SAT ni tu e.firma, y tus ingresos, tus gastos y tus montos '
            'no se envían ni se guardan en ningún servidor.</p></div>') % ico('escudo', 30)
    return {
        'archivo': ARCHIVO, 'menu': TITULO, 'menu_archivo': 'aprende.html', 'padre': ('aprende.html', 'Aprende'), 'padre2': (ft.ARCHIVO, 'Reforma fiscal 2026 → 2027'),
        'icono': '', 'sin_icono_lema': True, 'titulo': TITULO + ' · Cero CIEC', 'lema': 'Cuatro cuentas con las cifras oficiales de 2026 y de 2027, hechas en tu navegador',
        'estilos': ['asistente.css', 'fiscal-simulador.css'], 'scripts': ['fiscal-simulador.js'], 'pestanas': True, 'primera': True,
        'pista': 'Elige un módulo.',
        'entrada': ('Un simulador para decidir con números: el IVA opcional del RESICO, tu declaración anual, qué régimen te cuesta menos ISR y lo que conviene tener en orden ante el SAT. '
                    'Ninguna tasa, tarifa ni fecha está escrita a mano: todas se leen de la base fiscal, con su artículo y su cita, y lo que aún no se publica se dice como pendiente.'),
        'cab_bloque': cero + '<script type="application/json" id="fsDatos">%s</script>' % json.dumps(datos(), ensure_ascii=False).replace('</', '<\\/'),
        'pie_extra': ('<p class="fsim-pie"><a class="fsim-sec" href="%s">Ver la reforma fiscal 2026 → 2027 completa</a> '
                      '<a class="fsim-sec" href="%s">Pregúntale al Auditor por tu caso</a></p>') % (ft.ARCHIVO, e(aud % 'Qu%C3%A9%20cambia%20en%202027', quote=True)),
        'secciones': secc}


# ---------------------------------------------------------------- la prueba
PERMITIDOS = {'0', '1', '2', '12', '100', '0.5'}   # aritmética, nunca un dato fiscal: cero, uno, dos decimales, doce meses, por ciento y el medio centavo del redondeo


def _literales_py(ruta):
    """Los números escritos en las fórmulas de este módulo (sin las cadenas ni los comentarios)."""
    src = open(ruta, encoding='utf-8').read()
    src = src[src.index('# ' + '-' * 64 + ' las fórmulas'):src.index('# ' + '-' * 64 + ' la página')]
    return [t.string for t in tokenize.generate_tokens(io.StringIO(src).readline) if t.type == tokenize.NUMBER]


def _literales_js(ruta):
    src = open(ruta, encoding='utf-8').read()
    src = re.sub(r'/\*.*?\*/', ' ', src, flags=re.S)
    src = re.sub(r"'(?:\\.|[^'\\\n])*'|\"(?:\\.|[^\"\\\n])*\"", "''", src)
    src = re.sub(r'//[^\n]*', ' ', src)
    return re.findall(r'(?<![A-Za-z_$\d.])\d+(?:\.\d+)?', src)


def _casos(K):
    """Casos al azar, con semilla fija, para comparar Python con el navegador."""
    rnd = random.Random(len(K['isr']))
    tope = K['resico']['2027']['tope']
    niveles = sorted(K['col'])
    out = []
    for _ in range(100):
        c, g = round(rnd.uniform(0, tope / 10), 2), round(rnd.uniform(0, tope / 12), 2)
        out.append(['iva', c, g, rnd.randint(0, 100)])
        out.append(['resico', rnd.choice(['2026', '2027']), round(rnd.uniform(0, tope / 8), 2), rnd.randint(0, 100)])
        i = round(rnd.uniform(0, tope), 2)
        out.append(['anual', i, round(rnd.uniform(0, i / 3), 2), round(rnd.uniform(0, i / 4), 2), round(rnd.uniform(0, K['uma'] * 2), 2), round(rnd.uniform(0, i / 5), 2),
                    [[rnd.choice(niveles), round(rnd.uniform(0, K['uma']), 2)] for _ in range(rnd.randint(0, 3))]])
        out.append(['compara', rnd.choice(['servicios', 'arrendamiento', 'plataformas']), rnd.choice(sorted(k for k in K['plat'] if k != 'definitivo')),
                    round(rnd.uniform(0, tope / 8), 2), round(rnd.uniform(0, tope / 10), 2)])
    return out


def _corre(K, caso):
    f = {'iva': iva, 'resico': resico, 'anual': anual, 'compara': compara}[caso[0]]
    return f(K, *caso[1:])


def _igual(a, b):
    if isinstance(a, dict):
        return isinstance(b, dict) and set(a) == set(b) and all(_igual(a[k], b[k]) for k in a)
    if isinstance(a, bool) or a is None or isinstance(a, str):
        return a == b
    return b is not None and not isinstance(b, (bool, str)) and abs(a - b) < 0.006


def prueba():
    errores = []
    K = datos()
    pg = pagina()
    # 1. Ningún número de la página sale de fuera de la base.
    for s in pg['secciones']:
        for x in ft._sueltos(s['titulo'] + ' ' + s['texto'] + ' ' + s['bloque'] + ' ' + ' '.join(s['pestana'][1:])):
            errores.append('módulo %s: un número que no sale de la base: «…%s…»' % (s['id'], x))
        if s['id'] != 'blindaje' and 'fsim-fund' not in s['bloque']:
            errores.append('módulo %s: sin su fundamento' % s['id'])
    for x in ft._sueltos(pg['entrada'] + ' ' + pg['lema'] + ' ' + re.sub(r'<script.*?</script>', ' ', pg['cab_bloque'], flags=re.S)):
        errores.append('entrada: un número que no sale de la base: «…%s…»' % x)
    # 2. Ni este módulo ni el JavaScript escriben un número: solo aritmética.
    for ruta, lee in ((os.path.abspath(__file__), _literales_py), (JS, _literales_js)):
        for n in sorted(set(lee(ruta)) - PERMITIDOS):
            errores.append('%s: el número %s está escrito a mano; todo dato fiscal se lee de docs/fiscal-2027/' % (os.path.basename(ruta), n))
    # 3. Lo de 2027 se dice sin mover lo de 2026, y lo pendiente se enseña como pendiente.
    m1 = pg['secciones'][0]['bloque']
    if ft.RIGE not in m1 or 'valen las cifras de 2026' not in m1:
        errores.append('módulo resico: lo de 2027 se dice «%s», sin mover las cifras de 2026' % ft.RIGE)
    for i in ('rmf-2027', 'isr-tarifas-2027', 'resico-plataformas', 'buzon-excepcion-resico', 'visita-cfdi-falsos-pruebas'):
        if 'data-pend="%s%s"' % (ft.PRE, i) not in ''.join(s['bloque'] for s in pg['secciones']):
            errores.append('el pendiente %s no se enseña como pendiente' % i)
    pend = [i for i, d in ft._base()['D'].items() if d['estado'] == 'pendiente']
    for i in pend:
        if 'data-pend="%s%s"' % (ft.PRE, i) not in pg['secciones'][-1]['bloque']:
            errores.append('blindaje: el pendiente %s no está en la tabla de lo que falta' % i)
    # 4. Los casos conocidos.
    g, o = K['iva']['gen'], K['iva']['op']
    cobros = K['resico']['2026']['men'][0][0]
    x = iva(K, cobros, cobros * K['iva']['eq'] / 100, 0)
    if x['dif'] != 0 or x['conviene'] != 'igual' or abs(x['prop'] - (g - o) / g * 100) > 0.005:
        errores.append('punto de equilibrio: con gastos de %s %% de los cobros el IVA opcional y el general deben dar lo mismo (dif %s)' % (K['iva']['eq'], x['dif']))
    if iva(K, cobros, 0, 0)['conviene'] != 'opcion' or iva(K, cobros, cobros, 0)['conviene'] != 'general':
        errores.append('IVA: sin gastos conviene la opción, y con gastos iguales a los cobros, el régimen general')
    d, uma = K['ded'], K['uma']
    corte = d['veces'] * uma / (d['pct'] / 100)   # el ingreso donde los dos límites del tope global se cruzan
    abajo, arriba = anual(K, corte / 2, 0, corte, 0, 0, []), anual(K, corte * 2, 0, corte, 0, 0, [])
    if abs(abajo['tope'] - corte / 2 * d['pct'] / 100) > 0.006 or abs(arriba['tope'] - d['veces'] * uma) > 0.006 or abajo['glob'] != abajo['tope'] or arriba['glob'] != arriba['tope']:
        errores.append('tope global: debajo de %.2f manda el porcentaje de los ingresos y arriba, las veces de la UMA' % corte)
    y = anual(K, corte, 0, 0, 0, corte, [])
    if abs(y['ret'] - min(corte * d['retPct'] / 100, d['retVeces'] * uma)) > 0.006 or y['glob'] != 0:
        errores.append('aportaciones de retiro: van aparte del tope global, con su propio límite')
    nivel = sorted(K['col'])[0]
    if anual(K, corte, 0, 0, 0, 0, [[nivel, K['col'][nivel] * 2]])['col'] != K['col'][nivel]:
        errores.append('colegiaturas: cada una se topa con el límite de su nivel')
    for n, f in enumerate(K['isr']):
        inf, sup, cuota = f['inf'], f['sup'], f['cuota']
        if abs(tarifa(K, inf) - cuota) > 0.006:
            errores.append('tarifa anual, tramo %d: en su límite inferior el ISR es su cuota fija' % (n + 1))
        if sup is not None and abs(tarifa(K, sup + 0.01) - K['isr'][n + 1]['cuota']) > 0.011:
            errores.append('tarifa anual, tramo %d: un centavo arriba de su límite superior empieza la cuota del siguiente' % (n + 1))
    for a in ('2026', '2027'):
        R = K['resico'][a]
        for nombre, t in (('mensual', R['men']), ('anual', R['anu'])):
            for n, (hasta, tasa) in enumerate(t):
                sig = t[n + 1][1] if n + 1 < len(t) else None
                if tasa_resico(t, hasta) != tasa or tasa_resico(t, hasta + 0.01) != sig:
                    errores.append('RESICO %s, tabla %s: el salto del tramo %d no cae donde dice la tabla' % (a, nombre, n + 1))
        if not resico(K, a, R['tope'] / 12, 0)['dentro'] or resico(K, a, R['tope'] / 12 + 1, 0)['dentro']:
            errores.append('RESICO %s: el aviso del tope no salta en su tope' % a)
    if obligado(K, K['anualDesde'], 0) or not obligado(K, K['anualDesde'] + 0.01, 0) or not obligado(K, 0, 1):
        errores.append('declaración anual: obliga pasar del monto de la ley o estar en cualquiera de sus otros casos')
    z = compara(K, 'arrendamiento', '', cobros, 0)
    if abs(z['baseCiega'] - z['ing'] * (100 - K['ciega']) / 100) > 0.006:
        errores.append('arrendamiento: la deducción ciega es el porcentaje de la ley sobre los ingresos')
    lim = K['plat']['definitivo']
    if not compara(K, 'plataformas', 'hospedaje', lim / 12, 0)['definitivo'] or compara(K, 'plataformas', 'hospedaje', lim / 12 + 1, 0)['definitivo']:
        errores.append('plataformas: el pago definitivo solo se ofrece hasta el límite de la ley')
    # 5. Python y el navegador dan lo mismo.
    casos = _casos(K)
    if shutil.which('node'):
        guion = ('const S=require(%s);const K=%s;const C=%s;'
                 'process.stdout.write(JSON.stringify(C.map(c=>S[c[0]].apply(null,[K].concat(c.slice(1))))));') % (json.dumps(JS), json.dumps(K), json.dumps(casos))
        r = subprocess.run(['node', '-e', guion], capture_output=True, text=True)
        if r.returncode:
            errores.append('fiscal-simulador.js no corre en node: %s' % r.stderr.strip()[:300])
        else:
            for c, js in zip(casos, json.loads(r.stdout)):
                py = _corre(K, c)
                if not _igual(py, js):
                    errores.append('Python y JavaScript no dan lo mismo en %s: %s contra %s' % (c, py, js))
                    break
    else:
        errores.append('falta node para comparar las fórmulas de Python con las del navegador')
    if errores:
        for x in errores:
            print('fiscal_simulador: ERROR:', x)
        return 1
    print('fiscal_simulador: %d módulos; ningún número fuera de la base; equilibrio del IVA, tope global, saltos de tarifa y %d casos iguales en Python y en JavaScript'
          % (len(pg['secciones']), len(casos)))
    return 0


if __name__ == '__main__':
    if '--prueba' in sys.argv:
        sys.exit(prueba())
    print(__doc__)
