import json
from pathlib import Path
R=Path(__file__).resolve().parent
d=json.loads((R/'presupuesto-judicial-federal2026.json').read_text(encoding='utf-8'))
f=lambda n:f'{n:,.2f}'
mdp=lambda n:f'{n/1e6:,.6f}'
def src(k,label=None):return f"[{label or d['fuentes'][k]['titulo']}]({d['fuentes'][k]['url']})"
def table(head,rows):return '| '+' | '.join(head)+' |\n|'+'|'.join('---' for _ in head)+'|\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)+'\n'
units=d['unidades_pef'];tot=sum(x['aprobado'] for x in units)
scaps=[x for x in d['pef_objeto_gasto'] if x['ur']=='100' and x['nivel']=='capitulo']
ag=d['scjn_agosto_total']
parts={x['codigo']:x for x in d['scjn_agosto'] if x['nivel']=='partida'}
report='''# Presupuesto y distribución del Poder Judicial de la Federación

Investigación numérica para Auditavisión y su calculadora cívica. Consulta: **25 de septiembre de 2026**. Pesos mexicanos nominales. Ámbito exclusivamente federal.

## 1. Alcance y criterio de investigación

Se siguió el método de la investigación «Investigar finanzas legislativo»: fuente oficial por registro, conservación del periodo, conciliación aritmética y separación entre hechos, cálculos y faltantes. La enciclopedia aporta la estructura temática de las secciones 4.1 a 4.5; sus cifras no se aceptan por el solo hecho de existir en el proyecto.

El eje de esta entrega es el **presupuesto aprobado 2026**. Para profundizar en su ejecución se incorpora el corte de agosto de la SCJN y el segundo trimestre del OAJ. El cierre 2025 de la SCJN sirve como antecedente anual. No se presentan proyectos 2027 como recursos recibidos, ni 2026 como ejercicio cerrado. No se incorporan poderes judiciales estatales, fiscalías, tribunales administrativos ajenos al Ramo 03 ni gasto electoral del INE.

«Aprobado» es autorización de gasto; no acredita que todo ese dinero haya sido recibido o pagado. Se preservan las categorías que cada documento usa: modificado, devengado, pagado, compromiso, ejercido y disponible. «Oficial» identifica procedencia documental; no implica que dos documentos oficiales sean automáticamente comparables ni que estén libres de discrepancias.

Los registros originales llevan `oficial`, las sumas y proporciones `derivado`, y las cifras no verificadas `pendiente`, con valor nulo. La futura interfaz debe representarlos con `chipEstado(estado)`.

## 2. Cuánto se aprobó y cómo se reparte entre instituciones

'''
report+=table(['Unidad responsable','Presupuesto aprobado 2026, pesos','Parte del Ramo 03, derivada'],[[x['nombre']+' (UR '+x['ur']+')',f(x['aprobado']),f"{100*x['aprobado']/tot:.4f}%"] for x in units]+[['Total Ramo 03',f(tot),'100.0000%']])
report+=f'''
Fuentes: {src('UR')} (p. 1), {src('COG')} (pp. 3–8) y {src('PEF')} (anexos 1 y 32). Las cinco unidades suman exactamente el total aprobado. Sala Superior y Salas Regionales integran el TEPJF: **{f(2931820871+817672006)} pesos**. El presupuesto de las Salas Regionales es conjunto; no debe repetirse como asignación de cada sala.

El proyecto del Ramo 03 fue de 85,960,228,646 pesos y el aprobado de 70,005,628,646: reducción de 15,954,600,000 pesos. La SCJN solicitó 5,869,743,404 y recibió una autorización de 5,208,743,404: diferencia de 661,000,000 pesos, equivalente a **{661000000/5869743404*100:.4f}% del solicitado**. Son diferencias proyecto/aprobado, no ahorros comprobados del ejercicio. Fuente: anexo 32 del decreto PEF 2026.

El OAJ registra la principal bolsa del Ramo; esa bolsa cubre la operación de la justicia federal y su administración, no sólo el costo de sus integrantes. Tampoco es presupuesto propio de la SCJN. Las transferencias internas y los gastos ya incluidos no se vuelven a sumar.

### Por capítulo en las cinco unidades

'''
codes=['1000','2000','3000','4000','5000','6000']
pefmap={(x['ur'],x['codigo']):x['aprobado'] for x in d['pef_objeto_gasto'] if x['nivel']=='capitulo'}
report+=table(['Unidad','1000 Personal','2000 Materiales','3000 Servicios','4000 Transferencias','5000 Bienes','6000 Obra'],[[x['nombre']]+[mdp(pefmap[(x['ur'],c)]) if (x['ur'],c) in pefmap else 'No mostrado' for c in codes] for x in units])
report+='\nImportes en **millones de pesos**, convertidos de los pesos originales (estado `derivado`). «No mostrado» conserva una ausencia en este cuadro; no crea un registro de cero. Fuente: distribución SHCP, pp. 3–8. Los capítulos positivos publicados concilian con el total de cada unidad. El Excel conserva pesos y conceptos inferiores.\n'
report+=f'''
## 3. SCJN: en qué se integra el presupuesto

'''
report+=table(['Capítulo','Concepto','Aprobado, pesos','Por cada $100 del presupuesto'],[[x['codigo'],x['concepto'],f(x['aprobado']),f(100*x['aprobado']/5208743404)] for x in scaps])
report+=f'''
Fuente: {src('COG')} (pp. 3–4). La última columna es derivada. **Servicios personales absorbe {4289319105/5208743404*100:.4f}%**. El complemento financia materiales, servicios, transferencias, bienes y obra. «Servicios personales» comprende a la institución entera: sueldos, compensaciones, seguridad social, prestaciones y otras obligaciones. No equivale a dinero entregado exclusivamente a las ministras y ministros.

### Partidas para analizar el gasto de personal y prestaciones

'''
selected=['11301','12101','12201','13101','13201','13202','14403','14404','15301','15401','15402','15403','15405']
report+=table(['Partida','Concepto','Original 2026, pesos','Modificado a agosto','Ejercido a agosto'],[[k,parts[k]['concepto'],f(parts[k]['original']),f(parts[k]['modificado']),f(parts[k]['ejercido'])] for k in selected])
report+=f'''
Fuente: {src('SCJN_AGO')} (pp. 1–2). Esta selección está **incluida** en el capítulo 1000; no se suma otra vez al presupuesto. La entrega incorpora las **127 partidas** del documento, con páginas y sus ocho columnas monetarias.

Las partidas de seguros y retiro son gastos institucionales. Su presencia no acredita que todas las personas ocupantes del cargo de ministro reciban cada prestación ni el mismo monto. El importe ejercido de prestaciones de retiro tampoco es el haber individual de una persona retirada. Se requiere identificar beneficiario, régimen y periodo antes de formular comparaciones personales.

### Operación y servicios de la Corte

El capítulo 3000 aprobado se distribuye en: servicios básicos 166,962,665; arrendamientos 149,220,658; servicios profesionales, científicos y técnicos 226,727,587; financieros, bancarios y comerciales 27,381,786; instalación, reparación y mantenimiento 124,265,584; comunicación social 3,650,000; traslados y viáticos 6,288,806; servicios oficiales 3,522,731; otros servicios generales 117,639,017 pesos. La suma es 825,658,834 pesos. Fuente: distribución SHCP, p. 3.

Los 4,000,000 pesos de inversión pública original se desagregan en 1,000,000 para obras de construcción de edificios y 3,000,000 para otros servicios relacionados con obras públicas. El presupuesto modificado de ambas partidas seguía siendo 4,000,000 al corte de agosto y el documento registra cero ejercido. Eso describe esas partidas y ese corte, no demuestra ausencia de mantenimiento en la institución: el mantenimiento también aparece en el capítulo 3000. Fuente: estado de agosto, p. 8.

## 4. SCJN: presupuesto autorizado frente a su ejercicio

'''
report+=table(['Corte','Aprobado/original','Modificado','Devengado','Pagado','Ejercido (columna propia)'],[
 ['Cierre 2025','5,208,511,164','5,273,784,802','5,273,784,802','5,032,120,580','No se usa'],
 ['Enero–junio 2026','5,208,743,404','5,208,743,404','2,503,691,579','2,101,258,527','No se usa'],
 ['Enero–agosto 2026',f(ag['original']),f(ag['modificado']),'No informado en este cuadro','No informado en este cuadro',f(ag['ejercido'])]])
report+=f'''
Fuentes: {src('SCJN_2025')} (p. 1), {src('SCJN_JUN')} (p. 1) y {src('SCJN_AGO')} (p. 8). **No se renombra «ejercido» de agosto como «pagado» ni como «devengado».** Tampoco se suman cortes acumulados.

Al cierre 2025, devengado menos pagado da **241,664,222 pesos**. Esta diferencia es aritmética; por sí sola no demuestra pérdida, irregularidad ni causa de la obligación pendiente. Entre los presupuestos originales de 2025 y 2026 hay **232,240 pesos** de aumento, **{232240/5208511164*100:.6f}% nominal**. No se calcula variación real sin un deflactor y una base temporal explícitos, ni se atribuye la diferencia a la reforma sin conciliar los cambios de estructura.

A agosto 2026, la ampliación neta es **21,329,111.57 pesos**. El documento permite verificar:

- Original + ampliaciones − reducciones = modificado: 5,208,743,404.00 + 1,630,537,675.97 − 1,609,208,564.40 = **5,230,072,515.57**.
- Compromiso + ejercido + disponible = modificado: 1,707,440,588.30 + 3,253,791,174.26 + 268,840,753.01 = **5,230,072,515.57**.
- Ejercido/modificado = **{ag['ejercido']/ag['modificado']*100:.4f}%**, indicador derivado con la definición de ese cuadro.

La partida disponible no es ahorro definitivo ni recurso libre que pueda reasignarse automáticamente. El estado semestral indica que presenta el subejercicio al cuarto trimestre; no corresponde fabricar un subejercicio anual definitivo con el corte de junio.

## 5. Circuitos, órganos jurisdiccionales y administración del OAJ

Se verificó la publicación trimestral que desglosa **140 unidades ejecutoras y 1,768 registros unidad/partida**, con pagos por **13,977,400,359.62 pesos**. Su periodo es **1 de abril a 30 de junio de 2026**, no enero–junio. Las sumas por unidad y por capítulo coinciden con ese total.

Fuentes: {src('OAJ_CAP')} y {src('OAJ_UEG_PAR')}. El archivo incluye unidades de los circuitos, centros de justicia penal federal, defensoría, escuela, servicios centrales y otras áreas con denominación oficial conservada.

### Distribución de pagos del trimestre por capítulo

'''
report+=table(['Capítulo','Asignado anual según OAJ','Asignado abril–junio','Pagado abril–junio'],[[x['capitulo'],f(x['asignado_anual']),f(x['asignado_trimestre']),f(x['pagado_trimestre'])] for x in d['oaj_capitulos_trimestre']])
report+='''
### Pagos registrados en unidades denominadas «Circuito Judicial»

Son **sumas derivadas por circuito de las unidades administrativas que la propia fuente denomina así**. No incluyen la nómina centralizada, ni se añaden automáticamente centros penales o edificios por su ubicación. La correspondencia usa denominación de la fuente, no la suposición «un estado = un circuito». Las claves UEG no son números de circuito: por ejemplo, 1230 corresponde a una coordinación consolidada, no al circuito XXX.

'''
report+=table(['Circuito','UEG incluidas','Pagado registrado abril–junio, pesos'],[[x['circuito'],', '.join(x['ueg_incluidas']),f(x['pagado_registrado_ueg'])] for x in d['circuitos']])
report+=f'''
Total de este subconjunto: **277,230,888.48 pesos**, ya incluido en el pagado OAJ. Fuente: {src('OAJ_UEG')}; operación: suma por las UEG de la tabla. En el detalle de estas UEG no aparecen partidas del capítulo 1000. Por eso, **el presupuesto completo de cada circuito permanece `pendiente`**. El Excel incorpora además las sedes y permite rastrear cada importe.

Ejemplo de centralización: las UEG «Pago de Servicios Personales por Acuerdo» (5203), «Dirección de Seguros (Prestaciones y Ayudas)» (5206) y «Pago de Servicios Personales por Sustituciones» (5209) registran pagos separados de las UEG de circuito. No es válido interpretar una dirección de nómina como si todo ese gasto remunerara sólo a quienes trabajan en esa dirección.

### Diferencias oficiales que requieren conciliación

1. **Clasificación OAJ.** SHCP publica 5,051,355,262 pesos en capítulo 3000 y 26,766,117 en 4000; la columna «asignado anual» del OAJ muestra 5,040,717,363 y 37,404,016. La diferencia de **10,637,899 pesos** se compensa entre capítulos y ambos conservan el total anual. Se mantienen ambas series con fuente; la causa y autorización de la reclasificación quedan pendientes. No se etiqueta como desvío.
2. **Primer trimestre OAJ.** El PDF de estados financieros muestra totales pagados diferentes: 10,581,142,471 por objeto del gasto (p. 41), 10,604,602,286 en clasificación económica (p. 42) y 11,131,726,896 en administrativa (p. 46). También difieren algunos devengados. No se arma un acumulado semestral mezclando esos cuadros con abril–junio hasta conciliar alcance y metodología. Fuente: {src('OAJ_MAR')}.

## 6. Comparativas precisas para la calculadora cívica

### Dos modos distintos

**Presupuesto institucional.** Se compara una cantidad de dinero con otra para comprender su escala. Puede elegirse SCJN, OAJ, TEPJF, TDJ, un capítulo o una partida. La entrada debe indicar ingreso mensual y naturaleza bruta o neta. El resultado será «equivalente a X ingresos anuales como el declarado», no una afirmación de que se pueda contratar ese número de trabajadores ni de que ese dinero lo reciba una sola persona.

**Remuneración individual.** Se compara un sueldo tabulado neto con ingreso neto, o bruto con bruto, del mismo periodo. La fuente oficial localizada más específica es el Manual de remuneraciones publicado el 27 de febrero de 2026. Su Anexo B, p. 8, fija para ministro **134,310 pesos mensuales netos** en la columna máxima; p. 9 registra **290,273 pesos netos anuales conjuntos de aguinaldo y prima vacacional**. Son referencias tabulares, no comprobantes del pago efectivamente recibido por cada ministro.

Fuente: {src('MANUAL')}. El anexo 23.5 del PEF contiene otros límites y rótulos; no se mezclan automáticamente con el tabulador posterior. Los 290,273 no deben etiquetarse solamente «aguinaldo». La operación 134,310 × 12 + 290,273 = **1,901,993 pesos** reúne únicamente estos conceptos netos; no es costo patronal total ni remuneración bruta anual integrada.

'''
report+=table(['Indicador','Operación','Condición y etiqueta'],[
 ['Parte del presupuesto','Monto del rubro / total del mismo órgano × 100','Mismo ejercicio, corte y momento contable. Derivado.'],
 ['Por cada $100','$100 × monto del rubro / total comparable','Es proporción presupuestaria, no trazabilidad individual del ISR.'],
 ['Equivalente en ingresos anuales','Monto institucional / (ingreso mensual × 12)','Ingreso positivo y naturaleza declarada. Equivalencia monetaria.'],
 ['Múltiplo salarial neto','Sueldo mensual neto tabulado / ingreso mensual neto','Bruto contra neto: cálculo bloqueado.'],
 ['Ingresos mensuales equivalentes al aguinaldo y prima','290,273 / ingreso mensual neto','Beneficios conjuntos anuales frente a un ingreso mensual.'],
 ['Variación del presupuesto','(Modificado − aprobado) / aprobado × 100','No sustituye el avance del ejercicio.'],
 ['Avance de ejercicio SCJN agosto','Ejercido / modificado × 100','Conservar rótulo «ejercido» y fecha de agosto.'],
 ['Costo de cada ponencia','Sin fórmula habilitada','Pendiente de asignación y nómina por adscripción.'],
 ['Costo total por circuito','Sin fórmula habilitada','Pagos UEG disponibles son parciales.']])
report+='''
Si el ingreso está vacío, es cero, negativo o no numérico, la calculadora debe pedir un importe válido y no mostrar cero ni infinito. No debe equiparar días calendario con jornadas laborales. El cálculo de «cuánto de mi ISR financia la Corte» sólo podría ser una distribución proporcional hipotética expresamente rotulada, nunca un rastreo del impuesto de esa persona.

El libro incluye una hoja de comparativas editable con un ingreso **hipotético** de 15,000 pesos mensuales netos. Este importe es una entrada ilustrativa, no un dato oficial ni una estimación del ingreso del usuario. Las fórmulas se actualizan al modificarlo.

## 7. Qué debe corregirse en la enciclopedia antes de integrar

La revisión del código fue focalizada en las cifras judiciales. No se ha auditado toda la enciclopedia ni se ha modificado la aplicación.

- El comparador principal del motor conserva **206,948 pesos mensuales** para ministros (`audit-engine.js`, alrededor de la línea 1553). No debe usarse como referencia vigente 2026 frente al tabulador revisado.
- La base mezcla sueldo histórico, sueldo topado y **5,529,450 pesos anuales integrados** sin una correspondencia documental por ejercicio en cada cifra. El dato anual requiere su expediente propio antes de reutilizarlo.
- La ponencia «promedio» de **35 plazas, 2,850,000 mensuales y 34,200,000 anuales**, y la suma para once ponencias, no sustituyen la nómina y adscripción oficial de las ponencias actuales. Se mantienen fuera de las comparativas verificadas.
- Las antiguas Salas y sus asignaciones estimadas deben conservarse como históricas con vigencia; no convertirse en órganos receptores actuales mediante división del presupuesto.
- Los honorarios asimilables a salarios identificados aquí están en la partida **12101, capítulo 1000**. La narrativa existente que los vincula genéricamente al capítulo 3000 necesita corregirse; los servicios profesionales contratados del capítulo 3000 son otra clasificación.
- Ningún presupuesto, pago o diferencia contable de este informe acredita por sí mismo una irregularidad. Se excluyeron afirmaciones de daño o corrupción y expedientes ASF porque esta solicitud se limita a integración y distribución del dinero.

## 8. Datos entregados, verificación y pendientes concretos

La base JSON contiene 5 unidades presupuestarias, 183 filas jerárquicas de capítulos y conceptos, 127 partidas SCJN con sus ocho momentos/columnas, 140 UEG, 1,768 pagos UEG/partida, 32 agregados parciales por circuito, cortes SCJN y referencias tabulares. Los padres e hijos de la clasificación están identificados y no deben agregarse entre niveles.

Se conciliaron exactamente los totales del PEF, los conceptos de cada capítulo, las partidas SCJN con sus capítulos y total, las ocho columnas del estado de agosto y todas las UEG con sus partidas. Se conservaron originales y huellas SHA-256. En los cuadros semestrales redondeados, la suma de capítulos puede diferir del total en pesos por redondeo, advertencia expresa de la fuente.

Quedan pendientes, con motivo definido:

1. **Costo completo por circuito, tribunal y juzgado:** falta vincular nómina centralizada, adscripción, inmuebles y gastos compartidos, sin reparto arbitrario por población o número de jueces.
2. **Presupuesto de cada ponencia y área interna SCJN:** las clasificaciones verificadas agrupan a la Corte en UR 100. Se requiere el presupuesto por unidad interna/centro de costo, plantilla autorizada y ocupada, nómina por adscripción y contratos. El total institucional no se divide entre nueve.
3. **Conciliación de diferencias OAJ:** obtener el acto de reclasificación y aclaración de los estados de marzo. Se documentó la diferencia en lugar de ocultarla.
4. **Pago individual y prestaciones efectivas:** el manual informa límites tabulares; para afirmar cuánto recibió cada persona hacen falta nómina del periodo y concepto, con régimen aplicable y actualizaciones posteriores verificadas.
5. **Desglose individual de las Salas Regionales del TEPJF y ejercicio del TDJ:** esta entrega acredita su presupuesto aprobado y capítulos; no inventa el pagado ni distribuye la bolsa de salas en partes iguales.
6. **Integración a la calculadora y publicación:** ésta es la investigación preparatoria solicitada. No se cambiaron assets, el sello ni la interfaz. La carpeta no es un repositorio Git reconocido; no fue posible hacer pull, commit ni push. Los resultados quedan guardados localmente y el avance se registra en CONTEXT.md.

Para cerrar los puntos 1 y 2, el requerimiento documental preciso es: presupuesto aprobado, modificado, comprometido, devengado, ejercido y pagado del ejercicio 2026 por unidad interna, centro de costo, órgano jurisdiccional, circuito y partida; catálogo de equivalencias de claves; nómina por adscripción y plazas; y reglas/documentos de distribución del gasto centralizado. Solicitar archivos tabulares, fecha de corte y aclaración de transferencias internas. Este texto define los datos faltantes; no se ha enviado ninguna solicitud externa.

## Catálogo de fuentes conservadas

'''
for k,s in d['fuentes'].items():report+=f"- **{k}:** {src(k)}. Copia local: `fuentes-judicial/{s['archivo']}`.\n"
(R/'presupuesto-judicial-federal2026.md').write_bytes(report.replace('\n','\r\n').encode('utf-8'))
print('Informe guardado:',len(report),'caracteres')
