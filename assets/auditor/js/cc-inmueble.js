/* Auditavisión · Calculadora Cívica › Vendes una casa o un terreno (19-11-2026).
   La página la escribe herramientas/cc_inmueble.py con los datos de la base en #ciDatos
   (INPC de Banxico, tarifa mensual del art. 96 de 2026 y la UDI). Aquí solo se hace la
   cuenta de los arts. 93-XIX-a, 121, 124, 126 y 127 de la LISR y 17-A del CFF.
   Nada se guarda ni se envía. AuditorInmueble.calcula() se expone para las pruebas. */
(function () {
  'use strict';

  function calcula(D, x) {
    /* x: {V, vm, C, ca, cm, pT, M, ma, mm, Gc, Gv, casa} */
    var pasos = [], avisos = [];
    var r4 = function (v) { return Math.round(v * 10000) / 10000; };
    function inpc(a, m) {
      var s = D.inpc[a];
      return s && s[m - 1] != null ? s[m - 1] : null;
    }
    /* CFF 17-A: el INPC del mes anterior a la venta; si no se ha publicado, el último publicado. */
    var fa = x.vm === 1 ? D.anio - 1 : D.anio, fm = x.vm === 1 ? 12 : x.vm - 1;
    var ifin = inpc(fa, fm), finTxt = fm + '/' + fa;
    if (ifin == null) {
      ifin = inpc(D.inpc_ult[0], D.inpc_ult[1]);
      finTxt = D.inpc_ult[1] + '/' + D.inpc_ult[0];
      avisos.push('El INPC del mes anterior a la venta aún no está en la base: se usa el último publicado (' + finTxt + '), como manda el CFF, art. 17-A.');
    }
    function factor(a, m) {
      var i0 = inpc(a, m);
      if (i0 == null) return null;
      return Math.max(1, r4(ifin / i0));
    }
    function anios(a, m) {
      var meses = 12 * (D.anio - a) + (x.vm - m);
      return meses < 0 ? -1 : Math.floor(meses / 12);
    }
    var n = anios(x.ca, x.cm);
    if (n < 0) return { error: 'La compra no puede ser después de la venta.' };
    var F = factor(x.ca, x.cm);
    if (F == null) return { error: 'No hay INPC para el mes de la compra: la base lo trae desde enero de 1988.' };

    /* Art. 124: terreno y construcción. */
    var pT = x.pT == null ? 20 : x.pT;
    var T = x.C * pT / 100, K = x.C - T;
    var Kdep = Math.max(K * (1 - 0.03 * n), 0.2 * K);
    pasos.push(['Costo del terreno (' + pT + ' %' + (x.pT == null ? ', el que fija la ley si no se puede separar' : '') + ')', T, 'LISR, art. 124, fr. I']);
    if (K > 0) pasos.push(['Construcción, menos 3 % por ' + n + ' año' + (n === 1 ? '' : 's') + ' (sin bajar de 20 %)', Kdep, 'LISR, art. 124, fr. II']);
    pasos.push(['Factor de actualización: INPC ' + finTxt + ' ÷ INPC ' + x.cm + '/' + x.ca, F, 'CFF, art. 17-A', 'f']);
    var costo = (T + Kdep) * F, piso = 0.1 * x.V;
    pasos.push(['Costo actualizado', costo, 'LISR, art. 124']);
    if (costo < piso) {
      costo = piso;
      pasos.push(['Sube al mínimo: 10 % del precio de venta', costo, 'LISR, art. 121, fr. I']);
    }
    var ded = costo;
    if (x.M > 0) {
      var nm = anios(x.ma, x.mm), Fm = factor(x.ma, x.mm);
      if (nm < 0 || Fm == null) return { error: 'Revisa la fecha de la mejora: tiene que ser antes de la venta y desde 1988.' };
      var Md = Math.max(x.M * (1 - 0.03 * nm), 0.2 * x.M) * Fm;
      pasos.push(['Mejoras: menos 3 % por ' + nm + ' año' + (nm === 1 ? '' : 's') + ', actualizadas (factor ' + Fm.toFixed(4) + ')', Md, 'LISR, arts. 121, fr. II y 124, fr. II']);
      ded += Md;
    }
    if (x.Gc > 0) {
      var Gc = x.Gc * F;
      pasos.push(['Gastos de la compra, actualizados', Gc, 'LISR, art. 121, fr. III']);
      ded += Gc;
    }
    if (x.Gv > 0) {
      pasos.push(['Gastos y comisiones de la venta', x.Gv, 'LISR, art. 121, frs. III y IV']);
      ded += x.Gv;
    }
    pasos.push(['Total que se deduce', ded, 'LISR, art. 121', 'b']);
    var G = x.V - ded;
    var lim = D.udi.v * D.exento_udis, exento = false, prop = 1;
    if (x.casa) {
      if (x.V <= lim) exento = true;
      else prop = r4((x.V - lim) / x.V);
    }
    pasos.push(['Ganancia: precio de venta − lo que se deduce', G, 'LISR, art. 121', 'b']);
    var res = { pasos: pasos, avisos: avisos, n: n, G: G, lim: lim, exento: exento };
    if (G <= 0) {
      res.perdida = true; res.isr = 0; res.edo = 0; res.fed = 0;
      return res;
    }
    if (exento) {
      res.isr = 0; res.edo = 0; res.fed = 0;
      return res;
    }
    if (prop < 1) {
      G = G * prop;
      pasos.push(['Ganancia gravada: solo la parte del precio que pasa de 700,000 UDIS (proporción ' + prop.toFixed(4) + ')', G, 'LISR, art. 93, fr. XIX, a', 'b']);
    }
    /* Art. 126: la ganancia entre los años (1 a 20), la tarifa mensual por los meses del año, y por los mismos años. */
    var div = Math.min(Math.max(n, 1), 20);
    var base = G / div, m = x.vm, fila = null;
    D.tarifa.forEach(function (t) {
      if (base >= t.li * m && (t.ls == null || base <= t.ls * m + 0.0049)) fila = t;
    });
    if (!fila) fila = D.tarifa[D.tarifa.length - 1];
    var isr1 = fila.cf * m + (base - fila.li * m) * fila.pct / 100;
    var isr = isr1 * div;
    pasos.push(['Ganancia entre ' + div + ' año' + (div === 1 ? '' : 's'), base, 'LISR, art. 126']);
    pasos.push(['Tarifa del art. 96 × ' + m + ' mes' + (m === 1 ? '' : 'es') + ': cuota ' + (fila.cf * m).toFixed(2) + ' + ' + fila.pct + ' % sobre lo que pasa de ' + (fila.li * m).toFixed(2), isr1, 'LISR, arts. 96 y 126']);
    pasos.push(['Pago provisional: × ' + div + ' año' + (div === 1 ? '' : 's'), isr, 'LISR, art. 126', 'b']);
    var edo = Math.min(0.05 * G, isr);
    pasos.push(['A tu estado: 5 % de la ganancia' + (0.05 * G > isr ? ' (topado al pago provisional)' : ''), edo, 'LISR, art. 127']);
    pasos.push(['A la Federación: el resto', isr - edo, 'LISR, art. 127']);
    res.isr = isr; res.edo = edo; res.fed = isr - edo;
    return res;
  }

  window.AuditorInmueble = { calcula: calcula };

  var raiz = document.getElementById('ciRaiz');
  if (!raiz) return;
  var D = JSON.parse(document.getElementById('ciDatos').textContent);
  var $ = function (id) { return document.getElementById(id); };
  function num(id) {
    var s = ($(id).value || '').replace(/[$,\s]/g, '');
    if (s === '') return null;
    var v = Number(s);
    return isFinite(v) && v >= 0 ? v : NaN;
  }
  function pesos(v, dec) {
    return '$' + Number(v).toLocaleString('es-MX', { minimumFractionDigits: dec == null ? 2 : dec, maximumFractionDigits: dec == null ? 2 : dec });
  }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* Lo que llega por la dirección (?v=&c=&ca=&cm=&vm=&casa=1), para que el chat abra la cuenta ya puesta. */
  try {
    var q = new URLSearchParams(location.search);
    [['v', 'ciV'], ['c', 'ciC'], ['ca', 'ciCa'], ['cm', 'ciCm'], ['vm', 'ciVm'], ['t', 'ciT']].forEach(function (p) { if (q.get(p[0])) $(p[1]).value = q.get(p[0]); });
    if (q.get('casa') === '1') $('ciCasa').checked = true;
  } catch (e) { /* sin parámetros */ }
  var hoy = new Date();
  if (hoy.getFullYear() === D.anio && location.search.indexOf('vm=') < 0) $('ciVm').value = String(hoy.getMonth() + 1);

  function pinta(e) {
    if (e) e.preventDefault();
    var x = { V: num('ciV'), C: num('ciC'), vm: +$('ciVm').value, ca: +$('ciCa').value, cm: +$('ciCm').value, pT: num('ciT'),
      M: num('ciM') || 0, ma: +$('ciMa').value, mm: +$('ciMm').value, Gc: num('ciGc') || 0, Gv: num('ciGv') || 0, casa: $('ciCasa').checked };
    var res = $('ciRes'), tot = $('ciTotal');
    res.hidden = false;
    if (!x.V || !(x.C >= 0) || isNaN(x.V) || isNaN(x.C) || (x.pT != null && (isNaN(x.pT) || x.pT > 100))) {
      tot.innerHTML = '<p class="ci-error">Escribe el precio de venta y lo que pagaste al comprar, con números. El terreno va de 0 a 100 %.</p>';
      $('ciPasos').innerHTML = ''; $('ciNota').textContent = '';
      return;
    }
    var r = calcula(D, x);
    if (r.error) {
      tot.innerHTML = '<p class="ci-error">' + esc(r.error) + '</p>';
      $('ciPasos').innerHTML = ''; $('ciNota').textContent = '';
      return;
    }
    var h;
    if (r.perdida) h = '<p class="ci-cifra">Sin ISR por pagar: <b>no hay ganancia</b> (pierdes ' + pesos(-r.G) + ').</p><p>La pérdida se puede aprovechar en tu declaración anual (LISR, art. 122).</p>';
    else if (r.exento) h = '<p class="ci-cifra">Sin ISR por pagar: <b>tu casa habitación está exenta</b>.</p><p>La vendes en hasta 700,000 UDIS (' + pesos(r.lim) + ' con la UDI del ' + esc(D.udi.f) + '). La exención pide que la venta sea ante notario y que no hayas exentado otra casa en los tres años anteriores (LISR, art. 93, fr. XIX, a).</p>';
    else h = '<p class="ci-cifra">Pago provisional de ISR: <b>' + pesos(r.isr) + '</b></p><p>De eso, ' + pesos(r.edo) + ' van a tu estado y ' + pesos(r.fed) + ' a la Federación. Lo retiene y lo entera el notario dentro de los 15 días siguientes a la firma de la escritura (LISR, art. 126).</p>';
    tot.innerHTML = h;
    $('ciPasos').innerHTML = r.pasos.map(function (p) {
      var v = p[3] === 'f' ? Number(p[1]).toFixed(4) : pesos(p[1]);
      return '<tr' + (p[3] === 'b' ? ' class="ci-fuerte"' : '') + '><th scope="row">' + esc(p[0]) + '</th><td>' + v + '</td><td>' + esc(p[2]) + '</td></tr>';
    }).join('');
    $('ciNota').textContent = r.avisos.concat(['Es una cuenta aproximada (derivado) con los años completos que pasaron (' + r.n + '). Tu notario hace la definitiva, y tu declaración anual puede dar otro impuesto.']).join(' ');
  }
  $('ciForm').addEventListener('submit', pinta);
  if (num('ciV') && num('ciC') != null) pinta();
})();
