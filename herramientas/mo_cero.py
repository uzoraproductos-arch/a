# -*- coding: utf-8 -*-
"""Inversion y Megaobras, modulo 4: «De cero al resultado» en pagina
propia (13-10-2026). Sustituye al marco que cargaba la portada entera
(index.html?ir=megaobras&ancla=eb-cero&visor=1).

Reproduce lo que pintaban renderSimuladorTablas() (las tres mesas de
calculo), renderSimuladorPorSector() (el inventario por sector) y
renderSimuladorProcedencia() del motor (audit-engine.js), con los mismos
datos de AUDIT_DB.simulador_megaobras. Desde el 21-10-2026 la mesa 2 usa
la medida unica de ganancia o perdida de la herramienta (mo_base.resultado)
y la pagina ya no tiene filtro de industria ni de mandato: el unico de la
herramienta esta en Sector e industria (pedido del autor).

Correcciones frente al motor (para anotarlas en CONTEXT.md al integrar):
- La mesa 3 ya no suma el sobrecosto acumulado (saldo de 1988 a 2024) y la
  perdida de un año (flujo) en un solo «acumulado» para dividirlo: el
  propio motor decia debajo que no se suman. Ahora son dos divisiones.
- El padron de contribuyentes es el del SAT con su documento
  (calculadora_civica.parametros.padron, 88,085,311 con RFC activo,
  abril de 2026), no el 88.1 redondeado del bloque macro, que no trae
  fuente.
- Los ingresos y costos de operacion se atribuyen a su documento (Cuenta
  Publica 2024, estados de actividades; Ramo 34), no «a los informes de
  la ASF».
- Cada cifra de obra lleva su chip (oficial, derivado o pendiente) y las
  sumas dicen cuanto de ellas descansa en cifras pendientes. Se puede ver
  la cuenta solo con lo documentado.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['cero']).
"""
import html
import json
import math

from presupuesto_modulos import chip
import mo_base
import mo_capitulos

ESTILOS = ['mo-cero.css']
SCRIPTS = ['mo-cero.js']

# Los mismos criterios de SIM_ORDENES; el primero es el de arranque.
ORDENES = [('perdida', 'Gana o pierde'), ('sobrecosto', 'Sobrecosto'), ('inversion', 'Costo real'),
           ('brecha', 'Pesos de más'), ('cronologia', 'Cronología')]

def esc(t):
    return html.escape(str(t if t is not None else ''), quote=True)


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def _rnd(x, d=0):
    """Redondeo como Math.round de JavaScript (mitades hacia arriba)."""
    f = 10 ** d
    return math.floor(x * f + 0.5) / f


def fnum(x):
    """Como Number.toLocaleString('es-MX'): miles con coma, hasta 3 decimales."""
    v = _rnd(x, 3)
    s = format(abs(v), ',.3f').rstrip('0').rstrip('.')
    return ('-' if v < 0 and s != '0' else '') + s


def smdp(n):
    """simMdp() del motor: unidades sin ambiguedad."""
    a = abs(n)
    if a >= 1e6:
        return '$' + format(n / 1e6, '.2f') + ' billones'
    if a >= 1000:
        return '$' + fnum(_rnd(n / 100) / 10) + ' mil millones'
    return '$' + fnum(_rnd(n * 100) / 100) + ' millones'


def pesos(v):
    return '$' + fnum(_rnd(v))


def obras(base):
    """Las obras con la sustitucion de megaobrasOficialBase()."""
    sm = base['simulador_megaobras']
    res = mo_base.resultados(sm)
    vf = sm.get('verificacion') or {}
    vfu = vf.get('fuentes') or {}
    cvf = (base.get('costo_vivo_megaobras') or {}).get('fuentes') or {}
    out = []
    for o in sm['obras']:
        ver = (vf.get('obras') or {}).get(o['id']) or {}
        x = {'id': o['id'], 'n': o['nombre'], 'ico': o['icono'], 's': o['sector_id'], 'p': o['presidente'],
             'per': o['periodo_sexenal'], 'presu': o['inversion_presupuestada_mdp'], 'real': o['inversion_real_mdp'],
             'sob': o['sobrecosto_pct'], 'ec': dict(o.get('estado_campos') or {}), 'resc': o.get('tipo') == 'rescate',
             'defs': ver.get('definiciones') or {}, 'clave': ver.get('clave') or '',
             'fu': [{'d': (vfu.get(k) or cvf.get(k))['doc'], 'u': (vfu.get(k) or cvf.get(k))['url']}
                    for k in ver.get('fuentes') or [] if (vfu.get(k) or cvf.get(k))]}
        # La medida unica de ganancia o perdida (mo_base.resultado,
        # 21-10-2026): res con signo (+ gana, - pierde) y perd = -res, la
        # perdida que suman la mesa 2 y la mesa 3; sin dato, cero.
        r = res[o['id']]
        if r['tipo'] == 'dato':
            f0 = r['f'][0] if r['f'] else {}
            x.update(res=r['v'], perd=-r['v'], pe=r['e'], anio=r['anio'], base=r['base'], opx=r['op'],
                     op={'d': f0.get('doc', ''), 'u': f0.get('url', '')})
        else:
            x.update(res=None, perd=0, pe=r['tipo'], por=r['txt'])
        out.append(x)
    return out


def _orden(lista, criterio):
    k = {'perdida': lambda o: (o['res'] is None, -o['perd']), 'sobrecosto': lambda o: -o['sob'], 'inversion': lambda o: -o['real'],
         'brecha': lambda o: -(o['real'] - o['presu']), 'cronologia': lambda o: o['per']}[criterio]
    return sorted(lista, key=k)  # sorted() es estable, como Array.sort de V8


def _suma(vals):
    """Suma de izquierda a derecha, como reduce() de JavaScript: desde
    Python 3.12, sum() compensa el error de redondeo y podria diferir en
    el ultimo digito de lo que calcula la pagina."""
    t = 0
    for v in vals:
        t += v
    return t


def ag(lista):
    real = _suma(o['real'] for o in lista)
    presu = _suma(o['presu'] for o in lista)
    anual = _suma(o['perd'] for o in lista)
    return {'n': len(lista), 'real': real, 'presu': presu, 'brecha': real - presu,
            'sob': (real / presu - 1) * 100 if presu > 0 else 0, 'anual': anual,
            'seg': anual * 1e6 / (365 * 86400)}


def _ch(o, campo):
    e = o['ec'].get(campo) or 'pendiente'
    return chip(e, ('obra-' + o['id']) if e == 'pendiente' else None)


def _nom(o, mesa):
    return ('<button type="button" class="mc-lupa" data-id="%s" data-mesa="%s" aria-label="De dónde sale cada cifra de %s">'
            '<span class="mc-ico" aria-hidden="true">%s</span><span class="mc-nom-tx">%s</span>'
            '<span class="mc-lupa-i" aria-hidden="true">🔎</span></button>' % (esc(o['id']), mesa, esc(o['n']), o['ico'], esc(o['n'])))


def _pend_doc(o):
    return o['ec'].get('inversion_presupuestada_mdp') == 'pendiente' or o['ec'].get('inversion_real_mdp') == 'pendiente'


def mesa1_filas(lista):
    acum = 0
    filas = []
    for i, o in enumerate(lista, 1):
        dif = o['real'] - o['presu']
        acum += dif
        dch = ' ' + chip('pendiente', 'obra-' + o['id']) if _pend_doc(o) else ''
        filas.append(
            '<tr class="mc-fila" data-i="%d" data-id="%s"><td class="mc-n" data-et="#">%d</td><td class="mc-nom">%s</td>'
            '<td class="mc-num" data-et="Aprobado (mdp)" data-k="presu">%s %s</td>'
            '<td class="mc-num" data-et="Erogado (mdp)" data-k="real">%s %s</td>'
            '<td class="mc-num mc-dif" data-et="Diferencia" data-k="dif">%s%s%s</td>'
            '<td class="mc-num mc-acum" data-et="Acumulado" data-k="acum">%s</td></tr>'
            % (i, esc(o['id']), i, _nom(o, 1), fnum(o['presu']), _ch(o, 'inversion_presupuestada_mdp'),
               fnum(o['real']), _ch(o, 'inversion_real_mdp'), '+' if dif > 0 else '', fnum(dif), dch, fnum(_rnd(acum))))
    return '\n'.join(filas)


def _celda_res(o):
    if o['pe'] == 'pendiente':
        return 'no lo publica ' + chip('pendiente', 'cuenta-' + o['id'])
    if o['pe'] == 'no_aplica':
        return 'no opera'
    return '<span class="%s">%s%s</span> %s' % ('mc-gana' if o['res'] > 0 else 'mc-pierde', '+' if o['res'] > 0 else '',
                                                 fnum(o['res']), chip(o['pe']))


def mesa2_filas(lista):
    acum = 0
    filas = []
    for i, o in enumerate(lista, 1):
        acum += o['res'] or 0
        filas.append(
            '<tr class="mc-fila%s" data-i="%d" data-id="%s"><td class="mc-n" data-et="#">%d</td><td class="mc-nom">%s</td>'
            '<td class="mc-num" data-et="Año del dato" data-k="anio">%s</td>'
            '<td class="mc-num mc-dif" data-et="Gana o pierde (mdp)" data-k="res">%s</td>'
            '<td class="mc-num mc-acum" data-et="Acumulado" data-k="acum">%s</td></tr>'
            % ('' if o['pe'] not in ('pendiente', 'no_aplica') else ' mc-nula', i, esc(o['id']), i, _nom(o, 2),
               o.get('anio') or '—', _celda_res(o), fnum(_rnd(acum * 10) / 10)))
    return '\n'.join(filas)


CADENA = [('Un año', 1, 'cifra base'), ('Un semestre', 2, '÷ 2 semestres'), ('Un trimestre', 4, '÷ 4 trimestres'),
          ('Un mes', 12, '÷ 12 meses'), ('Un día', 365, '÷ 365 días'), ('Un segundo', 31536000, '÷ 31,536,000 segundos')]


def cadena(anual):
    out = []
    for et, div, op in CADENA:
        v = anual / div
        txt = smdp(v) if v >= 1 else '$' + fnum(_rnd(v * 1e6)) + ' pesos'
        out.append('<li class="mc-cad-p"><span class="mc-cad-et">%s</span><span class="mc-cad-op">%s</span>'
                   '<span class="mc-cad-v">%s</span></li>' % (et, op, txt))
    return ''.join(out)


def mesa3_filas(a, pad):
    bc = a['brecha'] * 1e6 / pad
    pc = a['anual'] * 1e6 / pad
    return ('<tr class="mc-fila" data-i="1"><td class="mc-n" data-et="Paso">1</td><td class="mc-nom">Pesos pagados de más sobre lo aprobado <small>(saldo de 2000 a 2024)</small></td>'
            '<td class="mc-op" data-et="Operación">resultado de la mesa 1</td><td class="mc-num mc-acum" data-et="Resultado">%s</td></tr>\n'
            '<tr class="mc-fila mc-div" data-i="2"><td class="mc-n" data-et="Paso">2</td><td class="mc-nom">Entre cada contribuyente con RFC activo</td>'
            '<td class="mc-op" data-et="Operación">%s mdp × 1,000,000 ÷ %s</td><td class="mc-num mc-acum" data-et="Resultado">%s <small>por contribuyente</small></td></tr>\n'
            '<tr class="mc-fila" data-i="3"><td class="mc-n" data-et="Paso">3</td><td class="mc-nom">Pérdida neta de un año <small>(cada obra con su año más reciente publicado)</small></td>'
            '<td class="mc-op" data-et="Operación">resultado de la mesa 2</td><td class="mc-num mc-acum" data-et="Resultado">%s</td></tr>\n'
            '<tr class="mc-fila mc-div" data-i="4"><td class="mc-n" data-et="Paso">4</td><td class="mc-nom">Entre cada contribuyente con RFC activo</td>'
            '<td class="mc-op" data-et="Operación">%s mdp × 1,000,000 ÷ %s</td><td class="mc-num mc-acum" data-et="Resultado">%s <small>por contribuyente, cada año</small></td></tr>'
            % (smdp(a['brecha']), fnum(_rnd(a['brecha'] * 10) / 10), fnum(pad), pesos(bc),
               smdp(a['anual']), fnum(_rnd(a['anual'] * 10) / 10), fnum(pad), pesos(pc)))


def pendiente_en(lista):
    """Cuanto de la suma de la mesa 1 descansa en cifras pendientes."""
    p = [o for o in lista if _pend_doc(o)]
    return p, _suma(o['real'] - o['presu'] for o in p)


def mesa1_cierre(lista):
    a = ag(lista)
    p, dp = pendiente_en(lista)
    txt = ('Se aprobaron <strong>%s</strong> y se erogaron <strong>%s</strong>. La diferencia es de <strong>%s</strong>, '
           'un <strong>%s%s%%</strong> sobre lo autorizado %s.' % (smdp(a['presu']), smdp(a['real']), smdp(a['brecha']),
                                                                   '+' if a['sob'] > 0 else '', format(a['sob'], '.1f'), chip('derivado')))
    if p:
        txt += (' <span class="mc-ojo">Ojo: <strong>%s</strong> de esa diferencia salen de %d %s con alguna cifra pendiente (%s). '
                'Cuentan en el inventario, no como dato auditado.</span>'
                % (smdp(dp), len(p), 'obra' if len(p) == 1 else 'obras', esc(', '.join(o['n'].split(' (')[0] for o in p))))
    else:
        txt += ' <span class="mc-ojo mc-ojo-ok">Todas las cifras de esta cuenta tienen documento.</span>'
    return txt


def proc_verificadas(base):
    sm = base['simulador_megaobras']
    v = list(((sm.get('verificacion') or {}).get('obras') or {}).keys())
    nombres = [o['nombre'].split(' (')[0] if o['nombre'].endswith(')') else o['nombre'] for o in sm['obras'] if o['id'] in v]
    con = sum(1 for o in sm['obras'] if (o.get('estado_campos') or {}).get('inversion_real_mdp') not in (None, 'pendiente'))
    doc = sum(1 for x in obras(base) if x['res'] is not None)
    return ('De las %d obras, %d ya tienen documentos oficiales cotejados (%s) y %d tienen su costo anclado a un documento oficial '
            '(la cartera de Hacienda, la Cuenta Pública o un informe de la ASF). Cada cifra lleva su chip: oficial, derivado o pendiente. '
            '%d obras publican su ganancia o pérdida del año; en las demás, el resultado, los costos de operación y el costo unitario siguen pendientes o no aplican, y no se estiman.'
            % (len(sm['obras']), len(nombres), esc(', '.join(nombres)), con, doc))


def sector_tabla(base, ref, lista):
    sm = base['simulador_megaobras']
    tot = ag([o for o in lista if not o['resc']])
    grupos = []
    for s in sm['sectores']:
        if s['id'] == 'todos':
            continue
        ob = sorted([o for o in lista if o['s'] == s['id']], key=lambda o: -(o['real'] - o['presu']))
        if ob:
            grupos.append((s, ob, ag(ob)))
    # Los rescates van al final y fuera del total (decision del autor, 17-10-2026).
    grupos.sort(key=lambda g: (g[1][0]['resc'], -g[2]['real']))
    cuerpos = []
    for s, ob, a in grupos:
        aparte = ob[0]['resc']
        cuota = 0 if aparte else a['real'] / tot['real'] * 100
        filas = ['<tr class="mc-sec-cab"><td class="mc-sec-nom" colspan="2"><span class="mc-ico" aria-hidden="true">%s</span>'
                 '<span class="mc-sec-t">%s</span><span class="mc-sec-n">%d %s</span></td>'
                 '<td class="mc-num" data-et="Aprobado (mdp)">%s</td><td class="mc-num" data-et="Erogado (mdp)">%s</td>'
                 '<td class="mc-num mc-dif" data-et="Diferencia">+%s</td><td class="mc-num" data-et="Sobrecosto">+%s%%</td>'
                 '<td class="mc-num mc-cuota" data-et="%% del total"><span class="mc-barra" aria-hidden="true"><i style="width:%s%%"></i></span>%s</td></tr>'
                 % (s['icono'], esc(s['nombre']), len(ob), 'obra' if len(ob) == 1 else 'obras',
                    fnum(a['presu']), fnum(a['real']), fnum(a['brecha']), format(a['sob'], '.1f'),
                    format(cuota, '.1f'), 'aparte, fuera del total' if aparte else format(cuota, '.1f') + '%')]
        for o in ob:
            dif = o['real'] - o['presu']
            filas.append(
                '<tr class="mc-sec-obra" data-id="%s"><td class="mc-ico-c" aria-hidden="true">%s</td><td class="mc-nom">%s'
                '<span class="mc-meta">%s · %s</span></td>'
                '<td class="mc-num" data-et="Aprobado (mdp)">%s %s</td><td class="mc-num" data-et="Erogado (mdp)">%s %s</td>'
                '<td class="mc-num mc-dif" data-et="Diferencia">%s%s</td><td class="mc-num" data-et="Sobrecosto">%s%s%% %s</td>'
                '<td class="mc-num mc-cuota" data-et="%% del total">%s</td></tr>'
                % (esc(o['id']), o['ico'], _nom(o, 'inv').replace('<span class="mc-ico" aria-hidden="true">%s</span>' % o['ico'], ''),
                   esc(o['p']), esc(o['per']),
                   fnum(o['presu']), _ch(o, 'inversion_presupuestada_mdp'), fnum(o['real']), _ch(o, 'inversion_real_mdp'),
                   '+' if dif > 0 else '', fnum(dif), '+' if o['sob'] > 0 else '', fnum(o['sob']), _ch(o, 'sobrecosto_pct'),
                   '—' if o['resc'] else format(o['real'] / tot['real'] * 100, '.1f') + '%'))
        cuerpos.append('<tbody class="mc-sec-grupo">%s</tbody>' % ''.join(filas))
    return ('<table class="mc-t mc-t-sec"><caption class="sr-only">Las %d obras por sector, en millones de pesos</caption>'
            '<thead><tr><th colspan="2" scope="col">Sector y obra %s</th><th scope="col">Aprobado (mdp)</th><th scope="col">Erogado (mdp)</th>'
            '<th scope="col">Diferencia %s</th><th scope="col">Sobrecosto</th><th scope="col">%% del total %s</th></tr></thead>%s'
            '<tfoot><tr><td colspan="2" class="mc-nom">Total de las %d obras evaluadas, sin los rescates</td><td class="mc-num" data-et="Aprobado (mdp)">%s</td>'
            '<td class="mc-num" data-et="Erogado (mdp)">%s</td><td class="mc-num mc-dif" data-et="Diferencia">+%s</td>'
            '<td class="mc-num" data-et="Sobrecosto">+%s%%</td><td class="mc-num" data-et="%% del total">100%%</td></tr></tfoot></table>'
            % (len(lista), ref('ref-asf-cp'), chip('derivado'), chip('derivado'), ''.join(cuerpos), tot['n'], fnum(tot['presu']),
               fnum(tot['real']), fnum(tot['brecha']), format(tot['sob'], '.1f')))


def _sel(id_, et, opciones, val):
    return ('<label class="mc-campo" for="%s"><span>%s</span><select id="%s" class="mc-select">%s</select></label>'
            % (id_, et, id_, ''.join('<option value="%s"%s>%s</option>' % (esc(k), ' selected' if k == val else '', esc(n))
                                     for k, n in opciones)))


def construir(base, ref):
    sm = base['simulador_megaobras']
    lista = obras(base)
    vista = _orden(lista, ORDENES[0][0])
    # La mesa 1 (costo y sobrecosto) mide las obras; los rescates van aparte
    # salvo que se elija su industria. La mesa 2 (perdida de un año) si
    # suma el rescate bancario, como el contador del pulso.
    vista1 = [o for o in vista if not o['resc']]
    a = ag(vista)
    a1 = ag(vista1)
    a3 = dict(a, brecha=a1['brecha'])
    padron = base['calculadora_civica']['parametros']['padron']
    pad = padron['personas']

    datos = {'obras': lista, 'sectores': {s['id']: {'n': s['nombre'], 'ico': s['icono']} for s in sm['sectores']},
             'padron': {'n': pad, 'corte': padron['corte'], 'd': padron['fuente'], 'u': padron['url']},
             'pendObra': [o['id'] for o in lista if _pend_doc(o)]}

    # Un solo filtro en toda la herramienta (pedido del autor, 21-10-2026):
    # industria y presidente se eligen en «Obra por obra, por industria».
    # Aqui las mesas cuentan todas las obras; solo se elige el orden.
    filtros = _sel('mcOrden', 'Orden de los renglones', ORDENES, ORDENES[0][0])

    def ctrl(m):
        return ('<div class="mc-ctrl" role="group" aria-label="Recorre la mesa %s">'
                '<button type="button" class="mc-b mc-b-pri" data-acc="sig" data-mesa="%s"><span aria-hidden="true">▶</span> Siguiente renglón</button>'
                '<button type="button" class="mc-b" data-acc="auto" data-mesa="%s" aria-pressed="false"><span aria-hidden="true">⏯</span> Reproducir</button>'
                '<button type="button" class="mc-b" data-acc="cero" data-mesa="%s"><span aria-hidden="true">↺</span> Desde cero</button>'
                '<button type="button" class="mc-b" data-acc="todo" data-mesa="%s"><span aria-hidden="true">⏭</span> Toda la cuenta</button>'
                '<button type="button" class="mc-b mc-b-csv" data-csv="%s"><span aria-hidden="true">⬇</span> CSV</button></div>'
                '<div class="mc-marcador" aria-live="polite"><span class="mc-marc-et">Vas en</span><b class="mc-marc-v" id="mcMarc%s"></b>'
                '<span class="mc-marc-paso" id="mcPaso%s"></span><span class="mc-riel" aria-hidden="true"><i id="mcRiel%s"></i></span></div>'
                '<p class="mc-explica" id="mcExp%s" aria-live="polite"></p>' % ((m,) * 10))

    cero1 = ('<tr class="mc-cero" data-i="0"><td class="mc-n" data-et="#">0</td><td class="mc-nom">Punto de partida</td>'
             '<td class="mc-num" data-et="Aprobado (mdp)">0</td><td class="mc-num" data-et="Erogado (mdp)">0</td>'
             '<td class="mc-num" data-et="Diferencia">0</td><td class="mc-num mc-acum" data-et="Acumulado">0</td></tr>')
    cero2 = ('<tr class="mc-cero" data-i="0"><td class="mc-n" data-et="#">0</td><td class="mc-nom">Punto de partida</td>'
             '<td class="mc-num" data-et="Año del dato">—</td><td class="mc-num" data-et="Gana o pierde (mdp)">0</td>'
             '<td class="mc-num mc-acum" data-et="Acumulado">0</td></tr>')

    return '''<div class="mc" id="mcRaiz">
  <section class="mc-arranque" aria-labelledby="mcArrTit">
    <p class="mc-kicker">{kicker}</p>
    <h2 class="mc-grande" id="mcArrTit">Ninguna cifra se escribe a mano: síguela con el dedo, de cero al resultado.</h2>
    <p class="mc-txt">Tres mesas de cálculo arrancan en cero y avanzan renglón por renglón: cómo se acumuló el sobrecosto de <b>{n_obras} megaobras</b> (los {n_resc} rescates van aparte), cómo se arma la pérdida de un año y cuánto le toca a cada contribuyente. Pulsa cualquier obra para ver de qué documento sale cada número.</p>
    <div class="mc-cifras">
      <div class="mc-cifra"><span>Pesos de más sobre lo aprobado</span><b id="mcK1">{k1}</b>{d}</div>
      <div class="mc-cifra"><span>Pérdida neta de un año, donde se publica</span><b id="mcK2">{k2}</b>{d}</div>
      <div class="mc-cifra"><span>Obras que publican su ganancia o pérdida</span><b>{doc} de {n}</b>{o}</div>
    </div>
    <div class="mc-arr-acc">
      <button type="button" class="mc-b mc-b-luz" id="mcEmpezar"><span aria-hidden="true">▶</span> Empieza la cuenta desde cero</button>
    </div>
    <ol class="mc-indice" aria-label="Las partes de esta página">
      <li><a href="#mcMesa1"><span class="mc-num-c">1</span> De lo aprobado a lo erogado</a></li>
      <li><a href="#mcMesa2"><span class="mc-num-c">2</span> Gana o pierde en un año</a></li>
      <li><a href="#mcMesa3"><span class="mc-num-c">3</span> A tu bolsillo</a></li>
      <li><a href="#mcInventario"><span class="mc-num-c">🧾</span> Inventario por sector</a></li>
      <li><a href="#mcProcedencia"><span class="mc-num-c">📚</span> Cómo se calcula</a></li>
    </ol>
  </section>

  <section class="mc-filtros" aria-labelledby="mcFilTit">
    <h2 class="mc-tit" id="mcFilTit"><span aria-hidden="true">🎛️</span> Las obras que entran en la cuenta</h2>
    <p class="mc-txt">Las tres mesas cuentan las {n} obras: los rescates, solo en la mesa 2. Para ver una industria o un presidente, usa el filtro de <a href="herramienta-megaobras-sector.html">Obra por obra, por industria</a>: es el único de la herramienta.</p>
    <div class="mc-fil-campos">{filtros}</div>
  </section>

  <article class="mc-mesa" id="mcMesa1" data-mesa="1" aria-labelledby="mcM1Tit">
    <h2 class="mc-tit" id="mcM1Tit"><span class="mc-num-c">1</span> De lo aprobado a lo erogado</h2>
    <p class="mc-txt">Cada renglón suma su diferencia (erogado menos aprobado) a la columna acumulada. La última celda de esa columna es el sobrecosto del conjunto, en millones de pesos. Los rescates (FOBAPROA y FARAC) no entran en esta mesa: son deudas asumidas, no obras, y su crecimiento no se compara con un sobrecosto. Están en la mesa 2 y en el inventario de abajo.</p>
    {ctrl1}
    <div class="mc-marco"><table class="mc-t" id="mcT1"><caption class="sr-only">Mesa 1: de lo aprobado a lo erogado, en millones de pesos</caption>
      <thead><tr><th scope="col">#</th><th scope="col">Obra</th><th scope="col">Aprobado (mdp)</th><th scope="col">Erogado (mdp)</th><th scope="col">Diferencia {d}</th><th scope="col">Acumulado {d}</th></tr></thead>
      <tbody>{cero1}
{f1}</tbody>
      <tfoot id="mcPie1"><tr><td></td><td class="mc-nom">Total de las obras</td><td class="mc-num" data-et="Aprobado (mdp)">{presu}</td><td class="mc-num" data-et="Erogado (mdp)">{real}</td><td class="mc-num mc-dif" data-et="Diferencia">{sg}{brecha}</td><td class="mc-num mc-acum" data-et="Acumulado">{brecha}</td></tr></tfoot>
    </table></div>
    <p class="mc-cierre" id="mcCierre1">{c1}</p>
  </article>

  <article class="mc-mesa" id="mcMesa2" data-mesa="2" aria-labelledby="mcM2Tit">
    <h2 class="mc-tit" id="mcM2Tit"><span class="mc-num-c">2</span> Cuánto gana o pierde cada obra en un año</h2>
    <p class="mc-txt">Cada renglón suma lo que la obra gana (en verde, con signo más) o pierde (en rojo, con signo menos) en un año. El acumulado de abajo es la pérdida neta, la misma cifra de toda la herramienta. {medida}</p>
    {ctrl2}
    <div class="mc-marco"><table class="mc-t" id="mcT2"><caption class="sr-only">Mesa 2: la pérdida operativa de un año, en millones de pesos</caption>
      <thead><tr><th scope="col">#</th><th scope="col">Obra</th><th scope="col">Año del dato</th><th scope="col">Gana o pierde (mdp)</th><th scope="col">Acumulado {d}</th></tr></thead>
      <tbody>{cero2}
{f2}</tbody>
      <tfoot id="mcPie2"><tr><td></td><td class="mc-nom">Ganancia o pérdida neta del año</td><td></td><td class="mc-num mc-dif" data-et="Gana o pierde (mdp)">{neto}</td><td class="mc-num mc-acum" data-et="Acumulado">{neto}</td></tr></tfoot>
    </table></div>
    <h3 class="mc-sub">La misma pérdida neta, partida en el tiempo {d}</h3>
    <ol class="mc-cadena" id="mcCadena">{cad}</ol>
    <div class="mc-vivo" role="group" aria-label="Contador en vivo">
      <p class="mc-vivo-tx">Desde que abriste esta página, a ese ritmo (<b id="mcSeg">${seg}</b> por segundo), van:</p>
      <b class="mc-vivo-v" id="mcVivo" aria-live="off">$0</b>
      <button type="button" class="mc-b" id="mcVivoB" aria-pressed="false"><span aria-hidden="true">⏸</span> Pausar</button>
    </div>
    <p class="mc-cierre">No es un gasto que ocurra en este instante: es la pérdida neta de un año proyectada sobre el tiempo que llevas mirando. Pulsa cada obra para ver de qué documento sale su resultado.</p>
  </article>

  <article class="mc-mesa mc-mesa-puente" id="mcMesa3" data-mesa="3" aria-labelledby="mcM3Tit">
    <h2 class="mc-tit" id="mcM3Tit"><span class="mc-num-c">3</span> De la cifra agregada a tu bolsillo</h2>
    <p class="mc-txt">Un billón de pesos no se siente. Dividido entre quienes tienen obligaciones con el SAT, sí. Las dos magnitudes se dividen por separado: el sobrecosto es un saldo que se acumuló de 2000 a 2024 y la pérdida es un flujo de un año; sumarlas mezclaría tiempos distintos.</p>
    {ctrl3}
    <div class="mc-marco"><table class="mc-t mc-t-puente" id="mcT3"><caption class="sr-only">Mesa 3: de la cifra agregada a cada contribuyente</caption>
      <thead><tr><th scope="col">Paso</th><th scope="col">Concepto</th><th scope="col">Operación</th><th scope="col">Resultado {d}</th></tr></thead>
      <tbody><tr class="mc-cero" data-i="0"><td class="mc-n" data-et="Paso">0</td><td class="mc-nom">Punto de partida</td><td class="mc-op" data-et="Operación">—</td><td class="mc-num mc-acum" data-et="Resultado">$0</td></tr>
{f3}</tbody>
    </table></div>
    <p class="mc-padron">Divisor: <b>{padn}</b> contribuyentes con RFC activo, {corte} {ofi}. <a href="{padu}" target="_blank" rel="noopener noreferrer">{padd} ↗</a>. Es el número de inscritos con RFC activo, no el de quienes pagaron impuestos ese mes.</p>
    <div class="mc-bolsillo" id="mcBolsillo">{bolsillo}</div>
    <p class="mc-acc-sig"><a class="mc-b mc-b-pri mc-b-a" href="herramienta-calculadora-reloj.html"><span aria-hidden="true">⏱️</span> Ver estas dos magnitudes en el reloj de la Calculadora Cívica</a></p>
  </article>

  <section class="mc-inventario" id="mcInventario" aria-labelledby="mcInvTit">
    <h2 class="mc-tit" id="mcInvTit"><span aria-hidden="true">🧾</span> Todo el dinero, obra por obra y dividido por sector</h2>
    <p class="mc-txt">Las {n_obras} obras evaluadas y, al final y fuera del total, los {n_resc} rescates, sin recortar por ningún filtro. Pulsa una obra para ver de dónde sale cada cifra.</p>
    <p class="mc-unidades"><strong>Unidades.</strong> Las columnas están en <strong>millones de pesos</strong> (mdp). Mil millones son 1,000 mdp; un billón de pesos son 1,000,000 mdp. Las cifras son nominales del año de cada erogación, sin deflactar.</p>
    <div class="mc-ctrl"><button type="button" class="mc-b mc-b-csv" data-csv="inv"><span aria-hidden="true">⬇</span> Descarga el inventario (CSV)</button></div>
    <p class="mc-explica" id="mcExpinv" aria-live="polite"></p>
    <div class="mc-marco">{sector}</div>
    <p class="mc-aviso"><strong>De dónde salen estas cifras y qué falta.</strong> {verif} Mientras las demás no tengan documento, esta tabla se lee como inventario, no como dictamen. El universo son {n_obras} obras emblemáticas de 2000 a 2024 y {n_resc} rescates del sexenio de Ernesto Zedillo; no pretende ser el catálogo completo de la inversión pública del periodo.</p>
  </section>

  <section class="mc-proc" id="mcProcedencia" aria-labelledby="mcProcTit">
    <h2 class="mc-tit" id="mcProcTit"><span aria-hidden="true">📚</span> Cómo se calcula lo que ves</h2>
    <ul class="mc-proc-lista">
      <li><strong>Los agregados se suman, no se escriben.</strong> {nota}</li>
      <li><strong>Gana o pierde.</strong> {medida}</li>
      <li><strong>La pérdida por segundo.</strong> Se obtiene dividiendo la pérdida neta del año entre los 31,536,000 segundos de un año de 365 días. El contador en vivo no mide un gasto que ocurra en ese instante: proyecta el ritmo anual sobre el tiempo que llevas mirando.</li>
      <li><strong>El sobrecosto del conjunto.</strong> Compara la inversión real total contra la presupuestada total, de modo que cada obra pesa según su tamaño. No es el promedio simple de los porcentajes, que trataría igual a una refinería y a una estela.</li>
      <li><strong>Cifras con documento.</strong> {verif}</li>
      <li><strong>Pendiente declarado.</strong> Las cifras marcadas como pendientes no tienen todavía el documento oficial que las sustenta; se muestran como consolidación documental y no como dato auditado. Pulsa cualquier etiqueta {pend} para ver por qué falta, quién debe publicarlo y dónde debería estar, en el <a href="pendientes.html#tema-megaobras">Registro de pendientes</a>.</li>
    </ul>
  </section>
  <script type="application/json" id="mcDatos">{datos}</script>
</div>'''.format(
        kicker=mo_capitulos.kicker('herramienta-megaobras-cero.html'),
        n=len(lista), n_obras=len(vista1), n_resc=len(lista) - len(vista1), k1=smdp(a1['brecha']), k2=smdp(a['anual']), doc=sum(1 for o in lista if o['res'] is not None),
        d=chip('derivado'), o=chip('oficial'), filtros=filtros,
        ctrl1=ctrl(1), ctrl2=ctrl(2), ctrl3=ctrl(3), cero1=cero1, cero2=cero2,
        f1=mesa1_filas(vista1), f2=mesa2_filas(vista), f3=mesa3_filas(a3, pad),
        sg='+' if a1['brecha'] > 0 else '', presu=fnum(a1['presu']), real=fnum(a1['real']), brecha=fnum(a1['brecha']), c1=mesa1_cierre(vista1),
        neto=fnum(_rnd(-a['anual'] * 10) / 10), medida=mo_base.medida_txt(sm), cad=cadena(a['anual']), seg=format(_rnd(a['seg'], 2), ',.2f'),
        padn=fnum(pad), corte=esc(padron['corte']), ofi=chip(padron.get('estado', 'oficial')), padu=esc(padron['url']), padd=esc(padron['fuente']),
        bolsillo=bolsillo(a3, pad), sector=sector_tabla(base, ref, lista), verif=proc_verificadas(base),
        nota=('El costo, lo aprobado y el sobrecosto de conjunto suman las %d obras; los %d rescates (FOBAPROA y FARAC) van aparte, '
              'porque son deudas asumidas y no obras. La pérdida neta del año sí suma los rescates, porque se siguen pagando hoy.'
              % (len(vista1), len(lista) - len(vista1))), pend=chip('pendiente', 'reloj-megaobras'), datos=_json(datos))


def bolsillo(a, pad):
    return ('<div class="mc-bol"><span class="mc-bol-et">Sobrecosto histórico por contribuyente</span><b class="mc-bol-v">%s</b>'
            '<span class="mc-bol-sub">acumulado de 2000 a 2024 (inversión de capital en exceso) %s</span></div>'
            '<div class="mc-bol mc-bol-alto"><span class="mc-bol-et">Conciliación temporal de cuentas</span><b class="mc-bol-v">No se suman</b>'
            '<span class="mc-bol-sub">un sobrecosto de varias décadas no se suma a un flujo de un año</span></div>'
            '<div class="mc-bol"><span class="mc-bol-et">Pérdida neta anual por contribuyente</span><b class="mc-bol-v">%s</b>'
            '<span class="mc-bol-sub">cada año (el resultado publicado más reciente de cada obra) %s</span></div>'
            % (pesos(a['brecha'] * 1e6 / pad), chip('derivado'), pesos(a['anual'] * 1e6 / pad), chip('derivado')))
