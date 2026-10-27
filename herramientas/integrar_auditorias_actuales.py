#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integra en window.AUDIT_DB el bloque `auditorias_actuales` para las
investigaciones de «Auditoría en imágenes» (26-10-2026):
  1. ine-contratos (INE: Ramo 22, ASF y contratos en revisión)
  2. guaymas-gas (Guaymas, Gaceta Parlamentaria y Golfo de California)
  3. medicamentos-imss (Compras de medicamentos y contratos del IMSS en ComprasMX)
  4. deuda-congreso-2027 (Ley de Ingresos 2027, techo de deuda y calificación BBB)
  5. inversion-megaobras (Panorama de las 11 obras y 2 rescates de seis sexenios)
  6. Las 8 obras y rescates individuales de `simulador_megaobras` que faltaban
     como página propia (`agronitrogenados`, `fertinal`, `estela-luz`,
     `bunker-garcia-luna`, `refineria-tula`, `enciclomedia`, `fobaproa`,
     `farac-carretero`), para que las 13 tengan su propia `auditoria-<id>.html`.

Todas las cifras provienen de los documentos oficiales ya verificados en la
plataforma (inspector_federal, cuenta_publica_asf, ambiente, paquete_2027,
comprasmx/inst.js, simulador_megaobras y las columnas de Verificamos en
columnas.js).
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from integrar_costo_vivo_megaobras import bloque_json  # noqa: E402
import mo_base  # noqa: E402
import mo_sector  # noqa: E402
import mo_tabla  # noqa: E402


def _cargar_inst():
    ruta = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'comprasmx', 'inst.js')
    s = open(ruta, encoding='utf-8').read()
    return json.loads(s[s.index('{'):s.rindex('}') + 1])['i']


def _obras_individuales(sm, obras_mo):
    por_id = {o['id']: o for o in obras_mo}
    ver = sm['verificacion']['obras']
    fmap = sm['verificacion']['fuentes']
    cta_map = (sm.get('cuenta') or {}).get('obras') or {}

    def fdoc(claves, extras=None):
        res = []
        for k in claves:
            f = fmap[k]
            res.append({'doc': f['doc'], 'url': f['url']})
        for ex in (extras or []):
            res.append(ex)
        return res

    o_agro = por_id['agronitrogenados']
    v_agro = ver['agronitrogenados']
    o_fert = por_id['fertinal']
    v_fert = ver['fertinal']
    f_fert_24 = next(x for x in cta_map['fertinal'] if x['c'] == 'resultado_anual_mdp')
    o_est = por_id['estela-luz']
    v_est = ver['estela-luz']
    o_bunk = por_id['bunker-garcia-luna']
    v_bunk = ver['bunker-garcia-luna']
    r_bunk_real = o_bunk['rangos_campos']['inversion_real_mdp']
    r_bunk_sob = o_bunk['rangos_campos']['sobrecosto_pct']
    o_tula = por_id['refineria-tula']
    v_tula = ver['refineria-tula']
    o_enc = por_id['enciclomedia']
    v_enc = ver['enciclomedia']
    o_fob = por_id['fobaproa']
    v_fob = ver['fobaproa']
    o_far = por_id['farac-carretero']
    v_far = ver['farac-carretero']

    return {
        'agronitrogenados': {
            'ente': 'Petróleos Mexicanos (PMI Comercio Internacional, Pro-Agroindustria y Pemex Fertilizantes)',
            'quien': 'El Consejo de Administración de Pemex autorizó la compra y rehabilitación en diciembre de 2013 (Acuerdo CA-146/2013); PMI Comercio Internacional y Pro-Agroindustria ejecutaron la operación en Pajaritos, Coatzacoalcos, Veracruz; la Auditoría Superior de la Federación revisó las Cuentas Públicas 2015 y 2017.',
            'que': (
                'En diciembre de 2013 el Consejo de Administración de Pemex aprobó el proyecto «Adquisición de una empresa de fertilizantes '
                '(Agronitrogenados)» por $7,894.2 millones de pesos (475 millones de dólares de esa fecha: 275 millones por los activos y '
                '200 millones para rehabilitar la planta, que llevaba 14 años sin operar). En 2014 PMI pagó $5,427.2 millones por los activos '
                '(264.1 millones de dólares) y, entre septiembre de 2014 y diciembre de 2017, destinó otros $8,271.1 millones (499 millones de '
                'dólares) a rehabilitar las plantas de urea I y II y sus servicios auxiliares: el desembolso acumulado subió a $13,698.3 millones '
                '(+73.5 % frente a lo autorizado). Además, la ASF documentó la baja contable de tres plantas ociosas por $4,206.0 millones y '
                'que al cierre de 2017 la planta aún no producía urea comercial.'
            ),
            'falta': (
                'Pemex no publica un estado de resultados individualizado de Pro-Agroindustria que separe los ingresos por venta de urea de '
                'la planta de Pajaritos, su costo de gas natural y su pérdida o utilidad anual: permanece en el Registro de pendientes '
                '(ficha cuenta-agronitrogenados).'
            ),
            'pendiente_id': 'cuenta-agronitrogenados',
            'caja': 'Planta de Pajaritos',
            'cont': [
                {'ico': '📐', 'tit': 'Autorizado en 2013', 'v': round(o_agro['inversion_presupuestada_mdp'], 1), 'f': 'mdp1', 'etq': '475 millones de dólares autorizados en el Acuerdo CA-146/2013 (17-12-2013)', 'est': 'oficial'},
                {'ico': '🏭', 'tit': 'Compra de activos (2014)', 'v': 5427.2, 'f': 'mdp1', 'etq': 'pagado por activos que llevaban 14 años fuera de operación (264.1 MUSD)', 'est': 'oficial'},
                {'ico': '🔧', 'tit': 'Rehabilitación (2014–2017)', 'v': 8271.1, 'f': 'mdp1', 'etq': '499 MUSD ejercidos en las plantas de urea I y II sin lograr operación comercial en 2017', 'est': 'oficial'},
                {'ico': '📈', 'tit': 'Costo real acumulado', 'v': round(o_agro['inversion_real_mdp'], 1), 'f': 'mdp1', 'etq': '+73.5 % frente al monto autorizado (+$5,804.1 millones)', 'est': 'derivado'},
                {'ico': '⏳', 'tit': 'Operación anual hoy', 'txt': 'Sin desglose propio', 'etq': 'Pemex consolida Fertilizantes sin estado de resultados por planta', 'est': 'pendiente', 'pend': 'cuenta-agronitrogenados'},
            ],
            'rastroTit': 'Los tramos del gasto y deterioro en Agronitrogenados documentados por la ASF (CP 2015 y CP 2017)',
            'rastroEst': 'oficial',
            'rastro': [
                {'k': 'Rehabilitación de plantas de urea I y II y servicios auxiliares (sep-2014 a dic-2017)', 'sub': '499.0 millones de dólares ejercidos · ASF CP 2017, aud. 492-DE', 'v': 8271.1, 'url': fmap['asf_fert17']['url'], 'est': 'oficial'},
                {'k': 'Compra de los activos de Agronitrogenados en Pajaritos (2014)', 'sub': '264.1 millones de dólares pagados · ASF CP 2017, aud. 492-DE', 'v': 5427.2, 'url': fmap['asf_fert17']['url'], 'est': 'oficial'},
                {'k': 'Baja contable de tres plantas ociosas por deterioro', 'sub': 'Activos dados de baja tras la compra · ASF CP 2017, aud. 492-DE', 'v': 4206.0, 'url': fmap['asf_fert17']['url'], 'est': 'oficial'},
                {'k': 'Intereses y comisiones bancarias pagados en 2015 con la planta detenida', 'sub': 'Financiamiento pagado antes de iniciar producción · ASF CP 2015, aud. 498-DE', 'v': 148.1, 'url': fmap['asf_agro15']['url'], 'est': 'oficial'},
            ],
            'fuentes': fdoc(v_agro['fuentes']),
        },
        'fertinal': {
            'ente': 'Petróleos Mexicanos (Pemex Fertilizantes y PMX Fertilizantes Pacífico, S.A. de C.V.)',
            'quien': 'El Consejo de Administración de Pemex autorizó la compra en octubre de 2015 (Acuerdo CA-209/2015); las filiales de Pemex contrataron el financiamiento con Nafin, Bancomext y Banobras; la ASF fiscalizó las Cuentas Públicas 2016 y 2017 y Pemex Transformación Industrial reporta los resultados de PMX Fertilizantes Pacífico en la Cuenta Pública 2024.',
            'que': (
                'En octubre de 2015 el Consejo de Administración de Pemex autorizó adquirir Grupo Fertinal (mina de roca fosfórica en San Juan de '
                'la Costa, Baja California Sur, y complejo industrial en Lázaro Cárdenas, Michoacán) hasta por 635 millones de dólares ($12,532.0 '
                'millones de pesos al tipo de cambio del cierre). Para concretar la operación y liquidar los pasivos de la empresa, las filiales '
                'de Pemex contrataron créditos por $13,121.6 millones (+4.7 %), incluyendo un dividendo de 51 millones de dólares decretado antes '
                'de la compra. En su primer año en manos de Pemex (2016) la empresa registró una pérdida integral de $11,690.6 millones; en 2017 '
                'deterioró $4,007.0 millones de crédito mercantil, y en la Cuenta Pública 2024 su filial PMX Fertilizantes Pacífico reportó una '
                'pérdida neta anual de $3,600.1 millones.'
            ),
            'falta': (
                'Pemex Transformación Industrial publica la utilidad o pérdida neta de PMX Fertilizantes Pacífico en su nota de subsidiarias '
                '(-$3,600.1 millones en 2024), pero no desglosa por separado los ingresos y los costos operativos de esa filial en un estado de '
                'resultados abierto al público.'
            ),
            'pendiente_id': None,
            'caja': 'Lázaro Cárdenas y BCS',
            'cont': [
                {'ico': '📐', 'tit': 'Tope autorizado (2015)', 'v': round(o_fert['inversion_presupuestada_mdp'], 1), 'f': 'mdp1', 'etq': 'hasta 635 millones de dólares en el Acuerdo CA-209/2015 (26-10-2015)', 'est': 'oficial'},
                {'ico': '🏦', 'tit': 'Financiamiento contratado', 'v': round(o_fert['inversion_real_mdp'], 1), 'f': 'mdp1', 'etq': 'créditos con Nafin, Bancomext y Banobras para acciones y deuda (+4.7 %)', 'est': 'oficial'},
                {'ico': '📉', 'tit': 'Pérdida integral en 2016', 'v': 11690.6, 'f': 'mdp1', 'etq': 'primer año de operación en Pemex · ASF CP 2016, aud. 468-DE', 'est': 'oficial'},
                {'ico': '🧾', 'tit': 'Deterioro contable (2017)', 'v': 4007.0, 'f': 'mdp1', 'etq': '223.8 millones de dólares de crédito mercantil deteriorado · ASF CP 2017', 'est': 'oficial'},
                {'ico': '🔴', 'tit': 'Pérdida neta en 2024', 'v': abs(round(o_fert['res']['v'], 1)), 'f': 'mdp1', 'etq': 'resultado del ejercicio 2024 de PMX Fertilizantes Pacífico (CP 2024, Tomo VIII)', 'est': 'oficial'},
            ],
            'rastroTit': 'Desembolsos, pérdidas operativas y deterioros de Grupo Fertinal en Pemex (2015–2024)',
            'rastroEst': 'oficial',
            'rastro': [
                {'k': 'Financiamiento contratado para adquirir acciones y liquidar deuda de Fertinal (dic-2015)', 'sub': '635 millones de dólares al tipo de cambio del cierre · ASF CP 2016, aud. 468-DE', 'v': 13121.6, 'url': fmap['asf_fert16']['url'], 'est': 'oficial'},
                {'k': 'Pérdida integral del primer ejercicio en Pemex (2016)', 'sub': '565.9 millones de dólares de pérdida integral · ASF CP 2016, aud. 468-DE', 'v': 11690.6, 'url': fmap['asf_fert16']['url'], 'est': 'oficial'},
                {'k': 'Gasto de operación de 2016 frente a $5,892.9 millones de ingresos reales', 'sub': 'Los ingresos quedaron 41.3 % debajo de lo proyectado · ASF CP 2016, aud. 468-DE', 'v': 6903.8, 'url': fmap['asf_fert16']['url'], 'est': 'derivado'},
                {'k': 'Deterioro del crédito mercantil reconocido en 2017', 'sub': '223.8 millones de dólares de deterioro · ASF CP 2017, aud. 492-DE', 'v': 4007.0, 'url': fmap['asf_fert17']['url'], 'est': 'oficial'},
                {'k': 'Pérdida neta de PMX Fertilizantes Pacífico en el ejercicio 2024', 'sub': 'Estados financieros dictaminados 2024 de Pemex Transformación Industrial (Nota 3)', 'v': 3600.1, 'url': f_fert_24['f'][0]['url'], 'est': 'oficial'},
            ],
            'fuentes': fdoc(v_fert['fuentes'], [{'doc': f_fert_24['f'][0]['doc'], 'url': f_fert_24['f'][0]['url']}]),
        },
        'estela-luz': {
            'ente': 'Fideicomiso del Bicentenario, III Servicios, S.A. de C.V. (filial de Pemex) y Secretaría de Educación Pública',
            'quien': 'El Fideicomiso del Bicentenario y la filial de Pemex III Servicios, S.A. de C.V. contrataron y supervisaron el monumento en Paseo de la Reforma; Gutsa Infraestructura ejecutó la obra; la Auditoría Superior de la Federación practicó la revisión de situación excepcional en la Cuenta Pública 2011.',
            'que': (
                'El monumento conmemorativo del Bicentenario de la Independencia y Centenario de la Revolución («Estela de Luz», en Paseo de la '
                'Reforma, Ciudad de México) se adjudicó el 18 de diciembre de 2009 por $393.5 millones de pesos para entregarse en agosto de '
                '2010. Tras cuatro convenios modificatorios, el contrato de obra subió a $1,146.4 millones (+192.0 %) y el costo total del '
                'proyecto —con supervisión, estudios, asesorías y espectáculo inaugural— cerró en $1,304.9 millones (+231.6 %, más del triple '
                'del contrato original), inaugurándose en enero de 2012 con 16 meses de retraso. La ASF determinó pagos improcedentes por '
                '$399.2 millones: $248.9 millones en el precio y transporte del acero inoxidable importado de Finlandia y Alemania y $150.3 '
                'millones en cuarzo de Brasil, conceptos fuera de catálogo y penas convencionales no aplicadas.'
            ),
            'falta': (
                'Como monumento y espacio cultural, la Estela de Luz no opera como empresa ni cobra entrada. La Secretaría de Cultura no '
                'publica por separado cuánto cuesta cada año mantener la torre ni operar el Centro de Cultura Digital que funciona en su '
                'sótano: ese gasto anual queda en el Registro de pendientes (ficha cuenta-estela-luz).'
            ),
            'pendiente_id': 'cuenta-estela-luz',
            'caja': 'Paseo de la Reforma',
            'cont': [
                {'ico': '📐', 'tit': 'Contrato original (2009)', 'v': round(o_est['inversion_presupuestada_mdp'], 1), 'f': 'mdp1', 'etq': 'adjudicado el 18 de diciembre de 2009 a Gutsa Infraestructura', 'est': 'oficial'},
                {'ico': '🏗️', 'tit': 'Obra tras 4 convenios', 'v': 1146.4, 'f': 'mdp1', 'etq': '+192.0 % sobre el contrato de construcción (16 meses de retraso)', 'est': 'oficial'},
                {'ico': '💰', 'tit': 'Costo final del proyecto', 'v': round(o_est['inversion_real_mdp'], 1), 'f': 'mdp1', 'etq': '+231.6 % frente al contrato original (incluye supervisión, proyectos e inauguración)', 'est': 'oficial'},
                {'ico': '⚠️', 'tit': 'Pagos improcedentes (ASF)', 'v': 399.2, 'f': 'mdp1', 'etq': '$248.9 millones en acero y $150.3 millones en cuarzo y extraordinarios', 'est': 'derivado'},
                {'ico': '⏳', 'tit': 'Mantenimiento anual', 'txt': 'Sin desglose propio', 'etq': 'Cultura no separa el gasto de la torre ni del Centro de Cultura Digital', 'est': 'pendiente', 'pend': 'cuenta-estela-luz'},
            ],
            'rastroTit': 'De $393.5 millones a $1,304.9 millones: el costo y los pagos observados por la ASF en la Estela de Luz',
            'rastroEst': 'oficial',
            'rastro': [
                {'k': 'Costo final total del proyecto (obra, proyectos, supervisión e inauguración)', 'sub': '+231.6 % frente al contrato original · ASF, Revisión de Situación Excepcional CP 2011', 'v': 1304.9, 'url': fmap['asf_estela']['url'], 'est': 'oficial'},
                {'k': 'Monto contratado de construcción tras cuatro convenios modificatorios', 'sub': '+192.0 % respecto a los $393.5 millones contratados en diciembre de 2009', 'v': 1146.4, 'url': fmap['asf_estela']['url'], 'est': 'oficial'},
                {'k': 'Contrato original de construcción (18 de diciembre de 2009)', 'sub': 'Plazo original de entrega: agosto de 2010 (se entregó en enero de 2012)', 'v': 393.5, 'url': fmap['asf_estela']['url'], 'est': 'oficial'},
                {'k': 'Pagos injustificados en el precio por kilogramo y flete del acero inoxidable', 'sub': 'Observados por la ASF en la revisión de situación excepcional', 'v': 248.9, 'url': fmap['asf_estela']['url'], 'est': 'oficial'},
                {'k': 'Otros pagos improcedentes en cuarzo, conceptos fuera de catálogo y penas no aplicadas', 'sub': 'Suman $399.2 millones de pagos improcedentes junto con el acero', 'v': 150.3, 'url': fmap['asf_estela']['url'], 'est': 'oficial'},
            ],
            'fuentes': fdoc(v_est['fuentes']),
        },
        'bunker-garcia-luna': {
            'ente': 'Secretaría de Seguridad Pública Federal (Coordinación General de Plataforma México, Ramo 36)',
            'quien': 'La Secretaría de Seguridad Pública Federal (encabezada en 2006–2012 por Genaro García Luna) adjudicó sin licitación la obra civil a TRADECO Infraestructura y reservó los contratos tecnológicos de Plataforma México; la Auditoría Superior de la Federación auditó las Cuentas Públicas 2008, 2009 y 2011.',
            'que': (
                'El Centro Nacional de Inteligencia de Plataforma México («el Búnker», en Av. Constituyentes 947, Ciudad de México) se adjudicó '
                'sin licitación el 30 de mayo de 2008 (contrato SSP/OM/DGARMSG/0645/2008 con TRADECO Infraestructura) por $347.4 millones de '
                'pesos, bajo la excepción de seguridad pública. Un convenio de reducción bajó el contrato civil a $289.1 millones y la ASF '
                'observó $23.4 millones de pagos en exceso, duplicados o sin soporte en acabados e instalaciones: por ello, el costo de la obra '
                'civil se ubica en un rango oficial entre $236.9 millones (ejercido en el capítulo de obra pública 2008–2009) y $289.1 millones '
                '(contrato modificado), con punto medio de $263.0 millones. Ese monto solo cubre el edificio: el programa Plataforma México '
                'ejerció $1,188.5 millones en 2008 y $1,898.1 millones en 2011, pero la SSP reservó por 12 años los contratos del equipamiento '
                'tecnológico e informático del sótano.'
            ),
            'falta': (
                'El costo total del Búnker con sus pantallas, servidores, enlaces satelitales y software sigue pendiente en el Registro '
                '(ficha obra-bunker-garcia-luna) porque la SSP reservó los contratos tecnológicos; y la SSPC tampoco publica por separado '
                'cuánto cuesta hoy operar y mantener el inmueble (ficha cuenta-bunker-garcia-luna).'
            ),
            'pendiente_id': 'obra-bunker-garcia-luna',
            'caja': 'Obra civil vs. tecnología reservada',
            'cont': [
                {'ico': '📐', 'tit': 'Contrato de obra civil (2008)', 'v': round(o_bunk['inversion_presupuestada_mdp'], 1), 'f': 'mdp1', 'etq': 'adjudicado sin licitación a TRADECO el 30 de mayo de 2008', 'est': 'oficial'},
                {'ico': '🏢', 'tit': 'Obra civil (punto medio)', 'v': round(r_bunk_real['medio'], 1), 'f': 'mdp1', 'etq': 'rango oficial entre $236.9 y $289.1 millones (' + ('%.1f' % r_bunk_sob['medio']) + '% frente al contrato inicial)', 'est': 'derivado'},
                {'ico': '⚠️', 'tit': 'Pagos observados en el edificio', 'v': 23.4, 'f': 'mdp1', 'etq': 'volúmenes pagados de más, conceptos duplicados y equipos sin soporte (ASF CP 2009)', 'est': 'oficial'},
                {'ico': '📡', 'tit': 'Plataforma México en 2011', 'v': 1898.1, 'f': 'mdp1', 'etq': 'ejercido por la Coordinación General de Plataforma México · ASF CP 2011, aud. 16-GB', 'est': 'oficial'},
                {'ico': '🔒', 'tit': 'Equipamiento tecnológico', 'txt': 'Reservado 12 años', 'etq': 'la SSP reservó los contratos de sistemas del Búnker y la SSPC no ha publicado el total', 'est': 'pendiente', 'pend': 'obra-bunker-garcia-luna'},
            ],
            'rastroTit': 'Lo que sí pudo auditar la ASF del edificio y del presupuesto de Plataforma México (2007–2011)',
            'rastroEst': 'oficial',
            'rastro': [
                {'k': 'Ejercido por la Coordinación General de Plataforma México en 2011', 'sub': 'Presupuesto anual del programa de interconexión y sistemas · ASF CP 2011, aud. 16-GB', 'v': 1898.1, 'url': fmap['asf_pm11']['url'], 'est': 'oficial'},
                {'k': 'Ejercido en acciones asociadas a Plataforma México en 2008', 'sub': 'Incluye telecomunicaciones, cómputo e infraestructura · ASF CP 2008, Informe Sector Seguridad', 'v': 1188.5, 'url': fmap['asf_pm08']['url'], 'est': 'oficial'},
                {'k': 'Construcción de instalaciones y equipamiento de Plataforma México (2007–2009)', 'sub': '$195.9 millones en 2007, $127.6 millones en 2008 y $109.3 millones en 2009 · ASF CP 2009, aud. 1053', 'v': 432.7, 'url': fmap['asf_bunker09']['url'], 'est': 'oficial'},
                {'k': 'Contrato original de obra civil del edificio en Constituyentes 947', 'sub': 'Adjudicado sin licitación a TRADECO Infraestructura (30-05-2008) · ASF CP 2009, aud. 1053', 'v': 347.4, 'url': fmap['asf_bunker09']['url'], 'est': 'oficial'},
                {'k': 'Monto del contrato civil tras el convenio de reducción del 29-12-2008', 'sub': 'Cota superior del rango oficial de la obra civil · ASF CP 2009, aud. 1053', 'v': 289.1, 'url': fmap['asf_bunker09']['url'], 'est': 'oficial'},
                {'k': 'Pagos en exceso, conceptos duplicados y sin soporte observados en el edificio', 'sub': 'Determinados por la ASF en la auditoría de inversiones físicas 1053 (CP 2009)', 'v': 23.4, 'url': fmap['asf_bunker09']['url'], 'est': 'oficial'},
            ],
            'fuentes': fdoc(v_bunk['fuentes']),
        },
        'refineria-tula': {
            'ente': 'Pemex Refinación (hoy Pemex Transformación Industrial)',
            'quien': 'Pemex Refinación registró en cartera y ejerció los estudios de preinversión y el acondicionamiento del predio en Atitalaquia y Tula de Allende, Hidalgo; el Gobierno del Estado de Hidalgo adquirió los terrenos; la Auditoría Superior de la Federación fiscalizó el cierre en la Cuenta Pública 2014 (auditoría 315-DE).',
            'que': (
                'Anunciada en marzo de 2008 como la nueva «Refinería Bicentenario» en Tula, Hidalgo (con un primer registro en cartera de '
                '$7,613.3 millones de pesos en 2009 para su etapa inicial), la obra se dividió en dos proyectos de inversión autorizados por '
                '$3,714.0 millones: $1,475.2 millones para estudios de preinversión y $2,238.8 millones para acondicionar el sitio. Pemex '
                'Refinación ejerció $659.3 millones en 17 contratos de estudios e ingeniería básica y $468.3 millones en limpiar el terreno '
                'y levantar la barda perimetral ($1,127.6 millones en total, el 30.4 % de lo autorizado), antes de cancelar definitivamente '
                'el proyecto en diciembre de 2014 sin haber construido un solo tren de refinación.'
            ),
            'falta': (
                'El proyecto se canceló en diciembre de 2014 sin entrar en operación: los $1,127.6 millones ejercidos en estudios, limpieza '
                'del predio y barda perimetral quedaron como costo hundido, sin ingresos ni estado de resultados anual.'
            ),
            'pendiente_id': None,
            'caja': 'Cancelada en 2014',
            'cont': [
                {'ico': '📋', 'tit': 'Primer registro (2009)', 'v': 7613.3, 'f': 'mdp1', 'etq': 'monto inicial en cartera de inversión de Pemex Refinación en 2009', 'est': 'oficial'},
                {'ico': '📐', 'tit': 'Autorizado en 2 proyectos', 'v': round(o_tula['inversion_presupuestada_mdp'], 1), 'f': 'mdp1', 'etq': '$1,475.2 millones en estudios + $2,238.8 millones en terreno y barda', 'est': 'derivado'},
                {'ico': '📄', 'tit': 'Ejercido en 17 estudios', 'v': 659.3, 'f': 'mdp1', 'etq': 'estudios de preinversión e ingeniería básica (2010–2014) · ASF CP 2014', 'est': 'oficial'},
                {'ico': '🧱', 'tit': 'Ejercido en predio y barda', 'v': 468.3, 'f': 'mdp1', 'etq': 'limpieza, nivelación y barda perimetral en Atitalaquia y Tula · ASF CP 2014', 'est': 'oficial'},
                {'ico': '🚫', 'tit': 'Total hundido al cancelar', 'v': round(o_tula['inversion_real_mdp'], 1), 'f': 'mdp1', 'etq': 'se ejerció el 30.4 % (-69.6 % respecto a lo autorizado) y no se refinó un barril', 'est': 'derivado'},
            ],
            'rastroTit': 'En qué se fueron los $1,127.6 millones antes de cancelar la Refinería Bicentenario (ASF CP 2014)',
            'rastroEst': 'oficial',
            'rastro': [
                {'k': 'Presupuesto autorizado para acondicionamiento y preparación del sitio', 'sub': 'De ese monto se dejaron de ejecutar $1,770.5 millones al cancelar · ASF CP 2014, aud. 315-DE', 'v': 2238.8, 'url': fmap['asf_tula14']['url'], 'est': 'oficial'},
                {'k': 'Obra de acondicionamiento que se dejó de ejecutar por la cancelación', 'sub': '79.1 % del presupuesto del sitio no se ejerció · ASF CP 2014, aud. 315-DE', 'v': 1770.5, 'url': fmap['asf_tula14']['url'], 'est': 'oficial'},
                {'k': 'Presupuesto autorizado para estudios de preinversión', 'sub': 'Ingeniería básica, ambiental y de factibilidad · ASF CP 2014, aud. 315-DE', 'v': 1475.2, 'url': fmap['asf_tula14']['url'], 'est': 'oficial'},
                {'k': 'Ejercido en 17 contratos de estudios de preinversión (2010–2014)', 'sub': 'Costo hundido tras la cancelación del proyecto · ASF CP 2014, aud. 315-DE', 'v': 659.3, 'url': fmap['asf_tula14']['url'], 'est': 'oficial'},
                {'k': 'Ejercido en acondicionamiento del terreno y barda perimetral', 'sub': 'Única obra física ejecutada en el predio de Tula · ASF CP 2014, aud. 315-DE', 'v': 468.3, 'url': fmap['asf_tula14']['url'], 'est': 'oficial'},
            ],
            'fuentes': fdoc(v_tula['fuentes']),
        },
        'enciclomedia': {
            'ente': 'Secretaría de Educación Pública (Ramo 11) e Instituto Latinoamericano de la Comunicación Educativa (ILCE)',
            'quien': 'La Secretaría de Educación Pública diseñó y contrató el programa multianual (2004–2011) con apoyo del ILCE; la Secretaría de Hacienda autorizó el techo multianual en el oficio OM-402; la Auditoría Superior de la Federación auditó el programa en siete Cuentas Públicas consecutivas (2005 a 2011).',
            'que': (
                'El Programa Enciclomedia buscó equipar 125,562 aulas de 5.º y 6.º de primaria con pizarrones interactivos, proyectores, '
                'computadoras e impresoras bajo esquemas multianuales de arrendamiento y compra. Hacienda autorizó un techo multianual de '
                '$21,398.3 millones de pesos (oficio OM-402, para 2005–2010), pero al sumar lo ejercido en las siete auditorías de la ASF '
                'de 2001 a 2011 el gasto acumulado llegó a $32,315.7 millones (+51.0 %, $10,917.4 millones por encima de la autorización '
                'original). La ASF documentó lámparas de proyectores fundidas sin reemplazo, aulas sin energía eléctrica ni conectividad, '
                'pagos por equipos no localizados y licencias sin soporte, hasta que el programa se cerró en 2011.'
            ),
            'falta': (
                'El programa se extinguió en 2011 y sus equipos quedaron dados de baja o en desuso en los planteles, por lo que no existe '
                'operación ni estado de resultados vigente.'
            ),
            'pendiente_id': None,
            'caja': '2001–2011 · 7 auditorías ASF',
            'cont': [
                {'ico': '📐', 'tit': 'Techo multianual (OM-402)', 'v': round(o_enc['inversion_presupuestada_mdp'], 1), 'f': 'mdp1', 'etq': 'autorizado por Hacienda para equipar 125,562 aulas de primaria (2005–2010)', 'est': 'oficial'},
                {'ico': '💻', 'tit': 'Ejercido de 2001 a 2006', 'v': 6417.8, 'f': 'mdp1', 'etq': 'arranque y primeros contratos multianuales · ASF CP 2006, aud. 280', 'est': 'oficial'},
                {'ico': '📈', 'tit': 'Pico anual en 2007', 'v': 7145.8, 'f': 'mdp1', 'etq': 'año de mayor desembolso del programa · ASF CP 2007, aud. 392', 'est': 'oficial'},
                {'ico': '💰', 'tit': 'Total ejercido (2001–2011)', 'v': round(o_enc['inversion_real_mdp'], 1), 'f': 'mdp1', 'etq': '+51.0 % sobre el techo autorizado (+$10,917.4 millones en once años)', 'est': 'derivado'},
                {'ico': '🚫', 'tit': 'Estado del programa', 'txt': 'Extinto en 2011', 'etq': 'liquidado tras siete Cuentas Públicas con observaciones de la ASF', 'est': 'oficial'},
            ],
            'rastroTit': 'Lo que ejerció la SEP en Enciclomedia año por año según las siete auditorías de la ASF (2001–2011)',
            'rastroEst': 'oficial',
            'rastro': [
                {'k': 'Ejercido en el ejercicio fiscal 2007', 'sub': 'Cuenta Pública 2007 · ASF, auditoría 392', 'v': 7145.8, 'url': fmap['asf_encic07']['url'], 'est': 'oficial'},
                {'k': 'Ejercido acumulado de 2001 a 2006', 'sub': 'Cuentas Públicas 2005 (aud. 142) y 2006 (aud. 280)', 'v': 6417.8, 'url': fmap['asf_encic06']['url'], 'est': 'oficial'},
                {'k': 'Ejercido en el ejercicio fiscal 2008', 'sub': 'Cuenta Pública 2008 · ASF, auditoría 907', 'v': 5817.7, 'url': fmap['asf_encic08']['url'], 'est': 'oficial'},
                {'k': 'Ejercido en el ejercicio fiscal 2011 (cierre del programa)', 'sub': 'Cuenta Pública 2011 · ASF, auditoría 226-DS', 'v': 4720.6, 'url': fmap['asf_encic11']['url'], 'est': 'oficial'},
                {'k': 'Ejercido en el ejercicio fiscal 2010', 'sub': 'Cuenta Pública 2010 · ASF, auditoría 261-DS', 'v': 4665.5, 'url': fmap['asf_encic10']['url'], 'est': 'oficial'},
                {'k': 'Ejercido en el ejercicio fiscal 2009', 'sub': 'Cuenta Pública 2009 · ASF, auditoría 275', 'v': 3548.4, 'url': fmap['asf_encic09']['url'], 'est': 'oficial'},
            ],
            'fuentes': fdoc(v_enc['fuentes']),
        },
        'fobaproa': {
            'ente': 'Instituto para la Protección al Ahorro Bancario (IPAB) y Secretaría de Hacienda (Ramo 34 Erogaciones para los Programas de Apoyo a Ahorradores y Deudores de la Banca)',
            'quien': 'El Ejecutivo Federal presentó en 1998 la iniciativa para convertir los pasivos del FOBAPROA; el Congreso creó el IPAB en diciembre de 1998 y cada año aprueba transferencias fiscales en el Ramo 34 del Presupuesto de Egresos; el IPAB refinancia los Bonos de Protección al Ahorro (BPA) y publica sus estados financieros dictaminados.',
            'que': (
                'Este registro corresponde a un rescate financiero —no a una obra física—, por lo que se contabiliza aparte de las 11 obras. '
                'En febrero de 1998 el Ejecutivo pidió reconocer como deuda pública $552,300.0 millones de pesos de pasivos del FOBAPROA '
                '(Informe Mackey, Gaceta Parlamentaria del 23-09-1999). De 1999 a 2025 el erario federal ha transferido al IPAB $710,923.3 '
                'millones por el Ramo 34 (Programa de Apoyo a Ahorradores) y, aun después de veintisiete años de pagos, al 31 de diciembre de '
                '2025 los pasivos netos del IPAB siguen en $1,023,571.0 millones: el costo comprometido (lo ya pagado con impuestos más el saldo '
                'que falta por pagar) suma $1,734,494.3 millones (+214.0 % frente al pasivo de 1998), o $2,009,825.7 millones si se agregan los '
                '$275,331.4 millones de programas de apoyo a deudores. Tan solo en 2025 el Fondo FOBAPROA devengó $97,855.8 millones de '
                'intereses; sin la transferencia de $52,451.9 millones del Ramo 34, su déficit propio fue de -$59,971.8 millones.'
            ),
            'falta': (
                'Los estados financieros del IPAB y la Cuenta Pública del Ramo 34 están publicados al cierre de 2025; lo que sigue corriendo '
                'cada año es el servicio de la deuda de los Bonos de Protección al Ahorro ($35,553.4 millones aprobados en el Ramo 34 del '
                'PEF 2026).'
            ),
            'pendiente_id': None,
            'caja': 'Rescate 1998 · Sigue en pago',
            'cont': [
                {'ico': '📜', 'tit': 'Pasivo de febrero de 1998', 'v': round(o_fob['inversion_presupuestada_mdp'], 1), 'f': 'mdp1', 'etq': 'monto presentado al Congreso para convertir en deuda pública (Informe Mackey)', 'est': 'oficial'},
                {'ico': '🏛️', 'tit': 'Pagado por Ramo 34 (1999–2025)', 'v': 710923.3, 'f': 'mdp1', 'etq': 'transferencias presupuestarias acumuladas al Programa de Apoyo a Ahorradores', 'est': 'oficial'},
                {'ico': '🏦', 'tit': 'Saldo de deuda al cierre 2025', 'v': 1023571.0, 'f': 'mdp1', 'etq': 'pasivos totales ($1,134,548 mdp) menos activos ($110,977 mdp) del IPAB', 'est': 'oficial'},
                {'ico': '📈', 'tit': 'Costo comprometido total', 'v': round(o_fob['inversion_real_mdp'], 1), 'f': 'mdp1', 'etq': 'pagado + saldo por pagar (+214.0 % frente a 1998; $2,009,825.7 mdp con deudores)', 'est': 'derivado'},
                {'ico': '🔴', 'tit': 'Déficit 2025 sin Ramo 34', 'v': abs(round(o_fob['res']['v'], 1)), 'f': 'mdp1', 'etq': 'en 2025 devengó $97,855.8 millones de intereses y recibió $52,451.9 millones del PEF', 'est': 'derivado'},
            ],
            'rastroTit': 'De $552,300 millones en 1998 a $1,734,494.3 millones comprometidos al cierre de 2025 (IPAB y SHCP)',
            'rastroEst': 'oficial',
            'rastro': [
                {'k': 'Pasivos netos del IPAB al 31 de diciembre de 2025 (deuda que sigue viva)', 'sub': 'Pasivos totales ($1,134,548 mdp) menos activos ($110,977 mdp) · Estados Financieros IPAB 2025', 'v': 1023571.0, 'url': 'https://www.gob.mx/cms/uploads/attachment/file/1068974/Estados-Financieros_diciembre-2025.pdf', 'est': 'oficial'},
                {'k': 'Transferencias acumuladas del Ramo 34 para apoyo a ahorradores (1999–2025)', 'sub': 'Pagado con recursos fiscales del Presupuesto de Egresos · Plan Anual de Financiamiento 2026 del IPAB', 'v': 710923.3, 'url': 'https://www.gob.mx/cms/uploads/attachment/file/1043973/Plan-Anual-De-Financiamiento_2026.pdf', 'est': 'oficial'},
                {'k': 'Pasivo del FOBAPROA presentado al Congreso en febrero de 1998', 'sub': 'Cifra original antes de intereses acumulados · Informe Mackey, Gaceta Parlamentaria (23-09-1999)', 'v': 552300.0, 'url': 'https://gaceta.diputados.gob.mx/Gaceta/57/1999/sep/19990923-I.html', 'est': 'oficial'},
                {'k': 'Recursos fiscales adicionales destinados a programas de apoyo a deudores', 'sub': 'Reportados aparte del PAB en el Plan Anual de Financiamiento 2026 del IPAB', 'v': 275331.4, 'url': 'https://www.gob.mx/cms/uploads/attachment/file/1043973/Plan-Anual-De-Financiamiento_2026.pdf', 'est': 'oficial'},
                {'k': 'Intereses de la deuda devengados por el Fondo FOBAPROA tan solo en 2025', 'sub': 'Nota 20 de los estados financieros dictaminados del IPAB 2025', 'v': 97855.8, 'url': 'https://www.gob.mx/cms/uploads/attachment/file/1068974/Estados-Financieros_diciembre-2025.pdf', 'est': 'oficial'},
                {'k': 'Ramo 34 ejercido en 2025 ($52,451.9 mdp) y aprobado en el PEF 2026 ($35,553.4 mdp)', 'sub': 'Transferencia anual del erario para cubrir el costo financiero de los Bonos de Protección al Ahorro', 'v': 52451.9, 'url': fmap['pef26dof']['url'], 'est': 'oficial'},
            ],
            'fuentes': [
                {'doc': 'IPAB: Estados financieros dictaminados al 31 de diciembre de 2025 y 2024', 'url': 'https://www.gob.mx/cms/uploads/attachment/file/1068974/Estados-Financieros_diciembre-2025.pdf'},
                {'doc': 'IPAB: Plan Anual de Financiamiento 2026', 'url': 'https://www.gob.mx/cms/uploads/attachment/file/1043973/Plan-Anual-De-Financiamiento_2026.pdf'},
                {'doc': 'Gaceta Parlamentaria (Cámara de Diputados, 23-09-1999): Informe de Michael W. Mackey sobre el FOBAPROA', 'url': 'https://gaceta.diputados.gob.mx/Gaceta/57/1999/sep/19990923-I.html'},
            ] + fdoc(v_fob['fuentes']),
        },
        'farac-carretero': {
            'ente': 'Fideicomiso de Apoyo para el Rescate de Autopistas Concesionadas (FARAC), hoy Fondo Nacional de Infraestructura (FONADIN) en BANOBRAS',
            'quien': 'El Gobierno Federal constituyó el FARAC en agosto de 1997 en BANOBRAS para rescatar 23 autopistas y puentes privados; en 2008 sus activos y pasivos pasaron al FONADIN; la Auditoría Superior de la Federación fiscalizó el rescate en las Cuentas Públicas 2015 y 2017 y Hacienda reporta el saldo del pasivo en los Requerimientos Financieros del Sector Público.',
            'que': (
                'Al igual que el FOBAPROA, el rescate carretero de 1997 es un rescate financiero y se presenta separado de las 11 obras '
                'físicas. En agosto de 1997 el Gobierno Federal rescató 23 autopistas y puentes concesionados y asumió $57,756.6 millones de '
                'pesos en indemnizaciones ($30,265.4 millones de deuda bancaria subrogada y $27,491.2 millones en Pagarés de Indemnización '
                'Carretera). Aunque el fondo cobró peajes y recibió $187,891.5 millones por re-concesionar autopistas entre 2007 y 2016, '
                'los intereses y gastos financieros superaron sus ingresos y de 1997 a 2017 acumuló pérdidas netas por $96,094.9 millones: '
                'el costo documentado hasta 2017 asciende al menos a $153,851.5 millones (+166.4 %). Al cierre de 2017 su deuda bursátil neta '
                'era de $225,500.2 millones (con $351,969.6 millones por pagar entre 2018 y 2033 según la ASF) y al cierre de 2025 Hacienda '
                'reporta todavía un saldo de pasivos del FARAC/FONADIN de $153,035.5 millones.'
            ),
            'falta': (
                'El último estado de resultados anual desglosado en informes públicos de la ASF es el de 2017 (déficit de -$10,564.3 millones): '
                'Banobras y Hacienda no publican en formato abierto la serie anual de ingresos por peaje, intereses pagados y pérdida o '
                'superávit del FONADIN de 2018 a 2025.'
            ),
            'pendiente_id': None,
            'caja': '23 autopistas rescatadas (1997)',
            'cont': [
                {'ico': '🛣️', 'tit': 'Indemnizaciones de 1997', 'v': round(o_far['inversion_presupuestada_mdp'], 1), 'f': 'mdp1', 'etq': '23 autopistas y puentes: $30,265.4 mdp de deuda bancaria + $27,491.2 mdp en pagarés PIC', 'est': 'oficial'},
                {'ico': '📉', 'tit': 'Pérdida acumulada (1997–2017)', 'v': 96094.9, 'f': 'mdp1', 'etq': 'veinte años en que los intereses superaron los ingresos del fondo · ASF CP 2017, aud. 91-GB', 'est': 'derivado'},
                {'ico': '💰', 'tit': 'Costo documentado a 2017', 'v': round(o_far['inversion_real_mdp'], 1), 'f': 'mdp1', 'etq': 'cota mínima (indemnizaciones + pérdida acumulada, +166.4 % frente a 1997)', 'est': 'derivado'},
                {'ico': '🏦', 'tit': 'Pasivo vivo al cierre 2025', 'v': 153035.5, 'f': 'mdp1', 'etq': 'saldo de pasivos del FARAC/FONADIN en el SHRFSP al 4T 2025 (SHCP)', 'est': 'oficial'},
                {'ico': '🔴', 'tit': 'Déficit anual (corte 2017)', 'v': abs(round(o_far['res']['v'], 1)), 'f': 'mdp1', 'etq': '$16,650.0 millones de gastos frente a $6,085.6 millones de ingresos en 2017 (ASF)', 'est': 'oficial'},
            ],
            'rastroTit': 'El rastro financiero del rescate carretero FARAC/FONADIN en la ASF y Hacienda (1997–2025)',
            'rastroEst': 'oficial',
            'rastro': [
                {'k': 'Capital e intereses por pagar de la deuda bursátil entre 2018 y 2033', 'sub': '$185,436.3 millones de capital + $166,533.3 millones de intereses proyectados · ASF CP 2017, aud. 96', 'v': 351969.6, 'url': fmap['asf_farac17']['url'], 'est': 'oficial'},
                {'k': 'Deuda bursátil neta del rescate al 31 de diciembre de 2017', 'sub': '3.9 veces las indemnizaciones asumidas veinte años antes · ASF CP 2017, aud. 96', 'v': 225500.2, 'url': fmap['asf_farac17']['url'], 'est': 'oficial'},
                {'k': 'Ingresos recibidos por re-concesionar autopistas a privados (2007–2016)', 'sub': 'No alcanzaron para extinguir el pasivo por el peso de los intereses · ASF CP 2017, aud. 91-GB', 'v': 187891.5, 'url': 'https://www.asf.gob.mx/Trans/Informes/IR2017c/Documentos/Auditorias/2017_0091_a.pdf', 'est': 'oficial'},
                {'k': 'Saldo de pasivos del FARAC/FONADIN en el SHRFSP al cierre de 2025', 'sub': '0.4 % del PIB reportado por la SHCP en los Informes sobre la Situación Económica 4T 2025', 'v': 153035.5, 'url': 'https://www.finanzaspublicas.hacienda.gob.mx/work/models/Finanzas_Publicas/docs/congreso/infotrim/2025/ivt/05adp/itandpdc_202504.pdf', 'est': 'oficial'},
                {'k': 'Pérdida neta acumulada del fideicomiso de 1997 a 2017', 'sub': '$37,260.4 millones (1997–2007) + $58,834.5 millones (2008–2017) · ASF CP 2017, aud. 91-GB', 'v': 96094.9, 'url': 'https://www.asf.gob.mx/Trans/Informes/IR2017c/Documentos/Auditorias/2017_0091_a.pdf', 'est': 'derivado'},
                {'k': 'Indemnizaciones asumidas en agosto de 1997 por 23 autopistas y puentes', 'sub': 'Deuda bancaria subrogada ($30,265.4 mdp) y pagarés PIC ($27,491.2 mdp) · ASF CP 2015, aud. 99', 'v': 57756.6, 'url': 'https://www.asf.gob.mx/Trans/Informes/IR2015i/Documentos/Auditorias/2015_0099_a.pdf', 'est': 'oficial'},
            ],
            'fuentes': fdoc(v_far['fuentes'], [
                {'doc': 'ASF, Cuenta Pública 2017, auditoría 91-GB: Análisis del Otorgamiento y Rescate de las Concesiones Carreteras (FARAC-FONADIN)', 'url': 'https://www.asf.gob.mx/Trans/Informes/IR2017c/Documentos/Auditorias/2017_0091_a.pdf'},
                {'doc': 'ASF, Cuenta Pública 2015, auditoría 99: Fondo Nacional de Infraestructura (FONADIN)', 'url': 'https://www.asf.gob.mx/Trans/Informes/IR2015i/Documentos/Auditorias/2015_0099_a.pdf'},
                {'doc': 'SHCP: Informes sobre la Situación Económica, las Finanzas Públicas y la Deuda Pública al 4T 2025', 'url': 'https://www.finanzaspublicas.hacienda.gob.mx/work/models/Finanzas_Publicas/docs/congreso/infotrim/2025/ivt/05adp/itandpdc_202504.pdf'},
            ]),
        },
    }


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

    sm = d['simulador_megaobras']
    obras_mo = mo_sector.obras_oficiales(d)
    solo_obras = [o for o in obras_mo if o.get('tipo') != 'rescate']
    rescates = [o for o in obras_mo if o.get('tipo') == 'rescate']
    bal = mo_base.balance(sm)
    _sm, _sec, _res, grupos_sx, _todos = mo_tabla._datos(d)
    obras_presu = round(sum(o['inversion_presupuestada_mdp'] for o in solo_obras), 1)
    obras_real = round(sum(o['inversion_real_mdp'] for o in solo_obras), 1)
    obras_sob = round((obras_real - obras_presu) / obras_presu * 100, 1)
    resc_presu = round(sum(o['inversion_presupuestada_mdp'] for o in rescates), 1)
    resc_real = round(sum(o['inversion_real_mdp'] for o in rescates), 1)
    aud_propia = {
        o['id']: ('auditoria-aifa.html' if o['id'] == 'aifa-texcoco' else 'auditoria-' + o['id'] + '.html')
        for o in obras_mo
    }

    res = {
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
        'inversion-megaobras': {
            'ente': 'Secretaría de la Defensa Nacional, Pemex, SICT, Salud, SEP, SSPC, IPAB y BANOBRAS (1988–2024)',
            'quien': 'Las dependencias y empresas públicas ejecutan y operan las obras (Defensa, Pemex, SICT, Birmex, SEP, SSPC, IPAB y BANOBRAS); la Secretaría de Hacienda reporta la Cuenta Pública y la Cartera de Inversión; la Auditoría Superior de la Federación fiscaliza los contratos y estados financieros.',
            'que': (
                'El registro de Inversión y Megaobras sigue 13 proyectos de seis sexenios (1988–2024), separados por método en 11 obras '
                'físicas o de equipamiento y 2 rescates financieros (FOBAPROA-IPAB y FARAC carretero). Las 11 obras pasaron de '
                '$529,936.6 millones de pesos presupuestados a $1,176,646.8 millones de costo real documentado (+122.0 % de sobrecosto, '
                '$646,710.2 millones por encima de lo aprobado). Los 2 rescates suman aparte $1,888,345.8 millones frente a los '
                '$610,056.6 millones reconocidos al inicio. En operación anual, de los 13 proyectos solo 6 publican su resultado financiero '
                '(5 pierden $78,171.3 millones y 1 gana $290.2 millones, con una pérdida neta anual documentada de $77,881.1 millones), '
                '4 no publican estados financieros individualizados y 3 no operan como empresa.'
            ),
            'falta': (
                'Cuatro obras en operación o en proceso (Megafarmacia de Huehuetoca, Tren Interurbano México-Toluca, Agronitrogenados y el '
                'Búnker de Seguridad) no publican estados financieros dictaminados individualizados que permitan conocer cuánto cuesta '
                'operarlas al año ni cuánto ingresan: quedan en el Registro de pendientes (ficha reloj-megaobras).'
            ),
            'pendiente_id': 'reloj-megaobras',
            'cifras': {
                'obras_n': len(solo_obras),
                'rescates_n': len(rescates),
                'obras_presu_mdp': obras_presu,
                'obras_real_mdp': obras_real,
                'obras_brecha_mdp': round(obras_real - obras_presu, 1),
                'obras_sobrecosto_pct': obras_sob,
                'rescates_presu_mdp': resc_presu,
                'rescates_real_mdp': resc_real,
                'total_con_rescates_mdp': round(obras_real + resc_real, 1),
                'balance_neto_anual_mdp': round(abs(bal['neto']), 1),
                'balance_pierde_mdp': round(abs(bal['pierde']), 1),
                'balance_gana_mdp': round(bal['gana'], 1),
                'n_con_dato_anual': bal['n_dato'],
                'n_pendiente_anual': bal['n_pend'],
                'n_no_aplica_anual': bal['n_na'],
            },
            'obras': [
                {
                    'id': o['id'],
                    'nombre': o['nombre'],
                    'presidente': o['presidente'],
                    'periodo': o['periodo_sexenal'],
                    'tipo': o.get('tipo') or 'obra',
                    'presu_mdp': round(o['inversion_presupuestada_mdp'], 1),
                    'real_mdp': round(o['inversion_real_mdp'], 1),
                    'sobrecosto_pct': round(o['sobrecosto_pct'], 1),
                    'estado_real': (o.get('estado_campos') or {}).get('inversion_real_mdp') or 'derivado',
                    'res_tipo': o['res']['tipo'],
                    'res_mdp': round(o['res']['v'], 1) if o['res']['tipo'] == 'dato' else None,
                    'ficha_href': 'herramienta-megaobras-sector.html#obra-' + o['id'],
                    'cuenta_href': 'herramienta-megaobras-pulso-cuenta.html#cuenta-' + o['id'],
                    'auditoria_href': aud_propia.get(o['id']),
                }
                for o in obras_mo
            ],
            'sexenios': [
                {
                    'clave': g['clave'],
                    'nombre': g['nombre'],
                    'obras_n': len(g['obras']),
                    'rescates_n': g['rescates'],
                    'costo_mdp': round(g['costo'], 1),
                    'res_mdp': round(g['res'], 1),
                    'href': 'herramienta-megaobras-tabla.html#mt-sx-' + g['clave'],
                }
                for g in grupos_sx
            ],
            'fuentes': [
                {
                    'doc': 'SHCP: Cuenta Pública 2024 y 2025, Tomo VII Sector Paraestatal (Tren Maya, AIFA, Pemex, Birmex)',
                    'url': 'https://www.cuentapublica.hacienda.gob.mx/',
                },
                {
                    'doc': 'Auditoría Superior de la Federación: Informes Individuales de las Cuentas Públicas 2015 a 2024 (Tren Maya, Dos Bocas, AIFA, Tren Interurbano, Birmex, Estela de Luz, Búnker, FARAC)',
                    'url': 'https://informe.asf.gob.mx/',
                },
                {
                    'doc': 'IPAB: Estados Financieros Dictaminados 2024 y 2025 y Presupuesto de Egresos Ramo 34 (FOBAPROA-IPAB)',
                    'url': 'https://www.gob.mx/ipab/documentos/estados-financieros-del-ipab',
                },
                {
                    'doc': 'SHCP, Transparencia Presupuestaria: Obra Pública Abierta y Cartera de Programas y Proyectos de Inversión',
                    'url': 'https://www.transparenciapresupuestaria.gob.mx/Obra-Publica-Abierta',
                },
            ],
        },
    }
    res.update(_obras_individuales(sm, obras_mo))
    return res


def actualizar_js():
    p = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'auditoria-imagen.js')
    raw = open(p, 'rb').read().decode('utf-8')
    nl = '\r\n'
    if 'obraMega(' in raw:
        return
    t = (
        "  var ARMA = {\n"
        "    'tren-maya': function () { return desdeExpediente('tren-maya'); },\n"
        "    'dos-bocas': function () { return desdeExpediente('dos-bocas'); },\n"
        "    'deuda-soberana': deuda,\n"
        "    'aifa': function () { return desdeExpediente('aifa'); },\n"
        "    'ramo-33': ramo33,\n"
        "    'lego-cienega': lego,\n"
        "    'tren-toluca': function () { return desdeExpediente('tren-toluca'); },\n"
        "    'megafarmacia': megafarmacia,\n"
        "    'huachicol-fiscal': huachicol,\n"
        "    'ine-contratos': ineContratos,\n"
        "    'guaymas-gas': guaymasGas,\n"
        "    'medicamentos-imss': medicamentosImss,\n"
        "    'deuda-congreso-2027': deudaCongreso2027,\n"
        "    'inversion-megaobras': inversionMegaobras\n"
        "  };"
    ).replace('\n', nl)
    r = (
        "  function obraMega(id) {\n"
        "    var A = DB.auditorias_actuales && DB.auditorias_actuales[id];\n"
        "    if (!A) return null;\n"
        "    var f = A.fuentes || [];\n"
        "    return {\n"
        "      cont: A.cont || [],\n"
        "      rastroTit: A.rastroTit,\n"
        "      rastroEst: A.rastroEst || 'oficial',\n"
        "      rastro: A.rastro || [],\n"
        "      escena: { tipo: 'reparto', tit: 'Los tramos del dinero documentados en informes oficiales', caja: A.caja || 'Evidencia oficial', unidad: 'mdp' },\n"
        "      hallazgo: A.que,\n"
        "      pendiente: A.falta,\n"
        "      pendienteId: A.pendiente_id || null,\n"
        "      fuente: f.map(function (x) { return x.doc; }).join('; ') + '.',\n"
        "      acciones: [\n"
        "        { txt: '🏗️ Ver su ficha, historia y simulador en Inversión y Megaobras', href: 'herramienta-megaobras-sector.html#obra-' + id },\n"
        "        { txt: '📊 Ver su cuenta (estado de resultados) y ritmo en vivo', href: 'herramienta-megaobras-pulso-cuenta.html#cuenta-' + id },\n"
        "        { txt: '🏛️ Ver su renglón en la tabla por presidente', href: 'herramienta-megaobras-tabla.html#mt-' + id },\n"
        "        { txt: '🖼️ Panorama de las 11 megaobras y 2 rescates', href: 'auditoria-inversion-megaobras.html' },\n"
        "        f[0] ? { txt: '📄 Abrir el documento oficial principal', url: f[0].url } : null\n"
        "      ].filter(Boolean)\n"
        "    };\n"
        "  }\n\n"
        "  var ARMA = {\n"
        "    'tren-maya': function () { return desdeExpediente('tren-maya'); },\n"
        "    'dos-bocas': function () { return desdeExpediente('dos-bocas'); },\n"
        "    'deuda-soberana': deuda,\n"
        "    'aifa': function () { return desdeExpediente('aifa'); },\n"
        "    'ramo-33': ramo33,\n"
        "    'lego-cienega': lego,\n"
        "    'tren-toluca': function () { return desdeExpediente('tren-toluca'); },\n"
        "    'megafarmacia': megafarmacia,\n"
        "    'huachicol-fiscal': huachicol,\n"
        "    'ine-contratos': ineContratos,\n"
        "    'guaymas-gas': guaymasGas,\n"
        "    'medicamentos-imss': medicamentosImss,\n"
        "    'deuda-congreso-2027': deudaCongreso2027,\n"
        "    'inversion-megaobras': inversionMegaobras,\n"
        "    'agronitrogenados': function () { return obraMega('agronitrogenados'); },\n"
        "    'fertinal': function () { return obraMega('fertinal'); },\n"
        "    'estela-luz': function () { return obraMega('estela-luz'); },\n"
        "    'bunker-garcia-luna': function () { return obraMega('bunker-garcia-luna'); },\n"
        "    'refineria-tula': function () { return obraMega('refineria-tula'); },\n"
        "    'enciclomedia': function () { return obraMega('enciclomedia'); },\n"
        "    'fobaproa': function () { return obraMega('fobaproa'); },\n"
        "    'farac-carretero': function () { return obraMega('farac-carretero'); }\n"
        "  };"
    ).replace('\n', nl)
    assert t in raw, 'ARMA block not found in auditoria-imagen.js'
    raw = raw.replace(t, r, 1)
    open(p, 'wb').write(raw.encode('utf-8'))
    print('auditoria-imagen.js actualizado con obraMega() y las 8 obras individuales')


def actualizar_index():
    p = os.path.join(RAIZ, 'index.html')
    raw = open(p, 'rb').read().decode('utf-8')
    nl = '\r\n'
    if 'auditoria-agronitrogenados.html' in raw:
        return
    nuevas_slides = [
        (
            15,
            'auditoria-agronitrogenados.html',
            'assets/auditor/img/showcase_agronitrogenados.jpg',
            'Ilustración de la planta petroquímica de fertilizantes Agronitrogenados en Pajaritos, Coatzacoalcos, con torres oxidadas y carpetas de auditoría',
            '🏭 Megaobras y compras de Pemex · De $7,894 millones autorizados a $13,698 millones ejercidos',
            '¿Cuánto costó comprar y rehabilitar las plantas de Agronitrogenados en Pajaritos y qué observó la ASF?',
        ),
        (
            16,
            'auditoria-fertinal.html',
            'assets/auditor/img/showcase_fertinal.jpg',
            'Ilustración de la mina de roca fosfórica y planta industrial de Grupo Fertinal junto al mar con documentos de deuda y pérdidas',
            '⛏️ Megaobras y compras de Pemex · $13,121.6 millones financiados y -$3,600.1 millones en 2024',
            '¿Cuánto financió Pemex para comprar Grupo Fertinal y cuánto sigue perdiendo al año su filial de fertilizantes?',
        ),
        (
            17,
            'auditoria-estela-luz.html',
            'assets/auditor/img/showcase_estela_luz.jpg',
            'Ilustración de la torre de cuarzo y acero inoxidable de la Estela de Luz en Paseo de la Reforma al atardecer',
            '🗼 Obras conmemorativas · De $393.5 millones contratados a $1,304.9 millones (+231.6 %)',
            '¿Por qué la Estela de Luz costó más del triple de su contrato original y cuántos pagos improcedentes detectó la ASF?',
        ),
        (
            18,
            'auditoria-bunker-garcia-luna.html',
            'assets/auditor/img/showcase_bunker.jpg',
            'Ilustración del edificio subterráneo de inteligencia de Plataforma México en Constituyentes con pantallas y carpetas reservadas',
            '📡 Seguridad e inteligencia · Obra civil auditada y contratos tecnológicos reservados 12 años',
            '¿Cuánto costó el edificio del Búnker de Seguridad en Constituyentes y por qué sigue pendiente el costo de sus sistemas?',
        ),
        (
            19,
            'auditoria-refineria-tula.html',
            'assets/auditor/img/showcase_refineria_tula.jpg',
            'Ilustración de la barda perimetral solitaria en el terreno semiárido de Tula, Hidalgo, donde se proyectó la Refinería Bicentenario',
            '🧱 Proyectos cancelados · $1,127.6 millones ejercidos en estudios, terreno y barda perimetral',
            '¿En qué se gastaron los $1,127.6 millones de la Refinería Bicentenario en Tula antes de cancelarse en 2014?',
        ),
        (
            20,
            'auditoria-enciclomedia.html',
            'assets/auditor/img/showcase_enciclomedia.jpg',
            'Ilustración de un salón de primaria en México con pizarrón electrónico interactivo, proyector y expedientes de auditoría',
            '💻 Equipamiento educativo · $32,315.7 millones ejercidos entre 2001 y 2011 (+51.0 %)',
            '¿Cuánto ejerció la SEP en el programa Enciclomedia a lo largo de once años y qué revisó la ASF en siete Cuentas Públicas?',
        ),
        (
            21,
            'auditoria-fobaproa.html',
            'assets/auditor/img/showcase_fobaproa.jpg',
            'Ilustración de bóvedas bancarias de los años noventa y bonos de deuda del rescate bancario FOBAPROA-IPAB',
            '🏦 Rescates financieros (1998) · $710,923 millones ya pagados y $1,023,571 millones aún en deuda',
            '¿Cuánto se ha pagado con impuestos por el rescate bancario FOBAPROA-IPAB y cuánto se sigue debiendo al cierre de 2025?',
        ),
        (
            22,
            'auditoria-farac-carretero.html',
            'assets/auditor/img/showcase_farac.jpg',
            'Ilustración de una autopista de cuota y caseta de peaje en México con carpetas del rescate carretero FARAC-FONADIN',
            '🛣️ Rescates financieros (1997) · 23 autopistas rescatadas y $153,035.5 millones de pasivo vivo en 2025',
            '¿Cuánto costó rescatar las 23 autopistas privadas del FARAC en 1997 y qué deuda sigue vigente hoy en el FONADIN?',
        ),
    ]
    bloques = []
    for num, href, img, alt, badge, preg in nuevas_slides:
        bloques.append(
            f'          <!-- Slide {num}: {href} -->\n'
            f'          <a class="showcase-slide" href="{href}" data-caso="{href}">\n'
            f'            <img src="{img}" alt="{alt}" loading="lazy">\n'
            f'            <span class="showcase-ia">Ilustración provisional</span>\n'
            f'            <div class="showcase-slide-gradient"></div>\n'
            f'            <div class="showcase-slide-content">\n'
            f'              <span class="showcase-slide-badge">{badge}</span>\n'
            f'              <h3 class="showcase-slide-q">{preg}</h3>\n'
            f'              <div class="showcase-click-cue">\n'
            f'                <span>💬 Pregúntale al Auditor</span> ➔\n'
            f'              </div>\n'
            f'            </div>\n'
            f'          </a>'
        )
    t_slide = (
        '              <h3 class="showcase-slide-q">¿Cuánto costaron las 11 megaobras y los 2 rescates de seis sexenios, cuánto pierden al año y dónde se consulta cada obra?</h3>\n'
        '              <div class="showcase-click-cue">\n'
        '                <span>💬 Pregúntale al Auditor</span> ➔\n'
        '              </div>\n'
        '            </div>\n'
        '          </a>\n'
        '        </div>\n'
        '\n'
        '        <!-- Flechas de navegación del carrusel -->'
    ).replace('\n', nl)
    r_slide = (
        '              <h3 class="showcase-slide-q">¿Cuánto costaron las 11 megaobras y los 2 rescates de seis sexenios, cuánto pierden al año y dónde se consulta cada obra?</h3>\n'
        '              <div class="showcase-click-cue">\n'
        '                <span>💬 Pregúntale al Auditor</span> ➔\n'
        '              </div>\n'
        '            </div>\n'
        '          </a>\n\n'
        + ('\n\n'.join(bloques)).replace('\n', nl)
        + '\n        </div>\n\n        <!-- Flechas de navegación del carrusel -->'.replace('\n', nl)
    )
    assert t_slide in raw, 't_slide not found in index.html'
    raw = raw.replace(t_slide, r_slide, 1)

    t_dot = '        <button type="button" class="showcase-dot" onclick="window.AuditEngine.showcaseGoTo(13)" aria-label="Ir a Inversión en megaobras y rescates"></button>'
    dots_extra = [
        (14, 'Ir a Plantas de fertilizantes Agronitrogenados'),
        (15, 'Ir a Compra de Grupo Fertinal'),
        (16, 'Ir a Estela de Luz'),
        (17, 'Ir a El Búnker de Seguridad de García Luna'),
        (18, 'Ir a Refinería Bicentenario en Tula'),
        (19, 'Ir a Programa Enciclomedia'),
        (20, 'Ir a FOBAPROA / IPAB (Rescate Bancario de 1998)'),
        (21, 'Ir a FARAC (Rescate Carretero de 1997)'),
    ]
    r_dot = t_dot + nl + nl.join(
        f'        <button type="button" class="showcase-dot" onclick="window.AuditEngine.showcaseGoTo({idx})" aria-label="{lbl}"></button>'
        for idx, lbl in dots_extra
    )
    assert t_dot in raw, 't_dot not found in index.html'
    raw = raw.replace(t_dot, r_dot, 1)

    open(p, 'wb').write(raw.encode('utf-8'))
    b_raw = open(p, 'rb').read()
    print('index.html actualizado con slides 15..22 (lone CRs: %d)' % (b_raw.count(b'\r') - b_raw.count(b'\r\n')))


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
    actualizar_js()
    actualizar_index()


if __name__ == '__main__':
    main()
