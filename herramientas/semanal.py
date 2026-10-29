#!/usr/bin/env python3
"""Revisión semanal de la plataforma (Bloque 3 del plan, 27-10-2026).

Dos preguntas, cada lunes (.github/workflows/semanal.yml) o cuando quieras:

1. ¿Se cayó algún enlace a una fuente? Revisa cada enlace externo de las
   páginas publicadas (sin las fuentes tipográficas ni el propio sitio).
   Los portales de gobierno fallan seguido por unas horas: un enlace roto
   aquí es un aviso para revisarlo a mano, no una prueba de que el
   documento desapareció. Si de verdad ya no está, se busca su nueva
   dirección o se recurre a su copia en la bóveda (docs/boveda/).
2. ¿Ya salió un dato que esperamos? Los «vigías» de abajo: documentos con
   fecha de entrega por ley que la plataforma debe integrar en cuanto
   aparezcan. Al integrarlo, se cambia el vigía por el del periodo siguiente.

No cambia nada de la plataforma: escribe un reporte (docs/SEMANAL.md, y en
GitHub, el resumen de la ejecución). Termina con error solo si un vigía ya
salió, para que el aviso no pase de largo.

    python3 herramientas/semanal.py
    python3 herramientas/semanal.py --sin-enlaces     # solo los vigías
"""
import argparse
import concurrent.futures
import glob
import os
import re
import ssl
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUERA = ('fonts.googleapis.com', 'fonts.gstatic.com', 'uzoraproductos-arch.github.io', 'auditavision.com.mx')

# Documentos que esperamos: (qué es, dirección donde aparecerá, qué hacer).
# Ojo: la ASF ya tiene en esa dirección un PDF de una página que dice
# «Próximamente se publicará el informe…» (155 KB, revisado el 27-10-2026):
# que el archivo exista no basta. Solo cuenta como publicado si pesa más de
# MIN_BYTES; el informe de marzo de 2026 trae 648 páginas.
MIN_BYTES = 1000000
VIGIAS = [
    ('Informe semestral de la ASF con corte al 30 de septiembre de 2026 (art. 38 de la LFRCF, a más tardar el 1 de noviembre de 2026)',
     'https://www.asf.gob.mx/uploads/56_Informes_especiales_de_auditoria/IS_30_09_2026.pdf',
     'Cambiar DOC y ANT de herramientas/informe_semestral.py con sus cifras nuevas, registrarlo en la bóveda y cambiar este vigía por el del corte al 31 de marzo de 2027.'),
]


def pide(url, metodo='HEAD', tam=False):
    req = urllib.request.Request(url, method=metodo, headers={'User-Agent': 'Mozilla/5.0 (revision semanal de Auditavision)'})
    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as r:
            return (r.status, int(r.headers.get('Content-Length') or 0)) if tam else r.status
    except urllib.error.HTTPError as e:
        # Hay portales que no contestan HEAD: se intenta una vez con GET.
        if metodo == 'HEAD' and e.code in (403, 405, 501):
            return pide(url, 'GET', tam)
        return (e.code, 0) if tam else e.code
    except Exception as e:  # red, certificado, tiempo
        return (type(e).__name__, 0) if tam else type(e).__name__


def enlaces():
    usos = {}
    for f in sorted(glob.glob(os.path.join(RAIZ, '*.html'))):
        for u in re.findall(r'href="(https?://[^"#]+)', open(f, encoding='utf-8', errors='ignore').read()):
            u = u.replace('&amp;', '&')
            if not any(d in u for d in FUERA):
                usos.setdefault(u, set()).add(os.path.basename(f))
    return usos


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--sin-enlaces', action='store_true', help='solo revisa los vigías')
    a = ap.parse_args()
    out = ['# Revisión semanal', '', 'La escribe `herramientas/semanal.py`. No cambia nada de la plataforma.', '', '## Vigías: datos que esperamos', '']
    salieron = 0
    for que, url, hacer in VIGIAS:
        st, n = pide(url, tam=True)
        ya = st == 200 and n > MIN_BYTES
        aviso = st == 200 and not ya
        salieron += ya
        out.append('- %s **%s**: %s. %s' % ('🆕' if ya else '⏳', 'YA SALIÓ' if ya else 'todavía no' + (' (solo está el aviso de «próximamente», %d KB)' % (n // 1000) if aviso else ''),
                                           que, ('Qué hacer: ' + hacer) if ya else '[Dónde aparecerá](%s).' % url))
    if not a.sin_enlaces:
        usos = enlaces()
        with concurrent.futures.ThreadPoolExecutor(12) as ex:
            estado = dict(zip(usos, ex.map(pide, usos)))
        rotos = sorted(u for u, s in estado.items() if not (isinstance(s, int) and s < 400))
        out += ['', '## Enlaces a fuentes', '', '%d enlaces externos revisados; %d no abrieron.' % (len(usos), len(rotos)), '']
        out += ['- `%s` → %s (en %s)' % (estado[u], u, ', '.join(sorted(usos[u])[:4]) + ('…' if len(usos[u]) > 4 else '')) for u in rotos]
        print('semanal: %d enlaces externos, %d no abrieron' % (len(usos), len(rotos)))
    texto = '\n'.join(out) + '\n'
    open(os.path.join(RAIZ, 'docs', 'SEMANAL.md'), 'w', encoding='utf-8').write(texto)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8').write(texto)
    print('semanal: %d de %d vigías ya salieron' % (salieron, len(VIGIAS)))
    return 1 if salieron else 0


if __name__ == '__main__':
    raise SystemExit(main())
