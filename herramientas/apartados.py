#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera las paginas de apartado del indice de Auditavision.

Desde el 08-10-2026, seis apartados del indice (Herramientas, Busca y
verifica, Sigue el dinero (hoy «Números»), Descarga los datos, Aprende y Participa) ya no se
desglosan en un menu: cada uno abre su propia pagina, con la informacion
ordenada por secciones. Desde el 09-10-2026 «Datos de referencia» (el radar
hacendario) tambien: se fusiono con Descarga los datos en una sola pagina.

Las tarjetas de cada pagina llevan al auditor con index.html?ir=destino
(&ancla=id). El motor (audit-engine.js, funcion irDesdeApartado) solo acepta
los destinos de su lista y limpia la direccion al llegar.

Uso:
    python3 herramientas/apartados.py      # regenera las seis paginas

Toma el sello de version de index.html, asi que hay que correrlo despues de
herramientas/sello.py (sello.py ya lo llama solo). Las paginas se escriben con
saltos de linea CRLF, la convencion del proyecto. Para cambiar su contenido,
edita este archivo y vuelve a correrlo: no edites a mano los .html generados.
"""
import json
import html
import os
import re
import unicodedata
import sys

import participa_html

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%230c0e15'/%3E%3Cg stroke='%23c9a84c' stroke-width='3.2' stroke-linecap='round' fill='none'%3E%3Cpath d='M32 12v38'/%3E%3Cpath d='M20 50h24'/%3E%3Cpath d='M14 22h36'/%3E%3Cpath d='M14 22l-6 13a7 7 0 0 0 12 0z'/%3E%3Cpath d='M50 22l-6 13a7 7 0 0 0 12 0z'/%3E%3C/g%3E%3Ccircle cx='32' cy='12' r='3.4' fill='%23f3cf65'/%3E%3C/svg%3E")


# El radar hacendario, que vivia en el menu «Datos de referencia» de la
# portada, se muda a la pagina de datos (09-10-2026).
RADAR = open(os.path.join(RAIZ, 'herramientas', 'plantillas', 'radar.html'), encoding='utf-8').read().rstrip().replace('\n', '\n        ')


def ir(destino, ancla=None):
    """Direccion de una tarjeta: el auditor con su destino."""
    url = 'index.html?ir=' + destino
    if ancla:
        url += '&amp;ancla=' + ancla
    return url


# Cada tarjeta: (icono, nombre, descripcion, destino, nota de fuente o None,
# rubro de color o None). Un destino que empieza con http abre afuera.
# Las cifras son las mismas que tenia el menu, con la misma fuente.


def glosario_ancla(termino):
    """Ancla de glosario.html#...: sin acentos ni signos. Es la forma de
    ancla() en assets/auditor/js/glosario.js: si cambia una, cambia la otra."""
    t = unicodedata.normalize('NFD', termino.split(' (')[0])
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^A-Za-z0-9]+', '-', t).strip('-')


def libro_html(a):
    """Recuadro del libro como nota de referencia: el llamado [n] y la ficha
    llevan al compendio de fuentes; los conceptos, al glosario."""
    ref = a.get('libro_ref')
    if not ref:
        return ('<aside class="apartado-libro"><span class="apartado-libro-ico" aria-hidden="true">📘</span>'
                '<p>%s</p></aside>' % a['libro'])
    rid, num, cita = ref
    url = 'fuentes-oficiales.html#%s' % rid
    llamado = ('<sup class="apartado-libro-llamado"><a href="%s" title="Ver la ficha [%d] en el compendio de fuentes" '
               'aria-label="Nota de referencia %d">[%d]</a></sup>' % (url, num, num, num))
    texto = a['libro'].replace('sobre todo sus capítulos 5 y 7.', 'sobre todo sus capítulos 5 y 7.' + llamado, 1)
    glos = ' · '.join('<a href="glosario.html#%s">%s</a>' % (glosario_ancla(t), t.split(' (')[0])
                      for t in a.get('libro_glosario', []))
    return ('<aside class="apartado-libro apartado-libro-nota" aria-labelledby="notaLibroTit">'
            '<span class="apartado-libro-ico" aria-hidden="true">📘</span>'
            '<div class="apartado-libro-cuerpo">'
            '<p class="apartado-libro-tit" id="notaLibroTit">Nota de referencia</p>'
            '<p>%s</p>'
            '%s'
            '<p class="apartado-libro-ficha" id="nota-%d"><span class="apartado-libro-num">[%d]</span> %s '
            '<a class="apartado-libro-ir" href="%s">Ver la ficha en el compendio de fuentes ➔</a></p>'
            '</div></aside>' % (texto, ('<p class="apartado-libro-glos"><b>Sus conceptos, en el glosario:</b> %s</p>' % glos) if glos else '',
                                num, num, cita, url))

def libro_enlace(a):
    """Enlace «Nota de referencia» y, en una plantilla, lo que muestra la
    ventana lateral: el texto con su llamado, los conceptos del glosario y
    la ficha del compendio de fuentes."""
    rid, num, cita = a['libro_ref']
    url = 'fuentes-oficiales.html#%s' % rid
    llamado = ('<sup class="apartado-libro-llamado"><a href="%s" title="Ver la ficha [%d] en el compendio de fuentes">[%d]</a></sup>'
               % (url, num, num))
    texto = a['libro'].replace('sobre todo sus capítulos 5 y 7.', 'sobre todo sus capítulos 5 y 7.' + llamado, 1)
    glos = ''.join('<li><a href="glosario.html#%s">%s ➔</a></li>' % (glosario_ancla(t), t.split(' (')[0])
                   for t in a.get('libro_glosario', []))
    return ('<a class="apartado-nota" href="%s" data-libro="1">📘 Nota de referencia</a>'
            '<template id="tplNotaLibro">'
            '<header class="glos-drawer-cab"><span class="glos-drawer-marca"><span aria-hidden="true">📘</span> Nota de referencia</span>'
            '<button type="button" class="glos-drawer-x" aria-label="Cerrar la nota">✕</button></header>'
            '<div class="glos-drawer-cuerpo">'
            '<span class="glos-drawer-cat">Doctrina y bibliografía</span>'
            '<h3 id="notaLibroTit" class="glos-drawer-tit">El libro que ordena este apartado</h3>'
            '<section class="glos-drawer-sec"><h4>Por qué se cita</h4><p>%s</p></section>'
            '%s'
            '<section class="glos-drawer-sec"><h4>Referencia [%d]</h4><p class="glos-drawer-ley">%s</p></section>'
            '</div>'
            '<footer class="glos-drawer-pie">'
            '<a class="glos-drawer-todo" href="%s" style="text-align:center; text-decoration:none;">📚 Ver la ficha en el compendio de fuentes ➔</a>'
            '</footer></template>'
            % (url, texto,
               ('<section class="glos-drawer-sec"><h4>Sus conceptos, en el glosario</h4><ul class="rc-plazos">%s</ul></section>' % glos) if glos else '',
               num, cita, url))


def fichas(lista):
    """Fichas que se despliegan en la misma página (datos.js): botones con
    el aspecto de las tarjetas, sin enlace a la portada."""
    partes = []
    for fid, icono, nombre, desc, rubro in lista:
        clase = 'apartado-tarjeta dt-ficha' + (' rubro-' + rubro if rubro else '')
        partes.append('<button type="button" class="%s" data-ficha="%s" aria-expanded="false">\n'
                      '  <span class="apartado-tarjeta-icono" aria-hidden="true">%s</span>\n'
                      '  <span class="apartado-tarjeta-nombre">%s</span>\n'
                      '  <span class="apartado-tarjeta-desc">%s</span>\n'
                      '  <span class="apartado-tarjeta-accion">Desplegar ▾</span>\n'
                      '</button>' % (clase, fid, icono, nombre, desc))
    return '<div class="apartado-rejilla dt-fichas">\n' + '\n'.join(partes) + '\n</div>'

def glos(termino, texto):
    return '<a class="glos-pagina" href="glosario.html#%s">%s</a>' % (glosario_ancla(termino), texto)


def nota_ref(ref, n, titulo):
    return '<sup class="apartado-libro-llamado"><a href="fuentes-oficiales.html#%s" title="%s">[%02d]</a></sup>' % (ref, titulo, n)


# El camino del dinero en cuatro pasos (10-10-2026): era la entrada del
# modulo «Circuito del Dinero», que se reparte en Numeros. Mismo texto y
# mismas fuentes; cada paso lleva a su capitulo.
CAMINO_NUMEROS = (
    '<section class="camino" aria-labelledby="caminoTit">\n'
    '        <h2 class="camino-tit" id="caminoTit">El camino del dinero, en cuatro pasos</h2>\n'
    '        <p class="camino-txt">El dinero público recorre siempre el mismo camino. Antes de auditar una cifra hay que saber por dónde pasó.</p>\n'
    '        <ol class="camino-pasos">\n%s\n        </ol>\n      </section>') % '\n'.join(
    '          <li class="camino-paso"><span class="camino-num" aria-hidden="true">%d</span><span class="camino-ico" aria-hidden="true">%s</span>'
    '<b class="camino-que">%s</b><span class="camino-det">%s</span><a class="camino-ir" href="%s">%s ➔</a></li>' % x for x in [
        (1, '📜', 'Se autoriza cobrarlo',
         'El Congreso lo aprueba en la %s %s.' % (glos('LIF (Ley de Ingresos de la Federación)', 'Ley de Ingresos de la Federación'),
                                                 nota_ref('ref-lif2026', 10, 'Ley de Ingresos de la Federación 2026')),
         '#origen', 'Capítulo 1'),
        (2, '🏛️', 'Se decide en qué gastarlo',
         'La Cámara de Diputados aprueba el %s %s.' % (glos('PEF (Presupuesto de Egresos de la Federación)', 'Presupuesto de Egresos'),
                                                      nota_ref('ref-pef2026', 11, 'Presupuesto de Egresos de la Federación 2026')),
         '#decide', 'Capítulo 2'),
        (3, '🗺️', 'Se ejerce y se reparte',
         'El gobierno lo gasta y lo baja al territorio por dos ramos: el %s, de participaciones que los estados gastan con libertad, '
         'y el %s, de aportaciones etiquetadas para educación, salud, agua o seguridad %s.' % (
             glos('Ramo 28 (Participaciones Federales)', 'Ramo 28'), glos('Ramo 33 (Aportaciones Federales)', 'Ramo 33'),
             nota_ref('ref-lcf', 5, 'Ley de Coordinación Fiscal')),
         '#baja', 'Capítulo 4'),
        (4, '🔍', 'Se rinden cuentas',
         'Al año siguiente se entrega la %s, que revisa la %s.' % (
             glos('Cuenta Pública', 'Cuenta Pública'), glos('Auditoría Superior de la Federación (ASF)', 'Auditoría Superior de la Federación')),
         'herramienta-inspector-asf.html', 'Qué encontró la ASF'),
    ])


# Diccionario del Gasto Publico (10-10-2026): la obra entera, en dos
# estantes. «Biblioteca hacendaria» es para entender (glosario, marco legal,
# preguntas); «Fuentes del auditor» es para verificar (compendio de fuentes y
# pase). Cada entrada: (archivo, icono, nombre, frase, descripcion, estante).
# Las pestanas de Aprende, la portada del Diccionario y la barra al pie de
# cada pagina salen de esta lista.
ESTANTES = [
    ('biblioteca', '🏛️', 'Biblioteca hacendaria', 'Para entender',
     'Las palabras, las leyes y las preguntas del dinero público, explicadas en lenguaje llano.'),
    ('kit', '🧭', 'Fuentes del auditor', 'Para verificar',
     'Los documentos oficiales que sostienen cada cifra y el pase para sostener la plataforma.'),
]

BIBLIOTECA = [
    ('glosario.html', '📖', 'Glosario de Términos Hacendarios', 'Las palabras del erario',
     'Los términos del presupuesto, la deuda y la fiscalización, en lenguaje llano, con su fundamento y con buscador.', 'biblioteca'),
    ('marco-legal.html', '⚖️', 'Marco Legal Hacendario', 'El texto vigente',
     'El ciclo del dinero público artículo por artículo: Constitución, Ley de Ingresos 2026, LFPRH, Coordinación Fiscal, Disciplina Financiera y Poder Judicial, con el texto vigente cotejado.', 'biblioteca'),
    ('preguntas-frecuentes.html', '💡', 'Preguntas Frecuentes en Casillas Didácticas', 'Respuestas con fuente',
     'Cómo funciona el gasto público, la deuda, el dinero de estados y municipios, qué revisa la Auditoría Superior y cuánto cuesta el Poder Judicial. Cada respuesta con sus fuentes.', 'biblioteca'),
    ('fuentes-oficiales.html', '📑', 'Compendio de Fuentes Oficiales', 'Cada documento citado',
     'El portal de referencias: todas las fichas que sostienen las cifras de la plataforma, numeradas y con su liga directa al DOF, Hacienda, la Auditoría Superior, Banxico, el INEGI y Transparencia Presupuestaria.', 'kit'),
    ('pase-del-auditor.html', '🍺', 'Pase del Auditor Cívico', 'Sostén la plataforma',
     'Herramientas independientes de fiscalización ciudadana: $79 al mes, menos que dos caguamas.', 'kit'),
]

DIC_ENLACE = ('<p class="bib-sello">📚 Forma parte del <a href="diccionario.html">Diccionario del Gasto Público</a>, '
              'la obra de consulta de la plataforma.</p>')


def bib_estante(clave):
    return [(b[1], b[2], b[4], b[0], None, None) for b in BIBLIOTECA if b[5] == clave]


def bib_nav(actual):
    """Barra al pie de cada pagina del Diccionario, con sus dos estantes."""
    filas = []
    for e in ESTANTES:
        filas.append('          <span class="bib-nav-estante">%s %s</span>\n' % (e[1], e[2]) + '\n'.join(
            '          <a class="bib-nav-a" href="%s"%s><span aria-hidden="true">%s</span><span>%s<small>%s</small></span></a>'
            % (b[0], ' aria-current="page"' if b[0] == actual else '', b[1], b[2], b[3]) for b in BIBLIOTECA if b[5] == e[0]))
    return ('<nav class="bib-nav" aria-label="Diccionario del Gasto Público">\n'
            '        <a class="bib-nav-tit" href="diccionario.html">📚 Diccionario del Gasto Público</a>\n'
            '        <div class="bib-nav-fila">\n%s\n        </div>\n      </nav>' % '\n'.join(filas))


APARTADOS = [
    {
        'archivo': 'herramientas.html',
        'menu': 'Herramientas',
        'icono': '🧰',
        'titulo': 'Herramientas para seguir el dinero público',
        'lema': 'El gasto público, a la vista',
        'entrada': ('Dicho fácil: <b>de dónde sale el dinero de todos, en qué se gasta y quién revisa que se use bien.</b> '
                    'Lo contamos con documentos oficiales, para que cualquier persona lo entienda y lo pueda revisar. '
                    'Aquí están las cuatro herramientas del auditor: cada una abre su propia página.'),
        'nota': True,
        'guia': 'abajo',
        'secciones': [
            {
                'id': 'modulos',
                # Desde el 09-10-2026 los modulos son «herramientas» y la
                # seccion va sin titulo ni parrafo (decision del autor): las
                # tarjetas, mas grandes y con su imagen, son lo principal, y
                # cada una abre su propia pagina (HERRAMIENTAS, abajo).
                'titulo': '',
                'texto': '',
                'modulos': True,
                'tarjetas': [
                    ('🏗️', 'Simulador de Inversión y Megaobras', '', 'herramienta-megaobras.html', None, 'obras'),
                    ('💳', 'Calculadora Cívica', '', 'herramienta-calculadora.html', None, 'calculadora'),
                    ('🔍', 'Modo Inspector', '', 'herramienta-inspector.html', None, 'inspector'),
                    ('🌎', 'Costo Ambiental', '', 'herramienta-ambiente.html', None, 'ambiente'),
                ],
            },
        ],
    },
    {
        'archivo': 'sigue-el-dinero.html',
        # Desde el 09-10-2026 el menu se llama «Números» (decision del autor);
        # el archivo conserva su nombre para no romper enlaces.
        'menu': 'Números',
        'icono': '💰',
        'titulo': 'Números',
        'lema': 'Seis capítulos, del impuesto a la deuda',
        'entrada': ('El dinero público tiene un recorrido: se recauda, se aprueba, se gasta, baja a estados y municipios, '
                    'se pide prestado y, al final, te toca una parte. Aquí lo sigues capítulo por capítulo.'),
        'libro': ('Este apartado sigue el orden de <cite>Introducción al Derecho Económico</cite>, de Moisés Gómez Granillo y '
                  'Rosa María Gutiérrez Rosas (Editorial Esfinge, 1995), sobre todo sus capítulos 5 y 7. Cada capítulo trae una '
                  'franja <b>«Ayer y hoy»</b>: lo que explicaba el libro y cómo está hoy, con el documento oficial que lo sostiene. '
                  'Las cifras no se copian del libro: se toman de su fuente oficial vigente.'),
        # Nota de referencia (decision del autor, 09-10-2026): la obra es la
        # ficha ref-gomez-granillo-1995 del catalogo de fuentes y sus
        # conceptos llevan al glosario del auditor.
        'libro_ref': ('ref-gomez-granillo-1995', 119,
                      'Gómez Granillo, M., y Gutiérrez Rosas, R. M. (1995). <cite>Introducción al derecho económico</cite>. Editorial Esfinge.'),
        'libro_glosario': ['Rectoría Económica del Estado', 'Economía Mixta', 'Sistema Nacional de Planeación Democrática',
                           'Hacienda Pública', 'LIF (Ley de Ingresos de la Federación)', 'PEF (Presupuesto de Egresos de la Federación)',
                           'Gasto Federalizado', 'Deuda Pública y SHRFSP'],
        'scripts': ['deuda-tiempo.js'],
        'antes': CAMINO_NUMEROS,
        # Desde el 09-10-2026 cada capitulo es una pestana (decision del
        # autor): su contenido y sus fichas solo se despliegan al pulsarla.
        'pestanas': True,
        'secciones': [
            {
                'id': 'origen',
                'pestana': ('💵', '1 · De dónde sale', 'Ingresos y Ley de Ingresos'),
                'num': 1,
                'titulo': 'De dónde sale el dinero',
                'texto': 'Impuestos, ingresos petroleros y deuda: todo lo que autoriza la Ley de Ingresos, y su recorrido completo hasta el gasto.',
                'ayer': ('El capítulo 7 abre con la «Acción financiera del Estado para el equilibrio de la economía» (p. 96), antes de pasar al presupuesto, a la ley de gasto y a la de deuda.',
                         'Cada año la <b>Ley de Ingresos de la Federación</b> dice cuánto puede recaudar y cuánto puede pedir prestado la Federación (la de 2026 se publicó en el DOF el 7 de noviembre de 2025). Contribuir al gasto público es una obligación del artículo 31, fracción IV de la Constitución.'),
                'tarjetas': [
                    ('🏛️', 'El camino del dinero, en cuatro etapas', 'Se recauda, se aprueba, se ejerce y se revisa: cuánto mueve cada etapa y qué ley la gobierna. Pulsa «Contabilizar».', ir('presupuesto', 'eb-arquitectura'), None, 'dinero'),
                    ('💰', 'Cuánto dinero es', 'Los $10.19 billones aprobados para 2026, la cifra total antes de partirla.', ir('presupuesto', 'eb-cuanto'),
                     'Presupuesto de Egresos de la Federación 2026, art. 1', 'dinero'),
                    ('📥', 'De dónde sale cada peso', 'El ingreso federal de 2026, renglón por renglón, tal como lo enumera el artículo 1o. de la Ley de Ingresos.', ir('presupuesto', 'eb-ingresos'), None, 'dinero'),
                    ('📏', '¿A qué equivale?', 'Tres comparaciones para dimensionar las cifras, con la operación a la vista.', ir('presupuesto', 'eb-equivale'), None, 'dinero'),
                    ('🔦', 'Lo que la cifra grande no dice', 'Cinco lecturas que no aparecen en el anuncio presupuestal y que cambian el sentido del total.', ir('presupuesto', 'eb-ciegos'), None, 'inspector'),
                    ('📈', 'Paquete Económico 2027', 'La proyección de ingresos y gasto para 2027, sus supuestos, riesgos y puntos ciegos.', ir('proyeccion2027'), None, 'dinero'),
                ],
            },
            {
                'id': 'decide',
                'pestana': ('🏛️', '2 · Quién lo decide', 'El Congreso y los Poderes'),
                'num': 2,
                'titulo': 'Quién lo decide',
                'texto': 'El Congreso autoriza los ingresos y la deuda; la Cámara de Diputados aprueba el gasto. Y los Poderes también cuestan.',
                'ayer': ('El capítulo 5 explica las facultades económicas del Congreso de la Unión, del Senado y de la Cámara de Diputados (pp. 74-76), y las de la Asamblea de Representantes del Distrito Federal (p. 77).',
                         'Las facultades siguen en los artículos 73 y 74 de la Constitución: la fracción IV del 74 da a los diputados la aprobación anual del Presupuesto de Egresos. El Distrito Federal es hoy la <b>Ciudad de México</b>, con su propio Congreso, desde la reforma constitucional publicada en el DOF el 29 de enero de 2016.'),
                'tarjetas': [
                    ('⚖️', 'Lo que Cuestan el Congreso y la Judicatura', 'Presupuesto 2026, gasto auditado 2024 y sueldos netos oficiales.', ir('poderes'), None, 'dinero'),
                ],
            },
            {
                'id': 'gasta',
                'pestana': ('🏢', '3 · Quién lo gasta', 'Ramos, obras y ambiente'),
                'num': 3,
                'titulo': 'Quién lo gasta y en qué',
                'texto': 'Cuánto recibe cada Secretaría, qué obras se pagan y qué le cuesta al ambiente.',
                'ayer': ('«Presupuesto y gasto público» (p. 97) reparte el Presupuesto de 1994 en sus Cuadros 1 y 2, y la sección 3 (p. 103) explica la Ley de Presupuesto, Contabilidad y Gasto Público Federal de 1976.',
                         'Esa ley fue abrogada: desde 2006 rige la <b>Ley Federal de Presupuesto y Responsabilidad Hacendaria</b> (DOF 30 de marzo de 2006). La clasificación funcional del gasto de 2026 la publican los Criterios Generales de Política Económica 2027 (cuadro de la p. 39).'),
                'tarjetas': [
                    ('🏢', 'En qué se va: ramos y dependencias', 'Cuánto recibe cada Secretaría, en bloques proporcionales: de la función al ramo y al programa.', ir('presupuesto', 'eb-egresos'), None, 'dinero'),
                    ('🌡️', '¿Cuánto margen tiene el presupuesto?', 'Lo que ya está comprometido antes de empezar: deuda, participaciones y gasto programable, en un termostato.', ir('presupuesto', 'eb-salud'), None, 'dinero'),
                    ('📒', 'El estado de resultados del Gobierno', 'La Cuenta Pública 2024 leída como un negocio: actividades, flujos, situación financiera y gasto social.', ir('presupuesto', 'eb-cuenta-federal'), None, 'dinero'),
                    ('🏗️', 'Inversión Pública &amp; Megaobras', 'Presupuesto, costo y pérdidas de las grandes obras, de Tren Maya y Dos Bocas al AIFA. Fuentes por obra en verificación.', ir('megaobras'), None, 'obras'),
                    ('🌎', 'Costo Ambiental', 'El daño ambiental en pesos, su promedio por habitante, el servicio municipal de basura y el presupuesto ambiental 2026-2027.', ir('ambiente'), None, 'ambiente'),
                ],
            },
            {
                'id': 'baja',
                'pestana': ('📍', '4 · A dónde baja', 'Estados y municipios'),
                'num': 4,
                'titulo': 'A dónde baja',
                'texto': 'El dinero federal llega a los 32 estados y a los 2,479 municipios, y ahí se suma a lo que cada uno recauda.',
                'ayer': ('El Cuadro 1 del capítulo 7 ya separaba, dentro del Presupuesto de 1994, lo que la Federación destinaba a estados y municipios.',
                         'Hoy viaja por dos vías: las <b>participaciones</b> (Ramo 28), de libre uso, y las <b>aportaciones</b> (Ramo 33), etiquetadas por la Ley de Coordinación Fiscal para salud, educación, infraestructura y seguridad.'),
                'tarjetas': [
                    ('📍', 'El mapa del gasto federalizado', 'El tramo del gasto que viaja a los 32 estados, sobre el territorio y de mayor a menor.', ir('presupuesto', 'eb-mapa'), None, 'dinero'),
                    ('🗺️', 'Las 32 Entidades: del Peso Federal al Estatal', 'Los tres pisos de la hacienda, participaciones (Ramo 28), aportaciones (Ramo 33) y el circuito de cada estado.', ir('territorio'), None, 'dinero'),
                    ('🏘️', 'Los 2,479 Municipios: Predial y Transferencias', 'Padrón INEGI EFIPEM con la ficha financiera de cada municipio: predial, participaciones, FORTAMUN y FISMDF.', ir('municipios'), None, 'dinero'),
                ],
            },
            {
                'id': 'deuda',
                'pestana': ('📉', '5 · Cuánto debemos', 'La deuda, sexenio por sexenio'),
                'num': 5,
                'titulo': 'Cuánto debemos',
                'texto': 'La deuda pública de 1994 a la proyección de 2027, sexenio por sexenio. Pulsa «Contabilizar» y mírala crecer.',
                'ayer': ('La sección 4 del capítulo 7 (p. 104) explica la Ley General de Deuda Pública y su Gráfica 1 sigue la deuda externa de 1988 a 1994, en dólares.',
                         'La misma ley se llama hoy <b>Ley Federal de Deuda Pública</b> (decreto del DOF del 27 de abril de 2016). Y la deuda se mide con un indicador más amplio, el saldo histórico de los requerimientos financieros del sector público (SHRFSP), que Hacienda publica desde 2000.'),
                'bloque': ('<div class="dt" id="deudaTiempo">\n'
                           '          <noscript><p>La línea de tiempo necesita JavaScript. La serie, con sus fuentes, está en el auditor.</p></noscript>\n'
                           '        </div>'),
                'tarjetas': [
                    ('⏱️', 'El Reloj de la Deuda', 'Lo que el país se endeuda, paga de intereses y pierde por segundo, con su contador en vivo.', ir('calculadora', 'eb-ccreloj'), None, 'inspector'),
                ],
            },
            {
                'id': 'ati',
                'pestana': ('🧮', '6 · ¿Cuánto te toca?', 'La calculadora de tu sueldo'),
                'num': 6,
                'titulo': 'Y a ti, ¿cuánto te toca?',
                'texto': 'Escribe tu sueldo y mira a qué rubros, fondos y pago de deuda se van tus impuestos.',
                'tarjetas': [
                    ('🧮', 'Calculadora Cívica de Tu Sueldo', 'A qué rubros y fondos se van los impuestos de tu nómina, con tu ticket cívico.', ir('calculadora'), None, 'calculadora'),
                ],
            },
        ],
    },
    {
        'archivo': 'descarga-los-datos.html',
        'menu': 'Datos',
        'icono': '💾',
        'titulo': 'Los datos: cifras de referencia y descargas',
        'lema': 'Datos abiertos con su fuente',
        'entrada': ('Todo lo que ves en el auditor sale de documentos oficiales. Aquí están las cifras de referencia '
                    'para poner el gasto en perspectiva, con su fuente, y los archivos que abren en Excel para que '
                    'hagas tus propias cuentas.'),
        'scripts': ['radar-datos.js', 'audit-database.js', 'municipios-efipem.js', 'datos.js'],
        # Desde el 09-10-2026 las secciones son pestanas y cada ficha se
        # despliega aqui mismo, con su contenido (decision del autor):
        # datos.js las arma. Ya no abren la portada.
        'pestanas': True,
        'secciones': [
            {
                'id': 'radar',
                'pestana': ('📡', 'Radar hacendario', 'Cifras en perspectiva'),
                'titulo': '📡 Radar hacendario: cifras en perspectiva',
                'texto': ('Las cifras grandes del erario y lo que equivalen por segundo mientras lees. '
                          'Pulsa «Desglosar cifras» o toca una cifra para ver cómo se calcula y de dónde sale.'),
                'bloque': RADAR,
                'tarjetas': [],
            },
            {
                'id': 'abiertos',
                'pestana': ('💾', 'Datos abiertos', 'Bases en CSV para Excel'),
                'titulo': '💾 Datos abiertos',
                'texto': 'Bases en CSV, listas para revisar. Pulsa una ficha para desplegarla.',
                'bloque': fichas([
                    ('descargas', '📥', 'Descarga en CSV (abre en Excel)', 'Siete bases con fuente oficial: municipios, sueldos netos, gasto de los Poderes, presupuesto ambiental, auditorías de la ASF por estado, lista 69-B y documentos.', 'dinero'),
                    ('municipios', '🏘️', 'Base de Datos Municipal EFIPEM (INEGI)', 'Los 2,479 municipios con sus ingresos, predial, participaciones y fondos del Ramo 33, en CSV.', 'dinero'),
                ]),
                'tarjetas': [],
            },
            {
                'id': 'informes',
                'pestana': ('📑', 'Informes oficiales', 'Cuenta Pública y diccionario'),
                'titulo': '📑 Informes oficiales',
                'texto': 'Lo que revisó la Auditoría Superior y qué contiene cada archivo. Pulsa una ficha para desplegarla.',
                'bloque': fichas([
                    ('asf', '🔎', 'Informes de la Cuenta Pública (ASF)', 'Qué revisó la Auditoría Superior en 2024, cuánto quedó por aclarar en tu estado y cuándo sale la siguiente entrega.', 'inspector'),
                    ('diccionario', '📋', 'Diccionario de Datos', 'Qué contiene cada archivo de datos de la plataforma, campo por campo.', None),
                ]),
                'tarjetas': [],
            },
        ],
    },
    {
        'archivo': 'aprende.html',
        'menu': 'Aprende',
        'icono': '📖',
        'titulo': 'Aprende',
        'lema': 'Biblioteca y fuentes del auditor ciudadano',
        'entrada': ('Las palabras del presupuesto, las leyes que lo rigen y las fuentes donde se publica, '
                    'explicadas en lenguaje llano. Para leer una cifra oficial no hace falta ser especialista. '
                    'Para ponerte a prueba, una trivia con el estado de cuenta de cada presidente; y para leer con calma, columnas con datos curiosos de personajes y hechos.'),
        'scripts': ['trivia-presidentes.js', 'columnas.js'],
        'estilos': ['columnas.css'],
        # Desde el 09-10-2026 las secciones son pestanas (decision del autor):
        # su contenido solo se despliega al pulsar la pestana.
        'pestanas': True,
        'secciones': [
            {
                'id': 'trivia',
                'pestana': ('🎯', 'Trivia', 'El examen de los presidentes'),
                'titulo': '🎯 Trivia: el examen de los presidentes',
                'texto': ('Del siglo XIX, con Santa Anna, Juárez y Porfirio Díaz, al primer año de Claudia Sheinbaum: adivina, comprueba con la cifra oficial '
                          'en barras o en línea y, al final, mira el estado de cuenta de cada presidente y el reloj de su deuda. '
                          'Incluye los rubros de la gran balanza de la Enciclopedia (déficit, deuda, aduanas y rieles), verificados de nuevo contra el INEGI y Hacienda.'),
                'bloque': ('<div class="tp" id="triviaPres">\n'
                           '          <noscript><p>La trivia necesita JavaScript.</p></noscript>\n'
                           '        </div>'),
                'tarjetas': [],
            },
            {
                # Diccionario del Gasto Publico, estante 1 (10-10-2026). Desde
                # el 09-10-2026 cada apartado tiene su pagina ligera; ya no se
                # abre la portada en un marco (eso era lo que se trababa).
                'id': 'biblioteca',
                'pestana': ('🏛️', 'Biblioteca hacendaria', 'Glosario, leyes y preguntas'),
                'titulo': '🏛️ Biblioteca hacendaria',
                'texto': ('Para entender: las palabras, las leyes y las preguntas del dinero público. '
                          'Cada apartado abre su propia página, con buscador y con el documento oficial que lo sostiene.' + DIC_ENLACE),
                'tarjetas': bib_estante('biblioteca'),
            },
            {
                # Estante 2: el portal de referencias y el pase.
                'id': 'kit',
                'pestana': ('🧭', 'Fuentes del auditor', 'Documentos oficiales y pase'),
                'titulo': '🧭 Fuentes del auditor ciudadano',
                'texto': ('Para verificar: los documentos oficiales que sostienen cada cifra de la plataforma, con su liga directa, '
                          'para que revises por tu cuenta.' + DIC_ENLACE),
                'tarjetas': bib_estante('kit'),
            },
            {
                # Columnas editoriales (09-10-2026): reune, verificado contra
                # documentos oficiales, lo que fueron las secciones 5.2 y 5.3
                # de la Enciclopedia (personajes relevantes y datos curiosos),
                # retiradas el 27-09-2026 por no citar fuentes. Las pinta
                # assets/auditor/js/columnas.js.
                'id': 'noticias',
                'pestana': ('📰', 'Noticias relevantes', 'Columnas de personajes y hechos'),
                'titulo': '📰 Noticias relevantes',
                'texto': ('Columnas con datos curiosos de personajes y hechos del dinero público. '
                          'Cada afirmación lleva el documento oficial que la sostiene.'),
                'bloque': ('<div class="col-diario" id="columnasDiario">\n'
                           '          <noscript><p>Las columnas necesitan JavaScript.</p></noscript>\n'
                           '        </div>'),
                'tarjetas': [],
            },
        ],
    },
    {
        'archivo': 'participa.html',
        'menu': 'Participa',
        'icono': '💬',
        'titulo': 'Participa',
        'lema': 'Ágora cívica y canales oficiales',
        'entrada': ('Contrasta posturas con fuentes, publica tu argumento y, si viste algo raro con el dinero público, '
                    'llévalo al canal oficial que corresponde. Sin correos, teléfonos ni rastreo.'),
        'pestanas': True,
        'scripts': ['audit-database.js', 'participa.js'],
        'secciones': [
            {
                # El contenido vive aquí desde el 09-10-2026 (antes eran
                # tarjetas que llevaban a la portada). Bloques tomados de
                # index.html en participa_html.py; los pinta participa.js.
                'id': 'agora',
                'pestana': ('💬', 'Ágora cívica', 'Diálogos y argumentos con fuentes'),
                'titulo': '💬 Ágora cívica y diálogos',
                'texto': 'Un espacio plural para argumentar con datos: publica tu postura con seudónimo y tus fuentes, y replica a cualquier argumento.',
                'bloque': participa_html.PORTAL,
                'tarjetas': [],
            },
            {
                'id': 'garantias',
                'pestana': ('🛡️', 'Garantías cívicas', 'Privacidad y canales de denuncia'),
                'titulo': '🛡️ Garantías cívicas y formación',
                'texto': 'Qué pasa con lo que escribes, cómo armar un reporte útil y a dónde llevar un señalamiento para que se vuelva expediente.',
                'bloque': ('<div id="comOrientacion"></div>\n'
                           '        <div class="fj-bloque" id="bloqueAportar">\n'
                           '        <div class="fj-bloque-head"><span class="fj-kicker">Función 1</span>'
                           '<h3>Ayúdanos a fiscalizar: comparte lo que viste</h3></div>\n'
                           + participa_html.APORTAR + '\n        </div>\n        '
                           + participa_html.CANALES),
                'tarjetas': [],
            },
        ],
    },
]

# Paginas de herramienta (decision del autor, 09-10-2026): cada tarjeta de
# Herramientas abre su propia pagina. El encabezado lleva la imagen y el
# proemio del modulo (PROEMIOS del motor: si cambia uno, cambia el otro) y
# cada tema es una pestana que despliega su bloque en el visor, sin salir.
# Las imagenes son ilustrativas, como en Auditoria en imagenes. La hoja
# apartados.css las pone por rubro (.herr-foto.rubro-*), porque un url()
# dentro de una variable se resolveria contra la carpeta de la hoja.
HERR_IMG = {
    'obras': 'assets/auditor/img/herr-megaobras-plataformas-amplia.jpg',
    'calculadora': 'assets/auditor/img/herr-calculadora-monedas-amplia.jpg',
    'inspector': 'assets/auditor/img/herr-inspector-foroptero-amplia.jpg',
    'ambiente': 'assets/auditor/img/herr-ambiente-refineria-amplia.jpg',
}

# (archivo, rubro, icono, titulo, subtitulo, texto, modulo del motor, temas)
# Cada tema: (ancla sin «eb-», icono, nombre, frase de la pestana,
# descripcion). Un tema que es un .html es un enlace a esa pagina.
HERRAMIENTAS = [
    ('herramienta-megaobras.html', 'obras', '🏗️', 'Inversión y Megaobras',
     'Lo que se prometió, lo que se pagó y la diferencia',
     'Seguimiento a costos, sobrecostos y subsidios de las obras que definieron cada sexenio: Tren Maya, Dos Bocas, AIFA y los demás '
     'proyectos estratégicos de la nación, desde 1988 a la fecha. Cada cifra remite al documento que la sostiene.',
     'megaobras', [
         ('pulso', '📊', 'El pulso del gasto', 'Costo y sobrecosto',
          'Las cifras de referencia de las obras (costo, sobrecosto, pérdidas de operación y subsidios), por día, mes, trimestre, semestre o año.'),
         ('sector', '🏭', 'Sector e industria', 'Obra por obra',
          'Filtra por industria y por mandato: la comparativa de las obras, su ficha viva y contra qué se compara ese dinero.'),
         ('sexenios', '🏛️', 'Las obras de cada sexenio', 'De 1988 a 2024',
          'Qué megaobras le tocan a cada presidente, de 1988 a 2024, en una sola línea del tiempo.'),
         ('cero', '🧮', 'De cero al resultado', 'Las cuentas, renglón por renglón',
          'Las mesas de cálculo renglón por renglón, el inventario por sector y la procedencia de cada cifra, para seguir la cuenta con el dedo.'),
     ]),
    ('herramienta-calculadora.html', 'calculadora', '💳', 'Calculadora Cívica',
     'Tu sueldo, tus impuestos y el rubro al que llegan',
     'Escribe tu sueldo y la calculadora reparte lo que pagas (ISR, IVA y predial) entre los rubros del presupuesto. Después compara tu '
     'estado y tu municipio con los 2,479 del padrón nacional.',
     'calculadora', [
         ('ccticket', '🧾', 'Tu estado de cuenta', 'Lo que pagas y a dónde va',
          'Escribe lo que ganas y la página saca cuatro cuentas: tu ingreso, lo que te retienen, a dónde va cada peso de tu impuesto y tu estado de cuenta.'),
         ('cccompara', '⚡', 'Tú contra ellos', 'Cargo por cargo',
          'Tu ingreso neto frente al de quienes legislan, juzgan y gobiernan, y sus prestaciones de ley contra las tuyas, con el documento de cada cifra.'),
         ('ccreloj', '⏱️', 'El reloj de la deuda', 'Y de lo perdido',
          'Lo que el país se endeuda, paga de intereses y pierde por segundo, repartido entre habitantes o entre contribuyentes, con su contador en vivo.'),
     ]),
    ('herramienta-inspector.html', 'inspector', '🔍', 'Modo Inspector',
     'Dónde quedó el dinero que nadie ha podido explicar',
     'Expedientes de la Auditoría Superior de la Federación (ASF), adjudicaciones directas, empresas que facturan operaciones simuladas '
     '(EFOS) y focos rojos de riesgo. Solo informes oficiales: pliegos de observaciones, montos por aclarar y contratos abiertos.',
     'verificador', [
         ('inspasf', '🏛️', 'Qué encontró la ASF', 'El gasto de 2024',
          'Cuánto revisó la Auditoría Superior en el gasto de 2024, qué acciones promovió, cuánto quedó por aclarar y cuánto le toca a tu estado.'),
         ('inspradar', '🚩', 'Radar por entidad', 'Banderas rojas',
          'Qué estados dejaron más dinero federal sin aclarar ante la Auditoría Superior en la Cuenta Pública 2024, ordenados como prefieras.'),
         ('expedientes.html', '📂', 'Expedientes de casos', 'Casos por aclarar',
          'Los casos de alto impacto que siguen por aclarar, cada uno con su expediente y sus documentos. Tienen su propia página.'),
         ('inspentes', '🏢', 'Auditor de entes públicos', 'Busca y verifica',
          'Elige una autoridad federal, estatal o municipal y ve su diagnóstico: si gastó lo que aprobó la Cámara, si rindió cuentas y qué quedó por aclarar.'),
         ('inspnota', '📰', 'Contrasta una nota', 'Busca y verifica',
          '¿Leíste una cifra en una noticia, en redes o en un discurso? Ponla junto al documento oficial y ve cuánto se aleja y por qué.'),
         ('inspefos', '🧾', 'Lista negra del SAT', 'Busca y verifica',
          'Busca por RFC o por nombre en el listado del artículo 69-B del Código Fiscal: a quienes el SAT presume o declara emisores de facturas por operaciones inexistentes.'),
     ]),
    ('herramienta-ambiente.html', 'ambiente', '🌎', 'Costo Ambiental',
     'El gasto que no aparece en el recibo',
     'El deterioro del ambiente también es gasto: lo pagamos en agua, aire, suelo y basura. Aquí se mide en pesos con cifras oficiales '
     '(INEGI, SEMARNAT y Hacienda), se calcula tu parte y se compara con el presupuesto ambiental 2026-2027 y las leyes que aplican.',
     'ambiente', [
         ('amreloj', '⏱️', 'El reloj y el año', 'Un año en veinte segundos',
          'El daño ambiental que corre mientras lees y una simulación que acumula, día por día, cinco comparaciones de un año entero.'),
         ('amticket', '🧾', 'Tu ticket en negativo', 'Lo que ya te cargaron',
          'Escribe lo que ganas y ve lo que ya te cargaron a tu nombre: tu parte de la deuda, de sus intereses y del daño ambiental, con tu basura en kilos.'),
         ('ambasura', '🗑️', 'Basura y protección', 'Lo que se gasta en proteger',
          'Un servicio municipal sin partida federal, el presupuesto ambiental 2026 y 2027, la huella de las megaobras y las leyes que aplican.'),
         ('ampib', '📉', 'El PIB no alcanza', 'Lo que se acabó y se ensució',
          'La cascada animada del PIB, el simulador del crecimiento real y el desglose de lo que se acabó y lo que se ensució.'),
     ]),
]


def modulo_archivo(archivo, clave):
    """Pagina propia de un modulo: herramienta-megaobras.html + pulso ->
    herramienta-megaobras-pulso.html (sin el prefijo insp, cc o am)."""
    if clave.endswith('.html'):
        return clave
    return archivo[:-5] + '-' + re.sub(r'^(insp|cc|am)', '', clave) + '.html'


def herr_otras(archivo):
    otras = '\n'.join(
        '          <a class="herr-otra herr-foto rubro-%s" href="%s">'
        '<span class="herr-otra-ico" aria-hidden="true">%s</span><span class="herr-otra-tx">%s</span></a>'
        % (o[1], o[0], o[2], o[3]) for o in HERRAMIENTAS if o[0] != archivo)
    return ('<nav class="herr-otras" aria-label="Las otras herramientas">\n'
            '        <span class="herr-otras-tit">Las otras herramientas</span>\n'
            '        <div class="herr-otras-fila">\n%s\n        </div>\n      </nav>' % otras)


def herramienta(h, n):
    """Pagina de una herramienta (10-10-2026): ya no despliega nada. Es la
    ruta de sus modulos, numerados, y cada uno abre su propia pagina
    (herramienta_modulo). Antes cada pestana abria la portada entera en un
    marco debajo de la tarjeta."""
    archivo, rubro, icono, titulo, sub, texto, modulo, temas = h
    pasos = []
    for i, (clave, ico, nombre, frase, desc) in enumerate(temas, 1):
        pasos.append(
            '          <li><a class="herr-paso rubro-%s" href="%s">\n'
            '            <span class="herr-paso-num" aria-hidden="true">%d</span>\n'
            '            <span class="herr-paso-ico" aria-hidden="true">%s</span>\n'
            '            <span class="herr-paso-tx"><span class="herr-paso-frase">%s</span>'
            '<span class="herr-paso-nombre">%s</span><span class="herr-paso-desc">%s</span></span>\n'
            '            <span class="herr-paso-accion">Abrir ➔</span>\n'
            '          </a></li>' % (rubro, modulo_archivo(archivo, clave), i, ico, frase, nombre, desc))
    ruta = ('<ol class="herr-ruta">\n%s\n        </ol>' % '\n'.join(pasos))
    return {
        'archivo': archivo,
        'menu': titulo,
        'menu_archivo': 'herramientas.html',
        'padre': ('herramientas.html', 'Herramientas'),
        'icono': icono,
        'titulo': titulo,
        'lema': 'Herramienta %d de %d' % (n, len(HERRAMIENTAS)),
        'entrada': '<b>%s.</b> %s' % (sub, texto),
        'fondo': HERR_IMG[rubro],
        'rubro': rubro,
        # Las pestanas viejas (#pulso, #inspentes...) llevan a su pagina.
        'hash_a_pagina': dict((t[0][:-5] if t[0].endswith('.html') else t[0], modulo_archivo(archivo, t[0])) for t in temas),
        'secciones': [{
            'id': 'modulos', 'titulo': 'Los %d módulos' % len(temas), 'sin_cab': False,
            'texto': 'Recórrelos en orden o entra directo al que te interesa. Cada uno abre su propia página.',
            'tarjetas': [], 'bloque': ruta,
        }],
        'pie_extra': herr_otras(archivo),
    }


def herramienta_modulo(h, n, i):
    """Pagina propia de un modulo de herramienta (10-10-2026)."""
    archivo, rubro, icono, titulo, sub, texto, modulo, temas = h
    clave, ico, nombre, frase, desc = temas[i]
    url = ir(modulo, 'eb-' + clave)
    hermanos = []
    for k, t in enumerate(temas):
        hermanos.append('          <a class="herr-mod-chip%s" href="%s"%s><span aria-hidden="true">%s</span> %d · %s</a>' % (
            ' actual' if k == i else '', modulo_archivo(archivo, t[0]), ' aria-current="page"' if k == i else '', t[1], k + 1, t[2]))
    ant = temas[i - 1] if i > 0 else None
    sig = temas[i + 1] if i + 1 < len(temas) else None
    def paso(t, k, rotulo, clase):
        if not t:
            return ('          <a class="herr-mod-paso %s" href="%s"><small>%s</small><b>%s %s</b></a>'
                    % (clase, archivo, rotulo, icono, titulo))
        return ('          <a class="herr-mod-paso %s" href="%s"><small>%s · módulo %d</small><b>%s %s</b></a>'
                % (clase, modulo_archivo(archivo, t[0]), rotulo, k + 1, t[1], t[2]))
    navegacion = ('<nav class="herr-mod-nav" aria-label="Los módulos de %s">\n'
                  '        <div class="herr-mod-pasos">\n%s\n%s\n        </div>\n'
                  '        <span class="herr-otras-tit">Todos los módulos de %s</span>\n'
                  '        <div class="herr-mod-chips">\n%s\n        </div>\n      </nav>' % (
                      titulo,
                      paso(ant, i - 1, '← Anterior', 'ant') if ant else paso(None, 0, '← Volver al índice de', 'ant'),
                      paso(sig, i + 1, 'Siguiente →', 'sig') if sig else paso(None, 0, 'Terminaste · volver a', 'sig'),
                      titulo, '\n'.join(hermanos)))
    marco = ('<div class="apartado-visor herr-modulo" style="--tarjeta: var(--rubro-%s)">\n'
             '          <div class="apartado-visor-cuerpo">\n'
             '            <p class="apartado-visor-carga" role="status">⏳ Cargando el módulo con sus cifras y fuentes…</p>\n'
             '            <iframe class="apartado-visor-marco" title="%s" data-modulo="%s&amp;visor=1"></iframe>\n'
             '            <noscript><p>Este módulo necesita JavaScript. <a href="%s">Ábrelo en el auditor</a>.</p></noscript>\n'
             '          </div>\n'
             '          <div class="herr-modulo-pie"><a href="%s">⤢ Abrir en el auditor completo</a></div>\n'
             '        </div>' % (rubro, esc_attr(nombre), url, url, url))
    return {
        'archivo': modulo_archivo(archivo, clave),
        'menu': nombre,
        'menu_archivo': 'herramientas.html',
        'padre': ('herramientas.html', 'Herramientas'),
        'padre2': (archivo, titulo),
        'icono': ico,
        'titulo': nombre,
        'lema': '%s %s · módulo %d de %d' % (icono, titulo, i + 1, len(temas)),
        'sin_icono_lema': True,
        'entrada': '<b>%s.</b> %s' % (frase, desc),
        'fondo': HERR_IMG[rubro],
        'rubro': rubro,
        'secciones': [{
            'id': 'modulo', 'titulo': nombre, 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': marco,
        }],
        'pie_extra': navegacion + '\n\n      ' + herr_otras(archivo),
    }


# Diccionario del Gasto Publico (decision del autor, 09-10-2026): los
# enlaces que llevaban a la Enciclopedia (congelada) llegan aqui. Desde el
# 09-10-2026 (tarde) cada apartado tiene su pagina ligera; ya no abre la
# portada en un marco. Las anclas viejas (#glosario, #fuentes, #marco-legal,
# #preguntas) mandan a la pagina nueva (ver 'hash_a_pagina').
DICCIONARIO = {
    'archivo': 'diccionario.html',
    'menu': 'Diccionario del Gasto Público',
    'menu_archivo': 'aprende.html',
    'padre': ('aprende.html#biblioteca', 'Aprende'),
    'icono': '📚',
    'titulo': 'Diccionario del Gasto Público',
    'lema': 'Las palabras, las leyes y las fuentes del erario',
    'entrada': ('La obra de consulta de la plataforma, en dos estantes. La <b>Biblioteca hacendaria</b> es para entender: '
                'el glosario, el marco legal con su texto vigente y las preguntas frecuentes. Las <b>Fuentes del auditor</b> son '
                'para verificar: el compendio de fuentes oficiales que sostiene cada cifra y el pase del auditor cívico. '
                'Cada apartado abre su propia página.'),
    'hash_a_pagina': {'preguntas': 'preguntas-frecuentes.html', 'glosario': 'glosario.html',
                      'marco-legal': 'marco-legal.html', 'fuentes': 'fuentes-oficiales.html',
                      'referencias': 'fuentes-oficiales.html', 'pase': 'pase-del-auditor.html'},
    'secciones': [{
        'id': e[0], 'titulo': '%s %s' % (e[1], e[2]), 'texto': '%s. %s' % (e[3], e[4]),
        'tarjetas': bib_estante(e[0]),
    } for e in ESTANTES],
}


# Glosario general en su propia pagina (decision del autor, 09-10-2026):
# lo pinta assets/auditor/js/glosario.js con los terminos de la base, sin
# cargar la portada en un marco. Los enlaces a un termino llevan a
# glosario.html#<glosario_ancla(termino)>.
GLOSARIO = {
    'archivo': 'glosario.html',
    'menu': 'Glosario',
    'menu_archivo': 'aprende.html',
    'padre': ('diccionario.html', 'Diccionario del Gasto Público'),
    'icono': '📖',
    'titulo': 'Glosario de Términos Hacendarios',
    'lema': 'Las palabras del erario, en lenguaje llano',
    'entrada': ('Los términos del presupuesto, la deuda, la fiscalización y los Poderes, explicados para quien no es especialista. '
                'Cada uno trae su fundamento: el artículo, la ley o el documento oficial que lo define. Busca una palabra o elige una categoría.'),
    'scripts': ['audit-database.js', 'glosario.js'],
    'pie_extra': bib_nav('glosario.html'),
    'secciones': [{
        'id': 'terminos', 'titulo': 'Los términos', 'texto': '', 'sin_cab': True, 'tarjetas': [],
        'bloque': ('<div class="gl" id="glosarioPagina">\n'
                   '          <p class="gl-carga" role="status">⏳ Cargando los términos…</p>\n'
                   '          <noscript><p>El glosario necesita JavaScript.</p></noscript>\n'
                   '        </div>'),
    }],
}



def pagina_biblioteca(archivo, titulo, lema, entrada, raiz, carga, scripts=('audit-database.js', 'biblioteca.js'), bloque=None):
    b = [x for x in BIBLIOTECA if x[0] == archivo][0]
    return {
        'archivo': archivo, 'menu': b[2], 'menu_archivo': 'aprende.html',
        'padre': ('diccionario.html', 'Diccionario del Gasto Público'),
        'icono': b[1], 'titulo': titulo, 'lema': lema, 'entrada': entrada,
        'scripts': list(scripts),
        'secciones': [{
            'id': 'contenido-' + archivo[:-5], 'titulo': titulo, 'texto': '', 'sin_cab': True, 'tarjetas': [],
            'bloque': bloque or ('<div class="bib" id="%s">\n'
                                 '          <p class="gl-carga" role="status">⏳ %s</p>\n'
                                 '          <noscript><p>Esta página necesita JavaScript.</p></noscript>\n'
                                 '        </div>' % (raiz, carga)),
        }],
        'pie_extra': bib_nav(archivo),
    }


PASE_HTML = """<div class="pase">
          <p class="pase-badge">⚡ Independencia cívica · Sin dinero de gobiernos ni de partidos políticos</p>
          <p>El erario se financia con tu trabajo y tus impuestos. Para auditarlo sin censura y mantener esta plataforma independiente de partidos políticos, te invitamos a sumarte. Menos de lo que te gastas en dos caguamas al mes.</p>
          <div class="pase-precios">
            <div class="pase-plan">
              <div class="pase-plan-tit">Plan mensual</div>
              <div class="pase-precio">$79 <small>MXN al mes</small></div>
              <p>Cancela cuando quieras.</p>
              <span class="pase-pronto">Disponible en el lanzamiento</span>
            </div>
            <div class="pase-plan pase-plan-pop">
              <div class="pase-plan-tit">★ Plan anual cívico</div>
              <div class="pase-precio">$699 <small>MXN al año</small></div>
              <p>Equivale a $58.25 al mes: ahorras más de tres meses frente al plan mensual.</p>
              <span class="pase-pronto">Disponible en el lanzamiento</span>
            </div>
          </div>
          <p><b>La suscripción todavía no está activa.</b> La pasarela segura de pago se abrirá con el lanzamiento; mientras tanto, todo lo que ves en la plataforma es libre y gratuito.</p>
          <h2 class="bib-bloque-tit">Qué obtendrás como auditor cívico</h2>
          <ul class="pase-lista">
            <li>✓ <b>Expediente de tu estado y tu municipio en PDF:</b> deuda, obras y observaciones de la Auditoría Superior, listo para imprimir antes de votar.</li>
            <li>✓ <b>Ticket cívico de tu quincena:</b> el rastro de tus impuestos en alta resolución, para compartir.</li>
            <li>✓ <b>Radar de alertas de la Auditoría Superior:</b> avisos de nuevas observaciones o contratos auditados en tu localidad.</li>
            <li>✓ <b>100 % cívico e independiente:</b> cero publicidad, cero convenios con partidos políticos.</li>
          </ul>
        </div>"""


PAGINAS_BIBLIOTECA = [
    pagina_biblioteca(
        'preguntas-frecuentes.html', 'Preguntas frecuentes', 'Respuestas directas, con su fuente',
        'Cómo funciona el dinero público, qué revisa la Auditoría Superior y cómo auditar por tu cuenta. Cada respuesta trae '
        'el documento que la sostiene y cada cifra su etiqueta: oficial, derivado o pendiente. Busca una palabra o elige un tema.',
        'bibPreguntas', 'Cargando las preguntas…'),
    pagina_biblioteca(
        'marco-legal.html', 'Marco legal hacendario', 'Las reglas del dinero público, con su texto vigente',
        'Los preceptos que rigen cómo se planea, se cobra, se aprueba, se gasta y se revisa el dinero público. El texto de cada '
        'uno se cotejó palabra por palabra con la versión vigente que publica la Cámara de Diputados o el DOF.',
        'bibMarco', 'Cargando los preceptos…'),
    pagina_biblioteca(
        'fuentes-oficiales.html', 'Compendio de fuentes oficiales', 'Cada documento que sostiene una cifra',
        'Las fichas numeradas que citan las cifras de la plataforma, con su liga al documento. Si llegaste desde una nota '
        'como [11], la ficha aparece iluminada.',
        'bibFuentes', 'Cargando el catálogo…'),
    pagina_biblioteca(
        'pase-del-auditor.html', 'Pase del Auditor Cívico', 'Sostén una plataforma independiente',
        'Herramientas independientes de fiscalización ciudadana, sin dinero de gobiernos ni de partidos.',
        None, None, scripts=(), bloque=PASE_HTML),
]

GUIA = '''<section class="apartado-guia" aria-labelledby="guiaTitulo">
        <h2 class="apartado-guia-titulo" id="guiaTitulo">Cómo se usa</h2>
        <ol class="apartado-pasos">
          <li><span class="apartado-paso-num" aria-hidden="true">1</span><span><b>Elige una herramienta y pulsa «Comenzar».</b> Cada color es un tema: las obras, tus impuestos, lo que revisó la Auditoría y el ambiente. Cada una abre su propia página y te cuenta qué trae.</span></li>
          <li><span class="apartado-paso-num" aria-hidden="true">2</span><span><b>Elige un módulo.</b> Cada herramienta se recorre en módulos numerados y cada uno abre su propia página; adentro hay juegos y cuentas para descubrir las cifras tú mismo.</span></li>
          <li><span class="apartado-paso-num" aria-hidden="true">3</span><span><b>Mira la etiqueta de cada cifra.</b> <span class="est-chip est-oficial">oficial</span> viene de un documento del gobierno; <span class="est-chip est-derivado">derivado</span> lo calculamos con datos oficiales y te decimos cómo; <span class="est-chip est-pendiente">pendiente</span> la dependencia responsable no lo ha transparentado en un documento oficial, y te decimos cuál.</span></li>
        </ol>
      </section>'''


def esc_attr(s):
    return html.escape(s, quote=True)


def cabecera(actual, sello):
    items = []
    for a in APARTADOS:
        cur = ' aria-current="page"' if a['archivo'] == actual else ''
        items.append('      <div class="nav-menu-item"><a class="mega-menu-trigger" href="%s"%s>%s</a></div>'
                     % (a['archivo'], cur, a['menu']))
    return '''  <nav class="site-top-nav" aria-label="Navegación principal">
    <div class="nav-brand-group">
      <button type="button" class="brand-logo-btn" id="apartadoPresentacion" title="Quiénes somos: qué es Auditavisión" aria-label="Quiénes somos: abrir la presentación de Auditavisión"><img src="assets/auditor/img/logo-auditavision.svg" alt="" width="72" height="56"></button>
      <a class="nav-brand-text" href="index.html" title="Ir a la página principal">
        <span class="nav-brand-title">Auditavisión</span>
        <span class="nav-brand-sub">El gasto público, a la vista</span>
      </a>
    </div>

    <button type="button" class="nav-hamburguesa" id="navHamburguesa" aria-expanded="false" aria-controls="navIndiceMovil" aria-label="Abrir el menú">
      <span class="nav-hamb-rayas" aria-hidden="true"><span></span><span></span><span></span></span>
      <span class="nav-hamb-txt">Menú</span>
    </button>

    <div class="nav-indice" id="navIndiceMovil">
    <div class="nav-center-links">
%s
    </div>

    <div class="nav-right-container">
      <div class="nav-right-actions">
        <a class="nav-action-btn nav-feedback-btn" href="index.html?ir=reporta" title="Ayúdanos a fiscalizar: comparte lo que viste y reporta anomalías presupuestales">
          <span>📢</span>
          <span>Cuéntanos lo que viste</span>
        </a>
        <button type="button" class="nav-action-btn nav-share-btn" id="apartadoCompartir" title="Compartir esta página o copiar su enlace">
          <span>🔗</span>
          <span>Compartir</span>
        </button>
        <a href="diccionario.html" class="nav-action-btn nav-creator-badge" title="Creado por Inspector Meteoro · Diccionario del Gasto Público">
          <span>🪐</span>
          <span>Inspector Meteoro</span>
        </a>
      </div>
      <div class="nav-movil-ayuda">
        <p class="nav-movil-ayuda-tit">¿Viste algo raro con el dinero público?</p>
        <p class="nav-movil-ayuda-txt">Cuéntanos qué, dónde y cuándo. Te ayudamos a ordenarlo y a llevarlo al canal oficial que corresponde.</p>
        <a class="nav-movil-ayuda-btn" href="index.html?ir=reporta">📢 Cuéntanos lo que viste</a>
      </div>
    </div>
    </div>
  </nav>''' % '\n'.join(items)


def tarjeta(t, modulo=False, auto=False):
    icono, nombre, desc, destino, fuente, rubro = t[:6]
    dato = t[6] if len(t) > 6 else None
    externo = destino.startswith('http')
    clase = 'apartado-tarjeta' + (' apartado-tarjeta-modulo' if modulo else '') + (' rubro-' + rubro if rubro else '')
    extra = ' target="_blank" rel="noopener noreferrer"' if externo else ''
    if modulo and rubro in HERR_IMG:
        clase += ' herr-foto'
    if auto:
        extra += ' data-auto="1"'
    titulo = ' title="%s"' % esc_attr(fuente) if fuente else ''
    accion = ('Abrir en su sitio oficial ↗' if externo else
              'Comenzar ➔' if modulo or 'moduloProemio' in destino else
              'Ver aquí ▾' if auto else 'Abrir ➔')
    partes = ['        <a class="%s" href="%s"%s%s>' % (clase, destino, extra, titulo),
              '          <span class="apartado-tarjeta-icono" aria-hidden="true">%s</span>' % icono,
              '          <span class="apartado-tarjeta-nombre">%s</span>' % nombre]
    if desc:
        partes.append('          <span class="apartado-tarjeta-desc">%s</span>' % desc)
    if dato:
        partes.append('          <span class="apartado-tarjeta-dato"><strong>%s</strong><span>%s</span></span>' % dato)
    partes.append('          <span class="apartado-tarjeta-accion">%s</span>' % accion)
    partes.append('        </a>')
    return '\n'.join(partes)


def pagina(a, sello):
    secciones = []
    for s in a['secciones']:
        num = ('<span class="apartado-cap-num" aria-hidden="true">%d</span>' % s['num']) if s.get('num') else ''
        titulo = ('Capítulo %d. ' % s['num'] if s.get('num') else '')
        ayer = ''
        if s.get('ayer'):
            ayer = '''
        <div class="apartado-ayer">
          <div><span class="apartado-ayer-tit">📘 En el libro (1995)</span>%s</div>
          <div><span class="apartado-ayer-tit">📍 Hoy (2026)</span>%s</div>
        </div>''' % s['ayer']
        bloque = ('\n        <div class="apartado-bloque">\n        %s\n        </div>' % s['bloque']) if s.get('bloque') else ''
        if s.get('sin_cab'):
            cab = '\n        <h2 class="sr-only" id="%s-tit">%s</h2>' % (s['id'], s['titulo'])
        elif s['titulo']:
            cab = '''
        <div class="apartado-seccion-cab">
          <h2 class="apartado-seccion-titulo" id="%s-tit">%s<span class="sr-only">%s</span>%s</h2>
          <p class="apartado-seccion-texto">%s</p>
        </div>''' % (s['id'], num, titulo, s['titulo'], s['texto'])
        else:
            cab = ''
        secciones.append('''      <section class="apartado-seccion%s" id="%s"%s%s>%s%s%s%s
      </section>''' % (' apartado-seccion-modulos' if s.get('modulos') else (' apartado-panel' if a.get('pestanas') else ''),
                       s['id'], (' aria-labelledby="%s-tit"' % s['id']) if cab else ' aria-label="Herramientas"',
                       ' role="tabpanel"' if a.get('pestanas') else '', cab, ayer, bloque,
                       ('\n        <div class="apartado-rejilla%s">\n%s\n        </div>' % (
                           ' apartado-rejilla-modulos' if s.get('modulos') else (' herr-rejilla' if s.get('sin_cab') else ''),
                           '\n'.join(tarjeta(t, s.get('modulos'), s.get('auto')) for t in s['tarjetas'])))
                       if s['tarjetas'] else ''))

    if a.get('pestanas'):
        botones = '\n'.join(
            '          <a class="apartado-pestana" role="tab" id="pestana-%s" href="#%s" aria-controls="%s" aria-selected="false">'
            '<span class="apartado-pestana-ico" aria-hidden="true">%s</span>'
            '<span class="apartado-pestana-tx"><b>%s</b><small>%s</small></span></a>'
            % ((s['id'], s['id'], s['id']) + s['pestana']) for s in a['secciones'])
        en_pagina = '''      <nav class="apartado-pestanas" role="tablist" aria-label="Pestañas de esta página"%s>
%s
      </nav>
      <p class="apartado-pestanas-pista" id="pestanasPista">Elige una pestaña para abrir su contenido.</p>''' % (
            ' data-primera="1"' if a.get('primera') else '', botones)
    elif len(a['secciones']) > 1:
        saltos = '\n'.join('          <a href="#%s">%s%s</a>' % (
            s['id'], ('<span class="apartado-cap-num" aria-hidden="true">%d</span>' % s['num']) if s.get('num') else '', s['titulo'])
            for s in a['secciones'])
        en_pagina = '''      <nav class="apartado-saltos" aria-label="En esta página">
          <span class="apartado-saltos-tit">En esta página:</span>
%s
      </nav>''' % saltos
    else:
        en_pagina = ''

    nota = ('<a class="apartado-nota" href="index.html?ir=nota">📖 Qué son las finanzas públicas y qué encontrarás aquí</a>'
            if a.get('nota') else '')
    guia = GUIA if a.get('guia') else ''
    guia_abajo = ''
    if a.get('guia') == 'abajo':
        guia, guia_abajo = '', '\n\n      ' + GUIA
    if a.get('libro_ref'):
        # Desde el 09-10-2026 la nota del libro ya no es un recuadro en la
        # pagina (decision del autor): es un enlace bajo la entrada que la
        # abre en la ventana lateral (apartados.js, data-libro).
        nota = (nota + ' ' if nota else '') + libro_enlace(a)
    elif a.get('libro'):
        guia = (guia + '\n      ' if guia else '') + libro_html(a)
    estilos = ''.join('\n  <link rel="stylesheet" href="assets/auditor/css/%s?v=%s">' % (css, sello) for css in a.get('estilos', []))
    scripts = ''.join('\n  <script src="assets/auditor/js/%s?v=%s"></script>' % (js, sello) for js in a.get('scripts', []))
    titulo_doc = '%s · Auditavisión' % re.sub('<[^>]+>', '', a['menu'])
    descripcion = re.sub('<[^>]+>', '', a['entrada'])
    padre = ('<a href="%s">%s</a> <span aria-hidden="true">›</span> ' % a['padre']) if a.get('padre') else ''
    if a.get('padre2'):
        padre += '<a href="%s">%s</a> <span aria-hidden="true">›</span> ' % a['padre2']
    cab_clase, cab_estilo = 'apartado-cab', ''
    if a.get('fondo'):
        cab_clase += ' herr-cab herr-foto rubro-%s' % a['rubro']
        nota = '<span class="herr-cab-credito">Imagen ilustrativa</span>' + nota
    pie_extra = ('\n\n      ' + a['pie_extra']) if a.get('pie_extra') else ''
    redirige = ''
    if a.get('hash_a_pagina'):
        # Anclas viejas que ahora son paginas: se mandan antes de pintar.
        redirige = ('\n  <script>(function () { var m = %s, h = location.hash.slice(1); '
                    'if (m[h]) location.replace(m[h]); })();</script>' % json.dumps(a['hash_a_pagina']))

    return '''<!DOCTYPE html>
<!-- Página generada por herramientas/apartados.py: no la edites a mano. -->
<html lang="es" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo_doc}</title>
  <meta name="description" content="{descripcion}">
  <meta name="theme-color" content="#0b2a63">
  <meta name="color-scheme" content="light">
  <link rel="icon" href="{favicon}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/auditor/css/auditavision.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/civico.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/apartados.css?v={sello}">{estilos}{redirige}
</head>
<body data-pagina="apartado">
{cabecera}

  <main class="apartado" id="contenido">
    <header class="{cab_clase}"{cab_estilo}>
      <div class="apartado-ancho">
        <nav class="apartado-migas" aria-label="Estás en"><a href="index.html">Inicio</a> <span aria-hidden="true">›</span> {padre}<span>{menu}</span></nav>
        <span class="apartado-lema">{icono}{lema}</span>
        <h1 class="apartado-titulo">{titulo}</h1>
        <p class="apartado-entrada">{entrada}</p>
        {nota}
      </div>
    </header>

    <div class="apartado-ancho apartado-cuerpo">
{antes}{en_pagina}
      {guia}
{secciones}{guia_abajo}{pie_extra}
    </div>
  </main>

  <footer class="apartado-pie">
    <div class="apartado-ancho">
      <a class="apartado-volver" href="index.html">← Volver al auditor</a>
      <a class="apartado-volver apartado-indice" href="indice.html">🗂️ Índice general</a>
      <span class="apartado-pie-txt">Auditavisión · Toda cifra lleva su fuente oficial. Versión publicada: <b>{sello}</b></span>
    </div>
  </footer>

  <script src="assets/auditor/js/apartados.js?v={sello}"></script>{scripts}
</body>
</html>
'''.format(titulo_doc=titulo_doc, descripcion=esc_attr(descripcion), favicon=FAVICON, sello=sello,
           cabecera=cabecera(a.get('menu_archivo', a['archivo']), sello), menu=a['menu'],
           padre=padre, cab_clase=cab_clase, cab_estilo=cab_estilo, pie_extra=pie_extra, redirige=redirige, icono='' if a.get('sin_icono_lema') else a['icono'] + ' ', lema=a['lema'],
           titulo=a['titulo'], entrada=a['entrada'], nota=nota, en_pagina=en_pagina, guia=guia, guia_abajo=guia_abajo, scripts=scripts, estilos=estilos, antes=(a['antes'] + '\n\n') if a.get('antes') else '',
           secciones='\n\n'.join(secciones))


# Indice general (entrega 2 de la propuesta de Astra, 10-10-2026): todo lo
# que tiene la plataforma en una sola pagina, por pestana y por tema, con la
# metodologia y las novedades. Se arma solo con las listas de este archivo y
# de auditorias.py: al agregar una pagina ahi, aparece aqui.
NOVEDADES = [
    ('10-10-2026', 'Índice general y portada con recorrido: cada investigación lleva a sus números y a su evidencia.'),
    ('10-10-2026', 'Becas de educación básica y media superior separadas, con aprobado y devengado verificados en la ASF.'),
    ('10-10-2026', 'El Circuito del Dinero se integró a Números, con el camino del dinero en cuatro pasos.'),
    ('10-10-2026', 'Cada herramienta se divide en módulos con página propia.'),
    ('10-10-2026', 'El Diccionario del Gasto Público, en dos estantes: Biblioteca hacendaria y Fuentes del auditor.'),
    ('09-10-2026', 'Los Expedientes de casos y el radar hacendario estrenan página; el menú queda en cinco pestañas.'),
]


def _grupo(icono, titulo, enlaces, href=None):
    cab = ('<a href="%s">%s %s</a>' % (href, icono, titulo)) if href else '%s %s' % (icono, titulo)
    filas = '\n'.join('              <li><a href="%s">%s</a>%s</li>' % (h, t, ('<span>%s</span>' % d) if d else '')
                      for h, t, d in enlaces)
    return ('          <div class="indice-grupo">\n            <h3 class="indice-grupo-tit">%s</h3>\n'
            '            <ul class="indice-lista">\n%s\n            </ul>\n          </div>' % (cab, filas))


def _rejilla(grupos):
    return '<div class="indice-grupos">\n%s\n        </div>' % '\n'.join(grupos)


def _a_numeros(destino):
    m = re.search(r'ir=presupuesto&(?:amp;)?ancla=(eb-[\w-]+)', destino)
    return 'sigue-el-dinero.html?abrir=' + m.group(1) if m else destino


def indice():
    import auditorias
    au = {a[0]: a for a in auditorias.AUDITORIAS}
    ap = {a['archivo']: a for a in APARTADOS}
    investigaciones = _rejilla([_grupo(ico, tit, [(auditorias.archivo(i), au[i][5], au[i][6]) for i in ids])
                                for ico, tit, ids in auditorias.TEMAS])
    num = ap['sigue-el-dinero.html']
    numeros = _rejilla([_grupo(s['pestana'][0], s['titulo'],
                               [(_a_numeros(t[3]), re.sub('<[^>]+>', '', t[1]), '') for t in s['tarjetas']],
                               'sigue-el-dinero.html#' + s['id'])
                        for s in num['secciones']])
    herr = _rejilla([_grupo(h[2], h[3], [(modulo_archivo(h[0], t[0]), t[2], t[3]) for t in h[7]], h[0])
                     for h in HERRAMIENTAS])
    otros = []
    for archivo in ('descarga-los-datos.html', 'aprende.html', 'participa.html'):
        a = ap[archivo]
        enl = [(archivo + '#' + x['id'], x['pestana'][1], x['pestana'][2]) for x in a['secciones']]
        if archivo == 'aprende.html':
            enl += [('diccionario.html', 'Diccionario del Gasto Público', 'La obra completa')] + [
                (b[0], b[2], '') for b in BIBLIOTECA]
        if archivo == 'participa.html':
            enl += [('expedientes.html', 'Expedientes de casos', 'Casos por aclarar')]
        otros.append(_grupo(a['icono'], a['menu'], enl, archivo))
    otros.append(_grupo('🏛️', 'Los Poderes', [
        ('index.html?ir=poderes', 'Lo que cuestan el Congreso y el Poder Judicial', 'Presupuesto 2026 y Cuenta Pública 2024')]))
    metodologia = (
        '<div class="indice-metodo">\n'
        '          <p>Toda cifra de la plataforma lleva su fuente oficial y uno de tres estados:</p>\n'
        '          <ul class="indice-lista indice-estados">\n'
        '            <li><span class="est-chip est-oficial">oficial</span> La tomamos tal cual de su documento (DOF, SHCP, ASF, INEGI, Banxico), con la liga para que la revises.</li>\n'
        '            <li><span class="est-chip est-derivado">derivado</span> La calculamos a partir de cifras oficiales y te decimos la operación.</li>\n'
        '            <li><span class="est-chip est-pendiente">pendiente</span> El dato no está en un documento que podamos citar. Decimos por qué y, si la dependencia obligada no lo ha publicado, la nombramos. Nunca lo estimamos.</li>\n'
        '          </ul>\n'
        '          <p>Las imágenes de las investigaciones son ilustraciones y lo dicen en una etiqueta: no son evidencia de ningún hecho. '
        'La evidencia está en los documentos del <a href="fuentes-oficiales.html">Compendio de Fuentes Oficiales</a>.</p>\n'
        '          <h3 class="indice-grupo-tit">🆕 Novedades</h3>\n'
        '          <ul class="indice-lista indice-novedades">\n%s\n          </ul>\n'
        '        </div>') % '\n'.join('            <li><b>%s</b> %s</li>' % n for n in NOVEDADES)
    secc = [
        ('investigaciones', '🖼️ Investigaciones, por tema', 'Las auditorías en imágenes. Cada una explica el caso y lleva a sus números y a su evidencia.', investigaciones),
        ('numeros', '💰 Números', 'El recorrido del dinero público, capítulo por capítulo.', numeros),
        ('herramientas', '🧰 Herramientas', 'Cada herramienta y sus módulos, con página propia.', herr),
        ('mas', '📚 Datos, Aprende, Participa y los Poderes', 'Descargas, la obra de consulta, la participación ciudadana y el costo de los Poderes.', _rejilla(otros)),
        ('metodologia', '🔎 Cómo verificamos', 'La regla que sigue cada cifra y lo último que cambió.', metodologia),
    ]
    return {
        'archivo': 'indice.html', 'menu': 'Índice general', 'menu_archivo': 'indice.html',
        'icono': '🗂️', 'titulo': 'Índice general', 'lema': 'Todo lo que hay en Auditavisión, en una página',
        'entrada': ('Aquí está el mapa completo de la plataforma: las investigaciones por tema, los capítulos de Números, '
                    'cada herramienta con sus módulos, los datos, la obra de consulta y cómo verificamos cada cifra. '
                    'Cada enlace abre su propia página.'),
        'secciones': [{'id': i, 'titulo': t, 'texto': x, 'tarjetas': [], 'bloque': b} for i, t, x, b in secc],
    }


# Paginas que dejaron de existir y redirigen a donde se mudo su contenido.
# Busca y verifica se fusiono con el Modo Inspector el 09-10-2026.
REDIRECCIONES = {
    'busca-y-verifica.html': ('herramienta-inspector-entes.html', 'Busca y verifica',
                              'Ahora vive dentro del Modo Inspector, en la parte «Busca y verifica».'),
}


def redireccion(destino, nombre, texto):
    return '''<!DOCTYPE html>
<!-- Página generada por herramientas/apartados.py: no la edites a mano. -->
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{nombre} · Auditavisión</title>
  <meta name="robots" content="noindex">
  <meta http-equiv="refresh" content="0; url={destino}">
  <link rel="icon" href="{favicon}">
  <script>window.location.replace('{url}');</script>
</head>
<body style="font-family:system-ui,sans-serif;background:#ffffff;color:#1c2a44;padding:24px">
  <p><b>{nombre}</b> cambió de lugar. {texto} <a href="{destino}">Ir ahora ➔</a></p>
</body>
</html>
'''.format(nombre=nombre, destino=destino, favicon=FAVICON, url=destino.replace('&amp;', '&'), texto=texto)


def generar(sello=None):
    if sello is None:
        d = open(os.path.join(RAIZ, 'index.html'), 'rb').read().decode('utf-8')
        m = re.search(r'id="selloVersion">([0-9a-z]+)<', d)
        if not m:
            print('ERROR: no encontré el sello en index.html')
            return 1
        sello = m.group(1)
    for a in APARTADOS:
        texto = pagina(a, sello).replace('\r\n', '\n').replace('\n', '\r\n')
        open(os.path.join(RAIZ, a['archivo']), 'wb').write(texto.encode('utf-8'))
    for n, h in enumerate(HERRAMIENTAS, 1):
        texto = pagina(herramienta(h, n), sello).replace('\r\n', '\n').replace('\n', '\r\n')
        open(os.path.join(RAIZ, h[0]), 'wb').write(texto.encode('utf-8'))
        for i, t in enumerate(h[7]):
            if t[0].endswith('.html'):
                continue
            m = herramienta_modulo(h, n, i)
            texto = pagina(m, sello).replace('\r\n', '\n').replace('\n', '\r\n')
            open(os.path.join(RAIZ, m['archivo']), 'wb').write(texto.encode('utf-8'))
    for extra in [DICCIONARIO, GLOSARIO, indice()] + PAGINAS_BIBLIOTECA:
        texto = pagina(extra, sello).replace('\r\n', '\n').replace('\n', '\r\n')
        open(os.path.join(RAIZ, extra['archivo']), 'wb').write(texto.encode('utf-8'))
    for archivo, datos in REDIRECCIONES.items():
        texto = redireccion(*datos).replace('\n', '\r\n')
        open(os.path.join(RAIZ, archivo), 'wb').write(texto.encode('utf-8'))
    print('apartados: %d páginas y %d herramientas generadas con el sello %s' % (len(APARTADOS), len(HERRAMIENTAS), sello))
    # Las paginas de Auditoria en imagenes comparten cabecera y sello.
    import auditorias
    import expedientes
    if auditorias.generar(sello):
        return 1
    return expedientes.generar(sello)


if __name__ == '__main__':
    sys.exit(generar())
