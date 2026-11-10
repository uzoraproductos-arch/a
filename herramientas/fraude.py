#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El fraude en números (pedido del autor, 05-11-2026: «los números que hay de
los fraudes… para nosotros defender nuestros servicios… sería auditor»).

Página de Aprende (`aprende-fraude-en-numeros.html`) y fichas del chat. La
investigación completa, con lo que dice la prensa y por qué no se usa, está en
docs/FRAUDE-MERCADO-Y-HOSPEDAJE.md §1. Cotejado contra el documento oficial:

- INEGI, ENVIPE 2026 (datos de 2025), Comunicado de prensa 50/26, 10-09-2026.
- INEGI, ENVE 2024 (datos de 2023), Comunicado de prensa 780/24, 10-12-2024, y
  el fraude contra las empresas de sus tabulados y su presentación de resultados,
  anclados con su huella por anclar_enve_fraude.py (07-11-2026).
- SESNSP, incidencia delictiva del fuero común (datos abiertos, estatal): las
  carpetas por fraude, ancladas con su huella por anclar_sesnsp_fraude.py y
  leídas de dimension_penal.py (07-11-2026), igual que el Planisferio.
- SAT, Listado completo del artículo 69-B del CFF: la cuenta se hace aquí
  mismo sobre `assets/auditor/data/sat-69b.js` (la copia con huella), así que
  cambia sola cuando se actualiza la lista.
- SAT, comunicado del 25-06-2019 («SAT combate la evasión fiscal por
  operaciones simuladas»): lo único oficial sobre cuánto facturaron las EFOS,
  anclado con la huella de su texto por anclar_sat_efos.py (07-11-2026).
- CONDUSEF, comunicados 081 (28-05-2026), 090 (18-06-2026) y 096 (09-07-2026):
  las reclamaciones por posible fraude a nivel nacional en 2026, ancladas con la
  huella de su texto por anclar_condusef_fraude.py (07-11-2026). El 096 habla de
  «asuntos relacionados con posibles afectaciones financieras», no de fraudes.

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
ENVIPE_FRAUDE, ENVIPE_FRAUDE_24 = 8290, 7574  # tasa total por cada 100 mil, 2025 y 2024 (presentación nacional, gráfica de los delitos más frecuentes)
ENVIPE_PRES = 'https://www.inegi.org.mx/contenidos/programas/envipe/2026/doc/envipe2026_presentacion_nacional.pdf'
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
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, ' data-pend="%s"' % p if p else '', 'auditada' if e == 'derivado' else e)


def enve():
    """El fraude contra las empresas de la ENVE 2024, del archivo anclado por
    anclar_enve_fraude.py (tabulados en CSV y presentación, con sus huellas)."""
    with open(os.path.join(RAIZ, 'docs', 'seguridad', 'enve-2024-fraude.json'), encoding='utf-8') as f:
        d = json.load(f)
    if round(d['costo_total_2018'] / 1e9, 1) != ENVE_COSTO or round(d['prevencion_2018'] / 1e9, 1) != ENVE_PREV:
        raise SystemExit('fraude.py: los tabulados de la ENVE no dan el costo del comunicado (%s y %s)' % (ENVE_COSTO, ENVE_PREV))
    return d


def efos():
    """Lo que facturaron las EFOS según el SAT (comunicado del 25-06-2019), del
    archivo anclado por anclar_sat_efos.py con la huella del texto."""
    with open(os.path.join(RAIZ, 'docs', 'seguridad', 'sat-efos-2019.json'), encoding='utf-8') as f:
        return json.load(f)


def condusef():
    """Las reclamaciones por posible fraude de los comunicados de la CONDUSEF de
    2026, del archivo anclado por anclar_condusef_fraude.py (081, 090 y 096)."""
    with open(os.path.join(RAIZ, 'docs', 'seguridad', 'condusef-fraude-2026.json'), encoding='utf-8') as f:
        d = json.load(f)
    c = {x['numero']: x for x in d['comunicados']}
    if sorted(c) != ['081', '090', '096']:
        raise SystemExit('fraude.py: faltan comunicados de la CONDUSEF en condusef-fraude-2026.json')
    return c


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
        {'id': 'fraude-enve-costo', 'tema': 'El fraude en números',
         'que': 'Cuánto le costó el fraude, en total, a las empresas en 2023 (ENVE 2024)',
         'porque': ('El INEGI publica lo que costó en promedio el fraude (${:,} en pesos de julio de 2018), pero no el total ni si ese promedio '
                    'es por delito o por empresa víctima. Multiplicarlo por los fraudes no sirve: hecho con los nueve delitos que se llaman '
                    'igual en la lámina y en los tabulados da ${:.1f} mil millones, más que los ${:.1f} mil millones que perdieron las empresas '
                    'por todos los delitos. Y los microdatos de la encuesta no son públicos: el INEGI los guarda por confidencialidad (Ley del SNIEG, '
                    'art. 37) y solo los abre en su Laboratorio de microdatos a personas acreditadas, o como tabulado especial con costo '
                    '(revisado el 07-11-2026 en su catálogo).').format(enve()['costo_promedio']['Fraude']['2023'], enve()['producto_9'] / 1e9, enve()['perdidas_2018'] / 1e9),
         'responsable': ('Nadie lo publica, y no se puede reprochar como omisión: ninguna ley obliga al INEGI a dar ese total. Es la cifra que '
                         'le faltaría a sus tabulados del costo del delito'),
         'enlace': 'https://www.inegi.org.mx/rnm/index.php/catalog/1058', 'enlace_txt': 'ENVE 2024, catálogo de microdatos (INEGI)', 'aparece': aqui},
        {'id': 'fraude-condusef', 'tema': 'El fraude en números',
         'que': 'Las reclamaciones por posible fraude de todo 2025 en el país, y de cualquier año cuánto dinero se reclamó y cuánto se devolvió (CONDUSEF)',
         'porque': ('Son dos cifras que no se suman: las reclamaciones que llegan a la CONDUSEF (decenas de miles al semestre, en su '
                    'Informe de Autoevaluación) y las que la gente presenta ante su propio banco (millones, en la estadística de la '
                    'CONDUSEF). Un buscador dio la dirección de un «Informe de Autoevaluación enero-diciembre 2025», pero no la '
                    'pudimos abrir (el 07-11-2026 el portal de la CONDUSEF respondió con error 503 o cortó la conexión) y, abierta '
                    'desde México ese mismo día, la página dice que no existe. De 2026 sí hay cifras nacionales en sus comunicados '
                    '(081 y 090), pero son parciales y no dan montos. Así que no tenemos ningún documento de la CONDUSEF con el '
                    'total de 2025 ni con el dinero: las cifras que repite la prensa, o el fragmento que da un buscador, no entran.'),
         'responsable': 'Falta de la plataforma: no hemos podido abrir ni cotejar un documento de la CONDUSEF con el total de 2025 (07-11-2026)',
         'enlace': 'https://www.condusef.gob.mx/?p=estadisticas',
         'enlace_txt': 'CONDUSEF, Estadísticas', 'aparece': aqui},
        {'id': 'fraude-efos-monto', 'tema': 'El fraude en números',
         'que': 'Cuánto han facturado las empresas de la lista 69-B (operaciones simuladas), con cifra exacta y al día',
         'porque': ('Lo único oficial es un comunicado del SAT del 25-06-2019: «un monto aproximado de {} billones de pesos» en {:,} facturas '
                    'falsas de {:,} empresas, de 2014 a esa fecha. Es una cifra redonda, de hace más de siete años, y no dice si esas '
                    'empresas son las definitivas de la lista. Desde entonces el SAT no ha vuelto a publicar el monto (revisado el '
                    '07-11-2026 en su sala de prensa y en su Informe Tributario y de Gestión), aunque la lista sigue creciendo. Las '
                    'cifras de 2 billones o más que repite la prensa no tienen documento del SAT.').format(
                        efos()['monto_billones'], efos()['facturas'], efos()['efos']),
         'responsable': ('SAT: es la única dependencia que tiene esas facturas. Lo dijo una vez, en 2019, y no ha publicado la cifra '
                         'exacta ni su actualización'), 'enlace': 'https://www.gob.mx/sat/acciones-y-programas/notificacion-a-contribuyentes-con-operaciones-presuntamente-inexistentes-y-listados-definitivos-333336',
         'enlace_txt': 'SAT, listados del artículo 69-B', 'aparece': aqui},
    ]


def _sesnsp():
    """Las carpetas por fraude del SESNSP y los fraudes que estima la ENVIPE,
    de los mismos archivos anclados que lee el Planisferio."""
    import dimension_penal as dpe
    d = dpe.sesnsp()
    ef = dpe.nacional()['delitos_fraude']
    n, n0 = d['nacional'][dpe.ANIO], d['nacional'][dpe.ANT]
    env = ef['bancario'] + ef['consumidor']
    return {'n': n, 'n0': n0, 'cam': round((n - n0) * 100.0 / n0, 1), 'env': env, 'c100': round(n * 100.0 / env, 1),
            'serie': d['nacional'], 'tx': 'SESNSP, incidencia delictiva del fuero común, datos abiertos estatales (archivo %s, corte %s)' % (d['archivo'], d['corte']),
            'url': d['pagina'], 'tab': dpe.tabulado()['url']}


def cifras():
    """(clave, título, valor, etiqueta, estado, operación, sección, fuente)."""
    s = lista_69b()
    k = _sesnsp()
    a0 = min(k['serie'])
    corte = s['meta'].get('corte', '')
    e = (ENVIPE_TX, ENVIPE)
    v = (ENVE_TX, ENVE)
    n = enve()
    nf = n['costo_promedio']['Fraude']
    vt = ('INEGI, ENVE 2024, tabulados en datos abiertos (1.8, 1.16 y 3.4)', n['zip']['url'])
    vp = ('INEGI, ENVE 2024, presentación de resultados, lámina «Costo del delito según tipo de delito»', n['pdf']['url'])
    f = efos()
    c = condusef()
    c81, c90 = c['081'], c['090']
    l = (SAT_TX + (', corte «%s»' % corte if corte else ''), s['meta']['url'])
    return [
        ('primero', 'El delito más frecuente en México', 'El fraude',
         'es el delito más frecuente contra las personas en 2025, por delante de la extorsión y del robo en la calle o en el transporte (incluye el fraude bancario y el fraude al consumidor)',
         'oficial', '', 'personas', e),
        ('tasa', 'Qué tanto pasa el fraude', _n(ENVIPE_FRAUDE),
         'fraudes por cada 100 mil habitantes en 2025 (en 2024 fueron %s; el INEGI marca el cambio como estadísticamente significativo). Por sexo: %s por cada 100 mil hombres y %s por cada 100 mil mujeres'
         % (_n(ENVIPE_FRAUDE_24), _n(ENVIPE_FRAUDE_H), _n(ENVIPE_FRAUDE_M)), 'oficial', '', 'personas', ('INEGI, ENVIPE 2026, presentación nacional de resultados', ENVIPE_PRES)),
        ('perdida', 'Cuánto pierde una víctima de fraude', '$%s' % _n(ENVIPE_PERDIDA),
         'perdió en promedio cada víctima de fraude en 2025', 'oficial', '', 'personas', e),
        ('oculta', 'Cuántos delitos no se denuncian', '%s %%' % ENVIPE_OCULTA,
         'de los %s millones de delitos de 2025 no se denunció o no se investigó (la cifra oculta)' % ENVIPE_DELITOS, 'oficial', '', 'personas', e),
        ('carpetas', 'Cuántas denuncias por fraude llegan a una fiscalía', _n(k['n']),
         'carpetas de investigación por fraude abrieron las fiscalías de los estados en 2025 (%s en 2024; %s en %s)' % (_n(k['n0']), _n(k['serie'][a0]), a0),
         'oficial', '', 'denuncias', (k['tx'], k['url'])),
        ('carpetas100', 'De cada 100 fraudes, cuántos llegan a una carpeta', 'Unas %s' % k['c100'],
         'carpetas por cada 100 fraudes que estima la encuesta del INEGI en 2025 (%s fraudes bancarios y al consumidor). No se restan: la encuesta cuenta a personas adultas en sus hogares y las carpetas incluyen a empresas'
         % _n(k['env']), 'derivado', '%s carpetas (SESNSP) × 100 ÷ %s fraudes estimados (INEGI, ENVIPE 2026, tabulado básico, cuadro 1.20)' % (_n(k['n']), _n(k['env'])),
         'denuncias', (k['tx'] + ' · INEGI, ENVIPE 2026, tabulados básicos', k['url'])),
        ('empresas', 'Cuántas empresas sufren un delito', '%s %%' % ENVE_PCT,
         'de las unidades económicas del país (%s millones) fue víctima de algún delito en 2023; entre las grandes, el %s %%' % (ENVE_UE, ENVE_GRANDES),
         'oficial', '', 'empresas', v),
        ('costo_empresas', 'Cuánto le cuesta el delito a las empresas', '$%s mil millones' % ENVE_COSTO,
         'costó la inseguridad y el delito a las unidades económicas en 2023, en pesos de julio de 2018 (en pesos de 2023 fueron $%.1f mil millones), '
         'el %s %% del PIB; $%s mil millones fueron gasto en protegerse y $%.1f mil millones, pérdidas por los delitos'
         % (n['costo_total_corrientes'] / 1e9, ENVE_PIB, ENVE_PREV, n['perdidas_2018'] / 1e9), 'oficial', '', 'empresas',
         (ENVE_TX + ' · tabulados 6.1 y 6.8', ENVE)),
        ('fraude_empresas', 'Cuántos fraudes sufren las empresas', _n(n['fraudes']),
         'fraudes contra unidades económicas en 2023 (bancarios y al consumo del establecimiento): el %s %% de los %s delitos contra empresas, '
         '%s por cada 10 mil unidades económicas' % (n['fraude_pct'], _n(n['delitos']), n['fraude_tasa']), 'oficial', '', 'empresas', vt),
        ('costo_fraude_empresas', 'Cuánto le cuesta un fraude a una empresa', '$%s' % _n(nf['2023']),
         'costó en promedio el fraude a las empresas en 2023, en pesos de julio de 2018 (en 2021, $%s; el INEGI %s el cambio como '
         'estadísticamente significativo). Es un promedio: el INEGI no publica cuánto costó el fraude en total'
         % (_n(nf['2021']), 'marca' if nf['significativo'] else 'no marca'), 'oficial', '', 'empresas', vp),
        ('oculta_empresas', 'Cuántos delitos contra empresas no se denuncian', '%s %%' % ENVE_OCULTA,
         'de los delitos contra unidades económicas de 2023 no se denunció o no se abrió carpeta de investigación; en el fraude, el %s %% (%s fraudes)'
         % (n['fraude_cifra_negra'], _n(n['fraude_sin_carpeta'])), 'oficial', '', 'empresas', (ENVE_TX + ' · tabulado 3.4', ENVE)),
        ('definitivos', 'Empresas fantasma en definitivo (lista 69-B)', _n(s['F']),
         'contribuyentes en situación definitiva en la lista 69-B (%s empresas y %s personas físicas): sus facturas «no producen ni produjeron efecto fiscal alguno» (CFF art. 69-B, párrafo quinto)'
         % (_n(s['Fm']), _n(s['Ff'])), 'derivado', 'conteo de los renglones con situación «Definitivo» en el listado del SAT', 'facturas', l),
        ('lista', 'Cuántos hay en la lista 69-B', _n(s['total']),
         'contribuyentes en la lista: %s definitivos, %s presuntos, %s con sentencia favorable y %s desvirtuados'
         % (_n(s['F']), _n(s['P']), _n(s['S']), _n(s['D'])), 'derivado', 'conteo de los renglones del listado del SAT, por situación', 'facturas', l),
        ('monto_efos', 'Cuánto facturaron las empresas fantasma', 'Unos $%s billones' % f['monto_billones'],
         'en %s facturas falsas de %s empresas que facturan operaciones simuladas, de 2014 al 25 de junio de 2019, según el SAT, que lo dio '
         'como «monto aproximado» y calculó una evasión de $%s millones, el %s %% del PIB. Es la única vez que el SAT ha publicado ese monto'
         % (_n(f['facturas']), _n(f['efos']), _n(f['evasion_mdp']), f['evasion_pib']), 'oficial', '', 'facturas', (f['fuente'], f['url'])),
        ('condusef_t1', 'Cuántas quejas (reclamaciones) por fraude llegan a la CONDUSEF', '%s %%' % c81['fraude_pct'],
         'de las %s reclamaciones que recibió la CONDUSEF en todo el país de enero a marzo de 2026 fueron por posible fraude; de ésas, '
         'el %s %% contra la banca múltiple' % (_n(c81['reclamaciones']), c81['banca_pct']), 'oficial', '', 'reclamaciones',
         ('CONDUSEF, Comunicado %s (%s)' % (c81['numero'], '28-05-2026'), c81['url'])),
        ('condusef_may', 'Cuántas reclamaciones por fraude van en 2026', 'Más de %s mil' % c90['fraude_mas_de_mil'],
         'reclamaciones por posible fraude ante la CONDUSEF de enero a mayo de 2026: en la banca múltiple, %s %% más que en el mismo '
         'periodo de 2025, y cerca de %s %% más en Sofipos y Sofomes' % (c90['banca_cambio_pct'], c90['sofi_cambio_pct']), 'oficial', '',
         'reclamaciones', ('CONDUSEF, Comunicado %s (%s)' % (c90['numero'], '18-06-2026'), c90['url'])),
    ]


CONTEXTO = ('Por eso conviene revisar antes de pagar: lo que no se denuncia no llega a ninguna estadística. En Auditavisión puedes buscar '
            'un RFC en la lista 69-B, leer una factura sin subirla y ver los contratos públicos de una empresa.')


def fichas():
    """Fichas del chat, con la misma cifra, su estado y su documento."""
    k = (' fraude fraudes estafa estafas defraudacion victimas delito delitos denuncia cifra negra cifra oculta envipe enve inegi empresas '
         'negocios facturas falsas empresas fantasma factureras 69-b efos cuanto pierde costo del delito condusef reclamaciones quejas banco bancos')
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


ENTRADA = ('El fraude es el delito que más le pasa a la gente en México, y casi nadie lo denuncia. Aquí están las cifras que el INEGI, el SAT y la CONDUSEF '
           'publican, con su documento, y lo que todavía nadie ha publicado. Sirven para una sola idea: <b>conviene revisar antes de pagar</b>.')


def pagina():
    """El diccionario de la página para apartados.py (tarjeta de Aprende)."""
    s = lista_69b()
    return {
        'archivo': ARCHIVO, 'menu': TITULO, 'menu_archivo': 'aprende.html',
        'padre': ('aprende.html', 'Aprende'),
        'icono': '🚨', 'titulo': TITULO, 'lema': 'Lo que el INEGI, el SAT y la CONDUSEF registran del fraude, y lo que nadie ha publicado',
        'estilos': ['asistente.css'], 'entrada': ENTRADA,
        'secciones': [
            {'id': 'fr-personas', 'titulo': 'A las personas: el delito más frecuente', 'texto': 'Encuesta de victimización del INEGI, datos de 2025.', 'tarjetas': [],
             'bloque': '<ul class="leg-cifras">%s%s%s%s</ul>%s' % (_cifra('primero'), _cifra('tasa'), _cifra('perdida'), _cifra('oculta'),
                                                                 _fuente((ENVIPE_TX, ENVIPE)))},
            {'id': 'fr-denuncias', 'titulo': 'Lo que llega a una fiscalía: casi nada', 'texto': 'Las carpetas de investigación por fraude que reportan las fiscalías de los estados (SESNSP).', 'tarjetas': [],
             'bloque': ('<ul class="leg-cifras">%s%s</ul><p>Una carpeta es una investigación, no una víctima: puede juntar a varias. Y más carpetas en un estado puede '
                        'querer decir más denuncia, no más fraude. <a href="planisferio.html?d=penal&amp;l=pnC">Las carpetas de cada estado, en el Planisferio</a>.</p>%s')
                       % (_cifra('carpetas'), _cifra('carpetas100'), _fuente((_sesnsp()['tx'], _sesnsp()['url'])))},
            {'id': 'fr-reclamaciones', 'titulo': 'Lo que llega a la CONDUSEF: las reclamaciones', 'texto': 'Lo que la CONDUSEF ha dicho del país en sus comunicados de 2026.', 'tarjetas': [],
             'bloque': ('<ul class="leg-cifras">%s%s</ul><p>Son de 2026 y de meses distintos: el total de 2025, y cuánto dinero se reclamó y se '
                        'devolvió, siguen %s. Las dos cifras no cuadran a simple vista: con el %s %% de %s, en tres meses serían unas 8,300, y en '
                        'cinco ya son más de %s mil; los comunicados no dicen si cuentan lo mismo, así que no se restan ni se suman. Los '
                        '«%s asuntos» de enero a junio que repite la prensa son, en palabras de la CONDUSEF, «asuntos relacionados con posibles '
                        'afectaciones financieras», no fraudes. Y una reclamación es una queja contra una institución financiera, no una '
                        'denuncia: no se compara con las carpetas de las fiscalías.</p>%s%s')
                       % (_cifra('condusef_t1'), _cifra('condusef_may'), _chip('pendiente', 'fraude-condusef'), condusef()['081']['fraude_pct'],
                          _n(condusef()['081']['reclamaciones']), condusef()['090']['fraude_mas_de_mil'], _n(condusef()['096']['asuntos']),
                          _fuente(('CONDUSEF, Comunicado 081 (28-05-2026)', condusef()['081']['url'])),
                          _fuente(('CONDUSEF, Comunicado 090 (18-06-2026)', condusef()['090']['url'])))},
            {'id': 'fr-empresas', 'titulo': 'A las empresas: una de cada cuatro', 'texto': 'Encuesta de victimización de empresas del INEGI, datos de 2023.', 'tarjetas': [],
             'bloque': ('<ul class="leg-cifras">%s%s%s%s%s</ul><p>En las empresas el delito más frecuente fue la extorsión. Los costos de la ENVE '
                        'están en pesos de julio de 2018, para compararlos entre años: no se suman con pesos de hoy. Cuánto costó el fraude '
                        'en total sigue %s: el INEGI da solo el promedio, y un promedio por el número de fraudes no da el total.</p>%s%s')
                       % (_cifra('empresas'), _cifra('fraude_empresas'), _cifra('costo_empresas'), _cifra('costo_fraude_empresas'),
                          _cifra('oculta_empresas'), _chip('pendiente', 'fraude-enve-costo'), _fuente((ENVE_TX, ENVE)),
                          _fuente(('INEGI, ENVE 2024, tabulados y presentación de resultados', enve()['pagina'])))},
            {'id': 'fr-facturas', 'titulo': 'Las facturas de empresas fantasma', 'texto': 'La lista 69-B del SAT, contada sobre la copia de la plataforma, y lo único que el SAT ha dicho de cuánto facturaron.', 'tarjetas': [],
             'bloque': ('<ul class="leg-cifras">%s%s</ul><p>Una factura de un contribuyente en definitivo no sirve para deducir, y la lista cambia: '
                        'el Vigía 69-B la compara cada semana. <a href="herramienta-inspector-efos.html">Busca un RFC en la lista</a> o '
                        '<a href="herramienta-inspector-factura.html">lee una factura sin subirla</a>.</p>%s')
                       % (_cifra('definitivos'), _cifra('lista'), _fuente((SAT_TX, s['meta']['url'])))
                       + ('<ul class="leg-cifras">%s</ul><p>Esa cifra tiene más de siete años y es redonda: la exacta y la de hoy siguen %s.</p>%s'
                          % (_cifra('monto_efos'), _chip('pendiente', 'fraude-efos-monto'), _fuente((efos()['fuente'], efos()['url']))))},
            {'id': 'fr-pendientes', 'titulo': 'Lo que todavía nadie ha publicado', 'texto': 'Cada uno con su ficha en el Registro de pendientes.', 'tarjetas': [],
             'bloque': '<ul>%s</ul>' % ''.join(_pend(p) for p in pendientes())},
            {'id': 'fr-revisar', 'titulo': 'Antes de pagarle a alguien', 'texto': 'Lo que puedes revisar hoy, gratis y con documento oficial.', 'tarjetas': [],
             'bloque': ('<ol>\n<li><a href="herramienta-inspector-efos.html">El RFC en la lista 69-B</a>: si está en definitivo, sus facturas no tienen efecto fiscal.</li>\n'
                        '<li><a href="herramienta-inspector-factura.html">La factura</a>: se lee en tu navegador, no se sube, y rehace la cuenta.</li>\n'
                        '<li><a href="contratos-publicos.html">Sus contratos públicos</a>: qué le ha vendido al gobierno y a quién.</li>\n'
                        '<li><a href="aprende-auditoria.html">Cómo se audita</a>: los tres factores del fraude y la prueba que aguanta un juicio.</li>\n'
                        '<li>¿Necesitas revisar a muchos proveedores? <a href="servicios.html">Pide un servicio</a>.</li>\n</ol>')},
            {'id': 'fr-no-dice', 'titulo': 'Lo que estas cifras no dicen', 'texto': 'Para leerlas bien.', 'tarjetas': [],
             'bloque': ('<ul>\n<li>Las encuestas del INEGI cuentan lo que las personas y las empresas <b>dicen</b> haber sufrido; las carpetas del SESNSP, lo que llegó a una fiscalía; las reclamaciones de la CONDUSEF, las quejas contra una institución financiera. Son tres mediciones distintas.</li>\n'
                        '<li>Estar en la lista 69-B en situación de presunto <b>no es una condena</b>: tiene 15 días para desvirtuarlo (CFF art. 69-B, párrafo segundo).</li>\n'
                        '<li>Revisar la lista y las facturas da <b>señales para revisar</b>: no evita un fraude ni sustituye la asesoría de un profesional.</li>\n'
                        '<li>Las cifras de personas son de 2025 y las de empresas de 2023: no se suman ni se comparan entre sí.</li>\n</ul>')},
        ],
    }
