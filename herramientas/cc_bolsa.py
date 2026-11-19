# -*- coding: utf-8 -*-
"""Séptima aplicación de la Calculadora Cívica: «Inviertes en la bolsa:
¿cuánto ISR pagas?» (19-11-2026, pendiente de la entrega de simuladores: el
autor pidió «simuladores de impuestos por ganancias, adquisiciones,
enajenaciones»; el autor dijo «continúa con los pendientes»).

Saca el ISR de una persona física por vender acciones en bolsa y por cobrar
dividendos, con la ley a la vista. Cotejado el 19-11-2026 contra el texto
vigente de la Cámara de Diputados (huella SHA-256 en cc_inmueble.LISR):

  - LISR, art. 129: 10 % definitivo sobre la ganancia del ejercicio por
    enajenar acciones en bolsas concesionadas o mercados reconocidos; la
    ganancia de cada emisora es precio de venta − comisiones de venta − costo
    promedio de adquisición (con sus comisiones), actualizado desde la
    adquisición hasta el mes inmediato anterior a la venta; las ganancias y
    pérdidas del año se suman; el intermediario hace la cuenta y da la
    constancia; la pérdida se disminuye solo de ganancias de la misma clase
    del ejercicio o de los diez siguientes; no aplica a quien tenga 10 % o
    más de la emisora y venda 10 % o más en 24 meses, ni fuera de bolsa (sus
    numerales 1 a 4). Se declara junto con la anual (art. 150).
  - LISR, art. 140: el dividendo se acumula y puede acreditarse el ISR de la
    sociedad (dividendo × 1.4286 × 30 %, la tasa del art. 9); además, una
    tasa adicional de 10 % que retiene la sociedad y es pago definitivo.
  - Transitorios 2014 (art. noveno del decreto DOF 11-12-2013): fr. XXX, el
    10 % adicional solo sobre utilidades generadas desde 2014; fr. XXXII,
    acciones compradas antes de 2014 pueden tomar el promedio de los últimos
    22 precios de cierre (no lo calculamos: no tenemos esos precios).

**La cuenta la hace el navegador** con el INPC de la base (la misma serie del
simulador de inmuebles); no usa tarifa, así que vale para ventas de 2014 al
último mes con INPC. Nada se guarda ni se envía. Es una cuenta aproximada
(derivado): la definitiva es la constancia de tu casa de bolsa.
Lo llama apartados.insp_nativa() (INSP_NATIVAS['ccbolsa']).
"""
import html
import json

from presupuesto_modulos import chip
import cc_inmueble

ESTILOS = ['cc-inmueble.css']
SCRIPTS = ['cc-bolsa.js']
DESDE = 2014  # el art. 129 vigente rige desde el 1 de enero de 2014
FACTOR_DIV = 1.4286  # LISR, art. 140, primer párrafo
TASA_PM = 30  # LISR, art. 9


def esc(t):
    return html.escape(str(t))


def datos(base):
    d = cc_inmueble.datos(base)
    ua, um = d['inpc_ult']
    return {'anio': d['anio'], 'desde': DESDE, 'inpc': d['inpc'], 'inpc_ult': [ua, um],
            'factor_div': FACTOR_DIV, 'tasa_pm': TASA_PM,
            'f': {'inpc': d['f']['inpc'], 'inpc_url': d['f']['inpc_url']}}


def construir(base, ref):
    D = datos(base)
    MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    ult = '%s de %d' % (MES[D['inpc_ult'][1] - 1], D['inpc_ult'][0])
    meses = ''.join('<option value="%d">%s</option>' % (i + 1, m) for i, m in enumerate(MES))
    anios_v = ''.join('<option value="%d"%s>%d</option>' % (a, ' selected' if a == D['anio'] else '', a)
                      for a in range(D['inpc_ult'][0], DESDE - 1, -1))
    anios_c = ''.join('<option value="%d"%s>%d</option>' % (a, ' selected' if a == 2020 else '', a)
                      for a in range(D['inpc_ult'][0], min(D['inpc']) - 1, -1))
    L = cc_inmueble.LISR
    ley = lambda arts: '<a href="%s">%s</a>' % (esc(L['url']), esc(arts))
    return '''<div class="ci" id="cbRaiz">
  <section class="ci-arranque" aria-labelledby="cbTit">
    <p class="ci-kicker">Calculadora Cívica · simulador</p>
    <h2 class="ci-grande" id="cbTit">Inviertes en la bolsa: ¿cuánto ISR pagas?</h2>
    <p class="ci-txt">Escribe lo que pagaste por tus acciones, en cuánto las vendiste y los dividendos que cobraste. La página saca, paso por paso y con su artículo, el <b>10 % de ISR sobre tu ganancia</b> ({a129}) y el <b>10 % que te retienen de los dividendos</b> ({a140}).</p>
    <p class="ci-privado">🔒 La cuenta la hace tu navegador: lo que escribes no se guarda ni se envía.</p>
  </section>

  <form class="ci-form" id="cbForm" novalidate>
    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">1</span> Una venta de acciones en bolsa</legend>
      <label class="ci-et" for="cbV">Lo que recibiste por la venta (pesos)</label>
      <input class="ci-in" id="cbV" inputmode="decimal" autocomplete="off" placeholder="Ej.: 150,000">
      <label class="ci-et" for="cbCv">Comisiones de la venta (pesos)</label>
      <input class="ci-in" id="cbCv" inputmode="decimal" autocomplete="off" placeholder="Opcional">
      <div class="ci-fila">
        <div><label class="ci-et" for="cbVa">Año de la venta</label><select class="ci-in" id="cbVa">{anios_v}</select></div>
        <div><label class="ci-et" for="cbVm">Mes</label><select class="ci-in" id="cbVm">{meses}</select></div>
      </div>
      <label class="ci-et" for="cbC">Lo que pagaste al comprar esas acciones, con comisiones (pesos)</label>
      <input class="ci-in" id="cbC" inputmode="decimal" autocomplete="off" placeholder="Ej.: 100,000">
      <div class="ci-fila">
        <div><label class="ci-et" for="cbCa">Año de la compra</label><select class="ci-in" id="cbCa">{anios_c}</select></div>
        <div><label class="ci-et" for="cbCm">Mes</label><select class="ci-in" id="cbCm">{meses}</select></div>
      </div>
      <p class="ci-pista">Si compraste en varias fechas, la ley usa el costo promedio: tu casa de bolsa lo lleva y lo trae tu constancia.</p>
    </fieldset>

    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">2</span> El resto de tu año <small>(opcional)</small></legend>
      <label class="ci-et" for="cbO">Ganancia o pérdida de tus otras ventas del año (pesos; una pérdida, con signo menos)</label>
      <input class="ci-in" id="cbO" inputmode="decimal" autocomplete="off" placeholder="Ej.: -20,000">
      <label class="ci-et" for="cbP">Pérdidas de años anteriores que aún no aprovechas, ya actualizadas (pesos)</label>
      <input class="ci-in" id="cbP" inputmode="decimal" autocomplete="off" placeholder="Vienen en tus constancias">
    </fieldset>

    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">3</span> Dividendos <small>(opcional)</small></legend>
      <label class="ci-et" for="cbD">Dividendos que te pagaron empresas mexicanas, antes de la retención (pesos)</label>
      <input class="ci-in" id="cbD" inputmode="decimal" autocomplete="off" placeholder="Ej.: 8,000">
    </fieldset>
    <p class="ci-acciones"><button type="submit" class="ci-boton">Saca la cuenta</button></p>
  </form>

  <section class="ci-res" id="cbRes" aria-live="polite" hidden>
    <h2 class="ci-tit"><span class="ci-n" aria-hidden="true">4</span> Tu cuenta, paso por paso {chip_d}</h2>
    <div class="ci-total" id="cbTotal"></div>
    <div class="ci-tabla-caja"><table class="ci-tabla"><caption>Cómo se llega al impuesto</caption>
      <thead><tr><th scope="col">Paso</th><th scope="col">Pesos</th><th scope="col">Regla</th></tr></thead>
      <tbody id="cbPasos"></tbody></table></div>
    <p class="ci-nota" id="cbNota"></p>
  </section>

  <aside class="ci-aviso" aria-labelledby="cbLeeTit">
    <h2 class="ci-tit" id="cbLeeTit"><span aria-hidden="true">📐</span> Cómo se calcula</h2>
    <ol class="ci-lista">
      <li><b>La ganancia de cada venta</b> = lo que recibiste − las comisiones de la venta − lo que te costaron las acciones, con sus comisiones ({a129}).</li>
      <li><b>El costo se actualiza por inflación</b> desde la compra hasta el mes anterior a la venta ({a129}): el INPC del mes anterior a la venta entre el del mes de la compra, a cuatro decimales y nunca menor que 1 ({a17a}). Es la lectura usual; leído al pie de la letra, el art. 17-A tomaría en cada extremo el mes anterior. En la base, el último INPC es el de {ult}.</li>
      <li><b>Se suman las ganancias y las pérdidas de todo el año</b>, de todas tus emisoras y casas de bolsa. Si el año deja pérdida, no pagas y la puedes restar de tus ganancias de los <b>diez años siguientes</b>; si teniendo ganancia no la restas, pierdes ese derecho por esa cantidad.</li>
      <li><b>El impuesto es 10 % de la ganancia</b> que queda, y es definitivo: se declara y se paga junto con tu declaración anual ({a150}).</li>
      <li><b>Los dividendos</b> de empresas mexicanas llevan una retención de 10 % que es definitiva ({a140}). Además, el dividendo se suma a tus ingresos del año: puedes sumarle el ISR que ya pagó la empresa (dividendo × {fd} × {tpm} %) y restar ese mismo ISR del impuesto de tu declaración anual. Esa parte depende del resto de tus ingresos, así que aquí solo te damos sus dos cifras.</li>
    </ol>
    <p><b>Lo que esta cuenta no hace:</b> no es tu declaración ni sustituye la constancia de tu casa de bolsa, que hace la cuenta oficial. No aplica si tienes 10 % o más de la empresa y vendes 10 % o más en 24 meses, si vendes fuera de bolsa o en operaciones de registro o cruces protegidos, ni a acciones que no estén entre el gran público inversionista: ahí rige otra regla (los numerales 1 a 4 del art. 129). Si compraste antes de 2014, la ley te deja tomar como costo el promedio de los últimos 22 precios de cierre de 2013 (transitorio 2014, fr. XXXII), y los dividendos de utilidades de antes de 2014 no llevan el 10 % adicional (fr. XXX): no tenemos esos datos, así que no los calculamos. Los préstamos de valores y los derivados (art. 20) tampoco entran.</p>
    <p class="ci-fuentes">Fuentes: {f_lisr} · {f_cff} · INPC: <a href="{inpc_url}">{f_inpc}</a> {chip_o}.</p>
    <p class="ci-hermanas">Sigue con la Calculadora: <a href="herramienta-calculadora-inmueble.html">🏠 Vendes una casa o un terreno</a> · <a href="herramienta-calculadora-ticket.html">🧾 Tu estado de cuenta</a></p>
  </aside>
  <script type="application/json" id="cbDatos">{datos}</script>
</div>'''.format(
        meses=meses, anios_v=anios_v, anios_c=anios_c, ult=ult, chip_d=chip('derivado'), chip_o=chip('oficial'),
        fd=FACTOR_DIV, tpm=TASA_PM,
        a129=ley('LISR, art. 129'), a140=ley('LISR, art. 140'), a150=ley('LISR, arts. 129 y 150'),
        a17a='<a href="%s">CFF, art. 17-A</a>' % esc(cc_inmueble.CFF['url']),
        f_lisr='<a href="%s">%s</a> (huella SHA-256 <code>%s…</code>)' % (esc(L['url']), esc(L['tx']), L['sha256'][:12]),
        f_cff='<a href="%s">%s</a> (huella SHA-256 <code>%s…</code>)' % (esc(cc_inmueble.CFF['url']), esc(cc_inmueble.CFF['tx']), cc_inmueble.CFF['sha256'][:12]),
        inpc_url=esc(D['f']['inpc_url']), f_inpc=esc(D['f']['inpc']), datos=cc_inmueble._json(D))
