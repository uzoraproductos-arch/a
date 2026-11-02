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
dimensiones. Las dimensiones que aún no se pintan en el Planisferio (deuda,
inversión, ambiental, legislativa, judicial) llevan a donde la Enciclopedia
ya las tiene: un enlace roto detiene la generación.

Lo usa apartados.generar(); lo interactivo vive en planisferio.js.
"""
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
# estado: %s recibe la clave de la entidad). La primera es la que se pinta.
DIMENSIONES = [
    ('financiera', '💰', 'Financiera',
     'Los tres presupuestos de cada entidad: lo que baja de la Federación, lo que cobra el estado y lo que ingresan sus municipios.',
     None, None),
    ('deuda', '🏦', 'Deuda',
     'Lo que debe cada gobierno estatal según el Sistema de Alertas de Hacienda, con su semáforo.',
     'numeros-mapa-del-gasto-federalizado.html?l=deuda', 'numeros-mapa-del-gasto-federalizado.html?l=deuda&e=%s'),
    ('inversion', '🏗️', 'Inversión',
     'Las obras que tocan a cada estado y lo que la ASF dejó por aclarar del dinero federal que recibió.',
     'numeros-mapa-del-gasto-federalizado.html?l=obras', 'numeros-mapa-del-gasto-federalizado.html?l=obras&e=%s'),
    ('ambiental', '🌎', 'Ambiental',
     'Las megaobras y crisis con alerta ambiental, separando el gasto público de la inversión privada.',
     'datos-ambiente-megaobras.html#abMapaObras', 'datos-ambiente-megaobras.html?e=%s#abMapaObras'),
    ('legislativa', '🏛️', 'Legislativa',
     'El Congreso de la Unión y los 32 congresos locales: quién los integra, cuánto cuestan y cómo se eligen.',
     'datos-poder-legislativo.html', 'radar-estado-de-cuenta.html?doc=%s'),
    ('judicial', '⚖️', 'Judicial',
     'El Poder Judicial: su presupuesto, la elección judicial y lo que resuelve con su dinero.',
     'datos-poder-judicial.html', None),
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


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def _padron():
    """El padrón municipal tal cual (municipios-efipem.js), leído con node
    para no reinterpretar a mano un objeto de JavaScript."""
    js = ('global.window={};require(%s);process.stdout.write(JSON.stringify(window.AUDIT_MUNICIPIOS));'
          % json.dumps(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'municipios-efipem.js')))
    return json.loads(subprocess.run(['node', '-e', js], check=True, capture_output=True, text=True).stdout)


def _existe(enlace):
    return os.path.exists(os.path.join(RAIZ, enlace.split('#')[0].split('?')[0]))


def _ritmo(anual_mdp):
    """Pesos por segundo de una cifra anual en millones: derivado."""
    return anual_mdp * 1e6 / SEG_ANIO


def _pesos(v):
    return '$' + format(round(v), ',')


def _contador(id_, ico, nom, v, est, que, fuente):
    s = _ritmo(v)
    return ('<article class="pl-cont" data-anual="%.1f">'
            '<p class="pl-cont-n"><span aria-hidden="true">%s</span> %s</p>'
            '<p class="pl-cont-v"><b class="num-tabular">%s</b> %s</p>'
            '<p class="pl-cont-s">A su ritmo anual, <b class="num-tabular">%s por segundo</b> %s</p>'
            '<p class="pl-cont-vivo" aria-live="off">Desde que abriste esta página: <b class="num-tabular pl-vivo">$0</b></p>'
            '<p class="pl-cont-que">%s</p><p class="pl-cont-f">%s</p></article>' % (
                v, ico, nom, mdp(v), chip(est), _pesos(s), chip('derivado'), que, fuente))


def _datos(base, padron):
    E = base['estados']
    C = base['fiscalEntidades']['campos']
    sin = set(C['recaudacionPropia'].get('sinFuente', []))
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
            'mn': m['n'], 'mc': con,
        })
    return filas


LENTES = [
    {'id': 'fed', 'nom': '1 · Lo que baja de la Federación', 'pal': 'oro', 'est': 'derivado', 'anio': 2026,
     'que': 'Participaciones (Ramo 28) más aportaciones (Ramo 33) que la Federación le entrega a cada entidad en 2026. Es el primer piso: el dinero federal que llega al territorio.'},
    {'id': 'est', 'nom': '2 · Lo que cobra el estado', 'pal': 'azul', 'est': 'derivado', 'anio': 2024,
     'que': 'Lo que el gobierno del estado recaudó por su cuenta en 2024: impuestos estatales, cuotas, derechos, productos y aprovechamientos. Es el segundo piso.'},
    {'id': 'mun', 'nom': '3 · Lo que ingresan sus municipios', 'pal': 'verde', 'est': 'derivado', 'anio': 2024,
     'que': 'Todo lo que ingresaron en 2024 los municipios del estado que rindieron su cuenta al INEGI: lo propio, lo que les llega del estado y de la Federación, y lo que pidieron prestado. Es el tercer piso.'},
]


def _fuentes(ref):
    return {
        'fed': 'Ramo 28: Anexo 15 del acuerdo de distribución (DOF 12-12-2025) %s. Ramo 33: Anexo 16, versión modificada (DOF 09-07-2026) %s. La suma de los dos es nuestra.' % (
            ref('ref-dof-distribucion-2026'), ref('ref-dof-distribucion-2026-mod')),
        'est': 'Suma de impuestos, cuotas de seguridad social, contribuciones de mejoras, derechos, productos y aprovechamientos de 2024. INEGI, finanzas públicas estatales, cifras definitivas %s.' % ref('ref-inegi-efipem-estatal'),
        'mun': 'Suma de los ingresos de 2024 de cada municipio que rindió su cuenta. INEGI, finanzas públicas municipales (EFIPEM), cifras definitivas %s. Los que no rindieron cuenta no se cuentan en cero: quedan sin cifra.' % ref('ref-inegi-efipem'),
    }


def pagina_mapa(base, ref, tres, padron):
    filas = _datos(base, padron)
    F = base['panoramaErario']['federalizado']
    s = {x['id']: x for x in tres['sale']}
    nac = padron['nacional']
    contadores = ''.join([
        _contador('estado', '🏛️', 'Presupuesto del Estado', s['estado']['v'], s['estado']['est'], s['estado']['que'],
                  'Criterios 2027, clasificación funcional %s. %s' % (ref('ref-cgpe2027'), s['estado']['op'])),
        _contador('nacional', '🏗️', 'Presupuesto nacional', s['nacional']['v'], s['nacional']['est'], s['nacional']['que'],
                  'Criterios 2027, clasificación funcional %s.' % ref('ref-cgpe2027')),
        _contador('social', '🫂', 'Presupuesto social', s['social']['v'], s['social']['est'], s['social']['que'],
                  'Criterios 2027, clasificación funcional %s.' % ref('ref-cgpe2027')),
        _contador('fed', '📍', 'Gasto federalizado', F['totalMdp'], 'oficial',
                  'Lo que la Federación transfiere a estados y municipios en 2026, por los cuatro ramos.',
                  'Presupuesto de Egresos de la Federación 2026 %s.' % ref('ref-pef2026')),
        _contador('mun', '🏘️', 'Lo que ingresaron los municipios', round(nac['ing'] / 1e6, 1), 'derivado',
                  'La suma de los ingresos de 2024 de los %s municipios que rindieron su cuenta, de %s en el catálogo.' % (
                      format(padron['conCifra'], ','), format(padron['catalogo'], ',')),
                  'INEGI, finanzas públicas municipales 2024 %s.' % ref('ref-inegi-efipem')),
    ])
    dims = []
    for i, ico, nom, que, ir, _ in DIMENSIONES:
        if ir and not _existe(ir):
            raise SystemExit('planisferio: la dimensión %s apunta a %s, que no existe' % (i, ir))
        dims.append('<button type="button" class="pl-dim%s" role="tab" aria-selected="%s" data-dim="%s"%s>'
                    '<span class="pl-dim-ico" aria-hidden="true">%s</span><span class="pl-dim-n">%s</span>'
                    '<small>%s</small></button>' % (
                        '' if ir is None else ' pl-dim-prox', 'true' if ir is None else 'false', i,
                        (' data-ir="%s"' % ir) if ir else '', ico, nom, 'En el mapa' if ir is None else 'Próximamente'))
    otras = ''.join('<li><span aria-hidden="true">%s</span> <b>%s.</b> %s <a href="%s">Ya está en la Enciclopedia ➔</a></li>' % (
        ico, nom, que, ir) for _, ico, nom, que, ir, _ in DIMENSIONES if ir)
    lentes = ''.join('<button type="button" class="pl-lente" role="radio" aria-checked="%s" data-l="%s">%s</button>' % (
        'true' if k == 0 else 'false', l['id'], l['nom']) for k, l in enumerate(LENTES))
    fu = _fuentes(ref)
    sin_est = [f['a'] for f in filas if f['est'] is None]
    sin_mun = [f['a'] for f in filas if f['mun'] is None]
    datos = {'lentes': [dict(l, fuente=fu[l['id']]) for l in LENTES], 'e': filas,
             'falta': {'est': sin_est, 'mun': sin_mun},
             'pend': {'est': 'entidades-' + '-'.join(sin_est).lower(), 'mun': 'municipios-sin-cuenta'},
             'dims': {i: {'n': nom, 'ir': ir, 'ire': ire} for i, _, nom, _, ir, ire in DIMENSIONES}}
    svg = tm.mapa_svg(RAIZ).replace('tt-svg', 'pl-svg').replace('tt-edo', 'pl-edo').replace(
        'aria-label="Mapa de las 32 entidades"', 'aria-label="Planisferio: las 32 entidades de México"')
    indice = ''.join('<li><a href="%s">%s</a></li>' % (f['p'], f['n']) for f in sorted(filas, key=lambda x: clave(x['n'])))
    bloque_mapa = '''<div class="pl-dims" role="tablist" aria-label="Dimensiones del Planisferio">%s</div>
          <p class="pl-dim-aviso" id="plDimAviso" hidden></p>
          <div class="pl-lentes" role="radiogroup" aria-label="Cuál de los tres presupuestos ver">%s</div>
          <p class="pl-que" id="plQue"></p>
          <div class="pl-rej">
            <figure class="pl-fig">
              %s
              <figcaption class="pl-leyenda" id="plLeyenda"></figcaption>
            </figure>
            <aside class="pl-ficha" id="plFicha" aria-live="polite">
              <p class="pl-ficha-vacia"><b>Toca una entidad.</b> Verás sus tres presupuestos y la puerta a su portal, con sus municipios.</p>
            </aside>
          </div>
          <p class="pl-pie" id="plFuente"></p>
          <p class="pl-pie" id="plFalta"></p>
          <nav class="pl-indice" aria-label="Las 32 entidades, una por una"><h3>Las 32 entidades, en orden alfabético</h3><ul>%s</ul></nav>
          <script type="application/json" id="plDatos">%s</script>
          <noscript><p>El mapa se colorea con JavaScript; sin él, cada entidad se abre desde la lista de arriba.</p></noscript>''' % (
        ''.join(dims), lentes, svg, indice, _json(datos))
    return {
        'archivo': ARCHIVO, 'menu': 'Planisferio', 'menu_archivo': ARCHIVO,
        'icono': '🗺️', 'titulo': 'Planisferio', 'lema': 'México en un mapa: cada entidad, cada municipio, cada peso',
        'entrada': ('El dinero público tiene domicilio. Aquí está México entero en un mapa: elige una dimensión, mira cómo se reparte '
                    'y toca una entidad para entrar a su portal, con sus municipios uno por uno. Todo sale de la base de la '
                    'Enciclopedia, con su fuente oficial y su etiqueta; el Planisferio solo lo pone en el territorio.'),
        'estilos': ['numeros.css', 'planisferio.css'],
        'scripts': ['planisferio.js'],
        'secciones': [
            {'id': 'mapa', 'titulo': 'El mapa: los tres presupuestos de cada entidad',
             'texto': ('Cada entidad vive en tres pisos de la hacienda: lo que le baja de la Federación, lo que cobra por su cuenta y lo que ingresan sus municipios. '
                       'Elige el piso; el color compara a las 32 por quintiles (cinco grupos con el mismo número de entidades).'),
             'tarjetas': [], 'bloque': bloque_mapa},
            {'id': 'contadores', 'titulo': 'Los contadores del año',
             'texto': ('Los tres presupuestos de la Federación en 2026 (del Estado, nacional y social), lo que baja al territorio y lo que ingresan los municipios. '
                       'El ritmo por segundo es la cifra anual entre los 31,536,000 segundos del año: sirve para dimensionarla, no es dinero que se mueva en tiempo real '
                       'ni dice cuándo se gasta de verdad cada peso.'),
             'tarjetas': [], 'bloque': '<div class="pl-conts">%s</div>' % contadores},
            {'id': 'dimensiones', 'titulo': 'Las dimensiones que vienen',
             'texto': ('El Planisferio crece por entregas, una dimensión a la vez y, después, municipio por municipio. Mientras llegan al mapa, cada una ya tiene su lugar en la Enciclopedia:'),
             'tarjetas': [], 'bloque': '<ul class="pl-otras">%s</ul>' % otras},
        ],
    }


def pagina_portal(base, ref, e, padron, prev, sig):
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
    # 2 · El ritmo
    s = _ritmo(e['gasto'])
    ritmo = ('<div class="pl-conts pl-conts-1"><article class="pl-cont" data-anual="%.1f">'
             '<p class="pl-cont-n"><span aria-hidden="true">⏱️</span> Lo que le baja de la Federación, a su ritmo</p>'
             '<p class="pl-cont-v"><b class="num-tabular">%s por segundo</b> %s</p>'
             '<p class="pl-cont-vivo" aria-live="off">Desde que abriste esta página: <b class="num-tabular pl-vivo">$0</b></p>'
             '<p class="pl-cont-que">Operación: %s ÷ 31,536,000 segundos del año. Sirve para dimensionar la cifra: no es dinero que se mueva en tiempo real, '
             'ni dice cuándo llega cada pago (las participaciones se entregan cada mes y las aportaciones según su calendario).</p></article></div>' % (
                 e['gasto'], _pesos(s), chip('derivado'), mdp(e['gasto'])))
    # 3 · Los municipios
    filas = []
    for r in m['lista']:
        if len(r) < 3:
            filas.append('<tr data-n="%s"><th scope="row">%s</th><td colspan="5" class="pl-sin">Sin cuenta de 2024 %s</td></tr>' % (
                json.dumps(r[1].lower(), ensure_ascii=False)[1:-1], r[1], chip('pendiente', 'municipios-sin-cuenta')))
            continue
        cve, n, ing, part, aport, fortamun, fismdf, predial, propios, egr = r[:10]
        dep = (part + aport) / ing * 100 if ing else None
        filas.append('<tr data-n="%s" data-ing="%d" data-predial="%d" data-dep="%s"><th scope="row">%s</th>'
                     '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                         json.dumps(n.lower(), ensure_ascii=False)[1:-1], ing, predial, '%.2f' % dep if dep is not None else '',
                         n, mdp(ing / 1e6), mdp(part / 1e6), mdp(aport / 1e6), mdp(predial / 1e6), pct(dep) if dep is not None else '—'))
    tabla = ('<div class="pl-mun-mandos"><label class="pl-sel"><span>Buscar municipio</span><input type="search" id="plMunBusca" placeholder="Escribe un nombre" autocomplete="off"></label>'
             '<label class="pl-sel"><span>Ordenar por</span><select id="plMunOrden"><option value="n">Nombre (A–Z)</option><option value="ing">Ingreso total</option>'
             '<option value="predial">Predial cobrado</option><option value="dep">Dependencia de transferencias</option></select></label></div>'
             '<div class="pl-tabla-caja"><table class="pl-tabla" id="plMun"><caption>Los %d municipios de %s en el catálogo del INEGI, con sus cuentas de %d</caption>'
             '<thead><tr><th scope="col">Municipio</th><th scope="col">Ingreso total</th><th scope="col">Participaciones</th><th scope="col">Aportaciones</th>'
             '<th scope="col">Predial</th><th scope="col">Dependencia</th></tr></thead><tbody>%s</tbody></table></div>'
             '<p class="pl-pie">Cifras de cada municipio: INEGI, finanzas públicas municipales %d %s, en millones de pesos (mdp) %s. '
             'La dependencia es (participaciones + aportaciones) ÷ ingreso total × 100 %s: cuánto de lo que ingresó llegó de fuera.</p>' % (
                 m['n'], nom, padron['anio'], ''.join(filas), padron['anio'], ref('ref-inegi-efipem'), chip('oficial'), chip('derivado')))
    # 4 · Las otras dimensiones y el Auditor
    dl = _congresos(base)
    puertas = []
    for i, ico, dn, que, ir, ire in DIMENSIONES:
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
    datos_e = '%s · capital: %s · %s habitantes a mitad de 2026 (CONAPO) %s' % (
        nom, e['capital'], format(e['pobPersonas'], ','), chip('derivado'))
    return {
        'archivo': portal(a), 'menu': nom, 'menu_archivo': ARCHIVO,
        'padre': (ARCHIVO, 'Planisferio'),
        'icono': '📍', 'titulo': nom, 'lema': 'Su portal en el Planisferio',
        'entrada': ('Los tres presupuestos de %s, sus municipios uno por uno y la puerta a sus otras dimensiones. '
                    'Cada cifra sale de la base de la Enciclopedia, con su fuente oficial y su etiqueta.' % nom),
        'estilos': ['numeros.css', 'planisferio.css'],
        'scripts': ['planisferio.js'],
        'antes': '      <p class="pl-ent-datos">%s</p>' % datos_e,
        'secciones': [
            {'id': 'presupuestos', 'titulo': 'Sus tres presupuestos',
             'texto': 'Un piso por cada orden de gobierno. Los años no se mezclan: lo que baja es de 2026 y lo que cobran el estado y sus municipios, de 2024, el último con cifras definitivas del INEGI.',
             'tarjetas': [], 'bloque': '<div class="pl-pisos">%s%s%s</div>' % (p1, p2, p3)},
            {'id': 'ritmo', 'titulo': 'Su contador', 'texto': '', 'tarjetas': [], 'bloque': ritmo},
            {'id': 'municipios', 'titulo': 'Sus municipios, uno por uno',
             'texto': ('El que no rindió cuenta sigue en la lista, sin cifra: borrarlo falsearía el padrón y ponerle cero falsearía la cifra. '
                       'El mapa de sus municipios, con el Marco Geoestadístico del INEGI, llega en una próxima entrega del Planisferio.'),
             'tarjetas': [], 'bloque': tabla},
            {'id': 'dimensiones', 'titulo': 'Sus otras dimensiones',
             'texto': 'Mientras llegan al Planisferio, ya están en la Enciclopedia y en el Auditor, con %s elegido:' % nom,
             'tarjetas': [], 'bloque': '<div class="pl-puertas">%s%s</div>%s' % (puertas_aud, ''.join(puertas), saltos)},
        ],
    }


def paginas(base, ref, tres):
    padron = _padron()
    E = sorted(base['estados'], key=lambda x: clave(x['name']))
    out = [pagina_mapa(base, ref, tres, padron)]
    for k, e in enumerate(E):
        out.append(pagina_portal(base, ref, e, padron, E[k - 1], E[(k + 1) % len(E)]))
    return out
