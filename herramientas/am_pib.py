# -*- coding: utf-8 -*-
"""Cuarta aplicacion de Costo Ambiental: «El PIB no alcanza», en pagina
propia (16-10-2026). Sustituye al marco que cargaba la portada entera
(index.html?ir=ambiente&ancla=eb-ampib).

Lo que antes pintaban renderCuentasEcologicas() y sus cinco ayudantes del
motor (renderCeeCascada, renderCeeSimulador, ceeRecalcular, renderCee-
Desglose, renderCeeCiegos, renderCeeJuridico) se escribe aqui, desde la
coleccion `cuentas_ecologicas` de la base. El JS (am-pib.js) solo anima la
cascada, mueve el simulador (la misma aritmetica de ceeRecalcular) y cambia
la unidad del desglose; no escribe ninguna cifra de la base.

Correcciones editoriales frente al motor, cotejadas con el comunicado de
prensa 150/25 del INEGI (CEEM 2024, 1 de diciembre de 2025):

1. Agotamiento por componente. La base reparte el total con 46/28/26 % y
   marca los montos como derivados; el comunicado los publica (Tabla 1,
   p. 2): hidrocarburos 66,319.0, forestales 40,848.0, agua subterranea
   36,853.0 mdp (suman 144,020.0). Aqui van esos, como oficiales, y el
   reparto en % pasa a derivado.
2. PINE. El INEGI lo publica redondeado: «25.7 billones» y «76.6 % del
   PIB». La base lo guarda como 25,700,000 mdp, que aparenta una precision
   que el documento no da. Aqui se escribe «$25.7 billones» y, como el
   consumo de capital fijo y el Producto Interno Neto se derivan restando
   ese PINE, se dan como rango (AGENTS.md §2): el PINE publicado cae entre
   25.65 y 25.75 billones; el punto medio es la cifra que usa el motor.
3. «Seis pesos de daño por cada peso» -> «Casi seis» (la razon es 5.94).
4. «Las emisiones al aire [son] casi dos terceras partes de toda la cuenta
   ambiental» -> son 60.3 % (832,799.4 / 1,382,214): «seis de cada diez».

Lo llama apartados.insp_nativa() (INSP_NATIVAS['ampib']).
"""
import html
import json

from presupuesto_modulos import chip, mdp

ESTILOS = ['am-pib.css']
SCRIPTS = ['am-pib.js']

URL_CEEM = 'https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/ee/CEEM2024_CP.pdf'
DOC_CEEM = 'INEGI, Cuentas Económicas y Ecológicas de México 2024, comunicado de prensa 150/25'

# Tabla 1 del comunicado (p. 2), millones de pesos corrientes y % del PIB.
# La base aun reparte el total con porcentajes; ver la nota del modulo.
AGOT_INEGI = {'hidrocarburos': (66319.0, 0.2), 'forestal': (40848.0, 0.1), 'agua': (36853.0, 0.1)}

# Media unidad del ultimo digito publicado del PINE (25.7 billones).
PINE_MEDIO_INTERVALO = 50000.0

# Correcciones de redaccion sobre textos de la base (si la base ya trae el
# texto corregido, el reemplazo no hace nada).
TEXTOS = [
    ('Seis pesos de daño por cada peso de protección', 'Casi seis pesos de daño por cada peso de protección'),
    ('casi dos terceras partes de toda la cuenta ambiental', 'seis de cada diez pesos de toda la cuenta ambiental (60.3%)'),
]

TONOS = {'base': 'ap-t-base', 'resta': 'ap-t-resta', 'subtotal': 'ap-t-sub', 'resultado': 'ap-t-res'}


def esc(t):
    return html.escape(str(t if t is not None else ''), quote=True)


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def _tx(t):
    t = str(t or '')
    for a, b in TEXTOS:
        t = t.replace(a, b)
    return t


def m0(v):
    return mdp(v, 0)


def billones(v):
    return '$%.1f billones' % (v / 1e6)


def _fuente(texto='CEEM 2024', pagina=None):
    return ('<a class="ap-fuente" href="%s" target="_blank" rel="noopener">%s%s ↗</a>'
            % (URL_CEEM, esc(texto), (', p. %s' % pagina) if pagina else ''))


def _op(texto):
    return '<span class="ap-op"><b>Operación:</b> %s</span>' % texto


def construir(base, ref):
    c = base['cuentas_ecologicas']
    pib = float(c['pib_mdp'])
    casc = {p['id']: p for p in c['cascada']}
    ctada = float(c['ctada']['total_mdp'])
    pine = float(casc['pine']['monto_mdp'])
    gpa = c['gasto_proteccion_ambiental']
    ej = c['ejercicio']

    # Rango del consumo de capital fijo y del PIN (derivados del PINE publicado).
    pine_min, pine_max = pine - PINE_MEDIO_INTERVALO, pine + PINE_MEDIO_INTERVALO
    ccf_min, ccf_max = pib - ctada - pine_max, pib - ctada - pine_min
    ccf_mid = (ccf_min + ccf_max) / 2
    pin_min, pin_max = pine_min + ctada, pine_max + ctada
    pin_mid = (pin_min + pin_max) / 2
    assert abs(ccf_mid - casc['ccf']['monto_mdp']) < 1 and abs(pin_mid - casc['pin']['monto_mdp']) < 1, \
        'El punto medio debe ser la cifra de la base'

    # Agotamiento: la Tabla 1 del INEGI.
    agot = c['agotamiento']
    comps_agot = []
    for x in agot['componentes']:
        monto, pp = AGOT_INEGI.get(x['id'], (x['monto_mdp'], None))
        comps_agot.append(dict(x, monto_mdp=monto, pct_pib=pp, estado='oficial' if x['id'] in AGOT_INEGI else x['estado']))
    assert abs(sum(x['monto_mdp'] for x in comps_agot) - agot['total_mdp']) < 1

    # ---------------- Cascada ----------------
    filas, tope = [], 100.0
    for k, p in enumerate(c['cascada']):
        ancho = p['monto_mdp'] / pib * 100
        if p['signo'] == 'resta':
            izq = tope - ancho
            tope = izq
        else:
            izq, tope = 0.0, ancho
        rango = ''
        if p['id'] == 'ccf':
            cifra = m0(p['monto_mdp'])
            rango = ('<span class="ap-rango">Entre <b>%s</b> y <b>%s</b>; punto medio <b>%s</b>. %s</span>'
                     % (m0(ccf_min), m0(ccf_max), m0(ccf_mid),
                        _op('PIB − costos ambientales (CTADA) − PINE. El INEGI publica el PINE redondeado a «25.7 billones», '
                            'es decir, entre $25.65 y $25.75 billones: con cada extremo sale un extremo del rango, y el punto medio es (mínimo + máximo) ÷ 2. '
                            'La cifra exacta está en los tabulados de las cuentas nacionales del INEGI; la plataforma aún no la integra.')))
            pct = '%.1f%% del PIB' % p['pct_pib']
        elif p['id'] == 'pin':
            cifra = m0(p['monto_mdp'])
            rango = ('<span class="ap-rango">Entre <b>%s</b> y <b>%s</b>; punto medio <b>%s</b>. %s</span>'
                     % (m0(pin_min), m0(pin_max), m0(pin_mid),
                        _op('PINE + costos ambientales (CTADA), con el PINE entre $25.65 y $25.75 billones; punto medio = (mínimo + máximo) ÷ 2.')))
            pct = '%.1f%% del PIB' % p['pct_pib']
        elif p['id'] == 'pine':
            cifra = billones(p['monto_mdp'])
            rango = '<span class="ap-rango">El INEGI lo publica así, redondeado: «25.7 billones de pesos», %.1f%% del PIB. %s</span>' % (p['pct_pib'], _fuente('CEEM 2024', 1))
            pct = '%.1f%% del PIB' % p['pct_pib']
        elif p['id'] == 'pib':
            cifra = m0(p['monto_mdp'])
            rango = '<span class="ap-rango">PIB nacional a precios de mercado %s %s</span>' % (ej, ref(c['ref_pib']))
            pct = '100% del PIB'
        else:
            cifra = m0(p['monto_mdp'])
            rango = '<span class="ap-rango">%s</span>' % _fuente('CEEM 2024, Tabla 1', 2)
            pct = '%.1f%% del PIB' % p['pct_pib']
        filas.append(
            '<li class="ap-casc-fila %s" data-paso="%d" data-cifra="%s" data-et="%s">'
            '<div class="ap-casc-cab"><span class="ap-casc-et">%s</span>'
            '<span class="ap-casc-cifra">%s</span><span class="ap-casc-pct">%s</span></div>'
            '<span class="ap-casc-riel" aria-hidden="true"><span class="ap-casc-barra" style="--izq:%.3f%%;--w:%.3f%%"></span></span>'
            '<p class="ap-casc-glosa">%s %s</p>%s</li>'
            % (TONOS[p['signo']], k, esc(cifra), esc(p['etiqueta'].lstrip('−= ')), esc(p['etiqueta']), cifra, pct,
               izq, max(0.35, ancho), esc(p['glosa']), chip(p['estado']), rango))

    # ---------------- Desglose ----------------
    def rubro(d, comps, titulo, icono, clave, nota):
        mayor = max(x['monto_mdp'] for x in comps)
        items = []
        for x in comps:
            de100 = x['monto_mdp'] / ctada * 100
            pp = ('%.1f%% del PIB' % x['pct_pib']) if x.get('pct_pib') is not None else '—'
            items.append(
                '<li class="ap-comp"><span class="ap-comp-ico" aria-hidden="true">%s</span>'
                '<span class="ap-comp-nom">%s</span>'
                '<span class="ap-comp-val" data-pesos="%s" data-pib="%s" data-de100="%s">%s</span>'
                '<span class="ap-comp-riel" aria-hidden="true"><span class="ap-comp-barra" style="--w:%.1f%%"></span></span>'
                '<span class="ap-comp-glosa">%s %s</span></li>'
                % (x['icono'], esc(x['nombre']), esc(m0(x['monto_mdp'])), esc(pp), esc('$%.2f' % de100), m0(x['monto_mdp']),
                   x['monto_mdp'] / mayor * 100, esc(_tx(x['glosa'])), chip(x['estado'])))
        return ('<article class="ap-rubro ap-rubro-%s"><header class="ap-rub-cab"><span class="ap-rub-ico" aria-hidden="true">%s</span>'
                '<div><h3 class="ap-rub-tit">%s</h3><p class="ap-rub-tot"><b>%s</b> · %.1f%% del PIB %s</p></div></header>'
                '<p class="ap-rub-def">%s</p><ul class="ap-comps">%s</ul><p class="ap-rub-nota">%s</p></article>'
                % (clave, icono, titulo, m0(d['total_mdp']), d['pct_pib'], chip(d['estado']), esc(d['definicion']), ''.join(items), nota))

    reparto = ', '.join('%s %.1f%%' % (x['nombre'].replace('Agotamiento de ', '').replace('recursos ', ''), x['monto_mdp'] / agot['total_mdp'] * 100)
                        for x in comps_agot)
    nota_agot = ('Montos de la Tabla 1 del comunicado del INEGI (p. 2) %s. Reparto del rubro, derivado (monto ÷ %s): %s.'
                 % (_fuente('CEEM 2024', 2), m0(agot['total_mdp']), reparto))
    deg = c['degradacion']
    aire = next(x for x in deg['componentes'] if x['id'] == 'aire')
    nota_deg = ('Montos y porcentajes de la Tabla 1 del comunicado del INEGI (p. 2) %s. Las emisiones al aire son %.1f%% de todo el costo ambiental '
                '(derivado: %s ÷ %s).' % (_fuente('CEEM 2024', 2), aire['monto_mdp'] / ctada * 100, m0(aire['monto_mdp']), m0(ctada)))

    ratio = ctada / gpa['monto_mdp']
    monedas = int(ratio)
    resto = ratio - monedas
    coins_dano = ''.join('<i class="ap-moneda ap-moneda-dano"></i>' for _ in range(monedas)) + \
        '<i class="ap-moneda ap-moneda-dano ap-moneda-parte" style="--p:%.0f%%"></i>' % (resto * 100)

    # ---------------- Puntos ciegos y juridico ----------------
    ciegos = ''.join(
        '<article class="ap-cie"><span class="ap-cie-n" aria-hidden="true">%d</span><h3 class="ap-cie-h">%s</h3><p class="ap-cie-tx">%s</p></article>'
        % (i + 1, esc(_tx(p['titulo'])), esc(_tx(p['texto']))) for i, p in enumerate(c['puntos_ciegos']))
    jur = ''.join(
        '<details class="ap-jur"><summary><span class="ap-jur-ico" aria-hidden="true">%s</span><span class="ap-jur-h">%s</span>'
        '<span class="ap-jur-fund">%s</span></summary><p class="ap-jur-tx">%s</p></details>'
        % (x['icono'], esc(x['titulo']), esc(x['fundamento']), esc(x['texto'])) for x in c['implicaciones_juridicas'])

    ccf_pct = casc['ccf']['monto_mdp'] / pib * 100
    ctada_pct = ctada / pib * 100
    datos = {'ej': ej, 'pib': pib, 'pine': pine, 'ccfPct': round(ccf_pct, 1), 'ctadaPct': round(ctada_pct, 1)}

    return '''<div class="ap" id="apRaiz">
  <section class="ap-arranque" aria-labelledby="apTit">
    <p class="ap-kicker">Costo ambiental · aplicación 4</p>
    <h2 class="ap-grande" id="apTit">El PIB dice {pib_b}. Lo que de verdad quedó: {pine_b}.</h2>
    <p class="ap-txt">{entrada}</p>
    <div class="ap-trio">
      <div class="ap-trio-d"><span class="ap-trio-k">📣 Se anunció (PIB {ej})</span><b>{pib_m}</b>{chip_pib}</div>
      <div class="ap-trio-d ap-trio-mal"><span class="ap-trio-k">🌫️ Costó al ambiente (CTADA)</span><b>{ctada_m}</b><span class="ap-trio-s">{ctada_pct}% del PIB</span>{chip_ctada}</div>
      <div class="ap-trio-d ap-trio-bien"><span class="ap-trio-k">🌱 Quedó de verdad (PINE)</span><b>{pine_b}</b><span class="ap-trio-s">{pine_pct}% del PIB</span>{chip_pine}</div>
    </div>
    <ol class="ap-indice" aria-label="Lo que hay en esta página">
      <li><a href="#apCascada"><span class="ap-n">1</span> La resta, paso a paso</a></li>
      <li><a href="#apSim"><span class="ap-n">2</span> Simula el crecimiento real</a></li>
      <li><a href="#apDesglose"><span class="ap-n">3</span> Qué se acabó y qué se ensució</a></li>
      <li><a href="#apCiegos"><span class="ap-n">4</span> Puntos ciegos y leyes</a></li>
    </ol>
  </section>

  <section class="ap-sec" id="apCascada" aria-labelledby="apCascTit">
    <h2 class="ap-tit" id="apCascTit"><span class="ap-n">1</span> De los {pib_b2} anunciados a los {pine_b2} que quedaron</h2>
    <p class="ap-txt">Cada renglón arranca donde terminó el anterior. Lo que se resta es lo que se gastó para producir: la maquinaria que se desgastó y lo que la naturaleza puso y nadie pagó.</p>
    <div class="ap-casc-mando" role="group" aria-label="Controles de la cascada">
      <button type="button" class="ap-btn ap-btn-pri" id="apPlay"><span aria-hidden="true">▶</span> <span id="apPlayTx">Reproducir la resta</span></button>
      <button type="button" class="ap-btn" id="apPrev" aria-label="Paso anterior"><span aria-hidden="true">⏮</span> Anterior</button>
      <button type="button" class="ap-btn" id="apNext" aria-label="Paso siguiente">Siguiente <span aria-hidden="true">⏭</span></button>
      <button type="button" class="ap-btn" id="apTodo">Ver completa</button>
    </div>
    <p class="ap-contador" id="apContador" aria-live="polite"></p>
    <ol class="ap-casc" id="apCascLista">
{filas}
    </ol>
    <p class="ap-remate">De cada $100 que el país anunció haber producido en {ej}, <strong>${pine_pct}</strong> quedaron después de reponer la maquinaria y de pagar la cuenta ambiental. {chip_pine} {f1}</p>
  </section>

  <section class="ap-sec ap-sim" id="apSim" aria-labelledby="apSimTit">
    <h2 class="ap-tit" id="apSimTit"><span class="ap-n">2</span> Simulador: ¿cuánto de ese crecimiento es real?</h2>
    <p class="ap-txt">Mueve los tres controles y ve qué le pasa al Producto Interno Neto Ecológico (PINE). El punto de partida son las cifras de {ej}.</p>
    <div class="ap-atajos" role="group" aria-label="Escenarios">
      <span class="ap-atajos-et">Escenarios:</span>
      <button type="button" class="ap-chipbtn" data-esc="base" aria-pressed="true">Como {ej}</button>
      <button type="button" class="ap-chipbtn" data-esc="espejismo" aria-pressed="false">🎭 Crece el PIB, crece el daño</button>
      <button type="button" class="ap-chipbtn" data-esc="limpio" aria-pressed="false">🌿 Crece el PIB, baja el daño</button>
    </div>
    <div class="ap-mandos">
      {m_g}
      {m_ct}
      {m_cf}
    </div>
    <div class="ap-graf" role="img" aria-label="Crecimiento del PIB contra crecimiento del PINE" id="apGraf">
      <div class="ap-graf-f"><span class="ap-graf-et">📣 PIB</span><span class="ap-graf-riel"><i class="ap-graf-cero"></i><span class="ap-graf-b ap-graf-pib" id="apBarPib"></span></span><b class="ap-graf-v" id="apBarPibV"></b></div>
      <div class="ap-graf-f"><span class="ap-graf-et">🌱 PINE</span><span class="ap-graf-riel"><i class="ap-graf-cero"></i><span class="ap-graf-b ap-graf-pine" id="apBarPine"></span></span><b class="ap-graf-v" id="apBarPineV"></b></div>
      <div class="ap-graf-esc" aria-hidden="true"><span>se encoge</span><span>0</span><span>crece</span></div>
    </div>
    <div class="ap-res" id="apRes" aria-live="polite"></div>
    <p class="ap-compartir"><button type="button" class="ap-btn" id="apCopiar"><span aria-hidden="true">🔗</span> Copiar el enlace de este escenario</button> <span id="apCopiado" aria-live="polite"></span></p>
    <p class="ap-honesto"><b>Qué hace y qué no hace este simulador.</b> No predice nada ni estima cifras: toma el año {ej} como base real y aplica la misma resta del INEGI a las proporciones que tú eliges. PIB del año siguiente = PIB {ej} × (1 + crecimiento); PINE del año siguiente = ese PIB × (1 − capital fijo − costo ambiental); su crecimiento se mide contra el PINE de {ej} ({pine_b}). Es aritmética de cuentas nacionales, no un modelo econométrico. Los valores de arranque ({ccf_pct}% y {ctada_pct}% del PIB) son los de {ej}; el del capital fijo es el punto medio de su rango (ver el paso 1).</p>
  </section>

  <section class="ap-sec" id="apDesglose" aria-labelledby="apDesTit">
    <h2 class="ap-tit" id="apDesTit"><span class="ap-n">3</span> Qué se acabó y qué se ensució</h2>
    <p class="ap-txt">Los {ctada_m} de costo ambiental de {ej} se parten en dos: lo que se agotó y ya no está, y lo que se degradó y empeoró. Cambia la forma de verlo:</p>
    <div class="ap-unidad" role="group" aria-label="Unidad del desglose">
      <button type="button" class="ap-chipbtn" data-u="pesos" aria-pressed="true">💵 En pesos</button>
      <button type="button" class="ap-chipbtn" data-u="pib" aria-pressed="false">📊 En % del PIB</button>
      <button type="button" class="ap-chipbtn" data-u="de100" aria-pressed="false">🪙 De cada $100 de daño</button>
    </div>
    <p class="ap-unidad-nota" id="apUnidadNota" aria-live="polite">Millones de pesos corrientes de {ej}.</p>
    <div class="ap-rubros">
      {r_agot}
      {r_deg}
    </div>
    <div class="ap-balanza" aria-labelledby="apBalTit">
      <h3 class="ap-rub-tit" id="apBalTit">⚖️ Se gastó en proteger frente a lo que se deterioró</h3>
      <div class="ap-bal-fila"><span class="ap-bal-k">🛡️ Protección ambiental del sector público</span><b class="ap-bal-v">{gpa_m}</b><span class="ap-bal-p">{gpa_pct}% del PIB {chip_gpa}</span>
        <span class="ap-bal-riel" aria-hidden="true"><span class="ap-bal-barra ap-bal-gasto" style="--w:{gpa_w:.2f}%"></span></span></div>
      <div class="ap-bal-fila"><span class="ap-bal-k">🌫️ Deterioro (agotamiento + degradación)</span><b class="ap-bal-v">{ctada_m}</b><span class="ap-bal-p">{ctada_pct}% del PIB {chip_ctada}</span>
        <span class="ap-bal-riel" aria-hidden="true"><span class="ap-bal-barra ap-bal-dano" style="--w:100%"></span></span></div>
      <div class="ap-monedas" role="img" aria-label="Por cada peso de protección, {ratio:.2f} pesos de deterioro">
        <span class="ap-mon-lado"><i class="ap-moneda ap-moneda-gasto"></i><small>$1 para proteger</small></span>
        <span class="ap-mon-vs" aria-hidden="true">→</span>
        <span class="ap-mon-lado ap-mon-dano">{coins}<small>${ratio:.2f} de deterioro</small></span>
      </div>
      <p class="ap-bal-lectura">{gpa_lectura} {chip_ratio}</p>
      {op_ratio}
      <p class="ap-bal-cob">Cobertura: {gpa_cob}. {f2}</p>
    </div>
  </section>

  <section class="ap-sec" id="apCiegos" aria-labelledby="apCieTit">
    <h2 class="ap-tit" id="apCieTit"><span class="ap-n">4</span> Cuatro puntos ciegos del indicador que se anuncia</h2>
    <div class="ap-cies">{ciegos}</div>
    <h2 class="ap-tit ap-tit-2" id="apJurTit"><span aria-hidden="true">⚖️</span> Por qué esto no es sólo estadística</h2>
    <p class="ap-txt">Una cifra que mide el daño convierte un principio en una obligación exigible. Toca cada una para leer las cuatro consecuencias jurídicas de que el deterioro tenga precio oficial.</p>
    <div class="ap-jurs">{jur}</div>
  </section>

  <aside class="ap-aviso" aria-labelledby="apProcTit">
    <h2 class="ap-tit ap-tit-3" id="apProcTit"><span aria-hidden="true">📚</span> Procedencia de cada cifra</h2>
    <p>{nota_met}</p>
    <ul class="ap-proc">
      <li>Cuentas Económicas y Ecológicas de México {ej}, publicadas el {publicacion}. {r_ceem} {f_doc}</li>
      <li>Programa estadístico de las cuentas verdes del INEGI. {r_prog}</li>
      <li>Producto Interno Bruto nacional a precios de mercado de {ej}. {r_pib}</li>
    </ul>
    <p>Cotejamos esta página con el comunicado del INEGI: los montos del agotamiento por componente son los de su Tabla 1, y el consumo de capital fijo y el Producto Interno Neto se dan como rango porque se derivan de un PINE que el INEGI publica redondeado. Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>. Lo que todavía nos deben las dependencias está en el <a href="pendientes.html">Registro de pendientes</a>.</p>
    <p class="ap-hermanas">Sigue en Costo ambiental: <a href="herramienta-ambiente-reloj.html">⏱️ El reloj y el año</a> · <a href="herramienta-ambiente-ticket.html">🧾 Tu ticket en negativo</a> · <a href="herramienta-ambiente-basura.html">🗑️ Basura y protección</a> · <a href="herramienta-ambiente-crisis.html">🔥 Crisis ambientales</a></p>
  </aside>
  <script type="application/json" id="apDatos">{datos}</script>
</div>'''.format(
        ej=ej, pib_b=billones(pib), pine_b=billones(pine), pib_b2=billones(pib), pine_b2=billones(pine),
        entrada=esc(c['entrada']), pib_m=m0(pib), ctada_m=m0(ctada), pine_pct='%.1f' % casc['pine']['pct_pib'],
        ctada_pct='%.1f' % c['ctada']['pct_pib'],
        chip_pib=chip(c.get('pib_estado', 'oficial')), chip_ctada=chip(c['ctada']['estado']), chip_pine=chip(casc['pine']['estado']),
        filas='\n'.join(filas), f1=_fuente('CEEM 2024', 1),
        m_g=_mando('apG', 'Crecimiento nominal del PIB', -6, 14, 5.0, '%', '📣'),
        m_ct=_mando('apCt', 'Costo ambiental del año siguiente', 0, 10, round(ctada_pct, 1), '% del PIB', '🌫️'),
        m_cf=_mando('apCf', 'Consumo de capital fijo', 10, 28, round(ccf_pct, 1), '% del PIB', '🏭'),
        ccf_pct='%.1f' % ccf_pct,
        r_agot=rubro(agot, comps_agot, 'Agotamiento: lo que ya no está', '📉', 'agot', nota_agot),
        r_deg=rubro(deg, deg['componentes'], 'Degradación: lo que empeoró', '🌫️', 'deg', nota_deg),
        gpa_m=m0(gpa['monto_mdp']), gpa_pct='%.1f' % gpa['pct_pib'], chip_gpa=chip(gpa['estado']),
        gpa_w=gpa['monto_mdp'] / ctada * 100, ratio=ratio, coins=coins_dano,
        gpa_lectura=esc(gpa['lectura']), chip_ratio=chip(gpa['ratio_estado']),
        op_ratio='<p class="ap-bal-op">' + _op('%s ÷ %s = %.2f pesos de deterioro por cada peso de protección.' % (m0(ctada), m0(gpa['monto_mdp']), ratio)) + '</p>',
        gpa_cob=esc(gpa['cobertura']), f2=_fuente('CEEM 2024', 2),
        ciegos=ciegos, jur=jur, nota_met=esc(c['nota_metodologica']), publicacion=esc(c['publicacion']),
        r_ceem=ref(c['ref_fuente']), r_prog=ref(c['ref_programa']), r_pib=ref(c['ref_pib']), f_doc=_fuente(DOC_CEEM),
        datos=_json(datos))


def _mando(id_, etiqueta, mn, mx, valor, unidad, ico):
    return ('<div class="ap-mando"><label class="ap-mando-et" for="%s"><span aria-hidden="true">%s</span> %s</label>'
            '<div class="ap-mando-fila"><button type="button" class="ap-paso" data-para="%s" data-d="-0.5" aria-label="Bajar medio punto">−</button>'
            '<input type="range" class="ap-rango" id="%s" min="%s" max="%s" step="0.1" value="%.1f" data-u="%s">'
            '<button type="button" class="ap-paso" data-para="%s" data-d="0.5" aria-label="Subir medio punto">+</button></div>'
            '<output class="ap-mando-val" id="%sVal" for="%s">%.1f %s</output></div>'
            % (id_, ico, etiqueta, id_, id_, mn, mx, valor, esc(unidad), id_, id_, id_, valor, esc(unidad)))
