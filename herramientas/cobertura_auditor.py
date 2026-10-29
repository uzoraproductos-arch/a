#!/usr/bin/env python3
"""La Enciclopedia, dentro del Auditor (pedido del autor, 29-10-2026: «que
el contenido que se encuentra en la enciclopedia quede integrado a nuestro
auditor en sus correspondientes modos para que todo ya quede vinculado»).

La Enciclopedia es la base de datos física del Auditor. Esta herramienta
toma cada página de la Enciclopedia (las que dicen «Enciclopedia» en sus
migas y las de modos.ENCICLOPEDIA_EXTRA; la pestaña misma es el
índice y no cuenta), hace en un navegador de verdad la
pregunta de su botón «Pregúntale al Auditor · Modo X», en ese modo, y revisa
tres cosas:

- que la página esté en la base del chat con su modo;
- que la respuesta lleve a ella: en «Saber más» o en «📚 En la Enciclopedia»;
- que la página no arroje errores.

Falla si una sola página queda fuera. Con --informe escribe
docs/COBERTURA-AUDITOR.md: cada página, su modo y adónde lleva su pregunta.

Uso:
    python3 herramientas/cobertura_auditor.py
    python3 herramientas/cobertura_auditor.py --ver
    python3 herramientas/cobertura_auditor.py --informe

Requisitos: Playwright con Chromium (GUARDIA_CHROMIUM=/ruta/al/chrome).
"""

import argparse
import html
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modos  # noqa: E402
from prueba_auditor import PAGINA, servidor  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
INFORME = RAIZ / 'docs' / 'COBERTURA-AUDITOR.md'

PREGUNTA_JS = '''async ([q, modo]) => {
  document.getElementById('paApp').setAttribute('data-modo', modo);
  let r = window.AuditorBot.respuesta(q, []);
  if (r && r.espera) r = await r.espera;
  const enc = window.AuditorBot.enciclopedia(q, r).map(f => f.ir[0].split('#')[0].split('?')[0]);
  return { ir: (r && r.ir && r.ir[0]) || (r && r.ficha && r.ficha.ir && r.ficha.ir[0]) || null, sin: !!(r && r.sin), enc: enc };
}'''


def paginas():
    """(archivo, migas, modo, pregunta) de cada página de la Enciclopedia, leídos de su botón."""
    out = []
    for p in sorted(RAIZ.glob('*.html')):
        s = p.read_text(encoding='utf-8')
        if 'http-equiv="refresh"' in s or p.name == 'enciclopedia-auditavision.html':
            continue
        m = re.search(r'class="apartado-auditor" href="([^"]+)"', s)
        mg = re.search(r'<nav class="apartado-migas".*?</nav>', s, re.S)
        migas = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', mg.group(0))).strip() if mg else ''
        en = 'Enciclopedia' in migas.split(' › ')[1:2] or p.name in modos.ENCICLOPEDIA_EXTRA
        if not en:
            continue
        if not m:
            out.append((p.name, migas, None, None))
            continue
        qs = parse_qs(urlparse(html.unescape(m.group(1))).query)
        out.append((p.name, migas, qs['modo'][0], qs['q'][0]))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--ver', action='store_true', help='imprime adónde lleva cada página')
    ap.add_argument('--informe', action='store_true', help='escribe docs/COBERTURA-AUDITOR.md')
    a = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit('Falta Playwright: pip install playwright && python3 -m playwright install chromium')

    lista = paginas()
    srv = servidor()
    filas, fallas, errores = [], [], []
    with sync_playwright() as pw:
        exe = os.environ.get('GUARDIA_CHROMIUM')
        nav = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
        pag = nav.new_page()
        pag.on('pageerror', lambda e: errores.append(str(e)))
        pag.goto('http://127.0.0.1:%d/%s' % (srv.server_address[1], PAGINA))
        pag.wait_for_function('() => !!(window.AuditorBot && window.AuditorBot.enciclopedia)')
        base = pag.evaluate('() => Object.fromEntries(AUDITOR_BASE.fichas.filter(f => f.t === "pagina" && f.e).map(f => [f.ir[0], f.m]))')
        for archivo, migas, modo, q in lista:
            if not modo:
                fallas.append((archivo, ['no trae su botón «Pregúntale al Auditor»']))
                continue
            mal = []
            if base.get(archivo) != modo:
                mal.append('en la base del chat está como %s y su botón dice %s' % (base.get(archivo), modo))
            r = pag.evaluate(PREGUNTA_JS, [q, modo])
            ir = (r['ir'] or '').split('#')[0].split('?')[0]
            donde = 'Saber más' if ir == archivo else ('En la Enciclopedia' if archivo in r['enc'] else None)
            if not donde:
                mal.append('«%s» lleva a %s y no la ofrece' % (q, 'nada' if r['sin'] else r['ir']))
            filas.append((archivo, migas, modo, q, donde))
            if a.ver:
                print('%s [%s] %s → %s' % ('✗' if mal else '✓', modo, q, donde or r['ir']))
            if mal:
                fallas.append((archivo, mal))
        nav.close()
    srv.shutdown()

    if a.informe:
        escribe_informe(filas)
    for e in errores:
        print('ERROR en la página: %s' % e)
    for p, mal in fallas:
        print('✗ %s\n    %s' % (p, '\n    '.join(mal)))
    cuenta = Counter(f[2] for f in filas)
    print('cobertura del Auditor: %d páginas de la Enciclopedia, %d vinculadas, %d fuera (%s)' % (
        len(lista), len(lista) - len(fallas), len(fallas),
        ', '.join('%s %d' % (modos.MODOS_NOMBRE[m], cuenta[m]) for m in modos.MODOS_NOMBRE)))
    sys.exit(1 if fallas or errores else 0)


def escribe_informe(filas):
    por = defaultdict(list)
    for f in filas:
        por[f[2]].append(f)
    t = ['# La Enciclopedia dentro del Auditor', '',
         'Lo escribe `python3 herramientas/cobertura_auditor.py --informe`: no se edita a mano.',
         'Cada página de la Enciclopedia, el modo del Auditor desde el que se pregunta por ella',
         '(`herramientas/modos.py`) y adónde lleva esa pregunta en el chat.', '']
    t.append('| Modo | Páginas | En «Saber más» | En «📚 En la Enciclopedia» |')
    t.append('|---|---|---|---|')
    for m in modos.MODOS_NOMBRE:
        fs = por.get(m, [])
        t.append('| %s %s | %d | %d | %d |' % (modos.MODOS_ICONO[m], modos.MODOS_NOMBRE[m], len(fs),
                                            sum(f[4] == 'Saber más' for f in fs), sum(f[4] == 'En la Enciclopedia' for f in fs)))
    for m in modos.MODOS_NOMBRE:
        t += ['', '## %s Modo %s' % (modos.MODOS_ICONO[m], modos.MODOS_NOMBRE[m]), '',
              '| Página | Dónde vive | Pregunta | La encuentra en |', '|---|---|---|---|']
        for archivo, migas, _, q, donde in sorted(por.get(m, []), key=lambda f: f[1]):
            t.append('| [%s](../%s) | %s | %s | %s |' % (q, archivo, ' › '.join(migas.split(' › ')[1:-1]) or '—', q, donde or '✗ fuera'))
    INFORME.write_text('\n'.join(t) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
