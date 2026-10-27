# -*- coding: utf-8 -*-
"""Inversion y Megaobras, aplicacion 2: «Sector e industria» (obra por
obra) en pagina propia (13-10-2026). Sustituye al marco que cargaba la
portada entera (bloque eb-sector del motor).

Lo que hacia el motor y aqui se conserva:
  - Paso 1, industria: mosaico de sectores con su costo real, cuantas obras
    y su parte del total, recalculado segun el mandato elegido
    (renderSimuladorSectorMosaico).
  - Paso 2, mandato: tarjetas de los seis sexenios con cuantas obras le
    tocan dentro de la industria (renderSimuladorMandatoPills).
  - Filtro activo y sus tres cifras: costo real, aprobado frente a erogado,
    perdida operativa anual y por segundo (renderSimuladorDesgloseCab).
  - El aviso de la ficha pericial del Tren Maya, retirada el 10-10-2026.
  - La comparativa: cinco criterios de orden, evaluar y reiniciar a ceros,
    medir al llegar, ver las 13 en contexto (renderSimuladorRankingFiltro).
  - La simulacion en vivo: lo que nos cuesta cada obra mientras miras, el
    contador conjunto y la ficha completa de cada obra con lo que dicen los
    documentos oficiales (simVivoTotal, simVivoCaja, renderSimuladorObrasGrid,
    simVerificadoHtml).
  - Contra que se compara este dinero (renderSimuladorEscala con
    simAnclasOficiales).

Antes de pintar se aplica, igual que megaobrasOficialBase() del motor, lo
que dicen los estados financieros oficiales (operacion_oficial) y el costo
en vivo (costo_vivo_megaobras). Mismas colecciones, mismas operaciones.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['sector']).
"""
import copy
import html
import json
import math

from presupuesto_modulos import chip
import mo_base
import mo_capitulos
from mo_base import nota_base

ESTILOS = ['mo-sector.css', 'mo-pulso.css']
SCRIPTS = ['mo-sector.js', 'mo-pulso.js']

SEXENIOS = [
    {'k': 'Salinas', 'nom': 'Carlos Salinas', 'ini': 1988, 'fin': 1994, 'color': '#8e6cb0'},
    {'k': 'Zedillo', 'nom': 'Ernesto Zedillo', 'ini': 1994, 'fin': 2000, 'color': '#4a90d9'},
    {'k': 'Fox', 'nom': 'Vicente Fox', 'ini': 2000, 'fin': 2006, 'color': '#3fa373'},
    {'k': 'Calderón', 'nom': 'Felipe Calderón', 'ini': 2006, 'fin': 2012, 'color': '#c9a227'},
    {'k': 'Peña Nieto', 'nom': 'Enrique Peña', 'ini': 2012, 'fin': 2018, 'color': '#d98032'},
    {'k': 'López Obrador', 'nom': 'López Obrador', 'ini': 2018, 'fin': 2024, 'color': '#c0504d'},
]

ORDENES = [('perdida', 'Pérdida anual'), ('sobrecosto', 'Sobrecosto'), ('inversion', 'Costo real'),
           ('brecha', 'Pesos de más'), ('cronologia', 'Cronología')]

DEFICIT = ('deficit_cronico', 'subsidio_permanente', 'deuda_perpetua', 'perdida_patrimonial')

# Fichas del Registro de pendientes que ya existen (herramientas/pendientes.py).
PEND_PERDIDA = 'reloj-megaobras'
PEND_UNITARIO = 'costo-unitario-megaobras'
PEND_FICHA_TM = 'tren-maya-ficha'

AUDITORIA_OBRA = {
    'tren-maya': 'auditoria-tren-maya.html',
    'dos-bocas': 'auditoria-dos-bocas.html',
    'aifa-texcoco': 'auditoria-aifa.html',
    'tren-toluca': 'auditoria-tren-toluca.html',
    'megafarmacia': 'auditoria-megafarmacia.html',
    'agronitrogenados': 'auditoria-agronitrogenados.html',
    'fertinal': 'auditoria-fertinal.html',
    'estela-luz': 'auditoria-estela-luz.html',
    'bunker-garcia-luna': 'auditoria-bunker-garcia-luna.html',
    'refineria-tula': 'auditoria-refineria-tula.html',
    'enciclomedia': 'auditoria-enciclomedia.html',
    'fobaproa': 'auditoria-fobaproa.html',
    'farac-carretero': 'auditoria-farac-carretero.html',
}


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def esc(t):
    return html.escape(str(t if t is not None else ''), quote=True)


def _r(x, n=0):
    """Redondeo como Math.round de JS (mitad hacia arriba)."""
    f = 10 ** n
    return math.floor(x * f + 0.5) / f


def num(v):
    """toLocaleString('es-MX') de JS: hasta tres decimales, sin ceros de cola."""
    s = format(_r(v, 3), ',.3f').rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def jsnum(v):
    """Un numero escrito como lo escribe JS al concatenarlo."""
    v = float(v)
    return str(int(v)) if v.is_integer() else repr(v)


def mdp1(n):
    return '$' + format(n, ',.1f') + ' mdp'


def sim_mdp(n):
    """simMdp() del motor: billones, mil millones o millones, sin ambiguedad."""
    a = abs(n)
    if a >= 1000000:
        return '$' + format(n / 1000000, '.2f') + ' billones'
    if a >= 1000:
        return '$' + num(_r(n / 100) / 10) + ' mil millones'
    return '$' + num(_r(n * 100) / 100) + ' millones'


# ---------------------------------------------------------------------------
# Datos: replica de megaobrasOficialBase() (audit-engine.js)
# ---------------------------------------------------------------------------
PEND_TXT = ('Ningún documento oficial cotejado todavía dice cuánto cuesta operar esta obra ni cuánto ingresa. '
            'La pérdida, los costos y cualquier proyección quedan pendientes; no se estiman.')
HALL_PEND = ('Falta cotejar el informe individual de la Auditoría Superior de la Federación del año de esta obra. '
             'Mientras tanto no se publica ningún hallazgo.')
ESTATUS = {'megafarmacia': 'En operación · cifras pendientes', 'estela-luz': 'Monumento concluido',
           'bunker-garcia-luna': 'Uso actual pendiente de documento'}


def obras_oficiales(base):
    sm = base['simulador_megaobras']
    of = sm.get('operacion_oficial') or {}
    ver_obras = (sm.get('verificacion') or {}).get('obras') or {}
    obras = copy.deepcopy(sm['obras'])
    # La medida unica de ganancia o perdida (mo_base.resultado, 21-10-2026).
    medida = mo_base.resultados(sm)
    cu = (sm.get('cuenta') or {}).get('obras') or {}
    for o in obras:
        d = (of.get('obras') or {}).get(o['id'])
        r = medida[o['id']]
        o['res'] = r
        ver = ver_obras.get(o['id'])
        o['estado_campos'] = dict(o.get('estado_campos') or {})
        ec = o['estado_campos']
        o['costo_unitario_real'] = 'pendiente de documento: falta el aforo o el volumen oficial de operación.'
        if not ver:
            o['hallazgo_asf'] = HALL_PEND
        if o['id'] in ESTATUS:
            o['estatus'] = ESTATUS[o['id']]
        o['perdida_pendiente'] = False
        if d and o['id'] == 'fobaproa':
            # Decision del autor (17-10-2026): la perdida antes del apoyo del
            # presupuesto (deficit del Fondo FOBAPROA + Ramo 34 que recibio).
            # Desde el 21-10-2026, con el año de la medida unica (2025):
            # deficit del ejercicio mas el Ramo 34 que recibio ese año.
            perd = -r['v']
            filas = cu.get(o['id']) or []
            def_r = next(f for f in filas if f['c'] == 'resultado_anual_mdp' and f.get('anio') == r['anio'])
            r34 = next(f for f in filas if f['c'] == 'transferencias_ramo34_paab_anuales_mdp' and f.get('anio') == r['anio'])
            o['ingresos_anuales_mdp'] = 0
            o['costo_operativo_anual_mdp'] = perd
            o['perdida_anual_mdp'] = perd
            ec['perdida_anual_mdp'] = r['e']
            ec['desglose'] = 'oficial'
            o['desglose_titulo'] = 'De qué está hecha su pérdida de %s, antes del apoyo del presupuesto' % r['anio']
            o['desglose_costos_operacion'] = [
                {'rubro': 'Déficit del Fondo FOBAPROA en %s, después de las transferencias (IPAB, estados financieros dictaminados)' % r['anio'],
                 'monto_anual_mdp': -def_r['v'], 'icono': '📉'},
                {'rubro': 'Ramo 34 que recibió ese año, apoyo a ahorradores y deudores de la banca', 'monto_anual_mdp': r34['v'], 'icono': '🏛️'}]
            o['proy_titulo'] = 'Lo que dicen los documentos: una deuda que sigue viva'
            o['proyeccion_resumen'] = (
                'Al 31 de diciembre de 2025 el IPAB debía %s en bonos (%s a corto plazo y %s a largo), según sus estados financieros. '
                'Del Ramo 34 salieron %s en %s y %s de 2014 a 2025 (suma de la Cuenta Pública). '
                'Cuánto se pagó de 1998 a 2013 y hasta qué año se pagará siguen pendientes de documento.'
                % (mdp1(d['saldo_bonos_2025']), mdp1(d['saldo_bonos_corto']), mdp1(d['saldo_bonos_largo']),
                   mdp1(r34['v']), r['anio'], mdp1(d['ramo34_2014_2025'])))
            o['fuente_operacion'] = 'cp'
        elif d:
            res = d['resultado_sin_transferencias']
            o['ingresos_anuales_mdp'] = d['ingresos_gestion']
            o['costo_operativo_anual_mdp'] = d['gastos_totales']
            o['perdida_anual_mdp'] = -r['v']
            ec['perdida_anual_mdp'] = r['e']
            ec['desglose'] = 'oficial'
            o['desglose_costos_operacion'] = [{'rubro': '%s (%s)' % (g['rubro'], d['anio']), 'monto_anual_mdp': g['mdp'], 'icono': '📄'}
                                              for g in d['gastos']]
            cubre = d['ingresos_gestion'] / d['gastos_totales'] * 100 if d['gastos_totales'] else 0
            o['proy_titulo'] = 'Lo que dicen sus estados financieros de %s' % d['anio']
            o['proyeccion_resumen'] = (
                'En %s cobró %s por sus servicios y gastó %s: sus ingresos propios cubrieron el %s %% de su gasto. '
                'Además recibió %s de transferencias federales y %s de otros ingresos, con lo que cerró con un resultado contable de %s. '
                % (d['anio'], mdp1(d['ingresos_gestion']), mdp1(d['gastos_totales']), format(cubre, '.1f'),
                   mdp1(d['transferencias']), mdp1(d['otros_ingresos']), mdp1(d['resultado_ejercicio']))
                + ('Sin esas transferencias ni otros ingresos, operar le habría costado %s más de lo que cobró: ese es su déficit antes de '
                   'transferencias y otros ingresos. En un servicio público gastar más de lo que se cobra no prueba por sí solo desperdicio, '
                   'pero sí dice cuánto depende del erario.' % mdp1(-res)
                   if res < 0 else
                   'Sin esas transferencias, su operación todavía deja %s a favor: no registra déficit antes de transferencias ese año. '
                   'Lo que pesa es lo que costó construirla, que se mide aparte.' % mdp1(res)))
            o['fuente_operacion'] = d['fuente']
        else:
            o['perdida_pendiente'] = r['tipo'] != 'dato'
            o['ingresos_anuales_mdp'] = 0
            o['costo_operativo_anual_mdp'] = 0
            o['perdida_anual_mdp'] = -r['v'] if r['tipo'] == 'dato' else 0
            o['desglose_costos_operacion'] = []
            if r['tipo'] == 'dato':
                ec['perdida_anual_mdp'] = r['e']
                o['proy_titulo'] = 'Lo que dice su resultado publicado de %s' % r['anio']
                o['proyeccion_resumen'] = '%s %s en %s (resultado del ejercicio). %s %s' % (
                    'Ganó' if r['v'] > 0 else 'Perdió', mdp1(abs(r['v'])), r['anio'], r['op'], r['nota'])
            elif r['tipo'] == 'no_aplica':
                o['proy_titulo'] = 'No opera'
                o['proyeccion_resumen'] = r['txt']
            else:
                o['proy_titulo'] = 'Lo que falta documentar'
                o['proyeccion_resumen'] = PEND_TXT
            cx = (of.get('contexto_entidad') or {}).get(o['id'])
            if cx and cx.get('texto'):
                o['proyeccion_resumen'] += ' ' + cx['texto']
            elif cx:
                rr = cx['resultado_ejercicio']
                o['proyeccion_resumen'] += (
                    ' Lo más cercano en un documento oficial: en %s %s ingresó %s por sus ventas y %s de otros ingresos, gastó %s y cerró con %s (%s). %s'
                    % (cx['anio'], cx['entidad'], mdp1(cx['ingresos_gestion']), mdp1(cx['otros_ingresos']), mdp1(cx['gastos_totales']),
                       'una pérdida contable de ' + mdp1(-rr) if rr < 0 else 'un resultado a favor de ' + mdp1(rr),
                       (of['fuentes'].get(cx['fuente']) or {}).get('doc'), cx['nota']))
            if cx and cx.get('extra'):
                o['proyeccion_resumen'] += ' ' + cx['extra']
            if cx and cx.get('desglose'):
                o['desglose_costos_operacion'] = [{'rubro': g['rubro'], 'monto_anual_mdp': g['mdp'], 'icono': g.get('icono') or '📄'}
                                                  for g in cx['desglose']]
                o['desglose_titulo'] = cx.get('desglose_titulo')
                ec['desglose'] = cx.get('desglose_estado') or 'oficial'
        o['perdida_segundo'] = o['perdida_anual_mdp'] * 1e6 / 31536000

    return obras


def anclas(base):
    """simAnclasOficiales() del motor, con su estado y su referencia."""
    P = base.get('panoramaErario') or {}
    F = P.get('federalizado') or {}
    r33 = next((c for c in F.get('componentes') or [] if c['id'] == 'fed-r33'), None)
    deuda = _r(sum(float(e.get('deuda') or 0) for e in base.get('estados') or []) * 10) / 10
    ce = (base.get('cuentas_ecologicas') or {}).get('ctada') or {}
    out = [
        {'k': 'Ramo 33 · aportaciones federales a estados y municipios', 'v': _r(r33['montoMdp'] * 10) / 10 if r33 else None,
         'ej': '2026', 'ref': 'ref-pef2026', 'e': 'oficial', 'op': ''},
        {'k': 'Gasto federalizado completo', 'v': F.get('totalMdp'), 'ej': '2026', 'ref': 'ref-pef2026', 'e': 'oficial', 'op': ''},
        {'k': 'Deuda subnacional de las 32 entidades', 'v': deuda or None, 'ej': 'cierre de 2025', 'ref': 'ref-shcp-alertas', 'e': 'derivado',
         'op': 'suma de la deuda de las 32 entidades que reporta el Sistema de Alertas'},
        {'k': 'Costo ambiental de un año completo', 'v': ce.get('total_mdp'), 'ej': '2024', 'ref': 'ref-ceem-2024', 'e': ce.get('estado') or 'oficial', 'op': ''},
        {'k': 'Presupuesto de Egresos de la Federación', 'v': P.get('totalPEF'), 'ej': '2026', 'ref': 'ref-pef2026', 'e': 'oficial', 'op': ''},
    ]
    return [a for a in out if a['v']]


# ---------------------------------------------------------------------------
# Piezas de HTML
# ---------------------------------------------------------------------------
def _fuente_link(k, fuentes):
    f = fuentes.get(k)
    if not f:
        return ''
    return '<li><a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a></li>' % (esc(f['url']), esc(f['doc']))


def verificado(o, ver, fuentes):
    """simVerificadoHtml() del motor."""
    if not ver:
        return ('<p class="ms-ver-nada">%s Ningún documento oficial localizado todavía para esta obra: sus cifras se muestran '
                'como las registra el simulador, sin fuente.</p>' % chip('pendiente'))

    def m(n):
        return '$' + num(n) + ' mdp'
    h = []
    if ver.get('cartera'):
        h.append('<h5 class="ms-ver-sub">Monto total de inversión registrado ante Hacienda · clave %s</h5>'
                 '<div class="ms-tabla-marco"><table class="ms-ver-tabla"><thead><tr><th>Corte</th><th>Monto total</th><th>Término previsto</th></tr></thead><tbody>%s</tbody></table></div>'
                 % (esc(ver.get('clave', '')), ''.join('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(c['corte']), m(c['mti']), esc(c.get('fin') or ''))
                                                         for c in ver['cartera'])))
    if ver.get('carteraNaim'):
        c = ver['carteraNaim'][0]
        h.append('<p class="ms-ver-p">El NAIM de Texcoco (clave 1409JZL0005) registraba %s en el corte %s %s.</p>' % (m(c['mti']), esc(c['corte']), chip('oficial')))
    if ver.get('ejercidoCP'):
        anios = sorted(ver['ejercidoCP'])
        h.append('<h5 class="ms-ver-sub">Ejercido bajo su clave, según la Cuenta Pública</h5>'
                 '<div class="ms-tabla-marco"><table class="ms-ver-tabla"><thead><tr><th>Año</th><th>Ejercido</th></tr></thead><tbody>%s'
                 '<tr class="ms-ver-total"><td>Suma</td><td>%s %s</td></tr></tbody></table></div>'
                 % (''.join('<tr><td>%s</td><td>%s</td></tr>' % (a, m(ver['ejercidoCP'][a])) for a in anios), m(ver['ejercidoTotal']), chip('derivado')))
    if ver.get('pef2026'):
        partes = []
        if ver['pef2026'].get('inversion'):
            partes.append(m(ver['pef2026']['inversion']) + ' para inversión bajo la misma clave')
        if ver['pef2026'].get('operacion'):
            partes.append(m(ver['pef2026']['operacion']) + ' para operar el servicio')
        if partes:
            h.append('<p class="ms-ver-p"><strong>PEF 2026:</strong> %s %s.</p>' % ('; '.join(partes), chip('oficial')))
    if ver.get('naicm'):
        n = ver['naicm']
        h.append('<p class="ms-ver-p"><strong>Costo de cancelar el NAIM:</strong> %s al 31 de diciembre de 2019, según la ASF; la fase 1 se había '
                 'planeado en %s (pp. %s) %s.</p>' % (m(n['costo']), m(n['faseUnoPlaneada']), esc(n['paginas']), chip('oficial')))
    if ver.get('ramo34'):
        anios = sorted(ver['ramo34'])
        h.append('<h5 class="ms-ver-sub">Ramo 34, apoyo a ahorradores y deudores de la banca, ejercido cada año</h5>'
                 '<div class="ms-tabla-marco"><table class="ms-ver-tabla"><thead><tr><th>Año</th><th>Ejercido</th></tr></thead><tbody>%s'
                 '<tr class="ms-ver-total"><td>PEF 2026</td><td>%s %s</td></tr></tbody></table></div>'
                 % (''.join('<tr><td>%s</td><td>%s</td></tr>' % (a, m(ver['ramo34'][a])) for a in anios), m(ver['pef2026Ramo34']), chip('oficial')))
    au = (ver.get('asf2024') or {}).get('auditorias') or []
    if au:
        items = []
        for a in au:
            det = 'universo ' + m(a['universo']) + '; ' + (('1 acción' if a['acciones'] == 1 else '%d acciones' % a['acciones']) if a['acciones'] else 'sin acciones')
            if a.get('recuperaciones'):
                det += '; recuperó ' + m(a['recuperaciones'])
            if a.get('porAclarar'):
                det += '; por aclarar ' + m(a['porAclarar'])
            det += '; p. %s' % a['pagina']
            items.append('<li><strong>%s</strong> · %s <span class="ms-ver-dim">(%s)</span></li>' % (a['num'], esc(a['titulo']), det))
        h.append('<h5 class="ms-ver-sub">Auditorías de la ASF a la Cuenta Pública 2024</h5><ul class="ms-ver-asf">%s</ul>' % ''.join(items))
    if ver.get('asfHist'):
        h.append('<h5 class="ms-ver-sub">Lo que documentó la Auditoría Superior de la Federación</h5>'
                 '<div class="ms-tabla-marco"><table class="ms-ver-tabla"><thead><tr><th>Dato</th><th>Cifra</th><th>Página</th></tr></thead><tbody>%s</tbody></table></div>'
                 % ''.join('<tr><td>%s</td><td>%s %s</td><td>%s</td></tr>' % (esc(a['dato']), esc(a['valor']), chip(a['estado']), esc(a['pagina']))
                           for a in ver['asfHist']))
    if ver.get('hallazgo') and ver.get('asfHist'):
        h.append('<p class="ms-ver-p">%s</p>' % esc(ver['hallazgo']))
    if ver.get('contradicciones'):
        h.append('<div class="ms-ver-inc"><strong>⚠️ Incongruencia entre documentos oficiales.</strong> Explicarla le corresponde al gobierno, '
                 'que es quien publica las dos cifras.%s</div>' % ''.join('<p>%s</p>' % esc(t) for t in ver['contradicciones']))
    h.append('<ul class="ms-fuentes">%s</ul>' % ''.join(_fuente_link(k, fuentes) for k in ver.get('fuentes') or []))
    return ('<details class="ms-plegable ms-docs"><summary><span aria-hidden="true">📑</span> Lo que dicen los documentos oficiales</summary>'
            '<div class="ms-plegable-cuerpo">%s</div></details>' % ''.join(h))


def caja_vivo(o):
    """La caja de cada ficha: lo que la obra gana o pierde al año con la
    medida unica de la herramienta (mo_base.resultado, 21-10-2026). Antes
    corria el «costo vivo» (lo que el PEF 2026 le asigna mas intereses a la
    tasa implicita de la deuda, una estimacion propia): el autor pidio una
    sola medida. La cifra del periodo la ajusta el JS."""
    r = o['res']
    if r['tipo'] != 'dato':
        na = r['tipo'] == 'no_aplica'
        return ('<div class="ms-vivo-caja ms-parado"><div class="ms-vivo-et">⏸️ Gana o pierde al año %s</div>'
                '<div class="ms-vivo-monto">%s</div><p class="ms-vivo-nota">%s%s</p></div>'
                % ('' if na else chip('pendiente', 'cuenta-' + o['id']), 'No opera' if na else 'No publica su resultado',
                   '' if na else '<b>Por qué falta:</b> ', esc(r['txt'])))
    v = r['v']
    seg = v * 1e6 / 31536000
    signo = '+' if v > 0 else '−'
    return (
        '<div class="ms-vivo-caja %s" data-anual="%s">'
        '<div class="ms-vivo-izq"><div class="ms-vivo-et"><span class="ms-punto" aria-hidden="true"></span> %s <span class="ms-per-et">al día</span> %s</div>'
        '<div class="ms-vivo-monto ms-num">%s %s/día</div>'
        '<p class="ms-vivo-nota">%s %s en %s, %s. <a href="herramienta-megaobras-pulso-cuenta.html#cuenta-%s">De dónde sale</a></p></div>'
        '<div class="ms-vivo-der"><span class="ms-vivo-et">⏱️ Mientras miras</span>'
        '<span class="ms-tic ms-num" data-rate="%r">%s$0.00</span><small class="ms-num">(%s$%s/seg)</small></div>'
        '</div>'
        % ('ms-gana' if v > 0 else 'ms-pierde', jsnum(v), 'Gana' if v > 0 else 'Pierde', chip(r['e']),
           'Gana' if v > 0 else 'Pierde', sim_mdp(abs(v) / 365), 'Ganó' if v > 0 else 'Perdió', mdp1(abs(v)), r['anio'],
           'antes del apoyo del presupuesto' if r['base'] == 'sin_apoyo' else 'resultado del ejercicio publicado', esc(o['id']),
           seg, signo, signo, format(abs(seg), ',.2f')))


def ficha(o, ver, fuentes, sectores, cuenta):
    ec = o['estado_campos']
    pend_obra = 'obra-' + o['id'] if ver and any(x == 'pendiente' for x in (ver.get('campos') or {}).values()) else None

    def chip_campo(campo, pend=None):
        e = ec.get(campo) or 'pendiente'
        return chip(e, pend if e == 'pendiente' else None)
    defs = (ver or {}).get('definiciones') or {}

    def defin(campo):
        return defs.get(campo) or 'Cifra del simulador sin documento oficial localizado todavía.'
    es_def = o.get('proyeccion_tipo') in DEFICIT
    sob = o['sobrecosto_pct']
    desg = o['desglose_costos_operacion']
    sec = sectores.get(o['sector_id'], {})
    return '''<article class="ms-ficha" id="obra-{id}" data-id="{id}" style="--ms-badge:{color}" tabindex="-1">
  <header class="ms-ficha-cab">
    <span class="ms-ficha-ico" aria-hidden="true">{ico}</span>
    <div class="ms-ficha-tx">
      <h3 class="ms-ficha-nom">{nombre}</h3>
      <p class="ms-ficha-meta">🏛️ <strong>{pres}</strong> ({per}) · {sico} {snom}</p>
    </div>
    <span class="ms-badge">{estatus}</span>
  </header>
  {vivo}
  <div class="ms-inv">
    <div class="ms-inv-c"><span class="ms-inv-l">Presupuesto original {c_presu}</span><span class="ms-inv-v ms-num">${presu} mdp</span></div>
    <div class="ms-inv-c"><span class="ms-inv-l">Costo real erogado {c_real}</span><span class="ms-inv-v ms-inv-oro ms-num">${real} mdp</span></div>
    <div class="ms-inv-c"><span class="ms-inv-l">{et_sob} {c_sob}</span><span class="ms-inv-v ms-num{rojo}">{sob}%</span></div>
  </div>
  {antecedente}{base}
  <details class="ms-plegable"><summary><span aria-hidden="true">🔎</span> De dónde sale cada una de estas tres cifras</summary>
    <div class="ms-plegable-cuerpo"><dl class="ms-defs">
      <dt>Presupuesto original</dt><dd>{d_presu}</dd>
      <dt>Costo real erogado</dt><dd>{d_real}</dd>
      <dt>{et_sob}</dt><dd>{d_sob}</dd>
    </dl></div></details>
  <div class="ms-desg">
    <p class="ms-desg-tit">⚙️ {desg_tit}: {c_desg}</p>
    <ul class="ms-desg-lista">{desg}</ul>
  </div>
  <div class="ms-proy{deficit}">
    <p class="ms-proy-tit"><span aria-hidden="true">{proy_ico}</span> {proy_tit}</p>
    <p class="ms-proy-tx">{proy}</p>
  </div>
  <div class="ms-asf">
    <p><strong>🔍 Auditoría y hallazgos:</strong> {c_hall} {hall}</p>
    <p class="ms-unit">📊 <strong>Costo por usuario:</strong> {c_unit} {unit}</p>
  </div>
  {docs}
  <div class="ms-ficha-pie">
    {auditoria}
    <button type="button" class="ms-btn ms-btn-sec ms-compartir" data-id="{id}"><span aria-hidden="true">🔗</span> Copiar el enlace a esta obra</button>
    <a class="ms-btn ms-btn-sec" href="#ms-comparativa"><span aria-hidden="true">↑</span> Volver a la comparativa</a>
    <span class="ms-copiado" role="status" aria-live="polite"></span>
  </div>
</article>'''.format(
        id=esc(o['id']), color=esc(o.get('badge_color') or 'var(--gold)'), ico=o['icono'], nombre=esc(o['nombre']),
        auditoria=('<a class="ms-btn ms-btn-sec" href="%s"><span aria-hidden="true">🖼️</span> Ver su Auditoría en imágenes</a> '
                   '<a class="ms-btn ms-btn-sec" href="auditoria-inversion-megaobras.html"><span aria-hidden="true">🖼️</span> Las 13 en imágenes</a>'
                   % AUDITORIA_OBRA[o['id']]) if o['id'] in AUDITORIA_OBRA else
                  '<a class="ms-btn ms-btn-sec" href="auditoria-inversion-megaobras.html"><span aria-hidden="true">🖼️</span> Ver en Auditoría en imágenes</a>',
        pres=esc(o['presidente']), per=esc(o['periodo_sexenal']), sico=sec.get('icono', ''), snom=esc(sec.get('nombre', '')),
        estatus=esc(o['estatus']), vivo=caja_vivo(o),
        c_presu=chip_campo('inversion_presupuestada_mdp', pend_obra), presu=num(o['inversion_presupuestada_mdp']),
        c_real=chip_campo('inversion_real_mdp', pend_obra), real=num(o['inversion_real_mdp']),
        et_sob=esc(o.get('sobrecosto_etiqueta') or 'Sobrecosto'),
        antecedente=('<p class="ms-nota"><span aria-hidden="true">🕰️</span> <strong>Antecedente.</strong> %s</p>' % esc(o['antecedente'])) if o.get('antecedente') else '',
        base=nota_base(o, cuenta.get(o['id']), 'ms-plegable ms-base'),
        c_sob=chip_campo('sobrecosto_pct', pend_obra), sob=('+' if sob > 0 else '') + jsnum(sob), rojo=' ms-inv-rojo' if sob > 100 else '',
        d_presu=esc(defin('inversion_presupuestada_mdp')), d_real=esc(defin('inversion_real_mdp')), d_sob=esc(defin('sobrecosto_pct')),
        desg_tit=esc(o.get('desglose_titulo') or 'Principales costos de operación anuales'),
        c_desg=chip_campo('desglose', PEND_PERDIDA),
        desg=''.join('<li><span aria-hidden="true">%s</span> %s: <strong class="ms-num">$%s mdp</strong></li>' % (c['icono'], esc(c['rubro']), num(c['monto_anual_mdp']))
                     for c in desg) or '<li>Sin desglose con documento oficial.</li>',
        deficit=' ms-proy-deficit' if es_def else '', proy_ico='⚠️' if es_def else '📊',
        proy_tit=esc(o.get('proy_titulo') or ('Diagnóstico financiero: déficit permanente o deuda' if es_def else 'Proyección de retorno o amortización')),
        proy=esc(o['proyeccion_resumen']),
        c_hall=chip('oficial') if ver else chip('pendiente'), hall=esc(o['hallazgo_asf']),
        c_unit=chip('pendiente', PEND_UNITARIO), unit=esc(o['costo_unitario_real']),
        docs=verificado(o, ver, fuentes))


def construir(base, ref):
    # Aplicacion 2 (pedido del autor, 21-10-2026): la obra por obra y, debajo,
    # de que esta hecho el total (la composicion del pulso, mo_pulso).
    import mo_pulso
    c = mo_pulso._contexto(base, ref)
    return mo_pulso.cajon_calculo(base, ref, c) + _construir(base, ref) + '\n' + mo_pulso.bloque(base, ref, ('composicion',), c)


def _construir(base, ref):
    sm = base['simulador_megaobras']
    obras = obras_oficiales(base)
    ver_obras = (sm.get('verificacion') or {}).get('obras') or {}
    cv = base.get('costo_vivo_megaobras') or {}
    fuentes = dict(((cv.get('fuentes') or {})))
    fuentes.update((sm.get('verificacion') or {}).get('fuentes') or {})
    sectores = [s for s in sm['sectores'] if s['id'] != 'todos']
    sec_por = {s['id']: s for s in sectores}
    periodos = sm['periodos']
    # Decision del autor (17-10-2026): los rescates van aparte; «todas las
    # industrias» suma solo las obras y la industria «rescates» se ve sola.
    solo_obras = [o for o in obras if o.get('tipo') != 'rescate']
    rescates = [o for o in obras if o.get('tipo') == 'rescate']
    n = len(solo_obras)
    total_real = sum(o['inversion_real_mdp'] for o in solo_obras)
    total_presu = sum(o['inversion_presupuestada_mdp'] for o in solo_obras)
    resc_real = sum(o['inversion_real_mdp'] for o in rescates)
    an = anclas(base)

    # Paso 1: losetas (el JS reescribe cifras y barras segun el mandato).
    losetas = []
    for s in sectores:
        ob = [o for o in obras if o['sector_id'] == s['id']]
        real = sum(o['inversion_real_mdp'] for o in ob)
        cuota = real / total_real * 100 if total_real and s['id'] != 'rescates' else 0
        losetas.append(
            '<button type="button" class="ms-los" data-sector="{id}" aria-pressed="false">'
            '<span class="ms-los-fila"><span class="ms-los-ico" aria-hidden="true">{ico}</span><span class="ms-los-nom">{nom}</span>'
            '<span class="ms-los-cif ms-num">{cif}</span></span>'
            '<span class="ms-riel"><span class="ms-barra" style="width:{w}%"></span></span>'
            '<span class="ms-los-pie"><span class="ms-los-n">{n}</span><span class="ms-los-cuota">{c}</span></span>'
            '</button>'.format(id=s['id'], ico=s['icono'], nom=esc(s['nombre']), cif=sim_mdp(real), w=format(cuota, '.1f'),
                               n='%d %s' % (len(ob), 'obra' if len(ob) == 1 else 'obras'),
                               c='Se cuentan aparte de las obras' if s['id'] == 'rescates' else format(cuota, '.1f') + '% del costo real'))

    # Paso 2: mandatos.
    def tarjeta(k, nom, periodo, cuantas, color):
        return ('<button type="button" class="ms-mdt" data-mandato="%s" aria-pressed="false" style="--ms-mdt:%s">'
                '<span class="ms-mdt-nom">%s</span><span class="ms-mdt-per">%s</span><span class="ms-mdt-n">%d %s</span></button>'
                % (esc(k), color, esc(nom), periodo, cuantas, 'obra' if cuantas == 1 else 'obras'))
    mandatos = [tarjeta('todos', 'Todos los mandatos', '1988–2024', n, '#c9a227')]
    for x in SEXENIOS:
        cuantas = sum(1 for o in solo_obras if x['k'].lower() in o['presidente'].lower())
        mandatos.append(tarjeta(x['k'], x['nom'], '%d–%d' % (x['ini'], x['fin']), cuantas, x['color']))

    ordenes = ''.join('<button type="button" class="ms-orden" data-orden="%s" aria-pressed="%s">%s</button>'
                      % (k, 'true' if k == 'perdida' else 'false', et) for k, et in ORDENES)
    cadencias = ''.join('<button type="button" class="ms-cad" data-per="%s" aria-pressed="%s">%s</button>'
                        % (k, 'true' if k == 'dia' else 'false', esc(p['label'])) for k, p in periodos.items())

    # Contador conjunto: las obras que publican su resultado (el JS oculta
    # las que no estan en el filtro).
    corren = sorted([o for o in obras if o['res']['tipo'] == 'dato'], key=lambda o: o['res']['v'])
    tabla_vivo = ''.join('<tr data-id="%s"><td>%s</td><td class="ms-num %s">%s %s</td><td class="ms-num">%s$%s</td></tr>'
                         % (esc(o['id']), esc(o['nombre']), 'ms-gana' if o['res']['v'] > 0 else 'ms-pierde',
                            'Gana' if o['res']['v'] > 0 else 'Pierde', sim_mdp(abs(o['res']['v'])),
                            '+' if o['res']['v'] > 0 else '−', num(_r(abs(o['res']['v']) * 1e6 / 31536000)))
                         for o in corren)

    cuenta = (sm.get('cuenta') or {}).get('obras') or {}
    fichas = '\n'.join(ficha(o, ver_obras.get(o['id']), fuentes, sec_por, cuenta) for o in obras)

    escala = ''.join(
        '<li class="ms-esc-fila" data-v="{v}"><span class="ms-esc-veces ms-num">—</span>'
        '<span class="ms-esc-k">{k} <span class="ms-esc-ej">({ej})</span> {chip}{ref}{op}</span>'
        '<span class="ms-riel"><span class="ms-barra" style="width:0%"></span></span>'
        '<span class="ms-esc-v ms-num">{vt}</span></li>'.format(
            v=jsnum(a['v']), k=esc(a['k']), ej=esc(a['ej']), chip=chip(a['e']), ref=ref(a['ref']),
            op=(' <small class="ms-esc-op">(%s)</small>' % esc(a['op'])) if a['op'] else '', vt=sim_mdp(a['v'])) for a in an)

    pend_real = [o['id'] for o in obras if (o['estado_campos'].get('inversion_real_mdp') or 'pendiente') == 'pendiente']
    tm = base.get('tren_maya_peritaje_2024') or {}

    datos = {
        'obras': [{'id': o['id'], 'n': o['nombre'], 'ico': o['icono'], 's': o['sector_id'], 'p': o['presidente'], 'per': o['periodo_sexenal'],
                   'real': o['inversion_real_mdp'], 'presu': o['inversion_presupuestada_mdp'], 'sob': o['sobrecosto_pct'],
                   'perd': o['perdida_anual_mdp'], 'pend': o['perdida_pendiente'], 'color': o.get('badge_color') or '',
                   'na': o['res']['tipo'] == 'no_aplica',
                   'vivo': o['res']['v'] if o['res']['tipo'] == 'dato' else None,
                   'parada': o['res']['tipo'] != 'dato',
                   'pendReal': o['id'] in pend_real, 'resc': o.get('tipo') == 'rescate'} for o in obras],
        'sectores': [{'id': s['id'], 'nom': s['nombre'], 'ico': s['icono']} for s in sectores],
        'sexenios': SEXENIOS,
        'ordenes': [{'id': k, 'et': et} for k, et in ORDENES],
        'periodos': periodos,
    }

    return '''<div class="ms" id="msRaiz">
  <section class="ms-arranque" aria-labelledby="msArrTit">
    <p class="ms-kicker">{kicker}</p>
    <h2 class="ms-grande" id="msArrTit">{n} megaobras, obra por obra. Elige una industria y un mandato.</h2>
    <p class="ms-lead">Las {n} obras emblemáticas de 2000 a 2024 costaron <b class="ms-num">{treal}</b> {c_der} frente a <b class="ms-num">{tpresu}</b> aprobados. Los {n_resc} rescates, bancario y carretero, van aparte (<b class="ms-num">{rreal}</b> pagados y debidos {c_der}): son deudas que el Estado asumió, no obras, y los ves en la industria «Rescates». Este es <b>el único filtro de la herramienta</b>: elige industria y presidente, compara las que queden, mira si cada una gana o pierde mientras lees y ponlo junto a cifras que conoces.</p>
    <div class="ms-resumen" id="msResumen" aria-live="polite"></div>
    <ol class="ms-indice" aria-label="Lo que hay en esta página">
      <li><a href="#ms-industria"><span class="ms-n">1</span> Industria</a></li>
      <li><a href="#ms-mandato"><span class="ms-n">2</span> Mandato</a></li>
      <li><a href="#ms-comparativa"><span aria-hidden="true">📊</span> Comparativa</a></li>
      <li><a href="#ms-vivo"><span aria-hidden="true">⏱️</span> Fichas en vivo</a></li>
      <li><a href="#ms-escala"><span aria-hidden="true">⚖️</span> Contra qué se compara</a></li>
    </ol>
  </section>

  <section class="ms-paso" id="ms-industria" aria-labelledby="msP1Tit">
    <div class="ms-paso-cab">
      <h2 class="ms-tit" id="msP1Tit"><span class="ms-n">1</span> Industria</h2>
      <button type="button" class="ms-btn ms-btn-sec ms-todas" data-sector="todos" aria-pressed="true">🌐 Todas las industrias</button>
    </div>
    <p class="ms-txt">Elige un sector estratégico. Industria y mandato filtran a la vez todo lo que sigue: las cifras, la comparativa, las fichas y la escala. La barra dice qué parte del costo real de las obras le toca a cada industria <span id="msMosaicoNota">en los seis mandatos</span>. «Todas las industrias» suma las obras; los rescates se ven solo al elegir su industria.</p>
    <div class="ms-mosaico" role="group" aria-label="Industrias">
      {losetas}
    </div>
  </section>

  <section class="ms-paso" id="ms-mandato" aria-labelledby="msP2Tit">
    <h2 class="ms-tit" id="msP2Tit"><span class="ms-n">2</span> Mandato presidencial</h2>
    <p class="ms-txt">Dentro de la industria elegida, ¿bajo qué gobierno se contrató? El número dice cuántas obras le tocan.</p>
    <div class="ms-mdt-grid" role="group" aria-label="Mandatos">
      {mandatos}
    </div>
  </section>

  <section class="ms-filtro" id="ms-filtro" aria-labelledby="msFiltroTit">
    <div class="ms-filtro-cab">
      <h2 class="ms-tit" id="msFiltroTit"><span aria-hidden="true">🎯</span> Lo que dejó el filtro</h2>
      <div class="ms-fa" id="msFa"></div>
      <div class="ms-filtro-mandos">
        <button type="button" class="ms-btn" id="msContar"><span aria-hidden="true">▶️</span> Contar desde cero</button>
        <button type="button" class="ms-btn ms-btn-sec" id="msQuitar" hidden>✕ Quitar filtros</button>
      </div>
    </div>
    <div class="ms-cifras">
      <div class="ms-cifra"><span class="ms-cifra-l">Costo real del filtro {c_der}</span>
        <span class="ms-cifra-v ms-num" id="msCReal">—</span>
        <span class="ms-cifra-s"><span class="ms-num" id="msCCuota">—</span> del costo real de las {n} obras</span></div>
      <div class="ms-cifra"><span class="ms-cifra-l">Aprobado frente a erogado {c_der}</span>
        <span class="ms-cifra-v ms-num" id="msCPresu">—</span>
        <span class="ms-cifra-s"><span class="ms-num" id="msCBrecha">—</span> de más, un <span class="ms-num" id="msCSob">—</span></span></div>
      <div class="ms-cifra ms-cifra-roja" id="msCPerdCaja"><span class="ms-cifra-l"><span id="msCPerdEt">Pérdida neta del año</span> {c_der}</span>
        <span class="ms-cifra-v ms-num" id="msCPerd">—</span>
        <span class="ms-cifra-s">equivale a <span class="ms-num" id="msCSeg">—</span> por segundo</span></div>
    </div>
    <p class="ms-nota" id="msNotaFiltro"></p>
    <p class="ms-nota">Las tres son sumas de las obras del filtro (<span class="ms-op">costo real = suma de lo erogado; sobrecosto = erogado ÷ aprobado − 1, de modo que cada obra pesa según su tamaño; por segundo = pérdida neta ÷ 31,536,000</span>). La pérdida neta es la misma medida de toda la herramienta: lo que pierden menos lo que ganan, en el año más reciente que publica cada obra; las que no lo publican no se estiman y dicen {c_pend_perd}.</p>
  </section>

  <aside class="ms-aviso">
    <p><strong>🔍 Peritaje multidimensional de inversión pública (ISSAI 100 / CONAC).</strong> La ficha pericial del Tren Maya 2024 se retiró el {tm_fecha}: sus cifras no se habían cotejado con el Tomo VII de la Cuenta Pública 2024 ni con la ASF. Mientras vuelve, lo que la ASF dejó por aclarar está en el expediente del Tren Maya.</p>
    <details class="ms-plegable"><summary>Por qué se retiró la ficha</summary>
      <div class="ms-plegable-cuerpo"><p class="ms-ver-p"><strong>Ficha retirada el {tm_fecha}.</strong> {tm_motivo} {c_tm}</p>
      <p><a class="ms-btn" href="{tm_alt}">Ver lo que la ASF dejó por aclarar en el Tren Maya ➔</a></p></div></details>
  </aside>

  <section class="ms-bloque" id="ms-comparativa" aria-labelledby="msCompTit">
    <h2 class="ms-tit" id="msCompTit"><span aria-hidden="true">📊</span> <span id="msCompTitTx">La comparativa</span></h2>
    <p class="ms-txt" id="msCompSub"></p>
    <div class="ms-ctl">
      <span class="ms-ctl-l">⇅ Ordenar y medir por:</span>
      <div class="ms-ordenes" role="group" aria-label="Criterio">{ordenes}</div>
    </div>
    <div class="ms-mandos">
      <p class="ms-estado" id="msRankEstado" aria-live="polite"></p>
      <div class="ms-mandos-b">
        <button type="button" class="ms-btn" id="msEvaluar"><span aria-hidden="true">▶️</span> Evaluar</button>
        <button type="button" class="ms-btn ms-btn-sec" id="msReiniciar"><span aria-hidden="true">↺</span> Reiniciar a ceros</button>
        <label class="ms-toggle"><input type="checkbox" id="msAuto" checked> <span>Medir en cuanto la lista aparezca</span></label>
        <label class="ms-toggle"><input type="checkbox" id="msUniverso"> <span>Ver las {n} en contexto</span></label>
      </div>
    </div>
    <ol class="ms-filas" id="msFilas"></ol>
    <div id="msCompAviso"></div>
    <p class="ms-nota"><strong>Cómo leer la barra.</strong> Mide el tamaño de la cifra frente a la mayor de la lista, no su dirección. En cronología el orden es por periodo sexenal y la barra sigue midiendo el costo real, para que la escala no cambie de significado a media lista. Pulsa cualquier renglón para ir a su ficha.</p>
  </section>

  <section class="ms-bloque" id="ms-vivo" aria-labelledby="msVivoTit">
    <h2 class="ms-tit" id="msVivoTit"><span aria-hidden="true">⏱️</span> Simulación en vivo: <span id="msVivoTitTx">las fichas del filtro</span></h2>
    <p class="ms-txt">Cada ficha corre con lo que esa obra gana (en verde) o pierde (en rojo) en un año, la misma medida de toda la herramienta. Las que no publican su resultado no corren y dicen por qué.</p>
    <div class="ms-vivo-total">
      <p class="ms-vivo-total-l"><span class="ms-punto" aria-hidden="true"></span> <span id="msVivoTotEt">Lo que estas obras ganan o pierden</span> mientras miras {c_der}</p>
      <p class="ms-vivo-total-v ms-num" id="msVivoTot">+$0.00</p>
      <p class="ms-vivo-total-s" id="msVivoTotSub"></p>
      <div class="ms-ctl ms-ctl-claro">
        <span class="ms-ctl-l">Léelo por:</span>
        <div class="ms-cads" role="group" aria-label="Cadencia">{cadencias}</div>
      </div>
      <p class="ms-vivo-total-s">Por <span id="msCadEt">día</span>: <b class="ms-num" id="msVivoPer">—</b>. Pasarlo a otra cadencia solo cambia la unidad.</p>
      <details class="ms-plegable ms-plegable-claro"><summary><span aria-hidden="true">🧮</span> Cómo se calcula y qué no entra</summary>
        <div class="ms-plegable-cuerpo">
          <div class="ms-tabla-marco"><table class="ms-ver-tabla" id="msVivoTabla"><thead><tr><th>Obra</th><th>Gana o pierde al año</th><th>Por segundo</th></tr></thead><tbody>{tabla_vivo}</tbody></table></div>
          <p class="ms-ver-p">{medida}</p>
          <p class="ms-ver-p">Por segundo = resultado del año × 1,000,000 ÷ 31,536,000 segundos {c_der}. No es dinero que se mueva en este instante: proyecta el resultado de un año sobre el tiempo que llevas mirando.</p>
          <p class="ms-ver-p" id="msVivoParadas" hidden></p>
        </div></details>
    </div>
    <div class="ms-vacio" id="msVacio" hidden></div>
    <div class="ms-fichas" id="msFichas">
{fichas}
    </div>
  </section>

  <section class="ms-bloque" id="ms-escala" aria-labelledby="msEscTit">
    <h2 class="ms-tit" id="msEscTit"><span aria-hidden="true">⚖️</span> Contra qué se compara este dinero</h2>
    <p class="ms-txt" id="msEscSub"></p>
    <ul class="ms-esc-lista" id="msEscLista">{escala}</ul>
    <p class="ms-nota"><strong>Cómo leer esta comparación.</strong> Las veces son una división nuestra: costo real del filtro ÷ cifra de contraste ({c_der}). El costo de las obras es una suma de pesos de años distintos, entre 1988 y 2024, que no están deflactados a un año común; las cifras de contraste son de un solo ejercicio. La comparación sirve para dimensionar el orden de magnitud, no para afirmar una equivalencia exacta de poder adquisitivo. Un peso de 1997 no compra lo mismo que uno de 2026, y esta plataforma prefiere decirlo a ocultarlo.</p>
  </section>

  <aside class="ms-pie">
    <p>Las cifras de las obras salen de la cartera de inversión de Hacienda (Obra Pública Abierta), la Cuenta Pública, el PEF 2026 {r_pef} y los informes de la ASF {r_asf}; cada ficha lleva sus documentos. Lo que todavía nos deben las dependencias está en el <a href="pendientes.html#tema-megaobras">Registro de pendientes</a>. Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>.</p>
  </aside>
  <script type="application/json" id="msDatos">{datos}</script>
</div>'''.format(
        kicker=mo_capitulos.kicker('herramienta-megaobras-sector.html'),
        n=n, treal=sim_mdp(total_real), tpresu=sim_mdp(total_presu), c_der=chip('derivado'),
        n_resc=len(rescates), rreal=sim_mdp(resc_real),
        c_pend_perd=chip('pendiente', PEND_PERDIDA),
        losetas='\n      '.join(losetas), mandatos='\n      '.join(mandatos), ordenes=ordenes, cadencias=cadencias,
        tm_fecha=esc(tm.get('fecha', '10-10-2026')), tm_motivo=esc(tm.get('motivo', '')), tm_alt=esc(tm.get('alternativa', 'expedientes.html#exp-tren-maya')),
        c_tm=chip('pendiente', PEND_FICHA_TM),
        tabla_vivo=tabla_vivo, medida=mo_base.medida_txt(sm),
        fichas=fichas, escala=escala, datos=_json(datos),
        r_pef=ref('ref-pef2026'), r_asf=ref('ref-asf-cp'))
