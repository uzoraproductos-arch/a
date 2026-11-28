#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La base fiscal 2026-2027 en las cuatro partes públicas (Ola 2, Ronda 39).

Lee docs/fiscal-2027/ (fiscal_2027.py) y arma, sin escribir una sola cifra:

- chat():       D.fis del Auditor: un tema por duda fiscal frecuente, con su
                cita textual, su chip y su liga a la página.
- pagina():     «Reforma fiscal 2026 → 2027 y calendario fiscal»
                (fiscal-reforma-2027.html), en el Planisferio.
- columnas():   cuatro verificaciones de servicio público para el Noticiero
                (sección «Verificado» de columnas.js; las escribe --columnas).
- glosario():   los términos del SAT para el Diccionario
                (integrar_glosario_fiscal.py).
- marco():      el bloque «Reforma 2027» del Marco legal.
- pendientes(): cada pendiente de la base, como ficha del Registro.

Toda cifra, tasa, fecha y artículo pasa por P(), T(), N(), F() o A(), que la
leen del JSON y anotan lo que entregaron. `--prueba` (corre en revision.py)
revisa que ningún número de lo que se publica haya salido de otro lado.

    python3 herramientas/fiscal_temas.py --prueba
    python3 herramientas/fiscal_temas.py --columnas   # escribe columnas.js
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fiscal_2027 as fb  # noqa: E402

RAIZ = fb.RAIZ
ARCHIVO = 'fiscal-reforma-2027.html'
TITULO = 'Reforma fiscal 2026 → 2027 y calendario fiscal'
SIMULADOR = 'fiscal-simulador-2027.html'   # Ronda 40: lo arma fiscal_simulador.py
SIM_TITULO = 'Simulador y Blindaje Fiscal 2027'
PRE = 'fiscal-'          # el id de cada pendiente en el Registro: fiscal-<id>
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
RIGE = 'rige desde el 1 de enero de 2027'
NO_ASESORIA = 'Es lo que dice el texto oficial, no una asesoría fiscal: tu caso puede tener particularidades que aquí no se ven.'

# Cómo se nombra en corto cada fuente (su nombre completo y su fecha salen de fuentes.json).
CORTO = {'LISR': 'LISR', 'CFF': 'CFF', 'LIVA': 'LIVA', 'LFPCA': 'LFPCA', 'RLIVA': 'Reglamento de la LIVA', 'LIF_2026': 'LIF 2026', 'LIF_2027': 'LIF 2027',
         'rmf26': 'RMF 2026', 'anx26': 'RMF 2026', 'dlisr27': 'Decreto de reforma a la LISR', 'ben13': 'Decreto de beneficios fiscales',
         'des16': 'Decreto de desindexación', 'sub26': 'Decreto del subsidio para el empleo', 'uma26': 'INEGI', 'sm26': 'CONASAMI'}
CON_FECHA = ('dlisr27', 'ben13', 'des16', 'sub26', 'uma26', 'sm26')

_M = {}
EMIT = set()   # todo lo que entregaron los lectores de la base: lo único numérico que puede publicarse


def _base():
    if not _M:
        _M['D'] = {d['id']: d for n in fb.MAESTROS for _, d in fb._datos(fb.carga(n))}
        _M['F'] = fb.carga('fuentes.json')['fuentes']
        _M['corte'] = fb.carga('reforma-2027.json')['corte']
        # Los textos de la propia base (concepto, nota, motivo, operación, ligas) también son la base.
        for d in _M['D'].values():
            EMIT.update(str(d[k]) for k in ('concepto', 'nota', 'motivo', 'operacion', 'unidad', 'quien', 'url') if d.get(k))
        EMIT.update(f['url'] for f in _M['F'].values())
    return _M


def D(i):
    return _base()['D'][i]


def _e(s):
    EMIT.add(s)
    return s


def _num(n, dec=None):
    if dec is None:
        dec = 0 if float(n) == int(n) else 2
    return format(n, ',.%df' % dec)


def _v(i, k=None):
    v = D(i)['valor']
    if k is None:
        assert len(v) == 1, i
        k = list(v)[0]
    return v[k]


def P(i, k=None):
    """Pesos, tal como están en la base."""
    return _e('$' + _num(_v(i, k)))


def T(i, k=None):
    """Una tasa o un porcentaje."""
    n = _v(i, k)
    return _e((('%.4f' % n).rstrip('0').rstrip('.') if float(n) != int(n) else str(int(n))) + ' %')


def N(i, k=None):
    """Un número sin unidad (días, veces la UMA, un factor)."""
    n = _v(i, k)
    return _e(_num(n) if not isinstance(n, float) or n >= 100 else ('%.4f' % n).rstrip('0').rstrip('.')) if not isinstance(n, str) else _e(n)


def fecha(iso):
    y, m, d = (int(x) for x in iso.split('-'))
    return _e('%d de %s de %d' % (d, MESES[m - 1], y))


def F(i, k=None):
    return fecha(_v(i, k))


def A(i, n=0):
    """El fundamento de un dato: fuente en corto y artículo."""
    c = D(i)['citas'][n]
    art = c['articulo']
    art = art[0].lower() + art[1:] if art.startswith(('Art.', 'Regla', 'Transitorio', 'Artículo', 'Anexo')) else art
    return _e('%s, %s' % (_fuente_corta(c['fuente']), art.rstrip('.')))


def _fuente_corta(k):
    f = _base()['F'][k]
    return CORTO[k] + (' (%s)' % f['publicacion'] if k in CON_FECHA else '')


def cita(i, n=0):
    return _e(D(i)['citas'][n]['cita'])


def cita_txt(i, n=0):
    """La cita para leerla: con puntos suspensivos si el fragmento empieza o termina a media frase."""
    c = cita(i, n)
    return ('… ' if c[0].islower() else '') + c + ('' if c.rstrip()[-1] in '.;:' else ' …')


def estado(i):
    e = D(i)['estado']
    return 'derivado' if e == 'auditada' else e


def chip(i):
    e = estado(i)
    p = ' data-pend="%s%s"' % (PRE, i) if e == 'pendiente' else ''
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, p, 'auditada' if e == 'derivado' else e)


def _url(k):
    return _base()['F'][k]['url']


def fu(i):
    """Las fuentes de un dato, en el formato del chat: [{que, e, fu: {tx, url}}]."""
    d = D(i)
    if d['estado'] == 'pendiente':
        return [{'que': d['concepto'], 'e': 'pendiente', 'p': PRE + i, 'fu': {'tx': 'Debe publicarlo o integrarlo: %s' % d['quien'], 'url': d['url']}}]
    out = []
    for n, c in enumerate(d['citas']):
        f = _base()['F'][c['fuente']]
        x = {'que': d['concepto'], 'e': estado(i), 'fu': {'tx': _e('%s, %s (%s)' % (f['nombre'], c['articulo'].rstrip('.'), f['publicacion'])), 'url': f['url']}}
        if d.get('operacion') and not n:
            x['op'] = _e(d['operacion'])
        out.append(x)
    return out


def liga(i, n=0):
    c = D(i)['citas'][n]
    return '<a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>' % (html.escape(_url(c['fuente']), quote=True), html.escape(A(i, n)))


def textual(i, n=0):
    """La cita, palabra por palabra, con su fundamento y su chip."""
    return '<p class="fis-cita">La ley lo dice así: «%s» (%s) %s</p>' % (html.escape(cita_txt(i, n)), liga(i, n), chip(i))


def pend(i):
    d = D(i)
    return '<li><b>%s</b> %s. %s Quién lo debe: %s.</li>' % (html.escape(d['concepto']), chip(i), html.escape(d['motivo']), html.escape(d['quien']))


def _valor_txt(i):
    """El valor de un dato, para una tabla: cada clave con su formato."""
    d = D(i)
    v = d.get('valor')
    if not v:
        return ''
    partes = []
    for k, x in v.items():
        if isinstance(x, list):
            tx = ', '.join(fecha(y) for y in x)
        elif isinstance(x, str):
            tx = fecha(x) if re.match(r'^\d{4}-\d{2}-\d{2}$', x) else _e(x)
        elif re.search(r'tasa|porcentaje|^hasta_|^de_|^mas_de|paga$|transporte|hospedaje|enajenacion', k):
            tx = T(i, k)
        elif re.search(r'veces|dias|udis|ejercicio|umbral|factor|millones', k):
            tx = N(i, k)
        else:
            tx = P(i, k)
        partes.append(tx if len(v) == 1 else '%s: %s' % (k.replace('_', ' '), tx))
    return '; '.join(partes)


# ---------------------------------------------------------------- los temas del chat
def _li(i, tx=None, n=0):
    d = D(i)
    v = _valor_txt(i)
    return '<li>%s%s %s <span class="pa-chico">(%s)</span></li>' % (tx or html.escape(d['concepto']), '' if tx or not v else ': <b>%s</b>' % html.escape(v), chip(i), liga(i, n))


def _tema(tit, ancla, rx, parrafos, ids, sug, ci, pendientes=(), nota=None, cita_de=None, rige=False, sim=None):
    h = ''.join('<p>%s</p>' % p for p in parrafos)
    if rige:
        h += '<p class="fis-rige"><b>Ojo con la fecha:</b> esto %s. Hasta el 31 de diciembre de 2026 valen las cifras de 2026.</p>' % RIGE
    for c in ([cita_de] if isinstance(cita_de, str) else (cita_de or [])):
        h += textual(c)
    if pendientes:
        h += '<p><b>Lo que todavía no se publica:</b></p><ul class="pa-lista">%s</ul>' % ''.join(pend(p) for p in pendientes)
    h += '<p class="pa-chico">%s%s</p>' % ((nota + ' ') if nota else '', NO_ASESORIA)
    fuentes = []
    for i in list(ids) + list(pendientes):
        fuentes += fu(i)
    # `sim`: el tema es una cuenta que hace el simulador (Ronda 40); «Saber más» abre su módulo.
    return {'tit': tit, 'rx': rx, 'h': h, 'fu': fuentes, 'ci': ci, 'ir': [SIMULADOR + '#' + sim, SIM_TITULO] if sim else [ARCHIVO + '#' + ancla, TITULO], 'sug': sug}


def _ci(i, v, etq):
    return {'v': v, 'etq': etq, 'e': estado(i)}


def temas():
    t = {}
    # ---- La reforma de 2027
    t['resico_pf'] = _tema(
        'RESICO de personas físicas: el tope sube en 2027', 'cambios',
        r'resico.*(tope|limite|cuanto puedo|millones|sube|cambi|2027|agricol|ganad|agro|pesquer)|(tope|limite).*(resico|simplificado de confianza)|simplificado de confianza.*(2027|tope|cambi)',
        ['En 2026 puedes tributar en el RESICO de personas físicas si tus ingresos no pasan de <b>%s</b> al año. Desde 2027 el tope sube a <b>%s</b>.'
         % (P('resico-pf-tope-2026'), P('resico-pf-tope-2027')),
         'Si te dedicas solo a actividades agrícolas, ganaderas, silvícolas o pesqueras, tus ingresos exentos pasan de <b>%s</b> a <b>%s</b> al año.'
         % (P('resico-agro-exencion-2026'), P('resico-agro-exencion-2027')),
         'Quien rebase el tope sale del régimen. %s Y sale también quien omite %s pagos mensuales o la anual (%s).'
         % (html.escape(D('resico-pf-regreso-2027')['nota']), N('resico-salida-por-omision'), liga('resico-salida-por-omision'))],
        ['resico-pf-tope-2026', 'resico-pf-tope-2027', 'resico-agro-exencion-2026', 'resico-agro-exencion-2027', 'resico-pf-regreso-2027', 'resico-salida-por-omision'],
        ['¿Qué es el IVA opcional del 7 % para RESICO?', '¿Qué cambia para el RESICO de personas morales en 2027?', '¿Qué no cambia en 2027?'],
        [_ci('resico-pf-tope-2026', P('resico-pf-tope-2026'), 'tope del RESICO de personas físicas en 2026'),
         _ci('resico-pf-tope-2027', P('resico-pf-tope-2027'), 'tope desde el 1 de enero de 2027'),
         _ci('resico-agro-exencion-2027', P('resico-agro-exencion-2027'), 'ingresos exentos del campo desde 2027')],
        pendientes=['scjn-pj-209-2026', 'isr-tarifas-2027'], cita_de='resico-pf-tope-2027', rige=True,
        nota='Las tablas de tasas de 2026 y de 2027 están completas en la página.')
    t['resico_pm'] = _tema(
        'RESICO de personas morales: de %s a %s' % (P('resico-pm-tope-2026'), P('resico-pm-tope-2027')), 'cambios',
        r'resico.*(personas? morales?|empresas?|sociedad)|(personas? morales?|empresas?).*(resico|simplificado de confianza)',
        ['El RESICO de personas morales es para empresas con ingresos de hasta <b>%s</b> en 2026. Desde 2027 el tope es de <b>%s</b>.'
         % (P('resico-pm-tope-2026'), P('resico-pm-tope-2027')),
         'Hay un cambio de una sola palabra que importa: %s' % html.escape(D('resico-pm-tope-2027')['nota']),
         'Cuando una persona moral le paga a una persona física del RESICO, le retiene <b>%s</b> del pago (%s).' % (T('retencion-resico-pm'), liga('retencion-resico-pm'))],
        ['resico-pm-tope-2026', 'resico-pm-tope-2027', 'retencion-resico-pm'],
        ['¿Cuál es el tope del RESICO de personas físicas en 2027?', '¿Qué cambia para las empresas de más de 50 millones?'],
        [_ci('resico-pm-tope-2026', P('resico-pm-tope-2026'), 'tope del RESICO de personas morales en 2026'),
         _ci('resico-pm-tope-2027', P('resico-pm-tope-2027'), 'tope desde el 1 de enero de 2027')],
        cita_de='resico-pm-tope-2027', rige=True)
    t['iva7'] = _tema(
        'IVA opcional del %s para RESICO en 2027' % T('iva-opcional-resico-7'), 'cambios',
        r'iva (opcional|del 7|de 7|al 7|del siete|de siete)|7 (por ciento )?de iva|iva.*(opcional|definitivo).*(resico|simplificado)|(resico|simplificado de confianza).* iva ',
        ['En 2027, quien tributa en el RESICO puede optar por pagar el IVA con una tasa de <b>%s</b> sobre lo que efectivamente cobró, como pago definitivo de cada mes. '
         'Sigues trasladando el IVA a tu cliente a la tasa de siempre; lo que cambia es cuánto enteras.' % T('iva-opcional-resico-7'),
         'A cambio, <b>no acreditas</b> el IVA que te trasladaron tus proveedores, y la opción no se puede cambiar durante el año (%s).' % liga('iva-opcional-resico-sin-acreditamiento'),
         'Hay que presentar un aviso de opción dentro de los <b>%s días</b> siguientes a tu primer cobro del año (%s).' % (N('iva-opcional-resico-aviso'), liga('iva-opcional-resico-aviso')),
         '<b>¿Cuándo conviene?</b> Nuestra cuenta, solo para actividades a la tasa de %s: si el IVA que podrías acreditar pasa de <b>%s</b> del que trasladas, te conviene más el régimen de siempre. %s'
         % (T('sin-cambio-iva-general'), T('iva-opcional-resico-equilibrio'), chip('iva-opcional-resico-equilibrio')),
         '<span class="pa-chico">Operación: %s. %s</span>' % (html.escape(_e(D('iva-opcional-resico-equilibrio')['operacion'])), html.escape(D('iva-opcional-resico-equilibrio')['nota']))],
        ['iva-opcional-resico-7', 'iva-opcional-resico-sin-acreditamiento', 'iva-opcional-resico-aviso', 'iva-opcional-resico-equilibrio', 'sin-cambio-iva-general'],
        ['¿Cuál es el tope del RESICO en 2027?', '¿Qué falta por publicar de la reforma 2027?'],
        [_ci('iva-opcional-resico-7', T('iva-opcional-resico-7'), 'IVA opcional sobre lo cobrado, en 2027'),
         _ci('iva-opcional-resico-aviso', N('iva-opcional-resico-aviso') + ' días', 'para presentar el aviso de opción'),
         _ci('iva-opcional-resico-equilibrio', T('iva-opcional-resico-equilibrio'), 'IVA acreditable a partir del cual deja de convenir')],
        pendientes=['rmf-2027'], cita_de='iva-opcional-resico-7', rige=True)
    t['intereses'] = _tema(
        'La retención sobre intereses baja en 2027', 'cambios',
        r'(retencion|retienen|impuesto|isr).*(intereses|ahorro|inversion(es)? en el banco|cetes)|intereses.*(retencion|retienen|banco|ahorro).*(2027|cuanto|tasa)|tasa de retencion.*intereses',
        ['El banco o la institución que te paga intereses te retiene el ISR con una tasa anual sobre el capital: <b>%s</b> en 2026 y <b>%s</b> en 2027.'
         % (T('retencion-intereses-2026'), T('retencion-intereses-2027')),
         'Es la tasa de retención anual de los artículos 54 y 135 de la LISR: la fija cada año la Ley de Ingresos.'],
        ['retencion-intereses-2026', 'retencion-intereses-2027'],
        ['¿Qué cambia en los impuestos en 2027?', '¿Qué no cambia en 2027?'],
        [_ci('retencion-intereses-2026', T('retencion-intereses-2026'), 'retención anual sobre el capital en 2026'),
         _ci('retencion-intereses-2027', T('retencion-intereses-2027'), 'retención anual sobre el capital en 2027')],
        cita_de='retencion-intereses-2027', rige=True)
    t['estimulo'] = _tema(
        'El estímulo de regularización de 2027: perdona multas y recargos, no el impuesto', 'cambios',
        r'(estimulo|condonacion|perdon|perdona|borron|amnistia).*(multas?|recargos?|adeudos?|sat|fiscal|regulariza)|regularizacion (fiscal|2027)|programa de regularizacion|(multas?|recargos?).*(100|perdon|condon)',
        ['En 2027 hay un estímulo del <b>%s</b> de las <b>multas, recargos y gastos de ejecución</b> para adeudos del ejercicio %s o anteriores, si presentas las declaraciones y pagas en una sola exhibición a más tardar el <b>%s</b>.'
         % (T('estimulo-regularizacion-100', 'porcentaje'), N('estimulo-regularizacion-100', 'adeudos_hasta_ejercicio').replace(',', ''), F('estimulo-regularizacion-100', 'pago_a_mas_tardar')),
         '<b>Lo que no perdona:</b> el impuesto. El texto solo nombra multas, recargos y gastos de ejecución: la contribución que se dejó de pagar se cubre.',
         'Si tu crédito fiscal firme es solo de multas por obligaciones distintas de las de pago, el estímulo es de <b>%s</b> (%s).' % (T('estimulo-regularizacion-90'), liga('estimulo-regularizacion-90')),
         'Quien tiene créditos fiscales firmes debe presentar su solicitud a más tardar el <b>%s</b>. %s' % (F('estimulo-regularizacion-solicitud'), html.escape(D('estimulo-regularizacion-solicitud')['nota'])),
         '<b>A quién no le aplica:</b> a quien no desvirtuó los procedimientos de los artículos %s del CFF (%s).' % (N('estimulo-regularizacion-exclusiones'), liga('estimulo-regularizacion-exclusiones'))],
        ['estimulo-regularizacion-100', 'estimulo-regularizacion-90', 'estimulo-regularizacion-solicitud', 'estimulo-regularizacion-exclusiones'],
        ['¿Cuánto son los recargos del SAT en 2027?', '¿Qué es la lista 69-B?', '¿Qué falta por publicar de la reforma 2027?'],
        [_ci('estimulo-regularizacion-100', T('estimulo-regularizacion-100', 'porcentaje'), 'de multas, recargos y gastos de ejecución'),
         _ci('estimulo-regularizacion-solicitud', F('estimulo-regularizacion-solicitud'), 'solicitud de quien tiene créditos firmes'),
         _ci('estimulo-regularizacion-100', F('estimulo-regularizacion-100', 'pago_a_mas_tardar'), 'pago en una sola exhibición, a más tardar')],
        pendientes=['rmf-2027'], cita_de='estimulo-regularizacion-100', rige=True)
    t['grandes'] = _tema(
        'Empresas con más de %s millones de ingresos: límites nuevos en 2027' % N('pm-limite-deducciones'), 'cambios',
        r'(empresas?|personas? morales?|corporativ).*(50 millones|grandes|limite.*(deduccion|perdida)|78 [a-f])|limite.*(deducciones|perdidas fiscales)|78 [a-f]\b|intereses netos|grupos? de sociedades|regimen opcional para grupos|deduccion inmediata',
        ['Desde 2027, las personas morales con ingresos acumulables de más de <b>%s millones de pesos</b> aplican sus deducciones y sus pérdidas fiscales con límites nuevos (%s).'
         % (N('pm-limite-deducciones'), liga('pm-limite-deducciones')),
         'Las pérdidas de ejercicios anteriores se pueden disminuir hasta la mitad de la utilidad fiscal (factor %s, %s), y lo mismo en los pagos provisionales (%s).'
         % (N('pm-limite-perdidas'), liga('pm-limite-perdidas'), liga('pm-perdidas-provisionales')),
         'Los intereses netos no deducibles pasan de lo que exceda del <b>%s</b> de la utilidad fiscal ajustada, en 2026, al <b>%s</b> desde 2027 (%s).'
         % (T('intereses-netos-2026'), T('intereses-netos-2027'), liga('intereses-netos-2027')),
         'Además, se deroga el régimen opcional para grupos de sociedades (arts. %s, %s) y hay una deducción inmediata para bienes nuevos de activo fijo adquiridos entre el %s y el %s. %s'
         % (N('grupos-sociedades-derogado'), liga('grupos-sociedades-derogado'), F('deduccion-inmediata-plan-mexico', 'adquiridos_desde'), F('deduccion-inmediata-plan-mexico', 'adquiridos_hasta'),
            html.escape(D('deduccion-inmediata-plan-mexico')['nota']))],
        ['pm-limite-deducciones', 'pm-factor-deducciones', 'pm-limite-perdidas', 'pm-perdidas-provisionales', 'pm-coeficiente-2027', 'intereses-netos-2026', 'intereses-netos-2027',
         'grupos-sociedades-derogado', 'deduccion-inmediata-plan-mexico'],
        ['¿Qué cambia para el RESICO de personas morales en 2027?', '¿Qué no cambia en 2027?'],
        [_ci('pm-limite-deducciones', N('pm-limite-deducciones') + ' millones', 'de ingresos: desde ahí aplican los límites'),
         _ci('intereses-netos-2026', T('intereses-netos-2026'), 'tope de intereses netos en 2026'),
         _ci('intereses-netos-2027', T('intereses-netos-2027'), 'tope de intereses netos desde 2027')],
        pendientes=['rmf-2027', 'lisr-consolidada-2027'], cita_de='pm-limite-deducciones', rige=True)
    t['nocambia'] = _tema(
        'Lo que no cambia en 2027', 'no-cambia',
        r'(que|lo que) no cambia.*(2027|impuestos|fiscal|isr|sat)|sigue igual.*2027|no (se )?(reforma|modifica).*2027|(sube|suben|aumenta|cambia).*(iva|isr|tarifa).*2027|2027.*(sube|suben|aumenta).*(iva|isr|impuestos)|nuevos impuestos.*2027',
        ['<b>Las tarifas del ISR no se reforman.</b> %s %s' % (html.escape(_e(D('sin-cambio-tarifas-isr')['operacion'])), chip('sin-cambio-tarifas-isr')),
         html.escape(D('sin-cambio-tarifas-isr')['nota']),
         '<b>El IVA general sigue en %s.</b> %s %s' % (T('sin-cambio-iva-general'), html.escape(_e(D('sin-cambio-iva-general')['operacion'])), chip('sin-cambio-iva-general')),
         '<b>La retención de %s en plataformas</b> por enajenación de bienes y prestación de servicios continúa: ya estaba en la Ley de Ingresos de 2026 (%s) y la de 2027 la repite (%s).'
         % (T('sin-cambio-plataformas'), liga('retencion-plataformas-lif'), liga('sin-cambio-plataformas')),
         'Los recargos tampoco se mueven: <b>%s</b> mensual por prórroga y <b>%s</b> por mora, en los dos años.' % (T('recargos-prorroga-2027'), T('recargos-mora-2027'))],
        ['sin-cambio-tarifas-isr', 'sin-cambio-iva-general', 'sin-cambio-plataformas', 'retencion-plataformas-lif', 'recargos-prorroga-2027', 'recargos-mora-2027'],
        ['¿Qué cambia en los impuestos en 2027?', '¿Qué falta por publicar de la reforma 2027?'],
        [_ci('sin-cambio-iva-general', T('sin-cambio-iva-general'), 'tasa general del IVA, sin cambio'),
         _ci('sin-cambio-plataformas', T('sin-cambio-plataformas'), 'retención en plataformas, igual que en 2026'),
         _ci('recargos-mora-2027', T('recargos-mora-2027'), 'recargos mensuales por mora, igual que en 2026')],
        pendientes=['isr-tarifas-2027', 'uma-2027'])
    t['reforma'] = _tema(
        'La reforma fiscal de 2027, en corto', 'cambios',
        r'reforma fiscal|(que|lo que) cambia.*(impuestos|sat|fiscal|isr|resico)|cambios fiscales|novedades fiscales|(isr|impuestos|sat|fiscal).*2027.*(cambi|nuev)|(cambi|nuev).*(isr|impuestos|fiscal).*2027',
        ['El %s entra en vigor el Decreto que reforma la LISR, junto con la Ley de Ingresos de 2027. Lo principal:' % F('decreto-lisr-vigencia'),
         '<ul class="pa-lista">%s</ul>' % ''.join([
             _li('resico-pf-tope-2027', 'RESICO de personas físicas: el tope pasa de <b>%s</b> a <b>%s</b>' % (P('resico-pf-tope-2026'), P('resico-pf-tope-2027'))),
             _li('resico-pm-tope-2027', 'RESICO de personas morales: de <b>%s</b> a <b>%s</b>' % (P('resico-pm-tope-2026'), P('resico-pm-tope-2027'))),
             _li('iva-opcional-resico-7', 'IVA opcional de <b>%s</b> sobre lo cobrado para RESICO, sin acreditamiento' % T('iva-opcional-resico-7')),
             _li('retencion-intereses-2027', 'Retención sobre intereses: de <b>%s</b> a <b>%s</b>' % (T('retencion-intereses-2026'), T('retencion-intereses-2027'))),
             _li('estimulo-regularizacion-100', 'Estímulo del <b>%s</b> de multas, recargos y gastos de ejecución en adeudos de %s o anteriores'
                 % (T('estimulo-regularizacion-100', 'porcentaje'), N('estimulo-regularizacion-100', 'adeudos_hasta_ejercicio').replace(',', ''))),
             _li('pm-limite-deducciones', 'Empresas con más de <b>%s millones</b> de ingresos: límites a deducciones y pérdidas' % N('pm-limite-deducciones')),
             _li('multa-buzon-desde', 'La multa del buzón tributario (de <b>%s</b> a <b>%s</b>) se aplica desde el %s'
                 % (P('multa-buzon-tributario', 'minima'), P('multa-buzon-tributario', 'maxima'), F('multa-buzon-desde')))]),
         'Lo que <b>no</b> cambia: las tarifas del ISR, el IVA general de %s y la retención de %s en plataformas.' % (T('sin-cambio-iva-general'), T('sin-cambio-plataformas'))],
        ['decreto-lisr-vigencia', 'resico-pf-tope-2027', 'resico-pm-tope-2027', 'iva-opcional-resico-7', 'retencion-intereses-2027', 'estimulo-regularizacion-100', 'pm-limite-deducciones',
         'multa-buzon-desde', 'multa-buzon-tributario'],
        ['¿Qué no cambia en 2027?', '¿Qué es el IVA opcional del 7 % para RESICO?', '¿Qué falta por publicar de la reforma 2027?'],
        [_ci('resico-pf-tope-2027', P('resico-pf-tope-2027'), 'tope del RESICO de personas físicas desde 2027'),
         _ci('iva-opcional-resico-7', T('iva-opcional-resico-7'), 'IVA opcional para RESICO'),
         _ci('retencion-intereses-2027', T('retencion-intereses-2027'), 'retención sobre intereses en 2027'),
         _ci('estimulo-regularizacion-100', T('estimulo-regularizacion-100', 'porcentaje'), 'de multas y recargos, no del impuesto')],
        pendientes=['rmf-2027', 'uma-2027', 'isr-tarifas-2027'], rige=True)
    # ---- La anual de 2026 y los sueldos
    t['anual'] = _tema(
        '¿Quién presenta declaración anual por sueldos?', 'calendario',
        r'(quien|quienes|estoy|debo|tengo que|obligad|me toca).*(declaracion anual|la anual|declarar)|declaracion anual.*(asalariad|sueldos?|obligad|quien|cuando|fecha|limite)|(cuando|fecha).*(declaracion anual|la anual)|dos patrones|400 000 .*anual|anual.*400 000',
        ['Si solo tienes sueldo, la presentas en cualquiera de estos casos: cuando ganas más de <b>%s</b> al año, cuando tuviste otros ingresos acumulables, cuando trabajaste para '
         'dos o más patrones a la vez o dejaste de trabajar antes del 31 de diciembre, cuando tus ingresos vienen del extranjero o de quien no está obligado a retener, o cuando '
         'avisaste por escrito a tu patrón que la presentarías.' % P('anual-asalariados-obligados'),
         'La declaración anual de 2026 de las personas físicas vence el <b>%s</b> (%s) y la de las personas morales, el <b>%s</b> (%s). %s'
         % (F('calendario-anual-pf-2026', 'vence'), liga('calendario-anual-pf-2026'), F('calendario-anual-pm-2026', 'vence'), liga('calendario-anual-pm-2026'), chip('calendario-anual-pf-2026')),
         'Los cinco casos están en la fracción III del artículo 98 de la LISR; el monto es solo uno de ellos.'],
        ['anual-asalariados-obligados', 'calendario-anual-pf-2026', 'calendario-anual-pm-2026'],
        ['¿Qué puedo deducir en mi declaración anual?', '¿Cuánto del aguinaldo está exento?', '¿Cuáles son las fechas del calendario fiscal 2027?'],
        [_ci('anual-asalariados-obligados', P('anual-asalariados-obligados'), 'de sueldos al año: desde ahí presentas anual'),
         _ci('calendario-anual-pf-2026', F('calendario-anual-pf-2026', 'vence'), 'vence la anual 2026 de personas físicas'),
         _ci('calendario-anual-pm-2026', F('calendario-anual-pm-2026', 'vence'), 'vence la anual 2026 de personas morales')],
        pendientes=['dias-inhabiles-sat-2027'], cita_de='anual-asalariados-obligados')
    cole = D('colegiaturas')['valor']
    t['deducciones'] = _tema(
        'Deducciones personales: qué entra y hasta cuánto', 'tarifas',
        r'deducciones? personales?|(que|cuanto) puedo deducir|deducir.*(colegiatura|medic|dentista|lentes|funeral|hipotec|donativ|retiro|afore)|(colegiaturas?|gastos? medicos?|gastos? funerarios?|donativos?|intereses hipotecarios).*(deduc|tope|limite)|tope.*deducciones',
        ['Tus deducciones personales tienen un <b>tope global</b>: lo que resulte menor entre %s veces la UMA anual (<b>%s</b> en 2026) y el <b>%s</b> de tus ingresos. %s'
         % (N('tope-deducciones-personales', 'veces_uma_anual'), P('tope-deducciones-personales', 'pesos'), T('tope-deducciones-personales', 'porcentaje_ingresos'), chip('tope-deducciones-personales')),
         '<b>Van aparte del tope:</b> las aportaciones complementarias de retiro (hasta el %s de tus ingresos, sin pasar de <b>%s</b>) y las colegiaturas, que son un estímulo con su propio límite por nivel: '
         'preescolar %s, primaria %s, secundaria %s, profesional técnico %s y bachillerato %s, al año por alumno (%s).'
         % (T('tope-aportaciones-retiro', 'porcentaje_ingresos'), P('tope-aportaciones-retiro', 'pesos'), P('colegiaturas', 'preescolar'), P('colegiaturas', 'primaria'),
            P('colegiaturas', 'secundaria'), P('colegiaturas', 'profesional_tecnico'), P('colegiaturas', 'bachillerato'), liga('colegiaturas')),
         'Otros límites: gastos funerarios hasta <b>%s</b>; donativos hasta el %s de tus ingresos del año anterior (%s si van al gobierno); e intereses reales de créditos hipotecarios de hasta %s UDIS.'
         % (P('tope-gastos-funerales', 'pesos'), T('tope-donativos', 'porcentaje_general'), T('tope-donativos', 'porcentaje_gobierno'), N('tope-intereses-hipotecarios')),
         '<span class="pa-chico">Operación del tope: %s. %s</span>' % (html.escape(_e(D('tope-deducciones-personales')['operacion'])), html.escape(D('exencion-aguinaldo')['nota']))],
        ['tope-deducciones-personales', 'tope-aportaciones-retiro', 'colegiaturas', 'tope-gastos-funerales', 'tope-donativos', 'tope-intereses-hipotecarios', 'uma-2026'],
        ['¿Quién presenta declaración anual?', '¿Cuánto del aguinaldo está exento?'],
        [_ci('tope-deducciones-personales', P('tope-deducciones-personales', 'pesos'), 'tope global en 2026 (o el %s de tus ingresos, lo menor)' % T('tope-deducciones-personales', 'porcentaje_ingresos')),
         _ci('tope-aportaciones-retiro', T('tope-aportaciones-retiro', 'porcentaje_ingresos'), 'de tus ingresos en aportaciones de retiro, aparte del tope'),
         _ci('colegiaturas', P('colegiaturas', 'bachillerato'), 'colegiatura deducible de bachillerato, por alumno')],
        pendientes=['uma-2027'], cita_de='tope-deducciones-personales')
    assert len(cole) == 5
    t['aguinaldo'] = _tema(
        'Aguinaldo, prima vacacional y PTU: cuánto está exento', 'tarifas',
        r'aguinaldo.*(exent|impuesto|isr|grava|retien|libre)|(exent|impuesto|isr).*aguinaldo|prima vacacional|\bptu\b|reparto de utilidades.*(exent|impuesto|isr)|prima dominical',
        ['Del aguinaldo no pagas ISR hasta <b>%s</b> (%s veces la UMA diaria). De la prima vacacional y de la PTU, hasta <b>%s</b> cada una (%s veces). De la prima dominical, <b>%s</b> por cada domingo trabajado. %s'
         % (P('exencion-aguinaldo', 'pesos'), N('exencion-aguinaldo', 'veces_uma'), P('exencion-prima-vacacional', 'pesos'), N('exencion-ptu', 'veces_uma'), P('exencion-prima-dominical', 'pesos'), chip('exencion-aguinaldo')),
         'Por lo que pase de esas cantidades sí se paga el impuesto.',
         '<b>Por qué va como «auditada»:</b> %s La cuenta es nuestra: %s.' % (html.escape(D('exencion-aguinaldo')['nota']), html.escape(_e(D('exencion-aguinaldo')['operacion'])))],
        ['exencion-aguinaldo', 'exencion-prima-vacacional', 'exencion-ptu', 'exencion-prima-dominical', 'uma-2026'],
        ['¿Cuánto es el subsidio para el empleo?', '¿Qué puedo deducir en mi declaración anual?'],
        [_ci('exencion-aguinaldo', P('exencion-aguinaldo', 'pesos'), 'del aguinaldo, exentos en 2026'),
         _ci('exencion-prima-vacacional', P('exencion-prima-vacacional', 'pesos'), 'de la prima vacacional, exentos'),
         _ci('exencion-ptu', P('exencion-ptu', 'pesos'), 'de la PTU, exentos')],
        pendientes=['uma-2027'], cita_de='exencion-aguinaldo',
        nota='Estas cifras valen con la UMA de 2026, que rige hasta el 31 de enero de 2027.')
    t['subsidio'] = _tema(
        'El subsidio para el empleo en 2026', 'tarifas',
        r'subsidio (para|al) (el )?empleo',
        ['En 2026 el subsidio para el empleo es el <b>%s</b> de la UMA mensual: <b>%s</b> al mes, para quien no gana más de <b>%s</b> mensuales. %s'
         % (T('subsidio-empleo-2026', 'porcentaje_uma_mensual'), P('subsidio-empleo-mensual-pesos'), P('subsidio-empleo-2026', 'limite_ingreso_mensual'), chip('subsidio-empleo-mensual-pesos')),
         'En enero de 2026 se usó el %s de la UMA de 2025 (%s).' % (T('subsidio-empleo-enero-2026'), liga('subsidio-empleo-enero-2026')),
         '<span class="pa-chico">Operación: %s. %s</span>' % (html.escape(_e(D('subsidio-empleo-mensual-pesos')['operacion'])), html.escape(_e(D('subsidio-empleo-mensual-pesos')['nota'])))],
        ['subsidio-empleo-2026', 'subsidio-empleo-enero-2026', 'subsidio-empleo-mensual-pesos', 'uma-2026'],
        ['¿Cuánto del aguinaldo está exento?', '¿Quién presenta declaración anual?'],
        [_ci('subsidio-empleo-mensual-pesos', P('subsidio-empleo-mensual-pesos'), 'de subsidio al mes, de febrero de 2026 en adelante'),
         _ci('subsidio-empleo-2026', P('subsidio-empleo-2026', 'limite_ingreso_mensual'), 'de ingreso mensual: hasta ahí aplica')],
        pendientes=['subsidio-empleo-2027', 'uma-2027'], cita_de='subsidio-empleo-2026')
    # ---- Mitos y fiscalización
    t['depositos'] = _tema(
        'Depósitos en efectivo de más de %s: el banco informa, no cobra' % P('depositos-efectivo-informe'), 'fiscalizacion',
        r'deposit\w*.*(efectivo|15 ?000|15 mil|quince mil|sat|impuesto|banco)|impuesto.*(deposit|transferencia)|transferencias?.*(impuesto|sat|15 ?000|15 mil|cobra|reporta|vigila)|15 ?000.*(sat|impuesto|banco|deposit)|\bide\b',
        ['<b>No existe un impuesto a los depósitos de %s.</b> Lo que sí existe es una obligación de los bancos: informar al SAT de los <b>depósitos en efectivo</b> que en el mes sumen más de <b>%s</b> '
         'en todas tus cuentas de una misma institución.' % (P('depositos-efectivo-informe'), P('depositos-efectivo-informe')),
         html.escape(D('depositos-efectivo-informe')['nota']) + ' El artículo solo habla de depósitos en efectivo y de la compra en efectivo de cheques de caja: una transferencia electrónica no es un depósito en efectivo.',
         '<b>Lo que sí conviene cuidar:</b> si lo que gastas en el año es más que lo que declaraste, el SAT puede abrirte un procedimiento de discrepancia fiscal (%s). '
         'Y a quien no está inscrito en el RFC, los depósitos se le presumen ingresos cuando en un ejercicio pasan de %s (%s).'
         % (liga('discrepancia-fiscal'), P('depositos-sin-rfc'), liga('depositos-sin-rfc'))],
        ['depositos-efectivo-informe', 'discrepancia-fiscal', 'depositos-sin-rfc'],
        ['¿Qué es la discrepancia fiscal?', '¿Cuánto es la multa del buzón tributario?'],
        [_ci('depositos-efectivo-informe', P('depositos-efectivo-informe'), 'en efectivo al mes, por banco: desde ahí el banco informa al SAT'),
         _ci('depositos-sin-rfc', P('depositos-sin-rfc'), 'en un ejercicio: presunción para quien no tiene RFC')],
        cita_de='depositos-efectivo-informe')
    t['discrepancia'] = _tema(
        'Discrepancia fiscal: gastar más de lo que declaras', 'fiscalizacion',
        r'discrepancia fiscal|gast\w+ mas de lo que (declar|gan)|tarjeta de credito.*sat|sat.*(tarjeta de credito|mis gastos)',
        ['Hay discrepancia fiscal cuando el SAT comprueba que tus erogaciones de un año son más que los ingresos que declaraste o que debiste declarar.',
         'No es una multa automática ni un impuesto: es un procedimiento, y la ley lo nombra así. El detalle de sus plazos no está todavía en nuestra base, así que no lo afirmamos aquí.'],
        ['discrepancia-fiscal', 'depositos-efectivo-informe'],
        ['¿El SAT cobra impuesto por depósitos de 15 mil pesos?', '¿Cuánto tiempo tengo para un recurso de revocación?'],
        [], cita_de='discrepancia-fiscal')
    t['buzon'] = _tema(
        'Buzón tributario: la multa se aplica desde el %s' % F('multa-buzon-desde'), 'fiscalizacion',
        r'buzon tributario|multa.*buzon|buzon.*(sat|multa|habilit|activar|obligatorio)|medios de contacto.*sat',
        ['El buzón tributario es el sistema de comunicación electrónico del Portal del SAT por el que la autoridad te notifica sus actos (%s). Si recibes un aviso, tienes %s para consultarlo.'
         % (liga('buzon-tributario-que-es'), N('buzon-tributario-que-es') + ' días'),
         'Quien no lo habilita o no mantiene al día sus medios de contacto se expone a una multa de <b>%s a %s</b> (%s), que se aplica desde el <b>%s</b> (%s).'
         % (P('multa-buzon-tributario', 'minima'), P('multa-buzon-tributario', 'maxima'), liga('multa-buzon-tributario'), F('multa-buzon-desde'), liga('multa-buzon-desde')),
         '<b>Quién puede optar por no habilitarlo:</b> los asalariados que en el año anterior ganaron menos de <b>%s</b> (%s).' % (P('buzon-opcion-asalariados'), liga('buzon-opcion-asalariados'))],
        ['buzon-tributario-que-es', 'multa-buzon-tributario', 'multa-buzon-desde', 'buzon-opcion-asalariados'],
        ['¿Quién presenta declaración anual?', '¿Qué es la restricción de sellos digitales?'],
        [_ci('multa-buzon-tributario', P('multa-buzon-tributario', 'minima'), 'multa mínima'),
         _ci('multa-buzon-tributario', P('multa-buzon-tributario', 'maxima'), 'multa máxima'),
         _ci('multa-buzon-desde', F('multa-buzon-desde'), 'desde cuándo se aplica')],
        pendientes=['buzon-excepcion-resico', 'rmf-2027'], cita_de=['multa-buzon-tributario', 'buzon-opcion-asalariados'])
    t['visita49'] = _tema(
        'La visita por comprobantes presuntamente falsos (art. 49 Bis del CFF)', 'fiscalizacion',
        r'49 bis|visita (domiciliaria )?.*(cfdi|factur|comprobantes?) fals|(facturas?|cfdi|comprobantes?) fals\w+.*(visita|sat|procedimiento)|visita domiciliaria',
        ['Cuando el SAT presume que los comprobantes que emite un contribuyente son falsos, puede hacerle una visita domiciliaria con reglas propias. El procedimiento completo dura como máximo <b>%s días hábiles</b> (%s).'
         % (N('visita-cfdi-falsos-plazo'), liga('visita-cfdi-falsos-plazo')),
         'Desde que se entrega o se notifica la orden, se suspende la emisión de comprobantes del visitado, y la suspensión sigue hasta que se resuelva (%s).' % liga('visita-cfdi-falsos-suspension'),
         html.escape(_base()['D']['visita-cfdi-falsos-plazo'].get('nota') or 'Una visita es un procedimiento de revisión: no es una sanción ni prueba que los comprobantes sean falsos.')],
        ['visita-cfdi-falsos-plazo', 'visita-cfdi-falsos-suspension'],
        ['¿Qué plazo tengo si mi proveedor cae en la lista 69-B?', '¿Qué es la restricción de sellos digitales?'],
        [_ci('visita-cfdi-falsos-plazo', N('visita-cfdi-falsos-plazo') + ' días hábiles', 'plazo máximo del procedimiento')],
        pendientes=['visita-cfdi-falsos-pruebas'], cita_de=['visita-cfdi-falsos-suspension'])
    t['plazo69b'] = _tema(
        'Lista 69-B: el plazo de quien recibió las facturas', 'fiscalizacion',
        r'(plazo|cuanto tiempo|cuantos dias|que hago|que pasa).*(69 ?b|efos|lista negra)|(69 ?b|lista negra).*(plazo|cuantos dias|cuanto tiempo|recibi|deduj|que hago|corregir)|mi proveedor.*(cayo|aparec|salio).*(69|lista)',
        ['Si le diste efectos fiscales a comprobantes de un contribuyente que quedó en el listado definitivo del artículo 69-B, tienes <b>%s días</b> desde la publicación para acreditar ante el SAT '
         'que sí recibiste los bienes o los servicios, o para corregir tu situación fiscal con una declaración complementaria (%s).' % (N('lista-69b-receptor'), liga('lista-69b-receptor')),
         'Aparecer junto a un proveedor de esa lista es una señal para revisar, nunca una acusación. Para saber si un RFC está en ella, pregúntame por la «lista negra del SAT» con el RFC.'],
        ['lista-69b-receptor'],
        ['¿Mi proveedor está en la lista negra del SAT?', '¿Qué es la visita del artículo 49 Bis?'],
        [_ci('lista-69b-receptor', N('lista-69b-receptor') + ' días', 'para acreditar la operación o corregir')],
        cita_de='lista-69b-receptor')
    t['sellos'] = _tema(
        'Restricción temporal de sellos digitales (art. 17-H Bis)', 'fiscalizacion',
        r'17 ?h bis|restric\w+.*(sellos?|csd|certificado)|(sellos?|csd).*(restring|bloque|cancel|suspend)|me (quitaron|bloquearon|restringieron) (los |el )?(sellos?|csd)|no puedo facturar',
        ['Antes de dejar sin efectos tus sellos digitales, el SAT puede restringir temporalmente su uso. Si te pasa, tienes <b>%s días hábiles</b> para presentar la solicitud de aclaración (%s).'
         % (N('csd-restriccion-aclaracion'), liga('csd-restriccion-aclaracion')),
         'La restricción es temporal y va antes de dejar los sellos sin efectos: la aclaración sirve para subsanar las irregularidades que el SAT detectó.'],
        ['csd-restriccion-aclaracion'],
        ['¿Cuánto es la multa del buzón tributario?', '¿Qué es la visita del artículo 49 Bis?'],
        [_ci('csd-restriccion-aclaracion', N('csd-restriccion-aclaracion') + ' días hábiles', 'para pedir la aclaración')],
        cita_de='csd-restriccion-aclaracion')
    t['plataformas'] = _tema(
        'Plataformas digitales: cuánto te retienen', 'tarifas',
        r'plataformas? (digital|tecnolog)|(uber|didi|rappi|airbnb|mercado libre|amazon|apps?).*(retien|retencion|impuesto|isr|sat)|(retien|retencion).*(plataforma|app|uber|didi|rappi|airbnb)|2 5 (por ciento|%).*plataforma|vendo por internet',
        ['La LISR fija la retención del ISR por tipo de actividad: <b>%s</b> en transporte de pasajeros y entrega de bienes, <b>%s</b> en hospedaje y <b>%s</b> en enajenación de bienes y prestación de servicios (%s).'
         % (T('retencion-plataformas-ley', 'transporte_y_entrega'), T('retencion-plataformas-ley', 'hospedaje'), T('retencion-plataformas-ley', 'enajenacion_y_servicios'), liga('retencion-plataformas-ley')),
         '<b>Pero ojo:</b> para enajenación y servicios, la Ley de Ingresos sustituye esa tasa por <b>%s</b>. No es una novedad de 2027: ya estaba en la de 2026 (%s) y la de 2027 la repite (%s).'
         % (T('retencion-plataformas-lif'), liga('retencion-plataformas-lif'), liga('sin-cambio-plataformas')),
         'A quien no le da su RFC a la plataforma se le retiene <b>%s</b> (%s). Y la relación laboral con una plataforma no cambia el tratamiento fiscal (%s).'
         % (T('retencion-plataformas-sin-rfc'), liga('retencion-plataformas-sin-rfc'), liga('plataformas-relacion-laboral'))],
        ['retencion-plataformas-ley', 'retencion-plataformas-lif', 'sin-cambio-plataformas', 'retencion-plataformas-sin-rfc', 'plataformas-relacion-laboral'],
        ['¿Qué no cambia en 2027?', '¿Cuál es el tope del RESICO en 2027?'],
        [_ci('retencion-plataformas-lif', T('retencion-plataformas-lif'), 'en enajenación y servicios, en 2026 y en 2027'),
         _ci('retencion-plataformas-ley', T('retencion-plataformas-ley', 'transporte_y_entrega'), 'en transporte y entrega'),
         _ci('retencion-plataformas-ley', T('retencion-plataformas-ley', 'hospedaje'), 'en hospedaje'),
         _ci('retencion-plataformas-sin-rfc', T('retencion-plataformas-sin-rfc'), 'si no das tu RFC')],
        cita_de='sin-cambio-plataformas')
    t['arrendamiento'] = _tema(
        'Arrendamiento: la deducción ciega del %s' % T('deduccion-ciega-arrendamiento'), 'tarifas',
        r'deduccion ciega|(rento|renta|arrend\w+|alquil\w+).*(deduc|35|impuesto|isr|retien|retencion)|35 (por ciento|%).*(renta|arrend)',
        ['Si rentas un inmueble, puedes deducir tus gastos uno por uno o, sin comprobantes, optar por deducir el <b>%s</b> de tus ingresos: la «deducción ciega», en sustitución de las demás deducciones.'
         % T('deduccion-ciega-arrendamiento'),
         'Cuando quien te paga la renta es una persona moral, te retiene el <b>%s</b> del pago como ISR (%s).' % (T('retencion-arrendamiento'), liga('retencion-arrendamiento'))],
        ['deduccion-ciega-arrendamiento', 'retencion-arrendamiento'],
        ['¿Cuánto pago de predial?', '¿Qué puedo deducir en mi declaración anual?'],
        [_ci('deduccion-ciega-arrendamiento', T('deduccion-ciega-arrendamiento'), 'de tus ingresos por rentas, sin comprobantes'),
         _ci('retencion-arrendamiento', T('retencion-arrendamiento'), 'te retiene una persona moral')],
        cita_de='deduccion-ciega-arrendamiento')
    t['recargos'] = _tema(
        'Recargos del SAT en 2026 y 2027', 'fiscalizacion',
        r'recargos?.*(sat|2026|2027|tasa|cuanto|mora|prorroga|parcialidades|plazos)|tasa de recargos|pago a plazos.*sat|parcialidades.*sat',
        ['Los recargos por prórroga son de <b>%s</b> mensual sobre saldos insolutos, y por mora, de <b>%s</b> mensual. Son los mismos en 2026 y en 2027. %s'
         % (T('recargos-prorroga-2027'), T('recargos-mora-2027'), chip('recargos-mora-2027')),
         'En pagos a plazos de 2027: <b>%s</b> hasta 12 meses, <b>%s</b> de 12 a 24 meses y <b>%s</b> a más de 24 meses o en pago diferido (%s).'
         % (T('recargos-parcialidades-2027', 'hasta_12_meses'), T('recargos-parcialidades-2027', 'de_12_a_24_meses'), T('recargos-parcialidades-2027', 'mas_de_24_meses_o_diferido'), liga('recargos-parcialidades-2027')),
         'Si te corriges durante una auditoría, la multa formal se reduce: pagas el %s antes del acta final y el %s después (%s).'
         % (T('reduccion-multas-auditoria', 'antes_del_acta_final_paga'), T('reduccion-multas-auditoria', 'despues_paga'), liga('reduccion-multas-auditoria')),
         '<span class="pa-chico">Operación de la mora: %s.</span>' % html.escape(_e(D('recargos-mora-2027')['operacion']))],
        ['recargos-prorroga-2026', 'recargos-mora-2026', 'recargos-prorroga-2027', 'recargos-mora-2027', 'recargos-parcialidades-2027', 'reduccion-multas-auditoria'],
        ['¿Qué perdona el estímulo de regularización de 2027?', '¿Cuánto tiempo tengo para un recurso de revocación?'],
        [_ci('recargos-prorroga-2027', T('recargos-prorroga-2027'), 'mensual por prórroga'),
         _ci('recargos-mora-2027', T('recargos-mora-2027'), 'mensual por mora')],
        pendientes=['multas-anexo-5-arts-82-84'], cita_de='recargos-prorroga-2027')
    t['caducidad'] = _tema(
        'Caducidad: cuántos años tiene el SAT para revisarte', 'fiscalizacion',
        r'(cuantos anos|cuanto tiempo|plazo|hasta cuando).*(sat|hacienda|fisco).*(revis|audit|cobrar|determinar|fiscaliz)|caducidad.*(sat|fiscal|facultades)|facultades de comprobacion.*(plazo|caduc)|(sat|hacienda).*(revisarme|auditarme).*(anos|tiempo)',
        ['Las facultades del SAT para determinar contribuciones omitidas y para imponer sanciones se extinguen en <b>%s años</b>, contados desde el día siguiente a aquel en que presentaste la declaración del ejercicio.'
         % N('caducidad-facultades', 'anios'),
         '<b>El plazo sube a %s años</b> en tres casos. %s' % (N('caducidad-facultades', 'anios_ampliado'), html.escape(D('caducidad-facultades')['nota'])),
         'Por eso perder los papeles sale caro: puede duplicar el tiempo en que te pueden revisar. Cuánto guardar cada documento está en el calendario de conservación del Inspector.'],
        ['caducidad-facultades'],
        ['¿Cuánto tiempo guardo mis facturas?', '¿Cuánto tiempo tengo para un recurso de revocación?'],
        [_ci('caducidad-facultades', N('caducidad-facultades', 'anios') + ' años', 'plazo general de caducidad'),
         _ci('caducidad-facultades', N('caducidad-facultades', 'anios_ampliado') + ' años', 'sin RFC, sin contabilidad o sin declaración')],
        cita_de='caducidad-facultades')
    t['defensa'] = _tema(
        'Medios de defensa: plazos', 'fiscalizacion',
        r'recurso de revocacion|acuerdos? conclusivos?|(plazo|cuanto tiempo|cuantos dias|demanda).*(tfja|tribunal federal de justicia administrativa|juicio (de nulidad|contencioso))|(como|plazo).*(impugn|defend).*(sat|multa|credito fiscal)',
        ['Contra una resolución del SAT tienes <b>%s días</b> para el recurso de revocación (%s). %s'
         % (N('recurso-revocacion-plazo'), liga('recurso-revocacion-plazo'), html.escape(D('recurso-revocacion-plazo')['nota'])),
         'La demanda ante el Tribunal Federal de Justicia Administrativa también se presenta dentro de <b>%s días</b> (%s).' % (N('juicio-tfja-plazo'), liga('juicio-tfja-plazo')),
         'Y durante una auditoría puedes pedir un acuerdo conclusivo ante la PRODECON (%s).' % liga('acuerdos-conclusivos')],
        ['recurso-revocacion-plazo', 'juicio-tfja-plazo', 'acuerdos-conclusivos'],
        ['¿Cuánto son los recargos del SAT?', '¿Qué es la discrepancia fiscal?'],
        [_ci('recurso-revocacion-plazo', N('recurso-revocacion-plazo') + ' días', 'para el recurso de revocación'),
         _ci('juicio-tfja-plazo', N('juicio-tfja-plazo') + ' días', 'para la demanda ante el TFJA')],
        cita_de='recurso-revocacion-plazo')
    cal = D('calendario-dia-17')
    rec = [f for f in cal['fechas'] if f['vence'] != f['dia_17']]
    t['calendario'] = _tema(
        'Calendario fiscal 2027', 'calendario',
        r'calendario fiscal|(fechas?|cuando|dia).*(pago|pagar|declarar|declaracion).*(sat|impuestos|mensual|provisional)|dia 17|sexto digito|dias? inhabiles?.*(2027|sat|fiscal)',
        ['Los pagos mensuales se presentan a más tardar el día 17 del mes siguiente; si cae en sábado, domingo o día inhábil, se recorre al siguiente día hábil (%s). %s'
         % (liga('calendario-dia-17'), chip('calendario-dia-17')),
         'En el periodo de diciembre de 2026 a diciembre de 2027, el 17 se recorre en estos meses: %s.' % ', '.join('<b>%s</b>' % fecha(f['vence']) for f in rec),
         'Las anuales de 2026: personas morales, <b>%s</b>; personas físicas, <b>%s</b>. Del estímulo de regularización: solicitud de créditos firmes, <b>%s</b>; pago, <b>%s</b>.'
         % (F('calendario-anual-pm-2026', 'vence'), F('calendario-anual-pf-2026', 'vence'), F('calendario-estimulo-2027', 'solicitud_creditos_firmes'), F('calendario-estimulo-2027', 'pago_adeudos_2025_o_anteriores')),
         html.escape(cal['nota']) + ' Las fechas son cuenta nuestra con el artículo 12 del CFF.'],
        ['calendario-dia-17', 'dias-inhabiles-2027', 'prorroga-sexto-digito', 'calendario-anual-pm-2026', 'calendario-anual-pf-2026', 'calendario-estimulo-2027'],
        ['¿Quién presenta declaración anual?', '¿Qué falta por publicar de la reforma 2027?'],
        [_ci('calendario-anual-pm-2026', F('calendario-anual-pm-2026', 'vence'), 'anual 2026 de personas morales'),
         _ci('calendario-anual-pf-2026', F('calendario-anual-pf-2026', 'vence'), 'anual 2026 de personas físicas'),
         _ci('calendario-estimulo-2027', F('calendario-estimulo-2027', 'solicitud_creditos_firmes'), 'solicitud del estímulo (créditos firmes)')],
        pendientes=['dias-inhabiles-sat-2027', 'cancelacion-cfdi-2026'])
    P_TODOS = [i for i, d in _base()['D'].items() if d['estado'] == 'pendiente']
    t['pendientes'] = _tema(
        'Lo que falta por publicar para 2027', 'pendientes',
        r'(\buma\b|salario minimo|tarifas? del isr|subsidio (para|al) (el )?empleo|miscelanea|\brmf\b|anexo 8).*2027|2027.*(\buma\b|salario minimo|miscelanea|\brmf\b)|falta por publicar|(que|lo que) falta.*publicar|iva.*(8|ocho).*frontera|frontera.*iva|estimulo fronterizo|209 2026|2032821',
        ['Estas piezas de 2027 todavía no están publicadas o no las hemos cotejado. Mientras tanto, <b>no usamos ninguna cifra de 2027 que dependa de ellas</b>: la UMA, el salario mínimo y las tarifas que ves en la plataforma son las de 2026.',
         'UMA vigente: <b>%s</b> diaria (%s). Salario mínimo general vigente: <b>%s</b> diarios (%s).' % (P('uma-2026', 'diaria'), liga('uma-2026'), P('salario-minimo-general-2026'), liga('salario-minimo-general-2026'))],
        ['uma-2026', 'salario-minimo-general-2026'],
        ['¿Qué cambia en los impuestos en 2027?', '¿Qué no cambia en 2027?'],
        [_ci('uma-2026', P('uma-2026', 'diaria'), 'UMA diaria de 2026, vigente hasta el 31 de enero de 2027'),
         _ci('salario-minimo-general-2026', P('salario-minimo-general-2026'), 'salario mínimo general diario de 2026')],
        pendientes=P_TODOS)
    # ---- Ronda 40: las cuentas que hace el simulador (fiscal_simulador.py). «Saber más» abre su módulo.
    t['sim_iva'] = _tema(
        'Simula tu IVA: la opción de %s o el régimen general' % T('iva-opcional-resico-7'), 'cambios',
        r'(simul|calcul|compar|decid|convien|convendr).*iva.*(7|siete|opcional|16|dieciseis)|iva.*(7|siete).*( o | vs | contra | versus ).*(16|dieciseis)|iva.*(16|dieciseis).*( o | vs | contra | versus ).*(7|siete)',
        ['Depende de cuánto IVA acreditas. En el régimen general trasladas <b>%s</b> y restas el IVA de tus gastos; con la opción pagas <b>%s</b> de lo cobrado, definitivo y sin acreditar nada.'
         % (T('sin-cambio-iva-general'), T('iva-opcional-resico-7')),
         'El punto de equilibrio es <b>%s</b> del IVA que trasladas %s: %s.' % (T('iva-opcional-resico-equilibrio'), chip('iva-opcional-resico-equilibrio'), html.escape(_e(D('iva-opcional-resico-equilibrio')['operacion']))),
         'El <b>simulador</b> hace la cuenta con lo que tú cobras y gastas, en tu navegador y sin guardar nada.'],
        ['iva-opcional-resico-7', 'sin-cambio-iva-general', 'iva-opcional-resico-equilibrio', 'iva-opcional-resico-sin-acreditamiento'],
        ['¿Qué es el IVA opcional del 7 % para RESICO?', '¿Qué régimen fiscal me conviene?'],
        [_ci('iva-opcional-resico-7', T('iva-opcional-resico-7'), 'IVA opcional para RESICO, definitivo'),
         _ci('iva-opcional-resico-equilibrio', T('iva-opcional-resico-equilibrio'), 'del IVA trasladado: el punto de equilibrio')],
        pendientes=['rmf-2027'], cita_de='iva-opcional-resico-sin-acreditamiento', rige=True, nota=html.escape(D('iva-opcional-resico-equilibrio')['nota']), sim='resico')
    t['sim_anual'] = _tema(
        'Simula tu declaración anual de 2026', 'tarifas',
        r'(simul|calcul|estim).*(declaracion anual|isr anual|mi anual|la anual|saldo a favor)|saldo a (favor|cargo)|cuanto (me (regresan|devuelven|devolveran)|(voy a )?pag(o|ar|aria)|me sale).*(declaracion anual|la anual|isr anual)|(calcul|cuanto es).*isr (anual|del ano)',
        ['Tu ISR del año sale de la tarifa anual (%s) sobre tu ingreso menos tus deducciones personales; si te retuvieron más que eso, tienes saldo a favor, y si menos, saldo a cargo.'
         % liga('isr-tarifa-anual-2026'),
         'Tus deducciones tienen un tope global: lo menor entre %s veces la UMA anual (<b>%s</b>) y el <b>%s</b> de tus ingresos. Las aportaciones de retiro y las colegiaturas van aparte.'
         % (N('tope-deducciones-personales', 'veces_uma_anual'), P('tope-deducciones-personales', 'pesos'), T('tope-deducciones-personales', 'porcentaje_ingresos')),
         'El <b>simulador</b> hace la cuenta con tus números y te dice si estás obligado a presentarla. La anual de 2026 de personas físicas vence el <b>%s</b>.' % F('calendario-anual-pf-2026', 'vence')],
        ['isr-tarifa-anual-2026', 'tope-deducciones-personales', 'tope-aportaciones-retiro', 'colegiaturas-fuera-del-tope', 'anual-asalariados-obligados', 'calendario-anual-pf-2026'],
        ['¿Quién presenta declaración anual?', '¿Qué puedo deducir en mi declaración anual?'],
        [_ci('tope-deducciones-personales', P('tope-deducciones-personales', 'pesos'), 'tope global de deducciones en 2026 (o el %s de tus ingresos, lo menor)' % T('tope-deducciones-personales', 'porcentaje_ingresos')),
         _ci('calendario-anual-pf-2026', F('calendario-anual-pf-2026', 'vence'), 'vence la anual 2026 de personas físicas')],
        pendientes=['isr-tarifas-2027'], cita_de='tope-deducciones-personales', sim='anual')
    t['sim_reg'] = _tema(
        'Compara regímenes: ¿en cuál pagas menos ISR?', 'tarifas',
        r'(que|cual) regimen (fiscal )?(me )?(conviene|convendria|es mejor|elijo|elegir)|compar\w*.*regimen|(resico|simplificado de confianza).*( o | vs | contra | versus ).*(actividad empresarial|honorarios|servicios profesionales|regimen general|arrendamiento|sueldos)|(convien|convendr).*(resico|simplificado de confianza)|resico.*(me conviene|sale mejor)',
        ['No hay una respuesta única: depende de tus ingresos y de tus gastos. En el RESICO pagas una tasa sobre todo lo cobrado, sin deducciones (%s); en actividad empresarial o servicios profesionales, la tarifa anual sobre tu utilidad (%s).'
         % (liga('resico-pf-sin-deducciones'), liga('isr-utilidad-actividades')),
         'En arrendamiento puedes deducir el <b>%s</b> de tus ingresos sin comprobantes (%s), y en plataformas la retención puede ser pago definitivo si tus ingresos del año anterior no pasaron de <b>%s</b> (%s).'
         % (T('deduccion-ciega-arrendamiento'), liga('deduccion-ciega-arrendamiento'), P('plataformas-pago-definitivo'), liga('plataformas-pago-definitivo')),
         'El <b>simulador</b> pone los regímenes lado a lado con tus números. Antes revisa los candados del RESICO: %s' % html.escape(D('resico-pf-exclusiones')['nota'])],
        ['resico-pf-sin-deducciones', 'isr-utilidad-actividades', 'deduccion-ciega-arrendamiento', 'plataformas-pago-definitivo', 'resico-pf-exclusiones', 'resico-pf-tope-2026', 'resico-pf-tope-2027'],
        ['¿Cuál es el tope del RESICO en 2027?', '¿Me conviene el IVA del 7 % o el del 16 %?'],
        [_ci('resico-pf-tope-2026', P('resico-pf-tope-2026'), 'tope del RESICO de personas físicas en 2026'),
         _ci('deduccion-ciega-arrendamiento', T('deduccion-ciega-arrendamiento'), 'deducción opcional sin comprobantes en arrendamiento'),
         _ci('plataformas-pago-definitivo', P('plataformas-pago-definitivo'), 'ingresos del año anterior para el pago definitivo en plataformas')],
        pendientes=['resico-plataformas', 'isr-tarifas-2027'], cita_de='resico-pf-exclusiones', sim='regimenes')
    t['sim_blindaje'] = _tema(
        'Tu lista de blindaje ante el SAT para 2027', 'fiscalizacion',
        r'blindaje|blindar\w*|checklist.*(sat|fiscal)|simulador fiscal|simulador.*(2027|impuestos|del sat|resico)|como me preparo.*(sat|2027)|(que debo|que tengo que) tener (en orden|al dia|listo).*(sat|fiscal|2027)',
        ['Ocho puntos para llegar en orden a 2027, cada uno con su artículo: buzón tributario, proveedores contra la lista 69-B, visitas por comprobantes, pagos mensuales del RESICO, el aviso del IVA opcional, el estímulo de regularización, depósitos en efectivo y la declaración anual.',
         'Dos fechas para empezar: la multa del buzón tributario (de <b>%s</b> a <b>%s</b>) se aplica desde el <b>%s</b>, y la anual de 2026 de personas físicas vence el <b>%s</b>.'
         % (P('multa-buzon-tributario', 'minima'), P('multa-buzon-tributario', 'maxima'), F('multa-buzon-desde'), F('calendario-anual-pf-2026', 'vence')),
         'En el <b>simulador</b> marcas lo que ya resolviste; la lista vive solo en tu navegador y nunca guarda montos.'],
        ['multa-buzon-tributario', 'multa-buzon-desde', 'lista-69b-receptor', 'visita-cfdi-falsos-plazo', 'resico-salida-por-omision', 'iva-opcional-resico-aviso', 'estimulo-regularizacion-100',
         'depositos-efectivo-informe', 'calendario-anual-pf-2026'],
        ['¿Cuáles son las fechas del calendario fiscal 2027?', '¿Qué cambia en los impuestos en 2027?'],
        [_ci('multa-buzon-tributario', P('multa-buzon-tributario', 'maxima'), 'multa máxima por no habilitar el buzón tributario'),
         _ci('multa-buzon-desde', F('multa-buzon-desde'), 'desde cuándo se aplica esa multa')],
        pendientes=['buzon-excepcion-resico', 'visita-cfdi-falsos-pruebas'], cita_de='multa-buzon-tributario', sim='blindaje')
    return t


# El orden en que el chat prueba los temas: de lo particular a lo general.
ORDEN = ['sim_iva', 'sim_anual', 'sim_reg', 'sim_blindaje', 'iva7', 'resico_pm', 'resico_pf', 'intereses', 'estimulo', 'grandes', 'pendientes', 'nocambia', 'depositos', 'discrepancia', 'buzon', 'visita49', 'plazo69b', 'sellos',
         'plataformas', 'arrendamiento', 'recargos', 'caducidad', 'defensa', 'aguinaldo', 'subsidio', 'deducciones', 'anual', 'calendario', 'reforma']


def chat():
    """D.fis del chat."""
    t = temas()
    assert sorted(t) == sorted(ORDEN), set(t) ^ set(ORDEN)
    # `no`: lo que es de otro módulo (el predial y los cobros municipales tienen su simulador y sus leyes).
    return {'t': t, 'orden': ORDEN, 'no': r'predial|catastr|tenencia|municip|ayuntamiento', 'corte': fecha(_base()['corte'])}


# ---------------------------------------------------------------- el Registro de pendientes
def pendientes():
    out = []
    for i, d in _base()['D'].items():
        if d['estado'] != 'pendiente':
            continue
        nuestra = d['quien'].startswith('Auditavisión')
        out.append({'id': PRE + i, 'tema': 'Ingresos', 'que': d['concepto'], 'porque': d['motivo'],
                    'responsable': 'Falta de la plataforma: el documento existe y aún no lo cotejamos' if nuestra else d['quien'], 'enlace': d['url'], 'enlace_txt': 'Dónde debe estar (%s)' % re.sub(r'^https://([^/]+)/.*$', r'\1', d['url']),
                    'aparece': [(ARCHIVO + '#pendientes', TITULO), (SIMULADOR + '#blindaje', SIM_TITULO), ('herramienta-inspector-pregunta.html', 'Pregúntale al Auditor')]})
    return out


# ---------------------------------------------------------------- la página del Planisferio
def _tabla(caption, cols, filas):
    th = ''.join('<th scope="col">%s</th>' % c for c in cols)
    tb = ''.join('<tr><th scope="row">%s</th>%s</tr>' % (f[0], ''.join('<td>%s</td>' % x for x in f[1:])) for f in filas)
    return '<div class="leg-tabla-caja"><table class="leg-tabla fis-tabla"><caption>%s</caption><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (caption, th, tb)


def _fund(i):
    return ' · '.join(liga(i, n) for n in range(len(D(i)['citas'])))


def _fila(i, nombre=None):
    d = D(i)
    return (html.escape(nombre or d['concepto']), '<b>%s</b>%s' % (html.escape(_valor_txt(i)), (' <span class="fis-uni">%s</span>' % html.escape(d['unidad'])) if d.get('unidad') else ''),
            chip(i), _fund(i))


def _par(nombre, a, b, fmt):
    return (html.escape(nombre), '<b>%s</b> %s' % (fmt(a), chip(a)), '<b>%s</b> %s' % (fmt(b), chip(b)), _fund(a) + ' · ' + _fund(b))


def _tarifa(i, isr):
    d = D(i)
    if isr:
        filas = [('$' + _e(_num(f['inferior'], 2)), _e('$' + _num(f['superior'], 2)) if f['superior'] is not None else 'En adelante', _e('$' + _num(f['cuota'], 2)), _e(_num(f['tasa'], 2)) + ' %') for f in d['tabla']]
        cols = ['Límite inferior', 'Límite superior', 'Cuota fija', 'Tasa sobre el excedente']
    else:
        filas = [('Hasta ' + _e('$' + _num(f['hasta'], 2)), _e(_num(f['tasa'], 2)) + ' %') for f in d['tabla']]
        cols = ['Ingresos cobrados, sin IVA', 'Tasa']
    return _tabla('%s %s · %s' % (html.escape(d['concepto']), chip(i), _fund(i)), cols, filas)


def pagina():
    B = _base()
    corte = fecha(B['corte'])
    cambios = _tabla(
        'Lo que cambia: 2026 frente a 2027 (%s)' % RIGE, ['Concepto', 'En 2026', 'Desde el 1 de enero de 2027', 'Fundamento'],
        [_par('RESICO de personas físicas: tope de ingresos al año', 'resico-pf-tope-2026', 'resico-pf-tope-2027', P),
         _par('RESICO: ingresos exentos del campo y la pesca, al año', 'resico-agro-exencion-2026', 'resico-agro-exencion-2027', P),
         _par('RESICO de personas morales: tope de ingresos al año', 'resico-pm-tope-2026', 'resico-pm-tope-2027', P),
         _par('Retención anual del ISR sobre intereses (sobre el capital)', 'retencion-intereses-2026', 'retencion-intereses-2027', T),
         _par('Intereses netos no deducibles: lo que exceda de este porcentaje de la utilidad fiscal ajustada', 'intereses-netos-2026', 'intereses-netos-2027', T),
         _par('Recargos por prórroga, al mes', 'recargos-prorroga-2026', 'recargos-prorroga-2027', T),
         _par('Recargos por mora, al mes', 'recargos-mora-2026', 'recargos-mora-2027', T)])
    nuevos = ['iva-opcional-resico-7', 'iva-opcional-resico-sin-acreditamiento', 'iva-opcional-resico-aviso', 'iva-opcional-resico-equilibrio', 'estimulo-regularizacion-100',
              'estimulo-regularizacion-90', 'estimulo-regularizacion-solicitud', 'estimulo-regularizacion-exclusiones', 'pm-limite-deducciones', 'pm-factor-deducciones',
              'pm-limite-perdidas', 'pm-perdidas-provisionales', 'pm-coeficiente-2027', 'grupos-sociedades-derogado', 'deduccion-inmediata-plan-mexico', 'repatriacion-capitales',
              'iva-cero-gestion-menstrual', 'plataformas-relacion-laboral', 'resico-pf-salida-2027', 'resico-pf-regreso-2027', 'recargos-parcialidades-2027', 'reduccion-multas-auditoria']
    t_nuevos = _tabla('Lo nuevo de 2027 (%s)' % RIGE, ['Concepto', 'Qué dice', 'Estado', 'Fundamento'], [_fila(i) for i in nuevos])
    notas_n = ''.join('<li><b>%s.</b> %s</li>' % (html.escape(D(i)['concepto']), html.escape(D(i)['nota'])) for i in nuevos + ['resico-pm-tope-2027'] if D(i).get('nota'))
    op = D('iva-opcional-resico-equilibrio')
    no_cambia = ''.join('<li><b>%s</b> %s. %s %s <span class="pa-chico">(%s)</span></li>' % (
        html.escape(D(i)['concepto']), chip(i), html.escape(_e(D(i).get('operacion') or '')), html.escape(D(i).get('nota') or ''), _fund(i))
        for i in ('sin-cambio-tarifas-isr', 'sin-cambio-iva-general', 'sin-cambio-plataformas'))
    topes = ['uma-2026', 'salario-minimo-general-2026', 'salario-minimo-zlfn-2026', 'subsidio-empleo-2026', 'subsidio-empleo-mensual-pesos', 'exencion-aguinaldo', 'exencion-prima-vacacional',
             'exencion-ptu', 'exencion-prima-dominical', 'tope-deducciones-personales', 'tope-aportaciones-retiro', 'tope-gastos-funerales', 'tope-donativos', 'tope-intereses-hipotecarios',
             'colegiaturas', 'colegiaturas-fuera-del-tope', 'anual-asalariados-obligados', 'isr-utilidad-actividades', 'resico-pf-sin-deducciones', 'resico-pf-exclusiones']
    reten = ['retencion-resico-pm', 'retencion-honorarios', 'retencion-arrendamiento', 'deduccion-ciega-arrendamiento', 'retencion-iva-dos-terceras', 'retencion-iva-autotransporte',
             'retencion-plataformas-ley', 'retencion-plataformas-lif', 'retencion-plataformas-sin-rfc', 'plataformas-pago-definitivo']
    ops = ''.join('<li><b>%s:</b> %s. %s</li>' % (html.escape(D(i)['concepto']), html.escape(_e(D(i)['operacion'])), html.escape(D(i).get('nota') or '')) for i in topes if D(i).get('operacion'))
    fisc = ['depositos-efectivo-informe', 'depositos-sin-rfc', 'discrepancia-fiscal', 'buzon-tributario-que-es', 'multa-buzon-tributario', 'multa-buzon-desde', 'buzon-opcion-asalariados',
            'visita-cfdi-falsos-plazo', 'visita-cfdi-falsos-suspension', 'lista-69b-receptor', 'csd-restriccion-aclaracion', 'constancia-situacion-fiscal', 'opinion-cumplimiento-32d',
            'resico-salida-por-omision', 'caducidad-facultades', 'recurso-revocacion-plazo', 'juicio-tfja-plazo', 'acuerdos-conclusivos']
    cal = D('calendario-dia-17')
    per = lambda p: _e('%s de %s' % (MESES[int(p[5:7]) - 1], p[:4]))
    t_cal = _tabla('Pagos mensuales: el día 17, recorrido al siguiente día hábil %s · %s' % (chip('calendario-dia-17'), _fund('calendario-dia-17')),
                   ['Mes en que se paga', 'Día 17', 'Vence', '¿Se recorre?'],
                   [(per(f['periodo_de_pago']), fecha(f['dia_17']), '<b>%s</b>' % fecha(f['vence']), 'Sí' if f['vence'] != f['dia_17'] else 'No') for f in cal['fechas']])
    otras = _tabla('Otras fechas de 2027', ['Qué', 'Fecha', 'Estado', 'Fundamento'], [
        ('Declaración anual 2026 de personas morales', '<b>%s</b>' % F('calendario-anual-pm-2026', 'vence'), chip('calendario-anual-pm-2026'), _fund('calendario-anual-pm-2026')),
        ('Declaración anual 2026 de personas físicas', '<b>%s</b>' % F('calendario-anual-pf-2026', 'vence'), chip('calendario-anual-pf-2026'), _fund('calendario-anual-pf-2026')),
        ('Estímulo de regularización: solicitud de quien tiene créditos firmes', '<b>%s</b>' % F('calendario-estimulo-2027', 'solicitud_creditos_firmes'), chip('calendario-estimulo-2027'), _fund('calendario-estimulo-2027')),
        ('Estímulo de regularización: pago en una sola exhibición', '<b>%s</b>' % F('calendario-estimulo-2027', 'pago_adeudos_2025_o_anteriores'), chip('calendario-estimulo-2027'), _fund('calendario-estimulo-2027')),
        ('Retorno de recursos del extranjero, a más tardar', '<b>%s</b>' % F('repatriacion-capitales', 'retorno_a_mas_tardar'), chip('repatriacion-capitales'), _fund('repatriacion-capitales')),
        ('La multa del buzón tributario se aplica desde', '<b>%s</b>' % F('multa-buzon-desde'), chip('multa-buzon-desde'), _fund('multa-buzon-desde'))])
    inh = D('dias-inhabiles-2027')
    sexto = D('prorroga-sexto-digito')
    ps = _e(sexto['valor']['tabla']).split(' | ')
    t_sexto = _tabla('%s %s · %s' % (html.escape(sexto['concepto']), chip('prorroga-sexto-digito'), _fund('prorroga-sexto-digito')), ['Sexto dígito numérico del RFC', 'Fecha límite'],
                     [(ps[k], ps[k + 1]) for k in range(0, len(ps), 2)])
    pends = [i for i, d in B['D'].items() if d['estado'] == 'pendiente']
    t_pend = _tabla('Lo que falta por publicar o por cotejar', ['Qué falta', 'Por qué', 'Quién lo debe', 'Dónde debe estar'], [
        ('%s %s' % (html.escape(D(i)['concepto']), chip(i)), html.escape(D(i)['motivo']), html.escape(D(i)['quien']),
         '<a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>' % (html.escape(D(i)['url'], quote=True), html.escape(re.sub(r'^https://([^/]+)/.*$', r'\1', D(i)['url'])))) for i in pends])
    usadas = sorted({c['fuente'] for d in B['D'].values() for c in d.get('citas') or []})
    fuentes = ''.join('<li><a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a> · %s</li>' % (html.escape(B['F'][k]['url'], quote=True), html.escape(B['F'][k]['nombre']), html.escape(_e(B['F'][k]['publicacion'])))
                      for k in usadas)
    aud = 'herramienta-inspector-pregunta.html?q=%s'
    secc = [
        {'id': 'cambios', 'salto': 'Qué cambia', 'titulo': 'Qué cambia: 2026 frente a 2027',
         'texto': 'El Decreto que reforma la LISR y la Ley de Ingresos de 2027 se publicaron en el DOF el mismo día. Todo lo de esta sección %s: hasta el 31 de diciembre de 2026 valen las cifras de 2026.' % RIGE,
         'tarjetas': [], 'bloque': '<p><a class="apartado-boton" href="%s">Simular mi caso 2026–2027</a></p>' % SIMULADOR + cambios + t_nuevos + '<details class="fis-notas"><summary>Las notas de cada cambio</summary><ul>%s</ul></details>' % notas_n +
         '<p class="fis-op"><b>La cuenta del IVA opcional</b> %s: %s. %s</p>' % (chip('iva-opcional-resico-equilibrio'), html.escape(_e(op['operacion'])), html.escape(op['nota'])) +
         _tarifa('resico-pf-mensual-2026', False) + _tarifa('resico-pf-mensual-2027', False) + _tarifa('resico-pf-anual-2026', False) + _tarifa('resico-pf-anual-2027', False)},
        {'id': 'no-cambia', 'salto': 'Qué no cambia', 'titulo': 'Qué no cambia en 2027', 'texto': 'Tan importante como lo nuevo: lo que la reforma no tocó.',
         'tarjetas': [], 'bloque': '<ul class="fis-lista">%s</ul>' % no_cambia},
        {'id': 'tarifas', 'salto': 'Tarifas y topes', 'titulo': 'Tarifas, topes y retenciones vigentes en 2026',
         'texto': 'Las cifras con las que se calcula hoy. Las que dependen de la UMA valen hasta el 31 de enero de 2027; las de 2027 siguen pendientes.',
         'tarjetas': [], 'bloque': _tabla('Unidades, exenciones y deducciones personales', ['Concepto', 'Valor', 'Estado', 'Fundamento'], [_fila(i) for i in topes]) +
         '<details class="fis-notas"><summary>Cómo se calculó cada cifra auditada</summary><ul>%s</ul></details>' % ops +
         _tabla('Retenciones', ['Concepto', 'Valor', 'Estado', 'Fundamento'], [_fila(i) for i in reten]) +
         _tarifa('isr-tarifa-mensual-2026', True) + _tarifa('isr-tarifa-anual-2026', True)},
        {'id': 'calendario', 'salto': 'Calendario 2027', 'titulo': 'Calendario fiscal 2027',
         'texto': 'Las fechas se calculan con el artículo 12 del CFF: si el plazo vence en día inhábil, se recorre al siguiente hábil. %s' % html.escape(cal['nota']),
         'tarjetas': [], 'bloque': t_cal + otras + t_sexto + '<p class="pa-chico">%s</p>' % html.escape(sexto['nota']) +
         '<p><b>Días inhábiles de 2027</b> %s (%s): %s. %s</p>' % (chip('dias-inhabiles-2027'), _fund('dias-inhabiles-2027'), ', '.join(fecha(x) for x in inh['valor']['fechas']), html.escape(inh['nota']))},
        {'id': 'fiscalizacion', 'salto': 'Fiscalización', 'titulo': 'Fiscalización, multas y medios de defensa',
         'texto': html.escape(fb.carga('fiscalizacion-y-plazos.json')['nota']),
         'tarjetas': [], 'bloque': _tabla('Plazos y cifras de fiscalización', ['Concepto', 'Qué dice', 'Estado', 'Fundamento'], [_fila(i) for i in fisc]) +
         _tabla('Recargos', ['Concepto', 'Valor', 'Estado', 'Fundamento'], [_fila(i) for i in ('recargos-prorroga-2026', 'recargos-mora-2026', 'recargos-prorroga-2027', 'recargos-mora-2027')])},
        {'id': 'pendientes', 'salto': 'Lo que falta', 'titulo': 'Lo que falta por publicar (pendiente)',
         'texto': 'Nada de esto se da por cerrado. Cada renglón dice por qué falta, quién lo debe y dónde debe aparecer; cuando se publique, entra con su cita.',
         'tarjetas': [], 'bloque': t_pend},
        {'id': 'fuentes', 'salto': 'Fuentes', 'titulo': 'De dónde sale cada dato',
         'texto': 'Cada cifra de esta página lleva su cita textual en la base, y un validador la busca palabra por palabra en el documento guardado con su huella. Corte: %s.' % corte,
         'tarjetas': [], 'bloque': '<ul class="fis-lista">%s</ul>' % fuentes +
         '<p class="pa-chico">%s Las cifras «auditadas» son cuentas nuestras con datos oficiales, con su operación dicha.</p>' % NO_ASESORIA +
         '<p><a class="apartado-boton" href="%s">Pregúntale al Auditor por tu caso</a></p>' % html.escape(aud % 'Qu%C3%A9%20cambia%20en%202027', quote=True)},
    ]
    return {
        'archivo': ARCHIVO, 'menu': TITULO, 'menu_archivo': 'aprende.html', 'padre': ('aprende.html', 'Aprende'),
        'icono': '🧾', 'titulo': TITULO, 'lema': 'Lo que cambia y lo que no el 1 de enero de 2027, las cifras vigentes y las fechas, con su cita',
        'estilos': ['asistente.css'],
        'entrada': ('La reforma a la Ley del ISR y la Ley de Ingresos de 2027 ya se publicaron en el DOF y rigen desde el 1 de enero de 2027. Aquí está qué cambia, qué no, '
                    'las tarifas y los topes vigentes, el calendario de 2027 y, con su nombre, lo que todavía falta por publicarse. Ninguna cifra está escrita a mano: '
                    'cada una se lee de la base fiscal, con su artículo y su cita.'),
        'secciones': secc}


# ---------------------------------------------------------------- el Noticiero: cuatro verificaciones
def _f(k):
    f = _base()['F'][k]
    return {'nombre': _e('%s (%s)' % (f['nombre'], f['publicacion'])), 'url': f['url']}


def _cif(i, valor, etq, n=0):
    c = D(i)['citas'][n]
    f = _base()['F'][c['fuente']]
    return {'valor': valor, 'etq': etq, 'estado': estado(i), 'fuente': _e('%s, %s' % (f['nombre'], c['articulo'].rstrip('.'))), 'url': f['url']}


def _cot(dice, res, explica, i=None, n=0):
    x = {'dice': dice, 'res': res, 'explica': explica, 'fuente': 'Sin documento oficial', 'url': ''}
    if i:
        d = D(i)
        if d['estado'] == 'pendiente':
            x.update({'fuente': 'Aún sin publicar', 'url': d['url'], 'quien': d['quien'] + ': ' + d['motivo'], 'donde': d['url']})
        else:
            c = d['citas'][n]
            f = _base()['F'][c['fuente']]
            x.update({'fuente': _e('%s, %s' % (f['nombre'], c['articulo'].rstrip('.'))), 'url': f['url']})
    return x


def columnas():
    corte = fecha(_base()['corte'])
    cir = lambda tx: {'red': 'Redes sociales y cadenas de mensajes', 'cuenta': 'Lo que suele decirse (no es una publicación en particular)', 'fecha': 'cotejado al ' + corte, 'texto': tx}
    pag = lambda a, tx: {'que': tx, 'url': ARCHIVO + '#' + a}
    out = []
    out.append({
        'id': 'fiscal-depositos-15-mil', 'seccion': 'Verificado', 'icono': '🏦',
        'titulo': 'No existe un impuesto a los depósitos de %s ni a las transferencias' % P('depositos-efectivo-informe'),
        'balazo': 'Lo que la ley manda es que el banco informe al SAT de los depósitos en efectivo que en el mes pasen de %s. No es un impuesto ni una retención, y la regla no habla de transferencias.' % P('depositos-efectivo-informe'),
        'circula': cir('El SAT te va a cobrar impuesto por cada depósito o transferencia de más de %s.' % P('depositos-efectivo-informe')),
        'cuerpo': [
            'La cifra es real, pero la regla es otra. La Ley del ISR obliga a las instituciones del sistema financiero a informar al SAT de los depósitos en efectivo cuando el acumulado del mes, en todas las cuentas que una persona tiene en una misma institución, pasa de %s.' % P('depositos-efectivo-informe'),
            'La ley lo dice así: «%s» (%s).' % (cita_txt('depositos-efectivo-informe'), A('depositos-efectivo-informe')),
            'Es un aviso del banco, no un cobro: nadie te descuenta nada por depositar. Y el artículo habla de depósitos en efectivo y de la compra en efectivo de cheques de caja; una transferencia electrónica no es un depósito en efectivo.',
            'Lo que sí puede pasar: si en un año gastas más de lo que declaraste, el SAT puede abrir un procedimiento de discrepancia fiscal (%s). Y a quien no está inscrito en el RFC, los depósitos se le presumen ingresos cuando en un ejercicio pasan de %s (%s).'
            % (A('discrepancia-fiscal'), P('depositos-sin-rfc'), A('depositos-sin-rfc')),
            'Nota de método: es una verificación de servicio público sobre un mito frecuente, no sobre una publicación en particular. Las cifras se leen de la base fiscal de la plataforma, con corte al %s.' % corte],
        'dato_curioso': 'El umbral es por institución: el banco suma los depósitos en efectivo de todas tus cuentas con él, no los de otros bancos.',
        'cifras': [_cif('depositos-efectivo-informe', P('depositos-efectivo-informe'), 'Depósitos en efectivo al mes, por institución: desde ahí el banco informa al SAT'),
                   _cif('depositos-sin-rfc', P('depositos-sin-rfc'), 'Depósitos en un ejercicio de quien no está en el RFC: se presumen ingresos')],
        'cotejo': [
            _cot('El SAT cobra un impuesto por los depósitos de más de %s.' % P('depositos-efectivo-informe'), 'no consta',
                 'El artículo establece una obligación de informar para los bancos. No fija tasa, cuota ni retención alguna.', 'depositos-efectivo-informe'),
            _cot('Los bancos reportan al SAT los depósitos en efectivo de más de %s al mes.' % P('depositos-efectivo-informe'), 'consta',
                 'Es el acumulado mensual de depósitos en efectivo en todas las cuentas de una misma institución.', 'depositos-efectivo-informe'),
            _cot('También aplica a las transferencias entre cuentas.', 'no consta',
                 'El artículo solo nombra los depósitos en efectivo y las adquisiciones en efectivo de cheques de caja.', 'depositos-efectivo-informe'),
            _cot('Si gastas más de lo que declaras, el SAT puede revisarte.', 'consta',
                 'Es el procedimiento de discrepancia fiscal: un procedimiento, no un impuesto ni una multa automática.', 'discrepancia-fiscal')],
        'sigue': [pag('fiscalizacion', 'La tabla de fiscalización, con cada plazo y su artículo')],
        'fuentes': [_f('LISR'), _f('anx26')], 'actualizado': corte})
    out.append({
        'id': 'fiscal-plataformas-2-5', 'seccion': 'Verificado', 'icono': '📱',
        'titulo': 'La retención de %s en plataformas digitales no es nueva en 2027: ya estaba en la Ley de Ingresos de 2026' % T('retencion-plataformas-lif'),
        'balazo': 'La Ley del ISR dice %s para quien vende bienes o presta servicios por plataformas; la Ley de Ingresos sustituye esa tasa por %s desde 2026, y la de 2027 lo repite.'
        % (T('retencion-plataformas-ley', 'enajenacion_y_servicios'), T('retencion-plataformas-lif')),
        'circula': cir('En 2027 el SAT va a empezar a cobrar un nuevo impuesto de %s a quienes venden por internet o por aplicaciones.' % T('retencion-plataformas-lif')),
        'cuerpo': [
            'No es un impuesto nuevo y no empieza en 2027. Es una retención del ISR que hace la plataforma, y la tasa de %s para enajenación de bienes y prestación de servicios ya estaba en la Ley de Ingresos de 2026 (%s).'
            % (T('retencion-plataformas-lif'), A('retencion-plataformas-lif')),
            'La Ley de Ingresos de 2027 la repite. Lo dice así: «%s» (%s).' % (cita_txt('sin-cambio-plataformas'), A('sin-cambio-plataformas')),
            'La confusión viene de que la Ley del ISR, en su texto, sigue diciendo %s para esa actividad (%s): la Ley de Ingresos de cada año la sustituye. Las otras dos tasas de la Ley del ISR no cambian: %s en transporte de pasajeros y entrega de bienes, y %s en hospedaje.'
            % (T('retencion-plataformas-ley', 'enajenacion_y_servicios'), A('retencion-plataformas-ley'), T('retencion-plataformas-ley', 'transporte_y_entrega'), T('retencion-plataformas-ley', 'hospedaje')),
            'Quien no le da su RFC a la plataforma sí paga más: la retención es de %s (%s).' % (T('retencion-plataformas-sin-rfc'), A('retencion-plataformas-sin-rfc')),
            'Nota de método: es una verificación de servicio público sobre un mito frecuente, no sobre una publicación en particular. Corte: %s.' % corte],
        'dato_curioso': 'La Ley de Ingresos vale un año: por eso la tasa de %s tiene que repetirse en cada una para seguir aplicando.' % T('retencion-plataformas-lif'),
        'cifras': [_cif('retencion-plataformas-lif', T('retencion-plataformas-lif'), 'Retención en plataformas por enajenación y servicios, en 2026'),
                   _cif('sin-cambio-plataformas', T('sin-cambio-plataformas'), 'La misma retención en 2027'),
                   _cif('retencion-plataformas-ley', T('retencion-plataformas-ley', 'enajenacion_y_servicios'), 'Lo que dice el texto de la Ley del ISR para esa actividad'),
                   _cif('retencion-plataformas-sin-rfc', T('retencion-plataformas-sin-rfc'), 'Retención a quien no da su RFC')],
        'cotejo': [
            _cot('La retención de %s en plataformas es nueva en 2027.' % T('retencion-plataformas-lif'), 'no consta',
                 'Ya estaba en el artículo 25 de la Ley de Ingresos de 2026. La de 2027 la repite.', 'retencion-plataformas-lif'),
            _cot('En 2027 la retención por enajenación y servicios en plataformas es de %s.' % T('sin-cambio-plataformas'), 'consta',
                 'La Ley de Ingresos de 2027 sustituye la tasa de la fracción III del artículo 113-A de la Ley del ISR.', 'sin-cambio-plataformas'),
            _cot('Es un impuesto nuevo.', 'matiz',
                 'Es una retención del ISR que ya existía: lo que la Ley de Ingresos cambia es su tasa para una de las tres actividades.', 'retencion-plataformas-ley')],
        'sigue': [pag('tarifas', 'Todas las retenciones vigentes, con su artículo')],
        'fuentes': [_f('LIF_2026'), _f('LIF_2027'), _f('LISR')], 'actualizado': corte})
    out.append({
        'id': 'fiscal-estimulo-2027', 'seccion': 'Verificado', 'icono': '🧾',
        'titulo': 'El estímulo del %s en 2027 perdona multas y recargos, no el impuesto' % T('estimulo-regularizacion-100', 'porcentaje'),
        'balazo': 'La Ley de Ingresos de 2027 da un estímulo sobre multas, recargos y gastos de ejecución de adeudos de %s o anteriores. El impuesto se paga completo, y hay fechas y exclusiones.'
        % N('estimulo-regularizacion-100', 'adeudos_hasta_ejercicio').replace(',', ''),
        'circula': cir('En 2027 el SAT va a perdonar el %s de las deudas fiscales.' % T('estimulo-regularizacion-100', 'porcentaje')),
        'cuerpo': [
            'El %s es real, pero no es de la deuda completa. El estímulo es sobre lo accesorio: multas, recargos y gastos de ejecución. La contribución que se dejó de pagar se cubre entera.' % T('estimulo-regularizacion-100', 'porcentaje'),
            'La ley lo dice así: «%s» (%s).' % (cita_txt('estimulo-regularizacion-100'), A('estimulo-regularizacion-100')),
            'Tiene condiciones: los adeudos deben ser del ejercicio %s o anteriores, hay que presentar las declaraciones y pagar en una sola exhibición a más tardar el %s. Quien tiene créditos fiscales firmes debe presentar su solicitud a más tardar el %s.'
            % (N('estimulo-regularizacion-100', 'adeudos_hasta_ejercicio').replace(',', ''), F('estimulo-regularizacion-100', 'pago_a_mas_tardar'), F('estimulo-regularizacion-solicitud')),
            'Cuando el crédito firme es solo de multas por obligaciones distintas de las de pago, el estímulo es de %s (%s). Y no aplica a quien no desvirtuó los procedimientos de los artículos %s del CFF.'
            % (T('estimulo-regularizacion-90'), A('estimulo-regularizacion-90'), N('estimulo-regularizacion-exclusiones')),
            'Lo que falta: las reglas del SAT con el formato y el trámite. Vienen en la Resolución Miscelánea Fiscal para 2027, que todavía no se publica.',
            'Nota de método: es una verificación de servicio público sobre un mito frecuente, no sobre una publicación en particular. Corte: %s.' % corte],
        'dato_curioso': 'El estímulo %s: no se puede pedir antes.' % RIGE,
        'cifras': [_cif('estimulo-regularizacion-100', T('estimulo-regularizacion-100', 'porcentaje'), 'De multas, recargos y gastos de ejecución; no del impuesto'),
                   _cif('estimulo-regularizacion-90', T('estimulo-regularizacion-90'), 'Cuando el crédito firme es solo de multas formales'),
                   _cif('estimulo-regularizacion-solicitud', F('estimulo-regularizacion-solicitud'), 'Solicitud de quien tiene créditos fiscales firmes'),
                   _cif('estimulo-regularizacion-100', F('estimulo-regularizacion-100', 'pago_a_mas_tardar'), 'Pago en una sola exhibición, a más tardar')],
        'cotejo': [
            _cot('El SAT perdonará el %s de las deudas fiscales en 2027.' % T('estimulo-regularizacion-100', 'porcentaje'), 'matiz',
                 'El estímulo es del total de multas, recargos y gastos de ejecución. El impuesto omitido no entra.', 'estimulo-regularizacion-100'),
            _cot('Aplica a adeudos de %s o anteriores.' % N('estimulo-regularizacion-100', 'adeudos_hasta_ejercicio').replace(',', ''), 'consta',
                 'Con las declaraciones presentadas y el pago en una sola exhibición dentro del plazo.', 'estimulo-regularizacion-100'),
            _cot('Cualquier contribuyente puede acogerse.', 'matiz',
                 'Quedan fuera quienes no desvirtuaron los procedimientos de los artículos %s del CFF.' % N('estimulo-regularizacion-exclusiones'), 'estimulo-regularizacion-exclusiones'),
            _cot('Ya se conoce el trámite para pedirlo.', 'pendiente',
                 'El formato y los requisitos los fijará el SAT en reglas de carácter general.', 'rmf-2027')],
        'sigue': [{'que': 'La Resolución Miscelánea Fiscal para 2027, con el trámite del estímulo', 'url': D('rmf-2027')['url']},
                  pag('calendario', 'Las fechas del estímulo en el calendario fiscal de 2027')],
        'fuentes': [_f('LIF_2027'), _f('CFF')], 'actualizado': corte})
    out.append({
        'id': 'fiscal-multa-buzon-2027', 'seccion': 'Verificado', 'icono': '🔔',
        'titulo': 'Multa del buzón tributario desde el %s: de %s a %s, y quién puede optar por no habilitarlo'
        % (F('multa-buzon-desde'), P('multa-buzon-tributario', 'minima'), P('multa-buzon-tributario', 'maxima')),
        'balazo': 'La multa por no habilitar el buzón o no actualizar los medios de contacto está en el CFF; la Resolución Miscelánea de 2026 la aplica desde el %s. Los asalariados de menos de %s al año pueden optar por no habilitarlo.'
        % (F('multa-buzon-desde'), P('buzon-opcion-asalariados')),
        'circula': cir('Desde enero de 2027 el SAT va a multar a todos los que no tengan activo su buzón tributario.'),
        'cuerpo': [
            'La multa existe y tiene fecha. El CFF la fija así: «%s» (%s).' % (cita_txt('multa-buzon-tributario'), A('multa-buzon-tributario')),
            'La Resolución Miscelánea Fiscal para 2026 dice desde cuándo se aplica: el %s (%s).' % (F('multa-buzon-desde'), A('multa-buzon-desde')),
            'Pero no es para todos. La misma Resolución da una opción: «%s» (%s).' % (cita_txt('buzon-opcion-asalariados'), A('buzon-opcion-asalariados')),
            'El buzón es el sistema electrónico del Portal del SAT por el que la autoridad notifica sus actos (%s). Habilitarlo y mantener al día los medios de contacto es lo que evita la multa.' % A('buzon-tributario-que-es'),
            'Lo que no afirmamos: que exista un plazo de gracia para el RESICO. No localizamos la regla que lo diga, así que queda pendiente. Y las reglas de 2027 vendrán en su propia Resolución Miscelánea, aún sin publicar.',
            'Nota de método: es una verificación de servicio público, no sobre una publicación en particular. Corte: %s.' % corte],
        'dato_curioso': 'El umbral de la opción para asalariados (%s) es el mismo monto desde el que un asalariado debe presentar declaración anual (%s).'
        % (P('buzon-opcion-asalariados'), A('anual-asalariados-obligados')),
        'cifras': [_cif('multa-buzon-tributario', P('multa-buzon-tributario', 'minima'), 'Multa mínima'),
                   _cif('multa-buzon-tributario', P('multa-buzon-tributario', 'maxima'), 'Multa máxima'),
                   _cif('multa-buzon-desde', F('multa-buzon-desde'), 'Desde cuándo se aplica'),
                   _cif('buzon-opcion-asalariados', P('buzon-opcion-asalariados'), 'Asalariados con ingresos menores a esta cifra pueden optar por no habilitarlo')],
        'cotejo': [
            _cot('La multa por no habilitar el buzón tributario va de %s a %s.' % (P('multa-buzon-tributario', 'minima'), P('multa-buzon-tributario', 'maxima')), 'consta',
                 'Es el artículo 86-D del CFF.', 'multa-buzon-tributario'),
            _cot('Se aplica desde el %s.' % F('multa-buzon-desde'), 'consta', 'Lo dice un transitorio de la Resolución Miscelánea Fiscal para 2026.', 'multa-buzon-desde'),
            _cot('Multarán a todos los contribuyentes sin buzón.', 'matiz',
                 'Los asalariados con ingresos menores a %s en el ejercicio anterior pueden optar por no habilitarlo.' % P('buzon-opcion-asalariados'), 'buzon-opcion-asalariados'),
            _cot('El RESICO tiene un plazo de gracia para habilitarlo.', 'pendiente', 'No se localizó la regla que lo establezca: no se afirma sin su regla.', 'buzon-excepcion-resico')],
        'sigue': [{'que': 'La Resolución Miscelánea Fiscal para 2027: si mantiene la opción de los asalariados', 'url': D('rmf-2027')['url']},
                  pag('fiscalizacion', 'Los demás plazos de fiscalización, con su artículo')],
        'fuentes': [_f('CFF'), _f('rmf26')], 'actualizado': corte})
    return out


def escribe_columnas():
    """Escribe las cuatro verificaciones en columnas.js, al principio de «Verificado» (el mismo modo de integrar_al_momento.py)."""
    ruta = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'columnas.js')
    raw = open(ruta, 'rb').read().decode('utf-8')
    ancla = ' {\r\n  "id": "%s",'
    primera = raw.index('  "seccion": "Verificado",')
    ini = raw.rindex(' {\r\n  "id": "', 0, primera)
    for n in reversed(columnas()):
        txt = '\r\n'.join(' ' + l for l in json.dumps(n, ensure_ascii=False, indent=1).split('\n')) + ',\r\n'
        marca = ancla % n['id']
        if marca in raw:
            a = raw.index(marca)
            b = raw.index('\r\n },\r\n', a) + len('\r\n },\r\n')
            raw = raw[:a] + txt + raw[b:]
        else:
            raw = raw[:ini] + txt + raw[ini:]
    open(ruta, 'wb').write(raw.encode('utf-8'))
    print('columnas.js: %d verificaciones fiscales' % len(columnas()))


# ---------------------------------------------------------------- la Biblioteca: glosario y marco legal
def _ley(*pares):
    return ' · '.join(A(i, n) for i, n in pares)


def glosario():
    return [
        {'termino': 'Buzón Tributario',
         'definicion': 'El sistema de comunicación electrónico, dentro del Portal del SAT, por el que la autoridad te notifica sus actos y resoluciones. '
                       'Cuando recibes un aviso electrónico tienes %s días para consultarlo. Quien no lo habilita o no mantiene al día sus medios de contacto se expone a una multa de %s a %s, '
                       'que se aplica desde el %s. Los asalariados con ingresos menores a %s en el año anterior pueden optar por no habilitarlo.'
                       % (N('buzon-tributario-que-es'), P('multa-buzon-tributario', 'minima'), P('multa-buzon-tributario', 'maxima'), F('multa-buzon-desde'), P('buzon-opcion-asalariados')),
         'ley': _ley(('buzon-tributario-que-es', 0), ('multa-buzon-tributario', 0), ('multa-buzon-desde', 0), ('buzon-opcion-asalariados', 0))},
        {'termino': 'Constancia de Situación Fiscal',
         'definicion': 'El documento del SAT que acompaña a tu cédula de identificación fiscal, con la que la autoridad entrega la clave del RFC. Su formato oficial está en el Anexo 1 de la '
                       'Resolución Miscelánea Fiscal y se genera en el Portal del SAT, con el trámite de la ficha %s.' % N('constancia-situacion-fiscal'),
         'ley': _ley(('constancia-situacion-fiscal', 1), ('constancia-situacion-fiscal', 0))},
        {'termino': 'Opinión de Cumplimiento (32-D)',
         'definicion': 'El documento con el que el SAT dice si un contribuyente está al corriente de sus obligaciones fiscales. Lo piden para contratar con el gobierno: quien recibe y ejerce '
                       'recursos públicos federales no puede contratar adquisiciones, arrendamientos, servicios u obra pública con quien, entre otros supuestos, tiene créditos fiscales firmes. '
                       'Se obtiene con el procedimiento de la Resolución Miscelánea Fiscal.',
         'ley': _ley(('opinion-cumplimiento-32d', 0), ('opinion-cumplimiento-32d', 1))},
        {'termino': 'Discrepancia Fiscal',
         'definicion': 'El procedimiento que el SAT puede abrirle a una persona física cuando comprueba que lo que gastó en un año es más que los ingresos que declaró o que debió declarar. '
                       'Es un procedimiento, no un impuesto ni una multa automática. Los bancos informan al SAT de los depósitos en '
                       'efectivo que en el mes pasan de %s por institución; eso es un aviso, no un impuesto.' % P('depositos-efectivo-informe'),
         'ley': _ley(('discrepancia-fiscal', 0), ('depositos-efectivo-informe', 0))},
        {'termino': 'Deducción Ciega (Arrendamiento)',
         'definicion': 'La opción de quien renta un inmueble de deducir, sin comprobantes, el %s de sus ingresos por rentas, en sustitución de las demás deducciones del artículo. '
                       'Cuando quien paga la renta es una persona moral, retiene el %s del pago como ISR.'
                       % (T('deduccion-ciega-arrendamiento'), T('retencion-arrendamiento')),
         'ley': _ley(('deduccion-ciega-arrendamiento', 0), ('retencion-arrendamiento', 0))},
        {'termino': 'IVA Opcional del 7 % (RESICO)',
         'definicion': 'Una opción de la Ley de Ingresos de 2027 para quien tributa en el RESICO: pagar el IVA con una tasa de %s sobre lo efectivamente cobrado, como pago definitivo de cada mes, '
                       'sin acreditar el IVA que le trasladaron y sin poder cambiar de opción en el año. Pide un aviso dentro de los %s días siguientes al primer cobro del año. %s '
                       'Por nuestra cuenta, para actividades a la tasa de %s, deja de convenir cuando el IVA acreditable pasa de %s del trasladado. Rige desde el 1 de enero de 2027; el formato del aviso sigue pendiente.'
                       % (T('iva-opcional-resico-7'), N('iva-opcional-resico-aviso'), D('iva-opcional-resico-7')['nota'], T('sin-cambio-iva-general'), T('iva-opcional-resico-equilibrio')),
         'ley': _ley(('iva-opcional-resico-7', 0), ('iva-opcional-resico-aviso', 0)) + ' · el punto de equilibrio es derivado: ' + _e(D('iva-opcional-resico-equilibrio')['operacion'])},
        {'termino': 'Visita por CFDI Falsos (Art. 49 Bis)',
         'definicion': 'La visita domiciliaria que el SAT puede hacer cuando presume que los comprobantes fiscales que emite un contribuyente son falsos. Desde la entrega o la notificación '
                       'de la orden se suspende la emisión de comprobantes del visitado, y el procedimiento dura como máximo %s días hábiles. Es un procedimiento de revisión: no prueba por sí '
                       'mismo que los comprobantes sean falsos. Quien no lo desvirtúa queda fuera del estímulo de regularización de 2027.' % N('visita-cfdi-falsos-plazo'),
         'ley': _ley(('visita-cfdi-falsos-suspension', 0), ('visita-cfdi-falsos-plazo', 0), ('estimulo-regularizacion-exclusiones', 0))},
        {'termino': 'Estímulo de Regularización 2027',
         'definicion': 'El estímulo de la Ley de Ingresos de 2027 que cubre el %s de las multas, recargos y gastos de ejecución de adeudos del ejercicio %s o anteriores, si se presentan las '
                       'declaraciones y se paga en una sola exhibición a más tardar el %s. No perdona el impuesto. Es de %s cuando el crédito firme es solo de multas por obligaciones distintas '
                       'de las de pago; quien tiene créditos firmes presenta su solicitud a más tardar el %s. No aplica a quien no desvirtuó los procedimientos de los artículos %s del CFF. Rige desde el 1 de enero de 2027.'
                       % (T('estimulo-regularizacion-100', 'porcentaje'), N('estimulo-regularizacion-100', 'adeudos_hasta_ejercicio').replace(',', ''), F('estimulo-regularizacion-100', 'pago_a_mas_tardar'),
                          T('estimulo-regularizacion-90'), F('estimulo-regularizacion-solicitud'), N('estimulo-regularizacion-exclusiones')),
         'ley': _ley(('estimulo-regularizacion-100', 0), ('estimulo-regularizacion-solicitud', 0))},
    ]


def marco():
    """El bloque «Reforma 2027» del Marco legal: los artículos ya cotejados de reforma-2027.json, con su cita."""
    doc = fb.carga('reforma-2027.json')
    items = []
    for d in doc['cambios'] + doc['lo_que_no_cambia']:
        i = d['id']
        if d['estado'] == 'pendiente' or d.get('tabla'):
            continue
        c = d['citas'][0]
        items.append('<details class="fis-precepto"><summary><b>%s</b> · %s %s</summary><blockquote>«%s»</blockquote>%s<p class="pa-chico">%s</p></details>' % (
            html.escape(A(i)), html.escape(d['concepto']), chip(i), html.escape(cita_txt(i)),
            ('<p class="pa-chico">%s</p>' % html.escape(d['nota'])) if d.get('nota') else '', liga(i)))
    return ('<p class="fis-rige"><b>Reforma 2027 (%s).</b> Los preceptos de abajo vienen del Decreto que reforma la LISR y de la Ley de Ingresos de 2027 (DOF del mismo día). '
            'Hasta el 31 de diciembre de 2026 valen los textos de 2026. Cada cita se cotejó palabra por palabra con su documento; el cuadro completo está en '
            '<a href="%s">%s</a>.</p>%s' % (RIGE, ARCHIVO, html.escape(TITULO), ''.join(items)))


# ---------------------------------------------------------------- la prueba
ANIO = re.compile(r'^(19|20)\d\d$')


def _sueltos(texto):
    """Los números de un texto que no entregó ningún lector de la base."""
    plano = html.unescape(re.sub(r'<[^>]+>', ' ', texto))
    permit = ' '.join(EMIT)
    malos = []
    for m in re.finditer(r'\d[\d,.]*\d|\d', plano):
        x = m.group(0).rstrip('.,')
        if len(x) < 2 or ANIO.match(x):
            continue
        if x not in permit:
            malos.append(plano[max(0, m.start() - 40):m.end() + 20].strip())
    return malos


def prueba():
    errores = []
    C = chat()
    for k, t in C['t'].items():
        try:
            re.compile(t['rx'])
        except re.error as e:
            errores.append('tema %s: su expresión no compila (%s)' % (k, e))
        if re.search(r'\(\?<|\(\?P', t['rx']):
            errores.append('tema %s: sin lookbehind ni grupos con nombre (debe valer igual en JavaScript)' % k)
        if not t['fu']:
            errores.append('tema %s: sin fuentes' % k)
        for x in _sueltos(t['h'] + ' ' + t['tit'] + ' ' + ' '.join(c['v'] + ' ' + c['etq'] for c in t['ci'])):
            errores.append('tema %s: un número que no sale de la base: «…%s…»' % (k, x))
        if RIGE in t['h'] and 'valen las cifras de 2026' not in t['h']:
            errores.append('tema %s: lo de 2027 se dice sin mover las cifras de 2026' % k)
    pg = pagina()
    for s in pg['secciones']:
        for x in _sueltos(s['titulo'] + ' ' + s['texto'] + ' ' + s['bloque']):
            errores.append('página, sección %s: un número que no sale de la base: «…%s…»' % (s['id'], x))
    pend = [i for i, d in _base()['D'].items() if d['estado'] == 'pendiente']
    sec = [s for s in pg['secciones'] if s['id'] == 'pendientes'][0]['bloque']
    for i in pend:
        if 'data-pend="%s%s"' % (PRE, i) not in sec:
            errores.append('página: el pendiente %s no está en «Lo que falta por publicar»' % i)
    for c in columnas():
        junto = json.dumps(c, ensure_ascii=False)
        for x in _sueltos(junto):
            errores.append('columna %s: un número que no sale de la base: «…%s…»' % (c['id'], x))
        if re.search(r'www\.dof\.gob\.mx', junto):
            errores.append('columna %s: el DOF se liga sin «www.»' % c['id'])
        for x in c['cotejo']:
            if x['res'] == 'pendiente' and not (x.get('quien') and x.get('donde')):
                errores.append('columna %s: un cotejo pendiente dice quién lo debe y dónde' % c['id'])
    for g in glosario():
        for x in _sueltos(g['termino'].replace('7 %', '') + ' ' + g['definicion'] + ' ' + g['ley']):
            errores.append('glosario «%s»: un número que no sale de la base: «…%s…»' % (g['termino'], x))
    for x in _sueltos(marco()):
        errores.append('marco legal: un número que no sale de la base: «…%s…»' % x)
    # Lo que ya está escrito en columnas.js es lo que hoy da la base.
    raw = open(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'columnas.js'), 'rb').read().decode('utf-8')
    for c in columnas():
        txt = '\r\n'.join(' ' + l for l in json.dumps(c, ensure_ascii=False, indent=1).split('\n'))
        if txt not in raw:
            errores.append('columna %s: columnas.js no trae lo que hoy dice la base; corre fiscal_temas.py --columnas' % c['id'])
    bd = open(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js'), 'rb').read().decode('utf-8')
    for g in glosario():
        if json.dumps(g['definicion'], ensure_ascii=False) not in bd or json.dumps(g['ley'], ensure_ascii=False) not in bd:
            errores.append('glosario «%s»: la base de la plataforma no trae lo que hoy dice la base fiscal; corre integrar_glosario_fiscal.py' % g['termino'])
    if errores:
        for e in errores:
            print('fiscal_temas: ERROR:', e)
        return 1
    print('fiscal_temas: %d temas del chat, %d secciones de la página, %d verificaciones y %d términos; ningún número fuera de la base'
          % (len(C['t']), len(pg['secciones']), len(columnas()), len(glosario())))
    return 0


if __name__ == '__main__':
    if '--columnas' in sys.argv:
        escribe_columnas()
    elif '--prueba' in sys.argv:
        sys.exit(prueba())
    else:
        print(__doc__)
