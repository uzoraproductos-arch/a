# -*- coding: utf-8 -*-
"""Sexta aplicación de la Calculadora Cívica: «Vendo una casa o un terreno:
¿cuánto ISR causa?» (19-11-2026, pedido del autor: «simuladores de impuestos
por ganancias, adquisiciones, enajenaciones»; «empieza con las tres entregas»).

Saca el pago provisional del ISR por la venta de un inmueble de una persona
física, el que calcula y entera el notario (LISR, art. 126), con la ley a la
vista. Cotejado el 19-11-2026 contra los textos vigentes de la Cámara de
Diputados (huella SHA-256 abajo):

  - LISR (última reforma DOF 13-11-2026, decreto sha256 f622599027d4…; sin cambios en estos artículos): art. 93, fr. XIX, inciso a (casa
    habitación exenta hasta 700,000 UDIS, con su proporción); art. 121
    (deducciones; costo actualizado de al menos 10 % de la venta); art. 124
    (terreno y construcción, 20 % de terreno si no se puede separar, 3 % anual
    a la construcción con piso de 20 %, actualización hasta el mes anterior a
    la venta; mejoras con el mismo trato); art. 126 (ganancia entre años,
    hasta 20, con la tarifa del art. 96 por los meses transcurridos del año, y
    el resultado por los mismos años); art. 127 (5 % de la ganancia para la
    entidad, acreditable contra el art. 126).
  - CFF (última reforma DOF 09-04-2026), art. 17-A: el factor divide el INPC
    «del mes anterior al más reciente del periodo» entre el «del mes anterior
    al más antiguo»; si el del mes anterior no se ha publicado, se usa el
    último publicado; si sale menor que 1, es 1. Usamos la lectura usual en
    la práctica (INPC del mes anterior a la venta ÷ INPC del mes de compra) y
    la página dice que, al pie de la letra, cada extremo correría un mes.

Lo que la ley no fija y decidimos a la vista: los años transcurridos se
cuentan completos (ni la LISR ni su Reglamento dicen cómo contar una fracción;
si no pasa un año, se divide entre 1).

**La cuenta la hace el navegador con los datos de la base**: el INPC de la
máquina del tiempo del peso (Banxico, serie SP1), la tarifa mensual del art. 96
del Anexo 8 de la RMF 2026 (calculadora_civica.tarifa_mensual) y la UDI de
Banxico (docs/sat/udi.json, anclar_udi.py). Por eso solo vale para ventas del
año de esa tarifa (lo lee de su renglón «RMF AAAA»). Nada se guarda ni se envía.

No es la declaración ni sustituye al notario: es una cuenta aproximada
(derivado). El impuesto del año se recalcula en la declaración anual (art. 120).
Lo llama apartados.insp_nativa() (INSP_NATIVAS['ccinmueble']).
"""
import html
import json
import os
import re

from presupuesto_modulos import chip

ESTILOS = ['cc-inmueble.css']
SCRIPTS = ['cc-inmueble.js']
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UDI = os.path.join(RAIZ, 'docs', 'sat', 'udi.json')
LISR = {'tx': 'Ley del Impuesto sobre la Renta, texto vigente (Cámara de Diputados, última reforma DOF 13-11-2026)',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LISR.pdf',
        'sha256': '803c2875c09c751c1966b8eb4dca99f460b237da4ef67ee04b4fa325d8c2f786'}
CFF = {'tx': 'Código Fiscal de la Federación, texto vigente (Cámara de Diputados, última reforma DOF 09-04-2026)',
       'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CFF.pdf',
       'sha256': 'be7427b20d3552775ab42018f8f87578078770095bf8cf46322c25e36ee3aa7d'}
EXENTO_UDIS = 700000


def esc(t):
    return html.escape(str(t))


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def datos(base):
    p = base['finanzas_sexenales']['peso']
    tm = base['calculadora_civica']['tarifa_mensual']
    u = json.load(open(UDI, encoding='utf-8'))
    inpc = {int(a): v for a, v in p['inpc']['mensual'].items()}
    ult = max(inpc)
    # El año de la tarifa sale de su propio renglón («Anexo 8 de la RMF 2026»):
    # cuando la base traiga la del año nuevo, el simulador cambia de año solo.
    m = re.search(r'RMF (\d{4})', tm['ley'])
    if not m:
        raise SystemExit('cc_inmueble: la tarifa mensual no dice de qué RMF es: %r' % tm['ley'])
    return {
        'anio': int(m.group(1)),
        'inpc': inpc, 'inpc_ult': [ult, len(inpc[ult])],
        'tarifa': tm['renglones'],
        'udi': {'v': u['valor'], 'f': u['fecha']}, 'exento_udis': EXENTO_UDIS,
        'f': {'inpc': p['fuentes'][p['inpc']['f']]['corto'], 'inpc_url': p['fuentes'][p['inpc']['f']]['url'],
              'tarifa': '%s (%s)' % (tm['ley'], tm['fuente']), 'udi': u['fuente'], 'udi_url': u['url']},
    }


def construir(base, ref):
    D = datos(base)
    MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    ult = '%s de %d' % (MES[D['inpc_ult'][1] - 1], D['inpc_ult'][0])
    lim = D['udi']['v'] * EXENTO_UDIS
    meses = ''.join('<option value="%d">%s</option>' % (i + 1, m) for i, m in enumerate(MES))
    anios = ''.join('<option value="%d"%s>%d</option>' % (a, ' selected' if a == 2010 else '', a) for a in range(D['anio'], min(D['inpc']) - 1, -1))
    ley = lambda arts: '<a href="%s">%s</a>' % (esc(LISR['url']), esc(arts))
    return '''<div class="ci" id="ciRaiz">
  <section class="ci-arranque" aria-labelledby="ciTit">
    <p class="ci-kicker">Calculadora Cívica · simulador</p>
    <h2 class="ci-grande" id="ciTit">Vendes una casa o un terreno: ¿cuánto ISR causa?</h2>
    <p class="ci-txt">Escribe cuánto te costó, cuándo lo compraste y en cuánto lo vendes. La página saca, paso por paso y con su artículo, el <b>pago provisional del ISR</b> que el notario calcula y entera por ti ({a126}), cuánto le toca a tu estado ({a127}) y si tu casa habitación queda exenta ({a93}).</p>
    <p class="ci-privado">🔒 La cuenta la hace tu navegador: lo que escribes no se guarda ni se envía.</p>
  </section>

  <form class="ci-form" id="ciForm" novalidate>
    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">1</span> La venta</legend>
      <label class="ci-et" for="ciV">Precio de venta (pesos)</label>
      <input class="ci-in" id="ciV" inputmode="decimal" autocomplete="off" placeholder="Ej.: 3,500,000">
      <label class="ci-et" for="ciVm">Mes de la venta, en {anio}</label>
      <select class="ci-in" id="ciVm">{meses}</select>
      <p class="ci-pista">Solo ventas de {anio}: la tarifa de otro año no está en la base.</p>
      <label class="ci-check"><input type="checkbox" id="ciCasa"> Es mi casa habitación y no he vendido otra exenta en los últimos tres años</label>
    </fieldset>

    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">2</span> La compra</legend>
      <label class="ci-et" for="ciC">Lo que pagaste al comprar (pesos)</label>
      <input class="ci-in" id="ciC" inputmode="decimal" autocomplete="off" placeholder="Ej.: 900,000">
      <div class="ci-fila">
        <div><label class="ci-et" for="ciCa">Año de la compra</label><select class="ci-in" id="ciCa">{anios}</select></div>
        <div><label class="ci-et" for="ciCm">Mes</label><select class="ci-in" id="ciCm">{meses}</select></div>
      </div>
      <label class="ci-et" for="ciT">Parte del precio que fue el terreno (%)</label>
      <input class="ci-in" id="ciT" inputmode="decimal" autocomplete="off" placeholder="Si no lo sabes, déjalo vacío: la ley toma 20 %">
      <p class="ci-pista">Si compraste solo un terreno, escribe 100.</p>
    </fieldset>

    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">3</span> Lo que también se deduce <small>(opcional)</small></legend>
      <label class="ci-et" for="ciM">Construcciones, mejoras o ampliaciones, con factura (pesos)</label>
      <input class="ci-in" id="ciM" inputmode="decimal" autocomplete="off" placeholder="No incluye mantenimiento">
      <div class="ci-fila">
        <div><label class="ci-et" for="ciMa">Año de la mejora</label><select class="ci-in" id="ciMa">{anios}</select></div>
        <div><label class="ci-et" for="ciMm">Mes</label><select class="ci-in" id="ciMm">{meses}</select></div>
      </div>
      <label class="ci-et" for="ciGc">Gastos de notario, impuestos y derechos cuando compraste (pesos)</label>
      <input class="ci-in" id="ciGc" inputmode="decimal" autocomplete="off">
      <label class="ci-et" for="ciGv">Gastos de la venta que pagas tú: avalúo, notario, impuesto local y comisión de la inmobiliaria (pesos)</label>
      <input class="ci-in" id="ciGv" inputmode="decimal" autocomplete="off">
    </fieldset>
    <p class="ci-acciones"><button type="submit" class="ci-boton">Saca la cuenta</button></p>
  </form>

  <section class="ci-res" id="ciRes" aria-live="polite" hidden>
    <h2 class="ci-tit"><span class="ci-n" aria-hidden="true">4</span> Tu cuenta, paso por paso {chip_d}</h2>
    <div class="ci-total" id="ciTotal"></div>
    <div class="ci-tabla-caja"><table class="ci-tabla"><caption>Cómo se llega al pago provisional</caption>
      <thead><tr><th scope="col">Paso</th><th scope="col">Pesos</th><th scope="col">Regla</th></tr></thead>
      <tbody id="ciPasos"></tbody></table></div>
    <p class="ci-nota" id="ciNota"></p>
  </section>

  <aside class="ci-aviso" aria-labelledby="ciLeeTit">
    <h2 class="ci-tit" id="ciLeeTit"><span aria-hidden="true">📐</span> Cómo se calcula</h2>
    <ol class="ci-lista">
      <li><b>El costo de lo que compraste.</b> Se separa el terreno de la construcción; si no se puede, el terreno es el 20 % ({a124}). La construcción pierde 3 % por cada año que pasó, sin bajar de 20 % de lo que costó.</li>
      <li><b>Se actualiza por inflación</b> con el INPC: el del mes anterior a la venta entre el del mes de la compra. El factor va a cuatro decimales y nunca es menor que 1; si el INPC del mes anterior aún no se publica, se usa el último ({a17a}). Es la lectura usual; leído al pie de la letra, el art. 17-A tomaría en cada extremo el mes anterior. En la base, el último es el de {ult}.</li>
      <li><b>El costo actualizado vale al menos 10 % del precio de venta</b> ({a121}). Las mejoras se tratan igual que la construcción; los gastos de la compra se actualizan desde su mes.</li>
      <li><b>Ganancia</b> = precio de venta − todo lo que se deduce. Si es tu casa habitación y la vendes en hasta 700,000 UDIS, no pagas ISR; si la vendes en más, solo pagas por la parte que excede, con las deducciones en la misma proporción ({a93}). Con la UDI del {udi_f} ({udi_v} pesos), el tope es de {lim} {chip_d}.</li>
      <li><b>El pago provisional</b>: la ganancia se divide entre los años completos que pasaron (al menos 1 y hasta 20), a ese resultado se le aplica la tarifa mensual del ISR multiplicada por el número de mes de la venta, y el impuesto se multiplica por los mismos años ({a126}).</li>
      <li><b>Lo de tu estado</b>: 5 % de la ganancia se paga a la entidad donde está el inmueble y se resta del pago provisional; si fuera mayor, a la entidad solo le toca el pago provisional ({a127}).</li>
    </ol>
    <p><b>Lo que esta cuenta no hace:</b> no es tu declaración ni sustituye al notario. No cuenta los años con fracción (contamos años completos: la ley no dice cómo contar una fracción), ni los impuestos que le tocan a quien compra. El impuesto definitivo se calcula en tu declaración anual, sumando la parte de la ganancia que corresponde al año (art. 120), y puede salir distinto. Si pierdes, la pérdida se aprovecha en tu declaración (art. 122).</p>
    <p class="ci-fuentes">Fuentes: {f_lisr} · {f_cff} · INPC: <a href="{inpc_url}">{f_inpc}</a> {chip_o} · Tarifa: {f_tarifa} {chip_o} · UDI: <a href="{udi_url}">{f_udi}</a> {chip_o}.</p>
    <p class="ci-hermanas">Sigue con la Calculadora: <a href="herramienta-calculadora-ticket.html">🧾 Tu estado de cuenta</a> · <a href="datos-padron-sat-regimenes.html">📑 Cuántos contribuyentes hay en cada régimen</a></p>
  </aside>
  <script type="application/json" id="ciDatos">{datos}</script>
</div>'''.format(
        anio=D['anio'], meses=meses, anios=anios, ult=ult, udi_f=esc(D['udi']['f']), udi_v=format(D['udi']['v'], '.6f'),
        lim='$' + format(round(lim, 2), ',.2f'), chip_d=chip('derivado'), chip_o=chip('oficial'),
        a93=ley('LISR, art. 93, fr. XIX, a'), a121=ley('LISR, art. 121'), a124=ley('LISR, art. 124'), a126=ley('LISR, art. 126'),
        a127=ley('LISR, art. 127'), a17a='<a href="%s">CFF, art. 17-A</a>' % esc(CFF['url']),
        f_lisr='<a href="%s">%s</a> (huella SHA-256 <code>%s…</code>)' % (esc(LISR['url']), esc(LISR['tx']), LISR['sha256'][:12]),
        f_cff='<a href="%s">%s</a> (huella SHA-256 <code>%s…</code>)' % (esc(CFF['url']), esc(CFF['tx']), CFF['sha256'][:12]),
        inpc_url=esc(D['f']['inpc_url']), f_inpc=esc(D['f']['inpc']), f_tarifa=esc(D['f']['tarifa']),
        udi_url=esc(D['f']['udi_url']), f_udi=esc(D['f']['udi']), datos=_json(D))
