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
