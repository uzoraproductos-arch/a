#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inventario de la plataforma publicada (entrega 1 de la propuesta de Astra).

Recorre cada pagina .html de la raiz (menos la Enciclopedia, que esta
congelada y no se abre) y anota: titulo, quien la genera, a que menu
pertenece, cuantos enlaces internos tiene, cuales apuntan a un archivo que
no existe, cuantos modulos del motor abre y cuantos chips de estado lleva.
Escribe docs/INVENTARIO.md. No toca ningun archivo de la plataforma.

    python3 herramientas/inventario.py
"""
import os
import re
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUIR = {'enciclopedia.html'}


def leer(nombre):
    return open(os.path.join(RAIZ, nombre), encoding='utf-8', errors='replace').read()


def generador(texto):
    m = re.search(r'generada por herramientas/(\w+\.py)', texto)
    return m.group(1) if m else 'a mano'


def destino_ir(href):
    m = re.search(r'[?&]ir=([\w-]+)', href)
    return m.group(1) if m else None


def main():
    paginas = sorted(f for f in os.listdir(RAIZ) if f.endswith('.html') and f not in EXCLUIR)
    existentes = set(os.listdir(RAIZ))
    filas, rotos, irs, redirige = [], [], Counter(), []
    for p in paginas:
        t = leer(p)
        tit = re.search(r'<title>(.*?)</title>', t, re.S)
        tit = re.sub(r'\s+', ' ', tit.group(1)).strip() if tit else '(sin título)'
        if 'http-equiv="refresh"' in t or "location.replace('" in t and len(t) < 4000:
            m = re.search(r"url=([^\"']+)|location\.replace\('([^']+)'", t)
            redirige.append((p, (m.group(1) or m.group(2)) if m else '?'))
        hrefs = re.findall(r'(?:href|data-modulo)="([^"]+)"', t)
        internos = [h for h in hrefs if not re.match(r'(https?:|mailto:|tel:|#|javascript:|data:)', h)]
        for h in internos:
            archivo = h.split('#')[0].split('?')[0].replace('&amp;', '&')
            if archivo and not archivo.startswith('assets/') and archivo not in existentes:
                rotos.append((p, h))
            d = destino_ir(h)
            if d:
                irs[d] += 1
        chips = Counter(re.findall(r'est-chip est-(oficial|derivado|pendiente)', t))
        filas.append((p, tit, generador(t), len(internos), len(re.findall(r'data-modulo=', t)),
                      chips['oficial'], chips['derivado'], chips['pendiente']))

    out = ['# Inventario de Auditavisión', '',
           'Generado por `herramientas/inventario.py`. No se edita a mano: se vuelve a correr.',
           'La Enciclopedia queda fuera porque está congelada.', '',
           '## Resumen', '',
           '| Concepto | Cantidad |', '|---|---|',
           '| Páginas revisadas | %d |' % len(paginas),
           '| Páginas que solo redirigen | %d |' % len(redirige),
           '| Enlaces internos a archivos que no existen | %d |' % len(rotos),
           '| Módulos del motor que se abren desde páginas (`?ir=`) | %d destinos |' % len(irs), '',
           '## Páginas', '',
           '| Página | Título | Generador | Enlaces internos | Módulos embebidos | oficial | derivado | pendiente |',
           '|---|---|---|---:|---:|---:|---:|---:|']
    for f in filas:
        out.append('| `%s` | %s | %s | %d | %d | %d | %d | %d |' % (f[0], f[1].replace('|', '/'), *f[2:]))
    out += ['', 'Los chips que pinta el motor al abrir un módulo no se cuentan aquí: solo los escritos en el HTML.', '',
            '## Redirecciones', '', '| Página | Lleva a |', '|---|---|']
    out += ['| `%s` | `%s` |' % r for r in redirige] or ['| — | — |']
    out += ['', '## Enlaces rotos', '']
    out += ['- `%s` → `%s`' % r for r in rotos] or ['Ninguno.']
    out += ['', '## Módulos del motor que todavía viven en la portada', '',
            'Se abren con `index.html?ir=…`. Cada uno es candidato a mudarse a su propia página (AGENTS.md §5 bis).', '',
            '| Destino | Veces enlazado |', '|---|---:|']
    out += ['| `%s` | %d |' % (k, v) for k, v in sorted(irs.items(), key=lambda x: -x[1])]
    # Toda etiqueta que lleva a una ficha del Registro de pendientes debe
    # encontrarla (10-10-2026).
    fichas = set(re.findall(r'<article class="pe-item[^"]*" id="([^"]+)"', leer('pendientes.html'))) if 'pendientes.html' in existentes else set()
    for p in paginas:
        for ancla in set(re.findall(r'data-pend="([^"]+)"', leer(p))):
            if ancla not in fichas:
                rotos.append((p, 'pendientes.html#' + ancla))
    out += ['', '## Registro de pendientes', '', '%d fichas, cada una con su porqué, su responsable y su enlace oficial.' % len(fichas)]
    os.makedirs(os.path.join(RAIZ, 'docs'), exist_ok=True)
    open(os.path.join(RAIZ, 'docs', 'INVENTARIO.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('inventario: %d páginas, %d enlaces rotos, %d redirecciones' % (len(paginas), len(rotos), len(redirige)))
    return 1 if rotos else 0


if __name__ == '__main__':
    raise SystemExit(main())
