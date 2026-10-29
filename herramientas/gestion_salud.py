# -*- coding: utf-8 -*-
"""Salud pública: lo que cuesta y lo que resuelve (auditoría de gestión,
pedido del autor, 27-10-2026: «hacer las auditorías… de salud pública,
hablándose del ISSSTE, del IMSS Bienestar, del Seguro Popular… tanto de dinero
como de números»; «sigue con salud»).

Mismo molde que gestion_judicial.py: el dinero junto a lo que se hizo con él,
con lo derivado a la vista y lo que falta con su ficha. Documentos cotejados
el 27-10-2026:

- IMSS, Memoria Estadística 2025 (archivos de Excel de su portal, huella
  SHA-256 de cada uno abajo): población derechohabiente (cap. II), servicios
  médicos (cap. IV, cuadros IV.2 y IV.3), recursos y estado de ingresos y
  gastos por ramo de seguro (cap. XIII, cuadros XIII.7, XIII.10 y XIII.45) e
  indicadores (cap. XV, cuadros XV.10 y XV.11). Las cifras se leyeron de las
  celdas con un script, no a mano.
- IMSS, Boletín de prensa 023/2026 (13-01-2026): lo que el Instituto anunció
  de 2025 y sus metas de 2026. Se coteja contra su propia Memoria.
- Ley General de Salud, texto vigente (Cámara de Diputados, última reforma
  DOF 15-01-2026): los decretos del 29-11-2019 (Seguro Popular → INSABI) y del
  29-05-2023 (INSABI → IMSS-Bienestar).
- El gasto de la Cuenta Pública 2025 del IMSS y del ISSSTE ya estaba en la
  base (inspector_federal, datos abiertos de Hacienda).

Lo que no se pudo cotejar y queda en el Registro de pendientes: los servicios
del ISSSTE (su anuario estadístico no respondió), los del IMSS-Bienestar y su
gasto, y el tiempo de espera de una consulta o una cirugía.

La lee asistente_judicial.poderes de apartados.py (como un tercer «Poder» de
Datos) y asistente.py (D.sal del chat).
"""

import html

from asistente_legislativo import _chip, bloque_tema

_X = 'https://www.imss.gob.mx/sites/all/statics/pdf/estadisticas/memoria/2025/'
MEM = {
    'II': {'tx': 'IMSS, Memoria Estadística 2025, cap. II: Población derechohabiente', 'url': _X + '02-PoblacionDerechohabiente.xlsx',
           'sha256': '960d6dd93e533a46123d7e2cc0c9a9e1fa05fd3545bcedc2842bc8cea8b83c9e'},
    'IV': {'tx': 'IMSS, Memoria Estadística 2025, cap. IV: Prestaciones médicas', 'url': _X + '04-PrestacionesMedicas.xlsx',
           'sha256': '9a616879f00e160262147305b377a1c997f66f2d80cec8d98756ef20e9b9a89d'},
    'XIII': {'tx': 'IMSS, Memoria Estadística 2025, cap. XIII: Recursos humanos, materiales y financieros', 'url': _X + '13-RecursosHumanosMaterialesFinancieros.xlsx',
             'sha256': '88bcd2173b23d414848562a8408fd341006a8eb5699f2a8e01f1c56e718006e4'},
    'XV': {'tx': 'IMSS, Memoria Estadística 2025, cap. XV: Indicadores', 'url': _X + '15-Indicadores.xlsx',
           'sha256': '52413e0b2c0a305831bccb388ffddb87ec848ec1d1c0611a1b1d1266a33d88e0'},
}
MEMORIA = 'https://www.imss.gob.mx/conoce-al-imss/memoria-estadistica-2025'
BOL = {'tx': 'IMSS, Boletín de prensa 023/2026 (13-01-2026)',
       'url': 'https://www.imss.gob.mx/sites/all/statics/i2f_news/IMSS.%20Boleti%CC%81n%20023._1.pdf',
       'sha256': '8c5119a0ad6bd69fdf6b4c50b92ecd609c1abe8d5e76c37f22e1b2ecf1d4fe13'}
LGS = {'tx': 'Ley General de Salud, texto vigente (Cámara de Diputados, última reforma DOF 15-01-2026)',
       'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGS.pdf',
       'sha256': 'a2d3f947b369e4383f2f27a4e9bd819a3dba768ab9bae527e6388e30c1f9e06c'}


def _m(cap, donde):
    f = dict(MEM[cap])
    f['tx'] = '%s, %s' % (f['tx'], donde)
    return f


# Seguro de Enfermedad y Maternidad, 2025 (cuadro XIII.45, columna «Total
# Enfermedad y Maternidad», en pesos). Es la parte de salud del IMSS: la
# separa de Riesgos de Trabajo, Invalidez y Vida, Guarderías y Seguro para la
# Familia. Es contabilidad (estado de ingresos y gastos), no la Cuenta Pública.
SEM = {'ingresos': 538021007539.78, 'personales': 294558641825.69, 'materiales': 101099366297.22,
       'generales': 79234476187.88, 'funcionamiento': 474892484310.79, 'pensiones': 164456388731.60,
       'gastos': 689147778977.38, 'resultado': -151126771437.60}
IMSS_RESULTADO = -4398433714.43   # resultado de todos los seguros juntos (misma tabla, columna Total)
IV_RESULTADO = 108197383491.16    # Invalidez y Vida

# Servicios médicos (cuadros IV.2 y IV.3): (2018, 2024, 2025). La Memoria
# advierte que no incluyen lo que se dio al IMSS-Bienestar.
SERV = [('Consultas, en total', 129992196, 144073739, 158037603, 'IV.3'),
        ('· de medicina familiar', 85720551, 96054934, 104798443, 'IV.3'),
        ('· de especialidad', 19737565, 23762522, 29673954, 'IV.3'),
        ('· de urgencias', 19768928, 18029122, 17193792, 'IV.3'),
        ('· dentales', 4765152, 6227161, 6371414, 'IV.3'),
        ('Egresos hospitalarios', 2074568, 2277161, 2355154, 'IV.2'),
        ('Intervenciones quirúrgicas', 1435499, 1865159, 2216220, 'IV.2')]
# Recursos (cuadros XIII.7 y XIII.10) e indicadores (XV.10 y XV.11): (2018, 2025).
REC = [('Personal médico', 77469, 113643, 'XIII', 'cuadro XIII.7'),
       ('· especialistas', 25292, 32026, 'XIII', 'cuadro XIII.7'),
       ('· médicas y médicos familiares', 17505, 24536, 'XIII', 'cuadro XIII.7'),
       ('Camas en servicio', 53490, 58325, 'XIII', 'cuadro XIII.10'),
       ('· censables (de hospitalización)', 33752, 38824, 'XIII', 'cuadro XIII.10'),
       ('Quirófanos', 1427, 1576, 'XIII', 'cuadro XIII.10'),
       ('Consultorios', 18247, 19859, 'XIII', 'cuadro XIII.10')]
OCUPACION = (90.0, 76.9)   # % de ocupación hospitalaria, 2018 y 2025 (XV.11; 2025: 76.95)
ESTANCIA = (4.76, 4.61)    # días promedio de estancia (XV.10)
# Población derechohabiente adscrita a unidad de medicina familiar (II.9) y
# potencial (II.3).
ADSCRITA = (57221796, 63598543)   # 2018, 2025
POTENCIAL_2025 = 79178109

# El boletín 023/2026 contra la Memoria: (lo que dice, resultado, explicación).
COTEJO = [
    ('«14 millones más de atenciones médicas» en 2025', 'consta',
     'La Memoria registra 158,037,603 consultas en 2025 y 144,073,739 en 2024: 13,963,864 más.'),
    ('«104 millones de consultas de Medicina Familiar» y 85.7 millones en 2018', 'consta',
     'La Memoria registra 104,798,443 en 2025 y 85,720,551 en 2018.'),
    ('Consultas de especialidad: 19.7 millones en 2018 y «10 millones de consultas más», un 48 %', 'consta',
     'La Memoria registra 19,737,565 en 2018 y 29,673,954 en 2025: 9,936,389 más, un 50.3 %. El redondeo no se aleja más de 10 %.'),
    ('«22 por ciento más» consultas de especialidad que en 2024', 'matiz',
     'Según la Memoria fueron 24.9 % más (23,762,522 en 2024). El boletín se queda corto.'),
    ('«Un millón 780 mil cirugías», un aumento de «prácticamente el 30 por ciento»', 'no cuadra',
     'La Memoria registra 2,216,220 intervenciones quirúrgicas en 2025 y 1,865,159 en 2024: un aumento de 18.8 %. '
     'Son dos conteos distintos del mismo Instituto, y ninguno de los dos documentos explica qué cuenta cada uno.'),
    ('En 2018 se hacían «1.1 millones de cirugías» y hoy «60 por ciento más»', 'no cuadra',
     'La Memoria registra 1,435,499 intervenciones quirúrgicas en 2018: con sus cifras, el aumento a 2025 es de 54.4 %.'),
    ('Cataratas con «12 días» menos de espera y vesícula con «10 días» menos', 'pendiente',
     'El IMSS da cuánto bajó la espera, pero no cuánto se esperaba antes ni cuánto se espera ahora. Sin esa base no se puede comprobar.'),
]
METAS_2026 = [('Cirugías', '2.1 millones'), ('Consultas de especialidad', '32.8 millones'), ('Consultas de medicina familiar', '108 millones')]

PORTADA = 'datos-salud-publica.html'
PORTADA_TIT = 'Salud pública'
PAGINAS = [
    ('datos-salud-imss.html', '🩺', 'El IMSS: lo que cuesta y lo que resuelve', 'Su gasto en salud, sus consultas y cirugías, y lo que anuncia contra lo que registra',
     'Cuánto gastó el IMSS en el seguro que paga tu atención médica, cuántas consultas, hospitalizaciones y cirugías dio con ese dinero, con cuántos médicos y camas, '
     'y si lo que anunció en conferencia coincide con lo que registra su propia Memoria Estadística.',
     ['imss_dinero', 'imss_servicios', 'imss_recursos', 'imss_cotejo']),
    ('datos-salud-sistema.html', '🏥', 'Seguro Popular, INSABI, IMSS-Bienestar e ISSSTE', 'Quién atiende a quién, qué cambió y lo que nadie ha publicado',
     'Qué pasó con el Seguro Popular, por qué las series de salud se rompen en 2020 y en 2023, y qué sabemos del IMSS-Bienestar y del ISSSTE. '
     'Lo que todavía no se puede auditar va con su ficha en el Registro de pendientes.',
     ['transicion', 'imss_bienestar', 'issste']),
]
PAGINA_DE = {k: (p[0], p[2]) for p in PAGINAS for k in p[5]}
PRE = 'sal-'

PEND_ESPERA = {'que': 'Cuánto espera una persona una consulta de especialidad o una cirugía en el IMSS', 'e': 'pendiente', 'p': 'salud-tiempos-espera',
               'fu': {'tx': 'IMSS, Memoria Estadística 2025', 'url': MEMORIA}}
PEND_ISSSTE = {'que': 'Consultas, egresos y cirugías del ISSSTE en 2025', 'e': 'pendiente', 'p': 'salud-issste-servicios',
               'fu': {'tx': 'ISSSTE, anuarios estadísticos', 'url': 'https://www.gob.mx/issste/documentos/anuarios-estadisticos'}}
PEND_BIEN = {'que': 'Consultas, egresos, cirugías y gasto del IMSS-Bienestar en 2025', 'e': 'pendiente', 'p': 'salud-imss-bienestar',
             'fu': {'tx': 'Servicios de Salud del IMSS-Bienestar', 'url': 'https://www.gob.mx/imssbienestar'}}


def _o(que, fu, op=None, e=None):
    d = {'que': que, 'e': e or ('derivado' if op else 'oficial'), 'fu': fu}
    if op:
        d['op'] = op
    return d


def _n(v):
    return format(int(round(v)), ',')


def _mdp(v):
    return '$%s millones' % format(round(v / 1e6, 1), ',.1f')


def _var(a, b):
    return ('+' if b >= a else '−') + format(abs(round(100.0 * (b - a) / a, 1)), '.1f') + ' %'


def _pct(a, b):
    return format(abs(round(100.0 * (b - a) / a, 1)), '.1f') + ' %'


def chequeo(d):
    assert abs(SEM['personales'] + SEM['materiales'] + SEM['generales'] - SEM['funcionamiento']) < 1
    assert abs(SEM['ingresos'] - SEM['gastos'] - SEM['resultado']) < 1
    assert sum(s[3] for s in SERV[1:5]) == SERV[0][3] and sum(s[2] for s in SERV[1:5]) == SERV[0][2]
    ent = {e['id']: e for e in d['inspector_federal']['entes']}
    return ent['imss']['cp2025']['ejercido'], ent['issste']['cp2025']['ejercido'], d['inspector_federal']['fuentes']['cp2025']


def salud(d):
    """Los temas del bot y de las páginas. `d` es window.AUDIT_DB."""
    cp_imss, cp_issste, fcp = chequeo(d)
    CP = {'tx': fcp['corto'], 'url': fcp['url'], 'sha256': fcp['sha256']}
    por_dh = SEM['funcionamiento'] / ADSCRITA[1]
    srv = {s[0]: s for s in SERV}
    con, esp, urg, iq = srv['Consultas, en total'], srv['· de especialidad'], srv['· de urgencias'], srv['Intervenciones quirúrgicas']
    med = REC[0]
    t = {}
    t['imss_dinero'] = {
        'tit': 'Cuánto gasta el IMSS en tu salud',
        'h': '<p>En 2025 el IMSS ejerció <b>%s</b> en total (Cuenta Pública), pero no todo es salud: también paga pensiones, guarderías y riesgos de trabajo. '
             'Lo que paga tu atención médica es el <b>Seguro de Enfermedad y Maternidad</b>. Ese seguro gastó <b>%s</b> en 2025:</p><ul class="pa-lista">'
             '<li><b>%s</b> en operar: %s de sueldos, %s de materiales y medicinas, y %s de servicios generales;</li>'
             '<li><b>%s</b> en pensiones y jubilaciones, que el cuadro carga a este seguro sin decir de quién son.</li></ul>'
             '<p>Ingresó %s, así que <b>gastó %s más de lo que recibió</b>. Otros seguros cerraron con excedente, sobre todo Invalidez y Vida (%s); '
             'con todos juntos, el IMSS cerró el año con un faltante de %s.</p>'
             '<p>Lo que gastó en operar equivale a <b>$%s por cada persona adscrita</b> a una clínica familiar (%s personas).</p>'
             '<p class="pa-chico">Ojo: la Cuenta Pública es presupuesto y la Memoria es contabilidad. No se suman ni se restan entre sí.</p>' % (
                 _mdp(cp_imss * 1e6), _mdp(SEM['gastos']), _mdp(SEM['funcionamiento']), _mdp(SEM['personales']), _mdp(SEM['materiales']),
                 _mdp(SEM['generales']), _mdp(SEM['pensiones']), _mdp(SEM['ingresos']), _mdp(-SEM['resultado']), _mdp(IV_RESULTADO), _mdp(-IMSS_RESULTADO),
                 _n(por_dh), _n(ADSCRITA[1])),
        'fu': [_o('Gasto ejercido del IMSS en 2025', CP),
               _o('Ingresos y gastos del Seguro de Enfermedad y Maternidad, 2025 (cuadro XIII.45)', _m('XIII', 'cuadro XIII.45')),
               _o('Población adscrita a unidad de medicina familiar, 2025 (cuadro II.9)', _m('II', 'cuadro II.9')),
               _o('Gasto de operación por persona adscrita', _m('XIII', 'cuadros XIII.45 y II.9'), '%s ÷ %s' % (_mdp(SEM['funcionamiento']), _n(ADSCRITA[1])))],
        'ci': [{'v': _mdp(SEM['gastos']), 'etq': 'gastó el seguro que paga tu atención médica en 2025', 'e': 'oficial'},
               {'v': _mdp(-SEM['resultado']), 'etq': 'más de lo que ingresó ese seguro', 'e': 'oficial'},
               {'v': '$' + _n(por_dh), 'etq': 'de operación por persona adscrita', 'e': 'derivado'}],
        'sug': ['¿Cuántas consultas dio el IMSS en 2025?', '¿Es cierto que el IMSS hizo 1.78 millones de cirugías?', '¿Cuántos médicos tiene el IMSS?']}
    t['imss_servicios'] = {
        'tit': 'Lo que resolvió el IMSS con ese dinero',
        'h': '<p>En 2025 el IMSS dio <b>%s consultas</b>, %s más que en 2018. Las de <b>especialidad</b> crecieron más que ninguna: <b>%s</b>, %s más. '
             'Las de <b>urgencias</b>, en cambio, bajaron: %s, %s menos. Hubo %s egresos hospitalarios y %s intervenciones quirúrgicas (%s más que en 2018).</p>'
             '<p>Un número de gestión dice <b>cuánto se hizo, no si se hizo bien ni a tiempo</b>: la Memoria no trae cuánto se espera una consulta o una cirugía.</p>' % (
                 _n(con[3]), _pct(con[1], con[3]), _n(esp[3]), _pct(esp[1], esp[3]), _n(urg[3]), _pct(urg[1], urg[3]),
                 _n(srv['Egresos hospitalarios'][3]), _n(iq[3]), _pct(iq[1], iq[3])),
        'fu': [_o('Consultas por tipo, 2018 a 2025 (cuadro IV.3)', _m('IV', 'cuadro IV.3')),
               _o('Egresos e intervenciones quirúrgicas, 2018 a 2025 (cuadro IV.2). No incluyen lo que se dio al IMSS-Bienestar', _m('IV', 'cuadro IV.2')),
               _o('Cambio contra 2018', _m('IV', 'cuadros IV.2 y IV.3'), '(2025 − 2018) ÷ 2018'),
               PEND_ESPERA],
        'ci': [{'v': _n(con[3]), 'etq': 'consultas del IMSS en 2025', 'e': 'oficial'},
               {'v': _var(esp[1], esp[3]), 'etq': 'consultas de especialidad contra 2018', 'e': 'derivado'},
               {'v': _var(urg[1], urg[3]), 'etq': 'consultas de urgencias contra 2018', 'e': 'derivado'}],
        'sug': ['¿Cuánto espera alguien una cirugía en el IMSS?', '¿Cuántos médicos tiene el IMSS?', '¿Qué pasó con el Seguro Popular?']}
    t['imss_recursos'] = {
        'tit': 'Con cuántos médicos, camas y quirófanos',
        'h': '<p>El IMSS pasó de %s a <b>%s médicas y médicos</b> entre 2018 y 2025 (%s), y de %s a %s camas en servicio (%s). '
             'Son <b>%s médicos por cada mil personas adscritas</b>.</p>'
             '<p>Algo que pocos dicen: los hospitales están <b>menos ocupados</b> que antes de la pandemia. En 2018 se ocupaba el %s %% de las camas; en 2025, el %s %%. '
             'Puede ser buena señal (hay más camas) o un aviso (faltan especialistas, enfermería o insumos para usarlas): la Memoria no lo explica.</p>' % (
                 _n(med[1]), _n(med[2]), _var(med[1], med[2]), _n(REC[3][1]), _n(REC[3][2]), _var(REC[3][1], REC[3][2]),
                 format(round(1000.0 * med[2] / ADSCRITA[1], 2), '.2f'), format(OCUPACION[0], '.1f'), format(OCUPACION[1], '.1f')),
        'fu': [_o('Personal médico, 2018 y 2025 (cuadro XIII.7)', _m('XIII', 'cuadro XIII.7')),
               _o('Camas, quirófanos y consultorios (cuadro XIII.10)', _m('XIII', 'cuadro XIII.10')),
               _o('Porcentaje de ocupación hospitalaria y días de estancia (cuadros XV.11 y XV.10)', _m('XV', 'cuadros XV.10 y XV.11')),
               _o('Médicos por cada mil personas adscritas', _m('XIII', 'cuadros XIII.7 y II.9'), '%s ÷ %s × 1,000' % (_n(med[2]), _n(ADSCRITA[1])))],
        'ci': [{'v': _n(med[2]), 'etq': 'médicas y médicos del IMSS en 2025', 'e': 'oficial'},
               {'v': format(OCUPACION[1], '.1f') + ' %', 'etq': 'de las camas de hospital ocupadas en 2025 (90.0 % en 2018)', 'e': 'oficial'}],
        'sug': ['¿Cuántas consultas dio el IMSS en 2025?', '¿Cuánto gasta el IMSS en salud?']}
    t['imss_cotejo'] = {
        'tit': 'Lo que el IMSS anuncia contra lo que registra',
        'h': '<p>El 13 de enero de 2026 el IMSS presentó sus resultados de 2025 en la conferencia de Palacio Nacional (boletín 023/2026). Lo cotejamos contra su propia '
             '<b>Memoria Estadística</b>: <b>las consultas cuadran; las cirugías, no</b>. El boletín habla de 1.78 millones de cirugías y un aumento de 30 %%; '
             'la Memoria registra %s intervenciones quirúrgicas y un aumento de %s. Puede que cuenten cosas distintas, pero ninguno de los dos documentos lo dice.</p>'
             '<p>Para 2026 el IMSS se puso metas: %s. Con la Memoria de 2026 se podrá ver si se cumplieron.</p>' % (
                 _n(iq[3]), _pct(iq[2], iq[3]), '; '.join('%s, %s' % (a.lower(), b) for a, b in METAS_2026)),
        'fu': [_o('Lo que anunció el IMSS de 2025 y sus metas de 2026', BOL),
               _o('Consultas e intervenciones quirúrgicas registradas (cuadros IV.2 y IV.3)', _m('IV', 'cuadros IV.2 y IV.3')),
               _o('Diferencias entre los dos documentos', _m('IV', 'cuadros IV.2 y IV.3'), 'cifra del boletín contra cifra de la Memoria'),
               PEND_ESPERA],
        'ci': [{'v': _n(iq[3]), 'etq': 'intervenciones quirúrgicas en la Memoria (el boletín dice 1.78 millones de cirugías)', 'e': 'oficial'}],
        'sug': ['¿Cuántas consultas dio el IMSS en 2025?', '¿Cuánto espera alguien una cirugía en el IMSS?']}
    t['transicion'] = {
        'tit': 'Del Seguro Popular al IMSS-Bienestar',
        'h': '<p>Quien no tiene IMSS ni ISSSTE ha pasado por <b>tres instituciones en seis años</b>:</p><ul class="pa-lista">'
             '<li>hasta 2019, el <b>Seguro Popular</b> (Sistema de Protección Social en Salud);</li>'
             '<li>desde el <b>1 de enero de 2020</b>, el <b>INSABI</b>, que recibió los recursos de la comisión que manejaba el Seguro Popular (decreto del DOF del 29-11-2019);</li>'
             '<li>desde el decreto del DOF del <b>29 de mayo de 2023</b>, el <b>IMSS-Bienestar</b>: se ordenó extinguir el INSABI y pasarle sus recursos.</li></ul>'
             '<p>Por eso <b>las series se rompen</b>: comparar 2019 contra 2024 es comparar instituciones distintas, que además cuentan de otra forma. Quien te muestre '
             '«más consultas que con el Seguro Popular» tiene que decir de qué documento sale cada año.</p>',
        'fu': [_o('Decreto del 29-11-2019: entrada en vigor el 1 de enero de 2020 y traspaso de recursos al INSABI (transitorios primero y tercero)', LGS),
               _o('Decreto del 29-05-2023: el Sistema de Salud para el Bienestar, la extinción del INSABI y el traspaso al IMSS-Bienestar (transitorios)', LGS)],
        'sug': ['¿Qué sabemos del IMSS-Bienestar?', '¿Cuánto gasta el ISSSTE?']}
    t['imss_bienestar'] = {
        'tit': 'Lo que sabemos del IMSS-Bienestar',
        'h': '<p>El IMSS-Bienestar atiende a quien no tiene seguridad social en los estados que se adhirieron. En conferencias se han dado cifras de sus consultas de 2025, '
             'pero <b>no encontramos un informe oficial</b> con sus consultas, egresos, cirugías y su gasto completo. La Memoria del IMSS tiene un capítulo del IMSS-Bienestar, '
             'pero su archivo no se pudo descargar (el enlace devuelve una página web, no el archivo).</p>'
             '<p>Mientras no haya documento, <b>no publicamos cifras</b> de lo que dicen las conferencias.</p>',
        'fu': [PEND_BIEN],
        'sug': ['¿Qué pasó con el Seguro Popular?', '¿Cuántas consultas dio el IMSS en 2025?']}
    t['issste'] = {
        'tit': 'El ISSSTE: el dinero sí, los números todavía no',
        'h': '<p>El ISSSTE, que atiende a quienes trabajan para el gobierno, ejerció <b>%s</b> en 2025 (Cuenta Pública). Igual que en el IMSS, ahí van también pensiones '
             'y otras prestaciones, no solo salud.</p>'
             '<p>Lo que resolvió con ese dinero está en su <b>anuario estadístico</b>, que el ISSSTE publica cada año. El 27-10-2026 su servidor no respondió y no lo pudimos cotejar: '
             'queda pendiente, como falta nuestra.</p>' % _mdp(cp_issste * 1e6),
        'fu': [_o('Gasto ejercido del ISSSTE en 2025', CP), PEND_ISSSTE],
        'ci': [{'v': _mdp(cp_issste * 1e6), 'etq': 'ejerció el ISSSTE en 2025', 'e': 'oficial'}],
        'sug': ['¿Cuánto gasta el IMSS en salud?', '¿Qué pasó con el Seguro Popular?']}
    assert sorted(t) == sorted(PAGINA_DE)
    for k, x in t.items():
        x['ir'] = [PAGINA_DE[k][0] + '#' + PRE + k, PAGINA_DE[k][1]]
        x['aqui'] = x['ir']
    return {'t': t, 'pag': [PORTADA, PORTADA_TIT]}


def secciones(d, temas):
    """Las secciones de una página de Datos: el mismo texto con que contesta el bot."""
    S = salud(d)
    out = []
    for k in temas:
        x = S['t'][k]
        extra = ''
        if k == 'imss_servicios':
            filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                html.escape(a), _n(c), _var(b18, c), _n(b18), _n(b24)) for a, b18, b24, c, _ in SERV)
            extra = ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Servicios médicos del IMSS %s</caption>'
                     '<thead><tr><th scope="col">Servicio</th><th scope="col">2025</th><th scope="col">Contra 2018 %s</th><th scope="col">2018</th>'
                     '<th scope="col">2024</th></tr></thead><tbody>%s</tbody></table></div>') % (_chip('oficial'), _chip('derivado'), filas)
        elif k == 'imss_recursos':
            filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td></tr>' % (html.escape(a), _n(b), _var(a18, b), _n(a18))
                            for a, a18, b, _, _ in REC)
            filas += '<tr><th scope="row">Ocupación hospitalaria</th><td>%s %%</td><td>%s puntos</td><td>%s %%</td></tr>' % (
                format(OCUPACION[1], '.1f'), format(OCUPACION[1] - OCUPACION[0], '.1f').replace('-', '−'), format(OCUPACION[0], '.1f'))
            filas += '<tr><th scope="row">Días promedio de estancia</th><td>%s</td><td></td><td>%s</td></tr>' % (ESTANCIA[1], ESTANCIA[0])
            extra = ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Recursos del IMSS %s</caption>'
                     '<thead><tr><th scope="col">Recurso</th><th scope="col">2025</th><th scope="col">Contra 2018 %s</th><th scope="col">2018</th></tr></thead>'
                     '<tbody>%s</tbody></table></div>') % (_chip('oficial'), _chip('derivado'), filas)
        elif k == 'imss_cotejo':
            filas = ''.join('<li><b>%s</b> → <b>%s</b>. %s</li>' % (html.escape(a), html.escape(r), html.escape(e)) for a, r, e in COTEJO)
            extra = ('<h3>El boletín 023/2026 contra la Memoria Estadística 2025</h3><ul class="pa-lista">%s</ul>'
                     '<p class="pa-chico">«Consta»: coincide, o el redondeo no se aleja más de 10 %%. «Matiz»: se acerca pero no es lo que dice. '
                     '«No cuadra»: los dos documentos del IMSS dan cifras distintas. Tiempo de espera: %s</p>') % (filas, _chip('pendiente', 'salud-tiempos-espera'))
        out.append({'id': PRE + k, 'titulo': html.escape(x['tit']), 'texto': '', 'tarjetas': [],
                    'bloque': bloque_tema(x, extra, x['aqui'][0].split('#')[0])})
    return out
