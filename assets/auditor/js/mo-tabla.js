/* Auditavisión · Inversión y Megaobras › La tabla general en vivo y la
   portada de la herramienta (21-10-2026). La página la escribe
   herramientas/mo_tabla.py con las cifras ya puestas; cada contador trae
   en data-mt-tasa los pesos por segundo de su resultado anual publicado
   (resultado × 1,000,000 ÷ 31,536,000). Aquí no se calcula ninguna cifra
   nueva: solo se multiplica esa tasa por el tiempo que llevas mirando.
   Prefijo: mt-. */
(function () {
  'use strict';

  /* La aplicación «El pulso del gasto» se repartió en capítulos el
     21-10-2026: sus anclas viejas llevan al capítulo que les toca. */
  var PULSO = { mpCifras: 'herramienta-megaobras-cero.html#mpCifras', mpRitmo: 'herramienta-megaobras-pulso-cuenta.html#mpRitmo', mpCompo: 'herramienta-megaobras-sector.html#mpCompo', mpComo: 'herramienta-megaobras-cero.html#como-se-calcula', mpCuenta: 'herramienta-megaobras-pulso-cuenta.html#mpCuenta' };
  var vieja = PULSO[location.hash.slice(1)];
  if (vieja && !document.getElementById(location.hash.slice(1))) {
    location.replace(vieja);
    return;
  }

  var raiz = document.getElementById('mtRaiz');
  if (!raiz) return;
  var vivos = Array.prototype.slice.call(raiz.querySelectorAll('[data-mt-tasa]'));
  if (!vivos.length) return;
  vivos.forEach(function (el) { el._tasa = parseFloat(el.getAttribute('data-mt-tasa')) || 0; });

  function pesos(v) {
    return (v < 0 ? '−' : '+') + '$' + Math.abs(v).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  var acumulado = 0;
  var desde = Date.now();
  var pausado = false;
  function segundos() { return acumulado + (pausado ? 0 : (Date.now() - desde) / 1000); }
  function pinta() {
    var s = segundos();
    vivos.forEach(function (el) { el.textContent = pesos(el._tasa * s); });
  }

  var bPausa = raiz.querySelector('[data-mt-pausa]');
  var bCero = raiz.querySelector('[data-mt-cero]');
  if (bPausa) {
    bPausa.addEventListener('click', function () {
      if (pausado) { desde = Date.now(); pausado = false; } else { acumulado = segundos(); pausado = true; }
      bPausa.setAttribute('aria-pressed', pausado ? 'true' : 'false');
      bPausa.querySelector('span:last-child').textContent = pausado ? 'Seguir' : 'Pausar';
      pinta();
    });
  }
  if (bCero) {
    bCero.addEventListener('click', function () {
      acumulado = 0;
      desde = Date.now();
      pinta();
    });
  }

  pinta();
  setInterval(function () { if (!pausado && !document.hidden) pinta(); }, 100);
})();
