#!/usr/bin/env python3
"""Todo pasa por el Auditor: cuenta las ligas directas entre pestañas.

Decisión del autor, 19-11-2026: «el chat se alimenta y vincula de todas las
pestañas y tarjetas y subtarjetas dentro de ellas, pero entre pestañas no se
vinculan: todo es a través del Auditor», y «las aplicaciones del chat se
convierten en servicios».

La plataforma es una estrella: el Auditor (el chat) es el centro y cada
pestaña (Planisferio, Comunidad con la Enciclopedia, Noticiero y Servicios) es
una punta. Dentro de una pestaña las páginas se ligan entre sí; para ir a otra
pestaña, la liga pasa por el chat (`herramienta-inspector-pregunta.html?q=…&abre=…`),
que contesta en corto, ofrece el dictamen, lleva a «Saber más» y ofrece el
servicio que toca.

Este script lee las páginas generadas y cuenta, por par de pestañas, las ligas
directas que todavía saltan de una a otra (sin contar la cabecera, el menú, las
migas ni el pie). Se muda por entregas, así que funciona como trinquete:

- Compara contra `docs/vinculos-auditor.json`. **Si un par sube, la revisión se
  detiene**: una liga nueva entre pestañas va por el Auditor.
- **Servicios ya está mudado** (19-11-2026): ninguna liga suya sale directo a
  otra pestaña.
- Cuando un par baja, `--fijar` guarda la cuenta nueva.

Uso: python3 herramientas/vinculos_auditor.py [--fijar] [--ver ORIGEN]
"""
import argparse
import glob
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(RAIZ, 'docs', 'vinculos-auditor.json')
PESTANAS = ('Auditor', 'Planisferio', 'Comunidad', 'Noticiero', 'Servicios')
# Las pestañas ya mudadas: no pueden tener ni una liga directa a otra.
MUDADAS = ('Servicios',)

_CUR = re.compile(r'<a [^>]*aria-current="page"[^>]*>([^<]*)</a>')
_FUERA = [re.compile(p, re.S) for p in (
    r'<header\b.*?</header>', r'<footer\b.*?</footer>', r'<nav class="site-top-nav".*?</nav>',
    r'<nav class="apartado-migas".*?</nav>',
    # El cajón «Cuéntanos lo que viste» es de la cabecera: va en todas las páginas.
    r'<aside class="pt-cajon".*?</aside>', r'<script\b.*?</script>', r'<noscript\b.*?</noscript>')]
_A = re.compile(r'<a\b[^>]*\bhref="([^"#?:]+\.html)[^"]*"')


def pestana(texto):
    for m in _CUR.finditer(texto):
        t = m.group(1).strip()
        if t in PESTANAS:
            return t
    return None


def mapa():
    """{archivo: pestaña} de todas las páginas del sitio."""
    out = {}
    for ruta in glob.glob(os.path.join(RAIZ, '*.html')):
        t = pestana(open(ruta, encoding='utf-8').read())
        if t:
            out[os.path.basename(ruta)] = t
    return out


def saltos(pest):
    """[(origen, destino, archivo, liga)] de las ligas directas entre pestañas."""
    out = []
    for arch, t in sorted(pest.items()):
        if t == 'Auditor':
            continue  # el centro: de ahí se va a todas partes
        s = open(os.path.join(RAIZ, arch), encoding='utf-8').read()
        for r in _FUERA:
            s = r.sub('', s)
        for liga in _A.findall(s):
            d = pest.get(liga)
            if d and d != t and d != 'Auditor':
                out.append((t, d, arch, liga))
    return out


def cuenta(lista):
    c = {}
    for o, d, _a, _l in lista:
        k = '%s → %s' % (o, d)
        c[k] = c.get(k, 0) + 1
    return dict(sorted(c.items()))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--fijar', action='store_true', help='guarda la cuenta de hoy como base (solo si bajó)')
    ap.add_argument('--ver', metavar='PESTANA', help='lista las ligas que salen de esa pestaña')
    a = ap.parse_args()
    pest = mapa()
    lista = saltos(pest)
    hoy = cuenta(lista)
    if a.ver:
        for o, d, arch, liga in lista:
            if o == a.ver:
                print('%s → %s  %s → %s' % (o, d, arch, liga))
    antes = json.load(open(BASE, encoding='utf-8'))['pares'] if os.path.exists(BASE) else {}
    mal = []
    # La regla por nombre (la que usa servicios_fichas para mudar las ligas) debe dar
    # la misma pestaña que marca cada página.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import servicios_fichas
    for arch, t in sorted(pest.items()):
        if servicios_fichas.pestana_de(arch) != t:
            mal.append('%s marca la pestaña %s, pero servicios_fichas.pestana_de() dice %s: agrégala a EXCEPCIONES'
                       % (arch, t, servicios_fichas.pestana_de(arch)))
    for k, n in hoy.items():
        if k.split(' → ')[0] in MUDADAS:
            mal.append('%s: %d ligas directas; esa pestaña ya pasa todo por el Auditor (usa servicios_fichas.por_auditor)' % (k, n))
        elif antes and n > antes.get(k, 0):
            mal.append('%s: %d ligas directas, antes %d. Una liga nueva entre pestañas va por el Auditor.' % (k, n, antes.get(k, 0)))
    if a.fijar:
        if mal:
            sys.exit('No se fija: ' + '; '.join(mal))
        with open(BASE, 'w', encoding='utf-8') as fh:
            json.dump({'nota': 'Ligas directas entre pestañas que faltan por mudar al Auditor (herramientas/vinculos_auditor.py). '
                               'Solo pueden bajar.', 'pares': hoy}, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
    for m in mal:
        print('✗ ' + m)
    print('vínculos por el Auditor: %d páginas en %d pestañas; %d ligas directas entre pestañas por mudar%s'
          % (len(pest), len(set(pest.values())), len(lista), '' if not mal else '; %d problemas' % len(mal)))
    sys.exit(1 if mal else 0)


if __name__ == '__main__':
    main()
