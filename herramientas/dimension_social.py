#!/usr/bin/env python3
"""La dimensión social del Planisferio y los vínculos de cada dimensión
con el Contexto dimensional y el estado de resultados (04-11-2026).

Pedido del autor: «integrar una dimensión más al planisferio, que sería la
dimensión social. Y para todas estas dimensiones, quiero que también quede
vinculada e integrada la información con la tarjeta que es contexto
dimensional… así como el estado de resultado de los gobiernos».

- La pobreza de cada estado sale de las infografías del INEGI, Pobreza
  multidimensional 2024 (ENIGH 2024, metodología del CONEVAL), que
  `anclar_pobreza_estados.py` copia con su huella a
  docs/social/pobreza-entidades-2024.json. Aquí se vuelve a revisar.
- **La pobreza se dice como lo que mide el INEGI, nunca como el resultado de
  un gobierno estatal**: la pobreza depende del ingreso de los hogares y de
  seis carencias, y a cada una la mueven los tres niveles de gobierno, la
  economía y las remesas.
- **Las aportaciones por persona en pobreza no son lo que le toca a cada
  persona pobre**: el Ramo 33 paga sobre todo la nómina de maestros y de
  salud, y solo el FAIS se destina por ley a la población en pobreza (Ley de
  Coordinación Fiscal, art. 33). Además junta dos años: aportaciones de 2026
  entre personas de 2024.
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(RAIZ, 'docs', 'social', 'pobreza-entidades-2024.json')
PRESENTACION = 'https://www.inegi.org.mx/contenidos/desarrollosocial/pm/doc/pm_presentacion_2024.pdf'
CARENCIAS = [('rez', 'Rezago educativo'), ('sal', 'Sin acceso a servicios de salud'), ('seg', 'Sin acceso a la seguridad social'),
             ('viv', 'Vivienda de mala calidad o con hacinamiento'), ('bas', 'Sin servicios básicos en la vivienda'),
             ('ali', 'Sin alimentación nutritiva y de calidad')]

# Cada dimensión del Planisferio, con su página del Contexto dimensional
# (Enciclopedia › Números › Cuentas claras › Contexto dimensional), que mira
# el mismo tema a nivel federal. Si una página deja de existir, la
# generación se detiene (planisferio.py).
CONTEXTO = {
    'financiera': [('contexto-dimensional-presupuestaria.html', 'Dimensión presupuestaria: lo que entra, lo que se gasta y lo que falta')],
    'deuda': [('contexto-dimensional-financiera.html', 'Dimensión financiera: lo que cuesta la deuda y cuánto se debe')],
    'inversion': [('contexto-dimensional-presupuestaria.html', 'Dimensión presupuestaria: el gasto de 2024, 2026 y 2027'),
                  ('contexto-dimensional-renglones.html', 'Renglones que no se suman: lo que la ASF dejó por aclarar')],
    'ambiental': [('contexto-dimensional-ambiental.html', 'Dimensión ambiental: lo que se pierde del ambiente y lo que se gasta en protegerlo')],
    'legislativa': [('contexto-dimensional-presupuestaria.html', 'Dimensión presupuestaria: el gasto de los Poderes en el total')],
    'judicial': [('contexto-dimensional-presupuestaria.html', 'Dimensión presupuestaria: el gasto de los Poderes en el total')],
    'salud': [('contexto-dimensional-social.html', 'Dimensión social: a dónde llegan los programas y qué se sabe de sus resultados')],
    'administracion': [('contexto-dimensional-renglones.html', 'Renglones que no se suman: lo que la ASF dejó por aclarar y el subejercicio')],
    'social': [('contexto-dimensional-social.html', 'Dimensión social: a dónde llegan los programas y qué se sabe de sus resultados')],
}
RESULTADOS = ('numeros-estado-de-resultados.html', 'El estado de resultados del Gobierno Federal: lo que entró, lo que gastó y lo que quedó')
# El de cada estado vive en su ficha del Auditor de entes.
RESULTADOS_EDO = 'herramienta-inspector-entes.html#ente=estatal:%s'


def doc():
    with open(DOC, encoding='utf-8') as f:
        d = json.load(f)
    if len(d['estados']) != 32:
        raise SystemExit('dimension_social: la pobreza no trae a las 32 entidades')
    for a, x in d['estados'].items():
        if abs(x['mod'] + x['ext'] - x['pobPres']) > 0.15:
            raise SystemExit('dimension_social: %s: moderada + extrema no da su pobreza' % a)
        if not x.get('sha') or not x.get('url'):
            raise SystemExit('dimension_social: %s no trae su huella o su enlace' % a)
    return d


def estados(base):
    """Por entidad: pobreza (oficial), extrema, personas en pobreza (derivado:
    porcentaje × población de la misma infografía), las seis carencias, el
    ingreso bajo la línea de pobreza y las aportaciones 2026 por persona en
    pobreza (derivado)."""
    d = doc()
    out = {}
    for e in base['estados']:
        x = d['estados'].get(e['abbr'])
        if x is None:
            raise SystemExit('dimension_social: falta la pobreza de %s' % e['abbr'])
        pers = round(x['pobPres'] / 100 * x['pob'])
        out[e['abbr']] = {'p': x['pobPres'], 'x': x['ext'], 'm': x['mod'], 'pers': pers, 'pobT': x['pob'], 'ing': x['ing'], 'ingx': x['ingx'],
                          'car': x['car'], 'url': x['url'], 'sha': x['sha'],
                          'r33': round(e['ramo33'] * 1e6 / pers) if e.get('ramo33') else None}
    return out


def nacional():
    n = doc()['nacional']
    return {'p': n['pobPres'], 'x': n['ext'], 'pobT': n['pob'], 'pers': round(n['pobPres'] / 100 * n['pob']), 'car': n['car'], 'url': n['url'], 'ing': n['ing']}


def fuente():
    d = doc()
    return d['fuente'], PRESENTACION


def chat(base):
    """Lo que lee el chat (D.soc): una fila por estado
    [abbr, pobreza %, personas, extrema %, ingreso bajo la línea %,
    sin seguridad social %, sin servicios de salud %, rezago educativo %,
    aportaciones 2026 por persona en pobreza, infografía], el país y la fuente."""
    E = estados(base)
    n = nacional()
    f, p = fuente()
    return {'est': [[a, x['p'], x['pers'], x['x'], x['ing'], x['car']['seg'], x['car']['sal'], x['car']['rez'], x['r33'], x['url']]
                    for a, x in sorted(E.items())],
            'nac': [n['p'], n['pers'], n['x'], n['ing']], 'fu': {'tx': f, 'url': p},
            'r33': base['fiscalEntidades']['campos']['ramo33']['fuente']}
