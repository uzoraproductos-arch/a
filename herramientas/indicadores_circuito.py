# -*- coding: utf-8 -*-
"""Litigiosidad y productividad de los juzgados y tribunales federales, circuito
por circuito, 2021 a 2025 (pedido del autor, 01-11-2026: «también por partidos
judiciales productividad y litigiosidad de los tribunales colegiados, unitarios,
apelación y juzgados de distrito, con todos los indicadores»).

La fuente es pública y no pide clave: los Indicadores Estadísticos Judiciales de
la Dirección General de Estadística Judicial (DGEJ, Órgano de Administración
Judicial), https://www.dgej.cjf.gob.mx/Indicadores/acuerd_nal_ini.asp. Los baja
y los lee herramientas/actualizar_indicadores_dgej.py, y quedan, con la huella
SHA-256 de cada cuadro, en docs/estadistica/dgej-indicadores-circuito.json.
Aquí no se escribe ninguna cifra a mano: todo se lee de ese archivo.

Tres cosas que se dicen siempre:
- La justicia federal no se divide en «partidos judiciales» (eso es de los
  poderes judiciales de los estados): se divide en 32 circuitos.
- Lo que la DGEJ llama «tasa de sentencia» (indicador 12) es egresos ÷
  ingresos: cuántos asuntos salen por cada uno que entra, no cuántas
  sentencias se dictan. La proporción de egresos con sentencia es el
  indicador 13.
- El sistema da años completos (16 de noviembre a 15 de noviembre): no parte
  2025 en antes y después de la llegada de las personas electas, ni cruza el
  dato con quién juzga en cada órgano. Ese cruce sigue pendiente
  (`judicial-electos-por-organo`).

La lee asistente_judicial.py: cuatro páginas de Datos · Poder Judicial (una por
tipo de órgano y una por circuito) y sus temas en D.jud del chat.
"""

import html
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
ARCHIVO = os.path.join(AQUI, '..', 'docs', 'estadistica', 'dgej-indicadores-circuito.json')
SISTEMA = 'https://www.dgej.cjf.gob.mx/Indicadores/acuerd_nal_ini.asp'
ANOS = ['2021', '2022', '2023', '2024', '2025']

ORD = ['Primer', 'Segundo', 'Tercer', 'Cuarto', 'Quinto', 'Sexto', 'Séptimo', 'Octavo', 'Noveno', 'Décimo',
       'Decimoprimer', 'Decimosegundo', 'Decimotercer', 'Decimocuarto', 'Decimoquinto', 'Decimosexto', 'Decimoséptimo',
       'Decimoctavo', 'Decimonoveno', 'Vigésimo', 'Vigésimo Primer', 'Vigésimo Segundo', 'Vigésimo Tercer',
       'Vigésimo Cuarto', 'Vigésimo Quinto', 'Vigésimo Sexto', 'Vigésimo Séptimo', 'Vigésimo Octavo',
       'Vigésimo Noveno', 'Trigésimo', 'Trigésimo Primer', 'Trigésimo Segundo']
# El estado donde tiene su sede cada circuito, como lo nombra el Órgano de
# Administración Judicial en sus unidades «Circuito Judicial» (OAJ_UEG de la
# base). Algunos circuitos alcanzan municipios de otro estado (el Octavo,
# municipios de Durango; el Décimo, de Veracruz; el Decimoquinto, de Sonora).
EDO = ['CDMX', 'MÉX', 'JAL', 'NL', 'SON', 'PUE', 'VER', 'COAH', 'SLP', 'TAB', 'MICH', 'SIN', 'OAX', 'YUC', 'BC', 'GTO',
       'CHIH', 'MOR', 'TAM', 'CHIS', 'GRO', 'QRO', 'ZAC', 'NAY', 'DGO', 'BCS', 'QROO', 'TLAX', 'HGO', 'AGS', 'CAM', 'COL']
EDO_NOM = dict(zip(EDO, ['Ciudad de México', 'Estado de México', 'Jalisco', 'Nuevo León', 'Sonora', 'Puebla', 'Veracruz', 'Coahuila',
    'San Luis Potosí', 'Tabasco', 'Michoacán', 'Sinaloa', 'Oaxaca', 'Yucatán', 'Baja California', 'Guanajuato', 'Chihuahua', 'Morelos', 'Tamaulipas',
    'Chiapas', 'Guerrero', 'Querétaro', 'Zacatecas', 'Nayarit', 'Durango', 'Baja California Sur', 'Quintana Roo', 'Tlaxcala', 'Hidalgo',
    'Aguascalientes', 'Campeche', 'Colima']))
ALCANCE = {8: 'y municipios de Durango', 10: 'y municipios de Veracruz', 15: 'y un municipio de Sonora'}

# Las páginas: (archivo, icono, título, frase, entrada, órganos, prefijo de temas).
GRUPOS = [
    ('datos-judicial-circuitos-distrito.html', '🏛️', 'Juzgados de distrito por circuito',
     'Litigiosidad y productividad de los 32 circuitos, 2021 a 2025',
     'Cuántos asuntos llegan a los juzgados de distrito de cada circuito por cada 100 mil habitantes, cuántos salen, cuántos se acumulan, '
     'cuánta carga tiene cada persona juzgadora y cuánto tardan, con todos los indicadores que publica la propia estadística del Poder Judicial.',
     ['2'], 'jd'),
    ('datos-judicial-circuitos-colegiados.html', '🧑‍⚖️', 'Tribunales colegiados por circuito',
     'Amparo directo y revisión: litigiosidad y productividad de los 32 circuitos, 2021 a 2025',
     'Los tribunales colegiados de circuito resuelven el amparo directo y las revisiones. Aquí, circuito por circuito, lo que les llega, '
     'lo que resuelven, lo que se les acumula y cuántos días tardan en cada tipo de asunto, con todos los indicadores de la estadística oficial.',
     ['4'], 'tcc'),
    ('datos-judicial-circuitos-apelacion.html', '📜', 'Tribunales de apelación por circuito',
     'Unitarios hasta 2023 y colegiados de apelación desde 2023, circuito por circuito',
     'Los tribunales unitarios de circuito, que revisaban en apelación lo que resolvían los juzgados de distrito, se transformaron en '
     'tribunales colegiados de apelación. Aquí van los dos, cada uno con los años que trae la estadística oficial.',
     ['3', '340'], 'apel'),
]
PAGINA_CIRC = ('datos-judicial-por-circuito.html', '📍', 'Tu circuito judicial',
               'Los 32 circuitos, uno por uno: lo que les llega, lo que resuelven y cuánto tardan',
               'Busca tu circuito: cuántos asuntos llegan a sus juzgados de distrito y a sus tribunales colegiados, cuántos resuelven, '
               'cuántos se les acumulan y cuánto tardan, comparado con todo el país. Con la estadística oficial del Poder Judicial, 2021 a 2025.')
TEMAS_GRUPO = {g[6]: [g[6] + '_litig', g[6] + '_prod'] for g in GRUPOS}
TEMAS_CIRC = ['circ_%d' % n for n in range(1, 33)]
TEMAS = [k for g in GRUPOS for k in TEMAS_GRUPO[g[6]]] + TEMAS_CIRC

# Cómo se dice cada indicador de litigiosidad (nivel 3) en sencillo.
NOMBRE3 = {1: 'Litigiosidad penal', 2: 'Litigiosidad administrativa', 3: 'Litigiosidad civil', 4: 'Litigiosidad del trabajo',
           5: 'Litigiosidad total', 6: 'Existencia inicial (pendientes al empezar el año)', 7: 'Ingresos (asuntos nuevos que entraron)',
           8: 'Carga de trabajo (pendientes, ingresos y traslados)', 9: 'Egresos (asuntos que salieron)', 10: 'Existencia final (pendientes al cerrar el año)',
           11: 'Tasa de asuntos pendientes', 12: 'Asuntos que salen por cada uno que entra («tasa de sentencia» de la DGEJ)',
           13: 'Proporción de egresos con sentencia', 14: 'Crecimiento anual de los ingresos (%)', 15: 'Crecimiento anual de los egresos (%)',
           16: 'Carga de trabajo por persona juzgadora', 17: 'Índice de congestión'}
UNIDAD3 = {1: 'por cada 100 mil habitantes', 2: 'por cada 100 mil habitantes', 3: 'por cada 100 mil habitantes',
           4: 'por cada 100 mil habitantes', 5: 'por cada 100 mil habitantes'}
ORGANO = {'2': 'Juzgados de Distrito', '3': 'Tribunales Unitarios de Circuito', '4': 'Tribunales Colegiados de Circuito',
          '340': 'Tribunales Colegiados de Apelación'}

AVISO = ('<p class="pa-chico">Cómo leerlo: son las cifras que cada órgano reporta de sí mismo al sistema de la DGEJ, por año estadístico '
         '(16 de noviembre a 15 de noviembre). Lo que la DGEJ llama «tasa de sentencia» es egresos ÷ ingresos (1 = sale lo mismo que entra), '
         'no cuántas sentencias se dictan. Su «carga de trabajo» suma, además de lo pendiente y lo nuevo, los asuntos que llegan por traslado de otro órgano, '
         'que «ingresos» no cuenta. El sistema se actualiza y sus totales pueden diferir un poco de los del Anexo Estadístico. '
         'Y no parte 2025 en antes y después de la llegada de las personas electas: eso solo se ve, para todo el país, en «Antes y después de la reforma».</p>')

PEND_ELECTOS = {'que': 'Los mismos indicadores, órgano por órgano, cruzados con quién llegó por elección y quién siguió', 'e': 'pendiente',
                'p': 'judicial-electos-por-organo', 'fu': {'tx': 'DGEJ, Indicadores Estadísticos Judiciales (detalle por órgano de cada circuito)', 'url': SISTEMA}}

_D = None


def datos():
    global _D
    if _D is None:
        with open(ARCHIVO, encoding='utf-8') as f:
            _D = json.load(f)
        _D['idx'] = {(x['org'], x['niv'], x['ind'], x['ano']): x for x in _D['datos']}
    return _D


def get(org, niv, ind, ano):
    return datos()['idx'].get((org, str(niv), ind, ano))


def anos_de(org, niv, ind):
    return [a for a in ANOS if get(org, niv, ind, a)]


def nombre(x):
    if x['niv'] == '3':
        return NOMBRE3.get(x['ind'], x['nombre'])
    n = x['nombre'].replace('ARCCHIVOS', 'ARCHIVOS')
    n = n[0] + n[1:].lower()
    for a in ('jd', 'tuc', 'tcc', 'admvos.'):
        n = n.replace(a, a.upper() if a != 'admvos.' else 'administrativos')
    return n.replace('( ', '(').replace(' )', ')').replace('dias', 'días').replace('instruccion', 'instrucción')


def definicion(org, niv, ind):
    for a in reversed(ANOS):
        x = get(org, niv, ind, a)
        if x and x['defi']:
            return x['defi']
    return ''


def _v(v):
    if v is None:
        return '—'
    if v == int(v) and abs(v) >= 100:
        return format(int(v), ',')
    return format(v, ',.2f').rstrip('0').rstrip('.')


def _pct(a, b):
    return format(round(100.0 * (a - b) / b, 1), '.1f')


def _circ(n):
    return '%s Circuito' % ORD[int(n) - 1]


def _o(que, x, op=None):
    d = {'que': que, 'e': 'derivado' if op else 'oficial',
         'fu': {'tx': 'DGEJ, Indicadores Estadísticos Judiciales, %s %s, %s: «%s»' % (ORGANO[x['org']], x['ano'], 'nivel ' + x['niv'], x['nombre']),
                'url': x['url'], 'sha256': x['sha256']}}
    if op:
        d['op'] = op
    return d


def orden(x, alto=True):
    """Los circuitos ordenados por su valor (de mayor a menor si alto)."""
    return sorted(((int(c), v) for c, v in x['c'].items()), key=lambda cv: (-cv[1] if alto else cv[1], cv[0]))


def lugar(x, n, alto=True):
    o = orden(x, alto)
    for i, (c, _) in enumerate(o, 1):
        if c == n:
            return i, len(o)
    return None, len(o)


def _lista(pares, unidad=''):
    return ', '.join('el <b>%s</b> (%s%s)' % (_circ(c), _v(v), unidad) for c, v in pares)


def chequeo():
    d = datos()
    assert len(ORD) == 32 and len(EDO) == 32
    assert len(d['datos']) > 300, 'faltan cuadros de la DGEJ'
    assert 'vacios' in d, 'el archivo no trae los indicadores vacíos: corre actualizar_indicadores_dgej.py'
    for org in ('2', '4'):
        for a in ANOS:
            for ind in (5, 7, 9, 10, 12, 17):
                x = get(org, 3, ind, a)
                assert x and len(x['c']) >= 30, 'falta %s %s %s' % (org, ind, a)
        # La carga de trabajo del sistema es existencia inicial + ingresos nuevos
        # + los que llegan por traslado (que «Total de ingresos» no suma): la
        # diferencia debe ser positiva y chica (en 2022, 14,934 en los juzgados
        # de distrito contra 15,068 traslados del Anexo). Si no, algo se leyó mal.
        for a in ANOS:
            ei, ing, car = (get(org, 3, i, a)['nac'] for i in (6, 7, 8))
            assert 0 <= car - ei - ing < 0.05 * car, (org, a, ei, ing, car)


def _litig(org, pre):
    """El tema de litigiosidad de un tipo de órgano (o del último disponible)."""
    a0, a1 = anos_de(org, 3, 7)[0], anos_de(org, 3, 7)[-1]
    ing0, ing1 = get(org, 3, 7, a0), get(org, 3, 7, a1)
    ef0, ef1 = get(org, 3, 10, a0), get(org, 3, 10, a1)
    lit = get(org, 3, 5, a1)
    tasa = get(org, 3, 12, a1)
    cong = get(org, 3, 17, a1)
    carga = get(org, 3, 16, a1)
    bajos = [cv for cv in orden(tasa, alto=False) if cv[1] < 1][:3]
    h = ('<p>En %s entraron a los %s <b>%s asuntos</b>; en %s, <b>%s</b> (%s %% de cambio). Al cerrar %s les quedaban <b>%s pendientes</b>; '
         'al cerrar %s, <b>%s</b>.</p><ul class="pa-lista">') % (
        a0, ORGANO[org].lower(), _v(ing0['nac']), a1, _v(ing1['nac']), _pct(ing1['nac'], ing0['nac']), a0, _v(ef0['nac']), a1, _v(ef1['nac']))
    if lit and lit['nac'] is not None:
        h += '<li><b>Dónde se litiga más</b> (asuntos por cada 100 mil habitantes, %s): %s. Nacional: %s.</li>' % (a1, _lista(orden(lit)[:3]), _v(lit['nac']))
    h += '<li><b>Cuántos salen por cada uno que entra</b> (%s): %s en todo el país. ' % (a1, _v(tasa['nac']))
    h += ('Por debajo de 1, donde se acumula: %s.</li>' % _lista(bajos)) if bajos else 'Ningún circuito quedó por debajo de 1.</li>'
    if cong:
        h += '<li><b>Más congestionados</b> (índice de congestión, %s): %s. Nacional: %s.</li>' % (a1, _lista(orden(cong)[:3]), _v(cong['nac']))
    if carga:
        h += '<li><b>Más carga por persona juzgadora</b> (%s): %s asuntos. Nacional: %s.</li>' % (a1, _lista(orden(carga)[:3]), _v(carga['nac']))
    h += '</ul>' + AVISO
    fu = [_o('Ingresos de %s' % a0, ing0), _o('Ingresos de %s' % a1, ing1, 'cambio: (%s − %s) ÷ %s × 100' % (_v(ing1['nac']), _v(ing0['nac']), _v(ing0['nac']))),
          _o('Existencia final de %s' % a0, ef0), _o('Existencia final de %s' % a1, ef1), _o('Egresos ÷ ingresos por circuito, %s' % a1, tasa)]
    if lit and lit['nac'] is not None:
        fu.append(_o('Litigiosidad total por circuito, %s' % a1, lit))
    if cong:
        fu.append(_o('Índice de congestión por circuito, %s' % a1, cong))
    if carga:
        fu.append(_o('Carga de trabajo por persona juzgadora, %s' % a1, carga))
    ci = [{'v': _v(ing1['nac']), 'etq': 'asuntos entraron en %s' % a1, 'e': 'oficial'},
          {'v': _v(ef1['nac']), 'etq': 'pendientes al cerrar %s' % a1, 'e': 'oficial'},
          {'v': _v(tasa['nac']), 'etq': 'asuntos salen por cada uno que entra (%s)' % a1, 'e': 'oficial'}]
    return h, fu, ci


def temas():
    chequeo()
    t = {}
    # Juzgados de distrito.
    h, fu, ci = _litig('2', 'jd')
    t['jd_litig'] = {'tit': 'Juzgados de distrito: litigiosidad y movimiento por circuito', 'h': h, 'fu': fu + [PEND_ELECTOS], 'ci': ci,
                     'sug': ['¿Cuánto tardan los juzgados de distrito por circuito?', '¿Cómo va el Primer Circuito?', '¿Litigiosidad de los tribunales colegiados por circuito?']}
    dur0, dur1 = get('2', 5, 15, '2021'), get('2', 5, 15, '2025')
    sec = [get('2', 5, 23, a) for a in anos_de('2', 5, 23)]
    sen = [get('2', 5, 22, a) for a in anos_de('2', 5, 22)]
    t['jd_prod'] = {
        'tit': 'Juzgados de distrito: productividad y tiempos por circuito',
        'h': ('<p>Un juicio de <b>amparo indirecto</b> tardaba en promedio <b>%s días</b> en un juzgado de distrito en 2021, del ingreso a la sentencia; '
              'en 2025, <b>%s días</b>.</p><ul class="pa-lista"><li><b>Los más lentos</b> (2025): %s.</li><li><b>Los más rápidos</b> (2025): %s.</li>'
              '<li><b>Lo que saca cada persona secretaria a la semana</b> (asuntos proyectados y aprobados que salen): %s en %s; %s en %s.</li>'
              '<li><b>Asuntos que salieron con sentencia</b>: %s en %s; %s en %s.</li></ul>'
              '<p class="pa-chico">El sistema no trae 2023 en estos tres últimos indicadores. Los tiempos del proceso penal federal (del auto de plazo al cierre '
              'de instrucción y a la sentencia) van en las tablas.</p>%s') % (
            _v(dur0['nac']), _v(dur1['nac']), _lista(orden(dur1)[:3], ' días'), _lista(orden(dur1, alto=False)[:3], ' días'),
            _v(sec[0]['nac']), sec[0]['ano'], _v(sec[-1]['nac']), sec[-1]['ano'], _v(sen[0]['nac']), sen[0]['ano'], _v(sen[-1]['nac']), sen[-1]['ano'], AVISO),
        'fu': [_o('Duración del amparo indirecto, 2021', dur0), _o('Duración del amparo indirecto por circuito, 2025', dur1),
               _o('Egreso por secretario, %s' % sec[0]['ano'], sec[0]), _o('Egreso por secretario, %s' % sec[-1]['ano'], sec[-1]),
               _o('Egreso por sentencia, %s' % sen[-1]['ano'], sen[-1]), PEND_ELECTOS],
        'ci': [{'v': _v(dur1['nac']), 'etq': 'días tarda un amparo indirecto (2025)', 'e': 'oficial'},
               {'v': _v(dur0['nac']), 'etq': 'días en 2021', 'e': 'oficial'}],
        'sug': ['¿Litigiosidad de los juzgados de distrito por circuito?', '¿Cuánto tardan los tribunales colegiados por circuito?']}
    # Tribunales colegiados de circuito.
    h, fu, ci = _litig('4', 'tcc')
    t['tcc_litig'] = {'tit': 'Tribunales colegiados de circuito: litigiosidad y movimiento por circuito', 'h': h, 'fu': fu + [PEND_ELECTOS], 'ci': ci,
                      'sug': ['¿Cuánto tardan los tribunales colegiados por circuito?', '¿Cómo va el Tercer Circuito?']}
    ad0, ad1 = get('4', 5, 1, '2021'), get('4', 5, 1, '2025')
    ar0, ar1 = get('4', 5, 2, '2021'), get('4', 5, 2, '2025')
    s0, s1 = get('4', 5, 23, '2021'), get('4', 5, 23, '2025')
    t['tcc_prod'] = {
        'tit': 'Tribunales colegiados: productividad y tiempos por circuito',
        'h': ('<p>Un <b>amparo directo</b> tardaba en promedio <b>%s días</b> en un tribunal colegiado en 2021, del ingreso a la sentencia; en 2025, <b>%s días</b>. '
              'Un <b>amparo en revisión</b>, %s días en 2021 y <b>%s</b> en 2025.</p><ul class="pa-lista">'
              '<li><b>Amparo directo más lento</b> (2025): %s.</li><li><b>Más rápido</b> (2025): %s.</li>'
              '<li><b>Lo que saca cada persona secretaria a la semana</b>: %s en 2021 y %s en 2025.</li></ul>'
              '<p class="pa-chico">Las tablas traen además quejas, reclamaciones, revisión fiscal, impedimentos, conflictos competenciales, '
              'incidentes de inejecución, repetición del acto, inconformidades y reconocimiento de inocencia.</p>%s') % (
            _v(ad0['nac']), _v(ad1['nac']), _v(ar0['nac']), _v(ar1['nac']), _lista(orden(ad1)[:3], ' días'), _lista(orden(ad1, alto=False)[:3], ' días'),
            _v(s0['nac']), _v(s1['nac']), AVISO),
        'fu': [_o('Duración del amparo directo, 2021', ad0), _o('Duración del amparo directo por circuito, 2025', ad1),
               _o('Duración del amparo en revisión, 2021', ar0), _o('Duración del amparo en revisión, 2025', ar1),
               _o('Egreso por secretario, 2021', s0), _o('Egreso por secretario, 2025', s1), PEND_ELECTOS],
        'ci': [{'v': _v(ad1['nac']), 'etq': 'días tarda un amparo directo (2025)', 'e': 'oficial'},
               {'v': _v(ad0['nac']), 'etq': 'días en 2021', 'e': 'oficial'}],
        'sug': ['¿Litigiosidad de los tribunales colegiados por circuito?', '¿Cuánto tarda un amparo indirecto por circuito?']}
    # Apelación: unitarios (2021-2023) y colegiados de apelación (2023-2025).
    h, fu, ci = _litig('340', 'apel')
    u0, u1 = anos_de('3', 3, 7)[0], anos_de('3', 3, 7)[-1]
    h = ('<p>Los <b>tribunales unitarios de circuito</b> se transformaron en <b>tribunales colegiados de apelación</b>: la estadística trae los unitarios de %s a %s '
         '(%s asuntos entraron en %s) y los de apelación de 2023 a 2025.</p>' % (u0, u1, _v(get('3', 3, 7, u0)['nac']), u0)) + h
    t['apel_litig'] = {'tit': 'Tribunales de apelación: litigiosidad y movimiento por circuito', 'h': h,
                       'fu': [_o('Ingresos de los tribunales unitarios, %s' % u0, get('3', 3, 7, u0))] + fu + [PEND_ELECTOS], 'ci': ci,
                       'sug': ['¿Productividad de los tribunales de apelación por circuito?', '¿Litigiosidad de los juzgados de distrito por circuito?']}
    e1 = [get('340', 5, i, '2025') for i in (22, 21, 23)]
    du = get('3', 5, 13, u1)
    t['apel_prod'] = {
        'tit': 'Tribunales de apelación: productividad por circuito',
        'h': ('<p>En 2025, los tribunales colegiados de apelación sacaron <b>%s asuntos con sentencia</b> y %s por resolución inicial; cada persona secretaria '
              'sacó <b>%s a la semana</b>.</p><p>De los unitarios queda el último año: en %s, una apelación de un proceso penal federal tardaba <b>%s días</b>. '
              'Cuánto tardan los colegiados de apelación no lo publica todavía el sistema de la DGEJ: el indicador existe, pero sale vacío.</p>%s') % (
            _v(e1[0]['nac']), _v(e1[1]['nac']), _v(e1[2]['nac']), u1, _v(du['nac']), AVISO),
        'fu': [_o('Egreso por sentencia, 2025', e1[0]), _o('Egreso por resolución inicial, 2025', e1[1]), _o('Egreso por secretario, 2025', e1[2]),
               _o('Duración de los procesos penales federales en los unitarios, %s' % u1, du),
               {'que': 'Cuánto tardan los tribunales colegiados de apelación', 'e': 'pendiente', 'p': 'judicial-apelacion-tiempos', 'fu': {'tx': 'DGEJ, Indicadores Estadísticos Judiciales, nivel 5', 'url': SISTEMA}},
               PEND_ELECTOS],
        'ci': [{'v': _v(e1[0]['nac']), 'etq': 'asuntos con sentencia en los colegiados de apelación (2025)', 'e': 'oficial'}],
        'sug': ['¿Litigiosidad de los tribunales de apelación por circuito?', '¿Cuánto tardan los tribunales colegiados por circuito?']}
    # Un tema por circuito.
    for n in range(1, 33):
        c = str(n)
        partes, fu = [], []
        for org, que, dur in (('2', 'juzgados de distrito', (15, 'un amparo indirecto')), ('4', 'tribunales colegiados', (1, 'un amparo directo'))):
            i0, i1 = get(org, 3, 7, '2021'), get(org, 3, 7, '2025')
            e0, e1_ = get(org, 3, 10, '2021'), get(org, 3, 10, '2025')
            ta = get(org, 3, 12, '2025')
            du = get(org, 5, dur[0], '2025')
            if c not in i1['c']:
                continue
            lt, tot = lugar(ta, n, alto=False)
            s = ('<li><b>%s</b>: entraron %s asuntos en 2025 (%s en 2021). Salieron <b>%s por cada uno que entró</b> (nacional: %s; '
                 'lugar %d de %d entre los que menos sacan). Pendientes al cerrar 2025: <b>%s</b> (%s en 2021).') % (
                que.capitalize(), _v(i1['c'][c]), _v(i0['c'].get(c)), _v(ta['c'][c]), _v(ta['nac']), lt, tot, _v(e1_['c'][c]), _v(e0['c'].get(c)))
            if du and c in du['c']:
                s += ' %s tarda <b>%s días</b> (nacional: %s).' % (dur[1].capitalize(), _v(du['c'][c]), _v(du['nac']))
                fu.append(_o('Duración (%s), 2025' % dur[1], du))
            partes.append(s + '</li>')
            fu += [_o('Ingresos de los %s, 2021 y 2025' % que, i1), _o('Egresos ÷ ingresos de los %s, 2025' % que, ta),
                   _o('Existencia final de los %s, 2025' % que, e1_)]
        lit = get('2', 3, 5, '2025')
        ll, lt_ = lugar(lit, n)
        t['circ_%d' % n] = {
            'tit': '%s Circuito: %s%s' % (ORD[n - 1], EDO_NOM[EDO[n - 1]], ' ' + ALCANCE[n] if n in ALCANCE else ''),
            'h': ('<p>En los juzgados de distrito del <b>%s Circuito</b> entraron <b>%s asuntos por cada 100 mil habitantes</b> en 2025: '
                  'lugar %d de %d en litigiosidad (nacional: %s).</p><ul class="pa-lista">%s</ul>%s') % (
                ORD[n - 1], _v(lit['c'][c]), ll, lt_, _v(lit['nac']), ''.join(partes), AVISO),
            'fu': [_o('Litigiosidad total de los juzgados de distrito por circuito, 2025', lit)] + fu + [PEND_ELECTOS],
            'ci': [{'v': _v(lit['c'][c]), 'etq': 'asuntos por cada 100 mil habitantes en sus juzgados de distrito (2025)', 'e': 'oficial'}],
            'sug': ['¿Litigiosidad de los juzgados de distrito por circuito?', '¿Cuánto tardan los tribunales colegiados por circuito?']}
    return t


def _tabla(org, niv, ind):
    an = anos_de(org, niv, ind)
    xs = [get(org, niv, ind, a) for a in an]
    nom = nombre(xs[-1])
    filas = ''.join('<tr><th scope="row">%s</th>%s</tr>' % (_circ(n), ''.join('<td>%s</td>' % _v(x['c'].get(str(n))) for x in xs))
                    for n in range(1, 33) if any(str(n) in x['c'] for x in xs))
    nac = '<tr><th scope="row">Nacional</th>%s</tr>' % ''.join('<td>%s</td>' % _v(x['nac']) for x in xs)
    defi = definicion(org, niv, ind)
    ult = xs[-1]['nac']
    return ('<details class="ic-ind"><summary>%s%s</summary>%s<div class="leg-tabla-caja"><table class="leg-tabla">'
            '<caption>%s, %s</caption><thead><tr><th scope="col">Circuito</th>%s</tr></thead><tbody>%s</tbody><tfoot>%s</tfoot></table></div>'
            '<p class="pa-chico">Cuadros de la DGEJ: %s.</p></details>') % (
        html.escape(nom), (' · nacional %s: %s' % (an[-1], _v(ult))) if ult is not None else '',
        '<p class="pa-chico">%s%s</p>' % (html.escape(defi), (' ' + UNIDAD3[ind].capitalize() + '.') if niv == 3 and ind in UNIDAD3 and 'habitantes' not in defi else '') if defi else '',
        html.escape(ORGANO[org]), html.escape(nom), ''.join('<th scope="col">%s</th>' % a for a in an), filas, nac,
        ', '.join('<a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>' % (html.escape(x['url'], quote=True), x['ano']) for x in xs))


def indicadores(org, niv):
    return sorted({x['ind'] for x in datos()['datos'] if x['org'] == org and x['niv'] == str(niv)})


NIVEL_NOM = {'1': 'Plantilla judicial', '2': 'Perfil de juezas, jueces y magistraturas', '3': 'Litigiosidad', '4': 'Acceso tecnológico',
             '5': 'Productividad', '6': 'Incidencia (por materia, delito y acto reclamado)'}


def vacios(org):
    """Lo que el sistema anuncia para este órgano y publica sin valores, en los
    años en que el órgano existía (los unitarios hasta 2023; los colegiados de
    apelación desde 2023)."""
    vivos = {x['ano'] for x in datos()['datos'] if x['org'] == org}
    out = []
    for v in datos().get('vacios', []):
        an = [a for a in v['anos'] if a in vivos]
        if v['org'] == org and an:
            out.append(dict(v, anos=an))
    return out


def _vacios_html(orgs):
    from asistente_legislativo import _chip
    filas = ''
    for org in orgs:
        for v in vacios(org):
            n = nombre(dict(v, niv=v['niv'])) if v['niv'] != '3' else NOMBRE3.get(v['ind'], v['nombre'])
            filas += '<li>%s%s · %s · %s</li>' % ((html.escape(ORGANO[org]) + ': ') if len(orgs) > 1 else '', html.escape(NIVEL_NOM[v['niv']]),
                                                 html.escape(n), ', '.join(v['anos']))
    if not filas:
        return ''
    return ('<details class="ic-ind"><summary>Lo que el sistema anuncia y publica vacío %s</summary><p class="pa-chico">El sistema de la DGEJ tiene estos indicadores, '
            'pero en los años que se indican no trae ningún valor, ni por circuito ni en el total nacional. Plantilla, perfil, acceso tecnológico e incidencia salen vacíos '
            'en todos los órganos de 2021 a 2025 (y en los juzgados de distrito, también en 2008, 2011, 2015 y 2018 a 2020, que revisamos). '
            'Cuántas juezas y jueces hay, su edad, sus estudios y su antigüedad, cuánto personal tienen y de qué tratan los asuntos son datos que el Órgano de '
            'Administración Judicial tiene y no publica ahí.</p><ul class="pa-lista">%s</ul></details>') % (_chip('pendiente', 'judicial-indicadores-vacios'), filas)


def extra(k):
    """Las tablas de la página: todos los indicadores, circuito por circuito y año por año."""
    from asistente_legislativo import _chip
    if k.startswith('circ_'):
        return ''
    pre, cual = k.rsplit('_', 1)
    niv = 3 if cual == 'litig' else 5
    orgs = next(g[5] for g in GRUPOS if g[6] == pre)
    out = '<p class="pa-chico">Todos los indicadores de %s que publica la DGEJ %s. Toca cada uno para abrir su tabla.</p>' % (
        'litigiosidad' if niv == 3 else 'productividad', _chip('oficial'))
    for org in orgs:
        if len(orgs) > 1:
            out += '<h3 class="ic-org">%s</h3>' % html.escape(ORGANO[org])
        out += ''.join(_tabla(org, niv, i) for i in indicadores(org, niv))
    if cual == 'litig':
        out += _vacios_html(orgs)
    return out + '<p class="pa-chico">Fuente: <a href="%s" target="_blank" rel="noopener noreferrer">Indicadores Estadísticos Judiciales de la DGEJ ↗</a>.</p>' % SISTEMA


def paginas():
    """Las entradas de PAGINAS de asistente_judicial.py."""
    return [(g[0], g[1], g[2], g[3], g[4], TEMAS_GRUPO[g[6]]) for g in GRUPOS] + [PAGINA_CIRC + (TEMAS_CIRC,)]
