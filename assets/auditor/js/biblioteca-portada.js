/* =========================================================================
   biblioteca-portada.js: Biblioteca del Erario Público (diccionario.html), Ronda 26D (26-11-2026).
   Centro de referencia editorial: el buscador del encabezado y la barra A–Z
   filtran los términos del Diccionario, que salen de window.AUDIT_DB.glosario
   (la misma base de glosario.html y del Auditor: aquí no se escribe ningún
   término). Cada ficha lleva a su ancla en glosario.html, con la forma de
   glosario_ancla() de herramientas/apartados.py y de ancla() de glosario.js:
   si cambia una, cambian las tres. Sin emojis: solo texto e íconos de trazo.
   ========================================================================= */
(function () {
  'use strict';
  var lista = document.getElementById('bibTerminos');
  var busca = document.getElementById('bibBusca');
  var az = document.getElementById('bibAZ');
  var cuenta = document.getElementById('bibCuenta');
  var mas = document.getElementById('bibMas');
  var DB = window.AUDIT_DB;
  if (!lista || !busca || !az || !DB || !DB.glosario) return;

  var PASO = 24;
  var visibles = PASO;
  var letra = '';

  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function sinAcentos(s) { return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function norm(s) { return sinAcentos(s).toLowerCase().replace(/\s+/g, ' ').trim(); }
  function ancla(t) { return sinAcentos(String(t).split(' (')[0]).replace(/[^A-Za-z0-9]+/g, '-').replace(/^-|-$/g, ''); }
  function inicial(t) { var c = sinAcentos(t).charAt(0).toUpperCase(); return /[A-Z]/.test(c) ? c : '#'; }

  var terminos = DB.glosario.slice().sort(function (a, b) { return a.termino.localeCompare(b.termino, 'es'); }).map(function (g) {
    return { g: g, l: inicial(g.termino), q: norm(g.termino + ' ' + g.categoria + ' ' + g.definicion + ' ' + (g.ley || '')) };
  });
  var hay = {};
  terminos.forEach(function (t) { hay[t.l] = (hay[t.l] || 0) + 1; });

  // La barra A–Z: las letras sin términos quedan quietas (no se inventa nada para llenarlas).
  Array.prototype.forEach.call(az.querySelectorAll('[data-letra]'), function (b) {
    var l = b.getAttribute('data-letra');
    if (l && !hay[l]) { b.disabled = true; b.setAttribute('aria-disabled', 'true'); b.title = 'Sin términos con ' + l; }
    else if (l) b.title = hay[l] + (hay[l] === 1 ? ' término' : ' términos') + ' con ' + l;
  });

  function ficha(t) {
    var g = t.g;
    return '<article class="bib-ficha">' +
      '<span class="bib-ficha-cat">' + esc(g.categoria) + '</span>' +
      '<h3 class="bib-ficha-tit"><a href="glosario.html#' + ancla(g.termino) + '">' + esc(g.termino) + '</a></h3>' +
      '<p class="bib-ficha-def">' + esc(g.definicion) + '</p>' +
      (g.ley ? '<p class="bib-ficha-ley"><span class="bib-sello-of">Fundamento</span> ' + esc(g.ley) + '</p>' : '') +
    '</article>';
  }

  function pintar() {
    var q = norm(busca.value);
    var ok = terminos.filter(function (t) { return (!letra || t.l === letra) && (!q || t.q.indexOf(q) !== -1); });
    lista.innerHTML = ok.length
      ? ok.slice(0, visibles).map(ficha).join('')
      : '<p class="bib-vacio">Ningún término coincide. Prueba con otra palabra o <a href="glosario.html">abre el Diccionario completo</a>; '
        + 'si no está, pregúntale al Auditor.</p>';
    cuenta.textContent = (ok.length === terminos.length && !q && !letra)
      ? 'Los ' + terminos.length + ' términos del Diccionario, de la A a la Z.'
      : ok.length + (ok.length === 1 ? ' término' : ' términos') + (letra ? ' con la ' + letra : '') + (q ? ' para «' + busca.value.trim() + '»' : '') + '.';
    mas.hidden = ok.length <= visibles;
    mas.textContent = 'Ver ' + Math.min(PASO, ok.length - visibles) + ' términos más';
  }

  busca.addEventListener('input', function () { visibles = PASO; pintar(); });
  busca.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); lista.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  });
  az.addEventListener('click', function (e) {
    var b = e.target.closest('[data-letra]');
    if (!b || b.disabled) return;
    letra = b.getAttribute('data-letra');
    Array.prototype.forEach.call(az.querySelectorAll('[data-letra]'), function (x) { x.setAttribute('aria-pressed', String(x === b)); });
    visibles = PASO;
    pintar();
    lista.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  mas.addEventListener('click', function () { visibles += PASO; pintar(); });

  var q0 = new URLSearchParams(location.search).get('q');
  if (q0) busca.value = q0;
  pintar();
})();
