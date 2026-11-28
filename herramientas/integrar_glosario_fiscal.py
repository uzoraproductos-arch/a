#!/usr/bin/env python3
"""Agrega al glosario los términos del SAT de la base fiscal 2026-2027 (Ola 2,
Ronda 39): buzón tributario, constancia de situación fiscal, opinión de
cumplimiento, discrepancia fiscal, deducción ciega, IVA opcional del 7 %,
la visita del art. 49 Bis y el estímulo de regularización de 2027.

Uso:
    python3 herramientas/integrar_glosario_fiscal.py

Ninguna definición trae una cifra propia: las arma fiscal_temas.glosario()
con docs/fiscal-2027/, y su «ley» es el fundamento que ahí está citado. Si la
base cambia, se vuelve a correr: quita sus términos y los vuelve a poner con lo
que hoy dice la base (fiscal_temas.py --prueba avisa si quedaron viejos). Usa
las funciones de integrar_glosario_fiscalizacion.py.
"""
import re

import integrar_glosario_fiscalizacion as g
import fiscal_temas

g.FIS = '💰 Hacendario & Deuda'
g.TERMINOS = fiscal_temas.glosario()
g.CORRECCIONES_GLOSARIO = []
g.REF_NUEVAS = []
g.CORRECCIONES_REF = []



def main():
    b = g.BASE.read_bytes().decode('utf-8')
    ini = b.index('"glosario": [')
    fin = b.index('\r\n  ]', ini)
    blo = b[ini:fin]
    for t in g.TERMINOS:  # el término que ya estaba se quita, para que entre con el texto de hoy
        blo = re.sub(r',\r\n    \{\r\n      "termino": %s,\r\n.*?\r\n    \}' % re.escape(g._valor(t['termino'])), lambda m: '', blo, flags=re.S)
    g.BASE.write_bytes((b[:ini] + blo + b[fin:]).encode('utf-8'))
    g.main()


if __name__ == '__main__':
    main()
