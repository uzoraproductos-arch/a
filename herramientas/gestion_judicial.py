# -*- coding: utf-8 -*-
"""Lo que cuesta y lo que resuelve el Poder Judicial: la auditoría de gestión
(pedido del autor, 27-10-2026: «el Poder Judicial se puede ver que lleva bien
unas finanzas, pero la idea es más bien cómo lo contrarrestamos respecto a
números estadísticos. ¿Cuánto tiempo tardan en celebrar una audiencia, el
rezago que tienen?»).

El dinero ya estaba en la plataforma: el presupuesto ejercido en 2024 que el
INEGI publica en el mismo censo (inspector_poderes de window.AUDIT_DB,
herramientas/integrar_poderes_inspector.py). Aquí se le pone al lado lo que se
resolvió con él. Todo sale de un solo documento, cotejado página por página el
27-10-2026:

- INEGI, Censo Nacional de Impartición de Justicia Federal y Estatal
  (CNIJF-E) 2025, reporte de resultados 43/25 (06-11-2025), la misma copia
  de la bóveda (SHA-256 abajo). Asuntos de la Corte (gráfica 10, p. 19),
  duración de sus asuntos (tabla 13, p. 23), Tribunal Electoral (p. 24 y
  tabla 17, p. 30), órganos del Consejo de la Judicatura (gráfica 16, p. 31),
  poderes judiciales estatales (tablas 22 y 23, pp. 37 y 39), causas penales
  pendientes de concluir (gráfica 22, p. 43, y tabla 25, p. 45) y personas
  juzgadoras (tabla 6, p. 12).

Lo que se calcula (derivado, con su operación a la vista): dinero por asunto
resuelto, asuntos concluidos por cada 100 que entraron y asuntos por persona
juzgadora. Nada de eso es «lo que cuesta un juicio»: el presupuesto paga
también la administración, los edificios y la defensoría pública, y así se
dice en cada respuesta.

Lo que el censo no trae y queda en el Registro de pendientes: cuánto tarda un
juzgado o tribunal (federal o estatal) en resolver y en celebrar una
audiencia, y cuántos expedientes civiles, familiares y mercantiles quedaron
sin resolver al cierre del año.

La lee asistente_judicial.py: sus temas entran a D.jud y a la página
«Lo que cuesta y lo que resuelve» de Datos · Poder Judicial.
"""

import html

from asistente_legislativo import CPEUM

URL = 'https://www.inegi.org.mx/contenidos/programas/cnije/2025/doc/cnije_2025_resultados.pdf'
SHA = '5dfdd93b437885a370fb9f03d988b99ba191be16986828ab4be008709881dee3'
CENSO = 'INEGI, Censo Nacional de Impartición de Justicia Federal y Estatal (CNIJF-E) 2025, reporte de resultados 43/25 (06-11-2025)'
MICRO = 'https://www.inegi.org.mx/programas/cnije/2025/'


def _f(donde):
    return {'tx': '%s, %s' % (CENSO, donde), 'url': URL, 'sha256': SHA}


# Poder Judicial de la Federación, 2024: (asuntos que ingresaron, asuntos que
# egresaron o concluyeron, dónde). El presupuesto ejercido de los tres se lee
# de la base (CNIJF de integrar_poderes_inspector.py, gráfica 6, p. 13).
FED = {
    'scjn': (16370, 13979, 'gráfica 10, p. 19'),
    'oaj': (1975457, 1859221, 'gráfica 16, p. 31'),
    'tepjf': (40018, 12565, 'p. 24'),
}
FED_NOMBRE = {'scjn': 'Suprema Corte', 'oaj': 'Juzgados y tribunales federales',
              'tepjf': 'Tribunal Electoral'}
# Gráfica 6 (p. 13), millones de pesos corrientes. Es la misma cifra que la
# base guarda en inspector_poderes: se comprueba al generar.
PRES_FED = {'scjn': 5665.8, 'tepjf': 3625.7, 'oaj': 72090.0}

# Los 32 poderes judiciales estatales, 2024, en el orden de la tabla 23:
# (entidad, asuntos ingresados, asuntos determinados y/o concluidos [tabla 23,
# p. 39], causas penales del sistema acusatorio pendientes de concluir al
# cierre del año [tabla 25, p. 45], personas juzgadoras [tabla 6, p. 12]).
# Transcritas del PDF con un script, no a mano.
EST = [('AGS', 49388, 33223, 3903, 49), ('BC', 86951, 42185, 30711, 138), ('BCS', 15753, 4442, 4317, 51),
       ('CAM', 20610, 19347, 858, 82), ('COAH', 80671, 83448, 7344, 104), ('COL', 18391, 6982, 1594, 36),
       ('CHIS', 33981, 14120, 3705, 104), ('CHIH', 88321, 69522, 4514, 269), ('CDMX', 240019, 76257, 14298, 291),
       ('DGO', 34045, 18103, 23317, 71), ('GTO', 174439, 171420, 7488, 304), ('GRO', 23904, 11614, 14191, 152),
       ('HGO', 58235, 52390, 30427, 110), ('JAL', 139454, 64628, 40431, 295), ('MÉX', 266002, 176470, 58288, 441),
       ('MICH', 66007, 39020, 1546, 160), ('MOR', 27429, 11005, 1260, 65), ('NAY', 29705, 34628, 12108, 82),
       ('NL', 130632, 96669, 8953, 151), ('OAX', 22608, 7595, 6009, 150), ('PUE', 67100, 42285, 17929, 124),
       ('QRO', 78856, 36679, 7262, 80), ('QROO', 29171, 9962, 11720, 97), ('SLP', 42184, 19338, 5570, 62),
       ('SIN', 44844, 36381, 10191, 137), ('SON', 85330, 53261, 12165, 119), ('TAB', 43254, 10286, 52444, 96),
       ('TAM', 59977, 42943, 11471, 122), ('TLAX', 17461, 10526, 4241, 44), ('VER', 82334, 69845, 9127, 304),
       ('YUC', 26039, 19384, 6644, 59), ('ZAC', 22769, 19639, 11894, 109)]
# Los totales que publica el INEGI: la transcripción tiene que cuadrar.
EST_TOTAL = (2205864, 1403597, 435920, 4458)  # pp. 35 y 39; p. 43 (503,937 − 68,017 del CJF); p. 12 (5,216 − 758 del CJF)

# Tabla 22 (p. 37): por materia, 2024 (ingresados, concluidos).
MATERIAS = [('Familiar', 905504, 577618), ('Civil', 635581, 350423), ('Mercantil', 408892, 325081),
            ('Penal', 250527, 146412), ('Justicia para adolescentes', 5360, 4063)]

# Causas penales del sistema acusatorio pendientes de concluir al cierre del
# año (gráfica 22, p. 43): (2023, 2024).
PEND_PENAL = {'cjf': (55871, 68017), 'pje': (385157, 435920), 'total': (441028, 503937)}
# Sistema tradicional (p. 40): pendientes al cierre de 2024.
PEND_TRAD = {'cjf': 4279, 'pje': 78441, 'total': 82720}

# Duración promedio de resolución en la Corte, 2024 (tabla 13, p. 23), días
# naturales: (asunto, Pleno, Primera Sala, Segunda Sala). 0 = no resolvió de
# ese tipo. Solo los que más le importan al lector; la tabla trae 40.
DUR_SCJN = [('Acción de inconstitucionalidad', 522, 470, 319),
            ('Controversia constitucional', 300, 338, 294),
            ('Amparo en revisión en materia administrativa', 644, 270, 170),
            ('Amparo directo en revisión en materia civil', 292, 260, 0),
            ('Amparo directo en revisión en materia penal', 0, 257, 0),
            ('Incidente de inejecución de sentencia', 624, 270, 251),
            ('Contradicción de criterios', 490, 284, 132)]
# Tribunal Electoral, 2024 (tabla 17, p. 30), días naturales, todas las salas.
DUR_TEPJF = [('Juicio de inconformidad', 25), ('Juicio de revisión constitucional electoral', 12),
             ('Conflictos laborales entre el Tribunal y su personal', 767)]

PAGINA = 'datos-judicial-gestion.html'
TEMAS = ['gestion', 'gestion_estados', 'rezago', 'tiempos']


def _o(que, fu, op=None, e=None, p=None):
    d = {'que': que, 'e': e or ('derivado' if op else 'oficial'), 'fu': fu}
    if op:
        d['op'] = op
    if p:
        d['p'] = p
    return d


def _n(v):
    return format(int(round(v)), ',')


def _pesos(v):
    return '$' + _n(v)


def _pct(a, b):
    return format(round(100.0 * a / b, 1), '.1f')


PEND_TIEMPOS = {'que': 'Cuánto tarda un juzgado o tribunal en resolver y en celebrar una audiencia', 'e': 'pendiente',
                'p': 'judicial-tiempos-juzgados', 'fu': {'tx': 'INEGI, CNIJF y CNIJE 2025: tabulados y datos abiertos', 'url': MICRO}}
PEND_CIVIL = {'que': 'Cuántos expedientes civiles, familiares y mercantiles quedaron sin resolver al cierre de 2024', 'e': 'pendiente',
              'p': 'judicial-rezago-civil', 'fu': {'tx': 'INEGI, CNIJE 2025: tabulados y datos abiertos', 'url': MICRO}}

NO_ES = ('<p class="pa-chico">Ojo: el dinero por asunto <b>no es lo que cuesta un juicio</b>. El presupuesto paga todo el órgano '
         '(administración, edificios, personal de apoyo y, en el federal, la defensoría pública), y un asunto resuelto puede ser una sentencia '
         'o un desechamiento. Sirve para comparar, no para cobrar. Y son cifras que <b>cada órgano reporta de sí mismo</b> al INEGI.</p>')


def chequeo(d):
    """Comprueba la transcripción contra los totales del INEGI y contra la base."""
    s = [sum(r[i] for r in EST) for i in (1, 2, 3, 4)]
    assert tuple(s) == EST_TOTAL, 'Los poderes judiciales estatales no cuadran con el INEGI: %s' % s
    assert len({r[0] for r in EST}) == 32
    assert sum(m[1] for m in MATERIAS) == EST_TOTAL[0] and sum(m[2] for m in MATERIAS) == EST_TOTAL[1]
    assert PEND_PENAL['cjf'][1] + PEND_PENAL['pje'][1] == PEND_PENAL['total'][1]
    assert PEND_PENAL['pje'][1] == EST_TOTAL[2]
    assert PEND_TRAD['cjf'] + PEND_TRAD['pje'] == PEND_TRAD['total']
    pje = d['inspector_poderes']['judicialesEstatales2024']
    assert sorted(pje) == sorted(r[0] for r in EST), 'Las entidades del censo no son las de la base'
    assert abs(sum(pje.values()) - 53516.3) < 0.05
    cot = {o['id']: o for o in d['inspector_poderes']['organos']}
    for k, v in PRES_FED.items():
        b = [c['b'][1] for c in cot[k].get('cotejos', []) if c['b'][2] == 'cnijf']
        assert b == [v], 'El presupuesto del INEGI de %s no es el de la base' % k
    return pje


def temas(d):
    """Los cuatro temas del bot y de la página. `d` es window.AUDIT_DB."""
    pje = chequeo(d)
    t = {}
    # --- El federal ---
    filas = []
    for k in ('scjn', 'oaj', 'tepjf'):
        ing, egr, _ = FED[k]
        filas.append((k, ing, egr, PRES_FED[k] * 1e6 / egr))
    sc, oa, te = filas
    t['gestion'] = {
        'tit': 'Lo que cuesta y lo que resuelve el Poder Judicial de la Federación',
        'h': '<p>Que las cuentas cuadren no dice si la justicia llega. Por eso aquí el <b>dinero</b> va junto a <b>lo que se resolvió con él</b>, '
             'con las cifras de 2024 que cada órgano le reportó al INEGI:</p><ul class="pa-lista">'
             '<li><b>Juzgados y tribunales federales:</b> entraron <b>%s</b> asuntos y salieron <b>%s</b>. Ejercieron $%s millones: '
             '<b>%s por cada asunto resuelto</b>.</li>'
             '<li><b>Suprema Corte:</b> entraron %s asuntos y resolvió %s. Ejerció $%s millones: <b>%s por asunto</b>.</li>'
             '<li><b>Tribunal Electoral:</b> entraron %s asuntos y concluyó %s (2024 fue año de elección: los ingresos crecieron 415.7 %%). '
             'Ejerció $%s millones: %s por asunto concluido.</li></ul>'
             '<p>En los juzgados federales del sistema penal acusatorio quedaron <b>%s causas pendientes</b> al cierre de 2024, %s %% más que un año antes.</p>%s' % (
                 _n(oa[1]), _n(oa[2]), format(PRES_FED['oaj'], ',.1f'), _pesos(oa[3]),
                 _n(sc[1]), _n(sc[2]), format(PRES_FED['scjn'], ',.1f'), _pesos(sc[3]),
                 _n(te[1]), _n(te[2]), format(PRES_FED['tepjf'], ',.1f'), _pesos(te[3]),
                 _n(PEND_PENAL['cjf'][1]), _pct(PEND_PENAL['cjf'][1] - PEND_PENAL['cjf'][0], PEND_PENAL['cjf'][0]), NO_ES),
        'fu': [_o('Asuntos ingresados y egresados de los juzgados y tribunales del Consejo de la Judicatura (gráfica 16)', _f('p. 31')),
               _o('Asuntos de la Suprema Corte: turnados y resueltos (gráfica 10)', _f('p. 19')),
               _o('Asuntos del Tribunal Electoral y su aumento de 415.7 %', _f('p. 24')),
               _o('Presupuesto ejercido en 2024 (gráfica 6). El del Consejo incluye al Instituto Federal de Defensoría Pública', _f('p. 13')),
               _o('Causas penales pendientes de concluir en el sistema acusatorio, 2023 y 2024 (gráfica 22)', _f('p. 43')),
               _o('Dinero por asunto resuelto', _f('pp. 13, 19, 24 y 31'), 'presupuesto ejercido 2024 ÷ asuntos egresados o concluidos en 2024')],
        'ci': [{'v': _pesos(oa[3]), 'etq': 'por asunto resuelto en los juzgados federales', 'e': 'derivado', 'op': '$72,090.0 millones ÷ %s' % _n(oa[2])},
               {'v': _n(oa[1] - oa[2]), 'etq': 'asuntos más entraron de los que salieron, en los juzgados federales', 'e': 'derivado', 'op': '%s − %s' % (_n(oa[1]), _n(oa[2]))},
               {'v': _n(PEND_PENAL['cjf'][1]), 'etq': 'causas penales federales pendientes al cierre de 2024', 'e': 'oficial'}],
        'sug': ['¿Cuánto rezago tienen los poderes judiciales de los estados?', '¿Cuánto tarda la Suprema Corte en resolver?',
                '¿Cuánto rezago penal hay?']}
    # --- Los estados ---
    nom = {e['abbr']: e['name'] for e in d['estados']}
    porc = sorted(EST, key=lambda r: r[2] / r[1])
    peor, mejor = porc[0], porc[-1]
    t['gestion_estados'] = {
        'tit': 'Lo que cuesta y lo que resuelve el Poder Judicial de cada estado',
        'h': '<p>En 2024 llegaron <b>%s asuntos</b> a los juzgados de primera instancia de los 32 poderes judiciales estatales y se concluyeron <b>%s</b>: '
             '<b>%s de cada 100</b>. Ejercieron $%s millones: <b>%s por asunto concluido</b>.</p>'
             '<p>El que menos concluyó para lo que le llegó fue <b>%s</b> (%s de cada 100); el que más, <b>%s</b> (%s). Más de 100 quiere decir que también '
             'cerró asuntos de años anteriores.</p>'
             '<p>Cuidado al leer «los que entraron menos los que salieron»: en lo civil, familiar y mercantil el INEGI cuenta como ingresada <b>toda demanda</b>, '
             'también la que se desecha o se manda corregir, y como concluida solo la que puso fin al pleito. La diferencia <b>no es el rezago</b>; el rezago civil y '
             'familiar no viene en el reporte del censo.</p>%s' % (
                 _n(EST_TOTAL[0]), _n(EST_TOTAL[1]), _pct(EST_TOTAL[1], EST_TOTAL[0]), format(53516.3, ',.1f'), _pesos(53516.3e6 / EST_TOTAL[1]),
                 html.escape(nom[peor[0]]), _pct(peor[2], peor[1]), html.escape(nom[mejor[0]]), _pct(mejor[2], mejor[1]), NO_ES),
        'fu': [_o('Asuntos ingresados y concluidos por entidad (tabla 23)', _f('p. 39')),
               _o('Qué cuenta como ingresado y como concluido (notas 1 y 2 de la tabla 23)', _f('p. 39')),
               _o('Presupuesto ejercido por cada poder judicial estatal (gráfica 7)', _f('p. 14')),
               _o('Concluidos por cada 100 ingresados y dinero por asunto concluido', _f('pp. 14 y 39'),
                  'concluidos ÷ ingresados × 100; presupuesto ejercido ÷ concluidos'),
               PEND_CIVIL],
        'ci': [{'v': _pct(EST_TOTAL[1], EST_TOTAL[0]), 'etq': 'asuntos concluidos por cada 100 que entraron', 'e': 'derivado'},
               {'v': _pesos(53516.3e6 / EST_TOTAL[1]), 'etq': 'por asunto concluido, promedio nacional', 'e': 'derivado'}],
        'sug': ['¿Cuánto rezago tiene el Poder Judicial de Jalisco?', '¿Cuánto rezago penal hay?', '¿Cuánto cuesta cada asunto que resuelve la Corte?']}
    # --- El rezago que sí se mide ---
    top = sorted(EST, key=lambda r: -r[3])[:3]
    t['rezago'] = {
        'tit': 'El rezago que sí se puede medir: las causas penales',
        'h': '<p>El único rezago que el censo publica completo es el <b>penal</b>. Al cierre de 2024 quedaban <b>%s causas pendientes de concluir</b> en el '
             'sistema acusatorio, <b>%s %% más</b> que un año antes: %s en los juzgados federales y %s en los estados. En el sistema tradicional, el de antes '
             'de los juicios orales, seguían otras %s.</p>'
             '<p>Donde más se acumulan: %s.</p>'
             '<p class="pa-chico">En los estados, el INEGI cuenta a <b>cada persona procesada</b>, no cada expediente: una causa con tres personas cuenta tres. '
             'De lo civil, familiar y mercantil, el reporte no trae cuántos asuntos quedaron sin resolver.</p>' % (
                 _n(PEND_PENAL['total'][1]), _pct(PEND_PENAL['total'][1] - PEND_PENAL['total'][0], PEND_PENAL['total'][0]),
                 _n(PEND_PENAL['cjf'][1]), _n(PEND_PENAL['pje'][1]), _n(PEND_TRAD['total']),
                 ', '.join('<b>%s</b> (%s)' % (html.escape(nom[r[0]]), _n(r[3])) for r in top)),
        'fu': [_o('Causas penales pendientes de concluir, 2023 y 2024, federal y estatal (gráfica 22)', _f('p. 43')),
               _o('Pendientes por entidad y qué cuenta el INEGI en los estados (tabla 25 y su nota 3)', _f('p. 45')),
               _o('Pendientes del sistema tradicional (tabla 24)', _f('pp. 40 y 41')),
               _o('Aumento contra 2023', _f('p. 43'), '(%s − %s) ÷ %s' % (_n(PEND_PENAL['total'][1]), _n(PEND_PENAL['total'][0]), _n(PEND_PENAL['total'][0]))),
               PEND_CIVIL],
        'ci': [{'v': _n(PEND_PENAL['total'][1]), 'etq': 'causas penales pendientes al cierre de 2024', 'e': 'oficial'},
               {'v': _pct(PEND_PENAL['total'][1] - PEND_PENAL['total'][0], PEND_PENAL['total'][0]) + ' %', 'etq': 'más que al cierre de 2023', 'e': 'derivado'}],
        'sug': ['¿Cuánto rezago tiene el Poder Judicial de Tabasco?', '¿Cuánto tarda la Suprema Corte en resolver?']}
    # --- Cuánto tarda ---
    t['tiempos'] = {
        'tit': 'Cuánto tarda la justicia',
        'h': '<p>El censo del INEGI solo publica cuánto tardan <b>la Suprema Corte y el Tribunal Electoral</b>. En 2024, en promedio:</p><ul class="pa-lista">'
             '<li>una <b>acción de inconstitucionalidad</b> tardó <b>522 días</b> en el Pleno de la Corte (casi año y medio);</li>'
             '<li>una <b>controversia constitucional</b>, 300 días en el Pleno;</li>'
             '<li>un <b>amparo en revisión</b> administrativo, 644 días en el Pleno y 170 en la Segunda Sala;</li>'
             '<li>en el Tribunal Electoral, un <b>juicio de inconformidad</b>, 25 días, y un pleito laboral con su propio personal, <b>767 días</b>.</li></ul>'
             '<p><b>De los juzgados</b>, que es donde llega casi todo, <b>no hay cifra publicada</b>: ni federal ni estatal, ni de cuánto se tarda una audiencia. '
             'Lo que sí fija la Constitución son <b>plazos máximos</b>: a una persona acusada se le debe juzgar antes de <b>cuatro meses</b> si la pena máxima del delito '
             'no pasa de dos años de prisión, y antes de <b>un año</b> si pasa (art. 20), y los juicios de impuestos se deben resolver en <b>seis meses</b> (art. 17). '
             'Si no se cumplen, el juzgado debe avisar al Tribunal de Disciplina Judicial y explicar por qué. Sin la duración de cada juzgado, nadie puede comprobar '
             'si se cumplen.</p>',
        'fu': [_o('Duración promedio en días naturales, por tipo de asunto y órgano de la Corte (tabla 13)', _f('p. 23')),
               _o('Duración promedio en el Tribunal Electoral, por medio de impugnación (tabla 17)', _f('p. 30')),
               _o('Juzgar antes de cuatro meses o de un año, y avisar al Tribunal de Disciplina si no (art. 20, apartado B, fr. VII)', CPEUM),
               _o('Seis meses en los juicios de impuestos (art. 17)', CPEUM),
               PEND_TIEMPOS],
        'ci': [{'v': '522 días', 'etq': 'una acción de inconstitucionalidad en el Pleno de la Corte', 'e': 'oficial'}],
        'sug': ['¿Cuánto rezago penal hay?', '¿Cuánto cuesta cada asunto que resuelve la Corte?', '¿Cuánto debe tardar un juicio de impuestos?']}
    return t


def por_estado(d):
    """Para el chat: [entidad, presupuesto (millones), ingresados, concluidos, penales pendientes, juzgadoras]."""
    pje = chequeo(d)
    return [[a, pje[a], i, c, p, j] for a, i, c, p, j in EST]


def extra(d, k):
    """Las tablas de la página, debajo del texto de cada tema."""
    from asistente_legislativo import _chip
    nom = {e['abbr']: e['name'] for e in d['estados']}
    pie = '<p class="pa-chico">Fuente: <a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>. %s</p>'
    if k == 'gestion':
        filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td><td>$%s</td></tr>' % (
            html.escape(FED_NOMBRE[x]), _pesos(PRES_FED[x] * 1e6 / FED[x][1]), _n(FED[x][0]), _n(FED[x][1]), format(PRES_FED[x], ',.1f'))
            for x in ('oaj', 'scjn', 'tepjf'))
        return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>El Poder Judicial de la Federación en 2024 %s</caption>'
                '<thead><tr><th scope="col">Órgano</th><th scope="col">Por asunto resuelto %s</th><th scope="col">Entraron</th><th scope="col">Resolvió</th>'
                '<th scope="col">Ejerció (millones)</th></tr></thead><tbody>%s</tbody></table></div>' + pie) % (
            _chip('oficial'), _chip('derivado'), filas, URL, html.escape(CENSO), 'pp. 13, 19, 24 y 31.')
    if k == 'gestion_estados':
        filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            html.escape(nom[a]), _pct(c, i), _pesos(pje * 1e6 / c), _n(i), _n(c))
            for a, pje, i, c, _, _ in sorted(por_estado(d), key=lambda r: nom[r[0]]))
        return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Primera instancia de cada poder judicial estatal, 2024 %s</caption>'
                '<thead><tr><th scope="col">Estado</th><th scope="col">Concluyó de cada 100 %s</th><th scope="col">Por asunto concluido %s</th>'
                '<th scope="col">Entraron</th><th scope="col">Concluyeron</th></tr></thead><tbody>%s</tbody>'
                '<tfoot><tr><th scope="row">Nacional</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr></tfoot></table></div>' + pie) % (
            _chip('oficial'), _chip('derivado'), _chip('derivado'), filas, _pct(EST_TOTAL[1], EST_TOTAL[0]), _pesos(53516.3e6 / EST_TOTAL[1]),
            _n(EST_TOTAL[0]), _n(EST_TOTAL[1]), URL, html.escape(CENSO),
            'Tabla 23 (p. 39) y gráfica 7 (p. 14). Materias penal, adolescentes, civil, familiar y mercantil.')
    if k == 'rezago':
        filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td></tr>' % (html.escape(nom[a]), _n(p), _n(j))
                        for a, p, j in sorted(((r[0], r[3], r[4]) for r in EST), key=lambda r: -r[1]))
        mat = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td></tr>' % (m, _n(i), _n(c)) for m, i, c in MATERIAS)
        return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Causas penales pendientes de concluir al cierre de 2024, sistema acusatorio %s</caption>'
                '<thead><tr><th scope="col">Estado</th><th scope="col">Pendientes</th><th scope="col">Personas juzgadoras del estado</th></tr></thead><tbody>%s</tbody>'
                '<tfoot><tr><th scope="row">Juzgados federales</th><td>%s</td><td>758</td></tr></tfoot></table></div>'
                '<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Estados, por materia, 2024 %s</caption>'
                '<thead><tr><th scope="col">Materia</th><th scope="col">Entraron</th><th scope="col">Concluyeron</th></tr></thead><tbody>%s</tbody></table></div>'
                '<p class="pa-chico">Cuánto quedó sin resolver en lo civil, familiar y mercantil: %s</p>' + pie) % (
            _chip('oficial'), filas, _n(PEND_PENAL['cjf'][1]), _chip('oficial'), mat, _chip('pendiente', 'judicial-rezago-civil'),
            URL, html.escape(CENSO), 'Tabla 25 (p. 45), tabla 6 (p. 12) y tabla 22 (p. 37).')
    if k == 'tiempos':
        cel = lambda v: _n(v) if v else '—'
        filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td></tr>' % (html.escape(a), cel(p), cel(s1), cel(s2))
                        for a, p, s1, s2 in DUR_SCJN)
        tep = ''.join('<tr><th scope="row">%s</th><td>%s</td></tr>' % (html.escape(a), _n(v)) for a, v in DUR_TEPJF)
        return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Suprema Corte: días naturales que tardó en resolver, 2024 %s</caption>'
                '<thead><tr><th scope="col">Asunto</th><th scope="col">Pleno</th><th scope="col">Primera Sala</th><th scope="col">Segunda Sala</th></tr></thead>'
                '<tbody>%s</tbody></table></div>'
                '<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Tribunal Electoral: días naturales, 2024 %s</caption>'
                '<thead><tr><th scope="col">Asunto</th><th scope="col">Días</th></tr></thead><tbody>%s</tbody></table></div>'
                '<p class="pa-chico">«—»: esa sala no resolvió asuntos de ese tipo. Cuánto tarda un juzgado o una audiencia: %s</p>' + pie) % (
            _chip('oficial'), filas, _chip('oficial'), tep, _chip('pendiente', 'judicial-tiempos-juzgados'),
            URL, html.escape(CENSO), 'Tabla 13 (p. 23) y tabla 17 (p. 30); la tabla 13 trae 40 tipos de asunto.')
    return ''
