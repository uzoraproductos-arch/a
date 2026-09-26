#!/usr/bin/env python3
"""Integra a assets/js/audit-database.js la colección «evaluacion_sexenal»:
las cifras verificadas con las que el bloque 3 del módulo 2 compara a los
presidentes de 1988 a 2024 (crecimiento, deuda, empleo formal y fiscalización
superior).

Uso:
    python3 herramientas/integrar_evaluacion_sexenal.py

Cada cifra se capturó de su documento oficial; el extracto de la página
queda en investigaciones/fuentes-sexenal/ para que cualquiera la coteje.
Lo que aquí se calcula (promedios, diferencias, sumas por sexenio) se marca
«derivado» y dice su operación. Lo que no se pudo sostener con un documento
se queda en None y el motor lo pinta como «pendiente».

Convención de años: a cada presidente se le asignan los seis años
calendario de su mandato (Fox 2001-2006, ..., López Obrador 2019-2024). El
de López Obrador terminó el 30 de septiembre de 2024; su último año
calendario incluye tres meses del gobierno siguiente, y así se advierte.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from integrar_ambiente import BASE, insertar  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PIB_JSON = RAIZ / 'investigaciones' / 'fuentes-sexenal' / 'inegi-pibt-anual-base2018.json'
CONSULTA = '26 de septiembre de 2026'
ASF = 'https://www.asf.gob.mx/'

FUENTES = {
    'INEGI_PIBT': {
        'corto': 'INEGI, PIB trimestral, año base 2018 (serie 1993–2026)',
        'doc': 'Instituto Nacional de Estadística y Geografía, Sistema de Cuentas Nacionales de México, Producto Interno Bruto Trimestral, año base 2018, serie detallada (PIBT_2.xlsx), renglón «Producto interno bruto», columna «Anual», millones de pesos a precios de 2018. Actualización del 24 de agosto de 2026; 2023 a 2025 son cifras preliminares.',
        'url': 'https://www.inegi.org.mx/contenidos/programas/pib/2018/tabulados/ori/PIBT_2.xlsx',
        'sha256': '65a7899d4106e94ddb0612919ea45f7ce356910693a6c74526994e3eb11a5dee'},
    'ASF_IR2012': {
        'corto': 'ASF, Informe del Resultado CP 2012, Tomo Ejecutivo, p. 67',
        'doc': 'Auditoría Superior de la Federación, Informe del Resultado de la Fiscalización Superior de la Cuenta Pública 2012, Tomo Ejecutivo, cuadro «Saldo histórico de los requerimientos financieros del sector público, 2000-2012», elaborado con información de la SHCP y del INEGI (página 67 del PDF).',
        'url': ASF + 'Trans/Informes/IR2012i/Documentos/InformeEjecutivo/Tomo%20Ejecutivo%20IR%202012.pdf',
        'sha256': '4be2952a01fbc0708cd4430eb6bd9cd6cdc7be0723e426e4464c13724018d66b'},
    'ASF_IGE2022': {
        'corto': 'ASF, Informe General Ejecutivo CP 2022',
        'doc': 'Auditoría Superior de la Federación, Informe General Ejecutivo de la Cuenta Pública 2022: cuadro «Recuperaciones operadas (Cuentas Públicas 2001-2022)», cifras al 31 de enero de 2024 (p. 16 del PDF), y cuadro «Saldo histórico de los requerimientos financieros del sector público, 2016-2022», con información de la SHCP y del INEGI (p. 150).',
        'url': ASF + 'uploads/55_Informes_de_auditoria/2022_IGE_a.pdf',
        'sha256': '618073724893b909c81e38e670dccd6f52a66b5e7abc1a2801408d6886c9b836'},
    'ASF_IGE2018': {
        'corto': 'ASF, Informe General Ejecutivo CP 2018, p. 313',
        'doc': 'Auditoría Superior de la Federación, Informe General Ejecutivo de la Cuenta Pública 2018, gráfica «Total de auditorías practicadas, con base en el Programa Anual de Auditorías, Cuentas Públicas 2000-2018» (página 313 del PDF). No incluye las auditorías por mandato judicial o por denuncia.',
        'url': ASF + 'uploads/55_Informes_de_auditoria/IGE_2018_PROTEGIDO.pdf',
        'sha256': 'b69defcd67d2f4196f75940a0f6da4f1a82141c98b187590673fa216ec2bf73b'},
    'ASF_MDB': {
        'corto': 'ASF, Matrices de Datos Básicos CP 2019–2024',
        'doc': 'Auditoría Superior de la Federación, Matriz de Datos Básicos consolidada de cada Cuenta Pública, 2019 a 2024, renglón Total (la misma serie de la colección cuenta_publica_asf, con la liga y la página de cada año).',
        'url': ASF + 'Trans/Informes/IR2024c/Documentos/Matriz/MDB_Consolidado.pdf'},
    'SHCP_C4_2025': {
        'corto': 'SHCP, Comunicado 4/2025 (30 ene. 2025)',
        'doc': 'Secretaría de Hacienda y Crédito Público, Comunicado No. 4, «Informes sobre la Situación Económica, las Finanzas Públicas y la Deuda Pública al cuarto trimestre de 2024», 30 de enero de 2025: la deuda pública (SHRFSP) cerró 2024 en 51.4% del PIB.',
        'url': 'https://www.gob.mx/shcp/prensa/comunicado-no-4-informes-sobre-la-situacion-economica-las-finanzas-publicas-y-la-deuda-publica-al-cuarto-trimestre-de-2024'},
    'PRES_5IG': {
        'corto': 'Presidencia, Quinto Informe de Gobierno, Anexo Estadístico, p. 530',
        'doc': 'Presidencia de la República, Quinto Informe de Gobierno 2016-2017, Anexo Estadístico, cuadro «Asegurados trabajadores en el IMSS» (fuente: IMSS), columna diciembre (página 530 del PDF).',
        'url': 'https://framework-gb.cdn.gob.mx/quintoinforme/5IG_ANEXO_FINAL_TGM_250818.pdf',
        'sha256': '7159e585765b0d4cf027b22ce826c5d66daa2f926e18aaceba7f65efe1178f57'},
    'IMSS_008_2019': {
        'corto': 'IMSS, Comunicado 008/2019',
        'doc': 'Instituto Mexicano del Seguro Social, Comunicado No. 008/2019, «Cierra 2018 con un registro de 20 millones 79 mil 365 puestos de trabajo».',
        'url': 'https://www.imss.gob.mx/prensa/archivo/201901/008'},
    'IMSS_009_2025': {
        'corto': 'IMSS, Comunicado 009/2025',
        'doc': 'Instituto Mexicano del Seguro Social, Comunicado No. 009/2025, «Puestos de trabajo afiliados al Instituto Mexicano del Seguro Social»: 22,238,379 al 31 de diciembre de 2024.',
        'url': 'https://www.imss.gob.mx/prensa/archivo/202501/009'},
}

# Presidentes, con los años calendario que se les asignan.
MANDATOS = [
    ('salinas', 1989, 1994), ('zedillo', 1995, 2000), ('fox', 2001, 2006),
    ('calderon', 2007, 2012), ('epn', 2013, 2018), ('amlo', 2019, 2024),
]

# Saldo Histórico de los Requerimientos Financieros del Sector Público, % del
# PIB, al cierre del último año de cada sexenio. 1994: pendiente (ninguno de
# los documentos consultados trae ese año).
DEUDA = {
    2000: (30.7, 'ASF_IR2012'), 2006: (29.1, 'ASF_IR2012'), 2012: (36.8, 'ASF_IR2012'),
    2018: (44.9, 'ASF_IGE2022'), 2024: (51.4, 'SHCP_C4_2025'),
}

# Trabajadores asegurados / puestos de trabajo afiliados al IMSS al 31 de
# diciembre. La serie del anexo empieza en 1997: Salinas y Zedillo, pendientes.
EMPLEO = {
    2000: (12437760, 'PRES_5IG'), 2006: (13678492, 'PRES_5IG'), 2012: (16062043, 'PRES_5IG'),
    2018: (20079365, 'IMSS_008_2019'), 2024: (22238379, 'IMSS_009_2025'),
}

# Auditorías practicadas por la ASF, por Cuenta Pública. 2000-2018: gráfica
# del IGE 2018; 2019-2024: Matrices de Datos Básicos. La ASF nace en 2000:
# antes revisaba la Contaduría Mayor de Hacienda, sin series comparables.
AUDITORIAS = dict(zip(range(2000, 2019), [312, 355, 336, 338, 424, 627, 754, 962, 987, 945,
                                          1031, 1111, 1173, 1413, 1659, 1643, 1865, 1676, 1808]))

# Recuperaciones operadas por Cuenta Pública, millones de pesos, cifras al 31
# de enero de 2024 (IGE 2022). La ASF publica 2001-2008 en una sola cifra.
RECUP_CONJUNTA = 41091.56
RECUP = {2009: 12333.46, 2010: 11503.99, 2011: 14551.14, 2012: 18066.99, 2013: 9545.02,
         2014: 8799.80, 2015: 6367.09, 2016: 14229.87, 2017: 10943.07, 2018: 2379.30,
         2019: 1802.08, 2020: 2742.48, 2021: 3245.75, 2022: 2218.30}


def serie_asf():
    b = BASE.read_bytes().decode('utf-8')
    i = b.index('"cuenta_publica_asf"')
    j = b.index('"serie": [', i)
    fin = b.index('\r\n    ]', j)
    return json.loads(b[j + len('"serie": '):fin + len('\r\n    ]')])


def construir():
    pib = json.loads(PIB_JSON.read_text())['pib']
    pib = {int(k.rstrip('P')): (v, k.endswith('P')) for k, v in pib.items()}
    mdb = {r['cp']: r for r in serie_asf()}
    for cp, r in mdb.items():
        AUDITORIAS.setdefault(cp, r['auditorias'])
    filas = []
    for mid, a0, a1 in MANDATOS:
        f = {'id': mid, 'anios': [a0, a1]}
        # PIB: tasa media anual y acumulada entre el año previo y el último.
        if a0 - 1 in pib and a1 in pib:
            ini, fin = pib[a0 - 1][0], pib[a1][0]
            f['pib'] = {'promedio': round(((fin / ini) ** (1 / 6) - 1) * 100, 2),
                        'acumulado': round((fin / ini - 1) * 100, 2),
                        'base': a0 - 1, 'cierre': a1, 'preliminar': pib[a1][1],
                        'estado': 'derivado', 'fuente': 'INEGI_PIBT',
                        'operacion': 'Tasa media anual: (PIB %d / PIB %d)^(1/6) − 1, a precios de 2018.' % (a1, a0 - 1)}
        else:
            f['pib'] = {'estado': 'pendiente',
                        'motivo': 'La serie del INEGI año base 2018 empieza en 1993; falta el PIB de %d en una base comparable.' % (a0 - 1)}
        if a1 in DEUDA:
            v, fu = DEUDA[a1]
            f['deuda'] = {'cierre': v, 'anio': a1, 'estado': 'oficial', 'fuente': fu}
        else:
            f['deuda'] = {'estado': 'pendiente', 'motivo': 'Falta el saldo de %d en los documentos consultados.' % a1}
        if a0 - 1 in EMPLEO and a1 in EMPLEO:
            ini, fi = EMPLEO[a0 - 1], EMPLEO[a1]
            f['empleo'] = {'inicio': ini[0], 'fin': fi[0], 'creados': fi[0] - ini[0],
                           'fuentes': sorted({ini[1], fi[1]}), 'estado': 'derivado',
                           'operacion': 'Asegurados en el IMSS al 31 de diciembre de %d menos los de %d.' % (a1, a0 - 1)}
        else:
            f['empleo'] = {'estado': 'pendiente',
                           'motivo': 'La serie de asegurados del anexo estadístico empieza en 1997.'}
        cps = [a for a in range(a0, a1 + 1) if a in AUDITORIAS]
        if cps:
            f['auditorias'] = {'total': sum(AUDITORIAS[a] for a in cps), 'cuentas': [cps[0], cps[-1]],
                               'porCuenta': {str(a): AUDITORIAS[a] for a in cps}, 'estado': 'derivado',
                               'fuentes': sorted({'ASF_IGE2018' if a <= 2018 else 'ASF_MDB' for a in cps}),
                               'operacion': 'Suma de las auditorías practicadas en las Cuentas Públicas %d a %d.' % (cps[0], cps[-1])}
        else:
            f['auditorias'] = {'estado': 'no_aplica',
                               'motivo': 'La ASF se creó en 2000; antes revisaba la Contaduría Mayor de Hacienda.'}
        rc = [a for a in range(a0, a1 + 1) if a in RECUP]
        if rc:
            f['recuperaciones'] = {'mdp': round(sum(RECUP[a] for a in rc), 2), 'cuentas': [rc[0], rc[-1]],
                                   'estado': 'derivado', 'fuente': 'ASF_IGE2022',
                                   'operacion': 'Suma de las recuperaciones operadas de las Cuentas Públicas %d a %d, cifras al 31 de enero de 2024.' % (rc[0], rc[-1])}
        else:
            f['recuperaciones'] = {'estado': 'pendiente'}
        pa = [a for a in range(a0, a1 + 1) if a in mdb]
        if pa:
            f['porAclarar'] = {'mdp': round(sum(mdb[a]['porAclarar'] for a in pa) / 1e6, 1), 'cuentas': [pa[0], pa[-1]],
                               'estado': 'derivado', 'fuente': 'ASF_MDB',
                               'operacion': 'Suma del monto por aclarar de las Cuentas Públicas %d a %d.' % (pa[0], pa[-1])}
        else:
            f['porAclarar'] = {'estado': 'pendiente'}
        filas.append(f)
    # Notas de cobertura que no caben en una celda
    por = {f['id']: f for f in filas}
    por['fox']['recuperaciones'] = {'estado': 'conjunta', 'fuente': 'ASF_IGE2022',
                                    'motivo': 'La ASF publica las recuperaciones de 2001 a 2008 en una sola cifra ($41,091.6 mdp), que no separa los años de Fox de los dos primeros de Calderón.'}
    por['calderon']['recuperaciones']['nota'] = 'Solo CP 2009–2012. Las de 2007 y 2008 están dentro de la cifra conjunta 2001–2008.'
    por['amlo']['recuperaciones']['nota'] = 'Solo CP 2019–2022: las de 2023 y 2024 siguen en solventación y no estaban en el corte.'
    por['zedillo']['auditorias']['nota'] = 'Solo la Cuenta Pública 2000, primera que revisó la ASF.'
    por['zedillo']['recuperaciones'] = {'estado': 'pendiente', 'motivo': 'La serie de recuperaciones de la ASF empieza en la Cuenta Pública 2001.'}
    por['salinas']['recuperaciones'] = {'estado': 'no_aplica', 'motivo': por['salinas']['auditorias']['motivo']}
    por['salinas']['porAclarar'] = {'estado': 'no_aplica', 'motivo': por['salinas']['auditorias']['motivo']}
    por['amlo']['auditorias']['nota'] = 'La Cuenta Pública 2024 incluye octubre a diciembre, ya con el gobierno siguiente.'
    por['amlo']['porAclarar']['nota'] = 'La Cuenta Pública 2024 incluye octubre a diciembre, ya con el gobierno siguiente.'
    for mid in ('zedillo', 'fox', 'calderon', 'epn'):
        por[mid]['porAclarar'] = {'estado': 'pendiente',
                                  'motivo': 'La ASF publica el monto por aclarar con esta definición desde la Cuenta Pública 2019; antes usaba otros conceptos que no se suman con este.'}
    return {
        'consulta': CONSULTA,
        'convencion': 'A cada presidente se le asignan los seis años calendario de su mandato: Salinas 1989–1994, Zedillo 1995–2000, Fox 2001–2006, Calderón 2007–2012, Peña Nieto 2013–2018 y López Obrador 2019–2024. El cambio de gobierno ocurre el 1 de diciembre (el 1 de octubre en 2024), así que el primer y el último año se comparten unas semanas o meses con el vecino.',
        'advertencias': [
            'La deuda de 2000 a 2012 se publicó con el PIB de su momento (base 2003) y la de 2018 y 2024 con bases más recientes. Las revisiones del PIB pueden mover el cociente más de un punto: la diferencia entre Zedillo (30.7%) y Fox (29.1%) no debe leerse como definitiva.',
            'Las recuperaciones operadas crecen con el tiempo: una Cuenta Pública vieja lleva más años de solventación que una reciente. Comparar sexenios con esta cifra favorece a los antiguos.',
            'El PIB de 2023 y 2024 es preliminar.',
        ],
        'recuperacionesConjuntas': {'mdp': RECUP_CONJUNTA, 'cuentas': [2001, 2008], 'fuente': 'ASF_IGE2022'},
        'fuentes': FUENTES,
        'filas': filas,
    }


def main():
    b = BASE.read_bytes().decode('utf-8')
    b = insertar(b, 'evaluacion_sexenal', construir())
    BASE.write_bytes(b.encode('utf-8'))
    print('evaluacion_sexenal integrada')


if __name__ == '__main__':
    main()
