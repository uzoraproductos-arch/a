/* Auditavisión · «Volver al Auditor» (24-10-2026, pedido del autor).
   Cuando el lector sale del chat por un enlace de una respuesta («Saber
   más», un expediente, una página de la plataforma), la página a la que
   llega le ofrece regresar: un botón flotante abajo a la izquierda. La
   plática lo espera tal como la dejó (asistente.js la guarda en la pestaña).
   La seña vive en sessionStorage y se borra al volver al chat o con ✕. */
(function () {
  'use strict';
  var CHAT = 'herramienta-inspector-pregunta.html', SENA = 'av-volver';
  var aqui = location.pathname.split('/').pop();
  /* Dentro del chat (24-10-2026, pedido del autor): el Auditor abre las seis
     aplicaciones del Modo Inspector en un marco de su respuesta. La página se
     muestra sola, sin cabecera, menú ni pie, y sus enlaces a otras páginas
     salen a la pestaña entera (con la seña para volver). El marco se llama
     «av-en-chat»: el nombre sobrevive a las navegaciones dentro de él. */
  var enChat = false;
  try { enChat = window.self !== window.top && window.top.location.origin === location.origin && window.name === 'av-en-chat'; } catch (e) { enChat = false; }
  if (enChat) {
    document.documentElement.classList.add('av-en-chat');
    document.addEventListener('click', function (ev) {
      var a = ev.target.closest ? ev.target.closest('a[href]') : null;
      if (!a || ev.defaultPrevented || a.target) return;
      if (a.origin === location.origin && a.pathname === location.pathname) return;
      a.target = '_top';
      try { sessionStorage.setItem(SENA, '1'); } catch (e) { /* nada */ }
    });
    return;
  }
  /* Todo pasa por el Auditor (decisión del autor, 19-11-2026: «entre pestañas no se
     vinculan: todo es a través del Auditor»). Las ligas de las páginas ya llegan
     mudadas al chat (servicios_fichas.por_auditor_html); esta es la red para las que
     arma el navegador (la ficha del Planisferio, por ejemplo): al tocar una liga a
     otra pestaña, se cambia por la del chat con la pregunta y ?abre=. La regla de
     cada pestaña es la de pestana_de() en servicios_fichas.py. */
  var EXC = { 'periodismo-en-riesgo.html': 'Noticiero' };
  function pestana(f) {
    if (EXC[f]) return EXC[f];
    if (f === CHAT || f === 'herramienta-inspector-dictamen.html') return 'Auditor';
    if (!f || f === 'index.html') return null;
    if (/^servicios?(-|\.html)/.test(f)) return 'Servicios';
    if (f.indexOf('planisferio') === 0) return 'Planisferio';
    if (f.indexOf('noticias') === 0) return 'Noticiero';
    return 'Comunidad';
  }
  var mia = pestana(aqui || 'index.html');
  if (mia && mia !== 'Auditor') {
    document.addEventListener('click', function (ev) {
      var a = ev.target.closest ? ev.target.closest('a[href]') : null;
      if (!a || a.origin !== location.origin || !a.closest('main') || a.closest('.pt-cajon, .apartado-migas, .site-top-nav')) return;
      var f = a.pathname.split('/').pop(), t = pestana(f);
      if (!/\.html$/.test(f) || !t || t === mia || t === 'Auditor') return;
      var b = a.querySelector('b'), q = ((b || a).textContent || '').replace(/\s+/g, ' ').replace(/[➔→›»]/g, '').trim();
      if (q.length < 4 || q.length > 140) q = f.replace(/\.html$/, '').replace(/-/g, ' ');
      a.href = CHAT + '?q=' + encodeURIComponent(q) + '&abre=' + encodeURIComponent(f + a.search + a.hash);
    }, true);
  }
  try {

    if (aqui === CHAT) { sessionStorage.removeItem(SENA); return; }
    if (!sessionStorage.getItem(SENA)) return;
  } catch (e) { return; }
  function pon() {
    if (document.querySelector('.av-volver')) return;
    var caja = document.createElement('div');
    caja.className = 'av-volver';
    caja.innerHTML = '<a class="av-volver-ir" href="' + CHAT + '">' +
      '<img src="assets/auditor/img/logo-auditavision.svg" alt="" width="34" height="26">' +
      '<span><b>Volver al Auditor</b><small>Tu plática sigue ahí</small></span></a>' +
      '<button type="button" class="av-volver-x" aria-label="Ocultar «Volver al Auditor»">✕</button>';
    caja.querySelector('.av-volver-ir').addEventListener('click', function (ev) {
      /* Si se llegó directo del chat, «atrás» lo recupera con todo y su lugar. */
      if (document.referrer && document.referrer.split('?')[0].split('#')[0].slice(-CHAT.length) === CHAT && history.length > 1) {
        ev.preventDefault();
        history.back();
      }
    });
    caja.querySelector('.av-volver-x').addEventListener('click', function () {
      try { sessionStorage.removeItem(SENA); } catch (e) { /* nada */ }
      caja.parentNode.removeChild(caja);
    });
    document.body.appendChild(caja);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', pon);
  else pon();
})();
