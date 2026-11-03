# -*- coding: utf-8 -*-
"""La administración pública en los tres niveles: quién la forma, qué hace,
cuánto cuesta, cómo contrata y quién la audita (pedido del autor, 03-11-2026:
«integraremos la administración pública, que consiste literalmente en las
administraciones de estado, qué funciones tiene, y checaremos sus auditorías,
que ya tenemos en nuestra base de datos, en los tres niveles»).

Mismo molde que gestion_salud.py y gestion_ambiental.py. Documentos cotejados
el 03-11-2026 (huella SHA-256 abajo):

- INEGI, Censo Nacional de Gobierno Federal y Gobiernos Estatales (CNGF-E)
  2025, Reporte de resultados 52/25 (4 de diciembre de 2025): la
  Administración Pública Federal (APF) y las 32 estatales (APE), con cifras
  de 2024. Por entidad publica: personas titulares (tabla 1), personal
  (tabla 3), presupuesto ejercido (gráfica 5) y contratos por procedimiento
  (tabla 9).
- INEGI, Censo Nacional de Gobiernos Municipales y Demarcaciones Territoriales
  de la Ciudad de México (CNGMD) 2025, Reporte de resultados (19 de marzo de
  2026; archivo sustituido el 01-04-2026 por la tabla de panteones): las
  administraciones municipales, con su presupuesto ejercido por entidad
  (gráfica 23) y sus instituciones por función (gráfica 15).
- Las auditorías de la ASF ya estaban en la base: la Matriz de Datos Básicos
  de la Cuenta Pública 2024 (DB.cuenta_publica_asf.cp2024), con lo de cada
  entidad partido en Gobierno del Estado, Municipios y Otros.

Todo lo que es del censo se dice como lo que cada gobierno le reportó al
INEGI: el censo no audita, pregunta. Por eso el personal de un estado no se
compara sin decir que cada uno cuenta distinto (unos incluyen a sus maestros
y médicos en organismos, otros no).

La leen el Planisferio (dimensión «Administración pública»), la Enciclopedia
(Datos › Administración pública, como un Poder más) y el chat (D.apu).
"""

import html

from asistente_legislativo import _chip, bloque_tema

CNGE = {'tx': 'INEGI, Censo Nacional de Gobierno Federal y Gobiernos Estatales (CNGF-E) 2025, Reporte de resultados 52/25',
        'url': 'https://www.inegi.org.mx/contenidos/programas/cnge/2025/doc/cnge_2025_resultados_adm_pub.pdf',
        'sha256': '1134ba1c5124c23537856f11090f2bbe898230ec4477befea5cd00c3cb7b0fcc'}
CNGMD = {'tx': 'INEGI, Censo Nacional de Gobiernos Municipales y Demarcaciones Territoriales (CNGMD) 2025, Reporte de resultados',
         'url': 'https://www.inegi.org.mx/contenidos/programas/cngmd/2025/doc/cngmd_2025_resultados.pdf',
         'sha256': '968cc3ec568ebacfe73b5684f44fb093f3b379956f65c99fa8aaeb8af0b0fb62'}
CPEUM = {'tx': 'Constitución Política de los Estados Unidos Mexicanos, texto vigente (Cámara de Diputados)',
         'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf'}
LOAPF = {'tx': 'Ley Orgánica de la Administración Pública Federal, texto vigente (Cámara de Diputados)',
         'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LOAPF.pdf'}


def _f(doc, pag, que=''):
    f = dict(doc)
    f['tx'] = '%s, p. %s%s' % (f['tx'], pag, (' (%s)' % que) if que else '')
    return f


def cnge(pag, que=''):
    return _f(CNGE, pag, que)


def cngmd(pag, que=''):
    return _f(CNGMD, pag, que)


# CNGE 2025, cifras de 2024 por entidad, en el orden de la base:
# (titulares de instituciones, tabla 1, p. 5; personal adscrito, tabla 3,
# p. 8; presupuesto ejercido en millones de pesos corrientes, gráfica 5,
# p. 11; contratos, tabla 9, p. 31; de cada 100 contratos, por adjudicación
# directa, tabla 9).
APE = {
    'AGS': (61, 40403, 29839.2, 645, 58.9), 'BC': (57, 51452, 124992.6, 465, 62.6),
    'BCS': (38, 12667, 20144.6, 712, 39.0), 'CAM': (82, 20341, 20881.8, 346, 34.1),
    'CHIS': (62, 75730, 128630.2, 695, 81.4), 'CHIH': (65, 56945, 47512.6, 3065, 61.8),
    'CDMX': (76, 150309, 184064.9, 9612, 69.4), 'COAH': (61, 24249, 49986.5, 175, 15.4),
    'COL': (32, 18543, 14010.2, 297, 47.5), 'DGO': (53, 58744, 32483.8, 1083, 41.7),
    'GTO': (73, 115813, 92974.2, 8616, 40.6), 'GRO': (82, 107820, 62270.0, 5313, 88.7),
    'HGO': (86, 13146, 51193.5, 923, 9.4), 'JAL': (82, 149888, 179417.7, 3542, 21.6),
    'MÉX': (98, 293328, 354987.2, 1000, 29.5), 'MICH': (52, 43218, 73375.6, 578, 24.7),
    'MOR': (72, 35391, 15084.7, 288, 57.3), 'NAY': (59, 35539, 22113.1, 1536, 80.9),
    'NL': (79, 89036, 106696.4, 629, 48.8), 'OAX': (82, 33311, 77851.7, 32, 37.5),
    'PUE': (83, 73044, 127198.3, 1011, 7.4), 'QRO': (85, 51442, 32940.2, 441, 13.2),
    'QROO': (71, 41135, 31637.4, 2598, 51.1), 'SLP': (77, 63242, 47033.0, 2443, 77.9),
    'SIN': (86, 11855, 62143.3, 433, 46.4), 'SON': (71, 64658, 68654.2, 7784, 94.1),
    'TAB': (61, 79108, 63744.9, 5025, 57.3), 'TAM': (53, 87761, 78466.8, 787, 31.0),
    'TLAX': (63, 37516, 22013.2, 5104, 88.8), 'VER': (71, 187374, 151952.6, 4857, 75.5),
    'YUC': (66, 68095, 37108.3, 525, 30.9), 'ZAC': (51, 46077, 31056.0, 4239, 87.8),
}
# Los totales que el reporte da en su texto (pp. 3, 5, 6, 10 y 30).
APE_TOT = {'tit': 2190, 'per': 2237180, 'pres': 2442458.829720, 'con': 74799, 'inst': 2253}
APF = {'tit': 268, 'per': 1691406, 'pres': 5401874.244503, 'con': 131252, 'ad': 83.9, 'inst': 292}
TOT = {'tit': 2458, 'per': 3928586, 'pres': 7844333.074223, 'con': 206051, 'ad': 76.8, 'inst': 2545}
# Auditorías que les aplicaron sus autoridades de control, vigilancia o
# fiscalización en 2024 (p. 21) y las de 2023 que el reporte compara.
AUD_INT = {'apf': 1858, 'ape': 6226, 'apf23_var': -8.7, 'ape23_var': 1.4}
APE_MAX_INST = (('MÉX', 106), ('NL', 90), ('SIN', 88))     # p. 3: las que más instituciones tienen
# Las dos salvedades de la tabla 9.
CONTRATOS_NOTA = ('Oaxaca solo reportó contratos de adquisiciones, arrendamientos y servicios, sin obra pública, '
                  'y Yucatán reportó una parte, por el cambio de administración.')

# CNGMD 2025, presupuesto ejercido por las administraciones municipales en
# 2024, millones de pesos corrientes (gráfica 23, p. 26).
APM_PRES = {
    'AGS': 8720.8, 'BC': 24025.5, 'BCS': 7404.8, 'CAM': 6528.8, 'CHIS': 28456.3, 'CHIH': 24119.4,
    'CDMX': 31842.0, 'COAH': 18848.5, 'COL': 5155.2, 'DGO': 10513.0, 'GTO': 38224.5, 'GRO': 19659.8,
    'HGO': 14547.3, 'JAL': 84837.1, 'MÉX': 138486.3, 'MICH': 23987.1, 'MOR': 11505.0, 'NAY': 8233.5,
    'NL': 42505.9, 'OAX': 16558.9, 'PUE': 31602.4, 'QRO': 22002.6, 'QROO': 18731.0, 'SLP': 15488.1,
    'SIN': 18629.1, 'SON': 18164.7, 'TAB': 16263.9, 'TAM': 38079.4, 'TLAX': 5025.3, 'VER': 40475.3,
    'YUC': 14546.9, 'ZAC': 8799.5,
}
APM = {'pres': 811968.057578, 'inst': 43289, 'central': 92.8, 'para': 7.2, 'tit': 43819, 'per': 1071516,
       'aud': 9487, 'informaron': 2434, 'municipios': 2478}
# Auditorías a los municipios en 2024 según quién las hizo (gráfica 63, p. 72).
APM_AUD = [('La contraloría interna del municipio', 3173), ('Sus órganos internos de control', 2250),
           ('La entidad de fiscalización superior del estado', 2192), ('La Auditoría Superior de la Federación', 1031),
           ('Un despacho privado', 433), ('Otra autoridad', 145), ('La Secretaría de la Función Pública', 69),
           ('La contraloría del estado', 49)]
# Instituciones municipales por función principal (gráfica 15, p. 18): las diez primeras.
APM_FUN = [('Función pública (control interno)', 5642), ('Servicios públicos', 3966), ('Desarrollo social', 3038),
           ('Asuntos financieros y hacendarios', 2787), ('Gobierno y política interior', 2737),
           ('Servicios registrales, administrativos y patrimoniales', 2167), ('Seguridad pública', 1859),
           ('Igualdad de género y derechos de las mujeres', 1586), ('Infraestructura, comunicaciones y transportes', 1577),
           ('Asuntos jurídicos', 1535)]
APM_FUN_TOT = 43289

# Los sectores de la Matriz de la ASF que no son la Administración Pública
# Federal: Poderes y órganos autónomos.
NO_APF = {'Poder Legislativo', 'Poder Judicial', 'Información Nacional Estadística y Geográfica', 'Comisión Nacional de los Derechos Humanos',
          'Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales', 'Instituto Nacional Electoral',
          'Tribunal Federal de Justicia Administrativa', 'Tribunales Agrarios'}

PORTADA = 'datos-administracion-publica.html'
PORTADA_TIT = 'Administración pública'
PAGINAS = [
    ('datos-administracion-publica-niveles.html', '🏢', 'Los tres niveles y lo que hacen', 'Federal, estatal y municipal: cuántas instituciones, cuánta gente y cuánto dinero',
     'Quién forma la administración pública de la Federación, de cada estado y de cada municipio, qué funciones le da la ley, cuánta gente trabaja ahí '
     'y cuánto ejerció en 2024. Con los censos de gobierno del INEGI, la Constitución y la Ley Orgánica de la Administración Pública Federal.',
     ['niveles', 'funciones', 'estados']),
    ('datos-administracion-publica-auditorias.html', '🔎', 'Quién la audita y cómo contrata', 'Las auditorías de los tres niveles y la adjudicación directa',
     'Cuántas auditorías le hicieron en 2024 sus propias contralorías y cuántas la Auditoría Superior de la Federación, qué quedó por aclarar en cada nivel '
     'y cuántos de sus contratos se dieron sin concurso.',
     ['auditorias', 'contratos']),
]
PAGINA_DE = {k: (p[0], p[2]) for p in PAGINAS for k in p[5]}
PRE = 'adm-'


def _n(v):
    return format(int(round(v)), ',')


def _m(v):
    return '$%s millones' % format(v, ',.1f')


def _mm(v):
    """Millones a miles de millones, para el texto."""
    return '$%s mil millones' % format(v / 1000.0, ',.1f')


def _o(que, fu, op=None, e=None):
    d = {'que': que, 'e': e or ('derivado' if op else 'oficial'), 'fu': fu}
    if op:
        d['op'] = op
    return d


def chequeo(base):
    """Que cada tabla sume lo que el INEGI dice en su texto, y que la base
    traiga a las 32 entidades. Si algo no cuadra, se detiene."""
    ab = sorted(e['abbr'] for e in base['estados'])
    if sorted(APE) != ab or sorted(APM_PRES) != ab:
        raise SystemExit('administración pública: las tablas no traen a las 32 entidades de la base')
    if sum(v[0] for v in APE.values()) != APE_TOT['tit'] or APE_TOT['tit'] + APF['tit'] != TOT['tit']:
        raise SystemExit('administración pública: los titulares no suman lo de la tabla 1')
    if sum(v[1] for v in APE.values()) != APE_TOT['per'] or APE_TOT['per'] + APF['per'] != TOT['per']:
        raise SystemExit('administración pública: el personal no suma lo de la tabla 3')
    if abs(sum(v[2] for v in APE.values()) - APE_TOT['pres']) > 0.2 or abs(APE_TOT['pres'] + APF['pres'] - TOT['pres']) > 0.01:
        raise SystemExit('administración pública: el presupuesto no suma lo de la gráfica 5')
    if sum(v[3] for v in APE.values()) != APE_TOT['con'] or APE_TOT['con'] + APF['con'] != TOT['con']:
        raise SystemExit('administración pública: los contratos no suman lo de la tabla 9')
    if APE_TOT['inst'] + APF['inst'] != TOT['inst']:
        raise SystemExit('administración pública: las instituciones no suman lo de la p. 3')
    if abs(sum(APM_PRES.values()) - APM['pres']) > 0.2:
        raise SystemExit('administración pública: el presupuesto municipal no suma lo de la gráfica 23')
    if abs(APM['central'] + APM['para'] - 100) > 0.05:
        raise SystemExit('administración pública: centralizadas y paramunicipales no suman 100')
    cp = base['cuenta_publica_asf']['cp2024']
    if len(cp['entidades']) != 32:
        raise SystemExit('administración pública: la Matriz de la ASF no trae a las 32 entidades')
    for x in cp['entidades']:
        t = x['total']
        if sum(d['auditorias'] for d in x['desglose']) != t['auditorias'] or abs(sum(d['porAclarar'] for d in x['desglose']) - t['porAclarar']) > 1:
            raise SystemExit('administración pública: el desglose de la ASF de %s no suma su total' % x['entidad'])
    return cp


def _norm(t):
    import unicodedata
    t = unicodedata.normalize('NFD', t)
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower().replace('estado de ', '')


def _asf_entidad(cp, nombre):
    n = _norm(nombre)
    for x in cp['entidades']:
        m = _norm(x['entidad'])
        if m == n or m.startswith(n + ' ') or n.startswith(m + ' '):
            return x
    raise SystemExit('administración pública: la Matriz de la ASF no trae a %s' % nombre)


def apf_asf(cp):
    """Lo que la ASF auditó a la Administración Pública Federal en la Cuenta
    Pública 2024: los sectores de los grupos funcionales sin el gasto
    federalizado y sin los Poderes ni los órganos autónomos (derivado)."""
    a = pa = 0
    for g in cp['grupos']:
        if g['grupo'] == 'Gasto Federalizado':
            continue
        for s in g['sectores']:
            if s['nombre'] not in NO_APF:
                a += s['auditorias']
                pa += s['porAclarar']
    return {'aud': a, 'pa': round(pa / 1e6, 1)}


def estados(base):
    """Lo de cada entidad por su clave: su administración (CNGE), la de sus
    municipios (CNGMD) y lo que la ASF le auditó a cada nivel."""
    cp = chequeo(base)
    out = {}
    for e in base['estados']:
        t, p, x, c, ad = APE[e['abbr']]
        q = _asf_entidad(cp, e['name'])
        dg = {d['ente']: d for d in q['desglose']}
        g, mu, ot = dg.get('Gobierno del Estado', {}), dg.get('Municipios', {}), dg.get('Otros', {})
        out[e['abbr']] = {
            'tit': t, 'per': p, 'pres': x, 'con': c, 'ad': ad,
            'perk': round(p * 1000.0 / e['pobPersonas'], 1),
            'presp': round(x * 1e6 / e['pobPersonas']),
            'mpres': APM_PRES[e['abbr']], 'mpresp': round(APM_PRES[e['abbr']] * 1e6 / e['pobPersonas']),
            'ga': g.get('auditorias', 0), 'gpa': round(g.get('porAclarar', 0) / 1e6, 1), 'gac': g.get('acciones', 0),
            'ma': mu.get('auditorias', 0), 'mpa': round(mu.get('porAclarar', 0) / 1e6, 1), 'mac': mu.get('acciones', 0),
            'oa': ot.get('auditorias', 0), 'opa': round(ot.get('porAclarar', 0) / 1e6, 1),
            'ta': q['total']['auditorias'], 'tpa': round(q['total']['porAclarar'] / 1e6, 1),
        }
    return out


def fuente_asf(base):
    f = base['cuenta_publica_asf']['fuentes']['MDB2024']
    cp = base['cuenta_publica_asf']['cp2024']
    return {'tx': '%s, desglose por entidad, p. %s' % (f['corto'], cp.get('paginaEntidades') or cp.get('pagina')), 'url': f['url'], 'sha256': f.get('sha256')}


def temas(base):
    """Los temas del bot y de las páginas."""
    cp = chequeo(base)
    E = estados(base)
    nom = {e['abbr']: e['name'] for e in base['estados']}
    fa = fuente_asf(base)
    af = apf_asf(cp)
    sga = sum(x['ga'] for x in E.values())
    sgp = sum(x['gpa'] for x in E.values())
    sma = sum(x['ma'] for x in E.values())
    smp = sum(x['mpa'] for x in E.values())
    t = {}
    t['niveles'] = {
        'tit': 'La administración pública en los tres niveles',
        'h': '<p>La <b>administración pública</b> es la parte del gobierno que <b>ejecuta</b>: las secretarías, los organismos y las empresas del Estado que encabeza '
             'quien gobierna. No hace leyes (eso es del Congreso) ni juzga (eso es de los tribunales). Hay una en cada nivel:</p><ul class="pa-lista">'
             '<li><b>Federal</b>: la encabeza la Presidencia. Al cierre de 2024 tenía <b>%s instituciones</b>, <b>%s personas</b> y ejerció <b>%s</b> '
             '(con PEMEX y la CFE).</li>'
             '<li><b>Estatal</b>: la encabeza cada gubernatura. Las 32 sumaban <b>%s instituciones</b>, <b>%s personas</b> y ejercieron <b>%s</b>.</li>'
             '<li><b>Municipal</b>: la encabeza cada presidencia municipal. Los municipios y alcaldías reportaron <b>%s instituciones</b> (%s de cada 100 centralizadas), '
             '<b>%s personas</b> y ejercieron <b>%s</b>.</li></ul>'
             '<p class="pa-chico">Todo sale de los censos de gobierno del INEGI, que le preguntan a cada gobierno: <b>es lo que cada uno reportó, no una auditoría</b>. '
             'Y el reporte no dice qué organismos incluyó cada gobierno en su cuenta, así que el tamaño de una administración se compara con cuidado.</p>' % (
                 _n(APF['inst']), _n(APF['per']), _mm(APF['pres']), _n(APE_TOT['inst']), _n(APE_TOT['per']), _mm(APE_TOT['pres']),
                 _n(APM['inst']), format(APM['central'], '.1f'), _n(APM['per']), _mm(APM['pres'])),
        'fu': [_o('Instituciones de la APF y de las APE al cierre de 2024', cnge(3)),
               _o('Personal adscrito a la APF y a las APE', cnge(6)),
               _o('Presupuesto ejercido por la APF y las APE en 2024', cnge(10)),
               _o('Instituciones de las administraciones municipales, por clasificación administrativa', cngmd(17, 'gráfica 14')),
               _o('Personal de las administraciones municipales', cngmd(21, 'gráfica 19')),
               _o('Presupuesto ejercido por las administraciones municipales', cngmd(25))],
        'ci': [{'v': _n(APE_TOT['per']), 'etq': 'personas en las 32 administraciones estatales', 'e': 'oficial'},
               {'v': _mm(APE_TOT['pres']), 'etq': 'ejercieron las 32 administraciones estatales en 2024', 'e': 'oficial'},
               {'v': _mm(APM['pres']), 'etq': 'ejercieron las administraciones municipales en 2024', 'e': 'oficial'}],
        'sug': ['¿Cuánta gente trabaja en el gobierno de Jalisco?', '¿Quién audita a la administración pública?', '¿Qué funciones tiene un municipio?']}
    fun = ''.join('<li>%s: <b>%s</b></li>' % (html.escape(n), _n(c)) for n, c in APM_FUN)
    t['funciones'] = {
        'tit': 'Qué funciones tiene cada nivel',
        'h': '<p><b>La federal</b> se divide en <b>centralizada</b> (la Presidencia, las secretarías y la Consejería Jurídica) y <b>paraestatal</b> '
             '(organismos descentralizados, empresas y fideicomisos), como dicen el art. 90 de la Constitución y los arts. 1 y 2 de su Ley Orgánica; '
             'esa ley reparte los asuntos de cada secretaría (art. 26 y siguientes).</p>'
             '<p><b>La de cada estado</b> la organiza su propia constitución y su ley orgánica: el art. 116 de la Constitución federal solo fija las bases. '
             'Por eso cada estado tiene un número distinto de instituciones: el que más, el Estado de México, con %s; le siguen Nuevo León (%s) y Sinaloa (%s).</p>'
             '<p><b>La del municipio</b> tiene sus servicios en la Constitución (art. 115, fr. III): agua potable, drenaje y aguas residuales; alumbrado público; '
             'limpia y residuos; mercados; panteones; rastro; calles, parques y jardines; seguridad pública y tránsito, y los demás que fije su congreso. '
             'Así repartieron los municipios sus %s instituciones en 2024, por su función principal:</p><ul class="pa-lista">%s</ul>'
             '<p class="pa-chico">La más común es «función pública»: las contralorías y oficinas de control interno, que revisan al propio municipio. '
             'Son más que los %s municipios y alcaldías que contestaron el censo.</p>' % (
                 APE_MAX_INST[0][1], APE_MAX_INST[1][1], APE_MAX_INST[2][1], _n(APM_FUN_TOT), fun, _n(APM['informaron'])),
        'fu': [_o('La administración pública federal, centralizada y paraestatal', dict(CPEUM, tx=CPEUM['tx'] + ', art. 90')),
               _o('Su organización y los asuntos de cada secretaría', dict(LOAPF, tx=LOAPF['tx'] + ', arts. 1, 2 y 26')),
               _o('Las bases de los gobiernos estatales', dict(CPEUM, tx=CPEUM['tx'] + ', art. 116')),
               _o('Los servicios públicos a cargo del municipio', dict(CPEUM, tx=CPEUM['tx'] + ', art. 115, fr. III')),
               _o('Las entidades con más instituciones estatales', cnge(3)),
               _o('Instituciones municipales por función principal', cngmd(18, 'gráfica 15'))],
        'ci': [{'v': _n(APM['inst']), 'etq': 'instituciones municipales en 2024', 'e': 'oficial'},
               {'v': _n(APM_FUN[0][1]), 'etq': 'de ellas, de control interno («función pública»)', 'e': 'oficial'}],
        'sug': ['¿Qué funciones tiene un municipio?', '¿Cuántas instituciones tiene el gobierno del Estado de México?']}
    ordp = sorted(E, key=lambda a: -E[a]['perk'])
    t['estados'] = {
        'tit': 'La administración de cada estado',
        'h': '<p>Por cada mil habitantes, el gobierno de <b>%s</b> reportó <b>%s personas</b> trabajando en su administración, y el de <b>%s</b>, <b>%s</b>. '
             'Es una diferencia demasiado grande para ser solo de tamaño: Sinaloa reportó %s personas e Hidalgo %s, aunque cada uno tiene %s y %s personas titulares '
             'de instituciones, más que casi todos. <b>El censo no dice qué dejó fuera cada gobierno</b>, así que esta comparación sirve para preguntar, no para concluir.</p>'
             '<p>La tabla trae lo que reportó cada gobierno al INEGI, lo que ejercieron sus municipios y lo que la ASF dejó por aclarar del dinero federal de cada nivel.</p>' % (
                 nom[ordp[0]], format(E[ordp[0]]['perk'], '.1f'), nom[ordp[-1]], format(E[ordp[-1]]['perk'], '.1f'),
                 _n(E['SIN']['per']), _n(E['HGO']['per']), E['SIN']['tit'], E['HGO']['tit']),
        'fu': [_o('Personas titulares por entidad', cnge(5, 'tabla 1')), _o('Personal por entidad', cnge(8, 'tabla 3')),
               _o('Presupuesto ejercido por entidad', cnge(11, 'gráfica 5')),
               _o('Presupuesto ejercido por los municipios de cada entidad', cngmd(26, 'gráfica 23')),
               _o('Personal por cada mil habitantes', cnge(8, 'tabla 3'), 'personal ÷ población de la entidad × 1,000'),
               _o('Lo que la ASF dejó por aclarar al gobierno del estado y a sus municipios', fa)],
        'sug': ['¿Cuánta gente trabaja en el gobierno de Jalisco?', '¿Qué estado tiene más burócratas por habitante?']}
    t['auditorias'] = {
        'tit': 'Quién audita a la administración pública',
        'h': '<p>Hay dos clases de auditoría. La <b>interna</b>, que hace el propio gobierno con sus contralorías y órganos internos de control, y la <b>externa</b>, '
             'que hace la Auditoría Superior de la Federación (ASF) con el dinero federal y la entidad de fiscalización de cada estado con el dinero local.</p><ul class="pa-lista">'
             '<li><b>Federal</b>: en 2024 sus autoridades de control le aplicaron <b>%s auditorías</b> a la APF (%s %% menos que en 2023). La ASF, al revisar la Cuenta Pública 2024, '
             'le hizo <b>%s</b> a las secretarías, organismos y empresas federales (sin Poderes ni autónomos) y dejó <b>%s por aclarar</b>.</li>'
             '<li><b>Estatal</b>: a las 32 administraciones estatales les aplicaron <b>%s auditorías</b>. La ASF les hizo <b>%s</b> a los gobiernos de los estados por el dinero federal que recibieron '
             'y quedaron <b>%s por aclarar</b>.</li>'
             '<li><b>Municipal</b>: a los municipios les aplicaron <b>%s auditorías</b>; la ASF hizo %s de ellas, según el censo. En la Matriz de la ASF, sus auditorías a municipios '
             'por el dinero federal suman <b>%s</b>, con <b>%s por aclarar</b>.</li></ul>'
             '<p>Quién audita a los municipios, según el censo: %s.</p>'
             '<p class="pa-chico">Un monto por aclarar no es un desfalco comprobado: es lo que, al cerrar la auditoría, no tenía papeles que acreditaran el uso del dinero, y puede solventarse. '
             'La ASF solo revisa el dinero federal; el dinero propio de cada estado y municipio lo revisa su entidad de fiscalización local, '
             'cuyos informes la plataforma todavía no ha integrado.</p>' % (
                 _n(AUD_INT['apf']), format(abs(AUD_INT['apf23_var']), '.1f'), _n(af['aud']), _m(af['pa']),
                 _n(AUD_INT['ape']), _n(sga), _m(sgp), _n(APM['aud']), _n(dict(APM_AUD)['La Auditoría Superior de la Federación']), _n(sma), _m(smp),
                 '; '.join('%s, %s' % (html.escape(n.lower()[0] + n[1:]), _n(c)) for n, c in APM_AUD)),
        'fu': [_o('Auditorías aplicadas a la APF y a las APE en 2024', cnge(21, 'gráfica 13')),
               _o('Auditorías aplicadas a los municipios, por autoridad', cngmd(72, 'gráficas 62 y 63')),
               _o('Auditorías de la ASF a la APF, por sector', dict(fa, tx=fa['tx'].split(', desglose')[0] + ', grupos funcionales'),
                  'suma de los sectores de los grupos Ingreso, Deuda, Gobierno, Desarrollo Social y Desarrollo Económico, sin los Poderes ni los órganos autónomos'),
               _o('Auditorías de la ASF a cada gobierno estatal y a sus municipios', fa, 'suma de las 32 entidades, renglones «Gobierno del Estado» y «Municipios»')],
        'ci': [{'v': _n(AUD_INT['ape']), 'etq': 'auditorías a las administraciones estatales en 2024', 'e': 'oficial'},
               {'v': _m(sgp), 'etq': 'por aclarar de los gobiernos estatales ante la ASF (CP 2024)', 'e': 'derivado'},
               {'v': _m(smp), 'etq': 'por aclarar de los municipios ante la ASF (CP 2024)', 'e': 'derivado'}],
        'sug': ['¿Cuánto dejó por aclarar el gobierno de Veracruz ante la ASF?', '¿Quién audita a los municipios?']}
    orda = sorted((a for a in E if a not in ('OAX', 'YUC')), key=lambda a: -E[a]['ad'])
    t['contratos'] = {
        'tit': 'Cómo contrata: la adjudicación directa',
        'h': '<p>En 2024 la Administración Pública Federal celebró <b>%s contratos</b>, y <b>%s de cada 100</b> fueron por <b>adjudicación directa</b>, sin concurso. '
             'La cifra federal no incluye a las empresas públicas del Estado, como PEMEX y la CFE. Las 32 administraciones estatales hicieron %s contratos.</p>'
             '<p>Entre los estados, <b>%s</b> dio por adjudicación directa %s de cada 100, <b>%s</b> %s y <b>%s</b> %s; en el otro extremo, %s dio %s y %s, %s.</p>'
             '<p class="pa-chico">Cuenta <b>contratos, no pesos</b>: muchos contratos chicos por adjudicación pesan igual que una licitación de miles de millones. '
             'Y la adjudicación directa es legal en los casos y montos que fija la ley; lo que dice esta cifra es cuánto se compra sin competir, no que haya irregularidad. %s</p>' % (
                 _n(APF['con']), format(APF['ad'], '.1f'), _n(APE_TOT['con']),
                 nom[orda[0]], format(E[orda[0]]['ad'], '.1f'), nom[orda[1]], format(E[orda[1]]['ad'], '.1f'), nom[orda[2]], format(E[orda[2]]['ad'], '.1f'),
                 nom[orda[-1]], format(E[orda[-1]]['ad'], '.1f'), nom[orda[-2]], format(E[orda[-2]]['ad'], '.1f'), CONTRATOS_NOTA),
        'fu': [_o('Contratos de la APF y de las APE, por entidad y procedimiento', cnge(31, 'tabla 9')),
               _o('Contratos celebrados en 2024; la APF, sin las empresas públicas del Estado (nota 20)', cnge(30))],
        'ci': [{'v': format(APF['ad'], '.1f') + ' %', 'etq': 'de los contratos federales, por adjudicación directa', 'e': 'oficial'},
               {'v': _n(APE_TOT['con']), 'etq': 'contratos de las 32 administraciones estatales', 'e': 'oficial'}],
        'sug': ['¿Qué estado da más contratos por adjudicación directa?', '¿Cuántos contratos da el gobierno federal sin licitar?']}
    assert sorted(t) == sorted(PAGINA_DE)
    for k, x in t.items():
        x['ir'] = [PAGINA_DE[k][0] + '#' + PRE + k, PAGINA_DE[k][1]]
        x['aqui'] = x['ir']
    return {'t': t, 'pag': [PORTADA, PORTADA_TIT]}


def chat(base):
    """Lo que lee el chat (D.apu): los temas y una fila por estado
    [abbr, titulares, personal, presupuesto, contratos, % adj. directa,
    personal por mil, presupuesto municipal, auditorías ASF al gobierno,
    por aclarar del gobierno, auditorías ASF a municipios, por aclarar de municipios]."""
    E = estados(base)
    T = temas(base)
    return {'t': T['t'], 'pag': T['pag'],
            'est': [[a, x['tit'], x['per'], x['pres'], x['con'], x['ad'], x['perk'], x['mpres'], x['ga'], x['gpa'], x['ma'], x['mpa']]
                    for a, x in sorted(E.items())],
            'fu': {'cnge': CNGE['url'], 'cngmd': CNGMD['url'], 'asf': fuente_asf(base)['url']}}


def tabla_estados(base):
    E = estados(base)
    nom = {e['abbr']: e['name'] for e in base['estados']}
    filas = ''.join(
        '<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            html.escape(nom[a]), _n(x['tit']), _n(x['per']), format(x['perk'], '.1f'), _m(x['pres']), _m(x['mpres']),
            '%d · %s' % (x['ga'], _m(x['gpa'])), '%d · %s' % (x['ma'], _m(x['mpa'])))
        for a, x in sorted(E.items(), key=lambda z: nom[z[0]]))
    return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>La administración pública de cada estado, 2024 %s; por mil habitantes %s; ASF, Cuenta Pública 2024 %s</caption>'
            '<thead><tr><th scope="col">Entidad</th><th scope="col">Titulares</th><th scope="col">Personal</th><th scope="col">Por mil hab.</th>'
            '<th scope="col">Ejerció el gobierno</th><th scope="col">Ejercieron sus municipios</th><th scope="col">ASF al gobierno: auditorías · por aclarar</th>'
            '<th scope="col">ASF a sus municipios</th></tr></thead><tbody>%s</tbody></table></div>') % (_chip('oficial'), _chip('derivado'), _chip('oficial'), filas)


def secciones(base, temas_):
    S = temas(base)
    out = []
    for k in temas_:
        x = S['t'][k]
        extra = tabla_estados(base) if k == 'estados' else ''
        out.append({'id': PRE + k, 'titulo': html.escape(x['tit']), 'texto': '', 'tarjetas': [],
                    'bloque': bloque_tema(x, extra, x['aqui'][0].split('#')[0])})
    return out
