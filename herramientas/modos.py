#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A qué modo del Auditor pertenece cada página de la Enciclopedia
(pedido del autor, 29-10-2026: «que el contenido que se encuentra en la
enciclopedia quede integrado a nuestro auditor en sus correspondientes
modos»).

La Enciclopedia es la base de datos física del Auditor: cada página suya se
indexa en la base del chat (asistente.py, _paginas()) con su modo, y cada
página lleva en su cabecera «Pregúntale al Auditor · Modo X», que abre el
chat en ese modo con la pregunta ya hecha. El modo cambia la forma de
investigar, nunca los datos (AGENTS.md §2): aquí solo se decide desde qué
modo se pregunta por la página.

La regla se lee en orden: la primera que toca decide. Se mira el nombre del
archivo y las migas («Números › Presupuesto › …»). Lo que no cae en ninguna
es del modo Inspector, la investigación más completa.
"""

import re

MODOS_NOMBRE = {'inspector': 'Inspector', 'reportero': 'Reportero',
                'ciudadano': 'Ciudadano', 'ambientalista': 'Ambientalista'}
MODOS_ICONO = {'inspector': '🔍', 'reportero': '📰', 'ciudadano': '🙋', 'ambientalista': '🌎'}

REGLAS = [
    ('ambientalista', r'ambient|basura|profepa|Medio ambiente|Justicia ambiental|Costo Ambiental'),
    ('reportero', r'^noticias|^periodismo|^derecho-de-replica|^auditoria-|^pilares|Noticias'),
    ('ciudadano', r'^glosario|^diccionario|^marco-legal|^preguntas-frecuentes|^fuentes-oficiales|^aprende|^garantias|'
                  r'^estado-de-cuenta|Calculadora Cívica|Tu estado de cuenta|Baja al territorio|Biblioteca del Erario'),
]


def modo_pagina(archivo, migas=''):
    """El modo de una página: por su archivo y por sus migas."""
    for m, rx in REGLAS:
        if re.search(rx, archivo) or re.search(rx, migas):
            return m
    return 'inspector'


# Paginas de la Enciclopedia que no muestran «Enciclopedia» en sus migas
# porque cuelgan de otra pestaña, pero que las tarjetas de Aprende ofrecen.
ENCICLOPEDIA_EXTRA = {'noticias-relevantes.html', 'periodismo-en-riesgo.html', 'derecho-de-replica.html', 'pilares.html',
                      'garantias.html', 'garantias-brujula.html', 'estado-de-cuenta.html'}


# La pregunta del boton es el titulo de la pagina, salvo cuando el titulo no
# basta para que el chat la encuentre: una sola palabra que dice mucho
# («Datos») o mayusculas que el chat lee como nombre propio.
PREGUNTA = {'descarga-los-datos.html': 'Descarga los datos',
            'preguntas-frecuentes.html': 'Preguntas frecuentes'}


def enlace(archivo, migas, titulo):
    """«Pregúntale al Auditor · Modo X» para la cabecera de una pagina de la
    Enciclopedia: abre el chat en su modo con la pregunta ya hecha."""
    from urllib.parse import quote
    m = modo_pagina(archivo, migas)
    titulo = PREGUNTA.get(archivo, titulo)
    return ('<a class="apartado-auditor" href="herramienta-inspector-pregunta.html?modo=%s&amp;q=%s" data-modo="%s">'
            '<span aria-hidden="true">%s</span><span>Pregúntale al Auditor · <b>Modo %s</b></span></a>' % (m, quote(titulo), m, MODOS_ICONO[m], MODOS_NOMBRE[m]))
