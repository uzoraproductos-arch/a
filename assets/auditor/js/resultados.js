/* Números › Cuentas claras › El estado de resultados del Gobierno
   (numeros-estado-de-resultados.html, 12-10-2026).
   La página trae todas sus cifras en el HTML (herramientas/resultados_modulo.py);
   este archivo solo hace dos cosas:
   1. Las seis pestañas: presupuesto, actividades, flujos, situación,
      resultados sociales y conciliación (clic y flechas del teclado).
   2. «¿Cuánto crees?»: el lector mueve su respuesta y al revelar ve cuántos
      pesos de cada $100 de ingresos se fueron en intereses. */
(function () {
  'use strict';
  var raiz = document.getElementById('erRaiz');
  if (!raiz) return;
  raiz.classList.add('er-js');

  /* 1. Las pestañas. Sin JavaScript se ven los seis paneles seguidos. */
  var pests = Array.prototype.slice.call(raiz.querySelectorAll('.er-pest'));
  var actual = 0;
  function ir(i, foco) {
    actual = (i + pests.length) % pests.length;
    pests.forEach(function (b, k) {
      var sel = k === actual;
      b.setAttribute('aria-selected', sel ? 'true' : 'false');
      b.tabIndex = sel ? 0 : -1;
      var panel = document.getElementById(b.getAttribute('aria-controls'));
      if (panel) panel.hidden = !sel;
    });
    if (foco) pests[actual].focus();
    try { history.replaceState(null, '', '#' + pests[actual].id.replace('erPest-', '')); } catch (e) { /* sin historial */ }
  }
  pests.forEach(function (b, k) {
    b.addEventListener('click', function () { ir(k, false); });
    b.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); ir(actual + 1, true); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); ir(actual - 1, true); }
      else if (e.key === 'Home') { e.preventDefault(); ir(0, true); }
      else if (e.key === 'End') { e.preventDefault(); ir(pests.length - 1, true); }
    });
  });
  var h = (location.hash || '').slice(1);
  var inicio = 0;
  pests.forEach(function (b, k) { if (b.id === 'erPest-' + h) inicio = k; });
  ir(inicio, false);

  /* 2. ¿Cuánto crees? */
  var caja = document.getElementById('erAdivina');
  if (caja) {
    var real = parseFloat(caja.getAttribute('data-real'));
    var r = document.getElementById('erAdivinaR');
    var v = document.getElementById('erAdivinaV');
    var btn = document.getElementById('erAdivinaBtn');
    var res = document.getElementById('erAdivinaRes');
    var nota = document.createElement('p');
    nota.className = 'er-adivina-nota';
    res.insertBefore(nota, res.firstChild);
    caja.classList.add('er-oculto');
    var pinta = function () { v.textContent = '$' + r.value; };
    r.addEventListener('input', function () {
      pinta();
      if (!caja.classList.contains('er-oculto')) { caja.classList.add('er-oculto'); btn.textContent = 'Revelar'; }
    });
    btn.addEventListener('click', function () {
      if (!caja.classList.contains('er-oculto')) { caja.classList.add('er-oculto'); btn.textContent = 'Revelar'; r.focus(); return; }
      var dif = parseInt(r.value, 10) - real;
      var cerca = Math.abs(dif) <= 2;
      nota.textContent = cerca ? '¡Muy cerca! Dijiste $' + r.value + '.' :
        'Dijiste $' + r.value + ': ' + (dif > 0 ? 'te pasaste por $' : 'te faltaron $') + Math.abs(dif).toFixed(2) + '.';
      caja.classList.remove('er-oculto');
      btn.textContent = 'Intentar otra vez';
    });
    pinta();
  }
})();
