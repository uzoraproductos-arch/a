#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El fraude en números (pedido del autor, 05-11-2026: «los números que hay de
los fraudes… para nosotros defender nuestros servicios… sería auditor»).

Página de Aprende (`aprende-fraude-en-numeros.html`) y fichas del chat. La
investigación completa, con lo que dice la prensa y por qué no se usa, está en
docs/FRAUDE-MERCADO-Y-HOSPEDAJE.md §1. Cotejado contra el documento oficial:

- INEGI, ENVIPE 2026 (datos de 2025), Comunicado de prensa 50/26, 10-09-2026.
- INEGI, ENVE 2024 (datos de 2023), Comunicado de prensa 780/24, 10-12-2024.
- SAT, Listado completo del artículo 69-B del CFF: la cuenta se hace aquí
  mismo sobre `assets/auditor/data/sat-69b.js` (la copia con huella), así que
  cambia sola cuando se actualiza la lista.

Cada cifra sirve para una sola idea: el fraude es frecuente, casi nadie lo
denuncia y por eso conviene revisar antes de pagar. **La plataforma no dice que
«evita el fraude»**: da señales para revisar con documento oficial.
"""

import html
import json
import os

ARCHIVO = 'aprende-fraude-en-numeros.html'
TITULO = 'El fraude en números'
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENVIPE = 'https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2026/envipe/ENVIPE2026_CP.pdf'
ENVIPE_TX = 'INEGI, ENVIPE 2026, Comunicado de prensa 50/26 (10-09-2026), datos de 2025'
ENVE = 'https://inegi.org.mx/contenidos/saladeprensa/boletines/2024/ENVE/ENVE24.pdf'
ENVE_TX = 'INEGI, ENVE 2024, Comunicado de prensa 780/24 (10-12-2024), datos de 2023'
SAT_TX = 'SAT, Listado completo de contribuyentes del artículo 69-B del CFF'

# ENVIPE 2026 (comunicado 50/26).
ENVIPE_FRAUDE_M, ENVIPE_FRAUDE_H = 7947, 8688  # tasa de fraude por cada 100 mil mujeres y hombres (gráfica 1)
ENVIPE_PERDIDA = 7551                          # pesos que perdió en promedio cada víctima de fraude
ENVIPE_OCULTA, ENVIPE_DELITOS = 93.4, 33.8     # % no denunciado o no investigado, de millones de delitos
ENVIPE_COSTO, ENVIPE_PIB = 267.3, 1.06         # mil millones de pesos y % del PIB, costo del delito en hogares

# ENVE 2024 (comunicado 780/24).
ENVE_PCT, ENVE_UE = 27.2, 1.3                  # % y millones de unidades económicas víctimas
ENVE_GRANDES = 47.3                            # % de las unidades económicas grandes víctimas
ENVE_OCULTA = 90.3                             # % de delitos sin denuncia o sin carpeta
ENVE_COSTO, ENVE_PIB, ENVE_PREV = 124.3, 0.51, 67.2  # mil millones, % del PIB, mil millones en prevención


def _n(x):
    return format(x, ',')


def _chip(e, p=None):
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, ' data-pend="%s"' % p if p else '', e)


def lista_69b():
    """La cuenta de la 69-B sobre la copia de la plataforma: por situación y por
    tipo de persona. Sale del archivo, nunca de un número escrito a mano."""
    with open(os.path.join(RAIZ, 'assets', 'auditor', 'data', 'sat-69b.js'), encoding='utf-8') as f:
        t = f.read()
    d = json.loads(t[t.index('{"meta"'):t.rindex('}') + 1])
    c = {}
    for r in d['r']:
        k = (r[2], 'f' if len(r[0]) == 13 else 'm')
        c[k] = c.get(k, 0) + 1
    tot = lambda s: c.get((s, 'm'), 0) + c.get((s, 'f'), 0)
    return {'meta': d['meta'], 'F': tot('F'), 'Fm': c.get(('F', 'm'), 0), 'Ff': c.get(('F', 'f'), 0),
            'P': tot('P'), 'S': tot('S'), 'D': tot('D'), 'total': len(d['r'])}


def pendientes():
    """Para el Registro de pendientes (pendientes.py)."""
    aqui = [(ARCHIVO, 'Aprende · El fraude en números')]
    plat = 'Falta de la plataforma: el documento existe y aún no lo integramos'
    return [
        {'id': 'fraude-envipe-tasa', 'tema': 'El fraude en números',
         'que': 'La tasa total de fraude de 2025 por cada 100 mil habitantes (ENVIPE 2026)',
         'porque': 'El comunicado del INEGI da la tasa por sexo, no la total. La prensa publicó 8,290, pero hay que cotejarla en los tabulados.',
         'responsable': plat, 'enlace': 'https://www.inegi.org.mx/programas/envipe/2026/', 'enlace_txt': 'ENVIPE 2026, tabulados (INEGI)', 'aparece': aqui},
        {'id': 'fraude-enve-costo', 'tema': 'El fraude en números',
         'que': 'Cuánto del costo del delito contra las empresas corresponde al fraude (ENVE 2024)',
         'porque': 'El comunicado agrupa el fraude («bancario y al consumo del establecimiento») sin dar su costo aparte; el desglose está en los tabulados.',
         'responsable': plat, 'enlace': 'https://www.inegi.org.mx/programas/enve/2024/', 'enlace_txt': 'ENVE 2024, tabulados (INEGI)', 'aparece': aqui},
        {'id': 'fraude-condusef', 'tema': 'El fraude en números',
         'que': 'Las reclamaciones nacionales por posible fraude de 2025: cuántas, por cuánto y cuánto se recuperó (CONDUSEF)',
         'porque': 'La CONDUSEF publica sus cifras por entidad; no encontramos su total nacional de 2025, y las notas de prensa no cuadran entre sí.',
         'responsable': 'CONDUSEF: publica comunicados por estado, pero no encontramos el total nacional de 2025 en su portal',
         'enlace': 'https://www.condusef.gob.mx', 'enlace_txt': 'CONDUSEF, estadística', 'aparece': aqui},
        {'id': 'fraude-sesnsp', 'tema': 'El fraude en números',
         'que': 'Las carpetas de investigación por fraude de 2025 en todo el país (SESNSP)',
         'porque': 'Sale de sumar el subtipo «Fraude» en los datos abiertos de incidencia del fuero común.',
         'responsable': plat, 'enlace': 'https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva',
         'enlace_txt': 'SESNSP, datos abiertos de incidencia delictiva', 'aparece': aqui},
        {'id': 'fraude-efos-monto', 'tema': 'El fraude en números',
         'que': 'Cuánto facturaron las empresas de la lista 69-B (operaciones simuladas)',
         'porque': 'La prensa repite de 1.6 a 2 billones de pesos, pero no encontramos el documento del SAT que lo sostenga. Ni el SAT ni Hacienda lo han publicado: falta de transparencia de esas dependencias.',
         'responsable': 'SAT', 'enlace': 'https://www.gob.mx/sat/acciones-y-programas/notificacion-a-contribuyentes-con-operaciones-presuntamente-inexistentes-y-listados-definitivos-333336',
         'enlace_txt': 'SAT, listados del artículo 69-B', 'aparece': aqui},
    ]


def cifras():
    """(clave, título, valor, etiqueta, estado, operación, sección, fuente)."""
    s = lista_69b()
    corte = s['meta'].get('corte', '')
    e = (ENVIPE_TX, ENVIPE)
    v = (ENVE_TX, ENVE)
    l = (SAT_TX + (', corte «%s»' % corte if corte else ''), s['meta']['url'])
    return [
        ('primero', 'El delito más frecuente en México', 'El fraude',
         'es el delito más frecuente contra las personas en 2025, por delante de la extorsión y del robo en la calle o en el transporte (incluye el fraude bancario y el fraude al consumidor)',
         'oficial', '', 'personas', e),
        ('tasa', 'Qué tanto pasa el fraude', '%s y %s' % (_n(ENVIPE_FRAUDE_H), _n(ENVIPE_FRAUDE_M)),
         'fraudes por cada 100 mil hombres y por cada 100 mil mujeres en 2025', 'oficial', '', 'personas', e),
        ('perdida', 'Cuánto pierde una víctima de fraude', '$%s' % _n(ENVIPE_PERDIDA),
         'perdió en promedio cada víctima de fraude en 2025', 'oficial', '', 'personas', e),
        ('oculta', 'Cuántos delitos no se denuncian', '%s %%' % ENVIPE_OCULTA,
         'de los %s millones de delitos de 2025 no se denunció o no se investigó (la cifra oculta)' % ENVIPE_DELITOS, 'oficial', '', 'personas', e),
        ('empresas', 'Cuántas empresas sufren un delito', '%s %%' % ENVE_PCT,
         'de las unidades económicas del país (%s millones) fue víctima de algún delito en 2023; entre las grandes, el %s %%' % (ENVE_UE, ENVE_GRANDES),
         'oficial', '', 'empresas', v),
        ('costo_empresas', 'Cuánto le cuesta el delito a las empresas', '$%s mil millones' % ENVE_COSTO,
         'costó la inseguridad y el delito a las unidades económicas en 2023, el %s %% del PIB; $%s mil millones fueron gasto en protegerse'
         % (ENVE_PIB, ENVE_PREV), 'oficial', '', 'empresas', v),
        ('oculta_empresas', 'Cuántos delitos contra empresas no se denuncian', '%s %%' % ENVE_OCULTA,
         'de los delitos contra unidades económicas de 2023 no se denunció o no se abrió carpeta de investigación', 'oficial', '', 'empresas', v),
        ('definitivos', 'Empresas fantasma en definitivo (lista 69-B)', _n(s['F']),
         'contribuyentes en situación definitiva en la lista 69-B (%s empresas y %s personas físicas): sus facturas «no producen ni produjeron efecto fiscal alguno» (CFF art. 69-B, párrafo quinto)'
         % (_n(s['Fm']), _n(s['Ff'])), 'derivado', 'conteo de los renglones con situación «Definitivo» en el listado del SAT', 'facturas', l),
        ('lista', 'Cuántos hay en la lista 69-B', _n(s['total']),
         'contribuyentes en la lista: %s definitivos, %s presuntos, %s con sentencia favorable y %s desvirtuados'
         % (_n(s['F']), _n(s['P']), _n(s['S']), _n(s['D'])), 'derivado', 'conteo de los renglones del listado del SAT, por situación', 'facturas', l),
    ]


CONTEXTO = ('Por eso conviene revisar antes de pagar: lo que no se denuncia no llega a ninguna estadística. En Auditavisión puedes buscar '
            'un RFC en la lista 69-B, leer una factura sin subirla y ver los contratos públicos de una empresa.')


def fichas():
    """Fichas del chat, con la misma cifra, su estado y su documento."""
    k = (' fraude fraudes estafa estafas defraudacion victimas delito delitos denuncia cifra negra cifra oculta envipe enve inegi empresas '
         'negocios facturas falsas empresas fantasma factureras 69-b efos cuanto pierde costo del delito')
    out = []
    for clave, tit, v, etq, e, op, sec, fu in cifras():
        c = {'v': v, 'etq': etq, 'e': e}
        if op:
            c['op'] = op
        out.append({'t': 'ficha', 'tit': tit, 'txt': CONTEXTO, 'ci': [c], 'fu': [{'tx': fu[0], 'url': fu[1]}],
                    'ir': ['%s#fr-%s' % (ARCHIVO, sec), TITULO], 'k': tit + k})
    return out


def _cifra(clave):
    c = next(x for x in cifras() if x[0] == clave)
    return '<li><b>%s</b> %s %s%s</li>' % (c[2], html.escape(c[3]), _chip(c[4]),
                                           '<br><small>Operación: %s</small>' % html.escape(c[5]) if c[5] else '')


def _fuente(fu):
    return '<p class="pa-chico">Fuente: <a href="%s" target="_blank" rel="noopener">%s ↗</a>.</p>' % (fu[1], html.escape(fu[0]))


def _pend(p):
    return '<li>%s %s<br><small>%s</small></li>' % (html.escape(p['que']), _chip('pendiente', p['id']), html.escape(p['porque']))


ENTRADA = ('El fraude es el delito que más le pasa a la gente en México, y casi nadie lo denuncia. Aquí están las cifras que el INEGI y el SAT '
           'publican, con su documento, y lo que todavía nadie ha publicado. Sirven para una sola idea: <b>conviene revisar antes de pagar</b>.')


def pagina():
    """El diccionario de la página para apartados.py (tarjeta de Aprende)."""
    s = lista_69b()
    return {
        'archivo': ARCHIVO, 'menu': TITULO, 'menu_archivo': 'aprende.html',
        'padre': ('aprende.html', 'Aprende'),
        'icono': '🚨', 'titulo': TITULO, 'lema': 'Lo que el INEGI y el SAT registran del fraude, y lo que nadie ha publicado',
        'estilos': ['asistente.css'], 'entrada': ENTRADA,
        'secciones': [
            {'id': 'fr-personas', 'titulo': 'A las personas: el delito más frecuente', 'texto': 'Encuesta de victimización del INEGI, datos de 2025.', 'tarjetas': [],
             'bloque': '<ul class="leg-cifras">%s%s%s%s</ul>%s' % (_cifra('primero'), _cifra('tasa'), _cifra('perdida'), _cifra('oculta'),
                                                                 _fuente((ENVIPE_TX, ENVIPE)))},
            {'id': 'fr-empresas', 'titulo': 'A las empresas: una de cada cuatro', 'texto': 'Encuesta de victimización de empresas del INEGI, datos de 2023.', 'tarjetas': [],
             'bloque': ('<ul class="leg-cifras">%s%s%s</ul><p>En las empresas el delito más frecuente fue la extorsión; el fraude se cuenta junto '
                        'con otros delitos sin costo aparte, y ese desglose sigue %s.</p>%s')
                       % (_cifra('empresas'), _cifra('costo_empresas'), _cifra('oculta_empresas'), _chip('pendiente', 'fraude-enve-costo'),
                          _fuente((ENVE_TX, ENVE)))},
            {'id': 'fr-facturas', 'titulo': 'Las facturas de empresas fantasma', 'texto': 'La lista 69-B del SAT, contada sobre la copia de la plataforma.', 'tarjetas': [],
             'bloque': ('<ul class="leg-cifras">%s%s</ul><p>Una factura de un contribuyente en definitivo no sirve para deducir, y la lista cambia: '
                        'el Vigía 69-B la compara cada semana. <a href="herramienta-inspector-efos.html">Busca un RFC en la lista</a> o '
                        '<a href="herramienta-inspector-factura.html">lee una factura sin subirla</a>.</p>%s')
                       % (_cifra('definitivos'), _cifra('lista'), _fuente((SAT_TX, s['meta']['url'])))},
            {'id': 'fr-pendientes', 'titulo': 'Lo que todavía nadie ha publicado', 'texto': 'Cada uno con su ficha en el Registro de pendientes.', 'tarjetas': [],
             'bloque': '<ul>%s</ul>' % ''.join(_pend(p) for p in pendientes())},
            {'id': 'fr-revisar', 'titulo': 'Antes de pagarle a alguien', 'texto': 'Lo que puedes revisar hoy, gratis y con documento oficial.', 'tarjetas': [],
             'bloque': ('<ol>\n<li><a href="herramienta-inspector-efos.html">El RFC en la lista 69-B</a>: si está en definitivo, sus facturas no tienen efecto fiscal.</li>\n'
                        '<li><a href="herramienta-inspector-factura.html">La factura</a>: se lee en tu navegador, no se sube, y rehace la cuenta.</li>\n'
                        '<li><a href="contratos-publicos.html">Sus contratos públicos</a>: qué le ha vendido al gobierno y a quién.</li>\n'
                        '<li><a href="aprende-auditoria.html">Cómo se audita</a>: los tres factores del fraude y la prueba que aguanta un juicio.</li>\n'
                        '<li>¿Necesitas revisar a muchos proveedores? <a href="servicios.html">Pide un servicio</a>.</li>\n</ol>')},
            {'id': 'fr-no-dice', 'titulo': 'Lo que estas cifras no dicen', 'texto': 'Para leerlas bien.', 'tarjetas': [],
             'bloque': ('<ul>\n<li>Las encuestas del INEGI cuentan lo que las personas y las empresas <b>dicen</b> haber sufrido; no son carpetas de investigación.</li>\n'
                        '<li>Estar en la lista 69-B en situación de presunto <b>no es una condena</b>: tiene 15 días para desvirtuarlo (CFF art. 69-B, párrafo segundo).</li>\n'
                        '<li>Revisar la lista y las facturas da <b>señales para revisar</b>: no evita un fraude ni sustituye la asesoría de un profesional.</li>\n'
                        '<li>Las cifras de personas son de 2025 y las de empresas de 2023: no se suman ni se comparan entre sí.</li>\n</ul>')},
        ],
    }
