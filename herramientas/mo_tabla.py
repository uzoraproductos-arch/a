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
- Gana o pierde: el resultado del año mas reciente publicado de la obra
  (cuenta, renglon resultado_anual_mdp), el mismo que suma «La cuenta de
  cada obra» (mo_pulso._resultados). Si la obra no lo publica, el renglon
  dice por que y a quien le toca (pendiente); si no opera, «no aplica».
- El contador: el resultado del año entre los 31,536,000 segundos de un
  año de 365 dias, proyectado sobre el tiempo que llevas mirando. No es un
  gasto que ocurra en ese instante, y asi se dice.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['tabla']); la portada de
la herramienta usa portada().
"""
import html

from presupuesto_modulos import chip
import mo_capitulos
import mo_pulso
from mo_sexenios import SEXENIOS, obras_de

ESTILOS = ['mo-tabla.css']
SCRIPTS = ['mo-tabla.js']

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


def resultado(o, filas):
    """Lo que dice la tabla en la columna «gana o pierde»."""
    con = [f for f in filas if f['c'] == 'resultado_anual_mdp' and 'v' in f]
    if con:
        f = max(con, key=lambda x: x.get('anio') or 0)
        return {'tipo': 'dato', 'v': f['v'], 'anio': f.get('anio'), 'e': f['e'], 'op': f.get('op') or '',
                'nota': f.get('nota') or '', 'fu': mo_pulso._fuentes_fila(f), 'et': f['et']}
    f = next((x for x in filas if x['c'] == 'resultado_anual_mdp'), None)
    if f and f['e'] == 'no_aplica':
        return {'tipo': 'no_aplica', 'txt': f.get('op') or 'No aplica.'}
    if f and f['e'] == 'pendiente':
        return {'tipo': 'pendiente', 'txt': f.get('resp') or ''}
    # Sin renglon de resultado: se dice lo que la cuenta si trae sobre su
    # operacion (el Bunker: la SSPC no publica el gasto del edificio).
    g = next((x for x in filas if x['c'] == 'costo_operativo_anual_mdp' and x['e'] == 'pendiente'), None)
    return {'tipo': 'pendiente', 'txt': (g.get('resp') if g else '') or 'Su cuenta no trae renglón de ganancia o pérdida.'}


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


def _celda_res(r, oid):
    if r['tipo'] == 'dato':
        v = r['v']
        verbo = 'Gana' if v > 0 else ('Pierde' if v < 0 else 'Sin ganancia ni pérdida')
        return ('<p class="mt-res %s"><span class="mt-res-ico" aria-hidden="true">%s</span> <b>%s %s al año</b> '
                '<small>(%s)</small> %s</p>'
                '<p class="mt-res-vivo">Desde que abriste esta página: %s</p>'
                % (_signo(v), '▲' if v > 0 else '▼', verbo, _sin_signo(v), r['anio'], chip(r['e']), _vivo(v)))
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
                % (esc(r['op']), (' ' + esc(r['nota'])) if r['nota'] else '', r['fu']))
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
    cu = (sm.get('cuenta') or {}).get('obras') or {}
    sectores = {s['id']: s for s in sm['sectores']}
    res = {o['id']: resultado(o, cu.get(o['id']) or []) for o in sm['obras']}
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
                  '<a href="herramienta-megaobras-sexenios.html">La línea del tiempo</a> lo explica.</p>')
        cab = ''
    else:
        cab = ('<p class="mt-sx-cifras"><span>%d obra%s</span> · <span>costo registrado <b class="mt-num">%s</b></span>%s</p>'
               % (len(g['obras']), '' if len(g['obras']) == 1 else 's', sim_mdp(g['costo']),
                  (' · <span>al año <b class="mt-num %s">%s%s</b> (%d con dato)</span>'
                   % (_signo(g['res']), '−' if g['res'] < 0 else '+', _sin_signo(g['res']), g['n_res'])) if g['n_res'] else
                  ' · <span class="mt-gris">ninguna publica su resultado</span>'))
        cuerpo = '<ol class="mt-obras">%s</ol>' % ''.join(_fila_obra(o, sectores, res[o['id']]) for o in g['obras'])
    return ('<section class="mt-sx" id="mt-sx-%s" style="--sx:%s" aria-labelledby="mt-sx-%s-t">'
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
    return '''<div class="mt" id="mtRaiz">
  <section class="mt-arranque" aria-labelledby="mtArrTit">
    <p class="mt-kicker">{kicker}</p>
    <h2 class="mt-grande" id="mtArrTit">🚦 ¿Gana o pierde? Las {n_tot} obras, sexenio por sexenio</h2>
    <p class="mt-lead">Cada renglón es una obra, en el sexenio en que se contrató: en qué se invirtió, cuánto se aprobó, cuánto costó y si hoy <b>gana dinero</b> (número verde) o <b>lo pierde</b> (número rojo). El contador corre con el resultado del año que publica cada obra. Si no lo publica, el renglón queda en gris y dice por qué falta y a quién le toca.</p>
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
    <p><b>Cómo leer la tabla.</b> «Gana o pierde» es el resultado del año que publica la empresa o el fondo que opera la obra, el mismo de <a href="{cuenta}">La cuenta de cada obra</a>: no descuenta lo que costó construirla. Por eso una obra puede ganar en el año y haber costado mucho más de lo aprobado. Los años no son iguales para todas ({anios}) y las cifras son nominales, sin deflactar.</p>
    <p><b>Los rescates.</b> El FOBAPROA y el FARAC son deudas que el Estado asumió, no obras: su «costo» es lo pagado y lo debido, y su crecimiento no se compara con el sobrecosto de una obra. En la tabla general su costo se suma con el de las obras solo como referencia.</p>
    <p><b>Cómo se calcula.</b> Costo del sexenio = suma del costo registrado de sus obras {chip_der}; donde una obra tiene rango, entra su punto medio. Gana o pierde al año = suma de los resultados publicados {chip_der}. Por segundo = resultado anual × 1,000,000 ÷ 31,536,000. Lo que falta está en el <a href="pendientes.html#tema-megaobras">Registro de pendientes</a>.</p>
  </aside>
</div>'''.format(
        kicker=mo_capitulos.kicker(ARCHIVO), n_tot=len(sm['obras']), n_dat=len(todos), vivo_tot=_vivo(tot, 'mt-grande-num'),
        n_gana=len(gana), gana=_sin_signo(sum(r['v'] for r in gana)), n_pierde=len(pierde), pierde=_sin_signo(sum(r['v'] for r in pierde)),
        n_sin=len(sin), n_na=len(na), tot=mdp(tot), chip_der=chip('derivado'), anios=', '.join(str(a) for a in anios),
        controles=CONTROLES, resumen=_resumen(grupos, todos, n_obras),
        grupos='\n    '.join(_grupo(g, sectores, res) for g in grupos), cuenta=CUENTA)


def cifras(base, ref):
    """La cifra de cada tarjeta de capitulo en la portada."""
    c = mo_pulso._contexto(base, ref)
    _sm, _s, _r, grupos, todos = _datos(base)
    tot = sum(r['v'] for r in todos)
    return {
        'sexenios': '6 presidentes · %d obras' % sum(len(g['obras']) for g in grupos),
        'tabla': '%s%s al año, en vivo' % ('−' if tot < 0 else '+', _sin_signo(tot)),
        'cero': '%s pagados de más' % c['brecha'],
        'cifras': '%s de costo real · %s de sobrecosto' % (c['real'], c['sobre']),
        'sector': '%d obras y %d rescates en 6 industrias' % (c['n'], c['n_resc']),
        'composicion': c['compo_cif'],
        'cuenta': '%d obras publican su ganancia o pérdida' % len(todos),
        'ritmo': '%s de pérdida y apoyo documentados' % c['per_v'],
        'calculo': 'Las operaciones y sus fuentes, paso a paso',
    }


def portada(base, ref):
    """Bloque de la portada de la herramienta: el contador de la balanza y
    los capitulos agrupados por pregunta. Cada tarjeta abre su pagina."""
    sm, _s, _res, _g, todos = _datos(base)
    c = mo_pulso._contexto(base, ref)
    cif = cifras(base, ref)
    tot = sum(r['v'] for r in todos)
    bloques = []
    k = 0
    for clave, pregunta, frase in mo_capitulos.BLOQUES:
        tarjetas = []
        for b, archivo, ico, corto, desc, ck in mo_capitulos.CAPITULOS:
            if b != clave:
                continue
            k += 1
            neg = ' mt-pierde' if ck == 'tabla' and tot < 0 else ''
            tarjetas.append(
                '<li><a class="mt-cap" href="%s"><span class="mt-cap-num">Capítulo %d</span>'
                '<span class="mt-cap-tit"><span aria-hidden="true">%s</span> %s</span>'
                '<span class="mt-cap-desc">%s</span><span class="mt-cap-cif mt-num%s">%s</span>'
                '<span class="mt-cap-ir">Abrir <span aria-hidden="true">→</span></span></a></li>'
                % (archivo, k, ico, esc(corto), esc(desc), neg, esc(cif[ck])))
        bloques.append('<section class="mt-bloque" aria-labelledby="mtB-%s"><h3 class="mt-bloque-tit" id="mtB-%s">%s</h3>'
                       '<p class="mt-bloque-txt">%s</p><ol class="mt-caps">%s</ol></section>'
                       % (clave, clave, esc(pregunta), esc(frase), ''.join(tarjetas)))
    return '''<div class="mt mt-portada" id="mtRaiz">
  <section class="mt-arranque" aria-labelledby="mtArrTit">
    <h2 class="mt-grande" id="mtArrTit">En qué invirtió cada presidente, cuánto costó y si hoy gana o pierde</h2>
    <div class="mt-claves">
      <p><span>Costo real de las {n} obras</span><b class="mt-num">{real}</b> {chip_der}</p>
      <p><span>Pagado de más sobre lo aprobado</span><b class="mt-num">{brecha}</b> {chip_der}</p>
      <p><span>Ganancia o pérdida del año, donde se publica</span><b class="mt-num {sig}">{tot}</b> {chip_der}</p>
    </div>
    <div class="mt-pantalla">
      <p class="mt-vivo-et"><span class="mt-punto" aria-hidden="true"></span> Desde que abriste esta página, las {n_dat} obras con resultado publicado van:</p>
      <p class="mt-vivo-total">{vivo}</p>
      <p class="mt-vivo-sub">Verde si ganan, rojo si pierden. Es el resultado de un año proyectado sobre el tiempo que llevas mirando, no dinero que se mueva en este instante. <a href="{tabla}">Míralo obra por obra en la tabla general</a>.</p>
      {controles}
    </div>
  </section>
  <nav class="mt-indice" aria-labelledby="mtIndTit">
    <h2 class="mt-tit" id="mtIndTit">{n_cap} capítulos · cada uno abre su página</h2>
    <p class="mt-txt">Organizados por lo que quieres saber. Recórrelos en orden o entra directo al que te interese.</p>
    {bloques}
  </nav>
</div>'''.format(
        n=c['n'], real=c['real'], brecha=c['brecha'], chip_der=chip('derivado'), sig=_signo(tot), tot=mdp(tot),
        n_dat=len(todos), vivo=_vivo(tot, 'mt-grande-num'), tabla=ARCHIVO, controles=CONTROLES,
        n_cap=len(mo_capitulos.CAPITULOS), bloques='\n    '.join(bloques))
