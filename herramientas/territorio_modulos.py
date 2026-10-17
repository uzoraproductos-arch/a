# -*- coding: utf-8 -*-
"""Los tres modulos de «Baja al territorio», cada uno en su pagina propia
(pedido del autor, 11-10-2026).

Antes eran tres tarjetas que desplegaban el auditor en un marco, debajo de
la portada de la parte. Ahora cada una es una pagina escrita aqui, con sus
cifras ya puestas desde window.AUDIT_DB (estados, fiscalEntidades,
panoramaErario.federalizado y panoramaErario.municipal):

  1. El mapa del gasto federalizado: el mapa de las 32 entidades, dibujado
     aqui en SVG desde mexico-states-geo.js (sin Leaflet ni teselas), con
     cinco lentes y el cuadro de las 32 de mayor a menor.
  2. Las 32 entidades: los tres pisos de la hacienda, lo que baja y con que
     libertad (los cuatro ramos del gasto federalizado) y el circuito de
     cada estado.
  3. Los 2,479 municipios: los dos fondos que el Presupuesto cifra como
     municipales, lo que la ley garantiza sin cifra, lo que cobran por su
     cuenta, el punto ciego del articulo 115 y el padron completo del INEGI.

Lo interactivo (lentes del mapa, selector de estado, buscador de
municipios) vive en assets/auditor/js/territorio.js; las cifras le llegan
en JSON escrito aqui. El padron municipal lo lee de municipios-efipem.js,
copia fiel de la fuente.

Lo usa apartados.numeros_preparar(); recibe `ref(id)`, que pinta la
llamada [nn] a fuentes-oficiales.html, y `glos(termino, texto)`.
"""
import json
import math
import os
import re

from presupuesto_modulos import chip, mdp, pct, bill, _seg, COLOR_FED

MAPA = 'numeros-mapa-del-gasto-federalizado.html'
ENTIDADES = 'numeros-las-32-entidades.html'
MUNICIPIOS = 'numeros-los-municipios.html'


def _json(x):
    # Dentro de <script type="application/json">: que nada cierre la etiqueta.
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def pend(id_):
    return chip('pendiente', id_)


# ---------------------------------------------------------------------------
# El mapa en SVG
# ---------------------------------------------------------------------------
def _geo(raiz):
    s = open(os.path.join(raiz, 'assets', 'auditor', 'js', 'mexico-states-geo.js'), encoding='utf-8').read()
    return json.loads(s[s.index('{'):s.rindex('}') + 1])


def _simplifica(pts, tol):
    """Douglas-Peucker: quita los vertices que no se notan a esta escala."""
    if len(pts) < 4:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    largo = math.hypot(dx, dy) or 1e-9
    peor, idx = -1, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / largo if (dx or dy) else math.hypot(x - x1, y - y1)
        if d > peor:
            peor, idx = d, i
    if peor <= tol:
        return [pts[0], pts[-1]]
    return _simplifica(pts[:idx + 1], tol)[:-1] + _simplifica(pts[idx:], tol)


def mapa_svg(raiz):
    """Las 32 entidades en una proyeccion equirrectangular corregida por la
    latitud media. Cada <path> lleva data-a con la clave de la entidad; el
    color lo pone territorio.js segun la lente."""
    g = _geo(raiz)
    K, LON0, LAT0 = 22.0, -117.3, 32.9
    cosl = math.cos(math.radians(23.5))

    def xy(c):
        return ((c[0] - LON0) * K * cosl, (LAT0 - c[1]) * K)

    estados = []
    xmax = ymax = 0
    for f in g['features']:
        polis = [f['geometry']['coordinates']] if f['geometry']['type'] == 'Polygon' else f['geometry']['coordinates']
        d = []
        for poli in polis:
            for anillo in poli:
                pts = _simplifica([xy(c) for c in anillo], 0.45)
                if len(pts) < 3:
                    continue
                xmax = max(xmax, max(p[0] for p in pts))
                ymax = max(ymax, max(p[1] for p in pts))
                d.append('M' + 'L'.join('%.1f %.1f' % p for p in pts) + 'Z')
        estados.append((f['properties']['abbr'], f['properties']['name'], ''.join(d)))
    return ('<svg class="tt-svg" viewBox="0 0 %d %d" role="group" aria-label="Mapa de las 32 entidades">%s</svg>' % (
        math.ceil(xmax) + 4, math.ceil(ymax) + 4,
        ''.join('<path class="tt-edo" data-a="%s" d="%s" tabindex="0" role="button" aria-label="%s"><title>%s</title></path>'
                % (a, d, n, n) for a, n, d in sorted(estados))))


# ---------------------------------------------------------------------------
# 1 · El mapa del gasto federalizado
# ---------------------------------------------------------------------------
def mapa(base, ref, raiz):
    E = base['estados']
    FE = base['fiscalEntidades']
    C = FE['campos']
    sin_dep = C['dep'].get('sinFuente', [])
    # El cuadre de la lente de los Ramos 28 y 33: lo que aprueba el
    # Presupuesto contra la suma de los 32 renglones, y lo que el acuerdo de
    # distribucion deja sin entidad.
    of = FE['totales']['ramo28'] + FE['totales']['ramo33']
    suma = sum(e['gasto'] for e in E)
    sin = FE['sinEntidad']['ramo28'] + FE['sinEntidad']['ramo33']
    resto = of - suma - sum(x['mdp'] for x in sin)
    cuadre = ('El Presupuesto de Egresos aprueba para los Ramos 28 y 33 juntos <b>%s</b> %s. Las 32 entidades suman <b>%s</b> %s. '
              'La diferencia, <b>%s</b>, es lo que el acuerdo de distribución no asigna a ninguna entidad: %s.%s' % (
                  mdp(of), chip('oficial'), mdp(suma), chip('derivado'), mdp(of - suma),
                  '; '.join('%s, %s' % (x['n'].lower() if x['n'].startswith(('No ', 'Componente')) else x['n'], mdp(x['mdp'])) for x in sin),
                  (' Quedan %s de redondeo a décimas.' % mdp(abs(resto))) if abs(resto) >= 0.5 else ''))
    deuda_f = sorted(set(e['deudaFuente'] for e in E), key=len)[0]
    sems = sorted(set(e['semaforoDeuda'] for e in E))
    lentes = [
        {'id': 'gasto', 'nom': 'Ramos 28 y 33', 'fmt': 'mdp', 'est': 'derivado', 'pal': 'oro', 'suma': True,
         'que': 'Lo que cada estado recibe en 2026 por participaciones (Ramo 28) y aportaciones (Ramo 33), las dos vías que fija la Ley de Coordinación Fiscal.',
         'fuente': 'Ramo 28: Anexo 15 del acuerdo de distribución (DOF 12-12-2025) %s. Ramo 33: Anexo 16, versión modificada (DOF 09-07-2026) %s. La suma de los dos es nuestra.' % (
             ref('ref-dof-distribucion-2026'), ref('ref-dof-distribucion-2026-mod')),
         'cuadre': cuadre},
        {'id': 'pc', 'nom': 'Por habitante', 'fmt': 'pesos', 'est': 'derivado', 'pal': 'oro', 'suma': False,
         'que': 'Los mismos Ramos 28 y 33, divididos entre la población de cada estado: así se comparan un estado grande y uno chico.',
         'fuente': 'Ramos 28 y 33 de 2026 ÷ población a mitad de 2026 según el CONAPO (<a href="%s">proyecciones, datos abiertos</a>).' % C['pc']['url']},
        {'id': 'dep', 'nom': 'Dependencia federal', 'fmt': 'pct', 'est': 'derivado', 'pal': 'azul', 'suma': False,
         'que': 'De cada $100 que el gobierno del estado ingresó en 2024, sin contar deuda, cuántos llegaron de la Federación.',
         'fuente': '%s %s' % (C['dep']['fuente'], ref(C['dep']['ref'])),
         'falta': sin_dep, 'falta_pend': 'entidades-' + '-'.join(sin_dep).lower(),
         'falta_txt': 'La Ciudad de México no figura en la estadística estatal del INEGI: su dependencia sigue pendiente.'},
        {'id': 'deuda', 'nom': 'Deuda registrada', 'fmt': 'mdp', 'est': 'oficial', 'pal': 'rojo', 'suma': True,
         'que': 'Lo que cada gobierno estatal debe según el Sistema de Alertas de Hacienda. ' + (
             'Las 32 están hoy en semáforo %s.' % sems[0].lower() if len(sems) == 1 else 'El color del semáforo va en su ficha.'),
         'fuente': '%s %s' % (deuda_f, ref('ref-shcp-alertas'))},
        {'id': 'asf', 'nom': 'Por aclarar ante la ASF', 'fmt': 'mdp', 'est': 'oficial', 'pal': 'rojo', 'suma': True,
         'que': 'Lo que la Auditoría Superior de la Federación dejó por aclarar del dinero federal que recibió cada estado en 2024.',
         'fuente': '%s %s' % (E[0]['asfFuente'], ref('ref-asf-mdb2024'))},
    ]
    datos = {
        'lentes': lentes,
        'e': [{'a': e['abbr'], 'n': e['name'], 'gasto': e['gasto'], 'r28': e['ramo28'], 'r33': e['ramo33'], 'pc': e['pc'],
               'dep': None if e['abbr'] in sin_dep else e['dep'], 'deuda': e['deuda'], 'sem': e['semaforoDeuda'],
               'asf': e['asfMontoObservado'], 'aud': e['asfAuditorias']} for e in E],
        'ent': ENTIDADES, 'mun': MUNICIPIOS,
    }
    botones = ''.join('<button type="button" class="tt-lente" role="radio" aria-checked="%s" data-l="%s">%s</button>'
                      % ('true' if i == 0 else 'false', l['id'], l['nom']) for i, l in enumerate(lentes))
    return '''<section class="pm tt-mapa" id="ttMapa" aria-labelledby="ttMapaTit">
          <h2 class="pm-tit" id="ttMapaTit">Las 32 entidades, sobre el territorio</h2>
          <p class="pm-txt">De los <b>%s</b> del gasto federalizado, la mayor parte viaja por dos ramos: las participaciones y las aportaciones. Elige qué quieres ver; el mapa y el cuadro de abajo cambian juntos. Toca un estado para ver su ficha.</p>
          <div class="tt-lentes" role="radiogroup" aria-label="Qué mostrar en el mapa">%s</div>
          <p class="tt-que" id="ttQue"></p>
          <div class="tt-mapa-rej">
            <figure class="tt-fig">
              %s
              <figcaption class="tt-leyenda" id="ttLeyenda"></figcaption>
            </figure>
            <aside class="tt-ficha" id="ttFicha" aria-live="polite"></aside>
          </div>
          <div class="tt-res" id="ttRes"></div>
          <p class="pm-pie" id="ttFuente"></p>
          <p class="pm-pie tt-cuadre" id="ttCuadre"></p>
        </section>
        <section class="pm" aria-labelledby="ttRankTit">
          <h2 class="pm-tit" id="ttRankTit">De mayor a menor</h2>
          <p class="pm-txt" id="ttRankTxt"></p>
          <ol class="tt-rank" id="ttRank"></ol>
        </section>
        <script type="application/json" id="ttMapaDatos">%s</script>''' % (
        bill(base['panoramaErario']['federalizado']['totalMdp']), botones, mapa_svg(raiz), _json(datos))


# ---------------------------------------------------------------------------
# 2 · Las 32 entidades
# ---------------------------------------------------------------------------
LIBERTAD = {'fed-r28': ('libre', 'El estado decide en qué'), 'fed-r33': ('etiq', 'Llega con destino fijado por ley'),
            'fed-r25': ('etiq', 'Llega con destino fijado'), 'fed-conv': ('pacto', 'Se pacta caso por caso')}


def entidades(base, ref, glos):
    P = base['panoramaErario']
    F = P['federalizado']
    E = base['estados']
    C = base['fiscalEntidades']['campos']
    total = F['totalMdp']
    pisos = ''.join(
        '<article class="tt-piso tt-piso-%s"><header><span aria-hidden="true">%s</span><h3>%s</h3></header>'
        '<dl><dt>Cobra por su cuenta</dt><dd>%s</dd><dt>Aprueba su ingreso</dt><dd>%s</dd>'
        '<dt>Aprueba su gasto</dt><dd>%s</dd><dt>Lo revisa</dt><dd>%s</dd></dl><footer>%s</footer></article>' % (
            p['color'], p['icono'], p['nivel'], p['recauda'], p['apruebaIngreso'], p['apruebaGasto'], p['fiscaliza'], p['fundamento'])
        for p in P['pisos'])
    comp = F['componentes']
    barra = ''.join(_seg(c['montoMdp'] / total * 100, COLOR_FED[c['id']], '%s: %s' % (c['nombre'], mdp(c['montoMdp'])),
                         '%s<small>%s</small>' % (c['nombre'].split(' — ')[0], pct(c['montoMdp'] / total * 100))) for c in comp)

    def dentro(c):
        if c.get('componentes'):
            mayor = max(x['m'] for x in c['componentes'])
            return '<ul class="tt-fondos">%s</ul>' % ''.join(
                '<li><span>%s</span><span class="tt-fondo-b"><span style="--w:%.2f%%;--c:%s"></span></span><b class="num-tabular">%s</b></li>'
                % (x['n'].split(' — ')[0], x['m'] / mayor * 100, COLOR_FED[c['id']], mdp(x['m'])) for x in c['componentes'])
        if c.get('reglas'):
            return '<ul class="tt-reglas">%s</ul>' % ''.join('<li><b>%s</b> <span>%s</span></li>' % (r['n'], r['v']) for r in c['reglas'])
        return ''
    ramos = ''.join(
        '<article class="tt-ramo" style="--c:%s"><p class="tt-ramo-lib tt-%s">%s</p>'
        '<h3><span aria-hidden="true">%s</span> %s</h3>'
        '<p class="tt-ramo-v"><b class="num-tabular">%s</b> %s <small>%s del gasto federalizado</small></p>'
        '<p>%s</p>%s<p class="tt-ramo-ley">%s %s%s</p></article>' % (
            COLOR_FED[c['id']], LIBERTAD[c['id']][0], LIBERTAD[c['id']][1], c['icono'], c['nombre'],
            mdp(c['montoMdp']), chip(c['estado']), pct(c['montoMdp'] / total * 100), c['queEs'], dentro(c), c['ley'], ref(c['refKey']),
            (' · ' + glos(c['glos'], '📖 El concepto')) if c.get('glos') else '')
        for c in comp)
    sin = C['recaudacionPropia'].get('sinFuente', [])
    datos = {
        'sin': sin, 'pend': 'entidades-' + '-'.join(sin).lower(),
        'e': sorted([{'a': e['abbr'], 'n': e['name'], 'cap': e['capital'], 'pob': e['pob'], 'gob': e['gobernador'],
                      'r28': e['ramo28'], 'r33': e['ramo33'],
                      'conv': None if e['abbr'] in sin else e['convenios'],
                      'propia': None if e['abbr'] in sin else e['recaudacionPropia'],
                      'fed24': None if e['abbr'] in sin else e.get('federal2024'),
                      'dep': None if e['abbr'] in sin else e['dep'],
                      'deuda': e['deuda'], 'sem': e['semaforoDeuda']} for e in E], key=lambda x: x['n']),
        'mapa': MAPA, 'mun': MUNICIPIOS,
    }
    opciones = ''.join('<option value="%s">%s</option>' % (e['a'], e['n']) for e in datos['e'])
    return '''<section class="pm" aria-labelledby="ttPisosTit">
          <h2 class="pm-tit" id="ttPisosTit">Tres pisos, tres haciendas</h2>
          <p class="pm-txt">México no tiene una %s, tiene tres superpuestas. Cada piso cobra sus impuestos, aprueba su presupuesto y responde ante un fiscalizador distinto. Saber quién cobra qué y quién revisa a quién es saber a qué puerta tocar cuando algo no cuadra.</p>
          <div class="tt-pisos">%s</div>
          <p class="pm-pie">Una asimetría que casi nunca se menciona: la ley de ingresos del municipio no la aprueba el municipio, la aprueba el congreso del estado. Se explica en <a href="%s#ttCiego">Los 2,479 municipios</a>.</p>
        </section>
        <section class="pm" aria-labelledby="ttBajaTit">
          <h2 class="pm-tit" id="ttBajaTit">Lo que baja, y con qué libertad</h2>
          <p class="pm-txt">El gasto federalizado de 2026 son <b>%s</b>, en cuatro renglones. La diferencia que más importa: el Ramo 28 es dinero del estado; el Ramo 33 sigue siendo dinero federal después de entregarse, y por eso lo revisa la Auditoría Superior de la Federación.</p>
          <div class="pm-barra pm-barra-alta" role="img" aria-label="Gasto federalizado 2026 por ramo">%s</div>
          <div class="tt-ramos">%s</div>
          <p class="pm-pie">%s %s</p>
        </section>
        <section class="pm" id="circuito" aria-labelledby="ttCircTit">
          <h2 class="pm-tit" id="ttCircTit">El circuito de cada estado</h2>
          <p class="pm-txt">Elige un estado: cuánto le baja de la Federación, cuánto cobra por su cuenta y qué tan dependiente resulta la suma.</p>
          <label class="tt-sel"><span>Entidad federativa</span><select id="ttEntSel">%s</select></label>
          <div class="tt-circ" id="ttCirc" aria-live="polite"></div>
          <p class="pm-pie">El Ramo 28 y el Ramo 33 salen del acuerdo con que Hacienda reparte ambos ramos entre las entidades, publicado en el Diario Oficial %s %s. Los convenios, la recaudación propia y la dependencia son de 2024, el último año con cifras definitivas en la estadística estatal del INEGI %s; por eso la razón entre lo federal y lo propio usa las dos cifras de 2024 y no mezcla años. La dependencia no cuenta la deuda: un préstamo no es autonomía. La población es la del CONAPO a mitad de 2026 %s.</p>
        </section>
        <script type="application/json" id="ttEntDatos">%s</script>''' % (
        glos('Hacienda Pública', 'hacienda pública'), pisos, MUNICIPIOS,
        bill(total), barra, ramos, F['nota'], ref('ref-pef2026'), opciones,
        ref('ref-dof-distribucion-2026'), ref('ref-dof-distribucion-2026-mod'), ref('ref-inegi-efipem-estatal'), chip('derivado'),
        _json(datos))


# ---------------------------------------------------------------------------
# 3 · Los 2,479 municipios
# ---------------------------------------------------------------------------
def municipios(base, ref, glos, raiz):
    M = base['panoramaErario']['municipal']
    s = open(os.path.join(raiz, 'assets', 'auditor', 'js', 'municipios-efipem.js'), encoding='utf-8').read()
    nac = dict(re.findall(r'(\w+):(\d+)', re.search(r'nacional:\s*\{([^}]*)\}', s).group(1)))
    nac = {k: int(v) / 1e6 for k, v in nac.items()}
    catalogo = int(re.search(r'catalogo:\s*(\d+)', s).group(1))
    con = int(re.search(r'conCifra:\s*(\d+)', s).group(1))
    anio = int(re.search(r'anio:\s*(\d+)', s).group(1))
    fondos = M['fuentes']
    etiq = M['etiquetadoMdp']
    fichas = ''.join(
        '<article class="tt-ramo" style="--c:%s"><p class="tt-ramo-lib tt-%s">%s</p><h3><span aria-hidden="true">%s</span> %s</h3>'
        '<p class="tt-ramo-v"><b class="num-tabular">%s</b> %s <small>%s de los dos</small></p><p>%s</p>'
        '<ul class="tt-reglas">%s</ul><p class="tt-ramo-ley">%s %s · %s</p></article>' % (
            c, cls, lib, f['icono'], f['nombre'], mdp(f['montoMdp']), chip(f['estado']), pct(f['montoMdp'] / etiq * 100),
            f['queEs'], ''.join('<li><b>%s</b> <span>%s</span></li>' % (r['n'], r['v']) for r in f['reglas']),
            f['ley'], ref(f['refKey']), glos(f['glos'], '📖 El concepto'))
        for f, (c, cls, lib) in zip(fondos, [('#1b7f4c', 'libre', 'Con holgura, dentro de su destino legal'),
                                              ('#c9a84c', 'etiq', 'Solo obra para población en pobreza')]))
    barra = ''.join(_seg(f['montoMdp'] / etiq * 100, c, '%s: %s' % (f['nombre'], mdp(f['montoMdp'])),
                         '%s<small>%s</small>' % (f['nombre'], mdp(f['montoMdp'])))
                    for f, c in zip(fondos, ('#1b7f4c', '#c9a84c')))
    sincifra = ''.join('<article class="pm-t"><p class="pm-tag">%s</p><h4>%s</h4><p>%s</p><p class="pm-t-v">sin cifra nacional</p></article>'
                       % (x['clave'], x['nombre'], x['que']) for x in M['sinCifra'])
    prop = M['propios']
    mayor = max(x['montoMdp'] for x in prop)
    propios = ''.join(
        '<div class="pm-hbar pm-hbar-s"><span class="pm-hbar-n"><span aria-hidden="true">%s</span> <b>%s</b><small>Art. %s de la Constitución</small></span>'
        '<span class="pm-hbar-b"><span class="pm-seg" style="--w:%.2f%%;--c:%s"></span></span><b class="num-tabular">%s %s</b></div>' % (
            x['icono'], x['nombre'], x['clave'], x['montoMdp'] / mayor * 100, '#1b7f4c' if 'part' not in x['id'] else '#d0632a',
            mdp(x['montoMdp']), chip(x['estado'])) for x in prop)
    pred = next(x for x in prop if x['id'] == 'mp-predial')
    partic = next((x for x in prop if 'part' in x['id']), None)
    veces = (partic['montoMdp'] / pred['montoMdp']) if partic else None
    A = M['asimetria']
    return '''<section class="pm" aria-labelledby="ttMun1">
          <p class="pm-eq-n">1 de 4</p>
          <h2 class="pm-tit" id="ttMun1">Lo que el Presupuesto le entrega con nombre</h2>
          <p class="pm-txt">De los ocho fondos del %s, solo dos llegan cifrados como municipales: el %s y el %s. Juntos suman <b>%s</b> %s en 2026.</p>
          <div class="pm-barra pm-barra-alta" role="img" aria-label="FORTAMUN y FISMDF 2026">%s</div>
          <div class="tt-ramos tt-ramos-2">%s</div>
          <p class="pm-pie">%s %s</p>
          <h3 class="pm-sub">Y lo que la ley le garantiza sin ponerle cifra</h3>
          <p class="pm-txt">El resto del dinero federal del municipio llega por participaciones, y su reparto no lo fija la Federación sino la legislatura de cada estado: no hay una regla, hay treinta y dos.</p>
          <div class="pm-rej">%s</div>
          <p class="pm-pie">Ley de Coordinación Fiscal %s.</p>
        </section>
        <section class="pm" aria-labelledby="ttMun2">
          <p class="pm-eq-n">2 de 4</p>
          <h2 class="pm-tit" id="ttMun2">Lo que cobra por su cuenta</h2>
          <p class="pm-txt">El artículo 115, fracción IV, de la Constitución enumera tres ingresos que el municipio recibe «en todo caso». Su total nacional no está en el Presupuesto: se rehace sumando lo que reportaron al INEGI los <b>%s</b> de los %s municipios que rindieron su cuenta de %d.</p>
          <div class="pm-hbars">%s</div>
          %s
          <p class="pm-pie">Suma de las cuentas municipales de %d en la estadística de finanzas públicas del INEGI %s. Faltan los municipios que no reportaron y las dieciséis demarcaciones de la Ciudad de México, que no rinden cuenta municipal %s.</p>
        </section>
        <section class="pm pm-aviso" id="ttCiego" aria-labelledby="ttMun3">
          <p class="pm-eq-n">3 de 4 · El punto ciego</p>
          <h2 class="pm-tit" id="ttMun3">%s</h2>
          <p class="pm-txt">%s</p>
          <p class="pm-txt">%s</p>
          <p class="pm-pie">Constitución Política, art. 115, fracción IV %s.</p>
        </section>
        <section class="pm" id="padron" aria-labelledby="ttMun4">
          <p class="pm-eq-n">4 de 4</p>
          <h2 class="pm-tit" id="ttMun4">Municipio por municipio</h2>
          <p class="pm-txt">Los %s municipios del catálogo del INEGI, con lo que de verdad ingresó cada uno en %d: su predial, sus participaciones, sus dos fondos del Ramo 33 y qué tan dependiente resulta la suma. El que no rindió cuenta sigue en la lista, sin cifra: borrarlo falsearía el padrón y ponerle cero falsearía la cifra.</p>
          <div class="tt-mun-mandos">
            <label class="tt-sel"><span>Entidad federativa</span><select id="ttMunSel"></select></label>
            <label class="tt-sel"><span>Buscar municipio</span><input type="search" id="ttMunBusca" placeholder="Escribe un nombre" autocomplete="off"></label>
            <label class="tt-sel"><span>Ordenar por</span><select id="ttMunOrden">
              <option value="nombre">Nombre (A–Z)</option><option value="ing">Ingreso total</option><option value="predial">Predial cobrado</option>
              <option value="fortamun">FORTAMUN recibido</option><option value="fismdf">FISMDF recibido</option><option value="dep">Dependencia de transferencias</option></select></label>
          </div>
          <div id="ttMun" aria-live="polite"><noscript><p>El padrón necesita JavaScript. Los datos completos se descargan en <a href="descarga-los-datos.html">Datos</a>.</p></noscript></div>
        </section>
        <script type="application/json" id="ttMunDatos">%s</script>''' % (
        glos('Ramo 33 (Aportaciones Federales)', 'Ramo 33'), glos('FORTAMUN', 'FORTAMUN'), glos('FISMDF / FAIS', 'FISMDF'),
        mdp(etiq), chip('oficial'), barra, fichas, M['nota'], ref('ref-pef2026'), sincifra, ref('ref-lcf'),
        format(con, ','), format(catalogo, ','), anio, propios,
        ('<p class="pm-op">Puesto en perspectiva: los municipios recibieron de participaciones <b>%.1f veces</b> lo que cobraron de predial %s '
         '(%s ÷ %s). Es el impuesto que la Constitución les reserva en exclusiva, y el que menos pesa en su bolsa.</p>' % (
             veces, chip('derivado'), mdp(partic['montoMdp']), mdp(pred['montoMdp']))) if veces else '',
        anio, ref('ref-inegi-efipem'), pend('municipios-sin-cuenta'),
        A['titulo'], A['texto'], A['consecuencia'], ref('ref-cpeum'),
        format(catalogo, ','), anio,
        _json({'mapa': MAPA, 'ent': ENTIDADES, 'pend': 'municipios-sin-cuenta', 'nom': {e['abbr']: e['name'] for e in base['estados']}}))
