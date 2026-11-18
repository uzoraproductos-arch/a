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

Desde el 18-11-2026 se leen además sus tabulados básicos
(docs/estadistica/cnije-2025-tabulados.json, que escribe
anclar_cnije_tabulados.py con la huella del libro): los expedientes civiles,
familiares y mercantiles pendientes de concluir en cada estado (cuadro 16) y
cuánto tardan los juzgados y tribunales federales (cuadro 13).

Lo que sigue en el Registro de pendientes: cuánto tardan los juzgados de los
estados y cuánto se espera una audiencia (ni el reporte ni los tabulados lo
traen), y el rezago civil y familiar de los seis poderes judiciales que le
dijeron al INEGI que no lo saben.

La lee asistente_judicial.py: sus temas entran a D.jud y a la página
«Lo que cuesta y lo que resuelve» de Datos · Poder Judicial.
"""

import html
import json
import os

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

# Los tabulados básicos del censo (cuadros 13 y 16), con su huella.
TAB = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'estadistica',
                                  'cnije-2025-tabulados.json'), encoding='utf-8'))
TAB_FU = TAB['fuente']
CFM = (('civ', 'civiles'), ('fam', 'familiares'), ('mer', 'mercantiles'))
# Lo que se le dice al lector de los juzgados federales (cuadro 13): (grupo,
# asunto tal como lo escribe el INEGI, cómo se dice aquí). Se lee la duración
# de los resueltos por sentencia.
DUR_CJF = [('Juzgados de Distrito', 'Juicios de amparo indirecto', 'Juicio de amparo indirecto (juzgado de distrito)'),
           ('Juzgados de Distrito', 'Causas penales en procesos de primera instancia', 'Causa penal en primera instancia (juzgado de distrito)'),
           ('Juzgados de Distrito', 'Procesos civiles o administrativos federales', 'Juicio civil o administrativo federal (juzgado de distrito)'),
           ('Juzgados de Distrito', 'Juicios orales mercantiles', 'Juicio oral mercantil (juzgado de distrito)'),
           ('Juzgados de Distrito', 'Extinción de dominio', 'Extinción de dominio (juzgado de distrito)'),
           ('Tribunales Colegiados de Circuito', 'Amparo directo', 'Amparo directo (tribunal colegiado)'),
           ('Tribunales Colegiados de Circuito', 'Amparo en revisión', 'Amparo en revisión (tribunal colegiado)'),
           ('Centros de Justicia Penal Federal', 'Causa penal. Juez de Control o Garantías', 'Causa penal ante juez de control'),
           ('Centros de Justicia Penal Federal', 'Causa penal. Juez de Enjuiciamiento o Juicio Oral', 'Juicio oral penal (tribunal de enjuiciamiento)')]


def _t(donde):
    return {'tx': '%s, %s' % (TAB_FU['tx'], donde), 'url': TAB_FU['url'], 'sha256': TAB_FU['sha256']}


def dur_cjf():
    """[(cómo se dice, días del proceso, días si hubo sentencia, días sin sentencia)]."""
    g = TAB['c13']['grupos']
    out = []
    for grupo, asunto, dicho in DUR_CJF:
        fila = next((r for r in g[grupo] if r[0] == asunto), None)
        assert fila and all(isinstance(v, int) for v in fila[1:]), 'El cuadro 13 ya no trae %s / %s' % (grupo, asunto)
        out.append((dicho, fila[1], fila[2], fila[3]))
    return out


def rezago_cfm():
    """Expedientes civiles, familiares y mercantiles pendientes al 31-12-2024
    (cuadro 16): {entidad: {civ, fam, mer}} (None = el poder judicial no lo
    sabe; en la Ciudad de México lo mercantil va dentro de lo civil), el país
    y las entidades que no lo saben."""
    est = {k: {m: v['tot'][m] for m, _ in CFM} for k, v in TAB['c16']['estados'].items()}
    pais = {m: TAB['c16']['pais']['tot'][m] for m, _ in CFM}
    nolo = sorted(k for k, v in est.items() if v['civ'] is None or v['fam'] is None or (v['mer'] is None and k != 'CDMX'))
    return est, pais, nolo


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


PEND_TIEMPOS = {'que': 'Cuánto tardan los juzgados de los estados en resolver, y cuánto se espera una audiencia', 'e': 'pendiente',
                'p': 'judicial-tiempos-juzgados', 'fu': {'tx': 'INEGI, CNIJE 2025: reporte de resultados y tabulados básicos', 'url': MICRO}}
PEND_CIVIL = {'que': 'Cuántos expedientes civiles, familiares y mercantiles tenían pendientes los seis poderes judiciales que no lo saben', 'e': 'pendiente',
              'p': 'judicial-rezago-civil', 'fu': {'tx': 'INEGI, CNIJE 2025, tabulados básicos, cuadro 16', 'url': TAB_FU['url']}}

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
    # Los tabulados y el reporte son el mismo censo: las causas penales del
    # sistema acusatorio (personas adultas más adolescentes) de cada estado en
    # el cuadro 16 tienen que ser las de la tabla 25 del reporte.
    t16 = TAB['c16']['estados']
    for a, _, _, p, _ in EST:
        o = t16[a]['oral']
        assert o['pen'] + o['ado'] == p, 'El cuadro 16 no da las causas penales de %s de la tabla 25' % a
    est, pais, nolo = rezago_cfm()
    assert nolo == ['BC', 'BCS', 'CHIH', 'DGO', 'MOR', 'PUE'], 'Cambió quién no sabe su rezago civil: %s' % nolo
    for m, _ in CFM:
        assert sum(v[m] or 0 for v in est.values()) == pais[m]
    dur_cjf()
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
             'también la que se desecha o se manda corregir, y como concluida solo la que puso fin al pleito. La diferencia <b>no es el rezago</b>: lo que quedó '
             'sin resolver se cuenta aparte, en «El rezago que sí se puede medir».</p>%s' % (
                 _n(EST_TOTAL[0]), _n(EST_TOTAL[1]), _pct(EST_TOTAL[1], EST_TOTAL[0]), format(53516.3, ',.1f'), _pesos(53516.3e6 / EST_TOTAL[1]),
                 html.escape(nom[peor[0]]), _pct(peor[2], peor[1]), html.escape(nom[mejor[0]]), _pct(mejor[2], mejor[1]), NO_ES),
        'fu': [_o('Asuntos ingresados y concluidos por entidad (tabla 23)', _f('p. 39')),
               _o('Qué cuenta como ingresado y como concluido (notas 1 y 2 de la tabla 23)', _f('p. 39')),
               _o('Presupuesto ejercido por cada poder judicial estatal (gráfica 7)', _f('p. 14')),
               _o('Concluidos por cada 100 ingresados y dinero por asunto concluido', _f('pp. 14 y 39'),
                  'concluidos ÷ ingresados × 100; presupuesto ejercido ÷ concluidos'),
        ],
        'ci': [{'v': _pct(EST_TOTAL[1], EST_TOTAL[0]), 'etq': 'asuntos concluidos por cada 100 que entraron', 'e': 'derivado'},
               {'v': _pesos(53516.3e6 / EST_TOTAL[1]), 'etq': 'por asunto concluido, promedio nacional', 'e': 'derivado'}],
        'sug': ['¿Cuánto rezago tiene el Poder Judicial de Jalisco?', '¿Cuánto rezago penal hay?', '¿Cuánto cuesta cada asunto que resuelve la Corte?']}
    # --- El rezago que sí se mide ---
    top = sorted(EST, key=lambda r: -r[3])[:3]
    cfm, cpais, nolo = rezago_cfm()
    ctop = sorted((k for k in cfm if k not in nolo), key=lambda k: -sum(cfm[k][m] or 0 for m, _ in CFM))[:3]
    csum = sum(cpais.values())
    t['rezago'] = {
        'tit': 'El rezago que sí se puede medir: penal, familiar, civil y mercantil',
        'h': '<p>El único rezago que el censo publica completo es el <b>penal</b>. Al cierre de 2024 quedaban <b>%s causas pendientes de concluir</b> en el '
             'sistema acusatorio, <b>%s %% más</b> que un año antes: %s en los juzgados federales y %s en los estados. En el sistema tradicional, el de antes '
             'de los juicios orales, seguían otras %s.</p>'
             '<p>Donde más se acumulan: %s.</p>'
             '<p class="pa-chico">En los estados, el INEGI cuenta a <b>cada persona procesada</b>, no cada expediente: una causa con tres personas cuenta tres.</p>'
             '<p>Lo <b>civil, familiar y mercantil</b> pesa mucho más. Al 31 de diciembre de 2024, los juzgados de primera instancia de los estados tenían '
             '<b>%s expedientes familiares</b>, <b>%s civiles</b> y <b>%s mercantiles</b> pendientes de concluir: <b>%s</b> en total, entre los que entraron ese año '
             'y los que venían de antes. Donde más: %s.</p>'
             '<p>La cuenta va <b>incompleta</b>: %s le dijeron al INEGI que <b>no saben</b> cuántos expedientes civiles y familiares tenían pendientes '
             '(y algunos, tampoco los mercantiles). El total del país suma solo a los que sí lo dijeron. Un poder judicial que no sabe cuánto le falta resolver '
             'no puede decir si va al día.</p>' % (
                 _n(PEND_PENAL['total'][1]), _pct(PEND_PENAL['total'][1] - PEND_PENAL['total'][0], PEND_PENAL['total'][0]),
                 _n(PEND_PENAL['cjf'][1]), _n(PEND_PENAL['pje'][1]), _n(PEND_TRAD['total']),
                 ', '.join('<b>%s</b> (%s)' % (html.escape(nom[r[0]]), _n(r[3])) for r in top),
                 _n(cpais['fam']), _n(cpais['civ']), _n(cpais['mer']), _n(csum),
                 ', '.join('<b>%s</b> (%s)' % (html.escape(nom[k]), _n(sum(cfm[k][m] or 0 for m, _ in CFM))) for k in ctop),
                 '<b>%s poderes judiciales</b> (%s)' % ('seis' if len(nolo) == 6 else len(nolo), ', '.join(html.escape(nom[k]) for k in nolo))),
        'fu': [_o('Causas penales pendientes de concluir, 2023 y 2024, federal y estatal (gráfica 22)', _f('p. 43')),
               _o('Pendientes por entidad y qué cuenta el INEGI en los estados (tabla 25 y su nota 3)', _f('p. 45')),
               _o('Pendientes del sistema tradicional (tabla 24)', _f('pp. 40 y 41')),
               _o('Aumento contra 2023', _f('p. 43'), '(%s − %s) ÷ %s' % (_n(PEND_PENAL['total'][1]), _n(PEND_PENAL['total'][0]), _n(PEND_PENAL['total'][0]))),
               _o('Expedientes civiles, familiares y mercantiles pendientes de concluir al 31-12-2024, por entidad, y quién no lo sabe («-»: no se sabe) (cuadro 16)', _t('cuadro 16')),
               _o('Suma de las tres materias', _t('cuadro 16'), '%s + %s + %s' % (_n(cpais['fam']), _n(cpais['civ']), _n(cpais['mer']))),
               PEND_CIVIL],
        'ci': [{'v': _n(PEND_PENAL['total'][1]), 'etq': 'causas penales pendientes al cierre de 2024', 'e': 'oficial'},
               {'v': _n(cpais['fam']), 'etq': 'expedientes familiares pendientes en los estados al cierre de 2024', 'e': 'oficial'},
               {'v': _pct(PEND_PENAL['total'][1] - PEND_PENAL['total'][0], PEND_PENAL['total'][0]) + ' %', 'etq': 'más que al cierre de 2023', 'e': 'derivado'}],
        'sug': ['¿Cuánto rezago tiene el Poder Judicial de Tabasco?', '¿Cuánto tarda un juicio de amparo?', '¿Cuánto tarda la Suprema Corte en resolver?']}
    # --- Cuánto tarda ---
    t['tiempos'] = {
        'tit': 'Cuánto tarda la justicia',
        'h': '<p>El censo del INEGI solo publica cuánto tardan <b>la Suprema Corte y el Tribunal Electoral</b>. En 2024, en promedio:</p><ul class="pa-lista">'
             '<li>una <b>acción de inconstitucionalidad</b> tardó <b>522 días</b> en el Pleno de la Corte (casi año y medio);</li>'
             '<li>una <b>controversia constitucional</b>, 300 días en el Pleno;</li>'
             '<li>un <b>amparo en revisión</b> administrativo, 644 días en el Pleno y 170 en la Segunda Sala;</li>'
             '<li>en el Tribunal Electoral, un <b>juicio de inconformidad</b>, 25 días, y un pleito laboral con su propio personal, <b>767 días</b>.</li></ul>'
             '<p><b>De los juzgados federales</b>, los tabulados del mismo censo sí lo traen. Cuando el asunto terminó en sentencia, en 2024 tardó en promedio: '
             '%s.</p>'
             '<p><b>De los juzgados de los estados</b>, que es donde llega casi todo, <b>no hay cifra publicada</b>, ni de cuánto se espera una audiencia. '
             'Lo que sí fija la Constitución son <b>plazos máximos</b>: a una persona acusada se le debe juzgar antes de <b>cuatro meses</b> si la pena máxima del delito '
             'no pasa de dos años de prisión, y antes de <b>un año</b> si pasa (art. 20), y los juicios de impuestos se deben resolver en <b>seis meses</b> (art. 17). '
             'Si no se cumplen, el juzgado debe avisar al Tribunal de Disciplina Judicial y explicar por qué. Sin la duración de cada juzgado, nadie puede comprobar '
             'si se cumplen.</p>' % '; '.join('%s, <b>%s días</b>' % (html.escape(x[0][0].lower() + x[0][1:]), _n(x[2])) for x in dur_cjf()
                                               if x[0].startswith(('Juicio de amparo', 'Juicio civil', 'Amparo directo', 'Juicio oral penal'))),
        'fu': [_o('Duración promedio en días naturales, por tipo de asunto y órgano de la Corte (tabla 13)', _f('p. 23')),
               _o('Duración promedio en días naturales de los asuntos que egresaron de los juzgados y tribunales federales, por tipo de resolución (cuadro 13)', _t('cuadro 13')),
               _o('Duración promedio en el Tribunal Electoral, por medio de impugnación (tabla 17)', _f('p. 30')),
               _o('Juzgar antes de cuatro meses o de un año, y avisar al Tribunal de Disciplina si no (art. 20, apartado B, fr. VII)', CPEUM),
               _o('Seis meses en los juicios de impuestos (art. 17)', CPEUM),
               PEND_TIEMPOS],
        'ci': [{'v': '522 días', 'etq': 'una acción de inconstitucionalidad en el Pleno de la Corte', 'e': 'oficial'},
               {'v': '%s días' % _n(dur_cjf()[0][2]), 'etq': 'un amparo indirecto con sentencia en un juzgado de distrito', 'e': 'oficial'}],
        'sug': ['¿Cuánto rezago penal hay?', '¿Cuánto cuesta cada asunto que resuelve la Corte?', '¿Cuánto debe tardar un juicio de impuestos?']}
    return t


def por_estado(d):
    """Para el chat: [entidad, presupuesto (millones), ingresados, concluidos, penales pendientes, juzgadoras]."""
    pje = chequeo(d)
    return [[a, pje[a], i, c, p, j] for a, i, c, p, j in EST]


def judiciales_estados(d):
    """Para el Planisferio (03-11-2026, dimensión judicial): {entidad: {g
    presupuesto ejercido 2024 en millones, i ingresados, c concluidos, p
    causas penales pendientes, j personas juzgadoras, c100 concluidos por
    cada 100 ingresados, xa pesos por asunto concluido, cj concluidos por
    persona juzgadora}}. Las tres divisiones son nuestras (derivado)."""
    out = {}
    for a, g, i, c, p, j in por_estado(d):
        out[a] = {'g': g, 'i': i, 'c': c, 'p': p, 'j': j, 'c100': round(100.0 * c / i, 1),
                  'xa': round(g * 1e6 / c), 'cj': round(c / j)}
    return out


def _tabla_cfm(nom):
    """Expedientes civiles, familiares y mercantiles pendientes por estado (cuadro 16)."""
    from asistente_legislativo import _chip
    est, pais, nolo = rezago_cfm()
    llam = TAB['c16']['llamadas']

    def cel(k, m):
        v = est[k][m]
        if v is None and k == 'CDMX' and m == 'mer':
            return 'en civil'
        return 'no lo sabe' if v is None else _n(v)
    filas = ''.join('<tr><th scope="row">%s%s</th><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        html.escape(nom[k]), '*' if k in llam else '', cel(k, 'fam'), cel(k, 'civ'), cel(k, 'mer'))
        for k in sorted(est, key=lambda k: nom[k]))
    notas = ' '.join('* %s: %s' % (html.escape(nom[k]), html.escape(v.split(' ', 1)[1])) for k, v in sorted(llam.items()))
    return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Expedientes pendientes de concluir al 31-12-2024, por estado %s</caption>'
            '<thead><tr><th scope="col">Estado</th><th scope="col">Familiares</th><th scope="col">Civiles</th><th scope="col">Mercantiles</th></tr></thead>'
            '<tbody>%s</tbody><tfoot><tr><th scope="row">Suma de los que lo saben</th><td>%s</td><td>%s</td><td>%s</td></tr></tfoot></table></div>'
            '<p class="pa-chico">«no lo sabe»: el poder judicial le respondió al INEGI que no lo sabe. %s Fuente: '
            '<a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>, cuadro 16. Lo que deben los que no lo saben: %s</p>') % (
        _chip('oficial'), filas, _n(pais['fam']), _n(pais['civ']), _n(pais['mer']), notas, TAB_FU['url'], html.escape(TAB_FU['tx']),
        _chip('pendiente', 'judicial-rezago-civil'))


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
                '%s' + pie) % (
            _chip('oficial'), filas, _n(PEND_PENAL['cjf'][1]), _chip('oficial'), mat, _tabla_cfm(nom),
            URL, html.escape(CENSO), 'Tabla 25 (p. 45), tabla 6 (p. 12) y tabla 22 (p. 37).')
    if k == 'tiempos':
        cel = lambda v: _n(v) if v else '—'
        filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td></tr>' % (html.escape(a), cel(p), cel(s1), cel(s2))
                        for a, p, s1, s2 in DUR_SCJN)
        tep = ''.join('<tr><th scope="row">%s</th><td>%s</td></tr>' % (html.escape(a), _n(v)) for a, v in DUR_TEPJF)
        cjf = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td></tr>' % (html.escape(a), _n(t_), _n(s_), _n(o_))
                      for a, t_, s_, o_ in dur_cjf())
        return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Suprema Corte: días naturales que tardó en resolver, 2024 %s</caption>'
                '<thead><tr><th scope="col">Asunto</th><th scope="col">Pleno</th><th scope="col">Primera Sala</th><th scope="col">Segunda Sala</th></tr></thead>'
                '<tbody>%s</tbody></table></div>'
                '<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Tribunal Electoral: días naturales, 2024 %s</caption>'
                '<thead><tr><th scope="col">Asunto</th><th scope="col">Días</th></tr></thead><tbody>%s</tbody></table></div>'
                '<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Juzgados y tribunales federales: días naturales, 2024 %s</caption>'
                '<thead><tr><th scope="col">Asunto</th><th scope="col">Todos</th><th scope="col">Con sentencia</th><th scope="col">Sin sentencia</th></tr></thead>'
                '<tbody>%s</tbody></table></div>'
                '<p class="pa-chico">«Sin sentencia» es todo lo que terminó de otro modo (desechado, sobreseído, por incompetencia…), casi siempre rápido; por eso el promedio '
                'de «Todos» puede quedar muy abajo del de una sentencia. Fuente: <a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>, cuadro 13.</p>'
                '<p class="pa-chico">«—»: esa sala no resolvió asuntos de ese tipo. Cuánto tardan los juzgados de los estados, y una audiencia: %s</p>' + pie) % (
            _chip('oficial'), filas, _chip('oficial'), tep, _chip('oficial'), cjf, TAB_FU['url'], html.escape(TAB_FU['tx']),
            _chip('pendiente', 'judicial-tiempos-juzgados'),
            URL, html.escape(CENSO), 'Tabla 13 (p. 23) y tabla 17 (p. 30); la tabla 13 trae 40 tipos de asunto.')
    return ''
