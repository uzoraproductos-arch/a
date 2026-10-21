# -*- coding: utf-8 -*-
"""Inversion y Megaobras, aplicacion 1: «El pulso del gasto» en pagina
propia (13-10-2026). Sustituye al marco que cargaba la portada entera
(index.html?ir=megaobras&ancla=eb-pulso&visor=1).

Reproduce lo que el motor (audit-engine.js) pinta en el bloque eb-pulso:
la tira de indicadores (renderSimuladorMegaobras), el selector de cadencia
(renderSimuladorPeriodoDial) y el contador en vivo (initLiveLossTicker),
con los mismos parametros:

- Costo real, aprobado, brecha y sobrecosto del conjunto: simAgregados()
  sobre las 13 obras de simulador_megaobras.obras.
- Perdida anual: la que el auditor sustituye en memoria con
  megaobrasOficialBase(): Tren Maya y AIFA por sus estados de actividades
  de la Cuenta Publica 2024 (ingresos de gestion menos gasto total; si el
  resultado es positivo, cero), el FOBAPROA por el Ramo 34 ejercido en
  2024, y las demas obras en cero con la marca de pendiente.
- Cadencias: simulador_megaobras.periodos (factor sobre la perdida anual).
- Por segundo: perdida anual x 1e6 / 31,536,000 (365 dias).

Correcciones frente al motor (AGENTS.md, §2):
- La tira del motor no llevaba chip. Aqui el costo, la brecha, el
  sobrecosto y la perdida son `derivado`, con su operacion.
- El motor decia «subsidio continuo del erario para cubrir el deficit de
  operacion de las 13 obras». Solo 3 de las 13 tienen documento de su
  operacion y una de ellas (AIFA) no registra deficit; el Ramo 34 no es
  deficit de operacion sino apoyo presupuestal al rescate bancario. Aqui
  se dice asi, componente por componente, y las 10 obras sin documento
  llevan chip `pendiente` hacia la ficha reloj-megaobras.
- El costo real del conjunto suma cifras pendientes (FOBAPROA, FARAC,
  AIFA + NAIM, Bunker). Se dice cuanto pesa cada estado en la suma, y el
  lector puede ver el conjunto solo con las cifras que tienen documento.

Desde el 21-10-2026 (pedido del autor) sus cinco partes son capitulos de
Inversion y Megaobras y ya no hay pagina del pulso: las genera
apartados.megaobras_pulso() con subpaginas().
"""
import html
import json
import re
from decimal import Decimal, ROUND_HALF_UP

from presupuesto_modulos import chip
from mo_base import nota_base

ESTILOS = ['mo-pulso.css']
SCRIPTS = ['mo-pulso.js']

SEG_ANO = 365 * 86400
ICONOS = {'dia': '🕐', 'mes': '📅', 'trimestre': '📆', 'semestre': '⏳', 'ano': '🗓️'}
ESTADOS = ('oficial', 'derivado', 'pendiente')


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def esc(t):
    return html.escape(str(t if t is not None else ''), quote=True)


def _r(v, d=0):
    """Math.round del motor (mitades hacia arriba)."""
    q = Decimal(1).scaleb(-d)
    return float(Decimal(repr(v)).quantize(q, rounding=ROUND_HALF_UP))


def _num(v, maxd=3):
    """formatNumber() del motor: separador de miles y hasta 3 decimales."""
    s = format(abs(v), ',.%df' % maxd).rstrip('0').rstrip('.')
    return ('-' if v < 0 else '') + s


def sim_mdp(n):
    """simMdp() del motor: 1 mdp = un millon; 1,000 mdp = mil millones;
    1,000,000 mdp = un billon."""
    a = abs(n)
    if a >= 1e6:
        return '$' + format(n / 1e6, '.2f') + ' billones'
    if a >= 1e3:
        return '$' + _num(_r(n / 100) / 10) + ' mil millones'
    return '$' + _num(_r(n * 100) / 100) + ' millones'


def mdp(v, d=1):
    return ('−' if v < 0 else '') + '$' + format(abs(v), ',.%df' % d) + ' mdp'


def _fuente(f, extra=''):
    if not f:
        return ''
    return '<a href="%s" target="_blank" rel="noopener">%s%s ↗</a>' % (esc(f['url']), esc(f['doc']), esc(extra))


def perdidas(sm):
    """megaobrasOficialBase(): perdida anual documentada de cada obra."""
    of = sm.get('operacion_oficial') or {}
    ob, fu = of.get('obras') or {}, of.get('fuentes') or {}
    vfu = (sm.get('verificacion') or {}).get('fuentes') or {}
    out = {}
    for o in sm['obras']:
        d = ob.get(o['id'])
        if d and o['id'] == 'fobaproa':
            # Decision del autor (17-10-2026): lo que el rescate pierde antes
            # del apoyo del presupuesto, no el Ramo 34 solo.
            out[o['id']] = {'v': -d['resultado_sin_transferencias'], 'e': 'derivado', 'anio': d['anio'], 'tipo': 'rescate',
                            'def': -d['deficit_ejercicio'], 'r34': d['ramo34_ejercido'],
                            'f': fu.get(d['fuente_resultado'])}
        elif d:
            res = d['resultado_sin_transferencias']
            out[o['id']] = {'v': -res if res < 0 else 0, 'e': 'derivado', 'anio': d['anio'], 'tipo': 'empresa',
                            'res': res, 'ing': d['ingresos_gestion'], 'gas': d['gastos_totales'],
                            'transf': d['transferencias'], 'f': fu.get(d['fuente'])}
        else:
            out[o['id']] = {'v': 0, 'e': 'pendiente', 'tipo': 'pendiente'}
    return out


def agregados(obras, perd):
    real = sum(o['inversion_real_mdp'] for o in obras)
    presu = sum(o['inversion_presupuestada_mdp'] for o in obras)
    anual = sum(perd[o['id']]['v'] for o in obras)
    return {'n': len(obras), 'real': real, 'presu': presu, 'brecha': real - presu,
            'sobre': (real / presu - 1) * 100 if presu > 0 else 0,
            'anual': anual, 'seg': anual * 1e6 / SEG_ANO}


def _est(o, campo):
    return (o.get('estado_campos') or {}).get(campo) or 'pendiente'


def _chip_obra(o, campo):
    e = _est(o, campo)
    return chip(e, ('obra-' + o['id']) if e == 'pendiente' else None)


def _contexto(base, ref):
    """Las cifras ya formadas que comparten la pagina y sus partes."""
    sm = base['simulador_megaobras']
    # Decision del autor (17-10-2026): las cifras de conjunto miden las
    # obras; los rescates (FOBAPROA y FARAC) son deudas asumidas y van
    # aparte. La perdida anual si suma los expedientes con documento,
    # rescate bancario incluido, y lo dice componente por componente.
    todas = sm['obras']
    obras = [o for o in todas if o.get('tipo') != 'rescate']
    rescates = [o for o in todas if o.get('tipo') == 'rescate']
    perd = perdidas(sm)
    ag = agregados(obras, perd)
    ag['anual'] = sum(perd[o['id']]['v'] for o in todas)
    ag['seg'] = ag['anual'] * 1e6 / SEG_ANO
    per = sm['periodos']
    ver = sm.get('verificacion') or {}
    vfu = ver.get('fuentes') or {}
    vob = ver.get('obras') or {}

    # Lo documentado: costo real sin pendientes; sobrecosto solo donde las
    # dos puntas (aprobado y erogado) tienen documento.
    doc_real = [o for o in obras if _est(o, 'inversion_real_mdp') != 'pendiente']
    doc_par = [o for o in obras if _est(o, 'inversion_real_mdp') != 'pendiente'
               and _est(o, 'inversion_presupuestada_mdp') != 'pendiente']
    ag_doc_real = agregados(doc_real, perd)
    ag_doc_par = agregados(doc_par, perd)

    comp = {e: sum(o['inversion_real_mdp'] for o in obras if _est(o, 'inversion_real_mdp') == e) for e in ESTADOS}
    comp_n = {e: sum(1 for o in obras if _est(o, 'inversion_real_mdp') == e) for e in ESTADOS}

    documentadas = [o for o in todas if perd[o['id']]['e'] != 'pendiente']
    pendientes_op = [o for o in todas if perd[o['id']]['e'] == 'pendiente']
    verificadas = [o['nombre'].split(' (')[0] for o in obras if o['id'] in vob]
    con_cifra = sum(1 for o in obras if _est(o, 'inversion_real_mdp') != 'pendiente')

    # ---- Componentes de la perdida anual ----
    comps = []
    for o in documentadas:
        p = perd[o['id']]
        nombre = o['nombre'].split(' (')[0]
        if p['tipo'] == 'rescate':
            et = 'Rescate bancario (FOBAPROA / IPAB): pérdida de %d antes del apoyo del presupuesto' % p['anio']
            op = ('Déficit del Fondo FOBAPROA (%s) más las transferencias del Ramo 34 que recibió ese año (%s): lo que el '
                  'rescate pierde antes de que el presupuesto lo cubra. Se cuenta aparte de las obras.' % (mdp(p['def']), mdp(p['r34'])))
        elif p['v'] > 0:
            et = '%s: déficit de operación %d' % (nombre, p['anio'])
            op = 'Ingresos por sus servicios (%s) menos gasto total (%s), de su estado de actividades: %s antes de transferencias.' % (
                mdp(p['ing']), mdp(p['gas']), mdp(p['res']))
        else:
            et = '%s: sin déficit de operación en %d' % (nombre, p['anio'])
            op = 'Ingresos por sus servicios (%s) menos gasto total (%s) da %s a favor: no registra déficit antes de transferencias, así que suma cero. Recibió además %s de transferencias federales.' % (
                mdp(p['ing']), mdp(p['gas']), mdp(p['res']), mdp(p['transf']))
        comps.append({'id': o['id'], 'ico': o['icono'], 'et': et, 'v': p['v'], 'e': p['e'], 'op': op,
                      'f': p['f']['doc'] if p['f'] else '', 'u': p['f']['url'] if p['f'] else ''})

    # ---- Obras, para la composicion y la tabla ----
    filas = []
    for o in sorted(obras, key=lambda x: -x['inversion_real_mdp']):
        v = vob.get(o['id']) or {}
        f0 = vfu.get((v.get('fuentes') or [None])[0])
        filas.append({'id': o['id'], 'ico': o['icono'], 'n': o['nombre'], 'pres': o['presidente'], 'per': o['periodo_sexenal'],
                      'sec': o['sector_id'], 'real': o['inversion_real_mdp'], 'presu': o['inversion_presupuestada_mdp'],
                      'sobre': o['sobrecosto_pct'], 'er': _est(o, 'inversion_real_mdp'), 'ep': _est(o, 'inversion_presupuestada_mdp'),
                      'es': _est(o, 'sobrecosto_pct'), 'perd': perd[o['id']]['v'], 'epd': perd[o['id']]['e'],
                      'f': f0['doc'] if f0 else '', 'u': f0['url'] if f0 else ''})

    actual = 'dia'
    p0 = per[actual]

    # ---- Selector de cadencias ----
    dial = ''.join(
        '<button type="button" class="mp-dial-b" data-per="%s" aria-pressed="%s">'
        '<span class="mp-dial-ico" aria-hidden="true">%s</span><span class="mp-dial-et">%s</span>'
        '<span class="mp-dial-cif mp-num">%s</span><span class="mp-dial-suf">%s</span></button>'
        % (k, 'true' if k == actual else 'false', ICONOS.get(k, '⏱️'), esc(p['label']), sim_mdp(ag['anual'] * p['factor']), esc(p['sufijo']))
        for k, p in per.items())

    comp_filas = ''.join(
        '<tr data-v="%r"><th scope="row"><span aria-hidden="true">%s</span> %s <small class="mp-op">%s %s</small></th>'
        '<td class="mp-num mp-c-v">%s</td><td>%s</td></tr>'
        % (c['v'], c['ico'], esc(c['et']), esc(c['op']), ('<a href="%s" target="_blank" rel="noopener">%s ↗</a>' % (esc(c['u']), esc(c['f']))) if c['u'] else '',
           sim_mdp(c['v'] * p0['factor']) + esc(p0['sufijo']), chip(c['e']))
        for c in comps)

    pend_lista = ', '.join(esc(o['nombre'].split(' (')[0]) for o in pendientes_op)

    # ---- Barra de composicion del costo ----
    seg = ''.join('<span class="mp-comp-seg mp-seg-%s" style="width:%.2f%%" title="%s: %s"></span>'
                  % (e, comp[e] / ag['real'] * 100, e, sim_mdp(comp[e])) for e in ESTADOS if comp[e] > 0)
    leyenda = ''.join('<li><span class="mp-ley mp-seg-%s" aria-hidden="true"></span>%s <b class="mp-num">%s</b> '
                      '<span class="mp-gris">(%s%% · %d %s)</span></li>'
                      % (e, chip(e),
                         sim_mdp(comp[e]), format(comp[e] / ag['real'] * 100, '.1f'), comp_n[e], 'obra' if comp_n[e] == 1 else 'obras')
                      for e in ESTADOS)

    datos = {
        'periodos': per, 'iconos': ICONOS, 'anual': ag['anual'], 'seg': ag['seg'],
        'comps': [{'id': c['id'], 'v': c['v']} for c in comps],
        'modos': {
            'todo': {'n': ag['n'], 'real': ag['real'], 'presu': ag['presu'], 'brecha': ag['brecha'], 'sobre': ag['sobre'],
                     'nReal': ag['n'], 'nPar': ag['n']},
            'doc': {'n': ag_doc_real['n'], 'real': ag_doc_real['real'], 'presu': ag_doc_par['presu'],
                    'realPar': ag_doc_par['real'], 'brecha': ag_doc_par['brecha'], 'sobre': ag_doc_par['sobre'],
                    'nReal': ag_doc_real['n'], 'nPar': ag_doc_par['n']},
        },
        'obras': filas,
    }

    sobre_txt = ('+' if ag['sobre'] > 0 else '') + format(ag['sobre'], '.1f') + '%'

    # Ya no quedan costos pendientes (17-10-2026): el aviso dice entonces lo
    # que mas mueve el total: las obras con rango.
    con_rango = [o for o in obras if 'inversion_real_mdp' in (o.get('rangos_campos') or {})]
    if comp['pendiente'] > 0:
        aviso = ('<b>Ojo:</b> %s%% del costo real del conjunto (%s) son cifras que siguen <b>pendientes</b> de documento %s. '
                 'La suma se puede hacer, pero no se puede afirmar como dato auditado: <a href="%s">mira de qué está hecha</a> '
                 'o pulsa «Solo con documento».' % (format(comp['pendiente'] / ag['real'] * 100, '.1f'), sim_mdp(comp['pendiente']),
                                                     chip('pendiente'), parte_archivo('composicion')))
        compo_cif = '%s%% del costo sigue pendiente de documento' % format(comp['pendiente'] / ag['real'] * 100, '.1f')
    else:
        aviso = ('<b>Ojo:</b> las %d obras ya tienen su costo con documento, oficial o derivado de cifras oficiales. %s %s su '
                 'costo como rango: en la suma entra su punto medio. <a href="%s">Mira la cuenta de cada obra</a>.'
                 % (ag['n'], esc(', '.join(o['nombre'].split(' (')[0] for o in con_rango)),
                    'tiene' if len(con_rango) == 1 else 'tienen', parte_archivo('cuenta')))
        compo_cif = '%d de %d obras con costo documentado' % (ag['n'] - comp_n['pendiente'], ag['n'])

    # ---- Los rescates, aparte ----
    ag_r = agregados(rescates, perd)
    resc_filas = ''.join(
        '<tr><th scope="row"><span aria-hidden="true">%s</span> %s <small class="mp-op">%s: %s frente a %s. %s</small></th>'
        '<td class="mp-num">%s</td><td>%s</td></tr>'
        % (o['icono'], esc(o['nombre']), esc(o.get('sobrecosto_etiqueta') or 'Crecimiento'),
           ('+' if o['sobrecosto_pct'] > 0 else '') + format(o['sobrecosto_pct'], '.1f') + ' %', sim_mdp(o['inversion_presupuestada_mdp']),
           esc(o['presidente'] + ', ' + o['periodo_sexenal']), mdp(o['inversion_real_mdp']), _chip_obra(o, 'inversion_real_mdp'))
        for o in rescates)
    rescates_html = (
        '<div class="mp-rescates">'
        '<h3 class="mp-sub"><span aria-hidden="true">🏦</span> Aparte: los %d rescates</h3>'
        '<p class="mp-txt">%s no son obras: son deudas que el Estado asumió para salvar a bancos y a concesionarios de '
        'autopistas. Lo que han costado mezcla pagos de décadas con lo que todavía se debe, en pesos de años distintos, así '
        'que su crecimiento no se compara con el sobrecosto de una obra y no entra en las cuatro cifras de arriba. Juntos '
        'comprometen <b class="mp-num">%s</b> %s frente a %s que se presentaron en su momento. Lo que el rescate bancario '
        'pierde cada año sí entra en el contador, porque se sigue pagando hoy.</p>'
        '<div class="mp-marco"><table class="mp-tabla"><caption class="sr-only">Los rescates, aparte de las obras</caption>'
        '<thead><tr><th scope="col">Rescate</th><th scope="col">Pagado y debido</th><th scope="col">Estado</th></tr></thead>'
        '<tbody>%s</tbody></table></div>'
        '<p class="mp-unidades">Las %d obras y los %d rescates juntos sumarían %s. <a href="%s">La cuenta de cada rescate</a> '
        'dice de qué está hecha cada cifra.</p></div>'
        % (len(rescates), esc(' y '.join(o['nombre'].split(' (')[0] for o in rescates)), sim_mdp(ag_r['real']), chip('derivado'),
           sim_mdp(ag_r['presu']), resc_filas, ag['n'], len(rescates), sim_mdp(ag['real'] + ag_r['real']), parte_archivo('cuenta')))

    return dict(
        n=ag['n'], n_doc=ag_doc_real['n'],
        seg_txt=format(_r(ag['seg'], 2), ',.2f'), anual=mdp(ag['anual']),
        chip_der=chip('derivado'), chip_of=chip('oficial'), chip_pend=chip('pendiente', 'reloj-megaobras'),
        chip_pend_obra=chip('pendiente'), chip_unit=chip('pendiente', 'costo-unitario-megaobras'),
        real=sim_mdp(ag['real']), real_mdp=mdp(ag['real']),
        per_label=esc(p0['label']), per_v=sim_mdp(ag['anual'] * p0['factor']) + esc(p0['sufijo']),
        per_mdp=mdp(ag['anual'] * p0['factor'], 2) + esc(p0['sufijo']), per_suf=esc(p0['sufijo']),
        factor_tx='1/365', n_op=len(documentadas), n_pend=len(pendientes_op),
        sobre=sobre_txt, presu=sim_mdp(ag['presu']),
        brecha=sim_mdp(ag['brecha']), brecha_mdp=mdp(ag['brecha']),
        dial=dial, comp_filas=comp_filas, pend_lista=pend_lista, seg=seg, leyenda=leyenda,
        anio_op=next((perd[o['id']]['anio'] for o in documentadas), ''),
        n_ver=len(verificadas), verificadas=esc(', '.join(verificadas)), con_cifra=con_cifra,
        f_cp=_fuente(vfu.get('cp')), f_opa=_fuente(vfu.get('opa')),
        f_tm=_fuente((sm['operacion_oficial']['fuentes']).get('ef_h0m')),
        f_ai=_fuente((sm['operacion_oficial']['fuentes']).get('ef_hzi')),
        f_ipab=_fuente((sm['operacion_oficial']['fuentes']).get('ipab_ef25')),
        r_asf=ref('ref-asf-cp'), datos=_json(datos), aviso=aviso, compo_cif=compo_cif,
        rescates_html=rescates_html, n_resc=len(rescates), n_tot=len(todas), resc_real=sim_mdp(ag_r['real']),
        rangos_lista=esc('; '.join('%s (%s)' % (o['nombre'].split(' (')[0], ', '.join(
            {'inversion_presupuestada_mdp': 'presupuesto', 'inversion_real_mdp': 'costo', 'sobrecosto_pct': 'sobrecosto'}[k]
            for k in o['rangos_campos'])) for o in obras if o.get('rangos_campos'))),
        cuenta_html=_cuenta_html(sm), res_txt=mdp(sum(f['v'] for _o, f in _resultados(sm))))


SECCIONES = {
    'cifras': '''  <section class="mp-sec" id="mpCifras" aria-labelledby="mpCifTit">
    <div class="mp-cab">
      <h2 class="mp-tit" id="mpCifTit"><span aria-hidden="true">🧭</span> Las cuatro cifras de referencia</h2>
      <div class="mp-modo" role="group" aria-label="Qué cifras sumar">
        <button type="button" class="mp-modo-b" data-modo="todo" aria-pressed="true">Todo lo registrado <small>{n} obras</small></button>
        <button type="button" class="mp-modo-b" data-modo="doc" aria-pressed="false">Solo con documento <small>{n_doc} obras</small></button>
      </div>
    </div>
    <p class="mp-txt" id="mpModoTx">Miden <b>siempre el universo completo</b> de las obras evaluadas: es la cifra contra la que se lee todo lo demás. Con «Solo con documento» dejas fuera las cifras que siguen pendientes.</p>
    <div class="mp-kpis">
      <article class="mp-kpi">
        <p class="mp-kpi-et"><span aria-hidden="true">🏗️</span> Costo real erogado</p>
        <p class="mp-kpi-v mp-num" id="mpKReal">{real}</p>
        <p class="mp-kpi-sub"><span id="mpKRealSub">Suma de las {n} obras evaluadas entre 2000 y 2024, sin los rescates</span> {chip_der} {r_asf}</p>
        <p class="mp-kpi-mdp mp-num" id="mpKRealMdp">{real_mdp}</p>
      </article>
      <article class="mp-kpi mp-kpi-alerta">
        <p class="mp-kpi-et"><span class="mp-punto" aria-hidden="true"></span> Pérdida anual <span id="mpKPerEt">({per_label})</span></p>
        <p class="mp-kpi-v mp-num" id="mpKPer">{per_v}</p>
        <p class="mp-kpi-sub">Déficit de operación documentado de las obras y pérdida del rescate bancario antes del apoyo del presupuesto: {n_op} de {n_tot} expedientes con documento {chip_der}. Los otros {n_pend} no tienen documento de su operación {chip_pend}</p>
        <p class="mp-kpi-mdp mp-num" id="mpKPerMdp">{per_mdp}</p>
      </article>
      <article class="mp-kpi">
        <p class="mp-kpi-et"><span aria-hidden="true">📈</span> Sobrecosto del conjunto</p>
        <p class="mp-kpi-v mp-num mp-ambar" id="mpKSobre">{sobre}</p>
        <p class="mp-kpi-sub"><span id="mpKSobreSub">{presu} aprobados frente a {real} erogados</span> {chip_der}</p>
        <p class="mp-kpi-mdp mp-num" id="mpKSobreOp">(erogado ÷ aprobado − 1) × 100</p>
      </article>
      <article class="mp-kpi">
        <p class="mp-kpi-et"><span aria-hidden="true">💸</span> Pesos de más</p>
        <p class="mp-kpi-v mp-num" id="mpKBrecha">{brecha}</p>
        <p class="mp-kpi-sub"><span id="mpKBrechaSub">Erogado menos aprobado, sumando las {n} obras</span> {chip_der}</p>
        <p class="mp-kpi-mdp mp-num" id="mpKBrechaMdp">{brecha_mdp}</p>
      </article>
    </div>
    <p class="mp-aviso" id="mpAvisoPend">{aviso}</p>
    {rescates_html}
  </section>''',
    'ritmo': '''  <section class="mp-sec" id="mpRitmo" aria-labelledby="mpRitTit">
    <h2 class="mp-tit" id="mpRitTit"><span aria-hidden="true">⏱️</span> Temporalidad de pérdidas y subsidios</h2>
    <p class="mp-txt">La misma cifra anual, repartida en cinco cadencias. Elige el ritmo con el que quieres leerla: cada botón dice su cifra antes de pulsarlo.</p>
    <div class="mp-dial" role="group" aria-label="Cadencia">{dial}</div>
    <div class="mp-marco">
      <table class="mp-tabla" id="mpComps">
        <caption>De qué está hecha la cifra <span id="mpCompsEt">{per_suf}</span></caption>
        <thead><tr><th scope="col">Componente</th><th scope="col">Monto</th><th scope="col">Estado</th></tr></thead>
        <tbody>{comp_filas}
          <tr class="mp-pend-fila"><th scope="row"><span aria-hidden="true">❔</span> Los otros {n_pend} expedientes <small class="mp-op">{pend_lista}. Ningún documento oficial cotejado dice cuánto cuesta operarlas ni cuánto ingresan: no se estiman y quedan fuera de la suma, lo que no quiere decir que cuesten cero. Qué falta y a quién le toca publicarlo está en el Registro de pendientes.</small></th>
            <td class="mp-num">sin cifra</td><td>{chip_pend}</td></tr>
        </tbody>
        <tfoot><tr><th scope="row">Total documentado <small class="mp-op">Suma de los componentes de arriba × <span id="mpFactorTx">{factor_tx}</span></small></th><td class="mp-num" id="mpCompsTot">{per_v}</td><td>{chip_der}</td></tr></tfoot>
      </table>
    </div>
    <p class="mp-equiv" id="mpEquiv" aria-live="polite"></p>
  </section>''',
    'composicion': '''  <section class="mp-sec" id="mpCompo" aria-labelledby="mpCompTit">
    <h2 class="mp-tit" id="mpCompTit"><span aria-hidden="true">🧩</span> De qué está hecho el costo real</h2>
    <p class="mp-txt">Los {real} de las {n} obras, según el estado de la cifra de cada una. Los {n_resc} rescates ({resc_real}) van aparte: están en <a href="herramienta-megaobras-pulso-cifras.html">las cuatro cifras</a> y en <a href="herramienta-megaobras-pulso-cuenta.html">la cuenta de cada obra</a>. Una sola obra puede mover el total entero: compara la barra antes de concluir.</p>
    <div class="mp-comp" role="img" aria-label="Composición del costo real por estado de la cifra">{seg}</div>
    <ul class="mp-leyenda">{leyenda}</ul>
    <div class="mp-orden" role="group" aria-label="Ordenar las obras">
      <span class="mp-orden-et">Ordena por:</span>
      <button type="button" class="mp-orden-b" data-orden="real" aria-pressed="true">Costo real</button>
      <button type="button" class="mp-orden-b" data-orden="sobre" aria-pressed="false">Sobrecosto</button>
      <button type="button" class="mp-orden-b" data-orden="brecha" aria-pressed="false">Pesos de más</button>
      <button type="button" class="mp-orden-b" data-orden="perd" aria-pressed="false">Pérdida anual</button>
    </div>
    <ol class="mp-obras" id="mpObras"></ol>
    <p class="mp-acciones">
      <button type="button" class="mp-boton mp-sec-b" id="mpCsv"><span aria-hidden="true">⬇️</span> Descarga las {n} obras (CSV)</button>
      <a class="mp-boton mp-sec-b" href="herramienta-megaobras-sector.html"><span aria-hidden="true">🏭</span> Ficha de cada obra, por sector</a>
    </p>
    <p class="mp-unidades"><b>Unidades.</b> 1 mdp es un millón de pesos; 1,000 mdp son mil millones; 1,000,000 mdp, un billón. Las cifras son nominales del año de cada erogación, sin deflactar: un peso de 1997 no compra lo mismo que uno de 2026.</p>
  </section>''',
    'cuenta': '{cuenta_html}',
    'calculo': '''  <section class="mp-sec mp-como" id="mpComo" aria-labelledby="mpComoTit">
    <h2 class="mp-tit" id="mpComoTit"><span aria-hidden="true">🔎</span> Cómo se calcula lo que ves</h2>
    <ul class="mp-lista">
      <li><b>Los agregados se suman, no se escriben.</b> El costo real, lo aprobado y la brecha son la suma obra por obra de las {n} obras evaluadas {chip_der}; la pérdida anual suma además el rescate bancario.</li>
      <li><b>Los rescates, aparte.</b> El FOBAPROA y el FARAC son deudas que el Estado asumió, no obras: lo que han costado mezcla pagos de décadas con saldos de hoy, en pesos sin deflactar. Por eso no entran en el costo ni en el sobrecosto del conjunto; tienen su propio bloque, y su «sobrecosto» se llama crecimiento frente a lo que se presentó en su momento.</li>
      <li><b>La pérdida anual.</b> Tren Maya y AIFA, por sus estados de actividades de la Cuenta Pública {anio_op}: ingresos por sus servicios menos gasto total, antes de transferencias {chip_der}; si el resultado queda a favor, cuenta cero. El rescate bancario, por lo que el Fondo FOBAPROA pierde antes del apoyo del presupuesto: su déficit de {anio_op} más las transferencias del Ramo 34 que recibió ese año, según los estados financieros dictaminados del IPAB {chip_der}. El Ramo 34 solo es el apoyo, no la pérdida. {n_pend} expedientes no tienen documento de su operación y no se estiman {chip_pend}.</li>
      <li><b>Las cadencias.</b> La cifra anual multiplicada por 1/365 (día), 1/12 (mes), 1/4 (trimestre) o 1/2 (semestre).</li>
      <li><b>La pérdida por segundo.</b> La cifra anual entre los 31,536,000 segundos de un año de 365 días. El contador en vivo no mide un gasto que ocurra en ese instante: proyecta el ritmo anual sobre el tiempo que llevas mirando.</li>
      <li><b>El sobrecosto del conjunto.</b> Compara la inversión real total contra la aprobada total, de modo que cada obra pesa según su tamaño. No es el promedio simple de los porcentajes, que trataría igual a una refinería y a una estela.</li>
      <li><b>Cifras con documento.</b> De las {n} obras, {n_ver} ya tienen documentos oficiales cotejados ({verificadas}) y {con_cifra} tienen su costo anclado a un documento oficial (la cartera de Hacienda, la Cuenta Pública o un informe de la ASF). La pérdida anual ya tiene documento en {n_op} obras; en las demás, la pérdida, los costos de operación y el costo unitario siguen pendientes y no se estiman {chip_unit}.</li>
      <li><b>Los rangos.</b> Cuando la cifra exacta no está publicada pero documentos oficiales la acotan por arriba y por abajo, la suma usa su punto medio, (mínimo + máximo) ÷ 2, y la obra dice sus dos cotas y de dónde sale cada una {chip_der}. Hoy entran así: {rangos_lista}. La cifra exacta se sigue debiendo y queda en el Registro de pendientes.</li>
      <li><b>La cuenta de cada obra.</b> Ingresos esperados y reales, gasto de operación, intereses y ganancia o pérdida del año, renglón por renglón, con su operación y su documento: <a href="herramienta-megaobras-pulso-cuenta.html">La cuenta de cada obra</a>.</li>
      <li><b>Pendiente declarado.</b> Las cifras marcadas como pendientes no tienen todavía el documento oficial que las sustenta; se muestran como consolidación documental y no como dato auditado. Qué falta y a quién le toca publicarlo está en el <a href="pendientes.html#tema-megaobras">Registro de pendientes</a>.</li>
    </ul>
    <p class="mp-fuentes">Fuentes: {f_cp}; {f_tm}; {f_ai}; {f_ipab}; {f_opa}; y la ASF {r_asf}.</p>
  </section>''',
}

DATOS = '''  <script type="application/json" id="mpDatos">{datos}</script>'''


# ---- La cuenta de cada obra (17-10-2026) ----
# simulador_megaobras.cuenta: renglones con estado oficial, derivado (si trae
# min y max es un rango), pendiente (con responsable) o no_aplica.
UNIDAD = {'mdp': lambda v: mdp(v), 'pesos': lambda v: '$' + format(v, ',.2f'),
          'personas': lambda v: format(int(round(v)), ','), 'mbd': lambda v: format(v, ',.0f') + ' mil barriles diarios',
          'musd': lambda v: format(v, ',.1f') + ' millones de dólares'}


def _v(f):
    fmt = UNIDAD.get(f.get('u'), UNIDAD['mdp'])
    if 'min' in f:
        return 'entre %s y %s; punto medio %s' % (fmt(f['min']), fmt(f['max']), fmt(f['medio']))
    return fmt(f['v'])


def _rango_txt(o, campo, fmt):
    r = (o.get('rangos_campos') or {}).get(campo)
    return ('entre %s y %s; punto medio' % (fmt(r['min']), fmt(r['max']))) if r else ''


def _resultados(sm):
    """El resultado documentado mas reciente de cada obra (sin el resultado
    sin transferencias ni los acumulados)."""
    out = []
    obras = {o['id']: o for o in sm['obras']}
    for oid, filas in ((sm.get('cuenta') or {}).get('obras') or {}).items():
        r = [f for f in filas if f['c'] == 'resultado_anual_mdp' and 'v' in f]
        if r:
            out.append((obras[oid], max(r, key=lambda x: x.get('anio') or 0)))
    return out


def _intereses(sm):
    obras = {o['id']: o for o in sm['obras']}
    return [(obras[oid], f) for oid, filas in ((sm.get('cuenta') or {}).get('obras') or {}).items()
            for f in filas if f['c'] == 'intereses_anuales_mdp' and 'v' in f]


def _fuentes_fila(f):
    return ' · '.join('<a href="%s" target="_blank" rel="noopener">%s%s ↗</a>'
                      % (esc(x['url']), esc(x['doc'] if len(x['doc']) < 110 else x['doc'][:108] + '…'),
                         (', ' + ('' if re.match(r'pp?\. ', x['pag']) else 'p. ') + esc(x['pag'])) if x.get('pag') else '')
                      for x in f.get('f') or [])


def _estado(f, oid):
    if f['e'] == 'no_aplica':
        return '<span class="mp-na">no aplica</span>'
    return chip(f['e'], ('cuenta-' + oid) if f['e'] == 'pendiente' else None)


def _signo(v):
    return ' mp-neg' if v < 0 else ''


CUENTA_INTRO = '''  <section class="mp-sec" id="mpCuenta" aria-labelledby="mpCuentaTit">
    <h2 class="mp-tit" id="mpCuentaTit"><span aria-hidden="true">📒</span> La cuenta de cada obra</h2>
    <p class="mp-txt">Para cada obra, lo que se esperaba de ella y lo que dio: su presupuesto, cuánto costó, cuánto esperaba ingresar y cuánto ingresa, cuánto gasta en operar, cuánto paga de intereses y si gana o pierde en el año. Donde no hay cifra exacta pero sí documentos que la acotan, va un <b>rango</b> con su mínimo, su máximo y su punto medio. Donde ni eso se puede, el renglón dice <b>por qué falta y a quién le toca publicarlo</b>. Y si una obra no tiene ese concepto (un monumento no vende boletos; una obra pagada con impuestos no paga intereses), dice «no aplica».</p>
    <p class="mp-unidades"><b>Unidades.</b> Millones de pesos (mdp) del año que dice cada renglón, sin deflactar. Una pérdida va con signo menos.</p>
'''


def _cuenta_html(sm):
    cu = (sm.get('cuenta') or {}).get('obras') or {}
    res, intr = _resultados(sm), _intereses(sm)
    tot = sum(f['v'] for _o, f in res)
    filas_res = ''.join(
        '<tr><th scope="row"><span aria-hidden="true">%s</span> %s <small class="mp-op">%s (%s)</small></th>'
        '<td class="mp-num%s">%s</td><td>%s</td></tr>'
        % (o['icono'], esc(o['nombre'].split(' (')[0]), esc(f['et']), f.get('anio') or '', _signo(f['v']),
           mdp(f['v']), chip(f['e'])) for o, f in sorted(res, key=lambda x: x[1]['v']))
    filas_int = ''.join(
        '<tr><th scope="row"><span aria-hidden="true">%s</span> %s <small class="mp-op">%s (%s)</small></th>'
        '<td class="mp-num">%s</td><td>%s</td></tr>'
        % (o['icono'], esc(o['nombre'].split(' (')[0]), esc(f['et']), f.get('anio') or '', mdp(f['v']), chip(f['e']))
        for o, f in sorted(intr, key=lambda x: -x[1]['v']))
    anios = sorted({f.get('anio') for _o, f in res if f.get('anio')})
    resumen = (
        '<div class="mp-marco"><table class="mp-tabla">'
        '<caption>Ganancia o pérdida del año, donde hay documento</caption>'
        '<thead><tr><th scope="col">Obra</th><th scope="col">Resultado</th><th scope="col">Estado</th></tr></thead>'
        '<tbody>%s</tbody><tfoot><tr><th scope="row">Suma de los resultados documentados <small class="mp-op">Suma de los %d '
        'renglones de arriba, cada obra con su año más reciente publicado (%s). Las demás no publican su resultado o no operan: '
        'su ficha dice por qué.</small></th><td class="mp-num%s">%s</td><td>%s</td></tr></tfoot></table></div>'
        '<div class="mp-marco"><table class="mp-tabla">'
        '<caption>Intereses que pagan al año, donde hay documento</caption>'
        '<thead><tr><th scope="col">Obra</th><th scope="col">Intereses</th><th scope="col">Estado</th></tr></thead>'
        '<tbody>%s</tbody></table></div>'
        % (filas_res, len(res), ', '.join(str(a) for a in anios), _signo(tot), mdp(tot), chip('derivado'), filas_int))

    def pct(v):
        return ('+' if v > 0 else '') + format(v, '.1f') + ' %'

    fichas = []
    for o in sm['obras']:
        ec = o.get('estado_campos') or {}
        base = []
        for campo, et, fmt in (('inversion_presupuestada_mdp', 'Presupuesto con el que se mide', mdp),
                               ('inversion_real_mdp', 'Costo real', mdp),
                               ('sobrecosto_pct', o.get('sobrecosto_etiqueta') or 'Sobrecosto', pct)):
            e = ec.get(campo) or 'pendiente'
            base.append('<div><dt>%s</dt><dd><span class="mp-num">%s %s</span> %s</dd></div>'
                        % (et, _rango_txt(o, campo, fmt), fmt(o[campo]), chip(e, ('obra-' + o['id']) if e == 'pendiente' else None)))
        cuerpo = []
        for f in cu.get(o['id']) or []:
            et = esc(f['et']) + (' (%s)' % f['anio'] if f.get('anio') and f['e'] in ('oficial', 'derivado') else '')
            txt = ''
            if f['e'] == 'pendiente':
                txt += '<b>Por qué falta:</b> ' + esc(f['resp']) + ' '
            elif f.get('op'):
                txt += esc(f['op']) + ' '
            if f.get('nota'):
                txt += esc(f['nota']) + ' '
            monto = _v(f) if f['e'] in ('oficial', 'derivado') else ('sin cifra' if f['e'] == 'pendiente' else '—')
            cuerpo.append('<tr><th scope="row">%s<small class="mp-op">%s%s</small></th><td class="mp-num%s">%s</td><td>%s</td></tr>'
                          % (et, txt, _fuentes_fila(f), _signo(f.get('v', 0)), monto, _estado(f, o['id'])))
        fichas.append(
            '<article class="mp-cta" id="cuenta-%s" aria-labelledby="cuenta-%s-t">'
            '<h3 class="mp-cta-tit" id="cuenta-%s-t"><span aria-hidden="true">%s</span> %s <small>%s · %s</small></h3>'
            '<dl class="mp-cta-base">%s</dl>%s'
            '<div class="mp-marco"><table class="mp-tabla"><caption class="sr-only">La cuenta de %s</caption>'
            '<thead><tr><th scope="col">Concepto</th><th scope="col">Monto</th><th scope="col">Estado</th></tr></thead>'
            '<tbody>%s</tbody></table></div>'
            '<p class="mp-cta-pie"><a href="herramienta-megaobras-sector.html#obra-%s">Ficha completa de la obra, por sector</a></p></article>'
            % (o['id'], o['id'], o['id'], o['icono'], esc(o['nombre']), esc(o['presidente']), esc(o['periodo_sexenal']),
               ''.join(base), nota_base(o, cu.get(o['id']), 'mp-base'), esc(o['nombre']), ''.join(cuerpo) or '<tr><td colspan="3">Sin renglones.</td></tr>', o['id']))

    indice = ''.join('<li><a href="#cuenta-%s"><span aria-hidden="true">%s</span> %s</a></li>'
                     % (o['id'], o['icono'], esc(o['nombre'].split(' (')[0])) for o in sm['obras'])
    return (CUENTA_INTRO + '    ' + resumen + '\n    <nav class="mp-cta-indice" aria-label="Ir a una obra"><ol>' + indice +
            '</ol></nav>\n    ' + '\n    '.join(fichas) + '\n  </section>')

# Las partes del pulso, cada una en su pagina (pedido del autor,
# 17-10-2026; la quinta, la cuenta de cada obra, el mismo dia). Desde el
# 21-10-2026 son capitulos de Inversion y Megaobras (mo_capitulos.py): ya no
# hay pagina del pulso con su contador y sus tarjetas, ni la fila de partes
# arriba y abajo; el pie de cada una va de capitulo en capitulo.
PAGINA = 'herramienta-megaobras-pulso.html'
PARTES = [
    ('cifras', '🧭', 'Las cuatro cifras', 'Las cuatro cifras de referencia',
     'Costo real erogado, pérdida y apoyo anual, sobrecosto del conjunto y pesos de más, con «todo lo registrado» o «solo con documento».',
     '{real} de costo real · {sobre} de sobrecosto'),
    ('ritmo', '⏱️', 'El ritmo', 'Temporalidad de pérdidas y subsidios',
     'La pérdida y el apoyo anual documentados, repartidos por día, mes, trimestre, semestre o año, componente por componente.',
     '{per_v} de pérdida y apoyo documentados'),
    ('composicion', '🧩', 'De qué está hecho el total', 'De qué está hecho el costo real',
     'Cuánto del costo real tiene documento oficial y cuánto sigue pendiente, y las {n} obras ordenadas por costo, sobrecosto, pesos de más o pérdida.',
     '{compo_cif}'),
    ('cuenta', '📒', 'La cuenta de cada obra', 'La cuenta de cada obra',
     'Lo que se esperaba de cada obra y lo que dio: presupuesto, ingresos esperados y reales, gasto de operación, intereses y ganancia o pérdida del año.',
     '{res_txt} de resultado documentado al año'),
    ('calculo', '🔎', 'Cómo se calcula', 'Cómo se calcula lo que ves',
     'Las reglas de cada suma, división y cadencia, qué cifras tienen documento y las fuentes oficiales de donde salen.',
     'Las operaciones y sus fuentes, paso a paso'),
]


def parte_archivo(slug):
    return PAGINA[:-5] + '-' + slug + '.html'


def subpaginas(base, ref):
    """Las partes, para apartados.insp_subpaginas(): cada una con su
    seccion, la navegacion entre partes y los datos que usa mo-pulso.js."""
    c = _contexto(base, ref)
    out = []
    for slug, ico, nombre, tit, desc, _cif in PARTES:
        bloque = '\n\n'.join(['<div class="mp mp-parte" id="mpRaiz">', SECCIONES[slug].format(**c),
                               DATOS.format(**c)]) + '\n</div>'
        out.append({'archivo': parte_archivo(slug), 'icono': ico, 'menu': nombre, 'titulo': tit,
                    'entrada': '<b>%s.</b> %s' % (esc(nombre), esc(desc.format(**c))), 'bloque': bloque})
    return out
