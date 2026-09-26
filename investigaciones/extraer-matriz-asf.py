from pathlib import Path
import re, json, sys
from decimal import Decimal
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parent
pages=(root/'fuentes-asf/matriz2024.txt').read_text(encoding='utf-8').split('PAGINA ')
num=r'([\d,]+\.\d+)'
tail=r'De Cumplimiento\s+([123])\s+1\s+'+num+r'\s+'+num+r'\s+([\d.]+)%\s+((?:\d+\s+){10})'+num+r'\s+'+num
patterns={
 'participaciones_estatales':r'(Gobierno (?:del Estado de|de la Ciudad de) [^\d]+?)\s+(\d+)\s+Participaciones Federales a Entidades Federativas\s+'+tail,
 'auditorias_integrales_municipales':r'((?:Municipio de|Municipio Del|Alcald[ií]a) (?:[^\d]|13,)+?)\s+(\d+)\s+Auditor[ií]a Integral a Recursos del Gasto Federalizado, Incluidas las Participaciones Federales, en (?:Municipios|Alcald[ií]as)\s+'+tail,
}
data={}
for kind,pattern in patterns.items():
    records={}
    for page in pages[1:]:
        page_number=int(page.split()[0])
        text=re.sub(r'\s+',' ',page)
        for m in re.finditer(pattern,text):
            name,number,delivery,universe,sample,coverage,counts,recovered,unresolved=m.groups()
            # Restrict to the actual institution cell when repeated headers precede it.
            if len(name)>180:
                raise ValueError(('Nombre ambiguo',page_number,name))
            counts=list(map(int,counts.split()))
            row={'institucion':name,'auditoria_numero':int(number),'ejercicio':2024,
                'entrega':int(delivery),'universo_miles':universe.replace(',',''),
                'muestra_miles':sample.replace(',',''),'cobertura_porcentaje':coverage,
                'resultados_con_observacion_solventada_atendida':counts[0],'resultados_con_observaciones':counts[1],
                'acciones_total':counts[8],'recuperaciones_miles':recovered.replace(',',''),
                'por_aclarar_miles':unresolved.replace(',',''),'estado':'oficial',
                'fuente':'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Matriz/MDB_Consolidado.pdf',
                'paginas':[page_number],'corte':'Informe consolidado CP 2024; seguimiento posterior no incorporado'}
            if number in records:
                previous=records[number]
                assert all(previous[k]==row[k] for k in row if k!='paginas'), (number,previous,row)
                previous['paginas'].append(page_number)
            else: records[number]=row
    data[kind]=list(records.values())
    print(kind,len(records))
    for field in ['universo_miles','muestra_miles','recuperaciones_miles','por_aclarar_miles']:
        print(field,str(sum(Decimal(r[field]) for r in records.values())))
(root/'datos-matriz-asf2024.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(data['participaciones_estatales'][:2],ensure_ascii=False,indent=2))
