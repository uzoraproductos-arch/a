/* Auditavisión · Costo Ambiental › Auditor ambiental (aplicación 5,
   22-10-2026). La página la escribe herramientas/am_auditor.py con todas
   las fichas y sus cifras; aquí solo se cambia de ficha, se arma el CSV de
   la ficha a la vista y se copia su enlace (#aa-<ur>). No calcula cifras.
   Prefijo: aa-. */
(function () {
  'use strict';

  var raiz = document.getElementById('aaRaiz');
  if (!raiz) return;
  var D;
  try { D = JSON.parse(document.getElementById('aaDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  var botones = Array.prototype.slice.call(raiz.querySelectorAll('.aa-org'));
  var fichas = Array.prototype.slice.call(raiz.querySelectorAll('.aa-ficha'));
  var actual = 'RAMO';

  function ver(ur, foco) {
    if (!D[ur]) return;
    actual = ur;
    botones.forEach(function (b) {
      var on = b.getAttribute('data-ur') === ur;
      b.setAttribute('aria-checked', on ? 'true' : 'false');
      b.tabIndex = on ? 0 : -1;
    });
    fichas.forEach(function (f) { f.hidden = f.getAttribute('data-ur') !== ur; });
    $('aaCopiado').textContent = '';
    try { history.replaceState(null, '', location.pathname + location.search + '#aa-' + ur); } catch (e) { /* sin historial */ }
    if (foco) {
      var f = $('aa-' + ur);
      if (f && f.scrollIntoView) f.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  botones.forEach(function (b, i) {
    b.addEventListener('click', function () { ver(b.getAttribute('data-ur'), true); });
    b.addEventListener('keydown', function (e) {
      var k = e.key, j = i;
      if (k === 'ArrowRight' || k === 'ArrowDown') j = (i + 1) % botones.length;
      else if (k === 'ArrowLeft' || k === 'ArrowUp') j = (i - 1 + botones.length) % botones.length;
      else return;
      e.preventDefault();
      botones[j].focus();
      ver(botones[j].getAttribute('data-ur'), false);
    });
  });

  $('aaCsv').addEventListener('click', function () {
    var c = function (v) { return '"' + String(v).replace(/"/g, '""') + '"'; };
    var d = D[actual];
    var filas = [['Concepto', 'Valor', 'Estado', 'Fuente']].concat(d.f);
    var txt = '﻿' + c('Auditavisión · Auditor ambiental · ' + d.n) + '\r\n' +
      filas.map(function (f) { return f.map(c).join(','); }).join('\r\n');
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([txt], { type: 'text/csv;charset=utf-8' }));
    a.download = 'auditavision-auditor-ambiental-' + actual.toLowerCase() + '.csv';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  });

  $('aaLiga').addEventListener('click', function () {
    var url = location.href.split('#')[0] + '#aa-' + actual;
    var ok = function () { $('aaCopiado').textContent = '✓ Enlace copiado: ' + url; };
    var no = function () { $('aaCopiado').textContent = url; };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(ok, no);
      else no();
    } catch (e) { no(); }
  });

  var m = /^#aa-([A-Z0-9]+)$/.exec(location.hash || '');
  ver(m && D[m[1]] ? m[1] : 'RAMO', false);
})();
