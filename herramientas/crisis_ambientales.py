# -*- coding: utf-8 -*-
"""Quinta aplicacion de Costo Ambiental: «Crisis ambientales» (pedido del
autor, 11-10-2026).

Los desastres (lo que llega en dias: Otis, Simon) y las crisis cronicas (lo
que se acumula en anos: el agua de Guadalajara) tambien son gasto publico.
La pagina responde cuatro preguntas con documentos oficiales:

  1. El hueco: cuanto puede costar un desastre y cuanto cubren el seguro y
     los bonos catastroficos (Criterios Generales 2027).
  2. Lo que cuesta esperar: la calculadora. Si el hueco se cubre con deuda,
     cuanto suman los intereses con una tasa oficial (crisis.js).
  3. Los casos: una ficha por crisis, con lo anunciado, lo comprobado, lo que
     observo la Auditoria y lo que sigue sin publicarse.
  4. El dano de fondo: lo que el INEGI calcula cada ano por el agua que se
     devuelve sin tratar y la que se saca de mas de los acuiferos.

Regla de la plataforma (AGENTS.md, §2): cada cifra lleva su fuente y su
chip. Lo que solo dijo la prensa no entra como cifra: queda pendiente, con
el nombre de quien debe publicarla.

Lo llama apartados.generar() (via herramienta_modulo con bloque).
"""
import json

from presupuesto_modulos import chip, mdp

ARCHIVO = 'herramienta-ambiente-crisis.html'


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def pend(id_):
    return chip('pendiente', id_)


def fuente(url, texto):
    return '<a href="%s" target="_blank" rel="noopener">%s ↗</a>' % (url, texto)


def _tasas(base, ref):
    p = base['paquete_2027']
    f = {x['id']: x for x in p['finanzas']}
    cetes = next(m for m in p['marco'] if m['v'].startswith('Tasa de interés'))
    cf, saldo = f['f-costofin']['m'], f['f-shrfsp']['m26']
    impl = round(cf / saldo * 100, 2)
    return [
        {'id': 'impl', 'nom': 'la tasa promedio de la deuda pública', 'v': impl, 'est': 'derivado',
         'op': 'Costo financiero de la deuda propuesto para 2027 (%s) ÷ saldo de la deuda pública al cierre estimado de 2026 (%s), ambos de los Criterios 2027.'
               % (mdp(cf), mdp(saldo))},
        {'id': 'cetes', 'nom': 'la tasa de Cetes a 28 días prevista para 2027', 'v': float(cetes['p27']), 'est': 'oficial',
         'op': 'Es la tasa de referencia del marco macroeconómico de los Criterios 2027 (fin de periodo).'},
    ]


def calculadora(base, ref, ejemplos):
    tasas = _tasas(base, ref)
    radios = '\n'.join(
        '            <label class="cr-tasa"><input type="radio" name="crTasa" value="%s"%s> <b>%s%%</b> %s %s</label>'
        % (t['id'], ' checked' if k == 0 else '', format(t['v'], '.2f'), t['nom'], chip(t['est']))
        for k, t in enumerate(tasas))
    botones = '\n'.join(
        '            <button type="button" class="cr-ej" data-cr-monto="%s" aria-pressed="false">%s<small>%s</small></button>'
        % (format(v, '.1f'), nom, det) for nom, v, det in ejemplos)
    return '''<section class="cr-sec" aria-labelledby="crCalcTit">
        <h2 class="cr-tit" id="crCalcTit"><span aria-hidden="true">🧮</span> Lo que cuesta esperar</h2>
        <p class="cr-txt">Cuando el fondo no alcanza, el hueco se cubre recortando otros programas o pidiendo prestado. Si se pide prestado, el desastre sigue costando cada año en intereses. Escribe un monto, o carga uno de la página, y elige la tasa.</p>
        <div class="cr-calc">
          <div class="cr-calc-in">
            <label class="cr-campo" for="crMonto"><span>El hueco, en millones de pesos</span>
              <input id="crMonto" type="text" inputmode="decimal" autocomplete="off" placeholder="0" value=""></label>
            <div class="cr-ejs" role="group" aria-label="Montos de esta página">
{botones}
              <button type="button" class="cr-ej cr-ej-cero" id="crCero">Volver a $0</button>
            </div>
            <fieldset class="cr-tasas"><legend>La tasa</legend>
{radios}
            </fieldset>
            <label class="cr-campo" for="crAnios"><span>¿Cuántos años? <b id="crAniosTx">10 años</b></span>
              <input id="crAnios" type="range" min="1" max="30" step="1" value="10"></label>
          </div>
          <div class="cr-calc-out" id="crSalida" aria-live="polite"></div>
        </div>
        <script type="application/json" id="crDatos">{datos}</script>
      </section>'''.format(botones=botones, radios=radios, datos=_json({'tasas': tasas}))


# ---------------------------------------------------------------------------
# Documentos que no estan en el compendio: se citan con su enlace directo.
# Todos se abrieron y se cotejaron el 11-10-2026.
# ---------------------------------------------------------------------------
PEF_HIST = [  # Fondo de Desastres Naturales aprobado en el PEF de cada ano (Ramo 23)
    (2018, 24644.0, 'https://www.diputados.gob.mx/LeyesBiblio/abro/pef_2018/PEF_2018_abro.pdf'),
    (2019, 3644.0, 'https://www.diputados.gob.mx/LeyesBiblio/abro/pef_2019/PEF_2019_abro.pdf'),
    (2020, 3353.0, 'https://www.diputados.gob.mx/LeyesBiblio/abro/pef_2020/PEF_2020_abro.pdf'),
]
FONDEN_2026 = 19430.107735   # PEF 2026, Anexo 20 (p. 60 del PDF)
FONDEN_2027 = 20057.115013   # Proyecto de PEF 2027, Anexo 20 (p. 442 del PDF)
SEGURO = 10400.0             # CGPE 2027, p. 49: «cobertura por 10.4 mmp»
BONOS_MDD = 595.0            # CGPE 2027, p. 60: cuatro clases de bonos
BONO_PACIFICO_MDD = 175.0    # Clase D, huracanes del Pacifico
GRANDE, MEDIANO, FRECUENTES = 62100.0, 22300.0, 20300.0   # CGPE 2027, p. 51
OTIS_DANO, OTIS_PLAN, OTIS_EJ = 84207.0, 61313.0, 35017.0
CENAPRED = [  # (ano, mdp, prefijo, nota)
    (2010, 92300.0, '', 'El año más costoso de la serie'),
    (2017, 88400.0, 'más de ', 'Los sismos de septiembre'),
    (2023, 88910.0, '', 'Otis, por sí solo: $84,207 mdp'),
    (2024, 14434.0, '', 'El último año publicado'),
]
EST_OTIS_EJ = ('https://www.gob.mx/amlo/articulos/version-estenografica-conferencia-de-prensa-del-presidente-'
               'andres-manuel-lopez-obrador-del-13-de-septiembre-de-2024')
DOF_OTIS_EMERG = 'https://dof.gob.mx/nota_detalle.php?codigo=5707225&fecha=30/10/2023'
DOF_OTIS_ACLARA = 'https://dof.gob.mx/nota_detalle.php?codigo=5707645&fecha=03/11/2023'
DOF = 'https://www.dof.gob.mx/'
JAL = 'https://www.jalisco.gob.mx/prensa/noticias/'
JAL_ROTACION = JAL + 'acuerdan-gobierno-de-jalisco-y-alcaldes-metropoli-48478'
JAL_PLAN = JAL + 'anuncia-gobierno-de-jalisco-plan-integral-para-me-47113'
JAL_HIDRICO = JAL + 'entrega-gobierno-de-jalisco-al-congreso-del-estad-47313'
JAL_ACUEDUCTO = JAL + 'entrega-gobierno-de-jalisco-iniciativa-del-acuedu-48495'
JAL_ZAPOTILLO = JAL + 'confirma-pablo-lemus-gobernador-de-jalisco-respal-47963'
JAL_SALUD = JAL + '47232'
PRES_0810 = ('https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-'
             'claudia-sheinbaum-pardo-del-08-de-octubre-de-2026')
PRES_1610 = ('https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-'
             'claudia-sheinbaum-pardo-del-16-de-octubre-de-2026')
PRES_2110 = ('https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-'
             'claudia-sheinbaum-pardo-del-21-de-octubre-de-2026')
GACETA_SON_2104 = 'https://gestion.api.congresoson.gob.mx/publico/descarga?uuid=f8cf663d-4257-4f5d-8b08-b05b80a83e72'
# El caso de Guaymas comparte sus pendientes con su columna de Verificamos
# (noticias-auditavision.html#col-guaymas-comodato-amigo-gnl): los ids
# red-<columna>-<n> los anota pendientes.py desde el cotejo.
COL_GUAYMAS = 'guaymas-comodato-amigo-gnl'


def mmp_tx(v):
    return '$%s mmp' % format(v / 1000, ',.1f')


def _barra(nom, sub, v, tope, color, tx):
    w = v / tope * 100
    return ('          <li><span class="cr-h-nom">%s<small>%s</small></span>'
            '<span class="cr-h-barra" style="--w:%.2f%%;--c:%s"><span class="cr-h-seg"></span>'
            '<span class="cr-h-tx%s">%s</span></span></li>' % (nom, sub, w, color, ' fuera' if w < 35 else '', tx))


def _pila(nom, sub, partes, tope, tx):
    segs = ''.join('<span class="cr-p-seg" style="--w:%.2f%%;--c:%s" title="%s: %s"></span>' % (v / tope * 100, c, n, mdp(v))
                   for n, v, c in partes)
    return ('          <li><span class="cr-h-nom">%s<small>%s</small></span>'
            '<span class="cr-h-barra cr-pila">%s<span class="cr-h-tx">%s</span></span></li>' % (nom, sub, segs, tx))


def _renglon(ico, cifra, nom, est, pid, tx):
    return ('          <li><span class="cr-r-ico" aria-hidden="true">%s</span><span class="cr-r-cifra"><b>%s</b><small>%s</small>%s</span>'
            '<span class="cr-r-tx">%s</span></li>' % (ico, cifra, nom, chip(est, pid), tx))


def hueco(base, ref):
    p = base['paquete_2027']
    tc = float(next(m for m in p['marco'] if m['v'].startswith('Tipo de cambio'))['p27'])
    bonos = round(BONOS_MDD * tc, 1)
    cubre = round(FONDEN_2026 + SEGURO + bonos, 1)
    falta = round(GRANDE - cubre, 1)
    cg = ref('ref-cgpe2027')
    filas = [
        _barra('Un desastre de los grandes', 'Probabilidad de 1% al año', GRANDE, GRANDE, '#b3261e', mmp_tx(GRANDE)),
        _barra('Uno mediano', 'Probabilidad de 5% al año', MEDIANO, GRANDE, '#c8641b', mmp_tx(MEDIANO)),
        _barra('Los frecuentes y menores', 'Cada año', FRECUENTES, GRANDE, '#a9541a', mmp_tx(FRECUENTES)),
        _pila('Lo que hay para pagarlo', 'Fondo + seguro + bonos', [
            ('Fondo de Desastres Naturales 2026', FONDEN_2026, '#4c5f45'),
            ('Seguro para catástrofes', SEGURO, '#7f9474'),
            ('Bonos catastróficos', bonos, '#a9b99a')], GRANDE, mmp_tx(cubre)),
    ]
    capas = [
        ('🏦', mdp(FONDEN_2026), 'Fondo de Desastres Naturales (Ramo 23), aprobado para 2026', 'oficial', None,
         'Presupuesto de Egresos 2026, Anexo 20 %s. Para 2027 se proponen %s (Proyecto de Presupuesto 2027, Anexo 20 %s).'
         % (ref('ref-pef2026'), mdp(FONDEN_2027), ref('ref-ppef2027'))),
        ('☂️', mdp(SEGURO), 'Seguro para catástrofes, de junio de 2026 a mayo de 2027', 'oficial', None,
         'Diez mil millones de un seguro paramétrico y 400 millones de un fondo de administración de pérdidas. Criterios 2027, p. 49 %s.' % cg),
        ('📜', '%s mdd ≈ %s' % (format(BONOS_MDD, ',.0f'), mdp(bonos)), 'Cuatro bonos catastróficos, vigentes hasta abril de 2028', 'derivado', None,
         '%s millones de dólares (oficial, Criterios 2027, p. 60 %s) × %s pesos por dólar, el tipo de cambio que los mismos Criterios prevén para 2027. '
         'Solo pagan si el sismo o el huracán rebasa los umbrales del contrato.' % (format(BONOS_MDD, ',.0f'), cg, format(tc, '.1f'))),
    ]
    hist = [(str(a), '<a href="%s" target="_blank" rel="noopener">PEF %d ↗</a>' % (u, a), v) for a, v, u in PEF_HIST]
    hist += [('2026', 'PEF 2026 ' + ref('ref-pef2026'), FONDEN_2026), ('2027', 'Propuesto ' + ref('ref-ppef2027'), FONDEN_2027)]
    tope_h = max(v for _, _, v in hist)
    hist_html = '\n'.join(_barra(a, f, v, tope_h, '#4c5f45', mdp(v)) for a, f, v in hist)
    cen = '\n'.join(_barra(str(a), nota, v, CENAPRED[0][1], '#8f1d17', pre + mdp(v, 0)) for a, v, pre, nota in CENAPRED)
    html = '''<section class="cr-sec" aria-labelledby="crHuecoTit">
        <h2 class="cr-tit" id="crHuecoTit"><span aria-hidden="true">🕳️</span> El hueco: lo que puede costar contra lo que hay</h2>
        <p class="cr-txt">Hacienda calcula cada año cuánto le costaría al gobierno federal un desastre, según qué tan probable es: son las tres primeras barras. La cuarta suma lo que hay para pagarlo: el fondo del presupuesto, el seguro y los bonos catastróficos.</p>
        <ul class="cr-hueco">
%s
        </ul>
        <p class="cr-nota">Pérdidas esperadas: Criterios Generales de Política Económica 2027, p. 51 %s %s. Lo que hay %s: fondo %s + seguro %s + bonos %s = %s.</p>
        <p class="cr-veredicto">Si llega un desastre de los grandes, faltarían <b>%s</b> %s: %s − %s. Y es el mejor caso: los bonos solo pagan si el fenómeno cumple las condiciones del contrato, y el fondo también se gasta en los desastres pequeños del año.</p>
        <h3 class="cr-sub">Las tres capas de protección</h3>
        <ul class="cr-renglones cr-capas">
%s
        </ul>
        <h3 class="cr-sub">El fondo, año por año <small>Aprobado en cada Presupuesto, en pesos de cada año</small></h3>
        <ul class="cr-hueco cr-hist">
%s
        </ul>
        <p class="cr-nota">En 2021 se extinguió el fideicomiso del FONDEN, pero el Presupuesto conserva el renglón con su nombre en el Ramo 23. Los años 2021 a 2025 todavía no los integramos %s.</p>
        <h3 class="cr-sub">Lo que de verdad costaron <small>Daños y pérdidas estimados por CENAPRED, en pesos de cada año</small></h3>
        <ul class="cr-hueco cr-cenapred">
%s
        </ul>
        <p class="cr-nota">CENAPRED, impacto socioeconómico de los desastres en 2024, p. 6 %s %s. CENAPRED publica la serie 2000-2024 solo como gráfica, sin el cuadro con la cifra de cada año %s.</p>
      </section>''' % (
        '\n'.join(filas), chip('oficial'), cg, chip('derivado'), mdp(FONDEN_2026), mdp(SEGURO), mdp(bonos), mdp(cubre),
        mdp(falta), chip('derivado'), mdp(GRANDE), mdp(cubre), '\n'.join(_renglon(*c) for c in capas), hist_html,
        pend('fonden-2021-2025'), cen, chip('oficial'), ref('ref-cenapred-impacto-2024'), pend('cenapred-serie'))
    return falta, html


def _caso(clase, ico, titulo, sub, tipo, renglones, ciego):
    return ('<article class="cr-caso %s">\n'
            '          <header class="cr-caso-cab"><span class="cr-caso-ico" aria-hidden="true">%s</span>'
            '<div><h3>%s</h3><p>%s</p></div><span class="cr-caso-tipo">%s</span></header>\n'
            '          <ul class="cr-renglones">\n%s\n          </ul>\n'
            '          <p class="cr-caso-ciego"><b>🔦 Punto ciego.</b> %s</p>\n'
            '        </article>' % (clase, ico, titulo, sub, tipo, '\n'.join(_renglon(*r) for r in renglones), ciego))


def casos(base, ref):
    dif = OTIS_PLAN - OTIS_EJ
    otis = _caso('', '🌀', 'Huracán Otis · Acapulco y Coyuca de Benítez', '24 y 25 de octubre de 2023 · Guerrero', 'Súbita', [
        ('📜', '2 municipios', 'Zona de desastre', 'oficial', None,
         'La emergencia se declaró el 30 de octubre de 2023 (%s) y el desastre el 2 de noviembre, primero para 47 municipios %s; '
         'una nota aclaratoria del día siguiente la dejó en Acapulco de Juárez y Coyuca de Benítez (%s).'
         % (fuente(DOF_OTIS_EMERG, 'DOF'), ref('ref-dof-otis-desastre'), fuente(DOF_OTIS_ACLARA, 'DOF'))),
        ('💥', mdp(OTIS_DANO, 0), 'Daños y pérdidas, según CENAPRED', 'oficial', None,
         'Cuadro 1.2 del informe de 2023 %s. El texto del mismo informe le atribuye $88,910 mdp, que es el total de todos los desastres del año: aquí se usa el cuadro.'
         % ref('ref-cenapred-impacto-2023')),
        ('📣', mdp(OTIS_PLAN, 0), 'Lo que se anunció', 'oficial', None,
         'El 1 de noviembre de 2023, Hacienda presentó el Plan General de Reconstrucción por «61 mil 313 millones de pesos», en 20 renglones; dos de ellos, «por determinar» %s.'
         % ref('ref-shcp-plan-otis')),
        ('✅', mdp(OTIS_EJ, 0), 'Lo que se informó como gastado', 'oficial', None,
         'La secretaria de Bienestar, el 13 de septiembre de 2024: «son 35 mil 17 millones de pesos para levantar estos dos municipios» (%s). El desglose que dio ese día no suma ese total.'
         % fuente(EST_OTIS_EJ, 'versión estenográfica')),
        ('➖', mdp(dif, 0), 'Lo anunciado que no aparece como gastado', 'derivado', None,
         '%s − %s. Ningún documento explica si se gastó por otra vía, si se dejó de gastar o si se reasignó %s.'
         % (mdp(OTIS_PLAN, 0), mdp(OTIS_EJ, 0), pend('otis-diferencia'))),
        ('🔍', mdp(1065.8), 'Compras sin licitación que revisó la Auditoría', 'oficial', None,
         'La ASF revisó las compras de enseres de la Defensa: 12 contratos adjudicados de manera directa por esa cifra, con bienes que no estaban en el programa de compras. '
         'Promovió una revisión fiscal y dos responsabilidades administrativas, sin fijar un monto por aclarar %s. En la revisión de 2024, de 13 resultados, 9 se solventaron y en 4 no hubo irregularidad %s.'
         % (ref('ref-asf-cp2023-0362'), ref('ref-asf-cp2024-0353'))),
        ('🧾', 'Sin publicar', 'De qué bolsa salió cada peso', 'pendiente', 'otis-financiamiento',
         'Hacienda no ha publicado cuánto se pagó con el Fondo de Desastres del Ramo 23 y cuánto con el presupuesto de cada dependencia. La Auditoría solo deja ver que las compras de la Defensa salieron de su propio ramo.'),
    ], 'Entre el daño que midió CENAPRED y lo que se informó como gastado hay una distancia esperable: no todo daño lo paga el gobierno. La que no tiene explicación es la otra, la de lo anunciado a lo gastado: %s sin un documento que diga a dónde fueron.'
       % mdp(dif, 0))
    simon = _caso('en-curso', '🌀', 'Huracán Simón · Pacífico', 'Octubre de 2026', 'En curso', [
        ('📜', 'Sin publicar', 'Declaratorias de emergencia o desastre', 'pendiente', 'simon-danos',
         'Al 11 de octubre de 2026 no hay declaratoria en el Diario Oficial (%s). Las emite la Coordinación Nacional de Protección Civil cuando el estado la solicita.' % fuente(DOF, 'DOF')),
        ('💥', 'Sin publicar', 'Daños y pérdidas', 'pendiente', 'simon-danos',
         'CENAPRED publica su estimación alrededor de un año después: la de 2024 salió en octubre de 2025. Hasta entonces, las cifras de la prensa no son datos oficiales.'),
        ('📜', '%s mdd' % format(BONO_PACIFICO_MDD, ',.0f'), 'El bono para huracanes del Pacífico', 'oficial', None,
         'Es la clase D de los cuatro bonos catastróficos (Criterios 2027, p. 60 %s). Paga solo si el huracán cumple las condiciones del contrato.' % ref('ref-cgpe2027')),
    ], 'Las cifras de daños que circulan estos días vienen de la prensa: la oficial tarda alrededor de un año. Esta ficha se completará con cada documento que se publique: la declaratoria, el primer gasto y, si se activa, el pago del bono.')
    gdl = _caso('cronica', '🚱', 'El agua de Guadalajara', '2026 · Área Metropolitana de Guadalajara, Jalisco', 'Crónica', [
        ('🔁', '6 meses', 'Rotación del servicio', 'oficial', None,
         'Mientras se deja de usar el sistema de Las Pintas, que aporta hasta 2.5 metros cúbicos por segundo, el servicio se rotará en una primera etapa «con una duración estimada de seis meses» '
         '(Gobierno de Jalisco, 6 de octubre de 2026, %s).' % fuente(JAL_ROTACION, 'comunicado')),
        ('🏗️', 'más de $20,000 mdp', 'El plan integral de junio', 'oficial', None,
         '«Cuya inversión conjunta supera los 20 mil millones de pesos» (Gobierno de Jalisco, 29 de junio de 2026, %s). El Plan Hídrico llegó al Congreso el 14 de julio sin decir cómo se pagaría: '
         '«la discusión sobre los mecanismos para financiar las obras se desarrollará posteriormente» (%s).' % (fuente(JAL_PLAN, 'comunicado'), fuente(JAL_HIDRICO, 'comunicado'))),
        ('🧾', 'Sin publicar', 'El costo de cada acción del Plan Hídrico', 'pendiente', 'gdl-plan-costos',
         'La prensa citó un total de $42,101 mdp, tomado de anexos del plan que el Gobierno de Jalisco no ha publicado. Sin el documento, esa cifra no entra aquí.'),
        ('💧', mdp(11922, 0), 'Acueducto Sustituto Chapala–Guadalajara', 'oficial', None,
         'Inversión estimada en la iniciativa entregada al Congreso el 8 de octubre de 2026 (%s). Ese día, la Presidenta dijo del gobierno de Jalisco: «quieren hacer una parte con deuda» (%s).'
         % (fuente(JAL_ACUEDUCTO, 'comunicado'), fuente(PRES_0810, 'versión estenográfica'))),
        ('🏭', mdp(7500, 0), 'Planta Potabilizadora 1', 'oficial', None,
         '«Con una inversión de 7 mil 500 millones de pesos de recurso estatal» (Gobierno de Jalisco, 26 de agosto de 2026, %s).' % fuente(JAL_ZAPOTILLO, 'comunicado')),
        ('🚧', '45%', 'El Zapotillo', 'oficial', None,
         'El gobernador dijo el 6 de octubre que «actualmente opera al 45 por ciento» y que lo pendiente será «ejecutado y pagado por la Federación» (%s). '
         'El monto cambia de un comunicado a otro y la Federación no ha publicado cuánto pondrá %s.' % (fuente(JAL_ROTACION, 'comunicado'), pend('gdl-zapotillo'))),
        ('🏘️', 'Sin publicar', 'Colonias afectadas', 'pendiente', 'gdl-colonias',
         'El SIAPA no ha publicado cuántas colonias reciben agua de mala calidad ni cuántas entran a la rotación. Las cifras que circulan (342, más de 400) no vienen de un documento oficial.'),
        ('🧪', 'Sin publicar', 'Resultados de laboratorio del agua', 'pendiente', 'gdl-calidad',
         'Salud Jalisco explicó cómo toma las muestras, pero no ha publicado los resultados. Sí informó 54,869 casos de enfermedad gastrointestinal en 2026 contra 56,448 en 2025, «sin incremento atípico» (%s).'
         % fuente(JAL_SALUD, 'comunicado')),
    ], 'Una misma obra tiene varios precios según el comunicado, el total del plan solo se conoce por la prensa y nadie ha publicado cuántas casas reciben agua sucia. Lo que sí está documentado suma ya %s en solo dos obras.'
       % mdp(11922 + 7500, 0))
    gym = _caso('en-curso', '🚢', 'Golfo de California · Proyecto AMIGO en Guaymas', '2026 · Guaymas, Sonora', 'En litigio', [
        ('📍', '41.7 ha', 'El terreno, según la Secretaría de Energía', 'oficial', None,
         'En el Parque Industrial Pesquero «General Rodolfo Sánchez Taboada», el 0.005 %% del municipio (%s). '
         'En redes circulan 54 hectáreas en comodato gratuito: <a href="noticias-auditavision.html#col-%s">lo cotejamos en Verificamos</a>.'
         % (fuente(PRES_2110, 'versión estenográfica del 21-10-2026'), COL_GUAYMAS)),
        ('🚢', '60 al año', 'Buques metaneros, como máximo', 'oficial', None,
         'Cinco al mes, el 4 %% de las embarcaciones que ya cruzan la zona; almacenamiento para 290 mil metros cúbicos de gas (%s).'
         % fuente(PRES_2110, 'versión estenográfica del 21-10-2026')),
        ('⚖️', 'Detenida', 'La obra, por amparos', 'oficial', None,
         'La Presidenta: «ahorita se paró, como hay amparos» y «no hay ningún daño ambiental» (%s); el 21 de octubre dijo que se revisan otra vez los impactos (%s).'
         % (fuente(PRES_1610, '16-10-2026'), fuente(PRES_2110, '21-10-2026'))),
        ('🌿', 'Sin publicar', 'El resolutivo de impacto ambiental', 'pendiente', 'red-%s-8' % COL_GUAYMAS,
         'Lo emite la ASEA, que también está en el <a href="herramienta-ambiente-auditor.html#aa-G00">Auditor ambiental</a> con su presupuesto. '
         'La prensa reporta versiones distintas sobre si ya se otorgó; no lo pudimos abrir.'),
        ('📄', 'Sin publicar', 'El contrato del terreno', 'pendiente', 'red-%s-1' % COL_GUAYMAS,
         'El Gobierno de Sonora no ha transparentado el comodato que reporta la prensa ni su estado jurídico.'),
        ('🏛️', '12-02-2026', 'El exhorto del Congreso de Sonora', 'oficial', None,
         'Diputados del PAN y de MC pidieron a la ASEA, al INECC y a la Semarnat revisar el impacto de los tres proyectos de gas del Golfo (Saguaro, AMIGO y Vista Pacífico). '
         'No se aprobó como urgente y se turnó a comisión (%s).' % fuente(GACETA_SON_2104, 'Gaceta No. 2104')),
    ], 'Nadie ha publicado cuánto pagaría el proyecto en impuestos y derechos ni cuánto dejaría en Sonora, y el estudio que diría cuánto riesgo corren las ballenas y la pesca es justo lo que está en litigio. '
       'Sin esos dos documentos no se puede hacer la cuenta de quién gana y quién pierde.')
    return '''<section class="cr-sec" aria-labelledby="crCasosTit">
        <h2 class="cr-tit" id="crCasosTit"><span aria-hidden="true">📂</span> Los casos, ficha por ficha</h2>
        <p class="cr-txt">Cada ficha sigue el mismo orden: qué se declaró, cuánto se dañó, cuánto se anunció, cuánto se comprobó y qué sigue sin publicarse. Lo que solo dijo la prensa no entra como cifra.</p>
        <div class="cr-casos">
        %s
        %s
        %s
        %s
        </div>
      </section>''' % (gym, otis, simon, gdl)


def fondo(base, ref):
    e = base['cuentas_ecologicas']
    ar = next(c for c in e['degradacion']['componentes'] if c['id'] == 'aguas_residuales')
    sub = next(c for c in e['agotamiento']['componentes'] if c['id'] == 'agua')
    dia = round(ar['monto_mdp'] / 366, 1)
    veces = ar['monto_mdp'] / FONDEN_2026
    r = ref(e['ref_fuente'])
    tarjetas = [
        ('🚱', mdp(ar['monto_mdp'], 0), 'Lo que costó en 2024 devolver agua sin tratar a ríos y presas.', chip(ar['estado']) + ' ' + r),
        ('💧', mdp(sub['monto_mdp'], 0), 'Lo que costó en 2024 sacar de los acuíferos más agua de la que se repone.', chip(sub['estado']) + ' ' + r),
        ('📅', mdp(dia), 'Cada día, solo por el agua sin tratar: %s ÷ 366 días de 2024.' % mdp(ar['monto_mdp'], 0), chip('derivado')),
    ]
    html = '\n'.join('          <div class="cr-fondo-c"><span class="cr-f-ico" aria-hidden="true">%s</span><b>%s</b><small>%s</small>%s</div>' % t
                     for t in tarjetas)
    return '''<section class="cr-sec" aria-labelledby="crFondoTit">
        <h2 class="cr-tit" id="crFondoTit"><span aria-hidden="true">🌊</span> El daño de fondo: el agua, todos los años</h2>
        <p class="cr-txt">Las crisis como la de Guadalajara no empiezan el día que sale agua sucia de la llave. El INEGI mide cada año lo que le cuesta al país tratar mal su agua %s.</p>
        <div class="cr-fondo">
%s
        </div>
        <p class="cr-veredicto">Solo el agua que se devuelve sin tratar cuesta cada año <b>%s veces</b> el Fondo de Desastres Naturales de 2026 %s: %s ÷ %s.</p>
      </section>''' % (r, html, format(veces, '.1f'), chip('derivado'), mdp(ar['monto_mdp'], 0), mdp(FONDEN_2026))


FALTA = [
    ('otis-diferencia', 'Hacienda y Bienestar', 'explicar qué pasó con los $26,296 mdp anunciados para Otis que no aparecen como gastados.'),
    ('otis-financiamiento', 'Hacienda', 'publicar de qué ramo salió cada peso de la atención a Otis.'),
    ('simon-danos', 'Protección Civil y CENAPRED', 'publicar las declaratorias y los daños del huracán Simón.'),
    ('gdl-plan-costos', 'El Gobierno de Jalisco', 'publicar el costo de cada acción del Plan Hídrico.'),
    ('gdl-zapotillo', 'Conagua y el Gobierno de Jalisco', 'publicar cuánto cuesta terminar El Zapotillo y quién lo paga.'),
    ('gdl-colonias', 'El SIAPA', 'publicar cuántas colonias reciben agua de mala calidad.'),
    ('gdl-calidad', 'Salud Jalisco', 'publicar los resultados de laboratorio del agua.'),
    ('cenapred-serie', 'CENAPRED', 'publicar en cuadro, y no solo en gráfica, la serie anual de daños 2000-2024.'),
    ('fonden-2021-2025', 'Auditavisión', 'integrar el Fondo de Desastres de los Presupuestos 2021 a 2025.'),
]


def pagina(base, ref):
    """El bloque de la pagina (lo envuelve apartados.herramienta_modulo)."""
    falta_hueco, h = hueco(base, ref)
    ejemplos = [
        ('El hueco de un desastre grande', falta_hueco, 'derivado, de esta página'),
        ('Un desastre grande, completo', GRANDE, 'oficial, Criterios 2027'),
        ('El daño de Otis', OTIS_DANO, 'oficial, CENAPRED'),
        ('El Acueducto Chapala–Guadalajara', 11922.0, 'oficial, Gobierno de Jalisco'),
    ]
    familias = '''<div class="cr-familias">
        <div class="cr-familia"><h3>🌀 Las súbitas</h3><p>Llegan en días: huracanes, sismos, inundaciones. Las paga primero el Fondo de Desastres Naturales, después el seguro y los bonos, y lo que falta sale de recortes o de deuda.</p></div>
        <div class="cr-familia cronica"><h3>🚱 Las crónicas</h3><p>Se acumulan en años: agua sucia, ríos contaminados, acuíferos vacíos. No tienen fondo propio: se pagan con obras de emergencia, tandeos y salud.</p></div>
      </div>'''
    falta = '\n'.join('          <li>%s<span><b>%s</b>: falta %s</span></li>' % (chip('pendiente', i), q, t) for i, q, t in FALTA)
    return '\n      '.join([
        '<div class="cr">',
        familias,
        h,
        calculadora(base, ref, ejemplos),
        casos(base, ref),
        fondo(base, ref),
        '''<section class="cr-sec" aria-labelledby="crFaltaTit">
        <h2 class="cr-tit" id="crFaltaTit"><span aria-hidden="true">🗂️</span> Lo que falta transparentar</h2>
        <p class="cr-txt">Cada etiqueta lleva a su ficha en el <a href="pendientes.html">Registro de pendientes</a>: qué falta, por qué y dónde debería estar.</p>
        <ul class="cr-falta">
%s
        </ul>
      </section>''' % falta,
        '</div>'])
