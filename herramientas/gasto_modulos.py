# -*- coding: utf-8 -*-
"""Tres desgloses de «Gasto publico», en pagina propia (pedido del autor,
12-10-2026): el margen del presupuesto, los ramos y dependencias, y lo que
la cifra grande no dice.

Antes cada pagina cargaba el auditor completo en un marco (unos 4 MB de
JavaScript) y, ya abierto, el margen esperaba en ceros a que alguien
pulsara «Contabilizar». Ahora la pagina se escribe aqui con sus cifras
puestas, desde window.AUDIT_DB: se lee sin JavaScript y sin esperar.

Datos:
- panoramaErario.egresos: los ocho renglones del gasto, con su fuente.
- panoramaErario.anexo1PEF2026: el Anexo 1 del decreto del Presupuesto 2026,
  ramo por ramo, en pesos (pp. 33-34). Sustituye al «treemap» del motor,
  cuyos montos por dependencia no tenian documento (12-10-2026).
- panoramaErario.gastosObligatoriosPEF2026: el Anexo 3 del mismo decreto.
- panoramaErario.puntosCiegos: las cinco lecturas.

Lo usa apartados.numeros_preparar(); recibe `ref(id)`, que pinta la
llamada [nn] a fuentes-oficiales.html, y `glos(termino, texto)`.
"""
from presupuesto_modulos import chip, mdp, bill, pct, COLOR_EGR, _seg


def egreso_archivo(x):
    """El mismo nombre que apartados.egreso_archivo (sin importarlo: evita
    el ciclo de importacion)."""
    return 'numeros-egreso-%s.html' % {
        'egr-social': 'desarrollo-social', 'egr-economico': 'desarrollo-economico', 'egr-gobierno': 'gobierno',
        'egr-poderes': 'poderes-y-organos-autonomos', 'egr-fondos': 'fondos-de-estabilizacion',
        'egr-costofin': 'costo-financiero', 'egr-participaciones': 'participaciones', 'egr-adefas': 'adefas'}[x['id']]


def _pdoc(url, paginas, texto):
    return '<a href="%s#page=%s" target="_blank" rel="noopener">%s, pp. %s ↗</a>' % (url, paginas.split('-')[0], texto, paginas)


# ---------------------------------------------------------------------------
# ¿Cuanto margen tiene el presupuesto?
# ---------------------------------------------------------------------------
def margen(base, ref, glos):
    P = base['panoramaErario']
    tot = P['totalPEF']
    eg = {x['id']: x for x in P['egresos']}
    nopr = [x for x in P['egresos'] if x['grupo'] == 'No programable']
    sn = round(sum(x['montoMdp'] for x in nopr), 1)
    sp = round(tot - sn, 1)
    pp, pn = sp / tot * 100, sn / tot * 100
    G = P['gastosObligatoriosPEF2026']
    ob, obp = G['obligatoriosMdp'], G['conPensionesMdp']
    resto = round(tot - obp, 1)

    tramos = [('Se programa', sp, '#1b7f4c', None)] + [(x['nombre'], x['montoMdp'], COLOR_EGR[x['id']], egreso_archivo(x)) for x in nopr]
    barra = ''.join(_seg(v / tot * 100, c, '%s: %s (%s)' % (n, mdp(v), pct(v / tot * 100)),
                         '%s<small>%s</small>' % (n if v / tot > .3 else '', pct(v / tot * 100)), href)
                    for n, v, c, href in tramos)
    ley = ''.join('<li><span class="pm-punto" style="--c:%s"></span><b>%s</b> <span class="num-tabular">%s</span> · %s %s%s</li>'
                  % (c, ('<a href="%s">%s</a>' % (href, n)) if href else n, mdp(v), pct(v / tot * 100), chip('derivado'),
                     '' if href else '<small>Gasto programable: el total menos lo no programable (%s − %s).</small>' % (mdp(tot), mdp(sn)))
                  for n, v, c, href in tramos)

    # El termostato: un arco con el % programable, ya puesto.
    C = 314.16
    arco = ('<svg class="gm-dial" viewBox="0 0 130 130" role="img" aria-label="Margen programable: %s del gasto">'
            '<circle cx="65" cy="65" r="50" fill="none" stroke="#e6ebf3" stroke-width="12"/>'
            '<circle cx="65" cy="65" r="50" fill="none" stroke="#1b7f4c" stroke-width="12" stroke-linecap="round" transform="rotate(-90 65 65)" '
            'stroke-dasharray="%.2f" stroke-dashoffset="%.2f" class="gm-dial-arco" style="--c0:%.2f"/>'
            '<text x="65" y="66" text-anchor="middle" class="gm-dial-n">%s</text>'
            '<text x="65" y="84" text-anchor="middle" class="gm-dial-pie">se programa</text></svg>'
            % (pct(pp), C, C * (1 - pp / 100), C, pct(pp)))
    tres = ''.join('<li class="gm-mini" style="--c:%s"><span>%s</span><b class="num-tabular">%s</b><small>%s</small></li>'
                   % (COLOR_EGR[x['id']], x['nombre'], pct(x['montoMdp'] / tot * 100), mdp(x['montoMdp'])) for x in nopr)

    obl = (_seg(obp / tot * 100, '#7a2a24', 'Gastos obligatorios con pensiones: %s' % mdp(obp), 'Obligatorio, con pensiones<small>%s</small>' % pct(obp / tot * 100))
           + _seg(resto / tot * 100, '#e6ebf3', 'Fuera de esa previsión: %s' % mdp(resto), 'El resto<small>%s</small>' % pct(resto / tot * 100), extra=' data-claro="1"'))

    return '''<section class="pm" aria-labelledby="gmProTit">
          <h2 class="pm-tit" id="gmProTit">De cada $100 del gasto, cuánto se decide</h2>
          <p class="pm-txt">El gasto de 2026 suma <b>%s</b> %s. Una parte se <b>programa</b>: se reparte cada año entre escuelas, hospitales, pensiones y obras. La otra, la <b>no programable</b>, no se decide: se debe. Son los intereses de la deuda, lo que la ley ya les da a los estados y las cuentas del año pasado.</p>
          <div class="pm-barra pm-barra-alta" role="img" aria-label="Gasto programable %s; no programable %s">%s</div>
          <ul class="pm-ley pm-ley-fila">%s</ul>
          <p class="pm-pie">Los tres renglones no programables son del Anexo 1 del decreto %s; cada porcentaje es renglón ÷ %s %s. Toca un renglón para ver su página.</p>
        </section>

        <section class="pm" aria-labelledby="gmTermTit">
          <h2 class="pm-tit" id="gmTermTit">🌡️ El termostato del presupuesto</h2>
          <div class="gm-term">
            %s
            <div class="gm-term-tx">
              <p class="pm-txt">De cada $100 del gasto federal de 2026, <b>$%.2f</b> se programan y <b>$%.2f</b> ya están comprometidos por ley antes de empezar el año %s.</p>
              <ul class="gm-minis">%s</ul>
            </div>
          </div>
          <p class="pm-op">Operación: %s ÷ %s × 100 = %s %s. La «rigidez» es su complemento: %s ÷ %s × 100 = %s.</p>
        </section>

        <section class="pm" aria-labelledby="gmOblTit">
          <h2 class="pm-tit" id="gmOblTit">Y dentro de lo programable, tampoco todo se mueve</h2>
          <p class="pm-txt">Que un gasto sea «programable» no quiere decir que se pueda recortar. Pensiones, nómina y los programas que la Constitución vuelve universales se pagan año con año. El propio decreto lo reconoce: su <b>Anexo 3</b> prevé <b>%s</b> de gastos obligatorios %s, y <b>%s</b> si se cuentan las pensiones y jubilaciones %s.</p>
          <div class="pm-barra pm-barra-alta" role="img" aria-label="Gastos obligatorios con pensiones: %s del gasto">%s</div>
          <p class="pm-op">Operación: %s ÷ %s × 100 = <b>%s</b> %s. Sin pensiones: %s ÷ %s × 100 = %s %s. Lo que queda fuera de esa previsión: %s − %s = <b>%s</b> %s.</p>
          <p class="pm-pie">%s Fuente: %s %s.</p>
        </section>
        <p class="pm-sigue">¿Qué más esconde la cifra total? <a href="numeros-lo-que-la-cifra-no-dice.html">🔦 Lo que la cifra grande no dice ➔</a></p>''' % (
        mdp(tot), chip('oficial'), pct(pp), pct(pn), barra, ley, ref('ref-pef2026'), mdp(tot), chip('derivado'),
        arco, pp, pn, chip('derivado'), tres,
        mdp(sp), mdp(tot), pct(pp), chip('derivado'), mdp(sn), mdp(tot), pct(pn),
        mdp(ob), chip('oficial'), mdp(obp), chip('oficial'),
        pct(obp / tot * 100), obl,
        mdp(obp), mdp(tot), pct(obp / tot * 100), chip('derivado'), mdp(ob), mdp(tot), pct(ob / tot * 100), chip('derivado'),
        mdp(tot), mdp(obp), mdp(resto), chip('derivado'),
        G['nota'], _pdoc(G['url'], G['paginas'], 'Presupuesto de Egresos 2026, Anexo 3'), ref(G['refKey']))


# ---------------------------------------------------------------------------
# En que se va: ramos y dependencias
# ---------------------------------------------------------------------------
def egresos(base, ref, glos):
    P = base['panoramaErario']
    tot = P['totalPEF']
    A = P['anexo1PEF2026']
    gnt = A['gastoNetoTotal'] / 1e6
    assert abs(gnt - tot) < 0.05, (gnt, tot)
    m = lambda pesos: pesos / 1e6

    # 1. Por finalidad: los ocho renglones, cada uno a su pagina.
    eg = sorted(P['egresos'], key=lambda x: -x['montoMdp'])
    maxe = eg[0]['montoMdp']
    fin = ''.join(
        '<a class="pm-hbar gm-hbar" href="%s"><span class="pm-hbar-n"><span aria-hidden="true">%s</span> %s<small>%s</small></span>'
        '<span class="pm-hbar-b" aria-hidden="true">%s</span><b class="num-tabular">%s</b><span class="pm-var">%s</span></a>'
        % (egreso_archivo(x), x['icono'], x['nombre'], x['grupo'], _seg(x['montoMdp'] / maxe * 100, COLOR_EGR[x['id']], x['nombre'], ''),
           mdp(x['montoMdp']), pct(x['montoMdp'] / tot * 100)) for x in eg)

    # 2. Ramo por ramo (Anexo 1).
    todos = [r for g in A['grupos'] for r in g['ramos']]
    maxr = max(r['pesos'] for r in todos)

    def fila(r):
        nombre = r['nombre']
        clave = ('Ramo %s' % r['ramo']) if r['ramo'].isdigit() else r['ramo']
        tag = '<span class="pm-tag">no programable</span>' if r['tipo'] == 'No programable' else ''
        cuerpo = ('<span class="pm-hbar-n">%s%s<small>%s</small></span><span class="pm-hbar-b" aria-hidden="true">%s</span>'
                  '<b class="num-tabular">%s</b><span class="pm-var">%s</span>'
                  % (tag, nombre, clave, _seg(max(r['pesos'] / maxr * 100, .4), '#0f6f8f' if r['tipo'] == 'Programable' else '#b3261e', nombre, ''),
                     mdp(m(r['pesos'])), pct(r['pesos'] / A['gastoNetoTotal'] * 100, 2)))
        if r.get('unidades'):
            uni = ''.join('<li><span>%s</span><b class="num-tabular">%s</b></li>' % (u['nombre'], mdp(m(u['pesos']))) for u in r['unidades'])
            return ('<details class="gm-ramo"><summary class="pm-hbar">%s</summary><ul class="gm-uni">%s</ul>'
                    '<p class="pm-pie">Más del %s: <a href="numeros-lo-que-cuestan-los-poderes.html">⚖️ Lo que cuestan el Congreso y la Judicatura ➔</a></p></details>'
                    % (cuerpo, uni, nombre))
        return '<div class="pm-hbar">%s</div>' % cuerpo

    LEMA = {'A': 'Los Poderes y los órganos que la Constitución hace autónomos.',
            'B': 'Las secretarías y dependencias del Ejecutivo: lo que cada una recibe.',
            'C': 'Dinero que no administra una secretaría: aportaciones, participaciones, deuda y provisiones.',
            'D': 'El IMSS y el ISSSTE, con su propio presupuesto.',
            'E': 'Pemex y la CFE, incluido el costo financiero de su deuda.'}
    bloques = []
    for g in A['grupos']:
        orden = sorted(g['ramos'], key=lambda r: -r['pesos'])
        fuera = [r for r in g['ramos'] if r.get('fueraDeSubtotal')]
        sub = g['subtotal'] + sum(r['pesos'] for r in fuera)
        bloques.append(
            '<details class="gm-grupo"%s><summary><span class="gm-grupo-l">%s</span><span class="gm-grupo-n">%s<small>%s · %d %s</small></span>'
            '<b class="num-tabular">%s</b></summary>\n            <div class="pm-hbars">%s</div>%s</details>'
            % (' open' if g['clave'] in ('B',) else '', g['clave'], {'A': 'Ramos autónomos', 'B': 'Ramos administrativos', 'C': 'Ramos generales', 'D': 'Entidades de control directo', 'E': 'Empresas públicas del Estado'}[g['clave']],
               LEMA[g['clave']], len(g['ramos']), 'renglones' if len(g['ramos']) != 1 else 'renglón', mdp(m(sub)),
               ''.join(fila(r) for r in orden),
               ('<p class="pm-pie">%s</p>' % A['notaSubtotal']) if fuera else ''))

    suma = sum(r['pesos'] for r in todos)
    top = sorted(todos, key=lambda r: -r['pesos'])[:10]
    top_li = ''.join('<li><span class="gm-top-n">%d</span><span>%s<small>%s</small></span><b class="num-tabular">%s</b></li>'
                     % (i + 1, r['nombre'], ('Ramo %s' % r['ramo']) if r['ramo'].isdigit() else 'Entidad %s' % r['ramo'], bill(m(r['pesos'])))
                     for i, r in enumerate(top))
    fuente = _pdoc(A['url'], A['paginas'], 'Presupuesto de Egresos 2026, Anexo 1')

    return '''<section class="pm" aria-labelledby="gmFinTit">
          <h2 class="pm-tit" id="gmFinTit">Primero, por finalidad: los ocho renglones</h2>
          <p class="pm-txt">El gasto se parte en dos mundos. El <b>programable</b> se decide cada año y compra cosas: pensiones, escuelas, hospitales, carreteras. El <b>no programable</b> no se decide, se debe: intereses, participaciones que ya son de los estados y cuentas del año pasado. Toca un renglón para ver su página.</p>
          <div class="pm-hbars">%s</div>
          <p class="pm-pie">Los cinco renglones programables son la clasificación funcional que Hacienda publica en miles de millones %s; los tres no programables, del decreto %s. Todos son %s; el porcentaje es renglón ÷ %s %s.</p>
        </section>

        <section class="pm" aria-labelledby="gmTopTit">
          <h2 class="pm-tit" id="gmTopTit">Las diez asignaciones más grandes del decreto</h2>
          <p class="pm-txt">El Anexo 1 del Presupuesto reparte el gasto ramo por ramo y entidad por entidad, en pesos. Estas son las diez cifras más altas %s.</p>
          <ol class="gm-top">%s</ol>
          <p class="pm-op">Ojo: estas cifras <b>no se suman</b> tal cual. El Ramo 19 (aportaciones a seguridad social) le transfiere dinero al IMSS y al ISSSTE, que aparecen otra vez con su propio presupuesto. Por eso el decreto resta un «neteo» al final: lo verás abajo.</p>
        </section>

        <section class="pm" aria-labelledby="gmRamTit">
          <h2 class="pm-tit" id="gmRamTit">Ramo por ramo: cuánto recibe cada uno</h2>
          <p class="pm-txt">Cinco grupos, como los ordena el decreto. Cada cifra es <b>oficial</b> %s; el porcentaje es el renglón ÷ el gasto neto total %s. Abre un grupo para ver sus ramos, de mayor a menor; el Congreso y el Poder Judicial abren también sus órganos.</p>
          <div class="gm-grupos">
            %s
          </div>
          <div class="gm-cuadre">
            <p><span>Suma de los cinco grupos</span><b class="num-tabular">%s</b></p>
            <p><span>Menos el neteo</span><b class="num-tabular">− %s</b></p>
            <p class="gm-cuadre-t"><span>Gasto neto total</span><b class="num-tabular">%s</b></p>
          </div>
          <p class="pm-op">%s La cuenta cierra al peso: %s − %s = %s %s.</p>
          <p class="pm-pie">Fuente: %s %s. Los montos están en pesos en el decreto; aquí se muestran en millones (mdp), con un decimal.</p>
        </section>
        <p class="pm-sigue">¿Cuánto de todo esto se puede mover de verdad? <a href="numeros-margen-del-presupuesto.html">🌡️ ¿Cuánto margen tiene el presupuesto? ➔</a></p>''' % (
        fin, ref('ref-cgpe2027'), ref('ref-pef2026'), chip('oficial'), mdp(tot), chip('derivado'),
        chip('oficial'), top_li,
        chip('oficial'), chip('derivado'), '\n            '.join(bloques),
        mdp(m(suma)), mdp(m(A['neteo'])), mdp(gnt),
        A['notaNeteo'], mdp(m(suma)), mdp(m(A['neteo'])), mdp(gnt), chip('derivado'),
        fuente, ref(A['refKey']))


# ---------------------------------------------------------------------------
# Lo que la cifra grande no dice
# ---------------------------------------------------------------------------
def ciegos(base, ref, glos):
    P = base['panoramaErario']
    ico = {'pc-deuda': '💳', 'pc-costofin': '📈', 'pc-margen': '🔒', 'pc-dependencia': '🗺️', 'pc-predial': '🏘️'}
    lleva = {'pc-margen': ('numeros-margen-del-presupuesto.html', '🌡️ El margen, en un termostato'),
             'pc-costofin': ('numeros-egreso-costo-financiero.html', '📈 El costo financiero, renglón por renglón'),
             'pc-deuda': ('numeros-cuentas-deuda-en-el-tiempo.html', '📈 La deuda en el tiempo'),
             'pc-dependencia': ('numeros-las-32-entidades.html', '🗺️ Las 32 entidades'),
             'pc-predial': ('numeros-los-municipios.html', '🏘️ Los 2,479 municipios')}
    tarjetas = []
    for i, pc in enumerate(P['puntosCiegos']):
        est = pc.get('estado')
        ch = chip(est, pc.get('pend')) if est else ''
        href, txt = lleva.get(pc['id'], (None, None))
        tarjetas.append(
            '<article class="pm-t gm-ciego"><span class="pm-t-ico" aria-hidden="true">%s</span>'
            '<p class="pm-et">Lectura %d de %d</p><p class="pm-t-v">%s %s</p><h3>%s</h3><p>%s%s</p>%s</article>'
            % (ico.get(pc['id'], '🔦'), i + 1, len(P['puntosCiegos']), pc['dato'], ch, pc['titulo'], pc['texto'],
               (' ' + ref(pc['ref'])) if pc.get('ref') else '',
               ('<a class="pm-mas-a" href="%s">%s ➔</a>' % (href, txt)) if href else ''))
    return '''<section class="pm" aria-labelledby="gmCieTit">
          <h2 class="pm-tit sr-only" id="gmCieTit">Las cinco lecturas</h2>
          <p class="pm-txt">El anuncio dice <b>%s</b>. Estas cinco lecturas no aparecen en él y cambian el sentido de la cifra. Cada una dice de dónde sale su dato y lleva a la página donde se ve completo.</p>
          <div class="pm-rej gm-ciegos">
            %s
          </div>
          <p class="pm-pie">Las cifras <b>derivadas</b> dicen su operación en el texto; la del predial está <b>pendiente</b>: toca su etiqueta para saber por qué.</p>
        </section>''' % (bill(P['totalPEF']), '\n            '.join(tarjetas))
