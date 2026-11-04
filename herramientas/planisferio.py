# -*- coding: utf-8 -*-
"""El Planisferio: México en un mapa, por dimensiones (pedido del autor,
02-11-2026: «un mapa grande de México interactivo con sus diferentes
dimensiones… al momento que le demos clic a las entidades nos lleve a su
respectiva [información]»).

Es la segunda pestaña, después del Auditor. No trae datos nuevos: ordena en
el territorio lo que la Enciclopedia ya tiene cotejado. Ninguna cifra se
escribe aquí; todas se leen de window.AUDIT_DB (estados, fiscalEntidades,
panoramaErario) y del padrón municipal del INEGI (municipios-efipem.js).

Primera entrega: la dimensión financiera, los tres presupuestos de cada
entidad, uno por cada piso de la hacienda:

  1. Lo que baja de la Federación (Ramos 28 y 33 de 2026, acuerdo de
     distribución publicado en el DOF).
  2. Lo que el gobierno del estado cobra por su cuenta (INEGI, 2024).
  3. Lo que ingresaron sus municipios (INEGI, 2024, suma del padrón).

Arriba van los contadores de la Enciclopedia: los tres presupuestos de la
Federación (del Estado, nacional y social), el gasto federalizado y la bolsa
municipal, con su ritmo por segundo (cifra anual ÷ 31,536,000 s: derivado,
nunca dinero que se mueve en tiempo real).

Cada entidad tiene su portal (planisferio-<clave>.html) con sus tres
presupuestos, su ritmo, sus municipios uno por uno y la puerta a las otras
dimensiones. Ya se pintan las seis: financiera, deuda, inversión, ambiental
(por ahora, las refinerías de PEMEX: recursos_naturales.py), legislativa y
judicial. Un enlace roto detiene la generación.

Lo usa apartados.generar(); lo interactivo vive en planisferio.js.
"""
import html
import json
import os
import subprocess
import unicodedata
from urllib.parse import quote

import territorio_modulos as tm
from presupuesto_modulos import chip, mdp, bill, pct

ARCHIVO = 'planisferio.html'
SEG_ANIO = 31536000
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (id, icono, nombre, qué trae, dónde vive ya en la Enciclopedia, con su
# estado: %s recibe la clave de la entidad; si ya se pinta en el mapa).
DIMENSIONES = [
    ('financiera', '💰', 'Financiera',
     'Los tres presupuestos de cada entidad: lo que baja de la Federación, lo que cobra el estado y lo que ingresan sus municipios.',
     None, None, True),
    ('deuda', '🏦', 'Deuda',
     'Lo que debe cada gobierno estatal según el Sistema de Alertas de Hacienda, con sus tres indicadores y su semáforo.',
     'numeros-mapa-del-gasto-federalizado.html?l=deuda', 'numeros-mapa-del-gasto-federalizado.html?l=deuda&e=%s', True),
    ('inversion', '🏗️', 'Inversión',
     'La obra que hace cada gobierno estatal, directa o por medio de sus organismos, y lo que la ASF dejó por aclarar del dinero federal que recibió.',
     'numeros-mapa-del-gasto-federalizado.html?l=inv', 'numeros-mapa-del-gasto-federalizado.html?l=inv&e=%s', True),
    ('ambiental', '🌎', 'Ambiental',
     'Los recursos naturales y quién los explota: los acuíferos de cada estado y cuántos ya no tienen agua para concesionar, su superficie forestal y sus incendios, sus concesiones mineras y las siete refinerías de PEMEX.',
     'aprende-recursos-naturales.html#rn-agua', None, True),
    ('legislativa', '🏛️', 'Legislativa',
     'Los 32 congresos locales: lo que gastó cada uno, cuántas personas legisladoras lo integran y cómo se compara con el tope de la Constitución.',
     'datos-poder-legislativo.html', 'radar-estado-de-cuenta.html?doc=%s', True),
    ('judicial', '⚖️', 'Judicial',
     'Los 32 poderes judiciales de los estados: lo que ejerció cada uno, lo que le llegó y lo que concluyó, cuánto le costó cada asunto y las causas penales que se le acumulan.',
     'datos-judicial-gestion.html#jud-gestion_estados', None, True),
    ('salud', '🩺', 'Salud pública',
     'El IMSS y el ISSSTE en cada estado: cuántas personas tiene adscritas el IMSS, cuántas consultas y cirugías les dio y con cuántas camas, y con cuántos médicos, camas y unidades cuenta el ISSSTE.',
     'datos-salud-sistema.html#sal-estados', None, True),
    ('social', '🫂', 'Social',
     'La pobreza en cada estado, medida por el INEGI: cuántas personas la viven, cuántas en pobreza extrema, cuántas no alcanzan a cubrir sus necesidades con su ingreso '
     'y qué carencias pesan más, junto a lo que la Federación le aporta al estado por persona en pobreza.',
     'contexto-dimensional-social.html', None, True),
    ('administracion', '🏢', 'Administración pública',
     'El gobierno que ejecuta, en los tres niveles: cuánta gente tiene la administración de cada estado, cuánto ejerció, cuántos contratos dio sin concurso, '
     'cuánto ejercieron sus municipios y qué les dejó por aclarar la Auditoría Superior de la Federación.',
     'datos-administracion-publica-niveles.html#adm-estados', None, True),
]


def clave(a):
    """MÉX → mex: la clave del archivo, sin acentos."""
    return unicodedata.normalize('NFKD', a).encode('ascii', 'ignore').decode().lower()


_DL = {}


def _congresos(base):
    """El documento del congreso local de cada entidad (dip-loc-jal…), el
    mismo que usa el Auditor."""
    if not _DL:
        import asistente_recursos
        por_nombre = {d.get('ent'): d['id'] for d in asistente_recursos._docs_expide() if d.get('tipo') == 'dip-loc'}
        _DL.update({x['abbr']: por_nombre.get(x['name']) for x in base['estados']})
    return _DL


def portal(a):
    return 'planisferio-%s.html' % clave(a)


# Las tarjetas del portal (pedido del autor, 04-11-2026: «cada tarjeta tenga su
# autonomía… al inicio… el mapa de sus municipios y sus municipios uno por
# uno; todo lo demás… en sus respectivas tarjetas»). Cada tema del portal vive
# en su propia página, planisferio-<clave>-<tema>.html. La dimensión
# financiera es «presupuestos». Un tema nuevo del portal necesita aquí su
# renglón: (id, ícono, nombre de la tarjeta, lo que trae).
TEMAS = [
    ('presupuestos', '💰', 'Sus tres presupuestos', 'Lo que le baja de la Federación, lo que cobra el estado, lo que ingresan sus municipios, lo que no cuadra y su contador.'),
    ('deuda', '🏦', 'Su deuda', 'Lo que debe el gobierno del estado, cuánto le pesa y lo que pagaron sus municipios por sus créditos.'),
    ('inversion', '🏗️', 'Su inversión', 'La obra del gobierno del estado y de sus municipios, y lo que la ASF dejó por aclarar.'),
    ('legislativa', '🏛️', 'Su congreso', 'Lo que gastó su congreso, cuántas curules tiene y el tope de la Constitución.'),
    ('judicial', '⚖️', 'Su Poder Judicial', 'Lo que ejerció, lo que le entró, lo que concluyó y sus causas pendientes.'),
    ('salud', '🩺', 'Su salud pública', 'El IMSS y el ISSSTE en el estado: personas, consultas, médicos, camas y unidades.'),
    ('social', '🫂', 'Su pobreza y sus carencias', 'Cuántas personas viven en pobreza, sus seis carencias y lo que le aporta la Federación.'),
    ('administracion', '🏢', 'Su administración pública', 'El gobierno que ejecuta: su personal, lo que ejerció y sus contratos sin concurso.'),
    ('ambiental', '🌎', 'Sus recursos naturales', 'Sus acuíferos, bosques, incendios, pesca, minas y su refinería, si la tiene.'),
    ('leyes', '📜', 'Sus leyes del dinero', 'Con qué leyes cobra, compra, se endeuda y rinde cuentas, y dónde se publican.'),
    ('dimensiones', '🚪', 'En la Enciclopedia y en el Auditor', 'Su estado de cuenta, su circuito del dinero, lo que dejó la ASF y sus otras dimensiones.'),
]
TEMA_DIM = {'financiera': 'presupuestos'}


def subpagina(a, tema):
    """La página de un tema del portal; con una dimensión, la de su tema."""
    tema = TEMA_DIM.get(tema, tema)
    if tema not in [t[0] for t in TEMAS]:
        raise SystemExit('planisferio: el portal no tiene el tema %s' % tema)
    return 'planisferio-%s-%s.html' % (clave(a), tema)


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def _padron():
    """El padrón municipal tal cual (municipios-efipem.js), leído con node
    para no reinterpretar a mano un objeto de JavaScript."""
    js = ('global.window={};require(%s);process.stdout.write(JSON.stringify(window.AUDIT_MUNICIPIOS));'
          % json.dumps(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'municipios-efipem.js')))
    return json.loads(subprocess.run(['node', '-e', js], check=True, capture_output=True, text=True).stdout)


def geo_mun(cve_ent):
    """Los límites municipales de una entidad (Marco Geoestadístico 2024 del
    INEGI), si ya se integraron con integrar_mg_municipios.py."""
    ruta = os.path.join(RAIZ, 'docs', 'geo', 'mg2024-mun-%s.json' % cve_ent)
    return json.load(open(ruta, encoding='utf-8')) if os.path.exists(ruta) else None


# Las lentes del mapa municipal: (id, nombre, paleta, qué dice).
LENTES_MUN = [
    ('ing', 'Ingreso total', 'verde',
     'Todo lo que ingresó cada municipio en 2024: lo propio, lo que le llegó del estado y de la Federación, y lo que pidió prestado.'),
    ('predial', 'Predial cobrado', 'azul',
     'Lo que cada municipio cobró de impuesto predial en 2024: el impuesto que la Constitución le reserva (art. 115, fr. IV).'),
    ('dep', 'Dependencia de transferencias', 'rojo',
     'De cada $100 que ingresó en 2024, cuántos llegaron de fuera: (participaciones + aportaciones) ÷ ingreso total × 100.'),
    ('inv', 'Inversión pública', 'verde',
     'La obra pública y los proyectos productivos que pagó cada municipio en 2024: su capítulo de inversión pública. Un municipio con cuenta y sin ese capítulo reportó $0.'),
    ('invp', 'Inversión de cada $100', 'verde',
     'De cada $100 de su egreso de 2024, cuántos fueron a inversión pública: inversión ÷ egreso total × 100. El egreso total del INEGI cuenta también lo que quedó en caja al cierre. Ojo: donde el fondo de infraestructura social municipal (FAIS) pesa mucho, la proporción sube sola, porque la ley lo destina a obra para la población en pobreza (Ley de Coordinación Fiscal, art. 33).'),
    ('dpag', 'Pagó de deuda', 'rojo',
     'Lo que cada municipio pagó en 2024 por sus créditos: el capital que devolvió, los intereses y las comisiones. Es lo que pagó, no lo que debe. En el tono más claro, los que reportaron $0.'),
    ('emp', 'Pidió prestado', 'rojo',
     'Los préstamos que cada municipio recibió en 2024 (el concepto «Empréstitos» de su cuenta). Casi todos reportaron $0: van en el tono más claro.'),
]
PCT_MUN = ('dep', 'invp')
# Las lentes donde el $0 es lo común: el $0 lleva su propio tono y los cortes
# se sacan de los que sí reportaron algo.
CERO_MUN = ('dpag', 'emp')


def inv_mun(padron):
    """La inversión de cada municipio (municipios-inversion.js, la escribe
    anclar_inversion_municipios.py). Se detiene si no trae justo a los
    municipios del padrón que rindieron cuenta."""
    t = open(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'municipios-inversion.js'), encoding='utf-8').read()
    i = t.index('window.AUDIT_MUN_INV =') + len('window.AUDIT_MUN_INV =')
    iv = json.loads(t[i:t.rindex(';')])
    con = {m['cve'] + r[0] for m in padron['ent'].values() for r in m['lista'] if len(r) >= 10}
    if set(iv['mun']) != con or iv['anio'] != padron['anio']:
        raise SystemExit('planisferio: municipios-inversion.js no trae a los mismos municipios con cuenta que el padrón (sobran %s; faltan %s)' % (
            sorted(set(iv['mun']) - con)[:5], sorted(con - set(iv['mun']))[:5]))
    return iv


def deu_mun(padron):
    """La deuda en la cuenta de cada municipio (municipios-deuda.js, la escribe
    anclar_deuda_municipios.py): lo que pagó y lo que pidió prestado en el año.
    Se detiene si no trae justo a los municipios del padrón con cuenta."""
    t = open(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'municipios-deuda.js'), encoding='utf-8').read()
    i = t.index('window.AUDIT_MUN_DEUDA =') + len('window.AUDIT_MUN_DEUDA =')
    dv = json.loads(t[i:t.rindex(';')])
    con = {m['cve'] + r[0] for m in padron['ent'].values() for r in m['lista'] if len(r) >= 10}
    if set(dv['mun']) != con or dv['anio'] != padron['anio']:
        raise SystemExit('planisferio: municipios-deuda.js no trae a los mismos municipios con cuenta que el padrón (sobran %s; faltan %s)' % (
            sorted(set(dv['mun']) - con)[:5], sorted(con - set(dv['mun']))[:5]))
    return dv

MAPA_MUN = """<div class="pl-lentes" role="radiogroup" aria-label="Qué ver en el mapa de los municipios">%s</div>
          <p class="pl-que" id="plMunQue"></p>
          <div class="pl-rej" id="plMunMapa">
            <figure class="pl-fig">
              %s
              <figcaption class="pl-leyenda" id="plMunLeyenda"></figcaption>
            </figure>
            <aside class="pl-ficha" id="plMunFicha" aria-live="polite">
              <p class="pl-ficha-vacia"><b>Toca un municipio.</b> Verás lo que ingresó en %d, de dónde le llegó, lo que invirtió, lo que pagó de deuda y la puerta a su ficha en el Auditor de entes.</p>
            </aside>
          </div>
          <p class="pl-pie">Límites: %s (<a href="%s">descarga del INEGI</a>), integrados el %s; huella SHA-256 del archivo de origen <code>%s</code>. Simplificados para verse en pantalla. %s
          Cifras: INEGI, finanzas públicas municipales %d %s. %s</p>
          <script type="application/json" id="plMunDatos">%s</script>"""


def _mapa_mun(e, m, g, ref, padron, iv, dv):
    """El mapa de los municipios de una entidad, con sus cifras del padrón."""
    cves_geo = {x['c'] for x in g['m']}
    # Las claves 990 y más del catálogo del INEGI («No especificado», en el
    # Estado de México la 996) no son un territorio: no tienen trazo.
    cves_pad = {r[0] for r in m['lista'] if r[0] < '990'}
    if cves_geo != cves_pad:
        raise SystemExit('planisferio: el Marco Geoestadístico y el padrón no traen los mismos municipios de %s (sobran %s; faltan %s)' % (
            e['name'], sorted(cves_geo - cves_pad), sorted(cves_pad - cves_geo)))
    datos = []
    for r in m['lista']:
        if r[0] >= '990':
            continue
        x = {'c': r[0], 'n': r[1]}
        if len(r) >= 10:
            ing, part, aport, fortamun, fismdf, predial = r[2], r[3], r[4], r[5], r[6], r[7]
            x.update({'ing': round(ing / 1e6, 1), 'part': round(part / 1e6, 1), 'aport': round(aport / 1e6, 1),
                      'predial': round(predial / 1e6, 1), 'fort': round(fortamun / 1e6, 1), 'fis': round(fismdf / 1e6, 1),
                      'dep': round((part + aport) / ing * 100, 1) if ing else None})
            v = iv['mun'][m['cve'] + r[0]]
            x.update({'inv': round(v[0] / 1e6, 1), 'invp': round(v[0] / r[9] * 100, 1) if r[9] else None})
            d = dv['mun'][m['cve'] + r[0]]
            x.update({'dpag': round((d[1] + d[2] + d[3]) / 1e6, 1), 'emp': round(d[5] / 1e6, 1), 'adef': round(d[4] / 1e6, 1)})
        datos.append(x)
    svg = '<svg class="pl-svg pl-svg-mun" viewBox="0 0 %s %s" role="group" aria-label="Los municipios de %s">%s</svg>' % (
        g['vb'][0], g['vb'][1], e['name'], ''.join(
            '<path class="pl-mun" data-c="%s" d="%s" tabindex="0" role="button" aria-label="%s"><title>%s</title></path>' % (
                x['c'], x['d'], x['n'], x['n']) for x in g['m']))
    lentes = ''.join('<button type="button" class="pl-lente" role="radio" aria-checked="%s" data-l="%s">%s</button>' % (
        'true' if k == 0 else 'false', i, n) for k, (i, n, _p, _q) in enumerate(LENTES_MUN))
    sin = None if m['conCifra'] else ('Las alcaldías de la Ciudad de México no rinden cuenta municipal al INEGI: '
                                      'su dinero va dentro del presupuesto de la Ciudad.')
    info = {'ent': e['abbr'], 'cve': m['cve'], 'pend': 'municipios-sin-cuenta', 'anio': padron['anio'], 'sin': sin,
            'lentes': [{'id': i, 'nom': n, 'pal': p, 'que': q, 'u': 'pct' if i in PCT_MUN else 'mdp', 'cero': i in CERO_MUN} for i, n, p, q in LENTES_MUN], 'm': datos}
    return MAPA_MUN % (
        '' if sin else lentes, svg, padron['anio'], g['fuente'], g['url'], g['integrado'], g['sha256'][:12] + '…', g['aviso'],
        padron['anio'], ref('ref-inegi-efipem'),
        ('En gris, todas, porque no rinden cuenta municipal %s.' % chip('pendiente', 'municipios-sin-cuenta') if sin else
         'En gris, los municipios que no rindieron su cuenta de %d %s.' % (padron['anio'], chip('pendiente', 'municipios-sin-cuenta'))),
        _json(info))


def _existe(enlace):
    # La página de los recursos naturales se escribe en la misma corrida
    # (recursos_naturales.pagina()), así que cuenta aunque aún no esté en disco.
    # Igual las de la administración pública (administracion_publica.py),
    # que escribe poderes_paginas() de apartados.py.
    import recursos_naturales
    import administracion_publica
    archivo = enlace.split('#')[0].split('?')[0]
    return (archivo == recursos_naturales.ARCHIVO or archivo in [administracion_publica.PORTADA] + [x[0] for x in administracion_publica.PAGINAS]
            or os.path.exists(os.path.join(RAIZ, archivo)))


def _ritmo(anual_mdp):
    """Pesos por segundo de una cifra anual en millones: derivado."""
    return anual_mdp * 1e6 / SEG_ANIO


def _pesos(v):
    return '$' + format(round(v), ',')


def _contador(id_, ico, nom, v, est, que, fuente, desglose):
    """Un contador del año: la cifra, su ritmo y su fuente a la vista; lo que
    es y su desglose, en la ventana lateral (decisión del autor, 03-11-2026:
    menos narración en la página, el desglose como cajón)."""
    s = _ritmo(v)
    tpl = 'plTplCont-' + id_
    return ('<article class="pl-cont" data-anual="%.1f">'
            '<p class="pl-cont-n"><span aria-hidden="true">%s</span> %s</p>'
            '<p class="pl-cont-v"><b class="num-tabular">%s</b> %s</p>'
            '<p class="pl-cont-s">A su ritmo anual, <b class="num-tabular">%s por segundo</b> %s</p>'
            '<p class="pl-cont-vivo" aria-live="off">Desde que abriste esta página: <b class="num-tabular pl-vivo">$0</b></p>'
            '<p class="pl-cont-f">%s</p>'
            '<button type="button" class="pl-cont-b" data-cajon="%s" data-cajon-tit="%sTit" aria-haspopup="dialog">🔎 Ver su desglose</button>'
            '<template id="%s">%s</template></article>' % (
                v, ico, nom, mdp(v), chip(est), _pesos(s), chip('derivado'), fuente, tpl, tpl, tpl,
                _cajon('🔎', 'El desglose', nom, tpl + 'Tit', '<section class="glos-drawer-sec"><h4>Qué es</h4><p>%s</p></section>%s' % (que, desglose),
                       '<a class="glos-drawer-todo" href="numeros-gasto-tres-presupuestos.html" style="text-align:center; text-decoration:none;">📚 Verlo en la Enciclopedia ➔</a>')))


def _cajon(ico, marca, titulo, tid, cuerpo, pie='', cat='Planisferio'):
    """El molde de la ventana lateral de apartados.js (button[data-cajon])."""
    return ('<header class="glos-drawer-cab"><span class="glos-drawer-marca"><span aria-hidden="true">%s</span> %s</span>'
            '<button type="button" class="glos-drawer-x" aria-label="Cerrar">✕</button></header>'
            '<div class="glos-drawer-cuerpo"><span class="glos-drawer-cat">%s</span><h3 id="%s" class="glos-drawer-tit">%s</h3>%s</div>%s') % (
                ico, marca, cat, tid, titulo, cuerpo, ('<footer class="glos-drawer-pie">%s</footer>' % pie) if pie else '')


def _filas(xs):
    return '<ul class="pl-des">%s</ul>' % ''.join(
        '<li><span>%s</span><b class="num-tabular">%s</b>%s</li>' % (n, v, (' ' + e) if e else '') for n, v, e in xs)


def _datos(base, padron):
    import asistente_legislativo as al
    import gestion_judicial as gj
    import recursos_naturales as rn
    cg = al.congresos_estados(base)
    rf = rn.refinerias_estados()
    mi = rn.mineria([e['abbr'] for e in base['estados']])
    aq = rn.acuiferos([e['abbr'] for e in base['estados']])
    ic = rn.incendios([e['abbr'] for e in base['estados']])
    fo = rn.forestal([e['abbr'] for e in base['estados']])
    pe = rn.pesca([e['abbr'] for e in base['estados']])
    pj = gj.judiciales_estados(base)
    import gestion_salud as gsal
    sa = gsal.salud_estados(base)
    import administracion_publica as apu
    ap = apu.estados(base)
    import dimension_social as dso
    so = dso.estados(base)
    E = base['estados']
    C = base['fiscalEntidades']['campos']
    sin = set(C['recaudacionPropia'].get('sinFuente', []))
    cuad, obras = tm.cuadre_obras(base)
    filas = []
    for e in E:
        m = padron['ent'].get(e['abbr'])
        if not m:
            raise SystemExit('planisferio: el padrón municipal no trae la entidad %s' % e['abbr'])
        con = m['conCifra']
        filas.append({
            'a': e['abbr'], 'n': e['name'], 'p': portal(e['abbr']), 'cap': e['capital'], 'pob': e['pobPersonas'],
            'fed': e['gasto'], 'r28': e['ramo28'], 'r33': e['ramo33'], 'pc': e['pc'],
            'est': None if e['abbr'] in sin else e['recaudacionPropia'],
            'dep': None if e['abbr'] in sin else e['dep'],
            'mun': round(m['tot']['ing'] / 1e6, 1) if con else None,
            'mn': m['n'], 'mc': con, 'mm': geo_mun(m['cve']) is not None,
            # La deuda (Sistema de Alertas, Cuenta Pública 2025). La entidad
            # que no se mide (hoy Tlaxcala) no trae indicadores: queda en gris.
            'deuda': e['deuda'], 'dpc': round(e['deuda'] * 1e6 / e['pobPersonas']),
            'ild': e['deudaIld'] if _medida(e) else None, 'sd': e.get('deudaSd'), 'ocp': e.get('deudaOcp'),
            'ildm': e.get('ildMdp'), 'sem': SEMAFORO[e['semaforoDeuda']] if _medida(e) else 'No se mide',
            # La inversión (INEGI, finanzas estatales 2024; la Ciudad de México
            # no figura en el conjunto estatal) y lo que dejó la ASF.
            'inv': e.get('invPub'), 'invt': e.get('invInfra'),
            'invp': round(e['invPub'] / e['egr2024'] * 100, 1) if e.get('invPub') is not None else None,
            'asf': e['asfMontoObservado'], 'aud': e['asfAuditorias'],
            # Su congreso (INEGI, CNPLE 2025): lo que ejerció en 2024, sus
            # personas legisladoras y las dos divisiones nuestras.
            'leg': cg[e['abbr']]['g'], 'legn': cg[e['abbr']]['n'], 'legx': cg[e['abbr']]['x'], 'legp': cg[e['abbr']]['p'],
            # Su Poder Judicial (INEGI, CNIJF-E 2025): lo que ejerció en 2024,
            # lo que concluyó, el rezago penal y sus personas juzgadoras.
            'jud': pj[e['abbr']]['g'], 'judc': pj[e['abbr']]['c100'], 'juda': pj[e['abbr']]['xa'],
            'judr': pj[e['abbr']]['p'], 'judj': pj[e['abbr']]['j'],
            'judi': pj[e['abbr']]['i'], 'judk': pj[e['abbr']]['c'],
            # Lo que no cuadra y sus obras con alerta ambiental (las mismas
            # cuentas del mapa de la Enciclopedia).
            'cua': cuad[e['abbr']],
            'obr': sum(obras.get(e['abbr'], {}).values()),
            'obp': obras.get(e['abbr'], {}).get('publico', 0), 'obv': obras.get(e['abbr'], {}).get('privado', 0),
        })
        # Su IMSS (Memoria Estadística 2025, por OOAD) y su ISSSTE (registro
        # sectorial de la DGIS 2025): las dos fuentes no se mezclan.
        h = sa[e['abbr']]
        filas[-1].update({'imA': h['ads'], 'imX': h['conx'], 'imQ': h['iq'], 'imK': h['camk'],
                          'isM': h['is']['med'], 'isK': h['is']['cam'], 'isU': h['is']['u'], 'imM': h['im']['med'],
                          'sal': {'con': h['con'], 'esp': h['esp'], 'urg': h['urg'], 'egr': h['egr'], 'camc': h['camc'], 'iqk': h['iqk'],
                                  'ie': h['is']['enf'], 'ic': h['is']['cons'], 'mu': h['im']['u'], 'mk': h['im']['cam'], 'me': h['im']['enf'],
                                  'oo': [n for n, _ in h.get('ooad', [])]}})
        # Su administración pública (03-11-2026): lo que su gobierno le reportó
        # al censo del INEGI (CNGE 2025), lo que ejercieron sus municipios
        # (CNGMD 2025) y lo que la ASF dejó por aclarar a cada nivel (CP 2024).
        # Su pobreza (INEGI, Pobreza multidimensional 2024) y sus aportaciones
        # federales de 2026 por persona en pobreza (derivado).
        z = so[e['abbr']]
        filas[-1].update({'soP': z['p'], 'soN': z['pers'], 'soX': z['x'], 'soI': z['ing'], 'soS': z['car']['seg'], 'soA': z['car']['sal'],
                          'soR': z['car']['rez'], 'soQ': z['r33'],
                          'soc': {'m': z['m'], 'ix': z['ingx'], 'v': z['car']['viv'], 'b': z['car']['bas'], 'al': z['car']['ali'], 'pt': z['pobT'], 'u': z['url']}})
        x = ap[e['abbr']]
        filas[-1].update({'apP': x['per'], 'apK': x['perk'], 'apX': x['pres'], 'apD': x['ad'], 'apG': x['gpa'], 'apM': x['mpres'], 'apA': x['mpa'],
                          'apu': {'tit': x['tit'], 'con': x['con'], 'ga': x['ga'], 'ma': x['ma'], 'presp': x['presp'], 'mpresp': x['mpresp'],
                                  'oa': x['oa'], 'opa': x['opa']}})
        # Su refinería de PEMEX, si tiene (Segundo Informe 2026 y estados
        # financieros de PEMEX 2025): una o ninguna por entidad.
        r = rf.get(e['abbr'])
        filas[-1].update({'refj': r['jun'] if r else None, 'refp': r['prom'] if r else None, 'refu': r['uso'] if r else None})
        if r:
            filas[-1]['ref'] = {k: r[k] for k in ('id', 'n', 'sede', 'jun', 'prom', 'max', 'mmax', 'd25', 'd24', 'vu25', 'lug', 'cap', 'uso', 'usoj')}
        # Sus concesiones mineras (Secretaría de Economía, DGM, marzo de 2024).
        x = mi.get(e['abbr'])
        filas[-1].update({'minT': x['t'] if x else None, 'minH': x['ha'] if x else None})
        if x:
            filas[-1]['min'] = {k: x[k] for k in ('pt', 'ph', 'hxt', 'lug', 't26', 'prod')}
        # Sus acuíferos (CONAGUA, DOF 09-11-2023, corte al 30-12-2022): las 32 tienen.
        w = aq[e['abbr']]
        filas[-1].update({'acuP': w['ps'], 'acuD': w['def'],
                          'acu': {'n': w['n'], 'con': w['con'], 'sin': w['sin'], 'disp': w['disp'], 'lug': w['lug'], 's27': [n for c, n, d in w['s27']]}})
        # Sus incendios forestales (CONAFOR, cierre de 2025 y de 2024): las 32 tienen.
        z = ic[e['abbr']]
        filas[-1].update({'incH': z['ha'], 'incN': z['n'],
                          'inc': {k: z[k] for k in ('parb', 'hxi', 'lleg', 'lh', 'ln', 'ha24', 'cam')}})
        # Su superficie forestal (CONAFOR, 2023, mapa de vegetación de 2018): las 32 tienen.
        b = fo[e['abbr']]
        filas[-1].update({'sfT': b['sf'], 'incP': b['pq'],
                          'sf': {k: b[k] for k in ('parb', 'psec', 'pnac', 'lug', 'lq')}})
        # Su pesca y su acuacultura (CONAPESCA, Anuario 2025): Nuevo León no registró en 2025.
        q = pe[e['abbr']]
        filas[-1].update({'peT': q['t'], 'peV': q['mdp'],
                          'pe': {k: q[k] for k in ('pacu', 'pt', 'lt', 'lv', 'ct', 'cv', 't24')}})
    return filas


# El color del semáforo, con el nombre que le da el Sistema de Alertas.
SEMAFORO = {'Verde': 'Endeudamiento sostenible', 'Amarillo': 'Endeudamiento en observación', 'Rojo': 'Endeudamiento elevado'}


def _medida(e):
    """Si el Sistema de Alertas midió a la entidad (Tlaxcala no: no tiene
    deuda inscrita en el Registro Público Único)."""
    return e.get('deudaSd') is not None


def _sda(base):
    """El archivo del Sistema de Alertas del que salen las cifras, con su
    huella: lo trae la ficha «deuda-estados» de los Expedientes."""
    f = next(x for x in base['expedientes']['fichas'] if x['id'] == 'deuda-estados')
    return f['documentos'][0], f['documentos'][1]['url']


LENTES = [
    {'id': 'fed', 'dim': 'financiera', 'fmt': 'mdp', 'nom': '1 · Lo que baja de la Federación', 'pal': 'oro', 'est': 'derivado', 'anio': 2026,
     'que': 'Participaciones (Ramo 28) más aportaciones (Ramo 33) que la Federación le entrega a cada entidad en 2026. Es el primer piso: el dinero federal que llega al territorio.'},
    {'id': 'est', 'dim': 'financiera', 'fmt': 'mdp', 'nom': '2 · Lo que cobra el estado', 'pal': 'azul', 'est': 'derivado', 'anio': 2024,
     'que': 'Lo que el gobierno del estado recaudó por su cuenta en 2024: impuestos estatales, cuotas, derechos, productos y aprovechamientos. Es el segundo piso.'},
    {'id': 'mun', 'dim': 'financiera', 'fmt': 'mdp', 'nom': '3 · Lo que ingresan sus municipios', 'pal': 'verde', 'est': 'derivado', 'anio': 2024,
     'que': 'Todo lo que ingresaron en 2024 los municipios del estado que rindieron su cuenta al INEGI: lo propio, lo que les llega del estado y de la Federación, y lo que pidieron prestado. Es el tercer piso.'},
    # «No cuadra» (04-11-2026, el Planisferio como matriz de los mapas): la
    # lente del mapa de la Enciclopedia, con su misma cuenta y su mismo texto
    # (cuadre_obras() y QUE_CUADRE de territorio_modulos.py).
    {'id': 'cua', 'dim': 'financiera', 'fmt': 'pct2', 'nom': 'No cuadra: lo recibido contra lo pagado', 'pal': 'rojo', 'est': 'derivado', 'anio': 2024,
     'que': tm.QUE_CUADRE},
    # La dimensión de la deuda (03-11-2026): lo que debe cada gobierno estatal
    # y los tres indicadores con que lo mide el Sistema de Alertas.
    {'id': 'deuda', 'dim': 'deuda', 'fmt': 'mdp', 'nom': 'Lo que debe', 'pal': 'rojo', 'est': 'oficial', 'anio': 2025,
     'que': 'La deuda pública y las obligaciones de cada gobierno estatal al cierre de 2025, según el Sistema de Alertas de Hacienda. Solo cuenta la que está inscrita en el Registro Público Único.'},
    {'id': 'dpc', 'dim': 'deuda', 'fmt': 'pesos', 'nom': 'Por habitante', 'pal': 'rojo', 'est': 'derivado', 'anio': 2025,
     'que': 'La misma deuda, repartida entre los habitantes de cada estado: así se comparan un estado grande y uno chico.'},
    {'id': 'ild', 'dim': 'deuda', 'fmt': 'pct', 'nom': 'Deuda ÷ ingresos libres', 'pal': 'rojo', 'est': 'oficial', 'anio': 2025,
     'que': ('Primer indicador del Sistema de Alertas: la deuda y las obligaciones entre los ingresos de libre disposición, los que el estado gasta en lo que decide '
             '(sus cobros propios y las participaciones federales, lo que no llega etiquetado). Un 50 % quiere decir que debe el equivalente a medio año de esos ingresos.')},
    {'id': 'sd', 'dim': 'deuda', 'fmt': 'pct', 'nom': 'Lo que se va en pagarla', 'pal': 'rojo', 'est': 'oficial', 'anio': 2025,
     'que': ('Segundo indicador: lo que el estado pagó en el año por su deuda y sus obligaciones (capital, intereses y comisiones) entre sus ingresos de libre disposición. '
             'Dice cuánto de su dinero libre ya no puede usar en otra cosa.')},
    {'id': 'ocp', 'dim': 'deuda', 'fmt': 'pct', 'nom': 'Deudas de corto plazo', 'pal': 'rojo', 'est': 'oficial', 'anio': 2025,
     'que': ('Tercer indicador: lo que debe a corto plazo, a proveedores y a contratistas, menos lo que tiene en efectivo, bancos e inversiones temporales, '
             'entre sus ingresos totales. Si sale negativo, tenía en caja más que esas deudas.')},
    # La inversión (03-11-2026): las dos vías por las que un gobierno estatal
    # hace obra, que no se suman, y lo que dejó por aclarar la ASF.
    {'id': 'inv', 'dim': 'inversion', 'fmt': 'mdp', 'nom': 'Obra que hizo el estado', 'pal': 'verde', 'est': 'oficial', 'anio': 2024,
     'que': ('Lo que el gobierno del estado gastó en su capítulo de inversión pública: la obra que contrató o hizo por su cuenta. '
             'No cuenta la que hace por medio de sus organismos de obra: esa es otra lente, y no se suman.')},
    {'id': 'invp', 'dim': 'inversion', 'fmt': 'pct', 'nom': 'De cada $100 de su egreso', 'pal': 'verde', 'est': 'derivado', 'anio': 2024,
     'que': 'La misma obra directa, entre todo el egreso del gobierno del estado en el año: cuántos de cada $100 se fueron en obra que hizo él mismo. El egreso total del INEGI cuenta también lo que quedó en caja al cierre (disponibilidad final).'},
    {'id': 'invt', 'dim': 'inversion', 'fmt': 'mdp', 'nom': 'A sus organismos de obra', 'pal': 'verde', 'est': 'oficial', 'anio': 2024,
     'que': ('Lo que el gobierno del estado les pasó a sus organismos de infraestructura: juntas de caminos, comisiones de agua, institutos de obra. '
             'Con eso hacen obra, pero también pagan su nómina y su operación.')},
    {'id': 'asf', 'dim': 'inversion', 'fmt': 'mdp', 'nom': 'Por aclarar ante la ASF', 'pal': 'rojo', 'est': 'oficial', 'anio': 2024,
     'que': ('Lo que la Auditoría Superior de la Federación dejó por aclarar del dinero federal que recibió cada estado (Cuenta Pública 2024). '
             'Por aclarar no es robado: es dinero cuyo destino no quedó acreditado. Es todo el dinero federal auditado, no solo el de obra.')},
    # La dimensión legislativa (03-11-2026): los 32 congresos locales, con
    # el censo del INEGI y el tope del art. 116 constitucional.
    {'id': 'leg', 'dim': 'legislativa', 'fmt': 'mdp', 'nom': 'Lo que gastó su congreso', 'pal': 'azul', 'est': 'oficial', 'anio': 2024,
     'que': ('Lo que ejerció en 2024 el congreso de cada entidad, según lo que reportó al Censo Nacional de Poderes Legislativos Estatales del INEGI. '
             'Es el gasto de toda la institución (personal, edificios, comisiones y órganos técnicos), no solo las dietas.')},
    {'id': 'legx', 'dim': 'legislativa', 'fmt': 'mdp', 'nom': 'Por cada legislador', 'pal': 'azul', 'est': 'derivado', 'anio': 2024,
     'que': ('El mismo gasto entre las personas legisladoras de cada congreso: así se comparan uno grande y uno chico. '
             'No es lo que gana cada quien: es lo que cuesta la institución por cada curul.')},
    {'id': 'legp', 'dim': 'legislativa', 'fmt': 'pct2', 'nom': 'Frente al tope del 0.70 %', 'pal': 'rojo', 'est': 'derivado', 'anio': 2024,
     'que': ('El gasto del congreso entre el egreso total del gobierno de su estado, × 100. Desde la reforma del 23 de abril de 2026, la Constitución pide que el presupuesto '
             'de cada congreso local no pase del 0.70 % del presupuesto de egresos de su estado (art. 116, fr. II). Es una referencia, no un incumplimiento: '
             'el gasto es de 2024, anterior a la reforma, y se divide entre el egreso que registró el INEGI, no entre el presupuesto que aprobó cada congreso.')},
    {'id': 'legn', 'dim': 'legislativa', 'fmt': 'n', 'nom': 'Cuántos lo integran', 'pal': 'azul', 'est': 'oficial', 'anio': 2025,
     'que': ('Las personas legisladoras en activo de cada congreso al cierre del último periodo que reportó al censo del INEGI. '
             'La Constitución pone el piso: 7, 9 u 11 según la población del estado (art. 116, fr. II).')},
    # La dimensión judicial (03-11-2026): los 32 poderes judiciales de los
    # estados, con el censo del INEGI. El dinero va junto a lo que resolvió.
    {'id': 'jud', 'dim': 'judicial', 'fmt': 'mdp', 'nom': 'Lo que ejerció', 'pal': 'cafe', 'est': 'oficial', 'anio': 2024,
     'que': ('El presupuesto que ejerció en 2024 el Poder Judicial de cada estado, según lo que le reportó al Censo Nacional de Impartición de Justicia del INEGI. '
             'Paga todo el poder judicial: juzgados, tribunal superior, administración, edificios y personal de apoyo.')},
    {'id': 'judc', 'dim': 'judicial', 'fmt': 'pct', 'nom': 'Concluyó de cada 100 que entraron', 'pal': 'cafe', 'est': 'derivado', 'anio': 2024,
     'que': ('Asuntos concluidos en primera instancia entre los que ingresaron, × 100. Más de 100 quiere decir que también cerró asuntos de años anteriores. '
             'No es el rezago: en lo civil, familiar y mercantil el INEGI cuenta como ingresada toda demanda, también la que se desecha.')},
    {'id': 'juda', 'dim': 'judicial', 'fmt': 'pesos', 'nom': 'Por asunto concluido', 'pal': 'cafe', 'est': 'derivado', 'anio': 2024,
     'que': ('Lo que ejerció entre los asuntos que concluyó en primera instancia. No es lo que cuesta un juicio: el presupuesto paga todo el poder judicial, '
             'y un asunto concluido puede ser una sentencia o un desechamiento. Sirve para comparar, no para cobrar.')},
    {'id': 'judr', 'dim': 'judicial', 'fmt': 'n', 'nom': 'Causas penales pendientes', 'pal': 'cafe', 'est': 'oficial', 'anio': 2024,
     'que': ('Las causas penales del sistema acusatorio que quedaron pendientes de concluir al cierre de 2024. Es el único rezago que el censo publica completo; '
             'en los estados, el INEGI cuenta a cada persona procesada, no cada expediente.')},
    {'id': 'judj', 'dim': 'judicial', 'fmt': 'n', 'nom': 'Personas juzgadoras', 'pal': 'cafe', 'est': 'oficial', 'anio': 2024,
     'que': ('Las magistradas, magistrados, juezas y jueces de cada poder judicial estatal que reportó el censo, de todas las materias. '
             'Desde la reforma de 2024, la Constitución pide que se elijan por voto directo (art. 116, fr. III).')},
    # La salud pública (03-11-2026, pedido del autor: «sería IMSS e ISSSTE»).
    # Del IMSS, su Memoria por OOAD; del ISSSTE, el registro de la DGIS,
    # porque su anuario no responde. Los dos documentos no se mezclan.
    {'id': 'imA', 'dim': 'salud', 'fmt': 'n', 'nom': 'IMSS · Personas adscritas', 'pal': 'naranja', 'est': 'oficial', 'anio': 2025,
     'que': ('Las personas adscritas a una clínica de medicina familiar del IMSS en cada estado al 31 de diciembre de 2025: trabajadores, sus familias y pensionados. '
             'Son las que el IMSS atiende en su primer nivel; no es la población del estado ni toda la que tiene derecho.')},
    {'id': 'imX', 'dim': 'salud', 'fmt': 'dec2', 'nom': 'IMSS · Consultas por persona adscrita', 'pal': 'naranja', 'est': 'derivado', 'anio': 2025,
     'que': ('Todas las consultas que dio el IMSS en el estado en 2025 (de medicina familiar, especialidad, urgencias y dentales) entre sus personas adscritas. '
             'Cuenta consultas, no si se resolvió el problema ni cuánto se esperó. Los hospitales de alta especialidad atienden a gente de otros estados y se cuentan donde están.')},
    {'id': 'imQ', 'dim': 'salud', 'fmt': 'n', 'nom': 'IMSS · Cirugías', 'pal': 'naranja', 'est': 'oficial', 'anio': 2025,
     'que': ('Las intervenciones quirúrgicas que registró el IMSS en cada estado en 2025, según su Memoria. Ojo: el IMSS anunció «1.78 millones de cirugías» en el país y su Memoria '
             'registra más intervenciones; son dos conteos que ningún documento explica.')},
    {'id': 'imK', 'dim': 'salud', 'fmt': 'dec2', 'nom': 'IMSS · Camas por cada mil adscritos', 'pal': 'naranja', 'est': 'derivado', 'anio': 2025,
     'que': ('Las camas censables (las de hospitalización, sin urgencias ni recuperación) del IMSS en cada estado por cada mil personas adscritas. '
             'Dice con cuánto cuenta, no cuántas están ocupadas ni si hay personal para usarlas.')},
    {'id': 'isM', 'dim': 'salud', 'fmt': 'n', 'nom': 'ISSSTE · Médicos', 'pal': 'naranja', 'est': 'oficial', 'anio': 2025,
     'que': ('Las médicas y médicos generales, especialistas y odontólogos del ISSSTE en cada estado, según el registro de recursos de la Secretaría de Salud (DGIS). '
             'Cuántas personas atiende el ISSSTE en cada estado no se puede decir: su anuario no responde. Algunas unidades no reportaron personal.')},
    {'id': 'isK', 'dim': 'salud', 'fmt': 'n', 'nom': 'ISSSTE · Camas de hospital', 'pal': 'naranja', 'est': 'oficial', 'anio': 2025,
     'que': ('Las camas del área de hospitalización del ISSSTE en cada estado (registro de la DGIS). Sin cuántos derechohabientes tiene cada estado, no se puede decir si son pocas o muchas.')},
    {'id': 'isU', 'dim': 'salud', 'fmt': 'n', 'nom': 'ISSSTE · Unidades', 'pal': 'naranja', 'est': 'oficial', 'anio': 2025,
     'que': ('Los establecimientos del ISSSTE en cada estado (registro de la DGIS): clínicas, hospitales y unidades de apoyo. Muchas unidades chicas no es lo mismo que mucha atención.')},
    {'id': 'imM', 'dim': 'salud', 'fmt': 'n', 'nom': 'IMSS · Médicos, en el mismo registro', 'pal': 'naranja', 'est': 'oficial', 'anio': 2025,
     'que': ('Las médicas y médicos del IMSS en cada estado según el mismo registro de la DGIS que el ISSSTE: así se comparan las dos instituciones con la misma regla. '
             'Desde 2025 incluye las unidades rurales del antiguo programa IMSS-Bienestar, por eso no es la cifra de la Memoria.')},
    # La administración pública (03-11-2026, pedido del autor): el gobierno
    # que ejecuta. Lo del INEGI es lo que cada gobierno reportó a su censo.
    # La dimensión social (04-11-2026, pedido del autor): la pobreza del INEGI
    # 2024 (dimension_social.py) y las aportaciones 2026 por persona en pobreza.
    {'id': 'soP', 'dim': 'social', 'fmt': 'pct', 'nom': 'Población en pobreza', 'pal': 'rosa', 'est': 'oficial', 'anio': 2024,
     'que': ('De cada 100 personas del estado, cuántas viven en pobreza según el INEGI: su ingreso no alcanza para lo básico y tienen al menos una de seis carencias '
             '(educación, salud, seguridad social, vivienda, servicios en la vivienda o alimentación). Es lo que mide el INEGI en los hogares, no el resultado de un solo gobierno.')},
    {'id': 'soN', 'dim': 'social', 'fmt': 'n', 'nom': 'Personas en pobreza', 'pal': 'rosa', 'est': 'derivado', 'anio': 2024,
     'que': 'Cuántas personas: el porcentaje en pobreza × la población que el INEGI usó en su medición. Los estados grandes salen arriba por tamaño, aunque su porcentaje sea bajo.'},
    {'id': 'soX', 'dim': 'social', 'fmt': 'pct', 'nom': 'Pobreza extrema', 'pal': 'rosa', 'est': 'oficial', 'anio': 2024,
     'que': ('De cada 100 personas, cuántas viven en pobreza extrema: su ingreso no alcanza ni para la canasta alimentaria y tienen tres o más carencias. '
             'En los estados donde es muy baja, el INEGI avisa que la cifra es menos precisa (su coeficiente de variación es moderado o bajo).')},
    {'id': 'soI', 'dim': 'social', 'fmt': 'pct', 'nom': 'Ingreso bajo la línea de pobreza', 'pal': 'rosa', 'est': 'oficial', 'anio': 2024,
     'que': 'De cada 100 personas, cuántas tienen un ingreso que no alcanza para la canasta alimentaria y la no alimentaria, aunque no tengan carencias. Es la pobreza por ingresos.'},
    {'id': 'soS', 'dim': 'social', 'fmt': 'pct', 'nom': 'Sin seguridad social', 'pal': 'rosa', 'est': 'oficial', 'anio': 2024,
     'que': 'De cada 100 personas, cuántas no tienen acceso a la seguridad social: ni empleo con IMSS o ISSSTE, ni pensión, ni la tienen por un familiar. Es la carencia más extendida del país.'},
    {'id': 'soA', 'dim': 'social', 'fmt': 'pct', 'nom': 'Sin acceso a servicios de salud', 'pal': 'rosa', 'est': 'oficial', 'anio': 2024,
     'que': 'De cada 100 personas, cuántas no están afiliadas ni tienen derecho a una institución pública o privada de salud. Mide la afiliación, no si la clínica tiene médico o medicina.'},
    {'id': 'soR', 'dim': 'social', 'fmt': 'pct', 'nom': 'Rezago educativo', 'pal': 'rosa', 'est': 'oficial', 'anio': 2024,
     'que': 'De cada 100 personas, cuántas no tienen la escolaridad obligatoria que les correspondía por su edad ni asisten a la escuela.'},
    {'id': 'soQ', 'dim': 'social', 'fmt': 'pesos', 'nom': 'Aportaciones por persona en pobreza', 'pal': 'rosa', 'est': 'derivado', 'anio': '2026 ÷ 2024',
     'que': ('Las aportaciones federales de 2026 (Ramo 33) ÷ las personas en pobreza de 2024. Sirve para comparar estados, no es lo que le llega a cada persona pobre: '
             'el Ramo 33 paga sobre todo maestros y salud, y solo su fondo de infraestructura social (FAIS) va por ley a la población en pobreza.')},
    {'id': 'apP', 'dim': 'administracion', 'fmt': 'n', 'nom': 'Personal de su administración', 'pal': 'azul', 'est': 'oficial', 'anio': 2024,
     'que': ('Las personas que el gobierno de cada estado le reportó al INEGI en su administración pública al cierre de 2024, con sus titulares. '
             'Es lo que cada uno contestó al censo: el INEGI no dice qué organismos incluyó cada gobierno, y por eso hay diferencias que no son de tamaño.')},
    {'id': 'apK', 'dim': 'administracion', 'fmt': 'dec1', 'nom': 'Personal por cada mil habitantes', 'pal': 'azul', 'est': 'derivado', 'anio': 2024,
     'que': ('El personal de su administración entre la población del estado, por mil. Sirve para preguntar, no para concluir: un estado que reporta poco '
             'puede tener a sus maestros o médicos en organismos que no contó.')},
    {'id': 'apX', 'dim': 'administracion', 'fmt': 'mdp', 'nom': 'Lo que ejerció su gobierno', 'pal': 'verde', 'est': 'oficial', 'anio': 2024,
     'que': ('El presupuesto que ejerció la administración pública de cada estado en 2024, en pesos de ese año, según su respuesta al censo del INEGI. '
             'No es la Cuenta Pública del estado: es lo que reportó su Poder Ejecutivo, sin su congreso ni su poder judicial.')},
    {'id': 'apD', 'dim': 'administracion', 'fmt': 'pct', 'nom': 'Contratos por adjudicación directa', 'pal': 'rojo', 'est': 'oficial', 'anio': 2024,
     'que': ('De cada 100 contratos que hizo la administración del estado en 2024, cuántos se dieron por adjudicación directa, sin concurso. '
             'Cuenta contratos, no pesos, y la adjudicación directa es legal en los casos que fija la ley: dice cuánto se compra sin competir, no que haya irregularidad.')},
    {'id': 'apG', 'dim': 'administracion', 'fmt': 'mdp', 'nom': 'ASF · Por aclarar del gobierno del estado', 'pal': 'rojo', 'est': 'oficial', 'anio': 2024,
     'que': ('Lo que la Auditoría Superior de la Federación dejó por aclarar al gobierno de cada estado al revisar el dinero federal de la Cuenta Pública 2024 '
             '(sin sus municipios ni lo que la ASF agrupa como «Otros»). No es un desfalco comprobado: es lo que no tenía papeles al cerrar la auditoría.')},
    {'id': 'apM', 'dim': 'administracion', 'fmt': 'mdp', 'nom': 'Lo que ejercieron sus municipios', 'pal': 'verde', 'est': 'oficial', 'anio': 2024,
     'que': ('El presupuesto que ejercieron en 2024 las administraciones de los municipios de cada estado (en la Ciudad de México, sus alcaldías), '
             'según el censo municipal del INEGI. Algunos municipios no contestaron.')},
    {'id': 'apA', 'dim': 'administracion', 'fmt': 'mdp', 'nom': 'ASF · Por aclarar de sus municipios', 'pal': 'rojo', 'est': 'oficial', 'anio': 2024,
     'que': ('Lo que la ASF dejó por aclarar a los municipios de cada estado por el dinero federal que recibieron (Cuenta Pública 2024). '
             'La ASF solo revisa a una parte de los municipios cada año, y su dinero propio lo revisa la entidad de fiscalización del estado.')},
    # La dimensión ambiental (03-11-2026): los recursos naturales, empezando
    # por las refinerías de PEMEX (recursos_naturales.py). Un estado sin
    # refinería va en gris como «sin refinería», nunca como «sin problema».
    {'id': 'acuP', 'dim': 'ambiental', 'fmt': 'pct', 'nom': 'Acuíferos sin agua para concesionar', 'pal': 'rojo', 'est': 'derivado', 'anio': 'corte dic 2022',
     'que': ('De cada 100 acuíferos de la entidad, cuántos no tenían disponibilidad: en el papel ya se comprometió más agua de la que se recarga. '
             'No es el agua que queda en el subsuelo ni su calidad, y no es lo mismo que «sobreexplotado». La división es nuestra.')},
    {'id': 'acuD', 'dim': 'ambiental', 'fmt': 'hm3', 'nom': 'Suma de sus déficits de agua', 'pal': 'rojo', 'est': 'derivado', 'anio': 'corte dic 2022',
     'que': ('Los millones de metros cúbicos al año que faltan en sus acuíferos en déficit, sumados. Un estado con muchos acuíferos grandes sale más alto; '
             'cero quiere decir que ninguno estaba en déficit, no que su agua esté limpia.')},
    {'id': 'sfT', 'dim': 'ambiental', 'fmt': 'ha', 'nom': 'Superficie forestal', 'pal': 'verde', 'est': 'oficial', 'anio': 'mapa de 2018',
     'que': ('Las hectáreas de vegetación forestal de cada entidad según la CONAFOR, con el mapa de uso del suelo de 2018 del INEGI. «Forestal» no es «bosque»: '
             'incluye matorrales y otras áreas, y en el norte el matorral es la mayor parte. No resta el desmonte de después de 2018.')},
    {'id': 'incP', 'dim': 'ambiental', 'fmt': 'pct', 'nom': 'Lo que el fuego de 2025 afectó, frente a su superficie forestal', 'pal': 'rojo', 'est': 'derivado', 'anio': 2025,
     'que': ('La superficie afectada por los incendios de 2025 ÷ la superficie forestal de la entidad × 100. Es una proporción con años distintos (el fuego de 2025, el mapa de 2018), '
             'no la parte del bosque que se perdió: casi todo lo afectado es pasto y matorral. La división es nuestra.')},
    {'id': 'peT', 'dim': 'ambiental', 'fmt': 't', 'nom': 'Pesca y acuacultura', 'pal': 'azul', 'est': 'oficial', 'anio': 2025,
     'que': ('Las toneladas en peso vivo que registró cada entidad en 2025, de captura y de cultivo, según el Anuario de la CONAPESCA. Es lo que se declaró en los avisos de arribo '
             'y de cosecha, no todo lo que se pescó, y no dice si las especies aguantan: eso lo dice la Carta Nacional Pesquera.')},
    {'id': 'peV', 'dim': 'ambiental', 'fmt': 'mdp', 'nom': 'Valor de su pesca', 'pal': 'azul', 'est': 'oficial', 'anio': 2025,
     'que': ('Lo que valió en 2025 lo que registró cada entidad, a precio de playa (la primera venta), en millones de pesos de ese año, sin descontar la inflación. '
             'Mucho volumen no es mucho valor: depende de qué se pesca.')},
    {'id': 'incH', 'dim': 'ambiental', 'fmt': 'ha', 'nom': 'Superficie afectada por incendios forestales', 'pal': 'rojo', 'est': 'oficial', 'anio': 2025,
     'que': ('Las hectáreas que afectaron los incendios forestales de cada entidad en 2025, según el cierre de la CONAFOR. Superficie afectada no es bosque perdido: '
             'en el país, 95 de cada 100 hectáreas fueron de pasto, matorral y hojarasca.')},
    {'id': 'incN', 'dim': 'ambiental', 'fmt': 'n', 'nom': 'Incendios forestales', 'pal': 'rojo', 'est': 'oficial', 'anio': 2025,
     'que': ('Cuántos incendios forestales tuvo cada entidad en 2025. Muchos incendios no es mucha superficie: la que más tuvo no es la que más terreno perdió.')},
    {'id': 'minT', 'dim': 'ambiental', 'fmt': 'n', 'nom': 'Concesiones mineras', 'pal': 'oro', 'est': 'oficial', 'anio': 'marzo 2024',
     'que': ('Los títulos de concesión minera vigentes en cada entidad, según la Dirección General de Minas. Una concesión da derecho a explorar y explotar; '
             'no quiere decir que ya haya una mina trabajando.')},
    {'id': 'minH', 'dim': 'ambiental', 'fmt': 'ha', 'nom': 'Hectáreas concesionadas', 'pal': 'oro', 'est': 'oficial', 'anio': 'marzo 2024',
     'que': ('El terreno que amparan esas concesiones, en hectáreas. Es la superficie del título, no la excavada: el tajo y las presas de jales no se miden aquí.')},
    {'id': 'refj', 'dim': 'ambiental', 'fmt': 'mbd', 'nom': 'Crudo que procesó su refinería', 'pal': 'oro', 'est': 'oficial', 'anio': 'junio 2026',
     'que': ('Los barriles diarios de petróleo crudo que procesó en junio de 2026 la refinería de PEMEX de cada entidad, en miles. Siete entidades tienen una; '
             'las demás van en gris porque no tienen refinería, no porque no tengan problemas ambientales: sus acuíferos, sus bosques, sus incendios y sus minas tienen su lente.')},
    {'id': 'refp', 'dim': 'ambiental', 'fmt': 'mbd1', 'nom': 'Su promedio de diez meses', 'pal': 'oro', 'est': 'derivado', 'anio': 'sep-25 a jun-26',
     'que': ('El promedio de los diez meses de septiembre de 2025 a junio de 2026: corrige un mes malo por mantenimiento. Es la media aritmética de las diez cifras mensuales del Informe; '
             'la cuenta es nuestra.')},
    {'id': 'refu', 'dim': 'ambiental', 'fmt': 'pct', 'nom': 'Cuánto usa de su capacidad', 'pal': 'oro', 'est': 'derivado', 'anio': 'sep-25 a jun-26',
     'que': ('El promedio de los diez meses entre la capacidad de destilación de la refinería al cierre de 2024, × 100. Dice cuánto usa, no por qué: '
             'falta de crudo, mantenimiento o una planta que no arranca se ven igual.')},
    # «Obras con alerta ambiental» (04-11-2026): el conteo del mapa de la
    # Enciclopedia, que sale del mapa ambiental de megaobras. Un conteo de 0 a
    # 3 no se parte en quintiles: va por número (cortes fijos).
    {'id': 'obr', 'dim': 'ambiental', 'fmt': 'n', 'nom': 'Obras con alerta ambiental', 'pal': 'verde', 'est': 'derivado', 'anio': 'conteo nuestro',
     'cortes': [1, 2, 3, 4], 'que': tm.QUE_OBRAS},
]


def _fuentes(ref, base=None):
    import recursos_naturales as rn
    extra = {}
    if base is not None:
        E = base['estados']
        doc, pagina = _sda(base)
        sda = '%s %s (<a href="%s">archivo de variables por entidad, XLSX</a>; huella SHA-256 <code>%s…</code>; <a href="%s">página oficial</a>).' % (
            sorted(set(e['deudaFuente'] for e in E), key=len)[0], ref('ref-shcp-alertas'), doc['url'], doc['sha256'][:12], pagina)
        ind = (' Las tres mediciones y su resultado (sostenible, en observación o elevado) las define el Reglamento del Sistema de Alertas; '
               'el archivo las publica por entidad.')
        C = base['fiscalEntidades']['campos']
        extra = {'inv': '%s %s.' % (C['invPub']['fuente'], ref(C['invPub']['ref'])),
                 'invt': '%s %s.' % (C['invInfra']['fuente'], ref(C['invInfra']['ref'])),
                 'invp': 'Inversión pública ÷ total de egresos del gobierno del estado en 2024 × 100; los dos del INEGI, finanzas públicas estatales %s. La división es nuestra.' % ref(C['egr2024']['ref']),
                 'asf': '%s %s.' % (E[0]['asfFuente'], ref('ref-asf-mdb2024')),
                 'cua': tm.fuente_cuadre(ref),
                 'deuda': sda, 'ild': sda + ind, 'sd': sda + ind, 'ocp': sda + ind,
                 'dpc': ('Deuda al cierre de 2025 (Sistema de Alertas %s) ÷ población a mitad de 2026 (CONAPO). La división es nuestra; '
                         'los años no coinciden porque es la deuda que hereda quien vive hoy en el estado.') % ref('ref-shcp-alertas')}
        cn = 'INEGI, Censo Nacional de Poderes Legislativos Estatales 2025'
        extra.update({
            'leg': '%s, gasto ejercido en 2024 por congreso, p. 11 %s.' % (cn, ref('ref-inegi-cnple2025')),
            'legn': '%s, personas legisladoras en activo, tabla 8, p. 32 %s.' % (cn, ref('ref-inegi-cnple2025')),
            'legx': 'Gasto ejercido en 2024 (p. 11) ÷ personas legisladoras en activo (tabla 8), los dos del %s %s. La división es nuestra.' % (cn, ref('ref-inegi-cnple2025')),
            'legp': ('Gasto del congreso en 2024 (%s, p. 11) ÷ total de egresos del gobierno del estado en 2024 (INEGI, finanzas públicas estatales %s) × 100. La división es nuestra. '
                     'El tope: Constitución, art. 116, fr. II, párrafo segundo, y transitorios quinto y octavo del decreto del DOF 23-04-2026 %s.') % (
                         cn, ref(C['egr2024']['ref']), ref('ref-cpeum')),
        })
        cj = 'INEGI, Censo Nacional de Impartición de Justicia Federal y Estatal 2025, reporte de resultados'
        rj = ref('ref-inegi-cnijfe2025-rr')
        extra.update({
            'jud': '%s, presupuesto ejercido por cada poder judicial estatal en 2024, gráfica 7, p. 14 %s.' % (cj, rj),
            'judc': ('Asuntos concluidos ÷ asuntos ingresados en primera instancia en 2024 × 100 (%s, tabla 23, p. 39, con sus notas 1 y 2 sobre qué cuenta cada uno) %s. '
                     'La división es nuestra.') % (cj, rj),
            'juda': 'Presupuesto ejercido en 2024 (gráfica 7, p. 14) ÷ asuntos concluidos en primera instancia (tabla 23, p. 39), los dos del %s %s. La división es nuestra.' % (cj, rj),
            'judr': '%s, causas penales del sistema acusatorio pendientes de concluir al cierre de 2024, tabla 25 y su nota 3, p. 45 %s.' % (cj, rj),
            'judj': '%s, personas juzgadoras de cada poder judicial estatal, tabla 6, p. 12 %s.' % (cj, rj),
        })
        import gestion_salud as gsal
        mem = ('IMSS, Memoria Estadística 2025, %s, por OOAD (<a href="%s">Memoria</a>; archivo de Excel del capítulo, huella SHA-256 <code>%s…</code>). '
               'La Ciudad de México, el Estado de México y Veracruz tienen dos OOAD cada uno: su suma es nuestra')
        dg = gsal.fuente_dgis()
        sp = gsal._estados_doc()['dgis']['sinPersonal']
        dgis = ('Secretaría de Salud, Dirección General de Información en Salud, Recursos en Salud Sectorial 2025, establecimientos del %s por entidad (<a href="%s">datos abiertos, ZIP</a>; '
                'huella SHA-256 <code>%s…</code>). La suma por entidad es nuestra; el total de establecimientos cuadra con la nota de cierre de la DGIS')
        def _mem(cuadro, cap):
            return mem % (cuadro, gsal.MEMORIA, gsal.MEM[cap]['sha256'][:12])
        extra.update({
            'imA': _mem('cuadro II.10 «Población derechohabiente adscrita a unidad de medicina familiar»', 'II') + '.',
            'imQ': _mem('cuadro IV.5 «Hospitalización», columna de intervenciones quirúrgicas de 2025', 'IV') + '.',
            'imX': 'Consultas de 2025 (%s) ÷ población adscrita (%s). La división es nuestra.' % (_mem('cuadro IV.3', 'IV'), _mem('cuadro II.10', 'II')),
            'imK': 'Camas censables (%s) ÷ población adscrita (%s) × 1,000. La división es nuestra.' % (_mem('cuadro XIII.11', 'XIII'), _mem('cuadro II.10', 'II')),
            'isM': (dgis % ('ISSSTE', html.escape(dg['url']), dg['sha256'][:12])) + ', columna «Total médicos generales especialistas y odontólogos». El ISSSTE no le reportó personal de %d establecimientos.' % sp['issste'],
            'isK': (dgis % ('ISSSTE', html.escape(dg['url']), dg['sha256'][:12])) + ', columna «Total camas área hospitalización».',
            'isU': (dgis % ('ISSSTE', html.escape(dg['url']), dg['sha256'][:12])) + '.',
            'imM': (dgis % ('IMSS', html.escape(dg['url']), dg['sha256'][:12])) + ', columna «Total médicos generales especialistas y odontólogos». El IMSS no le reportó personal de %d establecimientos.' % sp['imss'],
        })
        import administracion_publica as apu
        cg_ = '%s (<a href="%s">PDF</a>; huella SHA-256 <code>%s…</code>)' % (html.escape(apu.CNGE['tx']), apu.CNGE['url'], apu.CNGE['sha256'][:12])
        cm_ = '%s (<a href="%s">PDF</a>; huella SHA-256 <code>%s…</code>)' % (html.escape(apu.CNGMD['tx']), apu.CNGMD['url'], apu.CNGMD['sha256'][:12])
        fa = apu.fuente_asf(base)
        asf_ = '%s (<a href="%s">PDF</a>) %s' % (html.escape(fa['tx']), html.escape(fa['url']), ref('ref-asf-mdb2024'))
        extra.update({
            'apP': '%s, tabla 3 «Personal adscrito… según entidad federativa», p. 8. Las tablas suman los totales del texto del reporte.' % cg_,
            'apK': 'Personal (%s, tabla 3, p. 8) ÷ población de la entidad × 1,000. La división es nuestra.' % cg_,
            'apX': '%s, gráfica 5 «Presupuesto ejercido… según entidad federativa», p. 11, pesos corrientes.' % cg_,
            'apD': '%s, tabla 9 «Contratos… según entidad federativa y tipo de procedimiento», p. 31. %s' % (cg_, html.escape(apu.CONTRATOS_NOTA)),
            'apG': '%s, renglón «Gobierno del Estado» de cada entidad.' % asf_,
            'apM': '%s, gráfica 23 «Presupuesto ejercido… según entidad federativa», p. 26, pesos corrientes.' % cm_,
            'apA': '%s, renglón «Municipios» de cada entidad.' % asf_,
        })
    inf = ('Presidencia de la República, Segundo Informe de Gobierno 2025-2026, gráfica «Procesamiento de petróleo crudo en el Sistema Nacional de Refinación 2025-2026», '
           'p. 378, elaborada por la SENER con la Base de Datos Institucional de PEMEX %s') % ref('ref-presidencia-2ig')
    ae = ('PEMEX, Anuario Estadístico 2024, cuadro 3.6 «Capacidad de proceso por refinería, 2024», p. 48 (<a href="%s">PDF</a>; huella SHA-256 <code>%s…</code>)') % (
        html.escape(rn.AE['url']), rn.AE['sha256'][:12])
    pr = ('Secretaría de Economía, Prontuario Estadístico de la Minería enero-junio 2025, cuadro «Número de concesiones mineras y superficie por Entidad Federativa 2024», p. 20, '
          'con fuente «DGM, marzo 2024» (<a href="%s">PDF</a>; huella SHA-256 <code>%s…</code>). El cuadro trae 30 entidades.') % (html.escape(rn.PRONT['url']), rn.PRONT['sha256'][:12])
    extra.update({'refj': inf + '.', 'refp': inf + '. Promedio de los diez meses (media aritmética): la cuenta es nuestra.',
                  'refu': 'Promedio de los diez meses (%s) ÷ capacidad de destilación atmosférica al cierre de 2024 (%s) × 100. La división es nuestra.' % (inf, ae),
                  'minT': pr, 'minH': pr})
    aq = ('Comisión Nacional del Agua, Acuerdo por el que se actualiza la disponibilidad media anual de agua subterránea de los 653 acuíferos, DOF 09-11-2023, artículo primero, '
          'con corte al 30 de diciembre de 2022 (<a href="%s">DOF</a>; sus tablas, copiadas en <code>%s</code>, huella SHA-256 <code>%s…</code>)') % (
        html.escape(rn.ACU['url']), rn.ACU['archivo'].split('/')[-1], rn.ACU['sha256'][:12])
    extra.update({'acuP': 'Acuíferos con disponibilidad negativa ÷ acuíferos de la entidad × 100, con el %s. La división es nuestra.' % aq,
                  'acuD': 'Suma de la disponibilidad negativa (déficit) de los acuíferos de la entidad, con el %s. La suma es nuestra.' % aq})
    ic = ('Comisión Nacional Forestal, Gerencia de Manejo del Fuego, Cierre estadístico 2025, cuadro 4 «Incendios y superficie con información acumulada» '
          '(<a href="%s">PDF</a>; huella SHA-256 <code>%s…</code>)') % (html.escape(rn.INC_DOC['url']), rn.INC_DOC['sha256'][:12])
    sf = ('Comisión Nacional Forestal, «Estado que guarda el sector forestal en México 2023», tabla 1 «Superficie forestal por tipo de vegetación a nivel estatal», p. 4, con el '
          'Inventario Nacional Forestal y de Suelos 2015-2020 y la Serie VII de uso del suelo del INEGI, 2018 (<a href="%s">PDF</a>; huella SHA-256 <code>%s…</code>)') % (
        html.escape(rn.SF_DOC['url']), rn.SF_DOC['sha256'][:12])
    pe = ('Comisión Nacional de Acuacultura y Pesca, Anuario Estadístico de Acuacultura y Pesca 2025, cuadros 2.5.6 «Serie histórica de la producción pesquera nacional en peso vivo» '
          'y 2.5.12 «Serie histórica del valor de la producción pesquera», pp. 171 y 177 (<a href="%s">PDF</a>; huella SHA-256 <code>%s…</code>)') % (
        html.escape(rn.PE_DOC['url']), rn.PE_DOC['sha256'][:12])
    import dimension_social as dso
    so_f, so_p = dso.fuente()
    soc = ('%s (<a href="%s">presentación de resultados</a>; cada estado con su infografía y su huella SHA-256 en <code>docs/social/pobreza-entidades-2024.json</code>)') % (so_f, so_p)
    extra.update({'soP': soc + '.', 'soX': soc + '. Donde la cifra es baja, el INEGI la marca con coeficiente de variación moderado o bajo.', 'soI': soc + '.',
                  'soS': soc + '.', 'soA': soc + '.', 'soR': soc + '.',
                  'soN': 'Porcentaje en pobreza × población de la misma infografía (%s). La multiplicación es nuestra.' % soc})
    if base is not None:
        C = base['fiscalEntidades']['campos']
        extra['soQ'] = ('Aportaciones de 2026 (%s %s) ÷ personas en pobreza de 2024 (%s). La división es nuestra, y junta dos años: '
                        'el INEGI mide la pobreza cada dos años y la de 2026 aún no existe.') % (C['ramo33']['fuente'], ref(C['ramo33']['ref']), soc)
    extra['obr'] = tm.FUENTE_OBRAS
    extra.update({'peT': pe + '.', 'peV': pe + '. Miles de pesos ÷ 1,000: la cuenta es nuestra.'})
    extra.update({'incH': ic + '.', 'incN': ic + '.', 'sfT': sf + '.',
                  'incP': 'Superficie afectada por los incendios de 2025 (%s) ÷ superficie forestal (%s) × 100. La división es nuestra.' % (ic, sf)})
    return dict(extra, **{
        'fed': 'Ramo 28: Anexo 15 del acuerdo de distribución (DOF 12-12-2025) %s. Ramo 33: Anexo 16, versión modificada (DOF 09-07-2026) %s. La suma de los dos es nuestra.' % (
            ref('ref-dof-distribucion-2026'), ref('ref-dof-distribucion-2026-mod')),
        'est': 'Suma de impuestos, cuotas de seguridad social, contribuciones de mejoras, derechos, productos y aprovechamientos de 2024. INEGI, finanzas públicas estatales, cifras definitivas %s.' % ref('ref-inegi-efipem-estatal'),
        'mun': 'Suma de los ingresos de 2024 de cada municipio que rindió su cuenta. INEGI, finanzas públicas municipales (EFIPEM), cifras definitivas %s. Los que no rindieron cuenta no se cuentan en cero: quedan sin cifra.' % ref('ref-inegi-efipem'),
    })


def matriz():
    """El Planisferio es la matriz de los mapas (04-11-2026): cada lente del
    mapa de la Enciclopedia que dice vivir aquí (PLANISFERIO de
    territorio_modulos.py) apunta a una dimensión que se pinta y a una lente
    suya. Si no, la generación se detiene: una liga del chat o de la
    Enciclopedia abriría el Planisferio en el lugar equivocado."""
    pinta = {i for i, *_r, p in DIMENSIONES if p}
    lentes = {l['id']: l['dim'] for l in LENTES}
    malos = ['%s → %s/%s' % (k, d, l) for k, (d, l) in list(tm.PLANISFERIO.items()) + list(tm.OTROS_MAPAS.items())
             if d not in pinta or (l and lentes.get(l) != d)]
    if malos:
        raise SystemExit('planisferio: el mapa de la Enciclopedia apunta a dimensiones o lentes que no existen: ' + '; '.join(malos))
    return {d for d, _ in tm.PLANISFERIO.values()}


def pagina_mapa(base, ref, tres, padron, cuenta, cuanto='', origenes=''):
    matriz()
    filas = _datos(base, padron)
    F = base['panoramaErario']['federalizado']
    s = {x['id']: x for x in tres['sale']}
    nac = padron['nacional']
    tot = tres['total']

    def des_tres(x):
        filas = [(f['n'], ('%.1f pts. del PIB' % f['pib']) if 'pib' in f else mdp(f['v']), '') for f in x['filas']]
        return ('<section class="glos-drawer-sec"><h4>De cada $100 del presupuesto</h4><p><b class="num-tabular">$%.2f</b> %s '
                '(%s ÷ %s, el total del Presupuesto de Egresos 2026).</p></section>'
                '<section class="glos-drawer-sec"><h4>En qué se va</h4>%s<p>%s</p></section>'
                '<section class="glos-drawer-sec"><h4>Fuente</h4><p class="glos-drawer-ley">%s</p></section>') % (
                    x['v'] / tot * 100, chip('derivado'), mdp(x['v']), mdp(tot), _filas(filas), x['op'],
                    ' '.join(ref(f['url'].split('#')[1]) + ' ' + f['t'] for f in x['f']))
    comp = F['componentes']
    if abs(sum(c['montoMdp'] for c in comp) - F['totalMdp']) > 0.5:
        raise SystemExit('planisferio: los componentes del gasto federalizado no suman su total')
    des_fed = ('<section class="glos-drawer-sec"><h4>Por los cuatro ramos</h4>%s<p>%s</p></section>'
               '<section class="glos-drawer-sec"><h4>Fuente</h4><p class="glos-drawer-ley">Presupuesto de Egresos de la Federación 2026, Anexo 1 %s.</p></section>') % (
                   _filas([(c['nombre'], mdp(c['montoMdp']), chip(c['estado'])) for c in comp]),
                   F['nota'], ref('ref-pef2026'))
    m = lambda k: nac[k] / 1e6
    resto = nac['ing'] - nac['part'] - nac['aport'] - nac['propios']
    if resto < 0:
        raise SystemExit('planisferio: participaciones, aportaciones y lo propio pasan del ingreso municipal')
    des_mun = ('<section class="glos-drawer-sec"><h4>De dónde vino</h4>%s<p>Lo demás es el ingreso total menos las otras tres '
               '(%s − %s − %s − %s), como derivado.</p></section>'
               '<section class="glos-drawer-sec"><h4>Fuente</h4><p class="glos-drawer-ley">INEGI, finanzas públicas municipales %d, cifras definitivas %s. '
               'Faltan los municipios que no rindieron cuenta y las alcaldías de la Ciudad de México %s.</p></section>') % (
                   _filas([('Participaciones (Ramo 28)', mdp(m('part')), chip('derivado')),
                           ('Aportaciones (Ramo 33)', mdp(m('aport')), chip('derivado')),
                           ('· de ellas, del FORTAMUN', mdp(m('fortamun')), chip('derivado')),
                           ('· de ellas, del FAIS municipal', mdp(m('fismdf')), chip('derivado')),
                           ('Lo que cobraron por su cuenta', mdp(m('propios')), chip('derivado')),
                           ('· de ello, predial', mdp(m('predial')), chip('derivado')),
                           ('Lo demás de su ingreso', mdp(resto / 1e6), chip('derivado'))]),
                   mdp(m('ing')), mdp(m('part')), mdp(m('aport')), mdp(m('propios')),
                   padron['anio'], ref('ref-inegi-efipem'), chip('pendiente', 'municipios-sin-cuenta'))
    contadores = ''.join([
        _contador('estado', '🏛️', 'Presupuesto del Estado', s['estado']['v'], s['estado']['est'], s['estado']['que'],
                  'Criterios 2027, clasificación funcional %s.' % ref('ref-cgpe2027'), des_tres(s['estado'])),
        _contador('nacional', '🏗️', 'Presupuesto nacional', s['nacional']['v'], s['nacional']['est'], s['nacional']['que'],
                  'Criterios 2027, clasificación funcional %s.' % ref('ref-cgpe2027'), des_tres(s['nacional'])),
        _contador('social', '🫂', 'Presupuesto social', s['social']['v'], s['social']['est'], s['social']['que'],
                  'Criterios 2027, clasificación funcional %s.' % ref('ref-cgpe2027'), des_tres(s['social'])),
        _contador('fed', '📍', 'Gasto federalizado', F['totalMdp'], 'oficial',
                  'Lo que la Federación transfiere a estados y municipios en 2026, por los cuatro ramos.',
                  'Presupuesto de Egresos de la Federación 2026 %s.' % ref('ref-pef2026'), des_fed),
        _contador('mun', '🏘️', 'Lo que ingresaron los municipios', round(nac['ing'] / 1e6, 1), 'derivado',
                  'La suma de los ingresos de 2024 de los %s municipios que rindieron su cuenta, de %s en el catálogo.' % (
                      format(padron['conCifra'], ','), format(padron['catalogo'], ',')),
                  'INEGI, finanzas públicas municipales 2024 %s.' % ref('ref-inegi-efipem'), des_mun),
    ])
    cuenta_btn = ('<button type="button" class="pl-cuenta-b" data-cajon="plTplCuenta" data-cajon-tit="plTplCuentaTit" data-cajon-hash="cuenta" aria-haspopup="dialog">'
                  '🧮 La cuenta completa: los tres presupuestos, lo ya comprometido y los fondos</button><template id="plTplCuenta">%s</template>') % _cajon(
        '🧮', 'La cuenta completa', 'Los tres presupuestos de 2026', 'plTplCuentaTit', cuenta,
        '<a class="glos-drawer-todo" href="numeros-gasto-tres-presupuestos.html" style="text-align:center; text-decoration:none;">📚 Verlo en la Enciclopedia ➔</a>',
        'Enciclopedia · Números · Gasto público')
    # «Cuánto dinero es» y «Los 16 orígenes del ingreso» (pedido del autor,
    # 03-11-2026): las mismas funciones de la Enciclopedia. Desde el rediseño
    # del mismo día van integradas en la dimensión financiera, no en ventana.
    modulos = []
    for ico, marca, tit, cuerpo, href in (
            ('💰', 'Cuánto dinero es', 'El total de 2026 y lo que baja al territorio', cuanto, 'numeros-cuanto-dinero-es.html'),
            ('🧾', 'Los 16 orígenes del ingreso', 'De dónde sale cada peso de 2026', origenes, 'numeros-los-16-origenes.html')):
        if not cuerpo:
            continue
        if not _existe(href):
            raise SystemExit('planisferio: «%s» apunta a %s, que no existe' % (marca, href))
        modulos.append('<article class="pl-fin-mod"><h3><span aria-hidden="true">%s</span> %s</h3><p class="pl-fin-sub">%s</p>%s'
                       '<p class="pl-ficha-ir"><a href="%s">📚 Verlo en la Enciclopedia ➔</a></p></article>' % (ico, marca, tit, cuerpo, href))
    dims = []
    for k, (i, ico, nom, que, ir, _ire, pinta) in enumerate(DIMENSIONES):
        if ir and not _existe(ir):
            raise SystemExit('planisferio: la dimensión %s apunta a %s, que no existe' % (i, ir))
        if pinta and not any(l['dim'] == i for l in LENTES):
            raise SystemExit('planisferio: la dimensión %s se pinta pero no tiene lentes' % i)
        # Rediseño del 04-11-2026: las nueve dimensiones son un mosaico de
        # color (su color es el del tablero del mapa cuando se eligen).
        nl = sum(1 for l in LENTES if l['dim'] == i)
        dims.append('<button type="button" class="pl-dim%s" role="tab" aria-selected="%s" aria-controls="plTablero" data-dim="%s">'
                    '<span class="pl-dim-ico" aria-hidden="true">%s</span><span class="pl-dim-n">%s</span>'
                    '<small>%s</small></button>' % (
                        '' if pinta else ' pl-dim-prox', 'true' if k == 0 else 'false', i,
                        ico, nom, ('%d %s' % (nl, 'lente' if nl == 1 else 'lentes')) if pinta else 'Próximamente'))
    otras = ''.join('<li><span aria-hidden="true">%s</span> <b>%s.</b> %s <a href="%s">Ya está en la Enciclopedia ➔</a></li>' % (
        ico, nom, que, ir) for _, ico, nom, que, ir, _, pinta in DIMENSIONES if ir and not pinta)
    pintadas = [d for d in DIMENSIONES if d[6]]
    primera = {}
    for l in LENTES:
        primera.setdefault(l['dim'], l['id'])
    lentes = ''.join('<button type="button" class="pl-lente" role="radio" aria-checked="%s" data-l="%s" data-dim="%s"%s>%s</button>' % (
        'true' if primera[l['dim']] == l['id'] else 'false', l['id'], l['dim'],
        '' if l['dim'] == DIMENSIONES[0][0] else ' hidden', l['nom']) for l in LENTES)
    fu = _fuentes(ref, base)
    sin_est = [f['a'] for f in filas if f['est'] is None]
    sin_mun = [f['a'] for f in filas if f['mun'] is None]
    no_med = [f['a'] for f in filas if f['ild'] is None]
    nombre = {f['a']: f['n'] for f in filas}
    # Lo que no tiene cifra en cada lente, con su porqué: un pendiente lleva
    # su ficha; lo que no se mide por ley no es pendiente, y se dice así.
    falta = {
        'est': {'a': sin_est, 'gris': 'sin cifra', 'pend': 'entidades-' + '-'.join(sin_est).lower(),
                'txt': 'La Ciudad de México no figura en la estadística estatal del INEGI.'},
        'mun': {'a': sin_mun, 'gris': 'sin cifra', 'pend': 'municipios-sin-cuenta',
                'txt': 'Las alcaldías de la Ciudad de México no rinden cuenta municipal al INEGI.'},
    }
    for i in ('ild', 'sd', 'ocp'):
        falta[i] = {'a': no_med, 'gris': 'no se mide', 'pend': None,
                    'txt': ('%s no se mide: no tiene deuda inscrita en el Registro Público Único, y el Sistema de Alertas solo evalúa a quien '
                            'la tiene (Ley de Disciplina Financiera, art. 43). Hacienda no le publica semáforo.') % ' ni '.join(nombre[a] for a in no_med)}
    sin_inv = [f['a'] for f in filas if f['inv'] is None]
    for i in ('inv', 'invp', 'invt'):
        falta[i] = {'a': sin_inv, 'gris': 'sin cifra', 'pend': 'entidades-' + '-'.join(sin_inv).lower(),
                    'txt': 'La Ciudad de México no figura en la estadística estatal del INEGI: su inversión sigue pendiente.'}
    sin_cua = [f['a'] for f in filas if f['cua'] is None]
    falta['cua'] = {'a': sin_cua, 'gris': 'sin cifra', 'pend': 'entidades-' + '-'.join(sin_cua).lower(),
                    'txt': 'La Ciudad de México no figura en la estadística estatal del INEGI: no hay segunda cifra con que contrastar.'}
    sin_egr = [f['a'] for f in filas if f['legp'] is None]
    falta['legp'] = {'a': sin_egr, 'gris': 'sin cifra', 'pend': 'entidades-' + '-'.join(sin_egr).lower(),
                     'txt': 'La Ciudad de México no figura en la estadística estatal del INEGI: sin su egreso total no se puede hacer la división, aunque su congreso sí reportó su gasto.'}
    nota_leg = _nota_leg(filas)
    nota_jud = _nota_jud(filas)
    nota_amb = _nota_amb(filas)
    nota_sal = _nota_sal(filas)
    nota_apu = _nota_apu(filas)
    nota_soc = _nota_soc(filas)
    sin_ref = [f['a'] for f in filas if f['refj'] is None]
    for i in ('refj', 'refp', 'refu'):
        falta[i] = {'a': sin_ref, 'gris': 'sin refinería de PEMEX', 'pend': None,
                    'txt': ('%d entidades no tienen refinería de PEMEX: van en gris por eso, no porque no tengan problemas ambientales. Sus acuíferos, sus bosques, sus incendios forestales y sus concesiones mineras '
                            'tienen su lente.') % len(sin_ref)}
    sin_pe = [f['a'] for f in filas if f['peT'] is None]
    for i in ('peT', 'peV'):
        falta[i] = {'a': sin_pe, 'gris': 'no registró en 2025', 'pend': None,
                    'txt': ('%s no registró producción pesquera ni acuícola en 2025 en el Anuario de la CONAPESCA. Va en gris por eso: no registrar no es lo mismo que no tener pesca, '
                            'porque el Anuario es lo que se declaró en los avisos de arribo y de cosecha.') % ' y '.join(nombre[a] for a in sin_pe)}
    sin_min = [f['a'] for f in filas if f['minT'] is None]
    for i in ('minT', 'minH'):
        falta[i] = {'a': sin_min, 'gris': 'no figura en el cuadro', 'pend': None,
                    'txt': ('%s no figuran en el cuadro de concesiones mineras por entidad de la Dirección General de Minas, que trae 30 entidades. No quiere decir que no se extraiga '
                            'nada de su suelo: la Ley de Minería no se aplica a la grava, la arena y las rocas para construir (art. 5, fr. IV).') % ' y '.join(nombre[a] for a in sin_min)}
    # El punto ciego de la inversión: el capítulo de inversión pública, solo,
    # hace ver «sin obra» a quien la hace por medio de sus organismos.
    con_inv = [f for f in filas if f['inv'] is not None]
    mas = sorted((f for f in con_inv if f['invt'] > f['inv']), key=lambda f: -(f['invt'] / max(f['inv'], 0.1)))
    nota_inv = ('<b>Lo que el capítulo de obra no dice.</b> Un gobierno estatal hace obra por dos vías: la que contrata él mismo (su capítulo de inversión pública) '
                'y la que les encarga a sus organismos de infraestructura, a los que les pasa dinero como transferencia. En %d de las %d entidades con cifra, '
                'lo que pasó a esos organismos fue más que su obra directa. %s hizo obra directa por %s %s y les pasó %s %s a sus organismos: '
                'en el mapa de la obra directa sale en el lugar %d de %d. Por eso aquí van las dos lentes, separadas: lo de los organismos también paga su nómina y su operación, '
                'así que sumarlas inflaría la obra.') % (
                    len(mas), len(con_inv), mas[0]['n'], mdp(mas[0]['inv']), chip('oficial'), mdp(mas[0]['invt']), chip('oficial'),
                    sorted(con_inv, key=lambda f: -f['inv']).index(mas[0]) + 1, len(con_inv))
    # El punto ciego del semáforo: si todas comparten color, el color no
    # distingue a la más endeudada de la menos. Se dice con las cifras.
    med = sorted((f for f in filas if f['ild'] is not None), key=lambda f: -f['ild'])
    sems = sorted(set(f['sem'] for f in med))
    nota_deuda = ('<b>%s.</b> El semáforo de Hacienda pone a las %d que mide en «%s»%s. Ese color junta a %s, que debe el equivalente a %s de sus ingresos de libre disposición, '
                  'con %s, que debe %s %s. Por eso el mapa no colorea por semáforo, sino por cifra: el verde quiere decir que, con esas tres mediciones, Hacienda considera sostenible su deuda, no que deban poco.' % (
                      'Lo que el semáforo no dice' if len(sems) == 1 else 'El semáforo no lo dice todo',
                      len(med), sems[0].lower() if len(sems) == 1 else ' y '.join(x.lower() for x in sems),
                      ' (%s no se mide: no tiene deuda inscrita, LDF art. 43)' % ' ni '.join(nombre[a] for a in no_med) if no_med else '',
                      med[0]['n'], pct(med[0]['ild']), med[-1]['n'], pct(med[-1]['ild']), chip('oficial')))
    datos = {'lentes': [dict(l, fuente=fu[l['id']], falta=falta.get(l['id'])) for l in LENTES], 'e': filas,
             'dims': {i: {'n': nom, 'q': q, 'ir': ir, 'ire': ire, 'pinta': pinta} for i, _, nom, q, ir, ire, pinta in DIMENSIONES}}
    notas = {'deuda': nota_deuda, 'inversion': nota_inv, 'legislativa': nota_leg, 'judicial': nota_jud, 'ambiental': nota_amb, 'salud': nota_sal, 'administracion': nota_apu, 'social': nota_soc}
    # Lo que antes era un párrafo largo arriba del mapa y una nota debajo
    # (decisión del autor, 03-11-2026: «mucho contenido de narración»): cada
    # dimensión tiene su «Cómo leerla» y su «Lo que el mapa no dice» en la
    # ventana lateral, y la página deja solo las pestañas.
    cuantil = 'El color compara a las 32 por quintiles: cinco grupos con el mismo número de entidades.'
    leer = {
        'financiera': ('Los tres pisos de la hacienda de cada entidad: lo que le baja de la Federación, lo que cobra por su cuenta y lo que ingresan sus municipios. '
                       'La cuarta lente, «No cuadra», pone lo que el estado dice que recibió junto a lo que la Federación dice que le pagó.'),
        'deuda': 'Lo que debe cada gobierno estatal y cuánto le pesa, con los tres indicadores del Sistema de Alertas de Hacienda.',
        'inversion': 'La obra que hace cada gobierno estatal, directa o por medio de sus organismos, y lo que la Auditoría Superior dejó por aclarar.',
        'legislativa': 'Los 32 congresos locales: lo que gastó cada uno, cuánto cuesta por curul y cómo se compara con el tope del 0.70 % de la Constitución.',
        'judicial': 'Los 32 poderes judiciales de los estados: lo que ejerció cada uno junto a lo que concluyó con ese dinero y las causas penales que se le acumulan.',
        'salud': ('El IMSS y el ISSSTE en cada estado. Del IMSS, lo que registra su Memoria Estadística 2025: a cuántas personas tiene adscritas, cuántas consultas y cirugías dio '
                  'y cuántas camas tiene por cada mil. Del ISSSTE, con qué cuenta según el registro de la Secretaría de Salud: médicos, camas y unidades. '
                  'La última lente pone a los médicos del IMSS en ese mismo registro, para comparar las dos con la misma regla.'),
        'social': ('La pobreza en cada estado, como la mide el INEGI con la Encuesta de Ingresos y Gastos de los Hogares 2024 y la metodología del CONEVAL: '
                   'cuántas personas la viven y cuántas en pobreza extrema, cuántas tienen un ingreso que no alcanza y las tres carencias que más pesan '
                   '(seguridad social, servicios de salud y rezago educativo). La última lente pone junto a eso lo que la Federación le aporta a cada estado por persona en pobreza.'),
        'administracion': ('El gobierno que ejecuta, en los tres niveles. De la administración de cada estado, lo que le reportó al censo del INEGI: cuánta gente tiene, '
                           'cuánto ejerció en 2024 y cuántos de sus contratos dio por adjudicación directa. De sus municipios, cuánto ejercieron. Y de los dos, lo que la '
                           'Auditoría Superior de la Federación dejó por aclarar del dinero federal de la Cuenta Pública 2024. La ficha trae además el nivel federal, para comparar.'),
        'ambiental': ('Los recursos naturales: los acuíferos de cada estado y cuántos ya no tienen agua para concesionar, su superficie forestal y sus incendios forestales, '
                      'su pesca y su acuacultura, sus concesiones mineras y las siete refinerías de PEMEX, cuánto crudo procesa cada una frente a su capacidad y cuánto valor '
                      'ganó o perdió en sus libros. En las lentes de refinación, el punto marca la entidad, no el sitio exacto. '
                      'La lente de las obras con alerta ambiental cuenta los proyectos del mapa ambiental de megaobras que tocan cada estado.'),
    }
    cajones, plantillas = [], []
    for k, (i, ico, nom, _q, _ir, _ire, pinta) in enumerate(DIMENSIONES):
        if not pinta:
            continue
        if i not in leer:
            raise SystemExit('planisferio: la dimensión %s se pinta y no dice cómo leerla' % i)
        oculto = '' if k == 0 else ' hidden'
        ls = ''.join('<li>%s</li>' % html.escape(l['nom']) for l in LENTES if l['dim'] == i)
        t = 'plTplLeer-' + i
        cajones.append('<button type="button" class="pl-caj-b" data-dim="%s" data-cajon="%s" data-cajon-tit="%sTit" aria-haspopup="dialog"%s>📏 Cómo leer esta dimensión</button>' % (i, t, t, oculto))
        plantillas.append('<template id="%s">%s</template>' % (t, _cajon(ico, 'Cómo leerla', 'Cómo leer la dimensión «%s»' % nom, t + 'Tit',
            '<section class="glos-drawer-sec"><h4>Qué pinta</h4><p>%s</p></section><section class="glos-drawer-sec"><h4>Qué puedes ver</h4><ul class="pl-des-l">%s</ul>'
            '<p>%s Toca una entidad para ver su ficha; tócala otra vez para entrar a su portal.</p></section>' % (leer[i], ls, cuantil))))
        cajones.append(_ctx_botones(i, oculto))
        if notas.get(i):
            t = 'plTplNota-' + i
            cajones.append('<button type="button" class="pl-caj-b pl-caj-ojo" data-dim="%s" data-cajon="%s" data-cajon-tit="%sTit" aria-haspopup="dialog"%s>👁️ Lo que este mapa no dice</button>' % (i, t, t, oculto))
            plantillas.append('<template id="%s">%s</template>' % (t, _cajon('👁️', 'Puntos ciegos', 'Lo que el mapa no dice · %s' % nom, t + 'Tit',
                '<section class="glos-drawer-sec"><p>%s</p></section>' % notas[i])))
    svg = tm.mapa_svg(RAIZ).replace('tt-svg', 'pl-svg').replace('tt-edo', 'pl-edo').replace(
        'aria-label="Mapa de las 32 entidades"', 'aria-label="Planisferio: las 32 entidades de México"')
    indice = ''.join('<li><a href="%s">%s</a></li>' % (f['p'], f['n']) for f in sorted(filas, key=lambda x: clave(x['n'])))
    # Rediseño del 04-11-2026 (pedido del autor: «nuestro protagonista debe ser
    # nuestro mapa interactivo»): cómo se juega en tres pasos, el mosaico de
    # dimensiones, el mapa en su tablero (con lo de leerla bien debajo) y lo
    # de la dimensión financiera en pestañas. No se quitó nada: se reordenó.
    d0 = DIMENSIONES[0]
    pasos = ('<ol class="pl-pasos" aria-label="Cómo se usa el Planisferio">'
             '<li><b aria-hidden="true">1</b><span><strong>Elige una dimensión</strong><small>%d maneras de mirar el país</small></span></li>'
             '<li><b aria-hidden="true">2</b><span><strong>Toca una entidad</strong><small>su ficha aparece junto al mapa</small></span></li>'
             '<li><b aria-hidden="true">3</b><span><strong>Entra a su portal</strong><small>el mapa de sus municipios, uno por uno</small></span></li></ol>') % len(DIMENSIONES)
    hojas = [('cont', '⏱️', 'Los contadores', '<div class="pl-conts">%s</div><div class="pl-cuentas">%s</div>' % (contadores, cuenta_btn))]
    for mod in modulos:
        hojas.append(('cuanto' if 'numeros-cuanto-dinero-es.html' in mod else 'origenes',
                      '💰' if 'numeros-cuanto-dinero-es.html' in mod else '🧾',
                      'Cuánto dinero es' if 'numeros-cuanto-dinero-es.html' in mod else 'Los 16 orígenes del ingreso', mod))
    cuaderno = ('<div class="pl-cuaderno" role="tablist" aria-label="Lo de la dimensión financiera">%s</div>%s') % (
        ''.join('<button type="button" class="pl-hoja-b" role="tab" id="plHojaB-%s" aria-controls="plHoja-%s" aria-selected="%s">'
                '<span aria-hidden="true">%s</span> %s</button>' % (h, h, 'true' if k == 0 else 'false', ico, nom)
                for k, (h, ico, nom, _c) in enumerate(hojas)),
        ''.join('<div class="pl-hoja" role="tabpanel" id="plHoja-%s" aria-labelledby="plHojaB-%s">%s</div>' % (h, h, c)
                for h, _i, _n, c in hojas))
    bloque_mapa = '''%s
          <div class="pl-dims" role="tablist" aria-label="Las dimensiones del Planisferio">%s</div>
          <section class="pl-tablero" id="plTablero" data-dim="%s" aria-labelledby="plDimTit">
            <header class="pl-tab-cab">
              <h3 class="pl-tab-tit" id="plDimTit">Dimensión %s</h3>
              <p class="pl-tab-q" id="plDimQ">%s</p>
            </header>
            <p class="pl-dim-aviso" id="plDimAviso" hidden></p>
            <div class="pl-lentes" role="radiogroup" aria-label="Qué ver en el mapa">%s</div>
            <p class="pl-que" id="plQue"></p>
            <div class="pl-rej">
              <figure class="pl-fig">
                %s
                <figcaption class="pl-leyenda" id="plLeyenda"></figcaption>
              </figure>
              <aside class="pl-ficha" id="plFicha" aria-live="polite">
                <p class="pl-ficha-vacia"><b>Toca una entidad.</b> Verás sus cifras de la dimensión que elegiste y la puerta a su portal, con sus municipios.</p>
              </aside>
            </div>
            <p class="pl-pie" id="plFuente"></p>
            <p class="pl-pie" id="plFalta"></p>
            <footer class="pl-tab-pie">
              <p class="pl-tab-pie-t">Para leerla bien</p>
              <div class="pl-cajones">%s</div>
              <div class="pl-indice-b"><button type="button" class="pl-caj-b pl-indice-btn" data-cajon="plTplIndice" data-cajon-tit="plTplIndiceTit" data-cajon-hash="entidades" aria-haspopup="dialog">📍 Las 32 entidades: entra a su portal</button></div>
            </footer>
          </section>%s
          <template id="plTplIndice">%s</template>
          <div class="pl-solo-dim pl-fin" data-dim="financiera">
            <h3 class="pl-fin-tit">Cuánto dinero es, de dónde sale y lo que baja al territorio</h3>
            <p class="pl-fin-sub">Los tres presupuestos de la Federación en 2026, lo que transfiere a estados y municipios y lo que ingresaron los municipios. El ritmo por segundo es la cifra anual entre 31,536,000 segundos: sirve para dimensionarla, no es dinero que se mueva en tiempo real.</p>
            %s
          </div>
          <script type="application/json" id="plDatos">%s</script>
          <noscript><p>El mapa se colorea con JavaScript; sin él, cada entidad se abre desde la lista de arriba.</p></noscript>''' % (
        pasos, ''.join(dims), d0[0], d0[2].lower(), d0[3], lentes, svg, ''.join(cajones), ''.join(plantillas),
        _cajon('📍', 'Las 32 entidades', 'Elige una entidad para entrar a su portal', 'plTplIndiceTit',
               '<nav class="pl-indice" aria-label="Las 32 entidades, una por una"><ul>%s</ul></nav>' % indice),
        cuaderno, _json(datos))
    return {
        'archivo': ARCHIVO, 'menu': 'Planisferio', 'menu_archivo': ARCHIVO,
        'icono': '🗺️', 'titulo': 'Planisferio', 'lema': 'México en un mapa: cada entidad, cada municipio, cada peso',
        'entrada': ('El dinero público tiene domicilio. Elige una dimensión y toca una entidad para entrar a su portal, con sus municipios. '
                    'Todo sale de la Enciclopedia, con su fuente oficial y su etiqueta.'),
        # La imagen del encabezado (pedido del autor, 04-11-2026): el paisaje al
        # frente y la persona que lo mira, en sombra. planisferio.css la pone.
        'fondo': 'assets/auditor/img/planisferio-paisaje.webp', 'rubro': 'planisferio',
        'estilos': ['numeros.css', 'radar.css', 'planisferio.css'],
        'scripts': ['planisferio.js'],
        'secciones': [
            {'id': 'mapa', 'titulo': 'Juega con el mapa',
             'texto': 'Hoy se pintan %d dimensiones. Cada una trae su «Cómo leerla» y lo que su mapa no dice.' % len(pintadas),
             'tarjetas': [], 'bloque': bloque_mapa},
        ] + ([] if not otras else [
            {'id': 'dimensiones', 'titulo': 'Las dimensiones que vienen',
             'texto': ('El Planisferio crece por entregas, una dimensión a la vez y, después, municipio por municipio. Mientras llegan al mapa, cada una ya tiene su lugar en la Enciclopedia:'),
             'tarjetas': [], 'bloque': '<ul class="pl-otras">%s</ul>' % otras},
        ]),
    }


def _nota_amb(filas):
    """Los puntos ciegos de las refinerías, dichos con las cifras: procesar
    no es producir, un mes malo no es la regla y el deterioro no es efectivo."""
    import recursos_naturales as rn
    R = rn.refinerias()
    caida = min(R, key=lambda r: r['jun'] / r['prom'])
    if caida['id'] not in ('minatitlan', 'olmeca'):
        raise SystemExit('planisferio: la caída de junio es de %s; el Informe solo explica las de Minatitlán y Olmeca' % caida['id'])
    d25 = min((r for r in R if r['d25'] is not None), key=lambda r: r['d25'])
    A = rn.acuiferos([f['a'] for f in filas])
    dif = [(n, a) for a, xs in rn.SOBRE27.items() for c, n, d in xs if d > 0]
    nom = {f['a']: f['n'] for f in filas}
    agua = ('<b>Lo que el mapa del agua no dice.</b> La disponibilidad no es el agua que queda en el subsuelo: es la que todavía se puede concesionar, y mide cantidad, no calidad. '
            'Sin disponibilidad no es lo mismo que sobreexplotado: el Segundo Informe cuenta en sobreexplotación a %s, y el Acuerdo de 2023 les da disponibilidad %s. '
            'Y el corte es de diciembre de 2022, aunque la Ley de Aguas Nacionales pide revisarlo al menos cada dos años (art. 22) %s.<br><br>') % (
        rn._y(['%s (%s)' % (n, nom[a]) for n, a in dif]), chip('oficial'), chip('pendiente', 'acuiferos-disponibilidad-nueva'))
    if not dif or len(A) != 32:
        raise SystemExit('planisferio: el punto ciego del agua ya no tiene acuíferos sobreexplotados con disponibilidad')
    I = rn.incendios([f['a'] for f in filas])
    h25, a25 = rn.INC_TOT[25][1], rn.INC_TOT[25][2]
    mn = min(I, key=lambda k: I[k]['ln'])
    gh = min(I, key=lambda k: I[k]['lh'])
    F = rn.forestal([f['a'] for f in filas])
    fq = min(F, key=lambda k: F[k]['lq'])
    if fq == gh:
        raise SystemExit('planisferio: el punto ciego de la superficie forestal ya no aplica: la entidad más afectada frente a su bosque es la de más superficie afectada')
    if mn == gh:
        raise SystemExit('planisferio: el punto ciego del fuego ya no aplica: la entidad con más incendios es la de más superficie')
    fuego = ('<b>Lo que el mapa del fuego no dice.</b> Superficie afectada no es bosque perdido: de las %s ha que afectaron los incendios de 2025, solo el %s %% era de árboles %s, '
             'y la CONAFOR calificó de impacto mínimo el %s %% %s. Muchos incendios no es mucha superficie: %s tuvo más (%s) y %s, más terreno afectado. '
             'Y la cifra de una semana no es la del año: el cierre sumó incendios que se reportaron tarde. Frente a su superficie forestal, el fuego tocó más a %s (%s de cada 100 ha %s) que a %s (%s): '
             'es una proporción con el mapa de vegetación de 2018, no la parte que se perdió, y «forestal» incluye el matorral.<br><br>') % (
        format(round(h25), ','), format(a25 / h25 * 100, '.1f'), chip('derivado'), format(rn.INC_NAC['min'] / h25 * 100, '.1f'), chip('derivado'),
        nom[mn], format(I[mn]['n'], ','), nom[gh], nom[fq], format(F[fq]['pq'], '.1f'), chip('derivado'), nom[gh], format(F[gh]['pq'], '.1f'))
    P = rn.pesca([f['a'] for f in filas])
    gap = max((k for k in P if P[k]['t']), key=lambda k: P[k]['lv'] - P[k]['lt'])
    pesca = ('<b>Lo que el mapa de la pesca no dice.</b> Es lo que se declaró en los avisos de arribo y de cosecha, no todo lo que se pescó, y no dice si las especies aguantan. '
             'Mucho volumen no es mucho valor: %s es el lugar %d por toneladas y el %d por valor %s. El valor de 2025 es en pesos de ese año y subió %s %% contra 2024, con las toneladas casi iguales %s. '
             'Y el propio Anuario imprime cruzadas las cifras de Jalisco y Colima en dos de sus cuadros: aquí van las de sus series.<br><br>') % (
        nom[gap], P[gap]['lt'], P[gap]['lv'], chip('derivado'), format((rn.PE_TOT['val'] - rn.PE_TOT['val24']) / rn.PE_TOT['val24'] * 100, '.1f'), chip('derivado'))
    return agua + fuego + pesca + ('<b>Lo que una cifra de refinación no dice.</b> Un mes no es la regla: la %s procesó %s mil barriles diarios en junio de 2026 %s, contra %s mil de promedio en los diez meses %s, '
            'por mantenimiento según el Informe. Procesar crudo no es producir gasolina: lo que sale depende de cada planta. Y el valor que pierde una refinería en los libros de PEMEX '
            '(la %s, %s en 2025 %s) es una estimación de lo que dejará de generar, no dinero que salió de la caja.<br><br>'
            '<b>Lo que el mapa de las minas no dice.</b> Una concesión no es una mina trabajando: %s tienen concesiones y no aparecen entre las entidades con '
            'producción minera del Segundo Informe. Hectárea concesionada no es hectárea excavada. Y el cuadro por estado es de marzo de 2024 %s: al 30 de junio de 2026 el país tenía '
            '%s títulos %s, %s menos %s, pero la Secretaría de Economía solo ha dado al día cuatro estados.') % (
        caida['n'].replace('Refinería ', 'refinería '), caida['jun'], chip('oficial'), format(caida['prom'], '.1f'), chip('derivado'),
        d25['n'].replace('Refinería ', 'refinería '), rn._mdps(d25['d25']), chip('oficial'),
        rn._y([f['n'] for f in filas if f.get('min') and f['min']['prod'] is None]), chip('pendiente', 'mineria-por-estado-2026'),
        format(rn.NAC26['t'], ','), chip('oficial'), format(rn.MINAS_TOT[0] - rn.NAC26['t'], ','), chip('derivado'))


def _nota_sal(filas):
    """Los puntos ciegos de la salud pública, dichos con las cifras: la cama
    que no es igual en todos los estados, el ISSSTE concentrado en la capital
    y lo que su anuario no deja ver."""
    k = sorted(filas, key=lambda f: f['imK'])
    tm = sum(f['isM'] for f in filas)
    cd = max(filas, key=lambda f: f['isM'])
    pr = sorted(filas, key=lambda f: f['isM'] / (f['isM'] + f['imM']))
    return ('<b>La misma institución no da la misma cama en todos lados.</b> Por cada mil personas adscritas, el IMSS tiene %s camas de hospitalización en %s %s y %s en %s %s. '
            'Parte de la diferencia es que los hospitales de alta especialidad se cuentan donde están y atienden a gente de otros estados; la otra parte es que no hay '
            'la misma infraestructura en todos lados. <b>El ISSSTE, en la capital:</b> %s de sus %s médicos están en %s %s, %s de cada 100 %s. '
            'Y donde menos pesa frente al IMSS es %s: de cada 100 médicos de las dos instituciones, %s son del ISSSTE %s. '
            '<b>Lo que falta:</b> cuántas personas atiende el ISSSTE en cada estado y qué les resolvió %s. Sin eso, sus camas y sus médicos no se pueden poner por persona, '
            'y este mapa no puede decir si el ISSSTE de un estado alcanza o no. Tampoco está quien no tiene seguridad social: el IMSS-Bienestar y los servicios estatales.') % (
        format(k[-1]['imK'], '.2f'), k[-1]['n'], chip('derivado'), format(k[0]['imK'], '.2f'), k[0]['n'], chip('derivado'),
        format(cd['isM'], ','), format(tm, ','), cd['n'], chip('oficial'), format(round(100.0 * cd['isM'] / tm)), chip('derivado'),
        pr[0]['n'], format(100.0 * pr[0]['isM'] / (pr[0]['isM'] + pr[0]['imM']), '.1f'), chip('derivado'),
        chip('pendiente', 'salud-issste-servicios'))


def _ctx(i):
    """Las páginas que miran la dimensión a nivel federal: su Contexto
    dimensional y el estado de resultados del Gobierno (04-11-2026)."""
    import dimension_social as dso
    xs = dso.CONTEXTO.get(i)
    if not xs:
        raise SystemExit('planisferio: la dimensión %s no tiene su Contexto dimensional en dimension_social.CONTEXTO' % i)
    for arch, _ in xs + [dso.RESULTADOS]:
        if not _existe(arch):
            raise SystemExit('planisferio: el Contexto dimensional de %s apunta a %s, que no existe' % (i, arch))
    return xs, dso.RESULTADOS


def _ctx_botones(i, oculto):
    xs, (ra, rt) = _ctx(i)
    return ''.join('<a class="pl-caj-b pl-ctx" data-dim="%s" href="%s" title="%s"%s>🧭 %s</a>' % (
        i, arch, html.escape(t), oculto, html.escape(t.split(':')[0])) for arch, t in xs) + (
        '<a class="pl-caj-b pl-ctx" data-dim="%s" href="%s" title="%s"%s>📊 Estado de resultados del Gobierno</a>' % (i, ra, html.escape(rt), oculto))


def _ctx_portal(i, a, nom):
    """El mismo vínculo en el portal de cada estado, con su propio estado de
    cuenta y de resultados en el Auditor de entes."""
    import dimension_social as dso
    xs, (ra, rt) = _ctx(i)
    return ('<p class="pl-ctx-l"><b>En el país y en sus cuentas:</b> %s <a href="%s">📊 %s ➔</a> '
            '<a href="%s">🏢 El estado de cuenta y de resultados de %s ➔</a></p>') % (
        ' '.join('<a href="%s">🧭 Contexto dimensional · %s ➔</a>' % (arch, html.escape(t)) for arch, t in xs),
        ra, html.escape(rt), dso.RESULTADOS_EDO % a, html.escape(nom))


def _nota_soc(filas):
    """Los puntos ciegos de la dimensión social, dichos con las cifras: el
    porcentaje contra el número de personas, la pobreza que no es el saldo de
    un gobierno y las aportaciones que no siguen a la pobreza."""
    p = sorted(filas, key=lambda f: -f['soP'])
    n = sorted(filas, key=lambda f: -f['soN'])
    q = sorted((f for f in filas if f['soQ']), key=lambda f: -f['soQ'])
    lug = [f['a'] for f in p].index(n[0]['a']) + 1
    return ('<b>El porcentaje y las personas cuentan historias distintas.</b> %s tiene la pobreza más alta, %s de cada 100 %s; pero donde más personas la viven es %s: '
            '%s %s, aunque en porcentaje sale en el lugar %d. <b>La pobreza no es el saldo de un gobierno.</b> La mide el INEGI en los hogares: depende del ingreso y de seis carencias, '
            'y a cada una la mueven la Federación, el estado, el municipio, la economía y las remesas. Por eso este mapa no califica a nadie. '
            '<b>El dinero no sigue a la pobreza.</b> Por cada persona en pobreza, %s recibe %s de aportaciones federales y %s, %s %s: el Ramo 33 se reparte con fórmulas que pesan '
            'la nómina educativa y de salud que ya existe, y solo su fondo de infraestructura social (FAIS) se reparte por pobreza (Ley de Coordinación Fiscal, arts. 32 a 34). '
            'Además, esa división junta aportaciones de 2026 con pobreza de 2024. <b>Lo que falta:</b> cuánto de cada programa social llega a cada estado y a quién; '
            'la Secretaría de Bienestar no publica sus padrones por entidad en un formato que se pueda cotejar.') % (
        p[0]['n'], format(p[0]['soP'], '.1f'), chip('oficial'), n[0]['n'], format(n[0]['soN'], ','), chip('derivado'), lug,
        q[0]['n'], '$' + format(q[0]['soQ'], ','), q[-1]['n'], '$' + format(q[-1]['soQ'], ','), chip('derivado'))


def _social_portal(base, ref, e):
    """Su pobreza (04-11-2026): la infografía del INEGI de su estado, con su
    lugar entre los 32 y frente al país."""
    import dimension_social as dso
    so = dso.estados(base)
    na = dso.nacional()
    a, nom = e['abbr'], e['name']
    z = so[a]
    lug = lambda k: sorted(so, key=lambda b: -k(so[b])).index(a) + 1
    car = ''.join('<dt>%s</dt><dd>%s %s <small>en el país, %s</small></dd>' % (t, pct(z['car'][c]), chip('oficial'), pct(na['car'][c])) for c, t in dso.CARENCIAS)
    p1 = ('<article class="pl-piso"><h3>🫂 La pobreza en %s · 2024</h3>'
          '<dl class="pl-dl"><dt>Población en pobreza</dt><dd>%s %s <small>lugar %d de 32; en el país, %s</small></dd>'
          '<dt>Personas en pobreza</dt><dd>%s %s <small>%s × %s habitantes de la medición</small></dd>'
          '<dt>Pobreza moderada · extrema</dt><dd>%s · %s %s</dd>'
          '<dt>Ingreso bajo la línea de pobreza</dt><dd>%s %s <small>bajo la línea de pobreza extrema: %s</small></dd>'
          '<dt>Aportaciones federales 2026 por persona en pobreza</dt><dd>%s %s <small>lugar %d de 32; Ramo 33 ÷ personas en pobreza de 2024</small></dd>'
          '</dl><p class="pl-piso-f">INEGI, Pobreza multidimensional 2024, <a href="%s">infografía de %s</a> (huella SHA-256 <code>%s…</code>). '
          'Las personas y la división son nuestras.</p></article>') % (
              html.escape(nom), pct(z['p']), chip('oficial'), lug(lambda r: r['p']), pct(na['p']),
              format(z['pers'], ','), chip('derivado'), pct(z['p']), format(z['pobT'], ','),
              pct(z['m']), pct(z['x']), chip('oficial'), pct(z['ing']), chip('oficial'), pct(z['ingx']),
              ('$' + format(z['r33'], ',')) if z['r33'] else 'sin cifra', chip('derivado'), lug(lambda r: r['r33'] or 0),
              html.escape(z['url']), html.escape(nom), z['sha'][:12])
    p2 = '<article class="pl-piso"><h3>📋 Sus seis carencias sociales · 2024</h3><dl class="pl-dl">%s</dl><p class="pl-piso-f">De cada 100 personas del estado. Misma infografía del INEGI.</p></article>' % car
    ciego = ('<p class="pl-dim-nota"><b>Lo que estas cifras no dicen.</b> La pobreza la mide el INEGI en los hogares y la mueven los tres niveles de gobierno, la economía y las remesas: '
             'no es la calificación de un gobierno. «Sin acceso a servicios de salud» mide la afiliación, no si la clínica tiene médico o medicina. Y las aportaciones por persona en pobreza '
             'no son lo que le llega a cada persona: el Ramo 33 paga sobre todo maestros y salud.</p>')
    ir = ('<p class="pl-ficha-ir"><a href="planisferio.html?d=social&amp;e=%s">La pobreza de los 32 estados, en el mapa ➔</a> '
          '<a href="contexto-dimensional-social.html">Los programas sociales del país, en el Contexto dimensional ➔</a></p>') % quote(a)
    return '<div class="pl-pisos">%s%s</div>%s%s' % (p1, p2, ciego, ir)


def _nota_apu(filas):
    """Los puntos ciegos de la administración pública, dichos con las
    cifras: el personal que no se cuenta igual, la adjudicación que cuenta
    contratos y no pesos, y la auditoría que solo ve el dinero federal."""
    import administracion_publica as apu
    k = sorted(filas, key=lambda f: f['apK'])
    d = sorted((f for f in filas if f['a'] not in ('OAX', 'YUC')), key=lambda f: f['apD'])
    ga = sum(f['apG'] for f in filas)
    ma = sum(f['apA'] for f in filas)
    return ('<b>No todos cuentan lo mismo.</b> Por cada mil habitantes, el gobierno de %s reportó %s personas en su administración y el de %s, %s %s. '
            'Es lo que cada uno le contestó al censo del INEGI, que no dice qué organismos incluyó cada gobierno: una diferencia así se pregunta, no se concluye. '
            '<b>La adjudicación directa cuenta contratos, no pesos:</b> %s dio %s de cada 100 sin concurso y %s, %s %s, pero un solo contrato grande pesa más que cien chicos. %s '
            '<b>La auditoría que se ve es la del dinero federal.</b> La ASF dejó %s por aclarar a los 32 gobiernos estatales y %s a sus municipios %s, y no es un desfalco comprobado. '
            'El dinero propio de cada estado y de cada municipio lo revisa la entidad de fiscalización superior del estado, cuyos informes la plataforma todavía no ha integrado.') % (
        k[-1]['n'], format(k[-1]['apK'], '.1f'), k[0]['n'], format(k[0]['apK'], '.1f'), chip('derivado'),
        d[-1]['n'], format(d[-1]['apD'], '.1f'), d[0]['n'], format(d[0]['apD'], '.1f'), chip('oficial'), html.escape(apu.CONTRATOS_NOTA),
        mdp(ga), mdp(ma), chip('derivado'))


def _nota_jud(filas):
    """Los puntos ciegos de los poderes judiciales, dichos con las cifras:
    «concluyó de cada 100» no es el rezago, y el dinero por asunto no es lo
    que cuesta un juicio."""
    a = sorted(filas, key=lambda f: -f['juda'])
    c = sorted(filas, key=lambda f: f['judc'])
    r = sorted(filas, key=lambda f: -f['judr'])
    return ('<b>Lo que un solo número no dice.</b> Por asunto concluido, %s ejerció %s %s y %s, %s %s: %s veces más. Pero un asunto concluido puede ser una sentencia '
            'después de años de juicio o una demanda que se desechó el primer día, y el censo no los separa: la distancia es una pregunta, no un veredicto. '
            '<b>Y lo que concluye no es lo que debe.</b> %s concluyó %s de cada 100 asuntos que le entraron %s, el más bajo del país, y es el lugar %d de 32 en causas penales pendientes '
            '(%s %s, con %s personas juzgadoras en todas las materias). Pero en lo civil, familiar y mercantil el INEGI cuenta como ingresada toda demanda, '
            'y cuántas quedaron sin resolver no lo publica %s. Son cifras que cada poder judicial le reporta de sí mismo al INEGI.') % (
                a[0]['n'], _pesos(a[0]['juda']), chip('derivado'), a[-1]['n'], _pesos(a[-1]['juda']), chip('derivado'),
                format(a[0]['juda'] / a[-1]['juda'], '.1f'),
                c[0]['n'], pct(c[0]['judc']), chip('derivado'), r.index(c[0]) + 1, format(c[0]['judr'], ','), chip('oficial'), c[0]['judj'],
                chip('pendiente', 'judicial-rezago-civil'))


def _nota_leg(filas):
    """Los puntos ciegos de los congresos, dichos con las cifras: cuántos
    quedarían arriba del tope como referencia y la distancia entre el más
    caro y el más barato por curul."""
    import asistente_legislativo as al
    con = [f for f in filas if f['legp'] is not None]
    arriba = sorted((f for f in con if f['legp'] > al.TOPE_116), key=lambda f: -f['legp'])
    x = sorted(filas, key=lambda f: -f['legx'])
    return ('<b>Lo que el tope no dice.</b> Si el gasto de 2024 se midiera contra el tope del 0.70 %%, %d de los %d congresos con cifra quedarían arriba; el más alto, %s, con %s %s. '
            'Pero no es un incumplimiento: el tope es de abril de 2026, se mide contra el presupuesto de egresos que aprueba cada estado (no contra lo que registró el INEGI), '
            'y la Constitución da plazo: la reducción surte efecto al iniciar la legislatura siguiente de cada estado (transitorio quinto). Al que ya está debajo le pone otro candado: '
            'no puede crecer en términos reales sobre lo que aprobó para 2026 (transitorio octavo). '
            '<b>Y por curul</b>, %s gastó %s %s y %s, %s %s: %s veces más. El censo recoge lo que cada congreso le reportó al INEGI: '
            'la distancia es una pregunta que hacerle a su cuenta pública, no una conclusión.') % (
                len(arriba), len(con), arriba[0]['n'], pct(arriba[0]["legp"], 2), chip('derivado'),
                x[0]['n'], mdp(x[0]['legx']), chip('derivado'), x[-1]['n'], mdp(x[-1]['legx']), chip('derivado'),
                format(x[0]['legx'] / x[-1]['legx'], '.1f'))



def _lugar(E, a, k, med=False):
    """Su lugar entre las entidades, de la que más a la que menos (derivado)."""
    v = [x for x in E if x.get(k) is not None and (not med or _medida(x))]
    v.sort(key=lambda x: -x[k])
    return next(i for i, x in enumerate(v) if x['abbr'] == a) + 1, len(v)


def _deuda_portal(base, ref, e, pm=''):
    E = base['estados']
    fu = _fuentes(ref, base)
    a = e['abbr']
    dpc = e['deuda'] * 1e6 / e['pobPersonas']
    l1, n1 = _lugar(E, a, 'deuda')
    # El total, tal cual lo suma la ficha de los Expedientes con las cifras sin
    # redondear: sumar las cifras ya redondeadas daría una décima distinta.
    f = next(x for x in base['expedientes']['fichas'] if x['id'] == 'deuda-estados')
    tot = float(f['cifras'][0]['valor'].replace('$', '').replace(',', '').replace(' mdp', ''))
    if abs(tot - sum(x['deuda'] for x in E)) > 1:
        raise SystemExit('planisferio: la deuda de los estados no cuadra con la ficha deuda-estados')
    p1 = ('<article class="pl-piso pl-piso-deuda"><p class="pl-piso-n">Lo que debe · cierre de 2025</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%s</b> %s</p>'
          '<dl class="pl-dl"><dt>Por habitante</dt><dd>%s %s <small>la deuda entre la población a mitad de 2026</small></dd>'
          '<dt>Su lugar entre las 32</dt><dd>%s %s <small>de la que más debe a la que menos</small></dd>'
          '<dt>Su parte de la deuda de los 32 estados</dt><dd>%s %s <small>de %s que suman entre todos</small></dd></dl>'
          '<p class="pl-piso-f">%s</p></article>' % (
              mdp(e['deuda']), chip('oficial'), _pesos(dpc), chip('derivado'),
              ('%d.º de %d' % (l1, n1)) if e['deuda'] else 'Sin deuda inscrita', chip('derivado') if e['deuda'] else '',
              pct(e['deuda'] / tot * 100), chip('derivado'), mdp(tot), fu['deuda']))
    if _medida(e):
        l2, n2 = _lugar(E, a, 'deudaIld', med=True)
        p2 = ('<article class="pl-piso pl-piso-deuda"><p class="pl-piso-n">Cuánto le pesa · los tres indicadores</p>'
              '<p class="pl-piso-v"><b>%s</b> %s</p>'
              '<dl class="pl-dl"><dt>1 · Deuda ÷ ingresos de libre disposición</dt><dd>%s %s <small>%d.º de %d estados medidos; sus ingresos de libre disposición fueron %s %s</small></dd>'
              '<dt>2 · Lo que pagó por ella ÷ esos ingresos</dt><dd>%s %s <small>de cada $100 de su dinero libre, %s se fueron en pagar deuda y obligaciones</small></dd>'
              '<dt>3 · Deudas de corto plazo, menos lo que tiene en caja, ÷ ingresos totales</dt><dd>%s %s <small>%s</small></dd></dl>'
              '<p class="pl-piso-f">%s</p></article>' % (
                  SEMAFORO[e['semaforoDeuda']], chip('oficial'),
                  pct(e['deudaIld']), chip('oficial'), l2, n2, mdp(e['ildMdp']), chip('oficial'),
                  pct(e['deudaSd']), chip('oficial'), '$' + format(e['deudaSd'], '.1f'),
                  pct(e['deudaOcp']), chip('oficial'),
                  'negativo: tenía en efectivo, bancos e inversiones temporales más de lo que debía a corto plazo' if e['deudaOcp'] < 0 else
                  'lo que debía a corto plazo superaba lo que tenía en caja',
                  fu['ild']))
    else:
        p2 = ('<article class="pl-piso pl-piso-deuda"><p class="pl-piso-n">Cuánto le pesa · los tres indicadores</p>'
              '<p class="pl-piso-v"><b>No se mide</b> %s</p><p>%s no tiene deuda inscrita en el Registro Público Único, así que el Sistema de Alertas no le calcula '
              'indicadores: la Ley de Disciplina Financiera (art. 43) solo manda evaluar a quien tiene deuda inscrita, y Hacienda no le publica semáforo. No tener deuda inscrita no quiere decir no deberle '
              'a nadie: los adeudos con proveedores, por ejemplo, no pasan por ese registro.</p><p class="pl-piso-f">%s</p></article>' % (
                  chip('oficial'), e['name'], fu['deuda']))
    ciego = ('<p class="pl-dim-nota">El semáforo verde quiere decir que, con sus tres mediciones, Hacienda considera sostenible su deuda, no que deba poco. El Sistema de Alertas solo mide la deuda inscrita '
             'en el Registro Público Único que se paga con ingresos de libre disposición; lo que se debe por otras vías no entra en estas cifras.</p>')
    # Las reglas de su deuda (03-11-2026), cotejadas con su texto vigente.
    import leyes_niveles as ln
    techo = {'Verde': 15, 'Amarillo': 5, 'Rojo': 0}
    if _medida(e):
        t = techo[e['semaforoDeuda']]
        r_techo = ('Con su nivel, la LDF (art. 46) le fija un techo de financiamiento neto de hasta el %d %% de sus ingresos de libre disposición '
                   '(15 %% si es sostenible, 5 %% en observación, 0 %% si es elevado). Como referencia, el %d %% de los de 2025 es %s %s; '
                   'el techo de cada año lo calcula Hacienda.') % (t, t, mdp(round(e['ildMdp'] * t / 100, 1)), chip('derivado'))
    else:
        r_techo = ('Para fijarle un techo de financiamiento sin deuda inscrita, la LDF (art. 46) le pide entregar a Hacienda la información que marca el Reglamento '
                   'del Registro Público Único.')
    reglas = ('<div class="pl-reglas"><p><b>Las reglas de su deuda</b></p><ul>'
              '<li>Solo puede endeudarse para inversión pública productiva y para refinanciarla, nunca con acreedores extranjeros ni en moneda extranjera (%s, art. 117, fr. VIII).</li>'
              '<li>%s</li>'
              '<li>Hacienda la evalúa «única y exclusivamente» con la información que entrega el propio gobierno y la del Registro Público Único (%s, art. 43).</li>'
              '<li>La deuda de sus municipios también la mide el Sistema de Alertas: lo que pagaron y pidieron prestado en 2024 ya está arriba, con su cuenta; su saldo aún no lo integramos %s.</li>'
              '<li>Su propia ley de deuda pública se publica en: %s. <a href="%s#fed-deuda">⚖️ Las leyes de la deuda en los tres niveles</a></li></ul></div>') % (
        ln._a(ln.CPEUM, 'Constitución'), r_techo, ln._a(ln.pdf('LDFEFM.pdf'), 'LDF'),
        '<span class="est-chip est-pendiente" data-pend="deuda-municipios">pendiente</span>', html.escape(ln.ESTADOS[a][0]), ln.ARCHIVO)
    return '<div class="pl-pisos">%s%s%s</div>%s%s' % (p1, p2, pm, ciego, reglas)


def _deuda_mun(ref, e, m, dv, con_mapa):
    """La deuda en la cuenta de sus municipios, 2024 (03-11-2026): lo que
    pagaron por sus créditos y lo que pidieron prestado, suma de los que
    rindieron cuenta (derivado). El saldo sigue pendiente."""
    tit = '3 · La deuda en la cuenta de sus municipios · 2024'
    pend = chip('pendiente', 'deuda-municipios')
    if not m['conCifra']:
        return ('<article class="pl-piso pl-piso-deuda"><p class="pl-piso-n">%s</p>'
                '<p class="pl-piso-v"><b>Sin cuenta municipal</b> %s</p><p>Las alcaldías de la Ciudad de México no rinden cuenta municipal al INEGI ni se endeudan por su cuenta: '
                'la deuda es de la Ciudad, y es la que está arriba. Ponerles cero falsearía la cifra.</p></article>' % (tit, chip('pendiente', 'municipios-sin-cuenta')))
    filas = [(r, dv['mun'][m['cve'] + r[0]]) for r in m['lista'] if len(r) >= 10]
    pago = [d[1] + d[2] + d[3] for _r, d in filas]
    tot = sum(pago)
    cap = sum(d[1] for _r, d in filas)
    inte = sum(d[2] + d[3] for _r, d in filas)
    emp = sum(d[5] for _r, d in filas)
    n_emp = sum(1 for _r, d in filas if d[5])
    adef = sum(d[4] for _r, d in filas)
    n_pago = sum(1 for x in pago if x)
    ir = ('<p class="pl-ficha-ir"><a href="%s?ml=dpag#mapa-municipios">Municipio por municipio, en el mapa ➔</a></p>' % portal(e['abbr'])) if con_mapa else ''
    if tot:
        top_r, top_d = max(filas, key=lambda x: x[1][1] + x[1][2] + x[1][3])
        top = '<dt>El que más pagó</dt><dd>%s: %s %s</dd>' % (html.escape(top_r[1]), mdp((top_d[1] + top_d[2] + top_d[3]) / 1e6), chip('oficial'))
        desglose = ('<dt>Capital que devolvieron</dt><dd>%s %s</dd><dt>Intereses y comisiones</dt><dd>%s %s <small>lo que les costó deber</small></dd>' % (
            mdp(cap / 1e6), chip('derivado'), mdp(inte / 1e6), chip('derivado')))
    else:
        top = desglose = ''
    return ('<article class="pl-piso pl-piso-deuda"><p class="pl-piso-n">%s</p>'
            '<p class="pl-piso-v"><b class="num-tabular">%s</b> %s <small>pagaron por sus créditos</small></p>'
            '<dl class="pl-dl"><dt>Municipios que pagaron créditos</dt><dd>%d de %d con cuenta <small>(%d en total)</small></dd>%s'
            '<dt>Pidieron prestado en el año</dt><dd>%s %s <small>%s</small></dd>'
            '<dt>Adeudos de años anteriores (ADEFAS)</dt><dd>%s %s <small>lo que quedó a deber el año anterior, sobre todo a proveedores, y pagó en 2024: no es un crédito</small></dd>%s</dl>'
            '<p class="pl-piso-f">Suma de lo que cada municipio con cuenta reportó en su capítulo de deuda pública (capital, intereses, comisiones y gastos) y en sus empréstitos. '
            'INEGI, finanzas públicas municipales %d %s. <b>Es lo que pagaron y pidieron en el año, no lo que deben:</b> el saldo de cada municipio lo publica Hacienda en el Sistema de Alertas, '
            'y aún no lo integramos %s. Un municipio que reportó $0 puede deber a proveedores o tener un crédito sin pagos ese año.</p>%s</article>' % (
                tit, mdp(tot / 1e6), chip('derivado'), n_pago, len(filas), m['n'], desglose,
                mdp(emp / 1e6), chip('derivado'),
                'ninguno recibió préstamos' if not n_emp else ('%d %s' % (n_emp, 'municipio recibió préstamos' if n_emp == 1 else 'municipios recibieron préstamos')),
                mdp(adef / 1e6), chip('derivado'), top, dv['anio'], ref('ref-inegi-efipem'), pend, ir))


def _inversion_mun(ref, e, m, iv, con_mapa):
    """La obra de sus municipios, suma de los que rindieron cuenta (derivado)."""
    if not m['conCifra']:
        return ('<article class="pl-piso pl-piso-inv"><p class="pl-piso-n">3 · La obra de sus %d demarcaciones · 2024</p>'
                '<p class="pl-piso-v"><b>Sin cuenta municipal</b> %s</p><p>Las alcaldías de la Ciudad de México no rinden cuenta municipal al INEGI: '
                'su obra va dentro del presupuesto de la Ciudad. Ponerle cero falsearía la cifra.</p></article>' % (m['n'], chip('pendiente', 'municipios-sin-cuenta')))
    filas = [(r, iv['mun'][m['cve'] + r[0]]) for r in m['lista'] if len(r) >= 10]
    tot = sum(v[0] for _r, v in filas)
    egr = sum(r[9] for r, _v in filas)
    cero = sum(1 for _r, v in filas if v[0] == 0)
    top_r, top_v = max(filas, key=lambda x: x[1][0])
    ir = ('<p class="pl-ficha-ir"><a href="%s?ml=inv#mapa-municipios">Municipio por municipio, en el mapa ➔</a></p>' % portal(e['abbr'])) if con_mapa else ''
    return ('<article class="pl-piso pl-piso-inv"><p class="pl-piso-n">3 · La obra de sus municipios · 2024</p>'
            '<p class="pl-piso-v"><b class="num-tabular">%s</b> %s</p>'
            '<dl class="pl-dl"><dt>Municipios con cuenta</dt><dd>%d de %d</dd>'
            '<dt>De cada $100 de su egreso</dt><dd>%s %s <small>de un egreso total de %s</small></dd>'
            '<dt>El que más invirtió</dt><dd>%s: %s %s</dd>%s</dl>'
            '<p class="pl-piso-f">Suma del capítulo de inversión pública de cada municipio que rindió su cuenta: obra pública y proyectos productivos, '
            'con su dinero propio y con el que le llega (el fondo de infraestructura social municipal incluido). INEGI, finanzas públicas municipales %d %s. '
            'Es la obra de los ayuntamientos: no está dentro de la del gobierno del estado.</p>%s</article>' % (
                mdp(tot / 1e6), chip('derivado'), len(filas), m['n'],
                '$' + format(tot / egr * 100, '.1f') if egr else '—', chip('derivado'), mdp(egr / 1e6),
                html.escape(top_r[1]), mdp(top_v[0] / 1e6), chip('oficial'),
                ('<dt>En $0</dt><dd>%d %s <small>%s su cuenta sin capítulo de inversión pública</small></dd>' % (
                    cero, 'municipio' if cero == 1 else 'municipios', 'rindió' if cero == 1 else 'rindieron')) if cero else '',
                iv['anio'], ref('ref-inegi-efipem'), ir))


def _inversion_portal(base, ref, e, pm=''):
    """La inversión de la entidad (03-11-2026): su obra directa, lo que les
    pasa a sus organismos de obra (no se suman), la de sus municipios y lo que
    dejó la ASF."""
    import leyes_niveles as ln
    E = base['estados']
    fu = _fuentes(ref, base)
    a, nom = e['abbr'], e['name']
    pend = 'entidades-' + a.lower()
    if e.get('invPub') is None:
        p1 = ('<article class="pl-piso pl-piso-inv"><p class="pl-piso-n">La obra que hizo el estado · 2024</p>'
              '<p class="pl-piso-v"><b>Sin cifra cotejada</b> %s</p><p>%s. Ni su obra directa ni lo que pasa a sus organismos tienen todavía documento citado.</p></article>' % (
                  chip('pendiente', pend), base['fiscalEntidades']['campos']['invPub']['motivo']))
        ciego = ''
    else:
        l1, n1 = _lugar(E, a, 'invPub')
        l2, n2 = _lugar(E, a, 'invInfra')
        inv, invt = e['invPub'], e['invInfra']
        p1 = ('<article class="pl-piso pl-piso-inv"><p class="pl-piso-n">1 · La obra que hizo el estado · 2024</p>'
              '<p class="pl-piso-v"><b class="num-tabular">%s</b> %s</p>'
              '<dl class="pl-dl"><dt>De cada $100 de su egreso</dt><dd>%s %s <small>de un egreso total de %s %s, que incluye lo que quedó en caja al cierre</small></dd>'
              '<dt>Su lugar</dt><dd>%d.º de %d %s <small>de la que más obra directa hizo a la que menos</small></dd></dl>'
              '<p class="pl-piso-f">%s</p></article>' % (
                  mdp(inv), chip('oficial'), '$' + format(inv / e['egr2024'] * 100, '.1f'), chip('derivado'), mdp(e['egr2024']), chip('oficial'),
                  l1, n1, chip('derivado'), fu['inv']))
        p1 += ('<article class="pl-piso pl-piso-inv"><p class="pl-piso-n">2 · Lo que les pasó a sus organismos de obra · 2024</p>'
               '<p class="pl-piso-v"><b class="num-tabular">%s</b> %s</p>'
               '<dl class="pl-dl"><dt>Frente a su obra directa</dt><dd>%s</dd>'
               '<dt>Su lugar</dt><dd>%d.º de %d %s</dd></dl>'
               '<p class="pl-piso-f">%s</p></article>' % (
                   mdp(invt), chip('oficial'),
                   ('%s veces %s' % (format(invt / inv, '.1f'), chip('derivado'))) if inv and invt > inv else
                   ('menos que su obra directa %s' % chip('derivado')) if invt < inv else 'lo mismo',
                   l2, n2, chip('derivado'), fu['invt']))
        ciego = ('<p class="pl-dim-nota">%s Juntas de caminos, comisiones de agua e institutos de obra reciben su dinero como transferencia: con él construyen, pero también '
                 'pagan su nómina y su operación. Por eso las dos cifras no se suman, y la segunda no es «toda obra».</p>') % (
                     ('En %s, lo que pasó a sus organismos fue más que la obra que hizo él mismo: mirar solo su capítulo de inversión pública lo haría ver como un estado que casi no invierte.' % nom)
                     if invt > inv else ('En %s, la obra directa es la vía principal.' % nom))
    p3 = ('<article class="pl-piso pl-piso-asf"><p class="pl-piso-n">Lo que la ASF dejó por aclarar · Cuenta Pública 2024</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%s</b> %s</p><p>%s</p>'
          '<p class="pl-piso-f">Es todo el dinero federal que la ASF auditó en la entidad, no solo el de obra. Por aclarar no es robado: es dinero cuyo destino no quedó acreditado. %s</p></article>' % (
              mdp(e['asfMontoObservado']), chip('oficial'), html.escape(e['asfTipologia']), fu['asf']))
    reglas = ('<div class="pl-reglas"><p><b>Las reglas de su obra</b></p><ul>'
              '<li>Si construye con dinero federal por convenio, contrata con la ley federal de obra pública; los fondos del Ramo 33 quedan fuera de ella y siguen la ley del estado (%s, art. 1, fr. VI).</li>'
              '<li>Lo que pide prestado solo puede ir a inversión pública productiva (%s, art. 117, fr. VIII).</li>'
              '<li>Su propia ley de obra pública se publica en: %s. <a href="%s#fed-adquisiciones">⚖️ Las leyes de compras y obra en los tres niveles</a></li></ul>'
              '<p class="pl-ficha-ir"><a href="numeros-mapa-del-gasto-federalizado.html?l=inv&amp;e=%s">Las 32, en el mapa de la Enciclopedia ➔</a> '
              '<a href="datos-ambiente-megaobras.html?e=%s#abMapaObras">Sus obras con alerta ambiental ➔</a></p></div>') % (
        ln._a(ln.pdf('LOPSRM.pdf'), 'LOPSRM'), ln._a(ln.CPEUM, 'Constitución'), html.escape(ln.ESTADOS[a][0]), ln.ARCHIVO, quote(a), quote(a))
    return '<div class="pl-pisos">%s%s%s</div>%s%s' % (p1, pm, p3, ciego, reglas)


def _legislativa_portal(base, ref, e):
    """Su congreso (03-11-2026): lo que gastó en 2024, cuántos lo integran,
    el gasto por curul y la referencia contra el tope del art. 116, fr. II;
    si la ASF lo auditó, lo que dejó."""
    import asistente_legislativo as al
    import leyes_niveles as ln
    cg = al.congresos_estados(base)
    fu = _fuentes(ref, base)
    a, nom = e['abbr'], e['name']
    c = cg[a]
    orden = lambda k: sorted(cg, key=lambda x: -(cg[x][k] if cg[x][k] is not None else -1))
    lg, lx, ln_ = orden('g').index(a) + 1, orden('x').index(a) + 1, orden('n').index(a) + 1
    con_p = [x for x in cg if cg[x]['p'] is not None]
    if c['p'] is None:
        tope = ('<dt>Frente al tope del 0.70 %%</dt><dd>Sin cifra %s <small>la Ciudad de México no figura en la estadística estatal del INEGI: sin su egreso total no hay división</small></dd>' %
                chip('pendiente', 'entidades-' + a.lower()))
    else:
        tope = ('<dt>Frente al tope del 0.70 %%</dt><dd>%s %s <small>%s; de un egreso total del gobierno del estado de %s %s</small></dd>' % (
            pct(c['p'], 2), chip('derivado'),
            'arriba del 0.70 %% como referencia (lugar %d de %d)' % (sorted(con_p, key=lambda x: -cg[x]['p']).index(a) + 1, len(con_p)) if c['p'] > al.TOPE_116 else
            'debajo del 0.70 %% como referencia (lugar %d de %d)' % (sorted(con_p, key=lambda x: -cg[x]['p']).index(a) + 1, len(con_p)),
            mdp(c['egr']), chip('oficial')))
    p1 = ('<article class="pl-piso pl-piso-leg"><p class="pl-piso-n">1 · Lo que gastó su congreso · %d</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%s</b> %s</p>'
          '<dl class="pl-dl"><dt>Su lugar</dt><dd>%d.º de 32 %s <small>del que más gastó al que menos</small></dd>'
          '<dt>Personas legisladoras</dt><dd>%d %s <small>lugar %d de 32 por tamaño, en activo al cierre del último periodo que reportó</small></dd>'
          '<dt>Por curul</dt><dd>%s %s <small>lugar %d de 32; no es lo que gana cada quien, es lo que cuesta la institución por cada lugar del pleno</small></dd>'
          '%s</dl><p class="pl-piso-f">%s %s</p></article>') % (
              c['anio'], mdp(c['g']), chip('oficial'), lg, chip('derivado'), c['n'], chip('oficial'), ln_,
              mdp(c['x']), chip('derivado'), lx, tope, fu['leg'], fu['legn'])
    aud = [x for x in base['poderes']['legislativo']['asfCongresos2024'] if x['congreso'] == 'Congreso de ' + nom]
    if aud:
        ref_asf = {'ASF_NL': 'ref-asf-cp2024-congreso-nl', 'ASF_TLX': 'ref-asf-cp2024-congreso-tlax'}[aud[0]['fuente']]
        p2 = ('<article class="pl-piso pl-piso-asf"><p class="pl-piso-n">2 · Lo que revisó la ASF · Cuenta Pública 2024</p>'
              '<p class="pl-piso-v"><b class="num-tabular">Auditoría %d</b> %s</p><dl class="pl-dl">%s</dl>'
              '<p class="pl-piso-f">La ASF revisó el universo que eligió, no todo el gasto de su congreso. Un monto por aclarar es un saldo sujeto a seguimiento: no equivale a daño definitivo. %s</p></article>') % (
                  aud[0]['auditoria'], chip('oficial'),
                  ''.join('<dt>%s</dt><dd>%s %s <small>p. %s</small></dd>' % (html.escape(x['concepto']), mdp(x['pesos'] / 1e6), chip('oficial'), x['pagina']) for x in aud),
                  ref(ref_asf))
    else:
        p2 = ''
    ciego = ('<p class="pl-dim-nota"><b>Quién se pone el tope.</b> El congreso de %s aprueba cada año el presupuesto de egresos del estado, y dentro de él va el suyo (Constitución, art. 116, fr. II). '
             'La reforma del 23 de abril de 2026 le pide no pasar del 0.70 %% de ese presupuesto, pero la reducción surte efecto al iniciar su legislatura siguiente (transitorio quinto), '
             'y si ya estaba debajo, no puede crecer en términos reales sobre 2026 (transitorio octavo). La cifra de aquí es de 2024, anterior a la reforma: sirve para dimensionar, no para '
             'acusar. La prueba de verdad es su presupuesto de 2027 contra el presupuesto de egresos del estado, los dos en su periódico oficial.</p>') % nom
    reglas = ('<div class="pl-reglas"><p><b>Las reglas de su congreso</b></p><ul>'
              '<li>Aprueba cada año el presupuesto de egresos del estado; su proyecto debe traer los tabuladores desglosados de lo que cobrará su personal (%s, art. 116, fr. II).</li>'
              '<li>Su presupuesto no puede pasar del 0.70 %% del presupuesto de egresos del estado; el ahorro que deje esa reducción va a obra pública (transitorios quinto, séptimo y octavo, DOF 23-04-2026).</li>'
              '<li>Tiene una entidad estatal de fiscalización con autonomía técnica y de gestión, cuyos informes de auditoría son públicos (%s, art. 116, fr. II).</li>'
              '<li>Lo que cobra cada persona de su personal, en bruto y en neto, lo debe publicar en la Plataforma Nacional de Transparencia; la plataforma aún no lo integra %s.</li>'
              '<li>Su presupuesto y sus leyes se publican en: %s. <a href="%s#edo-%s">⚖️ Sus leyes del dinero</a></li></ul>'
              '<p class="pl-ficha-ir"><a href="planisferio.html?d=legislativa&amp;e=%s">Los 32 congresos, en el mapa ➔</a> '
              '<a href="numeros-lo-que-cuestan-los-poderes.html#pd-congreso">Lo que cuestan los Poderes, en la Enciclopedia ➔</a></p></div>') % (
        ln._a(ln.CPEUM, 'Constitución'), ln._a(ln.CPEUM, 'Constitución'), chip('pendiente', 'asesores-congresos-locales'),
        html.escape(ln.ESTADOS[a][0]), ln.ARCHIVO, clave(a), quote(a))
    return '<div class="pl-pisos">%s%s</div>%s%s' % (p1, p2, ciego, reglas)


def _judicial_portal(base, ref, e):
    """Su Poder Judicial (03-11-2026): lo que ejerció en 2024 junto a lo que
    le entró y lo que concluyó, el rezago penal, sus personas juzgadoras, el
    circuito federal con sede en el estado y sus reglas (art. 116, fr. III)."""
    import gestion_judicial as gj
    import indicadores_circuito as ic
    import leyes_niveles as ln
    pj = gj.judiciales_estados(base)
    a, nom = e['abbr'], e['name']
    j = pj[a]
    lugar = lambda k, alto=True: sorted(pj, key=lambda x: -pj[x][k] if alto else pj[x][k]).index(a) + 1
    nac_c100 = 100.0 * gj.EST_TOTAL[1] / gj.EST_TOTAL[0]
    p1 = ('<article class="pl-piso pl-piso-jud"><p class="pl-piso-n">1 · Lo que ejerció su Poder Judicial · 2024</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%s</b> %s</p>'
          '<dl class="pl-dl"><dt>Su lugar</dt><dd>%d.º de 32 %s <small>del que más ejerció al que menos</small></dd>'
          '<dt>Le entraron</dt><dd>%s asuntos %s <small>en primera instancia: penal, adolescentes, civil, familiar y mercantil</small></dd>'
          '<dt>Concluyó</dt><dd>%s asuntos %s <small>%s de cada 100 que entraron %s; en todo el país, %s; lugar %d de 32, del que más concluye al que menos</small></dd>'
          '<dt>Por asunto concluido</dt><dd>%s %s <small>lugar %d de 32; no es lo que cuesta un juicio: el presupuesto paga todo el poder judicial</small></dd>'
          '<dt>Personas juzgadoras</dt><dd>%d %s <small>de todas las materias; %s asuntos concluidos por cada una %s</small></dd>'
          '<dt>Causas penales pendientes</dt><dd>%s %s <small>al cierre de 2024, lugar %d de 32; el INEGI cuenta a cada persona procesada, no cada expediente</small></dd>'
          '<dt>Rezago civil, familiar y mercantil</dt><dd>Sin cifra %s <small>el reporte del censo no lo publica</small></dd>'
          '</dl><p class="pl-piso-f">INEGI, Censo Nacional de Impartición de Justicia Federal y Estatal 2025, reporte de resultados: presupuesto ejercido, gráfica 7 (p. 14); '
          'asuntos ingresados y concluidos, tabla 23 (p. 39, con sus notas 1 y 2); causas penales pendientes, tabla 25 (p. 45); personas juzgadoras, tabla 6 (p. 12) %s. '
          'Las divisiones son nuestras.</p></article>') % (
              mdp(j['g']), chip('oficial'), lugar('g'), chip('derivado'),
              format(j['i'], ','), chip('oficial'),
              format(j['c'], ','), chip('oficial'), pct(j['c100']), chip('derivado'), pct(nac_c100), lugar('c100'),
              _pesos(j['xa']), chip('derivado'), lugar('xa'),
              j['j'], chip('oficial'), format(j['cj'], ','), chip('derivado'),
              format(j['p'], ','), chip('oficial'), lugar('p'),
              chip('pendiente', 'judicial-rezago-civil'),
              ref('ref-inegi-cnijfe2025-rr'))
    n = ic.EDO.index(a) + 1
    circ = 'datos-judicial-por-circuito.html#jud-circ_%d' % n
    if 'id="jud-circ_%d"' % n not in open(os.path.join(RAIZ, circ.split('#')[0]), encoding='utf-8').read():
        raise SystemExit('planisferio: %s no existe' % circ)
    p2 = ('<article class="pl-piso pl-piso-asf"><p class="pl-piso-n">2 · La justicia federal en su territorio</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%s Circuito</b></p>'
          '<p>Además de su Poder Judicial, en %s hay juzgados y tribunales federales: los del %s Circuito, con sede en el estado%s. Esos los paga la Federación, no el estado. '
          'Cuántos asuntos les llegan por cada 100 mil habitantes, cuántos resuelven y cuántos se les acumulan, de 2021 a 2025:</p>'
          '<p class="pl-ficha-ir"><a href="%s">Su circuito judicial federal ➔</a></p></article>') % (
              ic.ORD[n - 1], html.escape(nom), ic.ORD[n - 1], (', que abarca %s %s' % (html.escape(ic.EDO_NOM[a]), ic.ALCANCE[n])) if n in ic.ALCANCE else '', circ)
    ciego = ('<p class="pl-dim-nota"><b>Lo que un solo número no dice.</b> «Concluyó de cada 100» no es el rezago: en lo civil, familiar y mercantil el INEGI cuenta como ingresada '
             'toda demanda, también la que se desecha o se manda corregir, y como concluida solo la que puso fin al pleito. Y un asunto concluido puede ser una sentencia después de años '
             'o un desechamiento del primer día: el censo no los separa. Por eso el dinero va junto a lo que se resolvió con él, para preguntar, no para condenar. '
             'Son cifras que el Poder Judicial de %s le reportó de sí mismo al INEGI.</p>') % html.escape(nom)
    reglas = ('<div class="pl-reglas"><p><b>Las reglas de su Poder Judicial</b></p><ul>'
              '<li>Sus magistradas, magistrados, juezas y jueces se eligen por voto directo y secreto de la ciudadanía, con las mismas bases que el Poder Judicial de la Federación, '
              'y duran nueve años en el cargo (%s, art. 116, fr. III, reformada DOF 15-09-2024).</li>'
              '<li>Debe tener un Tribunal de Disciplina Judicial y un órgano de administración judicial con independencia técnica y de gestión (%s, art. 116, fr. III).</li>'
              '<li>Lo que cobran sus personas juzgadoras no puede ser mayor que lo que recibe la persona titular de la Presidencia de la República, ni disminuir durante su encargo (%s, art. 116, fr. III).</li>'
              '<li>Su presupuesto va dentro del presupuesto de egresos del estado, que aprueba cada año su congreso; se publica en: %s. <a href="%s#edo-%s">⚖️ Sus leyes del dinero</a></li></ul>'
              '<p class="pl-ficha-ir"><a href="planisferio.html?d=judicial&amp;e=%s">Los 32 poderes judiciales, en el mapa ➔</a> '
              '<a href="datos-judicial-gestion.html#jud-gestion_estados">Lo que resuelve con su dinero, en la Enciclopedia ➔</a></p></div>') % (
        ln._a(ln.CPEUM, 'Constitución'), ln._a(ln.CPEUM, 'Constitución'), ln._a(ln.CPEUM, 'Constitución'),
        html.escape(ln.ESTADOS[a][0]), ln.ARCHIVO, clave(a), quote(a))
    return '<div class="pl-pisos">%s%s</div>%s%s' % (p1, p2, ciego, reglas)


def _salud_portal(base, ref, e):
    """Su salud pública (03-11-2026): el IMSS, con su Memoria Estadística 2025
    por OOAD, y el ISSSTE, con el registro sectorial de la DGIS. Las dos
    fuentes no se mezclan; lo que el ISSSTE no deja ver va con su ficha."""
    import gestion_salud as gs
    sa = gs.salud_estados(base)
    a, nom = e['abbr'], e['name']
    h = sa[a]
    tot = gs._estados_doc()['memoria']['total']
    lugar = lambda f, alto=True: sorted(sa, key=lambda x: -f(sa[x]) if alto else f(sa[x])).index(a) + 1
    dos = ''
    if h.get('ooad'):
        dos = '<dt>Sus dos OOAD</dt><dd>%s %s <small>la Memoria las publica por separado; la suma es nuestra</small></dd>' % (
            ' · '.join('%s: %s personas adscritas' % (html.escape(n), format(v['ads'], ',')) for n, v in h['ooad']), chip('oficial'))
    p1 = ('<article class="pl-piso pl-piso-sal"><p class="pl-piso-n">1 · El IMSS en %s · 2025</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%s</b> personas adscritas %s</p>'
          '<dl class="pl-dl"><dt>Su lugar</dt><dd>%d.º de 32 %s <small>de la que más personas adscritas tiene a la que menos; es el %s de las del país</small></dd>%s'
          '<dt>Consultas</dt><dd>%s %s <small>%s por persona adscrita %s, lugar %d de 32 (en el país, %s); %s de especialidad y %s de urgencias</small></dd>'
          '<dt>Egresos hospitalarios</dt><dd>%s %s</dd>'
          '<dt>Cirugías</dt><dd>%s %s <small>%s por cada mil personas adscritas %s</small></dd>'
          '<dt>Camas de hospitalización</dt><dd>%s %s <small>%s por cada mil personas adscritas %s, lugar %d de 32 (en el país, %s)</small></dd>'
          '</dl><p class="pl-piso-f">IMSS, Memoria Estadística 2025, por OOAD: población adscrita a unidad de medicina familiar, cuadro II.10; consultas, cuadro IV.3; egresos e '
          'intervenciones quirúrgicas, cuadro IV.5; camas censables, cuadro XIII.11 (<a href="%s">Memoria</a>). Las divisiones son nuestras.</p></article>') % (
              html.escape(nom), format(h['ads'], ','), chip('oficial'), lugar(lambda r: r['ads']), chip('derivado'), pct(100.0 * h['ads'] / tot['ads']), dos,
              format(h['con'], ','), chip('oficial'), format(h['conx'], '.2f'), chip('derivado'), lugar(lambda r: r['conx']), format(tot['con'] / tot['ads'], '.2f'),
              format(h['esp'], ','), format(h['urg'], ','),
              format(h['egr'], ','), chip('oficial'),
              format(h['iq'], ','), chip('oficial'), format(h['iqk'], '.1f'), chip('derivado'),
              format(h['camc'], ','), chip('oficial'), format(h['camk'], '.2f'), chip('derivado'), lugar(lambda r: r['camk']), format(1000.0 * tot['camc'] / tot['ads'], '.2f'),
              gs.MEMORIA)
    i, m = h['is'], h['im']
    tm = sum(r['is']['med'] for r in sa.values())
    p2 = ('<article class="pl-piso pl-piso-iss"><p class="pl-piso-n">2 · El ISSSTE en %s · 2025</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%s</b> médicas y médicos %s</p>'
          '<dl class="pl-dl"><dt>Su lugar</dt><dd>%d.º de 32 %s <small>tiene el %s de los médicos del ISSSTE en el país</small></dd>'
          '<dt>Unidades</dt><dd>%s %s <small>clínicas, hospitales y unidades de apoyo</small></dd>'
          '<dt>Camas de hospitalización</dt><dd>%s %s</dd>'
          '<dt>Enfermería en contacto con el paciente</dt><dd>%s %s</dd>'
          '<dt>Consultorios</dt><dd>%s %s</dd>'
          '<dt>Frente al IMSS, en el mismo registro</dt><dd>%s médicos del IMSS %s <small>el %s de los médicos de las dos instituciones en el estado son del ISSSTE %s</small></dd>'
          '<dt>Cuántas personas atiende y qué les resolvió</dt><dd>Sin cifra %s <small>su anuario estadístico no responde</small></dd>'
          '</dl><p class="pl-piso-f">Secretaría de Salud, DGIS, Recursos en Salud Sectorial 2025 (<a href="%s">datos abiertos</a>), establecimientos del ISSSTE y del IMSS en %s. '
          'Las sumas y las divisiones son nuestras.</p></article>') % (
              html.escape(nom), format(i['med'], ','), chip('oficial'), lugar(lambda r: r['is']['med']), chip('derivado'), pct(100.0 * i['med'] / tm),
              format(i['u'], ','), chip('oficial'), format(i['cam'], ','), chip('oficial'), format(i['enf'], ','), chip('oficial'), format(i['cons'], ','), chip('oficial'),
              format(m['med'], ','), chip('oficial'), pct(100.0 * i['med'] / (i['med'] + m['med'])), chip('derivado'),
              chip('pendiente', 'salud-issste-servicios'), html.escape(gs.fuente_dgis()['url']), html.escape(nom))
    ciego = ('<p class="pl-dim-nota"><b>Lo que estas cifras no dicen.</b> Cuentan cuánto se hizo y con qué, no si se hizo bien ni a tiempo: ni la Memoria del IMSS ni el registro '
             'de la DGIS dicen cuánto se espera una consulta o una cirugía %s. Los hospitales de alta especialidad del IMSS se cuentan en el estado donde están y atienden a gente de otros. '
             'Las dos fuentes no se mezclan: desde 2025 el IMSS del registro de la DGIS incluye las unidades rurales del antiguo programa IMSS-Bienestar. '
             'Y quien no tiene seguridad social se atiende en el IMSS-Bienestar o en los servicios del estado, que no están en esta dimensión %s.</p>') % (
                 chip('pendiente', 'salud-tiempos-espera'), chip('pendiente', 'salud-imss-bienestar'))
    ir = ('<p class="pl-ficha-ir"><a href="planisferio.html?d=salud&amp;e=%s">El IMSS y el ISSSTE de los 32 estados, en el mapa ➔</a> '
          '<a href="datos-salud-sistema.html#sal-estados">La tabla completa, en la Enciclopedia ➔</a> '
          '<a href="datos-salud-imss.html">El IMSS en el país: lo que cuesta y lo que resuelve ➔</a></p>') % quote(a)
    return '<div class="pl-pisos">%s%s</div>%s%s' % (p1, p2, ciego, ir)


def _administracion_portal(base, ref, e):
    """Su administración pública (03-11-2026): los tres niveles en tres pisos.
    La federal, para comparar; la del estado, con lo que reportó al censo del
    INEGI; la de sus municipios, con lo que ejercieron; y en cada piso, lo que
    la ASF dejó por aclarar. Todo sale de administracion_publica.py."""
    import administracion_publica as apu
    ap = apu.estados(base)
    a, nom = e['abbr'], e['name']
    x = ap[a]
    cp = base['cuenta_publica_asf']['cp2024']
    af = apu.apf_asf(cp)
    lugar = lambda k, alto=True: sorted(ap, key=lambda z: -ap[z][k] if alto else ap[z][k]).index(a) + 1
    pes = lambda v: '$' + format(v, ',')
    p1 = ('<article class="pl-piso pl-piso-fed"><p class="pl-piso-n">1 · La federal, para comparar · 2024</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%s</b> personas %s</p>'
          '<dl class="pl-dl"><dt>Instituciones</dt><dd>%s %s <small>secretarías, organismos y empresas del Estado, con PEMEX y la CFE</small></dd>'
          '<dt>Lo que ejerció</dt><dd>%s %s</dd>'
          '<dt>Contratos por adjudicación directa</dt><dd>%s de cada 100 %s <small>de %s contratos, sin las empresas públicas del Estado</small></dd>'
          '<dt>ASF, Cuenta Pública 2024</dt><dd>%s auditorías · %s por aclarar %s <small>a secretarías, organismos y empresas federales, sin los Poderes ni los autónomos</small></dd>'
          '</dl></article>') % (
              format(apu.APF['per'], ','), chip('oficial'), format(apu.APF['inst'], ','), chip('oficial'), mdp(apu.APF['pres']), chip('oficial'),
              format(apu.APF['ad'], '.1f'), chip('oficial'), format(apu.APF['con'], ','), format(af['aud'], ','), mdp(af['pa']), chip('derivado'))
    p2 = ('<article class="pl-piso pl-piso-ape"><p class="pl-piso-n">2 · La del gobierno de %s · 2024</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%s</b> personas %s</p>'
          '<dl class="pl-dl"><dt>Por cada mil habitantes</dt><dd>%s %s <small>lugar %d de 32, de la que más reporta a la que menos</small></dd>'
          '<dt>Personas titulares de sus instituciones</dt><dd>%s %s <small>una persona puede encabezar más de una; no cuenta las vacantes</small></dd>'
          '<dt>Lo que ejerció</dt><dd>%s %s <small>%s por habitante %s</small></dd>'
          '<dt>Contratos</dt><dd>%s %s <small>%s de cada 100 por adjudicación directa %s, lugar %d de 32 de la que más a la que menos</small></dd>'
          '<dt>ASF, Cuenta Pública 2024</dt><dd>%s auditorías al gobierno del estado · %s por aclarar %s <small>del dinero federal que recibió</small></dd>'
          '<dt>Otros entes, según la ASF</dt><dd>%s auditorías · %s por aclarar %s <small>lo que la ASF agrupa como «Otros»</small></dd>'
          '</dl></article>') % (
              html.escape(nom), format(x['per'], ','), chip('oficial'), format(x['perk'], '.1f'), chip('derivado'), lugar('perk'),
              format(x['tit'], ','), chip('oficial'), mdp(x['pres']), chip('oficial'), pes(x['presp']), chip('derivado'),
              format(x['con'], ','), chip('oficial'), format(x['ad'], '.1f'), chip('oficial'), lugar('ad'),
              format(x['ga'], ','), mdp(x['gpa']), chip('oficial'), format(x['oa'], ','), mdp(x['opa']), chip('oficial'))
    p3 = ('<article class="pl-piso pl-piso-apm"><p class="pl-piso-n">3 · La de sus %s · 2024</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%s</b> ejercidos %s</p>'
          '<dl class="pl-dl"><dt>Por habitante</dt><dd>%s %s</dd>'
          '<dt>ASF, Cuenta Pública 2024</dt><dd>%s auditorías · %s por aclarar %s <small>la ASF revisa a una parte de los municipios cada año</small></dd>'
          '<dt>Lo que hacen</dt><dd>Agua, drenaje, alumbrado, limpia, mercados, panteones, rastro, calles y parques, seguridad y tránsito %s <small>Constitución, art. 115, fr. III</small></dd>'
          '</dl></article>') % (
              'alcaldías' if a == 'CDMX' else 'municipios', mdp(x['mpres']), chip('oficial'), pes(x['mpresp']), chip('derivado'),
              format(x['ma'], ','), mdp(x['mpa']), chip('oficial'), chip('oficial'))
    fu = ('<p class="pl-piso-f">%s: personal, tabla 3, p. 8; titulares, tabla 1, p. 5; presupuesto, gráfica 5, p. 11; contratos, tabla 9, p. 31 (<a href="%s">PDF</a>). '
          '%s: presupuesto municipal, gráfica 23, p. 26 (<a href="%s">PDF</a>). %s (<a href="%s">PDF</a>). Las divisiones son nuestras, con la población de la base.</p>') % (
              html.escape(apu.CNGE['tx']), apu.CNGE['url'], html.escape(apu.CNGMD['tx']), apu.CNGMD['url'],
              html.escape(apu.fuente_asf(base)['tx']), html.escape(apu.fuente_asf(base)['url']))
    ciego = ('<p class="pl-dim-nota"><b>Lo que estas cifras no dicen.</b> Lo del INEGI es lo que el gobierno de %s le contestó a su censo, no una auditoría, y el censo no dice qué organismos '
             'incluyó en su cuenta. La adjudicación directa cuenta contratos, no pesos, y es legal en los casos que fija la ley. Un monto por aclarar no es un desfalco comprobado. '
             'Y la ASF solo revisa el dinero federal: el propio del estado y de sus municipios lo revisa la entidad de fiscalización superior del estado, '
             'cuyos informes la plataforma todavía no ha integrado.</p>') % html.escape(nom)
    ir = ('<p class="pl-ficha-ir"><a href="planisferio.html?d=administracion&amp;e=%s">Las 32 administraciones, en el mapa ➔</a> '
          '<a href="datos-administracion-publica-niveles.html#adm-estados">La tabla completa, en la Enciclopedia ➔</a> '
          '<a href="datos-administracion-publica-auditorias.html">Quién la audita y cómo contrata ➔</a></p>') % quote(a)
    return '<div class="pl-pisos">%s%s%s</div>%s%s%s' % (p1, p2, p3, fu, ciego, ir)


def _ambiental_portal(base, ref, e):
    """Sus recursos naturales (03-11-2026): sus acuíferos, sus incendios forestales, sus concesiones mineras, su refinería de PEMEX, si tiene,
    y los siete ramos de recursos con quién los explota y quién los audita,
    en esquema. Todo sale de recursos_naturales.py."""
    import recursos_naturales as rn
    a, nom = e['abbr'], e['name']
    r = rn.refinerias_estados().get(a)
    fu = _fuentes(ref)
    ef = 'Petróleos Mexicanos, estados financieros consolidados 2025, notas, pp. 59 y 63 %s' % ref('ref-pemex-cp2025')
    if r:
        d = lambda v: ('<b class="num-tabular">%s</b> %s' % (rn._mdps(v), chip('oficial'))) if v is not None else 'no figura en la nota'
        olmeca = r['id'] == 'olmeca'
        p1 = ('<article class="pl-piso pl-piso-amb"><p class="pl-piso-n">🛢️ %s · %s</p>'
              '<p class="pl-piso-v"><b class="num-tabular">%s mil</b> barriles diarios de crudo en junio de 2026 %s</p>'
              '<dl class="pl-dl"><dt>Su lugar entre las siete</dt><dd>%d.º %s</dd>'
              '<dt>Promedio de sep-25 a jun-26</dt><dd><b class="num-tabular">%s mil</b> %s</dd>'
              '<dt>Su mejor mes</dt><dd><b class="num-tabular">%s mil</b> en %s %s</dd>'
              '<dt>Su capacidad de destilación (2024)</dt><dd><b class="num-tabular">%s mil</b> %s</dd>'
              '<dt>Cuánto usó de ella, en promedio</dt><dd><b class="num-tabular">%s %%</b> %s</dd>'
              '<dt>Valor perdido (−) o recuperado (+) en libros, 2025</dt><dd>%s</dd>'
              '<dt>Igual, 2024</dt><dd>%s</dd></dl>'
              '<p class="pl-piso-f">Crudo procesado: %s Capacidad y uso: %s Valor en libros: %s.%s</p></article>') % (
            html.escape(r['n']), html.escape(r['sede']), format(r['jun'], ','), chip('oficial'), r['lug'], chip('derivado'),
            format(r['prom'], ',.1f'), chip('derivado'), format(r['max'], ','), r['mmax'], chip('oficial'),
            format(r['cap'], ','), chip('oficial'), format(r['uso'], '.1f'), chip('derivado'),
            'es de una filial de PEMEX, que se la arrienda: no se mide como unidad propia' if olmeca else d(r['d25']),
            '—' if olmeca else d(r['d24']), fu['refj'], fu['refu'], ef,
            ' <a href="auditoria-dos-bocas.html">📖 Lo que costó: la investigación de Dos Bocas ➔</a>' if olmeca else
            (' <a href="auditoria-refineria-tula.html">📖 La refinería que no se construyó en Tula ➔</a>' if r['id'] == 'tula' else ''))
        ciego = ('<p class="pl-dim-nota"><b>Lo que esas cifras no dicen.</b> Procesar crudo no es producir gasolina, y un mes no es la regla. El valor que pierde o recupera en los libros '
                 'es una estimación de lo que PEMEX espera que genere, con su precio, su tipo de cambio y su tasa; no es dinero que salió de la caja. Y el porcentaje de uso dice cuánto, '
                 'no por qué: falta de crudo, mantenimiento o una planta que no arranca se ven igual.</p>')
    else:
        p1 = ('<article class="pl-piso pl-piso-amb"><p class="pl-piso-n">🛢️ Refinación</p><p class="pl-piso-v"><b>No tiene refinería de PEMEX</b></p>'
              '<p>Las siete refinerías del Sistema Nacional de Refinación están en Nuevo León, Tamaulipas, Veracruz, Guanajuato, Oaxaca, Hidalgo y Tabasco. '
              'No tener refinería no quiere decir no tener problemas ambientales.</p></article>')
        ciego = ''
    m = rn.mineria([x['abbr'] for x in base['estados']]).get(a)
    if m:
        prod = {'mayor': 'Es una de las diez entidades que dan el 94.9 % del valor de la producción minera.',
                'menor': 'Está entre las 17 entidades que juntas dan el 5.2 % del valor de la producción minera.',
                None: 'No aparece entre las entidades con producción minera del Segundo Informe: tener concesiones no es tener minas trabajando.'}[m['prod']]
        p2 = ('<article class="pl-piso pl-piso-amb"><p class="pl-piso-n">⛏️ Concesiones mineras · marzo de 2024</p>'
              '<p class="pl-piso-v"><b class="num-tabular">%s títulos</b> vigentes %s</p>'
              '<dl class="pl-dl"><dt>Hectáreas que amparan</dt><dd><b class="num-tabular">%s</b> %s</dd>'
              '<dt>Su lugar entre las 30 con concesiones</dt><dd>%d.º %s</dd>'
              '<dt>Su parte de los títulos del país</dt><dd><b class="num-tabular">%s %%</b> %s</dd>'
              '<dt>Hectáreas por título</dt><dd><b class="num-tabular">%s</b> %s</dd>%s</dl>'
              '<p>%s</p><p class="pl-piso-f">%s</p></article>') % (
            format(m['t'], ','), chip('oficial'), format(m['ha'], ','), chip('oficial'), m['lug'], chip('derivado'), format(m['pt'], '.2f'), chip('derivado'),
            format(m['hxt'], ','), chip('derivado'),
            ('<dt>Al 30 de junio de 2026</dt><dd><b class="num-tabular">%s títulos</b> %s (%s%s %s)</dd>' % (
                format(m['t26'], ','), chip('oficial'), '−' if m['t26'] < m['t'] else '+', format(abs(m['t26'] - m['t']), ','), chip('derivado'))) if m['t26'] is not None else
            ('<dt>Al día</dt><dd>La Secretaría de Economía no ha publicado su cifra por estado después de marzo de 2024 %s</dd>' % chip('pendiente', 'mineria-por-estado-2026')),
            prod, fu['minT'] + ' Junio de 2026 y producción: Segundo Informe de Gobierno, p. 444 %s.' % ref('ref-presidencia-2ig'))
    else:
        p2 = ('<article class="pl-piso pl-piso-amb"><p class="pl-piso-n">⛏️ Concesiones mineras</p><p class="pl-piso-v"><b>No figura en el cuadro de la Dirección General de Minas</b></p>'
              '<p>El cuadro de marzo de 2024 trae 30 entidades. No quiere decir que no se extraiga nada de su suelo: la Ley de Minería no se aplica a la grava, la arena y las rocas '
              'para construir (art. 5, fr. IV), que regulan los estados y municipios.</p></article>')
    w = rn.acuiferos([x['abbr'] for x in base['estados']])[a]
    k27 = ''
    if w['s27']:
        k27 = ('<dt>Sobreexplotados que la CONAGUA mide con pozos (2026)</dt><dd>%s %s%s</dd>') % (
            html.escape(rn._y([n for c, n, d in w['s27']])), chip('oficial'),
            ''.join(' · %s todavía tiene disponibilidad en el Acuerdo de 2023 (+%s hm³)' % (html.escape(n), format(d, '.2f')) for c, n, d in w['s27'] if d > 0))
    p0 = ('<article class="pl-piso pl-piso-amb"><p class="pl-piso-n">💧 Sus acuíferos · corte al 30 de diciembre de 2022</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%d de %d</b> sin agua para concesionar %s</p>'
          '<dl class="pl-dl"><dt>De cada 100 acuíferos</dt><dd><b class="num-tabular">%s</b> sin disponibilidad %s</dd>'
          '<dt>Suma de sus déficits</dt><dd>%s</dd>'
          '<dt>Suma de lo que aún tienen disponible</dt><dd><b class="num-tabular">%s hm³</b> al año %s</dd>%s</dl>'
          '<p>La disponibilidad es el agua que todavía se puede concesionar, no la que queda en el subsuelo, y mide cantidad, no calidad. La ley pide revisarla al menos cada '
          'dos años (Ley de Aguas Nacionales, art. 22); este corte es el último publicado %s.</p>'
          '<p class="pl-piso-f">%s%s</p></article>') % (
        w['sin'], w['n'], chip('oficial'), format(w['ps'], '.1f'), chip('derivado'),
        ('<b class="num-tabular">%s hm³</b> al año %s · lugar %d de %d con déficit' % (format(w['def'], ',.1f'), chip('derivado'), w['lug'],
                                                                                     sum(1 for v in rn.ACUIFEROS.values() if v[3] > 0))) if w['def'] > 0 else 'ninguno estaba en déficit',
        format(w['disp'], ',.1f'), chip('derivado'), k27, chip('pendiente', 'acuiferos-disponibilidad-nueva'),
        fu['acuD'], (' Sobreexplotados: Segundo Informe de Gobierno, p. 513 %s.' % ref('ref-presidencia-2ig')) if w['s27'] else '')
    z = rn.incendios([x['abbr'] for x in base['estados']])[a]
    b = rn.forestal([x['abbr'] for x in base['estados']])[a]
    ps = ('<article class="pl-piso pl-piso-amb"><p class="pl-piso-n">🌲 Su superficie forestal · mapa de 2018</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%s ha</b> %s</p>'
          '<dl class="pl-dl"><dt>Su lugar</dt><dd>%d.º de 32 · %s del país %s</dd>'
          '<dt>De cada 100 hectáreas, arboladas</dt><dd><b class="num-tabular">%s</b> %s</dd>'
          '<dt>De cada 100, vegetación secundaria</dt><dd><b class="num-tabular">%s</b> %s</dd>'
          '<dt>Lo que el fuego de 2025 afectó, de cada 100</dt><dd><b class="num-tabular">%s</b> %s · lugar %d de 32</dd></dl>'
          '<p>«Forestal» no es «bosque»: incluye matorrales y otras áreas. Arbolada es bosque, selva, manglar y otras asociaciones; secundaria, la vegetación que ya fue alterada y se recupera. '
          'Lo del fuego es una proporción con el mapa de 2018, no la parte que se perdió.</p>'
          '<p class="pl-piso-f">%s</p></article>') % (
        format(b['sf'], ',.1f'), chip('oficial'), b['lug'], ('%s %%' % format(b['pnac'], '.1f')) if b['pnac'] >= 0.05 else 'menos del 0.1 %', chip('derivado'),
        format(b['parb'], '.1f'), chip('derivado'), format(b['psec'], '.1f'), chip('derivado'),
        format(b['pq'], '.1f') if b['pq'] >= 0.05 else 'menos de 0.1', chip('derivado'), b['lq'], fu['sfT'] + ' Tabla 2, pp. 10-11. Porcentajes y lugares: cuenta nuestra.')
    q = rn.pesca([x['abbr'] for x in base['estados']])[a]
    sg = lambda v: ('+' if v > 0 else '−' if v < 0 else '') + format(abs(v), '.1f') + ' %'
    if q['t']:
        pp = ('<article class="pl-piso pl-piso-amb"><p class="pl-piso-n">🐟 Su pesca y su acuacultura · 2025</p>'
              '<p class="pl-piso-v"><b class="num-tabular">%s t</b> en peso vivo %s</p>'
              '<dl class="pl-dl"><dt>Su lugar</dt><dd>%d.º por toneladas · %s del país %s</dd>'
              '<dt>Su valor, a precio de playa</dt><dd><b class="num-tabular">%s</b> %s · lugar %d por valor</dd>'
              '<dt>De cada 100 toneladas, de cultivo</dt><dd><b class="num-tabular">%s</b> %s</dd>'
              '<dt>Contra 2024</dt><dd>toneladas %s · valor %s %s</dd></dl>'
              '<p>Es lo que se declaró en los avisos de arribo y de cosecha (Ley General de Pesca y Acuacultura Sustentables, art. 4), no todo lo que se pescó, y no dice si las especies '
              'aguantan: eso lo dice la Carta Nacional Pesquera (art. 32). El valor es en pesos de cada año, sin descontar la inflación.%s</p>'
              '<p class="pl-piso-f">%s Captura y acuacultura: cuadros 2.5.8 y 2.5.10. Porcentajes, cambios y lugares: cuenta nuestra.</p></article>') % (
            format(q['t'], ','), chip('oficial'), q['lt'], ('%s %%' % format(q['pt'], '.1f')) if q['pt'] >= 0.05 else 'menos del 0.1 %', chip('derivado'),
            mdp(q['mdp']), chip('oficial'), q['lv'], format(q['pacu'], '.1f'), chip('derivado'), sg(q['ct']), sg(q['cv']), chip('derivado'),
            ' Los cuadros 2.1.10 y 2.1.11 del Anuario imprimen cruzadas las cifras de Jalisco y Colima; aquí van las de sus series.' if a in rn.PE_CRUCE else '', fu['peT'])
    else:
        pp = ('<article class="pl-piso pl-piso-amb"><p class="pl-piso-n">🐟 Su pesca y su acuacultura · 2025</p>'
              '<p class="pl-piso-v">No registró producción en 2025 %s</p>'
              '<p>En 2024 había registrado <b class="num-tabular">%s t</b> %s. No registrar no es lo mismo que no tener pesca: el Anuario es lo que se declaró en los avisos de arribo y de cosecha.</p>'
              '<p class="pl-piso-f">%s</p></article>') % (chip('oficial'), format(q['t24'], ','), chip('oficial'), fu['peT'])
    pf = ('<article class="pl-piso pl-piso-amb"><p class="pl-piso-n">🔥 Sus incendios forestales · 2025</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%s ha</b> afectadas %s</p>'
          '<dl class="pl-dl"><dt>Incendios</dt><dd><b class="num-tabular">%s</b> %s · lugar %d de 32</dd>'
          '<dt>Su lugar por superficie</dt><dd>%d.º de 32 %s</dd>'
          '<dt>De cada 100 hectáreas, de árboles</dt><dd><b class="num-tabular">%s</b> %s</dd>'
          '<dt>Hectáreas por incendio</dt><dd><b class="num-tabular">%s</b> %s</dd>'
          '<dt>Llegada de la brigada, en promedio</dt><dd><b class="num-tabular">%s</b> horas %s</dd>'
          '<dt>En 2024</dt><dd><b class="num-tabular">%s ha</b> %s · %s</dd></dl>'
          '<p>Superficie afectada no es bosque perdido: el daño depende del impacto, y la mayor parte del fuego del país corre por pasto y matorral. El combate inicial le toca al '
          'municipio, luego al estado y luego a la CONAFOR (Ley General de Desarrollo Forestal Sustentable, art. 119); quien tiene el terreno debe restaurarlo en dos años (art. 121).</p>'
          '<p class="pl-piso-f">%s Cierre de 2024: <a href="%s">PDF</a>. Lugares, porcentajes y promedios: cuenta nuestra.</p></article>') % (
        format(z['ha'], ',.2f'), chip('oficial'), format(z['n'], ','), chip('oficial'), z['ln'], z['lh'], chip('derivado'), format(z['parb'], '.1f'), chip('derivado'),
        format(z['hxi'], ',.1f'), chip('derivado'), z['lleg'], chip('oficial'), format(z['ha24'], ',.2f'), chip('oficial'),
        ('%s%s %% %s' % ('+' if z['cam'] > 0 else '−', format(abs(z['cam']), '.1f'), chip('derivado'))) if z['cam'] else 'igual',
        fu['incH'], html.escape(rn.INC_DOC24['url']))
    ramos = ''.join('<li><span aria-hidden="true">%s</span> <b>%s</b> <small>(%s)</small><br>Quién lo explota: %s<br><small>Quién lo regula: %s</small></li>' % (
        x['ico'], html.escape(x['nom']), html.escape(x['renov'].split(',')[0]), html.escape(x['quien']), html.escape(x['autoridad'].split(' (')[0]))
        for x in rn.RAMOS)
    esquema = ('<div class="pl-reglas"><p><b>Los recursos de su territorio, por sector</b></p>'
               '<p>Sus denuncias ante la PROFEPA ya tienen ley y autoridad, pero todavía no su cifra para %s %s. Así se reparte quién explota cada recurso:</p>'
               '<ul class="pl-sectores">%s</ul>'
               '<p class="pl-ficha-ir"><a href="%s">🌎 Cómo se audita cada recurso ➔</a> '
               '<a href="planisferio.html?d=ambiental&amp;e=%s">Las siete refinerías en el mapa ➔</a> '
               '<a href="datos-ambiente-megaobras.html?e=%s#abMapaObras">Sus obras con alerta ambiental ➔</a></p></div>') % (
        html.escape(nom), chip('pendiente', 'ambiente-por-estado'), ramos, rn.ARCHIVO, quote(a), quote(a))
    return '<div class="pl-pisos">%s%s%s%s%s%s</div>%s%s' % (p0, ps, pf, pp, p2, p1, ciego, esquema)


def pagina_portal(base, ref, e, padron, prev, sig, iv, dv):
    a = e['abbr']
    C = base['fiscalEntidades']['campos']
    sin = set(C['recaudacionPropia'].get('sinFuente', []))
    m = padron['ent'][a]
    fu = _fuentes(ref)
    nom = e['name']
    # 1 · Los tres presupuestos
    p1 = ('<article class="pl-piso pl-piso-fed"><p class="pl-piso-n">1 · Lo que baja de la Federación · 2026</p>'
          '<p class="pl-piso-v"><b class="num-tabular">%s</b> %s</p>'
          '<dl class="pl-dl"><dt>Participaciones (Ramo 28)</dt><dd>%s %s <small>el estado decide en qué</small></dd>'
          '<dt>Aportaciones (Ramo 33)</dt><dd>%s %s <small>llegan con destino fijado por ley</small></dd>'
          '<dt>Por habitante</dt><dd>%s %s</dd></dl><p class="pl-piso-f">%s Por habitante: entre la población del CONAPO a mitad de 2026.</p></article>' % (
              mdp(e['gasto']), chip('derivado'), mdp(e['ramo28']), chip('oficial'), mdp(e['ramo33']), chip('oficial'),
              _pesos(e['pc']), chip('derivado'), fu['fed']))
    pend_est = 'entidades-' + a.lower()
    if a in sin:
        p2 = ('<article class="pl-piso pl-piso-est"><p class="pl-piso-n">2 · Lo que cobra el estado · 2024</p>'
              '<p class="pl-piso-v"><b>Sin cifra cotejada</b> %s</p><p>%s</p></article>' % (
                  chip('pendiente', pend_est), C['recaudacionPropia']['motivo'] + '.'))
    else:
        p2 = ('<article class="pl-piso pl-piso-est"><p class="pl-piso-n">2 · Lo que cobra el estado · 2024</p>'
              '<p class="pl-piso-v"><b class="num-tabular">%s</b> %s</p>'
              '<dl class="pl-dl"><dt>Convenios con dependencias federales</dt><dd>%s %s</dd>'
              '<dt>Dependencia de la Federación</dt><dd>%s %s <small>de cada $100 que ingresó, sin contar deuda, %s llegaron de la Federación</small></dd></dl>'
              '<p class="pl-piso-f">%s</p></article>' % (
                  mdp(e['recaudacionPropia']), chip('derivado'), mdp(e['convenios']), chip('oficial'),
                  pct(e['dep']), chip('derivado'), '$' + format(e['dep'], '.1f'), fu['est']))
    if m['conCifra']:
        t = m['tot']
        p3 = ('<article class="pl-piso pl-piso-mun"><p class="pl-piso-n">3 · Lo que ingresan sus municipios · 2024</p>'
              '<p class="pl-piso-v"><b class="num-tabular">%s</b> %s</p>'
              '<dl class="pl-dl"><dt>Municipios con cuenta</dt><dd>%d de %d</dd>'
              '<dt>Participaciones</dt><dd>%s</dd><dt>Aportaciones</dt><dd>%s</dd>'
              '<dt>Predial que cobraron</dt><dd>%s</dd></dl><p class="pl-piso-f">%s</p></article>' % (
                  mdp(t['ing'] / 1e6), chip('derivado'), m['conCifra'], m['n'], mdp(t['part'] / 1e6), mdp(t['aport'] / 1e6),
                  mdp(t['predial'] / 1e6), fu['mun']))
    else:
        p3 = ('<article class="pl-piso pl-piso-mun"><p class="pl-piso-n">3 · Lo que ingresan sus %d demarcaciones · 2024</p>'
              '<p class="pl-piso-v"><b>Sin cuenta municipal</b> %s</p><p>Las alcaldías de la Ciudad de México no rinden cuenta municipal al INEGI: '
              'su dinero va dentro del presupuesto de la Ciudad. Por eso aquí no hay suma, y ponerle cero falsearía la cifra.</p></article>' % (
                  m['n'], chip('pendiente', 'municipios-sin-cuenta')))
    # «No cuadra» (04-11-2026, el Planisferio como matriz de los mapas): lo que
    # el estado reportó al INEGI como recibido contra lo que la Cuenta Pública
    # dice que la Federación le pagó, con la misma cuenta del mapa
    # (cuadre_obras() de territorio_modulos.py).
    cua = tm.cuadre_obras(base)[0][a]
    x = base['inspector_estatal']['entidades'].get(a) or {}
    if cua is None:
        p4 = ('<article class="pl-piso pl-piso-cua"><p class="pl-piso-n">4 · No cuadra: lo recibido contra lo pagado · 2024</p>'
              '<p class="pl-piso-v"><b>Sin cifra</b> %s</p><p>%s no figura en la estadística estatal del INEGI: no hay segunda cifra con que contrastar.</p></article>' % (
                  chip('pendiente', 'entidades-' + a.lower()), html.escape(nom)))
    else:
        p4 = ('<article class="pl-piso pl-piso-cua"><p class="pl-piso-n">4 · No cuadra: lo recibido contra lo pagado · 2024</p>'
              '<p class="pl-piso-v"><b class="num-tabular">%s</b> %s <small>de diferencia</small></p>'
              '<dl class="pl-dl"><dt>Lo que el estado reportó al INEGI como recibido</dt><dd>%s %s</dd>'
              '<dt>Lo que la Cuenta Pública dice que le pagó</dt><dd>%s %s</dd></dl>'
              '<p>Ramos 28 y 33, sin convenios; cada lado es la suma de sus dos ramos. Una diferencia puede tener explicación (retenciones por adeudos, pagos a un fideicomiso de deuda, registros en otro año), '
              'pero esa explicación tiene que darla el gobierno.</p>'
              '<p class="pl-piso-f">%s <a href="planisferio.html?d=financiera&amp;l=cua&amp;e=%s">Las 32 en el mapa ➔</a></p></article>' % (
                  format(cua, '.2f') + ' %', chip('derivado'),
                  mdp(x['inegiPart'] + x['inegiAportSinConvenios']), chip('derivado'), mdp(x['cpR28'] + x['cpR33']), chip('derivado'),
                  tm.fuente_cuadre(ref), quote(a)))
    # 2 · El ritmo
    s = _ritmo(e['gasto'])
    ritmo = ('<div class="pl-conts pl-conts-1"><article class="pl-cont" data-anual="%.1f">'
             '<p class="pl-cont-n"><span aria-hidden="true">⏱️</span> Lo que le baja de la Federación, a su ritmo</p>'
             '<p class="pl-cont-v"><b class="num-tabular">%s por segundo</b> %s</p>'
             '<p class="pl-cont-vivo" aria-live="off">Desde que abriste esta página: <b class="num-tabular pl-vivo">$0</b></p>'
             '<p class="pl-cont-que">Operación: %s ÷ 31,536,000 segundos del año. Sirve para dimensionar la cifra: no es dinero que se mueva en tiempo real, '
             'ni dice cuándo llega cada pago (las participaciones se entregan cada mes y las aportaciones según su calendario).</p></article></div>' % (
                 e['gasto'], _pesos(s), chip('derivado'), mdp(e['gasto'])))
    # 2 bis · Su deuda (Sistema de Alertas, Cuenta Pública 2025)
    g = geo_mun(m['cve'])
    deuda = _deuda_portal(base, ref, e, _deuda_mun(ref, e, m, dv, bool(g)))
    inversion = _inversion_portal(base, ref, e, _inversion_mun(ref, e, m, iv, bool(g)))
    # 3 · Los municipios
    filas = []
    for r in m['lista']:
        if len(r) < 3:
            filas.append('<tr data-c="%s" data-n="%s"><th scope="row">%s</th><td colspan="7" class="pl-sin">Sin cuenta de 2024 %s</td></tr>' % (
                r[0], json.dumps(r[1].lower(), ensure_ascii=False)[1:-1], r[1], chip('pendiente', 'municipios-sin-cuenta')))
            continue
        cve, n, ing, part, aport, fortamun, fismdf, predial, propios, egr = r[:10]
        dep = (part + aport) / ing * 100 if ing else None
        inv = iv['mun'][m['cve'] + cve][0]
        dd = dv['mun'][m['cve'] + cve]
        dpag = dd[1] + dd[2] + dd[3]
        filas.append('<tr data-c="%s" data-n="%s" data-ing="%d" data-predial="%d" data-dep="%s" data-inv="%d" data-dpag="%d"><th scope="row">%s</th>'
                     '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                         cve, json.dumps(n.lower(), ensure_ascii=False)[1:-1], ing, predial, '%.2f' % dep if dep is not None else '', inv, dpag,
                         n, mdp(ing / 1e6), mdp(part / 1e6), mdp(aport / 1e6), mdp(predial / 1e6), pct(dep) if dep is not None else '—', mdp(inv / 1e6), mdp(dpag / 1e6)))
    tabla = ('<div class="pl-mun-mandos"><label class="pl-sel"><span>Buscar municipio</span><input type="search" id="plMunBusca" placeholder="Escribe un nombre" autocomplete="off"></label>'
             '<label class="pl-sel"><span>Ordenar por</span><select id="plMunOrden"><option value="n">Nombre (A–Z)</option><option value="ing">Ingreso total</option>'
             '<option value="predial">Predial cobrado</option><option value="dep">Dependencia de transferencias</option><option value="inv">Inversión pública</option><option value="dpag">Pagó de deuda</option></select></label></div>'
             '<div class="pl-tabla-caja"><table class="pl-tabla" id="plMun"><caption>Los %d municipios de %s en el catálogo del INEGI, con sus cuentas de %d</caption>'
             '<thead><tr><th scope="col">Municipio</th><th scope="col">Ingreso total</th><th scope="col">Participaciones</th><th scope="col">Aportaciones</th>'
             '<th scope="col">Predial</th><th scope="col">Dependencia</th><th scope="col">Inversión pública</th><th scope="col">Pagó de deuda</th></tr></thead><tbody>%s</tbody></table></div>'
             '<p class="pl-pie">Cifras de cada municipio: INEGI, finanzas públicas municipales %d %s, en millones de pesos (mdp) %s. '
             'La dependencia es (participaciones + aportaciones) ÷ ingreso total × 100 %s: cuánto de lo que ingresó llegó de fuera. La inversión pública es su capítulo de egresos de obra y proyectos productivos; «pagó de deuda», el capital, los intereses y las comisiones de sus créditos en el año (no lo que debe).</p>' % (
                 m['n'], nom, padron['anio'], ''.join(filas), padron['anio'], ref('ref-inegi-efipem'), chip('oficial'), chip('derivado')))
    mapa_mun = _mapa_mun(e, m, g, ref, padron, iv, dv) if g else ''
    # 4 · Las otras dimensiones y el Auditor
    dl = _congresos(base)
    puertas = []
    for i, ico, dn, que, ir, ire, _pinta in DIMENSIONES:
        if not ir:
            continue
        liga = ire % a if ire and '%s' in ire and i != 'legislativa' else ir
        if i == 'legislativa':
            liga = ire % dl[a] if dl.get(a) else ir
        puertas.append('<a class="pl-puerta" href="%s"><span aria-hidden="true">%s</span><span><b>%s</b><small>%s</small></span></a>' % (
            liga, ico, dn, que))
    auditor = [
        ('herramienta-inspector-entes.html#ente=estatal:%s' % a, '🏢', 'Estado de cuenta y salud financiera',
         'Su ficha técnica en el Auditor de entes: si gastó lo que aprobó, si rindió cuentas, su dictamen y su ritmo en vivo.'),
        ('numeros-las-32-entidades.html?e=%s#circuito' % a, '🔄', 'Su circuito del dinero',
         'Cuánto le baja, cuánto cobra y qué tan dependiente resulta la suma.'),
        ('numeros-mapa-del-gasto-federalizado.html?l=asf&e=%s' % a, '🔎', 'Lo que la ASF dejó por aclarar',
         'El dinero federal de 2024 que la Auditoría Superior observó en la entidad.'),
        ('herramienta-inspector-pregunta.html?q=%s' % quote('Estado de cuenta de ' + nom), '🔍', 'Pregúntale al Auditor',
         'Lo que quieras saber de %s, con su fuente.' % nom),
    ]
    for ir, *_ in auditor:
        if not _existe(ir):
            raise SystemExit('planisferio: %s no existe' % ir)
    puertas_aud = ''.join('<a class="pl-puerta" href="%s"><span aria-hidden="true">%s</span><span><b>%s</b><small>%s</small></span></a>' % x for x in auditor)
    saltos = ('<nav class="pl-saltos" aria-label="Otras entidades"><a href="%s">← %s</a><a href="%s#mapa">🗺️ Volver al mapa</a><a href="%s">%s →</a></nav>' % (
        portal(prev['abbr']), prev['name'], ARCHIVO, portal(sig['abbr']), sig['name']))
    import leyes_niveles
    leyes = leyes_niveles.estado(e, leyes_niveles.municipios(padron, a))
    datos_e = '%s · capital: %s · %s habitantes a mitad de 2026 (CONAPO) %s' % (
        nom, e['capital'], format(e['pobPersonas'], ','), chip('derivado'))
    temas = [
            {'id': 'presupuestos', 'titulo': 'Sus tres presupuestos',
             'texto': ('Un piso por cada orden de gobierno. Los años no se mezclan: lo que baja es de 2026 y lo que cobran el estado y sus municipios, de 2024, el último con cifras definitivas del INEGI. '
                       'El cuarto pone lo que el estado dice que recibió en 2024 junto a lo que la Federación dice que le pagó.'),
             'tarjetas': [], 'bloque': '<div class="pl-pisos">%s%s%s%s</div>' % (p1, p2, p3, p4)},
            {'id': 'ritmo', 'titulo': 'Su contador', 'texto': '', 'tarjetas': [], 'bloque': ritmo},
            {'id': 'deuda', 'titulo': 'Su deuda',
             'texto': ('Lo que debe el gobierno de %s y cuánto le pesa, medido por el Sistema de Alertas de Hacienda con la Cuenta Pública 2025. '
                       'Abajo, lo que sus municipios pagaron por sus créditos y pidieron prestado en 2024, según su propia cuenta al INEGI; su saldo, que también mide Hacienda, sigue pendiente.') % nom,
             'tarjetas': [], 'bloque': deuda},
            {'id': 'inversion', 'titulo': 'Su inversión',
             'texto': ('La obra que hizo el gobierno de %s en 2024, por las dos vías que usa un gobierno estatal (la que contrata él mismo y la que les encarga a sus organismos), '
                       'la obra que pagaron sus municipios y lo que la Auditoría Superior dejó por aclarar del dinero federal que recibió.') % nom,
             'tarjetas': [], 'bloque': inversion},
            {'id': 'legislativa', 'titulo': 'Su congreso',
             'texto': ('Lo que gastó el congreso de %s en 2024, cuántas personas legisladoras lo integran, lo que cuesta por curul y cómo se compara con el tope que la Constitución '
                       'les pone desde abril de 2026. Las cifras son del censo de los congresos estatales del INEGI.') % nom,
             'tarjetas': [], 'bloque': _legislativa_portal(base, ref, e)},
            {'id': 'judicial', 'titulo': 'Su Poder Judicial',
             'texto': ('Lo que ejerció el Poder Judicial de %s en 2024, junto a lo que le llegó y lo que concluyó con ese dinero, las causas penales que se le acumulan '
                       'y sus personas juzgadoras. Las cifras son del censo de impartición de justicia del INEGI.') % nom,
             'tarjetas': [], 'bloque': _judicial_portal(base, ref, e)},
            {'id': 'salud', 'titulo': 'Su salud pública: el IMSS y el ISSSTE',
             'texto': ('A cuántas personas tiene adscritas el IMSS en %s, cuántas consultas y cirugías les dio y con cuántas camas, y con cuántos médicos, camas y unidades '
                       'cuenta el ISSSTE. Del IMSS, su Memoria Estadística 2025; del ISSSTE, el registro de recursos de la Secretaría de Salud, porque su anuario no responde.') % nom,
             'tarjetas': [], 'bloque': _salud_portal(base, ref, e)},
            {'id': 'social', 'titulo': 'Su pobreza y sus carencias',
             'texto': ('Cuántas personas viven en pobreza en %s, cuántas en pobreza extrema, sus seis carencias sociales frente al país y lo que la Federación le aporta '
                       'por persona en pobreza. Las cifras son de la medición de la pobreza 2024 del INEGI.') % nom,
             'tarjetas': [], 'bloque': _social_portal(base, ref, e)},
            {'id': 'administracion', 'titulo': 'Su administración pública',
             'texto': ('El gobierno que ejecuta, en los tres niveles: cuánta gente tiene la administración de %s, cuánto ejerció en 2024 y cuántos contratos dio sin concurso; '
                       'cuánto ejercieron sus municipios; y lo que la Auditoría Superior de la Federación dejó por aclarar a cada uno. Arriba, la federal, para comparar.') % nom,
             'tarjetas': [], 'bloque': _administracion_portal(base, ref, e)},
            {'id': 'ambiental', 'titulo': 'Sus recursos naturales',
             'texto': ('Quién explota los recursos de %s y quién los audita. Empieza por lo que ya tiene cifra: sus acuíferos y cuántos ya no tienen agua para concesionar, '
                       'su superficie forestal y sus incendios forestales de 2025, su pesca y su acuacultura, sus concesiones mineras y la refinería de PEMEX, si la tiene, con el crudo que procesa y el valor que ganó o perdió en los libros de PEMEX.') % nom,
             'tarjetas': [], 'bloque': _ambiental_portal(base, ref, e)},
            {'id': 'leyes', 'titulo': 'Sus leyes del dinero',
             'texto': 'Con qué leyes cobra, compra, se endeuda y rinde cuentas %s, quién las aprueba y dónde se publican.' % nom,
             'tarjetas': [], 'bloque': leyes},
        {'id': 'dimensiones', 'titulo': 'En la Enciclopedia y en el Auditor',
         'texto': 'Lo demás de %s que ya vive en la Enciclopedia y en el Auditor, con el estado elegido:' % nom,
         'tarjetas': [], 'bloque': '<div class="pl-puertas">%s%s</div>' % (puertas_aud, ''.join(puertas))},
    ]
    # Cada dimensión, vinculada a su Contexto dimensional, al estado de
    # resultados del Gobierno y al estado de cuenta del estado (04-11-2026).
    for sec in temas:
        i = 'financiera' if sec['id'] == 'presupuestos' else sec['id']
        if any(d[0] == i for d in DIMENSIONES):
            sec['bloque'] += _ctx_portal(i, a, nom)
    # El contador va dentro de los presupuestos.
    rit = next(x for x in temas if x['id'] == 'ritmo')
    temas.remove(rit)
    temas[0]['bloque'] += '<h3 class="pl-sub-tit">Su contador</h3>' + rit['bloque']
    if [x['id'] for x in temas] != [t[0] for t in TEMAS]:
        raise SystemExit('planisferio: los temas del portal no son los de TEMAS')
    with open(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'planisferio.js'), encoding='utf-8') as f:
        if "var TEMAS = %s;" % json.dumps([t[0] for t in TEMAS]).replace('"', "'") not in f.read():
            raise SystemExit('planisferio: TEMAS de planisferio.js no es el de planisferio.py')
    info = {t[0]: t for t in TEMAS}
    tarjetas = [(info[x['id']][1], info[x['id']][2], info[x['id']][3], subpagina(a, x['id']), None, None) for x in temas]
    comun = {'menu': nom, 'menu_archivo': ARCHIVO, 'estilos': ['numeros.css', 'planisferio.css'], 'scripts': ['planisferio.js'],
             'antes': '      <p class="pl-ent-datos">%s</p>' % datos_e}
    out = [dict(comun, **{
        'archivo': portal(a), 'padre': (ARCHIVO, 'Planisferio'),
        'icono': '📍', 'titulo': nom, 'lema': 'Su portal en el Planisferio',
        'entrada': ('El mapa de los municipios de %s y sus cuentas, uno por uno. Lo demás va en sus tarjetas, cada una con su página: sus tres presupuestos, su deuda, '
                    'su inversión, su congreso, su Poder Judicial, su salud pública, su pobreza, su administración pública, sus recursos naturales y sus leyes del dinero. '
                    'Cada cifra sale de la base de la Enciclopedia, con su fuente oficial y su etiqueta.' % nom),
        'secciones': ([
            {'id': 'mapa-municipios',
             'titulo': ('El mapa de sus %d municipios' if m['conCifra'] else 'El mapa de sus %d alcaldías') % len(g['m']),
             'texto': ('Cada municipio en su lugar, con lo que ingresó e invirtió en %d. Elige qué ver; el color compara a los municipios del estado por quintiles '
                       '(cinco grupos con el mismo número de municipios). Toca uno para ver su ficha.' % padron['anio'] if m['conCifra'] else
                       'Cada alcaldía en su lugar. No llevan color por cifra porque no rinden cuenta municipal al INEGI; '
                       'toca una para ir a su ficha en el Auditor de entes.'),
             'tarjetas': [], 'bloque': mapa_mun}] if g else []) + [
            {'id': 'municipios', 'titulo': 'Sus municipios, uno por uno',
             'texto': ('El que no rindió cuenta sigue en la lista, sin cifra: borrarlo falsearía el padrón y ponerle cero falsearía la cifra. ' +
                       ('' if g else 'El mapa de sus municipios, con el Marco Geoestadístico del INEGI, llega en una próxima entrega del Planisferio, entidad por entidad.')),
             'tarjetas': [], 'bloque': tabla},
            {'id': 'temas', 'titulo': 'Todo lo demás de %s, en sus tarjetas' % nom,
             'texto': 'Cada tarjeta abre su página, con sus cifras, sus fuentes y lo que no dicen.',
             'tarjetas': tarjetas},
            {'id': 'otras-entidades', 'titulo': 'Otras entidades', 'sin_cab': True, 'texto': '', 'tarjetas': [], 'bloque': saltos},
        ]})]
    for x in temas:
        t = info[x['id']]
        sx = ('<nav class="pl-saltos" aria-label="El mismo tema en otras entidades"><a href="%s">← %s</a><a href="%s">📍 Volver al portal de %s</a><a href="%s">%s →</a></nav>' % (
            subpagina(prev['abbr'], x['id']), prev['name'], portal(a), nom, subpagina(sig['abbr'], x['id']), sig['name']))
        x = dict(x, bloque=x['bloque'] + sx)
        out.append(dict(comun, **{
            'archivo': subpagina(a, x['id']), 'padre': (ARCHIVO, 'Planisferio'), 'padre2': (portal(a), nom),
            'menu': t[2],
            'icono': t[1], 'titulo': '%s: %s' % (nom, t[2][0].lower() + t[2][1:]) if x['id'] != 'dimensiones' else '%s en la Enciclopedia y en el Auditor' % nom,
            'lema': 'Su portal en el Planisferio', 'entrada': x['texto'],
            'secciones': [dict(x, texto=''),
                          {'id': 'otros-temas', 'titulo': 'Los demás temas de %s' % nom, 'texto': '',
                           'tarjetas': [y for y in tarjetas if y[3] != subpagina(a, x['id'])]}],
        }))
    return out


def paginas(base, ref, tres, cuenta, cuanto='', origenes=''):
    padron = _padron()
    iv = inv_mun(padron)
    dv = deu_mun(padron)
    E = sorted(base['estados'], key=lambda x: clave(x['name']))
    out = [pagina_mapa(base, ref, tres, padron, cuenta, cuanto, origenes)]
    for k, e in enumerate(E):
        out.extend(pagina_portal(base, ref, e, padron, E[k - 1], E[(k + 1) % len(E)], iv, dv))
    return out
