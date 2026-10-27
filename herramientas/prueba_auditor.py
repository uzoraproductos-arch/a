#!/usr/bin/env python3
"""Preguntas de prueba del Auditor (Bloque 3 del plan, 27-10-2026).

El Auditor Virtual tiene que encontrar lo que la plataforma sabe (AGENTS.md,
§5 ter). Esta herramienta le hace las preguntas de
herramientas/preguntas_auditor.json, en un navegador de verdad, y revisa que
cada una lleve a donde debe:

- «ir»: la página (y el ancla) de «Saber más», tal cual.
- «dice»: frases que la respuesta tiene que traer (por ejemplo, el veredicto
  «Coincide con el documento»).
- «no_dice»: frases que no debe traer.
- «sin»: true si lo correcto es decir que no lo sabe.

Falla si una sola pregunta cambia de destino o si la página arroja un error.
Cuando un cambio mueve una respuesta a propósito (una página nueva, un ancla
que cambió), se corrige su renglón en el JSON en el mismo commit.

Uso:
    python3 herramientas/prueba_auditor.py
    python3 herramientas/prueba_auditor.py --ver        # imprime adónde lleva cada una
    python3 herramientas/prueba_auditor.py --solo "Tren Maya"

Requisitos (solo para esta herramienta): Playwright para Python con Chromium.
Si ya hay un Chromium instalado, GUARDIA_CHROMIUM=/ruta/al/chrome lo usa.
"""

import argparse
import functools
import http.server
import json
import os
import socketserver
import sys
import threading
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PREGUNTAS = RAIZ / 'herramientas' / 'preguntas_auditor.json'
PAGINA = 'herramienta-inspector-pregunta.html'

# Lo mismo que hace el chat al contestar: respuesta(), y si espera una
# descarga (la lista del SAT, ComprasMX), su promesa.
PREGUNTA_JS = '''async (q) => {
  let r = window.AuditorBot.respuesta(q, []);
  if (r && r.espera) r = await r.espera;
  const t = ((r && r.html) || '').replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').trim();
  return { ir: (r && r.ir && r.ir[0]) || null, sin: !!(r && r.sin), texto: t };
}'''


class _Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def servidor():
    srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(_Silencioso, directory=str(RAIZ)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def revisa(p, r):
    """Lo que no cuadra entre lo esperado (p) y la respuesta (r)."""
    mal = []
    if p.get('sin'):
        if not r['sin']:
            mal.append('debía decir que no lo sabe y contestó con %s' % r['ir'])
        return mal
    if r['sin']:
        mal.append('no supo contestar')
    if 'ir' in p and r['ir'] != p['ir']:
        mal.append('«Saber más» lleva a %s y debía llevar a %s' % (r['ir'], p['ir']))
    for f in p.get('dice', []):
        if f not in r['texto']:
            mal.append('no dice «%s»' % f)
    for f in p.get('no_dice', []):
        if f in r['texto']:
            mal.append('dice «%s» y no debía' % f)
    return mal


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--ver', action='store_true', help='imprime adónde lleva cada pregunta')
    ap.add_argument('--solo', help='corre solo las preguntas que contienen este texto')
    a = ap.parse_args()

    banco = json.loads(PREGUNTAS.read_text(encoding='utf-8'))['preguntas']
    if a.solo:
        banco = [p for p in banco if a.solo.lower() in p['q'].lower()]
    vistas = set()
    for p in banco:
        if p['q'] in vistas:
            sys.exit('Pregunta repetida en el banco: %s' % p['q'])
        vistas.add(p['q'])
        if not p.get('sin') and 'ir' not in p and not p.get('dice'):
            sys.exit('La pregunta «%s» no dice qué espera (ir, dice o sin).' % p['q'])

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit('Falta Playwright: pip install playwright && python3 -m playwright install chromium')

    srv = servidor()
    fallas, errores = [], []
    with sync_playwright() as pw:
        exe = os.environ.get('GUARDIA_CHROMIUM')
        nav = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
        pag = nav.new_page()
        pag.on('pageerror', lambda e: errores.append(str(e)))
        pag.goto('http://127.0.0.1:%d/%s' % (srv.server_address[1], PAGINA))
        pag.wait_for_function('() => !!(window.AuditorBot && window.AuditorBot.respuesta)')
        for p in banco:
            r = pag.evaluate(PREGUNTA_JS, p['q'])
            mal = revisa(p, r)
            if a.ver:
                print('%s %s → %s' % ('✗' if mal else '✓', p['q'], 'no lo sabe' if r['sin'] else r['ir']))
            if mal:
                fallas.append((p['q'], mal))
        nav.close()
    srv.shutdown()

    for e in errores:
        print('ERROR en la página: %s' % e)
    for q, mal in fallas:
        print('✗ %s\n    %s' % (q, '\n    '.join(mal)))
    print('prueba del Auditor: %d preguntas, %d bien, %d mal, %d errores de página'
          % (len(banco), len(banco) - len(fallas), len(fallas), len(errores)))
    sys.exit(1 if fallas or errores else 0)


if __name__ == '__main__':
    main()
