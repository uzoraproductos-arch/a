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


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%230c0e15'/%3E%3Cg stroke='%23c9a84c' stroke-width='3.2' stroke-linecap='round' fill='none'%3E%3Cpath d='M32 12v38'/%3E%3Cpath d='M20 50h24'/%3E%3Cpath d='M14 22h36'/%3E%3Cpath d='M14 22l-6 13a7 7 0 0 0 12 0z'/%3E%3Cpath d='M50 22l-6 13a7 7 0 0 0 12 0z'/%3E%3C/g%3E%3Ccircle cx='32' cy='12' r='3.4' fill='%23f3cf65'/%3E%3C/svg%3E")




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
    '        <h2 class="camino-tit" id="caminoTit">El camino del dinero, en cinco pasos</h2>\n'
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
        (5, '🧾', 'Se hace el balance',
         'El %s junta lo que entró, lo que se gastó, lo que se debe y lo que se perdió: 2024 frente a 2026 y 2027.' % (
             '<a href="estado-de-cuenta.html">Estado de Cuenta Cívico</a>'),
         'estado-de-cuenta.html', 'Ver el estado de cuenta'),
    ])


# Diccionario del Gasto Publico (10-10-2026): la obra entera, en dos
# estantes. «Biblioteca hacendaria» es para entender (glosario, marco legal,
# preguntas); «Fuentes del auditor» es para verificar (compendio de fuentes y
# pase). Cada entrada: (archivo, icono, nombre, frase, descripcion, estante).
# Desde el 10-10-2026 (decision del autor) Aprende tiene una sola pestana,
# «Diccionario del Gasto Publico», con dos tarjetas; cada estante abre su
# pagina (ESTANTES[i][5]) y cada apartado del estante, la suya:
#   Aprende › Diccionario › Estante › Apartado.
# Las pestanas de Aprende, la portada del Diccionario y la barra al pie de
# cada pagina salen de esta lista.
ESTANTES = [
    ('biblioteca', '🏛️', 'Biblioteca hacendaria', 'Para entender',
     'Las palabras, las leyes y las preguntas del dinero público, explicadas en lenguaje llano.',
     'biblioteca-hacendaria.html'),
    ('kit', '🧭', 'Fuentes del auditor', 'Para verificar',
     'Los documentos oficiales que sostienen cada cifra y el pase para sostener la plataforma.',
     'fuentes-del-auditor.html'),
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


def estante_de(archivo):
    return [e for e in ESTANTES if e[0] == [b for b in BIBLIOTECA if b[0] == archivo][0][5]][0]


def tarjetas_estantes():
    return [(e[1], e[2], '<b>%s.</b> %s Contiene: %s.' % (e[3], e[4], ', '.join(b[2] for b in BIBLIOTECA if b[5] == e[0])),
             e[5], None, None) for e in ESTANTES]


def bib_nav(actual):
    """Barra al pie de cada pagina del Diccionario, con sus dos estantes."""
    filas = []
    for e in ESTANTES:
        filas.append('          <a class="bib-nav-estante" href="%s"%s>%s %s</a>\n' % (
            e[5], ' aria-current="page"' if e[5] == actual else '', e[1], e[2]) + '\n'.join(
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
        'scripts': ['audit-database.js', 'municipios-efipem.js', 'datos.js'],
        # El radar y sus anclas viejas (#rc-*) llevan a su pagina.
        'hash_a_pagina': {'radar': 'radar-hacendario.html', 'rc-megaobras': 'radar-presupuesto-en-curso.html',
                          'rc-deuda': 'radar-presupuesto-en-curso.html', 'rc-asf': 'radar-presupuesto-en-curso.html',
                          'rc-huachicol': 'radar-presupuesto-en-curso.html'},
        # Desde el 09-10-2026 las secciones son pestanas y cada ficha se
        # despliega aqui mismo, con su contenido (decision del autor):
        # datos.js las arma. Ya no abren la portada.
        'pestanas': True,
        'secciones': [
            {
                # Desde el 10-10-2026 es su propia pagina (radar()): el
                # tablero de cada administracion, con su reloj y su duelo.
                'id': 'radar',
                'pagina': 'radar-hacendario.html',
                'pestana': ('📡', 'Radar hacendario', 'Cada administración, con sus números: abre su página'),
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
        # Las pestanas viejas del Diccionario (10-10-2026) llevan a su estante.
        'hash_a_pagina': {'biblioteca': 'biblioteca-hacendaria.html', 'kit': 'fuentes-del-auditor.html'},
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
                # Diccionario del Gasto Publico (decision del autor, 10-10-2026):
                # una sola pestana con sus dos estantes; cada uno abre su pagina.
                'id': 'diccionario',
                'pestana': ('📚', 'Diccionario del Gasto Público', 'Biblioteca hacendaria y fuentes del auditor'),
                'titulo': '📚 Diccionario del Gasto Público',
                'texto': ('La obra de consulta de la plataforma, en dos estantes: uno para entender y otro para verificar. '
                          'Cada estante abre su propia página y, dentro, cada apartado tiene la suya. '
                          '<a href="diccionario.html">Ver el Diccionario completo ➔</a>'),
                'tarjetas': tarjetas_estantes(),
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
        'hash_a_pagina': {'agora': 'agora.html', 'garantias': 'garantias.html'},
        'secciones': [
            {
                # Desde el 10-10-2026 el Agora es su propia pagina (agora()):
                # la pestana ya no despliega, abre agora.html.
                'id': 'agora',
                'pagina': 'agora.html',
                'pestana': ('💬', 'Ágora cívica', 'La red de réplica y diálogo: abre su página'),
            },
            {
                # Desde el 10-10-2026 es su propia pagina (garantias()): la
                # brujula de denuncia, las seis puertas, las diez garantias y
                # el reto. Lo que repetia Comunidad y el Agora se quito.
                'id': 'garantias',
                'pagina': 'garantias.html',
                'pestana': ('🛡️', 'Garantías cívicas', 'A qué puerta tocar y qué te protege: abre su página'),
            },
            {
                # Entrega 7 de la propuesta de Astra (10-10-2026).
                'id': 'comunidad',
                'pestana': ('🤝', 'Comunidad', 'Cuéntanos lo que viste, corrígenos, comparte'),
                'titulo': '🤝 Comunidad: cuéntanos lo que viste',
                'texto': 'La plataforma mejora con quien la lee. Son las mismas tres rutas del botón «📢 Cuéntanos lo que viste» de la cabecera, más la fe de erratas y el botón para compartir.',
                'tarjetas': [
                    ('🏗️', 'Algo raro con el dinero público', 'Una obra que no cuadra, un contrato, un programa usado en campaña, un cobro indebido.', 'comunidad.html#reporta', None, None),
                    ('✏️', 'Un dato mal en esta plataforma', 'Un dato que no coincide con su documento oficial. Si tienes razón, se corrige en público.', 'comunidad.html#error', None, None),
                    ('💡', 'Un tema para investigar', 'Lo que te gustaría que investigáramos, con los documentos que conozcas.', 'comunidad.html#tema', None, None),
                    ('📣', 'Comparte el Estado de Cuenta', 'Un enlace para que más gente vea de dónde sale el dinero público y en qué se gasta.', 'comunidad.html#compartir', None, None),
                    ('📋', 'Fe de erratas', 'Cada corrección que hemos hecho: qué estaba mal y qué cambió.', 'comunidad.html#erratas', None, None),
                ],
            },
            {
                # Entrega 6 de la propuesta de Astra (10-10-2026): el Pase
                # convive con los Servicios (decision del autor).
                'id': 'servicios',
                'pestana': ('🔎', 'Servicios', 'Investigación a la medida y Pase del Auditor'),
                'titulo': '🔎 Servicios y Pase del Auditor',
                'texto': 'La consulta es gratuita. Si necesitas ir más a fondo, pide una investigación; si quieres sostener la plataforma, súmate con el Pase. Ambos se abren con el lanzamiento.',
                'tarjetas': [
                    ('🔎', 'Solicita una investigación', 'Revisión documental, expediente, seguimiento, capacitación o licencia, para quien sea y con la misma regla de la plataforma y su política de independencia.', 'servicios.html', None, None),
                    ('🍺', 'Pase del Auditor Cívico', 'Sostén la plataforma independiente: plan mensual o anual.', 'pase-del-auditor.html', None, None),
                ],
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
         ('simulador-presupuesto.html', '🧮', 'Reparte el presupuesto', 'Desde cero',
          'Empieza en $0: agrega lo que entra, reparte a dónde va, carga el ejemplo oficial de 2026 o 2027, compara dos escenarios y descarga la cuenta. Tiene su propia página.'),
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
         ('inspverifica', '🔏', 'Verifica un estado de cuenta', 'Busca y verifica',
          '¿Te compartieron un estado de cuenta de Auditavisión? Escribe su folio o su huella digital y comprueba, cifra por cifra, que no se alteró.'),
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


# Modulos que no abren la portada en un marco: su pagina la arma otra funcion
# (la verificacion de estados de cuenta, en radar()).
MODULOS_PROPIOS = {'inspverifica'}
VERIFICA_PAGINA = 'herramienta-inspector-verifica.html'


def modulo_archivo(archivo, clave):
    """Pagina propia de un modulo: herramienta-megaobras.html + pulso ->
    herramienta-megaobras-pulso.html (sin el prefijo insp, cc o am)."""
    if clave.endswith('.html'):
        return clave
    return archivo[:-5] + '-' + re.sub(r'^(insp|cc|am)', '', clave) + '.html'


# Para buscadores y para compartir (propuesta de Astra, punto 8; entrega 5,
# 10-10-2026): cada pagina dice su direccion estable y su tarjeta social.
SITIO = 'https://uzoraproductos-arch.github.io/a/'


def sociales(archivo, titulo, descripcion, imagen=None):
    d = esc_attr(re.sub('<[^>]+>', '', descripcion))
    filas = ['<link rel="canonical" href="%s">' % (SITIO + archivo),
             '<meta property="og:type" content="article">',
             '<meta property="og:site_name" content="Auditavisión">',
             '<meta property="og:locale" content="es_MX">',
             '<meta property="og:url" content="%s">' % (SITIO + archivo),
             '<meta property="og:title" content="%s">' % esc_attr(titulo),
             '<meta property="og:description" content="%s">' % d]
    if imagen:
        filas.append('<meta property="og:image" content="%s">' % (SITIO + imagen))
    filas.append('<meta name="twitter:card" content="%s">' % ('summary_large_image' if imagen else 'summary'))
    return '\n'.join('  ' + f for f in filas)


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
    'padre': ('aprende.html#diccionario', 'Aprende'),
    'icono': '📚',
    'titulo': 'Diccionario del Gasto Público',
    'lema': 'Las palabras, las leyes y las fuentes del erario',
    'entrada': ('La obra de consulta de la plataforma, en dos estantes. La <b>Biblioteca hacendaria</b> es para entender: '
                'el glosario, el marco legal con su texto vigente y las preguntas frecuentes. Las <b>Fuentes del auditor</b> son '
                'para verificar: el compendio de fuentes oficiales que sostiene cada cifra y el pase del auditor cívico. '
                'Cada estante abre su propia página y, dentro, cada apartado tiene la suya.'),
    'hash_a_pagina': {'preguntas': 'preguntas-frecuentes.html', 'glosario': 'glosario.html',
                      'biblioteca': 'biblioteca-hacendaria.html', 'kit': 'fuentes-del-auditor.html',
                      'marco-legal': 'marco-legal.html', 'fuentes': 'fuentes-oficiales.html',
                      'referencias': 'fuentes-oficiales.html', 'pase': 'pase-del-auditor.html'},
    'secciones': [{
        'id': 'estantes', 'titulo': 'Los dos estantes',
        'texto': 'Elige un estante: cada uno abre su página con sus apartados.',
        'tarjetas': tarjetas_estantes(),
    }],
}


def pagina_estante(e):
    """Pagina de un estante del Diccionario (10-10-2026): sus apartados en tarjetas."""
    return {
        'archivo': e[5], 'menu': e[2], 'menu_archivo': 'aprende.html',
        'padre': ('aprende.html#diccionario', 'Aprende'),
        'padre2': ('diccionario.html', 'Diccionario del Gasto Público'),
        'icono': e[1], 'titulo': e[2], 'lema': e[3], 'entrada': e[4] + ' Cada apartado abre su propia página.',
        'secciones': [{'id': 'apartados', 'titulo': 'Los apartados', 'texto': '', 'sin_cab': True,
                       'tarjetas': bib_estante(e[0])}],
        'pie_extra': bib_nav(e[5]),
    }


PAGINAS_ESTANTE = [pagina_estante(e) for e in ESTANTES]


def simulador():
    """Reparte el presupuesto, desde cero (propuesta de Astra, punto 6;
    entrega 4, 10-10-2026). Lo pinta assets/auditor/js/simulador-cero.js; el
    ejemplo oficial sale de investigaciones/simulador/cgpe2027-cuadro-ii6.json,
    que escribe herramientas/extraer_simulador.py desde el PDF."""
    ej = json.load(open(os.path.join(RAIZ, 'investigaciones', 'simulador', 'cgpe2027-cuadro-ii6.json'), encoding='utf-8'))
    datos = json.dumps(ej, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return {
        'archivo': 'simulador-presupuesto.html', 'menu': 'Reparte el presupuesto', 'menu_archivo': 'herramientas.html',
        'padre': ('herramientas.html', 'Herramientas'),
        'padre2': ('herramienta-calculadora.html', 'Calculadora Cívica'),
        'icono': '🧮', 'titulo': 'Reparte el presupuesto, desde cero', 'lema': 'Tú pones las cifras; el ejemplo oficial, Hacienda',
        'entrada': ('Un simulador que empieza en $0. Agrega lo que entra y a dónde va, reparte, compara dos escenarios y descarga la cuenta. '
                    'Si quieres partir de cifras reales, carga el ejemplo oficial: el presupuesto aprobado de 2026 o el estimado de 2027, '
                    'renglón por renglón, del cuadro II.6 de los Criterios Generales de Política Económica 2027.'),
        'scripts': ['simulador-cero.js'],
        'secciones': [{
            'id': 'simulador', 'titulo': 'El simulador', 'texto': '', 'sin_cab': True, 'tarjetas': [],
            'bloque': ('<div class="sz" id="simCero">\n'
                       '          <noscript><p>El simulador necesita JavaScript.</p></noscript>\n'
                       '        </div>\n'
                       '        <script type="application/json" id="simEjemplo">%s</script>' % datos),
        }],
        'pie_extra': herr_otras('herramienta-calculadora.html'),
    }


# Servicios de investigacion (propuesta de Astra, puntos 9 a 11; entrega 6,
# 10-10-2026). Decision del autor: el Pase del Auditor convive con los
# Servicios. El Pase sostiene la consulta gratuita; los Servicios son trabajo
# a la medida que se cotiza. La pagina queda lista para el lanzamiento: el
# formulario arma la solicitud en el navegador (servicios.js) y no envia ni
# guarda nada mientras no haya canal. Para abrirlo, pon aqui la direccion
# (por ejemplo 'mailto:investigaciones@tu-dominio.mx') y corre sello.py.
CANAL_SOLICITUD = ''

SERVICIOS = [
    ('revision', '📄', 'Revisión documental puntual',
     'Una pregunta delimitada, revisada contra los documentos públicos que la responden.',
     'Hallazgos, fuentes y límites de la revisión.', 'Periodistas, organizaciones, despachos y empresas.'),
    ('expediente', '🗂️', 'Expediente de investigación',
     'Un caso completo: quién, cuánto, cuándo y qué documento lo acredita.',
     'Cronología, documentos, relaciones verificadas y análisis de inconsistencias.', 'Medios, organizaciones, equipos profesionales y dependencias públicas.'),
    ('seguimiento', '📡', 'Seguimiento periódico',
     'Vigilancia de un tema que cambia: contratos, proveedores, presupuesto o auditorías.',
     'Reporte de cambios relevantes con su documento.', 'Quien necesita estar al día de un tema de forma recurrente.'),
    ('capacitacion', '🎓', 'Capacitación',
     'Talleres para leer el presupuesto y usar las herramientas de la plataforma.',
     'Taller de interpretación presupuestaria y uso del Modo Inspector.', 'Universidades públicas y privadas, organizaciones, equipos de trabajo y dependencias de gobierno.'),
    ('licencia', '🔑', 'Licencia de las herramientas',
     'El uso de las herramientas y los datos de la plataforma dentro de tu institución.',
     'Licencia de uso, adaptación y acompañamiento.', 'Dependencias de gobierno, universidades, medios y organizaciones.'),
]

PROCESO = [
    ('📝', 'Solicitud', 'Nos cuentas qué quieres saber con el formulario de abajo.'),
    ('🎯', 'Alcance', 'Acordamos la pregunta, el periodo, el territorio y lo que queda fuera.'),
    ('💬', 'Cotización', 'Recibes por escrito el costo y el plazo antes de empezar. Si no te conviene, ahí termina.'),
    ('🔍', 'Investigación', 'Revisamos documentos públicos con la misma regla de la plataforma.'),
    ('✅', 'Revisión', 'Una segunda persona coteja cada cifra contra su documento.'),
    ('📦', 'Entrega', 'Recibes el entregable con sus fuentes, sus etiquetas y sus límites.'),
    ('🔁', 'Seguimiento', 'Resolvemos dudas y, si lo pediste, seguimos el tema.'),
]

INDEPENDENCIA = [
    ('La consulta cívica es gratuita y lo seguirá siendo.',
     'Ningún dato publicado en la plataforma se esconde detrás de un pago. El Pase del Auditor, los Servicios, las licencias y las donaciones sostienen el trabajo; no compran acceso a la información pública.'),
    ('Abierta a todos, con las mismas reglas para todos.',
     'Pueden usarla, contratar un servicio o licenciar sus herramientas la ciudadanía, organizaciones, medios, empresas, universidades públicas y privadas y también gobiernos y dependencias. Nadie queda excluido; nadie tiene trato especial.'),
    ('Lo que no está en venta: las conclusiones y lo que publicamos.',
     'Ningún cliente, donante, gobierno ni partido puede pedir que se retire, se suavice o se retrase una publicación, ni decidir qué se investiga en la plataforma pública.'),
    ('Quien encarga define la pregunta, no la respuesta.',
     'Si los documentos no sostienen lo que esperabas encontrar, el entregable lo dice. Las conclusiones no se negocian.'),
    ('Los conflictos de interés se dicen antes de empezar.',
     'Si quien solicita es parte del caso (proveedor, dependencia o persona servidora pública involucrada, o contraparte en un litigio), se señala en la cotización. Si compromete la independencia, el encargo se declina.'),
    ('Las donaciones no compran contenido.',
     'Se agradecen y se reciben de cualquiera que comparta el propósito, pero no dan derecho a decidir qué se investiga, qué se publica ni cómo se dice.'),
    ('La misma regla para todo.',
     'Cada cifra lleva su documento y una de tres etiquetas: oficial, derivado o pendiente. Lo que no se puede sostener se queda pendiente, también en un encargo.'),
    ('Es investigación documental y análisis de indicios, no un dictamen.',
     'Revisamos documentos públicos y señalamos inconsistencias. No es un peritaje, no es asesoría legal y no acusa a nadie de un delito: eso le corresponde a las autoridades. Un encargo que requiera dictamen pericial se cotiza aparte, con su alcance, su metodología y su responsable profesional.'),
    ('De qué respondemos y de qué no.',
     'Respondemos de que cada dato coincida con el documento oficial que citamos, y si nos equivocamos lo corregimos en público, diciendo qué cambió. No respondemos del contenido de los documentos oficiales, que es de la dependencia que los emite, ni de las decisiones que alguien tome con la información.'),
    ('Solo fuentes lícitas.',
     'Documentos públicos y solicitudes de acceso a la información. No obtenemos datos personales ni información reservada por vías indebidas.'),
    ('Nuestro método y nuestras herramientas son nuestros.',
     'El entregable de un encargo es de quien lo encarga. Las herramientas, el método y la base de la plataforma son de Auditavisión: se pueden licenciar, pero una licencia no da control sobre lo que la plataforma publica.'),
    ('Tus datos y tu encargo son confidenciales.',
     'No publicamos quién encargó qué sin su permiso, y lo que la plataforma publique después sale solo de fuentes públicas.'),
    ('Rendimos cuentas de cómo nos sostenemos.',
     'Cada año publicaremos cuántos encargos recibimos, por tipo de cliente (incluidos los gobiernos), y cuánto entró por cada vía: Pase, Servicios, licencias y donaciones. Si el gobierno falla en transparentar, nosotros ponemos el ejemplo.'),
]


def servicios():
    oferta = '\n'.join(
        '          <article class="sv-servicio" id="sv-%s">\n'
        '            <span class="sv-ico" aria-hidden="true">%s</span>\n'
        '            <h3 class="sv-tit">%s</h3>\n'
        '            <p class="sv-que">%s</p>\n'
        '            <dl class="sv-dl"><dt>Entregable</dt><dd>%s</dd><dt>Para quién</dt><dd>%s</dd></dl>\n'
        '          </article>' % s for s in SERVICIOS)
    pasos = '\n'.join(
        '          <li class="sv-paso"><span class="sv-paso-num" aria-hidden="true">%d</span>'
        '<span class="sv-paso-ico" aria-hidden="true">%s</span><b>%s</b><span>%s</span></li>' % ((n,) + p)
        for n, p in enumerate(PROCESO, 1))
    politica = '\n'.join('            <li><b>%s</b> %s</li>' % p for p in INDEPENDENCIA)
    opciones = '\n'.join('                <option value="%s">%s</option>' % (s[0], s[2]) for s in SERVICIOS)
    campo = lambda i, et, ctl, ayuda='': (
        '            <div class="sv-campo"><label for="%s">%s</label>%s%s</div>'
        % (i, et, ctl, ('<small id="%s-ay">%s</small>' % (i, ayuda)) if ayuda else ''))
    formulario = '\n'.join([
        '<form class="sv-form" id="svForm" data-canal="%s" novalidate>' % esc_attr(CANAL_SOLICITUD),
        '          <p class="sv-privado">🔒 Esta página no guarda ni envía nada por su cuenta: tu solicitud se arma en tu navegador y tú decides cuándo mandarla.</p>',
        '          <fieldset class="sv-grupo"><legend>Qué quieres investigar</legend>',
        campo('svServicio', 'Servicio', '<select id="svServicio" name="servicio">\n%s\n                <option value="no-se">No sé, ayúdenme a definirlo</option>\n              </select>' % opciones),
        campo('svTema', 'Tema <span class="sv-req">obligatorio</span>', '<input id="svTema" name="tema" type="text" maxlength="160" required aria-describedby="svTema-ay">',
              'Por ejemplo: la compra de medicamentos de un hospital, un contrato de obra, el Ramo 33 de tu municipio.'),
        campo('svPregunta', 'Tu pregunta <span class="sv-req">obligatorio</span>', '<textarea id="svPregunta" name="pregunta" rows="4" maxlength="1500" required aria-describedby="svPregunta-ay"></textarea>',
              'Entre más concreta, mejor: «¿A quién se le pagó y cuánto?» rinde más que «investiguen todo».'),
        '            <div class="sv-dos">',
        campo('svAmbito', 'Ámbito', '<select id="svAmbito" name="ambito"><option>Federal</option><option>Estatal</option><option>Municipal</option><option>Varios</option></select>'),
        campo('svLugar', 'Entidad o municipio', '<input id="svLugar" name="lugar" type="text" maxlength="120">'),
        '            </div>',
        '            <div class="sv-dos">',
        campo('svPeriodo', 'Periodo', '<input id="svPeriodo" name="periodo" type="text" maxlength="60" placeholder="2019 a 2024">'),
        campo('svPlazo', 'Para cuándo lo necesitas', '<input id="svPlazo" name="plazo" type="text" maxlength="60">'),
        '            </div>',
        campo('svDocs', 'Documentos que ya tienes', '<textarea id="svDocs" name="documentos" rows="2" maxlength="800"></textarea>',
              'Ligas, números de contrato o de auditoría. Es opcional.'),
        '          </fieldset>',
        '          <fieldset class="sv-grupo"><legend>Quién lo solicita</legend>',
        '            <div class="sv-dos">',
        campo('svNombre', 'Nombre u organización <span class="sv-req">obligatorio</span>', '<input id="svNombre" name="nombre" type="text" maxlength="120" required autocomplete="name">'),
        campo('svCorreo', 'Correo para responderte <span class="sv-req">obligatorio</span>', '<input id="svCorreo" name="correo" type="email" maxlength="160" required autocomplete="email">'),
        '            </div>',
        campo('svUso', 'Para qué lo usarás', '<select id="svUso" name="uso"><option>Periodismo</option><option>Organización civil</option><option>Empresa o despacho</option><option>Universidad o academia</option><option>Gobierno o dependencia</option><option>Uso personal</option><option>Otro</option></select>'),
        '            <div class="sv-campo" role="radiogroup" aria-labelledby="svParteEt"><span class="sv-et" id="svParteEt">¿Eres parte del caso? <span class="sv-req">obligatorio</span></span>',
        '              <label class="sv-radio"><input type="radio" name="parte" value="No"> No</label>',
        '              <label class="sv-radio"><input type="radio" name="parte" value="Sí"> Sí (proveedor, persona servidora pública involucrada o contraparte en un litigio)</label>',
        '            </div>',
        '          </fieldset>',
        '          <label class="sv-check"><input type="checkbox" id="svPolitica" required> Leí la <a href="#independencia">política de independencia</a>.</label>',
        '          <label class="sv-check"><input type="checkbox" id="svAlcance" required> Entiendo que es investigación documental y análisis de indicios, no un dictamen pericial ni asesoría legal.</label>',
        '          <div class="sv-acciones"><button type="submit" class="sz-btn sz-btn-of">Revisar mi solicitud</button>'
        '<button type="reset" class="sz-btn">Empezar de nuevo</button></div>',
        '          <p class="sv-error" id="svError" role="alert" hidden></p>',
        '        </form>',
        '        <div class="sv-resumen" id="svResumen" hidden></div>',
        '        <noscript><p>El formulario necesita JavaScript.</p></noscript>'])
    return {
        'archivo': 'servicios.html', 'menu': 'Servicios', 'menu_archivo': 'participa.html',
        'padre': ('participa.html#servicios', 'Participa'),
        'icono': '🔎', 'titulo': 'Servicios de investigación', 'lema': 'La consulta es gratuita; la investigación a la medida se cotiza',
        'entrada': ('Todo lo que publica Auditavisión es libre y lo seguirá siendo. Cuando necesites ir más a fondo en un caso, '
                    'podemos hacer por encargo una investigación documental con la misma regla de la plataforma: cada cifra con '
                    'su documento y su etiqueta. Convive con el <a href="pase-del-auditor.html">Pase del Auditor</a>: el Pase '
                    'sostiene la consulta gratuita, los Servicios son trabajo a la medida y, cuando se abran, las donaciones '
                    'también ayudan. Ninguna de las tres vías compra lo que publicamos.'),
        'estilos': ['servicios.css'],
        'scripts': ['servicios.js'],
        'antes': ('      <p class="sv-aviso"><span class="sz-et">Próximamente</span> Los Servicios se abren con el lanzamiento de la '
                  'plataforma. Ya puedes armar tu solicitud y guardarla; el envío se activa entonces.</p>'),
        'secciones': [
            {'id': 'oferta', 'titulo': 'Qué podemos investigar', 'texto': 'Cinco servicios, de una pregunta puntual a una licencia para tu institución.',
             'tarjetas': [], 'bloque': '<div class="sv-servicios">\n%s\n        </div>' % oferta},
            {'id': 'proceso', 'titulo': 'Cómo trabajamos', 'texto': 'Siete pasos. Nada se cobra antes de que aceptes la cotización.',
             'tarjetas': [], 'bloque': '<ol class="sv-pasos">\n%s\n        </ol>' % pasos},
            {'id': 'precio', 'titulo': 'Cuánto cuesta', 'texto': 'Cada encargo se cotiza por escrito antes de empezar.', 'tarjetas': [],
             'bloque': ('<div class="sv-precio">\n'
                        '          <p>Todavía no hay tarifa publicada, y no vamos a inventarla: las primeras saldrán de encargos piloto. '
                        'Cuando las haya, se publicarán aquí. La cotización se arma con cuatro cosas:</p>\n'
                        '          <ul class="sv-lista"><li>las horas de investigación y de revisión;</li>'
                        '<li>el costo de las fuentes (copias certificadas, bases de datos o trámites);</li>'
                        '<li>la forma de entrega;</li><li>un margen para sostener la plataforma.</li></ul>\n'
                        '        </div>')},
            {'id': 'independencia', 'titulo': 'Política de independencia', 'texto': '%d compromisos que valen para cada cliente y cada donante, sin excepción.' % len(INDEPENDENCIA),
             'tarjetas': [], 'bloque': '<div class="sv-politica">\n          <ol class="sv-pol">\n%s\n          </ol>\n'
                                       '          <p class="sv-version">Versión 2 · 10 de octubre de 2026.</p>\n        </div>' % politica},
            {'id': 'solicitud', 'titulo': 'Solicita una investigación', 'texto': 'Cuéntanos qué quieres saber. Te mostramos tu solicitud antes de mandarla.',
             'tarjetas': [], 'bloque': formulario},
        ],
    }


# Comunidad, primera version (propuesta de Astra, punto 11; entrega 7,
# 10-10-2026): proponer temas, senalar errores y compartir el estado de
# cuenta. Sin perfiles, comentarios ni cuentas: eso necesita servidor. Los
# formularios los arma assets/auditor/js/comunidad.js en el navegador y no
# envian nada mientras CANAL_COMUNIDAD este vacio (se abre con el dominio,
# igual que CANAL_SOLICITUD). Cada pagina lleva al pie «¿Viste un error?».
CANAL_COMUNIDAD = ''

# Fe de erratas: correcciones reales, documentadas en CONTEXT.md. Politica
# de independencia, compromiso «De que respondemos»: se corrige en publico
# diciendo que cambio. (fecha, donde, que estaba mal, que se hizo, enlace)
ERRATAS = [
    ('10-10-2026', 'Calculadora Cívica',
     'El comparador «Tú contra ellos» usaba un ingreso de referencia de $15,000 que no salía de ningún documento.',
     'Se retiró. Ahora, si no escribes tu ingreso, usa el salario mínimo general mensual de 2026 ($9,451.20, CONASAMI), rotulado como ejemplo oficial.',
     'herramienta-calculadora.html'),
    ('10-10-2026', 'Tren Maya',
     'El recuadro del peritaje mostraba 515,487 mdp sin cotejo contra su documento.',
     'Se retiró la cifra; el dato quedó como retirado, con su motivo y el enlace al expediente de la Auditoría Superior.',
     'auditoria-tren-maya.html'),
    ('10-10-2026', 'Programas sociales',
     'La pensión (S176) mostraba 465,048 mdp como devengado, cuando es el aprobado; IMSS-Bienestar traía 128,900 mdp sin documento; las becas eran un solo renglón de 87,540 mdp sin documento.',
     'Se retiraron las tres. Las becas se separaron en S072 y S311 con aprobado y devengado de la Cuenta Pública 2024; la pensión e IMSS-Bienestar quedaron pendientes.',
     'pendientes.html'),
    ('09-10-2026', 'Marco legal hacendario',
     'Había dos «preceptos» de la Ley de Ingresos que no existen, y la extinción de los fideicomisos judiciales se atribuía al transitorio Cuarto, con «13 fideicomisos» y «$15,434 mdp» que el decreto no menciona.',
     'Se retiraron los dos preceptos, se corrigió el transitorio (es el Décimo) y se quitaron las cifras. Cada precepto se cotejó palabra por palabra con su texto vigente.',
     'marco-legal.html'),
    ('27-09-2026', 'Personajes relevantes',
     'Las fichas de personajes de la antigua Enciclopedia no citaban fuentes.',
     'Se retiraron. Lo que se rescató después se verificó afirmación por afirmación contra documentos oficiales.',
     None),
]


def _campo_cm(i, et, ctl, ayuda=''):
    return ('            <div class="sv-campo"><label for="%s">%s</label>%s%s</div>'
            % (i, et, ctl, ('<small>%s</small>' % ayuda) if ayuda else ''))


def _form_cm(id_, asunto, campos, boton):
    return '\n'.join([
        '<form class="sv-form cm-form" id="%s" data-canal="%s" data-asunto="%s" novalidate>' % (id_, esc_attr(CANAL_COMUNIDAD), esc_attr(asunto)),
        '\n'.join(campos),
        '          <div class="sv-acciones"><button type="submit" class="sz-btn sz-btn-of">%s</button>'
        '<button type="reset" class="sz-btn">Empezar de nuevo</button></div>' % boton,
        '          <p class="sv-error cm-error" role="alert" hidden></p>',
        '        </form>',
        '        <div class="sv-resumen cm-resumen" hidden></div>'])


def formas(pre):
    """Los tres formularios de «Cuéntanos lo que viste» (fusion del 10-10-2026:
    el cajon de la cabecera y la pagina comunidad.html usan los mismos). pre
    distingue los id: 'cm' en la pagina, 'pt' en el cajon de cada pagina."""
    ob = ' <span class="sv-req">obligatorio</span>'
    privado = ('          <p class="sv-privado">🔒 Nada se envía ni se guarda por su cuenta: el texto se arma en tu navegador. '
               'Puedes firmar con seudónimo; el correo es opcional y solo sirve para responderte.</p>')

    def c(sufijo, et, ctl, ayuda=''):
        i = pre + sufijo
        return _campo_cm(i, et, ctl.replace('{id}', i), ayuda)

    def firma(p):
        return [c(p + 'Firma', 'Firma o seudónimo', '<input id="{id}" type="text" maxlength="80">'),
                c(p + 'Correo', 'Correo (opcional)', '<input id="{id}" type="email" maxlength="160">')]
    reporte = _form_cm(pre + 'Reporte', 'Reporte ciudadano', [privado,
        '          <p class="sv-privado pt-aviso">⚠️ No escribas datos bancarios, documentos de identidad ni información de terceros que pueda ponerlos en riesgo.</p>',
        c('RepQue', 'Qué fue' + ob, '<select id="{id}" required><option value="">Elige una opción</option>'
          '<option>Una obra que no cuadra</option><option>Un contrato o una compra sospechosa</option>'
          '<option>Uso electoral de un programa social</option><option>Un cobro o trámite indebido</option>'
          '<option>Una duda sobre gasto o presupuesto</option></select>'),
        c('RepDonde', 'Dónde' + ob, '<input id="{id}" type="text" maxlength="200" required>',
          'Entidad, municipio, colonia y una referencia física. Una dirección vale más que un adjetivo.'),
        c('RepCuando', 'Cuándo', '<input id="{id}" type="text" maxlength="80">',
          'La fecha o el periodo: los fondos se fiscalizan por ejercicio anual.'),
        c('RepVio', 'Qué viste' + ob, '<textarea id="{id}" rows="4" maxlength="1500" required></textarea>',
          'La obra, el contrato, el programa o el trámite, con su nombre tal como aparece en la placa o en el recibo.'),
        c('RepDinero', 'Con qué dinero', '<input id="{id}" type="text" maxlength="160">',
          'Si lo sabes: Ramo 33, FISMDF, FORTAMUN, recurso estatal o propio del municipio.'),
        c('RepPrueba', 'Con qué prueba', '<input id="{id}" type="text" maxlength="300">',
          'Una foto con fecha, un número de contrato, una factura, un acta de entrega.'),
        ] + firma('Rep'), 'Revisar mi reporte')
    tema = _form_cm(pre + 'Tema', 'Propuesta de tema', [privado,
        c('TemaQue', 'Tema' + ob, '<input id="{id}" type="text" maxlength="160" required>',
          'Por ejemplo: las compras de un hospital, una obra de tu municipio, un fideicomiso.'),
        c('TemaPor', 'Por qué importa' + ob, '<textarea id="{id}" rows="3" maxlength="1200" required></textarea>'),
        c('TemaDonde', 'Entidad o municipio', '<input id="{id}" type="text" maxlength="120">'),
        c('TemaDocs', 'Documentos oficiales que conozcas', '<textarea id="{id}" rows="2" maxlength="800"></textarea>',
          'Ligas a la Auditoría Superior, Compranet, el DOF o Transparencia. Si no tienes, no pasa nada.'),
        ] + firma('Tema'), 'Revisar mi propuesta')
    error = _form_cm(pre + 'Error', 'Señalamiento de error', [privado,
        c('ErrPagina', 'Página' + ob, '<input id="{id}" class="cm-pagina" type="text" maxlength="200" required>',
          'Si abriste esto desde una página, ya está escrita.'),
        c('ErrDato', 'Qué dato está mal' + ob, '<textarea id="{id}" rows="2" maxlength="800" required></textarea>'),
        c('ErrDice', 'Qué dice el documento oficial' + ob, '<textarea id="{id}" rows="2" maxlength="800" required></textarea>'),
        c('ErrFuente', 'Enlace al documento' + ob, '<input id="{id}" type="url" maxlength="400" required placeholder="https://">',
          'Sin documento no podemos corregir: es la misma regla que seguimos nosotros.'),
        ] + firma('Err'), 'Revisar mi señalamiento')
    return {'reporta': reporte, 'tema': tema, 'error': error}


# Las tres rutas de «Cuéntanos lo que viste» (id, icono, titulo, para que).
RUTAS = [
    ('reporta', '🏗️', 'Algo raro con el dinero público',
     'Una obra que no cuadra, un contrato o una compra sospechosa, un programa social usado en campaña, un cobro indebido.'),
    ('error', '✏️', 'Un dato mal en esta plataforma',
     'Una cifra que no coincide con su documento oficial. Si tienes razón, se corrige y entra a la fe de erratas.'),
    ('tema', '💡', 'Un tema que deberíamos investigar',
     'Lo que te gustaría que revisáramos, con los documentos que conozcas.'),
]
DENUNCIA = ('Esto ordena tu reporte, pero <b>no es una denuncia</b>. La única vía con efecto jurídico es un canal oficial: '
            '<a href="garantias.html">la brújula de las seis puertas</a> te dice cuál toca, si admite anonimato '
            'y qué tener a la mano.')

RUTA_HTML = '''      <details class="pt-ruta" name="pt-ruta" data-ruta="{id}">
        <summary><span class="pt-ico" aria-hidden="true">{ico}</span><span class="pt-sum"><b>{tit}</b><span>{que}</span></span></summary>
        <div class="pt-ruta-cuerpo">
        {form}{extra}
        </div>
      </details>'''

PUERTA_HTML = '''  <div class="pt-velo" id="ptVelo" hidden></div>
  <aside class="pt-cajon" id="ptCajon" role="dialog" aria-modal="true" aria-labelledby="ptTit" hidden>
    <div class="pt-cab">
      <div>
        <span class="pt-kicker">📢 Cuéntanos lo que viste</span>
        <h2 class="pt-tit" id="ptTit">¿Qué viste?</h2>
        <p class="pt-sub">Elige una ruta. Nada se envía ni se guarda por su cuenta: el texto se arma en tu navegador y tú decides si lo copias, lo descargas o nos lo mandas.</p>
      </div>
      <button type="button" class="pt-cerrar" data-pt-cerrar aria-label="Cerrar">✕</button>
    </div>
    <div class="pt-cuerpo">
{rutas}
      <p class="pt-pie">Todo esto vive también en su página: <a href="comunidad.html">Comunidad</a> · <a href="comunidad.html#erratas">Fe de erratas</a> · <a href="garantias.html">Garantías cívicas: a qué puerta tocar</a></p>
    </div>
  </aside>'''


def puerta():
    """«Cuéntanos lo que viste»: la unica puerta para escribirnos (fusion del
    10-10-2026 con «¿Viste un error?», que estaba al pie). El boton de la
    cabecera abre este cajon en cada pagina; sin JavaScript lleva a
    comunidad.html. Lo abre y lo cierra comunidad.js. index.html recibe la
    misma copia entre marcas (poner_puerta)."""
    f = formas('pt')
    rutas = [RUTA_HTML.format(id=id_, ico=ico, tit=tit, que=que, form=f[id_],
                              extra=('\n          <p class="pt-nota">%s</p>' % DENUNCIA) if id_ == 'reporta' else '')
             for id_, ico, tit, que in RUTAS]
    return PUERTA_HTML.format(rutas='\n'.join(rutas))


# Ágora cívica en su propia pagina (decision del autor, 10-10-2026): antes
# era la primera pestana de Participa y se desplegaba ahi. Ahora es una red
# de replica y dialogo: perfil, muro, replicas, apoyos e insignias. Todo vive
# en el navegador del lector hasta que haya servidor, y la pagina lo dice.
# Lo pinta assets/auditor/js/agora.js; los hilos usan la misma llave que el
# foro anterior (auditavision_foro_debates), asi que no se pierde nada.
# Temas: (id, icono, nombre, pagina de la plataforma con sus datos).
AGORA_TEMAS = [
    ('presupuesto', '📊', 'Presupuesto', 'sigue-el-dinero.html'),
    ('megaobras', '🏗️', 'Megaobras', 'herramienta-megaobras.html'),
    ('deuda', '📈', 'Deuda', 'auditoria-deuda-soberana.html'),
    ('municipios', '📍', 'Estados y municipios', 'auditoria-ramo-33.html'),
    ('salud', '💊', 'Salud y medicinas', 'auditoria-megafarmacia.html'),
    ('ambiente', '🌳', 'Ambiente', 'herramienta-ambiente.html'),
    ('legislativo', '🏛️', 'Congreso', 'herramienta-inspector-entes.html'),
    ('judicial', '⚖️', 'Poder Judicial', 'herramienta-inspector-entes.html'),
    ('politicos', '👥', 'Personajes', 'diccionario.html'),
    ('general', '🌐', 'Debate general', 'indice.html'),
]
# Posturas: (id, icono, nombre).
AGORA_POSTURAS = [
    ('a_favor', '🟢', 'A favor'),
    ('en_contra', '🔴', 'En contra'),
    ('matiz', '🟡', 'Matiz'),
    ('aporte', '📄', 'Aporte documental'),
    ('pregunta', '❓', 'Pregunta'),
]
# Preguntas de la plataforma para abrir conversacion (tema, pregunta,
# pagina donde estan los datos). Son preguntas, no cifras ni opiniones.
AGORA_PREGUNTAS = [
    ('megaobras', '¿Con qué indicador medirías si una megaobra valió lo que costó?', 'herramienta-megaobras.html'),
    ('presupuesto', 'Si repartieras el presupuesto desde cero, ¿qué subirías y qué bajarías?', 'simulador-presupuesto.html'),
    ('municipios', '¿Tu municipio publica en qué gastó su Ramo 33? ¿Lo encontraste?', 'auditoria-ramo-33.html'),
    ('deuda', '¿Qué debería explicar el gobierno antes de contratar más deuda?', 'auditoria-deuda-soberana.html'),
    ('salud', '¿Qué tendría que transparentar una compra consolidada de medicinas?', 'auditoria-megafarmacia.html'),
]
AGORA_REGLAS = [
    ('Argumentos, no personas.', 'Se discute lo que alguien dijo, nunca quién es.'),
    ('Cifra sin fuente es opinión.', 'Si das un número, enlaza el documento oficial de donde sale.'),
    ('Seudónimo sí, suplantación no.', 'Firma como quieras, pero no te hagas pasar por otra persona ni por una institución.'),
    ('Nada de datos de terceros.', 'Ni domicilios, ni teléfonos, ni documentos de nadie.'),
    ('Cero odio y cero amenazas.', 'Lo que ataque a un grupo o a una persona no tiene lugar aquí.'),
    ('El desacuerdo se replica.', 'Si no estás de acuerdo, responde con tu argumento y tu fuente.'),
]
AGORA_SERVIDOR = [
    'Muro público: lo que publiques lo leerá cualquiera.',
    'Seguir temas y personas, y avisos cuando alguien te replique.',
    'Moderación con estas mismas reglas, publicadas y con apelación.',
    'Verificación de fuentes entre pares: quien revisa un enlace lo marca.',
]
AGORA_COLORES = ['#1a56b8', '#0f7b4f', '#b45309', '#b3261e', '#6d28d9', '#be185d', '#0e7490', '#334155']


def agora():
    temas_json = json.dumps({'temas': AGORA_TEMAS, 'posturas': AGORA_POSTURAS, 'colores': AGORA_COLORES}, ensure_ascii=False)
    opciones = ''.join('<option value="%s">%s %s</option>' % (t[0], t[1], t[2]) for t in AGORA_TEMAS)
    posturas = ''.join(
        '<label class="ag-postura"><input type="radio" name="agPostura" value="%s"%s><span>%s %s</span></label>'
        % (p[0], ' checked' if p[0] == 'matiz' else '', p[1], p[2]) for p in AGORA_POSTURAS)
    colores = ''.join(
        '<label class="ag-color" style="--c:%s"><input type="radio" name="agColor" value="%s"%s><span class="sr-only">Color %d</span></label>'
        % (c, c, ' checked' if i == 0 else '', i + 1) for i, c in enumerate(AGORA_COLORES))
    temas = {t[0]: t for t in AGORA_TEMAS}
    preguntas = '\n'.join(
        '              <li><button type="button" class="ag-preg" data-tema="%s" data-texto="%s"><span class="ag-preg-tema">%s %s</span>%s</button>'
        '<a class="ag-preg-datos" href="%s">Ver los datos ➔</a></li>'
        % (p[0], esc_attr(p[1]), temas[p[0]][1], temas[p[0]][2], p[1], p[2]) for p in AGORA_PREGUNTAS)
    reglas = '\n'.join('              <li><b>%s</b> %s</li>' % r for r in AGORA_REGLAS)
    servidor = '\n'.join('              <li>%s</li>' % s for s in AGORA_SERVIDOR)
    bloque = '''<script type="application/json" id="agDatos">{datos}</script>
        <div class="ag" id="agora">
          <aside class="ag-izq" aria-label="Tu perfil y las reglas">
            <section class="ag-card ag-perfil" aria-labelledby="agPerfilTit">
              <h2 class="ag-card-tit" id="agPerfilTit">Tu perfil cívico</h2>
              <div class="ag-perfil-cab"><span class="ag-avatar ag-avatar-xl" id="agAvatar" aria-hidden="true">?</span>
                <div class="ag-perfil-id"><b id="agPerfilNick">Sin seudónimo</b><span id="agPerfilLugar">Elige cómo firmar</span></div></div>
              <p class="ag-perfil-bio" id="agPerfilBio" hidden></p>
              <dl class="ag-stats" id="agStats"></dl>
              <div class="ag-insignias" id="agInsignias" aria-label="Insignias"></div>
              <details class="ag-editar" id="agEditar">
                <summary>✏️ Editar perfil</summary>
                <form id="agPerfilForm" class="ag-form">
                  <div class="ag-campo"><label for="agNick">Seudónimo</label>
                    <div class="ag-fila"><input id="agNick" type="text" maxlength="30" placeholder="@CiudadanaDelSur" autocomplete="off">
                    <button type="button" class="ag-btn" id="agNickAzar" title="Sugerir un seudónimo">🎲</button></div></div>
                  <div class="ag-campo"><label for="agLugar">Desde dónde escribes (opcional)</label>
                    <input id="agLugar" type="text" maxlength="60" placeholder="Municipio o estado"></div>
                  <div class="ag-campo"><label for="agBio">Una línea sobre ti (opcional)</label>
                    <input id="agBio" type="text" maxlength="140" placeholder="Qué te interesa fiscalizar"></div>
                  <fieldset class="ag-colores"><legend>Color de tu avatar</legend>{colores}</fieldset>
                  <button type="submit" class="ag-btn ag-btn-of">Guardar perfil</button>
                </form>
              </details>
              <div class="ag-perfil-acc">
                <button type="button" class="ag-btn" id="agDescargar">⬇️ Descargar mis hilos</button>
              </div>
            </section>
            <section class="ag-card" aria-labelledby="agReglasTit">
              <h2 class="ag-card-tit" id="agReglasTit">📜 Reglas del Ágora</h2>
              <ol class="ag-reglas">
{reglas}
              </ol>
            </section>
          </aside>

          <div class="ag-centro">
            <form class="ag-card ag-composer" id="agComposer" novalidate>
              <div class="ag-comp-cab"><span class="ag-avatar" id="agAvatarMini" aria-hidden="true">?</span>
                <label class="sr-only" for="agTesis">Tu tesis</label>
                <input id="agTesis" type="text" maxlength="160" placeholder="¿Qué quieres poner a debate?" autocomplete="off" required></div>
              <div class="ag-comp-mas" id="agCompMas">
                <label class="sr-only" for="agTexto">Tu argumento</label>
                <textarea id="agTexto" rows="4" maxlength="1200" placeholder="Desarrolla tu argumento: qué afirmas, por qué y con qué datos." required></textarea>
                <fieldset class="ag-posturas"><legend>Tu postura</legend>{posturas}</fieldset>
                <div class="ag-comp-fila">
                  <div class="ag-campo"><label for="agTema">Tema</label><select id="agTema">{opciones}</select></div>
                  <div class="ag-campo ag-campo-ancho"><label for="agFuente">Fuente oficial (enlace)</label>
                    <input id="agFuente" type="url" maxlength="400" placeholder="https://… (ASF, DOF, Hacienda, INEGI)"></div>
                </div>
                <div class="ag-comp-pie"><span class="ag-cuenta" id="agCuenta">0 / 1200</span>
                  <span class="ag-estado" id="agEstado" role="status"></span>
                  <button type="submit" class="ag-btn ag-btn-of">Publicar</button></div>
              </div>
            </form>

            <div class="ag-barra">
              <div class="ag-orden" role="group" aria-label="Ordenar el muro">
                <button type="button" class="ag-orden-btn" data-orden="recientes" aria-pressed="true">🕒 Recientes</button>
                <button type="button" class="ag-orden-btn" data-orden="apoyados" aria-pressed="false">👍 Más apoyados</button>
                <button type="button" class="ag-orden-btn" data-orden="replicados" aria-pressed="false">💬 Más replicados</button>
                <button type="button" class="ag-orden-btn" data-orden="fuente" aria-pressed="false">📄 Con fuente</button>
                <button type="button" class="ag-orden-btn" data-orden="mios" aria-pressed="false">🙋 Mis hilos</button>
              </div>
              <label class="sr-only" for="agBuscar">Buscar en el muro</label>
              <input id="agBuscar" class="ag-buscar" type="search" placeholder="🔍 Buscar en el muro" autocomplete="off">
            </div>
            <div class="ag-chips" id="agTemas" role="group" aria-label="Filtrar por tema"></div>
            <div class="ag-feed" id="agFeed" aria-live="polite"></div>
          </div>

          <aside class="ag-der" aria-label="Temas y preguntas">
            <section class="ag-card" aria-labelledby="agTendTit">
              <h2 class="ag-card-tit" id="agTendTit">🔥 Temas en conversación</h2>
              <ol class="ag-tend" id="agTendencias"></ol>
            </section>
            <section class="ag-card" aria-labelledby="agPregTit">
              <h2 class="ag-card-tit" id="agPregTit">💡 Preguntas para empezar</h2>
              <p class="ag-card-sub">Las propone la plataforma. Elige una y escribe tu respuesta.</p>
              <ul class="ag-pregs">
{preguntas}
              </ul>
            </section>
            <section class="ag-card" aria-labelledby="agComoTit">
              <h2 class="ag-card-tit" id="agComoTit">🧭 Cómo se replica bien</h2>
              <ol class="ag-como">
                <li><b>Cita.</b> Di con qué parte del argumento no estás de acuerdo.</li>
                <li><b>Prueba.</b> Enlaza el documento oficial que sostiene tu dato.</li>
                <li><b>Propón.</b> Termina con lo que harías tú o con la pregunta que falta responder.</li>
              </ol>
            </section>
            <section class="ag-card ag-pronto" aria-labelledby="agProntoTit">
              <h2 class="ag-card-tit" id="agProntoTit">🚧 Lo que llega con el servidor</h2>
              <ul>
{servidor}
              </ul>
            </section>
          </aside>
        </div>
        <noscript><p class="sv-aviso">El Ágora necesita JavaScript para funcionar.</p></noscript>'''.format(
        datos=temas_json.replace('</', '<\\/'), colores=colores, reglas=reglas, posturas=posturas,
        opciones=opciones, preguntas=preguntas, servidor=servidor)
    return {
        'archivo': 'agora.html', 'menu': 'Ágora cívica', 'menu_archivo': 'participa.html',
        'padre': ('participa.html', 'Participa'),
        'icono': '💬', 'titulo': 'Ágora cívica', 'lema': 'La red de réplica y diálogo',
        'entrada': ('Pon a debate lo que viste en los números, sostenlo con su fuente y replica a quien piense distinto. '
                    'Firmas con seudónimo: sin correo, sin teléfono y sin rastreo.'),
        'estilos': ['servicios.css', 'agora.css'],
        'scripts': ['agora.js'],
        'antes': ('      <p class="sv-aviso ag-aviso"><span class="sz-et">Versión de prueba</span> Por ahora el Ágora vive '
                  '<b>solo en tu navegador</b>: lo que publiques, tus apoyos y tu perfil se guardan en este equipo y nadie más '
                  'los ve todavía. El muro público se abre cuando la plataforma tenga servidor; mientras, puedes descargar tus hilos.</p>'),
        'secciones': [
            {'id': 'muro', 'titulo': '💬 El muro', 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': bloque},
        ],
    }


def poner_puerta():
    """Copia el cajon de «Cuéntanos lo que viste» en index.html, entre
    <!-- puerta:inicio --> y <!-- puerta:fin -->. index.html se edita en
    binario para no tocar sus CRLF ni sus CR sueltos."""
    ruta = os.path.join(RAIZ, 'index.html')
    d = open(ruta, 'rb').read().decode('utf-8')
    m = re.search(r'(  <!-- puerta:inicio -->)(.*?)(  <!-- puerta:fin -->)', d, re.S)
    if not m:
        print('ERROR: index.html no tiene las marcas de la puerta')
        return 1
    bloque = puerta().replace('\r\n', '\n').replace('\n', '\r\n')
    d = d[:m.start()] + m.group(1) + '\r\n' + bloque + '\r\n' + m.group(3) + d[m.end():]
    open(ruta, 'wb').write(d.encode('utf-8'))
    return 0


def comunidad():
    f = formas('cm')
    reporte, tema, error = f['reporta'], f['tema'], f['error']
    erratas = '\n'.join(
        '            <li class="cm-errata"><span class="cm-errata-fecha">%s</span><b>%s</b>'
        '<span><span class="cm-errata-et">Estaba mal:</span> %s</span><span><span class="cm-errata-et">Qué hicimos:</span> %s</span>%s</li>'
        % (e[0], e[1], e[2], e[3], (' <a href="%s">Ver la página ➔</a>' % e[4]) if e[4] else '') for e in ERRATAS)
    compartir = ('<div class="cm-compartir" data-url="%sestado-de-cuenta.html" '
                 'data-texto="El Estado de Cuenta Cívico de México: de dónde sale el dinero público y en qué se gasta, con fuentes oficiales.">\n'
                 '          <p>El <a href="estado-de-cuenta.html">Estado de Cuenta Cívico</a> resume 2024, 2026 y 2027 en cuatro dimensiones, '
                 'cada cifra con su fuente. Compártelo: entre más gente lo lea, más difícil es que el dinero público pase sin que nadie lo vea.</p>\n'
                 '          <div class="sv-acciones cm-redes"></div>\n'
                 '          <p class="cm-nota">Si sacaste tu cuenta personal en la <a href="herramienta-calculadora-ticket.html">Calculadora Cívica</a>, '
                 'compartimos solo el enlace: tu ingreso nunca sale de tu navegador.</p>\n'
                 '          <noscript><p>Para compartir, copia esta dirección: %sestado-de-cuenta.html</p></noscript>\n'
                 '        </div>') % (SITIO, SITIO)
    return {
        'archivo': 'comunidad.html', 'menu': 'Comunidad', 'menu_archivo': 'participa.html',
        'padre': ('participa.html#comunidad', 'Participa'),
        'icono': '🤝', 'titulo': 'Comunidad', 'lema': 'Cuéntanos lo que viste',
        'entrada': ('La plataforma mejora con quien la lee. Repórtanos algo raro con el dinero público, señala un dato que esté mal '
                    '(con su documento) o propón un tema para investigar. Es lo mismo que abre el botón «📢 Cuéntanos lo que viste» '
                    'de la cabecera, aquí en su página, junto con la fe de erratas: cada corrección que hemos hecho, qué estaba mal y qué cambió.'),
        'estilos': ['servicios.css'],
        'antes': ('      <p class="sv-aviso"><span class="sz-et">Próximamente</span> El envío se activa '
                  'con el lanzamiento. Ya puedes armar tu reporte, copiarlo o descargarlo. Compartir y la fe de erratas ya funcionan.</p>'),
        'secciones': [
            {'id': 'reporta', 'titulo': '🏗️ Algo raro con el dinero público', 'texto': RUTAS[0][3] + ' Dinos qué, dónde y cuándo.',
             'tarjetas': [], 'bloque': reporte + '\n        <p class="pt-nota">%s</p>' % DENUNCIA},
            {'id': 'error', 'titulo': '✏️ Un dato mal en esta plataforma', 'texto': 'Si un dato no coincide con su documento oficial, dínoslo. Si tienes razón, se corrige y entra a la fe de erratas.',
             'tarjetas': [], 'bloque': error},
            {'id': 'tema', 'titulo': '💡 Un tema que deberíamos investigar', 'texto': 'Lo que te gustaría que investigáramos. No compromete a nadie: lo revisamos y, si hay documentos, entra a la lista.',
             'tarjetas': [], 'bloque': tema},
            {'id': 'compartir', 'titulo': '📣 Comparte el Estado de Cuenta', 'texto': 'Un enlace basta.', 'tarjetas': [], 'bloque': compartir},
            {'id': 'erratas', 'titulo': '📋 Fe de erratas', 'texto': 'Las correcciones que hemos hecho, de la más reciente a la más antigua.',
             'tarjetas': [], 'bloque': '<div class="sv-politica">\n          <ol class="cm-erratas">\n%s\n          </ol>\n        </div>' % erratas},
        ],
    }


# Garantias civicas en su propia pagina (decision del autor, 10-10-2026).
# La pestana de Participa juntaba cinco cosas: la orientacion de las tres
# funciones, una copia de «Cuentanos lo que viste», los seis canales y el
# decalogo. Lo repetido ya vive en Comunidad y en el Agora; aqui se queda lo
# que es de verdad una garantia: a que puerta oficial tocar, que te protege y
# que llevar. Todo sale de window.AUDIT_DB (comunidad.canales_denuncia_oficial
# y principios_contraloria_social): aqui no se teclea ningun texto legal.
#
# La brujula: (id, icono, lo que viste, canal). El texto resume el «paraQue»
# de cada canal en la base.
BRUJULA_QUE = [
    ('federal', '🏗️', 'Dinero federal mal usado', 'Una obra, un contrato, un subsidio o un fondo federal (Ramo 28 o 33) que no cuadra.', 'ch-asf'),
    ('servidor', '🧑‍💼', 'Un servidor público federal', 'Pidió dinero, desvió recursos, abusó de su cargo o acosó a alguien.', 'ch-sabg'),
    ('delito', '⚔️', 'Algo que parece delito', 'Enriquecimiento ilícito, peculado, cohecho, uso ilícito de atribuciones o tráfico de influencias.', 'ch-fgr'),
    ('factura', '📑', 'Facturas falsas', 'Una empresa que cobra servicios que nunca se prestaron: el truco para vaciar un contrato.', 'ch-sat'),
    ('local', '🏘️', 'Algo de tu municipio o tu estado', 'La obra de tu colonia, un cobro indebido en ventanilla, un trámite condicionado.', 'ch-oic'),
]

# ¿Mito o realidad? (afirmacion, es realidad, de donde sale la respuesta).
# La explicacion y el fundamento se leen de la base: ('dec', n) es el punto n
# del decalogo; ('canal', id) es el campo «anonimo» de ese canal.
GARANTIAS_RETO = [
    ('Para pedir un contrato público tienes que explicar para qué lo quieres.', False, ('dec', 3)),
    ('Puedes denunciar ante la Auditoría Superior de la Federación sin decir tu nombre.', True, ('canal', 'ch-asf')),
    ('Una denuncia penal ante la Fiscalía puede ser del todo anónima.', False, ('canal', 'ch-fgr')),
    ('Si un contrato público no está publicado, es información secreta.', False, ('dec', 2)),
    ('El FISMDF puede pagar cualquier obra del municipio, donde el ayuntamiento decida.', False, ('dec', 5)),
    ('Condicionar una despensa o un apoyo a cambio de tu voto es un delito electoral.', True, ('dec', 7)),
    ('Si la dependencia no responde tu solicitud de información, ya no hay nada que hacer.', False, ('dec', 10)),
]


def _anonimo_corto(t):
    """«Sí, y con protección...» -> «Sí»; «No del todo. La...» -> «No del todo»."""
    return re.split(r'[.,;:]', t, 1)[0].strip()


def garantias():
    import auditorias
    base = auditorias.db()
    com = base['comunidad']
    canales = com['canales_denuncia_oficial']
    decalogo = com['principios_contraloria_social']
    refs = {r['id']: r for r in base.get('referencias_legales', [])}
    por_id = {c['id']: c for c in canales}

    def fuente(c):
        r = refs.get(c.get('refId'))
        return ('<a class="gr-fuente" href="%s" target="_blank" rel="noopener noreferrer">📜 Fundamento: %s</a>'
                % (r['url'], esc_attr(r['cita_apa'].split('.')[0]))) if r and r.get('url') else ''

    def acceso(c):
        if c.get('url'):
            return '<a class="sz-btn sz-btn-of" href="%s" target="_blank" rel="noopener noreferrer">Abrir el canal oficial ↗</a>' % c['url']
        return '<span class="gr-sin-url">%s</span>' % c.get('notaSinUrl', '')

    puertas = '\n'.join('''          <article class="gr-puerta" id="puerta-{id}" data-tono="{tono}">
            <div class="gr-puerta-cab"><span class="gr-puerta-ico" aria-hidden="true">{icono}</span>
              <div><span class="gr-puerta-num">Puerta {n} de {total}</span><h3>{organismo} <span class="gr-siglas">{siglas}</span></h3>
              <span class="gr-herr">{herramienta}</span></div></div>
            <p class="gr-paraque">{paraQue}</p>
            <p class="gr-anon"><span class="gr-anon-et">¿Sin dar tu nombre?</span> <b>{anon}</b></p>
            <details class="gr-mas"><summary>Qué llevar y qué pasa después</summary>
              <dl class="gr-datos">
                <div><dt>Anonimato</dt><dd>{anonimo}</dd></div>
                <div><dt>Qué llevar</dt><dd>{queNecesitas}</dd></div>
                <div><dt>Qué produce</dt><dd>{efecto}</dd></div>
              </dl>
              {fuente}
            </details>
            <div class="gr-puerta-pie">{acceso}</div>
          </article>'''.format(n=i + 1, total=len(canales), anon=_anonimo_corto(c['anonimo']), fuente=fuente(c), acceso=acceso(c),
                               **{k: c.get(k, '') for k in ('id', 'tono', 'icono', 'organismo', 'siglas', 'herramienta',
                                                            'paraQue', 'anonimo', 'queNecesitas', 'efecto')})
                        for i, c in enumerate(canales))

    cartas = '\n'.join('''          <li><button type="button" class="gr-carta" aria-pressed="false">
            <span class="gr-carta-cara gr-carta-frente"><span class="gr-carta-n">{n}</span><b>{titulo}</b><small>Toca para ver por qué</small></span>
            <span class="gr-carta-cara gr-carta-dorso"><span>{texto}</span><small>📜 {fundamento}</small></span>
          </button></li>'''.format(**d) for d in decalogo)

    reto = []
    for afirma, real, (tipo, clave) in GARANTIAS_RETO:
        if tipo == 'dec':
            d = [x for x in decalogo if x['n'] == clave][0]
            reto.append({'a': afirma, 'r': real, 'x': d['texto'], 'f': d['fundamento'], 'de': 'Garantía %d: %s' % (d['n'], d['titulo'])})
        else:
            c = por_id[clave]
            r = refs.get(c.get('refId'), {})
            reto.append({'a': afirma, 'r': real, 'x': c['anonimo'], 'f': c['herramienta'] + ' (' + c['siglas'] + ')',
                         'de': 'Puerta: ' + c['organismo'], 'u': r.get('url', '')})
    datos = json.dumps({
        'canales': {c['id']: {k: c.get(k) for k in ('organismo', 'siglas', 'icono', 'herramienta', 'anonimo', 'queNecesitas', 'efecto', 'url', 'notaSinUrl')}
                    for c in canales},
        'que': [{'id': q[0], 'canal': q[4]} for q in BRUJULA_QUE],
        'reto': reto,
    }, ensure_ascii=False).replace('</', '<\\/')

    opciones = '\n'.join(
        '              <button type="button" class="gr-op" data-que="%s"><span class="gr-op-ico" aria-hidden="true">%s</span>'
        '<b>%s</b><small>%s</small></button>' % (q[0], q[1], q[2], q[3]) for q in BRUJULA_QUE)

    brujula = '''<script type="application/json" id="grDatos">{datos}</script>
        <div class="gr-brujula" id="grBrujula">
          <ol class="gr-pasos" aria-label="Avance">
            <li class="gr-paso-on"><span>1</span> Qué viste</li><li><span>2</span> Tu prueba</li><li><span>3</span> Tu nombre</li><li><span>✓</span> Tu puerta</li>
          </ol>
          <div class="gr-etapa" data-etapa="1">
            <h3 class="gr-preg">¿Qué viste?</h3>
            <div class="gr-ops">
{opciones}
            </div>
          </div>
          <div class="gr-etapa" data-etapa="2" hidden>
            <h3 class="gr-preg">¿Ya tienes con qué probarlo?</h3>
            <p class="gr-ayuda">Un número de contrato, una factura, una foto con fecha, un acta de entrega.</p>
            <div class="gr-ops gr-ops-2">
              <button type="button" class="gr-op" data-prueba="si"><span class="gr-op-ico" aria-hidden="true">📎</span><b>Sí, tengo documentos</b><small>O al menos el nombre, el lugar y la fecha.</small></button>
              <button type="button" class="gr-op" data-prueba="no"><span class="gr-op-ico" aria-hidden="true">🔎</span><b>Todavía no</b><small>Lo vi, pero no tengo papeles.</small></button>
            </div>
            <button type="button" class="gr-atras" data-atras="1">← Cambiar lo que viste</button>
          </div>
          <div class="gr-etapa" data-etapa="3" hidden>
            <h3 class="gr-preg">¿Necesitas que no se sepa tu nombre?</h3>
            <div class="gr-ops gr-ops-2">
              <button type="button" class="gr-op" data-nombre="oculto"><span class="gr-op-ico" aria-hidden="true">🎭</span><b>Sí, prefiero no darlo</b><small>Temo represalias o no quiero exponerme.</small></button>
              <button type="button" class="gr-op" data-nombre="da"><span class="gr-op-ico" aria-hidden="true">🙋</span><b>Puedo dar mi nombre</b><small>No me preocupa que se sepa.</small></button>
            </div>
            <button type="button" class="gr-atras" data-atras="2">← Cambiar tu respuesta</button>
          </div>
          <div class="gr-etapa gr-resultado" data-etapa="4" hidden aria-live="polite">
            <div id="grRuta"></div>
            <p class="gr-res-pie"><button type="button" class="sz-btn" id="grOtra">🔄 Empezar otra vez</button>
              <a class="sz-btn" href="comunidad.html#reporta" data-puerta="reporta">📢 Ordena tu texto antes de presentarlo</a></p>
          </div>
          <noscript><p>La brújula necesita JavaScript. Abajo están las seis puertas con todo lo que necesitas saber.</p></noscript>
        </div>'''.format(datos=datos, opciones=opciones)

    reto_html = '''<div class="gr-reto" id="grReto">
          <div class="gr-reto-cab"><span id="grRetoAvance">Pregunta 1 de {n}</span><span id="grRetoPuntos">Aciertos: 0</span></div>
          <div class="gr-reto-barra" aria-hidden="true"><span id="grRetoBarra"></span></div>
          <p class="gr-reto-af" id="grRetoAf">…</p>
          <div class="gr-reto-ops"><button type="button" class="gr-reto-btn" data-r="1">✅ Realidad</button><button type="button" class="gr-reto-btn" data-r="0">❌ Mito</button></div>
          <div class="gr-reto-exp" id="grRetoExp" hidden aria-live="polite"></div>
          <noscript><p>El reto necesita JavaScript. Las respuestas están en las diez garantías de arriba.</p></noscript>
        </div>'''.format(n=len(GARANTIAS_RETO))

    return {
        'archivo': 'garantias.html', 'menu': 'Garantías cívicas', 'menu_archivo': 'participa.html',
        'padre': ('participa.html', 'Participa'),
        'icono': '🛡️', 'titulo': 'Garantías cívicas', 'lema': 'A qué puerta tocar y qué te protege',
        'entrada': ('Viste algo raro con el dinero público. Esta página responde tres preguntas: <b>a qué puerta oficial tocar</b>, '
                    '<b>qué derechos te protegen</b> y <b>qué llevar</b>. Empieza por la brújula: en tres clics te dice cuál de las '
                    '%d puertas te toca.' % len(canales)),
        'estilos': ['servicios.css', 'garantias.css'],
        'scripts': ['garantias.js'],
        'antes': ('      <p class="sv-aviso gr-aviso"><span class="sz-et">Importante</span> Auditavisión <b>no recibe denuncias</b>. '
                  '«📢 Cuéntanos lo que viste» te ayuda a redactar tu reporte y el <a href="agora.html">Ágora</a> es para debatir; '
                  'la denuncia con efecto jurídico (folio, plazos y obligación de responder) solo la abre una de estas puertas oficiales.</p>'),
        'secciones': [
            {'id': 'brujula', 'titulo': '🧭 La brújula: ¿a qué puerta toco?',
             'texto': 'Tres preguntas y te decimos qué canal oficial te toca, qué llevar y si puedes hacerlo sin dar tu nombre.',
             'tarjetas': [], 'bloque': brujula},
            {'id': 'puertas', 'titulo': '🚪 Las seis puertas oficiales',
             'texto': 'Cada una investiga cosas distintas. Una no es para denunciar sino para conseguir la prueba: la Plataforma Nacional de Transparencia.',
             'tarjetas': [], 'bloque': '<div class="gr-puertas">\n%s\n        </div>' % puertas},
            {'id': 'derechos', 'titulo': '🛡️ Tus diez garantías',
             'texto': 'Lo que la ley te asegura cuando vigilas el dinero público. Toca cada carta para ver la explicación y la norma que la sostiene.',
             'tarjetas': [], 'bloque': '<ol class="gr-cartas">\n%s\n        </ol>' % cartas},
            {'id': 'reto', 'titulo': '🎯 ¿Mito o realidad?',
             'texto': '%d afirmaciones que se oyen seguido. Adivina y comprueba con la ley.' % len(GARANTIAS_RETO),
             'tarjetas': [], 'bloque': reto_html},
        ],
    }


# Radar hacendario en su propia pagina (decision del autor, 10-10-2026): cada
# administracion con sus numeros. Era la pestana «Radar hacendario» de Datos
# (herramientas/plantillas/radar.html + radar-datos.js): cifras sueltas de
# 2026 y equivalencias por segundo. Ahora es un tablero por sexenio con
# ingresos, inversion, costo del gobierno, deuda y lo pendiente ante la ASF,
# mas el reloj de cada administracion y el duelo entre dos. Las cifras del
# ano en curso se quedan abajo, en «Hoy».
#
# Todo sale de window.AUDIT_DB: finanzas_sexenales (series anuales de
# Hacienda y deuda al recibir y al entregar), evaluacion_sexenal
# (auditorias y recuperaciones de la ASF), cuenta_publica_asf (por aclarar)
# y simulador_megaobras (las obras de cada sexenio). Aqui solo se promedia y
# se suma, y cada operacion se dice junto a su cifra.
RADAR_ADMINS = [
    # (id, nombre, corto, iniciales, anos que se le asignan, color, en curso)
    ('salinas', 'Carlos Salinas de Gortari', 'Salinas', 'CS', (1989, 1994), '#7a8aa8', False),
    ('zedillo', 'Ernesto Zedillo Ponce de León', 'Zedillo', 'EZ', (1995, 2000), '#4f9be8', False),
    ('fox', 'Vicente Fox Quesada', 'Fox', 'VF', (2001, 2006), '#23855a', False),
    ('calderon', 'Felipe Calderón Hinojosa', 'Calderón', 'FC', (2007, 2012), '#a9541a', False),
    ('epn', 'Enrique Peña Nieto', 'Peña Nieto', 'EPN', (2013, 2018), '#7d3fa6', False),
    ('amlo', 'Andrés Manuel López Obrador', 'López Obrador', 'AMLO', (2019, 2024), '#b3261e', False),
    ('sheinbaum', 'Claudia Sheinbaum Pardo', 'Sheinbaum', 'CSP', (2025, 2030), '#0f7f7a', True),
]
# Nombre de cada presidente como lo escribe simulador_megaobras.
RADAR_OBRAS_PRES = {'salinas': 'Carlos Salinas', 'zedillo': 'Ernesto Zedillo', 'fox': 'Vicente Fox',
                    'calderon': 'Felipe Calderón', 'epn': 'Enrique Peña Nieto', 'amlo': 'Andrés Manuel López Obrador',
                    'sheinbaum': 'Claudia Sheinbaum'}
# Serie anual -> (titulo, que mide, «ojo» para la suma en pesos)
RADAR_SERIES = {
    'ingresos': ('Ingresos presupuestarios', 'Todo lo que entró al sector público presupuestario: impuestos, ingresos petroleros, cuotas del IMSS e ISSSTE y ventas de la CFE. Sin deuda.'),
    'inversion': ('Inversión física', 'Obra pública y equipamiento del sector público presupuestario: carreteras, hospitales, refinerías, presas, trenes.'),
    'gasto': ('Gasto neto total', 'Todo lo que gastó el sector público presupuestario en el año, incluidos los intereses de la deuda.'),
    'costo_financiero': ('Costo financiero', 'Intereses, comisiones y gastos de la deuda, más los programas de apoyo a ahorradores y deudores de la banca.'),
}
RADAR_MONEDAS = [
    # (id, etiqueta del selector, como se lee la suma)
    ('nom', 'Pesos de cada año', 'en pesos de cada año, sin quitar la inflación'),
    ('hoy', 'Pesos de hoy', 'en pesos de septiembre de 2026: ya sin inflación'),
    ('usd', 'Dólares', 'en dólares, al tipo de cambio promedio de cada año'),
    ('eur', 'Euros', 'en euros, al tipo de cambio promedio de cada año'),
]
RADAR_OJO_MON = {
    'nom': 'Son pesos de cada año, sin quitar la inflación: un peso de 1995 no vale lo mismo que uno de 2024. Para comparar sexenios, cambia a «Pesos de hoy» o usa el promedio en % del PIB.',
    'hoy': 'Pesos de septiembre de 2026: a cada año se le quita la inflación con el INPC, así que los sexenios ya se comparan entre sí. No mide el tamaño de la economía: para eso, el % del PIB.',
    'usd': 'Dólares de cada año: cada año entre su tipo de cambio promedio. Mide lo que valían esos pesos frente al dólar en su momento, no su poder de compra; las devaluaciones de 1994-1995 y 2008 se notan aquí.',
    'eur': 'Euros de cada año: cada año entre su tipo de cambio promedio. Banxico publica el euro desde 2000, así que Salinas y Zedillo no tienen esta medida.',
}
RADAR_OJO_MDP = RADAR_OJO_MON['nom']

# «Hoy»: las cifras del ano en curso que traia el radar anterior
# (plantillas/radar.html), con las mismas fuentes y chips.
def _hoy(ico, cifra, que, fuente, chip='oficial', pend=''):
    return ('          <div class="rd-hoy-c"><span class="rd-hoy-que">%s %s</span><b>%s</b> <span class="est-chip est-%s"%s>%s</span><small>📄 %s</small></div>'
            % (ico, que, cifra, chip, (' data-pend="%s"' % pend) if pend else '', chip, fuente))


# El contador (pedido del autor, 10-10-2026): las cifras arrancan en cero y
# el boton «Contar» las lleva a su valor; el mismo boton las regresa a cero.
# El recuadro «Durante tu visita» queda bloqueado hasta que se presiona.
# radar.js hace la animacion; sin JavaScript se ven las cifras completas.
RADAR_HOY = ('''<div class="rd-cuenta" id="rdCuenta" hidden>
          <button type="button" class="rd-cuenta-btn" id="rdContar" aria-pressed="false">▶ Contar</button>
          <span class="rd-cuenta-txt" id="rdCuentaTxt">Las cifras están en cero. Presiona «Contar» para verlas llegar a su valor oficial.</span>
        </div>
        ''' + '<div class="rd-hoy">\n' + '\n'.join([
    _hoy('🏛️', '$10.19 billones', 'Presupuesto federal aprobado 2026', 'Presupuesto de Egresos de la Federación 2026, art. 1'),
    _hoy('🗺️', '$2.81 billones (27.6 %)', 'Gasto federalizado a los 32 estados', 'PEF 2026: estimación del gasto federalizado, $2,810,800 mdp; 27.6 % = ese monto ÷ $10,193,683.7 mdp del PEF', 'derivado'),
    _hoy('💰', '$5.42 billones', 'ISR, IVA e IEPS estimados en la Ley de Ingresos 2026', 'Ley de Ingresos de la Federación 2026, art. 1: ISR $3,070,149.1 + IVA $1,589,069.0 + IEPS $761,501.9 mdp', 'derivado'),
    _hoy('🤝', '$1.46 billones', 'Participaciones a estados y municipios (Ramo 28)', 'PEF 2026, Ramo General 28: $1,456,045.9 mdp'),
    _hoy('📉', '$1,572,073.3 mdp', 'Costo financiero de la deuda en 2026', 'PEF 2026, Anexo 8'),
    _hoy('🏦', '$643,695.7 mdp', 'Deuda de los 32 gobiernos estatales', 'SHCP, Sistema de Alertas, evaluación con la Cuenta Pública 2025 (29 de junio de 2026); suma de las 32 entidades', 'derivado'),
    _hoy('⚖️', '$65,169.1 mdp', 'Por aclarar ante la ASF, Cuenta Pública 2024 (no es daño comprobado)', 'ASF, Matriz de Datos Básicos de la Cuenta Pública 2024 (consolidado, feb. 2026), p. 11'),
    _hoy('⛽', 'sin cifra oficial', 'Huachicol fiscal: cuánto IEPS se deja de cobrar', '<a href="auditoria-huachicol-fiscal.html">Lo que se sabe y lo que falta ➔</a>', 'pendiente', 'huachicol-evasion'),
]) + '''
        </div>
        <div class="rd-hoy-vivo" id="rdHoyVivo" role="status"><div class="rd-hoy-candado" id="rdCandado" hidden>🔒 Se desbloquea al presionar «Contar»</div><span>⏱️ Durante tu visita (<span id="rdHoyT">0:00</span>), al ritmo de 2026:</span>
          <span>intereses de la deuda <b data-tasa="49850.12">+$0.00</b></span>
          <span>pérdida documentada de las megaobras <b data-tasa="2062.75">+$0.00</b></span>
          <small>Equivalencias: la cifra anual entre los 31,536,000 segundos del año ($1,572,073.3 mdp y $65,050.8 mdp, este último un piso derivado
          con la Cuenta Pública 2024). No son pagos que ocurran en este instante. <a href="auditoria-deuda-soberana.html">El reloj de los intereses ➔</a></small>
        </div>''')


# El Radar en paginas (decision del autor, 10-10-2026): radar-hacendario.html
# es la portada con una tarjeta por parte, y cada parte vive en su pagina.
# (id, archivo, icono, titulo, de que trata)
RADAR_PARTES = [
    # «Hoy» y «Expide el estado de cuenta» son una sola tarjeta (decision del
    # autor, 10-10-2026), pero «Expide» abre su propia pagina (decision del
    # autor, 10-10-2026, mas tarde): la tarjeta lleva a radar-hoy.html, con el
    # presupuesto en curso y el acceso a la herramienta, y la herramienta se
    # queda en radar-estado-de-cuenta.html porque esa direccion va impresa en
    # el sello de los PDF (?verifica=). Desde el mismo dia la verificacion es
    # un modulo del Modo Inspector (VERIFICA_PAGINA): los sellos nuevos llevan
    # ahi y radar-estado-de-cuenta.html?verifica= redirige.
    ('hoy', 'radar-hoy.html', '🧾', 'Hoy y los estados de cuenta',
     'El presupuesto en curso y el estado de cuenta de cada sexenio, de diputados federales y locales, del Senado y de la Suprema Corte, con semáforo y sello'),
    ('tablero', 'radar-tablero.html', '📡', 'El tablero', 'Cada administración, tarjeta por tarjeta, comparada con las demás'),
    ('peso', 'radar-peso.html', '💱', 'El peso en el tiempo', 'Inflación, dólar y euro desde 1988, con la proyección a 2032'),
    ('reloj', 'radar-reloj.html', '⏱️', 'El reloj de cada administración', 'El contador que corre al ritmo de cada sexenio'),
    ('duelo', 'radar-duelo.html', '⚔️', 'Duelo de administraciones', 'Dos administraciones, cara a cara'),
    ('lectura', 'radar-como-leer.html', '📏', 'Cómo leer estos números', 'Convenciones y advertencias de cada cifra'),
]


# El semaforo de la salud financiera (decision del autor, 10-10-2026): un
# color por indicador, sin calificacion global. Cada color sale de una regla
# escrita: el rango que van de la mejor a la peor de las administraciones
# cerradas se parte en tres tercios iguales (estado-administracion.js hace
# la cuenta y la escribe en el documento). Todo en % del PIB, para que los
# sexenios se comparen sin la inflacion de por medio.
RADAR_SEMAFORO = [
    {'id': 'balance', 'ico': '⚖️', 'tit': 'Balance presupuestario', 'u': 'pib', 'mejor': 'alto',
     'calc': ['resta', 'ingresos_pib', 'gasto_pib'],
     'que': 'Lo que entró menos lo que se gastó, en promedio al año. Negativo es déficit: se gastó más de lo que entró y la diferencia se cubrió con deuda.',
     'op': 'Ingresos presupuestarios (promedio anual, % del PIB) menos gasto neto total (promedio anual, % del PIB).'},
    {'id': 'deuda_anual', 'ico': '📉', 'tit': 'Cómo cambió la deuda, por año', 'u': 'ppa', 'mejor': 'bajo',
     'calc': ['por_anio', 'deuda_cambio'],
     'que': 'Cuánto subió (o bajó) la deuda pública, medida contra el tamaño de la economía, en promedio por cada año de gobierno.',
     'op': 'Cambio de la deuda en el periodo (puntos del PIB) entre los años que abarca.'},
    {'id': 'deuda_fin', 'ico': '🏦', 'tit': 'Deuda al cierre', 'u': 'pib', 'mejor': 'bajo',
     'calc': ['directo', 'deuda_fin'], 'excluye': {'salinas': 'Para 1994 solo existe la deuda neta de Banxico, un indicador distinto del SHRFSP: no se compara con los demás.'},
     'que': 'La deuda pública que dejó al cerrar su periodo (saldo histórico de los requerimientos financieros, SHRFSP), como parte del PIB.',
     'op': 'Tal como la publica su fuente.'},
    {'id': 'intereses', 'ico': '💸', 'tit': 'Peso de los intereses', 'u': 'pib', 'mejor': 'bajo',
     'calc': ['directo', 'costo_financiero_pib'],
     'que': 'Cuánto se fue, en promedio al año, solo en intereses y gastos de la deuda: dinero que no llega a escuelas, hospitales ni obras.',
     'op': 'Promedio anual del costo financiero, en % del PIB.'},
    {'id': 'inversion', 'ico': '🏗️', 'tit': 'Inversión física', 'u': 'pib', 'mejor': 'alto',
     'calc': ['directo', 'inversion_pib'],
     'que': 'Lo que se destinó a obra pública y equipamiento, en promedio al año: lo que deja infraestructura para los años siguientes.',
     'op': 'Promedio anual de la inversión física, en % del PIB.'},
    {'id': 'ingresos', 'ico': '💰', 'tit': 'Ingresos', 'u': 'pib', 'mejor': 'alto',
     'calc': ['directo', 'ingresos_pib'],
     'que': 'Todo lo que entró al sector público, sin deuda, en promedio al año. Más ingreso propio da más margen para gastar sin endeudarse.',
     'op': 'Promedio anual de los ingresos presupuestarios, en % del PIB.'},
]
RADAR_LEY17 = {'txt': ('La Ley Federal de Presupuesto y Responsabilidad Hacendaria (art. 17, vigente desde 2006) pide que el gasto contribuya '
                       'al equilibrio presupuestario, y permite un déficit solo de manera circunstancial, por las condiciones económicas '
                       'y sociales del país, con la justificación del Ejecutivo ante el Congreso.'),
               'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPRH.pdf', 'corto': 'LFPRH, art. 17 (Cámara de Diputados)'}


HOY_TEXTO = ('Las cifras grandes de 2026: el presupuesto federal, el gasto que va a los estados, los impuestos que se esperan '
             'y lo que cuesta la deuda. El punto de partida para leer cualquier estado de cuenta.')
EXPIDE_TEXTO = ('Elige de quién: una administración presidencial, la diputación federal, la senaduría, la diputación de cualquiera '
                'de los 32 congresos locales, o la Suprema Corte con su ponencia y sus asesores. Genera su estado de cuenta con su '
                'semáforo y descárgalo en PDF con folio y sello de verificación.')


def radar_nav(actual):
    """Barra al pie de cada pagina del Radar, con sus seis partes."""
    return ('<nav class="bib-nav" aria-label="Radar hacendario">\n'
            '        <a class="bib-nav-tit" href="radar-hacendario.html">📡 Radar hacendario: todas sus partes</a>\n'
            '        <div class="bib-nav-fila">\n%s\n        </div>\n      </nav>' % '\n'.join(
                '          <a class="bib-nav-a" href="%s"%s><span aria-hidden="true">%s</span><span>%s</span></a>'
                % (r[1], ' aria-current="page"' if r[1] == actual else '', r[2], r[3]) for r in RADAR_PARTES))


def _peso_base(ps):
    """INPC y tipos de cambio de Banxico, en promedios anuales y mensuales."""
    def prom(serie, y):
        v = serie['mensual'].get(str(y)) or []
        return sum(v) / 12 if len(v) == 12 and None not in v else None
    def mes(serie, y, m):
        v = serie['mensual'].get(str(y)) or []
        return v[m - 1] if len(v) >= m else None
    ult = max(int(y) for y in ps['inpc']['mensual'])
    ult_m = len(ps['inpc']['mensual'][str(ult)])
    ref = mes(ps['inpc'], ult, ult_m)
    return prom, mes, ref, (ult, ult_m)


MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']


def _peso_admins(ps, admins_def):
    """La inflacion y el tipo de cambio de cada sexenio: al recibir (diciembre
    del ano anterior) y al entregar (diciembre del ultimo ano; en curso, el
    ultimo mes publicado)."""
    prom, mes, ref, (uy, um) = _peso_base(ps)
    filas = []
    for (aid, nombre, corto, ini, (a0, a1), col, curso) in admins_def:
        r = (a0 - 1, 12)
        e = (uy, um) if curso else (a1, 12)
        et_r = 'dic. %d' % r[0]
        et_e = ('%s %d' % (MESES[e[1] - 1][:3] + '.', e[0])) if curso else 'dic. %d' % e[0]
        f = {'id': aid, 'rec': et_r, 'ent': et_e, 'curso': curso}
        i0, i1 = mes(ps['inpc'], *r), mes(ps['inpc'], *e)
        f['infl'] = {'v': round((i1 / i0 - 1) * 100, 1), 'est': 'derivado', 'f': [ps['inpc']['f']],
                     'op': 'INPC de %s (%s) ÷ INPC de %s (%s) − 1.' % (et_e, format(i1, '.3f'), et_r, format(i0, '.3f'))}
        f['cien'] = {'v': round(100 * i0 / i1, 2), 'est': 'derivado', 'f': [ps['inpc']['f']],
                     'op': '$100 × INPC de %s ÷ INPC de %s.' % (et_r, et_e)}
        for k in ('usd', 'eur'):
            s = ps[k]
            t0, t1 = mes(s, *r), mes(s, *e)
            if t0 is None or t1 is None:
                f[k] = {'na': s.get('antes', 'Sin serie.'), 'et': 'sin serie'}
                continue
            f[k] = {'rec': t0, 'ent': t1, 'v': round((t1 / t0 - 1) * 100, 1), 'est': 'derivado', 'f': [s['f']],
                    'op': 'Promedio de %s (%s) ÷ promedio de %s (%s) − 1, en %s.' % (et_e, format(t1, '.4f'), et_r, format(t0, '.4f'), s['unidad'])}
        filas.append(f)
    return filas


def _peso_json(ps):
    """Lo que necesita la seccion «El peso en el tiempo»: series anuales,
    valor de hoy y proyeccion. Las operaciones de las graficas se dicen en
    la pagina."""
    prom, mes, ref, (uy, um) = _peso_base(ps)
    anios = list(range(1988, uy))
    inpc = {y: prom(ps['inpc'], y) for y in anios}
    usd = {y: prom(ps['usd'], y) for y in anios}
    eur = {y: prom(ps['eur'], y) for y in anios if y >= ps['eur']['desde']}
    dic = {y: mes(ps['inpc'], y, 12) for y in anios}
    pr = ps['proyeccion']
    # Precios de diciembre proyectados: diciembre del ultimo ano observado por
    # la inflacion diciembre/diciembre que estima Hacienda para cada ano.
    y0 = pr['observado']
    p = dic[y0]
    proy = []
    for y in sorted(int(x) for x in pr['inflacion_dic'] if int(x) > y0):
        p = p * (1 + pr['inflacion_dic'][str(y)] / 100)
        proy.append({'y': y, 'inpc': round(p, 4), 'infl': pr['inflacion_dic'][str(y)], 'usd': pr['usd_prom'][str(y)]})
    return {
        'anios': anios,
        'inpc': {y: round(v, 4) for y, v in inpc.items()},
        'dic': {y: v for y, v in dic.items()},
        'infl': {y: round((dic[y] / dic[y - 1] - 1) * 100, 1) for y in anios if y - 1 in dic},
        'usd': {y: round(v, 4) for y, v in usd.items()},
        'eur': {y: round(v, 4) for y, v in eur.items()},
        'ref': {'inpc': ref, 'mes': '%s de %d' % (MESES[um - 1], uy), 'y': uy, 'm': um,
                'infl12': round((ref / mes(ps['inpc'], uy - 1, um) - 1) * 100, 1),
                'inpc12': mes(ps['inpc'], uy - 1, um),
                'ytd_usd': round(sum(ps['usd']['mensual'][str(uy)]) / len(ps['usd']['mensual'][str(uy)]), 4)},
        'hoy': ps['hoy'],
        'eur_desde': ps['eur']['desde'], 'eur_antes': ps['eur']['antes'],
        'proy': proy, 'proy_obs': y0, 'proy_eur': pr['eur'], 'proy_aviso': pr['aviso'],
        'f': {'inpc': ps['inpc']['f'], 'usd': ps['usd']['f'], 'eur': ps['eur']['f'], 'hoy': ps['hoy']['f'], 'proy': pr['f']},
    }


# ---------------------------------------------------------------------------
# Estado de cuenta de quienes legislan y juzgan (10-10-2026): la diputación
# federal, la de cada congreso local y la Suprema Corte con su ponencia. Se
# expide junto al de cada administración, con el mismo folio y el mismo sello.
#
# Todo sale de window.AUDIT_DB: comparador_salarial (lo que cobra cada cargo,
# de los manuales de remuneraciones y del Anexo 23 del PEF 2026) y poderes
# (presupuesto, ejercicio y auditorías de cada institución). Aquí no se
# escribe ninguna cifra. Tampoco se reparte el presupuesto entre el número de
# personas: ese reparto no es un dato (ver el Registro de pendientes).
# Dos señales con regla escrita en la ley: el tope del art. 127 de la
# Constitución y la obligación de publicar la remuneración bruta y la neta
# (art. 65, fr. VII, de la Ley General de Transparencia).
CARGOS_FUENTES = {
    'CPEUM': {'corto': 'Constitución Política de los Estados Unidos Mexicanos (arts. 52, 56, 94 y 127)',
              'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf'},
    'LGTAIP': {'corto': 'Ley General de Transparencia y Acceso a la Información Pública (DOF 20-03-2025), art. 65, fr. VII',
               'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGTAIP.pdf'},
    # La vista «como organo» (pedido del autor, 10-10-2026).
    'CONAPO': {'corto': 'CONAPO, Proyecciones de la Población 2020-2070: población a mitad de 2026',
               'url': 'https://repodatos.atdt.gob.mx/CONAPO/proyecciones/00_Pob_Mitad_1950_2070.csv'},
    'ASF_MDB': {'corto': 'ASF, Matriz de Datos Básicos de la Cuenta Pública 2024 (consolidado), p. 31',
                'url': 'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Matriz/MDB_Consolidado.pdf'},
    'CP2024': {'corto': 'SHCP, Cuenta Pública 2024, datos abiertos',
               'url': 'https://www.transparenciapresupuestaria.gob.mx/work/models/PTP/DatosAbiertos/BD_Cuenta_Publica/CSV/cuenta_publica_2024_gf_ecd_epe.csv'},
}
CARGOS_ENTIDADES = {
    'Aguascalientes': 'AGS', 'Baja California': 'BC', 'Baja California Sur': 'BCS', 'Campeche': 'CAM',
    'Chiapas': 'CHIS', 'Chihuahua': 'CHIH', 'Ciudad de México': 'CDMX', 'Coahuila': 'COAH', 'Colima': 'COL',
    'Durango': 'DGO', 'Estado de México': 'MEX', 'Guanajuato': 'GTO', 'Guerrero': 'GRO', 'Hidalgo': 'HGO',
    'Jalisco': 'JAL', 'Michoacán': 'MICH', 'Morelos': 'MOR', 'Nayarit': 'NAY', 'Nuevo León': 'NL', 'Oaxaca': 'OAX',
    'Puebla': 'PUE', 'Querétaro': 'QRO', 'Quintana Roo': 'QROO', 'San Luis Potosí': 'SLP', 'Sinaloa': 'SIN',
    'Sonora': 'SON', 'Tabasco': 'TAB', 'Tamaulipas': 'TAMS', 'Tlaxcala': 'TLX', 'Veracruz': 'VER',
    'Yucatán': 'YUC', 'Zacatecas': 'ZAC',
}
CARGOS_SENALES = {
    'tope': {'ico': '⚖️', 'tit': 'Tope constitucional (art. 127)', 'ley': 'CPEUM',
             'que': 'Nadie en el servicio público puede ganar más que la persona titular del Ejecutivo Federal en el presupuesto de ese año.',
             'reglas': {
                 'tope': 'Verde si la remuneración anual completa queda por debajo de la de la Presidenta; rojo si la rebasa. '
                         'Sin color si la cifra publicada es parcial y queda por debajo: con lo que falta podría acercarse, '
                         'así que no se puede afirmar. Se compara neto contra neto (CPEUM, art. 127, fr. II).',
                 'tope-sin-neto': 'Sin color: falta la remuneración neta, y el tope se compara neto contra neto (CPEUM, art. 127, fr. II).',
                 'tope-sin-doc': 'Sin color: no hay remuneración documentada que comparar (CPEUM, art. 127, fr. II).'}},
    'transparencia': {'ico': '🔎', 'tit': 'Publica lo que paga', 'ley': 'LGTAIP',
                      'que': 'Cada institución debe publicar la remuneración bruta y la neta de todo su personal, con todas sus percepciones y su periodicidad.',
                      'reglas': {
                          'transparencia': 'Verde si el documento oficial de 2026 trae la remuneración bruta y la neta; ámbar si solo trae la bruta. '
                                           'Sin color si la plataforma no localizó el documento de 2026: puede existir y no lo hemos integrado '
                                           '(Ley General de Transparencia, art. 65, fr. VII).'}},
}
# Las fuentes de estos documentos se consultaron entre el 25 y el 28 de
# septiembre de 2026 (poderes, comparador salarial, congresos locales).
CARGOS_CORTE = 'septiembre de 2026'
CARGOS_TIPOS = [
    # (id, icono, nombre, explicacion)
    ('adm', '🏛️', 'Administración presidencial', 'Cada sexenio, de Salinas a Sheinbaum'),
    ('dip-fed', '📜', 'Diputación federal', 'Las 500 curules de la Cámara de Diputados'),
    ('senado', '🗳️', 'Senaduría', 'Los 128 escaños de la Cámara de Senadores'),
    ('dip-loc', '🗺️', 'Diputación local', 'El congreso de cada uno de los 32 estados'),
    ('scjn', '⚖️', 'Suprema Corte', 'Ministras, ministros, su ponencia y sus asesores'),
]


def radar_cargos(base):
    cs, pd = base['comparador_salarial'], base['poderes']
    cargo = {c['id']: c for c in cs['cargos']}
    remu = {r['id']: r for r in pd['remuneraciones2026']}
    fuentes = {}

    def usa(k):
        if k in fuentes:
            return k
        for cat in (CARGOS_FUENTES, pd['fuentes'], cs['fuentes']):
            if k in cat:
                c = cat[k]
                fuentes[k] = {'corto': c.get('corto') or c.get('doc', k)[:90], 'url': c.get('url', '')}
                return k
        raise SystemExit('ERROR: fuente %s sin catalogo' % k)

    def fila(t, v, u, est, f, pag='', op='', nota='', v2=None, pid='', k=''):
        r = {'t': t, 'u': u, 'est': est}
        if k:
            r['k'] = k
        if v is not None:
            r['v'] = v
        if v2 is not None and v2 != v:
            r['v2'] = v2
        if f:
            r['f'] = usa(f)
        for k, x in (('pag', pag), ('op', op), ('nota', nota), ('pid', pid)):
            if x:
                r[k] = x
        return r

    def texto(t, txt, est, f, pag='', nota=''):
        r = fila(t, None, 'txt', est, f, pag, nota=nota)
        r['txt'] = txt
        return r

    def pesos(x):
        return '$' + format(x, ',.2f' if x != int(x) else ',.0f')

    # ----- La institucion como organo (pedido del autor, 10-10-2026) -----
    # Lo que nos cuesta toda la institucion, y del dinero que ejercio a lo que
    # reviso la ASF y lo que quedo por aclarar. Las dos secciones llevan
    # 'panel': el anverso las pinta como grafica; el sello las firma igual.
    pob = base['calculadora_civica']['parametros']['poblacion']['personas']
    mdb = {o['id']: o for o in base['inspector_poderes']['organos']}

    def pct(a, b):
        return round(a / b * 100, 1)

    def costo(inst, aprobado, sp, sp_total, sp_f, sp_pag, sp_op):
        dia, hab, ps = round(aprobado / 365), round(aprobado / pob, 2), pct(sp, sp_total)
        return {'tit': 'Lo que nos cuesta %s' % inst, 'panel': 'costo', 'filas': [
            fila('Presupuesto aprobado 2026', aprobado, '$g', 'oficial', 'PEF', 'Anexo 1, DOF p. 32', k='total'),
            fila('Cada día de 2026', dia, '$', 'derivado', 'PEF', 'Anexo 1, DOF p. 32', k='dia',
                 op='%s ÷ 365 días.' % pesos(aprobado)),
            fila('A cada habitante, en el año', hab, '$', 'derivado', 'CONAPO', k='hab',
                 op='%s ÷ %s habitantes. La población es derivada: suma de las 32 entidades, las 110 edades y ambos sexos del archivo del CONAPO.' % (
                     pesos(aprobado), format(pob, ','))),
            fila('Lo que se fue en sueldos y prestaciones de todo su personal, 2025', ps, 'pct100', 'derivado', sp_f, sp_pag, k='pers',
                 op='%s del capítulo 1000 (servicios personales) ÷ %s %s × 100 = %s%%.' % (pesos(sp), pesos(sp_total), sp_op, format(ps, ',.1f'))),
        ], 'nota': 'Es toda la institución: sus integrantes, su personal, sus edificios y sus servicios. El presupuesto lo paga el erario federal, '
                   'es decir, los impuestos y demás ingresos de la Federación.'}

    def embudo_fed(oid, ejercido, ej_est, ej_f, ej_pag, ej_op, univ=None, muestra=None, res=()):
        a = mdb[oid]['asf'][0]
        fs = [fila('Ejerció en 2024', ejercido, '$g', ej_est, ej_f, ej_pag, op=ej_op, k='recibio')]
        if univ:
            fs.append(fila('Universo que seleccionó la ASF', univ['pesos'], '$g', univ['estado'], univ['fuente'], 'p. %s' % univ['pagina'], k='universo'))
        if muestra:
            fs.append(fila('Muestra que revisó la ASF', muestra['pesos'], '$g', muestra['estado'], muestra['fuente'], 'p. %s' % muestra['pagina'], k='muestra'))
            pr = pct(muestra['pesos'], ejercido)
            fs.append(fila('Parte de lo ejercido que revisó la ASF', pr, 'pct100', 'derivado', muestra['fuente'], 'p. %s' % muestra['pagina'],
                           op='%s de la muestra ÷ %s ejercidos × 100 = %s%%.' % (pesos(muestra['pesos']), pesos(ejercido), format(pr, ',.1f'))))
            fs.append(fila('Lo que quedó fuera de la muestra', ejercido - muestra['pesos'], '$g', 'derivado', muestra['fuente'], 'p. %s' % muestra['pagina'],
                           op='%s − %s. Que no se revisara no quiere decir que haya irregularidad: la ASF audita por muestra.' % (
                               pesos(ejercido), pesos(muestra['pesos']))))
        else:
            fs.append(fila('La muestra, como parte del universo que seleccionó la ASF', a['repr'], 'pct100', 'oficial', 'ASF_MDB', 'p. 31',
                           nota='La Matriz publica la representatividad de la muestra, no su monto en pesos.'))
        fs += [fila('Acciones que promovió la ASF', sum(a['acc']), 'ent', 'oficial', 'ASF_MDB', 'p. 31', k='acciones'),
               fila('Monto por aclarar', a['porAclarar'], '$', 'oficial', 'ASF_MDB', 'p. 31', k='aclarar',
                    nota='Lo que la ASF observó y la institución aún debe justificar o devolver.'),
               fila('Recuperaciones', a['recuperaciones'], '$', 'oficial', 'ASF_MDB', 'p. 31', k='recup',
                    nota='Lo que la Matriz de la ASF reporta como recuperado en esta auditoría.')]
        fs += [texto('Resultado', x['texto'], x['estado'], x['fuente'], 'p. %s' % x['pagina']) for x in res]
        return {'tit': 'Del dinero que ejerció a lo que falta aclarar: Cuenta Pública 2024', 'panel': 'embudo', 'filas': fs,
                'nota': 'Auditoría de %s (%s), %s entrega del informe de la Cuenta Pública 2024. «Sin irregularidades» se refiere a la muestra revisada, no a todo el gasto.' % (
                    a['titulo'].lower(), a['tipo'].lower(), {1: 'primera', 2: 'segunda', 3: 'tercera'}[a['entrega']])}

    tope = remu['presidencia']['netoAnual']
    tope_f = fila('Tope: remuneración total anual neta de la Presidenta', tope, '$', 'oficial', 'PEF', remu['presidencia']['pagina'])

    def senal_tope(neto, completo, op, f, pag, est='derivado'):
        pct = round(neto / tope * 100, 1)
        c = 'rojo' if neto > tope else ('verde' if completo else None)
        return {'id': 'tope', 'c': c,
                'x': fila('Remuneración anual neta', neto, '$', est, f, pag, op=op),
                'extra': [fila('Proporción del tope', pct, 'pct100', 'derivado', None,
                               op='%s ÷ %s × 100 = %s%%.' % (pesos(neto), pesos(tope), format(pct, ',.1f'))), tope_f],
                'r': 'tope'}

    def senal_transp(c, txt):
        return {'id': 'transparencia', 'c': c,
                'x': dict({'t': 'Lo que hay', 'u': 'txt', 'est': 'oficial' if c else 'pendiente', 'txt': txt},
                          **({} if c else {'pid': 'poderes-legislativo-0'})),
                'extra': [],
                'r': 'transparencia'}

    docs = []
    # ===================== Diputación federal =====================
    dr, dc, ac = remu['diputados'], cargo['diputados'], cargo['asesor_diputados']
    ho = ac['honorarios']
    leg = pd['ramos2026']['legislativo']
    dip26 = [u for u in leg['unidades'] if u['id'] == 'diputados'][0]
    cp25 = [u for u in pd['ejercicio']['cp2025']['unidades'] if u['ramo'] == '01' and u['ur'] == '100'][0]
    av26 = [u for u in pd['ejercicio']['avance2026']['unidades'] if u['ramo'] == '01' and u['ur'] == '100'][0]
    corte_av = pd['ejercicio']['avance2026']['corte']
    caps25 = pd['ejercicio']['cp2025']['capitulosLegislativo']['100']
    asf24 = [x for x in pd['legislativo']['ejercicio2024'] if x['institucion'] == 'Diputados']
    res24 = [x for x in pd['legislativo']['resultadosAsf'] if x['institucion'] == 'Diputados']
    pct_av = round(av26['pagado'] / av26['modificado'] * 100, 1)
    dif25 = round((cp25['ejercido'] - cp25['original']) / cp25['original'] * 100, 1)
    docs.append({
        'id': 'dip-fed', 'tipo': 'dip-fed', 'ini': 'DIPFED', 'col': '#7a1f3d', 'corte': CARGOS_CORTE,
        'tipoTx': 'Estado de cuenta de la diputación federal', 'n': 'Diputada o diputado federal',
        'sub': 'Cámara de Diputados · LXVI Legislatura · cifras de 2024 a 2026',
        'aviso': 'Es el estado de cuenta del cargo, no de una persona: las 500 curules cobran lo mismo, según el Manual de remuneraciones de la Cámara.',
        'senales': [
            senal_tope(dr['netoAnual'], True, 'Remuneración total anual neta del Anexo 23.3.4. El propio anexo aclara que corresponde a las percepciones de 2025.',
                       'PEF', dr['pagina'], 'oficial'),
            senal_transp('verde', 'El Manual 2026 publica la dieta neta mensual y el Anexo 23 del PEF, la bruta y la neta anuales.'),
        ],
        'secciones': [
            costo('la Cámara de Diputados', dip26['aprobado'], [c for c in caps25 if c['cap'] == '1000'][0]['ejercido'], cp25['ejercido'],
                  'CP2025', 'capítulo 1000', 'ejercidos por la Cámara en 2025'),
            embudo_fed('diputados', [x for x in asf24 if x['concepto'] == 'Pagado'][0]['pesos'], 'oficial', 'ASF_DIP', 'p. 4',
                       'Lo pagado en 2024 según la auditoría de la ASF; coincide con el modificado.',
                       [x for x in asf24 if x['concepto'].startswith('Universo')][0], [x for x in asf24 if x['concepto'].startswith('Muestra')][0], res24),
            {'tit': 'Lo que cobra una diputada o diputado', 'filas': [
                fila('Dieta neta mensual 2026', dc['mensual']['max'], '$', dc['mensualEstado'], 'DIP', 'p. 144',
                     nota='La dieta es la remuneración por la representación política; es irrenunciable.'),
                fila('Remuneración total anual bruta', dr['brutoAnual'], '$', 'oficial', 'PEF', dr['pagina']),
                fila('ISR retenido en el año', dr['isrAnual'], '$', 'oficial', 'PEF', dr['pagina']),
                fila('Remuneración total anual neta', dr['netoAnual'], '$', 'oficial', 'PEF', dr['pagina'], nota=dr['nota']),
                fila('Aguinaldo (40 días de dieta, bruto)', dr['aguinaldo'], '$', 'oficial', 'PEF', dr['pagina']),
                fila('ISR del aguinaldo que paga la Cámara, no el diputado', 67785, '$', 'oficial', 'PEF', 'Anexo 23.3.4, nota 4, DOF p. 68',
                     nota='A cualquier trabajador se le retiene el impuesto de su aguinaldo; aquí lo cubre el presupuesto.'),
            ]},
            {'tit': 'Sus asesores', 'filas': [
                fila(s['nombre'], s['min'], '$', ac['mensualEstado'], 'DIP', ac['pagina'], v2=s['max'],
                     nota='Remuneración neta mensual del nivel.') for s in ac['subniveles']] + [
                fila('Contratos por honorarios (partida 1210)', ho['contratos'], 'ent', 'oficial', 'DIP', ho['pagina']),
                fila('Lo que suman esos contratos en el año', ho['montoAnual'], '$g', 'oficial', 'DIP', ho['pagina']),
                fila('Promedio mensual por contrato', ho['promedioMensual'], '$', 'derivado', 'DIP', ho['pagina'], op=ho['operacion'] + '.'),
            ], 'nota': ac['nota']},
            {'tit': 'La Cámara de Diputados: su presupuesto', 'filas': [
                fila('Integrantes', 500, 'ent', 'oficial', 'CPEUM', 'art. 52', nota='300 de mayoría relativa y 200 de representación proporcional.'),
                fila('Pagado al ' + corte_av, av26['pagado'], '$g', 'oficial', 'AV2T2026'),
                fila('Avance del año', pct_av, 'pct100', 'derivado', 'AV2T2026',
                     op='%s pagados ÷ %s del modificado × 100 = %s%%. A la mitad del año, el ritmo parejo sería 50%%.' % (
                         pesos(av26['pagado']), pesos(av26['modificado']), format(pct_av, ',.1f'))),
                fila('Aprobado 2025', cp25['original'], '$g', 'oficial', 'CP2025'),
                fila('Ejercido 2025', cp25['ejercido'], '$g', 'oficial', 'CP2025'),
                fila('Ejercido contra aprobado, 2025', dif25, 'pct', 'derivado', 'CP2025',
                     op='(%s − %s) ÷ %s × 100 = %s%%.' % (pesos(cp25['ejercido']), pesos(cp25['original']), pesos(cp25['original']),
                                                         ('+' if dif25 > 0 else '') + format(dif25, ',.1f'))),
            ], 'nota': 'No dividimos el presupuesto entre las 500 curules: ese reparto no es lo que cuesta cada diputado, porque la Cámara también paga personal, edificios y el Canal del Congreso.'},
            {'tit': 'En qué gastó la Cámara en 2025', 'filas': [
                fila(c['concepto'], c['ejercido'], '$g', 'oficial', 'CP2025', 'capítulo ' + c['cap']) for c in caps25]},
            {'tit': 'Su nómina de 2024, partida por partida', 'filas': [
                fila('%s · %s' % (x['partida'], x['concepto']), x['pesos'], '$g', x['estado'], x['fuente'], 'p. %s' % x['pagina'])
                for x in pd['legislativo']['personalDiputados2024']],
             'nota': 'Lo que la Cámara pagó en servicios personales en 2024, según la auditoría de la ASF: dietas, sueldos, honorarios, compensaciones y prestaciones de todo su personal.'},
        ]})

    # ===================== Senaduría =====================
    sr, sc, asn = remu['senado'], cargo['senado'], cargo['asesor_senado']
    sen26 = [u for u in leg['unidades'] if u['id'] == 'senado'][0]
    scp25 = [u for u in pd['ejercicio']['cp2025']['unidades'] if u['ramo'] == '01' and u['ur'] == '200'][0]
    sav26 = [u for u in pd['ejercicio']['avance2026']['unidades'] if u['ramo'] == '01' and u['ur'] == '200'][0]
    scaps25 = pd['ejercicio']['cp2025']['capitulosLegislativo']['200']
    sasf24 = [x for x in pd['legislativo']['ejercicio2024'] if x['institucion'] == 'Senado']
    sres24 = [x for x in pd['legislativo']['resultadosAsf'] if x['institucion'] == 'Senado']
    spct_av = round(sav26['pagado'] / sav26['modificado'] * 100, 1)
    sdif25 = round((scp25['ejercido'] - scp25['original']) / scp25['original'] * 100, 1)
    docs.append({
        'id': 'senado', 'tipo': 'senado', 'ini': 'SEN', 'col': '#8a5a00', 'corte': CARGOS_CORTE,
        'tipoTx': 'Estado de cuenta de la senaduría', 'n': 'Senadora o senador de la República',
        'sub': 'Cámara de Senadores · LXVI Legislatura · cifras de 2024 a 2026',
        'aviso': 'Es el estado de cuenta del cargo, no de una persona: los 128 escaños cobran lo mismo, según el Manual de remuneraciones del Senado.',
        'senales': [
            senal_tope(sr['netoAnual'], True, 'Remuneración total anual neta del Anexo 23.2.2. El propio anexo aclara que corresponde a las percepciones de 2025.',
                       'PEF', sr['pagina'], 'oficial'),
            senal_transp('verde', 'El Manual 2026 publica la dieta neta mensual y el Anexo 23 del PEF, la bruta y la neta anuales.'),
        ],
        'secciones': [
            costo('el Senado', sen26['aprobado'], [c for c in scaps25 if c['cap'] == '1000'][0]['ejercido'], scp25['ejercido'],
                  'CP2025', 'capítulo 1000', 'ejercidos por el Senado en 2025'),
            embudo_fed('senado', [x for x in sasf24 if x['concepto'] == 'Devengado'][0]['pesos'], 'oficial', 'ASF_SEN', 'p. 5',
                       'Lo devengado en 2024 según la auditoría de la ASF; de eso, %s quedaron por pagar al cierre y se pagaron en 2025.' % pesos(
                           [x for x in sasf24 if x['concepto'].startswith('Pendiente de pago')][0]['pesos']),
                       [x for x in sasf24 if x['concepto'].startswith('Universo')][0], [x for x in sasf24 if x['concepto'].startswith('Muestra')][0], sres24),
            {'tit': 'Lo que cobra una senadora o senador', 'filas': [
                fila('Dieta neta mensual 2026', sc['mensual']['max'], '$', sc['mensualEstado'], 'SEN', 'Anexo 1',
                     nota='El Manual la publica en miles (132.9). ' + sc['nota']),
                fila('Remuneración total anual bruta', sr['brutoAnual'], '$', 'oficial', 'PEF', sr['pagina']),
                fila('ISR retenido en el año', sr['isrAnual'], '$', 'oficial', 'PEF', sr['pagina']),
                fila('Remuneración total anual neta', sr['netoAnual'], '$', 'oficial', 'PEF', sr['pagina'], nota=sr['nota']),
                fila('Aguinaldo (bruto)', sr['aguinaldo'], '$', 'oficial', 'PEF', sr['pagina'],
                     nota='El Manual dice 40 días de dieta; esta cifra equivale a unos 60 días.'),
                fila('Por qué el aguinaldo equivale a 60 días y no a 40', None, '$', 'pendiente', None, pid='prest-aguinaldo-sen',
                     nota='$382,207 ÷ ($190,023 de dieta bruta mensual ÷ 30) = 60.3 días. Ningún documento explica la diferencia con el Manual.'),
                fila('Prima del seguro de vida pagada con presupuesto', 96759, '$', 'oficial', 'PEF', sr['pagina'],
                     nota='Seguro de 40 meses de dieta (Manual, Anexo 3).'),
            ]},
            {'tit': 'Sus asesores', 'filas': [
                fila(x['nombre'], x['min'], '$', asn['mensualEstado'], 'SEN', asn['pagina'], v2=x['max'],
                     nota='Percepción mensual neta del nivel.') for x in asn['subniveles']] + [
                fila('Asesor de grupo parlamentario en el año, con el máximo del nivel', asn['anual'], '$', asn['anualEstado'], 'SEN',
                     asn['pagina'], op=asn['anualOperacion'] + '.')], 'nota': asn['nota']},
            {'tit': 'El Senado: su presupuesto', 'filas': [
                fila('Integrantes', 128, 'ent', 'oficial', 'CPEUM', 'art. 56',
                     nota='Dos por estado de mayoría relativa, uno de primera minoría y 32 de representación proporcional.'),
                fila('Pagado al ' + corte_av, sav26['pagado'], '$g', 'oficial', 'AV2T2026'),
                fila('Avance del año', spct_av, 'pct100', 'derivado', 'AV2T2026',
                     op='%s pagados ÷ %s del modificado × 100 = %s%%. A la mitad del año, el ritmo parejo sería 50%%.' % (
                         pesos(sav26['pagado']), pesos(sav26['modificado']), format(spct_av, ',.1f'))),
                fila('Aprobado 2025', scp25['original'], '$g', 'oficial', 'CP2025'),
                fila('Ejercido 2025', scp25['ejercido'], '$g', 'oficial', 'CP2025'),
                fila('Ejercido contra aprobado, 2025', sdif25, 'pct', 'derivado', 'CP2025',
                     op='(%s − %s) ÷ %s × 100 = %s%%.' % (pesos(scp25['ejercido']), pesos(scp25['original']), pesos(scp25['original']),
                                                         ('+' if sdif25 > 0 else '') + format(sdif25, ',.1f'))),
            ], 'nota': 'No dividimos el presupuesto entre los 128 escaños: ese reparto no es lo que cuesta cada senador, porque el Senado también paga personal, edificios y el Canal del Congreso.'},
            {'tit': 'En qué gastó el Senado en 2025', 'filas': [
                fila(c['concepto'], c['ejercido'], '$g', 'oficial', 'CP2025', 'capítulo ' + c['cap']) for c in scaps25]},
            {'tit': 'Lo que gastó en 2024, capítulo por capítulo', 'filas': [
                fila('%s · %s (devengado)' % (x['cap'], x['concepto']), x['devengado'], '$g', x['estado'], x['fuente'], 'p. %s' % x['pagina'])
                for x in pd['legislativo']['senadoCapitulos2024']],
             'nota': 'Según la auditoría de la ASF a la Cámara de Senadores.'},
        ]})

    # ===================== Diputación local (las 32) =====================
    loc = cargo['diputado_local']
    ents = {e['nombre']: e for e in loc['entidades']}
    cnple = {c['entidad']: c for c in pd['legislativo']['congresos2024']}
    asfc = {}
    for x in pd['legislativo']['asfCongresos2024']:
        asfc.setdefault(x['congreso'].replace('Congreso de ', ''), []).append(x)
    faltan = sorted(set(CARGOS_ENTIDADES) ^ set(cnple))
    if faltan:
        raise SystemExit('ERROR: entidades sin abreviatura o sin CNPLE: %s' % ', '.join(faltan))
    for nombre in sorted(CARGOS_ENTIDADES, key=lambda s: s.replace('Á', 'A')):
        ab, en, cn = CARGOS_ENTIDADES[nombre], ents.get(nombre), cnple[nombre]
        pago, senales = [], []
        if en:
            pago.append(fila('Remuneración bruta mensual', en['bruto'], '$', en['brutoEstado'], en['fuente'], en['pagina'],
                             v2=en.get('brutoHasta')))
            pid_neto = 'neto-%s-%s' % (loc['id'], nombre.lower().replace(' ', '-'))
            if en.get('neto') is not None:
                pago.append(fila('Remuneración neta mensual', en['neto'], '$', en['netoEstado'], en['fuente'], en['pagina']))
                anual = round(en['neto'] * 12, 2)
                pago.append(fila('Neta en el año, sin aguinaldo', anual, '$', 'derivado', en['fuente'], en['pagina'],
                                 op='12 × %s. No incluye aguinaldo ni prima vacacional, así que es parcial.' % pesos(en['neto'])))
                senales.append(senal_tope(anual, False, '12 × %s de remuneración neta mensual; sin aguinaldo ni prima vacacional.' % pesos(en['neto']),
                                          en['fuente'], en['pagina']))
                senales.append(senal_transp('verde', 'Su documento de 2026 trae la remuneración bruta y la neta.'))
            else:
                pago.append(fila('Remuneración neta mensual', None, '$', 'pendiente', None,
                                 nota='El documento publica la bruta, no la neta.', pid=pid_neto))
                senales.append({'id': 'tope', 'c': None, 'r': 'tope-sin-neto', 'extra': [tope_f],
                                'x': fila('Remuneración anual neta', None, '$', 'pendiente', None, pid=pid_neto,
                                          nota='Sin la neta no se compara con el tope, que se mide neto contra neto.')})
                senales.append(senal_transp('ambar', 'Su documento de 2026 trae la remuneración bruta, pero no la neta.'))
            pago.append(texto('Cómo se integra', en['concepto'], en['brutoEstado'], en['fuente'], en['pagina']))
        else:
            pago.append(fila('Remuneración mensual 2026', None, '$', 'pendiente', None, pid='poderes-legislativo-0',
                             nota='La plataforma no localizó el documento oficial de 2026 de este congreso.'))
            senales.append({'id': 'tope', 'c': None, 'r': 'tope-sin-doc', 'extra': [tope_f],
                            'x': fila('Remuneración anual neta', None, '$', 'pendiente', None, pid='poderes-legislativo-0')})
            senales.append(senal_transp(None, 'La plataforma no localizó su documento de 2026. Puede estar en la Plataforma Nacional de Transparencia.'))
        ej = round(cn['ejercidoMdp'] * 1e6)
        aud = asfc.get(nombre)
        secs = [{'tit': 'Lo que nos costó el congreso del estado', 'panel': 'costo', 'filas': [
            fila('Lo que ejerció en 2024', ej, '$g', cn['estado'], cn['fuente'], 'p. %s' % cn['pagina'], k='total',
                 nota='Todo el congreso: diputados, personal, edificio y órgano de fiscalización si depende de él.'),
            fila('Cada día de 2024', round(ej / 366), '$', 'derivado', cn['fuente'], 'p. %s' % cn['pagina'], k='dia',
                 op='%s ÷ 366 días (2024 fue bisiesto).' % pesos(ej))],
            'nota': 'Un congreso local no recibe dinero federal directo: lo paga el presupuesto de su estado, que se financia en buena parte con '
                    'participaciones federales (Ramo 28). Por eso la ASF puede revisar la parte que pagó con ellas. No damos el costo por habitante: '
                    'la plataforma aún no integra la población de 2024 del CONAPO, y dividir el gasto de 2024 entre la de 2026 mezclaría años. '
                    + ('' if aud else 'La plataforma solo tiene integradas las auditorías de la ASF a los congresos de Nuevo León y Tlaxcala en la '
                                      'Cuenta Pública 2024; la de este congreso, si la hubo, aún no está integrada.')}]
        if aud:
            k_asf = {'Universo seleccionado': 'universo', 'Muestra auditada': 'muestra', 'Monto por aclarar': 'aclarar',
                     'Recuperaciones; incluye cargas financieras': 'recup'}
            fs = [fila('Ejerció en 2024 (todas sus fuentes)', ej, '$g', cn['estado'], cn['fuente'], 'p. %s' % cn['pagina'], k='recibio')]
            for x in aud:
                fs.append(fila(x['concepto'], x['pesos'], '$g' if x['pesos'] >= 1e6 else '$', x['estado'], x['fuente'], 'p. %s' % x['pagina'],
                               k=k_asf.get(x['concepto'], '')))
                if x['concepto'] == 'Muestra auditada':
                    pr = pct(x['pesos'], ej)
                    fs.append(fila('Parte de lo ejercido que revisó la ASF', pr, 'pct100', 'derivado', x['fuente'], 'p. %s' % x['pagina'],
                                   op='%s de la muestra ÷ %s ejercidos (INEGI) × 100 = %s%%.' % (pesos(x['pesos']), pesos(ej), format(pr, ',.1f'))))
            secs.append({'tit': 'Del dinero que ejerció a lo que falta aclarar: Cuenta Pública 2024', 'panel': 'embudo', 'filas': fs,
                         'nota': 'Auditoría %s de la ASF. Revisó las participaciones federales que pagó este congreso, no todo su gasto. '
                                 'Lo que no aparece aquí, la Matriz no lo reporta para esta auditoría.' % aud[0]['auditoria']})
        secs += [
            {'tit': 'Lo que cobra una diputada o diputado local', 'filas': pago, 'nota': '' if en else '@local'},
            {'tit': 'Sus asesores', 'filas': [fila('Remuneración de asesores y personal de apoyo', None, '$', 'pendiente', None,
                                                   pid='asesores-congresos-locales',
                                                   nota='Cada congreso debe publicarla; la plataforma aún no integra esos tabuladores.')]},
        ]
        docs.append({
            'id': 'dip-loc-' + ab.lower(), 'tipo': 'dip-loc', 'ent': nombre, 'conDoc': bool(en), 'ini': 'DL' + ab,
            'col': '#0b6e4f', 'corte': CARGOS_CORTE,
            'tipoTx': 'Estado de cuenta de la diputación local', 'n': 'Diputada o diputado local de ' + nombre,
            'sub': 'Congreso del estado de %s · cifras de 2024 a 2026' % nombre,
            'aviso': ('Es el estado de cuenta del cargo, no de una persona. Cada congreso paga con conceptos distintos: no se compara renglón a renglón con otro estado.'
                      if en else 'De este congreso aún no tenemos el documento oficial de 2026 con lo que paga: el estado de cuenta muestra lo que sí está documentado y dice qué falta.'),
            'senales': senales, 'secciones': secs})

    # ===================== Suprema Corte, su ponencia y sus asesores =====================
    mi, se_, asr = cargo['ministro'], cargo['secretario_estudio'], cargo['asesor_scjn']
    scjn26 = [u for u in pd['ramos2026']['judicial']['unidades'] if u['id'] == 'scjn'][0]
    ago = pd['judicial']['scjnAgosto']
    c25 = {c['concepto']: c for c in pd['judicial']['scjnCortes'] if c['corte'] == '2025-12-31'}
    recorte = scjn26['proyecto'] - scjn26['aprobado']
    pct_ago = round(ago['ejercido'] / ago['modificado'] * 100, 1)

    def ponencia(c):
        r = [fila(c['cargo'] + ': sueldo neto mensual', c['mensual']['min'], '$', c['mensualEstado'], c['fuente'], c['pagina'], v2=c['mensual']['max']),
             fila('Aguinaldo y prima vacacional netos', c['aguinaldoPrima']['min'], '$', 'oficial', c['fuente'], c['pagina'], v2=c['aguinaldoPrima']['max'])]
        if c.get('asignaciones'):
            r.append(fila('Asignaciones adicionales netas', c['asignaciones']['min'], '$', 'oficial', c['fuente'], c['pagina'], v2=c['asignaciones']['max']))
        r.append(fila('En el año, con el máximo de cada rango', c['anual'], '$', c['anualEstado'], c['fuente'], c['pagina'],
                      op=c['anualOperacion'] + '. Parcial: sin seguros ni aportaciones de seguridad social.'))
        return r
    docs.append({
        'id': 'scjn', 'tipo': 'scjn', 'ini': 'SCJN', 'col': '#5b3a8c', 'corte': CARGOS_CORTE,
        'tipoTx': 'Estado de cuenta de la Suprema Corte', 'n': 'Ministra o ministro de la Suprema Corte',
        'sub': 'Con su ponencia y sus asesores · cifras de 2025 y 2026',
        'aviso': 'Es el estado de cuenta del cargo, no de una persona: las nueve ministras y ministros cobran con el mismo tabulador del Manual de remuneraciones del Poder Judicial.',
        'senales': [
            senal_tope(mi['anual'], False, mi['anualOperacion'] + '.', mi['fuente'], mi['pagina']),
            senal_transp('verde', 'El Manual 2026 publica el sueldo neto tabulado de cada puesto de la Corte.'),
        ],
        'secciones': [
            costo('la Suprema Corte', scjn26['aprobado'], c25['Servicios personales']['devengado'], c25['Total']['devengado'],
                  c25['Servicios personales']['fuente'], 'p. %s' % c25['Servicios personales']['pagina'],
                  'devengados en total por la Corte en 2025'),
            embudo_fed('scjn', round(mdb['scjn']['cp2024']['ejercido'] * 1e6), 'derivado', 'CP2024', '',
                       'Suma de la unidad responsable 100 del Ramo 03 en los datos abiertos de la Cuenta Pública 2024, en millones redondeados a un decimal.'),
            {'tit': 'Lo que cobra una ministra o ministro', 'filas': [
                fila('Sueldo neto mensual del tabulador', mi['mensual']['max'], '$', mi['mensualEstado'], mi['fuente'], 'Anexo B, p. 8'),
                fila('Aguinaldo y prima vacacional netos', mi['aguinaldoPrima']['max'], '$', 'oficial', mi['fuente'], 'Anexo B, p. 9'),
                fila('En el año', mi['anual'], '$', mi['anualEstado'], mi['fuente'], mi['pagina'], op=mi['anualOperacion'] + '.', nota=mi['nota']),
                fila('Integrantes del Pleno', 9, 'ent', 'oficial', 'CPEUM', 'art. 94'),
            ]},
            {'tit': 'Su ponencia: quien proyecta las sentencias', 'filas': ponencia(se_), 'nota': se_['nota']},
            {'tit': 'Sus asesores', 'filas': ponencia(asr) + [
                fila('Cuántas plazas tiene cada ponencia y cuánto cuesta completa', None, '$', 'pendiente', None, pid='poderes-judicial-1',
                     nota='La Corte no publica el costo desglosado por ponencia. Las cifras que circulaban (35 colaboradores, $34.2 millones por ponencia) se retiraron porque no tienen documento.')],
             'nota': asr['nota']},
            {'tit': 'La Suprema Corte: su presupuesto', 'filas': [
                fila('Proyecto 2026', scjn26['proyecto'], '$g', 'oficial', 'PEF', 'Anexo 32, DOF p. 108'),
                fila('Recorte de la Cámara de Diputados', recorte, '$g', 'derivado', 'PEF', 'Anexo 32, DOF p. 108',
                     op='%s del proyecto − %s aprobados.' % (pesos(scjn26['proyecto']), pesos(scjn26['aprobado']))),
                fila('Ejercido al 31 de agosto de 2026', ago['ejercido'], '$g', ago['estado'], ago['fuente'], 'p. %s' % ago['pagina'], nota=ago['nota']),
                fila('Avance del año', pct_ago, 'pct100', 'derivado', ago['fuente'],
                     op='%s ejercidos ÷ %s del modificado × 100 = %s%%. A fines de agosto, el ritmo parejo sería 66.7%%.' % (
                         pesos(ago['ejercido']), pesos(ago['modificado']), format(pct_ago, ',.1f'))),
            ], 'nota': 'El aprobado de 2026 está arriba, en lo que nos cuesta la Corte.'},
            {'tit': 'Lo aprobado para 2026, capítulo por capítulo', 'filas': [
                fila(c['concepto'], c['aprobado'], '$g', c['estado'], c['fuente'], 'p. %s' % c['pagina'])
                for c in pd['judicial']['capitulosPorUR']['100']]},
            {'tit': 'Cómo cerró 2025', 'filas': [
                fila(k + ' (devengado)', c25[k]['devengado'], '$g', c25[k]['estado'], c25[k]['fuente'], 'p. %s' % c25[k]['pagina'])
                for k in c25], 'nota': 'Estado analítico del ejercicio de la propia Corte, enero a diciembre de 2025.'},
        ]})
    usa('CPEUM')
    usa('LGTAIP')
    return {'tipos': [{'id': t[0], 'ico': t[1], 'n': t[2], 'sub': t[3]} for t in CARGOS_TIPOS],
            'senales': CARGOS_SENALES, 'notaLocal': loc['nota'], 'docs': docs, 'fuentes': fuentes}


def radar():
    import auditorias
    import datetime
    base = auditorias.db()
    fs = base['finanzas_sexenales']
    ps = fs['peso']
    ev = {f['id']: f for f in base['evaluacion_sexenal']['filas']}
    cp = base['cuenta_publica_asf']
    fuentes = {}
    falta = fs['faltantes']['anio']
    prom, mes, ref, (uy, um) = _peso_base(ps)
    ref_mes = '%s de %d' % (MESES[um - 1], uy)

    def usa(k, catalogo):
        if k and k not in fuentes and k in catalogo:
            c = catalogo[k]
            fuentes[k] = {'corto': c.get('corto') or c.get('doc', k)[:90], 'url': c.get('url', '')}
        return k
    for k in ps['fuentes']:
        usa(k, ps['fuentes'])

    def mdp(v):
        return format(round(v, 1), ',.1f')

    def conversiones(datos, anios, fts):
        """La suma del sexenio en pesos de hoy, en dolares y en euros."""
        filas = [(y, datos[str(y)]['mdp']) for y in anios]
        alt = {}
        alt['hoy'] = {'v': round(sum(m * ref / prom(ps['inpc'], y) for y, m in filas), 1), 'est': 'derivado',
                      'f': fts + [ps['inpc']['f']],
                      'op': 'Cada año pasado a pesos de %s: monto × INPC de %s (%s) ÷ INPC promedio de ese año; luego se suman los %d años. %s'
                            % (ref_mes, ref_mes, format(ref, '.3f'), len(filas),
                               ' · '.join('%d: %s × %s ÷ %s' % (y, mdp(m), format(ref, '.3f'), format(prom(ps['inpc'], y), '.3f')) for y, m in filas))}
        alt['usd'] = {'v': round(sum(m / prom(ps['usd'], y) for y, m in filas), 1), 'est': 'derivado',
                      'f': fts + [ps['usd']['f']],
                      'op': 'Cada año entre su tipo de cambio promedio (pesos por dólar), en millones de dólares; luego se suman. %s'
                            % ' · '.join('%d: %s ÷ %s' % (y, mdp(m), format(prom(ps['usd'], y), '.4f')) for y, m in filas)}
        if anios[0] >= ps['eur']['desde']:
            alt['eur'] = {'v': round(sum(m / prom(ps['eur'], y) for y, m in filas), 1), 'est': 'derivado',
                          'f': fts + [ps['eur']['f']],
                          'op': 'Cada año entre su tipo de cambio promedio (pesos por euro), en millones de euros; luego se suman. %s'
                                % ' · '.join('%d: %s ÷ %s' % (y, mdp(m), format(prom(ps['eur'], y), '.4f')) for y, m in filas)}
        else:
            alt['eur'] = {'na': ps['eur']['antes'], 'et': 'sin euro'}
        return alt

    admins, valores, obras = [], {}, {}
    for (aid, nombre, corto, ini, (a0, a1), col, curso) in RADAR_ADMINS:
        todos = list(range(a0, a1 + 1))
        anios = [y for y in todos if str(y) in fs['anual']['ingresos']]
        faltan = [] if curso else [y for y in todos if y not in anios]
        periodo = '%d–%d · %s' % (a0, a1, 'en curso' if curso else 'seis años calendario')
        aviso = ''
        if curso:
            aviso = 'Sexenio en curso: solo %s, el único año cerrado. No se compara como sexenio completo.' % ', '.join(map(str, anios))
        elif faltan:
            aviso = 'Se mide con %d a %d: falta %s, que no está en la serie de Hacienda.' % (anios[0], anios[-1], ', '.join(map(str, faltan)))
        admins.append({'id': aid, 'n': nombre, 'c': corto, 'ini': ini, 'a': [a0, a1], 'col': col, 'curso': curso,
                       'periodo': periodo, 'aviso': aviso, 'ys': [anios[0], anios[-1]] if anios else None})
        v = {}
        rango = '%d a %d' % (anios[0], anios[-1]) if anios and anios[0] != anios[-1] else (str(anios[0]) if anios else '')
        for serie in RADAR_SERIES:
            datos = fs['anual'][serie]
            filas = [datos[str(y)] for y in anios]
            fts = []
            for x in filas:
                for k in x['f']:
                    if k not in fts:
                        fts.append(usa(k, fs['fuentes']))
            prom_pib = round(sum(x['pib'] for x in filas) / len(filas), 1)
            v[serie + '_pib'] = {'v': prom_pib, 'est': 'derivado', 'f': fts,
                                 'op': 'Promedio de %d %s (%s): (%s) ÷ %d.' % (len(filas), 'año' if len(filas) == 1 else 'años', rango,
                                       ' + '.join(str(x['pib']) for x in filas), len(filas)),
                                 'nota': (falta['motivo'] if faltan else ''), 'pid': falta['pid'] if faltan else ''}
            if faltan:
                v[serie + '_mdp'] = {'pend': falta['motivo'] + ' Una suma con cinco años no se compara con las de seis.', 'pid': falta['pid']}
                continue
            v[serie + '_mdp'] = {'v': round(sum(x['mdp'] for x in filas), 1), 'est': 'derivado', 'f': fts,
                                 'op': 'Suma de %s, en millones de pesos de cada año: %s.' % (rango, ' + '.join(mdp(x['mdp']) for x in filas)),
                                 'alt': conversiones(datos, anios, fts)}
        # Deuda al recibir y al entregar
        dd = fs['deuda'].get(aid, {})
        for k, m in (('dIni', 'deuda_ini'), ('dFin', 'deuda_fin')):
            x = dd.get(k)
            v[m] = ({'v': x['v'], 'est': 'oficial', 'f': [usa(x['f'], fs['fuentes'])], 'nota': x.get('nota', '')}
                    if x else {'na': dd.get('pend', 'Sin serie comparable para ese año.'), 'et': 'en curso' if curso else 'sin serie comparable'})
        if dd.get('dIni') and dd.get('dFin'):
            v['deuda_cambio'] = {'v': round(dd['dFin']['v'] - dd['dIni']['v'], 1), 'est': 'derivado',
                                 'f': sorted({usa(dd['dIni']['f'], fs['fuentes']), usa(dd['dFin']['f'], fs['fuentes'])}),
                                 'op': 'Deuda al entregar (%.1f%% del PIB) menos deuda al recibir (%.1f%%).' % (dd['dFin']['v'], dd['dIni']['v'])}
        else:
            v['deuda_cambio'] = {'na': dd.get('pend', 'Falta la deuda al recibir o al entregar con la misma serie.'), 'et': 'en curso' if curso else 'sin serie comparable'}
        if dd.get('mIni') and dd.get('mFin') and not curso:
            seg = (datetime.date(a1 + 1, 1, 1) - datetime.date(a0, 1, 1)).days * 86400
            ps_ = round((dd['mFin']['v'] - dd['mIni']['v']) * 1e6 / seg, 0)
            v['deuda_seg'] = {'v': ps_, 'est': 'derivado',
                              'f': sorted({usa(dd['mIni']['f'], fs['fuentes']), usa(dd['mFin']['f'], fs['fuentes'])}),
                              'op': 'Saldo de la deuda (SHRFSP) al entregar, $%s mdp, menos al recibir, $%s mdp, entre los %s segundos de sus seis años.'
                                    % (format(dd['mFin']['v'], ',.1f'), format(dd['mIni']['v'], ',.1f'), format(seg, ','))}
        else:
            v['deuda_seg'] = {'na': 'En curso: se calcula al cerrar el sexenio.' if curso else dd.get('pend', 'Falta el saldo en pesos al recibir o al entregar.'), 'et': 'en curso' if curso else 'sin serie comparable'}
        # ASF
        e = ev.get(aid)
        if e:
            a = e['auditorias']
            v['asf_aud'] = ({'v': a['total'], 'est': 'derivado', 'f': [usa(k, base['evaluacion_sexenal']['fuentes']) for k in a['fuentes']],
                             'op': a.get('operacion', ''), 'nota': a.get('nota', '')} if a.get('total') else
                            ({'na': a['motivo']} if a['estado'] == 'no_aplica' else {'pend': a.get('motivo', ''), 'pid': 'sexenal-auditorias' if a['estado'] == 'pendiente' else ''}))
            r = e['recuperaciones']
            v['asf_rec'] = ({'v': r['mdp'], 'est': 'derivado', 'f': [usa(r['fuente'], base['evaluacion_sexenal']['fuentes'])],
                             'op': r.get('operacion', ''), 'nota': r.get('nota', '')} if r.get('mdp') else
                            ({'na': r['motivo']} if r['estado'] == 'no_aplica' else ({'na': r.get('motivo', ''), 'et': 'cifra conjunta'} if r['estado'] == 'conjunta' else {'pend': r.get('motivo', ''), 'pid': 'sexenal-recuperaciones'})))
            p = e['porAclarar']
            v['asf_acl'] = ({'v': p['mdp'], 'est': 'derivado', 'f': [usa(p['fuente'], base['evaluacion_sexenal']['fuentes'])],
                             'op': p.get('operacion', ''), 'nota': p.get('nota', '')} if p.get('mdp') else
                            ({'na': p['motivo']} if p['estado'] == 'no_aplica' else {'pend': p.get('motivo', ''), 'pid': 'sexenal-porAclarar' if p['estado'] == 'pendiente' else ''}))
        else:
            c25 = cp['cp2025']
            nota = 'Solo la %s entrega de la Cuenta Pública 2025 (corte %s): faltan las otras dos.' % (c25['entrega'], c25['corte'])
            f25 = [usa(c25['fuente'], cp['fuentes'])]
            v['asf_aud'] = {'v': c25['auditorias'], 'est': 'oficial', 'f': f25, 'nota': nota}
            v['asf_rec'] = {'v': round(c25['recuperaciones'] / 1e6, 1), 'est': 'oficial', 'f': f25, 'nota': nota}
            v['asf_acl'] = {'v': round(c25['porAclarar'] / 1e6, 1), 'est': 'oficial', 'f': f25, 'nota': nota}
        valores[aid] = v
        pres = RADAR_OBRAS_PRES[aid]
        obras[aid] = [{'n': o['nombre'], 'v': o.get('inversion_real_mdp'),
                       'est': (o.get('estado_campos') or {}).get('inversion_real_mdp', 'pendiente')}
                      for o in base['simulador_megaobras']['obras'] if pres.split()[0] in o.get('presidente', '') and pres.split()[-1] in o.get('presidente', '')]

    metricas = {}
    for serie, (tit, _) in RADAR_SERIES.items():
        metricas[serie + '_pib'] = {'tit': tit + ' (promedio anual)', 'u': 'pib', 'kpi': 'del PIB al año, en promedio'}
        metricas[serie + '_mdp'] = {'tit': tit + ' (suma del sexenio)', 'u': 'mdp', 'kpi': 'en el sexenio', 'kpi2': 'Suma en pesos de cada año', 'mon': True}
    metricas.update({
        'deuda_ini': {'tit': 'Deuda al recibir', 'u': 'pib', 'kpi': 'del PIB al recibir'},
        'deuda_fin': {'tit': 'Deuda al entregar', 'u': 'pib', 'kpi': 'del PIB al entregar', 'kpi2': 'Al entregar'},
        'deuda_cambio': {'tit': 'Cambio en el sexenio', 'u': 'pp', 'kpi': 'puntos del PIB en el sexenio'},
        'deuda_seg': {'tit': 'Lo que creció por segundo', 'u': 'seg', 'kpi': 'de deuda nueva por segundo',
                      'ojo': 'Pesos de cada año: compara el ritmo, no el poder de compra.'},
        'asf_aud': {'tit': 'Auditorías practicadas', 'u': 'ent', 'kpi': 'auditorías de la ASF'},
        'asf_rec': {'tit': 'Recuperaciones operadas', 'u': 'mdp', 'kpi': 'recuperados', 'kpi2': 'Recuperado',
                    'ojo': 'Pesos de cada año. Las cuentas viejas llevan más años de solventación: comparar con esta cifra favorece a los sexenios antiguos.'},
        'asf_acl': {'tit': 'Monto por aclarar', 'u': 'mdp', 'kpi': 'por aclarar ante la ASF',
                    'ojo': 'Pesos de cada año. No es daño comprobado: es lo que, al corte, no tenía documentación que acreditara el gasto. La ASF lo mide así desde la Cuenta Pública 2019.'},
    })
    metricas['costo_financiero_pib']['kpi2'] = 'Intereses de la deuda'
    dims = [
        {'id': 'ingresos', 'ico': '💰', 'tit': 'Ingresos', 'tono': 'verde', 'kpi': 'ingresos_pib',
         'que': RADAR_SERIES['ingresos'][1], 'metricas': ['ingresos_pib', 'ingresos_mdp']},
        {'id': 'inversion', 'ico': '🏗️', 'tit': 'Inversión', 'tono': 'azul', 'kpi': 'inversion_pib',
         'que': RADAR_SERIES['inversion'][1], 'metricas': ['inversion_pib', 'inversion_mdp']},
        {'id': 'costo', 'ico': '🏛️', 'tit': 'Costo del gobierno', 'tono': 'ambar', 'kpi': 'gasto_pib', 'kpi2': 'costo_financiero_pib',
         'que': RADAR_SERIES['gasto'][1] + ' Y, aparte, lo que se fue solo en intereses.',
         'metricas': ['gasto_pib', 'costo_financiero_pib', 'gasto_mdp', 'costo_financiero_mdp']},
        {'id': 'deuda', 'ico': '📉', 'tit': 'Deuda', 'tono': 'rojo', 'kpi': 'deuda_fin', 'kpi2': 'deuda_cambio',
         'que': 'Cuánta deuda pública recibió cada administración y cuánta entregó, medida contra el tamaño de la economía (saldo histórico de los requerimientos financieros del sector público, SHRFSP).',
         'metricas': ['deuda_fin', 'deuda_ini', 'deuda_cambio', 'deuda_seg']},
        {'id': 'asf', 'ico': '⚖️', 'tit': 'Pendiente ante la ASF', 'tono': 'oro', 'kpi': 'asf_acl', 'kpi2': 'asf_rec',
         'que': 'Lo que la Auditoría Superior de la Federación revisó de las Cuentas Públicas de cada sexenio, lo que se recuperó y lo que quedó por aclarar.',
         'metricas': ['asf_acl', 'asf_aud', 'asf_rec']},
    ]
    metricas['deuda_cambio']['kpi2'] = 'Cambio'
    reloj = [
        {'met': 'deuda_seg', 'porSeg': True, 'tit': '📉 Deuda nueva', 'op': 'Lo que creció el saldo de la deuda en el sexenio, entre sus segundos.'},
        {'met': 'costo_financiero_mdp', 'tit': '💸 Intereses de la deuda', 'op': 'Costo financiero del sexenio (su suma) entre los segundos de sus seis años.'},
        {'met': 'inversion_mdp', 'tit': '🏗️ Inversión física', 'op': 'Inversión física del sexenio (su suma) entre los segundos de sus seis años.'},
        {'met': 'ingresos_mdp', 'tit': '💰 Ingresos', 'op': 'Ingresos presupuestarios del sexenio (su suma) entre los segundos de sus seis años.'},
        {'met': 'gasto_mdp', 'tit': '🏛️ Gasto total', 'op': 'Gasto neto del sexenio (su suma) entre los segundos de sus seis años.'},
    ]
    monedas = [{'id': i, 'et': et, 'lee': lee, 'ojo': RADAR_OJO_MON[i]} for (i, et, lee) in RADAR_MONEDAS]
    monedas[1]['lee'] = 'en pesos de %s: ya sin inflación' % ref_mes
    monedas[1]['ojo'] = RADAR_OJO_MON['hoy'].replace('septiembre de 2026', ref_mes)
    peso = _peso_json(ps)
    peso['admins'] = _peso_admins(ps, RADAR_ADMINS)
    datos = json.dumps({'admins': admins, 'valores': valores, 'metricas': metricas, 'dims': dims, 'obras': obras,
                        'fuentes': fuentes, 'reloj': reloj, 'inicial': 'amlo', 'monedas': monedas, 'peso': peso,
                        'corte': fs['consulta'], 'semaforo': RADAR_SEMAFORO, 'ley17': RADAR_LEY17,
                        'duelo': ['ingresos_pib', 'inversion_pib', 'gasto_pib', 'costo_financiero_pib',
                                  'inversion_mdp:hoy', 'costo_financiero_mdp:hoy', 'deuda_fin', 'deuda_cambio', 'asf_aud', 'asf_rec']},
                       ensure_ascii=False).replace('</', '<\\/')

    tablero = '''<script type="application/json" id="rdDatos">{datos}</script>
        <div class="rd-tablero" id="rdTablero">
          <div class="rd-admins" id="rdAdmins" role="tablist" aria-label="Elige una administración"></div>
          <div class="rd-ficha" id="rdFicha" aria-live="polite"></div>
          <div class="rd-dim" id="rdDim"></div>
          <noscript><p>El tablero necesita JavaScript.</p></noscript>
        </div>'''.format(datos=datos)
    peso_html = '''<div class="rd-peso" id="rdPeso">
          <div class="rd-peso-hoy" id="rdPesoHoy"></div>
          <div class="rd-graf" id="rdGraf">
            <div class="rd-mets" role="tablist" aria-label="Qué gráfica ver" id="rdGrafTabs"></div>
            <div class="rd-graf-lienzo" id="rdGrafSvg"></div>
            <p class="rd-graf-lee" id="rdGrafLee" aria-live="polite"></p>
            <div class="rd-graf-pie" id="rdGrafPie"></div>
          </div>
          <h3 class="rd-peso-sub">🧾 El peso en cada sexenio</h3>
          <div class="rd-peso-tabla" id="rdPesoTabla"></div>
          <h3 class="rd-peso-sub">🕰️ La máquina del tiempo del peso</h3>
          <div class="rd-maq" id="rdMaq">
            <div class="rd-maq-ctl">
              <label>Cantidad<span class="rd-maq-monto">$<input type="number" id="rdMaqMonto" min="0" step="any" value="1000" inputmode="decimal"></span></label>
              <label>Pesos del año<select id="rdMaqAnio"></select></label>
              <label>Proyectar hasta<select id="rdMaqHasta"></select></label>
            </div>
            <div id="rdMaqOut" aria-live="polite"></div>
          </div>
        </div>'''
    reloj_html = '''<div class="rd-reloj" id="rdReloj">
          <div class="rd-reloj-ctl">
            <label>Administración<select id="rdRelojAdm"></select></label>
            <label>Qué contar<select id="rdRelojMet"></select></label>
            <label>En qué moneda<select id="rdRelojMon"></select></label>
          </div>
          <div class="rd-reloj-pantalla">
            <small>Al ritmo de esa administración, en <span id="rdRelojSeg">0 s</span>:</small>
            <span id="rdRelojCont" aria-live="off">$0</span>
            <div class="rd-reloj-btns"><button type="button" class="sz-btn sz-btn-of" id="rdRelojPlay" aria-pressed="false">▶ Contabilizar</button>
              <button type="button" class="sz-btn" id="rdRelojCero">↺ A ceros</button></div>
          </div>
          <div id="rdRelojOut"></div>
        </div>'''
    duelo_html = '''<div class="rd-duelo" id="rdDuelo">
          <div class="rd-duelo-ctl"><select id="rdDuelo1" aria-label="Primera administración"></select><span>vs</span>
            <select id="rdDuelo2" aria-label="Segunda administración"></select></div>
          <div id="rdDueloOut"></div>
        </div>'''
    lectura = '<div class="rd-lectura"><ul>%s</ul></div>' % ''.join(
        '<li>%s</li>' % x for x in [base['evaluacion_sexenal']['convencion']] + fs['advertencias'] + [ps['proyeccion']['aviso']] + base['evaluacion_sexenal']['advertencias'])
    datos_js = '<script type="application/json" id="rdDatos">%s</script>\n        ' % datos

    cargos_js = '<script type="application/json" id="exCargos">%s</script>\n        ' % json.dumps(
        radar_cargos(base), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    # La imagen del encabezado del estado de cuenta (pedido del autor,
    # 10-10-2026): si existe assets/auditor/img/encabezado-estado-de-cuenta.*
    # se pinta en todos los documentos; si no, no se pide nada al servidor.
    banda = next(('assets/auditor/img/encabezado-estado-de-cuenta.' + x for x in ('svg', 'png', 'jpg', 'jpeg', 'webp')
                  if os.path.exists(os.path.join(RAIZ, 'assets', 'auditor', 'img', 'encabezado-estado-de-cuenta.' + x))), '')
    expide_html = '''<div class="ex" id="exApp"%s>
          <div class="ex-ctl">
            <p class="ex-paso"><b>1.</b> ¿De quién?</p>
            <div class="ex-tipos" id="exTipos" role="radiogroup" aria-label="Elige de quién es el estado de cuenta"></div>
            <p class="ex-paso" id="exPaso2"><b>2.</b> <span id="exPaso2Tx">Elige la administración</span></p>
            <div class="rd-admins" id="exAdmins" role="radiogroup" aria-label="Elige una administración"></div>
            <div class="ex-ents" id="exEnts" hidden></div>
            <p class="ex-paso"><b id="exPaso3">3.</b> Revisa su estado de cuenta y descárgalo</p>
            <div class="ex-btns"><button type="button" class="sz-btn sz-btn-of" id="exGenera">🧾 Generar estado de cuenta</button>
              <button type="button" class="sz-btn" id="exPdf" disabled>⬇️ Descargar en PDF</button>
              <button type="button" class="sz-btn" id="exLiga">🔗 Copiar el enlace</button></div>
            <p class="ex-pista">Primero genéralo; luego descárgalo. Al descargar, elige «Guardar como PDF» en la ventana de impresión.</p>
          </div>
          <article class="ex-doc" id="exDoc" aria-live="polite"></article>
          <noscript><p>La herramienta necesita JavaScript.</p></noscript>
        </div>''' % ((' data-cabecera="%s"' % banda) if banda else '')
    # «Verifica un estado de cuenta» se mudo al Modo Inspector (pedido del
    # autor, 10-10-2026): es un modulo de esa herramienta con su propia pagina,
    # que carga los mismos datos y el mismo estado-administracion.js.
    verifica_html = '''<div class="ex ex-solo-ver" id="exApp">
          <section class="ex-verifica" id="exVerifica" aria-labelledby="exVerTit">
            <h3 id="exVerTit">🔏 Verifica un estado de cuenta</h3>
            <p>¿Te compartieron uno? Escribe su folio (viene arriba del documento y junto al sello) o su huella digital, y te
              decimos si coincide, cifra por cifra, con los datos vigentes de la plataforma.</p>
            <form class="ex-ver-f" id="exVerForm"><input type="text" id="exVerIn" placeholder="AV-AMLO-1A2B3C4D" autocomplete="off" spellcheck="false" aria-label="Folio o huella digital">
              <button type="submit" class="sz-btn sz-btn-of">Verificar</button></form>
            <div id="exVerOut" aria-live="polite"></div>
          </section>
          <section class="ex-verifica ex-ver-como" aria-labelledby="exComoTit">
            <h3 id="exComoTit">Cómo funciona</h3>
            <ol>
              <li><b>La huella.</b> Cada estado de cuenta firma sus cifras con una huella digital SHA-256: si cambia una sola cifra, cambia la huella.</li>
              <li><b>El folio.</b> Son las iniciales de quién es el documento y los primeros ocho caracteres de su huella, por ejemplo AV-AMLO-1A2B3C4D.</li>
              <li><b>La comprobación.</b> Esta página recalcula, en tu navegador, la huella de los %d estados de cuenta vigentes y busca la tuya.
                Si coincide, el documento no se alteró; si no, o se alteró o se expidió con datos anteriores: expídelo de nuevo en
                <a href="radar-estado-de-cuenta.html">Expide un estado de cuenta</a> y compara.</li>
            </ol>
            <p class="ex-pista">El sello no hace oficial al documento: dice que sus cifras son las que publica Auditavisión, cada una con su fuente.</p>
          </section>
          <noscript><p>La verificación necesita JavaScript.</p></noscript>
        </div>''' % (len(admins) + len(radar_cargos(base)['docs']))

    partes = {
        'tablero': ('Elige una administración y toca cada tarjeta para ver la comparativa con las demás: ingresos, inversión, '
                    'costo del gobierno, deuda y lo pendiente ante la Auditoría Superior, desde 1989. Las sumas en pesos se ven '
                    'en pesos de cada año, en pesos de hoy, en dólares o en euros. Cada cifra trae su documento.', tablero),
        'peso': ('Cuánto vale hoy el peso, cuánto valía en cada sexenio frente al dólar y al euro, y hacia dónde lo proyecta '
                 'Hacienda hasta 2032. Con la máquina del tiempo, lleva cualquier cantidad de un año a otro.', datos_js + peso_html),
        'reloj': ('Elige una administración, qué contar y en qué moneda: el contador corre al ritmo promedio de su sexenio. '
                  'Es una equivalencia, no dinero que se mueva hoy.', datos_js + reloj_html),
        'duelo': ('Dos administraciones, cara a cara, en las mismas medidas. Sin ganador: los números dicen cuánto; el juicio es tuyo.',
                  datos_js + duelo_html),
        'hoy': ('Las cifras grandes del presupuesto de 2026 y el estado de cuenta de quien maneja el dinero público: cada administración '
                'de Salinas a Sheinbaum, con un semáforo de su salud financiera; la diputación federal, la senaduría y la diputación de los 32 congresos locales, '
                'y las ministras y ministros de la Suprema Corte con su ponencia y sus asesores: lo que cobran, lo que gasta su institución '
                'y lo que dijo la Auditoría Superior. Descárgalo en PDF con su folio y su sello de verificación: cualquiera puede '
                'comprobar que no se alteró.', [
                    {'id': 'partes', 'titulo': 'Elige por dónde empezar', 'texto': 'Cada tarjeta abre su propia página.',
                     'tarjetas': [('📌', 'Hoy: el presupuesto en curso', '', 'radar-presupuesto-en-curso.html', '', ''),
                                  ('🧾', 'Expide un estado de cuenta: administraciones, Congreso y la Corte', '',
                                   'radar-estado-de-cuenta.html', '', '')]}]),
        'lectura': ('Antes de comparar sexenios: qué mide cada cifra, de qué serie sale y qué no se puede concluir con ella.', lectura),
    }
    paginas = [{
        'archivo': 'radar-hacendario.html', 'menu': 'Radar hacendario', 'menu_archivo': 'descarga-los-datos.html',
        'padre': ('descarga-los-datos.html', 'Datos'),
        'icono': '📡', 'titulo': 'Radar hacendario', 'lema': 'Cada administración, con sus números',
        'entrada': ('Lo que entró, lo que se invirtió, lo que costó el gobierno, la deuda que recibió y entregó, y lo que quedó '
                    'por aclarar ante la Auditoría Superior: administración por administración, desde 1989. Compáralas en pesos de '
                    'cada año, en pesos de hoy, en dólares o en euros; mira cuánto ha valido el peso y hacia dónde lo proyecta Hacienda, '
                    'y pon a correr el reloj de cada sexenio. Cada cifra trae su documento.'),
        # Las anclas de cuando todo vivia en esta pagina llevan a la suya.
        'hash_a_pagina': dict({r[0]: r[1] for r in RADAR_PARTES}, hoy='radar-hoy.html#hoy',
                              expide='radar-estado-de-cuenta.html'),
        'pestanas': True,
        'pista': 'Cada parte del radar abre su propia página.',
        # Las tarjetas del Radar van sin descripcion, solo icono y titulo
        # (decision del autor, 10-10-2026): lo descriptivo se queda en cada pagina.
        'secciones': [{'id': r[0], 'pagina': r[1], 'pestana': (r[2], r[3], '')} for r in RADAR_PARTES],
    }]
    for (pid, archivo, ico, tit, sub) in RADAR_PARTES:
        entrada, bloque = partes[pid]
        paginas.append({
            # «Hoy y los estados de cuenta» es un indice de dos tarjetas
            # (decision del autor, 10-10-2026): sus anclas viejas van a la pagina de cada una.
            **({'hash_a_pagina': {'hoy': 'radar-presupuesto-en-curso.html', 'expide': 'radar-estado-de-cuenta.html'}}
               if pid == 'hoy' else {}),
            'archivo': archivo, 'menu': tit, 'menu_archivo': 'descarga-los-datos.html',
            'padre': ('descarga-los-datos.html', 'Datos'), 'padre2': ('radar-hacendario.html', 'Radar hacendario'),
            'icono': ico, 'titulo': tit, 'lema': 'Radar hacendario', 'entrada': entrada,
            'estilos': ['radar.css'], 'scripts': ['radar.js'], 'pie_extra': radar_nav(archivo),
            'secciones': bloque if isinstance(bloque, list) else
                         [{'id': pid, 'titulo': tit, 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': bloque}],
        })
    # «Hoy: el presupuesto en curso», en su propia pagina (pedido del autor, 10-10-2026).
    paginas.append({
        'archivo': 'radar-presupuesto-en-curso.html', 'menu': 'Hoy: el presupuesto en curso', 'menu_archivo': 'descarga-los-datos.html',
        'padre': ('descarga-los-datos.html', 'Datos'), 'padre2': ('radar-hacendario.html', 'Radar hacendario'),
        'padre3': ('radar-hoy.html', 'Hoy y los estados de cuenta'),
        'icono': '📌', 'titulo': 'Hoy: el presupuesto en curso', 'lema': 'Radar hacendario', 'entrada': HOY_TEXTO,
        'estilos': ['radar.css'], 'scripts': ['radar.js'], 'pie_extra': radar_nav('radar-hoy.html'),
        'secciones': [{'id': 'hoy', 'titulo': 'Hoy: el presupuesto en curso', 'texto': '', 'sin_cab': True, 'tarjetas': [],
                       'bloque': RADAR_HOY}],
    })
    # «Expide un estado de cuenta», en su propia pagina (pedido del autor, 10-10-2026).
    paginas.append({
        'archivo': 'radar-estado-de-cuenta.html', 'menu': 'Expide un estado de cuenta', 'menu_archivo': 'descarga-los-datos.html',
        'padre': ('descarga-los-datos.html', 'Datos'), 'padre2': ('radar-hacendario.html', 'Radar hacendario'),
        'padre3': ('radar-hoy.html', 'Hoy y los estados de cuenta'),
        'icono': '🧾', 'titulo': 'Expide un estado de cuenta', 'lema': 'Administraciones, Congreso y la Corte',
        'entrada': EXPIDE_TEXTO + ' Cualquiera puede comprobar que no se alteró.',
        'estilos': ['radar.css', 'estado-administracion.css'], 'scripts': ['radar.js', 'estado-administracion.js'],
        'pie_extra': radar_nav('radar-hoy.html'),
        'secciones': [{'id': 'expide', 'titulo': 'Expide un estado de cuenta', 'texto': '', 'sin_cab': True, 'tarjetas': [],
                       'bloque': datos_js + cargos_js + expide_html}],
    })
    h = next(x for x in HERRAMIENTAS if x[1] == 'inspector')
    i = [t[0] for t in h[7]].index('inspverifica')
    ver = herramienta_modulo(h, HERRAMIENTAS.index(h) + 1, i)
    assert ver['archivo'] == VERIFICA_PAGINA
    ver['estilos'] = ['estado-administracion.css']
    ver['scripts'] = ['estado-administracion.js']
    ver['secciones'][0]['bloque'] = datos_js + cargos_js + verifica_html
    paginas.append(ver)
    return paginas


# Glosario general en su propia pagina (decision del autor, 09-10-2026):
# lo pinta assets/auditor/js/glosario.js con los terminos de la base, sin
# cargar la portada en un marco. Los enlaces a un termino llevan a
# glosario.html#<glosario_ancla(termino)>.
GLOSARIO = {
    'archivo': 'glosario.html',
    'menu': 'Glosario',
    'menu_archivo': 'aprende.html',
    'padre': ('aprende.html#diccionario', 'Aprende'),
    'padre2': ('diccionario.html', 'Diccionario del Gasto Público'),
    'padre3': ('biblioteca-hacendaria.html', 'Biblioteca hacendaria'),
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
        'padre': ('aprende.html#diccionario', 'Aprende'),
        'padre2': ('diccionario.html', 'Diccionario del Gasto Público'),
        'padre3': (estante_de(archivo)[5], estante_de(archivo)[2]),
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
          <p class="pase-badge">⚡ Independencia cívica · Abierta a todos; nadie compra lo que publicamos</p>
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
            <li>✓ <b>100 % cívico e independiente:</b> cero publicidad, y ningún cliente, donante, gobierno ni partido decide lo que publicamos.</li>
          </ul>
          <p>¿Necesitas una investigación a la medida de un caso? Eso va aparte del Pase: mira los <a href="servicios.html">Servicios de investigación</a> y su política de independencia.</p>
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
        'Herramientas independientes de fiscalización ciudadana: abiertas a todos, y nadie compra lo que publicamos.',
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
        <a class="nav-action-btn nav-feedback-btn" href="comunidad.html" data-puerta title="Cuéntanos lo que viste: algo raro con el dinero público, un dato mal o un tema para investigar">
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
        <a class="nav-movil-ayuda-btn" href="comunidad.html" data-puerta>📢 Cuéntanos lo que viste</a>
      </div>
    </div>
    </div>
  </nav>
%s''' % ('\n'.join(items), puerta())


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
        if s.get('pagina'):
            continue  # pestana que abre su propia pagina (Agora, 10-10-2026)
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
            ('          <a class="apartado-pestana apartado-pestana-pagina" id="pestana-%s" href="%s">'
             '<span class="apartado-pestana-ico" aria-hidden="true">%s</span>'
             '<span class="apartado-pestana-tx"><b>%s</b><small>%s</small></span></a>' % ((s['id'], s['pagina']) + s['pestana'])).replace('<small></small>', '')
            if s.get('pagina') else
            ('          <a class="apartado-pestana" role="tab" id="pestana-%s" href="#%s" aria-controls="%s" aria-selected="false">'
             '<span class="apartado-pestana-ico" aria-hidden="true">%s</span>'
             '<span class="apartado-pestana-tx"><b>%s</b><small>%s</small></span></a>'
             % ((s['id'], s['id'], s['id']) + s['pestana'])) for s in a['secciones'])
        en_pagina = '''      <nav class="apartado-pestanas" role="tablist" aria-label="Pestañas de esta página"%s>
%s
      </nav>
      <p class="apartado-pestanas-pista" id="pestanasPista">%s</p>''' % (
            ' data-primera="1"' if a.get('primera') else '', botones, a.get('pista', 'Elige una pestaña para abrir su contenido.'))
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
    for nivel in ('padre2', 'padre3'):
        if a.get(nivel):
            padre += '<a href="%s">%s</a> <span aria-hidden="true">›</span> ' % a[nivel]
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
{sociales}
  <meta name="theme-color" content="#0b2a63">
  <meta name="color-scheme" content="light">
  <link rel="icon" href="{favicon}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/auditor/css/auditavision.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/civico.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/apartados.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/puerta.css?v={sello}">{estilos}{redirige}
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

  <script src="assets/auditor/js/apartados.js?v={sello}"></script>
  <script src="assets/auditor/js/comunidad.js?v={sello}"></script>{scripts}
</body>
</html>
'''.format(titulo_doc=titulo_doc, descripcion=esc_attr(descripcion), favicon=FAVICON, sello=sello,
           sociales=sociales(a['archivo'], titulo_doc, descripcion),
           cabecera=cabecera(a.get('menu_archivo', a['archivo']), sello), menu=a['menu'],
           padre=padre, cab_clase=cab_clase, cab_estilo=cab_estilo, pie_extra=pie_extra, redirige=redirige, icono='' if a.get('sin_icono_lema') else a['icono'] + ' ', lema=a['lema'],
           titulo=a['titulo'], entrada=a['entrada'], nota=nota, en_pagina=en_pagina, guia=guia, guia_abajo=guia_abajo, scripts=scripts, estilos=estilos, antes=(a['antes'] + '\n\n') if a.get('antes') else '',
           secciones='\n\n'.join(secciones))


# Indice general (entrega 2 de la propuesta de Astra, 10-10-2026): todo lo
# que tiene la plataforma en una sola pagina, por pestana y por tema, con la
# metodologia y las novedades. Se arma solo con las listas de este archivo y
# de auditorias.py: al agregar una pagina ahi, aparece aqui.
NOVEDADES = [
    ('10-10-2026', 'Las tarjetas del Radar hacendario quedan limpias: solo el icono y el nombre de cada parte. Lo descriptivo se queda dentro de cada página.'),
    ('10-10-2026', '«Hoy: el presupuesto en curso» tiene contador: las cifras arrancan en cero y el botón «Contar» las lleva a su valor oficial; el mismo botón las regresa a cero. «Durante tu visita» se desbloquea al contar.'),
    ('10-10-2026', 'Los estados de cuenta de la diputación federal y local, el Senado y la Suprema Corte suman la institución como órgano: cuánto nos cuesta al año, al día y a cada habitante, cuánto se va en sueldos y prestaciones, y del dinero que ejerció a lo que revisó la Auditoría Superior y lo que falta aclarar.'),
    ('10-10-2026', '«Verifica un estado de cuenta» se mudó al Modo Inspector: es su módulo 7, con página propia. Escribe el folio o la huella y comprueba que el documento no se alteró; los enlaces de los PDF ya impresos llegan ahí solos.'),
    ('10-10-2026', 'El estado de cuenta se lee como una hoja por los dos lados: al frente, el termostato de la salud financiera y las cuentas, con los negativos en rojo; atrás, la justificación por secciones (qué mide cada cifra, su operación, su fundamento y su fuente) y el sello.'),
    ('10-10-2026', 'En el Radar, «Hoy y los estados de cuenta» se abre en dos páginas: «Hoy: el presupuesto en curso» y «Expide un estado de cuenta». Cada tarjeta lleva a la suya.'),
    ('10-10-2026', 'Expide un estado de cuenta abre en su propia página: eliges de quién, presionas «Generar estado de cuenta» y luego lo descargas en PDF. El encabezado del documento es más amplio y el logo, más nítido.'),
    ('10-10-2026', 'El estado de cuenta suma a las senadoras y los senadores: su dieta, su remuneración anual bruta y neta, sus asesores, el presupuesto del Senado y su auditoría de la ASF, con el mismo folio y sello.'),
    ('10-10-2026', 'El estado de cuenta ya no es solo de las administraciones: expide también el de la diputación federal, el de cada uno de los 32 congresos locales y el de la Suprema Corte con su ponencia y sus asesores. Lo que cobran, lo que gasta su institución y lo que dijo la Auditoría Superior, con dos señales con regla de ley (el tope del art. 127 y la obligación de publicar lo que pagan), en PDF con folio y sello.'),
    ('10-10-2026', 'En el Radar, «Hoy: el presupuesto en curso» y «Expide el estado de cuenta» son ya una sola tarjeta: las cifras de 2026 y el estado de cuenta de cada administración, en la misma página.'),
    ('10-10-2026', 'Expide el estado de cuenta de cada administración, de Salinas a Sheinbaum: sus números en resumen, un semáforo de su salud financiera con reglas escritas y descarga en PDF con folio y sello de verificación.'),
    ('10-10-2026', 'El Radar hacendario se abre en seis páginas: el tablero, el peso en el tiempo, el reloj de cada administración, el duelo, el presupuesto en curso y cómo leer los números. Cada una con su propia dirección para compartirla.'),
    ('10-10-2026', 'El peso en el tiempo, en el Radar hacendario: las sumas de cada sexenio en pesos de hoy, dólares o euros; inflación y tipo de cambio desde 1988 con la proyección de Hacienda a 2032, el dólar y el euro de hoy, y la máquina del tiempo del peso. Las series vienen ahora de una sola fuente de Hacienda, de 1990 a 2025.'),
    ('10-10-2026', 'Radar hacendario, en su propia página: cada administración desde 1989 con sus ingresos, inversión, costo, deuda y lo pendiente ante la ASF, más el reloj de cada sexenio y el duelo entre dos.'),
    ('10-10-2026', 'Garantías cívicas, en su propia página: una brújula que en tres clics te dice a qué puerta oficial tocar, las seis puertas, tus diez garantías y el reto «¿Mito o realidad?».'),
    ('10-10-2026', 'Ágora cívica, en su propia página: la red de réplica y diálogo, con perfil, muro, réplicas, apoyos, insignias y preguntas para empezar.'),
    ('10-10-2026', 'Una sola puerta, «📢 Cuéntanos lo que viste»: en cualquier página abre tres rutas (algo raro con el dinero público, un dato mal, un tema para investigar).'),
    ('10-10-2026', 'Comunidad, en Participa: propón un tema, señala un error con su documento, comparte el Estado de Cuenta y consulta la fe de erratas.'),
    ('10-10-2026', 'Servicios de investigación, en Participa: cinco servicios (incluida la licencia de las herramientas), cómo trabajamos, política de independencia y el formulario «Solicita una investigación». Se abren con el lanzamiento.'),
    ('10-10-2026', 'Simulador «Reparte el presupuesto», desde $0: con ejemplo oficial de 2026 y 2027, comparación de escenarios y descarga. La Calculadora Cívica también arranca en cero.'),
    ('10-10-2026', 'Aprende reúne la Biblioteca hacendaria y las Fuentes del auditor en una sola tarjeta, el Diccionario del Gasto Público; cada estante abre su propia página.'),
    ('10-10-2026', 'Registro de pendientes: cada dato que falta, con su porqué, su responsable y el enlace oficial donde debería estar. Toda etiqueta «pendiente» lleva ahí.'),
    ('10-10-2026', 'Estado de Cuenta Cívico: 2024, 2026 y 2027 comparados en % del PIB, en cuatro dimensiones y con descarga en CSV.'),
    ('10-10-2026', 'Se retiraron las cifras del «Estado de Resultados» 2024 y la ficha pericial del Tren Maya que no tenían cotejo con su documento.'),
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
    numeros = _rejilla([_grupo('🧾', 'El balance', [
        ('estado-de-cuenta.html', 'Estado de Cuenta Cívico', '2024, 2026 y 2027 en cuatro dimensiones'),
        ('estado-de-cuenta-2024-2027.csv', 'Descarga el estado de cuenta en CSV', 'Con periodo, fuente y estado de cada renglón')])] +
                       [_grupo(s['pestana'][0], s['titulo'],
                               [(_a_numeros(t[3]), re.sub('<[^>]+>', '', t[1]), '') for t in s['tarjetas']],
                               'sigue-el-dinero.html#' + s['id'])
                        for s in num['secciones']])
    herr = _rejilla([_grupo(h[2], h[3], [(modulo_archivo(h[0], t[0]), t[2], t[3]) for t in h[7]], h[0])
                     for h in HERRAMIENTAS])
    otros = []
    for archivo in ('descarga-los-datos.html', 'aprende.html', 'participa.html'):
        a = ap[archivo]
        enl = [(x.get('pagina') or archivo + '#' + x['id'], x['pestana'][1], x['pestana'][2]) for x in a['secciones']]
        if archivo == 'descarga-los-datos.html':
            enl[1:1] = [(r[1], 'Radar · ' + r[3], r[4]) for r in RADAR_PARTES]
        if archivo == 'aprende.html':
            enl += [('diccionario.html', 'Diccionario del Gasto Público', 'La obra completa')] + [
                (e[5], e[2], e[3]) for e in ESTANTES] + [(b[0], b[2], '') for b in BIBLIOTECA]
        if archivo == 'participa.html':
            enl += [('expedientes.html', 'Expedientes de casos', 'Casos por aclarar'),
                    ('comunidad.html', 'Comunidad', 'Propón temas, señala errores, comparte y fe de erratas'),
                    ('servicios.html', 'Servicios de investigación', 'Solicita una investigación y política de independencia')]
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
        '          <p><a href="pendientes.html"><b>⏳ Registro de pendientes</b></a>: cada dato que falta, por qué falta, quién debe publicarlo y el enlace oficial donde debería estar.</p>\n'
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
            if t[0].endswith('.html') or t[0] in MODULOS_PROPIOS:
                continue
            m = herramienta_modulo(h, n, i)
            texto = pagina(m, sello).replace('\r\n', '\n').replace('\n', '\r\n')
            open(os.path.join(RAIZ, m['archivo']), 'wb').write(texto.encode('utf-8'))
    for extra in [DICCIONARIO, GLOSARIO, indice(), simulador(), servicios(), comunidad(), agora(), garantias()] + radar() + PAGINAS_ESTANTE + PAGINAS_BIBLIOTECA:
        texto = pagina(extra, sello).replace('\r\n', '\n').replace('\n', '\r\n')
        open(os.path.join(RAIZ, extra['archivo']), 'wb').write(texto.encode('utf-8'))
    for archivo, datos in REDIRECCIONES.items():
        texto = redireccion(*datos).replace('\n', '\r\n')
        open(os.path.join(RAIZ, archivo), 'wb').write(texto.encode('utf-8'))
    print('apartados: %d páginas y %d herramientas generadas con el sello %s' % (len(APARTADOS), len(HERRAMIENTAS), sello))
    if poner_puerta():
        return 1
    # Las paginas de Auditoria en imagenes comparten cabecera y sello.
    import auditorias
    import expedientes
    import estado_cuenta
    import pendientes
    if auditorias.generar(sello) or estado_cuenta.generar(sello) or pendientes.generar(sello):
        return 1
    import sitemap
    return expedientes.generar(sello) or sitemap.generar(sello)


if __name__ == '__main__':
    sys.exit(generar())
