#!/usr/bin/env python3
"""Agrega al glosario «Concesión», para «Grupos y filiales» de Contratos
públicos (pedido del autor, 17-11-2026: que el chat conteste si una empresa
es concesionaria de un gobierno).

Uso:
    python3 herramientas/integrar_glosario_concesion.py

La definición sale de su ley, citada en «ley» (textos vigentes de la Cámara
de Diputados): Ley de Caminos, Puentes y Autotransporte Federal (última
reforma DOF 14-11-2025) y Ley General de Bienes Nacionales. Usa las mismas
funciones de integrar_glosario_fiscalizacion.py: es idempotente.
"""
import integrar_glosario_fiscalizacion as g

g.TERMINOS = [
    {'termino': 'Concesión',
     'definicion': 'El acto por el que un gobierno da a una empresa, por un plazo, el derecho de construir, operar y explotar un bien o un '
                   'servicio público, como una autopista de cuota. No es un contrato de obra: en el contrato el gobierno paga a la empresa; '
                   'en la concesión la empresa invierte y cobra a quien usa la obra. Por eso una concesión no aparece en ComprasMX: se '
                   'acredita con su título de concesión. La de caminos y puentes federales dura hasta 30 años; la de inmuebles federales, '
                   'hasta 50. No da la propiedad del bien: solo el derecho de usarlo o explotarlo en los términos del título. A quien la '
                   'recibe se le llama concesionaria.',
     'ley': 'Art. 6o. Ley de Caminos, Puentes y Autotransporte Federal · Arts. 16 y 73 Ley General de Bienes Nacionales'},
]
g.CORRECCIONES_GLOSARIO = []
g.REF_NUEVAS = []
g.CORRECCIONES_REF = []

if __name__ == '__main__':
    g.main()
