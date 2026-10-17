# -*- coding: utf-8 -*-
"""Quinta aplicacion del Modo Inspector: «Contrasta una nota» en pagina
propia (12-10-2026). Sustituye al marco que cargaba la portada entera.

El lector pega la liga de una nota, elige de que cifra oficial habla y
escribe lo que la nota afirma. La pagina pone la cifra junto al documento,
con su chip, mide cuanto se aleja y explica por que podria no coincidir.

El catalogo de cifras contrastables se arma aqui desde la base con las
mismas reglas que vnCatalogo() del motor (audit-engine.js): mismas
colecciones, mismos identificadores, mismos estados. Los municipios no se
embeben: el padron EFIPEM ya vive aparte (assets/auditor/js/
municipios-efipem.js) y el JS lo carga al vuelo solo si el lector busca un
municipio.

Regla de la plataforma (AGENTS.md, §2): nada se estima. Si la cifra de
referencia esta pendiente, el contraste no se hace.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['inspnota']).
"""
import html
import json
import math

from presupuesto_modulos import chip, mdp

ESTILOS = ['insp-nota.css']
SCRIPTS = ['insp-nota.js']

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


def construir(base, ref):
    cat = catalogo(base)
    ejs = ejemplos(cat)
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

    ej_html = '\n'.join(
        '<button type="button" class="in-ej" data-ej="%d"><span class="in-ej-tipo">%s</span><span class="in-ej-fr">%s</span></button>'
        % (k, esc(e['tipo']), esc(e['frase'])) for k, e in enumerate(ejs))

    unidades = ''.join('<option value="%s"%s>%s</option>' % (u, ' selected' if u == 'millones' else '', et) for u, et in UNIDADES)

    datos = {'cat': cat, 'ejemplos': ejs, 'grupos': {g: nom for g, _, nom in GRUPOS},
             'estados': {e['abbr']: e['name'] for e in base.get('estados') or []}}

    return '''<div class="in" id="inRaiz">
  <section class="in-arranque" aria-labelledby="inArrTit">
    <p class="in-kicker">Busca y verifica · aplicación 5</p>
    <h2 class="in-grande" id="inArrTit">¿Esa cifra de la noticia es cierta? Ponla junto al documento.</h2>
    <p class="in-txt">Tienes <b>{total} cifras oficiales</b> con su documento, más los ingresos de cada municipio del INEGI. Eliges de cuál habla la nota, escribes lo que afirma y te decimos si coincide, cuánto se aleja y qué revisar antes de concluir.</p>
    <ol class="in-indice" aria-label="Los tres pasos">
      <li><a href="#inPaso1"><span class="in-n">1</span> La nota</a></li>
      <li><a href="#inPaso2"><span class="in-n">2</span> La cifra oficial</a></li>
      <li><a href="#inPaso3"><span class="in-n">3</span> Lo que dice la nota</a></li>
    </ol>
  </section>

  <section class="in-ejemplos" aria-labelledby="inEjTit">
    <h2 class="in-tit" id="inEjTit"><span aria-hidden="true">🧪</span> Pruébala sin escribir</h2>
    <p class="in-txt">Frases de prueba, <b>no son notas reales</b>: cada una lleva a un veredicto distinto para que veas cómo se lee el resultado.</p>
    <div class="in-ejs">
{ejs}
    </div>
  </section>

  <section class="in-paso" id="inPaso1" aria-labelledby="inP1Tit">
    <h2 class="in-tit" id="inP1Tit"><span class="in-n">1</span> La nota <small>(opcional)</small></h2>
    <label class="in-campo" for="inUrl"><span>Pega la liga: sirve para que el contraste diga de dónde salió la afirmación. No la abrimos ni la leemos.</span>
      <input type="url" id="inUrl" class="in-input" placeholder="https://…" autocomplete="off" inputmode="url"></label>
    <p class="in-url-ok" id="inUrlOk" aria-live="polite"></p>
  </section>

  <section class="in-paso" id="inPaso2" aria-labelledby="inP2Tit">
    <h2 class="in-tit" id="inP2Tit"><span class="in-n">2</span> ¿De qué cifra oficial habla?</h2>
    <label class="in-campo" for="inBuscar"><span>Busca el concepto, el estado, el municipio o la dependencia</span>
      <input type="search" id="inBuscar" class="in-input" placeholder="Ej.: intereses deuda, Jalisco deuda, Tren Maya, Monterrey" autocomplete="off"></label>
    <div class="in-filtros" role="group" aria-label="Categorías">
      {filtros}
    </div>
    <p class="in-cuenta" id="inCuenta" aria-live="polite"></p>
    <div class="in-catalogo" id="inCatalogo">
{grupos}
    </div>
    <div class="in-elegida" id="inElegida" aria-live="polite" hidden></div>
  </section>

  <section class="in-paso" id="inPaso3" aria-labelledby="inP3Tit">
    <h2 class="in-tit" id="inP3Tit"><span class="in-n">3</span> Lo que dice la nota</h2>
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

  <section class="in-revisa" aria-labelledby="inRevTit">
    <h2 class="in-tit" id="inRevTit"><span aria-hidden="true">🔍</span> Antes de concluir, revisa</h2>
    <ul class="in-tips">
      <li data-tip="anio"><b>El año.</b> Una cifra de 2025 no es la de 2026. El catálogo dice el año de cada cifra; la nota a veces no.</li>
      <li data-tip="etapa"><b>Aprobado, modificado o ejercido.</b> El presupuesto aprobado es lo que se planea; el ejercido, lo que se gastó. Pueden diferir bastante. <a href="numeros-gasto-tres-presupuestos.html">Los tres presupuestos</a>.</li>
      <li data-tip="real"><b>Nominal o real.</b> Si la nota habla «a precios de» otro año, ajustó por inflación y no tiene por qué coincidir con el documento, que da pesos corrientes.</li>
      <li data-tip="unidad"><b>La unidad.</b> mdp son millones de pesos; mmdp, miles de millones. En español un billón es un millón de millones; el «billion» del inglés son mil millones. <a href="numeros-cuanto-dinero-es.html">¿Cuánto dinero es?</a></li>
      <li data-tip="signo"><b>El signo.</b> Los balances y el déficit se publican en negativo. Aquí los comparamos en valor absoluto y te avisamos.</li>
      <li data-tip="concepto"><b>El concepto.</b> Total o una parte, bruto o neto, la empresa entera o solo un proyecto: un nombre parecido puede medir otra cosa. <a href="numeros-lo-que-la-cifra-no-dice.html">Lo que la cifra no dice</a>.</li>
    </ul>
  </section>

  <aside class="in-aviso">
    <p><b>Lo que esta herramienta no hace:</b> no abre ni lee la nota —un sitio sin servidor no puede hacerlo—, así que compara la cifra que tú copiaste, no la que la nota dice. Tampoco califica al medio: dice si una cifra coincide con un documento oficial, y por qué podría no coincidir.</p>
    <p>Las cifras salen de los documentos de la SHCP {r_pef} {r_lif} {r_cgpe}, la ASF, la Cuenta Pública y el INEGI; cada una lleva su enlace. Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>. Lo que todavía nos deben las dependencias está en el <a href="pendientes.html">Registro de pendientes</a>.</p>
    <p class="in-hermanas">Sigue verificando: <a href="herramienta-inspector-asf.html">🏛️ Qué encontró la ASF</a> · <a href="numeros-las-32-entidades.html">🗺️ Las 32 entidades</a> · <a href="numeros-los-municipios.html">🏘️ Los municipios</a> · <a href="fuentes-oficiales.html">📚 Fuentes oficiales</a></p>
  </aside>
  <script type="application/json" id="inDatos">{datos}</script>
</div>'''.format(total=format(len(cat), ','), ejs=ej_html, filtros='\n      '.join(filtros), grupos='\n'.join(grupos),
                 unidades=unidades, datos=_json(datos),
                 r_pef=ref('ref-pef2026'), r_lif=ref('ref-lif2026'), r_cgpe=ref('ref-cgpe2027'))
