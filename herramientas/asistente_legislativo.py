# -*- coding: utf-8 -*-
"""El Poder Legislativo y las elecciones, en el formato con que conversa el
bot (pedido del autor, 23-10-2026: «tomemos la pestaña de poder legislativo
[de la Enciclopedia]… para que también pueda resolver cuestiones del poder
legislativo, como cuántos curules son, las próximas elecciones…»).

La Enciclopedia sigue congelada: solo se leyó como guía de temas. Ninguna
cifra se copió de ella. Cada dato se cotejó contra su documento oficial
vigente al 23-10-2026, y lo que no cuadró se quedó fuera:

- Constitución (texto vigente de la Cámara de Diputados, última reforma
  DOF 07-10-2026): integración de las Cámaras (arts. 51 a 56), candados de
  los plurinominales (54), reelección (59 y transitorio tercero del decreto
  DOF 01-04-2025), periodos de sesiones (65 y 66), presupuesto (74, fr. IV),
  Comisión Permanente (78), congresos locales (116, fr. II), ayuntamientos
  (115, fr. I) y las reformas de 2026: «Plan B» (DOF 23-04-2026), elección
  judicial a 2028 (DOF 02-06-2026) y nacionalidad única (DOF 07-10-2026).
- LGIPE (última reforma DOF 02-06-2026): jornada el primer domingo de junio
  (art. 22), 40 diputaciones por circunscripción (art. 18) y campañas (251).
- LFPRH (última reforma DOF 09-04-2026), art. 42: fechas del paquete.
- Acuerdos del INE publicados en el DOF: casilla única (INE/CG469/2026,
  17 gubernaturas y concurrencia en las 32 entidades), fechas homologadas
  (INE/CG478/2026), precampañas (DOF 16-10-2026) e inicio del proceso
  (DOF 13-10-2026).
- INEGI, Censo Nacional de Poderes Legislativos Estatales 2025, tabla 8:
  las personas legisladoras en activo de cada congreso local.

Lo que la Enciclopedia decía y no se sostuvo (por eso no entra): el costo de
San Lázaro ($9,282 mdp; el PEF 2026 le aprobó $9,602.7), el del Senado
($5,365 mdp), sus desgloses por capítulo, las «~4,200 plazas», las partidas
de «gestión social» de los congresos, «1,098 curules locales» (el INEGI
cuenta 1,122 en activo) y la distritación «INE/CG130/2023» (ese acuerdo es
el de las circunscripciones; los distritos son del INE/CG875/2022).

asistente-charla.js lo lee como D.leg; la pagina congreso-y-elecciones.html
(apartados.py) se arma con secciones().
"""

import html
from urllib.parse import quote

CPEUM = {'tx': 'Constitución Política de los Estados Unidos Mexicanos, texto vigente (Cámara de Diputados, última reforma DOF 07-10-2026)',
         'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf',
         'sha256': 'cefb525ae8dfc97a7da40597d2ee918fe254d4bfce88301ff3c9959ced9e6e65'}
LGIPE = {'tx': 'Ley General de Instituciones y Procedimientos Electorales (última reforma DOF 02-06-2026)',
         'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGIPE.pdf',
         'sha256': '8d6253c7ac28c654543484bac172ca12bbda8db41564b07f27ca5bbea0b4cf80'}
LFPRH = {'tx': 'Ley Federal de Presupuesto y Responsabilidad Hacendaria, art. 42 (última reforma DOF 09-04-2026)',
         'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPRH.pdf',
         'sha256': 'ce45c7c0c4e9099691e6e24bd2456d0b6f71f91ab27eedd5c4f2190b66d47741'}
DOF2014 = {'tx': 'DOF 10-02-2014, reforma político-electoral: artículo 59 y transitorio décimo primero',
           'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5332025&fecha=10/02/2014'}
INE469 = {'tx': 'INE, Acuerdo INE/CG469/2026, modelo de casilla única 2026-2027, considerandos 25 y 29 (DOF 19-08-2026)',
          'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5796656&fecha=19/08/2026'}
INE478 = {'tx': 'INE, Resolución INE/CG478/2026, fechas homologadas de las precampañas en las 32 entidades (DOF 26-08-2026)',
          'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5797204&fecha=26/08/2026'}
INEPRE = {'tx': 'INE, Acuerdo de criterios y plazos de las precampañas del Proceso Electoral Federal 2026-2027, punto cuarto (DOF 16-10-2026)',
          'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5801398&fecha=16/10/2026'}
INECL = {'tx': 'INE, Acuerdo de designación de los Consejos Locales para el Proceso Electoral Federal 2026-2027 (DOF 13-10-2026): el proceso arrancó el 10 de septiembre de 2026',
         'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5801000&fecha=13/10/2026'}
CNPLE = {'tx': 'INEGI, Censo Nacional de Poderes Legislativos Estatales 2025, reporte de resultados, tabla 8, p. 32 (27-04-2026)',
         'url': 'https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2026/cnple/CNPLE_2025_RR.pdf',
         'sha256': '04305b1e81ec07b93d19ecb5ceb8d9da17aa45062d4c17ba00a8d3335a6c2524'}
INE_PEF = 'https://ine.mx/voto-y-elecciones/elecciones-2027/'

# Tabla 8 del CNPLE 2025: personas legisladoras en activo al cierre del
# último periodo que reportó cada congreso (clave de entidad de D.edo).
CONGRESOS = {'MÉX': 75, 'CDMX': 65, 'VER': 50, 'GRO': 46, 'NL': 42, 'OAX': 42, 'PUE': 41, 'CHIS': 40, 'MICH': 40,
             'SIN': 40, 'JAL': 38, 'GTO': 36, 'TAM': 36, 'CAM': 35, 'TAB': 35, 'YUC': 35, 'CHIH': 33, 'SON': 33,
             'HGO': 30, 'NAY': 30, 'ZAC': 30, 'AGS': 27, 'SLP': 27, 'BC': 25, 'COAH': 25, 'COL': 25, 'DGO': 25,
             'QRO': 25, 'QROO': 25, 'TLAX': 25, 'BCS': 21, 'MOR': 20}
CONGRESOS_TOTAL = 1122  # «EUM» de la misma tabla

# La pagina donde se lee todo esto (pedido del autor, 23-10-2026: cada
# respuesta del bot lleva «Saber mas» a la pagina donde esta la informacion).
PAGINA = 'congreso-y-elecciones.html'
PAGINA_TIT = 'El Congreso y las elecciones'
ORDEN = ['elecciones', 'diputados', 'senado', 'congreso', 'pluris', 'reeleccion', 'judicial',
         'sesiones', 'permanente', 'paquete', 'locales', 'ayuntamientos', 'reformas']


def _o(que, fu, op=None):
    d = {'que': que, 'e': 'derivado' if op else 'oficial', 'fu': fu}
    if op:
        d['op'] = op
    return d


def legislativo():
    assert sum(CONGRESOS.values()) == CONGRESOS_TOTAL and len(CONGRESOS) == 32
    t = {}
    t['diputados'] = {
        'tit': 'La Cámara de Diputados',
        'h': '<p>La Cámara de Diputados tiene <b>500 curules</b>: <b>300</b> de mayoría relativa, una por cada distrito electoral, '
             'y <b>200</b> de representación proporcional (las «plurinominales»), que se reparten por listas en <b>5 circunscripciones</b> de 40 cada una. '
             'Se renueva completa <b>cada tres años</b>, y por cada diputación propietaria se elige una suplente.</p>'
             '<p>La próxima vez que se elige es el <b>domingo 6 de junio de 2027</b>.</p>',
        'fu': [_o('Integración de la Cámara de Diputados (arts. 51, 52 y 53)', CPEUM), _o('40 diputaciones por circunscripción (art. 18)', LGIPE),
               _o('Próxima elección: 6 de junio de 2027', LGIPE, 'el art. 22 fija el primer domingo de junio; en 2027 cae el día 6')],
        'ci': [{'v': '500', 'etq': 'curules de la Cámara de Diputados', 'e': 'oficial'}, {'v': '300 + 200', 'etq': 'mayoría relativa + representación proporcional', 'e': 'oficial'}],
        'sug': ['¿Cuántos senadores hay?', '¿Qué son los plurinominales?', '¿Cuándo son las próximas elecciones?']}
    t['senado'] = {
        'tit': 'El Senado de la República',
        'h': '<p>El Senado tiene <b>128 escaños</b>: en cada estado y en la Ciudad de México se eligen <b>2 por mayoría relativa</b> (64 en total) '
             'y <b>1 de primera minoría</b> (32), que es para la fórmula del partido que quedó en segundo lugar; los <b>32 restantes</b> son de representación '
             'proporcional, de una lista nacional. Se renueva completo <b>cada seis años</b>: la última vez fue en 2024 y la próxima será en <b>2030</b>, junto con la Presidencia.</p>'
             '<p>Por la reforma del 23 de abril de 2026, el presupuesto del Senado debe bajar <b>15 % en términos reales</b> en cuatro años, contra el de 2026.</p>',
        'fu': [_o('Integración del Senado (art. 56)', CPEUM), _o('64 de mayoría relativa', CPEUM, '2 por entidad × 32 entidades'),
               _o('Próxima elección del Senado: 2030', LGIPE, 'el art. 22 la fija cada seis años; la última fue en 2024'),
               _o('Recorte de 15 % real al Senado (transitorio tercero, DOF 23-04-2026)', CPEUM)],
        'ci': [{'v': '128', 'etq': 'escaños del Senado', 'e': 'oficial'}],
        'sug': ['¿Cuántos diputados hay?', '¿Cuánto gana un senador?', '¿Cuánto cuesta el Senado?']}
    t['congreso'] = {
        'tit': 'El Congreso de la Unión',
        'h': '<p>El Congreso de la Unión suma <b>628 legisladoras y legisladores</b>: <b>500</b> en la Cámara de Diputados y <b>128</b> en el Senado. '
             'Durante los recesos funciona la <b>Comisión Permanente</b>, con 37 integrantes.</p>',
        'fu': [_o('628 legisladores', CPEUM, '500 diputaciones (art. 52) + 128 senadurías (art. 56)')],
        'ci': [{'v': '628', 'etq': 'legisladores federales', 'e': 'derivado', 'op': '500 + 128'}],
        'sug': ['¿Cuántos diputados hay?', '¿Cuántos senadores hay?', '¿Cuándo sesiona el Congreso?']}
    t['pluris'] = {
        'tit': 'Los plurinominales',
        'h': '<p>Los <b>plurinominales</b> son las curules de <b>representación proporcional</b>: no se votan por nombre, sino por partido. '
             'Son <b>200 diputaciones</b> (en 5 circunscripciones de 40) y <b>32 senadurías</b> (una lista nacional). Sirven para que la Cámara se parezca a la votación.</p>'
             '<p>Sus candados, en el artículo 54: un partido necesita al menos el <b>3 %</b> de la votación válida para entrar al reparto; '
             'ninguno puede tener más de <b>300 diputaciones</b>, ni más curules que <b>8 puntos</b> por encima de su porcentaje de votos '
             '(salvo que lo gane con distritos de mayoría).</p>'
             '<p class="pa-chico">Siguen vigentes: el artículo 52, que fija los 300 + 200, no ha cambiado desde 2019.</p>',
        'fu': [_o('Representación proporcional (arts. 52, 54 y 56)', CPEUM), _o('40 diputaciones por circunscripción (art. 18)', LGIPE)],
        'ci': [{'v': '200', 'etq': 'diputaciones plurinominales', 'e': 'oficial'}, {'v': '32', 'etq': 'senadurías plurinominales', 'e': 'oficial'}],
        'sug': ['¿Cuántos diputados hay?', '¿Se pueden reelegir los diputados?']}
    t['permanente'] = {
        'tit': 'La Comisión Permanente',
        'h': '<p>La <b>Comisión Permanente</b> trabaja cuando el Congreso está en receso. Tiene <b>37 integrantes</b>: <b>19</b> diputadas o diputados y <b>18</b> senadoras o senadores, '
             'que cada Cámara nombra la víspera de cerrar su periodo. Entre otras cosas, recibe iniciativas y puede convocar a periodos extraordinarios con dos terceras partes de los votos.</p>',
        'fu': [_o('Comisión Permanente (art. 78, reformado DOF 15-10-2025)', CPEUM)],
        'ci': [{'v': '37', 'etq': 'integrantes (19 + 18)', 'e': 'oficial'}],
        'sug': ['¿Cuándo sesiona el Congreso?', '¿Cuántos diputados hay?']}
    t['sesiones'] = {
        'tit': 'Los periodos de sesiones',
        'h': '<p>El Congreso tiene <b>dos periodos ordinarios</b> al año:</p><ul class="pa-lista">'
             '<li><b>Del 1 de septiembre al 15 de diciembre.</b> Es el del presupuesto. Se puede alargar al 31 de diciembre el año en que entra un nuevo presidente o presidenta.</li>'
             '<li><b>Del 1 de febrero al 30 de abril.</b></li></ul>'
             '<p>En los recesos trabaja la <b>Comisión Permanente</b> (37 integrantes).</p>',
        'fu': [_o('Periodos de sesiones (arts. 65 y 66)', CPEUM), _o('Comisión Permanente (art. 78)', CPEUM)],
        'sug': ['¿Cuándo se aprueba el presupuesto?', '¿Qué es la Comisión Permanente?']}
    t['paquete'] = {
        'tit': 'Las fechas del presupuesto',
        'h': '<p>El calendario del dinero público cada año:</p><ul class="pa-lista">'
             '<li><b>8 de septiembre:</b> Hacienda entrega el Paquete Económico (Criterios, Ley de Ingresos y proyecto de Presupuesto). '
             'El año en que entra un nuevo presidente o presidenta, el 15 de noviembre.</li>'
             '<li><b>20 de octubre:</b> la Cámara de Diputados aprueba la Ley de Ingresos; el Senado, a más tardar el <b>31 de octubre</b>.</li>'
             '<li><b>15 de noviembre:</b> la Cámara de Diputados aprueba el Presupuesto de Egresos. Es facultad solo suya: el Senado no vota el gasto.</li></ul>',
        'fu': [_o('Presupuesto de Egresos (art. 74, fr. IV)', CPEUM), _o('Ley de Ingresos y Presupuesto (art. 42)', LFPRH)],
        'ir': ['numeros-gasto-quien-lo-aprueba.html', '¿Quién lo aprueba?'],
        'sug': ['¿Cuándo sesiona el Congreso?', '¿Qué propone el Paquete 2027?']}
    t['elecciones'] = {
        'tit': 'Las próximas elecciones: 6 de junio de 2027',
        'h': '<p>Las próximas elecciones son el <b>domingo 6 de junio de 2027</b>. El proceso federal arrancó el <b>10 de septiembre de 2026</b>.</p><ul class="pa-lista">'
             '<li><b>Federal:</b> se renuevan las <b>500 diputaciones</b> federales (300 de mayoría y 200 plurinominales). No se vota Senado ni Presidencia: esos tocan en 2030.</li>'
             '<li><b>Local:</b> hay elecciones en las <b>32 entidades</b>, todas el mismo día y en casilla única. Se eligen <b>17 gubernaturas</b>, además de congresos locales y ayuntamientos.</li>'
             '<li><b>Precampañas</b> federales: del <b>4 de enero al 12 de febrero de 2027</b>.</li>'
             '<li><b>Campañas</b> federales: 60 días que terminan el <b>2 de junio</b>; del 3 al 5 de junio no hay actos de campaña (la veda).</li></ul>'
             '<p><b>Ojo:</b> la elección de juezas, jueces y magistraturas <b>ya no es en 2027</b>. Una reforma la movió al <b>primer domingo de junio de 2028</b>.</p>',
        'fu': [_o('Jornada electoral: 6 de junio de 2027', LGIPE, 'el art. 22 fija el primer domingo de junio; en 2027 cae el día 6'),
               _o('Inicio del Proceso Electoral Federal 2026-2027', INECL),
               _o('Concurrencia en las 32 entidades y 17 gubernaturas', INE469),
               _o('Precampañas del 4 de enero al 12 de febrero de 2027', INEPRE),
               _o('Campañas y veda', LGIPE, 'el art. 251 da 60 días a las campañas cuando solo se elige la Cámara y las cierra tres días antes de la jornada: terminan el 2 de junio y la veda va del 3 al 5'),
               _o('Elección judicial en 2028 (transitorios segundo y tercero, DOF 02-06-2026)', CPEUM),
               {'que': 'Cuáles son las 17 gubernaturas y cuántos cargos locales se eligen', 'e': 'pendiente', 'p': 'elecciones-2027-cargos',
                'fu': {'tx': 'INE, Proceso Electoral Federal 2026-2027', 'url': INE_PEF}}],
        'ci': [{'v': '6 de junio de 2027', 'etq': 'jornada electoral', 'e': 'derivado'}, {'v': '500', 'etq': 'diputaciones federales en juego', 'e': 'oficial'},
               {'v': '17', 'etq': 'gubernaturas', 'e': 'oficial'}],
        'sug': ['¿Cuándo es la elección judicial?', '¿Se pueden reelegir los diputados?', '¿Cuántos diputados hay?']}
    t['judicial'] = {
        'tit': 'La elección judicial pasó a 2028',
        'h': '<p>La segunda elección del Poder Judicial <b>ya no será en 2027</b>. La reforma publicada el <b>2 de junio de 2026</b> la movió al '
             '<b>primer domingo de junio de 2028</b>, para elegir a la vez los cargos federales y locales que no se renovaron en 2025.</p>'
             '<p>Quienes debían dejar el cargo en 2027 siguen hasta que tomen protesta los electos, el <b>1 de septiembre de 2028</b>. '
             'Las magistraturas de circuito y los juzgados de distrito que se elijan en 2028 durarán ocho años, hasta 2036.</p>',
        'fu': [_o('Elección judicial en 2028 (decreto DOF 02-06-2026, transitorios segundo, tercero y séptimo)', CPEUM)],
        'sug': ['¿Cuándo son las próximas elecciones?', '¿Cuánto gana un ministro de la Corte?']}
    t['reeleccion'] = {
        'tit': '¿Se pueden reelegir?',
        'h': '<p><b>En 2027, todavía sí.</b> La reforma del 1 de abril de 2025 prohibió la reelección inmediata de diputaciones y senadurías (art. 59), '
             'de congresos locales y de ayuntamientos, pero se aplica <b>a partir de las elecciones de 2030</b>. Hasta entonces sigue la regla de 2014: '
             'diputadas y diputados federales pueden encadenar hasta <b>cuatro periodos</b>, y senadoras y senadores hasta <b>dos</b>, postulados por el mismo partido o coalición.</p>'
             '<p>La misma reforma prohíbe desde 2030 el <b>nepotismo electoral</b>: no podrá competir por un cargo el cónyuge o pariente de quien lo ocupa.</p>',
        'fu': [_o('No reelección y nepotismo (art. 59 y transitorios segundo y tercero, DOF 01-04-2025)', CPEUM), _o('Regla de 2014 (art. 59)', DOF2014)],
        'sug': ['¿Cuándo son las próximas elecciones?', '¿Cuántos diputados hay?']}
    t['locales'] = {
        'tit': 'Los 32 congresos locales',
        'h': '<p>Los congresos de los estados y de la Ciudad de México sumaban <b>1,122 personas legisladoras en activo</b>, según el último censo del INEGI. '
             'El más grande es el del <b>Estado de México (75)</b> y el más chico, el de <b>Morelos (20)</b>.</p>'
             '<p>La Constitución pone el piso: <b>7</b> diputaciones si el estado tiene menos de 400 mil habitantes, <b>9</b> si tiene menos de 800 mil y <b>11</b> si tiene más. '
             'Desde la reforma del 23 de abril de 2026, el presupuesto de cada congreso no puede pasar del <b>0.70 %</b> del presupuesto de su estado.</p>',
        'fu': [_o('Personas legisladoras en activo por congreso (tabla 8)', CNPLE), _o('Piso de diputaciones y tope de 0.70 % (art. 116, fr. II)', CPEUM)],
        'ci': [{'v': '1,122', 'etq': 'personas legisladoras locales en activo', 'e': 'oficial'}],
        'sug': ['¿Cuántos diputados tiene el congreso de Jalisco?', '¿Cuánto gasta el Congreso de Jalisco?', '¿Cuántos diputados hay?']}
    t['ayuntamientos'] = {
        'tit': 'Cómo se integra un ayuntamiento',
        'h': '<p>Cada municipio lo gobierna un <b>ayuntamiento</b> electo: una <b>presidencia municipal</b>, <b>una sindicatura</b> y <b>hasta 15 regidurías</b>, con paridad de género. '
             'El tope de 15 regidurías viene de la reforma del 23 de abril de 2026 y cuenta a partir del siguiente periodo de cada ayuntamiento; los que ya tenían menos de 15 se quedan como están.</p>',
        'fu': [_o('Integración del ayuntamiento (art. 115, fr. I, y transitorio sexto, DOF 23-04-2026)', CPEUM)],
        'sug': ['¿Cuántos municipios hay?', '¿Cuándo son las próximas elecciones?']}
    t['reformas'] = {
        'tit': 'Las reformas recientes que tocan al Congreso y a las elecciones',
        'h': '<p>Lo que cambió en la Constitución, con su fecha en el Diario Oficial:</p><ul class="pa-lista">'
             '<li><b>1 de abril de 2025:</b> no reelección y no nepotismo electoral, a partir de 2030.</li>'
             '<li><b>23 de abril de 2026:</b> los congresos locales no pueden gastar más del 0.70 % del presupuesto de su estado; los ayuntamientos, hasta 15 regidurías; '
             'el Senado recorta 15 % real en cuatro años, y los sueldos de consejerías y magistraturas electorales no pueden pasar el tope del artículo 127.</li>'
             '<li><b>2 de junio de 2026:</b> la elección judicial pasa a 2028, y la intervención extranjera se vuelve causa para anular una elección.</li>'
             '<li><b>7 de octubre de 2026:</b> para ser presidente, presidenta o titular de un gobierno estatal hay que tener solo la nacionalidad mexicana; aplica desde el proceso electoral de 2028.</li></ul>'
             '<p class="pa-chico">Los 500 diputados (300 + 200) y los 128 senadores no cambiaron: los artículos 52 y 56 siguen igual.</p>',
        'fu': [_o('Decretos de reforma DOF 01-04-2025, 23-04-2026, 02-06-2026 y 07-10-2026', CPEUM)],
        'sug': ['¿Se pueden reelegir los diputados?', '¿Cuándo es la elección judicial?', '¿Cuántos diputados tiene el congreso de Jalisco?']}
    assert sorted(ORDEN) == sorted(t)
    for k, x in t.items():
        x.setdefault('ir', [PAGINA + '#leg-' + k, PAGINA_TIT])
    return {'t': t, 'cong': CONGRESOS, 'congTot': CONGRESOS_TOTAL, 'cnple': CNPLE, 'cpeum': CPEUM,
            'pag': [PAGINA + '#leg-locales', PAGINA_TIT]}


def _chip(e, p=None):
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, ' data-pend="%s"' % p if p else '', e)


def _fuentes(fu):
    li = []
    for x in fu:
        f = x.get('fu') or {}
        liga = ('<a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>' % (html.escape(f['url'], quote=True), html.escape(f['tx']))
                if f.get('url') else html.escape(f.get('tx', '')))
        li.append('<li>%s <b>%s.</b> %s%s</li>' % (_chip(x['e'], x.get('p')), html.escape(x['que']),
                                                   'Cuenta: %s. ' % html.escape(x['op']) if x.get('op') else '', liga))
    return '<details class="pa-dedonde leg-fuentes" open><summary><span>📎 De dónde sale</span></summary><ul>%s</ul></details>' % ''.join(li)


def secciones(estados):
    """Las secciones de la pagina «El Congreso y las elecciones»: el mismo
    texto con que contesta el bot, tema por tema, con sus fuentes a la vista.
    `estados` es la lista de la base (abbr y name) para nombrar los congresos."""
    L = legislativo()
    nombre = {e['abbr']: e['name'] for e in estados}
    out = []
    for k in ORDEN:
        x = L['t'][k]
        cifras = ''.join('<li><b>%s</b> <span>%s</span> %s%s</li>' % (html.escape(c['v']), html.escape(c['etq']), _chip(c['e']),
                                                                    ' <small>(%s)</small>' % html.escape(c['op']) if c.get('op') else '')
                         for c in x.get('ci', []))
        extra = ''
        if k == 'locales':
            filas = sorted(CONGRESOS.items(), key=lambda a: (-a[1], nombre[a[0]]))
            extra = ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Personas legisladoras en activo en cada congreso local %s</caption>'
                     '<thead><tr><th scope="col">Lugar</th><th scope="col">Congreso</th><th scope="col">Legisladores</th></tr></thead><tbody>%s</tbody>'
                     '<tfoot><tr><th scope="row" colspan="2">Los 32 congresos</th><td>%s</td></tr></tfoot></table></div>'
                     '<p class="pa-chico">Fuente: %s. El lugar es derivado: ordenamos los 32 congresos de mayor a menor. '
                     'El INEGI aclara que el Congreso de la Ciudad de México debe tener 66: una persona suplente tomó protesta después del corte.</p>') % (
                _chip('oficial'),
                ''.join('<tr><td>%d</td><th scope="row">%s</th><td>%d</td></tr>' % (1 + sum(1 for v in CONGRESOS.values() if v > n), html.escape(nombre[a]), n)
                        for a, n in filas),
                format(CONGRESOS_TOTAL, ','), '<a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>' % (CNPLE['url'], html.escape(CNPLE['tx'])))
        if x['ir'][0].split('#')[0] != PAGINA:
            extra += '<p class="leg-mas"><a href="%s">📖 Saber más en «%s» ➔</a></p>' % (x['ir'][0], html.escape(x['ir'][1]))
        q = (x.get('sug') or [''])[0]
        bloque = '<div class="leg-tema">%s%s%s%s%s</div>' % (
            x['h'], '<ul class="leg-cifras">%s</ul>' % cifras if cifras else '', extra, _fuentes(x['fu']),
            '<p class="leg-pregunta"><a href="herramienta-inspector-pregunta.html?q=%s">💬 Pregúntale al Auditor: «%s»</a></p>' % (quote(q), html.escape(q)) if q else '')
        out.append({'id': 'leg-' + k, 'titulo': html.escape(x['tit']), 'texto': '', 'tarjetas': [], 'bloque': bloque})
    return out
