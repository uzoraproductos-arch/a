#!/usr/bin/env python3
"""La memoria de promesas (segunda entrega del pilar «Competimos siendo el mejor
auditor», decisión del autor, 01-11-2026).

Cada cifra que anuncia un gobierno, con su fecha, seguida por las cuatro etapas
del dinero público: lo que se prometió, lo que aprobó el Presupuesto, lo que
dice la Cuenta Pública que se gastó y lo que revisó la Auditoría Superior. Así
se ve cuándo una cifra cambia o nunca llega. El detector de puntos ciegos no lo
puede ver con un solo texto (NO_VE de puntos_ciegos.py): aquí se comparan las
declaraciones.

Reglas (AGENTS.md §2):
- **Ninguna cifra se escribe aquí.** Cada una se lee del módulo que ya la
  coteja (integrar_al_momento.py, crisis_ambientales.py, la base de
  megaobras); si cambia allá, cambia aquí, y si desaparece, la generación se
  detiene.
- Una promesa es lo que dijo un gobierno en su propio documento (comunicado,
  versión estenográfica, plan). No es un gasto: se rotula «oficial» porque
  consta que se dijo, no porque se haya gastado.
- Una etapa sin documento es «pendiente», dice por qué y a quién le toca, y
  tiene su ficha en el Registro de pendientes (pendientes()). Una etapa que
  todavía no toca lo dice con su fecha legal.
- El cambio entre etapas es «derivado», con su operación.

La pintan noticias-seguimiento.html#promesas (seccion()) y el chat (datos(),
`D.prom`, promResp() de asistente-charla.js).
"""
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

PAGINA = 'noticias-seguimiento.html#promesas'
AL_MOMENTO = 'noticias-al-momento-%s.html'
TP = 'https://www.transparenciapresupuestaria.gob.mx/'
CPEUM = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf'
LFRCF = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFRCF.pdf'

# Las cuatro etapas, en su orden.
ETAPAS = [
    ('promesa', '📣', 'Lo que se prometió'),
    ('presupuesto', '📒', 'Lo que aprobó el Presupuesto'),
    ('gasto', '🧾', 'Lo que se gastó'),
    ('asf', '🔍', 'Lo que revisó la Auditoría'),
]
NOMBRE = {k: n for k, _i, n in ETAPAS}
ICONO = {k: i for k, i, _n in ETAPAS}


def m(v, d=0):
    return '$' + format(v, ',.%df' % d) + ' millones'


def _ref(rid):
    import anclar_crisis
    r = next((x for x in anclar_crisis.REF_NUEVAS if x['id'] == rid), None)
    if not r:
        raise SystemExit('promesas: falta la referencia %s en anclar_crisis.py' % rid)
    return r['url']


def _agua():
    """El agua de Guadalajara: la cifra federal cambió en una semana y todavía no aparece en el Presupuesto 2027."""
    import integrar_al_momento as im
    lo, hi = im.AGUA_FED
    ult = im.AGUA_FED_2810
    dmin, dmax = ult - hi, ult - lo
    return {
        'id': 'agua-guadalajara', 'ico': '🚰',
        'tit': 'El agua de Guadalajara: de «alrededor de 12 a 13 mil» a 14,500 millones en una semana',
        'quien': 'Gobierno de México (Presidencia); lo ejercería la Conagua',
        'temas': ['agua de guadalajara', 'agua en guadalajara', 'acueducto', 'chapala', 'san gaspar', 'agua potable de guadalajara'],
        'nota': AL_MOMENTO % 'agua-guadalajara-14500-federal',
        'etapas': [
            {'et': 'promesa', 'fecha': '21-10-2026', 'cifra': 'Entre %s y %s' % (m(lo), m(hi)), 'e': 'oficial',
             'tx': 'En su conferencia, la Presidenta habló de «alrededor de» 12 mil a 13 mil millones federales para el agua de la zona metropolitana.',
             'fu': 'Presidencia, versión estenográfica del 21-10-2026', 'url': im.PRES_2110},
            {'et': 'promesa', 'fecha': '28-10-2026', 'cifra': m(ult), 'e': 'oficial',
             'tx': 'El comunicado de Presidencia dice que el Gobierno de México «invertirá» esa cifra, sin deuda. Es un compromiso, no una partida aprobada.',
             'fu': 'Presidencia, comunicado del 28-10-2026', 'url': im.PRES_2810},
            {'et': 'presupuesto', 'fecha': 'a más tardar el 15-11-2026', 'cifra': 'Todavía no toca', 'e': 'pendiente',
             'pend': 'promesa-agua-guadalajara-pef', 'url': im.PPEF, 'fu': 'Proyecto de Presupuesto 2027 (Hacienda)',
             'tx': ('La Cámara de Diputados aprueba el Presupuesto 2027 a más tardar el 15 de noviembre (Constitución, art. 74, fr. IV). '
                    'Según la prensa, la Presidenta dijo que el dinero no vendrá etiquetado: si no aparece en el ramo de la Conagua, '
                    'no se podrá seguir de dónde sale.')},
            {'et': 'gasto', 'fecha': 'a más tardar el 30-04-2028', 'cifra': 'Todavía no toca', 'e': 'pendiente',
             'pend': 'promesa-agua-guadalajara-ejercido', 'url': im.CUENTA_PUBLICA, 'fu': 'Cuenta Pública (Hacienda)',
             'tx': 'Lo gastado en 2027 lo dirá la Cuenta Pública 2027, que el Ejecutivo entrega a más tardar el 30 de abril de 2028 (Constitución, art. 74, fr. VI).'},
            {'et': 'asf', 'fecha': 'desde junio de 2028', 'cifra': 'Todavía no toca', 'e': 'pendiente',
             'pend': 'promesa-agua-guadalajara-ejercido', 'url': LFRCF, 'fu': 'Ley de Fiscalización (LFRCF), art. 35',
             'tx': 'La Auditoría Superior revisa la Cuenta Pública 2027 en sus entregas de junio y octubre de 2028 y febrero de 2029.'},
        ],
        'cambio': {'tx': 'En una semana, la cifra federal creció entre %s y %s; punto medio, %s.' % (m(dmin), m(dmax), m((dmin + dmax) / 2)),
                   'e': 'derivado', 'op': '%s − %s = %s y %s − %s = %s; punto medio (%s + %s) ÷ 2' % (
                       format(ult, ','), format(hi, ','), format(dmin, ','), format(ult, ','), format(lo, ','), format(dmax, ','),
                       format(dmin, ','), format(dmax, ','))},
        'sigue': 'Que los 14,500 millones aparezcan en el Presupuesto 2027, en el ramo de la Conagua, con su programa y su monto.',
    }


def _otis():
    """El huracán Otis: lo anunciado y lo que se informó como gastado (crisis_ambientales.py)."""
    import crisis_ambientales as ca
    src = open(os.path.join(AQUI, 'crisis_ambientales.py'), encoding='utf-8').read()
    if "mdp(1065.8), 'Compras sin licitación que revisó la Auditoría'" not in src:
        raise SystemExit('promesas: cambió lo que revisó la ASF de Otis en crisis_ambientales.py; revisa la memoria de promesas')
    asf_rev = 1065.8
    dif = ca.OTIS_PLAN - ca.OTIS_EJ
    return {
        'id': 'otis', 'ico': '🌀',
        'tit': 'El huracán Otis: se anunciaron %s y se informaron %s gastados' % (m(ca.OTIS_PLAN), m(ca.OTIS_EJ)),
        'quien': 'Secretaría de Hacienda (el plan) y Secretaría de Bienestar (lo gastado)',
        'temas': ['otis', 'acapulco', 'coyuca', 'reconstruccion de guerrero', 'reconstruccion de acapulco'],
        'nota': ca.ARCHIVO,
        'etapas': [
            {'et': 'promesa', 'fecha': '01-11-2023', 'cifra': m(ca.OTIS_PLAN), 'e': 'oficial',
             'tx': 'Hacienda presentó el Plan General de Reconstrucción para Acapulco y Coyuca de Benítez, en 20 renglones; dos de ellos, «por determinar».',
             'fu': 'Presidencia y Hacienda, Plan de Reconstrucción (01-11-2023)', 'url': _ref('ref-shcp-plan-otis')},
            {'et': 'presupuesto', 'fecha': '', 'cifra': 'Sin publicar', 'e': 'pendiente', 'pend': 'otis-financiamiento',
             'tx': 'Hacienda no ha publicado cuánto se pagó con el Fondo de Desastres del Ramo 23 y cuánto con el presupuesto de cada dependencia.',
             'fu': 'Cuenta Pública 2024 (Hacienda)', 'url': 'https://www.cuentapublica.hacienda.gob.mx/es/CP/2024'},
            {'et': 'gasto', 'fecha': '13-09-2024', 'cifra': m(ca.OTIS_EJ), 'e': 'oficial',
             'tx': ('La secretaria de Bienestar: «son 35 mil 17 millones de pesos para levantar estos dos municipios». Es lo que se informó '
                    'en conferencia, no un cierre del plan; el desglose de ese día no suma ese total.'),
             'fu': 'Presidencia, versión estenográfica del 13-09-2024', 'url': ca.EST_OTIS_EJ},
            {'et': 'asf', 'fecha': 'Cuenta Pública 2023', 'cifra': m(asf_rev, 1), 'e': 'oficial',
             'tx': ('La Auditoría revisó las compras de enseres de la Defensa: 12 contratos por adjudicación directa. Promovió una revisión '
                    'fiscal y dos responsabilidades administrativas, sin fijar un monto por aclarar. No revisó el plan completo.'),
             'fu': 'ASF, Cuenta Pública 2023, auditoría 362', 'url': _ref('ref-asf-cp2023-0362')},
        ],
        'cambio': {'tx': 'Lo anunciado que no aparece como gastado: %s. Ningún documento dice si se gastó por otra vía, si se dejó de gastar o si se reasignó.' % m(dif),
                   'e': 'derivado', 'op': '%s − %s' % (format(ca.OTIS_PLAN, ',.0f'), format(ca.OTIS_EJ, ',.0f')), 'pend': 'otis-diferencia'},
        'sigue': 'Que Hacienda y Bienestar publiquen el cierre del plan: de qué ramo salió cada peso y qué pasó con la diferencia.',
    }


def _dos_bocas():
    """La Refinería Olmeca: lo anunciado en 2019 y la obra en proceso que registró la ASF en 2024 (base de megaobras)."""
    import auditorias
    d = auditorias.db()['simulador_megaobras']
    o = next((x for x in d['obras'] if x['id'] == 'dos-bocas'), None)
    filas = {f['c']: f for f in d['cuenta']['obras'].get('dos-bocas', []) if f.get('v') is not None}
    if not o or 'inversion_presupuestada_musd' not in filas or not o.get('rangos_campos'):
        raise SystemExit('promesas: la base de megaobras ya no trae lo anunciado de Dos Bocas; revisa la memoria de promesas')
    anun = filas['inversion_presupuestada_musd']
    rp, rs = o['rangos_campos']['inversion_presupuestada_mdp'], o['rangos_campos']['sobrecosto_pct']
    if anun['anio'] != 2019 or abs(rp['max'] - 160000.0) > 0.05:
        raise SystemExit('promesas: cambió lo anunciado de Dos Bocas en la base; revisa la memoria de promesas')
    asf = 'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Auditorias/2024_0247_a.pdf'
    real = o['inversion_real_mdp']
    return {
        'id': 'dos-bocas', 'ico': '🛢️',
        'tit': 'La Refinería Olmeca (Dos Bocas): se anunciaron 8,000 millones de dólares y la obra registrada ya va en %s de pesos' % m(real, 1),
        'quien': 'Secretaría de Energía y Presidencia (el anuncio); Pemex, por su filial PTI Infraestructura de Desarrollo (la obra)',
        'temas': ['dos bocas', 'refineria olmeca', 'olmeca'],
        'nota': 'auditoria-dos-bocas.html',
        'etapas': [
            {'et': 'promesa', 'fecha': '09-05-2019', 'cifra': '%s millones de dólares, o «160 mil millones de pesos»' % format(anun['v'], ',.0f'), 'e': 'oficial',
             'tx': ('La Sener anunció una «inversión máxima» de 8,000 millones de dólares, y el presidente dijo «160 mil millones de pesos en '
                    'tres años, no más». Al tipo de cambio de ese día, los dólares eran %s.' % m(rp['min'], 1)),
             'fu': anun['f'][0]['doc'], 'url': anun['f'][0]['url']},
            {'et': 'presupuesto', 'fecha': '2019 a 2024', 'cifra': 'Sin integrar', 'e': 'pendiente', 'pend': 'promesa-dos-bocas-pef',
             'tx': 'Lo que cada Presupuesto de 2019 a 2024 le asignó a la refinería está en documentos públicos que la plataforma aún no integra.',
             'fu': 'Transparencia Presupuestaria (Hacienda)', 'url': TP},
            {'et': 'gasto', 'fecha': 'al 31-12-2024', 'cifra': m(real, 1), 'e': 'oficial',
             'tx': ('Es la obra en proceso que registró la filial de Pemex que construye la refinería, según la Auditoría. La obra '
                    'seguía en proceso: es una cota inferior de lo que costará.'),
             'fu': 'ASF, Cuenta Pública 2024, auditoría 247, p. 8', 'url': asf},
            {'et': 'asf', 'fecha': 'Cuenta Pública 2024', 'cifra': '3 recomendaciones', 'e': 'oficial',
             'tx': o['hallazgo_asf'], 'fu': 'ASF, Cuenta Pública 2024, auditoría 247', 'url': asf},
        ],
        'cambio': {'tx': 'De lo anunciado a lo registrado, la obra subió entre %.1f %% y %.1f %%; punto medio, %.1f %%, en pesos de cada año.' % (
            rs['min'], rs['max'], rs['medio']), 'e': 'derivado', 'op': rs['op']},
        'sigue': 'Lo que asignó cada Presupuesto de 2019 a 2024 y el costo final cuando la obra se dé por terminada.',
    }


PROMESAS = [_agua, _otis, _dos_bocas]


def todas():
    out = [p() for p in PROMESAS]
    for p in out:
        ets = [x['et'] for x in p['etapas']]
        if ets[0] != 'promesa' or any(e not in NOMBRE for e in ets):
            raise SystemExit('promesas: %s debe empezar por la promesa y usar las cuatro etapas' % p['id'])
        for x in p['etapas']:
            if x['e'] == 'pendiente' and not x.get('pend'):
                raise SystemExit('promesas: la etapa «%s» de %s es pendiente y no dice su ficha' % (x['et'], p['id']))
            if not x.get('url'):
                raise SystemExit('promesas: la etapa «%s» de %s no trae su documento' % (x['et'], p['id']))
    return out


def datos():
    """Lo que lee el chat (D.prom)."""
    return {'pag': PAGINA, 'etapas': [[k, i, n] for k, i, n in ETAPAS], 'p': todas()}


def pendientes():
    """Las fichas del Registro de pendientes de las etapas que todavía no tienen documento."""
    import pendientes as pe
    ap = [('noticias-seguimiento.html#promesas', 'Noticias · Memoria de promesas')]
    return [
        {'id': 'promesa-agua-guadalajara-pef', 'tema': 'Memoria de promesas',
         'que': 'Si los 14,500 millones federales para el agua de Guadalajara aparecen en el Presupuesto 2027',
         'porque': ('Todavía no toca: la Cámara de Diputados aprueba el Presupuesto 2027 a más tardar el 15 de noviembre de 2026 '
                    '(Constitución, art. 74, fr. IV). Según la prensa, la Presidenta dijo que el dinero no vendrá etiquetado; si no aparece '
                    'en el ramo de la Conagua con su programa, Hacienda y la Conagua tendrán que decir de dónde sale.'),
         'responsable': 'Cámara de Diputados (aprobación) y Secretaría de Hacienda (publicación en el DOF)',
         'enlace': 'https://www.ppef.hacienda.gob.mx/', 'enlace_txt': 'Proyecto de Presupuesto 2027 (Hacienda)', 'aparece': ap},
        {'id': 'promesa-agua-guadalajara-ejercido', 'tema': 'Memoria de promesas',
         'que': 'Lo que de verdad se gaste en las obras de agua de Guadalajara y lo que revise la Auditoría',
         'porque': ('Todavía no toca: lo gastado en 2027 sale en la Cuenta Pública 2027, a más tardar el 30 de abril de 2028 (Constitución, '
                    'art. 74, fr. VI), y la Auditoría Superior la revisa en 2028 y 2029 (LFRCF, art. 35).'),
         'responsable': 'Secretaría de Hacienda (Cuenta Pública) y Comisión Nacional del Agua (ejecución)',
         'enlace': 'https://www.cuentapublica.hacienda.gob.mx/', 'enlace_txt': 'Cuenta Pública (Hacienda)', 'aparece': ap},
        {'id': 'promesa-dos-bocas-pef', 'tema': 'Memoria de promesas',
         'que': 'Lo que cada Presupuesto de 2019 a 2024 le asignó a la Refinería Olmeca',
         'porque': 'Los presupuestos de cada año son públicos; la plataforma todavía no integra la partida de la refinería.',
         'responsable': pe.PLATAFORMA, 'enlace': TP, 'enlace_txt': 'Transparencia Presupuestaria (Hacienda)', 'aparece': ap},
    ]


def seccion(esc, chip):
    """El cuerpo de la sección «Memoria de promesas» de noticias-seguimiento.html."""
    def etapa(x):
        return ('      <li class="nt-prom-et nt-prom-%s"><p class="nt-prom-et-n"><span aria-hidden="true">%s</span> <b>%s</b>%s</p>\n'
                '        <p class="nt-prom-cifra">%s %s</p>\n        <p>%s <a href="%s" target="_blank" rel="noopener">%s ↗</a></p></li>') % (
            x['et'], ICONO[x['et']], NOMBRE[x['et']], (' · ' + esc(x['fecha'])) if x['fecha'] else '',
            esc(x['cifra']), chip(x['e'], x.get('pend')), esc(x['tx']), esc(x['url']), esc(x['fu']))

    def caso(p):
        c = p['cambio']
        return ('  <article class="nt-prom" id="promesa-%s">\n'
                '    <h3 class="nt-sub"><span aria-hidden="true">%s</span> %s</h3>\n'
                '    <p class="nt-prom-quien">Quién lo dijo: %s</p>\n'
                '    <ol class="nt-prom-etapas">\n%s\n    </ol>\n'
                '    <p class="nt-prom-cambio"><b>Lo que cambió:</b> %s %s <span class="nt-prom-op">(%s)</span>%s</p>\n'
                '    <p><b>Lo que sigue:</b> %s <a href="%s">Ver el caso completo</a>.</p>\n'
                '  </article>') % (
            p['id'], p['ico'], esc(p['tit']), esc(p['quien']), '\n'.join(etapa(x) for x in p['etapas']),
            esc(c['tx']), chip(c['e']), esc(c['op']), (' ' + chip('pendiente', c['pend'])) if c.get('pend') else '',
            esc(p['sigue']), esc(p['nota']))

    pasos = ' → '.join('%s %s' % (i, n) for _k, i, n in ETAPAS)
    return ('  <p>Una promesa de gasto se puede seguir: primero se anuncia, luego debe aparecer en el Presupuesto, después la Cuenta '
            'Pública dice cuánto se gastó y al final la Auditoría Superior lo revisa. Aquí guardamos cada cifra que anuncia un gobierno, '
            'con su fecha y su documento, para ver cuándo cambia o nunca llega.</p>\n'
            '  <p class="nt-prom-pasos">%s</p>\n%s\n'
            '  <p class="nt-pie">Una promesa es «oficial» porque consta que se dijo, no porque se haya gastado. Lo que todavía no tiene '
            'documento va «pendiente», con su ficha en el <a href="pendientes.html">Registro de pendientes</a>. Las mismas reglas para '
            'todos los gobiernos.</p>') % (pasos, '\n'.join(caso(p) for p in todas()))


if __name__ == '__main__':
    for p in todas():
        print(p['id'], '·', p['tit'])
        for x in p['etapas']:
            print('   %-12s %-22s %-40s %s' % (x['et'], x['fecha'], x['cifra'][:40], x['e']))
        print('   cambio:', p['cambio']['tx'])
