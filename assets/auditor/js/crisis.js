/* Auditavisión · Herramientas › Costo Ambiental › Crisis ambientales
   (quinta aplicación, 11-10-2026). La página llega escrita por
   herramientas/crisis_ambientales.py y las cifras oficiales, en JSON dentro
   de la página (#crDatos): aquí no se escribe ninguna cifra. Este archivo
   solo mueve la calculadora «Lo que cuesta esperar»: el lector pone un monto
   (o carga uno de la página) y una tasa oficial, y ve cuánto suman los
   intereses si ese hueco se cubre con deuda. */
(function () {
  'use strict';

  var D;
  try { D = JSON.parse(document.getElementById('crDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  var monto = $('crMonto'), anios = $('crAnios'), salida = $('crSalida');
  if (!monto || !anios || !salida) return;

  function num(v, d) { return v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function mdp(v) { return '$' + num(v, 1) + ' mdp'; }
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function tasa() {
    var r = document.querySelector('input[name="crTasa"]:checked');
    var t = D.tasas[0];
    if (r) D.tasas.forEach(function (x) { if (x.id === r.value) t = x; });
    return t;
  }
  function valor() {
    var v = parseFloat(String(monto.value).replace(/[^0-9.]/g, ''));
    return isFinite(v) && v > 0 ? v : 0;
  }

  function pinta() {
    var m = valor(), n = parseInt(anios.value, 10) || 1, t = tasa(), r = t.v / 100;
    $('crAniosTx').textContent = n + (n === 1 ? ' año' : ' años');
    if (!m) {
      salida.innerHTML = '<p class="cr-vacio">Escribe un monto o carga uno de los ejemplos: aquí verás cuánto cuesta esperar.</p>';
      return;
    }
    var anual = m * r;
    var simple = anual * n;
    var comp = m * (Math.pow(1 + r, n) - 1);
    /* Barras: lo que se debe (el hueco) y lo que se paga encima, año por año. */
    var filas = [], tope = m + comp, k;
    var marcas = n <= 10 ? null : [1, 5, 10, 15, 20, 25, 30].filter(function (x) { return x <= n; });
    for (k = 1; k <= n; k++) {
      if (marcas && marcas.indexOf(k) < 0 && k !== n) continue;
      var c = m * (Math.pow(1 + r, k) - 1);
      filas.push('<li><span class="cr-b-anio">Año ' + k + '</span><span class="cr-b-barra">' +
        '<span class="cr-b-base" style="width:' + (m / tope * 100).toFixed(2) + '%"></span>' +
        '<span class="cr-b-int" style="width:' + (c / tope * 100).toFixed(2) + '%"></span></span>' +
        '<span class="cr-b-tx">' + mdp(c) + '</span></li>');
    }
    salida.innerHTML =
      '<div class="cr-res">' +
        '<div class="cr-res-c"><small>Intereses del primer año</small><b>' + mdp(anual) + '</b><span>' + mdp(m) + ' × ' + num(t.v, 2) + '%</span></div>' +
        '<div class="cr-res-c"><small>En ' + n + (n === 1 ? ' año' : ' años') + ', si cada año se pagan los intereses</small><b>' + mdp(simple) + '</b><span>' + mdp(anual) + ' × ' + n + '</span></div>' +
        '<div class="cr-res-c cr-res-fuerte"><small>En ' + n + (n === 1 ? ' año' : ' años') + ', si los intereses también se piden prestados</small><b>' + mdp(comp) + '</b><span>' + mdp(m) + ' × ((1 + ' + num(t.v, 2) + '%)<sup>' + n + '</sup> − 1)</span></div>' +
      '</div>' +
      '<ul class="cr-barras" aria-label="Intereses acumulados, año por año">' + filas.join('') + '</ul>' +
      '<p class="cr-leyenda"><span class="cr-l-base"></span> El hueco que se cubrió con deuda <span class="cr-l-int"></span> Los intereses acumulados</p>' +
      '<p class="cr-aviso">Es un <b>cálculo con tus datos</b>: el monto lo pones tú y se usa ' + esc(t.nom) + ' (' + esc(t.est) + '). ' + esc(t.op) + ' No es una cifra publicada por el gobierno.</p>';
  }

  document.querySelectorAll('[data-cr-monto]').forEach(function (b) {
    b.addEventListener('click', function () {
      monto.value = b.getAttribute('data-cr-monto');
      document.querySelectorAll('[data-cr-monto]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      pinta();
      monto.focus();
    });
  });
  $('crCero') && $('crCero').addEventListener('click', function () {
    monto.value = '';
    document.querySelectorAll('[data-cr-monto]').forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
    pinta();
  });
  monto.addEventListener('input', function () {
    document.querySelectorAll('[data-cr-monto]').forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
    pinta();
  });
  anios.addEventListener('input', pinta);
  document.querySelectorAll('input[name="crTasa"]').forEach(function (r) { r.addEventListener('change', pinta); });
  pinta();
})();
