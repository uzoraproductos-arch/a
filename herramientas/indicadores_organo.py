"""Los Indicadores Estadísticos Judiciales de la DGEJ, juzgado por juzgado y
tribunal por tribunal: una página por circuito (2021 a 2025).

Lee `docs/estadistica/dgej-indicadores-organo.json` (lo escribe
`actualizar_indicadores_organo.py`) y la tabla por circuito
(`indicadores_circuito`). No escribe cifras a mano.

El sistema no da clave de órgano: lo identifica por el nombre que publica ese
año. Un juzgado que cambió de nombre o de materia (lo que pasó con muchos tras
la reforma) sale en dos renglones; así se le dice al lector.
"""
import html
import json
import os

import indicadores_circuito as ic

AQUI = os.path.dirname(os.path.abspath(__file__))
ARCHIVO = os.path.join(AQUI, '..', 'docs', 'estadistica', 'dgej-indicadores-organo.json')
TEMAS = ['org_%d' % n for n in range(1, 33)]
ORGS = ('2', '4', '3', '340')

_D = None


def datos():
    global _D
    if _D is None:
        with open(ARCHIVO, encoding='utf-8') as f:
            _D = json.load(f)
        _D['idx'] = {(x['org'], x['niv'], x['ind'], x['ano'], x['circ']): x for x in _D['datos']}
    return _D


def get(org, niv, ind, ano, circ):
    return datos()['idx'].get((org, str(niv), ind, ano, str(circ)))


def valores(org, niv, ind, ano, circ):
    """{nombre del órgano: valor} de ese cuadro."""
    x = get(org, niv, ind, ano, circ)
    nom = datos()['nombres']
    return {nom[i]: v for i, v in x['v']} if x else {}


def archivo(n):
    return 'datos-judicial-circuito-%d-organos.html' % n


def chequeo():
    d = datos()
    assert not d['faltan'], 'faltan %d páginas por órgano: vuelve a correr actualizar_indicadores_organo.py' % len(d['faltan'])
    assert not d['descuadres'], 'la suma de los órganos no da la del circuito: %s' % d['descuadres'][:3]
    # Cada tabla por circuito de los niveles 3 y 5 tiene su detalle por órgano.
    n = 0
    for x in ic.datos()['datos']:
        if x['niv'] in ('3', '5'):
            for c in x['c']:
                assert get(x['org'], x['niv'], x['ind'], x['ano'], c), 'sin detalle: %s %s %s %s circuito %s' % (x['org'], x['niv'], x['ind'], x['ano'], c)
                n += 1
    assert len(d['datos']) == n
    # Los ingresos de cada juzgado de distrito suman los del circuito.
    for a in ic.ANOS:
        x = ic.get('2', 3, 7, a)
        for c, v in x['c'].items():
            s = sum(valores('2', 3, 7, a, c).values())
            assert abs(s - v) < 0.5, 'ingresos JD %s circuito %s: %s contra %s' % (a, c, s, v)


def _org_en(n):
    return [o for o in ORGS if any(get(o, 3, 7, a, n) for a in ic.ANOS)]


def _extremo(org, niv, ind, ano, n, alto=True):
    vs = valores(org, niv, ind, ano, n)
    if not vs:
        return None
    k = sorted(vs, key=lambda o: (-vs[o] if alto else vs[o], o))[0]
    return k, vs[k]


def _fu(org, niv, ind, ano, n, que):
    x = get(org, niv, ind, ano, n)
    xc = ic.get(org, niv, ind, ano)
    return {'que': que, 'e': 'oficial',
            'fu': {'tx': 'DGEJ, Indicadores Estadísticos Judiciales, %s %s, %s Circuito, detalle por órgano: «%s»' % (
                ic.ORGANO[org], ano, ic.ORD[n - 1], xc['nombre']),
                   'url': xc['url'].replace('IndicadoresJudicialesCircuito.asp?', 'IndicadoresJudicialesOrgano.asp?circuito=%d&' % n),
                   'sha256': x['sha256']}}


def temas():
    t = {}
    for n in range(1, 33):
        partes, fu, num = [], [], []
        for org, que, dur in (('2', 'juzgado de distrito', (15, 'el amparo indirecto')), ('4', 'tribunal colegiado', (1, 'el amparo directo'))):
            ano = '2025'
            ef = valores(org, 3, 10, ano, n)
            if not ef:
                continue
            num.append('%d %s' % (len(ef), 'juzgados de distrito' if org == '2' else 'tribunales colegiados'))
            a = _extremo(org, 3, 10, ano, n)
            s = '<li><b>El %s con más asuntos pendientes</b> al cerrar 2025: %s, con <b>%s</b>.' % (que, html.escape(a[0]), ic._v(a[1]))
            fu.append(_fu(org, 3, 10, ano, n, 'Existencia final de cada %s, 2025' % que))
            b = _extremo(org, 3, 12, ano, n, alto=False)
            if b:
                s += ' El que menos saca por cada asunto que entra: %s (%s).' % (html.escape(b[0]), ic._v(b[1]))
                fu.append(_fu(org, 3, 12, ano, n, 'Egresos ÷ ingresos de cada %s, 2025' % que))
            c = _extremo(org, 5, dur[0], ano, n)
            if c:
                s += ' El más lento en %s: %s (<b>%s días</b>).' % (dur[1], html.escape(c[0]), ic._v(c[1]))
                fu.append(_fu(org, 5, dur[0], ano, n, 'Duración de %s en cada %s, 2025' % (dur[1], que)))
            partes.append(s + '</li>')
        t['org_%d' % n] = {
            'tit': '%s Circuito, juzgado por juzgado: %s' % (ic.ORD[n - 1], ic.EDO_NOM[ic.EDO[n - 1]]),
            'h': ('<p>Los mismos indicadores de la estadística oficial, ahora <b>órgano por órgano</b>: en 2025 el %s Circuito reporta %s.</p>'
                  '<ul class="pa-lista">%s</ul>'
                  '<p class="pa-chico">Ojo: más pendientes o más días no prueban que un juzgado trabaje mal. Pesan la materia, el tamaño de su plantilla, '
                  'los asuntos que heredó y si cambió de competencia. Compara órganos de la misma materia, y el mismo órgano contra sí mismo año por año.</p>%s') % (
                ic.ORD[n - 1], ' y '.join(num), ''.join(partes), ic.AVISO),
            'fu': fu + [ic.PEND_ELECTOS],
            'sug': ['¿Cómo va el %s Circuito?' % ic.ORD[n - 1], '¿Cuánto tardan los juzgados de distrito por circuito?']}
    return t


def _tabla(org, niv, ind, n):
    an = [a for a in ic.ANOS if get(org, niv, ind, a, n)]
    if not an:
        return ''
    cols = [valores(org, niv, ind, a, n) for a in an]
    noms = sorted({o for c in cols for o in c})
    filas = ''.join('<tr><th scope="row">%s</th>%s</tr>' % (html.escape(o), ''.join('<td>%s</td>' % ic._v(c.get(o)) for c in cols)) for o in noms)
    xs = [ic.get(org, niv, ind, a) for a in an]
    tot = '<tr><th scope="row">%s Circuito</th>%s</tr>' % (ic.ORD[n - 1], ''.join('<td>%s</td>' % ic._v(x['c'].get(str(n))) for x in xs))
    nom = ic.nombre(xs[-1])
    return ('<details class="ic-ind"><summary>%s</summary><div class="leg-tabla-caja"><table class="leg-tabla">'
            '<caption>%s del %s Circuito: %s</caption><thead><tr><th scope="col">Órgano</th>%s</tr></thead><tbody>%s</tbody><tfoot>%s</tfoot></table></div>'
            '<p class="pa-chico">Cuadros de la DGEJ: %s.</p></details>') % (
        html.escape(nom), html.escape(ic.ORGANO[org]), ic.ORD[n - 1], html.escape(nom),
        ''.join('<th scope="col">%s</th>' % a for a in an), filas, tot,
        ', '.join('<a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>' % (
            html.escape(x['url'].replace('IndicadoresJudicialesCircuito.asp?', 'IndicadoresJudicialesOrgano.asp?circuito=%d&' % n), quote=True), x['ano'])
            for x in xs))


def extra(k):
    from asistente_legislativo import _chip
    n = int(k.split('_')[1])
    out = ('<p class="pa-chico">Cada indicador que la DGEJ publica para este circuito, órgano por órgano y año por año %s. El renglón del pie es la cifra del '
           'circuito. Un órgano que cambió de nombre o de materia sale en otro renglón, porque el sistema lo identifica por su nombre. Toca cada '
           'indicador para abrir su tabla.</p>') % _chip('oficial')
    for org in _org_en(n):
        out += '<h3 class="ic-org">%s</h3>' % html.escape(ic.ORGANO[org])
        for niv, que in ((3, 'Litigiosidad y movimiento'), (5, 'Productividad y tiempos')):
            tablas = ''.join(_tabla(org, niv, i, n) for i in ic.indicadores(org, niv))
            if tablas:
                out += '<p class="pa-chico"><b>%s</b></p>%s' % (que, tablas)
    return out + ('<p class="pa-chico">Fuente: <a href="%s" target="_blank" rel="noopener noreferrer">Indicadores Estadísticos Judiciales de la DGEJ ↗</a> '
                  '(«Ver todos los circuitos» y, en cada circuito, el detalle por órgano). En <a href="%s">Tu circuito judicial</a> está el resumen '
                  'comparado con el país.</p>') % (ic.SISTEMA, ic.PAGINA_CIRC[0] + '#circ_%d' % n)


def paginas():
    return [(archivo(n), '🔎', '%s Circuito: órgano por órgano' % ic.ORD[n - 1],
             'Cada juzgado y tribunal de %s, con todos sus indicadores, 2021 a 2025' % ic.EDO_NOM[ic.EDO[n - 1]],
             'Los indicadores oficiales de litigiosidad y productividad de cada juzgado de distrito y cada tribunal del %s Circuito (%s): '
             'cuántos asuntos les llegan, cuántos resuelven, cuántos se les acumulan y cuánto tardan, año por año.' % (
                 ic.ORD[n - 1], ic.EDO_NOM[ic.EDO[n - 1]]),
             ['org_%d' % n]) for n in range(1, 33)]
