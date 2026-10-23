# -*- coding: utf-8 -*-
"""Las cifras de la pestaña «Datos», en el formato con que conversa el bot
(pedido del autor, 23-10-2026: «continúa verificando la información que se
encuentra en la pestaña de datos»). Es la segunda pestaña; la primera fue
Números (asistente_numeros.py).

Cada renglón es una cifra que ya aparece en una página de Datos, con su
estado, su documento y la página donde se lee. No hay una sola cifra nueva:
todo sale de window.AUDIT_DB o del tablero del Radar hacendario.

- Medio ambiente (datos-ambiente-*.html): las Cuentas Económicas y
  Ecológicas 2024 del INEGI (cuentas_ecologicas), la basura del diagnóstico
  de la SEMARNAT y el Ramo 16 órgano por órgano (ambiente).
- Informes de la Cuenta Pública (informes-cuenta-publica.html): lo que
  revisó la ASF de 2019 a 2024, la primera entrega de 2025, dónde se
  concentra lo por aclarar y los plazos de la ley (cuenta_publica_asf).
- El peso en el tiempo (radar-peso-*.html): el dólar y el euro de hoy, el
  INPC, la inflación y la proyección de Hacienda (finanzas_sexenales.peso,
  ya preparado por el Radar).
- Datos abiertos (datos-descargas.html): las siete bases que se descargan.

Los renglones se suman a los de Números (dat.num.filas) y el bot los busca
igual; los que no son millones de pesos traen su unidad (un) y su frase
(fr, con {V} donde va la cifra). asistente-charla.js los lee.

Fuera, a propósito: el costo de las megaobras (datos-ambiente-megaobras.html)
viene del registro del simulador de megaobras, que se revisa con su
herramienta en la pestaña Herramientas.
"""
import os
import re

from asistente_numeros import limpio, plano

AMB = 'datos-ambiente-'
INF = 'informes-cuenta-publica.html'


def _al(*xs):
    return sorted({plano(x) for x in xs if len(plano(x)) >= 3}, key=len, reverse=True)


def _n(v, dec=0):
    return format(v, ',.%df' % dec)


def _mdp(v):
    return '$' + _n(v, 1) + ' millones'


def datos(d, num, radar):
    refs = {r['id']: r for r in d['referencias_legales']}

    def fu(tx, rid=None, url=None):
        return {'tx': limpio(tx), 'url': url or (refs.get(rid) or {}).get('url')}

    filas, grupos = num['filas'], num['grupos']

    def fila(**o):
        filas.append({k: v for k, v in o.items() if v not in (None, '', [])})

    # ------------------------------------------------------------------
    # 1. Lo que cuesta el daño ambiental (INEGI, CEEM 2024).
    C = d['cuentas_ecologicas']
    FC = fu('INEGI, Cuentas Económicas y Ecológicas de México 2024, comunicado 150/25, Tabla 1, p. 2', C['ref_fuente'])
    FP = fu('INEGI, PIB a precios de mercado 2024', C['ref_pib'])
    ct = C['ctada']['total_mdp']
    grupos['amb24'] = {'n': 'el costo ambiental de 2024', 'tot': ct, 'ir': [AMB + 'desglose.html', 'Qué se acabó y qué se ensució'],
                       'lista': 'El costo ambiental de 2024, renglón por renglón', 'li': 1,
                       'sug': ['¿En qué se va el costo ambiental?', '¿Cuánto cuesta la contaminación del aire?', '¿Cuánto se gasta en proteger el medio ambiente?', '¿Cuál es el PIB ecológico?']}
    cas = dict((x['id'], x) for x in C['cascada'])
    fila(id='amb-pib', g='amb24', st=1, n='Producto Interno Bruto de 2024', y='2024', v=C['pib_mdp'], e=C['pib_estado'], fu=FP,
         fr='En 2024, el Producto Interno Bruto (PIB) de México fue de {V}, a precios de mercado, según el INEGI.',
         d='Es el número que se anuncia cada trimestre. No descuenta el desgaste de la maquinaria ni lo que costó a la naturaleza: '
           'por eso el INEGI calcula también el PIB ecológico (PINE), de $25.7 billones.',
         al=_al('producto interno bruto', 'pib de mexico', 'pib del pais', 'pib 2024', 'pib de 2024', 'cuanto es el pib', 'pib nacional'),
         ir=[AMB + 'pib.html', 'El PIB que no alcanza'])
    fila(id='amb-pine', g='amb24', st=1, n='Producto Interno Neto Ecológico de 2024', y='2024', v=cas['pine']['monto_mdp'], vt='$25.7 billones',
         e='oficial', fu=fu('INEGI, Cuentas Económicas y Ecológicas de México 2024, comunicado 150/25, p. 1', C['ref_fuente']),
         fr='En 2024, el Producto Interno Neto Ecológico (el «PIB ecológico») fue de {V}: el 76.6 % del PIB. Es lo que de verdad quedó '
            'después de reponer la maquinaria que se desgastó y de pagar la cuenta ambiental.',
         d='El INEGI lo publica así, redondeado. De cada $100 que el país anunció haber producido, quedaron $76.6.',
         al=_al('producto interno neto ecologico', 'pib ecologico', 'pine', 'pib verde', 'lo que de verdad quedo'),
         ir=[AMB + 'pib.html', 'El PIB que no alcanza'])
    for k, nom, alx in (('ccf', 'Consumo de capital fijo de 2024', ('consumo de capital fijo', 'desgaste de la maquinaria')),
                        ('pin', 'Producto Interno Neto de 2024', ('producto interno neto',))):
        x = cas[k]
        fila(id='amb-' + k, g='amb24', st=1, n=nom, y='2024', v=x['monto_mdp'], e='derivado', fu=FC,
             vt='entre $%s y $%s millones; punto medio $%s millones' % (_n(x['monto_mdp'] - 50000), _n(x['monto_mdp'] + 50000), _n(x['monto_mdp'])),
             op=('PIB − costos ambientales (CTADA) − PINE' if k == 'ccf' else 'PINE + costos ambientales (CTADA)') +
                ', con el PINE entre $25.65 y $25.75 billones (el INEGI lo publica redondeado a 25.7); punto medio = (mínimo + máximo) ÷ 2',
             fr='En 2024, el ' + nom.replace(' de 2024', '').lower().replace('producto interno neto', 'Producto Interno Neto') + ' fue de {V}.',
             d=limpio(x['glosa']) + ' Es un rango porque sale de un PINE redondeado; la cifra exacta está en los tabulados del INEGI, que la plataforma aún no integra.',
             al=_al(*alx), ir=[AMB + 'pib.html', 'El PIB que no alcanza'])
    fila(id='amb-ctada', g='amb24', tot=1, n='Costo ambiental de 2024 (agotamiento y degradación)', y='2024', v=ct, e='oficial', fu=FC,
         fr='En 2024, el daño ambiental —lo que costó agotar y degradar la naturaleza para producir— fue de {V}: el 4.1 % del PIB, según el INEGI.',
         d='Su nombre técnico es Costos Totales por Agotamiento y Degradación Ambiental (CTADA). No aparece en el Presupuesto de Egresos: '
           'no tiene partida ni responsable con nombre.',
         al=_al('costo ambiental', 'costos ambientales', 'dano ambiental', 'danos ambientales', 'ctada', 'deterioro ambiental', 'costo del dano ambiental',
                'costos totales por agotamiento y degradacion', 'costo del deterioro', 'cuenta ambiental', 'dano al medio ambiente', 'dano a la naturaleza'),
         ir=[AMB + 'desglose.html', 'Qué se acabó y qué se ensució'])
    for rid, gn, alx in (('agotamiento', 'el agotamiento de recursos naturales', ('agotamiento', 'agotamiento de recursos naturales', 'recursos que se acabaron')),
                         ('degradacion', 'la degradación del ambiente', ('degradacion', 'degradacion ambiental', 'degradacion del ambiente'))):
        R = C[rid]
        pid = 'amb-' + rid
        fila(id=pid, g='amb24', sub=1, sut=1, n=gn[3:].capitalize() + ' (2024)', gn=gn, y='2024', v=R['total_mdp'], e=R['estado'], fu=FC,
             fr='En 2024, ' + gn + ' costó {V}: el %s %% del PIB.' % _n(R['pct_pib'], 1), d=limpio(R['definicion']), al=_al(*alx),
             ir=[AMB + 'desglose.html', 'Qué se acabó y qué se ensució'])
        for x in R['componentes']:
            # El agotamiento se lee contra su rubro y la degradación contra
            # todo el costo ambiental, como lo dice la página.
            fila(id=pid + '-' + x['id'], g='amb24', sub=1, li=1, pad=pid if rid == 'agotamiento' else None, n=limpio(x['nombre']), y='2024', v=x['monto_mdp'],
                 e=x['estado'], fu=FC, fr='En 2024, el costo ' + {'aire': 'de las emisiones al aire', 'suelo': 'de la degradación del suelo',
                                                                  'residuos': 'de los residuos sólidos urbanos (la basura mal gestionada)',
                                                                  'aguas_residuales': 'del tratamiento insuficiente de aguas residuales'}.get(x['id'], 'del ' + limpio(x['nombre'][0].lower() + x['nombre'][1:])) + ' fue de {V}' +
                 (' (%s %% del PIB)' % _n(x['pct_pib'], 1) if x.get('pct_pib') is not None else '') + ', según el INEGI.',
                 d=limpio(x['glosa']), ir=[AMB + 'desglose.html', 'Qué se acabó y qué se ensució'],
                 al=_al(x['nombre'], *{'aire': ('contaminacion del aire', 'emisiones al aire', 'contaminacion atmosferica', 'aire contaminado', 'costo del aire'),
                                       'suelo': ('degradacion del suelo', 'erosion', 'suelo degradado'),
                                       'residuos': ('dano por basura', 'costo de la basura', 'basura mal gestionada', 'residuos solidos urbanos'),
                                       'aguas_residuales': ('aguas residuales', 'aguas negras', 'agua sin tratar'),
                                       'hidrocarburos': ('agotamiento de hidrocarburos', 'agotamiento del petroleo'),
                                       'forestal': ('agotamiento forestal', 'bosque perdido', 'deforestacion', 'perdida de bosques'),
                                       'agua': ('agua subterranea', 'acuiferos', 'agotamiento del agua')}.get(x['id'], ())))
    P = C['gasto_proteccion_ambiental']
    fila(id='amb-proteccion', g='amb24', st=1, n='Gasto público en protección ambiental de 2024', y='2024', v=P['monto_mdp'], e=P['estado'], fu=FC,
         fr='En 2024, el sector público gastó {V} en proteger el ambiente: el %s %% del PIB.' % _n(P['pct_pib'], 1),
         d='Frente a un daño de %s: por cada peso que se destinó a proteger, el país resintió $%s de deterioro. Solo es el sector público '
           'consolidado (gobierno federal, entidades, municipios y empresas públicas): no incluye empresas privadas ni hogares.' % (_mdp(ct), _n(ct / P['monto_mdp'], 2)),
         al=_al('proteccion ambiental', 'proteger el ambiente', 'proteger el medio ambiente', 'gasto en proteccion ambiental', 'gasto ambiental',
                'se gasta en proteger', 'gasta en el medio ambiente', 'invierte en el medio ambiente'),
         ir=[AMB + 'proteger.html', 'Lo que se gasta en proteger'])
    fila(id='amb-razon', g='amb24', st=1, n='Daño ambiental por cada peso de protección (2024)', y='2024', v=round(ct / P['monto_mdp'], 2), un='pesos', dec=2,
         vt='$%s' % _n(ct / P['monto_mdp'], 2), e='derivado', fu=FC, op='%s ÷ %s' % (_mdp(ct), _mdp(P['monto_mdp'])),
         fr='En 2024, por cada peso del erario destinado a proteger el ambiente, el país resintió {V} de daño ambiental.',
         al=_al('por cada peso de proteccion', 'cuantos pesos de dano', 'dano por cada peso', 'proporcion del dano'),
         ir=[AMB + 'proteger.html', 'Lo que se gasta en proteger'])

    # ------------------------------------------------------------------
    # 2. La basura (SEMARNAT-INECC, Diagnóstico de residuos, abril de 2026).
    A = d['ambiente']
    FA = A['fuentes']
    R = A['residuos']

    def fa(clave, pag):
        f = FA[clave]
        return fu('%s, p. %s' % (f['corto'], pag), url=f['url'])
    grupos['basura'] = {'n': 'la basura', 'ir': [AMB + 'basura.html', 'La basura'],
                        'sug': ['¿Cuánta basura se genera al día?', '¿Cuánta basura se recolecta?', '¿Cuántos rellenos sanitarios hay?', '¿Cuánta basura genera una persona?']}
    IRB = [AMB + 'basura.html', 'La basura']
    g, rc, sp, sd, rs = R['generacionTdia'], R['recolectadaTdia'], R['separadaTdia'], R['sitiosDisposicion'], R['rellenosSanitarios']
    sinp = R['sinPartidaFederal']['texto']
    fila(id='bas-gen', g='basura', st=1, n='Basura que se genera al día en México', y='2026', v=g['valor'], un='toneladas al día', e=g['estado'], fu=fa(g['fuente'], g['pagina']),
         fr='En México se generan {V} de basura (residuos sólidos urbanos), según el diagnóstico de la SEMARNAT de abril de 2026.',
         d='Recogerla, trasladarla y disponerla es obligación del municipio (artículo 115 constitucional). ' + sinp,
         al=_al('basura se genera', 'basura generada', 'genera de basura', 'generan de basura', 'cuanta basura', 'toneladas de basura', 'residuos solidos', 'generacion de residuos', 'basura al dia'), ir=IRB)
    fila(id='bas-rec', g='basura', st=1, n='Basura que se recolecta al día', y='2022', v=rc['valor'], un='toneladas al día', e=rc['estado'], fu=fa(rc['fuente'], rc['pagina']), par='bas-rec',
         fr='Se recolectan {V} de basura: el %s %% de lo que se genera. Quedan sin recolectar %s toneladas al día.' % (_n(rc['pct'], 1), _n(g['valor'] - rc['valor'])),
         op='%s − %s toneladas generadas y recolectadas' % (_n(g['valor']), _n(rc['valor'])), d=limpio(rc.get('nota')), sx=1,
         al=_al('basura se recolecta', 'recolectan de basura', 'recoleccion de basura', 'basura recolectada', 'recolecta de basura'), ir=IRB)
    S = R['recolectadaSerie']
    for y, t in zip(S['anios'], S['tdia']):
        if y == 2022:
            continue
        fila(id='bas-rec-%d' % y, g='basura', st=1, sub=1, n='Basura recolectada al día en %d' % y, y=str(y), v=t, un='toneladas al día', e=S['estado'], par='bas-rec', sx=1,
             fu=fu('%s, p. %s' % (FA['DBGIR']['corto'], S['pagina']), url=FA['DBGIR']['url']),
             fr='En %d se recolectaban {V} de basura en el país, según el Censo de Gobiernos Municipales del INEGI.' % y, ir=IRB)
    fila(id='bas-sep', g='basura', st=1, n='Basura que se recolecta separada', y='2026', v=sp['pct'], un='%', dec=1, e=sp['estado'], fu=fa(sp['fuente'], sp['pagina']),
         fr='Solo el {V} de la basura se recolecta separada.', al=_al('basura separada', 'recolecta separada', 'separacion de basura', 'se separa la basura'), ir=IRB)
    fila(id='bas-disp', g='basura', st=1, n='Basura que llega a un sitio de disposición final', y='2026', v=sd['tdia'], un='toneladas al día', e=sd['estado'], fu=fa(sd['fuente'], sd['pagina']),
         fr='Llegan {V} a alguno de los %s sitios de disposición final del país.' % _n(sd['valor']),
         al=_al('disposicion final', 'a donde va la basura', 'donde termina la basura', 'tiraderos', 'basureros'), ir=IRB)
    fila(id='bas-sitios', g='basura', st=1, n='Sitios de disposición final', y='2026', v=sd['valor'], un='sitios', e=sd['estado'], fu=fa(sd['fuente'], sd['pagina']),
         fr='En México hay {V} de disposición final de basura; solo %d son rellenos sanitarios.' % rs['valor'],
         al=_al('sitios de disposicion', 'cuantos basureros', 'cuantos tiraderos'), ir=IRB)
    fila(id='bas-rellenos', g='basura', st=1, n='Rellenos sanitarios', y='2026', v=rs['valor'], un='rellenos sanitarios', e=rs['estado'], fu=fa(rs['fuente'], rs['pagina']),
         fr='En México hay {V}, el único sitio controlado por la norma. Reciben %s toneladas al día: el %s %% de lo que llega a disposición final. '
            'Los otros %s sitios (%s toneladas al día) se clasifican como no controlados.' % (_n(rs['tdia'], 1), _n(rs['pct'], 1), _n(sd['valor'] - rs['valor']), _n(sd['tdia'] - rs['tdia'], 1)),
         op='%s − %s sitios; %s − %s toneladas al día' % (_n(sd['valor']), rs['valor'], _n(sd['tdia']), _n(rs['tdia'], 1)), d=limpio(rs.get('nota')),
         al=_al('rellenos sanitarios', 'relleno sanitario', 'rellenos', 'llega a un relleno'), ir=IRB)
    ms = R['municipiosSinRecoleccion']
    fila(id='bas-sinrec', g='basura', st=1, n='Municipios sin servicio de recolección de basura', y='2026', v=ms['valor'], un='municipios', e=ms['estado'], fu=fa(ms['fuente'], ms['pagina']),
         fr='{V} del país no tienen servicio de recolección de basura; %d de ellos están en Oaxaca.' % ms['oaxaca'],
         al=_al('municipios no tienen recoleccion', 'municipios sin recoleccion', 'no tienen recoleccion de basura', 'sin recoleccion', 'sin servicio de recoleccion', 'no tienen recoleccion', 'no recogen la basura', 'sin servicio de basura', 'no tienen servicio de basura'), ir=IRB)
    pc = R['perCapitaKg']
    fila(id='bas-percap', g='basura', st=1, n='Basura que genera una persona al día', y='2026', v=pc['valor'], un='kilos', dec=3, e=pc['estado'], fu=fa(pc['fuente'], pc['pagina']),
         fr='Cada persona genera en promedio {V} de basura al día: unos %s kilos al año.' % _n(pc['valor'] * 365, 0),
         op='%s kilos × 365 días' % pc['valor'], d='Es el promedio nacional: tu municipio puede estar mejor o peor. En la página puedes calcular lo de tu casa.',
         al=_al('basura por persona', 'genera una persona', 'basura genera una persona', 'per capita', 'cada persona genera', 'kilos de basura', 'basura por habitante', 'basura genero yo'), ir=IRB)
    vh = R['vehiculos']
    fila(id='bas-camiones', g='basura', st=1, n='Camiones recolectores de basura', y='2026', v=vh['valor'], un='camiones', e=vh['estado'], fu=fa(vh['fuente'], vh['pagina']),
         fr='El país tiene {V} recolectores de basura; el %s %% son anteriores a 2002.' % _n(vh['pctAntes2002'], 2),
         al=_al('camiones recolectores', 'camiones de basura', 'camion de la basura', 'vehiculos recolectores'), ir=IRB)

    # ------------------------------------------------------------------
    # 3. El presupuesto ambiental (Ramo 16): aprobado, pagado y proyecto 2027.
    PR = A['presupuesto']
    FPEF = fa('PEF', PR['aprobado2026']['pagina']).copy()
    FPEF['tx'] = '%s, %s' % (FA['PEF']['corto'], PR['aprobado2026']['pagina'])
    FAV = {'tx': FA['AV2T2026']['corto'] + ', base de datos', 'url': FA['AV2T2026']['url']}
    FPP = {'tx': FA['PPEF2027']['corto'] + ', base de datos', 'url': FA['PPEF2027']['url']}
    ap = PR['aprobado2026']['valor'] / 1e6
    IRP = [AMB + 'presupuesto.html', 'El presupuesto ambiental']
    grupos['r16'] = {'n': 'el presupuesto ambiental (Ramo 16)', 'tot': round(ap, 1), 'ir': IRP,
                     'lista': 'El presupuesto ambiental de 2026 (Ramo 16), órgano por órgano'}
    ALR = {'B00': ('conagua', 'comision nacional del agua', 'cna'), 'RHQ': ('conafor', 'comision nacional forestal'),
           'F00': ('conanp', 'areas naturales protegidas'), 'E00': ('profepa', 'procuraduria federal de proteccion al ambiente'),
           'G00': ('asea', 'agencia de seguridad industrial'), 'RJJ': ('inecc', 'instituto nacional de ecologia'),
           'RESTO': ('oficinas centrales de la semarnat', 'resto de la semarnat')}

    def art(nom, para=False):
        la = re.match(r'(Comisi|Procur|Agencia)', nom)
        return (('la ' if la else 'el ') if para else ('a la ' if la else 'al ')) + nom

    for u in PR['unidades'] + [dict(ur='TOTAL', nombre='Ramo 16, Medio Ambiente y Recursos Naturales', aprobado=PR['aprobado2026']['valor'],
                                     modificado=PR['modificado2026']['valor'], pagado=PR['pagado2026']['valor'], proyecto2027=PR['proyecto2027']['valor'])]:
        tot = u['ur'] == 'TOTAL'
        nom = limpio(u['nombre'])
        a, m, p, py = u['aprobado'] / 1e6, u['modificado'] / 1e6, u['pagado'] / 1e6, u['proyecto2027'] / 1e6
        rid = 'r16-' + u['ur'].lower()
        fila(id=rid, g='r16', tot=1 if tot else None, n=nom, y='2026', v=round(a, 1), e='oficial', fu=FPEF, par=rid,
             fr=('Para 2026, el presupuesto ambiental (Ramo 16, Medio Ambiente y Recursos Naturales) es de {V}. Reúne a la SEMARNAT, la Comisión Nacional del Agua y sus órganos.'
                 if tot else 'Para 2026, el Presupuesto le aprobó {V} ' + art(nom) + ' (Ramo 16).'),
             av={'v': round(p, 1), 'mod': round(m, 1), 'corte': '30 de junio de 2026', 'fu': FAV},
             d=limpio(PR['proyecto2027'].get('nota')) if tot else None,
             al=_al('presupuesto ambiental', 'sector ambiental', 'ramo 16', 'presupuesto del medio ambiente', 'presupuesto para el medio ambiente', 'dinero para el medio ambiente')
             if tot else _al(nom, *ALR.get(u['ur'], ())), ir=IRP)
        fila(id=rid + '-27', g='r16', sub=1, st=1, tot=1 if tot else None, n=nom, y='2027', v=round(py, 1), e='oficial', fu=FPP, par=rid,
             fr='Para 2027, el proyecto de Presupuesto propone {V} para ' + ('el Ramo 16 (Medio Ambiente y Recursos Naturales)' if tot else art(nom, True)) +
                ': %s%s %% nominal contra lo aprobado en 2026. Todavía es propuesta: la Cámara de Diputados puede cambiarla hasta el 15 de noviembre.' % ('+' if py >= a else '−', _n(abs(py / a - 1) * 100, 1)),
             op='(%s ÷ %s − 1) × 100' % (_mdp(py), _mdp(a)), ir=IRP)

    # ------------------------------------------------------------------
    # 4. Lo que revisó la ASF en la Cuenta Pública (Matriz de Datos Básicos).
    Q = d['cuenta_publica_asf']
    FQ = Q['fuentes']

    def fq(clave, pag):
        f = FQ[clave]
        return {'tx': '%s, p. %s' % (f['corto'], pag), 'url': f['url']}
    T = Q['cp2024']['total']
    MET = [  # clave, nombre, unidad, verbo, alias
        ('auditorias', 'Auditorías practicadas', 'auditorías', 'practicó', ('auditorias practicadas', 'auditorias de la asf', 'auditorias hizo la asf', 'auditorias realizo la asf', 'cuantas auditorias', 'numero de auditorias', 'auditorias en la cuenta publica')),
        ('acciones', 'Acciones promovidas', 'acciones', 'promovió', ('acciones promovidas', 'acciones de la asf', 'acciones promovio', 'cuantas acciones')),
        ('PO', 'Pliegos de observaciones', 'pliegos de observaciones', 'emitió', ('pliegos de observaciones', 'pliegos de observacion', 'cuantos pliegos', 'pliegos')),
        ('PRAS', 'Promociones de responsabilidad administrativa sancionatoria', 'promociones de responsabilidad administrativa sancionatoria (PRAS)', 'emitió', ('pras', 'promociones de responsabilidad')),
        ('R', 'Recomendaciones', 'recomendaciones', 'emitió', ('recomendaciones de la asf', 'cuantas recomendaciones')),
        ('RD', 'Recomendaciones al desempeño', 'recomendaciones al desempeño', 'emitió', ('recomendaciones al desempeno',)),
        ('SA', 'Solicitudes de aclaración', 'solicitudes de aclaración', 'emitió', ('solicitudes de aclaracion',)),
        ('PEFCF', 'Promociones del ejercicio de la facultad de comprobación fiscal', 'promociones del ejercicio de la facultad de comprobación fiscal (avisos al SAT)', 'emitió', ('facultad de comprobacion fiscal', 'pefcf', 'avisos al sat')),
        ('recuperaciones', 'Recuperaciones operadas', None, 'recuperó durante las auditorías', ('recuperaciones', 'recupero la asf', 'recuperado por la asf', 'cuanto se recupero', 'cuanto recupero', 'dinero recuperado', 'monto recuperado')),
        ('porAclarar', 'Monto por aclarar', None, 'dejó por aclarar', ('por aclarar en la cuenta publica', 'aclarar en la cuenta publica', 'por aclarar', 'monto por aclarar', 'falta por aclarar', 'quedo por aclarar', 'sin aclarar', 'falta aclarar')),
        ('observado', 'Monto observado', None, 'observó', ('monto observado', 'cuanto observo', 'observado por la asf')),
        ('universo', 'Universo seleccionado', None, 'tomó como universo', ('universo seleccionado', 'universo de la asf')),
        ('muestra', 'Muestra auditada', None, 'revisó una muestra de', ('muestra auditada', 'cuanto reviso la asf', 'cuanto dinero reviso', 'cuanto audito la asf', 'monto auditado')),
        ('representatividad', 'Representatividad de la muestra', '%', 'revisó', ('representatividad',)),
    ]
    IRQ = [INF, 'Informes de la Cuenta Pública (ASF)']
    # La página grafica estas cinco año por año (2019 a 2024); las demás, solo de 2024 y 2025.
    SERIE_PAG = ('auditorias', 'PO', 'recuperaciones', 'porAclarar', 'observado')
    grupos['asf'] = {'n': 'lo que revisó la ASF', 'ir': IRQ,
                     'sug': ['¿Cuánto quedó por aclarar en la Cuenta Pública 2024?', '¿Cuántos pliegos de observaciones hubo?', '¿Dónde se concentra lo por aclarar?', '¿Cuánto recuperó la ASF?']}
    OJO = 'Ojo: «por aclarar» no es daño comprobado: es lo que, al cierre de la auditoría, no tenía documentos que acreditaran el gasto, y puede solventarse después.'
    ser = dict((s['cp'], s) for s in Q['serie'])
    c25 = Q['cp2025']

    def val(k, v):
        return v / 1e6 if k in ('recuperaciones', 'porAclarar', 'observado', 'universo', 'muestra') else v

    for k, nom, un, verbo, alx in MET:
        mdp = un is None
        base = 'asf-' + k.lower()

        def frase(y, ent=''):
            if k == 'representatividad':
                return 'En la Cuenta Pública %s%s, la muestra que revisó la ASF fue el {V} del universo seleccionado.' % (y, ent)
            return 'En la Cuenta Pública %s%s, la ASF %s {V}.' % (y, ent, verbo)
        anios = sorted(y for y, s in ser.items() if k in s and s[k] is not None and k in SERIE_PAG)
        if k in T and 2024 not in anios:
            anios.append(2024)
        for y in anios + ([2025] if k in c25 and k != 'observado' else []):
            vt = None
            if y == 2025:
                v, est, fte, ent = c25[k], c25['estado'], fq(c25['fuente'], c25['pagina']), ' (primera entrega, junio de 2026)'
                if k in ('recuperaciones', 'porAclarar'):
                    vt = '$' + _n(v) + ' pesos'
            elif y == 2024 and k in T:
                v, est, fte, ent = T[k], Q['cp2024']['estado'], fq(Q['cp2024']['fuente'], Q['cp2024']['pagina']), ' (las tres entregas, corte febrero de 2026)'
            else:
                s = ser[y]
                v, est, fte, ent = s[k], (s.get('observadoEstado') if k == 'observado' else None) or 'oficial', fq(s['fuente'], s['pagina']), ''
            if k == 'SA' and v == 1:
                un = 'solicitud de aclaración'
            elif k == 'SA':
                un = 'solicitudes de aclaración'
            ult = y == 2024 or (k not in T and y == anios[-1])
            fila(id=base + ('' if ult else '-%d' % y), g='asf', st=1, sub=None if ult else 1, sx=1, n=nom + ' (Cuenta Pública %d)' % y, y=str(y), par=base,
                 v=round(val(k, v), 1) if mdp else v, vt=vt, un=None if mdp else un, dec=2 if k == 'representatividad' else 0, e=est, fu=fte, fr=frase(y, ent),
                 op='monto por aclarar + recuperaciones operadas' if est == 'derivado' and k == 'observado' else None,
                 d=((OJO if k == 'porAclarar' else '') + (' La revisión de 2025 sigue: la segunda entrega es el 30 de octubre de 2026 y la tercera, el 20 de febrero de 2027.' if y == 2025 else '') +
                    (' Tengo de la Cuenta Pública %d a la %d: pregúntame por otro año.' % (anios[0], 2025 if k in c25 else anios[-1]) if len(anios) > 1 or k in c25 else '')).strip(),
                 al=_al(*alx) if ult else [], ir=IRQ)
    pa = T['porAclarar'] / 1e6
    # Los seis años juntos, como los suma la página.
    obs6, rec6 = sum(x['observado'] for x in Q['serie']) / 1e6, sum(x['recuperaciones'] for x in Q['serie']) / 1e6
    ys6 = '%d a %d' % (Q['serie'][0]['cp'], Q['serie'][-1]['cp'])
    fila(id='asf6-obs', g='asf', st=1, n='Lo observado por la ASF de %s' % ys6, y=str(Q['serie'][-1]['cp']), v=round(obs6, 1), e='derivado',
         fu=fq('MDB2024', Q['cp2024']['pagina']), op='suma de lo observado en las Cuentas Públicas %s (para 2023 y 2024, recuperado + por aclarar)' % ys6,
         fr='En las Cuentas Públicas %s, la ASF observó en total {V}; durante las propias auditorías se recuperaron %s: el %s %%.' % (ys6, _mdp(rec6), _n(rec6 / obs6 * 100, 1)),
         d='Pesos de cada año, sin ajustar por inflación. ' + OJO,
         al=_al('observo de 2019 a 2024', 'observado de 2019 a 2024', 'recupero de 2019 a 2024', 'recuperado de 2019 a 2024', 'en seis anos', 'en los seis anos', 'seis anos de revisiones'), ir=IRQ)
    # Los diez renglones con más por aclarar en 2024.
    sect = sorted(((x, gr['grupo']) for gr in Q['cp2024']['grupos'] for x in gr['sectores']), key=lambda z: -z[0]['porAclarar'])[:10]
    grupos['asfs'] = {'n': 'lo que quedó por aclarar en la Cuenta Pública 2024', 'tot': round(pa, 1), 'ir': IRQ,
                      'lista': 'Los diez renglones con más monto por aclarar en la Cuenta Pública 2024'}
    for x, gru in sect:
        fila(id='asfs-' + plano(x['nombre'] + ' ' + gru).replace(' ', '-')[:40], g='asfs', n='%s (%s)' % (limpio(x['nombre']), limpio(gru)), y='2024',
             v=round(x['porAclarar'] / 1e6, 1), e='oficial', fu=fq(Q['cp2024']['fuente'], '11 a 14'),
             fr='En la Cuenta Pública 2024, la ASF dejó {V} por aclarar en «%s», dentro de %s.' % (limpio(x['nombre']), limpio(gru).lower().replace('gasto federalizado', 'el gasto federalizado')),
             d='En el gasto federalizado la ASF agrupa por tema de fiscalización (educación, salud, participaciones…), no por dependencia. ' + OJO,
             al=_al('por aclarar de ' + x['nombre'], 'por aclarar en ' + x['nombre'], 'asf ' + x['nombre']) if gru != 'Gasto Federalizado' or 'Participaciones' in x['nombre'] else [], ir=IRQ)
    # Dónde se concentra lo por aclarar de 2024.
    grupos['asfg'] = {'n': 'lo que quedó por aclarar en la Cuenta Pública 2024', 'tot': round(pa, 1), 'ir': IRQ,
                      'lista': 'Lo que quedó por aclarar en la Cuenta Pública 2024, por grupo de gasto'}
    for gr in Q['cp2024']['grupos']:
        s = gr['subtotal']
        fila(id='asfg-' + plano(gr['grupo']).replace(' ', '-'), g='asfg', n=limpio(gr['grupo']), y='2024', v=round(s['porAclarar'] / 1e6, 1), e='oficial',
             fu=fq(Q['cp2024']['fuente'], Q['cp2024']['pagina']),
             fr='En la Cuenta Pública 2024, la ASF dejó {V} por aclarar en el grupo «%s», con %s auditorías.' % (limpio(gr['grupo']), _n(s['auditorias'])),
             d=OJO, al=_al('por aclarar en ' + gr['grupo'], 'asf ' + gr['grupo'], 'auditorias al ' + gr['grupo']), ir=IRQ)

    # ------------------------------------------------------------------
    # 5. El peso en el tiempo, tal como lo prepara el Radar.
    PS = radar['peso']
    FR = radar['fuentes']
    peso = {k: PS[k] for k in ('anios', 'inpc', 'infl', 'usd', 'eur', 'ref', 'hoy', 'eur_desde', 'eur_antes', 'proy', 'proy_obs', 'proy_eur', 'proy_aviso')}
    peso['f'] = {k: {'tx': FR[v]['corto'], 'url': FR[v].get('url')} for k, v in PS['f'].items()}
    peso['adm'] = {x['id']: {k: x[k] for k in ('rec', 'ent', 'curso', 'infl', 'cien', 'usd', 'eur') if k in x} for x in PS['admins']}
    peso['fx'] = {k: {'tx': v['corto'], 'url': v.get('url')} for k, v in FR.items() if k.startswith('BX_') or k == 'CGPE2027_MACRO'}
    peso['ir'] = {'maquina': 'radar-peso-maquina.html', 'monedas': 'radar-peso-monedas.html', 'sexenios': 'radar-peso-sexenios.html'}

    # ------------------------------------------------------------------
    # 6. Las bases que se descargan y los plazos de la ASF.
    js = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'auditor', 'js', 'datos.js'), encoding='utf-8').read()
    desc = [{'n': t, 'fu': limpio(f)} for t, f in re.findall(r"\{ id: '[^']+', titulo: '([^']+)',\s*fuente: '([^']+)'", js.split('const DESCARGAS')[1])]
    # Las leyes que aplican y quién mide cada dato (datos-ambiente-leyes y -quien-lo-mide).
    leyes = {'l': [{'n': limpio(x['norma']), 'd': limpio(x['dice']), 'fu': fu(x['norma'], x['refKey'])} for x in A['leyes']], 'ir': [AMB + 'leyes.html', 'Las leyes que aplican']}
    mide = {'l': [{'d': limpio(x['dato']), 'q': limpio(x['mide']), 'e': x['estado'], 'n': limpio(x['nota'])} for x in A['quienMide']],
            'falta': [limpio(x) for x in A['pendientes']], 'ir': [AMB + 'quien-lo-mide.html', 'Quién lo mide y de dónde sale']}
    plazos = {'l': [{'p': x['plazo'], 'q': limpio(x['que']), 'f': x['fundamento']} for x in Q['plazos']], 'fu': {'tx': FQ['LFRCF']['corto'], 'url': FQ['LFRCF']['url']}}
    return {'peso': peso, 'desc': desc, 'plazos': plazos, 'leyes': leyes, 'mide': mide}
