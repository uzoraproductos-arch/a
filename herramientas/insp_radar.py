# -*- coding: utf-8 -*-
"""Radar por entidad · Banderas rojas: las cifras de la Auditoria Superior,
estado por estado, para la ficha tecnica del Auditor de entes publicos.

Historia: fue la aplicacion 2 del Modo Inspector, con pagina propia
(12-10-2026). El 21-10-2026 (pedido del autor) paso primero a vivir dentro del
Auditor de entes publicos y, el mismo dia, se fusiono con su ficha tecnica:
ya no tiene pagina (herramienta-inspector-radar.html redirige al Auditor).
Lo que mostraba cada estado sale ahora en su ficha estatal, y el orden de
los 32 estados, en las vistas y el orden del directorio (insp-entes.js).

Este modulo solo calcula; no escribe HTML. Lee de window.AUDIT_DB:

- cuenta_publica_asf.cp2024.entidades: la Matriz de Datos Basicos de la ASF
  (CP 2024, corte febrero de 2026), pp. 19 a 23: por estado, auditorias,
  universo, muestra, acciones, PO, PRAS, recuperaciones y monto por
  aclarar, y su desglose Gobierno del Estado / Municipios (Alcaldias en la
  Ciudad de Mexico) / Otros.
- cuenta_publica_asf.acciones: que es un PO, una PRAS y una SA (LFRCF).

Los tres criterios se conservan (por cada $100 revisados, monto total, peso
de los municipios); los tres son orden, no juicio. El semaforo: rojo si por
cada $100 revisados queda al menos 1.5 veces el promedio nacional, ambar si
queda mas que el promedio, verde si menos.
"""

# Clave del estado en el Auditor de entes publicos (base['estados'][].abbr),
# por su nombre en la Matriz de la ASF.
CLAVE = {
    'Aguascalientes': 'AGS', 'Baja California': 'BC', 'Baja California Sur': 'BCS', 'Campeche': 'CAM',
    'Coahuila de Zaragoza': 'COAH', 'Colima': 'COL', 'Chiapas': 'CHIS', 'Chihuahua': 'CHIH',
    'Ciudad de México': 'CDMX', 'Durango': 'DGO', 'Guanajuato': 'GTO', 'Guerrero': 'GRO', 'Hidalgo': 'HGO',
    'Jalisco': 'JAL', 'México': 'MÉX', 'Michoacán de Ocampo': 'MICH', 'Morelos': 'MOR', 'Nayarit': 'NAY',
    'Nuevo León': 'NL', 'Oaxaca': 'OAX', 'Puebla': 'PUE', 'Querétaro': 'QRO', 'Quintana Roo': 'QROO',
    'San Luis Potosí': 'SLP', 'Sinaloa': 'SIN', 'Sonora': 'SON', 'Tabasco': 'TAB', 'Tamaulipas': 'TAM',
    'Tlaxcala': 'TLAX', 'Veracruz de Ignacio de la Llave': 'VER', 'Yucatán': 'YUC', 'Zacatecas': 'ZAC',
}

# (clave, etiqueta, icono, que mide, operacion, estado del dato)
CRITERIOS = [
    ('intensidad', 'Por cada $100 revisados', '💯',
     'Qué tanto quedó por aclarar en proporción a lo que la Auditoría revisó. Sirve para comparar estados grandes con chicos.',
     'Monto por aclarar ÷ muestra auditada del estado × 100.', 'derivado'),
    ('monto', 'Monto por aclarar', '💰',
     'Cuánto dinero, en pesos, quedó sin documentación suficiente al cierre de las auditorías. Los estados que reciben más dinero federal tienden a salir arriba.',
     'Es la cifra de la Matriz, sin operación.', 'oficial'),
    ('municipios', 'Peso de los municipios', '🏘️',
     'Qué parte de lo que quedó por aclarar en el estado le toca a sus municipios (en la Ciudad de México, a sus alcaldías). Dice si el pendiente está en el gobierno estatal o en los ayuntamientos.',
     'Monto por aclarar de los municipios ÷ monto por aclarar del estado × 100.', 'derivado'),
]

SEMAFORO = {'rojo': ('🔴', 'Bandera roja', 'al menos 1.5 veces el promedio nacional'),
            'ambar': ('🟡', 'Arriba del promedio', 'más que el promedio nacional, sin llegar a 1.5 veces'),
            'verde': ('🟢', 'Debajo del promedio', 'menos que el promedio nacional')}


def _tipo_ente(ente):
    if ente.startswith('Gobierno'):
        return 'gob'
    if ente.startswith('Municipios') or ente.startswith('Alcald'):
        return 'mun'
    return 'otr'


def _semaforo(r, prom):
    return 'rojo' if r >= prom * 1.5 else 'ambar' if r >= prom else 'verde'


def datos(C):
    """El radar para el JSON del Auditor: promedio nacional, criterios,
    semaforo, acciones y, por clave de estado, sus cifras, su desglose, sus
    tres valores y su lugar en cada criterio. Montos en pesos."""
    L = C['cp2024']['entidades']
    pa = sum(e['total']['porAclarar'] for e in L)
    mu = sum(e['total']['muestra'] for e in L)
    prom = pa / mu * 100
    est = {}
    for e in L:
        t = e['total']
        mun = sum(d['porAclarar'] for d in e['desglose'] if _tipo_ente(d['ente']) == 'mun')
        est[CLAVE[e['entidad']]] = {
            'ent': e['entidad'],
            't': [t[k] for k in ('auditorias', 'universo', 'muestra', 'acciones', 'PO', 'PRAS', 'recuperaciones', 'porAclarar')],
            'd': [[d['ente'], _tipo_ente(d['ente']), d['auditorias'], d['porAclarar'], d['acciones']] for d in e['desglose']],
            'v': [t['porAclarar'] / t['muestra'] * 100, t['porAclarar'], (mun / t['porAclarar'] * 100) if t['porAclarar'] else 0.0],
        }
    for i in range(len(CRITERIOS)):
        for n, k in enumerate(sorted(est, key=lambda k: -est[k]['v'][i]), 1):
            est[k].setdefault('l', [0] * len(CRITERIOS))[i] = n
    for x in est.values():
        x['s'] = _semaforo(x['v'][0], prom)
    f = C['fuentes']['MDB2024']
    return {
        'prom': prom, 'pa': pa, 'mu': mu,
        'fuente': {'corto': f['corto'], 'url': '%s#page=%s' % (f['url'], C['cp2024']['paginaEntidades'].split(' ')[0]),
                   'pags': C['cp2024']['paginaEntidades']},
        'nota': C['nota'].replace('Pesos corrientes. ', ''),
        'crit': [list(c) for c in CRITERIOS],
        'sem': {k: list(v) for k, v in SEMAFORO.items()},
        'acc': {a['clave']: [a['nombre'], a['que'], a['fundamento']] for a in C['acciones'] if a['clave'] in ('SA', 'PO', 'PRAS')},
        'est': est,
    }
