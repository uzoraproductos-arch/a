/* La billetera de tokens (Ronda 27A, 26-11-2026, decisión del autor: «cero fricción»). Va en el <head> de todas las
   páginas, después de acceso.js. Quien llega por primera vez recibe la bienvenida de la tabla del Precio Fundador
   (monetizacion.PRECIO_FUNDADOR, que herramientas/monetizacion.py escribe entre las marcas «tokens» y «fin-tokens»: no la edites a
   mano) y cada acción gasta lo que dice esa tabla, la misma que leen servicios.html y la Mesa de Trabajo.

   - Vive solo en este navegador (localStorage av-tokens): el saldo, los últimos movimientos, las huellas de lo ya
     pagado (para no cobrar dos veces la misma pregunta o el mismo dictamen; nunca la pregunta escrita) y los códigos
     canjeados. Es una medida de uso, no una cuenta: en la Ronda 27B el saldo se sincroniza con una cuenta por correo,
     y AvTokens no cambia de forma.
   - La administración (código maestro, sesión aal2 o su marca) y un código con tokens ilimitados no gastan nada.
   - La lectura abierta (Planisferio, Noticiero, Auditorías en imágenes, Biblioteca, el XML de muestra y abrir una
     página desde el Auditor) nunca pasa por aquí.
   - Sin saldo, avisa con tres salidas («Solicitar código para más tokens», «Tengo un código de recarga» y «Ver Planes y
     Precio Fundador») y no borra lo que el lector escribió. Sin emojis: íconos SVG de trazo. */
(function () {
  'use strict';
  if (window.AvTokens) return;
  var T = /*tokens*/{"bienvenida":35,"renueva":"mes","costo":{"pregunta":2,"dictamen":10,"inspector":17,"servicio":17,"semaforo":17,"lote":17},"nombre":{"pregunta":"Pregunta al Auditor en modo Ciudadano, Periodista o Ambientalista","dictamen":"Ficha o dictamen sellado con huella SHA-256","inspector":"Pregunta en el Modo Inspector · Pro","servicio":"Revisión de un servicio avanzado en el Inspector de Servicios","semaforo":"Semáforo Patrimonial completo","lote":"Lote XML / CSV · Cero CIEC, con tus archivos"},"gratis":["Probar el XML de muestra","El Planisferio","El Noticiero","Las Auditorías en imágenes","La Biblioteca","Abrir una página de la plataforma desde el Auditor"],"canje":"canjea-tu-codigo.html","planes":"servicios.html#precio-fundador"}/*fin-tokens*/;
  var CLAVE = 'av-tokens', MOVS = 30, PAGOS = 150;

  function ahora() { return Date.now(); }
  function lee() {
    var b = null;
    try { b = JSON.parse(localStorage.getItem(CLAVE) || 'null'); } catch (e) { b = null; }
    if (!b || typeof b.s !== 'number' || !isFinite(b.s)) return null;
    b.h = Array.isArray(b.h) ? b.h : []; b.p = b.p && typeof b.p === 'object' ? b.p : {}; b.k = Array.isArray(b.k) ? b.k : [];
    return b;
  }
  var memoria = null;  // si el navegador no deja guardar, la billetera vive mientras dure la página
  function guarda(b) {
    memoria = b;
    try { localStorage.setItem(CLAVE, JSON.stringify(b)); return true; } catch (e) { return false; }
  }
  /* Ronda 28B: los tokens gratis se renuevan cada mes calendario. Quien tiene menos vuelve a la bienvenida; a quien tiene
     más (canjeó un código) nunca se le resta. b.m es el mes de la última renovación (AAAA-MM, hora del navegador). */
  function mes(t) { var d = new Date(t || ahora()); return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2); }
  function renueva(b) {
    if (T.renueva !== 'mes') return b;
    if (!b.m) b.m = mes(b.d);
    if (b.m === mes()) return b;
    b.m = mes();
    if (b.s < T.bienvenida) {
      b.h.unshift({ f: ahora(), n: T.bienvenida - b.s, c: 'renovacion' });
      if (b.h.length > MOVS) b.h.length = MOVS;
      b.s = T.bienvenida;
    }
    guarda(b);
    return b;
  }
  function billetera() {
    var b = lee() || memoria;
    if (b) return renueva(b);
    b = { v: 1, s: T.bienvenida, d: ahora(), m: mes(), h: [{ f: ahora(), n: T.bienvenida, c: 'bienvenida' }], p: {}, k: [] };
    guarda(b);
    return b;
  }
  function apunta(b, n, c) {
    b.h.unshift({ f: ahora(), n: n, c: c });
    if (b.h.length > MOVS) b.h.length = MOVS;
  }

  function admin() {
    var A = window.AvAcceso;
    if (!A) return false;
    if (A.admin) return true;
    try {
      if (A.sesionAdmin && A.sesionAdmin()) return true;
      return +localStorage.getItem('av-admin-hasta') > ahora();
    } catch (e) { return false; }
  }
  function ilimitado() {
    if (admin()) return true;
    var b = billetera();
    return !!(b.ilim && Date.parse(b.ilim) > ahora());
  }
  function costo(c) { return T.costo[c] || 0; }
  /* La huella de lo pagado: la acción y un número sacado de la pregunta o del enlace (FNV-1a). La pregunta no se guarda. */
  function huella(c, q) {
    var t = String(q || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/\s+/g, ' ').trim();
    var h = 2166136261;
    for (var i = 0; i < t.length; i++) { h ^= t.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
    return c + ':' + h.toString(36);
  }
  function avisa() {
    pinta();
    try { document.dispatchEvent(new CustomEvent('av-tokens', { detail: { saldo: saldo(), ilimitado: ilimitado() } })); } catch (e) { /* nada */ }
  }
  function saldo() { return billetera().s; }

  /* Cobra una acción. Devuelve true si se puede seguir (pagada ahora, ya pagada antes, ilimitada o libre).
     o.libre: no se cobra (abrir una página desde el Auditor). o.sinAviso: no abre el aviso al faltar saldo. */
  function cobra(c, q, o) {
    o = o || {};
    var n = costo(c);
    if (!n || o.libre || ilimitado()) return true;
    var b = billetera(), k = q != null && q !== '' ? huella(c, q) : null;
    if (k && b.p[k]) return true;
    if (b.s < n) { if (!o.sinAviso) aviso(c); return false; }
    b.s -= n;
    apunta(b, -n, c);
    if (k) {
      b.p[k] = ahora();
      var ks = Object.keys(b.p);
      if (ks.length > PAGOS) ks.sort(function (x, y) { return b.p[x] - b.p[y]; }).slice(0, ks.length - PAGOS).forEach(function (x) { delete b.p[x]; });
    }
    guarda(b);
    avisa();
    return true;
  }
  /* Devuelve lo cobrado por una pregunta que el Auditor no supo contestar. */
  function devuelve(c, q) {
    if (ilimitado()) return;
    var b = billetera(), k = huella(c, q);
    if (!b.p[k]) return;
    delete b.p[k];
    b.s += costo(c);
    apunta(b, costo(c), 'devolucion');
    guarda(b);
    avisa();
  }
  /* Suma los tokens de un código canjeado (una sola vez por código en este navegador). */
  function suma(n, origen, id) {
    var b = billetera();
    if (id != null && b.k.indexOf(String(id)) >= 0) return false;
    n = Math.max(0, Math.floor(+n || 0));
    if (!n) return false;
    b.s += n;
    apunta(b, n, origen || 'codigo');
    if (id != null) { b.k.push(String(id)); if (b.k.length > 200) b.k.shift(); }
    guarda(b);
    avisa();
    return true;
  }
  /* Un código de tokens ilimitados: abre sin gastar hasta su vigencia (nunca acorta una más larga). */
  function ilimitadoHasta(iso, id) {
    var b = billetera(), f = Date.parse(iso);
    if (!f || f <= ahora()) return false;
    if (id != null && b.k.indexOf(String(id)) < 0) { b.k.push(String(id)); if (b.k.length > 200) b.k.shift(); }
    if (!b.ilim || Date.parse(b.ilim) < f) b.ilim = new Date(f).toISOString();
    apunta(b, 0, 'ilimitado');
    guarda(b);
    avisa();
    return true;
  }

  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"]/g, function (x) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[x]; }); }
  function svg(d, t) {
    return '<svg class="avb-i" width="' + (t || 18) + '" height="' + (t || 18) + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' + d + '</svg>';
  }
  var MONEDA = '<circle cx="12" cy="12" r="8"/><path d="M12 8v8M9.5 10.2c0-1 1.1-1.7 2.5-1.7s2.5.7 2.5 1.7-1.1 1.5-2.5 1.8-2.5.8-2.5 1.8 1.1 1.7 2.5 1.7 2.5-.7 2.5-1.7"/>';
  var LLAVE = '<circle cx="8" cy="15" r="4"/><path d="m10.8 12.2 9.2-9.2"/><path d="m17 6 3 3"/><path d="m14.5 8.5 2 2"/>';
  function aqui() { return (location.pathname.split('/').pop() || 'index.html') + location.search; }
  function volver() { var v = aqui(); return /^[\w.-]+\.html([?#][^\s]*)?$/.test(v) ? v : 'herramienta-inspector-pregunta.html'; }
  function tokens(n) { return n + ' token' + (n === 1 ? '' : 's'); }

  /* El saldo en la barra lateral (#avbAcceso) y en cualquier [data-av-saldo]. La administración conserva su tarjeta ∞. */
  function pinta() {
    if (!document.body) return;
    var il = ilimitado(), s = saldo();
    Array.prototype.forEach.call(document.querySelectorAll('[data-av-saldo]'), function (el) {
      el.textContent = il ? 'sin límite' : tokens(s);
    });
    var caja = document.getElementById('avbAcceso');
    if (!caja || admin()) return;
    var A = window.AvAcceso, p = A && A.leer && A.leer(), pase = p && A.vigente && A.vigente(p) && !p.admin;
    var b = billetera();
    caja.className = 'avb-acceso avb-billetera' + (il ? ' avb-ilimitado' : s < costo('pregunta') ? ' avb-sin-saldo' : '');
    caja.innerHTML = '<p class="avb-saldo">' + svg(MONEDA, 20) + '<span><b>' + (il ? 'Tokens ilimitados' : esc(tokens(s))) + '</b>' +
      '<small>' + (il ? 'hasta el ' + esc(new Date(b.ilim).toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' })) : 'disponibles') + '</small></span></p>' +
      '<a class="avb-ingresa" href="' + esc(T.canje) + '?volver=' + encodeURIComponent(volver()) + '">' + svg(LLAVE) + ' Canjear / Solicitar código</a>' +
      (pase ? '<small class="avb-vence">Tu código abre los Servicios hasta el ' + esc(new Date(p.hasta).toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' })) + '.</small>' : '');
  }

  /* El aviso cuando no alcanza: cuánto pide la acción, cuánto queda, lo que sigue gratis y las tres salidas. */
  var dlg = null;
  function aviso(c) {
    try { if (window.top !== window && window.top.AvTokens && window.top.document.body) { window.top.AvTokens.aviso(c); return; } } catch (e) { /* otro origen */ }
    if (!document.body) return;
    var n = costo(c), s = saldo(), v = encodeURIComponent(volver());
    if (!dlg) {
      dlg = document.createElement('dialog');
      dlg.className = 'av-tk-aviso';
      dlg.setAttribute('aria-labelledby', 'avTkTit');
      document.body.appendChild(dlg);
      dlg.addEventListener('click', function (ev) { if (ev.target === dlg || ev.target.closest('[data-av-tk-cierra]')) dlg.close(); });
    }
    dlg.innerHTML = '<div class="av-tk-caja">' +
      '<p class="av-tk-ico">' + svg(MONEDA, 28) + '</p>' +
      '<h2 id="avTkTit">Te faltan tokens para esto</h2>' +
      '<p>' + esc(T.nombre[c] || 'Esta acción') + ' usa <b>' + esc(tokens(n)) + '</b> y te ' + (s === 1 ? 'queda' : 'quedan') + ' <b>' + esc(tokens(s)) + '</b>. ' +
      'Lo que escribiste sigue en su lugar.</p>' +
      '<p class="av-tk-gratis">Siguen gratis: el Planisferio, el Noticiero, las Auditorías en imágenes, la Biblioteca y el XML de muestra.</p>' +
      '<p class="av-tk-acc">' +
      '<a class="av-tk-btn av-tk-pri" href="' + esc(T.canje) + '?pedir=1&volver=' + v + '">Solicitar código para más tokens</a>' +
      '<a class="av-tk-btn" href="' + esc(T.canje) + '?volver=' + v + '">Tengo un código de recarga</a>' +
      '<a class="av-tk-btn" href="' + esc(T.planes) + '">Ver Planes y Precio Fundador</a></p>' +
      '<p class="av-tk-pie"><button type="button" class="av-tk-cierra" data-av-tk-cierra>Seguir sin gastar</button></p></div>';
    if (dlg.showModal) { if (!dlg.open) dlg.showModal(); } else dlg.setAttribute('open', '');
    var f = dlg.querySelector('.av-tk-pri'); if (f) f.focus();
  }

  /* El dictamen (o la ficha): se cobra al tocar su enlace, una vez por enlace. Abrir un dictamen que te compartieron no
     gasta: el documento es público y vuelve a contestar con la base. */
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a[href*="herramienta-inspector-dictamen.html"]') : null;
    if (!a || ev.defaultPrevented) return;
    if (!cobra('dictamen', a.getAttribute('href'))) { ev.preventDefault(); ev.stopPropagation(); }
  }, true);

  window.addEventListener('storage', function (ev) { if (ev.key === CLAVE) avisa(); });
  window.AvTokens = { tabla: T, saldo: saldo, costo: costo, ilimitado: ilimitado, admin: admin, cobra: cobra, devuelve: devuelve,
    suma: suma, ilimitadoHasta: ilimitadoHasta, aviso: aviso, pinta: pinta, movimientos: function () { return billetera().h.slice(); } };
  billetera();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', avisa); else avisa();
})();
