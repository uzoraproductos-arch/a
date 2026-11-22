/* El Inspector de tu servicio (servicios-revisa.html; pedido del autor, 22-11-2026: «cada
   vínculo nos va a dirigir… a una página autónoma independiente dentro de la plataforma
   donde va a estar nuestro inspector… manteniendo ese filtrado del servicio que escojas»).
   El recuadro lo arma sv_mostrador() de apartados.py; ?s=<id> deja elegido el servicio y
   &q= (con &abre=) ya revisa. Contesta con la respuesta completa del Inspector en vista
   «De un vistazo» (servicios-respuesta.html?vista=1), en un marco «av-en-chat»; el
   dictamen es el documento que se descarga. Los archivos se leen en la aplicación del
   servicio, en el navegador: nada se sube. Nunca un monto. */
(function () {
  'use strict';
  var caja = document.getElementById('mostrador'), datosEl = document.getElementById('svMostDatos');
  if (!caja || !datosEl) return;
  var D = {};
  try { D = JSON.parse(datosEl.textContent); } catch (e) { return; }
  var RESP = 'servicios-respuesta.html';
  var sel = document.getElementById('svMostSrv'), q = document.getElementById('svMostQ'), ay = document.getElementById('svMostAy'),
    ej = document.getElementById('svMostEj'), app = document.getElementById('svMostApp'), res = document.getElementById('svMostRes'),
    marco = document.getElementById('svMostMarco'), carga = document.getElementById('svMostCarga'), doc = document.getElementById('svMostDoc'),
    form = caja.querySelector('form');
  var mide = 0;

  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* La dirección guarda el servicio y la pregunta, para compartirla o volver a ella. */
  function anota(sid, texto) {
    try { history.replaceState(null, '', location.pathname + '?s=' + sid + (texto ? '&q=' + encodeURIComponent(texto) : '')); } catch (e) { /* sin historial */ }
  }

  function pinta(sid) {
    var d = D[sid];
    if (!d) return;
    sel.value = sid;
    q.placeholder = d.ph;
    ay.textContent = d.ay;
    ej.innerHTML = d.ej.map(function (x) { return '<button type="button" class="sv-most-chip" data-q="' + esc(x) + '">' + esc(x) + '</button>'; }).join(' ');
    if (d.app) { app.hidden = false; app.textContent = d.bt; app.setAttribute('data-app', d.app); } else app.hidden = true;
    document.title = 'El Inspector: ' + d.n + ' · Auditavisión';
  }

  function alto() {
    try {
      var h = marco.contentDocument && marco.contentDocument.documentElement.scrollHeight;
      if (h && Math.abs(h - marco.offsetHeight) > 4) marco.style.height = h + 'px';
    } catch (e) { /* otro origen: se queda su alto */ }
  }

  function muestra(src, baja) {
    res.hidden = false;
    carga.hidden = false;
    if (doc) doc.hidden = false;
    marco.style.height = '';
    marco.src = src;
    clearInterval(mide);
    mide = setInterval(alto, 600);
    if (baja !== false) res.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function revisa(texto, abreL, baja) {
    var sid = sel.value, t = (texto || '').trim() || (D[sid] && D[sid].q) || '';
    if (!t) return;
    q.value = texto ? texto : '';
    anota(sid, texto ? t : '');
    muestra(RESP + '?vista=1&q=' + encodeURIComponent(t) + (abreL ? '&abre=' + encodeURIComponent(abreL) : ''), baja);
  }

  marco.addEventListener('load', function () { carga.hidden = true; alto(); });
  sel.addEventListener('change', function () { pinta(sel.value); anota(sel.value, ''); q.value = ''; q.focus(); });
  form.addEventListener('submit', function (ev) { ev.preventDefault(); revisa(q.value); });
  caja.addEventListener('click', function (ev) {
    var c = ev.target.closest('.sv-most-chip');
    if (c) { revisa(c.getAttribute('data-q')); return; }
    if (ev.target.closest('.sv-most-app')) muestra(app.getAttribute('data-app'));
  });

  /* Al llegar: el servicio de ?s= (o el primero) y, si trae ?q=, ya revisando. */
  var ps = new URLSearchParams(location.search), pide = ps.get('s'), texto = ps.get('q') || '';
  var sid = D[pide] ? pide : (D[sel.value] ? sel.value : Object.keys(D)[0]);
  pinta(sid);
  if (texto) revisa(texto, ps.get('abre') || '', false);
  else setTimeout(function () { try { q.focus({ preventScroll: true }); } catch (e) { q.focus(); } }, 300);
})();
