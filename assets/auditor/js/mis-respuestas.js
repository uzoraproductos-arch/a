/* Tus respuestas (mis-respuestas.html, 19-11-2026; herramientas/mis_respuestas.py).
   La página automatizada de lo que el lector le pidió al Auditor: se arma solo en su
   navegador con lo que el chat anotó (localStorage «av-caso», caso() de asistente.js),
   sus dictámenes («av-dics») y sus revisiones de Mi Auditavisión («av-mia»). Nada sale
   de aquí; la cotización se envía solo si el lector la manda. Nunca un monto. */
(function () {
  'use strict';
  var caja = document.getElementById('mr');
  if (!caja) return;
  var D = JSON.parse(document.getElementById('mrDatos').textContent);
  var CHAT = D.chat, DIC = 'herramienta-inspector-dictamen.html';
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  /* Solo ligas de la propia plataforma: una página .html con su ? y su #. */
  var propia = function (u) { return /^[a-z0-9][a-z0-9-]*\.html([?#][^\s<>"'\\]*)?$/i.test(String(u || '')); };
  var lee = function (k, vacio) {
    try { var x = JSON.parse(localStorage.getItem(k) || 'null'); return x == null ? vacio : x; } catch (e) { return vacio; }
  };
  var chat = function (q, modo) { return CHAT + '?q=' + encodeURIComponent(q) + (modo ? '&modo=' + encodeURIComponent(modo) : ''); };
  var cotiza = function (sid, preguntas) {
    var t = preguntas.slice(0, 3).join(' · ');
    return 'servicios-cotiza.html?servicio=' + encodeURIComponent(sid) + '&tema=' + encodeURIComponent(t.slice(0, 160)) +
      '&pregunta=' + encodeURIComponent(('Lo que le pregunté al Auditor: ' + preguntas.join(' / ')).slice(0, 1500)) + '#solicitud';
  };

  function pinta() {
    var c = lee('av-caso', []), dics = lee('av-dics', []), mia = lee('av-mia', {});
    c = Array.isArray(c) ? c.filter(function (x) { return x && x.q; }) : [];
    dics = Array.isArray(dics) ? dics.filter(function (x) { return x && x.q && /^\?/.test(x.u || ''); }) : [];
    var rev = (mia && Array.isArray(mia.rev)) ? mia.rev : [];
    var hay = c.length || dics.length || rev.length;
    $('mrVacio').hidden = !!hay;
    $('mrLleno').hidden = !hay;
    if (!hay) return;

    /* Los servicios para tu caso: de más a menos respuestas que los piden. */
    var cuenta = {}, orden = [];
    c.forEach(function (x) {
      (x.s || []).forEach(function (sid) {
        if (!D.srv[sid]) return;
        if (!cuenta[sid]) { cuenta[sid] = []; orden.push(sid); }
        if (cuenta[sid].indexOf(x.q) < 0) cuenta[sid].push(x.q);
      });
    });
    var sin = c.filter(function (x) { return x.sin; });
    if (sin.length && D.srv.expediente) {
      if (!cuenta.expediente) { cuenta.expediente = []; orden.push('expediente'); }
      sin.forEach(function (x) { if (cuenta.expediente.indexOf(x.q) < 0) cuenta.expediente.push(x.q); });
    }
    orden.sort(function (a, b) { return cuenta[b].length - cuenta[a].length || orden.indexOf(a) - orden.indexOf(b); });

    var temas = {};
    c.forEach(function (x) { if (x.ir && x.ir[1]) temas[x.ir[1]] = 1; });
    $('mrCifras').innerHTML = [
      [c.length - sin.length, c.length - sin.length === 1 ? 'respuesta' : 'respuestas'],
      [sin.length, sin.length === 1 ? 'solicitud sin respuesta' : 'solicitudes sin respuesta'],
      [Object.keys(temas).length, Object.keys(temas).length === 1 ? 'página a fondo' : 'páginas a fondo'],
      [orden.length, orden.length === 1 ? 'servicio para tu caso' : 'servicios para tu caso'],
      [dics.length, dics.length === 1 ? 'dictamen' : 'dictámenes']
    ].map(function (x) { return '<li><b class="num-tabular">' + x[0] + '</b><span>' + x[1] + '</span></li>'; }).join('');

    $('mrSrv').innerHTML = orden.length ? orden.map(function (sid) {
      var s = D.srv[sid], qs = cuenta[sid];
      return '<li><a class="mr-srv-n" href="' + esc(s[3]) + '"><span aria-hidden="true">' + s[0] + '</span> <b>' + esc(s[1]) + '</b></a>' +
        '<small>' + esc(s[2]) + '</small>' +
        '<span class="mr-srv-por">Viene a ' + (qs.length === 1 ? '1 de tus preguntas' : qs.length + ' de tus preguntas') + ': «' + esc(qs[0]) + '»' + (qs.length > 1 ? ' y ' + (qs.length - 1) + ' más' : '') + '</span>' +
        '<a class="mr-btn" href="' + esc(cotiza(sid, qs)) + '">Pide una cotización con tus preguntas ➔</a></li>';
    }).join('') : '<li class="mr-nada">Ninguna de tus respuestas llevó a una página que un servicio aproveche. Si quieres ir más a fondo, mira <a href="servicios.html">todos los servicios</a>.</li>';

    $('mrLista').innerHTML = c.map(function (x, i) {
      var m = D.modos[x.m], ir = x.ir && propia(x.ir[0]) ? x.ir : null;
      var srv = (x.s || []).filter(function (sid) { return D.srv[sid]; });
      return '<li class="mr-q' + (x.sin ? ' mr-q-sin' : '') + '">' +
        '<p class="mr-q-de">' + esc(x.f || '') + (m ? ' · <span aria-hidden="true">' + m[0] + '</span> Modo ' + esc(m[1]) : '') + (x.sin ? ' · <b>Sin respuesta todavía</b>' : '') + '</p>' +
        '<h3 class="mr-q-t">' + esc(x.q) + '</h3>' +
        (x.sin ? '<p>El Auditor no lo encontró en la base. Puedes pedirlo como investigación: va a la lista de lo que falta y, si lo aceptamos, a su expediente.</p>'
               : (x.t ? '<p class="mr-q-r">' + esc(x.t) + '</p>' : '')) +
        '<p class="mr-q-acc">' +
          '<a class="mr-btn" href="' + esc(chat(x.q, x.m)) + '">💬 Volver a preguntar</a>' +
          (ir ? '<a class="mr-btn mr-btn-of" href="' + esc(ir[0]) + '">📖 Saber más · ' + esc(ir[1] || '') + '</a>' : '') +
          (x.d && /^herramienta-inspector-dictamen\.html\?/.test(x.d) ? '<a class="mr-btn mr-btn-of" href="' + esc(x.d) + '" target="_blank" rel="noopener">🧾 Generar dictamen</a>' : '') +
          (x.sin && D.srv.expediente ? '<a class="mr-btn mr-btn-of" href="' + esc(cotiza('expediente', [x.q])) + '">📂 Pídelo como investigación</a>' : '') +
          '<button type="button" class="mr-btn mr-btn-of" data-quita="' + i + '">Quitar</button>' +
        '</p>' +
        (srv.length ? '<p class="mr-q-srv"><span aria-hidden="true">🧰</span> También como servicio: ' + srv.map(function (sid) {
          return '<a href="' + esc(D.srv[sid][3]) + '">' + esc(D.srv[sid][1]) + '</a>';
        }).join(' · ') + '</p>' : '') +
        '</li>';
    }).join('') || '<li class="mr-nada">Aún no hay preguntas guardadas. <a href="' + esc(CHAT) + '">Pregúntale al Auditor</a>.</li>';

    $('mrDics').innerHTML =
      (dics.length ? '<p class="mr-nota">Los que generaste en el chat y tocan una investigación, con su folio.</p><ol class="mr-dics">' + dics.map(function (x) {
        return '<li><a href="' + esc(DIC + x.u) + '" target="_blank" rel="noopener"><span>' + esc((x.fo ? x.fo + ' · ' : '') + (x.f || '')) + '</span>' + esc(x.q) + ' ➔</a>' +
          (propia(x.ex) ? ' <a class="mr-chico" href="' + esc(x.ex) + '">Ver su expediente</a>' : '') + '</li>';
      }).join('') + '</ol>' : '<p class="mr-nota">Todavía no generas un dictamen que toque una investigación. Cada respuesta con datos trae su botón «🧾 Generar dictamen».</p>') +
      (rev.length ? '<p class="mr-nota"><b>Tus revisiones en Mi Auditavisión:</b> ' + rev.length + (rev.length === 1 ? ' guardada' : ' guardadas') +
        ' (facturas y estados de resultados). <a href="herramienta-inspector-mia.html">Ábrelas en Mi Auditavisión ➔</a></p>' : '');

    Array.prototype.forEach.call(caja.querySelectorAll('[data-quita]'), function (b) {
      b.addEventListener('click', function () {
        var l = lee('av-caso', []), q = c[+b.getAttribute('data-quita')].q;
        try { localStorage.setItem('av-caso', JSON.stringify((Array.isArray(l) ? l : []).filter(function (x) { return x && x.q !== q; }))); } catch (e) { /* nada */ }
        pinta();
      });
    });
    return { c: c, orden: orden, cuenta: cuenta, dics: dics };
  }

  var hoy = pinta();
  $('mrImprime').addEventListener('click', function () { window.print(); });
  $('mrBaja').addEventListener('click', function () {
    var x = pinta() || hoy;
    if (!x) return;
    var t = ['Tus respuestas del Auditor · Auditavisión', 'Se armó en tu navegador; no es un documento oficial.', ''];
    x.c.forEach(function (y) {
      t.push('• ' + y.q + (y.f ? ' (' + y.f + ')' : ''));
      t.push('  ' + (y.sin ? 'Sin respuesta todavía.' : (y.t || '')));
      if (y.ir) t.push('  Saber más: ' + location.origin + location.pathname.replace(/[^/]*$/, '') + y.ir[0]);
      t.push('');
    });
    if (x.orden.length) {
      t.push('Servicios para tu caso (la forma de cobro, nunca un monto):');
      x.orden.forEach(function (sid) { t.push('• ' + D.srv[sid][1] + ': ' + D.srv[sid][2]); });
    }
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([t.join('\n')], { type: 'text/plain;charset=utf-8' }));
    a.download = 'mis-respuestas-auditavision.txt';
    document.body.appendChild(a); a.click(); a.remove();
  });
  $('mrBorra').addEventListener('click', function () {
    if (!window.confirm('¿Borrar todas tus respuestas guardadas en este navegador? Tus dictámenes y Mi Auditavisión no se tocan.')) return;
    try { localStorage.removeItem('av-caso'); } catch (e) { /* nada */ }
    pinta();
  });
  /* Si el lector pregunta en otra pestaña, la página se pone al día sola. */
  window.addEventListener('storage', function (ev) { if (ev.key === 'av-caso' || ev.key === 'av-dics' || ev.key === 'av-mia') pinta(); });
})();
