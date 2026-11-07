/* Vigía legislativo (marco-legal-tres-niveles.html#reformas-recientes, 05-11-2026).
   Pinta lo que junta herramientas/vigia_legislativo.py en
   docs/legislativo/bandeja.json: las publicaciones del DOF y los cambios del
   índice de la Cámara de Diputados que tocan las leyes del dinero, todas
   «sin verificar» hasta su cotejo, y los avisos de los módulos de la
   plataforma que citan una reforma anterior a la vigente. Solo título, fecha
   y liga: el texto de la reforma se lee en su documento. */
(function () {
  'use strict';
  var el = document.getElementById('vigiaLegislativo');
  if (!el || !window.fetch) return;
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function liga(u, t) {
    return '<a href="' + esc(u) + '" target="_blank" rel="noopener noreferrer">' + esc(t) + ' ↗</a>';
  }
  var FUENTE = { dof: 'Diario Oficial de la Federación', diputados: 'Cámara de Diputados, Leyes Federales Vigentes' };
  fetch(el.getAttribute('data-bandeja'), { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (b) {
    if (!b) return;
    var h = (b.hallazgos || []).slice(0, 30), av = b.avisos || [];
    var out = '<p class="pa-chico">Revisado por última vez el ' + esc(b.actualizado) + '. ' +
      (h.length ? h.length + ' publicaciones por cotejar.' : 'Sin publicaciones nuevas que toquen las leyes vigiladas.') + '</p>';
    if (h.length) {
      out += '<ol class="leg-leyes vig-lista">' + h.map(function (x) {
        return '<li><span class="vig-sinv">Por cotejar</span> ' + liga(x.liga, x.titulo) +
          '<small>' + esc(FUENTE[x.fuente] || x.fuente) + (x.fecha ? ' · ' + esc(x.fecha) : '') +
          (x.articulos ? ' · artículos ' + esc(x.articulos) : '') + ' · lo vimos el ' + esc(x.visto) + '</small></li>';
      }).join('') + '</ol>';
    }
    var viejas = av.filter(function (a) { return a.tipo === 'vieja'; }), otras = av.filter(function (a) { return a.tipo !== 'vieja'; });
    if (av.length) {
      out += '<h3 class="vig-sub">Lo que en Auditavisión quedó por actualizar</h3>' +
        '<p>Citamos estas leyes con una reforma distinta de la que hoy registra la Cámara de Diputados. Mientras se cotejan, manda el texto vigente.</p>' +
        '<ul class="leg-leyes">' + viejas.concat(otras).map(function (a) {
          return '<li><b>' + esc(a.nombre) + '</b>: citamos la reforma del ' + esc(a.cita) + '; ' +
            (a.tipo === 'vieja' ? 'ya hay una posterior, del ' : 'Diputados registra como última la del ') + esc(a.vigente) + '. ' +
            liga(a.liga, 'Texto vigente') + '<small>' + esc(a.archivo) + (a.renglon ? ', renglón ' + a.renglon : '') + '</small></li>';
        }).join('') + '</ul>';
    }
    el.innerHTML = out;
  }, function () { /* sin bandeja: queda el texto de la página */ });
})();
