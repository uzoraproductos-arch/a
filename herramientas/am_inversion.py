# -*- coding: utf-8 -*-
"""Costo Ambiental, aplicacion 4: «Simulador de inversion ambiental» (pedido
del autor, 22-10-2026: «tambien como por las inversiones, ese tipo de
simuladores»).

Dos simuladores, los dos aritmetica sobre cifras oficiales; lo unico que
pone el lector es el supuesto, y la pagina lo dice:

  1. ¿En cuantos anos alcanzaria? El gasto publico en proteccion ambiental
     de 2024 contra el costo del dano de ese ano (INEGI, CEEM 2024). El
     lector elige cuanto creceria cada ano el gasto y cuanto el dano, y ve
     en que ano se igualarian (o que no se igualan), con la brecha que se
     acumula mientras tanto.
  2. Si ese dinero fuera al ambiente. Una cantidad oficial (los intereses de
     la deuda o la deuda nueva de 2026, en un dia o una semana) o la que
     escriba el lector, medida en anos del presupuesto 2026 de cada organo
     del sector ambiental y en dias del dano ambiental de 2024.

Lo que calcula el JS (am-inversion.js) es derivado e hipotetico, y lo
rotula asi. No es un pronostico ni una propuesta: los intereses de la deuda
contratada son obligatorios, y que el gasto iguale al dano no significa que
el dano desaparezca.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['aminversion']).
"""
import html
import json

from presupuesto_modulos import chip

ESTILOS = ['am-inversion.css']
SCRIPTS = ['am-inversion.js']
SIGLAS = {'B00': 'Conagua', 'RHQ': 'CONAFOR', 'F00': 'CONANP', 'E00': 'PROFEPA', 'G00': 'ASEA', 'RJJ': 'INECC',
          'RESTO': 'SEMARNAT central'}


def esc(t):
    return html.escape(str(t if t is not None else ''), quote=True)


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def n(v, d=0):
    return format(v, ',.%df' % d)


def construir(base, ref):
    C = base['cuentas_ecologicas']
    A = base['ambiente']
    P, F = A['presupuesto'], A['fuentes']
    refs = {r['id']: r for r in base.get('referencias_legales', [])}
    rel = {x['id']: x for x in base['calculadora_civica']['relojes']['fuentes']}
    gpa, ctada, ej = C['gasto_proteccion_ambiental'], C['ctada'], C['ejercicio']

    def liga_ref(rid, texto):
        r = refs.get(rid)
        if not r:
            return esc(texto)
        return '<a class="ai-fu" href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>' % (esc(r['url']), esc(texto))

    ceem = liga_ref('ref-ceem-2024', 'INEGI, Cuentas Económicas y Ecológicas %s, p. 2' % ej)
    f_pef = '<a class="ai-fu" href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>' % (esc(F['PEF']['url']), esc(F['PEF'].get('corto') or F['PEF']['doc']))
    intereses, nueva = rel['intereses'], rel['deuda-nueva']

    presets = [
        ('int-dia', '📉', 'Los intereses de la deuda de un día', intereses['anual_mdp'] / 365,
         'Intereses de 2026 ÷ 365', intereses),
        ('int-sem', '📉', 'Los intereses de la deuda de una semana', intereses['anual_mdp'] * 7 / 365,
         'Intereses de 2026 ÷ 365 × 7', intereses),
        ('deu-dia', '🏦', 'La deuda nueva de un día', nueva['anual_mdp'] / 365,
         'Deuda nueva autorizada para 2026 ÷ 365', nueva),
    ]
    botones = ''.join(
        '<button type="button" class="ai-op" data-pre="%s" data-mdp="%.4f" aria-pressed="%s"><span aria-hidden="true">%s</span> %s</button>'
        % (pid, v, 'true' if i == 0 else 'false', ico, esc(nom)) for i, (pid, ico, nom, v, op, x) in enumerate(presets))
    origen = ''.join(
        '<li><b>%s:</b> $%s mdp al año %s · %s. Lo de un día o una semana es %s: %s.</li>'
        % (esc(x['nombre']), n(x['anual_mdp'], 1), chip(x['estado']), liga_ref(x['refKey'], x['fuente']), chip('derivado'), esc(op))
        for (pid, ico, nom, v, op, x) in presets[::2])
    orgs = [{'s': 'Ramo %s completo' % P['ramo'], 'v': P['aprobado2026']['valor'] / 1e6}] + \
           [{'s': SIGLAS.get(u['ur'], u['ur']), 'n': u['nombre'], 'v': u['aprobado'] / 1e6} for u in P['unidades']]
    datos = {'gpa': gpa['monto_mdp'], 'dano': ctada['total_mdp'], 'ej': ej, 'orgs': orgs,
             'pre': {p[0]: p[2] for p in presets}}

    return '''<div class="ai" id="aiRaiz">
  <section class="ai-arranque" aria-labelledby="aiArrTit">
    <p class="ai-kicker">Costo Ambiental · aplicación 4</p>
    <h2 class="ai-grande" id="aiArrTit">¿Y si se invirtiera en el ambiente?</h2>
    <p class="ai-txt">En {ej}, por cada peso que el sector público gastó en proteger el ambiente, el daño costó <b>${ratio}</b> {chip_d}. Aquí pruebas dos cosas: cuántos años tardaría el gasto en alcanzar al daño si creciera, y cuánto pesaría en el sector ambiental el dinero que hoy se va en intereses de la deuda.</p>
    <div class="ai-par">
      <div class="ai-par-d"><span class="ai-par-k">🛡️ Gasto público en protección ambiental, {ej}</span><b class="ai-num">${gpa} mdp</b>{chip_o}</div>
      <div class="ai-par-d ai-par-mal"><span class="ai-par-k">🌫️ Costo del daño ambiental, {ej}</span><b class="ai-num">${dano} mdp</b>{chip_o}</div>
    </div>
    <p class="ai-fuente">{ceem}. El gasto es solo del sector público consolidado: no incluye empresas ni hogares.</p>
  </section>

  <section class="ai-sec" id="aiAlcanza" aria-labelledby="aiAlcTit">
    <h2 class="ai-tit" id="aiAlcTit"><span class="ai-n">1</span> ¿En cuántos años alcanzaría el gasto al daño?</h2>
    <p class="ai-txt">Mueve los dos controles. El punto de partida son las cifras de {ej}; lo que pase después es tu supuesto.</p>
    <div class="ai-mandos">
      <div class="ai-mando"><label class="ai-mando-et" for="aiG"><span aria-hidden="true">🛡️</span> Cuánto crece cada año el gasto en proteger</label>
        <input type="range" class="ai-rango" id="aiG" min="0" max="25" step="0.5" value="10">
        <output class="ai-mando-val" id="aiGVal" for="aiG">10.0 % al año</output></div>
      <div class="ai-mando"><label class="ai-mando-et" for="aiD"><span aria-hidden="true">🌫️</span> Cuánto cambia cada año el costo del daño</label>
        <input type="range" class="ai-rango" id="aiD" min="-5" max="10" step="0.5" value="0">
        <output class="ai-mando-val" id="aiDVal" for="aiD">0.0 % al año</output></div>
    </div>
    <div class="ai-atajos" role="group" aria-label="Escenarios">
      <button type="button" class="ai-op" data-g="5" data-d="0">Gasto +5 %, daño igual</button>
      <button type="button" class="ai-op" data-g="10" data-d="0" aria-pressed="true">Gasto +10 %, daño igual</button>
      <button type="button" class="ai-op" data-g="10" data-d="3">Gasto +10 %, daño +3 %</button>
      <button type="button" class="ai-op" data-g="3" data-d="5">Gasto +3 %, daño +5 %</button>
    </div>
    <div class="ai-res" id="aiAlcRes" aria-live="polite"></div>
    <div class="ai-graf" id="aiGraf" role="img" aria-label="Gasto en protección contra costo del daño, año por año"></div>
    <p class="ai-honesto"><b>Qué hace y qué no hace.</b> {chip_d} Gasto del año t = ${gpa} mdp × (1 + crecimiento)<sup>t</sup>; daño del año t = ${dano} mdp × (1 + cambio)<sup>t</sup>. Se igualan cuando el gasto alcanza al daño. La brecha acumulada suma, año por año, el daño menos el gasto hasta ese momento. Todo en pesos de {ej}, sin inflación. Es una proporción, no un pronóstico: igualar el gasto con el daño no quiere decir que el daño desaparezca, ni que cada peso de protección evite un peso de daño.</p>
  </section>

  <section class="ai-sec" id="aiEquivale" aria-labelledby="aiEqTit">
    <h2 class="ai-tit" id="aiEqTit"><span class="ai-n">2</span> Si ese dinero fuera al ambiente</h2>
    <p class="ai-txt">Elige una cantidad oficial o escribe la tuya, y mírala en años del presupuesto 2026 de cada órgano del sector ambiental.</p>
    <div class="ai-atajos" role="group" aria-label="Cantidades de ejemplo">{botones}</div>
    <label class="ai-mando-et" for="aiMonto">O escribe una cantidad, en millones de pesos</label>
    <div class="ai-entrada"><span aria-hidden="true">$</span><input type="text" inputmode="decimal" id="aiMonto" class="ai-input" autocomplete="off"><span>mdp</span></div>
    <div class="ai-res" id="aiEqRes" aria-live="polite"></div>
    <ol class="ai-orgs" id="aiOrgs"></ol>
    <ul class="ai-origen">{origen}
      <li><b>Presupuesto de cada órgano:</b> aprobado 2026 {chip_o} · {f_pef}. Los años de presupuesto son {chip_d}: cantidad ÷ aprobado 2026 del órgano.</li>
      <li><b>Días del daño ambiental:</b> {chip_d} cantidad ÷ (costo del daño de {ej} ÷ 365). Compara una cifra de 2026 con una de {ej}: es ilustrativo.</li>
    </ul>
    <p class="ai-honesto"><b>Una comparación, no una propuesta.</b> Los intereses de la deuda ya contratada se tienen que pagar: no se pueden mover a otro rubro. La comparación sirve para medir su tamaño frente a lo que recibe el sector ambiental.</p>
  </section>

  <aside class="ai-aviso">
    <p>Las cifras del daño, de dónde salen y qué se acabó y qué se ensució están en <a href="datos-ambiente-desglose.html">Datos → Medio ambiente</a>. Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>.</p>
    <p class="ai-hermanas">Sigue en Costo Ambiental: <a href="herramienta-ambiente-pib.html">📈 ¿Cuánto del crecimiento es real?</a> · <a href="herramienta-ambiente-auditor.html">🔍 Auditor ambiental</a> · <a href="herramienta-calculadora-reloj.html">⏱️ El reloj de la deuda</a></p>
  </aside>
  <script type="application/json" id="aiDatos">{datos}</script>
</div>'''.format(
        ej=ej, ratio=n(ctada['total_mdp'] / gpa['monto_mdp'], 2), chip_d=chip('derivado'), chip_o=chip('oficial'),
        gpa=n(gpa['monto_mdp']), dano=n(ctada['total_mdp']), ceem=ceem, botones=botones, origen=origen, f_pef=f_pef,
        datos=_json(datos))
