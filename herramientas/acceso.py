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
que canjea, en supabase/functions/codigo. El candado se encendió el 30-10-2026
(«enciende el código», pedido del autor) y **se apagó el 25-11-2026 (Ronda 22,
decisión del autor: abrir la plataforma al público y a Google)**: cualquiera
entra sin código. La entrada sigue como página para ingresar, las cuatro
portadas privadas y el panel siguen solo para la administración, y los
Servicios siguen pidiendo un código vigente (SERVICIOS_OPERAN de apartados.py).

Ojo, y se le dice al autor: en un sitio estático el candado es del
navegador. Detiene a quien entra por la puerta, no a quien lee el código de
la página. Para cerrar de verdad, el sitio necesita un servidor que revise el
pase antes de entregar la página (Vercel, fase 1 de docs/LANZAMIENTO.md).
"""
import json
import os
import re
import seguridad

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'acceso.js')

# El candado: True = sin un código vigente no se entra a la plataforma.
# Ronda 22 (25-11-2026, decisión del autor): apagado, la plataforma abre al público y a Google.
CANDADO = False
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
LIBRES = [CANJE, PANEL, 'aviso-de-privacidad.html', 'derecho-de-replica.html', 'servicios.html', 'servicios-por-que.html',
          'servicios-fraude-y-lavado.html', 'servicios-catalogo.html', 'servicios-tu-perfil.html', 'servicios-empieza-gratis.html',
          'servicios-como-se-cobra.html', 'servicios-calendario.html', 'servicios-preguntas.html', 'servicios-cotiza.html']  # réplica: art. 7, siempre a la vista (02-11-2026); servicios: la página de venta no puede pedir código (11-11-2026)

# Las duraciones del panel (intervalos de PostgreSQL) y cómo se leen.
DURACIONES = [
    ('1 day', '1 día'), ('3 days', '3 días'), ('5 days', '5 días'), ('7 days', '1 semana'),
    ('14 days', '2 semanas'), ('1 mon', '1 mes'), ('3 mons', '3 meses'), ('6 mons', '6 meses'), ('1 year', '1 año'),
    ('100 years', 'Ilimitado'),
]


def _enciclopedia():
    """La antigua Enciclopedia, en privado (Ronda 7, decisión del autor, 22-11-2026): sus cuatro portadas ya no tienen
    liga pública (traslado.py) y acceso.js solo las abre en el navegador de la administración."""
    import traslado
    import auditor_bento
    nom = {'enciclopedia-auditavision.html': ('libro', 'La Enciclopedia', 'Su portada, con Números, Datos y Aprende.'),
           'sigue-el-dinero.html': ('panel', 'Números', 'El índice de Presupuesto, Gasto público, Cuentas claras, Baja al territorio y las Herramientas.'),
           'descarga-los-datos.html': ('carpeta', 'Datos', 'El índice de los Poderes, la salud, el ambiente, el padrón del SAT y los informes.'),
           'aprende.html': ('pluma', 'Aprende', 'El índice de la Biblioteca del Erario, cómo se audita, el fraude en números y los recursos naturales.')}
    return ('      <h3>La Enciclopedia, en privado</h3>\n'
            '      <details class="ac-nota"><summary>Por qué está aquí</summary>\n'
            '      <p class="ac-ayuda">Desde la Ronda 7 sus páginas viven en el Planisferio (cada una en su dimensión) y la Biblioteca del Erario en '
            'Comunidad. Sus cuatro portadas quedan aquí, solo para ti: el público ya no tiene ligas a ellas y, si alguien llega por una vieja, '
            'la página lo manda al Planisferio.</p></details>\n'
            '      <ul class="ac-enc">\n%s      </ul>\n') % ''.join(
        '        <li><a href="%s">%s <b>%s</b> <small>%s</small></a></li>\n'
        % (f, auditor_bento.ico(nom[f][0], 22, 'ac-i'), nom[f][1], nom[f][2])
        for f in traslado.PRIVADAS)


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
        'privadas': list(__import__('traslado').PRIVADAS),
        'fuera': 'planisferio.html',
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
    uno = lambda i: ('<input class="ac-casilla" type="text" autocomplete="off" autocapitalize="characters" '
                     'spellcheck="false" maxlength="1" aria-label="Carácter %d de 8" data-i="%d">' % (i + 1, i))
    return ('<div class="ac-casillas" role="group" aria-label="Tu código, de ocho números y letras">'
            '<span class="ac-grupo">%s</span><span class="ac-guion" aria-hidden="true">–</span><span class="ac-grupo">%s</span></div>'
            % (''.join(uno(i) for i in range(4)), ''.join(uno(i) for i in range(4, 8))))


def _ultimas(n=3):
    """Las notas «Al momento» más nuevas, para la entrada: solo el título y su
    fecha (la nota completa vive en Noticias)."""
    import asistente_personajes
    cols = [c for c in asistente_personajes.columnas()[0] if c.get('seccion') == 'Al momento' and c.get('fecha')]
    clave = lambda c: tuple(reversed(c['fecha'].split('-')))
    return sorted(cols, key=clave, reverse=True)[:n]


# La portada de acceso (rediseño del autor, 22-11-2026). Las preguntas invitan a mirar los documentos: no
# afirman cifras ni culpan a un gobierno o a un partido (AGENTS.md §2). Las respuestas de FAQ_ENTRADA dicen
# solo lo que la plataforma es y hace, y van iguales en la página y en sus datos estructurados (FAQPage).
DESC_ENTRADA = ('Fraudes, prevención de lavado de dinero, desvío de recursos y deuda pública en México, con sus documentos oficiales: la lista 69-B '
                'del SAT, los proveedores sancionados, la Auditoría Superior, los contratos y lo que debe cada estado. Versión de prueba por invitación.')
QUIENES_ENTRADA = ('Somos una plataforma cívica e independiente que sigue el dinero público de México: de dónde sale, quién lo gasta y '
                   'quién revisa que se use bien. Cada cifra trae su documento oficial (DOF, Hacienda, ASF, INEGI) y lo que no se puede '
                   'comprobar se dice como pendiente.')
# Ronda 7 (22-11-2026, decisión del autor): el gancho de la entrada son cuatro ejes. Las preguntas invitan a ver los documentos:
# nunca afirman una cifra ni culpan a un gobierno, a un partido o a una empresa (AGENTS.md §2 y §2 bis).
PREGUNTAS_ENTRADA = [
    '¿Tu proveedor está en la lista 69-B del SAT o en el directorio de sancionados?',
    '¿Cuántas denuncias por fraude hubo en tu municipio el año pasado?',
    '¿Revisas a tus clientes y proveedores antes de pagar, como pide la prevención de lavado?',
    '¿Tu contraparte aparece en las listas de sanciones de la OFAC o de la ONU?',
    '¿Cuánto dinero dejó por aclarar la Auditoría Superior en la Cuenta Pública?',
    '¿Quién ganó los contratos de la obra de tu ciudad?',
    '¿Cuánto debe tu estado y a qué bancos le debe?',
    '¿Qué créditos firmó tu municipio y con quién?',
]
# Los cuatro ejes: (ícono, título, texto, [(clave de monetizacion.contadores(), cómo se dice aquí)], liga para verlo).
# Los números se cuentan de los archivos de la base al generar (monetizacion.contadores()): ninguno se escribe aquí.
EJES_ENTRADA = [
    ('🚨', 'Fraudes', 'Las denuncias por fraude municipio por municipio, las empresas que el SAT señala por facturas simuladas y los proveedores sancionados.',
     [('69b', 'RFC en la lista 69-B del SAT, con su situación'), ('sancionados', 'empresas proveedoras y contratistas sancionadas'),
      ('municipios', 'municipios y alcaldías con sus carpetas por fraude del SESNSP')]),
    ('🧺', 'Prevención de lavado (PLD)', 'Revisa a tus clientes y proveedores contra las listas oficiales antes de pagar o de firmar. Te damos la señal y su '
     'documento; la decisión y el cumplimiento siguen siendo tuyos.',
     [('padron', 'RFC en las listas del SAT (arts. 69, 17-H Bis y 69-B Bis)'), ('ofac-onu', 'registros de las listas de la OFAC y la ONU')]),
    ('🔎', 'Desvío de recursos', 'Lo que la Auditoría Superior dejó por aclarar, los contratos públicos y las megaobras, con su documento. Un monto por aclarar '
     'no es un desfalco comprobado: es lo que faltaba acreditar al cierre de la auditoría.',
     [('asf', 'auditorías de la ASF a la Cuenta Pública 2024'), ('contratos', 'contratos públicos de ComprasMX')]),
    ('🏦', 'Deuda pública', 'Cuánto debe cada estado y a qué bancos o instituciones, crédito por crédito, según el Registro Público Único de Hacienda.',
     [('rpu', 'créditos y obligaciones de estados y municipios, con su acreedor')]),
]
# Ronda 12 (23-11-2026, Paquete de Datos 10): la imagen editorial aprobada por el autor (Opción 2), con su huella.
FOTO_ENTRADA = ('portada-acceso-editorial.webp',
                'Arquitectura cívica mexicana al amanecer: un muro azul marino a la izquierda y, a la derecha, un paseo arbolado con '
                'jacarandas en flor, cantera clara y luz cálida de mañana.',
                '07e1cc48e6e85e2ec9ae7a7bdc5febfeddf024f739da31d957ed76220df6d9f7')
# La tira del hero: (clave de monetizacion.contadores(), cómo se dice aquí).
TIRA_ENTRADA = [('69b', 'RFC en la lista 69-B del SAT'), ('contratos', 'contratos públicos de ComprasMX'),
                ('municipios', 'municipios y alcaldías con su ficha')]


def _foto_ok():
    import hashlib
    ruta = os.path.join(RAIZ, 'assets', 'auditor', 'img', 'portada', FOTO_ENTRADA[0])
    if hashlib.sha256(open(ruta, 'rb').read()).hexdigest() != FOTO_ENTRADA[2]:
        raise SystemExit('acceso.py: la imagen de la entrada no es la aprobada (%s): revisa su huella' % FOTO_ENTRADA[0])


FAQ_ENTRADA = [
    ('¿Qué es Auditavisión?', 'Una plataforma cívica que reúne y explica en sencillo el dinero público de México: impuestos, presupuesto, '
     'deuda, contratos y lo que la Auditoría Superior de la Federación dejó por aclarar. Tiene un chat, el Auditor, que contesta con esos datos.'),
    ('¿De dónde salen los datos?', 'De documentos oficiales publicados para todos: el Diario Oficial de la Federación, la Secretaría de Hacienda, '
     'la Auditoría Superior de la Federación, el INEGI, Banxico y los congresos. Cada cifra lleva su fuente y su estado: oficial, auditada o pendiente.'),
    ('¿Qué puedo revisar de fraudes, lavado, desvíos y deuda?', 'Si un RFC está en la lista 69-B del SAT, en el directorio de proveedores '
     'sancionados o en las listas de la OFAC y la ONU; las denuncias por fraude de cada municipio; lo que la Auditoría Superior dejó por aclarar y '
     'los contratos públicos; y cuánto debe cada estado y a quién. Todo con su documento, como señal para revisar y nunca como acusación.'),
    ('¿Toma partido?', 'No. Las mismas reglas valen para todos los gobiernos y todos los partidos: se muestra lo que dice el documento, y una '
     'acusación nunca se presenta como una condena.'),
    ('¿Cómo entro?', 'La versión de prueba es gratis y por invitación: escribe tu código de acceso de ocho caracteres o pide uno con tu correo.'),
]


def entrada_html(sello):
    """canjea-tu-codigo.html: la entrada de la versión de prueba. Desde la Ronda 12 (23-11-2026) va en dos
    planos: el hero con la imagen editorial y la tarjeta de dos pestañas, y el cuerpo con los ejes, lo último
    y las preguntas frecuentes (docs/ux/REDISENO-PORTAL-ACCESO.md). Origen (pedido del
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
    # Rediseño del autor (22-11-2026): la acuarela se queda; el lado del texto va limpio y concreto
    # (referencia: getfinos.com), con «¿Quiénes somos?», preguntas que aparecen una a una (todas en el
    # HTML, para los buscadores; sin animación si el lector la apagó) y el código al centro. Las
    # preguntas no afirman cifras ni toman partido (AGENTS.md §2): invitan a ver los documentos.
    preguntas = ''.join('\n          <li>%s</li>' % esc(q) for q in PREGUNTAS_ENTRADA)
    import monetizacion
    cuenta = {c[0]: c for c in monetizacion.contadores()}
    ejes = ''.join(
        '\n          <article class="ac-eje"><h3><span aria-hidden="true">%s</span> %s</h3><p>%s</p><ul>%s</ul></article>' % (
            ico, esc(tit), esc(tx), ''.join('<li><b>%s</b> %s</li>' % (format(cuenta[k][1], ','), esc(et)) for k, et in cifras))
        for ico, tit, tx, cifras in EJES_ENTRADA)
    # Ronda 12: tres cifras contadas de la base, en la tira del hero (ninguna se escribe aquí).
    tira = ''.join('\n            <div><dt>%s</dt><dd>%s</dd></div>' % (format(cuenta[k][1], ','), esc(et)) for k, et in TIRA_ENTRADA)
    _foto_ok()
    faq = ''.join('\n          <details class="ac-faq-p"><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(r)) for q, r in FAQ_ENTRADA)
    url = apartados.SITIO + CANJE
    ld = json.dumps([
        {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Auditavisión', 'url': apartados.SITIO, 'inLanguage': 'es-MX',
         'description': DESC_ENTRADA, 'keywords': 'fraudes, prevención de lavado de dinero, PLD, desvío de recursos, deuda pública, lista 69-B, '
         'proveedores sancionados, Auditoría Superior de la Federación, contratos públicos, México',
         'about': [{'@type': 'Thing', 'name': t, 'description': x} for _i, t, x, _c in EJES_ENTRADA]},
        {'@context': 'https://schema.org', '@type': 'Organization', 'name': 'Auditavisión', 'url': apartados.SITIO,
         'logo': apartados.SITIO + 'assets/auditor/img/logo-auditavision.svg', 'description': QUIENES_ENTRADA},
        {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': r}} for q, r in FAQ_ENTRADA]},
    ], ensure_ascii=False).replace('</', '<\\/')
    return """<!DOCTYPE html>
<!-- Página generada por herramientas/acceso.py: no la edites a mano. -->
<html lang="es-MX" data-theme="light">
<head>
  <meta charset="UTF-8">
  {csp}
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Auditavisión · Fraudes, prevención de lavado, desvío de recursos y deuda pública de México, con documentos oficiales</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Auditavisión">
  <meta property="og:locale" content="es_MX">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="Auditavisión · Fraudes, lavado, desvíos y deuda pública, con documentos">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{sitio}assets/auditor/img/portada/{foto}">
  <meta property="og:image:alt" content="{foto_alt}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#0b2a63">
  <meta name="color-scheme" content="light">
  <link rel="icon" href="assets/auditor/img/logo-auditavision.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=JetBrains+Mono:wght@500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="assets/auditor/js/iconos.js?v={sello}"></script>
  <script src="assets/auditor/js/acceso.js?v={sello}"></script>
  <script src="assets/auditor/js/tokens.js?v={sello}"></script>
  <link rel="stylesheet" href="assets/auditor/css/apartados.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/acceso.css?v={sello}">
  <script type="application/ld+json">{ld}</script>
</head>
<body class="ac-entrada-cuerpo">
  <main class="ac-entrada" id="contenido">
    <section class="ac-hero" aria-labelledby="acTitulo">
      <figure class="ac-hero-foto">
        <img src="assets/auditor/img/portada/{foto}" alt="{foto_alt}" width="1376" height="768" fetchpriority="high">
        <figcaption>Ilustración editorial generada con IA</figcaption>
      </figure>
      <div class="ac-hero-in">
        <div class="ac-ident">
          <p class="ac-marca">{logo}<span><b>Auditavisión</b><small>El gasto público, a la vista</small></span></p>
          <h1 id="acTitulo">Las cuentas del gobierno, <span>con sus documentos</span></h1>
          <div class="ac-quienes">
            <h2>¿Quiénes somos?</h2>
            <p>{quienes}</p>
          </div>
          <div class="ac-preguntas-caja">
            <h2 class="ac-vh">Preguntas que aquí se contestan con documentos</h2>
            <ul class="ac-preguntas">{preguntas}
            </ul>
          </div>
          <dl class="ac-tira" aria-label="La base de la plataforma, contada al generar esta página">{tira}
          </dl>
        </div>
        <div class="ac-card" id="acTarjeta">
          <div class="ac-tabs" role="tablist" aria-label="Tu acceso">
            <button class="ac-tab" type="button" role="tab" id="tabTengo" aria-controls="acPanTengo" aria-selected="true">Tengo código</button>
            <button class="ac-tab" type="button" role="tab" id="tabPedir" aria-controls="acPanPedir" aria-selected="false" tabindex="-1">Solicitar código</button>
          </div>
          <div class="ac-tabpanel" role="tabpanel" id="acPanTengo" aria-labelledby="tabTengo">
            <form class="ac-canje" id="acCanje" novalidate>
              <label class="ac-et" for="acCasilla0">Entra con tu código de acceso</label>
              {casillas}
              <p class="ac-ayuda">Ocho caracteres: números, letras o las dos cosas. Da igual si son mayúsculas o minúsculas. Si lo copiaste, pégalo en la primera casilla.</p>
              <button class="sz-btn sz-btn-of ac-boton" type="submit" disabled>Ingresar</button>
              <p class="ac-estado" id="acEstado" role="status" aria-live="polite"></p>
            </form>{sin_base}
            <div class="ac-tuyo" id="acTuyo" hidden></div>
          </div>
          <div class="ac-tabpanel" role="tabpanel" id="acPanPedir" aria-labelledby="tabPedir" hidden>
            <form class="ac-pedir" id="acPedir" novalidate>
              <p class="ac-pedir-txt">Es gratis y por invitación. Déjanos tu correo y te mandamos tu código: la versión de prueba se abre poco a poco.</p>
              <label class="ac-et" for="acPCorreo">Tu correo</label>
              <input class="ac-campo" id="acPCorreo" name="correo" type="email" autocomplete="email" required>
              <label class="ac-et" for="acPNombre">Tu nombre <small>(si quieres)</small></label>
              <input class="ac-campo" id="acPNombre" name="nombre" type="text" autocomplete="name" maxlength="80">
              <label class="ac-et" for="acPMotivo">¿A qué te dedicas o para qué lo quieres? <small>(si quieres)</small></label>
              <input class="ac-campo" id="acPMotivo" name="motivo" type="text" maxlength="300">
              <label class="ac-check"><input type="checkbox" name="acepta" required> <span>Acepto el <a href="aviso-de-privacidad.html#codigos" target="_blank" rel="noopener">aviso de privacidad</a>: mi correo solo sirve para mandarme el código.</span></label>
              <button class="sz-btn sz-btn-of ac-boton" type="submit">Pedir mi código</button>
              <p class="ac-estado" id="acPEstado" role="status" aria-live="polite"></p>
            </form>
          </div>
          <p class="ac-card-pie"><a class="ac-enlace" href="servicios.html">Conoce los Servicios</a></p>
        </div>
      </div>
    </section>
    <div class="ac-cuerpo">
      <section class="ac-ejes" aria-labelledby="acEjesTit">
        <h2 id="acEjesTit">Lo que puedes revisar, con su documento</h2>
        <div class="ac-ejes-rej">{ejes}
        </div>
        <p class="ac-ejes-nota">Los números son conteos de la base de la plataforma al generar esta página. Una coincidencia en una lista es una señal para revisar, nunca una acusación.</p>
        <p class="ac-ejes-cta"><button class="sz-btn sz-btn-of ac-pide-btn" type="button" data-pide-codigo>Solicita tu código para entrar</button></p>
      </section>
      <div class="ac-banda">
        <section class="ac-noticias" aria-labelledby="acNotTit">
          <h2 id="acNotTit">Lo último, verificado</h2>
          <ul>{notas}
          </ul>
        </section>
        <section class="ac-faq" aria-labelledby="acFaqTit">
          <h2 id="acFaqTit">Preguntas frecuentes</h2>{faq}
        </section>
      </div>
    </div>
  </main>
  <footer class="ac-pie">Versión de prueba · gratis · <a href="aviso-de-privacidad.html">Aviso de privacidad</a> · <span>{sello}</span></footer>
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
""".format(csp=seguridad.meta(), sello=sello, logo=apartados.LOGO_IMG, notas=notas, casillas=casillas, sin_base=sin_base,
                  desc=esc(DESC_ENTRADA), url=url, sitio=apartados.SITIO, quienes=esc(QUIENES_ENTRADA), preguntas=preguntas, faq=faq, ld=ld, ejes=ejes,
                  foto=FOTO_ENTRADA[0], foto_alt=esc(FOTO_ENTRADA[1]), tira=tira)


def escribir_entrada(sello):
    open(os.path.join(RAIZ, CANJE), 'w', encoding='utf-8', newline='\n').write(entrada_html(sello))


# El panel va en pestañas (pedido del autor, 18-11-2026: «tener esta parte de
# control interno dentro de nuestra plataforma»): el tablero de uso con sus
# gráficas, los códigos, las solicitudes, la bitácora y el acceso propio.
HOJAS = [
    ('tablero', 'panel', 'Tablero de uso'),
    ('codigos', 'llave', 'Códigos'),
    ('solicitudes', 'campana', 'Solicitudes'),
    ('bitacora', 'documento', 'Bitácora'),
    ('acceso', 'escudo', 'Mi acceso'),
    # Ronda 7 (22-11-2026): la antigua Enciclopedia, solo para la administración (traslado.py).
    ('enciclopedia', 'libro', 'Enciclopedia'),
]
# Ronda 28 (26-11-2026): el panel va sin emojis. El segundo dato de cada hoja es un trazo de auditor_bento.TRAZOS
# (si no existe, la generación se detiene) y la hoja de solicitudes lleva en su pestaña el número de pendientes.
# Las gráficas del tablero: id, título y qué responde. Las pinta
# acceso-paginas.js con lo que devuelve uso_tablero() de la base.
GRAFICAS = [
    ('dia', 'El uso, día por día', 'Páginas vistas cada día; pasa el dedo o el ratón por una columna para ver personas y minutos.'),
    ('secciones', 'Los temas que interesan', 'Minutos con la página a la vista en cada parte de la plataforma.'),
    ('paginas', 'Las páginas más vistas', 'Las 20 con más visitas, con sus minutos.'),
    ('clics', 'Dónde dan clic', 'Lo que más se toca: la página a la que lleva una liga o el texto del botón.'),
    ('chat', 'El Auditor: modos y a dónde llevó', 'Preguntas por modo y las páginas a las que llevaron las respuestas. La pregunta no se guarda.'),
    ('horas', 'A qué hora entran', 'Páginas vistas por hora del día (Ciudad de México).'),
    ('codigos', 'Los códigos que más se usan', 'Minutos de uso de quienes canjearon cada código.'),
    ('estados', 'Cómo están los códigos', 'Cuántos códigos hay en cada estado (sin contar los archivados).'),
]


def _pestanas():
    import auditor_bento
    return ('    <div class="ac-pestanas" role="tablist" aria-label="Partes del panel">\n'
            + ''.join('      <button class="ac-pestana" type="button" role="tab" id="ac-tab-%s" aria-controls="ac-hoja-%s" '
                      'aria-selected="%s" data-hoja="%s">%s <span>%s</span>%s</button>\n'
                      % (i, i, 'true' if n == 0 else 'false', i, auditor_bento.ico(ico, 18, 'ac-i'), t,
                         ' <b class="ac-pestana-n" id="acSolN" hidden></b>' if i == 'solicitudes' else '')
                      for n, (i, ico, t) in enumerate(HOJAS))
            + '    </div>\n')


def _tablero():
    graf = ''.join('      <figure class="ac-graf%s" id="acG-%s"><figcaption><b>%s</b> <span class="ac-ayuda">%s</span></figcaption>'
                   '<div class="ac-graf-cuerpo"><p class="ac-ayuda">Cargando…</p></div></figure>\n'
                   % (' ac-graf-ancha' if i in ('dia', 'horas') else '', i, t, d) for i, t, d in GRAFICAS)
    return ('      <h3>Tablero de uso</h3>\n'
            '      <details class="ac-nota"><summary>Qué se mide y qué no</summary>\n'
            '      <p class="ac-ayuda">Cómo se usa la plataforma, para saber dónde poner atención y qué falta en la base. '
            'Se mide por navegador (el número al azar de su pase), nunca por persona: no se guarda la IP, lo que se escribe ni las preguntas al chat. '
            'Tu navegador de administración no se cuenta. Las cifras son conteos de la plataforma, no estimaciones.</p></details>\n'
            '      <div class="ac-orden">\n'
            '        <div class="ac-vista" role="group" aria-label="Periodo">\n'
            + ''.join('          <button class="sz-btn ac-chico ac-claro" type="button" data-periodo="%d" aria-pressed="%s">%s</button>\n'
                      % (d, 'true' if d == 30 else 'false', t) for d, t in ((7, '7 días'), (30, '30 días'), (90, '90 días'), (365, '1 año')))
            + '        </div>\n'
            '        <button class="sz-btn ac-chico ac-claro" type="button" id="acTabRecargar">Actualizar</button>\n'
            '        <button class="sz-btn ac-chico ac-claro" type="button" id="acTabCsv">Descargar CSV</button>\n'
            '      </div>\n'
            '      <p class="ac-estado" id="acTabEstado" role="status" aria-live="polite"></p>\n'
            '      <div class="ac-kpis" id="acKpis"></div>\n'
            '      <div class="ac-mirar" id="acMirar" hidden></div>\n'
            '      <div class="ac-graficas">\n' + graf + '      </div>\n')


def _bitacora():
    return ('      <h3>Bitácora de la administración</h3>\n'
            '      <details class="ac-nota"><summary>Qué queda anotado</summary>\n'
            '      <p class="ac-ayuda">El control interno: cada cosa que se hace con los códigos, las solicitudes y el código maestro queda anotada sola, '
            'con quién y cuándo. No se edita ni se borra desde aquí. «sistema» es lo que hace la plataforma sola, como el código de la semana.</p></details>\n'
            '      <div class="ac-orden">\n'
            '        <label class="ac-busca">Qué <select class="ac-campo" id="acBitQue"><option value="">Todo</option></select></label>\n'
            '        <label class="ac-busca">Buscar <input class="ac-campo" id="acBitBusca" type="search" placeholder="Código, correo o detalle" autocomplete="off"></label>\n'
            '        <button class="sz-btn ac-chico ac-claro" type="button" id="acBitCsv">Descargar CSV</button>\n'
            '      </div>\n'
            '      <div class="ac-resumen" id="acBitResumen"></div>\n'
            '      <div class="ac-tabla-caja"><table class="ac-tabla" id="acBit">\n'
            '        <thead><tr><th>Cuándo</th><th>Quién</th><th>Qué hizo</th><th>Sobre</th><th>Detalle</th></tr></thead>\n'
            '        <tbody></tbody></table></div>\n')


def pagina_panel():
    import auditor_bento
    opciones = ''.join('<option value="%s"%s>%s</option>' % (v, ' selected' if v == '7 days' else '', t) for v, t in DURACIONES)
    bloque = ('<div class="ac-panel" id="acPanel">\n'
              '  <form class="ac-entrar" id="acEntrar" novalidate>\n'
              '    <label class="ac-et" for="acCorreo">Tu correo de administración</label>\n'
              '    <input class="ac-campo" id="acCorreo" type="email" autocomplete="email" required>\n'
              '    <button class="sz-btn sz-btn-of" type="submit">Mandarme el enlace para entrar</button>\n'
              '    <p class="ac-estado" id="acEntrarEstado" role="status" aria-live="polite"></p>\n'
              '    <p class="ac-ayuda">¿Ya pusiste tu código maestro? Escríbelo en <a href="canjea-tu-codigo.html">la entrada</a> y entras sin correo.</p>\n'
              '  </form>\n'
              # El doble factor (19-11-2026, LFPDPPP art. 18): el correo o el código maestro
              # abren la sesión, y el panel pide además el código de seis números de una
              # aplicación de autenticación (TOTP de Supabase). La base lo exige también:
              # es_admin() solo responde con la sesión de dos factores (aal2).
              '  <form class="ac-entrar" id="acFactor" novalidate hidden>\n'
              '    <h2 class="ac-et">Segundo paso: tu código de seis números</h2>\n'
              '    <div id="acFactorAlta" hidden>\n'
              '      <p class="ac-ayuda">Este código QR es nuevo: escanéalo con tu aplicación de autenticación '
              '(Google Authenticator, Microsoft Authenticator, 1Password, Authy…) y escribe los seis números que te da, sin recargar la página.</p>\n'
              '      <p class="ac-ayuda ac-ojo">Si en tu aplicación ya había una entrada «Panel Auditavisión» de un intento anterior, bórrala antes: '
              'sus números ya no sirven.</p>\n'
              '      <img class="ac-qr" id="acFactorQr" alt="Código QR para dar de alta el segundo factor" width="200" height="200">\n'
              '      <p class="ac-ayuda">¿No puedes escanearlo? Escribe esta clave en la aplicación: <code id="acFactorSecreto"></code></p>\n'
              '      <p class="ac-ayuda"><a class="sz-btn" id="acFactorUri" href="#" hidden>Ábrelo en tu aplicación (si estás en el celular)</a></p>\n'
              '    </div>\n'
              '    <label class="ac-et" for="acFactorCodigo">Código de tu aplicación</label>\n'
              '    <input class="ac-campo" id="acFactorCodigo" inputmode="numeric" autocomplete="one-time-code" maxlength="6" pattern="[0-9]{6}" required>\n'
              '    <button class="sz-btn sz-btn-of" type="submit">Entrar al panel</button>\n'
              '    <p class="ac-estado" id="acFactorEstado" role="status" aria-live="polite"></p>\n'
              '    <p class="ac-ayuda">El panel pide los dos pasos por seguridad (LFPDPPP, art. 18). '
              'Si perdiste tu aplicación o cambiaste de celular, el factor se borra en Supabase (Authentication, Users, «Remove MFA factors») '
              'y lo das de alta otra vez.</p>\n'
              '  </form>\n'
              '  <div class="ac-admin" id="acAdmin" hidden>\n'
              '    <div class="ac-tope">\n'
              '      <p class="ac-tope-yo"><span class="ac-insignia">%s Administración</span> <span id="acQuien"></span></p>\n'
              '      <button class="sz-btn ac-chico ac-claro" type="button" id="acSalir">Salir</button>\n'
              '      <p class="ac-pase-fila"><span class="ac-estado ac-pase" id="acPaseEstado" role="status" aria-live="polite"></span> '
              '<button class="sz-btn ac-chico ac-claro" type="button" id="acPaseReintentar" hidden>Reintentar</button></p>\n'
              '      <p class="ac-estado ac-pase-mal" id="acAviso" role="status" aria-live="polite" hidden></p>\n'
              '    </div>\n'
              + _pestanas() +
              '    <section class="ac-hoja" id="ac-hoja-tablero" role="tabpanel" aria-labelledby="ac-tab-tablero" data-sin-medir>\n'
              + _tablero() +
              '    </section>\n'
              '    <section class="ac-hoja" id="ac-hoja-enciclopedia" role="tabpanel" aria-labelledby="ac-tab-enciclopedia" hidden>\n'
              + _enciclopedia() +
              '    </section>\n'
              '    <section class="ac-hoja" id="ac-hoja-bitacora" role="tabpanel" aria-labelledby="ac-tab-bitacora" hidden>\n'
              + _bitacora() +
              '    </section>\n'
              '    <section class="ac-hoja" id="ac-hoja-acceso" role="tabpanel" aria-labelledby="ac-tab-acceso" hidden>\n'
              '    <div class="ac-dos">\n'
              '    <section class="ac-semana" aria-labelledby="acSemTit">\n'
              '      <h3 id="acSemTit">Tu código de la semana</h3>\n'
              '      <p class="ac-semana-cod"><button class="ac-cod" type="button" id="acSemCod" title="Copiar">····-····</button></p>\n'
              '      <p class="ac-ayuda" id="acSemVence">Es solo tuyo y cambia solo cada lunes a las 0:00 (hora de la Ciudad de México). '
              'Cuando cambie, tu acceso termina y la entrada te manda aquí por el nuevo.</p>\n'
              '      <p class="ac-acciones"><button class="sz-btn sz-btn-of" type="button" id="acComoAdmin">Abrir la plataforma con mi código</button> '
              '<button class="sz-btn ac-chico ac-claro" type="button" id="acSemCambiar">Cambiarlo ahora</button></p>\n'
              '      <p class="ac-estado" id="acComoAdminEstado" role="status" aria-live="polite"></p>\n'
              '    </section>\n'
              '    <form class="ac-semana ac-maestro" id="acMaestro" novalidate>\n'
              '      <h3>Tu código maestro</h3>\n'
              '      <p class="ac-ayuda">Son 8 números o letras que solo tú sabes: en la entrada te reconocen como administración, sin correo.</p>\n'
              '      <details class="ac-nota"><summary>Cómo elegirlo y cuidarlo</summary>\n'
              '      <p class="ac-ayuda">Escríbelo en la entrada de la plataforma, desde cualquier dispositivo. No cambia solo: lo cambias aquí cuando quieras. Si ese número ya era uno de tus códigos comunes, se archiva y pasa a ser tu código maestro. '
              'No uses una fecha ni un número que alguien pueda adivinar, y no lo mandes por chat ni por correo.</p></details>\n'
              '      <p class="ac-ayuda" id="acMaeEstado"></p>\n'
              '      <div class="ac-fila">\n'
              '        <label>Código maestro nuevo <input class="ac-campo" name="nuevo" type="password" autocapitalize="characters" maxlength="9" autocomplete="new-password" required></label>\n'
              '        <label>Escríbelo otra vez <input class="ac-campo" name="otra" type="password" autocapitalize="characters" maxlength="9" autocomplete="new-password" required></label>\n'
              '      </div>\n'
              '      <p class="ac-acciones"><button class="sz-btn sz-btn-of" type="submit">Guardar mi código maestro</button></p>\n'
              '      <p class="ac-estado" id="acMaeGuardar" role="status" aria-live="polite"></p>\n'
              '      <p class="ac-ayuda" id="acMaeEntradas"></p>\n'
              '    </form>\n'
              '    </div>\n'
              '    </section>\n'
              '    <section class="ac-hoja" id="ac-hoja-solicitudes" role="tabpanel" aria-labelledby="ac-tab-solicitudes" hidden>\n'
              '    <section class="ac-solicitudes" aria-labelledby="acSolTit">\n'
              '      <h3 id="acSolTit">Solicitudes de código <span class="ac-chip ac-sin_usar" id="acSolCuenta"></span></h3>\n'
              '      <p class="ac-ayuda ac-largo">Quien pidió código desde la entrada. Elige cuánto le das, asigna y mándaselo desde tu correo.</p>\n'
              '      <div class="ac-tabla-caja"><table class="ac-tabla" id="acSol">\n'
              '        <thead><tr><th>Correo</th><th>Quién y para qué</th><th>Pidió</th><th>Estado</th><th></th></tr></thead>\n'
              '        <tbody></tbody></table></div>\n'
              '    </section>\n'
              '    </section>\n'
              '    <section class="ac-hoja" id="ac-hoja-codigos" role="tabpanel" aria-labelledby="ac-tab-codigos" hidden>\n'
              '    <form class="ac-generar" id="acGenerar" novalidate>\n'
              '      <h3>Generar códigos</h3>\n'
              '      <div class="ac-fila">\n'
              '        <label>Cantidad <input class="ac-campo" name="cantidad" type="number" min="1" max="500" value="10" required></label>\n'
              '        <label>Duración <select class="ac-campo" name="duracion">%s<option value="otra">Otra (en días)</option></select></label>\n'
              '        <label class="ac-otra" hidden>Días <input class="ac-campo" name="dias" type="number" min="1" max="1825" value="10"></label>\n'
              '        <label>Personas por código <input class="ac-campo" name="usos" type="number" min="1" max="10000" value="1" required></label>\n'
              '        <label>Canjear antes del <input class="ac-campo" name="antes" type="date"></label>\n'
              '        <label>Tokens que da <select class="ac-campo" name="tokens"><option value="">Sin tokens (solo abre)</option></select></label>\n'
              '        <label class="ac-otros" hidden>Cuántos tokens <input class="ac-campo" name="tokensN" type="number" min="1" max="100000" value="35"></label>\n'
              '        <p class="ac-ayuda ac-ancho">Tokens (Ronda 27A): al canjearse, el código suma esa cantidad a la billetera de quien lo usa, una sola vez por navegador, o le da tokens ilimitados mientras dure su acceso. La duración sigue diciendo cuánto tiempo abre los Servicios. Sin tokens, el código solo abre, como antes.</p>\n'
              '        <label class="ac-ancho">Nota (opcional) <input class="ac-campo" name="nota" type="text" maxlength="120" placeholder="Para quién son: «Taller», «Prensa»…"></label>\n'
              '        <label class="ac-ancho">Código propio (opcional) <input class="ac-campo" name="propio" type="text" autocapitalize="characters" maxlength="9" autocomplete="off" spellcheck="false" placeholder="Vacío: salen al azar. Ejemplo: 2026-1029 o PASE-TALL"></label>\n'
              '        <details class="ac-nota ac-ancho"><summary>Ayuda sobre los códigos</summary>\n'
              '        <p class="ac-ayuda">Si escribes un código propio se crea solo ese, con la duración y los usos de arriba. Lleva 8 caracteres: puros números, puras letras o revueltos, como tú quieras. Los que salen al azar siempre revuelven letras y números, así que uno de puros números o de puras letras es uno que diste tú. La nota es opcional.</p>\n'
              '        <p class="ac-ayuda">Archivar solo ordena: el código sigue abriendo si alguien lo usa. Renovar le devuelve la vida: quita la revocación y el archivo, suma personas o fecha y, si quieres, da más tiempo a quien ya lo canjeó (desde hoy, si ya se le había acabado). Eliminar lo borra para siempre y quien lo canjeó pierde su tiempo. Todo queda en la Bitácora.</p></details>\n'
              '      </div>\n'
              '      <p class="ac-acciones"><button class="sz-btn sz-btn-of" type="submit">Generar</button></p>\n'
              '      <p class="ac-estado" id="acGenerarEstado" role="status" aria-live="polite"></p>\n'
              '    </form>\n'
              '    <h3 class="ac-reg-tit">Registro de códigos</h3>\n'
              '    <div class="ac-resumen" id="acResumen"></div>\n'
              '    <div class="ac-orden">\n'
              '      <div class="ac-vista" role="group" aria-label="Qué códigos ver">\n'
              '        <button class="sz-btn ac-chico ac-claro" type="button" data-vista="activos" aria-pressed="true">Activos <b id="acNAct">0</b></button>\n'
              '        <button class="sz-btn ac-chico ac-claro" type="button" data-vista="archivados" aria-pressed="false">Archivados <b id="acNArc">0</b></button></div>\n'
              '      <label class="ac-busca">Buscar <input class="ac-campo" id="acBusca" type="search" placeholder="Código o nota" autocomplete="off"></label>\n'
              '      <button class="sz-btn ac-chico ac-claro" type="button" id="acRecargar">Actualizar</button>\n'
              '      <button class="sz-btn ac-chico ac-claro" type="button" id="acArchInact" title="Revocados, terminados y vencidos">Archivar los que ya no abren</button>\n'
              '      <button class="sz-btn ac-chico ac-claro" type="button" id="acCsv">Descargar CSV</button>\n'
              '      <button class="sz-btn ac-chico ac-claro" type="button" id="acCsvUso">Descargar el registro de uso</button>\n'
              '    </div>\n'
              '    <p class="ac-estado" id="acTablaEstado" role="status" aria-live="polite"></p>\n'
              '    <div class="ac-tabla-caja"><table class="ac-tabla" id="acTabla">\n'
              '      <thead><tr><th>Código</th><th>Duración</th><th>Usos</th><th>Estado</th><th>Nota</th><th>Acciones</th></tr></thead>\n'
              '      <tbody></tbody></table></div>\n'
              '    </section>\n'
              '  </div>\n'
              '</div>') % (auditor_bento.ico('escudo', 16, 'ac-i'), opciones)
    return {
        'archivo': PANEL,
        'menu': 'Administración de códigos',
        'icono': '🗝️',
        'titulo': 'Administración y control interno',
        'lema': 'Solo para la administración',
        'entrada': ('El control interno de la plataforma: el tablero de uso, los códigos de invitación, las solicitudes, la bitácora '
                    'y tu acceso. Solo abre con una cuenta dada de alta en la administración.'),
        # Ronda 28: el encabezado va compacto (acceso.css, .ac-cab) para que el panel empiece en la primera pantalla.
        'cab_extra': 'ac-cab', 'sin_icono_lema': True,
        'noindex': True,
        'estilos': ['acceso.css'],
        'scripts': ['acceso-paginas.js'],
        'secciones': [{'id': 'panel', 'titulo': 'Control interno', 'texto': 'Tablero, códigos, solicitudes, bitácora y tu acceso, cada uno en su pestaña.', 'tarjetas': [], 'bloque': bloque}],
    }


def paginas():
    """Las páginas con el molde de apartados.py: el panel. La entrada tiene el
    suyo (escribir_entrada)."""
    escribir_config()
    __import__('monetizacion').escribir_tokens()
    return [pagina_panel()]
