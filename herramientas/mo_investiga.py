# -*- coding: utf-8 -*-
"""Inversion y Megaobras, aplicacion 1: «Haz tu propia investigacion»
(pedido del autor, 21-10-2026).

El cuadro con que abria la portada de la herramienta se volvio aplicacion
con pagina propia. El autor pidio que el lector pueda hacer su propia
investigacion de lo que invirtio cada sexenio, el resultado de cada obra,
sus estados de resultados, lo que nos sigue costando, el dano ambiental y
los rescates, de forma digerible. Aqui va en tres pasos: elige un
presidente (o los seis), elige una pregunta y lee la respuesta, con su
estado y el enlace a la aplicacion donde se investiga a fondo.

No hay cifra nueva. Todo sale de simulador_megaobras, con las mismas
funciones que pintan las otras aplicaciones:

- costo, aprobado y sobrecosto: los campos de la obra (mo_tabla._cifra);
- gana o pierde: la medida unica de la herramienta (mo_base.resultados);
- al mes y al dia: resultado del año ÷ 12 y ÷ 365 (derivado, dicho asi);
- las obras de construccion: am_basura.OBRAS_FISICAS.

Las 42 respuestas (7 opciones por 6 preguntas) se escriben aqui, en la
pagina; mo-investiga.js solo muestra la que elegiste.
"""
import html

from presupuesto_modulos import chip
import am_basura
import mo_base
import mo_capitulos
import mo_pulso
import mo_tabla
from mo_sexenios import SEXENIOS

ESTILOS = ['mo-tabla.css', 'mo-investiga.css', 'mo-pulso.css']
SCRIPTS = ['mo-tabla.js', 'mo-investiga.js']

ARCHIVO = 'herramienta-megaobras-investiga.html'
TABLA = 'herramienta-megaobras-tabla.html'
SECTOR = 'herramienta-megaobras-sector.html'
CIFRAS = 'herramienta-megaobras-cero.html'
CUENTA = 'herramienta-megaobras-pulso-cuenta.html'
AMBIENTE = 'herramienta-ambiente-basura.html#abMegaobras'

# (clave, icono, pregunta)
PREGUNTAS = [
    ('invirtio', '🏛️', '¿En qué invirtió?'),
    ('gana', '🚦', '¿Gana o pierde hoy?'),
    ('resultados', '📒', '¿Cuál es su estado de resultados?'),
    ('cuesta', '⏱️', '¿Cuánto nos sigue costando?'),
    ('rescates', '🏦', '¿Hubo rescates?'),
    ('ambiente', '🌎', '¿Qué huella ambiental deja?'),
]


def esc(t):
    return html.escape(str(t if t is not None else ''), quote=True)


mdp = mo_pulso.mdp
sim_mdp = mo_pulso.sim_mdp


def _signo_txt(v):
    return ('−' if v < 0 else '+') + mdp(abs(v))


def _ir(href, txt):
    return '<p class="mi-ir"><a class="mi-ir-a" href="%s">%s <span aria-hidden="true">→</span></a></p>' % (href, esc(txt))


def _obra_cab(o, sectores):
    sec = sectores.get(o['sector_id']) or {}
    return ('<span class="mi-o-ico" aria-hidden="true">%s</span><span class="mi-o-n"><b>%s</b><small>%s · %s</small></span>'
            % (o['icono'], esc(o['nombre']), esc(sec.get('nombre', '')), esc(o.get('estatus') or '')))


def _invirtio(obs, sectores, ancla):
    if not obs:
        return None
    costo = sum(o['inversion_real_mdp'] for o in obs)
    filas = ''.join(
        '<li class="mi-o">%s<dl class="mi-dl"><div><dt>%s</dt><dd>%s</dd></div><div><dt>%s</dt><dd>%s</dd></div>'
        '<div><dt>%s</dt><dd>%s</dd></div></dl></li>'
        % (_obra_cab(o, sectores),
           'Presentado en su momento' if o.get('tipo') == 'rescate' else 'Aprobado', mo_tabla._cifra(o, 'inversion_presupuestada_mdp', mdp),
           'Pagado y debido' if o.get('tipo') == 'rescate' else 'Costo real', mo_tabla._cifra(o, 'inversion_real_mdp', mdp),
           esc(o.get('sobrecosto_etiqueta') or 'Sobrecosto'), mo_tabla._cifra(o, 'sobrecosto_pct', mo_tabla._pct))
        for o in obs)
    return ('<p class="mi-res-lead"><b>%d obra%s</b> con un costo registrado de <b class="mt-num">%s</b> %s '
            '<small>(suma del costo de cada una; los rescates se suman solo como referencia).</small></p><ol class="mi-obras">%s</ol>%s'
            % (len(obs), '' if len(obs) == 1 else 's', sim_mdp(costo), chip('derivado'), filas,
               _ir(ancla, 'Investiga a fondo en «En qué invirtió cada presidente»')))


def _gana(obs, sectores, res, ancla):
    if not obs:
        return None
    dat = [res[o['id']]['v'] for o in obs if res[o['id']]['tipo'] == 'dato']
    lead = (('<p class="mi-res-lead">Las %d obras que publican su resultado suman <b class="mt-num %s">%s al año</b> %s.</p>'
             % (len(dat), mo_tabla._signo(sum(dat)), _signo_txt(sum(dat)), chip('derivado'))) if dat else
            '<p class="mi-res-lead">Ninguna de estas obras publica su ganancia o pérdida del año: cada una dice por qué falta.</p>')
    filas = ''.join('<li class="mi-o">%s<div class="mt-res-caja">%s</div></li>'
                    % (_obra_cab(o, sectores), mo_tabla._celda_res(res[o['id']], o['id'])) for o in obs)
    return lead + '<ol class="mi-obras">%s</ol>' % filas + _ir(ancla, 'Mira la tabla general en vivo')


def _resultados(obs, sectores, res, cuenta):
    if not obs:
        return None
    filas = []
    for o in obs:
        rr = cuenta.get(o['id']) or []
        n = {e: sum(1 for f in rr if f['e'] == e) for e in ('oficial', 'derivado', 'pendiente', 'no_aplica')}
        r = res[o['id']]
        if r['tipo'] == 'dato':
            linea = '%s al año (%s) %s' % ('Gana ' + mdp(r['v']) if r['v'] > 0 else 'Pierde ' + mdp(abs(r['v'])), r['anio'], chip(r['e']))
            clase = mo_tabla._signo(r['v'])
        elif r['tipo'] == 'no_aplica':
            linea, clase = esc(r['txt']), 'mt-cero'
        else:
            linea, clase = 'Sin resultado publicado %s' % chip('pendiente', 'cuenta-' + o['id']), 'mt-cero'
        filas.append('<li class="mi-o">%s<p class="mi-o-res %s">%s</p>'
                     '<p class="mi-o-pie">Su cuenta tiene %d renglones: %d con documento, %d calculados, %d pendientes y %d que no aplican. '
                     '<a href="%s#cuenta-%s">Abre su estado de resultados</a></p></li>'
                     % (_obra_cab(o, sectores), clase, linea, len(rr), n['oficial'], n['derivado'], n['pendiente'], n['no_aplica'], CUENTA, o['id']))
    return ('<p class="mi-res-lead">El estado de resultados de cada obra: lo que se esperaba de ella, lo que ingresa, lo que gasta en operar, '
            'lo que paga de intereses y si gana o pierde en el año, renglón por renglón y con su documento.</p><ol class="mi-obras">%s</ol>%s'
            % (''.join(filas), _ir(CUENTA + '#mpCuenta', 'Abre «La cuenta de cada obra»')))


def _cuesta(obs, res):
    if not obs:
        return None
    dat = [(o, res[o['id']]) for o in obs if res[o['id']]['tipo'] == 'dato']
    sin = [o for o in obs if res[o['id']]['tipo'] == 'pendiente']
    if not dat:
        cuerpo = '<p class="mi-res-lead">Ninguna de estas obras publica su ganancia o pérdida del año, así que no se puede decir cuánto nos sigue costando: no se estima.</p>'
    else:
        v = sum(r['v'] for _o, r in dat)
        verbo = 'nos siguen costando' if v < 0 else 'dejan'
        cuerpo = ('<p class="mi-res-lead">Con su resultado más reciente publicado, estas %d obras %s:</p>'
                  '<div class="mi-ritmo"><p><span>Al año</span><b class="mt-num %s">%s</b></p>'
                  '<p><span>Al mes <small>(÷ 12)</small></span><b class="mt-num %s">%s</b></p>'
                  '<p><span>Al día <small>(÷ 365)</small></span><b class="mt-num %s">%s</b></p></div>'
                  '<p class="mi-nota">%s Suma de los resultados de: %s.</p>'
                  '<p class="mt-res-vivo">Desde que abriste esta página: %s</p>'
                  % (len(dat), verbo, mo_tabla._signo(v), _signo_txt(v), mo_tabla._signo(v), _signo_txt(v / 12),
                     mo_tabla._signo(v), _signo_txt(v / 365), chip('derivado'),
                     esc('; '.join('%s %s (%s)' % (o['nombre'].split(' (')[0], _signo_txt(r['v']), r['anio']) for o, r in dat)),
                     mo_tabla._vivo(v)))
    if sin:
        cuerpo += ('<p class="mi-nota">Fuera de la suma, porque no publican su resultado: %s. No quiere decir que cuesten cero. %s</p>'
                   % (esc(', '.join(o['nombre'].split(' (')[0] for o in sin)), chip('pendiente', 'cuenta-' + sin[0]['id'])))
    return cuerpo + _ir(CUENTA + '#mpRitmo', 'Elige el ritmo en «El ritmo de la pérdida»')


def _rescates(obs, todas, sectores, res, quien):
    resc = [o for o in obs if o.get('tipo') == 'rescate']
    if not resc:
        otros = sorted({quien[o['id']] for o in todas if o.get('tipo') == 'rescate'})
        return ('<p class="mi-res-lead">En este sexenio no hay rescates evaluados. Los %d rescates del registro se cuentan con %s, que los hizo.</p>%s'
                % (sum(1 for o in todas if o.get('tipo') == 'rescate'), esc(' y '.join(otros)),
                   _ir(CIFRAS + '#mpRescates', 'Ve los rescates en «Las cuatro cifras y los rescates»')))
    filas = ''.join(
        '<li class="mi-o">%s<dl class="mi-dl"><div><dt>Presentado en su momento</dt><dd>%s</dd></div>'
        '<div><dt>Pagado y debido</dt><dd>%s</dd></div><div><dt>%s</dt><dd>%s</dd></div></dl>'
        '<div class="mt-res-caja">%s</div></li>'
        % (_obra_cab(o, sectores), mo_tabla._cifra(o, 'inversion_presupuestada_mdp', mdp), mo_tabla._cifra(o, 'inversion_real_mdp', mdp),
           esc(o.get('sobrecosto_etiqueta') or 'Crecimiento'), mo_tabla._cifra(o, 'sobrecosto_pct', mo_tabla._pct),
           mo_tabla._celda_res(res[o['id']], o['id']))
        for o in resc)
    return ('<p class="mi-res-lead">Un rescate no es una obra: es una deuda que el Estado asumió para salvar a bancos o a concesionarios. '
            'Por eso su «costo» es lo pagado y lo debido, y su crecimiento no se compara con el sobrecosto de una obra.</p>'
            '<ol class="mi-obras">%s</ol>%s' % (filas, _ir(CIFRAS + '#mpRescates', 'Investiga a fondo en «Las cuatro cifras y los rescates»')))


def _ambiente(obs, sectores):
    fis = [o for o in obs if o['id'] in am_basura.OBRAS_FISICAS]
    if not obs:
        return None
    if not fis:
        return ('<p class="mi-res-lead">Ninguna de estas obras es obra de construcción: los rescates, las compras de empresas y los programas no piden '
                'permiso ambiental. La huella de las que sí lo piden está en Costo Ambiental.</p>%s' % _ir(AMBIENTE, 'Abre «La huella de las megaobras»'))
    filas = ''.join('<li class="mi-o">%s<p class="mi-o-pie">Costo registrado: %s</p></li>'
                    % (_obra_cab(o, sectores), mo_tabla._cifra(o, 'inversion_real_mdp', mdp)) for o in fis)
    return ('<p class="mi-res-lead">%d obra%s de construcción: necesitaba%s una Manifestación de Impacto Ambiental aprobada por la SEMARNAT antes de empezar '
            '(Ley General del Equilibrio Ecológico, artículo 28). Lo que su permiso autorizó y lo que se documentó después se integra en Costo Ambiental, '
            'con su porqué donde todavía falta.</p><ol class="mi-obras">%s</ol>%s'
            % (len(fis), '' if len(fis) == 1 else 's', '' if len(fis) == 1 else 'n', filas, _ir(AMBIENTE, 'Abre «La huella de las megaobras»')))


def construir(base, ref):
    sm, sectores, res, grupos, todos = mo_tabla._datos(base)
    cuenta = (sm.get('cuenta') or {}).get('obras') or {}
    quien = {o['id']: g['corto'] for g in grupos for o in g['obras']}
    opciones = [('todos', 'Los seis', 1988, 2024, '#0b2a63', [o for g in grupos for o in g['obras']], TABLA + '#mtResTit')]
    opciones += [(g['clave'], g['corto'], g['a0'], g['a1'], g['color'], g['obras'], TABLA + '#mt-sx-' + g['clave']) for g in grupos]
    paneles = []
    for k, nom, a0, a1, color, obs, ancla in opciones:
        for q, ico, preg in PREGUNTAS:
            if q == 'invirtio':
                cuerpo = _invirtio(obs, sectores, ancla)
            elif q == 'gana':
                cuerpo = _gana(obs, sectores, res, ancla)
            elif q == 'resultados':
                cuerpo = _resultados(obs, sectores, res, cuenta)
            elif q == 'cuesta':
                cuerpo = _cuesta(obs, res)
            elif q == 'rescates':
                cuerpo = _rescates(obs, sm['obras'], sectores, res, quien)
            else:
                cuerpo = _ambiente(obs, sectores)
            if cuerpo is None:
                cuerpo = ('<p class="mi-res-lead">Este sexenio no tiene obras evaluadas. Las concesiones carreteras que fracasaron se otorgaron con él, '
                          'pero se rescataron y se pagaron desde 1997: ese rescate (el FARAC) se cuenta con Ernesto Zedillo, que lo hizo.</p>%s'
                          % _ir(TABLA + '#mxLinea', 'Ve la línea del tiempo'))
            paneles.append('<article class="mi-panel" id="inv-%s-%s" data-sx="%s" data-q="%s" style="--sx:%s" tabindex="-1"%s>'
                           '<h3 class="mi-panel-tit"><small>%s · %d–%d</small> <span aria-hidden="true">%s</span> %s</h3>%s</article>'
                           % (k, q, k, q, color, '' if (k, q) == ('todos', 'invirtio') else ' hidden',
                              esc(nom), a0, a1, ico, esc(preg), cuerpo))
    b_sx = ''.join('<button type="button" class="mi-b" data-sx="%s" aria-pressed="%s" style="--sx:%s">%s<small>%d–%d</small></button>'
                   % (k, 'true' if k == 'todos' else 'false', color, esc(nom), a0, a1) for k, nom, a0, a1, color, _o, _a in opciones)
    b_q = ''.join('<button type="button" class="mi-b mi-b-q" data-q="%s" aria-pressed="%s"><span aria-hidden="true">%s</span> %s</button>'
                  % (q, 'true' if q == 'invirtio' else 'false', ico, esc(preg)) for q, ico, preg in PREGUNTAS)
    accesos = ''.join('<li><a href="#inv-todos-%s" data-ir-q="%s"><span aria-hidden="true">%s</span> %s</a></li>' % (q, q, ico, esc(preg))
                      for q, ico, preg in PREGUNTAS)
    return mo_pulso.cajon_calculo(base, ref) + '''<div class="mt mi" id="mtRaiz">
  <section class="mt-arranque" aria-labelledby="miArrTit">
    <p class="mt-kicker">{kicker}</p>
    <h2 class="mt-grande" id="miArrTit">Haz tu propia investigación de las megaobras</h2>
    <p class="mt-lead">Con filtros, contadores, simuladores y tablas, recorre lo que invirtió cada presidente de 1988 a 2024, cuánto costó cada obra frente a lo aprobado, si hoy gana o pierde, su estado de resultados, lo que nos sigue costando, los rescates y la huella ambiental. Cada cifra trae su documento oficial y su estado: {chip_of}, {chip_der} o {chip_pend}.</p>
    <ul class="mt-investiga" aria-label="Lo que puedes investigar">{accesos}</ul>
  </section>

  <section class="mi-pasos" aria-labelledby="miPasosTit">
    <h2 class="mt-tit" id="miPasosTit"><span aria-hidden="true">🔍</span> Tu investigación en tres pasos</h2>
    <div class="mi-paso">
      <p class="mi-paso-et"><span class="mi-n">1</span> Elige a quién investigas</p>
      <div class="mi-bs" role="group" aria-label="Presidente">{b_sx}</div>
    </div>
    <div class="mi-paso">
      <p class="mi-paso-et"><span class="mi-n">2</span> Elige qué quieres saber</p>
      <div class="mi-bs" role="group" aria-label="Pregunta">{b_q}</div>
    </div>
    <div class="mi-paso mi-paso-res">
      <p class="mi-paso-et"><span class="mi-n">3</span> Lee la respuesta y síguela hasta su documento</p>
      <div class="mi-res" aria-live="polite">
        {paneles}
      </div>
      <p class="mi-acc"><button type="button" class="mt-boton mi-copiar" id="miCopiar"><span aria-hidden="true">🔗</span> Copia el enlace de esta respuesta</button> <span class="mi-copiado" id="miCopiado" aria-live="polite"></span></p>
    </div>
  </section>

  <aside class="mt-nota">
    <p>{medida}</p>
    <p><b>Cómo leer las respuestas.</b> No hay una cifra nueva: cada respuesta sale de las mismas obras y documentos de las otras cuatro aplicaciones, y cada una te lleva a la aplicación donde se investiga a fondo. Las cifras son nominales, sin quitar la inflación. «Al mes» y «al día» son el resultado del año ÷ 12 y ÷ 365 {chip_der}. Lo que falta está en el <a href="pendientes.html#tema-megaobras">Registro de pendientes</a>, con el nombre de quien debe publicarlo.</p>
  </aside>
</div>'''.format(
        kicker=mo_capitulos.kicker(ARCHIVO), chip_of=chip('oficial'), chip_der=chip('derivado'), chip_pend=chip('pendiente'),
        accesos=accesos, b_sx=b_sx, b_q=b_q, paneles='\n        '.join(paneles), medida=mo_base.medida_txt(sm))
