#!/usr/bin/env python3
"""Integra a assets/js/audit-database.js la colección «comparador_salarial»:
los cargos con los que el bloque 2 del módulo 3 (Calculadora Cívica) compara
el ingreso del lector, y el cuadro de prestaciones contra la Ley Federal del
Trabajo.

Uso:
    python3 herramientas/integrar_comparador.py

Cada cifra se capturó de su documento oficial; el extracto de la página
queda en investigaciones/fuentes-comparador/. Lo que aquí se calcula (el neto
anual de los cargos judiciales y de los asesores, los promedios de los
honorarios) se marca «derivado» y dice su operación. Lo que no se pudo
sostener con un documento se deja «pendiente».
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from integrar_ambiente import BASE, insertar  # noqa: E402

CONSULTA = '26 de septiembre de 2026'

FUENTES = {
    'PEF': {
        'corto': 'PEF 2026, Anexo 23 (DOF 21-11-2025)',
        'doc': 'Decreto de Presupuesto de Egresos de la Federación para el Ejercicio Fiscal 2026, Anexo 23 «Remuneraciones de los servidores públicos de la Federación», Diario Oficial de la Federación, 21 de noviembre de 2025, edición vespertina.',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/ref/pef_2026/PEF_2026_orig_21nov25.pdf',
        'sha256': '6db4a86b588a0f76928e5d61298579c4aff2c29c3ace68fdedbfa5afceb8f2bc'},
    'DIP': {
        'corto': 'Manual de remuneraciones de la Cámara de Diputados 2026 (DOF 27-02-2026)',
        'doc': 'Manual que Regula las Remuneraciones para las y los Diputados Federales, Personal de Mando y Homólogos de la Cámara de Diputados, de la Unidad de Evaluación y Control y del Canal del Congreso, para el ejercicio fiscal 2026. Diario Oficial de la Federación, 27 de febrero de 2026, pp. 137 a 146.',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/marjur/marco/Dip_manual_remun_27feb26.pdf',
        'sha256': 'e2d839ba972dbe26ba846a7190d7cf81184acf507c61a42deb09dc617de5c7dd'},
    'SEN': {
        'corto': 'Manual de remuneraciones del Senado 2026 (DOF 27-02-2026)',
        'doc': 'Manual de Remuneraciones de las Senadoras, Senadores, servidoras y servidores públicos de mando y homólogos, y la información relativa al Capítulo de Servicios Personales. Diario Oficial de la Federación, 27 de febrero de 2026.',
        'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5781138&fecha=27/02/2026'},
    'PJF': {
        'corto': 'Manual de remuneraciones del PJF 2026 (DOF 27-02-2026)',
        'doc': 'Manual que regula las remuneraciones de las personas servidoras públicas del Poder Judicial de la Federación para el ejercicio fiscal 2026, Anexo B «Presupuesto analítico de plazas». Diario Oficial de la Federación, 27 de febrero de 2026.',
        'url': 'https://apps.cjf.gob.mx/normativa/Recursos/2026-0-6-OAJ_V01.PDF',
        'sha256': '1bab2ed9e8821e6bd8e443b7239423b319a6626cc2a3104f2272eff676f55ef7'},
    'LOAPF': {
        'corto': 'Ley Orgánica de la Administración Pública Federal, art. 26',
        'doc': 'Ley Orgánica de la Administración Pública Federal, artículo 26, texto vigente (última reforma DOF 07-05-2026).',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LOAPF.pdf',
        'sha256': '3edf486e601217f5f595f94f56832d8845cbd9193b6494af52473237252bcc5f'},
    'LFT': {
        'corto': 'Ley Federal del Trabajo, arts. 76, 80 y 87',
        'doc': 'Ley Federal del Trabajo, texto vigente (última reforma DOF 14-05-2026): artículo 76 (vacaciones, reformado DOF 27-12-2022), 80 (prima vacacional) y 87 (aguinaldo).',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf',
        'sha256': '12f09393a1951a91c3f57f579bf611b034edf1a5f78cdbfb828e23ff3a9acbf7'},
}

GRUPOS = [
    {'id': 'ejecutivo', 'nombre': 'Poder Ejecutivo', 'icono': '🏛️'},
    {'id': 'legislativo', 'nombre': 'Congreso de la Unión', 'icono': '📜'},
    {'id': 'judicial', 'nombre': 'Poder Judicial de la Federación', 'icono': '⚖️'},
    {'id': 'local', 'nombre': 'Congresos de los estados', 'icono': '🗺️'},
]

SECRETARIAS = [
    'Gobernación', 'Relaciones Exteriores', 'Defensa Nacional', 'Marina',
    'Seguridad y Protección Ciudadana', 'Hacienda y Crédito Público', 'Bienestar',
    'Medio Ambiente y Recursos Naturales', 'Energía', 'Economía',
    'Agricultura y Desarrollo Rural', 'Infraestructura, Comunicaciones y Transportes',
    'Anticorrupción y Buen Gobierno', 'Educación Pública',
    'Ciencia, Humanidades, Tecnología e Innovación', 'Salud', 'Trabajo y Previsión Social',
    'Desarrollo Agrario, Territorial y Urbano', 'Cultura', 'Turismo', 'Mujeres',
    'Agencia de Transformación Digital y Telecomunicaciones',
]


def judicial(id_, cargo, detalle, mes, agui, riesgo, asig, pagina, nota):
    """Neto anual de un cargo judicial: el Manual publica el sueldo neto
    mensual y, aparte, los pagos anuales netos. Se suman con el máximo de
    cada rango; la operación queda escrita."""
    mmax = mes[-1]
    partes = ['12 × %s de sueldo neto mensual' % pesos(mmax),
              '%s de aguinaldo y prima vacacional' % pesos(agui[-1])]
    total = 12 * mmax + agui[-1]
    if riesgo:
        partes.append('%s de pago por riesgo' % pesos(riesgo))
        total += riesgo
    if asig:
        partes.append('%s de asignaciones adicionales' % pesos(asig[-1]))
        total += asig[-1]
    return {
        'id': id_, 'grupo': 'judicial', 'cargo': cargo, 'detalle': detalle, 'icono': '⚖️',
        'mensual': {'min': mes[0], 'max': mmax}, 'mensualEstado': 'oficial',
        'mensualConcepto': 'Sueldo neto mensual del tabulador',
        'aguinaldoPrima': {'min': agui[0], 'max': agui[-1]}, 'pagoRiesgo': riesgo,
        'asignaciones': {'min': asig[0], 'max': asig[-1]} if asig else None,
        'anual': total, 'anualEstado': 'derivado',
        'anualOperacion': ' + '.join(partes) + ' (todos netos, del Manual; con el máximo de cada rango)',
        'parcial': True, 'fuente': 'PJF', 'pagina': pagina, 'nota': nota,
    }


def pesos(v):
    return '${:,.0f}'.format(v)


def construir():
    cargos = [
        {'id': 'presidencia', 'grupo': 'ejecutivo', 'cargo': 'Presidenta de la República',
         'detalle': 'Titular del Poder Ejecutivo', 'icono': '🏛️',
         'mensual': {'max': 134290}, 'mensualEstado': 'oficial',
         'mensualConcepto': 'Remuneración ordinaria total líquida mensual neta',
         'anual': 2073878, 'anualEstado': 'oficial',
         'anualConcepto': 'Remuneración total anual neta de percepciones ordinarias',
         'fuente': 'PEF', 'pagina': 'Anexos 23.1.2 y 23.1.3, DOF p. 59',
         'nota': 'El tope del artículo 127 constitucional: ningún servidor público puede recibir una remuneración mayor que la establecida para la Presidencia.'},
        {'id': 'secretario', 'grupo': 'ejecutivo', 'cargo': 'Secretaria o secretario de Estado',
         'detalle': 'Gabinete: las 22 dependencias del art. 26 de la LOAPF', 'icono': '🗂️',
         'mensual': {'max': 168860}, 'mensualEstado': 'oficial',
         'mensualConcepto': 'Límite máximo de la percepción ordinaria neta mensual, grupo G (sueldo más prestaciones en efectivo y en especie)',
         'anual': 12 * 168860, 'anualEstado': 'derivado',
         'anualOperacion': '12 × $168,860 del límite mensual. El anexo no dice si ese límite ya prorratea el aguinaldo: no se le suma nada',
         'fuente': 'PEF', 'pagina': 'Anexo 23.1.1, DOF p. 58',
         'lista': SECRETARIAS, 'listaFuente': 'LOAPF',
         'nota': 'El Presupuesto no publica el sueldo de cada titular con su nombre: publica un solo límite para el grupo G, que rige a las 22 dependencias. Por eso las 22 comparten cifra. Ese límite incluye prestaciones en especie y no se compara renglón a renglón con la cifra «líquida» de la Presidenta.'},
        {'id': 'subsecretario', 'grupo': 'ejecutivo', 'cargo': 'Subsecretaria o subsecretario de Estado',
         'detalle': 'Grupo H: subsecretarías y oficialías mayores', 'icono': '🗂️',
         'mensual': {'max': 167353}, 'mensualEstado': 'oficial',
         'mensualConcepto': 'Límite máximo de la percepción ordinaria neta mensual, grupo H',
         'anual': 12 * 167353, 'anualEstado': 'derivado',
         'anualOperacion': '12 × $167,353 del límite mensual, sin sumar aguinaldo',
         'fuente': 'PEF', 'pagina': 'Anexo 23.1.1, DOF p. 58',
         'nota': 'Mismo tabulador para todas las dependencias.'},

        {'id': 'senado', 'grupo': 'legislativo', 'cargo': 'Senadora o senador',
         'detalle': '128 escaños', 'icono': '⚖️',
         'mensual': {'max': 132900}, 'mensualEstado': 'oficial',
         'mensualConcepto': 'Dieta neta mensual 2026 (el Manual la publica en miles: 132.9)',
         'anual': 2037848, 'anualEstado': 'oficial',
         'anualConcepto': 'Remuneración total anual neta (el anexo aclara que son percepciones de 2025)',
         'fuente': 'SEN', 'pagina': 'Anexo 1; anual: PEF, Anexo 23.2.2, DOF p. 61',
         'nota': 'La dieta no es sueldo: el Manual la define como la remuneración por la representación política, irrenunciable.'},
        {'id': 'asesor_senado', 'grupo': 'legislativo', 'cargo': 'Asesor parlamentario del Senado',
         'detalle': 'De grupo parlamentario (nivel 34); el asesor ejecutivo es nivel 30', 'icono': '🧑‍💼',
         'mensual': {'min': 121900, 'max': 126000}, 'mensualEstado': 'oficial',
         'mensualConcepto': 'Percepción mensual neta del nivel 34 del tabulador',
         'subniveles': [
             {'nombre': 'Asesor parlamentario de grupo parlamentario (nivel 34)', 'min': 121900, 'max': 126000},
             {'nombre': 'Asesor ejecutivo (nivel 30)', 'min': 58400, 'max': 89000},
             {'nombre': 'Asesor de tesorero (nivel 29)', 'min': 42900, 'max': 58300}],
         'anual': 12 * 126000, 'anualEstado': 'derivado',
         'anualOperacion': '12 × $126,000, el máximo del nivel 34, sin sumar aguinaldo',
         'fuente': 'SEN', 'pagina': 'Anexo 2 (tabulador) y Anexo 4 (catálogo de puestos por nivel)',
         'nota': 'El catálogo del Anexo 4 asigna cada puesto a un nivel y el tabulador del Anexo 2 fija el rango de cada nivel; aquí se cruzan las dos tablas. El Manual publica los miles con un decimal. Los asesores contratados por honorarios no están en el tabulador.'},
        {'id': 'diputados', 'grupo': 'legislativo', 'cargo': 'Diputada o diputado federal',
         'detalle': '500 curules', 'icono': '🏛️',
         'mensual': {'max': 79846.35}, 'mensualEstado': 'oficial',
         'mensualConcepto': 'Dieta neta mensual 2026',
         'anual': 1307224, 'anualEstado': 'oficial',
         'anualConcepto': 'Remuneración total anual neta (el anexo aclara que son percepciones de 2025)',
         'fuente': 'DIP', 'pagina': 'p. 144; anual: PEF, Anexo 23.3.4, DOF p. 68',
         'nota': 'La Cámara, además, cubre el impuesto del aguinaldo de cada diputado: $67,785 en el anexo anual.'},
        {'id': 'asesor_diputados', 'grupo': 'legislativo', 'cargo': 'Asesor de la Cámara de Diputados',
         'detalle': 'Personal «homólogo a mando»: funciones técnicas, de asesoría o de investigación', 'icono': '🧑‍💼',
         'mensual': {'min': 34486, 'max': 107177}, 'mensualEstado': 'oficial',
         'mensualConcepto': 'Remuneración neta mensual de los niveles homólogos',
         'subniveles': [
             {'nombre': 'Homólogo a director de área', 'min': 74159, 'max': 107177},
             {'nombre': 'Homólogo a subdirector de área', 'min': 50513, 'max': 68126},
             {'nombre': 'Homólogo a jefe de departamento', 'min': 34486, 'max': 42137}],
         'anual': 12 * 107177, 'anualEstado': 'derivado',
         'anualOperacion': '12 × $107,177, el máximo del homólogo a director de área, sin sumar aguinaldo',
         'honorarios': {'contratos': 3433, 'montoAnual': 1042550553,
                        'promedioAnual': round(1042550553 / 3433), 'promedioMensual': round(1042550553 / 3433 / 12),
                        'operacion': '$1,042,550,553 de la partida 1210 entre 3,433 contratos (y entre 12 para el mes)',
                        'pagina': 'Anexo 2, p. 146'},
         'fuente': 'DIP', 'pagina': 'pp. 142 y 143; definición de homólogo: p. 139',
         'nota': 'El Manual no tiene un puesto llamado «asesor de diputado»: la asesoría la hacen el personal homólogo a mando y, sobre todo, los contratos por honorarios, que no tienen tabulador público.'},

        {'id': 'ministro', 'grupo': 'judicial', 'cargo': 'Ministra o ministro de la SCJN',
         'detalle': 'Nueve integrantes del Pleno', 'icono': '⚖️',
         'mensual': {'max': 134310}, 'mensualEstado': 'oficial',
         'mensualConcepto': 'Sueldo neto mensual del tabulador',
         'aguinaldoPrima': {'max': 290273},
         'anual': 12 * 134310 + 290273, 'anualEstado': 'derivado',
         'anualOperacion': '12 × $134,310 de sueldo neto mensual + $290,273 de aguinaldo y prima vacacional netos',
         'parcial': True, 'fuente': 'PJF', 'pagina': 'Anexo B, pp. 8 y 9',
         'nota': 'Cifra parcial: el Manual no incluye seguros ni aportaciones de seguridad social, que sí entran en las cifras anuales del Congreso y de la Presidenta.'},
        judicial('secretario_estudio', 'Secretaria o secretario de estudio y cuenta',
                 'SCJN: quien proyecta las sentencias de una ponencia (grupo 7)',
                 (119317, 123105), (244054, 253281), None, (106875, 110663), 'Anexo B, pp. 8 y 9',
                 'Es el «proyectista» de la Corte. A diferencia de la ministra o ministro, recibe asignaciones adicionales.'),
        judicial('asesor_scjn', 'Asesora o asesor de la SCJN', 'Grupo 11 del tabulador de la Corte',
                 (91082, 102018, 117152), (179798, 205240, 240265), None, (79661, 89953, 104710),
                 'Anexo B, pp. 8 y 9', 'Comparte grupo con coordinador administrativo I, dictaminador I y secretario auxiliar I.'),
        judicial('magistrado', 'Magistrada o magistrado de circuito', 'Tribunales colegiados y de apelación',
                 (129310,), (270975,), 119460, None, 'Anexo B, pp. 16 y 19',
                 'El pago por riesgo lo reciben solo quienes juzgan: magistraturas de circuito y juzgados de distrito.'),
        judicial('juez', 'Jueza o juez de distrito', 'Juzgados de distrito', (126310,), (263912,), 110690, (52000,),
                 'Anexo B, pp. 16 y 19', 'Las asignaciones adicionales se toman en su máximo publicado.'),
        judicial('proyectista_tribunal', 'Secretaria o secretario proyectista de tribunal', 'Tribunal de circuito (nivel 13 A)',
                 (81027,), (154294,), None, (211170,), 'Anexo B, pp. 16 y 20',
                 'Comparte nivel con la secretaría de tribunal de circuito. Las asignaciones adicionales se toman en su máximo publicado.'),
        judicial('proyectista_juzgado', 'Secretaria o secretario proyectista de juzgado', 'Juzgado de distrito (nivel 13 C)',
                 (74865,), (141968,), None, (194796,), 'Anexo B, pp. 16 y 20',
                 'Comparte nivel con la secretaría de juzgado y la de instrucción de los juzgados laborales.'),

        {'id': 'diputado_local', 'grupo': 'local', 'cargo': 'Diputada o diputado local',
         'detalle': '32 congresos, 32 tabuladores', 'icono': '🗺️',
         'pendiente': True, 'mensualEstado': 'pendiente', 'anualEstado': 'pendiente',
         'nota': 'Cada congreso aprueba su propio presupuesto y publica la dieta en su periódico oficial o en su portal de transparencia. No hay una serie nacional oficial que las reúna: el Censo Nacional de Poderes Legislativos Estatales del INEGI cuenta legisladores y gasto, pero no publica la dieta. Se integrará entidad por entidad, con su documento.'},
    ]

    prestaciones = {
        'columnas': [
            {'id': 'lft', 'nombre': 'Usted (mínimo de ley)', 'sub': 'Ley Federal del Trabajo'},
            {'id': 'dip', 'nombre': 'Diputación federal', 'sub': 'Manual 2026 y Anexo 23.3.4'},
            {'id': 'sen', 'nombre': 'Senaduría', 'sub': 'Manual 2026 y Anexo 23.2.2'},
            {'id': 'pr', 'nombre': 'Presidencia', 'sub': 'Anexo 23.1.3'},
            {'id': 'pjf', 'nombre': 'Poder Judicial', 'sub': 'Manual PJF 2026'},
        ],
        'filas': [
            {'concepto': 'Aguinaldo', 'celdas': {
                'lft': {'tx': '15 días de salario, como mínimo, antes del 20 de diciembre', 'ref': 'LFT, art. 87', 'estado': 'oficial'},
                'dip': {'tx': '40 días de la dieta bruta: $147,438', 'ref': 'Manual, Anexo 1, p. 145; Anexo 23.3.4', 'estado': 'oficial'},
                'sen': {'tx': 'El Manual dice 40 días de dieta; el anexo anual reporta $382,207, que equivalen a unos 60 días', 'ref': 'Manual, Anexo 3; Anexo 23.2.2', 'estado': 'pendiente',
                        'nota': '$382,207 ÷ ($190,023 de dieta bruta mensual ÷ 30) = 60.3 días. El documento no explica la diferencia con los 40 días del Manual: queda por aclarar.'},
                'pr': {'tx': 'Aguinaldo $105,258 más gratificación de fin de año $282,074', 'ref': 'Anexo 23.1.3, DOF p. 59', 'estado': 'oficial'},
                'pjf': {'tx': 'Aguinaldo y prima vacacional netos: $290,273 una ministra o ministro; $270,975 una magistratura de circuito', 'ref': 'Manual PJF, Anexo B, pp. 9 y 19', 'estado': 'oficial'}}},
            {'concepto': 'Vacaciones', 'celdas': {
                'lft': {'tx': '12 días laborables el primer año; suben de dos en dos hasta 20', 'ref': 'LFT, art. 76 (DOF 27-12-2022)', 'estado': 'oficial'},
                'dip': {'tx': 'El Manual no las prevé para la diputación; su personal de mando tiene 20 días hábiles', 'ref': 'Manual, Anexo 1, p. 145', 'estado': 'oficial'},
                'sen': {'tx': 'El Manual no las prevé para la senaduría; su personal tiene 20 días hábiles', 'ref': 'Manual, numeral 9 b) vii', 'estado': 'oficial'},
                'pr': {'tx': 'El anexo registra la prima, no los días', 'ref': 'Anexo 23.1.3', 'estado': 'pendiente'},
                'pjf': {'tx': 'Dos periodos al año, conforme a la Ley Orgánica del PJF', 'ref': 'Manual PJF, numeral 8.2.10', 'estado': 'oficial'}}},
            {'concepto': 'Prima vacacional', 'celdas': {
                'lft': {'tx': '25 % de lo que se gana en las vacaciones: 3 días de salario el primer año', 'ref': 'LFT, art. 80', 'estado': 'oficial'},
                'dip': {'tx': 'Personal de mando: 50 % de 10 días por periodo, dos periodos (10 días al año)', 'ref': 'Manual, Anexo 1, p. 145', 'estado': 'oficial'},
                'sen': {'tx': 'Personal de mando: 15 días de sueldo base al año', 'ref': 'Manual, numeral 9 b) ii', 'estado': 'oficial'},
                'pr': {'tx': '$17,656 al año', 'ref': 'Anexo 23.1.3', 'estado': 'oficial'},
                'pjf': {'tx': '50 % de 10 días por periodo, dos periodos (10 días al año)', 'ref': 'Manual PJF, numeral 8.2.8', 'estado': 'oficial'}}},
            {'concepto': 'Seguro de vida', 'celdas': {
                'lft': {'tx': 'La ley no lo exige al patrón', 'ref': 'LFT', 'estado': 'oficial'},
                'dip': {'tx': '40 dietas brutas; 80 si la muerte es por accidente y 120 en accidente colectivo', 'ref': 'Manual, Anexo 1, p. 145', 'estado': 'oficial'},
                'sen': {'tx': '40 meses de dieta; prima pagada con presupuesto: $96,759', 'ref': 'Manual, Anexo 3; Anexo 23.2.2', 'estado': 'oficial'},
                'pr': {'tx': 'Prima pagada con presupuesto: $35,914 al año', 'ref': 'Anexo 23.1.3', 'estado': 'oficial'},
                'pjf': {'tx': '40 meses de sueldo básico', 'ref': 'Manual PJF, numeral 8.1.1', 'estado': 'oficial'}}},
            {'concepto': 'Impuesto del aguinaldo', 'celdas': {
                'lft': {'tx': 'Lo paga usted: se le retiene de la parte gravada', 'ref': 'Ley del ISR, arts. 93 fracc. XIV y 96', 'estado': 'oficial'},
                'dip': {'tx': 'Lo paga la Cámara: $67,785 como «prestación ISR de aguinaldo»', 'ref': 'Anexo 23.3.4, nota 4, DOF p. 68', 'estado': 'oficial'},
                'sen': {'tx': 'El anexo no registra esa prestación', 'ref': 'Anexo 23.2.2', 'estado': 'oficial'},
                'pr': {'tx': 'El anexo no registra esa prestación', 'ref': 'Anexo 23.1.3', 'estado': 'oficial'},
                'pjf': {'tx': 'El Manual publica el aguinaldo ya en neto', 'ref': 'Manual PJF, Anexo B', 'estado': 'oficial'}}},
        ],
    }

    return {
        'consulta': CONSULTA,
        'fuentes': FUENTES,
        'grupos': GRUPOS,
        'cargos': cargos,
        'prestaciones': prestaciones,
        'ley': {'aguinaldoDias': 15, 'primaVacacionalDias': 3, 'vacacionesDias': 12,
                'referencia': {'aguinaldoDias': 40, 'primaVacacionalDias': 10},
                'nota': 'Mínimos de la Ley Federal del Trabajo para el primer año de servicios. La referencia de 40 días de aguinaldo y 10 de prima vacacional es la que fijan los Manuales de la Cámara de Diputados (Anexo 1) y del PJF (numeral 8.2.8).'},
    }


def main():
    b = BASE.read_bytes().decode('utf-8')
    b = insertar(b, 'comparador_salarial', construir())
    BASE.write_bytes(b.encode('utf-8'))
    print('comparador_salarial integrada')


if __name__ == '__main__':
    main()
