/* Donaciones (donaciones.html, 11-10-2026): llena la alcancía con lo
   recaudado y anima la moneda de prueba. Las cifras vienen de
   herramientas/apartados.py en el JSON #dnDatos; aquí no se escribe ninguna. */
(function () {
  'use strict';
  var nodo = document.getElementById('dnDatos');
  var nivel = document.getElementById('dnNivel');
  if (!nodo || !nivel) return;
  var D;
  try { D = JSON.parse(nodo.textContent); } catch (e) { return; }
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* El nivel va de 160 (vacía) a 0 (llena). Sin meta o sin dinero, vacía. */
  var pct = (D.meta && D.recaudado > 0) ? Math.min(1, D.recaudado / D.meta) : 0;
  function llena() { nivel.style.transform = 'translateY(' + (160 - 160 * pct).toFixed(1) + 'px)'; }
  if (reduce) llena(); else setTimeout(llena, 300);

  /* La moneda de prueba: cae, la alcancía brinca y no suma nada. */
  var svg = document.querySelector('.dn-svg');
  var boton = document.getElementById('dnPrueba');
  var nota = document.getElementById('dnPruebaNota');
  var veces = 0;
  if (svg && boton) {
    boton.addEventListener('click', function () {
      veces++;
      var m = svg.querySelector('.dn-m1').cloneNode(true);
      m.setAttribute('class', 'dn-moneda dn-cae');
      svg.querySelector('.dn-monedas').appendChild(m);
      setTimeout(function () {
        if (m.parentNode) m.parentNode.removeChild(m);
        svg.classList.remove('dn-salta'); void svg.getBoundingClientRect(); svg.classList.add('dn-salta');
      }, reduce ? 0 : 800);
      if (nota) nota.textContent = veces === 1
        ? '¡Clinc! Así caerá cada donativo cuando se abra el canal. Esta fue de prueba: no suma a la cuenta.'
        : 'Llevas ' + veces + ' monedas de prueba. Ninguna suma: la alcancía solo cuenta dinero que de verdad entra.';
    });
  }
})();
