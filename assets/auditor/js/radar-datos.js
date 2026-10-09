/* ===================================================================
   AUDITAVISION - Radar hacendario en la pagina de datos
   -------------------------------------------------------------------
   El radar vivia en el menu «Datos de referencia» de la portada y lo
   animaba el motor. Desde el 09-10-2026 vive en descarga-los-datos.html
   (AGENTS.md §5 bis) y este guion, sin motor, hace lo mismo que hacia
   alla: cuenta el tiempo que llevas en la pagina y lo multiplica por la
   tasa por segundo que trae cada cifra en data-tasa. Son equivalencias
   (cifra anual entre los 31,536,000 segundos del año), no pagos que
   ocurran en este instante; el texto del radar lo dice.
   =================================================================== */
(function () {
  'use strict';

  var hub = document.getElementById('radarAlertaBar');
  if (!hub) return;

  var t0 = Date.now();
  var reloj = document.getElementById('radarSessionTimer');
  var relojDesglose = document.getElementById('desgloseLiveTimer');
  var cifras = [].slice.call(hub.querySelectorAll('[data-tasa]'));

  function dosDigitos(n) { return (n < 10 ? '0' : '') + n; }
  function tiempo(s) {
    var m = Math.floor(s / 60), h = Math.floor(m / 60);
    return h > 0 ? h + ':' + dosDigitos(m % 60) + ':' + dosDigitos(s % 60) : dosDigitos(m) + ':' + dosDigitos(s % 60);
  }
  function pesos(v) {
    return '+$' + v.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function pintar() {
    var seg = (Date.now() - t0) / 1000;
    var txt = tiempo(Math.floor(seg));
    if (reloj) reloj.textContent = '⏱️ ' + txt;
    if (relojDesglose) relojDesglose.textContent = txt;
    cifras.forEach(function (el) { el.textContent = pesos(seg * parseFloat(el.dataset.tasa)); });
  }
  pintar();
  setInterval(pintar, 250);

  /* Botones del radar, como estaban en la portada: «Ocultar
     estadisticas» despeja la vista y «Desglosar cifras» abre los datos
     duros (como se calcula cada cifra y de donde sale). El desglose
     empieza cerrado. */
  var items = document.getElementById('radarLiveItems');
  var desglose = document.getElementById('radarDesgloseDrawer');
  var btnStats = document.getElementById('radarToggleStatsBtn');
  var btnDesg = document.getElementById('radarToggleDesgloseBtn');

  function mostrarCifras(si) {
    if (!items) return;
    items.classList.toggle('radar-stats-hidden', !si);
    if (btnStats) {
      btnStats.setAttribute('aria-expanded', si ? 'true' : 'false');
      btnStats.classList.toggle('is-hidden-mode', !si);
      btnStats.title = si ? 'Ocultar las cifras para leer con calma' : 'Mostrar las cifras del radar';
      document.getElementById('radarToggleStatsText').textContent = si ? 'Ocultar estadísticas' : 'Mostrar estadísticas';
    }
  }

  function abrirDesglose(si) {
    if (!desglose) return;
    desglose.style.display = si ? 'block' : 'none';
    if (btnDesg) {
      btnDesg.setAttribute('aria-expanded', si ? 'true' : 'false');
      btnDesg.classList.toggle('active', si);
      document.getElementById('radarToggleDesgloseText').textContent = si ? 'Plegar desglose' : 'Desglosar cifras ▾';
      document.getElementById('radarToggleDesgloseIcon').textContent = si ? '▲' : '📊';
    }
    if (si) mostrarCifras(true);
  }

  if (btnStats) btnStats.addEventListener('click', function () {
    mostrarCifras(items.classList.contains('radar-stats-hidden'));
  });
  if (btnDesg) btnDesg.addEventListener('click', function () {
    abrirDesglose(desglose.style.display === 'none');
  });
  hub.querySelectorAll('[data-radar-cerrar]').forEach(function (b) {
    b.addEventListener('click', function () {
      abrirDesglose(false);
      if (btnDesg) btnDesg.focus({ preventScroll: true });
      var r = hub.getBoundingClientRect();
      if (r.top < 0) btnDesg.scrollIntoView({ block: 'center', behavior: 'smooth' });
    });
  });

  /* Cada cifra del radar lleva a su tarjeta del desglose (lo abre si esta
     cerrado): se resalta un momento para que el ojo la encuentre. */
  hub.querySelectorAll('a.radar-stat-item[href^="#rc-"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var c = document.getElementById(a.getAttribute('href').slice(1));
      if (!c) return;
      abrirDesglose(true);
      /* La cabecera fija se encoge al bajar: se mide y la tarjeta queda
         debajo de ella, no tapada. */
      e.preventDefault();
      document.body.classList.add('cabecera-compacta');
      var nav = document.querySelector('.site-top-nav');
      var alto = nav ? nav.getBoundingClientRect().height : 0;
      window.scrollTo({ top: Math.max(0, c.getBoundingClientRect().top + window.pageYOffset - alto - 16), behavior: 'smooth' });
      try { history.replaceState(history.state, '', a.getAttribute('href')); } catch (err) { /* sin historial */ }
      c.classList.remove('radar-card-destaca');
      void c.offsetWidth;
      c.classList.add('radar-card-destaca');
    });
  });
  if (/^#rc-/.test(location.hash)) abrirDesglose(true);
})();
