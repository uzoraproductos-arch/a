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
    /* Compacta, solo vuelve a crecer arriba del todo: la cabecera va en el
       flujo y al encogerse el navegador sube la página lo mismo que se
       encogió (anclaje del desplazamiento); con un umbral mayor que cero
       eso la hacía crecer y encogerse sin parar. */
    var nueva = compacta ? y > 0 : y > 120;
    if (nueva !== compacta) {
      compacta = nueva;
      document.body.classList.toggle('cabecera-compacta', compacta);
    }
  }
  window.addEventListener('scroll', revisar, { passive: true });
  /* Encoge la cabecera sin animación y devuelve su alto ya compacta, para
     calcular bien a dónde desplazarse. */
  function compactar() {
    compacta = true;
    if (!nav) { document.body.classList.add('cabecera-compacta'); return 0; }
    var antes = nav.style.transition;
    nav.style.transition = 'none';
    document.body.classList.add('cabecera-compacta');
    var alto = nav.getBoundingClientRect().height;
    void nav.offsetHeight;
    nav.style.transition = antes;
    return alto;
  }
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
    Array.prototype.forEach.call(pestanas.querySelectorAll('.apartado-pestana[aria-controls]'), function (t) {
      var panel = document.getElementById(t.getAttribute('aria-controls'));
      var on = t.getAttribute('aria-controls') === pestanaAbierta;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      if (panel) panel.hidden = !on;
    });
    var pista = document.getElementById('pestanasPista');
    if (pista) pista.hidden = !!pestanaAbierta;
    if (pestanaAbierta && desplazar) {
      var alto = compactar();
      var y = pestanas.getBoundingClientRect().top + window.pageYOffset - alto - 8;
      window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
    }
    document.dispatchEvent(new CustomEvent('apartado:pestana', { detail: { id: pestanaAbierta } }));
  }
  if (pestanas) {
    var inicial = decodeURIComponent(location.hash.slice(1));
    /* En las páginas de herramienta (data-primera) la primera pestaña ya
       llega abierta. */
    if (!pestanas.querySelector('[aria-controls="' + inicial + '"]')) {
      var primera = pestanas.getAttribute('data-primera') && pestanas.querySelector('.apartado-pestana');
      inicial = primera ? primera.getAttribute('aria-controls') : null;
    }
    abrirPestana(inicial, false);
    pestanas.addEventListener('click', function (e) {
      var t = e.target.closest('.apartado-pestana');
      /* Las pestañas sin panel (el Ágora) son enlaces a su página. */
      if (!t || !t.hasAttribute('aria-controls')) return;
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

  function abrirVisor(t, quieto) {
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
    var alto = compactar();
    visor.style.setProperty('--visor-alto', 'calc(100vh - ' + Math.round(alto + 24) + 'px)');
    if (quieto) return;
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

  /* Páginas de herramienta: la tarjeta de la pestaña (data-auto) despliega
     su visor sola al abrir la pestaña; el lector no tiene que pulsar dos
     veces. Cerrarlo deja la tarjeta para volver a abrirlo. */
  function visorDePestana(id) {
    var panel = id && document.getElementById(id);
    var t = panel && panel.querySelector('a.apartado-tarjeta[data-auto]');
    if (t && tarjetaAbierta !== t) abrirVisor(t, true);
  }
  document.addEventListener('apartado:pestana', function (e) { visorDePestana(e.detail && e.detail.id); });
  visorDePestana(pestanaAbierta);

  /* ?abrir=eb-bloque (10-10-2026): el auditor manda aquí lo que antes abría
     en el módulo «Circuito del Dinero», que ahora es la pestaña Números. Se
     abre la pestaña de la tarjeta que lleva ese bloque y su visor. */
  (function () {
    var abrir = new URLSearchParams(location.search).get('abrir');
    if (!abrir || !/^[A-Za-z0-9_-]+$/.test(abrir)) return;
    var re = new RegExp('[?&]ancla=' + abrir + '(&|$)');
    var t = Array.prototype.filter.call(document.querySelectorAll('a.apartado-tarjeta'), function (x) { return re.test(x.getAttribute('href') || ''); })[0];
    if (!t) return;
    var panel = t.closest('.apartado-panel');
    if (panel) abrirPestana(panel.id, false);
    history.replaceState(null, '', location.pathname + (panel ? '#' + panel.id : ''));
    if (tarjetaAbierta !== t) abrirVisor(t);
  })();

  /* El auditor, en el visor, pide cerrarlo con postMessage. */
  window.addEventListener('message', function (e) {
    if (e.origin !== window.location.origin || !e.data || e.data.auditavision !== 'cerrar-visor') return;
    cerrarVisor(true);
  });

  /* Páginas de módulo (10-10-2026): cada módulo de una herramienta tiene su
     página (herramienta-*-*.html) y el auditor se carga aquí en modo visor,
     con la altura de su contenido. Cerrarlo desde dentro vuelve al índice
     de la herramienta (el segundo enlace de las migas). */
  Array.prototype.forEach.call(document.querySelectorAll('iframe[data-modulo]'), function (marco) {
    var caja = marco.closest('.apartado-visor');
    marco.addEventListener('load', function () {
      if (caja) caja.classList.add('cargado');
      ajustarMarco(marco);
    });
    marco.src = marco.getAttribute('data-modulo');
    window.addEventListener('message', function (e) {
      if (e.origin !== window.location.origin || !e.data || e.data.auditavision !== 'cerrar-visor') return;
      var migas = document.querySelectorAll('.apartado-migas a');
      window.location.href = migas.length ? migas[migas.length - 1].getAttribute('href') : 'herramientas.html';
    });
  });
  /* Ventana lateral de estas páginas (decisión del autor, 09-10-2026): el
     logotipo abre la presentación «Quiénes somos» y el enlace «Qué son las
     finanzas públicas» abre su nota, más ancha, sin salir de la página.
     Son el mismo texto que abrirPresentacion() y abrirNotaPortada() del
     motor, que estas páginas no cargan: si cambia uno, cambia el otro. */
  var logo = document.getElementById('apartadoPresentacion');
  var cajOv = null, cajDr = null, cajOrigen = null;
  function chip(e) { return '<span class="est-chip est-' + e + '">' + e + '</span>'; }
  function sec(tit, h) { return '<section class="glos-drawer-sec"><h4>' + tit + '</h4>' + h + '</section>'; }
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function cerrarCajon() {
    if (!cajDr || !cajDr.classList.contains('abierto')) return;
    cajDr.classList.remove('abierto');
    cajOv.classList.remove('abierto');
    document.body.classList.remove('glos-drawer-bloqueo');
    if (cajOrigen && cajOrigen.focus) { try { cajOrigen.focus({ preventScroll: true }); } catch (err) { /* sin foco */ } }
  }
  /* Pinta html en la ventana y la abre. ancha: la nota de finanzas. */
  function cajon(html, titulo, ancha) {
    if (!cajDr) {
      cajOv = document.createElement('div');
      cajOv.className = 'glos-drawer-overlay';
      cajOv.addEventListener('click', cerrarCajon);
      cajDr = document.createElement('aside');
      cajDr.setAttribute('role', 'dialog');
      cajDr.setAttribute('aria-modal', 'true');
      document.body.appendChild(cajOv);
      document.body.appendChild(cajDr);
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape') cerrarCajon(); });
    }
    if (!cajDr.classList.contains('abierto')) cajOrigen = document.activeElement;
    cajDr.className = 'glos-drawer' + (ancha ? ' glos-drawer-ancha' : '');
    cajDr.setAttribute('aria-labelledby', titulo);
    cajDr.innerHTML = html;
    cajDr.querySelector('.glos-drawer-x').addEventListener('click', cerrarCajon);
    menu(false);
    cajOv.classList.add('abierto');
    /* Un cuadro antes de abrir, para que se vea deslizar. */
    void cajDr.offsetWidth;
    cajDr.classList.add('abierto');
    document.body.classList.add('glos-drawer-bloqueo');
    cajDr.querySelector('.glos-drawer-cuerpo').scrollTop = 0;
    var x = cajDr.querySelector('.glos-drawer-x');
    setTimeout(function () { x.focus(); }, 30);
    return cajDr;
  }
  function cabCajon(ico, marca, cerrar) {
    return '<header class="glos-drawer-cab">' +
      '<span class="glos-drawer-marca"><span aria-hidden="true">' + ico + '</span> ' + marca + '</span>' +
      '<button type="button" class="glos-drawer-x" aria-label="' + cerrar + '">✕</button>' +
    '</header>';
  }

  function abrirPresentacion() {
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
    var dr = cajon(
      cabCajon('👋', 'Quiénes somos', 'Cerrar la presentación') +
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
        '<button type="button" class="glos-drawer-todo glos-drawer-todo-2" data-finanzas="1">📖 Qué son las finanzas públicas ➔</button>' +
      '</footer>', 'presTitulo', false);
    dr.querySelector('[data-finanzas]').addEventListener('click', abrirFinanzas);
  }
  if (logo) logo.addEventListener('click', abrirPresentacion);

  /* «Qué son las finanzas públicas y qué encontrarás aquí». Las cifras se
     leen de la base (audit-database.js), que se carga al pedir la nota en
     las páginas que no la traen. */
  var baseCargando = false;
  function conBase(fn) {
    if (window.AUDIT_DB) { fn(window.AUDIT_DB); return; }
    if (baseCargando) return;
    baseCargando = true;
    var propio = document.querySelector('script[src*="apartados.js"]');
    var v = propio && propio.getAttribute('src').split('?')[1];
    var s = document.createElement('script');
    s.src = 'assets/auditor/js/audit-database.js' + (v ? '?' + v : '');
    s.onload = function () { baseCargando = false; if (window.AUDIT_DB) fn(window.AUDIT_DB); else s.onerror(); };
    s.onerror = function () {
      baseCargando = false;
      var c = cajDr && cajDr.querySelector('.glos-drawer-cuerpo');
      if (c) c.innerHTML = '<p>No se pudo cargar la base de datos de la plataforma. Revisa tu conexión y vuelve a intentarlo.</p>';
    };
    document.head.appendChild(s);
  }
  function billones(mdp) {
    return '$' + (mdp / 1e6).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' billones';
  }
  function fuente(txt) { return ' <span class="fin-fuente">(' + txt + ')</span>'; }
  function abrirFinanzas(e) {
    if (e && e.preventDefault) e.preventDefault();
    cajon(cabCajon('📖', 'Qué significa', 'Cerrar la nota') +
      '<div class="glos-drawer-cuerpo"><h3 id="finTitulo" class="glos-drawer-tit">Las finanzas públicas</h3>' +
      '<p role="status">⏳ Cargando las cifras con sus fuentes…</p></div>', 'finTitulo', true);
    conBase(pintarFinanzas);
  }
  function pintarFinanzas(DB) {
    var P = DB.panoramaErario || {};
    var fed = (P.federalizado && P.federalizado.totalMdp) || 0;
    var cf = ((P.egresos || []).filter(function (x) { return x.id === 'egr-costofin'; })[0] || {}).montoMdp || 0;
    var cp = DB.cuenta_publica_asf && DB.cuenta_publica_asf.cp2024 ? DB.cuenta_publica_asf.cp2024 : null;
    var mdp = function (v) { return '$' + Number(v).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' millones'; };
    var lugares = [
      ['⚖️', 'Números', 'sigue-el-dinero.html', 'de dónde sale cada peso (Ley de Ingresos), en qué se gasta (Presupuesto de Egresos), cómo llega a estados y municipios y cuánto se debe.'],
      ['🏗️', 'Inversión y Megaobras', 'herramienta-megaobras.html', 'cuánto costaron las grandes obras y cuánto cuesta mantenerlas.'],
      ['💳', 'Calculadora Cívica', 'herramienta-calculadora.html', 'lo que pagas de impuestos según tu ingreso y a qué rubros equivale.'],
      ['🔍', 'Modo Inspector', 'herramienta-inspector.html', 'lo que la Auditoría Superior revisó y lo que quedó por aclarar.'],
      ['🌎', 'Costo Ambiental', 'herramienta-ambiente.html', 'lo que el deterioro del ambiente cuesta y lo que se destina a protegerlo.'],
      ['📊', 'Datos', 'descarga-los-datos.html', 'las bases para descargar, el radar hacendario y los informes oficiales.']
    ];
    var dr = cajon(cabCajon('📖', 'Qué significa', 'Cerrar la nota') +
      '<div class="glos-drawer-cuerpo">' +
        '<span class="glos-drawer-cat">⚖️ Fiscalización ciudadana del gasto público</span>' +
        '<h3 id="finTitulo" class="glos-drawer-tit">Las finanzas públicas</h3>' +
        sec('Qué son', '<p>Todo lo que hace el Estado con el dinero público: <b>cómo lo obtiene</b> (impuestos, derechos, ventas de sus empresas y deuda), <b>en qué decide gastarlo</b> (el presupuesto), <b>cómo lo reparte</b> entre la Federación, los estados y los municipios, y <b>cómo rinde cuentas</b> de lo que gastó (la Cuenta Pública y sus auditorías).</p>') +
        sec('Por qué importan', '<p>Cada año el Congreso aprueba cuánto se cobra y en qué se gasta.</p>' +
          '<ul class="rc-plazos fin-cifras">' +
            '<li>' + chip('oficial') + ' En 2026 el Presupuesto de Egresos es de <b>' + billones(P.totalPEF || 0) + '</b>.' + fuente('PEF 2026, DOF') + '</li>' +
            '<li>' + chip('oficial') + ' De ellos, <b>' + billones(fed) + '</b> viajan a los 32 estados y a sus municipios.' + fuente('PEF 2026, Anexo 1') + '</li>' +
            '<li>' + chip('oficial') + ' Y <b>' + billones(cf) + '</b> pagan el costo de la deuda.' + fuente('PEF 2026, Anexo 8') + '</li>' +
            (cp && cp.total ? '<li>' + chip('oficial') + ' Al revisar la Cuenta Pública 2024, la Auditoría Superior dejó <b>' + mdp(cp.total.porAclarar / 1e6) + '</b> por aclarar.' + fuente('ASF, Matriz de Datos Básicos de la Cuenta Pública 2024, p. ' + esc(cp.pagina) + ', corte ' + esc(cp.corte)) + '</li>' : '') +
          '</ul>' +
          '<p>Entender ese recorrido es el primer paso para pedir cuentas con datos.</p>') +
        sec('Qué encontrarás aquí', '<ul class="rc-plazos fin-lugares">' + lugares.map(function (m) {
          return '<li>' + m[0] + ' <a href="' + m[2] + '"><b>' + m[1] + '</b></a>: ' + m[3] + '</li>';
        }).join('') + '</ul>' +
          '<p class="rc-nota">Para el marco legal completo, los conceptos y las fuentes de cada tema está el Diccionario del Gasto Público.</p>') +
        sec('Cómo leer las cifras', '<ul class="rc-plazos">' +
          '<li>' + chip('oficial') + ' tomada tal cual de su documento (DOF, SHCP, ASF, INEGI, Banxico…).</li>' +
          '<li>' + chip('derivado') + ' calculada a partir de datos oficiales; la operación se dice.</li>' +
          '<li>' + chip('pendiente') + ' la dependencia responsable no la ha transparentado en un documento oficial, y te decimos cuál.</li>' +
        '</ul>') +
        sec('Fundamento', '<p class="glos-drawer-ley">Constitución Política, art. 31 fr. IV (la obligación de contribuir al gasto público), art. 74 fr. IV y VI (la Cámara de Diputados aprueba el presupuesto y revisa la Cuenta Pública) y art. 134 (los recursos públicos se administran con eficiencia, eficacia, economía, transparencia y honradez).</p>') +
      '</div>' +
      '<footer class="glos-drawer-pie">' +
        '<button type="button" class="glos-drawer-todo" data-g="Gasto Público">📗 Qué es el gasto público ➔</button>' +
        '<button type="button" class="glos-drawer-todo glos-drawer-todo-2" data-g="Hacienda Pública">📗 Qué es la hacienda pública ➔</button>' +
        '<a class="glos-drawer-todo glos-drawer-todo-2" href="diccionario.html" style="text-align:center; text-decoration:none;">📚 Abrir el Diccionario del Gasto Público ➔</a>' +
      '</footer>', 'finTitulo', true);
    Array.prototype.forEach.call(dr.querySelectorAll('[data-g]'), function (b) {
      b.addEventListener('click', function () { pintarTermino(DB, b.getAttribute('data-g')); });
    });
  }
  /* Un término del glosario, en la misma ventana, con regreso a la nota. */
  function norm(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/\s+/g, ' ').trim(); }
  function pintarTermino(DB, termino) {
    var q = norm(termino);
    var g = (DB.glosario || []).filter(function (x) { return norm(x.termino) === q; })[0];
    if (!g) return;
    var ancla = norm(g.termino.split(' (')[0]).replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    var dr = cajon(cabCajon('📗', 'Glosario', 'Cerrar el glosario') +
      '<div class="glos-drawer-cuerpo">' +
        (g.categoria ? '<span class="glos-drawer-cat">' + esc(g.categoria) + '</span>' : '') +
        '<h3 id="glosTermTitulo" class="glos-drawer-tit">' + esc(g.termino) + '</h3>' +
        sec('Qué significa', '<p>' + g.definicion + '</p>') +
        (g.ley ? sec('Fundamento', '<p class="glos-drawer-ley">' + esc(g.ley) + '</p>') : '') +
      '</div>' +
      '<footer class="glos-drawer-pie">' +
        '<button type="button" class="glos-drawer-todo" data-volver="1">← Volver a la nota</button>' +
        '<a class="glos-drawer-todo glos-drawer-todo-2" href="glosario.html#' + ancla + '" style="text-align:center; text-decoration:none;">📖 Ver todo el glosario ➔</a>' +
      '</footer>', 'glosTermTitulo', true);
    dr.querySelector('[data-volver]').addEventListener('click', function () { pintarFinanzas(DB); });
  }
  /* La nota de referencia del libro (Números) se abre en la ventana
     lateral con el contenido de su plantilla. */
  var tplLibro = document.getElementById('tplNotaLibro');
  Array.prototype.forEach.call(document.querySelectorAll('a.apartado-nota[data-libro]'), function (a) {
    a.addEventListener('click', function (e) {
      if (!tplLibro || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      cajon(tplLibro.innerHTML, 'notaLibroTit', true);
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll('a.apartado-nota[href="index.html?ir=nota"]'), function (a) {
    a.addEventListener('click', function (e) {
      if (e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
      abrirFinanzas(e);
    });
  });

  /* Nada saca al lector a la portada (decisión del autor, 09-10-2026):
     solo el nombre «Auditavisión» y los botones de volver al inicio llevan
     a index.html. Un enlace que todavía apunta a un módulo de la portada
     (index.html?ir=...) se abre en la ventana lateral, ancha, con el
     auditor en modo visor; los términos del glosario van a su página. */
  function abrirMarco(href, nombre) {
    var url = String(href).replace(/&amp;/g, '&');
    var g = url.match(/^index\.html\?ir=(?:faq-)?glosario(?:&ancla=([A-Za-z0-9_-]+))?/);
    if (g) { window.location.href = 'glosario.html' + (g[1] ? '#' + g[1] : ''); return; }
    var dr = cajon(cabCajon('🔎', esc(nombre || 'Auditavisión'), 'Cerrar la ventana') +
      '<div class="glos-drawer-cuerpo">' +
        '<p class="apartado-visor-carga" role="status">⏳ Cargando el módulo con sus cifras y fuentes…</p>' +
        '<iframe class="glos-drawer-iframe" title="' + esc(nombre || 'Módulo del auditor') + '"></iframe>' +
      '</div>', '', true);
    dr.classList.add('glos-drawer-marco');
    dr.removeAttribute('aria-labelledby');
    dr.setAttribute('aria-label', nombre || 'Módulo del auditor');
    var marco = dr.querySelector('iframe');
    marco.addEventListener('load', function () { dr.classList.add('cargado'); });
    marco.src = url + (url.indexOf('?') === -1 ? '?' : '&') + 'visor=1';
  }
  window.Apartados = { abrirMarco: abrirMarco };
  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest && e.target.closest('a[href^="index.html?ir="]');
    if (!a || a.classList.contains('apartado-tarjeta')) return;
    e.preventDefault();
    abrirMarco(a.getAttribute('href'), (a.textContent || '').replace(/[➔↗]/g, '').replace(/\s+/g, ' ').trim());
  });
  /* El auditor, dentro de la ventana, pide cerrarla con postMessage. */
  window.addEventListener('message', function (e) {
    if (e.origin !== window.location.origin || !e.data || e.data.auditavision !== 'cerrar-visor') return;
    if (cajDr && cajDr.classList.contains('glos-drawer-marco')) cerrarCajon();
  });
  /* Toda etiqueta «pendiente» lleva al Registro de pendientes (10-10-2026):
     ahi esta por que falta el dato, quien debe publicarlo y el enlace
     oficial donde deberia estar. Se escucha en la fase de captura para que
     ninguna tarjeta que la contenga se la lleve. */
  document.addEventListener('click', function (ev) {
    var c = ev.target && ev.target.closest ? ev.target.closest('.est-chip.est-pendiente') : null;
    if (!c || /pendientes\.html$/.test(window.location.pathname)) return;
    ev.preventDefault();
    ev.stopPropagation();
    var destino = 'pendientes.html' + (c.getAttribute('data-pend') ? '#' + c.getAttribute('data-pend') : '');
    try { (window.top || window).location.href = destino; } catch (e) { window.location.href = destino; }
  }, true);
  document.addEventListener('mouseover', function (ev) {
    var c = ev.target && ev.target.closest ? ev.target.closest('.est-chip.est-pendiente') : null;
    if (c && !c.title) c.title = 'Por qué falta este dato, quién debe publicarlo y dónde debería estar: abre el Registro de pendientes';
  });
})();
