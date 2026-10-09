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

  /* El marco toma la altura de su contenido (09-10-2026): la ficha se lee
     como parte de la pagina, sin barra de desplazamiento propia ni franja
     en blanco. Es el mismo origen, asi que se puede medir; si el contenido
     cambia (un bloque que se abre, una grafica que se dibuja) se vuelve a
     medir. Si no se puede medir, se queda con la altura de la ventana. */
  function ajustarMarco(marco) {
    var doc;
    try { doc = marco.contentDocument; } catch (err) { return; }
    if (!doc || !doc.body) return;
    /* Se mide el fondo del contenido visible y no el alto del documento,
       que nunca baja del alto del marco. Los cajones fijos (fixed) miden
       lo que el marco y se ignoran. Si el contenido crece al mismo
       ritmo que el marco (algo medido en vh), se deja de ajustar. */
    var cambios = 0, ro = null;
    function medir() {
      if (!marco.isConnected) { if (ro) ro.disconnect(); return; }
      var win = marco.contentWindow, fondo = 0;
      Array.prototype.forEach.call(doc.body.children, function (el) {
        var r = el.getBoundingClientRect();
        if (r.height > 0 && win && win.getComputedStyle(el).position !== 'fixed') fondo = Math.max(fondo, r.bottom + (win ? win.pageYOffset : 0));
      });
      var h = Math.ceil(fondo) + 16;
      if (h < 240 || Math.abs(h - marco.offsetHeight) < 8) return;
      if (++cambios > 40) { if (ro) ro.disconnect(); return; }
      marco.style.minHeight = '240px';
      marco.style.height = h + 'px';
    }
    medir();
    if (window.ResizeObserver) {
      /* El body nunca baja del alto del marco: se observa cada bloque para
         notar también cuando el contenido se encoge. */
      ro = new ResizeObserver(medir);
      ro.observe(doc.body);
      Array.prototype.forEach.call(doc.body.children, function (el) {
        if (marco.contentWindow.getComputedStyle(el).position !== 'fixed') ro.observe(el);
      });
    }
    [300, 1200, 2800].forEach(function (ms) { setTimeout(medir, ms); });
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
    marco.addEventListener('load', function () {
      if (visor) visor.classList.add('cargado');
      ajustarMarco(marco);
    });
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
  /* El logotipo abre la presentación «Quiénes somos» en la ventana lateral,
     sin salir de la página (decisión del autor, 09-10-2026). Es el mismo
     texto que abrirPresentacion() del motor, que estas páginas no cargan:
     si cambia uno, cambia el otro. */
  var logo = document.getElementById('apartadoPresentacion');
  var presOv = null, presDr = null, presOrigen = null;
  function chip(e) { return '<span class="est-chip est-' + e + '">' + e + '</span>'; }
  function sec(tit, h) { return '<section class="glos-drawer-sec"><h4>' + tit + '</h4>' + h + '</section>'; }
  function cerrarPresentacion() {
    if (!presDr || !presDr.classList.contains('abierto')) return;
    presDr.classList.remove('abierto');
    presOv.classList.remove('abierto');
    document.body.classList.remove('glos-drawer-bloqueo');
    if (presOrigen && presOrigen.focus) { try { presOrigen.focus({ preventScroll: true }); } catch (err) { /* sin foco */ } }
  }
  function abrirPresentacion() {
    if (!presDr) {
      presOv = document.createElement('div');
      presOv.className = 'glos-drawer-overlay';
      presOv.addEventListener('click', cerrarPresentacion);
      presDr = document.createElement('aside');
      presDr.className = 'glos-drawer';
      presDr.setAttribute('role', 'dialog');
      presDr.setAttribute('aria-modal', 'true');
      presDr.setAttribute('aria-labelledby', 'presTitulo');
      var palabras = [
        ['Audita', 'de <i>auditar</i>: revisar con método que lo que se gastó corresponda a lo que se autorizó y a lo que se comprobó.'],
        ['visión', 'mirar el conjunto, de la Federación a los estados y municipios, y hacerlo visible para quien no lee informes técnicos.'],
        ['Sistema', 'no son notas sueltas: ingresos, egresos, transferencias, deuda y Cuenta Pública son piezas conectadas que se leen juntas.'],
        ['Cívico', 'lo construye y lo usa la ciudadanía. No es una autoridad ni sustituye a la Auditoría Superior de la Federación ni a las contralorías.'],
        ['Fiscalización', 'la revisión del uso de los recursos públicos. La oficial la hacen la ASF (art. 79 constitucional) y las entidades de fiscalización de los estados (art. 116, fr. II); la ciudadana la complementa: consulta, compara, pregunta y denuncia.']
      ];
      var principios = [
        ['Fuente antes que opinión', 'cada cifra se rastrea a su documento oficial: DOF, SHCP, ASF, INEGI, Banxico, Gaceta Parlamentaria.'],
        ['Honestidad del dato', 'cada cifra dice si es ' + chip('oficial') + ', ' + chip('derivado') + ' o ' + chip('pendiente') + '.'],
        ['Método a la vista', 'si una cifra se calcula, se dice la operación para que cualquiera la repita.'],
        ['Claridad con rigor', 'se explica en lenguaje llano, sin simplificar lo que la ley dice.'],
        ['Memoria', 'las normas y estructuras derogadas se marcan con su vigencia en lugar de borrarse.']
      ];
      var compromisos = [
        'No inventar ni redondear a ojo: lo que no se puede verificar se queda como <b>pendiente</b>.',
        'Poner el documento a tu alcance para que lo verifiques por tu cuenta.',
        'Corregir a la vista cuando se encuentre un error. El sello de versión al pie de la página dice qué copia está leyendo.',
        'Orientar hacia los canales oficiales de denuncia, sin suplantar a ninguna autoridad.'
      ];
      presDr.innerHTML =
        '<header class="glos-drawer-cab">' +
          '<span class="glos-drawer-marca"><span aria-hidden="true">👋</span> Quiénes somos</span>' +
          '<button type="button" class="glos-drawer-x" aria-label="Cerrar la presentación">✕</button>' +
        '</header>' +
        '<div class="glos-drawer-cuerpo">' +
          '<img class="pres-logo" src="assets/auditor/img/logo-auditavision.svg" alt="" width="200" height="156">' +
          '<span class="glos-drawer-cat">Presentación</span>' +
          '<h3 id="presTitulo" class="glos-drawer-tit">Auditavisión, Sistema Cívico de Fiscalización</h3>' +
          '<p class="pres-lema">Una plataforma ciudadana que explica, con los documentos oficiales en la mano, de dónde sale el dinero público, en qué se gasta y qué encontró quien lo revisó.</p>' +
          sec('El nombre, palabra por palabra', '<dl class="pres-palabras">' + palabras.map(function (w) { return '<dt>' + w[0] + '</dt><dd>' + w[1] + '</dd>'; }).join('') + '</dl>') +
          sec('Propósito', '<p>Que cualquier persona pueda seguir el rastro de un peso público, desde que se cobra hasta que se gasta y se audita, y convertir una duda en una pregunta bien hecha: una solicitud de información, una denuncia o un voto informado.</p>') +
          sec('Principios', '<ol class="pres-lista">' + principios.map(function (x) { return '<li><b>' + x[0] + ':</b> ' + x[1] + '</li>'; }).join('') + '</ol>') +
          sec('Compromisos', '<ul class="rc-plazos">' + compromisos.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>') +
          sec('Fundamento', '<p class="glos-drawer-ley">Constitución Política, art. 6º, apartado A (derecho de acceso a la información pública), art. 8º (derecho de petición), art. 79 (fiscalización superior de la Federación) y art. 134 (los recursos públicos se administran con eficiencia, eficacia, economía, transparencia y honradez).</p>') +
        '</div>' +
        '<footer class="glos-drawer-pie">' +
          '<a class="glos-drawer-todo" href="index.html" style="text-align:center; text-decoration:none;">⚡ Ir a la página principal ➔</a>' +
        '</footer>';
      presDr.querySelector('.glos-drawer-x').addEventListener('click', cerrarPresentacion);
      document.body.appendChild(presOv);
      document.body.appendChild(presDr);
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape') cerrarPresentacion(); });
    }
    presOrigen = document.activeElement;
    menu(false);
    presOv.classList.add('abierto');
    presDr.classList.add('abierto');
    document.body.classList.add('glos-drawer-bloqueo');
    presDr.querySelector('.glos-drawer-cuerpo').scrollTop = 0;
    var x = presDr.querySelector('.glos-drawer-x');
    setTimeout(function () { x.focus(); }, 30);
  }
  if (logo) logo.addEventListener('click', abrirPresentacion);
})();
