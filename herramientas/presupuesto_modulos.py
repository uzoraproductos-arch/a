# -*- coding: utf-8 -*-
"""Los cuatro modulos de «Presupuesto», cada uno en su pagina propia
(pedido del autor, 11-10-2026).

Antes, cada pagina cargaba el auditor completo en un marco y el modulo se
abria y se contaba alli dentro: tardaba. Ahora la pagina se escribe aqui,
con sus cifras ya puestas, desde window.AUDIT_DB (panoramaErario,
calculadora_civica, cuenta_publica_asf, constitucion_economica y
paquete_2027). Solo el simulador del Paquete 2027 necesita JavaScript
(presupuesto.js).

Lo usa apartados.numeros_preparar(); recibe `ref(id)`, que pinta la
llamada [nn] a fuentes-oficiales.html.
"""
import json


def chip(e, pend=None):
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, (' data-pend="%s"' % pend) if pend else '', e)


def mdp(v, d=1):
    return ('-' if v < 0 else '') + '$' + format(abs(v), ',.%df' % d) + ' mdp'


def mmp(v):
    """Miles de millones, como los publica el documento."""
    return '$' + format(v, ',.1f') + ' mmp'


def bill(v):
    return '$%.2f billones' % (v / 1e6)


def pct(v, d=1):
    return format(v, '.%df' % d) + '%'


# Colores de los renglones (los mismos de «Gasto publico»).
COLOR_EGR = {'egr-social': '#1b7f4c', 'egr-economico': '#0f6f8f', 'egr-gobierno': '#6b3fa0', 'egr-poderes': '#9468c9',
             'egr-fondos': '#8a94a8', 'egr-costofin': '#b3261e', 'egr-participaciones': '#d0632a', 'egr-adefas': '#7a2a24'}
COLOR_ING = {'Impuestos': '#0b2a63', 'Otras contribuciones': '#2f5fa8', 'No tributarios': '#6f8fc4', 'Financiamiento': '#b3261e'}
COLOR_FED = {'fed-r28': '#d0632a', 'fed-r33': '#c9a84c', 'fed-r25': '#8a6d1f', 'fed-conv': '#a8b3c7'}


def _seg(w, color, titulo, cuerpo, href=None, extra=''):
    """Un tramo de una barra proporcional: ancho en %, color y rotulo. Los
    tramos de menos de 4% no caben rotulados: su nombre queda en el titulo
    y en la leyenda."""
    tag = 'a' if href else 'span'
    if w < 4:
        cuerpo = ''
    return ('<%s class="pm-seg"%s style="--w:%.3f%%;--c:%s" title="%s"%s><span class="pm-seg-tx">%s</span></%s>'
            % (tag, (' href="%s"' % href) if href else '', w, color, titulo, extra, cuerpo, tag))


# ---------------------------------------------------------------------------
# 1 · Cuanto dinero es
# ---------------------------------------------------------------------------
def cuanto(base, ref, peso):
    """La cifra de 2026, las dos barras de «El peso de 2026» (`peso`, que
    arma apartados.numeros_peso y vuelve interactivo numeros.js) y lo que
    baja al territorio. Desde el 11-10-2026 aqui vive «El peso de 2026»:
    las dos paginas repetian el total y el reparto (pedido del autor)."""
    P = base['panoramaErario']
    tlif, tpef = P['totalLIF'], P['totalPEF']
    ing, eg = P['ingresos'], P['egresos']
    deuda = next(x for x in ing if x['id'] == 'ing-deuda')
    prog = [x for x in eg if x['grupo'] == 'Programable']
    nopr = [x for x in eg if x['grupo'] == 'No programable']
    sp, sn = round(sum(x['montoMdp'] for x in prog), 1), round(sum(x['montoMdp'] for x in nopr), 1)
    redondeo = round(tpef - sp - sn, 1)
    pdeuda = deuda['montoMdp'] / tlif * 100
    kpis = [
        ('Ingreso autorizado', bill(tlif), 'gold', 'Ley de Ingresos %d %s' % (P['ejercicio'], ref('ref-lif2026')), 'oficial'),
        ('Gasto aprobado', bill(tpef), 'gold', 'Presupuesto de Egresos %d %s' % (P['ejercicio'], ref('ref-pef2026')), 'oficial'),
        ('De eso, prestado', bill(deuda['montoMdp']), 'red',
         '%s del ingreso: %s ÷ %s' % (pct(pdeuda), mdp(deuda['montoMdp']), mdp(tlif)), 'derivado'),
        ('Se decide cada año', bill(sp), 'green', 'Gasto programable: suma de sus %d finalidades %s' % (len(prog), ref('ref-cgpe2027')), 'derivado'),
        ('Ya está comprometido', bill(sn), 'red', 'Gasto no programable: suma de sus %d renglones %s' % (len(nopr), ref('ref-pef2026')), 'derivado'),
    ]
    tarjetas = ''.join(
        '<div class="pm-kpi pm-%s"><span class="pm-kpi-k">%s %s</span><b class="pm-kpi-v num-tabular">%s</b><small>%s</small></div>'
        % (c, k, chip(e), v, s) for k, v, c, s, e in kpis)
    # Las barras ya no repiten el porque del cuadre: lo dice la cifra de arriba.
    peso = peso.replace('La Ley de Ingresos y el Presupuesto de Egresos suman lo mismo por construcción: la deuda se cuenta como ingreso. ', '')
    peso = peso.replace('El peso de 2026: de dónde viene y a dónde va', 'De dónde viene y a dónde va')
    peso = peso.replace('Todo el dinero federal del año, <b>', 'Los mismos <b>')

    # Lo que baja al territorio, sobre el total del gasto.
    F = P['federalizado']
    comp = F['componentes']
    pfed = F['totalMdp'] / tpef * 100
    barra_fed = ''.join(_seg(c['montoMdp'] / tpef * 100, COLOR_FED[c['id']], '%s: %s' % (c['nombre'], mdp(c['montoMdp'])), '')
                        for c in comp)
    barra_fed += _seg(100 - pfed, '#e6ebf3', 'Se queda en la Federación', 'Se queda en la Federación<small>%s</small>' % pct(100 - pfed), extra=' data-claro="1"')
    ley_fed = ''.join(
        '<li><span class="pm-punto" style="--c:%s"></span><b>%s</b> <span class="num-tabular">%s</span> %s</li>'
        % (COLOR_FED[c['id']], c['nombre'], mdp(c['montoMdp']), chip(c['estado'])) for c in comp)

    return '''<section class="pm" aria-labelledby="pmCifraTit">
          <h2 class="pm-tit" id="pmCifraTit">La cifra de 2026, de un vistazo</h2>
          <p class="pm-txt"><b>%s de pesos</b>: ese es el total de 2026, antes de partirlo. %s</p>
          <div class="pm-kpis">%s</div>
          <p class="pm-pie">Los cinco renglones programables son la clasificación funcional que Hacienda publica en miles de millones %s; por eso suman %s y no los $7,094,708.8 mdp del cuadro de finanzas públicas: la diferencia de %s millones es redondeo de la fuente, no un faltante.</p>
        </section>
        %s
        <section class="pm" aria-labelledby="pmBajaTit">
          <h2 class="pm-tit" id="pmBajaTit">Y de ese gasto, lo que baja al territorio</h2>
          <p class="pm-txt"><b>%s</b> no se quedan en la Federación: viajan a los 32 estados y a sus municipios. Son el <b>%s</b> del gasto aprobado %s (%s ÷ %s).</p>
          <div class="pm-barra" role="img" aria-label="Gasto federalizado: %s del gasto aprobado">%s</div>
          <ul class="pm-ley pm-ley-fila">%s</ul>
          <p class="pm-pie">%s %s <a href="numeros-baja-al-territorio.html">Míralo sobre el mapa, estado por estado ➔</a></p>
        </section>
        <p class="pm-sigue">Renglón por renglón: <a href="numeros-los-16-origenes.html">🧾 los 16 orígenes del ingreso ➔</a> · <a href="numeros-gasto-publico.html#gpReparte">🏛️ los ocho renglones del gasto ➔</a></p>''' % (
        bill(tpef), P['notaCuadre'], tarjetas, ref('ref-cgpe2027'), mdp(sp), format(redondeo, '.1f'), peso,
        bill(F['totalMdp']), pct(pfed), chip('derivado'), mdp(F['totalMdp']), mdp(tpef), pct(pfed), barra_fed, ley_fed,
        F['nota'], ref('ref-pef2026'))


# ---------------------------------------------------------------------------
# 2 · ¿A que equivale?
# ---------------------------------------------------------------------------
def equivale(base, ref):
    P = base['panoramaErario']
    eg = {x['id']: x for x in P['egresos']}
    cf, pod = eg['egr-costofin']['montoMdp'], eg['egr-poderes']['montoMdp']
    veces = cf / pod
    pob = base['calculadora_civica']['parametros']['poblacion']
    fed = P['federalizado']['totalMdp']
    por_hab = fed * 1e6 / pob['personas']
    bloques = ''.join('<span class="pm-bloque" style="--w:%.3f%%" title="Poderes y órganos autónomos: %s"></span>'
                      % (pod / cf * 100, mdp(pod)) for _ in range(int(veces)))
    tm = '$785.3 mdp'
    return '''<section class="pm" aria-labelledby="pmEq1">
          <p class="pm-eq-n">1 de 3</p>
          <h2 class="pm-tit" id="pmEq1">📉 La deuda cuesta %s veces lo que cuestan los Poderes %s</h2>
          <p class="pm-txt">El <a class="glos-pagina" href="glosario.html#Costo-Financiero-de-la-Deuda">costo financiero de la deuda</a> previsto para 2026 %s equivale a %s veces lo que el mismo presupuesto asigna al Congreso, al Poder Judicial, a los órganos autónomos, al INEGI y al Tribunal Federal de Justicia Administrativa juntos %s.</p>
          <figure class="pm-fig">
            <div class="pm-barra pm-barra-alta" role="img" aria-label="Costo financiero de la deuda: %s"><span class="pm-seg" style="--w:100%%;--c:#b3261e"><span class="pm-seg-tx">Costo financiero de la deuda<small>%s</small></span></span></div>
            <div class="pm-bloques" role="img" aria-label="%d veces el presupuesto de los Poderes y órganos autónomos">%s</div>
            <figcaption>Cada cuadro morado es todo lo que reciben los Poderes y órganos autónomos en el año: <b>%s</b>. Caben %d completos dentro de lo que se paga de intereses.</figcaption>
          </figure>
          <p class="pm-op"><b>La operación:</b> %s ÷ %s = %s.</p>
          <p class="pm-mas"><a href="numeros-egreso-costo-financiero.html">El costo financiero, en su página ➔</a> <a href="numeros-lo-que-cuestan-los-poderes.html">Lo que cuestan el Congreso y la Judicatura ➔</a></p>
        </section>
        <section class="pm" aria-labelledby="pmEq2">
          <p class="pm-eq-n">2 de 3</p>
          <h2 class="pm-tit" id="pmEq2">🗺️ $%s por habitante %s</h2>
          <p class="pm-txt">Es lo que el <a class="glos-pagina" href="glosario.html#Gasto-Federalizado">gasto federalizado</a> de 2026 %s reparte, en promedio, por cada persona que vive en México. El promedio esconde diferencias grandes entre estados; el mapa las muestra una por una.</p>
          <figure class="pm-fig pm-hab">
            <div class="pm-hab-op"><span><b class="num-tabular">%s</b><small>gasto federalizado %s</small></span><span class="pm-hab-signo" aria-hidden="true">÷</span>
              <span><b class="num-tabular">%s</b><small>personas a mitad de 2026 %s</small></span><span class="pm-hab-signo" aria-hidden="true">=</span>
              <span class="pm-hab-res"><b class="num-tabular">$%s</b><small>por persona</small></span></div>
          </figure>
          <p class="pm-op"><b>De dónde sale la población:</b> %s. %s <a href="%s" rel="noopener" target="_blank">Archivo oficial ↗</a></p>
          <p class="pm-mas"><a href="numeros-baja-al-territorio.html">El reparto, estado por estado ➔</a></p>
        </section>
        <section class="pm" aria-labelledby="pmEq3">
          <p class="pm-eq-n">3 de 3</p>
          <h2 class="pm-tit" id="pmEq3">🚆 %s por aclarar en el Tren Maya %s</h2>
          <p class="pm-txt">Es lo que la <a class="glos-pagina" href="glosario.html#Auditoria-Superior-de-la-Federacion">Auditoría Superior de la Federación</a> dejó sin aclarar en la construcción y el financiamiento del Tren Maya en la Cuenta Pública 2022, con 14 pliegos de observaciones. El tramo 4, Izamal-Cancún, concentra el 45 %%. La cifra suma los informes individuales de ese año.</p>
          <p class="pm-mas"><a href="expedientes.html#exp-tren-maya">Ver el expediente y sus informes ➔</a> <a href="auditoria-tren-maya.html">El Tren Maya en imágenes ➔</a></p>
        </section>
        <aside class="pm pm-aviso" aria-labelledby="pmHuach">
          <h2 class="pm-sub" id="pmHuach">⛽ Y lo que no entra %s</h2>
          <p class="pm-txt">La deuda crece también por lo que el erario deja de cobrar. El Gobierno reconoce que el robo y la venta ilegal de combustibles son «una de las principales fuentes de evasión» del IEPS, el impuesto que va en cada litro. Ni el SAT ni Hacienda han publicado cuánto se pierde: falta de transparencia de esas dependencias.</p>
          <p class="pm-mas"><a href="auditoria-huachicol-fiscal.html">Huachicol fiscal: lo que se sabe y lo que falta ➔</a> <a href="pendientes.html#huachicol-evasion">En el Registro de pendientes ➔</a></p>
        </aside>
        <section class="pm pm-nota" aria-labelledby="pmNota">
          <h2 class="pm-sub" id="pmNota">📌 Cómo se hicieron estas comparaciones</h2>
          <p class="pm-txt">Las tres usan solo cifras que esta plataforma ya cita de su documento oficial, y por eso llevan el chip %s: el resultado es una operación, y la operación está a la vista. La primera divide dos renglones del mismo Presupuesto 2026. La segunda reparte una cifra nacional entre la población proyectada por el Consejo Nacional de Población. La tercera suma los informes de la ASF que se enlistan, uno por uno, en el expediente del caso.</p>
          <p class="pm-txt">No comparamos contra el costo de un hospital, de una beca o de una obra «tipo» mientras ese costo no tenga su propio documento oficial: un costo supuesto convierte la comparación en opinión.</p>
        </section>''' % (
        format(veces, '.0f'), chip('derivado'), ref('ref-pef2026'), format(veces, '.0f'), ref('ref-cgpe2027'),
        mdp(cf), mdp(cf), int(veces), bloques, mdp(pod), int(veces),
        mdp(cf), mdp(pod), format(veces, '.2f'),
        format(round(por_hab), ','), chip('derivado'), ref('ref-pef2026'),
        mdp(fed, 0), ref('ref-pef2026'), format(pob['personas'], ','), chip(pob['estado']), format(round(por_hab), ','),
        pob['fuente'], pob['como'], pob['url'],
        tm, chip('derivado'),
        chip('pendiente', 'huachicol-evasion'), chip('derivado'))


# ---------------------------------------------------------------------------
# 3 · El camino del dinero, en cuatro etapas
# ---------------------------------------------------------------------------
def camino(base, ref):
    P = base['panoramaErario']
    tlif, tpef = P['totalLIF'], P['totalPEF']
    F = P['federalizado']
    asf = base['cuenta_publica_asf']['cp2024']['total']['porAclarar'] / 1e6
    etapas = {
        'cir-1': (bill(tlif), 'oficial', ref('ref-lif2026'),
                  'Impuestos, cuotas, lo que venden las empresas del Estado y <b>lo que se pide prestado</b>. '
                  'Cada renglón, con su cifra, está en <a href="numeros-los-16-origenes.html">los 16 orígenes</a>.', tlif),
        'cir-2': (bill(tpef), 'oficial', ref('ref-pef2026'),
                  'La misma cifra que se recauda, porque el presupuesto se construye para cuadrar. Se parte en lo que se decide cada año '
                  '(salud, educación, pensiones, inversión) y lo que ya está comprometido (intereses, participaciones y adeudos): '
                  'sus montos están en <a href="numeros-cuanto-dinero-es.html">Cuánto dinero es</a>.', tpef),
        'cir-3': (bill(F['totalMdp']), 'oficial', ref('ref-pef2026'),
                  'Es lo que viaja a los 32 estados y sus municipios, sobre todo como participaciones (Ramo 28) y aportaciones (Ramo 33), '
                  'con las reglas de la Ley de Coordinación Fiscal %s.' % ref('ref-lcf'), F['totalMdp']),
        'cir-4': (mdp(asf), 'oficial', ref('ref-asf-mdb2024'),
                  'Quedó <b>por aclarar</b> al revisar la Cuenta Pública 2024, la más reciente ya fiscalizada: dinero observado que las instituciones auditadas aún deben justificar o reintegrar. Esta etapa ocurre al año siguiente; por eso su cifra es de 2024 y no de 2026.',
                  None),
    }
    sigue = {'cir-1': ('numeros-los-16-origenes.html', 'Los 16 orígenes del ingreso'),
             'cir-2': ('numeros-gasto-publico.html', 'Gasto público: quién lo aprueba'),
             'cir-3': ('numeros-baja-al-territorio.html', 'Baja al territorio'),
             'cir-4': ('numeros-cuentas-claras.html', 'Cuentas claras')}
    pasos = []
    for e in P['circuito']:
        v, est, r, desc, _ = etapas[e['id']]
        pasos.append('''<li class="pm-etapa">
            <span class="pm-etapa-n">Etapa %d</span>
            <h3 class="pm-etapa-verbo"><span aria-hidden="true">%s</span> %s</h3>
            <p class="pm-etapa-inst">%s %s</p>
            <p class="pm-etapa-v num-tabular">%s %s</p>
            <p class="pm-etapa-d">%s</p>
            <dl class="pm-etapa-ley">
              <div><dt>Quién responde</dt><dd>%s</dd></div>
              <div><dt>Plazo legal</dt><dd>%s</dd></div>
              <div><dt>Fundamento</dt><dd>%s</dd></div>
            </dl>
            <p class="pm-etapa-que">%s</p>
            <a class="pm-etapa-sigue" href="%s">%s ➔</a>
          </li>''' % (e['orden'], e['icono'], e['titulo'], e['instrumento'], r, v, chip(est), desc, e['quien'], e['cuando'],
                     ' '.join('<span class="pm-ley-chip">%s</span>' % l for l in e['leyes']), e['que'], sigue[e['id']][0], sigue[e['id']][1]))
    return '''<section class="pm" aria-labelledby="pmCamTit">
          <h2 class="pm-tit" id="pmCamTit">Las cuatro etapas, con su ley</h2>
          <p class="pm-txt">Cada peso público pasa por cuatro manos: se recauda, se aprueba, se ejerce y se revisa. Cada etapa tiene quién responde, un plazo que fija la ley y su fundamento. Las cifras son las de 2026, salvo la revisión, que llega un año después.</p>
          <ol class="pm-etapas">%s</ol>
        </section>''' % '\n          '.join(pasos)


# ---------------------------------------------------------------------------
# 4 · Paquete Economico 2027
# ---------------------------------------------------------------------------
PE_FUENTE = {
    'cgpe': 'los Criterios Generales de Política Económica 2027',
    'ppef': 'el decreto del proyecto de Presupuesto de Egresos 2027',
    'ilif': 'la iniciativa de Ley de Ingresos 2027',
    'com': 'el comunicado 71 de la Secretaría de Hacienda',
    'lisr': 'la iniciativa de reforma a la Ley del Impuesto sobre la Renta',
    'lfd': 'la iniciativa de reforma a la Ley Federal de Derechos',
    'gaceta': 'la Gaceta Parlamentaria 7121, que publicó el paquete completo',
    'lfprh': 'la Ley Federal de Presupuesto y Responsabilidad Hacendaria',
}

PE_ESCENARIOS = [
    {'id': 'pe-base', 'n': 'Como lo proyecta Hacienda', 'icono': '📋', 'v': {},
     'd': 'Las seis variables en el valor que los Criterios suponen para 2027.'},
    {'id': 'pe-tasas', 'n': 'Choque de tasas', 'icono': '📈', 'v': {'s-tasa': 8.6},
     'd': 'La tasa de referencia sube 250 puntos base y no baja en todo el año.'},
    {'id': 'pe-crudo', 'n': 'Petróleo a 45 dólares', 'icono': '🛢️', 'v': {'s-precio': 45, 's-plataforma': 1700},
     'd': 'La mezcla cae a 45 dólares y la plataforma se queda cien mil barriles por debajo de la meta.'},
    {'id': 'pe-frenon', 'n': 'Frenón económico', 'icono': '🔻', 'v': {'s-crec': 0.5, 's-tasa': 7.1, 's-tipocambio': 19.5},
     'd': 'El PIB crece medio punto, el peso se deprecia a 19.50 y la tasa sube cien puntos base.'},
    {'id': 'pe-cola', 'n': 'Viento de cola', 'icono': '🌞', 'v': {'s-crec': 3.0, 's-precio': 78, 's-tasa': 5.1},
     'd': 'Crecimiento de 3%, petróleo en 78 dólares y cien puntos base menos de tasa.'},
]

PE_INDICE = [('peFacultad', '🏛️', 'Con qué facultad'), ('peItin', '🗓️', 'El itinerario'), ('peCifras', '📊', 'Cómo se ve 2027'),
             ('peGasto', '🧭', 'En qué se irá'), ('peSim', '🎛️', 'Simulador'), ('peFiscal', '🧾', 'Impuestos'),
             ('peColchon', '🛟', 'Colchón y pasivos'), ('peSenda', '🛣️', 'Ruta a 2032'), ('peCiegos', '🔦', 'Puntos ciegos'),
             ('peFuentes', '📚', 'Fuentes')]


def paquete(base, ref):
    P = base['paquete_2027']
    CE = base['constitucion_economica']
    def pr(k):
        return ref(P['refs'][k]) if k in P['refs'] else ''
    def fuente(k):
        k = k if k in PE_FUENTE else 'cgpe'
        return PE_FUENTE[k] + pr(k)
    oficial = chip('oficial')
    indice = ''.join('<a class="pm-ind" href="#%s"><span aria-hidden="true">%s</span> %s</a>' % x for x in PE_INDICE)

    pilares = ''.join('''<article class="pm-pilar" style="--c:%s">
            <p class="pm-pilar-art"><span aria-hidden="true">%s</span> %s constitucional</p>
            <h3>%s</h3>
            <p class="pm-pilar-preg"><b>%s</b> %s</p>
            <dl class="pm-ficha"><div><dt>Facultad</dt><dd>%s</dd></div><div><dt>Quién la ejerce</dt><dd>%s</dd></div><div><dt>Ley que la desarrolla</dt><dd>%s</dd></div></dl>
            <ul class="pm-claves">%s</ul>
            <p class="pm-ciego"><span class="pm-et">Punto ciego</span>%s</p>
            <a class="pm-mas-a" href="marco-legal.html#precepto-%s">📜 Leer el texto del %s</a>
          </article>''' % (p['color'], p['icono'], p['articulo'], p['titulo'], p['pregunta'], p['respuesta'], p['facultad'], p['organo'],
                          p['ley_secundaria'], ''.join('<li><b>%s.</b> %s</li>' % (c['k'], c['v']) for c in p['claves']),
                          p['punto_ciego'], p['precepto_id'], p['articulo'].lower()) for p in CE['pilares'])
    cadena = ''.join('<li><span class="pm-cad-n">%d</span><span class="pm-cad-et">%s</span><b>%s</b><small>%s</small></li>' % (i + 1, n, t, d) for i, (n, t, d) in enumerate([
        ('Art. 25', 'Rectoría', 'El Estado asume la conducción del desarrollo.'),
        ('Art. 26', 'Plan Nacional de Desarrollo', 'El rumbo se escribe y obliga a la Administración.'),
        ('Programa', 'Programa presupuestario', 'El objetivo se convierte en una unidad de gasto con clave.'),
        ('PEF', 'Partida del Presupuesto de Egresos', 'La unidad de gasto recibe pesos y un responsable.'),
        ('ASF', 'Fiscalización', 'Alguien revisa si el peso hizo lo que el Plan prometió.')]))

    itin = ''.join('''<li class="pm-itin-paso"><span class="pm-itin-n">%d</span>
            <div><p class="pm-itin-fecha">%s · <b>%s</b> <small>%s</small></p>
            <p class="pm-itin-ley">%s</p><p>%s</p>
            <p class="pm-ciego"><span class="pm-et">Lo que no se suele decir</span>%s</p></div></li>'''
                   % (i + 1, h['fecha'], h['hito'], h['quien'], h['ley'], h['texto'], h['ciego']) for i, h in enumerate(P['itinerario']))

    marco = ''.join('<tr><th scope="row">%s<small>%s</small><small class="pm-nota-var">%s</small></th><td>%s</td><td>%s</td><td class="pm-destaca">%s</td></tr>'
                    % (m['v'], m['u'], m['n'], m['a26'], m['e26'], m['p27']) for m in P['marco'])
    grupos = []
    for f in P['finanzas']:
        if not grupos or grupos[-1][0] != f['g']:
            grupos.append((f['g'], []))
        grupos[-1][1].append(f)
    finanzas = ''.join('<h3 class="pm-sub">%s</h3><div class="pm-fin">%s</div>' % (g, ''.join(
        '<article class="pm-fin-t%s"><h4>%s</h4><p class="pm-fin-v num-tabular">%s</p><p class="pm-fin-pib">%s del PIB <small>2026 aprobado: %s</small></p><p class="pm-fin-d">%s</p></article>'
        % (' neg' if f['m'] < 0 else '', f['n'], mdp(f['m'], 1), pct(f['pib']), pct(f['pib26']), f['d']) for f in fs)) for g, fs in grupos)

    Fn = P['funcional']
    maxf = max(f['ppef27'] for f in Fn['filas'])
    funcional = ''.join(
        '<div class="pm-hbar"><span class="pm-hbar-n">%s<small>%s</small></span><span class="pm-hbar-b"><span class="pm-seg" style="--w:%.2f%%;--c:%s"></span></span>'
        '<b class="num-tabular">%s</b><span class="pm-var %s">%s%s real</span></div>'
        % (f['n'], f['d'] + ' 2026 aprobado: ' + mmp(f['pef26']) + '.', f['ppef27'] / maxf * 100, '#b3261e' if f['var'] < 0 else '#0b2a63',
           mmp(f['ppef27']), 'baja' if f['var'] < 0 else 'sube', '+' if f['var'] > 0 else '', pct(f['var'])) for f in Fn['filas'])
    S, I = P['sociales'], P['inversion']
    def lista(filas, color):
        mx = max(f['m'] for f in filas)
        return ''.join('<div class="pm-hbar pm-hbar-s"><span class="pm-hbar-n"><span class="pm-tag">%s</span>%s%s</span><span class="pm-hbar-b"><span class="pm-seg" style="--w:%.2f%%;--c:%s"></span></span><b class="num-tabular">%s</b></div>'
                       % (f['g'], f['n'], ('<small>%s</small>' % f['d']) if f.get('d') else '', f['m'] / mx * 100, color, mdp(f['m'])) for f in filas)

    sens = P['sensibilidades']
    palancas = ''.join('''<div class="pm-pal" id="pepal-%s">
            <div class="pm-pal-cab"><span aria-hidden="true">%s</span><label for="perng-%s">%s</label><output id="peval-%s">%s</output></div>
            <input type="range" id="perng-%s" data-id="%s" min="%s" max="%s" step="%s" value="%s" aria-describedby="pedesc-%s">
            <div class="pm-pal-esc"><span>%s</span><span class="pm-pal-base">Criterios: %s</span><span>%s</span></div>
            <p class="pm-pal-u" id="pedesc-%s">%s</p>
            <p class="pm-pal-cita"><span class="pm-et">Coeficiente oficial</span>%s</p>
            <p class="pm-pal-porque">%s</p>
          </div>''' % (s['id'], s['icono'], s['id'], s['n'], s['id'], format(s['base'], '.%df' % s['dec']), s['id'], s['id'],
                       s['min'], s['max'], s['paso'], s['base'], s['id'], format(s['min'], '.%df' % s['dec']),
                       format(s['base'], '.%df' % s['dec']), format(s['max'], '.%df' % s['dec']), s['id'], s['unidad'], s['cita'], s['porque'])
                       for s in sens)
    escenarios = ''.join('<button type="button" class="pm-esc%s" data-esc="%s" title="%s"><span aria-hidden="true">%s</span> %s</button>'
                         % (' activo' if e['id'] == 'pe-base' else '', e['id'], e['d'], e['icono'], e['n']) for e in PE_ESCENARIOS)
    datos = json.dumps({'s': sens, 'b': P['simBase'], 'e': PE_ESCENARIOS}, ensure_ascii=False).replace('</', '<\\/')

    fiscal = ''
    for t, cls in (('Recauda más', 'mas'), ('Recauda menos', 'menos'), ('Estructural', 'estr')):
        fs = [f for f in P['fiscal'] if f['tipo'] == t]
        if fs:
            fiscal += '<h3 class="pm-sub pm-fis-%s">%s</h3><div class="pm-rej">%s</div>' % (cls, t, ''.join(
                '<article class="pm-t"><span class="pm-t-ico" aria-hidden="true">%s</span><h4>%s</h4><p>%s</p><p class="pm-t-ley">%s</p></article>'
                % (f['icono'], f['n'], f['d'], f['ley']) for f in fs))

    amort = ''.join('<article class="pm-t"><span class="pm-t-ico" aria-hidden="true">%s</span><h4>%s</h4><p class="pm-t-v num-tabular">%s</p><p>%s</p>%s</article>'
                    % (a['icono'], a['n'], ('$' + format(a['m'], ',.1f') + ' mdd') if a['u'] == 'mdd' else mdp(a['m']), a['d'],
                       ('<p class="pm-meta"><span class="pm-et">Lo que la ley llama reserva adecuada</span><b>%s</b> · tiene el %s'
                        '<span class="pm-meta-b"><span style="--w:%.1f%%"></span></span><small>%s</small></p>'
                        % (mdp(a['meta']), pct(a['metaPct']), min(a['metaPct'], 100), a['metaTexto'])) if a.get('meta') else '')
                    for a in P['amortiguadores'])
    conting = ''.join('<article class="pm-t"><span class="pm-t-ico" aria-hidden="true">%s</span><h4>%s</h4><p class="pm-t-v num-tabular">%s%s</p><p>%s</p><p class="pm-ciego"><span class="pm-et">Punto ciego</span>%s</p></article>'
                      % (c['icono'], c['n'], mdp(c['m']), (' <small>%s del PIB</small>' % pct(c['pib'])) if c['pib'] is not None else '', c['d'], c['ciego'])
                      for c in P['contingentes'])

    Sd = P['senda']
    senda = ('<thead><tr><th scope="col">Indicador</th>%s</tr></thead><tbody>%s</tbody>' % (
        ''.join('<th scope="col"%s>%s</th>' % (' class="pm-destaca"' if i == 1 else '', a) for i, a in enumerate(Sd['anios'])),
        ''.join('<tr class="pm-senda-%s"><th scope="row">%s<small>%s</small></th>%s</tr>' % (
            s['sentido'], s['n'], s['u'], ''.join('<td%s>%s</td>' % (' class="pm-destaca"' if i == 1 else '', format(v, '.1f')) for i, v in enumerate(s['v'])))
            for s in Sd['series'])))

    ciegos = ''.join('''<details class="pm-ciego-d" id="pe-ciego-%s"><summary><span class="pm-ciego-n">%d</span><span>%s</span></summary>
            <div class="pm-ciego-c"><div class="pm-cb dice"><span class="pm-et">Lo que se dijo</span><p>%s</p></div>
            <div class="pm-cb doc"><span class="pm-et">Lo que dice el documento</span><p>%s</p></div>
            <div class="pm-cb porque"><span class="pm-et">Por qué importa</span><p>%s</p></div>
            <p class="pm-pie">Verificado contra %s%s.</p></div></details>'''
                     % (c['id'], i + 1, c['titulo'], c['dice'], c['documento'], c['porque'], fuente(c['ref']),
                        (' y ' + fuente(c['ref2'])) if c.get('ref2') else '') for i, c in enumerate(P['ciegos']))

    return '''<nav class="pm-indice" aria-label="Secciones del Paquete Económico 2027">%s</nav>
        <section class="pm" id="peFacultad" aria-labelledby="peFacultadTit">
          <p class="pm-eq-n">Constitución económica · artículos 25, 26, 27 y 28</p>
          <h2 class="pm-tit" id="peFacultadTit">Con qué facultad interviene el Estado en la economía</h2>
          <p class="pm-txt">%s %s</p>
          <div class="pm-pilares">%s</div>
          <h3 class="pm-sub">Del artículo al peso ejercido</h3>
          <p class="pm-txt">La rectoría y la planeación no son declaraciones: son el primer eslabón de una cadena que termina en una partida con nombre. Donde la cadena se rompe, una meta desaparece sin dejar rastro contable.</p>
          <ol class="pm-cadena">%s</ol>
          <p class="pm-pie">Procedencia: Constitución Política de los Estados Unidos Mexicanos %s y Ley de Planeación %s.</p>
        </section>
        <section class="pm" id="peItin" aria-labelledby="peItinTit">
          <p class="pm-eq-n">Y qué hizo el Estado con esa facultad · entregado el %s</p>
          <h2 class="pm-tit" id="peItinTit">El itinerario que manda la ley</h2>
          <p class="pm-txt">%s <b>Todavía no es ley:</b> la Cámara de Diputados puede modificarlo hasta el 15 de noviembre.</p>
          <ol class="pm-itin">%s</ol>
        </section>
        <section class="pm" id="peCifras" aria-labelledby="peCifrasTit">
          <h2 class="pm-tit" id="peCifrasTit">Cómo se ve el año que viene</h2>
          <p class="pm-txt">Primero los supuestos: cuánto se espera que crezca la economía, a cuánto el dólar, a cuánto el barril. De esos números cuelga todo lo demás. Después, el resultado: <b>%s</b> de ingreso, <b>%s</b> de gasto y la diferencia entre ambos, que es deuda nueva. %s</p>
          <div class="gp-tabla-caja"><table class="gp-tabla pm-tabla"><thead><tr><th scope="col">Variable</th><th scope="col">2026 aprobado</th><th scope="col">2026 estimado</th><th scope="col">2027 propuesto</th></tr></thead><tbody>%s</tbody></table></div>
          <p class="pm-pie">Criterios Generales de Política Económica 2027, anexos II.5 y III.1 %s. El rango de crecimiento se publica como rango: la estimación de ingresos usa su punto medio.</p>
          %s
          <p class="pm-pie">Criterios Generales de Política Económica 2027, anexo II.6 %s. La columna de 2026 es la aprobada en el Presupuesto vigente, no el cierre estimado.</p>
        </section>
        <section class="pm" id="peGasto" aria-labelledby="peGastoTit">
          <h2 class="pm-tit" id="peGastoTit">En qué se irá en 2027</h2>
          <p class="pm-txt">Tres lecturas del mismo gasto: por finalidad, por programa social y por obra prioritaria. %s</p>
          <h3 class="pm-sub">La clasificación funcional, renglón por renglón</h3>
          <div class="pm-hbars">%s</div>
          <p class="pm-pie">%s %s</p>
          <h3 class="pm-sub">Los veinte programas sociales prioritarios</h3>
          <p class="pm-txt">Suman <b>%s</b>, el %s del PIB. Una sola línea —la Pensión para Adultos Mayores— vale más que las otras diecinueve juntas.</p>
          <div class="pm-hbars">%s</div>
          <p class="pm-pie">%s %s</p>
          <h3 class="pm-sub">Las prioridades de inversión</h3>
          <p class="pm-txt">Suman <b>%s</b>. Pemex y la Comisión Federal de Electricidad se llevan <b>56.5%%</b> de ese total: la inversión prioritaria del país es, sobre todo, energía.</p>
          <div class="pm-hbars">%s</div>
          <p class="pm-pie">%s %s. La suma de los veinte renglones da $560,172.5 mdp; el cuadro publica $560,172.6 por redondeo de sus propias decimales.</p>
        </section>
        <section class="pm pm-sim" id="peSim" aria-labelledby="peSimTit">
          <h2 class="pm-tit" id="peSimTit">🎛️ Qué pasa si los supuestos fallan</h2>
          <p class="pm-txt">La propia Secretaría de Hacienda publica cuánto cuesta cada equivocación. Las seis palancas <b>no las inventó esta plataforma</b>: son los seis coeficientes del cuadro de sensibilidades de los Criterios %s, con su cita textual. Elige un escenario o mueve las palancas y mira a dónde va el déficit.</p>
          <div class="pm-escs" role="group" aria-label="Escenarios">%s</div>
          <p class="pm-esc-d" id="peEscDesc">%s</p>
          <div class="pm-sim-rej">
            <div class="pm-pals">%s</div>
            <div class="pm-res" id="peSimResultado" aria-live="polite"><noscript><p>El simulador necesita JavaScript; los coeficientes están a la izquierda, con su cita.</p></noscript></div>
          </div>
          <p class="pm-pie"><b>El límite de este simulador, dicho por la fuente.</b> Los Criterios advierten que sus sensibilidades «son indicativas, dentro de un rango de variación acotado, y consideran el efecto <b>aislado</b> de cada variable, sin incorporar sus posibles interacciones». Esta calculadora hereda esa limitación a propósito: añadir interacciones exigiría inventar coeficientes que nadie publicó. El PIB nominal también se mantiene fijo por la misma razón. Los resultados son %s: aplican los coeficientes oficiales a la diferencia contra el supuesto de los Criterios.</p>
          <script type="application/json" id="peDatos">%s</script>
        </section>
        <section class="pm" id="peFiscal" aria-labelledby="peFiscalTit">
          <h2 class="pm-tit" id="peFiscalTit">Lo que cambia en los impuestos sin llamarse reforma</h2>
          <p class="pm-txt">El paquete no crea un impuesto nuevo ni sube una tasa general. Hace otra cosa: cambia la base sobre la que se calcula el impuesto de las empresas. Hacienda lo justifica con un dato propio —en 2025, de <b>524 mil empresas</b> con ingresos positivos, <b>318 mil no pagaron ISR</b>— y lo presenta en la misma página donde promete que no habrá impuestos nuevos.</p>
          %s
          <p class="pm-pie">Criterios Generales de Política Económica 2027, apartados 3.3.2 y 3.3.3 %s, e iniciativas de los anexos D a H de la Gaceta Parlamentaria 7121 %s.</p>
        </section>
        <section class="pm" id="peColchon" aria-labelledby="peColchonTit">
          <h2 class="pm-tit" id="peColchonTit">El colchón, y lo que no está en la deuda</h2>
          <p class="pm-txt">Dos inventarios que el documento publica y la conversación pública rara vez cruza: con qué se amortigua un golpe, y qué compromisos existen sin contar como deuda.</p>
          <h3 class="pm-sub">Con qué se amortigua un golpe</h3>
          <p class="pm-txt">Lo que los Criterios enumeran como defensa del país ante un choque externo, con el saldo que cada instrumento tenía a mitad de 2026.</p>
          <div class="pm-rej">%s</div>
          <p class="pm-pie">Criterios Generales de Política Económica 2027, apartado 4.3.1 %s.</p>
          <h3 class="pm-sub">Los pasivos que no cuentan como deuda</h3>
          <p class="pm-txt">La deuda pública se declara en 55.0%% del PIB. Estos compromisos existen, los cuantifica el propio documento y no están dentro de esa cifra.</p>
          <div class="pm-rej">%s</div>
          <p class="pm-pie">Criterios Generales de Política Económica 2027, apartado 4.3.2 %s.</p>
        </section>
        <section class="pm" id="peSenda" aria-labelledby="peSendaTit">
          <h2 class="pm-tit" id="peSendaTit">La ruta a 2032</h2>
          <p class="pm-txt">El artículo 16 de la Ley Federal de Presupuesto obliga a proyectar a cinco años. La tabla se lee en dos renglones: el déficit y la deuda. Uno baja siempre; el otro sube siempre.</p>
          <div class="gp-tabla-caja"><table class="gp-tabla pm-tabla pm-senda">%s</table></div>
          <div class="pm-lectura"><p><b>Lo que enseña la fila de la deuda.</b> El déficit amplio baja todos los años, de 4.1%% a 3.1%% del PIB. Y la deuda sube todos los años: 55.0, 55.6, 56.1, 56.4, 56.5 y 56.5. <b>En ningún año del horizonte proyectado baja.</b> Se estabiliza hasta 2031, cuatro puntos y medio del PIB por encima de donde estaba en 2026.</p>
          <p><b>Y la del costo financiero.</b> Se queda clavada en 3.7%% del PIB hasta 2032. El superávit primario crece hasta 1.0%%, pero nunca alcanza a cubrir los intereses: por eso el balance sigue en déficit y por eso la deuda sigue subiendo.</p></div>
          <p class="pm-pie">%s %s</p>
        </section>
        <section class="pm" id="peCiegos" aria-labelledby="peCiegosTit">
          <h2 class="pm-tit" id="peCiegosTit">%s puntos ciegos del Paquete Económico 2027</h2>
          <p class="pm-txt">No son errores de Hacienda: casi todos están publicados en el propio documento. Son lugares donde el resumen que circuló y el texto oficial dejan de decir lo mismo. Cada uno trae lo que se dijo, lo que dice el documento y por qué la diferencia importa.</p>
          %s
        </section>
        <section class="pm pm-nota" id="peFuentes" aria-labelledby="peFuentesTit">
          <h2 class="pm-sub" id="peFuentesTit">De dónde sale cada cifra de esta página</h2>
          <ol class="pm-fuentes">
            <li><b>Criterios Generales de Política Económica 2027</b> %s — Anexo C de la Gaceta Parlamentaria número 7121. Marco macroeconómico, finanzas públicas, clasificación funcional, sensibilidades, amortiguadores, pasivos contingentes y proyecciones a 2032.</li>
            <li><b>Proyecto de Presupuesto de Egresos de la Federación 2027</b> %s — Anexo B. Su artículo 2o. fija el gasto neto total y el déficit presupuestario.</li>
            <li><b>Iniciativa de Ley de Ingresos de la Federación 2027</b> %s — Anexo A. Su artículo 1o. enumera los ingresos estimados y los techos de endeudamiento.</li>
            <li><b>Comunicado 71 de la Secretaría de Hacienda</b> %s — Presentación oficial del paquete.</li>
            <li><b>Ley Federal de Presupuesto y Responsabilidad Hacendaria</b> %s — artículos 16, 17, 31 y 42, que mandan el contenido del paquete, su calendario y la tolerancia de desviación.</li>
          </ol>
          <p class="pm-txt">El paquete se entregó el <b>%s</b> y se publicó en la %s. <b>Todavía no es ley</b>: la Cámara de Diputados puede modificarlo. Cuando se apruebe, esta página se contrastará renglón por renglón contra el decreto publicado en el Diario Oficial.</p>
        </section>''' % (
        indice,
        CE['entrada'], ref(CE['ref_fuente']), pilares, cadena, ref('ref-cpeum'), ref('ref-ley-planeacion'),
        P['entregado'], P['entrada'], itin,
        bill(P['simBase']['ingresos']), bill(P['simBase']['gastoNeto']), oficial, marco, pr('cgpe'), finanzas, pr('cgpe'),
        oficial, funcional, Fn['nota'], pr('cgpe'),
        mdp(S['total']), pct(S['pibPct']), lista(S['filas'], '#1b7f4c'), S['nota'], pr('cgpe'),
        mdp(I['total']), lista(I['filas'], '#0f6f8f'), I['nota'], pr('cgpe'),
        pr('cgpe'), escenarios, PE_ESCENARIOS[0]['d'], palancas, chip('derivado'), datos,
        fiscal, pr('cgpe'), pr('ilif'),
        amort, pr('cgpe'), conting, pr('cgpe'),
        senda, Sd['nota'], pr('cgpe'),
        {10: 'Diez', 11: 'Once', 12: 'Doce'}.get(len(P['ciegos']), str(len(P['ciegos']))), ciegos,
        pr('cgpe'), pr('ppef'), pr('ilif'), pr('com'), pr('lfprh'), P['entregado'], P['gaceta'])
