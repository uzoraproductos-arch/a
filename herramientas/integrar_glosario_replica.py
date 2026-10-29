#!/usr/bin/env python3
"""Agrega al glosario y a las Referencias el derecho de réplica (Bloque 4 del
plan v2, 27-10-2026).

Uso:
    python3 herramientas/integrar_glosario_replica.py

La definición sale de su fuente, citada en «ley»: Ley Reglamentaria del
artículo 6o., párrafo primero, de la Constitución, en materia del Derecho de
Réplica, última reforma DOF 14-11-2025, arts. 2, 4, 6, 10 y 11.

Usa las mismas funciones de integrar_glosario_fiscalizacion.py: es
idempotente y no duplica términos ni fichas.
"""
import integrar_glosario_fiscalizacion as g

LEY = 'Arts. 2, fr. II, 4, 6, 10 y 11, Ley Reglamentaria del artículo 6o. constitucional en materia del Derecho de Réplica (última reforma DOF 14-11-2025)'

g.TERMINOS = [
    {'termino': 'Derecho de réplica',
     'definicion': 'El derecho de toda persona a que se publique su aclaración cuando un medio u otro emisor de información difunde sobre ella datos '
                   'inexactos o falsos que le causan un agravio político, económico, en su honor, vida privada o imagen. Se pide por escrito en los '
                   '15 días hábiles siguientes a la publicación; el emisor tiene 3 días hábiles para resolver y la publica gratis y sin comentarios.',
     'ley': LEY},
]
# 27-10-2026: la primera versión nombraba a Auditavisión y se quedaba con «¿qué es Auditavisión?»;
# se corrigió a mano en la base (la frase ya no está en TERMINOS).
g.CORRECCIONES_GLOSARIO = []
g.REF_NUEVAS = [
    {'num': 156, 'id': 'ref-ley-replica', 'categoria': 'constitucional', 'categoria_nombre': 'Constitución Política de los Estados Unidos Mexicanos',
     'cita_apa': 'Cámara de Diputados del H. Congreso de la Unión. (2025). Ley Reglamentaria del Artículo 6o., Párrafo Primero, de la Constitución Política '
                 'de los Estados Unidos Mexicanos, en Materia del Derecho de Réplica. Diario Oficial de la Federación, 4 de noviembre de 2015; última reforma DOF 14-11-2025.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LRArt6_MDR.pdf',
     'descripcion': 'Quién puede pedir una réplica, en qué plazos, cómo se publica y cuándo se puede negar. La SCJN invalidó porciones de los arts. 3, 10 y 19 '
                    '(DOF 24-04-2018). La aplica la página Derecho de réplica de Auditavisión.'},
]
g.CORRECCIONES_REF = []

if __name__ == '__main__':
    g.main()
