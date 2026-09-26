from pathlib import Path
from decimal import Decimal as D
import json,sys
sys.stdout.reconfigure(encoding='utf-8')
r=Path(__file__).resolve().parent
m=json.loads((r/'datos-matriz-asf2024.json').read_text(encoding='utf-8'))
sources={
 'Diputados':'https://www.asf.gob.mx/Trans/Informes/IR2024b/Documentos/Auditorias/2024_0031_a.pdf',
 'Senado':'https://www.asf.gob.mx/Trans/Informes/IR2024b/Documentos/Auditorias/2024_0032_a.pdf',
 'Congresos':'https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2026/cnple/CNPLE_2025_RR.pdf',
 'Matriz':'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Matriz/MDB_Consolidado.pdf',
 'General':'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Auditorias/MR-GENERAL_a.pdf',
 'Cuernavaca':'https://cuernavaca.gob.mx/contabilidad/wp-content/uploads/2025/01/20a-Edo.-An.-del-Eje.-del-Pto.-de-E.-Clas.-Admin-Subejer-1.pdf',
 'Nuevo León':'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Auditorias/2024_1402_a.pdf',
 'Tlaxcala':'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Auditorias/2024_1940_a.pdf',
}
names=['Ciudad de México','Michoacán','Jalisco','Baja California','Oaxaca','Chihuahua','Guerrero','Sinaloa','Estado de México','Morelos','Guanajuato','Quintana Roo','Sonora','Nuevo León','Durango','Tlaxcala','Querétaro','Veracruz','Zacatecas','Chiapas','Nayarit','San Luis Potosí','Tamaulipas','Tabasco','Aguascalientes','Hidalgo','Baja California Sur','Coahuila','Campeche','Yucatán','Colima','Puebla']
amounts='2044.0 1324.5 922.2 769.4 729.3 676.8 671.9 606.8 564.1 542.2 499.6 490.8 483.5 454.3 428.9 419.4 376.1 364.7 341.4 322.4 311.7 309.9 308.6 307.6 290.2 265.2 252.6 239.7 206.5 173.8 120.7 115.1'.split()
congress=[{'entidad':n,'ejercicio':2024,'presupuesto_ejercido_mdp':float(a),'estado':'oficial','fuente':sources['Congresos'],'pagina':11,'nota':'Redondeo de la gráfica oficial a 0.1 mdp; no es importe de auditoría ASF.'} for n,a in zip(names,amounts)]
federal=[
 ['Diputados','Aprobado',8982854.4,4],['Diputados','Modificado',9371736.5,4],['Diputados','Pagado',9371736.5,4],
 ['Diputados','Universo de egresos seleccionado',6833879.4,1],['Diputados','Muestra de egresos',6537228.2,1],
 ['Senado','Aprobado',4955182.0,4],['Senado','Modificado',5045707.6,4],['Senado','Devengado',5045707.6,5],['Senado','Pagado al 31 de diciembre',4978781.8,5],['Senado','Pendiente de pago al cierre; pagado en 2025',66925.8,1],['Senado','Universo de egresos seleccionado',5045707.6,1],['Senado','Muestra de egresos',3560328.5,1],
]
personnel=[['1110','Dietas',623908.0],['1130','Sueldos base',563826.5],['1210','Honorarios asimilables',913432.5],['1230','Servicio social',1200.0],['1310','Primas por antigüedad',7954.3],['1320','Primas vacacionales y gratificación anual',391828.2],['1330','Horas extraordinarias',963.4],['1340','Compensaciones',1005303.5],['1410','Seguridad social',144181.8],['1420','Fondos de vivienda',55008.8],['1430','Sistema de retiro',32287.6],['1440','Seguros',95602.5],['1520','Indemnizaciones',547396.4],['1530','Prestaciones y haberes de retiro',93773.9],['1540','Prestaciones contractuales',957800.0],['1590','Otras prestaciones',350115.6],['1710','Estímulos',183452.5]]
senate=[['1000','Servicios personales',3274276.0,3259885.8],['2000','Materiales y suministros',83699.0,81146.6],['3000','Servicios generales',1653842.6,1610384.5],['4000','Transferencias y ayudas',8751.2,8751.2],['5000','Bienes e intangibles',19761.0,13235.9],['6000','Inversión pública',5377.8,5377.8]]
cuernavaca=[
 ['Presidencia municipal',59205498.44,54918140.92,54917309.09,52006132.88],
 ['Sindicatura municipal',17704182.66,18818314.59,18818314.59,18687999.86],
 ['Regidores del Ayuntamiento',34178605.01,33365095.09,33365095.09,33280807.75],
 ['Secretaría del Ayuntamiento',44133008.45,42959963.27,42959963.27,42743538.58],
 ['Total del estado analítico municipal',1849671058.00,2252873274.92,2184515516.67,2113574138.66],
]
local=[
 ['Congreso de Nuevo León',1402,'Universo seleccionado',233044.5,'miles de pesos',1],
 ['Congreso de Nuevo León',1402,'Muestra auditada',233044.5,'miles de pesos',1],
 ['Congreso de Nuevo León',1402,'Monto por aclarar',4507703.95,'pesos',26],
 ['Congreso de Tlaxcala',1940,'Universo seleccionado',151900.8,'miles de pesos',1],
 ['Congreso de Tlaxcala',1940,'Muestra auditada',151900.8,'miles de pesos',1],
 ['Congreso de Tlaxcala',1940,'Recuperaciones; incluye cargas financieras',4995755.97,'pesos',29],
 ['Congreso de Tlaxcala',1940,'Cargas financieras incluidas en recuperación',97956.00,'pesos',29],
]
# Reconcile the extracted matrix against independently published, rounded ASF totals.
assert len(m['participaciones_estatales'])==32
assert len(m['auditorias_integrales_municipales'])==1056
for key,expected in [('participaciones_estatales',D('15675.7')),('auditorias_integrales_municipales',D('35074.7'))]:
    records=m[key]
    assert len({x['auditoria_numero'] for x in records})==len(records)
    total=sum(D(x['por_aclarar_miles']) for x in records)/1000
    assert abs(total-expected)<=D('0.05'),(key,total,expected)
assert sum(D(str(x[2])) for x in personnel)==D('5968035.5')
assert sum(D(str(x[2])) for x in senate)==D('5045707.6')
assert sum(D(str(x[3])) for x in senate)==D('4978781.8')
bundle={'fecha_consulta':'2026-09-25','fuentes':sources,'congresos':congress,'federal':federal,'personal_diputados':personnel,'capitulos_senado':senate,'cuernavaca':cuernavaca,'auditorias_congresos':local,**m}
(r/'desglose-numerico2024.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf-8')
def fmt(v,dec=3):return f'{D(str(v)):,.{dec}f}'
lines=['# Desglose numérico para la calculadora cívica',
 'Consulta: 24 de septiembre de 2026. Ejercicio analizado: **2024**. Montos nominales en pesos mexicanos.',
 'La entrega contiene presupuestos de los 32 congresos locales, cifras federales, 32 auditorías estatales de participaciones y 1,056 auditorías integrales municipales. Estas auditorías no equivalen al presupuesto completo de cada gobierno ni cubren todos los municipios del país. El seguimiento posterior a los informes no está incorporado.',
 'Los datos originales llevan estado `oficial`. Las conversiones, sumas y porcentajes llevan `derivado`. Los faltantes conservan `pendiente`. En el Excel se conserva la unidad original y el enlace por fila.',
 '## 1. Diputados y Senado',
 'Millones de pesos (mdp). Conversión derivada: importe del informe en miles de pesos / 1,000.',
 '| Institución | Concepto | Mdp |','|---|---|---:|']
lines += [f'| {n} | {c} | {fmt(D(str(v))/1000,4)} |' for n,c,v,p in federal]
lines += [f"Fuentes: [ASF, Diputados, pp. 1 y 4–5]({sources['Diputados']}); [ASF, Senado, pp. 1 y 4–5]({sources['Senado']}).",
 'Diputados: 26 resultados sin irregularidades detectadas (p. 43). Senado: 25 resultados sin irregularidades y dos solventados antes del informe (p. 31). Se refieren a esas revisiones y muestras.',
 '### Personal de Diputados',
 '| Partida | Concepto | Mdp |','|---|---|---:|']
lines += [f'| {k} | {n} | {fmt(D(str(v))/1000,4)} |' for k,n,v in personnel]
lines += [f"Total: **5,968.0355 mdp**. [ASF, Diputados, p. 5]({sources['Diputados']}). Son gastos de personal institucional, no remuneraciones exclusivas de diputados.",
 '### Senado por capítulo',
 '| Capítulo | Concepto | Devengado, mdp | Pagado, mdp |','|---|---|---:|---:|']
lines += [f'| {k} | {n} | {fmt(D(str(d))/1000,4)} | {fmt(D(str(p))/1000,4)} |' for k,n,d,p in senate]
lines += [f"[ASF, Senado, p. 5]({sources['Senado']}). La diferencia devengado/pagado corresponde a obligaciones al cierre; no se clasifica automáticamente como pérdida.",
 '## 2. Presupuesto ejercido de los 32 congresos locales',
 'Estado `oficial`: millones de pesos, con el redondeo de la gráfica publicada. Fuente INEGI, no un dictamen de ASF.',
 '| Entidad | Mdp |','|---|---:|']
lines += [f"| {x['entidad']} | {fmt(x['presupuesto_ejercido_mdp'],1)} |" for x in congress]
lines += [f"Total nacional publicado: **$15,934,015,120**. La suma de las barras redondeadas es 15,933.9 mdp; la diferencia de 0.115120 mdp es compatible con su precisión. [INEGI, CNPLE 2025, pp. 10–11]({sources['Congresos']}).",
 '### Auditorías específicas de congresos locales',
 '| Congreso | Concepto | Importe original | Unidad |','|---|---|---:|---|']
lines += [f'| {n} | {c} | {fmt(v,2)} | {u} |' for n,a,c,v,u,p in local]
lines += [f"Fuentes: [Nuevo León, auditoría 1402, pp. 1 y 26–27]({sources['Nuevo León']}); [Tlaxcala, auditoría 1940, pp. 1 y 29]({sources['Tlaxcala']}).",
 'No se suman cargas financieras a la recuperación que ya las incluye. Nuevo León registra diez acciones: cuatro recomendaciones, una promoción de responsabilidad y cinco pliegos. Tlaxcala registra dos recomendaciones. Los saldos son los del informe; su seguimiento actual está pendiente.',
 '## 3. Las 32 entidades: auditorías de participaciones federales',
 'No son presupuestos estatales completos. Se conserva un mismo objeto de revisión para evitar mezclar programas. Mdp derivados de la matriz (miles / 1,000).',
 '| Entidad | Muestra revisada | Por aclarar | Auditoría |','|---|---:|---:|---:|']
state=sorted(m['participaciones_estatales'],key=lambda x:x['institucion'])
lines += [f"| {x['institucion'].replace('Gobierno del Estado de ','').replace('Gobierno de la ','')} | {fmt(D(x['muestra_miles'])/1000,4)} | {fmt(D(x['por_aclarar_miles'])/1000,4)} | {x['auditoria_numero']} |" for x in state]
lines += [f"[ASF, matriz consolidada CP 2024]({sources['Matriz']}). Las páginas exactas se conservan en Excel y JSON.",
 '**Totales derivados:** universo 961,298.3166 mdp; muestra 795,695.0566 mdp; por aclarar 15,675.7109 mdp; recuperaciones 1.1808 mdp. Los ceros son los publicados para estas auditorías, no una evaluación general del estado.',
 '## 4. Municipios: 1,056 auditorías integrales',
 'El Excel incluye cada institución, auditoría, universo, muestra, recuperación, monto por aclarar, acciones, fuente y páginas. Se eliminaron las apariciones repetidas de la misma auditoría en las secciones de la matriz.',
 '**Totales derivados:** universo y muestra 58,363.5142 mdp; por aclarar 35,074.6539 mdp; recuperaciones 0.3033 mdp. Son operaciones de origen federal seleccionadas, no el gasto total de todos los municipios.',
 'Estas son diez filas con mayores importes por aclarar dentro de ese conjunto; no constituyen una clasificación de corrupción ni de eficiencia municipal.',
 '| Institución | Muestra, mdp | Por aclarar, mdp | Auditoría |','|---|---:|---:|---:|']
top=sorted(m['auditorias_integrales_municipales'],key=lambda x:D(x['por_aclarar_miles']),reverse=True)[:10]
lines += [f"| {x['institucion']} | {fmt(D(x['muestra_miles'])/1000,4)} | {fmt(D(x['por_aclarar_miles'])/1000,4)} | {x['auditoria_numero']} |" for x in top]
lines += [f"[ASF, matriz consolidada CP 2024]({sources['Matriz']}). Esta selección incluye sólo auditorías integrales municipales; otros fondos revisados separadamente quedan fuera.",
 '### Contexto nacional de observaciones',
 'La ASF reporta 59,363.7 mdp por aclarar en gasto federalizado: 35,350.3 en gobiernos municipales, 21,585.6 en gobiernos estatales y organismos descentralizados, 2,008.6 en universidades, 180.1 en poderes judiciales locales, 130.3 en fiscalías, 85.4 en institutos tecnológicos, 22.4 en congresos y 1.1 en gobierno federal. Las sumas publicadas tienen redondeo.',
 f"Los 35,350.3 mdp municipales tienen cobertura más amplia que las auditorías integrales anteriores: **no deben sumarse entre sí**. [ASF, marco general, p. 36]({sources['General']}).",
 '## 5. Ayuntamiento y áreas del cabildo: Cuernavaca',
 'Importes originales en **pesos**, estado `oficial`, enero–diciembre de 2024. Fuente municipal complementaria; no se presentan como hallazgos ASF.',
 '| Área | Aprobado | Modificado | Devengado | Pagado |','|---|---:|---:|---:|---:|']
lines += [f'| {n} | {fmt(a,2)} | {fmt(mo,2)} | {fmt(d,2)} | {fmt(p,2)} |' for n,a,mo,d,p in cuernavaca]
lines += [f"[Cuenta pública municipal, clasificación administrativa, p. 1]({sources['Cuernavaca']}).",
 'Las cuatro áreas están incluidas en el total municipal. El gasto de regidores no es el sueldo de cada regidor. Presidencia y secretaría también realizan funciones administrativas: su suma no debe publicarse como costo exacto del cabildo sin una delimitación adicional.',
 '## 6. Cuentas utilizables en la calculadora',
 'Operaciones derivadas: presupuesto en pesos / ingreso anual del usuario; muestra / universo; importe por aclarar / muestra de la misma auditoría; y gasto de un rubro / gasto total comparable. El ingreso debe ser positivo y debe conservarse su naturaleza bruta o neta.',
 'Para personal de Diputados: 5,968,035.5 / 9,371,736.5 × 100. Para personal del Senado sobre pagado: 3,259,885.8 / 4,978,781.8 × 100. Son participaciones en gasto institucional, no sueldos individuales.',
 'Los cálculos no extrapolan irregularidades fuera de la muestra. Las equivalencias no afirman que puedan contratarse trabajadores con ese importe ni que el contribuyente haya pagado personalmente una operación observada.',
 '## 7. Verificación y pendientes',
 'Se comprobaron las tablas y notas relevantes visualmente. La extracción identifica 32 auditorías estatales y 1,056 integrales municipales únicas; las apariciones duplicadas deben coincidir campo por campo. Se conciliaron los totales con las cifras redondeadas del marco general. Los capítulos del Senado y las partidas de personal de Diputados cuadran con sus totales.',
 'Pendientes: presupuestos completos de los gobiernos estatales, padrón financiero de todos los ayuntamientos, costo específico de cada cabildo, remuneraciones individuales y seguimiento actualizado por acción. Se requieren sus cuentas públicas y expedientes específicos; no se estiman con el monto auditado ni con promedios.',
 'No se modificó la plataforma. La carpeta de trabajo no tiene repositorio Git reconocido; la entrega queda guardada localmente. CONTEXT.md registra el avance y los pendientes.',
]
lines += ['### Cobertura de la búsqueda EFIPEM', 'INEGI documenta la información definitiva 2024 en https://www.inegi.org.mx/rnm/index.php/catalog/1120/related-materials. Los paquetes históricos efipem_estatal_csv.zip y efipem_municipal_csv.zip descargados durante esta revisión contienen años hasta 2023; no se incorporaron como cifras 2024. La extracción de ingresos y egresos completos 2024 queda pendiente, aunque sí existe la publicación oficial. No debe confundirse esta limitación de la extracción con ausencia de datos públicos.']
lines = [x.replace('24 de septiembre de 2026','25 de septiembre de 2026') for x in lines]
text = ''.join(('\n' if i and x.startswith('|') and lines[i-1].startswith('|') else '\n\n' if i else '') + x for i,x in enumerate(lines))
(r/'desglose-numerico-finanzas2024.md').write_text(text,encoding='utf-8')
print('Registros matriz:',sum(len(m[k]) for k in m),'Congresos:',len(congress))
print('Personal Diputados %',D('5968035.5')/D('9371736.5')*100)
print('Personal Senado pagado %',D('3259885.8')/D('4978781.8')*100)
print('Municipios mayores importes:',json.dumps(top[:3],ensure_ascii=False))
