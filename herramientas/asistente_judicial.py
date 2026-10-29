# -*- coding: utf-8 -*-
"""El Poder Judicial de la Federación, en el formato con que conversa el bot
y en sus páginas de la pestaña Datos (pedido del autor, 23-10-2026: «integra
la pestaña del Poder Judicial que se encuentra en la enciclopedia a nuestro
bot auditor… y que esté replicada en Datos, con cada subpestaña en su propia
página»).

La Enciclopedia sigue congelada: sus subpestañas 4.1 a 4.6 (estructura, el
Pleno, prestaciones, asesores, cálculos y cómo decide un juez) solo
guiaron los temas. Ninguna cifra se copió de ella. Cada dato se cotejó
contra su documento oficial al 23-10-2026:

- Constitución (texto vigente de la Cámara de Diputados, última reforma
  DOF 07-10-2026): arts. 17, 94 a 100, 103, 105 y 107, y los transitorios de
  la reforma judicial (DOF 15-09-2024), con los cambios del 02-06-2026.
- Ley de Amparo (texto vigente, última reforma DOF 16-10-2025): los cuatro
  recursos y sus plazos (arts. 80 a 105, 201 y 202), y quién conoce de la
  revisión (83 y 84). Entraron el 24-10-2026, cuando el autor pidió
  rescatar de la Enciclopedia antigua «los cuatro instrumentos», «los
  recursos» y «cuándo llega un caso a la Corte».
- INE, Acuerdo INE/CG563/2025 (sumatoria nacional y asignación de la SCJN)
  e INE/CG564/2025 (declaración de validez; considerando 25: los 881 cargos
  de 2025 en 32 circuitos). Copias con su huella SHA-256.
- Manual de remuneraciones del PJF 2026 (DOF 27-02-2026), anexo B.
- Presupuesto 2026 del Ramo 03, el ejercicio de la SCJN al 31-08-2026 y los
  pagos del OAJ por circuito: la colección «poderes» de window.AUDIT_DB
  (herramientas/integrar_poderes.py, investigación del 25-09-2026).

Lo que la Enciclopedia decía y no se sostuvo (por eso no entra): los
$206,948 mensuales de un ministro (el tabulador 2026 dice $134,310 netos),
los $5,529,450 anuales «integrados», la ponencia «promedio» de 35 plazas y
$34.2 millones al año, los $78,327 millones del Ramo 03 (el PEF 2026 aprobó
$70,005.6), los «$35 a $42 millones» por despacho y los «$15,434 millones en
13 fideicomisos», que el decreto no menciona.

Lo que queda pendiente, con su ficha en el Registro: la participación y el
costo final de la elección de 2025, el monto que se devolvió de los
fideicomisos, y el costo completo de cada circuito y de cada ponencia.

asistente-charla.js lo lee como D.jud; las páginas de Datos se arman con
paginas() (apartados.py).
"""

import html

from asistente_legislativo import CPEUM, _chip, _fuentes, bloque_tema
import gestion_judicial

INE563 = {'tx': 'INE, Acuerdo INE/CG563/2025: sumatoria nacional y asignación de ministras y ministros de la SCJN (15-06-2025)',
          'url': 'https://dof.gob.mx/2025/INE/CGext202506_15_ap_2_1.pdf',
          'sha256': '47dcfb8cc2103ea1f885c32537f436542aa8a8a41eeb0db1d50a14f0c404a8ac'}
INE564 = {'tx': 'INE, Acuerdo INE/CG564/2025: declaración de validez de la elección de la SCJN; considerando 25, cargos a elegir en 2025 (15-06-2025)',
          'url': 'https://dof.gob.mx/2025/INE/CGext202506_15_ap_2_2.pdf',
          'sha256': '3271e1d79a96349ea654d717f6156c29d3e0e200e6003643cf4244f8f5769ade'}
LAMP = {'tx': 'Ley de Amparo, Reglamentaria de los artículos 103 y 107 de la Constitución, texto vigente (Cámara de Diputados, última reforma DOF 16-10-2025)',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LAmp.pdf',
        'sha256': '05560493ac2b17b9e77eeb9741843176ee0fde76f05e75f853465b13621be78d'}
TRANS = 'Transitorios de la reforma judicial (DOF 15-09-2024), en el texto vigente de la Constitución'

# Las nueve personas que asignó el INE (acuerdo INE/CG563/2025, punto
# SEGUNDO), con los votos que les reconoció tras quitar las casillas con
# inconsistencias (considerando 297). Orden: el del propio acuerdo.
MINISTROS = [('Hugo Aguilar Ortiz', 5900789, 'H'), ('Lenia Batres Guadarrama', 5534681, 'M'),
             ('Yasmín Esquivel Mossa', 4985925, 'M'), ('Loretta Ortiz Ahlf', 4736571, 'M'),
             ('María Estela Ríos González', 4440634, 'M'), ('Giovanni Azael Figueroa Mejía', 3411191, 'H'),
             ('Irving Espinosa Betanzo', 3354485, 'H'), ('Arístides Rodrigo Guerrero García', 3278988, 'H'),
             ('Sara Irene Herrerías Guerra', 3053788, 'M')]

# INE/CG564/2025, considerando 25: los cargos de 2025 (mujeres, hombres).
CARGOS2025 = [('Ministras y ministros de la Suprema Corte', 'Todo el país', 5, 4),
              ('Tribunal de Disciplina Judicial', 'Todo el país', 3, 2),
              ('Sala Superior del Tribunal Electoral', 'Todo el país', 1, 1),
              ('Salas Regionales del Tribunal Electoral', '5 circunscripciones', 10, 5),
              ('Magistraturas de Tribunal Colegiado de Circuito', '32 circuitos', 318, 84),
              ('Magistraturas de Tribunal Colegiado de Apelación', '32 circuitos', 49, 13),
              ('Juezas y jueces de Distrito', '32 circuitos', 268, 118)]
CARGOS2025_TOTAL = 881

# Manual de remuneraciones del PJF 2026, anexo B: sueldos y salarios
# mensuales netos (página del DOF). Son tabulador, no recibo de nómina.
SUELDOS = [('Ministra o ministro de la Suprema Corte', 134310, 'p. 8'),
           ('Magistratura del Tribunal de Disciplina Judicial', 133310, 'p. 11'),
           ('Magistratura de la Sala Superior del Tribunal Electoral', 133310, 'p. 24'),
           ('Integrante del Pleno del Órgano de Administración Judicial', 131310, 'p. 16'),
           ('Magistratura de Circuito', 129310, 'p. 16'),
           ('Magistratura de Sala Regional del Tribunal Electoral', 129310, 'p. 24'),
           ('Jueza o juez de Distrito', 126310, 'p. 16')]
PRESIDENTA = 134290  # PEF 2026, Anexo 23.1.2: remuneración ordinaria neta mensual (la misma cifra de «Tú contra ellos»)

# Las páginas de Datos: (archivo, icono, título, frase, entrada, temas).
PORTADA = 'datos-poder-judicial.html'
PORTADA_TIT = 'Poder Judicial'
PAGINAS = [
    ('datos-judicial-estructura.html', '🗺️', 'Quién es quién y los 32 circuitos',
     'Los órganos, quién administra, quién sanciona y el mapa de circuitos',
     'Quién forma el Poder Judicial de la Federación desde la reforma de 2024, quién lo administra, quién sanciona a sus juezas y jueces '
     'y cómo se reparte el país en 32 circuitos judiciales.',
     ['estructura', 'circuitos', 'oaj', 'disciplina', 'tepjf']),
    ('datos-judicial-suprema-corte.html', '⚖️', 'La Suprema Corte', 'Sus nueve integrantes, quién la preside y cuánto dura el cargo',
     'Cómo está integrada la Suprema Corte de Justicia de la Nación, quiénes la forman desde el 1 de septiembre de 2025, '
     'con cuántos votos llegaron y qué se necesita para ser ministra o ministro.',
     ['corte', 'ministros', 'requisitos']),
    ('datos-judicial-sueldos.html', '💵', 'Sueldos y el tope del 127', 'Lo que dice el tabulador de cada cargo y el límite de la Presidenta',
     'Cuánto dice el tabulador oficial que gana cada cargo del Poder Judicial, comparado con el tope del artículo 127: nadie puede ganar más que la Presidenta.',
     ['sueldos', 'retiro']),
    ('datos-judicial-presupuesto.html', '🏦', 'El presupuesto', 'Cuánto se le aprobó, en qué se va y qué pasó con los fideicomisos',
     'Cuánto dinero le aprobó la Cámara de Diputados al Poder Judicial para 2026, cómo se reparte entre sus cinco unidades, en qué se va '
     'y cuánto lleva gastado la Corte. Con lo que todavía no se sabe.',
     ['presupuesto', 'scjn_gasto', 'fideicomisos']),
    ('datos-judicial-eleccion.html', '🗳️', 'La elección judicial', 'Los 881 cargos de 2025 y la segunda elección, en 2028',
     'Cómo se eligen las juezas, los jueces, las magistraturas y la Corte: lo que se votó el 1 de junio de 2025 y lo que falta por votar en 2028.',
     ['eleccion2025', 'eleccion2028']),
    ('datos-judicial-como-decide.html', '🧭', 'Cómo decide un juez', 'El amparo y sus recursos, cuándo llega un caso a la Corte y la jurisprudencia',
     'Los cuatro caminos para defender la Constitución, por dónde pasa un juicio de amparo y qué recursos proceden, cuándo llega un caso '
     'a la Suprema Corte y cuándo lo que decide obliga a todos los tribunales del país.',
     ['medios', 'amparo', 'recursos', 'controversias', 'llegar_corte', 'jurisprudencia', 'plazos']),
    # La auditoría de gestión (pedido del autor, 27-10-2026): el dinero junto a
    # lo que se resolvió con él. Cifras y tablas en gestion_judicial.py.
    (gestion_judicial.PAGINA, '📊', 'Lo que cuesta y lo que resuelve', 'Asuntos resueltos, rezago y cuánto tarda, junto al dinero',
     'Que las cuentas cuadren no dice si la justicia llega. Aquí el presupuesto de cada órgano va junto a cuántos asuntos le llegaron, cuántos resolvió, '
     'cuántos se le acumulan y cuánto tarda, con el censo del INEGI. Y lo que nadie ha publicado, con su ficha en el Registro de pendientes.',
     gestion_judicial.TEMAS),
]
PAGINA_DE = {k: (p[0], p[2]) for p in PAGINAS for k in p[5]}


def _o(que, fu, op=None, e=None):
    d = {'que': que, 'e': e or ('derivado' if op else 'oficial'), 'fu': fu}
    if op:
        d['op'] = op
    return d


def _n(v):
    return format(int(round(v)), ',')


def _mdp(v):
    return '$%s millones' % format(round(v / 1e6, 1), ',.1f')


def _fuentes_base(d):
    return {k: {'tx': v['doc'] if v.get('doc') else v['corto'], 'url': v['url']} for k, v in d['poderes']['fuentes'].items()}


def judicial(d):
    """Los temas del bot. `d` es window.AUDIT_DB."""
    F = _fuentes_base(d)
    po = d['poderes']
    r03 = po['ramos2026']['judicial']
    ur = {u['id']: u for u in r03['unidades']}
    caps = po['judicial']['capitulosPorUR']['RAMO03']
    c1000 = next(c for c in caps if c['cap'] == '1000')['aprobado']
    ago = po['judicial']['scjnAgosto']
    assert sum(u['aprobado'] for u in r03['unidades']) == r03['aprobado'] == sum(c['aprobado'] for c in caps)
    assert sum(m + h for _, _, m, h in CARGOS2025) == CARGOS2025_TOTAL and len(MINISTROS) == 9
    assert len(po['judicial']['circuitos']) == 32
    pct = lambda a, b: format(round(100 * a / b, 1), '.1f')
    MAN = F['MANUAL']
    t = {}
    t['estructura'] = {
        'tit': 'Quién forma el Poder Judicial de la Federación',
        'h': '<p>Desde la reforma de 2024, el Poder Judicial de la Federación lo forman la <b>Suprema Corte</b> (9 integrantes), el <b>Tribunal Electoral</b>, '
             'los <b>Plenos Regionales</b>, los <b>Tribunales Colegiados de Circuito</b>, los <b>Tribunales Colegiados de Apelación</b> y los <b>Juzgados de Distrito</b>.</p>'
             '<p>Dos órganos nuevos sustituyeron al Consejo de la Judicatura Federal, que desapareció el <b>1 de septiembre de 2025</b>:</p><ul class="pa-lista">'
             '<li>el <b>Órgano de Administración Judicial</b>, que administra el dinero, el personal y los circuitos, y</li>'
             '<li>el <b>Tribunal de Disciplina Judicial</b>, que investiga y sanciona a juezas, jueces y personal.</li></ul>',
        'fu': [_o('Quién ejerce el Poder Judicial y quién lo administra y disciplina (art. 94)', CPEUM),
               _o('El Consejo de la Judicatura se extinguió cuando tomó protesta el Tribunal de Disciplina, el 1 de septiembre de 2025 (transitorios segundo y sexto)', {'tx': TRANS, 'url': CPEUM['url']})],
        'ci': [{'v': '9', 'etq': 'integrantes de la Suprema Corte', 'e': 'oficial'}],
        'sug': ['¿Quién preside la Suprema Corte?', '¿Cuántos circuitos judiciales hay?', '¿Qué es el Tribunal de Disciplina Judicial?']}
    t['circuitos'] = {
        'tit': 'Los 32 circuitos judiciales',
        'h': '<p>Para impartir justicia federal, el país se divide en <b>32 circuitos judiciales</b>. Cada uno tiene sus tribunales colegiados y sus juzgados de distrito, '
             'y en la elección judicial cada circuito vota por los suyos. Cuántos circuitos hay, dónde y de qué materia es cada tribunal lo decide el <b>Órgano de Administración Judicial</b>.</p>'
             '<p>Entre abril y junio de 2026, las oficinas que el propio Órgano llama «Circuito Judicial» registraron pagos por <b>%s</b>. '
             '<b>No es lo que cuesta un circuito</b>: la nómina, que es la mayor parte del gasto, se paga desde oficinas centrales y no se reparte por circuito. '
             'El costo completo de cada circuito está pendiente.</p>' % _mdp(sum(c['pagado'] for c in po['judicial']['circuitos'])),
        'fu': [_o('Los 881 cargos de 2025 se eligieron en 32 circuitos judiciales (considerando 25)', INE564),
               _o('El Órgano de Administración Judicial decide número, división en circuitos y materias (arts. 94 y 100)', CPEUM),
               _o('Pagos de las unidades «Circuito Judicial», abril a junio de 2026', F['OAJ_UEG'], 'suma de las unidades que la fuente nombra «Circuito Judicial»'),
               {'que': 'Costo completo de cada circuito', 'e': 'pendiente', 'p': 'poderes-judicial-0', 'fu': F['OAJ_UEG']}],
        'ci': [{'v': '32', 'etq': 'circuitos judiciales', 'e': 'oficial'}],
        'sug': ['¿Quién forma el Poder Judicial?', '¿Cuánto cuesta el Poder Judicial?', '¿Cuántos cargos se votaron en la elección judicial?']}
    t['oaj'] = {
        'tit': 'El Órgano de Administración Judicial',
        'h': '<p>El <b>Órgano de Administración Judicial</b> maneja el dinero, el personal y la carrera judicial; decide cuántos tribunales y juzgados hay y en qué circuito, '
             'y <b>elabora el presupuesto</b> de todo el Poder Judicial.</p>'
             '<p>Lo dirige un Pleno de <b>5 personas</b> que duran <b>seis años</b>: 1 la nombra la Presidencia de la República, 1 el Senado (con dos terceras partes de los votos) '
             'y 3 la Suprema Corte (con seis votos). Su presidencia rota cada dos años.</p>'
             '<p>Es, por mucho, la unidad con más dinero: para 2026 le aprobaron <b>%s</b>, el <b>%s %%</b> de todo el Poder Judicial.</p>' % (
                 _mdp(ur['oaj']['aprobado']), pct(ur['oaj']['aprobado'], r03['aprobado'])),
        'fu': [_o('Atribuciones e integración del Órgano de Administración Judicial (art. 100)', CPEUM),
               _o('Presupuesto aprobado 2026 del Órgano (UR 120)', F['PEF']),
               _o('Su parte del Ramo 03', F['PEF'], '%s ÷ %s × 100' % (_mdp(ur['oaj']['aprobado']), _mdp(r03['aprobado'])))],
        'ci': [{'v': '5', 'etq': 'integrantes de su Pleno', 'e': 'oficial'}, {'v': _mdp(ur['oaj']['aprobado']), 'etq': 'aprobado 2026', 'e': 'oficial'}],
        'sug': ['¿Cuánto cuesta el Poder Judicial?', '¿Qué es el Tribunal de Disciplina Judicial?']}
    t['disciplina'] = {
        'tit': 'El Tribunal de Disciplina Judicial',
        'h': '<p>El <b>Tribunal de Disciplina Judicial</b> investiga y sanciona a quien trabaja en el Poder Judicial de la Federación, <b>incluidos ministros, magistrados y jueces</b>. '
             '<b>Cualquier persona puede denunciar</b> ante él una conducta indebida.</p>'
             '<p>Lo forman <b>5 magistraturas</b> electas por voto en todo el país; duran <b>seis años</b>, se renuevan de forma escalonada y no pueden reelegirse. '
             'Resuelve en Pleno, por mayoría de cuatro votos, o en comisiones de tres. Para 2026 le aprobaron <b>%s</b>.</p>' % _mdp(ur['tdj']['aprobado']),
        'fu': [_o('Integración y funcionamiento (art. 100) y denuncia ciudadana (art. 97)', CPEUM), _o('Presupuesto aprobado 2026 (UR 300)', F['PEF'])],
        'ci': [{'v': '5', 'etq': 'magistraturas', 'e': 'oficial'}, {'v': _mdp(ur['tdj']['aprobado']), 'etq': 'aprobado 2026', 'e': 'oficial'}],
        'sug': ['¿Cómo denuncio a un juez?', '¿Quién forma el Poder Judicial?']}
    t['tepjf'] = {
        'tit': 'El Tribunal Electoral',
        'h': '<p>El <b>Tribunal Electoral del Poder Judicial de la Federación</b> resuelve los pleitos de las elecciones. Su <b>Sala Superior</b> tiene <b>7 magistraturas</b> '
             'y además hay <b>salas regionales</b>, una por circunscripción. Sus integrantes se eligen por voto y duran <b>seis años improrrogables</b>.</p>'
             '<p>En 2025 se eligieron 2 lugares vacantes de la Sala Superior y las 15 magistraturas regionales; las otras cinco de la Sala Superior siguen hasta que se elijan en <b>2028</b>. '
             'Para 2026 le aprobaron <b>%s</b>.</p>' % _mdp(ur['tepjf']['aprobado']),
        'fu': [_o('Integración del Tribunal Electoral (art. 99)', CPEUM), _o('Cargos del Tribunal Electoral elegidos en 2025 (considerando 25)', INE564),
               _o('Las magistraturas en funciones de la Sala Superior siguen hasta 2028 (transitorio cuarto, reformado DOF 02-06-2026)', {'tx': TRANS, 'url': CPEUM['url']}),
               _o('Presupuesto aprobado 2026 (UR 210 y 211)', F['PEF'])],
        'ci': [{'v': '7', 'etq': 'magistraturas de la Sala Superior', 'e': 'oficial'}],
        'sug': ['¿Cuándo es la elección judicial?', '¿Quién forma el Poder Judicial?']}
    t['corte'] = {
        'tit': 'La Suprema Corte de Justicia de la Nación',
        'h': '<p>La Suprema Corte tiene <b>9 ministras y ministros</b>, electos por voto en todo el país. Ya no tiene salas: <b>trabaja en Pleno</b> y, si el Pleno lo aprueba, '
             'puede dividirse en dos secciones. Sus sesiones son públicas.</p>'
             '<ul class="pa-lista"><li>Cada ministra o ministro dura <b>12 años</b> y no puede volver a ser electo.</li>'
             '<li>La <b>presidencia</b> cambia cada <b>dos años</b>: le toca a quien sacó más votos. Por eso la preside <b>Hugo Aguilar Ortiz</b>, el más votado de 2025 '
             '(5,900,789 votos), desde el 1 de septiembre de 2025.</li>'
             '<li>Su sueldo no puede ser mayor que el de la Presidenta de la República.</li></ul>'
             '<p>Para 2026 le aprobaron <b>%s</b>.</p>' % _mdp(ur['scjn']['aprobado']),
        'fu': [_o('Integración, presidencia rotatoria, secciones, duración y tope de sueldo (art. 94, reformado DOF 02-06-2026)', CPEUM),
               _o('Hugo Aguilar Ortiz preside por ser el más votado', INE563, 'el art. 94 da la presidencia a la mayor votación; el acuerdo le reconoce 5,900,789 votos, la cifra más alta'),
               _o('Toma de protesta el 1 de septiembre de 2025 (transitorio segundo)', {'tx': TRANS, 'url': CPEUM['url']}),
               _o('Presupuesto aprobado 2026 (UR 100)', F['PEF'])],
        'ci': [{'v': '9', 'etq': 'ministras y ministros', 'e': 'oficial'}, {'v': '12 años', 'etq': 'duración del cargo', 'e': 'oficial'}],
        'sug': ['¿Quiénes son los ministros de la Corte?', '¿Cuánto gana un ministro de la Corte?', '¿Qué se necesita para ser ministro?'],
        # Lo primero que se lee cuando la pregunta es quién la preside.
        'lider': '<p>La Suprema Corte la preside <b>Hugo Aguilar Ortiz</b> desde el 1 de septiembre de 2025: fue el más votado de la elección de ese año.</p>'}
    t['ministros'] = {
        'tit': 'Las nueve ministras y ministros',
        'h': '<p>Las <b>9 personas</b> que integran la Suprema Corte desde el 1 de septiembre de 2025, con los votos que les reconoció el INE. '
             'Se asignaron alternando mujeres y hombres para que la Corte fuera paritaria: <b>5 ministras y 4 ministros</b>.</p><ol class="pa-lista">%s</ol>'
             '<p class="pa-chico">Lenia Batres, Yasmín Esquivel y Loretta Ortiz ya eran ministras y fueron reelectas; '
             'su periodo sigue reglas propias (transitorio tercero), así que no publicamos una fecha de salida por persona.</p>' % ''.join(
                 '<li><b>%s</b>: %s votos</li>' % (html.escape(n), _n(v)) for n, v, _ in MINISTROS),
        'fu': [_o('Asignación y votos de cada persona (punto segundo y considerando 297)', INE563),
               _o('Duración de los periodos de quienes ya eran ministras (transitorio tercero)', {'tx': TRANS, 'url': CPEUM['url']})],
        'ci': [{'v': '5 + 4', 'etq': 'ministras + ministros', 'e': 'oficial'}],
        'sug': ['¿Quién preside la Suprema Corte?', '¿Cuánto gana un ministro de la Corte?']}
    t['requisitos'] = {
        'tit': 'Qué se necesita para ser ministra o ministro',
        'h': '<ul class="pa-lista"><li>Ser mexicana o mexicano <b>por nacimiento</b>, con plenos derechos.</li>'
             '<li>Título de <b>licenciatura en derecho</b>, con promedio de al menos <b>8</b> en la carrera y de <b>9</b> en las materias del cargo, y <b>cinco años</b> de práctica profesional.</li>'
             '<li>Buena reputación y no haber sido condenado por delito con pena de más de un año de prisión (o por robo, fraude o falsificación, con cualquier pena).</li>'
             '<li>Haber vivido en el país los <b>dos años</b> anteriores a la convocatoria.</li>'
             '<li>No haber sido, el año anterior, secretaria o secretario de Estado, fiscal general, senador, diputado federal ni gobernador.</li></ul>'
             '<p>Cada Poder de la Unión postula candidaturas tras evaluarlas en un comité de cinco juristas; el Senado junta las listas y el INE organiza la votación.</p>',
        'fu': [_o('Requisitos (art. 95) y procedimiento de postulación (art. 96)', CPEUM)],
        'sug': ['¿Quiénes son los ministros de la Corte?', '¿Cuándo es la elección judicial?']}
    filas = ''.join('<li><b>%s</b>: $%s al mes</li>' % (html.escape(n), _n(v)) for n, v, _ in SUELDOS)
    t['sueldos'] = {
        'tit': 'Cuánto gana cada cargo del Poder Judicial',
        'h': '<p>Lo que dice el tabulador oficial de 2026, en <b>pesos netos al mes</b> (ya sin impuestos):</p><ul class="pa-lista">%s</ul>'
             '<p>La Constitución manda que <b>nadie gane más que la Presidenta</b>, cuyo límite neto es de <b>$%s</b> al mes. '
             '<b>Ojo:</b> el tabulador de una ministra o un ministro queda <b>$%s arriba</b> de esa cifra. Las dos salen de documentos oficiales distintos y la plataforma '
             'no ha podido cotejar si miden exactamente lo mismo, así que lo anotamos tal cual, sin llamarlo violación.</p>'
             '<p class="pa-chico">El tabulador es un límite, no el recibo de nómina de cada persona.</p>' % (filas, _n(PRESIDENTA), _n(SUELDOS[0][1] - PRESIDENTA)),
        'fu': [_o('Sueldos y salarios mensuales netos, anexo B (pp. 8, 11, 16 y 24)', MAN),
               _o('Tope: nadie gana más que la Presidencia (arts. 94 y 127)', CPEUM),
               _o('Límite neto de la Presidenta (Anexo 23.1.2)', F['PEF']),
               _o('Diferencia entre el tabulador de la Corte y el límite de la Presidenta', MAN, '$%s − $%s' % (_n(SUELDOS[0][1]), _n(PRESIDENTA)))],
        'ci': [{'v': '$%s' % _n(SUELDOS[0][1]), 'etq': 'neto al mes, ministra o ministro', 'e': 'oficial'},
               {'v': '$%s' % _n(SUELDOS[0][1] - PRESIDENTA), 'etq': 'arriba del límite de la Presidenta', 'e': 'derivado', 'op': '$%s − $%s' % (_n(SUELDOS[0][1]), _n(PRESIDENTA))}],
        'ir': ['herramienta-calculadora-compara.html', 'Tú contra ellos'],
        'sug': ['¿Cuánto gana un juez de distrito?', '¿Cuánto gana la presidenta?', '¿Qué pasó con el haber de retiro?']}
    t['retiro'] = {
        'tit': 'El haber de retiro y las liquidaciones',
        'h': '<p>La reforma de 2024 bajó los sueldos de todo el Poder Judicial al tope del artículo 127 y quitó el <b>haber de retiro</b> (la pensión vitalicia) a las ministras y ministros '
             'que se fueron por no postularse o no ganar en 2025. Solo lo conservó, proporcional a sus años, quien renunció antes de que cerrara la convocatoria.</p>'
             '<p>Las juezas, jueces y magistraturas que dejaron el cargo por no ser electos reciben <b>tres meses de salario integrado</b> y <b>veinte días por año</b> trabajado, además de sus otras prestaciones.</p>',
        'fu': [_o('Sueldos al tope y haber de retiro (transitorio séptimo)', {'tx': TRANS, 'url': CPEUM['url']}),
               _o('Liquidación de quienes no fueron electos (transitorio décimo)', {'tx': TRANS, 'url': CPEUM['url']})],
        'sug': ['¿Cuánto gana un ministro de la Corte?', '¿Qué pasó con los fideicomisos del Poder Judicial?']}
    t['presupuesto'] = {
        'tit': 'Cuánto cuesta el Poder Judicial',
        'h': '<p>Para 2026, la Cámara de Diputados le aprobó al Poder Judicial de la Federación <b>%s</b>. Es menos de lo que pidió: su proyecto era de %s, '
             'así que le recortaron <b>%s</b>.</p><ul class="pa-lista">'
             '<li><b>Órgano de Administración Judicial:</b> %s</li><li><b>Suprema Corte:</b> %s</li><li><b>Tribunal Electoral:</b> %s</li>'
             '<li><b>Tribunal de Disciplina Judicial:</b> %s</li></ul>'
             '<p>El <b>%s %%</b> se va en <b>servicios personales</b>: sueldos, prestaciones y cuotas.</p>' % (
                 _mdp(r03['aprobado']), _mdp(r03['proyecto']), _mdp(r03['proyecto'] - r03['aprobado']),
                 _mdp(ur['oaj']['aprobado']), _mdp(ur['scjn']['aprobado']), _mdp(ur['tepjf']['aprobado']), _mdp(ur['tdj']['aprobado']),
                 pct(c1000, r03['aprobado'])),
        'fu': [_o('Ramo 03 aprobado y por unidad (Anexo 1; proyecto y recorte, Anexo 32)', F['PEF']),
               _o('Recorte al proyecto', F['PEF'], '%s − %s' % (_mdp(r03['proyecto']), _mdp(r03['aprobado']))),
               _o('Capítulo 1000, servicios personales', F['COG'], '%s ÷ %s × 100' % (_mdp(c1000), _mdp(r03['aprobado'])))],
        'ci': [{'v': _mdp(r03['aprobado']), 'etq': 'aprobado 2026, Ramo 03', 'e': 'oficial'},
               {'v': '%s %%' % pct(c1000, r03['aprobado']), 'etq': 'en sueldos y prestaciones', 'e': 'derivado'}],
        'ir': ['numeros-lo-que-cuestan-los-poderes.html', 'Lo que cuestan el Congreso y la Judicatura'],
        'sug': ['¿Cuánto lleva gastado la Corte este año?', '¿Cuánto gana un ministro de la Corte?', '¿Qué pasó con los fideicomisos del Poder Judicial?']}
    t['scjn_gasto'] = {
        'tit': 'Cuánto lleva gastado la Suprema Corte',
        'h': '<p>Al <b>31 de agosto de 2026</b>, la Suprema Corte tenía un presupuesto modificado de <b>%s</b>. De eso había <b>ejercido %s</b> (el %s %%), '
             'tenía %s comprometidos y %s disponibles.</p>'
             '<p class="pa-chico">«Ejercido» es la palabra de la Corte; no es lo mismo que «pagado». Lo disponible tampoco es ahorro: el año aún no termina.</p>' % (
                 _mdp(ago['modificado']), _mdp(ago['ejercido']), pct(ago['ejercido'], ago['modificado']), _mdp(ago['compromiso']), _mdp(ago['disponible'])),
        'fu': [_o('Estado del ejercicio al 31 de agosto de 2026', F['SCJN_AGO']),
               _o('Avance', F['SCJN_AGO'], '%s ÷ %s × 100' % (_mdp(ago['ejercido']), _mdp(ago['modificado'])))],
        'ci': [{'v': '%s %%' % pct(ago['ejercido'], ago['modificado']), 'etq': 'ejercido al 31 de agosto', 'e': 'derivado'}],
        'ir': ['numeros-lo-que-cuestan-los-poderes.html', 'Lo que cuestan el Congreso y la Judicatura'],
        'sug': ['¿Cuánto cuesta el Poder Judicial?', '¿Quién preside la Suprema Corte?']}
    t['fideicomisos'] = {
        'tit': 'Qué pasó con los fideicomisos del Poder Judicial',
        'h': '<p>La reforma de 2024 ordenó <b>extinguir</b> los fondos y fideicomisos del Poder Judicial que no estuvieran previstos en una ley, y devolver lo que tuvieran a la '
             '<b>Tesorería de la Federación</b> en un máximo de <b>90 días</b>. Desde entonces la Constitución prohíbe crear otros.</p>'
             '<p>Las pensiones complementarias, los apoyos médicos y demás obligaciones laborales que pagaban se deben cubrir con el presupuesto de cada año.</p>'
             '<p><b>Cuánto dinero se devolvió</b> todavía no lo hemos cotejado con un documento oficial. Las cifras que circulan no aparecen en el decreto.</p>',
        'fu': [_o('Extinción y entero a la Tesorería (transitorio décimo)', {'tx': TRANS, 'url': CPEUM['url']}),
               _o('Prohibición de nuevos fideicomisos (art. 100, último párrafo)', CPEUM),
               {'que': 'Cuánto se devolvió a la Tesorería', 'e': 'pendiente', 'p': 'judicial-fideicomisos-monto',
                'fu': {'tx': 'Tesorería de la Federación, informes', 'url': 'https://www.gob.mx/tesofe'}}],
        'sug': ['¿Cuánto cuesta el Poder Judicial?', '¿Qué pasó con el haber de retiro?']}
    cargos = ''.join('<li><b>%s</b> (%s): %d</li>' % (html.escape(c), html.escape(a), m + h) for c, a, m, h in CARGOS2025)
    t['eleccion2025'] = {
        'tit': 'La elección judicial de 2025',
        'h': '<p>El <b>domingo 1 de junio de 2025</b> se votó por primera vez a juezas, jueces y ministros. Se eligieron <b>881 cargos</b> (654 para mujeres y 227 para hombres):</p>'
             '<ul class="pa-lista">%s</ul>'
             '<p>Las campañas duraron 60 días, sin precampañas y <b>sin dinero público ni privado</b>; los partidos no podían hacer proselitismo. Las personas electas tomaron protesta el '
             '<b>1 de septiembre de 2025</b>.</p>'
             '<p>Lo que todavía no tenemos cotejado: la <b>participación</b> final y <b>cuánto costó</b>. Para organizarla, el INE aprobó un presupuesto precautorio de '
             '$13,205.1 millones, que incluía una eventual consulta popular; no es lo que se gastó.</p>' % cargos,
        'fu': [_o('Cargos a elegir en 2025 (considerando 25)', INE564),
               _o('Jornada el primer domingo de junio de 2025 y protesta el 1 de septiembre (transitorio segundo)', {'tx': TRANS, 'url': CPEUM['url']}, 'el primer domingo de junio de 2025 cayó en día 1'),
               _o('Campañas sin financiamiento ni precampañas (art. 96)', CPEUM),
               _o('Presupuesto precautorio del INE, acuerdo INE/CG2321/2024 (antecedente XIV)', INE563),
               {'que': 'Participación ciudadana final', 'e': 'pendiente', 'p': 'judicial-2025-participacion', 'fu': {'tx': 'INE, cómputos distritales', 'url': 'https://www.ine.mx/voto-y-elecciones/computos-distritales/'}},
               {'que': 'Cuánto costó al final', 'e': 'pendiente', 'p': 'judicial-2025-costo', 'fu': {'tx': 'INE, transparencia', 'url': 'https://www.ine.mx/transparencia/'}}],
        'ci': [{'v': '881', 'etq': 'cargos elegidos en 2025', 'e': 'oficial'}, {'v': '1 de junio de 2025', 'etq': 'jornada', 'e': 'derivado'}],
        'sug': ['¿Cuándo es la próxima elección judicial?', '¿Quiénes son los ministros de la Corte?', '¿Cuántos circuitos judiciales hay?']}
    t['eleccion2028'] = {
        'tit': 'La segunda elección judicial: junio de 2028',
        'h': '<p>La segunda elección judicial <b>ya no será en 2027</b>: la reforma publicada el <b>2 de junio de 2026</b> la movió al <b>primer domingo de junio de 2028</b>. Ese día se votará:</p>'
             '<ul class="pa-lista"><li>la <b>otra mitad</b> de las magistraturas de circuito y de los juzgados de distrito, que no se renovó en 2025;</li>'
             '<li>las cinco magistraturas de la <b>Sala Superior</b> del Tribunal Electoral que siguen en funciones, y</li>'
             '<li>lo que falte de los <b>poderes judiciales de los estados</b>, que deben terminar de renovarse ese año.</li></ul>'
             '<p>Quienes debían dejar el cargo en 2027 siguen hasta que tomen protesta los electos, el <b>1 de septiembre de 2028</b>.</p>',
        'fu': [_o('Elección judicial en 2028 (decreto DOF 02-06-2026; transitorios segundo, cuarto y octavo reformados)', CPEUM)],
        'sug': ['¿Cuántos cargos se votaron en la elección judicial?', '¿Cuándo son las próximas elecciones?']}
    # Rescatados de la Enciclopedia antigua (pedido del autor, 24-10-2026):
    # «los cuatro instrumentos», «los recursos» y «cuándo llega un caso a la
    # Corte». Solo el tema: cada línea se cotejó contra la Constitución y la
    # Ley de Amparo vigentes.
    t['medios'] = {
        'tit': 'Los cuatro caminos para defender la Constitución',
        'h': '<p>Hay cuatro caminos para que un tribunal diga que una ley o un acto viola la Constitución. <b>No todos los puede usar cualquiera:</b></p><ul class="pa-lista">'
             '<li><b>Juicio de amparo:</b> lo promueves tú, si una autoridad viola tus derechos. Si ganas, te protege <b>solo a ti</b>. Lo resuelven juzgados y tribunales federales y, a veces, la Corte.</li>'
             '<li><b>Controversia constitucional:</b> es un pleito <b>entre autoridades</b> (la Federación, un estado, un municipio, un poder contra otro). Solo la resuelve la Corte.</li>'
             '<li><b>Acción de inconstitucionalidad:</b> ataca una ley <b>en abstracto</b>, sin un caso concreto. La presentan, entre otros, legisladores, partidos, comisiones de derechos humanos o la Fiscalía, '
             'dentro de los <b>30 días naturales</b> siguientes a que se publica la ley. Solo la resuelve la Corte.</li>'
             '<li><b>Declaratoria general de inconstitucionalidad:</b> convierte amparos repetidos en una regla <b>para todos</b>: si en <b>90 días</b> no se corrige la ley, la Corte la declara inválida con seis votos. No aplica a impuestos.</li></ul>',
        'fu': [_o('Amparo: quién lo promueve y para quién vale (arts. 103 y 107, frs. I y II)', CPEUM),
               _o('Controversias constitucionales y acciones de inconstitucionalidad, con su plazo de 30 días naturales (art. 105, frs. I y II)', CPEUM),
               _o('Declaratoria general de inconstitucionalidad: 90 días, seis votos y excepción de impuestos (art. 107, fr. II)', CPEUM)],
        'sug': ['¿Qué recursos hay en el amparo?', '¿Cuándo llega un caso a la Suprema Corte?', '¿Qué es el amparo?']}
    t['recursos'] = {
        'tit': 'Los recursos del amparo: qué procede contra qué',
        'h': '<p>En el amparo <b>no hay apelación</b>. La Ley de Amparo solo admite <b>cuatro recursos</b>, cada uno con su plazo:</p><ul class="pa-lista">'
             '<li><b>Revisión (10 días):</b> contra la sentencia del juzgado en el amparo indirecto, lo que decide sobre la suspensión definitiva o el sobreseimiento. '
             'En el amparo directo, solo si hay un tema de constitucionalidad que la Corte considere de interés excepcional.</li>'
             '<li><b>Queja (5 días):</b> contra lo que admite o desecha la demanda, la suspensión provisional y otras decisiones del trámite. Son <b>2 días hábiles</b> si se trata de la suspensión '
             'provisional o de plano, y se puede presentar <b>en cualquier tiempo</b> si la autoridad no tramita la demanda.</li>'
             '<li><b>Reclamación (3 días):</b> contra los acuerdos de trámite de quien preside la Corte o un tribunal colegiado. Se resuelve en un máximo de <b>10 días</b>.</li>'
             '<li><b>Inconformidad (15 días):</b> ya en el cumplimiento, contra lo que da por cumplida la sentencia, dice que no se puede cumplir o desecha la denuncia de que la autoridad repitió el acto. '
             'Si está en juego la vida, la libertad o una desaparición forzada, se presenta <b>en cualquier tiempo</b>.</li></ul>'
             '<p class="pa-chico">Esto es para que entiendas el camino, no es asesoría legal: un caso concreto lo revisa una abogada o un abogado.</p>',
        'fu': [_o('Solo revisión, queja, reclamación e inconformidad (art. 80)', LAMP),
               _o('Revisión: contra qué procede y su plazo de diez días (arts. 81 y 86)', LAMP),
               _o('Queja: contra qué procede y sus plazos de cinco días, dos días hábiles o en cualquier tiempo (arts. 97 y 98)', LAMP),
               _o('Reclamación: tres días para presentarla y diez para resolverla (arts. 104 y 105)', LAMP),
               _o('Inconformidad: contra qué procede y su plazo de quince días (arts. 201 y 202)', LAMP)],
        'sug': ['¿Cuándo llega un caso a la Suprema Corte?', '¿Qué es el amparo?']}
    t['llegar_corte'] = {
        'tit': '¿Cuándo llega un caso a la Suprema Corte?',
        'h': '<p>La Corte <b>no revisa todo</b> lo que se litiga en el país. La Constitución le abre estas puertas:</p><ul class="pa-lista">'
             '<li><b>Directo a la Corte:</b> las controversias constitucionales y las acciones de inconstitucionalidad.</li>'
             '<li><b>Amparo en revisión:</b> cuando, contra la sentencia de un juzgado de distrito o un tribunal colegiado de apelación, sigue en juego si una ley es inconstitucional.</li>'
             '<li><b>Amparo directo en revisión:</b> solo si el caso tiene un tema constitucional y la Corte decide que es de <b>interés excepcional</b>. Si lo desecha, ya no hay recurso.</li>'
             '<li><b>Atracción:</b> la Corte puede quedarse, por su cuenta o a petición, con un amparo o una apelación que por su interés y trascendencia lo amerite.</li>'
             '<li><b>Contradicción de criterios:</b> si los Plenos Regionales resuelven distinto, la Corte decide qué criterio vale. Eso fija jurisprudencia, pero no cambia los casos ya resueltos.</li></ul>'
             '<p>En todo lo demás, la última palabra es de un <b>tribunal colegiado</b>: sus sentencias de revisión no admiten recurso.</p>',
        'fu': [_o('Controversias, acciones y apelaciones atraídas (art. 105, frs. I a III)', CPEUM),
               _o('Amparo en revisión, amparo directo en revisión, atracción y contradicción de criterios (art. 107, frs. V, VIII, IX y XIII)', CPEUM),
               _o('Competencia de la Corte y de los tribunales colegiados en la revisión (arts. 83 y 84)', LAMP)],
        'sug': ['¿Qué recursos hay en el amparo?', '¿Qué es la jurisprudencia?']}
    t['amparo'] = {
        'tit': 'El juicio de amparo, paso a paso',
        'h': '<p>El <b>amparo</b> es el juicio con el que te defiendes cuando una ley, un acto o una omisión de una autoridad viola tus derechos. Lo promueve la persona afectada, '
             'y si gana, la sentencia <b>la protege solo a ella</b>: no anula la ley para todos. No procede contra reformas a la Constitución.</p><ul class="pa-lista">'
             '<li><b>Amparo indirecto:</b> contra leyes, actos de autoridades administrativas o actos dentro o fuera de un juicio. Se presenta ante un <b>Juzgado de Distrito</b>.</li>'
             '<li><b>Amparo directo:</b> contra la sentencia que pone fin a un juicio. Lo resuelve un <b>Tribunal Colegiado de Circuito</b>.</li>'
             '<li><b>Revisión:</b> si no estás de acuerdo con lo que resolvió el juzgado, se revisa. Llega a la <b>Suprema Corte</b> solo si sigue en juego si una ley es '
             'constitucional, o si la Corte decide atraer el caso por su importancia; si no, la última palabra es del tribunal colegiado.</li></ul>'
             '<p>Desde la reforma de 2024, cuando se reclama una ley, la suspensión <b>nunca</b> puede tener efectos para todos.</p>',
        'fu': [_o('Qué resuelven los tribunales federales (art. 103)', CPEUM),
               _o('Bases del amparo: parte agraviada, efectos solo para quien lo pide, directo, indirecto, revisión y suspensión (art. 107, frs. I, II, V, VII, VIII y X)', CPEUM)],
        'ir': ['glosario.html', 'Diccionario'],
        'sug': ['¿Qué es la jurisprudencia?', '¿Qué es una acción de inconstitucionalidad?', '¿Cuánto tarda un juicio fiscal?']}
    t['controversias'] = {
        'tit': 'La Corte como tribunal constitucional',
        'h': '<p>Además del amparo, solo la Suprema Corte resuelve dos juicios para proteger la Constitución:</p><ul class="pa-lista">'
             '<li><b>Controversia constitucional:</b> cuando dos autoridades pelean porque una invadió lo que le toca a la otra (la Federación contra un estado, un municipio contra su estado, '
             'el Ejecutivo contra el Congreso…).</li>'
             '<li><b>Acción de inconstitucionalidad:</b> la presentan, entre otros, una parte de los legisladores, los partidos (contra leyes electorales), las comisiones de derechos humanos o la '
             'Fiscalía, para que la Corte diga si una ley contradice la Constitución.</li></ul>'
             '<p>Para anular una ley <b>para todos</b> hacen falta <b>al menos seis de los nueve votos</b>. Y presentar estos juicios <b>no suspende</b> la ley mientras se resuelve.</p>',
        'fu': [_o('Controversias constitucionales y acciones de inconstitucionalidad (art. 105)', CPEUM)],
        'sug': ['¿Qué es el amparo?', '¿Qué es la jurisprudencia?']}
    t['jurisprudencia'] = {
        'tit': 'Cuándo lo que decide la Corte obliga a todos',
        'h': '<p>Cuando el Pleno de la Suprema Corte decide un asunto con <b>al menos seis votos</b>, las razones de su sentencia <b>obligan a todos los jueces</b> del país, '
             'federales y de los estados.</p>'
             '<p>Y si en amparos se repite que una ley es inconstitucional, la Corte avisa a quien la hizo; si en <b>90 días</b> no la corrige, la Corte puede emitir, con seis votos, '
             'una <b>declaratoria general de inconstitucionalidad</b> que vale para todos. Esto <b>no aplica a las leyes de impuestos</b>.</p>',
        'fu': [_o('Obligatoriedad de las razones del Pleno (art. 94) y declaratoria general (art. 107, fr. II)', CPEUM)],
        'ir': ['glosario.html', 'Diccionario'],
        'sug': ['¿Qué es el amparo?', '¿Qué es una acción de inconstitucionalidad?']}
    t['plazos'] = {
        'tit': 'Cuánto debe tardar un juicio de impuestos',
        'h': '<p>La Constitución pide que la justicia sea <b>pronta, completa, imparcial y gratuita</b>. Desde la reforma de 2024, en los juicios de <b>impuestos</b> que fijen las leyes, '
             'los tribunales deben resolver en un máximo de <b>seis meses</b>. Si no lo hacen, deben avisar al <b>Tribunal de Disciplina Judicial</b> y explicar por qué.</p>',
        'fu': [_o('Plazo de seis meses en materia tributaria (art. 17, reformado DOF 15-09-2024)', CPEUM)],
        'sug': ['¿Qué es el Tribunal de Disciplina Judicial?', '¿Qué es el amparo?']}
    t.update(gestion_judicial.temas(d))
    assert sorted(PAGINA_DE) == sorted(t)
    for k, x in t.items():
        x.setdefault('ir', [PAGINA_DE[k][0] + '#jud-' + k, PAGINA_DE[k][1]])
        x['aqui'] = [PAGINA_DE[k][0] + '#jud-' + k, PAGINA_DE[k][1]]
    return {'t': t, 'min': [[n, v] for n, v, _ in MINISTROS], 'pag': [PORTADA, PORTADA_TIT],
            'est': gestion_judicial.por_estado(d)}


def secciones(d, temas):
    """Las secciones de una página de Datos: el mismo texto con que contesta el bot."""
    J = judicial(d)
    F = _fuentes_base(d)
    out = []
    for k in temas:
        x = J['t'][k]
        extra = ''
        if k == 'circuitos':
            filas = ''.join('<tr><td>%d</td><th scope="row">%s</th><td>$%s</td></tr>' % (c['n'], html.escape(c['sede']), _n(c['pagado']))
                            for c in d['poderes']['judicial']['circuitos'])
            extra = ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Los 32 circuitos y lo que pagaron sus oficinas entre abril y junio de 2026 %s</caption>'
                     '<thead><tr><th scope="col">Circuito</th><th scope="col">Sede, como la nombra el Órgano</th><th scope="col">Pagado, abril a junio</th></tr></thead>'
                     '<tbody>%s</tbody></table></div><p class="pa-chico">Fuente: <a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>. '
                     'Son pagos parciales: no incluyen la nómina, que se paga desde oficinas centrales. Costo completo de cada circuito: %s</p>') % (
                _chip('derivado'), filas, html.escape(F['OAJ_UEG']['url'], quote=True), html.escape(F['OAJ_UEG']['tx']), _chip('pendiente', 'poderes-judicial-0'))
        elif k == 'sueldos':
            filas = ''.join('<tr><th scope="row">%s</th><td>$%s</td><td>%s</td></tr>' % (html.escape(n), _n(v), p) for n, v, p in SUELDOS)
            extra = ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Sueldo mensual neto según el tabulador 2026 %s</caption>'
                     '<thead><tr><th scope="col">Cargo</th><th scope="col">Neto al mes</th><th scope="col">Anexo B</th></tr></thead><tbody>%s</tbody>'
                     '<tfoot><tr><th scope="row">Límite de la Presidenta (PEF 2026, Anexo 23.1.2)</th><td>$%s</td><td></td></tr></tfoot></table></div>') % (
                _chip('oficial'), filas, _n(PRESIDENTA))
        elif k == 'ministros':
            filas = ''.join('<tr><td>%d</td><th scope="row">%s</th><td>%s</td><td>%s</td></tr>' % (i, html.escape(n), _n(v), 'Mujer' if g == 'M' else 'Hombre')
                            for i, (n, v, g) in enumerate(MINISTROS, 1))
            extra = ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Asignación del INE, en el orden de su acuerdo %s</caption>'
                     '<thead><tr><th scope="col">#</th><th scope="col">Persona</th><th scope="col">Votos</th><th scope="col">Lugar de</th></tr></thead><tbody>%s</tbody></table></div>') % (
                _chip('oficial'), filas)
        elif k == 'eleccion2025':
            filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (html.escape(c), html.escape(a), m, h, m + h)
                            for c, a, m, h in CARGOS2025)
            extra = ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Los cargos de la elección de 2025 %s</caption>'
                     '<thead><tr><th scope="col">Cargo</th><th scope="col">Dónde se votó</th><th scope="col">Mujeres</th><th scope="col">Hombres</th><th scope="col">Total</th></tr></thead>'
                     '<tbody>%s</tbody><tfoot><tr><th scope="row" colspan="2">Total</th><td>%d</td><td>%d</td><td>%d</td></tr></tfoot></table></div>') % (
                _chip('oficial'), filas, sum(c[2] for c in CARGOS2025), sum(c[3] for c in CARGOS2025), CARGOS2025_TOTAL)
        elif k == 'presupuesto':
            r03 = d['poderes']['ramos2026']['judicial']
            filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s %%</td></tr>' % (html.escape(u['nombre']), _mdp(u['aprobado']),
                                                                                      format(round(100 * u['aprobado'] / r03['aprobado'], 1), '.1f'))
                            for u in sorted(r03['unidades'], key=lambda u: -u['aprobado']))
            extra = ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Presupuesto aprobado 2026 por unidad %s</caption>'
                     '<thead><tr><th scope="col">Unidad</th><th scope="col">Aprobado</th><th scope="col">Parte</th></tr></thead><tbody>%s</tbody>'
                     '<tfoot><tr><th scope="row">Poder Judicial (Ramo 03)</th><td>%s</td><td>100 %%</td></tr></tfoot></table></div>'
                     '<p class="pa-chico">La parte de cada unidad es derivada: su aprobado entre el total del Ramo 03.</p>') % (
                _chip('oficial'), filas, _mdp(r03['aprobado']))
        elif k in gestion_judicial.TEMAS:
            extra = gestion_judicial.extra(d, k)
        out.append({'id': 'jud-' + k, 'titulo': html.escape(x['tit']), 'texto': '', 'tarjetas': [],
                    'bloque': bloque_tema(x, extra, x['aqui'][0].split('#')[0])})
    return out
