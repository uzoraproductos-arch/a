/* Los Expedientes de investigación (herramientas/expedientes_inv.py).
   Dos cosas: el buscador y los filtros del índice, y «En el radar»: los
   titulares del día que tocan el caso, leídos de la bandeja de la Mesa de
   redacción (docs/noticias/bandeja.json). Solo titular, medio, fecha y liga,
   rotulados «sin verificar»: un titular nunca es fuente. */
(function () {
  'use strict';
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function plano(s) {
    return ' ' + String(s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9ñ]+/g, ' ').trim() + ' ';
  }

  /* El índice: buscar y filtrar por estado. */
  var lista = document.getElementById('xiLista'), busca = document.getElementById('xiBusca');
  if (lista && busca) {
    var filtro = '', nada = document.getElementById('xiNada');
    var pinta = function () {
      var q = plano(busca.value).trim(), hay = 0;
      Array.prototype.forEach.call(lista.querySelectorAll('.xi-tarjeta'), function (t) {
        var ok = (!q || (' ' + t.getAttribute('data-xi-tx') + ' ').indexOf(q) >= 0) && (filtro === '' || t.getAttribute('data-xi-ab') === filtro);
        t.hidden = !ok;
        if (ok) hay++;
      });
      Array.prototype.forEach.call(lista.querySelectorAll('.xi-grupo'), function (g) {
        var r = g.nextElementSibling;
        g.hidden = r.hidden = !r.querySelector('.xi-tarjeta:not([hidden])');
      });
      if (nada) nada.hidden = hay > 0;
    };
    busca.addEventListener('input', pinta);
    Array.prototype.forEach.call(document.querySelectorAll('.xi-filtro'), function (b) {
      b.addEventListener('click', function () {
        filtro = b.getAttribute('data-xi-f');
        Array.prototype.forEach.call(document.querySelectorAll('.xi-filtro'), function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        pinta();
      });
    });
  }

  /* El radar de un expediente. */
  var radar = document.getElementById('xiRadar');
  if (!radar) return;
  var ks = [];
  try { ks = JSON.parse(radar.getAttribute('data-k')) || []; } catch (e) { ks = []; }
  var vacio = function (tx) { radar.innerHTML = '<p class="xi-vacio">' + tx + '</p>'; };
  if (!window.fetch) { vacio('Tu navegador no puede leer la recolección del día.'); return; }
  fetch(radar.getAttribute('data-bandeja'), { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (b) {
    var vistos = {}, notas = ((b && b.notas) || []).filter(function (x) {
      var t = plano(x.titulo), g = x.grupo || x.url;
      if (vistos[g] || !/^https?:\/\//.test(x.url || '')) return false;
      if (!ks.some(function (k) { return t.indexOf(' ' + k + ' ') >= 0; })) return false;
      vistos[g] = 1;
      return true;
    }).slice(0, 8);
    if (!notas.length) {
      vacio('La recolección' + (b && b.actualizado ? ' del ' + esc(b.actualizado) : '') + ' no trae titulares de este caso. Cuando aparezca uno, saldrá aquí solo.');
      return;
    }
    radar.innerHTML = '<span class="xi-sinver">Sin verificar · recolección del ' + esc(b.actualizado || 'día') + '</span><ol>' + notas.map(function (x) {
      return '<li><a href="' + esc(x.url) + '" target="_blank" rel="noopener noreferrer nofollow">' + esc(x.titulo) + ' ↗</a>' +
        '<small>' + esc(x.medio || '') + (x.fecha ? ' · ' + esc(x.fecha) : '') + '</small></li>';
    }).join('') + '</ol><p class="xi-chico">Son titulares de prensa: punto de partida, no fuente. Para cotejar uno, llévalo a <a href="noticias-verifica.html#verifica">Verifica una noticia</a>.</p>';
  }, function () { vacio('No se pudo leer la recolección del día. Vuelve a intentarlo más tarde.'); });
})();
