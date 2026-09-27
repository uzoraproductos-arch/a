"""Ancla el Ramo 28 y el Ramo 33 de las 32 entidades a los acuerdos del DOF.

La base traía cifras redondas por entidad sin documento: sumaban ,187,900 mdp
en el Ramo 28 contra ,456,045.9 del Presupuesto. Hacienda publica el reparto
en el «Acuerdo por el que se da a conocer a los gobiernos de las entidades
federativas la distribución y calendarización para la ministración, durante el
ejercicio fiscal de 2026, de los recursos correspondientes a los ramos generales
28 ... y 33 ...» (LFPRH, art. 44, párrafo cuarto):

- Ramo 28: Anexo 15 del acuerdo original, DOF 12-12-2025 (estimación de
  participaciones e incentivos; cambia con la recaudación y con los
  coeficientes de junio).
- Ramo 33: Anexo 16 en la versión que publicó la modificación del
  DOF 09-07-2026 (en materia del FASSA), la última localizada.

Las 32 entidades más los renglones sin entidad cuadran al peso con el total de
cada ramo. El campo «gasto» pasa a ser Ramo 28 + Ramo 33 (derivado) y «pc» se
recalcula con la población de la base, que sigue pendiente de fuente.

Idempotente.
    python3 herramientas/anclar_ramos_entidades.py
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from integrar_glosario_modulos import _cuerpo  # noqa: E402

BASE = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'js' / 'audit-database.js'

# Pesos, tal como los publica el DOF: (Ramo 28 Anexo 15, Ramo 33 Anexo 16).
PESOS = {
    'AGS': (15878531904, 14572718886),
    'BC': (45091482735, 24880384688),
    'BCS': (11307438617, 8885887046),
    'CAM': (10530057283, 10234672931),
    'CHIS': (55243070365, 67717196435),
    'CHIH': (45236793350, 30652267752),
    'CDMX': (142981119025, 19857543695),
    'COAH': (35151602359, 24831441263),
    'COL': (8471340421, 7731682661),
    'DGO': (20534140116, 19733156119),
    'GTO': (65936503540, 41793447100),
    'GRO': (33573141467, 49864288299),
    'HGO': (29949988285, 32413808675),
    'JAL': (96672167762, 50707498874),
    'MÉX': (194623212222, 100367466709),
    'MICH': (46853348979, 42560833968),
    'MOR': (18901233946, 16882754232),
    'NAY': (13183536752, 12382851234),
    'NL': (76530008951, 35809537223),
    'OAX': (39528949264, 56817072629),
    'PUE': (64718031019, 48274968921),
    'QRO': (28354794268, 17348256089),
    'QROO': (21954910548, 13928826121),
    'SLP': (29101467954, 26500292296),
    'SIN': (33662377920, 24662481431),
    'SON': (36980218635, 20460560991),
    'TAB': (34122502945, 19753593955),
    'TAM': (43004035997, 27802761517),
    'TLAX': (14391601767, 13585259678),
    'VER': (83582228424, 71711365342),
    'YUC': (24930430439, 18873418966),
    'ZAC': (17786868922, 16656120807),
}

TOTAL_R28 = 1456045894280
TOTAL_R33 = 1041892906925
SIN_ENTIDAD = {
    'ramo28': [
        {'n': 'No distribuible', 'pesos': 17278758099,
         'd': 'Parte de la estimación que el Anexo 15 no asigna a ninguna entidad.'},
    ],
    'ramo33': [
        {'n': 'No distribuible geográficamente', 'pesos': 39590894315,
         'd': 'Fondo de Aportaciones Múltiples 3,447.4 mdp, Fondo de Aportaciones para la Seguridad Pública ,941.2 mdp y Fondo de Aportaciones para los Servicios de Salud ,202.3 mdp (anexos 27, 34 y 22). El de seguridad pública se repartió después por acuerdo propio (DOF 20-03-2026).'},
        {'n': 'Componente indígena del FAIS', 'pesos': 13506070241,
         'd': 'Recursos del Fondo de Aportaciones para la Infraestructura Social que la Secretaría de Bienestar asigna aparte.'},
        {'n': 'Auditoría Superior de la Federación', 'pesos': 541525836,
         'd': 'Lo que la ley reserva para fiscalizar las aportaciones (Ley de Coordinación Fiscal, art. 49).'},
    ],
}

REF_NUEVAS = [
    {
        'num': 106,
        'id': 'ref-dof-distribucion-2026',
        'categoria': 'coordinacion_fiscal',
        'categoria_nombre': 'Federalismo y Coordinación Fiscal',
        'cita_apa': 'Secretaría de Hacienda y Crédito Público. (2025, 12 de diciembre). Acuerdo por el que se da a conocer a los gobiernos de las entidades federativas la distribución y calendarización para la ministración, durante el ejercicio fiscal de 2026, de los recursos correspondientes a los ramos generales 28 Participaciones a Entidades Federativas y Municipios y 33 Aportaciones Federales para Entidades Federativas y Municipios. Diario Oficial de la Federación.',
        'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5776006&fecha=12/12/2025',
        'descripcion': 'Reparte entre las 32 entidades el Ramo 28 (anexos 1 a 15) y el Ramo 33 (anexos 16 a 35) aprobados en el Presupuesto 2026, mes por mes. El Anexo 15 estima ,456,045.9 mdp de participaciones, de los que 7,278.8 mdp quedan sin distribuir. Lo ordena el artículo 44 de la Ley Federal de Presupuesto y Responsabilidad Hacendaria.',
    },
    {
        'num': 107,
        'id': 'ref-dof-distribucion-2026-mod',
        'categoria': 'coordinacion_fiscal',
        'categoria_nombre': 'Federalismo y Coordinación Fiscal',
        'cita_apa': 'Secretaría de Hacienda y Crédito Público. (2026, 9 de julio). Acuerdo por el que se modifica el diverso por el que se da a conocer a los gobiernos de las entidades federativas la distribución y calendarización para la ministración, durante el ejercicio fiscal de 2026, de los recursos correspondientes a los ramos generales 28 y 33, publicado el 12 de diciembre de 2025, y sus modificaciones del 6 de febrero y 8 de abril de 2026, en materia del Fondo de Aportaciones para los Servicios de Salud. Diario Oficial de la Federación.',
        'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5793100&fecha=09/07/2026',
        'descripcion': 'Tercera modificación del reparto de 2026, la última localizada. Asigna a las entidades parte de la previsión del FASSA que no estaba distribuida y vuelve a publicar completo el Anexo 16: ,041,892.9 mdp del Ramo 33, de los que 88,254.4 mdp van a las 32 entidades.',
    },
]


def mdp(p):
    return round(p / 1e6, 1)


def bloque_fiscal():
    campos = {
        'ramo28': {'estado': 'oficial', 'ref': 'ref-dof-distribucion-2026',
                   'fuente': 'Estimación de participaciones e incentivos 2026, Anexo 15 del acuerdo de distribución (DOF 12-12-2025)'},
        'ramo33': {'estado': 'oficial', 'ref': 'ref-dof-distribucion-2026-mod',
                   'fuente': 'Aportaciones 2026 por entidad, Anexo 16 del acuerdo de distribución en su versión modificada (DOF 09-07-2026)'},
        'gasto': {'estado': 'derivado', 'ref': 'ref-dof-distribucion-2026',
                  'fuente': 'Ramo 28 + Ramo 33 de la entidad, de los dos anexos anteriores. No incluye convenios ni el Ramo 25'},
        'pc': {'estado': 'pendiente',
               'fuente': 'Ramos 28 y 33 entre la población de la entidad. La división es derivada, pero la población por entidad aún no tiene su cuadro oficial citado'},
        'pob': {'estado': 'pendiente',
                'fuente': 'Población por entidad de la base; falta citar el cuadro de las proyecciones del CONAPO, cuya base abierta no resultó accesible'},
        'convenios': {'estado': 'pendiente',
                      'fuente': 'Convenios por entidad sin documento citado; el acuerdo de distribución no los incluye'},
        'recaudacionPropia': {'estado': 'pendiente',
                              'fuente': 'Recaudación propia por entidad sin documento citado (la fuente natural son las finanzas públicas estatales del INEGI)'},
        'dep': {'estado': 'pendiente',
                'fuente': 'Porcentaje de dependencia federal sin documento citado'},
    }
    return {
        'ejercicio': 2026,
        'nota': 'Las cifras por entidad del Ramo 28 y del Ramo 33 salen de los anexos del acuerdo de distribución que Hacienda publica en el Diario Oficial. Sumadas a los renglones que el acuerdo no asigna a ninguna entidad, cuadran al peso con el total aprobado de cada ramo.',
        'campos': campos,
        'totales': {'ramo28': round(TOTAL_R28 / 1e6, 6), 'ramo33': round(TOTAL_R33 / 1e6, 6)},
        'sinEntidad': {k: [{'n': x['n'], 'mdp': round(x['pesos'] / 1e6, 6), 'd': x['d']} for x in v] for k, v in SIN_ENTIDAD.items()},
    }


def main():
    for k, tot in (('ramo28', TOTAL_R28), ('ramo33', TOTAL_R33)):
        i = 0 if k == 'ramo28' else 1
        s = sum(v[i] for v in PESOS.values()) + sum(x['pesos'] for x in SIN_ENTIDAD[k])
        if s != tot:
            sys.exit('%s no cuadra: %d contra %d' % (k, s, tot))
    b = BASE.read_bytes().decode('utf-8')
    ini = b.index('\r\n  "estados": [')
    cambios = 0
    for abbr, (p28, p33) in PESOS.items():
        a = b.index('"abbr": "%s",' % abbr, ini)
        z = b.index('"gobernador"', a)
        seg = b[a:z]
        pob = float(re.search(r'"pob": ([\d.]+),', seg).group(1))
        r28, r33 = mdp(p28), mdp(p33)
        gasto = round(r28 + r33, 1)
        nuevos = {'gasto': gasto, 'ramo28': r28, 'ramo33': r33, 'pc': round(gasto / pob)}
        nseg = seg
        for campo, v in nuevos.items():
            nseg = re.sub(r'"%s": [\d.]+,' % campo, '"%s": %s,' % (campo, json.dumps(v)), nseg, count=1)
        if nseg != seg:
            b = b[:a] + nseg + b[z:]
            cambios += 1
    bloque = json.dumps(bloque_fiscal(), ensure_ascii=False, indent=2)
    bloque = '  "fiscalEntidades": ' + bloque.replace('\n', '\r\n  ') + ','
    if '"fiscalEntidades"' in b:
        a = b.index('  "fiscalEntidades": ')
        z = b.index('\r\n  "estados": [', a)
        b = b[:a] + bloque + b[z:]
    else:
        b = b[:ini] + '\r\n' + bloque + b[ini:]
    fichas = 0
    ancla = b.index('"id": "ref-subsidio-empleo-2026"')
    corte = b.index('\r\n    }', ancla) + len('\r\n    }')
    for ref in reversed(REF_NUEVAS):
        if '"id": "%s"' % ref['id'] not in b:
            b = b[:corte] + ',\r\n' + _cuerpo(ref) + b[corte:]
            fichas += 1
    BASE.write_bytes(b.encode('utf-8'))
    print('entidades: %d renglones anclados al DOF; %d fichas nuevas' % (cambios, fichas))


if __name__ == '__main__':
    main()
