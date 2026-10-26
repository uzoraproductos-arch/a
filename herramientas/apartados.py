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
import importlib
import re
import unicodedata
import sys

import mo_capitulos

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect x='2' y='2' width='60' height='60' rx='12' fill='%23ffffff' stroke='%231d5fd6' stroke-width='4'/%3E%3Cg fill='%23ffffff' stroke='%234f6286' stroke-width='2.2' stroke-linejoin='round'%3E%3Cpath d='M20 37 C14 28 9 23 3 22 C6 30 9 34 13 37 C9 36 6 37 4 39 C9 41 14 41 19 41 Z'/%3E%3Cpath d='M44 37 C50 28 55 23 61 22 C58 30 55 34 51 37 C55 36 58 37 60 39 C55 41 50 41 45 41 Z'/%3E%3C/g%3E%3Ccircle cx='32' cy='39' r='15' fill='%23d9a21a' stroke='%237a5206' stroke-width='2'/%3E%3Ccircle cx='32' cy='39' r='11' fill='%23f7cf45' stroke='%23a8740c' stroke-width='1.2'/%3E%3Cpath d='M27 44 Q32 47 37 44' fill='none' stroke='%235a3a02' stroke-width='1.8' stroke-linecap='round'/%3E%3Ccircle cx='28' cy='38' r='1.9' fill='%2310202e'/%3E%3Ccircle cx='36' cy='38' r='1.9' fill='%2310202e'/%3E%3Cg transform='rotate(-8 32 22)'%3E%3Cellipse cx='32' cy='24.5' rx='14' ry='3' fill='%231b2433'/%3E%3Cpath d='M23 24.5 C23 14 25 11 32 11 C39 11 41 14 41 24.5 Z' fill='%231b2433'/%3E%3Crect x='23.2' y='19.5' width='17.6' height='3.4' fill='%23d4a826'/%3E%3C/g%3E%3C/svg%3E")




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


def libro_pie(a):
    """Notas al pie de la pagina: la obra que ordena el apartado y sus
    conceptos en el glosario y el diccionario."""
    rid, num, cita = a['libro_ref']
    url = 'fuentes-oficiales.html#%s' % rid
    glos_ = ' · '.join('<a href="glosario.html#%s">%s</a>' % (glosario_ancla(t), t.split(' (')[0])
                       for t in a.get('libro_glosario', []))
    return ('<aside class="apartado-notas" aria-labelledby="notasTit">'
            '<h2 class="apartado-notas-tit" id="notasTit">Notas y referencias</h2>'
            '<ol class="apartado-notas-lista">'
            '<li id="nota-%d" value="%d"><span class="apartado-libro-num">[%d]</span> %s <a href="%s">Ficha en las Referencias ➔</a>'
            '<br><span class="apartado-notas-por">%s</span></li></ol>'
            '<p class="apartado-notas-glos"><b>Los conceptos de este apartado:</b> %s. '
            'Búscalos también en el <a href="glosario.html">Diccionario</a> de la Biblioteca del Erario Público.</p>'
            '</aside>' % (num, num, num, cita, url, a['libro'], glos_))


# Datos abiertos e Informes oficiales, en sus paginas (pedido del autor,
# 11-10-2026), como Comunidad y Garantias: cada pestana de Datos abre su
# portada y cada ficha, su pagina. El contenido lo sigue armando datos.js
# (FICHAS), que ahora llena el <div data-ficha-fija> de cada pagina. Las
# anclas viejas (descarga-los-datos.html#abiertos, #ficha-asf...) redirigen.
# (id, portada, icono, nombre, frase de la pestana, entrada,
#  [(ficha, archivo, icono, nombre, frase de la tarjeta, entrada)])
DATOS_PARTES = [
    ('abiertos', 'datos-abiertos.html', '💾', 'Datos abiertos', 'Bases en CSV para Excel',
     'Las bases de la plataforma, listas para que hagas tus propias cuentas. Cada una se descarga en CSV, abre directo en Excel '
     'y lleva su fuente oficial al final del archivo. Cada tarjeta abre su propia página.',
     [('descargas', 'datos-descargas.html', '📥', 'Descarga en CSV (abre en Excel)',
       'Siete bases con fuente oficial: municipios, sueldos netos, gasto de los Poderes, presupuesto ambiental, auditorías de la ASF por estado, lista 69-B y documentos.',
       'Siete bases con fuente oficial, cada una con su botón de descarga y su diccionario de columnas.'),
      ('municipios', 'datos-municipios.html', '🏘️', 'Base de Datos Municipal EFIPEM (INEGI)',
       'Los 2,479 municipios con sus ingresos, predial, participaciones y fondos del Ramo 33, en CSV.',
       'Los municipios del país con sus ingresos, predial, participaciones y aportaciones, según las Estadísticas de Finanzas '
       'Públicas Estatales y Municipales del INEGI. Descárgala completa o consulta un estado aquí mismo.')]),
    ('informes', 'informes-oficiales.html', '📑', 'Informes oficiales', 'Cuenta Pública y diccionario',
     'Lo que revisó la Auditoría Superior de la Federación en la Cuenta Pública y qué contiene cada archivo de datos de la '
     'plataforma. Cada tarjeta abre su propia página.',
     [('asf', 'informes-cuenta-publica.html', '🔎', 'Informes de la Cuenta Pública (ASF)',
       'Qué revisó la Auditoría Superior en 2024, cuánto quedó por aclarar en tu estado y cuándo sale la siguiente entrega.',
       'Qué revisó la Auditoría Superior de la Federación en la Cuenta Pública 2024, cuánto quedó por aclarar en tu estado '
       'y cuándo sale la siguiente entrega. Cada cifra, con su informe.'),
      ('diccionario', 'informes-diccionario.html', '📋', 'Diccionario de Datos',
       'Qué contiene cada archivo de datos de la plataforma, campo por campo.',
       'Qué contiene cada archivo de datos de la plataforma, columna por columna. Cada base se descarga con el botón de su renglón.')]),
]
# Anclas viejas de descarga-los-datos.html: la pestana y cada #ficha-<id>.
DATOS_ANCLAS = dict([(d[0], d[1]) for d in DATOS_PARTES] +
                    [('ficha-' + f[0], f[1]) for d in DATOS_PARTES for f in d[6]])


def datos_paginas():
    """Portadas de Datos abiertos e Informes oficiales y una pagina por ficha."""
    paginas = []
    for id_, portada, ico, nombre, frase, entrada, fichas_ in DATOS_PARTES:
        partes = [(f[0], f[1], f[2], f[3]) for f in fichas_]
        paginas.append({
            'archivo': portada, 'menu': nombre, 'menu_archivo': 'descarga-los-datos.html',
            'padre': ('descarga-los-datos.html', 'Datos'),
            'icono': ico, 'titulo': nombre, 'lema': frase, 'entrada': entrada,
            'hash_a_pagina': dict((f[0], f[1]) for f in fichas_),
            'secciones': [{'id': 'partes', 'titulo': nombre, 'texto': '', 'sin_cab': True,
                           'tarjetas': [(f[2], f[3], f[4], f[1], None, None) for f in fichas_]}],
        })
        for fid, archivo, fico, fnombre, ffrase, fentrada in fichas_:
            paginas.append({
                'archivo': archivo, 'menu': fnombre, 'menu_archivo': 'descarga-los-datos.html',
                'padre': ('descarga-los-datos.html', 'Datos'), 'padre2': (portada, nombre),
                'icono': fico, 'titulo': fnombre, 'lema': nombre, 'entrada': fentrada,
                'scripts': ['audit-database.js', 'municipios-efipem.js', 'datos.js'],
                'pie_extra': partes_nav(nombre, portada, ico, partes, archivo),
                'secciones': [{'id': fid, 'titulo': fnombre, 'texto': '', 'sin_cab': True, 'tarjetas': [],
                               'bloque': ('<div class="dt-cuerpo dt-fija" data-ficha-fija="%s">\n'
                                          '          <noscript><p>Esta página necesita JavaScript.</p></noscript>\n'
                                          '        </div>' % fid)}],
            })
    return paginas


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
         'herramienta-inspector-asf.html', 'Expedientes de casos de la ASF'),
        (5, '🧭', 'Se hace el balance',
         'El %s junta lo que entró, lo que se gastó, lo que se debe y lo que se perdió: 2024 frente a 2026 y 2027.' % (
             '<a href="estado-de-cuenta.html">Contexto dimensional</a>'),
         'estado-de-cuenta.html', 'Ver el contexto dimensional'),
    ])


# Biblioteca del Erario Publico (decision del autor, 11-10-2026). Antes
# «Diccionario del Erario Publico», en dos estantes (Biblioteca hacendaria y
# Fuentes del auditor) con sus paginas intermedias. Ahora es una sola pagina
# (diccionario.html, el archivo no cambia para no romper enlaces) con cuatro
# tarjetas y cada una abre su pagina:
#   Aprende › Biblioteca del Erario Publico › Apartado.
# Las paginas de los estantes redirigen aqui (REDIRECCIONES). Cada entrada:
# (archivo, icono, nombre, frase, descripcion).
BIB_NOMBRE = 'Biblioteca del Erario Público'
BIBLIOTECA = [
    ('glosario.html', '📖', 'Diccionario', 'Glosario de términos hacendarios',
     'Los términos del presupuesto, la deuda y la fiscalización, en lenguaje llano, con su fundamento y con buscador.'),
    ('fuentes-oficiales.html', '📑', 'Referencias', 'Compendio de fuentes oficiales',
     'El catálogo de referencias: las leyes, decretos, acuerdos, informes y bases de datos que sostienen las cifras de la plataforma, numerados y con su liga directa al DOF, Hacienda, la Auditoría Superior, el INE, Banxico, el INEGI y Transparencia Presupuestaria. Cada nota [n] de la plataforma lleva a su ficha.'),
    ('marco-legal.html', '⚖️', 'Marco Legal Hacendario', 'El texto vigente',
     'El ciclo del dinero público artículo por artículo: Constitución, Ley de Ingresos 2026, LFPRH, Coordinación Fiscal, Disciplina Financiera y Poder Judicial, con el texto vigente cotejado.'),
    ('preguntas-frecuentes.html', '💡', 'Preguntas Frecuentes', 'En casillas didácticas',
     'Cómo funciona el gasto público, la deuda, el dinero de estados y municipios, qué revisa la Auditoría Superior y cuánto cuesta el Poder Judicial. Cada respuesta con sus fuentes.'),
]
DIC_ENLACE = ('<p class="bib-sello">📚 Forma parte de la <a href="diccionario.html">%s</a>, '
              'la obra de consulta de la plataforma.</p>' % BIB_NOMBRE)


def tarjetas_biblioteca():
    return [(b[1], b[2], '<b>%s.</b> %s' % (b[3], b[4]), b[0], None, None) for b in BIBLIOTECA]


def bib_nav(actual):
    """Barra al pie de cada pagina de la Biblioteca, con sus cuatro apartados."""
    return ('<nav class="bib-nav" aria-label="%s">\n'
            '        <a class="bib-nav-tit" href="diccionario.html">📚 %s</a>\n'
            '        <div class="bib-nav-fila">\n%s\n        </div>\n      </nav>' % (BIB_NOMBRE, BIB_NOMBRE, '\n'.join(
                '          <a class="bib-nav-a" href="%s"%s><span aria-hidden="true">%s</span><span>%s<small>%s</small></span></a>'
                % (b[0], ' aria-current="page"' if b[0] == actual else '', b[1], b[2], b[3]) for b in BIBLIOTECA)))


ENCICLOPEDIA = 'enciclopedia-auditavision.html'

# Las pestañas del menú (decisión del autor, 23-10-2026): eran cinco y son
# tres. Cada una: (archivo, nombre, páginas que la marcan como actual).
# La pestaña «Auditor Virtual» abre primero «Pregúntale al Auditor» (pedido del
# autor, 23-10-2026); las cuatro herramientas cuelgan del botón «Herramientas»
# de su cabecera, y herramientas.html sigue como su índice.
AUDITOR_VIRTUAL = 'herramienta-inspector-pregunta.html'
MENU = [
    (AUDITOR_VIRTUAL, 'Auditor Virtual', ('herramientas.html',)),
    (ENCICLOPEDIA, 'Enciclopedia', (ENCICLOPEDIA, 'sigue-el-dinero.html', 'descarga-los-datos.html', 'aprende.html')),
    ('participa.html', 'Comunidad', ('participa.html',)),
]

APARTADOS = [
    {
        'archivo': 'herramientas.html',
        # Desde el 23-10-2026 la pestaña se llama «Auditor Virtual» (decisión
        # del autor); el archivo conserva su nombre para no romper enlaces.
        'menu': 'Herramientas',
        'padre': (AUDITOR_VIRTUAL, 'Auditor Virtual'),
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
                    ('🏗️', 'Inversión y Megaobras', '', 'herramienta-megaobras.html', None, 'obras'),
                    ('💳', 'Calculadora Cívica', '', 'herramienta-calculadora.html', None, 'calculadora'),
                    ('🔍', 'Modo Inspector', '', 'herramienta-inspector.html', None, 'inspector'),
                    ('🌎', 'Costo Ambiental', '', 'herramienta-ambiente.html', None, 'ambiente'),
                ],
            },
        ],
    },
    {
        # La Enciclopedia (decisión del autor, 23-10-2026): la segunda de las
        # tres pestañas junta Números, Datos y Aprende. No es la plataforma antigua
        # (enciclopedia.html, retirada el 24-10-2026): aquí solo hay tres tarjetas.
        'archivo': ENCICLOPEDIA,
        'menu': 'Enciclopedia',
        'icono': '📚',
        'titulo': 'Enciclopedia',
        'lema': 'La obra de consulta del auditor',
        'entrada': ('Aquí está la parte de consulta de la plataforma: los números del dinero público, los datos para descargar '
                    'y lo que hace falta para leerlos. Cada tarjeta abre su propia página, y toda cifra lleva su fuente oficial.'),
        'pestanas': True,
        'pista': 'Cada tarjeta abre su propia página.',
        'secciones': [
            {'id': 'numeros', 'pagina': 'sigue-el-dinero.html',
             'pestana': ('💰', 'Números', 'El recorrido del dinero, del impuesto a la rendición de cuentas: abre su página')},
            {'id': 'datos', 'pagina': 'descarga-los-datos.html',
             'pestana': ('💾', 'Datos', 'El radar, las descargas, el ambiente y los Poderes: abre su página')},
            {'id': 'aprende', 'pagina': 'aprende.html',
             'pestana': ('📖', 'Aprende', 'La trivia, la Biblioteca del Erario Público y las noticias: abre su página')},
        ],
    },
    {
        'archivo': 'sigue-el-dinero.html',
        # Desde el 09-10-2026 el menu se llama «Números» (decision del autor);
        # el archivo conserva su nombre para no romper enlaces.
        # Reestructura del 10-10-2026 (pedido del autor): un solo recorrido
        # de seis pasos, que son a la vez el camino y las pestanas; arriba,
        # «El peso de 2026» (de donde viene y a donde va, numeros.js), y en
        # el paso 3 los tres presupuestos: del Estado, nacional y social.
        # La nota del libro ya no es un apartado: es una nota al pie.
        # Desde el 11-10-2026 (pedido del autor) la portada son siete
        # tarjetas, como el Radar hacendario, y cada una abre su pagina:
        # las arma numeros_preparar() con estas secciones (NUMEROS_PARTES).
        'menu': 'Números',
        'icono': '💰',
        'titulo': 'Números',
        'lema': 'Del impuesto a la rendición de cuentas',
        'entrada': ('El dinero público tiene un recorrido: se recauda, se aprueba, se gasta, baja a estados y municipios, '
                    'paga lo que se debe y, al final, alguien revisa que se haya usado bien. Empieza por el presupuesto '
                    'completo y después síguelo: cada tarjeta abre su propia página.'),
        'libro': ('Este apartado sigue el orden de <cite>Introducción al Derecho Económico</cite>, de Moisés Gómez Granillo y '
                  'Rosa María Gutiérrez Rosas (Editorial Esfinge, 1995), sobre todo sus capítulos 5 y 7. Cada paso trae una '
                  'franja <b>«Ayer y hoy»</b>: lo que explicaba el libro y cómo está hoy, con el documento oficial que lo sostiene. '
                  'Las cifras no se copian del libro: se toman de su fuente oficial vigente.'),
        # Nota de referencia (decision del autor, 09-10-2026): la obra es la
        # ficha ref-gomez-granillo-1995 del catalogo de fuentes y sus
        # conceptos llevan al glosario del auditor. Desde el 10-10-2026 va
        # al pie de la pagina (libro_pie), no como enlace bajo la entrada.
        'libro_ref': ('ref-gomez-granillo-1995', 119,
                      'Gómez Granillo, M., y Gutiérrez Rosas, R. M. (1995). <cite>Introducción al derecho económico</cite>. Editorial Esfinge.'),
        'libro_glosario': ['Rectoría Económica del Estado', 'Economía Mixta', 'Sistema Nacional de Planeación Democrática',
                           'Hacienda Pública', 'LIF (Ley de Ingresos de la Federación)', 'PEF (Presupuesto de Egresos de la Federación)',
                           'Gasto Programable vs No Programable', 'Gasto Federalizado', 'Deuda Pública y SHRFSP', 'Cuenta Pública'],
        # El bloque del paso 3 lo arma numeros_preparar() con window.AUDIT_DB
        # al generar, y tambien 'hash_a_pagina' y 'abrir_a_pagina'.
        'pestanas': True,
        'pista': 'Cada parte de Números abre su propia página. Van en el orden en que se mueve el dinero.',
        'secciones': [
            {
                'id': 'origen',
                'pestana': ('💵', '1 · Presupuesto', 'Cuánto es y de dónde sale'),
                'num': 1,
                'titulo': 'Presupuesto: cuánto dinero es y de dónde sale',
                'texto': ('Todo el dinero federal de 2026, en seis tarjetas: los tres presupuestos (del Estado, nacional y social); '
                          'cuánto es, de dónde viene y a dónde va; los 16 orígenes que autoriza la Ley de Ingresos; a qué equivale; '
                          'el camino que recorre, y lo que propone el Paquete Económico 2027. Cada tarjeta abre su propia página.'),
                # Sin franja «Ayer y hoy» ni nota del libro desde el
                # 11-10-2026 (pedido del autor): viven en el Diccionario,
                # en la pregunta frecuente de la accion financiera del
                # Estado y en la ficha [119] del compendio de fuentes.
                # Desde el 11-10-2026 (pedidos del autor) la pagina es solo
                # tarjetas, en mosaico, y cada una abre su pagina de modulo
                # (NUMEROS_MODULOS). «El peso de 2026» se fundio el mismo dia
                # en «Cuanto dinero es»: repetian el total y el reparto.
                # (icono, nombre, descripcion de la pagina, archivo, fuente,
                # rubro, descripcion breve de la tarjeta)
                'mosaico': 'np-mosaico',
                'bloque': '',
                # «Los tres presupuestos» paso de «Gasto publico» a ser la
                # primera de aqui (pedido del autor, 24-10-2026): seis tarjetas.
                'tarjetas': [
                    ('🧭', 'Los tres presupuestos', 'El gasto de 2026 leído en tres renglones, del Estado, nacional y social, más lo que ya está comprometido antes de empezar, con la operación a la vista.',
                     'numeros-gasto-tres-presupuestos.html', None, 'dinero',
                     'Del Estado, nacional y social: hacia dónde va'),
                    ('💰', 'Cuánto dinero es', 'Los $10.19 billones de 2026 de un vistazo: de dónde viene y a dónde va cada peso, en dos barras que se pueden tocar, y lo que baja al territorio.',
                     'numeros-cuanto-dinero-es.html', 'Ley de Ingresos y Presupuesto de Egresos de la Federación 2026', 'dinero',
                     'El total de 2026: de dónde viene y a dónde va'),
                    ('🧾', 'Los 16 orígenes del ingreso', 'Impuestos, cuotas, ventas de las empresas del Estado y deuda, tal como los enumera el artículo 1o. de la Ley de Ingresos 2026. Cada renglón abre su página.',
                     'numeros-los-16-origenes.html', 'Ley de Ingresos de la Federación 2026, art. 1o.', 'dinero',
                     'Renglón por renglón, cada uno con su página'),
                    ('📏', '¿A qué equivale?', 'Tres comparaciones para dimensionar las cifras, con la operación a la vista.', 'numeros-a-que-equivale.html', None, 'dinero',
                     'Tres comparaciones, con la operación a la vista'),
                    ('🏛️', 'El camino del dinero', 'Se recauda, se aprueba, se ejerce y se revisa: quién responde en cada etapa, en qué plazo y con qué ley.', 'numeros-camino-del-dinero.html', None, 'dinero',
                     'Cuatro etapas: quién responde y con qué ley'),
                    ('📈', 'Paquete Económico 2027', 'La proyección de ingresos y gasto para 2027, sus supuestos, un simulador con los coeficientes oficiales y sus puntos ciegos.', 'numeros-paquete-2027.html', None, 'dinero',
                     'Lo que viene, con su simulador y puntos ciegos'),
                ],
            },
            {
                # «Se aprueba» y «Se gasta: los tres presupuestos» se fundieron
                # en «Gasto público» (pedido del autor, 11-10-2026): primero
                # quien lo aprueba, luego en que se va.
                'id': 'gasta',
                'pestana': ('🏛️', '2 · Gasto público', 'Quién lo aprueba y en qué se va'),
                'num': 2,
                'titulo': 'Gasto público: quién lo aprueba y en qué se va',
                'texto': ('La Cámara de Diputados aprueba cada año el Presupuesto de Egresos y, con él, en qué se va cada peso. '
                          'Aquí está quién tiene la facultad de aprobarlo, parada por parada, y cómo se reparte el dinero que sostiene '
                          'al país: un simulador contable que lo parte del total a sus ocho renglones y, al final, cada desglose '
                          'en su propia página.'),
                # Su «Ayer y hoy» vive en las Preguntas frecuentes (12-10-2026).
                'bloque': '',
                # Las vistas del motor abren su pagina de modulo
                # (NUMEROS_MODULOS). Megaobras y costo ambiental se quitaron
                # (11-10-2026): son herramientas y ya viven en Herramientas;
                # el pie de la pagina (gasto_pie) lleva alla.
                'tarjetas': [
                    ('🎛️', 'Reparte tú el presupuesto', 'Ponte en el lugar de la Cámara: arranca en $0, reparte los $10.19 billones y compáralo con lo aprobado.', 'simulador-presupuesto.html', None, 'calculadora'),
                    ('⚖️', 'Lo que cuestan el Congreso y la Judicatura', 'Presupuesto 2026, gasto auditado 2024 y sueldos netos oficiales.', 'numeros-lo-que-cuestan-los-poderes.html', None, 'dinero'),
                    ('🏢', 'En qué se va: ramos y dependencias', 'Cuánto recibe cada Secretaría: de los ocho renglones del gasto a los 46 ramos y entidades del decreto, en pesos.', 'numeros-ramos-y-dependencias.html', None, 'dinero'),
                    ('🌡️', '¿Cuánto margen tiene el presupuesto?', 'Lo que ya está comprometido antes de empezar: deuda, participaciones y gastos obligatorios, en un termostato.', 'numeros-margen-del-presupuesto.html', None, 'dinero'),
                    ('🔦', 'Lo que la cifra grande no dice', 'Cinco lecturas que no aparecen en el anuncio presupuestal y que cambian el sentido del total.', 'numeros-lo-que-la-cifra-no-dice.html', None, 'inspector'),
                ],
            },
            {
                'id': 'baja',
                'pestana': ('📍', '3 · Baja al territorio', 'Estados y municipios'),
                'num': 3,
                'titulo': 'Baja al territorio: estados y municipios',
                'texto': ('El dinero federal llega a los 32 estados y a los 2,479 municipios, y ahí se suma a lo que cada uno '
                          'recauda. En tres tarjetas: el mapa de lo que recibe cada estado, el circuito de cada uno y el padrón '
                          'de sus municipios. Cada tarjeta abre su propia página.'),
                # Desde el 11-10-2026 (pedido del autor) la pagina es solo
                # tarjetas, como «Presupuesto», y cada una abre su pagina de
                # modulo (territorio_modulos.py): antes desplegaban el auditor
                # debajo. La franja «Ayer y hoy» y la nota del libro viven en
                # el Diccionario, en la pregunta frecuente del Ramo 28 y el
                # Ramo 33.
                'mosaico': 'np-mosaico',
                'bloque': '',
                'tarjetas': [
                    ('📍', 'El mapa del gasto federalizado', 'Las 32 entidades sobre el mapa, con cinco lentes: lo que reciben por los Ramos 28 y 33, por habitante, su dependencia federal, su deuda y lo que dejó por aclarar la ASF.',
                     'numeros-mapa-del-gasto-federalizado.html', 'Acuerdo de distribución de los Ramos 28 y 33 (DOF)', 'dinero',
                     'Cinco lentes y las 32, de mayor a menor'),
                    ('🗺️', 'Las 32 entidades: del peso federal al estatal', 'Los tres pisos de la hacienda, lo que baja y con qué libertad (Ramos 28, 33 y 25 y convenios) y el circuito de cada estado.',
                     'numeros-las-32-entidades.html', 'Presupuesto de Egresos 2026 e INEGI', 'dinero',
                     'Tres pisos, cuatro ramos y el circuito de cada estado'),
                    ('🏘️', 'Los 2,479 municipios: predial y transferencias', 'FORTAMUN y FISMDF, lo que la ley les garantiza sin cifra, lo que cobran por su cuenta, el punto ciego del artículo 115 y el padrón completo del INEGI, municipio por municipio.',
                     'numeros-los-municipios.html', 'INEGI, finanzas públicas municipales 2024', 'dinero',
                     'Sus fondos, su predial y el padrón completo'),
                ],
            },
            {
                # «Se paga lo que se debe» y «Se revisa» se fundieron en
                # «Cuentas claras» (pedido del autor, 11-10-2026): lo que se
                # debe, lo que se gasto de verdad y quien lo revisa.
                'id': 'cuentas',
                'pestana': ('⚖️', '4 · Cuentas claras', 'Lo que se debe y quién lo revisa'),
                'num': 4,
                'titulo': 'Cuentas claras: lo que se debe y quién lo revisa',
                'texto': ('El recorrido se cierra con dos cuentas. La primera, la deuda: lo que el país pidió prestado de 1994 a la '
                          'proyección de 2027, sexenio por sexenio; pulsa «Contabilizar» y mírala crecer. La segunda, la rendición: al '
                          'año siguiente el gobierno entrega la Cuenta Pública y la Auditoría Superior de la Federación la revisa. '
                          'Abajo, lo que se gastó de verdad, lo que quedó por aclarar y el balance de todo el recorrido.'),
                # Su «Ayer y hoy» lo cuentan sus paginas de la deuda (12-10-2026).
                'bloque': ('<div class="dt" id="deudaTiempo">\n'
                           '          <noscript><p>La línea de tiempo necesita JavaScript. La serie, con sus fuentes, está en el auditor.</p></noscript>\n'
                           '        </div>'),
                # La vista del motor abre su pagina de modulo; las que son
                # herramientas (el reloj, el inspector de la ASF) van a su
                # pagina en Herramientas, sin duplicarlas aqui.
                'tarjetas': [
                    ('📒', 'El estado de resultados del Gobierno', 'La Cuenta Pública 2024 leída como un negocio: actividades, flujos, situación financiera y gasto social.', 'numeros-estado-de-resultados.html', None, 'dinero'),
                    ('🧭', 'Contexto dimensional', 'El balance de todo el recorrido: lo que entró, lo que se gastó, lo que se debe y lo que se perdió, 2024 frente a 2026 y 2027.', 'estado-de-cuenta.html', None, 'dinero'),
                    ('🔍', 'Expedientes de casos de la ASF', 'Los casos que la Auditoría Superior dejó abiertos, lo que encontró en la Cuenta Pública 2024 sector por sector y quién más fiscaliza. Es una herramienta: abre en el Auditor Virtual.', 'herramienta-inspector-asf.html', None, 'inspector'),
                    ('⏱️', 'El reloj de la deuda', 'Lo que el país se endeuda, paga de intereses y pierde por segundo, con su contador en vivo. Es una herramienta: abre en el Auditor Virtual.', 'herramienta-calculadora-reloj.html', None, 'inspector'),
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
        # El radar y sus anclas viejas (#rc-*) llevan a su pagina.
        'hash_a_pagina': {'radar': 'radar-hacendario.html', 'rc-megaobras': 'numeros-cuanto-dinero-es.html',
                          'rc-deuda': 'numeros-cuanto-dinero-es.html', 'rc-asf': 'numeros-cuanto-dinero-es.html',
                          'rc-huachicol': 'numeros-cuanto-dinero-es.html',
                          'estado-de-cuenta': 'radar-estado-de-cuenta.html', 'ambiente': 'datos-medio-ambiente.html', **DATOS_ANCLAS},
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
                # Desde el 11-10-2026 (pedido del autor) Datos abiertos e
                # Informes oficiales abren su pagina (datos_paginas()).
                'id': 'abiertos',
                'pagina': 'datos-abiertos.html',
                'pestana': ('💾', 'Datos abiertos', 'Bases en CSV para Excel: abre su página'),
            },
            {
                'id': 'informes',
                'pagina': 'informes-oficiales.html',
                'pestana': ('📑', 'Informes oficiales', 'Cuenta Pública y diccionario: abre su página'),
            },
            {
                # Cuarta tarjeta de Datos desde el 22-10-2026 (pedido del
                # autor): la parte informativa de Costo Ambiental.
                'id': 'ambiente',
                'pagina': 'datos-medio-ambiente.html',
                'pestana': ('🌎', 'Medio ambiente', 'El daño, la basura, el dinero y las leyes: abre su página'),
            },
            {
                # Los Poderes Legislativo y Judicial (23-10-2026, pedido del
                # autor): poderes_paginas(), una pagina por grupo de temas.
                'id': 'legislativo',
                'pagina': 'datos-poder-legislativo.html',
                'pestana': ('🏛️', 'Poder Legislativo', 'Curules, sesiones, presupuesto y elecciones: abre su página'),
            },
            {
                'id': 'judicial',
                'pagina': 'datos-poder-judicial.html',
                'pestana': ('⚖️', 'Poder Judicial', 'La Corte, los circuitos, los sueldos y la elección: abre su página'),
            },
            # El Estado de cuenta administrativo fue la cuarta tarjeta de Datos
            # del 12-10-2026 al 22-10-2026; desde entonces (pedido del autor)
            # es la quinta aplicacion de la Calculadora Civica. Su ancla vieja
            # lleva a su pagina, que no cambia de direccion.
        ],
    },
    {
        'archivo': 'aprende.html',
        'menu': 'Aprende',
        'icono': '📖',
        'titulo': 'Aprende',
        'lema': 'Biblioteca y fuentes del auditor ciudadano',
        # Las pestanas viejas de los estantes (10-10-2026) llevan a la Biblioteca.
        # Noticias relevantes es su propia pagina desde el 11-10-2026; los
        # enlaces a una columna (#col-<id>) llegan a ella con su ancla.
        'hash_a_pagina': {'biblioteca': 'diccionario.html', 'kit': 'diccionario.html',
                          'noticias': 'noticias-relevantes.html', 'col-*': 'noticias-relevantes.html',
                          'congreso': 'datos-poder-legislativo.html'},
        'entrada': ('Las palabras del presupuesto, las leyes que lo rigen y las fuentes donde se publica, '
                    'explicadas en lenguaje llano. Para leer una cifra oficial no hace falta ser especialista. '
                    'Para ponerte a prueba, una trivia con el estado de cuenta de cada presidente; y para leer con calma, columnas con datos curiosos de personajes y hechos.'),
        'scripts': ['trivia-presidentes.js'],
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
                # Biblioteca del Erario Publico (decision del autor, 11-10-2026):
                # la pestana ya no despliega, abre la Biblioteca, con sus cuatro
                # apartados. El id sigue siendo 'diccionario' para no romper enlaces.
                'id': 'diccionario',
                'pagina': 'diccionario.html',
                'pestana': ('📚', BIB_NOMBRE, 'Diccionario, referencias, marco legal y preguntas: abre su página'),
            },
            {
                # Columnas editoriales (09-10-2026). Desde el 11-10-2026 (pedido
                # del autor) son su propia pagina: NOTICIAS.
                'id': 'noticias',
                'pagina': 'noticias-relevantes.html',
                'pestana': ('📰', 'Noticias relevantes', 'La Columna del Erario: abre su página'),
            },
            # «El Congreso y las elecciones» fue la cuarta pestaña de Aprende la
            # mañana del 23-10-2026; esa tarde (pedido del autor) se mudó a
            # Datos, como «Poder Legislativo» (poderes_paginas()).
        ],
    },
    {
        'archivo': 'participa.html',
        # Desde el 23-10-2026 la pestaña se llama «Comunidad» y su tarjeta
        # «Comunidad» pasa a llamarse «Participa» (decisión del autor). Los
        # archivos se quedan como estaban para no romper enlaces.
        'menu': 'Comunidad',
        'icono': '💬',
        'titulo': 'Comunidad',
        'lema': 'Ágora cívica y canales oficiales',
        'entrada': ('Contrasta posturas con fuentes, publica tu argumento y, si viste algo raro con el dinero público, '
                    'llévalo al canal oficial que corresponde. Sin correos, teléfonos ni rastreo.'),
        'pestanas': True,
        # «Servicios» paso al Modo Inspector (pedido del autor, 11-10-2026).
        'hash_a_pagina': {'agora': 'agora.html', 'garantias': 'garantias.html', 'servicios': 'servicios.html',
                          'pase': 'donaciones.html', 'comunidad': 'comunidad.html', 'donaciones': 'donaciones.html'},
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
            # «Cuéntanos lo que viste» (comunidad.html) fue tarjeta de esta
            # pestana hasta el 24-10-2026: ese dia (pedido del autor) se fundio
            # con el boton «Cuéntanos lo que viste» de la cabecera, que es su
            # unica puerta. Comunidad queda con tres tarjetas.
            {
                # Pedido del autor, 11-10-2026: una via mas para sostener la
                # plataforma, con su alcancia a la vista (donaciones()).
                # El Pase del Auditor Civico se retiro el 24-10-2026 (decision
                # del autor): sostener la plataforma tiene dos vias en
                # evaluacion, las donaciones y los Servicios del Auditor
                # Virtual (docs/LANZAMIENTO.md §4.4). pase-del-auditor.html
                # redirige aqui.
                'id': 'donaciones',
                'pagina': 'donaciones.html',
                'pestana': ('🐷', 'Donaciones', 'Ayuda a sostener la plataforma, a la vista de todos: abre su página'),
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
    # Imagen del Modo Inspector desde el 24-10-2026 (la eligió el autor); el
    # foróptero se queda en el Auditor Virtual (foto_clase 'foto-auditor').
    'inspector': 'assets/auditor/img/herr-inspector-camaras.jpg',
    'ambiente': 'assets/auditor/img/herr-ambiente-refineria-amplia.jpg',
}

# (archivo, rubro, icono, titulo, subtitulo, texto, modulo del motor, temas)
# Cada tema: (ancla sin «eb-», icono, nombre, frase de la pestana,
# descripcion). Un tema que es un .html es un enlace a esa pagina.
HERRAMIENTAS = [
    ('herramienta-megaobras.html', 'obras', '🏗️', 'Inversión y Megaobras',
     'Lo que se prometió, lo que se pagó y la diferencia',
     'Seguimiento a costos, sobrecostos y subsidios de las obras que definieron cada sexenio: Tren Maya, Dos Bocas, AIFA y los demás '
     'proyectos estratégicos de la nación, desde 1988 a la fecha. Cada cifra remite al documento que la sostiene.'
     ' Todo también lo preguntas en el chat del <a href="herramienta-inspector-pregunta.html">Auditor</a>: cada obra, cada presidente y las cinco aplicaciones.',
     'megaobras',
     # Desde el 21-10-2026 (pedido del autor) las cuatro aplicaciones son una
     # sola herramienta en capitulos y, el mismo dia, cuatro aplicaciones
     # nuevas: la lista vive en herramientas/mo_capitulos.py.
     mo_capitulos.temas()),
    ('herramienta-calculadora.html', 'calculadora', '💳', 'Calculadora Cívica',
     'Tu sueldo, tus impuestos y el rubro al que llegan',
     'Escribe tu sueldo y la calculadora reparte lo que pagas (ISR, IVA y predial) entre los rubros del presupuesto. Después compara tu '
     'estado y tu municipio con los 2,479 del padrón nacional.',
     'calculadora', [
         ('ccticket', '🧾', 'Tu estado de cuenta', 'Lo que pagas y a dónde va',
          'Cuatro cuentas, cada una en su página: tu ingreso, lo que te retienen, a dónde va cada peso de tu impuesto y tu estado de cuenta.'),
         ('cccompara', '⚡', 'Tú contra ellos', 'Cargo por cargo',
          'Tu ingreso neto frente al de quienes legislan, juzgan y gobiernan, y sus prestaciones de ley contra las tuyas, con el documento de cada cifra.'),
         ('ccreloj', '⏱️', 'El reloj de la deuda', 'Y de lo perdido',
          'Lo que el país se endeuda, paga de intereses y pierde por segundo, repartido entre habitantes o entre contribuyentes, con su contador en vivo.'),
         ('simulador-presupuesto.html', '🧮', 'Reparte el presupuesto', 'Desde cero',
          'Empieza en $0: agrega lo que entra, reparte a dónde va, carga el ejemplo oficial de 2026 o 2027, compara dos escenarios y descarga la cuenta. Tiene su propia página.'),
         # Quinta aplicacion desde el 22-10-2026 (pedido del autor): venia de
         # la pestana Datos. La direccion no cambia: va impresa en los sellos.
         ('radar-estado-de-cuenta.html', '🏛️', 'Estado de cuenta administrativo', 'Gobiernos, Congreso y Corte',
          'Elige de quién: una administración presidencial, la diputación federal, la senaduría, un congreso local o la Suprema Corte. Genera su estado de cuenta con su semáforo y descárgalo en PDF con folio y sello de verificación.'),
     ]),
    ('herramienta-inspector.html', 'inspector', '🔍', 'Modo Inspector',
     'Dónde quedó el dinero que nadie ha podido explicar',
     'Expedientes de la Auditoría Superior de la Federación (ASF), adjudicaciones directas, empresas que facturan operaciones simuladas '
     '(EFOS) y focos rojos de riesgo. Solo informes oficiales: pliegos de observaciones, montos por aclarar y contratos abiertos.'
     ' Y si un caso necesita ir más a fondo, en la aplicación de Servicios puedes pedir una investigación a la medida: cada cifra con su documento y bajo una política de independencia.'
     ' Las seis también las usas desde el chat del <a href="herramienta-inspector-pregunta.html">Auditor</a>, sin salir de la plática.',

     'verificador', [
         # «Que encontro la ASF» y «Expedientes de casos» se fusionaron el
         # 21-10-2026 (pedido del autor) en una sola aplicacion, con todas las
         # autoridades que fiscalizan y su agente de busqueda (insp_asf.py).
         ('inspasf', '🏛️', 'Expedientes de casos de la ASF', 'Los expedientes oficiales',
          'Los casos por aclarar, lo que la Auditoría Superior encontró en el gasto de 2024 y 2025 y lo que publicará de 2026 y 2027, y todas las autoridades que fiscalizan, cada una con su expediente oficial.'),
         # El Radar por entidad (antes la aplicacion 2) se fusiono el
         # 21-10-2026 con la ficha estatal del Auditor de entes publicos.
         ('inspentes', '🏢', 'Auditor de entes públicos', 'Busca y verifica',
          'Elige una autoridad federal, estatal o municipal y ve su diagnóstico: si gastó lo que aprobó la Cámara, si rindió cuentas y qué quedó por aclarar. Cada estado trae su radar de la Auditoría Superior: su lugar entre los 32.'),
         ('inspnota', '📰', 'Contrasta una nota', 'Busca y verifica',
          'Pega la liga de una noticia, una revista o una publicación en redes: leemos sus cifras, las ponemos junto al documento oficial y te damos un veredicto, cifra por cifra.'),
         ('inspefos', '🧾', 'Lista negra del SAT', 'Busca y verifica',
          'Busca por RFC o por nombre en el listado del artículo 69-B del Código Fiscal: a quienes el SAT presume o declara emisores de facturas por operaciones inexistentes.'),
         ('inspverifica', '🔏', 'Verifica un estado de cuenta', 'Busca y verifica',
          '¿Te compartieron un estado de cuenta de Auditavisión? Escribe su folio o su huella digital y comprueba, cifra por cifra, que no se alteró.'),
         # Venia de la pestana «Servicios» de Participa (pedido del autor, 11-10-2026).
         ('servicios.html', '🔎', 'Servicios de investigación', 'Investigación a la medida',
          'Cuando necesites ir más a fondo en un caso: revisión documental, expediente, seguimiento, capacitación o licencia, con la misma regla de la plataforma y su política de independencia. Tiene su propia página.'),
     ]),
    # Reestructurada el 22-10-2026 (pedido del autor): la herramienta se
    # queda con lo que el lector calcula y audita; la parte informativa
    # (la basura, el presupuesto, las leyes, la cascada del PIB...) vive en
    # Datos → Medio ambiente (herramientas/datos_ambiente.py).
    ('herramienta-ambiente.html', 'ambiente', '🌎', 'Costo Ambiental',
     'El gasto que no aparece en el recibo',
     'El deterioro del ambiente también es gasto: lo pagamos en agua, aire, suelo y basura. Aquí haces tus cuentas con cifras oficiales '
     '(INEGI, SEMARNAT, Hacienda y la Auditoría Superior): tu estado de cuenta ambiental, el reloj del daño, los simuladores del crecimiento real y de la '
     'inversión, el auditor del sector y las investigaciones de las crisis. Las cifras de referencia viven en '
     '<a href="datos-medio-ambiente.html">Datos → Medio ambiente</a>.',
     'ambiente', [
         ('amticket', '🧾', 'Tu estado de cuenta ambiental', 'Lo que ya te cargaron a tu nombre',
          'Escribe lo que ganas y ve lo que ya te cargaron a tu nombre: tu parte de la deuda, de sus intereses y del daño ambiental, con tu basura en kilos.'),
         ('amreloj', '⏱️', 'El reloj y el año', 'Un año en veinte segundos',
          'El daño ambiental que corre mientras lees y una simulación que acumula, día por día, cinco comparaciones de un año entero.'),
         ('ampib', '📈', '¿Cuánto del crecimiento es real?', 'El simulador del PIB verde',
          'Mueve el crecimiento, el costo ambiental y el desgaste de la maquinaria, y ve si la riqueza que de verdad queda crece o se encoge.'),
         ('aminversion', '🌱', 'Simulador de inversión ambiental', 'Si se invirtiera en el ambiente',
          'En cuántos años alcanzaría el gasto en proteger al costo del daño, y cuánto pesan los intereses de la deuda frente a cada órgano del sector.'),
         ('amauditor', '🔍', 'Auditor ambiental', 'Órgano por órgano',
          'Elige la SEMARNAT, la Conagua, la CONAFOR, la PROFEPA u otro órgano: lo aprobado, lo pagado, lo que se propone para 2027, lo que observó la Auditoría Superior y las preguntas que deja.'),
         # Sexta aplicacion (pedido del autor, 11-10-2026): la arma
         # herramientas/crisis_ambientales.py.
         ('herramienta-ambiente-crisis.html', '🌀', 'Crisis ambientales', 'Investigaciones',
          'Huracanes, inundaciones y crisis del agua: cuánto cubre el fondo, cuánto se anunció, cuánto se comprobó y lo que cuesta esperar. Con Otis, Simón y el agua de Guadalajara.'),
     ]),
]

# Herramientas cuyos modulos son «aplicaciones» y llevan su icono grande en
# el encabezado, sobre el tono de su imagen (pedido del autor, 11-10-2026:
# Costo Ambiental, verde gris; el mismo dia, las otras tres: naranja para
# Megaobras, dorado para la Calculadora y gris para el Modo Inspector, y las
# tarjetas de la pestana Herramientas se quedan sin icono).
# (singular, plural, articulo del plural)
HERR_PALABRA = {'ambiente': ('aplicación', 'aplicaciones', 'Las'), 'inspector': ('aplicación', 'aplicaciones', 'Las'),
                'calculadora': ('aplicación', 'aplicaciones', 'Las'), 'obras': ('aplicación', 'aplicaciones', 'Las')}
# Herramientas que parten sus aplicaciones en divisiones (pedido del autor,
# 11-10-2026): el Modo Inspector tiene «Grandes investigaciones» (sus seis
# aplicaciones) y, aparte, el bot interno «Preguntale al Auditor»
# (herramientas/asistente.py).
# Desde el 24-10-2026 (decisión del autor) «Grandes investigaciones» ES el
# Modo Inspector: una sola página, herramienta-inspector.html, con las seis
# aplicaciones. La vieja página de las investigaciones redirige ahí.
HERR_DIVISION = {'inspector': ('Modo Inspector', 'Grandes investigaciones a través de seis aplicaciones. Recórrelas en orden o entra directo a la que te interesa: cada una abre su propia página.')}
ASISTENTE = ('herramienta-inspector-pregunta.html', 'Pregúntale al Auditor', 'Pregunta fácil, respuesta fácil',
             'El chat de Auditavisión. Pregúntale lo que quieras del dinero público, como lo dirías platicando: cuánto debe un estado, cuánto le llega a un municipio, cuánto gana un cargo o qué significa un término. Te contesta en corto y con datos oficiales, y si quieres el respaldo, te lleva a la página donde está la información y te arma el dictamen con su respaldo.')
LOGO_IMG = '<img src="assets/auditor/img/logo-auditavision.svg" alt="" width="62" height="48">'
# Desde el 11-10-2026 (pedido del autor) las dos divisiones del Modo Inspector
# son tarjetas autonomas: la pagina de la herramienta solo las presenta y cada
# una abre su propia pagina.
INVESTIGACIONES = 'herramienta-inspector-investigaciones.html'
FOTO_AUDITOR = 'assets/auditor/img/herr-inspector-foroptero-amplia.jpg'
MODO_INSPECTOR = 'herramienta-inspector.html'
# El menú «Herramientas» del chat (pedido del autor, 23-10-2026), en el orden
# que pidió.
HERR_MENU = [(h[0], h[2], h[3], h[4], HERR_IMG[h[1]])
             for r in ('inspector', 'ambiente', 'calculadora', 'obras') for h in HERRAMIENTAS if h[1] == r]
HERR_ICONO_CAB = {'ambiente', 'obras', 'calculadora', 'inspector'}


def herr_palabra(rubro):
    return HERR_PALABRA.get(rubro, ('módulo', 'módulos', 'Los'))


# Modulos que no abren la portada en un marco: su pagina la arma otra funcion
# (la verificacion de estados de cuenta, en radar()).
MODULOS_PROPIOS = {'inspverifica'}
# Aplicaciones del Modo Inspector que ya no abren la portada en un marco
# (pedido del autor, 12-10-2026: «se traba y se pone a calcular»). Cada
# modulo de herramientas/ arma su pagina con construir(base, ref) y dice
# sus ESTILOS y SCRIPTS (assets/auditor/css y js).
INSP_NATIVAS = {'inspasf': 'insp_asf', 'inspentes': 'insp_entes',
                'inspnota': 'insp_nota', 'inspefos': 'insp_efos',
                # Calculadora Civica (pedido del autor, 12-10-2026): sus tres
                # aplicaciones que abrian el motor en un marco.
                'ccticket': 'cc_ticket', 'cccompara': 'cc_compara', 'ccreloj': 'cc_reloj',
                # Inversion y Megaobras (pedido del autor, 13-10-2026).
                'pulso': 'mo_pulso', 'sector': 'mo_sector', 'sexenios': 'mo_sexenios', 'cero': 'mo_cero',
                'tabla': 'mo_tabla', 'investiga': 'mo_investiga',
                # Costo Ambiental (pedido del autor, 16-10-2026).
                'amreloj': 'am_reloj', 'amticket': 'am_ticket', 'ampib': 'am_pib',
                # Las dos nuevas de la reestructura (22-10-2026); am_basura dejo
                # de ser aplicacion: sus bloques viven en Datos → Medio ambiente.
                'aminversion': 'am_inversion', 'amauditor': 'am_auditor'}


def insp_nativa(m, clave, base, ref):
    """Pone en la pagina m (de herramienta_modulo) el contenido propio de la
    aplicacion en lugar del marco con la portada."""
    nat = importlib.import_module(INSP_NATIVAS[clave])
    m['secciones'][0]['bloque'] = nat.construir(base, ref)
    m['estilos'] = list(getattr(nat, 'ESTILOS', []))
    m['scripts'] = list(getattr(nat, 'SCRIPTS', []))
    return m


def insp_subpaginas(m, clave, base, ref):
    """Paginas hijas de una aplicacion nativa (17-10-2026): si su modulo
    trae subpaginas(), cada parte sale en su propia pagina, debajo de la
    aplicacion en las migas. Hoy: las cuatro partes de El pulso del gasto y
    los nueve capitulos de Que encontro la ASF (21-10-2026; el catalogo de
    cifras oficiales es el octavo, con sus propios estilos y scripts). Si la
    subpagina trae cap_nav, su pie va de capitulo en capitulo."""
    nat = importlib.import_module(INSP_NATIVAS[clave])
    if not hasattr(nat, 'subpaginas'):
        return []
    out = []
    for k, sp in enumerate(nat.subpaginas(base, ref), 1):
        h = dict(m)
        h.update({'archivo': sp['archivo'], 'menu': sp['menu'], 'titulo': sp['titulo'], 'icono': sp['icono'],
                  'entrada': sp['entrada'], 'padre3': (m['archivo'], m['titulo']),
                  'lema': sp.get('lema') or '%s · parte %d' % (m['titulo'], k),
                  'icono_cab': sp['icono'] if m.get('icono_cab') else '',
                  'secciones': [dict(m['secciones'][0], bloque=sp['bloque'])]})
        if 'cap_nav' in sp:
            h['cap_nav'] = sp['cap_nav']
        for k2 in ('estilos', 'scripts'):
            if k2 in sp:
                h[k2] = list(sp[k2])
        out.append(h)
    return out
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
        '%s<span class="herr-otra-tx">%s</span></a>'
        % (o[1], o[0], '' if o[1] in HERR_ICONO_CAB else '<span class="herr-otra-ico" aria-hidden="true">%s</span>' % o[2], o[3])
        for o in HERRAMIENTAS if o[0] != archivo)
    return ('<nav class="herr-otras" aria-label="Las otras herramientas">\n'
            '        <span class="herr-otras-tit">Las otras herramientas</span>\n'
            '        <div class="herr-otras-fila">\n%s\n        </div>\n      </nav>' % otras)


def apps_rejilla(h, cifras=None):
    """Las aplicaciones de una herramienta, numeradas y en vertical, como el
    Modo Inspector (pedido del autor, 22-10-2026: «enumeradas de forma
    vertical como estaban antes»). cifras ya no se usa: se queda el
    parametro para no romper a quien lo llame."""
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
    return '<ol class="herr-ruta">\n%s\n        </ol>' % '\n'.join(pasos)


def herramienta(h, n):
    """Pagina de una herramienta (10-10-2026): ya no despliega nada. Es la
    ruta de sus modulos, numerados, y cada uno abre su propia pagina
    (herramienta_modulo). Antes cada pestana abria la portada entera en un
    marco debajo de la tarjeta."""
    archivo, rubro, icono, titulo, sub, texto, modulo, temas = h
    pal = herr_palabra(rubro)
    ruta = apps_rejilla(h)
    division = HERR_DIVISION.get(rubro)
    if rubro == 'inspector':
        return herramienta_divisiones(h, n, ruta)
    return {
        'archivo': archivo,
        'menu': titulo,
        'menu_archivo': 'herramientas.html',
        'padre': (AUDITOR_VIRTUAL, 'Auditor Virtual'),
        'icono': icono,
        'titulo': titulo,
        'lema': 'Herramienta %d de %d' % (n, len(HERRAMIENTAS)),
        'sin_icono_lema': rubro in HERR_ICONO_CAB,
        'icono_cab': icono if rubro in HERR_ICONO_CAB else '',
        'entrada': '<b>%s.</b> %s' % (sub, texto),
        'fondo': HERR_IMG[rubro],
        'rubro': rubro,
        # Las pestanas viejas (#pulso, #inspentes...) llevan a su pagina.
        'hash_a_pagina': dict((t[0][:-5] if t[0].endswith('.html') else t[0], modulo_archivo(archivo, t[0])) for t in temas),
        'secciones': [{
            'id': 'modulos', 'titulo': ('%s · %s %d %s' % (division[0], pal[2].lower(), len(temas), pal[1])) if division else
                                       '%s %d %s' % (pal[2], len(temas), pal[1]), 'sin_cab': False,
            'texto': division[1] if division else
                     ('Recórrelas en orden o entra directo a la que te interesa. Cada una abre su propia página.' if pal[2] == 'Las' else
                      'Recórrelos en orden o entra directo al que te interesa. Cada uno abre su propia página.'),
            'tarjetas': [], 'bloque': ruta,
        }],
        'pie_extra': herr_otras(archivo),
    }


def herramienta_divisiones(h, n, ruta):
    """Modo Inspector. Desde el 24-10-2026 (decisión del autor) es las Grandes
    investigaciones: su página muestra directo las seis aplicaciones. El chat
    ya no es su «otra división»: es la portada del Auditor Virtual."""
    archivo, rubro, icono, titulo, sub, texto, modulo, temas = h
    division = HERR_DIVISION[rubro]
    principal = {
        'menu_archivo': 'herramientas.html',
        'padre': (AUDITOR_VIRTUAL, 'Auditor Virtual'),
        'fondo': HERR_IMG[rubro],
        'rubro': rubro,
        'sin_icono_lema': True,
        'archivo': archivo, 'menu': titulo, 'icono': icono, 'titulo': titulo,
        'lema': 'Grandes investigaciones · %d aplicaciones' % len(temas),
        'icono_cab': icono,
        'entrada': '<b>%s</b> %s' % (division[1].split('. ')[0] + '.', texto),
        # Las pestanas viejas (#pulso, #inspentes...) y las secciones que
        # vivian aqui (#pregunta...) llevan a su pagina.
        'hash_a_pagina': dict([(t[0][:-5] if t[0].endswith('.html') else t[0], modulo_archivo(archivo, t[0])) for t in temas] +
                              [('pregunta', ASISTENTE[0]),
                               ('inspradar', 'herramienta-inspector-entes.html?nivel=estatal&orden=radInt#ie-dir'),
                               ('expedientes', 'expedientes.html')]),
        'secciones': [{
            'id': 'apps', 'titulo': 'Las %d aplicaciones' % len(temas), 'sin_cab': False,
            'texto': 'Recórrelas en orden o entra directo a la que te interesa. Cada una abre su propia página.',
            'tarjetas': [], 'bloque': ruta,
        }],
        'pie_extra': herr_otras(archivo),
    }
    return principal


def herramienta_modulo(h, n, i, bloque=None):
    """Pagina propia de un modulo de herramienta (10-10-2026). Con bloque, la
    pagina trae su propio contenido en lugar del marco con la portada (la
    quinta aplicacion de Costo Ambiental, 11-10-2026)."""
    archivo, rubro, icono, titulo, sub, texto, modulo, temas = h
    clave, ico, nombre, frase, desc = temas[i]
    pal = herr_palabra(rubro)
    url = ir(modulo, 'eb-' + clave)
    hermanos = []
    for k, t in enumerate(temas):
        hermanos.append('          <a class="herr-mod-chip%s" href="%s"%s><span aria-hidden="true">%s</span> %d · %s</a>' % (
            ' actual' if k == i else '', modulo_archivo(archivo, t[0]), ' aria-current="page"' if k == i else '', t[1], k + 1, t[2]))
    ant = temas[i - 1] if i > 0 else None
    sig = temas[i + 1] if i + 1 < len(temas) else None
    def paso(t, k, rotulo, clase):
        if not t and rubro == 'inspector':
            return ('          <a class="herr-mod-paso %s" href="%s"><small>%s</small><b>%s %s</b></a>'
                    % (clase, MODO_INSPECTOR, rotulo, icono, HERR_DIVISION[rubro][0]))
        if not t:
            return ('          <a class="herr-mod-paso %s" href="%s"><small>%s</small><b>%s %s</b></a>'
                    % (clase, archivo, rotulo, icono, titulo))
        return ('          <a class="herr-mod-paso %s" href="%s"><small>%s · %s %d</small><b>%s %s</b></a>'
                % (clase, modulo_archivo(archivo, t[0]), rotulo, pal[0], k + 1, t[1], t[2]))
    navegacion = ('<nav class="herr-mod-nav" aria-label="%s %s de %s">\n'
                  '        <div class="herr-mod-pasos">\n%s\n%s\n        </div>\n'
                  '        <span class="herr-otras-tit">%s %s de %s</span>\n'
                  '        <div class="herr-mod-chips">\n%s\n        </div>\n      </nav>' % (
                      pal[2], pal[1], titulo,
                      paso(ant, i - 1, '← Anterior', 'ant') if ant else paso(None, 0, '← Volver al índice de', 'ant'),
                      paso(sig, i + 1, 'Siguiente →', 'sig') if sig else paso(None, 0, 'Terminaste · volver a', 'sig'),
                      'Todas las' if pal[2] == 'Las' else 'Todos los', pal[1], titulo, '\n'.join(hermanos)))
    carga = ('la ' if pal[2] == 'Las' else 'el ') + pal[0]
    marco = bloque or ('<div class="apartado-visor herr-modulo" style="--tarjeta: var(--rubro-%s)">\n'
             '          <div class="apartado-visor-cuerpo">\n'
             '            <p class="apartado-visor-carga" role="status">⏳ Cargando %s con sus cifras y fuentes…</p>\n'
             '            <iframe class="apartado-visor-marco" title="%s" data-modulo="%s&amp;visor=1"></iframe>\n'
             '            <noscript><p>%s necesita JavaScript. <a href="%s">Ábrelo en el auditor</a>.</p></noscript>\n'
             '          </div>\n'
             '          <div class="herr-modulo-pie"><a href="%s">⤢ Abrir en el auditor completo</a></div>\n'
             '        </div>' % (rubro, carga, esc_attr(nombre), url, 'Esta aplicación' if pal[2] == 'Las' else 'Este módulo', url, url))
    return {
        'archivo': modulo_archivo(archivo, clave),
        'menu': nombre,
        'menu_archivo': 'herramientas.html',
        'padre': (AUDITOR_VIRTUAL, 'Auditor Virtual'),
        'padre2': (archivo, titulo),
        'icono': ico,
        'titulo': nombre,
        'lema': ('%s · %s %d de %d' % (titulo, pal[0], i + 1, len(temas)) if rubro in HERR_ICONO_CAB else
                 '%s %s · %s %d de %d' % (icono, titulo, pal[0], i + 1, len(temas))),
        'sin_icono_lema': True,
        'icono_cab': ico if rubro in HERR_ICONO_CAB else '',
        'entrada': '<b>%s.</b> %s' % (frase, desc),
        'fondo': HERR_IMG[rubro],
        'rubro': rubro,
        'secciones': [{
            'id': 'modulo', 'titulo': nombre, 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': marco,
        }],
        'pie_extra': navegacion + '\n\n      ' + herr_otras(archivo),
    }


def megaobras_portada(hp, base, ref):
    """Inversion y Megaobras en cinco aplicaciones (pedidos del autor,
    21-10-2026): la portada lleva la lista de sus aplicaciones, numerada y
    en vertical (22-10-2026), y el boton de «¿Como se calcula?». El cuadro «Haz tu
    propia investigacion» es ahora la aplicacion 1 (mo_investiga.py)."""
    import mo_pulso
    h = next(x for x in HERRAMIENTAS if x[1] == 'obras')
    hp['secciones'][0]['bloque'] = mo_pulso.cajon_calculo(base, ref) + apps_rejilla(h)
    hp['estilos'] = ['mo-pulso.css']
    # La aplicacion «El pulso del gasto» ya no tiene pagina: su pestana vieja
    # lleva a sus cuatro cifras.
    hp['hash_a_pagina'] = dict(hp.get('hash_a_pagina') or {}, pulso='herramienta-megaobras-cero.html#mpCifras')
    return hp


def megaobras_pulso(h, n, base, ref):
    """Las partes de «El pulso del gasto», que desde el 21-10-2026 son
    capitulos de Inversion y Megaobras: se generan con mo_pulso.subpaginas()
    sin la pagina del pulso (redirige a la portada, REDIRECCIONES), con el
    lema y el pie de capitulo."""
    tema = ('pulso', '📊', 'El pulso del gasto', 'Costo y sobrecosto', '')
    m = herramienta_modulo(h[:7] + ([tema],), n, 0)
    # Sus estilos y su codigo (mo-pulso.css y .js), como insp_nativa().
    nat = importlib.import_module(INSP_NATIVAS['pulso'])
    m['estilos'] = list(nat.ESTILOS)
    m['scripts'] = list(nat.SCRIPTS)
    out = []
    for sp in insp_subpaginas(m, 'pulso', base, ref):
        cap = mo_capitulos.CAPITULOS[mo_capitulos.numero(sp['archivo']) - 1]
        sp.update({'lema': mo_capitulos.kicker(sp['archivo']), 'padre3': None, 'titulo': cap[3], 'menu': cap[3],
                   'cap_nav': mo_capitulos.vecinos(sp['archivo'])})
        sp['secciones'] = [dict(sp['secciones'][0], titulo=cap[3])]
        out.append(sp)
    return out


def nav_compacta(h, i, padre=None):
    """Navegacion de una sola fila para el pie de una aplicacion (pedido del
    autor, 21-10-2026: la grande «absorbe mucha parte de la pagina»; el
    mismo dia, para todas las aplicaciones): anterior, todas las
    aplicaciones, siguiente e indice general, sin las tarjetas grandes ni
    las otras herramientas. En una subpagina (padre), el primer boton
    vuelve a su aplicacion y no hay anterior ni siguiente."""
    archivo, rubro, icono, titulo, sub, texto, modulo, temas = h
    pal = herr_palabra(rubro)
    todas = archivo
    ant = temas[i - 1] if i > 0 and not padre else None
    sig = temas[i + 1] if i + 1 < len(temas) and not padre else None
    # Los rotulos de Inversion y Megaobras (21-10-2026): «Aplicacion
    # anterior», «Las N aplicaciones», «Aplicacion siguiente».
    def boton(t, clase, rotulo):
        return ('        <a class="herr-min %s" href="%s"><span>%s</span><small>%s %s</small></a>'
                % (clase, modulo_archivo(archivo, t[0]), rotulo, t[1], t[2]))
    filas = ['        <a class="herr-min ant" href="%s"><span>← Volver</span><small>%s</small></a>' % padre if padre else '',
             boton(ant, 'ant', '← %s anterior' % pal[0].capitalize()) if ant else '',
             '        <a class="herr-min" href="%s"><span>%s %d %s</span><small>%s</small></a>' % (
                 todas, pal[2], len(temas), pal[1],
                 HERR_DIVISION[rubro][0] if rubro == 'inspector' else titulo),
             boton(sig, 'sig', '%s siguiente →' % pal[0].capitalize()) if sig else '',
             '        <a class="herr-min" href="indice.html"><span>Índice</span><small>Todo Auditavisión</small></a>']
    return ('<nav class="herr-nav-min" aria-label="Moverte desde aquí">\n%s\n      </nav>'
            % '\n'.join(f for f in filas if f))


def nav_capitulos(padre, cap, palabra=('Capítulo', 'capítulos')):
    """Pie de un capitulo con pagina propia (pedido del autor, 21-10-2026):
    capitulo anterior, todos los capitulos (la portada de la aplicacion),
    capitulo siguiente e indice general. cap = (anterior, siguiente, total),
    cada vecino (archivo, nombre) o None."""
    ant, sig, total = cap[:3]
    if len(cap) > 3:
        palabra = cap[3]
    art = 'Las' if palabra[1].endswith(('ones', 'as')) else 'Los'
    filas = ['        <a class="herr-min ant" href="%s"><span>← %s anterior</span><small>%s</small></a>' % (ant[0], palabra[0], ant[1]) if ant else '',
             '        <a class="herr-min" href="%s"><span>%s %d %s</span><small>%s</small></a>' % (padre[0], art, total, palabra[1], padre[1]),
             '        <a class="herr-min sig" href="%s"><span>%s siguiente →</span><small>%s</small></a>' % (sig[0], palabra[0], sig[1]) if sig else '',
             '        <a class="herr-min" href="indice.html"><span>Índice</span><small>Todo Auditavisión</small></a>']
    return ('<nav class="herr-nav-min" aria-label="Moverte entre %s">\n%s\n      </nav>'
            % (palabra[1], '\n'.join(f for f in filas if f)))


def nav_de_pagina(archivo, padre3=None, cap=None):
    """La fila compacta que le toca a una pagina, o None si no es una
    aplicacion de las cuatro herramientas (ni subpagina de una, ni el bot
    del Modo Inspector)."""
    if mo_capitulos.numero(archivo):
        return nav_capitulos((mo_capitulos.PORTAL, mo_capitulos.TITULO), mo_capitulos.vecinos(archivo), ('Aplicación', 'aplicaciones'))
    apps = {}
    for h in HERRAMIENTAS:
        for i, t in enumerate(h[7]):
            apps[modulo_archivo(h[0], t[0])] = (h, i)
    if archivo in apps:
        return nav_compacta(*apps[archivo])
    if padre3 and cap:
        return nav_capitulos(padre3, cap)
    if padre3 and padre3[0] in apps:
        return nav_compacta(*apps[padre3[0]], padre=padre3)
    if archivo == ASISTENTE[0]:
        # El chat es la portada del Auditor Virtual (24-10-2026): ya no es una
        # «división» del Modo Inspector; desde aquí se va a las herramientas,
        # al Modo Inspector (las Grandes investigaciones) y a la Enciclopedia.
        return ('<nav class="herr-nav-min" aria-label="Moverte desde aquí">\n'
                '        <a class="herr-min" href="herramientas.html"><span>🧰 Herramientas</span><small>Las cuatro, en una página</small></a>\n'
                '        <a class="herr-min" href="%s"><span>🔍 Modo Inspector</span><small>Grandes investigaciones en seis aplicaciones</small></a>\n'
                '        <a class="herr-min" href="%s"><span>📚 Enciclopedia</span><small>Números, Datos y Aprende</small></a>\n'
                '      </nav>' % (MODO_INSPECTOR, ENCICLOPEDIA))
    return None


def herramienta_asistente(bloque):
    """Pagina del bot interno del Modo Inspector (11-10-2026): no es una de
    las seis aplicaciones, es la segunda division de la herramienta."""
    h = next(x for x in HERRAMIENTAS if x[1] == 'inspector')
    archivo, rubro, icono, titulo = h[:4]
    nav = ('<nav class="herr-mod-nav" aria-label="Más del Modo Inspector">\n'
           '        <div class="herr-mod-pasos">\n'
           '          <a class="herr-mod-paso ant" href="%s"><small>← Volver al índice de</small><b>%s %s</b></a>\n'
           '          <a class="herr-mod-paso sig" href="%s"><small>La otra división</small><b>%s %s</b></a>\n'
           '        </div>\n      </nav>' % (archivo, icono, titulo, MODO_INSPECTOR, icono, HERR_DIVISION[rubro][0]))
    return {
        # Es la portada de la pestaña Auditor Virtual (23-10-2026): sin padres.
        # Título «Auditor Virtual» (pedido del autor, 24-10-2026); el chat de
        # adentro conserva su nombre, «Pregúntale al Auditor».
        'archivo': ASISTENTE[0], 'menu': 'Auditor Virtual', 'menu_archivo': 'herramientas.html',
        'icono': '💬', 'titulo': 'Auditor Virtual',
        'lema': 'Pregúntale al Auditor · el chat de Auditavisión', 'sin_icono_lema': True, 'icono_cab': '💬',
        'entrada': '<b>%s.</b> %s' % (ASISTENTE[2], ASISTENTE[3]),
        'fondo': FOTO_AUDITOR, 'rubro': rubro, 'foto_clase': 'foto-auditor',
        'secciones': [{'id': 'chat', 'titulo': ASISTENTE[1], 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': bloque}],
        'estilos': ['asistente.css'], 'scripts': ['municipios-efipem.js', 'asistente-base.js', 'verificador.js', 'asistente-charla.js', 'asistente.js'],
        'pie_extra': nav + '\n\n      ' + herr_otras(archivo),
    }


def herramienta_dictamen(bloque):
    """Pagina del dictamen de una respuesta del bot (pedido del autor,
    23-10-2026): la abre «Generar dictamen» con la pregunta en la direccion."""
    h = next(x for x in HERRAMIENTAS if x[1] == 'inspector')
    import asistente
    return {
        'archivo': asistente.DICTAMEN, 'menu': 'Dictamen pericial', 'menu_archivo': 'herramientas.html',
        'padre': (AUDITOR_VIRTUAL, 'Auditor Virtual'),
        'icono': '🧾', 'titulo': 'Dictamen pericial de Auditavisión',
        'lema': '%s · el respaldo de una respuesta' % ASISTENTE[1], 'sin_icono_lema': True, 'icono_cab': LOGO_IMG,
        'entrada': ('<b>El respaldo de una respuesta del Auditor.</b> Tu pregunta, lo que se contestó, cada cifra con su estado, '
                    'sus fuentes oficiales y el método, con folio, sello y huella digital. Se arma de nuevo con los datos de la plataforma cada vez que se abre el enlace.'),
        'fondo': FOTO_AUDITOR, 'rubro': h[1], 'foto_clase': 'foto-auditor',
        'secciones': [{'id': 'dictamen', 'titulo': 'Dictamen pericial de Auditavisión', 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': bloque}],
        'estilos': ['asistente.css'], 'scripts': ['municipios-efipem.js', 'asistente-base.js', 'verificador.js', 'asistente-charla.js', 'asistente.js'],
    }


def poderes_paginas(base):
    """Los Poderes Legislativo y Judicial en la pestaña Datos (pedido del
    autor, 23-10-2026: «que esa pestaña este replicada en Datos, asi como la
    del Poder Legislativo, y que cada subpestaña se quede en su propia
    pagina»). Cada Poder tiene su portada con tarjetas y una pagina por grupo
    de temas: el mismo texto con que contesta el bot, sus tablas y sus
    fuentes. Todo sale de asistente_legislativo.py y asistente_judicial.py."""
    import asistente_legislativo as al
    import asistente_judicial as aj
    paginas = []
    poderes = [
        (al, '🏛️', 'Curules, escaños, sesiones, el calendario del presupuesto y las elecciones de 2027',
         'Cuántas personas legisladoras hay, cómo se eligen, cuándo sesionan, qué se vota el 6 de junio de 2027 y qué cambió con las reformas recientes. '
         'Cotejado con la Constitución vigente, la LGIPE, los acuerdos del INE publicados en el Diario Oficial y el censo del INEGI. Cada tarjeta abre su propia página.',
         lambda temas: al.secciones(base['estados'], temas), 'leg-'),
        (aj, '⚖️', 'Quién juzga, cuánto cuesta, cuánto ganan y cómo decide',
         'La estructura del Poder Judicial de la Federación tras la reforma de 2024, la Suprema Corte electa en 2025, el tabulador de sueldos, '
         'el presupuesto 2026, la elección judicial y cómo decide un juez. Cotejado con la Constitución vigente, los acuerdos del INE, el Manual de '
         'remuneraciones y el Presupuesto de Egresos. Cada tarjeta abre su propia página.',
         lambda temas: aj.secciones(base, temas), 'jud-'),
    ]
    for mod, ico, lema, entrada, secc, pre in poderes:
        partes = [(x[0], x[0], x[1], x[2]) for x in mod.PAGINAS]
        paginas.append({
            'archivo': mod.PORTADA, 'menu': mod.PORTADA_TIT, 'menu_archivo': 'descarga-los-datos.html',
            'padre': ('descarga-los-datos.html', 'Datos'),
            'icono': ico, 'titulo': mod.PORTADA_TIT, 'lema': lema,
            'entrada': entrada + ' Es la misma información con que contesta <a href="%s">Pregúntale al Auditor</a>.' % ASISTENTE[0],
            # Las anclas de cada tema llevan a su pagina.
            'hash_a_pagina': {pre + k: p[0] + '#' + pre + k for p in mod.PAGINAS for k in p[5]},
            'secciones': [{'id': 'partes', 'titulo': mod.PORTADA_TIT, 'texto': '', 'sin_cab': True,
                           'tarjetas': [(x[1], x[2], x[3], x[0], None, None) for x in mod.PAGINAS]}],
        })
        for archivo, pico, titulo, frase, pentrada, temas in mod.PAGINAS:
            paginas.append({
                'archivo': archivo, 'menu': titulo, 'menu_archivo': 'descarga-los-datos.html',
                'padre': ('descarga-los-datos.html', 'Datos'), 'padre2': (mod.PORTADA, mod.PORTADA_TIT),
                'icono': pico, 'titulo': titulo, 'lema': frase, 'entrada': pentrada,
                'estilos': ['asistente.css'],
                'pie_extra': partes_nav(mod.PORTADA_TIT, mod.PORTADA, ico, partes, archivo),
                'secciones': secc(temas),
            })
    return paginas


# Diccionario del Gasto Publico (decision del autor, 09-10-2026; el 11-10-2026
# se llamo «Diccionario del Erario Publico» y despues «Biblioteca del Erario
# Publico», pedidos del autor): los
# enlaces que llevaban a la Enciclopedia (congelada) llegan aqui. Desde el
# 09-10-2026 (tarde) cada apartado tiene su pagina ligera; ya no abre la
# portada en un marco. Las anclas viejas (#glosario, #fuentes, #marco-legal,
# #preguntas) mandan a la pagina nueva (ver 'hash_a_pagina').
# Noticias relevantes (pedido del autor, 11-10-2026): la pestana de Aprende
# abre esta pagina. Columnas editoriales que reunen, verificado contra
# documentos oficiales, lo que fueron las secciones 5.2 y 5.3 de la
# Enciclopedia (personajes relevantes y datos curiosos), retiradas el
# 27-09-2026 por no citar fuentes. Las pinta assets/auditor/js/columnas.js,
# en formato de periodico: «La Columna del Erario».
NOTICIAS = {
    'archivo': 'noticias-relevantes.html',
    'menu': 'Noticias relevantes',
    'menu_archivo': 'aprende.html',
    'padre': ('aprende.html', 'Aprende'),
    'icono': '📰',
    'titulo': 'Noticias relevantes',
    'lema': 'La Columna del Erario',
    'entrada': ('Columnas con datos curiosos de personajes y hechos del dinero público, en formato de periódico. '
                'Cada afirmación lleva el documento oficial que la sostiene.'),
    'scripts': ['columnas.js'],
    'estilos': ['columnas.css'],
    'secciones': [{
        'id': 'columnas', 'titulo': 'La Columna del Erario', 'texto': '', 'sin_cab': True, 'tarjetas': [],
        'bloque': ('<div class="col-diario" id="columnasDiario">\n'
                   '          <noscript><p>Las columnas necesitan JavaScript.</p></noscript>\n'
                   '        </div>'),
    }],
}


DICCIONARIO = {
    'archivo': 'diccionario.html',
    'menu': BIB_NOMBRE,
    'menu_archivo': 'aprende.html',
    'padre': ('aprende.html', 'Aprende'),
    'icono': '📚',
    'titulo': BIB_NOMBRE,
    'lema': 'Las palabras, las referencias, las leyes y las preguntas del erario',
    'entrada': ('La obra de consulta de la plataforma, en cuatro apartados: el <b>Diccionario</b> con los términos hacendarios, '
                'las <b>Referencias</b> con cada documento oficial que sostiene una cifra, el <b>Marco Legal Hacendario</b> con su '
                'texto vigente y las <b>Preguntas Frecuentes</b> en casillas didácticas. Cada tarjeta abre su propia página.'),
    'hash_a_pagina': {'preguntas': 'preguntas-frecuentes.html', 'glosario': 'glosario.html',
                      'marco-legal': 'marco-legal.html', 'fuentes': 'fuentes-oficiales.html',
                      'referencias': 'fuentes-oficiales.html', 'pase': 'donaciones.html'},
    'secciones': [{
        'id': 'apartados', 'titulo': 'Los cuatro apartados',
        'texto': 'Elige uno: cada tarjeta abre su página.',
        'tarjetas': tarjetas_biblioteca(),
    }],
}





def simulador():
    """Reparte el presupuesto, desde cero (propuesta de Astra, punto 6;
    entrega 4, 10-10-2026). Lo pinta assets/auditor/js/simulador-cero.js; el
    ejemplo oficial sale de investigaciones/simulador/cgpe2027-cuadro-ii6.json,
    que escribe herramientas/extraer_simulador.py desde el PDF."""
    ej = json.load(open(os.path.join(RAIZ, 'investigaciones', 'simulador', 'cgpe2027-cuadro-ii6.json'), encoding='utf-8'))
    datos = json.dumps(ej, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return {
        'archivo': 'simulador-presupuesto.html', 'menu': 'Reparte el presupuesto', 'menu_archivo': 'herramientas.html',
        'padre': (AUDITOR_VIRTUAL, 'Auditor Virtual'),
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
# 10-10-2026). Los Servicios son trabajo a la medida que se cotiza; el Pase
# del Auditor que convivia con ellos se retiro el 24-10-2026 (decision del
# autor). La pagina queda lista para el lanzamiento: el
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
     'Ningún dato publicado en la plataforma se esconde detrás de un pago. Los Servicios, las licencias y las donaciones sostienen el trabajo; no compran acceso a la información pública.'),
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
     'Cada año publicaremos cuántos encargos recibimos, por tipo de cliente (incluidos los gobiernos), y cuánto entró por cada vía: Servicios, licencias y donaciones. Si el gobierno falla en transparentar, nosotros ponemos el ejemplo.'),
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
        'archivo': 'servicios.html', 'menu': 'Servicios de investigación', 'menu_archivo': 'herramientas.html',
        # Desde el 11-10-2026 es un modulo del Modo Inspector (pedido del autor).
        'padre': (AUDITOR_VIRTUAL, 'Auditor Virtual'),
        'padre2': ('herramienta-inspector.html', 'Modo Inspector'),
        'icono': '🔎', 'titulo': 'Servicios de investigación', 'lema': 'La consulta es gratuita; la investigación a la medida se cotiza',
        'entrada': ('Todo lo que publica Auditavisión es libre y lo seguirá siendo. Cuando necesites ir más a fondo en un caso, '
                    'podemos hacer por encargo una investigación documental con la misma regla de la plataforma: cada cifra con '
                    'su documento y su etiqueta. Los Servicios son trabajo a la medida y, cuando se abran, las '
                    '<a href="donaciones.html">donaciones</a> también ayudan. Ninguna de las dos vías compra lo que publicamos.'),
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
            # Hasta el 24-10-2026 aqui iba el Pase del Auditor Civico.
            {'id': 'pase', 'titulo': 'Donaciones', 'texto': 'Si lo que quieres es sostener la consulta gratuita, puedes donar. Se abre con el lanzamiento.',
             'tarjetas': [('🐷', 'Donaciones', 'Ayuda a sostener la plataforma, a la vista de todos.', 'donaciones.html', None, None)]},
        ],
        'pie_extra': herr_otras('herramienta-inspector.html'),
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
    ('24-10-2026', 'Referencias y Gasto público',
     'La ficha [11] del Presupuesto de Egresos 2026 y la página «¿Quién lo aprueba?» decían que se publicó en el DOF el 28 de noviembre de 2025.',
     'Se publicó el 21 de noviembre de 2025: así lo dice el propio documento de la Cámara de Diputados. Se corrigieron las dos.',
     'fuentes-oficiales.html#ref-pef2026'),
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


def erratas_html():
    """La lista de la fe de erratas (comunidad-erratas.html y el cajon)."""
    lista = '\n'.join(
        '            <li class="cm-errata"><span class="cm-errata-fecha">%s</span><b>%s</b>'
        '<span><span class="cm-errata-et">Estaba mal:</span> %s</span><span><span class="cm-errata-et">Qué hicimos:</span> %s</span>%s</li>'
        % (e[0], e[1], e[2], e[3], (' <a href="%s">Ver la página ➔</a>' % e[4]) if e[4] else '') for e in ERRATAS)
    return '<ol class="cm-erratas">\n%s\n          </ol>' % lista


def compartir_html():
    """El bloque para compartir el Estado de Cuenta (pagina y cajon)."""
    return ('<div class="cm-compartir" data-url="%sestado-de-cuenta.html" '
            'data-texto="El contexto dimensional de las cuentas de México: de dónde sale el dinero público y en qué se gasta, con fuentes oficiales.">\n'
            '          <p>El <a href="estado-de-cuenta.html">Contexto dimensional</a> resume 2024, 2026 y 2027 en cuatro dimensiones, '
            'cada cifra con su fuente. Compártelo: entre más gente lo lea, más difícil es que el dinero público pase sin que nadie lo vea.</p>\n'
            '          <div class="sv-acciones cm-redes"></div>\n'
            '          <p class="cm-nota">Si sacaste tu cuenta personal en la <a href="herramienta-calculadora-ticket.html">Calculadora Cívica</a>, '
            'compartimos solo el enlace: tu ingreso nunca sale de tu navegador.</p>\n'
            '          <noscript><p>Para compartir, copia esta dirección: %sestado-de-cuenta.html</p></noscript>\n'
            '        </div>') % (SITIO, SITIO)


# Las cinco rutas de «Cuéntanos lo que viste» (id, icono, titulo, para que).
RUTAS = [
    ('reporta', '🏗️', 'Algo raro con el dinero público',
     'Una obra que no cuadra, un contrato o una compra sospechosa, un programa social usado en campaña, un cobro indebido.'),
    ('error', '✏️', 'Un dato mal en esta plataforma',
     'Una cifra que no coincide con su documento oficial. Si tienes razón, se corrige y entra a la fe de erratas.'),
    ('tema', '💡', 'Un tema que deberíamos investigar',
     'Lo que te gustaría que revisáramos, con los documentos que conozcas.'),
    # Compartir y la fe de erratas entraron al cajon el 24-10-2026 (pedido del
    # autor): las cinco partes de comunidad.html se abren desde la cabecera.
    ('compartir', '📣', 'Comparte el Estado de Cuenta',
     'Un enlace para que más gente vea de dónde sale el dinero público y en qué se gasta.'),
    ('erratas', '📋', 'Fe de erratas',
     'Cada corrección que hemos hecho: qué estaba mal y qué cambió.'),
]
DENUNCIA = ('Esto ordena tu reporte, pero <b>no es una denuncia</b>. La única vía con efecto jurídico es un canal oficial: '
            '<a href="garantias-brujula.html">la brújula de las seis puertas</a> te dice cuál toca, si admite anonimato '
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
        <p class="pt-sub">Elige una de las cinco rutas. Nada se envía ni se guarda por su cuenta: el texto se arma en tu navegador y tú decides si lo copias, lo descargas o nos lo mandas.</p>
      </div>
      <button type="button" class="pt-cerrar" data-pt-cerrar aria-label="Cerrar">✕</button>
    </div>
    <div class="pt-cuerpo">
{rutas}
      <p class="pt-pie">Todo esto vive también en su página: <a href="comunidad.html">Cuéntanos lo que viste</a> · <a href="garantias.html">Garantías cívicas: a qué puerta tocar</a></p>
    </div>
  </aside>'''


def puerta():
    """«Cuéntanos lo que viste»: la unica puerta para escribirnos (fusion del
    10-10-2026 con «¿Viste un error?», que estaba al pie). El boton de la
    cabecera abre este cajon en cada pagina; sin JavaScript lleva a
    comunidad.html. Lo abre y lo cierra comunidad.js. index.html recibe la
    misma copia entre marcas (poner_puerta)."""
    f = formas('pt')
    f['compartir'] = compartir_html()
    f['erratas'] = erratas_html()
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
        'padre': ('participa.html', 'Comunidad'),
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


# Comunidad, en cinco paginas (pedido del autor, 11-10-2026): comunidad.html
# queda como portada con cinco tarjetas y cada una abre la suya. Las anclas
# viejas (comunidad.html#reporta...) llevan a su pagina. Los formularios los
# sigue armando comunidad.js, que se carga en todas las paginas.
# (id, archivo, icono, titulo, frase de la tarjeta, texto de la pagina)
COMUNIDAD_PARTES = [
    ('reporta', 'comunidad-reporta.html', '🏗️', 'Algo raro con el dinero público',
     'Una obra que no cuadra, un contrato, un programa usado en campaña, un cobro indebido.',
     RUTAS[0][3] + ' Dinos qué, dónde y cuándo.'),
    ('error', 'comunidad-error.html', '✏️', 'Un dato mal en esta plataforma',
     'Un dato que no coincide con su documento oficial. Si tienes razón, se corrige en público.',
     'Si un dato no coincide con su documento oficial, dínoslo. Si tienes razón, se corrige y entra a la fe de erratas.'),
    ('tema', 'comunidad-tema.html', '💡', 'Un tema que deberíamos investigar',
     'Lo que te gustaría que investigáramos, con los documentos que conozcas.',
     'Lo que te gustaría que investigáramos. No compromete a nadie: lo revisamos y, si hay documentos, entra a la lista.'),
    ('compartir', 'comunidad-compartir.html', '📣', 'Comparte el Estado de Cuenta',
     'Un enlace para que más gente vea de dónde sale el dinero público y en qué se gasta.',
     'Un enlace basta.'),
    ('erratas', 'comunidad-erratas.html', '📋', 'Fe de erratas',
     'Cada corrección que hemos hecho: qué estaba mal y qué cambió.',
     'Las correcciones que hemos hecho, de la más reciente a la más antigua.'),
]
COMUNIDAD_ARCHIVO = dict((c[0], c[1]) for c in COMUNIDAD_PARTES)
AVISO_ENVIO = ('      <p class="sv-aviso"><span class="sz-et">Próximamente</span> El envío se activa '
               'con el lanzamiento. Ya puedes armar tu texto, copiarlo o descargarlo.</p>')


def partes_nav(nombre, portada, icono, partes, actual):
    """Barra al pie de una pagina partida: su portada y sus partes
    (cada parte es una tupla (id, archivo, icono, titulo, ...))."""
    return ('<nav class="bib-nav" aria-label="%s">\n'
            '        <a class="bib-nav-tit" href="%s">%s %s</a>\n'
            '        <div class="bib-nav-fila">\n%s\n        </div>\n      </nav>' % (nombre, portada, icono, nombre, '\n'.join(
                '          <a class="bib-nav-a" href="%s"%s><span aria-hidden="true">%s</span><span>%s</span></a>'
                % (c[1], ' aria-current="page"' if c[1] == actual else '', c[2], c[3]) for c in partes)))


def comunidad_nav(actual):
    """Barra al pie de cada pagina de Comunidad, con sus cinco partes."""
    return partes_nav('Cuéntanos lo que viste', 'comunidad.html', '📢', COMUNIDAD_PARTES, actual)


def comunidad():
    """La portada de Comunidad y sus cinco paginas: [portada, parte, ...]."""
    f = formas('cm')
    bloques = {
        'reporta': f['reporta'] + '\n        <p class="pt-nota">%s</p>' % DENUNCIA,
        'error': f['error'],
        'tema': f['tema'],
        'compartir': compartir_html(),
        'erratas': '<div class="sv-politica">\n          %s\n        </div>' % erratas_html(),
    }
    portada = {
        # Cuelga del boton de la cabecera, no de una pestana (24-10-2026).
        'archivo': 'comunidad.html', 'menu': 'Cuéntanos lo que viste', 'menu_archivo': 'comunidad.html',
        'icono': '📢', 'titulo': 'Cuéntanos lo que viste', 'lema': 'Participa: reporta, corrige y comparte',
        'entrada': ('La plataforma mejora con quien la lee. Repórtanos algo raro con el dinero público, señala un dato que esté mal '
                    '(con su documento) o propón un tema para investigar: son las tres rutas del botón «📢 Cuéntanos lo que viste» '
                    'de la cabecera. Aquí están también el botón para compartir y la fe de erratas. Cada tarjeta abre su propia página.'),
        'hash_a_pagina': COMUNIDAD_ARCHIVO,
        'secciones': [{'id': 'partes', 'titulo': 'Las cinco puertas para participar', 'texto': '', 'sin_cab': True,
                       'tarjetas': [(c[2], c[3], c[4], c[1], None, None) for c in COMUNIDAD_PARTES]}],
    }
    partes = []
    for id_, archivo, ico, tit, frase, texto in COMUNIDAD_PARTES:
        partes.append({
            'archivo': archivo, 'menu': tit, 'menu_archivo': 'comunidad.html',
            'padre': ('comunidad.html', 'Cuéntanos lo que viste'),
            'icono': ico, 'titulo': tit, 'lema': 'Cuéntanos lo que viste', 'entrada': texto,
            'estilos': ['servicios.css'],
            'antes': AVISO_ENVIO if id_ in ('reporta', 'error', 'tema') else '',
            'pie_extra': comunidad_nav(archivo),
            'secciones': [{'id': id_, 'titulo': tit, 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': bloques[id_]}],
        })
    return [portada] + partes

# Donaciones (pedido del autor, 11-10-2026): una pagina para recibir
# donativos que sostengan la plataforma, con una alcancia que se llena a la
# vista de todos. Regla de la casa: la alcancia solo muestra dinero que de
# verdad entro. Mientras CANAL_DONACION este vacio no se recibe nada y la
# alcancia marca $0. Para anotar un movimiento real se agrega aqui y se
# regenera: la cifra sale de estas listas, nunca se teclea en la pagina.
CANAL_DONACION = ''      # direccion de la pasarela de pago, cuando exista
DONACIONES_CORTE = '11-10-2026'
# Meta: (monto en pesos, que cubre). None hasta que el autor publique
# cuanto cuesta sostener la plataforma; sin meta la alcancia no se inventa una.
DONACIONES_META = None
# Entradas recibidas: (fecha, monto en pesos, nota sin datos personales).
DONACIONES_ENTRADAS = []
# Salidas pagadas con donativos: (fecha, monto, concepto, enlace al comprobante).
DONACIONES_SALIDAS = []

DN_CERDITO = '''<svg class="dn-svg" viewBox="0 0 320 250" role="img" aria-labelledby="dnSvgTit">
              <title id="dnSvgTit">Alcancía en forma de cochinito. Su nivel muestra lo recaudado: {nivel}.</title>
              <defs>
                <clipPath id="dnCuerpo"><ellipse cx="160" cy="148" rx="112" ry="78"/></clipPath>
              </defs>
              <ellipse class="dn-sombra" cx="160" cy="236" rx="96" ry="9"/>
              <rect class="dn-pata" x="92" y="196" width="26" height="38" rx="9"/>
              <rect class="dn-pata" x="200" y="196" width="26" height="38" rx="9"/>
              <path class="dn-cola" d="M50 138 q-24 -4 -20 -22 q4 -14 16 -6"/>
              <ellipse class="dn-cuerpo" cx="160" cy="148" rx="112" ry="78"/>
              <g clip-path="url(#dnCuerpo)">
                <g class="dn-nivel" id="dnNivel" style="transform: translateY(160px)">
                  <path class="dn-ola" d="M-40 70 q20 -10 40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 V260 H-40 Z"/>
                </g>
              </g>
              <ellipse class="dn-brillo" cx="118" cy="110" rx="34" ry="13"/>
              <path class="dn-oreja" d="M204 84 l22 -36 l16 40 z"/>
              <ellipse class="dn-hocico" cx="268" cy="152" rx="22" ry="27"/>
              <ellipse class="dn-nariz" cx="262" cy="148" rx="4" ry="6"/><ellipse class="dn-nariz" cx="275" cy="148" rx="4" ry="6"/>
              <circle class="dn-ojo" cx="232" cy="120" r="7"/>
              <g class="dn-monedas" aria-hidden="true">
                <g class="dn-moneda dn-m1"><circle cx="160" cy="-20" r="13"/><text x="160" y="-15">$</text></g>
                <g class="dn-moneda dn-m2"><circle cx="160" cy="-20" r="13"/><text x="160" y="-15">$</text></g>
                <g class="dn-moneda dn-m3"><circle cx="160" cy="-20" r="13"/><text x="160" y="-15">$</text></g>
              </g>
              <rect class="dn-ranura" x="136" y="66" width="48" height="9" rx="4.5"/>
            </svg>'''


def _pesos(n):
    t = format(n, ',.2f')
    return '$' + (t[:-3] if t.endswith('.00') else t)


def donaciones():
    recaudado = sum(e[1] for e in DONACIONES_ENTRADAS)
    gastado = sum(g[1] for g in DONACIONES_SALIDAS)
    meta = DONACIONES_META[0] if DONACIONES_META else None
    datos = json.dumps({'recaudado': recaudado, 'meta': meta, 'n': len(DONACIONES_ENTRADAS)})

    if DONACIONES_META:
        meta_txt = '<b>%s MXN</b><small>%s</small>' % (_pesos(meta), DONACIONES_META[1])
    else:
        meta_txt = ('<b>Por definir</b><small>La fijaremos cuando publiquemos cuánto cuesta sostener la plataforma, '
                    'para que sepas qué se paga con tu donativo.</small>')
    alcancia = '''<script type="application/json" id="dnDatos">{datos}</script>
        <div class="dn-alcancia">
          <div class="dn-figura">
            {cerdito}
            <button type="button" class="sz-btn dn-prueba" id="dnPrueba">🪙 Echa una moneda de prueba</button>
            <p class="dn-prueba-nota" id="dnPruebaNota" aria-live="polite">Es solo la animación: no es un donativo y no suma a la cuenta.</p>
          </div>
          <dl class="dn-cifras">
            <div class="dn-cifra dn-cifra-grande"><dt>Recaudado</dt><dd><b id="dnRecaudado">{rec} MXN</b><small>{n} · corte al {corte}</small></dd></div>
            <div class="dn-cifra"><dt>Meta</dt><dd>{meta}</dd></div>
            <div class="dn-cifra"><dt>Avance</dt><dd><b id="dnAvance">{avance}</b><small>{avance_nota}</small></dd></div>
          </dl>
        </div>'''.format(
        datos=datos, cerdito=DN_CERDITO.format(nivel=_pesos(recaudado) + ' MXN'), rec=_pesos(recaudado),
        corte=DONACIONES_CORTE, meta=meta_txt,
        n=('%d donativos' % len(DONACIONES_ENTRADAS)) if DONACIONES_ENTRADAS else 'Todavía ningún donativo: el canal aún no se abre',
        avance=('%.0f %%' % (recaudado * 100.0 / meta)) if meta else '—',
        avance_nota='Lo recaudado entre la meta, por cien.' if meta else 'Se calcula cuando haya meta.')

    def tabla(cab, filas, vacio):
        if filas:
            cuerpo = '\n'.join('              <tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in f) for f in filas)
        else:
            cuerpo = '              <tr><td colspan="%d" class="dn-vacio">%s</td></tr>' % (len(cab), vacio)
        return ('<div class="dn-tabla-caja"><table class="dn-tabla">\n            <thead><tr>%s</tr></thead>\n'
                '            <tbody>\n%s\n            </tbody>\n          </table></div>'
                % (''.join('<th scope="col">%s</th>' % c for c in cab), cuerpo))
    entradas = tabla(('Fecha', 'Monto', 'Nota'), [(e[0], _pesos(e[1]), e[2]) for e in DONACIONES_ENTRADAS],
                     'Aún no hay entradas: el canal de donativos todavía no se abre.')
    salidas = tabla(('Fecha', 'Monto', 'En qué se gastó', 'Comprobante'),
                    [(g[0], _pesos(g[1]), g[2],
                      '<a href="%s" target="_blank" rel="noopener noreferrer">Ver ↗</a>' % g[3] if g[3] else '—')
                     for g in DONACIONES_SALIDAS],
                    'Aún no hay salidas: no se ha gastado ningún donativo.')
    cuentas = '''<div class="dn-cuentas">
          <div class="dn-saldo"><span>Entró <b>{rec}</b></span><span>Salió <b>{gas}</b></span><span>Queda <b>{saldo}</b></span></div>
          <h3 class="dn-sub">⬇️ Lo que entró</h3>
          {entradas}
          <h3 class="dn-sub">⬆️ En qué se gastó</h3>
          {salidas}
          <p class="dn-nota">Nunca publicamos quién donó: solo la fecha y el monto. Cada gasto lleva su comprobante.</p>
        </div>'''.format(rec=_pesos(recaudado), gas=_pesos(gastado), saldo=_pesos(recaudado - gastado),
                         entradas=entradas, salidas=salidas)

    # Tres compromisos de la politica de independencia, citados de INDEPENDENCIA.
    pol = dict(INDEPENDENCIA)
    reglas_items = [
        ('🔓', 'La consulta cívica es gratuita y lo seguirá siendo.'),
        ('🚫', 'Las donaciones no compran contenido.'),
        ('🧾', 'Rendimos cuentas de cómo nos sostenemos.'),
    ]
    reglas = '''<ul class="dn-reglas">
{items}
          <li><span class="dn-regla-ico" aria-hidden="true">🏛️</span><div><b>Tu donativo no es deducible de impuestos.</b> Auditavisión no es
            donataria autorizada por el SAT, y la Ley del Impuesto sobre la Renta solo deja deducir los donativos hechos a donatarias
            autorizadas (<a href="https://www.diputados.gob.mx/LeyesBiblio/pdf/LISR.pdf" target="_blank" rel="noopener noreferrer">artículo 151, fracción III ↗</a>).
            Donas como apoyo cívico, sin beneficio fiscal.</div></li>
        </ul>
        <p class="dn-nota">Estas reglas vienen de la <a href="servicios.html#independencia">política de independencia</a> de la plataforma, que vale igual para cada donante.
          ¿Necesitas una investigación a la medida? Esa es la otra vía para sostener la plataforma: los <a href="servicios.html">Servicios de investigación</a>.</p>'''.format(
        items='\n'.join('          <li><span class="dn-regla-ico" aria-hidden="true">%s</span><div><b>%s</b> %s</div></li>' % (i, t, pol[t])
                        for i, t in reglas_items))

    if CANAL_DONACION:
        boton = '<a class="sz-btn sz-btn-of dn-donar" href="%s" target="_blank" rel="noopener noreferrer">🐷 Donar ahora ↗</a>' % CANAL_DONACION
        aviso = ''
    else:
        boton = '<button type="button" class="sz-btn sz-btn-of dn-donar" disabled>🐷 Donar · se abre con el lanzamiento</button>'
        aviso = ('      <p class="sv-aviso"><span class="sz-et">Próximamente</span> El canal para donar se abre con el lanzamiento '
                 'de la plataforma. Mientras tanto la alcancía está en $0: aquí solo se muestra dinero que de verdad entró.</p>')

    return {
        'archivo': 'donaciones.html', 'menu': 'Donaciones', 'menu_archivo': 'participa.html',
        'padre': ('participa.html', 'Comunidad'),
        'icono': '🐷', 'titulo': 'Donaciones', 'lema': 'Exigimos transparencia, y empezamos por casa',
        'entrada': ('Auditavisión no tiene publicidad y su consulta es gratuita. Si quieres ayudar a sostenerla, puedes donar lo que quieras. '
                    'Te ofrecemos lo mismo que le pedimos al gobierno: <b>cuentas claras</b>. Cada peso que entre se ve en la alcancía, '
                    'y cada peso que salga se anota con su comprobante.'),
        'estilos': ['servicios.css', 'donaciones.css'],
        'scripts': ['donaciones.js'],
        'antes': aviso,
        'secciones': [
            {'id': 'alcancia', 'titulo': '🐷 La alcancía de la transparencia',
             'texto': 'Se llena con cada donativo que llegue, a la vista de todos. Solo cuenta dinero que de verdad entró.',
             'tarjetas': [], 'bloque': alcancia + '\n        <p class="dn-accion">%s</p>' % boton},
            {'id': 'cuentas', 'titulo': '📒 Cuentas claras',
             'texto': 'Lo que entra y lo que sale, con fecha y monto. Si exigimos que el gobierno transparente su gasto, nosotros también.',
             'tarjetas': [], 'bloque': cuentas},
            {'id': 'reglas', 'titulo': '🤝 Las reglas de tu donativo',
             'texto': 'Lo que tu donativo sí hace y lo que no.',
             'tarjetas': [], 'bloque': reglas},
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


# Garantias civicas, en cuatro paginas (pedido del autor, 11-10-2026), como
# Comunidad: garantias.html queda como portada con cuatro tarjetas y cada una
# abre la suya. Las anclas viejas (garantias.html#brujula...) llevan a su
# pagina. (id, archivo, icono, titulo, frase de la tarjeta, entrada)
GARANTIAS_PARTES = [
    ('brujula', 'garantias-brujula.html', '🧭', 'La brújula: ¿a qué puerta toco?',
     'Tres preguntas y te decimos qué canal oficial te toca, qué llevar y si puedes hacerlo sin dar tu nombre.',
     'Viste algo raro con el dinero público. Contesta tres preguntas (qué viste, si ya tienes con qué probarlo y si '
     'necesitas cuidar tu nombre) y la brújula te dice a cuál de las seis puertas oficiales tocar, qué llevar y qué pasa después.'),
    ('puertas', 'garantias-puertas.html', '🚪', 'Las seis puertas oficiales',
     'Quién investiga qué, si admite anonimato, qué llevar y qué produce tu denuncia.',
     'Cada puerta investiga cosas distintas. Una no es para denunciar sino para conseguir la prueba: la Plataforma '
     'Nacional de Transparencia. Abre «Qué llevar y qué pasa después» en cada una para ver el detalle y su fundamento legal.'),
    ('derechos', 'garantias-derechos.html', '🛡️', 'Tus diez garantías',
     'Lo que la ley te asegura cuando vigilas el dinero público, cada una con su norma.',
     'Lo que la ley te asegura cuando vigilas el dinero público. Toca cada carta para ver la explicación y la norma que la sostiene.'),
    ('reto', 'garantias-reto.html', '🎯', '¿Mito o realidad?',
     'Afirmaciones que se oyen seguido. Adivina y comprueba con la ley.',
     'Afirmaciones que se oyen seguido sobre denunciar y pedir información. Adivina si son mito o realidad y comprueba '
     'la respuesta con la ley que la sostiene.'),
]
GARANTIAS_ARCHIVO = dict((g[0], g[1]) for g in GARANTIAS_PARTES)
AVISO_GARANTIAS = ('      <p class="sv-aviso gr-aviso"><span class="sz-et">Importante</span> Auditavisión <b>no recibe denuncias</b>. '
                   '«📢 Cuéntanos lo que viste» te ayuda a redactar tu reporte y el <a href="agora.html">Ágora</a> es para debatir; '
                   'la denuncia con efecto jurídico (folio, plazos y obligación de responder) solo la abre una de las puertas oficiales.</p>')


def _anonimo_corto(t):
    """«Sí, y con protección...» -> «Sí»; «No del todo. La...» -> «No del todo»."""
    return re.split(r'[.,;:]', t, 1)[0].strip()


def garantias():
    """La portada de Garantias civicas y sus cuatro paginas: [portada, parte, ...]."""
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
              <a class="sz-btn" href="comunidad-reporta.html" data-puerta="reporta">📢 Ordena tu texto antes de presentarlo</a></p>
          </div>
          <noscript><p>La brújula necesita JavaScript. En <a href="garantias-puertas.html">las seis puertas oficiales</a> está todo lo que necesitas saber.</p></noscript>
        </div>'''.format(datos=datos, opciones=opciones)

    reto_html = '''<div class="gr-reto" id="grReto">
          <div class="gr-reto-cab"><span id="grRetoAvance">Pregunta 1 de {n}</span><span id="grRetoPuntos">Aciertos: 0</span></div>
          <div class="gr-reto-barra" aria-hidden="true"><span id="grRetoBarra"></span></div>
          <p class="gr-reto-af" id="grRetoAf">…</p>
          <div class="gr-reto-ops"><button type="button" class="gr-reto-btn" data-r="1">✅ Realidad</button><button type="button" class="gr-reto-btn" data-r="0">❌ Mito</button></div>
          <div class="gr-reto-exp" id="grRetoExp" hidden aria-live="polite"></div>
          <noscript><p>El reto necesita JavaScript. Las respuestas están en <a href="garantias-derechos.html">tus diez garantías</a>.</p></noscript>
        </div>'''.format(n=len(GARANTIAS_RETO))

    bloques = {
        'brujula': brujula,
        'puertas': '<div class="gr-puertas">\n%s\n        </div>' % puertas,
        'derechos': '<ol class="gr-cartas">\n%s\n        </ol>' % cartas,
        # El reto lee sus afirmaciones del mismo JSON que la brujula.
        'reto': '<script type="application/json" id="grDatos">%s</script>\n        %s' % (datos, reto_html),
    }
    # Las fichas de cada puerta (garantias.html#puerta-ch-asf) tambien llevan a su pagina.
    anclas = dict(GARANTIAS_ARCHIVO)
    anclas.update(('puerta-' + c['id'], 'garantias-puertas.html#puerta-' + c['id']) for c in canales)
    portada = {
        'archivo': 'garantias.html', 'menu': 'Garantías cívicas', 'menu_archivo': 'participa.html',
        'padre': ('participa.html', 'Comunidad'),
        'icono': '🛡️', 'titulo': 'Garantías cívicas', 'lema': 'A qué puerta tocar y qué te protege',
        'entrada': ('Viste algo raro con el dinero público. Estas páginas responden tres preguntas: <b>a qué puerta oficial tocar</b>, '
                    '<b>qué derechos te protegen</b> y <b>qué llevar</b>. Empieza por la brújula: en tres clics te dice cuál de las '
                    '%d puertas te toca. Cada tarjeta abre su propia página.' % len(canales)),
        'estilos': ['servicios.css'],
        'antes': AVISO_GARANTIAS,
        'hash_a_pagina': anclas,
        'secciones': [{'id': 'partes', 'titulo': 'Las cuatro partes de Garantías cívicas', 'texto': '', 'sin_cab': True,
                       'tarjetas': [(g[2], g[3], g[4], g[1], None, None) for g in GARANTIAS_PARTES]}],
    }
    partes = []
    for id_, archivo, ico, tit, frase, texto in GARANTIAS_PARTES:
        partes.append({
            'archivo': archivo, 'menu': tit, 'menu_archivo': 'participa.html',
            'padre': ('participa.html', 'Comunidad'), 'padre2': ('garantias.html', 'Garantías cívicas'),
            'icono': ico, 'titulo': tit, 'lema': 'Garantías cívicas', 'entrada': texto,
            'estilos': ['servicios.css', 'garantias.css'],
            'scripts': ['garantias.js'],
            'antes': AVISO_GARANTIAS if id_ in ('brujula', 'puertas') else '',
            'pie_extra': partes_nav('Garantías cívicas', 'garantias.html', '🛡️', GARANTIAS_PARTES, archivo),
            'secciones': [{'id': id_, 'titulo': tit, 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': bloques[id_]}],
        })
    return [portada] + partes


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
# Desde el 12-10-2026 (pedido del autor) estas cifras viven en Numeros →
# Presupuesto → «Cuanto dinero es», junto a las de esa pagina: las dos
# repetian el total. presupuesto_modulos.cuanto() las arma; las dos primeras
# (total del PEF y gasto federalizado) no se repiten alla porque esa pagina
# ya las da con su desglose.
RADAR_HOY_CUENTA = '''<div class="rd-cuenta" id="rdCuenta" hidden>
          <button type="button" class="rd-cuenta-btn" id="rdContar" aria-pressed="false">▶ Contar</button>
          <span class="rd-cuenta-txt" id="rdCuentaTxt">Las cifras están en cero. Presiona «Contar» para verlas llegar a su valor oficial.</span>
        </div>'''
RADAR_HOY_FILAS = [
    _hoy('🏛️', '$10.19 billones', 'Presupuesto federal aprobado 2026', 'Presupuesto de Egresos de la Federación 2026, art. 1'),
    _hoy('🗺️', '$2.81 billones (27.6 %)', 'Gasto federalizado a los 32 estados', 'PEF 2026: estimación del gasto federalizado, $2,810,800 mdp; 27.6 % = ese monto ÷ $10,193,683.7 mdp del PEF', 'derivado'),
    _hoy('💰', '$5.42 billones', 'ISR, IVA e IEPS estimados en la Ley de Ingresos 2026', 'Ley de Ingresos de la Federación 2026, art. 1: ISR $3,070,149.1 + IVA $1,589,069.0 + IEPS $761,501.9 mdp', 'derivado'),
    _hoy('🤝', '$1.46 billones', 'Participaciones a estados y municipios (Ramo 28)', 'PEF 2026, Ramo General 28: $1,456,045.9 mdp'),
    _hoy('📉', '$1,572,073.3 mdp', 'Costo financiero de la deuda en 2026', 'PEF 2026, Anexo 8'),
    _hoy('🏦', '$643,695.7 mdp', 'Deuda de los 32 gobiernos estatales', 'SHCP, Sistema de Alertas, evaluación con la Cuenta Pública 2025 (29 de junio de 2026); suma de las 32 entidades', 'derivado'),
    _hoy('⚖️', '$65,169.1 mdp', 'Por aclarar ante la ASF, Cuenta Pública 2024 (no es daño comprobado)', 'ASF, Matriz de Datos Básicos de la Cuenta Pública 2024 (consolidado, feb. 2026), p. 11'),
    _hoy('⛽', 'sin cifra oficial', 'Huachicol fiscal: cuánto IEPS se deja de cobrar', '<a href="auditoria-huachicol-fiscal.html">Lo que se sabe y lo que falta ➔</a>', 'pendiente', 'huachicol-evasion'),
]
RADAR_HOY_VIVO = ('''<div class="rd-hoy-vivo" id="rdHoyVivo" role="status"><div class="rd-hoy-candado" id="rdCandado" hidden>🔒 Se desbloquea al presionar «Contar»</div><span>⏱️ Durante tu visita (<span id="rdHoyT">0:00</span>), al ritmo de 2026:</span>
          <span>intereses de la deuda <b data-tasa="49850.12">+$0.00</b></span>
          <span>pérdida neta de las megaobras <b data-tasa="{mo_tasa}">+$0.00</b></span>
          <small>Equivalencias: la cifra anual entre los 31,536,000 segundos del año ($1,572,073.3 mdp y {mo_anual}, este último la pérdida neta del año de las megaobras que publican su resultado,
          la misma de <a href="herramienta-megaobras-tabla.html">Inversión y Megaobras</a>, derivado). No son pagos que ocurran en este instante. <a href="auditoria-deuda-soberana.html">El reloj de los intereses ➔</a></small>
        </div>''')


def radar_hoy_vivo(base):
    """El contador de «Hoy» con la perdida neta de las megaobras: la medida
    unica de Inversion y Megaobras (mo_base.balance, 21-10-2026). Antes
    decia 65,050.8 mdp, un piso de la Cuenta Publica 2024."""
    import mo_base
    b = mo_base.balance(base['simulador_megaobras'])
    perd = -b['neto']
    return RADAR_HOY_VIVO.format(mo_tasa=repr(round(perd * 1e6 / 31536000, 2)), mo_anual='$' + format(perd, ',.1f') + ' mdp')


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
    # Desde el 12-10-2026 (pedido del autor) ya no hay tarjeta «Hoy y los
    # estados de cuenta»: el presupuesto en curso se fundio en Numeros →
    # «Cuanto dinero es», y el estado de cuenta fue la cuarta tarjeta de Datos
    # hasta el 22-10-2026, cuando paso a ser la quinta aplicacion de la Calculadora
    # (desde el 12-10-2026 el tablero ya no lleva sus botones). radar-hoy.html y
    # radar-presupuesto-en-curso.html redirigen (REDIRECCIONES).
    ('tablero', 'radar-tablero.html', '📡', 'El tablero', 'Cada administración, tarjeta por tarjeta, comparada con las demás'),
    ('peso', 'radar-peso.html', '💱', 'El peso en el tiempo', 'Inflación, dólar y euro desde 1988, con la proyección a 2032'),
    ('reloj', 'radar-reloj.html', '⏱️', 'El reloj de cada administración', 'El contador que corre al ritmo de cada sexenio'),
    ('duelo', 'radar-duelo.html', '⚔️', 'Duelo de administraciones', 'Dos administraciones, cara a cara'),
    # «Como leer estos numeros» dejo de ser tarjeta el 12-10-2026 (pedido del
    # autor): se abre en la ventana lateral desde el boton 📖 de la entrada
    # del radar ('cajon' de la pagina). radar-como-leer.html redirige ahi.
]


# «El peso en el tiempo», en tres tarjetas con su propia pagina (pedido del
# autor, 12-10-2026): (icono, pagina, titulo, descripcion, entrada, id).
RADAR_PESO_PARTES = [
    ('💱', 'radar-peso-monedas.html', 'El peso frente al dólar, el euro y la inflación',
     'Un simulador que recorre los sexenios año por año, desde cero.',
     'Cuánto vale hoy el peso y cómo ha cambiado desde 1988 frente al dólar, frente al euro y frente a los precios, '
     'con la proyección de Hacienda hasta 2032. Presiona «Recorrer los sexenios» y mira, año por año y presidente por '
     'presidente, cómo se mueve cada cifra; o elige un año, o toca a un presidente para ir a su sexenio.', 'monedas'),
    ('🧾', 'radar-peso-sexenios.html', 'El peso en cada sexenio',
     'Cuánto subieron los precios, el dólar y el euro con cada presidente.',
     'Cada administración, de lo que recibió a lo que entregó: cuánto subieron los precios, cuánto pasó a costar el dólar '
     'y cuánto el euro. Cada cifra trae su operación y su fuente.', 'sexenios'),
    ('🕰️', 'radar-peso-maquina.html', 'La máquina del tiempo del peso',
     'Lleva cualquier cantidad de un año a otro.',
     'Escribe una cantidad y elige un año: te decimos cuánto vale en pesos de hoy, en dólares y en euros de ese año, '
     'y cuánto haría falta para comprar lo mismo hasta 2032, según la proyección de Hacienda.', 'maquina'),
]


# La descripcion narrativa de cada tarjeta en la portada del Radar
# (pedido del autor, 12-10-2026): una frase corta, de unas dos lineas, sin cifras.
RADAR_NARRATIVA = {
    'tablero': 'Cada gobierno desde 1989, tarjeta por tarjeta, comparado con los demás.',
    'peso': 'Cuánto ha valido tu dinero frente al dólar y el euro.',
    'reloj': 'Mira correr, segundo a segundo, el dinero de cada sexenio.',
    'duelo': 'Dos gobiernos frente a frente; el juicio es tuyo.',
}

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
    """Barra al pie de cada pagina del Radar, con sus partes."""
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


def _rango_txt(a, b):
    return str(a) if a == b else '%d a %d' % (a, b)


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
        def en_euros(fe):
            return {'v': round(sum(m / prom(ps['eur'], y) for y, m in fe), 1), 'est': 'derivado',
                    'f': fts + [ps['eur']['f']],
                    'op': 'Cada año entre su tipo de cambio promedio (pesos por euro), en millones de euros; luego se suman. %s'
                          % ' · '.join('%d: %s ÷ %s' % (y, mdp(m), format(prom(ps['eur'], y), '.4f')) for y, m in fe)}
        if anios[0] >= ps['eur']['desde']:
            alt['eur'] = en_euros(filas)
        else:
            alt['eur'] = {'na': ps['eur']['antes'], 'et': 'sin euro'}
            # El reloj (pedido del autor, 12-10-2026) corre con los años del
            # sexenio que si tienen cotizacion del euro, si los hay.
            con = [(y, m) for y, m in filas if y >= ps['eur']['desde']]
            if con:
                par = en_euros(con)
                par['ys'] = [con[0][0], con[-1][0]]
                par['just'] = ('En euros, el reloj corre al ritmo de %s, %s del sexenio con cotización del euro en Banxico. %s'
                               % (_rango_txt(con[0][0], con[-1][0]), 'el único año' if len(con) == 1 else 'los años',
                                  ps['eur']['antes']))
                alt['eur']['parcial'] = par
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
                # La suma no se compara, pero el ritmo si se puede medir con
                # los años que hay: el reloj lo usa (pedido del autor, 12-10-2026).
                v[serie + '_mdp']['parcial'] = {
                    'v': round(sum(x['mdp'] for x in filas), 1), 'est': 'derivado', 'f': fts, 'ys': [anios[0], anios[-1]],
                    'op': 'Suma de %s, los años con dato, en millones de pesos de cada año: %s.' % (rango, ' + '.join(mdp(x['mdp']) for x in filas)),
                    'just': 'El reloj corre al ritmo de %s, los %d años del sexenio con dato, entre los segundos de esos %d años. %s'
                            % (rango, len(anios), len(anios), falta['motivo']),
                    'alt': conversiones(datos, anios, fts)}
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
    # El dinero va primero en cada dimension (pedido del autor, 12-10-2026):
    # la suma en pesos abre la comparativa y el % del PIB queda de contexto.
    dims = [
        {'id': 'ingresos', 'ico': '💰', 'tit': 'Ingresos', 'tono': 'verde', 'kpi': 'ingresos_pib',
         'que': RADAR_SERIES['ingresos'][1], 'metricas': ['ingresos_mdp', 'ingresos_pib']},
        {'id': 'inversion', 'ico': '🏗️', 'tit': 'Inversión', 'tono': 'azul', 'kpi': 'inversion_pib',
         'que': RADAR_SERIES['inversion'][1], 'metricas': ['inversion_mdp', 'inversion_pib']},
        {'id': 'costo', 'ico': '🏛️', 'tit': 'Costo del gobierno', 'tono': 'ambar', 'kpi': 'gasto_pib', 'kpi2': 'costo_financiero_pib',
         'que': RADAR_SERIES['gasto'][1] + ' Y, aparte, lo que se fue solo en intereses.',
         'metricas': ['gasto_mdp', 'costo_financiero_mdp', 'gasto_pib', 'costo_financiero_pib']},
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
          <div class="rd-ficha" id="rdFicha"></div>
          <div class="rd-dim" id="rdDim"></div>
          <noscript><p>El tablero necesita JavaScript.</p></noscript>
        </div>
        <section class="rd-comp-sec" aria-labelledby="rdCompH">
          <h2 class="rd-comp-h" id="rdCompH">📊 Las administraciones, lado a lado</h2>
          <p class="rd-comp-intro">Elige qué comparar: las barras se mueven dentro de la misma gráfica y las cifras se cuentan solas.</p>
          <div id="rdComp"></div>
        </section>'''.format(datos=datos)
    # «El peso en el tiempo» se parte en tres paginas (pedido del autor,
    # 12-10-2026): las monedas y la inflacion, con un simulador que recorre
    # los sexenios año por año y arranca en ceros; el peso en cada sexenio,
    # y la maquina del tiempo. radar-peso.html queda como indice de las tres.
    peso_monedas_html = '''<div class="rd-peso" id="rdPeso">
          <div class="rd-peso-hoy" id="rdPesoHoy"></div>
          <div class="rd-graf" id="rdGraf">
            <div class="rd-mets" role="tablist" aria-label="Qué gráfica ver" id="rdGrafTabs"></div>
            <div class="rd-cuenta rd-sim-cuenta" id="rdSimCuenta" hidden>
              <button type="button" class="rd-cuenta-btn" id="rdSimPlay" aria-pressed="false">▶ Recorrer los sexenios</button>
              <button type="button" class="rd-cuenta-btn rd-cuenta-sec" id="rdSimCero">↺ Reiniciar en ceros</button>
              <span class="rd-cuenta-txt" id="rdSimTxt"></span>
            </div>
            <div class="rd-sim-marca" id="rdSimMarca" aria-live="polite"></div>
            <div class="rd-graf-lienzo" id="rdGrafSvg"></div>
            <label class="rd-sim-reg" id="rdSimReg" hidden><span>Elige un año: <b id="rdSimAnioTxt">—</b></span>
              <input type="range" id="rdSimAnio" step="1"></label>
            <div class="rd-sim-adms" id="rdSimAdms" aria-label="Ir al sexenio de"></div>
            <p class="rd-graf-lee" id="rdGrafLee" aria-live="polite"></p>
            <div class="rd-graf-pie" id="rdGrafPie"></div>
          </div>
          <noscript><p>El simulador necesita JavaScript.</p></noscript>
        </div>'''
    peso_sexenios_html = '''<div class="rd-peso" id="rdPeso">
          <div class="rd-peso-tabla" id="rdPesoTabla"></div>
          <noscript><p>Esta sección necesita JavaScript.</p></noscript>
        </div>'''
    peso_html = '''<div class="rd-peso" id="rdPeso">
          <div class="rd-maq" id="rdMaq">
            <div class="rd-maq-ctl">
              <label>Cantidad<span class="rd-maq-monto">$<input type="number" id="rdMaqMonto" min="0" step="any" value="1000" inputmode="decimal"></span></label>
              <label>Pesos del año<select id="rdMaqAnio"></select></label>
              <label>Proyectar hasta<select id="rdMaqHasta"></select></label>
            </div>
            <div id="rdMaqOut" aria-live="polite"></div>
          </div>
          <noscript><p>La máquina del tiempo necesita JavaScript.</p></noscript>
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
    # El duelo arranca en ceros (pedido del autor, 12-10-2026): el boton
    # «Empezar duelo» lleva cada cifra y cada barra a su valor; el mismo
    # boton las regresa a cero. Sin JavaScript no hay duelo que mostrar.
    duelo_html = '''<div class="rd-duelo" id="rdDuelo">
          <div class="rd-duelo-ctl"><select id="rdDuelo1" aria-label="Primera administración"></select><span>vs</span>
            <select id="rdDuelo2" aria-label="Segunda administración"></select></div>
          <div class="rd-cuenta rd-duelo-cuenta" id="rdDueloCuenta" hidden>
            <span class="rd-cuenta-txt" id="rdDueloTxt">Las cifras están en cero. Elige dos administraciones y presiona «Empezar duelo».</span>
            <button type="button" class="rd-cuenta-btn" id="rdDueloBtn" aria-pressed="false">▶ Empezar duelo</button>
          </div>
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
            <h3 id="exVerTit">🔏 Verifica un estado de cuenta o una ficha técnica</h3>
            <p>¿Te compartieron uno? Escribe su folio (viene arriba del documento y junto al sello) o su huella digital, y te
              decimos si coincide, cifra por cifra, con los datos vigentes de la plataforma. También sirve para las fichas
              técnicas del <a href="herramienta-inspector-entes.html">Auditor de entes públicos</a> (folios AV-FT-…).</p>
            <form class="ex-ver-f" id="exVerForm"><input type="text" id="exVerIn" placeholder="AV-AMLO-1A2B3C4D" autocomplete="off" spellcheck="false" aria-label="Folio o huella digital">
              <button type="submit" class="sz-btn sz-btn-of">Verificar</button></form>
            <div id="exVerOut" aria-live="polite"></div>
          </section>
          <section class="ex-verifica ex-ver-como" aria-labelledby="exComoTit">
            <h3 id="exComoTit">Cómo funciona</h3>
            <ol>
              <li><b>La huella.</b> Cada estado de cuenta firma sus cifras con una huella digital SHA-256: si cambia una sola cifra, cambia la huella.</li>
              <li><b>El folio.</b> Son las iniciales de quién es el documento y los primeros ocho caracteres de su huella, por ejemplo AV-AMLO-1A2B3C4D. Las fichas técnicas de los entes públicos llevan AV-FT y los ocho caracteres de la suya: su huella se recalcula en la página del Auditor de entes públicos, que tiene los datos de los tres niveles de gobierno, y allá te lleva esta página.</li>
              <li><b>La comprobación.</b> Esta página recalcula, en tu navegador, la huella de los %d estados de cuenta vigentes y busca la tuya.
                Si coincide, el documento no se alteró; si no, o se alteró o se expidió con datos anteriores: expídelo de nuevo en
                <a href="radar-estado-de-cuenta.html">Expide un estado de cuenta</a> y compara.</li>
            </ol>
            <p class="ex-pista">El sello no hace oficial al documento: dice que sus cifras son las que publica Auditavisión, cada una con su fuente.</p>
          </section>
          <noscript><p>La verificación necesita JavaScript.</p></noscript>
        </div>''' % (len(admins) + len(radar_cargos(base)['docs']))

    partes = {
        'tablero': ('Elige una administración y toca cada tarjeta para ver sus cifras: ingresos, inversión, '
                    'costo del gobierno, deuda y lo pendiente ante la Auditoría Superior, desde 1989. Abajo, una gráfica las pone '
                    'lado a lado. Las sumas en pesos se ven en pesos de cada año, en pesos de hoy, en dólares o en euros. '
                    'Cada cifra trae su documento.', tablero),
        'peso': ('Cuánto vale hoy el peso, cuánto valía en cada sexenio frente al dólar y al euro, y hacia dónde lo proyecta '
                 'Hacienda hasta 2032. Con la máquina del tiempo, lleva cualquier cantidad de un año a otro.', [
                    {'id': 'partes', 'titulo': 'Elige por dónde empezar', 'texto': 'Cada tarjeta abre su propia página.',
                     'tarjetas': [(r[0], r[2], r[3], r[1], '', '') for r in RADAR_PESO_PARTES]}]),
        'reloj': ('Elige una administración, qué contar y en qué moneda: el contador corre al ritmo promedio de su sexenio. '
                  'Es una equivalencia, no dinero que se mueva hoy.', datos_js + reloj_html),
        'duelo': ('Dos administraciones, cara a cara, en las mismas medidas. Sin ganador: los números dicen cuánto; el juicio es tuyo.',
                  datos_js + duelo_html),
    }
    paginas = [{
        'archivo': 'radar-hacendario.html', 'menu': 'Radar hacendario', 'menu_archivo': 'descarga-los-datos.html',
        'padre': ('descarga-los-datos.html', 'Datos'),
        'icono': '📡', 'titulo': 'Radar hacendario', 'lema': 'Cada administración, con sus números',
        'entrada': ('Lo que entró, lo que se invirtió, lo que costó el gobierno, la deuda que recibió y entregó, y lo que quedó '
                    'por aclarar ante la Auditoría Superior: administración por administración, desde 1989. Compáralas en pesos de '
                    'cada año, en pesos de hoy, en dólares o en euros; mira cuánto ha valido el peso y hacia dónde lo proyecta Hacienda, '
                    'y pon a correr el reloj de cada sexenio. Cada cifra trae su documento.'),
        # El boton 📖 al final de la entrada abre «Como leer estos numeros»
        # en la ventana lateral (apartados.js, data-cajon).
        'cajon': {'id': 'tplRadarLectura', 'hash': 'lectura', 'titulo_id': 'rdLecturaTit',
                  'boton': 'Cómo leer estos números: qué mide cada cifra y de dónde sale',
                  'html': '<header class="glos-drawer-cab"><span class="glos-drawer-marca"><span aria-hidden="true">📏</span> Cómo leer estos números</span>'
                          '<button type="button" class="glos-drawer-x" aria-label="Cerrar">✕</button></header>'
                          '<div class="glos-drawer-cuerpo"><span class="glos-drawer-cat">Radar hacendario · Punto de referencia</span>'
                          '<h3 id="rdLecturaTit" class="glos-drawer-tit">Cómo leer estos números</h3>'
                          '<section class="glos-drawer-sec"><h4>Antes de comparar sexenios</h4>'
                          '<p>Qué mide cada cifra, de qué serie sale y qué no se puede concluir con ella.</p>%s</section></div>'
                          '<footer class="glos-drawer-pie"><a class="glos-drawer-todo" href="fuentes-oficiales.html" style="text-align:center; text-decoration:none;">📚 Ver las fuentes oficiales ➔</a></footer>'
                          % lectura.replace('class="rd-lectura"', 'class="rd-lectura glos-drawer-lista"')},
        # Las anclas de cuando todo vivia en esta pagina llevan a la suya.
        'hash_a_pagina': dict({r[0]: r[1] for r in RADAR_PARTES}, hoy='numeros-cuanto-dinero-es.html',
                              expide='radar-estado-de-cuenta.html'),
        'pestanas': True,
        'pista': 'Cada parte del radar abre su propia página.',
        # Cada tarjeta lleva una descripcion narrativa breve (pedido del autor,
        # 12-10-2026; antes iban solo con icono y titulo). Sin cifras: lo
        # numerico, con su fuente, se queda en cada pagina.
        'secciones': [{'id': r[0], 'pagina': r[1], 'pestana': (r[2], r[3], RADAR_NARRATIVA[r[0]])} for r in RADAR_PARTES],
    }]
    for (pid, archivo, ico, tit, sub) in RADAR_PARTES:
        entrada, bloque = partes[pid]
        paginas.append({
            'archivo': archivo, 'menu': tit, 'menu_archivo': 'descarga-los-datos.html',
            'padre': ('descarga-los-datos.html', 'Datos'), 'padre2': ('radar-hacendario.html', 'Radar hacendario'),
            'icono': ico, 'titulo': tit, 'lema': 'Radar hacendario', 'entrada': entrada,
            'estilos': ['radar.css'], 'scripts': ['radar.js'], 'pie_extra': radar_nav(archivo),
            'secciones': bloque if isinstance(bloque, list) else
                         [{'id': pid, 'titulo': tit, 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': bloque}],
        })
    # Las tres partes de «El peso en el tiempo» (pedido del autor, 12-10-2026).
    peso_bloques = {'monedas': peso_monedas_html, 'sexenios': peso_sexenios_html, 'maquina': peso_html}
    for (ico, archivo, tit, sub, entrada, pid) in RADAR_PESO_PARTES:
        paginas.append({
            'archivo': archivo, 'menu': tit, 'menu_archivo': 'descarga-los-datos.html',
            'padre': ('descarga-los-datos.html', 'Datos'), 'padre2': ('radar-hacendario.html', 'Radar hacendario'),
            'padre3': ('radar-peso.html', 'El peso en el tiempo'),
            'icono': ico, 'titulo': tit, 'lema': 'Radar hacendario', 'entrada': entrada,
            'estilos': ['radar.css'], 'scripts': ['radar.js'], 'pie_extra': radar_nav('radar-peso.html'),
            'secciones': [{'id': pid, 'titulo': tit, 'texto': '', 'sin_cab': True, 'tarjetas': [],
                           'bloque': datos_js + peso_bloques[pid]}],
        })
    # «Expide un estado de cuenta», en su propia pagina (pedido del autor, 10-10-2026).
    paginas.append({
        'archivo': 'radar-estado-de-cuenta.html', 'menu': 'Estado de cuenta administrativo', 'menu_archivo': 'herramientas.html',
        # Del 12-10-2026 al 22-10-2026 fue la cuarta tarjeta de Datos; desde
        # entonces (pedido del autor) es la quinta aplicacion de la
        # Calculadora Civica, con sus migas y su pie (nav_de_pagina).
        'padre': (AUDITOR_VIRTUAL, 'Auditor Virtual'),
        'padre2': ('herramienta-calculadora.html', 'Calculadora Cívica'),
        'icono': '🏛️', 'titulo': 'Estado de cuenta administrativo', 'lema': 'Calculadora Cívica · aplicación 5 de 5',
        'sin_icono_lema': True, 'icono_cab': '🏛️', 'fondo': HERR_IMG['calculadora'], 'rubro': 'calculadora',
        'entrada': EXPIDE_TEXTO + ' Cualquiera puede comprobar que no se alteró.',
        'estilos': ['radar.css', 'estado-administracion.css'], 'scripts': ['radar.js', 'estado-administracion.js'],
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
    'menu': 'Diccionario',
    'menu_archivo': 'aprende.html',
    'padre': ('aprende.html', 'Aprende'),
    'padre2': ('diccionario.html', BIB_NOMBRE),
    'icono': '📖',
    'titulo': 'Diccionario',
    'lema': 'Glosario de términos hacendarios, en lenguaje llano',
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
    migas = {'menu_archivo': 'aprende.html', 'padre': ('aprende.html', 'Aprende'),
             'padre2': ('diccionario.html', BIB_NOMBRE), 'pie_extra': bib_nav(archivo)}
    return dict(migas, **{
        'archivo': archivo, 'menu': b[2],
        'icono': b[1], 'titulo': titulo, 'lema': lema, 'entrada': entrada,
        'scripts': list(scripts),
        'secciones': [{
            'id': 'contenido-' + archivo[:-5], 'titulo': titulo, 'texto': '', 'sin_cab': True, 'tarjetas': [],
            'bloque': bloque or ('<div class="bib" id="%s">\n'
                                 '          <p class="gl-carga" role="status">⏳ %s</p>\n'
                                 '          <noscript><p>Esta página necesita JavaScript.</p></noscript>\n'
                                 '        </div>' % (raiz, carga)),
        }],
    })


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
        'fuentes-oficiales.html', 'Referencias', 'Compendio de fuentes oficiales: cada documento que sostiene una cifra',
        'Las fichas numeradas que citan las cifras de la plataforma, con su liga al documento. Si llegaste desde una nota '
        'como [11], la ficha aparece iluminada.',
        'bibFuentes', 'Cargando el catálogo…'),
    # El Pase del Auditor Civico se retiro el 24-10-2026 (decision del
    # autor): pase-del-auditor.html redirige a Donaciones (REDIRECCIONES).
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
    for archivo, nombre, marcan in MENU:
        cur = ' aria-current="page"' if actual in marcan else ''
        items.append('      <div class="nav-menu-item"><a class="mega-menu-trigger" href="%s"%s>%s</a></div>'
                     % (archivo, cur, nombre))
    # Cuarta pestaña, solo en pantalla angosta (pedido del autor, 23-10-2026):
    # sustituye al recuadro que cerraba el menú plegado.
    items.append('      <div class="nav-menu-item nav-menu-cuentanos"><a class="mega-menu-trigger nav-cuentanos" '
                 'href="comunidad.html" data-puerta>📢 Cuéntanos lo que viste</a></div>')
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
        <a class="nav-action-btn nav-feedback-btn" href="comunidad.html" data-puerta title="Cuéntanos lo que viste: algo raro con el dinero público, un dato mal, un tema para investigar, compartir y fe de erratas">
          <span>📢</span>
          <span>Cuéntanos lo que viste</span>
        </a>
        <button type="button" class="nav-action-btn nav-share-btn" id="apartadoCompartir" title="Compartir esta página o copiar su enlace">
          <span>🔗</span>
          <span>Compartir</span>
        </button>
        <a href="diccionario.html" class="nav-action-btn nav-creator-badge" title="Creado por Inspector Meteoro · Biblioteca del Erario Público">
          <span>🪐</span>
          <span>Inspector Meteoro</span>
        </a>
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
              '          <span class="apartado-tarjeta-nombre">%s</span>' % nombre]
    # Las tarjetas con foto de las herramientas ya no llevan icono: vive en
    # el encabezado de su pagina (pedido del autor, 11-10-2026).
    if not (modulo and rubro in HERR_ICONO_CAB):
        partes.insert(1, '          <span class="apartado-tarjeta-icono" aria-hidden="true">%s</span>' % icono)
    if desc:
        partes.append('          <span class="apartado-tarjeta-desc">%s</span>' % desc)
    if dato:
        partes.append('          <span class="apartado-tarjeta-dato"><strong>%s</strong><span>%s</span></span>' % dato)
    partes.append('          <span class="apartado-tarjeta-accion">%s</span>' % accion)
    partes.append('        </a>')
    return '\n'.join(partes)


# Numeros (reestructura del 10-10-2026, pedido del autor): «El peso de
# 2026» arriba de los seis pasos y, en el paso 3, los tres presupuestos.
# Todas las cifras salen de window.AUDIT_DB (panoramaErario): la Ley de
# Ingresos renglon por renglon y la clasificacion funcional del gasto
# programable de los Criterios 2027 (cuadro de la p. 39). La lectura en
# tres presupuestos agrupa esas finalidades oficiales: es derivada y dice
# su operacion.
NUM_GRUPOS_ING = [
    # (grupo de la base, id, icono, nombre, que es)
    ('Impuestos', 'impuestos', '🧾', 'Impuestos',
     'ISR, IVA, IEPS, comercio exterior y los demás impuestos federales. Contribuir es una obligación del artículo 31, fracción IV de la Constitución.'),
    ('Otras contribuciones', 'contribuciones', '🏥', 'Cuotas y derechos',
     'Las cuotas de seguridad social, los derechos por usar bienes de la Nación o recibir un servicio público y las contribuciones de mejoras.'),
    ('No tributarios', 'propios', '🏭', 'Ventas y otros ingresos',
     'Lo que venden IMSS, ISSSTE, Pemex y CFE, las transferencias del Fondo Mexicano del Petróleo, productos y aprovechamientos.'),
    ('Financiamiento', 'deuda', '🏦', 'Deuda',
     'Lo que se pide prestado. La Ley de Ingresos lo cuenta como ingreso: por eso el presupuesto siempre «cuadra».'),
]


def _mdp(v, d=1):
    return '$' + format(v, ',.%df' % d) + ' mdp'


def _bill(v):
    return '$%.2f billones' % (v / 1e6)


def numeros_datos(base):
    """Datos de «El peso de 2026» y de los tres presupuestos."""
    p = base['panoramaErario']
    total = p['totalPEF']
    refs = {r['id']: r for r in base['referencias_legales']}
    eg = {r['id']: r for r in p['egresos']}

    def fuente(rid):
        r = refs[rid]
        return {'n': r['num'], 'url': 'fuentes-oficiales.html#' + rid, 't': re.sub('<[^>]+>', '', r['cita_apa'])[:160]}

    entra = []
    for grupo, gid, ico, nom, que in NUM_GRUPOS_ING:
        filas = [r for r in p['ingresos'] if r['grupo'] == grupo]
        entra.append({
            'id': gid, 'ico': ico, 'nom': nom, 'que': que, 'v': round(sum(r['montoMdp'] for r in filas), 1),
            'est': 'oficial' if len(filas) == 1 else 'derivado',
            'op': '' if len(filas) == 1 else 'Suma de %d renglones del artículo 1o. de la Ley de Ingresos 2026.' % len(filas),
            'filas': [{'n': r['nombre'], 'v': r['montoMdp'], 'g': glosario_ancla(r['glos']) if r.get('glos') else ''} for r in filas],
            'f': [fuente('ref-lif2026')], 'paso': 'origen', 'pnum': 1,
        })
    estado = eg['egr-gobierno']['montoMdp'] + eg['egr-poderes']['montoMdp']
    noprog = [eg['egr-costofin'], eg['egr-participaciones'], eg['egr-adefas']]
    sale = [
        {'id': 'social', 'ico': '🫂', 'nom': 'Presupuesto social', 'v': eg['egr-social']['montoMdp'], 'est': 'oficial',
         'que': 'Lo que se invierte en las personas: educación, salud pública, seguridad social, vivienda y esparcimiento.',
         'op': 'Finalidad «Desarrollo social» del gasto programable, tal como la publica la fuente.',
         'filas': [{'n': 'Protección social', 'pib': 6.2}, {'n': 'Educación', 'pib': 2.9}, {'n': 'Salud', 'pib': 2.5},
                   {'n': 'Vivienda y servicios a la comunidad', 'pib': 1.1}, {'n': 'Protección ambiental', 'pib': 0.0}],
         'f': [fuente('ref-cgpe2027')], 'g': glosario_ancla('Gasto Programable vs No Programable'), 'paso': 'gasta', 'pnum': 3},
        {'id': 'nacional', 'ico': '🏗️', 'nom': 'Presupuesto nacional', 'v': eg['egr-economico']['montoMdp'], 'est': 'oficial',
         'que': 'Lo que mueve al país: energía eléctrica, combustibles, carreteras, ferrocarriles, campo, ciencia y las empresas públicas.',
         'op': 'Finalidad «Desarrollo económico» del gasto programable, tal como la publica la fuente. Pemex y CFE reciben $1,071,929.6 mdp en el Anexo 1 del PEF 2026.',
         'filas': [{'n': 'Combustibles y energía', 'pib': 3.3}, {'n': 'Comunicaciones y transportes', 'pib': 0.6},
                   {'n': 'Agropecuaria, silvicultura, pesca y caza', 'pib': 0.2}, {'n': 'Asuntos económicos y laborales', 'pib': 0.2},
                   {'n': 'Ciencia, tecnología e innovación', 'pib': 0.2}],
         'f': [fuente('ref-cgpe2027'), fuente('ref-pef2026')], 'g': glosario_ancla('Rectoría Económica del Estado'), 'paso': 'gasta', 'pnum': 3},
        {'id': 'estado', 'ico': '🏛️', 'nom': 'Presupuesto del Estado', 'v': round(estado, 1), 'est': 'derivado',
         'que': 'Lo que el poder público necesita para funcionar: gobierno, justicia, seguridad, relaciones exteriores, el Congreso, los tribunales y los órganos autónomos.',
         'op': 'Finalidad «Gobierno» ($%s mdp) más poderes, órganos autónomos, INEGI y Tribunal Federal de Justicia Administrativa ($%s mdp).'
               % (format(eg['egr-gobierno']['montoMdp'], ',.1f'), format(eg['egr-poderes']['montoMdp'], ',.1f')),
         'filas': [{'n': 'Gobierno: Administración Pública Federal', 'v': eg['egr-gobierno']['montoMdp']},
                   {'n': 'Poderes, órganos autónomos, INEGI y TFJA', 'v': eg['egr-poderes']['montoMdp']}],
         'f': [fuente('ref-cgpe2027')], 'g': glosario_ancla('Hacienda Pública'), 'paso': 'decide', 'pnum': 2},
        {'id': 'fondos', 'ico': '🛟', 'nom': 'Fondos de estabilización', 'v': eg['egr-fondos']['montoMdp'], 'est': 'oficial',
         'que': 'La aportación del año a los fondos que deben amortiguar una caída de los ingresos.',
         'op': 'Renglón de la clasificación funcional, tal como lo publica la fuente.', 'filas': [],
         'f': [fuente('ref-cgpe2027')], 'g': glosario_ancla('Fondo Mexicano del Petróleo (FMP)'), 'paso': 'gasta', 'pnum': 3},
        {'id': 'comprometido', 'ico': '🔒', 'nom': 'Ya comprometido', 'v': round(sum(r['montoMdp'] for r in noprog), 1), 'est': 'derivado',
         'que': 'El gasto no programable: no compra bienes ni servicios. Paga intereses, entrega a estados y municipios lo que les toca y salda las cuentas del año anterior.',
         'op': 'Costo financiero + participaciones (Ramo 28) + ADEFAS (Ramo 30).',
         'filas': [{'n': r['nombre'], 'v': r['montoMdp'], 'g': glosario_ancla(r['glos'])} for r in noprog],
         'f': [fuente('ref-pef2026')], 'g': glosario_ancla('Gasto Programable vs No Programable'), 'paso': 'deuda', 'pnum': 5},
    ]
    suma = round(sum(x['v'] for x in sale), 1)
    return {'total': total, 'entra': entra, 'sale': sale, 'redondeo': round(total - suma, 1),
            'fTotal': [fuente('ref-lif2026'), fuente('ref-pef2026')]}


def numeros_peso(d):
    """«El peso de 2026»: el bloque que numeros.js vuelve interactivo."""
    def barra(lado, filas):
        return ''.join('<button type="button" class="np-seg np-%s" data-lado="%s" data-id="%s" style="flex-grow:%s" '
                       'aria-pressed="false"><span class="np-seg-tx"><b>%s</b> <span class="np-seg-v">%s</span></span></button>'
                       % (x['id'], lado, x['id'], '%.4f' % (x['v'] / d['total'] * 100), x['nom'], _bill(x['v'])) for x in filas)
    def leyenda(lado, filas):
        return '<div class="np-ley">%s</div>' % ''.join(
            '<button type="button" class="np-ley-b" data-lado="%s" data-id="%s" aria-pressed="false">'
            '<span class="np-ley-p np-%s" aria-hidden="true"></span>%s</button>' % (lado, x['id'], x['id'], x['nom']) for x in filas)
    return '''<section class="np" id="numPeso" aria-labelledby="npTit">
        <div class="np-cab">
          <h2 class="np-tit" id="npTit">El peso de 2026: de dónde viene y a dónde va</h2>
          <p class="np-txt">Todo el dinero federal del año, <b>%s</b>, cabe en estas dos barras. Arriba, lo que entra según la %s; abajo, lo que sale según el %s. Toca cualquier tramo.</p>
          <div class="np-modo" role="radiogroup" aria-label="Cómo ver las cifras">
            <button type="button" role="radio" aria-checked="true" data-modo="pesos">En pesos</button>
            <button type="button" role="radio" aria-checked="false" data-modo="cien">Por cada $100</button>
          </div>
        </div>
        <div class="np-fila"><span class="np-lado">⬇️ Entra</span><div class="np-barra" role="group" aria-label="Lo que entra">%s</div></div>
        %s
        <div class="np-fila"><span class="np-lado">⬆️ Sale</span><div class="np-barra" role="group" aria-label="Lo que sale">%s</div></div>
        %s
        <div class="np-det" id="npDet" aria-live="polite"></div>
        <p class="np-pie">Cifras en millones de pesos (mdp). La Ley de Ingresos y el Presupuesto de Egresos suman lo mismo por construcción: la deuda se cuenta como ingreso. %s %s</p>
        <script type="application/json" id="npDatos">%s</script>
        <noscript><p>Sin JavaScript se ven las dos barras; el detalle de cada tramo necesita JavaScript.</p></noscript>
      </section>''' % (
        _mdp(d['total']), glos('LIF (Ley de Ingresos de la Federación)', 'Ley de Ingresos'),
        glos('PEF (Presupuesto de Egresos de la Federación)', 'Presupuesto de Egresos'),
        barra('entra', d['entra']), leyenda('entra', d['entra']), barra('sale', d['sale']), leyenda('sale', d['sale']),
        nota_ref('ref-lif2026', 10, 'Ley de Ingresos de la Federación 2026'), nota_ref('ref-pef2026', 11, 'Presupuesto de Egresos de la Federación 2026'),
        json.dumps(d, ensure_ascii=False).replace('</', '<\\/'))


def numeros_tres(d):
    """Paso 3: los tres presupuestos, con su cifra oficial o derivada."""
    tot = d['total']
    s = {x['id']: x for x in d['sale']}
    def tarjeta(x):
        filas = ''.join('<li><span>%s</span><b>%s</b></li>' % (
            f['n'], ('%.1f pts. del PIB' % f['pib']) if 'pib' in f else _mdp(f['v'])) for f in x['filas'])
        return ('<article class="np3-c np3-%s"><span class="np3-ico" aria-hidden="true">%s</span><h3>%s</h3>'
                '<p class="np3-cifra"><b>%s</b> <span class="est-chip est-%s">%s</span></p>'
                '<p class="np3-cien">De cada $100: <b>$%.2f</b></p>'
                '<p class="np3-que">%s</p><ul class="np3-filas">%s</ul><p class="np3-op">%s %s</p></article>'
                % (x['id'], x['ico'], x['nom'], _mdp(x['v']), x['est'], x['est'], x['v'] / tot * 100,
                   x['que'], filas, x['op'], ' '.join(nota_ref(f['url'].split('#')[1], f['n'], f['t']) for f in x['f'])))
    return '''<div class="np3">
          <p class="np3-intro">La doctrina del derecho económico lee el presupuesto en tres renglones %s. Hacienda no los publica con esos nombres, pero sí su <b>clasificación funcional</b>: cada uno corresponde a una de sus finalidades. Aquí se juntan, con la operación a la vista.</p>
          <div class="np3-rej">%s</div>
          <div class="np3-ojo"><b>👁️ Ojo con la frontera.</b> Las dos lecturas no coinciden en todo: el agua potable y la urbanización, que la doctrina pone en el presupuesto nacional, en la clasificación oficial entran en «vivienda y servicios a la comunidad», dentro del desarrollo social. Así lo ordena el Clasificador Funcional del Gasto del CONAC, que se emite con base en la %s. Y las empresas públicas cuentan por su gasto: combustibles y energía, donde están Pemex y CFE, pesan tres cuartas partes del presupuesto nacional. Los puntos del PIB son los que publican los Criterios 2027 para 2026.</div>
          <div class="np3-fuera"><span class="np3-ico" aria-hidden="true">%s</span><div><h3>%s: %s <span class="est-chip est-%s">%s</span></h3>
            <p>%s De cada $100, <b>$%.2f</b>. %s</p>
            <ul class="np3-filas">%s</ul></div></div>
          <p class="np3-op">Además, %s (%s de cada $100) van a los %s. Las cinco partes suman %s; los %s que faltan para %s son redondeo de la fuente, que publica la clasificación funcional en miles de millones.</p>
        </div>''' % (
        nota_ref('ref-gomez-granillo-1995', 119, 'Gómez Granillo y Gutiérrez Rosas (1995)'),
        ''.join(tarjeta(s[k]) for k in ('estado', 'nacional', 'social')),
        'Ley General de Contabilidad Gubernamental ' + nota_ref('ref-lgcg', 12, 'Ley General de Contabilidad Gubernamental'),
        s['comprometido']['ico'], s['comprometido']['nom'], _mdp(s['comprometido']['v']), s['comprometido']['est'], s['comprometido']['est'],
        s['comprometido']['que'], s['comprometido']['v'] / tot * 100, s['comprometido']['op'],
        ''.join('<li><a href="glosario.html#%s">%s</a><b>%s</b></li>' % (f['g'], f['n'], _mdp(f['v'])) for f in s['comprometido']['filas']),
        _mdp(s['fondos']['v']), '$%.2f' % (s['fondos']['v'] / tot * 100), glos('Fondo Mexicano del Petróleo (FMP)', 'fondos de estabilización'),
        _mdp(tot - d['redondeo']), _mdp(d['redondeo']), _mdp(tot))


# Numeros en paginas (pedido del autor, 11-10-2026): la portada es como la
# del Radar hacendario, tarjetas sin numero, y cada una
# abre su propia pagina. Eran siete; el mismo dia «Presupuesto» (El peso de
# 2026) se fundio con «Se recauda» (pedido del autor), y despues «Se
# aprueba» y «Se gasta» en «Gasto publico», y «Se paga lo que se debe» y
# «Se revisa» en «Cuentas claras»: quedan cuatro, cada una con su
# descripcion breve, como las de Participa.
NUMEROS_PARTES = [
    # (id de la seccion, archivo, icono, nombre de la tarjeta, descripcion)
    ('origen', 'numeros-presupuesto.html', '💵', 'Presupuesto', 'Cuánto dinero hay en 2026 y de dónde sale cada peso'),
    ('gasta', 'numeros-gasto-publico.html', '🏛️', 'Gasto público', 'Quién lo aprueba, cómo se reparte y en qué se va'),
    ('baja', 'numeros-baja-al-territorio.html', '📍', 'Baja al territorio', 'Lo que llega a los 32 estados y a los 2,479 municipios'),
    ('cuentas', 'numeros-cuentas-claras.html', '⚖️', 'Cuentas claras', 'Lo que se debe, sexenio por sexenio, y quién revisa cómo se gastó'),
]
# Paginas de Numeros que cambiaron de nombre o se fundieron (11-10-2026).
NUMEROS_ANTES = [
    ('numeros-se-recauda.html', 'numeros-presupuesto.html', 'Se recauda',
     'Ahora se llama «Presupuesto»: las dos barras viven en «Cuánto dinero es» y los 16 orígenes del ingreso tienen su propia página.'),
    ('numeros-se-aprueba.html', 'numeros-gasto-publico.html', 'Se aprueba',
     'Se fundió con «Se gasta» en «Gasto público».'),
    ('numeros-se-gasta.html', 'numeros-gasto-publico.html', 'Se gasta: los tres presupuestos',
     'Se fundió con «Se aprueba» en «Gasto público».'),
    ('numeros-el-peso-de-2026.html', 'numeros-cuanto-dinero-es.html#numPeso', 'El peso de 2026',
     'Se fundió con «Cuánto dinero es»: las dos barras de lo que entra y lo que sale siguen ahí.'),
    ('numeros-la-deuda.html', 'numeros-cuentas-claras.html', 'Se paga lo que se debe',
     'Se fundió con «Se revisa» en «Cuentas claras».'),
    ('numeros-se-revisa.html', 'numeros-cuentas-claras.html', 'Se revisa',
     'Se fundió con «Se paga lo que se debe» en «Cuentas claras».'),
]
NUMEROS_PAGINAS = []
# ?abrir=eb-bloque: a que direccion de Numeros lleva cada bloque del motor.
NUMEROS_ABRIR = {}
# Los bloques del motor que eran tarjetas de «Presupuesto» y de «Gasto
# publico» y ahora tienen su pagina de modulo (11-10-2026):
# (ancla, archivo, icono, nombre, destino, parte).
NUMEROS_MODULOS = [
    # Abre «Presupuesto» desde el 24-10-2026 (vivia en «Gasto publico»).
    ('gp-tres', 'numeros-gasto-tres-presupuestos.html', '🧭', 'Los tres presupuestos', None, 'origen'),
    ('eb-cuanto', 'numeros-cuanto-dinero-es.html', '💰', 'Cuánto dinero es', ir('presupuesto', 'eb-cuanto'), 'origen'),
    ('nr-origenes', 'numeros-los-16-origenes.html', '🧾', 'Los 16 orígenes del ingreso', None, 'origen'),
    ('eb-equivale', 'numeros-a-que-equivale.html', '📏', '¿A qué equivale?', ir('presupuesto', 'eb-equivale'), 'origen'),
    ('eb-arquitectura', 'numeros-camino-del-dinero.html', '🏛️', 'El camino del dinero, en cuatro etapas', ir('presupuesto', 'eb-arquitectura'), 'origen'),
    ('proyeccion2027', 'numeros-paquete-2027.html', '📈', 'Paquete Económico 2027', ir('proyeccion2027'), 'origen'),
    ('poderes', 'numeros-lo-que-cuestan-los-poderes.html', '⚖️', 'Lo que cuestan el Congreso y la Judicatura', ir('poderes'), 'gasta'),
    ('eb-egresos', 'numeros-ramos-y-dependencias.html', '🏢', 'En qué se va: ramos y dependencias', ir('presupuesto', 'eb-egresos'), 'gasta'),
    ('eb-salud', 'numeros-margen-del-presupuesto.html', '🌡️', '¿Cuánto margen tiene el presupuesto?', ir('presupuesto', 'eb-salud'), 'gasta'),
    ('eb-ciegos', 'numeros-lo-que-la-cifra-no-dice.html', '🔦', 'Lo que la cifra grande no dice', ir('presupuesto', 'eb-ciegos'), 'gasta'),
    ('eb-cuenta-federal', 'numeros-estado-de-resultados.html', '📒', 'El estado de resultados del Gobierno', ir('presupuesto', 'eb-cuenta-federal'), 'cuentas'),
    # Los tres de «Baja al territorio», en pagina propia (11-10-2026):
    # territorio_modulos.py.
    ('eb-mapa', 'numeros-mapa-del-gasto-federalizado.html', '📍', 'El mapa del gasto federalizado', None, 'baja'),
    ('territorio', 'numeros-las-32-entidades.html', '🗺️', 'Las 32 entidades: del peso federal al estatal', None, 'baja'),
    ('municipios', 'numeros-los-municipios.html', '🏘️', 'Los 2,479 municipios: predial y transferencias', None, 'baja'),
]
# Las tres categorias de impuesto que el art. 1o. de la Ley de Ingresos 2026
# enumera en $0.0 (el mismo texto que ERARIO_RUBROS_CERO del motor).
NUM_INGRESO_CERO = [
    ('1.12', 'Impuestos sobre el patrimonio',
     'La Federación no grava la riqueza acumulada. No existe hoy un impuesto federal al patrimonio neto, a la herencia ni a las donaciones.'),
    ('1.15', 'Impuestos sobre nóminas y asimilables',
     'El impuesto sobre nóminas existe, pero es estatal: lo cobran las 32 entidades, no la Federación. Por eso aparece en el catálogo federal con cero.'),
    ('1.16', 'Impuestos ecológicos',
     'El catálogo federal los contempla y los presupuesta en cero. Los gravámenes ambientales que sí recauda la Federación viven dentro del IEPS (combustibles fósiles y plaguicidas), no en este rubro.'),
]


def ingreso_archivo(x):
    """Pagina de un renglon de la Ley de Ingresos: ing-isr -> numeros-ingreso-isr.html."""
    corto = {'comext': 'comercio-exterior', 'hidro': 'hidrocarburos', 'rezagos': 'ejercicios-anteriores',
             'aprovech': 'aprovechamientos', 'ventas': 'venta-de-bienes-y-servicios',
             'transf': 'fondo-mexicano-del-petroleo'}.get(x['id'][4:], x['id'][4:])
    return 'numeros-ingreso-%s.html' % corto


def _mdp0(v):
    return ('-' if v < 0 else '') + '$' + format(abs(v), ',.1f') + ' mdp'


def numeros_renglones(base, d):
    """Los 16 origenes del ingreso, con contador (numeros.js): arrancan en
    cero y cada renglon lleva a su pagina."""
    p = base['panoramaErario']
    total = p['totalLIF']
    mayor = max(x['montoMdp'] for x in p['ingresos'])
    grupos = []
    for x in p['ingresos']:
        if x['grupo'] not in [g[0] for g in grupos]:
            grupos.append((x['grupo'], []))
        grupos[[g[0] for g in grupos].index(x['grupo'])][1].append(x)
    bloques = []
    for nombre, filas in grupos:
        suma = sum(x['montoMdp'] for x in filas)
        bloques.append(
            '<div class="nr-grupo"><h3 class="nr-grupo-tit"><span>%s</span><span class="nr-grupo-v">%s · %s%% %s</span></h3><ol class="nr-filas">%s</ol></div>' % (
                nombre, _mdp0(suma), format(suma / total * 100, '.1f'),
                '<span class="est-chip est-derivado" title="Suma de sus renglones">derivado</span>' if len(filas) > 1 else '<span class="est-chip est-oficial">oficial</span>',
                ''.join('<li><a class="nr-fila" href="%s" data-v="%.1f" data-w="%.2f" data-pct="%.1f">'
                        '<span class="nr-ico" aria-hidden="true">%s</span><span class="nr-nom">%s</span>'
                        '<span class="nr-barra" aria-hidden="true"><span class="nr-relleno"></span></span>'
                        '<span class="nr-v">%s</span><span class="nr-pct">%s%%</span><span class="nr-ir" aria-hidden="true">➔</span></a></li>' % (
                            ingreso_archivo(x), x['montoMdp'], x['montoMdp'] / mayor * 100, x['montoMdp'] / total * 100,
                            x['icono'], x['nombre'], _mdp0(x['montoMdp']), format(x['montoMdp'] / total * 100, '.1f'))
                        for x in filas)))
    ceros = ''.join('<li><span class="nr-cero-clave">LIF %s</span><b>%s</b><span class="nr-cero-v">$0.0 mdp</span><p>%s</p></li>' % c
                    for c in NUM_INGRESO_CERO)
    return '''<section class="nr" id="nrRenglones" aria-labelledby="nrTit">
          <div class="nr-cab">
            <h2 class="np-tit" id="nrTit">Los 16 orígenes del ingreso, renglón por renglón</h2>
            <p class="np-txt">Tal como los enumera el artículo 1o. de la %s %s, en cuatro familias. Arrancan en cero: presiona «Contabilizar» y mira crecer cada barra. Toca un renglón para abrir su página: qué grava, qué ley lo sustenta, qué efecto jurídico produce y qué trae por dentro.</p>
            <div class="nr-mandos"><button type="button" class="rd-cuenta-btn nr-btn" id="nrContar" aria-pressed="false">▶ Contabilizar</button>
            <span class="nr-estado" id="nrEstado" role="status">Los 16 renglones están en ceros.</span></div>
          </div>
          <div class="nr-lista nr-ceros" id="nrLista">%s</div>
          <p class="np-pie">Cifras en millones de pesos (mdp), tal como las publica la ley. Cada barra se mide contra el renglón mayor (el ISR); el porcentaje es su parte del ingreso total, %s.</p>
          <details class="nr-cero">
            <summary>Y los que la ley enumera, pero deja en cero</summary>
            <p>El artículo 1o. lista tres categorías más de impuesto, presupuestadas en <b>$0.0 mdp</b> para 2026 <span class="est-chip est-oficial">oficial</span>. No se grafican porque una barra de cero no se ve; se dicen porque su ausencia explica tanto como las cifras de arriba.</p>
            <ul>%s</ul>
          </details>
        </section>''' % (glos('LIF (Ley de Ingresos de la Federación)', 'Ley de Ingresos de la Federación 2026'),
                         nota_ref('ref-lif2026', 10, 'Ley de Ingresos de la Federación 2026'),
                         ''.join(bloques), _mdp0(total), ceros)


def ingreso_pagina(x, n, lista, total, refs, glosario):
    """Pagina propia de un renglon del ingreso (11-10-2026): la ficha que
    antes abria en una ventana lateral dentro del visor."""
    archivo = ingreso_archivo(x)
    r = refs[x['refKey']]
    comps = x.get('componentes') or []
    if comps:
        mayor = max(abs(c['m']) for c in comps)
        desglose = ('<ol class="ni-comps">%s</ol>' % ''.join(
            '<li class="%s"><span class="ni-comp-n">%s%s</span><span class="nr-barra"><span class="nr-relleno" style="width:%.2f%%"></span></span>'
            '<b>%s</b><span class="nr-pct">%s%%</span></li>' % (
                'ni-neg' if c['m'] < 0 else ('ni-cero' if c['m'] == 0 else ''), c['n'],
                ('<small>%s</small>' % c['d']) if c['d'] else '', abs(c['m']) / mayor * 100 if mayor else 0,
                _mdp0(c['m']), format(c['m'] / x['montoMdp'] * 100, '.1f') if x['montoMdp'] else '0.0') for c in comps)
            + '<p class="np-pie">El desglose lo trae la propia Ley de Ingresos dentro de su clave %s. El porcentaje es la parte de cada componente en el total del renglón.%s</p>' % (
                x['claveLIF'], ' Las barras rayadas en rojo <b>restan</b>: reducen el total.' if any(c['m'] < 0 for c in comps) else ''))
    else:
        desglose = ('<p class="ni-sin">La Ley de Ingresos 2026 lo autoriza en <b>un solo renglón</b> (su clave es %s): no lo parte por dentro, '
                    'ni por tipo de contribuyente ni por actividad. Por eso aquí no hay desglose: no lo inventamos.</p>' % x['claveLIF'])
    term = x['glos'] if x['glos'] in glosario else None
    ant, sig = (lista[n - 1] if n > 0 else None), (lista[n + 1] if n + 1 < len(lista) else None)
    # El ultimo renglon sigue con el modulo que va despues de los 16 origenes.
    tras = NUMEROS_MODULOS[[m[0] for m in NUMEROS_MODULOS].index('nr-origenes') + 1]
    nav = presupuesto_pie(
        (ingreso_archivo(ant), '← Anterior', ant['icono'], ant['nombre']) if ant else ('numeros-los-16-origenes.html', '← Volver a', '🧾', 'Los 16 orígenes'),
        (ingreso_archivo(sig), 'Siguiente →', sig['icono'], sig['nombre']) if sig else (tras[1], 'Siguiente →', tras[2], tras[3]),
        ('numeros-los-16-origenes.html', '🧾 Los 16 orígenes: todos los renglones') if ant else None)
    bloque = '''<div class="ni">
          <div class="ni-cifra">
            <p class="ni-monto"><b>%s</b> <span class="est-chip est-%s">%s</span></p>
            <p class="ni-datos"><span>De cada $100 que entran: <b>$%.2f</b> <span class="est-chip est-derivado">derivado</span></span>
            <span>Familia: <b>%s</b></span><span>Clave en el art. 1o. de la ley: <b>%s</b></span></p>
            <p class="np-pie">Monto autorizado por la %s %s. «De cada $100» = %s ÷ %s × 100.</p>
          </div>
          <div class="ni-rej">
            <section class="ni-c"><h2>¿Qué %s?</h2><p>%s</p></section>
            <section class="ni-c"><h2>Qué efecto jurídico produce</h2><p>%s</p></section>
            <section class="ni-c"><h2>Qué ley lo sustenta</h2><p>%s %s</p>%s</section>
          </div>
          <section class="ni-desg"><h2>Qué trae por dentro</h2>%s</section>
        </div>''' % (
        _mdp0(x['montoMdp']), x['estado'], x['estado'], x['montoMdp'] / total * 100, x['grupo'], x['claveLIF'],
        glos('LIF (Ley de Ingresos de la Federación)', 'Ley de Ingresos de la Federación 2026, art. 1o.'),
        nota_ref('ref-lif2026', 10, 'Ley de Ingresos de la Federación 2026'), _mdp0(x['montoMdp']), _mdp0(total),
        'grava' if x['grupo'] == 'Impuestos' else 'es', x['quePaga'], x['efecto'], x['ley'],
        nota_ref(x['refKey'], r['num'], re.sub('<[^>]+>', '', r.get('cita_apa', ''))[:160].replace('"', '&quot;')),
        ('<p><a href="glosario.html#%s">📖 El concepto, en el glosario</a></p>' % glosario_ancla(term)) if term else '',
        desglose)
    return {
        'archivo': archivo, 'menu': x['nombre'], 'menu_archivo': 'sigue-el-dinero.html',
        'padre': ('sigue-el-dinero.html', 'Números'), 'padre2': ('numeros-presupuesto.html', 'Presupuesto'),
        'icono': x['icono'], 'lema': 'Presupuesto · Ley de Ingresos 2026',
        'titulo': x['nombreLargo'] if x['nombre'] in x['nombreLargo'] else '%s (%s)' % (x['nombreLargo'], x['nombre']),
        'entrada': re.sub('<[^>]+>', '', x['quePaga']),
        'estilos': ['numeros.css'], 'pie_extra': nav,
        'secciones': [{'id': 'ficha', 'titulo': x['nombre'], 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': bloque}],
    }


def numeros_modulo(m, tarjetas, bloque=None, script='presupuesto.js'):
    """Pagina de modulo de una parte de Numeros (11-10-2026): el bloque del
    motor a lo alto de su contenido, como los modulos de las herramientas.
    Con `bloque`, la pagina es propia y no carga el motor (los de
    «Presupuesto», presupuesto_modulos.py)."""
    ancla, archivo, ico, nombre, url, parte = m
    _, parch, pico, pnom = next(r for r in NUMEROS_PARTES if r[0] == parte)[:4]
    hermanos = [x for x in NUMEROS_MODULOS if x[5] == parte]
    i = hermanos.index(m)
    ant = hermanos[i - 1] if i > 0 else None
    sig = hermanos[i + 1] if i + 1 < len(hermanos) else None
    def paso(m, rot, cls):
        if not m:
            return '<a class="herr-mod-paso %s" href="%s"><small>%s</small><b>%s %s</b></a>' % (
                cls, parch, '← Volver a' if cls == 'ant' else 'Terminaste · volver a', pico, pnom)
        return '<a class="herr-mod-paso %s" href="%s"><small>%s</small><b>%s %s</b></a>' % (cls, m[1], rot, m[2], m[3])
    chips = ''.join('<a class="herr-mod-chip%s" href="%s"%s><span aria-hidden="true">%s</span> %s</a>' % (
        ' actual' if m[1] == archivo else '', m[1], ' aria-current="page"' if m[1] == archivo else '', m[2], m[3]) for m in hermanos)
    nav = ('<nav class="herr-mod-nav" aria-label="Más de %s">\n'
           '        <div class="herr-mod-pasos">\n          %s\n          %s\n        </div>\n'
           '        <span class="herr-otras-tit">Más de «%s»</span>\n'
           '        <div class="herr-mod-chips">%s</div>\n      </nav>' % (pnom, paso(ant, '← Anterior', 'ant'), paso(sig, 'Siguiente →', 'sig'), pnom, chips))
    marco = ('<div class="apartado-visor herr-modulo" style="--tarjeta: var(--rubro-dinero)">\n'
             '          <div class="apartado-visor-cuerpo">\n'
             '            <p class="apartado-visor-carga" role="status">⏳ Cargando el módulo con sus cifras y fuentes…</p>\n'
             '            <iframe class="apartado-visor-marco" title="%s" data-modulo="%s&amp;visor=1"></iframe>\n'
             '            <noscript><p>Este módulo necesita JavaScript. <a href="%s">Ábrelo en el auditor</a>.</p></noscript>\n'
             '          </div>\n'
             '        </div>' % (esc_attr(nombre), url, url))
    tarjeta = next((t for t in tarjetas if t[3] == archivo), None)
    p = {
        'archivo': archivo, 'menu': nombre, 'menu_archivo': 'sigue-el-dinero.html',
        'padre': ('sigue-el-dinero.html', 'Números'), 'padre2': (parch, pnom),
        'icono': ico, 'lema': pnom, 'titulo': nombre, 'entrada': tarjeta[2] if tarjeta else nombre,
        'pie_extra': nav + '\n\n      ' + numeros_nav(parch),
        'secciones': [{'id': ancla, 'titulo': nombre, 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': bloque or marco}],
    }
    if parte in ('origen', 'baja'):
        cuantas = {3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis'}.get(len(hermanos), str(len(hermanos)))
        p['pie_extra'] = presupuesto_pie(
            (ant[1], '← Anterior', ant[2], ant[3]) if ant else (parch, '← Volver a', pico, pnom),
            (sig[1], 'Siguiente →', sig[2], sig[3]) if sig else presupuesto_siguiente_parte(parte),
            (parch, '%s %s: sus %s tarjetas' % (pico, pnom, cuantas)) if ant else None)
    if bloque:
        p['estilos'] = ['numeros.css']
        p['scripts'] = list(script) if isinstance(script, (list, tuple)) else [script]
    return p


def paquete_paginas(p, partes, lista):
    """El Paquete Economico 2027 en diez paginas (pedido del autor,
    12-10-2026): su pagina queda con una tarjeta por seccion y cada seccion
    vive en la suya, con anterior y siguiente. Las anclas viejas
    (#peSim, #peSimTit...) llevan a su pagina."""
    p['pestanas'] = True
    p['pista'] = 'Cada tarjeta abre su propia página.'
    p['secciones'] = [{'id': x[0], 'pagina': x[2], 'pestana': (x[1], x[3], x[5])} for x in lista]
    p['hash_a_pagina'] = dict([(x[0], x[2]) for x in lista] + [(x[0] + 'Tit', x[2]) for x in lista] +
                              [('pe-ciego-*', next(x[2] for x in lista if x[0] == 'peCiegos'))])
    p['scripts'] = []
    out = []
    for i, (pid, ico, archivo, corto, desc, _) in enumerate(lista):
        titulo, html = partes[pid]
        ant = lista[i - 1] if i else None
        sig = lista[i + 1] if i + 1 < len(lista) else None
        out.append({
            'archivo': archivo, 'menu': corto, 'menu_archivo': 'sigue-el-dinero.html',
            'padre': ('sigue-el-dinero.html', 'Números'), 'padre2': p['padre2'], 'padre3': (p['archivo'], p['titulo']),
            'icono': ico, 'lema': p['titulo'], 'titulo': titulo, 'entrada': desc,
            'estilos': ['numeros.css'], 'scripts': ['presupuesto.js'] if pid == 'peSim' else [],
            'pie_extra': presupuesto_pie(
                (ant[2], '← Anterior', ant[1], ant[3]) if ant else (p['archivo'], '← Volver a', p['icono'], p['titulo']),
                (sig[2], 'Siguiente →', sig[1], sig[3]) if sig else (p['archivo'], 'Terminaste · volver a', p['icono'], p['titulo']),
                (p['archivo'], '%s %s: sus diez tarjetas' % (p['icono'], p['titulo'])) if ant else None),
            'secciones': [{'id': pid, 'titulo': titulo, 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': html}],
        })
    return out


def presupuesto_pie(ant, sig, arriba=None):
    """Pie de las paginas de «Presupuesto» (pedido del autor, 11-10-2026):
    solo anterior y siguiente, y un enlace para subir cuando el anterior no
    es ya la pagina de arriba. Sustituye a los chips «Mas de...» y a la
    barra de Numeros, que repetian los mismos destinos. Cada paso es
    (archivo, rotulo, icono, nombre)."""
    def paso(x, cls):
        if not x:
            return '<span></span>'
        return '<a class="herr-mod-paso %s" href="%s"><small>%s</small><b>%s %s</b></a>' % ((cls,) + x)
    sube = ('\n        <a class="np-saltos-arriba" href="%s">↑ %s</a>' % arriba) if arriba else ''
    return ('<nav class="herr-mod-nav np-saltos" aria-label="Anterior y siguiente">\n'
            '        <div class="herr-mod-pasos">\n          %s\n          %s\n        </div>%s\n      </nav>' % (
                paso(ant, 'ant'), paso(sig, 'sig'), sube))


def presupuesto_siguiente_parte(parte='origen'):
    """La parte de Numeros que sigue a `parte`."""
    ids = [r[0] for r in NUMEROS_PARTES]
    _, arch, ico, nom = NUMEROS_PARTES[ids.index(parte) + 1][:4]
    return (arch, 'Siguiente parte →', ico, nom)


def numeros_nav(actual):
    """Barra al pie de cada pagina de Numeros, con sus siete partes."""
    return ('<nav class="bib-nav" aria-label="Números">\n'
            '        <a class="bib-nav-tit" href="sigue-el-dinero.html">💰 Números: todas sus partes</a>\n'
            '        <div class="bib-nav-fila">\n%s\n        </div>\n      </nav>' % '\n'.join(
                '          <a class="bib-nav-a" href="%s"%s><span aria-hidden="true">%s</span><span>%s</span></a>'
                % (r[1], ' aria-current="page"' if r[1] == actual else '', r[2], r[3]) for r in NUMEROS_PARTES))


# «Gasto publico», dinamico (pedido del autor, 11-10-2026): quien lo aprueba
# (el ciclo, con los preceptos cotejados de preceptos_legales) y como se
# reparte (el simulador contable). Lo vuelve interactivo gasto-publico.js.
GP_CICLO = [
    # (id, icono, verbo, cuando, quien, que hace, preceptos, en los hechos)
    ('propone', '📨', 'Propone', 'A más tardar el 8 de septiembre', 'El Ejecutivo Federal, por la Secretaría de Hacienda',
     'Elabora y envía a la Cámara de Diputados el Paquete Económico: los Criterios Generales de Política Económica, la iniciativa de Ley de Ingresos y el proyecto de Presupuesto de Egresos. El secretario de Hacienda comparece a dar cuenta de ellos.',
     ['cpeum_art_74_iv', 'lfprh_art_42'],
     'La Gaceta Parlamentaria del 8 de septiembre de 2026 publica los Criterios Generales de Política Económica 2027, la pieza con que abre el paquete del año que viene. %s'),
    ('ingresos', '💵', 'Aprueba los ingresos', 'Diputados: a más tardar el 20 de octubre', 'El Congreso de la Unión: las dos Cámaras',
     'Decreta las contribuciones que cubrirán el gasto y da las bases para que el Ejecutivo pida prestado. La Ley de Ingresos fija cuánto se puede recaudar y el techo de la deuda del año.',
     ['cpeum_art_73', 'lfprh_art_42', 'lif_techo_endeudamiento'],
     'La Ley de Ingresos 2026 se publicó en el DOF el 7 de noviembre de 2025: autoriza %s de ingresos, deuda incluida, y un endeudamiento neto interno de hasta 1 billón 780 mil millones de pesos. %s'),
    ('gasto', '🗳️', 'Aprueba el gasto', 'A más tardar el 15 de noviembre', 'La Cámara de Diputados, sola',
     'Examina, discute y, en su caso, modifica el proyecto, y lo aprueba. Es su facultad exclusiva: el Senado no vota el Presupuesto de Egresos. No puede haber partidas secretas, y todo gasto que se agregue debe traer de dónde pagarse.',
     ['cpeum_art_74_iv', 'lfprh_art_17_18'],
     'El Presupuesto de Egresos 2026 se publicó en el DOF el 21 de noviembre de 2025, por %s. %s'),
    ('ejerce', '⚙️', 'Lo ejerce', 'Del 1 de enero al 31 de diciembre', 'El Ejecutivo, los Poderes Legislativo y Judicial y los órganos autónomos',
     'Gastan lo aprobado y nada más: ningún pago puede salir del presupuesto. El dinero se administra con eficiencia, eficacia, economía, transparencia y honradez, y las compras y obras se licitan por regla general.',
     ['cpeum_art_126', 'cpeum_art_134'],
     '2026 está en curso: sus cifras grandes, con su contador, están en <a href="numeros-cuanto-dinero-es.html">Cuánto dinero es</a>.'),
    ('cierra', '↩️', 'Cierra el año', '31 de diciembre, y 15 días después', 'Quien conserve dinero sin gastar',
     'Lo que no se devengó al 31 de diciembre ya no se puede gastar y se devuelve a la Tesorería de la Federación dentro de los 15 días naturales siguientes. Está prohibido gastar a última hora para no devolverlo.',
     ['lfprh_art_54'], ''),
    ('revisa', '🔍', 'Lo revisa', 'Al año siguiente', 'La Auditoría Superior de la Federación, de la Cámara de Diputados',
     'Fiscaliza después del gasto los ingresos, los egresos y la deuda, con autonomía técnica y de gestión.',
     ['cpeum_art_79'],
     'La revisión de la Cuenta Pública 2024, lo que se gastó de verdad y lo que quedó por aclarar, está en <a href="numeros-cuentas-claras.html">Cuentas claras</a>.'),
]

# Quien puede que (cada celda, con su articulo).
GP_QUIEN = [
    ('Ejecutivo Federal', ['Propone la iniciativa <small>(art. 74, fr. IV)</small>', 'Propone el proyecto y lo ejerce <small>(arts. 74, fr. IV, y 126)</small>',
                           'La contrata, por Hacienda, dentro del techo <small>(LIF 2026, art. 2o.)</small>', '—']),
    ('Cámara de Diputados', ['La aprueba, a más tardar el 20 de octubre <small>(LFPRH, art. 42, fr. IV)</small>', '<b>La aprueba sola</b>, a más tardar el 15 de noviembre <small>(art. 74, fr. IV)</small>',
                             'Da las bases y aprueba los empréstitos, como Congreso <small>(art. 73, fr. VIII)</small>', 'Por su Auditoría Superior <small>(art. 79)</small>']),
    ('Senado', ['La aprueba, como Congreso <small>(art. 73, fr. VII)</small>', '<b>No interviene</b>: es facultad exclusiva de Diputados <small>(art. 74, fr. IV)</small>',
                'Da las bases y aprueba los empréstitos, como Congreso <small>(art. 73, fr. VIII)</small>', '—']),
    ('Auditoría Superior', ['—', '—', '—', '<b>Fiscaliza</b> ingresos, egresos y deuda, en forma posterior <small>(art. 79)</small>']),
]

GP_COLOR = {'egr-social': '#1b7f4c', 'egr-economico': '#0f6f8f', 'egr-gobierno': '#6b3fa0', 'egr-poderes': '#9468c9',
            'egr-fondos': '#8a94a8', 'egr-costofin': '#b3261e', 'egr-participaciones': '#d0632a', 'egr-adefas': '#7a2a24'}


def egreso_archivo(x):
    """Pagina de un renglon del gasto: egr-social -> numeros-egreso-desarrollo-social.html."""
    return 'numeros-egreso-%s.html' % {
        'social': 'desarrollo-social', 'economico': 'desarrollo-economico', 'poderes': 'poderes-y-organos-autonomos',
        'fondos': 'fondos-de-estabilizacion', 'costofin': 'costo-financiero'}.get(x['id'][4:], x['id'][4:])


def gasto_ciclo(base):
    """«¿Quien lo aprueba?»: el ciclo del presupuesto, parada por parada."""
    pre = {x['id']: x for x in base['preceptos_legales']}
    refs = {r['id']: r for r in base['referencias_legales']}
    total = base['panoramaErario']['totalPEF']
    def ref(rid):
        r = refs[rid]
        return nota_ref(rid, r['num'], re.sub('<[^>]+>', '', r['cita_apa'])[:160].replace('"', '&quot;'))
    hechos = {'propone': ('%s', [ref('ref-cgpe2027')]), 'ingresos': ('%s %s', [_mdp(total), ref('ref-lif2026')]),
              'gasto': ('%s %s', [_mdp(total), ref('ref-pef2026')])}
    pasos, paneles = [], []
    for n, (cid, ico, verbo, cuando, quien, hace, ids, hecho) in enumerate(GP_CICLO):
        if cid in hechos:
            hecho = hecho % tuple(hechos[cid][1])
        citas = ''.join(
            '<blockquote class="gp-cita"><p class="gp-cita-cab"><b>%s</b> · %s %s</p><p>%s</p>'
            '<p class="gp-cita-pie">%s <a href="%s" rel="noopener" target="_blank">Texto oficial ↗</a> <span class="est-chip est-oficial">oficial</span></p></blockquote>'
            % (pre[i]['precepto'], pre[i]['ley'], ref(pre[i]['ref']), pre[i]['texto_oficial'], pre[i]['vigencia'], pre[i]['url_oficial'])
            for i in ids)
        pasos.append('<button type="button" class="gp-paso" role="tab" id="gpPaso-%s" aria-controls="gpPanel-%s" aria-selected="%s" data-i="%d">'
                     '<span class="gp-paso-n" aria-hidden="true">%s</span><b>%s</b><small>%s</small></button>'
                     % (cid, cid, 'true' if n == 0 else 'false', n, ico, verbo, cuando))
        paneles.append('<div class="gp-panel" role="tabpanel" id="gpPanel-%s" aria-labelledby="gpPaso-%s"%s>'
                       '<p class="gp-panel-cuando">%d de %d · %s</p><h3>%s %s: %s</h3><p class="gp-panel-hace">%s</p>%s%s</div>'
                       % (cid, cid, '' if n == 0 else ' data-oculto="1"', n + 1, len(GP_CICLO), cuando, ico, verbo, quien, hace,
                          ('<p class="gp-hecho"><b>En los hechos.</b> %s</p>' % hecho) if hecho else '', citas))
    filas = ''.join('<tr><th scope="row">%s</th>%s</tr>' % (q, ''.join('<td>%s</td>' % c for c in celdas)) for q, celdas in GP_QUIEN)
    return '''<section class="gp gp-ciclo" id="gpAprueba" aria-labelledby="gpApruebaTit">
          <h2 class="gp-tit sr-only" id="gpApruebaTit">¿Quién lo aprueba? El ciclo del presupuesto</h2>
          <p class="gp-txt">Cada peso del presupuesto recorre estas seis paradas, del proyecto a la revisión. Cada una tiene a su autoridad, su fecha límite y el artículo que le da la facultad, citado tal como lo dice la ley. Toca una parada o avanza con las flechas.</p>
          <div class="gp-ruta" role="tablist" aria-label="Las seis paradas del presupuesto">%s</div>
          <div class="gp-mando"><button type="button" class="gp-flecha" data-dir="-1" aria-label="Parada anterior">←</button>
            <span class="gp-prog" aria-hidden="true"><span></span></span>
            <button type="button" class="gp-flecha" data-dir="1" aria-label="Parada siguiente">→</button></div>
          %s
          <h3 class="gp-sub">Quién puede qué</h3>
          <div class="gp-tabla-caja"><table class="gp-tabla">
            <thead><tr><th scope="col">Autoridad</th><th scope="col">Ley de Ingresos</th><th scope="col">Presupuesto de Egresos</th><th scope="col">Deuda</th><th scope="col">Revisión</th></tr></thead>
            <tbody>%s</tbody></table></div>
          <p class="np-pie">Los artículos sin ley son de la Constitución Política %s; LFPRH es la Ley Federal de Presupuesto y Responsabilidad Hacendaria %s. Textos cotejados con su fuente oficial.</p>
        </section>''' % ('\n'.join(pasos), '\n'.join(paneles), filas, ref('ref-cpeum'), ref('ref-lfprh'))


def gasto_reparte(base, d):
    """«¿Como se reparte?»: el simulador contable. Del total a lo
    programable y lo no programable, y de ahi a sus ocho renglones; y una
    cantidad cualquiera repartida en la misma proporcion."""
    p = base['panoramaErario']
    total = p['totalPEF']
    refs = {r['id']: r for r in base['referencias_legales']}
    def ref(rid):
        r = refs[rid]
        return nota_ref(rid, r['num'], re.sub('<[^>]+>', '', r['cita_apa'])[:160].replace('"', '&quot;'))
    eg = p['egresos']
    prog = [x for x in eg if x['grupo'] == 'Programable']
    nopr = [x for x in eg if x['grupo'] == 'No programable']
    sp, sn = round(sum(x['montoMdp'] for x in prog), 1), round(sum(x['montoMdp'] for x in nopr), 1)
    redondeo = round(total - sp - sn, 1)
    datos = {'total': total, 'redondeo': redondeo, 'grupos': [
        {'id': 'prog', 'nom': 'Gasto programable', 'v': sp, 'est': 'derivado', 'color': '#0b2a63',
         'que': 'Lo que compra bienes y presta servicios a la población: escuelas, hospitales, pensiones, carreteras, seguridad, el funcionamiento de los Poderes.',
         'op': 'Suma de las %d finalidades del gasto programable de los Criterios 2027.' % len(prog)},
        {'id': 'nopr', 'nom': 'Gasto no programable', 'v': sn, 'est': 'derivado', 'color': '#8f1d17',
         'que': 'Lo que ya está comprometido antes de empezar: intereses de la deuda, lo que les toca a estados y municipios y las cuentas del año anterior.',
         'op': 'Costo financiero + participaciones (Ramo 28) + ADEFAS (Ramo 30) del PEF 2026.'}],
        'renglones': [{'id': x['id'], 'g': 'prog' if x['grupo'] == 'Programable' else 'nopr', 'nom': x['nombre'], 'ico': x['icono'],
                       'v': x['montoMdp'], 'est': x['estado'], 'que': x['queCubre'], 'color': GP_COLOR[x['id']], 'p': egreso_archivo(x)}
                      for x in prog + nopr]}
    def seg(x, nivel):
        return ('<button type="button" class="gp-seg" data-id="%s" data-nivel="%d" style="--w:%.4f;--c:%s" aria-pressed="false">'
                '<span class="gp-seg-tx"><b>%s</b><span>%s</span></span></button>'
                % (x['id'], nivel, x['v'] / total * 100, x['color'], x['nom'], _bill(x['v'])))
    filas_rep = ''.join(
        '<li class="gp-rep-f" data-v="%s" style="--c:%s"><a href="%s"><span aria-hidden="true">%s</span> %s</a>'
        '<span class="gp-rep-barra"><span></span></span><b class="gp-rep-m">$0.00</b></li>'
        % (x['v'], x['color'], x['p'], x['ico'], x['nom']) for x in datos['renglones'])
    # Desde el 12-10-2026 el simulador y «Si el presupuesto fuera de…»
    # viven en paginas distintas: cada una lleva su copia de #gpDatos.
    jdatos = json.dumps(datos, ensure_ascii=False).replace('</', '<\\/')
    return ('''<section class="gp gp-reparte" id="gpReparte" aria-labelledby="gpReparteTit">
          <h2 class="gp-tit sr-only" id="gpReparteTit">¿Cómo se reparte? El simulador contable</h2>
          <p class="gp-txt">El gasto neto total de 2026 es de <b>%s</b> %s. Pulsa «Contabilizar» y míralo partirse: primero en lo que se programa y lo que ya está comprometido; después, en sus ocho renglones. Toca cualquier tramo para ver qué es; cada renglón tiene su propia página.</p>
          <div class="gp-cont">
            <button type="button" class="gp-boton" id="gpContar" aria-pressed="false">▶ Contabilizar</button>
            <p class="gp-cifra" aria-live="polite"><b id="gpTotal">$0.0 mdp</b><small id="gpEstado">El presupuesto está en ceros.</small></p>
          </div>
          <div class="gp-ici" id="gpIci">
            <div class="gp-nivel" data-nivel="0"><span class="gp-nivel-tit">Total</span><div class="gp-barra">%s</div></div>
            <div class="gp-nivel" data-nivel="1"><span class="gp-nivel-tit">Tipo de gasto</span><div class="gp-barra">%s</div></div>
            <div class="gp-nivel" data-nivel="2"><span class="gp-nivel-tit">Renglones</span><div class="gp-barra">%s</div></div>
          </div>
          <div class="gp-det" id="gpDet" aria-live="polite"><p class="gp-det-vacio">👆 Toca un tramo de las barras.</p></div>
          <p class="np-pie">Los ocho renglones suman %s; los %s que faltan para el total son redondeo de la fuente, que publica la clasificación funcional en miles de millones. Cifras de la clasificación funcional de los Criterios 2027 %s y del PEF 2026 %s.</p>
          <script type="application/json" id="gpDatos">%s</script>
          <noscript><p>El simulador necesita JavaScript. Los ocho renglones, con su cifra y su fuente, están en sus páginas.</p></noscript>
        </section>''' % (
        _mdp(total), ref('ref-pef2026'),
        seg({'id': 'total', 'nom': 'Gasto neto total', 'v': total, 'color': '#33415c'}, 0),
        ''.join(seg(g, 1) for g in datos['grupos']), ''.join(seg(x, 2) for x in datos['renglones']),
        _mdp(sp + sn), _mdp(redondeo), ref('ref-cgpe2027'), ref('ref-pef2026'), jdatos),
        '''<section class="gp gp-reparte gp-fuera" id="gpFuera" aria-labelledby="gpFueraTit">
          <h2 class="gp-tit sr-only" id="gpFueraTit">Si el presupuesto fuera de…</h2>
          <p class="gp-txt">Escribe una cantidad y mira cómo se repartiría en la misma proporción que el presupuesto aprobado para 2026, de <b>%s</b>. No es lo que pagas tú de impuestos (para eso está la <a href="herramienta-calculadora.html">Calculadora Cívica</a>): es la forma del gasto, en pequeño.</p>
          <div class="gp-rep-mando">
            <label for="gpMonto">Cantidad en pesos</label>
            <input type="number" id="gpMonto" min="0" step="1" value="100" inputmode="numeric">
            <span class="gp-rep-atajos">%s</span>
          </div>
          <ol class="gp-rep" id="gpRep">%s</ol>
          <p class="np-pie" id="gpRepPie">Operación: cantidad × (renglón ÷ %s) <span class="est-chip est-derivado">derivado</span>. Los ocho renglones suman %s; los %s que faltan para el total son redondeo de la fuente, que publica la clasificación funcional en miles de millones. Cifras de la clasificación funcional de los Criterios 2027 %s y del PEF 2026 %s.</p>
          <script type="application/json" id="gpDatos">%s</script>
          <noscript><p>La cuenta necesita JavaScript. Los ocho renglones, con su cifra y su fuente, están en sus páginas.</p></noscript>
        </section>''' % (
        _mdp(total), ''.join('<button type="button" data-monto="%d">$%s</button>' % (m, format(m, ',')) for m in (100, 1000, 10000, 1000000)),
        filas_rep, _mdp(total), _mdp(sp + sn), _mdp(redondeo), ref('ref-cgpe2027'), ref('ref-pef2026'), jdatos))


# «Gasto publico» en tarjetas (pedido del autor, 12-10-2026): su pagina
# queda solo con tarjetas, en dos grupos, y cada una abre la suya. Las cuatro
# primeras eran secciones de la misma pagina; las cinco de desglose ya
# tenian pagina (NUMEROS_MODULOS y el simulador de Herramientas).
# (id, icono, archivo, nombre de la tarjeta, descripcion breve, titulo, entrada, grupo)
GASTO_GRUPOS = {'como': '🗺️ Cómo se aprueba y cómo se reparte', 'desg': '🔎 Los desgloses'}
GASTO_PARTES = [
    ('gpAprueba', '🗳️', 'numeros-gasto-quien-lo-aprueba.html', '¿Quién lo aprueba?', 'Las seis paradas del presupuesto y quién puede qué',
     '¿Quién lo aprueba? El ciclo del presupuesto',
     'Del proyecto de Hacienda a la revisión de la Auditoría Superior: cada parada del presupuesto, con su autoridad, su fecha límite y el artículo que le da la facultad.', 'como'),
    ('gpReparte', '🧮', 'numeros-gasto-simulador-contable.html', 'El simulador contable', 'Mira partirse los $10.19 billones, del total a sus ocho renglones',
     '¿Cómo se reparte? El simulador contable',
     'El gasto de 2026, contabilizado desde cero: primero en lo que se programa y lo ya comprometido, después en sus ocho renglones, cada uno con su página.', 'como'),
    ('gpFuera', '🪙', 'numeros-gasto-si-fuera-de.html', 'Si el presupuesto fuera de…', 'Escribe una cantidad y mírala repartirse igual',
     'Si el presupuesto fuera de…',
     'Una cantidad cualquiera, repartida en la misma proporción que el presupuesto aprobado: la forma del gasto, en pequeño.', 'como'),
    # «Los tres presupuestos» se mudo a «Presupuesto» (24-10-2026): NUMEROS_MODULOS.
    ('reparte', '🎛️', 'simulador-presupuesto.html', 'Reparte tú el presupuesto', 'Arranca en $0, reparte los $10.19 billones y compáralo', None, None, 'desg'),
    ('poderes', '⚖️', 'numeros-lo-que-cuestan-los-poderes.html', 'Lo que cuestan el Congreso y la Judicatura', 'Presupuesto 2026, gasto auditado 2024 y sueldos netos', None, None, 'desg'),
    ('eb-egresos', '🏢', 'numeros-ramos-y-dependencias.html', 'En qué se va: ramos y dependencias', 'Cuánto recibe cada Secretaría, ramo por ramo', None, None, 'desg'),
    ('eb-salud', '🌡️', 'numeros-margen-del-presupuesto.html', '¿Cuánto margen tiene el presupuesto?', 'Lo ya comprometido antes de empezar, en un termostato', None, None, 'desg'),
    ('eb-ciegos', '🔦', 'numeros-lo-que-la-cifra-no-dice.html', 'Lo que la cifra grande no dice', 'Cinco lecturas que cambian el sentido del total', None, None, 'desg'),
]


# «Cuentas claras» en tarjetas (pedido del autor, 12-10-2026), como «Gasto
# publico»: la grafica de la deuda se parte en tres paginas; el estado de
# resultados y el Estado de Cuenta Civico se quedan (no hay otro igual en la
# plataforma). Las tres que ya son herramientas (la ASF, los Expedientes y el
# reloj de la deuda) tuvieron su grupo de enlaces y se quitaron el mismo dia:
# viven solo en Herramientas (pedido del autor).
CUENTAS_GRUPOS = {'debe': '📉 Lo que se debe', 'revisa': '🔍 Lo que se gastó y el balance'}
CUENTAS_PARTES = [
    ('dtTiempo', '📈', 'numeros-cuentas-deuda-en-el-tiempo.html', 'La deuda en el tiempo', 'De 1994 a 2027, sexenio por sexenio, con su contador',
     'La deuda a través del tiempo',
     'Lo que el país debe, de 1994 a la proyección de 2027, como parte del PIB o en billones de pesos. Pulsa «Contabilizar» y mírala crecer, recorre los años o toca un sexenio.', 'debe'),
    ('dtReglas', '⚖️', 'numeros-cuentas-quien-autoriza-la-deuda.html', '¿Quién autoriza la deuda?', 'El Congreso da las bases y la Ley de Ingresos pone el tope',
     '¿Quién autoriza la deuda?',
     'Tres reglas sostienen cada peso que se pide prestado: las bases que da el Congreso, el tope de cada año en la Ley de Ingresos y la ley con que Hacienda la contrata.', 'debe'),
    ('dtAntes', '👑', 'numeros-cuentas-antes-de-1994.html', 'Antes de 1994', 'El Porfiriato y la deuda externa de 1988 a 1994',
     'Antes de la serie: el Porfiriato y la deuda externa de 1988 a 1994',
     'Lo que hay antes de la serie comparable: el primer superávit del Porfiriato y la deuda externa que seguía el libro de 1995, cotejada con Banxico.', 'debe'),
    ('eb-cuenta-federal', '📒', 'numeros-estado-de-resultados.html', 'El estado de resultados del Gobierno', 'La Cuenta Pública 2024 leída como un negocio',
     None, None, 'revisa'),
    ('estado-de-cuenta', '🧭', 'estado-de-cuenta.html', 'Contexto dimensional', 'Seis dimensiones: 2024 frente a 2026 y 2027', None, None, 'revisa'),
]
# Paginas que una tarjeta abre pero que no entran en la fila de anterior y
# siguiente: son de Herramientas y tienen su propio pie.
FUERA_DE_FILA = {'simulador-presupuesto.html'}


def partes_portada(p, partes, grupos, entrada, extra_hash=()):
    """Una parte de Numeros queda solo con tarjetas, en grupos con su titulo
    (Gasto publico y Cuentas claras, 12-10-2026); cada una abre su pagina."""
    p.update({'pestanas': True, 'pista': 'Cada tarjeta abre su propia página.', 'scripts': [], 'pie_extra': '', 'entrada': entrada})
    p['secciones'] = [dict({'id': x[0], 'pagina': x[2], 'pestana': (x[1], x[3], x[4])},
                           **({'grupo': grupos[x[7]]} if i == 0 or partes[i - 1][7] != x[7] else {}))
                      for i, x in enumerate(partes)]
    # Las anclas de cuando todo vivia en esta pagina llevan a la suya.
    nuevas = [x for x in partes if x[5]]
    p['hash_a_pagina'] = dict([(x[0], x[2]) for x in nuevas] + [(x[0] + 'Tit', x[2]) for x in nuevas] + list(extra_hash))


def partes_paginas(partes, html, padre2, lema, scripts):
    """Las paginas nuevas de una parte (las que traen titulo y entrada)."""
    return [{
        'archivo': archivo, 'menu': corto, 'menu_archivo': 'sigue-el-dinero.html',
        'padre': ('sigue-el-dinero.html', 'Números'), 'padre2': padre2,
        'icono': ico, 'lema': lema, 'titulo': titulo, 'entrada': entrada,
        'estilos': ['numeros.css'], 'scripts': scripts.get(pid, []),
        'secciones': [{'id': pid + '-pag', 'titulo': titulo, 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': html[pid]}],
    } for pid, ico, archivo, corto, _, titulo, entrada, _ in partes if titulo]


def partes_fila(partes):
    return [x for x in partes if x[7] != 'herr' and x[2] not in FUERA_DE_FILA]


def partes_pie(partes, archivo, portada, fin):
    """Anterior y siguiente de `archivo` en la fila de su parte. `portada` es
    (archivo, icono, nombre) de la pagina de tarjetas; `fin`, el paso que
    sigue a la ultima."""
    fila = partes_fila(partes)
    i = [x[2] for x in fila].index(archivo)
    ant = fila[i - 1] if i else None
    sig = fila[i + 1] if i + 1 < len(fila) else None
    return presupuesto_pie(
        (ant[2], '← Anterior', ant[1], ant[3]) if ant else (portada[0], '← Volver a', portada[1], portada[2]),
        (sig[2], 'Siguiente →', sig[1], sig[3]) if sig else fin,
        (portada[0], '%s %s: sus %s tarjetas' % (portada[1], portada[2], {5: 'cinco', 8: 'ocho', 9: 'nueve'}.get(len(partes), len(partes)))) if ant else None)


def partes_pies(partes, portada, fin):
    por = {q['archivo']: q for q in NUMEROS_PAGINAS}
    for x in partes_fila(partes):
        if x[2] in por:  # estado-de-cuenta.html lo pone su propio generador
            por[x[2]]['pie_extra'] = partes_pie(partes, x[2], portada, fin)


CUENTAS_PORTADA = ('numeros-cuentas-claras.html', '⚖️', 'Cuentas claras')
CUENTAS_FIN = ('sigue-el-dinero.html', 'Terminaste · volver a', '💰', 'Números')


def egreso_pagina(x, n, lista, total, refs, glosario):
    """Pagina propia de un renglon del gasto (11-10-2026), como las del ingreso."""
    archivo = egreso_archivo(x)
    r = refs[x['refKey']]
    comps = x.get('componentes') or []
    if comps:
        mayor = max(abs(c['m']) for c in comps)
        desglose = ('<ol class="ni-comps">%s</ol>' % ''.join(
            '<li class="%s"><span class="ni-comp-n">%s%s</span><span class="nr-barra"><span class="nr-relleno" style="width:%.2f%%"></span></span>'
            '<b>%s</b><span class="nr-pct">%s%%</span></li>' % (
                'ni-cero' if c['m'] == 0 else '', c['n'], ('<small>%s</small>' % c['d']) if c['d'] else '',
                abs(c['m']) / mayor * 100 if mayor else 0, _mdp0(c['m']), format(c['m'] / x['montoMdp'] * 100, '.1f')) for c in comps)
            + '<p class="np-pie">El desglose lo trae el propio decreto (%s). El porcentaje es la parte de cada componente en el total del renglón.</p>' % x['clave'])
    else:
        desglose = ''
    term = x['glos'] if x['glos'] in glosario else None
    ant, sig = (lista[n - 1] if n > 0 else None), (lista[n + 1] if n + 1 < len(lista) else None)
    def paso(y, rot, cls):
        if not y:
            return '<a class="herr-mod-paso %s" href="numeros-gasto-simulador-contable.html"><small>%s</small><b>🧮 El simulador contable</b></a>' % (
                cls, '← Volver a' if cls == 'ant' else 'Terminaste · volver a')
        return '<a class="herr-mod-paso %s" href="%s"><small>%s</small><b>%s %s</b></a>' % (cls, egreso_archivo(y), rot, y['icono'], y['nombre'])
    chips = ''.join('<a class="herr-mod-chip%s" href="%s"%s><span aria-hidden="true">%s</span> %s</a>' % (
        ' actual' if y is x else '', egreso_archivo(y), ' aria-current="page"' if y is x else '', y['icono'], y['nombre']) for y in lista)
    nav = ('<nav class="herr-mod-nav" aria-label="Los ocho renglones del gasto">\n'
           '        <div class="herr-mod-pasos">\n          %s\n          %s\n        </div>\n'
           '        <span class="herr-otras-tit">Los ocho renglones del gasto</span>\n'
           '        <div class="herr-mod-chips">%s</div>\n      </nav>' % (
               paso(ant, '← Anterior', 'ant'), paso(sig, 'Siguiente →', 'sig'), chips))
    extra = ''
    if x.get('comoSeObtuvo'):
        extra += '<section class="ni-desg"><h2>Cómo se obtuvo la cifra</h2><p>%s</p></section>' % x['comoSeObtuvo']
    if x.get('pendiente'):
        extra += '<section class="ni-desg"><h2>Lo que el decreto no dice</h2><p>%s</p></section>' % x['pendiente']
    bloque = '''<div class="ni" style="--c:%s">
          <div class="ni-cifra">
            <p class="ni-monto"><b>%s</b> <span class="est-chip est-%s">%s</span></p>
            <p class="ni-datos"><span>De cada $100 que se gastan: <b>$%.2f</b> <span class="est-chip est-derivado">derivado</span></span>
            <span>Tipo: <b>gasto %s</b></span><span>Dónde está: <b>%s</b></span></p>
            <p class="np-pie">«De cada $100» = %s ÷ %s × 100.</p>
          </div>
          <div class="ni-rej">
            <section class="ni-c"><h2>¿Qué cubre?</h2><p>%s</p></section>
            <section class="ni-c"><h2>Qué ley lo sustenta</h2><p>%s %s</p>%s</section>
          </div>
          <section class="ni-desg"><h2>Por qué importa</h2><p>%s</p></section>
          %s%s
        </div>''' % (
        GP_COLOR[x['id']], _mdp0(x['montoMdp']), x['estado'], x['estado'], x['montoMdp'] / total * 100, x['grupo'].lower(), x['clave'],
        _mdp0(x['montoMdp']), _mdp0(total), x['queCubre'], x['ley'],
        nota_ref(x['refKey'], r['num'], re.sub('<[^>]+>', '', r.get('cita_apa', ''))[:160].replace('"', '&quot;')),
        ('<p><a href="glosario.html#%s">📖 El concepto, en el glosario</a></p>' % glosario_ancla(term)) if term else '',
        x['efecto'], ('<section class="ni-desg"><h2>Qué trae por dentro</h2>%s</section>' % desglose) if desglose else '', extra)
    return {
        'archivo': archivo, 'menu': x['nombre'], 'menu_archivo': 'sigue-el-dinero.html',
        'padre': ('sigue-el-dinero.html', 'Números'), 'padre2': ('numeros-gasto-publico.html', 'Gasto público'),
        'icono': x['icono'], 'lema': 'Gasto público · Presupuesto de Egresos 2026',
        'titulo': x['nombreLargo'], 'entrada': re.sub('<[^>]+>', '', x['queCubre']),
        'estilos': ['numeros.css'], 'pie_extra': nav + '\n\n      ' + numeros_nav('numeros-gasto-publico.html'),
        'secciones': [{'id': 'ficha', 'titulo': x['nombre'], 'texto': '', 'sin_cab': True, 'tarjetas': [], 'bloque': bloque}],
    }

def numeros_preparar():
    if NUMEROS_PAGINAS:
        return
    import auditorias
    base = auditorias.db()
    d = numeros_datos(base)
    pag = {r[0]: r for r in NUMEROS_PARTES}
    pag['decide'] = pag['gasta']  # «Se aprueba» vive en «Gasto publico»
    pag['deuda'] = pag['revisa'] = pag['cuentas']  # y la deuda, en «Cuentas claras»
    for x in d['entra'] + d['sale']:
        # «Ver ...» de cada tramo lleva a su pagina; los de lo que entra,
        # a sus renglones, en la misma pagina.
        if x['paso'] == 'origen':
            x['ptit'], x['paso'] = 'Los 16 orígenes, renglón por renglón', 'numeros-los-16-origenes.html'
        else:
            x['ptit'] = pag[x['paso']][3]
            x['paso'] = pag[x['paso']][1]
        x.pop('pnum', None)
    ingresos = base['panoramaErario']['ingresos']
    por_nombre = {r['nombre']: r for r in ingresos}
    for x in d['entra']:
        for f in x['filas']:
            # Cada renglon de lo que entra abre su pagina (11-10-2026).
            f['p'] = ingreso_archivo(por_nombre[f['n']])
    eg_nombre = {r['nombre']: r for r in base['panoramaErario']['egresos']}
    for x in d['sale']:
        for f in x['filas']:
            if f['n'] in eg_nombre:
                f['p'] = egreso_archivo(eg_nombre[f['n']])
    a = next(x for x in APARTADOS if x['archivo'] == 'sigue-el-dinero.html')
    pasos = {sec['id']: sec for sec in a['secciones']}
    contable, fuera = gasto_reparte(base, d)
    gasto_html = {'gpAprueba': gasto_ciclo(base), 'gpReparte': contable, 'gpFuera': fuera}
    # La nota del libro va al pie de cada paso, no en la portada.
    comun = {k: a.pop(k) for k in ('libro', 'libro_ref', 'libro_glosario')}
    for pid, archivo, ico, nombre, desc in NUMEROS_PARTES:
        p = {'archivo': archivo, 'menu': nombre, 'menu_archivo': 'sigue-el-dinero.html',
             'padre': ('sigue-el-dinero.html', 'Números'), 'icono': ico, 'lema': 'Números',
             'estilos': ['numeros.css'], 'pie_extra': numeros_nav(archivo)}
        sec = dict(pasos[pid], sin_cab=True)
        sec.pop('num', None)
        # «Presupuesto» y «Baja al territorio» ya no llevan la nota del
        # libro: vive en el Diccionario (pedidos del autor, 11-10-2026).
        # Ni «Gasto publico» ni «Cuentas claras» (12-10-2026): el «Ayer y hoy»
        # del primero paso a las Preguntas frecuentes; el del segundo ya lo
        # cuentan sus paginas «Antes de 1994» y «¿Quien autoriza la deuda?».
        con_libro = False
        if con_libro:
            p.update(comun)
        p.update({'titulo': sec['titulo'], 'entrada': sec['texto'], 'libro_pie': con_libro, 'secciones': [sec]})
        # ?abrir=eb-bloque que llegue aqui (de una pagina vieja) va a su pagina.
        p['abrir_a_pagina'] = NUMEROS_ABRIR
        if pid == 'origen':
            # «El peso de 2026» y «Los 16 origenes» vivian aqui; desde el
            # 11-10-2026 tienen su pagina y sus anclas viejas llevan alla.
            p['hash_a_pagina'] = {'numPeso': 'numeros-cuanto-dinero-es.html#numPeso', 'nrRenglones': 'numeros-los-16-origenes.html'}
            # Solo las tarjetas, sin saltos al pie (pedido del autor, 11-10-2026).
            p['pie_extra'] = ''
        if pid == 'baja':
            # Igual que «Presupuesto»: solo sus tres tarjetas (11-10-2026).
            p['pie_extra'] = ''
        if pid == 'gasta':
            # Solo sus tarjetas, en dos grupos; cada una abre su pagina
            # (pedido del autor, 12-10-2026). partes_paginas() arma las cuatro
            # nuevas; las cinco de desglose ya la tenian.
            partes_portada(p, GASTO_PARTES, GASTO_GRUPOS,
                           'La Cámara de Diputados aprueba cada año el Presupuesto de Egresos y, con él, en qué se va cada peso. '
                           'Arriba, cómo se aprueba y cómo se reparte; abajo, cada desglose. Cada tarjeta abre su propia página.',
                           [('gpContar', GASTO_PARTES[1][2]), ('gpMonto', GASTO_PARTES[2][2]), ('gpRep', GASTO_PARTES[2][2]),
                            ('gpTres', 'numeros-gasto-tres-presupuestos.html'), ('gpTresTit', 'numeros-gasto-tres-presupuestos.html')])
            p['cierre'] = ('<p class="gp-pie-herr">🧰 ¿Buscas la inversión pública y las megaobras, o el costo ambiental? Son herramientas y viven en '
                           '<a href="herramienta-megaobras.html">Herramientas · Megaobras</a> y <a href="herramienta-ambiente.html">Herramientas · Costo ambiental</a>.</p>')
        if pid == 'cuentas':
            # Solo sus tarjetas, en tres grupos (pedido del autor, 12-10-2026).
            partes_portada(p, CUENTAS_PARTES, CUENTAS_GRUPOS,
                           'El recorrido se cierra con dos cuentas: lo que el país debe, sexenio por sexenio, y la rendición, '
                           'cuando el gobierno entrega la Cuenta Pública y la Auditoría Superior de la Federación la revisa. '
                           'Cada tarjeta abre su propia página.',
                           [('deudaTiempo', CUENTAS_PARTES[0][2])])
            # Sin cierre: «¿Y a ti, cuanto te toca?» y las tarjetas de la ASF,
            # los Expedientes y el reloj viven solo en Herramientas (pedido
            # del autor, 12-10-2026).
        for t in sec['tarjetas']:
            m = re.search(r'ancla=(eb-[\w-]+)', t[3])
            if m:
                NUMEROS_ABRIR.setdefault(m.group(1), archivo + '?abrir=' + m.group(1))
        NUMEROS_PAGINAS.append(p)
    # El desglose del ingreso y las vistas del motor, a su pagina.
    NUMEROS_ABRIR['eb-ingresos'] = 'numeros-los-16-origenes.html'
    refs = {r['id']: r for r in base['referencias_legales']}
    # Los cuatro modulos de «Presupuesto», en pagina propia y sin el motor
    # (pedido del autor, 11-10-2026): se abrian en un marco y tardaban.
    import presupuesto_modulos as pm
    def ref(rid):
        r = refs[rid]
        return nota_ref(rid, r['num'], re.sub('<[^>]+>', '', r['cita_apa'])[:160].replace('"', '&quot;'))
    # «Cuanto dinero es» lleva dentro las dos barras de «El peso de 2026».
    propios = {'gp-tres': lambda: '<section class="gp gp-tres" id="gpTres" aria-labelledby="gpTresTit"><h2 class="gp-tit sr-only" id="gpTresTit">¿Hacia dónde va? Los tres presupuestos</h2>\n        ' + numeros_tres(d) + '</section>',
               'eb-cuanto': lambda: pm.cuanto(base, ref, numeros_peso(d),
                                              (RADAR_HOY_CUENTA, RADAR_HOY_FILAS[2:], radar_hoy_vivo(base))),
               'eb-equivale': lambda: pm.equivale(base, ref),
               'eb-arquitectura': lambda: pm.camino(base, ref),
               # El titulo del bloque ya es el de la pagina: queda solo para lectores de pantalla.
               'nr-origenes': lambda: numeros_renglones(base, d).replace('class="np-tit" id="nrTit"', 'class="np-tit sr-only" id="nrTit"'),
               # Los tres de «Baja al territorio» (11-10-2026).
               'eb-mapa': lambda: tm.mapa(base, ref, RAIZ),
               'territorio': lambda: tm.entidades(base, ref, glos),
               'municipios': lambda: tm.municipios(base, ref, glos, RAIZ),
               # El estado de resultados, en pagina propia y sin el motor (12-10-2026).
               'eb-cuenta-federal': lambda: rm.construir(base, ref, glos),
               # Tres desgloses de «Gasto publico», igual (12-10-2026): gasto_modulos.py.
               'eb-salud': lambda: gm.margen(base, ref, glos),
               'eb-egresos': lambda: gm.egresos(base, ref, glos),
               'eb-ciegos': lambda: gm.ciegos(base, ref, glos),
               'poderes': lambda: pdm.construir(base, ref, glos)}
    import territorio_modulos as tm
    import resultados_modulo as rm
    import gasto_modulos as gm
    import poderes_modulo as pdm
    guion = {'gp-tres': [], 'eb-cuenta-federal': 'resultados.js', 'eb-salud': [], 'eb-egresos': [], 'eb-ciegos': [], 'poderes': [], 'eb-cuanto': ['numeros.js', 'radar.js'], 'nr-origenes': 'numeros.js', 'eb-mapa': 'territorio.js', 'territorio': 'territorio.js',
             'municipios': ['municipios-efipem.js', 'territorio.js']}
    for m in NUMEROS_MODULOS:
        NUMEROS_ABRIR[m[0]] = m[1]
        hecho = propios.get(m[0])
        NUMEROS_PAGINAS.append(numeros_modulo(m, pasos[m[5]]['tarjetas'], hecho() if hecho else None,
                                              guion.get(m[0], 'presupuesto.js')))
        # Las cifras de «Hoy» del Radar, con su contador (12-10-2026), traen sus estilos.
        if m[0] == 'eb-cuanto':
            NUMEROS_PAGINAS[-1]['estilos'] = NUMEROS_PAGINAS[-1]['estilos'] + ['radar.css']
        if m[0] == 'poderes':
            NUMEROS_PAGINAS[-1]['estilos'] = NUMEROS_PAGINAS[-1]['estilos'] + ['poderes.css']
        if m[0] == 'proyeccion2027':
            NUMEROS_PAGINAS.extend(paquete_paginas(NUMEROS_PAGINAS[-1], pm.paquete_partes(base, ref), pm.PE_PARTES))
    NUMEROS_PAGINAS.extend(partes_paginas(GASTO_PARTES, gasto_html, ('numeros-gasto-publico.html', 'Gasto público'), 'Gasto público',
                                          {'gpAprueba': ['gasto-publico.js'], 'gpReparte': ['gasto-publico.js'], 'gpFuera': ['gasto-publico.js']}))
    partes_pies(GASTO_PARTES, ('numeros-gasto-publico.html', '🏛️', 'Gasto público'), presupuesto_siguiente_parte('gasta'))
    deuda = {pid: '<div class="dt" id="deudaTiempo" data-parte="%s">\n          <noscript><p>%s necesita JavaScript.</p></noscript>\n        </div>' % (dp, q)
             for pid, dp, q in (('dtTiempo', 'tiempo', 'La línea de tiempo'), ('dtReglas', 'reglas', 'Esta página'), ('dtAntes', 'antes', 'Esta página'))}
    NUMEROS_PAGINAS.extend(partes_paginas(CUENTAS_PARTES, deuda, CUENTAS_PORTADA[0::2], 'Cuentas claras',
                                          {k: ['deuda-tiempo.js'] for k in deuda}))
    partes_pies(CUENTAS_PARTES, CUENTAS_PORTADA, CUENTAS_FIN)
    glosario = set(t['termino'] for t in base['glosario'])
    total = base['panoramaErario']['totalLIF']
    for n, x in enumerate(ingresos):
        NUMEROS_PAGINAS.append(ingreso_pagina(x, n, ingresos, total, refs, glosario))
    # Y cada renglon del gasto, la suya (11-10-2026).
    egresos = base['panoramaErario']['egresos']
    for n, x in enumerate(egresos):
        NUMEROS_PAGINAS.append(egreso_pagina(x, n, egresos, base['panoramaErario']['totalPEF'], refs, glosario))
    # La portada: solo las tarjetas, cada una a su pagina.
    a['secciones'] = [{'id': r[0], 'pagina': r[1], 'pestana': (r[2], r[3], r[4])} for r in NUMEROS_PARTES]
    # Las anclas de cuando todo vivia en esta pagina llevan a la suya.
    a['hash_a_pagina'] = dict({r[0]: r[1] for r in NUMEROS_PARTES}, decide='numeros-gasto-publico.html', deuda='numeros-cuentas-claras.html', revisa='numeros-cuentas-claras.html', numPeso='numeros-cuanto-dinero-es.html#numPeso',
                              presupuesto='numeros-presupuesto.html', ati='herramienta-calculadora.html')
    a['abrir_a_pagina'] = NUMEROS_ABRIR
    for viejo, nuevo, nombre, texto in NUMEROS_ANTES:
        REDIRECCIONES[viejo] = (nuevo, nombre, texto)


def pagina(a, sello):
    nav = nav_de_pagina(a['archivo'], a.get('padre3'), a.get('cap_nav'))
    if nav:
        a = dict(a, pie_extra=nav, pie_corto=True)
    secciones = []
    for s in a['secciones']:
        if s.get('pagina'):
            continue  # pestana que abre su propia pagina (Agora, 10-10-2026)
        num = ('<span class="apartado-cap-num" aria-hidden="true">%d</span>' % s['num']) if s.get('num') else ''
        titulo = ('Capítulo %d. ' % s['num'] if s.get('num') else '')
        ayer = ''
        if s.get('ayer') and a.get('libro_pie'):
            # Desde el 10-10-2026 (Numeros) la franja va plegada, con su
            # llamado a la nota al pie del libro.
            rid, rnum = a['libro_ref'][:2]
            ayer = '''
        <details class="apartado-ayer-plegado">
          <summary>📘 Ayer y hoy: lo que explicaba el libro y lo que dice la ley vigente <sup class="apartado-libro-llamado"><a href="#nota-%d">[%d]</a></sup></summary>
          <div class="apartado-ayer">
            <div><span class="apartado-ayer-tit">📘 En el libro (1995)</span>%s</div>
            <div><span class="apartado-ayer-tit">📍 Hoy (2026)</span>%s</div>
          </div>
        </details>''' % ((rnum, rnum) + s['ayer'])
        elif s.get('ayer'):
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
        if s.get('mosaico'):
            # Tarjetas en mosaico, del tamano de las pestanas de Datos,
            # Aprende y Participa (Presupuesto, 11-10-2026): cada una abre
            # su pagina. Van antes de la franja «Ayer y hoy».
            mosaico = ('\n        <nav class="apartado-pestanas %s" aria-label="%s">\n%s\n        </nav>' % (
                s['mosaico'], esc_attr(s['titulo']), '\n'.join(
                    '          <a class="apartado-pestana apartado-pestana-pagina" href="%s">'
                    '<span class="apartado-pestana-ico" aria-hidden="true">%s</span>'
                    '<span class="apartado-pestana-tx"><b>%s</b><small>%s</small></span></a>' % (t[3], t[0], t[1], t[6])
                    for t in s['tarjetas'])))
            secciones.append('''      <section class="apartado-seccion" id="%s" aria-labelledby="%s-tit">%s%s%s
      </section>''' % (s['id'], s['id'], cab, mosaico, ayer))
            continue
        secciones.append('''      <section class="apartado-seccion%s" id="%s"%s%s>%s%s%s%s
      </section>''' % (' apartado-seccion-modulos' if s.get('modulos') else (' apartado-panel' if a.get('pestanas') else ''),
                       s['id'], (' aria-labelledby="%s-tit"' % s['id']) if cab else ' aria-label="Herramientas"',
                       ' role="tabpanel"' if a.get('pestanas') else '', cab, ayer, bloque,
                       ('\n        <div class="apartado-rejilla%s">\n%s\n        </div>' % (
                           ' apartado-rejilla-modulos' if s.get('modulos') else (' herr-rejilla' if s.get('sin_cab') else ''),
                           '\n'.join(tarjeta(t, s.get('modulos'), s.get('auto')) for t in s['tarjetas'])))
                       if s['tarjetas'] else ''))

    if a.get('pestanas'):
        def boton(s):
            if s.get('pagina'):
                return ('          <a class="apartado-pestana apartado-pestana-pagina" id="pestana-%s" href="%s">'
                        '<span class="apartado-pestana-ico" aria-hidden="true">%s</span>'
                        '<span class="apartado-pestana-tx"><b>%s</b><small>%s</small></span></a>'
                        % ((s['id'], s['pagina']) + s['pestana'])).replace('<small></small>', '')
            return ('          <a class="apartado-pestana" role="tab" id="pestana-%s" href="#%s" aria-controls="%s" aria-selected="false">'
                    '<span class="apartado-pestana-ico" aria-hidden="true">%s</span>'
                    '<span class="apartado-pestana-tx"><b>%s</b><small>%s</small></span></a>'
                    % ((s['id'], s['id'], s['id']) + s['pestana']))
        pista = '\n      <p class="apartado-pestanas-pista" id="pestanasPista">%s</p>' % a.get('pista', 'Elige una pestaña para abrir su contenido.')
        if any(s.get('grupo') for s in a['secciones']):
            # Tarjetas en grupos con su titulo (Gasto publico, 12-10-2026);
            # todas abren su pagina.
            grupos = []
            for s in a['secciones']:
                if s.get('grupo') or not grupos:
                    grupos.append((s.get('grupo', ''), []))
                grupos[-1][1].append(boton(s))
            en_pagina = ''.join('''
      <h2 class="apartado-pestanas-grupo">%s</h2>
      <nav class="apartado-pestanas" aria-label="%s">
%s
      </nav>''' % (g, esc_attr(re.sub(r'^\W+', '', g)), '\n'.join(b)) for g, b in grupos).lstrip('\n') + pista
        else:
            en_pagina = '''      <nav class="apartado-pestanas" role="tablist" aria-label="Pestañas de esta página"%s>
%s
      </nav>%s''' % (' data-primera="1"' if a.get('primera') else '', '\n'.join(boton(s) for s in a['secciones']), pista)
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
    if a.get('libro_pie'):
        # Desde el 10-10-2026 (Numeros) la nota del libro va al pie de la
        # pagina, como nota con su numero, ligada al compendio de fuentes,
        # al glosario y al diccionario (decision del autor).
        guia_abajo += ('\n\n      ' + a['cierre'] if a.get('cierre') else '') + '\n\n      ' + libro_pie(a)
    elif a.get('cierre'):
        guia_abajo += '\n\n      ' + a['cierre']
    elif a.get('libro_ref'):
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
    if (a.get('menu_archivo', a['archivo']) in MENU[1][2] and a['archivo'] != ENCICLOPEDIA
            and (a.get('padre') or (None,))[0] != ENCICLOPEDIA):
        padre = '<a href="%s">Enciclopedia</a> <span aria-hidden="true">›</span> %s' % (ENCICLOPEDIA, padre)
    for nivel in ('padre2', 'padre3'):
        if a.get(nivel):
            padre += '<a href="%s">%s</a> <span aria-hidden="true">›</span> ' % a[nivel]
    cab_clase, cab_estilo = 'apartado-cab', ''
    if a.get('fondo'):
        cab_clase += ' herr-cab herr-foto rubro-%s' % a['rubro'] + (' ' + a['foto_clase'] if a.get('foto_clase') else '')
        nota = '<span class="herr-cab-credito">Imagen ilustrativa</span>' + nota
    pie_extra = ('\n\n      ' + a['pie_extra']) if a.get('pie_extra') else ''
    entrada = a['entrada']
    if a.get('cajon'):
        # Boton 📖 al final de la entrada: abre su plantilla en la ventana
        # lateral (como el de «Auditoria en imagenes» en la portada).
        c = a['cajon']
        cabeza, ultima = entrada.rsplit(' ', 1)
        entrada = cabeza + ' <span class="apartado-cajon-ancla">' + ultima + (' <button type="button" class="hero-nota-btn apartado-cajon-btn" data-cajon="%s" data-cajon-hash="%s" data-cajon-tit="%s" '
                    'title="%s" aria-label="%s" aria-haspopup="dialog">📖</button></span>' % (c['id'], c['hash'], c['titulo_id'], c['boton'], c['boton']))
        nota += '<template id="%s">%s</template>' % (c['id'], c['html'])
    redirige = ''
    if a.get('hash_a_pagina'):
        # Anclas viejas que ahora son paginas: se mandan antes de pintar.
        # Una clave 'prefijo-*' lleva cualquier ancla con ese prefijo a su
        # pagina, conservando el ancla (las columnas, #col-<id>).
        redirige = ('\n  <script>(function () { var m = %s, h = location.hash.slice(1); '
                    'if (m[h]) { location.replace(m[h] + (/[?#]/.test(m[h]) ? \'\' : location.search)); return; } '
                    'for (var k in m) if (k.slice(-1) === \'*\' && h && h.indexOf(k.slice(0, -1)) === 0) { location.replace(m[k] + \'#\' + h); return; } '
                    '})();</script>' % json.dumps(a['hash_a_pagina']))
    if a.get('abrir_a_pagina'):
        # ?abrir=eb-bloque (Numeros, 11-10-2026): la tarjeta de ese bloque ya
        # vive en otra pagina; se manda alla con el mismo ?abrir.
        redirige += ('\n  <script>(function () { var m = %s, b = new URLSearchParams(location.search).get(\'abrir\'); '
                     'if (b && m[b]) location.replace(m[b]); })();</script>' % json.dumps(
                         {k: v for k, v in a['abrir_a_pagina'].items() if not v.startswith(a['archivo'] + '?')}))

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
  <script src="assets/auditor/js/iconos.js?v={sello}"></script>
  <script src="assets/auditor/js/volver-auditor.js?v={sello}" defer></script>
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
{volver}      <span class="apartado-pie-txt">Auditavisión · Toda cifra lleva su fuente oficial. Versión publicada: <b>{sello}</b></span>
    </div>
  </footer>

  <script src="assets/auditor/js/apartados.js?v={sello}"></script>
  <script src="assets/auditor/js/comunidad.js?v={sello}"></script>{scripts}
</body>
</html>
'''.format(titulo_doc=titulo_doc, descripcion=esc_attr(descripcion), favicon=FAVICON, sello=sello,
           sociales=sociales(a['archivo'], titulo_doc, descripcion),
           cabecera=cabecera(a.get('menu_archivo', a['archivo']), sello), menu=a['menu'],
           volver='' if a.get('pie_corto') else (
               '      <a class="apartado-volver" href="index.html">← Volver al auditor</a>\n'
               '      <a class="apartado-volver apartado-indice" href="indice.html">🗂️ Índice general</a>\n'),
           padre=padre, cab_clase=cab_clase, cab_estilo=cab_estilo, pie_extra=pie_extra, redirige=redirige, icono='' if a.get('sin_icono_lema') else a['icono'] + ' ', lema=a['lema'],
           titulo=(('<span class="herr-cab-ico" aria-hidden="true">%s</span><span class="herr-cab-tit">%s</span>' % (a['icono_cab'], a['titulo']))
                   if a.get('icono_cab') else a['titulo']), entrada=entrada, nota=nota, en_pagina=en_pagina, guia=guia, guia_abajo=guia_abajo, scripts=scripts, estilos=estilos, antes=(a['antes'] + '\n\n') if a.get('antes') else '',
           secciones='\n\n'.join(secciones))


# Indice general (entrega 2 de la propuesta de Astra, 10-10-2026): todo lo
# que tiene la plataforma en una sola pagina, por pestana y por tema, con la
# metodologia y las novedades. Se arma solo con las listas de este archivo y
# de auditorias.py: al agregar una pagina ahi, aparece aqui.
NOVEDADES = [
    ('26-10-2026', 'Verificamos sigue el dinero: cada caso trae «Lo que sigue» (el voto, el Diario Oficial o el informe que falta revisar), y el Auditor ya reconoce a las empresas contratistas. Escribe «Cyber Robotic Solutions» o «Cajas Graf» y te dice qué consta en documentos, y dónde ver sus contratos, si está sancionada o si la autoridad la ha señalado. Nueva columna: medicinas y ventiladores del IMSS.'),
    ('26-10-2026', 'Verificamos, en Noticias relevantes: lo que circula en redes, cotejado afirmación por afirmación contra el documento oficial. Tres primeras: la Ley de Ingresos 2027 (deuda y perdón de multas), la baja de la calificación de México por HR Ratings y la renuncia de la presidenta del INE. Pregúntale al Auditor «¿es cierto que perdonaron multas a grandes contribuyentes?» y te muestra qué consta, qué tiene matices y qué solo dice la prensa; el dictamen trae el cotejo completo.'),
    ('24-10-2026', 'Noticias relevantes, en el chat del Auditor Virtual. Escribe el nombre de un personaje («García Luna», «¿quién es Omar García Harfuch?», «noticias de Elba Esther Gordillo») y te muestra lo que la plataforma pudo sostener con documentos, con sus cifras y su fuente, y también lo que circula sin pruebas y por qué se quedó fuera. Para buscar más, te deja las búsquedas listas en portales oficiales y en las noticias, marcadas como sin verificar, y la liga a Contrasta una nota.'),
    ('24-10-2026', 'Las aplicaciones que usas dentro del Auditor Virtual ya traen «Generar dictamen»: dice qué hace la aplicación, de qué documentos oficiales salen sus datos y el enlace para repetir tu cuenta. Y el chat lee mejor tu ingreso: «gano 15 mil y tengo 2 hijos» usa los 15 mil, «8 mil a la quincena» se cuenta como 16 mil al mes (con la operación a la vista), y si dices Uber, Airbnb, renta o RESICO, la calculadora abre en ese régimen.'),
    ('24-10-2026', 'El Auditor Virtual ya abre las cuatro herramientas. Además del Modo Inspector y de Inversión y Megaobras, ahora usas desde el chat las seis aplicaciones de Costo Ambiental y las cinco de la Calculadora Cívica. Dile «gano 15 mil al mes, ¿cuánto me retienen?» y abre tu estado de cuenta con tu ingreso ya puesto. Y cuando la plática toca el Tren Maya, Dos Bocas, el huachicol o el Ramo 33, te ofrece su investigación en imágenes.'),
    ('24-10-2026', 'Una sola Enciclopedia. La plataforma antigua se fusionó con Auditavisión: lo que servía ya vivía aquí con su fuente, y su dirección te trae a la pestaña Enciclopedia. De ella rescatamos cinco temas, cotejados contra la ley vigente: en Poder Judicial, los cuatro caminos para defender la Constitución, los recursos del amparo con sus plazos y cuándo llega un caso a la Suprema Corte; en Poder Legislativo, el proceso electoral etapa por etapa y cómo evaluar a una candidata o candidato. También los contesta el chat del Auditor.'),
    ('24-10-2026', 'La salud financiera de cada megaobra, en el chat del Auditor: su estado de resultados básico (ingresos, costos y gastos, ganancia bruta, intereses, resultado neto e inversión), en verde lo que suma y en rojo lo que resta, en pesos de su año y en pesos de hoy con el mismo INPC de la máquina del tiempo del peso. Y donde no hay mapa, el chat te lleva al simulador en vivo ya filtrado por la industria y el sexenio de la obra.'),
    ('24-10-2026', 'Inversión y Megaobras entra al chat del Auditor Virtual. Pregúntale por el Tren Maya, Dos Bocas, el AIFA, el FOBAPROA o cualquiera de las 13 obras y rescates: cuánto se aprobó, cuánto costó, su sobrecosto, si gana o pierde al año y qué dijo la ASF, cada cifra con su chip y su documento. También en qué invirtió cada presidente, cuál tiene más sobrecosto o pierde más, dos obras o dos sexenios frente a frente y las cuatro cifras del total. Cada respuesta lleva a la ficha y la cuenta de la obra, al estado de cuenta de su presidente, a la salud financiera de la dependencia a cargo y a los portales oficiales, y sus cinco aplicaciones se abren ahí mismo con «▶️ Úsala aquí».'),
    ('24-10-2026', 'El Modo Inspector entra al chat del Auditor Virtual. Sus seis aplicaciones se usan sin salir de la plática: escríbele un RFC o un nombre y te dice si está en la lista negra del SAT; pégale un folio y comprueba el estado de cuenta; la liga de una nota y la contrasta; pídele el diagnóstico de un ente («diagnóstico de Pemex»), un expediente de la ASF («expediente de Segalmex») o una investigación a la medida. La aplicación se abre dentro de la respuesta con «Úsala aquí», y cada respuesta que lleva a una de ellas trae su tarjeta.'),
    ('24-10-2026', 'La Biblioteca del Erario Público, al día. Referencias suma 28 fichas, de la [126] a la [153]: los acuerdos del INE de la elección judicial y del Proceso Electoral 2026-2027, en una familia nueva «Elecciones e INE»; los estados financieros del IPAB; los estados de actividades de la Cuenta Pública del Tren Maya, el AIFA, Birmex y el Gobierno Federal; las bases de datos abiertas del PEF 2026 y del proyecto 2027, la cartera de Obra Pública Abierta, CONAPO, el padrón del SAT, la AFAC, el FIX de Banxico y los informes de la ASF sobre el NAICM y la Estela de Luz. El Diccionario suma cinco términos: los tres presupuestos, la clasificación funcional del gasto, el pasivo contingente, el Proceso Electoral Federal 2026-2027 y el estado de actividades. Fe de erratas: el Presupuesto de Egresos 2026 se publicó en el DOF el 21 de noviembre de 2025, no el 28.'),
    ('24-10-2026', 'En Números, Presupuesto queda en seis tarjetas: la primera es Los tres presupuestos (del Estado, nacional y social), que se mudó desde Gasto público, y le siguen Cuánto dinero es, Los 16 orígenes del ingreso, ¿A qué equivale?, El camino del dinero y el Paquete Económico 2027. Su página y sus cifras no cambian.'),
    ('24-10-2026', 'Comunidad queda en tres tarjetas: Ágora cívica, Garantías cívicas y Donaciones. La antigua Participa se fundió con el botón «📢 Cuéntanos lo que viste» de la cabecera, que abre su cajón con las cinco rutas: algo raro con el dinero público, un dato mal, un tema para investigar, compartir el Estado de Cuenta y la fe de erratas. El Pase del Auditor Cívico se retira: la plataforma se sostendrá con donaciones o con los Servicios de investigación.'),
    ('24-10-2026', 'Cada estado y cada municipio tiene sus cuatro documentos en su ficha técnica: estado de cuenta, salud financiera, dictamen y un contador en vivo de lo que le llega al día, por hora y por segundo, con su operación a la vista. Y al Auditor ya le puedes preguntar «Zapopan, Jalisco».'),
    ('24-10-2026', 'El Auditor Virtual abre cualquier estado de cuenta: el tuyo cívico, el ambiental (antes «Tu ticket en negativo»), el de cada presidente, la diputación federal y local, la senaduría, la Corte, tu estado y tu municipio. Y al pie de cada respuesta te ofrece el mapa, el reloj, el tablero o la fiscalización que vienen al caso, ya con tu estado elegido.'),
    ('24-10-2026', 'Las Grandes investigaciones son el Modo Inspector: una sola página con sus seis aplicaciones y una imagen nueva. Las migas de cada aplicación llevan directo a ella.'),
    ('24-10-2026', 'El Auditor Virtual se rediseña: un solo logo, respuestas con más aire y la fuente en su panel, preguntas de ejemplo que cambian solo cuando tú quieres, y los botones Regresar y Limpiar. Tu plática se guarda mientras navegas, y desde la página a la que te llevó una respuesta puedes volver al Auditor. El Modo Inspector queda con sus Grandes investigaciones.'),
    ('23-10-2026', 'Las imágenes de la portada abren el chat del Auditor con la pregunta de cada investigación escrita: al enviarla, te contesta y te lleva a su página. Las nueve investigaciones tienen además su capítulo, «Auditoría en imágenes», en los Expedientes de casos de la ASF del Modo Inspector.'),
    ('23-10-2026', 'La pestaña Auditor Virtual abre directo en Pregúntale al Auditor. Junto a «Cómo platicar conmigo» está el botón «Herramientas», con las cuatro: Modo Inspector, que lleva a las Grandes investigaciones, Costo Ambiental, Calculadora Cívica e Inversión y Megaobras.'),
    ('23-10-2026', 'El menú queda en tres pestañas: Auditor Virtual, con las herramientas; Enciclopedia, que junta Números, Datos y Aprende; y Comunidad, la antigua Participa, donde la tarjeta Comunidad se llama ahora Participa. Ningún enlace cambia de dirección.'),
    ('23-10-2026', 'El Poder Judicial y el Poder Legislativo viven en Datos, cada uno con su portada y una página por tema: quién es quién, la Suprema Corte, los sueldos, el presupuesto, la elección judicial y cómo decide; las Cámaras, el calendario, las elecciones y los congresos de los estados. Pregúntale al Auditor contesta sobre los dos.'),
    ('23-10-2026', 'Cada respuesta de Pregúntale al Auditor trae «Saber más», que abre la página donde está el dato, y «Generar dictamen», que abre el dictamen pericial sellado en su propia página.'),
    ('23-10-2026', 'Pregúntale al Auditor es el auditor de toda la plataforma: contesta como chat con las cifras de Números y de Datos, cada una con su fuente, y verifica lo que «dicen» o la liga de una nota contra el documento oficial.'),
    ('22-10-2026', 'Costo Ambiental se reestructura: la parte informativa pasa a Datos → Medio ambiente, en nueve páginas, y la herramienta se queda con sus aplicaciones.'),
    ('22-10-2026', 'Calculadora Cívica: Tu estado de cuenta se abre en cuatro páginas (tu ingreso, lo que te retienen, a dónde va cada peso y tu estado de cuenta), y el Estado de cuenta administrativo pasa a ser su quinta aplicación.'),
    ('21-10-2026', 'Expedientes de casos de la ASF reúne lo que encontró la Auditoría Superior: cada capítulo abre su propia página, del monto por aclarar a quién más fiscaliza.'),
    ('21-10-2026', 'Inversión y Megaobras queda en cuatro aplicaciones, y Contrasta una nota lee la liga, da un veredicto con semáforo y lo sella.'),
    ('20-10-2026', 'Los emojis se ven ahora como íconos de trazo de un solo color en toda la plataforma.'),
    ('16-10-2026', 'Costo Ambiental e Inversión y Megaobras abren cada aplicación en su propia página.'),
    ('13-10-2026', 'Calculadora Cívica: Tú contra ellos y El reloj de la deuda en su propia página.'),
    ('12-10-2026', 'Números: el Paquete Económico 2027 se abre en diez páginas, el Estado de Cuenta Cívico se llama Contexto dimensional y se abre en seis, y «El peso en el tiempo» del Radar se parte en tres.'),
    ('11-10-2026', 'Datos abiertos e Informes oficiales abren su propia página, y cada tarjeta, la suya: las descargas en CSV, la base municipal del INEGI, los informes de la Cuenta Pública y el diccionario de datos.'),
    ('11-10-2026', 'Nueva página de Donaciones en Participa: una alcancía que se llena a la vista de todos con cada donativo, y unas cuentas claras de lo que entra y lo que sale. El canal para donar se abre con el lanzamiento.'),
    ('11-10-2026', 'Garantías cívicas se parte en cuatro páginas, como Comunidad: la brújula que te dice a qué puerta tocar, las seis puertas oficiales, tus diez garantías y el reto ¿Mito o realidad?'),
    ('11-10-2026', 'Comunidad ya no se despliega en Participa: abre su página, con cinco tarjetas, y cada una abre la suya: algo raro con el dinero público, un dato mal, un tema para investigar, comparte el Estado de Cuenta y la fe de erratas.'),
    ('11-10-2026', 'La portada se simplifica: el carrusel de investigaciones habla en palabras llanas y sin siglas, y la cabecera ya no trae buscador. Para encontrar algo, pregúntale al Auditor.'),
    ('11-10-2026', 'Noticias relevantes abre en su propia página, con «La Columna del Erario» en su formato de periódico.'),
    ('11-10-2026', 'El Modo Inspector se abre en dos tarjetas, cada una con su página: Grandes investigaciones, con las ocho aplicaciones, y Pregúntale al Auditor, el bot interno.'),
    ('11-10-2026', 'Pregúntale al Auditor anota lo que todavía no sabe contestar, y lo que marcas con «No era lo que buscaba», en el recuadro «Lo que aún no sé». Lo copias y nos lo mandas desde Comunidad.'),
    ('11-10-2026', 'Nace Pregúntale al Auditor, el bot interno del Modo Inspector: responde con una nota técnica sellada, armada solo con datos verificados, cada cifra con su fuente y su estado.'),
    ('11-10-2026', 'Costo Ambiental estrena encabezado verde gris con su icono y sus módulos pasan a ser cinco aplicaciones. La quinta es nueva: Crisis ambientales. Compara lo que puede costar un desastre con lo que hay para pagarlo (el fondo, el seguro y los bonos), trae una calculadora de lo que cuesta esperar si el hueco se cubre con deuda, y abre tres fichas: el huracán Otis, el huracán Simón y el agua de Guadalajara, cada cifra con su documento y lo que falta con el nombre de quien debe publicarlo.'),
    ('11-10-2026', 'Baja al territorio queda en tres tarjetas, y cada una abre su página: el mapa del gasto federalizado, con cinco lentes y las 32 entidades de mayor a menor; las 32 entidades, con los tres pisos de la hacienda, lo que baja y con qué libertad, y el circuito de cada estado; y los 2,479 municipios, con sus fondos, su predial, el punto ciego del artículo 115 y el padrón completo del INEGI. La franja «Ayer y hoy» pasa a la pregunta frecuente del Ramo 28 y el Ramo 33.'),
    ('11-10-2026', 'El Diccionario del Erario Público se llama ahora Biblioteca del Erario Público: una página con cuatro tarjetas, Diccionario, Referencias, Marco Legal Hacendario y Preguntas Frecuentes. El Pase del Auditor Cívico pasa a Participa.'),
    ('11-10-2026', 'El Diccionario del Gasto Público se llama ahora Diccionario del Erario Público.'),
    ('11-10-2026', 'Los Servicios de investigación salen de Participa y pasan a ser un módulo del Modo Inspector, en Herramientas, con todo su contenido: los cinco servicios, cómo trabajamos, el precio, la política de independencia, el formulario y el Pase del Auditor Cívico. El enlace viejo de Participa lleva ahí.'),
    ('11-10-2026', 'La página de Presupuesto queda solo con sus cinco tarjetas: sin botones de salto al pie.'),
    ('11-10-2026', 'Presupuesto se aligera: la franja «Ayer y hoy» y las notas del libro pasan al Diccionario del Gasto Público, en la pregunta frecuente sobre la acción financiera del Estado y en la ficha del libro en el Compendio de fuentes. Al pie de cada página de Presupuesto quedan solo dos botones, anterior y siguiente, sin listas que repitan los mismos destinos.'),
    ('11-10-2026', 'Presupuesto queda en cinco tarjetas compactas. El peso de 2026 se fundió con Cuánto dinero es, que ahora reúne la cifra del año, las dos barras de lo que entra y lo que sale, y lo que baja al territorio, sin repetir el reparto en columnas. El camino del dinero se concentra en quién responde, en qué plazo y con qué ley, y remite a las cifras en lugar de repetirlas.'),
    ('11-10-2026', 'La página de Presupuesto queda en seis tarjetas, y cada una abre su propia página: El peso de 2026, con las dos barras de lo que entra y lo que sale; Los 16 orígenes del ingreso, renglón por renglón y con su contador; Cuánto dinero es; ¿A qué equivale?; El camino del dinero, en cuatro etapas, y el Paquete Económico 2027.'),
    ('11-10-2026', 'Los cuatro módulos de Presupuesto ya no se despliegan dentro del auditor: cada uno es una página propia que abre al instante, con sus cifras ya puestas. Cuánto dinero es pone lo que entra y lo que sale columna contra columna; ¿A qué equivale? dibuja cada comparación con su operación; El camino del dinero muestra las cuatro etapas con quién responde, su plazo y su ley; y el Paquete Económico 2027 reúne la constitución económica, el itinerario, las cifras, el simulador de sensibilidades con los coeficientes oficiales y los puntos ciegos.'),
    ('11-10-2026', 'La página de Gasto público se vuelve dinámica. «¿Quién lo aprueba?» recorre las seis paradas del presupuesto, de la propuesta de Hacienda a la revisión de la Auditoría Superior, con su fecha límite y el artículo que da cada facultad, y una tabla de quién puede qué. «¿Cómo se reparte?» es un simulador contable que parte los $10.19 billones en programable y no programable y en sus ocho renglones, y reparte cualquier cantidad en la misma proporción. Cada renglón del gasto tiene ya su propia página. Megaobras y costo ambiental quedan solo en Herramientas.'),
    ('11-10-2026', 'En Números, «Se paga lo que se debe» y «Se revisa» son una sola página, «Cuentas claras»: la línea de tiempo de la deuda, sexenio por sexenio, y lo que pasa al año siguiente, cuando la Auditoría Superior revisa la Cuenta Pública. El estado de resultados del Gobierno abre en su propia página; el reloj de la deuda y el inspector de la ASF llevan a Herramientas. Números queda en cuatro tarjetas.'),
    ('11-10-2026', 'En Números, «Se aprueba» y «Se gasta» son una sola página, «Gasto público»: quién aprueba el presupuesto, los tres presupuestos (del Estado, nacional y social) y lo ya comprometido, con el simulador para repartirlo tú. Lo que cuestan los Poderes, los ramos y dependencias, el margen del presupuesto y lo que la cifra grande no dice abren cada uno en su página; megaobras y costo ambiental llevan a Herramientas. «Se recauda» ahora se llama «Presupuesto», y cada tarjeta de Números trae su descripción breve.'),
    ('11-10-2026', 'En Números, «Presupuesto» y «Se recauda» son una sola página: arriba, las dos barras de lo que entra y lo que sale; abajo, los 16 orígenes del ingreso con su contador. Cada renglón (ISR, IVA, IEPS, cuotas, deuda...) tiene su propia página con qué grava, su ley, su efecto jurídico y su desglose; y Cuánto dinero es, ¿A qué equivale?, El camino del dinero y el Paquete Económico 2027 abren en la suya.'),
    ('11-10-2026', 'Números se abre en siete páginas, como el Radar hacendario: el presupuesto completo (de dónde viene y a dónde va cada peso), se recauda, se aprueba, se gasta con los tres presupuestos, baja al territorio, se paga lo que se debe y se revisa. Cada tarjeta lleva a la suya.'),
    ('10-10-2026', 'Números, reorganizado: un solo recorrido de seis pasos (se recauda, se aprueba, se gasta, baja al territorio, se paga la deuda y se revisa). Arriba, «El peso de 2026», dos barras interactivas con todo lo que entra y todo lo que sale, en pesos o por cada $100; en el paso 3, los tres presupuestos: del Estado, nacional y social. La nota del libro pasa al pie.'),
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


def _grupo(icono, titulo, enlaces, href=None, hijas=None):
    if hijas:
        # Debajo de cada enlace, sus subpaginas, si no estan ya en el grupo.
        # Se sacan del diccionario al ponerlas: una pagina que se enlaza en
        # dos grupos despliega sus subpaginas solo en el primero.
        vistos, todo = set(e[0] for e in enlaces), []
        for e in enlaces:
            todo.append(e)
            todo += [(h, '· ' + t, '') for h, t in hijas.pop(e[0], []) if h not in vistos]
        enlaces = todo
    cab = ('<a href="%s">%s %s</a>' % (href, icono, titulo)) if href else '%s %s' % (icono, titulo)
    filas = '\n'.join('              <li><a href="%s">%s</a>%s</li>' % (h, t, ('<span>%s</span>' % d) if d else '')
                      for h, t, d in enlaces)
    return ('          <div class="indice-grupo">\n            <h3 class="indice-grupo-tit">%s</h3>\n'
            '            <ul class="indice-lista">\n%s\n            </ul>\n          </div>' % (cab, filas))


def _rejilla(grupos):
    return '<div class="indice-grupos">\n%s\n        </div>' % '\n'.join(grupos)


def _a_numeros(destino):
    m = re.search(r'ir=presupuesto&(?:amp;)?ancla=(eb-[\w-]+)', destino)
    return NUMEROS_ABRIR.get(m.group(1), 'sigue-el-dinero.html?abrir=' + m.group(1)) if m else destino


def _hijas(base, ref):
    """Las subpaginas de cada pagina del indice (pedido del autor,
    23-10-2026): sin ellas, el indice se quedaba en las portadas. Salen de las
    mismas listas que arman cada pagina, asi que una nueva aparece sola."""
    import estado_cuenta, presupuesto_modulos, cc_ticket, insp_asf, datos_ambiente, asistente
    import asistente_legislativo as al, asistente_judicial as aj
    limpio = lambda t: re.sub('<[^>]+>', '', t)
    return {
        estado_cuenta.ARCHIVO: [(p['archivo'], limpio(p.get('menu') or p['titulo'])) for p in estado_cuenta.construir()[0]
                                if p['archivo'] != estado_cuenta.ARCHIVO],
        'numeros-paquete-2027.html': [(x[2], x[3]) for x in presupuesto_modulos.PE_PARTES],
        cc_ticket.PORTADA: [(cc_ticket.paso_archivo(x[1]), x[3]) for x in cc_ticket.PASOS],
        'herramienta-inspector-asf.html': [(p['archivo'], limpio(p['menu'])) for p in insp_asf.subpaginas(base, ref)],
        ASISTENTE[0]: [(asistente.DICTAMEN, 'El dictamen pericial')],
        'radar-peso.html': [(x[1], x[2]) for x in RADAR_PESO_PARTES],
        datos_ambiente.PORTADA: [(x[1], x[3]) for x in datos_ambiente.PARTES],
        al.PORTADA: [(x[0], x[2]) for x in al.PAGINAS],
        aj.PORTADA: [(x[0], x[2]) for x in aj.PAGINAS],
    }


def indice(base, ref):
    import auditorias
    import asistente_legislativo as al, asistente_judicial as aj
    hijas = _hijas(base, ref)
    def grupo(*a):
        return _grupo(*a, hijas=hijas)
    au = {a[0]: a for a in auditorias.AUDITORIAS}
    ap = {a['archivo']: a for a in APARTADOS}
    investigaciones = _rejilla([grupo(ico, tit, [(auditorias.archivo(i), au[i][5], au[i][6]) for i in ids])
                                for ico, tit, ids in auditorias.TEMAS])
    numeros = _rejilla([grupo('🧾', 'El balance', [
        ('estado-de-cuenta.html', 'Contexto dimensional', '2024, 2026 y 2027 en cuatro dimensiones'),
        ('estado-de-cuenta-2024-2027.csv', 'Descarga el contexto dimensional en CSV', 'Con periodo, fuente y estado de cada renglón')])] +
                       [grupo(p['icono'], p['titulo'],
                               ([(ingreso_archivo(x), '· ' + x['nombre'], '') for x in auditorias.db()['panoramaErario']['ingresos']]
                                if p['archivo'] == 'numeros-presupuesto.html' else []) +
                               ([(x[2], x[3], '') for x in GASTO_PARTES if x[7] == 'como'] +
                                [(egreso_archivo(x), '· ' + x['nombre'], '') for x in auditorias.db()['panoramaErario']['egresos']] +
                                [(x[2], x[3], '') for x in GASTO_PARTES if x[7] != 'como']
                                if p['archivo'] == 'numeros-gasto-publico.html' else []) +
                               ([(x[2], x[3], '') for x in CUENTAS_PARTES] if p['archivo'] == 'numeros-cuentas-claras.html' else []) +
                               [(_a_numeros(t[3]), re.sub('<[^>]+>', '', t[1]), '') for s in p['secciones'] for t in s.get('tarjetas', [])],
                               p['archivo'])
                        for p in NUMEROS_PAGINAS if p['archivo'] in [r[1] for r in NUMEROS_PARTES]])
    # El Modo Inspector se abre en dos tarjetas (11-10-2026): sus ocho
    # aplicaciones cuelgan de «Grandes investigaciones», y el bot va aparte.
    herr = _rejilla([grupo(h[2], h[3],
                            [(modulo_archivo(h[0], t[0]), t[2], t[3]) for t in h[7]],
                            h[0])
                     for h in HERRAMIENTAS])
    otros = [_grupo('📚', 'Enciclopedia', [
        (ENCICLOPEDIA, 'Enciclopedia', 'Números, Datos y Aprende en una sola puerta'),
        ('sigue-el-dinero.html', 'Números', 'El recorrido del dinero público'),
        ('descarga-los-datos.html', 'Datos', 'El radar, las descargas, el ambiente y los Poderes'),
        ('aprende.html', 'Aprende', 'La trivia, la Biblioteca y las noticias')])]
    for archivo in ('descarga-los-datos.html', 'aprende.html', 'participa.html'):
        a = ap[archivo]
        enl = [(x.get('pagina') or archivo + '#' + x['id'], x['pestana'][1], x['pestana'][2]) for x in a['secciones']]
        if archivo == 'descarga-los-datos.html':
            enl[1:1] = [(r[1], 'Radar · ' + r[3], r[4]) for r in RADAR_PARTES]
            for d in DATOS_PARTES:
                k = [e[0] for e in enl].index(d[1]) + 1
                enl[k:k] = [(f[1], '· ' + f[3], '') for f in d[6]]
        if archivo == 'aprende.html':
            enl += [('diccionario.html', BIB_NOMBRE, 'La obra de consulta')] + [(b[0], '· ' + b[2], b[3]) for b in BIBLIOTECA]
        if archivo == 'participa.html':
            enl = [e for e in enl if e[0] != 'comunidad.html']
            k = [e[0] for e in enl].index('garantias.html') + 1
            enl[k:k] = [(g[1], '· ' + g[3], '') for g in GARANTIAS_PARTES]
            enl += [('expedientes.html', 'Expedientes de casos de la ASF', 'Los casos por aclarar')]
        otros.append(grupo(a['icono'], a['menu'], enl, archivo))
        if archivo == 'participa.html':
            # El boton de la cabecera, con sus cinco paginas (24-10-2026).
            otros.append(_grupo('📢', 'Cuéntanos lo que viste', [
                ('comunidad.html', 'Cuéntanos lo que viste', 'Reporta, señala errores, propón temas, comparte y fe de erratas')] + [
                (c[1], '· ' + c[3], '') for c in COMUNIDAD_PARTES]))
    otros.append(_grupo('🏛️', 'Los Poderes', [
        (al.PORTADA, 'Poder Legislativo', 'Las Cámaras, el calendario, las elecciones y los estados'),
        (aj.PORTADA, 'Poder Judicial', 'La Corte, los sueldos, el presupuesto y la elección judicial'),
        ('numeros-lo-que-cuestan-los-poderes.html', 'Lo que cuestan el Congreso y la Judicatura', 'Presupuesto 2026 y Cuenta Pública 2024')]))
    metodologia = (
        '<div class="indice-metodo">\n'
        '          <p>Toda cifra de la plataforma lleva su fuente oficial y uno de tres estados:</p>\n'
        '          <ul class="indice-lista indice-estados">\n'
        '            <li><span class="est-chip est-oficial">oficial</span> La tomamos tal cual de su documento (DOF, SHCP, ASF, INEGI, Banxico), con la liga para que la revises.</li>\n'
        '            <li><span class="est-chip est-derivado">derivado</span> La calculamos a partir de cifras oficiales y te decimos la operación.</li>\n'
        '            <li><span class="est-chip est-pendiente">pendiente</span> El dato no está en un documento que podamos citar. Decimos por qué y, si la dependencia obligada no lo ha publicado, la nombramos. Nunca lo estimamos.</li>\n'
        '          </ul>\n'
        '          <p>Las imágenes de las investigaciones son ilustraciones y lo dicen en una etiqueta: no son evidencia de ningún hecho. '
        'La evidencia está en los documentos de las <a href="fuentes-oficiales.html">Referencias</a> de la Biblioteca del Erario Público.</p>\n'
        '          <p><a href="pendientes.html"><b>⏳ Registro de pendientes</b></a>: cada dato que falta, por qué falta, quién debe publicarlo y el enlace oficial donde debería estar.</p>\n'
        '          <h3 class="indice-grupo-tit">🆕 Novedades</h3>\n'
        '          <ul class="indice-lista indice-novedades">\n%s\n          </ul>\n'
        '        </div>') % '\n'.join('            <li><b>%s</b> %s</li>' % n for n in NOVEDADES)
    secc = [
        ('investigaciones', '🖼️ Investigaciones, por tema', 'Las auditorías en imágenes. Cada una explica el caso y lleva a sus números y a su evidencia.', investigaciones),
        ('numeros', '💰 Enciclopedia · Números', 'El recorrido del dinero público, del impuesto a la rendición de cuentas, cada parte en su propia página.', numeros),
        ('herramientas', '🧰 Auditor Virtual', 'Cada herramienta y sus módulos, con página propia.', herr),
        ('mas', '📚 Enciclopedia · Datos y Aprende, Comunidad y los Poderes', 'Descargas, la Biblioteca del Erario Público, las noticias, la participación ciudadana y los Poderes de la Unión.', _rejilla(otros)),
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
    # El Pase del Auditor Civico se retiro el 24-10-2026 (decision del autor).
    'pase-del-auditor.html': ('donaciones.html', 'Pase del Auditor Cívico',
                              'El Pase se retiró. Para sostener la plataforma están las donaciones y los Servicios de investigación.'),
    # «El Congreso y las elecciones» se mudó a Datos el 23-10-2026 (pedido del
    # autor): su ancla (#leg-<tema>) viaja y la portada la manda a su página.
    'congreso-y-elecciones.html': ('datos-poder-legislativo.html', 'El Congreso y las elecciones',
                                   'Está ahora en la pestaña Datos, como «Poder Legislativo», con una página por tema.'),
    # Las cuatro aplicaciones de Inversion y Megaobras se fundieron en
    # capitulos el 21-10-2026 (pedido del autor): el pulso ya no tiene
    # pagina propia; sus cinco partes son capitulos.
    'herramienta-megaobras-pulso.html': ('herramienta-megaobras.html', 'El pulso del gasto',
                                         'Sus partes están ahora en las cuatro aplicaciones de Inversión y Megaobras.'),
    # Los nueve capitulos se fundieron en cuatro aplicaciones el mismo dia
    # (pedido del autor, mo_capitulos.py): los que se quedaron sin pagina
    # llevan a la aplicacion donde vive su contenido; el ancla viaja con la
    # redireccion cuando el destino no trae la suya.
    'herramienta-megaobras-sexenios.html': ('herramienta-megaobras-tabla.html', 'Los seis sexenios',
                                            'La línea del tiempo y la comparación de dos sexenios están ahora en la aplicación «En qué invirtió cada presidente».'),
    'herramienta-megaobras-pulso-cifras.html': ('herramienta-megaobras-cero.html#mpCifras', 'Las cuatro cifras y los rescates',
                                                'Están ahora en la aplicación «Las cuatro cifras y los rescates», junto con De cero al resultado.'),
    'herramienta-megaobras-pulso-composicion.html': ('herramienta-megaobras-sector.html#mpCompo', 'De qué está hecho el total',
                                                     'Está ahora al pie de la aplicación «Obra por obra, por industria».'),
    'herramienta-megaobras-pulso-ritmo.html': ('herramienta-megaobras-pulso-cuenta.html#mpRitmo', 'El ritmo de la pérdida',
                                               'Está ahora en la aplicación «La cuenta de cada obra y el ritmo de la pérdida».'),
    'herramienta-megaobras-pulso-calculo.html': ('herramienta-megaobras-cero.html#como-se-calcula', 'Cómo se calcula',
                                                 'Ahora se abre desde el botón «¿Cómo se calcula?» de cada aplicación de Inversión y Megaobras.'),
    # El directorio del Auditor de entes publicos volvio a su pagina el
    # 21-10-2026 (pedido del autor): un solo navegador con el buscador, los
    # niveles y los filtros. ?nivel=, ?q= y #ente= viajan con la redireccion.
    # El Radar por entidad se fusiono con la ficha estatal (21-10-2026).
    'herramienta-inspector-radar.html': ('herramienta-inspector-entes.html?nivel=estatal&orden=radInt#ie-dir', 'Radar por entidad',
                                         'El radar de cada estado está ahora en su ficha técnica, y los 32 estados se ordenan en el directorio del Auditor de entes públicos.'),
    'herramienta-inspector-entes-directorio.html': ('herramienta-inspector-entes.html', 'Directorio de entes públicos',
                                                    'El directorio, el buscador y los filtros están ahora juntos en el Auditor de entes públicos.'),
    # Los tres pasos de Contrasta una nota se juntaron en una sola pagina el
    # 21-10-2026 (pedido del autor); la ?liga= de un veredicto compartido
    # viaja con la redireccion.
    'herramienta-inspector-nota-liga.html': ('herramienta-inspector-nota.html', 'Contrasta una nota · la nota',
                                             'Ahora pegas la nota y ves el veredicto en una sola página.'),
    'herramienta-inspector-nota-cifras.html': ('herramienta-inspector-nota.html', 'Contrasta una nota · las cifras',
                                               'Ahora pegas la nota y ves el veredicto en una sola página.'),
    'herramienta-inspector-nota-veredicto.html': ('herramienta-inspector-nota.html', 'Contrasta una nota · el veredicto',
                                                  'Ahora pegas la nota y ves el veredicto en una sola página.'),
    # «Hoy y los estados de cuenta» se repartio el 12-10-2026 (pedido del
    # autor): el presupuesto en curso, a «Cuanto dinero es»; el estado de
    # cuenta, al tablero (radar-estado-de-cuenta.html no cambia de direccion).
    'radar-como-leer.html': ('radar-hacendario.html#lectura', 'Cómo leer estos números',
                             'Ahora se abre desde el botón 📖 de la entrada del Radar hacendario.'),
    'radar-hoy.html': ('numeros-cuanto-dinero-es.html', 'Hoy y los estados de cuenta',
                       'Las cifras de 2026 viven ahora en Números → Presupuesto → Cuánto dinero es; el estado de cuenta se expide desde el tablero del Radar hacendario.'),
    'radar-presupuesto-en-curso.html': ('numeros-cuanto-dinero-es.html', 'Hoy: el presupuesto en curso',
                                        'Las cifras de 2026, con su contador, viven ahora en Números → Presupuesto → Cuánto dinero es.'),
    # «Basura y proteccion» dejo de ser aplicacion de Costo Ambiental el
    # 22-10-2026 (pedido del autor): sus bloques viven en Datos → Medio
    # ambiente, y sus anclas (#abBasura, #abLeyes...) llevan a su pagina.
    'herramienta-ambiente-basura.html': ('datos-medio-ambiente.html', 'Basura y protección',
                                         'Ahora vive en Datos → Medio ambiente, una página por tema.'),
    INVESTIGACIONES: (MODO_INSPECTOR, 'Grandes investigaciones',
                      'Desde el 24-10-2026 las Grandes investigaciones son el Modo Inspector: sus seis aplicaciones están en su página.'),
    # La plataforma Enciclopedia antigua (9 pestañas, con assets/css, js y
    # data) se retiró el 24-10-2026 por decisión del autor: lo que servía ya
    # vive en Auditavisión. Su dirección lleva a la pestaña Enciclopedia; el
    # código original queda en el historial (commit 490233d).
    'enciclopedia.html': ('enciclopedia-auditavision.html', 'La Enciclopedia antigua',
                          'Lo que servía de ella ya vive en la pestaña Enciclopedia de Auditavisión: Números, Datos y Aprende.'),
    'busca-y-verifica.html': ('herramienta-inspector-entes.html', 'Busca y verifica',
                              'Ahora vive dentro del Modo Inspector, en la parte «Busca y verifica».'),
    # Los dos estantes del Diccionario se fundieron en la Biblioteca del
    # Erario Publico el 11-10-2026 (decision del autor).
    'biblioteca-hacendaria.html': ('diccionario.html', 'Biblioteca hacendaria',
                                   'Sus apartados (Diccionario, Marco Legal y Preguntas Frecuentes) viven ahora en la Biblioteca del Erario Público.'),
    'fuentes-del-auditor.html': ('diccionario.html', 'Fuentes del auditor',
                                 'Las Referencias viven ahora en la Biblioteca del Erario Público.'),
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
  <script>(function () {{ var u = '{url}'; if (!/[?#]/.test(u)) u += location.search + location.hash; window.location.replace(u); }})();</script>
</head>
<body style="font-family:system-ui,sans-serif;background:#ffffff;color:#1c2a44;padding:24px">
  <p><b>{nombre}</b> cambió de lugar. {texto} <a href="{destino}">Ir ahora ➔</a></p>
</body>
</html>
'''.format(nombre=nombre, destino=destino, favicon=FAVICON, url=destino.replace('&amp;', '&'), texto=texto)


def generar(sello=None):
    numeros_preparar()
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
    import auditorias
    base_nat = auditorias.db()
    refs_nat = {r['id']: r for r in base_nat['referencias_legales']}
    def ref_nat(rid):
        r = refs_nat[rid]
        return nota_ref(rid, r['num'], re.sub('<[^>]+>', '', r['cita_apa'])[:160].replace('"', '&quot;'))
    for n, h in enumerate(HERRAMIENTAS, 1):
        hp = herramienta(h, n)
        if h[1] == 'obras':
            megaobras_portada(hp, base_nat, ref_nat)
            for sp in megaobras_pulso(h, n, base_nat, ref_nat):
                texto = pagina(sp, sello).replace('\r\n', '\n').replace('\n', '\r\n')
                open(os.path.join(RAIZ, sp['archivo']), 'wb').write(texto.encode('utf-8'))
        for pg in [hp] + hp.pop('_extra', []):
            texto = pagina(pg, sello).replace('\r\n', '\n').replace('\n', '\r\n')
            open(os.path.join(RAIZ, pg['archivo']), 'wb').write(texto.encode('utf-8'))
        for i, t in enumerate(h[7]):
            if t[0].endswith('.html') or t[0] in MODULOS_PROPIOS:
                continue
            m = herramienta_modulo(h, n, i)
            if t[0] in INSP_NATIVAS and os.path.exists(os.path.join(RAIZ, 'herramientas', INSP_NATIVAS[t[0]] + '.py')):
                insp_nativa(m, t[0], base_nat, ref_nat)
                for sp in insp_subpaginas(m, t[0], base_nat, ref_nat):
                    texto = pagina(sp, sello).replace('\r\n', '\n').replace('\n', '\r\n')
                    open(os.path.join(RAIZ, sp['archivo']), 'wb').write(texto.encode('utf-8'))
            texto = pagina(m, sello).replace('\r\n', '\n').replace('\n', '\r\n')
            open(os.path.join(RAIZ, m['archivo']), 'wb').write(texto.encode('utf-8'))
    # La quinta aplicacion de Costo Ambiental trae su propio contenido
    # (herramientas/crisis_ambientales.py, 11-10-2026).
    import auditorias
    import crisis_ambientales as ca
    base = auditorias.db()
    refs = {r['id']: r for r in base['referencias_legales']}
    def ref(rid):
        r = refs[rid]
        return nota_ref(rid, r['num'], re.sub('<[^>]+>', '', r['cita_apa'])[:160].replace('"', '&quot;'))
    n, h = next((k, x) for k, x in enumerate(HERRAMIENTAS, 1) if x[1] == 'ambiente')
    i = next(k for k, t in enumerate(h[7]) if t[0] == ca.ARCHIVO)
    m = herramienta_modulo(h, n, i, bloque=ca.pagina(base, ref))
    m.update({'archivo': ca.ARCHIVO, 'estilos': ['crisis.css'], 'scripts': ['crisis.js']})
    texto = pagina(m, sello).replace('\r\n', '\n').replace('\n', '\r\n')
    open(os.path.join(RAIZ, ca.ARCHIVO), 'wb').write(texto.encode('utf-8'))
    import datos_ambiente
    for extra in [DICCIONARIO, NOTICIAS, GLOSARIO, indice(base, ref), simulador(), servicios(), agora(), donaciones()] + datos_paginas() + poderes_paginas(base) + garantias() + comunidad() + radar() + datos_ambiente.paginas(base, ref) + NUMEROS_PAGINAS + PAGINAS_BIBLIOTECA:
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
    import estado_cuenta
    import pendientes
    if auditorias.generar(sello) or estado_cuenta.generar(sello) or pendientes.generar(sello):
        return 1
    # El bot interno del Modo Inspector: su base se arma con las paginas ya
    # escritas (herramientas/asistente.py, 11-10-2026).
    import asistente
    cuenta = asistente.escribir_base()
    texto = pagina(herramienta_asistente(asistente.pagina(cuenta, CANAL_COMUNIDAD, HERR_MENU)), sello).replace('\r\n', '\n').replace('\n', '\r\n')
    open(os.path.join(RAIZ, asistente.ARCHIVO), 'wb').write(texto.encode('utf-8'))
    texto = pagina(herramienta_dictamen(asistente.dictamen_pagina()), sello).replace('\r\n', '\n').replace('\n', '\r\n')
    open(os.path.join(RAIZ, asistente.DICTAMEN), 'wb').write(texto.encode('utf-8'))
    print('asistente: %s con %d fichas %s' % (asistente.ARCHIVO, sum(cuenta.values()), cuenta))
    import sitemap
    return sitemap.generar(sello)


if __name__ == '__main__':
    sys.exit(generar())
