/* Expedientes de casos por aclarar: pinta expedientes.html.

   Antes vivian plegados en el bloque 3 del Modo Inspector de la portada;
   desde el 09-10-2026 tienen su pagina (AGENTS.md, 5 bis). Todo sale de
   window.AUDIT_DB.expedientes (herramientas/integrar_expedientes.py): cada
   cifra suma informes individuales de la ASF enlistados en la ficha, o viene
   del Sistema de Alertas de la SHCP. Aqui no se escribe ningun monto. */
(function () {
  'use strict';
  var DB = window.AUDIT_DB || {};
  var E = DB.expedientes || {};
  var FICHAS = E.fichas || [];
  var QUIETO = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var CATEGORIAS = [
    ['todos', 'Todos'], ['megaobras', 'Megaobras'], ['energia', 'Energía (Pemex)'],
    ['salud', 'Salud y fármacos'], ['alimentos', 'Segalmex'], ['deuda', 'Deuda de los estados']
  ];
  var NOMBRE_CAT = {};
  CATEGORIAS.forEach(function (c) { NOMBRE_CAT[c[0]] = c[1]; });

  var ACCIONES = {
    R: ['recomendación', 'recomendaciones'], RD: ['recomendación al desempeño', 'recomendaciones al desempeño'],
    SA: ['solicitud de aclaración', 'solicitudes de aclaración'], PEFCF: ['aviso al SAT', 'avisos al SAT'],
    PRAS: ['promoción de responsabilidad', 'promociones de responsabilidad'], PO: ['pliego de observaciones', 'pliegos de observaciones'],
    DH: ['denuncia de hechos', 'denuncias de hechos']
  };

  /* El caso que tambien tiene su pagina en Auditoria en imagenes. */
  var EN_IMAGENES = {
    'tren-maya': 'auditoria-tren-maya.html', 'tren-toluca': 'auditoria-tren-toluca.html',
    'aifa': 'auditoria-aifa.html', 'dos-bocas': 'auditoria-dos-bocas.html',
    'cuchillo-ii': 'auditoria-lego-cienega.html', 'birmex': 'auditoria-megafarmacia.html'
  };

  function esc(t) {
    return String(t == null ? '' : t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function chip(e) {
    var t = (e === 'oficial' || e === 'pendiente') ? e : 'derivado';
    return '<span class="est-chip est-' + t + '">' + t + '</span>';
  }
  function mdp(pesos) {
    return '$' + (pesos / 1e6).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp';
  }
  function pct(p) {
    return p.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' %';
  }
  function accionesTexto(a) {
    var k = Object.keys(a || {});
    if (!k.length) return 'sin acciones';
    return k.map(function (x) { return a[x] + ' ' + (ACCIONES[x] ? ACCIONES[x][a[x] === 1 ? 0 : 1] : x); }).join(', ');
  }
  function num(n) { return (n < 10 ? '0' : '') + n; }

  /* --- Indice: una tarjeta por caso ------------------------------------- */
  function tarjeta(f, n) {
    var c = f.cifras[1] || f.cifras[0];
    return '<a class="ex-tarjeta" href="#exp-' + f.id + '" data-cat="' + f.categoria + '">' +
      '<span class="ex-tarjeta-n num-tabular" aria-hidden="true">' + num(n) + '</span>' +
      '<span class="ex-tarjeta-ico" aria-hidden="true">' + f.icono + '</span>' +
      '<span class="ex-tarjeta-cat">' + esc(NOMBRE_CAT[f.categoria] || f.categoria) + '</span>' +
      '<span class="ex-tarjeta-tit">' + esc(f.titulo) + '</span>' +
      (c ? '<span class="ex-tarjeta-dato"><b class="num-tabular">' + esc(c.valor) + '</b> ' + esc(c.etq) + '</span>' : '') +
      '<span class="ex-tarjeta-ir">Ver expediente ➔</span>' +
    '</a>';
  }

  /* --- Barras: lo que quedo por aclarar, Cuenta Publica por Cuenta Publica */
  function barras(f) {
    if (!f.anios) return '';
    var max = Math.max.apply(null, f.anios.map(function (a) { return a.porAclarar; }));
    if (!(max > 0)) return '';
    return '<div class="ex-barras" aria-label="Por aclarar en cada Cuenta Pública">' +
      '<p class="ex-sub">💸 Por aclarar en cada Cuenta Pública ' + chip('derivado') + '</p>' +
      f.anios.map(function (a) {
        var w = a.porAclarar / max * 100;
        return '<div class="ex-barra"><span class="ex-barra-k">CP ' + a.cp + '</span>' +
          '<span class="ex-barra-pista"><span class="ex-barra-llena" style="--w:' + w.toFixed(2) + '%"></span></span>' +
          '<span class="ex-barra-v num-tabular">' + (a.porAclarar ? mdp(a.porAclarar) : 'Nada por aclarar') + '</span></div>';
      }).join('') +
      '<p class="ex-nota">Suma de los informes de cada año enlistados abajo.</p>' +
    '</div>';
  }

  /* --- Un caso completo -------------------------------------------------- */
  function caso(f, n) {
    var cifras = '<div class="exp-cifras">' + f.cifras.map(function (c) {
      return '<div class="exp-cifra"><span class="exp-cifra-v num-tabular">' + esc(c.valor) + '</span>' +
        '<span class="exp-cifra-e">' + esc(c.etq) + ' ' + chip(c.estado) + '</span></div>';
    }).join('') + '</div>';

    var detalle = '';
    if (f.anios) {
      detalle = '<div class="pd-tabla-w"><table class="pd-tabla exp-anios"><thead><tr><th>Cuenta Pública</th><th>Informes</th><th>Por aclarar</th><th>Pliegos</th><th>Promociones</th></tr></thead><tbody>' +
        f.anios.map(function (a) {
          return '<tr><td>' + a.cp + '</td><td class="num-tabular">' + a.auditorias + '</td><td class="num-tabular">' + mdp(a.porAclarar) +
            '</td><td class="num-tabular">' + a.PO + '</td><td class="num-tabular">' + a.PRAS + '</td></tr>';
        }).join('') + '</tbody></table></div>';
    } else if (f.tabla) {
      detalle = '<div class="pd-tabla-w"><table class="pd-tabla exp-anios"><thead><tr><th>Estado</th><th>Deuda / ingresos libres</th><th>Deuda y obligaciones</th></tr></thead><tbody>' +
        f.tabla.map(function (t) {
          return '<tr><td>' + esc(t.entidad) + '</td><td class="num-tabular">' + pct(t.dyoIld * 100) + '</td><td class="num-tabular">' + mdp(t.dyo) + '</td></tr>';
        }).join('') + '</tbody></table></div>';
    }

    var docs = f.auditorias
      ? '<details class="exp-informes"><summary>' + (f.auditorias.length === 1 ? 'El informe de la ASF' : 'Los ' + f.auditorias.length + ' informes de la ASF, uno por uno') + '</summary><ol>' +
          f.auditorias.map(function (a) {
            return '<li><a href="' + esc(a.url) + '" target="_blank" rel="noopener noreferrer">CP ' + a.cp + ' · Auditoría ' + a.num + ' ↗</a> ' +
              '<span>' + esc(a.titulo) + ' · <i>' + esc(a.ente) + '</i></span> <small>' +
              (a.porAclarar ? mdp(a.porAclarar) + ' por aclarar; ' : 'Sin monto por aclarar; ') +
              (a.recuperado ? mdp(a.recuperado) + ' recuperados; ' : '') + accionesTexto(a.acciones) + '.</small></li>';
          }).join('') + '</ol></details>'
      : '<ul class="exp-docs">' + (f.documentos || []).map(function (d) {
          return '<li><a href="' + esc(d.url) + '" target="_blank" rel="noopener noreferrer">' + esc(d.titulo) + ' ↗</a></li>';
        }).join('') + '</ul>';

    var principal = f.auditorias
      ? f.auditorias.slice().sort(function (x, y) { return y.porAclarar - x.porAclarar; })[0].url
      : (f.documentos && f.documentos[0] ? f.documentos[0].url : '');

    return '<article class="ex-caso" id="exp-' + f.id + '" data-cat="' + f.categoria + '" aria-labelledby="exp-' + f.id + '-tit">' +
      '<header class="ex-caso-cab">' +
        '<span class="ex-caso-n num-tabular" aria-hidden="true">' + num(n) + '</span>' +
        '<span class="ex-caso-ico" aria-hidden="true">' + f.icono + '</span>' +
        '<div><span class="ex-caso-cat">' + esc(NOMBRE_CAT[f.categoria] || f.categoria) + '</span>' +
          '<h2 class="ex-caso-tit" id="exp-' + f.id + '-tit">' + esc(f.titulo) + '</h2>' +
          '<p class="ex-caso-ente">' + esc(f.ente) + '</p></div>' +
      '</header>' +
      '<p class="exp-hallazgo ex-hallazgo"><span aria-hidden="true">🔦</span> ' + esc(f.hallazgo) + '</p>' +
      cifras + barras(f) + detalle + docs +
      '<p class="ex-nota">' + chip('oficial') + ' ' + esc(f.fuente) + '. ' + esc(f.alcance) + '</p>' +
      '<div class="ex-acciones">' +
        (principal ? '<a class="ex-btn ex-btn-oro" href="' + esc(principal) + '" target="_blank" rel="noopener noreferrer">🏛️ ' +
          (f.auditorias ? 'Informe principal' : 'Documento oficial') + ' ↗</a>' : '') +
        '<button type="button" class="ex-btn" data-copiar="' + f.id + '">📋 Copiar ficha con fuentes</button>' +
        (EN_IMAGENES[f.id] ? '<a class="ex-btn" href="' + EN_IMAGENES[f.id] + '">🖼️ Verlo en Auditoría en imágenes</a>' : '') +
        '<a class="ex-btn ex-btn-sutil" href="#casos">↑ Volver a la lista</a>' +
      '</div>' +
    '</article>';
  }

  function copiar(id) {
    var f = FICHAS.find(function (x) { return x.id === id; });
    if (!f) return;
    var t = f.titulo + '\n' + f.ente + '\n\n' + f.hallazgo + '\n\n' +
      f.cifras.map(function (c) { return '- ' + c.valor + ': ' + c.etq + ' (' + c.estado + ')'; }).join('\n');
    if (f.auditorias) t += '\n\nInformes de la ASF:\n' + f.auditorias.map(function (a) {
      return '- CP ' + a.cp + ', auditoría ' + a.num + ' (' + a.clave + '): ' + a.titulo + '. ' + a.url;
    }).join('\n');
    if (f.documentos) t += '\n\nDocumentos:\n' + f.documentos.map(function (d) { return '- ' + d.titulo + ': ' + d.url; }).join('\n');
    t += '\n\nFuente: ' + f.fuente + '. ' + f.alcance + '\nConsultado en Auditavisión: ' + location.href.split('#')[0] + '#exp-' + f.id;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t).then(function () { alert('✓ Ficha copiada con sus fuentes.'); })
        .catch(function () { prompt('No se pudo copiar automáticamente. Copia el texto desde aquí:', t); });
    } else {
      prompt('Este navegador no permite copiar automáticamente. Copia el texto desde aquí:', t);
    }
  }

  /* --- Filtro por tema --------------------------------------------------- */
  function filtrar(cat) {
    var n = 0;
    document.querySelectorAll('#exIndice .ex-tarjeta, #exCasos .ex-caso').forEach(function (el) {
      var ver = cat === 'todos' || el.getAttribute('data-cat') === cat;
      el.hidden = !ver;
      if (ver && el.classList.contains('ex-caso')) n++;
    });
    document.querySelectorAll('#exChips button').forEach(function (b) {
      var on = b.getAttribute('data-cat') === cat;
      b.classList.toggle('activo', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    var c = document.getElementById('exConteo');
    if (c) c.textContent = n;
  }

  /* La cabecera fija se compacta al bajar: se compacta antes de medir para
     que el caso no quede debajo de ella. */
  function irA(id, suave) {
    var el = document.getElementById(id);
    if (!el) return;
    if (el.hidden) filtrar('todos');
    document.body.classList.add('cabecera-compacta');
    var nav = document.querySelector('.site-top-nav');
    var alto = nav ? nav.getBoundingClientRect().height : 0;
    var y = el.getBoundingClientRect().top + window.pageYOffset - alto - 16;
    window.scrollTo({ top: Math.max(0, y), behavior: suave && !QUIETO ? 'smooth' : 'auto' });
    if (el.classList.contains('ex-caso')) {
      el.classList.remove('ex-destaca');
      void el.offsetWidth;
      el.classList.add('ex-destaca');
    }
  }

  /* Las barras crecen cuando entran en pantalla. */
  function animarBarras() {
    var barras = document.querySelectorAll('.ex-barras');
    if (QUIETO || !('IntersectionObserver' in window)) {
      barras.forEach(function (b) { b.classList.add('visto'); });
      return;
    }
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('visto'); io.unobserve(e.target); }
      });
    }, { threshold: 0.3 });
    barras.forEach(function (b) { io.observe(b); });
  }

  function init() {
    var casos = document.getElementById('exCasos');
    if (!casos) return;
    if (!FICHAS.length) {
      casos.innerHTML = '<p class="ex-nota">' + chip('pendiente') + ' La base no trae la colección de expedientes.</p>';
      return;
    }
    var hay = {};
    FICHAS.forEach(function (f) { hay[f.categoria] = true; });
    document.getElementById('exChips').innerHTML = CATEGORIAS.filter(function (c) { return c[0] === 'todos' || hay[c[0]]; })
      .map(function (c) { return '<button type="button" data-cat="' + c[0] + '" aria-pressed="false">' + c[1] + '</button>'; }).join('');
    document.getElementById('exIndice').innerHTML = FICHAS.map(function (f, i) { return tarjeta(f, i + 1); }).join('');
    casos.innerHTML = FICHAS.map(function (f, i) { return caso(f, i + 1); }).join('') +
      (E.consulta ? '<p class="ex-nota ex-consulta">Informes consultados el ' + esc(E.consulta) + '.</p>' : '');
    filtrar('todos');
    animarBarras();

    document.getElementById('exChips').addEventListener('click', function (ev) {
      var b = ev.target.closest('button[data-cat]');
      if (b) filtrar(b.getAttribute('data-cat'));
    });
    document.addEventListener('click', function (ev) {
      var cp = ev.target.closest('[data-copiar]');
      if (cp) { copiar(cp.getAttribute('data-copiar')); return; }
      var a = ev.target.closest('a[href^="#"]');
      if (!a) return;
      var id = a.getAttribute('href').slice(1);
      if (!id || !document.getElementById(id)) return;
      ev.preventDefault();
      history.replaceState(null, '', '#' + id);
      irA(id, true);
    });
    window.addEventListener('hashchange', function () { irA(location.hash.slice(1), true); });
    /* Al llegar con #exp-<id>: apartados.js corrige el salto a los 350 ms
       de cargar; este va despues, sin animacion, y resalta el caso. */
    if (location.hash.length > 1) {
      var llegar = function () { setTimeout(function () { irA(decodeURIComponent(location.hash.slice(1)), false); }, 420); };
      if (document.readyState === 'complete') llegar(); else window.addEventListener('load', llegar);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
