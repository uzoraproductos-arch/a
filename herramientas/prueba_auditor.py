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
- «modo»: el modo en que se pregunta (si falta, Ciudadano, con el que abre).

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
# Con «modo» (29-10-2026), la pregunta se hace en ese modo y el texto suma
# lo que el modo agrega a la respuesta (la nota del Periodista y, desde el
# 04-11-2026, la capa del Inspector, del Ciudadano y del Ambientalista).
PREGUNTA_JS = '''async (arg) => {
  const [q, modo] = Array.isArray(arg) ? arg : [arg, ''];
  const app = document.getElementById('paApp');
  if (app) app.setAttribute('data-modo', modo || 'ciudadano');
  let r = window.AuditorBot.respuesta(q, []);
  if (r && r.espera) r = await r.espera;
  const n = modo && window.AuditorBot.capaModo ? window.AuditorBot.capaModo(q, r, modo)
    : modo === 'periodista' && window.AuditorBot.periodista ? window.AuditorBot.periodista(q, r) : null;
  const t = (((r && r.html) || '') + ' ' + ((n && n.html) || '')).replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').trim();
  return { ir: (r && r.ir && r.ir[0]) || null, sin: !!(r && r.sin), texto: t };
}'''


class _Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def servidor():
    srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(_Silencioso, directory=str(RAIZ)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def ligas_abre():
    """[(pregunta, página, dónde)] de cada liga al chat con ?abre= del sitio, sin repetir la página."""
    import html as _h
    import re
    from urllib.parse import parse_qs, urlsplit
    vistas, out = set(), []
    for ruta in sorted(RAIZ.glob('*.html')):
        # Las del Inspector de Servicios (21-11-2026) abren igual: mismo motor, misma base.
        # Y las de su respuesta completa (servicios-respuesta.html, 21-11-2026).
        for href in re.findall(r'href="((?:%s|servicios-inspector\.html|servicios-respuesta\.html)\?[^"]*abre=[^"]*)"' % re.escape(PAGINA), ruta.read_text(encoding='utf-8')):
            ps = parse_qs(urlsplit(_h.unescape(href)).query)
            liga = ps.get('abre', [''])[0]
            if liga and liga not in vistas:
                vistas.add(liga)
                out.append((ps.get('q', [''])[0], liga, ruta.name))
    return out


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
        clave = (p['q'], p.get('modo', ''))
        if clave in vistas:
            sys.exit('Pregunta repetida en el banco: %s' % p['q'])
        vistas.add(clave)
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
        # Todo pasa por el Auditor (19-11-2026): cada liga ?abre= del sitio debe abrir su página en el chat.
        for q, liga, de in ligas_abre():
            r = pag.evaluate('''([q, l]) => { const r = window.AuditorBot.abre(q, l); return r ? { ir: (r.ir && r.ir[0]) || null } : null; }''', [q, liga])
            if not (RAIZ / liga.split('#')[0].split('?')[0]).exists():
                fallas.append(('abre=%s (en %s)' % (liga, de), ['la página no existe']))
            elif not r or r['ir'] != liga:
                fallas.append(('abre=%s (en %s)' % (liga, de), ['el chat no la abre' if not r else '«Saber más» lleva a %s' % r['ir']]))
        for p in banco:
            r = pag.evaluate(PREGUNTA_JS, [p['q'], p.get('modo', '')])
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
