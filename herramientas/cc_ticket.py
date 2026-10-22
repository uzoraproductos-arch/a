# -*- coding: utf-8 -*-
"""Calculadora Civica, aplicacion 1: «Tu estado de cuenta» en pagina propia
(12-10-2026). Sustituye al marco que cargaba la portada entera
(index.html?ir=calculadora&ancla=eb-ccticket&visor=1).

El lector escribe lo que gana y la pagina saca cuatro cuentas: su ingreso,
lo que le retienen (ISR, cuotas obreras al IMSS y el IVA como escenario),
a donde iria cada peso de su ISR segun el PEF 2026 y su estado de cuenta
civico, con folio y huella SHA-256.

Las reglas son las mismas del motor (audit-engine.js: ccDesdeBruto,
ccDesdeNeto, ccCalcularResultado, ccReparto, eccDatos) y los parametros los
mismos de window.AUDIT_DB.calculadora_civica, panoramaErario y poderes. Las
tablas oficiales (tarifa del art. 96, tabla del RESICO, cuotas obreras) se
escriben aqui; el JS (assets/auditor/js/cc-ticket.js) solo calcula con la
cifra del lector, que no sale de su navegador.

Diferencias con el motor (correcciones, no cambios de dato):
- En actividad empresarial, la deduccion escrita «al año» se divide entre
  doce antes de restarla al ingreso del mes (el motor la restaba entera al
  mes).
- El folio ya no es aleatorio: sale de la huella SHA-256 de las cifras y
  de la entrada, como los estados de cuenta del Radar, y la liga de
  verificacion de esta misma pagina lo recalcula.
- Los textos del motor que quedaban de usted van de tu.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['ccticket']).
"""
import html
import json
import re

from presupuesto_modulos import chip

ESTILOS = ['cc-ticket.css']
SCRIPTS = ['cc-ticket.js']


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def esc(t):
    return html.escape(str(t if t is not None else ''), quote=True)


def pesos2(v):
    return '$' + format(v, ',.2f')


def pesos(v):
    return '$' + format(round(v), ',d')


# Textos de la base que estan de usted: se pasan a tu (AGENTS.md §4).
_TU = [('El impuesto que usted paga', 'El impuesto que pagas'), ('que su dinero', 'que tu dinero'),
       ('Su ISR', 'Tu ISR'), ('a su aportación', 'a tu aportación'), ('que usted ve', 'que ves'),
       ('cuánto IVA paga usted', 'cuánto IVA pagas'), ('que usted fija', 'que tú fijas')]


def tu(t):
    for a, b in _TU:
        t = t.replace(a, b)
    return t


def datos_js(base):
    """Lo que el JS necesita para calcular: los mismos parametros del motor."""
    c = base['calculadora_civica']
    p = c['parametros']
    P = base['panoramaErario']
    po = base.get('poderes') or {}
    dip = next((x for x in po.get('remuneraciones2026') or [] if 'diputad' in x['cargo'].lower()), None)
    regs = []
    for r in c['regimenes']:
        o = {k: r[k] for k in ('id', 'nombre', 'corto', 'icono', 'quien_es', 'retiene', 'punto_ciego', 'nota') if k in r}
        if r.get('hereda'):
            o['hereda'] = r['hereda']
        if r.get('tasas'):
            o['tasas'] = r['tasas']
        regs.append(o)
    return {
        'par': {
            'uma': {k: p['uma'][k] for k in ('diaria', 'mensual')},
            'sm': {k: p['salario_minimo'][k] for k in ('general', 'frontera_norte', 'mensual_general', 'mensual_frontera')},
            'sub': {'pct': p['subsidio_empleo']['pct_uma'], 'tope': p['subsidio_empleo']['tope_ingreso_mensual']},
            'iva': p['iva']['tasa'],
        },
        'tarifa': c['tarifa_mensual']['renglones'],
        'resico': c['resico']['renglones'],
        'resicoTope': c['resico'].get('tope_anual'),
        'imss': {'tope': c['imss_obrero']['tope_sbc_uma'],
                 'ramos': [{'ramo': x['ramo'], 'pct': x['pct'], 'base': x['base'], 'ley': x['ley']} for x in c['imss_obrero']['ramos']]},
        'regimenes': regs,
        'egresos': [{'id': e['id'], 'nombre': e['nombre'], 'icono': e['icono'], 'grupo': e['grupo'], 'm': e['montoMdp']}
                    for e in P['egresos']],
        'poderes': ({'gnt': po['gastoNetoTotal']['valor'],
                     'ramos': [{'k': k, 'nombre': po['ramos2026'][k]['nombre'], 'ramo': po['ramos2026'][k]['ramo'],
                                'aprobado': po['ramos2026'][k]['aprobado']} for k in ('legislativo', 'judicial')]}
                    if po.get('ramos2026') else None),
        'dip': ({'cargo': dip['cargo'], 'netoAnual': dip['netoAnual'], 'pagina': dip.get('pagina', '')} if dip else None),
    }


def _tarifa_tabla(t):
    filas = []
    for i, r in enumerate(t['renglones']):
        filas.append('<tr data-i="%d"><td>%s</td><td>%s</td><td>%s</td><td>%s%%</td></tr>'
                     % (i, pesos2(r['li']), 'En adelante' if r['ls'] is None else pesos2(r['ls']), pesos2(r['cf']), format(r['pct'], '.2f')))
    return '\n'.join(filas)


def _resico_tabla(rs):
    return '\n'.join('<tr data-tasa="%s"><td>%s</td><td>%s%%</td></tr>' % (r['tasa'], pesos2(r['hasta']), format(r['tasa'], '.2f'))
                     for r in rs['renglones'])


def _completo(base, ref):
    c = base['calculadora_civica']
    p = c['parametros']
    P = base['panoramaErario']
    po = base.get('poderes') or {}
    D = datos_js(base)
    sm, uma, sub = p['salario_minimo'], p['uma'], p['subsidio_empleo']
    t, rs, im = c['tarifa_mensual'], c['resico'], c['imss_obrero']
    ciego = c['puntos_ciegos'][0]

    # Regimenes: tarjetas
    regs = '\n'.join(
        '<button type="button" class="ct-reg" data-reg="%s" aria-pressed="false"><span class="ct-reg-ico" aria-hidden="true">%s</span>'
        '<span class="ct-reg-nom">%s</span><span class="ct-reg-corto">%s</span></button>'
        % (esc(r['id']), r['icono'], esc(r['nombre']), esc(r['corto'])) for r in c['regimenes'])
    plat = next((r for r in c['regimenes'] if r['id'] == 'plataformas'), None)
    plat_bot = '\n'.join('<button type="button" class="ct-seg-b" data-plat="%s" aria-pressed="false">%s · %s%%</button>'
                         % (esc(x['id']), esc(x['nombre']), x['pct']) for x in (plat or {}).get('tasas', []))
    nose = next((r for r in c['regimenes'] if r['id'] == 'nose'), None)

    # Presets del deslizador. Solo dos son cifras oficiales; los demas son
    # ejemplos para probar y lo dicen.
    presets = [
        (sm['mensual_general'], 'Salario mínimo', 'oficial', 'CONASAMI: $%s diarios × 30' % format(sm['general'], ',.2f'), True),
        (sub['tope_ingreso_mensual'], 'Tope del subsidio al empleo', 'oficial', 'Decreto del 31-12-2025', False),
        (15000, '$15,000', '', 'ejemplo', False), (25000, '$25,000', '', 'ejemplo', False),
        (50000, '$50,000', '', 'ejemplo', False), (100000, '$100,000', '', 'ejemplo', False),
    ]
    pre_html = '\n'.join(
        '<button type="button" class="ct-preset%s" data-monto="%s"%s><b>%s</b><small>%s%s</small></button>'
        % (' ct-preset-of' if e else '', v, ' data-oficial="1"' if of else '', esc(n), esc(s), (' ' + chip(e)) if e else '')
        for v, n, e, s, of in presets)

    # Reparto: cada rubro pintado con su monto oficial; el JS pone lo tuyo.
    eg = P['egresos']
    total = sum(e['montoMdp'] for e in eg)
    rubros = []
    for e in sorted(eg, key=lambda x: -x['montoMdp']):
        pc = e['montoMdp'] / total * 100
        rubros.append(
            '<li class="ct-rub" data-id="%s" style="--ct-p:%.3f">'
            '<button type="button" class="ct-rub-b" aria-expanded="false" aria-controls="ctRub-%s">'
            '<span class="ct-rub-ico" aria-hidden="true">%s</span>'
            '<span class="ct-rub-nom">%s<small>%s</small></span>'
            '<span class="ct-rub-v"><b data-tuyo>$0</b><small>%s%%</small></span>'
            '<span class="ct-rub-riel" aria-hidden="true"><span class="ct-rub-barra"></span></span></button>'
            '<div class="ct-rub-det" id="ctRub-%s" hidden>'
            '<p>%s</p>'
            '<p class="ct-rub-dato">Presupuesto aprobado 2026 para este renglón: <b>$%s mdp</b> %s %s</p>'
            '<p class="ct-rub-dato">Su peso en el gasto: <b>%s%%</b> %s <small>(este renglón ÷ la suma de los ocho, $%s mdp)</small></p>'
            '<p class="ct-rub-dato">Lo tuyo: <b data-tuyo-largo>—</b> %s <small>(tu ISR × %s%%)</small></p>'
            '</div></li>'
            % (esc(e['id']), pc, esc(e['id']), e['icono'], esc(e['nombre']), esc(e['grupo']), format(pc, '.1f'), esc(e['id']),
               esc(e['queCubre']), format(e['montoMdp'], ',.1f'), chip(e.get('estado') or 'oficial'),
               ref(e['refKey']) if e.get('refKey') else '', format(pc, '.2f'), chip('derivado'), format(total, ',.1f'),
               chip('derivado'), format(pc, '.2f')))

    # Lo que paga el patron y el trabajador no ve.
    patron = '\n'.join('<li><b>%s%s</b> %s</li>' % (esc(x['ramo']), (' · %s%%' % x['pct']) if x.get('pct') is not None else '', esc(x['ley']))
                       for x in im.get('no_los_paga_el_trabajador', []))
    ramos_imss = '\n'.join('<tr><td>%s</td><td>%s%%</td><td>%s</td></tr>'
                           % (esc(x['ramo']), format(x['pct'], '.3f').rstrip('0').rstrip('.'),
                              'lo que excede 3 UMA' if x['base'] == 'excedente_3_uma' else 'todo el salario base')
                           for x in im['ramos'])

    poderes_txt = ''
    if po.get('ramos2026'):
        g = po['gastoNetoTotal']['valor']
        poderes_txt = ' '.join('%s (Ramo %s): %s de cada $1,000 del gasto %s.' % (
            esc(po['ramos2026'][k]['nombre']), po['ramos2026'][k]['ramo'],
            pesos2(po['ramos2026'][k]['aprobado'] / g * 1000), chip('derivado')) for k in ('legislativo', 'judicial'))

    return '''<div class="ct" id="ctRaiz">
  <section class="ct-arranque" aria-labelledby="ctArrTit">
    <p class="ct-kicker">Calculadora Cívica · aplicación 1</p>
    <h2 class="ct-grande" id="ctArrTit">¿Cuánto pagas y a dónde va?</h2>
    <p class="ct-txt">Escribe lo que ganas, di cómo tributas y la página saca cuatro cuentas con el aparato legal de 2026: <b>cuánto te retienen y con qué regla</b>, <b>a dónde iría esa aportación</b> según el reparto del Presupuesto aprobado y, al final, <b>tu estado de cuenta cívico</b>, con folio y huella para comprobarlo. Las tarifas salen del Anexo 8 de la Resolución Miscelánea publicado el 28 de diciembre de 2025 {r_rmf}; las cuotas del Seguro Social, de cinco artículos de su ley {r_lss}; la UMA de {uma_mes} al mes, del INEGI {r_uma}.</p>
    <p class="ct-privado"><span aria-hidden="true">🔒</span> Nada de lo que escribas sale de tu navegador: la plataforma no guarda ni envía tu ingreso. Solo este equipo lo recuerda para la próxima vez, y lo borras con «Reiniciar a ceros».</p>
    <ol class="ct-indice" aria-label="Las cuatro cuentas">
      <li><a href="#ctPaso1"><span class="ct-n">1</span> Tu ingreso</a></li>
      <li><a href="#ctPaso2"><span class="ct-n">2</span> Lo que te retienen</a></li>
      <li><a href="#ctPaso3"><span class="ct-n">3</span> A dónde va cada peso</a></li>
      <li><a href="#ctPaso4"><span class="ct-n">4</span> Tu estado de cuenta</a></li>
    </ol>
  </section>

  <section class="ct-paso" id="ctPaso1" aria-labelledby="ctP1Tit">
    <h2 class="ct-tit" id="ctP1Tit"><span class="ct-n">1</span> Tu ingreso</h2>
    <div class="ct-monto">
      <label class="ct-et" for="ctMonto">¿Cuánto ganas?</label>
      <div class="ct-caja"><span class="ct-caja-sig" aria-hidden="true">$</span>
        <input type="text" id="ctMonto" class="ct-input" value="" placeholder="0" inputmode="decimal" autocomplete="off" spellcheck="false" aria-describedby="ctMontoPista"></div>
      <p class="ct-pista" id="ctMontoPista">En pesos. Escríbelo o mueve la barra; la cuenta se rehace sola.</p>
      <input type="range" id="ctRango" class="ct-rango" min="0" max="1000" step="1" value="0" aria-label="Mueve para cambiar tu ingreso">
      <div class="ct-presets" role="group" aria-label="Cifras para probar">
{presets}
      </div>
    </div>

    <div class="ct-campos">
      <div class="ct-campo"><span class="ct-et" id="ctPerEt">¿Cada cuándo?</span>
        <div class="ct-seg" role="group" aria-labelledby="ctPerEt">
          <button type="button" class="ct-seg-b" data-per="mes" aria-pressed="true"><span aria-hidden="true">📅</span> Al mes</button>
          <button type="button" class="ct-seg-b" data-per="ano" aria-pressed="false"><span aria-hidden="true">🗓️</span> Al año</button>
        </div></div>
      <div class="ct-campo"><span class="ct-et" id="ctNatEt">¿Esa cifra es antes o después de descuentos?</span>
        <div class="ct-seg" role="group" aria-labelledby="ctNatEt">
          <button type="button" class="ct-seg-b" data-nat="bruto" aria-pressed="true">Bruto, antes de descuentos</button>
          <button type="button" class="ct-seg-b" data-nat="neto" aria-pressed="false">Neto, lo que recibo</button>
        </div></div>
    </div>

    <p class="ct-et" id="ctRegEt">¿En qué régimen tributas?</p>
    <div class="ct-regs" role="group" aria-labelledby="ctRegEt">
{regs}
    </div>
    <div class="ct-opcion" id="ctOpHon" hidden>
      <label class="ct-et" for="ctDed">¿Cuánto deduces <span id="ctDedPer">al mes</span>?</label>
      <div class="ct-caja ct-caja-chica"><span class="ct-caja-sig" aria-hidden="true">$</span>
        <input type="text" id="ctDed" class="ct-input" value="0" inputmode="decimal" autocomplete="off"></div>
      <p class="ct-pista">Gastos autorizados con factura. Si lo dejas en cero, el impuesto se calcula sobre todo lo que facturaste, que es el peor de los casos y también el más frecuente entre quienes no llevan contabilidad.</p>
    </div>
    <div class="ct-opcion" id="ctOpPlat" hidden>
      <span class="ct-et" id="ctPlatEt">¿Qué haces en la plataforma?</span>
      <div class="ct-seg ct-seg-col" role="group" aria-labelledby="ctPlatEt">
{plat}
      </div>
      <p class="ct-pista">Las tres tasas son las del artículo 113-A de la Ley del ISR {r_lisr}.</p>
    </div>
    <p class="ct-aviso ct-aviso-suave" id="ctOpNose" hidden><b>Seguimos adelante.</b> {nose_nota} Mientras tanto se calcula como <b>sueldos y salarios</b>, que es el régimen de la mayoría; el resultado lo dice en cada renglón.</p>

    <div class="ct-mandos">
      <button type="button" class="ct-boton" id="ctCalcular"><span aria-hidden="true">🧮</span> <span id="ctCalcTx">Sacar la cuenta</span></button>
      <button type="button" class="ct-boton ct-sec" id="ctEjemplo" title="Salario mínimo general 2026: CONASAMI, DOF 9 de diciembre de 2025"><span aria-hidden="true">📄</span> Cargar ejemplo oficial</button>
      <button type="button" class="ct-boton ct-sec" id="ctReiniciar"><span aria-hidden="true">↺</span> Reiniciar a ceros</button>
    </div>
    <p class="ct-estado" id="ctEstado" aria-live="polite">⚪ Todo está en ceros ($0). Escribe tu ingreso, elige tu régimen y pulsa «Sacar la cuenta».</p>
    <p class="ct-pista ct-sim"><span class="ct-sim-et">Simulación</span> Lo que escribes es tuyo, no un dato oficial, y un $0 tuyo no quiere decir que el dato oficial sea cero. El ejemplo oficial carga el salario mínimo general mensual de 2026 ({sm_mes}, CONASAMI {r_sm} {chip_of}).</p>

    <div class="ct-vivo" id="ctVivo" hidden aria-live="polite">
      <div><span>Ingreso bruto</span><b id="ctVBruto">$0</b></div>
      <div><span>ISR</span><b id="ctVIsr">$0</b></div>
      <div><span>IMSS</span><b id="ctVImss">$0</b></div>
      <div class="ct-vivo-neto"><span>Te queda</span><b id="ctVNeto">$0</b></div>
      <div class="ct-vivo-barra" aria-hidden="true"><i class="ct-vb-isr" id="ctVbIsr"></i><i class="ct-vb-imss" id="ctVbImss"></i><i class="ct-vb-neto" id="ctVbNeto"></i></div>
    </div>
  </section>

  <section class="ct-paso" id="ctPaso2" aria-labelledby="ctP2Tit">
    <h2 class="ct-tit" id="ctP2Tit"><span class="ct-n">2</span> Lo que te retienen</h2>
    <p class="ct-vacio" id="ctVacio2">Aquí aparece la cuenta, renglón por renglón, en cuanto escribas tu ingreso.</p>
    <div id="ctRet" hidden>
      <p class="ct-sub" id="ctRetSub"></p>
      <div class="ct-resumen" id="ctResumen"></div>
      <h3 class="ct-sub-tit" id="ctCascTit">Renglón por renglón</h3>
      <ol class="ct-cascada" id="ctCascada"></ol>
      <p class="ct-leyenda"><b>−</b> y <b>+</b> son movimientos: dinero que sale o que vuelve. <b>=</b> es un subtotal, no se suma aparte. <b>·</b> es un renglón que explica cómo se llega a la base gravable y <b>no toca tu bolsillo</b>.</p>
      <div class="ct-escalon" id="ctEscalon"></div>

      <details class="ct-tabla-det" id="ctTarifaDet">
        <summary>📋 La tarifa mensual del ISR: el renglón en que caíste</summary>
        <div class="ct-tabla-caja"><table class="ct-tabla" id="ctTarifa"><thead><tr><th>Límite inferior</th><th>Límite superior</th><th>Cuota fija</th><th>% sobre el excedente</th></tr></thead>
        <tbody>
{tarifa}
        </tbody></table></div>
        <p class="ct-fuente">{t_ley} {chip_t} · {t_fuente} {r_rmf}. {t_nota}</p>
      </details>
      <details class="ct-tabla-det" id="ctResicoDet" hidden>
        <summary>📋 La tabla del RESICO: la tasa en que caíste</summary>
        <div class="ct-tabla-caja"><table class="ct-tabla" id="ctResico"><thead><tr><th>Ingresos mensuales hasta</th><th>Tasa</th></tr></thead>
        <tbody>
{resico}
        </tbody></table></div>
        <p class="ct-fuente">{rs_ley} {chip_rs} {r_lisr} · {rs_nota}</p>
      </details>
      <details class="ct-tabla-det" id="ctImssDet">
        <summary>🏥 Las cuotas obreras al Seguro Social, ramo por ramo</summary>
        <div class="ct-tabla-caja"><table class="ct-tabla"><thead><tr><th>Ramo</th><th>Cuota obrera</th><th>Sobre</th></tr></thead>
        <tbody>
{ramos_imss}
        </tbody></table></div>
        <p class="ct-fuente">{im_fuente} {chip_im} {r_lss}. {im_tope} Tope de cotización: {tope_uma} veces la UMA diaria ({uma_dia}) × 30 = <b>{tope_mes}</b> al mes {chip_der}.</p>
        <h4 class="ct-sub-tit">Lo que el patrón paga por ti y no ves en tu recibo</h4>
        <ul class="ct-patron">
{patron}
        </ul>
      </details>

      <div class="ct-esc" id="ctIva">
        <div class="ct-esc-cab"><h3 class="ct-esc-tit"><span aria-hidden="true">🛒</span> El impuesto que nadie te retiene</h3><span class="ct-esc-sello">Escenario, no dato</span></div>
        <p class="ct-esc-nota">Esta plataforma <b>no puede saber</b> cuánto IVA pagas tú: depende de en qué gastas, y una parte del gasto —alimentos básicos, medicinas, colegiaturas, renta de casa habitación— está a tasa cero o exenta. Por eso este renglón es el único que tú fijas y nosotros no afirmamos. La tasa general es de {iva}% (Ley del IVA, art. 1º {r_liva} {chip_of}).</p>
        <label class="ct-esc-mando" for="ctIvaRango"><span>Supongamos que gastas el <b id="ctIvaPct">50%</b> de lo que te queda en cosas gravadas al {iva}%</span>
          <input type="range" id="ctIvaRango" class="ct-rango" min="0" max="100" step="5" value="50"></label>
        <div class="ct-esc-res">
          <div><span>IVA al año en ese escenario</span><b id="ctIvaAno">$0</b></div>
          <div><span>Sobre tu ingreso bruto</span><b id="ctIvaSobre">0.00%</b></div>
          <div><span>Sumado a lo que ya te retienen</span><b id="ctIvaSuma">0.00%</b></div>
        </div>
        <p class="ct-esc-pie">El IVA va dentro del precio: de cada $116 pagados por un bien gravado, $16 son impuesto. Como la tasa no distingue quién compra, quien gana poco entrega al fisco una proporción mayor de su ingreso que quien gana mucho. Eso es lo que la doctrina llama un impuesto regresivo.</p>
      </div>
      <div id="ctAvisos"></div>
    </div>
  </section>

  <section class="ct-paso" id="ctPaso3" aria-labelledby="ctP3Tit">
    <h2 class="ct-tit" id="ctP3Tit"><span class="ct-n">3</span> A dónde iría cada peso</h2>
    <p class="ct-sub" id="ctRepSub">Tu impuesto sobre la renta, repartido con las mismas proporciones del Presupuesto de Egresos aprobado para 2026 {r_pef}. Toca un renglón para ver qué cubre y de dónde sale.</p>
    <div class="ct-seg ct-rep-per" role="group" aria-label="Ver el reparto">
      <button type="button" class="ct-seg-b" data-rper="ano" aria-pressed="true">Al año</button>
      <button type="button" class="ct-seg-b" data-rper="mes" aria-pressed="false">Al mes</button>
      <button type="button" class="ct-seg-b" data-rper="dia" aria-pressed="false">Al día</button>
    </div>
    <ol class="ct-reparto" id="ctReparto">
{rubros}
    </ol>
    <div class="ct-aparte" id="ctAparte" hidden>
      <h3 class="ct-aparte-tit"><span aria-hidden="true">🏥</span> Tus cuotas al Seguro Social van aparte, y por ley</h3>
      <p>Los <b id="ctAparteV">$0</b> que cotizas al año <b>no entran en el reparto de arriba</b>. El artículo 2º del Código Fiscal {r_cff} las define como contribución con <b>destino específico</b>: no van a la bolsa común del gasto, no forman parte de la Recaudación Federal Participable y, por lo mismo, no se reparten a estados ni a municipios. Financian tu servicio médico, tus incapacidades y tu pensión. Es la única parte de lo que se te descuenta que tiene un destino declarado en la ley.</p>
    </div>
    <p class="ct-aviso ct-aviso-ciego"><span aria-hidden="true">{ciego_ico}</span> <b>{ciego_tit}.</b> {ciego_tx}</p>
    <p class="ct-fuente">Clasificación del gasto del Presupuesto de Egresos de la Federación 2026 {r_pef}: montos {chip_of}; los porcentajes se calculan dividiendo cada renglón entre la suma de los ocho ({total} mdp) {chip_der}, no se escriben a mano. {poderes_txt} Más en <a href="numeros-cuanto-dinero-es.html">Cuánto dinero es</a> y <a href="numeros-lo-que-cuestan-los-poderes.html">Lo que cuestan el Congreso y la Judicatura</a>.</p>
  </section>

  <section class="ct-paso" id="ctPaso4" aria-labelledby="ctP4Tit">
    <h2 class="ct-tit" id="ctP4Tit"><span class="ct-n">4</span> Tu estado de cuenta cívico</h2>
    <div class="ct-verif" id="ctVerif" hidden aria-live="polite"></div>
    <p class="ct-sub" id="ctDocSub">Lo que ganaste, lo que te retuvieron y a dónde fue tu impuesto, en un solo documento con folio y huella. Aparece aquí en cuanto saques la cuenta.</p>
    <div class="ct-doc-marco" id="ctDocMarco" hidden>
      <article class="ct-doc" id="ctDoc" aria-labelledby="ctDocTit"></article>
    </div>
    <div class="ct-acciones" id="ctAcciones" hidden>
      <button type="button" class="ct-boton" id="ctImagen"><span aria-hidden="true">⬇️</span> Descargar imagen para compartir</button>
      <button type="button" class="ct-boton ct-sec" id="ctCopiar"><span aria-hidden="true">📋</span> Copiar como texto</button>
      <button type="button" class="ct-boton ct-sec" id="ctImprimir"><span aria-hidden="true">🖨️</span> Imprimir o guardar en PDF</button>
      <button type="button" class="ct-boton ct-sec" id="ctLiga"><span aria-hidden="true">🔏</span> Copiar la liga de verificación</button>
      <a class="ct-boton ct-sec" href="pase-del-auditor.html"><span aria-hidden="true">🍺</span> Pase Cívico</a>
      <label class="ct-noche"><input type="checkbox" id="ctNoche"> Imagen de noche</label>
    </div>
    <p class="ct-copiado" id="ctCopiado" aria-live="polite"></p>
    <details class="ct-como">
      <summary>🔏 Cómo se comprueba tu estado de cuenta</summary>
      <ol>
        <li><b>La huella.</b> El documento firma sus cifras y los datos que escribiste con una huella digital SHA-256: si cambia una sola cifra, cambia la huella.</li>
        <li><b>El folio.</b> Son las letras EC (estado de cuenta cívico) y los primeros ocho caracteres de la huella, por ejemplo AV-EC-1A2B3C4D. Los mismos datos dan siempre el mismo folio.</li>
        <li><b>La comprobación.</b> La liga de verificación abre esta página con tus datos, recalcula la huella en el navegador de quien la abre y dice si coincide. <b>La liga lleva tu ingreso escrito:</b> compártela solo si quieres que se vea.</li>
      </ol>
      <p class="ct-pista">Los estados de cuenta de las administraciones, del Congreso y de la Corte se comprueban en <a href="herramienta-inspector-verifica.html">Verifica un estado de cuenta</a>; el tuyo depende de tu ingreso, por eso se comprueba aquí, con su liga.</p>
    </details>
  </section>

  <aside class="ct-pie">
    <p><b>Lo que esta herramienta no hace:</b> no sustituye tu constancia de retenciones ni tu declaración. Usa la tarifa mensual con un ingreso parejo todo el año; aguinaldo, horas extra, prestaciones exentas y deducciones personales cambian la cuenta final.</p>
    <p>Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>. Lo que todavía nos deben las dependencias está en el <a href="pendientes.html">Registro de pendientes</a>.</p>
    <p class="ct-hermanas">Sigue con la calculadora: <a href="herramienta-calculadora-compara.html">⚡ Tú contra ellos</a> · <a href="herramienta-calculadora-reloj.html">⏱️ El reloj de la deuda</a> · <a href="simulador-presupuesto.html">🧮 Reparte el presupuesto</a></p>
  </aside>
  <script type="application/json" id="ctDatos">{datos}</script>
</div>'''.format(
        r_rmf=ref('ref-rmf2026'), r_lss=ref('ref-lss'), r_uma=ref('ref-uma2026'), r_sm=ref('ref-conasami2026'),
        r_lisr=ref('ref-lisr'), r_liva=ref('ref-liva'), r_pef=ref('ref-pef2026'), r_cff=ref('ref-cff'),
        uma_mes=pesos2(uma['mensual']), uma_dia=pesos2(uma['diaria']), sm_mes=pesos2(sm['mensual_general']),
        presets=pre_html, regs=regs, plat=plat_bot, nose_nota=esc((nose or {}).get('nota', '')),
        chip_of=chip('oficial'), chip_der=chip('derivado'),
        tarifa=_tarifa_tabla(t), t_ley=esc(t['ley']), chip_t=chip(t['estado']), t_fuente=esc(t['fuente']), t_nota=esc(t.get('nota', '')),
        resico=_resico_tabla(rs), rs_ley=esc(rs['ley']), chip_rs=chip(rs['estado']), rs_nota=rs.get('nota', ''),
        ramos_imss=ramos_imss, im_fuente=esc(im['fuente']), chip_im=chip(im['estado']), im_tope=esc(im.get('nota_tope', '')),
        tope_uma=im['tope_sbc_uma'], tope_mes=pesos2(im['tope_sbc_uma'] * uma['diaria'] * 30), patron=patron,
        iva=p['iva']['tasa'], rubros='\n'.join(rubros),
        ciego_ico=ciego['icono'], ciego_tit=esc(tu(ciego['titulo'])), ciego_tx=esc(tu(ciego['texto'])) + (' ' + esc(tu(ciego['excepcion'])) if ciego.get('excepcion') else ''),
        total='$' + format(total, ',.1f'), poderes_txt=poderes_txt, datos=_json(D))


# Las cuatro cuentas en paginas propias (pedido del autor, 22-10-2026): la
# aplicacion 1 solo presenta las cuatro tarjetas, y cada una abre su pagina
# con su parte de la calculadora. El ingreso viaja de una pagina a otra en
# el almacenamiento del navegador (cc-ticket.js), nunca en el servidor.
PORTADA = 'herramienta-calculadora-ticket.html'
PASOS = [
    # (n, slug, icono, nombre, frase, que hace)
    (1, 'ingreso', '💵', 'Tu ingreso', 'Escribe lo que ganas',
     'Cuánto ganas, cada cuándo, si es antes o después de descuentos y en qué régimen tributas. Con eso la calculadora saca la cuenta.'),
    (2, 'retienen', '💸', 'Lo que te retienen', 'Renglón por renglón',
     'El ISR con la tarifa del artículo 96, las cuotas obreras al IMSS y el IVA como escenario, cada uno con la regla y el documento que lo sostienen.'),
    (3, 'reparto', '🧭', 'A dónde va cada peso', 'Según el Presupuesto 2026',
     'Tu impuesto sobre la renta repartido con las mismas proporciones del Presupuesto de Egresos aprobado para 2026, rubro por rubro.'),
    (4, 'estado', '📄', 'Tu estado de cuenta', 'Con folio y huella',
     'Lo que ganaste, lo que te retuvieron y a dónde fue tu impuesto en un solo documento, con folio y huella para comprobarlo, listo para descargar o compartir.'),
]


def paso_archivo(slug):
    return PORTADA[:-5] + '-' + slug + '.html'


def _corta(completo, inicio, fin='\n  </section>'):
    i = completo.index(inicio)
    return completo[i:completo.index(fin, i) + len(fin)]


def construir(base, ref):
    """La aplicacion 1: la presentacion y las cuatro tarjetas."""
    c = _completo(base, ref)
    arr = _corta(c, '  <section class="ct-arranque"')
    arr = re.sub(r'\n    <ol class="ct-indice".*?</ol>', '', arr, flags=re.S)
    arr = arr.replace('la página saca cuatro cuentas', 'la calculadora saca cuatro cuentas, cada una en su página')
    tarjetas = '\n'.join(
        '      <li><a class="herr-paso rubro-calculadora" href="%s">\n'
        '        <span class="herr-paso-num" aria-hidden="true">%d</span>\n'
        '        <span class="herr-paso-ico" aria-hidden="true">%s</span>\n'
        '        <span class="herr-paso-tx"><span class="herr-paso-frase">%s</span>'
        '<span class="herr-paso-nombre">%s</span><span class="herr-paso-desc">%s</span></span>\n'
        '        <span class="herr-paso-accion">Abrir ➔</span>\n'
        '      </a></li>' % (paso_archivo(slug), n, ico, frase, nombre, desc)
        for n, slug, ico, nombre, frase, desc in PASOS)
    rutas = ' '.join('data-paso%d="%s"' % (n, paso_archivo(slug)) for n, slug, _, _, _, _ in PASOS)
    return ('<div class="ct ct-portada" id="ctPortada" %s>\n%s\n'
            '  <section class="ct-cuentas" aria-labelledby="ctCuentasTit">\n'
            '    <h2 class="ct-cuentas-tit" id="ctCuentasTit">Las cuatro cuentas</h2>\n'
            '    <p class="ct-cuentas-tx">Empieza por tu ingreso: las otras tres usan esa cifra. Cada tarjeta abre su propia página.</p>\n'
            '    <ol class="herr-ruta">\n%s\n    </ol>\n  </section>\n\n%s\n</div>'
            % (rutas, arr, tarjetas, _corta(c, '  <aside class="ct-pie">', '\n  </aside>')))


def subpaginas(base, ref):
    """Para apartados.insp_subpaginas(): una pagina por cuenta. Cada una
    lleva la calculadora entera (el JS la necesita) con solo su parte a la
    vista."""
    c = _completo(base, ref)
    sm = base['calculadora_civica']['parametros']['salario_minimo']['mensual_general']
    out = []
    for k, (n, slug, ico, nombre, frase, desc) in enumerate(PASOS):
        pag = c.replace('<div class="ct" id="ctRaiz">', '<div class="ct ct-sola" id="ctRaiz" data-paso="%d">' % n, 1)
        pag = pag.replace(_corta(c, '  <section class="ct-arranque"'), '', 1)
        for m in range(1, 5):
            if m != n:
                pag = pag.replace('<section class="ct-paso" id="ctPaso%d"' % m, '<section class="ct-paso" id="ctPaso%d" hidden' % m, 1)
        aviso = ''
        if n > 1:
            aviso = ('  <div class="ct-falta" id="ctFalta" hidden>\n'
                     '    <p><b>Todavía no escribes tu ingreso.</b> Esta cuenta sale de esa cifra: escríbela en '
                     '<a href="%s">1 · Tu ingreso</a> o prueba con el salario mínimo general de 2026, %s al mes %s.</p>\n'
                     '    <div class="ct-acciones"><a class="ct-boton" href="%s"><span aria-hidden="true">💵</span> Escribir mi ingreso</a>'
                     '<button type="button" class="ct-boton ct-sec" data-monto="%s" data-oficial="1"><span aria-hidden="true">📄</span> Usar el salario mínimo</button></div>\n'
                     '  </div>\n'
                     '  <p class="ct-tuing" id="ctTuIng" hidden></p>\n'
                     % (paso_archivo('ingreso'), pesos2(sm), chip('oficial'), paso_archivo('ingreso'), sm))
        sig = PASOS[k + 1] if k + 1 < len(PASOS) else None
        sigue = ('  <p class="ct-sigue" id="ctSigue"><a class="ct-boton" href="%s">Sigue con %d · %s <span aria-hidden="true">→</span></a></p>\n'
                 % (paso_archivo(sig[1]), sig[0], sig[3])) if sig else ''
        i = pag.index('  <section class="ct-paso" id="ctPaso%d"' % n)
        pag = pag[:i] + aviso + pag[i:]
        j = pag.index('\n  </section>', pag.index('id="ctPaso%d"' % n)) + len('\n  </section>')
        pag = pag[:j] + '\n' + sigue + pag[j:]
        out.append({'archivo': paso_archivo(slug), 'icono': ico, 'menu': nombre, 'titulo': nombre,
                    'lema': 'Tu estado de cuenta · cuenta %d de %d' % (n, len(PASOS)),
                    'entrada': '<b>%s.</b> %s' % (frase, desc), 'bloque': pag,
                    'cap_nav': tuple((paso_archivo(x[1]), x[3]) if x else None
                                     for x in (PASOS[k - 1] if k else None, sig)) + (len(PASOS), ('Cuenta', 'cuentas'))})
    return out
