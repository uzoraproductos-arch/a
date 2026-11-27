# -*- coding: utf-8 -*-
"""«¿Hasta cuándo guardas tus papeles?», el calendario de conservación
(19-11-2026; entrega 1 del servicio «Gobernanza documental y cumplimiento»,
pedido del autor: «la forma de proteger la información» y, tras proponerlo,
«sí, arranca»).

Qué hace: dice, documento por documento, cuánto tiempo obliga la ley a
guardarlo, desde cuándo se cuenta y, para un ejercicio, la fecha mínima hasta
la que se guarda. Manda el plazo más largo de las leyes que te alcanzan, y al
vencer, los datos personales se suprimen (no se guardan «por si acaso»).

Cada renglón se cotejó el 19-11-2026 contra el texto vigente de la Cámara de
Diputados (huella SHA-256 de cada PDF en LEYES):

  - CFF, art. 30: 5 años desde la declaración con que se relacionan; actos con
    efectos que duran, desde la del último ejercicio con efectos; en recurso o
    juicio, desde que queda firme; actas, capital, fusión, dividendos y las
    declaraciones, mientras subsista la sociedad. Art. 67: la facultad del SAT
    dura 5 años, y 10 si no llevas o no conservas la contabilidad o no
    presentas una declaración.
  - LISR, art. 9 (las morales declaran dentro de los tres meses siguientes al
    cierre) y art. 150 (las físicas, en abril).
  - Código de Comercio, arts. 38, 46, 46 bis y 49: el comerciante, 10 años como
    mínimo, en papel o en medios electrónicos con la norma de conservación.
  - LSS, art. 15, fr. II: nóminas y listas de raya, los 5 años siguientes al de
    su fecha.
  - LFT, art. 804: contratos, mientras dure la relación y un año después;
    recibos, asistencia y pagos, el último año y uno después de terminar.
  - LFPIORPI, art. 18, fr. IV (reformada DOF 16-07-2025): actividades
    vulnerables, al menos 10 años desde la operación (salvo la fr. XIV del
    art. 17, comercio exterior).
  - LFPDPPP (DOF 20-03-2025), arts. 3, fr. III, 10 y 24: suprimir al terminar
    el plazo, previo bloqueo; los datos de incumplimiento, a los 72 meses.
  - Ley General de Archivos, art. 4, frs. XIII y XLVI: en el gobierno lo fija el
    catálogo de disposición documental de cada sujeto obligado.

**Las reglas son `oficial` (dicen la ley); las fechas, `derivado`**: es nuestra
cuenta, con la lectura dicha en cada renglón. No es asesoría ni sustituye a tu
contador o a tu abogado. La cuenta la hace el navegador
(`insp-conservacion.js`); `vence()` es su gemela y `--prueba` las compara.
Lo llama apartados.insp_nativa() (INSP_NATIVAS['inspconservacion']).
"""
import datetime
import html
import json
import os
import subprocess
import sys

from presupuesto_modulos import chip

ESTILOS = ['cc-inmueble.css', 'insp-conservacion.css']
SCRIPTS = ['insp-conservacion.js']
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESDE = 2015  # el selector de ejercicio

_D = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/'
LEYES = {
    'cff': ('Código Fiscal de la Federación', 'CFF', 'DOF 09-04-2026', _D + 'CFF.pdf',
            'be7427b20d3552775ab42018f8f87578078770095bf8cf46322c25e36ee3aa7d'),
    'lisr': ('Ley del Impuesto sobre la Renta', 'LISR', 'DOF 01-04-2024', _D + 'LISR.pdf',
             '803c2875c09c751c1966b8eb4dca99f460b237da4ef67ee04b4fa325d8c2f786'),
    'ccom': ('Código de Comercio', 'CCom', 'DOF 14-11-2025', _D + 'CCom.pdf',
             'b99bbf981434011b6351ef308922fea90f6f0f8777b113183cf1737840c5bbef'),
    'lss': ('Ley del Seguro Social', 'LSS', 'DOF 15-01-2026', _D + 'LSS.pdf',
            '8a28a16e1dce1f8e666f4cce5ed19745bc912b2ab1ca49787d5d4bef229398ed'),
    'lft': ('Ley Federal del Trabajo', 'LFT', 'DOF 14-05-2026', _D + 'LFT.pdf',
            '12f09393a1951a91c3f57f579bf611b034edf1a5f78cdbfb828e23ff3a9acbf7'),
    'lfpiorpi': ('Ley Federal para la Prevención e Identificación de Operaciones con Recursos de Procedencia Ilícita', 'LFPIORPI',
                 'DOF 16-07-2025', _D + 'LFPIORPI.pdf', '2e35228bd3100a3a137f313359833c4836f2b4b6d4e52e1ce4fe58a970cd768f'),
    'lfpdppp': ('Ley Federal de Protección de Datos Personales en Posesión de los Particulares (DOF 20-03-2025)', 'LFPDPPP',
                'DOF 14-11-2025', _D + 'LFPDPPP.pdf', '04d67464e1efc0472040e2ff8012ced52c73ff4fc3573c8e2d3477fd976359c6'),
    'lga': ('Ley General de Archivos', 'LGA', 'DOF 14-11-2025', _D + 'LGA.pdf',
            '2f931111ab2745aa5a3b2ef0a99dc5beaf73d78f7674f2d90b4462319c1fc688'),
}

# Cada renglón: id, ícono, a quién alcanza (todos, moral, comerciante, patron,
# pld, gobierno), qué se guarda, cuánto, desde cuándo, ley y artículo, lo que la
# ley dice entre comillas (copiado del texto vigente) y el punto ciego.
# `cuenta` dice cómo saca la fecha el navegador (vence()).
REGLAS = [
    dict(id='fiscal', ic='🧾', quien='todos', cuenta='decl',
         doc='Tu contabilidad y los papeles de tus impuestos: facturas que emites y recibes, estados de cuenta, pólizas, papeles de trabajo.',
         plazo='5 años', desde='Desde el día en que presentaste, o debiste presentar, la declaración con que se relacionan: para lo del año, la anual.',
         ley='cff', art='art. 30, tercer párrafo',
         cita='deberán conservarse durante un plazo de cinco años, contado a partir de la fecha en la que se presentaron o debieron haberse presentado las declaraciones con ellas relacionadas',
         ojo='Los 5 años no se cuentan desde la fecha de la factura: una factura de enero de 2026 entra a la anual de 2026, que se presenta en 2027, y de ahí corren los 5.'),
    dict(id='efectos', ic='⏳', quien='todos', cuenta='texto',
         doc='Lo que tiene efectos fiscales por varios años: lo que deprecias, las pérdidas que vas restando, una inversión que deduces poco a poco.',
         plazo='5 años', desde='Desde la declaración del último ejercicio en que ese acto todavía tuvo efectos.',
         ley='cff', art='art. 30, tercer párrafo',
         cita='el plazo de referencia comenzará a computarse a partir del día en el que se presente la declaración fiscal del último ejercicio en que se hayan producido dichos efectos',
         ojo='La factura de una camioneta que deprecias durante cuatro años se guarda hasta 5 años después de la anual del último de esos cuatro.'),
    dict(id='juicio', ic='⚖️', quien='todos', cuenta='texto',
         doc='Lo que está en un recurso o en un juicio (contra el SAT o contra quien sea, si toca algo fiscal).',
         plazo='5 años', desde='Desde que queda firme la resolución que le pone fin.',
         ley='cff', art='art. 30, tercer párrafo',
         cita='el plazo para conservarla se computará a partir de la fecha en la que quede firme la resolución que les ponga fin',
         ojo='Un juicio largo detiene el reloj: no destruyas nada de un asunto abierto, aunque ya pasen 5 años desde la declaración.'),
    dict(id='sociedad', ic='🏛️', quien='moral', cuenta='siempre',
         doc='Acta constitutiva, actas de aumento o disminución de capital, de fusión o escisión, constancias de dividendos, los ajustes de los arts. 22 y 23 de la LISR y '
             'las declaraciones de pagos provisionales y del ejercicio, con sus estados de cuenta y avalúos.',
         plazo='Siempre', desde='Por todo el tiempo en que exista la sociedad.',
         ley='cff', art='art. 30, tercer a sexto párrafos',
         cita='dicha documentación deberá conservarse por todo el tiempo en el que subsista la sociedad o contrato de que se trate',
         ojo='Las declaraciones de una sociedad no se tiran a los 5 años: se guardan mientras la sociedad exista. Lo mismo el soporte de cada aumento de capital.'),
    dict(id='comercio', ic='🏪', quien='comerciante', cuenta='diez',
         doc='Los libros, registros y documentos de tu negocio y los comprobantes originales de tus operaciones.',
         plazo='10 años como mínimo', desde='La ley no dice desde cuándo; contamos desde la fecha del documento (lo de este año, desde el 31 de diciembre).',
         ley='ccom', art='arts. 38 y 46',
         cita='Todo comerciante está obligado a conservar los libros, registros y documentos de su negocio por un plazo mínimo de diez años',
         ojo='Si eres comerciante (toda sociedad mercantil lo es), el Código de Comercio pide el doble que el SAT: 10 años, no 5. Y sus herederos tienen la misma obligación.'),
    dict(id='contratos', ic='✍️', quien='comerciante', cuenta='diez',
         doc='Los originales de cartas, correos, mensajes de datos o cualquier documento donde consten contratos, convenios o compromisos.',
         plazo='10 años como mínimo', desde='Contamos desde la fecha del documento.',
         ley='ccom', art='art. 49',
         cita='están obligados a conservar por un plazo mínimo de diez años los originales de aquellas cartas, telegramas, mensajes de datos o cualesquiera otros documentos en que se consignen contratos, convenios o compromisos',
         ojo='Un correo con el que cerraste un trato cuenta como original: si es electrónico, tiene que quedar íntegro e inalterado desde que se generó.'),
    dict(id='imss', ic='🏥', quien='patron', cuenta='anio5',
         doc='Nóminas y listas de raya con los días trabajados y los salarios de tus trabajadores.',
         plazo='5 años', desde='Los cinco años siguientes al de su fecha: lo de este año, hasta el 31 de diciembre del quinto año siguiente.',
         ley='lss', art='art. 15, fr. II',
         cita='Es obligatorio conservar estos registros durante los cinco años siguientes al de su fecha',
         ojo='Aquí el reloj corre por año calendario, no desde una declaración.'),
    dict(id='lft_contrato', ic='📃', quien='patron', cuenta='fin1',
         doc='Los contratos individuales de trabajo (si no hay contrato colectivo o contrato-ley).',
         plazo='Mientras dure la relación y 1 año después', desde='Desde que termina la relación de trabajo.',
         ley='lft', art='art. 804, fr. I y último párrafo',
         cita='deberán conservarse mientras dure la relación laboral y hasta un año después',
         ojo='Si no lo exhibes en un juicio, se presumen ciertos los hechos que diga quien te demanda (LFT, art. 805).'),
    dict(id='lft_pagos', ic='💵', quien='patron', cuenta='fin1',
         doc='Recibos de salario, controles de asistencia y comprobantes de PTU, vacaciones, aguinaldo, primas y cuotas de seguridad social.',
         plazo='El último año y 1 año después', desde='Desde que termina la relación de trabajo.',
         ley='lft', art='art. 804, frs. II a IV y último párrafo',
         cita='durante el último año y un año después de que se extinga la relación laboral',
         ojo='La LFT pide poco, pero los mismos recibos son nómina para el IMSS (5 años) y comprobantes para el SAT (5 años desde la anual): manda el plazo más largo.'),
    dict(id='pld', ic='🛡️', quien='pld', cuenta='diez',
         doc='El expediente de cada actividad vulnerable: la identificación de tu cliente, su beneficiario controlador, los registros y la correspondencia de la operación.',
         plazo='10 años como mínimo', desde='Desde la fecha en que se realizó la actividad vulnerable; lo de este año, a más tardar desde el 31 de diciembre.',
         ley='lfpiorpi', art='art. 18, fr. IV (reformada DOF 16-07-2025)',
         cita='por al menos un plazo de diez años contado a partir de la fecha de la realización de la Actividad Vulnerable',
         ojo='Esta fracción cambió en julio de 2025: revisa contra el texto vigente lo que ya tenías calendarizado. Un recurso o un juicio interrumpe el plazo. '
             'Los agentes y agencias aduanales (art. 17, fr. XIV) siguen su propia regla.'),
    dict(id='datos', ic='🔒', quien='todos', cuenta='texto',
         doc='Los datos personales de tus clientes, trabajadores o usuarios que vienen en todo lo anterior.',
         plazo='Solo el plazo que te obliga', desde='Al terminar la finalidad y el plazo de conservación: bloqueo (igual a la prescripción de las acciones) y después supresión.',
         ley='lfpdppp', art='arts. 3, fr. III, 10 y 24',
         cita='deberán ser suprimidos previo bloqueo, en su caso, y una vez que concluya el plazo de conservación de los mismos',
         ojo='Guardar de más también es incumplir: «por si acaso» no es una finalidad. Cuando vence el plazo más largo de arriba, toca bloquear y luego suprimir.'),
    dict(id='impago', ic='📉', quien='todos', cuenta='texto',
         doc='Los datos de que alguien no cumplió un contrato contigo (un adeudo, un impago).',
         plazo='Se eliminan a los 72 meses', desde='Desde la fecha en que ocurrió el incumplimiento.',
         ley='lfpdppp', art='art. 10, tercer párrafo',
         cita='El responsable estará obligado a eliminar los datos relativos al incumplimiento de obligaciones contractuales, una vez que transcurra un plazo de setenta y dos meses',
         ojo='Este es un plazo máximo, no mínimo: pasados los 72 meses, ese dato ya no se puede conservar.'),
    dict(id='gobierno', ic='🏢', quien='gobierno', cuenta='texto',
         doc='Los archivos de una dependencia, un municipio o cualquier sujeto obligado.',
         plazo='Lo fija su catálogo', desde='La vigencia documental y el plazo de conservación de cada serie, en su catálogo de disposición documental.',
         ley='lga', art='art. 4, frs. XIII y XLVI',
         cita='Catálogo de disposición documental: Al registro general y sistemático que establece los valores documentales, la vigencia documental, los plazos de conservación y la disposición documental',
         ojo='En el gobierno no hay un plazo único: un documento sin catálogo no se puede dar de baja.'),
]

# Cómo se pregunta por cada papel en el chat (Ronda 32, 27-11-2026, pedido del autor: que la respuesta
# conteste el plazo y no describa la página). Por regla: la expresión que la reconoce (sin acentos, igual en
# Python y en JavaScript) y las reglas que conviene decir junto a ella, porque manda el plazo más largo.
# **Una regla nueva de REGLAS necesita aquí su renglón**, o la generación se detiene. El orden importa:
# lo más específico va primero.
PAL = [
    ('lft_contrato', r'contratos? (individual(es)? )?de trabajo|contratos? laboral', ['lft_pagos']),
    ('lft_pagos', r'recibos? de (nomina|salario|sueldo|pago)|control(es)? de asistencia|aguinaldo|vacaciones|\bptu\b', ['imss', 'fiscal']),
    ('imss', r'nomina|listas? de raya|\bimss\b', ['lft_pagos', 'fiscal']),
    ('pld', r'actividad(es)? vulnerable|lavado|\bpld\b|expedientes? de (mis |los |tus )?clientes|beneficiario controlador', []),
    ('impago', r'impago|adeudo|incumplimiento|buro de credito', []),
    ('datos', r'datos personales', []),
    ('sociedad', r'acta constitutiva|actas? de asamblea|aumento de capital|dividendos', []),
    ('juicio', r'juicio|litigio|demanda|recurso de revocacion', []),
    ('efectos', r'depreci|perdidas? fiscal|activos? fijos?', []),
    ('contratos', r'contratos?|convenios?|correos?', []),
    ('gobierno', r'dependencia|ayuntamiento|sujeto obligado|archivos? (publico|del gobierno|municipal)', []),
    ('comercio', r'libros|comerciante|de mi negocio', ['fiscal']),
    ('fiscal', r'factura|cfdi|contabilidad|estados? de cuenta|poliza|comprobantes?|declaraci|impuestos', ['comercio']),
]


def chat():
    """Las reglas para el chat: el plazo de cada papel con su ley, su artículo y su cita. Sin cifras propias."""
    ids = [r['id'] for r in REGLAS]
    pal = [x[0] for x in PAL]
    if sorted(ids) != sorted(pal):
        raise SystemExit('insp_conservacion: cada regla de REGLAS necesita su renglón en PAL (faltan o sobran: %s)'
                         % ', '.join(sorted(set(ids) ^ set(pal))))
    for k, _, junto in PAL:
        for j in junto:
            if j not in ids:
                raise SystemExit('insp_conservacion: PAL de «%s» cita una regla que no existe: %s' % (k, j))
    por = {r['id']: r for r in REGLAS}
    return [{'id': k, 're': rx, 'junto': junto, 'ic': por[k]['ic'], 'doc': por[k]['doc'], 'plazo': por[k]['plazo'],
             'desde': por[k]['desde'], 'ley': LEYES[por[k]['ley']][1], 'url': LEYES[por[k]['ley']][3], 'art': por[k]['art'],
             'cita': por[k]['cita'], 'ojo': por[k]['ojo']} for k, rx, junto in PAL]


# Lo que casi nadie dice (los puntos ciegos de la conversación «guárdalo 5 años»).
CIEGOS = [
    ('Los 5 años no empiezan con la factura', 'Empiezan con la declaración anual del ejercicio: lo de 2026 se guarda, como mínimo, hasta 2032.', 'cff', 'art. 30'),
    ('Si no conservas, el SAT tiene el doble', 'Su facultad de revisarte dura 5 años; dura 10 si no llevas tu contabilidad, no la conservas el plazo que marca la ley o no presentas una declaración.', 'cff', 'art. 67'),
    ('El comerciante guarda 10, no 5', 'El Código de Comercio pide 10 años como mínimo para los libros, los comprobantes y los contratos.', 'ccom', 'arts. 38, 46 y 49'),
    ('Las declaraciones de una sociedad, siempre', 'Junto con el acta constitutiva y cada movimiento de capital, mientras exista la sociedad.', 'cff', 'art. 30'),
    ('Manda el plazo más largo', 'Un mismo recibo de nómina es documento laboral (1 año después de terminar), registro del IMSS (5 años) y comprobante fiscal (5 años desde la anual).', 'lft', 'art. 804'),
    ('Guardar de más también es incumplir', 'Los datos personales se suprimen, previo bloqueo, cuando termina el plazo; los de un impago, a los 72 meses.', 'lfpdppp', 'art. 10'),
    ('Lo digital vale si no se altera', 'En papel o en electrónico, con la norma oficial sobre digitalización y conservación de mensajes de datos; lo firmado con sello digital, con las reglas del SAT.', 'ccom', 'arts. 46 bis y 49'),
]

PERFILES = [('moral', 'Soy una sociedad (persona moral)'), ('comerciante', 'Tengo un negocio: soy comerciante'),
            ('patron', 'Tengo trabajadores'), ('pld', 'Hago una actividad vulnerable (LFPIORPI)')]


def esc(t):
    return html.escape(str(t))


def ley_liga(k, art=''):
    n, corto, ref, url, sha = LEYES[k]
    return '<a href="%s" title="%s, última reforma %s">%s%s</a>' % (esc(url), esc(n), esc(ref), esc(corto), (', ' + esc(art)) if art else '')


# ---- La cuenta (gemela de calcula() de insp-conservacion.js) ----

def _mas_anios(f, n):
    try:
        return f.replace(year=f.year + n)
    except ValueError:  # 29 de febrero
        return f.replace(year=f.year + n, day=28)


def vence(fisica, anio, presento=None, fin=None):
    """Fechas mínimas para lo del ejercicio `anio` (ISO, o None si no aplica a
    una fecha). `presento` y `fin` son fechas ISO opcionales."""
    base = datetime.date(anio + 1, 4, 30) if fisica else datetime.date(anio + 1, 3, 31)  # LISR arts. 150 y 9
    if presento:
        base = max(base, datetime.date.fromisoformat(presento))
    out = {'decl': base.isoformat(), 'fiscal': _mas_anios(base, 5).isoformat(),
           'diez': datetime.date(anio + 10, 12, 31).isoformat(), 'anio5': datetime.date(anio + 5, 12, 31).isoformat(),
           'fin1': _mas_anios(datetime.date.fromisoformat(fin), 1).isoformat() if fin else None}
    return out


def datos():
    return {'reglas': [{k: r[k] for k in ('id', 'quien', 'cuenta')} for r in REGLAS], 'desde': DESDE,
            'leyes': {k: [v[1], v[3]] for k, v in LEYES.items()}}


def construir(base, ref):
    hoy = datetime.date.today().year
    anios = ''.join('<option value="%d"%s>%d</option>' % (a, ' selected' if a == hoy - 1 else '', a) for a in range(hoy, DESDE - 1, -1))
    perf = ''.join('<label class="cs-op"><input type="checkbox" name="csP" value="%s"> %s</label>' % (k, esc(t)) for k, t in PERFILES)
    filas = ''.join(
        '<tr data-q="{quien}" id="cs-{id}"><th scope="row"><span aria-hidden="true">{ic}</span> {doc}</th><td><b>{plazo}</b><br><small>{desde}</small></td>'
        '<td>{liga}<details class="cs-cita"><summary>Qué dice</summary><blockquote>«…{cita}…»</blockquote><p>👁️ {ojo}</p></details></td></tr>'.format(
            quien=r['quien'], id=r['id'], ic=r['ic'], doc=esc(r['doc']), plazo=esc(r['plazo']), desde=esc(r['desde']),
            liga=ley_liga(r['ley'], r['art']), cita=esc(r['cita']), ojo=esc(r['ojo'])) for r in REGLAS)
    ciegos = ''.join('<li><b>%s.</b> %s <span class="cs-ley">(%s)</span></li>' % (esc(t), esc(x), ley_liga(k, a)) for t, x, k, a in CIEGOS)
    fuentes = ' · '.join('<a href="%s">%s</a>, última reforma %s (huella SHA-256 <code>%s…</code>)' % (esc(v[3]), esc(v[0]), esc(v[2]), v[4][:12])
                         for v in LEYES.values())
    return '''<div class="ci cs" id="csRaiz">
  <section class="ci-arranque" aria-labelledby="csTit">
    <p class="ci-kicker">Modo Inspector · gobernanza documental</p>
    <h2 class="ci-grande" id="csTit">¿Hasta cuándo guardas tus papeles?</h2>
    <p class="ci-txt">Facturas, contabilidad, nómina, contratos, expedientes de clientes: cada papel tiene un plazo que dice la ley, y casi nunca es el que se repite. Dinos quién eres y de qué año son, y te damos la <b>fecha mínima hasta la que se guarda cada uno</b>, con su artículo.</p>
    <p class="ci-privado">🔒 La cuenta la hace tu navegador: lo que eliges no se guarda ni se envía.</p>
  </section>

  <form class="ci-form" id="csForm" novalidate>
    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">1</span> Quién eres</legend>
      <div class="cs-ops">{perf}</div>
      <p class="ci-pista">Si no marcas nada, te contestamos como persona física sin negocio ni trabajadores. Una sociedad mercantil también es comerciante (Código de Comercio, art. 3o.): marca las dos.</p>
    </fieldset>
    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">2</span> De qué año son tus papeles</legend>
      <label class="ci-et" for="csAnio">Ejercicio fiscal (año calendario)</label>
      <select class="ci-in" id="csAnio">{anios}</select>
      <label class="ci-et" for="csPres">Si presentaste la anual después del plazo, el día en que la presentaste <small>(opcional)</small></label>
      <input class="ci-in" id="csPres" type="date">
      <label class="ci-et" for="csFin">Si terminó la relación con un trabajador, el día en que terminó <small>(opcional)</small></label>
      <input class="ci-in" id="csFin" type="date">
    </fieldset>
    <p class="ci-acciones"><button type="submit" class="ci-boton">Dame mi calendario</button></p>
  </form>

  <section class="ci-res" id="csRes" aria-live="polite" hidden>
    <h2 class="ci-tit"><span class="ci-n" aria-hidden="true">3</span> Tu calendario {chip_d}</h2>
    <div class="ci-total" id="csTotal"></div>
    <div class="ci-tabla-caja"><table class="ci-tabla"><caption>Guárdalo, como mínimo, hasta</caption>
      <thead><tr><th scope="col">Qué</th><th scope="col">Hasta</th><th scope="col">Por qué</th></tr></thead>
      <tbody id="csFechas"></tbody></table></div>
    <p class="ci-nota" id="csNota"></p>
  </section>

  <section class="ci-aviso" aria-labelledby="csLeyTit">
    <h2 class="ci-tit" id="csLeyTit"><span aria-hidden="true">📚</span> Lo que dice la ley, papel por papel {chip_o}</h2>
    <div class="ci-tabla-caja"><table class="ci-tabla cs-reglas"><caption>Los plazos de conservación en México</caption>
      <thead><tr><th scope="col">Qué se guarda</th><th scope="col">Cuánto y desde cuándo</th><th scope="col">Dónde lo dice</th></tr></thead>
      <tbody>{filas}</tbody></table></div>
  </section>

  <aside class="ci-aviso" aria-labelledby="csCiegoTit">
    <h2 class="ci-tit" id="csCiegoTit"><span aria-hidden="true">👁️</span> Lo que casi nadie te dice</h2>
    <ol class="ci-lista">{ciegos}</ol>
    <p><b>Lo que esta cuenta no hace:</b> no es asesoría ni sustituye a tu contador o a tu abogado. Las fechas son nuestra lectura de cada artículo (el chip «auditada» lo dice) y no recorren los plazos que caen en día inhábil. No cubre leyes de un sector (bancos, seguros, salud, aduanas) ni lo que te pida un contrato o una autoridad en un caso concreto, que pueden pedir más. Antes de destruir, revisa que no haya un recurso, un juicio, una revisión del SAT o un acto con efectos que sigan.</p>
    <p class="ci-fuentes">Fuentes, cotejadas el 19-11-2026: {fuentes} {chip_o}.</p>
    <p class="ci-hermanas">Sigue con el Modo Inspector: <a href="herramienta-inspector-factura.html">📑 Lector de facturas CFDI</a> · <a href="herramienta-inspector-padron.html">🛡️ Revisa a tu contraparte</a> · <a href="servicio-gobernanza.html">🗄️ El servicio de gobernanza documental</a></p>
  </aside>
  <script type="application/json" id="csDatos">{datos}</script>
</div>'''.format(perf=perf, anios=anios, filas=filas, ciegos=ciegos, fuentes=fuentes,
                 chip_d=chip('derivado'), chip_o=chip('oficial'),
                 datos=json.dumps(datos(), ensure_ascii=False).replace('</', '<\\/'))


# ---- Prueba: la cuenta del navegador y la de aquí dan lo mismo ----

CASOS = [(True, 2026, None, None), (False, 2026, None, None), (True, 2020, '2021-07-15', '2024-02-29'),
         (False, 2023, '2024-03-15', '2025-06-30'), (True, 2019, None, '2023-12-31')]


def prueba():
    js = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'insp-conservacion.js')
    prog = ("global.window={};global.document={addEventListener:function(){}};require(%s);"
            "var c=%s;console.log(JSON.stringify(c.map(function(x){return window.AuditorConserva.vence(x[0],x[1],x[2],x[3]);})));"
            % (json.dumps(js), json.dumps(CASOS)))
    r = subprocess.run(['node', '-e', prog], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr)
        return 1
    nav = json.loads(r.stdout)
    mal = 0
    for c, n in zip(CASOS, nav):
        py = vence(*c)
        if py != n:
            mal += 1
            print('✗', c, 'Python', py, 'navegador', n)
    # Las reglas: cada una con su ley, su cita y un quién conocido.
    for x in REGLAS:
        if x['ley'] not in LEYES or x['quien'] not in ('todos', 'moral', 'comerciante', 'patron', 'pld', 'gobierno') or len(x['cita']) < 30:
            mal += 1
            print('✗ regla', x['id'])
    # Un caso a mano: persona física, 2026 → anual 30-04-2027 → 30-04-2032.
    if vence(True, 2026)['fiscal'] != '2032-04-30' or vence(False, 2026)['fiscal'] != '2032-03-31':
        mal += 1
        print('✗ el caso a mano no da 2032')
    if mal:
        print('%d diferencias en el calendario de conservación' % mal)
        return 1
    print('✓ Calendario de conservación: %d casos iguales en Python y en el navegador, %d reglas con su ley' % (len(CASOS), len(REGLAS)))
    return 0


if __name__ == '__main__':
    if '--prueba' in sys.argv:
        sys.exit(prueba())
