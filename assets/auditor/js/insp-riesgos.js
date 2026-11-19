/* Auditavisión · Modo Inspector › Tu matriz de riesgos documentales (19-11-2026).
   La página la escribe herramientas/insp_riesgos.py con sus datos en #rgDatos.
   Aquí solo se acomodan las respuestas (gemela de matriz() en Python; --prueba las compara).
   Nada se guarda ni se envía. AuditorRiesgos.matriz() se expone para las pruebas. */
(function () {
  'use strict';

  var PROB = { no: 3, nose: 2, si: 1 };
  var ZONAS = [['alta', 6], ['media', 3], ['baja', 1]];
  function zona(p, g) {
    var s = p * g;
    for (var i = 0; i < ZONAS.length; i++) if (s >= ZONAS[i][1]) return ZONAS[i][0];
    return 'baja';
  }

  /* preguntas: [{id, area, quien}]; perfil: lista de claves; resp: {id: 'si'|'no'|'nose'}; grav: {id: 1|2|3}. */
  function matriz(preguntas, perfil, resp, grav) {
    var tiene = {};
    (perfil || []).forEach(function (k) { tiene[k] = true; });
    var out = { celdas: {}, orden: [], zonas: { alta: 0, media: 0, baja: 0 }, sinGrave: [], sinResp: [] };
    var filas = [];
    preguntas.forEach(function (p, n) {
      if (p.quien !== 'todos' && !tiene[p.quien]) return;
      var r = resp[p.id];
      if (!PROB.hasOwnProperty(r)) { out.sinResp.push(p.id); return; }
      var g = grav[p.id];
      if (g !== 1 && g !== 2 && g !== 3) { out.sinGrave.push(p.id); return; }
      filas.push([PROB[r] * g, g, n, p.id, PROB[r]]);
    });
    filas.sort(function (a, b) { return (b[0] - a[0]) || (b[1] - a[1]) || (a[2] - b[2]); });
    filas.forEach(function (f) {
      var z = zona(f[4], f[1]), k = f[4] + '-' + f[1];
      (out.celdas[k] || (out.celdas[k] = [])).push(f[3]);
      out.orden.push([f[3], f[4], f[1], z]);
      out.zonas[z] += 1;
    });
    return out;
  }

  window.AuditorRiesgos = { matriz: matriz };

  if (typeof document.getElementById !== 'function') return;
  var raiz = document.getElementById('rgRaiz');
  if (!raiz) return;
  var D = JSON.parse(document.getElementById('rgDatos').textContent);
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var ZI = {}; D.zonas.forEach(function (z) { ZI[z[0]] = z; });

  /* Lo que llega por la dirección: ?p=moral,patron&r=f_plazo.no,d_aviso.si&g=f_plazo.3 (el autodiagnóstico manda p y r). */
  function marca(nombre, valor) {
    var i = raiz.querySelector('input[name="' + nombre + '"][value="' + valor + '"]');
    if (i) i.checked = true;
  }
  try {
    var u = new URLSearchParams(location.search);
    (u.get('p') || '').split(',').forEach(function (k) { if (/^\w+$/.test(k)) marca('rgP', k); });
    (u.get('r') || '').split(',').forEach(function (x) { var a = x.split('.'); if (/^\w+$/.test(a[0]) && /^(si|no|nose)$/.test(a[1] || '')) marca('rg-r-' + a[0], a[1]); });
    (u.get('g') || '').split(',').forEach(function (x) { var a = x.split('.'); if (/^\w+$/.test(a[0]) && /^[123]$/.test(a[1] || '')) marca('rg-g-' + a[0], a[1]); });
  } catch (e) { /* sin parámetros */ }

  function perfil() {
    var p = [];
    raiz.querySelectorAll('input[name="rgP"]').forEach(function (c) { if (c.checked) p.push(c.value); });
    return p;
  }
  function muestra() {
    var t = { todos: true };
    perfil().forEach(function (k) { t[k] = true; });
    raiz.querySelectorAll('.rg-q').forEach(function (li) { li.hidden = !t[li.getAttribute('data-q')]; });
  }
  function leer(pref, num) {
    var r = {};
    raiz.querySelectorAll('.rg-q input[name^="' + pref + '"]:checked').forEach(function (i) {
      r[i.name.slice(pref.length)] = num ? Number(i.value) : i.value;
    });
    return r;
  }
  function nombre(id) { return esc(D.cortos[id] || id); }

  function pinta(e) {
    if (e) e.preventDefault();
    var m = matriz(D.preguntas, perfil(), leer('rg-r-'), leer('rg-g-', true));
    var n = m.orden.length;
    $('rgTotal').innerHTML = n
      ? '<p class="ci-cifra">Acomodaste <b>' + n + '</b> obligaciones: <b>' + m.zonas.alta + '</b> para atender primero, ' + m.zonas.media + ' después y ' + m.zonas.baja + ' para vigilar</p>'
      : '<p>Todavía no hay nada que acomodar: contesta cada obligación y elige qué tan grave sería fallar.</p>';
    var filas = '';
    [3, 2, 1].forEach(function (g) {
      filas += '<tr><th scope="row">Gravedad ' + ({ 3: 'alta', 2: 'media', 1: 'baja' })[g] + '</th>';
      [1, 2, 3].forEach(function (p) {
        var ids = m.celdas[p + '-' + g] || [], z = zona(p, g);
        filas += '<td class="rg-c rg-z-' + z + '"><span class="rg-num">' + ids.length + '</span>' +
          (ids.length ? '<ul>' + ids.map(function (i) { return '<li><a href="#rg-' + i + '">' + nombre(i) + '</a></li>'; }).join('') + '</ul>' : '') + '</td>';
      });
      filas += '</tr>';
    });
    $('rgMat').innerHTML = filas;
    $('rgOrden').innerHTML = n ? m.orden.map(function (o) {
      var z = ZI[o[3]];
      return '<li><span class="rg-et-z rg-z-' + o[3] + '">' + z[2] + ' ' + z[3] + '</span> <b>' + nombre(o[0]) + '</b> · probabilidad ' +
        ({ 1: 'baja', 2: 'media', 3: 'alta' })[o[1]] + ' × gravedad ' + ({ 1: 'baja', 2: 'media', 3: 'alta' })[o[2]] +
        ' = ' + (o[1] * o[2]) + ' · <a href="#rg-' + o[0] + '">qué dice la ley</a></li>';
    }).join('') : '<li>Nada acomodado todavía.</li>';
    var falta = '';
    if (m.sinGrave.length) falta += '<p class="ci-pista"><b>Te falta decir qué tan grave sería:</b> ' + m.sinGrave.map(nombre).join(' · ') + '.</p>';
    if (m.sinResp.length) falta += '<p class="ci-pista"><b>Sin contestar si la cumples:</b> ' + m.sinResp.map(nombre).join(' · ') + '.</p>';
    $('rgFalta').innerHTML = falta;
    $('rgRes').hidden = false;
    $('rgRes').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  raiz.querySelectorAll('input[name="rgP"]').forEach(function (c) { c.addEventListener('change', muestra); });
  muestra();
  $('rgForm').addEventListener('submit', pinta);
  $('rgImprime').addEventListener('click', function () { window.print(); });
})();
