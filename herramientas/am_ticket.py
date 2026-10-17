# -*- coding: utf-8 -*-
"""Segunda aplicacion de Costo Ambiental: «Tu ticket en negativo» en pagina
propia (16-10-2026). Sustituye al marco que cargaba la portada entera
(index.html?ir=ambiente&ancla=eb-amticket&visor=1).

Lo mismo que pintaba renderAmTicket() / amTicketEmitir() del motor
(audit-engine.js): reparte por habitante (CONAPO 2026, la misma poblacion de
calculadora_civica.parametros) cuatro cifras oficiales y las mide contra el
ingreso neto del lector:
  - intereses de la deuda (PEF 2026, Anexo 8: calculadora_civica.relojes),
  - dano ambiental del pais y su renglon de basura (INEGI, CEEM 2024:
    cuentas_ecologicas),
  - deuda publica total (SHRFSP estimado al cierre de 2026, CGPE 2027:
    ticket_negativo),
  - y como abonos, el Ramo 16 aprobado 2026 (ambiente.presupuesto) y el
    gasto en proteccion ambiental 2024 (cuentas_ecologicas), con la basura
    en kilos (SEMARNAT, ambiente.residuos).
Las cifras por habitante se calculan aqui con la misma operacion que
amTkCuentas() (monto entre poblacion.millones x 1e6) y se escriben en el
HTML; el JS (am-ticket.js) solo divide entre el ingreso del lector.

Diferencia con el motor: alla el ingreso sugerido salia del bloque 1 de la
Calculadora ya calculado. Aqui se lee la clave compartida
auditavision_cc_sueldo; si el lector guardo un bruto, su neto se saca con
las reglas de quien esta en nomina (tarifa del art. 96 de la LISR, subsidio
para el empleo y cuotas obreras del IMSS), igual que cc_compara.py, y se
dice.

Regla de la plataforma (AGENTS.md, §2): todo lo del ticket es derivado y lo
dice; cada cifra de origen lleva su documento y su chip.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['amticket']).
"""
import html
import json

from presupuesto_modulos import chip

ESTILOS = ['am-ticket.css']
SCRIPTS = ['am-ticket.js']


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def esc(t):
    return html.escape(str(t or ''), quote=True)


def _n(v, d=0):
    return format(v, ',.%df' % d)


def _mdp(v):
    return '$' + format(round(v), ',') + ' mdp'


def _pesos(v):
    return '$' + format(round(v), ',')


def _liga(url, texto, titulo=''):
    if not url:
        return '<span class="at-fuente">%s fuente por documentar</span>' % chip('pendiente')
    return ('<a class="at-fuente" href="%s" target="_blank" rel="noopener noreferrer"%s>%s ↗</a>'
            % (esc(url), (' title="%s"' % esc(titulo)) if titulo else '', esc(texto)))


def cuentas(base):
    """Replica de amTkCuentas() del motor, sin el ingreso: lo que toca a
    cada habitante. Devuelve tambien las cifras de origen y sus fuentes."""
    T = base['ticket_negativo']
    C = base['cuentas_ecologicas']
    A = base['ambiente']
    cc = base['calculadora_civica']
    pob = cc['parametros']['poblacion']
    hab = pob['millones'] * 1e6
    rel = next((x for x in (cc.get('relojes') or {}).get('fuentes') or [] if x['id'] == 'intereses'), None)
    resid = next((x for x in C['degradacion'].get('componentes') or [] if x['id'] == 'residuos'), None)
    return {
        'T': T, 'C': C, 'A': A, 'pob': pob, 'hab': hab, 'rel': rel, 'resid': resid,
        'intereses': rel['anual_mdp'] * 1e6 / hab if rel else 0,
        'dano': C['ctada']['total_mdp'] * 1e6 / hab,
        'basuraPesos': resid['monto_mdp'] * 1e6 / hab if resid else 0,
        'deuda': T['shrfsp']['estimado2026_mdp'] * 1e6 / hab,
        'ramo16': A['presupuesto']['aprobado2026']['valor'] / hab,
        'gpa': C['gasto_proteccion_ambiental']['monto_mdp'] * 1e6 / hab,
        'kgDia': A['residuos']['perCapitaKg']['valor'],
        'kg': A['residuos']['perCapitaKg']['valor'] * 365,
    }


def _fuente_amb(A, clave, pagina):
    f = (A.get('fuentes') or {}).get(clave)
    if not f:
        return _liga('', '')
    pag = '' if pagina in (None, '') else (', p. %s' % pagina if str(pagina).isdigit() else ', %s' % pagina)
    return _liga(f.get('url'), (f.get('corto') or f.get('doc')) + pag, f.get('doc'))


def _fuente_tk(T, clave, pagina):
    f = (T.get('fuentes') or {}).get(clave)
    if not f:
        return _liga('', '')
    return _liga(f.get('url'), f['corto'] + ', p. ' + str(pagina), f.get('doc'))


def construir(base, ref):
    c = cuentas(base)
    T, C, A, pob, rel, resid = c['T'], c['C'], c['A'], c['pob'], c['rel'], c['resid']
    cc = base['calculadora_civica']
    par = cc['parametros']
    sm = par['salario_minimo']
    refs = {r['id']: r for r in base.get('referencias_legales') or []}
    r_pef = refs.get(rel['refKey']) if rel else None
    r_ceem = refs.get('ref-ceem-2024')
    ceem = _liga(r_ceem and r_ceem.get('url'), 'INEGI, CEEM 2024', r_ceem and r_ceem.get('cita_apa'))
    sh = T['shrfsp']

    origen = [
        ('📉', 'Intereses de la deuda pública, 2026',
         '%s de costo financiero de la deuda %s %s' % (_mdp(rel['anual_mdp']) if rel else '', chip(rel.get('estado', 'oficial')) if rel else chip('pendiente'),
                                                       _liga(r_pef and r_pef.get('url'), 'PEF 2026, Anexo 8', r_pef and r_pef.get('cita_apa'))),
         'Entre %s millones de habitantes: <b>%s</b> por persona %s.' % (_n(pob['millones'], 1), _pesos(c['intereses']), chip('derivado'))),
        ('🏭', 'Daño ambiental del país, 2024',
         '%s de costos totales por agotamiento y degradación ambiental (%s %% del PIB) %s %s'
         % (_mdp(C['ctada']['total_mdp']), _n(C['ctada']['pct_pib'], 1), chip(C['ctada'].get('estado', 'oficial')), ceem),
         'Entre los habitantes: <b>%s</b> por persona %s.' % (_pesos(c['dano']), chip('derivado'))),
        ('🗑️', 'De él, basura mal gestionada, 2024',
         '%s del renglón «%s» de la degradación %s %s' % (_mdp(resid['monto_mdp']), esc(resid['nombre']), chip(resid.get('estado', 'oficial')), ceem) if resid else chip('pendiente'),
         'Entre los habitantes: <b>%s</b> por persona %s. Ya va incluido en el daño ambiental: no se suma dos veces.' % (_pesos(c['basuraPesos']), chip('derivado'))),
        ('🏦', 'Deuda pública total (SHRFSP), cierre estimado 2026',
         '%s, %s %% del PIB %s %s. %s' % (_mdp(sh['estimado2026_mdp']), _n(sh['estimado2026_pib'], 1), chip(sh['estado']),
                                          _fuente_tk(T, sh['fuente'], sh['pagina']), esc(sh['que'])),
         'Entre los habitantes: <b>%s</b> por persona %s.' % (_pesos(c['deuda']), chip('derivado'))),
        ('🌳', 'Presupuesto federal de Medio Ambiente (Ramo 16), aprobado 2026',
         '$%s pesos %s %s' % (_n(A['presupuesto']['aprobado2026']['valor']), chip(A['presupuesto']['aprobado2026'].get('estado', 'oficial')),
                              _fuente_amb(A, A['presupuesto']['aprobado2026']['fuente'], A['presupuesto']['aprobado2026']['pagina'])),
         'Entre los habitantes: <b>+%s</b> por persona %s.' % (_pesos(c['ramo16']), chip('derivado'))),
        ('🛡️', 'Gasto en protección ambiental del sector público, 2024',
         '%s del sector público consolidado (federación, entidades, municipios y empresas públicas; sin hogares ni empresas privadas) %s %s, p. 2'
         % (_mdp(C['gasto_proteccion_ambiental']['monto_mdp']), chip(C['gasto_proteccion_ambiental'].get('estado', 'oficial')), ceem),
         'Entre los habitantes: <b>+%s</b> por persona %s.' % (_pesos(c['gpa']), chip('derivado'))),
        ('⚖️', 'Basura por persona',
         '%s kg por persona al día %s %s' % (_n(c['kgDia'], 3), chip(A['residuos']['perCapitaKg'].get('estado', 'oficial')),
                                             _fuente_amb(A, A['residuos']['perCapitaKg']['fuente'], A['residuos']['perCapitaKg']['pagina'])),
         'Por 365 días: <b>%s kg</b> al año %s.' % (_n(c['kg']), chip('derivado'))),
        ('👥', 'Población entre la que se reparte',
         '%s millones de personas %s %s. %s' % (_n(pob['millones'], 1), chip(pob['estado']), _liga(pob.get('url'), 'CONAPO, población a mitad de 2026', pob.get('fuente')),
                                                esc(pob.get('como') or '')),
         'Como en el motor, el reparto usa la cifra en millones (%s × 1,000,000).' % _n(pob['millones'], 1)),
    ]
    origen_html = '\n'.join(
        '<li class="at-or"><span class="at-or-ico" aria-hidden="true">%s</span><div><p class="at-or-t">%s</p><p class="at-or-d">%s</p><p class="at-or-op">%s</p></div></li>'
        % (ico, t, d, op) for ico, t, d, op in origen)

    tm = cc['tarifa_mensual']
    im = cc['imss_obrero']
    se = par['subsidio_empleo']
    uma = par['uma']

    datos = {
        'pob': pob['millones'],
        'intereses': c['intereses'], 'dano': c['dano'], 'basuraPesos': c['basuraPesos'], 'deuda': c['deuda'],
        'ramo16': c['ramo16'], 'gpa': c['gpa'], 'kgDia': c['kgDia'], 'kg': c['kg'],
        'nota': T['nota'],
        'sm': {'general': sm['mensual_general'], 'frontera': sm['mensual_frontera'], 'diario': sm['general']},
        'isr': {'renglones': tm['renglones'], 'tope_uma': im['tope_sbc_uma'], 'ramos': [{'pct': r['pct'], 'base': r['base']} for r in im['ramos']],
                'uma_diaria': uma['diaria'], 'uma_mensual': uma['mensual'], 'sub_pct': se['pct_uma'], 'sub_tope': se['tope_ingreso_mensual']},
    }

    return '''<div class="at" id="atRaiz">
  <section class="at-arranque" aria-labelledby="atArrTit">
    <p class="at-kicker">Costo Ambiental · aplicación 2</p>
    <h2 class="at-grande" id="atArrTit"><span aria-hidden="true">🧾</span> Tu ticket en negativo</h2>
    <p class="at-txt">Tu estado de cuenta de la Calculadora te dice a dónde va lo que pagas. Este ticket te dice lo contrario: <b>lo que ya te cargaron a tu nombre sin preguntarte</b>. Tu parte de la deuda del gobierno, de los intereses que esa deuda cobra cada año y del daño ambiental del país, medida contra lo que ganas.</p>
    <p class="at-privado"><span aria-hidden="true">🔒</span> Lo que escribes se queda en tu navegador: no se envía a ningún lado.</p>
    <ol class="at-indice" aria-label="Lo que hay en esta página">
      <li><a href="#atPaso1"><span class="at-n">1</span> Lo que ganas</a></li>
      <li><a href="#atTicketSec"><span class="at-n">2</span> Tu ticket</a></li>
      <li><a href="#atCalendario"><span class="at-n">3</span> Tu año en días</a></li>
      <li><a href="#atBasura"><span class="at-n">4</span> Tu basura</a></li>
      <li><a href="#atOrigen"><span class="at-n">5</span> De dónde sale</a></li>
    </ol>
  </section>

  <section class="at-paso" id="atPaso1" aria-labelledby="atP1Tit">
    <h2 class="at-tit" id="atP1Tit"><span class="at-n">1</span> ¿Cuánto ganas?</h2>
    <div class="at-mandos">
      <div class="at-seg" role="group" aria-label="Periodo">
        <button type="button" class="at-seg-b" data-per="mes" aria-pressed="true">Al mes</button>
        <button type="button" class="at-seg-b" data-per="anio" aria-pressed="false">Al año</button>
      </div>
      <div class="at-seg" role="group" aria-label="Neto o bruto">
        <button type="button" class="at-seg-b" data-tipo="neto" aria-pressed="true">Neto (lo que te llega)</button>
        <button type="button" class="at-seg-b" data-tipo="bruto" aria-pressed="false">Bruto (antes de impuestos)</button>
      </div>
    </div>
    <label class="at-campo" for="atIngreso"><span id="atIngresoEt">Tu ingreso neto al mes</span>
      <span class="at-caja"><b class="at-caja-sig" aria-hidden="true">$</b><input type="text" id="atIngreso" class="at-input" inputmode="decimal" autocomplete="off" placeholder="Ej.: {sm_txt}"></span></label>
    <input type="range" id="atRango" class="at-rango" min="0" max="200000" step="500" value="0" aria-label="Ajusta tu ingreso mensual">
    <p class="at-neto" id="atNeto" aria-live="polite"></p>
    <div class="at-acciones">
      <button type="button" class="at-boton" id="atEmitir"><span aria-hidden="true">🧾</span> Emitir mi ticket en negativo</button>
      <button type="button" class="at-btn" data-ej="general" title="Salario mínimo general 2026: CONASAMI, DOF 9 de diciembre de 2025"><span aria-hidden="true">📄</span> Ejemplo oficial: salario mínimo ({sm_g})</button>
      <button type="button" class="at-btn" data-ej="frontera" title="Salario mínimo de la Zona Libre de la Frontera Norte 2026: CONASAMI, DOF 9 de diciembre de 2025"><span aria-hidden="true">🌵</span> Mínimo de la frontera norte ({sm_f})</button>
      <button type="button" class="at-btn" id="atReiniciar"><span aria-hidden="true">↺</span> Reiniciar en cero</button>
    </div>
    <p class="at-origen" id="atOrigenTx">Lo que te queda después de impuestos. Si no lo sabes, escríbelo en bruto y lo calculamos, o sácalo completo en <a href="herramienta-calculadora-ticket.html">🧾 Tu estado de cuenta</a>.</p>
  </section>

  <section class="at-sec" id="atTicketSec" aria-labelledby="atTkTit">
    <h2 class="at-tit" id="atTkTit"><span class="at-n">2</span> Tu ticket</h2>
    <div id="atSalida" aria-live="polite"><p class="at-vacio">Escribe tu ingreso y pulsa «Emitir». El ticket se imprime renglón por renglón.</p></div>
    <div class="at-tk-acc" id="atTkAcc" hidden>
      <button type="button" class="at-btn" id="atCopiar"><span aria-hidden="true">📋</span> Copiar mi ticket</button>
      <button type="button" class="at-btn" id="atLiga"><span aria-hidden="true">🔗</span> Compartir</button>
      <button type="button" class="at-btn" id="atImprimir"><span aria-hidden="true">🖨️</span> Imprimir</button>
      <span class="at-aviso-c" id="atAvisoC" role="status"></span>
    </div>
  </section>

  <section class="at-sec" id="atCalendario" aria-labelledby="atCalTit">
    <h2 class="at-tit" id="atCalTit"><span class="at-n">3</span> Tu año en días</h2>
    <p class="at-txt">Imagina que, desde el 1 de enero, todo lo que ganas se fuera a pagar tu parte. ¿Hasta qué día trabajarías? La regla mide cada cargo en días de tu ingreso {chip_d}.</p>
    <div id="atCal"><p class="at-vacio">Aparece cuando escribas tu ingreso.</p></div>
    <h3 class="at-sub">Y la deuda acumulada, en meses de tu ingreso</h3>
    <p class="at-txt">Cada cuadro es un mes de lo que ganas. La deuda no se paga en un año: es lo que el sector público debe, acumulado.</p>
    <div id="atMeses"><p class="at-vacio">Aparece cuando escribas tu ingreso.</p></div>
  </section>

  <section class="at-sec" id="atBasura" aria-labelledby="atBasTit">
    <h2 class="at-tit" id="atBasTit"><span class="at-n">4</span> <span aria-hidden="true">🗑️</span> Tu huella física: la basura</h2>
    <p class="at-txt">Según SEMARNAT, cada persona genera en promedio <b>{kg_dia} kg de basura al día</b> {chip_kg} {f_kg}. No depende de lo que ganas: es el promedio nacional. Lo demás es multiplicar {chip_d}.</p>
    <div class="at-kg" id="atKg">
      <div class="at-kg-c"><b>{kg_dia} kg</b><span>al día</span></div>
      <div class="at-kg-c"><b>{kg_sem} kg</b><span>a la semana (× 7)</span></div>
      <div class="at-kg-c"><b>{kg_mes} kg</b><span>al mes (× 30)</span></div>
      <div class="at-kg-c at-kg-anio"><b>{kg_anio} kg</b><span>al año (× 365)</span></div>
    </div>
    <p class="at-txt" id="atKgHoy"></p>
    <p class="at-txt">Ese servicio lo pagan los municipios, que son el orden de gobierno con menos ingreso propio. La basura mal gestionada le costó al país <b>{basura_mdp}</b> en 2024 {chip_b} {ceem}: <b>{basura_hab}</b> por persona {chip_d}. Más en <a href="herramienta-ambiente-basura.html">🗑️ Basura y protección</a>.</p>
  </section>

  <section class="at-sec" id="atOrigen" aria-labelledby="atOrTit">
    <h2 class="at-tit" id="atOrTit"><span class="at-n">5</span> De dónde sale cada renglón</h2>
    <p class="at-txt">Cada renglón del ticket divide una cifra oficial entre los habitantes del país {r_pef} {r_ceem}. Aquí está cada cifra con su documento.</p>
    <ul class="at-origenes">
{origen}
    </ul>
  </section>

  <aside class="at-aviso" aria-labelledby="atLeeTit">
    <h2 class="at-tit" id="atLeeTit"><span aria-hidden="true">🔍</span> ¿Cómo se lee este ticket?</h2>
    <p>{nota} Los días y los meses dividen cada cargo entre tu ingreso {chip_d}.</p>
    <p>Los cargos del año juntan cifras de años distintos: los intereses son los aprobados para 2026 y el daño ambiental es el último que publicó el INEGI, el de 2024. Se suman para darte un orden de magnitud, y cada renglón dice su año.</p>
    <p>Si escribes un bruto, tu neto se calcula como el de quien trabaja en nómina (sueldos y salarios): la tarifa mensual del ISR ({r_isr}) menos el subsidio para el empleo ({r_sub}) y las cuotas obreras del IMSS ({r_imss}). El salario mínimo no paga ISR ni cuota obrera: su neto es igual a su bruto. Si cobras por honorarios, RESICO u otro régimen, escribe tu neto.</p>
    <p>Lo que todavía nos deben las dependencias está en el <a href="pendientes.html">Registro de pendientes</a>. Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>.</p>
    <p class="at-hermanas">Sigue con Costo Ambiental: <a href="herramienta-ambiente-reloj.html">⏱️ El reloj y el año</a> · <a href="herramienta-ambiente-basura.html">🗑️ Basura y protección</a> · <a href="herramienta-ambiente-pib.html">📉 El PIB no alcanza</a> · <a href="herramienta-ambiente-crisis.html">🌀 Crisis ambientales</a></p>
    <p class="at-hermanas">Y con la Calculadora: <a href="herramienta-calculadora-ticket.html">🧾 Tu estado de cuenta</a> · <a href="herramienta-calculadora-reloj.html">⏱️ El reloj de la deuda</a></p>
  </aside>
  <script type="application/json" id="atDatos">{datos}</script>
</div>'''.format(
        sm_txt=_n(sm['mensual_general'], 2), sm_g=_pesos(sm['mensual_general']), sm_f=_pesos(sm['mensual_frontera']),
        chip_d=chip('derivado'),
        kg_dia=_n(c['kgDia'], 3), kg_sem=_n(c['kgDia'] * 7, 1), kg_mes=_n(c['kgDia'] * 30, 1), kg_anio=_n(c['kg']),
        chip_kg=chip(A['residuos']['perCapitaKg'].get('estado', 'oficial')),
        f_kg=_fuente_amb(A, A['residuos']['perCapitaKg']['fuente'], A['residuos']['perCapitaKg']['pagina']),
        basura_mdp=_mdp(resid['monto_mdp']) if resid else '', chip_b=chip(resid.get('estado', 'oficial')) if resid else chip('pendiente'),
        ceem=ceem, basura_hab=_pesos(c['basuraPesos']),
        r_pef=ref('ref-pef2026'), r_ceem=ref('ref-ceem-2024'),
        origen=origen_html, nota=esc(T['nota']),
        r_isr=esc(tm['ley'] + ', ' + tm['fuente']), r_sub=esc(se['fuente']), r_imss=esc(im['fuente']),
        datos=_json(datos))
