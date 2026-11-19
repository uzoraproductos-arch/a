/* Auditavisión · Calculadora Cívica › Inviertes en la bolsa (19-11-2026).
   La página la escribe herramientas/cc_bolsa.py con el INPC de la base en #cbDatos.
   Aquí solo se hace la cuenta de los arts. 129 y 140 de la LISR y 17-A del CFF.
   Nada se guarda ni se envía. AuditorBolsa.calcula() se expone para las pruebas. */
(function () {
  'use strict';

  function calcula(D, x) {
    /* x: {V, cv, va, vm, C, ca, cm, O, P, Div} */
    var pasos = [], avisos = [];
    var r4 = function (v) { return Math.round(v * 10000) / 10000; };
    function inpc(a, m) {
      var s = D.inpc[a];
      return s && s[m - 1] != null ? s[m - 1] : null;
    }
    var res = { pasos: pasos, avisos: avisos, isr: 0, ret: 0 };
    if (x.V != null) {
      if ((x.ca * 12 + x.cm) > (x.va * 12 + x.vm)) return { error: 'La compra no puede ser después de la venta.' };
      /* Art. 129, inciso a): actualizar hasta el mes inmediato anterior a la venta; CFF 17-A, si no se ha publicado, el último. */
      var fa = x.vm === 1 ? x.va - 1 : x.va, fm = x.vm === 1 ? 12 : x.vm - 1;
      var ifin = inpc(fa, fm), finTxt = fm + '/' + fa;
      if (ifin == null) {
        ifin = inpc(D.inpc_ult[0], D.inpc_ult[1]);
        finTxt = D.inpc_ult[1] + '/' + D.inpc_ult[0];
        avisos.push('El INPC del mes anterior a la venta aún no está en la base: se usa el último publicado (' + finTxt + '), como manda el CFF, art. 17-A.');
      }
      var i0 = inpc(x.ca, x.cm);
      if (i0 == null) return { error: 'No hay INPC para el mes de la compra: la base lo trae desde enero de 1988.' };
      var F = Math.max(1, r4(ifin / i0));
      var costo = x.C * F, neta = x.V - (x.cv || 0);
      pasos.push(['Lo que recibiste, menos las comisiones de la venta', neta, 'LISR, art. 129, inciso a']);
      pasos.push(['Factor de actualización: INPC ' + finTxt + ' ÷ INPC ' + x.cm + '/' + x.ca, F, 'CFF, art. 17-A', 'f']);
      pasos.push(['Costo de las acciones, actualizado', costo, 'LISR, art. 129, inciso a']);
      var g1 = neta - costo;
      pasos.push([g1 >= 0 ? 'Ganancia de esta venta' : 'Pérdida de esta venta', g1, 'LISR, art. 129, inciso a', 'b']);
      if (x.ca < 2014) avisos.push('Compraste antes de 2014: la ley te deja tomar como costo el promedio de los últimos 22 precios de cierre de 2013 (transitorio 2014, fr. XXXII), que puede bajar tu ganancia. Aquí usamos lo que pagaste.');
      var g = g1;
      if (x.O) {
        g += x.O;
        pasos.push(['Más la ganancia o pérdida de tus otras ventas del año', x.O, 'LISR, art. 129']);
        pasos.push([g >= 0 ? 'Ganancia del año' : 'Pérdida del año', g, 'LISR, art. 129', 'b']);
      }
      res.g = g;
      if (g <= 0) {
        res.perdida = true;
        if (x.P > 0) avisos.push('Con pérdida en el año, tus pérdidas anteriores siguen pendientes.');
      } else {
        var base = g;
        if (x.P > 0) {
          var dis = Math.min(x.P, g);
          base = g - dis;
          pasos.push(['Menos pérdidas de años anteriores (hasta lo que ganaste)', -dis, 'LISR, art. 129']);
          if (x.P > dis) avisos.push('Te quedan ' + Number(x.P - dis).toLocaleString('es-MX', { style: 'currency', currency: 'MXN' }) + ' de pérdidas para los años siguientes, si no han pasado diez.');
        }
        res.isr = 0.10 * base;
        pasos.push(['ISR de tus acciones: 10 % de ' + Number(base).toLocaleString('es-MX', { style: 'currency', currency: 'MXN' }), res.isr, 'LISR, art. 129', 'b']);
      }
    }
    if (x.Div > 0) {
      res.ret = 0.10 * x.Div;
      res.acred = x.Div * D.factor_div * D.tasa_pm / 100;
      res.acum = x.Div + res.acred;
      pasos.push(['Dividendos: retención definitiva de 10 %', res.ret, 'LISR, art. 140, segundo párrafo', 'b']);
      pasos.push(['Para tu anual: ISR que pagó la empresa (' + D.tasa_pm + ' % de dividendo × ' + D.factor_div + '), que puedes restar', res.acred, 'LISR, arts. 9 y 140']);
      pasos.push(['Para tu anual: lo que sumas a tus ingresos (dividendo + ese ISR)', res.acum, 'LISR, art. 140, primer párrafo']);
      avisos.push('Si el dividendo sale de utilidades de antes de 2014, no lleva el 10 % adicional (transitorio 2014, fr. XXX): lo dice la constancia de la empresa.');
    }
    return res;
  }

  window.AuditorBolsa = { calcula: calcula };

  var raiz = document.getElementById('cbRaiz');
  if (!raiz) return;
  var D = JSON.parse(document.getElementById('cbDatos').textContent);
  var $ = function (id) { return document.getElementById(id); };
  function num(id, neg) {
    var s = ($(id).value || '').replace(/[$,\s]/g, '').replace(/−/g, '-');
    if (s === '') return null;
    var v = Number(s);
    return isFinite(v) && (neg || v >= 0) ? v : NaN;
  }
  function pesos(v) {
    return (v < 0 ? '−' : '') + '$' + Math.abs(Number(v)).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* Lo que llega por la dirección (?v=&c=&ca=&div=), para que el chat abra la cuenta ya puesta. */
  try {
    var q = new URLSearchParams(location.search);
    [['v', 'cbV'], ['c', 'cbC'], ['ca', 'cbCa'], ['cm', 'cbCm'], ['va', 'cbVa'], ['vm', 'cbVm'], ['div', 'cbD']].forEach(function (p) { if (q.get(p[0])) $(p[1]).value = q.get(p[0]); });
  } catch (e) { /* sin parámetros */ }
  var hoy = new Date();
  if (location.search.indexOf('vm=') < 0 && hoy.getFullYear() === +$('cbVa').value) $('cbVm').value = String(hoy.getMonth() + 1);

  function pinta(e) {
    if (e) e.preventDefault();
    var x = { V: num('cbV'), cv: num('cbCv') || 0, va: +$('cbVa').value, vm: +$('cbVm').value, C: num('cbC'), ca: +$('cbCa').value, cm: +$('cbCm').value,
      O: num('cbO', true) || 0, P: num('cbP') || 0, Div: num('cbD') || 0 };
    var res = $('cbRes'), tot = $('cbTotal');
    res.hidden = false;
    var malo = [x.V, x.C, x.cv, x.O, x.P, x.Div].some(function (v) { return typeof v === 'number' && isNaN(v); });
    var venta = x.V != null && x.C != null;
    if (malo || (!venta && !(x.Div > 0)) || (x.V != null) !== (x.C != null)) {
      tot.innerHTML = '<p class="ci-error">Escribe, con números, lo que recibiste por la venta y lo que pagaste al comprar, o tus dividendos.</p>';
      $('cbPasos').innerHTML = ''; $('cbNota').textContent = '';
      return;
    }
    if (!venta) x.V = null;
    var r = calcula(D, x);
    if (r.error) {
      tot.innerHTML = '<p class="ci-error">' + esc(r.error) + '</p>';
      $('cbPasos').innerHTML = ''; $('cbNota').textContent = '';
      return;
    }
    var h = '';
    if (venta) {
      if (r.perdida) h += '<p class="ci-cifra">Por tus acciones: <b>sin ISR</b>, el año deja pérdida (' + pesos(-r.g) + ').</p><p>Pide a tu casa de bolsa la constancia de la pérdida: la puedes restar de tus ganancias de los diez años siguientes (LISR, art. 129).</p>';
      else h += '<p class="ci-cifra">ISR por tus acciones: <b>' + pesos(r.isr) + '</b></p><p>Es pago definitivo y se declara con tu declaración anual (LISR, arts. 129 y 150).</p>';
    }
    if (x.Div > 0) h += '<p class="ci-cifra">Retención por tus dividendos: <b>' + pesos(r.ret) + '</b></p><p>La empresa te la retiene y la entera; es definitiva (LISR, art. 140).</p>';
    tot.innerHTML = h;
    $('cbPasos').innerHTML = r.pasos.map(function (p) {
      var v = p[3] === 'f' ? Number(p[1]).toFixed(4) : pesos(p[1]);
      return '<tr' + (p[3] === 'b' ? ' class="ci-fuerte"' : '') + '><th scope="row">' + esc(p[0]) + '</th><td>' + v + '</td><td>' + esc(p[2]) + '</td></tr>';
    }).join('');
    $('cbNota').textContent = r.avisos.concat(['Es una cuenta aproximada (derivado). La cuenta oficial es la constancia de tu casa de bolsa y la de la empresa que te pagó dividendos.']).join(' ');
  }
  $('cbForm').addEventListener('submit', pinta);
  if ((num('cbV') && num('cbC') != null) || num('cbD') > 0) pinta();
})();
