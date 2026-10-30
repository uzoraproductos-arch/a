/* El candado de la versión de prueba (pedido del autor, 29-10-2026). Va en el
   <head> de todas las páginas, antes de pintar. Si el candado está puesto y
   este navegador no trae un pase vigente, manda a canjea-tu-codigo.html.
   La configuración la escribe herramientas/acceso.py entre sus marcas: no la
   edites a mano. Las páginas del canje y del panel usan acceso-paginas.js. */
(function () {
  var C = /*config*/{"candado":true,"funciones":"https://nuqiyzcilbrrlezmesnf.supabase.co/functions/v1","supabase":"https://nuqiyzcilbrrlezmesnf.supabase.co","anon":"sb_publishable_gf28FUrT1zcoaGl4C2f_aQ_exkzAQ9g","canje":"canjea-tu-codigo.html","panel":"administracion-codigos.html","libres":["canjea-tu-codigo.html","administracion-codigos.html","aviso-de-privacidad.html"]}/*fin-config*/;
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
  var yo = leer();
  if (yo && yo.admin && vigente(yo)) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', pestana); else pestana();
  }

  if (!C.candado || !C.funciones) return;
  // En la copia local (python3 -m http.server y las pruebas de revision.py)
  // no se pide código.
  if (/^(localhost|127\.0\.0\.1)$/.test(location.hostname)) return;
  var pagina = location.pathname.split('/').pop() || 'index.html';
  if (C.libres.indexOf(pagina) >= 0) return;
  // Dentro del marco del chat manda la página de arriba.
  try { if (window.top !== window && window.top.AvAcceso) return; } catch (e) {}

  var p = leer();
  if (!vigente(p)) {
    location.replace(C.canje + '?volver=' + encodeURIComponent(pagina + location.search + location.hash));
    return;
  }
  // Con pase vigente se entra de inmediato; de vez en cuando se confirma con
  // la base, por si el código se revocó.
  if (!p.visto || Date.now() - p.visto > DIA) {
    pide({ accion: 'consultar', pase: p.pase }).then(function (j) {
      if (!j || !j.ok) return;
      p.hasta = j.hasta; p.visto = Date.now(); guardar(p);
      if (!vigente(p)) location.replace(C.canje + '?volver=' + encodeURIComponent(pagina));
    }).catch(function () {});
  }
})();
