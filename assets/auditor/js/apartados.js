/* Auditavisión · páginas de apartado (herramientas.html, busca-y-verifica.html...).
   Lo poco que necesitan sin cargar el motor: el menú de tres rayas en
   pantallas angostas y el botón para compartir la página. */
(function () {
  'use strict';
  var nav = document.querySelector('.site-top-nav');
  var btn = document.getElementById('navHamburguesa');
  function menu(abrir) {
    if (!nav || !btn) return;
    nav.classList.toggle('nav-abierta', abrir);
    document.body.classList.toggle('menu-movil-abierto', abrir);
    btn.setAttribute('aria-expanded', abrir ? 'true' : 'false');
    btn.setAttribute('aria-label', abrir ? 'Cerrar el menú' : 'Abrir el menú');
    var txt = btn.querySelector('.nav-hamb-txt');
    if (txt) txt.textContent = abrir ? 'Cerrar' : 'Menú';
  }
  if (btn) btn.addEventListener('click', function () { menu(!nav.classList.contains('nav-abierta')); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') menu(false); });

  var compartir = document.getElementById('apartadoCompartir');
  if (compartir) compartir.addEventListener('click', function () {
    var url = window.location.href.split('#')[0];
    if (navigator.share) {
      navigator.share({ title: document.title, url: url }).catch(function () {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(function () {
        alert('Enlace copiado. Ya lo puedes pegar donde quieras compartirlo.');
      }).catch(function () { prompt('Copia este enlace para compartirlo:', url); });
    } else {
      prompt('Copia este enlace para compartirlo:', url);
    }
  });

  /* Cabecera alta arriba, compacta al desplazarse (igual que en el auditor). */
  var compacta = false;
  function revisar() {
    var y = window.pageYOffset || 0;
    var nueva = compacta ? y > 10 : y > 120;
    if (nueva !== compacta) {
      compacta = nueva;
      document.body.classList.toggle('cabecera-compacta', compacta);
    }
  }
  window.addEventListener('scroll', revisar, { passive: true });
  revisar();
})();
