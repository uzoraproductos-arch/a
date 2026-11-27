/* El mostrador de servicios.html (Ronda 30, 27-11-2026; herramientas/servicios_planes.catalogo()).
   Dos filtros que se combinan: «Soy» (data-g de cada tarjeta) y «Busco» (data-l). Sin este archivo se ven todos.
   No guarda nada: la dirección recuerda la vista (?soy=&busco=) con replaceState. */
(function () {
  'use strict';
  var caja = document.getElementById('svpFiltros'), lista = document.getElementById('svpMostrador');
  if (!caja || !lista) return;
  var cuenta = document.getElementById('svpCuenta'), vacio = document.getElementById('svpVacio');
  var f = { g: '', l: '' }, CLAVE = { g: 'soy', l: 'busco' };
  function pinta() {
    var n = 0;
    Array.prototype.forEach.call(lista.children, function (li) {
      var si = (!f.g || (' ' + li.getAttribute('data-g') + ' ').indexOf(' ' + f.g + ' ') >= 0) && (!f.l || li.getAttribute('data-l') === f.l);
      li.hidden = !si; if (si) n++;
    });
    Array.prototype.forEach.call(caja.querySelectorAll('[data-svp-f]'), function (b) {
      b.setAttribute('aria-pressed', String(f[b.getAttribute('data-svp-f')] === b.getAttribute('data-v')));
    });
    if (cuenta) cuenta.textContent = n + (n === 1 ? ' servicio' : ' servicios');
    if (vacio) vacio.hidden = n > 0;
  }
  function anota() {
    try {
      var p = new URLSearchParams(location.search);
      ['g', 'l'].forEach(function (k) { if (f[k]) p.set(CLAVE[k], f[k]); else p.delete(CLAVE[k]); });
      var q = p.toString();
      history.replaceState(null, '', location.pathname + (q ? '?' + q : '') + location.hash);
    } catch (e) { /* sin historial */ }
  }
  caja.addEventListener('click', function (ev) {
    var b = ev.target.closest ? ev.target.closest('[data-svp-f]') : null;
    if (!b) return;
    f[b.getAttribute('data-svp-f')] = b.getAttribute('data-v');
    pinta(); anota();
  });
  var todos = document.getElementById('svpTodos');
  if (todos) todos.addEventListener('click', function () { f.g = ''; f.l = ''; pinta(); anota(); });
  try {
    var p0 = new URLSearchParams(location.search);
    ['g', 'l'].forEach(function (k) {
      var v = p0.get(CLAVE[k]) || '';
      if (v && caja.querySelector('[data-svp-f="' + k + '"][data-v="' + v.replace(/[^a-z0-9]/g, '') + '"]')) f[k] = v;
    });
  } catch (e) { /* sin URLSearchParams */ }
  pinta();
})();
