#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Escribe sitemap.xml (propuesta de Astra, punto 8; entrega 5,
10-10-2026): cada pagina de la plataforma con su direccion estable, para
que los buscadores la encuentren sin abrir una pestana interna.

Entran todas las paginas .html de la raiz menos la Enciclopedia (congelada,
proyecto aparte) y las que solo redirigen. La fecha es la del sello.
No escribe robots.txt: el sitio vive en /a/ y los buscadores solo leen
el robots.txt de la raiz del dominio. El mapa se registra a mano en Google
Search Console (o se anuncia desde un robots.txt en la raiz, si algun dia
el sitio tiene dominio propio).

Lo llama apartados.generar(), asi que sello.py lo regenera.
"""
import os
import re

from apartados import RAIZ, SITIO

EXCLUIR = {'enciclopedia.html'}


def redirige(texto):
    return 'http-equiv="refresh"' in texto or ("location.replace('" in texto and len(texto) < 4000)


def generar(sello):
    fecha = '%s-%s-%s' % (sello[:4], sello[4:6], sello[6:8])
    paginas = []
    for f in sorted(os.listdir(RAIZ)):
        if not f.endswith('.html') or f in EXCLUIR:
            continue
        t = open(os.path.join(RAIZ, f), encoding='utf-8', errors='replace').read()
        if redirige(t) or re.search(r'<meta name="robots" content="[^"]*noindex', t):
            continue
        paginas.append('' if f == 'index.html' else f)
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += ['  <url><loc>%s%s</loc><lastmod>%s</lastmod></url>' % (SITIO, p, fecha) for p in paginas]
    xml.append('</urlset>')
    open(os.path.join(RAIZ, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write('\n'.join(xml) + '\n')
    print('sitemap: %d páginas en sitemap.xml' % len(paginas))
    return 0
