# -*- coding: utf-8 -*-
"""Justicia ambiental: lo que cuesta y lo que resuelve la PROFEPA (auditoría
de gestión, pedido del autor, 27-10-2026: el ambiente «tanto de dinero como de
números» de gestión administrativa; «continuemos», 28-10-2026).

Mismo molde que gestion_judicial.py y gestion_salud.py: el dinero junto a lo
que se hizo con él, con lo derivado a la vista y lo que falta con su ficha.
Documentos cotejados el 28-10-2026 (huella SHA-256 abajo):

- PROFEPA, Informes de Actividades 2022, 2023 y 2024 (gob.mx): denuncias
  populares, procedimientos de inspección, rezago, multas, recursos de
  revisión, denuncias ante la FGR y el ejercicio del presupuesto. Las páginas
  que se citan son las del archivo PDF, no las impresas.
- Ley General del Equilibrio Ecológico y la Protección al Ambiente (LGEEPA),
  texto vigente (Cámara de Diputados, última reforma DOF 19-01-2026): la
  denuncia popular, arts. 189 a 204.
- El presupuesto 2026 y el proyecto 2027 de la PROFEPA ya estaban en la base
  (ambiente.presupuesto, unidad E00).

Lo que se buscó y no está: el Informe de Actividades 2025 de la PROFEPA (en su
página de gob.mx «Informe de Actividades 2025» está el informe del Comité de
Ética, no el de la Procuraduría), cuántas denuncias admitidas se concluyeron y
por qué causa, cuánto tarda una denuncia, el rezago al cierre de 2024, cuánto
se cobró de las multas y en qué terminaron las denuncias ante la FGR.

La lee asistente_judicial.poderes de apartados.py (como un «Poder» más de
Datos) y asistente.py (D.amg del chat).
"""

import html

from asistente_legislativo import _chip, bloque_tema

_G = 'https://www.gob.mx/cms/uploads/attachment/file/'
INF = {
    2022: {'tx': 'PROFEPA, Informe de Actividades 2022', 'url': _G + '830999/Informe_de_Actividades_Profepa_2022.pdf',
           'sha256': '11b3e2ab93259b1ec51fb2c5fc9f6e1b4e889e23774d6ea36afee8b95f6cb951'},
    2023: {'tx': 'PROFEPA, Informe de Actividades 2023', 'url': _G + '946951/INFORME_DE_ACTIVIDADES_2023..pdf',
           'sha256': '3e06d48d9a0e8fe91080db1aa4c8921634cdde740baed7ee4cde0c013729d85a'},
    2024: {'tx': 'PROFEPA, Informe de Actividades 2024', 'url': _G + '1038916/Informe_Anual_Profepa_2025_VF_.pdf',
           'sha256': '33c1ed8f40acfe93e079aaac4eaa68f211e2057aaa7c9774af1d8b8bf5f814ec'},
}
INFORMES = 'https://www.gob.mx/profepa/articulos/informes-de-actividades-360477'
LGEEPA = {'tx': 'LGEEPA, texto vigente (Cámara de Diputados, última reforma DOF 19-01-2026)',
          'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGEEPA.pdf',
          'sha256': '0574853d06020030188e8aee1eae5dabb2b476ac630cc52be631a48d2b91adbc'}


def _i(anio, pag, que=''):
    f = dict(INF[anio])
    f['tx'] = '%s, p. %s del PDF%s' % (f['tx'], pag, (' (%s)' % que) if que else '')
    return f


def _ley(arts):
    f = dict(LGEEPA)
    f['tx'] = '%s, %s' % (f['tx'], arts)
    return f


# Denuncias populares: (año, iniciadas, no admitidas por incompetencia,
# admitidas, concluidas, en trámite, página del PDF). En los tres años,
# concluidas + en trámite = iniciadas.
DEN = [(2022, 6317, 2421, 3896, 3573, 2744, 5),
       (2023, 7010, 3115, 3895, 4224, 2786, 6),
       (2024, 7939, 3821, 4118, 4640, 3299, 10)]

# Presupuesto (millones de pesos): (año, original, modificado = ejercido, página).
PRES = [(2022, 776.48, 921.70, 56), (2023, 830.34, 914.23, 67), (2024, 896.07, 1040.89, 73)]
# 2024 por programa (tabla 19) y por capítulo (tabla 20), millones.
G005 = (187.67, 333.89)        # Inspección y Vigilancia: original, modificado
M001 = (708.41, 707.00)        # Apoyo administrativo
PERSONALES_2024 = 691.86       # capítulo 1000, ejercido
EXCEDENTES_2024 = 291.77       # ampliaciones por ingresos excedentes (multas y derechos)
CAPITULOS_2024 = (691.86, 24.14, 324.50, 0.39)

# Procedimientos de inspección y vigilancia concluidos: (año, total, del año, de años anteriores, página).
PROC = [(2022, 5513, 1797, 3716, 26), (2024, 6957, 2011, 4946, 31)]
# Informe 2023, p. 29: el rezago.
REZ_INICIO = (10621, [(2012, 1), (2013, 13), (2014, 127), (2015, 457), (2016, 1348), (2017, 3299), (2018, 5376)])
REZ_RESUELTO_2023 = 10570
REZ_1923 = {'iniciados': 38736, 'resueltos': 27557, 'pendientes': 11179, 'de_2023': 4675, 'de_19_22': 6504}

MULTAS_IND_2024 = (325, 925.88)   # multas de inspección industrial: número y millones (p. 17)
VISITAS_IND_2024 = 3227
FGR = [(2023, 814, 31), (2024, 709, 33)]   # denuncias, querellas y coadyuvancias ante la FGR
# Recursos de revisión 2024 (pp. 31 y 32).
REV = {'recibidos': 506, 'resueltos_2024': 166, 'resueltos_previos': 178, 'confirma': 71, 'desecha': 44, 'sobresee': 7,
       'nulidad_efectos': 22, 'cerrados': 2, 'nulidad_lisa': 20}

PORTADA = 'datos-justicia-ambiental.html'
PORTADA_TIT = 'Justicia ambiental'
PAGINAS = [
    ('datos-justicia-ambiental-denuncias.html', '📣', 'Tus denuncias ante la PROFEPA', 'Cuánto cuesta la Procuraduría, cuántas denuncias recibe y cuántas resuelve',
     'Cuánto dinero ejerció la PROFEPA, cuántas denuncias populares recibió de 2022 a 2024, cuántas investigó y cuántas concluyó, y qué plazos le pone la ley. '
     'Cotejado con sus Informes de Actividades y con la LGEEPA.',
     ['dinero', 'denuncias', 'plazos']),
    ('datos-justicia-ambiental-rezago.html', '🗂️', 'Expedientes, multas y la Fiscalía', 'El rezago de los procedimientos, lo que se multa y lo que llega a la FGR',
     'Cuántos procedimientos de inspección resuelve la PROFEPA y cuántos se le acumulan, cuánto multa, cuántas denuncias lleva a la Fiscalía, '
     'y si lo que dice su informe cuadra con sus propias tablas.',
     ['rezago', 'multas', 'cotejo']),
]
PAGINA_DE = {k: (p[0], p[2]) for p in PAGINAS for k in p[5]}
PRE = 'amg-'

PEND_CAUSA = {'que': 'Cuántas denuncias admitidas concluyó la PROFEPA, por qué causa y en cuánto tiempo', 'e': 'pendiente', 'p': 'ambiente-denuncias-causa',
              'fu': {'tx': 'PROFEPA, Informes de Actividades', 'url': INFORMES}}
PEND_REZ = {'que': 'Cuántos procedimientos de inspección quedaron sin resolver al cierre de 2024', 'e': 'pendiente', 'p': 'ambiente-profepa-rezago',
            'fu': {'tx': 'PROFEPA, Informes de Actividades', 'url': INFORMES}}
PEND_COBRO = {'que': 'Cuánto se cobró de las multas que impuso la PROFEPA', 'e': 'pendiente', 'p': 'ambiente-multas-cobradas',
              'fu': {'tx': 'PROFEPA, Informes de Actividades', 'url': INFORMES}}
PEND_FGR = {'que': 'En qué terminaron las denuncias de la PROFEPA ante la FGR', 'e': 'pendiente', 'p': 'ambiente-profepa-fgr',
            'fu': {'tx': 'PROFEPA, Informes de Actividades', 'url': INFORMES}}
PEND_2025 = {'que': 'El Informe de Actividades 2025 de la PROFEPA', 'e': 'pendiente', 'p': 'ambiente-profepa-informe-2025',
             'fu': {'tx': 'PROFEPA, Informes de Actividades', 'url': INFORMES}}


def _o(que, fu, op=None, e=None):
    d = {'que': que, 'e': e or ('derivado' if op else 'oficial'), 'fu': fu}
    if op:
        d['op'] = op
    return d


def _n(v):
    return format(int(round(v)), ',')


def _m(v):
    return '$%s millones' % format(v, ',.1f')


def _p(a, b):
    return format(round(100.0 * a / b, 1), '.1f') + ' %'


def _admitidas_concluidas(x):
    """Concluidas entre las admitidas, si las turnadas cuentan como concluidas (art. 199, fr. I)."""
    return x[4] - x[2]


def chequeo(d):
    for x in DEN:
        assert x[2] + x[3] == x[1] and x[4] + x[5] == x[1], x
        assert x[3] - _admitidas_concluidas(x) == x[5]
    for x in PROC:
        assert x[2] + x[3] == x[1]
    assert sum(c for _, c in REZ_INICIO[1]) == REZ_INICIO[0]
    r = REZ_1923
    assert r['iniciados'] - r['resueltos'] == r['pendientes'] == r['de_2023'] + r['de_19_22']
    assert REZ_RESUELTO_2023 + r['resueltos'] == 38127   # «se resolvieron 38,127 procedimientos»
    assert abs(G005[1] + M001[1] - PRES[2][2]) < 0.01 and abs(sum(CAPITULOS_2024) - PRES[2][2]) < 0.01
    v = REV
    assert v['confirma'] + v['desecha'] + v['sobresee'] + v['nulidad_efectos'] + v['cerrados'] + v['nulidad_lisa'] == v['resueltos_2024']
    u = next(x for x in d['ambiente']['presupuesto']['unidades'] if x['ur'] == 'E00')
    return u, d['ambiente']['fuentes']


def temas(d):
    """Los temas del bot y de las páginas. `d` es window.AUDIT_DB."""
    u, F = chequeo(d)
    PEF = {'tx': F['PEF'].get('corto') or F['PEF']['doc'], 'url': F['PEF']['url'], 'sha256': F['PEF'].get('sha256')}
    PP = {'tx': F['PPEF2027'].get('corto') or F['PPEF2027']['doc'], 'url': F['PPEF2027']['url']}
    ap26, py27 = u['aprobado'] / 1e6, u['proyecto2027'] / 1e6
    p24 = PRES[2]
    assert ap26 < p24[1]   # el texto dice que 2026 tiene menos que 2024
    d22, d24 = DEN[0], DEN[2]
    ac24 = _admitidas_concluidas(d24)
    pend_previos = REZ_1923['pendientes'] + (REZ_INICIO[0] - REZ_RESUELTO_2023) - PROC[1][3]
    t = {}
    t['dinero'] = {
        'tit': 'Cuánto cuesta la PROFEPA',
        'h': '<p>La Procuraduría Federal de Protección al Ambiente ejerció <b>%s en 2024</b>: empezó el año con %s aprobados y terminó con %s más: le ampliaron %s por lo que '
             'cobró de más en multas y derechos, y le recortaron otras partidas. En 2022 ejerció %s y en 2023, %s.</p>'
             '<p>¿En qué se va? <b>%s de cada 100 pesos son sueldos</b> (%s). Por programa, el de <b>Inspección y Vigilancia</b> arrancó 2024 con apenas %s '
             'y terminó con %s; el resto es «apoyo administrativo».</p>'
             '<p>Para <b>2026</b> la Cámara de Diputados le aprobó <b>%s</b>, menos que lo que se le aprobó en 2024 (sin contar inflación), y el proyecto de 2027 propone %s.</p>'
             '<p class="pa-chico">La PROFEPA hace mucho más que atender denuncias (inspecciona industria, bosques, costas, puertos y fronteras), así que '
             'no dividimos su presupuesto entre sus denuncias: ese número no sería el costo de una denuncia.</p>' % (
                 _m(p24[2]), _m(p24[1]), _m(p24[2] - p24[1]), _m(EXCEDENTES_2024), _m(PRES[0][2]), _m(PRES[1][2]),
                 format(round(100.0 * PERSONALES_2024 / p24[2]), '.0f'), _m(PERSONALES_2024), _m(G005[0]), _m(G005[1]), _m(ap26), _m(py27)),
        'fu': [_o('Presupuesto original y ejercido 2024, por programa y por capítulo (tablas 19 y 20)', _i(2024, 73, 'tablas 19 y 20')),
               _o('Presupuesto 2022', _i(2022, 56)), _o('Presupuesto 2023', _i(2023, 67)),
               _o('Sueldos como parte del gasto ejercido de 2024', _i(2024, 74, 'tabla 20'), '%s ÷ %s' % (_m(PERSONALES_2024), _m(p24[2]))),
               _o('Presupuesto aprobado 2026 de la PROFEPA (unidad E00 del Ramo 16)', PEF),
               _o('Proyecto de presupuesto 2027', PP)],
        'ci': [{'v': _m(p24[2]), 'etq': 'ejerció la PROFEPA en 2024', 'e': 'oficial'},
               {'v': _p(PERSONALES_2024, p24[2]), 'etq': 'de su gasto fueron sueldos', 'e': 'derivado'},
               {'v': _m(ap26), 'etq': 'aprobado para 2026', 'e': 'oficial'}],
        'sug': ['¿Cuántas denuncias resuelve la PROFEPA?', '¿Cuánto rezago tiene la PROFEPA?', '¿Cuánto tarda la PROFEPA en atender una denuncia?']}
    t['denuncias'] = {
        'tit': 'Cuántas denuncias recibe y cuántas resuelve',
        'h': '<p>En 2024 la PROFEPA abrió <b>%s expedientes de denuncia popular</b> (%s más que en 2022). <b>%s no los admitió</b> por no ser de su competencia y los turnó '
             'a otra autoridad; investigó %s. Al cierre del año informó <b>%s concluidos</b> y %s en trámite.</p>'
             '<p>Lo que el informe no dice: <b>sus cuentas cuadran solo si las denuncias turnadas cuentan como «concluidas»</b>, algo que la ley permite (art. 199, fr. I). '
             'Si es así, de las %s denuncias que sí investigó en 2024, <b>concluyó %s en el mismo año: %s</b>. En 2022 fue el %s. '
             'La PROFEPA no publica cuántas concluyó por cada causa ni cuánto tardó.</p>' % (
                 _n(d24[1]), _p(d24[1] - d22[1], d22[1]), _n(d24[2]), _n(d24[3]), _n(d24[4]), _n(d24[5]),
                 _n(d24[3]), _n(ac24), _p(ac24, d24[3]), _p(_admitidas_concluidas(d22), d22[3])),
        'fu': [_o('Expedientes de denuncia popular 2024 (tabla 1)', _i(2024, 10, 'tabla 1')),
               _o('Denuncias populares 2023', _i(2023, 6)), _o('Denuncias populares 2022', _i(2022, 5)),
               _o('Causas por las que se concluye una denuncia: la primera es la incompetencia de la PROFEPA', _ley('art. 199')),
               _o('Denuncias investigadas que se concluyeron en el año', _i(2024, 10, 'tabla 1'),
                  'concluidas − no admitidas: %s − %s = %s; %s ÷ %s admitidas' % (_n(d24[4]), _n(d24[2]), _n(ac24), _n(ac24), _n(d24[3]))),
               PEND_CAUSA, PEND_2025],
        'ci': [{'v': _n(d24[1]), 'etq': 'denuncias populares en 2024', 'e': 'oficial'},
               {'v': _n(d24[2]), 'etq': 'no admitidas y turnadas a otra autoridad', 'e': 'oficial'},
               {'v': _p(ac24, d24[3]), 'etq': 'de las investigadas, concluidas en el mismo año', 'e': 'derivado'}],
        'sug': ['¿Cuánto tarda la PROFEPA en atender una denuncia?', '¿Cuánto cuesta la PROFEPA?', '¿Cuánto rezago tiene la PROFEPA?']}
    t['plazos'] = {
        'tit': 'Cuánto debe tardar una denuncia ambiental',
        'h': '<p>La LGEEPA le pone a la PROFEPA plazos para <b>empezar</b>, no para <b>terminar</b>:</p><ul class="pa-lista">'
             '<li>al recibir tu denuncia te da número de expediente, y <b>en 10 días</b> te notifica si la admite o la turna a otra autoridad (art. 191);</li>'
             '<li>si la admite, a quien denunciaste le da <b>15 días hábiles</b> para presentar pruebas (art. 192);</li>'
             '<li>la cierra por alguna de las causas del art. 199: incompetencia, recomendación, que no haya violación, falta de interés, acumulación, conciliación, '
             'resolución de inspección o desistimiento.</li></ul>'
             '<p>Pero <b>el capítulo de la denuncia popular (arts. 189 a 204) no fija un plazo para concluirla</b>, y la PROFEPA no publica cuánto tarda. '
             'Por eso no se puede saber si tu denuncia va lenta.</p>',
        'fu': [_o('Registro, acuerdo de calificación en 10 días y turno a otra autoridad', _ley('art. 191')),
               _o('Plazo de 15 días hábiles para pruebas', _ley('art. 192')),
               _o('Causas de conclusión', _ley('art. 199')), PEND_CAUSA],
        'sug': ['¿Cuántas denuncias resuelve la PROFEPA?', '¿Cuánto rezago tiene la PROFEPA?']}
    t['rezago'] = {
        'tit': 'El rezago: lo que se resuelve y lo que se acumula',
        'h': '<p>Cuando una inspección encuentra irregularidades, se abre un <b>procedimiento administrativo</b>. Al empezar la administración anterior (diciembre de 2018), la PROFEPA tenía '
             '<b>%s expedientes sin resolver</b> de 2012 a 2018; para 2023 informó haber resuelto %s (%s).</p>'
             '<p>Lo que no se dice tan fuerte: en el camino se juntó <b>otro rezago, más grande</b>. De %s procedimientos iniciados de 2019 a 2023, '
             'al cierre de 2023 quedaban <b>%s sin resolver</b>.</p>'
             '<p>En 2024 concluyó %s procedimientos: %s de ese año y %s de años anteriores. Con las cifras de sus dos informes, '
             '<b>al cerrar 2024 seguían sin resolver al menos %s de años anteriores</b>, más los de 2024 que no se cerraron, cifra que el informe 2024 ya no da.</p>' % (
                 _n(REZ_INICIO[0]), _n(REZ_RESUELTO_2023), _p(REZ_RESUELTO_2023, REZ_INICIO[0]), _n(REZ_1923['iniciados']), _n(REZ_1923['pendientes']),
                 _n(PROC[1][1]), _n(PROC[1][2]), _n(PROC[1][3]), _n(pend_previos)),
        'fu': [_o('Rezago al inicio de la administración, programa de abatimiento y procedimientos 2019 a 2023', _i(2023, 29)),
               _o('Procedimientos concluidos en 2024', _i(2024, 31)), _o('Procedimientos concluidos en 2022', _i(2022, 26)),
               _o('Procedimientos de años anteriores sin resolver al cierre de 2024 (cota mínima)', _i(2024, 31),
                  '(%s pendientes de 2019 a 2023 + %s del rezago viejo) − %s resueltos de años anteriores en 2024' % (
                      _n(REZ_1923['pendientes']), _n(REZ_INICIO[0] - REZ_RESUELTO_2023), _n(PROC[1][3]))),
               PEND_REZ],
        'ci': [{'v': _n(REZ_1923['pendientes']), 'etq': 'procedimientos de 2019 a 2023 sin resolver al cierre de 2023', 'e': 'oficial'},
               {'v': _n(pend_previos), 'etq': 'de años anteriores, aún sin resolver al cierre de 2024 (al menos)', 'e': 'derivado'}],
        'sug': ['¿Cuánto multa la PROFEPA?', '¿Cuántas denuncias resuelve la PROFEPA?']}
    t['multas'] = {
        'tit': 'Lo que se multa y lo que llega a la Fiscalía',
        'h': '<p>En 2024, de sus %s visitas de inspección a la industria, la PROFEPA impuso <b>%s multas por %s</b>. Pero <b>imponer no es cobrar</b>: '
             'el informe no dice cuánto de eso se pagó, cuánto se impugnó ni cuánto se conmutó por inversión ambiental (art. 173 de la LGEEPA).</p>'
             '<p>Lo más cercano es que en 2024 recibió %s extra por ingresos excedentes de <b>multas y derechos juntos</b>, sin separar unos de otros.</p>'
             '<p>Además presentó <b>%s denuncias, querellas y coadyuvancias ante la Fiscalía General de la República</b> por delitos ambientales (%s en 2023). '
             'Ni sus informes ni ningún documento que encontráramos dicen <b>cuántas terminaron ante un juez</b>.</p>' % (
                 _n(VISITAS_IND_2024), _n(MULTAS_IND_2024[0]), _m(MULTAS_IND_2024[1]), _m(EXCEDENTES_2024), _n(FGR[1][1]), _n(FGR[0][1])),
        'fu': [_o('Visitas de inspección industrial y multas impuestas en 2024', _i(2024, 17)),
               _o('Ampliación por ingresos excedentes de multas y derechos', _i(2024, 74)),
               _o('Denuncias ante la FGR en 2024', _i(2024, 33)), _o('Denuncias ante la FGR en 2023', _i(2023, 31)),
               _o('Conmutación de multas por inversión', _ley('art. 173')), PEND_COBRO, PEND_FGR],
        'ci': [{'v': _m(MULTAS_IND_2024[1]), 'etq': 'en multas impuestas a la industria en 2024', 'e': 'oficial'},
               {'v': _n(FGR[1][1]), 'etq': 'denuncias y querellas ante la FGR en 2024', 'e': 'oficial'}],
        'sug': ['¿Cuánto rezago tiene la PROFEPA?', '¿Cuánto cuesta la PROFEPA?']}
    v = REV
    fav = v['resueltos_2024'] - v['nulidad_lisa']
    t['cotejo'] = {
        'tit': 'Lo que dice el informe contra sus propias tablas',
        'h': '<p>Cotejamos el Informe 2024 de la PROFEPA contra sus propias cifras. <b>Casi todo cuadra</b>, con tres detalles que el informe no aclara:</p><ul class="pa-lista">'
             '<li><b>Una tabla del presupuesto trae dos erratas</b> (tabla 19): el total ejercido dice «1,40.89» y el ejercido del programa de inspección dice 339.89 '
             'cuando su modificado es 333.89. La otra tabla (la 20) sí suma %s.</li>'
             '<li><b>«En el 87.7 %% se sostuvo la legalidad»</b> de los recursos de revisión: con sus números (%s de %s) es %s, y en esa cuenta suma, como el propio informe dice, %s '
             '<b>nulidades «para determinados efectos»</b>: actos que se anularon para reponerlos por vicios de forma. Sin ellas, es %s.</li>'
             '<li><b>«99.5 %% del rezago resuelto»</b> (informe 2023) consta: %s de %s. Pero es el rezago de 2012 a 2018; el de 2019 a 2023 era de %s.</li></ul>' % (
                 _m(PRES[2][2]), _n(fav), _n(v['resueltos_2024']), _p(fav, v['resueltos_2024']), _n(v['nulidad_efectos']),
                 _p(fav - v['nulidad_efectos'], v['resueltos_2024']), _n(REZ_RESUELTO_2023), _n(REZ_INICIO[0]), _n(REZ_1923['pendientes'])),
        'fu': [_o('Ejercicio presupuestal 2024 por programa y por capítulo (tablas 19 y 20)', _i(2024, 73, 'tablas 19 y 20')),
               _o('Recursos de revisión recibidos y resueltos en 2024', _i(2024, 32)),
               _o('Recursos de revisión con resultado favorable', _i(2024, 32), '%s favorables ÷ %s resueltos; sin las nulidades para efectos: %s ÷ %s' % (
                   _n(fav), _n(v['resueltos_2024']), _n(fav - v['nulidad_efectos']), _n(v['resueltos_2024']))),
               _o('Rezago resuelto en 2023', _i(2023, 29))],
        'ci': [{'v': _p(fav, v['resueltos_2024']), 'etq': 'de recursos favorables con sus números (el informe dice 87.7 %)', 'e': 'derivado'}],
        'sug': ['¿Cuánto rezago tiene la PROFEPA?', '¿Cuánto cuesta la PROFEPA?']}
    assert sorted(t) == sorted(PAGINA_DE)
    for k, x in t.items():
        x['ir'] = [PAGINA_DE[k][0] + '#' + PRE + k, PAGINA_DE[k][1]]
        x['aqui'] = x['ir']
    return {'t': t, 'pag': [PORTADA, PORTADA_TIT]}


def secciones(d, temas_):
    """Las secciones de una página de Datos: el mismo texto con que contesta el bot."""
    S = temas(d)
    out = []
    for k in temas_:
        x = S['t'][k]
        extra = ''
        if k == 'denuncias':
            filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                a, _n(r[1]), _p(_admitidas_concluidas(r), r[3]), _n(r[3]), _n(r[2]), _n(r[4]), _n(r[5])) for r in DEN for a in [r[0]])
            extra = ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Denuncias populares ante la PROFEPA %s</caption>'
                     '<thead><tr><th scope="col">Año</th><th scope="col">Recibidas</th><th scope="col">Investigadas y concluidas en el año %s</th>'
                     '<th scope="col">Investigadas</th><th scope="col">Turnadas</th><th scope="col">Concluidas</th><th scope="col">En trámite</th></tr></thead>'
                     '<tbody>%s</tbody></table></div>') % (_chip('oficial'), _chip('derivado'), filas)
        elif k == 'dinero':
            filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td></tr>' % (a, _m(e), _m(o)) for a, o, e, _ in PRES)
            extra = ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Presupuesto de la PROFEPA, millones de pesos de cada año %s</caption>'
                     '<thead><tr><th scope="col">Año</th><th scope="col">Ejercido</th><th scope="col">Aprobado al inicio</th></tr></thead>'
                     '<tbody>%s</tbody></table></div>') % (_chip('oficial'), filas)
        out.append({'id': PRE + k, 'titulo': html.escape(x['tit']), 'texto': '', 'tarjetas': [],
                    'bloque': bloque_tema(x, extra, x['aqui'][0].split('#')[0])})
    return out
