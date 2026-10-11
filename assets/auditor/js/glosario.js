/* =========================================================================
   Glosario general en su propia página (glosario.html, 09-10-2026).
   Antes vivía en la pestaña «faq» de la portada y sus enlaces sacaban al
   lector a la página principal (decisión del autor: nada redirige a la
   portada). Lee los términos de window.AUDIT_DB.glosario, la misma base
   del auditor: buscador, categorías y un ancla por término
   (glosario.html#Huachicol-Fiscal), con la forma de glosario_ancla() en
   herramientas/apartados.py: si cambia una, cambia la otra.
   ========================================================================= */
(function () {
  'use strict';
  var raiz = document.getElementById('glosarioPagina');
  var DB = window.AUDIT_DB;
  if (!raiz || !DB || !DB.glosario) return;

  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function sinAcentos(s) { return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function norm(s) { return sinAcentos(s).toLowerCase().replace(/\s+/g, ' ').trim(); }
  function ancla(t) { return sinAcentos(String(t).split(' (')[0]).replace(/[^A-Za-z0-9]+/g, '-').replace(/^-|-$/g, ''); }

  var terminos = DB.glosario.slice().sort(function (a, b) { return a.termino.localeCompare(b.termino, 'es'); });
  var cats = {};
  terminos.forEach(function (g) { cats[g.categoria] = (cats[g.categoria] || 0) + 1; });
  var catActiva = 'todas';

  raiz.innerHTML =
    '<div class="gl-barra">' +
      '<label class="gl-busca"><span class="sr-only">Buscar un término</span>' +
        '<input type="search" id="glBusca" placeholder="Busca un concepto: deuda, Ramo 28, FONE, Cuenta Pública…" autocomplete="off"></label>' +
      '<div class="gl-cats" role="group" aria-label="Categorías">' +
        '<button type="button" class="gl-cat on" data-cat="todas" aria-pressed="true">Todos (' + terminos.length + ')</button>' +
        Object.keys(cats).sort().map(function (c) {
          return '<button type="button" class="gl-cat" data-cat="' + esc(c) + '" aria-pressed="false">' + esc(c) + ' (' + cats[c] + ')</button>';
        }).join('') +
      '</div>' +
      '<p class="gl-cuenta" id="glCuenta" role="status"></p>' +
    '</div>' +
    '<div class="gl-lista" id="glLista"></div>';

  var lista = document.getElementById('glLista');
  var busca = document.getElementById('glBusca');
  var cuenta = document.getElementById('glCuenta');

  lista.innerHTML = terminos.map(function (g) {
    return '<article class="gl-t" id="' + ancla(g.termino) + '" data-cat="' + esc(g.categoria) + '" data-q="' + esc(norm(g.termino + ' ' + g.definicion)) + '">' +
      '<span class="gl-t-cat">' + esc(g.categoria) + '</span>' +
      '<h3 class="gl-t-tit">' + esc(g.termino) + '</h3>' +
      '<p class="gl-t-def">' + esc(g.definicion) + '</p>' +
      (g.ley ? '<p class="gl-t-ley"><b>Fundamento:</b> ' + esc(g.ley) + '</p>' : '') +
    '</article>';
  }).join('');
  var fichas = Array.prototype.slice.call(lista.children);

  function filtrar() {
    var q = norm(busca.value), n = 0;
    fichas.forEach(function (f) {
      var ok = (catActiva === 'todas' || f.getAttribute('data-cat') === catActiva) && (!q || f.getAttribute('data-q').indexOf(q) !== -1);
      f.hidden = !ok;
      if (ok) n++;
    });
    cuenta.textContent = n === 1 ? '1 término' : n + ' términos';
  }
  busca.addEventListener('input', filtrar);
  raiz.querySelector('.gl-cats').addEventListener('click', function (e) {
    var b = e.target.closest('.gl-cat');
    if (!b) return;
    catActiva = b.getAttribute('data-cat');
    Array.prototype.forEach.call(raiz.querySelectorAll('.gl-cat'), function (x) {
      x.classList.toggle('on', x === b);
      x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
    });
    filtrar();
  });
  filtrar();

  /* La barra del buscador se queda pegada bajo la cabecera, que cambia de
     alto al bajar. */
  function altoNav() {
    var nav = document.querySelector('.site-top-nav');
    return nav ? Math.max(0, nav.getBoundingClientRect().bottom) : 0;
  }
  function pegar() { raiz.style.setProperty('--gl-tope', Math.round(altoNav()) + 'px'); }
  window.addEventListener('scroll', pegar, { passive: true });
  window.addEventListener('resize', pegar);
  pegar();

  /* glosario.html#Termino: el término queda a la vista y resaltado. */
  function irAlTermino() {
    var h = decodeURIComponent(location.hash.slice(1)).toLowerCase();
    if (!h) return;
    var f = fichas.filter(function (x) { return x.id.toLowerCase() === h; })[0];
    if (!f) return;
    busca.value = '';
    catActiva = 'todas';
    raiz.querySelector('.gl-cat[data-cat="todas"]').click();
    /* Se repite: la cabecera se encoge al bajar y las fuentes terminan de
       cargar despues del primer salto. */
    function saltar() {
      var barra = raiz.querySelector('.gl-barra');
      var tapa = altoNav() + (barra && getComputedStyle(barra).position === 'sticky' ? barra.offsetHeight : 0);
      window.scrollTo({ top: Math.max(0, f.getBoundingClientRect().top + window.pageYOffset - tapa - 16), behavior: 'instant' });
    }
    [60, 450, 900].forEach(function (ms) { setTimeout(saltar, ms); });
    f.classList.add('gl-t-destacado');
    setTimeout(function () { f.classList.remove('gl-t-destacado'); }, 2600);
  }
  window.addEventListener('hashchange', irAlTermino);
  irAlTermino();
})();
