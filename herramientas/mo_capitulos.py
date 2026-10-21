# -*- coding: utf-8 -*-
"""Inversion y Megaobras en capitulos (pedido del autor, 21-10-2026).

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

# (clave, pregunta, frase)
BLOQUES = [
    ('que', '¿En qué invirtió cada presidente?',
     'Los seis sexenios de 1988 a 2024, sus obras y si cada una gana o pierde dinero hoy.'),
    ('cuanto', '¿Cuánto costó?',
     'De lo que se aprobó a lo que se pagó, obra por obra y por industria, con las cuentas a la vista.'),
    ('gana', '¿Gana o pierde?',
     'Lo que cada obra ingresa, lo que gasta y lo que nos cuesta cada año, al ritmo que elijas.'),
    ('como', '¿Cómo se sabe?',
     'Las reglas de cada suma y los documentos oficiales de donde sale cada cifra.'),
]

# (bloque, archivo, icono, nombre corto, descripcion, clave de la cifra)
# La cifra la llena apartados con los datos (mo_tabla.cifras()).
CAPITULOS = [
    ('que', 'herramienta-megaobras-sexenios.html', '🏛️', 'Los seis sexenios',
     'La línea del tiempo de 1988 a 2024: qué obras le tocan a cada presidente, cuánto costaron y dos sexenios frente a frente.',
     'sexenios'),
    ('que', 'herramienta-megaobras-tabla.html', '🚦', 'La tabla general en vivo',
     'Todas las obras por sexenio en una sola tabla: en qué se invirtió, cuánto costó y si hoy gana (verde) o pierde (rojo), con su contador.',
     'tabla'),
    ('cuanto', 'herramienta-megaobras-cero.html', '🧮', 'De cero al resultado',
     'Las tres mesas de cálculo, renglón por renglón: de lo aprobado a lo pagado, la pérdida de un año y lo que te toca a ti.',
     'cero'),
    ('cuanto', 'herramienta-megaobras-pulso-cifras.html', '🧭', 'Las cuatro cifras y los rescates',
     'Costo real, pérdida anual, sobrecosto y pesos de más del conjunto, y aparte los dos rescates, que son deudas y no obras.',
     'cifras'),
    ('cuanto', 'herramienta-megaobras-sector.html', '🏭', 'Obra por obra, por industria',
     'Filtra por industria y por presidente: la comparativa, la ficha viva de cada obra y contra qué se compara ese dinero.',
     'sector'),
    ('cuanto', 'herramienta-megaobras-pulso-composicion.html', '🧩', 'De qué está hecho el total',
     'Cuánto del costo tiene documento oficial y cuánto es cálculo, con las obras en el orden que elijas y su descarga.',
     'composicion'),
    ('gana', 'herramienta-megaobras-pulso-cuenta.html', '📒', 'La cuenta de cada obra',
     'Lo que se esperaba de cada obra y lo que dio: ingresos, gasto de operación, intereses y ganancia o pérdida del año.',
     'cuenta'),
    ('gana', 'herramienta-megaobras-pulso-ritmo.html', '⏱️', 'El ritmo de la pérdida',
     'La pérdida y el apoyo de un año, por día, mes, trimestre, semestre o año, componente por componente.',
     'ritmo'),
    ('como', 'herramienta-megaobras-pulso-calculo.html', '🔎', 'Cómo se calcula',
     'Las reglas de cada suma, división y cadencia, qué cifras tienen documento y las fuentes oficiales.',
     'calculo'),
]


def numero(archivo):
    """Numero de capitulo (1..N) de una pagina, o None."""
    for k, c in enumerate(CAPITULOS, 1):
        if c[1] == archivo:
            return k
    return None


def kicker(archivo):
    return '%s · capítulo %d de %d' % (TITULO, numero(archivo), len(CAPITULOS))


def vecinos(archivo):
    """(anterior, siguiente, total) para el pie, cada vecino (archivo, nombre)."""
    k = numero(archivo) - 1
    ant = CAPITULOS[k - 1] if k > 0 else None
    sig = CAPITULOS[k + 1] if k + 1 < len(CAPITULOS) else None
    return ((ant[1], ant[2] + ' ' + ant[3]) if ant else None,
            (sig[1], sig[2] + ' ' + sig[3]) if sig else None, len(CAPITULOS))


FRASE = {'que': '¿En qué invirtió?', 'cuanto': '¿Cuánto costó?', 'gana': '¿Gana o pierde?', 'como': '¿Cómo se sabe?'}


def temas():
    """Los capitulos como temas de apartados.HERRAMIENTAS: (clave, icono,
    nombre, frase, descripcion). Las paginas que arma un modulo nativo van
    por su clave (sexenios, tabla, cero, sector); las partes del pulso, por
    su archivo, porque las genera la subpagina del pulso."""
    out = []
    for b, archivo, ico, corto, desc, _ck in CAPITULOS:
        clave = archivo if archivo.startswith('herramienta-megaobras-pulso-') else archivo[len('herramienta-megaobras-'):-5]
        out.append((clave, ico, corto, FRASE[b], desc))
    return out
