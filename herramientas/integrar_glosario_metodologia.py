#!/usr/bin/env python3
"""Agrega al glosario y a las Referencias el vocabulario de «Cómo se audita»
(aprende-auditoria.html, metodologia_auditoria.py), pedido del autor del
02-11-2026.

Uso:
    python3 herramientas/integrar_glosario_metodologia.py

Cada definición sale de su fuente oficial, citada en «ley»; los temarios de
los diplomados que subió el autor solo sirvieron de guía de temas:
- ASF, Marco Integrado de Control Interno para el Sector Público (SNF).
- LFPIORPI, última reforma DOF 16-07-2025, arts. 17 y 18.
- CNPP, última reforma DOF 28-11-2025, arts. 227, 368 y 369.

Usa las mismas funciones de integrar_glosario_fiscalizacion.py: es
idempotente y no duplica términos ni fichas.
"""
import integrar_glosario_fiscalizacion as g

MICI = 'ASF, Marco Integrado de Control Interno para el Sector Público (Sistema Nacional de Fiscalización)'
LFPIORPI = 'Ley Federal para la Prevención e Identificación de Operaciones con Recursos de Procedencia Ilícita (última reforma DOF 16-07-2025)'
CNPP = 'Código Nacional de Procedimientos Penales (última reforma DOF 28-11-2025)'

g.TERMINOS = [
    {'termino': 'Control Interno',
     'definicion': 'Proceso que hacen el órgano de gobierno, el titular y todo el personal de una institución para dar una seguridad razonable (alta, no absoluta) '
                   'de que se cumplen sus objetivos, se cuidan los recursos públicos y se previene la corrupción. En el sector público mexicano se arma con 5 componentes '
                   '(ambiente de control, administración de riesgos, actividades de control, información y comunicación, y supervisión) y 17 principios, con base en COSO 2013.',
     'ley': MICI + ', pp. 7, 8, 10 y 11'},
    {'termino': 'Riesgo Inherente y Riesgo Residual',
     'definicion': 'El riesgo inherente es el que enfrenta una institución si no hace nada para responderle; el residual, el que queda después de que responde con sus '
                   'controles. Auditar por riesgos es empezar por donde más puede salir mal. A los riesgos de corrupción no se les aplica tolerancia: en cumplimiento, la tolerancia es cero.',
     'ley': MICI + ', numeral 7.03 (p. 32) y principio 8 (p. 35)'},
    {'termino': 'Factores de Riesgo de Fraude (Triángulo del Fraude)',
     'definicion': 'Las tres condiciones que suelen estar presentes cuando hay corrupción o fraude: un incentivo o presión (el motivo), una oportunidad (controles que faltan '
                   'o que alguien puede saltarse) y una actitud o racionalización (justificarse). No prueban que haya un acto corrupto; el riesgo es mayor con los tres, pero basta uno.',
     'ley': MICI + ', numerales 8.04 y 8.05 (p. 34)'},
    {'termino': 'Segregación de Funciones',
     'definicion': 'Control básico que divide la autoridad, la custodia y la contabilidad entre personas distintas, para que nadie pueda autorizar, guardar y registrar '
                   'la misma operación. Ayuda a prevenir la corrupción, el fraude y el desperdicio.',
     'ley': MICI + ', principio 3 (p. 26)'},
    {'termino': 'Actividad Vulnerable',
     'definicion': 'Negocio que la ley antilavado obliga a identificar a sus clientes y, desde cierto monto en veces la UMA diaria, a dar aviso a Hacienda: juegos y sorteos, '
                   'inmuebles, joyas y metales preciosos, arte, vehículos, blindaje, servicios profesionales, notarios y corredores, activos virtuales y los donativos que reciben '
                   'las asociaciones sin fines de lucro, entre otras (16 fracciones). Un aviso es un reporte obligatorio, no una acusación.',
     'ley': 'Arts. 17, frs. I a XVI, y 18 · ' + LFPIORPI},
    {'termino': 'Beneficiario Controlador',
     'definicion': 'La persona que de verdad controla o se beneficia de una empresa, un fideicomiso u otra figura, aunque no aparezca como dueña en los papeles. Quien realiza '
                   'una actividad vulnerable debe identificarlo con documentos oficiales.',
     'ley': 'Art. 18, fr. III · ' + LFPIORPI},
    {'termino': 'Cadena de Custodia',
     'definicion': 'Sistema de control y registro de cada evidencia desde que se encuentra hasta que la autoridad ordena cerrarla: su identidad, estado original, cómo se '
                   'recolectó, guardó y trasladó, dónde y cuándo estuvo, y quién la tocó. Si la evidencia se altera no pierde por eso su valor, salvo que ya no sirva para acreditar el hecho.',
     'ley': 'Arts. 227 y 228 · ' + CNPP},
    {'termino': 'Prueba Pericial',
     'definicion': 'La que se ofrece cuando hace falta un conocimiento especial (contabilidad, ingeniería, informática) para examinar hechos, objetos o personas. El perito debe '
                   'tener título oficial en la materia si esa profesión está reglamentada. El dictamen cívico de esta plataforma no es un peritaje.',
     'ley': 'Arts. 368 y 369 · ' + CNPP},
]
g.CORRECCIONES_GLOSARIO = []
g.REF_NUEVAS = [
    {'num': 157, 'id': 'ref-asf-mici', 'categoria': 'fiscalizacion_auditoria', 'categoria_nombre': 'Fiscalización Superior y Auditoría',
     'cita_apa': 'Auditoría Superior de la Federación. Marco Integrado de Control Interno para el Sector Público. Sistema Nacional de Fiscalización. ASF.',
     'url': 'https://www.asf.gob.mx/uploads/176_Marco_Integrado_de_Control/Marco_Integrado_de_Cont_Int_leyen.pdf',
     'descripcion': 'El modelo de control interno para los tres órdenes de gobierno y los tres Poderes: 5 componentes, 17 principios, riesgo inherente y residual, '
                    'factores de riesgo de fraude y segregación de funciones. Se basa en COSO 2013 y en el «Green Book» de la GAO. Lo explica la página Cómo se audita de Aprende.'},
    {'num': 158, 'id': 'ref-lfpiorpi', 'categoria': 'fiscalizacion_auditoria', 'categoria_nombre': 'Fiscalización Superior y Auditoría',
     'cita_apa': 'Ley Federal para la Prevención e Identificación de Operaciones con Recursos de Procedencia Ilícita [LFPIORPI]. Diario Oficial de la Federación, '
                 '17 de octubre de 2012; última reforma, 16 de julio de 2025 (México). Cámara de Diputados.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPIORPI.pdf',
     'descripcion': 'La ley antilavado: actividades vulnerables (art. 17), identificación del cliente y del beneficiario controlador (art. 18) y avisos a Hacienda. '
                    'Lo explica la página Cómo se audita de Aprende.'},
    {'num': 159, 'id': 'ref-cnpp', 'categoria': 'fiscalizacion_auditoria', 'categoria_nombre': 'Fiscalización Superior y Auditoría',
     'cita_apa': 'Código Nacional de Procedimientos Penales [CNPP]. Diario Oficial de la Federación, 5 de marzo de 2014; última reforma, 28 de noviembre de 2025 (México). Cámara de Diputados.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CNPP.pdf',
     'descripcion': 'Cadena de custodia (arts. 227 y 228) y prueba pericial (arts. 368 y 369): lo que hace que una evidencia aguante un juicio penal. '
                    'Lo explica la página Cómo se audita de Aprende.'},
]
g.CORRECCIONES_REF = []

if __name__ == '__main__':
    g.main()
