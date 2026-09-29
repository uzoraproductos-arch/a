/* ==========================================================================
   AUDITAVISIÓN · NAVEGACIÓN Y LECTURA (fase 1 de docs/ux/PLAN.md)

   1. Una sola lista de destinos (SECCIONES) para la barra de escritorio, el
      menú del celular y las puertas de la portada.
   2. Ruta de migas al abrir un módulo: «Inicio › Lee › Megaobras».
   3. Rótulos sin emojis (DESIGN.md §7): títulos, botones, enlaces y pestañas
      que pinta el motor pierden el emoji decorativo al aparecer en pantalla.
      Es una capa de transición: cuando cada módulo pase a su plantilla
      (fase 2), el emoji se quita en la fuente y esta limpieza deja de hacer
      falta.

   Los textos de navegación están escritos para que los entienda cualquier
   persona, sin jerga (explicado «como a alguien de diez años»). Los nombres
   de sección son propuesta: docs/ux/fase-0-propuestas.md §3.
   ========================================================================== */
(function () {
  'use strict';

  // m = módulo del motor; a = ancla dentro del módulo; accion = caso especial.
  // enPortada = cuántos destinos muestra la puerta en la portada.
  var SECCIONES = [
    {
      id: 'lee', nombre: 'Lee', que: 'Historias que explican a dónde va el dinero.', enPortada: 4,
      destinos: [
        { t: 'El presupuesto 2026, explicado', m: 'presupuesto' },
        { t: 'Megaobras: cuánto costaron', m: 'megaobras' },
        { t: 'El plan de gastos para 2027', m: 'proyeccion2027' },
        { t: 'Cuánto cuestan el Congreso y los jueces', m: 'poderes' },
        { t: 'Cuánto recibe cada secretaría', m: 'presupuesto', a: 'eb-egresos' },
        { t: 'Lo que nos cuesta dañar el ambiente', m: 'ambiente' }
      ]
    },
    {
      id: 'explora', nombre: 'Explora', que: 'Pon tus datos y haz tus propias cuentas.', enPortada: 4,
      destinos: [
        { t: '¿A dónde van tus impuestos?', m: 'calculadora' },
        { t: '¿Es cierta la cifra de una noticia?', m: 'verificador', a: 'vnSeccion' },
        { t: 'Historias en imágenes', accion: 'imagenes' },
        { t: 'El reloj del dinero público', accion: 'reloj' }
      ]
    },
    {
      id: 'consulta', nombre: 'Consulta', que: 'Busca datos oficiales y descárgalos.', enPortada: 4,
      destinos: [
        { t: 'Qué encontró la Auditoría en 2024', m: 'verificador', a: 'cuentaPublicaASF' },
        { t: 'Busca tu municipio', m: 'municipios' },
        { t: 'Busca tu estado', m: 'territorio' },
        { t: '¿Tu proveedor está en la lista negra del SAT?', accion: 'efos' },
        { t: 'Estados con más dinero sin aclarar', m: 'verificador', a: 'radarBanderasNacional' },
        { t: 'Casos que revisó la Auditoría', m: 'verificador', a: 'expedientesCasos' },
        { t: 'Descarga los datos', accion: 'descargas' },
        { t: 'Qué significa cada columna de los datos', accion: 'diccionario' },
        { t: 'Palabras difíciles, explicadas', accion: 'glosario' },
        { t: 'Preguntas frecuentes', accion: 'preguntas' },
        { t: 'Las leyes que ordenan el gasto', accion: 'leyes' },
        { t: 'De dónde salen los datos', accion: 'fuentes' }
      ]
    },
    {
      id: 'participa', nombre: 'Participa', que: 'Cuenta lo que viste y aprende dónde denunciar.', enPortada: 0,
      destinos: [
        { t: 'Cuéntanos lo que viste', accion: 'ayudanos' },
        { t: 'Opina con otras personas', m: 'portal' },
        { t: 'Dónde denunciar', m: 'portal', a: 'bloqueCanales' },
        { t: '10 reglas para revisar el gasto', m: 'portal', a: 'decalogoWrap' },
        { t: 'Guías para revisar el gasto', accion: 'guias' },
        { t: 'Qué pasa con lo que escribes aquí', m: 'portal', a: 'comOrientacion' }
      ]
    }
  ];

  function motor() { return window.AuditEngine || {}; }
  function llamar(fn) {
    var args = Array.prototype.slice.call(arguments, 1);
    var f = motor()[fn];
    if (typeof f === 'function') return f.apply(null, args);
  }

  // Claves candidatas del módulo abierto: la subpestaña activa, la pestaña
  // activa y lo que el motor dejó en la dirección (#pestaña/subpestaña).
  function clavesAbiertas() {
    var claves = [];
    var activo = document.querySelector('.tab-panel.active');
    if (activo) {
      var sub = activo.querySelector('.subtab-panel.active[data-subpanel]');
      if (sub) claves.push(sub.getAttribute('data-subpanel'));
      claves.push(activo.id.replace('tab-panel-', ''));
    }
    return claves.concat((location.hash || '').replace('#', '').split('/').reverse());
  }

  function moduloAbierto() {
    var d = document.getElementById('seccionDesgloseModulos');
    return !!(d && d.classList.contains('desglose-abierto'));
  }
  function volverAPortada() {
    if (moduloAbierto()) llamar('plegarDesgloseModulos');
  }
  function llevarA(el) {
    if (el) setTimeout(function () { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 80);
  }

  var ACCIONES = {
    imagenes: function () { volverAPortada(); llevarA(document.querySelector('.civic-showcase-section')); },
    reloj: function () {
      volverAPortada();
      document.body.classList.add('ver-reloj');
      llevarA(document.getElementById('radarAlertaBar'));
    },
    efos: function () { llamar('efosAbrir'); },
    descargas: function () { llamar('abrirDescargas'); },
    diccionario: function () { llamar('abrirDescargas', 'diccionario'); },
    glosario: function () { llamar('abrirDiccionarioSubtab', 'faq-glosario'); },
    preguntas: function () { llamar('abrirDiccionarioSubtab', 'faq-preguntas'); },
    leyes: function () { llamar('abrirDiccionarioSubtab', 'faq-marco-legal'); },
    fuentes: function () { llamar('abrirCatalogoFuentes'); },
    guias: function () { llamar('openPaseCivicoModal'); },
    ayudanos: function () { llamar('openAyudanosFiscalizar'); }
  };

  var ultimoDestino = null;
  function ir(destino, seccion) {
    cerrarMenu();
    cerrarPanel();
    ultimoDestino = { d: destino, s: seccion };
    if (destino.accion) {
      if (ACCIONES[destino.accion]) ACCIONES[destino.accion]();
    } else {
      llamar('seleccionarModuloExplorer', destino.m, destino.a);
    }
    setTimeout(pintarMigas, 120);
    setTimeout(alAbrirModulo, 200);
  }

  function boton(texto, clase, alPulsar) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = clase;
    b.textContent = texto;
    b.addEventListener('click', alPulsar);
    return b;
  }

  function lista(s, destinos) {
    var ul = document.createElement('ul');
    ul.className = 'puerta-lista';
    destinos.forEach(function (d) {
      var li = document.createElement('li');
      li.appendChild(boton(d.t, 'puerta-ir', function () { ir(d, s); }));
      ul.appendChild(li);
    });
    return ul;
  }

  // ---- Portada ------------------------------------------------------------
  function pintarPortada() {
    var cont = document.getElementById('portadaPuertas');
    if (!cont) return;
    SECCIONES.forEach(function (s) {
      if (!s.enPortada) return;
      var li = document.createElement('li');
      li.className = 'puerta';
      li.id = 'puerta-' + s.id;
      var h = document.createElement('h2');
      h.className = 'puerta-nombre';
      h.textContent = s.nombre;
      var p = document.createElement('p');
      p.className = 'puerta-que';
      p.textContent = s.que;
      li.appendChild(h);
      li.appendChild(p);
      var ul = lista(s, s.destinos.slice(0, s.enPortada));
      if (s.destinos.length > s.enPortada) {
        var mas = document.createElement('li');
        mas.appendChild(boton('Ver todo lo de ' + s.nombre + ' (' + s.destinos.length + ')', 'puerta-ir puerta-ir-mas',
          function () { abrirSeccion(s.id); }));
        ul.appendChild(mas);
      }
      li.appendChild(ul);
      cont.appendChild(li);
    });
  }

  // ---- Barra de escritorio: cuatro secciones con su lista desplegable -------
  var panel, panelAbierto = null;

  function pintarNav() {
    var cont = document.getElementById('navSecciones');
    if (!cont) return;
    panel = document.createElement('div');
    panel.className = 'nav-panel';
    panel.id = 'navPanel';
    panel.hidden = true;
    SECCIONES.forEach(function (s) {
      var b = boton(s.nombre, 'nav-seccion', function () {
        if (panelAbierto === s.id) cerrarPanel(); else abrirPanel(s.id);
      });
      b.id = 'navSeccion-' + s.id;
      b.setAttribute('aria-expanded', 'false');
      b.setAttribute('aria-controls', 'navPanel');
      cont.appendChild(b);
    });
    document.querySelector('.site-top-nav').appendChild(panel);
    document.addEventListener('click', function (e) {
      if (panelAbierto && !e.target.closest('#navPanel') && !e.target.closest('.nav-seccion')) cerrarPanel();
    });
  }

  function abrirPanel(id) {
    var s = SECCIONES.filter(function (x) { return x.id === id; })[0];
    if (!s || !panel) return;
    panel.innerHTML = '';
    var cab = document.createElement('p');
    cab.className = 'nav-panel-que';
    cab.textContent = s.que;
    panel.appendChild(cab);
    panel.appendChild(lista(s, s.destinos));
    panel.hidden = false;
    panelAbierto = id;
    document.querySelectorAll('.nav-seccion').forEach(function (b) {
      var activo = b.id === 'navSeccion-' + id;
      b.setAttribute('aria-expanded', activo ? 'true' : 'false');
      b.classList.toggle('activa', activo);
    });
    var primero = panel.querySelector('.puerta-ir');
    if (primero) primero.focus();
  }

  function cerrarPanel() {
    if (!panel || panel.hidden) return;
    panel.hidden = true;
    panelAbierto = null;
    document.querySelectorAll('.nav-seccion').forEach(function (b) {
      b.setAttribute('aria-expanded', 'false');
      b.classList.remove('activa');
    });
  }

  // En escritorio abre la lista de la barra; en celular, el menú en esa sección.
  function abrirSeccion(id) {
    if (window.matchMedia('(max-width: 900px)').matches) abrirMenu(id);
    else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      abrirPanel(id);
    }
  }

  // ---- Menú del celular -----------------------------------------------------
  var menu, botonMenu, ultimoFoco;

  function pintarMenu() {
    menu = document.getElementById('menuMovil');
    botonMenu = document.getElementById('menuMovilBtn');
    if (!menu || !botonMenu) return;
    var cuerpo = menu.querySelector('.menu-movil-cuerpo');
    SECCIONES.forEach(function (s) {
      var g = document.createElement('section');
      g.className = 'menu-grupo';
      g.id = 'menu-' + s.id;
      var h = document.createElement('h2');
      h.className = 'menu-grupo-nombre';
      h.textContent = s.nombre;
      var p = document.createElement('p');
      p.className = 'menu-grupo-que';
      p.textContent = s.que;
      g.appendChild(h);
      g.appendChild(p);
      g.appendChild(lista(s, s.destinos));
      cuerpo.appendChild(g);
    });
    botonMenu.addEventListener('click', function () { abrirMenu(); });
    menu.querySelector('.menu-movil-cerrar').addEventListener('click', cerrarMenu);
    menu.addEventListener('click', function (e) {
      var b = e.target.closest('[data-menu-accion]');
      if (!b) return;
      var acc = b.getAttribute('data-menu-accion');
      cerrarMenu();
      if (acc === 'tema') llamar('toggleTheme');
      if (acc === 'compartir') llamar('compartirPlataforma');
      if (acc === 'ayudanos') ACCIONES.ayudanos();
    });
  }

  function abrirMenu(seccion) {
    if (!menu) return;
    ultimoFoco = document.activeElement;
    menu.hidden = false;
    menu.classList.add('abierto');
    document.body.classList.add('menu-abierto');
    botonMenu.setAttribute('aria-expanded', 'true');
    var destino = seccion && document.getElementById('menu-' + seccion);
    if (destino) destino.scrollIntoView({ block: 'start' });
    else menu.scrollTop = 0;
    menu.querySelector('.menu-movil-cerrar').focus();
  }

  function cerrarMenu() {
    if (!menu || !menu.classList.contains('abierto')) return;
    menu.classList.remove('abierto');
    menu.hidden = true;
    document.body.classList.remove('menu-abierto');
    botonMenu.setAttribute('aria-expanded', 'false');
    if (ultimoFoco && ultimoFoco.focus) ultimoFoco.focus();
  }

  // ---- Ruta de migas: dónde estás y cómo volver ---------------------------
  // Si el módulo se abrió desde otro lugar (un enlace dentro de otro módulo),
  // se busca en la lista por el módulo que el motor dejó activo.
  function destinoActual() {
    if (ultimoDestino && ultimoDestino.d.m) return ultimoDestino;
    var candidatos = clavesAbiertas();
    for (var i = 0; i < candidatos.length; i++) {
      for (var j = 0; j < SECCIONES.length; j++) {
        var s = SECCIONES[j];
        for (var k = 0; k < s.destinos.length; k++) {
          var d = s.destinos[k];
          if (d.m && d.m === candidatos[i] && !d.a) return { d: d, s: s };
        }
      }
    }
    return null;
  }

  function pintarMigas() {
    var desglose = document.getElementById('seccionDesgloseModulos');
    if (!desglose) return;
    var migas = document.getElementById('rutaMigas');
    if (!migas) {
      migas = document.createElement('nav');
      migas.id = 'rutaMigas';
      migas.className = 'ruta-migas';
      migas.setAttribute('aria-label', 'Estás aquí');
      desglose.insertBefore(migas, desglose.firstChild);
    }
    migas.innerHTML = '';
    migas.appendChild(boton('‹ Inicio', 'ruta-inicio', function () {
      ultimoDestino = null;
      llamar('plegarDesgloseModulos');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }));
    var actual = destinoActual();
    if (actual) {
      var sec = boton(actual.s.nombre, 'ruta-seccion', function () { abrirSeccion(actual.s.id); });
      migas.appendChild(sec);
      var aqui = document.createElement('span');
      aqui.className = 'ruta-aqui';
      aqui.setAttribute('aria-current', 'page');
      aqui.textContent = actual.d.t;
      migas.appendChild(aqui);
    }
  }

  // ---- Rótulos sin emojis ---------------------------------------------------
  var EMOJI = /(?:\p{Extended_Pictographic}|\p{Regional_Indicator})(?:️|‍(?:\p{Extended_Pictographic}))*️?/gu;
  var ROTULOS = 'h1,h2,h3,h4,h5,h6,button,a,label,summary,th,legend,[role="tab"],[role="button"],' +
                '.hero-tag,.erario-kicker,.dec-kicker,.label,.explorer-hero-tag,.radar-tag,.radar-stat-lbl,' +
                '.showcase-slide-badge,.insp-sep-n,.section-hero .hero-tag';
  var IGNORAR = 'input,textarea,select,[contenteditable],script,style,.com-post,.com-hilo';

  function limpiarTexto(nodo) {
    var t = nodo.nodeValue;
    if (!t || !EMOJI.test(t)) return;
    EMOJI.lastIndex = 0;
    var el = nodo.parentElement;
    if (!el || el.closest(IGNORAR)) return;
    if (el.closest(ROTULOS)) {
      var empiezaConEmoji = /^\s*(?:\p{Extended_Pictographic}|\p{Regional_Indicator})/u.test(t);
      var limpio = t.replace(EMOJI, '').replace(/ {2,}/g, ' ');
      nodo.nodeValue = empiezaConEmoji ? limpio.replace(/^\s+/, '') : limpio;
    } else {
      // Fuera de rótulos solo se quita el emoji que hace de ícono al inicio.
      nodo.nodeValue = t.replace(/^(\s*)(?:(?:\p{Extended_Pictographic}|\p{Regional_Indicator})(?:️|‍\p{Extended_Pictographic})*️?\s*)+/u, '$1');
    }
    EMOJI.lastIndex = 0;
  }

  function limpiar(raiz) {
    if (!raiz) return;
    if (raiz.nodeType === 3) { limpiarTexto(raiz); return; }
    if (raiz.nodeType !== 1) return;
    var w = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT);
    var n;
    while ((n = w.nextNode())) limpiarTexto(n);
  }

  var pendientes = [];
  var programado = false;
  function observar() {
    new MutationObserver(function (cambios) {
      cambios.forEach(function (c) {
        if (c.type === 'characterData') pendientes.push(c.target);
        else c.addedNodes.forEach(function (n) { pendientes.push(n); });
      });
      if (!programado) {
        programado = true;
        requestAnimationFrame(function () {
          programado = false;
          var lote = pendientes;
          pendientes = [];
          lote.forEach(limpiar);
        });
      }
    }).observe(document.body, { childList: true, subtree: true, characterData: true });
  }

  // ---- Padrón municipal diferido (fase 1f) ----------------------------------
  // Los dos archivos pesan 677 KB. Se descargan cuando la página ya se puede
  // usar, o antes si alguien busca o abre un módulo que los necesita. Si el
  // módulo se abrió sin ellos, se vuelve a pintar cuando llegan.
  var MODULOS_CON_MUNICIPIOS = ['municipios', 'territorio', 'verificador'];
  var muniPromesa = null;
  var repintarAlLlegar = null;

  function sello() {
    var s = document.querySelector('script[src*="legibilidad.js"]');
    var m = s && s.getAttribute('src').match(/\?v=([0-9a-z]+)/);
    return m ? m[1] : '';
  }
  function cargarScript(nombre) {
    return new Promise(function (ok, mal) {
      var sc = document.createElement('script');
      sc.src = 'assets/auditor/js/' + nombre + (sello() ? '?v=' + sello() : '');
      sc.onload = ok;
      sc.onerror = function () { mal(new Error(nombre)); };
      document.head.appendChild(sc);
    });
  }
  function municipiosListos() { return !!(window.AUDIT_MUNICIPIOS && window.AUDIT_MUN_RENDICION); }

  function cargarMunicipios() {
    if (municipiosListos()) return Promise.resolve();
    if (muniPromesa) return muniPromesa;
    avisoMunicipios('cargando');
    muniPromesa = cargarScript('municipios-efipem.js')
      .then(function () { return cargarScript('municipios-rendicion.js'); })
      .then(function () {
        avisoMunicipios(null);
        if (repintarAlLlegar && moduloAbierto()) llamar('seleccionarModuloExplorer', repintarAlLlegar);
        repintarAlLlegar = null;
      })
      .catch(function () { muniPromesa = null; avisoMunicipios('error'); });
    return muniPromesa;
  }

  function claveModuloAbierto() {
    var partes = clavesAbiertas();
    for (var i = 0; i < partes.length; i++) {
      if (MODULOS_CON_MUNICIPIOS.indexOf(partes[i]) > -1) return partes[i];
    }
    return null;
  }

  function avisoMunicipios(estado) {
    var el = document.getElementById('avisoMunicipios');
    if (!estado) { if (el) el.remove(); return; }
    if (!moduloAbierto() || !claveModuloAbierto()) return;
    var migas = document.getElementById('rutaMigas');
    if (!migas) return;
    if (!el) {
      el = document.createElement('p');
      el.id = 'avisoMunicipios';
      el.className = 'aviso-carga';
      el.setAttribute('role', 'status');
      migas.insertAdjacentElement('afterend', el);
    }
    el.innerHTML = '';
    if (estado === 'cargando') {
      el.textContent = 'Descargando los datos de los municipios. Tarda unos segundos con internet lento.';
    } else {
      el.textContent = 'No se pudieron descargar los datos de los municipios. ';
      el.appendChild(boton('Reintentar', 'aviso-carga-btn', cargarMunicipios));
    }
  }

  function vigilarMunicipios() {
    var buscador = document.getElementById('globalSearchInput');
    if (buscador) buscador.addEventListener('focus', cargarMunicipios, { once: true });
    window.addEventListener('load', function () {
      var ocioso = window.requestIdleCallback || function (f) { return setTimeout(f, 1500); };
      ocioso(function () { cargarMunicipios(); }, { timeout: 4000 });
    });
  }

  function alAbrirModulo() {
    var clave = claveModuloAbierto();
    if (clave && !municipiosListos()) {
      repintarAlLlegar = clave;
      cargarMunicipios();
      setTimeout(function () { if (!municipiosListos()) avisoMunicipios(muniPromesa ? 'cargando' : 'error'); }, 150);
    }
  }

  // ---- Arranque ---------------------------------------------------------------
  function iniciar() {
    pintarNav();
    pintarPortada();
    pintarMenu();
    limpiar(document.body);
    observar();

    var inicio = document.getElementById('navInicio');
    if (inicio) inicio.addEventListener('click', function (e) {
      e.preventDefault();
      ultimoDestino = null;
      volverAPortada();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    var cifra = document.getElementById('portadaCifraIr');
    if (cifra) cifra.addEventListener('click', function () { ir(SECCIONES[2].destinos[0], SECCIONES[2]); });
    var ayuda = document.getElementById('portadaAyudanos');
    if (ayuda) ayuda.addEventListener('click', ACCIONES.ayudanos);

    // La ruta de migas se actualiza cada vez que se abre un módulo, venga de
    // donde venga (menú, portada o un enlace dentro de otro módulo).
    var desglose = document.getElementById('seccionDesgloseModulos');
    if (desglose) new MutationObserver(function () {
      if (moduloAbierto()) { pintarMigas(); setTimeout(alAbrirModulo, 60); } else ultimoDestino = null;
    }).observe(desglose, { attributes: true, attributeFilter: ['class'] });
    vigilarMunicipios();
    window.addEventListener('hashchange', function () {
      if (moduloAbierto()) { ultimoDestino = null; pintarMigas(); alAbrirModulo(); }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      cerrarPanel();
      cerrarMenu();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
