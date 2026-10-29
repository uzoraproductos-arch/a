#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Periodismo en riesgo (pedido del autor, 29-10-2026: «las amenazas y
riesgos que ese reportero en México, de asesinatos de reporteros,
incidentes que han sido denunciados, antecedentes»).

Página del modo Reportero (`periodismo-en-riesgo.html`, cuelga de Noticias)
y fichas del chat. Cotejado contra el documento oficial:

- Mecanismo de Protección para Personas Defensoras de Derechos Humanos y
  Periodistas (Secretaría de Gobernación), Informe estadístico mensual,
  información actualizada al 31 de mayo de 2026: solicitudes, personas
  beneficiarias, probables agresores y tipo de agresiones. Solo cuenta a
  quienes pidieron entrar al Mecanismo, no a todas las personas periodistas.
- Ley para la Protección de Personas Defensoras de Derechos Humanos y
  Periodistas (DOF 25-06-2012).

Los homicidios, las carpetas de investigación y las sentencias los publica
la FEADLE de la FGR en sus estadísticas mensuales: la plataforma aún no las
coteja (su archivo no abrió desde el entorno donde se integran los datos),
así que quedan pendientes, con su enlace, y no se rellenan con las cifras de
organizaciones civiles. A las personas no se les nombra: solo cifras.
"""

import html

ARCHIVO = 'periodismo-en-riesgo.html'
TITULO = 'Periodismo en riesgo'
MEC = 'https://www.gob.mx/cms/uploads/attachment/file/1086159/05._Informe_mensual_mayo_26.pdf'
MEC_TX = 'Mecanismo de Protección para Personas Defensoras de Derechos Humanos y Periodistas (Gobernación), informe estadístico mensual al 31-05-2026'
LEY = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LPPDDHP.pdf'
FEADLE = 'https://stastdgv2portfgr032.blob.core.windows.net/femdh/FEADLE/Informes/ReportesMensuales2026/ESTADISTICAS%20Abr%2026.pdf'
FEADLE_TX = 'FGR, FEADLE, estadísticas mensuales 2026'
CORTE = '31-05-2026'

# Solicitudes de incorporación de personas periodistas, por año (informe, 1.1):
# (año, presentadas, no admitidas, admitidas ordinarias, admitidas extraordinarias).
SOLICITUDES = [
    (2019, 90, 3, 55, 32), (2020, 68, 1, 29, 38), (2021, 84, 14, 44, 26), (2022, 126, 49, 60, 17),
    (2023, 141, 50, 72, 19), (2024, 66, 33, 32, 1), (2025, 71, 46, 24, 1), ('2026 (ene-may)', 16, 9, 7, 0),
]
SOL_TOTAL = (1106, 270, 607, 229)      # 2012 (oct) a mayo de 2026
BENEF_TOTAL = (298, 723, 1021)         # mujeres, hombres, total (2.1)
BENEF_HOY = (201, 489, 690)            # al corte (2.2)
AGRESIONES = (40, 183, 536, 759)       # secuestro o privación de la libertad, agresión física, amenaza, total (3.2)
AGRESORES = (374, 293, 251, 918)       # servidores públicos, particulares, no identificados, total (3.1)
# Personas periodistas actualmente beneficiarias, las diez entidades con más (2.2.1).
ENTIDADES = [('Ciudad de México', 87), ('Guerrero', 81), ('Tamaulipas', 51), ('Quintana Roo', 50), ('Michoacán', 39),
             ('Oaxaca', 34), ('Puebla', 33), ('Veracruz', 30), ('Sonora', 23), ('Sinaloa', 23)]


def _n(x):
    return format(x, ',')


def _p(a, b):
    return ('%.1f %%' % (100.0 * a / b))


def _chip(e, p=None):
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, ' data-pend="%s"' % p if p else '', e)


def _fu(tx=MEC_TX, url=MEC):
    return {'tx': tx, 'url': url}


def pendientes():
    """Para el Registro de pendientes (pendientes.py)."""
    return [{
        'id': 'periodistas-feadle', 'tema': 'Libertad de expresión',
        'que': 'Homicidios de periodistas, carpetas de investigación y sentencias por delitos contra la libertad de expresión',
        'porque': ('La FGR publica cada mes las estadísticas de la FEADLE (Fiscalía Especial para la Atención de Delitos cometidos contra '
                   'la Libertad de Expresión), con sus carpetas de investigación, los homicidios y las sentencias. La plataforma aún no las '
                   'coteja: su archivo no abrió desde el entorno donde se integran los datos. Es falta de la plataforma, no de la FGR. '
                   'Mientras tanto no se usan en su lugar las cifras de organizaciones civiles, que no son documento oficial.'),
        'responsable': 'Falta de la plataforma: el documento existe y aún no lo integramos',
        'enlace': FEADLE, 'enlace_txt': FEADLE_TX, 'aparece': [(ARCHIVO, TITULO)]}]


def cifras():
    """Las cifras del módulo: (clave, título, valor, etiqueta, estado, operación)."""
    sp, sn = SOL_TOTAL[0], SOL_TOTAL[1]
    s25 = next(x for x in SOLICITUDES if x[0] == 2025)
    s23 = next(x for x in SOLICITUDES if x[0] == 2023)
    return [
        ('hoy', 'Cuántos periodistas protege hoy el Mecanismo', _n(BENEF_HOY[2]),
         'personas periodistas con medidas de protección al %s (%s mujeres y %s hombres)' % (CORTE, _n(BENEF_HOY[0]), _n(BENEF_HOY[1])), 'oficial', ''),
        ('total', 'Periodistas que ha protegido el Mecanismo desde 2012', _n(BENEF_TOTAL[2]),
         'personas periodistas que ha atendido desde octubre de 2012 (%s mujeres y %s hombres)' % (_n(BENEF_TOTAL[0]), _n(BENEF_TOTAL[1])), 'oficial', ''),
        ('agresiones', 'Agresiones a periodistas protegidos', _n(AGRESIONES[3]),
         'agresiones registradas a periodistas beneficiarios de 2012 a mayo de 2026: %s amenazas, %s agresiones físicas y %s secuestros o privaciones de la libertad'
         % (_n(AGRESIONES[2]), _n(AGRESIONES[1]), _n(AGRESIONES[0])), 'oficial', ''),
        ('agresores', 'Quién agrede a los periodistas protegidos', _p(AGRESORES[0], AGRESORES[3]),
         'de los probables agresores son servidoras o servidores públicos (%s de %s); %s son particulares y %s no se identificaron'
         % (_n(AGRESORES[0]), _n(AGRESORES[3]), _n(AGRESORES[1]), _n(AGRESORES[2])), 'derivado',
         '%s servidores públicos ÷ %s probables agresores × 100' % (_n(AGRESORES[0]), _n(AGRESORES[3]))),
        ('rechazo', 'Solicitudes de periodistas que no admite el Mecanismo', _p(s25[2], s25[1]),
         'de las solicitudes de periodistas no se admitieron en 2025 (%s de %s); en 2023 fue %s' % (s25[2], s25[1], _p(s23[2], s23[1])), 'derivado',
         '%s no admitidas ÷ %s presentadas en 2025 × 100; 2023: %s ÷ %s × 100' % (s25[2], s25[1], s23[2], s23[1])),
        ('solicitudes', 'Solicitudes de periodistas al Mecanismo', _n(sp),
         'solicitudes de protección presentadas por periodistas de octubre de 2012 a mayo de 2026; %s no se admitieron' % _n(sn), 'oficial', ''),
    ]


CONTEXTO = ('Lo registra el Mecanismo de Protección de Gobernación al %s. Solo cuenta a las personas periodistas que pidieron '
            'entrar al Mecanismo, no a todas.' % CORTE)

# La sección de la página donde se lee cada cifra (las tres primeras viven juntas).
SECCION = {'total': 'hoy', 'solicitudes': 'hoy'}


def fichas():
    """Fichas del chat, con la misma cifra, su estado y su documento."""
    out = []
    k = ' periodistas periodista reporteros reportero prensa libertad de expresion mecanismo de proteccion amenazas agresiones riesgo'
    for clave, tit, v, etq, e, op in cifras():
        c = {'v': v, 'etq': etq, 'e': e}
        if op:
            c['op'] = op
        out.append({'t': 'ficha', 'tit': tit, 'txt': CONTEXTO, 'ci': [c], 'fu': [_fu()],
                    'ir': ['%s#pr-%s' % (ARCHIVO, SECCION.get(clave, clave)), TITULO], 'k': tit + k})
    return out


def _tabla_solicitudes():
    filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        a, p, n, o + x, _p(n, p)) for a, p, n, o, x in SOLICITUDES)
    return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Solicitudes de protección presentadas por periodistas %s; '
            'la proporción no admitida es %s</caption><thead><tr><th scope="col">Año</th><th scope="col">Presentadas</th>'
            '<th scope="col">No admitidas</th><th scope="col">Admitidas</th><th scope="col">No admitidas, %%</th></tr></thead>'
            '<tbody>%s</tbody></table></div>') % (_chip('oficial'), _chip('derivado'), filas)


def _tabla_entidades():
    filas = ''.join('<tr><th scope="row">%s</th><td>%s</td></tr>' % (html.escape(e), n) for e, n in ENTIDADES)
    return ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Periodistas protegidos hoy, las diez entidades con más %s</caption>'
            '<thead><tr><th scope="col">Entidad</th><th scope="col">Periodistas</th></tr></thead><tbody>%s</tbody></table></div>') % (_chip('oficial'), filas)


def _cifra(clave):
    c = next(x for x in cifras() if x[0] == clave)
    return '<li><b>%s</b> %s %s%s</li>' % (c[2], html.escape(c[3]), _chip(c[4]), '<br><small>Operación: %s</small>' % html.escape(c[5]) if c[5] else '')


def _fuente():
    return '<p class="pa-chico">Fuente: <a href="%s" target="_blank" rel="noopener">%s ↗</a>.</p>' % (MEC, MEC_TX)


def pagina():
    """El diccionario de la página para apartados.py."""
    return {
        'archivo': ARCHIVO,
        'menu': TITULO,
        'menu_archivo': 'noticias-relevantes.html',
        'padre': ('noticias-relevantes.html', 'Noticias'),
        'icono': '🛡️',
        'titulo': TITULO,
        'lema': 'Lo que el Estado registra de las agresiones a la prensa',
        'estilos': ['asistente.css'],
        'entrada': ('Hacer periodismo en México tiene riesgos que el propio Estado reconoce: desde 2012 existe una ley para proteger a periodistas '
                    'y a personas defensoras de derechos humanos (<a href="%s" target="_blank" rel="noopener">Ley para la Protección de Personas '
                    'Defensoras de Derechos Humanos y Periodistas, DOF 25-06-2012 ↗</a>), y con ella el Mecanismo de Protección de Gobernación. '
                    'Aquí está lo que ese Mecanismo registra, con su documento, y lo que todavía falta: los homicidios y las sentencias. '
                    'No nombramos a las personas: solo cifras.' % LEY),
        'secciones': [
            {'id': 'pr-hoy', 'titulo': 'Cuántos periodistas protege el Mecanismo', 'texto': 'Al %s.' % CORTE, 'tarjetas': [],
             'bloque': '<ul class="leg-cifras">%s%s%s</ul>%s' % (_cifra('hoy'), _cifra('total'), _cifra('solicitudes'), _fuente())},
            {'id': 'pr-agresores', 'titulo': 'Lo que casi nadie te cuenta: cuatro de cada diez agresores son servidores públicos',
             'texto': 'Probables agresores de las personas periodistas que protege el Mecanismo.', 'tarjetas': [],
             'bloque': ('<ul class="leg-cifras">%s</ul><p>El Mecanismo registra a la persona o el grupo que la víctima señala. Es un '
                        '<b>probable</b> agresor: <b>una acusación no es una condena</b>, y el registro no dice si hubo sentencia.</p>%s'
                        % (_cifra('agresores'), _fuente()))},
            {'id': 'pr-agresiones', 'titulo': 'Qué agresiones sufren', 'texto': 'De octubre de 2012 a mayo de 2026.', 'tarjetas': [],
             'bloque': '<ul class="leg-cifras">%s</ul>%s' % (_cifra('agresiones'), _fuente())},
            {'id': 'pr-rechazo', 'titulo': 'Cada vez se admiten menos solicitudes', 'texto': 'Solicitudes de periodistas, año por año.', 'tarjetas': [],
             'bloque': '<ul class="leg-cifras">%s</ul>%s%s' % (_cifra('rechazo'), _tabla_solicitudes(), _fuente())},
            {'id': 'pr-entidades', 'titulo': 'Dónde están los periodistas protegidos', 'texto': 'Por entidad, al %s.' % CORTE, 'tarjetas': [],
             'bloque': _tabla_entidades() + _fuente()},
            {'id': 'pr-falta', 'titulo': 'Lo que falta: homicidios, investigaciones y sentencias', 'texto': 'Los publica la FGR.', 'tarjetas': [],
             'bloque': ('<p>%s Cuántas personas periodistas han sido asesinadas, cuántas carpetas de investigación abrió la FEADLE y cuántas '
                        'terminaron en sentencia lo publica la FGR cada mes (<a href="%s" target="_blank" rel="noopener">%s ↗</a>). '
                        'La plataforma aún no lo coteja; es falta nuestra, no de la FGR. Las cifras que circulan son de organizaciones '
                        'civiles: no son documento oficial y no las usamos en su lugar.</p>') % (_chip('pendiente', 'periodistas-feadle'), FEADLE, FEADLE_TX)},
            {'id': 'pr-no-dice', 'titulo': 'Lo que estas cifras no dicen', 'texto': 'Para leerlas bien.', 'tarjetas': [],
             'bloque': ('<ul>\n<li>Solo cuentan a quienes <b>pidieron entrar al Mecanismo</b>: una agresión a alguien que no lo pidió no está aquí.</li>\n'
                        '<li>Un año con menos agresiones registradas puede ser un año con menos personas protegidas, no un año más seguro.</li>\n'
                        '<li>Las cifras de 2026 llegan solo a mayo.</li>\n'
                        '<li>Si eres periodista y estás en riesgo, la ley te da derecho a pedir protección al Mecanismo. '
                        '<a href="%s" target="_blank" rel="noopener">Lee la ley ↗</a></li>\n</ul>') % LEY},
        ],
    }
