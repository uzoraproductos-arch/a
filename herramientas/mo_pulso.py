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

Lo llama apartados.insp_nativa() (INSP_NATIVAS['pulso']).
"""
import html
import json
from decimal import Decimal, ROUND_HALF_UP

from presupuesto_modulos import chip

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
            out[o['id']] = {'v': d['ramo34_ejercido'], 'e': 'oficial', 'anio': d['anio'], 'tipo': 'ramo34',
                            'f': vfu.get(d['fuente']) or vfu.get('cp')}
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
    """Las cifras ya formadas que comparten la pagina y sus cuatro partes."""
    sm = base['simulador_megaobras']
    obras = sm['obras']
    perd = perdidas(sm)
    ag = agregados(obras, perd)
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

    documentadas = [o for o in obras if perd[o['id']]['e'] != 'pendiente']
    pendientes_op = [o for o in obras if perd[o['id']]['e'] == 'pendiente']
    verificadas = [o['nombre'].split(' (')[0] for o in obras if o['id'] in vob]
    con_cifra = sum(1 for o in obras if _est(o, 'inversion_real_mdp') != 'pendiente')

    # ---- Componentes de la perdida anual ----
    comps = []
    for o in documentadas:
        p = perd[o['id']]
        nombre = o['nombre'].split(' (')[0]
        if p['tipo'] == 'ramo34':
            et = 'Rescate bancario (FOBAPROA / IPAB): Ramo 34 ejercido en %d' % p['anio']
            op = 'Apoyo presupuestal a ahorradores y deudores de la banca, tal como lo publica la Cuenta Pública. No es déficit de operación: es lo que el rescate le sigue costando al presupuesto cada año.'
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
        pend_pct=format(comp['pendiente'] / ag['real'] * 100, '.1f'), pend_v=sim_mdp(comp['pendiente']),
        dial=dial, comp_filas=comp_filas, pend_lista=pend_lista, seg=seg, leyenda=leyenda,
        anio_op=next((perd[o['id']]['anio'] for o in documentadas), ''),
        n_ver=len(verificadas), verificadas=esc(', '.join(verificadas)), con_cifra=con_cifra,
        f_cp=_fuente(vfu.get('cp')), f_opa=_fuente(vfu.get('opa')),
        f_tm=_fuente((sm['operacion_oficial']['fuentes']).get('ef_h0m')),
        f_ai=_fuente((sm['operacion_oficial']['fuentes']).get('ef_hzi')),
        r_asf=ref('ref-asf-cp'), datos=_json(datos))


ARRANQUE = '''  <section class="mp-arranque" aria-labelledby="mpArrTit">
    <p class="mp-kicker">Inversión y Megaobras · aplicación 1</p>
    <h2 class="mp-grande" id="mpArrTit">📊 El pulso del gasto</h2>
    <p class="mp-lead">Las cifras de referencia de las {n} megaobras evaluadas, de 1988 a 2024: cuánto costaron, cuánto se pasaron de lo aprobado y cuánto siguen costando cada año. Abajo están las cuatro partes del pulso: cada tarjeta abre su propia página con el desglose completo.</p>
    <div class="mp-pantalla" id="mpPantalla">
      <p class="mp-vivo-et"><span class="mp-punto" aria-hidden="true"></span> Desde que abriste esta página, al ritmo documentado</p>
      <p class="mp-vivo-num mp-num"><b id="mpVivo" aria-live="off">+$0.00</b></p>
      <p class="mp-vivo-sub">A <b class="mp-num">${seg_txt}</b> por segundo: la pérdida y el apoyo anual documentados ({anual}) entre los 31,536,000 segundos de un año de 365 días {chip_der}. No mide un gasto que ocurra en este instante: proyecta el ritmo anual sobre el tiempo que llevas mirando.</p>
      <div class="mp-ctl">
        <button type="button" class="mp-boton mp-claro" id="mpPausa" aria-pressed="false"><span aria-hidden="true">⏸️</span> <span>Pausar</span></button>
        <button type="button" class="mp-boton mp-claro" id="mpCero"><span aria-hidden="true">↺</span> Volver a cero</button>
      </div>
    </div>
  </section>'''

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
        <p class="mp-kpi-sub"><span id="mpKRealSub">Suma de las {n} inversiones evaluadas entre 1988 y 2024</span> {chip_der} {r_asf}</p>
        <p class="mp-kpi-mdp mp-num" id="mpKRealMdp">{real_mdp}</p>
      </article>
      <article class="mp-kpi mp-kpi-alerta">
        <p class="mp-kpi-et"><span class="mp-punto" aria-hidden="true"></span> Pérdida y apoyo anual <span id="mpKPerEt">({per_label})</span></p>
        <p class="mp-kpi-v mp-num" id="mpKPer">{per_v}</p>
        <p class="mp-kpi-sub">Déficit de operación documentado y Ramo 34 del rescate bancario: {n_op} de {n} obras con documento {chip_der}. Las otras {n_pend} no tienen documento de su operación {chip_pend}</p>
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
    <p class="mp-aviso" id="mpAvisoPend"><b>Ojo:</b> {pend_pct}% del costo real del conjunto ({pend_v}) son cifras que siguen <b>pendientes</b> de documento {chip_pend_obra}. La suma se puede hacer, pero no se puede afirmar como dato auditado: <a href="herramienta-megaobras-pulso-composicion.html">mira de qué está hecha</a> o pulsa «Solo con documento».</p>
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
          <tr class="mp-pend-fila"><th scope="row"><span aria-hidden="true">❔</span> Las otras {n_pend} obras <small class="mp-op">{pend_lista}. Ningún documento oficial cotejado dice cuánto cuesta operarlas ni cuánto ingresan: no se estiman y quedan fuera de la suma, lo que no quiere decir que cuesten cero. Qué falta y a quién le toca publicarlo está en el Registro de pendientes.</small></th>
            <td class="mp-num">sin cifra</td><td>{chip_pend}</td></tr>
        </tbody>
        <tfoot><tr><th scope="row">Total documentado <small class="mp-op">Suma de los componentes de arriba × <span id="mpFactorTx">{factor_tx}</span></small></th><td class="mp-num" id="mpCompsTot">{per_v}</td><td>{chip_der}</td></tr></tfoot>
      </table>
    </div>
    <p class="mp-equiv" id="mpEquiv" aria-live="polite"></p>
  </section>''',
    'composicion': '''  <section class="mp-sec" id="mpCompo" aria-labelledby="mpCompTit">
    <h2 class="mp-tit" id="mpCompTit"><span aria-hidden="true">🧩</span> De qué está hecho el costo real</h2>
    <p class="mp-txt">Los {real} del conjunto, según el estado de la cifra de cada obra. Una sola obra puede mover el total entero: compara la barra antes de concluir.</p>
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
    'calculo': '''  <section class="mp-sec mp-como" id="mpComo" aria-labelledby="mpComoTit">
    <h2 class="mp-tit" id="mpComoTit"><span aria-hidden="true">🔎</span> Cómo se calcula lo que ves</h2>
    <ul class="mp-lista">
      <li><b>Los agregados se suman, no se escriben.</b> El costo real, lo aprobado, la brecha y la pérdida anual son la suma obra por obra de las {n} evaluadas {chip_der}.</li>
      <li><b>La pérdida y el apoyo anual.</b> Tren Maya y AIFA, por sus estados de actividades de la Cuenta Pública {anio_op}: ingresos por sus servicios menos gasto total, antes de transferencias {chip_der}; si el resultado queda a favor, cuenta cero. El rescate bancario, por el Ramo 34 ejercido ese año {chip_of}. {n_pend} obras no tienen documento de su operación y no se estiman {chip_pend}.</li>
      <li><b>Las cadencias.</b> La cifra anual multiplicada por 1/365 (día), 1/12 (mes), 1/4 (trimestre) o 1/2 (semestre).</li>
      <li><b>La pérdida por segundo.</b> La cifra anual entre los 31,536,000 segundos de un año de 365 días. El contador en vivo no mide un gasto que ocurra en ese instante: proyecta el ritmo anual sobre el tiempo que llevas mirando.</li>
      <li><b>El sobrecosto del conjunto.</b> Compara la inversión real total contra la aprobada total, de modo que cada obra pesa según su tamaño. No es el promedio simple de los porcentajes, que trataría igual a una refinería y a una estela.</li>
      <li><b>Cifras con documento.</b> De las {n} obras, {n_ver} ya tienen documentos oficiales cotejados ({verificadas}) y {con_cifra} tienen su costo anclado a un documento oficial (la cartera de Hacienda, la Cuenta Pública o un informe de la ASF). La pérdida anual ya tiene documento en {n_op} obras; en las demás, la pérdida, los costos de operación y el costo unitario siguen pendientes y no se estiman {chip_unit}.</li>
      <li><b>Pendiente declarado.</b> Las cifras marcadas como pendientes no tienen todavía el documento oficial que las sustenta; se muestran como consolidación documental y no como dato auditado. Qué falta y a quién le toca publicarlo está en el <a href="pendientes.html#tema-megaobras">Registro de pendientes</a>.</li>
    </ul>
    <p class="mp-fuentes">Fuentes: {f_cp}; {f_tm}; {f_ai}; {f_opa}; y la ASF {r_asf}.</p>
  </section>''',
}

SIGUE = '''  <aside class="mp-sigue">
    <p><b>Sigue con las megaobras:</b></p>
    <ul>
      <li><a href="herramienta-megaobras-sector.html"><span aria-hidden="true">🏭</span> El desglose obra por obra: sector e industria</a></li>
      <li><a href="herramienta-megaobras-sexenios.html"><span aria-hidden="true">🏛️</span> Las obras de cada sexenio</a></li>
      <li><a href="herramienta-megaobras-cero.html"><span aria-hidden="true">🧮</span> De cero al resultado</a></li>
      <li><a href="herramienta-calculadora-reloj.html"><span aria-hidden="true">⏰</span> El reloj de la deuda y de lo perdido</a></li>
    </ul>
    <p class="mp-gris">¿Encontraste un error? <a href="comunidad-erratas.html">Repórtalo</a>.</p>
  </aside>'''

DATOS = '''  <script type="application/json" id="mpDatos">{datos}</script>'''


# Las cuatro partes del pulso, cada una en su pagina (pedido del autor,
# 17-10-2026): la pagina de la aplicacion queda con el contador y cuatro
# tarjetas; cada tarjeta abre herramienta-megaobras-pulso-<slug>.html.
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
     '{pend_pct}% del costo sigue pendiente de documento'),
    ('calculo', '🔎', 'Cómo se calcula', 'Cómo se calcula lo que ves',
     'Las reglas de cada suma, división y cadencia, qué cifras tienen documento y las fuentes oficiales de donde salen.',
     'Las operaciones y sus fuentes, paso a paso'),
]


def parte_archivo(slug):
    return PAGINA[:-5] + '-' + slug + '.html'


def _tarjetas(c):
    filas = []
    for k, (slug, ico, nombre, _tit, desc, cifra) in enumerate(PARTES, 1):
        filas.append(
            '    <li><a class="mp-tarjeta" href="%s">'
            '<span class="mp-tarjeta-num">%d de %d</span>'
            '<span class="mp-tarjeta-tit"><span aria-hidden="true">%s</span> %s</span>'
            '<span class="mp-tarjeta-desc">%s</span>'
            '<span class="mp-tarjeta-cif%s">%s</span>'
            '<span class="mp-tarjeta-ir">Abrir <span aria-hidden="true">→</span></span></a></li>'
            % (parte_archivo(slug), k, len(PARTES), ico, esc(nombre), esc(desc.format(**c)),
               ' mp-num' if '{' in cifra else '', cifra.format(**c)))
    return ('  <nav class="mp-partes" aria-labelledby="mpPartesTit">\n'
            '    <h2 class="mp-tit" id="mpPartesTit"><span aria-hidden="true">🗂️</span> Las cuatro partes del pulso</h2>\n'
            '    <ol class="mp-tarjetas">\n%s\n    </ol>\n  </nav>' % '\n'.join(filas))


def _subnav(actual):
    chips = ''.join(
        '<a class="mp-subnav-chip%s" href="%s"%s><span aria-hidden="true">%s</span> %d · %s</a>'
        % (' actual' if slug == actual else '', parte_archivo(slug), ' aria-current="page"' if slug == actual else '',
           ico, k, esc(nombre))
        for k, (slug, ico, nombre, *_r) in enumerate(PARTES, 1))
    return ('  <nav class="mp-subnav" aria-label="Las cuatro partes del pulso">\n'
            '    <a class="mp-subnav-volver" href="%s"><span aria-hidden="true">←</span> Volver al pulso y su contador</a>\n'
            '    <div class="mp-subnav-chips">%s</div>\n  </nav>' % (PAGINA, chips))


def construir(base, ref):
    c = _contexto(base, ref)
    return '\n\n'.join(['<div class="mp" id="mpRaiz">', ARRANQUE.format(**c), _tarjetas(c),
                         SIGUE.format(**c), DATOS.format(**c)]) + '\n</div>'


def subpaginas(base, ref):
    """Las cuatro partes, para apartados.insp_subpaginas(): cada una con su
    seccion, la navegacion entre partes y los datos que usa mo-pulso.js."""
    c = _contexto(base, ref)
    out = []
    for slug, ico, nombre, tit, desc, _cif in PARTES:
        bloque = '\n\n'.join(['<div class="mp mp-parte" id="mpRaiz">', _subnav(slug),
                               SECCIONES[slug].format(**c), _subnav(slug).replace('class="mp-subnav" aria-label="Las cuatro partes del pulso"', 'class="mp-subnav mp-subnav-pie" aria-label="Sigue con otra parte del pulso"', 1),
                               DATOS.format(**c)]) + '\n</div>'
        out.append({'archivo': parte_archivo(slug), 'icono': ico, 'menu': nombre, 'titulo': tit,
                    'entrada': '<b>%s.</b> %s' % (esc(nombre), esc(desc.format(**c))), 'bloque': bloque})
    return out
