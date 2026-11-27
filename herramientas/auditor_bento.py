#!/usr/bin/env python3
"""La página del Auditor (herramienta-inspector-pregunta.html).

Ronda 21 (25-11-2026): barra lateral en azul marino y lienzo modular. Ronda 22: una sola caja de pregunta.
Ronda 23 (25-11-2026, «Solo barra lateral, tipo Claude.ai»): una sola navegación, sin emojis.
Ronda 24 (25-11-2026, decisión del autor): **la Estación de Auditoría en tres paneles**.

- **Izquierda**: la barra lateral de la Ronda 23 (marca, los seis destinos, con la Biblioteca al final, «Tu portafolio»,
  «Cómo funciona (3 pasos)» y la cuenta que llena acceso.js).
- **Centro**: el Auditor, con la imagen de la entrada de fondo bajo un velo claro (su huella es la de
  acceso.FOTO_ENTRADA), una barra fina (insignia y «Mostrar / Ocultar mesa derecha»), el encabezado editorial (logo,
  «¿Quiénes somos?» de acceso.QUIENES_ENTRADA y las preguntas de acceso.PREGUNTAS_ENTRADA, una cada 4 s: **se cambian
  allá, nunca aquí**), la única caja (con «Probar XML de muestra», que arma en el navegador un CFDI ficticio con RFC
  genéricos del SAT), los ejemplos, la plática y el lector local.
- **Derecha, la Mesa de Trabajo**: «Herramientas» (los seis accesos a Servicios con su etiqueta, leída de
  monetizacion.PRECIO_FUNDADOR, y el resumen de planes) y «Expediente vivo» (auditor-bento.js lee las fuentes de la
  última respuesta del chat: no escribe ninguna).
- **El pie** trae los cinco conteos de monetizacion.contadores() (**ninguna cifra escrita a mano**).

Los únicos montos van dentro de <!--precio-fundador--> y salen de monetizacion.PRECIO_FUNDADOR. No trae datos propios ni
entra a la huella del dictamen. Sin emojis: íconos SVG de trazo, sin librerías.
"""
import html
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANJE = 'canjea-tu-codigo.html'
PANEL = 'administracion-codigos.html'
PLANES_LIGA = 'servicios.html#precio-fundador'

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
    'panel': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M15 4v16"/>',
    'ayuda': '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 0 1 4.9.7c0 1.7-2.4 2.3-2.4 3.8"/><path d="M12 17h.01"/>',
    'boleto': '<path d="M3 8a2 2 0 0 0 2-2h14a2 2 0 0 0 2 2v2a2 2 0 0 0 0 4v2a2 2 0 0 0-2 2H5a2 2 0 0 0-2-2v-2a2 2 0 0 0 0-4z"/><path d="M14 6v12" stroke-dasharray="2 2"/>',
    'matraz': '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.8 3h10.4a2 2 0 0 0 1.8-3l-5-9V3"/><path d="M7.5 15h9"/>',
    'cerrar': '<path d="M6 6l12 12M18 6 6 18"/>',
    'carpeta': '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    'marcador': '<path d="M6 3h12v18l-6-4-6 4z"/>',
    'liga': '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    'herramientas': '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
    'pausa': '<path d="M9 5v14M15 5v14"/>',
    'libro': '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5"/><path d="M9 7h6"/>',
}


def ico(nombre, tam=18, clase='avb-i'):
    """Un ícono de trazo fino, decorativo (aria-hidden)."""
    return ('<svg class="%s" width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">%s</svg>') % (clase, tam, tam, TRAZOS[nombre])


# Los destinos de la barra lateral, en el orden del menú (el primero es esta página). **La Biblioteca va siempre al
# final** (decisión del autor, 25-11-2026): un destino nuevo entra antes que ella, y revisa() lo comprueba.
BIBLIOTECA = 'diccionario.html'
NAV = [('herramienta-inspector-pregunta.html', 'lupa', 'Auditor'),
       ('servicios.html', 'maletin', 'Servicios y Planes'),
       ('planisferio.html', 'mapa', 'Planisferio'),
       ('noticias-relevantes.html', 'periodico', 'Noticiero'),
       ('participa.html', 'personas', 'Comunidad'),
       (BIBLIOTECA, 'libro', 'Biblioteca')]
# Las imágenes del formato anterior: no van ni en esta página ni en servicios.html (Ronda 24, decisión del autor).
# La única imagen editorial del Auditor es la de la entrada (acceso.FOTO_ENTRADA), de fondo del centro.
IMAGENES_VIEJAS = ('servicios-encabezado', 'herr-auditor-foroptero', 'herr-inspector-ilustracion', 'showcase_')
# Los cuatro modos (el orden de asistente.ORDEN_AUDITOR) y su pista corta.
SEGMENTOS = [('inspector', 'lupa', 'Inspector', 'Investigación completa, con dictamen sellado'),
             ('ciudadano', 'usuario', 'Ciudadano', 'En corto, como te lo diría un amigo'),
             ('periodista', 'pluma', 'Periodista', 'Contado como nota, con sus documentos'),
             ('ambientalista', 'hoja', 'Ambientalista', 'El costo y el daño ambiental')]
# Las preguntas de ejemplo: cada una ya la contesta el chat (preguntas_auditor.json). Ronda 28B: ya no van como fila de
# botones bajo la caja; rotan en «Pregúntale al Auditor», después de las de acceso.PREGUNTAS_ENTRADA (que no se tocan).
CHIPS = ['Dame mi estado de cuenta cívico', 'Mi estado de cuenta ambiental', 'Estado de cuenta administrativo',
         '¿Mi proveedor está en la lista negra del SAT?', '¿Cuánto debe Jalisco?',
         '¿Cuánto costó el Tren Maya?', 'Diagnóstico de Pemex', 'Semáforo Patrimonial de Zapopan, Jalisco']
TITULO = 'Las cuentas del gobierno, con sus documentos'
# Los accesos de la Mesa de Trabajo: (ícono, etiqueta, título, una línea, servicio o liga, precio). El precio es
# ('gratis',), ('consumo', clave de PRECIO_FUNDADOR['consumo']) o ('plan', id de PRECIO_FUNDADOR['planes']): la
# etiqueta se arma de la tabla, nunca se escribe aquí.
ACCESOS = [
    ('escudo', 'Prevención', 'Contrapartes y 69-B',
     'Tu cartera contra las listas del SAT, Sancionados, la OFAC y la ONU.', 'contrapartes', ('gratis',)),
    ('factura', 'Facturas', 'Facturas XML · Cero CIEC',
     'Tus CFDI y recibos revisados por proveedor, con su cruce con la 69-B.', 'facturas', ('consumo', 'lote')),
    ('casa', 'Simuladores', 'Semáforo Patrimonial',
     'Antes de comprar o rentar: el predial de su ley, el Índice SHF y con quién firmas.', 'simulacion', ('consumo', 'semaforo')),
    ('mapa', 'Gobiernos', 'Estados y municipios',
     'Lo que le entra y lo que gasta, su deuda, su inversión y lo pendiente ante la ASF.', 'radiografia', ('gratis',)),
    ('edificio', 'Proveedores', 'Contratos y ASF',
     'Los contratos de una empresa en ComprasMX, la 69-B, Sancionados y la ASF.', 'diligencia', ('gratis',)),
    ('campana', 'Vigilancia', 'Vigía 69-B',
     'Cada semana, las altas, los cambios de situación y las bajas de la lista del SAT.', 'servicio-seguimiento.html#vigia', ('plan', 'pro')),
]
# Los tres pasos del recorrido «Cómo funciona» (auditor-bento.js): (a qué apunta, título, texto).
TOUR = [('avbForm', 'La caja del Auditor y sus cuatro modos',
         'Escribe tu pregunta en tus palabras. Arriba eliges el modo: Inspector, Ciudadano, Periodista o Ambientalista. '
         'El modo cambia la forma de contestar, nunca los datos.'),
        ('avbAdjuntos', 'Tus archivos, sin Contraseña del SAT',
         'Adjunta tus XML o un CSV de RFC, o prueba con el XML de muestra. Se leen en este navegador: nada se sube.'),
        ('avbMesa', 'La Mesa de Trabajo',
         'Aquí están las Herramientas y el Expediente vivo: las fuentes de cada respuesta, tu dictamen y tu portafolio. '
         'En pantallas angostas se abre con «Mostrar mesa derecha».')]
# Los conteos del pie (claves de monetizacion.contadores()).
CONTEOS = ('69b', 'contratos', 'municipios', 'predial', 'boveda')
ACEPTA = '.xml,.csv,.txt,text/xml,application/xml,text/csv,text/plain'


def _e(x):
    return html.escape(x, quote=True)


def _liga(destino):
    return destino if '.html' in destino else 'servicios-revisa.html?s=' + destino


def etiqueta(precio):
    """La etiqueta de un acceso, leída de monetizacion.PRECIO_FUNDADOR."""
    import monetizacion
    if precio[0] == 'gratis':
        return 'Gratis'
    if precio[0] == 'consumo':
        t = monetizacion.consumo(precio[1])
        return '%d token%s' % (t, '' if t == 1 else 's')
    if precio[0] == 'plan':
        return monetizacion.plan(precio[1])['nombre']
    raise SystemExit('auditor_bento.py: precio desconocido %r' % (precio,))


def revisa(servicios):
    """Detiene la generación si una liga, un servicio, la imagen o un paso del recorrido no existen."""
    import acceso
    acceso._foto_ok()
    if NAV[-1][0] != BIBLIOTECA:
        raise SystemExit('auditor_bento.py: la Biblioteca (%s) debe ir al final de la barra lateral' % BIBLIOTECA)
    for u in [n[0] for n in NAV] + [_liga(a[4]) for a in ACCESOS] + [CANJE, PANEL, 'base-al-dia.html', 'indice.html', 'servicios.html']:
        if not os.path.exists(os.path.join(RAIZ, u.split('#')[0].split('?')[0])):
            raise SystemExit('auditor_bento.py: la liga %s no existe' % u)
    for a in ACCESOS:
        if '.html' not in a[4] and a[4] not in servicios:
            raise SystemExit('auditor_bento.py: el servicio %s no está en SERVICIOS' % a[4])
        etiqueta(a[5])
    if not open(os.path.join(RAIZ, 'servicio-seguimiento.html'), encoding='utf-8').read().count('id="vigia"'):
        raise SystemExit('auditor_bento.py: servicio-seguimiento.html ya no tiene #vigia')
    if not acceso.PREGUNTAS_ENTRADA or not acceso.QUIENES_ENTRADA:
        raise SystemExit('auditor_bento.py: faltan las preguntas o el «¿Quiénes somos?» de la entrada (acceso.py)')


def sin_imagenes_viejas(nombre, texto):
    """Detiene la generación si la página trae una imagen del formato anterior."""
    for v in IMAGENES_VIEJAS:
        if v in texto:
            raise SystemExit('auditor_bento.py: %s trae una imagen del formato anterior (%s)' % (nombre, v))


AUDITOR = NAV[0][0]
# Ronda 26B (26-11-2026, decisión del autor): la misma barra lateral en todas las páginas (cabecera() de apartados.py
# la pone en lugar de la barra superior vieja). Bajo la Biblioteca va «Cómo clasificamos los datos»: los tres sellos.
LEYENDA = [('oficial', 'oficial', 'Cifra textual de un documento público: DOF, SHCP, SAT, ASF, INEGI.'),
           ('derivado', 'auditada', 'Cruce o cálculo verificable que hacemos sobre documentos oficiales, con su operación.'),
           ('pendiente', 'pendiente', 'La autoridad no lo ha publicado o la ley aún no está cotejada: nunca lo inventamos.')]


def lado(actual, n_serv, en_auditor=False, pestana=''):
    """La barra lateral: en el Auditor, con sus botones («Nueva investigación», «Cómo funciona»); en las demás páginas,
    esos dos son ligas al Auditor. Ronda 26E: la barra arranca con la marca y los seis destinos, y «+ Nueva
    investigación» va dentro de «Tu portafolio». `actual`: el destino de NAV que se marca (aria-current), o '' si ninguno."""
    nav = []
    for u, i_, t in NAV:
        pastilla = ' <span class="avb-pastilla" title="%d servicios">%d</span>' % (n_serv, n_serv) if u == 'servicios.html' else ''
        nav.append('        <a href="%s"%s>%s<span>%s</span>%s</a>' % (u, ' aria-current="page"' if u == actual else '', ico(i_), t, pastilla))
    ley = '\n'.join('          <li><span class="est-chip est-%s">%s</span> %s</li>' % (c, n, html.escape(x)) for c, n, x in LEYENDA)
    if en_auditor:
        nueva = '<button type="button" class="avb-nueva" id="avbNueva">%s Nueva investigación</button>' % ico('mas', 16)
        tour = '<button type="button" class="avb-tour-btn" id="avbTourBtn">%s Cómo funciona (3 pasos)</button>' % ico('ayuda')
        # Ronda 34: en celular, la franja del Auditor enseña la billetera, y la Mesa y la insignia viven en el menú.
        movil = ('<div class="avb-lado-movil">\n        <button type="button" class="avb-mesa-btn-m" id="avbMesaBtnM" aria-controls="avbMesa">'
                 '%s<span>Mostrar mesa derecha</span><i class="avb-aviso" id="avbAvisoM" hidden></i></button>\n'
                 '        <p class="avb-insignia">%s Plataforma abierta · Cero CIEC · Datos oficiales</p>\n      </div>' % (ico('panel'), ico('check', 16)))
    else:
        nueva = '<a class="avb-nueva" href="%s">%s Nueva investigación</a>' % (AUDITOR, ico('mas', 16))
        tour = '<a class="avb-tour-btn" href="%s?tour=1">%s Cómo funciona (3 pasos)</a>' % (AUDITOR, ico('ayuda'))
        movil = ''
    return LADO % (_e(pestana or ('Auditor' if en_auditor else '')), AUDITOR, ico('panel'), '\n'.join(nav), ley, ico('flecha', 14), nueva, tour, CANJE, ico('llave'), movil)


LADO = '''<aside class="avb-lado" id="avbLado" data-pestana="%s" aria-label="Navegación de Auditavisión">
      <div class="avb-lado-cab">
        <div class="avb-marca">
          <button type="button" class="avb-logo-btn" id="apartadoPresentacion" title="Quiénes somos: abrir la presentación de Auditavisión" aria-label="Quiénes somos: abrir la presentación de Auditavisión"><img src="assets/auditor/img/logo-auditavision.svg" alt="" width="64" height="50"></button>
          <a class="avb-marca-tx" href="%s"><b>Auditavisión</b></a>
        </div>
        <button type="button" class="avb-lado-menu" id="avbLadoMenu" aria-controls="avbLadoCuerpo" aria-expanded="false">%s<span>Menú</span></button>
      </div>
      <div class="avb-lado-cuerpo" id="avbLadoCuerpo">
      <nav class="avb-nav" aria-label="Destinos">
%s
      </nav>
      <details class="avb-leyenda">
        <summary>Cómo clasificamos los datos</summary>
        <ul>
%s
        </ul>
        <a href="base-al-dia.html">Cómo se alimenta la base %s</a>
      </details>
      <details class="avb-port" id="avbPort" open>
        <summary>Tu portafolio</summary>
        %s
        <ol id="avbPortLista" hidden></ol>
        <p class="avb-port-vacio" id="avbPortVacio">Aún no guardas investigaciones. «Guardar en mi portafolio», bajo cada respuesta del Auditor, en una Auditoría en imágenes o en el Inspector de Servicios, las deja aquí, solo en tu navegador.</p>
      </details>
      %s
      <div class="avb-acceso" id="avbAcceso">
        <a class="avb-ingresa" href="%s">%s Ingresar / Canjear código</a>
      </div>
      %s
      </div>
    </aside>'''


def _lado(n_serv):
    return lado(AUDITOR, n_serv, True)


def _barra():
    return '''<div class="avb-barra">
        <p class="avb-barra-tk" id="avbBarraTk"><b class="avb-barra-saldo" id="avbBarraSaldo"></b><a href="%s">Canjear / Solicitar código</a></p>
        <p class="avb-insignia">%s Plataforma abierta · Cero CIEC · Datos oficiales</p>
        <button type="button" class="avb-mesa-btn" id="avbMesaBtn" aria-controls="avbMesa" aria-expanded="true">%s<span>Ocultar mesa derecha</span><i class="avb-aviso" id="avbAviso" hidden></i></button>
      </div>''' % (CANJE, ico('check', 16), ico('panel'))


def _cab():
    import acceso
    pre = '\n'.join('            <li><button type="button" class="avb-rota-q" data-avb-q="%s">%s</button></li>' % (_e(q), html.escape(q))
                    for q in list(acceso.PREGUNTAS_ENTRADA) + [c for c in CHIPS if c not in acceso.PREGUNTAS_ENTRADA])
    return '''<header class="avb-cab">
        <div class="avb-cab-tit">
          <img src="assets/auditor/img/logo-auditavision.svg" alt="" width="100" height="79">
          <h1 class="avb-tit" id="avbTit">%s</h1>
        </div>
        <details class="avb-quienes" id="avbQuienes" open>
          <summary><h2>¿Quiénes somos?</h2></summary>
          <p>%s</p>
        </details>
        <div class="avb-rota" id="avbRota">
          <p class="avb-rota-et" id="avbRotaEt">Pregúntale al Auditor</p>
          <ul aria-labelledby="avbRotaEt">
%s
          </ul>
        </div>
      </header>''' % (html.escape(TITULO), html.escape(acceso.QUIENES_ENTRADA), pre)


def _caja():
    # Ronda 27A: el Modo Inspector lleva su insignia «Pro» (gasta lo de 'inspector' en monetizacion.PRECIO_FUNDADOR).
    import asistente
    ini = asistente.MODO_INICIAL
    seg = '\n'.join('              <button type="button" data-avb-modo="%s" data-pista="%s" title="%s" aria-pressed="%s">%s<span>%s</span>%s</button>' % (
        m, _e(p), _e(p), 'true' if m == ini else 'false', ico(i), n,
        ' <i class="avb-pro" aria-label="Pro">Pro</i>' if m == 'inspector' else '') for m, i, n, p in SEGMENTOS)
    return '''<form class="avb-box" id="avbForm" autocomplete="off" aria-labelledby="avbCajaT">
        <p class="avb-caja-t" id="avbCajaT">¿Qué quieres auditar hoy?</p>
        <div class="avb-box-arriba">
          <div class="avb-seg" role="group" aria-label="Modo del Auditor">
%s
          </div>
          <p class="avb-pista" id="avbPista" aria-live="polite">%s</p>
        </div>
        <label class="sr-only" for="avbQ">Pregunta por un RFC, un municipio, una megaobra o una nota</label>
        <textarea id="avbQ" rows="3" maxlength="600" placeholder="Por ejemplo: ¿quién ganó los contratos de la obra de mi ciudad?" required></textarea>
        <div class="avb-box-abajo">
          <div class="avb-adjuntos" id="avbAdjuntos">
            <label class="avb-adjunta" id="avbSuelta" for="avbArch" title="Se leen en tu navegador: nada se sube y nunca te pedimos la Contraseña del SAT">
              %s<span>Adjuntar XML / CSV <small>· Cero CIEC</small></span>
              <input type="file" id="avbArch" multiple accept="%s">
            </label>
            <button type="button" class="avb-muestra" id="avbMuestra" title="Una factura ficticia, armada en tu navegador con RFC genéricos de prueba del SAT">%s<span>Probar XML de muestra</span></button>
          </div>
          <button type="submit" id="avbEnvia"><span>Dictaminar</span>%s</button>
        </div>
        <p class="avb-costo" id="avbCosto" aria-live="polite"></p>
      </form>''' % (seg, html.escape(next(p for m, _i, _n, p in SEGMENTOS if m == ini)), ico('clip'), ACEPTA, ico('matraz'), ico('flecha'))


def _chat(chat):
    """Ronda 22: la plática original sigue aquí con su motor, sin su cabecera, su selector de modos, sus ejemplos ni
    su caja (auditor-bento.css); la tarjeta solo aparece cuando ya hay una pregunta (auditor-bento.js).
    Ronda 29: con una pregunta, la tarjeta sube arriba de la caja y abre con su barra fija (la última pregunta, lo que
    gastó en tokens y «Hacer otra pregunta»); cada respuesta se ordena como hoja de resultado en auditor-bento.js."""
    return '''<section class="avb-chatcard" id="avbChat" aria-labelledby="avbChatT" hidden>
        <div class="avb-rbar" id="avbRbar">
          <div class="avb-rbar-q">
            <h2 id="avbChatT">Tu plática con el Auditor</h2>
            <p id="avbRQ"></p>
          </div>
          <p class="avb-rbar-tk" id="avbRTk" aria-live="polite"></p>
          <button type="button" class="avb-rbar-otra" id="avbOtra">%s<span>Hacer otra pregunta</span></button>
        </div>
%s
      </section>''' % (ico('pluma'), chat)


def _planes():
    """El resumen de planes de la Mesa: sale de monetizacion.PRECIO_FUNDADOR, dentro de su marca."""
    import monetizacion as mo
    F, M = mo.PRECIO_FUNDADOR, mo.MARCA_PRECIO
    pro, pyme, paq = mo.plan('pro'), mo.plan('pyme'), F['paquetes'][0]
    return '''%s<div class="avb-mplan">
          <p class="avb-mplan-t">%s Planes y Precio Fundador</p>
          <ul>
            <li><b>%s</b> %s · %s</li>
            <li><b>Tokens</b> desde %s (%d tokens)</li>
            <li><b>%s</b> %s al mes · Precio Fundador</li>
            <li><b>%s</b> %s al mes · Precio Fundador</li>
          </ul>
          <p class="avb-mplan-t avb-mplan-t2">%s Lo que gasta cada acción</p>
          <ul class="avb-tabu">
%s
          </ul>
          <p class="avb-mplan-n">Recibes %d tokens gratis cada mes en este navegador. Gratis siempre: %s. Los pagos en línea se activan próximamente; hoy se recarga con códigos piloto y promocionales.</p>
          <a href="%s">Ver planes y códigos promocionales %s</a>
        </div>%s''' % (M[0], ico('boleto', 16), F['libre']['nombre'], mo.pesos(0), F['libre']['nota'].lower(), mo.pesos(paq['precio']),
                       paq['tokens'], pro['nombre'], mo.pesos(pro['precio']), pyme['nombre'], mo.pesos(pyme['precio']), ico('check', 16), tabulador(),
                       F['libre']['bienvenida'], html.escape(_lista([x[0].lower() + x[1:] for x in F['gratis']])), PLANES_LIGA, ico('flecha', 14), M[1])


def _lista(xs):
    return ', '.join(xs[:-1]) + ' y ' + xs[-1] if len(xs) > 1 else ''.join(xs)


def tabulador():
    """Ronda 27A: lo que gasta cada acción, leído de monetizacion.PRECIO_FUNDADOR (el mismo que cobra tokens.js)."""
    import monetizacion as mo
    return '\n'.join('            <li>%s <b>%d tokens</b></li>' % (html.escape(q), t) for _k, q, t in mo.PRECIO_FUNDADOR['consumo'])


def _mesa():
    tarjetas = '\n'.join('''          <a class="avb-acc" href="%s">
            <span class="avb-acc-ico">%s</span>
            <span class="avb-acc-tx"><small>%s</small><b>%s</b><span>%s</span></span>
            <em class="avb-et%s">%s</em>
          </a>''' % (_e(_liga(d)), ico(i, 20), html.escape(et), html.escape(t), html.escape(tx),
                     ' avb-et-libre' if pr[0] == 'gratis' else '', html.escape(etiqueta(pr))) for i, et, t, tx, d, pr in ACCESOS)
    return '''<aside class="avb-mesa" id="avbMesa" aria-labelledby="avbMesaT">
      <div class="avb-mesa-cab">
        <h2 id="avbMesaT">Mesa de Trabajo</h2>
        <button type="button" class="avb-mesa-x" id="avbMesaX" aria-label="Cerrar la mesa">%s</button>
      </div>
      <div class="avb-tabs" role="tablist" aria-label="Mesa de Trabajo">
        <button type="button" role="tab" id="avbTabH" aria-controls="avbPanH" aria-selected="true">%s Herramientas</button>
        <button type="button" role="tab" id="avbTabE" aria-controls="avbPanE" aria-selected="false" tabindex="-1">%s Expediente vivo</button>
      </div>
      <div class="avb-tabpanel" role="tabpanel" id="avbPanH" aria-labelledby="avbTabH">
        <div class="avb-accs">
%s
        </div>
        %s
        <a class="avb-catal" href="servicios.html#necesitas">Ver los servicios %s</a>
      </div>
      <div class="avb-tabpanel" role="tabpanel" id="avbPanE" aria-labelledby="avbTabE" hidden>
        <div class="avb-exp-vacio" id="avbExpVacio">%s<p>Haz una pregunta al centro para ver aquí sus fuentes oficiales y generar tu dictamen.</p></div>
        <div class="avb-exp" id="avbExp" hidden>
          <p class="avb-exp-q" id="avbExpQ"></p>
          <p class="avb-exp-chips" id="avbExpChips"></p>
          <div class="avb-exp-vis" id="avbExpVis" hidden></div>
          <h3 id="avbExpPorT" hidden>Portales para profundizar</h3>
          <ul class="avb-exp-por" id="avbExpPor" hidden></ul>
          <h3>Fuentes y documentos de la respuesta</h3>
          <ol class="avb-exp-fu" id="avbExpFu"></ol>
          <p class="avb-exp-sin" id="avbExpSin" hidden>Esta respuesta no cita un documento externo; ábrela con «Saber más» para ver sus fuentes.</p>
          <div class="avb-exp-acc">
            <a class="avb-exp-dic" id="avbExpDic" href="#" target="_blank" rel="noopener" hidden>%s<span>Generar dictamen</span></a>
            <a class="avb-exp-ver" id="avbExpVer" href="#" hidden>%s<span>Saber más</span></a>
            <button type="button" class="avb-exp-guarda" id="avbExpGuarda">%s<span>Guardar en mi portafolio</span></button>
          </div>
          <p class="avb-exp-nota">Lo que ves aquí es lo que citó la respuesta del chat, y el lugar que toca dibujado con lo que la base ya trae: no agregamos cifras ni documentos.</p>
        </div>
      </div>
    </aside>
    <div class="avb-velo" id="avbVelo" hidden></div>''' % (ico('cerrar'), ico('herramientas', 16), ico('carpeta', 16), tarjetas, _planes(),
                                                       ico('flecha', 14), ico('documento', 28), ico('documento', 16), ico('liga', 16), ico('marcador', 16))


def _tour():
    import json
    datos = json.dumps([{'id': i, 't': t, 'x': x} for i, t, x in TOUR], ensure_ascii=False).replace('</', '<\\/')
    return '''<div class="avb-tour" id="avbTour" role="dialog" aria-modal="true" aria-labelledby="avbTourT" hidden>
      <div class="avb-tour-luz" id="avbTourLuz"></div>
      <div class="avb-tour-card" id="avbTourCard">
        <p class="avb-tour-n" id="avbTourN"></p>
        <h2 id="avbTourT"></h2>
        <p id="avbTourX"></p>
        <p class="avb-tour-acc"><button type="button" id="avbTourCierra">Cerrar</button><button type="button" id="avbTourSig">Siguiente</button></p>
      </div>
      <script type="application/json" id="avbTourDatos">%s</script>
    </div>''' % datos


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
    """La Estación completa alrededor del chat del Auditor. `servicios`: los id de SERVICIOS de apartados.py."""
    revisa(servicios)
    return '''<div class="avb" id="avb">
    %s
    <div class="avb-centro">
      %s
      <div class="avb-lienzo">
      %s
      %s
      %s
      <section class="avb-lector" id="avbLector" hidden aria-labelledby="avbLecT">
        <h2 id="avbLecT">Tu revisión, en este navegador</h2>
        <iframe id="avbMarco" class="av-en-chat" title="Lector de tus archivos"></iframe>
      </section>
      </div>
    </div>
    %s
    %s
  </div>''' % (_lado(len(servicios)), _barra(), _cab(), _caja(), _chat(chat), _mesa(), _tour())
