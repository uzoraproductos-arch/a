#!/usr/bin/env python3
"""La página del Auditor (herramienta-inspector-pregunta.html).

Ronda 21 (25-11-2026): barra lateral en azul marino y lienzo modular. Ronda 22: una sola caja de pregunta.
Ronda 23 (25-11-2026, diseño aprobado por el autor, «Solo barra lateral, tipo Claude.ai»): la página se limpia.

- **Una sola navegación**: la barra lateral (marca, «Nueva revisión», los cinco destinos, «Tu portafolio» de
  av-portafolio y, al fondo, la cuenta que llena acceso.js). La página no lleva la barra superior del sitio
  (apartados.pagina() la quita) ni la franja de módulo del Modo Inspector.
- **El lienzo**, en blanco y a ~820 px: el encabezado sobrio, la única caja (los cuatro modos arriba, la pregunta
  al centro, «Adjuntar XML / CSV · Cero CIEC» y «Dictaminar» abajo: los archivos se leen en este navegador, nada
  se sube), cuatro ejemplos, la plática (solo con una pregunta), el lector local y seis accesos directos a
  Servicios. **Sin emojis**: íconos SVG de trazo, sin librerías.
- **El pie** trae los cinco conteos de monetizacion.contadores() (**ninguna cifra escrita a mano**) y sus ligas.

Nunca un monto. No trae datos propios ni entra a la huella del dictamen.
"""
import html
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANJE = 'canjea-tu-codigo.html'
PANEL = 'administracion-codigos.html'

# Íconos de trazo (24 × 24, stroke="currentColor"): solo trazos propios, sin librerías.
TRAZOS = {
    'lupa': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    'maletin': '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M3 13h18"/>',
    'mapa': '<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
    'periodico': '<path d="M4 5h12v14a2 2 0 0 0 2 2H6a2 2 0 0 1-2-2z"/><path d="M16 9h4v10a2 2 0 0 1-2 2"/><path d="M8 9h4M8 13h4M8 17h2"/>',
    'personas': '<circle cx="9" cy="8" r="3.5"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8"/><path d="M18 14.6c1.8.8 3 2.7 3 5.4"/>',
    'mas': '<path d="M12 5v14M5 12h14"/>',
    'documento': '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h4"/>',
    'llave': '<circle cx="8" cy="15" r="4"/><path d="m10.8 12.2 9.2-9.2"/><path d="m17 6 3 3"/><path d="m14.5 8.5 2 2"/>',
    'check': '<path d="M20 6 9 17l-5-5"/>',
    'escudo': '<path d="M12 3 4 6v6c0 5 3.4 8 8 9 4.6-1 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    'factura': '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6M9 16h3"/>',
    'casa': '<path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
    'edificio': '<path d="M4 9.5 12 4l8 5.5"/><path d="M3 21h18"/><path d="M6 10v8M10 10v8M14 10v8M18 10v8"/>',
    'campana': '<path d="M6 16v-5a6 6 0 0 1 12 0v5l2 2H4z"/><path d="M10 21a2 2 0 0 0 4 0"/>',
    'clip': '<path d="m20.5 11.5-8.4 8.4a5 5 0 0 1-7.1-7.1l8.4-8.4a3.4 3.4 0 0 1 4.8 4.8l-8.4 8.4a1.7 1.7 0 0 1-2.4-2.4L15 7.6"/>',
    'flecha': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'usuario': '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/>',
    'pluma': '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    'hoja': '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10z"/><path d="M2 21c0-3 1.9-5.4 5.2-6"/>',
}


def ico(nombre, tam=18, clase='avb-i'):
    """Un ícono de trazo fino, decorativo (aria-hidden)."""
    return ('<svg class="%s" width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">%s</svg>') % (clase, tam, tam, TRAZOS[nombre])


# Los cinco destinos de la barra lateral, en el orden del menú (el primero es esta página).
NAV = [('herramienta-inspector-pregunta.html', 'lupa', 'Auditor'),
       ('servicios.html', 'maletin', 'Servicios'),
       ('planisferio.html', 'mapa', 'Planisferio'),
       ('noticias-relevantes.html', 'periodico', 'Noticiero'),
       ('participa.html', 'personas', 'Comunidad')]
# Los cuatro modos (el orden de asistente.ORDEN_AUDITOR) y su pista corta.
SEGMENTOS = [('inspector', 'lupa', 'Inspector', 'Investigación completa, con dictamen sellado'),
             ('ciudadano', 'usuario', 'Ciudadano', 'En corto, como te lo diría un amigo'),
             ('periodista', 'pluma', 'Periodista', 'Contado como nota, con sus documentos'),
             ('ambientalista', 'hoja', 'Ambientalista', 'El costo y el daño ambiental')]
# Las preguntas de ejemplo: cada una ya la contesta el chat (preguntas_auditor.json).
CHIPS = ['¿Mi proveedor está en la lista negra del SAT?', '¿Cuánto debe Jalisco?',
         '¿Cuánto costó el Tren Maya?', 'Diagnóstico de Pemex']
# Los accesos directos a Servicios: (ícono, etiqueta, título, una línea, servicio o liga). Sin montos.
ACCESOS = [
    ('escudo', 'Prevención', 'Contrapartes y 69-B',
     'Tu cartera contra las listas del SAT, Sancionados, la OFAC y la ONU.', 'contrapartes'),
    ('factura', 'Facturas', 'Facturas XML y nómina',
     'Tus CFDI y recibos revisados por proveedor, con su cruce con la 69-B.', 'facturas'),
    ('casa', 'Simuladores', 'Semáforo patrimonial',
     'Antes de comprar o rentar: el predial de su ley, el Índice SHF y con quién firmas.', 'simulacion'),
    ('mapa', 'Gobiernos', 'Estados y municipios',
     'Lo que le entra y lo que gasta, su deuda, su inversión y lo pendiente ante la ASF.', 'radiografia'),
    ('edificio', 'Proveedores', 'Contratos y ASF',
     'Los contratos de una empresa en ComprasMX, la 69-B, Sancionados y la ASF.', 'diligencia'),
    ('campana', 'Vigilancia', 'Vigía 69-B y dictámenes',
     'Cada semana, las altas, los cambios de situación y las bajas de la lista del SAT.', 'servicio-seguimiento.html#vigia'),
]
# Los conteos del pie (claves de monetizacion.contadores()).
CONTEOS = ('69b', 'contratos', 'municipios', 'predial', 'boveda')
ACEPTA = '.xml,.csv,.txt,text/xml,application/xml,text/csv,text/plain'


def _e(x):
    return html.escape(x, quote=True)


def _liga(destino):
    return destino if '.html' in destino else 'servicios-revisa.html?s=' + destino


def revisa(servicios):
    """Detiene la generación si una liga o un servicio no existen."""
    for u in [n[0] for n in NAV] + [_liga(a[4]) for a in ACCESOS] + [CANJE, PANEL, 'base-al-dia.html', 'indice.html']:
        if not os.path.exists(os.path.join(RAIZ, u.split('#')[0].split('?')[0])):
            raise SystemExit('auditor_bento.py: la liga %s no existe' % u)
    for a in ACCESOS:
        if '.html' not in a[4] and a[4] not in servicios:
            raise SystemExit('auditor_bento.py: el servicio %s no está en SERVICIOS' % a[4])
    if not open(os.path.join(RAIZ, 'servicio-seguimiento.html'), encoding='utf-8').read().count('id="vigia"'):
        raise SystemExit('auditor_bento.py: servicio-seguimiento.html ya no tiene #vigia')


def _lado(n_serv):
    nav = []
    for i, (u, i_, t) in enumerate(NAV):
        pastilla = ' <span class="avb-pastilla" title="%d servicios">%d</span>' % (n_serv, n_serv) if u == 'servicios.html' else ''
        nav.append('        <a href="%s"%s>%s<span>%s</span>%s</a>' % (u, ' aria-current="page"' if i == 0 else '', ico(i_), t, pastilla))
    return '''<aside class="avb-lado" aria-label="Navegación del Auditor">
      <a class="avb-marca" href="index.html"><img src="assets/auditor/img/logo-auditavision.svg" alt="" width="36" height="28"> <b>Auditavisión</b></a>
      <button type="button" class="avb-nueva" id="avbNueva">%s Nueva revisión</button>
      <nav class="avb-nav" aria-label="Destinos">
%s
      </nav>
      <details class="avb-port" id="avbPort" open>
        <summary>Tu portafolio</summary>
        <ol id="avbPortLista" hidden></ol>
        <p class="avb-port-vacio" id="avbPortVacio">Aún no guardas investigaciones. En el Inspector de Servicios, «Guardar en mi portafolio» las deja aquí, solo en tu navegador.</p>
      </details>
      <div class="avb-acceso" id="avbAcceso">
        <a class="avb-ingresa" href="%s">%s Ingresar</a>
      </div>
    </aside>''' % (ico('mas'), '\n'.join(nav), CANJE, ico('llave'))


def _caja():
    seg = '\n'.join('              <button type="button" data-avb-modo="%s" data-pista="%s" aria-pressed="%s">%s<span>%s</span></button>' % (
        m, _e(p), 'true' if m == 'inspector' else 'false', ico(i), n) for m, i, n, p in SEGMENTOS)
    chips = '\n'.join('        <button type="button" class="avb-chip" data-avb-q="%s">%s</button>' % (_e(q), html.escape(q)) for q in CHIPS)
    return '''<header class="avb-cab">
        <p class="avb-insignia">%s Plataforma abierta · Cero CIEC · Datos oficiales</p>
        <h1 class="avb-tit" id="avbTit">¿Qué quieres auditar hoy?</h1>
        <p class="avb-sub">Pregunta en lenguaje normal o adjunta tus XML/CSV. El Auditor investiga en toda la base oficial y te lleva al servicio exacto.</p>
      </header>
      <form class="avb-box" id="avbForm" autocomplete="off" aria-labelledby="avbTit">
        <div class="avb-box-arriba">
          <div class="avb-seg" role="group" aria-label="Modo del Auditor">
%s
          </div>
          <p class="avb-pista" id="avbPista" aria-live="polite">%s</p>
        </div>
        <label class="sr-only" for="avbQ">Pregunta por un RFC, un municipio, una megaobra o una nota</label>
        <textarea id="avbQ" rows="3" maxlength="600" placeholder="Por ejemplo: ¿quién ganó los contratos de la obra de mi ciudad?" required></textarea>
        <div class="avb-box-abajo">
          <label class="avb-adjunta" id="avbSuelta" for="avbArch" title="Se leen en tu navegador: nada se sube y nunca te pedimos la Contraseña del SAT">
            %s<span>Adjuntar XML / CSV <small>· Cero CIEC</small></span>
            <input type="file" id="avbArch" multiple accept="%s">
          </label>
          <button type="submit" id="avbEnvia"><span>Dictaminar</span>%s</button>
        </div>
      </form>
      <div class="avb-chips" role="group" aria-label="Preguntas de ejemplo">
%s
      </div>''' % (ico('check', 16), seg, html.escape(SEGMENTOS[0][3]), ico('clip'), ACEPTA, ico('flecha'), chips)


def _chat(chat):
    """Ronda 22: la plática original sigue aquí con su motor, sin su cabecera, su selector de modos, sus ejemplos ni
    su caja (auditor-bento.css); la tarjeta solo aparece cuando ya hay una pregunta (auditor-bento.js)."""
    return '''<section class="avb-chatcard" id="avbChat" aria-labelledby="avbChatT" hidden>
        <h2 id="avbChatT">Tu plática con el Auditor</h2>
%s
        <p class="avb-otra"><button type="button" id="avbOtra">%s Hacer otra pregunta</button></p>
      </section>''' % (chat, ico('pluma'))


def _servicios():
    tarjetas = '\n'.join('''        <a class="avb-acc" href="%s">
          <span class="avb-acc-ico">%s</span>
          <small>%s</small>
          <b>%s</b>
          <span>%s</span>
        </a>''' % (_e(_liga(d)), ico(i, 20), html.escape(et), html.escape(t), html.escape(tx)) for i, et, t, tx, d in ACCESOS)
    return '''<section class="avb-serv" aria-labelledby="avbServT">
        <div class="avb-serv-cab">
          <h2 id="avbServT">Accesos directos a Servicios</h2>
          <a href="servicios.html">Ver catálogo completo %s</a>
        </div>
        <div class="avb-accs">
%s
        </div>
      </section>''' % (ico('flecha', 16), tarjetas)


def pie(sello):
    """El pie de esta página: los cinco conteos de la base y las ligas, sin «Volver al auditor»."""
    import monetizacion
    c = {x[0]: x for x in monetizacion.contadores()}
    falta = [k for k in CONTEOS if k not in c]
    if falta:
        raise SystemExit('auditor_bento.py: monetizacion.contadores() ya no trae %s' % ', '.join(falta))
    li = '\n'.join('          <li><b>%s</b> <span>%s</span></li>' % (format(c[k][1], ','), html.escape(c[k][2])) for k in CONTEOS)
    return '''<footer class="apartado-pie avb-pie">
    <div class="apartado-ancho">
      <a class="avb-conteos" href="base-al-dia.html">
        <ul>
%s
        </ul>
        <span class="avb-con-nota">Conteos de los archivos de la plataforma <span class="est-chip est-derivado">auditada</span> · cada uno con su fuente en La base al día %s</span>
      </a>
      <nav class="avb-pie-ligas" aria-label="Pie de página">
        <a href="indice.html">Índice general</a>
        <a href="aviso-de-privacidad.html">Aviso de privacidad</a>
        <a href="derecho-de-replica.html">Derecho de réplica</a>
        <span>Auditavisión · Toda cifra lleva su fuente oficial · Versión publicada: <b>%s</b></span>
      </nav>
    </div>
  </footer>''' % (li, ico('flecha', 14), sello)


def bloque(chat, servicios):
    """El lienzo completo alrededor del chat del Auditor. `servicios`: los id de SERVICIOS de apartados.py."""
    revisa(servicios)
    return '''<div class="avb" id="avb">
    %s
    <div class="avb-lienzo">
      %s
      %s
      <section class="avb-lector" id="avbLector" hidden aria-labelledby="avbLecT">
        <h2 id="avbLecT">Tu revisión, en este navegador</h2>
        <iframe id="avbMarco" class="av-en-chat" title="Lector de tus archivos"></iframe>
      </section>
      %s
    </div>
  </div>''' % (_lado(len(servicios)), _caja(), _chat(chat), _servicios())
