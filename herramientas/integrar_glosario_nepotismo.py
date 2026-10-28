#!/usr/bin/env python3
"""Agrega al glosario los términos del nepotismo y del parentesco, para la
página «Nepotismo y cargos públicos» (pedido del autor, 28-10-2026: «investigar
los cargos públicos... si hay manera de encontrar una relación... de
consanguinidad o afinidad, para poderlos nosotros también auditar»).

Uso:
    python3 herramientas/integrar_glosario_nepotismo.py

Cada definición sale de su ley, citada en «ley» (textos vigentes de la Cámara
de Diputados): LGRA (última reforma DOF 15-12-2025), Código Civil Federal
(última reforma DOF 14-11-2025), Código Penal Federal (última reforma DOF
13-03-2026) y Constitución (decreto DOF 01-04-2025). Usa las mismas funciones
de integrar_glosario_fiscalizacion.py: es idempotente y no duplica términos.
"""
import integrar_glosario_fiscalizacion as g

g.TERMINOS = [
    {'termino': 'Nepotismo',
     'definicion': 'La falta administrativa grave del servidor público que, valiéndose de su cargo, nombra, designa o interviene para que '
                   'se contrate en el ente público donde trabaja a su cónyuge, a su concubina o concubino, o a un pariente: por consanguinidad '
                   'hasta el cuarto grado (de padres e hijos a primos hermanos) o por afinidad hasta el segundo (suegros y cuñados). Vale '
                   'para personal de confianza, de estructura, de base o por honorarios. La sanción la impone el tribunal de justicia '
                   'administrativa: suspensión, destitución, multa o inhabilitación.',
     'ley': 'Art. 63 Bis Ley General de Responsabilidades Administrativas (adicionado DOF 19-11-2019) · Art. 78 LGRA (sanciones)'},
    {'termino': 'Nepotismo electoral',
     'definicion': 'La prohibición de que el cónyuge, la pareja o un pariente de quien ocupa un cargo de elección compita por ese mismo '
                   'cargo en la elección siguiente: Presidencia, gubernatura, diputación federal o local y ayuntamiento. Alcanza a quien tuvo '
                   'el vínculo en los tres años anteriores a la elección, a los parientes en línea recta sin límite de grado, a los '
                   'colaterales hasta el cuarto grado y a los afines hasta el segundo. Se aplica a partir de las elecciones de 2030.',
     'ley': 'Arts. 55 fr. VIII, 82 fr. VIII, 115 fr. I, 116 fr. I inciso c) y fr. II Constitución, y transitorio segundo del decreto DOF 01-04-2025'},
    {'termino': 'Parentesco por consanguinidad',
     'definicion': 'El que existe entre personas que descienden de un mismo progenitor: padres e hijos, abuelos y nietos, hermanos, tíos y '
                   'sobrinos, primos. La adopción plena se equipara a él. Cada generación es un grado: en línea recta se cuentan las '
                   'generaciones entre las dos personas, y entre colaterales se sube hasta el tronco común y se baja por la otra línea, '
                   'sin contar al tronco (hermanos, segundo grado; tíos, tercero; primos hermanos, cuarto).',
     'ley': 'Arts. 292, 293, 296, 297, 299 y 300 Código Civil Federal'},
    {'termino': 'Parentesco por afinidad',
     'definicion': 'El que nace del matrimonio entre cada cónyuge y los parientes del otro: los suegros, el yerno o la nuera, los hijastros y '
                   'los cuñados. No une a los parientes de un cónyuge con los del otro: entre concuños y entre consuegros no hay parentesco. '
                   'El Código no dice cómo contar su grado; se cuenta, por costumbre, como el parentesco del cónyuge con esa persona '
                   '(suegros, primero; cuñados, segundo).',
     'ley': 'Arts. 292 y 294 Código Civil Federal'},
    {'termino': 'Ejercicio Abusivo de Funciones',
     'definicion': 'El delito del servidor público que otorga ilícitamente contratos, concesiones, permisos o compras que benefician '
                   'económicamente a él, a su cónyuge, a sus ascendientes o descendientes, a sus parientes por consanguinidad o afinidad '
                   'hasta el cuarto grado, a un tercero con quien tenga vínculos afectivos, económicos o de dependencia, o a sus socios y '
                   'sociedades. Lo persigue la fiscalía y lo juzga un juez penal.',
     'ley': 'Art. 220 Código Penal Federal (fracción reformada DOF 18-07-2016)'},
]
g.CORRECCIONES_GLOSARIO = []
g.REF_NUEVAS = []
g.CORRECCIONES_REF = []

if __name__ == '__main__':
    g.main()
