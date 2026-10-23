# -*- coding: utf-8 -*-
"""Modo Inspector, aplicacion 1: «Expedientes de casos de la ASF».

Fue «Que encontro la ASF», en pagina propia desde el 12-10-2026. El
21-10-2026 (pedido del autor) se fusiono con la aplicacion 2, «Expedientes
de casos», y se amplio a todas las autoridades que fiscalizan el dinero
publico (fiscalizadores.py), con un agente que vigila lo que publican de las
Cuentas Publicas 2024 a 2027 (agente_fiscalizacion.py). Sus capitulos: los
casos (expedientes.html, de expedientes.py), quien fiscaliza, el
seguimiento, y los siete que ya tenia.

Antes la pagina cargaba la portada entera en un marco y el motor pintaba
renderCuentaPublica(). Ahora el cuerpo se escribe aqui, con las cifras ya
puestas, desde base['cuenta_publica_asf'] (Matrices de Datos Basicos de la
ASF). El JavaScript (assets/auditor/js/insp-asf.js) solo enriquece: cuenta
regresiva, cambio de cifra en la serie, selector de estado con memoria,
orden del ranking y la descarga CSV generada en el navegador.

Regla de la plataforma (AGENTS.md, §2): cada cifra lleva su chip y su
fuente; los derivados dicen su operacion.

Lo llama apartados.insp_nativa(): construir(base, ref) -> HTML del cuerpo.
"""
import html
import json

import expedientes
import fiscalizadores
import insp_nota

from presupuesto_modulos import chip

ESTILOS = ['insp-asf.css']
SCRIPTS = ['insp-asf.js']

MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
         'septiembre', 'octubre', 'noviembre', 'diciembre']

# Las cifras que se comparan en la serie (las mismas del motor).
METRICAS = [('porAclarar', 'Por aclarar', True), ('observado', 'Observado', True),
            ('recuperaciones', 'Recuperado', True), ('auditorias', 'Auditorías', False),
            ('PO', 'Pliegos', False)]

ACC = ['R', 'RD', 'PEFCF', 'SA', 'PRAS', 'PO']


def esc(t):
    return html.escape(str(t), quote=True)


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def num(v):
    return format(int(round(v)), ',')


def mdp(p, d=1):
    return '$' + format(p / 1e6, ',.%df' % d) + ' mdp'


def monto(p):
    if abs(p) >= 1e12:
        return '$' + format(p / 1e12, ',.2f') + ' billones'
    return mdp(p)


def pesos(p):
    return '$' + format(int(round(p)), ',')


def pct(v, d=1):
    return format(v, ',.%df' % d) + ' %'


def fecha(iso):
    y, m, d = (int(x) for x in iso.split('-'))
    return '%d de %s de %d' % (d, MESES[m - 1], y)


def minus(t):
    return t[0].lower() + t[1:]


def nombre(n):
    return 'Estado de México' if n == 'México' else n


def fuente(C, clave, pagina=None):
    f = C['fuentes'].get(clave)
    if not f:
        return chip('pendiente') + ' fuente por documentar'
    pag = ''
    if pagina not in (None, ''):
        s = str(pagina)
        pag = (', p. ' + s) if s.isdigit() else ((', pp. ' + s) if s[0].isdigit() else ', ' + s)
    return '<a class="ia-fuente" href="%s" target="_blank" rel="noopener" title="%s">%s%s ↗</a>' % (
        esc(f['url']), esc(f['doc']), esc(f.get('corto') or f['doc']), esc(pag))


def dato(valor, rotulo, estado, pie=''):
    return ('<div class="ia-dato"><strong>%s</strong><span>%s %s</span>%s</div>'
            % (valor, rotulo, chip(estado), ('<small>%s</small>' % pie) if pie else ''))


def barra(v, mx, extra=''):
    w = 0 if not mx else max(0.0, min(100.0, v / mx * 100))
    return '<span class="ia-barra%s" aria-hidden="true"><i style="--w:%.2f%%"></i></span>' % (extra, w)


def fila(etq, v, mx, txt, extra=''):
    return '<li class="ia-fila"><span class="ia-fila-et">%s</span>%s<span class="ia-fila-v">%s</span></li>' % (
        etq, barra(v, mx, extra), txt)


# ---------------------------------------------------------------- arranque
def arranque(C, ref, prox):
    T, F = C['cp2024']['total'], C['cp2024']['federalizado']
    fed = F['porAclarar'] / T['porAclarar'] * 100
    cuenta = ''
    if prox:
        cuenta = ('<p class="ia-reloj" id="iaReloj" data-fecha="%s"><span class="ia-reloj-n" id="iaRelojN" hidden></span>'
                  '<span class="ia-reloj-tx"><b>Próxima entrega de la ASF:</b> %s, el <b>%s</b>. '
                  '<span id="iaRelojEst" hidden>%s</span></span></p>') % (
            prox['fecha'], esc(minus(prox['titulo'])), fecha(prox['fecha']), chip('derivado'))
    return '''<section class="ia-arranque" aria-labelledby="iaArrTit">
        <p class="ia-arr-pre">Los expedientes oficiales de quienes fiscalizan el dinero público · Cuenta Pública 2024, tres entregas de la Auditoría Superior</p>
        <h2 class="ia-arr-tit" id="iaArrTit"><span class="ia-arr-cifra">%s</span> quedaron por aclarar %s</h2>
        <p class="ia-arr-txt">Es el dinero público que, al cerrar cada auditoría, <b>no tenía documentos que acreditaran en qué se gastó</b>. No es lo mismo que robado: los entes todavía pueden aclararlo. Si no lo hacen, el caso pasa a investigación y puede llegar al Tribunal Federal de Justicia Administrativa o a la Fiscalía (LFRCF, art. 40). %s %s</p>
        <div class="ia-arr-datos">
          %s
          %s
          %s
        </div>
        <p class="ia-arr-nota">%s Porcentaje: por aclarar del gasto federalizado (%s) ÷ total por aclarar (%s).</p>
        %s
        <div class="ia-arr-acc">
          <a class="ia-boton ia-boton-pri" href="expedientes.html">📂 Los casos por aclarar</a>
          <a class="ia-boton" href="herramienta-inspector-asf-autoridades.html">🏛️ Quién fiscaliza</a>
          <a class="ia-boton" href="herramienta-inspector-asf-estado.html">🗺️ Lo de tu estado</a>
        </div>
      </section>''' % (
        mdp(T['porAclarar']), chip('oficial'), fuente(C, 'MDB2024', C['cp2024']['pagina']), ref('ref-asf-mdb2024'),
        dato(num(T['auditorias']), 'auditorías practicadas', 'oficial'),
        dato(pct(fed), 'de lo por aclarar está en estados y municipios', 'derivado'),
        dato(mdp(T['recuperaciones']), 'se recuperaron durante las auditorías', 'oficial'),
        chip('derivado'), mdp(F['porAclarar']), mdp(T['porAclarar']), cuenta)


def cap_archivo(slug):
    """Cada capitulo vive en su pagina (pedido del autor, 21-10-2026): la
    portada de la aplicacion queda con el arranque y el indice. Los casos
    conservan su direccion de siempre, expedientes.html."""
    return {'catalogo': insp_nota.CATALOGO, 'casos': expedientes.ARCHIVO}.get(slug) or 'herramienta-inspector-asf-%s.html' % slug


def indice(caps):
    return ('<nav class="ia-indice" aria-label="Capítulos de esta aplicación"><p class="ia-indice-tit">%d capítulos · cada uno abre su página</p><ol>%s</ol></nav>'
            % (len(caps), ''.join(
                '<li><a href="%s" data-ia-ancla="%s"><span class="ia-i-num">%02d</span><span class="ia-i-ico" aria-hidden="true">%s</span>'
                '<span class="ia-i-tit">%s</span><span class="ia-i-cifra">%s</span></a></li>'
                % (cap_archivo(c['slug']), c['ancla'], k, c['ico'], esc(c['corto']), c['cifra']) for k, c in enumerate(caps, 1))))


def sec(ancla, ico, tit, cuerpo):
    """Un capitulo. El titulo lo pone la cabecera de su pagina (h1), asi que
    aqui solo queda como nombre de la region."""
    return '''<section class="ia-sec" id="%s" aria-label="%s">
        %s
      </section>''' % (ancla, esc(tit), cuerpo)


# ---------------------------------------------------------------- capitulos
def calendario(C, prox):
    items = []
    for c in C['calendario']:
        cls = 'ia-hecho' if c.get('hecho') else ('ia-prox' if c is prox else '')
        pie = ('<small>%s · %s</small>' % (fuente(C, c['fuente']), esc(c['fundamento']))) if c.get('fundamento') else ''
        items.append('<li class="%s" data-fecha="%s"><span class="ia-l-fecha">%s</span><b>%s</b><span>%s</span>%s</li>'
                     % (cls, c['fecha'], fecha(c['fecha']), esc(c['titulo']), esc(c['texto']), pie))
    return sec('ia-calendario', '📡', 'Qué es la Cuenta Pública y el seguimiento de 2024 a 2027', '''
        <p class="ia-txt">El presupuesto dice cuánto se <b>puede</b> gastar. La <b>Cuenta Pública</b> dice cuánto se gastó de verdad: es el informe contable, presupuestario y programático de los tres Poderes, los órganos autónomos y las empresas del Estado. Hacienda la entrega a la Cámara de Diputados y la <b>Auditoría Superior de la Federación (ASF)</b> la revisa en tres entregas.</p>
        <ol class="ia-linea">%s</ol>
        <p class="ia-nota">Los datos de la Cuenta Pública de cada año están en el %s. Las fechas son las que fija la ley; si la Cámara concede prórroga a Hacienda, la ASF recorre las suyas (CPEUM, art. 74, fr. VI). La cuenta regresiva %s la calcula tu navegador con la fecha de hoy.</p>
        <h2 class="ia-sub" id="ia-seguimiento">📡 El seguimiento: 2024, 2025, 2026 y 2027</h2>
        <p class="ia-txt">Un agente de Auditavisión recorre las direcciones donde la ASF publica cada entrega y los portales de las demás autoridades. Cuando aparece un documento nuevo, lo marca aquí; sus cifras entran a la plataforma solo después de extraerlas del documento oficial, con su huella. Nada se estima.</p>
        %s''' % (
        ''.join(items), fuente(C, 'CPSHCP'), chip('derivado'), fiscalizadores.seguimiento_html(chip)))


def autoridades(ref):
    return '''<section class="ia-sec" id="ia-autoridades" aria-label="Quién fiscaliza el dinero público">
        <p class="ia-txt">La Auditoría Superior no está sola. Revisar el dinero público es trabajo de varias autoridades, cada una con su expediente oficial: unas auditan desde fuera, otras vigilan desde dentro, otras sancionan y otras coordinan. Aquí están todas, con el artículo que les da la facultad, el documento que publican y lo que de eso ya está en Auditavisión.</p>
        %s
        <p class="ia-nota">Cada fundamento se verificó contra el texto vigente de la ley en el portal de la Cámara de Diputados. El estado de cada portal (📡) lo revisa el agente de seguimiento en cada vuelta. Lo que aún no está integrado es una falta de la plataforma, no de la autoridad.</p>
      </section>''' % fiscalizadores.autoridades_html(ref)


def cifras(C):
    T = C['cp2024']['total']
    acc = {a['clave']: a for a in C['acciones']}
    pila = ''.join('<span class="ia-pila-%s" style="--w:%.3f%%" title="%s: %s"></span>'
                   % (k, T[k] / T['acciones'] * 100, k, num(T[k])) for k in ACC)
    ley = ''.join('<li><i class="ia-pila-%s" aria-hidden="true"></i><b>%s</b> <span class="ia-ley-n">%s</span> %s <small>%s del total</small></li>'
                  % (k, k, num(T[k]), esc(acc[k]['nombre']), pct(T[k] / T['acciones'] * 100)) for k in ACC)
    return sec('ia-cifras', '🔎', 'Lo que encontró la ASF en la Cuenta Pública 2024', '''
        <p class="ia-txt">Es el ejercicio más reciente con sus tres entregas completas (corte: %s).</p>
        <div class="ia-datos">%s%s%s%s%s</div>
        <h3 class="ia-sub">Las %s acciones, por tipo</h3>
        <div class="ia-pila" role="img" aria-label="Acciones por tipo: %s">%s</div>
        <ul class="ia-ley">%s</ul>
        <p class="ia-nota">%s %s. Porcentajes %s: acciones de cada tipo ÷ %s acciones. Los informes individuales, uno por auditoría, están en el %s.</p>
        <div class="ia-alerta"><b>Por aclarar no es lo mismo que robado.</b> %s</div>''' % (
        esc(C['cp2024']['corte']),
        dato(num(T['auditorias']), 'auditorías practicadas', 'oficial'),
        dato(monto(T['muestra']), 'revisados, de %s seleccionados' % monto(T['universo']), 'oficial', pct(T['representatividad'], 2) + ' de lo seleccionado'),
        dato(num(T['acciones']), 'acciones promovidas', 'oficial'),
        dato(mdp(T['porAclarar']), 'por aclarar', 'oficial', 'Sin documentos que acreditaran el gasto al cierre de la auditoría'),
        dato(mdp(T['recuperaciones']), 'recuperados durante la auditoría', 'oficial', 'Dinero efectivamente reintegrado'),
        num(T['acciones']), esc(', '.join('%s %s' % (k, num(T[k])) for k in ACC)), pila, ley,
        chip('oficial'), fuente(C, 'MDB2024', C['cp2024']['pagina']), chip('derivado'), num(T['acciones']),
        fuente(C, 'IR2024'), esc('. '.join(C['nota'].split('. ')[2:]))))


def serie_filas(C, S, k, es_mdp):
    mx = max(r.get(k) or 0 for r in S)
    out = []
    for r in S:
        est = r['observadoEstado'] if k == 'observado' else 'oficial'
        v = r.get(k) or 0
        out.append(fila('CP %d <small>%s</small>' % (r['cp'], fuente(C, r['fuente'], r['pagina'])), v, mx,
                        '%s %s' % (mdp(v) if es_mdp else num(v), chip(est))))
    return ''.join(out)


def serie(C):
    S = C.get('serie') or []
    if not S:
        return sec('ia-serie', '📈', 'Seis años de revisiones', '<p class="ia-nota">%s La base no trae la serie histórica.</p>' % chip('pendiente'))
    obs = sum(r['observado'] for r in S)
    rec = sum(r['recuperaciones'] for r in S)
    botones = ''.join('<button type="button" class="ia-chipbtn" data-ia-met="%s" aria-pressed="%s">%s</button>'
                      % (k, 'true' if i == 0 else 'false', et) for i, (k, et, _) in enumerate(METRICAS))
    tabla = ''.join('<tr><th scope="row">CP %d</th><td>%s</td><td>%s %s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                    % (r['cp'], mdp(r['porAclarar']), mdp(r['observado']), chip(r['observadoEstado']),
                       mdp(r['recuperaciones']), num(r['auditorias']), num(r['PO'])) for r in S)
    return sec('ia-serie', '📈', 'Seis años de revisiones: %d a %d' % (S[0]['cp'], S[-1]['cp']), '''
        <p class="ia-txt">Cada renglón es el total de la matriz consolidada de una Cuenta Pública, con su documento y su página. En esos seis años la ASF observó %s y, durante las propias auditorías, se recuperaron %s: el <b>%s</b> %s (recuperado ÷ observado, suma de los seis años).</p>
        <div class="ia-metricas" role="group" aria-label="Qué cifra comparar" id="iaMetricas" hidden>%s</div>
        <ul class="ia-filas" id="iaSerie" aria-live="polite">%s</ul>
        <details class="ia-det"><summary>Ver la tabla completa de los seis años</summary>
          <div class="ia-tabla-w"><table class="ia-tabla"><thead><tr><th>Cuenta Pública</th><th>Por aclarar</th><th>Observado</th><th>Recuperado</th><th>Auditorías</th><th>Pliegos</th></tr></thead><tbody>%s</tbody></table></div>
        </details>
        <p class="ia-nota"><b>Cómo leerla.</b> Observado = recuperado + por aclarar. Desde la Cuenta Pública 2023 la matriz ya no publica el total observado: para 2023 y 2024 se suma y se marca %s. Los montos están en pesos de cada año, sin ajustar por inflación, y el «por aclarar» es el del corte de cada matriz: lo que se solventó después no aparece aquí. La matriz de la Cuenta Pública 2018 no está publicada en el portal de la ASF %s: queda pendiente hasta que la ASF la transparente.</p>''' % (
        mdp(obs), mdp(rec), pct(rec / obs * 100), chip('derivado'), botones,
        serie_filas(C, S, 'porAclarar', True), tabla, chip('derivado'), chip('pendiente', 'asf-matriz-2018')))


def donde(C):
    T, F = C['cp2024']['total'], C['cp2024']['federalizado']
    grupos = C['cp2024']['grupos']
    mxg = max(g['subtotal']['porAclarar'] for g in grupos)
    sect = [dict(s, grupo=g['grupo']) for g in grupos for s in g['sectores']]
    top = sorted([s for s in sect if s['porAclarar'] > 0], key=lambda s: -s['porAclarar'])[:10]
    fed = F['porAclarar'] / T['porAclarar'] * 100
    return sec('ia-donde', '🏛️', 'Dónde se concentra lo que falta aclarar', '''
        <p class="ia-txt">El <b>%s</b> %s de lo que quedó por aclarar está en el <b>gasto federalizado</b>: el dinero federal que reciben estados y municipios (%s en %s auditorías).</p>
        <h3 class="ia-sub">Por grupo de gasto</h3>
        <ul class="ia-filas">%s</ul>
        <h3 class="ia-sub">Los diez renglones con más monto por aclarar</h3>
        <ol class="ia-filas ia-top">%s</ol>
        <p class="ia-nota">%s %s. En el gasto federalizado la ASF agrupa por tema de fiscalización (educación, salud, participaciones…), no por dependencia. Porcentaje %s: por aclarar del grupo ÷ total. ¿Quieres ver casos concretos? Los <a href="expedientes.html">Expedientes de casos por aclarar</a> siguen auditorías una por una.</p>''' % (
        pct(fed), chip('derivado'), mdp(F['porAclarar']), num(F['auditorias']),
        ''.join(fila('%s <small>%s auditorías</small>' % (esc(g['grupo']), num(g['subtotal']['auditorias'])),
                     g['subtotal']['porAclarar'], mxg, mdp(g['subtotal']['porAclarar'])) for g in grupos),
        ''.join(fila('%s <small>%s</small>' % (esc(s['nombre']), esc(s['grupo'])), s['porAclarar'], top[0]['porAclarar'],
                     mdp(s['porAclarar'])) for s in top),
        chip('oficial'), fuente(C, 'MDB2024', '11 a 14'), chip('derivado')))


def _nacional(E):
    pa = sum(e['total']['porAclarar'] for e in E)
    mu = sum(e['total']['muestra'] for e in E)
    return {'porAclarar': pa, 'muestra': mu, 'prom': pa / len(E), 'cada100': pa / mu * 100}


def estado_panel(C, e, orden, nac):
    """El panel de un estado. insp-asf.js pinta el mismo marcado al cambiar."""
    t = e['total']
    pos = orden.index(e) + 1
    c100 = t['porAclarar'] / t['muestra'] * 100 if t['muestra'] else 0
    veces = t['porAclarar'] / nac['prom']
    mx = max(t['porAclarar'], nac['prom'])
    filas = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                    % (esc(d['ente']), num(d['auditorias']), num(d['acciones']), mdp(d['porAclarar']), mdp(d['recuperaciones']))
                    for d in e['desglose'])
    return '''<p class="ia-est-tit"><b>%s</b> · lugar <b>%d de 32</b> por monto por aclarar %s</p>
          <div class="ia-datos">%s%s%s%s</div>
          <div class="ia-compara">
            <h3 class="ia-sub">Tu estado contra el promedio</h3>
            <ul class="ia-filas">%s%s</ul>
            <p class="ia-compara-tx">De cada <b>$100</b> que la ASF revisó en %s, quedaron <b>$%s</b> por aclarar; en los 32 estados juntos, <b>$%s</b>. Lo por aclarar es <b>%s veces</b> el promedio por estado. %s</p>
            <p class="ia-nota">%s Promedio por estado = suma de lo por aclarar en los 32 (%s) ÷ 32. «De cada $100» = por aclarar ÷ monto revisado (muestra) × 100; el de los 32 usa las sumas de ambos. Veces = por aclarar del estado ÷ promedio por estado.</p>
          </div>
          <div class="ia-tabla-w"><table class="ia-tabla"><caption>Quién gastó el dinero federal en %s</caption><thead><tr><th>Quién gastó</th><th>Auditorías</th><th>Acciones</th><th>Por aclarar</th><th>Recuperado</th></tr></thead><tbody>%s</tbody></table></div>''' % (
        esc(nombre(e['entidad'])), pos, chip('derivado'),
        dato(num(t['auditorias']), 'auditorías al dinero federal que recibió', 'derivado'),
        dato(num(t['acciones']), 'acciones promovidas', 'derivado', '%s pliegos de observaciones y %s promociones de responsabilidad' % (num(t['PO']), num(t['PRAS']))),
        dato(mdp(t['porAclarar']), 'por aclarar', 'derivado', 'Lugar %d de 32' % pos),
        dato(mdp(t['recuperaciones']), 'recuperados durante la auditoría', 'derivado'),
        fila(esc(nombre(e['entidad'])), t['porAclarar'], mx, mdp(t['porAclarar']), ' ia-barra-sel'),
        fila('Promedio por estado', nac['prom'], mx, mdp(nac['prom'])),
        esc(nombre(e['entidad'])), format(c100, ',.2f'), format(nac['cada100'], ',.2f'), format(veces, ',.2f'), chip('derivado'),
        chip('derivado'), mdp(nac['porAclarar']),
        esc(nombre(e['entidad'])), filas)


def ranking(E, sel):
    orden = sorted(E, key=lambda x: -x['total']['porAclarar'])
    mx = orden[0]['total']['porAclarar']
    return ''.join(
        '<li><button type="button" class="ia-rank%s" data-ia-ent="%s"%s><span class="ia-fila-et">%d. %s</span>%s<span class="ia-fila-v">%s</span></button></li>'
        % (' ia-rank-sel' if x is sel else '', esc(x['entidad']), ' aria-current="true"' if x is sel else '', i, esc(nombre(x['entidad'])),
           barra(x['total']['porAclarar'], mx, ' ia-barra-sel' if x is sel else ''), mdp(x['total']['porAclarar']))
        for i, x in enumerate(orden, 1))


def estado(C):
    E = C['cp2024']['entidades']
    orden = sorted(E, key=lambda x: -x['total']['porAclarar'])
    e = E[0]
    nac = _nacional(E)
    opciones = ''.join('<option value="%s"%s>%s</option>' % (esc(x['entidad']), ' selected' if x is e else '', esc(nombre(x['entidad'])))
                       for x in sorted(E, key=lambda x: nombre(x['entidad'])))
    ordenes = [('porAclarar', 'Por aclarar'), ('cada100', 'De cada $100 revisados'), ('auditorias', 'Auditorías'), ('recuperaciones', 'Recuperado')]
    ob = ''.join('<button type="button" class="ia-chipbtn" data-ia-orden="%s" aria-pressed="%s">%s</button>'
                 % (k, 'true' if i == 0 else 'false', et) for i, (k, et) in enumerate(ordenes))
    return sec('ia-estado', '🗺️', 'Lo que la ASF le observó a tu estado', '''
        <p class="ia-txt">El dinero federal que llega a cada estado lo revisa la ASF en tres niveles: el gobierno del estado, sus municipios (alcaldías en la Ciudad de México) y otros entes locales. Aparte, %s auditorías se hicieron a las dependencias federales que coordinan esos fondos.</p>
        <div class="ia-elige">
          <label for="iaEntSel">Elige tu estado</label>
          <select id="iaEntSel" class="ia-select">%s</select>
          <noscript><p class="ia-nota">Sin JavaScript se muestra Aguascalientes; el ranking de abajo trae los 32 y la descarga CSV de cada estado está en el %s.</p></noscript>
        </div>
        <div class="ia-panel" id="iaEntidad" aria-live="polite">%s</div>
        <p class="ia-nota">%s Cada renglón: %s. %s Los totales del estado suman sus tres renglones. «Otros» agrupa organismos, universidades y demás entes locales que recibieron dinero federal. Más señales de tu estado en su ficha técnica del <a href="herramienta-inspector-entes.html?nivel=estatal&amp;orden=radInt#ie-dir">Auditor de entes públicos</a>.</p>
        <h3 class="ia-sub" id="iaRankTit">Los 32 estados, por monto por aclarar</h3>
        <div class="ia-metricas" role="group" aria-label="Ordenar el ranking" id="iaOrden" hidden>%s</div>
        <p class="ia-nota ia-solojs" hidden>Toca un estado para ver su detalle arriba.</p>
        <ol class="ia-ranking" id="iaRanking" aria-labelledby="iaRankTit">%s</ol>''' % (
        num(C['cp2024']['coordinadoras']['auditorias']), opciones, fuente(C, 'MDB2024', C['cp2024']['paginaEntidades']),
        estado_panel(C, e, orden, nac), chip('oficial'), fuente(C, 'MDB2024', C['cp2024']['paginaEntidades']), chip('derivado'),
        ob, ranking(E, e)))


def acciones(C):
    tarjetas = ''.join('<div class="ia-accion ia-acc-%s"><span class="ia-clave">%s</span><b>%s</b><p>%s</p><small>%s · %s</small></div>'
                       % (a['tipo'], a['clave'], esc(a['nombre']), esc(a['que']), esc(a['fundamento']), a['tipo']) for a in C['acciones'])
    plazos = ''.join('<li><b>%s</b> <span>%s</span> <small>%s</small></li>' % (esc(p['plazo']), esc(p['que']), esc(p['fundamento'])) for p in C['plazos'])
    return sec('ia-acciones', '⚖️', 'Qué significa cada acción y qué pasa después', '''
        <p class="ia-txt">Una observación no es una sentencia. Cada acción abre un camino distinto y con plazos que marca la ley. Las <b>preventivas</b> sugieren mejoras; las <b>correctivas</b> exigen aclarar, devolver o sancionar.</p>
        <div class="ia-acciones">%s</div>
        <h3 class="ia-sub">El reloj de la ley después de cada entrega</h3>
        <ol class="ia-plazos">%s</ol>
        <p class="ia-nota">%s %s. Cuando un pliego no se solventa, el caso pasa a investigación y, si hay falta grave, al Tribunal Federal de Justicia Administrativa; si hay delito, a la Fiscalía Especializada (LFRCF, art. 40). Para seguir casos concretos, abre los <a href="expedientes.html">Expedientes de casos por aclarar</a>.</p>''' % (
        tarjetas, plazos, chip('oficial'), fuente(C, 'LFRCF', 'arts. 33 a 42')))


def nueva(C, ref, prox):
    N = C['cp2025']
    st = N['estado']
    return sec('ia-2025', '🆕', 'La Cuenta Pública 2025: lo que ya salió', '''
        <p class="ia-txt">La primera entrega (%s) revisó un solo tema: <b>cómo se repartieron las participaciones federales</b>, el dinero de libre uso que la Federación entrega a los estados. %s</p>
        <div class="ia-datos">%s%s%s%s%s</div>
        <p class="ia-nota">%s %s %s. Los 33 informes, en el %s. %s</p>''' % (
        esc(N['corte']), esc(N['que']),
        dato(num(N['auditorias']), 'auditorías', st),
        dato(monto(N['muestra']), 'revisados', st, pct(N['representatividad'], 0) + ' del universo'),
        dato(num(N['acciones']), 'acciones', st, '%s recomendaciones y %s solicitud de aclaración' % (num(N['R']), num(N['SA']))),
        dato(pesos(N['porAclarar']), 'por aclarar', st),
        dato(pesos(N['recuperaciones']), 'recuperados', st),
        chip('oficial'), fuente(C, N['fuente'], N['pagina']), ref('ref-asf-mdb2025a'), fuente(C, 'IR2025A'),
        ('Lo que viene: la %s, el %s.' % (esc(minus(prox['titulo'])), fecha(prox['fecha']))) if prox else ''))


def documentos(C, ref):
    docs = ''.join('<li><a href="%s" target="_blank" rel="noopener">%s ↗</a>%s</li>'
                   % (esc(f['url']), esc(f['doc']), ('<code title="Huella SHA-256 del PDF">%s…</code>' % f['sha256'][:16]) if f.get('sha256') else '')
                   for f in C['fuentes'].values())
    return sec('ia-docs', '📚', 'Documentos y descarga', '''
        <p class="ia-txt">Cada cifra de la Auditoría Superior en esta aplicación sale de estos documentos. Puedes bajarlos y comprobarlos, o descargar la base por estado para abrirla en Excel.</p>
        <div class="ia-arr-acc">
          <button type="button" class="ia-boton ia-boton-pri" id="iaCSV" hidden>⬇️ Descargar CSV por estado</button>
          <a class="ia-boton" href="%s" target="_blank" rel="noopener">🔎 Buscar una auditoría en ASF Datos ↗</a>
          <a class="ia-boton" href="fuentes-oficiales.html#ref-asf-mdb2024">📑 Ver en el Catálogo de Fuentes</a>
        </div>
        <p class="ia-nota" id="iaCSVNota">El CSV trae, por estado y por quién gastó (gobierno del estado, municipios o alcaldías, y otros entes): auditorías, acciones, recuperado y por aclarar, en pesos, con la fuente al final. %s</p>
        <ol class="ia-docs">%s</ol>
        <p class="ia-nota">%s Consulta: %s. %s</p>''' % (
        esc(C['fuentes']['ASFDATOS']['url']), '<noscript>La descarga necesita JavaScript.</noscript>', docs,
        esc(C['nota']), esc(C['consulta']), ref('ref-asf-mdb2024')))


def _datos(C):
    S = C.get('serie') or []
    E = C['cp2024']['entidades']
    return {
        'ent': [{'e': e['entidad'], 'n': nombre(e['entidad']), 't': e['total'], 'd': e['desglose']} for e in E],
        'serie': [{k: r.get(k) for k in ('cp', 'porAclarar', 'observado', 'observadoEstado', 'recuperaciones', 'auditorias', 'PO', 'fuente', 'pagina')} for r in S],
        'met': [{'k': k, 'et': et, 'mdp': m} for k, et, m in METRICAS],
        'fuentes': {k: {'url': f['url'], 'doc': f['doc'], 'corto': f.get('corto') or f['doc']} for k, f in C['fuentes'].items()},
        'pagEnt': C['cp2024']['paginaEntidades'],
        'csvFuente': 'ASF, Matriz de Datos Básicos del Informe del Resultado de la Cuenta Pública 2024, tres entregas (consolidado), corte %s, pp. %s'
                     % (C['cp2024']['corte'], C['cp2024']['paginaEntidades']),
    }


def _au():
    import auditorias
    return auditorias


def capitulos(base, ref):
    """Los doce capitulos, en orden: slug de su pagina, ancla vieja (para
    los enlaces que aun traen #ia-...), icono, nombre corto del indice, cifra
    de la tarjeta, titulo de la pagina, entrada y cuerpo (None en el
    catalogo, que arma insp_nota)."""
    C = base['cuenta_publica_asf']
    T = C['cp2024']['total']
    N = C['cp2025']
    S = C.get('serie') or []
    prox = next((c for c in C['calendario'] if not c.get('hecho')), None)
    fed = C['cp2024']['federalizado']['porAclarar'] / T['porAclarar'] * 100
    def c(slug, ancla, ico, corto, cifra, titulo, entrada, cuerpo, con_datos=False):
        return {'slug': slug, 'ancla': ancla, 'ico': ico, 'corto': corto, 'cifra': cifra, 'titulo': titulo,
                'entrada': entrada, 'cuerpo': cuerpo, 'datos': con_datos}
    nexp = len(base['expedientes']['fichas'])
    return [
        c('casos', 'ex-casos', '📂', 'Los casos por aclarar', '%d expedientes' % nexp,
          'Expedientes de casos por aclarar',
          'Casos de alto impacto, contados con los informes de la Auditoría Superior de la Federación y el Sistema de Alertas de Hacienda: <b>cuánto dinero no se pudo comprobar, quién lo manejó y qué acciones se promovieron.</b>',
          None),
        # Pedido del autor, 23-10-2026: las investigaciones de la portada,
        # capítulo propio junto a los casos (auditorias.capitulo_inspector()).
        c('imagenes', 'ia-imagenes', '🖼️', 'Auditoría en imágenes', '%d investigaciones' % len(_au().AUDITORIAS),
          'Auditoría en imágenes',
          'Las investigaciones de la portada, contadas con imágenes: <b>cada una abre su página</b> y, si la Auditoría Superior la revisó, su expediente.',
          lambda: sec('ia-imagenes', '🖼️', 'Auditoría en imágenes', _au().capitulo_inspector())),
        c('autoridades', 'ia-autoridades', '🏛️', 'Quién fiscaliza', '%d autoridades' % len(fiscalizadores.AUTORIDADES),
          'Quién fiscaliza el dinero público',
          'La Auditoría Superior, la Secretaría Anticorrupción, los tribunales, la Fiscalía y las demás: qué revisa cada una y qué expediente oficial publica.',
          lambda: autoridades(ref)),
        c('calendario', 'ia-calendario', '📡', 'El seguimiento 2024–2027', ('Próxima: ' + fecha(prox['fecha'])) if prox else '',
          'Qué es la Cuenta Pública y el seguimiento de 2024 a 2027',
          'El presupuesto dice cuánto se <b>puede</b> gastar; la Cuenta Pública, cuánto se gastó de verdad. Aquí ves quién la revisa, en qué fechas, y lo que el agente de seguimiento encontró publicado.',
          lambda: calendario(C, prox)),
        c('cifras', 'ia-cifras', '🔎', 'La Cuenta Pública 2024 en cifras', num(T['auditorias']) + ' auditorías',
          'Lo que encontró la ASF en la Cuenta Pública 2024',
          'Cuántas auditorías hizo, cuánto revisó y qué acciones promovió en el ejercicio más reciente con sus tres entregas completas.',
          lambda: cifras(C)),
        c('serie', 'ia-serie', '📈', 'Seis años de revisiones', '%d a %d' % (S[0]['cp'], S[-1]['cp']) if S else '',
          'Seis años de revisiones: %d a %d' % (S[0]['cp'], S[-1]['cp']) if S else 'Seis años de revisiones',
          'Cada Cuenta Pública revisada, renglón por renglón, con su documento: elige qué cifra comparar.',
          lambda: serie(C), True),
        c('donde', 'ia-donde', '🏛️', 'Dónde se concentra', pct(fed, 0) + ' en estados y municipios',
          'Dónde se concentra lo que falta aclarar',
          'Por grupo de gasto y en los diez renglones con más monto por aclarar.',
          lambda: donde(C)),
        c('estado', 'ia-estado', '🗺️', 'Tu estado', '32 estados comparados',
          'Lo que la ASF le observó a tu estado',
          'Elige tu estado: cuántas auditorías tuvo, cuánto quedó por aclarar, quién gastó el dinero y en qué lugar queda de los 32.',
          lambda: estado(C), True),
        c('acciones', 'ia-acciones', '⚖️', 'Qué significa cada acción', num(T['PO']) + ' pliegos',
          'Qué significa cada acción y qué pasa después',
          'Una observación no es una sentencia. Cada acción abre un camino distinto, con los plazos que marca la ley.',
          lambda: acciones(C)),
        c('2025', 'ia-2025', '🆕', 'La Cuenta Pública 2025', num(N['auditorias']) + ' auditorías en la 1.ª entrega',
          'La Cuenta Pública 2025: lo que ya salió',
          'Lo que trae la primera entrega de la ASF sobre el gasto de 2025 y lo que viene después.',
          lambda: nueva(C, ref, prox)),
        c('catalogo', 'ia-catalogo', '📋', 'Catálogo de cifras oficiales', format(len(insp_nota.catalogo(base)), ',') + ' cifras con documento',
          'Catálogo de cifras oficiales',
          '<b>Catálogo de cifras oficiales.</b> Elige una cifra con su documento, escribe la que leíste en una nota y mide cuánto se aleja.',
          None),
        c('documentos', 'ia-docs', '📚', 'Documentos y descarga', 'CSV por estado',
          'Documentos y descarga',
          'Los documentos oficiales de donde sale cada cifra de esta aplicación, y la base por estado para abrirla en Excel.',
          lambda: documentos(C, ref), True),
    ]


def construir(base, ref):
    """La portada de la aplicacion: el arranque y el indice de capitulos."""
    C = base['cuenta_publica_asf']
    prox = next((c for c in C['calendario'] if not c.get('hecho')), None)
    return '\n      '.join([
        '<div class="ia">',
        arranque(C, ref, prox),
        '<div id="ia-indice">' + indice(capitulos(base, ref)) + '</div>',
        '</div>'])


def subpaginas(base, ref):
    """Para apartados.insp_subpaginas(): una pagina por capitulo, con
    anterior y siguiente entre capitulos (cap_nav)."""
    caps = capitulos(base, ref)
    datos = '<script type="application/json" id="iaDatos">%s</script>' % _json(_datos(base['cuenta_publica_asf']))
    out = []
    for k, cp in enumerate(caps):
        p = {'archivo': cap_archivo(cp['slug']), 'icono': cp['ico'], 'menu': cp['corto'], 'titulo': cp['titulo'],
             'lema': 'Expedientes de casos de la ASF · capítulo %d de %d' % (k + 1, len(caps)), 'entrada': cp['entrada'],
             'cap_nav': tuple((cap_archivo(x['slug']), x['corto']) if x else None
                              for x in (caps[k - 1] if k else None, caps[k + 1] if k + 1 < len(caps) else None)) + (len(caps),)}
        if cp['slug'] == 'casos':
            p.update({'bloque': expedientes.bloque(), 'estilos': list(expedientes.ESTILOS), 'scripts': list(expedientes.SCRIPTS)})
        elif cp['cuerpo'] is None:
            p.update({'bloque': insp_nota.catalogo_pagina(base, ref), 'estilos': ['insp-nota.css'], 'scripts': ['insp-nota.js']})
        else:
            p['bloque'] = '\n      '.join(['<div class="ia ia-cap">', cp['cuerpo'](), datos if cp['datos'] else '', '</div>'])
        out.append(p)
    return out
