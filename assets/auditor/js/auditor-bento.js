/* La página del Auditor: lo que se mueve en la Estación (herramientas/auditor_bento.py).
   Ronda 21 (25-11-2026): los cuatro modos, el portafolio y el lector local. Ronda 22: una sola caja.
   Ronda 23: la caja con los modos arriba y «Adjuntar XML / CSV · Cero CIEC» abajo; sin emojis.
   Ronda 24 (25-11-2026, decisión del autor): la Estación de Auditoría en tres paneles.
   - La Mesa de Trabajo (derecha) se oculta y se muestra; en pantallas de menos de 1100 px va oculta y abre como cajón.
   - «Expediente vivo»: al contestar el Auditor, lee de la última respuesta del chat sus ligas a documentos, su
     «Generar dictamen» y su «Saber más». No escribe cifras ni documentos: solo enseña lo que el chat ya citó.
   - Las preguntas de la entrada (acceso.PREGUNTAS_ENTRADA) rotan cada 4 s; se pausan con el cursor o el foco y, si
     el navegador pide menos movimiento, se ven todas. Al tocar una, el Auditor la contesta.
   - «Probar XML de muestra»: arma en el navegador un CFDI 4.0 ficticio con RFC genéricos de prueba del SAT
     (EKU9003173C9 y XAXX010101000) y lo abre en el Lector de facturas. Nada se sube.
   - «Cómo funciona (3 pasos)»: un recorrido que solo abre con su botón; deja av-tour-visto en este navegador.
   - El selector de modos usa los mismos botones del chat (poneModo de asistente.js): el modo se recuerda (av-modo).
   - «Tu portafolio» lee av-portafolio (lo escriben sv-mostrador.js y el Expediente vivo): solo este navegador.
   Se carga antes que asistente.js y espera al DOM. */
(function () {
  'use strict';
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var SVG = function (d) { return '<svg class="avb-i" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' + d + '</svg>'; };
  var DOC = SVG('<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h4"/>');
  var LIGA = SVG('<path d="M14 4h6v6"/><path d="M20 4 11 13"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>');
  function quieto() { return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches; }
  function ancho() { return !window.matchMedia || window.matchMedia('(min-width: 1100px)').matches; }
  function guarda(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* el navegador no deja guardar */ } }
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

    /* La Mesa de Trabajo: a la derecha en escritorio; cajón en pantallas angostas. */
    var mesa = document.getElementById('avbMesa'), mBtn = document.getElementById('avbMesaBtn'), mX = document.getElementById('avbMesaX'),
      velo = document.getElementById('avbVelo'), aviso = document.getElementById('avbAviso');
    function mesaVista() { return !avb.classList.contains('avb-sin-mesa') && (ancho() || avb.classList.contains('avb-mesa-abierta')); }
    function pintaBtn() {
      var v = mesaVista();
      if (!mBtn) return;
      mBtn.setAttribute('aria-expanded', v ? 'true' : 'false');
      mBtn.querySelector('span').textContent = v ? 'Ocultar mesa derecha' : 'Mostrar mesa derecha';
      if (v && aviso) aviso.hidden = true;
      if (velo) velo.hidden = !(v && !ancho());
    }
    function abreMesa(si, foco) {
      if (ancho()) avb.classList.toggle('avb-sin-mesa', !si);
      else { avb.classList.remove('avb-sin-mesa'); avb.classList.toggle('avb-mesa-abierta', si); }
      pintaBtn();
      if (si && foco && mesa) { var t = mesa.querySelector('[aria-selected="true"]'); if (t) t.focus(); }
      if (!si && foco && mBtn) mBtn.focus();
    }
    if (mBtn) mBtn.addEventListener('click', function () { abreMesa(!mesaVista(), true); });
    if (mX) mX.addEventListener('click', function () { abreMesa(false, true); });
    if (velo) velo.addEventListener('click', function () { abreMesa(false, true); });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && !ancho() && avb.classList.contains('avb-mesa-abierta') && !tourVivo()) abreMesa(false, true);
    });
    if (window.matchMedia) {
      var mq = window.matchMedia('(min-width: 1100px)');
      var cambia = function () { avb.classList.remove('avb-mesa-abierta'); pintaBtn(); };
      if (mq.addEventListener) mq.addEventListener('change', cambia); else if (mq.addListener) mq.addListener(cambia);
    }
    pintaBtn();

    /* Las dos pestañas de la Mesa. */
    var tabs = [document.getElementById('avbTabH'), document.getElementById('avbTabE')];
    function pestana(i, foco) {
      tabs.forEach(function (t, j) {
        if (!t) return;
        t.setAttribute('aria-selected', i === j ? 'true' : 'false');
        t.tabIndex = i === j ? 0 : -1;
        var p = document.getElementById(t.getAttribute('aria-controls'));
        if (p) p.hidden = i !== j;
      });
      if (foco && tabs[i]) tabs[i].focus();
    }
    tabs.forEach(function (t, i) {
      if (!t) return;
      t.addEventListener('click', function () { pestana(i); });
      t.addEventListener('keydown', function (ev) {
        if (ev.key === 'ArrowRight' || ev.key === 'ArrowLeft') { ev.preventDefault(); pestana(1 - i, true); }
      });
    });

    /* La caja y sus ejemplos preguntan en la plática de abajo (Ronda 22: es la única caja). La tarjeta de la plática
       aparece solo cuando ya hay una pregunta (también al volver con la plática guardada) y se esconde con «Limpiar». */
    var campo = document.getElementById('paPregunta'), forma = document.getElementById('paForm'), chat = document.getElementById('avbChat'),
      hilo = document.getElementById('paHilo');
    function verChat() { if (chat && hilo) chat.hidden = !hilo.querySelector('.pa-yo'); }

    /* Expediente vivo: lo que la última respuesta ya citó. */
    var exp = { vacio: document.getElementById('avbExpVacio'), caja: document.getElementById('avbExp'), q: document.getElementById('avbExpQ'),
      chips: document.getElementById('avbExpChips'), fu: document.getElementById('avbExpFu'), sin: document.getElementById('avbExpSin'),
      dic: document.getElementById('avbExpDic'), ver: document.getElementById('avbExpVer'), guarda: document.getElementById('avbExpGuarda') };
    exp.vis = document.getElementById('avbExpVis');
    exp.por = document.getElementById('avbExpPor');
    exp.porT = document.getElementById('avbExpPorT');
    /* Ronda 26B: las páginas de la plataforma que la respuesta ya liga, como portales para ir a fondo (y volver con
       «Volver al Auditor»). Se reconoce su sección por el nombre del archivo; no se agrega ninguna liga nueva. */
    var PORTALES = [[/^planisferio/, 'Planisferio'], [/^(herramienta-calculadora|cc-|calculadora)/, 'Simulador'], [/^auditoria-/, 'Auditoría en imágenes'],
      [/^expedientes?(-|\.)/, 'Expediente'], [/^servicio/, 'Servicio'], [/^noticias/, 'Noticiero'], [/^herramienta-/, 'Aplicación'],
      [/^(diccionario|glosario|fuentes-oficiales|marco-legal)/, 'Biblioteca']];
    var MAPA = SVG('<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>');
    function portales(bot) {
      var vistos = {}, out = [], aqui = location.pathname.split('/').pop();
      Array.prototype.forEach.call(bot.querySelectorAll('a[href]'), function (a) {
        var h = a.getAttribute('href') || '';
        if (/^(https?:|mailto:|#|javascript:)/i.test(h) || a.matches('.pa-genera, .pa-ver') || out.length >= 6) return;
        var arch = h.split('#')[0].split('?')[0].split('/').pop();
        if (!/\.html$/.test(arch) || arch === aqui || arch === 'herramienta-inspector-dictamen.html' || vistos[arch]) return;
        vistos[arch] = 1;
        var tipo = 'Página de la plataforma';
        PORTALES.some(function (p) { if (p[0].test(arch)) { tipo = p[1]; return true; } return false; });
        var t = texto(a).slice(0, 90) || arch;
        out.push('<li><a href="' + esc(h) + '">' + MAPA + '<span><small>' + esc(tipo) + '</small><b>' + esc(t) + '</b></span></a></li>');
      });
      return out;
    }
    var ultimo = null, visto = '';
    function texto(el) { return el ? (el.textContent || '').replace(/\s+/g, ' ').trim() : ''; }
    function leeExpediente() {
      if (!hilo || !exp.caja) return;
      var yo = hilo.querySelectorAll('.pa-yo'), bots = hilo.querySelectorAll('.pa-bot:not(.pa-escribe):not(.pa-modo-aviso)');
      if (!yo.length || !bots.length) { exp.caja.hidden = true; exp.vacio.hidden = false; ultimo = null; visto = ''; return; }
      var bot = bots[bots.length - 1], q = texto(yo[yo.length - 1]);
      var firma = q + '|' + bot.innerHTML.length;
      if (firma === visto) return;
      var nueva = visto.split('|')[0] !== q;
      visto = firma;
      var vistos = {}, fu = [];
      Array.prototype.forEach.call(bot.querySelectorAll('a[href^="http"]'), function (a) {
        var h = a.href.split('#')[0];
        if (vistos[h] || fu.length >= 8) return;
        vistos[h] = 1;
        var host = '';
        try { host = new URL(h).hostname.replace(/^www\./, ''); } catch (e) { host = ''; }
        fu.push('<li><a href="' + esc(a.href) + '" target="_blank" rel="noopener">' + LIGA + '<span><b>' + esc(texto(a).slice(0, 110) || host) + '</b><small>' + esc(host) + '</small></span></a></li>');
      });
      var cuenta = { oficial: 0, derivado: 0, pendiente: 0 };
      Array.prototype.forEach.call(bot.querySelectorAll('.est-chip'), function (c) {
        var m = /est-(oficial|derivado|pendiente)/.exec(c.className);
        if (m) cuenta[m[1]]++;
      });
      var chips = [];
      if (cuenta.oficial) chips.push('<span class="est-chip est-oficial">oficial</span> ' + cuenta.oficial);
      if (cuenta.derivado) chips.push('<span class="est-chip est-derivado">auditada</span> ' + cuenta.derivado);
      if (cuenta.pendiente) chips.push('<span class="est-chip est-pendiente">pendiente</span> ' + cuenta.pendiente);
      var dic = bot.querySelector('a.pa-genera'), ver = bot.querySelector('a.pa-ver');
      exp.q.textContent = '«' + q + '»';
      exp.chips.innerHTML = chips.length ? 'Datos en la respuesta: ' + chips.join(' · ') : '';
      exp.fu.innerHTML = fu.join('');
      exp.fu.hidden = !fu.length;
      exp.sin.hidden = !!fu.length;
      exp.dic.hidden = !dic;
      if (dic) { exp.dic.href = dic.getAttribute('href'); exp.dic.querySelector('span').textContent = /ficha/i.test(texto(dic)) ? 'Generar ficha' : 'Generar dictamen'; }
      exp.ver.hidden = !ver;
      if (ver) exp.ver.href = ver.getAttribute('href');
      if (exp.por) {
        var pt = portales(bot);
        exp.por.innerHTML = pt.join('');
        exp.por.hidden = exp.porT.hidden = !pt.length;
      }
      if (nueva && exp.vis && window.AuditorBot && window.AuditorBot.visual) {
        /* El mini-mapa del INEGI y el semáforo del lugar de la pregunta (insp-visual.js): lo que la base ya trae, dibujado. */
        exp.vis.innerHTML = '';
        exp.vis.hidden = true;
        window.AuditorBot.visual(q, exp.vis, function () {
          var h3 = exp.vis.querySelector('.pv h3 span[aria-hidden]');
          if (h3) h3.parentNode.removeChild(h3);
          exp.vis.hidden = !exp.vis.innerHTML;
        });
      }
      if (nueva) { exp.guarda.disabled = false; exp.guarda.querySelector('span').textContent = 'Guardar en mi portafolio'; }
      ultimo = { q: q, dic: dic ? dic.getAttribute('href') : '' };
      exp.vacio.hidden = true;
      exp.caja.hidden = false;
      if (nueva) {
        pestana(1);
        if (!mesaVista() && aviso) aviso.hidden = false;
      }
    }
    var espera = 0;
    function cambioHilo() { verChat(); clearTimeout(espera); espera = setTimeout(leeExpediente, 250); }
    if (hilo && window.MutationObserver) new MutationObserver(cambioHilo).observe(hilo, { childList: true, subtree: true });
    verChat();
    setTimeout(function () { verChat(); leeExpediente(); }, 0);

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
    /* «Nueva revisión»: regresa arriba, a la caja vacía y a «Herramientas» (la plática queda guardada hasta «Limpiar»). */
    var nueva = document.getElementById('avbNueva');
    if (nueva) nueva.addEventListener('click', function () { if (hq) hq.value = ''; pestana(0); aLaCaja(true); });
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

    /* Las preguntas de la entrada, una cada 4 s. */
    var rota = document.getElementById('avbRota'), rq = rota ? rota.querySelectorAll('li') : [], ri = 0, rt = 0, pausa = false;
    if (rq.length > 1 && !quieto()) {
      rota.classList.add('avb-rota-viva');
      var muestra = function (i) { Array.prototype.forEach.call(rq, function (li, j) { li.classList.toggle('avb-rota-on', i === j); }); };
      muestra(0);
      rt = setInterval(function () { if (pausa || document.hidden) return; ri = (ri + 1) % rq.length; muestra(ri); }, 4000);
      ['mouseenter', 'focusin'].forEach(function (t) { rota.addEventListener(t, function () { pausa = true; }); });
      ['mouseleave', 'focusout'].forEach(function (t) { rota.addEventListener(t, function (ev) { if (t === 'focusout' && rota.contains(ev.relatedTarget)) return; pausa = false; }); });
    }

    /* Tu portafolio (los tres últimos), en una línea cada uno. */
    var lista = document.getElementById('avbPortLista'), vacio = document.getElementById('avbPortVacio');
    function leePort() { try { var l = JSON.parse(localStorage.getItem('av-portafolio') || '[]'); return Array.isArray(l) ? l : []; } catch (e) { return []; } }
    function port() {
      var l = leePort().filter(function (x) { return x && x.q; }).slice(0, 3);
      lista.hidden = !l.length;
      vacio.hidden = !!l.length;
      lista.innerHTML = l.map(function (x) {
        var u = x.o === 'auditor' ? 'herramienta-inspector-pregunta.html?q=' + encodeURIComponent(x.q)
          : 'servicios-revisa.html?s=' + encodeURIComponent(x.s || '') + '&q=' + encodeURIComponent(x.q);
        return '<li><a href="' + esc(u) + '" title="' + esc((x.t || x.q) + (x.f ? ' · ' + x.f : '')) + '">' + DOC + '<span>' + esc(x.t || x.q) + '</span></a></li>';
      }).join('');
    }
    if (lista) { port(); window.addEventListener('storage', function (ev) { if (ev.key === 'av-portafolio') port(); }); }
    /* En el celular, el portafolio va plegado. */
    var pd = document.getElementById('avbPort');
    if (pd && window.matchMedia && window.matchMedia('(max-width: 980px)').matches) pd.open = false;
    /* «Guardar en mi portafolio» del Expediente vivo: la pregunta, la fecha y el enlace de su dictamen; nunca la respuesta. */
    if (exp.guarda) exp.guarda.addEventListener('click', function () {
      if (!ultimo) return;
      var l = leePort().filter(function (x) { return !(x.o === 'auditor' && x.q === ultimo.q); });
      l.unshift({ s: 'revision', o: 'auditor', q: ultimo.q, t: '', dic: ultimo.dic, f: new Date().toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' }) });
      var ok = true;
      try { localStorage.setItem('av-portafolio', JSON.stringify(l.slice(0, 60))); } catch (e) { ok = false; }
      exp.guarda.querySelector('span').textContent = ok ? 'Guardado en tu portafolio' : 'Tu navegador no deja guardar aquí';
      exp.guarda.disabled = true;
      if (lista) port();
    });

    /* Adjuntar XML / CSV · Cero CIEC: el botón de la caja, soltarlos sobre la caja o el XML de muestra. */
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
    /* Un CFDI 4.0 de muestra, ficticio: RFC genéricos de prueba del SAT, sin timbre y con un concepto que lo dice. */
    function xmlMuestra() {
      var d = new Date(), p = function (n) { return (n < 10 ? '0' : '') + n; };
      var f = d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + 'T10:00:00';
      var tr = '<cfdi:Traslados><cfdi:Traslado Base="1000.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="160.00"/></cfdi:Traslados>';
      return '<?xml version="1.0" encoding="UTF-8"?>\n' +
        '<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" Version="4.0" Serie="MUESTRA" Folio="1" Fecha="' + f + '" FormaPago="03" ' +
        'SubTotal="1000.00" Moneda="MXN" Total="1160.00" TipoDeComprobante="I" Exportacion="01" MetodoPago="PUE" LugarExpedicion="26015">\n' +
        '  <cfdi:Emisor Rfc="EKU9003173C9" Nombre="EMISOR DE MUESTRA FICTICIO" RegimenFiscal="601"/>\n' +
        '  <cfdi:Receptor Rfc="XAXX010101000" Nombre="PUBLICO EN GENERAL" DomicilioFiscalReceptor="26015" RegimenFiscalReceptor="616" UsoCFDI="S01"/>\n' +
        '  <cfdi:Conceptos><cfdi:Concepto ClaveProdServ="01010101" Cantidad="1" ClaveUnidad="ACT" Descripcion="Concepto de muestra (factura ficticia, sin timbre)" ' +
        'ValorUnitario="1000.00" Importe="1000.00" ObjetoImp="02"><cfdi:Impuestos>' + tr + '</cfdi:Impuestos></cfdi:Concepto></cfdi:Conceptos>\n' +
        '  <cfdi:Impuestos TotalImpuestosTrasladados="160.00">' + tr + '</cfdi:Impuestos>\n' +
        '</cfdi:Comprobante>\n';
    }
    var mu = document.getElementById('avbMuestra');
    if (mu) mu.addEventListener('click', function () {
      var nombre = 'cfdi-muestra-ficticio.xml', archivo;
      try { archivo = new File([xmlMuestra()], nombre, { type: 'text/xml' }); }
      catch (e) { archivo = new Blob([xmlMuestra()], { type: 'text/xml' }); archivo.name = nombre; }
      recibe([archivo]);
    });

    /* «Cómo funciona (3 pasos)»: solo abre con su botón. */
    var tour = document.getElementById('avbTour'), tBtn = document.getElementById('avbTourBtn'), pasos = [], tp = 0, antes = null;
    try { pasos = JSON.parse(document.getElementById('avbTourDatos').textContent); } catch (e) { pasos = []; }
    var luz = document.getElementById('avbTourLuz'), card = document.getElementById('avbTourCard'), tSig = document.getElementById('avbTourSig'),
      tCie = document.getElementById('avbTourCierra');
    function tourVivo() { return tour && !tour.hidden; }
    function coloca() {
      var p = pasos[tp], el = p && document.getElementById(p.id);
      if (!el) return;
      if (p.id === 'avbMesa' && !mesaVista()) el = mBtn || el;
      var r = el.getBoundingClientRect(), m = 8;
      luz.style.top = (r.top - m) + 'px'; luz.style.left = (r.left - m) + 'px';
      luz.style.width = (r.width + 2 * m) + 'px'; luz.style.height = (r.height + 2 * m) + 'px';
      var cw = card.offsetWidth, ch = card.offsetHeight, vw = document.documentElement.clientWidth, vh = window.innerHeight;
      var top = r.bottom + 16 + ch <= vh ? r.bottom + 16 : (r.top - 16 - ch >= 0 ? r.top - 16 - ch : Math.max(12, vh - ch - 12));
      var left = Math.min(Math.max(12, r.left), vw - cw - 12);
      card.style.top = top + 'px'; card.style.left = Math.max(12, left) + 'px';
    }
    function paso(i) {
      tp = i;
      var p = pasos[i], el = p && document.getElementById(p.id);
      if (!p) return cierraTour();
      if (p.id === 'avbMesa' && !mesaVista()) el = mBtn || el;
      document.getElementById('avbTourN').textContent = 'Paso ' + (i + 1) + ' de ' + pasos.length;
      document.getElementById('avbTourT').textContent = p.t;
      document.getElementById('avbTourX').textContent = p.x;
      tSig.textContent = i === pasos.length - 1 ? 'Terminar' : 'Siguiente';
      if (el) el.scrollIntoView({ behavior: 'auto', block: 'center' });
      coloca();
      tSig.focus();
    }
    function cierraTour() {
      if (!tour) return;
      tour.hidden = true;
      guarda('av-tour-visto', '1');
      window.removeEventListener('resize', coloca);
      window.removeEventListener('scroll', coloca, true);
      if (antes && antes.focus) antes.focus();
    }
    if (tour && tBtn && pasos.length) {
      tBtn.addEventListener('click', function () {
        antes = document.activeElement;
        tour.hidden = false;
        window.addEventListener('resize', coloca);
        window.addEventListener('scroll', coloca, true);
        paso(0);
      });
      tSig.addEventListener('click', function () { if (tp >= pasos.length - 1) cierraTour(); else paso(tp + 1); });
      tCie.addEventListener('click', cierraTour);
      tour.addEventListener('keydown', function (ev) {
        if (ev.key === 'Escape') { ev.preventDefault(); cierraTour(); }
        if (ev.key === 'Tab') { ev.preventDefault(); (document.activeElement === tSig ? tCie : tSig).focus(); }
      });
      /* Ronda 26B: «Cómo funciona» de la barra lateral de otra página trae ?tour=1 (el lector lo pidió con su botón). */
      if (/[?&]tour=1(&|$)/.test(location.search)) {
        try { history.replaceState(null, '', location.pathname + location.search.replace(/([?&])tour=1(&|$)/, function (m, a, b) { return b ? a : ''; }) + location.hash); } catch (e) { /* nada */ }
        setTimeout(function () { tBtn.click(); }, 300);
      }
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', listo); else listo();
})();
