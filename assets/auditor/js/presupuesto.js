/* Auditavisión · Números › Presupuesto, páginas de sus cuatro módulos.
   Las páginas llegan ya escritas por herramientas/presupuesto_modulos.py:
   cifras, barras y tablas no necesitan este archivo. Aquí solo vive el
   simulador de sensibilidades del Paquete Económico 2027, que aplica los
   seis coeficientes oficiales de los Criterios (efecto aislado de cada
   variable, sin interacciones: así los publica la fuente). */
(function () {
  'use strict';

  var nodo = document.getElementById('peDatos');
  var res = document.getElementById('peSimResultado');
  if (!nodo || !res) return;
  var D;
  try { D = JSON.parse(nodo.textContent); } catch (e) { return; }
  var S = D.s, B = D.b, E = D.e;
  var val = {};
  S.forEach(function (s) { val[s.id] = s.base; });

  function fmtMdp(n) {
    n = Math.round(n);
    return (n < 0 ? '-$' : '$') + Math.abs(n).toLocaleString('es-MX') + ' mdp';
  }
  function mmp(v) {
    return '$' + (v / 1000).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mmp';
  }
  function signo(v) {
    return (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(1);
  }
  function efecto(s, v) {
    var pasos = (v - s.base) / s.tramo;
    if (s.destino === 'costofin') return { ing: 0, fin: pasos * s.coef };
    if (s.destino === 'ambos') return { ing: pasos * s.coef, fin: pasos * s.coef2 };
    return { ing: pasos * s.coef, fin: 0 };
  }

  function cuenta() {
    var dIng = 0, dFin = 0;
    var det = S.map(function (s) {
      var e = efecto(s, val[s.id]);
      dIng += e.ing; dFin += e.fin;
      return { s: s, v: val[s.id], ing: e.ing, fin: e.fin, neto: e.ing - e.fin };
    });
    var bal = B.balance + dIng - dFin;
    var rfsp = bal + B.extrapres;
    return { det: det, dIng: dIng, dFin: dFin, desvio: dIng - dFin,
      ingresos: B.ingresos + dIng, costofin: B.costofin + dFin, balance: bal, rfsp: rfsp };
  }

  function panel(nombre, v, base, saldo, malSiSube) {
    var dif = v - base, quieto = Math.abs(dif) < 1;
    var bien = saldo ? dif > 0 : (malSiSube ? dif < 0 : dif > 0);
    return '<div class="pm-res-p' + (quieto ? '' : (bien ? ' mejora' : ' empeora')) + '">' +
      '<h4>' + nombre + '</h4><p class="pm-res-v num-tabular">' + fmtMdp(v) + '</p>' +
      '<p class="pm-res-pib">' + (v / B.pib * 100).toFixed(1) + '% del PIB</p>' +
      '<p class="pm-res-dif">' + (quieto ? 'sin cambio respecto de los Criterios' : signo(dif / 1000) + ' mmp respecto de los Criterios') + '</p></div>';
  }

  function celda(v, malSiPositivo) {
    if (!v) return '<td>—</td>';
    var c = (v > 0) !== !!malSiPositivo ? 'pos' : 'neg';
    return '<td class="' + c + '">' + signo(v / 1000) + ' mmp</td>';
  }

  function pinta() {
    var r = cuenta();
    var dentro = Math.abs(r.desvio) <= B.tolerancia;
    var mejor = r.desvio > 0;
    var quieto = Math.abs(r.desvio) < 1;
    var veredicto = quieto
      ? 'Sin movimiento: las seis variables están donde los Criterios las suponen.'
      : (dentro
        ? 'La desviación es de ' + mmp(Math.abs(r.desvio)) + '. Cabe dentro del 2% del gasto neto total —' + mmp(B.tolerancia) +
          '— que el artículo 17 de la Ley Federal de Presupuesto tolera <b>sin obligar siquiera a una explicación</b> en el informe trimestral.'
        : 'La desviación es de ' + mmp(Math.abs(r.desvio)) + ' y <b>rebasa</b> el 2% del gasto neto total —' + mmp(B.tolerancia) +
          '—. A partir de aquí, el artículo 17 de la Ley Federal de Presupuesto obliga a la Secretaría a justificarla en el último informe trimestral del ejercicio. La ley habla de «desviación» sin distinguir el signo: recaudar de más también obliga a explicarse.');
    var rfspPib = r.rfsp / B.pib * 100, balPib = r.balance / B.pib * 100;
    res.innerHTML =
      '<div class="pm-res-rej">' +
        panel('Ingresos presupuestarios', r.ingresos, B.ingresos, false, false) +
        panel('Costo financiero', r.costofin, B.costofin, false, true) +
        panel('Balance presupuestario', r.balance, B.balance, true) +
        panel('RFSP · balance público amplio', r.rfsp, B.rfsp, true) +
      '</div>' +
      '<div class="pm-res-meta ' + (quieto ? 'base' : dentro ? 'ok' : (mejor ? 'fuera' : 'alerta')) + '">' +
        '<b>' + (quieto ? '● Escenario base' : mejor ? '▲ Mejora sobre lo proyectado' : '▼ Deterioro sobre lo proyectado') + '</b>' +
        '<p>' + veredicto + '</p>' +
        '<p>La meta publicada para 2027 es un RFSP de ' + B.meta.toFixed(1) + '% del PIB y un balance presupuestario de ' +
          B.metaBalance.toFixed(1) + '%. Este escenario da <b>' + rfspPib.toFixed(2) + '%</b> y <b>' + balPib.toFixed(2) +
          '%</b>. Van con dos decimales para que un movimiento pequeño no se pierda en el redondeo; el documento publica una sola.</p>' +
      '</div>' +
      '<div class="gp-tabla-caja"><table class="gp-tabla pm-tabla pm-res-t"><caption class="sr-only">Aporte de cada variable al resultado</caption>' +
        '<thead><tr><th scope="col">Variable</th><th scope="col">Valor</th><th scope="col">Ingresos</th><th scope="col">Costo financiero</th><th scope="col">Efecto neto</th></tr></thead><tbody>' +
        r.det.map(function (d) {
          return '<tr' + (Math.abs(d.neto) < 1 ? ' class="pm-quieta"' : '') + '><th scope="row">' + d.s.icono + ' ' + d.s.n + '</th>' +
            '<td>' + d.v.toFixed(d.s.dec) + '</td>' + celda(d.ing) + celda(d.fin, true) + celda(d.neto) + '</tr>';
        }).join('') +
        '<tr class="pm-res-total"><th scope="row">Total</th><td></td>' + celda(r.dIng) + celda(r.dFin, true) + celda(r.desvio) + '</tr>' +
      '</tbody></table></div>';
  }

  var desc = document.getElementById('peEscDesc');
  var botones = document.querySelectorAll('.pm-esc');

  function marcaPalanca(s) {
    var out = document.getElementById('peval-' + s.id);
    if (out) out.textContent = val[s.id].toFixed(s.dec);
    var caja = document.getElementById('pepal-' + s.id);
    if (caja) caja.classList.toggle('movida', Math.abs(val[s.id] - s.base) > 1e-9);
  }

  S.forEach(function (s) {
    var rng = document.getElementById('perng-' + s.id);
    if (!rng) return;
    rng.addEventListener('input', function () {
      val[s.id] = parseFloat(rng.value);
      marcaPalanca(s);
      Array.prototype.forEach.call(botones, function (b) { b.classList.remove('activo'); b.setAttribute('aria-pressed', 'false'); });
      if (desc) desc.textContent = 'Escenario propio: las palancas ya no están donde las dejaron los Criterios.';
      pinta();
    });
  });

  Array.prototype.forEach.call(botones, function (b) {
    b.setAttribute('aria-pressed', b.classList.contains('activo') ? 'true' : 'false');
    b.addEventListener('click', function () {
      var e = E.filter(function (x) { return x.id === b.getAttribute('data-esc'); })[0];
      if (!e) return;
      S.forEach(function (s) {
        val[s.id] = e.v[s.id] !== undefined ? e.v[s.id] : s.base;
        var rng = document.getElementById('perng-' + s.id);
        if (rng) rng.value = val[s.id];
        marcaPalanca(s);
      });
      Array.prototype.forEach.call(botones, function (x) {
        x.classList.toggle('activo', x === b);
        x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
      });
      if (desc) desc.textContent = e.d;
      pinta();
    });
  });

  pinta();
})();
