/* Números › Gasto público (numeros-gasto-publico.html, 11-10-2026).
   1. «¿Quién lo aprueba?»: las seis paradas del ciclo del presupuesto, como
      pestañas (clic, flechas del teclado y botones ← →).
   2. «¿Cómo se reparte?»: el simulador contable. «Contabilizar» lleva de
      cero a su cifra el total, los dos tipos de gasto y los ocho renglones;
      cada tramo abre su ficha. Y «Si el presupuesto fuera de…» reparte una
      cantidad en la misma proporción.
   Las cifras vienen en #gpDatos, escritas por herramientas/apartados.py
   (gasto_ciclo() y gasto_reparte()). */
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function num(v, d) { return v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* 1. El ciclo. */
  var ciclo = document.querySelector('.gp-ciclo');
  if (ciclo) {
    ciclo.classList.add('gp-js');
    var pasos = Array.prototype.slice.call(ciclo.querySelectorAll('.gp-paso'));
    var prog = ciclo.querySelector('.gp-prog span');
    var actual = 0;
    var ir = function (i, foco) {
      actual = (i + pasos.length) % pasos.length;
      pasos.forEach(function (b, k) {
        var sel = k === actual;
        b.setAttribute('aria-selected', sel ? 'true' : 'false');
        b.tabIndex = sel ? 0 : -1;
        b.classList.toggle('gp-hecho-paso', k < actual);
        var panel = document.getElementById(b.getAttribute('aria-controls'));
        if (panel) { if (sel) panel.removeAttribute('data-oculto'); else panel.setAttribute('data-oculto', '1'); }
      });
      if (prog) prog.style.width = ((actual + 1) / pasos.length * 100).toFixed(1) + '%';
      if (foco) pasos[actual].focus();
    };
    pasos.forEach(function (b, k) {
      b.addEventListener('click', function () { ir(k, false); });
      b.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); ir(actual + 1, true); }
        else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); ir(actual - 1, true); }
        else if (e.key === 'Home') { e.preventDefault(); ir(0, true); }
        else if (e.key === 'End') { e.preventDefault(); ir(pasos.length - 1, true); }
      });
    });
    Array.prototype.forEach.call(ciclo.querySelectorAll('.gp-flecha'), function (b) {
      b.addEventListener('click', function () { ir(actual + parseInt(b.getAttribute('data-dir'), 10), false); });
    });
    ir(0, false);
  }

  /* 2. El simulador contable. */
  var nodo = document.getElementById('gpDatos');
  if (!nodo) return;
  var D;
  try { D = JSON.parse(nodo.textContent); } catch (e) { return; }
  var total = D.total;
  var porId = { total: { id: 'total', nom: 'Gasto neto total', v: total, est: 'oficial', color: '#33415c',
    que: 'Todo lo que la Federación puede gastar en 2026, tal como lo aprobó la Cámara de Diputados.', op: '' } };
  D.grupos.forEach(function (g) { porId[g.id] = g; });
  D.renglones.forEach(function (r) { porId[r.id] = r; });

  var ici = document.getElementById('gpIci'), det = document.getElementById('gpDet');
  var btn = document.getElementById('gpContar'), tot = document.getElementById('gpTotal'), est = document.getElementById('gpEstado');
  var niveles = Array.prototype.slice.call(ici.querySelectorAll('.gp-nivel'));
  var segs = Array.prototype.slice.call(ici.querySelectorAll('.gp-seg'));
  var lleno = false, anim = null;

  function pinta(t) {
    // Cada nivel arranca un poco después del anterior: el total se parte.
    niveles.forEach(function (n, k) {
      var a = Math.max(0, Math.min(1, (t - k * 0.25) / 0.5));
      n.style.setProperty('--t', (1 - Math.pow(1 - a, 3)).toFixed(4));
    });
    tot.textContent = '$' + num(total * Math.min(1, t / 0.5), 1) + ' mdp';
  }
  function ceros() {
    if (anim) cancelAnimationFrame(anim);
    lleno = false; pinta(0); ici.classList.add('gp-ceros');
    btn.textContent = '▶ Contabilizar'; btn.setAttribute('aria-pressed', 'false');
    est.textContent = 'El presupuesto está en ceros.';
  }
  function contar() {
    lleno = true; ici.classList.remove('gp-ceros');
    btn.textContent = '↺ Reiniciar en ceros'; btn.setAttribute('aria-pressed', 'true');
    est.textContent = 'Contabilizado: el Presupuesto de Egresos 2026, del total a sus ocho renglones.';
    if (reduce) { pinta(1); return; }
    var t0 = null, dur = 2600;
    function paso(ts) {
      if (t0 === null) t0 = ts;
      var t = Math.min(1, (ts - t0) / dur);
      pinta(t);
      if (t < 1) anim = requestAnimationFrame(paso);
    }
    anim = requestAnimationFrame(paso);
  }
  btn.addEventListener('click', function () { if (lleno) ceros(); else contar(); });

  function ficha(id) {
    var x = porId[id];
    if (!x) return;
    if (!lleno) { pinta(1); lleno = true; ici.classList.remove('gp-ceros'); btn.textContent = '↺ Reiniciar en ceros'; btn.setAttribute('aria-pressed', 'true');
      est.textContent = 'Contabilizado: el Presupuesto de Egresos 2026, del total a sus ocho renglones.'; }
    segs.forEach(function (s) {
      var sid = s.getAttribute('data-id'), y = porId[sid];
      var rel = sid === id || id === 'total' || (y && y.g === id) || (x.g && x.g === sid) || sid === 'total';
      s.setAttribute('aria-pressed', sid === id ? 'true' : 'false');
      s.classList.toggle('gp-apagado', !rel);
    });
    var hijos = id === 'total' ? D.grupos : D.renglones.filter(function (r) { return r.g === id; });
    var lista = hijos.length ? '<ul class="gp-det-hijos">' + hijos.map(function (h) {
      return '<li><span class="gp-det-p" style="background:' + h.color + '"></span>' +
        (h.p ? '<a href="' + h.p + '">' + esc(h.nom) + '</a>' : '<button type="button" class="gp-det-ir" data-id="' + h.id + '">' + esc(h.nom) + '</button>') +
        '<b>$' + num(h.v, 1) + ' mdp</b><span>' + num(h.v / x.v * 100, 1) + '%</span></li>';
    }).join('') + '</ul>' : '';
    det.innerHTML = '<div class="gp-det-cab" style="--c:' + x.color + '">' + (x.ico ? '<span class="gp-det-ico" aria-hidden="true">' + x.ico + '</span>' : '') +
      '<h3>' + esc(x.nom) + '</h3></div>' +
      '<div class="gp-det-cifras"><p><b>$' + num(x.v, 1) + ' mdp</b> <span class="est-chip est-' + x.est + '">' + x.est + '</span></p>' +
      (id === 'total' ? '' : '<p class="gp-det-cien">De cada $100 que se gastan<b>$' + num(x.v / total * 100, 2) + '</b> <span class="est-chip est-derivado">derivado</span></p>') + '</div>' +
      '<p class="gp-det-que">' + esc(x.que) + '</p>' +
      (x.op ? '<p class="gp-det-op">Operación: ' + esc(x.op) + '</p>' : '') + lista +
      (x.p ? '<p class="gp-det-irp"><a href="' + x.p + '">Abrir la página de «' + esc(x.nom) + '» ➔</a></p>' : '');
    Array.prototype.forEach.call(det.querySelectorAll('.gp-det-ir'), function (b) {
      b.addEventListener('click', function () { ficha(b.getAttribute('data-id')); });
    });
  }
  segs.forEach(function (s) { s.addEventListener('click', function () { ficha(s.getAttribute('data-id')); }); });
  ceros();

  /* «Si el presupuesto fuera de…». */
  var monto = document.getElementById('gpMonto'), rep = document.getElementById('gpRep');
  if (!monto || !rep) return;
  var filas = Array.prototype.slice.call(rep.querySelectorAll('.gp-rep-f'));
  var mayor = Math.max.apply(null, D.renglones.map(function (r) { return r.v; }));
  function reparte() {
    var m = parseFloat(monto.value);
    if (!(m >= 0)) m = 0;
    filas.forEach(function (f) {
      var v = parseFloat(f.getAttribute('data-v'));
      f.querySelector('.gp-rep-m').textContent = '$' + num(m * v / total, 2);
      f.querySelector('.gp-rep-barra span').style.width = (v / mayor * 100).toFixed(2) + '%';
    });
  }
  monto.addEventListener('input', reparte);
  Array.prototype.forEach.call(document.querySelectorAll('.gp-rep-atajos button'), function (b) {
    b.addEventListener('click', function () { monto.value = b.getAttribute('data-monto'); reparte(); });
  });
  reparte();
})();
