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

from presupuesto_modulos import chip, mdp, pct

ARCHIVO = 'herramienta-ambiente-crisis.html'


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def pend(id_):
    return chip('pendiente', id_)


def fuente(url, texto):
    return '<a href="%s" target="_blank" rel="noopener">%s ↗</a>' % (url, texto)


# ---------------------------------------------------------------------------
# Las fichas. Cada renglon: (rotulo, cifra o None, estado, id de pendiente o
# None, explicacion con su fuente). Se llenan solo con lo verificado en el
# documento oficial (ver CASOS_FUENTES en CONTEXT.md).
# ---------------------------------------------------------------------------
CASOS = []


def _hueco(base, ref):
    p = base['paquete_2027']
    des = next(c for c in p['contingentes'] if c['n'].startswith('Pérdida esperada por desastres'))
    return des


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


def pagina(base, ref):
    """Devuelve el bloque HTML de la pagina (lo envuelve herramienta_modulo)."""
    raise NotImplementedError
