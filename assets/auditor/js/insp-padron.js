/* «Revisa a tu contraparte» (18-11-2026): la búsqueda de la aplicación.
   Todo lo hace padron.js en el navegador; aquí solo se lee lo que el lector
   escribe (o trae en ?q=) y se pinta la ficha con Padron.html(). */
(function () {
  'use strict';
  var form = document.getElementById('pdForm'), q = document.getElementById('pdQ'), res = document.getElementById('pdRes');
  if (!form || !window.Padron) return;
  var RFC_G = /[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}/g, MAX = 100;

  function buscar(t) {
    t = String(t || '').trim();
    if (!t) return;
    var rfcs = (t.toUpperCase().match(RFC_G) || []).filter(function (x, i, l) { return l.indexOf(x) === i; });
    res.innerHTML = '<p>Buscando…</p>';
    if (!rfcs.length) {
      Padron.nombre(t).then(function (x) {
        res.innerHTML = Padron.htmlNombre(x) + '<p class="pd-chico">Para buscar a una empresa por su nombre en la lista 69-B, usa la <a href="herramienta-inspector-efos.html?q=' + encodeURIComponent(t) + '">Lista negra del SAT</a>.</p>';
      }, falla);
      return;
    }
    Promise.all(rfcs.slice(0, MAX).map(function (r) { return Padron.rfc(r); })).then(function (fs) {
      if (fs.length === 1) { res.innerHTML = Padron.html(fs[0]); return; }
      var con = fs.filter(function (f) { return f.senales && f.senales.length; });
      res.innerHTML = '<p>Revisé <b>' + fs.length + ' RFC</b>: <b>' + con.length + '</b> con alguna coincidencia y <b>' + (fs.length - con.length) + '</b> sin coincidencias.' +
        (rfcs.length > MAX ? ' Revisé solo los primeros ' + MAX + '.' : '') + '</p>' +
        fs.slice().sort(function (a, b) { return (b.nivel || 0) - (a.nivel || 0); }).map(function (f) {
          return '<details class="pd-uno"' + (f.nivel >= 2 ? ' open' : '') + '><summary><code>' + f.rfc + '</code> ' + (f.nombre ? f.nombre.replace(/</g, '&lt;') : '') + '</summary>' + Padron.html(f) + '</details>';
        }).join('');
    }, falla);
  }
  function falla() { res.innerHTML = '<p>No pude descargar las listas ahora. Revisa tu conexión y vuelve a intentarlo.</p>'; }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    buscar(q.value);
    try { history.replaceState(null, '', '?q=' + encodeURIComponent(q.value.trim())); } catch (x) { /* sin historial */ }
  });
  var p = new URLSearchParams(location.search).get('q');
  if (p) { q.value = p; buscar(p); }
})();
