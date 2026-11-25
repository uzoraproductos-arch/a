/* Ronda 21 (25-11-2026, diseño D + F del autor): lo que se mueve en el lienzo del Auditor.
   - El selector de cuatro modos (Inspector primero) usa los mismos botones del chat (poneModo
     de asistente.js), así que el modo se recuerda igual (av-modo).
   - «Tu portafolio reciente» lee av-portafolio (lo escribe sv-mostrador.js): solo este navegador.
   - El Escáner Cero CIEC pasa los archivos al Lector de facturas o a la matriz del padrón en un
     marco de esta misma página: nada se sube y nunca se pide la Contraseña del SAT.
   Se carga antes que asistente.js y espera al DOM. */
(function () {
  'use strict';
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function listo() {
    var avb = document.getElementById('avb'), app = document.getElementById('paApp');
    if (!avb) return;

    /* Los cuatro modos. */
    var segs = avb.querySelectorAll('[data-avb-modo]'),
      envia = [app && app.querySelector('.pa-form button[type="submit"]'), document.getElementById('avbEnvia')];
    function marca(m) {
      Array.prototype.forEach.call(segs, function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-avb-modo') === m ? 'true' : 'false'); });
      envia.forEach(function (b) { if (b) b.textContent = m === 'inspector' ? 'Dictaminar ➔' : 'Investigar ➔'; });
    }

    /* La caja del hero, sus ejemplos y las ocho preguntas preguntan en el chat de abajo. */
    var campo = document.getElementById('paPregunta'), forma = document.getElementById('paForm'), chat = document.getElementById('avbChat');
    /* Ronda 22 (25-11-2026): una sola caja, la del hero. La tarjeta de la plática aparece solo cuando ya hay una
       pregunta (también al volver con la plática guardada) y se esconde con «Limpiar». */
    var hilo = document.getElementById('paHilo');
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
      var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (ult || chat) (ult || chat).scrollIntoView({ behavior: quieto ? 'auto' : 'smooth', block: 'start' });
    }
    var hf = document.getElementById('avbForm'), hq = document.getElementById('avbQ');
    /* Lo que el chat deja escrito en su caja (escondida) pasa a la del hero: «Regresar» y las ligas con ?p=. */
    function alHero() {
      if (!campo || !hq || !campo.value) return;
      hq.value = campo.value; campo.value = '';
      hf.scrollIntoView({ block: 'center' });
      hq.focus({ preventScroll: true });
    }
    var reg = document.getElementById('paRegresa');
    if (reg) reg.addEventListener('click', function () { setTimeout(alHero, 0); });
    if (/[?&]p=/.test(location.search)) setTimeout(alHero, 0);
    /* «Hacer otra pregunta» regresa a la única caja. */
    var otra = document.getElementById('avbOtra');
    if (otra && hq) otra.addEventListener('click', function () {
      hf.scrollIntoView({ behavior: 'smooth', block: 'center' });
      hq.focus({ preventScroll: true });
    });
    if (hf) hf.addEventListener('submit', function (ev) { ev.preventDefault(); pregunta(hq.value); hq.value = ''; });
    if (hq) hq.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' && !ev.shiftKey) { ev.preventDefault(); hf.requestSubmit ? hf.requestSubmit() : pregunta(hq.value); } });
    avb.addEventListener('click', function (ev) { var b = ev.target.closest('[data-avb-q]'); if (b) pregunta(b.getAttribute('data-avb-q')); });
    /* Una pregunta a la vez cada 4 s; con el movimiento reducido, todas a la vista y quietas. */
    var ps = document.querySelectorAll('#avbPreg li'), quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (quieto) Array.prototype.forEach.call(ps, function (li) { li.hidden = false; });
    else if (ps.length > 1) {
      var k = 0, para = false, caja = document.getElementById('avbPreg');
      caja.addEventListener('mouseenter', function () { para = true; });
      caja.addEventListener('mouseleave', function () { para = false; });
      caja.addEventListener('focusin', function () { para = true; });
      caja.addEventListener('focusout', function () { para = false; });
      setInterval(function () {
        if (para || document.hidden) return;
        ps[k].hidden = true; k = (k + 1) % ps.length; ps[k].hidden = false;
      }, 4000);
    }
    Array.prototype.forEach.call(segs, function (b) {
      b.addEventListener('click', function () {
        var op = app && app.querySelector('.pa-modo-op[data-pa-modo="' + b.getAttribute('data-avb-modo') + '"]');
        if (op) op.click();
      });
    });
    if (app) {
      app.addEventListener('pa-modo', function (ev) { marca(ev.detail); });
      marca(app.getAttribute('data-modo'));
      setTimeout(function () { marca(app.getAttribute('data-modo')); }, 0);
    }

    /* Tu portafolio reciente (los tres últimos). */
    var lista = document.getElementById('avbPortLista'), vacio = document.getElementById('avbPortVacio');
    function port() {
      var l = [];
      try { l = JSON.parse(localStorage.getItem('av-portafolio') || '[]'); if (!Array.isArray(l)) l = []; } catch (e) { l = []; }
      l = l.filter(function (x) { return x && x.q; }).slice(0, 3);
      lista.hidden = !l.length;
      vacio.hidden = !!l.length;
      lista.innerHTML = l.map(function (x) {
        var u = 'servicios-revisa.html?s=' + encodeURIComponent(x.s || '') + '&q=' + encodeURIComponent(x.q);
        return '<li><a href="' + esc(u) + '">' + esc(x.t || x.q) + '<small>' + esc(x.f || '') + '</small></a></li>';
      }).join('');
    }
    if (lista) { port(); window.addEventListener('storage', function (ev) { if (ev.key === 'av-portafolio') port(); }); }
    /* En el celular, el portafolio y los servicios van plegados. */
    var mas = avb.querySelector('.avb-mas');
    if (mas && window.matchMedia && window.matchMedia('(max-width: 980px)').matches) mas.open = false;

    /* El Escáner Cero CIEC. */
    var suelta = document.getElementById('avbSuelta'), arch = document.getElementById('avbArch'),
      caja = document.getElementById('avbLector'), marco = document.getElementById('avbMarco'), pend = null;
    var APPS = { xml: ['herramienta-inspector-factura.html', 'cfArchivos'], csv: ['herramienta-inspector-padron.html#lote', 'pdArch'] };
    function pasa() {
      var fs = pend && pend[1], campo;
      if (!fs) return;
      pend = null;
      try {
        campo = marco.contentDocument && marco.contentDocument.getElementById(campoId);
        if (!campo) return;
        var dt = new DataTransfer();
        Array.prototype.forEach.call(fs, function (f) { dt.items.add(f); });
        campo.files = dt.files;
        campo.dispatchEvent(new Event('change', { bubbles: true }));
      } catch (e) { /* el navegador no deja pasar archivos: se eligen dentro de la aplicación */ }
    }
    var campoId = null;
    function recibe(fs) {
      if (!fs || !fs.length) return;
      var todosXml = Array.prototype.every.call(fs, function (f) { return /\.xml$/i.test(f.name) || /xml/.test(f.type); });
      var a = todosXml ? APPS.xml : APPS.csv;
      campoId = a[1];
      pend = [a[0], fs];
      caja.hidden = false;
      if (marco.getAttribute('data-app') === a[0] && marco.contentDocument && marco.contentDocument.readyState === 'complete') pasa();
      else { marco.setAttribute('data-app', a[0]); marco.src = a[0]; }
      caja.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    if (marco) marco.addEventListener('load', pasa);
    if (suelta && arch) {
      ['dragenter', 'dragover'].forEach(function (t) { suelta.addEventListener(t, function (ev) { ev.preventDefault(); suelta.classList.add('avb-sobre'); }); });
      ['dragleave', 'drop'].forEach(function (t) { suelta.addEventListener(t, function () { suelta.classList.remove('avb-sobre'); }); });
      suelta.addEventListener('drop', function (ev) { ev.preventDefault(); recibe(ev.dataTransfer && ev.dataTransfer.files); });
      arch.addEventListener('change', function () { recibe(arch.files); });
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', listo); else listo();
})();
