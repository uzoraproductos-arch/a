#!/usr/bin/env python3
"""Agrega al glosario y a las Referencias el vocabulario de «Documentar para
sancionar», el informe especial de la ASF (pedido del autor, 27-10-2026).

Uso:
    python3 herramientas/integrar_glosario_sancion.py

Cada definición sale de su fuente, citada en «ley»:
- Ley General de Responsabilidades Administrativas, última reforma DOF
  15-12-2025, art. 3, frs. II a IV.
- ASF, «Documentar para sancionar», julio de 2026, pp. 13 a 16.

Usa las mismas funciones de integrar_glosario_fiscalizacion.py: es
idempotente y no duplica términos ni fichas.
"""
import integrar_glosario_fiscalizacion as g

LGRA3 = 'Art. 3, frs. II a IV, Ley General de Responsabilidades Administrativas (última reforma DOF 15-12-2025)'
DOC = 'ASF, «Documentar para sancionar», julio de 2026'

g.TERMINOS = [
    {'termino': 'Autoridad investigadora',
     'definicion': 'La que investiga una posible falta administrativa: en la Secretaría Anticorrupción, en un órgano interno de control, en la ASF o en los fiscalizadores '
                   'de los estados. Recibe el expediente de la auditoría y, si encuentra mérito, redacta el Informe de Presunta Responsabilidad Administrativa.',
     'ley': LGRA3 + ' · ' + DOC + ', pp. 65 y 66'},
    {'termino': 'Autoridad substanciadora',
     'definicion': 'La que conduce el procedimiento de responsabilidad desde que admite el Informe de Presunta Responsabilidad Administrativa hasta que termina la '
                   'audiencia inicial, donde el presunto responsable declara y ofrece sus pruebas. Nunca puede ser la misma que investigó.',
     'ley': LGRA3 + ' · ' + DOC + ', p. 66'},
    {'termino': 'Autoridad resolutora',
     'definicion': 'La que decide si hay responsabilidad y qué sanción corresponde. En las faltas no graves es la unidad de responsabilidades del órgano interno de '
                   'control; en las graves y en las de particulares, el tribunal competente (en lo federal, el Tribunal Federal de Justicia Administrativa).',
     'ley': LGRA3 + ' · ' + DOC + ', p. 67'},
    {'termino': 'Elementos de la irregularidad (personal, conductual, circunstancial y finalidad)',
     'definicion': 'Lo que, según la ASF, debe probar todo expediente para que una irregularidad termine en sanción: quién fue (personal), qué norma o contrato violó '
                   '(conductual), cuándo, dónde y cómo ocurrió (circunstancial) y a dónde fue el dinero y cuánto se afectó (finalidad). Si falta uno, el caso se '
                   'puede caer aunque la irregularidad sea cierta.',
     'ley': DOC + ', pp. 13 a 16'},
]
g.CORRECCIONES_GLOSARIO = []
g.REF_NUEVAS = [
    {'num': 154, 'id': 'ref-asf-documentar', 'categoria': 'fiscalizacion_auditoria', 'categoria_nombre': 'Fiscalización Superior y Auditoría',
     'cita_apa': 'Auditoría Superior de la Federación. (2026). Documentar para sancionar: de la irregularidad a la sanción (1.ª ed.). ASF.',
     'url': 'https://www.asf.gob.mx/Trans/Informes/Ir2025a/Documentos/Informes_Especiales/Documentar.pdf',
     'descripcion': 'Informe especial de la primera entrega de la Cuenta Pública 2025. Explica la cadena de la auditoría a la sanción, los cuatro elementos que '
                    'debe probar un expediente y trae 20 matrices de documentos por tipo de irregularidad, hechas con lo observado en las Cuentas Públicas 2023 y 2024. '
                    'Lo explica la página Informe especial de Informes oficiales.'},
]
g.CORRECCIONES_REF = []

if __name__ == '__main__':
    g.main()
