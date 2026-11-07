#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La dimensión penal del Planisferio (pedido del autor, 05-11-2026: «para
ponerlo en un mapa… una dimensión de penal»).

Lo que el INEGI mide de los delitos que sufre la gente en cada estado, con la
ENVIPE 2026 (datos de 2025): la tasa de fraude por cada 100 mil habitantes y
la cifra oculta (los delitos que no se denunciaron o no se investigaron). Los
números salen de las fichas estatales del INEGI, ancladas con su huella en
docs/seguridad/envipe-2026-entidades.json por anclar_envipe_estados.py. Aquí
se vuelven a revisar.

Reglas:
- **Más fraude registrado no es «peor gobierno»**: la ENVIPE es una encuesta
  en los hogares, con su margen de error, y el fraude lo cometen particulares.
- **La cifra oculta no es la eficacia de la fiscalía**: junta lo que la gente
  no denunció y lo que la autoridad no investigó.
- Cinco fichas estatales dan la tasa de fraude solo en una gráfica (imagen):
  van en gris como pendiente, con su ficha en el Registro, nunca leídas a ojo.
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(RAIZ, 'docs', 'seguridad', 'envipe-2026-entidades.json')
PEND = 'penal-fraude-graficas'


def doc():
    with open(DOC, encoding='utf-8') as f:
        d = json.load(f)
    if len(d['estados']) != 32:
        raise SystemExit('dimension_penal: la ENVIPE no trae a las 32 entidades')
    for a, x in d['estados'].items():
        if not x.get('sha') or not x.get('url') or x.get('oculta') is None:
            raise SystemExit('dimension_penal: %s no trae su cifra oculta, su huella o su enlace' % a)
        if not (50 <= x['oculta'] <= 100) or (x['fraude'] is not None and not (1000 <= x['fraude'] <= 40000)):
            raise SystemExit('dimension_penal: %s trae una cifra fuera de rango; revisa el anclaje' % a)
    return d


def estados(base):
    d = doc()
    out = {}
    for e in base['estados']:
        x = d['estados'].get(e['abbr'])
        if x is None:
            raise SystemExit('dimension_penal: falta la ENVIPE de %s' % e['abbr'])
        out[e['abbr']] = dict(x)
    return out


def nacional():
    return doc()['nacional']


def fuente():
    d = doc()
    return d['fuente'], d['nacional']['url']


def sin_fraude():
    return sorted(a for a, x in doc()['estados'].items() if x['fraude'] is None)


def pendientes():
    """Para el Registro de pendientes (pendientes.py)."""
    sin = sin_fraude()
    if not sin:
        return []
    return [{'id': PEND, 'tema': 'Planisferio · dimensión penal',
             'que': 'La tasa de fraude 2025 de %s (ENVIPE 2026)' % ', '.join(sin),
             'porque': ('En la ficha estatal del INEGI de estas entidades el delito que se destaca es otro, y su tasa de fraude viene solo en una gráfica (imagen). '
                        'No la leemos a ojo: hay que tomarla de los tabulados de la ENVIPE 2026.'),
             'responsable': 'Falta de la plataforma: el documento existe y aún no lo integramos',
             'enlace': 'https://www.inegi.org.mx/programas/envipe/2026/', 'enlace_txt': 'ENVIPE 2026 (INEGI)',
             'aparece': [('planisferio.html?d=penal', 'Planisferio · dimensión penal')]}]


def chat(base):
    """Lo que lee el chat (D.pen): [abbr, tasa de fraude o null, cifra oculta,
    delito que destaca su ficha, liga], el país y la fuente."""
    E = estados(base)
    n = nacional()
    f, u = fuente()
    return {'est': [[a, x['fraude'], x['oculta'], x['destaca'], x['url']] for a, x in sorted(E.items())],
            'nac': [n['fraude'], n['oculta']], 'fu': {'tx': f, 'url': u}}
