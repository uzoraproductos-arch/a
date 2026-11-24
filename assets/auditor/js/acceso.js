/* El candado de la versión de prueba (pedido del autor, 29-10-2026). Va en el
   <head> de todas las páginas, antes de pintar. Si el candado está puesto y
   este navegador no trae un pase vigente, manda a canjea-tu-codigo.html.
   La configuración la escribe herramientas/acceso.py entre sus marcas: no la
   edites a mano. Las páginas del canje y del panel usan acceso-paginas.js. */
(function () {
  var C = /*config*/{"candado":true,"funciones":"https://nuqiyzcilbrrlezmesnf.supabase.co/functions/v1","supabase":"https://nuqiyzcilbrrlezmesnf.supabase.co","anon":"sb_publishable_gf28FUrT1zcoaGl4C2f_aQ_exkzAQ9g","canje":"canjea-tu-codigo.html","panel":"administracion-codigos.html","libres":["canjea-tu-codigo.html","administracion-codigos.html","aviso-de-privacidad.html","derecho-de-replica.html","servicios.html","servicios-por-que.html","servicios-fraude-y-lavado.html","servicios-catalogo.html","servicios-tu-perfil.html","servicios-empieza-gratis.html","servicios-como-se-cobra.html","servicios-calendario.html","servicios-preguntas.html","servicios-cotiza.html"],"privadas":["enciclopedia-auditavision.html","sigue-el-dinero.html","descarga-los-datos.html","aprende.html"],"fuera":"planisferio.html"}/*fin-config*/;
  var CLAVE = 'av-pase';
  var DIA = 12 * 3600 * 1000;  // cada cuánto se vuelve a preguntar a la base (por si se revocó)

  function leer() {
    try { var p = JSON.parse(localStorage.getItem(CLAVE) || 'null'); return p && p.pase ? p : null; } catch (e) { return null; }
  }
  function guardar(p) {
    try { if (p) localStorage.setItem(CLAVE, JSON.stringify(p)); else localStorage.removeItem(CLAVE); } catch (e) {}
  }
  function vigente(p) { return !!(p && p.hasta && Date.parse(p.hasta) > Date.now()); }
  function pide(cuerpo) {
    return fetch(C.funciones + '/codigo', {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'apikey': C.anon, 'Authorization': 'Bearer ' + C.anon },
      body: JSON.stringify(cuerpo)
    }).then(function (r) { return r.json(); });
  }
  window.AvAcceso = { config: C, leer: leer, guardar: guardar, vigente: vigente, pide: pide };

  // La pestaña «Administración» (pedido del autor, 30-10-2026): solo aparece
  // en el navegador de la administración: el que entró a su panel (con el
  // correo o con el código maestro) o con su código de la semana. El público
  // no la ve, y el panel sigue pidiendo sesión de administración para abrir.
  // El panel la pone en cuanto la administración entra, sin recargar.
  function pestana() {
    var barra = document.querySelector('.site-top-nav .nav-center-links');
    if (!barra || barra.querySelector('.nav-menu-admin')) return;
    var aqui = (location.pathname.split('/').pop() || '') === C.panel;
    var d = document.createElement('div');
    d.className = 'nav-menu-item nav-menu-pagina nav-menu-admin';
    d.innerHTML = '<a class="mega-menu-trigger" href="' + C.panel + '" title="Tus códigos, las solicitudes y tu código de la semana"' +
      (aqui ? ' aria-current="page"' : '') + '>Administración</a>';
    barra.insertBefore(d, barra.querySelector('.nav-menu-cuentanos'));
  }
  window.AvAcceso.pestana = pestana;
  // La sesión de la administración de esta pestaña (Ronda 16, 24-11-2026): el autor
  // entró con su código maestro y las pestañas lo regresaban al panel cuando el pase
  // de la semana no se activaba. Con la sesión de dos factores (aal2) ya hecha en
  // esta pestaña se entra igual que con el pase; el panel sigue pidiendo la sesión.
  function sesionAdmin() {
    try {
      var s = JSON.parse(sessionStorage.getItem('av-admin') || 'null');
      if (!s || !s.token || !s.refresh) return false;
      var b = s.token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      return JSON.parse(atob(b + '==='.slice((b.length + 3) % 4))).aal === 'aal2';
    } catch (e) { return false; }
  }
  window.AvAcceso.sesionAdmin = sesionAdmin;
  // Ronda 17 (24-11-2026): la sesión de dos factores vive en una sola pestaña y el autor
  // seguía rebotando al panel. El panel deja además en este navegador una marca de 12 h
  // (av-admin-hasta) al confirmar la sesión aal2; «Salir» la borra. Solo abre el candado:
  // los datos los sigue cuidando es_admin() en la base.
  var MARCA = 'av-admin-hasta';
  function marcaAdmin() {
    try { return +localStorage.getItem(MARCA) > Date.now(); } catch (e) { return false; }
  }
  window.AvAcceso.marcaAdmin = function (si) {
    try { if (si) localStorage.setItem(MARCA, String(Date.now() + 12 * 3600 * 1000)); else localStorage.removeItem(MARCA); } catch (e) {}
  };
  var yo = leer();
  var admin = (yo && yo.admin && vigente(yo)) || sesionAdmin() || marcaAdmin();
  if (admin) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', pestana); else pestana();
  }

  // La medición de uso (pedido del autor, 18-11-2026: «el tiempo que ha
  // consumido los usuarios, qué tema les ha interesado… dónde le da clic»).
  // Solo para mejorar la plataforma: la página, el tiempo con la pestaña a la
  // vista y el texto y destino de lo que se toca. Nunca lo que se escribe, la
  // IP ni nada que diga quién eres. No mide en la copia local, en el navegador
  // de la administración, con «No rastrear» o el control global de privacidad,
  // ni si lo apagas en el aviso de privacidad (av-sin-medir).
  var SIN = 'av-sin-medir';
  function sinMedir() { try { return localStorage.getItem(SIN) === '1'; } catch (e) { return false; } }
  window.AvAcceso.medir = function (si) {
    try { if (si) localStorage.removeItem(SIN); else localStorage.setItem(SIN, '1'); } catch (e) {}
  };
  window.AvAcceso.midiendo = function () { return !sinMedir() && !navigator.globalPrivacyControl && navigator.doNotTrack !== '1'; };
  window.AvUso = { marca: function () {} };
  // El botón del aviso de privacidad: «No medir este navegador» / «Volver a medir».
  function botonMedir() {
    document.querySelectorAll('[data-av-medir]').forEach(function (b) {
      var est = b.parentNode.querySelector('[data-av-medir-estado]');
      function pinta() {
        var gpc = navigator.globalPrivacyControl || navigator.doNotTrack === '1';
        b.textContent = sinMedir() ? 'Volver a medir este navegador' : 'No medir este navegador';
        b.disabled = !!gpc;
        if (est) est.textContent = gpc ? 'Tu navegador ya pide no ser medido: no se mide.' : sinMedir() ? 'Este navegador no se mide.' : 'Este navegador se mide, como se explica arriba.';
      }
      b.addEventListener('click', function () { window.AvAcceso.medir(sinMedir()); pinta(); });
      pinta();
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', botonMedir); else botonMedir();
  (function () {
    var pag = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
    var enMarco = false; try { enMarco = window.top !== window; } catch (e) { enMarco = true; }
    if (!C.funciones || enMarco || /^(localhost|127\.0\.0\.1)$/.test(location.hostname) || !/^[a-z0-9._-]{1,120}\.html$/.test(pag)) return;
    if (!window.AvAcceso.midiendo() || admin) return;
    var ses; try { ses = sessionStorage.getItem('av-sesion'); } catch (e) {}
    if (!ses) { ses = (Date.now().toString(36) + Math.random().toString(36).slice(2, 10)).slice(0, 20); try { sessionStorage.setItem('av-sesion', ses); } catch (e) {} }
    var cola = [], visible = 0, desde = document.visibilityState === 'visible' ? Date.now() : 0;
    function manda() {
      if (!cola.length) return;
      var p = leer(), cuerpo = JSON.stringify({ accion: 'uso', pase: p && p.pase, sesion: ses, eventos: cola.splice(0, 40) });
      // Texto plano y sin cabeceras: el navegador lo manda aunque la página se cierre.
      var ok = false;
      try { ok = navigator.sendBeacon && navigator.sendBeacon(C.funciones + '/codigo', new Blob([cuerpo], { type: 'text/plain' })); } catch (e) {}
      if (!ok) { try { fetch(C.funciones + '/codigo', { method: 'POST', body: cuerpo, keepalive: true }).catch(function () {}); } catch (e) {} }
      if (cola.length) manda();
    }
    function marca(tipo, x) {
      if (sinMedir()) return;
      x = x || {}; x.tipo = tipo; x.pagina = pag; cola.push(x);
      if (cola.length >= 20) manda();
    }
    function corte() {
      if (desde) { visible += Date.now() - desde; desde = 0; }
      var s = Math.round(visible / 1000); visible = 0;
      if (s >= 2) marca('tiempo', { segundos: Math.min(s, 7200) });
    }
    window.AvUso.marca = marca;
    marca('vista');
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'visible') desde = Date.now();
      else { corte(); manda(); }
    });
    window.addEventListener('pagehide', function () { corte(); manda(); });
    // Lo que se toca: ligas, botones, pestañas y desplegables. De las ligas,
    // la página de destino (de otro sitio, solo su dominio); de lo demás, su
    // texto. Nada de lo que se escribe en un campo.
    document.addEventListener('click', function (e) {
      var t = e.target && e.target.closest && e.target.closest('a[href], button, summary, [role="tab"]');
      if (!t || t.closest('[data-sin-medir]')) return;
      var dest = '', h = t.getAttribute('href');
      if (h && t.tagName === 'A') {
        try {
          var u = new URL(h, location.href);
          if (/^(mailto|tel):/.test(u.protocol)) dest = u.protocol.slice(0, -1);
          else dest = u.origin === location.origin ? (u.pathname.split('/').pop() || 'index.html') + (u.hash || '').slice(0, 40) : 'externo: ' + u.hostname;
        } catch (e2) { return; }
      } else dest = '[' + (t.getAttribute('data-vista') || t.getAttribute('aria-controls') || t.id || t.tagName.toLowerCase()) + ']';
      // Una pregunta que escribió la persona (la lista de «Lo que aún no sé», su burbuja) no se lee.
      var et = t.closest('[data-pa-ya], .pa-reintenta, .pa-yo') ? '(su pregunta)' : (t.getAttribute('aria-label') || t.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 80);
      marca('clic', { destino: dest.slice(0, 160), etiqueta: et });
    }, true);
    setInterval(manda, 30000);
  })();

  // Las portadas de la antigua Enciclopedia (Ronda 7, 22-11-2026): solo en el navegador
  // de la administración; a quien llega por una liga vieja, al Planisferio.
  var pagina = location.pathname.split('/').pop() || 'index.html';
  // Ronda 18 (24-11-2026): el enlace del correo trae la sesión en la dirección
  // (#access_token=…). Si Supabase lo manda a otra página (la portada o la entrada),
  // el candado lo perdía al redirigir y el autor quedaba en «Canjea tu código».
  // Se lleva al panel tal cual, antes que cualquier otra regla.
  if (pagina !== C.panel && /(^#|&)(access_token|error_description)=/.test(location.hash)) {
    location.replace(C.panel + location.hash);
    return;
  }
  if ((C.privadas || []).indexOf(pagina) >= 0 && !admin &&
      !/^(localhost|127\.0\.0\.1)$/.test(location.hostname)) {
    /* Una liga vieja con ?abrir= o #ancla: la página la manda primero a su página propia;
       si no la conoce, al Planisferio. */
    if (/[?&]abrir=/.test(location.search) || location.hash) document.addEventListener('DOMContentLoaded', function () { location.replace(C.fuera); });
    else location.replace(C.fuera);
    return;
  }
  if (!C.candado || !C.funciones) return;
  // En la copia local (python3 -m http.server y las pruebas de revision.py)
  // no se pide código.
  if (/^(localhost|127\.0\.0\.1)$/.test(location.hostname)) return;
  if (C.libres.indexOf(pagina) >= 0) return;
  // Dentro del marco del chat manda la página de arriba.
  try { if (window.top !== window && window.top.AvAcceso) return; } catch (e) {}

  // Sin pase vigente, a la entrada. Pero si en esta pestaña ya entraste al panel
  // (sesión de la administración, Ronda 13), al panel: ahí se activa tu pase de la
  // semana y te regresa a donde ibas, en vez de pedirte el código otra vez.
  function fuera(adonde) {
    var ses = null; try { ses = sessionStorage.getItem('av-admin'); } catch (e) {}
    location.replace((ses ? C.panel : C.canje) + '?volver=' + encodeURIComponent(adonde));
  }
  if (admin) return;
  var p = leer();
  if (!vigente(p)) {
    fuera(pagina + location.search + location.hash);
    return;
  }
  // Con pase vigente se entra de inmediato; de vez en cuando se confirma con
  // la base, por si el código se revocó.
  if (!p.visto || Date.now() - p.visto > DIA) {
    pide({ accion: 'consultar', pase: p.pase }).then(function (j) {
      if (!j || !j.ok) return;
      p.hasta = j.hasta; p.visto = Date.now(); guardar(p);
      if (!vigente(p)) fuera(pagina);
    }).catch(function () {});
  }
})();
