# -*- coding: utf-8 -*-
"""Inversion y Megaobras, aplicacion 3: «Las obras de cada sexenio» en
pagina propia (13-10-2026). Sustituye al marco que cargaba la portada
entera (index.html?ir=megaobras&ancla=eb-sexenios&visor=1).

Lo que hacia el motor (renderSimuladorSexenioLinea, simSexEvaluar y
simSexReiniciar de audit-engine.js) se conserva entero: las seis torres de
1988 a 2024, el numero de obras y el costo de cada periodo, el boton que
las levanta desde cero y el que las regresa a ceros, el filtro por
industria y la nota del FARAC (13 obras, 14 en el reparto por mandato).
Se agrega: cada sexenio con su ficha y su ancla (#sexenio-<id>), las obras
de cada uno con sus tres cifras y su chip, la medida por costo ademas de
por numero de obras, y la comparacion de dos sexenios (#comparar-<a>-<b>).

Las obras salen de simulador_megaobras con el mismo criterio de
simObrasDe(): el nombre del presidente contiene la clave del sexenio.

Correccion editorial frente al motor: el costo de cada periodo es una
suma (derivado) y, cuando alguna de las obras sumadas tiene su costo
pendiente, la suma tambien lo esta. El motor la mostraba sin chip; aqui
se separa la parte con documento (derivado) de la parte sin documento
(pendiente, con su ficha en el Registro).

Lo llama apartados.insp_nativa() (INSP_NATIVAS['sexenios']).
"""
import html
import json

from presupuesto_modulos import chip

ESTILOS = ['mo-sexenios.css']
SCRIPTS = ['mo-sexenios.js']

# Mismas claves, nombres, anios y colores que SIM_SEXENIOS del motor.
SEXENIOS = [
    ('salinas', 'Salinas', 'Carlos Salinas', 'Carlos Salinas de Gortari', 1988, 1994, '#8e6cb0'),
    ('zedillo', 'Zedillo', 'Ernesto Zedillo', 'Ernesto Zedillo Ponce de León', 1994, 2000, '#4a90d9'),
    ('fox', 'Fox', 'Vicente Fox', 'Vicente Fox Quesada', 2000, 2006, '#3fa373'),
    ('calderon', 'Calderón', 'Felipe Calderón', 'Felipe Calderón Hinojosa', 2006, 2012, '#c9a227'),
    ('pena-nieto', 'Peña Nieto', 'Enrique Peña', 'Enrique Peña Nieto', 2012, 2018, '#d98032'),
    ('lopez-obrador', 'López Obrador', 'López Obrador', 'Andrés Manuel López Obrador', 2018, 2024, '#c0504d'),
]

CAMPOS = [('inversion_presupuestada_mdp', 'Presupuesto original'),
          ('inversion_real_mdp', 'Costo registrado'),
          ('sobrecosto_pct', 'Sobrecosto')]


def esc(t):
    return html.escape(str(t if t is not None else ''), quote=True)


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def _num(v, maxdec=3):
    """toLocaleString('es-MX') del motor: comas de miles, hasta 3 decimales."""
    s = format(round(v, maxdec), ',.%df' % maxdec)
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s


def sim_mdp(n):
    """Replica de simMdp() del motor."""
    a = abs(n)
    if a >= 1000000:
        return '$' + format(n / 1000000, '.2f') + ' billones'
    if a >= 1000:
        return '$' + _num(round(n / 100) / 10) + ' mil millones'
    return '$' + _num(round(n * 100) / 100) + ' millones'


def mdp1(v):
    return '$' + format(v, ',.1f') + ' mdp'


def corto_sector(nombre):
    return nombre.split(',')[0].split(' y ')[0]


def obras_de(obras, clave):
    """simObrasDe('todos', clave)."""
    k = clave.lower()
    return [o for o in obras if k in o['presidente'].lower()]


def _estado(o, campo):
    return (o.get('estado_campos') or {}).get(campo) or 'pendiente'


def _fuentes(base, o):
    sim = base['simulador_megaobras']
    ver = (sim.get('verificacion') or {})
    fu = dict((base.get('costo_vivo_megaobras') or {}).get('fuentes') or {})
    fu.update((sim.get('operacion_oficial') or {}).get('fuentes') or {})
    fu.update(ver.get('fuentes') or {})
    v = (ver.get('obras') or {}).get(o['id']) or {}
    out = []
    for k in v.get('fuentes') or []:
        f = fu.get(k)
        if f and f.get('url'):
            out.append((f.get('doc') or k, f['url']))
    return out, v


def _cifra(o, campo, v):
    e = _estado(o, campo)
    val = o.get(campo)
    if campo == 'sobrecosto_pct':
        txt = format(val, '.1f') + ' %' if isinstance(val, (int, float)) else '—'
    else:
        txt = mdp1(val) if isinstance(val, (int, float)) else '—'
    pend = ('obra-' + o['id']) if e == 'pendiente' else None
    defs = (v.get('definiciones') or {})
    d = defs.get(campo) or ''
    return e, txt, pend, d


def _ficha_obra(base, o, sectores, sx_clave, compartida):
    fuentes, v = _fuentes(base, o)
    sec = sectores.get(o['sector_id'], {})
    filas = []
    for campo, et in CAMPOS:
        e, txt, pend, d = _cifra(o, campo, v)
        filas.append('<div class="mx-c"><dt>%s</dt><dd><b>%s</b> %s</dd>%s</div>'
                     % (et, esc(txt), chip(e, pend),
                        ('<dd class="mx-c-def">%s</dd>' % esc(d)) if d else ''))
    otro = ''
    if compartida:
        otros = [s[2] for s in SEXENIOS if s[1] != sx_clave and s[1].lower() in o['presidente'].lower()]
        otro = ('<p class="mx-dos"><span aria-hidden="true">↔️</span> Esta obra también aparece en el sexenio de <b>%s</b>: '
                'el registro la consigna como «%s». Su costo se cuenta una sola vez en el total de las 13 obras.</p>'
                % (esc(' y '.join(otros)), esc(o['presidente'])))
    fu_html = ''
    if fuentes:
        fu_html = ('<p class="mx-fu-t">Documentos cotejados</p><ul class="mx-fu">%s</ul>'
                   % ''.join('<li><a href="%s" target="_blank" rel="noopener">%s ↗</a></li>' % (esc(u), esc(d)) for d, u in fuentes))
    hall = o.get('hallazgo_asf') or ''
    return ('<li class="mx-obra" data-sector="%s" data-obra="%s">'
            '<div class="mx-obra-cab"><span class="mx-obra-ico" aria-hidden="true">%s</span>'
            '<div><h4 class="mx-obra-n">%s</h4><p class="mx-obra-m">%s %s · %s · %s</p></div></div>'
            '%s<dl class="mx-cifras">%s</dl>'
            '<details class="mx-mas"><summary>Lo que encontró la ASF y de dónde sale cada cifra</summary>'
            '<p class="mx-hall">%s</p>%s'
            '<p class="mx-ir"><a href="herramienta-megaobras-sector.html">🏭 Ver la ficha completa en «Sector e industria» ➔</a></p>'
            '</details></li>'
            % (esc(o['sector_id']), esc(o['id']), esc(o.get('icono')), esc(o['nombre']),
               esc(sec.get('icono', '')), esc(corto_sector(sec.get('nombre', o['sector_id']))),
               esc(o.get('periodo_sexenal')), esc(o.get('estatus')),
               otro, ''.join(filas), esc(hall), fu_html))


def _resumen(obras):
    """Totales de un conjunto de obras. Todo es suma: derivado."""
    real = sum(o['inversion_real_mdp'] for o in obras)
    doc = [o for o in obras if _estado(o, 'inversion_real_mdp') != 'pendiente']
    pen = [o for o in obras if _estado(o, 'inversion_real_mdp') == 'pendiente']
    return {'n': len(obras), 'real': real,
            'doc': sum(o['inversion_real_mdp'] for o in doc), 'ndoc': len(doc),
            'pen': sum(o['inversion_real_mdp'] for o in pen), 'npen': len(pen),
            'pend': ['obra-' + o['id'] for o in pen]}


def res_html(r, nombres):
    """Resumen de un sexenio. mo-sexenios.js lo reescribe igual (resHtml)
    cuando el lector filtra por industria."""
    if r['n'] == 0:
        return '<p class="mx-r-vacio">Sin obras de esta industria en este periodo.</p>'
    total_e = 'pendiente' if r['npen'] else 'derivado'
    h = ('<div class="mx-r"><div><span>Obras</span><b>%d</b></div>'
         '<div><span>Costo registrado %s</span><b>%s</b><small>Suma del costo registrado de %d %s.</small></div>'
         % (r['n'], chip(total_e, r['pend'][0] if r['npen'] else None), sim_mdp(r['real']), r['n'],
            'obra' if r['n'] == 1 else 'obras'))
    if r['ndoc']:
        h += ('<div><span>Con documento %s</span><b>%s</b><small>Suma de %d %s con costo oficial o derivado.</small></div>'
              % (chip('derivado'), sim_mdp(r['doc']), r['ndoc'], 'obra' if r['ndoc'] == 1 else 'obras'))
    else:
        h += '<div><span>Con documento</span><b>—</b><small>Ninguna obra de este periodo tiene su costo total en un documento oficial.</small></div>'
    if r['npen']:
        h += ('<div class="mx-r-pen"><span>Sin documento %s</span><b>%s</b><small>%s: su costo total no tiene documento oficial todavía. '
              'Toca la etiqueta para ver por qué falta y a quién le toca publicarlo.</small></div>'
              % (chip('pendiente', r['pend'][0]), sim_mdp(r['pen']),
                 esc(', '.join(nombres.get(p[5:], p) for p in r['pend']))))
    return h + '</div>'


def construir(base, ref):
    sim = base['simulador_megaobras']
    obras = sim['obras']
    sectores = {s['id']: s for s in sim['sectores'] if s['id'] != 'todos'}
    total_n = len(obras)
    reparto = [(s, obras_de(obras, s[1])) for s in SEXENIOS]
    suma_reparto = sum(len(x) for _, x in reparto)
    tope = max(len(x) for _, x in reparto) or 1
    tope_real = max(sum(o['inversion_real_mdp'] for o in x) for _, x in reparto) or 1
    compartidas = [o for o in obras if '/' in o['presidente']]
    nombres = {o['id']: o['nombre'] for o in obras}

    # Torres de la linea del tiempo (sector «todas»; el JS las recalcula
    # con el mismo criterio si el lector filtra por industria).
    torres = []
    for (k, clave, nom, nom_l, ini, fin, color), xs in reparto:
        r = _resumen(xs)
        n = r['n']
        torres.append(
            '<li class="mx-t-li"><button type="button" class="mx-torre%s" data-sx="%s" aria-pressed="false" %s'
            'aria-label="%s, %d a %d: %d %s">'
            '<span class="mx-t-n" data-n="%d">%d</span>'
            '<span class="mx-t-riel"><span class="mx-t-barra" style="--mx-c:%s;--mx-h:%.4f;--mx-hc:%.4f"></span></span>'
            '<span class="mx-t-nom">%s</span><span class="mx-t-an">%d–%d</span>'
            '<span class="mx-t-cif" data-real="%s">%s</span></button></li>'
            % (' mx-vacia' if n == 0 else '', k, 'disabled ' if n == 0 else '', esc(nom_l), ini, fin, n,
               'obra' if n == 1 else 'obras', n, n, color, n / tope, r['real'] / tope_real,
               esc(nom), ini, fin, r['real'], 'sin obras aquí' if n == 0 else sim_mdp(r['real'])))

    filtros = ['<button type="button" class="mx-filtro" data-sec="todos" aria-pressed="true">🌐 Todas las industrias</button>']
    for sid, s in sectores.items():
        filtros.append('<button type="button" class="mx-filtro" data-sec="%s" aria-pressed="false"><span aria-hidden="true">%s</span> %s</button>'
                       % (esc(sid), esc(s.get('icono')), esc(corto_sector(s['nombre']))))

    # Ficha de cada sexenio (y la de todo el periodo).
    paneles = []
    for (k, clave, nom, nom_l, ini, fin, color), xs in reparto:
        r = _resumen(xs)
        fichas = ''.join(_ficha_obra(base, o, sectores, clave, '/' in o['presidente']) for o in
                         sorted(xs, key=lambda o: -o['inversion_real_mdp']))
        paneles.append(
            '<article class="mx-panel" id="sexenio-%s" data-sx="%s" style="--mx-c:%s" hidden tabindex="-1" aria-labelledby="mxPT-%s">'
            '<header class="mx-p-cab"><p class="mx-p-an">%d–%d</p><h3 class="mx-p-tit" id="mxPT-%s">%s</h3></header>'
            '<div class="mx-p-res" data-res="%s">%s</div>'
            '<ol class="mx-obras">%s</ol>'
            '<p class="mx-p-vacio" hidden>Ninguna obra de esta industria cae en este sexenio. Elige «Todas las industrias» para verlas todas.</p>'
            '</article>'
            % (k, k, color, k, ini, fin, k, esc(nom_l), k, res_html(r, nombres), fichas))

    opts = ''.join('<option value="%s">%s (%d–%d)</option>' % (k, esc(nom_l), ini, fin)
                   for k, clave, nom, nom_l, ini, fin, color in SEXENIOS)

    datos = {
        'sx': [{'k': k, 'clave': clave, 'nom': nom, 'noml': nom_l, 'ini': ini, 'fin': fin, 'color': color}
               for k, clave, nom, nom_l, ini, fin, color in SEXENIOS],
        'obras': [{'id': o['id'], 'n': o['nombre'], 'i': o.get('icono', ''), 'sec': o['sector_id'], 'pres': o['presidente'],
                   'real': o['inversion_real_mdp'], 'e': _estado(o, 'inversion_real_mdp')} for o in obras],
        'sec': {sid: corto_sector(s['nombre']) for sid, s in sectores.items()},
    }

    farac = compartidas[0] if compartidas else None
    nota_farac = ''
    if farac:
        nota_farac = '''
  <details class="mx-nota" id="mxNota">
    <summary><span aria-hidden="true">📖</span> Por qué a veces verás {n} obras y a veces {s}</summary>
    <p class="mx-txt"><b>No es un error de suma: es una obra que pertenece a dos sexenios a la vez.</b> El universo de este módulo son <b>{n} megaobras</b>: {n} proyectos, {n} presupuestos, {n} costos. Cuando sumes dinero, siempre estarás sumando {n} veces. Pero al repartir las obras por mandato, las seis columnas suman <b>{s}</b> (suma de las seis columnas {chip_d}).</p>
    <p class="mx-txt"><b>El caso FARAC.</b> Las concesiones carreteras se otorgaron durante el gobierno de <b>Carlos Salinas de Gortari</b>, y el rescate que las devolvió al Estado se ejecutó durante el de <b>Ernesto Zedillo</b>. El expediente no pertenece a un sexenio: <em>atraviesa</em> dos. Por eso el registro lo consigna literalmente como «{pres}», y al repartir las obras por mandato aparece en ambos.</p>
    <p class="mx-txt"><b>Por qué lo dejamos así y no lo «arreglamos».</b> Había tres caminos, y ninguno es neutral:</p>
    <ol class="mx-ol">
      <li><b>Asignarlo solo a Salinas</b>, por ser quien concesionó. Borraría que el costo se reconoció y se pagó en el sexenio siguiente.</li>
      <li><b>Asignarlo solo a Zedillo</b>, por ser quien rescató. Borraría el diseño que hizo necesario el rescate.</li>
      <li><b>Contarlo en los dos</b>, y decirlo en voz alta. Es lo que hicimos.</li>
    </ol>
    <p class="mx-txt">Elegimos el tercero porque los dos primeros <em>esconden</em> la mitad de la historia para que un número quede redondo. Preferimos una cifra que necesita explicación a una cifra cómoda que miente por omisión.</p>
    <p class="mx-regla"><b>La regla, en una línea:</b> el <b>dinero</b> se cuenta una sola vez, sobre las <b>{n}</b> obras; la <b>responsabilidad política</b> se cuenta donde ocurrió, y por eso en el reparto por mandato el FARAC aparece <b>dos veces</b>. Al comparar el costo de Salinas con el de Zedillo, recuerda que el del FARAC está en los dos.</p>
  </details>'''.format(n=total_n, s=suma_reparto, pres=esc(farac['presidente']), chip_d=chip('derivado'))

    return '''<div class="mx" id="mxRaiz">
  <section class="mx-arranque" aria-labelledby="mxArrTit">
    <p class="mx-kicker">Inversión y Megaobras · aplicación 3</p>
    <h2 class="mx-grande" id="mxArrTit">Treinta y seis años de obra pública en una sola línea</h2>
    <p class="mx-txt">De 1988 a 2024, seis presidentes y <b>{n} megaobras</b> con su presupuesto, su costo y lo que la ASF encontró. Toca un sexenio para ver sus obras, mide la línea por número de obras o por costo, y pon dos sexenios frente a frente.</p>
    <ol class="mx-indice" aria-label="Lo que hay en esta página">
      <li><a href="#mxLinea"><span aria-hidden="true">🕰️</span> La línea del tiempo</a></li>
      <li><a href="#mxFicha"><span aria-hidden="true">🏛️</span> Las obras de cada sexenio</a></li>
      <li><a href="#mxComparar"><span aria-hidden="true">⚖️</span> Compara dos sexenios</a></li>
    </ol>
  </section>

  <section class="mx-bloque" id="mxLinea" aria-labelledby="mxLinTit">
    <h2 class="mx-tit" id="mxLinTit"><span aria-hidden="true">🕰️</span> La línea del tiempo, de 1988 a 2024</h2>
    <p class="mx-txt">La altura de cada bloque es el número de obras evaluadas en ese periodo, o su costo registrado si cambias la medida. Todos arrancan en cero: pulsa «Evaluar» para verlos levantarse a su escala real.</p>
    <div class="mx-filtros" role="group" aria-label="Industria">
      {filtros}
    </div>
    <div class="mx-controles">
      <div class="mx-medida" role="group" aria-label="Qué mide la altura">
        <button type="button" class="mx-med" data-med="n" aria-pressed="true">🔢 Por número de obras</button>
        <button type="button" class="mx-med" data-med="real" aria-pressed="false">💰 Por costo registrado</button>
      </div>
      <div class="mx-acc">
        <button type="button" class="mx-boton" id="mxEvaluar"><span aria-hidden="true">▶️</span> Evaluar los seis sexenios</button>
        <button type="button" class="mx-boton mx-sec" id="mxReiniciar"><span aria-hidden="true">↺</span> Reiniciar a ceros</button>
      </div>
    </div>
    <p class="mx-estado" id="mxEstado" aria-live="polite">⚪ Periodos en reposo (0 obras / $0). Pulsa «Evaluar» para levantarlos desde cero.</p>
    <ol class="mx-linea" id="mxTorres" aria-label="Los seis sexenios">
      {torres}
    </ol>
    <div class="mx-eje" aria-hidden="true"><span>1988</span><span class="mx-eje-riel"></span><span>2024</span></div>
    <p class="mx-pie-cif">Costo de cada periodo: suma del costo registrado de sus obras {chip_d}, en pesos de cada año, sin quitar la inflación. Cuando alguna obra tiene su costo pendiente, la ficha del sexenio te dice qué parte tiene documento y cuál no.</p>
    <p class="mx-ciego"><b>Punto ciego declarado.</b> El rescate carretero FARAC se contrató bajo Salinas y se asumió como deuda pública bajo Zedillo, así que aparece en ambos bloques. Por eso la suma de los seis periodos da {s} obras y no {n}: una misma obra tiene dos responsables, no medio responsable cada uno. <a href="#mxNota">Lee la nota de método</a>.</p>
  </section>

  <section class="mx-bloque" id="mxFicha" aria-labelledby="mxFiTit">
    <h2 class="mx-tit" id="mxFiTit"><span aria-hidden="true">🏛️</span> Las obras de cada sexenio</h2>
    <div class="mx-chips" role="group" aria-label="Elige un sexenio">
      <a class="mx-chip" href="#sexenio-todos" data-sx="todos">🕰️ Todo el periodo</a>
      {chips}
    </div>
    <article class="mx-panel" id="sexenio-todos" data-sx="todos" hidden tabindex="-1" aria-labelledby="mxPT-todos">
      <header class="mx-p-cab"><p class="mx-p-an">1988–2024</p><h3 class="mx-p-tit" id="mxPT-todos">Todo el periodo</h3></header>
      <div class="mx-p-res" data-res="todos">{res_todos}</div>
      <p class="mx-txt">Toca un sexenio en la línea del tiempo o en los botones de arriba para ver sus obras, una por una, con su presupuesto, su costo, su sobrecosto y los documentos de donde salen.</p>
    </article>
    {paneles}
  </section>

  <section class="mx-bloque" id="mxComparar" aria-labelledby="mxCoTit">
    <h2 class="mx-tit" id="mxCoTit"><span aria-hidden="true">⚖️</span> Compara dos sexenios</h2>
    <p class="mx-txt">Elige dos administraciones y ponlas frente a frente: cuántas obras, cuánto cuestan y qué parte de ese costo tiene documento. Respeta la industria que elegiste arriba.</p>
    <div class="mx-co-sel">
      <label class="mx-campo" for="mxCoA"><span>Primer sexenio</span><select id="mxCoA" class="mx-input">{opts}</select></label>
      <button type="button" class="mx-boton mx-sec mx-inv" id="mxCoInv" aria-label="Intercambiar los dos sexenios">⇄</button>
      <label class="mx-campo" for="mxCoB"><span>Segundo sexenio</span><select id="mxCoB" class="mx-input">{opts}</select></label>
    </div>
    <div class="mx-co" id="mxCoSalida" aria-live="polite"></div>
    <p class="mx-acciones"><button type="button" class="mx-boton mx-sec" id="mxCoCopiar"><span aria-hidden="true">🔗</span> Copiar el enlace de esta comparación</button> <span class="mx-copiado" id="mxCopiado" aria-live="polite"></span></p>
  </section>
{nota}
  <aside class="mx-aviso">
    <p><b>Cómo leer el costo.</b> El costo de las obras es una suma de pesos de años distintos, entre 1988 y 2024, que no están deflactados a un año común. Sirve para dimensionar el orden de magnitud, no para afirmar una equivalencia exacta de poder adquisitivo: un peso de 1997 no compra lo mismo que uno de 2026, y preferimos decirlo a ocultarlo.</p>
    <p><b>De dónde sale cada cifra.</b> Del registro de megaobras de la plataforma, cotejado contra la cartera de inversión de Hacienda, la Cuenta Pública, el PEF y los informes de la Auditoría Superior de la Federación; cada obra lleva sus documentos. Lo que todavía nos deben las dependencias está en el <a href="pendientes.html">Registro de pendientes</a>. Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>.</p>
    <p>🎯 ¿Y cómo le fue a cada presidente en economía, deuda y fiscalización? La trivia, con el estado de cuenta de cada uno, está en <a href="aprende.html#trivia">Aprende › El examen de los presidentes</a>.</p>
    <p class="mx-hermanas">Sigue en Megaobras: <a href="herramienta-megaobras-pulso.html">📡 El pulso</a> · <a href="herramienta-megaobras-sector.html">🏭 Sector e industria</a> · <a href="herramienta-megaobras-cero.html">🧮 De cero al resultado</a></p>
  </aside>
  <script type="application/json" id="mxDatos">{datos}</script>
</div>'''.format(
        n=total_n, s=suma_reparto, filtros='\n      '.join(filtros), torres='\n      '.join(torres),
        chips='\n      '.join('<a class="mx-chip" href="#sexenio-%s" data-sx="%s" style="--mx-c:%s">%s</a>' % (k, k, c, esc(nom))
                               for k, _, nom, _, _, _, c in SEXENIOS),
        paneles='\n    '.join(paneles), res_todos=res_html(_resumen(obras), nombres), opts=opts, nota=nota_farac, chip_d=chip('derivado'), datos=_json(datos))
