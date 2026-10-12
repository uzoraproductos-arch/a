# -*- coding: utf-8 -*-
"""Tercera aplicacion de la Calculadora Civica: «El reloj de la deuda y de
lo perdido» en pagina propia (12-10-2026). Sustituye al marco que cargaba
la portada entera (index.html?ir=calculadora&ancla=eb-ccreloj).

Reproduce ccPintarReloj() del motor (audit-engine.js) con los mismos
parametros: cada reloj toma su cifra anual de calculadora_civica.relojes,
la divide entre los 31,536,000 segundos de un ano de 365 dias y la reparte
entre los habitantes (CONAPO) o los inscritos en el SAT, en la cadencia
que el lector elija. Las cifras de arranque (al dia, por habitante) se
escriben aqui; el JS (cc-reloj.js) solo las recalcula con los datos que
van embebidos en #crDatos y mueve los contadores.

Correccion frente al motor: el reloj de la ASF traia 46,122.0 mdp como
«suma de los montos observados a las 32 entidades», pero esa suma, hecha
hoy con los montos por aclarar de la Matriz de Datos Basicos de la Cuenta
Publica 2024 que guarda la base (estados[].asfMontoObservado), da otra
cifra. Aqui se suma al vuelo, con su operacion dicha.

Regla de la plataforma (AGENTS.md, §2): nada se estima. La perdida de las
megaobras sigue con su chip pendiente y su ficha del Registro
(reloj-megaobras); el lector puede sacarla de la cuenta.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['ccreloj']).
"""
import html
import json
from decimal import Decimal, ROUND_HALF_UP

from presupuesto_modulos import chip

ESTILOS = ['cc-reloj.css']
SCRIPTS = ['cc-reloj.js']

SEG_ANO = 31536000  # 365 dias, la misma base que el motor (CC_SEG_ANO)


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def esc(t):
    return html.escape(str(t or ''), quote=True)


def _r(v, d=0):
    """Redondeo como Math.round del motor (mitades hacia arriba)."""
    q = Decimal(1).scaleb(-d)
    return float(Decimal(repr(v)).quantize(q, rounding=ROUND_HALF_UP))


def pesos(v):
    return '$' + format(int(_r(v)), ',')


def pesos_finos(v):
    """ccPesosFinos(): dos decimales por debajo de mil pesos."""
    return '$' + format(_r(v, 2), ',.2f') if abs(v) < 1000 else pesos(v)


def sim_mdp(n):
    """simMdp() del motor."""
    a = abs(n)
    if a >= 1e6:
        return '$%.2f billones' % (n / 1e6)
    if a >= 1e3:
        x = _r(n / 100) / 10
        return '$' + (format(x, ',.1f') if x != int(x) else format(int(x), ',')) + ' mil millones'
    x = _r(n, 2)
    return '$' + (format(x, ',.2f').rstrip('0').rstrip('.') if x != int(x) else format(int(x), ',')) + ' millones'


def megaobras(base):
    """Replica de megaobrasOficialBase() del motor: en el auditor el reloj
    de las megaobras deja de ser la suma sin documento (pendiente) y pasa a
    ser lo documentado: el deficit antes de transferencias de las empresas
    con estado de actividades oficial mas el Ramo 34 ejercido para el IPAB.
    Las obras sin documento no entran, no se suponen cero en el texto y
    conservan su ficha del Registro (reloj-megaobras)."""
    sm = base.get('simulador_megaobras') or {}
    of = sm.get('operacion_oficial') or {}
    ob = of.get('obras') or {}
    if not ob:
        return None
    nombres = {o['id']: o['nombre'] for o in sm.get('obras') or []}
    total = len(sm.get('obras') or [])
    vfu = ((sm.get('verificacion') or {}).get('fuentes') or {})
    empresas, partes, urls = 0.0, [], []
    ramo34 = 0.0
    for oid, d in ob.items():
        if oid == 'fobaproa':
            ramo34 = d.get('ramo34_ejercido') or 0
            continue
        res = d.get('resultado_sin_transferencias')
        perd = -res if isinstance(res, (int, float)) and res < 0 else 0
        empresas += perd
        partes.append('%s %s' % (nombres.get(oid, oid), ('$' + format(perd, ',.1f') + ' mdp') if perd else 'sin déficit'))
        f = (of.get('fuentes') or {}).get(d.get('fuente')) or {}
        if f.get('url'):
            urls.append(f['url'])
    anual = round(empresas + ramo34, 1)
    doc = len(ob)
    cp = vfu.get('cp') or {}
    return {
        'nombre': 'Pérdida anual documentada de las megaobras y apoyo del Ramo 34',
        'anual': anual, 'estado': 'derivado',
        'fuente': ('Estados de actividades de 2024 en la Cuenta Pública (Tomo VII) y Ramo 34 ejercido en 2024 (Cuenta Pública 2024). '
                   'Cubre %d de las %d obras.' % (doc, total)),
        'url': cp.get('url') or (urls[0] if urls else ''),
        'op': ('Déficit antes de transferencias de las empresas con estado de actividades oficial (%s; suma $%s mdp) '
               'más el Ramo 34 ejercido para el rescate bancario del IPAB ($%s mdp).'
               % ('; '.join(partes), format(empresas, ',.1f'), format(ramo34, ',.1f'))),
        'que': ('Lo que cuesta cada año mantener andando obras que ingresan menos de lo que gastan, más lo que el presupuesto '
                'sigue pagando por el rescate bancario. No es el sobrecosto de construirlas: es el déficit de tenerlas abiertas.'),
        'pend': 'reloj-megaobras',
        'motivo': ('Las otras %d obras no entran en este reloj: no hay un estado de actividades oficial de su operación, '
                   'y las dependencias que las operan (Sedena, Pemex, Fonatur) no han transparentado obra por obra su costo '
                   'de operación ni sus ingresos. No se suponen en cero: siguen pendientes.' % (total - doc)),
    }


def relojes(base):
    cc = base['calculadora_civica']
    refs = {r['id']: r for r in base.get('referencias_legales', [])}
    asf_src = ((base.get('cuenta_publica_asf') or {}).get('fuentes') or {}).get('MDB2024') or {}
    estados = base.get('estados') or []
    out = []
    for f in cc['relojes']['fuentes']:
        o = {'id': f['id'], 'nombre': f['nombre'], 'icono': f['icono'], 'anual': f['anual_mdp'],
             'estado': f['estado'], 'fuente': f['fuente'], 'que': f['que'], 'culpa': bool(f.get('culpa'))}
        if f.get('refKey') and refs.get(f['refKey']):
            o['url'] = refs[f['refKey']].get('url', '')
            o['ref'] = f['refKey']
        if f['estado'] == 'pendiente':
            o['pend'] = 'reloj-' + f['id']
            o['motivo'] = f.get('motivo', '')
            o['url'] = f.get('url', '')
        if f['id'] == 'megaobras':
            o.update(megaobras(base) or {})
        if f['id'] == 'asf':
            con = [e for e in estados if isinstance(e.get('asfMontoObservado'), (int, float))]
            suma = round(sum(e['asfMontoObservado'] for e in con), 1)
            fu = con[0].get('asfFuente') if con else ''
            o.update({
                'nombre': 'Monto por aclarar ante la ASF en las 32 entidades',
                'anual': suma, 'estado': 'derivado',
                'fuente': 'Suma de lo que quedó por aclarar en cada una de las %d entidades. %s' % (len(con), fu),
                'url': asf_src.get('url', ''),
                'op': 'Suma de los %d montos por aclarar, entidad por entidad, de la Cuenta Pública 2024.' % len(con),
                'que': 'Lo que la Auditoría Superior de la Federación no pudo dar por justificado en el gasto federal '
                       'que recibieron las entidades en la Cuenta Pública 2024. Por aclarar no es lo mismo que perdido: '
                       'parte se aclara y parte se recupera.'})
        out.append(o)
    return out


def construir(base, ref):
    cc = base['calculadora_civica']
    par = cc['parametros']
    pob, pad, sm, uma = par['poblacion'], par['padron'], par['salario_minimo'], par['uma']
    cads = cc['cadencias']
    rel = relojes(base)
    sim = base.get('simulador_megaobras') or {}
    smT = sim.get('totales_consolidados')
    sob = dict(cc['relojes']['sobrecosto_acumulado'])
    if smT:
        sob['mdp'] = _r((smT['inversion_total_mdp'] - smT['inversion_presupuestada_total_mdp']) * 10) / 10
    n_obras = len(sim.get('obras') or [])
    nombres = {o['id']: o['nombre'] for o in sim.get('obras') or []}
    obras_pend = [(oid, nombres.get(oid, oid)) for oid, o in ((sim.get('verificacion') or {}).get('obras') or {}).items()
                  if any(v == 'pendiente' and k in ('inversion_presupuestada_mdp', 'inversion_real_mdp')
                         for k, v in (o.get('campos') or {}).items())]

    # Arranque: al dia y por habitante, como el motor.
    den = pob['millones'] * 1e6
    cad = cads[0]
    tot_anual = sum(r['anual'] for r in rel) * 1e6
    tot_seg = tot_anual / SEG_ANO
    tot_pers = tot_anual / den
    en_cad = [r['anual'] * 1e6 / den * cad['dias'] / 365 for r in rel]
    mayor = max(en_cad) or 1

    def boton(grupo, valor, texto, activo, ico=''):
        return ('<button type="button" class="cr-seg-b" data-%s="%s" aria-pressed="%s">%s%s</button>'
                % (grupo, valor, 'true' if activo else 'false',
                   ('<span aria-hidden="true">%s</span> ' % ico) if ico else '', texto))

    cad_html = '\n        '.join(boton('cad', c['id'], c['nombre'], k == 0, c.get('icono', '')) for k, c in enumerate(cads))
    den_html = '\n        '.join([
        boton('den', 'habitante', 'Entre los %s millones de habitantes' % pob['millones'], True, '👥'),
        boton('den', 'padron', 'Entre los %s millones inscritos en el SAT' % pad['millones'], False, '🧾')])

    tarjetas = []
    for r, v in zip(rel, en_cad):
        fuente = ('<a href="%s" target="_blank" rel="noopener">%s ↗</a>' % (esc(r['url']), esc(r['fuente']))
                  if r.get('url') else esc(r['fuente']))
        if r.get('ref'):
            fuente += ' ' + ref(r['ref'])
        extra = ''
        if r.get('op'):
            extra += '<p class="cr-op"><b>Operación:</b> %s</p>' % esc(r['op'])
        if r.get('motivo'):
            extra += ('<p class="cr-motivo"><b>Lo que falta:</b> %s %s '
                      '<a href="pendientes.html#%s">Ver su ficha en el Registro de pendientes</a>.</p>' % (esc(r['motivo']), chip('pendiente', r['pend']), esc(r['pend'])))
        tarjetas.append(
            '<li class="cr-card%s" data-id="%s">\n'
            '  <div class="cr-card-cab"><span class="cr-card-ico" aria-hidden="true">%s</span>'
            '<h3 class="cr-card-nom">%s</h3>%s</div>\n'
            '  <p class="cr-card-vivo"><span>Mientras lees, en todo el país</span> <b class="cr-num" data-vivo="%s">+$0.00</b></p>\n'
            '  <p class="cr-card-cif"><b class="cr-num" data-cad="%s">%s</b> <span class="cr-card-rot" data-rot>%s, por habitante</span></p>\n'
            '  <span class="cr-riel" aria-hidden="true"><span class="cr-barra" data-barra="%s" style="width:%.1f%%"></span></span>\n'
            '  <p class="cr-card-ano"><span data-anual="%s">%s</span> al año <span data-rotden>por habitante</span> · %s en todo el país</p>\n'
            '  <p class="cr-card-que">%s</p>\n%s'
            '  <p class="cr-card-fte"><b>Fuente:</b> %s</p>\n'
            '  <label class="cr-quita"><input type="checkbox" data-incluye="%s" checked> Contarla en el total</label>\n'
            '</li>'
            % (' cr-culpa' if r['culpa'] else '', esc(r['id']), r['icono'], esc(r['nombre']),
               chip(r['estado'], r.get('pend') if r['estado'] == 'pendiente' else None), esc(r['id']),
               esc(r['id']), pesos_finos(v), cad['nombre'].lower(),
               esc(r['id']), v / mayor * 100,
               esc(r['id']), pesos(r['anual'] * 1e6 / den), sim_mdp(r['anual']),
               esc(r['que']), extra, fuente, esc(r['id'])))

    pend = [r for r in rel if r['estado'] == 'pendiente']
    pend_tx = ''
    if pend:
        pend_tx = (' Una de las cuatro, <b>%s</b>, está %s: la puedes sacar de la cuenta.'
                   % (esc(pend[0]['nombre'].lower()), chip('pendiente', pend[0]['pend'])))

    obras_pend_html = ''
    if obras_pend:
        obras_pend_html = ('<p class="cr-txt">Ojo: %d de las %d obras tienen pendiente su presupuesto original o su costo total, '
                           'y la suma usa lo que la base registra para ellas: %s.</p>'
                           % (len(obras_pend), n_obras,
                              ', '.join('%s %s' % (esc(n), chip('pendiente', 'obra-' + oid)) for oid, n in obras_pend)))

    datos = {
        'relojes': [{k: r[k] for k in ('id', 'nombre', 'anual', 'estado')} for r in rel],
        'cadencias': [{k: c[k] for k in ('id', 'nombre', 'dias')} for c in cads],
        'den': {'habitante': {'millones': pob['millones'], 'rot': 'por habitante'},
                'padron': {'millones': pad['millones'], 'rot': 'por contribuyente'}},
        'segAno': SEG_ANO, 'sobrecosto': sob['mdp'], 'smDia': sm['general'], 'umaDia': uma['diaria'],
        'anioRitmo': 2026,
    }

    nota = cc['relojes']['nota'].replace('en que usted lo mira', 'en que lo miras').replace(
        'el tiempo que usted lleva', 'el tiempo que llevas')

    return '''<div class="cr" id="crRaiz">
  <section class="cr-arranque" aria-labelledby="crTit">
    <p class="cr-kicker">Calculadora Cívica · aplicación 3</p>
    <h2 class="cr-grande" id="crTit">⏱️ El reloj de la deuda y de lo perdido</h2>
    <p class="cr-lead">Cuatro cuentas que no aparecen en ningún recibo y que, sin embargo, alguien paga: lo que el país pide prestado este año, lo que cuestan los intereses de lo ya prestado, lo que pierden al año las megaobras que ingresan menos de lo que gastan y lo que la Auditoría Superior dejó por aclarar.</p>
    <div class="cr-pantalla" role="group" aria-labelledby="crVivoEt">
      <p class="cr-vivo-et" id="crVivoEt">Desde que abriste esta página, el país lleva</p>
      <p class="cr-vivo-num"><b class="cr-num" id="crVivoTotal">+$0.00</b></p>
      <p class="cr-vivo-sub">en <b id="crTiempo">0 s</b> · <b id="crPorSeg">{por_seg}</b> por segundo · tu parte: <b class="cr-num" id="crVivoTuyo">+$0.00</b></p>
      <div class="cr-ctl">
        <button type="button" class="cr-boton" id="crPausa" aria-pressed="false"><span aria-hidden="true">⏸️</span> <span>Pausa</span></button>
        <button type="button" class="cr-boton cr-sec" id="crCero"><span aria-hidden="true">🔄</span> Volver a cero</button>
      </div>
      <p class="cr-quieto" id="crQuieto" aria-live="polite"></p>
    </div>
    <ul class="cr-indice" aria-label="En esta página">
      <li><a href="#crMandos">🎛️ Ajusta el reloj</a></li>
      <li><a href="#crRelojes">⏱️ Los cuatro relojes</a></li>
      <li><a href="#crPerdido">💸 Lo que se fue</a></li>
      <li><a href="#crTuyo">🙋 Junto a lo tuyo</a></li>
      <li><a href="#crComo">🔍 Cómo se calcula</a></li>
    </ul>
  </section>

  <section class="cr-panel" id="crMandos" aria-labelledby="crMandTit">
    <h2 class="cr-tit" id="crMandTit"><span aria-hidden="true">🎛️</span> Ajusta el reloj</h2>
    <div class="cr-mandos">
      <div class="cr-campo"><span class="cr-campo-et" id="crCadEt">¿Cada cuándo?</span>
        <div class="cr-seg" role="group" aria-labelledby="crCadEt">
        {cad_html}
        </div></div>
      <div class="cr-campo"><span class="cr-campo-et" id="crDenEt">¿Repartido entre quiénes?</span>
        <div class="cr-seg" role="group" aria-labelledby="crDenEt">
        {den_html}
        </div></div>
    </div>
    <p class="cr-txt cr-den-nota" id="crDenNota">Entre habitantes cuenta a todos, de recién nacidos a personas mayores. Entre inscritos en el SAT cuenta solo a quienes tienen RFC activo: tocan a más cada uno.</p>
  </section>

  <section class="cr-panel" id="crRelojes" aria-labelledby="crRelTit">
    <h2 class="cr-tit" id="crRelTit"><span aria-hidden="true">⏱️</span> {titulo}</h2>
    <p class="cr-txt">Cada tarjeta dice cuánto te toca <span data-cadtx>al día</span> <span data-rotden>por habitante</span>, cuánto al año y cuánto en todo el país, con su documento y su chip. Con la casilla de cada tarjeta decides cuáles cuentan en el total.{pend_tx}</p>
    <ul class="cr-relojes">
{tarjetas}
    </ul>
    <div class="cr-total">
      <span class="cr-total-k">Las <span id="crCuantas">cuatro</span> juntas, <span data-cadtx>al día</span> y <span data-rotden>por habitante</span> {chip_der}</span>
      <b class="cr-total-v cr-num" id="crTotCad">{tot_cad}</b>
      <span class="cr-total-s"><span id="crTotAno">{tot_ano}</span> al año <span data-rotden>por habitante</span> · <span id="crTotPais">{tot_pais}</span> en todo el país</span>
      <span class="cr-total-op">Operación: suma de las tarjetas que cuentas en el total.</span>
    </div>
  </section>

  <section class="cr-panel" id="crPerdido" aria-labelledby="crPerTit">
    <h2 class="cr-tit" id="crPerTit"><span aria-hidden="true">💸</span> Lo que se fue mientras lees</h2>
    <p class="cr-txt">Lo que el reloj lleva desde que abriste la página, puesto en medidas que se entienden. Todo es {chip_der}: el acumulado entre el salario mínimo o la UMA del día, que sí son oficiales.</p>
    <ul class="cr-equiv">
      <li><span class="cr-eq-ico" aria-hidden="true">👷</span><span><b class="cr-num" id="crEqSm">0</b> jornadas de salario mínimo: lo que ganan en un día ese número de personas con el mínimo general de ${sm_dia} diarios {chip_sm}.</span></li>
      <li><span class="cr-eq-ico" aria-hidden="true">📏</span><span><b class="cr-num" id="crEqUma">0</b> veces la UMA diaria de ${uma_dia} {chip_uma}, la medida de multas y cuotas.</span></li>
      <li><span class="cr-eq-ico" aria-hidden="true">🙋</span><span>Tu parte al año, <b id="crEqTuAno">{tot_ano}</b>, equivale a <b id="crEqTuSm">{tu_sm}</b> días de salario mínimo.</span></li>
      <li><span class="cr-eq-ico" aria-hidden="true">🗓️</span><span>En lo que va de {anio}, al ritmo anual de estas cifras: <b class="cr-num" id="crEqAnio">$0</b> en todo el país. <small>Operación: cifra anual × segundos transcurridos del año ÷ {seg_ano} segundos.</small></span></li>
    </ul>
  </section>

  <section class="cr-panel" id="crTuyo" aria-labelledby="crTuyoTit">
    <h2 class="cr-tit" id="crTuyoTit"><span aria-hidden="true">🙋</span> Puesto junto a lo tuyo</h2>
    <p class="cr-txt">Escribe lo que recibes al mes, ya con descuentos, y te decimos a cuántos días de tu ingreso equivale tu parte de estas cuentas. Si no lo sabes, sácalo en <a href="herramienta-calculadora-ticket.html">🧾 Tu estado de cuenta</a>: ahí también sale el ISR que pagas al año. No guardamos ni enviamos nada.</p>
    <div class="cr-form">
      <label class="cr-campo" for="crNeto"><span class="cr-campo-et">Tu ingreso neto al mes</span>
        <input type="text" id="crNeto" class="cr-input" inputmode="decimal" placeholder="Ej.: 12,000" autocomplete="off"></label>
      <label class="cr-campo" for="crIsr"><span class="cr-campo-et">El ISR que pagas al año (opcional)</span>
        <input type="text" id="crIsr" class="cr-input" inputmode="decimal" placeholder="Ej.: 9,500" autocomplete="off"></label>
    </div>
    <p class="cr-personal" id="crPersonal" aria-live="polite">Cuando escribas tu ingreso, esta línea dirá a cuántos días de lo que ganas equivale tu parte.</p>
  </section>

  <section class="cr-panel cr-sobre" aria-labelledby="crSobTit">
    <h2 class="cr-tit" id="crSobTit"><span aria-hidden="true">🧱</span> Y aparte, lo ya gastado de más</h2>
    <p class="cr-txt">Construir las {n_obras} obras costó <b>{sob_mdp}</b> más de lo presupuestado, o <b id="crSobPers">{sob_pers}</b> <span data-rotden>por habitante</span>. {sob_nota} {chip_sob}</p>
    <p class="cr-txt cr-op"><b>Operación:</b> inversión real menos inversión presupuestada de las {n_obras} obras del <a href="herramienta-megaobras.html">simulador de megaobras</a>, repartida entre las personas que elijas arriba.</p>
    {obras_pend}
  </section>

  <aside class="cr-huachicol" role="note">
    <span class="cr-eq-ico" aria-hidden="true">⛽</span>
    <div><p><b>Lo que no entra también te cuesta.</b> Estos relojes miden lo que sale. El huachicol fiscal es lo que <b>no entra</b>: combustible vendido sin pagar el IEPS que tú sí pagas en cada litro. Ese faltante se cubre con más deuda o con menos gasto, pero ninguna autoridad ha publicado cuánto es, así que no se suma a ningún reloj.</p>
    <a class="cr-boton cr-sec" href="auditoria-huachicol-fiscal.html"><span aria-hidden="true">⛽</span> Huachicol fiscal: lo que se sabe ›</a></div>
  </aside>

  <section class="cr-panel" id="crComo" aria-labelledby="crComoTit">
    <h2 class="cr-tit" id="crComoTit"><span aria-hidden="true">🔍</span> Cómo se calcula</h2>
    <ul class="cr-proc">
      <li><b>Los relojes.</b> Cada uno toma una cifra anual de su documento y la divide entre los {seg_ano} segundos de un año de 365 días. <b>No miden un gasto que ocurra en el instante en que miras</b>: proyectan un ritmo anual sobre el tiempo que llevas en esta página. {chip_der}</li>
      <li><b>Por persona.</b> La cifra anual del país entre los habitantes o entre los inscritos en el SAT; la cadencia la toma en proporción a sus días (un mes son 30.4167 días; un trimestre, 91.25; un semestre, 182.5). {chip_der}</li>
      <li><b>Los habitantes.</b> {pob_m} millones. {pob_f}. {pob_c} {chip_pob} <a href="{pob_u}" target="_blank" rel="noopener">Ver el archivo original ↗</a></li>
      <li><b>El padrón de contribuyentes.</b> {pad_m} millones. {pad_f}. {pad_c} {chip_pad} <a href="{pad_u}" target="_blank" rel="noopener">Ver el archivo original ↗</a></li>
      <li><b>El salario mínimo y la UMA.</b> ${sm_dia} diarios: {sm_f}. ${uma_dia} diarios: {uma_f}. {chip_sm}</li>
    </ul>
    <p class="cr-txt">{nota}</p>
    <p class="cr-txt">Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>. Lo que todavía deben las dependencias está en el <a href="pendientes.html">Registro de pendientes</a>.</p>
  </section>

  <aside class="cr-hermanas">
    <p>Sigue la cuenta: <a href="herramienta-calculadora-ticket.html">🧾 Tu estado de cuenta</a> · <a href="herramienta-calculadora-compara.html">⚡ Tú contra ellos</a> · <a href="simulador-presupuesto.html">🧮 Reparte el presupuesto</a> · <a href="auditoria-deuda-soberana.html">📉 Los intereses de la deuda</a> · <a href="numeros-la-deuda.html">🏦 La deuda</a> · <a href="radar-reloj.html">⏱️ El reloj de cada administración</a></p>
  </aside>
  <script type="application/json" id="crDatos">{datos}</script>
</div>'''.format(
        por_seg=pesos_finos(tot_seg), cad_html=cad_html, den_html=den_html, titulo=esc(cc['relojes']['titulo']),
        pend_tx=pend_tx, tarjetas='\n'.join(tarjetas), chip_der=chip('derivado'),
        tot_cad=pesos_finos(sum(en_cad)), tot_ano=pesos(tot_pers), tot_pais=sim_mdp(tot_anual / 1e6),
        sm_dia=format(sm['general'], ',.2f'), chip_sm=chip(sm['estado']), uma_dia=format(uma['diaria'], ',.2f'),
        chip_uma=chip(uma['estado']), tu_sm=format(_r(tot_pers / sm['general'], 1), ',.1f'), anio=2026,
        seg_ano=format(SEG_ANO, ','), n_obras=n_obras, sob_mdp=sim_mdp(sob['mdp']),
        sob_pers=pesos(sob['mdp'] * 1e6 / den), sob_nota=esc(sob['nota']), chip_sob=chip(sob['estado']),
        obras_pend=obras_pend_html,
        pob_m=pob['millones'], pob_f=esc(pob['fuente']), pob_c=esc(pob['como']), chip_pob=chip(pob['estado']), pob_u=esc(pob['url']),
        pad_m=pad['millones'], pad_f=esc(pad['fuente']), pad_c=esc(pad['como']), chip_pad=chip(pad['estado']), pad_u=esc(pad['url']),
        sm_f=esc(sm['fuente']), uma_f=esc(uma['fuente']), nota=esc(nota), datos=_json(datos))
