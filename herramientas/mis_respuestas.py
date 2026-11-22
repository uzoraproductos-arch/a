#!/usr/bin/env python3
"""La página automatizada de tus respuestas: lo que le pediste al Auditor y los servicios que vienen a tu caso.

Pedido del autor, 19-11-2026: «ya después vendrá esta parte donde estará la página,
digamos, automatizada de las respuestas o de los servicios a los problemas, peticiones,
solicitudes de lo que hayan hecho los usuarios».

Cómo funciona, sin servidor y sin cuenta:

- El chat anota cada pregunta que contesta en el navegador del lector (`av-caso` de
  localStorage, hasta 60; `caso()` de `asistente.js`): la pregunta, la fecha, el modo,
  la respuesta en corto (el texto que ya dio, nunca una cifra nueva), «Saber más», el
  enlace que vuelve a armar su dictamen y los servicios que aprovechan esa página
  (`srv`, el mismo mapa de «Ya revisamos esto por ti»). Lo que no supo
  contestar queda como solicitud, para pedirla como investigación.
- `mis-respuestas.html` (esta página, en la pestaña Auditor) lo lee y lo arma en el
  navegador (`mis-respuestas.js`): tus preguntas, los servicios para tu caso (de más a
  menos respuestas que los piden, con su cotización ya llenada con tus preguntas),
  tus dictámenes (`av-dics`) y tus revisiones de Mi Auditavisión (`av-mia`).
- **Nada sale del navegador**: la cotización solo se envía si el lector la manda. **Nunca
  un monto**: cada servicio dice su forma de cobro (`COBRO`). Se imprime, se descarga y
  se borra ahí mismo, y el aviso de privacidad lo dice (`_AV_NAVEGADOR` de `apartados.py`).
"""
import html
import json

ARCHIVO = 'mis-respuestas.html'
CLAVE = 'av-caso'


def pagina(servicios, cobro, modos, auditor):
    """La página. Los datos que necesita el navegador (nombre, ícono, cobro y página de
    cada servicio; nombre e ícono de cada modo) van dentro, como JSON."""
    srv = {s[0]: [s[1], s[2], cobro[s[0]], 'servicio-%s.html' % s[0]] for s in servicios}
    mod = {m[0]: [m[1], m[2]] for m in modos}
    datos = json.dumps({'srv': srv, 'modos': mod, 'chat': auditor}, ensure_ascii=False, sort_keys=True).replace('</', '<\\/')
    cuerpo = '''<div class="mr" id="mr" data-chat="%(chat)s">
        <p class="mr-priv"><span aria-hidden="true">🔒</span> <span>Esta página se arma <b>solo en tu navegador</b>, con lo que le preguntaste al Auditor en este dispositivo.
          Nada se manda a ningún servidor: la cotización sale solo si tú la envías. La borras cuando quieras.</span></p>
        <div class="mr-vacio" id="mrVacio" hidden>
          <p><b>Todavía no hay respuestas guardadas en este navegador.</b> Pregúntale al Auditor lo que quieras (un dato, tu municipio, una factura, una empresa):
            cada respuesta se anota aquí sola, con su dictamen, su «Saber más» y el servicio que viene a tu caso.</p>
          <p><a class="mr-btn" href="%(chat)s">💬 Pregúntale al Auditor</a></p>
        </div>
        <div id="mrLleno" hidden>
          <ul class="mr-cifras" id="mrCifras" aria-label="Tu caso en números"></ul>
          <nav class="mr-saltos" aria-label="En esta página">
            <a href="#mr-preguntas">💬 Tus preguntas</a><a href="#mr-servicios">🧰 Servicios para tu caso</a><a href="#mr-dictamenes">🧾 Tus dictámenes</a>
          </nav>
          <section class="mr-sec" id="mr-preguntas" aria-labelledby="mrPregT">
            <h2 id="mrPregT">💬 Lo que le preguntaste al Auditor</h2>
            <p class="mr-nota">La más reciente primero. Cada una con lo que te contestó en corto, «Saber más», su dictamen y los servicios que vienen al caso.
              Lo que no supo contestar queda como solicitud: pídela como investigación.</p>
            <ol class="mr-lista" id="mrLista"></ol>
          </section>
          <section class="mr-sec" id="mr-servicios" aria-labelledby="mrServT">
            <h2 id="mrServT">🧰 Los servicios para tu caso</h2>
            <p class="mr-nota">Lo básico ya lo hiciste tú, gratis, en el chat. Si quieres ir más a fondo, estos son los servicios que aprovechan las páginas a las que te llevaron tus respuestas,
              de más a menos. La cotización llega ya llenada con tus preguntas, y el costo y el plazo te llegan por escrito antes de empezar.</p>
            <ul class="mr-srv" id="mrSrv"></ul>
          </section>
          <section class="mr-sec" id="mr-dictamenes" aria-labelledby="mrDicT">
            <h2 id="mrDicT">🧾 Tus dictámenes y tus revisiones</h2>
            <div id="mrDics"></div>
          </section>
          <div class="mr-ctl" role="group" aria-label="Tu página">
            <button type="button" class="mr-btn" id="mrImprime">🖨️ Imprimir o guardar en PDF</button>
            <button type="button" class="mr-btn mr-btn-of" id="mrBaja">⬇️ Descargar (texto)</button>
            <button type="button" class="mr-btn mr-btn-of" id="mrBorra">🗑️ Borrar mis respuestas</button>
          </div>
          <p class="mr-nota">Esta página no es un documento oficial ni un peritaje: junta lo que el Auditor te contestó con la base de la plataforma.
            Cada respuesta lleva a su página y a su dictamen, que vuelve a contestar con la misma base.</p>
        </div>
        <script type="application/json" id="mrDatos">%(datos)s</script>
      </div>''' % {'chat': html.escape(auditor, quote=True), 'datos': datos}
    return {
        'archivo': ARCHIVO, 'menu': 'Tus respuestas', 'menu_archivo': ARCHIVO, 'padre': (auditor, 'Auditor'),
        'icono': '📋', 'titulo': 'Tus respuestas', 'lema': 'Lo que le pediste al Auditor y los servicios que vienen a tu caso',
        'entrada': ('Todo lo que le preguntes al Auditor queda aquí, en una sola página que se arma sola: cada respuesta en corto, '
                    'su «Saber más», su dictamen, lo que no supo contestarte y los servicios que vienen a tu caso, ya listos para pedirlos.'),
        'estilos': ['mis-respuestas.css'], 'scripts': ['mis-respuestas.js'],
        'secciones': [{'id': 'tu-caso', 'titulo': 'Tu caso', 'sin_cab': True, 'texto': '', 'tarjetas': [], 'bloque': cuerpo}],
    }
