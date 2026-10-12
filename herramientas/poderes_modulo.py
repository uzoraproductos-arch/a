# -*- coding: utf-8 -*-
"""Lo que cuestan los Poderes, en pagina propia (pedido del autor,
12-10-2026): numeros-lo-que-cuestan-los-poderes.html.

Antes la pagina cargaba el auditor completo en un marco para abrir la
subpestana «poderes» del motor (renderPoderes en audit-engine.js). Ahora se
escribe aqui, con las mismas cifras de window.AUDIT_DB (coleccion poderes)
ya puestas en el HTML: se lee sin JavaScript y no carga el motor.

Es un traslado, no un rehecho: mismos siete capitulos, mismas cifras, mismos
chips y las mismas ligas a cada documento con su pagina. Los numeros se
escriben como los escribe el motor con toLocaleString('es-MX') (coma de
miles, punto decimal, redondeo a la mitad hacia arriba). Lo que cambia:

- «Tu parte» muestra la version sin personalizar (proporcion del gasto neto
  total, derivado): la pagina no tiene la calculadora. El boton que abria la
  2.4 es una liga a la Calculadora Cívica de Herramientas.
- Los bloques plegables del motor (panel lateral) son <details>.
- Los pendientes llevan su ficha del Registro de pendientes (data-pend).
- La lista de documentos lleva la llamada [nn] a fuentes-oficiales.html
  cuando el documento esta en las referencias.

Lo usa apartados.numeros_preparar(); recibe `ref(id)`, que pinta la
llamada [nn] a fuentes-oficiales.html, y `glos(termino, texto)`.
Estilos: assets/auditor/css/poderes.css. No necesita guion.
"""
from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR

# ---------------------------------------------------------------------------
# Formato de numeros: el mismo que el motor.
# ---------------------------------------------------------------------------


def _loc(x, d):
    """x.toLocaleString('es-MX', {min/max fraction digits: d}).

    Intl redondea el decimal mas corto que representa al double (repr en
    Python) a la mitad hacia arriba; la coma separa miles."""
    q = Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    if q == 0:
        q = abs(q)
    return format(q, ',.%df' % d)


def _fijo(x, d):
    """Number.prototype.toFixed(d): sobre el valor exacto del double."""
    q = Decimal(float(x)).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    if q == 0:
        q = abs(q)
    return format(q, '.%df' % d)


def esc(t):
    return (str('' if t is None else t).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def mdp(pesos, d=1):
    return '$' + _loc(pesos / 1e6, d) + ' mdp'


def pesos(p):
    n = int((Decimal(repr(float(p))) + Decimal('0.5')).to_integral_value(rounding=ROUND_FLOOR))
    return '$' + format(n, ',')


def pct(p, d=1):
    return _loc(p, d) + ' %'


def chip(e, pend=None):
    e = e if e in ('oficial', 'pendiente') else 'derivado'
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, (' data-pend="%s"' % pend) if pend else '', e)


# Cada documento de la coleccion y su referencia en fuentes-oficiales.html,
# cuando la hay. COG (distribucion por capitulo) no tiene ficha propia.
REF_DE = {
    'CP2025': 'ref-shcp-cp2025-datos', 'AV2T2026': 'ref-shcp-avance-2t2026', 'PEF': 'ref-pef2026',
    'UR': 'ref-pef-ramo03', 'SCJN_AGO': 'ref-scjn-ejercicio2026', 'SCJN_JUN': 'ref-scjn-trim2-2026',
    'SCJN_2025': 'ref-scjn-cierre2025', 'MANUAL': 'ref-manual-remun-pjf', 'OAJ_CAP': 'ref-oaj-trimestre2026',
    'OAJ_UEG': 'ref-oaj-trimestre2026', 'ASF_DIP': 'ref-asf-cp2024-diputados', 'ASF_SEN': 'ref-asf-cp2024-senado',
    'ASF_NL': 'ref-asf-cp2024-congreso-nl', 'ASF_TLX': 'ref-asf-cp2024-congreso-tlax', 'CNPLE': 'ref-inegi-cnple2025',
}

CALCULADORA = 'herramienta-calculadora.html'
COMPARA = 'herramienta-calculadora-compara.html'


def construir(base, ref, glos):
    P = base['poderes']
    F = P['fuentes']

    def fuente(clave, pagina=None):
        """pdFuente: documento y pagina, abre el PDF oficial."""
        f = F.get(clave)
        if not f:
            return '<span class="po-fuente">%s fuente por documentar</span>' % chip('pendiente')
        if pagina is None or pagina == '':
            pag = ''
        elif str(pagina).isdigit():
            pag = ', p. %s' % pagina
        else:
            pag = ', %s' % pagina
        return ('<a class="po-fuente" href="%s" target="_blank" rel="noopener noreferrer" title="%s">%s%s ↗</a>'
                % (esc(f['url']), esc(f['doc']), esc(f.get('corto') or f['doc']), esc(pag)))

    def barra(valor, maximo, clase=''):
        w = max(0.6, valor / maximo * 100) if maximo > 0 else 0
        return ('<span class="po-barra" aria-hidden="true"><span class="po-barra-v %s" style="width:%s%%"></span></span>'
                % (clase, _fijo(w, 2)))

    def plegable(titulo, cuerpo, extra=None, ico='📑'):
        return ('<details class="po-det"><summary><span class="po-det-ico" aria-hidden="true">%s</span>'
                '<span class="po-det-t">%s%s</span></summary><div class="po-det-cuerpo">%s</div></details>'
                % (ico, titulo, (' ' + extra) if extra else '', cuerpo))

    def tabla(cab_aria, html):
        return '<div class="po-tabla-w" role="region" aria-label="%s" tabindex="0">%s</div>' % (esc(cab_aria), html)

    def fila(nombre, valor_html, barra_html):
        return ('<div class="po-fila"><span class="po-fila-n">%s</span>%s<span class="po-fila-v">%s</span></div>'
                % (nombre, barra_html, valor_html))

    L = P['ramos2026']['legislativo']
    J = P['ramos2026']['judicial']
    total = P['gastoNetoTotal']['valor']

    # --- Las tarjetas del indice (pdCapitulos) ---
    nomina = todo = 0
    for c in P['judicial']['capitulosPorUR'].get('RAMO03', []):
        todo += c['aprobado']
        if c['cap'] == '1000':
            nomina += c['aprobado']
    tope = {'netoAnual': 0}
    for r in P.get('remuneraciones2026') or []:
        if r['netoAnual'] > tope['netoAnual']:
            tope = r
    gasto_cifra, gasto_pie = '', ''
    EJ = P.get('ejercicio')
    if EJ and EJ.get('avance2026'):
        leg = [u for u in EJ['avance2026']['unidades'] if u['ramo'] == '01']
        pag_leg = sum(u['pagado'] for u in leg)
        apr_leg = sum(u['modificado'] for u in leg)
        if apr_leg > 0:
            gasto_cifra, gasto_pie = pct(pag_leg / apr_leg * 100), 'del año pagado por el Congreso al 30 de junio'

    def pm(v):
        return '$' + _loc(v / total * 1000, 2)

    caps = [
        ('pd-tuparte', '🧾', 'Tu parte', pm(L['aprobado']) + ' y ' + pm(J['aprobado']), 'de cada $1,000 del gasto federal', 'derivado',
         'Cuánto de lo que pagas llega al Congreso y cuánto a la Judicatura.'),
        ('pd-poderes', '🏛️', 'Los dos Poderes en 2026', mdp(L['aprobado'] + J['aprobado']), 'aprobados entre ambos', 'derivado',
         'Lo que la Cámara aprobó a cada uno, y lo que le recortó al Poder Judicial.'),
        ('pd-gastado', '📊', 'Lo ya gastado', gasto_cifra, gasto_pie, 'derivado',
         'Lo que ejercieron en 2025 y lo que llevan pagado al 30 de junio de 2026.'),
        ('pd-judicial', '⚖️', 'Poder Judicial: en qué se va', pct(nomina / todo * 100) if todo else '', 'se va en servicios personales (nómina)', 'derivado',
         'Órgano por órgano y capítulo por capítulo, con lo ya ejercido.'),
        ('pd-congreso', '🔎', 'Congreso: lo que la ASF revisó', 'Cuenta Pública 2024', 'último año auditado', 'oficial',
         'Los resultados de la Auditoría en Diputados y Senado, y los 32 congresos locales.'),
        ('pd-sueldos', '💰', 'Cuánto ganan', pesos(tope['netoAnual']) if tope['netoAnual'] else '',
         ('neto al año: ' + tope['cargo']) if tope.get('cargo') else '', 'oficial',
         'Remuneraciones netas oficiales de 2026, y la comparación con tu ingreso.'),
        ('pd-documentos', '📂', 'Los documentos', '%d documentos' % len(F), 'oficiales, con liga y página', 'oficial',
         'De dónde sale cada cifra, para que lo compruebes.'),
    ]
    n_caps = len(caps)
    indice = ('<nav class="po-indice" id="poIndice" aria-label="Capítulos de esta página">'
              '<p class="po-indice-cab">%d capítulos · elige por dónde empezar, o léelos de corrido aquí abajo</p>'
              '<ol class="po-tarjetas">%s</ol></nav>') % (n_caps, ''.join(
                  '<li><a class="po-tarjeta" href="#%s">'
                  '<span class="po-t-num">%02d</span><span class="po-t-ico" aria-hidden="true">%s</span>'
                  '<span class="po-t-tit">%s</span>%s%s<span class="po-t-res">%s</span></a></li>' % (
                      cid, i + 1, ico, esc(tit),
                      ('<span class="po-t-cifra">%s</span>' % esc(cifra)) if cifra else '',
                      ('<span class="po-t-pie">%s %s</span>' % (esc(pie), chip(est))) if pie else '',
                      esc(res))
                  for i, (cid, ico, tit, cifra, pie, est, res) in enumerate(caps)))

    def capitulo(i, titulo, cuerpo):
        cid = caps[i][0]
        sig = ('<a class="po-nav-sig" href="#%s">Siguiente: %s →</a>' % (caps[i + 1][0], esc(caps[i + 1][2]))
               if i + 1 < n_caps else '')
        return ('<section class="po-cap" id="%s" aria-labelledby="%s-tit">'
                '<p class="po-cap-num"><span aria-hidden="true">%s</span> Capítulo %d de %d</p>'
                '<h2 class="po-tit" id="%s-tit">%s</h2>%s'
                '<nav class="po-nav" aria-label="Seguir leyendo"><a class="po-nav-arriba" href="#poIndice">↑ Volver al índice</a>%s</nav>'
                '</section>') % (cid, cid, caps[i][1], i + 1, n_caps, cid, titulo, cuerpo, sig)

    # --- 1. Tu parte (sin personalizar: la pagina no tiene la calculadora) ---
    partes = []
    for k in ('legislativo', 'judicial'):
        r = P['ramos2026'][k]
        partes.append({'k': k, 'nombre': r['nombre'], 'ramo': r['ramo'],
                       'proporcion': r['aprobado'] / total, 'porMil': r['aprobado'] / total * 1000})
    tu_parte = capitulo(0, 'Lo que a ti te toca pagar de cada Poder', (
        '<p class="po-lead">De cada <b>$1,000</b> del gasto federal aprobado para 2026, el Congreso de la Unión recibe <b>$%s</b> '
        'y el Poder Judicial de la Federación <b>$%s</b>. %s <span class="po-op">Aprobado del ramo ÷ gasto neto total (%s) × 1,000.</span></p>'
        '<div class="po-duo">%s</div>'
        '<p class="po-nota">¿Cuántos pesos tuyos son? Calcula tu %s anual en la calculadora y multiplícalo por estos porcentajes: '
        'es el mismo reparto que hace ella, solo con el ISR. Las cuotas de seguridad social no entran: tienen destino específico.</p>'
        '<p class="po-accion"><a class="po-btn" href="%s">🧮 Calcula tu ISR en la Calculadora Cívica ➔</a></p>') % (
        _fijo(partes[0]['porMil'], 2), _fijo(partes[1]['porMil'], 2), chip('derivado'), mdp(total, 0),
        ''.join('<div class="po-duo-c po-%s"><span class="po-k">%s %s · Ramo %s</span><b class="po-v">%s</b>'
                '<span class="po-s">del gasto neto total %s</span></div>' % (
                    p['k'], '🏛️' if p['k'] == 'legislativo' else '⚖️', esc(p['nombre']), p['ramo'],
                    pct(p['proporcion'] * 100, 2), chip('derivado')) for p in partes),
        glos('ISR (Impuesto Sobre la Renta)', 'ISR (impuesto sobre la renta)'), CALCULADORA))

    # --- 2. Los dos Poderes lado a lado ---
    max_u = max(u['aprobado'] for u in L['unidades'] + J['unidades'])

    def fila_u(u):
        return fila(esc(u['nombre']), mdp(u['aprobado']), barra(u['aprobado'], max_u))
    recorte = J['proyecto'] - J['aprobado']
    lado = capitulo(1, 'Los dos Poderes en el Presupuesto 2026', (
        '<p class="po-lead">Lo aprobado por la Cámara de Diputados en el Decreto publicado el 21 de noviembre de 2025. '
        '«Aprobado» es autorización de gasto: no es dinero ya pagado.</p>'
        '<div class="po-lado">'
        '<div class="po-lado-c"><div class="po-lado-cab"><span>🏛️ Poder Legislativo · Ramo 01</span><b>%s</b>%s</div>%s'
        '<p class="po-nota">La Cámara no le hizo cambios: el proyecto y lo aprobado son iguales. %s</p></div>'
        '<div class="po-lado-c"><div class="po-lado-cab"><span>⚖️ Poder Judicial · Ramo 03</span><b>%s</b>%s</div>%s'
        '<p class="po-nota">Se pidieron %s y se aprobaron %s: <b>%s menos</b> %s, casi todo al Órgano de Administración Judicial. '
        'Es una diferencia entre proyecto y aprobado, no un ahorro comprobado. %s</p></div>'
        '</div>') % (
        mdp(L['aprobado']), chip('oficial'), ''.join(fila_u(u) for u in L['unidades']), fuente('PEF', 'Anexos 1 y 32, DOF pp. 32 y 108'),
        mdp(J['aprobado']), chip('oficial'), ''.join(fila_u(u) for u in J['unidades']),
        mdp(J['proyecto']), mdp(J['aprobado']), mdp(recorte), chip('derivado'), fuente('PEF', 'Anexo 32, DOF p. 108')))

    # --- 3. Lo ya gastado: cierre 2025 y avance 2026, de Hacienda ---
    gastado = ''
    if EJ and EJ.get('cp2025') and EJ.get('avance2026'):
        cp, av = EJ['cp2025']['unidades'], EJ['avance2026']['unidades']

        def busca(lista, ramo, ur):
            return next((u for u in lista if u['ramo'] == ramo and u['ur'] == ur), None)
        orden = {'01': ['100', '200', '101'], '03': ['100', '120', '110', '300', '210', '211']}

        def fila_g(ramo, ur):
            a, b = busca(cp, ramo, ur), busca(av, ramo, ur)
            nombre = (a or b)['nombre']
            # Sin variacion para quien nacio o desaparecio a media ano: es
            # un cambio de estructura, no un sobre o subejercicio.
            var = (a['ejercido'] / a['original'] - 1) * 100 if a and b and a['original'] > 0 else None
            avp = b['pagado'] / b['modificado'] * 100 if b and b['modificado'] > 0 else None
            c_orig = (mdp(a['original']) if a['original'] > 0 else '<small>creado en 2025</small>') if a else '—'
            c_ej = (mdp(a['ejercido']) if a else '—') + (
                (' <small class="po-var %s">%s%s</small>' % ('po-var-sube' if var > 0 else 'po-var-baja', '+' if var > 0 else '', pct(var)))
                if var is not None else '')
            c_apr = (mdp(b['aprobado']) + (('<br><small>modificado: %s</small>' % mdp(b['modificado']))
                                           if abs(b['modificado'] - b['aprobado']) > 1 else '')) if b else '—'
            c_pag = mdp(b['pagado']) if b else '—'
            c_av = (('<span class="po-avance"><span class="po-avance-v" style="width:%s%%"></span>'
                     '<span class="po-avance-mitad" title="Mitad del año"></span></span><span class="po-num">%s</span>')
                    % (_fijo(min(100, avp), 1), pct(avp))) if avp is not None else '<small>dejó de operar en 2025</small>'
            return ('<tr><td>%s</td><td class="po-num">%s</td><td class="po-num">%s</td><td class="po-num">%s</td>'
                    '<td class="po-num">%s</td><td><div class="po-avance-c">%s</div></td></tr>') % (
                esc(nombre), c_orig, c_ej, c_apr, c_pag, c_av)

        def tabla_g(ramo, titulo):
            filas = ''.join(fila_g(ramo, ur) for ur in orden[ramo] if busca(cp, ramo, ur) or busca(av, ramo, ur))
            return tabla(titulo, (
                '<table class="po-tabla po-tabla-gasto"><thead>'
                '<tr><th rowspan="2" scope="col">%s</th><th colspan="2" scope="colgroup">2025 · Cuenta Pública</th><th colspan="3" scope="colgroup">2026 · al 30 de junio</th></tr>'
                '<tr><th scope="col">Original</th><th scope="col">Ejercido</th><th scope="col">Aprobado</th><th scope="col">Pagado</th><th scope="col">Avance (pagado ÷ modificado)</th></tr>'
                '</thead><tbody>%s</tbody></table>') % (titulo, filas))

        leg_orig = sum(u['original'] for u in cp if u['ramo'] == '01')
        leg_ej = sum(u['ejercido'] for u in cp if u['ramo'] == '01')
        asf_cp, asf_av = busca(cp, '01', '101'), busca(av, '01', '101')
        caps_leg = EJ['cp2025'].get('capitulosLegislativo') or {}
        cap_filas = ''
        for ur in ('100', '200'):
            if not caps_leg.get(ur):
                continue
            u = busca(cp, '01', ur)
            tot = sum(c['ejercido'] for c in caps_leg[ur])
            cap_filas += '<p class="po-pila-cab">%s · %s ejercidos en 2025</p>' % (esc(u['nombre']), mdp(tot)) + ''.join(
                fila(esc(c['cap'] + ' · ' + c['concepto']), mdp(c['ejercido']) + ' · ' + pct(c['ejercido'] / tot * 100),
                     barra(c['ejercido'], tot, 'po-v-leg')) for c in caps_leg[ur])
        gastado = capitulo(2, 'Lo ya gastado: el cierre de 2025 y lo que va de 2026', (
            '<p class="po-lead">El presupuesto aprobado es un permiso para gastar. Lo que de verdad salió está en dos documentos de Hacienda: '
            'la <b>%s 2025</b>, que cierra el año pasado, y el <b>avance del gasto al 30 de junio de 2026</b>. '
            'A mitad del año, lo esperable ronda la mitad; la marca de cada barra señala ese punto.</p>'
            '%s'
            '<p class="po-nota">En 2025 el Congreso tenía %s aprobados y ejerció %s (%s%s) %s%s</p>'
            '%s'
            '<p class="po-nota">En 2025 conviven el Consejo de la Judicatura Federal, que operó hasta el cambio de estructura de ese año, '
            'y los dos órganos que lo sustituyeron: el Órgano de Administración Judicial y el Tribunal de Disciplina Judicial. '
            'Por eso estos dos aparecen con original en cero.</p>'
            '%s'
            '<p class="po-nota">%s Montos: %s y %s. Variaciones y avance: %s (ejercido ÷ original − 1; pagado ÷ presupuesto modificado). %s</p>') % (
            glos('Cuenta Pública', 'Cuenta Pública'),
            tabla_g('01', '🏛️ Poder Legislativo'),
            mdp(leg_orig), mdp(leg_ej), '+' if leg_ej >= leg_orig else '', pct((leg_ej / leg_orig - 1) * 100), chip('derivado'),
            ('. La Auditoría Superior es la que más creció respecto de lo aprobado: %s a %s en 2025, y en 2026 su presupuesto ya se amplió a %s.'
             % (mdp(asf_cp['original']), mdp(asf_cp['ejercido']), mdp(asf_av['modificado']))) if asf_cp and asf_av else '.',
            tabla_g('03', '⚖️ Poder Judicial'),
            plegable('En qué gastaron las cámaras en 2025, capítulo por capítulo', cap_filas, None, '🏛️') if cap_filas else '',
            chip('oficial'), fuente('CP2025', 'base de datos'), fuente('AV2T2026', 'base de datos'), chip('derivado'), esc(EJ['nota'])))

    # --- 4. Poder Judicial: en que se gasta ---
    nombres_ur = [('100', 'Suprema Corte'), ('120', 'Órgano de Administración Judicial'), ('210', 'TEPJF · Sala Superior'),
                  ('211', 'TEPJF · Salas Regionales'), ('300', 'Tribunal de Disciplina Judicial')]
    caps_orden = ['1000', '2000', '3000', '4000', '5000', '6000']
    caps_nombre = {'1000': 'Personal', '2000': 'Materiales', '3000': 'Servicios generales', '4000': 'Transferencias',
                   '5000': 'Bienes muebles e inmuebles', '6000': 'Obra pública'}
    cap_ur = P['judicial']['capitulosPorUR']
    pilas = ''
    for ur, nom in nombres_ur:
        cs = cap_ur.get(ur) or []
        tot = sum(c['aprobado'] for c in cs)
        personal = next((c['aprobado'] for c in cs if c['cap'] == '1000'), 0)
        segs = ''
        for cp_ in caps_orden:
            c = next((x for x in cs if x['cap'] == cp_), None)
            if c:
                segs += '<span class="po-cap-%s" style="width:%s%%" title="%s: %s"></span>' % (
                    cp_, _fijo(c['aprobado'] / tot * 100, 3), caps_nombre[cp_], mdp(c['aprobado']))
        pilas += ('<div class="po-pila"><p class="po-pila-cab"><span>%s</span><span>%s · %s en personal</span></p>'
                  '<div class="po-pila-barra" role="img" aria-label="%s: %s">%s</div></div>') % (
            esc(nom), mdp(tot), pct(personal / tot * 100), esc(nom),
            ', '.join('%s %s' % (caps_nombre[c['cap']], pct(c['aprobado'] / tot * 100)) for c in cs), segs)
    leyenda = '<ul class="po-leyenda">%s</ul>' % ''.join(
        '<li><i class="po-cap-%s" aria-hidden="true"></i>%s %s</li>' % (cp_, cp_, caps_nombre[cp_]) for cp_ in caps_orden)

    ag = P['judicial']['scjnAgosto']
    bar_ag = [('ejercido', ag['ejercido'], 'Ejercido'), ('compromiso', ag['compromiso'], 'Comprometido'), ('disponible', ag['disponible'], 'Disponible')]
    scjn = ('<div class="po-sub"><h3 class="po-sub-t">La Suprema Corte, al 31 de agosto de 2026</h3>'
            '<div class="po-pila-barra po-ejec" role="img" aria-label="Ejercido %s, comprometido %s, disponible %s">%s</div>'
            '%s<p class="po-nota">%s Porcentajes sobre el modificado %s. %s</p></div>') % (
        pct(ag['ejercido'] / ag['modificado'] * 100), pct(ag['compromiso'] / ag['modificado'] * 100), pct(ag['disponible'] / ag['modificado'] * 100),
        ''.join('<span class="po-ej-%s" style="width:%s%%"></span>' % (k, _fijo(v / ag['modificado'] * 100, 3)) for k, v, _ in bar_ag),
        tabla('La Suprema Corte, al 31 de agosto de 2026', '<table class="po-tabla"><tbody>'
              '<tr><th scope="row">Presupuesto original</th><td>%s</td><td>%s</td></tr>'
              '<tr><th scope="row">Modificado</th><td>%s</td><td>%s</td></tr>%s</tbody></table>' % (
                  mdp(ag['original']), chip('oficial'), mdp(ag['modificado']), chip('oficial'),
                  ''.join('<tr><th scope="row"><i class="po-ej-%s" aria-hidden="true"></i>%s</th><td>%s <small>(%s)</small></td><td>%s</td></tr>' % (
                      k, nom, mdp(v), pct(v / ag['modificado'] * 100), chip('oficial')) for k, v, nom in bar_ag))),
        esc(ag['nota']), chip('derivado'), fuente('SCJN_AGO', ag['pagina']))

    oaj = P['judicial']['oajCapitulos']
    oaj_t = ('<div class="po-sub"><h3 class="po-sub-t">El Órgano de Administración Judicial, abril a junio de 2026</h3>%s'
             '<p class="po-nota">%s %s %s · %s</p></div>') % (
        tabla('El Órgano de Administración Judicial, abril a junio de 2026',
              '<table class="po-tabla"><thead><tr><th scope="col">Capítulo</th><th scope="col">Anual (SHCP)</th><th scope="col">Asignado en el trimestre</th>'
              '<th scope="col">Pagado en el trimestre</th></tr></thead><tbody>%s</tbody></table>' % ''.join(
                  '<tr><th scope="row">%s %s</th><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                      c['cap'], esc(c['concepto']), mdp(c['anualShcp']) if c.get('anualShcp') else '—', mdp(c['asignadoTrim']), mdp(c['pagadoTrim']))
                  for c in oaj if c.get('anualShcp') or c.get('pagadoTrim'))),
        chip('oficial'), esc(P['judicial']['oajNota']), fuente('OAJ_CAP'), fuente('COG', 'pp. 3–8'))

    circ = sorted(P['judicial']['circuitos'], key=lambda c: -c['pagado'])
    max_c = circ[0]['pagado'] if circ else 0

    def sede(c):
        s = str(c['sede']).split(' / ')[0]
        i = s.find('Circuito Judicial ')
        return s[i + len('Circuito Judicial '):] if i >= 0 else s
    circ_t = plegable('Los 32 circuitos judiciales: pagos registrados de abril a junio',
                      '<p class="po-nota"><b>No es el costo de cada circuito.</b> %s</p>%s'
                      '<p class="po-nota">Suma de las unidades ejecutoras de cada circuito. %s</p>' % (
                          esc(P['judicial']['circuitosNota']),
                          ''.join(fila('%s. %s' % (c['n'], esc(sede(c))), pesos(c['pagado']), barra(c['pagado'], max_c, 'po-v-jud')) for c in circ),
                          fuente('OAJ_UEG')), chip('derivado'), '⚖️')

    pend_j = ' · '.join('%s %s' % (chip('pendiente', 'poderes-judicial-%d' % i), esc(t)) for i, t in enumerate(P['judicial']['pendientes']))
    judicial = capitulo(3, '⚖️ Poder Judicial: en qué se va el dinero', (
        '<p class="po-lead">Presupuesto aprobado 2026 de cada órgano, por %s. Casi todo es nómina: jueces, magistrados y el personal que '
        'opera los juzgados en todo el país.</p>%s%s'
        '<p class="po-nota">%s montos; %s porcentajes. %s</p>%s%s%s'
        '<p class="po-nota">%s. No se calculan dividiendo el presupuesto entre el número de personas: el dinero paga estructuras, no sólo cargos.</p>') % (
        glos('Capítulo de Gasto', 'capítulo de gasto'), pilas, leyenda, chip('oficial'), chip('derivado'), fuente('COG', 'pp. 3–8'),
        scjn, oaj_t, circ_t, pend_j))

    # --- 5. Poder Legislativo: lo que la ASF ya audito ---
    E = P['legislativo']['ejercicio2024']

    def fila_ej(inst, concepto):
        x = next((x for x in E if x['institucion'] == inst and x['concepto'].startswith(concepto)), None)
        if not x:
            return ''
        return '<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            esc(x['concepto']), mdp(x['pesos']), chip(x['estado']), fuente(x['fuente'], x['pagina']))
    res_asf = ''.join('<li><b>%s:</b> %s %s %s</li>' % (esc(r['institucion']), esc(r['texto']), chip(r['estado']), fuente(r['fuente'], r['pagina']))
                      for r in P['legislativo']['resultadosAsf'])

    pers = sorted(P['legislativo']['personalDiputados2024'], key=lambda x: -x['pesos'])
    tot_pers = sum(x['pesos'] for x in pers)
    pers_t = plegable('Cámara de Diputados 2024: gasto de personal por partida',
                      '<p class="po-nota"><b>Es el personal de toda la institución</b>, no sólo el de las 500 diputaciones. Total: %s %s.</p>%s'
                      '<p class="po-nota">%s %s</p>' % (
                          mdp(tot_pers), chip('derivado'),
                          ''.join(fila('%s %s' % (x['partida'], esc(x['concepto'])), mdp(x['pesos']), barra(x['pesos'], pers[0]['pesos'], 'po-v-leg')) for x in pers),
                          chip('oficial'), fuente('ASF_DIP', 5)), None, '🏛️')

    sc = P['legislativo']['senadoCapitulos2024']
    sen_t = plegable('Cámara de Senadores 2024: devengado y pagado por capítulo', '%s<p class="po-nota">%s Lo devengado y no pagado al cierre se pagó en 2025. %s</p>' % (
        tabla('Cámara de Senadores 2024: devengado y pagado por capítulo',
              '<table class="po-tabla"><thead><tr><th scope="col">Capítulo</th><th scope="col">Devengado</th><th scope="col">Pagado al 31 de diciembre</th></tr></thead><tbody>%s</tbody></table>' % ''.join(
                  '<tr><th scope="row">%s %s</th><td>%s</td><td>%s</td></tr>' % (c['cap'], esc(c['concepto']), mdp(c['devengado']), mdp(c['pagado'])) for c in sc)),
        chip('oficial'), fuente('ASF_SEN', 5)), None, '🏛️')

    cg = sorted(P['legislativo']['congresos2024'], key=lambda x: -x['ejercidoMdp'])
    tot_cg = sum(x['ejercidoMdp'] for x in cg)
    pend_l = ' · '.join('%s %s' % (chip('pendiente', 'poderes-legislativo-%d' % i), esc(t)) for i, t in enumerate(P['legislativo']['pendientes']))
    cg_t = plegable('Los 32 congresos locales: gasto ejercido en 2024', '%s<p class="po-nota">%s cada congreso; %s la suma de las 32 filas, %s. Millones de pesos corrientes. %s</p>'
                    '<p class="po-nota">%s.</p>' % (
                        ''.join(fila(esc(x['entidad']), mdp(x['ejercidoMdp'] * 1e6), barra(x['ejercidoMdp'], cg[0]['ejercidoMdp'], 'po-v-leg')) for x in cg),
                        chip('oficial'), chip('derivado'), mdp(tot_cg * 1e6), fuente('CNPLE', 11), pend_l), None, '🏛️')

    ac = P['legislativo']['asfCongresos2024']
    ac_t = plegable('Dos congresos locales auditados por la ASF', '%s<p class="po-nota">%s Un monto «por aclarar» es un saldo sujeto a seguimiento: no equivale a daño definitivo.</p>' % (
        tabla('Dos congresos locales auditados por la ASF',
              '<table class="po-tabla"><thead><tr><th scope="col">Congreso</th><th scope="col">Concepto</th><th scope="col">Importe</th><th scope="col">Fuente</th></tr></thead><tbody>%s</tbody></table>' % ''.join(
                  '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(x['congreso']), esc(x['concepto']), pesos(x['pesos']), fuente(x['fuente'], x['pagina'])) for x in ac)),
        chip('oficial')), None, '🔍')

    legislativo = capitulo(4, '🏛️ Poder Legislativo: lo que la Auditoría ya revisó', (
        '<p class="po-lead">Lo gastado en 2025 y en lo que va de 2026 está en el capítulo <a class="po-enlace" href="#pd-gastado">«Lo ya gastado»</a>. '
        'Aquí va lo <b>auditado</b>, y el año más reciente con auditoría terminada es 2024: la %s ya publicó sus informes de la revisión de la Cuenta Pública 2024.</p>'
        '%s<ul class="po-lista">%s</ul>%s%s%s%s') % (
        glos('Auditoría Superior de la Federación (ASF)', 'Auditoría Superior de la Federación'),
        tabla('Lo que la Auditoría revisó en las dos cámaras, 2024',
              '<table class="po-tabla po-tabla-asf"><thead><tr><th colspan="4" scope="colgroup">Cámara de Diputados · 2024</th></tr></thead><tbody>%s</tbody>'
              '<thead><tr><th colspan="4" scope="colgroup">Cámara de Senadores · 2024</th></tr></thead><tbody>%s</tbody></table>' % (
                  fila_ej('Diputados', 'Aprobado') + fila_ej('Diputados', 'Modificado') + fila_ej('Diputados', 'Pagado') + fila_ej('Diputados', 'Muestra'),
                  fila_ej('Senado', 'Aprobado') + fila_ej('Senado', 'Modificado') + fila_ej('Senado', 'Pagado al 31') + fila_ej('Senado', 'Pendiente de pago') + fila_ej('Senado', 'Muestra'))),
        res_asf, pers_t, sen_t, cg_t, ac_t))

    # --- 6. Remuneraciones ---
    R = P['remuneraciones2026']
    max_r = max(r['netoAnual'] for r in R)
    fuentes_r = '<br>'.join('<b>%s:</b> %s%s' % (
        esc(r['cargo']), fuente(r['fuente'], r['pagina']),
        (' — ' + esc(r['nota']) + ((' ' + chip('derivado') + ' ' + esc(r['netoAnualOperacion']) + '.') if r.get('netoAnualOperacion') else ''))
        if r.get('parcial') else '') for r in R)
    rem = capitulo(5, 'Cuánto ganan, en neto y al año', (
        '<p class="po-lead">La remuneración total anual neta que publica el propio Presupuesto: lo que llega a la persona después de impuestos. '
        'Es la única medida comparable entre cargos.</p>%s<p class="po-nota">%s</p>'
        '<p class="po-accion"><a class="po-btn" href="%s">⚔️ Compáralo con tu ingreso: Tú contra ellos ➔</a></p>') % (
        ''.join(fila('%s %s%s' % (r['icono'], esc(r['cargo']), ' <small>(parcial)</small>' if r.get('parcial') else ''),
                     '%s %s' % (pesos(r['netoAnual']), chip(r.get('netoAnualEstado') or r['estado'])),
                     barra(r['netoAnual'], max_r, 'po-v-jud' if r['id'] == 'ministro' else 'po-v-leg')) for r in R),
        fuentes_r, COMPARA))

    # --- 7. Documentos ---
    def ref_doc(k):
        rid = REF_DE.get(k)
        if not rid:
            return ''
        try:
            return ' ' + ref(rid)
        except KeyError:
            return ''
    docs = capitulo(6, 'Los documentos de esta sección', (
        '<p class="po-lead">Todos son documentos públicos oficiales. Consulta del %s. Si una liga deja de funcionar, la huella SHA-256 permite '
        'comprobar que un archivo es el mismo que se usó aquí.</p><ol class="po-docs">%s</ol><p class="po-nota">%s</p>') % (
        esc(P['consulta']),
        ''.join('<li><a class="po-doc" href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>%s%s</li>' % (
            esc(f['url']), esc(f['doc']), ('<code title="SHA-256">%s…</code>' % f['sha256'][:16]) if f.get('sha256') else '', ref_doc(k))
            for k, f in F.items()),
        esc(P['nota'])))

    return '<div class="po" id="poRaiz">\n        %s\n        %s\n      </div>' % (
        indice, '\n        '.join([tu_parte, lado, gastado, judicial, legislativo, rem, docs]))
