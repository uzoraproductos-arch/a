# -*- coding: utf-8 -*-
"""Inversion y Megaobras en capitulos y luego en cuatro aplicaciones (pedidos del autor, 21-10-2026).

Las cuatro aplicaciones (el pulso, sector e industria, los sexenios y de
cero al resultado) se repetian: cada una traia su propio contador, sus
cifras de conjunto, sus filtros y su «sigue con». El autor pidio fundirlas
en una sola herramienta, ordenada por lo que el lector quiere saber: en que
invirtio cada presidente, cuanto costo, si gana o pierde y como se sabe,
con una tabla general en vivo (mo_tabla.py). Las paginas y sus direcciones
se quedan; lo que cambia es el orden, la portada de la herramienta y el pie
de cada pagina, que va de capitulo en capitulo.

Aqui solo esta la lista: la usan apartados.py (portada, pie y lema),
mo_tabla.py y el rotulo de cada modulo. No importa nada para que cualquiera
la pueda importar.
"""

PORTAL = 'herramienta-megaobras.html'
TITULO = 'Inversión y Megaobras'
PALABRA = 'aplicación'

# Desde el 21-10-2026 (segundo pedido del autor, el mismo dia) los nueve
# capitulos se funden en cuatro aplicaciones, para que el lector haga su
# propia investigacion con filtros, contadores, simuladores y tablas:
#
# (Despues, el mismo dia, el cuadro de la portada se volvio la aplicacion
# 1 y estas pasaron a ser de la 2 a la 5.)
# 1. Los seis sexenios + la tabla general en vivo + el contador de la
#    portada (el «simulador inicial»): en que invirtio cada presidente,
#    cuanto costo y que se gana.
# 2. Obra por obra, por industria + de que esta hecho el total.
# 3. De cero al resultado + las cuatro cifras y los rescates.
# 4. La cuenta de cada obra + el ritmo de la perdida.
#
# «Como se calcula» deja de ser capitulo: es un boton que abre la ventana
# lateral (mo_pulso.cajon_calculo) en las cuatro aplicaciones y en la
# portada. Las paginas que se quedaron sin contenido redirigen
# (apartados.REDIRECCIONES).

# (clave, archivo, icono, nombre corto, descripcion, clave de la cifra)
# La cifra la llena apartados con los datos (mo_tabla.cifras()).
CAPITULOS = [
    # El cuadro «Haz tu propia investigacion» de la portada se volvio la
    # aplicacion 1, con pagina propia (pedido del autor, 21-10-2026):
    # herramientas/mo_investiga.py.
    ('investiga', 'herramienta-megaobras-investiga.html', '🔍', 'Haz tu propia investigación',
     'Elige un presidente y una pregunta (en qué invirtió, si gana o pierde, su estado de resultados, cuánto nos sigue costando, los rescates y la huella ambiental) y lee la respuesta con su documento.',
     'investiga'),
    ('que', 'herramienta-megaobras-tabla.html', '🏛️', 'En qué invirtió cada presidente',
     'El contador en vivo, la tabla general de los seis sexenios con cada obra en verde si gana o en rojo si pierde, la línea del tiempo de 1988 a 2024 y dos sexenios frente a frente.',
     'tabla'),
    ('obra', 'herramienta-megaobras-sector.html', '🏭', 'Obra por obra, por industria',
     'Filtra por industria y por presidente: la comparativa, la ficha viva de cada obra, contra qué se compara ese dinero y de qué está hecho el total, con su descarga.',
     'sector'),
    ('cifras', 'herramienta-megaobras-cero.html', '🧭', 'Las cuatro cifras y los rescates',
     'Costo real, pérdida del año, sobrecosto y pesos de más, los dos rescates aparte, y las tres mesas de cálculo que llegan a esas cifras desde cero.',
     'cifras'),
    ('cuenta', 'herramienta-megaobras-pulso-cuenta.html', '📒', 'La cuenta de cada obra y el ritmo de la pérdida',
     'El estado de resultados de cada obra (ingresos, gasto de operación, intereses, ganancia o pérdida) y lo que nos sigue costando por día, mes, trimestre, semestre o año.',
     'cuenta'),
]

# La ventana lateral de «Como se calcula»: con este ancla en la direccion
# se abre al cargar (apartados.js, button[data-cajon]).
CALCULO_HASH = 'como-se-calcula'


def numero(archivo):
    """Numero de aplicacion (1..N) de una pagina, o None."""
    for k, c in enumerate(CAPITULOS, 1):
        if c[1] == archivo:
            return k
    return None


def kicker(archivo):
    return '%s · %s %d de %d' % (TITULO, PALABRA, numero(archivo), len(CAPITULOS))


def vecinos(archivo):
    """(anterior, siguiente, total) para el pie, cada vecino (archivo, nombre)."""
    k = numero(archivo) - 1
    ant = CAPITULOS[k - 1] if k > 0 else None
    sig = CAPITULOS[k + 1] if k + 1 < len(CAPITULOS) else None
    return ((ant[1], ant[2] + ' ' + ant[3]) if ant else None,
            (sig[1], sig[2] + ' ' + sig[3]) if sig else None, len(CAPITULOS))


FRASE = {'investiga': 'Paso a paso', 'que': 'Cuánto costó y qué se gana', 'obra': 'Filtros y fichas', 'cifras': 'Desde cero',
         'cuenta': 'Estados de resultados'}


def temas():
    """Las aplicaciones como temas de apartados.HERRAMIENTAS: (clave, icono,
    nombre, frase, descripcion). Las paginas que arma un modulo nativo van
    por su clave (tabla, sector, cero); la cuenta, por su archivo, porque la
    genera la subpagina del pulso."""
    out = []
    for b, archivo, ico, corto, desc, _ck in CAPITULOS:
        clave = archivo if archivo.startswith('herramienta-megaobras-pulso-') else archivo[len('herramienta-megaobras-'):-5]
        out.append((clave, ico, corto, FRASE[b], desc))
    return out
