/* Nepotismo y cargos públicos (nepotismo-y-cargos-publicos.html, 28-10-2026).
   La calculadora de parentesco: lee la tabla que escribe
   herramientas/nepotismo.py (alcance()) y dice qué grado es y qué ley lo
   alcanza. No busca a nadie y no guarda nada. Acepta ?rel=<id> para que el
   Auditor llegue con el parentesco ya elegido. */
(function () {
  'use strict';
  var sel = document.getElementById('nepRel'), res = document.getElementById('nepRes'), el = document.getElementById('nepDatos');
  if (!sel || !res || !el) return;
  var D;
  try { D = JSON.parse(el.textContent); } catch (e) { return; }
  var MARCA = { si: ['✅', 'Sí lo alcanza'], no: ['➖', 'No lo alcanza'], quiza: ['⚠️', 'Depende'] };
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function tipo(p) {
    if (p.t === 'cons') return 'Consanguinidad · línea ' + p.l + ' · ' + D.o[p.g] + ' grado';
    if (p.t === 'afin') return 'Afinidad · línea ' + p.l + ' · ' + D.o[p.g] + ' grado';
    if (p.t === 'vinc') return 'Vínculo de pareja, no parentesco';
    return 'Sin parentesco para la ley';
  }
  function pintar() {
    var p = null;
    for (var k = 0; k < D.p.length; k++) if (D.p[k].id === sel.value) p = D.p[k];
    if (!p) { res.innerHTML = ''; return; }
    res.innerHTML = '<div class="nep-res-cab"><b>' + esc(p.n) + '</b><span>' + esc(tipo(p)) + '</span><p>' + esc(p.x) + '</p></div>' +
      '<ul class="nep-res-leyes">' + D.l.map(function (l) {
        var r = p.r[l.k], m = MARCA[r];
        return '<li class="nep-r-' + r + '"><span class="nep-r-m" aria-hidden="true">' + m[0] + '</span><div><b>' + esc(l.n) + ': ' + m[1].toLowerCase() + '</b>' +
          '<small>' + esc(l.d) + ' <a href="' + esc(l.u) + '" target="_blank" rel="noopener">' + esc(l.a) + ' ↗</a></small>' +
          (r === 'quiza' && D.q[l.k] ? '<small>' + esc(D.q[l.k]) + '</small>' : '') + '</div></li>';
      }).join('') + '</ul>' +
      '<p class="nep-res-pie">Que la ley alcance a un parentesco no quiere decir que haya falta: tiene que haber un nombramiento, un contrato o una candidatura, y lo decide la autoridad.</p>';
  }
  sel.addEventListener('change', pintar);
  var q = '';
  try { q = new URLSearchParams(location.search).get('rel') || ''; } catch (e) { q = ''; }
  if (q) { sel.value = q; pintar(); }
})();
