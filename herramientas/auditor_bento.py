#!/usr/bin/env python3
"""Ronda 21 (25-11-2026, diseño aprobado por el autor: «D + F»): la página del Auditor
(herramienta-inspector-pregunta.html) con barra lateral en azul marino y lienzo modular
(«Bento»), con el modo Inspector primero.

- La barra lateral: la marca, cuatro destinos (Auditor · Inspector, Noticiero, Planisferio y
  Comunidad; la pestaña «Administración» la agrega acceso.js en el navegador de la
  administración), «Tu portafolio reciente» (lo lee auditor-bento.js de av-portafolio, solo en
  el navegador) y la puerta dorada a Servicios. **Nunca un monto.**
- El lienzo: la tarjeta protagonista con el chat y sus cuatro modos, el Escáner Cero CIEC (los
  XML o el CSV pasan al Lector de facturas o a la matriz del padrón en el mismo navegador: nada
  se sube), tres puertas (Semáforo patrimonial, Vigía 69-B, Auditorías en imágenes) y la tira de
  conteos de la base, que sale de monetizacion.contadores(): **ninguna cifra escrita a mano**.

No trae datos propios ni entra a la huella del dictamen.
"""
import html
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAV = [('herramienta-inspector-pregunta.html', '🔍', 'Auditor · Inspector'),
       ('noticias-relevantes.html', '📰', 'Noticiero'),
       ('planisferio.html', '🗺️', 'Planisferio'),
       ('participa.html', '🤝', 'Comunidad')]
SEGMENTOS = [('inspector', '🔍', 'Inspector'), ('ciudadano', '🙋', 'Ciudadano'),
             ('periodista', '📰', 'Periodista'), ('ambientalista', '🌎', 'Ambientalista')]
# Las tres puertas de la segunda fila: (ícono, título, texto, liga, rótulo de la liga, imagen).
PUERTAS = [
    ('🏠', 'Semáforo patrimonial inmobiliario',
     'Antes de comprar o rentar: el predial que manda la ley de su municipio, el precio de la vivienda del Índice SHF y con quién firmas.',
     'servicios-revisa.html?s=simulacion', 'Ábrelo en el Inspector', None),
    ('🛡️', 'Vigía antifraude y 69-B',
     'Cada semana comparamos la lista del SAT: altas, cambios de situación y bajas de las empresas que facturan operaciones simuladas.',
     'servicio-seguimiento.html#vigia', 'Ver el Vigía', None),
    ('🖼️', 'Auditorías en imágenes',
     'Las grandes investigaciones contadas como reportaje: la cifra, sus documentos y lo que falta saber.',
     'noticias-relevantes.html#auditorias', 'Ir al Noticiero', 'assets/auditor/img/showcase_deuda_2027.jpg'),
]
# Los conteos de la tira (claves de monetizacion.contadores()).
CONTEOS = ('69b', 'contratos', 'municipios', 'predial', 'boveda')
ACEPTA = '.xml,.csv,.txt,text/xml,application/xml,text/csv,text/plain'


def _e(x):
    return html.escape(x, quote=True)


def revisa():
    """Detiene la generación si una liga, una imagen o un conteo no existen."""
    for u in [n[0] for n in NAV] + [p[3] for p in PUERTAS]:
        if not os.path.exists(os.path.join(RAIZ, u.split('#')[0].split('?')[0])):
            raise SystemExit('auditor_bento.py: la liga %s no existe' % u)
    for p in PUERTAS:
        if p[5] and not os.path.exists(os.path.join(RAIZ, p[5])):
            raise SystemExit('auditor_bento.py: la imagen %s no existe' % p[5])
    if not open(os.path.join(RAIZ, 'servicio-seguimiento.html'), encoding='utf-8').read().count('id="vigia"'):
        raise SystemExit('auditor_bento.py: servicio-seguimiento.html ya no tiene #vigia')


def _lado():
    nav = '\n'.join('        <a href="%s"%s><span aria-hidden="true">%s</span> %s</a>' % (
        u, ' aria-current="true"' if i == 0 else '', ico, html.escape(t)) for i, (u, ico, t) in enumerate(NAV))
    return '''<aside class="avb-lado" aria-label="Navegación del Auditor">
      <a class="avb-marca" href="index.html"><img src="assets/auditor/img/logo-auditavision.svg" alt="" width="40" height="31"> <b>Auditavisión</b></a>
      <nav class="avb-nav" aria-label="Destinos">
%s
      </nav>
      <details class="avb-mas" open>
        <summary>Tu portafolio y los servicios</summary>
        <section class="avb-port" aria-labelledby="avbPortT">
          <h2 id="avbPortT">Tu portafolio reciente</h2>
          <ol id="avbPortLista" hidden></ol>
          <p class="avb-port-vacio" id="avbPortVacio">Aún no guardas investigaciones. En el Inspector de Servicios, «💾 Guardar en mi portafolio» las deja aquí, solo en tu navegador.</p>
        </section>
        <section class="avb-serv" aria-labelledby="avbServT">
          <h2 id="avbServT">Servicios del Inspector</h2>
          <p>Consulta pública gratis siempre. Dictámenes sellados, lotes XML y vigilancia semanal en Servicios.</p>
          <a class="avb-oro" href="servicios.html">Servicios y Paquetes ➔</a>
          <a class="avb-cuenta" href="comunidad.html">📢 Cuéntanos lo que viste</a>
        </section>
      </details>
    </aside>''' % nav


# Las preguntas de ejemplo de la tarjeta del hero: cada una ya la contesta el chat (preguntas_auditor.json).
CHIPS = [('¿Mi proveedor está en la lista negra del SAT?', '🧾'), ('¿Cuánto debe Jalisco?', '🗺️'),
         ('¿Cuánto costó el Tren Maya?', '🚆'), ('Diagnóstico de Pemex', '🏛️')]


def _hero():
    """El hero editorial (ajuste del autor a la Ronda 21): la misma imagen de la entrada, con su huella
    (acceso.FOTO_ENTRADA), «¿Quiénes somos?» y las ocho preguntas, que aquí se tocan y se preguntan;
    a la derecha, la tarjeta con los cuatro modos y la caja de pregunta. La entrada no cambia."""
    import hashlib
    import acceso
    foto, alt, huella = acceso.FOTO_ENTRADA
    ruta = os.path.join(RAIZ, 'assets', 'auditor', 'img', 'portada', foto)
    if hashlib.sha256(open(ruta, 'rb').read()).hexdigest() != huella:
        raise SystemExit('auditor_bento.py: la imagen editorial no es la aprobada (%s)' % foto)
    seg = '\n'.join('            <button type="button" data-avb-modo="%s" aria-pressed="%s"><span aria-hidden="true">%s</span> %s</button>' % (
        m, 'true' if m == 'inspector' else 'false', ico, n) for m, ico, n in SEGMENTOS)
    preg = '\n'.join('            <li%s><button type="button" data-avb-q="%s">%s</button></li>' % (
        '' if i == 0 else ' hidden', _e(q), html.escape(q)) for i, q in enumerate(acceso.PREGUNTAS_ENTRADA))
    chips = '\n'.join('            <button type="button" class="avb-chip" data-avb-q="%s"><span aria-hidden="true">%s</span> %s</button>' % (
        _e(q), i, html.escape(q)) for q, i in CHIPS)
    return '''<section class="avb-hero" aria-labelledby="avbTit">
        <figure class="avb-hero-foto"><img src="assets/auditor/img/portada/%s" alt="%s" width="1376" height="768" fetchpriority="high">
          <figcaption>Ilustración editorial generada con IA</figcaption></figure>
        <div class="avb-hero-in">
          <div class="avb-ident">
            <h2 class="avb-tit" id="avbTit">Las cuentas del gobierno, <span>con sus documentos</span></h2>
            <div class="avb-quienes"><h3>¿Quiénes somos?</h3><p>%s</p></div>
            <div class="avb-preguntas"><h3 class="sr-only">Preguntas que aquí se contestan con documentos: tócala y te la contesto</h3>
            <ul id="avbPreg">
%s
            </ul></div>
          </div>
          <div class="avb-card avb-prota">
            <div class="avb-seg" role="group" aria-label="Modo del Auditor">
%s
            </div>
            <p class="avb-insignia">✓ Cero CIEC · Sin contraseñas del SAT</p>
            <form class="avb-form" id="avbForm" autocomplete="off">
              <label for="avbQ">Pregunta por un RFC, un municipio, una megaobra o una nota</label>
              <textarea id="avbQ" rows="3" maxlength="600" placeholder="Por ejemplo: ¿quién ganó los contratos de la obra de mi ciudad?" required></textarea>
              <button type="submit" id="avbEnvia">Dictaminar ➔</button>
            </form>
            <div class="avb-chips" role="group" aria-label="Preguntas de ejemplo">
%s
            </div>
          </div>
        </div>
      </section>''' % (foto, _e(alt), html.escape(acceso.QUIENES_ENTRADA), preg, seg, chips)


def _chat(chat):
    return '''<section class="avb-card avb-chatcard" id="avbChat" aria-labelledby="avbChatT">
        <h2 id="avbChatT">Tu plática con el Auditor</h2>
%s
      </section>''' % chat


def _escaner():
    return '''<section class="avb-card avb-navy avb-esc" aria-labelledby="avbEscT">
        <h2 id="avbEscT">Escáner Cero CIEC</h2>
        <p>Suelta tus facturas o recibos de nómina en XML, o tu cartera en CSV. Se leen aquí, en tu navegador: no se suben y nunca te pedimos la Contraseña del SAT ni tu e.firma.</p>
        <label class="avb-suelta" id="avbSuelta" for="avbArch">
          <span aria-hidden="true">📂</span> Suelta aquí tus XML o tu CSV, o tócalo para elegirlos
          <input type="file" id="avbArch" multiple accept="%s">
        </label>
        <p class="avb-esc-nota">XML → Lector de facturas · CSV o TXT → la matriz del padrón de contrapartes.</p>
      </section>''' % ACEPTA


def _puertas():
    out = []
    for ico, tit, tx, u, rot, img in PUERTAS:
        foto = '<img class="avb-foto" src="%s" alt="" loading="lazy" width="640" height="360">' % img if img else ''
        out.append('''      <a class="avb-card avb-puerta%s" href="%s">%s
        <span class="avb-puerta-ico" aria-hidden="true">%s</span>
        <b>%s</b>
        <span>%s</span>
        <span class="avb-puerta-ir">%s ➔</span>
      </a>''' % (' avb-con-foto' if img else '', _e(u), foto, ico, html.escape(tit), html.escape(tx), html.escape(rot)))
    return '\n'.join(out)


def _conteos():
    import monetizacion
    c = {x[0]: x for x in monetizacion.contadores()}
    falta = [k for k in CONTEOS if k not in c]
    if falta:
        raise SystemExit('auditor_bento.py: monetizacion.contadores() ya no trae %s' % ', '.join(falta))
    li = '\n'.join('          <li><b>%s</b><span>%s</span></li>' % (format(c[k][1], ','), html.escape(c[k][2])) for k in CONTEOS)
    return '''<section class="avb-card avb-conteos" aria-labelledby="avbConT">
        <h2 id="avbConT">La base, contada al generar esta página <span class="est-chip est-derivado">auditada</span></h2>
        <ul>
%s
        </ul>
        <p class="avb-con-nota">Conteos de los archivos de la plataforma, cada uno con su fuente oficial en <a href="base-al-dia.html">La base al día</a>.</p>
      </section>''' % li


def bloque(chat):
    """El lienzo completo alrededor del chat del Auditor."""
    revisa()
    return '''<div class="avb" id="avb">
    %s
    <div class="avb-lienzo">
      %s
      %s
      %s
      <div class="avb-fila">
%s
      </div>
      <section class="avb-card avb-lector" id="avbLector" hidden aria-labelledby="avbLecT">
        <h2 id="avbLecT">Tu revisión, en este navegador</h2>
        <iframe id="avbMarco" class="av-en-chat" title="Lector de tus archivos"></iframe>
      </section>
      %s
    </div>
  </div>''' % (_lado(), _hero(), _chat(chat), _escaner(), _puertas(), _conteos())
