from pathlib import Path
from decimal import Decimal
import re, json, hashlib

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'fuentes-judicial'
D=lambda s: Decimal(s.replace(',','').strip().rstrip('-'))*(-1 if s.strip().endswith('-') else 1)
money=r'-?\d[\d,]*\.\d{2}-?'
sources={
 'PEF':('pef2026.pdf','https://www.diputados.gob.mx/LeyesBiblio/ref/pef_2026/PEF_2026_orig_21nov25.pdf','Decreto PEF 2026, DOF 21-11-2025'),
 'UR':('r03_aae.pdf','https://www.pef.hacienda.gob.mx/work/models/P3f26115/PEF2026/y6k1r4r1/docs/03/r03_aae.pdf','PEF 2026, análisis administrativo económico, enero 2026'),
 'COG':('r03_apurog.pdf','https://www.comunicacionpef.hacienda.gob.mx/work/models/COMUNICACION_DEL_PEF/Documentos/2026/distribucion_gasto_UR/r03_apurog.pdf','PEF 2026, distribución por UR, capítulo y concepto, enero 2026'),
 'SCJN_AGO':('scjn-agosto2026.pdf','https://www.scjn.gob.mx/sites/default/files/presupuesto-asignado/documento/2026-09/EEP-2026-08.pdf','SCJN, estado del ejercicio al 31-08-2026'),
 'SCJN_JUN':('scjn-trim2-2026.pdf','https://www.scjn.gob.mx/sites/default/files/presupuesto%20asignado/documento/2026-07/Estado-Analitico-Ejercicio-Presupuesto-2026-Trim-02.pdf','SCJN, estado analítico enero-junio 2026'),
 'SCJN_2025':('scjn-cierre2025.pdf','https://www.scjn.gob.mx/sites/default/files/presupuesto%20asignado/documento/2026-01/Estado-Analitico-Ejercicio-Presupuesto-2025-Trim-04.pdf','SCJN, estado analítico enero-diciembre 2025'),
 'OAJ_MAR':('oaj-marzo2026.pdf','https://www.oaj.gob.mx/acceso_informacion/InfoFinanciera/Estados_Financieros_Patrimonio_31Marzo2026_editable.pdf','OAJ, estados financieros enero-marzo 2026; discrepancias entre clasificaciones'),
 'MANUAL':('manual-remuneraciones2026.pdf','https://apps.cjf.gob.mx/normativa/Recursos/2026-0-6-OAJ_V01.PDF','Manual de remuneraciones PJF 2026, DOF 27-02-2026'),
}
for id,nn in [('OAJ_CAP','001'),('OAJ_UEG','007'),('OAJ_PAR','009'),('OAJ_UEG_PAR','010')]:
 sources[id]=(f'oaj-junio-sheet{nn}.html',f'https://www.cjf.gob.mx/transparencia/resources/Presupuestoejercido/cierremensual/2026/Cierre_Transparencia_2Trim_2026_archivos/sheet{nn}.htm','OAJ, segundo trimestre: exclusivamente 01-04 a 30-06-2026')
out={'consulta':'2026-09-25','moneda':'MXN','unidad':'pesos nominales','fuentes':{k:{'archivo':v[0],'url':v[1],'titulo':v[2],'sha256':hashlib.sha256((SRC/v[0]).read_bytes()).hexdigest()} for k,v in sources.items()}}

# PEF: preserve hierarchy. Parent and child amounts must never be added together.
ur='RAMO03';page=0; rows=[]; units=[]
for line in (SRC/'r03_apurog.txt').read_text(encoding='utf-8').splitlines():
 if line.startswith('PAGINA '):page=int(line.split()[1])
 m=re.match(r'^(100|120|210|211|300) (.+) ([\d,]+)$',line)
 if m:
  ur=m[1]; units.append({'ur':ur,'nombre':m[2],'aprobado':int(m[3].replace(',','')),'pagina':page,'fuente':'COG','estado':'oficial'})
 m=re.match(r'^(\d{4}) (.+?) ([\d,]+)$',line)
 if m:
  code,name,val=m.groups(); rows.append({'ur':ur,'codigo':code,'nivel':'capitulo' if code.endswith('000') else 'concepto','concepto':name,'aprobado':int(val.replace(',','')),'pagina':page,'fuente':'COG','estado':'oficial'})
out['unidades_pef']=units; out['pef_objeto_gasto']=rows
assert sum(x['aprobado'] for x in units)==70005628646
for unit in units:
 assert sum(x['aprobado'] for x in rows if x['ur']==unit['ur'] and x['nivel']=='capitulo')==unit['aprobado'],unit
for x in rows:
 if x['nivel']=='capitulo':
  children=[y for y in rows if y['ur']==x['ur'] and y['nivel']=='concepto' and y['codigo'][0]==x['codigo'][0]]
  assert sum(y['aprobado'] for y in children)==x['aprobado'],x

# SCJN August: original, additions, reductions, net, modified, commitment, exercised, available.
keys=['original','ampliaciones','reducciones','neto','modificado','compromiso','ejercido','disponible']
sc=[];total=None;page=0
for line in (SRC/'scjn-agosto2026.txt').read_text(encoding='utf-8').splitlines():
 if line.startswith('PAGINA '):page=int(line.split()[1])
 vals=re.findall(money,line)
 m=re.match(r'^(\d{4,5})([^\d].*?)\s'+money,line)
 if len(vals)==8 and m:
  code,name=m.groups();sc.append({'codigo':code,'concepto':name.strip(),'nivel':'partida' if len(code)==5 else ('capitulo' if code.endswith('000') else 'concepto'),**dict(zip(keys,map(D,vals))),'pagina':page,'fuente':'SCJN_AGO','estado':'oficial'})
 elif len(vals)==8 and re.match(money,line):total=dict(zip(keys,map(D,vals)))
assert total is not None
for key in keys:
 assert sum(x[key] for x in sc if x['nivel']=='partida')==total[key],key
 assert sum(x[key] for x in sc if x['nivel']=='capitulo')==total[key],key
for x in sc:
 assert x['original']+x['ampliaciones']-x['reducciones']==x['modificado'],x
 assert x['compromiso']+x['ejercido']+x['disponible']==x['modificado'],x
out['scjn_agosto']=sc;out['scjn_agosto_total']=total

# SCJN states for whole-year 2025 and first half 2026.
caps=['Servicios personales','Materiales y Suministros','Servicios Generales','Transferencias, Asignaciones, Subsidios y Otras Ayudas','Bienes Muebles, Inmuebles e Intangibles','Inversión Pública']
states=[]
for file,year,cut,source in [('scjn-cierre2025.txt',2025,'2025-12-31','SCJN_2025'),('scjn-trim2-2026.txt',2026,'2026-06-30','SCJN_JUN')]:
 page1=(SRC/file).read_text(encoding='utf-8').split('PAGINA 2')[0]
 for line in page1.splitlines():
  name=next((c for c in caps if line.startswith(c+' ')),None)
  if 'Total del Egreso' in line:name='Total'
  if not name:continue
  vals=re.findall(r'-?\d[\d,]*',line[line.index(name)+len(name):])
  numbers=list(map(lambda s:int(s.replace(',','')),vals))
  states.append({'ejercicio':year,'corte':cut,'concepto':name,**dict(zip(['aprobado','adecuaciones','modificado','devengado','pagado','subejercicio'],numbers)),'fuente':source,'pagina':1,'estado':'oficial'})
out['scjn_cortes']=states

# OAJ second quarter, not cumulative first half.
def table(file):
 for line in (SRC/file).read_text(encoding='utf-8').splitlines():
  yield [re.sub(r'\s+',' ',v).strip() for v in line.split('|') if v.strip()]
ueg=[]
for cells in table('oaj-junio-sheet007.txt'):
 if len(cells)==3 and re.fullmatch(r'\d{4}',cells[0]):
  ueg.append({'ueg':cells[0],'nombre':cells[1],'pagado':D(cells[2]),'periodo_desde':'2026-04-01','periodo_hasta':'2026-06-30','estado':'oficial','fuente':'OAJ_UEG'})
assert len({x['ueg'] for x in ueg})==len(ueg)
assert sum(x['pagado'] for x in ueg)==D('13,977,400,359.62')
out['oaj_ueg']=ueg
oajcap=[]
for cells in table('oaj-junio-sheet001.txt'):
 if len(cells)==5 and re.fullmatch(r'\d{4}',cells[0]):
  oajcap.append({'capitulo':cells[0],'concepto':cells[1],'asignado_anual':D(cells[2]),'asignado_trimestre':D(cells[3]),'pagado_trimestre':D(cells[4]),'estado':'oficial','fuente':'OAJ_CAP'})
out['oaj_capitulos_trimestre']=oajcap
assert sum(x['pagado_trimestre'] for x in oajcap)==sum(x['pagado'] for x in ueg)
details=[];uid=None
for cells in table('oaj-junio-sheet010.txt'):
 if len(cells)!=2:continue
 m=re.match(r'^(\d{4}) - (.+)',cells[0])
 if m:uid=m[1];continue
 m=re.match(r'^(\d{5}) (.+)',cells[0])
 if m and uid:details.append({'ueg':uid,'partida':m[1],'concepto':m[2],'pagado':D(cells[1]),'estado':'oficial','fuente':'OAJ_UEG_PAR'})
for u in ueg:
 assert sum(x['pagado'] for x in details if x['ueg']==u['ueg'])==u['pagado'],u
out['oaj_ueg_partida']=details
names={x['partida']:x['concepto'] for x in details}
names.update({'11301':'Sueldo base','12101':'Honorarios asimilables a salarios','12201':'Sueldos base al personal eventual','13101':'Prima quinquenal por años de servicios efectivos','13201':'Primas de vacaciones y dominical','13202':'Aguinaldo o gratificación de fin de año','14403':'Cuotas para el seguro de gastos médicos del personal','14404':'Cuotas para el seguro de separación individualizado','15301':'Prestaciones de retiro','15401':'Prestaciones establecidas por condiciones generales de trabajo','15402':'Compensación garantizada','15403':'Asignaciones adicionales al sueldo','15405':'Compensación de apoyo'})
for x in sc:
 x['concepto_fuente']=x['concepto']
 if x['codigo'] in names:x['concepto']=names[x['codigo']]
 elif x['nivel']=='capitulo':
  match=next((r for r in rows if r['ur']=='100' and r['codigo']==x['codigo']),None)
  if match:x['concepto']=match['concepto']

out['remuneraciones_referencia']=[
 {'cargo':'Ministro SCJN','concepto':'Sueldo y salario mensual neto, tabulador máximo','importe':134310,'periodicidad':'mensual','naturaleza':'neto','fuente':'MANUAL','pagina':8,'estado':'oficial','nota':'Tabulador publicado 27-02-2026; no es comprobante individual de nómina.'},
 {'cargo':'Ministro SCJN','concepto':'Aguinaldo y prima vacacional netos anuales','importe':290273,'periodicidad':'anual','naturaleza':'neto','fuente':'MANUAL','pagina':9,'estado':'oficial','nota':'Importe conjunto, no aguinaldo aislado ni costo laboral total.'},
 {'cargo':'Secretario de estudio y cuenta coordinador de ponencia SCJN (grupo 5)','concepto':'Sueldo mensual neto máximo del grupo','importe':124686,'periodicidad':'mensual','naturaleza':'neto','fuente':'MANUAL','pagina':8,'estado':'oficial','nota':'El grupo incluye otros puestos. No informa número de plazas.'},
 {'cargo':'Secretario de estudio y cuenta de ponencia SCJN (grupo 7)','concepto':'Sueldo mensual neto mínimo publicado','importe':119317,'periodicidad':'mensual','naturaleza':'neto','fuente':'MANUAL','pagina':8,'estado':'oficial','nota':'Conservar el intervalo tabular; no sustituir por promedio.'},
 {'cargo':'Secretario de estudio y cuenta de ponencia SCJN (grupo 7)','concepto':'Sueldo mensual neto máximo publicado','importe':123105,'periodicidad':'mensual','naturaleza':'neto','fuente':'MANUAL','pagina':8,'estado':'oficial','nota':'Conservar el intervalo tabular; no informa plaza ocupada.'}
]

# Link administrative office codes to judicial circuit only where explicitly named.
mapping={str(1200+i):i for i in range(1,30)}
mapping.update({'1231':30,'1232':21,'1233':17,'1234':3,'1235':15,'1236':12,'1237':7,'1238':31,'1239':32,'1240':8,'1241':10})
circs=[]
for i in range(1,33):
 subset=[u for u in ueg if mapping.get(u['ueg'])==i]
 assert subset
 ids=[x['ueg'] for x in subset]
 # The per-office detail has no chapter 1000. This is not the total cost of the circuit.
 assert not [d for d in details if d['ueg'] in ids and d['partida'].startswith('1')]
 circs.append({'circuito':i,'ueg_incluidas':ids,'sedes':[x['nombre'] for x in subset],'pagado_registrado_ueg':sum(x['pagado'] for x in subset),'presupuesto_total_circuito':None,'estado_total':'pendiente','estado_pago_agregado':'derivado','periodo_desde':'2026-04-01','periodo_hasta':'2026-06-30','formula':'Suma del pagado de UEG explícitamente denominadas Circuito Judicial; excluye nómina centralizada, centros penales y servicios centrales','fuentes':['OAJ_UEG','OAJ_UEG_PAR']})
out['circuitos']=circs
out['pendientes']=[
 {'concepto':'Costo total por circuito, tribunal y juzgado','importe':None,'estado':'pendiente','motivo':'Se requiere asignar nómina centralizada y gasto compartido mediante adscripción verificable, sin prorrateos arbitrarios.'},
 {'concepto':'Presupuesto y nómina de cada ponencia SCJN','importe':None,'estado':'pendiente','motivo':'Las fuentes presupuestarias verificadas agregan la Corte como UR 100; falta matriz por unidad interna y adscripción.'},
 {'concepto':'Conciliación de clasificación OAJ capítulos 3000 y 4000','importe':None,'estado':'pendiente','motivo':'Comunicación SHCP y cuadro OAJ difieren en 10,637,899 pesos, con total anual idéntico; falta documento de reclasificación.'},
 {'concepto':'Conciliación OAJ primer trimestre','importe':None,'estado':'pendiente','motivo':'Estados analíticos por objeto, económico y administrativo publican pagados distintos; no se combinan con el segundo trimestre.'},
 {'concepto':'Integración de datos a la aplicación','importe':None,'estado':'pendiente','motivo':'Esta entrega es investigación y especificación; no modifica assets ni la calculadora.'}
]
def encode(o):
 if isinstance(o,Decimal):return float(o)
 raise TypeError(type(o))
(ROOT/'presupuesto-judicial-federal2026.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=encode),encoding='utf-8')
summary={'unidades_pef':len(units),'pef_filas':len(rows),'scjn_partidas':sum(x['nivel']=='partida' for x in sc),'oaj_ueg':len(ueg),'oaj_ueg_partida':len(details),'circuitos':len(circs),'pagos_ueg_circuitos':sum(x['pagado_registrado_ueg'] for x in circs),'scjn_total_agosto':total,'validaciones':'sumas PEF, conceptos, partidas SCJN, UEG OAJ y detalle UEG/partida conciliados exactamente'}
(ROOT/'verificacion-judicial2026.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=encode),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,default=encode))
