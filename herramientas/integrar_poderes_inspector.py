#!/usr/bin/env python3
"""Abre en el Modo Inspector los órganos de los poderes Legislativo y Judicial.

Las auditorías tocan a los tres niveles de gobierno y a los tres poderes. El
nivel federal del inspector tenía a cada poder como un solo ramo; aquí se abre
cada órgano que tiene presupuesto propio (unidad responsable de Hacienda):

- Legislativo (Ramo 01): Cámara de Diputados, Cámara de Senadores y Auditoría
  Superior de la Federación.
- Judicial (Ramo 03): Suprema Corte de Justicia de la Nación, Consejo de la
  Judicatura Federal / Órgano de Administración Judicial, Tribunal Electoral y
  Tribunal de Disciplina Judicial.

De cada uno: Cuenta Pública 2024 y 2025 y avance de 2026 (SHCP, datos
abiertos), las auditorías de la ASF a su nombre (Matriz de Datos Básicos de la
CP 2024, p. 31) y, cuando hay dos documentos oficiales sobre el mismo dinero,
el cotejo entre ellos (INEGI, la propia SCJN).

También deja, por entidad, lo que ejerció en 2024 el Poder Judicial de cada
estado (INEGI, CNIJF-E 2025, gráfica 7, p. 14). Lo de los congresos locales ya
está en `poderes.legislativo.congresos2024`.

    python3 herramientas/integrar_poderes_inspector.py CP2024.csv CP2025.csv AVANCE_2T_2026.csv

Escribe el bloque `inspector_poderes` de la base (idempotente) y las fichas
114 a 118 de la bibliografía. No toca `inspector_federal`: si se vuelve a
correr integrar_inspector_federal.py, este bloque sigue valiendo.
"""
import collections
import csv
import hashlib
import io
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from integrar_glosario_modulos import _cuerpo  # noqa: E402

BASE = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'js' / 'audit-database.js'
SHA_CP24 = '94cd87dfb1f0dbcb27886d5792046c9c6d96eeab2878f898c8a9813ef1fdf6de'
SHA_CP25 = '973aab21969233bdfad3c4f87ccd467ab92421ea5c2cd249644c0bf2f7f1d0c0'
SHA_AV = 'faa3a3de57981aa117828d2569aa5c8144db11e3f8d290e68d97aaf73467c511'
SHA_MDB = '49732c8da82eaafc6bdd67b0b0ce5c995773294d7e48e5412ad73e5c4fe15d66'
SHA_CNIJ = '5dfdd93b437885a370fb9f03d988b99ba191be16986828ab4be008709881dee3'
URL_CNIJ = 'https://www.inegi.org.mx/contenidos/programas/cnije/2025/doc/cnije_2025_resultados.pdf'
URL_SCJN25 = 'https://www.scjn.gob.mx/sites/default/files/presupuesto%20asignado/documento/2026-01/Estado-Analitico-Ejercicio-Presupuesto-2025-Trim-04.pdf'
URL_SCJN26 = 'https://www.scjn.gob.mx/sites/default/files/presupuesto%20asignado/documento/2026-07/Estado-Analitico-Ejercicio-Presupuesto-2026-Trim-02.pdf'
URL_NL = 'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Auditorias/2024_1402_a.pdf'
URL_TLX = 'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Auditorias/2024_1940_a.pdf'

# A qué poder pertenece cada ente del nivel federal. Los tribunales Agrario
# y de Justicia Administrativa no forman parte del Poder Judicial de la
# Federación (arts. 27 fr. XIX y 73 fr. XXIX-H de la Constitución): se agrupan
# con los autónomos.
PODER = {
    'legislativo': 'legislativo', 'judicial': 'judicial',
    'ine': 'autonomo', 'cndh': 'autonomo', 'inegi': 'autonomo', 'cofece': 'autonomo', 'ift': 'autonomo',
    'inai': 'autonomo', 'fgr': 'autonomo', 'tribunales-agrarios': 'autonomo', 'tfja': 'autonomo',
}

# Auditorías de la ASF a cada órgano, transcritas de la Matriz de Datos
# Básicos de la CP 2024 (p. 31). Miles de pesos en el documento; aquí pesos.
# res = [resultados con observación solventada o atendida, con observaciones y acciones]
# acc = [R, RD, PEFCF, SA, PRAS, PO, total]
MDB = {
    'diputados': [dict(num=31, titulo='Gestión Financiera', tipo='De Cumplimiento', entrega=2, repr=95.66,
                       res=[0, 0], acc=[0, 0, 0, 0, 0, 0, 0], recuperaciones=0.0, porAclarar=0.0)],
    'senado': [dict(num=32, titulo='Gestión Financiera', tipo='De Cumplimiento', entrega=2, repr=85.28,
                    res=[2, 0], acc=[0, 0, 0, 0, 0, 0, 0], recuperaciones=0.0, porAclarar=0.0)],
    'scjn': [dict(num=425, titulo='Gestión Financiera', tipo='De Cumplimiento', entrega=1, repr=92.81,
                  res=[3, 0], acc=[0, 0, 0, 0, 0, 0, 0], recuperaciones=8133.3, porAclarar=0.0)],
    'oaj': [dict(num=108, titulo='Erogaciones por Adquisición de Bienes y Prestación de Servicios',
                 tipo='De Cumplimiento Forense', entrega=2, repr=30.83,
                 res=[0, 5], acc=[11, 0, 1, 0, 11, 11, 34], recuperaciones=0.0, porAclarar=272437.5)],
    'tepjf': [dict(num=430, titulo='Erogaciones por Adquisición de Bienes y Prestación de Servicios',
                   tipo='De Cumplimiento Forense', entrega=3, repr=31.24,
                   res=[0, 7], acc=[5, 0, 4, 0, 5, 6, 20], recuperaciones=0.0, porAclarar=12137.4)],
}
# El subtotal de la Matriz para el sector «Poder Judicial» (p. 31): se
# comprueba que la transcripción cuadra con él.
SUBTOTAL_JUDICIAL = dict(acciones=54, PO=17, recuperaciones=8133.3, porAclarar=284574.8)

# Presupuesto ejercido en 2024 según el INEGI (CNIJF-E 2025, gráfica 6, p. 13),
# millones de pesos corrientes. El INEGI advierte que el del CJF incluye al
# Instituto Federal de Defensoría Pública y el del TEPJF a la Defensoría
# Pública Electoral.
CNIJF = {'scjn': 5665.8, 'tepjf': 3625.7, 'oaj': 72090.0}

# Poderes Judiciales estatales, 2024 (CNIJF-E 2025, gráfica 7, p. 14), en el
# orden de la gráfica. Deben sumar 53,516.3 (gráfica 6, p. 13).
PJE = [('CDMX', 8222.6), ('MÉX', 6196.8), ('CHIH', 3370.9), ('NL', 3130.2), ('JAL', 2533.8), ('GTO', 2290.6),
       ('VER', 2193.9), ('BC', 1950.8), ('PUE', 1744.4), ('SON', 1693.2), ('MICH', 1649.0), ('QRO', 1608.9),
       ('COAH', 1500.2), ('SLP', 1321.5), ('OAX', 1171.9), ('CHIS', 1167.1), ('TAM', 1155.2), ('GRO', 1065.7),
       ('MOR', 951.8), ('QROO', 891.2), ('TAB', 882.5), ('YUC', 855.6), ('SIN', 851.3), ('AGS', 772.9),
       ('HGO', 761.0), ('NAY', 669.1), ('ZAC', 656.1), ('TLAX', 563.7), ('DGO', 542.4), ('BCS', 507.6),
       ('CAM', 333.3), ('COL', 311.1)]
PJE_TOTAL = 53516.3

# Lo que la SCJN publica de sí misma (estado analítico del ejercicio), en
# pesos; ya transcrito en `poderes.judicial.scjnCortes`, p. 1 de cada informe.
SCJN_PROPIO = {
    '2025': dict(modificado=5273784802, devengado=5273784802, pagado=5032120580),
    '2026-06': dict(modificado=5208743404, devengado=2503691579, pagado=2101258527),
}

# (id, padre, ramo, unidades, nombre, icono, tipo)
ORGANOS = [
    ('diputados', 'legislativo', '1', ['100'], 'Cámara de Diputados', '🏛️', 'Órgano del Poder Legislativo · UR 100'),
    ('senado', 'legislativo', '1', ['200'], 'Cámara de Senadores', '🏛️', 'Órgano del Poder Legislativo · UR 200'),
    ('asf', 'legislativo', '1', ['101'], 'Auditoría Superior de la Federación', '🔍', 'Órgano técnico de la Cámara de Diputados · UR 101'),
    ('scjn', 'judicial', '3', ['100'], 'Suprema Corte de Justicia de la Nación', '⚖️', 'Órgano del Poder Judicial · UR 100'),
    ('oaj', 'judicial', '3', ['110', '120'], 'Órgano de Administración Judicial (antes Consejo de la Judicatura Federal)', '🏢',
     'Órgano del Poder Judicial · UR 110 y 120'),
    ('tepjf', 'judicial', '3', ['210', '211'], 'Tribunal Electoral del Poder Judicial de la Federación', '🗳️',
     'Órgano del Poder Judicial · UR 210 y 211'),
    ('tdj', 'judicial', '3', ['300'], 'Tribunal de Disciplina Judicial', '📜', 'Órgano del Poder Judicial · UR 300'),
]

NOTAS = {
    'oaj': 'La reforma judicial publicada en el DOF el 15 de septiembre de 2024 extinguió al Consejo de la Judicatura Federal y repartió sus funciones entre el Órgano de Administración Judicial y el Tribunal de Disciplina Judicial. En la Cuenta Pública 2025 conviven las dos unidades: la 110 (el Consejo, mientras existió) y la 120 (el Órgano). Aquí se suman para no partir en dos el mismo aparato administrativo.',
    'tepjf': 'Suma de la Sala Superior (UR 210) y las Salas Regionales (UR 211).',
    'tdj': 'Nació con la reforma judicial de 2024 y empezó a operar en 2025: no tiene gasto en la Cuenta Pública 2024 ni, por lo tanto, auditorías de la ASF sobre ese año.',
    'asf': 'La ASF no se audita a sí misma. La ley encarga revisar su gasto a la Unidad de Evaluación y Control de la Comisión de Vigilancia de la Cámara de Diputados, que puede practicar auditorías por sí o con auditores externos (art. 104, fr. II, de la Ley de Fiscalización y Rendición de Cuentas de la Federación).',
}

REF_NUEVAS = [
    {
        'num': 114,
        'id': 'ref-inegi-cnijfe2025-rr',
        'categoria': 'judicial',
        'categoria_nombre': 'Poder Judicial & SCJN',
        'cita_apa': 'Instituto Nacional de Estadística y Geografía. (2025, 6 de noviembre). Censo Nacional de Impartición de Justicia Federal y Estatal (CNIJF-E) 2025: reporte de resultados 43/25. INEGI.',
        'url': URL_CNIJ,
        'descripcion': 'Presupuesto que ejercieron en 2024 la Suprema Corte ($5,665.8 millones), el Tribunal Electoral ($3,625.7 millones) y el Consejo de la Judicatura Federal ($72,090.0 millones), en la gráfica 6 (p. 13), y el de cada uno de los 32 poderes judiciales estatales, que suman $53,516.3 millones, en la gráfica 7 (p. 14). Lo reporta cada órgano al INEGI. Huella SHA-256 del archivo: ' + SHA_CNIJ + '.',
    },
    {
        'num': 115,
        'id': 'ref-scjn-cierre2025',
        'categoria': 'judicial',
        'categoria_nombre': 'Poder Judicial & SCJN',
        'cita_apa': 'Suprema Corte de Justicia de la Nación. (2026). Estado analítico del ejercicio del presupuesto de egresos, enero-diciembre de 2025. SCJN.',
        'url': URL_SCJN25,
        'descripcion': 'El cierre de 2025 que publica la propia Corte, por capítulo de gasto: $5,273.8 millones modificados y devengados y $5,032.1 millones pagados (p. 1). Coincide peso por peso con lo que Hacienda consolidó en la Cuenta Pública.',
    },
    {
        'num': 116,
        'id': 'ref-scjn-trim2-2026',
        'categoria': 'judicial',
        'categoria_nombre': 'Poder Judicial & SCJN',
        'cita_apa': 'Suprema Corte de Justicia de la Nación. (2026). Estado analítico del ejercicio del presupuesto de egresos, enero-junio de 2026. SCJN.',
        'url': URL_SCJN26,
        'descripcion': 'Lo que la Corte reporta haber devengado ($2,503.7 millones) y pagado ($2,101.3 millones) en el primer semestre de 2026 (p. 1). Hacienda, con el mismo corte, le registra $1,939.1 millones pagados.',
    },
    {
        'num': 117,
        'id': 'ref-asf-cp2024-congreso-nl',
        'categoria': 'fiscalizacion_auditoria',
        'categoria_nombre': 'Fiscalización Superior y Auditoría',
        'cita_apa': 'Auditoría Superior de la Federación. Informe individual de la auditoría 2024-1402: Congreso del Estado de Nuevo León. Fiscalización Superior de la Cuenta Pública 2024, tercera entrega.',
        'url': URL_NL,
        'descripcion': 'Revisión de las participaciones federales que ejerció el Congreso de Nuevo León en 2024: universo y muestra de $233.0 millones (p. 1) y $4.5 millones por aclarar (p. 26).',
    },
    {
        'num': 118,
        'id': 'ref-asf-cp2024-congreso-tlax',
        'categoria': 'fiscalizacion_auditoria',
        'categoria_nombre': 'Fiscalización Superior y Auditoría',
        'cita_apa': 'Auditoría Superior de la Federación. Informe individual de la auditoría 2024-1940: Congreso del Estado de Tlaxcala. Fiscalización Superior de la Cuenta Pública 2024, tercera entrega.',
        'url': URL_TLX,
        'descripcion': 'Revisión de las participaciones federales que ejerció el Congreso de Tlaxcala en 2024: universo y muestra de $151.9 millones (p. 1) y $5.0 millones recuperados, con cargas financieras (p. 29).',
    },
]


def num(x):
    x = (x or '').strip().replace(',', '')
    return float(x) if x not in ('', '-') else 0.0


def leer(ruta, sha):
    datos = pathlib.Path(ruta).read_bytes()
    h = hashlib.sha256(datos).hexdigest()
    if h != sha:
        sys.exit('%s: la huella no coincide (%s)' % (ruta, h))
    try:
        return datos.decode('utf-8-sig')
    except UnicodeDecodeError:
        return datos.decode('latin-1')


def mdp(p):
    return round(p / 1e6, 1)


def por_ur(texto, ramo, ur, cols):
    """Suma, por (ramo, unidad), las columnas pedidas."""
    r = csv.reader(io.StringIO(texto))
    cab = [c.strip() for c in next(r)]
    i = {c: k for k, c in enumerate(cab)}
    tot = collections.defaultdict(lambda: [0.0] * len(cols))
    for f in r:
        if f[i[ramo]].strip() not in ('1', '3'):
            continue
        t = tot[(f[i[ramo]].strip(), f[i[ur]].strip())]
        for k, c in enumerate(cols):
            t[k] += num(f[i[c]])
    return tot


def suma(tot, ramo, urs):
    v = None
    for u in urs:
        x = tot.get((ramo, u))
        if x is None:
            continue
        v = x[:] if v is None else [a + b for a, b in zip(v, x)]
    return v


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    cp24 = por_ur(leer(sys.argv[1], SHA_CP24), 'ID_RAMO', 'ID_UR',
                  ('MONTO_APROBADO', 'MONTO_MODIFICADO', 'MONTO_DEVENGADO', 'MONTO_PAGADO', 'MONTO_EJERCIDO'))
    cp25 = por_ur(leer(sys.argv[2], SHA_CP25), 'R', 'UR',
                  ('Original_Bruto', 'Modificado_Bruto', 'Devengado', 'Pagado', 'Ejercido_Bruto'))
    av = por_ur(leer(sys.argv[3], SHA_AV), 'ID_RAMO', 'ID_UR',
                ('MONTO_APROBADO', 'MONTO_MODIFICADO', 'MONTO_MODIFICADO_MENSUAL', 'MONTO_PAGADO'))

    sub = collections.Counter()
    for k in ('scjn', 'oaj', 'tepjf'):
        for a in MDB[k]:
            sub['acciones'] += a['acc'][6]
            sub['PO'] += a['acc'][5]
            sub['recuperaciones'] += a['recuperaciones']
            sub['porAclarar'] += a['porAclarar']
    for k, v in SUBTOTAL_JUDICIAL.items():
        if abs(sub[k] - v) > 0.15:
            sys.exit('La transcripción de la Matriz no cuadra con el subtotal del Poder Judicial: %s %s contra %s' % (k, sub[k], v))
    if abs(sum(v for _, v in PJE) - PJE_TOTAL) > 0.05 or len({a for a, _ in PJE}) != 32:
        sys.exit('Los poderes judiciales estatales no suman %s' % PJE_TOTAL)

    organos = []
    for ident, padre, ramo, urs, nombre, icono, tipo in ORGANOS:
        c25 = suma(cp25, ramo, urs)
        c24 = suma(cp24, ramo, urs)
        a26 = suma(av, ramo, urs)
        o = {'id': ident, 'padre': padre, 'poder': padre, 'ramo': ramo.zfill(2), 'ur': urs, 'nombre': nombre,
             'icono': icono, 'tipo': tipo,
             'cp2025': dict(zip(('original', 'modificado', 'devengado', 'pagado', 'ejercido'), map(mdp, c25))),
             'av2026': dict(zip(('aprobado', 'modificado', 'calendarioAlCorte', 'pagado'), map(mdp, a26))) if a26 else None,
             'cp2024': dict(zip(('original', 'modificado', 'devengado', 'pagado', 'ejercido'), map(mdp, c24))) if c24 else None,
             'asf': [dict(a, recuperaciones=round(a['recuperaciones'] * 1000, 1), porAclarar=round(a['porAclarar'] * 1000, 1))
                     for a in MDB.get(ident, [])]}
        if ident in NOTAS:
            o['nota'] = NOTAS[ident]
        if ident == 'asf':
            o['asfNoAplica'] = 'uec'
        if ident == 'tdj':
            o['asfNoAplica'] = 'nuevo'
        coteja = []
        if ident in CNIJF and c24:
            coteja.append({'tema': 'Gasto ejercido en 2024', 'a': ['Cuenta Pública 2024 (Hacienda)', mdp(c24[4]), 'cp2024'],
                           'b': ['Censo del INEGI (lo reporta el propio órgano)', CNIJF[ident], 'cnijf'], 'tol': 0.15,
                           'nota': {'oaj': 'El INEGI advierte que su cifra incluye al Instituto Federal de Defensoría Pública. En la Cuenta Pública el Ramo 03 de 2024 sólo tiene cuatro unidades y el Instituto no aparece por separado: su gasto ya está dentro del del Consejo, así que no explica la diferencia.',
                                    'tepjf': 'El INEGI incluye a la Defensoría Pública Electoral; la Cuenta Pública la trae dentro de las dos unidades del Tribunal.'}.get(ident, '')})
        if ident == 'scjn':
            p = SCJN_PROPIO['2025']
            coteja.append({'tema': 'Pagado en 2025', 'a': ['Cuenta Pública 2025 (Hacienda)', mdp(c25[3]), 'cp2025'],
                           'b': ['Estado analítico de la propia Corte, enero-diciembre', mdp(p['pagado']), 'scjn2025'], 'tol': 0.15, 'nota': ''})
            coteja.append({'tema': 'Devengado en 2025', 'a': ['Cuenta Pública 2025 (Hacienda)', mdp(c25[2]), 'cp2025'],
                           'b': ['Estado analítico de la propia Corte, enero-diciembre', mdp(p['devengado']), 'scjn2025'], 'tol': 0.15, 'nota': ''})
            p = SCJN_PROPIO['2026-06']
            coteja.append({'tema': 'Pagado de enero a junio de 2026', 'a': ['Avance del gasto de Hacienda al 30 de junio', mdp(a26[3]), 'av2026'],
                           'b': ['Estado analítico de la propia Corte, enero-junio', mdp(p['pagado']), 'scjn2026'], 'tol': 0.15,
                           'nota': 'Hacienda consolida lo que cada ente le reporta y puede registrar un pago en una fecha distinta a la del ente. Aun así, el corte es el mismo: la Corte debería poder conciliar las dos cifras.'})
        if coteja:
            o['cotejos'] = coteja
        organos.append(o)

    bloque = {
        'nota': 'Órganos de los poderes Legislativo y Judicial con presupuesto propio, abiertos como entes del Modo Inspector. Millones de pesos, sumados por unidad responsable desde los datos abiertos de Hacienda; auditorías de la ASF transcritas de la Matriz de Datos Básicos de la CP 2024 (p. 31), en pesos.',
        'fuentes': {
            'cp2024': {'ref': 'ref-shcp-cp2024-datos', 'corto': 'SHCP, Cuenta Pública 2024, datos abiertos', 'sha256': SHA_CP24},
            'cp2025': {'ref': 'ref-shcp-cp2025-datos', 'corto': 'SHCP, Cuenta Pública 2025, datos abiertos', 'sha256': SHA_CP25},
            'av2026': {'ref': 'ref-shcp-avance-2t2026', 'corto': 'SHCP, avance del gasto al 2.º trimestre de 2026', 'sha256': SHA_AV},
            'asf2024': {'ref': 'ref-asf-mdb2024', 'corto': 'ASF, Matriz de Datos Básicos CP 2024, p. 31', 'sha256': SHA_MDB},
            'cnijf': {'ref': 'ref-inegi-cnijfe2025-rr', 'corto': 'INEGI, CNIJF-E 2025, p. 13', 'sha256': SHA_CNIJ},
            'cnije': {'ref': 'ref-inegi-cnijfe2025-rr', 'corto': 'INEGI, CNIJF-E 2025, p. 14', 'sha256': SHA_CNIJ},
            'cnple': {'ref': 'ref-inegi-cnple2025', 'corto': 'INEGI, CNPLE 2025, p. 11'},
            'scjn2025': {'ref': 'ref-scjn-cierre2025', 'corto': 'SCJN, estado analítico enero-diciembre 2025, p. 1'},
            'scjn2026': {'ref': 'ref-scjn-trim2-2026', 'corto': 'SCJN, estado analítico enero-junio 2026, p. 1'},
            'lfrcf': {'ref': 'ref-lfrcf', 'corto': 'Ley de Fiscalización y Rendición de Cuentas de la Federación, art. 104'},
            'asfCongresos': {'Congreso de Nuevo León': 'ref-asf-cp2024-congreso-nl', 'Congreso de Tlaxcala': 'ref-asf-cp2024-congreso-tlax'},
        },
        'poderDeEnte': PODER,
        'organos': organos,
        'judicialesEstatales2024': dict(PJE),
    }

    b = BASE.read_bytes().decode('utf-8')
    texto = '  "inspector_poderes": ' + json.dumps(bloque, ensure_ascii=False, indent=1).replace('\n', '\r\n  ') + ','
    if '"inspector_poderes":' in b:
        a = b.index('  "inspector_poderes": ')
        z = b.index('\r\n  "', a + 10)
        b = b[:a] + texto + b[z:]
    else:
        a = b.index('\r\n  "estados": [')
        b = b[:a] + '\r\n' + texto + b[a:]
    fichas = 0
    for ref in reversed(REF_NUEVAS):
        marca = '"id": "%s"' % ref['id']
        if marca in b:
            i = b.index(marca)
            ini = b.rindex('\r\n    {\r\n', 0, i) + 2
            fin = b.index('\r\n    }', i) + len('\r\n    }')
            b = b[:ini] + _cuerpo(ref) + b[fin:]
            continue
        ancla = b.index('"id": "ref-inafed-presidencias"')
        corte = b.index('\r\n    }', ancla) + len('\r\n    }')
        b = b[:corte] + ',\r\n' + _cuerpo(ref) + b[corte:]
        fichas += 1
    BASE.write_bytes(b.encode('utf-8'))

    print('órganos: %d; fichas nuevas: %d' % (len(organos), fichas))
    for o in organos:
        c = o['cp2025']
        print('  %-10s ejercido 2025 %10.1f  2024 %10s  ASF %d' % (o['id'], c['ejercido'],
              o['cp2024']['ejercido'] if o['cp2024'] else '—', len(o['asf'])))
        for x in o.get('cotejos', []):
            print('     %-34s %10.1f  %10.1f  dif %+.1f' % (x['tema'], x['a'][1], x['b'][1], x['b'][1] - x['a'][1]))


if __name__ == '__main__':
    main()
