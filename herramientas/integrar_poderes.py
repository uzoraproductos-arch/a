#!/usr/bin/env python3
"""Integra a window.AUDIT_DB la coleccion "poderes": presupuesto y ejercicio
del Poder Legislativo y del Poder Judicial de la Federacion, y las
remuneraciones oficiales que usa el comparador "Tu vs Ellos" (2.4 B).

Fuentes de entrada, todas en el repositorio:
  investigaciones/Auditavision_Poder_Judicial_2026.xlsx
  investigaciones/Auditavision_Desglose_2024.xlsx
  y las cifras del Decreto PEF 2026 (DOF 21-11-2025) transcritas abajo con
  su anexo y su pagina del DOF.

Uso (desde la raiz del repositorio):
  python3 herramientas/integrar_poderes.py

Es idempotente: si la coleccion ya existe, la reemplaza. Conserva los CRLF
de audit-database.js. Solo modifica esa coleccion.
"""
import json
import pathlib
import sys

import openpyxl

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BASE = RAIZ / 'assets' / 'js' / 'audit-database.js'
XLS_PJF = RAIZ / 'investigaciones' / 'Auditavision_Poder_Judicial_2026.xlsx'
XLS_2024 = RAIZ / 'investigaciones' / 'Auditavision_Desglose_2024.xlsx'

CONSULTA = '2026-09-25'

# ---------------------------------------------------------------------------
# Catalogo de documentos. Clave corta -> documento, URL y, cuando se conoce,
# la huella SHA-256 del archivo descargado.
# ---------------------------------------------------------------------------
FUENTES = {
    'CP2025': {
        'corto': 'Cuenta Pública 2025, datos abiertos SHCP',
        'doc': 'SHCP, Cuenta Pública 2025, base de datos abierta de ramos administrativos, generales y autónomos (Transparencia Presupuestaria)',
        'url': 'https://www.transparenciapresupuestaria.gob.mx/work/models/PTP/DatosAbiertos/BD_Cuenta_Publica/CSV/cuenta_publica_2025_gf_ecd_epe.csv',
        'sha256': '973aab21969233bdfad3c4f87ccd467ab92421ea5c2cd249644c0bf2f7f1d0c0'},
    'AV2T2026': {
        'corto': 'SHCP, avance del gasto al 2.º trimestre 2026',
        'doc': 'SHCP, Presupuesto de Egresos 2026, avance del gasto (AC01) al segundo trimestre, base de datos abierta (Transparencia Presupuestaria)',
        'url': 'https://www.transparenciapresupuestaria.gob.mx/work/models/PTP/DatosAbiertos/Bases_de_datos_presupuesto/CSV/pef_ac01_avance_2t_2026.csv',
        'sha256': 'faa3a3de57981aa117828d2569aa5c8144db11e3f8d290e68d97aaf73467c511'},
    'PEF': {
        'corto': 'PEF 2026, DOF 21-11-2025',
        'doc': 'Decreto de Presupuesto de Egresos de la Federación 2026, DOF 21-11-2025 (edición vespertina)',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/ref/pef_2026/PEF_2026_orig_21nov25.pdf',
        'sha256': '6db4a86b588a0f76928e5d61298579c4aff2c29c3ace68fdedbfa5afceb8f2bc'},
    'UR': {
        'corto': 'SHCP, Ramo 03 por unidad responsable',
        'doc': 'PEF 2026, Ramo 03, análisis administrativo económico (SHCP, enero 2026)',
        'url': 'https://www.pef.hacienda.gob.mx/work/models/P3f26115/PEF2026/y6k1r4r1/docs/03/r03_aae.pdf'},
    'COG': {
        'corto': 'SHCP, Ramo 03 por capítulo y concepto',
        'doc': 'PEF 2026, Ramo 03, distribución por unidad responsable, capítulo y concepto (SHCP, enero 2026)',
        'url': 'https://www.comunicacionpef.hacienda.gob.mx/work/models/COMUNICACION_DEL_PEF/Documentos/2026/distribucion_gasto_UR/r03_apurog.pdf'},
    'SCJN_AGO': {
        'corto': 'SCJN, ejercicio al 31-08-2026',
        'doc': 'SCJN, estado del ejercicio del presupuesto al 31 de agosto de 2026',
        'url': 'https://www.scjn.gob.mx/sites/default/files/presupuesto-asignado/documento/2026-09/EEP-2026-08.pdf'},
    'SCJN_JUN': {
        'corto': 'SCJN, enero-junio 2026',
        'doc': 'SCJN, estado analítico del ejercicio del presupuesto, enero-junio 2026',
        'url': 'https://www.scjn.gob.mx/sites/default/files/presupuesto%20asignado/documento/2026-07/Estado-Analitico-Ejercicio-Presupuesto-2026-Trim-02.pdf'},
    'SCJN_2025': {
        'corto': 'SCJN, cierre 2025',
        'doc': 'SCJN, estado analítico del ejercicio del presupuesto, enero-diciembre 2025',
        'url': 'https://www.scjn.gob.mx/sites/default/files/presupuesto%20asignado/documento/2026-01/Estado-Analitico-Ejercicio-Presupuesto-2025-Trim-04.pdf'},
    'MANUAL': {
        'corto': 'Manual de remuneraciones PJF 2026, DOF 27-02-2026',
        'doc': 'Manual de remuneraciones de las personas servidoras públicas del Poder Judicial de la Federación 2026, DOF 27-02-2026',
        'url': 'https://apps.cjf.gob.mx/normativa/Recursos/2026-0-6-OAJ_V01.PDF'},
    'OAJ_CAP': {
        'corto': 'OAJ, 2.º trimestre 2026 por capítulo',
        'doc': 'OAJ, presupuesto ejercido por capítulo, segundo trimestre 2026 (1 de abril a 30 de junio)',
        'url': 'https://www.cjf.gob.mx/transparencia/resources/Presupuestoejercido/cierremensual/2026/Cierre_Transparencia_2Trim_2026_archivos/sheet001.htm'},
    'OAJ_UEG': {
        'corto': 'OAJ, 2.º trimestre 2026 por unidad',
        'doc': 'OAJ, pagos por unidad ejecutora, segundo trimestre 2026',
        'url': 'https://www.cjf.gob.mx/transparencia/resources/Presupuestoejercido/cierremensual/2026/Cierre_Transparencia_2Trim_2026_archivos/sheet007.htm'},
    'ASF_DIP': {
        'corto': 'ASF, auditoría 31 (Diputados)',
        'doc': 'ASF, Cuenta Pública 2024, auditoría 31: Cámara de Diputados (segunda entrega)',
        'url': 'https://www.asf.gob.mx/Trans/Informes/IR2024b/Documentos/Auditorias/2024_0031_a.pdf'},
    'ASF_SEN': {
        'corto': 'ASF, auditoría 32 (Senado)',
        'doc': 'ASF, Cuenta Pública 2024, auditoría 32: Cámara de Senadores (segunda entrega)',
        'url': 'https://www.asf.gob.mx/Trans/Informes/IR2024b/Documentos/Auditorias/2024_0032_a.pdf'},
    'ASF_NL': {
        'corto': 'ASF, auditoría 1402 (Congreso de NL)',
        'doc': 'ASF, Cuenta Pública 2024, auditoría 1402: Congreso de Nuevo León (tercera entrega)',
        'url': 'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Auditorias/2024_1402_a.pdf'},
    'ASF_TLX': {
        'corto': 'ASF, auditoría 1940 (Congreso de Tlaxcala)',
        'doc': 'ASF, Cuenta Pública 2024, auditoría 1940: Congreso de Tlaxcala (tercera entrega)',
        'url': 'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Auditorias/2024_1940_a.pdf'},
    'CNPLE': {
        'corto': 'INEGI, CNPLE 2025',
        'doc': 'INEGI, Censo Nacional de Poderes Legislativos Estatales 2025, resultados (ejercicio 2024)',
        'url': 'https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2026/cnple/CNPLE_2025_RR.pdf'},
}

# ---------------------------------------------------------------------------
# Cifras del Decreto PEF 2026 (clave PEF), transcritas con su anexo y pagina
# impresa del DOF. Se verificaron contra el PDF cuya huella esta arriba.
# ---------------------------------------------------------------------------
GASTO_NETO_TOTAL = 10193683700000  # Anexo 1, DOF p. 32

RAMOS_2026 = {
    'legislativo': {
        'ramo': '01', 'nombre': 'Poder Legislativo', 'aprobado': 17529076499,
        'proyecto': 17529076499,
        'unidades': [
            {'id': 'diputados', 'nombre': 'Cámara de Diputados', 'aprobado': 9602671330, 'proyecto': 9602671330},
            {'id': 'senado', 'nombre': 'Cámara de Senadores', 'aprobado': 5103817038, 'proyecto': 5103817038},
            {'id': 'asf', 'nombre': 'Auditoría Superior de la Federación', 'aprobado': 2822588131, 'proyecto': 2822588131},
        ]},
    'judicial': {
        'ramo': '03', 'nombre': 'Poder Judicial de la Federación', 'aprobado': 70005628646,
        'proyecto': 85960228646,
        'unidades': [
            {'id': 'oaj', 'ur': '120', 'nombre': 'Órgano de Administración Judicial', 'aprobado': 59190814696, 'proyecto': 74224414696},
            {'id': 'scjn', 'ur': '100', 'nombre': 'Suprema Corte de Justicia de la Nación', 'aprobado': 5208743404, 'proyecto': 5869743404},
            {'id': 'tepjf', 'ur': '210 y 211', 'nombre': 'Tribunal Electoral del Poder Judicial de la Federación', 'aprobado': 3749492877, 'proyecto': 4009492877},
            {'id': 'tdj', 'ur': '300', 'nombre': 'Tribunal de Disciplina Judicial', 'aprobado': 1856577669, 'proyecto': 1856577669},
        ]},
}

# Remuneraciones: el unico criterio comparable entre cargos es la
# remuneracion total anual NETA que el propio Decreto publica en su Anexo 23.
REMUNERACIONES = [
    {'id': 'presidencia', 'cargo': 'Presidenta de la República', 'ente': 'Poder Ejecutivo Federal',
     'icono': '🏛️', 'netoAnual': 2073878, 'brutoAnual': 2882131, 'isrAnual': 808253,
     'aguinaldo': 105258, 'aguinaldoNota': 'Aguinaldo sobre sueldo base; la gratificación de fin de año sobre compensación garantizada es aparte ($282,074 brutos).',
     'estado': 'oficial', 'fuente': 'PEF', 'pagina': 'Anexo 23.1.3, DOF p. 59',
     'nota': 'Remuneración total anual neta de percepciones ordinarias 2026.'},
    {'id': 'senado', 'cargo': 'Senadora o senador', 'ente': 'Cámara de Senadores · Ramo 01',
     'icono': '⚖️', 'netoAnual': 2037848, 'brutoAnual': 2822953, 'isrAnual': 785105,
     'aguinaldo': 382207, 'aguinaldoNota': 'Aguinaldo bruto sobre la dieta.',
     'estado': 'oficial', 'fuente': 'PEF', 'pagina': 'Anexo 23.2.2, DOF p. 61',
     'nota': 'El propio anexo aclara que corresponde a las percepciones de 2025.'},
    {'id': 'asf', 'cargo': 'Auditor Superior de la Federación', 'ente': 'Auditoría Superior de la Federación · Ramo 01',
     'icono': '🔎', 'netoAnual': 2037546, 'brutoAnual': 2849965, 'isrAnual': 812419,
     'aguinaldo': 89058, 'aguinaldoNota': 'Aguinaldo bruto sobre sueldo base; la gratificación de fin de año es aparte ($297,065 brutos).',
     'estado': 'oficial', 'fuente': 'PEF', 'pagina': 'Anexo 23.4.3, DOF p. 73',
     'nota': 'Remuneración total anual neta de la máxima representación de la ASF.'},
    {'id': 'diputados', 'cargo': 'Diputada o diputado federal', 'ente': 'Cámara de Diputados · Ramo 01',
     'icono': '🏛️', 'netoAnual': 1307224, 'brutoAnual': 1710677, 'isrAnual': 403453,
     'aguinaldo': 147438, 'aguinaldoNota': 'Aguinaldo bruto sobre la dieta.',
     'estado': 'oficial', 'fuente': 'PEF', 'pagina': 'Anexo 23.3.4, DOF p. 68',
     'nota': 'El propio anexo aclara que corresponde a las percepciones de 2025.'},
    {'id': 'ministro', 'cargo': 'Ministra o ministro de la SCJN', 'ente': 'Suprema Corte de Justicia · Ramo 03',
     'icono': '⚖️', 'netoMensualTabulado': 134310, 'aguinaldoPrimaNetos': 290273,
     'netoAnual': 134310 * 12 + 290273, 'netoAnualEstado': 'derivado',
     'netoAnualOperacion': '12 × $134,310 de sueldo neto tabulado + $290,273 de aguinaldo y prima vacacional netos',
     'aguinaldo': 290273, 'aguinaldoNota': 'Aguinaldo y prima vacacional netos, juntos (Manual, p. 9).',
     'estado': 'oficial', 'fuente': 'MANUAL', 'pagina': 'pp. 8 y 9',
     'parcial': True,
     'nota': 'Cifra parcial: el Manual publica el sueldo neto tabulado y el aguinaldo con la prima; no incluye seguros ni aportaciones de seguridad social, que sí entran en la remuneración total de los otros cargos. En el Decreto, los tabuladores de la Corte vienen como imagen (Anexo 23.5).'},
]


def filas(ws, desde):
    for r in ws.iter_rows(min_row=desde, values_only=True):
        if r and r[0] is not None and any(c is not None for c in r):
            yield r


def ejercicio_hacienda():
    """Cierre 2025 y avance 2026 de los dos Poderes, de los datos abiertos de
    Hacienda (lo produce extraer_ejercicio_poderes.py)."""
    ruta = RAIZ / 'investigaciones' / 'ejercicio-poderes.json'
    j = json.loads(ruta.read_text(encoding='utf-8'))
    for k in ('cp2025', 'avance2026'):
        j[k].pop('sha256', None)
        j[k]['estado'] = 'oficial'
    j.pop('urls', None)
    j['nota'] = ('Hacienda consolida lo que cada ente le reporta; el propio ente puede publicar cifras '
                 'distintas para el mismo periodo por fechas de registro. «Ejercido» incluye lo devengado '
                 'y no pagado al cierre.')
    return j


def construir():
    pjf = openpyxl.load_workbook(XLS_PJF, data_only=True)
    d24 = openpyxl.load_workbook(XLS_2024, data_only=True)

    # --- Judicial: capitulos por unidad (PEF conceptos, nivel capitulo) ---
    capitulos = {}
    for r in filas(pjf['PEF conceptos'], 5):
        ur, nivel, cod, concepto, aprobado, pagina = r[0], r[1], r[2], r[3], r[4], r[5]
        if nivel != 'capitulo':
            continue
        capitulos.setdefault(str(ur), []).append(
            {'cap': str(cod), 'concepto': concepto, 'aprobado': aprobado,
             'estado': 'oficial', 'fuente': 'COG', 'pagina': pagina})

    # --- SCJN: cortes (cierre 2025 y enero-junio 2026), solo filas Total y capitulos ---
    cortes = []
    for r in filas(pjf['SCJN cortes'], 5):
        corte, concepto, aprobado, adec, modif, deveng, pagado = r[:7]
        if not isinstance(aprobado, (int, float)):
            continue
        cortes.append({'corte': corte, 'concepto': concepto, 'aprobado': aprobado,
                       'modificado': modif, 'devengado': deveng, 'pagado': pagado,
                       'estado': 'oficial',
                       'fuente': 'SCJN_2025' if str(corte).startswith('2025') else 'SCJN_JUN',
                       'pagina': r[7]})

    # --- OAJ: capitulos SHCP contra OAJ y trimestre abril-junio ---
    oaj = []
    for r in filas(pjf['OAJ capítulos'], 5):
        cap, concepto, shcp, oajv, dif, asig, pag = r[:7]
        if not str(cap).isdigit():
            continue
        oaj.append({'cap': str(cap), 'concepto': str(concepto).capitalize(), 'anualShcp': shcp,
                    'anualOaj': oajv, 'diferencia': dif, 'asignadoTrim': asig, 'pagadoTrim': pag,
                    'estado': 'oficial', 'fuente': 'OAJ_CAP'})

    # --- Circuitos: pagos registrados abril-junio (derivado) ---
    circuitos = []
    for r in filas(pjf['Circuitos 32'], 5):
        if not isinstance(r[0], int):
            continue
        circuitos.append({'n': r[0], 'ueg': r[1], 'sede': r[2], 'pagado': r[3],
                          'estado': 'derivado', 'fuente': 'OAJ_UEG'})

    # --- Legislativo 2024: ejecucion federal (miles de pesos -> pesos) ---
    federal = []
    for r in filas(d24['Federal'], 4):
        inst, concepto, miles, estado, pagina = r[:5]
        if not isinstance(miles, (int, float)):
            continue
        federal.append({'institucion': inst, 'concepto': concepto, 'pesos': round(miles * 1000),
                        'estado': estado, 'fuente': 'ASF_DIP' if inst == 'Diputados' else 'ASF_SEN',
                        'pagina': pagina})

    personal_dip = []
    for r in filas(d24['Personal Diputados'], 4):
        partida, concepto, miles, estado, pagina = r[:5]
        if not isinstance(miles, (int, float)):
            continue
        personal_dip.append({'partida': str(partida), 'concepto': concepto, 'pesos': round(miles * 1000),
                             'estado': estado, 'fuente': 'ASF_DIP', 'pagina': pagina})

    senado_cap = []
    for r in filas(d24['Senado capítulos'], 5):
        cap, concepto, dev, pag = r[:4]
        if not isinstance(dev, (int, float)):
            continue
        senado_cap.append({'cap': str(cap), 'concepto': concepto, 'devengado': round(dev * 1000),
                           'pagado': round(pag * 1000), 'estado': 'oficial', 'fuente': 'ASF_SEN', 'pagina': 5})

    congresos = []
    for r in filas(d24['Congresos 32'], 4):
        ent, ejercicio, mdp, estado, pagina = r[:5]
        if not isinstance(mdp, (int, float)):
            continue
        congresos.append({'entidad': ent, 'ejercicio': ejercicio, 'ejercidoMdp': mdp,
                          'estado': estado, 'fuente': 'CNPLE', 'pagina': pagina})

    asf_congresos = []
    for r in filas(d24['ASF congresos'], 4):
        congreso, aud, concepto, importe, unidad, pagina = r[:6]
        if not isinstance(importe, (int, float)):
            continue
        pesos = importe * 1000 if unidad == 'miles de pesos' else importe
        asf_congresos.append({'congreso': congreso, 'auditoria': aud, 'concepto': concepto,
                              'pesos': round(pesos, 2), 'estado': 'oficial',
                              'fuente': 'ASF_NL' if aud == 1402 else 'ASF_TLX', 'pagina': pagina})

    return {
        'consulta': CONSULTA,
        'nota': 'Pesos nominales. «Aprobado» es autorización de gasto, no dinero pagado. '
                'Cada cifra conserva su documento, su página y su estado: oficial (transcrita), '
                'derivado (calculada, con la operación dicha) o pendiente. Las vistas de un mismo '
                'dinero no se suman entre sí.',
        'fuentes': FUENTES,
        'gastoNetoTotal': {'valor': GASTO_NETO_TOTAL, 'estado': 'oficial', 'fuente': 'PEF', 'pagina': 'Anexo 1, DOF p. 32'},
        'ramos2026': {k: dict(v, estado='oficial', fuente='PEF',
                              pagina='Anexo 1, DOF p. 32; proyecto y recorte: Anexo 32, DOF p. 108')
                      for k, v in RAMOS_2026.items()},
        'remuneraciones2026': REMUNERACIONES,
        'ejercicio': ejercicio_hacienda(),
        'judicial': {
            'capitulosPorUR': capitulos,
            'scjnCortes': cortes,
            'scjnAgosto': {'original': 5208743404, 'modificado': 5230072515.57, 'compromiso': 1707440588.3,
                           'ejercido': 3253791174.26, 'disponible': 268840753.01,
                           'estado': 'oficial', 'fuente': 'SCJN_AGO', 'pagina': 1,
                           'nota': 'Compromiso + ejercido + disponible = modificado. «Ejercido» no se renombra como pagado.'},
            'oajCapitulos': oaj,
            'oajNota': 'SHCP y OAJ difieren en $10,637,899 entre los capítulos 3000 y 4000; el total coincide. La causa está pendiente.',
            'circuitos': circuitos,
            'circuitosNota': 'Pagos registrados en las unidades ejecutoras de cada circuito entre abril y junio de 2026. '
                             'Son pagos parciales: excluyen la nómina, que se paga de forma centralizada. No son el costo del circuito.',
            'pendientes': ['Costo completo por circuito', 'Costo completo por ponencia de la SCJN'],
        },
        'legislativo': {
            'ejercicio2024': federal,
            'resultadosAsf': [
                {'institucion': 'Diputados', 'texto': '26 resultados sin irregularidades detectadas en la muestra revisada.',
                 'estado': 'oficial', 'fuente': 'ASF_DIP', 'pagina': 43},
                {'institucion': 'Senado', 'texto': '25 resultados sin irregularidades y dos solventados antes del informe, en la muestra revisada.',
                 'estado': 'oficial', 'fuente': 'ASF_SEN', 'pagina': 31},
            ],
            'personalDiputados2024': personal_dip,
            'senadoCapitulos2024': senado_cap,
            'congresos2024': congresos,
            'asfCongresos2024': asf_congresos,
            'pendientes': ['Remuneraciones individuales de los 32 congresos locales',
                           'Número de legisladores de cada congreso con su fuente, para el costo por legislador'],
        },
    }


# ---------------------------------------------------------------------------
# Catalogo de referencias (DB.referencias_legales): las fichas 21 y 22
# apuntaban a paginas de inicio y traian cifras sin documento; se fijan a su
# documento exacto. Las fichas 71 a 75 son los documentos nuevos.
# ---------------------------------------------------------------------------
REF_ACTUALIZAR = {
    'ref-pef-ramo03': {
        'cita_apa': 'Secretaría de Hacienda y Crédito Público. (2026). Presupuesto de Egresos de la Federación 2026. Ramo 03, Poder Judicial: análisis administrativo económico. SHCP.',
        'url': FUENTES['UR']['url'],
        'descripcion': 'Presupuesto aprobado 2026 del Ramo 03 por unidad responsable: $70,005.6 millones de pesos. La Suprema Corte tiene $5,208.7 millones; el Órgano de Administración Judicial, $59,190.8 millones; el Tribunal Electoral, $3,749.5 millones, y el Tribunal de Disciplina Judicial, $1,856.6 millones. Las cifras cuadran con el Anexo 1 del Decreto de Presupuesto (DOF 21-11-2025, p. 32).'},
    'ref-manual-remun-pjf': {
        'cita_apa': 'Poder Judicial de la Federación. (2026, 27 de febrero). Manual que regula las remuneraciones de las personas servidoras públicas del Poder Judicial de la Federación para el ejercicio fiscal 2026. Diario Oficial de la Federación.',
        'url': FUENTES['MANUAL']['url'],
        'descripcion': 'Tabulador 2026 del Poder Judicial de la Federación. Una ministra o un ministro de la Suprema Corte percibe como máximo $134,310 de sueldo neto mensual (p. 8) y $290,273 netos al año de aguinaldo y prima vacacional (p. 9).'},
}

REF_NUEVAS = [
    {'num': 71, 'id': 'ref-asf-cp2024-diputados', 'categoria': 'fiscalizacion_auditoria',
     'categoria_nombre': 'Fiscalización Superior y Auditoría',
     'cita_apa': 'Auditoría Superior de la Federación. Informe individual de la auditoría 2024-0031: Cámara de Diputados. Fiscalización Superior de la Cuenta Pública 2024, segunda entrega.',
     'url': FUENTES['ASF_DIP']['url'],
     'descripcion': 'Gasto 2024 de la Cámara de Diputados: $8,982.9 millones aprobados y $9,371.7 millones pagados (p. 4), con el desglose de su capítulo de personal (p. 5). La revisión reporta 26 resultados sin irregularidades en la muestra (p. 43).'},
    {'num': 72, 'id': 'ref-asf-cp2024-senado', 'categoria': 'fiscalizacion_auditoria',
     'categoria_nombre': 'Fiscalización Superior y Auditoría',
     'cita_apa': 'Auditoría Superior de la Federación. Informe individual de la auditoría 2024-0032: Cámara de Senadores. Fiscalización Superior de la Cuenta Pública 2024, segunda entrega.',
     'url': FUENTES['ASF_SEN']['url'],
     'descripcion': 'Gasto 2024 del Senado: $4,955.2 millones aprobados, $5,045.7 millones devengados y $4,978.8 millones pagados al 31 de diciembre (pp. 4 y 5), por capítulo de gasto.'},
    {'num': 73, 'id': 'ref-inegi-cnple2025', 'categoria': 'estadistica_oficial',
     'categoria_nombre': 'Estadística Oficial del Estado Mexicano',
     'cita_apa': 'Instituto Nacional de Estadística y Geografía. (2026). Censo Nacional de Poderes Legislativos Estatales 2025: presentación de resultados. INEGI.',
     'url': FUENTES['CNPLE']['url'],
     'descripcion': 'Gasto ejercido en 2024 por cada uno de los 32 congresos locales, en millones de pesos corrientes (p. 11).'},
    {'num': 74, 'id': 'ref-scjn-ejercicio2026', 'categoria': 'judicial',
     'categoria_nombre': 'Poder Judicial & SCJN',
     'cita_apa': 'Suprema Corte de Justicia de la Nación. (2026). Estado del ejercicio del presupuesto al 31 de agosto de 2026. SCJN.',
     'url': FUENTES['SCJN_AGO']['url'],
     'descripcion': 'Las 127 partidas de la Corte con su presupuesto original, modificado, comprometido, ejercido y disponible. Al corte, de $5,230.1 millones modificados se habían ejercido $3,253.8 millones.'},
    {'num': 75, 'id': 'ref-oaj-trimestre2026', 'categoria': 'judicial',
     'categoria_nombre': 'Poder Judicial & SCJN',
     'cita_apa': 'Órgano de Administración Judicial. (2026). Presupuesto ejercido: cierre del segundo trimestre de 2026. OAJ.',
     'url': FUENTES['OAJ_CAP']['url'],
     'descripcion': 'Presupuesto asignado y pagado del Órgano de Administración Judicial entre el 1 de abril y el 30 de junio de 2026, por capítulo, por unidad ejecutora y por partida.'},
]


def _valor(v):
    return json.dumps(v, ensure_ascii=True)


def actualizar_referencias(b):
    for rid, campos in REF_ACTUALIZAR.items():
        i = b.index('"id": "%s"' % rid)
        fin = b.index('\r\n    }', i)
        bloque = b[i:fin]
        for k, v in campos.items():
            ini = bloque.index('"%s": ' % k)
            eol = bloque.index('\r\n', ini) if '\r\n' in bloque[ini:] else len(bloque)
            coma = ',' if bloque[ini:eol].rstrip().endswith(',') else ''
            bloque = bloque[:ini] + '"%s": %s%s' % (k, _valor(v), coma) + bloque[eol:]
        b = b[:i] + bloque + b[fin:]
    ancla = '"id": "ref-gaceta7121"'
    i = b.index(ancla)
    fin = b.index('\r\n    }', i) + len('\r\n    }')
    for ref in reversed(REF_NUEVAS):
        if '"id": "%s"' % ref['id'] in b:
            continue
        cuerpo = ',\r\n    {\r\n' + ',\r\n'.join('      "%s": %s' % (k, _valor(v)) for k, v in ref.items()) + '\r\n    }'
        b = b[:fin] + cuerpo + b[fin:]
    return b


def main():
    datos = construir()
    cuerpo = json.dumps(datos, ensure_ascii=True, indent=2)
    cuerpo = '\n'.join('  ' + l if i else l for i, l in enumerate(cuerpo.split('\n')))
    bloque = ('"poderes": ' + cuerpo).replace('\n', '\r\n')

    b = BASE.read_bytes().decode('utf-8')
    marca = '\r\n"poderes": '
    cierre = b.rfind('\r\n};')
    if cierre < 0 or b[cierre + 4:].strip():
        sys.exit('No encuentro el cierre de window.AUDIT_DB; no toco nada.')
    if marca in b:
        b = b[:b.index(marca)] + '\r\n' + bloque + b[cierre:]
    else:
        # la ultima coleccion cierra con "}"; se le agrega la coma
        previo = b[:cierre].rstrip()
        b = previo + ',\r\n' + bloque + b[cierre:]
    b = actualizar_referencias(b)
    BASE.write_bytes(b.encode('utf-8'))
    print('poderes integrada:', len(bloque) // 1024, 'KB')


if __name__ == '__main__':
    main()
