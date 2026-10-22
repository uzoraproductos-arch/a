# -*- coding: utf-8 -*-
"""Inversion y Megaobras, capitulo 2: «La tabla general en vivo» (pedido
del autor, 21-10-2026) y la portada de la herramienta en capitulos.

El autor pidio una tabla general donde se vean los sexenios, en que
invirtio cada presidente, cuanto costo y, en vivo, si cada inversion
genera dinero (numero verde) o lo pierde (numero rojo). No hay cifra
nueva: cada renglon sale de simulador_megaobras, las mismas que pintan
los otros capitulos.

- Aprobado, costo y sobrecosto: los campos de la obra, con su estado
  (estado_campos) y, si es rango, su minimo y su maximo.
- Gana o pierde: la medida unica de la herramienta (mo_base.resultado):
  el resultado del año mas reciente publicado, sin el apoyo del
  presupuesto cuando se publica asi. Si la obra no lo publica, el renglon
  dice por que y a quien le toca (pendiente); si no opera, «no aplica».
- El contador: el resultado del año entre los 31,536,000 segundos de un
  año de 365 dias, proyectado sobre el tiempo que llevas mirando. No es un
  gasto que ocurra en ese instante, y asi se dice.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['tabla']); la portada de
la herramienta usa portada().
"""
import html

from presupuesto_modulos import chip
import mo_base
import mo_capitulos
import mo_pulso
import mo_sexenios
from mo_sexenios import SEXENIOS, obras_de

# Desde el 21-10-2026 (pedido del autor) la pagina es la aplicacion 1 y
# trae tambien los seis sexenios (mo_sexenios) y la ventana del calculo
# (mo-pulso.css da el boton).
ESTILOS = ['mo-tabla.css', 'mo-sexenios.css', 'mo-pulso.css']
SCRIPTS = ['mo-tabla.js', 'mo-sexenios.js']

SEG_ANO = 365 * 86400
ARCHIVO = 'herramienta-megaobras-tabla.html'
CUENTA = 'herramienta-megaobras-pulso-cuenta.html'
SECTOR = 'herramienta-megaobras-sector.html'


def esc(t):
    return html.escape(str(t if t is not None else ''), quote=True)


mdp = mo_pulso.mdp
sim_mdp = mo_pulso.sim_mdp


def _tasa(v):
    """Pesos por segundo de un resultado anual en mdp."""
    return v * 1e6 / SEG_ANO


def _signo(v):
    return 'mt-gana' if v > 0 else ('mt-pierde' if v < 0 else 'mt-cero')


def _sin_signo(v):
    return mdp(abs(v))


def _cifra(o, campo, fmt):
    e = (o.get('estado_campos') or {}).get(campo) or 'pendiente'
    rango = mo_pulso._rango_txt(o, campo, fmt)
    return ('<span class="mt-num">%s%s</span> %s'
            % ((esc(rango) + ' ') if rango else '', fmt(o[campo]), chip(e, ('obra-' + o['id']) if e == 'pendiente' else None)))


def _pct(v):
    return ('+' if v > 0 else '') + format(v, '.1f') + ' %'


def _vivo(v, clase=''):
    """Contador: arranca en cero y lo mueve mo-tabla.js."""
    return ('<b class="mt-vivo mt-num %s%s" data-mt-tasa="%r" aria-live="off">%s$0.00</b>'
            % (_signo(v), (' ' + clase) if clase else '', _tasa(v), '−' if v < 0 else '+'))


BASE = {'sin_apoyo': 'antes del apoyo del presupuesto', 'ejercicio': 'resultado del ejercicio publicado'}


def _celda_res(r, oid):
    if r['tipo'] == 'dato':
        v = r['v']
        verbo = 'Gana' if v > 0 else ('Pierde' if v < 0 else 'Sin ganancia ni pérdida')
        return ('<p class="mt-res %s"><span class="mt-res-ico" aria-hidden="true">%s</span> <b>%s %s al año</b> '
                '<small>(%s, %s)</small> %s</p>'
                '<p class="mt-res-vivo">Desde que abriste esta página: %s</p>'
                % (_signo(v), '▲' if v > 0 else '▼', verbo, _sin_signo(v), r['anio'], BASE[r['base']], chip(r['e']), _vivo(v)))
    if r['tipo'] == 'no_aplica':
        return ('<p class="mt-res mt-cero"><span class="mt-res-ico" aria-hidden="true">●</span> <b>No aplica</b> '
                '<small>%s</small></p>' % esc(r['txt']))
    return ('<p class="mt-res mt-cero"><span class="mt-res-ico" aria-hidden="true">●</span> <b>Sin resultado publicado</b> %s</p>'
            '<p class="mt-por"><b>Por qué falta:</b> %s</p>' % (chip('pendiente', 'cuenta-' + oid), esc(r['txt'])))


def _fila_obra(o, sectores, r):
    sec = sectores.get(o['sector_id']) or {}
    resc = o.get('tipo') == 'rescate'
    como = ''
    if r['tipo'] == 'dato':
        como = ('<details class="mt-como"><summary>De dónde sale</summary><p>%s%s</p><p>Fuente: %s</p></details>'
                % (esc(r['op']), (' ' + esc(r['nota'])) if r['nota'] else '', mo_pulso._fuentes_fila(r)))
    return (
        '<li class="mt-obra%s" id="mt-%s">'
        '<div class="mt-obra-cab"><span class="mt-obra-ico" aria-hidden="true">%s</span>'
        '<div><h4 class="mt-obra-tit">%s</h4><p class="mt-obra-sub">%s%s · %s</p></div></div>'
        '<dl class="mt-dl">'
        '<div><dt>%s</dt><dd>%s</dd></div>'
        '<div><dt>%s</dt><dd>%s</dd></div>'
        '<div><dt>%s</dt><dd>%s</dd></div>'
        '</dl>'
        '<div class="mt-res-caja">%s%s</div>'
        '<p class="mt-obra-pie"><a href="%s#cuenta-%s">Su cuenta completa</a> · <a href="%s#obra-%s">Su ficha</a></p>'
        '</li>'
        % (' mt-rescate' if resc else '', o['id'], o['icono'], esc(o['nombre']),
           ('<b class="mt-etq">Rescate: deuda, no obra</b> ' if resc else ''),
           esc(sec.get('nombre', '')), esc(o.get('estatus') or ''),
           'Presentado en su momento' if resc else 'Aprobado', _cifra(o, 'inversion_presupuestada_mdp', mdp),
           'Pagado y debido' if resc else 'Costo real', _cifra(o, 'inversion_real_mdp', mdp),
           esc(o.get('sobrecosto_etiqueta') or 'Sobrecosto'), _cifra(o, 'sobrecosto_pct', _pct),
           _celda_res(r, o['id']), como, CUENTA, o['id'], SECTOR, o['id']))


def _datos(base):
    sm = base['simulador_megaobras']
    sectores = {s['id']: s for s in sm['sectores']}
    res = mo_base.resultados(sm)
    grupos = []
    for clave, apellido, corto, nombre, a0, a1, color in SEXENIOS:
        ob = obras_de(sm['obras'], apellido)
        dat = [res[o['id']]['v'] for o in ob if res[o['id']]['tipo'] == 'dato']
        grupos.append({'clave': clave, 'corto': corto, 'nombre': nombre, 'a0': a0, 'a1': a1, 'color': color, 'obras': ob,
                       'costo': sum(o['inversion_real_mdp'] for o in ob),
                       'rescates': sum(1 for o in ob if o.get('tipo') == 'rescate'),
                       'pend_costo': any(((o.get('estado_campos') or {}).get('inversion_real_mdp') or 'pendiente') == 'pendiente' for o in ob),
                       'res': sum(dat), 'n_res': len(dat)})
    todos = [r for r in res.values() if r['tipo'] == 'dato']
    return sm, sectores, res, grupos, todos


def _resumen(grupos, todos, n_obras):
    filas = []
    for g in grupos:
        costo = (sim_mdp(g['costo']) + (' <small>con %d rescate%s</small>' % (g['rescates'], 's' if g['rescates'] > 1 else '')
                                        if g['rescates'] else '')) if g['obras'] else '—'
        if g['n_res']:
            res = ('<span class="mt-num %s">%s%s</span> <small>%d de %d con dato</small><br>%s'
                   % (_signo(g['res']), '−' if g['res'] < 0 else '+', _sin_signo(g['res']), g['n_res'], len(g['obras']), _vivo(g['res'])))
        elif g['obras']:
            res = '<span class="mt-gris">Ninguna publica su resultado</span>'
        else:
            res = '<span class="mt-gris">Sin obras evaluadas</span>'
        filas.append('<tr><th scope="row"><a href="#mt-sx-%s"><span class="mt-sx-color" style="--sx:%s" aria-hidden="true"></span>%s</a>'
                     '<small>%d–%d</small></th><td class="mt-num">%d</td><td class="mt-num">%s</td><td>%s</td></tr>'
                     % (g['clave'], g['color'], esc(g['corto']), g['a0'], g['a1'], len(g['obras']), costo, res))
    tot = sum(r['v'] for r in todos)
    costo_tot = sum(g['costo'] for g in grupos)
    return (
        '<div class="mt-marco"><table class="mt-tabla">'
        '<caption>La tabla general: los seis sexenios</caption>'
        '<thead><tr><th scope="col">Sexenio</th><th scope="col">Obras</th><th scope="col">Costo registrado %s</th>'
        '<th scope="col">Gana o pierde al año %s</th></tr></thead>'
        '<tbody>%s</tbody>'
        '<tfoot><tr><th scope="row">Los seis</th><td class="mt-num">%d</td><td class="mt-num">%s <small>las %d obras y los 2 rescates, '
        'solo como referencia</small></td><td><span class="mt-num %s">%s%s</span> <small>%d obras con dato</small><br>%s</td></tr></tfoot>'
        '</table></div>'
        % (chip('derivado'), chip('derivado'), ''.join(filas), sum(len(g['obras']) for g in grupos), sim_mdp(costo_tot), n_obras,
           _signo(tot), '−' if tot < 0 else '+', _sin_signo(tot), len(todos), _vivo(tot)))


def _grupo(g, sectores, res):
    if not g['obras']:
        cuerpo = ('<p class="mt-vacio">Sin obras evaluadas. Las concesiones carreteras que fracasaron se otorgaron con él, '
                  'pero se rescataron y se pagaron desde 1997: ese rescate (el FARAC) se cuenta con Ernesto Zedillo, que lo hizo. '
                  '<a href="#mxLinea">La línea del tiempo</a>, más abajo, lo explica.</p>')
        cab = ''
    else:
        cab = ('<p class="mt-sx-cifras"><span>%d obra%s</span> · <span>costo registrado <b class="mt-num">%s</b></span>%s</p>'
               % (len(g['obras']), '' if len(g['obras']) == 1 else 's', sim_mdp(g['costo']),
                  (' · <span>al año <b class="mt-num %s">%s%s</b> (%d con dato)</span>'
                   % (_signo(g['res']), '−' if g['res'] < 0 else '+', _sin_signo(g['res']), g['n_res'])) if g['n_res'] else
                  ' · <span class="mt-gris">ninguna publica su resultado</span>'))
        cuerpo = '<ol class="mt-obras">%s</ol>' % ''.join(_fila_obra(o, sectores, res[o['id']]) for o in g['obras'])
    return ('<section class="mt-sx" id="mt-sx-%s" style="--sx:%s" tabindex="-1" aria-labelledby="mt-sx-%s-t">'
            '<h3 class="mt-sx-tit" id="mt-sx-%s-t"><small>%d–%d</small> %s</h3>%s%s</section>'
            % (g['clave'], g['color'], g['clave'], g['clave'], g['a0'], g['a1'], esc(g['nombre']), cab, cuerpo))


CONTROLES = '''<div class="mt-ctl">
        <button type="button" class="mt-boton" data-mt-pausa aria-pressed="false"><span aria-hidden="true">⏸️</span> <span>Pausar</span></button>
        <button type="button" class="mt-boton" data-mt-cero><span aria-hidden="true">↺</span> Volver a cero</button>
      </div>'''


def construir(base, ref):
    sm, sectores, res, grupos, todos = _datos(base)
    n_obras = sum(1 for o in sm['obras'] if o.get('tipo') != 'rescate')
    gana = [r for r in todos if r['v'] > 0]
    pierde = [r for r in todos if r['v'] < 0]
    sin = [o for o in sm['obras'] if res[o['id']]['tipo'] == 'pendiente']
    na = [o for o in sm['obras'] if res[o['id']]['tipo'] == 'no_aplica']
    tot = sum(r['v'] for r in todos)
    anios = sorted({r['anio'] for r in todos})
    c = mo_pulso._contexto(base, ref)
    return mo_pulso.cajon_calculo(base, ref, c) + '''<div class="mt" id="mtRaiz">
  <section class="mt-arranque" aria-labelledby="mtArrTit">
    <p class="mt-kicker">{kicker}</p>
    <h2 class="mt-grande" id="mtArrTit">En qué invirtió cada presidente, cuánto costó y qué se gana</h2>
    <p class="mt-lead">Las {n_tot} obras y rescates, cada una en el sexenio en que se contrató: en qué se invirtió, cuánto se aprobó, cuánto costó y si hoy <b>gana dinero</b> (número verde) o <b>lo pierde</b> (número rojo). El contador corre con el resultado del año que publica cada obra. Si no lo publica, el renglón queda en gris y dice por qué falta y a quién le toca. Más abajo, la línea del tiempo de 1988 a 2024 y dos sexenios frente a frente.</p>
    <ol class="mx-indice" aria-label="Lo que hay en esta página">
      <li><a href="#mtResTit"><span aria-hidden="true">📋</span> La tabla general</a></li>
      <li><a href="#mtObTit"><span aria-hidden="true">🚦</span> Obra por obra, en verde o en rojo</a></li>
      <li><a href="#mxLinea"><span aria-hidden="true">🕰️</span> La línea del tiempo</a></li>
      <li><a href="#mxComparar"><span aria-hidden="true">⚖️</span> Compara dos sexenios</a></li>
    </ol>
    <div class="mt-claves">
      <p><span>Costo real de las {n} obras</span><b class="mt-num">{real}</b> {chip_der}</p>
      <p><span>Pagado de más sobre lo aprobado</span><b class="mt-num">{brecha}</b> {chip_der}</p>
      <p><span>Ganancia o pérdida del año, donde se publica</span><b class="mt-num {sig}">{tot}</b> {chip_der}</p>
    </div>
    <div class="mt-pantalla">
      <p class="mt-vivo-et"><span class="mt-punto" aria-hidden="true"></span> Desde que abriste esta página, las {n_dat} obras con resultado publicado van:</p>
      <p class="mt-vivo-total">{vivo_tot}</p>
      <div class="mt-balanza">
        <p class="mt-gana"><span aria-hidden="true">▲</span> Ganan {n_gana}: <b class="mt-num">{gana}</b> al año</p>
        <p class="mt-pierde"><span aria-hidden="true">▼</span> Pierden {n_pierde}: <b class="mt-num">{pierde}</b> al año</p>
        <p class="mt-cero"><span aria-hidden="true">●</span> Sin resultado publicado: {n_sin} · No operan: {n_na}</p>
      </div>
      <p class="mt-vivo-sub">Suma de los resultados del año publicados ({tot}) {chip_der}, cada obra con su año más reciente ({anios}), entre los 31,536,000 segundos de un año de 365 días. No es dinero que se mueva en este instante: proyecta el resultado de un año sobre el tiempo que llevas mirando.</p>
      {controles}
    </div>
  </section>

  <section class="mt-sec" aria-labelledby="mtResTit">
    <h2 class="mt-tit" id="mtResTit"><span aria-hidden="true">📋</span> La tabla general</h2>
    <p class="mt-txt">Un renglón por sexenio. Pulsa el nombre del presidente para ver sus obras una por una.</p>
    {resumen}
  </section>

  <section class="mt-sec" aria-labelledby="mtObTit">
    <h2 class="mt-tit" id="mtObTit"><span aria-hidden="true">🏛️</span> Las obras de cada sexenio</h2>
    <p class="mt-leyenda"><span class="mt-gana">▲ verde: gana</span> <span class="mt-pierde">▼ rojo: pierde</span> <span class="mt-cero">● gris: sin dato o no aplica</span></p>
    {grupos}
  </section>

  <aside class="mt-nota">
    <p>{medida}</p>
    <p><b>Cómo leer la tabla.</b> «Gana o pierde» no descuenta lo que costó construir la obra: una obra puede ganar en el año y haber costado mucho más de lo aprobado. Los años no son iguales para todas ({anios}) y las cifras son nominales, sin deflactar. Cada renglón está completo en <a href="{cuenta}">La cuenta de cada obra</a>.</p>
    <p><b>Los rescates.</b> El FOBAPROA y el FARAC son deudas que el Estado asumió, no obras: su «costo» es lo pagado y lo debido, y su crecimiento no se compara con el sobrecosto de una obra. En la tabla general su costo se suma con el de las obras solo como referencia.</p>
    <p><b>Cómo se calcula.</b> Costo del sexenio = suma del costo registrado de sus obras {chip_der}; donde una obra tiene rango, entra su punto medio. Gana o pierde al año = suma de los resultados publicados {chip_der}. Por segundo = resultado anual × 1,000,000 ÷ 31,536,000. Lo que falta está en el <a href="pendientes.html#tema-megaobras">Registro de pendientes</a>.</p>
  </aside>
</div>
'''.format(
        n=c['n'], real=c['real'], brecha=c['brecha'], sig=_signo(tot),
        kicker=mo_capitulos.kicker(ARCHIVO), n_tot=len(sm['obras']), n_dat=len(todos), vivo_tot=_vivo(tot, 'mt-grande-num'),
        n_gana=len(gana), gana=_sin_signo(sum(r['v'] for r in gana)), n_pierde=len(pierde), pierde=_sin_signo(sum(r['v'] for r in pierde)),
        n_sin=len(sin), n_na=len(na), tot=mdp(tot), chip_der=chip('derivado'), anios=', '.join(str(a) for a in anios),
        controles=CONTROLES, resumen=_resumen(grupos, todos, n_obras),
        grupos='\n    '.join(_grupo(g, sectores, res) for g in grupos), cuenta=CUENTA,
        medida=mo_base.medida_txt(sm)) + _sexenios(base, ref)


def _sexenios(base, ref):
    """Los seis sexenios (mo_sexenios) debajo de la tabla, sin su
    portadilla (el arranque de la tabla ya dice que hay en la pagina) ni
    sus fichas por sexenio: las obras de cada sexenio se ven una sola vez,
    en la tabla (pedido del autor, 21-10-2026). Tocar un sexenio en la
    linea del tiempo lleva a sus obras en la tabla (mo-sexenios.js)."""
    import re
    h = mo_sexenios.construir(base, ref)
    h = re.sub(r'\s*<section class="mx-arranque".*?</section>', '', h, count=1, flags=re.S)
    return re.sub(r'\s*<section class="mx-bloque" id="mxFicha".*?\n  </section>', '', h, count=1, flags=re.S)


def cifras(base, ref):
    """La cifra de cada tarjeta de aplicacion en la portada (apartados.apps_rejilla)."""
    c = mo_pulso._contexto(base, ref)
    _sm, _s, _r, grupos, todos = _datos(base)
    tot = sum(r['v'] for r in todos)
    return {
        'investiga': '7 opciones × 6 preguntas · cada respuesta con su documento',
        'tabla': '6 presidentes · %d obras · %s%s al año, en vivo' % (sum(len(g['obras']) for g in grupos), '−' if tot < 0 else '+', _sin_signo(tot)),
        'sector': '%d obras y %d rescates en 6 industrias' % (c['n'], c['n_resc']),
        'cifras': '%s de costo real · %s de sobrecosto' % (c['real'], c['sobre']),
        'cuenta': '%d obras publican su ganancia o pérdida' % len(todos),
    }
