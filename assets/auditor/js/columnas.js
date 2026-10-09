/* Auditavisión · Aprende › Noticias relevantes (09-10-2026).
   Columnas editoriales con datos curiosos de personajes y hechos del dinero
   público, en formato de periódico. Reúnen lo que fueron las secciones 5.2
   («Personajes relevantes») y 5.3 («Datos curiosos») de la Enciclopedia,
   retiradas el 27-09-2026 porque no citaban fuentes: aquí solo entra lo que
   se pudo verificar contra un documento oficial, y cada columna lista los
   suyos. Lo que no se pudo sostener se quedó fuera (ver CONTEXT.md).
   Regla editorial (AGENTS.md §2): presunción de inocencia, nada de
   adjetivos; un proceso no es una condena y una observación de la ASF «por
   aclarar» no es un robo probado. */
(function () {
  'use strict';

  var EDICION = '9 de octubre de 2026';
  var SECCIONES = [
    ['todas', 'Todas'],
    ['Personajes', 'Personajes'],
    ['Hechos', 'Hechos'],
    ['Historia', 'Historia']
  ];
  /* Ilustración de cada sección cuando la columna no trae retrato. */
  var ILUS = { Personajes: ['🧑‍⚖️', 'tinta'], Hechos: ['🗂️', 'sepia'], Historia: ['📜', 'oliva'] };

  /* Cada columna: {id, seccion, titulo, balazo, cuerpo[], dato_curioso,
     cifras[{valor, etq, estado, fuente, url}], fuentes[{nombre, url}],
     actualizado, icono?, imagen?{src, alt, credito}} */
  var COLUMNAS = [];

  var raiz = document.getElementById('columnasDiario');
  if (!raiz) return;

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function chip(estado) {
    return '<span class="est-chip est-' + esc(estado) + '">' + esc(estado) + '</span>';
  }
  function figura(c, grande) {
    if (c.imagen) {
      return '<figure class="col-fig"><img src="' + esc(c.imagen.src) + '" alt="' + esc(c.imagen.alt) + '" loading="lazy"' +
        (grande ? '' : ' width="480" height="320"') + '>' +
        '<figcaption>' + esc(c.imagen.credito) + '</figcaption></figure>';
    }
    var il = ILUS[c.seccion] || ['📰', 'tinta'];
    return '<figure class="col-fig col-ilus col-ilus-' + il[1] + '" aria-hidden="true"><span>' + (c.icono || il[0]) + '</span></figure>';
  }

  function articulo(c, i) {
    var cifras = (c.cifras || []).map(function (x) {
      return '<li><strong>' + esc(x.valor) + '</strong><span>' + esc(x.etq) + '</span>' +
        '<small>' + chip(x.estado) + ' ' + (x.url ? '<a href="' + esc(x.url) + '" target="_blank" rel="noopener noreferrer">' + esc(x.fuente) + ' ↗</a>' : esc(x.fuente)) + '</small></li>';
    }).join('');
    var fuentes = (c.fuentes || []).map(function (f) {
      return '<li><a href="' + esc(f.url) + '" target="_blank" rel="noopener noreferrer">' + esc(f.nombre) + ' ↗</a></li>';
    }).join('');
    return '<article class="col-art' + (i === 0 ? ' col-art-portada' : '') + '" id="col-' + esc(c.id) + '" data-seccion="' + esc(c.seccion) + '">' +
      figura(c, i === 0) +
      '<div class="col-art-tx">' +
        '<span class="col-kicker">' + esc(c.seccion) + '</span>' +
        '<h4 class="col-titular">' + esc(c.titulo) + '</h4>' +
        '<p class="col-balazo">' + esc(c.balazo) + '</p>' +
        '<p class="col-firma">Redacción Auditavisión · Con documentos oficiales</p>' +
        '<button type="button" class="col-leer" aria-expanded="false" aria-controls="col-cuerpo-' + esc(c.id) + '">Leer la columna ➔</button>' +
      '</div>' +
      '<div class="col-cuerpo" id="col-cuerpo-' + esc(c.id) + '" hidden>' +
        (c.cuerpo || []).map(function (p, k) { return '<p' + (k === 0 ? ' class="col-capitular"' : '') + '>' + esc(p) + '</p>'; }).join('') +
        (c.dato_curioso ? '<aside class="col-dato"><b>💡 Dato curioso</b><p>' + esc(c.dato_curioso) + '</p></aside>' : '') +
        (cifras ? '<ul class="col-cifras" aria-label="Cifras de la columna">' + cifras + '</ul>' : '') +
        '<div class="col-fuentes"><b>📎 Documentos que la sostienen</b><ol>' + fuentes + '</ol>' +
          (c.actualizado ? '<p class="col-act">Verificado al ' + esc(c.actualizado) + '.</p>' : '') +
        '</div>' +
        '<div class="col-acciones">' +
          '<button type="button" class="col-copiar" data-id="' + esc(c.id) + '">🔗 Copiar enlace a esta columna</button>' +
          '<button type="button" class="col-cerrar">Cerrar la columna ▴</button>' +
        '</div>' +
      '</div>' +
    '</article>';
  }

  var filtro = 'todas';
  function pintar() {
    var lista = COLUMNAS.filter(function (c) { return filtro === 'todas' || c.seccion === filtro; });
    raiz.innerHTML =
      '<header class="col-cabezal">' +
        '<div class="col-cabezal-linea"><span>Edición del ' + EDICION + '</span><span>Cada cifra, con su documento</span></div>' +
        '<h3 class="col-nombre">La Columna del Erario</h3>' +
        '<p class="col-lema">Personajes y hechos del dinero público que vale la pena conocer</p>' +
        '<nav class="col-secciones" aria-label="Secciones del diario">' +
          SECCIONES.map(function (s) {
            var n = s[0] === 'todas' ? COLUMNAS.length : COLUMNAS.filter(function (c) { return c.seccion === s[0]; }).length;
            return '<button type="button" data-sec="' + s[0] + '" aria-pressed="' + (filtro === s[0]) + '">' + s[1] + ' <small>' + n + '</small></button>';
          }).join('') +
        '</nav>' +
      '</header>' +
      '<p class="col-aviso">Estas columnas sustituyen las fichas de personajes de la Enciclopedia, retiradas en septiembre de 2026 porque no citaban fuentes. ' +
        'Aquí solo entra lo que sostiene un documento oficial: una sentencia, una resolución, un informe de la Auditoría Superior o el Diario Oficial. ' +
        'Un proceso abierto no es una condena, y una cifra «por aclarar» no es un robo probado.</p>' +
      (lista.length ? '<div class="col-rejilla">' + lista.map(articulo).join('') + '</div>'
                    : '<p class="col-vacio">Todavía no hay columnas verificadas en esta sección.</p>');
  }

  function abrir(art, abrirla, desplazar) {
    var btn = art.querySelector('.col-leer'), cuerpo = art.querySelector('.col-cuerpo');
    btn.setAttribute('aria-expanded', abrirla ? 'true' : 'false');
    btn.textContent = abrirla ? 'Leyendo la columna ▾' : 'Leer la columna ➔';
    cuerpo.hidden = !abrirla;
    art.classList.toggle('col-abierta', abrirla);
    if (desplazar) {
      var nav = document.querySelector('.site-top-nav');
      document.body.classList.add('cabecera-compacta');
      var alto = nav ? nav.getBoundingClientRect().height : 0;
      window.scrollTo({ top: Math.max(0, art.getBoundingClientRect().top + window.pageYOffset - alto - 12), behavior: 'smooth' });
    }
  }

  raiz.addEventListener('click', function (e) {
    var sec = e.target.closest('.col-secciones button');
    if (sec) { filtro = sec.getAttribute('data-sec'); pintar(); return; }
    var leer = e.target.closest('.col-leer');
    if (leer) {
      var art = leer.closest('.col-art');
      abrir(art, leer.getAttribute('aria-expanded') !== 'true', true);
      return;
    }
    var cerrar = e.target.closest('.col-cerrar');
    if (cerrar) { abrir(cerrar.closest('.col-art'), false, true); return; }
    var copiar = e.target.closest('.col-copiar');
    if (copiar) {
      var url = location.href.split('#')[0] + '#col-' + copiar.getAttribute('data-id');
      var listo = function () { copiar.textContent = '✅ Enlace copiado'; setTimeout(function () { copiar.textContent = '🔗 Copiar enlace a esta columna'; }, 2200); };
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(listo, function () { prompt('Copia este enlace:', url); });
      else prompt('Copia este enlace:', url);
    }
  });

  pintar();

  /* Enlace directo a una columna (#col-<id>): abre la pestaña y la columna. */
  function irAColumna() {
    var h = decodeURIComponent(location.hash.slice(1));
    if (h.indexOf('col-') !== 0) return;
    var art = document.getElementById(h);
    if (!art) return;
    var pest = document.getElementById('pestana-noticias');
    if (pest && pest.getAttribute('aria-selected') !== 'true') pest.click();
    setTimeout(function () { abrir(art, true, true); }, 60);
  }
  window.addEventListener('hashchange', irAColumna);
  if (location.hash.indexOf('#col-') === 0) window.addEventListener('load', function () { setTimeout(irAColumna, 420); });
})();
