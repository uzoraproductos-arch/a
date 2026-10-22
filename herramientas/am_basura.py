# -*- coding: utf-8 -*-
"""Costo Ambiental, aplicacion 3: «Basura y proteccion» en pagina propia
(16-10-2026). Sustituye al marco que cargaba la portada entera
(index.html?ir=ambiente&ancla=eb-ambasura&visor=1).

Lo que pintaba el motor en #ambienteRaiz (renderCostoAmbiental de
audit-engine.js, en modo «en bloques»: basura, proteccion, megaobras,
leyes y quien lo mide) se conserva entero, con las mismas colecciones
(ambiente y cuentas_ecologicas) y las mismas operaciones. Se agrega:
el camino de la basura de un dia paso por paso, un «¿Cuanto crees?», la
calculadora de la basura de tu casa, la serie 2010-2022 que se toca, la
balanza con su calculadora, el presupuesto por organo con cinco medidas y
CSV, las megaobras de construccion con su ficha en «Sector e industria», y
filtros en las leyes y en quien lo mide.

Correcciones editoriales frente al motor: los porcentajes calculados
(avance del pago, cambio 2027 contra 2026, peso de la Conagua) llevan su
chip «derivado» con la operacion; la proporcion daño/proteccion se dice
como division; los pendientes llevan data-pend a su ficha del Registro
(ambiente-0, -1, -2; obra-<id>).

Lo llama apartados.insp_nativa() (INSP_NATIVAS['ambasura']).
"""
import html
import json

from presupuesto_modulos import chip

ESTILOS = ['am-basura.css']
SCRIPTS = ['am-basura.js']

# Las megaobras que son obra de construccion (tienen o debieron tener una
# Manifestacion de Impacto Ambiental). Quedan fuera los rescates
# financieros, las compras de empresas y los programas.
OBRAS_FISICAS = ['tren-maya', 'dos-bocas', 'aifa-texcoco', 'tren-toluca', 'refineria-tula',
                 'megafarmacia', 'estela-luz', 'bunker-garcia-luna']


def esc(t):
    return html.escape(str(t if t is not None else ''), quote=True)


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def num(v, dec=0):
    """amNum() del motor: miles con coma y decimales fijos."""
    return format(v, ',.%df' % dec)


def pmdp(pesos, dec=1):
    """pdMdp() del motor: pesos -> millones con un decimal."""
    return '$' + format(pesos / 1e6, ',.%df' % dec) + ' mdp'


def pct(p, dec=1):
    return format(p, ',.%df' % dec) + ' %'


def construir(base, ref):
    A = base['ambiente']
    C = base['cuentas_ecologicas']
    R, P = A['residuos'], A['presupuesto']
    F = A['fuentes']
    refs = {r['id']: r for r in base.get('referencias_legales', [])}
    pend_ids = ['ambiente-%d' % i for i in range(len(A.get('pendientes', [])))]

    def fuente(clave, pagina=None):
        f = F.get(clave)
        if not f:
            return chip('pendiente') + ' fuente por documentar'
        pag = ''
        if pagina not in (None, ''):
            pag = (', p. %s' % pagina) if str(pagina).isdigit() else ', ' + str(pagina)
        return ('<a class="ab-fu" href="%s" target="_blank" rel="noopener noreferrer" title="%s">%s%s ↗</a>'
                % (esc(f['url']), esc(f['doc']), esc(f.get('corto') or f['doc']), esc(pag)))

    def liga_ref(rid, texto):
        r = refs.get(rid)
        if not r:
            return chip('pendiente') + ' ' + esc(texto)
        return ('<a class="ab-fu" href="%s" target="_blank" rel="noopener noreferrer" title="%s">%s ↗</a>'
                % (esc(r['url']), esc(r['cita_apa']), esc(texto)))

    ceem = liga_ref('ref-ceem-2024', 'INEGI, Cuentas Económicas y Ecológicas 2024')

    def tarjeta(valor, rotulo, estado, pie='', pend=None, cls=''):
        return ('<div class="ab-dato%s"><strong class="ab-num">%s</strong><span class="ab-dato-r">%s %s</span>%s</div>'
                % (cls, valor, rotulo, chip(estado, pend), ('<small>%s</small>' % pie) if pie else ''))

    # ------------------------------------------------------------------
    # 1. La basura
    gen = R['generacionTdia']['valor']
    rec = R['recolectadaTdia']
    sit = R['sitiosDisposicion']
    rel = R['rellenosSanitarios']
    sep = R['separadaTdia']
    msr = R['municipiosSinRecoleccion']
    veh = R['vehiculos']
    per = R['perCapitaKg']['valor']
    no_rec = gen - rec['valor']
    no_ctrl_t = sit['tdia'] - rel['tdia']
    no_ctrl_n = sit['valor'] - rel['valor']
    residuos_cee = next((x for x in C['degradacion'].get('componentes', []) if x['id'] == 'residuos'), None)

    pasos = [
        ('🏠', 'Se genera', gen, 'oficial',
         'Toda la basura que producen hogares, comercios y servicios en un día.',
         fuente('DBGIR', R['generacionTdia']['pagina'])),
        ('🚛', 'Se recolecta', rec['valor'], 'oficial',
         'El %s de lo generado. No se recolectan %s t al día (%s − %s, %s).'
         % (pct(rec['pct']), num(no_rec), num(gen), num(rec['valor']), chip('derivado')),
         fuente('DBGIR', rec['pagina'])),
        ('🏚️', 'Llega a un sitio de disposición final', sit['tdia'], 'oficial',
         'A alguno de los %s sitios de disposición final del país.' % num(sit['valor']),
         fuente('DBGIR', sit['pagina'])),
        ('✅', 'Llega a un relleno sanitario', rel['tdia'], 'oficial',
         'A uno de los %d rellenos sanitarios: el %s de lo que llega a disposición final. Las otras %s t al día van a %s sitios '
         'clasificados como no controlados (%s − %s t y %s − %d sitios, %s).'
         % (rel['valor'], pct(rel['pct']), num(no_ctrl_t, 1), num(no_ctrl_n), num(sit['tdia']), num(rel['tdia'], 1),
            num(sit['valor']), rel['valor'], chip('derivado')),
         fuente('DBGIR', rel['pagina'])),
    ]
    camino = []
    for i, (ico, tit, t, e, txt, fu) in enumerate(pasos):
        camino.append(
            '<li class="ab-paso" data-paso="%d">'
            '<div class="ab-paso-cab"><span class="ab-paso-ico" aria-hidden="true">%s</span>'
            '<div><p class="ab-paso-tit">%s</p><p class="ab-paso-t"><b class="ab-num">%s t</b> al día %s</p></div></div>'
            '<div class="ab-riel" aria-hidden="true"><span class="ab-riel-b" style="--ab-w:%.4f"></span></div>'
            '<p class="ab-paso-tx">%s <span class="ab-paso-fu">%s</span></p>'
            '%s</li>'
            % (i, ico, esc(tit), num(t, 1 if t != int(t) else 0), chip(e), t / gen, txt, fu,
               ('<p class="ab-paso-pct">%s del total generado %s</p>' % (pct(t / gen * 100), chip('derivado'))) if i else
               '<p class="ab-paso-pct">El punto de partida: todo lo que se genera.</p>'))

    serie = R['recolectadaSerie']
    smax = max(serie['tdia'])
    barras = []
    for i, (a, v) in enumerate(zip(serie['anios'], serie['tdia'])):
        barras.append('<li><button type="button" class="ab-s-b%s" data-i="%d" aria-pressed="%s" aria-label="%d: %s toneladas al día">'
                      '<span class="ab-s-riel"><span class="ab-s-barra" style="--ab-h:%.4f"></span></span>'
                      '<span class="ab-s-a">%d</span></button></li>'
                      % (' ab-act' if i == len(serie['anios']) - 1 else '', i, 'true' if i == len(serie['anios']) - 1 else 'false',
                         a, num(v), v / smax, a))

    datos_basura = (
        tarjeta(num(gen) + ' t', 'de basura al día en el país', 'oficial', fuente('DBGIR', R['generacionTdia']['pagina'])) +
        tarjeta(pct(rec['pct']), 'se recolecta (%s t/día)' % num(rec['valor']), 'oficial', fuente('DBGIR', rec['pagina'])) +
        tarjeta(pct(rel['pct']), 'llega a uno de los %d rellenos sanitarios' % rel['valor'], 'oficial', fuente('DBGIR', rel['pagina'])) +
        tarjeta(pct(sep['pct']), 'se recolecta separada', 'oficial', fuente('DBGIR', sep['pagina'])) +
        tarjeta(str(msr['valor']), 'municipios sin servicio de recolección', 'oficial',
                '%d de ellos en Oaxaca · %s' % (msr['oaxaca'], fuente('DBGIR', msr['pagina']))) +
        (tarjeta(pmdp(residuos_cee['monto_mdp'] * 1e6), 'costo anual del daño por basura mal gestionada (2024)',
                 residuos_cee.get('estado', 'oficial'), ceem, cls=' ab-dato-rojo') if residuos_cee else ''))

    basura = '''
  <section class="ab-bloque" id="abBasura" aria-labelledby="abBasTit">
    <h2 class="ab-tit" id="abBasTit"><span aria-hidden="true">🗑️</span> La basura: un servicio municipal sin dinero federal</h2>
    <p class="ab-txt">Recoger, trasladar, tratar y disponer la basura es obligación del municipio (artículo 115 constitucional). El diagnóstico nacional de la SEMARNAT, publicado en abril de 2026, retrata cómo se cumple.</p>

    <div class="ab-adivina" id="abAdivina">
      <p class="ab-adivina-k"><span aria-hidden="true">🤔</span> ¿Cuánto crees?</p>
      <p class="ab-adivina-p">De cada 100 kilos de basura que llegan a un sitio de disposición final, ¿cuántos llegan a un <b>relleno sanitario</b>, el único sitio controlado por la norma?</p>
      <label class="ab-adivina-l" for="abAdivinaR"><span>Tu respuesta: <b id="abAdivinaV">50</b> kilos de cada 100</span>
        <input type="range" id="abAdivinaR" min="0" max="100" step="1" value="50" class="ab-rango"></label>
      <button type="button" class="ab-boton" id="abAdivinaB"><span aria-hidden="true">👀</span> Ver la respuesta</button>
      <p class="ab-adivina-res" id="abAdivinaRes" aria-live="polite" hidden></p>
    </div>

    <h3 class="ab-sub">El camino de la basura de un día</h3>
    <p class="ab-txt">Sigue las toneladas desde que salen de las casas hasta donde terminan. Cada barra mide lo que queda frente a lo que se generó.</p>
    <p class="ab-acciones"><button type="button" class="ab-boton" id="abCaminoB"><span aria-hidden="true">▶️</span> Seguir la basura paso por paso</button>
      <button type="button" class="ab-boton ab-sec" id="abCaminoT">Ver todo de una vez</button></p>
    <ol class="ab-camino" id="abCamino">
      %(camino)s
    </ol>
    <p class="ab-nota">Barras y porcentajes del total: %(chip_d)s cada cifra ÷ %(gen)s t generadas al día × 100.</p>

    <div class="ab-datos">%(datos)s</div>
    <div class="ab-alerta">%(chip_o)s <b>Sin partida federal.</b> %(sinpart)s %(sinpart_fu)s</div>
    <p class="ab-nota">%(rel_nota)s Hay %(sitios)s sitios de disposición final; %(veh)s camiones recolectores, de los cuales el %(veh_pct)s %% son anteriores a 2002. %(chip_o)s %(veh_fu)s</p>

    <div class="ab-casa" id="abCasa">
      <h3 class="ab-sub"><span aria-hidden="true">🏠</span> La basura de tu casa, al promedio nacional</h3>
      <p class="ab-txt">Cada persona genera en promedio <b>%(per)s kg</b> de basura al día %(chip_o)s %(per_fu)s. Dinos cuántos viven contigo y elige el periodo.</p>
      <div class="ab-casa-ctl">
        <div class="ab-paso-n" role="group" aria-label="Personas en tu casa">
          <button type="button" class="ab-boton ab-sec ab-mm" id="abMenos" aria-label="Una persona menos">−</button>
          <output class="ab-casa-n" id="abPersonas" aria-live="polite">3</output>
          <button type="button" class="ab-boton ab-sec ab-mm" id="abMas" aria-label="Una persona más">+</button>
          <span class="ab-casa-nl" id="abPersonasL">personas</span>
        </div>
        <div class="ab-grupo" role="group" aria-label="Periodo">
          <button type="button" class="ab-op" data-dias="1" aria-pressed="false">Un día</button>
          <button type="button" class="ab-op" data-dias="7" aria-pressed="false">Una semana</button>
          <button type="button" class="ab-op" data-dias="30" aria-pressed="false">30 días</button>
          <button type="button" class="ab-op" data-dias="365" aria-pressed="true">Un año</button>
        </div>
      </div>
      <div class="ab-casa-res" id="abCasaRes" aria-live="polite"></div>
      <p class="ab-nota">%(chip_d)s Personas × %(per)s kg × días. Si tu basura siguiera el promedio nacional, el %(norec_pct)s no se recolectaría (100 − %(rec_pct)s, %(chip_d)s). Es un promedio del país: tu municipio puede estar mejor o peor.</p>
    </div>

    <div class="ab-serie" id="abSerie">
      <h3 class="ab-sub">Basura recolectada al día, %(s_ini)d a %(s_fin)d %(chip_o)s</h3>
      <p class="ab-txt">De %(s_v0)s toneladas en %(s_ini)d a %(s_vn)s en %(s_fin)d. Toca un año para ver su cifra y cuánto cambió.</p>
      <ol class="ab-s-g" aria-label="Basura recolectada al día por año">%(barras)s</ol>
      <p class="ab-s-det" id="abSerieDet" aria-live="polite"></p>
      <p class="ab-nota">%(serie_fu)s. Los cambios son %(chip_d)s: la cifra del año menos la del levantamiento anterior.</p>
    </div>

    <details class="ab-plg">
      <summary><span aria-hidden="true">🚛</span> ¿Quién recoge la basura de tu municipio? Las concesiones</summary>
      <p class="ab-txt">La Ley General de Residuos (artículo 10, fracciones IV y V) permite al municipio prestar el servicio por sí mismo o a través de gestores, y le da la facultad de otorgar concesiones. La decisión se toma en el cabildo y debe constar en sus actas. %(lgpgir)s</p>
      <p class="ab-txt">%(chip_p1)s Qué municipios tienen el servicio concesionado y cuánto cuesta vienen en los microdatos del censo municipal del INEGI; se integrarán municipio por municipio.</p>
    </details>
  </section>''' % {
        'camino': '\n      '.join(camino), 'chip_d': chip('derivado'), 'chip_o': chip('oficial'),
        'chip_p1': chip('pendiente', pend_ids[1] if len(pend_ids) > 1 else None),
        'gen': num(gen), 'datos': datos_basura,
        'sinpart': esc(R['sinPartidaFederal']['texto']), 'sinpart_fu': fuente('DBGIR', R['sinPartidaFederal']['pagina']),
        'rel_nota': esc(rel.get('nota', '')), 'sitios': num(sit['valor']), 'veh': num(veh['valor']),
        'veh_pct': num(veh['pctAntes2002'], 2), 'veh_fu': fuente('DBGIR', veh['pagina']),
        'per': num(per, 3), 'per_fu': fuente('DBGIR', R['perCapitaKg']['pagina']),
        'norec_pct': pct(100 - rec['pct']), 'rec_pct': num(rec['pct'], 1),
        's_ini': serie['anios'][0], 's_fin': serie['anios'][-1], 's_v0': num(serie['tdia'][0]), 's_vn': num(serie['tdia'][-1]),
        'barras': ''.join(barras), 'serie_fu': fuente('CNGMD', serie['pagina']),
        'lgpgir': liga_ref('ref-lgpgir', 'Ley General de Residuos, reforma DOF 19-01-2026'),
    }

    # ------------------------------------------------------------------
    # 2. Proteger contra dañar
    gpa = C['gasto_proteccion_ambiental']
    dano = C['ctada']['total_mdp']
    ratio = dano / gpa['monto_mdp']
    proteger = '''
  <section class="ab-bloque" id="abProteger" aria-labelledby="abProTit">
    <h2 class="ab-tit" id="abProTit"><span aria-hidden="true">💸</span> Lo que se gasta en proteger, contra lo que cuesta el daño</h2>
    <p class="ab-txt">%(lect)s</p>
    <div class="ab-balanza" aria-label="Gasto en protección contra costo del daño, 2024">
      <div class="ab-bal-f"><span class="ab-bal-r">Gasto en protección ambiental, 2024 %(chip_g)s</span>
        <span class="ab-bal-riel"><span class="ab-bal-b ab-bal-verde" style="--ab-w:%(wg).4f"></span></span>
        <strong class="ab-num">%(gpa)s</strong></div>
      <div class="ab-bal-f"><span class="ab-bal-r">Costo del daño ambiental, 2024 %(chip_c)s</span>
        <span class="ab-bal-riel"><span class="ab-bal-b ab-bal-rojo" style="--ab-w:1"></span></span>
        <strong class="ab-num">%(dano)s</strong></div>
      <p class="ab-bal-x"><span class="ab-bal-xn">× %(ratio)s</span> el daño contra la protección %(chip_d)s</p>
    </div>
    <p class="ab-nota">%(chip_d)s Por cada peso destinado a proteger el ambiente, se deterioraron %(ratio)s (%(dano_n)s ÷ %(gpa_n)s millones). El gasto es solo del sector público consolidado: no incluye empresas privadas ni hogares. %(ceem)s</p>
    <div class="ab-calc" id="abCalc">
      <label class="ab-calc-l" for="abCalcIn">Si se gastan en proteger</label>
      <div class="ab-calc-in"><span aria-hidden="true">$</span><input type="text" inputmode="decimal" id="abCalcIn" class="ab-input" value="100" autocomplete="off"></div>
      <div class="ab-grupo" role="group" aria-label="Montos de ejemplo">
        <button type="button" class="ab-op" data-m="1">$1</button>
        <button type="button" class="ab-op" data-m="100">$100</button>
        <button type="button" class="ab-op" data-m="1000">$1,000</button>
        <button type="button" class="ab-op" data-m="1000000">$1 millón</button>
      </div>
      <p class="ab-calc-res" id="abCalcRes" aria-live="polite"></p>
      <p class="ab-nota">%(chip_d)s Monto × (%(dano_n)s ÷ %(gpa_n)s), con las cifras de 2024 del INEGI.</p>
    </div>
  </section>''' % {
        'lect': 'El INEGI mide cuánto gastó el sector público en proteger el ambiente y cuánto le costó al país agotarlo y dañarlo. Las dos cifras son de 2024, el año más reciente publicado.',
        'chip_g': chip(gpa.get('estado') or 'oficial'), 'chip_c': chip(C['ctada'].get('estado') or 'oficial'), 'chip_d': chip('derivado'),
        'wg': gpa['monto_mdp'] / dano, 'gpa': pmdp(gpa['monto_mdp'] * 1e6), 'dano': pmdp(dano * 1e6),
        'ratio': num(gpa['ratio_dano_sobre_gasto'], 2), 'dano_n': num(dano), 'gpa_n': num(gpa['monto_mdp']), 'ceem': ceem,
    }

    # ------------------------------------------------------------------
    # 3. El presupuesto 2026 y el proyecto 2027
    ap, mo, pa, pr = P['aprobado2026']['valor'], P['modificado2026']['valor'], P['pagado2026']['valor'], P['proyecto2027']['valor']
    var27 = (pr / ap - 1) * 100
    conagua = next((u for u in P['unidades'] if u['ur'] == 'B00'), None)
    filas = []
    for u in P['unidades']:
        av = u['pagado'] / u['modificado'] * 100 if u['modificado'] > 0 else 0
        vp = (u['proyecto2027'] / u['aprobado'] - 1) * 100 if u['aprobado'] > 0 else 0
        filas.append('<tr><th scope="row">%s</th><td class="ab-num">%s</td><td class="ab-num">%s</td><td class="ab-num">%s <small>%s</small></td>'
                     '<td class="ab-num">%s <small class="ab-var %s">%s%s</small></td></tr>'
                     % (esc(u['nombre']), pmdp(u['aprobado']), pmdp(u['modificado']), pmdp(u['pagado']), pct(av),
                        pmdp(u['proyecto2027']), 'ab-sube' if vp >= 0 else 'ab-baja', '+' if vp >= 0 else '', pct(vp)))
    presupuesto = '''
  <section class="ab-bloque" id="abPresupuesto" aria-labelledby="abPreTit">
    <h2 class="ab-tit" id="abPreTit"><span aria-hidden="true">🏛️</span> El presupuesto del sector ambiental: 2026 y el proyecto 2027</h2>
    <p class="ab-txt">El Ramo %(ramo)s, %(nombre)s, reúne a la SEMARNAT, la Comisión Nacional del Agua y sus órganos. Esto se aprobó para 2026, esto se había pagado a medio año y esto propone el Ejecutivo para 2027.</p>
    <div class="ab-datos">%(tarjetas)s</div>
    <h3 class="ab-sub">Órgano por órgano</h3>
    <p class="ab-txt">Elige qué medir. Toca un órgano para ver todas sus cifras.</p>
    <div class="ab-grupo ab-med" role="group" aria-label="Qué medir">
      <button type="button" class="ab-op" data-med="aprobado" aria-pressed="true">Aprobado 2026</button>
      <button type="button" class="ab-op" data-med="pagado" aria-pressed="false">Pagado al 30 de junio</button>
      <button type="button" class="ab-op" data-med="proyecto2027" aria-pressed="false">Proyecto 2027</button>
      <button type="button" class="ab-op" data-med="avance" aria-pressed="false">Avance del pago</button>
      <button type="button" class="ab-op" data-med="cambio" aria-pressed="false">Cambio 2027</button>
    </div>
    <ol class="ab-org" id="abOrg" aria-live="polite"></ol>
    <p class="ab-nota" id="abOrgNota"></p>
    <div class="ab-org-det" id="abOrgDet" aria-live="polite" hidden></div>
    <details class="ab-plg">
      <summary><span aria-hidden="true">📋</span> La tabla completa</summary>
      <div class="ab-tabla-w"><table class="ab-tabla"><thead><tr><th scope="col">Órgano</th><th scope="col">Aprobado 2026</th><th scope="col">Modificado 2026</th><th scope="col">Pagado al 30-jun</th><th scope="col">Proyecto 2027</th></tr></thead>
      <tbody>%(filas)s</tbody>
      <tfoot><tr><th scope="row">Total del Ramo %(ramo)s</th><td class="ab-num">%(ap)s</td><td class="ab-num">%(mo)s</td><td class="ab-num">%(pa)s</td><td class="ab-num">%(pr)s</td></tr></tfoot></table></div>
      <p class="ab-nota">Montos %(chip_o)s: aprobado, %(fu_pef)s; modificado y pagado, %(fu_av)s; proyecto, %(fu_pp)s. Porcentajes %(chip_d)s: el pequeño junto a lo pagado es pagado ÷ modificado × 100; el de 2027, (proyecto ÷ aprobado − 1) × 100. Los siete órganos suman exactamente el total del ramo.</p>
    </details>
    <p class="ab-acciones"><button type="button" class="ab-boton ab-sec" id="abCsv"><span aria-hidden="true">⬇️</span> Descargar la tabla en CSV</button></p>
    <p class="ab-nota">%(nota27)s %(conagua)s Comparar el presupuesto de 2026 con el daño de 2024 es ilustrativo: son años distintos.</p>
  </section>''' % {
        'ramo': esc(P['ramo']), 'nombre': esc(P['nombre']),
        'tarjetas': (
            tarjeta(pmdp(ap), 'aprobado 2026 (Ramo %s)' % esc(P['ramo']), P['aprobado2026'].get('estado', 'oficial'), fuente('PEF', P['aprobado2026']['pagina'])) +
            tarjeta(pmdp(pa), 'pagado al 30 de junio de 2026', P['pagado2026'].get('estado', 'oficial'),
                    '%s del modificado (%s) %s · %s' % (pct(pa / mo * 100), pmdp(mo), chip('derivado'), fuente('AV2T2026', 'base de datos'))) +
            tarjeta(pmdp(pr), 'proyecto 2027', P['proyecto2027'].get('estado', 'oficial'),
                    '%s%s nominal contra 2026 %s · %s' % ('+' if var27 >= 0 else '', pct(var27), chip('derivado'), fuente('PPEF2027', 'base de datos')))),
        'filas': ''.join(filas), 'ap': pmdp(ap), 'mo': pmdp(mo), 'pa': pmdp(pa), 'pr': pmdp(pr),
        'chip_o': chip('oficial'), 'chip_d': chip('derivado'),
        'fu_pef': fuente('PEF', P['aprobado2026']['pagina']), 'fu_av': fuente('AV2T2026', 'base de datos'), 'fu_pp': fuente('PPEF2027', 'base de datos'),
        'nota27': esc(P['proyecto2027'].get('nota', '')),
        'conagua': ('La Comisión Nacional del Agua concentra el %s del ramo aprobado (%s ÷ %s × 100, %s).'
                    % (pct(conagua['aprobado'] / ap * 100), pmdp(conagua['aprobado']), pmdp(ap), chip('derivado'))) if conagua else '',
    }

    # ------------------------------------------------------------------
    # 4. Megaobras
    sim = base.get('simulador_megaobras') or {}
    obras = {o['id']: o for o in sim.get('obras', [])}
    tarj_obras = []
    for oid in OBRAS_FISICAS:
        o = obras.get(oid)
        if not o:
            continue
        e = (o.get('estado_campos') or {}).get('inversion_real_mdp') or 'pendiente'
        e = e if e in ('oficial', 'derivado', 'pendiente') else 'derivado'
        tarj_obras.append(
            '<li class="ab-obra"><a class="ab-obra-a" href="herramienta-megaobras-sector.html#obra-%s">'
            '<span class="ab-obra-ico" aria-hidden="true">%s</span><span class="ab-obra-n">%s</span>'
            '<span class="ab-obra-ir">Su ficha en Obra por obra, por industria ➔</span></a>'
            '<dl class="ab-obra-dl"><div><dt>Costo registrado</dt><dd><b class="ab-num">%s</b> %s</dd></div>'
            '<div><dt>Lo que su permiso ambiental autorizó</dt><dd>%s</dd></div></dl></li>'
            % (esc(oid), esc(o.get('icono', '')), esc(o['nombre']), '$' + format(o['inversion_real_mdp'], ',.1f') + ' mdp',
               chip(e, ('obra-' + oid) if e == 'pendiente' else None), chip('pendiente', pend_ids[0] if pend_ids else None)))
    megaobras = '''
  <section class="ab-bloque" id="abMegaobras" aria-labelledby="abMegTit">
    <h2 class="ab-tit" id="abMegTit"><span aria-hidden="true">🏗️</span> La huella de las megaobras</h2>
    <p class="ab-txt">Toda obra que pueda causar desequilibrio ecológico necesita, antes de empezar, una Manifestación de Impacto Ambiental aprobada por la SEMARNAT (Ley General del Equilibrio Ecológico, artículo 28). En ese documento la propia obra reconoce cuánta vegetación retirará, qué especies afecta y qué medidas promete. %(lgeepa)s</p>
    <div class="ab-alerta ab-alerta-p">%(chip_p0)s %(pend0)s</div>
    <p class="ab-txt">Aquí irá, obra por obra: lo que su permiso ambiental autorizó, lo que la Auditoría Superior o la PROFEPA hayan documentado después y lo que la obra costó. Mientras llega el documento, estas son las megaobras de construcción del registro, con lo que ya se sabe de su costo:</p>
    <ul class="ab-obras">%(obras)s</ul>
    <p class="ab-nota">Costo registrado en pesos de cada año, sin quitar la inflación, con el estado que le da el registro de megaobras; toca la etiqueta para ver de dónde sale o por qué falta. Quedan fuera los rescates financieros (FOBAPROA, FARAC), las compras de empresas (Fertinal, Agronitrogenados) y los programas (Enciclomedia): no son obra que pida permiso ambiental.</p>
    <p class="ab-acciones"><a class="ab-boton ab-sec" href="herramienta-megaobras-sector.html"><span aria-hidden="true">🏭</span> Ver el costo de todas las megaobras</a></p>
  </section>''' % {
        'lgeepa': liga_ref('ref-lgeepa', 'Ley General del Equilibrio Ecológico'),
        'chip_p0': chip('pendiente', pend_ids[0] if pend_ids else None),
        'pend0': esc(A['pendientes'][0]) if A.get('pendientes') else '',
        'obras': ''.join(tarj_obras),
    }

    # ------------------------------------------------------------------
    # 5. Leyes
    TEMAS = {'ref-cpeum': 'derecho', 'ref-lgpgir': 'basura', 'ref-lgeepa': 'obras', 'ref-lgcc': 'clima', 'ref-lieps': 'clima'}
    leyes = []
    for lx in A['leyes']:
        tema = TEMAS.get(lx['refKey'], 'derecho')
        if '115' in lx['norma']:
            tema = 'basura'
        leyes.append('<li class="ab-ley" data-tema="%s"><p class="ab-ley-n">%s</p><p class="ab-ley-d">%s</p><p class="ab-ley-r">%s %s</p></li>'
                     % (tema, esc(lx['norma']), esc(lx['dice']), chip('oficial'), liga_ref(lx['refKey'], 'Texto vigente')))
    leyes_html = '''
  <section class="ab-bloque" id="abLeyes" aria-labelledby="abLeyTit">
    <h2 class="ab-tit" id="abLeyTit"><span aria-hidden="true">⚖️</span> Las leyes que aplican</h2>
    <p class="ab-txt">%(n)d normas, con su texto vigente en la Cámara de Diputados. Filtra por tema.</p>
    <div class="ab-grupo" role="group" aria-label="Tema de la ley">
      <button type="button" class="ab-op" data-tema="todas" aria-pressed="true">Todas</button>
      <button type="button" class="ab-op" data-tema="derecho" aria-pressed="false">🌱 Tu derecho</button>
      <button type="button" class="ab-op" data-tema="basura" aria-pressed="false">🗑️ La basura</button>
      <button type="button" class="ab-op" data-tema="obras" aria-pressed="false">🏗️ Las obras</button>
      <button type="button" class="ab-op" data-tema="clima" aria-pressed="false">🌡️ Clima e impuestos</button>
    </div>
    <ul class="ab-leyes" id="abLeyesL">%(leyes)s</ul>
  </section>''' % {'n': len(A['leyes']), 'leyes': ''.join(leyes)}

    # ------------------------------------------------------------------
    # 6. Quien lo mide hoy
    quien = []
    for q in A['quienMide']:
        v = q['estado'] == 'vigente'
        quien.append('<li class="ab-q%s" data-est="%s"><p class="ab-q-d">%s</p><p class="ab-q-m">%s</p>'
                     '<p class="ab-q-e"><span class="ab-est ab-est-%s">%s</span>%s</p></li>'
                     % ('' if v else ' ab-q-c', 'v' if v else 'c', esc(q['dato']), esc(q['mide']), 'v' if v else 'c',
                        'vigente' if v else 'cambió', (' <small>%s</small>' % esc(q['nota'])) if q.get('nota') else ''))
    docs = []
    for k, f in F.items():
        sha = f.get('sha256') or ''
        docs.append('<li><a class="ab-fu" href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>%s</li>'
                    % (esc(f['url']), esc(f['doc']),
                       (' <button type="button" class="ab-sha" data-sha="%s" title="Copiar la huella SHA-256 completa">SHA-256 <code>%s…</code></button>'
                        % (esc(sha), esc(sha[:16]))) if sha else ''))
    docs.append('<li>%s</li>' % ceem)
    pend_li = ''.join('<li>%s %s</li>' % (chip('pendiente', pend_ids[i]), esc(t)) for i, t in enumerate(A.get('pendientes', [])))
    n_cambio = sum(1 for q in A['quienMide'] if q['estado'] != 'vigente')
    quien_html = '''
  <section class="ab-bloque" id="abQuien" aria-labelledby="abQuiTit">
    <h2 class="ab-tit" id="abQuiTit"><span aria-hidden="true">🏛️</span> Quién lo mide hoy</h2>
    <p class="ab-txt">Varias instituciones cambiaron con las reformas de 2024 y 2025. Así queda cada dato de esta sección.</p>
    <div class="ab-grupo" role="group" aria-label="Qué mostrar">
      <button type="button" class="ab-op" data-q="todo" aria-pressed="true">Todos (%(nq)d)</button>
      <button type="button" class="ab-op" data-q="c" aria-pressed="false">Solo lo que cambió (%(nc)d)</button>
    </div>
    <ul class="ab-quien" id="abQuienL">%(quien)s</ul>
    <h3 class="ab-sub">Los documentos de esta sección</h3>
    <p class="ab-txt">Cada documento con su huella SHA-256: si descargas el archivo y su huella coincide, es el mismo que usamos. Toca la huella para copiarla completa.</p>
    <ol class="ab-docs">%(docs)s</ol>
    <p class="ab-copiado" id="abCopiado" aria-live="polite"></p>
    <h3 class="ab-sub">Lo que todavía falta</h3>
    <ul class="ab-pend">%(pend)s</ul>
    <p class="ab-nota">%(nota)s Consulta: %(consulta)s.</p>
    <p class="ab-acciones"><a class="ab-boton ab-sec" href="herramienta-ambiente-pib.html"><span aria-hidden="true">📉</span> Ver el detalle de las cuentas ecológicas</a></p>
  </section>''' % {'nq': len(A['quienMide']), 'nc': n_cambio, 'quien': ''.join(quien), 'docs': ''.join(docs),
                   'pend': pend_li, 'nota': esc(A.get('nota', '')), 'consulta': esc(A.get('consulta', ''))}

    # ------------------------------------------------------------------
    datos = {
        'gen': gen, 'per': per, 'recPct': rec['pct'], 'relPct': rel['pct'], 'relT': rel['tdia'], 'sitT': sit['tdia'],
        'serie': {'a': serie['anios'], 't': serie['tdia']},
        'dano': dano, 'gpa': gpa['monto_mdp'],
        'ramo': P['ramo'], 'tot': {'aprobado': ap, 'modificado': mo, 'pagado': pa, 'proyecto2027': pr},
        'org': [{'ur': u['ur'], 'n': u['nombre'], 'aprobado': u['aprobado'], 'modificado': u['modificado'],
                 'pagado': u['pagado'], 'proyecto2027': u['proyecto2027']} for u in P['unidades']],
        'fu': {k: {'doc': F[k]['doc'], 'url': F[k]['url']} for k in ('PEF', 'AV2T2026', 'PPEF2027') if k in F},
    }

    arranque = '''
  <section class="ab-arranque" aria-labelledby="abArrTit">
    <p class="ab-kicker">Costo Ambiental · aplicación 3</p>
    <h2 class="ab-grande" id="abArrTit">La basura y lo que se gasta en proteger</h2>
    <p class="ab-txt">Cada día el país genera <b>%(gen)s toneladas</b> de basura y solo el <b>%(rel)s</b> de lo que llega a un sitio de disposición final termina en un relleno sanitario. Por cada peso que el sector público gastó en proteger el ambiente en 2024, el daño costó <b>%(ratio)s</b>. Aquí ves cómo, con qué dinero y con qué leyes.</p>
    <ol class="ab-indice" aria-label="Lo que hay en esta página">
      <li><a href="#abBasura"><span aria-hidden="true">🗑️</span> La basura</a></li>
      <li><a href="#abProteger"><span aria-hidden="true">💸</span> Proteger contra dañar</a></li>
      <li><a href="#abPresupuesto"><span aria-hidden="true">🏛️</span> Presupuesto 2026 y 2027</a></li>
      <li><a href="#abMegaobras"><span aria-hidden="true">🏗️</span> Las megaobras</a></li>
      <li><a href="#abLeyes"><span aria-hidden="true">⚖️</span> Las leyes</a></li>
      <li><a href="#abQuien"><span aria-hidden="true">🔎</span> Quién lo mide</a></li>
    </ol>
  </section>''' % {'gen': num(gen), 'rel': pct(rel['pct']), 'ratio': '$' + num(gpa['ratio_dano_sobre_gasto'], 2)}

    aviso = '''
  <aside class="ab-aviso">
    <p><b>De dónde sale cada cifra.</b> De la SEMARNAT (diagnóstico de residuos de abril de 2026), del INEGI (censo municipal 2023 y Cuentas Económicas y Ecológicas 2024) y de Hacienda (PEF 2026, avance al 30 de junio y proyecto 2027). Cada una lleva su documento y su página; las que hacemos nosotros dicen «derivado» y su operación. Lo que todavía falta está en el <a href="pendientes.html#tema-ambiente">Registro de pendientes</a>. Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>.</p>
    <p class="ab-hermanas">Sigue en Costo Ambiental: <a href="herramienta-ambiente-reloj.html">⏱️ El reloj y el año</a> · <a href="herramienta-ambiente-ticket.html">🧾 Tu ticket en negativo</a> · <a href="herramienta-ambiente-pib.html">📉 El PIB no alcanza</a> · <a href="herramienta-ambiente-crisis.html">🌀 Crisis ambientales</a></p>
  </aside>'''

    return ('<div class="ab" id="abRaiz">' + arranque + basura + proteger + presupuesto + megaobras + leyes_html + quien_html + aviso +
            '\n  <script type="application/json" id="abDatos">' + _json(datos) + '</script>\n</div>')
