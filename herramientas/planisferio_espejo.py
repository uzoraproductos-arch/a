#!/usr/bin/env python3
"""Las páginas propias del Planisferio: el reflejo de lo que antes mandaba a la Enciclopedia.

Decisión del autor, 19-11-2026: «todo el contenido que se encuentra en las fichas,
tarjetas de la pestaña de planisferio es para que… al momento en que se dé clic…
se abran en su propia página automatizada, no dentro de la enciclopedia», y «la
enciclopedia únicamente es el reflejo de la construcción de nuestra base de datos».

Cómo funciona:

1. `a_espejo()` corre sobre cada página del Planisferio al generarla (`pagina()` de
   `apartados.py`): una liga a una página de la Comunidad (la Enciclopedia) se cambia
   por la de su reflejo, `planisferio-ficha-<página>`, con su `?` y su `#`, y la anota.
2. `generar()` corre al final, cuando ya existen todas las páginas: escribe cada
   reflejo a partir de la página generada de la Enciclopedia (**la misma página,
   nunca una copia a mano ni una cifra nueva**), marcada como Planisferio, con sus
   migas en el Planisferio y su dirección canónica en la original (para buscadores
   es la misma página; `sitemap.py` no la lista). Dentro, sus ligas siguen la regla
   de la estrella: a otro reflejo, directo; a otra pestaña, por el Auditor.
3. Un reflejo que ya no se pide se borra; el que pida `planisferio.js` y no exista
   detiene la generación.
"""
import glob
import html
import os
import re
from urllib.parse import unquote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIJO = 'planisferio-ficha-'
PIDEN = set()   # las páginas de la Enciclopedia que el Planisferio pide (se llena al generar)
_A = re.compile(r'(<a\b[^>]*?\bhref=")([^"]+)(")')


def nombre(base):
    return PREFIJO + base


def _base(liga):
    return liga.split('#')[0].split('?')[0]


def _main(texto, fn):
    i, j = texto.find('<main'), texto.rfind('</main>')
    if i < 0 or j < 0:
        return texto
    return texto[:i] + fn(texto[i:j]) + texto[j:]


def a_espejo(texto):
    """En <main>, cada liga a la Comunidad pasa a su reflejo en el Planisferio."""
    import servicios_fichas as sf

    def cambia(m):
        liga = html.unescape(m.group(2))
        if re.match(r'[a-z]+:|#|//', liga):
            return m.group(0)
        b = _base(liga)
        if not b.endswith('.html') or sf.pestana_de(b) != 'Comunidad' or not os.path.exists(os.path.join(RAIZ, b)):
            return m.group(0)
        PIDEN.add(b)
        return m.group(1) + html.escape(nombre(b) + liga[len(b):], quote=True) + m.group(3)
    return _main(texto, lambda s: _A.sub(cambia, s))


def _desenvuelve(s):
    """Una liga al chat que abría una página del Planisferio vuelve a ser directa: el
    reflejo ya está en el Planisferio."""
    import servicios_fichas as sf

    def cambia(m):
        liga = html.unescape(m.group(2))
        if not liga.startswith(sf.CHAT + '?'):
            return m.group(0)
        x = re.search(r'[?&]abre=([^&]+)', liga)
        if not x:
            return m.group(0)
        dest = unquote(x.group(1))
        if sf.pestana_de(dest) != 'Planisferio':
            return m.group(0)
        return m.group(1) + html.escape(dest, quote=True) + m.group(3)
    return _A.sub(cambia, s)


def _reflejo(base, texto, titulo):
    import modos
    import servicios_fichas as sf
    # La pestaña: Planisferio.
    texto = re.sub(r' aria-current="page"(>(?:Auditor|Comunidad|Noticiero|Servicios)</a>)', r'\1', texto)
    texto = texto.replace('<a class="mega-menu-trigger" href="planisferio.html">',
                          '<a class="mega-menu-trigger" href="planisferio.html" aria-current="page">', 1)
    # Ronda 26B: la barra lateral (auditor_bento.lado) marca el Planisferio.
    def _lado(m):
        s = m.group(0).replace(' aria-current="page"', '')
        s = re.sub(r'data-pestana="[^"]*"', 'data-pestana="Planisferio"', s, count=1)
        return s.replace('<a href="planisferio.html">', '<a href="planisferio.html" aria-current="page">', 1)
    texto = re.sub(r'<aside class="avb-lado".*?</aside>', _lado, texto, count=1, flags=re.S)
    # Las migas: Inicio › Planisferio › la página.
    texto = re.sub(r'<nav class="apartado-migas".*?</nav>',
                   lambda m: ('<nav class="apartado-migas" aria-label="Estás en"><a href="index.html">Inicio</a> <span aria-hidden="true">›</span> '
                              '<a href="planisferio.html">Planisferio</a> <span aria-hidden="true">›</span> <span>%s</span></nav>' % html.escape(titulo)),
                   texto, count=1, flags=re.S)
    aviso = ('<p class="pl-espejo"><span aria-hidden="true">📍</span> <span>Lo ves desde el <b>Planisferio</b>: es la misma página de la base, '
             'sin una cifra distinta. <a href="planisferio.html">Volver al mapa</a> · <a href="%s">Pregúntale al Auditor</a></span></p>') % (
        sf.por_auditor(base, titulo, modos.modo_pagina(base)))

    def dentro(s):
        s = _desenvuelve(s)
        # A otro reflejo, directo (misma pestaña).
        s = _A.sub(lambda m: m.group(1) + nombre(_base(m.group(2))) + m.group(2)[len(_base(m.group(2))):] + m.group(3)
                   if _base(m.group(2)) in PIDEN and not re.match(r'[a-z]+:|#|//', m.group(2)) else m.group(0), s)
        k = s.find('>') + 1
        return s[:k] + aviso + s[k:]
    texto = _main(texto, dentro)
    # A otra pestaña, por el Auditor.
    return sf.por_auditor_html(texto, 'Planisferio', None, modos.modo_pagina)


def generar():
    with open(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'planisferio.js'), encoding='utf-8') as f:
        falta = sorted({b for b in re.findall(PREFIJO + r'([a-z0-9-]+\.html)', f.read()) if b not in PIDEN})
    if falta:
        raise SystemExit('planisferio_espejo: planisferio.js liga a reflejos que ninguna página pide: %s' % ', '.join(falta))
    for viejo in glob.glob(os.path.join(RAIZ, PREFIJO + '*.html')):
        if os.path.basename(viejo)[len(PREFIJO):] not in PIDEN:
            os.remove(viejo)
    for base in sorted(PIDEN):
        with open(os.path.join(RAIZ, base), encoding='utf-8', newline='') as f:
            texto = f.read()
        t = re.search(r'<title>(.*?)(?: · Auditavisión)?</title>', texto, re.S)
        titulo = html.unescape(t.group(1)).strip() if t else base
        with open(os.path.join(RAIZ, nombre(base)), 'w', encoding='utf-8', newline='') as f:
            f.write(_reflejo(base, texto, titulo))
    print('planisferio: %d páginas propias (reflejos de la Enciclopedia)' % len(PIDEN))
    return 0
