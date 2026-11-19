#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La política de seguridad de contenido (CSP) de Auditavisión.

Por qué (19-11-2026, pedido del autor: «la forma de proteger la información»).
La LFPDPPP (DOF 20-03-2025), art. 18, pide medidas de seguridad técnicas según
el riesgo y la tecnología disponible. La plataforma lee facturas, recibos de
nómina, estados de resultados y listas de RFC **en el navegador, sin subirlos**:
la CSP es la defensa del navegador para que, aun si alguien lograra inyectar
código en una página, ese código no pueda mandar lo que el lector abrió a un
servidor ajeno (`connect-src`), cargar programas de otro sitio (`script-src`)
ni cambiar a dónde apuntan las ligas y formularios (`base-uri`, `form-action`).

Lo que no hace, dicho con su nombre:
- Va como <meta>, porque GitHub Pages no deja poner encabezados: por eso no
  puede llevar `frame-ancestors` (quién nos mete en un marco) ni reportes.
- Todavía permite código en línea ('unsafe-inline'): la portada tiene botones
  con onclick y varias páginas traen su script en línea. Quitarlo es la
  siguiente entrega (pasarlos a archivos o a huellas sha256).

Toda página generada la lleva (apartados.py, auditorias.py, acceso.py) y la
portada, a mano. Uso:
    python3 herramientas/seguridad.py          # revisa que todas la traigan igual
    python3 herramientas/seguridad.py --meta   # imprime la etiqueta

**Un servicio externo nuevo (una API, un CDN, un antispam) necesita aquí su
anfitrión, en la directiva que usa**, o el navegador lo bloquea en silencio.
"""
import glob
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# La base de datos y sus funciones (acceso.py y apartados.py dicen la misma).
SUPABASE = 'https://nuqiyzcilbrrlezmesnf.supabase.co'

# Cada directiva con el porqué de cada anfitrión.
DIRECTIVAS = [
    ('default-src', ["'self'"]),
    # Leaflet en la portada (cdnjs) y el antispam Turnstile de los formularios.
    ('script-src', ["'self'", "'unsafe-inline'", 'https://cdnjs.cloudflare.com',
                    'https://challenges.cloudflare.com']),
    ('style-src', ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com',
                   'https://cdnjs.cloudflare.com']),
    ('font-src', ["'self'", 'data:', 'https://fonts.gstatic.com']),
    # Fotos propias, los mosaicos del mapa (cartocdn) y las de portales oficiales.
    ('img-src', ["'self'", 'data:', 'blob:', 'https:']),
    # A dónde puede hablar la página: solo la base de datos, los dos lectores de
    # notas de «Contrasta una nota» y la Mesa de redacción, y el antispam.
    ('connect-src', ["'self'", SUPABASE, 'https://r.jina.ai',
                     'https://api.allorigins.win', 'https://challenges.cloudflare.com']),
    ('frame-src', ["'self'", 'https://challenges.cloudflare.com']),
    ('media-src', ["'self'", 'data:', 'blob:']),
    ('worker-src', ["'self'", 'blob:']),
    ('object-src', ["'none'"]),
    ('base-uri', ["'self'"]),
    ('form-action', ["'self'"]),
    ('upgrade-insecure-requests', []),
]


def politica():
    return '; '.join((k + ' ' + ' '.join(v)).strip() for k, v in DIRECTIVAS)


def meta():
    return '<meta http-equiv="Content-Security-Policy" content="%s">' % politica()


META_RE = re.compile(r'<meta http-equiv="Content-Security-Policy" content="[^"]*">')


def paginas():
    """Las páginas de la plataforma: las de la raíz. Las copias de documentos
    oficiales (investigaciones/) y el manual de marca (brand/) no son páginas."""
    return sorted(glob.glob(os.path.join(RAIZ, '*.html')))


def revisar():
    errores = []
    esperado = meta()
    # La misma base en los tres lugares que la nombran.
    for f, pat in (('acceso.py', r"SUPABASE_URL = '([^']+)'"), ('apartados.py', r"FUNCIONES = '([^']+)/functions/v1'")):
        t = open(os.path.join(RAIZ, 'herramientas', f), encoding='utf-8').read()
        m = re.search(pat, t)
        if not m or m.group(1) != SUPABASE:
            errores.append('%s nombra otra base de datos que seguridad.SUPABASE: agrega su anfitrión a connect-src' % f)
    for p in paginas():
        t = open(p, encoding='utf-8', errors='replace').read()
        hallados = META_RE.findall(t)
        nombre = os.path.basename(p)
        if not hallados:
            errores.append('%s no trae la política de seguridad (CSP)' % nombre)
        elif len(hallados) > 1:
            errores.append('%s trae la política dos veces' % nombre)
        elif hallados[0] != esperado:
            errores.append('%s trae una política vieja: vuelve a generarla' % nombre)
        else:
            cab = t.split('</head>', 1)[0]
            if cab.find(hallados[0]) > cab.find('<script') >= 0:
                errores.append('%s carga un script antes de la política' % nombre)
    return errores


if __name__ == '__main__':
    if '--meta' in sys.argv:
        print(meta())
        sys.exit(0)
    e = revisar()
    for x in e[:40]:
        print('✗', x)
    if e:
        print('%d problemas de la política de seguridad' % len(e))
        sys.exit(1)
    print('✓ Política de seguridad (CSP) igual en las %d páginas' % len(paginas()))
