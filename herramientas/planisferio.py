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
     'Las obras que tocan a cada estado y lo que la ASF dejó por aclarar del dinero federal que recibió.',
     'numeros-mapa-del-gasto-federalizado.html?l=obras', 'numeros-mapa-del-gasto-federalizado.html?l=obras&e=%s', False),
    ('ambiental', '🌎', 'Ambiental',
     'Las megaobras y crisis con alerta ambiental, separando el gasto público de la inversión privada.',
     'datos-ambiente-megaobras.html#abMapaObras', 'datos-ambiente-megaobras.html?e=%s#abMapaObras', False),
    ('legislativa', '🏛️', 'Legislativa',
     'El Congreso de la Unión y los 32 congresos locales: quién los integra, cuánto cuestan y cómo se eligen.',
     'datos-poder-legislativo.html', 'radar-estado-de-cuenta.html?doc=%s', False),
    ('judicial', '⚖️', 'Judicial',
     'El Poder Judicial: su presupuesto, la elección judicial y lo que resuelve con su dinero.',
     'datos-poder-judicial.html', None, False),
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
]

MAPA_MUN = """<div class="pl-lentes" role="radiogroup" aria-label="Qué ver en el mapa de los municipios">%s</div>
          <p class="pl-que" id="plMunQue"></p>
          <div class="pl-rej" id="plMunMapa">
            <figure class="pl-fig">
              %s
              <figcaption class="pl-leyenda" id="plMunLeyenda"></figcaption>
            </figure>
            <aside class="pl-ficha" id="plMunFicha" aria-live="polite">
              <p class="pl-ficha-vacia"><b>Toca un municipio.</b> Verás lo que ingresó en %d, de dónde le llegó y la puerta a su ficha en el Auditor de entes.</p>
            </aside>
          </div>
          <p class="pl-pie">Límites: %s (<a href="%s">descarga del INEGI</a>), integrados el %s; huella SHA-256 del archivo de origen <code>%s</code>. Simplificados para verse en pantalla. %s
          Cifras: INEGI, finanzas públicas municipales %d %s. %s</p>
          <script type="application/json" id="plMunDatos">%s</script>"""


def _mapa_mun(e, m, g, ref, padron):
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
            'lentes': [{'id': i, 'nom': n, 'pal': p, 'que': q} for i, n, p, q in LENTES_MUN], 'm': datos}
    return MAPA_MUN % (
        '' if sin else lentes, svg, padron['anio'], g['fuente'], g['url'], g['integrado'], g['sha256'][:12] + '…', g['aviso'],
        padron['anio'], ref('ref-inegi-efipem'),
        ('En gris, todas, porque no rinden cuenta municipal %s.' % chip('pendiente', 'municipios-sin-cuenta') if sin else
         'En gris, los municipios que no rindieron su cuenta de %d %s.' % (padron['anio'], chip('pendiente', 'municipios-sin-cuenta'))),
        _json(info))


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
            'mn': m['n'], 'mc': con, 'mm': geo_mun(m['cve']) is not None,
            # La deuda (Sistema de Alertas, Cuenta Pública 2025). La entidad
            # que no se mide (hoy Tlaxcala) no trae indicadores: queda en gris.
            'deuda': e['deuda'], 'dpc': round(e['deuda'] * 1e6 / e['pobPersonas']),
            'ild': e['deudaIld'] if _medida(e) else None, 'sd': e.get('deudaSd'), 'ocp': e.get('deudaOcp'),
            'ildm': e.get('ildMdp'), 'sem': SEMAFORO[e['semaforoDeuda']] if _medida(e) else 'No se mide',
        })
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
]


def _fuentes(ref, base=None):
    extra = {}
    if base is not None:
        E = base['estados']
        doc, pagina = _sda(base)
        sda = '%s %s (<a href="%s">archivo de variables por entidad, XLSX</a>; huella SHA-256 <code>%s…</code>; <a href="%s">página oficial</a>).' % (
            sorted(set(e['deudaFuente'] for e in E), key=len)[0], ref('ref-shcp-alertas'), doc['url'], doc['sha256'][:12], pagina)
        ind = (' Las tres mediciones y su resultado (sostenible, en observación o elevado) las define el Reglamento del Sistema de Alertas; '
               'el archivo las publica por entidad.')
        extra = {'deuda': sda, 'ild': sda + ind, 'sd': sda + ind, 'ocp': sda + ind,
                 'dpc': ('Deuda al cierre de 2025 (Sistema de Alertas %s) ÷ población a mitad de 2026 (CONAPO). La división es nuestra; '
                         'los años no coinciden porque es la deuda que hereda quien vive hoy en el estado.') % ref('ref-shcp-alertas')}
    return dict(extra, **{
        'fed': 'Ramo 28: Anexo 15 del acuerdo de distribución (DOF 12-12-2025) %s. Ramo 33: Anexo 16, versión modificada (DOF 09-07-2026) %s. La suma de los dos es nuestra.' % (
            ref('ref-dof-distribucion-2026'), ref('ref-dof-distribucion-2026-mod')),
        'est': 'Suma de impuestos, cuotas de seguridad social, contribuciones de mejoras, derechos, productos y aprovechamientos de 2024. INEGI, finanzas públicas estatales, cifras definitivas %s.' % ref('ref-inegi-efipem-estatal'),
        'mun': 'Suma de los ingresos de 2024 de cada municipio que rindió su cuenta. INEGI, finanzas públicas municipales (EFIPEM), cifras definitivas %s. Los que no rindieron cuenta no se cuentan en cero: quedan sin cifra.' % ref('ref-inegi-efipem'),
    })


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
    for k, (i, ico, nom, que, ir, _ire, pinta) in enumerate(DIMENSIONES):
        if ir and not _existe(ir):
            raise SystemExit('planisferio: la dimensión %s apunta a %s, que no existe' % (i, ir))
        if pinta and not any(l['dim'] == i for l in LENTES):
            raise SystemExit('planisferio: la dimensión %s se pinta pero no tiene lentes' % i)
        dims.append('<button type="button" class="pl-dim%s" role="tab" aria-selected="%s" data-dim="%s">'
                    '<span class="pl-dim-ico" aria-hidden="true">%s</span><span class="pl-dim-n">%s</span>'
                    '<small>%s</small></button>' % (
                        '' if pinta else ' pl-dim-prox', 'true' if k == 0 else 'false', i,
                        ico, nom, 'En el mapa' if pinta else 'Próximamente'))
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
    # El punto ciego del semáforo: si todas comparten color, el color no
    # distingue a la más endeudada de la menos. Se dice con las cifras.
    med = sorted((f for f in filas if f['ild'] is not None), key=lambda f: -f['ild'])
    sems = sorted(set(f['sem'] for f in filas))
    nota_deuda = ('<b>%s.</b> El semáforo de Hacienda pone a las %d en «%s»%s. Ese color junta a %s, que debe el equivalente a %s de sus ingresos de libre disposición, '
                  'con %s, que debe %s %s. Por eso el mapa no colorea por semáforo, sino por cifra: el verde quiere decir que, con esas tres mediciones, Hacienda considera sostenible su deuda, no que deban poco.' % (
                      'Lo que el semáforo no dice' if len(sems) == 1 else 'El semáforo no lo dice todo',
                      len(filas), sems[0].lower() if len(sems) == 1 else ' y '.join(x.lower() for x in sems),
                      ' (las que no se miden cuentan como sostenibles por ley)' if no_med else '',
                      med[0]['n'], pct(med[0]['ild']), med[-1]['n'], pct(med[-1]['ild']), chip('oficial')))
    datos = {'lentes': [dict(l, fuente=fu[l['id']], falta=falta.get(l['id'])) for l in LENTES], 'e': filas,
             'dims': {i: {'n': nom, 'ir': ir, 'ire': ire, 'pinta': pinta} for i, _, nom, _, ir, ire, pinta in DIMENSIONES},
             'notas': {'deuda': nota_deuda}}
    svg = tm.mapa_svg(RAIZ).replace('tt-svg', 'pl-svg').replace('tt-edo', 'pl-edo').replace(
        'aria-label="Mapa de las 32 entidades"', 'aria-label="Planisferio: las 32 entidades de México"')
    indice = ''.join('<li><a href="%s">%s</a></li>' % (f['p'], f['n']) for f in sorted(filas, key=lambda x: clave(x['n'])))
    bloque_mapa = '''<div class="pl-dims" role="tablist" aria-label="Dimensiones del Planisferio">%s</div>
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
          <p class="pl-dim-nota" id="plDimNota" hidden></p>
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
                    'y toca una entidad para entrar a su portal, con el mapa de sus municipios y cada uno con sus cuentas. Todo sale de la base de la '
                    'Enciclopedia, con su fuente oficial y su etiqueta; el Planisferio solo lo pone en el territorio.'),
        'estilos': ['numeros.css', 'planisferio.css'],
        'scripts': ['planisferio.js'],
        'secciones': [
            {'id': 'mapa', 'titulo': 'El mapa: elige una dimensión',
             'texto': ('Hoy se pintan %s. La financiera son los tres pisos de la hacienda de cada entidad: lo que le baja de la Federación, lo que cobra por su cuenta y lo que ingresan sus municipios. '
                       'La deuda es lo que debe cada gobierno estatal y cuánto le pesa, con los tres indicadores del Sistema de Alertas de Hacienda. '
                       'Elige la dimensión y qué ver; el color compara a las 32 por quintiles (cinco grupos con el mismo número de entidades).') % (
                           ('%d dimensiones: la %s' % (len(pintadas), ' y la '.join(d[2].lower() for d in pintadas))) if len(pintadas) > 1 else 'una dimensión'),
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


def _lugar(E, a, k, med=False):
    """Su lugar entre las entidades, de la que más a la que menos (derivado)."""
    v = [x for x in E if x.get(k) is not None and (not med or _medida(x))]
    v.sort(key=lambda x: -x[k])
    return next(i for i, x in enumerate(v) if x['abbr'] == a) + 1, len(v)


def _deuda_portal(base, ref, e):
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
              '<li>La deuda de sus municipios también la mide el Sistema de Alertas; aún no la integramos %s.</li>'
              '<li>Su propia ley de deuda pública se publica en el %s. <a href="%s#fed-deuda">⚖️ Las leyes de la deuda en los tres niveles</a></li></ul></div>') % (
        ln._a(ln.CPEUM, 'Constitución'), r_techo, ln._a(ln.pdf('LDFEFM.pdf'), 'LDF'),
        '<span class="est-chip est-pendiente" data-pend="deuda-municipios">pendiente</span>', html.escape(ln.ESTADOS[a][0]), ln.ARCHIVO)
    return '<div class="pl-pisos">%s%s</div>%s%s' % (p1, p2, ciego, reglas)


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
    # 2 bis · Su deuda (Sistema de Alertas, Cuenta Pública 2025)
    deuda = _deuda_portal(base, ref, e)
    # 3 · Los municipios
    filas = []
    for r in m['lista']:
        if len(r) < 3:
            filas.append('<tr data-c="%s" data-n="%s"><th scope="row">%s</th><td colspan="5" class="pl-sin">Sin cuenta de 2024 %s</td></tr>' % (
                r[0], json.dumps(r[1].lower(), ensure_ascii=False)[1:-1], r[1], chip('pendiente', 'municipios-sin-cuenta')))
            continue
        cve, n, ing, part, aport, fortamun, fismdf, predial, propios, egr = r[:10]
        dep = (part + aport) / ing * 100 if ing else None
        filas.append('<tr data-c="%s" data-n="%s" data-ing="%d" data-predial="%d" data-dep="%s"><th scope="row">%s</th>'
                     '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                         cve, json.dumps(n.lower(), ensure_ascii=False)[1:-1], ing, predial, '%.2f' % dep if dep is not None else '',
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
    g = geo_mun(m['cve'])
    mapa_mun = _mapa_mun(e, m, g, ref, padron) if g else ''
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
    return {
        'archivo': portal(a), 'menu': nom, 'menu_archivo': ARCHIVO,
        'padre': (ARCHIVO, 'Planisferio'),
        'icono': '📍', 'titulo': nom, 'lema': 'Su portal en el Planisferio',
        'entrada': ('Los tres presupuestos de %s, su deuda, sus leyes del dinero, sus municipios uno por uno y la puerta a sus otras dimensiones. '
                    'Cada cifra sale de la base de la Enciclopedia, con su fuente oficial y su etiqueta.' % nom),
        'estilos': ['numeros.css', 'planisferio.css'],
        'scripts': ['planisferio.js'],
        'antes': '      <p class="pl-ent-datos">%s</p>' % datos_e,
        'secciones': [
            {'id': 'presupuestos', 'titulo': 'Sus tres presupuestos',
             'texto': 'Un piso por cada orden de gobierno. Los años no se mezclan: lo que baja es de 2026 y lo que cobran el estado y sus municipios, de 2024, el último con cifras definitivas del INEGI.',
             'tarjetas': [], 'bloque': '<div class="pl-pisos">%s%s%s</div>' % (p1, p2, p3)},
            {'id': 'ritmo', 'titulo': 'Su contador', 'texto': '', 'tarjetas': [], 'bloque': ritmo},
            {'id': 'deuda', 'titulo': 'Su deuda',
             'texto': ('Lo que debe el gobierno de %s y cuánto le pesa, medido por el Sistema de Alertas de Hacienda con la Cuenta Pública 2025. '
                       'Es la deuda del gobierno del estado; la de sus municipios la mide el mismo sistema y llegará al Planisferio en una próxima entrega.') % nom,
             'tarjetas': [], 'bloque': deuda},
            {'id': 'leyes', 'titulo': 'Sus leyes del dinero',
             'texto': 'Con qué leyes cobra, compra, se endeuda y rinde cuentas %s, quién las aprueba y dónde se publican.' % nom,
             'tarjetas': [], 'bloque': leyes},
        ] + ([
            {'id': 'mapa-municipios',
             'titulo': ('El mapa de sus %d municipios' if m['conCifra'] else 'El mapa de sus %d alcaldías') % len(g['m']),
             'texto': ('Cada municipio en su lugar, con lo que ingresó en %d. Elige qué ver; el color compara a los municipios del estado por quintiles '
                       '(cinco grupos con el mismo número de municipios). Toca uno para ver su ficha.' % padron['anio'] if m['conCifra'] else
                       'Cada alcaldía en su lugar. No llevan color por cifra porque no rinden cuenta municipal al INEGI; '
                       'toca una para ir a su ficha en el Auditor de entes.'),
             'tarjetas': [], 'bloque': mapa_mun}] if g else []) + [
            {'id': 'municipios', 'titulo': 'Sus municipios, uno por uno',
             'texto': ('El que no rindió cuenta sigue en la lista, sin cifra: borrarlo falsearía el padrón y ponerle cero falsearía la cifra. ' +
                       ('' if g else 'El mapa de sus municipios, con el Marco Geoestadístico del INEGI, llega en una próxima entrega del Planisferio, entidad por entidad.')),
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
