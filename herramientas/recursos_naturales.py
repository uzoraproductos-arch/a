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
AE = {'tx': 'Petróleos Mexicanos, Anuario Estadístico 2024, cuadro 3.6 «Capacidad de proceso por refinería, 2024»',
      'url': 'https://www.pemex.com/ri/Publicaciones/Anuario%20Estadistico%20Archivos/Anuario%20Estad%C3%ADstico%202024.pdf',
      'archivo': 'investigaciones/recursos-naturales/PEMEX_AnuarioEstadistico2024.pdf',
      'sha256': '8114ab3ab3d1fe0ca4f68a99e01ca1c7cf5f235ecad235607ee4c33b0b41c897'}
# Capacidad de destilación atmosférica de crudo al cierre de 2024, miles de
# barriles diarios (Anuario 2024, cuadro 3.6, p. 48). Sumadas dan los 1,980
# del Sistema Nacional de Refinación que publica el mismo cuadro.
CAPACIDAD = {'cadereyta': 275, 'madero': 190, 'olmeca': 340, 'minatitlan': 285, 'salamanca': 245, 'salina-cruz': 330, 'tula': 315}
CAP_SNR = 1980

# Las concesiones mineras (03-11-2026, la entrega que pidió el autor después
# de las refinerías). Secretaría de Economía, Prontuario Estadístico de la
# Minería enero-junio 2025, cuadro «Número de concesiones mineras y superficie
# por Entidad Federativa 2024», p. 20, con fuente «DGM, marzo 2024». Treinta
# entidades: la Ciudad de México y Quintana Roo no figuran en el cuadro.
PRONT = {'tx': 'Secretaría de Economía, Prontuario Estadístico de la Minería, enero-junio 2025, cuadro «Número de concesiones mineras y superficie por Entidad Federativa 2024» '
               '(fuente del cuadro: Dirección General de Minas, marzo de 2024)',
         'url': 'https://www.gob.mx/cms/uploads/attachment/file/1042764/Prontuario_Ene-Jun_2025.pdf',
         'archivo': 'investigaciones/recursos-naturales/SE_ProntuarioMineria_EneJun2025.pdf',
         'sha256': '6de85f293d5bc78f65eb9be89ef7fb089db5be5c95d5c23d64e7f86ba128e353'}
MINAS = {'AGS': (136, 49256.43), 'BC': (528, 537622.68), 'BCS': (148, 417000.27), 'CAM': (15, 2009.67), 'COAH': (1738, 914040.82),
         'COL': (258, 172590.75), 'CHIS': (47, 54220.31), 'CHIH': (3069, 1428070.42), 'DGO': (3402, 1491399.90), 'GTO': (578, 207235.44),
         'GRO': (594, 593182.55), 'HGO': (407, 125064.29), 'JAL': (1252, 708584.26), 'MÉX': (224, 140259.88), 'MICH': (691, 731218.75),
         'MOR': (45, 11681.52), 'NAY': (367, 287557.81), 'NL': (561, 114681.11), 'OAX': (286, 311578.15), 'PUE': (301, 102312.39),
         'QRO': (340, 87002.08), 'SLP': (552, 322711.8409), 'SIN': (1249, 610318.84), 'SON': (4029, 2687585.45), 'TAB': (3, 1313.00),
         'TAM': (102, 92959.99), 'TLAX': (2, 1803.00), 'VER': (78, 71089.79), 'YUC': (29, 9751.28), 'ZAC': (2200, 1186071.46)}
MINAS_TOT = (23231, 13470174)
# Lo que paga la minería por sus concesiones y lo que extrae (millones de
# pesos, enero a junio de 2025, cifras preliminares de Hacienda que reproduce
# el mismo Prontuario, p. 21): Ley Federal de Derechos, arts. 263, 268, 269 y 270.
DERECHOS = [('263', 'Por la concesión (cuota por hectárea)', 1497.3), ('268', 'Derecho especial sobre minería', 9806.5),
            ('269', 'Derecho adicional sobre minería', 6.0), ('270', 'Derecho extraordinario sobre minería (oro, plata y platino)', 982.1)]
DERECHOS_TOT = 12291.8
# Segundo Informe de Gobierno, p. 444 (p. 468 del PDF): el corte al 30 de
# junio de 2026, nacional y de cuatro estados; las diez entidades que dan el
# 94.9 % del valor de la producción (nota 1/) y las 17 que dan el 5.2 % (2/).
MIN26 = {'SON': 3643, 'DGO': 3178, 'CHIH': 2761, 'ZAC': 1999}
NAC26 = {'t': 20542, 'mha': 9.19, 'pct': 4.6, 'canc': 2141, 'rec': 1.62}
PROD_MAYOR = ['BCS', 'CHIH', 'COAH', 'COL', 'DGO', 'GRO', 'JAL', 'SLP', 'SON', 'ZAC']
PROD_MENOR = ['AGS', 'BC', 'CAM', 'CHIS', 'MÉX', 'GTO', 'HGO', 'MICH', 'NAY', 'NL', 'OAX', 'PUE', 'QRO', 'SIN', 'TAM', 'VER', 'YUC']
INF_MIN = 'p. 444 (p. 468 del PDF)'

# El agua del subsuelo (03-11-2026, la primera cifra de un recurso renovable).
# CONAGUA, «Acuerdo por el que se actualiza la disponibilidad media anual de
# agua subterránea de los 653 acuíferos», DOF 09-11-2023, artículo primero,
# con corte al 30 de diciembre de 2022: sus tablas, una fila por acuífero y
# agrupadas por entidad, se copiaron tal cual a un CSV (clave, nombre,
# entidad y los ocho términos, en millones de m³ al año). Por entidad:
# (acuíferos, con disponibilidad, sin disponibilidad, suma de los déficits,
# suma de lo disponible), en hm³. Si el CSV ya no da esto, se detiene.
ACU = {'tx': 'Comisión Nacional del Agua, «Acuerdo por el que se actualiza la disponibilidad media anual de agua subterránea de los 653 acuíferos de los Estados Unidos Mexicanos», '
             'DOF 09-11-2023, artículo primero (fecha de corte: 30 de diciembre de 2022)',
       'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5708074&fecha=09/11/2023',
       'archivo': 'investigaciones/recursos-naturales/CONAGUA_DisponibilidadAcuiferos_DOF2023.csv',
       'sha256': '1a230f536769b89307a35e99270b4973f1e9e3812c45d046f1d4414cdc1e6efa'}
ACUIFEROS = {'AGS': (5, 0, 5, 134.3, 0.0), 'BC': (48, 32, 16, 603.3, 51.6), 'BCS': (39, 17, 22, 105.1, 15.9), 'CAM': (1, 1, 0, 0.0, 306.5),
             'COAH': (28, 9, 19, 515.1, 69.8), 'COL': (11, 7, 4, 5.6, 14.0), 'CHIS': (15, 15, 0, 0.0, 2948.3), 'CHIH': (61, 23, 38, 3063.0, 424.6),
             'CDMX': (1, 0, 1, 480.4, 0.0), 'DGO': (29, 17, 12, 288.8, 249.4), 'GTO': (18, 5, 13, 676.8, 134.3), 'GRO': (35, 32, 3, 2.7, 717.2),
             'HGO': (21, 18, 3, 27.0, 190.6), 'JAL': (59, 24, 35, 454.4, 104.9), 'MÉX': (9, 1, 8, 562.3, 4.6), 'MICH': (22, 13, 9, 178.3, 281.1),
             'MOR': (4, 3, 1, 0.7, 28.8), 'NAY': (12, 9, 3, 39.9, 83.7), 'NL': (23, 10, 13, 381.1, 109.5), 'OAX': (21, 19, 2, 10.9, 340.2),
             'PUE': (6, 4, 2, 83.0, 113.9), 'QRO': (11, 4, 7, 173.1, 78.7), 'QROO': (2, 2, 0, 0.0, 207.2), 'SLP': (19, 8, 11, 308.8, 154.3),
             'SIN': (14, 6, 8, 172.1, 171.1), 'SON': (60, 37, 23, 553.3, 269.6), 'TAB': (8, 8, 0, 0.0, 7526.1), 'TAM': (14, 10, 4, 35.7, 235.5),
             'TLAX': (4, 4, 0, 0.0, 62.7), 'VER': (18, 14, 4, 64.5, 658.4), 'YUC': (1, 1, 0, 0.0, 2059.6), 'ZAC': (34, 14, 20, 396.1, 43.1)}
ACU_TOT = (653, 367, 286)
# Las dos sumas nacionales con los valores sin redondear del CSV (hm³ al año).
ACU_SUMAS = (9316.4, 17655.2)
# El Programa Nacional Hídrico 2026-2030 (DOF 18-05-2026) repite los 367 y
# 286 de ese Acuerdo, y da en qué se usa el agua que se extrae de ellos.
PNH = {'tx': 'Comisión Nacional del Agua, Programa Nacional Hídrico 2026-2030, DOF 18-05-2026, apartado de diagnóstico',
       'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5787687&fecha=18/05/2026'}
USO_SUB = [('agrícola', 71.1), ('abastecimiento público', 20.9), ('industria', 6.9), ('energía eléctrica, sin hidroelectricidad', 1.1)]
# Segundo Informe de Gobierno: los 27 acuíferos «en condición de
# sobreexplotación» donde CONAGUA mide niveles con pozos (p. 513, nota 1/),
# con la clave y el valor que les da el Acuerdo de 2023 (+ disponible, −
# déficit); los títulos de agua revisados (p. 511) y lo que se cobró (p. 510).
SOBRE27 = {'AGS': [('0103', 'El Llano', -6.257537), ('0105', 'Valle de Calvillo', -17.710928), ('0102', 'Valle de Chicalote', -13.796082), ('0101', 'Valle de Aguascalientes', -95.758309)],
           'BCS': [('0306', 'Santo Domingo', -30.280721), ('0326', 'Alfredo V. Bonfil', 2.13557), ('0324', 'La Paz', -13.488404)],
           'BC': [('0210', 'Valle de Mexicali', -432.044272)],
           'CHIH': [('0831', 'Meoqui-Delicias', -167.118741), ('0801', 'Ascensión', -104.204731)],
           'COAH': [('0511', 'Región Manzanera-Zapalinamé', -38.141433)],
           'CDMX': [('0901', 'Zona Metropolitana de la Ciudad de México', -480.429914)],
           'DGO': [('1001', 'Valle de Santiaguillo', -73.307923), ('1023', 'Ceballos', -18.677546)],
           'JAL': [('1422', 'Encarnación', -61.947808)],
           'NL': [('1919', 'Campo Cerritos', -2.708159)],
           'QRO': [('2204', 'Valle de Buenavista', -13.877392), ('2205', 'Valle de Tequisquiapan', -5.149624), ('2202', 'Valle de Amazcala', -22.161829)],
           'SLP': [('2409', 'Villa Hidalgo', 7.378531), ('2402', 'El Barril', -63.296591)],
           'SON': [('2619', 'Costa de Hermosillo', -74.253541)],
           'ZAC': [('3227', 'Guadalupe Bañuelos', -0.394701), ('3228', 'La Blanca', -10.653091), ('3229', 'Loreto', -49.416281), ('3214', 'Aguanaval', -89.538741), ('3210', 'Benito Juárez', -3.386465)]}
AGUA26 = {'mon': 138, 'pozos': 3904, 'pozos_s': 772, 'bal': 189, 'tit': 538805, 'inc': 58938, 'rec': 24712.5, 'tram': 7868, 'res': 6094}
INF_AGUA = {'s27': 'p. 513 (p. 537 del PDF), nota 1/', 'tit': 'p. 511 (p. 535 del PDF)', 'rec': 'p. 510 (p. 534 del PDF)'}

# Los incendios forestales (03-11-2026, la primera cifra de los bosques).
# CONAFOR, Gerencia de Manejo del Fuego, «Cierre estadístico 2025» (01-01 al
# 31-12-2025), cuadro 4 «Incendios y superficie con información acumulada»:
# por entidad, (incendios, hectáreas de arbolado adulto, renuevo, arbustivo,
# herbáceo, hojarasca, total, tiempo promedio de llegada h:mm). El arbóreo es
# adulto + renuevo; el herbáceo de sus resúmenes incluye la hojarasca. Y el
# cierre de 2024, por entidad (incendios, hectáreas). Si no suman, se detiene.
INC_DOC = {'tx': 'Comisión Nacional Forestal, Gerencia de Manejo del Fuego, «Cierre estadístico 2025», del 1 de enero al 31 de diciembre de 2025',
           'url': 'https://www.gob.mx/cms/uploads/attachment/file/1084029/Cierre_de_la_Temporada_2025.pdf',
           'archivo': 'investigaciones/recursos-naturales/CONAFOR_CierreIncendios2025.pdf',
           'sha256': 'f29ead61c128a65cc745b2341ff0451468368c0321a7ade3d327bcbb8db0e1e5'}
INC_DOC24 = {'tx': 'Comisión Nacional Forestal, Gerencia de Manejo del Fuego, «Cierre estadístico 2024», cuadro 4',
             'url': 'https://www.gob.mx/cms/uploads/attachment/file/965295/Cierre_de_la_Temporada_2024.pdf',
             'archivo': 'investigaciones/recursos-naturales/CONAFOR_CierreIncendios2024.pdf',
             'sha256': '15a4c0af14443d2729a6534b098cbfa298e5563883c1eeaf622c949e8e7c6c03'}
INC_PAG = 'https://www.gob.mx/conafor/documentos/reporte-semanal-de-incendios'
INC25 = {'AGS': (136, 33.72, 0.0, 2276.86, 5386.47, 231.59, 7928.65, '01:29'), 'BC': (65, 6798.49, 138.78, 43248.42, 4672.65, 576.22, 55434.56, '08:43'),
         'BCS': (7, 96.82, 0.0, 17.08, 6.45, 0.0, 120.35, '00:35'), 'CAM': (56, 1482.22, 52.23, 7243.18, 43165.37, 37.32, 51980.32, '55:36'),
         'CHIS': (287, 115.88, 13.40, 754.84, 22942.96, 15753.99, 39581.06, '10:26'), 'CHIH': (596, 6609.12, 11032.86, 27938.37, 95665.73, 80287.23, 221533.30, '08:13'),
         'CDMX': (512, 0.0, 0.0, 48.73, 2794.69, 400.22, 3243.65, '01:10'), 'COAH': (44, 159.57, 89.69, 2654.01, 1931.08, 887.19, 5721.55, '07:54'),
         'COL': (68, 0.0, 0.0, 138.28, 1537.40, 1336.55, 3012.23, '06:51'), 'DGO': (411, 656.71, 4340.02, 26925.70, 37949.91, 33529.97, 103402.31, '06:00'),
         'GTO': (125, 65.04, 0.0, 4027.81, 2790.44, 3158.94, 10042.24, '02:40'), 'GRO': (304, 364.74, 4258.50, 16935.76, 49982.37, 33039.27, 104580.64, '09:33'),
         'HGO': (144, 142.66, 183.39, 2429.12, 824.89, 178.09, 3758.14, '04:45'), 'JAL': (919, 5034.19, 581.55, 21842.71, 41103.13, 20260.29, 88821.87, '02:45'),
         'MÉX': (796, 227.61, 1035.29, 10235.29, 8164.28, 76.45, 19738.93, '01:46'), 'MICH': (682, 3106.87, 1640.13, 14155.19, 15344.58, 11556.09, 45802.86, '01:58'),
         'MOR': (194, 87.70, 0.78, 2449.04, 3182.73, 4455.50, 10175.74, '05:47'), 'NAY': (163, 4.44, 0.0, 14485.03, 16330.27, 36951.12, 67770.85, '24:46'),
         'NL': (52, 2.0, 0.0, 1074.84, 1456.11, 1533.34, 4066.30, '01:55'), 'OAX': (201, 1035.74, 1569.37, 6615.19, 8671.08, 18330.12, 36221.50, '13:01'),
         'PUE': (303, 174.19, 338.29, 3699.14, 9019.23, 0.0, 13230.85, '02:07'), 'QRO': (93, 296.84, 185.04, 1709.29, 267.25, 1256.20, 3714.61, '02:56'),
         'QROO': (29, 173.65, 0.0, 6324.81, 143.09, 0.0, 6641.55, '43:12'), 'SLP': (119, 0.0, 0.0, 4285.08, 6164.01, 6415.04, 16864.13, '06:35'),
         'SIN': (76, 0.0, 0.0, 10739.02, 30737.86, 65338.56, 106815.44, '31:24'), 'SON': (43, 1476.78, 500.38, 4290.31, 14986.78, 27273.61, 48527.87, '38:50'),
         'TAB': (150, 7045.93, 0.0, 0.0, 72214.48, 0.0, 79260.42, '03:21'), 'TAM': (23, 2129.29, 0.0, 5913.36, 1682.39, 9702.59, 19427.62, '44:52'),
         'TLAX': (93, 96.35, 75.28, 659.68, 1385.57, 212.96, 2429.85, '00:55'), 'VER': (172, 195.0, 116.21, 3761.75, 2668.29, 37.66, 6778.92, '07:25'),
         'YUC': (13, 107.34, 0.0, 2091.47, 16.06, 0.0, 2214.87, '09:04'), 'ZAC': (126, 636.87, 1.02, 6597.92, 15503.27, 10128.78, 32867.85, '05:28')}
INC24 = {'AGS': (32, 636.14), 'BC': (120, 32674.71), 'BCS': (11, 71.05), 'CAM': (30, 27666.61),
         'CHIS': (456, 187263.77), 'CHIH': (543, 127711.32), 'CDMX': (993, 3532.09), 'COAH': (32, 500.78),
         'COL': (110, 10853.61), 'DGO': (364, 72829.43), 'GTO': (39, 3857.41), 'GRO': (327, 416780.18),
         'HGO': (179, 4562.54), 'JAL': (950, 112487.43), 'MÉX': (1079, 42162.36), 'MICH': (831, 97718.52),
         'MOR': (163, 4825.11), 'NAY': (142, 83859.53), 'NL': (26, 2411.73), 'OAX': (274, 160437.52),
         'PUE': (421, 30406.15), 'QRO': (87, 1179.69), 'QROO': (64, 91547.95), 'SLP': (70, 18252.75),
         'SIN': (47, 42364.46), 'SON': (48, 7957.84), 'TAB': (52, 23263.54), 'TAM': (33, 9769.82),
         'TLAX': (166, 2549.77), 'VER': (235, 15108.89), 'YUC': (29, 20333.81), 'ZAC': (49, 16639.18)}
INC_TOT = {25: (7002, 1221711.03, 64507.94), 24: (8002, 1672215.70)}
# Del mismo cierre: el promedio 1998-2024 (cuadro 7), la clasificación de
# impacto (cuadro 9: severo, moderado, mínimo), los ecosistemas sensibles al
# fuego (cuadro 10) y los que dependen de él (cuadro 11), los días-persona (resumen) y los incendios que la última
# semana integró con retraso (resumen). Y el tiempo de detección que el cierre
# de 2025 le da a 2024 (00:47) contra el que dio el cierre de 2024 (01:51).
INC_NAC = {'prom_n': 7999, 'prom_ha': 442458, 'sev': 17484.91, 'mod': 416421.77, 'min': 787804.34, 'sens_n': 1442, 'sens_ha': 171127.79,
           'dep_n': 4589, 'dep_ha': 771912.75, 'dp': 363065, 'tarde_n': 80, 'tarde_ha': 17136.51, 'det25': '03:54', 'det24_en25': '00:47', 'det24_en24': '01:51'}


# CONAFOR, «Estado que guarda el sector forestal en México 2023» (publicado en
# agosto de 2024), con el Inventario Nacional Forestal y de Suelos 2015-2020 y
# la Serie VII de uso del suelo del INEGI (2018). Por entidad, en hectáreas:
# (bosques, selvas, manglar, otras asociaciones, matorral xerófilo, otras áreas
# forestales, total forestal; tabla 1, p. 4) y (vegetación primaria,
# secundaria; tabla 2, pp. 10-11). El documento imprime cortado el matorral de
# Chiapas («125.») y de la Ciudad de México («978.»): van en None y se toman
# como el total menos las otras columnas, una cuenta nuestra que se coteja
# contra el total de la columna. La fila de Querétaro no suma su total por
# 0.9 ha: así viene. Si una fila o una columna deja de cuadrar, se detiene.
SF_DOC = {'tx': 'Comisión Nacional Forestal, «Estado que guarda el sector forestal en México 2023», con el Inventario Nacional Forestal y de Suelos 2015-2020 y la Serie VII de uso del suelo del INEGI (2018)',
          'url': 'https://www.gob.mx/cms/uploads/attachment/file/947878/2024_07_31_EGSFM_2023.pdf',
          'archivo': 'investigaciones/recursos-naturales/CONAFOR_EstadoSectorForestal2023.pdf',
          'sha256': 'd651bb164cbaaab9968ed214ef782de4f666c8d8aa19170c6d477ef66d5df5be'}
SF = {'AGS': (101575.2, 30031.7, 0.0, 0.0, 35700.7, 92327.2, 259634.8, 95225.4, 164409.4), 'BC': (176522.3, 0.0, 0.0, 6968.5, 5786795.5, 329350.8, 6299637.1, 6040359.4, 259277.8),
      'BCS': (58469.3, 380251.0, 37291.9, 498.3, 5658129.9, 683785.5, 6818426.0, 6689755.2, 128670.8), 'CAM': (13460.9, 3782854.8, 192663.6, 116572.2, 0.0, 225283.8, 4330835.3, 2272230.7, 2058604.6),
      'CHIS': (1591903.5, 1819327.5, 54082.2, 53288.1, None, 66828.1, 3585555.1, 1257344.9, 2328210.1), 'CHIH': (7007289.1, 510593.3, 0.0, 169.9, 8514135.9, 5578616.8, 21610805.0, 17552787.0, 4058018.0),
      'CDMX': (40978.8, 0.0, 0.0, 1712.6, None, 1045.2, 44715.2, 17571.7, 27143.5), 'COAH': (836629.7, 0.0, 0.0, 1929.0, 11412626.2, 1491675.8, 13742860.7, 12254186.5, 1488674.2),
      'COL': (54113.7, 249573.9, 4664.9, 0.0, 9646.0, 5601.0, 323599.4, 67444.9, 256154.6), 'DGO': (5193060.0, 583392.2, 0.0, 317.0, 2623500.3, 2217840.8, 10618110.3, 7117284.3, 3500826.0),
      'GTO': (477178.8, 243715.4, 0.0, 41.4, 210912.6, 330331.4, 1262179.6, 579876.3, 682303.2), 'GRO': (2306850.1, 1955112.2, 12341.3, 35393.5, 0.0, 29468.1, 4339165.1, 1404277.2, 2934888.0),
      'HGO': (545670.4, 115896.9, 0.0, 269.0, 279624.9, 20672.9, 962134.1, 434806.5, 527327.6), 'JAL': (2366019.6, 1733227.2, 3642.7, 12515.3, 14664.8, 416441.9, 4546511.5, 1932933.1, 2613578.4),
      'MÉX': (623624.7, 116540.6, 0.0, 12884.1, 17108.8, 18345.7, 788503.9, 413367.2, 375136.6), 'MICH': (1652546.3, 1839871.9, 1984.7, 8508.6, 3652.0, 12452.0, 3519015.5, 1267799.4, 2251216.0),
      'MOR': (54185.6, 129133.4, 0.0, 89.7, 246.5, 125.2, 183780.5, 31928.0, 151852.5), 'NAY': (936335.3, 815127.7, 99124.9, 17418.5, 4542.7, 45784.2, 1918333.3, 989953.3, 928380.0),
      'NL': (687653.6, 10864.9, 0.0, 0.0, 3342697.9, 154895.7, 4196112.1, 3600655.2, 595457.0), 'OAX': (3714255.4, 2767107.4, 29412.2, 98439.9, 56966.3, 26548.8, 6692730.0, 2142797.5, 4549932.5),
      'PUE': (620601.1, 622179.8, 0.0, 18057.0, 280642.3, 32074.0, 1573554.1, 687694.9, 885859.2), 'QRO': (280065.4, 145633.3, 0.0, 541.0, 261455.8, 8651.5, 696347.9, 349139.2, 347208.6),
      'QROO': (0.0, 3445295.7, 188860.2, 11656.7, 0.0, 231440.3, 3877252.9, 1981096.7, 1896156.2), 'SLP': (569355.9, 400110.1, 0.0, 5682.7, 2910064.8, 363047.7, 4248261.3, 3304975.0, 943286.3),
      'SIN': (870592.7, 2013372.7, 102066.5, 3610.7, 136586.0, 78973.8, 3205202.3, 2454523.7, 750678.6), 'SON': (1973339.5, 1806246.6, 15492.1, 297.9, 9818318.8, 1334133.7, 14947828.6, 13189333.0, 1758495.6),
      'TAB': (19657.8, 236079.2, 61933.2, 67066.0, 0.0, 432417.9, 817154.1, 608785.3, 208368.8), 'TAM': (607746.6, 838563.4, 4721.9, 2403.9, 2126148.5, 243438.8, 3823023.0, 2611281.5, 1211741.5),
      'TLAX': (66710.9, 0.0, 0.0, 71.9, 6315.3, 1071.9, 74170.0, 43717.3, 30452.7), 'VER': (315966.7, 846457.0, 46956.2, 24862.8, 12667.0, 224271.5, 1471181.3, 502193.4, 968987.9),
      'YUC': (0.0, 2541686.9, 92654.8, 25786.8, 0.0, 34246.0, 2694374.5, 146339.8, 2548034.7), 'ZAC': (1084248.0, 354075.3, 0.0, 0.0, 2675952.6, 1109959.3, 5224235.3, 3185797.8, 2038437.5)}
SF_TOT = (34846606.8, 30332322.1, 947893.3, 527054.0, 56200206.3, 15841147.2, 138695229.8, 95227461.4, 43467768.4)

# CONAPESCA, Anuario Estadístico de Acuacultura y Pesca 2025 (cifras de 2025,
# publicado en junio de 2026). Por entidad: (peso vivo 2025, captura 2025,
# acuacultura 2025, en toneladas; valor 2025, en miles de pesos a precio de
# playa; peso vivo 2024; valor 2024). Salen de las series de los cuadros 2.5.6,
# 2.5.8, 2.5.10 y 2.5.12 (pp. 171 a 177). «-» va en 0: Nuevo León no registró
# producción en 2025. El Anuario trae dos tropiezos que se dicen tal cual: los
# cuadros 2.1.10 y 2.1.11 (pp. 137-138) le dan a Jalisco las cifras de Colima y
# a Colima las de Jalisco (PE_CRUCE, contra el cuadro 2.1.5 y las series), y el
# renglón TOTAL del cuadro 2.5.8 de la captura repite el de la acuacultura. Si
# una fila o una columna deja de cuadrar, o si la CONAPESCA corrige el cruce,
# la generación se detiene.
PE_DOC = {'tx': 'Comisión Nacional de Acuacultura y Pesca, Anuario Estadístico de Acuacultura y Pesca 2025',
          'url': 'https://www.gob.mx/cms/uploads/attachment/file/1088921/ANUARIO_CONAPESCA_2025.pdf',
          'archivo': 'investigaciones/recursos-naturales/CONAPESCA_AnuarioAcuaculturaPesca2025.pdf',
          'sha256': '670ac9d63f44f1da732a5a59fa0290532a201509d869e4b28bf9fed911af2932'}
PE_PAG = 'https://www.gob.mx/conapesca/documentos/anuario-estadistico-de-acuacultura-y-pesca'
PESCA = {'AGS': (93, 0, 93, 9218, 86, 7919), 'BC': (325246, 311398, 13848, 4266136, 353035, 3609317), 'BCS': (313063, 303925, 9138, 5102990, 204271, 2510392),
      'CAM': (43717, 43288, 428, 1785651, 44785, 1352349), 'CDMX': (7, 0, 7, 1112, 1, 164), 'CHIH': (524, 270, 253, 23782, 407, 28292),
      'CHIS': (42127, 22103, 20024, 1101853, 34697, 941396), 'COAH': (133, 121, 12, 7082, 23, 805), 'COL': (52444, 46070, 6375, 1031904, 43144, 950550),
      'DGO': (427, 28, 399, 27917, 229, 11613), 'GRO': (9609, 8465, 1144, 624058, 7230, 392262), 'GTO': (100, 0, 100, 9024, 77, 6394),
      'HGO': (4098, 54, 4044, 349010, 5879, 588924), 'JAL': (16800, 6366, 10434, 554960, 13806, 351928), 'MICH': (8833, 3068, 5764, 292081, 12951, 422704),
      'MOR': (300, 2, 299, 25294, 208, 5335), 'MÉX': (15845, 2275, 13570, 1077978, 15651, 1086955), 'NAY': (31562, 13787, 17775, 1410524, 32512, 1578088),
      'NL': (0, 0, 0, 0, 34, 3114), 'OAX': (5048, 4590, 457, 276867, 5587, 234806), 'PUE': (467, 53, 414, 41102, 315, 16496),
      'QRO': (562, 23, 540, 42472, 451, 33194), 'QROO': (2836, 2728, 108, 408835, 2226, 314164), 'SIN': (480141, 336586, 143555, 17286288, 468319, 14529716),
      'SLP': (1188, 7, 1181, 84297, 52, 3351), 'SON': (682879, 564812, 118067, 18444569, 776180, 11430875), 'TAB': (34942, 26899, 8044, 1071952, 38591, 1351973),
      'TAM': (33394, 28588, 4806, 1223585, 31738, 1183953), 'TLAX': (118, 17, 101, 9125, 103, 7333), 'VER': (51641, 46172, 5469, 1664947, 60612, 1805531),
      'YUC': (46576, 45702, 873, 3639420, 40230, 2434149), 'ZAC': (1720, 0, 1720, 47416, 1154, 34253)}
# Los totales del Anuario: peso vivo 2025, acuacultura 2025, valor 2025, peso
# vivo 2024, valor 2024 y peso desembarcado 2025 (cuadros 2.1.5, 2.5.6, 2.5.10
# y 2.5.12). La captura total no se lee del cuadro 2.5.8: es peso vivo menos
# acuacultura, cuenta nuestra.
PE_TOT = {'viv': 2206439, 'acu': 389043, 'val': 61941451, 'viv24': 2194586, 'val24': 47228294, 'des': 2036574}
# Lo que imprimen los cuadros 2.1.10 y 2.1.11 en los renglones de Jalisco y
# Colima: (toneladas desembarcadas, miles de pesos).
PE_CRUCE = {'JAL': (52213, 1031904), 'COL': (16317, 554960)}
# Las toneladas desembarcadas de 2025 de las dos, en el cuadro 2.1.5.
PE_DES = {'JAL': 16317, 'COL': 52213}
# El renglón TOTAL de 2025 que imprime el cuadro 2.5.8 de la captura.
PE_TOT_258 = 389043
# El valor nacional de dos especies, 2024 y 2025 (cuadro 2.5.11, p. 176), en miles de pesos.
PE_ESP = {'camarón': (20330496, 26214666), 'calamar': (115865, 1562449)}


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
    _huella(AE)
    out = []
    for i, (k, n, sede, a, m, d25, d24, d23, vu25, vu24) in enumerate(REFINERIAS):
        if len(m) != len(MESES):
            raise SystemExit('recursos_naturales: %s no trae los %d meses' % (k, len(MESES)))
        out.append({'id': k, 'n': n, 'sede': sede, 'a': a, 'm': m, 'jun': m[-1], 'prom': round(sum(m) / len(m), 1),
                    'max': max(m), 'mmax': MES_LARGO[MESES[m.index(max(m))]], 'd25': d25, 'd24': d24, 'd23': d23, 'vu25': vu25, 'vu24': vu24})
        cap = CAPACIDAD[k]
        out[-1].update({'cap': cap, 'uso': round(out[-1]['prom'] / cap * 100, 1), 'usoj': round(m[-1] / cap * 100, 1)})
    if sum(CAPACIDAD.values()) != CAP_SNR or set(CAPACIDAD) != {r['id'] for r in out}:
        raise SystemExit('recursos_naturales: las capacidades por refinería ya no suman los %s mil barriles diarios del Anuario' % format(CAP_SNR, ','))
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


def mineria(abbrs=None):
    """Las concesiones mineras de cada entidad (DGM, marzo de 2024) y lo
    derivado: su parte del total nacional y las hectáreas por título. Si el
    cuadro ya no suma su total, la generación se detiene."""
    _huella(PRONT)
    t = sum(v[0] for v in MINAS.values())
    h = sum(v[1] for v in MINAS.values())
    if t != MINAS_TOT[0] or abs(h - MINAS_TOT[1]) > 1:
        raise SystemExit('recursos_naturales: el cuadro de concesiones suma %d títulos y %.0f ha; el Prontuario dice %d y %d' % (t, h, MINAS_TOT[0], MINAS_TOT[1]))
    if abs(sum(x[2] for x in DERECHOS) - DERECHOS_TOT) > 0.2:
        raise SystemExit('recursos_naturales: los derechos mineros ya no suman %s' % DERECHOS_TOT)
    if abbrs is not None and not set(MINAS) | set(MIN26) <= set(abbrs):
        raise SystemExit('recursos_naturales: claves de entidad que no existen en la base: %s' % sorted((set(MINAS) | set(MIN26)) - set(abbrs)))
    orden = sorted(MINAS, key=lambda a: -MINAS[a][0])
    out = {}
    for a, (n, ha) in MINAS.items():
        out[a] = {'t': n, 'ha': round(ha), 'pt': round(n / MINAS_TOT[0] * 100, 2), 'ph': round(ha / MINAS_TOT[1] * 100, 2),
                  'hxt': round(ha / n), 'lug': orden.index(a) + 1, 't26': MIN26.get(a),
                  'prod': 'mayor' if a in PROD_MAYOR else 'menor' if a in PROD_MENOR else None}
    return out


def acuiferos(abbrs=None):
    """Los acuíferos de cada entidad (CONAGUA, DOF 09-11-2023, corte al
    30-12-2022) y lo derivado: cuántos de cada 100 no tienen disponibilidad y
    su lugar por déficit. Se coteja contra el CSV de las 653 filas: si una
    suma o un acuífero sobreexplotado del Informe ya no cuadra, se detiene."""
    import csv
    p = os.path.join(RAIZ, ACU['archivo'])
    if os.path.exists(p):
        _huella(ACU)
        F = list(csv.DictReader(open(p, encoding='utf-8')))
        if len(F) != ACU_TOT[0] or len({f['clave'] for f in F}) != ACU_TOT[0]:
            raise SystemExit('recursos_naturales: el CSV de acuíferos no trae los %d acuíferos' % ACU_TOT[0])
        por = {f['clave']: f for f in F}
        nom = {v: k for k, v in ACU_ENT.items()}
        agg = {}
        for f in F:
            x = agg.setdefault(ACU_ENT[f['entidad']], [0, 0, 0, 0.0, 0.0])
            pos, neg = float(f['DMA_positiva']), float(f['DMA_negativa_deficit'])
            x[0] += 1
            x[1] += pos > 0
            x[2] += neg < 0
            x[3] -= neg
            x[4] += pos
        for a, v in ACUIFEROS.items():
            w = agg.get(a)
            if not w or tuple(w[:3]) != v[:3] or abs(round(w[3], 1) - v[3]) > 0.05 or abs(round(w[4], 1) - v[4]) > 0.05:
                raise SystemExit('recursos_naturales: %s ya no da %s en el CSV de acuíferos (da %s)' % (a, v, w))
        tot = (round(sum(-float(f['DMA_negativa_deficit']) for f in F), 1), round(sum(float(f['DMA_positiva']) for f in F), 1))
        if tot != ACU_SUMAS:
            raise SystemExit('recursos_naturales: las sumas nacionales del CSV de acuíferos dan %s, no %s' % (tot, ACU_SUMAS))
        for a, xs in SOBRE27.items():
            for c, n, d in xs:
                f = por.get(c)
                dma = float(f['DMA_positiva']) or float(f['DMA_negativa_deficit']) if f else None
                if not f or ACU_ENT[f['entidad']] != a or abs(dma - d) > 1e-5:
                    raise SystemExit('recursos_naturales: el acuífero %s (%s) del Informe ya no cuadra con el Acuerdo de 2023' % (c, n))
    if sum(v[0] for v in ACUIFEROS.values()) != ACU_TOT[0] or sum(v[1] for v in ACUIFEROS.values()) != ACU_TOT[1] or \
            sum(v[2] for v in ACUIFEROS.values()) != ACU_TOT[2] or any(v[0] != v[1] + v[2] for v in ACUIFEROS.values()):
        raise SystemExit('recursos_naturales: los acuíferos por entidad ya no suman %d, %d con disponibilidad y %d sin ella' % ACU_TOT)
    if sum(len(x) for x in SOBRE27.values()) != 27:
        raise SystemExit('recursos_naturales: el Informe enlista 27 acuíferos sobreexplotados; aquí hay %d' % sum(len(x) for x in SOBRE27.values()))
    if abbrs is not None and set(ACUIFEROS) != set(abbrs):
        raise SystemExit('recursos_naturales: las entidades de los acuíferos no son las de la base: %s' % sorted(set(ACUIFEROS) ^ set(abbrs)))
    orden = sorted(ACUIFEROS, key=lambda a: -ACUIFEROS[a][3])
    out = {}
    for a, (n, con, sin, de, di) in ACUIFEROS.items():
        out[a] = {'n': n, 'con': con, 'sin': sin, 'ps': round(sin / n * 100, 1), 'def': de, 'disp': di,
                  'lug': orden.index(a) + 1 if de > 0 else None, 's27': SOBRE27.get(a, [])}
    return out


def incendios(abbrs=None):
    """Los incendios forestales de cada entidad (CONAFOR, cierre de 2025, y el
    de 2024 para comparar) y lo derivado: el arbóreo de cada 100 hectáreas,
    las hectáreas por incendio, el cambio contra 2024 y su lugar. Si las filas
    ya no suman los totales del cierre, la generación se detiene."""
    _huella(INC_DOC)
    _huella(INC_DOC24)
    for k, v in INC25.items():
        if abs(sum(v[1:6]) - v[6]) > 0.05:
            raise SystemExit('recursos_naturales: la fila de incendios de %s ya no suma su total (%s)' % (k, v[6]))
    n25, h25, a25 = sum(v[0] for v in INC25.values()), sum(v[6] for v in INC25.values()), sum(v[1] + v[2] for v in INC25.values())
    n24, h24 = sum(v[0] for v in INC24.values()), sum(v[1] for v in INC24.values())
    if n25 != INC_TOT[25][0] or abs(h25 - INC_TOT[25][1]) > 0.05 or abs(a25 - INC_TOT[25][2]) > 0.05:
        raise SystemExit('recursos_naturales: los incendios de 2025 suman %d y %.2f ha (arbóreo %.2f); el cierre dice %s' % (n25, h25, a25, INC_TOT[25]))
    if n24 != INC_TOT[24][0] or abs(h24 - INC_TOT[24][1]) > 0.05:
        raise SystemExit('recursos_naturales: los incendios de 2024 suman %d y %.2f ha; el cierre dice %s' % (n24, h24, INC_TOT[24]))
    if abs(INC_NAC['sev'] + INC_NAC['mod'] + INC_NAC['min'] - INC_TOT[25][1]) > 0.05:
        raise SystemExit('recursos_naturales: la clasificación de impacto de los incendios ya no suma el total del cierre')
    if abbrs is not None and (set(INC25) != set(abbrs) or set(INC24) != set(abbrs)):
        raise SystemExit('recursos_naturales: las entidades de los incendios no son las de la base: %s' % sorted((set(INC25) | set(INC24)) ^ set(abbrs)))
    oh = sorted(INC25, key=lambda a: -INC25[a][6])
    on = sorted(INC25, key=lambda a: -INC25[a][0])
    out = {}
    for a, v in INC25.items():
        n, ha, arb = v[0], v[6], v[1] + v[2]
        n4, h4 = INC24[a]
        out[a] = {'n': n, 'ha': round(ha, 2), 'arb': round(arb, 2), 'parb': round(arb / ha * 100, 1) if ha else 0.0,
                  'hxi': round(ha / n, 1) if n else None, 'lleg': v[7], 'lh': oh.index(a) + 1, 'ln': on.index(a) + 1,
                  'n24': n4, 'ha24': h4, 'cam': round((ha - h4) / h4 * 100, 1) if h4 else None,
                  'pn': round(n / INC_TOT[25][0] * 100, 1), 'ph': round(ha / INC_TOT[25][1] * 100, 1)}
    return out


def forestal(abbrs=None):
    """La superficie forestal de cada entidad (CONAFOR, 2023) y lo derivado: la
    parte arbolada, la secundaria, su lugar y su parte del país, y lo que tocó
    el fuego de 2025 frente a ella. Si las filas o las columnas ya no cuadran
    con los totales del documento, la generación se detiene."""
    _huella(SF_DOC)
    res = {}
    for k, v in SF.items():
        otras = v[0] + v[1] + v[2] + v[3] + v[5]
        if v[4] is None:
            res[k] = round(v[6] - otras, 1)
        elif abs(otras + v[4] - v[6]) > 1.0:
            raise SystemExit('recursos_naturales: la fila forestal de %s ya no suma su total (%s)' % (k, v[6]))
        if abs(v[7] + v[8] - v[6]) > 0.15:
            raise SystemExit('recursos_naturales: lo primario y lo secundario de %s ya no suman su total forestal' % k)
    for j in range(9):
        s = sum((res[k] if v[j] is None else v[j]) for k, v in SF.items())
        if abs(s - SF_TOT[j]) > 1.05:
            raise SystemExit('recursos_naturales: la columna %d de la superficie forestal suma %.1f; el documento dice %.1f' % (j, s, SF_TOT[j]))
    if abbrs is not None and set(SF) != set(abbrs):
        raise SystemExit('recursos_naturales: las entidades de la superficie forestal no son las de la base: %s' % sorted(set(SF) ^ set(abbrs)))
    I = incendios(abbrs)
    orden = sorted(SF, key=lambda a: -SF[a][6])
    out = {}
    for a, v in SF.items():
        arb = v[0] + v[1] + v[2] + v[3]
        z = I[a]
        out[a] = {'sf': v[6], 'arb': round(arb, 1), 'parb': round(arb / v[6] * 100, 1), 'mat': res.get(a, v[4]), 'mat_cuenta': a in res,
                  'bos': v[0], 'sel': v[1], 'psec': round(v[8] / v[6] * 100, 1), 'pnac': round(v[6] / SF_TOT[6] * 100, 1), 'lug': orden.index(a) + 1,
                  'pq': round(z['ha'] / v[6] * 100, 2), 'parbq': round(z['arb'] / arb * 100, 2) if arb else None}
    oq = sorted(out, key=lambda a: -out[a]['pq'])
    for a in out:
        out[a]['lq'] = oq.index(a) + 1
    return out


def pesca(abbrs=None):
    """La pesca y la acuacultura de cada entidad (CONAPESCA, Anuario 2025) y lo
    derivado: su parte del país, su lugar por toneladas y por valor, la parte
    que es cultivo y el cambio contra 2024. Si las filas o las columnas ya no
    cuadran con el Anuario, o si se corrige el cruce de Jalisco y Colima, la
    generación se detiene."""
    _huella(PE_DOC)
    for k, v in PESCA.items():
        if abs(v[1] + v[2] - v[0]) > 2:
            raise SystemExit('recursos_naturales: la captura y la acuacultura de %s ya no suman su peso vivo (%s)' % (k, v[0]))
    s = lambda j: sum(v[j] for v in PESCA.values())
    for j, c, tol in ((0, 'viv', 3), (2, 'acu', 3), (3, 'val', 5), (4, 'viv24', 3), (5, 'val24', 5)):
        if abs(s(j) - PE_TOT[c]) > tol:
            raise SystemExit('recursos_naturales: la columna %s de la pesca suma %s; el Anuario dice %s' % (c, s(j), PE_TOT[c]))
    if abbrs is not None and set(PESCA) != set(abbrs):
        raise SystemExit('recursos_naturales: las entidades de la pesca no son las de la base: %s' % sorted(set(PESCA) ^ set(abbrs)))
    # El cruce del Anuario: lo que imprime en Jalisco es lo de Colima, y al revés.
    if not (PE_CRUCE['JAL'] == (PE_DES['COL'], PESCA['COL'][3]) and PE_CRUCE['COL'] == (PE_DES['JAL'], PESCA['JAL'][3])):
        raise SystemExit('recursos_naturales: los cuadros 2.1.10 y 2.1.11 ya no cruzan a Jalisco y Colima: cambia el punto ciego de la pesca')
    if PE_TOT_258 != PE_TOT['acu']:
        raise SystemExit('recursos_naturales: el renglón TOTAL del cuadro 2.5.8 ya no repite la acuacultura: cambia el punto ciego de la pesca')
    ov = sorted(PESCA, key=lambda a: -PESCA[a][0])
    op = sorted(PESCA, key=lambda a: -PESCA[a][3])
    out = {}
    for a, v in PESCA.items():
        reg = v[0] > 0
        out[a] = {'t': v[0] if reg else None, 'cap': v[1], 'acu': v[2], 'val': v[3], 'mdp': round(v[3] / 1000, 1) if reg else None, 't24': v[4], 'val24': v[5],
                  'pacu': round(v[2] / v[0] * 100, 1) if reg else None, 'pt': round(v[0] / PE_TOT['viv'] * 100, 2), 'pv': round(v[3] / PE_TOT['val'] * 100, 2),
                  'lt': ov.index(a) + 1 if reg else None, 'lv': op.index(a) + 1 if reg else None,
                  'ct': round((v[0] - v[4]) / v[4] * 100, 1) if reg and v[4] else None, 'cv': round((v[3] - v[5]) / v[5] * 100, 1) if reg and v[5] else None}
    return out


# Cómo nombra el Acuerdo de 2023 a cada entidad, para leer su CSV.
ACU_ENT = {'AGUASCALIENTES': 'AGS', 'BAJA CALIFORNIA': 'BC', 'BAJA CALIFORNIA SUR': 'BCS', 'CAMPECHE': 'CAM', 'COAHUILA': 'COAH', 'COLIMA': 'COL',
           'CHIAPAS': 'CHIS', 'CHIHUAHUA': 'CHIH', 'CIUDAD DE MÉXICO': 'CDMX', 'DURANGO': 'DGO', 'GUANAJUATO': 'GTO', 'GUERRERO': 'GRO', 'HIDALGO': 'HGO',
           'JALISCO': 'JAL', 'ESTADO DE MÉXICO': 'MÉX', 'MICHOACÁN': 'MICH', 'MORELOS': 'MOR', 'NAYARIT': 'NAY', 'NUEVO LEÓN': 'NL', 'OAXACA': 'OAX',
           'PUEBLA': 'PUE', 'QUERÉTARO': 'QRO', 'QUINTANA ROO': 'QROO', 'SAN LUIS POTOSÍ': 'SLP', 'SINALOA': 'SIN', 'SONORA': 'SON', 'TABASCO': 'TAB',
           'TAMAULIPAS': 'TAM', 'TLAXCALA': 'TLAX', 'VERACRUZ': 'VER', 'YUCATÁN': 'YUC', 'ZACATECAS': 'ZAC'}


def _mdps(v):
    if v is None:
        return '—'
    return ('−' if v < 0 else '+') + '$' + format(abs(v), ',.1f') + ' mdp'


def _chip(e, pend=None):
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, ' data-pend="%s"' % pend if pend else '', e)


def uso_snr():
    """El sistema entero: el promedio del total publicado en los diez meses ÷ la capacidad de las siete × 100."""
    return round(sum(TOTAL_SNR) / len(TOTAL_SNR) / CAP_SNR * 100, 1)


def tabla_refinerias():
    R = refinerias()
    filas = ''.join(
        '<tr><th scope="row">%s<br><small>%s</small></th><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s<br><small>%s</small></td>'
        '<td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s</td></tr>' % (
            html.escape(r['n']), html.escape(r['sede']), format(r['jun'], ','), format(r['prom'], ',.1f'), format(r['max'], ','), r['mmax'],
            format(r['cap'], ','), format(r['uso'], '.1f') + ' %',
            _mdps(r['d25']) if r['d25'] is not None else ('no la consolida como unidad propia' if r['id'] == 'olmeca' else 'no figura'),
            _mdps(r['d24']) if r['d24'] is not None else ('—' if r['id'] == 'olmeca' else 'no figura'))
        for r in sorted(R, key=lambda x: -x['jun']))
    s_jun = sum(r['jun'] for r in R)
    return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>El Sistema Nacional de Refinación, refinería por refinería '
            '(miles de barriles diarios de crudo procesado y millones de pesos)</caption>'
            '<thead><tr><th scope="col">Refinería</th><th scope="col">Junio 2026 %s</th><th scope="col">Promedio sep-25 a jun-26 %s</th>'
            '<th scope="col">Su mejor mes %s</th><th scope="col">Capacidad de destilación, 2024 %s</th><th scope="col">Uso promedio de su capacidad %s</th><th scope="col">Valor perdido (−) o recuperado (+) en libros, 2025 %s</th><th scope="col">Igual, 2024 %s</th></tr></thead>'
            '<tbody>%s</tbody><tfoot><tr><th scope="row">Las siete</th><td class="num-tabular">%s</td><td colspan="2"><small>La suma de las etiquetas da %s; '
            'el Informe publica %s. La diferencia es redondeo de la gráfica.</small></td><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td colspan="2"><small>'
            'Uso: promedio de los diez meses ÷ capacidad × 100, cuenta nuestra. La capacidad es la del cierre de 2024 (PEMEX, Anuario Estadístico 2024, cuadro 3.6, p. 48).</small></td></tr></tfoot></table></div>') % (
        _chip('oficial'), _chip('derivado'), _chip('oficial'), _chip('oficial'), _chip('derivado'), _chip('oficial'), _chip('oficial'), filas,
        format(s_jun, ','), format(s_jun, ','), format(TOTAL_SNR[-1], ','), format(CAP_SNR, ','), format(uso_snr(), '.1f') + ' %')


def tabla_mineria():
    import auditorias
    nom = {e['abbr']: e['name'] for e in auditorias.db()['estados']}
    M = mineria(list(nom))
    P = {'mayor': 'de las 10 que dan el 94.9 %', 'menor': 'de las 17 que dan el 5.2 %', None: 'no figura'}
    filas = ''.join(
        '<tr><th scope="row">%d. %s</th><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s %%</td>'
        '<td class="num-tabular">%s</td><td class="num-tabular">%s</td><td>%s</td></tr>' % (
            x['lug'], html.escape(nom[a]), _n(x['t']), _n(x['ha']), _n(x['pt'], 2), _n(x['hxt']), _n(x['t26']) if x['t26'] is not None else '—', P[x['prod']])
        for a, x in sorted(M.items(), key=lambda i: i[1]['lug']))
    return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Las concesiones mineras de cada entidad (títulos vigentes y hectáreas que amparan)</caption>'
            '<thead><tr><th scope="col">Entidad</th><th scope="col">Títulos, marzo de 2024 %s</th><th scope="col">Hectáreas %s</th><th scope="col">Su parte de los títulos del país %s</th>'
            '<th scope="col">Hectáreas por título %s</th><th scope="col">Títulos, junio de 2026 %s</th><th scope="col">En la producción minera %s</th></tr></thead>'
            '<tbody>%s</tbody><tfoot><tr><th scope="row">Las %d</th><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td colspan="4"><small>%s no figuran en el cuadro. '
            'Junio de 2026: el Segundo Informe solo da cuatro estados y el total nacional (%s títulos).</small></td></tr></tfoot></table></div>') % (
        _chip('oficial'), _chip('oficial'), _chip('derivado'), _chip('derivado'), _chip('oficial'), _chip('oficial'), filas, len(M),
        _n(MINAS_TOT[0]), _n(MINAS_TOT[1]), _y([nom[a] for a in sorted(set(nom) - set(M))]), _n(NAC26['t']))


def tabla_agua():
    import auditorias
    nom = {e['abbr']: e['name'] for e in auditorias.db()['estados']}
    A = acuiferos(list(nom))
    orden = sorted(A, key=lambda a: (-A[a]['def'], -A[a]['ps'], nom[a]))
    filas = ''.join(
        '<tr><th scope="row">%s</th><td class="num-tabular">%d</td><td class="num-tabular">%d</td><td class="num-tabular">%s</td><td class="num-tabular">%s</td>'
        '<td class="num-tabular">%s</td><td>%s</td></tr>' % (
            html.escape(nom[a]), A[a]['n'], A[a]['sin'], _n(A[a]['ps'], 1), _n(A[a]['def'], 1) if A[a]['def'] else '—', _n(A[a]['disp'], 1),
            html.escape(_y([n for c, n, d in A[a]['s27']])) if A[a]['s27'] else '—')
        for a in orden)
    return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Los acuíferos de cada entidad, con corte al 30 de diciembre de 2022 (millones de m³ al año)</caption>'
            '<thead><tr><th scope="col">Entidad</th><th scope="col">Acuíferos %s</th><th scope="col">Sin disponibilidad %s</th><th scope="col">De cada 100 %s</th>'
            '<th scope="col">Suma de sus déficits %s</th><th scope="col">Suma de lo disponible %s</th><th scope="col">Sobreexplotados que se miden con pozos (2026) %s</th></tr></thead>'
            '<tbody>%s</tbody><tfoot><tr><th scope="row">Las 32</th><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s</td>'
            '<td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">27</td></tr></tfoot></table></div>') % (
        _chip('oficial'), _chip('oficial'), _chip('derivado'), _chip('derivado'), _chip('derivado'), _chip('oficial'), filas,
        _n(ACU_TOT[0]), _n(ACU_TOT[2]), _n(ACU_TOT[2] / ACU_TOT[0] * 100, 1), _n(ACU_SUMAS[0], 1), _n(ACU_SUMAS[1], 1))


def tabla_forestal():
    import auditorias
    nom = {e['abbr']: e['name'] for e in auditorias.db()['estados']}
    F = forestal(list(nom))
    q = lambda v: _n(v, 1) if v >= 0.05 else 'menos de 0.1'
    filas = ''.join(
        '<tr><th scope="row">%d. %s</th><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s</td>'
        '<td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s <small>(%d.º)</small></td></tr>' % (
            x['lug'], html.escape(nom[a]), _n(x['sf'], 1), _n(x['bos'] + x['sel'], 1), _n(x['parb'], 1), _n(x['psec'], 1), q(x['pnac']), q(x['pq']), x['lq'])
        for a, x in sorted(F.items(), key=lambda i: i[1]['lug']))
    arb = sum(x['arb'] for x in F.values())
    return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>La superficie forestal de cada entidad (hectáreas, con el mapa de vegetación de 2018), ordenada de más a menos, '
            'y lo que el fuego de 2025 afectó frente a ella</caption>'
            '<thead><tr><th scope="col">Entidad</th><th scope="col">Superficie forestal %s</th><th scope="col">Bosques y selvas %s</th><th scope="col">Arbolada, de cada 100 %s</th>'
            '<th scope="col">Secundaria, de cada 100 %s</th><th scope="col">Su parte del país %s</th><th scope="col">Afectada por el fuego de 2025, de cada 100 (lugar) %s</th></tr></thead>'
            '<tbody>%s</tbody><tfoot><tr><th scope="row">Las 32</th><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s</td>'
            '<td class="num-tabular">%s</td><td class="num-tabular">100</td><td class="num-tabular">%s</td></tr></tfoot></table></div>'
            '<p><small>Arbolada: bosques, selvas, manglar y otras asociaciones. Lo afectado por el fuego es la superficie del cierre de 2025 ÷ la superficie forestal × 100: una proporción '
            'con años distintos, no la parte que se perdió. Las sumas, porcentajes y lugares son nuestros.</small></p>') % (
        _chip('oficial'), _chip('derivado'), _chip('derivado'), _chip('derivado'), _chip('derivado'), _chip('derivado'), filas,
        _n(SF_TOT[6], 1), _n(SF_TOT[0] + SF_TOT[1], 1), _n(arb / SF_TOT[6] * 100, 1), _n(SF_TOT[8] / SF_TOT[6] * 100, 1), _n(INC_TOT[25][1] / SF_TOT[6] * 100, 1))


def _sig(v):
    return ('+' if v > 0 else '−' if v < 0 else '') + _n(abs(v), 1) + ' %'


def tabla_pesca():
    import auditorias
    nom = {e['abbr']: e['name'] for e in auditorias.db()['estados']}
    P = pesca(list(nom))
    reg = sorted((a for a in P if P[a]['t']), key=lambda a: P[a]['lt'])
    filas = ''.join(
        '<tr><th scope="row">%d. %s</th><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s</td>'
        '<td class="num-tabular">%s <small>(%d.º)</small></td><td class="num-tabular">%s</td><td class="num-tabular">%s</td></tr>' % (
            P[a]['lt'], html.escape(nom[a]), _n(P[a]['t']), _n(P[a]['pacu'], 1), _n(P[a]['pt'], 1) if P[a]['pt'] >= 0.05 else 'menos de 0.1',
            _n(P[a]['mdp'], 1), P[a]['lv'], _sig(P[a]['ct']), _sig(P[a]['cv']))
        for a in reg)
    sin = [a for a in P if not P[a]['t']]
    filas += ''.join('<tr><th scope="row">%s</th><td colspan="6">No registró producción en 2025 (en 2024, %s t y $%s mdp)</td></tr>' % (
        html.escape(nom[a]), _n(P[a]['t24']), _n(P[a]['val24'] / 1000, 1)) for a in sin)
    return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>La pesca y la acuacultura de cada entidad, 2025 (toneladas en peso vivo, ordenadas de más a menos, '
            'y millones de pesos a precio de playa)</caption>'
            '<thead><tr><th scope="col">Entidad</th><th scope="col">Toneladas %s</th><th scope="col">De cultivo, de cada 100 %s</th><th scope="col">Su parte del país %s</th>'
            '<th scope="col">Valor, mdp (lugar) %s</th><th scope="col">Toneladas contra 2024 %s</th><th scope="col">Valor contra 2024 %s</th></tr></thead>'
            '<tbody>%s</tbody><tfoot><tr><th scope="row">Las 32</th><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">100</td>'
            '<td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s</td></tr></tfoot></table></div>'
            '<p><small>De cultivo: la acuacultura ÷ el peso vivo × 100. El valor es en pesos de cada año, sin descontar la inflación. Las proporciones, cambios y lugares son nuestros. '
            'Jalisco y Colima van con las cifras de las series del Anuario y de su cuadro 2.1.5: sus cuadros 2.1.10 y 2.1.11 las imprimen cruzadas.</small></p>') % (
        _chip('oficial'), _chip('derivado'), _chip('derivado'), _chip('oficial'), _chip('derivado'), _chip('derivado'), filas,
        _n(PE_TOT['viv']), _n(PE_TOT['acu'] / PE_TOT['viv'] * 100, 1), _n(PE_TOT['val'] / 1000, 1),
        _sig((PE_TOT['viv'] - PE_TOT['viv24']) / PE_TOT['viv24'] * 100), _sig((PE_TOT['val'] - PE_TOT['val24']) / PE_TOT['val24'] * 100))


def tabla_incendios():
    import auditorias
    nom = {e['abbr']: e['name'] for e in auditorias.db()['estados']}
    I = incendios(list(nom))
    filas = ''.join(
        '<tr><th scope="row">%d. %s</th><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s</td>'
        '<td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s%s %%</td></tr>' % (
            x['lh'], html.escape(nom[a]), _n(x['n']), _n(x['ha'], 2), _n(x['parb'], 1), _n(x['hxi'], 1), x['lleg'], _n(x['ha24'], 2),
            '+' if x['cam'] > 0 else '−' if x['cam'] < 0 else '', _n(abs(x['cam']), 1))
        for a, x in sorted(I.items(), key=lambda i: i[1]['lh']))
    return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Los incendios forestales de cada entidad, 2025 (hectáreas afectadas, ordenadas de más a menos)</caption>'
            '<thead><tr><th scope="col">Entidad</th><th scope="col">Incendios %s</th><th scope="col">Hectáreas %s</th><th scope="col">De árboles, de cada 100 %s</th>'
            '<th scope="col">Hectáreas por incendio %s</th><th scope="col">Llegada de la brigada (h:mm, promedio) %s</th><th scope="col">Hectáreas en 2024 %s</th>'
            '<th scope="col">Cambio de la superficie %s</th></tr></thead>'
            '<tbody>%s</tbody><tfoot><tr><th scope="row">Las 32</th><td class="num-tabular">%s</td><td class="num-tabular">%s</td><td class="num-tabular">%s</td>'
            '<td class="num-tabular">%s</td><td></td><td class="num-tabular">%s</td><td class="num-tabular">−%s %%</td></tr></tfoot></table></div>') % (
        _chip('oficial'), _chip('oficial'), _chip('derivado'), _chip('derivado'), _chip('oficial'), _chip('oficial'), _chip('derivado'), filas,
        _n(INC_TOT[25][0]), _n(INC_TOT[25][1], 2), _n(INC_TOT[25][2] / INC_TOT[25][1] * 100, 1), _n(INC_TOT[25][1] / INC_TOT[25][0], 1), _n(INC_TOT[24][1], 2),
        _n((INC_TOT[24][1] - INC_TOT[25][1]) / INC_TOT[24][1] * 100, 1))


def tabla_derechos():
    filas = ''.join('<tr><th scope="row">Art. %s · %s</th><td class="num-tabular">$%s mdp</td></tr>' % (k, html.escape(n), _n(v, 1)) for k, n, v in DERECHOS)
    return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Lo que pagó la minería en derechos, enero a junio de 2025 (cifras preliminares de Hacienda)</caption>'
            '<thead><tr><th scope="col">Derecho (Ley Federal de Derechos)</th><th scope="col">Millones de pesos %s</th></tr></thead><tbody>%s</tbody>'
            '<tfoot><tr><th scope="row">Total</th><td class="num-tabular">$%s mdp</td></tr></tfoot></table></div>') % (_chip('oficial'), filas, _n(DERECHOS_TOT, 1))


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
    uso = sorted(R, key=lambda r: -r['uso'])
    peor24 = min((r for r in R if r['d24'] is not None), key=lambda r: r['d24'])
    peor25 = min((r for r in R if r['d25'] is not None), key=lambda r: r['d25'])
    t['rn_refinerias'] = {
        'tit': 'Las refinerías de PEMEX: cuánto procesan y cuánto valen en sus libros',
        'h': ('<p>El Sistema Nacional de Refinación tiene <b>siete refinerías</b>. En junio de 2026 la que más crudo procesó fue la <b>%s</b>, con %s mil barriles diarios %s, '
              'y la que menos, la <b>%s</b>, con %s mil %s. De septiembre de 2025 a junio de 2026 el promedio de Olmeca fue de %s mil barriles diarios %s; el texto del Informe, redondeado, dice 188.</p>'
              '<p>¿Cuánto de lo que pueden procesar usan? PEMEX publica la capacidad de destilación de cada una al cierre de 2024: <b>%s mil barriles diarios</b> entre las siete %s. '
              'En los diez meses el sistema usó en promedio el <b>%s %%</b> %s. La que más, la <b>%s</b>, con el %s %%; la que menos, la <b>%s</b>, con el %s %% %s.</p>'
              '<p>Lo que casi nadie cruza está en los estados financieros de PEMEX: cada año revisa si cada refinería todavía vale lo que dicen sus libros. Si espera recuperar menos, '
              'reconoce un <b>deterioro</b> (pierde valor); si mejora, una <b>reversa</b>. En 2024 la %s perdió %s %s. En 2025 la %s recuperó %s %s por su coquizadora, y la %s perdió %s %s.</p>'
              '<p>Dos cosas que no dicen esas cifras: el deterioro es una <b>estimación contable</b> con el precio, el tipo de cambio y la tasa que supone PEMEX, no dinero que salió de la caja; '
              'y Olmeca no aparece en esa nota porque es de una filial y PEMEX la arrienda. Lo que costó Olmeca ya lo audita la plataforma en su investigación.</p>') % (
            jun[0]['n'], jun[0]['jun'], _chip('oficial'), jun[-1]['n'], jun[-1]['jun'], _chip('oficial'), format(por['olmeca']['prom'], '.1f'), _chip('derivado'),
            format(CAP_SNR, ','), _chip('oficial'), format(uso_snr(), '.1f'), _chip('derivado'), uso[0]['n'], format(uso[0]['uso'], '.1f'), uso[-1]['n'], format(uso[-1]['uso'], '.1f'), _chip('derivado'),
            peor24['n'], _mdps(peor24['d24']).lstrip('−'), _chip('oficial'), por['tula']['n'], _mdps(por['tula']['d25']).lstrip('+'), _chip('oficial'),
            peor25['n'], _mdps(peor25['d25']).lstrip('−'), _chip('oficial')),
        'ci': [{'v': '7', 'etq': 'refinerías en el Sistema Nacional de Refinación', 'e': 'oficial'},
               {'v': format(TOTAL_SNR[-1], ',') + ' mil', 'etq': 'barriles diarios de crudo procesados en junio de 2026', 'e': 'oficial'}],
        'fu': [_o('Crudo procesado por refinería y por mes, sep-25 a jun-26; el promedio de cada una es la media de los diez meses (nuestra)', _f(INF, '')),
               _o('Deterioro y reversa de 2025 por refinería', _f(EF, 'p. 59')),
               _o('Deterioro y reversa de 2024 y 2023 por refinería', _f(EF, 'p. 63')),
               _o('Valor de uso de cada refinería, 2025, 2024 y 2023', _f(EF, 'pp. 61 y 65')),
               _o('Capacidad de destilación atmosférica de cada refinería al cierre de 2024; el uso (promedio ÷ capacidad × 100) es nuestro', _f(AE, 'p. 48'))],
        'sug': ['¿Cuánto crudo procesa la refinería de Salina Cruz?', '¿Qué refinería usa más su capacidad?', '¿Cuánto costó Dos Bocas?']}
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
            '<b>Un estado sin refinería no es un estado sin problema ambiental.</b> El mapa marca dónde hay refinerías, concesiones mineras y acuíferos en déficit, no dónde hay daño. '
            'De los bosques, la plataforma ya tiene la superficie forestal y los incendios de cada estado; la proporción que tocó el fuego es una cuenta con años distintos, no la parte que se perdió.',
            '<b>La capacidad no es una meta.</b> Usar poco más de la mitad de una refinería, como hizo el sistema en esos diez meses, puede ser falta de crudo, mantenimiento o una planta que no arranca: el porcentaje dice cuánto, no por qué.',
            '<b>El libro no trae el agua,</b> que es un recurso renovable en crisis en varios estados y se explota por concesión. La plataforma la agrega con los 653 acuíferos '
            'de la CONAGUA, y su corte es de 2022 aunque la ley pide revisarlo cada dos años.']),
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
                  '<p>Su capacidad de destilación es de <b>%s mil barriles diarios</b> (PEMEX, cierre de 2024) %s: en esos diez meses usó en promedio el <b>%s %%</b> %s, '
                  'y en junio, el %s %%. Procesar crudo no es producir gasolina, y un mes bajo puede ser mantenimiento.</p>') % (
                r['n'].replace('Refinería ', 'refinería '), r['sede'], format(r['jun'], ','), _chip('oficial'), r['lug'], format(r['prom'], '.1f'), _chip('derivado'),
                r['mmax'], format(r['max'], ','), _chip('oficial'), val, format(r['cap'], ','), _chip('oficial'), format(r['uso'], '.1f'), _chip('derivado'), format(r['usoj'], '.1f')),
            'ci': [{'v': '%s mil' % format(r['jun'], ','), 'etq': 'barriles diarios de crudo, junio de 2026', 'e': 'oficial'},
                   {'v': '%s mil' % format(r['prom'], '.1f'), 'etq': 'promedio de sep-25 a jun-26', 'e': 'derivado', 'op': 'media aritmética de los diez meses'},
                   {'v': '%s %%' % format(r['uso'], '.1f'), 'etq': 'de su capacidad, en promedio', 'e': 'derivado', 'op': 'promedio de los diez meses ÷ %s mil de capacidad × 100' % r['cap']}],
            'fu': [_o('Crudo procesado por refinería y por mes', _f(INF, '')), _o('Capacidad de destilación al cierre de 2024', _f(AE, 'p. 48'))] + ([] if r['id'] == 'olmeca' else [_o('Deterioro y reversa por refinería, 2025 y 2024', _f(EF, 'pp. 59 y 63'))]),
            'sug': ['¿Cuánto crudo procesa cada refinería?', '¿Qué refinería perdió más valor?', '¿Quién audita a PEMEX?']}
    _temas_mineria(t)
    _temas_agua(t)
    _temas_incendios(t)
    _temas_pesca(t)
    for k, x in t.items():
        x['ir'] = [ARCHIVO + '#' + (k.replace('_', '-') if not k.startswith(('rn_ref_', 'rn_min_', 'rn_acu_', 'rn_if_', 'rn_pe_')) else
                                   'rn-refinerias' if k.startswith('rn_ref_') else 'rn-mineria' if k.startswith('rn_min_') else
                                   'rn-incendios' if k.startswith('rn_if_') else 'rn-pesca' if k.startswith('rn_pe_') else 'rn-agua'), TITULO]
        x['aqui'] = x['ir']
        if k.startswith(('rn_min_', 'rn_acu_', 'rn_if_', 'rn_pe_')):
            x['ir'] = [x.pop('portal').replace('.html', '-ambiental.html'), 'sus recursos naturales en el Planisferio']
    return t


def _y(xs):
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' y ' + xs[-1]


def _n(v, d=0):
    return format(v, ',.%df' % d)


def _temas_mineria(t):
    """Las concesiones mineras: el panorama nacional y una ficha por entidad."""
    import auditorias
    import planisferio
    E = auditorias.db()['estados']
    nom = {e['abbr']: e['name'] for e in E}
    M = mineria(list(nom))
    orden = sorted(M, key=lambda a: -M[a]['t'])
    sin_prod = [a for a in orden if M[a]['prod'] is None]
    fp = _f(PRONT, 'p. 20')
    fi = {'tx': 'Presidencia de la República, Segundo Informe de Gobierno 2025-2026, sector minero, %s' % INF_MIN, 'url': INF['url']}
    fd = {'tx': 'Secretaría de Economía, Prontuario Estadístico de la Minería, enero-junio 2025, «Recaudación fiscal del sector minero», p. 21 (cifras preliminares de Hacienda)', 'url': PRONT['url']}
    d26 = sorted(MIN26, key=lambda a: MIN26[a] - M[a]['t'])
    implicita = round(NAC26['rec'] / 0.15, 1)
    t['rn_mineria'] = {
        'tit': 'Las concesiones mineras, estado por estado',
        'h': ('<p>Los minerales son de la Nación y un particular solo los explota con una <b>concesión</b> de la Secretaría de Economía. En marzo de 2024 había '
              '<b>%s títulos</b> vigentes sobre <b>%s hectáreas</b> %s, en %d entidades. <b>%s</b> tenía más que nadie: %s títulos %s, el %s %% del país %s; '
              'le seguían %s y %s. %s no figuran en el cuadro.</p>'
              '<p>El Segundo Informe da un corte más nuevo, pero solo nacional y de cuatro estados: al 30 de junio de 2026 quedaban <b>%s títulos</b> sobre '
              '<b>%s millones de hectáreas</b>, el %s %% del territorio %s, y se habían cancelado %s concesiones por incumplir sus obligaciones, con %s millones de hectáreas '
              'de vuelta al Estado %s.</p>'
              '<p>Lo que paga una mina se ve en la Ley Federal de Derechos: de enero a junio de 2025 la minería pagó <b>$%s mdp</b> en derechos %s, y de ellos solo '
              '$%s mdp fueron la cuota por hectárea concesionada (art. 263); lo demás se cobra sobre lo que vende y extrae (arts. 268 a 270). Esa recaudación no se publica por estado.</p>') % (
            _n(MINAS_TOT[0]), _n(MINAS_TOT[1]), _chip('oficial'), len(M), nom[orden[0]], _n(M[orden[0]]['t']), _chip('oficial'), _n(M[orden[0]]['pt'], 2), _chip('derivado'),
            nom[orden[1]], nom[orden[2]], _y([nom[a] for a in sorted(set(nom) - set(M))]),
            _n(NAC26['t']), _n(NAC26['mha'], 2), _n(NAC26['pct'], 1), _chip('oficial'), _n(NAC26['canc']), _n(NAC26['rec'], 2), _chip('oficial'),
            _n(DERECHOS_TOT, 1), _chip('oficial'), _n(DERECHOS[0][2], 1)),
        'ci': [{'v': _n(MINAS_TOT[0]), 'etq': 'títulos de concesión minera vigentes en marzo de 2024 (DGM)', 'e': 'oficial'},
               {'v': _n(NAC26['t']), 'etq': 'títulos vigentes al 30 de junio de 2026 (Segundo Informe)', 'e': 'oficial'},
               {'v': '$%s mdp' % _n(DERECHOS_TOT, 1), 'etq': 'derechos mineros pagados de enero a junio de 2025 (preliminar)', 'e': 'oficial'}],
        'fu': [_o('Títulos y hectáreas concesionadas por entidad, marzo de 2024; las partes de cada estado y las hectáreas por título son nuestras', fp),
               _o('Títulos y superficie al 30 de junio de 2026, cancelaciones y las entidades con producción minera', fi),
               _o('Derechos mineros de enero a junio de 2025 (Ley Federal de Derechos, arts. 263, 268, 269 y 270)', fd),
               _o('Concesiones, concurso, plazo y exclusiones (arts. 5, 14 Bis y 15)', ley('lmin', 'arts. 5, 14 Bis y 15'))],
        'sug': ['¿Cuántas concesiones mineras tiene Sonora?', '¿Qué estado tiene más concesiones mineras?', '¿Cuánto paga una mina por su concesión?']}
    t['rn_mineria_ciegos'] = {
        'tit': 'Lo que el cuadro de concesiones no dice',
        'h': '<p>Cinco cosas que conviene preguntar antes de leer el mapa de las minas:</p>%s' % _lista([
            ('<b>Una concesión no es una mina trabajando.</b> %s tienen concesiones y no aparecen entre las 27 entidades con producción minera que enlista el Informe. '
             'La concesión da el derecho a explorar y explotar; no dice que ya se excave.') % _y([nom[a] for a in sin_prod]),
            '<b>Hectárea concesionada no es hectárea excavada.</b> El cuadro mide el terreno que ampara cada título, no el tajo ni la presa de jales.',
            ('<b>Dos cortes que no se explican entre sí.</b> En marzo de 2024 eran %s millones de hectáreas %s; en junio de 2026, %s millones %s. Pero el Informe dice que los %s millones '
             'de hectáreas recuperadas son el 15 %% de lo concesionado en octubre de 2024, lo que daría unos %s millones %s (cuenta nuestra). Pudo haber concesiones vencidas o '
             'renuncias en medio, pero ninguno de los dos documentos lo explica. Es pregunta para la Secretaría de Economía.') % (
                _n(MINAS_TOT[1] / 1e6, 2), _chip('oficial'), _n(NAC26['mha'], 2), _chip('oficial'), _n(NAC26['rec'], 2), _n(implicita, 1), _chip('derivado')),
            ('<b>El cuadro por estado no se ha puesto al día.</b> El Prontuario de enero-junio de 2025 repite el corte de marzo de 2024; el Informe solo da cuatro estados al día: %s.') % '; '.join(
                '%s, %s títulos (%s)' % (nom[a], _n(MIN26[a]), ('−' if MIN26[a] < M[a]['t'] else '+') + _n(abs(MIN26[a] - M[a]['t']))) for a in d26),
            '<b>La grava y la arena no están ahí.</b> La Ley de Minería no se aplica a las rocas que solo sirven para materiales de construcción (art. 5, fr. IV): '
            'esos bancos de material los regulan los estados y municipios, y no salen en este cuadro.']),
        'fu': [_o('Títulos y hectáreas por entidad, marzo de 2024', fp), _o('Corte de junio de 2026, cancelaciones y entidades con producción', fi),
               _o('Exclusión de las rocas para construcción (art. 5, fr. IV)', ley('lmin', 'art. 5'))],
        'sug': ['¿Qué estado tiene más concesiones mineras?', '¿Cuántas concesiones mineras se cancelaron?', '¿Qué ley rige la minería?']}
    for a in nom:
        x = M.get(a)
        if x:
            cambio = ''
            if x['t26'] is not None:
                cambio = (' Al 30 de junio de 2026 el Segundo Informe le cuenta <b>%s títulos</b> %s: %s %s que en marzo de 2024 %s.') % (
                    _n(x['t26']), _chip('oficial'), _n(abs(x['t26'] - x['t'])), 'menos' if x['t26'] < x['t'] else 'más', _chip('derivado'))
            prod = {'mayor': 'Es una de las diez entidades que dan el 94.9 % del valor de la producción minera del país.',
                    'menor': 'Está entre las 17 entidades que juntas dan el 5.2 % del valor de la producción minera.',
                    None: 'No aparece entre las 27 entidades con producción minera que enlista el Informe: tener concesiones no es lo mismo que tener minas trabajando.'}[x['prod']]
            h = ('<p>En marzo de 2024 <b>%s</b> tenía <b>%s títulos de concesión minera</b> vigentes %s, sobre <b>%s hectáreas</b> %s: el lugar %d de %d entidades, '
                 'con el %s %% de los títulos del país %s y unas %s hectáreas por título %s.%s</p><p>%s</p>'
                 '<p>Que una empresa tenga una concesión no es una irregularidad: lo que se audita es que pague sus derechos, cumpla sus obligaciones y repare el daño. '
                 'Hectárea concesionada no es hectárea excavada, y lo que paga la minería no se publica por estado.</p>') % (
                nom[a], _n(x['t']), _chip('oficial'), _n(x['ha']), _chip('oficial'), x['lug'], len(M), _n(x['pt'], 2), _chip('derivado'), _n(x['hxt']), _chip('derivado'), cambio, prod)
            ci = [{'v': _n(x['t']), 'etq': 'títulos de concesión minera, marzo de 2024', 'e': 'oficial'},
                  {'v': _n(x['ha']) + ' ha', 'etq': 'superficie concesionada', 'e': 'oficial'}]
            if x['t26'] is not None:
                ci.append({'v': _n(x['t26']), 'etq': 'títulos al 30 de junio de 2026', 'e': 'oficial'})
            fu = [_o('Títulos y hectáreas por entidad, marzo de 2024; su parte del país y las hectáreas por título son nuestras', fp), _o('Entidades con producción minera y corte de junio de 2026', fi)]
        else:
            h = ('<p><b>%s</b> no figura en el cuadro de concesiones mineras por entidad de la Dirección General de Minas (marzo de 2024), que trae 30 entidades, ni entre las 27 '
                 'con producción minera del Segundo Informe.</p><p>Eso no quiere decir que no se extraiga nada de su suelo: la Ley de Minería no se aplica a las rocas que solo sirven '
                 'para materiales de construcción (art. 5, fr. IV), y esos bancos de grava y arena no salen en el cuadro.</p>') % nom[a]
            ci = []
            fu = [_o('Las 30 entidades del cuadro de concesiones', fp), _o('Exclusión de las rocas para construcción (art. 5, fr. IV)', ley('lmin', 'art. 5'))]
        t['rn_min_' + planisferio.clave(a)] = {
            'tit': '%s: sus concesiones mineras' % nom[a], 'h': h, 'ci': ci, 'fu': fu, 'portal': planisferio.portal(a), 'edo': a,
            'sug': ['¿Qué estado tiene más concesiones mineras?', '¿Cuánto paga una mina por su concesión?', '¿Cuánto crudo procesa cada refinería?']}


def _hm3(v, d=1):
    return format(v, ',.%df' % d) + ' hm³'


def _temas_agua(t):
    """El agua del subsuelo: el panorama nacional, sus puntos ciegos y una
    ficha por entidad."""
    import auditorias
    import planisferio
    E = auditorias.db()['estados']
    nom = {e['abbr']: e['name'] for e in E}
    A = acuiferos(list(nom))
    fa = _f(ACU, 'artículo primero')
    fp = {'tx': PNH['tx'], 'url': PNH['url']}
    fi = lambda k: {'tx': 'Presidencia de la República, Segundo Informe de Gobierno 2025-2026, %s' % INF_AGUA[k], 'url': INF['url']}
    de = sorted((a for a in A if A[a]['def'] > 0), key=lambda a: -A[a]['def'])
    todos = sorted((a for a in A if A[a]['sin'] == A[a]['n']), key=lambda a: nom[a])
    ninguno = sorted((a for a in A if A[a]['sin'] == 0), key=lambda a: nom[a])
    tot_def = ACU_SUMAS[0]
    dif = [(a, c, n, d) for a, xs in SOBRE27.items() for c, n, d in xs if d > 0]
    s27 = sum(len(x) for x in SOBRE27.values())
    t['rn_agua'] = {
        'tit': 'El agua del subsuelo, estado por estado',
        'h': ('<p>El agua del subsuelo es de la Nación y se usa por <b>concesión o asignación</b> de la Comisión Nacional del Agua (Constitución, art. 27, párrafo sexto). '
              'Antes de dar una, la CONAGUA debe tomar en cuenta la <b>disponibilidad media anual</b> del acuífero: el agua que todavía se puede sacar además de la ya '
              'concesionada y de la que la naturaleza necesita (Ley de Aguas Nacionales, art. 3, fr. XXIV, y art. 22). Si sale negativa, el acuífero tiene <b>déficit</b>: '
              'en el papel ya se comprometió más agua de la que se recarga, descontada la que necesita la naturaleza.</p>'
              '<p>El país tiene <b>%s acuíferos</b>. Con corte al 30 de diciembre de 2022, <b>%s tenían disponibilidad y %s no</b> %s. Sumados, los déficits dan '
              '<b>%s al año</b> %s. <b>%s</b> tiene el mayor: %s de sus %s acuíferos sin disponibilidad, con %s de déficit %s. En %s ninguno tiene disponibilidad; '
              'en %s, ninguno está en déficit.</p>'
              '<p>Siete de cada diez litros que se sacan del subsuelo van al campo: en 2023, el %s %% fue para uso agrícola, el %s %% para el abastecimiento público, '
              'el %s %% para la industria y el %s %% para generar electricidad %s.</p>'
              '<p>Lo más nuevo está en el Segundo Informe: la CONAGUA midió con %s pozos los niveles de %s acuíferos, y en <b>%s de ellos, en condición de sobreexplotación</b>, '
              'usó %s pozos %s; actualizó el balance de %s acuíferos, revisó <b>%s títulos de concesión</b> de agua y encontró <b>%s inconsistencias</b> %s. '
              'De septiembre de 2025 a junio de 2026 se cobraron <b>$%s mdp</b> en derechos y aprovechamientos por aguas nacionales %s; ese cobro no se publica por estado.</p>') % (
            _n(ACU_TOT[0]), _n(ACU_TOT[1]), _n(ACU_TOT[2]), _chip('oficial'), _hm3(tot_def), _chip('derivado'),
            nom[de[0]], A[de[0]]['sin'], A[de[0]]['n'], _hm3(A[de[0]]['def']), _chip('derivado'), _y([nom[a] for a in todos]), _y([nom[a] for a in ninguno]),
            _n(USO_SUB[0][1], 1), _n(USO_SUB[1][1], 1), _n(USO_SUB[2][1], 1), _n(USO_SUB[3][1], 1), _chip('oficial'),
            _n(AGUA26['pozos']), AGUA26['mon'], s27, _n(AGUA26['pozos_s']), _chip('oficial'), AGUA26['bal'], _n(AGUA26['tit']), _n(AGUA26['inc']), _chip('oficial'),
            _n(AGUA26['rec'], 1), _chip('oficial')),
        'ci': [{'v': '%s de %s' % (_n(ACU_TOT[2]), _n(ACU_TOT[0])), 'etq': 'acuíferos sin disponibilidad, corte de diciembre de 2022', 'e': 'oficial'},
               {'v': _hm3(tot_def), 'etq': 'suma de sus déficits, al año', 'e': 'derivado', 'op': 'suma de la disponibilidad negativa de los %d acuíferos en déficit' % ACU_TOT[2]},
               {'v': _n(AGUA26['inc']), 'etq': 'inconsistencias en %s títulos de agua revisados' % _n(AGUA26['tit']), 'e': 'oficial'}],
        'fu': [_o('Disponibilidad de los 653 acuíferos, por entidad; las sumas por estado y la nacional de los déficits son nuestras', fa),
               _o('Acuíferos con y sin disponibilidad y usos del agua subterránea en 2023', fp),
               _o('Los %d acuíferos sobreexplotados que se miden con pozos' % s27, fi('s27')), _o('Títulos de concesión revisados', fi('tit')),
               _o('Derechos y aprovechamientos por aguas nacionales', fi('rec')),
               _o('Disponibilidad y su revisión (arts. 3, fr. XXIV, y 22)', ley('lan', 'arts. 3 y 22'))],
        'sug': ['¿Cuántos acuíferos de Chihuahua están en déficit?', '¿Qué acuíferos están sobreexplotados?', '¿Cuánta agua se le debe al subsuelo?']}
    t['rn_agua_ciegos'] = {
        'tit': 'Lo que el mapa del agua no dice',
        'h': '<p>Cinco preguntas que conviene hacer antes de leer el mapa de los acuíferos:</p>%s' % _lista([
            '<b>La disponibilidad no es el agua que hay.</b> Es lo que todavía se puede concesionar. Un acuífero en déficit no está vacío: tiene más agua comprometida en títulos '
            'de la que se recarga. Y uno con disponibilidad puede estar contaminado: aquí se mide cantidad, no calidad.',
            ('<b>Sin disponibilidad no es lo mismo que sobreexplotado.</b> El Segundo Informe cuenta en sobreexplotación a %s, y el Acuerdo de 2023 les da disponibilidad '
             '(%s). No necesariamente se contradicen: la sobreexplotación se refiere a lo que se extrae, y la disponibilidad, a lo que está concesionado. Si se extrae más de lo concesionado, '
             'hay pozos sin título o mediciones distintas; '
             'es pregunta para la CONAGUA.') % (_y(['%s (%s)' % (n, nom[a]) for a, c, n, d in dif]), '; '.join('%s: +%s %s' % (n, _hm3(d, 2), _chip('oficial')) for a, c, n, d in dif)),
            ('<b>El corte ya pasó del plazo de la ley.</b> La disponibilidad se debe revisar al menos cada dos años (Ley de Aguas Nacionales, art. 22, reformado el 11-12-2025; antes '
             'decía tres). La última publicada es la del DOF del 9 de noviembre de 2023, con corte de 2022, y el Programa Nacional Hídrico de mayo de 2026 todavía la usa. El Informe dice '
             'que se actualizaron %s balances, pero el acuerdo nuevo no se ha publicado %s.') % (AGUA26['bal'], _chip('pendiente', 'acuiferos-disponibilidad-nueva')),
            '<b>Un acuífero no respeta fronteras.</b> El Acuerdo agrupa cada acuífero en una sola entidad, aunque su agua cruce los límites: la Península de Yucatán, por ejemplo, '
            'sale en Yucatán.',
            ('<b>Los %d de la lista son los que se miden, no todos los sobreexplotados.</b> La CONAGUA vigila con pozos los niveles de %s acuíferos; el Informe no publica cuántos '
             'de los %s están sobreexplotados en total.') % (s27, AGUA26['mon'], _n(ACU_TOT[0]))]),
        'fu': [_o('Disponibilidad de los 653 acuíferos', fa), _o('Acuíferos sobreexplotados medidos con pozos y balances actualizados', fi('s27')),
               _o('Revisión de la disponibilidad «al menos cada dos años» (art. 22)', ley('lan', 'art. 22')), _o('El Programa Nacional Hídrico usa el corte de 2023', fp)],
        'sug': ['¿Qué estado tiene más acuíferos en déficit?', '¿Qué ley rige el agua?', '¿Cuántas concesiones mineras tiene Sonora?']}
    for a in nom:
        x = A[a]
        if x['def'] > 0:
            lugar = 'el lugar %d de %d entidades con déficit %s' % (x['lug'], len(de), _chip('derivado'))
            h1 = ('<p>Con corte al 30 de diciembre de 2022, <b>%s</b> tenía <b>%d acuíferos</b>: <b>%d sin disponibilidad</b> y %d con ella %s. De cada 100, %s no tenían '
                  'agua para concesionar %s. Sumados, sus déficits dan <b>%s al año</b> %s: %s.</p>') % (
                nom[a], x['n'], x['sin'], x['con'], _chip('oficial'), _n(x['ps'], 1), _chip('derivado'), _hm3(x['def']), _chip('derivado'), lugar)
        else:
            h1 = ('<p>Con corte al 30 de diciembre de 2022, <b>%s</b> tenía <b>%d %s</b> y %s en déficit %s: %s de disponibilidad al año %s. Eso dice que todavía hay agua '
                  'para concesionar, no que esté limpia: la disponibilidad mide cantidad, no calidad.</p>') % (
                nom[a], x['n'], 'acuífero' if x['n'] == 1 else 'acuíferos', 'no estaba' if x['n'] == 1 else 'ninguno estaba', _chip('oficial'), _hm3(x['disp']), _chip('derivado'))
        h2 = ''
        if x['s27']:
            k = len(x['s27'])
            h2 = ('<p>%s está%s entre los %d acuíferos sobreexplotados que la CONAGUA mide con pozos, según el Segundo Informe: %s %s.%s</p>') % (
                'Uno de sus acuíferos' if k == 1 else '%s de sus acuíferos' % {2: 'Dos', 3: 'Tres', 4: 'Cuatro', 5: 'Cinco'}.get(k, str(k)), '' if k == 1 else 'n',
                s27, _y([n for c, n, d in x['s27']]), _chip('oficial'),
                ''.join(' Ojo: el Acuerdo de 2023 le da disponibilidad a %s (+%s): sobreexplotado y sin disponibilidad no son lo mismo.' % (n, _hm3(d, 2)) for c, n, d in x['s27'] if d > 0))
        ci = [{'v': '%d de %d' % (x['sin'], x['n']), 'etq': 'acuíferos sin disponibilidad (corte 2022)', 'e': 'oficial'}]
        if x['def'] > 0:
            ci.append({'v': _hm3(x['def']), 'etq': 'suma de sus déficits, al año', 'e': 'derivado', 'op': 'suma de la disponibilidad negativa de sus acuíferos'})
        fu = [_o('Disponibilidad de cada acuífero; las sumas y los porcentajes por estado son nuestros', fa)]
        if x['s27']:
            fu.append(_o('Acuíferos sobreexplotados medidos con pozos', fi('s27')))
        t['rn_acu_' + planisferio.clave(a)] = {
            'tit': '%s: sus acuíferos' % nom[a], 'h': h1 + h2 + '<p>La ley pide revisar la disponibilidad al menos cada dos años (art. 22); este corte es de 2022.</p>',
            'ci': ci, 'fu': fu, 'portal': planisferio.portal(a), 'edo': a,
            'sug': ['¿Qué estado tiene más acuíferos en déficit?', '¿Qué acuíferos están sobreexplotados?', '¿Cuántas concesiones mineras tiene %s?' % nom[a]]}


def _ha(v, d=0):
    return format(v, ',.%df' % d) + ' ha'


def _temas_incendios(t):
    """Los incendios forestales: el panorama nacional, sus puntos ciegos y una
    ficha por entidad."""
    import auditorias
    import planisferio
    E = auditorias.db()['estados']
    nom = {e['abbr']: e['name'] for e in E}
    I = incendios(list(nom))
    F = forestal(list(nom))
    fq = min(F, key=lambda a: F[a]['lq'])
    fc = lambda c: _f(INC_DOC, c)
    fs = lambda c: _f(SF_DOC, c)
    N = INC_NAC
    n25, h25, a25 = INC_TOT[25]
    n24, h24 = INC_TOT[24]
    oh = sorted(I, key=lambda a: I[a]['lh'])
    on = sorted(I, key=lambda a: I[a]['ln'])
    top = oh[0]
    masn = on[0]
    grande = max(I, key=lambda a: I[a]['hxi'] or 0)
    sube = max(I, key=lambda a: I[a]['cam'])
    baja = min(I, key=lambda a: I[a]['cam'])
    p = lambda x, y: _n(x / y * 100, 1)
    lgdfs = ley('lgdfs', 'arts. 117 a 121 y 155')
    t['rn_incendios'] = {
        'tit': 'Los incendios forestales, estado por estado',
        'h': ('<p>Los bosques, las selvas y los matorrales son un recurso renovable: se reponen si se les deja. El fuego es la amenaza que se mide cada semana. La ley reparte la tarea: '
              'el <b>municipio</b> atiende el combate inicial; si lo rebasa, va el <b>estado</b>, y si tampoco alcanza, la <b>Comisión Nacional Forestal</b>, que coordina el Programa de '
              'Manejo del Fuego (Ley General de Desarrollo Forestal Sustentable, art. 119). Quien tiene el terreno debe restaurar lo quemado en un plazo máximo de dos años (art. 121), '
              'y provocar un incendio forestal es infracción (art. 155).</p>'
              '<p>En 2025 hubo <b>%s incendios forestales</b> en las 32 entidades, que afectaron <b>%s</b> %s. Fue %s %% menos superficie que en 2024, el año más alto de la serie que publica la CONAFOR (1998 y 2011 a 2025), con %s %s; '
              'pero %s veces el promedio de 1998 a 2024, de %s al año %s.</p>'
              '<p><b>%s</b> tuvo la mayor superficie afectada: %s en %s incendios %s, el %s %% del país %s. <b>%s</b> tuvo más incendios, %s, pero quedó en el lugar %d por superficie. '
              '<b>%s</b> tuvo los más grandes: %s por incendio %s, y su brigada tardó en promedio %s horas en llegar %s.</p>'
              '<p>De cada 100 hectáreas afectadas, solo %s eran de árboles (arbolado adulto y renuevo) %s; el resto, pasto, matorral y hojarasca. La CONAFOR clasificó el '
              '%s %% de la superficie como de impacto mínimo y el %s %% como de impacto severo %s. En el combate se aplicaron %s días-persona %s.</p>') % (
            _n(n25), _ha(h25, 2), _chip('oficial'), _n((h24 - h25) / h24 * 100, 1), _ha(h24, 2), _chip('oficial'),
            _n(h25 / N['prom_ha'], 1), _ha(N['prom_ha']), _chip('derivado'),
            nom[top], _ha(I[top]['ha'], 2), _n(I[top]['n']), _chip('oficial'), _n(I[top]['ph'], 1), _chip('derivado'), nom[masn], _n(I[masn]['n']), I[masn]['lh'],
            nom[grande], _ha(I[grande]['hxi'], 1), _chip('derivado'), I[grande]['lleg'], _chip('oficial'),
            p(a25, h25), _chip('derivado'), p(N['min'], h25), p(N['sev'], h25), _chip('derivado'), _n(N['dp']), _chip('oficial')),
        'ci': [{'v': _n(n25), 'etq': 'incendios forestales en 2025', 'e': 'oficial'},
               {'v': _ha(h25), 'etq': 'superficie afectada en 2025', 'e': 'oficial'},
               {'v': '%s %%' % p(a25, h25), 'etq': 'de esa superficie era de árboles', 'e': 'derivado', 'op': 'arbolado adulto + renuevo ÷ superficie total × 100'}],
        'fu': [_o('Incendios y superficie por entidad, 2025 (cuadro 4); el promedio 1998-2024 (cuadro 7); el impacto (cuadro 9). Los porcentajes y las veces son nuestros', fc('cuadros 4, 7 y 9')),
               _o('Incendios y superficie por entidad, 2024', _f(INC_DOC24, 'cuadro 4')),
               _o('Quién combate, la restauración y la infracción', lgdfs)],
        'sug': ['¿Cuántos incendios forestales hubo en Chihuahua?', '¿Qué estado tuvo más incendios forestales?', '¿Qué no dicen las cifras de incendios?']}
    arb = sum(F[a]['arb'] for a in F)
    of = sorted(F, key=lambda a: F[a]['lug'])
    c5 = sum(F[a]['sf'] for a in of[:5]) / SF_TOT[6] * 100
    if round(c5, 1) != 48.8:
        raise SystemExit('recursos_naturales: los cinco estados con más superficie forestal ya no suman el 48.8 %% que dice la CONAFOR (%.1f)' % c5)
    pa = lambda a: _n(F[a]['pq'], 1) if F[a]['pq'] >= 0.05 else 'menos de 0.1'
    t['rn_bosques'] = {
        'tit': 'Los bosques de cada estado: su superficie forestal',
        'h': ('<p>México tiene <b>%s de vegetación forestal</b> %s: siete de cada diez hectáreas del país (el 70.6 %%, según la CONAFOR). Pero «forestal» no quiere decir «bosque»: '
              'el %s %% es matorral xerófilo, el de las zonas secas; el %s %% son bosques templados y el %s %% selvas %s. Lo arbolado (bosques, selvas, manglar y otras asociaciones) '
              'suma %s, el %s %% %s. Y de toda esa superficie, el %s %% es vegetación secundaria %s: la que ya fue alterada y se está recuperando.</p>'
              '<p><b>%s</b> tiene la mayor superficie forestal, %s %s, y con %s, %s, %s y %s junta el %s %% del país %s. %s, la menor: %s.</p>'
              '<p><b>Frente al fuego.</b> Los incendios de 2025 afectaron el equivalente a %s de cada 100 hectáreas forestales del país, y lo afectado de árboles, a %s de cada 100 '
              'arboladas %s. Por estado, el más alto fue <b>%s</b>: %s de cada 100 %s, aunque por hectáreas quedó en el lugar %d. %s, el de más superficie afectada, quedó en %s de cada 100.</p>'
              '<p><b>Lo que esta cifra no dice.</b> El mapa de la vegetación es de 2018 (Serie VII del INEGI): no es la superficie de hoy, y el desmonte de después no está restado. '
              'Lo secundario no es lo perdido, y lo arbolado incluye «otras asociaciones». El documento imprime cortado el matorral de Chiapas y de la Ciudad de México: '
              'los tomamos como el total menos las otras columnas %s, y la fila de Querétaro no suma su total por 0.9 ha.</p>') % (
            _ha(SF_TOT[6], 1), _chip('oficial'), _n(SF_TOT[4] / SF_TOT[6] * 100, 1), _n(SF_TOT[0] / SF_TOT[6] * 100, 1), _n(SF_TOT[1] / SF_TOT[6] * 100, 1), _chip('oficial'),
            _ha(arb), _n(arb / SF_TOT[6] * 100, 1), _chip('derivado'), _n(SF_TOT[8] / SF_TOT[6] * 100, 1), _chip('oficial'),
            nom[of[0]], _ha(F[of[0]]['sf']), _chip('oficial'), nom[of[1]], nom[of[2]], nom[of[3]], nom[of[4]], _n(c5, 1), _chip('derivado'), nom[of[-1]], _ha(F[of[-1]]['sf'], 1),
            _n(h25 / SF_TOT[6] * 100, 1), _n(a25 / arb * 100, 2), _chip('derivado'), nom[fq], pa(fq), _chip('derivado'), I[fq]['lh'], nom[top], pa(top), _chip('derivado')),
        'ci': [{'v': _ha(SF_TOT[6]), 'etq': 'de vegetación forestal en el país', 'e': 'oficial'},
               {'v': '%s %%' % _n(arb / SF_TOT[6] * 100, 1), 'etq': 'de esa superficie es arbolada', 'e': 'derivado', 'op': '(bosques + selvas + manglar + otras asociaciones) ÷ total forestal × 100'},
               {'v': '%s %%' % _n(h25 / SF_TOT[6] * 100, 1), 'etq': 'equivalente que tocó el fuego de 2025', 'e': 'derivado', 'op': 'superficie afectada 2025 ÷ superficie forestal × 100'}],
        'fu': [_o('Superficie forestal por tipo de vegetación y por condición, en cada entidad', fs('tabla 1, p. 4, y tabla 2, pp. 10-11')),
               _o('La superficie afectada por los incendios de 2025, por entidad', fc('cuadro 4')),
               _o('Lo arbolado, las proporciones y los lugares', fs('tabla 1, p. 4'), 'derivado')],
        'sug': ['¿Cuánto bosque tiene Durango?', '¿Qué estado tuvo más incendios forestales?', '¿Qué no dicen las cifras de incendios?']}
    t['rn_incendios_ciegos'] = {
        'tit': 'Lo que las cifras de incendios no dicen',
        'h': '<p>Siete preguntas que conviene hacer antes de leer el mapa del fuego:</p>%s' % _lista([
            ('<b>Superficie afectada no es bosque perdido.</b> De las %s de 2025, el %s %% fue pasto, matorral y hojarasca, y la CONAFOR calificó de impacto mínimo el %s %% %s, '
             'donde muere menos del 20 %% del arbolado. El impacto severo, donde muere más de la mitad, fue de %s %s.') % (
                _ha(h25), _n(100 - a25 / h25 * 100, 1), p(N['min'], h25), _chip('derivado'), _ha(N['sev'], 2), _chip('oficial')),
            ('<b>No todo fuego es daño.</b> La CONAFOR cuenta %s incendios, en %s, en ecosistemas que dependen del fuego para renovarse %s, y %s, en %s, en ecosistemas sensibles a él, '
             'donde el daño es mayor (NOM-015-SEMARNAT/AGRICULTURA-2023).') % (_n(N['dep_n']), _ha(N['dep_ha'], 2), _chip('oficial'), _n(N['sens_n']), _ha(N['sens_ha'], 2)),
            ('<b>Un año no es la tendencia.</b> 2024 fue el más alto de la serie y 2025 bajó, pero quedó en %s veces el promedio de 1998 a 2024. Por estado los saltos son enormes: %s subió %s %% (de %s a %s) y %s bajó %s %% %s; '
             'sobre una base chica, un solo incendio grande cambia el porcentaje.') % (
                _n(h25 / N['prom_ha'], 1), nom[sube], _n(I[sube]['cam'], 1), _ha(I[sube]['ha24']), _ha(I[sube]['ha']), nom[baja], _n(-I[baja]['cam'], 1), _chip('derivado')),
            ('<b>Muchos incendios no es mucha superficie.</b> %s tuvo %s incendios y %s, %s, pero %s quemó más terreno: %s contra %s %s. Lo que cambia la superficie es cuánto tarda la brigada en llegar y '
             'cuánto dura el fuego.') % (nom[masn], _n(I[masn]['n']), nom[grande], _n(I[grande]['n']), nom[grande], _ha(I[grande]['ha']), _ha(I[masn]['ha']), _chip('oficial')),
            ('<b>La cifra cambia después de la temporada.</b> Los reportes semanales no son el cierre: solo la última semana de 2025 sumó %d incendios de fechas anteriores, con %s, que no se habían '
             'reportado %s. Una nota con la cifra de mayo o de junio no es la del año.') % (N['tarde_n'], _ha(N['tarde_ha'], 2), _chip('oficial')),
            ('<b>Los tiempos no cuadran entre documentos.</b> El cierre de 2025 dice que en 2024 un incendio se detectaba en promedio en %s (horas:minutos); el cierre de 2024 había dicho %s %s. '
             'Con dos cifras de la misma dependencia para el mismo año, la comparación de tiempos es pregunta para la CONAFOR.') % (N['det24_en25'], N['det24_en24'], _chip('oficial')),
            ('<b>La parte del bosque que tocó el fuego mezcla años.</b> Frente a su superficie forestal, el fuego de 2025 afectó %s de cada 100 hectáreas del país %s, y en %s, %s. '
             'Pero el fuego es de 2025 y el mapa de la vegetación, de 2018 (Serie VII del INEGI), y la superficie de cada incendio se suma aunque dos incendios del año hayan pasado por el mismo terreno: es una proporción, no la parte que se perdió.') % (
                _n(h25 / SF_TOT[6] * 100, 1), _chip('derivado'), nom[fq], _n(F[fq]['pq'], 1))]),
        'fu': [_o('Impacto, ecosistemas, días-persona e incendios integrados con retraso', fc('resumen ejecutivo y cuadros 7, 9, 10 y 11')),
               _o('El tiempo de detección de 2024 en su propio cierre', _f(INC_DOC24, 'cuadro 4')),
               _o('La superficie forestal de cada entidad; la proporción afectada es nuestra', fs('tabla 1, p. 4'), 'derivado')],
        'sug': ['¿Qué estado tuvo más superficie quemada?', '¿Cuántos acuíferos de Chihuahua están en déficit?', '¿Quién combate los incendios forestales?']}
    for a in nom:
        x = I[a]
        f = F[a]
        cam = ('%s %s %% contra 2024 (%s en %s incendios) %s' % ('subió' if x['cam'] > 0 else 'bajó', _n(abs(x['cam']), 1), _ha(x['ha24'], 2), _n(x['n24']), _chip('derivado'))
               if x['cam'] else 'igual que en 2024')
        h = ('<p>En 2025, <b>%s</b> tuvo <b>%s incendios forestales</b> que afectaron <b>%s</b> %s: el lugar %d de 32 por superficie y el %d por número de incendios %s. '
             'La superficie %s.</p>'
             '<p>De cada 100 hectáreas afectadas, %s eran de árboles %s. Cada incendio afectó en promedio %s %s, y la brigada tardó en promedio %s horas en llegar %s.</p>'
             '<p><b>Su superficie forestal</b> es de %s %s, el lugar %d de 32 y el %s %% del país %s. De cada 100 hectáreas, %s son arboladas (bosques, selvas, manglar y otras asociaciones) '
             'y %s son vegetación secundaria %s. El fuego de 2025 afectó el equivalente a %s de cada 100 hectáreas forestales del estado (lugar %d de 32) %s; es una proporción con el mapa de 2018, '
             'no la parte que se perdió.</p>'
             '<p>%sEl combate inicial le toca al municipio, luego al estado y luego a la CONAFOR '
             '(Ley General de Desarrollo Forestal Sustentable, art. 119), y quien tiene el terreno debe restaurarlo en dos años (art. 121).</p>') % (
            nom[a], _n(x['n']), _ha(x['ha'], 2), _chip('oficial'), x['lh'], x['ln'], _chip('derivado'), cam,
            _n(x['parb'], 1), _chip('derivado'), _ha(x['hxi'], 1), _chip('derivado'), x['lleg'], _chip('oficial'),
            _ha(f['sf'], 1), _chip('oficial'), f['lug'], _n(f['pnac'], 1) if f['pnac'] >= 0.05 else 'menos del 0.1', _chip('derivado'), _n(f['parb'], 1), _n(f['psec'], 1), _chip('derivado'),
            pa(a), f['lq'], _chip('derivado'),
            'Superficie afectada no es bosque perdido: aquí la mayor parte del fuego corrió por pasto, matorral y hojarasca. ' if x['parb'] < 50 else
            'Aquí la mayor parte de lo afectado fue de árboles, y aun así superficie afectada no es bosque perdido: el daño depende del impacto. ')
        t['rn_if_' + planisferio.clave(a)] = {
            'tit': '%s: sus bosques y sus incendios forestales' % nom[a], 'h': h,
            'ci': [{'v': _ha(f['sf']), 'etq': 'de superficie forestal', 'e': 'oficial'},
                   {'v': _n(x['n']), 'etq': 'incendios forestales en 2025', 'e': 'oficial'},
                   {'v': _ha(x['ha']), 'etq': 'superficie afectada en 2025', 'e': 'oficial'},
                   {'v': '%s%s %%' % ('+' if x['cam'] > 0 else '−' if x['cam'] < 0 else '', _n(abs(x['cam']), 1)), 'etq': 'superficie contra 2024', 'e': 'derivado',
                    'op': '(superficie 2025 − superficie 2024) ÷ superficie 2024 × 100'}],
            'fu': [_o('Su superficie forestal, por tipo y por condición de la vegetación', fs('tabla 1, p. 4, y tabla 2, pp. 10-11')),
                   _o('Incendios y superficie de 2025 por entidad; los porcentajes, lugares y promedios son nuestros', fc('cuadro 4')),
                   _o('Incendios y superficie de 2024 por entidad', _f(INC_DOC24, 'cuadro 4')), _o('Quién combate y la restauración', ley('lgdfs', 'arts. 119 y 121'))],
            'portal': planisferio.portal(a), 'edo': a,
            'sug': ['¿Qué estado tuvo más superficie quemada?', '¿Qué no dicen las cifras de incendios?', '¿Cuántos acuíferos de %s están en déficit?' % nom[a]]}


def _t(v):
    return format(v, ',') + ' t'


def _temas_pesca(t):
    """La pesca y la acuacultura: el panorama nacional, sus puntos ciegos y una
    ficha por entidad."""
    import auditorias
    import planisferio
    E = auditorias.db()['estados']
    nom = {e['abbr']: e['name'] for e in E}
    P = pesca(list(nom))
    fp = lambda c: _f(PE_DOC, c)
    T = PE_TOT
    cap = T['viv'] - T['acu']
    reg = [a for a in P if P[a]['t']]
    ot = sorted(reg, key=lambda a: P[a]['lt'])
    ov = sorted(reg, key=lambda a: P[a]['lv'])
    c4 = sum(P[a]['t'] for a in ot[:4]) / T['viv'] * 100
    if [nom[a] for a in ot[:4]] != ['Sonora', 'Sinaloa', 'Baja California', 'Baja California Sur'] or round(c4, 1) != 81.6:
        raise SystemExit('recursos_naturales: los cuatro estados con más pesca ya no son los que nombra el Anuario (p. 123), o ya no suman más de cuatro quintas partes')
    sinl = ['AGS', 'CHIH', 'CDMX', 'COAH', 'DGO', 'GTO', 'HGO', 'MÉX', 'MOR', 'NL', 'PUE', 'QRO', 'SLP', 'TLAX', 'ZAC']
    tsin = sum(PESCA[a][0] for a in sinl)
    if abs(tsin - 25582) > 3:
        raise SystemExit('recursos_naturales: las entidades sin litoral ya no suman las 25,582 t del Anuario')
    ex = max(sinl, key=lambda a: PESCA[a][0])
    gap = max(reg, key=lambda a: P[a]['lv'] - P[a]['lt'])
    dv = (T['val'] - T['val24']) / T['val24'] * 100
    dt = (T['viv'] - T['viv24']) / T['viv24'] * 100
    inc = T['val'] - T['val24']
    cam, cal = PE_ESP['camarón'], PE_ESP['calamar']
    son = P['SON']
    lgpas = ley('lgpas', 'arts. 4, fracciones VI y VII, 32 y 63')
    nl = [a for a in P if not P[a]['t']]
    t['rn_pesca'] = {
        'tit': 'La pesca y la acuacultura, estado por estado',
        'h': ('<p>La pesca es un recurso renovable si se respeta el ritmo con que se reproducen las especies. La ley distingue la <b>captura</b> (lo que se saca del mar, los ríos y las presas) '
              'de la <b>acuacultura</b> (lo que se cultiva en granjas), y obliga a reportar las dos: el pescador con su <b>aviso de arribo</b> y el productor acuícola con su <b>aviso de cosecha</b> '
              '(Ley General de Pesca y Acuacultura Sustentables, art. 4, fracciones VI y VII). Con esos avisos, la Comisión Nacional de Acuacultura y Pesca (CONAPESCA) arma su Anuario.</p>'
              '<p>En 2025 el país registró <b>%s</b> de pesca y acuacultura en peso vivo %s, %s más que en 2024 %s. De cada 100 toneladas, %s fueron de cultivo %s. '
              'Su valor a precio de playa fue de <b>%s</b> %s, %s más que en 2024 %s.</p>'
              '<p><b>%s</b> registró más que nadie: %s, el %s %% del país %s. Con %s, %s y %s junta el %s %% %s: el Anuario lo atribuye a sus pesquerías masivas de sardina, túnidos, camarón, '
              'anchoveta y, en 2025, calamar. Las %d entidades sin litoral registraron %s, el %s %% %s, casi todo de cultivo; %s es la mayor, con %s.</p>') % (
            _t(T['viv']), _chip('oficial'), _n(dt, 1) + ' %', _chip('derivado'), _n(T['acu'] / T['viv'] * 100, 1), _chip('derivado'),
            _mdps(T['val'] / 1000).lstrip('+'), _chip('oficial'), _n(dv, 1) + ' %', _chip('derivado'),
            nom[ot[0]], _t(P[ot[0]]['t']), _n(P[ot[0]]['pt'], 1), _chip('derivado'), nom[ot[1]], nom[ot[2]], nom[ot[3]], _n(c4, 1), _chip('derivado'),
            len(sinl), _t(tsin), _n(tsin / T['viv'] * 100, 2), _chip('derivado'), nom[ex], _t(PESCA[ex][0])),
        'ci': [{'v': _t(T['viv']), 'etq': 'de pesca y acuacultura en 2025', 'e': 'oficial'},
               {'v': _mdps(T['val'] / 1000).lstrip('+'), 'etq': 'su valor a precio de playa', 'e': 'oficial'},
               {'v': '%s %%' % _n(T['acu'] / T['viv'] * 100, 1), 'etq': 'fue de cultivo (acuacultura)', 'e': 'derivado', 'op': 'acuacultura ÷ peso vivo total × 100'}],
        'fu': [_o('Peso vivo, captura, acuacultura y valor por entidad, 2015-2025', fp('cuadros 2.5.6, 2.5.8, 2.5.10 y 2.5.12, pp. 171 a 177')),
               _o('Lo que dice el Anuario de su método y de la concentración en el noroeste', fp('pp. 122-123')),
               _o('Los avisos de arribo y de cosecha', lgpas),
               _o('Las proporciones, los cambios y los lugares', fp('cuadros 2.5.6 y 2.5.12'), 'derivado')],
        'sug': ['¿Cuánto pesca Sinaloa?', '¿Qué estado pesca más?', '¿Qué no dicen las cifras de la pesca?']}
    t['rn_pesca_ciegos'] = {
        'tit': 'Lo que las cifras de la pesca no dicen',
        'h': '<p>Siete preguntas que conviene hacer antes de leer el mapa de la pesca:</p>%s' % _lista([
            ('<b>Es lo que se declaró, no todo lo que se pescó.</b> El Anuario sale de los avisos de arribo, de cosecha y de producción que captura el propio productor en el Sistema de '
             'Información de Pesca y Acuacultura (SIPESCA), con factores de conversión y ajustes (p. 122). Lo que no se declara no aparece. Y lo de un estado no es solo lo de su costa: '
             'quien pesca en altamar o en aguas extranjeras con barco mexicano también entrega su aviso de arribo (Ley General de Pesca y Acuacultura Sustentables, art. 63).'),
            ('<b>Hay dos toneladas.</b> El peso desembarcado es el del producto como llega, descabezado, fileteado o eviscerado: %s en 2025. El peso vivo, el del animal entero, '
             'se calcula con factores del Instituto Mexicano de Investigación en Pesca y Acuacultura Sustentables (IMIPAS): %s %s (glosario, p. 336). Una nota que mezcla las dos compara cosas distintas; '
             'aquí se usa el peso vivo.') % (_t(T['des']), _t(T['viv']), _chip('oficial')),
            ('<b>El propio Anuario cruza a Jalisco y Colima.</b> Sus cuadros 2.1.10 y 2.1.11 (pp. 137-138) le dan a Jalisco %s y %s, y a Colima %s y %s. Pero su cuadro 2.1.5 y sus series '
             '(cuadros 2.5.6 y 2.5.12) dicen lo contrario: Colima desembarcó %s y su pesca valió %s; Jalisco, %s y %s. Aquí van las de las series. Con el cruce, el ranking del cuadro 2.1.11 '
             'pone a Jalisco donde va Colima.') % (
                _t(PE_CRUCE['JAL'][0]), _mdps(PE_CRUCE['JAL'][1] / 1000).lstrip('+'), _t(PE_CRUCE['COL'][0]), _mdps(PE_CRUCE['COL'][1] / 1000).lstrip('+'),
                _t(PE_DES['COL']), _mdps(P['COL']['val'] / 1000).lstrip('+'), _t(PE_DES['JAL']), _mdps(P['JAL']['val'] / 1000).lstrip('+')),
            ('<b>Un total que no es el suyo.</b> El renglón TOTAL del cuadro 2.5.8, el de la captura (p. 173), repite el total de la acuacultura: %s en 2025. La captura de 2025 fue de %s %s, '
             'peso vivo menos acuacultura, y es lo que suman sus propios renglones.') % (_t(PE_TOT_258), _t(cap), _chip('derivado')),
            ('<b>El valor subió y el volumen casi no.</b> El valor creció %s y las toneladas, %s %s. El camarón explica %s de cada 100 pesos del alza y el calamar, %s %s: el calamar pasó de %s a %s. '
             'Y son pesos de cada año, sin descontar la inflación. En %s las toneladas bajaron %s y el valor subió %s.') % (
                _n(dv, 1) + ' %', _n(dt, 1) + ' %', _chip('derivado'), _n((cam[1] - cam[0]) / inc * 100, 1), _n((cal[1] - cal[0]) / inc * 100, 1), _chip('derivado'),
                _mdps(cal[0] / 1000).lstrip('+'), _mdps(cal[1] / 1000).lstrip('+'), nom['SON'], _sig(son['ct']).lstrip('−'), _sig(son['cv']).lstrip('+')),
            ('<b>Mucho volumen no es mucho valor.</b> %s quedó en el lugar %d por toneladas y en el %d por valor %s: lo que se pesca pesa distinto en la caja. '
             'Y sobre una base chica los saltos engañan: %s pasó de %s en 2024 a %s en 2025 %s; un salto así pide preguntar si cambió la producción o el registro.') % (
                nom[gap], P[gap]['lt'], P[gap]['lv'], _chip('derivado'), nom['SLP'], _t(P['SLP']['t24']), _t(P['SLP']['t']), _chip('oficial')),
            ('<b>Volumen no es salud del recurso.</b> Que se pesque más no dice si la especie aguanta. Eso lo dice la Carta Nacional Pesquera, que elabora el IMIPAS y debe publicarse en el DOF '
             'cada dos años (Ley General de Pesca y Acuacultura Sustentables, art. 32). %s') % (
                ('Y %s no registró producción en 2025, lo que no es lo mismo que no tener pesca.' % _y([nom[a] for a in nl])) if nl else '')]),
        'fu': [_o('El método (p. 122), el glosario (p. 336) y los cuadros 2.1.5, 2.1.10, 2.1.11, 2.5.6, 2.5.8, 2.5.11 y 2.5.12', fp('pp. 122, 132, 137-138, 171, 173, 176-177 y 336')),
               _o('Los avisos, la pesca en altamar y la Carta Nacional Pesquera', lgpas),
               _o('La captura, los cambios, las partes del alza y los lugares', fp('cuadros 2.5.6, 2.5.10, 2.5.11 y 2.5.12'), 'derivado')],
        'sug': ['¿Qué estado pesca más?', '¿Cuánto vale la pesca de Sonora?', '¿Qué no dicen las cifras de incendios?']}
    for a in nom:
        x = P[a]
        cv = lambda c, pl='': ('subi%s %s' % ('eron' if pl else 'ó', _sig(c).lstrip('+'))) if c > 0 else ('baj%s %s' % ('aron' if pl else 'ó', _sig(c).lstrip('−'))) if c < 0 else ('quedaron igual' if pl else 'quedó igual')
        if x['t']:
            h = ('<p>En 2025, <b>%s</b> registró <b>%s</b> de pesca y acuacultura en peso vivo %s: el lugar %d de %d entidades con registro y el %s %% del país %s. '
                 'De cada 100 toneladas, %s fueron de cultivo y %s de captura %s.</p>'
                 '<p>Su valor a precio de playa fue de <b>%s</b> %s, el lugar %d por valor %s. Contra 2024, las toneladas %s y el valor %s %s; el valor es en pesos de cada año, sin descontar la inflación.</p>'
                 '<p>Es lo que se declaró en los avisos de arribo y de cosecha (Ley General de Pesca y Acuacultura Sustentables, art. 4), no todo lo que se pescó, y no dice si las especies aguantan: '
                 'eso lo dice la Carta Nacional Pesquera (art. 32).%s</p>') % (
                nom[a], _t(x['t']), _chip('oficial'), x['lt'], len(reg), _n(x['pt'], 2) if x['pt'] >= 0.01 else 'menos del 0.01', _chip('derivado'),
                _n(x['pacu'], 1), _n(100 - x['pacu'], 1), _chip('derivado'),
                _mdps(x['mdp']).lstrip('+'), _chip('oficial'), x['lv'], _chip('derivado'), cv(x['ct'], 1), cv(x['cv']), _chip('derivado'),
                ' Ojo: los cuadros 2.1.10 y 2.1.11 del Anuario le dan a %s las cifras de %s; aquí van las de sus series y su cuadro 2.1.5.' % (nom[a], nom['COL' if a == 'JAL' else 'JAL'])
                if a in PE_CRUCE else '')
            ci = [{'v': _t(x['t']), 'etq': 'de pesca y acuacultura en 2025', 'e': 'oficial'},
                  {'v': _mdps(x['mdp']).lstrip('+'), 'etq': 'su valor a precio de playa', 'e': 'oficial'},
                  {'v': '%s %%' % _n(x['pacu'], 1), 'etq': 'fue de cultivo', 'e': 'derivado', 'op': 'acuacultura ÷ peso vivo × 100'}]
        else:
            h = ('<p><b>%s</b> no registró producción pesquera ni acuícola en 2025 en el Anuario de la CONAPESCA %s. En 2024 había registrado %s, con un valor de %s %s. '
                 'No registrar no es lo mismo que no tener pesca: el Anuario es lo que se declaró en los avisos de arribo y de cosecha (Ley General de Pesca y Acuacultura Sustentables, art. 4).</p>') % (
                nom[a], _chip('oficial'), _t(x['t24']), _mdps(x['val24'] / 1000).lstrip('+'), _chip('oficial'))
            ci = [{'v': '0 t', 'etq': 'registradas en 2025', 'e': 'oficial'}, {'v': _t(x['t24']), 'etq': 'registradas en 2024', 'e': 'oficial'}]
        t['rn_pe_' + planisferio.clave(a)] = {
            'tit': '%s: su pesca y su acuacultura' % nom[a], 'h': h, 'ci': ci,
            'fu': [_o('Su peso vivo, captura, acuacultura y valor, 2024 y 2025', fp('cuadros 2.5.6, 2.5.8, 2.5.10 y 2.5.12, pp. 171 a 177')),
                   _o('Las proporciones, los cambios y los lugares', fp('cuadros 2.5.6 y 2.5.12'), 'derivado'), _o('Los avisos y la Carta Nacional Pesquera', lgpas)],
            'portal': planisferio.portal(a), 'edo': a,
            'sug': ['¿Qué estado pesca más?', '¿Qué no dicen las cifras de la pesca?', '¿Cuánto bosque tiene %s?' % nom[a]]}


SECCIONES = [('rn_capitulo','Renovables y no renovables'), ('rn_regimen', 'Las tres vías y las tres auditorías'),
             ('rn_ramos', 'Los seis ramos, ayer y hoy'), ('rn_agua', 'El agua del subsuelo, estado por estado'),
             ('rn_agua_ciegos', 'Lo que el mapa del agua no dice'), ('rn_bosques', 'Los bosques de cada estado: su superficie forestal'),
             ('rn_incendios', 'Los incendios forestales, estado por estado'),
             ('rn_incendios_ciegos', 'Lo que las cifras de incendios no dicen'), ('rn_pesca', 'La pesca y la acuacultura, estado por estado'),
             ('rn_pesca_ciegos', 'Lo que las cifras de la pesca no dicen'), ('rn_pemex', 'PEMEX, ayer y hoy'),
             ('rn_refinerias', 'Las refinerías de PEMEX'), ('rn_mineria', 'Las concesiones mineras, estado por estado'),
             ('rn_mineria_ciegos', 'Lo que el cuadro de las minas no dice'), ('rn_auditar', 'Lo subrayado: la guía del auditor'),
             ('rn_ciegos', 'Los puntos ciegos')]


def secciones():
    T = temas()
    extra = {'rn_ramos': tabla_ramos(),
             'rn_refinerias': tabla_refinerias() + '<p class="leg-mas"><a href="planisferio.html?d=ambiental">🗺️ Verlas en el Planisferio ➔</a> · '
                                                   '<a href="auditoria-dos-bocas.html">📖 La investigación de Dos Bocas ➔</a> · '
                                                   '<a href="auditoria-refineria-tula.html">📖 La de la refinería de Tula ➔</a></p>',
             'rn_bosques': tabla_forestal() + '<p class="leg-mas"><a href="planisferio.html?d=ambiental&amp;l=sfT">🗺️ Los bosques en el Planisferio ➔</a> · '
                                               '<a href="%s">El documento de la CONAFOR (PDF) ➔</a></p>' % SF_DOC['url'],
             'rn_incendios': tabla_incendios() + '<p class="leg-mas"><a href="planisferio.html?d=ambiental&amp;l=incH">🗺️ Los incendios en el Planisferio ➔</a> · '
                                                 '<a href="%s">Los reportes semanales de la CONAFOR ➔</a></p>' % INC_PAG,
             'rn_pesca': tabla_pesca() + '<p class="leg-mas"><a href="planisferio.html?d=ambiental&amp;l=peT">🗺️ La pesca en el Planisferio ➔</a> · '
                                         '<a href="%s">El Anuario de la CONAPESCA (PDF) ➔</a></p>' % PE_DOC['url'],
             'rn_agua': tabla_agua() + '<p class="leg-mas"><a href="planisferio.html?d=ambiental&amp;l=acuP">🗺️ Los acuíferos en el Planisferio ➔</a></p>',
             'rn_mineria': tabla_mineria() + tabla_derechos() + '<p class="leg-mas"><a href="planisferio.html?d=ambiental&amp;l=minT">🗺️ Las concesiones en el Planisferio ➔</a></p>'}
    return [{'id': k.replace('_', '-'), 'titulo': html.escape(tit), 'texto': '', 'tarjetas': [],
             'bloque': bloque_tema(T[k], extra.get(k, ''), ARCHIVO)} for k, tit in SECCIONES]


ENTRADA = ('El capítulo de recursos naturales del libro del autor, «Introducción al Derecho Económico», convertido en método de auditoría y puesto al día: '
           'qué recursos se renuevan y cuáles se agotan, de quién son, quién los explota y con qué ley, y a quién se audita en cada caso. '
           'Empieza por el agua del subsuelo: los 653 acuíferos del país, cuáles ya no tienen agua para concesionar y cuáles se miden como sobreexplotados. '
           'Sigue con los bosques: la superficie forestal de cada estado y los incendios forestales de 2025, cuánto terreno afectaron, qué parte era de árboles y cuánto es frente a su superficie forestal. '
           'Luego, la pesca y la acuacultura de cada estado en 2025: cuántas toneladas registró, cuánto valieron y qué parte fue de cultivo. '
           'Cada regla está cotejada contra el texto vigente, porque el libro describe las leyes de 1993-1994. Incluye la sección de PEMEX y sus siete refinerías, '
           'con lo que procesa cada una frente a su capacidad, y las concesiones mineras de cada estado, que también se ven en el Planisferio. Es la misma información con que contesta Pregúntale al Auditor.')


def pagina():
    """El diccionario de la página para apartados.py (tarjeta de Aprende)."""
    return {
        'archivo': ARCHIVO, 'menu': TITULO, 'menu_archivo': 'aprende.html',
        'padre': ('aprende.html', 'Aprende'),
        'icono': '🌎', 'titulo': TITULO, 'lema': 'Renovables y no renovables: el agua del subsuelo, los bosques y sus incendios, la pesca, las minas de cada estado y las refinerías de PEMEX, qué se audita y con qué ley',
        'estilos': ['asistente.css'], 'entrada': ENTRADA, 'secciones': secciones(),
    }


def pendientes():
    """Para el Registro de pendientes (pendientes.py)."""
    import pendientes as P
    ap = [(ARCHIVO, 'Aprende · ' + TITULO), ('planisferio.html', 'Planisferio · dimensión ambiental')]
    return [
        {'id': 'mineria-por-estado-2026', 'tema': 'Recursos naturales',
         'que': 'Las concesiones mineras vigentes de cada una de las 32 entidades con un corte reciente (títulos y hectáreas)',
         'porque': ('El Prontuario Estadístico de la Minería de la Secretaría de Economía, en su edición de enero-junio de 2025 (publicada en diciembre de 2025), repite el cuadro '
                    'por entidad con corte de marzo de 2024. El Segundo Informe da el corte del 30 de junio de 2026, pero solo nacional (20,542 títulos) y de cuatro estados. '
                    'Mientras la Secretaría de Economía no publique el cuadro por entidad al día, el mapa usa el de marzo de 2024 y lo dice.'),
         'responsable': 'Secretaría de Economía (Dirección General de Minas)', 'enlace': 'https://www.gob.mx/se/acciones-y-programas/mineria',
         'enlace_txt': 'Secretaría de Economía, minería', 'aparece': ap},
        {'id': 'acuiferos-disponibilidad-nueva', 'tema': 'Recursos naturales',
         'que': 'La disponibilidad media anual de agua subterránea de los 653 acuíferos con un corte posterior a diciembre de 2022',
         'porque': ('La Ley de Aguas Nacionales pide revisarla al menos cada dos años (art. 22, reformado el 11-12-2025; antes, cada tres). La última publicada en el DOF es la del '
                    '9 de noviembre de 2023, con corte al 30 de diciembre de 2022, y el Programa Nacional Hídrico 2026-2030 (DOF 18-05-2026) todavía la usa. El Segundo Informe dice que '
                    'se actualizaron los balances de 189 acuíferos, pero la CONAGUA no ha publicado el acuerdo nuevo, ni la lista completa de los sobreexplotados: solo los 27 que mide con pozos.'),
         'responsable': 'Comisión Nacional del Agua (CONAGUA)', 'enlace': 'https://sigagis.conagua.gob.mx/gas1/sections/Disponibilidad_Acuiferos.html',
         'enlace_txt': 'CONAGUA, disponibilidad de los acuíferos', 'aparece': ap},
        {'id': 'ambiente-por-estado', 'tema': 'Recursos naturales',
         'que': 'El resto de la cifra ambiental de cada una de las 32 entidades: las denuncias ante la PROFEPA',
         'porque': ('El Informe de Actividades 2024 de la PROFEPA nombra estados pero no publica sus cifras por entidad, y la plataforma aún no coteja si sus datos abiertos las traen; '
                    'ese es el último que falta. Ya están las concesiones mineras, los acuíferos, los incendios forestales, la superficie forestal (CONAFOR, «Estado que guarda el sector forestal '
                    'en México 2023», con el mapa de vegetación de 2018) y la pesca y la acuacultura de cada entidad (CONAPESCA, Anuario Estadístico de Acuacultura y Pesca 2025), '
                    'todos desde el 03-11-2026.'),
         'responsable': P.PLATAFORMA, 'enlace': 'https://www.inegi.org.mx/temas/ambiente/',
         'enlace_txt': 'INEGI, estadísticas de medio ambiente', 'aparece': ap},
    ]
