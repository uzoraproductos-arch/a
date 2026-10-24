# -*- coding: utf-8 -*-
"""Costo Ambiental, aplicacion 5: «Auditor ambiental» (pedido del autor,
22-10-2026: «replicando cierto tipo de aplicaciones que estaban en modo
inspector [...] pero respecto al medio ambiente»).

Como el Auditor de entes publicos del Modo Inspector, pero para el sector
ambiental: el lector elige el Ramo 16 completo o uno de sus siete organos y
ve su ficha, con lo que publican Hacienda y la Auditoria Superior:

  - el dinero de 2026: aprobado (PEF 2026), modificado y pagado al 30 de
    junio (avance del 2.o trimestre), y el avance del pago (derivado);
  - lo que pide para 2027 (proyecto de PEF 2027) y su cambio nominal;
  - su peso en el ramo;
  - del ramo completo, la Cuenta Publica 2025 (original contra ejercido) y
    lo pagado contra lo calendarizado al corte (inspector_federal);
  - lo que observo la ASF en el sector Medio Ambiente y Recursos Naturales
    (Matriz de Datos Basicos de la Cuenta Publica 2024) y, de la Conagua, su
    expediente del acueducto El Cuchillo II;
  - las preguntas que la ficha deja abiertas, escritas a partir de las
    cifras (no son juicios: son lo que un auditor ciudadano preguntaria).

Todas las cifras se escriben aqui con su chip y su fuente; el JS
(am-auditor.js) solo cambia de ficha, arma el CSV y copia el enlace.

Regla de la plataforma (AGENTS.md, §2): la ASF publica sus cifras por
sector, no por organo; la ficha de cada organo lo dice y muestra las del
sector, sin repartirlas.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['amauditor']).
"""
import html
import json

from presupuesto_modulos import chip

ESTILOS = ['am-auditor.css']
SCRIPTS = ['am-auditor.js']
SECTOR_ASF = 'Medio Ambiente y Recursos Naturales'
# Siglas para el selector y la ficha.
SIGLAS = {'B00': 'Conagua', 'RHQ': 'CONAFOR', 'F00': 'CONANP', 'E00': 'PROFEPA', 'G00': 'ASEA', 'RJJ': 'INECC',
          'RESTO': 'SEMARNAT central'}
ICONOS = {'RAMO': '🌎', 'B00': '💧', 'RHQ': '🌲', 'F00': '🦋', 'E00': '⚖️', 'G00': '🛢️', 'RJJ': '🌡️', 'RESTO': '🏛️'}


def esc(t):
    return html.escape(str(t if t is not None else ''), quote=True)


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def n(v, d=0):
    return format(v, ',.%df' % d)


def mdp(pesos):
    return '$' + n(pesos / 1e6, 1) + ' mdp'


def pct(v):
    return n(v, 1) + ' %'


def signo(v, suf=' %'):
    return ('+' if v >= 0 else '−') + n(abs(v), 1) + suf


def _liga(url, texto):
    return '<a class="aa-fu" href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>' % (esc(url), esc(texto))


def _dato(valor, rotulo, estado, pie=''):
    return ('<div class="aa-dato"><strong class="aa-num">%s</strong><span class="aa-dato-r">%s %s</span>%s</div>'
            % (valor, rotulo, chip(estado), ('<small>%s</small>' % pie) if pie else ''))


def construir(base, ref):
    A = base['ambiente']
    P, F = A['presupuesto'], A['fuentes']
    sem = next(e for e in base['inspector_federal']['entes'] if e['id'] == 'semarnat')
    IF = base['inspector_federal']['fuentes']
    cpa = base['cuenta_publica_asf']
    sector = next(s for g in cpa['cp2024']['grupos'] for s in g.get('sectores', []) if s['nombre'] == SECTOR_ASF)
    asf_fu = cpa['fuentes'][cpa['cp2024']['fuente']]
    exp = next((x for x in base['expedientes']['fichas'] if x['id'] in sem.get('expedientes', [])), None)

    f_pef = _liga(F['PEF']['url'], F['PEF'].get('corto') or F['PEF']['doc'])
    f_av = _liga(F['AV2T2026']['url'], F['AV2T2026'].get('corto') or F['AV2T2026']['doc'])
    f_pp = _liga(F['PPEF2027']['url'], F['PPEF2027'].get('corto') or F['PPEF2027']['doc'])
    f_asf = _liga(asf_fu['url'], asf_fu['corto'])
    f_cp = _liga(IF['cp2025']['url'], IF['cp2025']['corto'])
    f_cal = _liga(IF['av2026']['url'], IF['av2026']['corto'])
    tot_ap = P['aprobado2026']['valor']

    ramo = {'ur': 'RAMO', 'nombre': 'Ramo %s completo: %s' % (P['ramo'], P['nombre']),
            'aprobado': tot_ap, 'modificado': P['modificado2026']['valor'], 'pagado': P['pagado2026']['valor'],
            'proyecto2027': P['proyecto2027']['valor']}
    orgs = [ramo] + list(P['unidades'])
    assert abs(sum(u['aprobado'] for u in P['unidades']) - tot_ap) < 1, 'Los órganos deben sumar el ramo'

    fichas, csv, botones = [], {}, []
    for u in orgs:
        ur, es_ramo = u['ur'], u['ur'] == 'RAMO'
        sig = 'Ramo %s' % P['ramo'] if es_ramo else SIGLAS.get(ur, ur)
        av = u['pagado'] / u['modificado'] * 100 if u['modificado'] else 0
        mov = u['modificado'] - u['aprobado']
        mov_p = mov / u['aprobado'] * 100 if u['aprobado'] else 0
        c27 = (u['proyecto2027'] / u['aprobado'] - 1) * 100 if u['aprobado'] else 0
        peso = u['aprobado'] / tot_ap * 100
        filas = [('Aprobado 2026 (pesos)', u['aprobado'], 'oficial', F['PEF']['url']),
                 ('Modificado 2026 (pesos)', u['modificado'], 'oficial', F['AV2T2026']['url']),
                 ('Pagado al 30 de junio de 2026 (pesos)', u['pagado'], 'oficial', F['AV2T2026']['url']),
                 ('Avance del pago, % (pagado / modificado x 100)', round(av, 2), 'derivado', ''),
                 ('Proyecto 2027 (pesos)', u['proyecto2027'], 'oficial', F['PPEF2027']['url']),
                 ('Cambio 2027 contra 2026, % nominal ((proyecto / aprobado - 1) x 100)', round(c27, 2), 'derivado', '')]

        # El dinero de 2026
        dinero = (
            _dato(mdp(u['aprobado']), 'aprobado para 2026', 'oficial', f_pef) +
            _dato(mdp(u['modificado']), 'modificado al 30 de junio', 'oficial',
                  '%s (%s) contra lo aprobado %s · %s' % (('+' if mov >= 0 else '−') + mdp(abs(mov)), signo(mov_p), chip('derivado'), f_av)) +
            _dato(mdp(u['pagado']), 'pagado al 30 de junio', 'oficial', f_av) +
            _dato(pct(av), 'avance del pago', 'derivado', 'pagado ÷ modificado × 100'))
        ritmo = av - 50
        barra = ('<div class="aa-avance" role="img" aria-label="Avance del pago: %s; a medio año, un ritmo parejo daría cerca del 50 %%">'
                 '<span class="aa-avance-b" style="--aa-w:%.4f"></span><span class="aa-avance-m" aria-hidden="true"></span></div>'
                 '<p class="aa-nota">La raya marca el 50 %%: a medio año, un ritmo parejo daría cerca de esa mitad. Lleva %s, '
                 '%s puntos %s de esa mitad %s.</p>'
                 % (pct(av), min(av, 100) / 100, pct(av), n(abs(ritmo), 1), 'por encima' if ritmo >= 0 else 'por debajo', chip('derivado')))

        extra = ''
        if es_ramo:
            cp = sem['cp2025']
            ej_p = cp['ejercido'] / cp['original'] * 100
            cal = sem['av2026']['calendarioAlCorte']
            cal_p = sem['av2026']['pagado'] / cal * 100
            extra = '''
        <h4 class="aa-sub">Cómo le fue en 2025 y cómo va contra su calendario</h4>
        <div class="aa-datos">%s%s%s%s</div>''' % (
                _dato('$' + n(cp['original'], 1) + ' mdp', 'aprobado original 2025', 'oficial', f_cp),
                _dato('$' + n(cp['ejercido'], 1) + ' mdp', 'ejercido en 2025', 'oficial',
                      '%s de lo aprobado (ejercido ÷ original × 100) %s' % (pct(ej_p), chip('derivado'))),
                _dato('$' + n(cal, 1) + ' mdp', 'calendarizado al 30 de junio de 2026', 'oficial', f_cal),
                _dato(pct(cal_p), 'de lo calendarizado ya se pagó', 'derivado',
                      'pagado ($%s mdp) ÷ calendarizado × 100 · %s' % (n(sem['av2026']['pagado'], 1), f_cal)))
            filas += [('Cuenta Pública 2025, original (millones de pesos)', cp['original'], 'oficial', IF['cp2025']['url']),
                      ('Cuenta Pública 2025, ejercido (millones de pesos)', cp['ejercido'], 'oficial', IF['cp2025']['url']),
                      ('Calendarizado al 30-jun-2026 (millones de pesos)', cal, 'oficial', IF['av2026']['url']),
                      ('Pagado / calendarizado, %', round(cal_p, 2), 'derivado', '')]

        # 2027 y su peso
        futuro = (_dato(mdp(u['proyecto2027']), 'propuesto para 2027', 'oficial', f_pp) +
                  _dato(signo(c27), 'contra lo aprobado en 2026', 'derivado', '(proyecto ÷ aprobado − 1) × 100, en pesos nominales: no descuenta la inflación') +
                  ('' if es_ramo else _dato(pct(peso), 'del Ramo %s aprobado' % esc(P['ramo']), 'derivado',
                                            'aprobado del órgano ÷ aprobado del ramo × 100')))
        filas.append(('Peso en el ramo, %', round(peso, 2), 'derivado', '') if not es_ramo else ('', '', '', ''))

        # La Auditoria Superior
        asf = ('<p class="aa-txt">%s</p><div class="aa-datos">%s%s%s%s</div><p class="aa-nota">%s %s</p>' % (
            ('La Auditoría Superior publica sus cifras por sector, no por órgano: estas son las del sector %s completo, '
             'al que pertenece este órgano.' % SECTOR_ASF) if not es_ramo else
            'Lo que la Auditoría Superior revisó del sector %s en la Cuenta Pública 2024.' % SECTOR_ASF,
            _dato(n(sector['auditorias']), 'auditorías al sector', 'oficial', f_asf),
            _dato(n(sector['acciones']), 'acciones promovidas', 'oficial', '%s de ellas, pliegos de observaciones · %s' % (n(sector['PO']), f_asf)),
            _dato(mdp(sector['porAclarar']), 'por aclarar', 'oficial', f_asf),
            _dato(mdp(sector['recuperaciones']), 'recuperado', 'oficial', f_asf),
            esc(cpa['nota']), 'Corte: %s.' % esc(cpa['cp2024']['corte'])))
        filas += [('ASF, sector %s, CP 2024: auditorías' % SECTOR_ASF, sector['auditorias'], 'oficial', asf_fu['url']),
                  ('ASF, sector %s, CP 2024: por aclarar (pesos)' % SECTOR_ASF, sector['porAclarar'], 'oficial', asf_fu['url'])]
        if exp and (es_ramo or ur == 'B00'):
            anios = ''.join('<li><b>Cuenta Pública %d:</b> %s por aclarar · %d acciones, %d pliegos de observaciones %s</li>'
                            % (a['cp'], mdp(a['porAclarar']), a['acciones'], a['PO'], chip('oficial')) for a in exp['anios'])
            asf += ('<div class="aa-exp"><p class="aa-exp-t"><span aria-hidden="true">%s</span> %s</p><p class="aa-txt">%s</p>'
                    '<ul class="aa-exp-l">%s</ul><p class="aa-acciones"><a class="aa-boton aa-sec" href="expedientes.html#exp-%s">'
                    'Abrir el expediente completo ➔</a></p></div>'
                    % (exp['icono'], esc(exp['titulo']), esc(exp['hallazgo']), anios, esc(exp['id'])))

        # Las preguntas que deja la ficha
        preg = []
        if av < 45:
            preg.append('A mitad de año lleva pagado %s de su presupuesto. ¿Qué parte de lo programado no se ha pagado y por qué?' % pct(av))
        elif av > 55:
            preg.append('A mitad de año ya pagó %s de su presupuesto. ¿Qué pagos adelantó y le alcanzará para el segundo semestre?' % pct(av))
        if abs(mov_p) >= 1:
            preg.append('Su presupuesto se %s %s respecto de lo que aprobó la Cámara. ¿Quién autorizó la adecuación y a qué se destinó?'
                        % ('amplió' if mov > 0 else 'redujo', pct(abs(mov_p))))
        if c27 < 0:
            preg.append('El proyecto 2027 le asigna %s menos en pesos nominales. ¿Qué programas dejarían de hacerse?' % pct(abs(c27)))
        else:
            preg.append('El proyecto 2027 le asigna %s más en pesos nominales. ¿En qué se usaría el aumento y con qué metas?' % pct(c27))
        preg.append('La Auditoría Superior dejó %s por aclarar en el sector en la Cuenta Pública 2024. ¿Ya se solventaron?' % mdp(sector['porAclarar']))
        preguntas = ''.join('<li>%s</li>' % esc(p) for p in preg)

        fichas.append('''
    <article class="aa-ficha" id="aa-%(ur)s" data-ur="%(ur)s"%(oculta)s aria-labelledby="aaT-%(ur)s">
      <header class="aa-ficha-cab"><span class="aa-ficha-ico" aria-hidden="true">%(ico)s</span>
        <div><p class="aa-ficha-k">%(clave)s</p><h3 class="aa-ficha-t" id="aaT-%(ur)s">%(nombre)s</h3></div></header>
      <section class="aa-blq"><h4 class="aa-sub">💵 El dinero de 2026</h4><div class="aa-datos">%(dinero)s</div>%(barra)s%(extra)s</section>
      <section class="aa-blq"><h4 class="aa-sub">📅 Lo que se propone para 2027</h4><div class="aa-datos">%(futuro)s</div>
        <p class="aa-nota">%(nota27)s</p></section>
      <section class="aa-blq"><h4 class="aa-sub">🔎 Lo que observó la Auditoría Superior</h4>%(asf)s</section>
      <section class="aa-blq aa-preg"><h4 class="aa-sub">❓ Las preguntas que deja esta ficha</h4>
        <p class="aa-txt">Salen de sus propias cifras. No son acusaciones: son lo que un auditor ciudadano preguntaría.</p>
        <ol class="aa-preg-l">%(preguntas)s</ol></section>
    </article>''' % {
            'ur': ur, 'oculta': '' if es_ramo else ' hidden', 'ico': ICONOS.get(ur, '🏛️'),
            'clave': ('Unidad responsable %s · %s' % (ur, esc(sig))) if ur not in ('RAMO', 'RESTO') else esc(sig),
            'nombre': esc(u['nombre']), 'dinero': dinero, 'barra': barra, 'extra': extra, 'futuro': futuro,
            'nota27': esc(P['proyecto2027'].get('nota', '')), 'asf': asf, 'preguntas': preguntas})
        csv[ur] = {'n': u['nombre'], 'f': [list(f) for f in filas if f[0]]}
        botones.append('<button type="button" class="aa-org" role="radio" data-ur="%s" aria-checked="%s">'
                       '<span class="aa-org-ico" aria-hidden="true">%s</span><span class="aa-org-tx"><b>%s</b><small>%s</small></span></button>'
                       % (ur, 'true' if es_ramo else 'false', ICONOS.get(ur, '🏛️'), esc(sig),
                          'Todo el sector' if es_ramo else mdp(u['aprobado']) + ' en 2026'))

    return '''<div class="aa" id="aaRaiz">
  <section class="aa-arranque" aria-labelledby="aaArrTit">
    <p class="aa-kicker">Costo Ambiental · aplicación 5</p>
    <h2 class="aa-grande" id="aaArrTit">Audita el dinero del medio ambiente</h2>
    <p class="aa-txt">Elige el sector completo o uno de sus siete órganos y revisa su ficha: cuánto le aprobó la Cámara, cuánto lleva pagado, cuánto se le propone para 2027 y qué encontró la Auditoría Superior. Cada cifra trae su documento, y al final, las preguntas que deja abiertas.</p>
  </section>

  <section class="aa-sec" aria-labelledby="aaSelTit">
    <h2 class="aa-tit" id="aaSelTit"><span class="aa-n">1</span> Elige a quién auditar</h2>
    <div class="aa-orgs" id="aaOrgs" role="radiogroup" aria-label="Órgano del sector ambiental">%(botones)s</div>
  </section>

  <section class="aa-sec" aria-labelledby="aaFichaTit">
    <h2 class="aa-tit" id="aaFichaTit"><span class="aa-n">2</span> Su ficha</h2>
    <div id="aaFichas" aria-live="polite">%(fichas)s
    </div>
    <p class="aa-acciones"><button type="button" class="aa-boton" id="aaCsv"><span aria-hidden="true">⬇️</span> Descargar esta ficha en CSV</button>
      <button type="button" class="aa-boton aa-sec" id="aaLiga"><span aria-hidden="true">🔗</span> Copiar el enlace de esta ficha</button></p>
    <p class="aa-nota" id="aaCopiado" aria-live="polite"></p>
  </section>

  <aside class="aa-aviso">
    <p><b>De dónde sale cada cifra.</b> El presupuesto, del Decreto de PEF 2026, del avance del gasto al 30 de junio de 2026 y del proyecto de PEF 2027 (Hacienda); la Cuenta Pública 2025 y el calendario, de los datos abiertos de Hacienda; lo de la Auditoría Superior, de su Matriz de Datos Básicos de la Cuenta Pública 2024. Lo que dice «derivado» lo calculamos nosotros y trae su operación. La tabla de todos los órganos lado a lado está en <a href="datos-ambiente-presupuesto.html">Datos → Medio ambiente</a>. Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>.</p>
    <p class="aa-hermanas">Sigue en Costo Ambiental: <a href="herramienta-ambiente-ticket.html">🧾 Tu estado de cuenta ambiental</a> · <a href="herramienta-ambiente-inversion.html">🌱 Simulador de inversión ambiental</a> · <a href="herramienta-ambiente-crisis.html">🌀 Crisis ambientales</a> · <a href="herramienta-inspector-entes.html">🏢 Auditor de entes públicos</a></p>
  </aside>
  <script type="application/json" id="aaDatos">%(datos)s</script>
</div>''' % {'botones': ''.join(botones), 'fichas': ''.join(fichas), 'datos': _json(csv)}
