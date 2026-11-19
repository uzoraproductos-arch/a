# -*- coding: utf-8 -*-
"""«Tu matriz de riesgos documentales» (19-11-2026; entrega 3 del servicio
«Gobernanza documental y cumplimiento», pedido del autor: «entrega 3»).

Qué hace: toma las mismas obligaciones del autodiagnóstico (PREGUNTAS de
insp_cumplimiento.py, que puede llegar ya contestado por la dirección) y las
acomoda en una matriz de 3 × 3: **qué tan probable es fallar** (sale de tu
respuesta: «no» = alta, «no sé» = media, «sí» = baja) por **qué tan grave sería
para ti** (lo eliges tú: bajo, medio o alto). Junto a cada una va lo que la ley
tiene por infracción, con su artículo y su cita al pie de la letra, cotejada el
19-11-2026 contra el texto vigente de la Cámara de Diputados (las mismas huellas
de LEYES de insp_conservacion.py):

  - CFF, art. 81, fr. XLI, y art. 83, frs. III y VI.
  - LSS, art. 304 A, frs. I, II y VII.  LFT, art. 805 (la presunción en juicio).
  - LFPIORPI, art. 53, fr. II.
  - LFPDPPP (DOF 20-03-2025), art. 58, frs. I, V, XI y XIX.
  - Ley General de Archivos, art. 116, fr. VII.

El Código de Comercio no trae aquí una consecuencia citada: el renglón lo dice y
la gravedad la valoras tú. **Ningún monto de multa se escribe**: las multas
cambian con la UMA y se individualizan; se cita el artículo.

**Las obligaciones y sus consecuencias son `oficial`; la matriz es `derivado`**:
tu respuesta y tu valoración, acomodadas con una regla dicha en la página
(probabilidad × gravedad), nunca una calificación, una certificación ni una
auditoría. La cuenta la hace el navegador (`insp-riesgos.js`) y nada se guarda
ni se envía; `matriz()` es su gemela y `--prueba` las compara.
Lo llama apartados.insp_nativa() (INSP_NATIVAS['inspriesgos']).
"""
import html
import json
import os
import subprocess
import sys

from presupuesto_modulos import chip
from insp_conservacion import LEYES, ley_liga
from insp_cumplimiento import PREGUNTAS, PERFILES, AREAS

ESTILOS = ['cc-inmueble.css', 'insp-conservacion.css', 'insp-cumplimiento.css', 'insp-riesgos.css']
SCRIPTS = ['insp-riesgos.js']
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_CFF83 = 'Son infracciones relacionadas con la obligación de llevar contabilidad'
_PLD = ('lfpiorpi', 'art. 53, fr. II', 'Se aplicará la multa correspondiente a quienes: […] Incumplan con cualquiera de las obligaciones establecidas en el artículo 18 de esta Ley')
_LGA = ('lga', 'arts. 116, fr. VII, y 117', 'Cualquier otra acción u omisión que contravenga lo dispuesto en esta Ley y demás disposiciones aplicables que de ellos deriven')

# Para cada obligación: su nombre corto (el que sale en la matriz) y lo que la
# ley tiene por infracción (ley, artículo, cita del texto vigente), o None si
# no lo citamos.
RIESGOS = {
    'f_electronica': ('Contabilidad electrónica y comprobantes en tu domicilio',
                      ('cff', 'art. 83, fr. III', _CFF83 + ' […] Llevar la contabilidad en forma distinta a como las disposiciones de este Código o de otras leyes señalan; llevarla en lugares distintos a los señalados en dichas disposiciones')),
    'f_mensual': ('Envío mensual de la contabilidad al SAT',
                  ('cff', 'art. 81, fr. XLI', 'No ingresar la información contable a través de la página de Internet del Servicio de Administración Tributaria estando obligado a ello; ingresarla fuera de los plazos establecidos en las disposiciones fiscales')),
    'f_plazo': ('Plazo de 5 años de la contabilidad',
                ('cff', 'art. 83, fr. VI', _CFF83 + ' […] No conservar la contabilidad a disposición de las autoridades por el plazo que establezcan las disposiciones fiscales')),
    'f_sociedad': ('Papeles de la sociedad mientras exista',
                   ('cff', 'art. 83, fr. VI', _CFF83 + ' […] No conservar la contabilidad a disposición de las autoridades por el plazo que establezcan las disposiciones fiscales')),
    'm_libros': ('Libros y registros del negocio, 10 años', None),
    'm_contratos': ('Contratos y mensajes que los cierran, 10 años', None),
    'm_digital': ('Archivo digital con la norma oficial', None),
    'l_imss': ('Altas, bajas y salarios ante el IMSS',
               ('lss', 'art. 304 A, frs. I y II', 'Son infracciones a esta Ley y a sus reglamentos, los actos u omisiones del patrón o sujeto obligado que se enumeran a continuación: I. No registrarse ante el Instituto, o hacerlo fuera del plazo establecido en la Ley; II. No inscribir a sus trabajadores ante el Instituto o hacerlo en forma extemporánea')),
    'l_nomina': ('Nóminas y listas de raya, 5 años',
                 ('lss', 'art. 304 A, fr. VII', 'No llevar los registros de nóminas o listas de raya, en los términos que señala la Ley y el Reglamento para el Pago de Cuotas del Seguro Social')),
    'l_juicio': ('Expediente de quien sale, para un juicio',
                 ('lft', 'art. 805', 'establecerá la presunción de ser ciertos los hechos que el actor exprese en su demanda, en relación con tales documentos, salvo la prueba en contrario')),
    'p_padron': ('Alta en el Padrón de actividades vulnerables', _PLD),
    'p_identifica': ('Identificación de cada cliente', _PLD),
    'p_beneficiario': ('Beneficiario controlador', _PLD),
    'p_custodia': ('Expedientes de operaciones, 10 años', _PLD),
    'p_avisos': ('Avisos, y el de sospecha en 24 horas', _PLD),
    'd_aviso': ('Aviso de privacidad',
                ('lfpdppp', 'art. 58, fr. V', 'Omitir en el aviso de privacidad, alguno o todos los elementos a que se refiere el artículo 15 de esta Ley')),
    'd_seguridad': ('Medidas de seguridad de los datos',
                    ('lfpdppp', 'art. 58, fr. XI', 'Vulnerar la seguridad de bases de datos, locales, programas o equipos, cuando resulte imputable al responsable')),
    'd_vulneracion': ('Qué hacer si se filtran datos',
                      ('lfpdppp', 'art. 58, fr. XI', 'Vulnerar la seguridad de bases de datos, locales, programas o equipos, cuando resulte imputable al responsable')),
    'd_arco': ('Quién atiende las solicitudes ARCO',
               ('lfpdppp', 'art. 58, fr. I', 'No cumplir con la solicitud para el ejercicio de los derechos ARCO de la persona titular, sin razón fundada, en los términos previstos en esta Ley')),
    'd_plazo': ('Respuesta ARCO en 20 días',
                ('lfpdppp', 'art. 58, fr. I', 'No cumplir con la solicitud para el ejercicio de los derechos ARCO de la persona titular, sin razón fundada, en los términos previstos en esta Ley')),
    'd_supresion': ('Bloquear y suprimir al vencer el plazo',
                    ('lfpdppp', 'art. 58, fr. XIX', 'Cualquier incumplimiento del responsable a las obligaciones establecidas a su cargo en términos de lo previsto en la presente Ley')),
    'a_sistema': ('Sistema institucional de archivos', _LGA),
    'a_instrumentos': ('Cuadro, catálogo e inventarios', _LGA),
    'a_grupo': ('Grupo interdisciplinario', _LGA),
    'a_registro': ('Inscripción en el Registro Nacional de Archivos', _LGA),
}

PROB = {'no': 3, 'nose': 2, 'si': 1}          # qué tan probable es fallar, según tu respuesta
NIVEL = {1: 'Baja', 2: 'Media', 3: 'Alta'}
GRAVE = {1: 'Bajo', 2: 'Medio', 3: 'Alto'}
# La regla de las zonas (dicha en la página): probabilidad × gravedad.
ZONAS = [('alta', 6, '🔴', 'Atiéndelo primero'), ('media', 3, '🟠', 'Después'), ('baja', 1, '🟢', 'Vigílalo')]

CIEGOS = [
    ('La gravedad la pones tú', 'Nadie sabe mejor que tú cuánto te dolería: una multa, una revisión, un juicio que pierdes o un cliente que se va. Por eso no la rellenamos.'),
    ('«Sí» no es riesgo cero', 'Un «sí» va a la columna de probabilidad baja, no desaparece: si no lo puedes enseñar con un documento, cámbialo a «no sé».'),
    ('No ponemos montos de multa', 'Las multas se fijan en la ley con la UMA o en pesos que se actualizan, y la autoridad las individualiza: citamos el artículo, no un monto que mañana estaría viejo.'),
    ('Una infracción no es una sanción', 'Que la ley tenga algo por infracción no quiere decir que te vayan a multar: primero tiene que descubrirlo una autoridad, con su procedimiento.'),
    ('No cubre todo', 'Faltan leyes de un sector, las normas estatales, lo que pida un contrato y los riesgos que no son de papeles (fraude, ciberataques, reputación).'),
]


def esc(t):
    return html.escape(str(t))


def zona(p, g):
    s = p * g
    for k, minimo, _, _ in ZONAS:
        if s >= minimo:
            return k
    return 'baja'


# ---- La cuenta (gemela de matriz() de insp-riesgos.js) ----

def matriz(perfil, resp, grav):
    """`perfil`: lista de claves de PERFILES; `resp`: {id: 'si'|'no'|'nose'};
    `grav`: {id: 1|2|3}. Devuelve las celdas ('p-g': [ids]), el orden de
    atención (probabilidad × gravedad, luego gravedad, luego el orden de
    PREGUNTAS), cuántos hay por zona, los que falta valorar y los que falta
    contestar."""
    perfil = set(perfil)
    out = {'celdas': {}, 'orden': [], 'zonas': {'alta': 0, 'media': 0, 'baja': 0}, 'sinGrave': [], 'sinResp': []}
    filas = []
    for n, p in enumerate(PREGUNTAS):
        if not (p['quien'] == 'todos' or p['quien'] in perfil):
            continue
        r = resp.get(p['id'])
        if r not in PROB:
            out['sinResp'].append(p['id'])
            continue
        g = grav.get(p['id'])
        if g not in (1, 2, 3):
            out['sinGrave'].append(p['id'])
            continue
        pr = PROB[r]
        filas.append((-(pr * g), -g, n, p['id'], pr, g))
    for _, _, _, i, pr, g in sorted(filas):
        z = zona(pr, g)
        out['celdas'].setdefault('%d-%d' % (pr, g), []).append(i)
        out['orden'].append([i, pr, g, z])
        out['zonas'][z] += 1
    return out


def datos():
    return {'preguntas': [{k: p[k] for k in ('id', 'area', 'quien')} for p in PREGUNTAS],
            'cortos': {k: v[0] for k, v in RIESGOS.items()},
            'zonas': [[k, m, ic, t] for k, m, ic, t in ZONAS]}


def construir(base, ref):
    perf = ''.join('<label class="cs-op"><input type="checkbox" name="rgP" value="%s"> %s</label>' % (k, esc(t)) for k, t in PERFILES)
    nombres = {k: n for k, _, n in AREAS}
    filas = []
    for p in PREGUNTAS:
        corto, cons = RIESGOS[p['id']]
        resp = ''.join('<label class="cu-r"><input type="radio" name="rg-r-%s" value="%s"> %s</label>' % (p['id'], v, t)
                       for v, t in (('si', 'Sí'), ('no', 'No'), ('nose', 'No sé')))
        grav = ''.join('<label class="cu-r"><input type="radio" name="rg-g-%s" value="%d"> %s</label>' % (p['id'], v, GRAVE[v])
                       for v in (1, 2, 3))
        if cons:
            ley = '<p class="rg-cons"><b>Lo que prevé la ley</b> ({liga}): «…{cita}…»</p>'.format(
                liga=ley_liga(cons[0], cons[1]), cita=esc(cons[2]))
        else:
            ley = '<p class="rg-cons">No citamos aquí una consecuencia: valora tú qué pasaría si te faltara (por ejemplo, quedarte sin con qué probar).</p>'
        filas.append(
            '<li class="cu-q rg-q" id="rg-{id}" data-q="{quien}"><p class="rg-area">{area}</p><p class="cu-preg">{corto}</p>'
            '<p class="rg-preg">{q} <span class="cs-ley">({liga})</span></p>'
            '<p class="rg-et">¿La cumples?</p><div class="cu-ops" role="radiogroup" aria-label="¿La cumples? {corto}">{resp}</div>'
            '<p class="rg-et">Si fallara, ¿qué tan grave sería para ti?</p><div class="cu-ops" role="radiogroup" aria-label="Gravedad: {corto}">{grav}</div>'
            '<details class="cs-cita"><summary>Qué pasaría según la ley</summary>{ley}</details></li>'.format(
                id=p['id'], quien=p['quien'], area=esc(nombres[p['area']]), corto=esc(corto), q=esc(p['q']),
                liga=ley_liga(p['ley'], p['art']), resp=resp, grav=grav, ley=ley))
    ciegos = ''.join('<li><b>%s.</b> %s</li>' % (esc(t), esc(x)) for t, x in CIEGOS)
    usadas = []
    for p in PREGUNTAS:
        for k in (p['ley'], (RIESGOS[p['id']][1] or ('',))[0]):
            if k and k not in usadas:
                usadas.append(k)
    fuentes = ' · '.join('<a href="%s">%s</a>, última reforma %s (huella SHA-256 <code>%s…</code>)' % (esc(LEYES[k][3]), esc(LEYES[k][0]), esc(LEYES[k][2]), LEYES[k][4][:12])
                         for k in usadas)
    zonas = ' · '.join('%s <b>%s</b>: %s' % (ic, esc(t), 'probabilidad × gravedad de %d o más' % m if m > 1 else 'lo demás')
                       for _, m, ic, t in ZONAS)
    return '''<div class="ci cs cu rg" id="rgRaiz">
  <section class="ci-arranque" aria-labelledby="rgTit">
    <p class="ci-kicker">Modo Inspector · gobernanza documental</p>
    <h2 class="ci-grande" id="rgTit">Tu matriz de riesgos documentales</h2>
    <p class="ci-txt">Las mismas {n} obligaciones del autodiagnóstico, acomodadas en una matriz: <b>qué tan probable es que falles</b> (sale de tu respuesta) por <b>qué tan grave sería para ti</b> (lo eliges tú). Junto a cada una va lo que prevé la ley si fallas (la infracción o, en un juicio laboral, la presunción en tu contra), con su artículo. Así sabes <b>por dónde empezar</b>.</p>
    <p class="ci-privado">🔒 La cuenta la hace tu navegador: lo que contestas no se guarda ni se envía.</p>
  </section>

  <form class="ci-form" id="rgForm" novalidate>
    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">1</span> Quién eres</legend>
      <div class="cs-ops">{perf}</div>
      <p class="ci-pista">Si vienes del <a href="herramienta-inspector-cumplimiento.html">✅ autodiagnóstico</a>, tus respuestas ya están puestas. Una sociedad mercantil también es comerciante (Código de Comercio, art. 3o.): marca las dos.</p>
    </fieldset>
    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">2</span> Cada obligación: ¿la cumples y qué tan grave sería fallar?</legend>
      <p class="ci-pista">La probabilidad sale de tu respuesta: «no» es alta, «no sé» es media y «sí» es baja. La gravedad la pones tú: piensa en una multa, una revisión, un juicio que pierdes o un cliente que se va.</p>
      <ol class="cu-lista">{filas}</ol>
    </fieldset>
    <p class="ci-acciones"><button type="submit" class="ci-boton">Arma mi matriz</button></p>
  </form>

  <section class="ci-res" id="rgRes" aria-live="polite" hidden>
    <h2 class="ci-tit"><span class="ci-n" aria-hidden="true">3</span> Tu matriz {chip_d}</h2>
    <div class="ci-total" id="rgTotal"></div>
    <div class="ci-tabla-caja"><table class="rg-mat"><caption>Gravedad (filas) por probabilidad de fallar (columnas)</caption>
      <thead><tr><th scope="col"><span class="rg-oculto">Gravedad</span></th><th scope="col">Probabilidad baja<br><small>(«sí»)</small></th><th scope="col">Media<br><small>(«no sé»)</small></th><th scope="col">Alta<br><small>(«no»)</small></th></tr></thead>
      <tbody id="rgMat"></tbody></table></div>
    <p class="ci-pista">Las zonas son nuestra regla: {zonas}.</p>
    <h3 class="ci-tit">Por dónde empezar</h3>
    <ol class="ci-lista" id="rgOrden"></ol>
    <div id="rgFalta"></div>
    <p class="ci-acciones"><button type="button" class="ci-boton cu-sec" id="rgImprime">🖨️ Imprímela</button></p>
    <p class="ci-nota">Es tu respuesta y tu valoración acomodadas con una regla dicha aquí (auditada), no una calificación, una certificación ni una auditoría de tus papeles. Para que alguien la arme contigo y contra tus documentos: <a href="servicio-gobernanza.html">🗄️ el servicio de gobernanza documental</a>.</p>
  </section>

  <aside class="ci-aviso" aria-labelledby="rgCiegoTit">
    <h2 class="ci-tit" id="rgCiegoTit"><span aria-hidden="true">👁️</span> Lo que casi nadie te dice</h2>
    <ol class="ci-lista">{ciegos}</ol>
    <p><b>Lo que esta matriz no hace:</b> no es asesoría ni sustituye a tu contador o a tu abogado; no revisa tus documentos, no calcula multas ni dice que cumples ante ninguna autoridad. Cada obligación y cada consecuencia citan su artículo {chip_o}; la matriz solo acomoda tus respuestas.</p>
    <p class="ci-fuentes">Fuentes, cotejadas el 19-11-2026: {fuentes} {chip_o}.</p>
    <p class="ci-hermanas">Sigue con el Modo Inspector: <a href="herramienta-inspector-cumplimiento.html">✅ ¿Cumples con tus papeles?</a> · <a href="herramienta-inspector-conservacion.html">🗄️ ¿Hasta cuándo guardas tus papeles?</a> · <a href="servicio-gobernanza.html">🗄️ El servicio de gobernanza documental</a></p>
  </aside>
  <script type="application/json" id="rgDatos">{datos}</script>
</div>'''.format(n=len(PREGUNTAS), perf=perf, filas=''.join(filas), ciegos=ciegos, fuentes=fuentes, zonas=zonas,
                 chip_d=chip('derivado'), chip_o=chip('oficial'),
                 datos=json.dumps(datos(), ensure_ascii=False).replace('</', '<\\/'))


# ---- Prueba: la cuenta del navegador y la de aquí dan lo mismo ----

_TODOS = ['moral', 'comerciante', 'patron', 'pld', 'gobierno']
CASOS = [
    ([], {}, {}),
    ([], {'f_electronica': 'no', 'f_mensual': 'nose', 'f_plazo': 'si', 'd_aviso': 'no', 'p_padron': 'no'},
     {'f_electronica': 3, 'f_mensual': 3, 'f_plazo': 3, 'd_aviso': 2, 'p_padron': 3}),
    (_TODOS, {p['id']: ('no', 'nose', 'si')[i % 3] for i, p in enumerate(PREGUNTAS)},
     {p['id']: (i % 3) + 1 for i, p in enumerate(PREGUNTAS)}),
    (['patron'], {p['id']: 'no' for p in PREGUNTAS}, {'l_imss': 2, 'l_nomina': 2, 'd_arco': 9, 'x': 3}),
    (_TODOS, {p['id']: 'nose' for p in PREGUNTAS}, {p['id']: 3 - (i % 3) for i, p in enumerate(PREGUNTAS)}),
]


def prueba():
    mal = 0
    js = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'insp-riesgos.js')
    prog = ("global.window={};global.document={addEventListener:function(){}};require(%s);var D=%s;"
            "var c=%s;console.log(JSON.stringify(c.map(function(x){return window.AuditorRiesgos.matriz(D.preguntas,x[0],x[1],x[2]);})));"
            % (json.dumps(js), json.dumps(datos(), ensure_ascii=False), json.dumps(CASOS)))
    r = subprocess.run(['node', '-e', prog], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr)
        return 1
    for c, n in zip(CASOS, json.loads(r.stdout)):
        py = matriz(*c)
        if py != n:
            mal += 1
            print('✗', c[0], 'Python', py, 'navegador', n)
    ids = {p['id'] for p in PREGUNTAS}
    if set(RIESGOS) != ids:
        mal += 1
        print('✗ RIESGOS y PREGUNTAS no traen las mismas obligaciones:', sorted(set(RIESGOS) ^ ids))
    for k, (corto, cons) in RIESGOS.items():
        if not corto or (cons and (cons[0] not in LEYES or len(cons[2]) < 30)):
            mal += 1
            print('✗ riesgo', k)
    # Casos a mano: un «no» de gravedad alta es 9 (zona alta) y va primero;
    # un «sí» de gravedad baja es 1 (zona baja).
    m = matriz([], {'f_plazo': 'si', 'f_mensual': 'no'}, {'f_plazo': 1, 'f_mensual': 3})
    if m['orden'] != [['f_mensual', 3, 3, 'alta'], ['f_plazo', 1, 1, 'baja']] or len(m['sinResp']) != 7:
        mal += 1
        print('✗ el caso a mano no da lo esperado:', m)
    if [zona(p, g) for p, g in ((1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3))] != ['baja', 'baja', 'media', 'media', 'alta', 'alta']:
        mal += 1
        print('✗ las zonas no siguen la regla probabilidad × gravedad')
    if mal:
        print('%d diferencias en la matriz de riesgos' % mal)
        return 1
    print('✓ Matriz de riesgos: %d casos iguales en Python y en el navegador, %d obligaciones con su consecuencia o su aviso' % (len(CASOS), len(RIESGOS)))
    return 0


if __name__ == '__main__':
    if '--prueba' in sys.argv:
        sys.exit(prueba())
