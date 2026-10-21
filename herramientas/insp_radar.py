# -*- coding: utf-8 -*-
"""Modo Inspector: «Radar por entidad · Banderas rojas», en pagina propia
(pedido del autor, 12-10-2026). Desde el 21-10-2026 (pedido del autor) ya no
es una aplicacion aparte: vive dentro del Auditor de entes publicos, que la
abre desde su directorio, y la genera insp_entes.subpaginas().

Antes la pagina cargaba el auditor completo en un marco para mostrar seis
tarjetas (audit-engine.js, renderRadarBanderasNacional). Ahora se escribe
aqui con sus cifras puestas: los 32 estados ya ordenados, su mapa de calor
y la ficha de cada uno, desde window.AUDIT_DB:

- cuenta_publica_asf.cp2024.entidades: la Matriz de Datos Basicos de la ASF
  (CP 2024, corte febrero de 2026), pp. 19 a 23: por estado, auditorias,
  universo, muestra, acciones, PO, PRAS, recuperaciones y monto por
  aclarar, y su desglose Gobierno del Estado / Municipios (Alcaldias en la
  Ciudad de Mexico) / Otros.
- cuenta_publica_asf.acciones: que es un PO y una PRAS (LFRCF, art. 40).

Los tres criterios del motor se conservan (por cada $100 revisados, monto
total, peso de los municipios); los tres son orden, no juicio. El semaforo
es el mismo del motor: rojo si por cada $100 revisados queda al menos 1.5
veces el promedio nacional, ambar si queda mas que el promedio, verde si
menos. Diferencia con el motor: en la Ciudad de Mexico el «peso de los
municipios» usa sus Alcaldias (el motor buscaba solo «Municipios» y le
ponia 0 %).

insp-radar.js reordena, pinta el mapa por el criterio elegido y muestra la
ficha del estado que eliges; sin JavaScript la pagina se lee entera en el
orden por omision.
"""
import re
import unicodedata

from presupuesto_modulos import chip

ESTILOS = ['insp-radar.css']
SCRIPTS = ['insp-radar.js']

# Abreviatura y casilla (columna, renglon) del mapa en cuadricula: una
# silueta aproximada de Mexico en 7 columnas, para que cada casilla mida al
# menos 44 px en un celular.
CASILLAS = {
    'Baja California': ('BC', 0, 0), 'Sonora': ('SON', 1, 0), 'Chihuahua': ('CHIH', 2, 0),
    'Coahuila de Zaragoza': ('COAH', 3, 0), 'Nuevo León': ('NL', 4, 0),
    'Baja California Sur': ('BCS', 0, 1), 'Sinaloa': ('SIN', 1, 1), 'Durango': ('DGO', 2, 1),
    'Zacatecas': ('ZAC', 3, 1), 'San Luis Potosí': ('SLP', 4, 1), 'Tamaulipas': ('TAM', 5, 1),
    'Nayarit': ('NAY', 0, 2), 'Jalisco': ('JAL', 1, 2), 'Aguascalientes': ('AGS', 2, 2),
    'Guanajuato': ('GTO', 3, 2), 'Querétaro': ('QRO', 4, 2), 'Hidalgo': ('HGO', 5, 2),
    'Veracruz de Ignacio de la Llave': ('VER', 6, 2),
    'Colima': ('COL', 0, 3), 'Michoacán de Ocampo': ('MICH', 1, 3), 'México': ('MEX', 2, 3),
    'Ciudad de México': ('CDMX', 3, 3), 'Tlaxcala': ('TLAX', 4, 3), 'Puebla': ('PUE', 5, 3),
    'Yucatán': ('YUC', 6, 3),
    'Guerrero': ('GRO', 1, 4), 'Morelos': ('MOR', 2, 4), 'Oaxaca': ('OAX', 3, 4),
    'Tabasco': ('TAB', 4, 4), 'Campeche': ('CAM', 5, 4), 'Quintana Roo': ('QROO', 6, 4),
    'Chiapas': ('CHIS', 4, 5),
}

# Clave del mismo estado en el Auditor de entes publicos, donde difiere.
CLAVE_AUDITOR = {'MEX': 'MÉX'}
AUDITOR = 'herramienta-inspector-entes.html'

CORTO = {'México': 'Estado de México', 'Coahuila de Zaragoza': 'Coahuila',
         'Michoacán de Ocampo': 'Michoacán', 'Veracruz de Ignacio de la Llave': 'Veracruz'}

CRITERIOS = [
    ('intensidad', 'Por cada $100 revisados', '💯',
     'Qué tanto quedó por aclarar <b>en proporción</b> a lo que la Auditoría revisó. Sirve para comparar estados '
     'grandes con chicos.',
     'Monto por aclarar ÷ muestra auditada del estado × 100.'),
    ('monto', 'Monto por aclarar', '💰',
     'Cuánto dinero, en pesos, quedó sin documentación suficiente al cierre de las auditorías. Los estados que '
     'reciben más dinero federal tienden a salir arriba.',
     'Es la cifra de la Matriz, sin operación.'),
    ('municipios', 'Peso de los municipios', '🏘️',
     'Qué parte de lo que quedó por aclarar en el estado le toca a sus municipios (en la Ciudad de México, a sus '
     'alcaldías). Dice si el pendiente está en el gobierno estatal o en los ayuntamientos.',
     'Monto por aclarar de los municipios ÷ monto por aclarar del estado × 100.'),
]

COLOR_ENTE = {'gob': '#1d4f91', 'mun': '#c2571a', 'otr': '#7b8597'}


def _num(v, d=0):
    return format(v, ',.%df' % d)


def _mdp(pesos):
    return '$' + _num(pesos / 1e6, 1) + ' mdp'


def _slug(t):
    t = unicodedata.normalize('NFD', t).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


def _esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def _tipo_ente(ente):
    if ente.startswith('Gobierno'):
        return 'gob'
    if ente.startswith('Municipios') or ente.startswith('Alcald'):
        return 'mun'
    return 'otr'


def _semaforo(r, prom):
    if r >= prom * 1.5:
        return 'rojo', '🔴', 'Bandera roja', 'al menos 1.5 veces el promedio nacional'
    if r >= prom:
        return 'ambar', '🟡', 'Arriba del promedio', 'más que el promedio nacional, sin llegar a 1.5 veces'
    return 'verde', '🟢', 'Debajo del promedio', 'menos que el promedio nacional'


def _estados(C):
    L = C['cp2024']['entidades']
    pa = sum(e['total']['porAclarar'] for e in L)
    mu = sum(e['total']['muestra'] for e in L)
    prom = pa / mu * 100
    est = []
    for e in L:
        t = e['total']
        mun = sum(d['porAclarar'] for d in e['desglose'] if _tipo_ente(d['ente']) == 'mun')
        x = {
            'e': e, 'nom': CORTO.get(e['entidad'], e['entidad']), 'slug': _slug(CORTO.get(e['entidad'], e['entidad'])),
            'abr': CASILLAS[e['entidad']][0], 'col': CASILLAS[e['entidad']][1], 'fil': CASILLAS[e['entidad']][2],
            'v': {
                'intensidad': t['porAclarar'] / t['muestra'] * 100,
                'monto': t['porAclarar'],
                'municipios': (mun / t['porAclarar'] * 100) if t['porAclarar'] else 0.0,
            },
            'mun_ente': next((d['ente'] for d in e['desglose'] if _tipo_ente(d['ente']) == 'mun'), 'Municipios'),
        }
        x['f'] = {'intensidad': '$%.2f' % x['v']['intensidad'], 'monto': _mdp(x['v']['monto']),
                  'municipios': _num(x['v']['municipios'], 1) + ' %'}
        x['sem'] = _semaforo(x['v']['intensidad'], prom)
        est.append(x)
    # Lugar, ancho de barra y cuartil por criterio.
    for c, *_ in CRITERIOS:
        orden = sorted(est, key=lambda x: -x['v'][c])
        tope = orden[0]['v'][c] or 1
        for i, x in enumerate(orden):
            x.setdefault('lugar', {})[c] = i + 1
            x.setdefault('w', {})[c] = x['v'][c] / tope * 100
            x.setdefault('q', {})[c] = 4 - i // 8
    return est, pa, mu, prom


def _fuente(C, texto=None):
    f = C['fuentes']['MDB2024']
    pags = C['cp2024']['paginaEntidades']
    return '<a href="%s#page=%s" target="_blank" rel="noopener">%s, pp. %s ↗</a>' % (
        f['url'], pags.split(' ')[0], texto or f['corto'], pags)


def _attrs(x):
    out = ['data-ent="%s"' % x['slug']]
    for c, *_ in CRITERIOS:
        out.append('data-v-%s="%.6f" data-f-%s="%s" data-w-%s="%.2f" data-l-%s="%d" data-q-%s="%d"' % (
            c, x['v'][c], c, x['f'][c], c, x['w'][c], c, x['lugar'][c], c, x['q'][c]))
    return ' '.join(out)


def _hero(est, pa, mu, prom, C, ref):
    por_int = sorted(est, key=lambda x: -x['v']['intensidad'])
    por_monto = sorted(est, key=lambda x: -x['v']['monto'])
    a, m = por_int[0], por_monto[0]
    rojos = sum(1 for x in est if x['sem'][0] == 'rojo')
    aud = sum(x['e']['total']['auditorias'] for x in est)
    return '''<section class="ir-hero" aria-labelledby="irHeroTit">
        <p class="ir-kicker">La respuesta corta · Cuenta Pública 2024</p>
        <h2 class="ir-hero-tit" id="irHeroTit">De cada <b>$100</b> que la Auditoría Superior revisó del dinero federal de los estados, quedaron <b class="ir-hero-cifra">$%.2f</b> por aclarar %s</h2>
        <p class="ir-hero-op">Promedio nacional: la suma de lo que quedó por aclarar en los 32 estados (%s) ÷ la suma de lo que la Auditoría revisó en ellos (%s) × 100. %s</p>
        <div class="ir-hero-datos">
          <a class="ir-hd" href="#ir-e-%s" data-ir-ir="%s"><small>Más alto en proporción %s</small><b>%s</b><span>$%.2f de cada $100 revisados: %s veces el promedio</span></a>
          <a class="ir-hd" href="#ir-e-%s" data-ir-ir="%s"><small>Más dinero por aclarar %s</small><b>%s</b><span>%s en %s auditorías</span></a>
          <div class="ir-hd"><small>Los 32 estados juntos %s</small><b>%s</b><span>por aclarar, en %s auditorías; %d estados con bandera roja</span></div>
        </div>
      </section>''' % (
        prom, chip('derivado'), _mdp(pa), _mdp(mu), _fuente(C),
        a['slug'], a['slug'], chip('derivado'), a['nom'], a['v']['intensidad'], _num(a['v']['intensidad'] / prom, 1),
        m['slug'], m['slug'], chip('oficial'), m['nom'], _mdp(m['v']['monto']), _num(m['e']['total']['auditorias']),
        chip('derivado'), _mdp(pa), _num(aud), rojos)


def _aviso(C):
    return '''<aside class="ir-aviso" aria-labelledby="irAvisoTit">
        <h2 class="ir-aviso-tit" id="irAvisoTit"><span aria-hidden="true">⚖️</span> Antes de leer: «por aclarar» no es «robado»</h2>
        <p>%s</p>
        <p>Una bandera roja en esta página quiere decir que <b>ahí conviene preguntar primero</b>, no que alguien sea culpable. El estado y sus municipios pueden solventar con documentos; si no lo hacen, la Auditoría emite un pliego de observaciones y el caso sigue su camino legal.</p>
      </aside>''' % _esc(C['nota']).replace('Pesos corrientes. ', '')


def _criterios(prom):
    botones = ''.join(
        '<button type="button" class="ir-crit" data-crit="%s" aria-pressed="%s"><span aria-hidden="true">%s</span> %s</button>'
        % (c, 'true' if i == 0 else 'false', ico, etq) for i, (c, etq, ico, _, _) in enumerate(CRITERIOS))
    exps = ''.join(
        '<div class="ir-crit-exp" data-crit-exp="%s"%s><p>%s</p><p class="ir-op">%s <b>Operación:</b> %s</p></div>'
        % (c, '' if i == 0 else ' hidden', que, chip('oficial' if c == 'monto' else 'derivado'), op)
        for i, (c, _, _, que, op) in enumerate(CRITERIOS))
    return '''<div class="ir-controles">
          <div class="ir-crits" role="group" aria-label="Ordenar los 32 estados por">%s</div>
          %s
        </div>''' % (botones, exps)


def _lista(est, prom):
    orden = sorted(est, key=lambda x: -x['v']['intensidad'])
    p = prom / orden[0]['v']['intensidad'] * 100
    filas = []
    for x in orden:
        filas.append(
            '<li class="ir-li" %s><button type="button" class="ir-fila sem-%s" aria-controls="ir-e-%s" '
            'aria-label="%s: %s">'
            '<span class="ir-lugar">%d</span>'
            '<span class="ir-nom"><span class="ir-sem" aria-hidden="true">%s</span> %s</span>'
            '<span class="ir-val">%s</span>'
            '<span class="ir-barra" aria-hidden="true"><span class="ir-barra-v" style="--w:%.2f%%"></span>'
            '<span class="ir-barra-prom" style="--p:%.2f%%"></span></span>'
            '</button></li>' % (
                _attrs(x), x['sem'][0], x['slug'], _esc(x['nom']), x['f']['intensidad'],
                x['lugar']['intensidad'], x['sem'][1], _esc(x['nom']), x['f']['intensidad'], x['w']['intensidad'], p))
    leyenda = ('<ul class="ir-ley">'
               '<li><span aria-hidden="true">🔴</span> <b>Bandera roja</b>: por cada $100 revisados quedó 1.5 veces el promedio o más (≥ $%.2f)</li>'
               '<li><span aria-hidden="true">🟡</span> <b>Arriba del promedio</b> (≥ $%.2f)</li>'
               '<li><span aria-hidden="true">🟢</span> <b>Debajo del promedio</b></li>'
               '<li><span class="ir-ley-prom" aria-hidden="true"></span> La raya marca el promedio nacional (solo en «por cada $100»)</li>'
               '</ul>') % (prom * 1.5, prom)
    return '''<div class="ir-col-lista">
            <p class="ir-orden-tx" id="irOrdenTx" aria-live="polite">Ordenados por <b>por cada $100 revisados</b>, de mayor a menor.</p>
            <ol class="ir-lista" id="irLista" data-prom="%.4f">
            %s
            </ol>
            %s
          </div>''' % (p, '\n            '.join(filas), leyenda)


def _mapa(est):
    casillas = []
    for x in sorted(est, key=lambda x: (x['fil'], x['col'])):
        casillas.append(
            '<button type="button" class="ir-casilla q%d" %s aria-controls="ir-e-%s" style="--c:%d;--f:%d" '
            'title="%s: %s" aria-label="%s: %s"><span>%s</span></button>' % (
                x['q']['intensidad'], _attrs(x), x['slug'], x['col'] + 1, x['fil'] + 1,
                _esc(x['nom']), x['f']['intensidad'], _esc(x['nom']), x['f']['intensidad'], x['abr']))
    return '''<div class="ir-mapa-caja">
              <h3 class="ir-sub">🗺️ Mapa de calor</h3>
              <div class="ir-mapa" id="irMapa">%s</div>
              <ul class="ir-mapa-ley" aria-label="Colores del mapa">
                <li><span class="ir-mc q4" aria-hidden="true"></span> Los 8 más altos</li>
                <li><span class="ir-mc q3" aria-hidden="true"></span> Del 9 al 16</li>
                <li><span class="ir-mc q2" aria-hidden="true"></span> Del 17 al 24</li>
                <li><span class="ir-mc q1" aria-hidden="true"></span> Los 8 más bajos</li>
              </ul>
              <p class="ir-nota">Cada casilla es un estado, en una silueta aproximada del país. El color dice en qué grupo de ocho queda según el criterio elegido %s. Tócala para ver su ficha.</p>
            </div>''' % ('\n                '.join(casillas), chip('derivado'))


def _ficha(x, prom, C, acc, primero):
    e, t = x['e'], x['e']['total']
    r = x['v']['intensidad']
    sem = x['sem']
    if r >= prom:
        comp = 'Es <b>%s veces</b> el promedio nacional ($%.2f).' % (_num(r / prom, 1), prom)
    else:
        comp = 'Está <b>$%.2f por debajo</b> del promedio nacional ($%.2f).' % (prom - r, prom)
    tope = max(r, prom)
    # Desglose por ente.
    seg, filas = [], []
    for d in e['desglose']:
        k = _tipo_ente(d['ente'])
        w = d['porAclarar'] / t['porAclarar'] * 100 if t['porAclarar'] else 0
        if w > 0:
            seg.append('<span class="ir-pila-seg" style="--w:%.3f%%;--c:%s" title="%s: %s"></span>'
                       % (w, COLOR_ENTE[k], _esc(d['ente']), _num(w, 1) + ' %'))
        filas.append(
            '<tr><th scope="row"><span class="ir-punto" style="--c:%s" aria-hidden="true"></span>%s</th>'
            '<td class="ir-num" data-etq="Por aclarar">%s</td><td class="ir-num" data-etq="Parte">%s</td>'
            '<td class="ir-num" data-etq="Auditorías">%s</td><td class="ir-num" data-etq="Acciones">%s</td></tr>'
            % (COLOR_ENTE[k], _esc(d['ente']), _mdp(d['porAclarar']), _num(w, 1) + ' %', _num(d['auditorias']),
               _num(d['acciones'])))
    lugares = ''.join(
        '<li><b>%d.º</b> de 32 · %s</li>' % (x['lugar'][c], etq[0].lower() + etq[1:])
        for c, etq, *_ in CRITERIOS)
    nombre_matriz = '' if x['nom'] == e['entidad'] else ' <span class="ir-f-matriz">(en la Matriz: «%s»)</span>' % _esc(e['entidad'])
    return '''<article class="ir-ficha sem-%s" id="ir-e-%s" data-ent="%s" tabindex="-1" aria-labelledby="ir-t-%s"%s>
                <header class="ir-f-cab">
                  <span class="ir-f-sem">%s %s</span>
                  <h3 class="ir-f-tit" id="ir-t-%s">%s%s</h3>
                </header>
                <div class="ir-f-cifras">
                  <div class="ir-fc"><small>Por aclarar %s</small><b>%s</b></div>
                  <div class="ir-fc"><small>De cada $100 revisados %s</small><b>$%.2f</b></div>
                  <div class="ir-fc"><small>Auditorías · acciones %s</small><b>%s · %s</b></div>
                </div>
                <div class="ir-comp">
                  <p>%s Por cada $100 revisados quedó %s; eso es %s.</p>
                  <div class="ir-comp-b"><span>%s</span><span class="ir-comp-barra"><span class="sem-%s" style="--w:%.2f%%"></span></span><b>$%.2f</b></div>
                  <div class="ir-comp-b"><span>Promedio nacional</span><span class="ir-comp-barra"><span class="ir-comp-prom" style="--w:%.2f%%"></span></span><b>$%.2f</b></div>
                  <p class="ir-op">%s %s ÷ %s de muestra auditada × 100.</p>
                </div>
                <h4 class="ir-f-sub">Su lugar entre los 32 %s</h4>
                <ul class="ir-lugares">%s</ul>
                <h4 class="ir-f-sub">¿Quién tiene que aclararlo?</h4>
                <div class="ir-pila" role="img" aria-label="Reparto de lo que quedó por aclarar entre los entes del estado">%s</div>
                <div class="ir-tabla-caja">
                  <table class="ir-tabla">
                    <thead><tr><th scope="col">Ente</th><th scope="col">Por aclarar %s</th><th scope="col">Parte %s</th><th scope="col">Auditorías %s</th><th scope="col">Acciones %s</th></tr></thead>
                    <tbody>%s</tbody>
                  </table>
                </div>
                <p class="ir-op">La parte de cada ente divide su monto por aclarar entre el del estado (%s) × 100. «Otros» es como la Matriz agrupa a los entes que no son el gobierno estatal ni los municipios.</p>
                <h4 class="ir-f-sub">Más de la Matriz %s</h4>
                <dl class="ir-dl">
                  <div><dt>Universo seleccionado</dt><dd>%s</dd></div>
                  <div><dt>Muestra auditada</dt><dd>%s</dd></div>
                  <div><dt>Pliegos de observaciones (PO)</dt><dd>%s</dd></div>
                  <div><dt>Promociones de responsabilidad (PRAS)</dt><dd>%s</dd></div>
                  <div><dt>Recuperado durante la auditoría</dt><dd>%s</dd></div>
                </dl>
                <p class="ir-fuente">Fuente: %s</p>
                <div class="ir-f-acc">
                  <a class="ir-btn ir-btn-of" href="%s#ente=estatal:%s">🏢 Su ficha técnica en el Auditor</a>
                  <a class="ir-btn" href="herramienta-inspector-asf.html">🏛️ Ver qué encontró la ASF</a>
                  <a class="ir-btn" href="informes-cuenta-publica.html">🔎 Informes de la Cuenta Pública</a>
                  <a class="ir-btn" href="numeros-las-32-entidades.html">🧭 Cuánto recibe cada estado</a>
                </div>
              </article>''' % (
        sem[0], x['slug'], x['slug'], x['slug'], '' if primero else ' hidden',
        sem[1], sem[2], x['slug'], _esc(x['nom']), nombre_matriz,
        chip('oficial'), _mdp(t['porAclarar']), chip('derivado'), r, chip('oficial'), _num(t['auditorias']), _num(t['acciones']),
        sem[1], '$%.2f' % r, sem[3], _esc(x['nom']), sem[0], r / tope * 100, r, prom / tope * 100, prom,
        chip('derivado'), _mdp(t['porAclarar']), _mdp(t['muestra']),
        chip('derivado'), lugares,
        ''.join(seg) or '<span class="ir-pila-vacia">Sin monto por aclarar</span>',
        chip('oficial'), chip('derivado'), chip('oficial'), chip('oficial'), '\n                    '.join(filas),
        _mdp(t['porAclarar']), chip('oficial'),
        _mdp(t['universo']), _mdp(t['muestra']), _num(t['PO']), _num(t['PRAS']), _mdp(t['recuperaciones']),
        _fuente(C), AUDITOR, CLAVE_AUDITOR.get(x['abr'], x['abr']))


def _glosario(C):
    acc = {a['clave']: a for a in C['acciones']}
    def a(k):
        x = acc[k]
        return '<div><dt>%s (%s)</dt><dd>%s <small>%s</small></dd></div>' % (_esc(x['nombre']), k, _esc(x['que']), _esc(x['fundamento']))
    return '''<section class="ir-sec" aria-labelledby="irGlosTit">
        <h2 class="ir-tit" id="irGlosTit"><span aria-hidden="true">📖</span> Las palabras de la ficha</h2>
        <dl class="ir-glos">
          <div><dt>Monto por aclarar</dt><dd>Dinero que, al cierre de la auditoría, no tenía documentos que acreditaran su uso. Puede solventarse después.</dd></div>
          <div><dt>Universo seleccionado y muestra auditada</dt><dd>El universo es el dinero que la Auditoría eligió fiscalizar; la muestra, la parte que de verdad revisó. «Por cada $100 revisados» se mide contra la muestra.</dd></div>
          %s
          %s
          %s
          <div><dt>Recuperaciones</dt><dd>Dinero que el ente devolvió o justificó mientras la auditoría estaba en curso.</dd></div>
        </dl>
      </section>''' % (a('SA'), a('PO'), a('PRAS'))


def construir(base, ref):
    C = base['cuenta_publica_asf']
    est, pa, mu, prom = _estados(C)
    acc = {a['clave']: a for a in C['acciones']}
    orden = sorted(est, key=lambda x: -x['v']['intensidad'])
    opciones = ''.join('<option value="%s">%s</option>' % (x['slug'], _esc(x['nom']))
                       for x in sorted(est, key=lambda x: _slug(x['nom'])))
    fichas = '\n              '.join(_ficha(x, prom, C, acc, i == 0) for i, x in enumerate(orden))
    seguir = '''<section class="ir-sec" aria-labelledby="irSigueTit">
        <h2 class="ir-tit" id="irSigueTit"><span aria-hidden="true">🧭</span> Sigue investigando</h2>
        <div class="ir-sigue">
          <a class="ir-sig" href="herramienta-inspector-entes.html"><b>🏢 Auditor de entes públicos</b><span>De aquí vienes: la ficha técnica de cada estado, dependencia y municipio.</span></a>
          <a class="ir-sig" href="herramienta-inspector-asf.html"><b>🏛️ Qué encontró la ASF</b><span>Lo que la Auditoría observó en la Cuenta Pública, ente por ente y estado por estado.</span></a>
          <a class="ir-sig" href="expedientes.html"><b>📂 Expedientes de casos</b><span>Casos concretos por aclarar, con sus documentos.</span></a>
          <a class="ir-sig" href="numeros-las-32-entidades.html"><b>🧭 Las 32 entidades</b><span>Cuánto dinero federal recibe cada estado y por qué vía.</span></a>
          <a class="ir-sig" href="numeros-los-municipios.html"><b>🏘️ Los municipios</b><span>Qué reciben y qué gastan los ayuntamientos.</span></a>
        </div>
      </section>'''
    return '\n      '.join([
        '<div class="ir" id="irRaiz" data-crit="intensidad">',
        _hero(est, pa, mu, prom, C, ref),
        _aviso(C),
        '''<section class="ir-sec" id="ir-radar" aria-labelledby="irRadarTit">
        <h2 class="ir-tit" id="irRadarTit"><span aria-hidden="true">🚩</span> Los 32 estados, ordenados como prefieras</h2>
        <p class="ir-txt">Elige un criterio y la lista se reordena. Toca un estado, en la lista o en el mapa, para ver su ficha: cuánto quedó por aclarar, cómo se compara con el promedio y quién lo tiene que aclarar.</p>
        %s
        <div class="ir-busca">
          <label for="irBusca">🔍 Busca tu estado</label>
          <select id="irBusca">%s</select>
        </div>
        <div class="ir-tablero">
          %s
          <div class="ir-col-ficha">
            %s
            <div class="ir-fichas" id="irFichas">
              %s
            </div>
          </div>
        </div>
        <p class="ir-nota">%s Monto por aclarar, muestra, auditorías y acciones: %s %s. %s Por cada $100 revisados, peso de los municipios, lugares, sumas y promedio: operaciones de Auditavisión con esas cifras.</p>
      </section>''' % (_criterios(prom), opciones, _lista(est, prom), _mapa(est), fichas,
                       chip('oficial'), _fuente(C), ref('ref-asf-mdb2024'), chip('derivado')),
        _glosario(C),
        seguir,
        '</div>'])
