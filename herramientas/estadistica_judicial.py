# -*- coding: utf-8 -*-
"""Antes y después de la reforma judicial: lo que resuelven los juzgados y
tribunales federales, con la estadística oficial del propio Poder Judicial
(pedido del autor, 01-11-2026: «ir auditando… haciendo una diferencia de
antes y después de la reforma judicial… sacar este tipo de indicadores de
datos para exhibirlos aquí»).

La fuente es pública y no pide clave: los Anexos Estadísticos de la
Dirección General de Estadística Judicial (DGEJ), que forman parte del
informe de labores del Órgano de Administración Judicial (antes, del Consejo
de la Judicatura Federal). Se cotejaron el 01-11-2026 en su
introducción, que trae el movimiento nacional y las personas juzgadoras:

- 2022, 2023 y 2024: año estadístico del 16 de noviembre al 15 de noviembre.
- 2025-1: del 16-11-2024 al 30-06-2025. Todo antes del cambio de personas
  juzgadoras (las electas tomaron protesta el 1-09-2025).
- 2025-2: el año estadístico completo, del 16-11-2024 al 15-11-2025.

El tramo «después» (1-07-2025 a 15-11-2025) no lo publica la DGEJ por
separado: se saca restando 2025-1 de 2025-2 y va como derivado, con tres
avisos que se dicen siempre: incluye julio y agosto, todavía con las personas
juzgadoras anteriores; 2025-2 corrige algunas cifras de 2025-1 (la
existencia inicial pasó de 705,673 a 703,813), así que la resta es
aproximada; y comparar por día no corrige vacaciones ni días inhábiles.

Lo que todavía no se puede decir, con su ficha en el Registro de pendientes:
cómo resuelven las personas electas frente a las que siguieron, órgano por
órgano (la DGEJ publica tabulados por órgano y la plataforma aún no los cruza
con la lista del INE), y la estadística de la nueva Suprema Corte.

La lee asistente_judicial.py: sus temas entran a D.jud y a la página
«Antes y después de la reforma» de Datos · Poder Judicial.
"""

import html

PAGINA = 'datos-judicial-reforma.html'
TEMAS = ['reforma_antes_despues', 'reforma_serie', 'reforma_titulares']

DGEJ = 'https://www.dgej.cjf.gob.mx/paginas/informacionRelevante.htm?pageName=informacion%2FanexoEstadisticoWeb.htm'
_BASE = 'https://www.dgej.cjf.gob.mx/resources/anexos/'

# Introducción de cada Anexo Estadístico, con su huella SHA-256 (01-11-2026).
DOC = {
    '2022': ('2022/graficas/intro_2022.pdf', '2ec8a8d25b831d66ecfa13d1a193000d3a6cf2b285ab8391c953c851c463fc27'),
    '2023': ('2023/graficas/intro_2023.pdf', '7de19e9181d44111b54cd51f4eb172793ece065ee9e9b6d85ee1edc5a7d24d6c'),
    '2024': ('2024/graficas/intro_2024.pdf', 'ef57285986c76416da423abd1c44bcd507cbcb1cf0b2f70b09310e409fec4c41'),
    '2025-1': ('2025/graficas/intro_2025.pdf', '0a9060e2da686d358dac96693a9523ac3d7fa0b8f01720d60ee813a099ea1ebc'),
    '2025-2': ('2025/graficas/intro_2025-2.pdf', 'aa036b58b4072ee07514076885f135ec58708ce1b9a968431b788b2b435d0ec9'),
}
PERIODO = {'2022': '16-11-2021 a 15-11-2022', '2023': '16-11-2022 a 15-11-2023', '2024': '16-11-2023 a 15-11-2024',
           '2025-1': '16-11-2024 a 30-06-2025', '2025-2': '16-11-2024 a 15-11-2025'}


def _f(k, donde):
    ruta, sha = DOC[k]
    tx = 'Órgano de Administración Judicial, DGEJ, Anexo Estadístico %s (%s), introducción, %s' % (
        '2025, corte al 30 de junio' if k == '2025-1' else ('2025' if k == '2025-2' else k), PERIODO[k], donde)
    return {'tx': tx, 'url': _BASE + ruta, 'sha256': sha}


# Movimiento nacional de los órganos ordinarios: (existencia inicial, total de
# ingresos, carga de trabajo, total de egresos, existencia final, dónde).
# Ingresos y egresos incluyen los de traslado o por acuerdo, como los suma el anexo.
MOV = {
    '2022': (468908, 1346228, 1815136, 1285953, 525486, 'apartado 1.6 y cuadro 1.10'),
    '2023': (531571, 1493712, 2025283, 1413724, 610782, 'cuadro 10'),
    '2024': (606330, 2024297, 2630627, 1920547, 706419, 'apartado 1.6 y cuadro 10'),
    '2025-1': (705673, 1988882, 2694555, 1923028, 771532, 'apartado 1.6'),
    '2025-2': (703813, 3094458, 3798271, 2960367, 837930, 'apartado 1.6 y cuadro 11'),
}
# Por tipo de órgano, solo los dos que más pesan (mismo orden que MOV):
# tribunales colegiados de circuito y juzgados de distrito.
TCC = {
    '2024': (252930, 418445, 671375, 393256, 277970, 'cuadro 10'),
    '2025-1': (278049, 351012, 629061, 293270, 335804, 'apartado A, Tribunales Colegiados de Circuito'),
    '2025-2': (277951, 559584, 837535, 461457, 376086, 'cuadro 11'),
}
JD = {
    '2024': (179089, 1426898, 1605987, 1383576, 221872, 'cuadro 10'),
    '2025-1': (222005, 1504556, 1726561, 1517958, 208606, 'apartado C, Juzgados de Distrito'),
    '2025-2': (221972, 2310410, 2532382, 2317989, 214390, 'cuadro 11'),
}
DIAS_ANTES, DIAS_DESPUES = 227, 138  # 16-11-2024 a 30-06-2025 y 1-07-2025 a 15-11-2025

# Personas titulares de órganos ordinarios (apartado 1.4): (total, mujeres).
# 2024 y 2025 completos vienen en el texto del anexo; el corte de junio de
# 2025 solo da el porcentaje de mujeres (su cuadro es una imagen).
TIT = {
    '2024': [('Tribunales Colegiados de Circuito', 668, 144), ('Tribunales Colegiados de Apelación', 106, 35),
             ('Juzgados de Distrito', 417, 188), ('Centros de Justicia Penal Federal', 171, 39),
             ('Centro Nacional de Justicia Especializado (técnicas de investigación)', 10, 3),
             ('Tribunales Laborales Federales', 141, 58), ('Plenos Regionales', 12, 7)],
    '2025-2': [('Tribunales Colegiados de Circuito', 684, 290), ('Tribunales Colegiados de Apelación', 104, 48),
               ('Juzgados de Distrito', 421, 229), ('Centros de Justicia Penal Federal', 166, 66),
               ('Centro Nacional de Justicia Especializado (técnicas de investigación)', 10, 4),
               ('Tribunales Laborales Federales', 142, 71), ('Plenos Regionales', 12, 8)],
}
MUJERES_PCT = {'2024': '31.1', '2025-1': '32', '2025-2': '47'}  # como lo dice cada anexo
# Personas secretarias en funciones de titulares de órganos ordinarios
# (apartado 1.5): no hay juez o magistrado nombrado y lo suple su secretario.
SECRETARIAS = {'2025-1': 444, '2025-2': 138}


def _n(v):
    return format(int(round(v)), ',')


def _pct(a, b, dec=1):
    return format(round(100.0 * a / b, dec), '.%df' % dec)


def _o(que, fu, op=None, e=None, p=None):
    d = {'que': que, 'e': e or ('derivado' if op else 'oficial'), 'fu': fu}
    if op:
        d['op'] = op
    if p:
        d['p'] = p
    return d


def despues(t):
    """El tramo 1-07-2025 a 15-11-2025: 2025-2 menos 2025-1 (ingresos, egresos)."""
    return (t['2025-2'][1] - t['2025-1'][1], t['2025-2'][3] - t['2025-1'][3])


def chequeo():
    """Que la transcripción cuadre consigo misma: carga = existencia inicial + ingresos."""
    for tabla in (MOV, TCC, JD):
        for k, r in tabla.items():
            assert r[0] + r[1] == r[2], 'La carga de trabajo no cuadra en %s: %s' % (k, r)
    for k, filas in TIT.items():
        assert len(filas) == 7
    assert sum(f[1] for f in TIT['2024']) == 1525 and sum(f[2] for f in TIT['2024']) == 474
    assert sum(f[1] for f in TIT['2025-2']) == 1539 and sum(f[2] for f in TIT['2025-2']) == 716
    assert _pct(474, 1525) == MUJERES_PCT['2024']
    assert round(100.0 * 716 / 1539) == int(MUJERES_PCT['2025-2'])
    assert DIAS_ANTES + DIAS_DESPUES == 365


PEND_ELECTOS = {'que': 'Cómo resuelven las personas juzgadoras electas en 2025 frente a las que siguieron, órgano por órgano', 'e': 'pendiente',
                'p': 'judicial-electos-por-organo', 'fu': {'tx': 'DGEJ, Anexo Estadístico: tabulados por órgano jurisdiccional', 'url': DGEJ}}
PEND_SCJN = {'que': 'Cuántos asuntos resuelve la nueva Suprema Corte y cuánto tarda, comparado con la anterior', 'e': 'pendiente',
             'p': 'scjn-estadistica-nueva-corte', 'fu': {'tx': 'Suprema Corte de Justicia de la Nación: estadística judicial', 'url': 'https://www.scjn.gob.mx/'}}

AVISO = ('<p class="pa-chico">Cómo leerlo: el tramo «después» no lo publica la DGEJ por separado; es nuestra resta del año completo menos el corte de junio. '
         'Incluye <b>julio y agosto</b>, todavía con las personas juzgadoras anteriores (las electas empezaron el 1 de septiembre); el anexo del año completo '
         '<b>corrige algunas cifras</b> del corte de junio, así que la resta es aproximada; y la cuenta por día <b>no corrige vacaciones ni días inhábiles</b>. '
         'Son cifras que <b>cada órgano reporta de sí mismo</b>. Y una baja no dice por qué: puede ser el cambio de personas, la curva de aprendizaje, '
         'más asuntos difíciles o menos personal. Eso no lo dice el anexo.</p>')


def temas():
    """Los tres temas del bot y de la página."""
    chequeo()
    t = {}
    a_i, a_e = MOV['2025-1'][1], MOV['2025-1'][3]
    d_i, d_e = despues(MOV)
    tc_i, tc_e = despues(TCC)
    jd_i, jd_e = despues(JD)
    t['reforma_antes_despues'] = {
        'tit': 'Antes y después de la reforma: lo que resuelven los juzgados y tribunales federales',
        'h': '<p>La estadística oficial del Poder Judicial parte el año 2025 en dos, y eso deja ver el cambio. Del <b>16 de noviembre de 2024 al 30 de junio de 2025</b> '
             '(antes de la reforma) los juzgados y tribunales federales sacaron <b>%s de cada 100</b> asuntos que les entraron. Del <b>1 de julio al 15 de noviembre</b>, '
             '<b>%s de cada 100</b>.</p><ul class="pa-lista">'
             '<li><b>Juzgados de distrito:</b> antes, %s de cada 100 (sacaban también rezago); después, <b>%s</b>.</li>'
             '<li><b>Tribunales colegiados de circuito</b> (amparo directo y revisión): antes, %s de cada 100; después, <b>%s</b>. Ahí ya se acumulaba: '
             'cerraron el año con <b>%s asuntos pendientes</b>, %s %% más que al cierre de 2024.</li>'
             '<li>Por día, entraban unos %s asuntos y salían %s; después, entraban %s y salían %s.</li></ul>%s' % (
                 _pct(a_e, a_i), _pct(d_e, d_i), _pct(JD['2025-1'][3], JD['2025-1'][1]), _pct(jd_e, jd_i),
                 _pct(TCC['2025-1'][3], TCC['2025-1'][1]), _pct(tc_e, tc_i), _n(TCC['2025-2'][4]),
                 _pct(TCC['2025-2'][4] - TCC['2024'][4], TCC['2024'][4]),
                 _n(a_i / DIAS_ANTES), _n(a_e / DIAS_ANTES), _n(d_i / DIAS_DESPUES), _n(d_e / DIAS_DESPUES), AVISO),
        'fu': [_o('Movimiento nacional al 30 de junio de 2025: ingresos y egresos', _f('2025-1', MOV['2025-1'][5])),
               _o('Movimiento nacional del año completo, al 15 de noviembre de 2025', _f('2025-2', MOV['2025-2'][5])),
               _o('Tribunales colegiados y juzgados de distrito, corte de junio', _f('2025-1', 'apartados A y C')),
               _o('Tribunales colegiados y juzgados de distrito, año completo (cuadro 11)', _f('2025-2', 'cuadro 11')),
               _o('El tramo de julio a noviembre', _f('2025-2', 'cuadro 11'),
                  'ingresos: %s − %s = %s; egresos: %s − %s = %s' % (_n(MOV['2025-2'][1]), _n(a_i), _n(d_i), _n(MOV['2025-2'][3]), _n(a_e), _n(d_e))),
               _o('Asuntos que salen por cada 100 que entran', _f('2025-2', 'cuadro 11'),
                  'antes: %s ÷ %s × 100; después: %s ÷ %s × 100' % (_n(a_e), _n(a_i), _n(d_e), _n(d_i))),
               _o('Por día', _f('2025-2', 'cuadro 11'), 'entre %d días (16-11-2024 a 30-06-2025) y %d días (1-07 a 15-11-2025)' % (DIAS_ANTES, DIAS_DESPUES)),
               PEND_ELECTOS, PEND_SCJN],
        'ci': [{'v': _pct(a_e, a_i), 'etq': 'asuntos que salieron por cada 100 que entraron, antes (nov-2024 a jun-2025)', 'e': 'derivado'},
               {'v': _pct(d_e, d_i), 'etq': 'después (jul a nov-2025)', 'e': 'derivado'},
               {'v': _n(TCC['2025-2'][4]), 'etq': 'asuntos pendientes en los tribunales colegiados al 15-11-2025', 'e': 'oficial'}],
        'sug': ['¿Cómo ha crecido el rezago de los juzgados federales?', '¿Cuántas juezas hay desde la reforma?', '¿Cuánto rezago penal hay?']}
    s0, s1 = MOV['2022'], MOV['2025-2']
    t['reforma_serie'] = {
        'tit': 'Cuatro años de juzgados federales: lo que entra, lo que sale y lo que se acumula',
        'h': '<p>Al cierre de cada año estadístico, los juzgados y tribunales federales se quedan con asuntos sin terminar. En 2022 eran <b>%s</b>; '
             'al 15 de noviembre de 2025, <b>%s</b>: <b>%s %% más</b>. Solo en el último año crecieron %s %%.</p>'
             '<p>No es que trabajen menos: en 2025 salieron %s asuntos, más del doble que en 2022. Es que entran todavía más: %s. '
             'El anexo no explica en su resumen nacional por qué crecieron tanto los ingresos.</p>'
             '<p class="pa-chico">Cada anexo corrige un poco el cierre del anterior (por eso la existencia inicial de un año no siempre es la final del año pasado). '
             'Son cifras que cada órgano reporta de sí mismo.</p>' % (
                 _n(s0[4]), _n(s1[4]), _pct(s1[4] - s0[4], s0[4]), _pct(s1[4] - MOV['2024'][4], MOV['2024'][4]), _n(s1[3]), _n(s1[1])),
        'fu': [_o('Movimiento nacional de %s' % k, _f(k, MOV[k][5])) for k in ('2022', '2023', '2024', '2025-2')] +
              [_o('Aumento de lo pendiente', _f('2025-2', 'apartado 1.6'),
                  '(%s − %s) ÷ %s × 100' % (_n(s1[4]), _n(s0[4]), _n(s0[4])))],
        'ci': [{'v': _n(s1[4]), 'etq': 'asuntos pendientes al 15-11-2025', 'e': 'oficial'},
               {'v': _pct(s1[4] - s0[4], s0[4]) + ' %', 'etq': 'más que al cierre de 2022', 'e': 'derivado'}],
        'sug': ['¿Resuelven igual los juzgados federales después de la reforma judicial?', '¿Cuánto rezago penal hay?']}
    m24 = sum(f[2] for f in TIT['2024'])
    m25 = sum(f[2] for f in TIT['2025-2'])
    t['reforma_titulares'] = {
        'tit': 'Quién juzga desde la reforma: juezas, jueces y suplentes',
        'h': '<p>Las mujeres eran el <b>%s %%</b> de las personas titulares de juzgados y tribunales federales al cierre de 2024 y el %s %% en junio de 2025. '
             'Al 15 de noviembre de 2025, con las personas electas ya en funciones, son el <b>%s %%</b>: %s de %s. En los juzgados de distrito ya son mayoría.</p>'
             '<p>Otro dato que casi nadie mira: las <b>personas secretarias que hacían las veces de jueza, juez o magistratura</b>, porque en ese lugar no había '
             'titular. El 30 de junio de 2025 eran <b>%s</b>; el 15 de noviembre, <b>%s</b>.</p>'
             '<p class="pa-chico">El anexo cuenta personas titulares, no cuántas llegaron por elección y cuántas siguieron. Ese cruce está pendiente.</p>' % (
                 MUJERES_PCT['2024'], MUJERES_PCT['2025-1'], MUJERES_PCT['2025-2'], _n(m25), _n(sum(f[1] for f in TIT['2025-2'])),
                 _n(SECRETARIAS['2025-1']), _n(SECRETARIAS['2025-2'])),
        'fu': [_o('Personas titulares por sexo y tipo de órgano, 2024', _f('2024', 'apartado 1.4')),
               _o('Porcentaje de mujeres titulares al 30 de junio de 2025', _f('2025-1', 'apartado 1.4')),
               _o('Personas titulares por sexo y tipo de órgano, 15 de noviembre de 2025', _f('2025-2', 'apartado 1.4 y cuadro 8')),
               _o('Personas secretarias en funciones de titulares', _f('2025-1', 'apartado 1.5')),
               _o('Personas secretarias en funciones de titulares', _f('2025-2', 'apartado 1.5')),
               PEND_ELECTOS],
        'ci': [{'v': MUJERES_PCT['2025-2'] + ' %', 'etq': 'de las personas titulares son mujeres (nov-2025)', 'e': 'oficial'},
               {'v': MUJERES_PCT['2024'] + ' %', 'etq': 'al cierre de 2024', 'e': 'oficial'},
               {'v': _n(SECRETARIAS['2025-2']), 'etq': 'personas secretarias haciendo de titular (nov-2025)', 'e': 'oficial'}],
        'sug': ['¿Resuelven igual los juzgados federales después de la reforma judicial?', '¿Cuántos cargos se votaron en la elección judicial?']}
    return t


def extra(k):
    """Las tablas de la página, debajo del texto de cada tema."""
    from asistente_legislativo import _chip
    pie = '<p class="pa-chico">Fuente: <a href="%s" target="_blank" rel="noopener noreferrer">Anexos Estadísticos de la DGEJ ↗</a> (introducción de cada año). %s</p>'
    if k == 'reforma_antes_despues':
        def fila(nom, tb):
            di, de = despues(tb)
            a = tb['2025-1']
            return '<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                nom, _n(a[1]), _n(a[3]), _pct(a[3], a[1]), _n(di), _n(de), _pct(de, di))
        filas = fila('Todos los órganos', MOV) + fila('Juzgados de distrito', JD) + fila('Tribunales colegiados de circuito', TCC)
        return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Antes (16-11-2024 a 30-06-2025) %s y después (1-07 a 15-11-2025) %s</caption>'
                '<thead><tr><th scope="col">Órgano</th><th scope="col">Entraron antes</th><th scope="col">Salieron antes</th><th scope="col">De cada 100</th>'
                '<th scope="col">Entraron después</th><th scope="col">Salieron después</th><th scope="col">De cada 100</th></tr></thead><tbody>%s</tbody></table></div>'
                '<p class="pa-chico">Cómo resuelven las personas electas frente a las que siguieron: %s</p>' + pie) % (
            _chip('oficial'), _chip('derivado'), filas, _chip('pendiente', 'judicial-electos-por-organo'), DGEJ, 'Corte de junio y año completo 2025.')
    if k == 'reforma_serie':
        filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            '2025' if a == '2025-2' else a, _n(MOV[a][1]), _n(MOV[a][3]), _pct(MOV[a][3], MOV[a][1]), _n(MOV[a][4]))
            for a in ('2022', '2023', '2024', '2025-2'))
        return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Juzgados y tribunales federales, cada año estadístico %s</caption>'
                '<thead><tr><th scope="col">Año</th><th scope="col">Entraron</th><th scope="col">Salieron</th><th scope="col">De cada 100 %s</th>'
                '<th scope="col">Pendientes al cierre</th></tr></thead><tbody>%s</tbody></table></div>' + pie) % (
            _chip('oficial'), _chip('derivado'), filas, DGEJ, 'Del 16 de noviembre al 15 de noviembre de cada año.')
    if k == 'reforma_titulares':
        f25 = {f[0]: f for f in TIT['2025-2']}
        filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            html.escape(n), _n(t), _n(m), _n(f25[n][1]), _n(f25[n][2])) for n, t, m in TIT['2024'])
        return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Personas titulares de órganos federales ordinarios %s</caption>'
                '<thead><tr><th scope="col">Órgano</th><th scope="col">Titulares 2024</th><th scope="col">Mujeres 2024</th>'
                '<th scope="col">Titulares nov-2025</th><th scope="col">Mujeres nov-2025</th></tr></thead><tbody>%s</tbody>'
                '<tfoot><tr><th scope="row">Total</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr></tfoot></table></div>' + pie) % (
            _chip('oficial'), filas, _n(sum(f[1] for f in TIT['2024'])), _n(sum(f[2] for f in TIT['2024'])),
            _n(sum(f[1] for f in TIT['2025-2'])), _n(sum(f[2] for f in TIT['2025-2'])), DGEJ,
            'Sin las personas secretarias que suplen a un titular.')
    return ''
