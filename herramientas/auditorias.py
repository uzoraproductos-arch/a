#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera una pagina por cada diapositiva de «Auditoria en imagenes».

Desde el 09-10-2026 la portada ya no despliega nada debajo de si misma:
cada clic lleva a una pagina propia (decision del autor, ver AGENTS.md).
Las nueve diapositivas del carrusel abren auditoria-<id>.html, que pinta
assets/auditor/js/auditoria-imagen.js con las cifras de window.AUDIT_DB.
Aqui no se escribe ni un monto: solo el marco de cada pagina.

Lo llama apartados.generar(), asi que sello.py las regenera con el sello.
"""
import html
import json
import os
import re

from apartados import RAIZ, FAVICON, cabecera, esc_attr, sociales

# id, imagen, nota de la imagen, texto alternativo, etiqueta, titulo, pregunta
AUDITORIAS = [
    ('tren-maya', 'assets/img/showcase_tren_maya.jpg', 'Ilustración generada con IA',
     'Ilustración generada con IA de un tren sobre vías en la selva',
     '🚅 Megaobra ferroviaria · FONATUR y Tren Maya', 'Tren Maya',
     '¿Cuánto dinero del Tren Maya dejó la ASF por aclarar, y en qué tramos?'),
    ('dos-bocas', 'assets/img/showcase_dos_bocas.jpg', 'Ilustración generada con IA',
     'Ilustración generada con IA de una refinería junto al mar',
     '🏭 Refinación · Pemex, Paraíso, Tabasco', 'Refinería Olmeca (Dos Bocas)',
     '¿Qué encontró la ASF al revisar la refinería paquete por paquete?'),
    ('deuda-soberana', 'assets/img/showcase_deuda_soberana.jpg', 'Ilustración generada con IA',
     'Ilustración generada con IA de un edificio de gobierno',
     '🏛️ Costo financiero de la deuda · PEF 2026', 'Los intereses de la deuda pública',
     '¿Cuánto cuesta al año pagar sólo los intereses de la deuda pública?'),
    ('aifa', 'assets/img/showcase_aifa.jpg', 'Ilustración generada con IA',
     'Ilustración generada con IA de una terminal aérea',
     '✈️ Infraestructura aeroportuaria · Defensa', 'Aeropuerto Internacional Felipe Ángeles (AIFA)',
     '¿Qué revisó la ASF en la construcción y la operación del AIFA?'),
    ('ramo-33', 'assets/img/showcase_ramo33.jpg', 'Ilustración generada con IA',
     'Ilustración generada con IA de un centro de salud',
     '🏥 Gasto federalizado · Ramo 33', 'Ramo 33: el dinero para estados y municipios',
     '¿Cuánto dinero del Ramo 33 llega a estados y municipios, y cuánto quedó por aclarar?'),
    ('lego-cienega', 'assets/img/showcase_lego_expansion.jpg', 'Imagen ilustrativa',
     'Imagen ilustrativa de una planta industrial',
     '🧱 Inversión privada y obra pública · Nuevo León', 'Ciénega de Flores: el dinero público alrededor de LEGO',
     '¿Qué dinero público rodea a la planta de LEGO en Ciénega de Flores?'),
    ('tren-toluca', 'assets/img/showcase_tren_toluca.jpg', 'Imagen ilustrativa',
     'Imagen ilustrativa de un tren sobre un viaducto elevado',
     '🚄 Transporte ferroviario · SICT', 'Tren Interurbano México-Toluca «El Insurgente»',
     '¿Qué dejó por aclarar la ASF en la obra que faltaba para terminar el Tren Interurbano?'),
    ('megafarmacia', 'assets/img/showcase_megafarmacia.jpg', 'Imagen ilustrativa',
     'Imagen ilustrativa de un almacén de medicamentos',
     '💊 Almacén de medicamentos · Birmex, Huehuetoca', 'Megafarmacia del Bienestar (Huehuetoca)',
     '¿Cuánto costó el almacén de Huehuetoca y qué encontró la ASF en Birmex?'),
    ('huachicol-fiscal', 'assets/auditor/img/showcase_huachicol.jpg', 'Ilustración provisional',
     'Ilustración de pipas de combustible frente a una aduana portuaria al atardecer',
     '⛽ Evasión en combustibles · IEPS, aduanas y SAT', 'Huachicol fiscal: el impuesto que no entra',
     '¿Cuánto IEPS de gasolinas y diésel está en juego, y qué se sabe de lo que se evade?'),
    ('ine-contratos', 'assets/auditor/img/showcase_ine_contratos.jpg', 'Ilustración provisional',
     'Ilustración del edificio del Instituto Nacional Electoral, urnas y carpetas de licitación bajo revisión',
     '🗳️ Órgano autónomo · Ramo 22, ASF y licitaciones', 'El INE: su presupuesto, lo auditado y los contratos en revisión',
     '¿Cuánto presupuesto maneja el INE, qué le observó la ASF y qué consta de los contratos bajo revisión?'),
    ('guaymas-gas', 'assets/auditor/img/showcase_guaymas_gas.jpg', 'Ilustración provisional',
     'Ilustración de tanques de gas y un buque metanero frente a la costa de Guaymas y la Gaceta Parlamentaria de Sonora',
     '🚢 Energía y medio ambiente · Guaymas, Sonora y Golfo de California', 'Guaymas y la Gaceta Parlamentaria: el proyecto de gas y su revisión ambiental',
     '¿Qué consta en la Gaceta Parlamentaria y en documentos oficiales sobre el proyecto de gas en Guaymas y su impacto ambiental?'),
    ('medicamentos-imss', 'assets/auditor/img/showcase_medicamentos_imss.jpg', 'Ilustración provisional',
     'Ilustración de un almacén de medicamentos y expedientes de contratos de salud bajo revisión',
     '💊 Contratos de salud · IMSS, IMSS-Bienestar y Birmex', 'Compras de medicamentos y contratos del sector salud',
     '¿Cuánto contratan en medicinas e insumos el IMSS, IMSS-Bienestar y Birmex, y qué parte se da por adjudicación directa?'),
    ('deuda-congreso-2027', 'assets/auditor/img/showcase_deuda_2027.jpg', 'Ilustración provisional',
     'Ilustración del tablero de votación en el Congreso con el techo de deuda 2027 y la nota soberana BBB',
     '🧾 Paquete Económico 2027 · Congreso, deuda y calificación BBB', 'El Congreso aprobó más deuda: Ley de Ingresos 2027 y nota soberana',
     '¿Cuánta deuda autorizó la Cámara de Diputados para 2027, qué cambió en las multas fiscales y qué dijo Hacienda sobre la nota BBB?'),
    ('inversion-megaobras', 'assets/auditor/img/showcase_inversion_megaobras.jpg', 'Ilustración provisional',
     'Ilustración panorámica de grandes obras de infraestructura, trenes, refinerías y el balance financiero de seis sexenios',
     '🏗️ Inversión pública y rescates · 1988–2024', 'Inversión en megaobras y rescates: 11 obras, 2 rescates y 6 sexenios',
     '¿Cuánto costaron las 11 megaobras y los 2 rescates de seis sexenios, cuánto pierden al año y dónde se consulta cada obra?'),
]


# Investigaciones agrupadas por tema (entrega 2 de Astra, 10-10-2026). Las
# usan el indice general (apartados.py) y el pie de cada investigacion.
TEMAS = [
    ('🏗️', 'Megaobras e infraestructura', ['inversion-megaobras', 'tren-maya', 'dos-bocas', 'aifa', 'tren-toluca', 'megafarmacia', 'guaymas-gas']),
    ('🗺️', 'Dinero para estados y municipios', ['ramo-33', 'lego-cienega']),
    ('💸', 'Deuda e ingresos del gobierno', ['deuda-soberana', 'huachicol-fiscal', 'deuda-congreso-2027']),
    ('🔍', 'Contratos, salud y órganos autónomos', ['ine-contratos', 'medicamentos-imss']),
]


# Recorrido de cada investigacion (propuesta de Astra, entrega 1, 10-10-2026):
# entender el caso aqui, explorar sus numeros en «Numeros» y revisar la
# evidencia en el Inspector. id: (tarjeta de Numeros, que la abre, modulo del
# Inspector, que revisa).
RUTAS = {
    'tren-maya': ('eb-cuenta-federal', 'La Cuenta Pública federal y el peritaje del Tren Maya',
                  'herramienta-inspector-asf.html', 'Lo que auditó la ASF, ente por ente'),
    'dos-bocas': ('eb-egresos', 'Cuánto recibe cada ramo, Pemex incluido',
                  'herramienta-inspector-asf.html', 'Lo que auditó la ASF, ente por ente'),
    'deuda-soberana': ('eb-ccreloj', 'El reloj del costo de la deuda',
                       'radar-tablero.html', 'El radar hacendario: la deuda de cada administración'),
    'aifa': ('eb-egresos', 'Cuánto recibe cada ramo, Defensa incluida',
             'herramienta-inspector-asf.html', 'Lo que auditó la ASF, ente por ente'),
    'ramo-33': ('eb-mapa', 'El mapa de lo que baja a cada estado',
                'herramienta-inspector-asf.html', 'Lo que auditó la ASF, ente por ente'),
    'lego-cienega': ('eb-mapa', 'El mapa de lo que baja a cada estado',
                     'herramienta-inspector-entes.html', 'El auditor de entes públicos'),
    'tren-toluca': ('eb-egresos', 'Cuánto recibe cada ramo, la SICT incluida',
                    'herramienta-inspector-asf.html', 'Lo que auditó la ASF, ente por ente'),
    'megafarmacia': ('eb-salud', 'El gasto en salud, institución por institución',
                     'herramienta-inspector-asf.html', 'Lo que auditó la ASF, ente por ente'),
    'huachicol-fiscal': ('eb-ingresos', 'De dónde sale el dinero: el IEPS en la Ley de Ingresos',
                         'herramienta-inspector-efos.html', 'La lista negra del SAT'),
    'ine-contratos': ('eb-egresos', 'Cuánto recibe cada ramo, el INE incluido (Ramo 22)',
                      'herramienta-inspector-entes.html#ente=federal:ine', 'La ficha técnica del INE en el Auditor de entes públicos'),
    'guaymas-gas': ('eb-egresos', 'Cuánto recibe cada ramo, Medio Ambiente y Energía incluidos',
                    'herramienta-ambiente-crisis.html', 'Crisis ambientales y el presupuesto de la ASEA'),
    'medicamentos-imss': ('eb-egresos', 'Cuánto recibe cada ramo, el IMSS y Salud incluidos',
                          'contratos-publicos.html?i=050GYR', 'Los contratos del IMSS en ComprasMX 2025 y 2026'),
    'deuda-congreso-2027': ('proyeccion2027', 'El Paquete Económico 2027 y la Ley de Ingresos',
                            'noticias-relevantes.html#col-lif-2027-deuda-y-multas', 'El cotejo documento por documento en Verificamos'),
    'inversion-megaobras': ('eb-egresos', 'Cuánto se destina a inversión y desarrollo económico en el PEF',
                            'herramienta-megaobras.html', 'Las 5 aplicaciones de Inversión y Megaobras: simuladores, sexenios y estados de resultados'),
}


def ruta(id_):
    ancla, num_txt, insp, insp_txt = RUTAS[id_]
    pasos = [
        ('📖', 'Entiende el caso', 'Qué pasó, cuánto dinero involucra, quién interviene y qué falta saber.',
         '#auLectura', 'Leer el caso', ' aqui'),
        ('💰', 'Explora los números', num_txt + ', con su fuente oficial.',
         'sigue-el-dinero.html?abrir=' + ancla, 'Ir a Números', ''),
        ('🔍', 'Revisa la evidencia', insp_txt + ': los documentos que sostienen el caso.',
         insp, 'Abrir el Inspector', ''),
    ]
    return ('      <section class="camino au-ruta" aria-labelledby="auRutaTit">\n'
            '        <h2 class="camino-tit" id="auRutaTit">El recorrido de esta investigación</h2>\n'
            '        <p class="camino-txt">Tres pasos: entender el caso, comprobar sus números y revisar los documentos que lo sostienen.</p>\n'
            '        <ol class="camino-pasos camino-tres">\n%s\n        </ol>\n      </section>') % '\n'.join(
        '          <li class="camino-paso%s"><span class="camino-num" aria-hidden="true">%d</span>'
        '<span class="camino-ico" aria-hidden="true">%s</span><b class="camino-que">%s</b>'
        '<span class="camino-det">%s</span><a class="camino-ir" href="%s">%s ➔</a></li>'
        % (aqui, n, ico, que, det, href, ir) for n, (ico, que, det, href, ir, aqui) in enumerate(pasos, 1))


def archivo(id_):
    return 'auditoria-%s.html' % id_


# --- Lectura breve (propuesta de Astra, puntos 3 y 8; entrega 5, 10-10-2026)
# La lectura ampliada la pinta auditoria-imagen.js; esta va escrita en el
# HTML para que un buscador la lea sin JavaScript. Responde cinco preguntas
# con los mismos datos de window.AUDIT_DB: nada se teclea aqui.
EXPEDIENTE = {'tren-maya': 'tren-maya', 'dos-bocas': 'dos-bocas', 'aifa': 'aifa', 'tren-toluca': 'tren-toluca',
              'megafarmacia': 'birmex', 'lego-cienega': 'cuchillo-ii'}
_DB = None


def db():
    global _DB
    if _DB is None:
        s = open(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js'), encoding='utf-8').read()
        _DB = json.loads(s[s.index('{'):s.rindex('}') + 1])
    return _DB


def _mdp(v):
    return '$%s mdp' % format(round(v, 1), ',.1f')


def _chip(e, pend=None):
    e = e if e in ('oficial', 'pendiente') else 'derivado'
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, ' data-pend="%s"' % pend if pend else '', e)


def _doc(texto, url):
    return '<a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>' % (esc_attr(url), html.escape(texto))


def _ref(clave):
    return next((r['url'] for r in db().get('referencias_legales', []) if r.get('id') == clave), None)


def _datos(id_):
    D = db()
    if id_ in EXPEDIENTE:
        f = next(x for x in D['expedientes']['fichas'] if x['id'] == EXPEDIENTE[id_])
        docs = [_doc('Cuenta Pública %s, auditoría %s: %s' % (a['cp'], a['num'], a['titulo']), a['url']) for a in f['auditorias'] if a.get('url')]
        falta = f['alcance'] + (' Un monto «por aclarar» no es un daño probado: es dinero que el ente no comprobó al cierre de la auditoría y que sigue en proceso.'
                                if any(a.get('porAclarar') for a in f['auditorias']) else '')
        que = f['hallazgo']
        if id_ == 'lego-cienega':
            falta += (' La ampliación de la planta de LEGO que se ha anunciado no tiene todavía un documento oficial en esta plataforma: '
                      'su monto no se suma a ninguna cifra.')
        return {'que': que, 'cuanto': [(c['valor'], c['etq'], c['estado'], None) for c in f['cifras']],
                'quien': f['ente'] + '. Revisó la Auditoría Superior de la Federación.',
                'docs': [html.escape(f['fuente']) + '.'] + docs, 'falta': falta}
    P = D['panoramaErario']
    if id_ == 'deuda-soberana':
        e = next(x for x in P['egresos'] if x['id'] == 'egr-costofin')
        return {'que': e['queCubre'] + ' La Ley Federal de Presupuesto (art. 2º, fracc. XXV) deja fuera del gasto neto total las amortizaciones: este renglón paga el precio de lo prestado, no devuelve el capital.',
                'cuanto': [(_mdp(e['montoMdp']), 'al año en el Presupuesto de Egresos 2026 (%s)' % e['clave'], e['estado'], None),
                           (_mdp(e['montoMdp'] / 365), 'cada día: el monto anual entre 365', 'derivado', None),
                           ('%.1f %%' % (e['montoMdp'] / P['totalPEF'] * 100), 'del Presupuesto de Egresos 2026 (%s)' % _mdp(P['totalPEF']), 'derivado', None)],
                'quien': 'Lo aprueba la Cámara de Diputados en el Presupuesto de Egresos y lo paga el Gobierno Federal. Fundamento: ' + e['ley'] + '.',
                'docs': [_doc('Presupuesto de Egresos de la Federación 2026, ' + e['clave'], _ref('ref-pef2026'))],
                'falta': 'Esta es la cifra aprobada para 2026. Lo que de verdad se pague se sabrá en la Cuenta Pública 2026, que Hacienda entrega a la Cámara de Diputados al año siguiente.'}
    if id_ == 'ramo-33':
        r = next(x for x in P['federalizado']['componentes'] if x['id'] == 'fed-r33')
        cp = D['cuenta_publica_asf']['cp2024']
        mdb = D['cuenta_publica_asf']['fuentes']['MDB2024']
        return {'que': r['queEs'],
                'cuanto': [(_mdp(r['montoMdp']), 'Ramo 33 aprobado para 2026 (%s)' % r['clave'], r['estado'], None),
                           (format(cp['federalizado']['auditorias'], ','), 'auditorías de la ASF al gasto federalizado de la Cuenta Pública 2024', cp['estado'], None),
                           (_mdp(cp['federalizado']['porAclarar'] / 1e6), 'quedó por aclarar en esas auditorías (Cuenta Pública 2024)', cp['estado'], None)],
                'quien': 'La Federación transfiere; los estados y municipios gastan; la Auditoría Superior de la Federación revisa (Ley de Coordinación Fiscal, art. 49).',
                'docs': [_doc('Presupuesto de Egresos de la Federación 2026, ' + r['clave'], _ref('ref-pef2026')),
                         _doc(mdb['corto'], mdb['url']), _doc('Ley de Coordinación Fiscal', _ref('ref-lcf'))],
                'falta': 'Las cifras de la ASF son de la Cuenta Pública 2024, la última revisada completa; las del presupuesto, de 2026. Son años distintos y se muestran juntas solo para dar escala.'}
    if id_ == 'huachicol-fiscal':
        H = D['huachicol_fiscal']
        J, R = H['en_juego'], H['reconocimiento']
        il = H['fuentes']['ilif27']
        return {'que': 'El Gobierno lo reconoce por escrito: en la exposición de motivos de la Ley de Ingresos 2027 dice que «%s». Las prácticas que nombra: %s.' % (R['cita'], R['practicas']),
                'cuanto': [(_mdp(J['ieps_combustibles_2027_mdp']), 'de IEPS de gasolinas y diésel que se espera cobrar en 2027 (Ley de Ingresos 2027, p. %s)' % re.sub(r' \((.*)\)$', r': \1', J['pagina']), J['estado'], None),
                           (_mdp(J['uno_por_ciento_mdp']), 'cada 1 % que se evada: el monto anterior entre 100', 'derivado', None),
                           ('Sin cifra', 'cuánto se evade de verdad', 'pendiente', 'huachicol-evasion')],
                'quien': 'El SAT cobra el IEPS y la Agencia Nacional de Aduanas revisa lo que entra al país; Hacienda propone la Ley de Ingresos y la Cámara de Diputados la aprueba.',
                'docs': [_doc(il['doc'], il['url'])],
                'falta': 'Ni el SAT ni Hacienda han publicado cuánto se pierde: el dato sigue pendiente por falta de transparencia de esas dependencias. ' + H['estudios']['texto']}
    A = D.get('auditorias_actuales') or {}
    if id_ in A:
        x = A[id_]
        c = x['cifras']
        docs = [_doc(f['doc'], f['url']) for f in x['fuentes']]
        if id_ == 'ine-contratos':
            cuanto = [
                (_mdp(c['ejercido_2025_mdp']), 'ejercidos por el INE en la Cuenta Pública 2025 (Ramo 22)', 'oficial', None),
                (_mdp(c['aprobado_2026_mdp']), 'aprobados para el INE en el Presupuesto de Egresos 2026', 'oficial', None),
                (_mdp(c['asf_cp2024_por_aclarar_mdp']), 'quedaron por aclarar en %d auditorías de la ASF (Cuenta Pública 2024)' % c['asf_cp2024_auditorias'], 'oficial', None),
                ('En revisión', 'contratos de Cajas Graf señalados en prensa (INE e IEE Sonora)', 'pendiente', x['pendiente_id']),
            ]
        elif id_ == 'guaymas-gas':
            cuanto = [
                ('%s ha' % c['superficie_sener_ha'], 'superficie del proyecto en Guaymas según la Secretaría de Energía (21-10-2026)', 'oficial', None),
                ('%s ha' % c['diferencia_ha'], 'diferencia frente a las %s ha señaladas en tribuna (%s − %s)' % (int(c['superficie_tribuna_ha']), int(c['superficie_tribuna_ha']), c['superficie_sener_ha']), 'derivado', None),
                ('%s buques al año' % c['buques_anuales'], 'máximo de buques metaneros (4 %% del tránsito de la zona) y %s mil m³ de almacenamiento' % c['almacenamiento_mil_m3'], 'oficial', None),
                (_mdp(c['asea_2026_mdp']), 'presupuesto 2026 de la ASEA (Ramo 16, unidad G00), la agencia que revisa el impacto ambiental', 'oficial', None),
                ('Sin publicar', 'contrato de comodato sobre el predio en Guaymas y resolutivo ambiental', 'pendiente', x['pendiente_id']),
            ]
        elif id_ == 'medicamentos-imss':
            cuanto = [
                (_mdp(c['imss_monto_mdp']), 'en %s contratos del IMSS registrados en ComprasMX (2025 y 2026)' % format(c['imss_contratos'], ','), 'oficial', None),
                ('%s %% (%s)' % (c['imss_adj_directa_pct'], _mdp(c['imss_adj_directa_mdp'])), 'del monto del IMSS asignado por adjudicación directa (%s ÷ %s)' % (_mdp(c['imss_adj_directa_mdp']), _mdp(c['imss_monto_mdp'])), 'derivado', None),
                (_mdp(c['imss_bienestar_monto_mdp']), 'en %s contratos de IMSS-Bienestar (%s %% por adjudicación directa)' % (format(c['imss_bienestar_contratos'], ','), c['imss_bienestar_adj_directa_pct']), 'oficial', None),
                (_mdp(c['birmex_monto_mdp']), 'en %s contratos de Birmex (%s %% por adjudicación directa)' % (format(c['birmex_contratos'], ','), c['birmex_adj_directa_pct']), 'oficial', None),
                ('Sin contrato oficial', 'señalamientos en prensa por más de $800 mdp en medicinas (2023-2024)', 'pendiente', x['pendiente_id']),
            ]
        elif id_ == 'deuda-congreso-2027':
            cuanto = [
                (_mdp(c['ingresos_totales_2027_mdp']), 'ingresos totales estimados en la Ley de Ingresos 2027 aprobada por Diputados (15-10-2026)', 'oficial', None),
                (_mdp(c['techo_deuda_interna_2027_mdp']), 'techo de endeudamiento interno neto autorizado para 2027 (%d votos a favor y %d en contra)' % (c['votos_diputados_favor'], c['votos_diputados_contra']), 'oficial', None),
                (_mdp(c['costo_financiero_2027_mdp']), 'costo financiero de la deuda propuesto para 2027 en el Paquete Económico', 'oficial', None),
                ('BBB+ → BBB', 'ajuste de HR Ratings a la nota soberana de largo plazo reconocido por Hacienda (Comunicado 82)', 'oficial', None),
                ('Por cotejar', 'proyecciones del reporte de HR Ratings (déficit de 4.6 % del PIB y deuda a 2030)', 'pendiente', x['pendiente_id']),
            ]
        elif id_ == 'inversion-megaobras':
            cuanto = [
                (_mdp(c['obras_presu_mdp']), 'presupuesto inicial documentado de las %d obras (1988–2024)' % c['obras_n'], 'derivado', None),
                ('%s (+%s %%)' % (_mdp(c['obras_real_mdp']), c['obras_sobrecosto_pct']), 'costo real documentado de las %d obras (%s por encima de lo aprobado)' % (c['obras_n'], _mdp(c['obras_brecha_mdp'])), 'derivado', None),
                (_mdp(c['rescates_real_mdp']), 'costo comprometido aparte en los %d rescates (FOBAPROA-IPAB y FARAC carretero)' % c['rescates_n'], 'derivado', None),
                ('−%s al año' % _mdp(c['balance_neto_anual_mdp']), 'pérdida neta anual en los %d proyectos con dato publicado (%d pierden %s y %d gana %s)' % (c['n_con_dato_anual'], 5, _mdp(c['balance_pierde_mdp']), 1, _mdp(c['balance_gana_mdp'])), 'derivado', None),
                ('4 obras sin dato', 'operación anual no publicada por separado (Megafarmacia, Tren Interurbano, Agronitrogenados y Búnker)', 'pendiente', x['pendiente_id']),
            ]
        return {'que': x['que'], 'cuanto': cuanto, 'quien': x['quien'], 'docs': docs, 'falta': x['falta']}
    raise SystemExit('Sin lectura breve para %s' % id_)


def lectura(id_):
    d = _datos(id_)
    cuanto = '\n'.join('            <li><b>%s</b> %s %s</li>' % (html.escape(v), html.escape(etq), _chip(e, pend)) for v, etq, e, pend in d['cuanto'])
    docs = '\n'.join('            <li>%s</li>' % x for x in d['docs'])
    filas = [('🔎', 'Qué pasó', '<p>%s</p>' % html.escape(d['que'])),
             ('💰', 'Cuánto dinero', '<ul>\n%s\n          </ul>' % cuanto),
             ('🏛️', 'Quién interviene', '<p>%s</p>' % html.escape(d['quien'])),
             ('📄', 'Qué documento lo acredita', '<ul>\n%s\n          </ul>' % docs),
             ('❓', 'Qué falta saber', '<p>%s</p>' % html.escape(d['falta']))]
    return ('      <section class="au-lectura" id="auLectura" aria-labelledby="auLecTit">\n'
            '        <h2 class="au-sec-tit" id="auLecTit">📝 Lectura breve</h2>\n'
            '        <p class="au-sec-txt">El caso en cinco preguntas, con sus documentos. Más abajo, la lectura ampliada: las cuentas paso a paso.</p>\n'
            '        <dl class="au-lec">\n%s\n        </dl>\n      </section>') % '\n'.join(
        '          <div class="au-lec-fila"><dt><span aria-hidden="true">%s</span> %s</dt><dd>%s</dd></div>' % f for f in filas)


def tema_de(id_):
    return [t for t in TEMAS if id_ in t[2]][0]


def temas(actual):
    """Las investigaciones por tema y la nota de como verificamos. Vivian en
    la portada («Por donde empezar»); el 10-10-2026 el autor las saco de
    ahi y viven al pie de cada investigacion."""
    au = {a[0]: a for a in AUDITORIAS}
    grupos = '\n'.join(
        '          <div class="au-tema%s"><span class="au-tema-tit">%s %s%s</span>%s</div>' % (
            ' au-tema-actual' if actual in ids else '', ico, tit,
            ' <small>· el tema de esta investigación</small>' if actual in ids else '',
            ''.join(('<span aria-current="page">%s</span>' if i == actual else '<a href="%s">%%s</a>' % archivo(i)) % au[i][5]
                    for i in ids))
        for ico, tit, ids in sorted(TEMAS, key=lambda t: actual not in t[2]))
    return ('        <div class="au-temas">\n%s\n        </div>\n'
            '        <p class="au-metodo"><span aria-hidden="true">🔎</span> <b>Cómo verificamos:</b> cada cifra lleva su fuente oficial y su estado: '
            '<span class="est-chip est-oficial">oficial</span> <span class="est-chip est-derivado">derivado</span> '
            '<span class="est-chip est-pendiente">pendiente</span>. Las imágenes son ilustraciones, no evidencia. '
            '<a href="indice.html#metodologia">Lee la metodología y las novedades ➔</a></p>') % grupos


def otras(actual):
    filas = []
    mismo = tema_de(actual)[2]
    for a in sorted(AUDITORIAS, key=lambda a: a[0] not in mismo):
        if a[0] == actual:
            continue
        filas.append('          <a class="au-otra" href="%s"><img src="%s" alt="" loading="lazy">'
                     '<span class="au-otra-txt"><span class="au-otra-badge">%s</span>%s</span></a>'
                     % (archivo(a[0]), a[1], a[4], a[5]))
    return '\n'.join(filas)


def pagina(a, sello):
    id_, img, nota_img, alt, badge, titulo, pregunta = a
    # LEGO necesita el padron municipal del INEGI; las demas no lo cargan.
    extra = ('\n  <script src="assets/auditor/js/municipios-efipem.js?v=%s"></script>' % sello
             if id_ == 'lego-cienega' else '')
    return '''<!DOCTYPE html>
<!-- Página generada por herramientas/auditorias.py: no la edites a mano. -->
<html lang="es" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo_doc} · Auditoría en imágenes · Auditavisión</title>
  <meta name="description" content="{pregunta_attr}">
{sociales}
  <meta name="theme-color" content="#0b2a63">
  <meta name="color-scheme" content="light">
  <link rel="icon" href="{favicon}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/auditor/css/auditavision.css?v={sello}">
  <script src="assets/auditor/js/iconos.js?v={sello}"></script>
  <script src="assets/auditor/js/volver-auditor.js?v={sello}" defer></script>
  <link rel="stylesheet" href="assets/auditor/css/civico.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/apartados.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/puerta.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/auditoria-imagen.css?v={sello}">
</head>
<body data-pagina="apartado">
{cabecera}

  <main class="apartado au-pagina" id="contenido">
    <header class="au-hero">
      <img class="au-hero-img" src="{img}" alt="{alt}">
      <span class="au-hero-ia">{nota_img}</span>
      <div class="au-hero-velo"></div>
      <div class="apartado-ancho au-hero-txt">
        <nav class="apartado-migas" aria-label="Estás en"><a href="index.html">Inicio</a> <span aria-hidden="true">›</span> <a href="index.html#auditoria-en-imagenes">Auditoría en imágenes</a> <span aria-hidden="true">›</span> <span>{titulo}</span></nav>
        <span class="au-hero-badge">{badge}</span>
        <h1 class="au-hero-tit">{titulo}</h1>
        <p class="au-hero-preg">{pregunta}</p>
      </div>
    </header>

    <div class="apartado-ancho apartado-cuerpo">
{ruta}

{lectura}

      <div id="auImg" class="au-raiz" data-id="{id}">
        <noscript><p>Esta página arma sus cuentas con JavaScript a partir de la base de datos de la plataforma. Actívalo para verlas.</p></noscript>
      </div>

{servicio}

      <section class="au-otras-sec" aria-labelledby="auOtrasTit">
        <h2 class="au-sec-tit" id="auOtrasTit">🖼️ Otras auditorías en imágenes</h2>
{temas}
        <div class="au-otras">
{otras}
        </div>
      </section>
    </div>
  </main>

  <footer class="apartado-pie">
    <div class="apartado-ancho">
      <a class="apartado-volver" href="index.html#auditoria-en-imagenes">← Volver a Auditoría en imágenes</a>
      <a class="apartado-volver apartado-indice" href="indice.html">🗂️ Índice general</a>
      <a class="apartado-volver" href="aviso-de-privacidad.html">🔒 Aviso de privacidad</a>
      <span class="apartado-pie-txt">Auditavisión · Toda cifra lleva su fuente oficial. Versión publicada: <b>{sello}</b></span>
    </div>
  </footer>

  <script src="assets/auditor/js/audit-database.js?v={sello}"></script>{extra}
  <script src="assets/auditor/js/apartados.js?v={sello}"></script>
  <script src="assets/auditor/js/comunidad.js?v={sello}"></script>
  <script src="assets/auditor/js/auditoria-imagen.js?v={sello}"></script>
</body>
</html>
'''.format(titulo_doc=re.sub('<[^>]+>', '', titulo), pregunta_attr=esc_attr(pregunta), favicon=FAVICON,
           sello=sello, cabecera=cabecera(archivo(id_), sello), img=img, alt=esc_attr(alt), nota_img=nota_img,
           titulo=titulo, badge=badge, pregunta=pregunta, id=id_, otras=otras(id_), temas=temas(id_), extra=extra, ruta=ruta(id_), lectura=lectura(id_), servicio=servicio(titulo),
           sociales=sociales(archivo(id_), re.sub('<[^>]+>', '', titulo) + ' · Auditavisión', pregunta, img))



def servicio(titulo):
    """El servicio pertinente de cada investigacion (propuesta de Astra,
    punto 8): lleva al formulario de servicios.html con el tema escrito."""
    from urllib.parse import quote
    tema = re.sub('<[^>]+>', '', titulo)
    return ('      <aside class="au-servicio" aria-label="Servicio de investigación">\n'
            '        <p><b>🔎 ¿Necesitas ir más a fondo en este caso?</b> Podemos hacer por encargo una investigación documental '
            'con la misma regla de esta página: cada cifra con su documento. La consulta sigue siendo gratuita.</p>\n'
            '        <a class="camino-ir" href="servicios.html?tema=%s#solicitud">Solicita una investigación ➔</a>\n'
            '      </aside>') % quote(tema)

# Desde el 23-10-2026 (pedido del autor) cada imagen de la portada abre el
# chat del Auditor con la pregunta de la diapositiva escrita: el lector la
# envía y el Auditor contesta con la investigación y su «Saber más».
CHAT = 'herramienta-inspector-pregunta.html'


def _bloques_portada(d):
    """[(id, pregunta visible)] de cada diapositiva de la portada, en orden."""
    out = []
    for blk in d.split('<a class="showcase-slide" ')[1:]:
        m = re.search(r'data-caso="auditoria-([\w-]+)\.html"', blk) or re.match(r'href="auditoria-([\w-]+)\.html"', blk)
        q = re.search(r'class="showcase-slide-q">([^<]*)<', blk)
        out.append((m.group(1), html.unescape(q.group(1)).strip()))
    return out


def preguntas_portada():
    return dict(_bloques_portada(open(os.path.join(RAIZ, 'index.html'), 'rb').read().decode('utf-8')))


def chat_url(pregunta):
    from urllib.parse import quote
    return '%s?p=%s' % (CHAT, quote(pregunta))


def _docs_planos(docs):
    """Los documentos de la lectura breve, como fuentes del bot {tx, url}."""
    out = []
    for x in docs:
        m = re.search(r'<a href="([^"]+)"[^>]*>(.*?) ↗</a>', x)
        if m:
            out.append({'tx': html.unescape(m.group(2)), 'url': html.unescape(m.group(1))})
        else:
            out.append({'tx': html.unescape(re.sub('<[^>]+>', '', x)).rstrip('.')})
    return out


# Las frases con que se nombra el tema de cada investigación (sin acentos),
# para que el chat ofrezca «Ver la investigación» cuando la plática lo toca,
# aunque la pregunta no sea la de su diapositiva (24-10-2026).
TEMA_BOT = {
    'tren-maya': ['tren maya'],
    'dos-bocas': ['dos bocas', 'refineria olmeca'],
    'deuda-soberana': ['intereses de la deuda', 'costo financiero', 'deuda soberana', 'deuda publica'],
    'aifa': ['aifa', 'felipe angeles'],
    'ramo-33': ['ramo 33', 'aportaciones federales', 'fais', 'fortamun'],
    'lego-cienega': ['lego', 'cienega de flores'],
    'tren-toluca': ['tren interurbano', 'tren a toluca', 'mexico toluca', 'el insurgente'],
    'megafarmacia': ['megafarmacia', 'huehuetoca', 'birmex'],
    'huachicol-fiscal': ['huachicol'],
    'ine-contratos': ['contratos del ine', 'investigacion de la asf al ine', 'cajas graf', 'taddei', 'presupuesto del ine'],
    'guaymas-gas': ['guaymas', 'amigo lng', 'epcilon', 'sanchez taboada', 'gas de texas', 'gaceta de sonora'],
    'medicamentos-imss': ['medicamentos del imss', 'compra de medicamentos', 'compras de medicinas', 'ventiladores del imss', 'cyber robotic'],
    'deuda-congreso-2027': ['ley de ingresos 2027', 'aprobo mas deuda', 'techo de deuda 2027', 'perdon de multas', 'hr ratings'],
    'inversion-megaobras': ['megaobras', 'megaobra', 'inversion en megaobras', 'inversiones en megaobras', 'fobaproa', 'farac', 'agronitrogenados', 'fertinal', 'estela de luz', 'bunker', 'refineria de tula', 'barda de tula', 'enciclomedia', 'obras de cada sexenio'],
}


def bot_fichas():
    """Una ficha por investigación para «Pregúntale al Auditor» (23-10-2026):
    la contesta cuando le llega la pregunta de su diapositiva. Las cifras
    son las mismas de la lectura breve (window.AUDIT_DB), con su estado."""
    pq = preguntas_portada()
    out = []
    for a in AUDITORIAS:
        id_ = a[0]
        if not TEMA_BOT.get(id_):
            raise SystemExit('auditorias.py: la investigacion %s no tiene sus frases en TEMA_BOT' % id_)
        d = _datos(id_)
        out.append({'t': 'investigacion', 'tit': re.sub('<[^>]+>', '', a[5]), 'txt': d['que'],
                    'ci': [dict({'v': v, 'etq': etq, 'e': e}, **({'p': pend} if pend else {})) for v, etq, e, pend in d['cuanto']],
                    'fu': _docs_planos(d['docs']), 'qs': [q for q in (pq.get(id_), a[6]) if q],
                    'ir': [archivo(id_), 'la investigación en imágenes'],
                    'exp': ('expedientes.html#exp-' + EXPEDIENTE[id_]) if id_ in EXPEDIENTE else '',
                    'k': TEMA_BOT.get(id_, [])})
    return out


def capitulo_inspector():
    """El capítulo «Auditoría en imágenes» del Modo Inspector, aplicación 1
    (pedido del autor, 23-10-2026). No repite cifras: es la puerta a cada
    investigación, a su expediente de la ASF, si lo tiene, y al chat."""
    pq = preguntas_portada()
    filas = []
    for a in AUDITORIAS:
        id_, img, nota_img, alt, etq, tit, preg = a
        q = pq.get(id_) or preg
        acc = ['<a class="ia-boton ia-boton-pri" href="%s">📖 Ver la investigación</a>' % archivo(id_)]
        if id_ in EXPEDIENTE:
            acc.append('<a class="ia-boton" href="expedientes.html#exp-%s">📂 Su expediente de la ASF</a>' % EXPEDIENTE[id_])
        acc.append('<a class="ia-boton" href="%s">💬 Pregúntale al Auditor</a>' % esc_attr(chat_url(q)))
        filas.append('<li class="ia-au"><a class="ia-au-img" href="%s"><img src="%s" alt="%s" loading="lazy" width="480" height="270">'
                     '<span class="ia-au-nota">%s</span></a><div class="ia-au-tx"><span class="ia-au-etq">%s</span>'
                     '<h3><a href="%s">%s</a></h3><p>%s</p><p class="ia-au-acc">%s</p></div></li>'
                     % (archivo(id_), img, esc_attr(alt), html.escape(nota_img), html.escape(etq), archivo(id_), tit,
                        html.escape(q), ' '.join(acc)))
    n_exp = sum(1 for a in AUDITORIAS if a[0] in EXPEDIENTE)
    return ('<p class="ia-txt">Las %d investigaciones de la portada, cada una con su página: el dinero paso a paso, quién interviene '
            'y qué falta saber, con cada cifra y su documento. %d de ellas tienen expediente de la Auditoría Superior en el capítulo anterior; '
            'las otras se arman con el Presupuesto, la Ley de Ingresos y la Cuenta Pública.</p>\n        <ul class="ia-aus">%s</ul>'
            % (len(AUDITORIAS), n_exp, ''.join(filas)))


def portada():
    """Escribe en index.html lo que la portada toma de aqui: los enlaces de
    las tres acciones de cada diapositiva (data-*). La lista de
    investigaciones por tema ya no va ahi: vive al pie de cada investigacion
    (temas()) y en el indice general. index.html se edita en binario para no tocar
    sus CRLF ni sus CR sueltos."""
    ruta_idx = os.path.join(RAIZ, 'index.html')
    d = open(ruta_idx, 'rb').read().decode('utf-8')
    au = {a[0]: a for a in AUDITORIAS}

    orden = iter(_bloques_portada(d))

    def attrs(m):
        id_, q = next(orden)
        ancla, _, insp, _ = RUTAS[id_]
        nom = esc_attr(re.sub('<[^>]+>', '', au[id_][5]))
        return ('<a class="showcase-slide" href="%s" data-caso="%s" data-nombre="%s" data-numeros="sigue-el-dinero.html?abrir=%s" '
                'data-evidencia="%s" title="Pregúntale al Auditor: %s"') % (esc_attr(chat_url(q)), archivo(id_), nom, ancla, insp, nom)
    d, n = re.subn(r'<a class="showcase-slide" href="[^"]*"(?: data-caso="[^"]*")?(?: data-nombre="[^"]*" data-numeros="[^"]*" data-evidencia="[^"]*")?(?: title="[^"]*")?',
                   attrs, d)
    if n != len(AUDITORIAS):
        print('ERROR: la portada no tiene las %d diapositivas (%d)' % (len(AUDITORIAS), n))
        return 1
    open(ruta_idx, 'wb').write(d.encode('utf-8'))
    return 0


def generar(sello):
    for a in AUDITORIAS:
        texto = pagina(a, sello).replace('\r\n', '\n').replace('\n', '\r\n')
        open(os.path.join(RAIZ, archivo(a[0])), 'wb').write(texto.encode('utf-8'))
    print('auditorías en imágenes: %d páginas generadas con el sello %s' % (len(AUDITORIAS), sello))
    return portada()
