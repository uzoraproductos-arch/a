#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera expedientes.html, la pagina de los Expedientes de casos por aclarar.

Hasta el 09-10-2026 los diez expedientes se desplegaban dentro del Modo
Inspector de la portada (bloque 3). Por la regla de AGENTS.md (5 bis) se
mudaron a su propia pagina. La pinta assets/auditor/js/expedientes.js con
las fichas de window.AUDIT_DB.expedientes: aqui no se escribe ni un monto,
solo el marco y los conceptos para leerlos.

Cada caso tiene su ancla, expedientes.html#exp-<id>; el motor manda ahi los
enlaces viejos (index.html?ir=expediente&ancla=<id>).

Lo llama apartados.generar(), asi que sello.py la regenera con el sello.
"""
import os

from apartados import RAIZ, FAVICON, cabecera

ARCHIVO = 'expedientes.html'

# Los cuatro pasos de un expediente: conceptos, sin cifras.
PASOS = [
    ('🏛️', 'La ASF revisa', 'Cada año la Auditoría Superior de la Federación revisa la Cuenta Pública y publica un informe por auditoría.'),
    ('🧾', 'Pide comprobantes', 'Si el ente no demuestra en qué se fue un peso, ese peso queda «por aclarar».'),
    ('⚖️', 'Promueve acciones', 'Pliegos de observaciones, promociones de responsabilidad, avisos al SAT o denuncias de hechos.'),
    ('🔎', 'Tú lo verificas', 'Cada cifra enlaza al informe oficial. Ábrelo y compruébalo con tus propios ojos.'),
]

# Las palabras que aparecen en cada caso, en llano.
GLOSA = [
    ('Por aclarar', 'Dinero que el ente no pudo comprobar al cierre de la auditoría. No es un robo probado: es una cuenta que sigue abierta.'),
    ('Pliego de observaciones', 'La ASF presume un daño a la Hacienda Pública y exige que se repare o se justifique.'),
    ('Promoción de responsabilidad', 'La ASF pide al órgano interno de control que investigue a las personas servidoras públicas.'),
    ('Recuperado', 'Lo que el ente ya devolvió o justificó durante la auditoría.'),
]


def pagina(sello):
    pasos = []
    for i, (ico, tit, txt) in enumerate(PASOS):
        if i:
            pasos.append('          <span class="ex-flecha" aria-hidden="true">➜</span>')
        pasos.append('          <div class="ex-paso"><span class="ex-paso-ico" aria-hidden="true">%s</span>'
                     '<b>%s</b><span>%s</span></div>' % (ico, tit, txt))
    glosa = '\n'.join('          <div><dt>%s</dt><dd>%s</dd></div>' % g for g in GLOSA)
    return '''<!DOCTYPE html>
<!-- Página generada por herramientas/expedientes.py: no la edites a mano. -->
<html lang="es" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Expedientes de casos por aclarar · Auditavisión</title>
  <meta name="description" content="Diez casos de alto impacto con lo que la Auditoría Superior de la Federación dejó por aclarar: megaobras, Pemex, salud, Segalmex y deuda de los estados.">
  <meta name="theme-color" content="#0b2a63">
  <meta name="color-scheme" content="light">
  <link rel="icon" href="{favicon}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/auditor/css/auditavision.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/civico.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/apartados.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/expedientes.css?v={sello}">
</head>
<body data-pagina="apartado">
{cabecera}

  <main class="apartado ex-pagina" id="contenido">
    <header class="apartado-cab">
      <div class="apartado-ancho">
        <nav class="apartado-migas" aria-label="Estás en"><a href="index.html">Inicio</a> <span aria-hidden="true">›</span> <a href="busca-y-verifica.html">Busca y verifica</a> <span aria-hidden="true">›</span> <span>Expedientes de casos</span></nav>
        <span class="apartado-lema">📂 Lo que sigue sin explicarse</span>
        <h1 class="apartado-titulo">Expedientes de casos por aclarar</h1>
        <p class="apartado-entrada">Diez casos de alto impacto, contados con los informes de la Auditoría Superior de la Federación y el Sistema de Alertas de Hacienda: <b>cuánto dinero no se pudo comprobar, quién lo manejó y qué acciones se promovieron.</b></p>
      </div>
    </header>

    <div class="apartado-ancho apartado-cuerpo">
      <section class="apartado-seccion" id="como-se-lee" aria-labelledby="como-se-lee-tit">
        <div class="apartado-seccion-cab">
          <h2 class="apartado-seccion-titulo" id="como-se-lee-tit">🧭 Cómo nace un expediente</h2>
          <p class="apartado-seccion-texto">Cuatro pasos, del informe a tus manos.</p>
        </div>
        <div class="ex-mapa">
{pasos}
        </div>
        <dl class="ex-glosa">
{glosa}
        </dl>
      </section>

      <section class="apartado-seccion" id="casos" aria-labelledby="casos-tit">
        <div class="apartado-seccion-cab">
          <h2 class="apartado-seccion-titulo" id="casos-tit">📂 Los casos</h2>
          <p class="apartado-seccion-texto">Elige un tema o pulsa un caso para ir directo a su expediente.</p>
        </div>
        <div class="ex-filtros" role="group" aria-label="Filtrar por tema">
          <span class="ex-conteo">Casos a la vista: <b id="exConteo">0</b></span>
          <div class="ex-chips" id="exChips"></div>
        </div>
        <div class="ex-indice" id="exIndice"></div>
      </section>

      <div id="exCasos" class="ex-casos">
        <noscript><p>Esta página arma los expedientes con JavaScript a partir de la base de datos de la plataforma. Actívalo para verlos.</p></noscript>
      </div>
    </div>
  </main>

  <footer class="apartado-pie">
    <div class="apartado-ancho">
      <a class="apartado-volver" href="busca-y-verifica.html">← Volver a Busca y verifica</a>
      <span class="apartado-pie-txt">Auditavisión · Toda cifra lleva su fuente oficial. Versión publicada: <b>{sello}</b></span>
    </div>
  </footer>

  <script src="assets/auditor/js/audit-database.js?v={sello}"></script>
  <script src="assets/auditor/js/apartados.js?v={sello}"></script>
  <script src="assets/auditor/js/expedientes.js?v={sello}"></script>
</body>
</html>
'''.format(favicon=FAVICON, sello=sello, cabecera=cabecera('busca-y-verifica.html', sello),
           pasos='\n'.join(pasos), glosa=glosa)


def generar(sello):
    texto = pagina(sello).replace('\r\n', '\n').replace('\n', '\r\n')
    open(os.path.join(RAIZ, ARCHIVO), 'wb').write(texto.encode('utf-8'))
    print('expedientes: %s generada con el sello %s' % (ARCHIVO, sello))
    return 0
