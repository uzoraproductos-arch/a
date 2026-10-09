/* Auditavisión · páginas de apartado (herramientas.html, sigue-el-dinero.html...).
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

  /* Al llegar con #ancla, la cabecera se encoge despues del salto y el
     titulo queda debajo de ella: se corrige una vez ya compacta. */
  /* Pestañas (09-10-2026, Aprende): el contenido de cada sección solo se
     despliega al pulsar su pestaña; pulsarla otra vez la cierra. Sin
     JavaScript, todas las secciones se ven una debajo de otra. El ancla
     (#trivia, #noticias...) abre la pestaña y se puede compartir. */
  var pestanas = document.querySelector('.apartado-pestanas');
  var pestanaAbierta = null;
  function abrirPestana(id, desplazar) {
    if (!pestanas) return;
    pestanaAbierta = id || null;
    Array.prototype.forEach.call(pestanas.querySelectorAll('.apartado-pestana'), function (t) {
      var panel = document.getElementById(t.getAttribute('aria-controls'));
      var on = t.getAttribute('aria-controls') === pestanaAbierta;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      if (panel) panel.hidden = !on;
    });
    var pista = document.getElementById('pestanasPista');
    if (pista) pista.hidden = !!pestanaAbierta;
    if (pestanaAbierta && desplazar) {
      compacta = true;
      document.body.classList.add('cabecera-compacta');
      var alto = nav ? nav.getBoundingClientRect().height : 0;
      var y = pestanas.getBoundingClientRect().top + window.pageYOffset - alto - 8;
      window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
    }
    document.dispatchEvent(new CustomEvent('apartado:pestana', { detail: { id: pestanaAbierta } }));
  }
  if (pestanas) {
    var inicial = decodeURIComponent(location.hash.slice(1));
    abrirPestana(pestanas.querySelector('[aria-controls="' + inicial + '"]') ? inicial : null, false);
    pestanas.addEventListener('click', function (e) {
      var t = e.target.closest('.apartado-pestana');
      if (!t) return;
      e.preventDefault();
      var id = t.getAttribute('aria-controls');
      var cerrar = id === pestanaAbierta;
      abrirPestana(cerrar ? null : id, !cerrar);
      history.replaceState(null, '', cerrar ? location.pathname + location.search : '#' + id);
    });
    pestanas.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      var lista = Array.prototype.slice.call(pestanas.querySelectorAll('.apartado-pestana'));
      var i = lista.indexOf(document.activeElement);
      if (i < 0) return;
      e.preventDefault();
      lista[(i + (e.key === 'ArrowRight' ? 1 : lista.length - 1)) % lista.length].focus();
    });
    window.addEventListener('hashchange', function () {
      var id = decodeURIComponent(location.hash.slice(1));
      if (pestanas.querySelector('[aria-controls="' + id + '"]')) abrirPestana(id, true);
    });
  }

  if (location.hash.length > 1) window.addEventListener('load', function () {
    setTimeout(function () {
      var t = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (!t || !nav) return;
      var y = t.getBoundingClientRect().top + window.pageYOffset - nav.getBoundingClientRect().height - 12;
      window.scrollTo({ top: Math.max(0, y), behavior: 'instant' });
    }, 350);
  });

  /* Visor (08-10-2026): las tarjetas que llevan al auditor ya no sacan al
     lector de esta página. El módulo se despliega aquí mismo, debajo de la
     fila de la tarjeta, en un marco con el auditor en modo visor
     (index.html?ir=...&visor=1: sin cabecera, portada ni pie). Con Ctrl,
     Cmd o la rueda del ratón se abre en otra pestaña, como cualquier enlace. */
  var visor = null, tarjetaAbierta = null;

  function cerrarVisor(devolverFoco) {
    if (!visor) return;
    visor.parentNode.removeChild(visor);
    visor = null;
    if (tarjetaAbierta) {
      tarjetaAbierta.setAttribute('aria-expanded', 'false');
      tarjetaAbierta.classList.remove('apartado-tarjeta-abierta');
      if (devolverFoco) tarjetaAbierta.focus({ preventScroll: false });
    }
    tarjetaAbierta = null;
  }

  function ultimaDeSuFila(t) {
    var rejilla = t.parentNode, fila = t;
    var arriba = t.offsetTop;
    Array.prototype.forEach.call(rejilla.querySelectorAll('.apartado-tarjeta'), function (o) {
      if (o.offsetTop === arriba) fila = o;
    });
    return fila;
  }

  function abrirVisor(t) {
    var href = t.getAttribute('href');
    var nombre = (t.querySelector('.apartado-tarjeta-nombre') || t).textContent.trim();
    cerrarVisor(false);
    tarjetaAbierta = t;
    t.setAttribute('aria-expanded', 'true');
    t.classList.add('apartado-tarjeta-abierta');

    visor = document.createElement('div');
    visor.className = 'apartado-visor';
    visor.setAttribute('role', 'region');
    visor.setAttribute('aria-label', nombre);
    var c = getComputedStyle(t).getPropertyValue('--tarjeta');
    if (c) visor.style.setProperty('--tarjeta', c.trim());
    visor.innerHTML =
      '<div class="apartado-visor-cab">' +
        '<span class="apartado-visor-tit" tabindex="-1"></span>' +
        '<a class="apartado-visor-b" href="' + href + '" title="Abre el módulo en la vista completa del auditor">⤢ Pantalla completa</a>' +
        '<button type="button" class="apartado-visor-b apartado-visor-cerrar">✕ Cerrar</button>' +
      '</div>' +
      '<div class="apartado-visor-cuerpo">' +
        '<p class="apartado-visor-carga" role="status">⏳ Cargando el módulo con sus cifras y fuentes…</p>' +
        '<iframe class="apartado-visor-marco" loading="eager"></iframe>' +
      '</div>';
    visor.querySelector('.apartado-visor-tit').textContent = (t.querySelector('.apartado-tarjeta-icono') ? t.querySelector('.apartado-tarjeta-icono').textContent + ' ' : '') + nombre;
    var marco = visor.querySelector('iframe');
    marco.title = nombre;
    marco.addEventListener('load', function () { if (visor) visor.classList.add('cargado'); });
    marco.src = href.replace(/&amp;/g, '&') + '&visor=1';
    visor.querySelector('.apartado-visor-cerrar').addEventListener('click', function () { cerrarVisor(true); });

    var tras = ultimaDeSuFila(t);
    tras.parentNode.insertBefore(visor, tras.nextSibling);

    /* La cabecera se encoge al bajar: se mide ya compacta para que no tape
       el visor. */
    compacta = true;
    document.body.classList.add('cabecera-compacta');
    var alto = nav ? nav.getBoundingClientRect().height : 0;
    visor.style.setProperty('--visor-alto', 'calc(100vh - ' + Math.round(alto + 24) + 'px)');
    var y = visor.getBoundingClientRect().top + window.pageYOffset - alto - 8;
    window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
    setTimeout(function () {
      var tit = visor && visor.querySelector('.apartado-visor-tit');
      if (tit) tit.focus({ preventScroll: true });
    }, 450);
  }

  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('a.apartado-tarjeta');
    if (!t) return;
    var href = t.getAttribute('href') || '';
    if (href.indexOf('index.html?ir=') !== 0) return;
    if (e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    if (tarjetaAbierta === t) cerrarVisor(true); else abrirVisor(t);
  });

  /* El auditor, en el visor, pide cerrarlo con postMessage. */
  window.addEventListener('message', function (e) {
    if (e.origin !== window.location.origin || !e.data || e.data.auditavision !== 'cerrar-visor') return;
    cerrarVisor(true);
  });
})();
