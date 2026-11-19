/* Auditavisión · Modo Inspector › ¿Cumples con tus papeles? (19-11-2026).
   La página la escribe herramientas/insp_cumplimiento.py con sus preguntas en #cuDatos.
   Aquí solo se cuentan las respuestas (gemela de resumen() en Python; --prueba las compara).
   Nada se guarda ni se envía. AuditorCumple.resumen() se expone para las pruebas. */
(function () {
  'use strict';

  /* preguntas: [{id, area, quien}]; perfil: lista de claves; resp: {id: 'si'|'no'|'nose'}. */
  function resumen(preguntas, perfil, resp) {
    var tiene = {};
    (perfil || []).forEach(function (k) { tiene[k] = true; });
    var out = { aplican: 0, si: 0, no: 0, nose: 0, sin: 0, areas: {}, falta: [] };
    preguntas.forEach(function (p) {
      if (p.quien !== 'todos' && !tiene[p.quien]) return;
      var r = resp[p.id], k = (r === 'si' || r === 'no' || r === 'nose') ? r : 'sin';
      out.aplican += 1;
      out[k] += 1;
      var a = out.areas[p.area] || (out.areas[p.area] = { aplican: 0, si: 0 });
      a.aplican += 1;
      if (k === 'si') a.si += 1;
      else if (k === 'no' || k === 'nose') out.falta.push([p.id, k]);
    });
    return out;
  }

  window.AuditorCumple = { resumen: resumen };

  if (typeof document.getElementById !== 'function') return;
  var raiz = document.getElementById('cuRaiz');
  if (!raiz) return;
  var D = JSON.parse(document.getElementById('cuDatos').textContent);
  var $ = function (id) { return document.getElementById(id); };

  /* Lo que llega por la dirección (?p=moral,patron), para que el chat abra con el perfil puesto. */
  try {
    (new URLSearchParams(location.search).get('p') || '').split(',').forEach(function (k) {
      var c = raiz.querySelector('input[name="cuP"][value="' + k + '"]');
      if (c) c.checked = true;
    });
  } catch (e) { /* sin parámetros */ }

  function perfil() {
    var p = [];
    raiz.querySelectorAll('input[name="cuP"]').forEach(function (c) { if (c.checked) p.push(c.value); });
    return p;
  }
  /* Solo se ven las preguntas que te tocan; un área sin preguntas se esconde. */
  function muestra() {
    var t = { todos: true };
    perfil().forEach(function (k) { t[k] = true; });
    raiz.querySelectorAll('.cu-q').forEach(function (li) { li.hidden = !t[li.getAttribute('data-q')]; });
    raiz.querySelectorAll('.cu-area').forEach(function (f) { f.hidden = !f.querySelector('.cu-q:not([hidden])'); });
  }
  function respuestas() {
    var r = {};
    raiz.querySelectorAll('.cu-q input[type=radio]:checked').forEach(function (i) { r[i.name.slice(3)] = i.value; });
    return r;
  }

  function pinta(e) {
    if (e) e.preventDefault();
    var s = resumen(D.preguntas, perfil(), respuestas());
    var h = '<p class="ci-cifra">Contestaste «sí» a <b>' + s.si + ' de ' + s.aplican + '</b> obligaciones que te tocan</p>';
    var partes = [];
    if (s.no) partes.push(s.no + ' con «no»');
    if (s.nose) partes.push(s.nose + ' con «no sé»');
    if (s.sin) partes.push(s.sin + ' sin contestar');
    h += partes.length ? '<p>' + partes.join(', ') + '. Abajo va lo que falta, cada cosa con su artículo y qué hacer.</p>'
      : '<p>Todo lo que te toca, al corriente según tus respuestas. Para que valga, cada «sí» tiene que poder enseñarse con un documento.</p>';
    $('cuTotal').innerHTML = h;
    $('cuAreas').innerHTML = D.areas.filter(function (a) { return s.areas[a[0]]; }).map(function (a) {
      var x = s.areas[a[0]], pct = Math.round(100 * x.si / x.aplican);
      return '<tr><th scope="row"><span aria-hidden="true">' + a[1] + '</span> ' + a[2] + '</th><td><b>' + x.si + ' de ' + x.aplican + '</b></td>' +
        '<td><span class="cu-barra" role="img" aria-label="' + x.si + ' de ' + x.aplican + '"><span style="width:' + pct + '%"></span></span></td></tr>';
    }).join('');
    $('cuFalta').innerHTML = s.falta.length ? s.falta.map(function (f) {
      var li = $('cu-' + f[0]);
      var q = li.querySelector('.cu-preg').textContent, ley = li.querySelector('summary a').outerHTML,
        falta = li.querySelector('.cu-falta').innerHTML, app = li.querySelector('.cu-app');
      return '<li><span class="cu-et cu-et-' + f[1] + '">' + (f[1] === 'no' ? 'No' : 'No sé') + '</span> <b>' + q + '</b> ' +
        '<span class="cs-ley">(' + ley + ')</span><br>' + falta + (app ? ' ' + app.innerHTML : '') + '</li>';
    }).join('') : '<li>Nada con «no» ni «no sé».</li>';
    var r = respuestas(), lr = Object.keys(r).map(function (k) { return k + '.' + r[k]; }).join(',');
    $('cuMatriz').href = 'herramienta-inspector-riesgos.html?p=' + encodeURIComponent(perfil().join(',')) + '&r=' + encodeURIComponent(lr);
    $('cuRes').hidden = false;
    $('cuRes').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  raiz.querySelectorAll('input[name="cuP"]').forEach(function (c) { c.addEventListener('change', muestra); });
  muestra();
  $('cuForm').addEventListener('submit', pinta);
  $('cuImprime').addEventListener('click', function () { window.print(); });
})();
