#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integra en window.AUDIT_DB el bloque `auditorias_actuales` para las cuatro
nuevas investigaciones de «Auditoría en imágenes» (26-10-2026):
  1. ine-contratos (INE: Ramo 22, ASF y contratos en revisión)
  2. guaymas-gas (Guaymas, Gaceta Parlamentaria y Golfo de California)
  3. medicamentos-imss (Compras de medicamentos y contratos del IMSS en ComprasMX)
  4. deuda-congreso-2027 (Ley de Ingresos 2027, techo de deuda y calificación BBB)

Todas las cifras provienen de los documentos oficiales ya verificados en la
plataforma (inspector_federal, cuenta_publica_asf, ambiente, paquete_2027,
comprasmx/inst.js y las columnas de Verificamos en columnas.js).
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from integrar_costo_vivo_megaobras import bloque_json  # noqa: E402


def _cargar_inst():
    ruta = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'comprasmx', 'inst.js')
    s = open(ruta, encoding='utf-8').read()
    return json.loads(s[s.index('{'):s.rindex('}') + 1])['i']


def construir(d):
    inst = _cargar_inst()
    imss = inst['050GYR']
    imss_b = inst['056AYO']
    birmex = inst['012NEF']

    ine_ente = next(x for x in d['inspector_federal']['entes'] if x['id'] == 'ine')
    cp_gob = next(x for x in d['cuenta_publica_asf']['cp2024']['grupos'] if x['grupo'] == 'Gobierno')
    ine_asf = next(x for x in cp_gob['sectores'] if 'Electoral' in x['nombre'])
    mdb24 = d['cuenta_publica_asf']['fuentes']['MDB2024']

    amb_p = d['ambiente']['presupuesto']
    unidades = {u['ur']: u for u in amb_p['unidades']}

    return {
        'ine-contratos': {
            'ente': 'Instituto Nacional Electoral (Ramo 22)',
            'quien': 'El Instituto Nacional Electoral ejerce el Ramo 22; la Cámara de Diputados aprueba su presupuesto y recibe la renuncia o designa a su presidencia; la Auditoría Superior de la Federación y el Órgano Interno de Control del INE fiscalizan sus contrataciones.',
            'que': (
                'El 24 de octubre de 2026 la Presidencia del INE publicó que respalda la investigación que la Auditoría Superior de la Federación '
                'abrió de oficio sobre contrataciones, que envió los antecedentes a su Órgano Interno de Control y que abrirá un micrositio con '
                'los contratos, montos, proveedores y documentos. Un día después, el 25 de octubre, su consejera presidenta anunció que el 26 de '
                'octubre presentaría su renuncia ante la Cámara de Diputados. En el único documento de licitación del INE que pudimos abrir donde '
                'aparece Cajas Graf (fallo LP-INE-001/2025, del 6 de febrero de 2025, para urnas y mamparas de la elección judicial), su propuesta '
                'en participación conjunta no cumplió las especificaciones técnicas.'
            ),
            'falta': (
                'Los contratos que la prensa suma en al menos $245 millones de pesos para Cajas Graf (en el INE y en el Instituto Estatal Electoral '
                'de Sonora) siguen pendientes: falta de la plataforma abrir los contratos oficiales. En ComprasMX 2025-2026 no aparece Cajas Graf, '
                'pero tampoco el INE, porque como órgano autónomo no contrata en esa plataforma. Una investigación abierta no es una resolución.'
            ),
            'pendiente_id': 'red-taddei-renuncia-ine-contratos-4',
            'cifras': {
                'ejercido_2025_mdp': ine_ente['cp2025']['ejercido'],
                'aprobado_2026_mdp': ine_ente['av2026']['aprobado'],
                'calendario_2t_2026_mdp': ine_ente['av2026']['calendarioAlCorte'],
                'pagado_2t_2026_mdp': ine_ente['av2026']['pagado'],
                'asf_cp2024_auditorias': ine_asf['auditorias'],
                'asf_cp2024_po': ine_asf['PO'],
                'asf_cp2024_por_aclarar_mdp': round(ine_asf['porAclarar'] / 1e6, 1),
                'asf_cp2024_recuperado_mdp': round(ine_asf['recuperaciones'] / 1e6, 1),
            },
            'fuentes': [
                {
                    'doc': 'Presupuesto de Egresos de la Federación 2026, Anexo 1, Ramo 22 Instituto Nacional Electoral',
                    'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/PEF_2026.pdf',
                },
                {
                    'doc': mdb24['corto'] + ' (Ramo 22, Instituto Nacional Electoral)',
                    'url': mdb24['url'],
                },
                {
                    'doc': 'INE, Central Electoral: La Presidencia del INE respalda la investigación de la ASF (24-10-2026)',
                    'url': 'https://centralelectoral.ine.mx/2026/10/24/la-presidencia-del-ine-respalda-la-investigacion-de-la-asf-y-reafirma-su-compromiso-con-el-estado-de-derecho/',
                },
                {
                    'doc': 'INE, Central Electoral: Mensaje de la Consejera Presidenta del INE (25-10-2026)',
                    'url': 'https://centralelectoral.ine.mx/2026/10/25/mensaje-de-la-consejera-presidenta-del-instituto-nacional-electoral-guadalupe-taddei-zavala/',
                },
                {
                    'doc': 'INE, Dirección Ejecutiva de Administración: fallo de la licitación pública LP-INE-001/2025 (06-02-2025)',
                    'url': 'https://ine.mx/wp-content/uploads/2025/02/lp-ine-001-2025-fallo.pdf',
                },
            ],
        },
        'guaymas-gas': {
            'ente': 'Secretaría de Energía, ASEA (Ramo 16), Gobierno de Sonora y Congreso del Estado de Sonora',
            'quien': 'La empresa Epcilon LNG LLC promueve el proyecto AMIGO; el Departamento de Energía de EE. UU. autorizó la exportación de gas (Orden 4629); la Secretaría de Energía y la ASEA (Ramo 16) intervienen en el ámbito federal; en el Congreso de Sonora se presentó el exhorto en la Gaceta Parlamentaria No. 2104.',
            'que': (
                'El proyecto AMIGO busca instalar una planta de licuefacción de gas natural en el Parque Industrial Pesquero «General Rodolfo '
                'Sánchez Taboada», en Guaymas, Sonora. En tribuna del Congreso de Sonora y en redes se señaló la entrega en comodato gratuito '
                'de 54 hectáreas de suelo público para procesar gas de Texas y enviarlo a Asia, y el 12 de febrero de 2026 diputados presentaron '
                'en la Gaceta Parlamentaria No. 2104 un exhorto a la ASEA, al INECC y a la Semarnat para revisar los tres proyectos de gas del '
                'Golfo de California (Saguaro, AMIGO y Vista Pacífico). El 21 de octubre de 2026 la Secretaría de Energía reportó 41.7 hectáreas, '
                'hasta 60 buques al año (el 4 % del tránsito de la zona) y 290 mil m³ de almacenamiento, y la Presidenta informó que la obra está '
                'detenida por amparos mientras se revisan de nuevo los impactos ambientales.'
            ),
            'falta': (
                'El contrato de comodato sobre el predio en Guaymas no está publicado por el Gobierno de Sonora (pendiente en el Registro), y el '
                'resolutivo de impacto ambiental de la ASEA tampoco se pudo abrir desde la plataforma. Tampoco se ha publicado cuánto pagaría el '
                'proyecto en impuestos y derechos ni qué parte se quedaría en Sonora.'
            ),
            'pendiente_id': 'red-guaymas-comodato-amigo-gnl-1',
            'pendiente_mia_id': 'red-guaymas-comodato-amigo-gnl-8',
            'cifras': {
                'superficie_sener_ha': 41.7,
                'superficie_tribuna_ha': 54.0,
                'diferencia_ha': 12.3,
                'buques_anuales': 60,
                'almacenamiento_mil_m3': 290,
                'doe_mmmpc_anuales': 395,
                'asea_2026_mdp': round(unidades['G00']['aprobado'] / 1e6, 1),
                'asea_2027_mdp': round(unidades['G00']['proyecto2027'] / 1e6, 1),
                'profepa_2026_mdp': round(unidades['E00']['aprobado'] / 1e6, 1),
                'conanp_2026_mdp': round(unidades['F00']['aprobado'] / 1e6, 1),
                'inecc_2026_mdp': round(unidades['RJJ']['aprobado'] / 1e6, 1),
            },
            'fuentes': [
                {
                    'doc': 'Presidencia de la República: versión estenográfica del 21-10-2026 (Secretaría de Energía, proyecto en Guaymas)',
                    'url': 'https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-claudia-sheinbaum-pardo-del-21-de-octubre-de-2026',
                },
                {
                    'doc': 'Congreso del Estado de Sonora: Gaceta Parlamentaria No. 2104, sesión del 12-02-2026 (exhorto sobre Saguaro, AMIGO y Vista Pacífico)',
                    'url': 'https://gestion.api.congresoson.gob.mx/publico/descarga?uuid=f8cf663d-4257-4f5d-8b08-b05b80a83e72',
                },
                {
                    'doc': 'Departamento de Energía de EE. UU.: Orden DOE/FE 4629 (08-12-2020), expediente 20-31-LNG (Epcilon LNG LLC)',
                    'url': 'https://www.energy.gov/sites/prod/files/2020/12/f81/ord4629.pdf',
                },
                {
                    'doc': 'Presupuesto de Egresos de la Federación 2026, Ramo 16 Medio Ambiente y Recursos Naturales (ASEA, PROFEPA, CONANP e INECC)',
                    'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/PEF_2026.pdf',
                },
            ],
        },
        'medicamentos-imss': {
            'ente': 'IMSS (050GYR), IMSS-Bienestar (056AYO) y Birmex (012NEF)',
            'quien': 'El IMSS, el IMSS-Bienestar y Birmex contratan medicamentos e insumos médicos; la Secretaría Anticorrupción y Buen Gobierno publica los datos abiertos de ComprasMX y las circulares de inhabilitación en el Diario Oficial.',
            'que': (
                'En los datos abiertos de ComprasMX de 2025 y 2026, el IMSS registra 31,666 contratos por $381,890.6 millones de pesos, de los '
                'cuales $202,923.6 millones (53.1 %) se asignaron por adjudicación directa; IMSS-Bienestar suma 14,835 contratos por $227,202.8 '
                'millones (50.7 % por adjudicación directa), y Birmex registra 198 contratos por $35,853.1 millones (98.6 % por adjudicación '
                'directa). Respecto a los casos que circulan en redes: en mayo de 2020 el IMSS en Hidalgo devolvió 20 ventiladores sin haber '
                'pagado un peso porque no cumplían las especificaciones técnicas, y el Diario Oficial publicó la inhabilitación por 27 meses de '
                'Cyber Robotic Solutions (circular 11/2020).'
            ),
            'falta': (
                'Los señalamientos de prensa sobre más de $800 millones de pesos en adjudicaciones directas de medicinas atribuidas a redes de '
                'particulares siguen pendientes: ningún documento oficial abierto liga esos nombres con una razón social contratista, y los '
                'contratos de 2023 y 2024 están en el CompraNet histórico, que no responde.'
            ),
            'pendiente_id': 'red-salud-ventiladores-y-medicinas-4',
            'cifras': {
                'imss_contratos': imss['c'],
                'imss_monto_mdp': round(imss['m'] / 1e6, 1),
                'imss_adj_directa_contratos': imss['ad'],
                'imss_adj_directa_mdp': round(imss['mad'] / 1e6, 1),
                'imss_adj_directa_pct': round(imss['mad'] / imss['m'] * 100, 1),
                'imss_competencia_mdp': round((imss['m'] - imss['mad']) / 1e6, 1),
                'imss_bienestar_contratos': imss_b['c'],
                'imss_bienestar_monto_mdp': round(imss_b['m'] / 1e6, 1),
                'imss_bienestar_adj_directa_mdp': round(imss_b['mad'] / 1e6, 1),
                'imss_bienestar_adj_directa_pct': round(imss_b['mad'] / imss_b['m'] * 100, 1),
                'birmex_contratos': birmex['c'],
                'birmex_monto_mdp': round(birmex['m'] / 1e6, 1),
                'birmex_adj_directa_mdp': round(birmex['mad'] / 1e6, 1),
                'birmex_adj_directa_pct': round(birmex['mad'] / birmex['m'] * 100, 1),
                'ventiladores_2020_inhabilitacion_meses': 27,
            },
            'proveedores_imss': [
                {'nombre': p[1], 'rfc': p[0], 'contratos': p[2], 'monto_mdp': round(p[3] / 1e6, 1)}
                for p in imss['p'][:6]
            ],
            'fuentes': [
                {
                    'doc': 'ComprasMX, Datos Abiertos: Datos relevantes de los contratos 2025 y 2026 (IMSS 050GYR, IMSS-Bienestar 056AYO y Birmex 012NEF)',
                    'url': 'https://comprasmx.buengobierno.gob.mx/datos-abiertos',
                },
                {
                    'doc': 'IMSS: comunicado sobre la devolución sin pago de los ventiladores en Hidalgo (13-05-2020)',
                    'url': 'https://www.gob.mx/imss/prensa/respecto-a-la-informacion-sobre-la-compra-de-ventiladores-por-el-organo-de-operacion-administrativa-desconcentrada-hidalgo-el-imss-informa',
                },
                {
                    'doc': 'Diario Oficial de la Federación: Circular 11/2020 que inhabilita 27 meses a Cyber Robotic Solutions, S.A. de C.V. (06-07-2020)',
                    'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5596199&fecha=06/07/2020',
                },
            ],
        },
        'deuda-congreso-2027': {
            'ente': 'Congreso de la Unión (Cámara de Diputados y Senado) y Secretaría de Hacienda y Crédito Público',
            'quien': 'La Secretaría de Hacienda propone la Iniciativa de Ley de Ingresos; la Cámara de Diputados (15-10-2026) y el Senado de la República autorizan los ingresos y el techo de endeudamiento (art. 73, fracc. VIII constitucional); las agencias calificadoras evalúan el riesgo soberano.',
            'que': (
                'El 15 de octubre de 2026 el pleno de la Cámara de Diputados aprobó la Ley de Ingresos de la Federación para 2027 (331 votos a '
                'favor y 118 en contra en lo general), y el 21 de octubre la avalaron las comisiones unidas del Senado (18 a 11). El dictamen '
                'estima ingresos totales por $10,636,488.0 millones de pesos y autoriza un techo de endeudamiento interno neto del Gobierno '
                'Federal hasta por $1,700,000.0 millones ($1.7 billones). Además, aprobó una reserva al artículo vigésimo primero transitorio que '
                'quita el tope de $300 millones de pesos de ingresos anuales y permite a grandes contribuyentes obtener la reducción de multas, '
                'recargos y gastos de ejecución si pagan completo su adeudo principal. Ese mismo 15 de octubre, en su Comunicado 82, Hacienda '
                'informó que HR Ratings bajó la calificación soberana de largo plazo de México de BBB+ a BBB, con perspectiva estable.'
            ),
            'falta': (
                'Falta la votación del pleno del Senado y la publicación del decreto en el Diario Oficial de la Federación para confirmar el texto '
                'definitivo del transitorio vigésimo primero. Además, el reporte de HR Ratings (donde constan sus razones y sus proyecciones de '
                'déficit de 4.6 % del PIB y deuda de 61.2 % en 2030) sigue pendiente porque su portal no abrió desde la plataforma.'
            ),
            'pendiente_id': 'red-hr-ratings-baja-mexico-bbb-3',
            'cifras': {
                'ingresos_totales_2027_mdp': 10636488.0,
                'ingresos_presupuestarios_2027_mdp': 9156528.9,
                'techo_deuda_interna_2027_mdp': 1700000.0,
                'costo_financiero_2027_mdp': 1636247.1,
                'rfsp_2027_mdp': 1555655.8,
                'financiamiento_2027_mdp': round(10636488.0 - 9156528.9, 1),
                'votos_diputados_favor': 331,
                'votos_diputados_contra': 118,
                'ajuste_fiscal_2025_pp_pib': 1.3,
            },
            'fuentes': [
                {
                    'doc': 'Canal del Congreso: Aprueban en San Lázaro Ley de Ingresos 2027 (15-10-2026)',
                    'url': 'https://www.canaldelcongreso.gob.mx/noticias/10320',
                },
                {
                    'doc': 'Canal del Congreso: Modificación a Ley de Ingresos busca ampliar beneficios de regularización fiscal (16-10-2026)',
                    'url': 'https://www.canaldelcongreso.gob.mx/noticias/10322',
                },
                {
                    'doc': 'Canal del Congreso: Comisiones del Senado aprueban Ley de Ingresos 2027 (21-10-2026)',
                    'url': 'https://www.canaldelcongreso.gob.mx/noticias/10329',
                },
                {
                    'doc': 'SHCP, Comunicado No. 82: México mantiene el grado de inversión con las ocho agencias calificadoras; HR Ratings ajusta de BBB+ a BBB (15-10-2026)',
                    'url': 'https://www.gob.mx/shcp/prensa/comunicado-no-82',
                },
                {
                    'doc': 'SHCP, Criterios Generales de Política Económica para 2027 (Gaceta Parlamentaria, 08-09-2026)',
                    'url': 'https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-C.pdf',
                },
            ],
        },
    }


def main():
    raw = open(DB, 'rb').read().decode('utf-8')
    d = json.loads(raw[raw.index('{'):raw.rindex('}') + 1])
    datos = construir(d)
    nl = '\r\n'
    txt = json.dumps(datos, ensure_ascii=False, indent=2)
    txt = '\n  '.join(txt.split('\n')).replace('\n', nl)
    if '"auditorias_actuales": {' in raw:
        a, b = bloque_json(raw, 'auditorias_actuales')
        raw = raw[:a] + txt + raw[b:]
    else:
        fin = raw.rindex(nl + '};')
        raw = raw[:fin] + ',' + nl + '  "auditorias_actuales": ' + txt + raw[fin:]
    open(DB, 'wb').write(raw.encode('utf-8'))
    # Verificar lone CRs (deben seguir siendo 2 en audit-database.js)
    b_raw = open(DB, 'rb').read()
    lone_cr = b_raw.count(b'\r') - b_raw.count(b'\r\n')
    print('auditorias_actuales integradas en audit-database.js (%d casos, lone CRs: %d)' % (len(datos), lone_cr))


if __name__ == '__main__':
    main()
