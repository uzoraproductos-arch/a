#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quién responde por tu ahorro (pedido del autor, 12-11-2026: «podríamos
integrar este servicio también», sobre un texto que comparaba el seguro del
IPAB, el fondo de las SOFIPO y la custodia de una casa de bolsa).

Página de Aprende (`aprende-quien-protege-tu-ahorro.html`), fichas del chat y
un riesgo más de Servicios (RIESGOS de apartados.py). El texto que pasó el
autor fue punto de partida, como una nota de prensa: cada regla se cotejó el
12-11-2026 contra la ley vigente que publica la Cámara de Diputados
(LEYES, con la huella SHA-256 del PDF) y lo que no se pudo sostener quedó
fuera o pendiente (pendientes()):

- LPAB, arts. 6, 10 y 11: 400 mil UDIS por persona y por banco.
- LACP, arts. 98, 99, 105 y 112: 25 mil UDIS por persona y por SOFIPO; el
  fondo «procurará cubrir» y no es una entidad pública.
- LMV, arts. 156 (fr. IV), 271 y 280: en una casa de bolsa no hay seguro de
  depósito; los valores van a un depósito y, si se liquida, se separan y se
  entregan o se transfieren.
- LRITF, arts. 11 y 46: el Gobierno no garantiza el dinero en una ITF; solo
  debe estar separado del de la empresa.
- LISR, arts. 93 (fr. XX), 129 y 140, y LIF 2026, art. 24: los impuestos.
- Banco de México, valor de la UDI (serie SP68257), y la UMA 2026 del INEGI.

**No se nombra a ninguna empresa**: qué figura tiene cada una lo dice el
padrón de la CNBV, que la plataforma todavía no integra (pendiente
`ahorro-padron`). **Nunca se dice que el dinero «está seguro»**: se dice qué
ley responde, hasta cuánto y lo que no cubre.
"""

import html

ARCHIVO = 'aprende-quien-protege-tu-ahorro.html'
TITULO = '¿Quién responde por tu ahorro?'
COTEJO = '12-11-2026'
DIP = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/%s.pdf'

# sigla: (nombre, archivo en LeyesBiblio, última reforma que dice el PDF, huella SHA-256 del PDF bajado el 12-11-2026)
LEYES = {
    'LPAB': ('Ley de Protección al Ahorro Bancario', 'LPAB', 'última reforma DOF 11-05-2022',
             '40725278819b2229ddb95c8deda858d7fda9c9dd83654729e9242727f1eee4a8'),
    'LACP': ('Ley de Ahorro y Crédito Popular', 'LACP', 'última reforma DOF 14-11-2025',
             'd7c97f38c1dfe7dbf0ac5eba162d5fedb51dd132975912cf6e84aee9a614f348'),
    'LMV': ('Ley del Mercado de Valores', 'LMV', 'última reforma DOF 14-11-2025',
            'cc72fd6a12721826b6be40a77e3bb8bc297e5ce7b8794a24486a9aa2ee7c61d9'),
    'LRITF': ('Ley para Regular las Instituciones de Tecnología Financiera', 'LRITF', 'última reforma DOF 14-11-2025',
              'd6f645e6a7d3c2eeb46905d4d24ecd8e078907057dc034cda715abf019ce8491'),
    'LISR': ('Ley del Impuesto sobre la Renta', 'LISR', 'última reforma DOF 01-04-2024',
             '803c2875c09c751c1966b8eb4dca99f460b237da4ef67ee04b4fa325d8c2f786'),
    'LIF': ('Ley de Ingresos de la Federación para el Ejercicio Fiscal de 2026', 'LIF_2026', 'DOF 07-11-2025',
            'a305ca23bba43cddf2275067af29bb0ba35def7aedbbb0d3fc4557da9067a82c'),
}

# Los topes, en UDIS, como los dice la ley.
TOPE_BANCO = 400000      # LPAB, art. 11
TOPE_SOFIPO = 25000      # LACP, art. 105

# Banco de México, Valor de UDIS (serie SP68257, cuadro CP150): el último valor
# publicado al 12-11-2026. Cuando se actualice, se cambian la fecha y el valor.
UDI = 8.932476
UDI_FECHA = '25-11-2026'
UDI_URL = 'https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=8&accion=consultarCuadro&idCuadro=CP150&locale=es'
UDI_TX = 'Banco de México, Valor de UDIS (serie SP68257), valor del %s' % UDI_FECHA

# INEGI, UMA 2026 (DOF 09-01-2026), ya cotejada en la plataforma (nepotismo.py,
# glosario): diaria y anual. La anual del INEGI es la mensual por 12.
UMA_DIA = 117.31
UMA_ANUAL = 42794.64
UMA_URL = 'https://www.inegi.org.mx/temas/uma/'
EXENTO_MIN = round(5 * UMA_ANUAL, 2)        # 5 × UMA anual del INEGI
EXENTO_MAX = round(5 * UMA_DIA * 365, 2)    # 5 × UMA diaria × 365 días
EXENTO_MEDIO = round((EXENTO_MIN + EXENTO_MAX) / 2, 2)
RETENCION = 0.90                             # %, LIF 2026, art. 24


def _n(x, dec=2):
    return format(x, ',.%df' % dec)


def ley(sig, arts=''):
    """(texto de la fuente, liga) de una ley, con sus artículos."""
    nom, arch, ult, _h = LEYES[sig]
    return ('%s%s (%s)' % (nom, ', ' + arts if arts else '', ult), DIP % arch)


def _chip(e, p=None):
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, ' data-pend="%s"' % p if p else '', 'auditada' if e == 'derivado' else e)


def pesos(udis):
    return round(udis * UDI, 2)


def cifras():
    """(clave, título, valor, etiqueta, estado, operación, sección, fuente)."""
    op = '%s UDIS × %s pesos (UDI del %s, Banco de México) = $%s'
    return [
        ('banco', 'Hasta cuánto protege el IPAB tu dinero en un banco', '%s UDIS' % _n(TOPE_BANCO, 0),
         'por persona y por banco, sumando todas tus cuentas en ese banco, con capital e intereses', 'oficial', '', 'tres', ley('LPAB', 'art. 11')),
        ('banco_pesos', 'Cuánto es en pesos el seguro del IPAB', '$%s' % _n(pesos(TOPE_BANCO)),
         'son las 400 mil UDIS del IPAB con la UDI del %s' % UDI_FECHA, 'derivado',
         op % (_n(TOPE_BANCO, 0), UDI, UDI_FECHA, _n(pesos(TOPE_BANCO))), 'pesos', (UDI_TX, UDI_URL)),
        ('sofipo', 'Hasta cuánto cubre el Fondo de Protección si quiebra una SOFIPO', '%s UDIS' % _n(TOPE_SOFIPO, 0),
         'por persona y por sociedad financiera popular, y solo si se liquida o entra en concurso mercantil. La ley dice que el fondo «procurará cubrir»', 'oficial', '', 'tres', ley('LACP', 'art. 105')),
        ('sofipo_pesos', 'Cuánto es en pesos la cobertura de una SOFIPO', '$%s' % _n(pesos(TOPE_SOFIPO)),
         'son las 25 mil UDIS del Fondo de Protección con la UDI del %s' % UDI_FECHA, 'derivado',
         op % (_n(TOPE_SOFIPO, 0), UDI, UDI_FECHA, _n(pesos(TOPE_SOFIPO))), 'pesos', (UDI_TX, UDI_URL)),
        ('veces', 'Cuántas veces cabe la cobertura de una SOFIPO en la de un banco', '%d veces' % (TOPE_BANCO // TOPE_SOFIPO),
         'el seguro de un banco frente a la cobertura de una SOFIPO', 'derivado',
         '%s UDIS ÷ %s UDIS = %d' % (_n(TOPE_BANCO, 0), _n(TOPE_SOFIPO, 0), TOPE_BANCO // TOPE_SOFIPO), 'pesos', ley('LPAB', 'art. 11')),
        ('bolsa', 'El seguro de depósito de una casa de bolsa', 'No tiene',
         'una casa de bolsa no es un banco: el IPAB solo cubre depósitos y préstamos en bancos. Tus valores van a una institución para el depósito de valores y, si la casa de bolsa se liquida, lo primero que hace el liquidador es separarlos y entregarlos o transferirlos',
         'oficial', '', 'tres', ley('LMV', 'arts. 156, fr. IV, 271 y 280')),
        ('itf', 'La garantía del Gobierno en una app de pagos o de fondeo (ITF)', 'No tiene',
         'ni el Gobierno Federal ni sus entidades garantizan el dinero de los clientes de una institución de tecnología financiera; la empresa debe tenerlo separado del suyo y decírtelo en su página y en su aplicación',
         'oficial', '', 'tres', ley('LRITF', 'arts. 11 y 46')),
        ('exento', 'Hasta qué saldo no pagan impuesto los intereses de una SOFIPO', 'Entre $%s y $%s' % (_n(EXENTO_MIN), _n(EXENTO_MAX)),
         'de saldo promedio diario en 2026; punto medio $%s. La ley dice «5 salarios mínimos elevados al año», que hoy se leen en UMA' % _n(EXENTO_MEDIO), 'derivado',
         'mínimo: 5 × UMA anual del INEGI ($%s); máximo: 5 × UMA diaria ($%s) × 365 días; punto medio: (mínimo + máximo) ÷ 2' % (_n(UMA_ANUAL), _n(UMA_DIA)),
         'impuestos', ley('LISR', 'art. 93, fr. XX, inciso b)')),
        ('retencion', 'Cuánto retienen de impuesto por los intereses en 2026', '%.2f %%' % RETENCION,
         'anual sobre el capital que da lugar a los intereses, como pago provisional', 'oficial', '', 'impuestos', ley('LIF', 'art. 24')),
        ('bolsa_isr', 'El impuesto al vender acciones en bolsa', '10 %',
         'sobre las ganancias del ejercicio por vender acciones en bolsa, como pago definitivo, para las personas físicas', 'oficial', '', 'impuestos', ley('LISR', 'art. 129')),
        ('dividendos', 'El impuesto adicional a los dividendos', '10 %',
         'adicional sobre los dividendos que reparten las empresas residentes en México a las personas físicas; lo retiene la empresa y es pago definitivo', 'oficial', '', 'impuestos', ley('LISR', 'art. 140')),
    ]


CONTEXTO = ('La protección de tu dinero depende de la figura legal de la institución, no de si es una aplicación o una sucursal. '
            'Antes de depositar, revisa en el padrón de la CNBV qué figura tiene.')


def pendientes():
    """Para el Registro de pendientes (pendientes.py)."""
    aqui = [(ARCHIVO, 'Aprende · ¿Quién responde por tu ahorro?')]
    plat = 'Falta de la plataforma: el documento existe y aún no lo integramos'
    return [
        {'id': 'ahorro-padron', 'tema': '¿Quién responde por tu ahorro?',
         'que': 'Qué figura legal tiene cada institución (banco, SOFIPO, casa de bolsa o ITF), para buscarla aquí por su nombre',
         'porque': ('La CNBV publica su Padrón de Entidades Supervisadas, el IPAB la lista de bancos y el Fondo de Protección la lista de las '
                    'SOFIPO que participan (LACP, art. 98: cada semestre, en el DOF). La plataforma todavía no integra ninguna de las tres con su huella, '
                    'así que no nombra a ninguna empresa: lo que diga una nota o una publicidad sobre la figura de una aplicación no entra.'),
         'responsable': plat, 'enlace': 'https://www.gob.mx/cnbv', 'enlace_txt': 'CNBV, Padrón de Entidades Supervisadas', 'aparece': aqui},
        {'id': 'ahorro-indicadores', 'tema': '¿Quién responde por tu ahorro?',
         'que': 'Los indicadores de cada SOFIPO (capitalización, morosidad y cobertura) y el nivel de capitalización que la regla le exige',
         'porque': ('Los publica la CNBV en su portafolio de información, y el nivel que se exige está en sus disposiciones de carácter general para '
                    'las sociedades financieras populares. El %s no pudimos abrir ese portal ni cotejar esas disposiciones, así que los umbrales '
                    'que circulan (qué porcentaje es «sano») no entran.' % COTEJO),
         'responsable': plat, 'enlace': 'https://www.gob.mx/cnbv', 'enlace_txt': 'CNBV, información estadística', 'aparece': aqui},
        {'id': 'ahorro-fondo-saldo', 'tema': '¿Quién responde por tu ahorro?',
         'que': 'Cuánto dinero tiene el Fondo de Protección de las SOFIPO frente a los depósitos que debe cubrir',
         'porque': ('La ley dice que el fondo «procurará cubrir» los depósitos (LACP, art. 105) y que el fideicomiso no es una entidad de la '
                    'administración pública (art. 99). Para saber si alcanza hace falta su patrimonio y el total de depósitos cubiertos. El %s su '
                    'portal no respondió desde la plataforma, y no tenemos su informe.' % COTEJO),
         'responsable': 'Falta de la plataforma: no hemos podido abrir ni cotejar un informe del Fondo de Protección (%s)' % COTEJO,
         'enlace': 'https://www.gob.mx/cnbv', 'enlace_txt': 'CNBV, sector de ahorro y crédito popular', 'aparece': aqui},
        {'id': 'ahorro-extranjero', 'tema': '¿Quién responde por tu ahorro?',
         'que': 'Cómo se custodian los valores extranjeros comprados desde México (Sistema Internacional de Cotizaciones) y qué impuesto se retiene fuera',
         'porque': ('La cadena de custodia en el extranjero y la retención de otro país sobre los dividendos dependen de las disposiciones de la '
                    'CNBV, de los contratos del depósito de valores y de los tratados fiscales. No los hemos cotejado, así que no decimos nada de eso.'),
         'responsable': plat, 'enlace': DIP % 'LMV', 'enlace_txt': 'Ley del Mercado de Valores', 'aparece': aqui},
    ]


def fichas():
    """Fichas del chat, con la misma cifra, su estado y su documento."""
    k = (' ahorro ahorros deposito depositos dinero protegido proteccion seguro de depositos garantia ipab prosofipo fondo de proteccion sofipo sofipos '
         'sociedad financiera popular banco bancos casa de bolsa indeval valores acciones fintech app aplicacion wallet itf udis udi quiebra quiebre '
         'liquidacion si quiebra pierdo mi dinero cajita cuenta de ahorro inversion rendimiento intereses impuesto isr')
    out = []
    for clave, tit, v, etq, e, op, sec, fu in cifras():
        c = {'v': v, 'etq': etq, 'e': e}
        if op:
            c['op'] = op
        out.append({'t': 'ficha', 'tit': tit, 'txt': CONTEXTO, 'ci': [c], 'fu': [{'tx': fu[0], 'url': fu[1]}],
                    'ir': ['%s#ap-%s' % (ARCHIVO, sec), TITULO], 'k': tit + k})
    return out


def _cifra(clave):
    c = next(x for x in cifras() if x[0] == clave)
    return '<li><b>%s</b> %s %s%s</li>' % (c[2], html.escape(c[3]), _chip(c[4]),
                                           '<br><small>Operación: %s</small>' % html.escape(c[5]) if c[5] else '')


def _fuente(fu):
    return '<p class="pa-chico">Fuente: <a href="%s" target="_blank" rel="noopener">%s ↗</a>.</p>' % (html.escape(fu[1]), html.escape(fu[0]))


def _pend(p):
    return '<li>%s %s<br><small>%s</small></li>' % (html.escape(p['que']), _chip('pendiente', p['id']), html.escape(p['porque']))


# (ícono, figura, quién responde, hasta cuánto, lo que conviene saber, ley)
FIGURAS = [
    ('🏦', 'Banco (institución de banca múltiple)', 'El IPAB, un organismo del Gobierno Federal',
     '400,000 UDIS por persona y por banco',
     'Cubre depósitos y préstamos al banco, con capital e intereses. Si tienes tres cuentas en el mismo banco, se suman.', ('LPAB', 'arts. 6 y 11')),
    ('🏪', 'SOFIPO (sociedad financiera popular)', 'El Fondo de Protección, un fideicomiso que pagan las propias SOFIPO',
     '25,000 UDIS por persona y por SOFIPO',
     'Solo si la sociedad se liquida o entra en concurso mercantil. La ley dice que el fondo «procurará cubrir», y el fideicomiso no es una entidad pública.', ('LACP', 'arts. 99 y 105')),
    ('📈', 'Casa de bolsa', 'Nadie asegura el monto: no es un depósito',
     'Sin seguro de depósito',
     'Tus valores se guardan en una institución para el depósito de valores. Si la casa de bolsa se liquida, primero se separan y se te entregan o se transfieren a otra. Si tus acciones bajan de precio, nadie responde.', ('LMV', 'arts. 156, fr. IV, 271 y 280')),
    ('📱', 'Institución de tecnología financiera (ITF)', 'Nadie: la ley prohíbe que el Gobierno lo garantice',
     'Sin seguro de depósito',
     'La empresa debe tener tu dinero separado del suyo, identificado a tu nombre, y avisarte en su página, en su aplicación y en su contrato que el Gobierno no responde.', ('LRITF', 'arts. 11 y 46')),
]

ENTRADA = ('Que tu dinero esté en una aplicación o en una sucursal no dice quién responde si la institución quiebra: lo dice su <b>figura legal</b>. '
           'Un banco, una SOFIPO, una casa de bolsa y una aplicación de pagos tienen cuatro reglas distintas, y entre la primera y la segunda la '
           'cobertura cambia 16 veces. Aquí está cada una con su ley vigente, lo que no cubre y cómo revisarlo tú antes de depositar.')

# Portales para revisar: (nombre, para qué, liga o '' si no respondió al cotejo).
PORTALES = [
    ('CNBV, Padrón de Entidades Supervisadas', 'Qué figura tiene la institución y si está autorizada.', 'https://www.gob.mx/cnbv'),
    ('IPAB', 'La lista de bancos y lo que su seguro no cubre.', 'https://www.gob.mx/ipab'),
    ('Fondo de Protección de las SOFIPO', 'La lista de las sociedades que participan (se publica cada semestre en el DOF: LACP, art. 98).', ''),
    ('CONDUSEF, SIPRES', 'El registro de prestadores de servicios financieros: domicilio, estado y sanciones.', ''),
    ('Banco de México, valor de la UDI', 'Para pasar a pesos las 25 mil o las 400 mil UDIS en cualquier fecha.', UDI_URL),
]


def pagina():
    """El diccionario de la página para apartados.py (tarjeta de Aprende)."""
    tabla = '<ul class="leg-cifras">\n%s\n</ul>' % '\n'.join(
        '<li><span aria-hidden="true">%s</span> %s<b>%s</b> %s<br>Quién responde: %s.<br>%s<br>'
        '<small><a href="%s" target="_blank" rel="noopener">%s, %s ↗</a></small></li>'
        % (ico, html.escape(fig), html.escape(tope), _chip('oficial'), html.escape(quien), html.escape(saber), DIP % LEYES[l][1], l, a)
        for ico, fig, quien, tope, saber, (l, a) in FIGURAS)
    portales = '\n'.join(
        '<li><b>%s</b>: %s</li>' % (('<a href="%s" target="_blank" rel="noopener">%s ↗</a>' % (html.escape(u), html.escape(n))) if u
                                     else '%s <small>(liga por cotejar: su portal no respondió el %s)</small>' % (html.escape(n), COTEJO), html.escape(q))
        for n, q, u in PORTALES)
    leyes = ''.join('<li><a href="%s" target="_blank" rel="noopener">%s ↗</a>, %s. <small>Huella SHA-256 del PDF cotejado el %s: <code>%s</code></small></li>\n'
                    % (DIP % a, html.escape(n), u, COTEJO, h) for n, a, u, h in LEYES.values())
    return {
        'archivo': ARCHIVO, 'menu': TITULO, 'menu_archivo': 'aprende.html',
        'padre': ('aprende.html', 'Aprende'),
        'icono': '🏦', 'titulo': TITULO, 'lema': 'Banco, SOFIPO, casa de bolsa o aplicación: qué ley protege tu dinero, hasta cuánto y lo que no cubre',
        'estilos': ['asistente.css'], 'entrada': ENTRADA,
        'secciones': [
            {'id': 'ap-tres', 'titulo': 'Cuatro figuras, cuatro reglas', 'texto': 'Lo que dice la ley vigente de cada una, cotejado el %s.' % COTEJO, 'tarjetas': [],
             'bloque': ('%s\n<p>El tope es <b>por persona y por institución</b>: lo que tengas en dos bancos, o en dos SOFIPO, '
                        'se cuenta aparte en cada una. Y es por figura legal: una aplicación puede ser banco, SOFIPO o ITF, y eso no se ve en la pantalla.</p>')
                       % tabla},
            {'id': 'ap-pesos', 'titulo': 'Cuánto es en pesos', 'texto': 'La ley fija el tope en UDIS, una unidad que sube con la inflación. En pesos cambia cada día.', 'tarjetas': [],
             'bloque': ('<ul class="leg-cifras">%s%s%s</ul>\n<p>En una SOFIPO, el monto queda fijado en UDIS el día en que se declara la liquidación o el concurso, '
                        'y se paga en pesos con el valor de la UDI del día del pago (LACP, art. 112). Para otra fecha, multiplica las UDIS por el valor que publica el Banco de México.</p>%s')
                       % (_cifra('banco_pesos'), _cifra('sofipo_pesos'), _cifra('veces'), _fuente((UDI_TX, UDI_URL)))},
            {'id': 'ap-no-cubre', 'titulo': 'Lo que ninguna protección cubre', 'texto': 'Las letras chicas de cada ley.', 'tarjetas': [],
             'bloque': ('<ul>\n'
                        '<li><b>En un banco</b>, el IPAB no cubre, entre otras cosas, los títulos negociables o al portador, los depósitos de sus accionistas, '
                        'consejeros y funcionarios de los dos primeros niveles, ni las operaciones con mala fe o ligadas a operaciones con recursos de procedencia ilícita (LPAB, art. 10).</li>\n'
                        '<li><b>En una SOFIPO</b>, el fondo no cubre los depósitos de sus consejeros, comisario y funcionarios de los dos primeros niveles, ni las operaciones con mala fe o ilícitas (LACP, art. 105). '
                        'Si le debes un crédito a la misma sociedad, <b>se descuenta</b> de lo que te pagan; y si tienes varias cuentas que juntas pasan del tope, el tope se reparte entre ellas (art. 112).</li>\n'
                        '<li><b>El fondo de las SOFIPO no es el Gobierno</b>: es un fideicomiso que «no tendrá el carácter de entidad de la administración pública federal ni de fideicomiso público» (LACP, art. 99), '
                        'y la ley dice que su fin es «procurar cubrir» los depósitos (art. 105). Cuánto dinero tiene frente a lo que debe cubrir sigue %s.</li>\n'
                        '<li><b>En una casa de bolsa</b>, lo que se protege es que los valores sigan siendo tuyos, no su precio. Y si los valores o el efectivo de los clientes no alcanzan, '
                        'el liquidador paga con los activos propios de la casa de bolsa, mientras no estén dados en garantía (LMV, art. 156, fr. IV): la ley no promete que alcance.</li>\n'
                        '<li><b>En una ITF</b>, tu dinero debe estar separado del de la empresa (LRITF, art. 46), pero separado no es asegurado.</li>\n</ul>%s%s%s%s')
                       % (_chip('pendiente', 'ahorro-fondo-saldo'), _fuente(ley('LPAB', 'art. 10')), _fuente(ley('LACP', 'arts. 99, 105 y 112')),
                          _fuente(ley('LMV', 'art. 156, fr. IV')), _fuente(ley('LRITF', 'arts. 11 y 46')))},
            {'id': 'ap-impuestos', 'titulo': 'Los impuestos, que también cambian con la figura', 'texto': 'Lo que dice la Ley del ISR para una persona física, en lo básico.', 'tarjetas': [],
             'bloque': ('<ul class="leg-cifras">%s%s%s%s</ul>\n'
                        '<p>La exención de los intereses de una SOFIPO está escrita todavía en <b>salarios mínimos</b> («5 salarios mínimos generales… elevados al año»). '
                        'Desde la reforma constitucional de desindexación (DOF 27-01-2016), esas menciones se leen en UMA. Como «elevada al año» puede hacerse con la UMA anual del INEGI '
                        'o con la diaria por 365 días, damos el rango. Por arriba de ese saldo se paga impuesto. Los bancos tienen una exención parecida, pero solo para ciertas cuentas (inciso a).</p>\n'
                        '<p>Esto no es asesoría fiscal: tu caso puede traer deducciones, pérdidas o intereses reales que cambian la cuenta. Tu retención y tu sueldo se calculan en la '
                        '<a href="herramienta-calculadora.html">Calculadora Cívica</a>.</p>%s%s%s')
                       % (_cifra('exento'), _cifra('retencion'), _cifra('bolsa_isr'), _cifra('dividendos'),
                          _fuente(ley('LISR', 'arts. 93, fr. XX, 129 y 140')), _fuente(ley('LIF', 'art. 24')), _fuente(('INEGI, UMA 2026 (DOF 09-01-2026)', UMA_URL)))},
            {'id': 'ap-verifica', 'titulo': 'Antes de depositar: revísalo tú', 'texto': 'Cinco pasos, gratis y con el portal oficial.', 'tarjetas': [],
             'bloque': ('<ol>\n<li><b>Busca su razón social</b>, no su marca: está en el contrato y al pie de su página.</li>\n'
                        '<li><b>Revisa su figura</b> en el padrón de la CNBV: banco, SOFIPO, casa de bolsa o ITF. Si no aparece, pregunta antes de depositar.</li>\n'
                        '<li><b>Ubica tu tope</b> en la tabla de arriba y compáralo con lo que piensas dejar ahí.</li>\n'
                        '<li><b>Reparte</b> si pasas del tope: la cobertura es por persona y por institución.</li>\n'
                        '<li><b>Desconfía del rendimiento que no explica su riesgo</b>: el fraude es el delito más frecuente del país. '
                        '<a href="aprende-fraude-en-numeros.html">El fraude en números</a>.</li>\n</ol>\n<ul>\n%s\n</ul>\n'
                        '<p>¿Tu empresa, tu despacho o tu organización necesita revisar dónde tiene su tesorería o a un intermediario? '
                        '<a href="servicios-fraude-y-lavado.html">Prevención de fraude y de lavado, en Servicios</a>.</p>') % portales},
            {'id': 'ap-pendientes', 'titulo': 'Lo que todavía falta', 'texto': 'Cada uno con su ficha en el Registro de pendientes.', 'tarjetas': [],
             'bloque': '<ul>%s</ul>' % ''.join(_pend(p) for p in pendientes())},
            {'id': 'ap-no-dice', 'titulo': 'Lo que esta página no dice', 'texto': 'Para leerla bien.', 'tarjetas': [],
             'bloque': ('<ul>\n<li><b>No nombra a ninguna empresa</b> ni dice cuál es más segura: la figura de cada una la dice el padrón de la CNBV, y puede cambiar (una SOFIPO puede volverse banco).</li>\n'
                        '<li><b>No dice que tu dinero «está seguro»</b>: dice qué ley responde, hasta cuánto y lo que no cubre.</li>\n'
                        '<li>No habla de las cooperativas de ahorro y préstamo, de las SOFOM ni de las afores: tienen sus propias leyes, que aún no cotejamos.</li>\n'
                        '<li>Los montos en pesos son de un día: el tope de ley está en UDIS.</li>\n'
                        '<li>No es una recomendación de inversión ni asesoría fiscal.</li>\n</ul>\n<p class="pa-chico">Las leyes cotejadas:</p>\n<ul class="pa-chico">\n%s</ul>') % leyes},
        ],
    }


if __name__ == '__main__':
    for c in cifras():
        print('%-14s %-28s %s' % (c[0], c[2], c[4]))
