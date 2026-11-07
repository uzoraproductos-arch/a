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

Y lo que llegó a una fiscalía (pedido del autor, 07-11-2026: «integra las
carpetas de fraude del SESNSP»): las carpetas de investigación por fraude que
las fiscalías de cada estado reportaron al SESNSP en 2025, ancladas con su
huella en docs/seguridad/sesnsp-fraude-estatal.json por anclar_sesnsp_fraude.py.

Reglas:
- **Más fraude registrado no es «peor gobierno»**: la ENVIPE es una encuesta
  en los hogares, con su margen de error, y el fraude lo cometen particulares.
- **La cifra oculta no es la eficacia de la fiscalía**: junta lo que la gente
  no denunció y lo que la autoridad no investigó.
- **Una carpeta no es un fraude ni una víctima**: es una investigación que
  abrió una fiscalía (puede juntar varias víctimas o varios delitos), y más
  carpetas puede querer decir más denuncia, no más fraude.
- **Las carpetas no se restan de la encuesta**: la ENVIPE cuenta a personas de
  18 años y más en sus hogares, y las carpetas incluyen a empresas y a todas las
  edades. Comparar el total del país es una proporción para dar idea, derivada,
  nunca «la cifra oculta del fraude».
- La tasa de carpetas usa la población del CONAPO a mitad de 2026 (la de la
  base): junta carpetas de 2025 con población de 2026, y se dice.
- Cinco fichas estatales (Chiapas, Guerrero, Estado de México, Oaxaca y
  Puebla) dan la tasa de fraude solo en una gráfica (imagen). Nunca se lee a
  ojo: la suya sale del tabulado básico del INEGI (cuadro 1.13), que cuadra
  entero con las otras 27 fichas y con el país. Cada entidad dice de dónde
  salió su tasa en «fraude_de».
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(RAIZ, 'docs', 'seguridad', 'envipe-2026-entidades.json')
SES = os.path.join(RAIZ, 'docs', 'seguridad', 'sesnsp-fraude-estatal.json')
PEND = 'penal-fraude-graficas'
ANIO, ANT = '2025', '2024'


def doc():
    with open(DOC, encoding='utf-8') as f:
        d = json.load(f)
    if len(d['estados']) != 32:
        raise SystemExit('dimension_penal: la ENVIPE no trae a las 32 entidades')
    if not d.get('tabulado', {}).get('sha') or not d['tabulado'].get('url'):
        raise SystemExit('dimension_penal: falta la huella o el enlace del tabulado de la ENVIPE')
    for a, x in d['estados'].items():
        if x['fraude'] is not None and x.get('fraude_de') not in ('ficha', 'tabulado'):
            raise SystemExit('dimension_penal: %s no dice de dónde salió su tasa de fraude' % a)
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


def tabulado():
    """El tabulado del INEGI de donde salen las tasas que la ficha da en gráfica."""
    return doc()['tabulado']


def del_tabulado():
    return sorted(a for a, x in doc()['estados'].items() if x.get('fraude_de') == 'tabulado')


def sin_fraude():
    return sorted(a for a, x in doc()['estados'].items() if x['fraude'] is None)


def pendientes():
    """Para el Registro de pendientes (pendientes.py). Desde el 07-11-2026 las
    32 tienen su tasa (las cinco que faltaban, del cuadro 1.13 del tabulado);
    si una ENVIPE nueva vuelve a dejar alguna sin ella, su ficha regresa sola."""
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


def sesnsp():
    with open(SES, encoding='utf-8') as f:
        d = json.load(f)
    if len(d['estados']) != 32 or not d.get('sha') or not d.get('pagina'):
        raise SystemExit('dimension_penal: las carpetas del SESNSP no traen a las 32 entidades, su huella o su página')
    for y, n in d['nacional'].items():
        if n != sum(x[y] for x in d['estados'].values()):
            raise SystemExit('dimension_penal: las carpetas de %s de los estados no suman las del país' % y)
    if ANIO not in d['nacional'] or ANT not in d['nacional']:
        raise SystemExit('dimension_penal: faltan las carpetas de %s o %s' % (ANT, ANIO))
    return d


def carpetas(base):
    """Por entidad: carpetas por fraude de 2025 y 2024 (oficial), el cambio y
    la tasa por cada 100 mil habitantes (derivados)."""
    d = sesnsp()
    out = {}
    for e in base['estados']:
        x = d['estados'][e['abbr']]
        n, n0 = x[ANIO], x[ANT]
        out[e['abbr']] = {'n': n, 'n24': n0, 'cam': round((n - n0) * 100.0 / n0, 1) if n0 else None,
                          't': round(n * 1e5 / e['pobPersonas'], 1)}
    return out


def carpetas_pais(base):
    """El país: carpetas, su tasa y cuántas hay por cada 100 fraudes que estima
    la ENVIPE (derivado)."""
    d = sesnsp()
    n, n0 = d['nacional'][ANIO], d['nacional'][ANT]
    pob = sum(e['pobPersonas'] for e in base['estados'])
    ef = nacional()['delitos_fraude']
    env = ef['bancario'] + ef['consumidor']
    return {'n': n, 'n24': n0, 'cam': round((n - n0) * 100.0 / n0, 1), 't': round(n * 1e5 / pob, 1), 'pob': pob,
            'env': env, 'env_b': ef['bancario'], 'env_c': ef['consumidor'], 'c100': round(n * 100.0 / env, 1),
            'serie': d['nacional'], 'fuente': d['fuente'], 'pagina': d['pagina'], 'enlace': d['enlace'], 'sha': d['sha'],
            'corte': d['corte'], 'archivo': d['archivo']}


def chat(base):
    """Lo que lee el chat (D.pen): [abbr, tasa de fraude o null, cifra oculta,
    delito que destaca su ficha, liga, de dónde salió la tasa, carpetas por
    fraude de 2025, carpetas por cada 100 mil], el país y las fuentes."""
    E = estados(base)
    n = nacional()
    f, u = fuente()
    C = carpetas(base)
    P = carpetas_pais(base)
    return {'est': [[a, x['fraude'], x['oculta'], x['destaca'], x['url'], x.get('fraude_de'), C[a]['n'], C[a]['t']] for a, x in sorted(E.items())],
            'nac': [n['fraude'], n['oculta'], P['n'], P['t'], P['c100']], 'fu': {'tx': f, 'url': u},
            'ses': {'tx': P['fuente'], 'url': P['pagina']}}
