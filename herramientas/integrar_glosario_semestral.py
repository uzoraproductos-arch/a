#!/usr/bin/env python3
"""Agrega al glosario y a las Referencias el vocabulario del informe semestral
de la ASF a la Cámara de Diputados (pedido del autor, 27-10-2026).

Uso:
    python3 herramientas/integrar_glosario_semestral.py

Cada definición sale de su fuente, citada en «ley»:
- Ley de Fiscalización y Rendición de Cuentas de la Federación, última
  reforma DOF 14-05-2026, art. 38.
- ASF, informe semestral con corte al 31 de marzo de 2026, pp. 23, 30 y 35.

Usa las mismas funciones de integrar_glosario_fiscalizacion.py: es
idempotente y no duplica términos ni fichas.
"""
import integrar_glosario_fiscalizacion as g

LFRCF38 = 'Art. 38, Ley de Fiscalización y Rendición de Cuentas de la Federación (última reforma DOF 14-05-2026)'
DOC = 'ASF, Informe sobre la situación que guardan las observaciones, recomendaciones y acciones promovidas, corte al 31 de marzo de 2026'

g.TERMINOS = [
    {'termino': 'Informe semestral de la ASF',
     'definicion': 'El reporte que la Auditoría Superior de la Federación entrega a la Cámara de Diputados a más tardar el 1 de mayo y el 1 de noviembre sobre qué pasó con '
                   'sus observaciones: cuáles se aclararon, cuánto se recuperó y cómo van los procedimientos de responsabilidad y las denuncias penales. La ley pide que '
                   'diga las sanciones que procedieron y que se publique en datos abiertos.',
     'ley': LFRCF38 + ' · ' + DOC + ', p. 7 del PDF'},
    {'termino': 'No ejercicio de la acción penal (NEAP)',
     'definicion': 'Decisión del Ministerio Público de no llevar una denuncia ante un juez, por ejemplo porque no encontró delito o pruebas suficientes. Es el segundo estado '
                   'más común de las denuncias penales de la ASF: 425 de 1,196 al 31 de marzo de 2026.',
     'ley': DOC + ', p. 35'},
    {'termino': 'Fincamiento de Responsabilidad Resarcitoria',
     'definicion': 'El procedimiento con que la ASF, hasta las Cuentas Públicas de 2016, obligaba directamente a pagar el daño causado al erario. Lleva 4,787 casos y '
                   '$3,069.1 millones recuperados. Hoy los daños se persiguen también con procedimientos de la Ley General de Responsabilidades Administrativas: 2,395, de las Cuentas Públicas 2016 a 2022.',
     'ley': DOC + ', pp. 30 y 560'},
]
g.CORRECCIONES_GLOSARIO = []
g.REF_NUEVAS = [
    {'num': 155, 'id': 'ref-asf-semestral', 'categoria': 'fiscalizacion_auditoria', 'categoria_nombre': 'Fiscalización Superior y Auditoría',
     'cita_apa': 'Auditoría Superior de la Federación. (2026). Informe sobre la situación que guardan las observaciones, recomendaciones y acciones promovidas. Corte al 31 de marzo de 2026. ASF.',
     'url': 'https://www.asf.gob.mx/uploads/56_Informes_especiales_de_auditoria/IS_31_03_2026.pdf',
     'descripcion': 'Informe semestral a la Cámara de Diputados (art. 38 de la LFRCF). Trae el estado de las 37,390 acciones de las Cuentas Públicas 2019 a 2024, los 2,395 '
                    'procedimientos de responsabilidad, las 1,196 denuncias penales y las recuperaciones de 2001 a 2024. Lo explica la página Informe semestral de la ASF de '
                    'Informes oficiales.'},
]
g.CORRECCIONES_REF = []

if __name__ == '__main__':
    g.main()
