#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Códigos de acceso a la versión de prueba (pedido del autor, 29-10-2026:
«que funcionara un poquito como lo hace este Nintendo Switch… cuatro casillas
de un lado, espacio, cuatro casillas de otro lado, y yo estar administrando
tanto el número de código como el tiempo de apertura»).

Mientras la plataforma se perfecciona todo es gratis: el código solo abre la
puerta. Tres piezas:

- canjea-tu-codigo.html: las ocho casillas (XXXX-XXXX). El canje da un «pase»
  que se queda en el navegador, sin cuenta ni correo.
- administracion-codigos.html: el panel del autor. Entra con su correo (enlace
  mágico de Supabase), genera códigos con su duración y sus usos, los revoca y
  los descarga en CSV. Solo lo abre una cuenta de la tabla administradores.
- assets/auditor/js/acceso.js, en el <head> de todas las páginas: si el
  candado está puesto y el navegador no trae un pase vigente, manda a
  canjea-tu-codigo.html. Su configuración la escribe este módulo.

La base vive en supabase/migrations/20261030000001_codigos.sql y la función
que canjea, en supabase/functions/codigo. **El candado está apagado** hasta
que exista el proyecto de Supabase: se enciende con CANDADO = True.

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
CANDADO = False
# La llave PÚBLICA (anon) del proyecto de Supabase. Va en la página por
# diseño; la llave de servicio, nunca.
SUPABASE_ANON = ''

CANJE = 'canjea-tu-codigo.html'
PANEL = 'administracion-codigos.html'
# Las páginas que abren sin código: la del canje, el panel y lo que la ley
# obliga a tener siempre a la vista.
LIBRES = [CANJE, PANEL, 'aviso-de-privacidad.html']

# Las duraciones del panel (intervalos de PostgreSQL) y cómo se leen.
DURACIONES = [
    ('1 day', '1 día'), ('3 days', '3 días'), ('5 days', '5 días'), ('7 days', '1 semana'),
    ('14 days', '2 semanas'), ('1 mon', '1 mes'), ('3 mons', '3 meses'), ('6 mons', '6 meses'), ('1 year', '1 año'),
]


def config():
    import apartados
    funciones = apartados.FUNCIONES.rstrip('/')
    if CANDADO and not (funciones and SUPABASE_ANON):
        raise SystemExit('acceso.py: CANDADO está puesto, pero faltan FUNCIONES (apartados.py) o SUPABASE_ANON: '
                         'nadie podría canjear un código y la plataforma quedaría cerrada para todos.')
    return {
        'candado': CANDADO,
        'funciones': funciones,
        'supabase': re.sub(r'/functions/v1$', '', funciones),
        'anon': SUPABASE_ANON,
        'canje': CANJE,
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
    uno = lambda i: ('<input class="ac-casilla" type="text" inputmode="text" autocomplete="off" autocapitalize="characters" '
                     'spellcheck="false" maxlength="1" aria-label="Carácter %d de 8" data-i="%d">' % (i + 1, i))
    return ('<div class="ac-casillas" role="group" aria-label="Tu código, de ocho caracteres">'
            '<span class="ac-grupo">%s</span><span class="ac-guion" aria-hidden="true">–</span><span class="ac-grupo">%s</span></div>'
            % (''.join(uno(i) for i in range(4)), ''.join(uno(i) for i in range(4, 8))))


def pagina_canje():
    sin_base = '' if config()['funciones'] else (
        '<p class="ac-aviso" id="acSinBase">⏳ El canje se enciende cuando la plataforma tenga su base de datos (Supabase). '
        'Por ahora la entrada es libre.</p>')
    bloque = ('<form class="ac-canje" id="acCanje" novalidate>\n'
              '  <label class="ac-et" for="acCasilla0">Escribe tu código</label>\n'
              '  %s\n'
              '  <p class="ac-ayuda">Son ocho letras y números. No lleva la O, el cero, la I, la L ni el uno, para que no se confundan. '
              'Si lo copiaste, pégalo en la primera casilla.</p>\n'
              '  <button class="sz-btn sz-btn-of ac-boton" type="submit" disabled>Canjear</button>\n'
              '  <p class="ac-estado" id="acEstado" role="status" aria-live="polite"></p>\n'
              '</form>\n%s\n'
              '<div class="ac-tuyo" id="acTuyo" hidden></div>') % (_casillas().replace('data-i="0"', 'data-i="0" id="acCasilla0"'), sin_base)
    return {
        'archivo': CANJE,
        'menu': 'Canjea tu código',
        'icono': '🎫',
        'titulo': 'Canjea tu código',
        'lema': 'La versión de prueba, por invitación',
        'entrada': ('Auditavisión está en su versión de prueba y por ahora es gratis. Para entrar necesitas un código de invitación: '
                    'escríbelo aquí y la plataforma se abre en este navegador por el tiempo que diga tu código. '
                    'No te pedimos nombre ni correo.'),
        'estilos': ['acceso.css'],
        'scripts': ['acceso-paginas.js'],
        'secciones': [
            {'id': 'canje', 'titulo': 'Tu código', 'texto': 'Cuatro caracteres, un guion y otros cuatro: XXXX-XXXX.', 'tarjetas': [], 'bloque': bloque},
            {'id': 'como', 'titulo': 'Cómo funciona', 'texto': 'Lo que pasa al canjear.', 'tarjetas': [],
             'bloque': ('<ul>\n'
                        '<li><b>El tiempo corre desde que lo canjeas</b>, no desde que te lo dieron.</li>\n'
                        '<li><b>Si canjeas otro código</b> en el mismo navegador, su tiempo se suma al que te quedaba.</li>\n'
                        '<li><b>Se queda en este navegador.</b> Si cambias de teléfono o borras los datos del sitio, necesitas otro código.</li>\n'
                        '<li><b>Lo que guardamos:</b> que un código se canjeó, cuándo y un número al azar que identifica a tu navegador. '
                        'Nada que diga quién eres. Lo explica el <a href="aviso-de-privacidad.html">aviso de privacidad</a>.</li>\n'
                        '</ul>')},
        ],
    }


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
              '    <form class="ac-generar" id="acGenerar" novalidate>\n'
              '      <h3>Generar códigos</h3>\n'
              '      <div class="ac-fila">\n'
              '        <label>Cantidad <input class="ac-campo" name="cantidad" type="number" min="1" max="500" value="10" required></label>\n'
              '        <label>Duración <select class="ac-campo" name="duracion">%s<option value="otra">Otra (en días)</option></select></label>\n'
              '        <label class="ac-otra" hidden>Días <input class="ac-campo" name="dias" type="number" min="1" max="1825" value="10"></label>\n'
              '        <label>Usos por código <input class="ac-campo" name="usos" type="number" min="1" max="10000" value="1" required></label>\n'
              '        <label>Canjear antes del <input class="ac-campo" name="antes" type="date"></label>\n'
              '        <label class="ac-ancho">Nota <input class="ac-campo" name="nota" type="text" maxlength="120" placeholder="Para quién son: «Taller», «Prensa»…"></label>\n'
              '      </div>\n'
              '      <p class="ac-acciones"><button class="sz-btn sz-btn-of" type="submit">Generar</button>\n'
              '        <button class="sz-btn ac-claro" type="button" id="acCsv">Descargar CSV</button>\n'
              '        <button class="sz-btn ac-claro" type="button" id="acRecargar">Actualizar la lista</button></p>\n'
              '      <p class="ac-estado" id="acGenerarEstado" role="status" aria-live="polite"></p>\n'
              '    </form>\n'
              '    <div class="ac-resumen" id="acResumen"></div>\n'
              '    <div class="ac-tabla-caja"><table class="ac-tabla" id="acTabla">\n'
              '      <thead><tr><th>Código</th><th>Duración</th><th>Usos</th><th>Estado</th><th>Nota</th><th></th></tr></thead>\n'
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
                    'y los revocas cuando quieras. Solo abre con una cuenta dada de alta en la administración.'),
        'noindex': True,
        'estilos': ['acceso.css'],
        'scripts': ['acceso-paginas.js'],
        'secciones': [{'id': 'panel', 'titulo': 'Los códigos', 'texto': 'El tiempo de cada código corre desde que se canjea.', 'tarjetas': [], 'bloque': bloque}],
    }


def paginas():
    escribir_config()
    return [pagina_canje(), pagina_panel()]
