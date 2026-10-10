#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera una pagina por cada diapositiva de «Auditoria en imagenes».

Desde el 09-10-2026 la portada ya no despliega nada debajo de si misma:
cada clic lleva a una pagina propia (decision del autor, ver AGENTS.md).
Las nueve diapositivas del carrusel abren auditoria-<id>.html, que pinta
assets/auditor/js/auditoria-imagen.js con las cifras de window.AUDIT_DB.
Aqui no se escribe ni un monto: solo el marco de cada pagina.

Lo llama apartados.generar(), asi que sello.py las regenera con el sello.
"""
import os
import re

from apartados import RAIZ, FAVICON, cabecera, esc_attr

# id, imagen, nota de la imagen, texto alternativo, etiqueta, titulo, pregunta
AUDITORIAS = [
    ('tren-maya', 'assets/img/showcase_tren_maya.jpg', 'Ilustración generada con IA',
     'Ilustración generada con IA de un tren sobre vías en la selva',
     '🚅 Megaobra ferroviaria · FONATUR y Tren Maya', 'Tren Maya',
     '¿Cuánto dinero del Tren Maya dejó la ASF por aclarar, y en qué tramos?'),
    ('dos-bocas', 'assets/img/showcase_dos_bocas.jpg', 'Ilustración generada con IA',
     'Ilustración generada con IA de una refinería junto al mar',
     '🏭 Refinación · Pemex, Paraíso, Tabasco', 'Refinería Olmeca (Dos Bocas)',
     '¿Qué encontró la ASF al revisar la refinería paquete por paquete?'),
    ('deuda-soberana', 'assets/img/showcase_deuda_soberana.jpg', 'Ilustración generada con IA',
     'Ilustración generada con IA de un edificio de gobierno',
     '🏛️ Costo financiero de la deuda · PEF 2026', 'Los intereses de la deuda pública',
     '¿Cuánto cuesta al año pagar sólo los intereses de la deuda pública?'),
    ('aifa', 'assets/img/showcase_aifa.jpg', 'Ilustración generada con IA',
     'Ilustración generada con IA de una terminal aérea',
     '✈️ Infraestructura aeroportuaria · Defensa', 'Aeropuerto Internacional Felipe Ángeles (AIFA)',
     '¿Qué revisó la ASF en la construcción y la operación del AIFA?'),
    ('ramo-33', 'assets/img/showcase_ramo33.jpg', 'Ilustración generada con IA',
     'Ilustración generada con IA de un centro de salud',
     '🏥 Gasto federalizado · Ramo 33', 'Ramo 33: el dinero para estados y municipios',
     '¿Cuánto dinero del Ramo 33 llega a estados y municipios, y cuánto quedó por aclarar?'),
    ('lego-cienega', 'assets/img/showcase_lego_expansion.jpg', 'Imagen ilustrativa',
     'Imagen ilustrativa de una planta industrial',
     '🧱 Inversión privada y obra pública · Nuevo León', 'Ciénega de Flores: el dinero público alrededor de LEGO',
     '¿Qué dinero público rodea a la planta de LEGO en Ciénega de Flores?'),
    ('tren-toluca', 'assets/img/showcase_tren_toluca.jpg', 'Imagen ilustrativa',
     'Imagen ilustrativa de un tren sobre un viaducto elevado',
     '🚄 Transporte ferroviario · SICT', 'Tren Interurbano México-Toluca «El Insurgente»',
     '¿Qué dejó por aclarar la ASF en la obra que faltaba para terminar el Tren Interurbano?'),
    ('megafarmacia', 'assets/img/showcase_megafarmacia.jpg', 'Imagen ilustrativa',
     'Imagen ilustrativa de un almacén de medicamentos',
     '💊 Almacén de medicamentos · Birmex, Huehuetoca', 'Megafarmacia del Bienestar (Huehuetoca)',
     '¿Cuánto costó el almacén de Huehuetoca y qué encontró la ASF en Birmex?'),
    ('huachicol-fiscal', 'assets/auditor/img/showcase_huachicol.jpg', 'Ilustración provisional',
     'Ilustración de pipas de combustible frente a una aduana portuaria al atardecer',
     '⛽ Evasión en combustibles · IEPS, aduanas y SAT', 'Huachicol fiscal: el impuesto que no entra',
     '¿Cuánto IEPS de gasolinas y diésel está en juego, y qué se sabe de lo que se evade?'),
]


# Investigaciones agrupadas por tema (entrega 2 de Astra, 10-10-2026). Las
# usan el indice general (apartados.py) y la portada.
TEMAS = [
    ('🏗️', 'Megaobras e infraestructura', ['tren-maya', 'dos-bocas', 'aifa', 'tren-toluca', 'megafarmacia']),
    ('🗺️', 'Dinero para estados y municipios', ['ramo-33', 'lego-cienega']),
    ('💸', 'Deuda e ingresos del gobierno', ['deuda-soberana', 'huachicol-fiscal']),
]


# Recorrido de cada investigacion (propuesta de Astra, entrega 1, 10-10-2026):
# entender el caso aqui, explorar sus numeros en «Numeros» y revisar la
# evidencia en el Inspector. id: (tarjeta de Numeros, que la abre, modulo del
# Inspector, que revisa).
RUTAS = {
    'tren-maya': ('eb-cuenta-federal', 'La Cuenta Pública federal y el peritaje del Tren Maya',
                  'herramienta-inspector-asf.html', 'Lo que auditó la ASF, ente por ente'),
    'dos-bocas': ('eb-egresos', 'Cuánto recibe cada ramo, Pemex incluido',
                  'herramienta-inspector-asf.html', 'Lo que auditó la ASF, ente por ente'),
    'deuda-soberana': ('eb-ccreloj', 'El reloj del costo de la deuda',
                       'herramienta-inspector-radar.html', 'El radar hacendario: deuda e ingresos'),
    'aifa': ('eb-egresos', 'Cuánto recibe cada ramo, Defensa incluida',
             'herramienta-inspector-asf.html', 'Lo que auditó la ASF, ente por ente'),
    'ramo-33': ('eb-mapa', 'El mapa de lo que baja a cada estado',
                'herramienta-inspector-asf.html', 'Lo que auditó la ASF, ente por ente'),
    'lego-cienega': ('eb-mapa', 'El mapa de lo que baja a cada estado',
                     'herramienta-inspector-entes.html', 'El auditor de entes públicos'),
    'tren-toluca': ('eb-egresos', 'Cuánto recibe cada ramo, la SICT incluida',
                    'herramienta-inspector-asf.html', 'Lo que auditó la ASF, ente por ente'),
    'megafarmacia': ('eb-salud', 'El gasto en salud, institución por institución',
                     'herramienta-inspector-asf.html', 'Lo que auditó la ASF, ente por ente'),
    'huachicol-fiscal': ('eb-ingresos', 'De dónde sale el dinero: el IEPS en la Ley de Ingresos',
                         'herramienta-inspector-efos.html', 'La lista negra del SAT'),
}


def ruta(id_):
    ancla, num_txt, insp, insp_txt = RUTAS[id_]
    pasos = [
        ('📖', 'Entiende el caso', 'Qué pasó, cuánto dinero involucra, quién interviene y qué falta saber.',
         '#auImg', 'Leer el caso', ' aqui'),
        ('💰', 'Explora los números', num_txt + ', con su fuente oficial.',
         'sigue-el-dinero.html?abrir=' + ancla, 'Ir a Números', ''),
        ('🔍', 'Revisa la evidencia', insp_txt + ': los documentos que sostienen el caso.',
         insp, 'Abrir el Inspector', ''),
    ]
    return ('      <section class="camino au-ruta" aria-labelledby="auRutaTit">\n'
            '        <h2 class="camino-tit" id="auRutaTit">El recorrido de esta investigación</h2>\n'
            '        <p class="camino-txt">Tres pasos: entender el caso, comprobar sus números y revisar los documentos que lo sostienen.</p>\n'
            '        <ol class="camino-pasos camino-tres">\n%s\n        </ol>\n      </section>') % '\n'.join(
        '          <li class="camino-paso%s"><span class="camino-num" aria-hidden="true">%d</span>'
        '<span class="camino-ico" aria-hidden="true">%s</span><b class="camino-que">%s</b>'
        '<span class="camino-det">%s</span><a class="camino-ir" href="%s">%s ➔</a></li>'
        % (aqui, n, ico, que, det, href, ir) for n, (ico, que, det, href, ir, aqui) in enumerate(pasos, 1))


def archivo(id_):
    return 'auditoria-%s.html' % id_


def otras(actual):
    filas = []
    for a in AUDITORIAS:
        if a[0] == actual:
            continue
        filas.append('          <a class="au-otra" href="%s"><img src="%s" alt="" loading="lazy">'
                     '<span class="au-otra-txt"><span class="au-otra-badge">%s</span>%s</span></a>'
                     % (archivo(a[0]), a[1], a[4], a[5]))
    return '\n'.join(filas)


def pagina(a, sello):
    id_, img, nota_img, alt, badge, titulo, pregunta = a
    # LEGO necesita el padron municipal del INEGI; las demas no lo cargan.
    extra = ('\n  <script src="assets/auditor/js/municipios-efipem.js?v=%s"></script>' % sello
             if id_ == 'lego-cienega' else '')
    return '''<!DOCTYPE html>
<!-- Página generada por herramientas/auditorias.py: no la edites a mano. -->
<html lang="es" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo_doc} · Auditoría en imágenes · Auditavisión</title>
  <meta name="description" content="{pregunta_attr}">
  <meta name="theme-color" content="#0b2a63">
  <meta name="color-scheme" content="light">
  <link rel="icon" href="{favicon}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/auditor/css/auditavision.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/civico.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/apartados.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/auditoria-imagen.css?v={sello}">
</head>
<body data-pagina="apartado">
{cabecera}

  <main class="apartado au-pagina" id="contenido">
    <header class="au-hero">
      <img class="au-hero-img" src="{img}" alt="{alt}">
      <span class="au-hero-ia">{nota_img}</span>
      <div class="au-hero-velo"></div>
      <div class="apartado-ancho au-hero-txt">
        <nav class="apartado-migas" aria-label="Estás en"><a href="index.html">Inicio</a> <span aria-hidden="true">›</span> <a href="index.html#auditoria-en-imagenes">Auditoría en imágenes</a> <span aria-hidden="true">›</span> <span>{titulo}</span></nav>
        <span class="au-hero-badge">{badge}</span>
        <h1 class="au-hero-tit">{titulo}</h1>
        <p class="au-hero-preg">{pregunta}</p>
      </div>
    </header>

    <div class="apartado-ancho apartado-cuerpo">
{ruta}

      <div id="auImg" class="au-raiz" data-id="{id}">
        <noscript><p>Esta página arma sus cuentas con JavaScript a partir de la base de datos de la plataforma. Actívalo para verlas.</p></noscript>
      </div>

      <section class="au-otras-sec" aria-labelledby="auOtrasTit">
        <h2 class="au-sec-tit" id="auOtrasTit">🖼️ Otras auditorías en imágenes</h2>
        <div class="au-otras">
{otras}
        </div>
      </section>
    </div>
  </main>

  <footer class="apartado-pie">
    <div class="apartado-ancho">
      <a class="apartado-volver" href="index.html#auditoria-en-imagenes">← Volver a Auditoría en imágenes</a>
      <a class="apartado-volver apartado-indice" href="indice.html">🗂️ Índice general</a>
      <span class="apartado-pie-txt">Auditavisión · Toda cifra lleva su fuente oficial. Versión publicada: <b>{sello}</b></span>
    </div>
  </footer>

  <script src="assets/auditor/js/audit-database.js?v={sello}"></script>{extra}
  <script src="assets/auditor/js/apartados.js?v={sello}"></script>
  <script src="assets/auditor/js/auditoria-imagen.js?v={sello}"></script>
</body>
</html>
'''.format(titulo_doc=re.sub('<[^>]+>', '', titulo), pregunta_attr=esc_attr(pregunta), favicon=FAVICON,
           sello=sello, cabecera=cabecera(archivo(id_), sello), img=img, alt=esc_attr(alt), nota_img=nota_img,
           titulo=titulo, badge=badge, pregunta=pregunta, id=id_, otras=otras(id_), extra=extra, ruta=ruta(id_))


def portada():
    """Escribe en index.html lo que la portada toma de aqui: los enlaces de
    las tres acciones de cada diapositiva (data-*) y la lista de
    investigaciones por tema. index.html se edita en binario para no tocar
    sus CRLF ni sus CR sueltos."""
    ruta_idx = os.path.join(RAIZ, 'index.html')
    d = open(ruta_idx, 'rb').read().decode('utf-8')
    au = {a[0]: a for a in AUDITORIAS}

    def attrs(m):
        id_ = m.group(2)
        ancla, _, insp, _ = RUTAS[id_]
        return '%s data-nombre="%s" data-numeros="sigue-el-dinero.html?abrir=%s" data-evidencia="%s"' % (
            m.group(1), esc_attr(re.sub('<[^>]+>', '', au[id_][5])), ancla, insp)
    d, n = re.subn(r'(<a class="showcase-slide" href="auditoria-([\w-]+)\.html")(?: data-nombre="[^"]*" data-numeros="[^"]*" data-evidencia="[^"]*")?',
                   attrs, d)
    temas = '\r\n'.join(
        '      <div class="portada-tema"><span class="portada-tema-tit">%s %s</span>%s</div>' % (
            ico, tit, ''.join('<a href="%s">%s</a>' % (archivo(i), au[i][5]) for i in ids))
        for ico, tit, ids in TEMAS)
    d, t = re.subn(r'(<!-- TEMAS:inicio[^>]*-->\r\n)[\s\S]*?(      <!-- TEMAS:fin -->)',
                   lambda m: m.group(1) + temas + '\r\n' + m.group(2), d)
    if n != len(AUDITORIAS) or t != 1:
        print('ERROR: la portada no tiene las %d diapositivas o el bloque de temas (%d, %d)' % (len(AUDITORIAS), n, t))
        return 1
    open(ruta_idx, 'wb').write(d.encode('utf-8'))
    return 0


def generar(sello):
    for a in AUDITORIAS:
        texto = pagina(a, sello).replace('\r\n', '\n').replace('\n', '\r\n')
        open(os.path.join(RAIZ, archivo(a[0])), 'wb').write(texto.encode('utf-8'))
    print('auditorías en imágenes: %d páginas generadas con el sello %s' % (len(AUDITORIAS), sello))
    return portada()
