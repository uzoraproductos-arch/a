# -*- coding: utf-8 -*-
"""El estado de resultados del Gobierno, en pagina propia (pedido del autor,
12-10-2026): numeros-estado-de-resultados.html.

Antes la pagina cargaba el auditor completo en un marco para abrir el bloque
eb-cuenta-federal del motor. Ahora se escribe aqui, con las mismas cifras de
window.AUDIT_DB (cuentaFederal2024 y cuentas_ecologicas) ya puestas en el
HTML: se lee sin JavaScript. resultados.js solo cambia de pestana y mueve el
«¿Cuanto crees?» de los intereses.

Ninguna cifra es nueva: las oficiales son las de la base, con su documento;
las derivadas dicen su operacion, y las pendientes llevan su chip, su porque
y su ficha del Registro de pendientes (cp2024-tomo2, prog-montos-*,
prog-resultados).

Lo usa apartados.numeros_preparar(); recibe `ref(id)`, que pinta la
llamada [nn] a fuentes-oficiales.html, y `glos(termino, texto)`.
"""
import json


def chip(e, pend=None):
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, (' data-pend="%s"' % pend) if pend else '', e)


def mdp(v, d=1):
    return '$' + format(v, ',.%df' % d) + ' mdp'


def doc(url, texto='Documento ↗'):
    return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (url, texto)


PEND_CP = 'cp2024-tomo2'

# Lo que cada estado financiero es, dicho como en una empresa. La Ley General
# de Contabilidad Gubernamental (art. 46) le pide al Gobierno Federal estos
# estados, con las normas del CONAC.
VISTAS = [
    ('presupuesto', '📊', 'Presupuesto', 'Lo que se autorizó y lo que se gastó',
     'El presupuesto se sigue en cinco momentos: lo que <b>aprobó</b> la Cámara de Diputados, cómo se <b>modificó</b> en el año, lo que se <b>devengó</b> (la obligación de pagar ya reconocida), lo que se <b>ejerció</b> y lo que se <b>pagó</b>. Es la vista de la caja chica: cuánto se prometió y cuánto salió.'),
    ('actividades', '📑', 'Estado de actividades', 'El estado de resultados: lo que entró y lo que costó',
     'Es el equivalente del <b>estado de pérdidas y ganancias</b> de una empresa: los ingresos de la gestión (impuestos, derechos, productos y aprovechamientos) contra los gastos del año. Si los ingresos superan a los gastos hay <b>ahorro</b>; si no, <b>desahorro</b>.'),
    ('flujos', '💵', 'Flujos de efectivo', 'Por dónde entró y salió el dinero en efectivo',
     'Separa el efectivo en tres corrientes: la <b>operación</b> diaria del gobierno, la <b>inversión</b> (obra, equipo, activos) y el <b>financiamiento</b> (deuda que se contrata o se paga). Al final queda el efectivo con que cierra el año.'),
    ('situacion', '🏛️', 'Situación financiera', 'El balance: lo que tiene, lo que debe y lo que queda',
     'Es la foto al 31 de diciembre: el <b>activo</b> (lo que el Gobierno Federal tiene), el <b>pasivo</b> (lo que debe) y la <b>hacienda pública</b> o patrimonio, que es la diferencia. Siempre se cumple: activo = pasivo + patrimonio.'),
    ('social', '🎯', 'Resultados sociales', 'Programas sociales y cuentas ecológicas',
     'Un estado financiero dice cuánto se gastó, no qué se logró. Aquí van los programas sociales más grandes, con lo aprobado contra lo devengado, y el costo ambiental del país que mide el INEGI.'),
    ('conciliacion', '⚖️', 'Conciliación', 'Por qué el gasto del presupuesto no es el del estado de resultados',
     'La Ley General de Contabilidad Gubernamental pide conciliar el gasto del presupuesto con el gasto contable. No son iguales, y la diferencia tiene reglas: la obra que se vuelve activo no es gasto del año, es inversión; y pagar el capital de una deuda no es gasto, reduce el pasivo.'),
]

# Que significa cada renglon pendiente, para que el lector sepa que falta.
QUE_ES = {
    'modificado': 'Lo aprobado, con las ampliaciones y reducciones que Hacienda autorizó durante el año.',
    'devengado': 'Lo que el gobierno reconoció como obligación de pago: el bien se recibió o el servicio se prestó.',
    'ejercido': 'Lo que ya tiene su cuenta por liquidar certificada: la orden de pago emitida.',
    'pagado': 'Lo que de verdad salió de la Tesorería.',
    'capitulos': 'Servicios personales (1000), materiales (2000), servicios generales (3000), transferencias (4000), bienes muebles, inmuebles e intangibles (5000), inversión pública (6000), inversiones financieras (7000), participaciones (8000) y deuda (9000).',
    'gastos_totales': 'Todo lo que costó operar el año: funcionamiento, transferencias, intereses, depreciación y otras pérdidas.',
    'resultado': 'Ingresos menos gastos: si es positivo es ahorro; si es negativo, desahorro.',
    'flujo_operacion': 'El efectivo que dejó (o se llevó) la operación de todos los días.',
    'flujo_inversion': 'El efectivo que se fue en obra, equipo y otros activos, menos lo que se recuperó al venderlos.',
    'flujo_financiamiento': 'El efectivo que entró por deuda contratada, menos lo que salió para pagar capital.',
    'efectivo_final': 'Con cuánto dinero en caja y bancos cerró el Gobierno Federal el año.',
    'activo': 'Lo que el Gobierno Federal tiene: efectivo, derechos de cobro, inmuebles, infraestructura, inversiones.',
    'pasivo': 'Lo que el Gobierno Federal debe: deuda pública, proveedores, pensiones y otras obligaciones.',
    'patrimonio': 'La diferencia entre lo que tiene y lo que debe.',
}


def _renglon(c, ref_cp):
    """Una cifra de la Cuenta Publica: con monto y documento, o pendiente con su porque."""
    if c['mdp'] is not None:
        return ('<li class="er-cifra er-ok"><span class="er-cifra-n">%s</span><b class="er-cifra-v">%s</b>%s'
                '<p class="er-cifra-f">%s %s %s</p>%s</li>' % (
                    c['concepto'], mdp(c['mdp']), chip(c['estado']),
                    c['fuente'], ref_cp, doc(c['url']),
                    ('<p class="er-cifra-nota">%s</p>' % c['nota']) if c.get('nota') else ''))
    return ('<li class="er-cifra er-falta"><span class="er-cifra-n">%s</span><b class="er-cifra-v">—</b>%s'
            '<p class="er-cifra-que">%s</p><p class="er-cifra-f">%s %s</p></li>' % (
                c['concepto'], chip('pendiente', PEND_CP), QUE_ES.get(c['id'], ''), c['motivo'], doc(c['url'], 'Dónde está ↗')))


def construir(base, ref, glos):
    cf = base['cuentaFederal2024']
    eco = base['cuentas_ecologicas']
    cif = cf['cifras']
    por = {c['id']: c for c in cif}
    ref_cp = ref('ref-shcp-cuentapublica')
    ref_lgcg = ref('ref-lgcg')
    ok = [c for c in cif if c['mdp'] is not None]
    # Becas con monto oficial: aprobado y devengado.
    mir = cf['evaluacion_social_mir']
    con_monto = [m for m in mir if m['estado_montos'] == 'oficial']

    # --- Cabecera: la empresa y el gobierno, lado a lado ---
    espejo = ''.join('<li><span class="er-esp-ico" aria-hidden="true">%s</span><span class="er-esp-emp">%s</span>'
                     '<span class="er-esp-fl" aria-hidden="true">➔</span><span class="er-esp-gob">%s</span></li>' % x for x in (
                         ('📑', 'Estado de pérdidas y ganancias', 'Estado de actividades'),
                         ('🏛️', 'Balance general', 'Estado de situación financiera'),
                         ('💵', 'Flujo de efectivo', 'Estado de flujos de efectivo'),
                         ('📊', 'Presupuesto del año', 'Los momentos del gasto: aprobado a pagado')))
    avance = len(ok) * 100.0 / len(cif)
    cab = '''<div class="er-cab">
          <div class="er-espejo">
            <p class="er-espejo-tit">Si el Gobierno Federal fuera una empresa…</p>
            <ul class="er-esp">%s</ul>
            <p class="er-txt">Así como una empresa rinde sus estados financieros, el Gobierno Federal rinde los suyos cada año en la %s, con las reglas de la Ley General de Contabilidad Gubernamental (art. 46) %s. Aquí se lee la de <b>2024</b>, Tomo II: los tres Poderes y los órganos autónomos %s.</p>
          </div>
          <div class="er-avance">
            <p class="er-avance-tit">Cuánto hemos cotejado</p>
            <p class="er-avance-n"><b>%d</b> de %d cifras</p>
            <span class="er-avance-b" aria-hidden="true"><span style="width:%.1f%%"></span></span>
            <p class="er-avance-tx">tienen ya su documento a la vista %s. Las demás están en el Tomo II, que Hacienda <b>sí publicó</b>: falta que la plataforma las coteje, y por eso se muestran sin monto %s.</p>
            <p class="er-avance-tx"><small>%d ÷ %d = %.0f%%.</small></p>
          </div>
        </div>''' % (espejo, glos('Cuenta Pública', 'Cuenta Pública'), ref_lgcg, ref_cp,
                     len(ok), len(cif), avance, chip('derivado'), chip('pendiente', PEND_CP), len(ok), len(cif), avance)

    # --- Pestanas ---
    botones = ''.join(
        '<button type="button" class="er-pest" role="tab" id="erPest-%s" aria-controls="erPanel-%s" aria-selected="%s"%s>'
        '<span class="er-pest-ico" aria-hidden="true">%s</span><b>%s</b></button>' % (
            v, v, 'true' if i == 0 else 'false', '' if i == 0 else ' tabindex="-1"', ico, nom)
        for i, (v, ico, nom, _, _) in enumerate(VISTAS))

    def panel(v, cuerpo):
        _, ico, nom, sub, txt = next(x for x in VISTAS if x[0] == v)
        return ('<section class="er-panel" role="tabpanel" id="erPanel-%s" aria-labelledby="erPest-%s" tabindex="0">'
                '<h2 class="er-panel-tit"><span aria-hidden="true">%s</span> %s <small>%s</small></h2>'
                '<p class="er-txt">%s</p>%s</section>' % (v, v, ico, nom, sub, txt, cuerpo))

    def lista(v):
        return '<ol class="er-cifras">%s</ol>' % ''.join(_renglon(c, ref_cp) for c in cif if c['vista'] == v)

    # Presupuesto: los cinco momentos como una escalera.
    momentos = ['aprobado', 'modificado', 'devengado', 'ejercido', 'pagado']
    escalera = '<ol class="er-momentos">%s</ol>' % ''.join(
        '<li class="%s"><span class="er-mom-n">%d</span><b>%s</b><span class="er-mom-v">%s</span></li>' % (
            'er-ok' if por[m]['mdp'] is not None else 'er-falta', i + 1, m.capitalize(),
            mdp(por[m]['mdp']) if por[m]['mdp'] is not None else chip('pendiente', PEND_CP))
        for i, m in enumerate(momentos))
    p_pres = panel('presupuesto', escalera + '<p class="er-pie">Los cinco %s del gasto neto total 2024. Solo el aprobado tiene ya su cifra cotejada.</p>' % glos(
        'Momentos Contables del Gasto (Aprobado, Modificado, Devengado y Ejercido)', 'momentos') + lista('presupuesto'))

    # Estado de actividades: el «¿Cuanto crees?» de los intereses.
    ing, inte = por['ingresos_gestion'], por['intereses_deuda']
    de100 = inte['mdp'] / ing['mdp'] * 100
    adivina = '''<div class="er-adivina" id="erAdivina" data-real="%.2f">
            <p class="er-adivina-tit">🎯 ¿Cuánto crees?</p>
            <p class="er-txt">En 2024 el Gobierno Federal recaudó <b>%s</b> por la gestión: impuestos, derechos, productos y aprovechamientos. De cada <b>$100</b> de esos ingresos, ¿cuántos crees que se fueron solo en <b>intereses de la deuda</b>?</p>
            <div class="er-adivina-mando">
              <label for="erAdivinaR">Tu respuesta: <b id="erAdivinaV">$10</b> de cada $100</label>
              <input type="range" id="erAdivinaR" min="0" max="50" step="1" value="10">
              <button type="button" class="er-adivina-btn" id="erAdivinaBtn">Revelar</button>
            </div>
            <div class="er-adivina-res" id="erAdivinaRes" role="status">
              <div class="er-moneda" aria-hidden="true"><span class="er-moneda-int" style="width:%.2f%%"></span></div>
              <p class="er-adivina-real">De cada $100: <b>$%.2f</b> se pagaron en intereses %s</p>
              <p class="er-pie">%s ÷ %s × 100. Son <b>solo intereses</b>: el capital que se abona no es gasto del estado de actividades, porque reduce lo que se debe.</p>
            </div>
          </div>''' % (de100, mdp(ing['mdp']), de100, de100, chip('derivado'), mdp(inte['mdp']), mdp(ing['mdp']))
    p_act = panel('actividades', adivina + lista('actividades'))

    p_flu = panel('flujos', '<div class="er-corrientes" aria-hidden="true"><span>🔁 Operación</span><span>🏗️ Inversión</span><span>🏦 Financiamiento</span><span>🧾 Efectivo al cierre</span></div>' + lista('flujos'))

    # Situacion financiera: la ecuacion.
    ecuacion = '<p class="er-ecuacion"><span>🏛️ Activo</span><b>=</b><span>💳 Pasivo</span><b>+</b><span>🧱 Patrimonio</span></p>'
    p_sit = panel('situacion', ecuacion + lista('situacion'))

    # Resultados sociales: becas con aprobado y devengado, y las pendientes.
    tarjetas = []
    for m in mir:
        if m['estado_montos'] == 'oficial':
            pct = m['devengado_mdp'] / m['aprobado_mdp'] * 100
            tarjetas.append(
                '<li class="er-prog er-ok"><p class="er-prog-n"><b>%s</b> <small>%s · Ramo %s</small></p>'
                '<div class="er-prog-b"><span class="er-prog-ap" title="Aprobado"></span><span class="er-prog-dev" style="width:%.1f%%" title="Devengado"></span></div>'
                '<p class="er-prog-v"><span>Aprobado <b>%s</b></span><span>Devengado <b>%s</b></span>%s</p>'
                '<p class="er-prog-pct">Se devengó el <b>%.1f%%</b> de lo aprobado %s <small>(%s ÷ %s × 100)</small></p>'
                '<p class="er-cifra-f">%s %s</p></li>' % (
                    m['programa'], m['clave'], m['ramo'], pct, mdp(m['aprobado_mdp']), mdp(m['devengado_mdp']), chip('oficial'),
                    pct, chip('derivado'), mdp(m['devengado_mdp']), mdp(m['aprobado_mdp']), m['fuente_montos'], doc(m['url'])))
        else:
            clave = 'imss-bienestar' if 'IMSS' in m['programa'] else m['clave'].lower()
            tarjetas.append(
                '<li class="er-prog er-falta"><p class="er-prog-n"><b>%s</b>%s</p>'
                '<p class="er-prog-v"><span>Aprobado y devengado: %s</span></p><p class="er-cifra-f">%s %s</p></li>' % (
                    m['programa'], (' <small>%s · Ramo %s</small>' % (m['clave'], m['ramo'])) if m['clave'] != 'pendiente' else '',
                    chip('pendiente', 'prog-montos-' + clave), m['motivo_montos'], doc(m['url'], 'Dónde está ↗')))
    social = ('<ul class="er-progs">%s</ul>'
              '<p class="er-pie">Aprobado es lo que autorizó la Cámara de Diputados; devengado, lo que el gobierno reconoció como obligación de pago al cierre del año. '
              'La diferencia no es ahorro ni desvío: es una modificación del presupuesto que la Cuenta Pública debe explicar.</p>'
              '<p class="er-falta-res">%s <b>¿Y qué lograron?</b> %s %s</p>') % (
        ''.join(tarjetas), chip('pendiente', 'prog-resultados'), mir[0]['motivo_resultados'], doc(mir[0]['url_resultados'], 'Transparencia Presupuestaria ↗'))
    ct, gpa = eco['ctada'], eco['gasto_proteccion_ambiental']
    social += '''<h3 class="er-sub">🌳 Lo que el país gasta de su naturaleza (INEGI, 2024)</h3>
          <div class="er-eco">
            <div class="er-eco-c er-eco-costo"><span>Costo por agotamiento y degradación ambiental %s</span><b>%s</b><small>%s%% del PIB de 2024</small></div>
            <div class="er-eco-c er-eco-prot"><span>Gasto público en protección ambiental %s</span><b>%s</b><small>%s%% del PIB de 2024</small></div>
          </div>
          <p class="er-pie">Por cada peso que el sector público destinó a proteger el ambiente, el capital natural resintió <b>$%.2f</b> de deterioro %s (%s ÷ %s). %s %s Es contexto nacional: no se resta del presupuesto. <a href="herramienta-ambiente-pib.html">Las cuentas ecológicas completas: Herramientas › Costo ambiental › El PIB no alcanza ➔</a></p>''' % (
        chip(ct['estado']), mdp(ct['total_mdp'], 0), ct['pct_pib'], chip(gpa['estado']), mdp(gpa['monto_mdp'], 0), gpa['pct_pib'],
        gpa['ratio_dano_sobre_gasto'], chip(gpa['ratio_estado']), mdp(ct['total_mdp'], 0), mdp(gpa['monto_mdp'], 0),
        'INEGI, Cuentas Económicas y Ecológicas de México 2024 (1 de diciembre de 2025).', ref('ref-ceem-2024'))
    p_soc = panel('social', social)

    c = cf['conciliacion']
    pasos = '<ol class="er-concil">%s</ol>' % ''.join(
        '<li class="%s"><span class="er-concil-n">%d</span><span class="er-concil-t">%s</span><span class="er-concil-v">%s</span></li>' % (
            'er-concil-fin' if t.startswith('Igual') else ('er-concil-menos' if t.startswith('Menos') else ('er-concil-mas' if t.startswith('Más') else '')),
            i + 1, t, chip('pendiente', PEND_CP)) for i, t in enumerate(c['pasos']))
    p_con = panel('conciliacion', pasos + '<p class="er-pie">El método es el de la Ley General de Contabilidad Gubernamental %s. Los importes de 2024 se retiraron el 10-10-2026 porque no tenían cotejo. %s %s</p>' % (
        ref_lgcg, c['motivo'], doc(c['url'], 'Dónde está ↗')))

    correccion = ('<details class="er-correccion"><summary>📝 Corrección del 10-10-2026: por qué hay tantos pendientes</summary>'
                  '<p>%s</p><p>Alcance: %s</p></details>' % (cf['correccion'], cf['alcance']))
    otra = ('<p class="er-otra">🧾 ¿Quieres ver 2024 junto a 2026 y 2027, en las mismas unidades? '
            '<a href="estado-de-cuenta.html">Abre el Estado de Cuenta Cívico ➔</a></p>')

    return '''<div class="er" id="erRaiz">
        %s
        <div class="er-pests" role="tablist" aria-label="Los estados financieros de 2024">%s</div>
        <div class="er-paneles">
        %s
        </div>
        %s
        %s
      </div>''' % (cab, botones, '\n        '.join([p_pres, p_act, p_flu, p_sit, p_soc, p_con]), otra, correccion)
