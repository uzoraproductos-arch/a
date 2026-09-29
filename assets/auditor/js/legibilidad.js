/* ==========================================================================
   AUDITAVISIÓN · PORTADA DE TRES PUERTAS Y MENÚ MÓVIL (fase 1 de docs/ux/PLAN.md)
   Las listas de cada sección viven solo aquí: de ellas salen las puertas de
   la portada y el menú del celular. Cada destino abre un módulo con las
   mismas funciones que ya usa la barra de navegación.
   Nombres de secciones: propuesta en docs/ux/fase-0-propuestas.md §3.
   ========================================================================== */
(function () {
  'use strict';

  // m = módulo del motor; a = ancla dentro del módulo; accion = caso especial.
  // enPortada = cuántos destinos muestra la puerta de la portada (el menú los muestra todos).
  var SECCIONES = [
    {
      id: 'lee', nombre: 'Lee', que: 'Reportajes para entender a dónde va el dinero.', enPortada: 4,
      destinos: [
        { t: 'Panorama del presupuesto 2026', m: 'presupuesto' },
        { t: 'Megaobras: lo que costaron', m: 'megaobras' },
        { t: 'Paquete Económico 2027', m: 'proyeccion2027' },
        { t: 'Lo que cuestan el Congreso y la Judicatura', m: 'poderes' },
        { t: 'El costo ambiental', m: 'ambiente' }
      ]
    },
    {
      id: 'explora', nombre: 'Explora', que: 'Herramientas para hacer tus propias cuentas.', enPortada: 4,
      destinos: [
        { t: 'A dónde van tus impuestos', m: 'calculadora' },
        { t: 'Contrasta la cifra de una nota', m: 'verificador', a: 'vnSeccion' },
        { t: 'Auditoría en imágenes', accion: 'imagenes' },
        { t: 'El reloj del dinero público', accion: 'reloj' }
      ]
    },
    {
      id: 'consulta', nombre: 'Consulta', que: 'Datos oficiales para buscar y descargar.', enPortada: 4,
      destinos: [
        { t: 'Lo que encontró la ASF en 2024', m: 'verificador', a: 'cuentaPublicaASF' },
        { t: 'Los 2,479 municipios', m: 'municipios' },
        { t: 'Las 32 entidades', m: 'territorio' },
        { t: '¿Tu proveedor está en la lista 69-B del SAT?', accion: 'efos' },
        { t: 'Estados con más por aclarar', m: 'verificador', a: 'radarBanderasNacional' },
        { t: 'Expedientes de casos', m: 'verificador', a: 'expedientesCasos' },
        { t: 'Datos para descargar', accion: 'descargas' },
        { t: 'Glosario', accion: 'glosario' },
        { t: 'Fuentes oficiales', accion: 'fuentes' }
      ]
    },
    {
      id: 'participa', nombre: 'Participa', que: 'Aporta lo que viste y conoce dónde denunciar.', enPortada: 0,
      destinos: [
        { t: 'Reporta lo que viste', accion: 'ayudanos' },
        { t: 'Portal ciudadano', m: 'portal' },
        { t: 'Canales oficiales de denuncia', m: 'portal', a: 'bloqueCanales' },
        { t: 'Decálogo del ciudadano auditor', m: 'portal', a: 'decalogoWrap' }
      ]
    }
  ];

  function motor() { return window.AuditEngine || {}; }

  function volverAPortada() {
    var desglose = document.getElementById('seccionDesgloseModulos');
    if (desglose && desglose.classList.contains('desglose-abierto') && motor().plegarDesgloseModulos) {
      motor().plegarDesgloseModulos();
    }
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
    efos: function () { motor().efosAbrir && motor().efosAbrir(); },
    descargas: function () { motor().abrirDescargas && motor().abrirDescargas(); },
    glosario: function () { motor().abrirDiccionarioSubtab && motor().abrirDiccionarioSubtab('faq-glosario'); },
    fuentes: function () { motor().abrirCatalogoFuentes && motor().abrirCatalogoFuentes(); },
    ayudanos: function () { motor().openAyudanosFiscalizar && motor().openAyudanosFiscalizar(); }
  };

  function ir(destino) {
    cerrarMenu();
    if (destino.accion) {
      if (ACCIONES[destino.accion]) ACCIONES[destino.accion]();
      return;
    }
    if (motor().seleccionarModuloExplorer) motor().seleccionarModuloExplorer(destino.m, destino.a);
  }

  function lista(destinos) {
    var ul = document.createElement('ul');
    ul.className = 'puerta-lista';
    destinos.forEach(function (d) {
      var li = document.createElement('li');
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'puerta-ir';
      b.textContent = d.t;
      b.addEventListener('click', function () { ir(d); });
      li.appendChild(b);
      ul.appendChild(li);
    });
    return ul;
  }

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
      var ul = lista(s.destinos.slice(0, s.enPortada));
      if (s.destinos.length > s.enPortada) {
        var li2 = document.createElement('li');
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'puerta-ir';
        b.textContent = 'Ver todo en ' + s.nombre;
        b.addEventListener('click', function () { abrirMenu(s.id); });
        li2.appendChild(b);
        ul.appendChild(li2);
      }
      li.appendChild(ul);
      cont.appendChild(li);
    });
  }

  // ---- Menú móvil -------------------------------------------------------
  var menu, boton, ultimoFoco;

  function pintarMenu() {
    menu = document.getElementById('menuMovil');
    boton = document.getElementById('menuMovilBtn');
    if (!menu || !boton) return;
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
      g.appendChild(lista(s.destinos));
      cuerpo.appendChild(g);
    });
    boton.addEventListener('click', function () { abrirMenu(); });
    menu.querySelector('.menu-movil-cerrar').addEventListener('click', cerrarMenu);
    menu.addEventListener('click', function (e) {
      var b = e.target.closest('[data-menu-accion]');
      if (!b) return;
      var acc = b.getAttribute('data-menu-accion');
      cerrarMenu();
      if (acc === 'tema' && motor().toggleTheme) motor().toggleTheme();
      if (acc === 'compartir' && motor().compartirPlataforma) motor().compartirPlataforma();
      if (acc === 'ayudanos') ACCIONES.ayudanos();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('abierto')) cerrarMenu();
    });
  }

  function abrirMenu(seccion) {
    if (!menu) return;
    ultimoFoco = document.activeElement;
    menu.hidden = false;
    menu.classList.add('abierto');
    document.body.classList.add('menu-abierto');
    boton.setAttribute('aria-expanded', 'true');
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
    boton.setAttribute('aria-expanded', 'false');
    if (ultimoFoco && ultimoFoco.focus) ultimoFoco.focus();
  }

  function iniciar() {
    pintarPortada();
    pintarMenu();
    var cifra = document.getElementById('portadaCifraIr');
    if (cifra) cifra.addEventListener('click', function () { ir({ m: 'verificador', a: 'cuentaPublicaASF' }); });
    var ayuda = document.getElementById('portadaAyudanos');
    if (ayuda) ayuda.addEventListener('click', ACCIONES.ayudanos);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
