# -*- coding: utf-8 -*-
"""Costo Ambiental, aplicacion 3: «Basura y proteccion» en pagina propia
(16-10-2026). Sustituye al marco que cargaba la portada entera
(index.html?ir=ambiente&ancla=eb-ambasura&visor=1).

Lo que pintaba el motor en #ambienteRaiz (renderCostoAmbiental de
audit-engine.js, en modo «en bloques»: basura, proteccion, megaobras,
leyes y quien lo mide) se conserva entero, con las mismas colecciones
(ambiente y cuentas_ecologicas) y las mismas operaciones. Se agrega:
el camino de la basura de un dia paso por paso, un «¿Cuanto crees?», la
calculadora de la basura de tu casa, la serie 2010-2022 que se toca, la
balanza con su calculadora, el presupuesto por organo con cinco medidas y
CSV, las megaobras de construccion con su ficha en «Sector e industria», y
filtros en las leyes y en quien lo mide.

Correcciones editoriales frente al motor: los porcentajes calculados
(avance del pago, cambio 2027 contra 2026, peso de la Conagua) llevan su
chip «derivado» con la operacion; la proporcion daño/proteccion se dice
como division; los pendientes llevan data-pend a su ficha del Registro
(ambiente-0, -1, -2; obra-<id>).

Lo llama apartados.insp_nativa() (INSP_NATIVAS['ambasura']).
"""
import html
import json
import os

from presupuesto_modulos import chip
from territorio_modulos import mapa_svg

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESTILOS = ['am-basura.css']
SCRIPTS = ['am-basura.js']

# Las megaobras que son obra de construccion (tienen o debieron tener una
# Manifestacion de Impacto Ambiental). Quedan fuera los rescates
# financieros, las compras de empresas y los programas.
OBRAS_FISICAS = ['tren-maya', 'dos-bocas', 'aifa-texcoco', 'tren-toluca', 'refineria-tula',
                 'megafarmacia', 'estela-luz', 'bunker-garcia-luna']

# Catalogo georreferenciado para el Mapa Ambiental de Megaobras e Infraestructura
# por Estado (26-10-2026): las 8 megaobras de construccion, las 2 plantas
# industriales petroquimicas/fertilizantes de Pemex y los 4 casos estatales de
# infraestructura hidrica, gasifera y reconstruccion por desastres.
OBRAS_MAPA = [
    {
        'id': 'tren-maya', 'ico': '🚆', 'nombre': 'Tren Maya (1,554 km)',
        'tipo': 'trenes', 'tipoNom': 'Trenes y selvas',
        'edos': ['CAM', 'CHIS', 'QROO', 'TAB', 'YUC'], 'multi': True,
        'sede': 'Campeche, Chiapas, Quintana Roo, Tabasco y Yucatán',
        'presMdp': 167341.6, 'realMdp': 497350.2, 'sobrePct': 197.2,
        'estReal': 'derivado', 'pendReal': None,
        'asfMdp': 8563.5, 'asfTxt': '$8,563.5 mdp acumulados por aclarar ante la ASF (CP 2019–2024)',
        'ecosistema': 'Selva maya, acuíferos kársticos, cenotes y cavernas subterráneas (Tramos 5, 6 y 7)',
        'alerta': 'Tala y fragmentación de corredor biológico en cinco estados y cimentación con pilotes sobre suelo kárstico y cenotes. Los permisos ambientales definitivos (MIA) y el conteo oficial de árboles talados contra compensados siguen sin integrarse.',
        'miaEst': 'pendiente', 'miaPend': 'ambiente-0',
        'miaTxt': 'Manifestaciones de Impacto Ambiental (SEMARNAT) y auditorías de desempeño ambiental',
        'aud': 'auditoria-tren-maya.html', 'ficha': 'herramienta-megaobras-sector.html#obra-tren-maya',
        'exp': 'expedientes.html#exp-tren-maya', 'expNom': 'Expediente ASF Tren Maya',
    },
    {
        'id': 'dos-bocas', 'ico': '🛢️', 'nombre': 'Refinería Olmeca en Dos Bocas',
        'tipo': 'energia', 'tipoNom': 'Refinerías y energía',
        'edos': ['TAB'], 'multi': False,
        'sede': 'Paraíso, Tabasco',
        'presMdp': 157049.2, 'realMdp': 357887.3, 'sobrePct': 128.0,
        'estReal': 'oficial', 'pendReal': 'obra-dos-bocas',
        'asfMdp': 594.9, 'asfTxt': '$594.9 mdp por aclarar ante la ASF en contratos y supervisión',
        'ecosistema': 'Humedales costeros, manglar y zona inundable del litoral de Paraíso, Tabasco',
        'alerta': 'Desmonte de manglar en el predio costero, relleno hidráulico en zona de inundación y emisiones de refinación petrolera frente a la meta climática (NDC) de la Ley General de Cambio Climático.',
        'miaEst': 'pendiente', 'miaPend': 'ambiente-0',
        'miaTxt': 'MIA y resolutivos de la ASEA sobre desmonte de manglar y condicionantes operativas',
        'aud': 'auditoria-dos-bocas.html', 'ficha': 'herramienta-megaobras-sector.html#obra-dos-bocas',
        'exp': 'expedientes.html#exp-dos-bocas', 'expNom': 'Expediente ASF Dos Bocas',
    },
    {
        'id': 'tren-toluca', 'ico': '🚈', 'nombre': 'Tren Interurbano México–Toluca «El Insurgente»',
        'tipo': 'trenes', 'tipoNom': 'Trenes y selvas',
        'edos': ['MÉX', 'CDMX'], 'multi': True,
        'sede': 'Zinacantepec a Observatorio (Estado de México y Ciudad de México)',
        'presMdp': 76346.8, 'realMdp': 153694.3, 'sobrePct': 101.3,
        'estReal': 'oficial', 'pendReal': None,
        'asfMdp': 3098.6, 'asfTxt': '$3,098.6 mdp acumulados por aclarar ante la ASF (CP 2019–2024)',
        'ecosistema': 'Bosque de Agua en la Sierra de las Cruces, La Marquesa y barrancas de Santa Fe',
        'alerta': 'Más de una década de obras sobre la zona de recarga acuífera entre el Valle de Toluca y el Valle de México, con liberación tardía de derecho de vía y taludes forestales intervenidos.',
        'miaEst': 'pendiente', 'miaPend': 'ambiente-0',
        'miaTxt': 'MIA regional de la SICT y cumplimiento de reforestación en la Sierra de las Cruces',
        'aud': 'auditoria-tren-toluca.html', 'ficha': 'herramienta-megaobras-sector.html#obra-tren-toluca',
        'exp': 'expedientes.html#exp-tren-toluca', 'expNom': 'Expediente ASF Tren Toluca',
    },
    {
        'id': 'aifa-texcoco', 'ico': '🛫', 'nombre': 'AIFA en Santa Lucía y cancelación del NAIM Texcoco',
        'tipo': 'aeropuertos', 'tipoNom': 'Aeropuertos y equipamiento',
        'edos': ['MÉX'], 'multi': False,
        'sede': 'Zumpango y Texcoco, Estado de México',
        'presMdp': 79305.0, 'realMdp': 101935.3, 'sobrePct': 28.5,
        'estReal': 'derivado', 'pendReal': 'obra-aifa-texcoco',
        'asfMdp': 123.9, 'asfTxt': '$123.9 mdp por aclarar en AIFA + $113,327.7 mdp auditados por la ASF en la cancelación de Texcoco',
        'ecosistema': 'Cuenca endorreica del Valle de México, acuífero Cuautitlán-Pachuca y vaso del Lago de Texcoco',
        'alerta': 'Doble huella territorial: obras inconclusas y rehabilitación hidrológica en el vaso de Texcoco más extracción de agua y bancos de materiales pétreos en la cuenca de Zumpango-Santa Lucía.',
        'miaEst': 'pendiente', 'miaPend': 'ambiente-0',
        'miaTxt': 'MIA del AIFA (SEDENA) y seguimiento del Área de Protección de Recursos Naturales Lago de Texcoco',
        'aud': 'auditoria-aifa.html', 'ficha': 'herramienta-megaobras-sector.html#obra-aifa-texcoco',
        'exp': 'expedientes.html#exp-aifa', 'expNom': 'Expediente ASF AIFA y Texcoco',
    },
    {
        'id': 'agronitrogenados', 'ico': '🏭', 'nombre': 'Planta de fertilizantes Agronitrogenados (Pro-Agroindustria)',
        'tipo': 'energia', 'tipoNom': 'Refinerías y energía',
        'edos': ['VER'], 'multi': False,
        'sede': 'Complejo Petroquímico Pajaritos, Coatzacoalcos, Veracruz',
        'presMdp': 7894.2, 'realMdp': 13698.3, 'sobrePct': 73.5,
        'estReal': 'derivado', 'pendReal': None,
        'asfMdp': 0.0, 'asfTxt': 'Auditado por la ASF en la Cuenta Pública 2017 ($819 millones de dólares entre compra y rehabilitación)',
        'ecosistema': 'Corredor industrial y estuario del río Coatzacoalcos – Laguna de Pajaritos, Veracruz',
        'alerta': 'Planta química con 14 años fuera de operación al momento de su compra en 2014, con equipos corroídos y pasivos industriales en la zona petroquímica de Pajaritos.',
        'miaEst': 'pendiente', 'miaPend': 'ambiente-0',
        'miaTxt': 'Auditorías ambientales y dictámenes de pasivos industriales de la ASEA y PROFEPA en Pajaritos',
        'aud': 'auditoria-agronitrogenados.html', 'ficha': 'herramienta-megaobras-sector.html#obra-agronitrogenados',
        'exp': 'herramienta-megaobras-pulso-cuenta.html#cuenta-agronitrogenados', 'expNom': 'Cuenta de la obra en Pemex',
    },
    {
        'id': 'fertinal', 'ico': '🧪', 'nombre': 'Grupo Fertinal (planta industrial y mina de roca fosfórica)',
        'tipo': 'energia', 'tipoNom': 'Refinerías y energía',
        'edos': ['MICH', 'BCS'], 'multi': True,
        'sede': 'Lázaro Cárdenas, Michoacán y mina en San Juan de la Costa, Baja California Sur',
        'presMdp': 12532.0, 'realMdp': 13121.6, 'sobrePct': 4.7,
        'estReal': 'oficial', 'pendReal': None,
        'asfMdp': 0.0, 'asfTxt': 'Auditado por la ASF en la Cuenta Pública 2017 ($635 millones de dólares pagados con deuda incluida)',
        'ecosistema': 'Estero del río Balsas en Lázaro Cárdenas (Michoacán) y litoral de la Bahía de La Paz (Baja California Sur)',
        'alerta': 'Acumulación histórica de fosfoyeso (yeso ácido) en pilas industriales en Lázaro Cárdenas y extracción minera de roca fosfórica frente al Golfo de California.',
        'miaEst': 'pendiente', 'miaPend': 'ambiente-0',
        'miaTxt': 'Diagnóstico de pasivos ambientales y vida útil de reservas mineras en SEMARNAT y Pemex',
        'aud': 'auditoria-fertinal.html', 'ficha': 'herramienta-megaobras-sector.html#obra-fertinal',
        'exp': 'herramienta-megaobras-pulso-cuenta.html#cuenta-fertinal', 'expNom': 'Cuenta de la obra en Pemex',
    },
    {
        'id': 'megafarmacia', 'ico': '💊', 'nombre': 'Megafarmacia del Bienestar (Birmex)',
        'tipo': 'aeropuertos', 'tipoNom': 'Aeropuertos y equipamiento',
        'edos': ['MÉX'], 'multi': False,
        'sede': 'Huehuetoca, Estado de México',
        'presMdp': 3614.6, 'realMdp': 3948.6, 'sobrePct': 9.2,
        'estReal': 'oficial', 'pendReal': None,
        'asfMdp': 1045.0, 'asfTxt': '$1,045.0 mdp por aclarar ante la ASF en Birmex (Cuenta Pública 2023)',
        'ecosistema': 'Zona industrial y cuenca hidrológica de Huehuetoca, Estado de México',
        'alerta': 'Reconversión de bodegas logísticas para almacenamiento federal y cadena de frío de medicamentos; la ASF documentó observaciones por $1,045.0 mdp en Birmex.',
        'miaEst': 'pendiente', 'miaPend': 'ambiente-0',
        'miaTxt': 'Dictámenes de impacto ambiental y manejo de residuos farmacéuticos (COFEPRIS / SEMARNAT)',
        'aud': 'auditoria-megafarmacia.html', 'ficha': 'herramienta-megaobras-sector.html#obra-megafarmacia',
        'exp': 'expedientes.html#exp-birmex', 'expNom': 'Expediente ASF Birmex',
    },
    {
        'id': 'estela-luz', 'ico': '🗼', 'nombre': 'Estela de Luz (Monumento del Bicentenario)',
        'tipo': 'aeropuertos', 'tipoNom': 'Aeropuertos y equipamiento',
        'edos': ['CDMX'], 'multi': False,
        'sede': 'Bosque de Chapultepec, Ciudad de México',
        'presMdp': 393.5, 'realMdp': 1304.9, 'sobrePct': 231.6,
        'estReal': 'oficial', 'pendReal': None,
        'asfMdp': 0.0, 'asfTxt': 'Auditado por la ASF en la Cuenta Pública 2010–2011 con pliegos por acero, cuarzo y cimentación',
        'ecosistema': 'Entrada al Bosque de Chapultepec y Paseo de la Reforma, Ciudad de México',
        'alerta': 'Excavación profunda y cimentación al pie del Bosque de Chapultepec con un sobrecosto de +231.6 % frente al proyecto original.',
        'miaEst': 'pendiente', 'miaPend': 'ambiente-0',
        'miaTxt': 'Autorización de impacto ambiental urbano en área de valor ambiental de Chapultepec',
        'aud': 'auditoria-estela-luz.html', 'ficha': 'herramienta-megaobras-sector.html#obra-estela-luz',
        'exp': 'herramienta-megaobras-pulso-cuenta.html#cuenta-estela-luz', 'expNom': 'Cuenta de la obra',
    },
    {
        'id': 'refineria-tula', 'ico': '🧱', 'nombre': 'Refinería Bicentenario en Tula (barda perimetral)',
        'tipo': 'energia', 'tipoNom': 'Refinerías y energía',
        'edos': ['HGO'], 'multi': False,
        'sede': 'Tula de Allende, Atitalaquia y Tlaxcoapan, Hidalgo',
        'presMdp': 3714.0, 'realMdp': 1127.6, 'sobrePct': -69.6,
        'estReal': 'derivado', 'pendReal': None,
        'asfMdp': 0.0, 'asfTxt': 'Más de $9,375.0 mdp de gasto hundido total (compra de 700 hectáreas, nivelación y deuda) para 0 % de refinería',
        'ecosistema': 'Cuenca atmosférica e hidrológica de Tula – Valle del Mezquital, Hidalgo',
        'alerta': '700 hectáreas desmontadas y cercadas en una de las cuencas con mayor carga de contaminantes atmosféricos y de aguas residuales del centro del país, sin construir la planta.',
        'miaEst': 'pendiente', 'miaPend': 'ambiente-0',
        'miaTxt': 'MIA del proyecto cancelado y estado ambiental actual del polígono de 700 hectáreas',
        'aud': 'auditoria-refineria-tula.html', 'ficha': 'herramienta-megaobras-sector.html#obra-refineria-tula',
        'exp': 'herramienta-megaobras-pulso-cuenta.html#cuenta-refineria-tula', 'expNom': 'Cuenta de la obra',
    },
    {
        'id': 'bunker-garcia-luna', 'ico': '🏢', 'nombre': 'Búnker de Seguridad de García Luna (Centro de Inteligencia)',
        'tipo': 'aeropuertos', 'tipoNom': 'Aeropuertos y equipamiento',
        'edos': ['CDMX'], 'multi': False,
        'sede': 'Av. Constituyentes, Ciudad de México',
        'presMdp': 347.4, 'realMdp': 263.0, 'sobrePct': -24.3,
        'estReal': 'derivado', 'pendReal': 'obra-bunker-garcia-luna',
        'asfMdp': 0.0, 'asfTxt': '$3,365.0 mdp de inversión total con equipamiento tecnológico según Cuenta Pública 2009',
        'ecosistema': 'Ladera poniente colindante con la Tercera Sección del Bosque de Chapultepec, CDMX',
        'alerta': 'Construcción subterránea de tres niveles en la ladera de Constituyentes; su operación técnica y mantenimiento quedaron reservados por seguridad nacional.',
        'miaEst': 'pendiente', 'miaPend': 'ambiente-0',
        'miaTxt': 'Manifestación de impacto ambiental de la obra subterránea en Constituyentes',
        'aud': 'auditoria-bunker-garcia-luna.html', 'ficha': 'herramienta-megaobras-sector.html#obra-bunker-garcia-luna',
        'exp': 'herramienta-megaobras-pulso-cuenta.html#cuenta-bunker-garcia-luna', 'expNom': 'Cuenta de la obra',
    },
    {
        'id': 'cuchillo-ii', 'ico': '💧', 'nombre': 'Acueducto El Cuchillo II (Conagua)',
        'tipo': 'agua', 'tipoNom': 'Agua y desastres',
        'edos': ['NL'], 'multi': False,
        'sede': 'China a Monterrey, Nuevo León',
        'presMdp': None, 'realMdp': None, 'sobrePct': None,
        'estReal': 'oficial', 'pendReal': None,
        'asfMdp': 1655.9, 'asfTxt': '$1,655.9 mdp acumulados por aclarar ante la ASF ($1,123.5 mdp en CP 2023 + $532.4 mdp en CP 2024)',
        'ecosistema': 'Cuenca del río San Juan, presa El Cuchillo y zona metropolitana de Monterrey, Nuevo León',
        'alerta': 'Obra hidráulica de emergencia para trasvase de agua a Monterrey; la ASF observó $1,655.9 mdp por pagos en exceso, sobrecostos en tubería de acero y bombeo sin comprobar.',
        'miaEst': 'pendiente', 'miaPend': 'ambiente-0',
        'miaTxt': 'Exención o MIA de emergencia ante SEMARNAT y caudal ecológico de la cuenca del río San Juan',
        'aud': 'auditoria-presupuesto-ambiental.html', 'ficha': 'herramienta-ambiente-auditor.html',
        'exp': 'expedientes.html#exp-cuchillo-ii', 'expNom': 'Expediente ASF El Cuchillo II',
    },
    {
        'id': 'guaymas-gas', 'ico': '🔥', 'nombre': 'Puerto de Guaymas y terminal de licuefacción AMIGO LNG',
        'tipo': 'energia', 'tipoNom': 'Refinerías y energía',
        'edos': ['SON'], 'multi': False,
        'sede': 'Heroica Guaymas, Sonora',
        'presMdp': 3977.5, 'realMdp': 3977.5, 'sobrePct': None,
        'estReal': 'oficial', 'pendReal': 'red-guaymas-comodato-amigo-gnl-1',
        'asfMdp': 0.0, 'asfTxt': '$3,977.5 mdp de modernización portuaria anunciada; punto de acuerdo en la Gaceta Parlamentaria del 14-04-2026',
        'ecosistema': 'Bahía de Guaymas y litoral del Golfo de California, Sonora',
        'alerta': 'El Congreso de Sonora exhortó en diciembre de 2025 a la ASEA y a la SEMARNAT a agilizar permisos de una planta de gas natural licuado; el comodato y el resolutivo ambiental siguen sin publicarse.',
        'miaEst': 'pendiente', 'miaPend': 'red-guaymas-comodato-amigo-gnl-8',
        'miaTxt': 'Resolutivo de impacto ambiental de la ASEA y contrato de comodato portuario en Guaymas',
        'aud': 'auditoria-guaymas-gas.html', 'ficha': 'noticias-relevantes.html#col-guaymas-comodato-amigo-gnl',
        'exp': 'noticias-relevantes.html#col-guaymas-comodato-amigo-gnl', 'expNom': 'Verificación Guaymas y ASEA',
    },
    {
        'id': 'otis-acapulco', 'ico': '🌀', 'nombre': 'Reconstrucción por el huracán Otis en Acapulco y Coyuca',
        'tipo': 'agua', 'tipoNom': 'Agua y desastres',
        'edos': ['GRO'], 'multi': False,
        'sede': 'Acapulco de Juárez y Coyuca de Benítez, Guerrero',
        'presMdp': 61313.0, 'realMdp': 35017.0, 'sobrePct': None,
        'estReal': 'oficial', 'pendReal': 'otis-diferencia',
        'asfMdp': 0.0, 'asfTxt': '$84,207.0 mdp en daños estimados por CENAPRED; $26,296.0 mdp de diferencia entre lo anunciado y lo reportado como gastado',
        'ecosistema': 'Bahía de Acapulco, Laguna de Coyuca y cuenca baja del río Papagayo, Guerrero',
        'alerta': 'Impacto ambiental y sanitario tras el huracán categoría 5: residuos de demolición, drenaje colapsado y $26,296.0 mdp anunciados cuyo cierre presupuestario no han publicado Hacienda ni Bienestar.',
        'miaEst': 'pendiente', 'miaPend': 'otis-diferencia',
        'miaTxt': 'Cierre presupuestario de los $61,313 mdp anunciados y desglose por ramo (Hacienda y Bienestar)',
        'aud': 'auditoria-presupuesto-ambiental.html', 'ficha': 'herramienta-ambiente-crisis.html',
        'exp': 'herramienta-ambiente-crisis.html', 'expNom': 'Crisis ambientales: Huracán Otis',
    },
    {
        'id': 'jalisco-agua', 'ico': '🚰', 'nombre': 'Presa El Zapotillo, Acueducto y red del SIAPA',
        'tipo': 'agua', 'tipoNom': 'Agua y desastres',
        'edos': ['JAL'], 'multi': False,
        'sede': 'Cañadas de Obregón y Área Metropolitana de Guadalajara, Jalisco',
        'presMdp': None, 'realMdp': None, 'sobrePct': None,
        'estReal': 'pendiente', 'pendReal': 'gdl-zapotillo',
        'asfMdp': 0.0, 'asfTxt': 'Plan Hídrico entregado al Congreso el 14-07-2026 sin anexo público de costos ni resultados de laboratorio de calidad del agua',
        'ecosistema': 'Cuenca del río Verde (Los Altos de Jalisco) y red de agua potable de Guadalajara',
        'alerta': 'Falta de transparencia de Conagua, el Gobierno de Jalisco, SIAPA y COPRISJAL sobre cuánto falta para concluir El Zapotillo, cuántas colonias reciben agua turbia y qué arrojan los análisis de laboratorio.',
        'miaEst': 'pendiente', 'miaPend': 'gdl-plan-costos',
        'miaTxt': 'Anexos financieros del Plan Hídrico, costo federal de El Zapotillo y resultados de laboratorio (COPRISJAL)',
        'aud': 'auditoria-presupuesto-ambiental.html', 'ficha': 'herramienta-ambiente-crisis.html',
        'exp': 'herramienta-ambiente-crisis.html', 'expNom': 'Crisis ambientales: Agua en Jalisco',
    },
]


def esc(t):
    return html.escape(str(t if t is not None else ''), quote=True)


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def num(v, dec=0):
    """amNum() del motor: miles con coma y decimales fijos."""
    return format(v, ',.%df' % dec)


def pmdp(pesos, dec=1):
    """pdMdp() del motor: pesos -> millones con un decimal."""
    return '$' + format(pesos / 1e6, ',.%df' % dec) + ' mdp'


def pct(p, dec=1):
    return format(p, ',.%df' % dec) + ' %'


def construir(base, ref):
    A = base['ambiente']
    C = base['cuentas_ecologicas']
    R, P = A['residuos'], A['presupuesto']
    F = A['fuentes']
    refs = {r['id']: r for r in base.get('referencias_legales', [])}
    pend_ids = ['ambiente-%d' % i for i in range(len(A.get('pendientes', [])))]

    def fuente(clave, pagina=None):
        f = F.get(clave)
        if not f:
            return chip('pendiente') + ' fuente por documentar'
        pag = ''
        if pagina not in (None, ''):
            pag = (', p. %s' % pagina) if str(pagina).isdigit() else ', ' + str(pagina)
        return ('<a class="ab-fu" href="%s" target="_blank" rel="noopener noreferrer" title="%s">%s%s ↗</a>'
                % (esc(f['url']), esc(f['doc']), esc(f.get('corto') or f['doc']), esc(pag)))

    def liga_ref(rid, texto):
        r = refs.get(rid)
        if not r:
            return chip('pendiente') + ' ' + esc(texto)
        return ('<a class="ab-fu" href="%s" target="_blank" rel="noopener noreferrer" title="%s">%s ↗</a>'
                % (esc(r['url']), esc(r['cita_apa']), esc(texto)))

    ceem = liga_ref('ref-ceem-2024', 'INEGI, Cuentas Económicas y Ecológicas 2024')

    def tarjeta(valor, rotulo, estado, pie='', pend=None, cls=''):
        return ('<div class="ab-dato%s"><strong class="ab-num">%s</strong><span class="ab-dato-r">%s %s</span>%s</div>'
                % (cls, valor, rotulo, chip(estado, pend), ('<small>%s</small>' % pie) if pie else ''))

    # ------------------------------------------------------------------
    # 1. La basura
    gen = R['generacionTdia']['valor']
    rec = R['recolectadaTdia']
    sit = R['sitiosDisposicion']
    rel = R['rellenosSanitarios']
    sep = R['separadaTdia']
    msr = R['municipiosSinRecoleccion']
    veh = R['vehiculos']
    per = R['perCapitaKg']['valor']
    no_rec = gen - rec['valor']
    no_ctrl_t = sit['tdia'] - rel['tdia']
    no_ctrl_n = sit['valor'] - rel['valor']
    residuos_cee = next((x for x in C['degradacion'].get('componentes', []) if x['id'] == 'residuos'), None)

    pasos = [
        ('🏠', 'Se genera', gen, 'oficial',
         'Toda la basura que producen hogares, comercios y servicios en un día.',
         fuente('DBGIR', R['generacionTdia']['pagina'])),
        ('🚛', 'Se recolecta', rec['valor'], 'oficial',
         'El %s de lo generado. No se recolectan %s t al día (%s − %s, %s).'
         % (pct(rec['pct']), num(no_rec), num(gen), num(rec['valor']), chip('derivado')),
         fuente('DBGIR', rec['pagina'])),
        ('🏚️', 'Llega a un sitio de disposición final', sit['tdia'], 'oficial',
         'A alguno de los %s sitios de disposición final del país.' % num(sit['valor']),
         fuente('DBGIR', sit['pagina'])),
        ('✅', 'Llega a un relleno sanitario', rel['tdia'], 'oficial',
         'A uno de los %d rellenos sanitarios: el %s de lo que llega a disposición final. Las otras %s t al día van a %s sitios '
         'clasificados como no controlados (%s − %s t y %s − %d sitios, %s).'
         % (rel['valor'], pct(rel['pct']), num(no_ctrl_t, 1), num(no_ctrl_n), num(sit['tdia']), num(rel['tdia'], 1),
            num(sit['valor']), rel['valor'], chip('derivado')),
         fuente('DBGIR', rel['pagina'])),
    ]
    camino = []
    for i, (ico, tit, t, e, txt, fu) in enumerate(pasos):
        camino.append(
            '<li class="ab-paso" data-paso="%d">'
            '<div class="ab-paso-cab"><span class="ab-paso-ico" aria-hidden="true">%s</span>'
            '<div><p class="ab-paso-tit">%s</p><p class="ab-paso-t"><b class="ab-num">%s t</b> al día %s</p></div></div>'
            '<div class="ab-riel" aria-hidden="true"><span class="ab-riel-b" style="--ab-w:%.4f"></span></div>'
            '<p class="ab-paso-tx">%s <span class="ab-paso-fu">%s</span></p>'
            '%s</li>'
            % (i, ico, esc(tit), num(t, 1 if t != int(t) else 0), chip(e), t / gen, txt, fu,
               ('<p class="ab-paso-pct">%s del total generado %s</p>' % (pct(t / gen * 100), chip('derivado'))) if i else
               '<p class="ab-paso-pct">El punto de partida: todo lo que se genera.</p>'))

    serie = R['recolectadaSerie']
    smax = max(serie['tdia'])
    barras = []
    for i, (a, v) in enumerate(zip(serie['anios'], serie['tdia'])):
        barras.append('<li><button type="button" class="ab-s-b%s" data-i="%d" aria-pressed="%s" aria-label="%d: %s toneladas al día">'
                      '<span class="ab-s-riel"><span class="ab-s-barra" style="--ab-h:%.4f"></span></span>'
                      '<span class="ab-s-a">%d</span></button></li>'
                      % (' ab-act' if i == len(serie['anios']) - 1 else '', i, 'true' if i == len(serie['anios']) - 1 else 'false',
                         a, num(v), v / smax, a))

    datos_basura = (
        tarjeta(num(gen) + ' t', 'de basura al día en el país', 'oficial', fuente('DBGIR', R['generacionTdia']['pagina'])) +
        tarjeta(pct(rec['pct']), 'se recolecta (%s t/día)' % num(rec['valor']), 'oficial', fuente('DBGIR', rec['pagina'])) +
        tarjeta(pct(rel['pct']), 'llega a uno de los %d rellenos sanitarios' % rel['valor'], 'oficial', fuente('DBGIR', rel['pagina'])) +
        tarjeta(pct(sep['pct']), 'se recolecta separada', 'oficial', fuente('DBGIR', sep['pagina'])) +
        tarjeta(str(msr['valor']), 'municipios sin servicio de recolección', 'oficial',
                '%d de ellos en Oaxaca · %s' % (msr['oaxaca'], fuente('DBGIR', msr['pagina']))) +
        (tarjeta(pmdp(residuos_cee['monto_mdp'] * 1e6), 'costo anual del daño por basura mal gestionada (2024)',
                 residuos_cee.get('estado', 'oficial'), ceem, cls=' ab-dato-rojo') if residuos_cee else ''))

    basura = '''
  <section class="ab-bloque" id="abBasura" aria-labelledby="abBasTit">
    <h2 class="ab-tit" id="abBasTit"><span aria-hidden="true">🗑️</span> La basura: un servicio municipal sin dinero federal</h2>
    <p class="ab-txt">Recoger, trasladar, tratar y disponer la basura es obligación del municipio (artículo 115 constitucional). El diagnóstico nacional de la SEMARNAT, publicado en abril de 2026, retrata cómo se cumple.</p>

    <div class="ab-adivina" id="abAdivina">
      <p class="ab-adivina-k"><span aria-hidden="true">🤔</span> ¿Cuánto crees?</p>
      <p class="ab-adivina-p">De cada 100 kilos de basura que llegan a un sitio de disposición final, ¿cuántos llegan a un <b>relleno sanitario</b>, el único sitio controlado por la norma?</p>
      <label class="ab-adivina-l" for="abAdivinaR"><span>Tu respuesta: <b id="abAdivinaV">50</b> kilos de cada 100</span>
        <input type="range" id="abAdivinaR" min="0" max="100" step="1" value="50" class="ab-rango"></label>
      <button type="button" class="ab-boton" id="abAdivinaB"><span aria-hidden="true">👀</span> Ver la respuesta</button>
      <p class="ab-adivina-res" id="abAdivinaRes" aria-live="polite" hidden></p>
    </div>

    <h3 class="ab-sub">El camino de la basura de un día</h3>
    <p class="ab-txt">Sigue las toneladas desde que salen de las casas hasta donde terminan. Cada barra mide lo que queda frente a lo que se generó.</p>
    <p class="ab-acciones"><button type="button" class="ab-boton" id="abCaminoB"><span aria-hidden="true">▶️</span> Seguir la basura paso por paso</button>
      <button type="button" class="ab-boton ab-sec" id="abCaminoT">Ver todo de una vez</button></p>
    <ol class="ab-camino" id="abCamino">
      %(camino)s
    </ol>
    <p class="ab-nota">Barras y porcentajes del total: %(chip_d)s cada cifra ÷ %(gen)s t generadas al día × 100.</p>

    <div class="ab-datos">%(datos)s</div>
    <div class="ab-alerta">%(chip_o)s <b>Sin partida federal.</b> %(sinpart)s %(sinpart_fu)s</div>
    <p class="ab-nota">%(rel_nota)s Hay %(sitios)s sitios de disposición final; %(veh)s camiones recolectores, de los cuales el %(veh_pct)s %% son anteriores a 2002. %(chip_o)s %(veh_fu)s</p>

    <div class="ab-casa" id="abCasa">
      <h3 class="ab-sub"><span aria-hidden="true">🏠</span> La basura de tu casa, al promedio nacional</h3>
      <p class="ab-txt">Cada persona genera en promedio <b>%(per)s kg</b> de basura al día %(chip_o)s %(per_fu)s. Dinos cuántos viven contigo y elige el periodo.</p>
      <div class="ab-casa-ctl">
        <div class="ab-paso-n" role="group" aria-label="Personas en tu casa">
          <button type="button" class="ab-boton ab-sec ab-mm" id="abMenos" aria-label="Una persona menos">−</button>
          <output class="ab-casa-n" id="abPersonas" aria-live="polite">3</output>
          <button type="button" class="ab-boton ab-sec ab-mm" id="abMas" aria-label="Una persona más">+</button>
          <span class="ab-casa-nl" id="abPersonasL">personas</span>
        </div>
        <div class="ab-grupo" role="group" aria-label="Periodo">
          <button type="button" class="ab-op" data-dias="1" aria-pressed="false">Un día</button>
          <button type="button" class="ab-op" data-dias="7" aria-pressed="false">Una semana</button>
          <button type="button" class="ab-op" data-dias="30" aria-pressed="false">30 días</button>
          <button type="button" class="ab-op" data-dias="365" aria-pressed="true">Un año</button>
        </div>
      </div>
      <div class="ab-casa-res" id="abCasaRes" aria-live="polite"></div>
      <p class="ab-nota">%(chip_d)s Personas × %(per)s kg × días. Si tu basura siguiera el promedio nacional, el %(norec_pct)s no se recolectaría (100 − %(rec_pct)s, %(chip_d)s). Es un promedio del país: tu municipio puede estar mejor o peor.</p>
    </div>

    <div class="ab-serie" id="abSerie">
      <h3 class="ab-sub">Basura recolectada al día, %(s_ini)d a %(s_fin)d %(chip_o)s</h3>
      <p class="ab-txt">De %(s_v0)s toneladas en %(s_ini)d a %(s_vn)s en %(s_fin)d. Toca un año para ver su cifra y cuánto cambió.</p>
      <ol class="ab-s-g" aria-label="Basura recolectada al día por año">%(barras)s</ol>
      <p class="ab-s-det" id="abSerieDet" aria-live="polite"></p>
      <p class="ab-nota">%(serie_fu)s. Los cambios son %(chip_d)s: la cifra del año menos la del levantamiento anterior.</p>
    </div>

    <details class="ab-plg">
      <summary><span aria-hidden="true">🚛</span> ¿Quién recoge la basura de tu municipio? Las concesiones</summary>
      <p class="ab-txt">La Ley General de Residuos (artículo 10, fracciones IV y V) permite al municipio prestar el servicio por sí mismo o a través de gestores, y le da la facultad de otorgar concesiones. La decisión se toma en el cabildo y debe constar en sus actas. %(lgpgir)s</p>
      <p class="ab-txt">%(chip_p1)s Qué municipios tienen el servicio concesionado y cuánto cuesta vienen en los microdatos del censo municipal del INEGI; se integrarán municipio por municipio.</p>
    </details>
  </section>''' % {
        'camino': '\n      '.join(camino), 'chip_d': chip('derivado'), 'chip_o': chip('oficial'),
        'chip_p1': chip('pendiente', pend_ids[1] if len(pend_ids) > 1 else None),
        'gen': num(gen), 'datos': datos_basura,
        'sinpart': esc(R['sinPartidaFederal']['texto']), 'sinpart_fu': fuente('DBGIR', R['sinPartidaFederal']['pagina']),
        'rel_nota': esc(rel.get('nota', '')), 'sitios': num(sit['valor']), 'veh': num(veh['valor']),
        'veh_pct': num(veh['pctAntes2002'], 2), 'veh_fu': fuente('DBGIR', veh['pagina']),
        'per': num(per, 3), 'per_fu': fuente('DBGIR', R['perCapitaKg']['pagina']),
        'norec_pct': pct(100 - rec['pct']), 'rec_pct': num(rec['pct'], 1),
        's_ini': serie['anios'][0], 's_fin': serie['anios'][-1], 's_v0': num(serie['tdia'][0]), 's_vn': num(serie['tdia'][-1]),
        'barras': ''.join(barras), 'serie_fu': fuente('CNGMD', serie['pagina']),
        'lgpgir': liga_ref('ref-lgpgir', 'Ley General de Residuos, reforma DOF 19-01-2026'),
    }

    # ------------------------------------------------------------------
    # 2. Proteger contra dañar
    gpa = C['gasto_proteccion_ambiental']
    dano = C['ctada']['total_mdp']
    ratio = dano / gpa['monto_mdp']
    proteger = '''
  <section class="ab-bloque" id="abProteger" aria-labelledby="abProTit">
    <h2 class="ab-tit" id="abProTit"><span aria-hidden="true">💸</span> Lo que se gasta en proteger, contra lo que cuesta el daño</h2>
    <p class="ab-txt">%(lect)s</p>
    <div class="ab-balanza" aria-label="Gasto en protección contra costo del daño, 2024">
      <div class="ab-bal-f"><span class="ab-bal-r">Gasto en protección ambiental, 2024 %(chip_g)s</span>
        <span class="ab-bal-riel"><span class="ab-bal-b ab-bal-verde" style="--ab-w:%(wg).4f"></span></span>
        <strong class="ab-num">%(gpa)s</strong></div>
      <div class="ab-bal-f"><span class="ab-bal-r">Costo del daño ambiental, 2024 %(chip_c)s</span>
        <span class="ab-bal-riel"><span class="ab-bal-b ab-bal-rojo" style="--ab-w:1"></span></span>
        <strong class="ab-num">%(dano)s</strong></div>
      <p class="ab-bal-x"><span class="ab-bal-xn">× %(ratio)s</span> el daño contra la protección %(chip_d)s</p>
    </div>
    <p class="ab-nota">%(chip_d)s Por cada peso destinado a proteger el ambiente, se deterioraron %(ratio)s (%(dano_n)s ÷ %(gpa_n)s millones). El gasto es solo del sector público consolidado: no incluye empresas privadas ni hogares. %(ceem)s</p>
    <div class="ab-calc" id="abCalc">
      <label class="ab-calc-l" for="abCalcIn">Si se gastan en proteger</label>
      <div class="ab-calc-in"><span aria-hidden="true">$</span><input type="text" inputmode="decimal" id="abCalcIn" class="ab-input" value="100" autocomplete="off"></div>
      <div class="ab-grupo" role="group" aria-label="Montos de ejemplo">
        <button type="button" class="ab-op" data-m="1">$1</button>
        <button type="button" class="ab-op" data-m="100">$100</button>
        <button type="button" class="ab-op" data-m="1000">$1,000</button>
        <button type="button" class="ab-op" data-m="1000000">$1 millón</button>
      </div>
      <p class="ab-calc-res" id="abCalcRes" aria-live="polite"></p>
      <p class="ab-nota">%(chip_d)s Monto × (%(dano_n)s ÷ %(gpa_n)s), con las cifras de 2024 del INEGI.</p>
    </div>
  </section>''' % {
        'lect': 'El INEGI mide cuánto gastó el sector público en proteger el ambiente y cuánto le costó al país agotarlo y dañarlo. Las dos cifras son de 2024, el año más reciente publicado.',
        'chip_g': chip(gpa.get('estado') or 'oficial'), 'chip_c': chip(C['ctada'].get('estado') or 'oficial'), 'chip_d': chip('derivado'),
        'wg': gpa['monto_mdp'] / dano, 'gpa': pmdp(gpa['monto_mdp'] * 1e6), 'dano': pmdp(dano * 1e6),
        'ratio': num(gpa['ratio_dano_sobre_gasto'], 2), 'dano_n': num(dano), 'gpa_n': num(gpa['monto_mdp']), 'ceem': ceem,
    }

    # ------------------------------------------------------------------
    # 3. El presupuesto 2026 y el proyecto 2027
    ap, mo, pa, pr = P['aprobado2026']['valor'], P['modificado2026']['valor'], P['pagado2026']['valor'], P['proyecto2027']['valor']
    var27 = (pr / ap - 1) * 100
    conagua = next((u for u in P['unidades'] if u['ur'] == 'B00'), None)
    filas = []
    for u in P['unidades']:
        av = u['pagado'] / u['modificado'] * 100 if u['modificado'] > 0 else 0
        vp = (u['proyecto2027'] / u['aprobado'] - 1) * 100 if u['aprobado'] > 0 else 0
        filas.append('<tr><th scope="row">%s</th><td class="ab-num">%s</td><td class="ab-num">%s</td><td class="ab-num">%s <small>%s</small></td>'
                     '<td class="ab-num">%s <small class="ab-var %s">%s%s</small></td></tr>'
                     % (esc(u['nombre']), pmdp(u['aprobado']), pmdp(u['modificado']), pmdp(u['pagado']), pct(av),
                        pmdp(u['proyecto2027']), 'ab-sube' if vp >= 0 else 'ab-baja', '+' if vp >= 0 else '', pct(vp)))
    presupuesto = '''
  <section class="ab-bloque" id="abPresupuesto" aria-labelledby="abPreTit">
    <h2 class="ab-tit" id="abPreTit"><span aria-hidden="true">🏛️</span> El presupuesto del sector ambiental: 2026 y el proyecto 2027</h2>
    <p class="ab-txt">El Ramo %(ramo)s, %(nombre)s, reúne a la SEMARNAT, la Comisión Nacional del Agua y sus órganos. Esto se aprobó para 2026, esto se había pagado a medio año y esto propone el Ejecutivo para 2027.</p>
    <div class="ab-datos">%(tarjetas)s</div>
    <h3 class="ab-sub">Órgano por órgano</h3>
    <p class="ab-txt">Elige qué medir. Toca un órgano para ver todas sus cifras.</p>
    <div class="ab-grupo ab-med" role="group" aria-label="Qué medir">
      <button type="button" class="ab-op" data-med="aprobado" aria-pressed="true">Aprobado 2026</button>
      <button type="button" class="ab-op" data-med="pagado" aria-pressed="false">Pagado al 30 de junio</button>
      <button type="button" class="ab-op" data-med="proyecto2027" aria-pressed="false">Proyecto 2027</button>
      <button type="button" class="ab-op" data-med="avance" aria-pressed="false">Avance del pago</button>
      <button type="button" class="ab-op" data-med="cambio" aria-pressed="false">Cambio 2027</button>
    </div>
    <ol class="ab-org" id="abOrg" aria-live="polite"></ol>
    <p class="ab-nota" id="abOrgNota"></p>
    <div class="ab-org-det" id="abOrgDet" aria-live="polite" hidden></div>
    <details class="ab-plg">
      <summary><span aria-hidden="true">📋</span> La tabla completa</summary>
      <div class="ab-tabla-w"><table class="ab-tabla"><thead><tr><th scope="col">Órgano</th><th scope="col">Aprobado 2026</th><th scope="col">Modificado 2026</th><th scope="col">Pagado al 30-jun</th><th scope="col">Proyecto 2027</th></tr></thead>
      <tbody>%(filas)s</tbody>
      <tfoot><tr><th scope="row">Total del Ramo %(ramo)s</th><td class="ab-num">%(ap)s</td><td class="ab-num">%(mo)s</td><td class="ab-num">%(pa)s</td><td class="ab-num">%(pr)s</td></tr></tfoot></table></div>
      <p class="ab-nota">Montos %(chip_o)s: aprobado, %(fu_pef)s; modificado y pagado, %(fu_av)s; proyecto, %(fu_pp)s. Porcentajes %(chip_d)s: el pequeño junto a lo pagado es pagado ÷ modificado × 100; el de 2027, (proyecto ÷ aprobado − 1) × 100. Los siete órganos suman exactamente el total del ramo.</p>
    </details>
    <p class="ab-acciones"><button type="button" class="ab-boton ab-sec" id="abCsv"><span aria-hidden="true">⬇️</span> Descargar la tabla en CSV</button></p>
    <p class="ab-nota">%(nota27)s %(conagua)s Comparar el presupuesto de 2026 con el daño de 2024 es ilustrativo: son años distintos.</p>
  </section>''' % {
        'ramo': esc(P['ramo']), 'nombre': esc(P['nombre']),
        'tarjetas': (
            tarjeta(pmdp(ap), 'aprobado 2026 (Ramo %s)' % esc(P['ramo']), P['aprobado2026'].get('estado', 'oficial'), fuente('PEF', P['aprobado2026']['pagina'])) +
            tarjeta(pmdp(pa), 'pagado al 30 de junio de 2026', P['pagado2026'].get('estado', 'oficial'),
                    '%s del modificado (%s) %s · %s' % (pct(pa / mo * 100), pmdp(mo), chip('derivado'), fuente('AV2T2026', 'base de datos'))) +
            tarjeta(pmdp(pr), 'proyecto 2027', P['proyecto2027'].get('estado', 'oficial'),
                    '%s%s nominal contra 2026 %s · %s' % ('+' if var27 >= 0 else '', pct(var27), chip('derivado'), fuente('PPEF2027', 'base de datos')))),
        'filas': ''.join(filas), 'ap': pmdp(ap), 'mo': pmdp(mo), 'pa': pmdp(pa), 'pr': pmdp(pr),
        'chip_o': chip('oficial'), 'chip_d': chip('derivado'),
        'fu_pef': fuente('PEF', P['aprobado2026']['pagina']), 'fu_av': fuente('AV2T2026', 'base de datos'), 'fu_pp': fuente('PPEF2027', 'base de datos'),
        'nota27': esc(P['proyecto2027'].get('nota', '')),
        'conagua': ('La Comisión Nacional del Agua concentra el %s del ramo aprobado (%s ÷ %s × 100, %s).'
                    % (pct(conagua['aprobado'] / ap * 100), pmdp(conagua['aprobado']), pmdp(ap), chip('derivado'))) if conagua else '',
    }

    # ------------------------------------------------------------------
    # 4. Megaobras y Mapa Ambiental por Estado
    sim = base.get('simulador_megaobras') or {}
    obras = {o['id']: o for o in sim.get('obras', [])}
    mapa_idx = {m['id']: m for m in OBRAS_MAPA}
    edos_base = [{
        'a': e['abbr'], 'n': e['name'], 'gasto': e['gasto'],
        'r28': e['ramo28'], 'r33': e['ramo33'], 'pc': e['pc'],
        'deuda': e['deuda'], 'sem': e['semaforoDeuda'],
        'asf': e['asfMontoObservado'], 'aud': e['asfAuditorias'],
    } for e in base.get('estados', [])]
    edos_nom = {e['a']: e['n'] for e in edos_base}
    edos_con_obra = sorted({a for m in OBRAS_MAPA for a in m['edos']}, key=lambda k: edos_nom.get(k, k))
    inv_obras_fis = sum(m['realMdp'] for m in OBRAS_MAPA if m.get('realMdp') and m['id'] in obras)
    asf_obras_tot = sum(m['asfMdp'] for m in OBRAS_MAPA if m.get('asfMdp'))

    botones_edos = []
    for a in edos_con_obra:
        os_edo = [m for m in OBRAS_MAPA if a in m['edos']]
        icos = ''.join(m['ico'] for m in os_edo)
        botones_edos.append(
            '<button type="button" class="ab-edo-btn" data-edo="%s">'
            '<span class="ab-edo-ico" aria-hidden="true">%s</span>'
            '<span class="ab-edo-nom">%s</span>'
            '<span class="ab-edo-cnt ab-num">%d</span></button>'
            % (esc(a), icos, esc(edos_nom.get(a, a)), len(os_edo)))
    opciones_sel = ''.join(
        '<option value="%s">%s (%s)%s</option>' % (
            esc(e['a']), esc(e['n']), esc(e['a']),
            (' · %d obra%s' % (sum(1 for m in OBRAS_MAPA if e['a'] in m['edos']),
                               's' if sum(1 for m in OBRAS_MAPA if e['a'] in m['edos']) != 1 else ''))
            if any(e['a'] in m['edos'] for m in OBRAS_MAPA) else '')
        for e in sorted(edos_base, key=lambda x: x['n']))

    tarj_obras = []
    for oid in OBRAS_FISICAS:
        o = obras.get(oid)
        if not o:
            continue
        m = mapa_idx.get(oid, {})
        e = (o.get('estado_campos') or {}).get('inversion_real_mdp') or 'pendiente'
        e = e if e in ('oficial', 'derivado', 'pendiente') else 'derivado'
        pend_o = m.get('pendReal') or (('obra-' + oid) if e == 'pendiente' else None)
        aud_href = m.get('aud') or ('auditoria-aifa.html' if oid == 'aifa-texcoco' else ('auditoria-%s.html' % oid))
        sede_txt = m.get('sede') or ', '.join(edos_nom.get(x, x) for x in m.get('edos', []))
        eco_txt = m.get('ecosistema') or 'Pendiente de integrar su Manifestación de Impacto Ambiental.'
        tarj_obras.append(
            '<li class="ab-obra"><a class="ab-obra-a" href="herramienta-megaobras-sector.html#obra-%s">'
            '<span class="ab-obra-ico" aria-hidden="true">%s</span><span class="ab-obra-n">%s</span>'
            '<span class="ab-obra-ir">Su ficha en Obra por obra, por industria ➔</span></a>'
            '<dl class="ab-obra-dl">'
            '<div><dt>Dónde está</dt><dd><b>%s</b></dd></div>'
            '<div><dt>Costo registrado</dt><dd><b class="ab-num">%s</b> %s</dd></div>'
            '<div><dt>Ecosistema y alerta ambiental</dt><dd>%s</dd></div>'
            '<div><dt>Lo que su permiso ambiental autorizó</dt><dd>%s · <a class="ab-fu" href="%s">Su Auditoría en imágenes ➔</a></dd></div>'
            '</dl></li>'
            % (esc(oid), esc(o.get('icono', '')), esc(o['nombre']), esc(sede_txt),
               '$' + format(o['inversion_real_mdp'], ',.1f') + ' mdp',
               chip(e, pend_o), esc(eco_txt),
               chip('pendiente', pend_ids[0] if pend_ids else None), esc(aud_href)))

    megaobras = '''
  <section class="ab-bloque" id="abMegaobras" aria-labelledby="abMegTit">
    <h2 class="ab-tit" id="abMegTit"><span aria-hidden="true">🏗️</span> La huella de las megaobras y el mapa ambiental por estado</h2>
    <p class="ab-txt">Toda obra que pueda causar desequilibrio ecológico necesita, antes de empezar, una Manifestación de Impacto Ambiental aprobada por la SEMARNAT (Ley General del Equilibrio Ecológico, artículo 28). En ese documento la propia obra reconoce cuánta vegetación retirará, qué especies afecta y qué medidas promete. %(lgeepa)s</p>
    <div class="ab-alerta ab-alerta-p">%(chip_p0)s %(pend0)s</div>

    <div class="ab-mapa" id="abMapaObras">
      <h3 class="ab-sub"><span aria-hidden="true">🗺️</span> Mapa de inversión en megaobras, gasto federalizado y alerta ambiental por estado</h3>
      <p class="ab-txt">Toca cualquier estado en el mapa o en la lista para abrir la <b>Ficha del Auditor Ambiental</b>: qué megaobras o proyectos de infraestructura tiene en su territorio, cuánto reciben sus finanzas estatales por gasto federalizado (Ramos 28 y 33), cuánto tiene por aclarar ante la ASF y qué alerta ambiental o permiso sigue pendiente.</p>

      <div class="ab-mapa-mandos">
        <div>
          <p class="ab-mapa-et">1. Qué pintar en el mapa</p>
          <div class="ab-grupo ab-mapa-lentes" role="group" aria-label="Qué pintar en el mapa">
            <button type="button" class="ab-op" data-lente="obras" aria-pressed="true"><span aria-hidden="true">🏗️</span> Megaobras y alerta ambiental</button>
            <button type="button" class="ab-op" data-lente="gasto" aria-pressed="false"><span aria-hidden="true">🏛️</span> Gasto federalizado 2026 (Ramos 28 y 33)</button>
            <button type="button" class="ab-op" data-lente="asf" aria-pressed="false"><span aria-hidden="true">🔍</span> Por aclarar ante la ASF (CP 2024)</button>
          </div>
        </div>
        <div>
          <p class="ab-mapa-et">2. Filtrar por tipo de infraestructura y alerta</p>
          <div class="ab-grupo ab-mapa-tipos" role="group" aria-label="Tipo de infraestructura">
            <button type="button" class="ab-op" data-tipo="todas" aria-pressed="true"><span aria-hidden="true">🗺️</span> Todas (14)</button>
            <button type="button" class="ab-op" data-tipo="trenes" aria-pressed="false"><span aria-hidden="true">🚆</span> Trenes y selvas (2)</button>
            <button type="button" class="ab-op" data-tipo="energia" aria-pressed="false"><span aria-hidden="true">🛢️</span> Refinerías y energía (5)</button>
            <button type="button" class="ab-op" data-tipo="aeropuertos" aria-pressed="false"><span aria-hidden="true">🛫</span> Aeropuertos y equipamiento (4)</button>
            <button type="button" class="ab-op" data-tipo="agua" aria-pressed="false"><span aria-hidden="true">💧</span> Agua y desastres (3)</button>
          </div>
        </div>
      </div>

      <div class="ab-datos ab-mapa-kpis" id="abMapaKpis">
        <div class="ab-dato"><strong class="ab-num" id="abKpiEdos">%(n_edos)d de 32</strong><span class="ab-dato-r">entidades con megaobras o alertas en este filtro %(chip_d)s</span><small>Toca un estado en el mapa para ver qué obras cruzan su territorio</small></div>
        <div class="ab-dato"><strong class="ab-num" id="abKpiInv">%(inv_fis)s</strong><span class="ab-dato-r">inversión registrada en las megaobras del filtro %(chip_d)s</span><small>Suma nacional de cada obra sin prorratear entre estados</small></div>
        <div class="ab-dato ab-dato-rojo"><strong class="ab-num" id="abKpiAsf">%(asf_tot)s</strong><span class="ab-dato-r">por aclarar ante la ASF en estas obras %(chip_d)s</span><small>Adicional a los $113,327.7 mdp auditados en la cancelación de Texcoco</small></div>
        <div class="ab-dato"><strong class="ab-num">0 de 11</strong><span class="ab-dato-r">permisos ambientales (MIA) integrados %(chip_p0)s</span><small>SEMARNAT y ASEA · Toca el chip pendiente para ver la ficha del registro</small></div>
      </div>

      <p class="ab-nota" id="abMapaQue">Los estados en verde concentran las megaobras físicas, refinerías, complejos industriales y crisis de agua o reconstrucción registrados en la plataforma. En obras que cruzan varios estados (como el Tren Maya o el Tren México–Toluca), se muestra el costo total de la obra con la advertencia de que Hacienda no publica cuánto se ejerció dentro de cada entidad.</p>

      <div class="ab-mapa-rej">
        <figure class="ab-mapa-fig">
          <div class="ab-mapa-barra-sel">
            <label class="ab-mapa-sel-l" for="abMapaSel">Ir directo a una entidad:</label>
            <select class="ab-mapa-sel" id="abMapaSel">%(opciones_sel)s</select>
          </div>
          %(svg)s
          <figcaption class="ab-mapa-ley" id="abMapaLeyenda"></figcaption>
        </figure>
        <aside class="ab-ficha" id="abMapaFicha" aria-live="polite"></aside>
      </div>

      <h4 class="ab-sub">Los %(n_edos)d estados con megaobras o alertas ambientales en el padrón</h4>
      <p class="ab-txt">Toca una entidad para abrir su Ficha del Auditor Ambiental con su gasto federalizado, observaciones de la ASF y alertas por obra:</p>
      <div class="ab-edos-lista" id="abMapaEdos" role="group" aria-label="Entidades con megaobras o alertas ambientales">
        %(botones_edos)s
      </div>
    </div>

    <h3 class="ab-sub">Las 8 megaobras de construcción del registro, obra por obra</h3>
    <p class="ab-txt">Aquí va, obra por obra: dónde está, cuánto costó, qué ecosistema interviene y el estado de su permiso ambiental:</p>
    <ul class="ab-obras">%(obras)s</ul>
    <p class="ab-nota">Costo registrado en pesos de cada año, sin quitar la inflación, con el estado que le da el registro de megaobras; toca la etiqueta para ver de dónde sale o por qué falta. Quedan fuera de esta lista de construcción los rescates financieros (FOBAPROA, FARAC) y los programas (Enciclomedia): no son obra que pida permiso ambiental.</p>
    <p class="ab-acciones"><a class="ab-boton ab-sec" href="herramienta-megaobras-sector.html"><span aria-hidden="true">🏭</span> Ver el costo de todas las megaobras</a> <a class="ab-boton ab-sec" href="herramienta-ambiente-auditor.html"><span aria-hidden="true">🌱</span> Auditar órganos del sector ambiental</a></p>
  </section>''' % {
        'lgeepa': liga_ref('ref-lgeepa', 'Ley General del Equilibrio Ecológico'),
        'chip_p0': chip('pendiente', pend_ids[0] if pend_ids else None),
        'chip_d': chip('derivado'),
        'pend0': esc(A['pendientes'][0]) if A.get('pendientes') else '',
        'n_edos': len(edos_con_obra),
        'inv_fis': '$' + format(inv_obras_fis, ',.1f') + ' mdp',
        'asf_tot': '$' + format(asf_obras_tot, ',.1f') + ' mdp',
        'opciones_sel': opciones_sel,
        'svg': mapa_svg(RAIZ),
        'botones_edos': ''.join(botones_edos),
        'obras': ''.join(tarj_obras),
    }

    # ------------------------------------------------------------------
    # 5. Leyes
    TEMAS = {'ref-cpeum': 'derecho', 'ref-lgpgir': 'basura', 'ref-lgeepa': 'obras', 'ref-lgcc': 'clima', 'ref-lieps': 'clima'}
    leyes = []
    for lx in A['leyes']:
        tema = TEMAS.get(lx['refKey'], 'derecho')
        if '115' in lx['norma']:
            tema = 'basura'
        leyes.append('<li class="ab-ley" data-tema="%s"><p class="ab-ley-n">%s</p><p class="ab-ley-d">%s</p><p class="ab-ley-r">%s %s</p></li>'
                     % (tema, esc(lx['norma']), esc(lx['dice']), chip('oficial'), liga_ref(lx['refKey'], 'Texto vigente')))
    leyes_html = '''
  <section class="ab-bloque" id="abLeyes" aria-labelledby="abLeyTit">
    <h2 class="ab-tit" id="abLeyTit"><span aria-hidden="true">⚖️</span> Las leyes que aplican</h2>
    <p class="ab-txt">%(n)d normas, con su texto vigente en la Cámara de Diputados. Filtra por tema.</p>
    <div class="ab-grupo" role="group" aria-label="Tema de la ley">
      <button type="button" class="ab-op" data-tema="todas" aria-pressed="true">Todas</button>
      <button type="button" class="ab-op" data-tema="derecho" aria-pressed="false">🌱 Tu derecho</button>
      <button type="button" class="ab-op" data-tema="basura" aria-pressed="false">🗑️ La basura</button>
      <button type="button" class="ab-op" data-tema="obras" aria-pressed="false">🏗️ Las obras</button>
      <button type="button" class="ab-op" data-tema="clima" aria-pressed="false">🌡️ Clima e impuestos</button>
    </div>
    <ul class="ab-leyes" id="abLeyesL">%(leyes)s</ul>
  </section>''' % {'n': len(A['leyes']), 'leyes': ''.join(leyes)}

    # ------------------------------------------------------------------
    # 6. Quien lo mide hoy
    quien = []
    for q in A['quienMide']:
        v = q['estado'] == 'vigente'
        quien.append('<li class="ab-q%s" data-est="%s"><p class="ab-q-d">%s</p><p class="ab-q-m">%s</p>'
                     '<p class="ab-q-e"><span class="ab-est ab-est-%s">%s</span>%s</p></li>'
                     % ('' if v else ' ab-q-c', 'v' if v else 'c', esc(q['dato']), esc(q['mide']), 'v' if v else 'c',
                        'vigente' if v else 'cambió', (' <small>%s</small>' % esc(q['nota'])) if q.get('nota') else ''))
    docs = []
    for k, f in F.items():
        sha = f.get('sha256') or ''
        docs.append('<li><a class="ab-fu" href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>%s</li>'
                    % (esc(f['url']), esc(f['doc']),
                       (' <button type="button" class="ab-sha" data-sha="%s" title="Copiar la huella SHA-256 completa">SHA-256 <code>%s…</code></button>'
                        % (esc(sha), esc(sha[:16]))) if sha else ''))
    docs.append('<li>%s</li>' % ceem)
    pend_li = ''.join('<li>%s %s</li>' % (chip('pendiente', pend_ids[i]), esc(t)) for i, t in enumerate(A.get('pendientes', [])))
    n_cambio = sum(1 for q in A['quienMide'] if q['estado'] != 'vigente')
    quien_html = '''
  <section class="ab-bloque" id="abQuien" aria-labelledby="abQuiTit">
    <h2 class="ab-tit" id="abQuiTit"><span aria-hidden="true">🏛️</span> Quién lo mide hoy</h2>
    <p class="ab-txt">Varias instituciones cambiaron con las reformas de 2024 y 2025. Así queda cada dato de esta sección.</p>
    <div class="ab-grupo" role="group" aria-label="Qué mostrar">
      <button type="button" class="ab-op" data-q="todo" aria-pressed="true">Todos (%(nq)d)</button>
      <button type="button" class="ab-op" data-q="c" aria-pressed="false">Solo lo que cambió (%(nc)d)</button>
    </div>
    <ul class="ab-quien" id="abQuienL">%(quien)s</ul>
    <h3 class="ab-sub">Los documentos de esta sección</h3>
    <p class="ab-txt">Cada documento con su huella SHA-256: si descargas el archivo y su huella coincide, es el mismo que usamos. Toca la huella para copiarla completa.</p>
    <ol class="ab-docs">%(docs)s</ol>
    <p class="ab-copiado" id="abCopiado" aria-live="polite"></p>
    <h3 class="ab-sub">Lo que todavía falta</h3>
    <ul class="ab-pend">%(pend)s</ul>
    <p class="ab-nota">%(nota)s Consulta: %(consulta)s.</p>
    <p class="ab-acciones"><a class="ab-boton ab-sec" href="herramienta-ambiente-pib.html"><span aria-hidden="true">📉</span> Ver el detalle de las cuentas ecológicas</a></p>
  </section>''' % {'nq': len(A['quienMide']), 'nc': n_cambio, 'quien': ''.join(quien), 'docs': ''.join(docs),
                   'pend': pend_li, 'nota': esc(A.get('nota', '')), 'consulta': esc(A.get('consulta', ''))}

    # ------------------------------------------------------------------
    datos = {
        'gen': gen, 'per': per, 'recPct': rec['pct'], 'relPct': rel['pct'], 'relT': rel['tdia'], 'sitT': sit['tdia'],
        'serie': {'a': serie['anios'], 't': serie['tdia']},
        'dano': dano, 'gpa': gpa['monto_mdp'],
        'ramo': P['ramo'], 'tot': {'aprobado': ap, 'modificado': mo, 'pagado': pa, 'proyecto2027': pr},
        'org': [{'ur': u['ur'], 'n': u['nombre'], 'aprobado': u['aprobado'], 'modificado': u['modificado'],
                 'pagado': u['pagado'], 'proyecto2027': u['proyecto2027']} for u in P['unidades']],
        'fu': {k: {'doc': F[k]['doc'], 'url': F[k]['url']} for k in ('PEF', 'AV2T2026', 'PPEF2027') if k in F},
        'mapaObras': {'edos': edos_base, 'obras': OBRAS_MAPA},
    }

    arranque = '''
  <section class="ab-arranque" aria-labelledby="abArrTit">
    <p class="ab-kicker">Costo Ambiental · aplicación 3</p>
    <h2 class="ab-grande" id="abArrTit">La basura y lo que se gasta en proteger</h2>
    <p class="ab-txt">Cada día el país genera <b>%(gen)s toneladas</b> de basura y solo el <b>%(rel)s</b> de lo que llega a un sitio de disposición final termina en un relleno sanitario. Por cada peso que el sector público gastó en proteger el ambiente en 2024, el daño costó <b>%(ratio)s</b>. Aquí ves cómo, con qué dinero y con qué leyes.</p>
    <ol class="ab-indice" aria-label="Lo que hay en esta página">
      <li><a href="#abBasura"><span aria-hidden="true">🗑️</span> La basura</a></li>
      <li><a href="#abProteger"><span aria-hidden="true">💸</span> Proteger contra dañar</a></li>
      <li><a href="#abPresupuesto"><span aria-hidden="true">🏛️</span> Presupuesto 2026 y 2027</a></li>
      <li><a href="#abMegaobras"><span aria-hidden="true">🏗️</span> Las megaobras</a></li>
      <li><a href="#abLeyes"><span aria-hidden="true">⚖️</span> Las leyes</a></li>
      <li><a href="#abQuien"><span aria-hidden="true">🔎</span> Quién lo mide</a></li>
    </ol>
  </section>''' % {'gen': num(gen), 'rel': pct(rel['pct']), 'ratio': '$' + num(gpa['ratio_dano_sobre_gasto'], 2)}

    aviso = '''
  <aside class="ab-aviso">
    <p><b>De dónde sale cada cifra.</b> De la SEMARNAT (diagnóstico de residuos de abril de 2026), del INEGI (censo municipal 2023 y Cuentas Económicas y Ecológicas 2024) y de Hacienda (PEF 2026, avance al 30 de junio y proyecto 2027). Cada una lleva su documento y su página; las que hacemos nosotros dicen «derivado» y su operación. Lo que todavía falta está en el <a href="pendientes.html#tema-ambiente">Registro de pendientes</a>. Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>.</p>
    <p class="ab-hermanas">Sigue en Costo Ambiental: <a href="herramienta-ambiente-reloj.html">⏱️ El reloj y el año</a> · <a href="herramienta-ambiente-ticket.html">🧾 Tu estado de cuenta ambiental</a> · <a href="herramienta-ambiente-pib.html">📉 El PIB no alcanza</a> · <a href="herramienta-ambiente-crisis.html">🌀 Crisis ambientales</a></p>
  </aside>'''

    return ('<div class="ab" id="abRaiz">' + arranque + basura + proteger + presupuesto + megaobras + leyes_html + quien_html + aviso +
            '\n  <script type="application/json" id="abDatos">' + _json(datos) + '</script>\n</div>')
