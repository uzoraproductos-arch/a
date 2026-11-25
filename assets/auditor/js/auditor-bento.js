/* La página del Auditor: lo que se mueve en el lienzo (herramientas/auditor_bento.py).
   Ronda 21 (25-11-2026): los cuatro modos, el portafolio y el lector local. Ronda 22: una sola caja.
   Ronda 23 (25-11-2026, diseño «Solo barra lateral» del autor): la caja lleva arriba los modos con su pista y abajo
   «Adjuntar XML / CSV · Cero CIEC», que también recibe archivos soltados sobre la caja; «Nueva revisión» regresa a
   ella. Sin emojis: íconos SVG de trazo.
   - El selector de modos usa los mismos botones del chat (poneModo de asistente.js): el modo se recuerda (av-modo).
   - «Tu portafolio» lee av-portafolio (lo escribe sv-mostrador.js): solo este navegador.
   - Los XML van al Lector de facturas y el CSV a la matriz del padrón, en un marco de esta misma página: nada se
     sube y nunca se pide la Contraseña del SAT.
   Se carga antes que asistente.js y espera al DOM. */
(function () {
  'use strict';
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var DOC = '<svg class="avb-i" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h4"/></svg>';
  function quieto() { return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches; }
  function listo() {
    var avb = document.getElementById('avb'), app = document.getElementById('paApp');
    if (!avb) return;

    /* Los cuatro modos, con su pista. */
    var segs = avb.querySelectorAll('[data-avb-modo]'), envia = document.getElementById('avbEnvia'),
      pista = document.getElementById('avbPista');
    function marca(m) {
      Array.prototype.forEach.call(segs, function (b) {
        var si = b.getAttribute('data-avb-modo') === m;
        b.setAttribute('aria-pressed', si ? 'true' : 'false');
        if (si && pista) pista.textContent = b.getAttribute('data-pista');
      });
      var t = envia && envia.querySelector('span');
      if (t) t.textContent = m === 'inspector' ? 'Dictaminar' : 'Investigar';
    }

    /* La caja y sus ejemplos preguntan en la plática de abajo (Ronda 22: es la única caja). La tarjeta de la plática
       aparece solo cuando ya hay una pregunta (también al volver con la plática guardada) y se esconde con «Limpiar». */
    var campo = document.getElementById('paPregunta'), forma = document.getElementById('paForm'), chat = document.getElementById('avbChat'),
      hilo = document.getElementById('paHilo');
    function verChat() { if (chat && hilo) chat.hidden = !hilo.querySelector('.pa-yo'); }
    if (hilo && window.MutationObserver) new MutationObserver(verChat).observe(hilo, { childList: true });
    verChat();
    setTimeout(verChat, 0);
    function pregunta(q) {
      q = (q || '').trim();
      if (!q || !campo || !forma) return;
      campo.value = q.slice(0, 600);
      if (forma.requestSubmit) forma.requestSubmit(); else forma.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      verChat();
      var yo = hilo && hilo.querySelectorAll('.pa-yo'), ult = yo && yo[yo.length - 1];
      if (ult || chat) (ult || chat).scrollIntoView({ behavior: quieto() ? 'auto' : 'smooth', block: 'start' });
    }
    var hf = document.getElementById('avbForm'), hq = document.getElementById('avbQ');
    function aLaCaja(arriba) {
      if (!hf || !hq) return;
      if (arriba) window.scrollTo({ top: 0, behavior: quieto() ? 'auto' : 'smooth' });
      else hf.scrollIntoView({ behavior: quieto() ? 'auto' : 'smooth', block: 'center' });
      hq.focus({ preventScroll: true });
    }
    /* Lo que el chat deja escrito en su caja (escondida) pasa a la única caja: «Regresar» y las ligas con ?p=. */
    function alaCajaTexto() {
      if (!campo || !hq || !campo.value) return;
      hq.value = campo.value; campo.value = '';
      aLaCaja(false);
    }
    var reg = document.getElementById('paRegresa');
    if (reg) reg.addEventListener('click', function () { setTimeout(alaCajaTexto, 0); });
    if (/[?&]p=/.test(location.search)) setTimeout(alaCajaTexto, 0);
    var otra = document.getElementById('avbOtra');
    if (otra) otra.addEventListener('click', function () { aLaCaja(false); });
    /* «Nueva revisión»: regresa arriba, a la caja vacía (la plática queda guardada hasta «Limpiar»). */
    var nueva = document.getElementById('avbNueva');
    if (nueva) nueva.addEventListener('click', function () { if (hq) hq.value = ''; aLaCaja(true); });
    if (hf) hf.addEventListener('submit', function (ev) { ev.preventDefault(); pregunta(hq.value); hq.value = ''; });
    if (hq) hq.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' && !ev.shiftKey) { ev.preventDefault(); if (hf.requestSubmit) hf.requestSubmit(); else pregunta(hq.value); } });
    avb.addEventListener('click', function (ev) { var b = ev.target.closest('[data-avb-q]'); if (b) pregunta(b.getAttribute('data-avb-q')); });
    Array.prototype.forEach.call(segs, function (b) {
      b.addEventListener('click', function () {
        var m = b.getAttribute('data-avb-modo'), op = app && app.querySelector('.pa-modo-op[data-pa-modo="' + m + '"]');
        if (op) op.click(); else marca(m);
      });
    });
    if (app) {
      app.addEventListener('pa-modo', function (ev) { marca(ev.detail); });
      marca(app.getAttribute('data-modo'));
      setTimeout(function () { marca(app.getAttribute('data-modo')); }, 0);
    }

    /* Tu portafolio (los tres últimos), en una línea cada uno. */
    var lista = document.getElementById('avbPortLista'), vacio = document.getElementById('avbPortVacio');
    function port() {
      var l = [];
      try { l = JSON.parse(localStorage.getItem('av-portafolio') || '[]'); if (!Array.isArray(l)) l = []; } catch (e) { l = []; }
      l = l.filter(function (x) { return x && x.q; }).slice(0, 3);
      lista.hidden = !l.length;
      vacio.hidden = !!l.length;
      lista.innerHTML = l.map(function (x) {
        var u = 'servicios-revisa.html?s=' + encodeURIComponent(x.s || '') + '&q=' + encodeURIComponent(x.q);
        return '<li><a href="' + esc(u) + '" title="' + esc((x.t || x.q) + (x.f ? ' · ' + x.f : '')) + '">' + DOC + '<span>' + esc(x.t || x.q) + '</span></a></li>';
      }).join('');
    }
    if (lista) { port(); window.addEventListener('storage', function (ev) { if (ev.key === 'av-portafolio') port(); }); }
    /* En el celular, el portafolio va plegado. */
    var pd = document.getElementById('avbPort');
    if (pd && window.matchMedia && window.matchMedia('(max-width: 980px)').matches) pd.open = false;

    /* Adjuntar XML / CSV · Cero CIEC: el botón de la caja, o soltarlos sobre la caja. */
    var arch = document.getElementById('avbArch'), caja = document.getElementById('avbLector'), marco = document.getElementById('avbMarco'),
      pend = null, campoId = null;
    var APPS = { xml: ['herramienta-inspector-factura.html', 'cfArchivos'], csv: ['herramienta-inspector-padron.html#lote', 'pdArch'] };
    function pasa() {
      var fs = pend && pend[1], c;
      if (!fs) return;
      pend = null;
      try {
        c = marco.contentDocument && marco.contentDocument.getElementById(campoId);
        if (!c) return;
        var dt = new DataTransfer();
        Array.prototype.forEach.call(fs, function (f) { dt.items.add(f); });
        c.files = dt.files;
        c.dispatchEvent(new Event('change', { bubbles: true }));
      } catch (e) { /* el navegador no deja pasar archivos: se eligen dentro de la aplicación */ }
    }
    function recibe(fs) {
      if (!fs || !fs.length) return;
      var todosXml = Array.prototype.every.call(fs, function (f) { return /\.xml$/i.test(f.name) || /xml/.test(f.type); });
      var a = todosXml ? APPS.xml : APPS.csv;
      campoId = a[1];
      pend = [a[0], fs];
      caja.hidden = false;
      if (marco.getAttribute('data-app') === a[0] && marco.contentDocument && marco.contentDocument.readyState === 'complete') pasa();
      else { marco.setAttribute('data-app', a[0]); marco.src = a[0]; }
      caja.scrollIntoView({ behavior: quieto() ? 'auto' : 'smooth', block: 'start' });
    }
    if (marco) marco.addEventListener('load', pasa);
    if (arch) arch.addEventListener('change', function () { recibe(arch.files); });
    if (hf) {
      ['dragenter', 'dragover'].forEach(function (t) { hf.addEventListener(t, function (ev) { ev.preventDefault(); hf.classList.add('avb-sobre'); }); });
      ['dragleave', 'drop'].forEach(function (t) { hf.addEventListener(t, function (ev) { if (t === 'dragleave' && hf.contains(ev.relatedTarget)) return; hf.classList.remove('avb-sobre'); }); });
      hf.addEventListener('drop', function (ev) { ev.preventDefault(); recibe(ev.dataTransfer && ev.dataTransfer.files); });
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', listo); else listo();
})();
