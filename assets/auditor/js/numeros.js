/* Números › Presupuesto (numeros-presupuesto.html; 10-10-2026, en su página desde el 11-10-2026): «El peso de 2026».
   Dos barras con todo el dinero federal del año: arriba lo que entra
   (Ley de Ingresos) y abajo lo que sale (Presupuesto de Egresos, en los
   tres presupuestos más lo ya comprometido). Al tocar un tramo se abre su
   detalle: cifra, cuánto es de cada $100, su estado, de qué está hecho, su
   fuente y el paso del recorrido donde se explica.
   Las cifras llegan en el JSON #npDatos, que arma herramientas/apartados.py
   (numeros_datos()) con window.AUDIT_DB: aquí no se escribe ninguna cifra. */
(function () {
  'use strict';
  var nodo = document.getElementById('npDatos'), raiz = document.getElementById('numPeso');
  if (!nodo || !raiz) return;
  var D;
  try { D = JSON.parse(nodo.textContent); } catch (e) { return; }
  var modo = 'pesos', sel = { lado: 'sale', id: 'social' };

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function num(v, d) { return v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function mdp(v) { return '$' + num(v, 1) + ' mdp'; }
  function bill(v) { return '$' + num(v / 1e6, 2) + ' billones'; }
  function cien(v) { var x = v / D.total * 100; return x > 0 && x < 0.005 ? 'menos de $0.01' : '$' + num(x, 2); }
  function chip(e) { return '<span class="est-chip est-' + e + '">' + e + '</span>'; }
  function busca(lado, id) {
    var l = D[lado];
    for (var i = 0; i < l.length; i++) if (l[i].id === id) return l[i];
    return null;
  }
  function refs(f) {
    return f.map(function (r) {
      return '<a class="np-ref" href="' + esc(r.url) + '" title="' + esc(r.t) + '">[' + (r.n < 10 ? '0' : '') + r.n + ']</a>';
    }).join(' ');
  }

  function pintaBarras() {
    Array.prototype.forEach.call(raiz.querySelectorAll('.np-seg'), function (b) {
      var x = busca(b.getAttribute('data-lado'), b.getAttribute('data-id'));
      if (!x) return;
      b.querySelector('.np-seg-v').textContent = modo === 'cien' ? cien(x.v) : bill(x.v);
      var on = b.getAttribute('data-lado') === sel.lado && b.getAttribute('data-id') === sel.id;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.setAttribute('aria-label', x.nom + ': ' + mdp(x.v) + ', ' + cien(x.v) + ' de cada $100');
      b.classList.toggle('np-chico', b.offsetWidth < 96);
    });
    Array.prototype.forEach.call(raiz.querySelectorAll('.np-ley-b'), function (b) {
      var on = b.getAttribute('data-lado') === sel.lado && b.getAttribute('data-id') === sel.id;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  function pintaDetalle() {
    var x = busca(sel.lado, sel.id), det = document.getElementById('npDet');
    if (!x || !det) return;
    var filas = (x.filas || []).map(function (f) {
      var n = f.g ? '<a href="glosario.html#' + esc(f.g) + '">' + esc(f.n) + '</a>' : esc(f.n);
      var v = f.pib != null ? num(f.pib, 1) + ' pts. del PIB' : (modo === 'cien' ? cien(f.v) : mdp(f.v));
      var w = f.pib != null ? null : Math.max(0.8, f.v / x.v * 100);
      return '<li><span class="np-det-n">' + n + '</span><b>' + v + '</b>' +
        (w != null ? '<span class="np-det-pista"><span style="width:' + w.toFixed(1) + '%"></span></span>' : '') + '</li>';
    }).join('');
    det.innerHTML =
      '<div class="np-det-cab np-' + esc(x.id) + '"><span class="np-det-ico" aria-hidden="true">' + x.ico + '</span>' +
      '<div><span class="np-det-lado">' + (sel.lado === 'entra' ? '⬇️ Lo que entra' : '⬆️ Lo que sale') + '</span>' +
      '<h3>' + esc(x.nom) + '</h3></div></div>' +
      '<div class="np-det-cifras"><p><b>' + mdp(x.v) + '</b> ' + chip(x.est) + '<small>' + bill(x.v) + '</small></p>' +
      '<p class="np-det-cien">De cada $100<b>' + cien(x.v) + '</b></p></div>' +
      '<p class="np-det-que">' + esc(x.que) + '</p>' +
      (filas ? '<ul class="np-det-filas">' + filas + '</ul>' : '') +
      '<p class="np-det-op">' + (x.op ? esc(x.op) + ' ' : '') + 'Fuente: ' + refs(x.f) + '</p>' +
      '<p class="np-det-ir">' + (x.g ? '<a href="glosario.html#' + esc(x.g) + '">📖 El concepto, en el glosario</a>' : '') +
      '<a class="np-det-paso" href="' + esc(x.paso) + '">Ver «' + esc(x.ptit) + '» ➔</a></p>';
  }

  function pinta() { pintaBarras(); pintaDetalle(); }

  raiz.addEventListener('click', function (ev) {
    var b = ev.target.closest('.np-seg, .np-ley-b');
    if (b) { sel = { lado: b.getAttribute('data-lado'), id: b.getAttribute('data-id') }; pinta(); return; }
    var m = ev.target.closest('[data-modo]');
    if (m) {
      modo = m.getAttribute('data-modo');
      Array.prototype.forEach.call(raiz.querySelectorAll('[data-modo]'), function (r) {
        r.setAttribute('aria-checked', r === m ? 'true' : 'false');
      });
      pinta();
    }
  });
  pinta();
  window.addEventListener('resize', pintaBarras);
})();
