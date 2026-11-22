/* El mostrador del Inspector en Servicios (pedido del autor, 22-11-2026: «este chat lo
   vamos a integrar… a cada uno de nuestros servicios… al momento en que le dé clic se va
   a abrir… y ya la respuesta va a ser toda esta parte de nuestro dictamen»).
   Un solo recuadro (#mostrador, sv_mostrador() de apartados.py): se abre bajo la tarjeta
   tocada con su servicio ya elegido, pide lo que ese servicio recibe (SV_ENTRADA) y
   contesta ahí mismo con la respuesta completa del Inspector en vista «De un vistazo»
   (servicios-respuesta.html?vista=1), dentro de un marco «av-en-chat». Los archivos se
   leen en la aplicación del servicio, en el navegador: nada se sube. Nunca un monto. */
(function () {
  'use strict';
  var caja = document.getElementById('mostrador'), datosEl = document.getElementById('svMostDatos');
  if (!caja || !datosEl) return;
  var D = {};
  try { D = JSON.parse(datosEl.textContent); } catch (e) { return; }
  var RESP = 'servicios-respuesta.html';
  var sel = document.getElementById('svMostSrv'), q = document.getElementById('svMostQ'), ay = document.getElementById('svMostAy'),
    ej = document.getElementById('svMostEj'), app = document.getElementById('svMostApp'), res = document.getElementById('svMostRes'),
    marco = document.getElementById('svMostMarco'), carga = document.getElementById('svMostCarga'), form = caja.querySelector('form');
  var mide = 0;

  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function pinta(sid) {
    var d = D[sid];
    if (!d) return;
    sel.value = sid;
    q.placeholder = d.ph;
    ay.textContent = d.ay;
    ej.innerHTML = d.ej.map(function (x) { return '<button type="button" class="sv-most-chip" data-q="' + esc(x) + '">' + esc(x) + '</button>'; }).join(' ');
    if (d.app) { app.hidden = false; app.textContent = d.bt; app.setAttribute('data-app', d.app); } else app.hidden = true;
  }

  function alto() {
    try {
      var h = marco.contentDocument && marco.contentDocument.documentElement.scrollHeight;
      if (h && Math.abs(h - marco.offsetHeight) > 4) marco.style.height = h + 'px';
    } catch (e) { /* otro origen: se queda su alto */ }
  }

  function muestra(src) {
    res.hidden = false;
    carga.hidden = false;
    marco.style.height = '';
    marco.src = src;
    clearInterval(mide);
    mide = setInterval(alto, 600);
    res.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function revisa(texto, abreL) {
    var sid = sel.value, t = (texto || '').trim() || (D[sid] && D[sid].q) || '';
    if (!t) return;
    q.value = texto ? texto : '';
    muestra(RESP + '?vista=1&q=' + encodeURIComponent(t) + (abreL ? '&abre=' + encodeURIComponent(abreL) : ''));
  }

  function abre(sid, tarjeta, texto, abreL) {
    var lista = tarjeta && tarjeta.closest('.sv-cards');
    if (lista) lista.parentNode.insertBefore(caja, lista.nextSibling);
    caja.hidden = false;
    [].forEach.call(document.querySelectorAll('.sv-card.sv-most-activa'), function (c) { c.classList.remove('sv-most-activa'); });
    if (tarjeta) tarjeta.classList.add('sv-most-activa');
    pinta(sid);
    if (texto) revisa(texto, abreL);
    else {
      q.value = '';
      res.hidden = true;
      caja.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setTimeout(function () { try { q.focus({ preventScroll: true }); } catch (e) { q.focus(); } }, 350);
    }
  }

  marco.addEventListener('load', function () { carga.hidden = true; alto(); });
  sel.addEventListener('change', function () { pinta(sel.value); q.focus(); });
  form.addEventListener('submit', function (ev) { ev.preventDefault(); revisa(q.value); });
  caja.addEventListener('click', function (ev) {
    var c = ev.target.closest('.sv-most-chip');
    if (c) { revisa(c.getAttribute('data-q')); return; }
    if (ev.target.closest('.sv-most-app')) {
      muestra(app.getAttribute('data-app'));
      return;
    }
    if (ev.target.closest('.sv-most-cierra')) {
      caja.hidden = true;
      clearInterval(mide);
      marco.src = 'about:blank';
      var act = document.querySelector('.sv-card.sv-most-activa');
      if (act) { act.classList.remove('sv-most-activa'); act.scrollIntoView({ block: 'center' }); }
    }
  });

  /* Las tarjetas de los servicios: su nombre y «Revísalo aquí» abren el mostrador; cada
     novedad, también, ya con su pregunta. Sin JavaScript, las ligas abren la página. */
  var zona = document.getElementById('necesitas') || document;
  zona.addEventListener('click', function (ev) {
    if (ev.defaultPrevented || ev.button > 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey) return;
    var a = ev.target.closest('a[href]'), t = a && a.closest('.sv-card[data-sv-srv]');
    if (!t || caja.contains(a)) return;
    var sid = t.getAttribute('data-sv-srv');
    if (a.hasAttribute('data-sv-most') || a.closest('.sv-card-tit')) { ev.preventDefault(); abre(sid, t); return; }
    if (a.closest('.sv-nuevo-lista') && a.pathname.split('/').pop() === RESP) {
      ev.preventDefault();
      var ps = new URLSearchParams(a.search);
      abre(sid, t, ps.get('q') || '', ps.get('abre') || '');
    }
  });

  /* #revisa-<id> abre el mostrador con ese servicio (?servicio= es de la cotización). */
  var pide = (/^#revisa-([a-z]+)$/.exec(location.hash) || [])[1];
  if (pide && D[pide]) {
    var tj = document.querySelector('.sv-card[data-sv-srv="' + pide + '"]'), panel = tj && tj.closest('[data-sv-panel]');
    var tab = panel && document.querySelector('[data-sv-tab="' + panel.getAttribute('data-sv-panel') + '"]');
    if (tab && tab.getAttribute('aria-pressed') !== 'true') tab.click();
    abre(pide, tj);
  }
})();
