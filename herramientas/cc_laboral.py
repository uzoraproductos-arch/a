# -*- coding: utf-8 -*-
"""Novena aplicación de la Calculadora Cívica: «Tu finiquito o tu
liquidación» (20-11-2026, pedido del autor: «construye el simulador
laboral», tras «en el simulador también me refería al estado de cuenta
cívico, ambiental, nómina, predial, laboral»).

Saca lo que le toca a una persona trabajadora al terminar su relación de
trabajo (apartado A del art. 123 constitucional, Ley Federal del Trabajo) y la
retención aproximada de ISR, cada renglón con su artículo. Cotejado el
20-11-2026 contra los textos vigentes de la Cámara de Diputados (huella
SHA-256 de cada PDF abajo):

  - LFT (última reforma DOF 14-05-2026):
    art. 79: vacaciones proporcionales si la relación termina antes del año;
    art. 76: doce días al cumplir el primer año, dos más por año hasta veinte
      y, desde el sexto, dos más por cada cinco;
    art. 80: prima vacacional no menor de 25 %;
    art. 87: aguinaldo de 15 días por lo menos, y su parte proporcional;
    art. 84 y 89: el salario para indemnizar incluye la cuota diaria y la
      parte proporcional de las prestaciones; el mensual se divide entre 30;
    art. 48: despido sin causa probada, tres meses de salario (los salarios
      vencidos dependen del juicio: no se calculan);
    arts. 49 y 50, fr. II y III: si el patrón no reinstala (o la persona
      rescinde por causa del patrón, arts. 51 y 52), además veinte días por
      año de servicios en la relación por tiempo indeterminado;
    art. 162: prima de antigüedad de doce días por año, a quien es separado
      con causa o sin ella y a quien se va por su voluntad con quince años o
      más; su salario entre uno y dos salarios mínimos (arts. 485 y 486).
  - LISR (última reforma DOF 01-04-2024), art. 93, fr. XIII y XIV: exentos
    hasta 90 veces por año de servicio lo de la separación (fracción de más
    de seis meses, año completo), 30 el aguinaldo y 15 la prima vacacional;
    la ley dice «salario mínimo» y desde la reforma de desindexación (CPEUM,
    DOF 27-01-2016, transitorio tercero) se lee como UMA;
    art. 96: la retención de lo de la separación usa la tasa del último
    sueldo mensual ordinario (o la tarifa, si lo pagado es menor).
  - RLISR, art. 174: la retención opcional del aguinaldo y la prima
    vacacional (÷ 365 × 30.4).

**Las reglas son `oficial` y la cuenta, `derivado`.** Lo nuestro se dice: los
años de 365 días, la parte del último año en proporción, el mes de 30 días,
el salario integrado con aguinaldo y prima vacacional, y que el salario y las
vacaciones se tasan como si fueran todo el ingreso del mes, sin el subsidio
para el empleo. **No es asesoría legal ni un convenio**: lo que vale es lo que
pacten ante el Centro de Conciliación o resuelva el Tribunal. No aplica a
quien trabaja para el gobierno (apartado B y su ley), ni a contratos por
tiempo u obra determinados (art. 50, fr. I), ni a plataformas digitales (fr.
IV). `calcula()` y la de `cc-laboral.js` son gemelas (`--prueba`).
Lo llama apartados.insp_nativa() (INSP_NATIVAS['cclaboral']).
"""
import datetime
import html
import json
import os
import subprocess
import sys

from presupuesto_modulos import chip
import cc_inmueble

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESTILOS = ['cc-inmueble.css']
SCRIPTS = ['cc-laboral.js']

LFT = {'tx': 'Ley Federal del Trabajo, texto vigente (Cámara de Diputados, última reforma DOF 14-05-2026)',
       'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf',
       'sha256': '12f09393a1951a91c3f57f579bf611b034edf1a5f78cdbfb828e23ff3a9acbf7'}
RLISR = {'tx': 'Reglamento de la Ley del Impuesto sobre la Renta (Cámara de Diputados, última reforma DOF 06-05-2016)',
         'url': 'https://www.diputados.gob.mx/LeyesBiblio/regley/Reg_LISR_060516.pdf',
         'sha256': '0538fd2fa3da9705370350b1e25a1656cc681d2c489545334079e1b35360d6e3'}
CPEUM = {'tx': 'Constitución Política de los Estados Unidos Mexicanos (Cámara de Diputados), decreto de desindexación del salario mínimo, DOF 27-01-2016, transitorio tercero',
         'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf',
         'sha256': 'cefb525ae8dfc97a7da40597d2ee918fe254d4bfce88301ff3c9959ced9e6e65'}

# Cuándo toca cada concepto, por causa (LFT). Lo leen la página y el navegador.
CAUSAS = [
    ('renuncia', 'Renuncié o terminamos de común acuerdo', 'LFT, art. 53, fr. I; prima de antigüedad solo con 15 años o más (art. 162, fr. III)'),
    ('justificado', 'Me despidieron con una causa del art. 47', 'LFT, art. 47; prima de antigüedad (art. 162, fr. III)'),
    ('injustificado', 'Me despidieron sin causa y pido la indemnización', 'LFT, art. 48: tres meses de salario y prima de antigüedad'),
    ('sin_reinstalar', 'El patrón no me reinstala, o yo rescindí por su culpa', 'LFT, arts. 49 a 52: tres meses, veinte días por año y prima de antigüedad'),
]
EJEMPLO = {'ing': '2019-03-01', 'sal': '2026-11-15', 'sd': 600, 'zona': 'gen', 'agd': 15, 'pv': 25, 'vacPend': 0, 'vacTom': 0, 'dp': 15,
           'causa': 'injustificado', 'agPag': False}


def esc(t):
    return html.escape(str(t))


def datos(base):
    cc = base['calculadora_civica']
    p = cc['parametros']
    tm = cc['tarifa_mensual']
    return {'uma': p['uma']['diaria'], 'sm': {'gen': p['salario_minimo']['general'], 'fro': p['salario_minimo']['frontera_norte']},
            'tarifa': [[r['li'], r['ls'], r['cf'], r['pct']] for r in tm['renglones']],
            'causas': [[c[0], c[1], c[2]] for c in CAUSAS],
            'f': {'uma': p['uma']['fuente'], 'sm': p['salario_minimo']['fuente'], 'tarifa': '%s (%s)' % (tm['ley'], tm['fuente'])}}


# ---- La cuenta (gemela de calcula() en cc-laboral.js) ----

def _dia(s):
    return datetime.date(*[int(x) for x in s.split('-')])


def vac_tabla(n):
    """Días de vacaciones del año de servicios n (LFT, art. 76)."""
    if n <= 0:
        return 0
    if n <= 5:
        return 12 + 2 * (n - 1)
    return 20 + 2 * ((n - 6) // 5 + 1)


def isr_tarifa(D, m):
    if m <= 0:
        return 0.0
    fila = D['tarifa'][0]
    for f in D['tarifa']:
        if f[0] <= m:
            fila = f
    li, _ls, cf, pct = fila
    return cf + max(0.0, m - li) * pct / 100.0


def calcula(D, x):
    ing, sal = _dia(x['ing']), _dia(x['sal'])
    if sal < ing:
        return {'error': 'La fecha de salida no puede ser antes de la de ingreso.'}
    sd = float(x['sd'])
    dias = (sal - ing).days + 1
    anios = dias / 365.0
    comp = int(dias // 365)
    dcur = dias - comp * 365
    agd, pv = float(x.get('agd') or 15), float(x.get('pv') or 25)
    vac_anio = vac_tabla(comp + 1)
    sdi = sd * (1 + (agd + vac_anio * pv / 100.0) / 365.0)
    r = {'dias': dias, 'anios': anios, 'sdi': sdi, 'vac_anio': vac_anio, 'conc': []}
    c = r['conc']
    # Finiquito: lo que se debe siempre.
    dp = float(x.get('dp') or 0)
    if dp > 0:
        c.append(['salario', 'Días de salario que no te han pagado (%g × salario diario)' % dp, dp * sd, 'LFT, art. 88'])
    vprop = max(0.0, vac_anio * dcur / 365.0 - float(x.get('vacTom') or 0))
    vdias = vprop + float(x.get('vacPend') or 0)
    vac = vdias * sd
    if vac > 0:
        c.append(['vacaciones', 'Vacaciones: %.2f días (proporcionales del año en curso y pendientes)' % vdias, vac, 'LFT, arts. 76 y 79'])
        c.append(['prima_vac', 'Prima vacacional (%g %% de tus vacaciones)' % pv, vac * pv / 100.0, 'LFT, art. 80'])
    if not x.get('agPag'):
        ini = max(ing, datetime.date(sal.year, 1, 1))
        dag = (sal - ini).days + 1
        ag = agd * dag / 365.0 * sd
        c.append(['aguinaldo', 'Aguinaldo proporcional (%g días × %d días trabajados este año ÷ 365)' % (agd, dag), ag, 'LFT, art. 87'])
    # Lo que depende de la causa.
    causa = x['causa']
    tope = 2 * D['sm'][x.get('zona') or 'gen']
    piso = D['sm'][x.get('zona') or 'gen']
    if causa in ('justificado', 'injustificado', 'sin_reinstalar') or (causa == 'renuncia' and anios >= 15):
        bpa = min(max(sdi, piso), tope)
        c.append(['prima_ant', 'Prima de antigüedad: 12 días × %.2f años × %s de salario (entre uno y dos salarios mínimos)' % (anios, _p(bpa)),
                  12 * anios * bpa, 'LFT, arts. 162, 485 y 486'])
    if causa in ('injustificado', 'sin_reinstalar'):
        c.append(['ind3', 'Indemnización: tres meses (90 días) de salario integrado', 90 * sdi, 'LFT, arts. 48, 50 (fr. III) y 89'])
    if causa == 'sin_reinstalar':
        c.append(['ind20', 'Veinte días de salario integrado por cada año de servicios (%.2f años)' % anios, 20 * anios * sdi, 'LFT, arts. 49 y 50, fr. II'])
    tot = sum(k[2] for k in c)
    # ISR aproximado (LISR arts. 93, 95 y 96; RLISR art. 174).
    U = D['uma']
    m = float(x.get('mens') or 0) or sd * 30
    isr_m = isr_tarifa(D, m)
    tasa_m = isr_m / m if m else 0.0
    val = {k[0]: k[2] for k in c}
    sep = val.get('prima_ant', 0) + val.get('ind3', 0) + val.get('ind20', 0)
    anios_isr = comp + (1 if anios - comp > 0.5 else 0)
    ex_sep = min(sep, 90 * U * anios_isr)
    g_sep = sep - ex_sep
    ret_sep = 0.0
    if g_sep > 0:
        ret_sep = isr_tarifa(D, g_sep) if g_sep < m else g_sep * tasa_m

    def art174(g):
        if g <= 0:
            return 0.0
        R = g / 365.0 * 30.4
        dif = isr_tarifa(D, m + R) - isr_m
        return g * (dif / R)
    ag = val.get('aguinaldo', 0)
    ex_ag = min(ag, 30 * U)
    pvv = val.get('prima_vac', 0)
    ex_pv = min(pvv, 15 * U)
    ret_ag, ret_pv = art174(ag - ex_ag), art174(pvv - ex_pv)
    ordi = val.get('salario', 0) + val.get('vacaciones', 0)
    ret_ord = isr_tarifa(D, ordi)
    isr = ret_sep + ret_ag + ret_pv + ret_ord
    r.update({'total': tot, 'exento': ex_sep + ex_ag + ex_pv, 'isr': isr, 'neto': tot - isr, 'm': m, 'tasa_m': tasa_m,
              'isr_det': [ret_ord, ret_ag, ret_pv, ret_sep], 'ex_det': [ex_ag, ex_pv, ex_sep], 'anios_isr': anios_isr})
    return r


def _p(v):
    return '$' + format(round(v, 2), ',.2f')


def construir(base, ref):
    D = datos(base)
    L = cc_inmueble.LISR
    hoy = datetime.date.today().isoformat()
    lft = lambda a: '<a href="%s">LFT, %s</a>' % (esc(LFT['url']), esc(a))
    lisr = lambda a: '<a href="%s">LISR, %s</a>' % (esc(L['url']), esc(a))
    causas = ''.join('<option value="%s"%s>%s</option>' % (k, ' selected' if k == 'renuncia' else '', esc(t)) for k, t, _r in CAUSAS)
    huella = lambda d: '<a href="%s">%s</a> (huella SHA-256 <code>%s…</code>)' % (esc(d['url']), esc(d['tx']), d['sha256'][:12])
    return '''<div class="ci" id="clRaiz">
  <section class="ci-arranque" aria-labelledby="clTit">
    <p class="ci-kicker">Calculadora Cívica · simulador</p>
    <h2 class="ci-grande" id="clTit">Tu finiquito o tu liquidación: ¿cuánto te toca?</h2>
    <p class="ci-txt">Escribe cuándo entraste, cuándo sales, tu salario y por qué termina tu trabajo. La página saca, renglón por renglón y con su artículo, <b>lo que siempre te deben</b> (salario, vacaciones, prima vacacional y aguinaldo: el finiquito) y, según la causa, <b>la indemnización y la prima de antigüedad</b> (la liquidación), con la parte exenta de ISR y la retención aproximada.</p>
    <p class="ci-privado">🔒 La cuenta la hace tu navegador: lo que escribes no se guarda ni se envía.</p>
  </section>

  <form class="ci-form" id="clForm" novalidate>
    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">1</span> Tu relación de trabajo</legend>
      <div class="ci-fila">
        <div><label class="ci-et" for="clIng">Fecha en que entraste</label><input class="ci-in" id="clIng" type="date" value="2022-01-10"></div>
        <div><label class="ci-et" for="clSal">Fecha en que sales</label><input class="ci-in" id="clSal" type="date" value="{hoy}"></div>
      </div>
      <label class="ci-et" for="clSd">Tu salario (pesos, antes de descuentos)</label>
      <input class="ci-in" id="clSd" inputmode="decimal" autocomplete="off" placeholder="Ej.: 12,000">
      <div class="ci-fila">
        <div><label class="ci-et" for="clPer">Cada cuándo</label><select class="ci-in" id="clPer"><option value="mes">Al mes</option><option value="dia">Al día</option></select></div>
        <div><label class="ci-et" for="clZona">Dónde trabajas</label><select class="ci-in" id="clZona"><option value="gen">Resto del país</option><option value="fro">Zona libre de la frontera norte</option></select></div>
      </div>
      <label class="ci-et" for="clCausa">Por qué termina</label>
      <select class="ci-in" id="clCausa">{causas}</select>
      <p class="ci-pista" id="clCausaLey"></p>
    </fieldset>

    <fieldset class="ci-grupo">
      <legend class="ci-tit"><span class="ci-n" aria-hidden="true">2</span> Lo que ya te pagaron y tus prestaciones <small>(opcional)</small></legend>
      <label class="ci-et" for="clDp">Días trabajados que todavía no te pagan</label>
      <input class="ci-in" id="clDp" inputmode="decimal" autocomplete="off" placeholder="Ej.: 15">
      <div class="ci-fila">
        <div><label class="ci-et" for="clVt">Días de vacaciones que ya tomaste este año de servicio</label><input class="ci-in" id="clVt" inputmode="decimal" autocomplete="off" placeholder="0"></div>
        <div><label class="ci-et" for="clVp">Días de vacaciones de años anteriores que no tomaste</label><input class="ci-in" id="clVp" inputmode="decimal" autocomplete="off" placeholder="0"></div>
      </div>
      <div class="ci-fila">
        <div><label class="ci-et" for="clAg">Días de aguinaldo de tu contrato</label><input class="ci-in" id="clAg" inputmode="decimal" autocomplete="off" value="15"></div>
        <div><label class="ci-et" for="clPv">Prima vacacional (%)</label><input class="ci-in" id="clPv" inputmode="decimal" autocomplete="off" value="25"></div>
      </div>
      <label class="ci-check"><input type="checkbox" id="clAgPag"> Ya me pagaron el aguinaldo de este año</label>
    </fieldset>
    <p class="ci-acciones"><button type="submit" class="ci-boton">Saca la cuenta</button></p>
  </form>

  <section class="ci-res" id="clRes" aria-live="polite" hidden>
    <h2 class="ci-tit"><span class="ci-n" aria-hidden="true">3</span> Lo que te toca, renglón por renglón {chip_d}</h2>
    <div class="ci-total" id="clTotal"></div>
    <div class="ci-tabla-caja"><table class="ci-tabla"><caption>Cómo se llega a la cifra</caption>
      <thead><tr><th scope="col">Concepto</th><th scope="col">Pesos</th><th scope="col">Regla</th></tr></thead>
      <tbody id="clPasos"></tbody></table></div>
    <p class="ci-nota" id="clNota"></p>
  </section>

  <aside class="ci-aviso" aria-labelledby="clLeeTit">
    <h2 class="ci-tit" id="clLeeTit"><span aria-hidden="true">📐</span> Cómo se calcula</h2>
    <ol class="ci-lista">
      <li><b>El finiquito siempre se paga</b>, sin importar por qué termina el trabajo: los días que no te han pagado, tus <b>vacaciones</b> (las del año en curso en proporción y las que no tomaste: {a76}, {a79}) con su <b>prima vacacional</b> de al menos 25 % ({a80}) y la parte proporcional del <b>aguinaldo</b>, de al menos 15 días ({a87}).</li>
      <li><b>La prima de antigüedad</b> es de 12 días por año ({a162}): se paga a quien despiden, con causa o sin ella, y a quien se va por su voluntad con 15 años o más. Su salario no baja de un salario mínimo ni pasa de dos ({a486}).</li>
      <li><b>La indemnización</b> depende de la causa: si te despiden sin una causa probada, tres meses de salario ({a48}); si el patrón no te reinstala o tú terminas por su culpa, además veinte días por cada año ({a50}, {a51}). Se paga con el <b>salario integrado</b>: tu salario diario más la parte de aguinaldo y prima vacacional ({a89}).</li>
      <li><b>El ISR</b>: no pagas por lo de la separación hasta 90 UMA por año de servicio; por el aguinaldo, hasta 30, y por la prima vacacional, hasta 15 ({a93}). La ley todavía dice «salario mínimo», y desde 2016 esas referencias se leen como UMA ({cpeum}). Lo demás se retiene: lo de la separación con la tasa de tu último sueldo mensual ({a96}) y el aguinaldo y la prima con el art. 174 del Reglamento ({r174}).</li>
    </ol>
    <p><b>Lo que esta cuenta supone:</b> años de 365 días, la parte del último año en proporción, el mes de 30 días ({a89b}), y que el salario y las vacaciones se tasan como si fueran todo tu ingreso del mes, sin el subsidio para el empleo. Todo eso es nuestro (<span class="est-chip est-derivado">auditada</span>).</p>
    <p><b>Lo que no hace:</b> no es asesoría legal ni un convenio. Lo que vale es lo que firmen ante el Centro de Conciliación o resuelva el Tribunal. No calcula los salarios vencidos ni sus intereses ({a48}), que dependen del juicio, ni el reparto de utilidades, que depende de la declaración de la empresa ({a117}). No aplica si trabajas para el gobierno (te rige el apartado B y su ley), si tu contrato era por tiempo u obra determinados ({a50i}) o si trabajas en plataformas digitales ({a50iv}). Si tienes dudas, la Procuraduría Federal de la Defensa del Trabajo asesora gratis.</p>
    <p class="ci-fuentes">Fuentes: {f_lft} · {f_lisr} · {f_rlisr} · {f_cpeum} · UMA: {f_uma} · Salario mínimo: {f_sm} · Tarifa: {f_tarifa} {chip_o}.</p>
    <p class="ci-hermanas">Sigue con la Calculadora: <a href="herramienta-calculadora-ticket-retienen.html">💼 Lo que te retienen y tu nómina completa</a> · <a href="herramienta-calculadora-ticket.html">🧾 Tu estado de cuenta</a></p>
  </aside>
  <script type="application/json" id="clDatos">{datos}</script>
</div>'''.format(
        hoy=hoy, causas=causas, chip_d=chip('derivado'), chip_o=chip('oficial'),
        a76=lft('art. 76'), a79=lft('art. 79'), a80=lft('art. 80'), a87=lft('art. 87'), a162=lft('art. 162'), a486=lft('arts. 485 y 486'),
        a48=lft('art. 48'), a50=lft('arts. 49 y 50, fr. II y III'), a51=lft('arts. 51 y 52'), a89=lft('arts. 84 y 89'), a89b=lft('art. 89'),
        a117=lft('arts. 117 a 131'), a50i=lft('art. 50, fr. I'), a50iv=lft('art. 50, fr. IV'),
        a93=lisr('art. 93, fr. XIII y XIV'), a96=lisr('arts. 95 y 96'),
        r174='<a href="%s">RLISR, art. 174</a>' % esc(RLISR['url']),
        cpeum='<a href="%s">CPEUM, decreto DOF 27-01-2016, transitorio tercero</a>' % esc(CPEUM['url']),
        f_lft=huella(LFT), f_lisr=huella(L), f_rlisr=huella(RLISR), f_cpeum=huella(CPEUM),
        f_uma=esc(D['f']['uma']), f_sm=esc(D['f']['sm']), f_tarifa=esc(D['f']['tarifa']),
        datos=cc_inmueble._json(D))


def prueba():
    """Python y el navegador dan lo mismo en casos fijos."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import auditorias
    D = datos(auditorias.db())
    casos = []
    for causa in ('renuncia', 'justificado', 'injustificado', 'sin_reinstalar'):
        for ing, sal, sd in (('2019-03-01', '2026-11-15', 600), ('2026-02-01', '2026-06-30', 280), ('2008-01-15', '2026-11-20', 2500),
                             ('2010-06-01', '2026-01-31', 15000 / 30.0)):
            casos.append(dict(EJEMPLO, ing=ing, sal=sal, sd=sd, causa=causa))
    casos.append(dict(EJEMPLO, agPag=True, vacPend=6, vacTom=3, zona='fro', agd=30, pv=50))
    js = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'cc-laboral.js')
    prog = ("global.window={};global.document={getElementById:function(){return null}};require(%s);"
            "var D=%s;console.log(JSON.stringify(%s.map(function(x){var r=window.AuditorLaboral.calcula(D,x);"
            "return [r.total,r.isr,r.exento,r.sdi,r.conc.length];})));" % (json.dumps(js), json.dumps(D), json.dumps(casos)))
    r = subprocess.run(['node', '-e', prog], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr)
        return 1
    nav = json.loads(r.stdout)
    mal = 0
    for x, n in zip(casos, nav):
        p = calcula(D, x)
        py = [p['total'], p['isr'], p['exento'], p['sdi'], len(p['conc'])]
        if any(abs(a - b) > 0.005 for a, b in zip(py, n)):
            mal += 1
            print('✗', x['causa'], x['ing'], x['sal'], 'Python', py, 'navegador', n)
    # Reglas a mano: la tabla de vacaciones del art. 76 y que la causa decide los conceptos.
    if [vac_tabla(n) for n in (1, 2, 5, 6, 10, 11, 16)] != [12, 14, 20, 22, 22, 24, 26]:
        mal += 1
        print('✗ la tabla de vacaciones del art. 76')
    kinds = lambda c: {k[0] for k in calcula(D, dict(EJEMPLO, causa=c))['conc']}
    if 'prima_ant' in kinds('renuncia') or 'ind3' in kinds('justificado') or 'ind20' in kinds('injustificado') or not {'prima_ant', 'ind3', 'ind20'} <= kinds('sin_reinstalar'):
        mal += 1
        print('✗ la causa no decide bien los conceptos')
    if mal:
        print('Simulador laboral: %d diferencias' % mal)
        return 1
    print('Simulador laboral: %d casos iguales en Python y en el navegador; la tabla del art. 76 y las cuatro causas de la LFT en orden' % len(casos))
    return 0


if __name__ == '__main__':
    if '--prueba' in sys.argv:
        sys.exit(prueba())
