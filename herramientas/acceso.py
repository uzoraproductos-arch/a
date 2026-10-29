#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Códigos de acceso a la versión de prueba (pedido del autor, 29-10-2026:
«que funcionara un poquito como lo hace este Nintendo Switch… cuatro casillas
de un lado, espacio, cuatro casillas de otro lado, y yo estar administrando
tanto el número de código como el tiempo de apertura»).

Mientras la plataforma se perfecciona todo es gratis: el código solo abre la
puerta. Tres piezas:

- canjea-tu-codigo.html: la entrada, con la acuarela de la ciudad, lo último
  verificado, las ocho casillas (XXXX-XXXX) y «¿No tienes código? Obtén uno»,
  que deja el correo para que el autor mande uno. El canje da un «pase» que
  se queda en el navegador, sin cuenta ni correo, y abre la ventana
  «¡Felicidades! Cuentas con…».
- administracion-codigos.html: el panel del autor. Entra con su correo (enlace
  mágico de Supabase), genera códigos con su duración y sus usos, los revoca y
  los descarga en CSV. Solo lo abre una cuenta de la tabla administradores.
- assets/auditor/js/acceso.js, en el <head> de todas las páginas: si el
  candado está puesto y el navegador no trae un pase vigente, manda a
  canjea-tu-codigo.html. Su configuración la escribe este módulo.

La base vive en supabase/migrations/20261030000001_codigos.sql y la función
que canjea, en supabase/functions/codigo. **El candado está encendido**
desde el 30-10-2026 («enciende el código», pedido del autor); se apaga con
CANDADO = False. En localhost no se pide código, para las pruebas.

Ojo, y se le dice al autor: en un sitio estático el candado es del
navegador. Detiene a quien entra por la puerta, no a quien lee el código de
la página. Para cerrar de verdad, el sitio necesita un servidor que revise el
pase antes de entregar la página (Vercel, fase 1 de docs/LANZAMIENTO.md).
"""
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'acceso.js')

# El candado: True = sin un código vigente no se entra a la plataforma.
CANDADO = True
# El proyecto de Supabase (creado por el autor el 29-10-2026) y su llave
# PÚBLICA (publishable). Va en la página por diseño; la llave de servicio
# (secret), nunca. Va aparte de FUNCIONES de apartados.py: los códigos se
# conectan sin encender el envío de los formularios, que espera su aviso.
SUPABASE_URL = 'https://nuqiyzcilbrrlezmesnf.supabase.co'
SUPABASE_ANON = 'sb_publishable_gf28FUrT1zcoaGl4C2f_aQ_exkzAQ9g'

CANJE = 'canjea-tu-codigo.html'
PANEL = 'administracion-codigos.html'
# Las páginas que abren sin código: la del canje, el panel y lo que la ley
# obliga a tener siempre a la vista.
LIBRES = [CANJE, PANEL, 'aviso-de-privacidad.html']

# Las duraciones del panel (intervalos de PostgreSQL) y cómo se leen.
DURACIONES = [
    ('1 day', '1 día'), ('3 days', '3 días'), ('5 days', '5 días'), ('7 days', '1 semana'),
    ('14 days', '2 semanas'), ('1 mon', '1 mes'), ('3 mons', '3 meses'), ('6 mons', '6 meses'), ('1 year', '1 año'),
    ('100 years', 'Ilimitado'),
]


def config():
    base = SUPABASE_URL.rstrip('/')
    funciones = (base + '/functions/v1') if base else ''
    if CANDADO and not (base and SUPABASE_ANON):
        raise SystemExit('acceso.py: CANDADO está puesto, pero faltan SUPABASE_URL o SUPABASE_ANON: '
                         'nadie podría canjear un código y la plataforma quedaría cerrada para todos.')
    return {
        'candado': CANDADO,
        'funciones': funciones,
        'supabase': base,
        'anon': SUPABASE_ANON,
        'canje': CANJE,
        'panel': PANEL,
        'libres': LIBRES,
    }


def escribir_config():
    """Pone la configuración dentro de acceso.js, entre sus dos marcas."""
    t = open(JS, encoding='utf-8').read()
    nuevo = '/*config*/%s/*fin-config*/' % json.dumps(config(), ensure_ascii=False, separators=(',', ':'))
    t2 = re.sub(r'/\*config\*/.*?/\*fin-config\*/', lambda m: nuevo, t, count=1, flags=re.S)
    if t2 == t and nuevo not in t:
        raise SystemExit('acceso.py: no encontré las marcas /*config*/ … /*fin-config*/ en acceso.js')
    if t2 != t:
        open(JS, 'w', encoding='utf-8', newline='').write(t2)


def _casillas():
    uno = lambda i: ('<input class="ac-casilla" type="text" inputmode="numeric" autocomplete="off" '
                     'spellcheck="false" maxlength="1" aria-label="Número %d de 8" data-i="%d">' % (i + 1, i))
    return ('<div class="ac-casillas" role="group" aria-label="Tu código, de ocho números">'
            '<span class="ac-grupo">%s</span><span class="ac-guion" aria-hidden="true">–</span><span class="ac-grupo">%s</span></div>'
            % (''.join(uno(i) for i in range(4)), ''.join(uno(i) for i in range(4, 8))))


def _ultimas(n=3):
    """Las notas «Al momento» más nuevas, para la entrada: solo el título y su
    fecha (la nota completa vive en Noticias)."""
    import asistente_personajes
    cols = [c for c in asistente_personajes.columnas()[0] if c.get('seccion') == 'Al momento' and c.get('fecha')]
    clave = lambda c: tuple(reversed(c['fecha'].split('-')))
    return sorted(cols, key=clave, reverse=True)[:n]


def entrada_html(sello):
    """canjea-tu-codigo.html: la entrada de la versión de prueba (pedido del
    autor, 29-10-2026: «de un lado… la imagen de la ciudad… y por la parte de
    que quieres saber sobre las finanzas públicas, descubre el gasto y
    posiblemente alguna noticia… ingresa con tu código promocional. ¿No tienes
    código? Dale clic en obtener uno»). Página propia, sin el menú: mientras el
    candado esté puesto es la única puerta."""
    import html
    import apartados
    esc = lambda t: html.escape(t, quote=True)
    notas = ''.join('\n          <li><span class="ac-n-fecha">%s</span> %s</li>' % (esc(c['fecha']), esc(c['titulo'])) for c in _ultimas())
    sin_base = '' if config()['funciones'] else (
        '\n        <p class="ac-aviso" id="acSinBase">⏳ El canje se enciende cuando la plataforma tenga su base de datos. '
        'Por ahora la entrada es libre: <a href="index.html">pasa a la plataforma</a>.</p>')
    casillas = _casillas().replace('data-i="0"', 'data-i="0" id="acCasilla0"')
    return """<!DOCTYPE html>
<!-- Página generada por herramientas/acceso.py: no la edites a mano. -->
<html lang="es" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ingresa con tu código · Auditavisión</title>
  <meta name="description" content="Auditavisión, el gasto público a la vista. Versión de prueba por invitación: ingresa con tu código o pide uno.">
  <meta name="theme-color" content="#0b2a63">
  <meta name="color-scheme" content="light">
  <link rel="icon" href="assets/auditor/img/logo-auditavision.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=JetBrains+Mono:wght@500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="assets/auditor/js/iconos.js?v={sello}"></script>
  <script src="assets/auditor/js/acceso.js?v={sello}"></script>
  <link rel="stylesheet" href="assets/auditor/css/apartados.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/acceso.css?v={sello}">
</head>
<body class="ac-entrada-cuerpo">
  <main class="ac-entrada" id="contenido">
    <figure class="ac-foto">
      <img src="assets/auditor/img/portada/cabecera-lluvia.webp" alt="Una calle de ciudad bajo la lluvia, con torres entre la niebla, luces azules y gente caminando." width="1376" height="768">
      <figcaption>Ilustración generada con IA</figcaption>
    </figure>
    <section class="ac-lado" aria-labelledby="acTitulo">
      <p class="ac-marca">{logo}<span><b>Auditavisión</b><small>El gasto público, a la vista</small></span></p>
      <h1 id="acTitulo">¿Quieres saber en qué se gasta el dinero de todos?</h1>
      <p class="ac-lema"><b>Descubre el gasto público:</b> de dónde sale cada peso, quién lo gasta y quién revisa que se use bien. Todo con documentos oficiales.</p>
      <div class="ac-noticias">
        <h2>Lo último, verificado</h2>
        <ul>{notas}
        </ul>
      </div>
      <form class="ac-canje" id="acCanje" novalidate>
        <label class="ac-et" for="acCasilla0">Ingresa con tu código promocional</label>
        {casillas}
        <p class="ac-ayuda">Ocho números. Si lo copiaste, pégalo en la primera casilla.</p>
        <button class="sz-btn sz-btn-of ac-boton" type="submit" disabled>Ingresar</button>
        <p class="ac-estado" id="acEstado" role="status" aria-live="polite"></p>
      </form>{sin_base}
      <div class="ac-tuyo" id="acTuyo" hidden></div>
      <div class="ac-obtener">
        <p>¿No tienes código? <button class="ac-enlace" type="button" id="acObtener" aria-expanded="false" aria-controls="acPedir">Obtén uno</button></p>
        <form class="ac-pedir" id="acPedir" novalidate hidden>
          <p class="ac-pedir-txt">Déjanos tu correo y te mandamos tu código. La versión de prueba es por invitación: la estamos abriendo poco a poco.</p>
          <label class="ac-et" for="acPCorreo">Tu correo</label>
          <input class="ac-campo" id="acPCorreo" name="correo" type="email" autocomplete="email" required>
          <label class="ac-et" for="acPNombre">Tu nombre <small>(si quieres)</small></label>
          <input class="ac-campo" id="acPNombre" name="nombre" type="text" autocomplete="name" maxlength="80">
          <label class="ac-et" for="acPMotivo">¿A qué te dedicas o para qué lo quieres? <small>(si quieres)</small></label>
          <input class="ac-campo" id="acPMotivo" name="motivo" type="text" maxlength="300">
          <label class="ac-check"><input type="checkbox" name="acepta" required> Acepto el <a href="aviso-de-privacidad.html#codigos" target="_blank" rel="noopener">aviso de privacidad</a>: mi correo solo sirve para mandarme el código.</label>
          <button class="sz-btn sz-btn-of" type="submit">Pedir mi código</button>
          <p class="ac-estado" id="acPEstado" role="status" aria-live="polite"></p>
        </form>
      </div>
      <p class="ac-pie">Versión de prueba · gratis · <a href="aviso-de-privacidad.html">Aviso de privacidad</a> · <span>{sello}</span></p>
    </section>
  </main>
  <dialog class="ac-felicidades" id="acFelicidades" aria-labelledby="acFTit">
    <p class="ac-f-ico" aria-hidden="true">👏</p>
    <h2 id="acFTit">¡Felicidades!</h2>
    <p class="ac-f-cuanto" id="acFCuanto"></p>
    <p class="ac-f-hasta" id="acFHasta"></p>
    <a class="sz-btn sz-btn-of ac-boton" id="acFEntrar" href="index.html">Entrar a la plataforma</a>
  </dialog>
  <script src="assets/auditor/js/acceso-paginas.js?v={sello}"></script>
</body>
</html>
""".format(sello=sello, logo=apartados.LOGO_IMG, notas=notas, casillas=casillas, sin_base=sin_base)


def escribir_entrada(sello):
    open(os.path.join(RAIZ, CANJE), 'w', encoding='utf-8', newline='\n').write(entrada_html(sello))


def pagina_panel():
    opciones = ''.join('<option value="%s"%s>%s</option>' % (v, ' selected' if v == '7 days' else '', t) for v, t in DURACIONES)
    bloque = ('<div class="ac-panel" id="acPanel">\n'
              '  <form class="ac-entrar" id="acEntrar" novalidate>\n'
              '    <label class="ac-et" for="acCorreo">Tu correo de administración</label>\n'
              '    <input class="ac-campo" id="acCorreo" type="email" autocomplete="email" required>\n'
              '    <button class="sz-btn sz-btn-of" type="submit">Mandarme el enlace para entrar</button>\n'
              '    <p class="ac-estado" id="acEntrarEstado" role="status" aria-live="polite"></p>\n'
              '  </form>\n'
              '  <div class="ac-admin" id="acAdmin" hidden>\n'
              '    <p class="ac-sesion"><span id="acQuien"></span> <button class="sz-btn ac-chico" type="button" id="acSalir">Salir</button></p>\n'
              '    <section class="ac-semana" aria-labelledby="acSemTit">\n'
              '      <h3 id="acSemTit">Tu código de administración</h3>\n'
              '      <p class="ac-semana-cod"><button class="ac-cod" type="button" id="acSemCod" title="Copiar">····-····</button></p>\n'
              '      <p class="ac-ayuda" id="acSemVence">Es solo tuyo y cambia solo cada lunes a las 0:00 (hora de la Ciudad de México). '
              'Cuando cambie, tu acceso termina y la entrada te manda aquí por el nuevo.</p>\n'
              '      <p class="ac-acciones"><button class="sz-btn sz-btn-of" type="button" id="acComoAdmin">Abrir la plataforma con mi código</button> '
              '<button class="sz-btn ac-chico ac-claro" type="button" id="acSemCambiar">Cambiarlo ahora</button></p>\n'
              '    </section>\n'
              '    <p class="ac-estado" id="acComoAdminEstado" role="status" aria-live="polite"></p>\n'
              '    <section class="ac-solicitudes" aria-labelledby="acSolTit">\n'
              '      <h3 id="acSolTit">Solicitudes de código <span class="ac-chip ac-sin_usar" id="acSolCuenta"></span></h3>\n'
              '      <p class="ac-ayuda">Quien pidió código desde la entrada. Elige cuánto le das, asigna y mándaselo desde tu correo.</p>\n'
              '      <div class="ac-tabla-caja"><table class="ac-tabla" id="acSol">\n'
              '        <thead><tr><th>Correo</th><th>Quién y para qué</th><th>Pidió</th><th>Estado</th><th></th></tr></thead>\n'
              '        <tbody></tbody></table></div>\n'
              '    </section>\n'
              '    <form class="ac-generar" id="acGenerar" novalidate>\n'
              '      <h3>Generar códigos</h3>\n'
              '      <div class="ac-fila">\n'
              '        <label>Cantidad <input class="ac-campo" name="cantidad" type="number" min="1" max="500" value="10" required></label>\n'
              '        <label>Duración <select class="ac-campo" name="duracion">%s<option value="otra">Otra (en días)</option></select></label>\n'
              '        <label class="ac-otra" hidden>Días <input class="ac-campo" name="dias" type="number" min="1" max="1825" value="10"></label>\n'
              '        <label>Personas por código <input class="ac-campo" name="usos" type="number" min="1" max="10000" value="1" required></label>\n'
              '        <label>Canjear antes del <input class="ac-campo" name="antes" type="date"></label>\n'
              '        <label class="ac-ancho">Nota (opcional) <input class="ac-campo" name="nota" type="text" maxlength="120" placeholder="Para quién son: «Taller», «Prensa»…"></label>\n'
              '        <label class="ac-ancho">Código propio (opcional) <input class="ac-campo" name="propio" type="text" inputmode="numeric" maxlength="9" autocomplete="off" spellcheck="false" placeholder="Vacío: salen al azar. Ejemplo: 2026-1029"></label>\n'
              '        <p class="ac-ayuda ac-ancho">Si escribes un código propio se crea solo ese, con la duración y los usos de arriba. Lleva 8 números, del 0 al 9. La nota es opcional.</p>\n'
              '      </div>\n'
              '      <p class="ac-acciones"><button class="sz-btn sz-btn-of" type="submit">Generar</button>\n'
              '        <button class="sz-btn ac-claro" type="button" id="acCsv">Descargar CSV</button>\n'
              '        <button class="sz-btn ac-claro" type="button" id="acCsvUso">Descargar el registro de uso</button>\n'
              '        <button class="sz-btn ac-claro" type="button" id="acRecargar">Actualizar la lista</button></p>\n'
              '      <p class="ac-estado" id="acGenerarEstado" role="status" aria-live="polite"></p>\n'
              '    </form>\n'
              '    <h3 class="ac-reg-tit">Registro de códigos</h3>\n'
              '    <div class="ac-resumen" id="acResumen"></div>\n'
              '    <div class="ac-orden">\n'
              '      <div class="ac-vista" role="group" aria-label="Qué códigos ver">\n'
              '        <button class="sz-btn ac-chico ac-claro" type="button" data-vista="activos" aria-pressed="true">Activos <b id="acNAct">0</b></button>\n'
              '        <button class="sz-btn ac-chico ac-claro" type="button" data-vista="archivados" aria-pressed="false">Archivados <b id="acNArc">0</b></button></div>\n'
              '      <label class="ac-busca">Buscar <input class="ac-campo" id="acBusca" type="search" placeholder="Código o nota" autocomplete="off"></label>\n'
              '      <button class="sz-btn ac-chico ac-claro" type="button" id="acArchInact" title="Revocados, terminados y vencidos">Archivar los que ya no abren</button>\n'
              '    </div>\n'
              '    <p class="ac-ayuda">Archivar solo ordena: el código sigue abriendo si alguien lo usa. Eliminar lo borra para siempre y quien lo canjeó pierde su tiempo.</p>\n'
              '    <p class="ac-estado" id="acTablaEstado" role="status" aria-live="polite"></p>\n'
              '    <div class="ac-tabla-caja"><table class="ac-tabla" id="acTabla">\n'
              '      <thead><tr><th>Código</th><th>Duración</th><th>Usos</th><th>Estado</th><th>Nota</th><th>Acciones</th></tr></thead>\n'
              '      <tbody></tbody></table></div>\n'
              '  </div>\n'
              '</div>') % opciones
    return {
        'archivo': PANEL,
        'menu': 'Administración de códigos',
        'icono': '🗝️',
        'titulo': 'Administración de códigos',
        'lema': 'Solo para la administración',
        'entrada': ('Aquí generas los códigos de invitación, eliges cuánto dura cada uno y cuántas personas lo pueden usar, '
                    'y los editas, archivas, revocas o eliminas cuando quieras. Solo abre con una cuenta dada de alta en la administración.'),
        'noindex': True,
        'estilos': ['acceso.css'],
        'scripts': ['acceso-paginas.js'],
        'secciones': [{'id': 'panel', 'titulo': 'Los códigos', 'texto': 'El tiempo de cada código corre desde que se canjea.', 'tarjetas': [], 'bloque': bloque}],
    }


def paginas():
    """Las páginas con el molde de apartados.py: el panel. La entrada tiene el
    suyo (escribir_entrada)."""
    escribir_config()
    return [pagina_panel()]
