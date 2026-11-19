#!/usr/bin/env python3
"""Agrega al Diccionario y a las Referencias lo que cita el calendario de
conservación (herramienta-inspector-conservacion.html, insp_conservacion.py),
entrega 1 del servicio «Gobernanza documental y cumplimiento» (19-11-2026).

Uso:
    python3 herramientas/integrar_glosario_conservacion.py

Cada definición sale del texto vigente que bajamos de la Cámara de Diputados
(sus huellas viven en LEYES de insp_conservacion.py):
- CFF, última reforma DOF 09-04-2026, arts. 30 y 67.
- Código de Comercio, última reforma DOF 14-11-2025, arts. 38, 46 y 49.
- LFPDPPP, nueva ley DOF 20-03-2025, arts. 3, fr. III, 10 y 24.
- Ley General de Archivos, última reforma DOF 14-11-2025, art. 4, frs. XIII y XLVI.

Usa las mismas funciones de integrar_glosario_fiscalizacion.py: es
idempotente y no duplica términos ni fichas.
"""
import integrar_glosario_fiscalizacion as g

CFF = 'Código Fiscal de la Federación (última reforma DOF 09-04-2026)'
CCOM = 'Código de Comercio (última reforma DOF 14-11-2025)'
LFPDPPP = 'Ley Federal de Protección de Datos Personales en Posesión de los Particulares (DOF 20-03-2025)'
LGA = 'Ley General de Archivos (última reforma DOF 14-11-2025)'

g.FIS = '📜 Ley de Ingresos & Marco Legal'
g.TERMINOS = [
    {'termino': 'Plazo de Conservación',
     'definicion': 'El tiempo mínimo que la ley obliga a guardar un documento. Para el SAT son 5 años, contados desde que se presentó (o debió presentarse) '
                   'la declaración del ejercicio, no desde la fecha de la factura; un comerciante guarda sus libros, comprobantes y contratos 10 años; y las actas, '
                   'los movimientos de capital y las declaraciones de una sociedad se guardan mientras exista. Si te alcanzan varias leyes, manda el plazo más largo. '
                   'En los archivos públicos es la suma de la vigencia del documento y, en su caso, su plazo precautorio y de reserva, y se fija en el catálogo de disposición documental.',
     'ley': 'Art. 30 · ' + CFF + ' · Arts. 38, 46 y 49 · ' + CCOM + ' · Art. 4, frs. XIII y XLVI · ' + LGA},
    {'termino': 'Bloqueo de Datos Personales',
     'definicion': 'Lo que se hace con los datos personales cuando ya cumplieron su finalidad: se identifican y se apartan, sin usarlos para nada más, '
                   'solo por si hay que responder por cómo se trataron, hasta que prescriba esa responsabilidad; después se suprimen. Por eso guardar '
                   'de más también incumple: al vencer el plazo de conservación, primero se bloquea y luego se borra. Los datos de un impago se eliminan a los 72 meses.',
     'ley': 'Arts. 3, fr. III, 10 y 24 · ' + LFPDPPP},
    {'termino': 'Plazo para que el SAT te Revise (Caducidad)',
     'definicion': 'El SAT tiene 5 años para revisarte y determinar contribuciones omitidas. Sube a 10 años si no te inscribiste en el RFC, si no llevas '
                   'contabilidad o no la conservas el plazo de ley, o si no presentaste la declaración del ejercicio estando obligado. Por eso perder '
                   'los papeles puede doblar el tiempo en que te pueden revisar.',
     'ley': 'Art. 67 · ' + CFF},
]
g.CORRECCIONES_GLOSARIO = []
g.REF_NUEVAS = [
    {'num': 160, 'id': 'ref-ccom', 'categoria': 'leyes_federales', 'categoria_nombre': 'Leyes Hacendarias y Presupuestales',
     'cita_apa': 'Código de Comercio [CCom]. Diario Oficial de la Federación, 7 de octubre al 13 de diciembre de 1889; última reforma, 14 de noviembre de 2025 (México). Cámara de Diputados.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CCom.pdf',
     'descripcion': 'Obliga a todo comerciante, y las sociedades mercantiles lo son (art. 3o.), a guardar sus libros, registros y comprobantes (arts. 38 y 46) '
                    'y los originales de sus contratos (art. 49) por 10 años como mínimo, en papel o en medios electrónicos (art. 46 bis). Lo aplica la '
                    'aplicación «¿Hasta cuándo guardas tus papeles?» del Modo Inspector.'},
    {'num': 161, 'id': 'ref-lfpdppp', 'categoria': 'leyes_federales', 'categoria_nombre': 'Leyes Hacendarias y Presupuestales',
     'cita_apa': 'Ley Federal de Protección de Datos Personales en Posesión de los Particulares [LFPDPPP]. Diario Oficial de la Federación, 20 de marzo de 2025; '
                 'última reforma, 14 de noviembre de 2025 (México). Nueva ley que abrogó la de 2010. Cámara de Diputados.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf',
     'descripcion': 'Rige los datos personales que tienen las empresas y las personas: al cumplir su finalidad se bloquean y se suprimen (arts. 3, fr. III, 10 y 24), '
                    'y los de un impago se eliminan a los 72 meses. Es la ley de nuestro aviso de privacidad y la que pone tope a «guardarlo por si acaso».'},
    {'num': 162, 'id': 'ref-lga', 'categoria': 'leyes_federales', 'categoria_nombre': 'Leyes Hacendarias y Presupuestales',
     'cita_apa': 'Ley General de Archivos [LGA]. Diario Oficial de la Federación, 15 de junio de 2018; última reforma, 14 de noviembre de 2025 (México). Cámara de Diputados.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGA.pdf',
     'descripcion': 'Ordena los archivos de los gobiernos, los Poderes, los órganos autónomos y de quien recibe o ejerce recursos públicos: cada uno fija en su '
                    'catálogo de disposición documental cuánto se guarda cada serie y qué pasa después (art. 4, frs. XIII y XLVI).'},
]
g.CORRECCIONES_REF = []

if __name__ == '__main__':
    g.main()
