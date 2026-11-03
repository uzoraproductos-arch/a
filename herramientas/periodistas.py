#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Periodismo en riesgo (pedido del autor, 29-10-2026: «las amenazas y
riesgos que ese reportero en México, de asesinatos de reporteros,
incidentes que han sido denunciados, antecedentes»).

Página del modo Periodista (`periodismo-en-riesgo.html`, cuelga de Noticias)
y fichas del chat. Cotejado contra el documento oficial:

- Mecanismo de Protección para Personas Defensoras de Derechos Humanos y
  Periodistas (Secretaría de Gobernación), Informe estadístico mensual,
  información actualizada al 31 de mayo de 2026: solicitudes, personas
  beneficiarias, probables agresores y tipo de agresiones. Solo cuenta a
  quienes pidieron entrar al Mecanismo, no a todas las personas periodistas.
- Ley para la Protección de Personas Defensoras de Derechos Humanos y
  Periodistas (DOF 25-06-2012).
- Fiscalía Especial para la Atención de Delitos cometidos contra la Libertad de
  Expresión (FEADLE, FGR), Informe estadístico actualizado al 30 de septiembre
  de 2026: indagatorias iniciadas (averiguaciones previas y carpetas de
  investigación), homicidios registrados, ejercicio de la acción penal y
  sentencias condenatorias. A las personas no se les nombra: solo cifras.
"""

import html

ARCHIVO = 'periodismo-en-riesgo.html'
TITULO = 'Periodismo en riesgo'
MEC = 'https://www.gob.mx/cms/uploads/attachment/file/1086159/05._Informe_mensual_mayo_26.pdf'
MEC_TX = 'Mecanismo de Protección para Personas Defensoras de Derechos Humanos y Periodistas (Gobernación), informe estadístico mensual al 31-05-2026'
LEY = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LPPDDHP.pdf'
FEADLE = 'https://stastdgv2portfgr032.blob.core.windows.net/femdh/FEADLE/Informes/ReportesMensuales2026/ESTADISTICAS%20Sep%2026.pdf'
FEADLE_TX = 'FGR, FEADLE, Informe estadístico actualizado al 30 de septiembre de 2026'
CORTE = '31-05-2026'
CORTE_FEADLE = '30-09-2026'

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

# FEADLE (FGR), Informe estadístico actualizado al 30-09-2026:
FEADLE_INDAG_TOTAL = 1940              # jul. 2010 a sep. 2026 (p. 9; 822 AP [p. 12] y 1,119 CI [p. 14])
FEADLE_HOMICIDIOS_2000 = 110           # ene. 2000 a sep. 2026, derivados de su actividad periodística (p. 11)
FEADLE_HOMICIDIOS_2010 = (109, 43, 66, 17)  # jul. 2010 a sep. 2026: registrados, línea periodística, incompetencia, acción penal (p. 8)
FEADLE_SENTENCIAS = (53, 8, 5)         # condenatorias totales, por homicidio consumado, por tentativa de homicidio (pp. 6-8)
FEADLE_RESUELTOS = (258, 53, 122, 83)  # total en favor de víctimas, sentencias, suspensiones condicionales, acuerdos reparatorios (p. 8)
FEADLE_ACCION_PENAL = (472, 156, 315)  # total con acción penal, consignaciones, judicializaciones (p. 3)
FEADLE_DELITOS = [                     # principales delitos en las 1,940 indagatorias, jul. 2010 a sep. 2026 (p. 9)
    ('Amenazas', 973), ('Abuso de autoridad', 237), ('Lesiones', 147),
    ('Homicidio', 116), ('Robo', 109), ('Privación ilegal de la libertad', 78),
]
FEADLE_ANUAL = [                       # indagatorias iniciadas y homicidios por actividad periodística (pp. 9 y 11)
    (2019, 158, 7), (2020, 112, 1), (2021, 114, 3), (2022, 123, 4),
    (2023, 103, 5), (2024, 84, 1), (2025, 85, 1), ('2026 (ene-sep)', 74, 4),
]


def _n(x):
    return format(x, ',')


def _p(a, b):
    return ('%.1f %%' % (100.0 * a / b))


def _chip(e, p=None):
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, ' data-pend="%s"' % p if p else '', e)


def _fu(tx=MEC_TX, url=MEC):
    return {'tx': tx, 'url': url}


def pendientes():
    """Para el Registro de pendientes (pendientes.py). Ya se integró el informe de la FEADLE."""
    return []


def cifras():
    """Las cifras del módulo: (clave, título, valor, etiqueta, estado, operación)."""
    sp, sn = SOL_TOTAL[0], SOL_TOTAL[1]
    s25 = next(x for x in SOLICITUDES if x[0] == 2025)
    s23 = next(x for x in SOLICITUDES if x[0] == 2023)
    h_reg, h_per, h_inc, h_ap = FEADLE_HOMICIDIOS_2010
    st_tot, st_hom, st_tent = FEADLE_SENTENCIAS
    rs_tot, _, rs_susp, rs_ac = FEADLE_RESUELTOS
    ap_tot, ap_con, ap_jud = FEADLE_ACCION_PENAL
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
        ('homicidios', 'Homicidios de periodistas registrados por la FEADLE', _n(FEADLE_HOMICIDIOS_2000),
         'homicidios de periodistas derivados de su labor de 2000 a septiembre de 2026 (p. 11); desde julio de 2010 la FEADLE abrió %s expedientes de homicidio, %s con línea ligada al periodismo (%s con acción penal) y %s enviados al fuero común (p. 8)'
         % (_n(h_reg), _n(h_per), _n(h_ap), _n(h_inc)), 'oficial', ''),
        ('indagatorias', 'Investigaciones de la FEADLE por delitos contra periodistas', _n(FEADLE_INDAG_TOTAL),
         'indagatorias iniciadas de julio de 2010 a septiembre de 2026 (p. 9): %s por amenazas, %s por abuso de autoridad y %s por lesiones'
         % (_n(FEADLE_DELITOS[0][1]), _n(FEADLE_DELITOS[1][1]), _n(FEADLE_DELITOS[2][1])), 'oficial', ''),
        ('sentencias', 'Sentencias condenatorias obtenidas por la FEADLE', _n(st_tot),
         'sentencias condenatorias de julio de 2010 a septiembre de 2026 (%s por homicidio consumado y %s por tentativa, pp. 6–8); en total hay %s casos resueltos en favor de las víctimas sumando %s suspensiones condicionales y %s acuerdos reparatorios (p. 8)'
         % (_n(st_hom), _n(st_tent), _n(rs_tot), _n(rs_susp), _n(rs_ac)), 'oficial', ''),
        ('accion_penal', 'Proporción de investigaciones de la FEADLE con acción penal', _p(ap_tot, FEADLE_INDAG_TOTAL),
         'de las indagatorias iniciadas llegaron a ejercicio de la acción penal (%s de %s: %s consignaciones y %s judicializaciones, pp. 3 y 9)'
         % (_n(ap_tot), _n(FEADLE_INDAG_TOTAL), _n(ap_con), _n(ap_jud)), 'derivado',
         '%s con acción penal ÷ %s indagatorias iniciadas × 100' % (_n(ap_tot), _n(FEADLE_INDAG_TOTAL))),
    ]


CONTEXTO = ('Lo registra el Mecanismo de Protección de Gobernación al %s. Solo cuenta a las personas periodistas que pidieron '
            'entrar al Mecanismo, no a todas.' % CORTE)
CONTEXTO_FEADLE = ('Lo registra la FEADLE (Fiscalía Especial para la Atención de Delitos cometidos contra la Libertad de Expresión, '
                   'FGR) al %s. Cuenta las indagatorias del fuero federal, no las que llevan las fiscalías de los estados.' % CORTE_FEADLE)

# La sección de la página donde se lee cada cifra (las tres primeras viven juntas, y las cuatro de la FEADLE en #pr-feadle).
SECCION = {'total': 'hoy', 'solicitudes': 'hoy', 'homicidios': 'feadle', 'indagatorias': 'feadle', 'sentencias': 'feadle', 'accion_penal': 'feadle'}
CLAVES_FEADLE = {'homicidios', 'indagatorias', 'sentencias', 'accion_penal'}


def fichas():
    """Fichas del chat, con la misma cifra, su estado y su documento."""
    out = []
    k = ' periodistas periodista reporteros reportero prensa libertad de expresion mecanismo de proteccion amenazas agresiones riesgo feadle fgr homicidios asesinatos sentencias carpetas'
    for clave, tit, v, etq, e, op in cifras():
        c = {'v': v, 'etq': etq, 'e': e}
        if op:
            c['op'] = op
        es_f = clave in CLAVES_FEADLE
        out.append({'t': 'ficha', 'tit': tit, 'txt': CONTEXTO_FEADLE if es_f else CONTEXTO, 'ci': [c],
                    'fu': [_fu(FEADLE_TX, FEADLE) if es_f else _fu()],
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


def _tabla_feadle():
    filas_del = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td></tr>' % (
        html.escape(d), _n(n), _p(n, FEADLE_INDAG_TOTAL)) for d, n in FEADLE_DELITOS)
    t_del = ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Principales delitos en las %s indagatorias de la FEADLE '
             '(julio de 2010 a septiembre de 2026, p. 9) %s; porcentaje %s</caption><thead><tr><th scope="col">Delito</th>'
             '<th scope="col">Indagatorias</th><th scope="col">Del total, %%</th></tr></thead><tbody>%s</tbody></table></div>'
             % (_n(FEADLE_INDAG_TOTAL), _chip('oficial'), _chip('derivado'), filas_del))
    filas_an = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td></tr>' % (a, _n(ind), _n(hom)) for a, ind, hom in FEADLE_ANUAL)
    t_an = ('<div class="leg-tabla-caja"><table class="leg-tabla"><caption>Indagatorias iniciadas (p. 9) y homicidios ligados a la labor '
            'periodística (p. 11), por año %s</caption><thead><tr><th scope="col">Año</th><th scope="col">Indagatorias iniciadas</th>'
            '<th scope="col">Homicidios</th></tr></thead><tbody>%s</tbody></table></div>' % (_chip('oficial'), filas_an))
    return t_del + t_an


def _cifra(clave):
    c = next(x for x in cifras() if x[0] == clave)
    return '<li><b>%s</b> %s %s%s</li>' % (c[2], html.escape(c[3]), _chip(c[4]), '<br><small>Operación: %s</small>' % html.escape(c[5]) if c[5] else '')


def _fuente(tx=MEC_TX, url=MEC):
    return '<p class="pa-chico">Fuente: <a href="%s" target="_blank" rel="noopener">%s ↗</a>.</p>' % (url, tx)


def pagina():
    """El diccionario de la página para apartados.py."""
    return {
        'archivo': ARCHIVO,
        'menu': TITULO,
        'menu_archivo': 'noticias-relevantes.html',
        'padre': ('noticias-relevantes.html', 'Noticiero'),
        'icono': '🛡️',
        'titulo': TITULO,
        'lema': 'Lo que el Estado registra de las agresiones a la prensa',
        'estilos': ['asistente.css'],
        'entrada': ('Hacer periodismo en México tiene riesgos que el propio Estado reconoce: desde 2012 existe una ley para proteger a periodistas '
                    'y a personas defensoras de derechos humanos (<a href="%s" target="_blank" rel="noopener">Ley para la Protección de Personas '
                    'Defensoras de Derechos Humanos y Periodistas, DOF 25-06-2012 ↗</a>), con el Mecanismo de Protección de Gobernación (690 periodistas protegidos), y en la '
                    'Fiscalía General de la República opera la FEADLE (110 homicidios de periodistas, 1,940 indagatorias y 53 sentencias condenatorias). Aquí está lo que ambos registran, con su documento oficial. '
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
            {'id': 'pr-feadle', 'titulo': 'Homicidios, carpetas de investigación y sentencias (FEADLE)',
             'texto': 'Al %s. Lo que investiga la Fiscalía Especial para la Atención de Delitos cometidos contra la Libertad de Expresión.' % CORTE_FEADLE,
             'tarjetas': [],
             'bloque': ('<ul class="leg-cifras">%s%s%s%s</ul>'
                        '<p>De los 109 expedientes de homicidio que la FEADLE abrió desde julio de 2010, en 66 declinó competencia al fuero '
                        'común por no encontrar vínculo con el ejercicio periodístico (p. 8). Las entidades con más homicidios registrados de '
                        '2000 a septiembre de 2026 son Veracruz (17), Chihuahua (15), Guerrero (15), Tamaulipas (14), Oaxaca (7) y Sinaloa (6) (p. 11).</p>'
                        '%s%s') % (_cifra('homicidios'), _cifra('indagatorias'), _cifra('sentencias'), _cifra('accion_penal'),
                                   _tabla_feadle(), _fuente(FEADLE_TX, FEADLE))},
            {'id': 'pr-no-dice', 'titulo': 'Lo que estas cifras no dicen', 'texto': 'Para leerlas bien.', 'tarjetas': [],
             'bloque': ('<ul>\n<li>El Mecanismo solo cuenta a quienes <b>pidieron entrar</b>: una agresión a alguien que no lo pidió no está ahí.</li>\n'
                        '<li>La FEADLE solo cuenta los casos en que ejerció la facultad de atracción federal: las carpetas que se quedan en las fiscalías de los estados no aparecen en su estadística.</li>\n'
                        '<li>Un año con menos agresiones registradas puede ser un año con menos personas protegidas o menos denuncias atraídas, no un año más seguro.</li>\n'
                        '<li>Las cifras del Mecanismo llegan a mayo de 2026 y las de la FEADLE a septiembre de 2026.</li>\n'
                        '<li>Si eres periodista y estás en riesgo, la ley te da derecho a pedir protección al Mecanismo. '
                        '<a href="%s" target="_blank" rel="noopener">Lee la ley ↗</a></li>\n</ul>') % LEY},
        ],
    }
