#!/usr/bin/env python3
"""Pone al día el glosario y la bibliografía con el vocabulario de los cinco
módulos reorganizados (Circuito del Dinero, Inversión y Megaobras,
Calculadora Cívica, Modo Inspector y Costo Ambiental).

Uso:
    python3 herramientas/integrar_glosario_modulos.py

Hace cuatro cosas:
1. Suma términos que los módulos usan sin definición: Paquete Económico,
   CGPE, Resolución Miscelánea Fiscal, aguinaldo, prima vacacional, salario
   mínimo, subsidio para el empleo, retención del ISR, cuota obrera, las
   instituciones que más se citan (SHCP, SAT, INEGI, CONAPO, SEMARNAT,
   CONAGUA, IMSS, IPAB), Ramo 16, sobrecosto, ente público, sexenio, promedio
   por habitante, bandera roja, residuos sólidos urbanos, cambio climático,
   gases de efecto invernadero, impuesto al carbono y las CEEM.
2. Corrige definiciones viejas que afirmaban cifras sin documento o que el
   texto vigente de la ley ya no sostiene (partida secreta, Ramo 23, costo
   financiero, FASSA, Ramo 03, seguros del PJF, haber de retiro, tope
   salarial, declaración 3 de 3, periodos de sesiones, entre otras).
3. Abre tres categorías nuevas (Medio Ambiente, Trabajo y Salario,
   Instituciones) y mueve ahí los términos que ya existían.
4. Suma fichas bibliográficas de las leyes y documentos que las definiciones
   citan y que la plataforma ya enlazaba sin ficha.

Cada definición sale del texto vigente de su ley, descargado de la Cámara de
Diputados (LeyesBiblio) en septiembre de 2026, o de un documento oficial
publicado en el DOF o en gob.mx. Es idempotente: no duplica términos ni
fichas, y reescribir un término ya reescrito no cambia nada.
"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BASE = RAIZ / 'assets' / 'js' / 'audit-database.js'

AMB = '\U0001f30e Medio Ambiente'
TRA = '\U0001f477 Trabajo y Salario'
INS = '\U0001f3e2 Instituciones'
PRE = '\U0001f3db️ Presupuesto & ASF'
HAC = '\U0001f4b0 Hacendario & Deuda'
LEY = '\U0001f4dc Ley de Ingresos & Marco Legal'
FIS = '\U0001f50d Fiscalización Superior'
JUD = '⚖️ Poder Judicial'
LEG = '\U0001f5f3️ Poder Legislativo & Elecciones'

LFPRH = 'Ley Federal de Presupuesto y Responsabilidad Hacendaria'
PEF26 = 'PEF 2026 (DOF 21-11-2025)'
MANPJF = 'Manual de remuneraciones del PJF 2026 (DOF 27-02-2026)'

TERMINOS = [
    # --- Paquete Económico y reglas fiscales ---
    {'termino': 'Paquete Económico',
     'definicion': 'Los documentos que el Ejecutivo entrega cada año al Congreso para el año siguiente, a más tardar el 8 de septiembre: los Criterios Generales de Política Económica, la iniciativa de Ley de Ingresos con las reformas fiscales que proponga y el proyecto de Presupuesto de Egresos. En el año en que cambia la Presidencia, el plazo corre hasta el 15 de noviembre. Después, la Cámara de Diputados aprueba la Ley de Ingresos a más tardar el 20 de octubre y el Senado a más tardar el 31; el Presupuesto lo aprueba sólo la Cámara de Diputados, a más tardar el 15 de noviembre. El Paquete de 2027 se entregó el 8 de septiembre de 2026.',
     'ley': 'Art. 74 fr. IV CPEUM · Art. 42 frs. III a V ' + LFPRH,
     'categoria': LEY},
    {'termino': 'Criterios Generales de Política Económica (CGPE)',
     'definicion': 'El documento del Paquete Económico en el que Hacienda dice con qué supuestos armó los ingresos y el gasto del año siguiente —crecimiento, inflación, tasa de interés, tipo de cambio y precio del petróleo— y proyecta las finanzas públicas cinco años hacia adelante, incluidos los requerimientos financieros del sector público y su saldo histórico (SHRFSP). Por eso es la fuente oficial de la deuda total estimada: los CGPE 2027 estiman el SHRFSP al cierre de 2026 en 54.0 % del PIB (p. 67).',
     'ley': 'Arts. 16 y 42 fr. III inciso a) ' + LFPRH + ' · CGPE 2027, p. 67',
     'categoria': LEY},
    {'termino': 'Resolución Miscelánea Fiscal (RMF)',
     'definicion': 'Las reglas generales que el SAT publica cada año en el Diario Oficial para aplicar las leyes fiscales: trámites, plazos, formatos y, en sus anexos, las tablas de cálculo. El Anexo 8 de la RMF 2026 trae las tarifas mensuales y anuales del impuesto sobre la renta que usa la Calculadora Cívica. El Código Fiscal les pone un límite: cuando tocan sujeto, objeto, base, tasa o tarifa, no pueden crear obligaciones o cargas que las leyes no establezcan.',
     'ley': 'Art. 33 fr. I inciso g) Código Fiscal de la Federación · RMF 2026 y su Anexo 8 (DOF 28-12-2025)',
     'categoria': LEY},

    # --- Trabajo y salario (Calculadora Cívica) ---
    {'termino': 'Aguinaldo',
     'definicion': 'El pago anual que todo patrón debe hacer antes del 20 de diciembre: por lo menos quince días de salario, o la parte proporcional a quien no completó el año. Es un mínimo, no un tope: los manuales de remuneraciones de la Cámara de Diputados y del Poder Judicial fijan 40 días. Para el impuesto sobre la renta, una parte queda exenta: la ley habla de 30 días de salario mínimo, y desde la desindexación de 2016 ese límite se calcula con la UMA. Lo que pasa de ahí paga el impuesto.',
     'ley': 'Art. 87 Ley Federal del Trabajo · Art. 93 fr. XIV Ley del Impuesto sobre la Renta',
     'categoria': TRA},
    {'termino': 'Prima Vacacional',
     'definicion': 'El pago extra que acompaña a las vacaciones: no menos del 25 % del salario de los días de descanso. Desde la reforma que entró en vigor en 2023, el primer año de trabajo da derecho a doce días de vacaciones pagadas, así que la prima mínima equivale a tres días de salario. Hasta el equivalente a quince días de salario mínimo al año queda libre del impuesto sobre la renta.',
     'ley': 'Arts. 76 y 80 Ley Federal del Trabajo (reforma DOF 27-12-2022) · Art. 93 fr. XIV Ley del Impuesto sobre la Renta',
     'categoria': TRA},
    {'termino': 'Salario Mínimo (CONASAMI)',
     'definicion': 'La cantidad menor que debe recibir en efectivo una persona por una jornada de trabajo; la ley pide que alcance para las necesidades normales de una familia y que su revisión anual nunca quede por debajo de la inflación observada. Lo fija una comisión tripartita —trabajadores, patrones y gobierno—: la Comisión Nacional de los Salarios Mínimos. Para 2026 es de $315.04 diarios en el país y de $440.87 en la zona libre de la frontera norte.',
     'ley': 'Art. 123 apartado A fr. VI CPEUM · Arts. 90 y 94 Ley Federal del Trabajo · Resolución de la CONASAMI (DOF 9-12-2025)',
     'categoria': TRA},
    {'termino': 'Subsidio para el Empleo',
     'definicion': 'Una cantidad que se resta del impuesto que se retiene a quien gana poco. Desde 2024 dejó de ser una tabla por tramos y es un monto fijo: el valor mensual de la UMA multiplicado por 15.02 %, para quien no rebasa $11,492.66 al mes en 2026. Si el subsidio es mayor que el impuesto, no hay impuesto a cargo, pero tampoco se entrega la diferencia.',
     'ley': 'Decreto que reforma el diverso por el que se otorga el subsidio para el empleo (DOF 31-12-2025)',
     'categoria': TRA},
    {'termino': 'Retención del ISR (Tarifa del Artículo 96)',
     'definicion': 'El impuesto que el patrón descuenta cada mes del salario y entrega al SAT como pago provisional del impuesto anual. Se calcula con una tarifa de once tramos: cada tramo tiene una cuota fija y un porcentaje que se aplica sobre lo que el ingreso excede su límite inferior. A quien sólo gana un salario mínimo no se le retiene. Las tablas vigentes se publican en el Anexo 8 de la Resolución Miscelánea Fiscal.',
     'ley': 'Art. 96 Ley del Impuesto sobre la Renta · Anexo 8 de la RMF 2026 (DOF 28-12-2025)',
     'categoria': TRA},
    {'termino': 'Cuota Obrera del IMSS',
     'definicion': 'La parte de las cuotas de seguridad social que paga la propia persona trabajadora y que el patrón le descuenta del salario: por enfermedades y maternidad, invalidez y vida, y cesantía en edad avanzada y vejez. Se calcula sobre el salario base de cotización, con porcentajes distintos por seguro y un tope medido en UMA. El patrón y el gobierno pagan su propia parte aparte.',
     'ley': 'Arts. 25, 106 fr. II, 107, 147 y 168 fr. II Ley del Seguro Social',
     'categoria': TRA},

    # --- Instituciones ---
    {'termino': 'Secretaría de Hacienda y Crédito Público (SHCP)',
     'definicion': 'La dependencia del Ejecutivo que calcula los ingresos de la Federación, redacta las iniciativas de leyes fiscales y de ingresos, maneja la deuda pública y formula el proyecto de Presupuesto de Egresos. De ella dependen el SAT y la Tesorería de la Federación, y es quien publica los informes trimestrales, la Cuenta Pública y los datos abiertos del presupuesto.',
     'ley': 'Art. 31 frs. II, III, V y XV Ley Orgánica de la Administración Pública Federal',
     'categoria': INS},
    {'termino': 'Servicio de Administración Tributaria (SAT)',
     'definicion': 'Órgano desconcentrado de la Secretaría de Hacienda con carácter de autoridad fiscal. Aplica la legislación fiscal y aduanera, fiscaliza a los contribuyentes y publica, entre otras cosas, la Resolución Miscelánea Fiscal y los listados del artículo 69-B del Código Fiscal: las empresas que facturan operaciones simuladas.',
     'ley': 'Arts. 1o. y 2o. Ley del Servicio de Administración Tributaria',
     'categoria': INS},
    {'termino': 'Instituto Nacional de Estadística y Geografía (INEGI)',
     'definicion': 'Organismo con autonomía técnica y de gestión que norma y coordina el Sistema Nacional de Información Estadística y Geográfica. Produce el PIB, el INPC, los censos y, para esta plataforma, las Cuentas Económicas y Ecológicas y la estadística de finanzas públicas estatales y municipales. También calcula el valor de la UMA.',
     'ley': 'Art. 26 apartado B CPEUM · Art. 52 Ley del Sistema Nacional de Información Estadística y Geográfica',
     'categoria': INS},
    {'termino': 'Consejo Nacional de Población (CONAPO)',
     'definicion': 'El órgano a cargo de la planeación demográfica del país. Publica las proyecciones de población que se usan para repartir cifras entre habitantes: el número de personas que la plataforma usa como denominador (134.4 millones a mitad de 2026) viene de sus proyecciones.',
     'ley': 'Art. 5o. Ley General de Población',
     'categoria': INS},
    {'termino': 'Secretaría de Medio Ambiente y Recursos Naturales (SEMARNAT)',
     'definicion': 'La dependencia que fomenta la protección, restauración y aprovechamiento sustentable de los ecosistemas y recursos naturales para garantizar el derecho a un medio ambiente sano. Evalúa las manifestaciones de impacto ambiental de las obras federales y encabeza el Ramo 16 del Presupuesto.',
     'ley': 'Art. 32 Bis Ley Orgánica de la Administración Pública Federal',
     'categoria': INS},
    {'termino': 'Comisión Nacional del Agua (CONAGUA)',
     'definicion': 'Órgano desconcentrado de la SEMARNAT que ejerce la autoridad federal en materia de aguas nacionales: administra concesiones, cuencas y acuíferos, y es el órgano técnico y normativo de la Federación en la gestión del agua. Su presupuesto forma parte del Ramo 16.',
     'ley': 'Art. 9 Ley de Aguas Nacionales',
     'categoria': INS},
    {'termino': 'Instituto Mexicano del Seguro Social (IMSS)',
     'definicion': 'Organismo público descentralizado, de integración tripartita —sector público, social y privado—, que organiza y administra el Seguro Social. Es también organismo fiscal autónomo: cobra las cuotas obrero-patronales. Su registro de puestos de trabajo afiliados es la serie con la que la plataforma mide el empleo formal al comparar sexenios.',
     'ley': 'Art. 5 Ley del Seguro Social',
     'categoria': INS},
    {'termino': 'Rescate Bancario: FOBAPROA e IPAB',
     'definicion': 'El FOBAPROA era el fideicomiso de protección al ahorro de la Ley de Instituciones de Crédito con el que el gobierno sostuvo a los bancos en la crisis de 1994-1995. En 1999 la Ley de Protección al Ahorro Bancario creó el Instituto para la Protección al Ahorro Bancario (IPAB), que administra el sistema de protección al ahorro, y dejó al viejo fideicomiso sólo para liquidar sus operaciones. Lo que el rescate sigue costando se paga cada año con el Ramo 34: $35,553.4 millones de pesos en 2026.',
     'ley': 'Arts. 1o. y 2o. y transitorio quinto Ley de Protección al Ahorro Bancario (DOF 19-01-1999) · ' + PEF26 + ', Anexo 8',
     'categoria': HAC},

    # --- Presupuesto, obra y método ---
    {'termino': 'Ramo 16 (Medio Ambiente y Recursos Naturales)',
     'definicion': 'El ramo del Presupuesto de Egresos de la SEMARNAT y los órganos de su sector, entre ellos la Comisión Nacional del Agua. Para 2026 se le aprobaron $45,564.1 millones de pesos. Es lo que la Federación destina a esa secretaría, no todo lo que el país gasta en proteger el ambiente: ese dato más amplio lo mide el INEGI como gasto en protección ambiental.',
     'ley': PEF26 + ', Anexo 1 · Art. 32 Bis Ley Orgánica de la Administración Pública Federal',
     'categoria': PRE},
    {'termino': 'Sobrecosto',
     'definicion': 'La diferencia entre lo que una obra terminó costando y lo que se presupuestó al aprobarla. No es por sí mismo una irregularidad: puede venir de cambios de proyecto, de precios o de plazos. Pero cada aumento debe pasar por un convenio justificado de manera fundada y explícita, sin cambiar la naturaleza de la obra, y se informa al órgano interno de control. La reforma de abril de 2025 a la Ley de Obras Públicas quitó del artículo 59 el antiguo tope del 25 % para esos convenios.',
     'ley': 'Art. 59 Ley de Obras Públicas y Servicios Relacionados con las Mismas (reforma DOF 16-04-2025)',
     'categoria': FIS},
    {'termino': 'Ente Público',
     'definicion': 'Todo órgano que maneja dinero público y debe llevar contabilidad gubernamental: los poderes Ejecutivo, Legislativo y Judicial de la Federación y de los estados, los órganos autónomos, los ayuntamientos, las alcaldías de la Ciudad de México y las entidades paraestatales federales, estatales o municipales.',
     'ley': 'Art. 4 fr. XII Ley General de Contabilidad Gubernamental',
     'categoria': PRE},
    {'termino': 'Sexenio',
     'definicion': 'El periodo de seis años de un gobierno federal. La Presidencia de la República empieza el 1 de octubre y dura seis años, sin reelección posible. Cuando la plataforma compara sexenios, cada uno se cuenta por los años completos de su gobierno y la fuente de cada cifra se dice aparte.',
     'ley': 'Art. 83 CPEUM',
     'categoria': LEG},
    {'termino': 'Promedio por Habitante (Per Cápita)',
     'definicion': 'Una cifra nacional dividida entre el número de habitantes. Sirve para traer un monto de billones a una escala que se entiende, pero es un promedio: nadie paga, debe ni contamina a partes iguales. En esta plataforma el denominador es la población de CONAPO a mitad de 2026 (134.4 millones), y toda cifra por habitante lleva el chip «derivado» con la operación dicha.',
     'ley': 'Método de la plataforma · CONAPO, Proyecciones de la Población de México y las entidades federativas 2020-2070',
     'categoria': HAC},
    {'termino': 'Bandera Roja (Radar de la Plataforma)',
     'definicion': 'En esta plataforma, una bandera roja no es una acusación: es una señal para mirar primero. El radar ordena a las entidades según el dinero federal que dejaron por aclarar ante la Auditoría Superior en la Cuenta Pública 2024: por cada $100 revisados, por monto total o por la parte que toca a sus municipios. Un monto por aclarar todavía puede solventarse con documentos; por eso la bandera invita a leer el informe individual antes de concluir.',
     'ley': 'Método de la plataforma · ASF, Matriz de Datos Básicos de la Cuenta Pública 2024 (montos por aclarar por entidad federativa)',
     'categoria': FIS},

    # --- Medio ambiente ---
    {'termino': 'Residuos Sólidos Urbanos',
     'definicion': 'La basura de todos los días: lo que se genera en las casas al desechar materiales, productos, envases y empaques, lo que sale de otros lugares con características domiciliarias y lo que deja la limpieza de calles y lugares públicos. Recogerla, trasladarla, tratarla y darle disposición final es servicio público del municipio, por mandato constitucional.',
     'ley': 'Art. 115 fr. III inciso c) CPEUM · Arts. 5 fr. XXXIII y 10 Ley General para la Prevención y Gestión Integral de los Residuos',
     'categoria': AMB},
    {'termino': 'Cambio Climático',
     'definicion': 'La variación del clima atribuida directa o indirectamente a la actividad humana, que altera la composición de la atmósfera global y se suma a la variabilidad natural del clima. La ley la distingue de la variación natural: lo que la política pública puede atender es la parte que provocamos.',
     'ley': 'Art. 3 fr. IV Ley General de Cambio Climático',
     'categoria': AMB},
    {'termino': 'Gases de Efecto Invernadero',
     'definicion': 'Los componentes gaseosos de la atmósfera, naturales o producidos por la actividad humana, que absorben y emiten radiación infrarroja; su acumulación es la causa principal del cambio climático. Su emisión se estima en el inventario nacional que prevé la Ley General de Cambio Climático.',
     'ley': 'Art. 3 fr. XXIII Ley General de Cambio Climático',
     'categoria': AMB},
    {'termino': 'Impuesto al Carbono (IEPS a Combustibles Fósiles)',
     'definicion': 'La parte del IEPS que grava la venta e importación de combustibles fósiles —propano, butano, gasolinas, turbosina, diésel, combustóleo, coque y carbón— con una cuota fija por unidad de cada combustible. Es el impuesto federal más cercano a la idea de que quien contamina paga, aunque su cuota es de centavos por litro.',
     'ley': 'Art. 2 fr. I inciso H) Ley del Impuesto Especial sobre Producción y Servicios',
     'categoria': AMB},
    {'termino': 'Cuentas Económicas y Ecológicas de México (CEEM)',
     'definicion': 'La estadística del INEGI que pone en pesos lo que la economía le cuesta al ambiente: el agotamiento de recursos naturales, la degradación del aire, el agua y el suelo, y lo que se gasta en proteger el ambiente. De ellas salen el PIB ecológico (PINE) y los costos totales por agotamiento y degradación: $1,382,214 millones de pesos en 2024. Se publican cada diciembre con los datos del año anterior.',
     'ley': 'INEGI, Cuentas Económicas y Ecológicas de México 2024 (1-12-2025) · Art. 26 apartado B CPEUM',
     'categoria': AMB},
]

# Términos que ya existían y se reescriben. La clave es el nombre actual; si
# el término se renombra, el nombre nuevo entra en «termino». Sólo se cambia
# lo que se da; lo demás del objeto se conserva.
REESCRITURAS = {
    'Partida Secreta / Ramo 23 / Subvenciones Opacas': {
        'termino': 'Ramo 23 (Provisiones Salariales y Económicas) y la Partida Secreta',
        'definicion': 'Dos cosas que conviene no confundir. La partida secreta era una bolsa del Presupuesto que el Ejecutivo podía gastar sin decir en qué; la Constitución la prohibió en 2021: «no podrá haber partidas secretas en el Presupuesto de Egresos de la Federación». El Ramo 23, en cambio, sigue vivo y es público: guarda las provisiones salariales y económicas —ajustes de sueldos, fondos para estados y municipios, reservas— que después se reparten a otros ramos. Para 2026 se le aprobaron $167,652.2 millones de pesos. Es un ramo de reasignación, y por eso conviene seguir a dónde va a dar.',
        'ley': 'Art. 74 fr. IV CPEUM (reforma DOF 17-05-2021) · ' + PEF26 + ', Anexos 1 y 20',
        'categoria': PRE},
    'Costo Financiero de la Deuda': {
        'definicion': 'Lo que el sector público paga cada año por deber: intereses, comisiones y gastos de la deuda, sin contar lo que se abona al capital. El Presupuesto 2026 lo reúne en su Anexo 8: $1,297,681.1 millones de pesos del Gobierno Federal (Ramo 24), $238,838.8 millones de las empresas públicas y $35,553.4 millones de los programas de apoyo a ahorradores y deudores de la banca (Ramo 34). En total, $1,572,073.3 millones: es gasto no programable, se paga antes que cualquier programa.',
        'ley': PEF26 + ', Anexo 8 · Ley Federal de Deuda Pública',
        'categoria': HAC},
    'FASSA / IMSS-Bienestar': {
        'termino': 'FASSA e IMSS-Bienestar',
        'definicion': 'El Fondo de Aportaciones para los Servicios de Salud es el fondo del Ramo 33 que financia la salud de los estados. Desde 2024 la ley distingue dos casos: la entidad que no firma convenio con los Servicios de Salud del IMSS para el Bienestar (IMSS-Bienestar) ejerce el fondo por sí misma; la que lo firma transfiere a ese organismo el personal, la infraestructura y los recursos que acuerden, y conserva del fondo sólo lo necesario para las obligaciones que le quedan.',
        'ley': 'Arts. 25 y 29 Ley de Coordinación Fiscal (reforma DOF 03-01-2024) · Art. 77 bis 16 A Ley General de Salud'},
    'Partida de Gestión Social (Congresos)': {
        'definicion': 'Recursos que algunos congresos asignan a sus legisladores para atender peticiones de su distrito: despensas, apoyos o pequeñas obras. Su riesgo está en la discrecionalidad: cuando no hay reglas públicas de quién recibe y por qué, se vuelven difíciles de fiscalizar. La plataforma no tiene todavía un documento oficial que cuantifique estas partidas por congreso.',
        'ley': 'Presupuestos y reglamentos de cada congreso (sin documento integrado en la plataforma)'},
    'Ponencia de Ministro(a) (SCJN)': {
        'definicion': 'El despacho y el equipo jurídico de cada ministra o ministro de la Suprema Corte: secretarias y secretarios de estudio y cuenta, auxiliares y personal de apoyo que estudian los expedientes, revisan precedentes y redactan los proyectos de sentencia que se votan en el Pleno. Desde la reforma judicial, el Pleno tiene nueve integrantes y por tanto nueve ponencias.',
        'ley': 'Art. 94 CPEUM (reforma DOF 15-09-2024) · Presupuesto analítico de plazas del ' + MANPJF},
    'Secretario(a) de Estudio y Cuenta': {
        'definicion': 'Persona funcionaria judicial adscrita a una ponencia que analiza amparos, controversias y acciones de inconstitucionalidad y redacta los proyectos de sentencia. Su remuneración se fija en el manual anual del Poder Judicial según su nivel; la plataforma la cita de ese documento y no de estimaciones.',
        'ley': 'Ley Orgánica del Poder Judicial de la Federación · ' + MANPJF},
    'Asesoría de Ponencia y Récord de Plazas (Más de 70 asesores)': {
        'termino': 'Asesoría de Ponencia',
        'definicion': 'Personal de confianza o por honorarios que apoya a las ponencias con investigación jurídica. Cuántas plazas tiene cada ponencia se lee en el presupuesto analítico de plazas del manual anual del Poder Judicial; la cifra de «más de 70 asesores por ministro» que circuló en el debate público no tiene documento citado en la plataforma y no se usa.',
        'ley': MANPJF + ', Anexo B · Plataforma Nacional de Transparencia'},
    'Artículo 127 Constitucional (Tope Salarial)': {
        'definicion': 'El precepto que prohíbe a cualquier persona servidora pública de la Federación, los estados y los municipios ganar más que la Presidencia de la República. Para 2026, la remuneración ordinaria neta de la Presidenta es de $134,290 al mes ($193,706 brutos). La reforma judicial de 2024 ordenó ajustar a ese tope los sueldos del Poder Judicial en funciones, sin excepción.',
        'ley': 'Art. 127 fr. II CPEUM · Transitorio séptimo del decreto DOF 15-09-2024 · ' + PEF26 + ', Anexo 23.1.2'},
    'Fideicomisos del Poder Judicial (Extinción y Litigio)': {
        'definicion': 'Los fideicomisos que la Suprema Corte y el Consejo de la Judicatura Federal constituyeron con recursos públicos para pensiones complementarias, vivienda y otros fines. El Congreso ordenó extinguirlos y reintegrar su dinero a la Tesorería de la Federación mediante reforma publicada en octubre de 2023, y la extinción se impugnó en tribunales.',
        'ley': 'Decreto de reforma a la Ley Orgánica del Poder Judicial de la Federación (DOF 27-10-2023)'},
    'Consejo de la Judicatura Federal (CJF)': {
        'definicion': 'El órgano que administraba, vigilaba y disciplinaba a los juzgados de distrito y tribunales de circuito. La reforma judicial de 2024 lo sustituyó por dos órganos: el Tribunal de Disciplina Judicial, que sanciona, y el Órgano de Administración Judicial, que administra. En el Presupuesto 2026 ya no tiene asignación: el Ramo 03 incluye en su lugar al Órgano de Administración Judicial.',
        'ley': 'Art. 100 CPEUM (régimen previo y reforma DOF 15-09-2024)'},
    'Haber de Retiro': {
        'definicion': 'La pensión que recibían las ministras y los ministros de la Suprema Corte al concluir su encargo. La reforma judicial de 2024 dispuso que quienes dejaran la Corte por no postularse o no ser electos en 2025 no la recibirían, salvo si renunciaban antes del cierre de la convocatoria, en cuyo caso sería proporcional al tiempo servido. Los haberes ya concedidos se conservan.',
        'ley': 'Transitorio séptimo del decreto de reforma judicial (DOF 15-09-2024) · Art. 127 fr. IV CPEUM'},
    'Seguro de Separación Individualizado (SSI)': {
        'definicion': 'Un seguro al que el personal de mando medio del Poder Judicial puede incorporarse voluntariamente, para tener un ahorro si se separa del servicio. La persona aporta el 2, 4, 5 o 10 % de su sueldo básico y el Poder Judicial aporta una prima igual, con dinero público.',
        'ley': MANPJF + ', numeral 8.1.4'},
    'Seguro de Gastos Médicos Mayores (SGMM)': {
        'definicion': 'Un seguro con cargo al presupuesto que cubre accidentes y enfermedades que requieren cirugía u hospitalización, para la persona servidora pública y su familia directa. En el Poder Judicial lo reciben el personal de mando medio y el operativo, con una suma asegurada básica de hasta 333 UMA mensuales, que la persona puede ampliar a su cargo.',
        'ley': MANPJF + ', numeral 8.1.3'},
    'Ramo 03 (Poder Judicial de la Federación)': {
        'definicion': 'El ramo del Presupuesto de Egresos del Poder Judicial de la Federación: la Suprema Corte, el Tribunal Electoral, el Tribunal de Disciplina Judicial y el Órgano de Administración Judicial. Para 2026 se le aprobaron $70,005.6 millones de pesos. Como ramo autónomo, el Poder Judicial elabora su propio proyecto y Hacienda lo integra al Presupuesto.',
        'ley': 'Art. 74 fr. IV CPEUM · ' + PEF26 + ', Anexo 1'},
    'Capítulo 1000 (Servicios Personales)': {
        'definicion': 'El capítulo del clasificador por objeto del gasto que reúne todo lo que se paga a las personas: sueldos, honorarios asimilados, aguinaldo, primas, estímulos y aportaciones de seguridad social. Es la nómina del Estado, y en las instituciones que prestan servicios con personal —tribunales, escuelas, hospitales— suele ser la mayor parte de su presupuesto.',
        'ley': 'Clasificador por Objeto del Gasto (CONAC) · Ley General de Contabilidad Gubernamental'},
    'Auditoría Forense': {
        'definicion': 'Tipo de auditoría que la ASF clasifica como «de cumplimiento forense»: revisa con técnicas de investigación operaciones en las que hay indicios de irregularidad, para documentar los hechos y, en su caso, sostener una denuncia o una promoción de responsabilidad. En la Matriz de Datos Básicos de la Cuenta Pública 2024 aparece en auditorías al Consejo de la Judicatura Federal, al Tribunal Electoral y al INAI, entre otras.',
        'ley': 'ASF, Matriz de Datos Básicos de la Cuenta Pública 2024 (tipo de auditoría «De Cumplimiento Forense») · Ley de Fiscalización y Rendición de Cuentas de la Federación'},
    'Declaración 3 de 3 (Patrimonial, Intereses y Fiscal)': {
        'definicion': 'Las tres declaraciones que toda persona servidora pública debe presentar: la de situación patrimonial (lo que tiene), la de intereses (los vínculos que podrían chocar con su cargo) y la constancia de su declaración fiscal anual. Se presentan bajo protesta de decir verdad ante la Secretaría Anticorrupción o el órgano interno de control, al entrar, cada año y al salir del cargo.',
        'ley': 'Art. 108 CPEUM · Arts. 32 y 33 Ley General de Responsabilidades Administrativas'},
    'Periodos Ordinarios de Sesiones del Congreso': {
        'definicion': 'Los dos periodos en que el Congreso sesiona cada año: el primero empieza el 1 de septiembre y puede durar hasta el 15 de diciembre (hasta el 31 cuando la Presidencia inicia su encargo ese año); el segundo empieza el 1 de febrero y no puede pasar del 30 de abril. En el primero caen la Ley de Ingresos y el Presupuesto de Egresos del año siguiente.',
        'ley': 'Arts. 65 y 66 CPEUM'},
    'Concejalías de las Alcaldías CDMX': {
        'definicion': 'Cada alcaldía de la Ciudad de México se integra por su titular y un concejo de concejales electos, con mayoría y representación proporcional, que supervisa y evalúa la acción de gobierno, el presupuesto y el gasto de la alcaldía. El número de concejales por alcaldía está en la Constitución de la Ciudad; la plataforma aún no lo cita de su texto.',
        'ley': 'Constitución Política de la Ciudad de México, art. 53'},
}

# Términos que cambian de categoría. Nombre exacto -> categoría nueva.
RECATEGORIZAR = {
    'Producto Interno Neto Ecológico': AMB,
    'Costos Totales por Agotamiento y Degradación Ambiental': AMB,
    'Agotamiento de Recursos Naturales': AMB,
    'Degradación Ambiental': AMB,
    'Externalidad Negativa': AMB,
    'Impuesto Pigouviano': AMB,
    'Manifestación de Impacto Ambiental': AMB,
    'Capital Natural': AMB,
    'Estrés Hídrico': AMB,
    'Matriz Energética': AMB,
    'Gasto en Protección Ambiental': AMB,
    'Desarrollo Sustentable': AMB,
    'Aportaciones de Seguridad Social': TRA,
    'Remuneración Total Anual Neta': TRA,
    'UMA (Unidad de Medida y Actualización)': TRA,
    'TESOFE (Tesorería de la Federación)': INS,
    'Auditoría Superior de la Federación (ASF)': INS,
    'Fiscalía Especializada en Materia de Combate a la Corrupción (FEMCC)': INS,
    'Transparencia para el Pueblo (Autoridad Garante)': INS,
    'Tribunal Electoral del Poder Judicial de la Federación (TEPJF)': INS,
}

LEYES = 'leyes_federales'
LEYES_N = 'Leyes Hacendarias y Presupuestales'
OFI = 'fuentes_oficiales'
OFI_N = 'Fuentes Oficiales & Datos Abiertos'
TRIB = 'tributario'
TRIB_N = 'Marco Tributario y Fiscal'

REF_NUEVAS = [
    {'num': 90, 'id': 'ref-lft', 'categoria': LEYES, 'categoria_nombre': LEYES_N,
     'cita_apa': 'Ley Federal del Trabajo [LFT]. Diario Oficial de la Federación, 1 de abril de 1970, última reforma 14 de mayo de 2026 (México). Cámara de Diputados del H. Congreso de la Unión.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf',
     'descripcion': 'Fija los mínimos de toda relación de trabajo. La plataforma cita sus artículos 76 (vacaciones), 80 (prima vacacional), 87 (aguinaldo), 90 (salario mínimo) y 94 (la comisión que lo fija). Es la regla con la que la Calculadora Cívica compara las prestaciones de quien la usa con las de los altos cargos.'},
    {'num': 91, 'id': 'ref-loapf', 'categoria': LEYES, 'categoria_nombre': LEYES_N,
     'cita_apa': 'Ley Orgánica de la Administración Pública Federal [LOAPF]. Diario Oficial de la Federación, 29 de diciembre de 1976, última reforma 7 de mayo de 2026 (México). Cámara de Diputados del H. Congreso de la Unión.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LOAPF.pdf',
     'descripcion': 'Reparte los asuntos entre las secretarías de Estado. Su artículo 31 dice qué hace Hacienda (ingresos, deuda y proyecto de presupuesto) y el 32 Bis qué hace la SEMARNAT.'},
    {'num': 92, 'id': 'ref-lsnieg', 'categoria': LEYES, 'categoria_nombre': LEYES_N,
     'cita_apa': 'Ley del Sistema Nacional de Información Estadística y Geográfica [LSNIEG]. Diario Oficial de la Federación, 16 de abril de 2008, última reforma 14 de noviembre de 2025 (México). Cámara de Diputados del H. Congreso de la Unión.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LSNIEG.pdf',
     'descripcion': 'Regula al INEGI y la información de interés nacional. Su artículo 52 le da autonomía técnica y de gestión. De ese sistema salen el PIB, el INPC, los censos y las Cuentas Económicas y Ecológicas que usa la plataforma.'},
    {'num': 93, 'id': 'ref-lgpob', 'categoria': LEYES, 'categoria_nombre': LEYES_N,
     'cita_apa': 'Ley General de Población. Diario Oficial de la Federación, 7 de enero de 1974, última reforma 16 de julio de 2025 (México). Cámara de Diputados del H. Congreso de la Unión.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGP.pdf',
     'descripcion': 'Su artículo 5o. crea el Consejo Nacional de Población, a cargo de la planeación demográfica. De sus proyecciones sale el número de habitantes con que la plataforma reparte cifras por persona.'},
    {'num': 94, 'id': 'ref-lan', 'categoria': LEYES, 'categoria_nombre': LEYES_N,
     'cita_apa': 'Ley de Aguas Nacionales [LAN]. Diario Oficial de la Federación, 1 de diciembre de 1992, última reforma 11 de diciembre de 2025 (México). Cámara de Diputados del H. Congreso de la Unión.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LAN.pdf',
     'descripcion': 'Regula las aguas nacionales. Su artículo 9 define a la Comisión Nacional del Agua como órgano desconcentrado de la SEMARNAT y autoridad federal en materia hídrica.'},
    {'num': 95, 'id': 'ref-lpab', 'categoria': 'hacendario_fiscal', 'categoria_nombre': 'Hacendario y Fiscal',
     'cita_apa': 'Ley de Protección al Ahorro Bancario [LPAB]. Diario Oficial de la Federación, 19 de enero de 1999, última reforma 11 de mayo de 2022 (México). Cámara de Diputados del H. Congreso de la Unión.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LPAB.pdf',
     'descripcion': 'Crea el Instituto para la Protección al Ahorro Bancario (IPAB) y, en su transitorio quinto, deja al fideicomiso del FOBAPROA sólo para liquidar sus operaciones. Es el marco legal del rescate bancario que el Presupuesto sigue pagando con el Ramo 34.'},
    {'num': 96, 'id': 'ref-lgs', 'categoria': LEYES, 'categoria_nombre': LEYES_N,
     'cita_apa': 'Ley General de Salud. Diario Oficial de la Federación, 7 de febrero de 1984, última reforma 15 de enero de 2026 (México). Cámara de Diputados del H. Congreso de la Unión.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGS.pdf',
     'descripcion': 'Su artículo 77 bis 16 A regula los convenios con los que los estados pasan sus servicios de salud a IMSS-Bienestar. Explica por qué el FASSA se reparte distinto según si la entidad firmó o no.'},
    {'num': 97, 'id': 'ref-rmf2026', 'categoria': TRIB, 'categoria_nombre': TRIB_N,
     'cita_apa': 'Servicio de Administración Tributaria. (2025, 28 de diciembre). Resolución Miscelánea Fiscal para 2026 y sus Anexos 4, 5, 6, 8, 15 y 25. Diario Oficial de la Federación.',
     'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5777219&fecha=28/12/2025',
     'descripcion': 'El Anexo 8 contiene las tarifas mensuales y anuales del impuesto sobre la renta de 2026 que la Calculadora Cívica transcribió renglón por renglón. La resolución misma está en https://dof.gob.mx/nota_detalle.php?codigo=5777217&fecha=28/12/2025.'},
    {'num': 98, 'id': 'ref-uma2026', 'categoria': 'estadistica_oficial', 'categoria_nombre': 'Estadística Oficial del Estado Mexicano',
     'cita_apa': 'Instituto Nacional de Estadística y Geografía. (2026, 9 de enero). Unidad de Medida y Actualización. Diario Oficial de la Federación.',
     'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5778072&fecha=09/01/2026',
     'descripcion': 'Da a conocer el valor de la UMA vigente del 1 de febrero de 2026 al 31 de enero de 2027: $117.31 diarios y $3,566.22 mensuales. Con ella se calculan el tope de cotización al Seguro Social, el subsidio para el empleo y los límites exentos del ISR.'},
    {'num': 99, 'id': 'ref-conasami2026', 'categoria': 'estadistica_oficial', 'categoria_nombre': 'Estadística Oficial del Estado Mexicano',
     'cita_apa': 'Comisión Nacional de los Salarios Mínimos. (2025). Salarios mínimos vigentes a partir del 1 de enero de 2026 [tabla de la resolución publicada en el DOF el 9 de diciembre de 2025]. CONASAMI.',
     'url': 'https://www.gob.mx/cms/uploads/attachment/file/1041076/Tabla_de_Salarios_M_nimos_2026.pdf',
     'descripcion': 'El salario mínimo general de 2026 es de $315.04 diarios (13.0 % más que en 2025) y el de la zona libre de la frontera norte, de $440.87 (5.0 % más). La tabla incluye también los salarios mínimos profesionales.'},
    {'num': 100, 'id': 'ref-dip-manual2026', 'categoria': 'leyes_anuales', 'categoria_nombre': 'Paquete Económico Anual',
     'cita_apa': 'Cámara de Diputados. (2026, 27 de febrero). Manual que Regula las Remuneraciones para las y los Diputados Federales, Personal de Mando y Homólogos de la Cámara de Diputados, de la Unidad de Evaluación y Control y del Canal del Congreso, para el ejercicio fiscal 2026. Diario Oficial de la Federación.',
     'url': 'https://www.diputados.gob.mx/LeyesBiblio/marjur/marco/Dip_manual_remun_27feb26.pdf',
     'descripcion': 'Fija la dieta, las prestaciones y los días de aguinaldo del personal de la Cámara (Anexo 1). Es la fuente de las cifras de San Lázaro en la Calculadora Cívica.'},
    {'num': 101, 'id': 'ref-sen-manual2026', 'categoria': 'leyes_anuales', 'categoria_nombre': 'Paquete Económico Anual',
     'cita_apa': 'Cámara de Senadores. (2026, 27 de febrero). Manual de Remuneraciones de las Senadoras, Senadores, servidoras y servidores públicos de mando y homólogos, y la información relativa al Capítulo de Servicios Personales. Diario Oficial de la Federación.',
     'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5781138&fecha=27/02/2026',
     'descripcion': 'Fija la dieta y las prestaciones de las senadoras y los senadores para 2026. La plataforma lo coteja con el Anexo 23.2 del Presupuesto de Egresos.'},
    {'num': 102, 'id': 'ref-sat-69b', 'categoria': TRIB, 'categoria_nombre': TRIB_N,
     'cita_apa': 'Servicio de Administración Tributaria. (s. f.). Notificación a contribuyentes con operaciones presuntamente inexistentes y listados definitivos [artículo 69-B del Código Fiscal de la Federación]. Gobierno de México.',
     'url': 'https://www.gob.mx/sat/acciones-y-programas/notificacion-a-contribuyentes-con-operaciones-presuntamente-inexistentes-y-listados-definitivos-333336',
     'descripcion': 'Los listados oficiales de empresas que facturan operaciones simuladas. De aquí sale la copia que consulta el verificador del Modo Inspector; se actualiza a mano con cada corte del SAT.'},
    {'num': 103, 'id': 'ref-comprasmx', 'categoria': 'adquisiciones_compras', 'categoria_nombre': 'Compras Públicas y Contrataciones',
     'cita_apa': 'Secretaría Anticorrupción y Buen Gobierno. (s. f.). ComprasMX: Plataforma Digital de Contrataciones Públicas. Gobierno de México.',
     'url': 'https://comprasmx.buengobierno.gob.mx/',
     'descripcion': 'El portal federal donde se publican los procedimientos de contratación: licitaciones, invitaciones y adjudicaciones, con sus contratos. Es el lugar para buscar a quién se le pagó una obra o un servicio.'},
    {'num': 104, 'id': 'ref-imss-empleo', 'categoria': 'estadistica_oficial', 'categoria_nombre': 'Estadística Oficial del Estado Mexicano',
     'cita_apa': 'Instituto Mexicano del Seguro Social. (2025, enero). Puestos de trabajo afiliados al Instituto Mexicano del Seguro Social [boletín de prensa]. IMSS.',
     'url': 'https://www.imss.gob.mx/prensa/archivo/202501/009',
     'descripcion': 'El registro de puestos de trabajo afiliados al IMSS al cierre de 2024, serie oficial de empleo formal. La plataforma la usa para comparar sexenios junto con el boletín del cierre de 2018 (https://www.imss.gob.mx/prensa/archivo/201901/008).'},
]

# Fichas cuya descripción afirmaba cifras de otro año o sin documento.
CORRECCIONES_REF = [
    ('ref-cpeum-art127', 'descripcion',
     'Principio supremo de remuneración máxima que prohíbe a cualquier persona servidora pública percibir ingresos mayores a los del Presidente de la República ($134,310 pesos netos / $191,657 pesos brutos al mes). Pone fin a los sueldos tabulares previos de ministros que alcanzaban $206,948 netos ($297,404 brutos), vedando bonos discrecionales, pago de seguros médicos privados y seguros de separación con cargo a fondos públicos.',
     'Principio de remuneración máxima: ninguna persona servidora pública puede ganar más que la Presidencia de la República. Para 2026, la remuneración ordinaria neta de la Presidenta es de $134,290 al mes y la bruta de $193,706 (PEF 2026, Anexo 23.1.2). La reforma judicial de 2024 ordenó ajustar a ese tope los sueldos del Poder Judicial en funciones (transitorio séptimo).'),
]


def _valor(v):
    return json.dumps(v, ensure_ascii=False)


def _variantes(texto):
    """El archivo mezcla acentos reales y secuencias \\uXXXX."""
    crudo = json.dumps(texto, ensure_ascii=False)
    escapado = json.dumps(texto, ensure_ascii=True)
    return [crudo] if crudo == escapado else [crudo, escapado]


def _objeto(b, desde, hasta, clave, valor):
    """(inicio, fin) del objeto de nivel 4 que contiene "clave": valor."""
    for v in _variantes(valor):
        i = b.find('"%s": %s' % (clave, v), desde, hasta)
        if i >= 0:
            ini = b.rfind('\r\n    {', 0, i) + 2
            fin = b.index('\r\n    }', i) + len('\r\n    }')
            return ini, fin
    return None


def _cuerpo(obj):
    return '    {\r\n' + ',\r\n'.join('      "%s": %s' % (k, _valor(v)) for k, v in obj.items()) + '\r\n    }'


def _limites(b, clave):
    ini = b.index('"%s": [' % clave)
    return ini, b.index('\r\n  ]', ini)


def glosario(b):
    ini, fin = _limites(b, 'glosario')
    existentes = b[ini:fin]
    nuevos = ''
    agregados = 0
    for t in TERMINOS:
        if any('"termino": %s' % v in existentes for v in _variantes(t['termino'])):
            continue
        nuevos += ',\r\n' + _cuerpo(t)
        agregados += 1
    b = b[:fin] + nuevos + b[fin:]

    reescritos = 0
    for actual, cambios in REESCRITURAS.items():
        ini, fin = _limites(b, 'glosario')
        pos = _objeto(b, ini, fin, 'termino', actual)
        if not pos:
            nombre = cambios.get('termino')
            if nombre and _objeto(b, ini, fin, 'termino', nombre):
                continue  # ya se había reescrito
            sys.exit('No encuentro el término «%s»; no toco nada.' % actual)
        a, z = pos
        obj = json.loads(b[a:z])
        nuevo = dict(obj)
        nuevo.update(cambios)
        if nuevo != obj:
            b = b[:a] + _cuerpo(nuevo) + b[z:]
            reescritos += 1

    movidos = 0
    for termino, cat in RECATEGORIZAR.items():
        ini, fin = _limites(b, 'glosario')
        pos = _objeto(b, ini, fin, 'termino', termino)
        if not pos:
            sys.exit('No encuentro el término «%s» para moverlo.' % termino)
        a, z = pos
        obj = json.loads(b[a:z])
        if obj.get('categoria') != cat:
            obj['categoria'] = cat
            b = b[:a] + _cuerpo(obj) + b[z:]
            movidos += 1
    return b, agregados, reescritos, movidos


def referencias(b):
    ini, fin = _limites(b, 'referencias_legales')
    ancla = b.index('"id": "ref-transparencia-presupuestaria"', ini)
    corte = b.index('\r\n    }', ancla) + len('\r\n    }')
    agregadas = 0
    for ref in reversed(REF_NUEVAS):
        if '"id": "%s"' % ref['id'] in b:
            continue
        b = b[:corte] + ',\r\n' + _cuerpo(ref) + b[corte:]
        agregadas += 1
    cambios = 0
    for rid, campo, viejo, nuevo in CORRECCIONES_REF:
        ini, fin = _limites(b, 'referencias_legales')
        pos = _objeto(b, ini, fin, 'id', rid)
        if not pos:
            sys.exit('No encuentro la ficha %s.' % rid)
        a, z = pos
        obj = json.loads(b[a:z])
        if obj.get(campo) == viejo:
            obj[campo] = nuevo
            b = b[:a] + _cuerpo(obj) + b[z:]
            cambios += 1
    return b, agregadas, cambios


def main():
    b = BASE.read_bytes().decode('utf-8')
    b, tg, rg, mg = glosario(b)
    b, tr, cr = referencias(b)
    BASE.write_bytes(b.encode('utf-8'))
    print('glosario: %d términos nuevos, %d reescritos, %d cambiados de categoría' % (tg, rg, mg))
    print('referencias: %d fichas nuevas, %d corregidas' % (tr, cr))


if __name__ == '__main__':
    main()
