# -*- coding: utf-8 -*-
"""Las cifras de la pestaña «Números», en el formato con que conversa el bot
(pedido del autor, 23-10-2026: «que se integre toda la información que obra
en la pestaña de números a nuestro auditor»).

Cada renglón es una cifra que ya aparece en una página de Números, con su
estado, su documento y la página donde se lee. No hay una sola cifra nueva:
todo sale de window.AUDIT_DB, de las mismas colecciones con que se escriben
esas páginas.

- panoramaErario: los 16 orígenes del ingreso (LIF 2026), los ocho renglones
  del gasto, el gasto federalizado, los fondos municipales, el Anexo 1 del
  PEF 2026 (ramo por ramo) y el Anexo 3 (gastos obligatorios).
- poderes: las unidades del Legislativo y del Judicial (aprobado 2026 y
  ejercido 2025).
- paquete_2027: las finanzas públicas, la clasificación funcional, los
  programas sociales, la inversión, los amortiguadores, los pasivos
  contingentes y el marco macroeconómico.
- cuentaFederal2024: el estado de resultados del Gobierno Federal.
- finanzas_sexenales: las series anuales de 1990 a 2025 (Radar hacendario).

Lo que se deja fuera, a propósito:
- panoramaErario.treemapPEF y macro: sus montos no tienen documento (el
  12-10-2026 gasto_modulos.py los sustituyó por el Anexo 1).
- Las cifras con estado «pendiente»: ya están en el Registro de pendientes,
  que el bot lee por su lado.

Lo usa asistente._charla(); asistente-charla.js lo lee como B.dat.num.
"""
import html
import re

from apartados import ingreso_archivo, numeros_datos
from gasto_modulos import egreso_archivo
import insp_nota


def limpio(t):
    return html.unescape(re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', str(t or '')))).strip()


def plano(s):
    """La misma normalización que plano() de asistente-charla.js."""
    s = limpio(s).lower()
    for a, b in (('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ü', 'u')):
        s = s.replace(a, b)
    return re.sub(r'[^a-z0-9ñ]+', ' ', s).strip()


# Cómo se le dice a cada renglón en la calle. Solo lo que no sale de su nombre.
ALIAS = {
    'ing-isr': ['isr', 'impuesto sobre la renta', 'impuesto a la renta'],
    'ing-iva': ['iva', 'impuesto al valor agregado'],
    'ing-ieps': ['ieps', 'impuesto especial'],
    'ing-comext': ['comercio exterior', 'aranceles', 'arancel', 'impuestos a las importaciones', 'aduanas'],
    'ing-accesorios': ['accesorios', 'multas y recargos', 'recargos'],
    'ing-isan': ['isan', 'impuesto sobre automoviles nuevos', 'autos nuevos'],
    'ing-hidro': ['impuesto por la actividad de exploracion', 'exploracion y extraccion'],
    'ing-rezagos': ['rezagos', 'impuestos atrasados'],
    'ing-cuotas': ['cuotas de seguridad social', 'cuotas del imss', 'cuotas obrero patronales'],
    'ing-mejoras': ['contribuciones de mejoras'],
    'ing-derechos': ['derechos'],
    'ing-productos': ['productos'],
    'ing-aprovech': ['aprovechamientos'],
    'ing-ventas': ['venta de bienes y servicios', 'ventas de las empresas publicas'],
    'ing-transf': ['fondo mexicano del petroleo', 'transferencias del fondo mexicano', 'renta petrolera'],
    'ing-deuda': ['financiamiento', 'endeudamiento', 'dinero prestado', 'prestamos'],
    'egr-social': ['desarrollo social', 'gasto social'],
    'egr-economico': ['desarrollo economico'],
    'egr-gobierno': ['funcion gobierno', 'gasto en gobierno'],
    'egr-poderes': ['poderes y organos autonomos', 'organos autonomos'],
    'egr-fondos': ['fondos de estabilizacion'],
    'egr-costofin': ['costo financiero', 'intereses', 'intereses de la deuda', 'pago de intereses'],
    'egr-participaciones': ['participaciones', 'ramo 28'],
    'egr-adefas': ['adefas', 'adeudos de ejercicios fiscales anteriores', 'adeudos del ano anterior'],
    'fed-r33': ['aportaciones', 'ramo 33'],
    'fed-r25': ['ramo 25', 'previsiones educativas'],
    'fed-conv': ['convenios'],
    'mun-fortamun': ['fortamun', 'fortalecimiento de los municipios'],
    'mun-fismdf': ['fismdf', 'fais municipal', 'infraestructura social municipal'],
}

# Ramos del Anexo 1 que la gente nombra distinto.
ALIAS_RAMO = {
    '01': ['congreso', 'congreso de la union'], '03': ['poder judicial', 'judicatura'], '22': ['ine'], '35': ['cndh', 'derechos humanos'], '49': ['fgr', 'fiscalia'],
    '40': ['inegi'], '32': ['tfja'], '02': ['presidencia'], '04': ['segob'], '05': ['sre', 'cancilleria'], '06': ['shcp', 'hacienda'],
    '07': ['sedena', 'ejercito', 'defensa'], '08': ['sader', 'agricultura'], '09': ['sict', 'comunicaciones y transportes'], '10': ['economia'],
    '11': ['sep', 'educacion'], '12': ['ssa', 'salud'], '13': ['semar', 'marina'], '14': ['stps', 'secretaria del trabajo'], '15': ['sedatu'], '16': ['semarnat', 'medio ambiente'],
    '18': ['sener', 'energia'], '20': ['bienestar', 'secretaria de bienestar'], '21': ['sectur', 'turismo'], '27': ['anticorrupcion', 'buen gobierno'],
    '36': ['sspc', 'seguridad publica', 'seguridad ciudadana'], '38': ['secihti', 'ciencia'], '48': ['cultura'], '54': ['mujeres'], '55': ['transformacion digital'],
    '56': ['imss bienestar'], '19': ['aportaciones a seguridad social'], '23': ['provisiones salariales', 'ramo 23'],
    '24': ['deuda publica ramo 24', 'ramo 24'], '30': ['ramo 30'], '34': ['fobaproa', 'ipab', 'rescate bancario', 'apoyo a ahorradores'],
    'GYN': ['issste'], 'GYR': ['imss', 'seguro social'],
}
ALIAS_UNIDAD = {'diputados': ['camara de diputados', 'diputados'], 'senado': ['camara de senadores', 'senado', 'senadores'],
                'asf': ['auditoria superior de la federacion', 'presupuesto de la asf', 'cuesta la asf', 'le dan a la asf', 'gasta la asf'], 'scjn': ['suprema corte', 'scjn', 'la corte'], 'oaj': ['organo de administracion judicial', 'oaj'],
                'tepjf': ['tribunal electoral', 'tepjf'], 'tdj': ['tribunal de disciplina']}
# Las mismas unidades en la Cuenta Pública 2025 (por su UR).
UR_UNIDAD = {('01', '100'): 'diputados', ('01', '101'): 'asf', ('01', '200'): 'senado', ('03', '100'): 'scjn', ('03', '120'): 'oaj', ('03', '300'): 'tdj'}

NUM = 'numeros-'
# Los nombres de calle de algunos desgloses.
COMP_ALIAS = {'Combustibles automotrices': ['gasolina', 'gasolinas', 'diesel', 'ieps de gasolina', 'ieps a combustibles'],
              'Bebidas con contenido alcohólico y cerveza': ['cerveza', 'alcohol', 'bebidas alcoholicas'],
              'Bebidas saborizadas': ['refrescos', 'bebidas azucaradas', 'impuesto a los refrescos'],
              'Tabacos labrados y otros': ['tabaco', 'cigarros', 'impuesto al tabaco'],
              'Alimentos no básicos con alta densidad calórica': ['comida chatarra', 'alimentos chatarra', 'botanas'],
              'Juegos con apuestas y sorteos': ['apuestas', 'casinos'], 'Videojuegos con contenido violento': ['videojuegos'],
              'Bebidas energetizantes': ['bebidas energeticas', 'energeticas'], 'Combustibles fósiles': ['impuesto al carbono'],
              'Endeudamiento interno del Gobierno Federal': ['deuda interna', 'endeudamiento interno'],
              'Petróleos Mexicanos': ['ventas de pemex', 'lo que vende pemex', 'vende pemex', 'ingresos de pemex'],
              'Comisión Federal de Electricidad': ['ventas de la cfe', 'vende la cfe', 'ingresos de la cfe', 'lo que vende la cfe'],
              'Costo financiero de Pemex y CFE': ['intereses de pemex', 'deuda de pemex y cfe']}
# El estado de resultados de 2024: se nombra con el año para no confundirlo con 2026.
CF_ALIAS = {'aprobado': ['gasto aprobado en 2024', 'presupuesto aprobado 2024', 'aprobado en 2024'],
            'ejercido': ['gasto ejercido en 2024', 'ejercido en 2024', 'se ejercio en 2024', 'cuenta publica 2024'],
            'pagado': ['gasto pagado en 2024', 'pagado en 2024'],
            'ingresos_gestion': ['ingresos de la gestion', 'por la gestion'],
            'intereses_deuda': ['intereses de la deuda en 2024', 'intereses en 2024', 'intereses de 2024']}


def datos(d):
    refs = {r['id']: r for r in d['referencias_legales']}

    def fu(tx, rid=None, url=None):
        return {'tx': limpio(tx), 'url': url or (refs.get(rid) or {}).get('url')}

    def al(nom, extra=()):
        """Los nombres con que se busca un renglón: su nombre, sin su
        «Secretaría de», y los apodos."""
        k = plano(nom)
        out = [k, plano(nom.split(' (')[0]), re.sub(r'^(secretaria|instituto|comision|tribunal(es)?|agencia|consejeria|fiscalia|oficina) (de (la |los |las |el )?|del |federal de |nacional de |general de )?', '', k)]
        out += [plano(x) for x in extra]
        return sorted({x for x in out if len(x) >= 3}, key=len, reverse=True)

    filas, grupos = [], {}

    def fila(**o):
        filas.append({k: v for k, v in o.items() if v not in (None, '', [])})

    P = d['panoramaErario']
    tlif, tpef = P['totalLIF'], P['totalPEF']
    LIF = fu('Ley de Ingresos de la Federación 2026, art. 1o.', 'ref-lif2026')
    PEF = fu('Presupuesto de Egresos de la Federación 2026 (DOF)', 'ref-pef2026')
    CGPE = fu('SHCP, Criterios Generales de Política Económica 2027', 'ref-cgpe2027')

    # 1. Los 16 orígenes del ingreso.
    grupos['ing26'] = {'n': 'todo lo que entra en 2026', 'tot': tlif, 'ir': [NUM + 'los-16-origenes.html', 'Los 16 orígenes del ingreso'],
                       'fu': LIF, 'lista': 'Los 16 orígenes del ingreso de 2026, según la Ley de Ingresos'}
    for x in P['ingresos']:
        fila(id=x['id'], g='ing26', sg=x['grupo'], n=limpio(x['nombreLargo']) if x['nombre'] in ('ISR', 'IVA', 'IEPS', 'ISAN') else limpio(x['nombre']),
             c=limpio(x['nombre']), y='2026', v=x['montoMdp'], e=x['estado'], fu=fu('Ley de Ingresos de la Federación 2026, art. 1o., renglón %s' % x['claveLIF'], 'ref-lif2026'),
             d=limpio(x['quePaga']), ley=limpio(x['ley']), al=al(x['nombre'], ALIAS.get(x['id'], []) + [x['nombreLargo']]),
             ir=[ingreso_archivo(x), limpio(x['nombre']) + ' en Números'])
    for sg in ('Impuestos', 'Otras contribuciones', 'No tributarios'):
        xs = [x for x in P['ingresos'] if x['grupo'] == sg]
        fila(id='ing-sub-' + plano(sg).replace(' ', '-'), g='ing26', sub=1, sut=1, n={'Impuestos': 'Impuestos (los ocho renglones)', 'Otras contribuciones': 'Otras contribuciones',
                                                                              'No tributarios': 'Ingresos no tributarios'}[sg],
             y='2026', v=round(sum(x['montoMdp'] for x in xs), 1), e='derivado', fu=LIF, op='suma de sus %d renglones en la Ley de Ingresos' % len(xs),
             al={'Impuestos': ['impuestos', 'ingresos tributarios', 'recaudacion de impuestos', 'lo que se cobra de impuestos'],
                 'Otras contribuciones': ['otras contribuciones'], 'No tributarios': ['no tributarios', 'ingresos no tributarios']}[sg],
             ir=[NUM + 'los-16-origenes.html', 'Los 16 orígenes del ingreso'])
    fila(id='ing-total', g='ing26', tot=1, n='Ingreso total autorizado de 2026', y='2026', v=tlif, e='oficial', fu=LIF,
         d='Todo lo que la Federación espera recibir en el año. Incluye la deuda nueva: por eso cuadra exacto con el gasto.',
         al=['ley de ingresos', 'ingreso total', 'ingresos totales', 'ingresos del gobierno', 'ingresos de la federacion', 'lo que entra', 'cuanto dinero entra',
             'cuanto se recauda', 'cuanto recauda el gobierno', 'cuanto cobra el gobierno', 'ingresos 2026', 'va a recaudar', 'van a recaudar', 'recaudara', 'va a entrar'],
         ir=[NUM + 'los-16-origenes.html', 'Los 16 orígenes del ingreso'])

    # 2. Los ocho renglones del gasto.
    grupos['egr26'] = {'n': 'todo el gasto de 2026', 'tot': tpef, 'ir': [NUM + 'gasto-simulador-contable.html', 'Los ocho renglones del gasto'],
                       'fu': PEF, 'lista': 'Los ocho renglones del gasto de 2026'}
    FU_EGR = {'ref-cgpe2027': fu('SHCP, Criterios Generales de Política Económica 2027 (clasificación funcional del PEF 2026)', 'ref-cgpe2027'),
              'ref-pef2026': fu('Presupuesto de Egresos de la Federación 2026, Anexo 8', 'ref-pef2026')}
    for x in P['egresos']:
        f = FU_EGR.get(x['refKey']) or fu('Presupuesto de Egresos de la Federación 2026, ' + x['clave'].replace('PEF 2026, ', ''), 'ref-pef2026')
        fila(id=x['id'], g='egr26', sg=x['grupo'], n=limpio(x['nombre']), y='2026', v=x['montoMdp'], e=x['estado'], fu=f, d=limpio(x['queCubre']),
             ley=limpio(x['ley']), al=[z for z in al(x['nombre'], ALIAS.get(x['id'], [])) if z != 'gobierno'], par=x['id'], ir=[egreso_archivo(x), limpio(x['nombre']) + ' en Números'])
    for sg, ali in (('Programable', ['gasto programable', 'lo que se decide', 'se decide cada ano']),
                    ('No programable', ['gasto no programable', 'ya comprometido', 'gasto comprometido', 'esta comprometido', 'estan comprometidos', 'comprometido'])):
        xs = [x for x in P['egresos'] if x['grupo'] == sg]
        # El programable se obtiene como en «¿Cuánto margen tiene?»: el total
        # menos el no programable (la suma de sus cinco finalidades difiere
        # 8.8 millones por el redondeo de la fuente).
        nopr = round(sum(x['montoMdp'] for x in P['egresos'] if x['grupo'] == 'No programable'), 1)
        fila(id='egr-sub-' + plano(sg).replace(' ', '-'), g='egr26', sub=1, sut=1, n='Gasto ' + sg.lower(), y='2026', v=nopr if sg == 'No programable' else round(tpef - nopr, 1), e='derivado',
             fu=FU_EGR['ref-cgpe2027'], op='suma de sus %d renglones' % len(xs) if sg == 'No programable' else 'gasto neto total menos el gasto no programable', al=ali,
             d='Lo que la Cámara reparte cada año entre programas.' if sg == 'Programable' else 'Intereses, participaciones a estados y adeudos del año anterior: no se decide, se debe.',
             ir=[NUM + 'margen-del-presupuesto.html', '¿Cuánto margen tiene el presupuesto?'])
    fila(id='egr-total', g='egr26', tot=1, n='Gasto neto total aprobado de 2026', y='2026', v=tpef, e='oficial', fu=fu('Presupuesto de Egresos de la Federación 2026, art. 1o. y Anexo 1', 'ref-pef2026'),
         d='El presupuesto federal del año: todo lo que la Cámara de Diputados autorizó gastar.',
         al=['presupuesto de egresos', 'presupuesto 2026', 'presupuesto federal', 'presupuesto del gobierno', 'gasto total', 'gasto neto total',
             'cuanto gasta el gobierno', 'cuanto se gasta', 'presupuesto de este ano', 'presupuesto', 'gasto publico', 'va a gastar', 'van a gastar', 'gastara'],
         ir=[NUM + 'gasto-publico.html', 'Gasto público'])

    # 2 bis. Los tres presupuestos (del Estado, nacional y social), las mismas
    # cifras de su tarjeta en «Presupuesto» (numeros_datos(), 24-10-2026).
    sale = {x['id']: x for x in numeros_datos(d)['sale']}
    grupos['tres26'] = {'n': 'todo el gasto de 2026', 'tot': tpef, 'ir': [NUM + 'gasto-tres-presupuestos.html', 'Los tres presupuestos'],
                        'fu': CGPE, 'lista': 'Los tres presupuestos de 2026'}
    for k, ali in (('estado', ['presupuesto del estado']), ('nacional', ['presupuesto nacional']), ('social', ['presupuesto social'])):
        x = sale[k]
        fila(id='tres-' + k, g='tres26', n=x['nom'], y='2026', v=x['v'], e=x['est'], fu=CGPE, op=x['op'] if x['est'] == 'derivado' else None,
             d=x['que'], al=ali, fr='Para 2026, el ' + x['nom'][0].lower() + x['nom'][1:] + ' suma {V}.',
             ir=[NUM + 'gasto-tres-presupuestos.html', 'Los tres presupuestos'])

    # 3. Los gastos obligatorios (Anexo 3).
    go = P['gastosObligatoriosPEF2026']
    FU_GO = fu('Presupuesto de Egresos de la Federación 2026, Anexo 3, pp. %s' % go['paginas'], url=go['url'])
    fila(id='egr-oblig', g='egr26', sub=1, sut=1, n='Gastos obligatorios (sin pensiones)', y='2026', v=go['obligatoriosMdp'], e='oficial', fu=FU_GO,
         d='Lo que la ley obliga a pagar antes de decidir nada: el decreto los agrupa en su Anexo 3.', al=['gastos obligatorios', 'gasto obligatorio'],
         ir=[NUM + 'margen-del-presupuesto.html', '¿Cuánto margen tiene el presupuesto?'])
    fila(id='egr-oblig-pen', g='egr26', sub=1, sut=1, n='Gastos obligatorios con pensiones', y='2026', v=go['conPensionesMdp'], e='oficial', fu=FU_GO,
         d='Los mismos gastos obligatorios más las pensiones.', al=['obligatorios con pensiones', 'gasto obligatorio con pensiones'],
         ir=[NUM + 'margen-del-presupuesto.html', '¿Cuánto margen tiene el presupuesto?'])

    # 4. El gasto federalizado y lo municipal.
    F = P['federalizado']
    grupos['fed26'] = {'n': 'el gasto federalizado de 2026', 'tot': F['totalMdp'], 'ir': [NUM + 'las-32-entidades.html', 'Las 32 entidades'],
                       'fu': PEF, 'lista': 'El gasto federalizado de 2026: lo que baja a estados y municipios'}
    for x in F['componentes']:
        fila(id=x['id'], g='fed26', n=limpio(x['nombreLargo']), c=limpio(x['nombre']), y='2026', v=round(x['montoMdp'], 1), e=x['estado'],
             fu=fu('Presupuesto de Egresos de la Federación 2026, ' + x['clave'].replace('PEF ', ''), 'ref-pef2026') if x['estado'] == 'oficial' else PEF,
             op='gasto federalizado total menos los Ramos 28, 33 y 25' if x['estado'] == 'derivado' else None,
             d=limpio(x['queEs']), al=al(x['nombre'].split(' — ')[-1], ALIAS.get(x['id'], [])), ir=[NUM + 'las-32-entidades.html', 'Las 32 entidades'])
    fila(id='fed-total', g='fed26', tot=1, n='Gasto federalizado de 2026', y='2026', v=F['totalMdp'], e='oficial', fu=PEF, d=limpio(F['nota']),
         al=['gasto federalizado', 'lo que baja a los estados', 'dinero para los estados', 'transferencias a estados', 'recursos federales a estados'],
         ir=[NUM + 'mapa-del-gasto-federalizado.html', 'El mapa del gasto federalizado'])
    # Los desgloses que la propia Ley de Ingresos o el Presupuesto traen dentro
    # de un renglón (IEPS por producto, Ramo 33 por fondo...): su parte se
    # mide contra su renglón, no contra el total.
    padres = {x['id']: x for x in P['ingresos'] + P['egresos'] + F['componentes']}
    hecho = {f['id']: f for f in filas}
    for pid, x in padres.items():
        for i, c in enumerate(x.get('componentes') or []):
            if not c.get('m'):
                continue
            nom = limpio(c['n'])
            corto = nom.split(' — ')[0] if ' — ' in nom else ''
            fila(id='%s-c%d' % (pid, i), g=hecho[pid]['g'], sub=1, pad=pid, n=('Ventas de ' + nom) if pid == 'ing-ventas' else nom, c=corto or None, y='2026', v=round(c['m'], 1), e=hecho[pid]['e'],
                 fu=hecho[pid]['fu'], d=limpio(c.get('d')) or 'Parte de %s.' % hecho[pid]['n'],
                 al=al(nom.split(' — ')[-1] if corto else nom, COMP_ALIAS.get(nom, []) + ([corto] if corto else [])), ir=hecho[pid]['ir'])

    M = P['municipal']
    grupos['mun26'] = {'n': 'lo que el Presupuesto etiqueta para municipios', 'tot': M['etiquetadoMdp'], 'ir': [NUM + 'los-municipios.html', 'Los municipios'],
                       'fu': PEF, 'lista': 'Lo que el Presupuesto 2026 cifra como municipal'}
    for x in M['fuentes']:
        fila(id=x['id'], g='mun26', n=limpio(x['nombreLargo']), c=limpio(x['nombre']), y='2026', v=round(x['montoMdp'], 1), e=x['estado'],
             fu=fu('Presupuesto de Egresos de la Federación 2026, ' + x['clave'].replace('PEF ', ''), 'ref-pef2026'), d=limpio(x['queEs']),
             al=al(x['nombre'], ALIAS.get(x['id'], [])), ir=[NUM + 'los-municipios.html', 'Los municipios'])
    fila(id='mun-total', g='mun26', tot=1, n='Recursos federales etiquetados para municipios en 2026', y='2026', v=round(M['etiquetadoMdp'], 1), e='oficial',
         fu=fu('Presupuesto de Egresos de la Federación 2026, Anexo 22', 'ref-pef2026'), d=limpio(M['nota']),
         al=['dinero para los municipios', 'recursos para municipios', 'lo que llega a los municipios', 'gasto municipal'],
         ir=[NUM + 'los-municipios.html', 'Los municipios'])

    # Lo que cobran los municipios por su cuenta (INEGI, EFIPEM 2024): sumas
    # de lo que reportó cada municipio.
    PROP_AL = {'mp-predial': ['predial en total', 'predial de todos los municipios', 'predial en todos los municipios', 'predial en el pais', 'predial en todo el pais', 'predial nacional', 'predial en mexico'],
               'mp-servicios': ['derechos por servicios publicos', 'cobro de agua de los municipios'],
               'mp-participaciones': ['participaciones a los municipios', 'participaciones de los municipios']}
    for x in M.get('propios', []):
        fila(id=x['id'], g='munp', n=limpio(x['nombreLargo']), c=limpio(x['nombre']), y='2024', v=x['montoMdp'], e=x['estado'],
             fu=fu('INEGI, Estadística de Finanzas Públicas Estatales y Municipales (EFIPEM) 2024', x.get('refKey')),
             op=limpio(x.get('comoSeObtuvo')).split('. ')[0], d=limpio(x['queEs']), ley=limpio(x.get('ley')), al=PROP_AL.get(x['id'], []),
             ir=[NUM + 'los-municipios.html', 'Los municipios'])

    # 5. El Anexo 1, ramo por ramo, y las unidades de los Poderes.
    A = P['anexo1PEF2026']
    FU_A1 = fu('Presupuesto de Egresos de la Federación 2026, Anexo 1, pp. %s' % A['paginas'], url=A['url'])
    grupos['ramo26'] = {'n': 'el gasto neto total de 2026', 'tot': A['gastoNetoTotal'] / 1e6, 'ir': [NUM + 'ramos-y-dependencias.html', 'Ramos y dependencias'],
                        'fu': FU_A1, 'lista': 'Los ramos del Presupuesto 2026 (Anexo 1)'}
    for g in A['grupos']:
        for r in g['ramos']:
            if not r['pesos']:
                continue
            costo = '· costo financiero' in r['nombre']
            nom = r['nombre'] if g['clave'] != 'B' or r['ramo'] in ('02', '31', '37', '47', '55', '56') else 'Secretaría de ' + r['nombre'].replace('Defensa', 'la Defensa').replace('Mujeres', 'las Mujeres')
            clave = 'ramo-' + r['ramo'] + ('-cf' if costo else '')
            extra = ALIAS_RAMO.get(r['ramo'], []) if not costo else []
            if r['ramo'].isdigit():
                extra = extra + ['ramo ' + r['ramo'], 'ramo ' + str(int(r['ramo']))]
            fila(id=clave, g='ramo26', sg=limpio(g['nombre']).capitalize(), n=limpio(nom), y='2026', v=round(r['pesos'] / 1e6, 1), e='oficial', fu=FU_A1,
                 d=('Ramo %s · %s · %s.' % (r['ramo'], limpio(g['nombre']).lower(), r['tipo'].lower())) if r['ramo'].isdigit() else '%s · %s.' % (limpio(g['nombre']).capitalize(), r['tipo'].lower()),
                 al=al(nom, extra) if not costo else [plano(r['nombre'])], par='u-' + r['ramo'] if not costo else None,
                 ir=[NUM + 'ramos-y-dependencias.html', 'Ramos y dependencias'])
            for u in r.get('unidades', []):
                uid = next((k for k, v in ALIAS_UNIDAD.items() if plano(v[0]) in plano(u['nombre'])), None)
                fila(id='ur-' + (uid or plano(u['nombre']).replace(' ', '-')), g='ramo26', sub=1, n=limpio(u['nombre']), y='2026', v=round(u['pesos'] / 1e6, 1), e='oficial',
                     fu=FU_A1, d='Parte del %s (Ramo %s).' % (limpio(r['nombre']), r['ramo']), al=al(u['nombre'], ALIAS_UNIDAD.get(uid, [])), par='u-' + (uid or ''),
                     ir=[NUM + 'lo-que-cuestan-los-poderes.html', 'Lo que cuestan el Congreso y la Judicatura'])
    for g in A['grupos']:
        fila(id='ramos-sub-' + g['clave'], g='ramo26', sub=1, sut=1, n=limpio(g['nombre']).capitalize() + ' (subtotal)', y='2026', v=round(g['subtotal'] / 1e6, 1), e='oficial', fu=FU_A1,
             d='El subtotal que imprime el decreto para este grupo de ramos.' + (' ' + limpio(A['notaSubtotal']) if g['clave'] == 'A' else ''),
             al=[plano(g['nombre'])], ir=[NUM + 'ramos-y-dependencias.html', 'Ramos y dependencias'])
    fila(id='ramos-neteo', g='ramo26', sub=1, sut=1, n='Lo que se resta para no contar dos veces (neteo)', y='2026', v=round(A['neteo'] / 1e6, 1), e='oficial', fu=FU_A1,
         d=limpio(A['notaNeteo']), al=['neteo', 'se cuenta dos veces', 'doble conteo'], ir=[NUM + 'ramos-y-dependencias.html', 'Ramos y dependencias'])
    fila(id='ramos-bruto', g='ramo26', sub=1, sut=1, n='Suma de todos los ramos antes de restar el neteo', y='2026', v=round((A['gastoNetoTotal'] + A['neteo']) / 1e6, 1), e='derivado', fu=FU_A1,
         op='gasto neto total + neteo', d='Si sumas todos los ramos del Anexo 1 da más que el presupuesto: hay dinero que sale de un ramo y entra a otro.',
         al=['suma de los ramos', 'suma bruta'], ir=[NUM + 'ramos-y-dependencias.html', 'Ramos y dependencias'])

    # Lo que de verdad gastaron en 2025 (Cuenta Pública), unidad por unidad.
    po = d['poderes']
    FU_CP = fu(po['fuentes']['CP2025']['doc'], url=po['fuentes']['CP2025']['url'])
    for u in po['ejercicio']['cp2025']['unidades']:
        uid = UR_UNIDAD.get((u['ramo'], u['ur']))
        if not uid or not u.get('ejercido'):
            continue
        fila(id='cp25-' + uid, g='cp25', n=limpio(u['nombre']).replace('H. ', ''), y='2025', v=round(u['ejercido'] / 1e6, 1), e='oficial', fu=FU_CP,
             d='Lo que de verdad ejerció en 2025; le habían aprobado %s millones.' % format(u['original'] / 1e6, ',.1f'), par='u-' + uid, al=[],
             ir=[NUM + 'lo-que-cuestan-los-poderes.html', 'Lo que cuestan el Congreso y la Judicatura'])

    # Por capítulo de gasto (en qué se va: sueldos, materiales, servicios...)
    # y lo pagado en lo que va de 2026.
    UR_CAP = {'RAMO03': 'ramo-03', '100': 'ur-scjn', '120': 'ur-oaj', '300': 'ur-tdj'}
    porid = {f['id']: f for f in filas}
    fco = po['fuentes'].get('COG', {})
    for ur, lst in po['judicial']['capitulosPorUR'].items():
        f = porid.get(UR_CAP.get(ur))
        if f:
            f['caps'] = {'y': '2026', 'et': 'aprobado', 'fu': fu(fco.get('doc') or fco.get('corto') or 'Clasificador por objeto del gasto, PEF 2026', url=fco.get('url')),
                         'l': [[c['cap'], limpio(c['concepto']), round(c['aprobado'] / 1e6, 1)] for c in lst if c.get('aprobado') is not None]}
    for ur, uid in (('100', 'ur-diputados'), ('200', 'ur-senado'), ('101', 'ur-asf')):
        lst = po['ejercicio']['cp2025'].get('capitulosLegislativo', {}).get(ur)
        if lst and uid in porid:
            porid[uid]['caps'] = {'y': '2025', 'et': 'ejercido', 'fu': FU_CP, 'l': [[c['cap'], limpio(c['concepto']), round(c['ejercido'] / 1e6, 1)] for c in lst]}
    av = po['ejercicio']['avance2026']
    fav = po['fuentes'].get(av['fuente'], {})
    for u in av['unidades']:
        uid = UR_UNIDAD.get((u['ramo'], u['ur']))
        if uid and 'ur-' + uid in porid and u.get('pagado') is not None:
            porid['ur-' + uid]['av'] = {'v': round(u['pagado'] / 1e6, 1), 'corte': av['corte'], 'fu': fu(fav.get('doc') or fav.get('corto'), url=fav.get('url'))}
    fcn = po['fuentes'].get('CNPLE', {})
    congresos = {x['entidad']: x['ejercidoMdp'] for x in po['legislativo']['congresos2024'] if x.get('estado') == 'oficial'}
    cong = {'v': congresos, 'fu': fu(fcn.get('doc') or fcn.get('corto'), url=fcn.get('url')), 'y': '2024'}

    # Los programas sociales que la ASF revisó en la Cuenta Pública 2024.
    for x in d['cuentaFederal2024'].get('evaluacion_social_mir', []):
        if x.get('ejercido_mdp') is None or x.get('estado_montos') != 'oficial':
            continue
        fila(id='mir-' + x['clave'], g='mir24', n=limpio(x['programa']), y='2024', v=round(x['ejercido_mdp'], 1), e='oficial',
             fu=fu(limpio(x['fuente_montos']).split(':')[0], url=x.get('url')),
             d='Ejercido en 2024 (Cuenta Pública). Le habían aprobado %s millones. Programa %s, ramo %s.' % (format(x['aprobado_mdp'], ',.1f'), x['clave'], x['ramo']),
             par='prog-pam' if x['clave'] == 'S176' else None, al=al(x['programa']), ir=[NUM + 'estado-de-resultados.html', 'El estado de resultados'])

    # 6. El Paquete Económico 2027.
    pq = d['paquete_2027']
    pqi = NUM + 'paquete-2027.html'
    for x in pq['finanzas']:
        base = {'g': 'pq27', 'n': limpio(x['n']), 'e': 'oficial', 'fu': CGPE, 'd': limpio(x['d']), 'ir': [NUM + 'paquete-2027-cifras.html', 'Las cifras del Paquete 2027']}
        fila(id='pq-' + x['id'], y='2027', v=x['m'], pib=x['pib'], par='pq-' + x['id'], al=al(x['n'].split(' · ')[0], ['deficit'] if x['id'] == 'f-balance' else
                                                                                       ['rfsp', 'requerimientos financieros', 'deficit amplio'] if x['id'] == 'f-rfsp' else
                                                                                       ['deuda publica', 'deuda del pais', 'shrfsp'] if x['id'] == 'f-shrfsp' else []), **base)
        fila(id='pq26-' + x['id'], y='2026', v=x['m26'], pib=x['pib26'], par='pq-' + x['id'], al=[], **dict(base, ir=[insp_nota.CATALOGO, 'Catálogo de cifras oficiales']))
    grupos['func27'] = {'n': 'el gasto programable propuesto para 2027', 'ir': [NUM + 'paquete-2027-gasto.html', 'El gasto del Paquete 2027'], 'fu': CGPE,
                        'lista': 'El gasto programable de 2027 por finalidad (propuesta)'}
    egr_par = {'Desarrollo social': 'egr-social', 'Desarrollo económico': 'egr-economico', 'Gobierno': 'egr-gobierno'}
    for x in pq['funcional']['filas']:
        fila(id='func-' + plano(x['n'])[:20].replace(' ', '-'), g='func27', n=limpio(x['n']), y='2027', v=round(x['ppef27'] * 1000, 1), v26=round(x['pef26'] * 1000, 1),
             var=x['var'], e='oficial', fu=fu('SHCP, Criterios Generales de Política Económica 2027, p. 39 (miles de millones)', 'ref-cgpe2027'), d=limpio(x['d']),
             par=egr_par.get(x['n']) or ('egr-poderes' if x['n'].startswith('Poderes') else None), al=[],
             ir=[NUM + 'paquete-2027-gasto.html', 'El gasto del Paquete 2027'])
    for clave, col, tit in (('soc27', 'sociales', 'Los programas sociales prioritarios de 2027 (propuesta)'), ('inv27', 'inversion', 'Las prioridades de inversión de 2027 (propuesta)')):
        C = pq[col]
        grupos[clave] = {'n': 'el total de %s propuesto para 2027' % ('los programas sociales prioritarios' if col == 'sociales' else 'las prioridades de inversión'),
                         'tot': C['total'], 'ir': [NUM + 'paquete-2027-gasto.html', 'El gasto del Paquete 2027'], 'fu': CGPE, 'lista': tit}
        for x in C['filas']:
            fila(id='%s-%s' % (clave, plano(x['n'])[:24].replace(' ', '-')), g=clave, sg=x.get('g'), n=limpio(x['n']), y='2027', v=x['m'], e='oficial',
                 fu=fu('SHCP, Criterios Generales de Política Económica 2027, p. 33', 'ref-cgpe2027'), d=limpio(x.get('d')),
                 al=al(x['n'], ['pension de adultos mayores', 'pension del bienestar', 'pension de los abuelitos', 'pension para adultos mayores'] if 'Adultos Mayores' in x['n'] else []),
                 par='prog-pam' if 'Adultos Mayores' in x['n'] else None,
                 ir=[NUM + 'paquete-2027-gasto.html', 'El gasto del Paquete 2027'])
        fila(id=clave + '-total', g=clave, tot=1, n=tit.replace('Los ', '').replace('Las ', '').replace(' (propuesta)', ''), y='2027', v=C['total'], e='oficial',
             fu=fu('SHCP, Criterios Generales de Política Económica 2027, p. 33', 'ref-cgpe2027'), d=limpio(C['nota']),
             al=['programas sociales', 'programas del bienestar', 'apoyos sociales'] if col == 'sociales' else ['inversion 2027', 'obras 2027', 'prioridades de inversion', 'proyectos prioritarios'],
             ir=[NUM + 'paquete-2027-gasto.html', 'El gasto del Paquete 2027'])
    for x in pq['amortiguadores'] + pq['contingentes']:
        cont = x in pq['contingentes']
        fila(id='pq-' + plano(x['n'])[:28].replace(' ', '-'), g='colchon', st=1, n=limpio(x['n']), y='2026', v=x['m'], u=x.get('u', 'mdp'), pib=x.get('pib'),
             e='oficial', fu=CGPE, d=limpio(x['d']) + ((' La ley fija como reserva adecuada %s millones: hoy tiene el %s %%.' % (format(x['meta'], ',.1f'), x['metaPct'])) if x.get('meta') else ''), al=al(x['n'], ['feip', 'fondo de estabilizacion de los ingresos'] if 'FEIP' in x['n'] else
                                                         ['feief'] if 'FEIEF' in x['n'] else ['reservas internacionales', 'reservas del banco de mexico'] if 'Reservas' in x['n'] else
                                                         ['pasivo pensionario', 'deuda de las pensiones'] if 'pensionario' in x['n'] else []),
             ir=[NUM + 'paquete-2027-colchon.html', 'El colchón del Paquete 2027'], tipo='contingente' if cont else 'amortiguador')
    marco = []
    for x in pq['marco']:
        marco.append({'n': limpio(x['v']), 'u': limpio(x['u']), 'a26': x['a26'], 'e26': x['e26'], 'p27': x['p27'], 'nota': limpio(x.get('n')),
                      'al': al(x['v'], {'Tipo de cambio': ['dolar', 'precio del dolar'], 'Mezcla mexicana de exportación': ['precio del petroleo', 'barril'],
                                         'Inflación, diciembre contra diciembre': ['inflacion'], 'Crecimiento real del PIB': ['crecimiento', 'cuanto va a crecer'],
                                         'Tasa de interés, Cetes 28 días': ['tasa de interes', 'cetes']}.get(x['v'], []))})

    # 7. El estado de resultados del Gobierno Federal (Cuenta Pública 2024).
    cf = d['cuentaFederal2024']
    for x in cf['cifras']:
        if x.get('mdp') is None or x['estado'] != 'oficial':
            continue
        fila(id='cf24-' + x['id'], g='cf24', n=limpio(x['concepto']), y='2024', v=x['mdp'], e='oficial', fu=fu(limpio(x['fuente'])[:160], url=x.get('url') or cf['fuente']['url']),
             d=limpio(cf['alcance']), al=CF_ALIAS.get(x['id'], []), ir=[NUM + 'estado-de-resultados.html', 'El estado de resultados'])

    # 8. Las series de 1990 a 2025.
    fs = d['finanzas_sexenales']
    serie = {}
    for k, nom, ali in (('ingresos', 'los ingresos presupuestarios del sector público', 'ingres|recaud|entr[oó]'),
                        ('gasto', 'el gasto neto del sector público presupuestario', 'gast|egres|presupuesto'),
                        ('inversion', 'la inversión física presupuestaria', 'invers|obra'),
                        ('costo_financiero', 'el costo financiero de la deuda (los intereses)', 'interes|costo financiero')):
        f0 = fs['fuentes'][fs['anual'][k]['2025']['f'][0]]
        serie[k] = {'n': nom, 're': ali, 'fu': {'tx': f0['corto'], 'url': f0['url']},
                    'a': {y: [v['mdp'], v.get('pib')] for y, v in fs['anual'][k].items() if v.get('mdp') is not None}}

    return {'filas': filas, 'grupos': grupos, 'marco': marco, 'serie': serie, 'congresos': cong,
            'pob': {'v': d['calculadora_civica']['parametros']['poblacion']['personas'],
                    'fu': fu(d['calculadora_civica']['parametros']['poblacion']['fuente'], url=d['calculadora_civica']['parametros']['poblacion']['url'])},
            'cgpe': {'gasto': next(x for x in pq['finanzas'] if x['id'] == 'f-gasto'), 'ing': next(x for x in pq['finanzas'] if x['id'] == 'f-ing')}}
