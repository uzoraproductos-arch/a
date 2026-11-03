# -*- coding: utf-8 -*-
"""Los recursos naturales: qué se audita, a quién y con qué ley (pedido del
autor, 03-11-2026: «integrar todo el contenido de este capítulo a nuestra
plataforma, como metodología, y de ahí extraer la información que debemos
integrar en nuestra base de datos para llevar a cabo las auditorías»).

El autor subió 16 fotografías del capítulo 6, «Recursos naturales», de su
libro «Introducción al Derecho Económico» (pp. 79 a 94, tomadas el
02-11-2026; viven en docs/libro/derecho-economico/), con lo que quiere
auditar subrayado. **El libro es metodología, no fuente** (AGENTS.md §5 ter):
da el orden de los temas (renovables y no renovables, el artículo 27 y seis
ramos: hidrocarburos, electricidad, minerales radiactivos, pesca, forestal y
minería). Cada regla se cotejó contra el texto vigente, porque el libro
describe el marco de 1993-1994 (cita a la SEMIP, la SECOFI, la Secretaría de
Pesca y la SARH, y una reforma del 25-11-1993) y casi todas sus leyes fueron
abrogadas. Lo que cambió se dice al lado: es el primer punto ciego.

Documentos cotejados el 03-11-2026 (textos vigentes de la Cámara de
Diputados, LeyesBiblio, con su fecha de publicación y su última reforma):

- Constitución, arts. 25, 27 y 28 (última reforma DOF 07-10-2026).
- Ley de la Empresa Pública del Estado, Petróleos Mexicanos (DOF 18-03-2025):
  arts. 2, 3, 4, 18, 44, 51, 54 y 61, y transitorios segundo y tercero.
- Ley del Sector Hidrocarburos y Ley del Sector Eléctrico (DOF 18-03-2025),
  Ley de la Empresa Pública del Estado, CFE (DOF 18-03-2025), Ley de Minería
  (antes Ley Minera, DOF 26-06-1992, reforma 08-05-2023), Ley Reglamentaria
  del Artículo 27 Constitucional en Materia Nuclear (DOF 04-02-1985, reforma
  09-04-2012), Ley General de Pesca y Acuacultura Sustentables, Ley General
  de Desarrollo Forestal Sustentable y Ley de Aguas Nacionales.

Y las cifras de las refinerías, que ya estaban en la plataforma:

- Presidencia, Segundo Informe de Gobierno 2025-2026, p. 378 (p. 402 del
  PDF): la gráfica «Procesamiento de petróleo crudo en el Sistema Nacional de
  Refinación 2025-2026», por refinería y por mes, de septiembre de 2025 a junio
  de 2026 (elaborada por la SENER con la Base de Datos Institucional de PEMEX).
  Los valores se leyeron de las etiquetas de la gráfica; la suma de cada mes
  difiere del total publicado en uno o dos miles por el redondeo, y se dice.
- PEMEX, estados financieros consolidados 2025 (Cuenta Pública 2025, tomo
  VIII): el deterioro o la reversa de deterioro de cada refinería en 2025
  (p. 59), 2024 y 2023 (p. 63), y su valor de uso (pp. 61 y 65). Miles de
  pesos en el documento; aquí, millones con un decimal.

La página es la tarjeta «Los recursos naturales» de Aprende; el Planisferio
lee refinerias_estados() para su dimensión ambiental, y el chat lee temas()
dentro de D.san (claves rn_*).
"""

import hashlib
import html
import os

from asistente_legislativo import bloque_tema

ARCHIVO = 'aprende-recursos-naturales.html'
TITULO = 'Los recursos naturales'
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LB = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/'

LIBRO = {'tit': 'Introducción al Derecho Económico', 'cap': 'capítulo 6, «Recursos naturales»', 'pags': 'pp. 79 a 94',
         'fotos': 'docs/libro/derecho-economico/'}

# Las leyes vigentes, como las publica la Cámara de Diputados (índice de
# LeyesBiblio consultado el 03-11-2026).
LEYES = {
    'cpeum': ('Constitución Política de los Estados Unidos Mexicanos', None, '07-10-2026', 'CPEUM.pdf'),
    'lepepm': ('Ley de la Empresa Pública del Estado, Petróleos Mexicanos', '18-03-2025', None, 'LEPEPM.pdf'),
    'lsh': ('Ley del Sector Hidrocarburos', '18-03-2025', None, 'LSH.pdf'),
    'lih': ('Ley de Ingresos sobre Hidrocarburos', '11-08-2014', '28-12-2025', 'LIH.pdf'),
    'lasea': ('Ley de la Agencia Nacional de Seguridad Industrial y de Protección al Medio Ambiente del Sector Hidrocarburos', '11-08-2014', '11-05-2022', 'LANSI.pdf'),
    'lse': ('Ley del Sector Eléctrico', '18-03-2025', None, 'LSE.pdf'),
    'lepecfe': ('Ley de la Empresa Pública del Estado, Comisión Federal de Electricidad', '18-03-2025', None, 'LEPECFE.pdf'),
    'lgeo': ('Ley de Geotermia', '18-03-2025', None, 'LGeo.pdf'),
    'lnuc': ('Ley Reglamentaria del Artículo 27 Constitucional en Materia Nuclear', '04-02-1985', '09-04-2012', '207.pdf'),
    'lmin': ('Ley de Minería (antes «Ley Minera»)', '26-06-1992', '08-05-2023', 'LMin.pdf'),
    'lgpas': ('Ley General de Pesca y Acuacultura Sustentables', '24-07-2007', '01-04-2024', 'LGPAS.pdf'),
    'lgdfs': ('Ley General de Desarrollo Forestal Sustentable', '05-06-2018', '01-04-2024', 'LGDFS.pdf'),
    'lan': ('Ley de Aguas Nacionales', '01-12-1992', '11-12-2025', 'LAN.pdf'),
    'lgbn': ('Ley General de Bienes Nacionales', '20-05-2004', '14-11-2025', 'LGBN.pdf'),
}


def ley(k, donde=''):
    """La ficha de fuente de una ley vigente, con su artículo."""
    n, pub, ult, pdf = LEYES[k]
    fechas = ('publicada en el DOF el %s' % pub if pub else '') + (', última reforma DOF %s' % ult if ult and pub else
                                                                   ('última reforma DOF %s' % ult if ult else ', sin reforma'))
    return {'tx': '%s (%s)%s' % (n, fechas, (', ' + donde) if donde else ''), 'url': LB + pdf}


def ley_corta(k):
    n, pub, ult, _ = LEYES[k]
    return '%s (DOF %s%s)' % (n, pub or ult, ', reforma %s' % ult if ult and pub else '')


def _o(que, fu, e='oficial'):
    return {'que': que, 'e': e, 'fu': fu}


def _lista(items):
    return '<ul class="pa-lista">%s</ul>' % ''.join('<li>%s</li>' % i for i in items)


def _libro(pags):
    return {'tx': 'Libro del autor: %s, %s, %s (guía de temas, no fuente; fotografías en el repositorio)' % (LIBRO['tit'], LIBRO['cap'], pags),
            'url': 'https://github.com/uzoraproductos-arch/a/tree/claude/funny-turing-imtm54/' + LIBRO['fotos']}


# ---------------------------------------------------------------------------
# Los siete ramos: los seis del capítulo y el que el capítulo no trae (agua).
# 'libro' es lo que describe el libro; 'hoy', lo vigente.
# ---------------------------------------------------------------------------
RAMOS = [
    {'id': 'hidrocarburos', 'letra': 'A', 'ico': '🛢️', 'nom': 'Hidrocarburos', 'renov': 'No renovable',
     'libro': 'Ley Orgánica de Petróleos Mexicanos y Organismos Subsidiarios (DOF 16-07-1992) y Ley Reglamentaria del Artículo 27 Constitucional en el Ramo del Petróleo. Autoridad: la SEMIP.',
     'hoy': ['lepepm', 'lsh', 'lih', 'lasea'],
     'autoridad': 'Secretaría de Energía y Comisión Nacional de Energía (LSH, art. 9); la ASEA vigila la seguridad industrial y la protección al ambiente del sector.',
     'regimen': 'Propiedad de la Nación inalienable e imprescriptible; no se otorgan concesiones. Se explora y extrae por asignaciones a empresas públicas del Estado o por contratos con ellas o con particulares (art. 27, párrafo séptimo).',
     'quien': 'PEMEX, empresa pública del Estado, y particulares por contrato.',
     'auditar': 'Cuánto se extrae y cuánto recibe el Estado por cada barril (derechos y aprovechamientos de la Ley de Ingresos sobre Hidrocarburos); las asignaciones y contratos; los estados financieros de PEMEX y sus refinerías.'},
    {'id': 'electricidad', 'letra': 'B', 'ico': '⚡', 'nom': 'Energía eléctrica', 'renov': 'Según la fuente: renovable (agua, sol, viento, geotermia) o no (gas, combustóleo, carbón, uranio)',
     'libro': 'Ley del Servicio Público de Energía Eléctrica (DOF 22-12-1975): la CFE, organismo descentralizado, prestaba el servicio en exclusiva. Autoridad: la SEMIP.',
     'hoy': ['lse', 'lepecfe', 'lgeo'],
     'autoridad': 'Secretaría de Energía y Comisión Nacional de Energía (LSE, art. 3, fracciones XIII y XLVI).',
     'regimen': 'La planeación y el control del sistema eléctrico y la transmisión y distribución son exclusivos de la Nación, sin concesiones; los particulares participan en las demás actividades sin prevalecer sobre la empresa pública del Estado (art. 27, párrafo sexto).',
     'quien': 'CFE, empresa pública del Estado, y generadores particulares.',
     'auditar': 'Los estados financieros de la CFE; cuánto genera con fuentes renovables y cuánto con combustibles; los permisos a particulares.'},
    {'id': 'radiactivos', 'letra': 'C', 'ico': '☢️', 'nom': 'Minerales radiactivos y litio', 'renov': 'No renovable',
     'libro': 'Ley Reglamentaria del Artículo 27 Constitucional en Materia Nuclear (DOF 04-02-1985): sin concesiones ni contratos, solo fines pacíficos. Autoridad: la SEMIP.',
     'hoy': ['lnuc', 'lmin'],
     'autoridad': 'La ley nuclear es la misma de 1985 y todavía nombra a la «Secretaría de Energía, Minas e Industria Paraestatal» en algunos artículos; la Comisión Nacional de Seguridad Nuclear y Salvaguardias evalúa y verifica. El litio está a cargo de un organismo público descentralizado sectorizado a la Secretaría de Energía (Ley de Minería, art. 1).',
     'regimen': 'No se otorgan concesiones de minerales radiactivos ni de litio (art. 27, párrafo sexto); el litio es de utilidad pública y sus yacimientos son reserva minera (Ley de Minería, art. 5 Bis).',
     'quien': 'Solo el Estado.',
     'auditar': 'El presupuesto y los resultados del organismo del litio; que no existan concesiones ni contratos sobre esos minerales.'},
    {'id': 'pesca', 'letra': 'D', 'ico': '🐟', 'nom': 'Pesca', 'renov': 'Renovable, si se respeta su ritmo de reproducción',
     'libro': 'Ley Federal de Pesca (DOF 26-12-1986). Autoridad: la Secretaría de Pesca, con un Instituto Nacional de Pesca desconcentrado.',
     'hoy': ['lgpas'],
     'autoridad': 'Secretaría de Agricultura y Desarrollo Rural, a través de la Comisión Nacional de Acuacultura y Pesca (LGPAS, art. 4, fracción XLIII).',
     'regimen': 'Concesiones y permisos para pescar y cultivar (LGPAS, art. 2, fracción IX); vedas y sanciones.',
     'quien': 'Particulares, cooperativas y comunidades con concesión o permiso.',
     'auditar': 'Las concesiones y permisos otorgados, las vedas, lo que se captura frente a lo que se puede capturar sin agotar la especie, y lo que se gasta en inspección.'},
    {'id': 'forestal', 'letra': 'E', 'ico': '🌲', 'nom': 'Forestal', 'renov': 'Renovable, si se reforesta y se respeta su ritmo',
     'libro': 'Ley Forestal (DOF 22-12-1992). Autoridad: la Secretaría de Agricultura y Recursos Hidráulicos.',
     'hoy': ['lgdfs'],
     'autoridad': 'Secretaría de Medio Ambiente y Recursos Naturales y Comisión Nacional Forestal, organismo descentralizado (LGDFS, arts. 7 y 15).',
     'regimen': 'Autorizaciones de aprovechamiento de recursos forestales (LGDFS); vedas, reservas y parques nacionales, y la PROFEPA inspecciona y sanciona.',
     'quien': 'Ejidos, comunidades y particulares con autorización.',
     'auditar': 'Las autorizaciones de aprovechamiento, la reforestación pagada frente a la que sobrevive, los programas de la CONAFOR y lo que la PROFEPA inspecciona y sanciona.'},
    {'id': 'mineria', 'letra': 'F', 'ico': '⛏️', 'nom': 'Minería', 'renov': 'No renovable',
     'libro': 'Ley Reglamentaria del Artículo 27 Constitucional en Materia Minera (DOF 22-12-1975), con el Consejo de Recursos Minerales y la Comisión de Fomento Minero, y empresas de participación estatal mayoritaria con acciones serie «A» del Gobierno Federal (al menos 51 %). Autoridad: la SEMIP.',
     'hoy': ['lmin'],
     'autoridad': 'Secretaría de Economía (Ley de Minería, art. 1) y el Servicio Geológico Mexicano, organismo descentralizado con sede en Pachuca (art. 9), que heredó la tarea del Consejo de Recursos Minerales.',
     'regimen': 'Concesiones de 30 años, prorrogables una vez por 25 (art. 15); desde 2023 se entregan a quien gana el concurso (art. 14 Bis). Son causa de utilidad pública, así que el Estado puede expropiar.',
     'quien': 'Particulares con concesión y empresas en que participa el Estado.',
     'auditar': 'Las concesiones (quién, dónde, cuánto tiempo), los derechos que pagan, lo que de esos derechos regresa a las regiones mineras y el daño ambiental de las minas activas y abandonadas.'},
    {'id': 'agua', 'letra': '+', 'ico': '💧', 'nom': 'Agua (no está en el capítulo)', 'renov': 'Renovable, si no se extrae más de lo que se recarga',
     'libro': 'El capítulo no trae el agua, aunque el artículo 27 la regula en el mismo párrafo que los minerales.',
     'hoy': ['lan'],
     'autoridad': 'Comisión Nacional del Agua, órgano desconcentrado de la SEMARNAT (Ley de Aguas Nacionales, art. 3).',
     'regimen': 'Las aguas nacionales se usan por concesión o asignación del Ejecutivo Federal (art. 27, párrafo sexto); el Ejecutivo puede vedar zonas.',
     'quien': 'Particulares, industrias, municipios y organismos de agua con título.',
     'auditar': 'Los títulos de concesión, la disponibilidad de cada acuífero, lo que pagan los grandes usuarios y las crisis de agua que ya registra la plataforma.'},
]


# ---------------------------------------------------------------------------
# Las refinerías: el Sistema Nacional de Refinación.
# ---------------------------------------------------------------------------
MES_LARGO = {'sep-25': 'septiembre de 2025', 'oct-25': 'octubre de 2025', 'nov-25': 'noviembre de 2025', 'dic-25': 'diciembre de 2025',
             'ene-26': 'enero de 2026', 'feb-26': 'febrero de 2026', 'mar-26': 'marzo de 2026', 'abr-26': 'abril de 2026',
             'may-26': 'mayo de 2026', 'jun-26': 'junio de 2026'}
MESES = ['sep-25', 'oct-25', 'nov-25', 'dic-25', 'ene-26', 'feb-26', 'mar-26', 'abr-26', 'may-26', 'jun-26']
# Total del SNR publicado en la gráfica, mes por mes.
TOTAL_SNR = [946, 1043, 1144, 1221, 1058, 1190, 1178, 1068, 941, 1017]
# id, nombre, sede, entidad, crudo procesado por mes (miles de barriles
# diarios, de la gráfica), deterioro (−) o reversa (+) en millones de pesos
# 2025, 2024 y 2023 (None: no figura en la nota), y valor de uso 2025 y 2024.
REFINERIAS = [
    ('cadereyta', 'Refinería Cadereyta', 'Cadereyta Jiménez, Nuevo León', 'NL',
     [98, 146, 169, 180, 152, 163, 173, 165, 172, 149], -4339.8, None, None, 24735.3, 38491.0),
    ('madero', 'Refinería Madero', 'Ciudad Madero, Tamaulipas', 'TAM',
     [92, 101, 104, 102, 101, 111, 118, 110, 93, 102], -624.4, -6369.7, -10125.6, None, None),
    ('minatitlan', 'Refinería Minatitlán', 'Minatitlán, Veracruz', 'VER',
     [91, 76, 124, 129, 125, 117, 124, 119, 57, 50], -315.6, -16652.1, 4615.4, None, None),
    ('salamanca', 'Refinería Salamanca', 'Salamanca, Guanajuato', 'GTO',
     [81, 98, 93, 116, 116, 136, 123, 56, 94, 128], None, 0.4, 5750.3, 28082.8, 38826.3),
    ('salina-cruz', 'Refinería Salina Cruz', 'Salina Cruz, Oaxaca', 'OAX',
     [145, 224, 197, 210, 137, 207, 202, 207, 124, 202], -9346.0, -7270.8, None, 10680.1, 20203.7),
    ('tula', 'Refinería Tula (Miguel Hidalgo)', 'Tula de Allende, Hidalgo', 'HGO',
     [248, 208, 249, 221, 222, 252, 250, 263, 257, 243], 11780.7, -33661.6, -13.8, 43042.4, 18074.8),
    ('olmeca', 'Refinería Olmeca (Dos Bocas)', 'Paraíso, Tabasco', 'TAB',
     [191, 192, 207, 263, 206, 205, 187, 147, 144, 141], None, None, None, None, None),
]
INF = {'tx': 'Presidencia de la República, Segundo Informe de Gobierno 2025-2026, gráfica «Procesamiento de petróleo crudo en el Sistema Nacional de Refinación 2025-2026», '
             'p. 378 (p. 402 del PDF), elaborada por la SENER con la Base de Datos Institucional de PEMEX',
       'url': 'https://www.segundoinformedegobierno.gob.mx/gmx_media/2-ig-informe-consolidado-final_01_09_2026',
       'archivo': 'investigaciones/entregas/Presidencia_SegundoInformeGobierno2026.pdf',
       'sha256': 'cc95e5ade7cb306b734e9dc1e61e1defcba14c444e5705de24be6ca6e115fa9d'}
EF = {'tx': 'Petróleos Mexicanos, estados financieros consolidados 2025, notas (Cuenta Pública 2025, tomo VIII)',
      'url': 'https://www.cuentapublica.hacienda.gob.mx/work/models/CP/2025/tomo/VIII/52TYY.05.DAR.pdf',
      'archivo': 'investigaciones/costo-vivo/PEMEX_EstadosFinancierosConsolidados2025.pdf',
      'sha256': '0a6fe9e89e0d94714ea441134ac3c1ee7446c4c4713baaf9e62d8ebd554b86b2'}


def _huella(doc):
    """Si el documento está en el repositorio, su huella debe coincidir."""
    p = os.path.join(RAIZ, doc['archivo'])
    if os.path.exists(p):
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        if h != doc['sha256']:
            raise SystemExit('recursos_naturales: %s cambió (huella %s…)' % (doc['archivo'], h[:12]))


def _f(d, pag):
    return {'tx': '%s, %s' % (d['tx'], pag), 'url': d['url']}


def refinerias():
    """Las siete refinerías con sus cifras y lo derivado: el promedio de los
    diez meses (media aritmética) y el lugar en junio de 2026."""
    _huella(INF)
    _huella(EF)
    out = []
    for i, (k, n, sede, a, m, d25, d24, d23, vu25, vu24) in enumerate(REFINERIAS):
        if len(m) != len(MESES):
            raise SystemExit('recursos_naturales: %s no trae los %d meses' % (k, len(MESES)))
        out.append({'id': k, 'n': n, 'sede': sede, 'a': a, 'm': m, 'jun': m[-1], 'prom': round(sum(m) / len(m), 1),
                    'max': max(m), 'mmax': MES_LARGO[MESES[m.index(max(m))]], 'd25': d25, 'd24': d24, 'd23': d23, 'vu25': vu25, 'vu24': vu24})
    # La suma de las etiquetas de cada mes contra el total publicado: el
    # redondeo de la gráfica deja hasta 2 miles de diferencia, nunca más.
    for j, tot in enumerate(TOTAL_SNR):
        s = sum(r['m'][j] for r in out)
        if abs(s - tot) > 2:
            raise SystemExit('recursos_naturales: %s suma %d y el Informe dice %d' % (MESES[j], s, tot))
    # Olmeca: el promedio de la gráfica debe dar los 188 del texto del Informe.
    if round(next(r for r in out if r['id'] == 'olmeca')['prom']) != 188:
        raise SystemExit('recursos_naturales: el promedio de Olmeca ya no da 188 mil barriles diarios')
    orden = sorted(out, key=lambda r: -r['jun'])
    for r in out:
        r['lug'] = orden.index(r) + 1
    return out


def refinerias_estados():
    """Para el Planisferio: la refinería de cada entidad (hoy hay una o
    ninguna por entidad)."""
    out = {}
    for r in refinerias():
        if r['a'] in out:
            raise SystemExit('recursos_naturales: %s ya tiene refinería; el Planisferio suma una por entidad' % r['a'])
        out[r['a']] = r
    return out


def _mdps(v):
    if v is None:
        return '—'
    return ('−' if v < 0 else '+') + '$' + format(abs(v), ',.1f') + ' mdp'


def _chip(e, pend=None):
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, ' data-pend="%s"' % pend if pend else '', e)


def tabla_refinerias():
    R = refinerias()
    filas = ''.join(
        '<tr><th scope="row">%s<br><small>%s</small></th><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s<br><small>%s</small></td>'
        '<td class="num-tabular">%s</td><td class="num-tabular">%s</td></tr>' % (
            html.escape(r['n']), html.escape(r['sede']), format(r['jun'], ','), format(r['prom'], ',.1f'), format(r['max'], ','), r['mmax'],
            _mdps(r['d25']) if r['d25'] is not None else ('no la consolida como unidad propia' if r['id'] == 'olmeca' else 'no figura'),
            _mdps(r['d24']) if r['d24'] is not None else ('—' if r['id'] == 'olmeca' else 'no figura'))
        for r in sorted(R, key=lambda x: -x['jun']))
    s_jun = sum(r['jun'] for r in R)
    return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>El Sistema Nacional de Refinación, refinería por refinería '
            '(miles de barriles diarios de crudo procesado y millones de pesos)</caption>'
            '<thead><tr><th scope="col">Refinería</th><th scope="col">Junio 2026 %s</th><th scope="col">Promedio sep-25 a jun-26 %s</th>'
            '<th scope="col">Su mejor mes %s</th><th scope="col">Valor perdido (−) o recuperado (+) en libros, 2025 %s</th><th scope="col">Igual, 2024 %s</th></tr></thead>'
            '<tbody>%s</tbody><tfoot><tr><th scope="row">Las siete</th><td class="num-tabular">%s</td><td colspan="4"><small>La suma de las etiquetas da %s; '
            'el Informe publica %s. La diferencia es redondeo de la gráfica.</small></td></tr></tfoot></table></div>') % (
        _chip('oficial'), _chip('derivado'), _chip('oficial'), _chip('oficial'), _chip('oficial'), filas,
        format(s_jun, ','), format(s_jun, ','), format(TOTAL_SNR[-1], ','))


def tabla_ramos():
    filas = ''.join(
        '<tr><th scope="row"><span aria-hidden="true">%s</span> %s. %s<br><small>%s</small></th><td>%s</td><td>%s<br><small>%s</small></td><td>%s</td><td>%s</td></tr>' % (
            r['ico'], r['letra'], html.escape(r['nom']), html.escape(r['renov']), html.escape(r['libro']),
            '<br>'.join(html.escape(ley_corta(k)) for k in r['hoy']), html.escape(r['autoridad']), html.escape(r['regimen']), html.escape(r['auditar']))
        for r in RAMOS)
    return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Los ramos del capítulo: lo que dice el libro y lo que rige hoy</caption>'
            '<thead><tr><th scope="col">Ramo</th><th scope="col">Lo que describe el libro (1993-1994)</th><th scope="col">Lo que rige hoy y quién lo aplica</th>'
            '<th scope="col">Cómo se explota</th><th scope="col">Qué auditar</th></tr></thead><tbody>%s</tbody></table></div>') % filas


def temas():
    """Los temas del bot y de la página, con el mismo texto."""
    R = refinerias()
    por = {r['id']: r for r in R}
    jun = sorted(R, key=lambda r: -r['jun'])
    t = {}
    t['rn_capitulo'] = {
        'tit': 'Los recursos naturales: renovables y no renovables',
        'h': '<p>Para la economía, un <b>recurso</b> es lo que permite producir bienes y servicios: <b>tierra, trabajo y capital</b>. La «tierra» incluye a los '
             '<b>recursos naturales</b>, lo que se encuentra en la naturaleza y no se fabrica.</p>'
             '<p>Se dividen en dos, y la diferencia cambia lo que se audita:</p>%s'
             '<p>La Constitución dice de quién son: la propiedad de las tierras y aguas corresponde <b>originariamente a la Nación</b>, y a ella le toca el '
             '<b>dominio directo</b> de los minerales, el petróleo y los hidrocarburos, la plataforma continental y el espacio aéreo (art. 27, párrafos primero y cuarto). '
             'Por eso su explotación es asunto de dinero público aunque la haga un particular.</p>' % _lista([
                 '<b>No renovables</b> (petróleo, gas, oro, plata, litio, uranio): lo que se saca no vuelve. La pregunta del auditor es <b>cuánto queda, cuánto se saca '
                 'y cuánto recibe el Estado por cada unidad</b> antes de que se agote.',
                 '<b>Renovables</b> (bosques, pesca, agua, tierras de labor): se reponen, pero solo si no se aprovechan más rápido de lo que se regeneran. La pregunta es '
                 '<b>si se respeta ese ritmo</b>: vedas, permisos, reforestación y acuíferos sobreexplotados.']),
        'ci': [{'v': '7', 'etq': 'ramos que revisa la plataforma: los seis del libro y el agua', 'e': 'derivado'}],
        'fu': [_o('Tierra, trabajo y capital; renovables y no renovables', _libro('p. 80'), 'derivado'),
               _o('Propiedad originaria de la Nación y dominio directo (art. 27, párrafos primero y cuarto)', ley('cpeum', 'art. 27'))],
        'sug': ['¿Quién puede explotar los recursos naturales?', '¿Qué se audita en PEMEX?', '¿Cuánto crudo procesa cada refinería?']}
    t['rn_regimen'] = {
        'tit': 'Las tres vías para explotar un recurso de la Nación, y las tres auditorías',
        'h': '<p>El libro lo resume en una frase que conviene subrayar: el Estado explota sus recursos <b>de manera directa o indirecta</b>, por medio de organismos '
             'descentralizados, de empresas en que participa o <b>otorgando concesiones a particulares</b>. Hoy la Constitución lo dice así:</p>%s'
             '<p>Cada vía se audita distinto:</p>%s'
             '<p>Los estados y los municipios también pueden adquirir y tener los inmuebles que necesitan para sus servicios públicos (art. 27, fracción VI): ese patrimonio '
             'también es dinero público y se audita en su cuenta.</p>' % (
                 _lista(['<b>Dominio inalienable e imprescriptible:</b> los recursos de la Nación no se venden ni se pierden con el tiempo (art. 27, párrafo sexto); los particulares solo los aprovechan '
                         '<b>por concesión</b> del Ejecutivo Federal (art. 27, párrafo sexto).',
                         '<b>Sin concesiones:</b> el petróleo y los hidrocarburos, los minerales radiactivos y el litio, y la planeación, el control, la transmisión y la '
                         'distribución de la electricidad (art. 27, párrafos sexto y séptimo).',
                         '<b>Áreas estratégicas:</b> las ejerce el Estado en exclusiva, por medio de <b>empresas públicas del Estado</b> que el Gobierno Federal no puede dejar de '
                         'poseer ni controlar (arts. 25, párrafo quinto, y 28, párrafo cuarto). Desde la reforma del DOF 31-10-2024 PEMEX y la CFE ya no son «empresas '
                         'productivas»: son empresas públicas del Estado.']),
                 _lista(['<b>Directa</b> (una dependencia): su Cuenta Pública y la Auditoría Superior de la Federación.',
                         '<b>Por una empresa pública del Estado</b> (PEMEX, CFE): sus estados financieros, su Comité de Auditoría, su auditoría interna y externa, y la ASF '
                         '(Ley de PEMEX, arts. 54 y 61).',
                         '<b>Por concesión</b> (minas, agua, pesca, bosques): el título, lo que paga el concesionario y lo que inspecciona la PROFEPA. Que una empresa '
                         'tenga una concesión no es una irregularidad; lo que se audita es que pague y cumpla.'])),
        'fu': [_o('Explotación directa, por organismos, empresas de participación estatal o concesiones', _libro('p. 80'), 'derivado'),
               _o('Concesiones; sin concesiones en hidrocarburos, radiactivos, litio y la red eléctrica (art. 27, párrafos sexto y séptimo)', ley('cpeum', 'art. 27')),
               _o('Áreas estratégicas y empresas públicas del Estado (arts. 25 y 28)', ley('cpeum', 'arts. 25 y 28')),
               _o('Inmuebles de estados y municipios para servicios públicos (art. 27, fracción VI)', ley('cpeum', 'art. 27, fr. VI')),
               _o('Vigilancia y auditoría de PEMEX y competencia de la ASF (arts. 54 y 61)', ley('lepepm', 'arts. 54 y 61'))],
        'sug': ['¿Qué ley rige la minería?', '¿Qué se audita en PEMEX?', '¿Qué cambió en PEMEX desde 2025?']}
    t['rn_ramos'] = {
        'tit': 'Los seis ramos del libro, y lo que rige hoy',
        'h': '<p>El capítulo recorre seis ramos: hidrocarburos, energía eléctrica, minerales radiactivos, pesca, forestal y minería. De cada uno da su ley, el objeto y '
             'el sujeto de la ley, la autoridad y el procedimiento. Es buen método, pero el libro describe el marco de <b>1993-1994</b>: de las leyes que cita, solo la '
             'nuclear sigue vigente. La tabla pone al lado lo que rige hoy, cotejado contra el texto vigente de la Cámara de Diputados, y agrega el agua, que el capítulo no trae.</p>',
        'ci': [{'v': '1 de 7', 'etq': 'leyes del libro que siguen vigentes (la nuclear de 1985)', 'e': 'derivado'}],
        'fu': [_o('Los seis ramos y sus leyes de entonces', _libro('pp. 79 a 94'), 'derivado')] + [_o(LEYES[k][0], ley(k)) for k in
                                                                                                  ('lepepm', 'lsh', 'lse', 'lepecfe', 'lnuc', 'lmin', 'lgpas', 'lgdfs', 'lan')],
        'sug': ['¿Qué ley rige la pesca?', '¿Se puede dar una concesión de litio?', '¿Quién audita a PEMEX?']}
    t['rn_pemex'] = {
        'tit': 'PEMEX: lo que dice el libro y lo que es hoy',
        'h': '<p>El libro describe a PEMEX como un organismo descentralizado con cuatro organismos subsidiarios (Exploración y Producción, Refinación, Gas y Petroquímica '
             'Básica, y Petroquímica). Desde entonces cambió tres veces de forma. Hoy:</p>%s'
             '<p>La pregunta que deja el libro sigue viva: PEMEX tiene a su cargo la <b>dirección estratégica</b> de toda la industria petrolera del Estado y puede contratar '
             'obra y servicios. Por eso sus contratos, su deuda y sus refinerías son de lo más importante que audita la plataforma.</p>' % _lista([
                 '<b>Qué es:</b> una <b>empresa pública del Estado</b>, sectorizada a la Secretaría de Energía, con personalidad jurídica y patrimonio propios (Ley de PEMEX, art. 2). '
                 'Sus actividades no constituyen monopolio (art. 4).',
                 '<b>Sus subsidiarias se extinguieron:</b> Pemex Exploración y Producción, Pemex Transformación Industrial y Pemex Logística dejaron de existir por ministerio de ley, '
                 'y PEMEX se quedó con sus derechos y obligaciones (transitorio tercero). Hoy puede tener empresas filiales (art. 62).',
                 '<b>Su Consejo de Administración:</b> ocho personas. Lo preside la Secretaría de Energía, con voto de calidad; lo integran Hacienda, Medio Ambiente, Ciencia, '
                 'la Dirección General de la CFE y tres consejeros independientes que propone la Presidencia y ratifica el Senado (art. 18). En el libro eran 11 y cinco venían '
                 'del sindicato petrolero: hoy el sindicato ya no tiene asiento.',
                 '<b>Su director general</b> lo nombra la Presidencia, y no puede ser cónyuge, concubino ni pariente, sin límite de grado, de ningún consejero (art. 51).',
                 '<b>Quién la vigila:</b> el Comité de Auditoría (solo tres consejeros independientes, art. 44), la Auditoría Interna y la externa (art. 54). La Auditoría Superior '
                 'de la Federación es competente para fiscalizarla (art. 61).']),
        'ci': [{'v': '8', 'etq': 'personas en su Consejo de Administración (en el libro, 11)', 'e': 'oficial'},
               {'v': '3', 'etq': 'subsidiarias extinguidas por la ley de 2025', 'e': 'oficial'}],
        'fu': [_o('PEMEX y sus cuatro organismos subsidiarios; conducción central y dirección estratégica; consejo de 11 (6 del Estado y 5 del sindicato)', _libro('pp. 83 y 84'), 'derivado'),
               _o('Naturaleza, objeto y no monopolio (arts. 2, 3 y 4)', ley('lepepm', 'arts. 2 a 4')),
               _o('Consejo de Administración (art. 18) y Comité de Auditoría (art. 44)', ley('lepepm', 'arts. 18 y 44')),
               _o('Dirección General y su impedimento por parentesco (art. 51)', ley('lepepm', 'art. 51')),
               _o('Vigilancia, auditoría y la ASF (arts. 54 y 61)', ley('lepepm', 'arts. 54 y 61')),
               _o('Extinción de las subsidiarias y abrogación de la Ley de PEMEX de 2014 (transitorios segundo y tercero)', ley('lepepm', 'transitorios'))],
        'sug': ['¿Quién audita a PEMEX?', '¿Cuánto crudo procesa cada refinería?', '¿Qué refinería perdió más valor?']}
    peor24 = min((r for r in R if r['d24'] is not None), key=lambda r: r['d24'])
    peor25 = min((r for r in R if r['d25'] is not None), key=lambda r: r['d25'])
    t['rn_refinerias'] = {
        'tit': 'Las refinerías de PEMEX: cuánto procesan y cuánto valen en sus libros',
        'h': ('<p>El Sistema Nacional de Refinación tiene <b>siete refinerías</b>. En junio de 2026 la que más crudo procesó fue la <b>%s</b>, con %s mil barriles diarios %s, '
              'y la que menos, la <b>%s</b>, con %s mil %s. De septiembre de 2025 a junio de 2026 el promedio de Olmeca fue de %s mil barriles diarios %s; el texto del Informe, redondeado, dice 188.</p>'
              '<p>Lo que casi nadie cruza está en los estados financieros de PEMEX: cada año revisa si cada refinería todavía vale lo que dicen sus libros. Si espera recuperar menos, '
              'reconoce un <b>deterioro</b> (pierde valor); si mejora, una <b>reversa</b>. En 2024 la %s perdió %s %s. En 2025 la %s recuperó %s %s por su coquizadora, y la %s perdió %s %s.</p>'
              '<p>Dos cosas que no dicen esas cifras: el deterioro es una <b>estimación contable</b> con el precio, el tipo de cambio y la tasa que supone PEMEX, no dinero que salió de la caja; '
              'y Olmeca no aparece en esa nota porque es de una filial y PEMEX la arrienda. Lo que costó Olmeca ya lo audita la plataforma en su investigación.</p>') % (
            jun[0]['n'], jun[0]['jun'], _chip('oficial'), jun[-1]['n'], jun[-1]['jun'], _chip('oficial'), format(por['olmeca']['prom'], '.1f'), _chip('derivado'),
            peor24['n'], _mdps(peor24['d24']).lstrip('−'), _chip('oficial'), por['tula']['n'], _mdps(por['tula']['d25']).lstrip('+'), _chip('oficial'),
            peor25['n'], _mdps(peor25['d25']).lstrip('−'), _chip('oficial')),
        'ci': [{'v': '7', 'etq': 'refinerías en el Sistema Nacional de Refinación', 'e': 'oficial'},
               {'v': format(TOTAL_SNR[-1], ',') + ' mil', 'etq': 'barriles diarios de crudo procesados en junio de 2026', 'e': 'oficial'}],
        'fu': [_o('Crudo procesado por refinería y por mes, sep-25 a jun-26; el promedio de cada una es la media de los diez meses (nuestra)', _f(INF, '')),
               _o('Deterioro y reversa de 2025 por refinería', _f(EF, 'p. 59')),
               _o('Deterioro y reversa de 2024 y 2023 por refinería', _f(EF, 'p. 63')),
               _o('Valor de uso de cada refinería, 2025, 2024 y 2023', _f(EF, 'pp. 61 y 65'))],
        'sug': ['¿Cuánto crudo procesa la refinería de Salina Cruz?', '¿Qué es el deterioro de un activo?', '¿Cuánto costó Dos Bocas?']}
    t['rn_auditar'] = {
        'tit': 'Lo que el autor subrayó: la guía para auditar recursos naturales',
        'h': '<p>Lo subrayado en el capítulo marca la ruta. Cada punto, con lo que ya tiene la plataforma y lo que falta:</p>%s' % _lista([
            '<b>«Los recursos naturales pertenecen al dominio del Estado».</b> Primero se pregunta de quién es el recurso y por cuál de las tres vías se explota: eso dice a quién auditar.',
            '<b>«Organismos descentralizados, empresas de participación estatal, concesiones».</b> Las paraestatales (PEMEX, CFE, el organismo del litio, el Servicio Geológico Mexicano, '
            'la CONAFOR) rinden estados financieros; las concesiones, títulos y pagos.',
            '<b>«Personalidad jurídica y patrimonio propios».</b> Una empresa del Estado con patrimonio propio puede perder valor: por eso la plataforma lee el deterioro de cada refinería.',
            '<b>«Pemex-Exploración y Producción», «Gas y Petroquímica Básica».</b> Ya no existen: hoy todo está en PEMEX y sus filiales, y una cifra de una subsidiaria vieja no se compara con la de hoy sin decirlo.',
            '<b>«Dirección estratégica… contratos de obra y de prestación de servicios… un Director General designado por el Presidente».</b> Los contratos de PEMEX se buscan en ComprasMX '
            'y en las auditorías de la ASF; el nombramiento se revisa con la regla de parentesco del art. 51.',
            '<b>«Las entidades federativas y municipios pueden adquirir los bienes raíces necesarios para los servicios públicos».</b> Su patrimonio inmobiliario está en su cuenta pública.']),
        'fu': [_o('Los pasajes subrayados por el autor', _libro('pp. 80, 82 y 83'), 'derivado'),
               _o('Dirección General e impedimento por parentesco (art. 51)', ley('lepepm', 'art. 51'))],
        'sug': ['¿Quién puede explotar los recursos naturales?', '¿Qué cambió en PEMEX desde 2025?', '¿Qué refinería perdió más valor?']}
    t['rn_ciegos'] = {
        'tit': 'Los puntos ciegos al auditar recursos naturales',
        'h': '<p>Lo que conviene tener a la vista antes de sacar una conclusión:</p>%s' % _lista([
            '<b>Un libro de derecho envejece con la ley.</b> El capítulo cita a la SEMIP, la SECOFI y la Secretaría de Pesca, que ya no existen, y leyes abrogadas. Toda cita se coteja con el texto vigente.',
            '<b>La ley vigente también envejece.</b> La ley nuclear de 1985 sigue nombrando a la «Secretaría de Energía, Minas e Industria Paraestatal».',
            '<b>Procesar no es producir.</b> El crudo que entra a una refinería no es la gasolina que sale: la gasolina depende de cada planta.',
            '<b>Un deterioro no es dinero perdido en efectivo.</b> Es una estimación de lo que la refinería dejará de generar, con supuestos que PEMEX pone y que cambian cada año.',
            '<b>Un estado sin refinería no es un estado sin problema ambiental.</b> El mapa marca dónde hay refinerías, no dónde hay daño. Las minas, el agua y los bosques de cada estado '
            'todavía no tienen cifra en la plataforma.',
            '<b>El libro no trae el agua,</b> que es un recurso renovable en crisis en varios estados y se explota por concesión.']),
        'fu': [_o('La ley nuclear vigente todavía nombra a la SEMIP', ley('lnuc', 'art. 3')),
               _o('Las leyes que cita el libro', _libro('pp. 83 a 94'), 'derivado')],
        'sug': ['¿Qué es el deterioro de un activo?', '¿Qué se audita en PEMEX?', '¿Qué ley rige el agua?']}
    # Una ficha por refinería, para que el chat conteste la que se le pide.
    for r in R:
        val = ('<p>En sus libros, PEMEX le reconoció en 2025 %s %s y en 2024 %s %s (−: perdió valor; +: lo recuperó). Es una estimación de lo que espera que genere, '
               'no dinero que salió de la caja.</p>') % (
            _mdps(r['d25']) if r['d25'] is not None else 'nada (no figura en la nota)', _chip('oficial') if r['d25'] is not None else '',
            _mdps(r['d24']) if r['d24'] is not None else 'nada', _chip('oficial') if r['d24'] is not None else '')
        if r['id'] == 'olmeca':
            val = ('<p>No aparece en la nota de deterioro de PEMEX: la refinería es de una filial, PTI Infraestructura de Desarrollo, y PEMEX se la arrienda. '
                   'Lo que costó construirla ya lo audita la plataforma: <a href="auditoria-dos-bocas.html">la investigación de Dos Bocas</a>.</p>')
        t['rn_ref_' + r['id'].replace('-', '_')] = {
            'tit': '%s: cuánto crudo procesa' % r['n'],
            'h': ('<p>La <b>%s</b>, en %s, procesó <b>%s mil barriles diarios</b> de petróleo crudo en junio de 2026 %s: el lugar %d de las siete refinerías de PEMEX. '
                  'De septiembre de 2025 a junio de 2026 promedió %s mil %s, y su mejor mes fue %s, con %s mil %s.</p>%s'
                  '<p>Procesar crudo no es producir gasolina, y un mes bajo puede ser mantenimiento. Su capacidad instalada sigue %s.</p>') % (
                r['n'].replace('Refinería ', 'refinería '), r['sede'], format(r['jun'], ','), _chip('oficial'), r['lug'], format(r['prom'], '.1f'), _chip('derivado'),
                r['mmax'], format(r['max'], ','), _chip('oficial'), val, _chip('pendiente', 'refinerias-capacidad')),
            'ci': [{'v': '%s mil' % format(r['jun'], ','), 'etq': 'barriles diarios de crudo, junio de 2026', 'e': 'oficial'},
                   {'v': '%s mil' % format(r['prom'], '.1f'), 'etq': 'promedio de sep-25 a jun-26', 'e': 'derivado', 'op': 'media aritmética de los diez meses'}],
            'fu': [_o('Crudo procesado por refinería y por mes', _f(INF, ''))] + ([] if r['id'] == 'olmeca' else [_o('Deterioro y reversa por refinería, 2025 y 2024', _f(EF, 'pp. 59 y 63'))]),
            'sug': ['¿Cuánto crudo procesa cada refinería?', '¿Qué refinería perdió más valor?', '¿Quién audita a PEMEX?']}
    for k, x in t.items():
        x['ir'] = [ARCHIVO + '#' + (k.replace('_', '-') if not k.startswith('rn_ref_') else 'rn-refinerias'), TITULO]
        x['aqui'] = x['ir']
    return t


SECCIONES = [('rn_capitulo', 'Renovables y no renovables'), ('rn_regimen', 'Las tres vías y las tres auditorías'),
             ('rn_ramos', 'Los seis ramos, ayer y hoy'), ('rn_pemex', 'PEMEX, ayer y hoy'),
             ('rn_refinerias', 'Las refinerías de PEMEX'), ('rn_auditar', 'Lo subrayado: la guía del auditor'),
             ('rn_ciegos', 'Los puntos ciegos')]


def secciones():
    T = temas()
    extra = {'rn_ramos': tabla_ramos(),
             'rn_refinerias': tabla_refinerias() + '<p class="leg-mas"><a href="planisferio.html?d=ambiental">🗺️ Verlas en el Planisferio ➔</a> · '
                                                   '<a href="auditoria-dos-bocas.html">📖 La investigación de Dos Bocas ➔</a> · '
                                                   '<a href="auditoria-refineria-tula.html">📖 La de la refinería de Tula ➔</a></p>'}
    return [{'id': k.replace('_', '-'), 'titulo': html.escape(tit), 'texto': '', 'tarjetas': [],
             'bloque': bloque_tema(T[k], extra.get(k, ''), ARCHIVO)} for k, tit in SECCIONES]


ENTRADA = ('El capítulo de recursos naturales del libro del autor, «Introducción al Derecho Económico», convertido en método de auditoría y puesto al día: '
           'qué recursos se renuevan y cuáles se agotan, de quién son, quién los explota y con qué ley, y a quién se audita en cada caso. '
           'Cada regla está cotejada contra el texto vigente, porque el libro describe las leyes de 1993-1994. Incluye la sección de PEMEX y sus siete refinerías, '
           'que también se ven en el Planisferio. Es la misma información con que contesta Pregúntale al Auditor.')


def pagina():
    """El diccionario de la página para apartados.py (tarjeta de Aprende)."""
    return {
        'archivo': ARCHIVO, 'menu': TITULO, 'menu_archivo': 'aprende.html',
        'padre': ('aprende.html', 'Aprende'),
        'icono': '🌎', 'titulo': TITULO, 'lema': 'Renovables y no renovables, PEMEX y sus refinerías: qué se audita y con qué ley',
        'estilos': ['asistente.css'], 'entrada': ENTRADA, 'secciones': secciones(),
    }


def pendientes():
    """Para el Registro de pendientes (pendientes.py)."""
    import pendientes as P
    ap = [(ARCHIVO, 'Aprende · ' + TITULO), ('planisferio.html', 'Planisferio · dimensión ambiental')]
    return [
        {'id': 'refinerias-capacidad', 'tema': 'Recursos naturales',
         'que': 'La capacidad instalada de destilación de cada refinería de PEMEX, para medir cuánto de ella usa',
         'porque': ('El Segundo Informe da el crudo procesado por refinería y solo la capacidad de Olmeca en porcentaje (263 mil barriles diarios, 77 %). '
                    'PEMEX publica la capacidad de cada una en su Base de Datos Institucional y su anuario estadístico, pero su portal no respondió desde donde '
                    'se construye la plataforma en el cotejo del 03-11-2026. Las cifras que circulan en la prensa no se usan en su lugar.'),
         'responsable': P.PLATAFORMA, 'enlace': 'https://www.pemex.com/ri/Publicaciones/Paginas/default.aspx',
         'enlace_txt': 'PEMEX, publicaciones para inversionistas y Base de Datos Institucional', 'aparece': ap},
        {'id': 'ambiente-por-estado', 'tema': 'Recursos naturales',
         'que': 'Una cifra ambiental de cada una de las 32 entidades: concesiones mineras, acuíferos sobreexplotados, superficie forestal y denuncias ante la PROFEPA',
         'porque': ('El Informe de Actividades 2024 de la PROFEPA nombra estados pero no publica sus cifras por entidad. Las concesiones mineras (Secretaría de Economía), '
                    'la disponibilidad de los acuíferos (CONAGUA) y la superficie forestal (CONAFOR) sí se publican por entidad y la plataforma aún no las integra. '
                    'Mientras tanto el mapa ambiental solo marca dónde están las refinerías, y lo dice.'),
         'responsable': P.PLATAFORMA, 'enlace': 'https://www.inegi.org.mx/temas/ambiente/',
         'enlace_txt': 'INEGI, estadísticas de medio ambiente', 'aparece': ap},
    ]
