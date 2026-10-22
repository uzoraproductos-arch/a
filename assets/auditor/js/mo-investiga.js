/* Auditavisión · Inversión y Megaobras › Haz tu propia investigación
   (aplicación 1, 21-10-2026). La página la escribe herramientas/mo_investiga.py
   con las 42 respuestas ya puestas (7 opciones × 6 preguntas): aquí no se
   calcula ninguna cifra, solo se muestra la que eliges. El ancla
   #inv-<presidente>-<pregunta> abre una respuesta y se puede compartir.
   Prefijo: mi-. */
(function () {
  'use strict';

  var raiz = document.getElementById('mtRaiz');
  if (!raiz || !raiz.classList.contains('mi')) return;
  var paneles = [].slice.call(raiz.querySelectorAll('.mi-panel'));
  var bSx = [].slice.call(raiz.querySelectorAll('.mi-b[data-sx]'));
  var bQ = [].slice.call(raiz.querySelectorAll('.mi-b[data-q]'));
  var est = { sx: 'todos', q: 'invirtio' };

  function existe(sx, q) { return !!document.getElementById('inv-' + sx + '-' + q); }
  function pinta(mover) {
    paneles.forEach(function (p) { p.hidden = !(p.getAttribute('data-sx') === est.sx && p.getAttribute('data-q') === est.q); });
    bSx.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-sx') === est.sx ? 'true' : 'false'); });
    bQ.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-q') === est.q ? 'true' : 'false'); });
    try { history.replaceState(null, '', '#inv-' + est.sx + '-' + est.q); } catch (e) { /* nada */ }
    var c = document.getElementById('miCopiado');
    if (c) c.textContent = '';
    if (mover) {
      var p = document.getElementById('inv-' + est.sx + '-' + est.q);
      if (p) {
        p.scrollIntoView({ behavior: 'smooth', block: 'start' });
        try { p.focus({ preventScroll: true }); } catch (e) { /* nada */ }
      }
    }
  }
  bSx.forEach(function (b) { b.addEventListener('click', function () { est.sx = b.getAttribute('data-sx'); pinta(false); }); });
  bQ.forEach(function (b) { b.addEventListener('click', function () { est.q = b.getAttribute('data-q'); pinta(false); }); });
  raiz.querySelectorAll('[data-ir-q]').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      ev.preventDefault();
      est.q = a.getAttribute('data-ir-q');
      pinta(true);
    });
  });

  var copiar = document.getElementById('miCopiar');
  if (copiar) copiar.addEventListener('click', function () {
    var url = location.href.split('#')[0] + '#inv-' + est.sx + '-' + est.q;
    var c = document.getElementById('miCopiado');
    function listo() { if (c) c.textContent = 'Enlace copiado.'; }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(listo, function () { if (c) c.textContent = url; });
    } else if (c) { c.textContent = url; }
  });

  function leer() {
    var m = /^#inv-(.+)-([a-z]+)$/.exec(location.hash);
    if (m && existe(m[1], m[2])) { est.sx = m[1]; est.q = m[2]; pinta(true); }
  }
  window.addEventListener('hashchange', leer);
  leer();
})();
