# -*- coding: utf-8 -*-
"""El padrón de contribuyentes del SAT, las donatarias autorizadas y las
asociaciones religiosas (pedido del autor, 19-11-2026: «¿podemos obtener
información de cuántos contribuyentes están registrados en el SAT, cuántas
personas morales, jurídicas, asociaciones religiosas, diferentes regímenes
fiscales…?»; «empieza con las tres entregas»).

Mismo molde que gestion_ambiental.py: cada tema es el texto con que contesta
el chat (D.pad) y la sección de su página en Datos. **Ninguna cifra se escribe
aquí**: todas salen de los archivos que anclan, con su huella,

  - docs/sat/padron-sat.json   (anclar_padron_sat.py: los datos abiertos del SAT)
  - docs/sat/donatarias.json   (anclar_donatarias.py: «Estadísticos Donatarias Autorizadas»)

Reglas de lectura que el texto dice al lector:
  - el padrón cuenta RFC activos, no a quien pagó impuestos;
  - los regímenes no se suman: una persona puede tributar en varios;
  - el estado es el del domicilio fiscal, no donde se trabaja o se gasta;
  - las asociaciones religiosas no son contribuyentes del ISR (LISR, art. 79,
    fr. XVI) y el SAT no las separa en su padrón: su registro lo lleva
    Gobernación y está pendiente de integrar (falta nuestra, no de Gobernación).

Lo leen apartados.poderes_paginas() (páginas de Datos), asistente.py (D.pad),
planisferio.py (las lentes del padrón) y pendientes.py.
"""

import html
import json
import os

from asistente_legislativo import _chip, bloque_tema

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PADRON = os.path.join(RAIZ, 'docs', 'sat', 'padron-sat.json')
DONAT = os.path.join(RAIZ, 'docs', 'sat', 'donatarias.json')
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
LISR = {'tx': 'Ley del Impuesto sobre la Renta, texto vigente (Cámara de Diputados, última reforma DOF 13-11-2026)',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LISR.pdf',
        'sha256': '803c2875c09c751c1966b8eb4dca99f460b237da4ef67ee04b4fa325d8c2f786'}
SEGOB_AR = 'https://asociacionesreligiosas.segob.gob.mx/es/AsuntosReligiosos/Numeralia'
SIMULADOR = 'herramienta-calculadora-inmueble.html'

PORTADA = 'datos-padron-sat.html'
PORTADA_TIT = 'Padrón del SAT'
PAGINAS = [
    ('datos-padron-sat-contribuyentes.html', '🧾', 'Cuántos contribuyentes hay', 'Activos, suspendidos y cancelados; personas físicas, morales y asalariados',
     'Cuántas personas y empresas tienen su RFC activo ante el SAT, de qué tipo son y cómo ha crecido el padrón desde 2010. '
     'Con los datos abiertos del SAT, mes por mes.',
     ['cuantos', 'tipos', 'serie']),
    ('datos-padron-sat-regimenes.html', '📑', 'Los regímenes fiscales', 'Sueldos, RESICO, plataformas, arrendamiento, dividendos y los demás',
     'En qué régimen tributa cada quien: cuántos contribuyentes tiene cada uno de los 26 regímenes que registra el SAT, '
     'por qué no se suman y qué quiere decir el régimen de enajenación de bienes.',
     ['regimenes', 'enajenacion']),
    ('datos-padron-sat-estados.html', '🗺️', 'Por estado y por actividad', 'Dónde tienen su domicilio fiscal y a qué se dedican',
     'El padrón por entidad federativa y por sector de actividad económica, con lo que esas dos cuentas no dicen.',
     ['estados', 'sectores']),
    ('datos-padron-sat-sin-fines-de-lucro.html', '🤝', 'Sin fines de lucro', 'Donatarias autorizadas y asociaciones religiosas',
     'Cuántas personas morales no lucrativas hay, cuántas donatarias puede recibir donativos deducibles, de qué tipo, en qué estado, '
     'cuántas pierden la autorización, y qué falta para contar a las asociaciones religiosas.',
     ['nolucrativas', 'donatarias', 'religiosas']),
]
PAGINA_DE = {k: (p[0], p[2]) for p in PAGINAS for k in p[5]}
PRE = 'pad-'

PEND_AR = {'que': 'Cuántas asociaciones religiosas tienen registro constitutivo, por entidad y por credo', 'e': 'pendiente', 'p': 'segob-asociaciones-religiosas',
           'fu': {'tx': 'Secretaría de Gobernación, Asuntos Religiosos: numeralia', 'url': SEGOB_AR}}


def pendientes():
    return [{'id': 'segob-asociaciones-religiosas', 'tema': 'Ingresos',
             'que': 'Cuántas asociaciones religiosas tienen registro constitutivo, por entidad federativa y por credo',
             'porque': 'El registro lo lleva la Secretaría de Gobernación (Ley de Asociaciones Religiosas y Culto Público, art. 6) y publica su numeralia '
                       'en su portal de Asuntos Religiosos. Al 19-11-2026 ese portal no respondió a nuestra descarga, así que todavía no lo integramos: '
                       'la falta es de la plataforma, no de Gobernación. El SAT no las separa en su padrón: no son contribuyentes del ISR '
                       '(LISR, art. 79, fr. XVI) y quedan dentro de las personas morales con fines no lucrativos. Una cifra que solo diga la prensa no entra.',
             'responsable': None, 'enlace': SEGOB_AR, 'enlace_txt': 'Numeralia de Asuntos Religiosos (Gobernación)',
             'aparece': [('herramienta-inspector-pregunta.html', 'Pregúntale al Auditor'),
                         ('datos-padron-sat-sin-fines-de-lucro.html', 'Datos · Padrón del SAT · Sin fines de lucro')]}]


def _n(v):
    return format(int(v), ',')


def _p(a, b, dec=1):
    return format(round(100.0 * a / b, dec), '.%df' % dec) + ' %'


def _o(que, fu, op=None, e=None):
    d = {'que': que, 'e': e or ('derivado' if op else 'oficial'), 'fu': fu}
    if op:
        d['op'] = op
    return d


def cargar():
    P = json.load(open(PADRON, encoding='utf-8'))
    Dn = json.load(open(DONAT, encoding='utf-8'))
    # El mismo cuadre que el script de anclaje: si alguien edita el JSON a mano, se detiene.
    for f in P['tipo']['serie']:
        assert sum(f[2:7]) == f[7], f
    assert P['sit']['serie'][-1][2] == P['tipo']['serie'][-1][7]
    assert sum(P['ent']['serie'][-1][2:]) == P['tipo']['serie'][-1][7]
    assert sum(Dn['por_entidad'].values()) == sum(Dn['por_tipo'].values()) == Dn['total'] == Dn['anual'][-1][1]
    return P, Dn


def _fu(P, k, que):
    a = P['archivos'][k]
    return {'tx': 'SAT, datos abiertos del padrón: %s (%s), cifras preliminares' % (que, a['archivo']), 'url': a['url'], 'sha256': a['sha256']}


def _mes(f):
    return '%s de %d' % (MESES[f[1] - 1], f[0])


def _dic(serie, anio):
    for f in serie:
        if f[0] == anio and f[1] == 12:
            return f
    return None


def datos():
    """Lo que necesitan el chat, la página y el Planisferio, ya leído y cuadrado."""
    P, Dn = cargar()
    t, s, r = P['tipo']['serie'][-1], P['sit']['serie'][-1], P['reg']['serie'][-1]
    reg = dict(zip(P['reg']['cols'], r[2:]))
    nreg = dict(zip(P['reg']['cols'], P['reg']['nombres']))
    ent = {a: v for a, v in zip(P['ent']['abbr'], P['ent']['serie'][-1][2:]) if a}
    sec = list(zip(P['sec']['cols'], P['sec']['nombres'], P['sec']['serie'][-1][2:]))
    return P, Dn, t, s, reg, nreg, ent, sec


def temas(d):
    """Los temas del chat y de las páginas. `d` es window.AUDIT_DB (para la población)."""
    P, Dn, t, s, reg, nreg, ent, sec = datos()
    corte = _mes(t)
    FT, FS, FR, FE, FC = (_fu(P, 'tipo', 'por tipo de contribuyente'), _fu(P, 'sit', 'por situación ante el RFC'),
                          _fu(P, 'reg', 'por régimen'), _fu(P, 'ent', 'por entidad federativa'), _fu(P, 'sec', 'por sector de actividad económica'))
    FD = {'tx': Dn['doc']['tx'], 'url': Dn['doc']['url'], 'sha256': Dn['doc']['sha256']}
    pob = sum(e['pobPersonas'] for e in d['estados'])
    pf, gpf, asal, pm, gpm, tot = t[2:8]
    act, sus, can = s[2:5]
    tt = {}
    tt['cuantos'] = {
        'tit': 'Cuántos contribuyentes hay',
        'h': '<p>En %s el SAT tenía <b>%s contribuyentes activos</b>: personas y empresas con su RFC vigente. Además, <b>%s suspendidos</b> '
             '(avisaron que dejaron de tener actividad) y <b>%s cancelados</b>.</p>'
             '<p>De los activos, <b>%s son asalariados</b>: su impuesto lo retiene el patrón. '
             'Las personas morales (empresas, asociaciones y sociedades) son <b>%s</b>, contando a las %s más grandes.</p>'
             '<p class="pa-chico">Un RFC activo no quiere decir que esa persona pagó impuestos ese mes: es quien está inscrito y tiene obligaciones. '
             'Son cifras preliminares del SAT. Para comparar: la población de México a mitad de 2026 es de %s personas (CONAPO, la de la base), '
             'pero un contribuyente puede ser una empresa, así que dividir una cifra entre la otra no da «cuántos mexicanos pagan».</p>' % (
                 corte, _n(act), _n(sus), _n(can), _n(asal), _n(pm + gpm), _n(gpm), _n(pob)),
        'fu': [_o('Contribuyentes activos, suspendidos y cancelados, %s' % corte, FS),
               _o('Activos por tipo de contribuyente, %s' % corte, FT),
               _o('Personas morales, con las grandes', FT, '%s + %s grandes contribuyentes' % (_n(pm), _n(gpm)))],
        'ci': [{'v': _n(act), 'etq': 'contribuyentes activos (%s)' % corte, 'e': 'oficial'},
               {'v': _n(asal), 'etq': 'asalariados', 'e': 'oficial'},
               {'v': _n(pm + gpm), 'etq': 'personas morales', 'e': 'derivado', 'op': '%s + %s grandes' % (_n(pm), _n(gpm))}],
        'sug': ['¿Cuántas personas morales hay en el SAT?', '¿Cuántos contribuyentes hay en RESICO?', '¿Cuántas donatarias autorizadas hay?']}
    tt['tipos'] = {
        'tit': 'Personas físicas, morales y asalariados',
        'h': '<p>El SAT reparte a sus %s contribuyentes activos en cinco tipos, y los cinco suman exacto el total:</p><ul class="pa-lista">'
             '<li><b>Asalariados</b>: %s (%s). Trabajan en nómina.</li>'
             '<li><b>Personas físicas</b> que no son asalariadas: %s (%s). Profesionistas, comercios, arrendadores, RESICO, plataformas…</li>'
             '<li><b>Personas morales</b>: %s (%s). Sociedades, asociaciones civiles, fideicomisos con RFC.</li>'
             '<li><b>Grandes contribuyentes</b>: %s personas morales y %s personas físicas, que el SAT atiende aparte por el tamaño de sus ingresos '
             '(desde 2021 incluye a los de hidrocarburos, según la nota del SAT).</li></ul>'
             '<p class="pa-chico">«Persona moral» es el término de la ley para lo que en otros países se llama persona jurídica: una empresa o una organización con '
             'personalidad propia, distinta de la de sus socios.</p>' % (
                 _n(tot), _n(asal), _p(asal, tot), _n(pf), _p(pf, tot), _n(pm), _p(pm, tot), _n(gpm), _n(gpf)),
        'fu': [_o('Activos por tipo de contribuyente, %s' % corte, FT),
               _o('Proporción de cada tipo', FT, 'cada tipo ÷ %s activos' % _n(tot))],
        'ci': [{'v': _n(pf), 'etq': 'personas físicas no asalariadas', 'e': 'oficial'},
               {'v': _n(pm), 'etq': 'personas morales (sin las grandes)', 'e': 'oficial'},
               {'v': _n(gpm + gpf), 'etq': 'grandes contribuyentes', 'e': 'derivado', 'op': '%s morales + %s físicas' % (_n(gpm), _n(gpf))}],
        'sug': ['¿Cuántos contribuyentes hay en el SAT?', '¿En qué régimen tributa más gente?']}
    serie = P['tipo']['serie']
    ini = serie[0]
    d25 = _dic(serie, 2025)
    tt['serie'] = {
        'tit': 'Cómo ha crecido el padrón',
        'h': '<p>En %s había %s contribuyentes activos; en %s, <b>%s</b>: el padrón se multiplicó por %s. Casi todo el crecimiento son asalariados y personas físicas: '
             'las personas morales pasaron de %s a %s.</p>'
             '<p>Del cierre de 2025 a %s se sumaron %s activos.</p>'
             '<p class="pa-chico">Que crezca el padrón no quiere decir que crezca la recaudación en la misma medida: el padrón cuenta inscritos con RFC activo, no pagos.</p>' % (
                 _mes(ini), _n(ini[7]), corte, _n(tot), format(round(tot / ini[7], 1), '.1f'), _n(ini[5] + ini[6]), _n(pm + gpm), corte, _n(tot - d25[7])),
        'fu': [_o('Serie mensual de activos por tipo, desde %s' % _mes(ini), FT),
               _o('Veces que creció el padrón', FT, '%s ÷ %s' % (_n(tot), _n(ini[7]))),
               _o('Altas netas desde el cierre de 2025', FT, '%s − %s (diciembre de 2025)' % (_n(tot), _n(d25[7])))],
        'ci': [{'v': format(round(tot / ini[7], 1), '.1f') + ' veces', 'etq': 'creció el padrón desde %d' % ini[0], 'e': 'derivado'}],
        'sug': ['¿Cuántos contribuyentes hay en el SAT?', '¿Cuántas personas morales hay en el SAT?']}

    orden = sorted(((k, v) for k, v in reg.items() if v), key=lambda x: (-x[1], x[0]))
    top = ''.join('<li><b>%s</b>: %s</li>' % (html.escape(nreg[k]), _n(v)) for k, v in orden[:8])
    tt['regimenes'] = {
        'tit': 'Cuántos hay en cada régimen fiscal',
        'h': '<p>El régimen dice qué reglas del ISR te tocan. En %s, los que más contribuyentes tienen:</p><ul class="pa-lista">%s</ul>'
             '<p><b>Los regímenes no se suman</b>: como avisa el propio SAT, una persona puede estar en varios a la vez (por ejemplo, con sueldo y con una casa que renta). '
             'Por eso la suma de la tabla pasa del total de activos.</p>'
             '<p>Los «sin obligaciones fiscales» (%s) tienen RFC activo pero ninguna obligación dada de alta ante el SAT.</p>' % (corte, top, _n(reg['sinobl'])),
        'fu': [_o('Contribuyentes activos por régimen, %s' % corte, FR)],
        'ci': [{'v': _n(reg['resico']), 'etq': 'en el Régimen Simplificado de Confianza (RESICO)', 'e': 'oficial'},
               {'v': _n(reg['plataf']), 'etq': 'con ingresos por plataformas tecnológicas', 'e': 'oficial'},
               {'v': _n(reg['arrend']), 'etq': 'en arrendamiento', 'e': 'oficial'}],
        'sug': ['¿Cuántos contribuyentes hay en RESICO?', '¿Cuánto ISR pago si vendo mi casa?', '¿Cuántas personas morales hay en el SAT?']}
    tt['enajenacion'] = {
        'tit': 'El régimen de enajenación de bienes',
        'h': '<p>En %s el padrón tiene <b>%s contribuyentes en el régimen de enajenación o adquisición de bienes</b>, %s en el de dividendos y %s en el de intereses.</p>'
             '<p>Que haya tan pocos en enajenación <b>no quiere decir que pocas personas vendan</b>: cuando vendes una casa o un terreno ante notario, '
             'el notario calcula el impuesto y lo entera por ti (LISR, art. 126), y el padrón solo cuenta la obligación dada de alta. '
             'Por eso esa cifra no sirve para saber cuántas ventas hay.</p>'
             '<p>¿Cuánto ISR causa vender un inmueble? Lo calcula el <a href="%s">simulador de venta de un inmueble</a> de la Calculadora Cívica, '
             'con la ley a la vista.</p>' % (corte, _n(reg['enaj']), _n(reg['divid']), _n(reg['interes']), SIMULADOR),
        'fu': [_o('Activos por régimen, %s' % corte, FR),
               _o('El notario calcula y entera el pago provisional de una venta de inmueble', LISR)],
        'ci': [{'v': _n(reg['enaj']), 'etq': 'en el régimen de enajenación o adquisición de bienes', 'e': 'oficial'},
               {'v': _n(reg['divid']), 'etq': 'en el régimen de dividendos', 'e': 'oficial'}],
        'sug': ['¿Cuánto ISR pago si vendo mi casa?', '¿Cuántos contribuyentes hay en el SAT?']}

    nombre = {e['abbr']: e['name'] for e in d['estados']}
    por = sorted(ent.items(), key=lambda x: (-x[1], x[0]))
    pc = sorted(((a, 100.0 * v / next(e['pobPersonas'] for e in d['estados'] if e['abbr'] == a)) for a, v in ent.items()), key=lambda x: (-x[1], x[0]))
    nesp = P['ent']['serie'][-1][-1]
    tt['estados'] = {
        'tit': 'El padrón por estado',
        'h': '<p>Por domicilio fiscal, los estados con más contribuyentes activos en %s son %s.</p>'
             '<p>Frente a su población, los que más contribuyentes tienen por cada 100 habitantes son %s; los que menos, %s.</p>'
             '<p class="pa-chico"><b>Ojo con esta cuenta</b>: el SAT cuenta a cada contribuyente donde tiene su domicilio fiscal, no donde trabaja, vende o gasta. '
             'Una empresa que opera en todo el país cuenta solo donde tiene su domicilio fiscal, y una persona moral no es un habitante. Por eso «por cada 100 habitantes» '
             'puede pasar de 100 y no es una calificación del estado. Hay además %s contribuyentes sin entidad especificada.</p>' % (
                 corte, ', '.join('%s (%s)' % (nombre[a], _n(v)) for a, v in por[:3]),
                 ', '.join('%s (%s)' % (nombre[a], format(round(x, 1), '.1f')) for a, x in pc[:3]),
                 ', '.join('%s (%s)' % (nombre[a], format(round(x, 1), '.1f')) for a, x in pc[-3:]), _n(nesp)),
        'fu': [_o('Activos por entidad federativa, %s' % corte, FE),
               _o('Contribuyentes por cada 100 habitantes', FE, 'activos de la entidad × 100 ÷ su población a mitad de 2026 (CONAPO, la de la base)')],
        'ci': [{'v': _n(por[0][1]), 'etq': 'activos con domicilio fiscal en %s' % nombre[por[0][0]], 'e': 'oficial'}],
        'sug': ['¿Cuántos contribuyentes hay en Jalisco?', '¿Cuántas donatarias hay en Nuevo León?']}
    sc = P['sec']['serie'][-1]
    ords = sorted(sec, key=lambda x: (-x[2], x[0]))
    tt['sectores'] = {
        'tit': 'El padrón por actividad económica',
        'h': '<p>Al cierre del %s trimestre de %d, por la actividad que declararon: %s.</p>'
             '<p class="pa-chico">El SAT asigna a cada contribuyente una sola actividad de su catálogo. Que «servicios profesionales» y «otros» junten a la mayoría '
             'depende de cómo el SAT clasifica a cada inscrito (el archivo no lo explica), así que no es un retrato de la economía: para eso están los censos del INEGI.</p>' % (
                 ['primer', 'segundo', 'tercer', 'cuarto'][sc[1] // 3 - 1], sc[0],
                 '; '.join('<b>%s</b>, %s' % (html.escape(n.lower() if i else n), _n(v)) for i, (_, n, v) in enumerate(ords[:5]))),
        'fu': [_o('Activos por sector de actividad económica, trimestral', FC)],
        'ci': [{'v': _n(dict((k, v) for k, _, v in sec)['manuf']), 'etq': 'en industrias manufactureras', 'e': 'oficial'}],
        'sug': ['¿Cuántos contribuyentes hay en el SAT?', '¿En qué régimen tributa más gente?']}

    tt['nolucrativas'] = {
        'tit': 'Personas morales sin fines de lucro',
        'h': '<p>En %s el padrón tiene <b>%s personas morales con fines no lucrativos</b>. La ley dice quiénes pueden serlo (LISR, Título III, art. 79): sindicatos, cámaras, '
             'colegios de profesionistas, instituciones de asistencia o de beneficencia, sociedades cooperativas de consumo, asociaciones civiles con fines políticos '
             'y asociaciones religiosas, entre otras. El padrón no dice cuántas hay de cada clase.</p>'
             '<p>Que no busquen lucro no quiere decir que no tengan obligaciones (art. 86). Pero <b>solo las donatarias autorizadas '
             'pueden dar recibos deducibles</b>: en %d son %s, unas %s de cada 100 no lucrativas del padrón (con cortes distintos: enero y %s).</p>' % (
                 corte, _n(reg['nolucro']), Dn['anio'], _n(Dn['total']), format(round(100.0 * Dn['total'] / reg['nolucro'], 1), '.1f'), MESES[t[1] - 1]),
        'fu': [_o('Personas morales con fines no lucrativos, %s' % corte, FR),
               _o('Quiénes son personas morales con fines no lucrativos', dict(LISR, tx=LISR['tx'] + ', arts. 79 a 89')),
               _o('Donatarias frente a las no lucrativas del padrón', FD, '%s ÷ %s (años y cortes distintos)' % (_n(Dn['total']), _n(reg['nolucro'])))],
        'ci': [{'v': _n(reg['nolucro']), 'etq': 'personas morales con fines no lucrativos', 'e': 'oficial'}],
        'sug': ['¿Cuántas donatarias autorizadas hay?', '¿Cuántas asociaciones religiosas hay?']}
    tipos = sorted(Dn['por_tipo'].items(), key=lambda x: (-x[1], x[0]))
    an = Dn['anual']
    mx = max(an, key=lambda x: x[1])
    tt['donatarias'] = {
        'tit': 'Las donatarias autorizadas',
        'h': '<p>Para %d el SAT autorizó a <b>%s donatarias</b>: organizaciones civiles y fideicomisos que pueden recibir donativos deducibles del ISR. '
             'En %d fueron %s, y en %d, su máximo, %s.</p>'
             '<p class="pa-chico">Ojo al comparar: la cifra de %d es la del Anexo 14 publicado en enero; la de los años anteriores cuenta a todas las que estuvieron '
             'autorizadas en algún momento del año, así que la de %d todavía puede subir con las modificaciones al Anexo.</p>'
             '<p>Por lo que hacen, %s son <b>asistenciales</b> (%s), %s educativas y %s culturales. %s pueden recibir además donativos deducibles desde Estados Unidos.</p>'
             '<p>La autorización se pierde: en %d el SAT <b>revocó %s</b> por incumplir requisitos (LISR, art. 82-Quáter), %s pidieron la cancelación y %s '
             'perdieron su vigencia al empezar %d por no cumplir los requisitos de la renovación.</p>'
             '<p class="pa-chico">La lista con nombre y RFC de cada una es el Anexo 14 de la Resolución Miscelánea Fiscal, publicado en el DOF; antes de deducir un donativo, '
             'revisa que la organización esté ahí. Haber sido donataria el año pasado no basta.</p>' % (
                 Dn['anio'], _n(Dn['total']), an[-2][0], _n(an[-2][1]), mx[0], _n(mx[1]), Dn['anio'], Dn['anio'],
                 _n(Dn['por_tipo']['A']), _p(Dn['por_tipo']['A'], Dn['total']), _n(Dn['por_tipo']['B']), _n(Dn['por_tipo']['D']), _n(Dn['extranjero'][-1][1]),
                 Dn['revocaciones'][-2][0], _n(Dn['revocaciones'][-2][1]), _n(Dn['cancelaciones'][-2][1]),
                 _n(Dn['perdieron_vigencia'][-1][1]), Dn['perdieron_vigencia'][-1][0]),
        'fu': [_o('Donatarias autorizadas por ejercicio, por tipo, por entidad, revocaciones, cancelaciones y pérdidas de vigencia', FD),
               _o('Revocación de la autorización', dict(LISR, tx=LISR['tx'] + ', art. 82-Quáter')),
],
        'ci': [{'v': _n(Dn['total']), 'etq': 'donatarias autorizadas en %d' % Dn['anio'], 'e': 'oficial'},
               {'v': _n(Dn['revocaciones'][-2][1]), 'etq': 'autorizaciones revocadas en %d' % Dn['revocaciones'][-2][0], 'e': 'oficial'}],
        'sug': ['¿Cuántas donatarias hay en Nuevo León?', '¿Cuántas asociaciones religiosas hay?', '¿Cuántas personas morales hay en el SAT?']}
    tt['religiosas'] = {
        'tit': 'Las asociaciones religiosas',
        'h': '<p><b>Las asociaciones religiosas no son contribuyentes del ISR</b> (LISR, art. 79, fr. XVI), y el SAT no las cuenta aparte en su padrón: '
             'el art. 79 está en el Título III, el de las personas morales con fines no lucrativos, que en el padrón son %s en total. Sí tienen obligaciones fiscales, como llevar contabilidad y expedir comprobantes (LISR, art. 86).</p>'
             '<p>Cuántas hay lo sabe la <b>Secretaría de Gobernación</b>, que les otorga el registro constitutivo (Ley de Asociaciones Religiosas y Culto Público) '
             'y publica su numeralia. <b>Todavía no la integramos</b>: su portal no respondió a nuestra descarga. Mientras no la cotejemos, '
             'la cifra queda pendiente; no la tomamos de notas de prensa.</p>' % _n(reg['nolucro']),
        'fu': [_o('Las asociaciones religiosas no son contribuyentes del ISR', dict(LISR, tx=LISR['tx'] + ', art. 79, fr. XVI')),
               _o('Obligaciones de las personas morales no lucrativas', dict(LISR, tx=LISR['tx'] + ', art. 86')),
               _o('Personas morales con fines no lucrativos, %s' % corte, FR), PEND_AR],
        'sug': ['¿Cuántas donatarias autorizadas hay?', '¿Cuántas personas morales hay en el SAT?']}

    assert sorted(tt) == sorted(PAGINA_DE)
    for k, x in tt.items():
        x['ir'] = [PAGINA_DE[k][0] + '#' + PRE + k, PAGINA_DE[k][1]]
        x['aqui'] = x['ir']
    return {'t': tt, 'pag': [PORTADA, PORTADA_TIT], 'corte': corte}


def chat(d):
    """D.pad del chat: los temas y las cifras por estado para «¿cuántos contribuyentes hay en Jalisco?»."""
    T = temas(d)
    P, Dn, t, s, reg, nreg, ent, sec = datos()
    T['ent'] = {a: [v, Dn['por_entidad'].get(a)] for a, v in ent.items()}
    T['danio'] = Dn['anio']
    T['fe'] = {'tx': 'SAT, datos abiertos del padrón por entidad federativa', 'url': P['archivos']['ent']['url']}
    T['fd'] = {'tx': Dn['doc']['tx'], 'url': Dn['doc']['url']}
    return T


def planisferio(d):
    """Por entidad, para las lentes del Planisferio: activos, por cada 100 habitantes y donatarias."""
    P, Dn, t, s, reg, nreg, ent, sec = datos()
    out = {}
    for e in d['estados']:
        a = e['abbr']
        out[a] = {'n': ent[a], 'h': round(100.0 * ent[a] / e['pobPersonas'], 1), 'don': Dn['por_entidad'][a]}
    meta = {'corte': _mes(t), 'fe': P['archivos']['ent']['url'], 'fd': Dn['doc']['url'], 'danio': Dn['anio'], 'dtx': Dn['doc']['tx']}
    return out, meta


def _tabla(caption, cols, filas, pie=None):
    th = ''.join('<th scope="col">%s</th>' % c for c in cols)
    tb = ''.join('<tr><th scope="row">%s</th>%s</tr>' % (f[0], ''.join('<td>%s</td>' % x for x in f[1:])) for f in filas)
    tf = '<tfoot><tr><th scope="row">%s</th>%s</tr></tfoot>' % (pie[0], ''.join('<td>%s</td>' % x for x in pie[1:])) if pie else ''
    return '<div class="leg-tabla-caja"><table class="leg-tabla"><caption>%s</caption><thead><tr>%s</tr></thead><tbody>%s</tbody>%s</table></div>' % (caption, th, tb, tf)


def secciones(d, temas_):
    """Las secciones de una página de Datos: el mismo texto con que contesta el chat, con sus tablas."""
    S = temas(d)
    P, Dn, t, s, reg, nreg, ent, sec = datos()
    nombre = {e['abbr']: e['name'] for e in d['estados']}
    pobl = {e['abbr']: e['pobPersonas'] for e in d['estados']}
    out = []
    for k in temas_:
        x = S['t'][k]
        extra = ''
        if k == 'tipos':
            extra = _tabla('Contribuyentes activos por tipo, %s %s' % (S['corte'], _chip('oficial')), ['Tipo', 'Activos'],
                           [(html.escape(n), _n(v)) for n, v in zip(P['tipo']['nombres'][:5], t[2:7])], ('Total', _n(t[7])))
        elif k == 'serie':
            filas = []
            for a in range(P['tipo']['serie'][0][0], t[0] + 1):
                f = _dic(P['tipo']['serie'], a) or (t if a == t[0] else None)
                if f:
                    filas.append(('%d%s' % (a, '' if f[1] == 12 else ' (%s)' % MESES[f[1] - 1]), _n(f[4]), _n(f[2] + f[3]), _n(f[5] + f[6]), _n(f[7])))
            extra = _tabla('Activos al cierre de cada año %s · las personas morales y físicas incluyen a las grandes (%s)' % (_chip('oficial'), _chip('derivado')),
                           ['Año', 'Asalariados', 'Personas físicas', 'Personas morales', 'Total'], filas)
        elif k == 'regimenes':
            orden = sorted(((n, v) for n, v in zip(P['reg']['nombres'], P['reg']['serie'][-1][2:]) if v), key=lambda x: -x[1])
            extra = _tabla('Contribuyentes activos por régimen, %s %s · no se suman: una persona puede estar en varios' % (S['corte'], _chip('oficial')),
                           ['Régimen', 'Activos'], [(html.escape(n), _n(v)) for n, v in orden])
        elif k == 'estados':
            filas = sorted(ent.items(), key=lambda a: (-a[1], a[0]))
            extra = _tabla('Contribuyentes activos por domicilio fiscal, %s %s y por cada 100 habitantes %s' % (S['corte'], _chip('oficial'), _chip('derivado')),
                           ['Entidad', 'Activos', 'Por cada 100 habitantes', 'Donatarias %d' % Dn['anio']],
                           [(html.escape(nombre[a]), _n(v), format(round(100.0 * v / pobl[a], 1), '.1f'), _n(Dn['por_entidad'][a])) for a, v in filas],
                           ('Sin entidad especificada', _n(P['ent']['serie'][-1][-1]), '', ''))
        elif k == 'sectores':
            filas = sorted(sec, key=lambda x: -x[2])
            extra = _tabla('Contribuyentes activos por sector de actividad %s' % _chip('oficial'), ['Sector', 'Activos'],
                           [(html.escape(n), _n(v)) for _, n, v in filas], ('Total', _n(sum(v for _, _, v in sec))))
        elif k == 'donatarias':
            tipos = sorted(Dn['por_tipo'].items(), key=lambda a: (-a[1], a[0]))
            extra = (_tabla('Donatarias autorizadas %d por tipo de actividad (clave del Anexo 14) %s' % (Dn['anio'], _chip('oficial')), ['Tipo', 'Donatarias'],
                            [('%s · %s' % (c, html.escape(Dn['tipos'][c])), _n(v)) for c, v in tipos], ('Total', _n(Dn['total'])))
                     + _tabla('Donatarias autorizadas por ejercicio %s' % _chip('oficial'), ['Ejercicio', 'Autorizadas', 'Para donativos del extranjero'],
                              [(str(a), _n(v), _n(dict(Dn['extranjero']).get(a, 0))) for a, v in Dn['anual']]))
        out.append({'id': PRE + k, 'titulo': html.escape(x['tit']), 'texto': '', 'tarjetas': [],
                    'bloque': bloque_tema(x, extra, x['aqui'][0].split('#')[0])})
    return out
