# -*- coding: utf-8 -*-
"""Quinta aplicacion del Modo Inspector: «Contrasta una nota» en pagina
propia (12-10-2026). Sustituye al marco que cargaba la portada entera.

Desde el 21-10-2026 (pedido del autor) lee la nota: el lector pega la liga
(o el texto), assets/auditor/js/insp-nota-lee.js la abre con un lector
externo, encuentra sus cifras en pesos, las empata con el catalogo por
palabras (claves()) y da un veredicto con el documento de cada una. Todo
en una sola pagina: el portal y, debajo, el veredicto. Si la nota no habla
de dinero publico (FISCAL), lo dice y no la califica.

El catalogo para elegir la cifra a mano y las frases de prueba se mudaron
a la aplicacion 1, Que encontro la ASF (catalogo_pagina(), que pinta
insp_asf.subpaginas() y maneja assets/auditor/js/insp-nota.js).

El catalogo de cifras contrastables se arma aqui desde la base con las
mismas reglas que vnCatalogo() del motor (audit-engine.js): mismas
colecciones, mismos identificadores, mismos estados. Los municipios no se
embeben: el padron EFIPEM ya vive aparte (assets/auditor/js/
municipios-efipem.js) y el catalogo lo carga al vuelo.

Regla de la plataforma (AGENTS.md, §2): nada se estima. Si la cifra de
referencia esta pendiente, el contraste no se hace; una cifra de la nota
sin documento con que compararla queda «sin contrastar», no se cuenta como
falsa.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['inspnota']). Lleva la
navegacion compacta (NAV_COMPACTA).
"""
import html
import json
import math

from presupuesto_modulos import chip, mdp

ESTILOS = ['insp-nota.css']
SCRIPTS = ['insp-nota-lee.js']
# Abajo, solo anterior, siguiente, las aplicaciones y el indice (pedido del
# autor, 21-10-2026: la navegacion grande «absorbe mucha parte de la pagina»).
NAV_COMPACTA = True

GRUPOS = [
    ('nacional', '🇲🇽', 'Nacional'),
    ('paquete', '📦', 'Paquete Económico 2027'),
    ('megaobras', '🚆', 'Megaobras'),
    ('federal', '🏛️', 'Dependencias federales'),
    ('estados', '🗺️', 'Estados'),
    ('municipios', '🏘️', 'Municipios'),
]


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def esc(t):
    return html.escape(str(t or ''), quote=True)


def catalogo(base):
    """Replica de vnCatalogo() sin los municipios."""
    refs = {r['id']: r.get('url', '') for r in base.get('referencias_legales', [])}
    out = []

    def add(**o):
        v = o.get('v')
        if v is None or not isinstance(v, (int, float)) or not math.isfinite(v):
            return
        out.append({k: x for k, x in o.items() if x not in (None, '')})

    rel = ((base.get('calculadora_civica') or {}).get('relojes') or {}).get('fuentes') or []
    for f in rel:
        if f['id'] in ('intereses', 'deuda-nueva'):
            add(id='rel-' + f['id'], g='nacional', n=f['nombre'], a='2026', v=f.get('anual_mdp'),
                e=f.get('estado'), f=f.get('fuente'), u=refs.get(f.get('refKey'), ''))

    asf = base.get('cuenta_publica_asf') or {}
    a24 = asf.get('cp2024')
    if a24:
        fa = asf['fuentes'].get(a24['fuente'], {})
        fu = (fa.get('doc') or 'ASF') + ', p. ' + str(a24['pagina'])
        add(id='asf-poraclarar', g='nacional', n='Monto por aclarar ante la ASF, Cuenta Pública 2024', a='2024',
            v=a24['total']['porAclarar'] / 1e6, e='oficial', f=fu, u=fa.get('url'))
        add(id='asf-recuperado', g='nacional', n='Recuperado por la ASF durante las auditorías, Cuenta Pública 2024', a='2024',
            v=a24['total']['recuperaciones'] / 1e6, e='oficial', f=fu, u=fa.get('url'))

    H = base.get('huachicol_fiscal')
    if H:
        add(id='ieps-comb-27', g='nacional', n='IEPS a combustibles automotrices estimado para 2027', a='2027',
            v=H['en_juego']['ieps_combustibles_2027_mdp'], e='oficial',
            f=H['fuentes']['ilif27']['doc'] + ', p. ' + str(H['en_juego']['pagina']), u=H['fuentes']['ilif27']['url'])

    pq = base.get('paquete_2027') or {}
    for f in pq.get('finanzas') or []:
        add(id='pq27-' + f['id'], g='paquete', n=f['n'] + ' (propuesta 2027)', a='2027', v=abs(f['m']), e='oficial',
            f='SHCP, Criterios Generales de Política Económica 2027', u=refs.get('ref-cgpe2027'),
            s='negativo' if f['m'] < 0 else '')
        if isinstance(f.get('m26'), (int, float)):
            add(id='pq26-' + f['id'], g='paquete', n=f['n'] + ' (aprobado 2026)', a='2026', v=abs(f['m26']), e='oficial',
                f='SHCP, Criterios Generales de Política Económica 2027 (columna 2026 aprobado)', u=refs.get('ref-cgpe2027'),
                s='negativo' if f['m26'] < 0 else '')

    sm = base.get('simulador_megaobras') or {}
    of, vf = sm.get('operacion_oficial'), sm.get('verificacion')
    if of:
        ob, fu = of['obras'], of['fuentes']
        tm, ai, fb = ob.get('tren-maya'), ob.get('aifa-texcoco'), ob.get('fobaproa')
        f1, f2, f3 = fu.get('ef_h0m'), fu.get('ef_hzi'), fu.get('ipab_ef')
        if tm:
            add(id='tm-ingresos', g='megaobras', n='Tren Maya S.A.: ingresos por sus servicios en 2024', a='2024', v=tm['ingresos_gestion'], e='oficial', f=f1['doc'], u=f1['url'])
            add(id='tm-gasto', g='megaobras', n='Tren Maya S.A.: gasto total en 2024', a='2024', v=tm['gastos_totales'], e='oficial', f=f1['doc'], u=f1['url'])
            add(id='tm-transf', g='megaobras', n='Tren Maya S.A.: transferencias federales recibidas en 2024', a='2024', v=tm['transferencias'], e='oficial', f=f1['doc'], u=f1['url'])
            add(id='tm-perdida', g='megaobras', n='Tren Maya S.A.: pérdida de operación en 2024 (sin transferencias)', a='2024',
                v=-tm['resultado_sin_transferencias'], e='derivado', f=f1['doc'] + ' (ingresos menos gasto total)', u=f1['url'],
                op='Ingresos por sus servicios (%s) menos gasto total (%s), del mismo estado de actividades.'
                   % (mdp(tm['ingresos_gestion']), mdp(tm['gastos_totales'])))
        bx = (of.get('contexto_entidad') or {}).get('megafarmacia')
        fb4 = bx and fu.get(bx['fuente'])
        if bx and fb4:
            add(id='birmex-resultado', g='megaobras', n='Birmex (opera la Megafarmacia): resultado del ejercicio 2024, toda la empresa', a='2024',
                v=bx['resultado_ejercicio'], e='oficial', f=fb4['doc'], u=fb4['url'])
        if ai:
            add(id='aifa-ingresos', g='megaobras', n='AIFA S.A.: ingresos por sus servicios en 2024', a='2024', v=ai['ingresos_gestion'], e='oficial', f=f2['doc'], u=f2['url'])
        if fb:
            add(id='ipab-saldo', g='megaobras', n='IPAB (FOBAPROA): deuda en bonos al 31 de diciembre de 2025', a='2025', v=fb['saldo_bonos_2025'], e='oficial', f=f3['doc'], u=f3['url'])
            add(id='ipab-r34', g='megaobras', n='Rescate bancario: Ramo 34 ejercido en 2024', a='2024', v=fb['ramo34_ejercido'], e='oficial',
                f='SHCP, Cuenta Pública 2024', u=((vf or {}).get('fuentes', {}).get('cp') or {}).get('url'))
            f5 = fu.get(fb.get('fuente_resultado'))
            if f5 and 'resultado_sin_transferencias' in fb:
                add(id='ipab-perdida', g='megaobras', n='Rescate bancario: lo que el Fondo FOBAPROA pierde en 2024 antes del apoyo del presupuesto',
                    a='2024', v=-fb['resultado_sin_transferencias'], e='derivado', f=f5['doc'], u=f5['url'],
                    op='Déficit del Fondo FOBAPROA en 2024 (%s) + Ramo 34 que recibió ese año (%s).'
                       % (format(-fb['deficit_ejercicio'], ',.1f'), format(fb['ramo34_ejercido'], ',.1f')))
    if vf and vf.get('obras'):
        vo, vfu = vf['obras'], vf['fuentes']
        t, to, na = vo.get('tren-maya'), vo.get('tren-toluca'), vo.get('aifa-texcoco')
        if t:
            add(id='tm-ejercido', g='megaobras', n='Tren Maya: ejercido de 2020 a 2025 bajo su clave de cartera', a='2020-2025',
                v=t.get('ejercidoTotal'), e='derivado', f=vfu['cp']['doc'] + ' (suma por año)', u=vfu['cp']['url'],
                op='Suma de lo ejercido cada año, de 2020 a 2025, bajo la clave de cartera del Tren Maya en la Cuenta Pública.')
        if to and to.get('cartera'):
            u = to['cartera'][-1]
            add(id='toluca-mti', g='megaobras', n='Tren Interurbano México-Toluca: monto total de inversión registrado (%s)' % u['corte'], a=u['corte'],
                v=u['mti'], e='oficial', f=vfu['opa']['doc'], u=vfu['opa']['url'])
        if na and na.get('naicm'):
            add(id='naicm', g='megaobras', n='Costo de cancelar el NAIM de Texcoco, según la ASF', a='2019', v=na['naicm']['costo'], e='oficial',
                f=vfu['asfnaicm']['doc'] + ', pp. ' + na['naicm']['paginas'], u=vfu['asfnaicm']['url'])

    IF = base.get('inspector_federal')
    if IF:
        for f in IF.get('entes') or []:
            if f.get('cp2025'):
                add(id='fed-cp-' + f['id'], g='federal', n=f['nombre'] + ': gasto ejercido en 2025', a='2025', v=f['cp2025']['ejercido'], e='oficial',
                    f=IF['fuentes']['cp2025']['corto'], u=IF['fuentes']['cp2025']['url'])
            if f.get('av2026'):
                add(id='fed-pef-' + f['id'], g='federal', n=f['nombre'] + ': presupuesto aprobado para 2026', a='2026', v=f['av2026']['aprobado'], e='oficial',
                    f=IF['fuentes']['av2026']['corto'], u=IF['fuentes']['av2026']['url'])

    FE = (base.get('fiscalEntidades') or {}).get('campos') or {}
    for e in base.get('estados') or []:
        c28, c33 = FE.get('ramo28') or {}, FE.get('ramo33') or {}
        add(id='est-r28-' + e['abbr'], g='estados', n=e['name'] + ': participaciones del Ramo 28 en 2026', a='2026', v=e.get('ramo28'),
            e=c28.get('estado') or 'pendiente', f=c28.get('fuente'), u=refs.get(c28.get('ref'), ''))
        add(id='est-r33-' + e['abbr'], g='estados', n=e['name'] + ': aportaciones del Ramo 33 en 2026', a='2026', v=e.get('ramo33'),
            e=c33.get('estado') or 'pendiente', f=c33.get('fuente'), u=refs.get(c33.get('ref'), ''))
        add(id='est-deuda-' + e['abbr'], g='estados', n=e['name'] + ': deuda pública del estado', a='2025', v=e.get('deuda'),
            e='oficial' if e.get('deudaFuente') else 'pendiente', f=e.get('deudaFuente') or 'Sin documento citado')
        add(id='est-asf-' + e['abbr'], g='estados', n=e['name'] + ': monto por aclarar ante la ASF (Cuenta Pública 2024)', a='2024',
            v=e.get('asfMontoObservado'), e='oficial' if e.get('asfFuente') else 'pendiente', f=e.get('asfFuente') or 'Sin documento citado')
    return out


def _bill(v):
    """Una cifra en mdp escrita como la daria una nota, con su unidad."""
    if v >= 1e6:
        return format(v / 1e6, '.2f'), 'billones'
    if v >= 1e3:
        return format(v / 1e3, '.1f'), 'milmillones'
    return format(v, ',.1f'), 'millones'


def ejemplos(cat):
    """Frases de prueba. No son notas reales: la cifra «de la nota» se
    escribe a partir de la oficial para que el lector vea cada veredicto."""
    by = {o['id']: o for o in cat}
    out = []
    o = by.get('rel-intereses')
    if o:
        n, u = _bill(o['v'])
        out.append({'id': o['id'], 'n': n, 'u': u, 'tipo': 'Coincide',
                    'frase': '«Este año el país pagará %s billones de pesos solo en intereses de la deuda.»' % n})
    o = by.get('tm-transf')
    if o:
        n = format(o['v'] / 1e3, '.1f')
        out.append({'id': o['id'], 'n': n, 'u': 'billones', 'tipo': 'Error de unidades',
                    'frase': '«El Tren Maya recibió %s billones de pesos en transferencias en 2024.» (traducción literal de «%s billion»)' % (n, n)})
    o = by.get('rel-deuda-nueva')
    if o:
        n = format(math.floor(o['v'] / 1e5) / 10, '.1f')
        out.append({'id': o['id'], 'n': n, 'u': 'billones', 'tipo': 'Se acerca',
                    'frase': '«Para 2026 se autorizó deuda nueva por %s billones.» (cifra truncada)' % n})
    o = by.get('asf-poraclarar')
    if o:
        n = format(round(o['v'] / 1e4, 1), '.1f')
        out.append({'id': o['id'], 'n': n, 'u': 'milmillones', 'tipo': 'No coincide',
                    'frase': '«La ASF dejó %s mil millones por aclarar en la Cuenta Pública 2024.» (un cero de menos)' % n})
    return out


UNIDADES = [('pesos', 'pesos'), ('miles', 'miles de pesos'), ('millones', 'millones de pesos (mdp)'),
            ('milmillones', 'miles de millones (mmdp)'), ('billones', 'billones (millones de millones)')]


def _item(o):
    signo = ' <span class="in-signo">en negativo</span>' if o.get('s') == 'negativo' else ''
    fuente = ('<a href="%s" target="_blank" rel="noopener">%s ↗</a>' % (esc(o['u']), esc(o.get('f') or 'documento'))
              if o.get('u') else esc(o.get('f')))
    return ('<li class="in-it" data-id="%s"><button type="button" class="in-elige" data-id="%s" aria-pressed="false">'
            '<span class="in-it-n">%s</span><span class="in-it-v"><b>%s</b>%s %s <small>%s</small></span></button>'
            '<span class="in-it-f">%s</span></li>'
            % (esc(o['id']), esc(o['id']), esc(o['n']), mdp(o['v']), signo, chip(o['e']), esc(o['a']), fuente))




# ------------------------------------------------------------------ lector
# Desde el 21-10-2026 (pedido del autor) Contrasta una nota lee la nota: el
# lector pega la liga (o el texto), la pagina la abre con un lector externo
# (r.jina.ai y, de respaldo, allorigins), encuentra sus cifras en pesos, las
# empata con el catalogo y da un veredicto con el documento de cada una. El
# empate es por palabras: una cifra solo se contrasta si la oracion nombra
# a quien gasta o recibe (la entidad) y lo que se mide (el concepto). Si no,
# queda «sin cifra oficial para contrastar»: no se adivina ni se cuenta como
# falsa. Cada grupo de «k» es una lista de alternativas; deben aparecer
# todos los grupos. «x» son frases que se borran antes de buscar (para que
# «Baja California Sur» no cuente como «Baja California»).
FED_ALIAS = {
    'legislativo': ['poder legislativo', 'congreso de la union'],
    'judicial': ['poder judicial'],
    'presidencia': ['oficina de la presidencia', 'presidencia de la republica'],
    'gobernacion': ['gobernacion', 'segob'],
    'sre': ['relaciones exteriores', 'cancilleria', 'sre'],
    'shcp': ['hacienda y credito publico', 'secretaria de hacienda', 'shcp'],
    'defensa': ['defensa nacional', 'secretaria de la defensa', 'sedena'],
    'agricultura': ['agricultura y desarrollo rural', 'secretaria de agricultura', 'sader'],
    'sict': ['infraestructura, comunicaciones y transportes', 'comunicaciones y transportes', 'sict', 'sct'],
    'economia': ['secretaria de economia'],
    'sep': ['educacion publica', 'sep'],
    'salud': ['secretaria de salud', 'ssa'],
    'marina': ['secretaria de marina', 'semar'],
    'stps': ['trabajo y prevision social', 'secretaria del trabajo', 'stps'],
    'sedatu': ['desarrollo agrario, territorial y urbano', 'sedatu'],
    'semarnat': ['medio ambiente y recursos naturales', 'semarnat'],
    'energia': ['secretaria de energia', 'sener'],
    'bienestar': ['secretaria de bienestar', 'secretaria del bienestar'],
    'turismo': ['secretaria de turismo', 'sectur'],
    'ine': ['instituto nacional electoral', 'ine'],
    'anticorrupcion': ['anticorrupcion y buen gobierno', 'secretaria anticorrupcion'],
    'tribunales-agrarios': ['tribunales agrarios', 'tribunal superior agrario'],
    'tfja': ['justicia administrativa', 'tfja'],
    'cndh': ['comision nacional de los derechos humanos', 'cndh'],
    'sspc': ['seguridad y proteccion ciudadana', 'sspc'],
    'cjef': ['consejeria juridica'],
    'secihti': ['ciencia, humanidades', 'secihti'],
    'inegi': ['inegi', 'instituto nacional de estadistica'],
    'cofece': ['competencia economica', 'cofece'],
    'ift': ['instituto federal de telecomunicaciones', 'ift'],
    'inai': ['instituto nacional de transparencia', 'inai'],
    'cre': ['comision reguladora de energia', 'cre'],
    'cnh': ['comision nacional de hidrocarburos', 'cnh'],
    'cultura': ['secretaria de cultura'],
    'fgr': ['fiscalia general de la republica', 'fgr'],
    'imss': ['seguro social', 'imss'],
    'issste': ['issste'],
    'pemex': ['petroleos mexicanos', 'pemex'],
    'cfe': ['comision federal de electricidad', 'cfe'],
    'mujeres': ['secretaria de las mujeres'],
    'atdt': ['transformacion digital', 'atdt'],
}
FED_EXCLUYE = {'imss': ['imss-bienestar', 'imss bienestar'], 'cultura': [], 'ine': []}
ESTADO_ALIAS = {'CDMX': ['ciudad de mexico', 'cdmx'], 'MÉX': ['estado de mexico', 'edomex'],
                'BC': ['baja california'], 'QROO': ['quintana roo'], 'SLP': ['san luis potosi'],
                'COAH': ['coahuila'], 'MICH': ['michoacan'], 'VER': ['veracruz']}
ESTADO_EXCLUYE = {'BC': ['baja california sur']}
PQ = {
    'rfsp': [['rfsp', 'requerimientos financieros']],
    'balance': [['balance presupuestario', 'deficit presupuestario']],
    'extra': [['fuera del presupuesto']],
    'primario': [['superavit primario', 'balance primario']],
    'ing': [['ingresos presupuestarios', 'ingresos del sector publico', 'ingresos totales']],
    'trib': [['ingresos tributarios', 'recaudacion tributaria', 'recaudacion']],
    'petro': [['ingresos petroleros']],
    'gasto': [['gasto neto', 'gasto total', 'gasto publico total']],
    'prog': [['gasto programable']],
    'noprog': [['no programable']],
    'costofin': [['costo financiero', 'interes']],
    'defer': [['diferimiento de pagos', 'adefas']],
    'shrfsp': [['shrfsp', 'saldo historico', 'deuda publica total', 'deuda total', 'deuda publica']],
}
FIJAS = {
    'rel-intereses': [['interes', 'costo financiero'], ['deuda']],
    'rel-deuda-nueva': [['deuda nueva', 'endeudamiento', 'nueva deuda', 'financiamiento']],
    'asf-poraclarar': [['asf', 'auditoria superior'], ['aclarar', 'observ']],
    'asf-recuperado': [['asf', 'auditoria superior'], ['recuper', 'reintegr']],
    'ieps-comb-27': [['ieps'], ['combustible', 'gasolina', 'diesel']],
    'tm-ingresos': [['tren maya'], ['ingres', 'venta', 'boleto']],
    'tm-gasto': [['tren maya'], ['gasto de operacion', 'gasto total', 'gastos', 'gasto']],
    'tm-transf': [['tren maya'], ['transferencia', 'subsidi']],
    'tm-perdida': [['tren maya'], ['perdi', 'deficit', 'numeros rojos']],
    'tm-ejercido': [['tren maya'], ['cost', 'invers', 'ejerci', 'gastad']],
    'birmex-resultado': [['birmex', 'megafarmacia'], ['resultado', 'perdi', 'deficit']],
    'aifa-ingresos': [['aifa', 'aeropuerto internacional felipe angeles', 'aeropuerto felipe angeles'], ['ingres']],
    'ipab-saldo': [['ipab', 'fobaproa', 'rescate bancario'], ['deuda', 'bonos', 'saldo', 'pasivo']],
    'ipab-r34': [['ramo 34', 'ipab', 'fobaproa', 'rescate bancario'], ['ramo 34', 'presupuesto', 'pag', 'transfer', 'apoyo']],
    'ipab-perdida': [['fobaproa', 'ipab'], ['perdi', 'pierde', 'deficit']],
    'toluca-mti': [['tren interurbano', 'mexico-toluca', 'mexico toluca', 'el insurgente'], ['cost', 'invers', 'invert']],
    'naicm': [['naim', 'naicm', 'texcoco'], ['cancel']],
}


def _plano(t):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', t.lower()) if unicodedata.category(c) != 'Mn')


def claves(o, base):
    """Las palabras con que el lector empata una cifra de la nota con este
    renglon del catalogo. Sin claves, el renglon no se empata solo."""
    i = o['id']
    if i in FIJAS:
        return {'k': FIJAS[i]}
    if i.startswith(('pq27-', 'pq26-')):
        k = PQ.get(i[5:].replace('f-', ''))
        if not k:
            return None
        return {'k': k, 'b': ['propuesta', 'proyecto', 'paquete economico', 'propone', 'para 2027'] if i.startswith('pq27') else ['aprobad', 'para 2026']}
    if i.startswith(('fed-cp-', 'fed-pef-')):
        ente = i.split('-', 2)[2]
        ali = FED_ALIAS.get(ente)
        if not ali:
            return None
        concepto = ['ejerci', 'gast', 'erog'] if i.startswith('fed-cp-') else ['presupuesto', 'aprob', 'asign', 'recibira', 'contara']
        return {'k': [ali, concepto], 'x': FED_EXCLUYE.get(ente) or None}
    if i.startswith('est-'):
        _, que, ab = i.split('-', 2)
        nombre = next((e['name'] for e in base.get('estados') or [] if e['abbr'] == ab), '')
        ali = ESTADO_ALIAS.get(ab) or [_plano(nombre)]
        concepto = {'r28': ['participaciones', 'ramo 28'], 'r33': ['aportaciones', 'ramo 33'],
                    'deuda': ['deuda', 'endeud', 'pasivo']}.get(que)
        k = [ali, concepto] if concepto else [ali, ['asf', 'auditoria superior'], ['aclarar', 'observ']]
        return {'k': k, 'x': ESTADO_EXCLUYE.get(ab)}
    return None


def catalogo_lector(base):
    out = []
    for o in catalogo(base):
        c = claves(o, base)
        if c:
            out.append(dict(o, **{k: v for k, v in c.items() if v}))
    return out


PAGINA = 'herramienta-inspector-nota.html'
# El catalogo para elegir la cifra a mano y las frases de prueba se mudaron
# a la aplicacion 1 (Que encontro la ASF), en su propia pagina (pedido del
# autor, 21-10-2026): no se borro ni se depuro nada.
CATALOGO = 'herramienta-inspector-asf-catalogo.html'
# Los tres pasos tuvieron pagina propia el 21-10-2026; ese mismo dia el
# autor pidio juntarlos en una sola: pegas la nota y ahi mismo sale el
# veredicto. Las paginas viejas redirigen aqui (apartados.REDIRECCIONES),
# con su ?liga= intacta, para no romper los veredictos compartidos.
PASOS_VIEJOS = ['liga', 'cifras', 'veredicto']

# Palabras de finanzas publicas: deciden si la nota «se identifica dentro de
# los supuestos de la plataforma» (pedido del autor, 21-10-2026). Peso 2 a
# las que por si solas son del tema; 1 a las que necesitan compania. Hace
# falta sumar 2.
FISCAL = {
    2: ['presupuesto de egresos', 'presupuesto federal', 'presupuesto publico', 'gasto publico', 'dinero publico',
        'recursos publicos', 'erario', 'hacienda', 'shcp', 'cuenta publica', 'auditoria superior', 'asf',
        'deuda publica', 'endeudamiento', 'ley de ingresos', 'paquete economico', 'finanzas publicas', 'recaudacion',
        'sat', 'isr', 'iva', 'ieps', 'participaciones federales', 'aportaciones federales', 'ramo 28', 'ramo 33',
        'licitacion', 'adjudicacion directa', 'adjudico', 'sobrecosto', 'subejercicio', 'peculado', 'desvio de recursos',
        'facturas falsas', 'empresas fantasma', 'costo financiero', 'deficit', 'rfsp', 'pef', 'banxico',
        'tren maya', 'dos bocas', 'refineria olmeca', 'aifa', 'megafarmacia', 'birmex', 'ipab', 'fonden'],
    1: ['presupuesto', 'gasto', 'deuda', 'impuesto', 'contribuyente', 'pemex', 'cfe', 'subsidio', 'contrato',
        'licita', 'gobierno federal', 'secretaria de', 'dependencia', 'municipio', 'gobierno del estado', 'congreso',
        'diputados', 'senado', 'programa social', 'pension', 'obra publica', 'megaobra', 'transparencia', 'auditoria',
        'corrupcion', 'fiscal', 'tesoreria', 'intereses', 'credito', 'bono', 'inversion publica'],
}

# Lo que la plataforma ya tiene de cada tema: se ofrece debajo del
# veredicto, haya o no cifras que contrastar.
TEMAS = [
    (['tren maya'], 'auditoria-tren-maya.html', 'Tren Maya', 'Auditoría en imágenes'),
    (['dos bocas', 'refineria olmeca', 'olmeca'], 'auditoria-dos-bocas.html', 'Refinería Olmeca (Dos Bocas)', 'Auditoría en imágenes'),
    (['aifa', 'felipe angeles'], 'auditoria-aifa.html', 'AIFA', 'Auditoría en imágenes'),
    (['tren interurbano', 'insurgente', 'mexico-toluca', 'mexico toluca'], 'auditoria-tren-toluca.html', 'Tren México-Toluca', 'Auditoría en imágenes'),
    (['megafarmacia', 'birmex'], 'auditoria-megafarmacia.html', 'Megafarmacia del Bienestar', 'Auditoría en imágenes'),
    (['huachicol'], 'auditoria-huachicol-fiscal.html', 'Huachicol fiscal', 'Auditoría en imágenes'),
    (['lego', 'cienega de flores'], 'auditoria-lego-cienega.html', 'Ciénega de Flores y LEGO', 'Auditoría en imágenes'),
    (['intereses', 'costo financiero'], 'numeros-egreso-costo-financiero.html', 'Costo financiero de la deuda', 'Números'),
    (['deuda', 'endeudamiento', 'rfsp'], 'numeros-la-deuda.html', 'La deuda: se paga lo que se debe', 'Números'),
    (['paquete economico', '2027'], 'numeros-paquete-2027.html', 'Paquete Económico 2027', 'Números'),
    (['aprobado', 'ejercido', 'modificado', 'subejercicio'], 'numeros-gasto-tres-presupuestos.html', 'Los tres presupuestos', 'Números'),
    (['presupuesto de egresos', 'pef', 'gasto publico'], 'numeros-presupuesto.html', 'El presupuesto', 'Números'),
    (['isr', 'impuesto sobre la renta'], 'numeros-ingreso-isr.html', 'ISR', 'Números'),
    (['iva', 'impuesto al valor agregado'], 'numeros-ingreso-iva.html', 'IVA', 'Números'),
    (['ieps', 'gasolina'], 'numeros-ingreso-ieps.html', 'IEPS', 'Números'),
    (['participaciones', 'ramo 28'], 'numeros-egreso-participaciones.html', 'Participaciones (Ramo 28)', 'Números'),
    (['aportaciones', 'ramo 33'], 'auditoria-ramo-33.html', 'Ramo 33', 'Auditoría en imágenes'),
    (['gobierno del estado', 'gobernador', 'gobernadora', 'entidad federativa', 'estatal'], 'numeros-las-32-entidades.html', 'Las 32 entidades', 'Números'),
    (['municipio', 'alcaldia', 'ayuntamiento', 'predial'], 'numeros-los-municipios.html', 'Los 2,479 municipios', 'Números'),
    (['asf', 'auditoria superior', 'cuenta publica', 'por aclarar'], 'herramienta-inspector-asf.html', 'Qué encontró la ASF', 'Modo Inspector'),
    (['efos', 'facturas falsas', 'empresas fantasma', '69-b', 'factureras'], 'herramienta-inspector-efos.html', 'Lista negra del SAT', 'Modo Inspector'),
    (['congreso', 'diputados', 'senado', 'poder judicial', 'suprema corte', 'judicatura'], 'numeros-lo-que-cuestan-los-poderes.html', 'Lo que cuestan el Congreso y la Judicatura', 'Números'),
    (['megaobra', 'obra publica', 'sobrecosto'], 'herramienta-megaobras.html', 'Inversión y Megaobras', 'Herramientas'),
]


def paso_archivo(slug):
    return PAGINA[:-5] + '-' + slug + '.html'


def _aviso(ref):
    return '''  <details class="in-aviso">
    <summary>Cómo leemos la nota y qué califica el veredicto</summary>
    <p><b>Cómo la leemos.</b> Un sitio sin servidor no puede abrir páginas de otros, así que la liga pasa por un lector externo gratuito: <a href="https://jina.ai/reader/" target="_blank" rel="noopener">r.jina.ai ↗</a> y, si falla, <a href="https://allorigins.win/" target="_blank" rel="noopener">allorigins ↗</a>. Ellos abren la nota y nos devuelven el texto; no guardamos la liga ni el texto en ningún servidor nuestro. Si prefieres que la liga no salga de tu navegador, pega el texto. De un video leemos el título y la descripción, no lo que se dice en él: para eso, pega su transcripción.</p>
    <p><b>Qué califica.</b> Las cifras en pesos de la nota frente a los documentos oficiales que tenemos, no al medio ni a quien la escribió. Una cifra sin documento con qué compararla queda «sin contrastar»: no la contamos como falsa. El empate entre la nota y el documento lo hace la página por las palabras de cada oración; puedes cambiarlo en cada cifra. Si la nota no habla de dinero público, te lo decimos y no la calificamos.</p>
    <p><b>De dónde salen las cifras.</b> De los documentos de la SHCP {r_pef} {r_lif} {r_cgpe}, la ASF, la Cuenta Pública y el INEGI; cada una lleva su enlace. Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>. Lo que todavía nos deben las dependencias está en el <a href="pendientes.html">Registro de pendientes</a>. ¿Prefieres elegir tú la cifra? Está el <a href="{cat}">catálogo de cifras oficiales</a>, en Qué encontró la ASF.</p>
  </details>'''.format(r_pef=ref('ref-pef2026'), r_lif=ref('ref-lif2026'), r_cgpe=ref('ref-cgpe2027'), cat=CATALOGO)


def _temas():
    import os
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for _p, href, _t, _s in TEMAS:
        if not os.path.exists(os.path.join(raiz, href)):
            raise SystemExit('insp_nota.TEMAS: no existe %s' % href)
    return [{'k': p, 'h': h, 't': t, 's': s} for p, h, t, s in TEMAS]


def _datos_lector(base):
    datos = {'cat': catalogo_lector(base), 'catalogo': CATALOGO, 'pagina': PAGINA,
             'fiscal': FISCAL, 'temas': _temas()}
    return '  <script type="application/json" id="inDatos">%s</script>' % _json(datos)


TIPS = '''    <ul class="in-tips">
      <li data-tip="anio"><b>El año.</b> Una cifra de 2025 no es la de 2026. El catálogo dice el año de cada cifra; la nota a veces no.</li>
      <li data-tip="etapa"><b>Aprobado, modificado o ejercido.</b> El presupuesto aprobado es lo que se planea; el ejercido, lo que se gastó. Pueden diferir bastante. <a href="numeros-gasto-tres-presupuestos.html">Los tres presupuestos</a>.</li>
      <li data-tip="real"><b>Nominal o real.</b> Si la nota habla «a precios de» otro año, ajustó por inflación y no tiene por qué coincidir con el documento, que da pesos corrientes.</li>
      <li data-tip="unidad"><b>La unidad.</b> mdp son millones de pesos; mmdp, miles de millones. En español un billón es un millón de millones; el «billion» del inglés son mil millones. <a href="numeros-cuanto-dinero-es.html">¿Cuánto dinero es?</a></li>
      <li data-tip="signo"><b>El signo.</b> Los balances y el déficit se publican en negativo. Aquí los comparamos en valor absoluto y te avisamos.</li>
      <li data-tip="concepto"><b>El concepto.</b> Total o una parte, bruto o neto, la empresa entera o solo un proyecto: un nombre parecido puede medir otra cosa. <a href="numeros-lo-que-la-cifra-no-dice.html">Lo que la cifra no dice</a>.</li>
    </ul>'''


def construir(base, ref):
    """La aplicacion entera en una pagina (pedido del autor, 21-10-2026):
    el portal donde se pega la nota y, debajo, el veredicto."""
    total = format(len(catalogo(base)), ',')
    return '\n\n'.join([
        '<div class="in in-portal" id="inRaiz" data-paso="portal">',
        '''  <section class="in-caja" aria-labelledby="inArrTit">
    <p class="in-kicker">Verificador de notas</p>
    <h2 class="in-grande" id="inArrTit">¿Lo que dice la nota es cierto?</h2>
    <p class="in-txt">Pega la liga de una noticia, una revista, un blog, un video o una publicación en redes. Leemos la nota, encontramos sus cifras y las ponemos junto a <b>{total} cifras oficiales</b>, cada una con su documento.</p>
    <div class="in-modos" role="tablist" aria-label="Cómo nos das la nota">
      <button type="button" class="in-modo" role="tab" id="inTabLiga" aria-selected="true" aria-controls="inFormLiga">Pegar la liga</button>
      <button type="button" class="in-modo" role="tab" id="inTabTexto" aria-selected="false" aria-controls="inFormTexto" tabindex="-1">Pegar el texto</button>
    </div>
    <form class="in-lee" id="inFormLiga" role="tabpanel" aria-labelledby="inTabLiga" novalidate>
      <label class="in-campo" for="inUrl"><span class="in-sr">Liga de la nota</span>
        <span class="in-fila"><input type="url" id="inUrl" class="in-input" placeholder="https://… la liga de la nota" autocomplete="off" inputmode="url"><button type="submit" class="in-boton" id="inLeer"><span aria-hidden="true">⚖️</span> Verificar</button></span></label>
    </form>
    <form class="in-lee" id="inFormTexto" role="tabpanel" aria-labelledby="inTabTexto" novalidate hidden>
      <label class="in-campo" for="inTexto"><span>Copia el texto de la nota, la publicación o la transcripción del video y pégalo aquí.</span>
        <textarea id="inTexto" class="in-input in-area" rows="6" placeholder="Pega aquí el texto…"></textarea></label>
      <label class="in-campo" for="inUrlTexto"><span>Liga de donde lo copiaste <small>(opcional, para citar la fuente)</small></span>
        <input type="url" id="inUrlTexto" class="in-input" placeholder="https://…" autocomplete="off" inputmode="url"></label>
      <button type="submit" class="in-boton" id="inAnalizar"><span aria-hidden="true">⚖️</span> Verificar este texto</button>
    </form>
    <p class="in-estado" id="inEstado" role="status" aria-live="polite"></p>
    <ol class="in-como" aria-label="Cómo funciona">
      <li><span class="in-n">1</span> Leemos la nota</li>
      <li><span class="in-n">2</span> Encontramos sus cifras</li>
      <li><span class="in-n">3</span> Las contrastamos con el documento</li>
    </ol>
  </section>'''.format(total=total),
        '''  <section class="in-resultado" id="inResultado" aria-labelledby="inResTit" hidden>
    <h2 class="in-sr" id="inResTit">El veredicto</h2>
    <div class="in-cab-nota" id="inCabNota"></div>
    <div id="inVeredicto"></div>
    <details class="in-revisa" id="inRevisa">
      <summary>Antes de concluir, revisa</summary>
''' + TIPS + '''
    </details>
  </section>''',
        _aviso(ref), _datos_lector(base)]) + '\n</div>'


# ------------------------------------------------- catalogo (aplicacion 1)
def _ejemplos(ejs):
    from urllib.parse import urlencode
    botones = '\n'.join(
        '<a class="in-ej" href="%s?%s#inResultado"><span class="in-ej-tipo">%s</span><span class="in-ej-fr">%s</span></a>'
        % (CATALOGO, esc(urlencode({'id': e['id'], 'n': e['n'], 'u': e['u'], 'ver': '1'})), esc(e['tipo']), esc(e['frase']))
        for e in ejs)
    return '''  <section class="in-ejemplos" aria-labelledby="inEjTit">
    <h2 class="in-tit" id="inEjTit"><span aria-hidden="true">🧪</span> Pruébala sin escribir</h2>
    <p class="in-txt">Frases de prueba, <b>no son notas reales</b>: cada una lleva a un veredicto distinto para que veas cómo se lee el resultado.</p>
    <div class="in-ejs">
{0}
    </div>
  </section>'''.format(botones)


def _catalogo_html(cat):
    cuenta = {g: sum(1 for o in cat if o['g'] == g) for g, _, _ in GRUPOS}
    filtros = ['<button type="button" class="in-filtro" data-g="" aria-pressed="true">Todas</button>']
    for g, ico, nom in GRUPOS:
        filtros.append('<button type="button" class="in-filtro" data-g="%s" aria-pressed="false"><span aria-hidden="true">%s</span> %s%s</button>'
                       % (g, ico, nom, (' <small>%d</small>' % cuenta[g]) if cuenta[g] else ''))
    grupos = []
    for g, ico, nom in GRUPOS:
        if g == 'municipios':
            grupos.append(
                '<details class="in-grupo" data-g="municipios"><summary><span aria-hidden="true">%s</span> %s</summary>\n'
                '<p class="in-muni-tx" id="inMuniTx">Los ingresos totales de 2024 de cada municipio, del padrón del INEGI (EFIPEM, cifras definitivas). '
                'Son más de dos mil: escribe el nombre del municipio en el buscador y los cargamos en ese momento.</p>\n'
                '<ul class="in-items" id="inMuniLista"></ul></details>' % (ico, nom))
            continue
        items = [o for o in cat if o['g'] == g]
        grupos.append('<details class="in-grupo" data-g="%s"%s><summary><span aria-hidden="true">%s</span> %s <small>%d cifras</small></summary>\n'
                      '<ul class="in-items">\n%s\n</ul></details>'
                      % (g, ' open' if g == 'nacional' else '', ico, nom, len(items), '\n'.join(_item(o) for o in items)))
    return '\n      '.join(filtros), '\n'.join(grupos)


def catalogo_pagina(base, ref):
    """La pagina del catalogo, hija de Que encontro la ASF: elegir a mano
    la cifra oficial, escribir lo que dice la nota y medir la diferencia,
    con las frases de prueba. Es la version anterior de Contrasta una nota
    (12-10-2026), tal cual; la maneja assets/auditor/js/insp-nota.js."""
    cat = catalogo(base)
    ejs = ejemplos(cat)
    filtros, grupos = _catalogo_html(cat)
    unidades = ''.join('<option value="%s"%s>%s</option>' % (u, ' selected' if u == 'millones' else '', et) for u, et in UNIDADES)
    datos = {'cat': cat, 'ejemplos': ejs, 'grupos': {g: nom for g, _, nom in GRUPOS},
             'estados': {e['abbr']: e['name'] for e in base.get('estados') or []},
             'pasos': {'cifra': CATALOGO + '#inPaso2', 'contraste': CATALOGO + '#inPaso3'}}
    return '''<div class="in" id="inRaiz" data-paso="manual">
  <nav class="in-subnav" aria-label="De dónde viene esta página">
    <a class="in-subnav-volver" href="herramienta-inspector-asf.html#ia-catalogo"><span aria-hidden="true">←</span> Volver a Qué encontró la ASF</a>
  </nav>
  <section class="in-arranque" aria-labelledby="inArrTit">
    <p class="in-kicker">Qué encontró la ASF · catálogo</p>
    <h2 class="in-grande" id="inArrTit">{total} cifras oficiales, cada una con su documento.</h2>
    <p class="in-txt">Más los ingresos de cada municipio del INEGI. Elige una, escribe la cifra que leíste en una nota y mide cuánto se aleja. Si tienes la liga de la nota, <a href="{nota}">Contrasta una nota</a> la lee por ti y encuentra sus cifras.</p>
  </section>

{ejs}

  <section class="in-paso" id="inPaso2" aria-labelledby="inP2Tit">
    <h2 class="in-tit" id="inP2Tit"><span class="in-n">1</span> Elige la cifra oficial</h2>
    <label class="in-campo" for="inBuscar"><span>Busca el concepto, el estado, el municipio o la dependencia</span>
      <input type="search" id="inBuscar" class="in-input" placeholder="Ej.: intereses deuda, Jalisco deuda, Tren Maya, Monterrey" autocomplete="off"></label>
    <div class="in-filtros" role="group" aria-label="Categorías">
      {filtros}
    </div>
    <p class="in-cuenta" id="inCuenta" aria-live="polite"></p>
    <div class="in-catalogo" id="inCatalogo">
{grupos}
    </div>
  </section>

  <section class="in-paso" id="inPaso3" aria-labelledby="inP3Tit">
    <h2 class="in-tit" id="inP3Tit"><span class="in-n">2</span> Lo que dice la nota</h2>
    <div class="in-elegida" id="inElegida" aria-live="polite" hidden></div>
    <p class="in-falta" id="inFalta">Todavía no eliges contra qué cifra oficial contrastar: tócala en el catálogo de arriba.</p>
    <div class="in-cifra">
      <label class="in-campo" for="inCifra"><span>La cifra, como la da la nota. Puedes escribir «1.5 billones» o «300 mil millones».</span>
        <input type="text" id="inCifra" class="in-input in-input-num" placeholder="Ej.: 1.6 billones" autocomplete="off" inputmode="text"></label>
      <label class="in-campo" for="inUnidad"><span>Unidad</span>
        <select id="inUnidad" class="in-input">{unidades}</select></label>
    </div>
    <p class="in-lectura" id="inLectura" aria-live="polite"></p>
    <button type="button" class="in-boton" id="inContrastar"><span aria-hidden="true">⚖️</span> Contrastar con el documento</button>
  </section>

  <section class="in-resultado" id="inResultado" aria-live="polite" aria-labelledby="inResTit">
    <h2 class="in-tit" id="inResTit"><span aria-hidden="true">📏</span> El contraste</h2>
    <p class="in-vacio" id="inVacio">Aquí aparecerá el medidor cuando elijas una cifra oficial y escribas lo que dice la nota.</p>
    <div id="inSalida"></div>
  </section>

{tips}

  <aside class="in-aviso">
    <p>Las cifras salen de los documentos de la SHCP {r_pef} {r_lif} {r_cgpe}, la ASF, la Cuenta Pública y el INEGI; cada una lleva su enlace. Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>. Lo que todavía nos deben las dependencias está en el <a href="pendientes.html">Registro de pendientes</a>.</p>
  </aside>
  <script type="application/json" id="inDatos">{datos}</script>
</div>'''.format(total=format(len(cat), ','), nota=PAGINA, ejs=_ejemplos(ejs), filtros=filtros, grupos=grupos,
                 unidades=unidades, tips=TIPS, datos=_json(datos),
                 r_pef=ref('ref-pef2026'), r_lif=ref('ref-lif2026'), r_cgpe=ref('ref-cgpe2027'))
