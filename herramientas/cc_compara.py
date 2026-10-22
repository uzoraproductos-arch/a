# -*- coding: utf-8 -*-
"""Segunda aplicacion de la Calculadora Civica: «Tu contra ellos» en pagina
propia (12-10-2026). Sustituye al marco que cargaba la portada entera
(index.html?ir=calculadora&ancla=eb-cccompara&visor=1).

Lo mismo que pintaba renderComparadorSalarial() del motor (audit-engine.js),
con las mismas cifras de window.AUDIT_DB.comparador_salarial (Anexo 23 del
PEF 2026 y los manuales de remuneraciones del Senado, la Camara de
Diputados y el PJF, DOF 27-02-2026): las tarjetas de cada cargo, el filtro
por Poder, los congresos locales uno por uno, el cuadro de prestaciones y
la comparativa para copiar. Las cifras oficiales se escriben aqui, en el
HTML; el JS (cc-compara.js) solo hace las cuentas con el ingreso del lector
(«veces», «dias», «meses») y las marca derivadas.

Diferencia de fondo con el motor: alla, si el lector no habia sacado la
cuenta en el bloque 1, se comparaba su bruto contra el neto de ellos (con
aviso). Aqui la pagina calcula su neto con las mismas reglas del bloque 1
para quien esta en nomina (tarifa del art. 96 de la LISR, subsidio para el
empleo y cuotas obreras del IMSS, de calculadora_civica), y lo dice. Asi se
compara siempre neto contra neto.

Regla de la plataforma (AGENTS.md, §2): nada se estima. Los chips
«pendiente» llevan data-pend a su ficha del Registro (pendientes.py arma
esas fichas con los mismos identificadores).

Lo llama apartados.insp_nativa() (INSP_NATIVAS['cccompara']).
"""
import html
import json
import re

from presupuesto_modulos import chip

ESTILOS = ['cc-compara.css']
SCRIPTS = ['cc-compara.js']

# El motor compartia textos con la Enciclopedia (usted); al lector del
# auditor se le habla de tu (AGENTS.md, §6). Solo cambian rotulos, no datos.
TU = [('Usted (mínimo de ley)', 'Tú (mínimo de ley)'),
      ('Lo paga usted: se le retiene de la parte gravada', 'Lo pagas tú: te lo retienen de la parte gravada')]

# Marcas ✓/✗ del cuadro de prestaciones: solo donde el propio texto de la
# celda lo dice sin ambiguedad («la ley no lo exige», «lo paga la Camara»).
# Donde el documento no registra algo, no se marca: no registrar no es
# probar que no exista.
MARCAS = {
    ('Seguro de vida', 'lft'): 'no', ('Seguro de vida', 'dip'): 'si', ('Seguro de vida', 'sen'): 'si',
    ('Seguro de vida', 'pr'): 'si', ('Seguro de vida', 'pjf'): 'si',
    ('Impuesto del aguinaldo', 'lft'): 'no', ('Impuesto del aguinaldo', 'dip'): 'si',
}


def esc(t):
    return html.escape(str('' if t is None else t), quote=True)


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def tu(t):
    for a, b in TU:
        t = t.replace(a, b)
    return t


def pesos(v):
    """Como ccPesos() del motor: pesos enteros con separador de miles."""
    return '$' + format(int(v + 0.5) if v >= 0 else -int(-v + 0.5), ',')


def rango(r):
    if not r:
        return ''
    if r.get('min') and r.get('min') != r.get('max'):
        return pesos(r['min']) + ' a ' + pesos(r['max'])
    return pesos(r['max'])


def pend_id(cargo, nombre):
    """El mismo identificador que arma pendientes.py (seccion 7)."""
    return 'neto-%s-%s' % (cargo, nombre.lower().replace(' ', '-'))


def prest_id(concepto, col):
    return 'prest-%s-%s' % (re.sub(r'[^a-z]+', '-', concepto.lower()), col)


def fuente(d, clave, pagina=None):
    f = (d.get('fuentes') or {}).get(clave) or {}
    return ('<a class="cv-fuente" href="%s" target="_blank" rel="noopener noreferrer" title="%s">%s%s ↗</a>'
            % (esc(f.get('url') or '#'), esc(f.get('doc')), esc(f.get('corto')), (', ' + esc(pagina)) if pagina else ''))


def fila(rotulo, valor, estado=None, pend=None):
    return ('<div class="cv-fig"><span class="cv-fig-et">%s</span><span class="cv-fig-v">%s%s</span></div>'
            % (rotulo, valor, (' ' + chip(estado, pend)) if estado else ''))


def ficha(d, c):
    """La tarjeta completa del motor (cmpTarjeta), sin las cuentas con el
    ingreso del lector: esas las pone el JS en .cv-ficha-tuyo."""
    cab = ('<header class="cv-ficha-cab"><span class="cv-ficha-ico" aria-hidden="true">%s</span>'
           '<div><h3 class="cv-ficha-cargo">%s</h3><p class="cv-ficha-ente">%s</p></div></header>'
           % (c['icono'], esc(c['cargo']), esc(c['detalle'])))
    if c.get('pendiente'):
        return ('<article class="cv-ficha" id="cv-f-%s" data-id="%s" hidden>%s<div class="cv-figs">%s</div>'
                '<p class="cv-nota">%s</p></article>'
                % (esc(c['id']), esc(c['id']), cab, fila('Neto al mes', 'sin cifra', 'pendiente'), esc(c.get('nota'))))
    figs = [fila('Neto al mes', '<b>%s</b>' % rango(c['mensual']), c['mensualEstado']),
            '<p class="cv-concepto">%s</p>' % esc(c['mensualConcepto'])]
    if c.get('aguinaldoPrima'):
        figs.append(fila('Aguinaldo y prima vacacional, al año', rango(c['aguinaldoPrima']), 'oficial'))
    if c.get('pagoRiesgo'):
        figs.append(fila('Pago por riesgo, al año', pesos(c['pagoRiesgo']), 'oficial'))
    if c.get('asignaciones'):
        figs.append(fila('Asignaciones adicionales, al año', rango(c['asignaciones']), 'oficial'))
    figs.append(fila('Neto al año' + (' (parcial)' if c.get('parcial') else ''), '<b>%s</b>' % pesos(c['anual']), c['anualEstado']))
    figs.append('<p class="cv-concepto">%s</p>' % esc(c.get('anualConcepto') or ('Cómo se obtuvo: ' + c.get('anualOperacion', '') + '.')))

    extra = []
    if c.get('subniveles'):
        extra.append('<div class="cv-sub"><h4 class="cv-h4">Por nivel del tabulador</h4><ul>%s</ul></div>' % ''.join(
            '<li><span>%s</span><b>%s</b></li>' % (esc(s['nombre']), rango(s)) for s in c['subniveles']))
    h = c.get('honorarios')
    if h:
        extra.append('<p class="cv-nota cv-hon"><b>Además, por honorarios:</b> %s contratos con %s al año; en promedio %s '
                     '<b>brutos</b> al mes por contrato %s <small>(%s; %s)</small></p>'
                     % (format(h['contratos'], ','), pesos(h['montoAnual']), pesos(h['promedioMensual']), chip('derivado'),
                        esc(h['operacion']), esc(h['pagina'])))
    if c.get('lista'):
        extra.append('<details class="cv-lista"><summary>Las %d dependencias que comparten este límite</summary><ul>%s</ul>'
                     '<p class="cv-ficha-fuente">%s</p></details>'
                     % (len(c['lista']), ''.join('<li>%s</li>' % esc(n) for n in c['lista']), fuente(d, c.get('listaFuente'))))
    if c.get('entidades'):
        li = []
        for e in c['entidades']:
            if e.get('neto') is not None:
                neto = '%s netos %s' % (pesos(e['neto']), chip(e['netoEstado']))
            else:
                neto = 'neto no publicado %s' % chip('pendiente', pend_id(c['id'], e['nombre']))
            bruto = ('de %s a %s' % (pesos(e['bruto']), pesos(e['brutoHasta']))) if e.get('brutoHasta') else pesos(e['bruto'])
            li.append('<li><b>%s:</b> %s y %s brutos al mes %s<small>%s %s</small></li>'
                      % (esc(e['nombre']), neto, bruto, chip(e['brutoEstado']), esc(e['concepto']), fuente(d, e['fuente'], e.get('pagina'))))
        extra.append('<details class="cv-lista" open><summary>Congreso por congreso (%d con documento de 2026)</summary>'
                     '<ul class="cv-ents">%s</ul></details>' % (len(c['entidades']), ''.join(li)))

    return ('<article class="cv-ficha" id="cv-f-{id}" data-id="{id}" hidden>{cab}'
            '<div class="cv-ficha-tuyo" aria-live="polite"></div>'
            '<div class="cv-figs">{figs}</div>{extra}'
            '<p class="cv-nota">{nota}</p>'
            '<p class="cv-ficha-fuente">Fuente: {fu}</p></article>').format(
        id=esc(c['id']), cab=cab, figs=''.join(figs), extra=''.join(extra), nota=esc(c.get('nota')),
        fu=fuente(d, c['fuente'], c.get('pagina')))


def tarjeta(c):
    """Boton del selector de cargos: lo esencial para elegir."""
    if c.get('pendiente'):
        v = 'sin cifra ' + chip('pendiente')
    else:
        v = '<b>%s</b> <small>netos al mes</small>' % rango(c['mensual'])
    return ('<button type="button" class="cv-carta" data-id="%s" data-g="%s" aria-pressed="false">'
            '<span class="cv-carta-ico" aria-hidden="true">%s</span><span class="cv-carta-cargo">%s</span>'
            '<span class="cv-carta-v">%s</span><span class="cv-carta-veces" data-veces></span></button>'
            % (esc(c['id']), esc(c['grupo']), c['icono'], esc(c['cargo']), v))


def prestaciones(d):
    P, L = d['prestaciones'], d['ley']
    cols = P['columnas']
    cab = ''.join('<th scope="col"%s>%s<small>%s</small></th>' % (' class="cv-td-tu"' if c['id'] == 'lft' else '', esc(tu(c['nombre'])), esc(c['sub']))
                  for c in cols)
    filas = []
    tarjetas = []
    for f in P['filas']:
        celdas = []
        items = []
        for c in cols:
            x = f['celdas'].get(c['id']) or {}
            m = MARCAS.get((f['concepto'], c['id']))
            marca = ('<span class="cv-marca cv-marca-%s" aria-label="%s">%s</span> ' % (m, 'Lo tiene' if m == 'si' else 'No lo tiene', '✓' if m == 'si' else '✗')) if m else ''
            pend = (' ' + chip('pendiente', prest_id(f['concepto'], c['id']))) if x.get('estado') == 'pendiente' else ''
            nota = ('<span class="cv-td-nota">%s</span>' % esc(x['nota'])) if x.get('nota') else ''
            cuerpo = '%s%s%s%s<small>%s</small>' % (marca, esc(tu(x.get('tx', ''))), pend, nota, esc(x.get('ref', '')))
            celdas.append('<td%s>%s</td>' % (' class="cv-td-tu"' if c['id'] == 'lft' else '', cuerpo))
            items.append('<li%s><span class="cv-pc-quien">%s</span><span class="cv-pc-tx">%s</span></li>'
                         % (' class="cv-pc-tu"' if c['id'] == 'lft' else '', esc(tu(c['nombre'])), cuerpo))
        filas.append('<tr><th scope="row">%s</th>%s</tr>' % (esc(f['concepto']), ''.join(celdas)))
        tarjetas.append('<details class="cv-pc"%s><summary>%s</summary><ul>%s</ul></details>'
                        % (' open' if not tarjetas else '', esc(f['concepto']), ''.join(items)))
    tabla = ('<div class="cv-tabla-caja" tabindex="0" role="region" aria-label="Cuadro de prestaciones">'
             '<table class="cv-tabla"><thead><tr><th scope="col">Prestación</th>%s</tr></thead><tbody>%s</tbody></table></div>'
             % (cab, ''.join(filas)))
    fu = ''.join('<li>%s</li>' % x for x in [fuente(d, 'LFT'), fuente(d, 'DIP', 'Anexo 1, p. 145'), fuente(d, 'SEN', 'Anexo 3'),
                     fuente(d, 'PEF', 'Anexos 23.1.3, 23.2.2 y 23.3.4'), fuente(d, 'PJF', 'numerales 8.1 y 8.2')])
    fu = '<ul class="cv-fuentes">%s</ul>' % fu
    return '''<section class="cv-sec" id="cvPrest" aria-labelledby="cvPrestTit">
    <h2 class="cv-tit" id="cvPrestTit"><span class="cv-n">4</span> Tus prestaciones de ley contra las de ellos</h2>
    <p class="cv-txt">La Ley Federal del Trabajo fija lo mínimo que un patrón debe darte. Los manuales de cada Poder fijan lo que reciben sus integrantes. Estas son las dos reglas, lado a lado.</p>
    <div class="cv-prest-cuenta" id="cvPrestCuenta" aria-live="polite"></div>
    <p class="cv-nota cv-ley">{nota_ley}</p>
    <div class="cv-pcs">{tarjetas}</div>
    {tabla}
    <p class="cv-leyenda"><span class="cv-marca cv-marca-si">✓</span> lo tiene · <span class="cv-marca cv-marca-no">✗</span> no lo tiene, según el propio documento. Donde el documento no registra algo, no se marca: que no lo registre no prueba que no exista.</p>
    <div class="cv-ficha-fuente">Fuentes: {fu}</div>
  </section>'''.format(nota_ley=esc(L['nota']), tarjetas=''.join(tarjetas), tabla=tabla, fu=fu)


def construir(base, ref):
    d = base['comparador_salarial']
    cc = base['calculadora_civica']
    par = cc['parametros']
    cargos = d['cargos']
    grupos = d['grupos']

    filtros = ['<button type="button" class="cv-filtro" data-g="todos" aria-pressed="true">Todos <small>%d</small></button>' % len(cargos)]
    for g in grupos:
        n = sum(1 for c in cargos if c['grupo'] == g['id'])
        filtros.append('<button type="button" class="cv-filtro" data-g="%s" aria-pressed="false"><span aria-hidden="true">%s</span> %s <small>%d</small></button>'
                       % (esc(g['id']), g['icono'], esc(g['nombre']), n))

    sm = par['salario_minimo']
    tm = cc['tarifa_mensual']
    im = cc['imss_obrero']
    se = par['subsidio_empleo']
    uma = par['uma']

    datos = {
        'cargos': [{k: c.get(k) for k in ('id', 'grupo', 'cargo', 'icono', 'mensual', 'anual', 'anualEstado', 'parcial', 'pendiente', 'fuente')}
                   for c in cargos],
        'grupos': {g['id']: g['nombre'] for g in grupos},
        'ley': d['ley'],
        'fuentes': {k: {'corto': v.get('corto'), 'url': v.get('url')} for k, v in d['fuentes'].items()},
        'sm': {'general': sm['mensual_general'], 'frontera': sm['mensual_frontera']},
        'isr': {'renglones': tm['renglones'], 'tope_uma': im['tope_sbc_uma'], 'ramos': [{'pct': r['pct'], 'base': r['base']} for r in im['ramos']],
                'uma_diaria': uma['diaria'], 'uma_mensual': uma['mensual'], 'sub_pct': se['pct_uma'], 'sub_tope': se['tope_ingreso_mensual']},
    }

    return '''<div class="cv" id="cvRaiz">
  <section class="cv-arranque" aria-labelledby="cvArrTit">
    <p class="cv-kicker">Calculadora Cívica · aplicación 2</p>
    <h2 class="cv-grande" id="cvArrTit">⚡ Tú contra la alta burocracia</h2>
    <p class="cv-txt">Tu ingreso neto frente al de quienes legislan, juzgan y gobiernan —y sus asesores y proyectistas—, con el documento de cada cifra. Cifras del Anexo 23 del Presupuesto de Egresos 2026 {r_pef} y de los manuales de remuneraciones que el Senado, la Cámara de Diputados y el Poder Judicial publicaron en el Diario Oficial el 27 de febrero de 2026.</p>
    <ol class="cv-indice" aria-label="Los pasos">
      <li><a href="#cvPaso1"><span class="cv-n">1</span> Tu ingreso</a></li>
      <li><a href="#cvPaso2"><span class="cv-n">2</span> Elige un cargo</a></li>
      <li><a href="#cvDuelo"><span class="cv-n">3</span> Cara a cara</a></li>
      <li><a href="#cvPrest"><span class="cv-n">4</span> Prestaciones</a></li>
    </ol>
  </section>

  <section class="cv-sec cv-paso" id="cvPaso1" aria-labelledby="cvP1Tit">
    <h2 class="cv-tit" id="cvP1Tit"><span class="cv-n">1</span> Tu ingreso</h2>
    <div class="cv-form">
      <label class="cv-campo" for="cvMonto"><span>¿Cuánto ganas? Sin separadores o con ellos, como quieras.</span>
        <input type="text" id="cvMonto" class="cv-input cv-input-num" inputmode="decimal" autocomplete="off" placeholder="{sm_txt}"></label>
      <div class="cv-seg" role="group" aria-label="Periodo">
        <button type="button" class="cv-opc" data-periodo="mes" aria-pressed="true">Al mes</button>
        <button type="button" class="cv-opc" data-periodo="ano" aria-pressed="false">Al año</button>
      </div>
      <div class="cv-seg" role="group" aria-label="Bruto o neto">
        <button type="button" class="cv-opc" data-tipo="bruto" aria-pressed="true">Bruto <small>(antes de descuentos)</small></button>
        <button type="button" class="cv-opc" data-tipo="neto" aria-pressed="false">Neto <small>(lo que te depositan)</small></button>
      </div>
    </div>
    <div class="cv-atajos" role="group" aria-label="Atajos con cifras oficiales">
      <span>O usa una cifra oficial:</span>
      <button type="button" class="cv-atajo" data-sm="general">Salario mínimo general · {sm_g} al mes</button>
      <button type="button" class="cv-atajo" data-sm="frontera">Salario mínimo en la frontera norte · {sm_f} al mes</button>
      <button type="button" class="cv-atajo cv-borrar" data-borrar>Borrar mi sueldo</button>
    </div>
    <p class="cv-fuente-sm">Salario mínimo 2026 {chip_of}: {sm_fuente}. Lo que escribes se queda en tu navegador: no se envía a ningún lado.</p>
    <div class="cv-lector" id="cvLector" aria-live="polite"></div>
  </section>

  <section class="cv-sec cv-paso" id="cvPaso2" aria-labelledby="cvP2Tit">
    <h2 class="cv-tit" id="cvP2Tit"><span class="cv-n">2</span> Elige un cargo</h2>
    <div class="cv-filtros" role="group" aria-label="Filtrar cargos por Poder">
      {filtros}
    </div>
    <div class="cv-cartas" id="cvCartas">
      {cartas}
    </div>
  </section>

  <section class="cv-sec" id="cvDuelo" aria-labelledby="cvDueloTit">
    <h2 class="cv-tit" id="cvDueloTit"><span class="cv-n">3</span> Cara a cara</h2>
    <div class="cv-duelo" id="cvDueloCaja" aria-live="polite"></div>
    <div class="cv-fichas">
      {fichas}
    </div>
    <div class="cv-acciones">
      <button type="button" class="cv-boton" id="cvCompartir"><span aria-hidden="true">📣</span> Compartir este cara a cara</button>
      <button type="button" class="cv-boton cv-sec-b" id="cvCopiarTodo"><span aria-hidden="true">📋</span> Copiar la comparativa para redes</button>
      <button type="button" class="cv-boton cv-sec-b" id="cvEnlace"><span aria-hidden="true">🔗</span> Copiar el enlace a este cargo</button>
      <a class="cv-boton cv-sec-b" href="pase-del-auditor.html"><span aria-hidden="true">🍺</span> Descargar Reporte Salarial ($79)</a>
    </div>
    <p class="cv-copiado" id="cvCopiado" aria-live="polite"></p>
    <textarea class="cv-texto" id="cvTexto" rows="8" readonly hidden aria-label="Texto para copiar"></textarea>
  </section>

  <section class="cv-sec" id="cvTodos" aria-labelledby="cvTodosTit">
    <h2 class="cv-tit" id="cvTodosTit"><span aria-hidden="true">📊</span> Todos de un vistazo: neto al año</h2>
    <p class="cv-txt">Cada barra es el neto anual del cargo, a la misma escala que la tuya. Toca una para verla cara a cara.</p>
    <div class="cv-ranking" id="cvRanking"></div>
    <p class="cv-nota">Las barras usan la cifra anual de cada tarjeta, con su estado: oficial cuando el documento la publica así; derivado cuando la armamos con el mensual del documento (la operación está en la tarjeta). Las del Poder Judicial y los congresos locales son parciales.</p>
  </section>

  {prest}

  <aside class="cv-aviso" aria-labelledby="cvLeeTit">
    <h2 class="cv-tit" id="cvLeeTit"><span aria-hidden="true">🔍</span> ¿Cómo se lee esta comparación?</h2>
    <p>Las cifras son netas —lo que llega a la persona después de impuestos— salvo el promedio de los honorarios y los brutos de los congresos locales, que el documento da en bruto y así se dice. Cuando un documento publica un rango, las cuentas usan su máximo. El artículo 127 de la Constitución prohíbe que un servidor público reciba una remuneración mayor que la de la Presidencia. Las cuentas «veces», «meses» y «días» son derivadas: dividen la cifra oficial entre tu ingreso neto.</p>
    <p>Tu neto, si escribes un bruto, se calcula como el de quien trabaja en nómina (sueldos y salarios): {r_isr} menos el subsidio para el empleo ({r_sub}), y las cuotas obreras del IMSS ({r_imss}). Todas oficiales; tu neto es derivado. Si cobras por honorarios, RESICO, arrendamiento o plataformas, escribe tu neto, o saca la cuenta completa en <a href="herramienta-calculadora-ticket.html">🧾 Tu estado de cuenta</a>.</p>
    <p>Lo que todavía nos deben las instituciones está en el <a href="pendientes.html">Registro de pendientes</a>. Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>.</p>
    <p class="cv-hermanas">Sigue con la Calculadora: <a href="herramienta-calculadora-ticket.html">🧾 Tu estado de cuenta</a> · <a href="herramienta-calculadora-reloj.html">⏱️ El reloj de la deuda</a> · <a href="simulador-presupuesto.html">🧮 Reparte el presupuesto</a> · <a href="radar-estado-de-cuenta.html">🏛️ Estado de cuenta administrativo</a> · <a href="numeros-lo-que-cuestan-los-poderes.html">🏛️ Lo que cuestan los Poderes</a></p>
  </aside>
  <script type="application/json" id="cvDatos">{datos}</script>
</div>'''.format(
        r_pef=ref('ref-pef2026'),
        sm_txt='Ej.: ' + format(sm['mensual_general'], ',.2f'),
        sm_g=pesos(sm['mensual_general']), sm_f=pesos(sm['mensual_frontera']),
        chip_of=chip(sm.get('estado', 'oficial')), sm_fuente=esc(sm['fuente']),
        filtros='\n      '.join(filtros),
        cartas='\n      '.join(tarjeta(c) for c in cargos),
        fichas='\n      '.join(ficha(d, c) for c in cargos),
        prest=prestaciones(d),
        r_isr=esc('la tarifa mensual del ISR (' + tm['ley'] + ', ' + tm['fuente'] + ')'),
        r_sub=esc(se['fuente']), r_imss=esc(im['fuente']),
        datos=_json(datos))
