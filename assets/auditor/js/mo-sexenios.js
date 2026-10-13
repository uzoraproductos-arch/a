/* Auditavisión · Inversión y Megaobras › Las obras de cada sexenio
   (aplicación 3, 13-10-2026). La página la escribe herramientas/
   mo_sexenios.py con las torres, las fichas y sus cifras ya puestas; en
   JSON (#mxDatos) van las 13 obras con su costo y su estado para que este
   archivo recalcule las torres y los resúmenes cuando el lector filtra por
   industria, con el mismo criterio que simObrasDe() del motor. No carga el
   motor ni la base. Prefijo: mx-. */
(function () {
  'use strict';

  var D;
  try { D = JSON.parse(document.getElementById('mxDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  var raiz = $('mxRaiz');
  if (!raiz) return;
  var CLAVE = 'av-mo-sexenios';
  var porK = {};
  D.sx.forEach(function (x) { porK[x.k] = x; });
  var est = { sec: 'todos', med: 'n', evaluado: false, sel: null, a: 'lopez-obrador', b: 'pena-nieto' };
  try {
    var g = JSON.parse(localStorage.getItem(CLAVE) || '{}');
    if (g.med === 'n' || g.med === 'real') est.med = g.med;
    if (g.sec && (g.sec === 'todos' || D.sec[g.sec])) est.sec = g.sec;
  } catch (e) { /* sin almacenamiento: valores de fábrica */ }
  function guardar() {
    try { localStorage.setItem(CLAVE, JSON.stringify({ med: est.med, sec: est.sec })); } catch (e) { /* nada */ }
  }
  var quieto = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function chip(e, pend) {
    return '<span class="est-chip est-' + e + '"' + (pend ? ' data-pend="' + esc(pend) + '"' : '') + '>' + e + '</span>';
  }
  function num(v) { return Number(v).toLocaleString('es-MX'); }
  /* simMdp() del motor, letra por letra. */
  function simMdp(n) {
    var a = Math.abs(n);
    if (a >= 1000000) return '$' + (n / 1000000).toFixed(2) + ' billones';
    if (a >= 1000) return '$' + num(Math.round(n / 100) / 10) + ' mil millones';
    return '$' + num(Math.round(n * 100) / 100) + ' millones';
  }
  function plural(n, s, p) { return n === 1 ? s : p; }

  /* simObrasDe(sector, clave): el nombre del presidente contiene la clave. */
  function obrasDe(sec, k) {
    return D.obras.filter(function (o) {
      if (sec !== 'todos' && o.sec !== sec) return false;
      if (k === 'todos') return true;
      return o.pres.toLowerCase().indexOf(porK[k].clave.toLowerCase()) > -1;
    });
  }
  function resumen(xs) {
    var r = { n: xs.length, real: 0, doc: 0, ndoc: 0, pen: 0, npen: 0, pend: [], nom: [], top: null };
    xs.forEach(function (o) {
      r.real += o.real;
      if (o.e === 'pendiente') { r.pen += o.real; r.npen++; r.pend.push('obra-' + o.id); r.nom.push(o.n); }
      else { r.doc += o.real; r.ndoc++; }
      if (!r.top || o.real > r.top.real) r.top = o;
    });
    return r;
  }
  /* Igual que res_html() de mo_sexenios.py. */
  function resHtml(r) {
    if (!r.n) return '<p class="mx-r-vacio">Sin obras de esta industria en este periodo.</p>';
    var h = '<div class="mx-r"><div><span>Obras</span><b>' + r.n + '</b></div>' +
      '<div><span>Costo registrado ' + chip(r.npen ? 'pendiente' : 'derivado', r.npen ? r.pend[0] : null) + '</span><b>' + simMdp(r.real) +
      '</b><small>Suma del costo registrado de ' + r.n + ' ' + plural(r.n, 'obra', 'obras') + '.</small></div>' +
      (r.ndoc
        ? '<div><span>Con documento ' + chip('derivado') + '</span><b>' + simMdp(r.doc) + '</b><small>Suma de ' + r.ndoc + ' ' +
          plural(r.ndoc, 'obra', 'obras') + ' con costo oficial o derivado.</small></div>'
        : '<div><span>Con documento</span><b>—</b><small>Ninguna obra de este periodo tiene su costo total en un documento oficial.</small></div>');
    if (r.npen) {
      h += '<div class="mx-r-pen"><span>Sin documento ' + chip('pendiente', r.pend[0]) + '</span><b>' + simMdp(r.pen) + '</b><small>' +
        esc(r.nom.join(', ')) + ': su costo total no tiene documento oficial todavía. Toca la etiqueta para ver por qué falta y a quién le toca publicarlo.</small></div>';
    }
    return h + '</div>';
  }

  /* ---------- Línea del tiempo ---------- */
  var torres = Array.prototype.slice.call(raiz.querySelectorAll('.mx-torre'));
  var anim = null;
  var REPOSO = '⚪ Periodos en reposo (0 obras / $0). Pulsa «Evaluar» para levantarlos desde cero.';
  var LISTO = '✓ Evaluación completada: los seis periodos a escala real.';

  function medidas() {
    var datos = D.sx.map(function (x) { return resumen(obrasDe(est.sec, x.k)); });
    var topeN = Math.max.apply(null, datos.map(function (r) { return r.n; })) || 1;
    var topeR = Math.max.apply(null, datos.map(function (r) { return r.real; })) || 1;
    return datos.map(function (r) {
      var f = est.med === 'n' ? r.n / topeN : r.real / topeR;
      /* Como el motor: una torre con obras nunca queda plana. */
      return { r: r, v: r.n === 0 ? 0 : 0.08 + 0.92 * f };
    });
  }
  function pintarTorres(e) {
    var m = medidas();
    torres.forEach(function (b, i) {
      var x = m[i], r = x.r;
      var barra = b.querySelector('.mx-t-barra');
      var nEl = b.querySelector('.mx-t-n');
      var cEl = b.querySelector('.mx-t-cif');
      b.disabled = r.n === 0;
      b.classList.toggle('mx-vacia', r.n === 0);
      barra.style.setProperty('--mx-v', (x.v * e).toFixed(4));
      nEl.textContent = Math.round(r.n * e);
      cEl.textContent = r.n === 0 ? 'sin obras aquí' : simMdp(r.real * e);
      b.querySelector('.mx-t-pen').hidden = !r.npen;
      var sx = D.sx[i];
      b.setAttribute('aria-label', sx.noml + ', ' + sx.ini + ' a ' + sx.fin + ': ' + r.n + ' ' + plural(r.n, 'obra', 'obras') +
        (r.n ? ', ' + simMdp(r.real) : ''));
    });
  }
  function evaluar() {
    if (anim) cancelAnimationFrame(anim);
    var btn = $('mxEvaluar');
    if (quieto) { terminar(); return; }
    $('mxEstado').textContent = '⚡ Levantando los seis periodos desde cero…';
    btn.innerHTML = '<span aria-hidden="true">⏳</span> Evaluando…';
    var ini = performance.now(), dur = 1400;
    function paso(t) {
      var a = Math.min(1, (t - ini) / dur);
      var e = (a - 1) * (a - 1) * (a - 1) + 1;
      pintarTorres(e);
      if (a < 1) anim = requestAnimationFrame(paso);
      else terminar();
    }
    anim = requestAnimationFrame(paso);
  }
  function terminar() {
    anim = null;
    est.evaluado = true;
    pintarTorres(1);
    $('mxEstado').textContent = LISTO;
    $('mxEstado').classList.add('mx-ok');
    $('mxEvaluar').innerHTML = '<span aria-hidden="true">🔄</span> Volver a evaluar';
  }
  function reiniciar() {
    if (anim) { cancelAnimationFrame(anim); anim = null; }
    est.evaluado = false;
    pintarTorres(0);
    $('mxEstado').textContent = REPOSO;
    $('mxEstado').classList.remove('mx-ok');
    $('mxEvaluar').innerHTML = '<span aria-hidden="true">▶️</span> Evaluar los seis sexenios';
  }

  /* ---------- Fichas por sexenio ---------- */
  var paneles = Array.prototype.slice.call(raiz.querySelectorAll('.mx-panel'));
  function pintarPaneles() {
    paneles.forEach(function (p) {
      var k = p.getAttribute('data-sx');
      var res = p.querySelector('.mx-p-res');
      if (res) res.innerHTML = resHtml(resumen(obrasDe(est.sec, k)));
      var vis = 0;
      p.querySelectorAll('.mx-obra').forEach(function (li) {
        var ok = est.sec === 'todos' || li.getAttribute('data-sector') === est.sec;
        li.hidden = !ok;
        if (ok) vis++;
      });
      var vac = p.querySelector('.mx-p-vacio');
      if (vac) vac.hidden = vis > 0;
    });
  }
  function seleccionar(k, mover) {
    if (!k || (k !== 'todos' && !porK[k])) k = 'todos';
    est.sel = k;
    paneles.forEach(function (p) { p.hidden = p.getAttribute('data-sx') !== k; });
    torres.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-sx') === k ? 'true' : 'false'); });
    raiz.querySelectorAll('.mx-chip').forEach(function (a) {
      if (a.getAttribute('data-sx') === k) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    });
    if (mover) {
      var p = $('sexenio-' + k);
      if (p) {
        p.scrollIntoView({ behavior: quieto ? 'auto' : 'smooth', block: 'start' });
        try { p.focus({ preventScroll: true }); } catch (e) { /* nada */ }
      }
    }
  }
  /* Las selecciones cambian el ancla sin sumar pasos al historial: la flecha
     Atrás sale de la página, como espera el lector. */
  function ancla(h) {
    try { history.replaceState(null, '', h); } catch (e) { /* nada */ }
  }

  /* ---------- Comparación ---------- */
  function filaBar(et, va, vb, txa, txb, ca, cb, chipA, chipB) {
    var m = Math.max(va, vb) || 1;
    return '<div class="mx-co-fila"><p class="mx-co-et">' + et + '</p>' +
      '<div class="mx-co-par">' +
        '<div class="mx-co-l"><span class="mx-co-v">' + txa + ' ' + (chipA || '') + '</span>' +
          '<span class="mx-co-pista"><span class="mx-co-b" style="--mx-c:' + ca + ';--mx-w:' + (va / m * 100).toFixed(1) + '%"></span></span></div>' +
        '<div class="mx-co-l"><span class="mx-co-v">' + txb + ' ' + (chipB || '') + '</span>' +
          '<span class="mx-co-pista"><span class="mx-co-b" style="--mx-c:' + cb + ';--mx-w:' + (vb / m * 100).toFixed(1) + '%"></span></span></div>' +
      '</div></div>';
  }
  function comparar(escribirAncla) {
    var A = porK[est.a], B = porK[est.b];
    $('mxCoA').value = est.a;
    $('mxCoB').value = est.b;
    var oa = obrasDe(est.sec, A.k), ob = obrasDe(est.sec, B.k);
    var ra = resumen(oa), rb = resumen(ob);
    var cab = '<div class="mx-co-cab"><span style="--mx-c:' + A.color + '">' + esc(A.noml) + ' <small>' + A.ini + '–' + A.fin + '</small></span>' +
      '<span style="--mx-c:' + B.color + '">' + esc(B.noml) + ' <small>' + B.ini + '–' + B.fin + '</small></span></div>';
    var h = '';
    if (A.k === B.k) h += '<p class="mx-co-nota">Elegiste el mismo sexenio dos veces: cambia uno de los dos para ver la diferencia.</p>';
    if (est.sec !== 'todos') h += '<p class="mx-co-nota">Solo cuenta las obras de <b>' + esc(D.sec[est.sec]) + '</b>, la industria que elegiste arriba.</p>';
    h += cab;
    h += filaBar('Obras', ra.n, rb.n, String(ra.n), String(rb.n), A.color, B.color);
    h += filaBar('Costo registrado', ra.real, rb.real, simMdp(ra.real), simMdp(rb.real), A.color, B.color,
      ra.n ? chip(ra.npen ? 'pendiente' : 'derivado', ra.npen ? ra.pend[0] : null) : '',
      rb.n ? chip(rb.npen ? 'pendiente' : 'derivado', rb.npen ? rb.pend[0] : null) : '');
    h += filaBar('Con documento', ra.doc, rb.doc, ra.ndoc ? simMdp(ra.doc) : '—', rb.ndoc ? simMdp(rb.doc) : '—', A.color, B.color,
      ra.ndoc ? chip('derivado') : '', rb.ndoc ? chip('derivado') : '');
    if (ra.npen || rb.npen) {
      h += filaBar('Sin documento', ra.pen, rb.pen, simMdp(ra.pen), simMdp(rb.pen), A.color, B.color,
        ra.npen ? chip('pendiente', ra.pend[0]) : '', rb.npen ? chip('pendiente', rb.pend[0]) : '');
    }
    function topTx(r) {
      if (!r.top) return '—';
      return esc(r.top.i + ' ' + r.top.n) + ': ' + simMdp(r.top.real) + ' ' + chip(r.top.e, r.top.e === 'pendiente' ? 'obra-' + r.top.id : null);
    }
    h += '<div class="mx-co-fila"><p class="mx-co-et">La obra más cara</p><div class="mx-co-par"><p class="mx-co-top">' + topTx(ra) +
      '</p><p class="mx-co-top">' + topTx(rb) + '</p></div></div>';

    /* La lectura, solo con la parte que tiene documento. */
    var lect;
    if (A.k === B.k) lect = '';
    else if (!ra.n || !rb.n) {
      lect = 'No hay comparación posible: ' + esc((!ra.n ? A : B).noml) + ' no tiene obras ' + (est.sec === 'todos' ? 'en este registro.' : 'de esta industria.');
    } else if (!ra.doc || !rb.doc) {
      lect = 'Con documento no se pueden comparar: ninguna obra de ' + esc((!ra.doc ? A : B).noml) +
        ' tiene su costo total en un documento oficial. Sus cifras siguen pendientes y no las estimamos.';
    } else {
      var mayor = ra.doc >= rb.doc ? ra : rb, menor = mayor === ra ? rb : ra;
      var MA = mayor === ra ? A : B, ME = mayor === ra ? B : A;
      var veces = mayor.doc / menor.doc;
      lect = 'Contando solo lo que tiene documento, las obras de <b>' + esc(MA.noml) + '</b> suman <b>' +
        veces.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' veces</b> lo de ' + esc(ME.noml) + ' ' + chip('derivado') +
        ' <small>(' + simMdp(mayor.doc) + ' ÷ ' + simMdp(menor.doc) + ', en pesos de cada año, sin quitar la inflación).</small>';
    }
    if (lect) h += '<p class="mx-co-lect">' + lect + '</p>';
    var comunes = oa.filter(function (o) { return ob.indexOf(o) > -1; });
    if (comunes.length && A.k !== B.k) {
      h += '<p class="mx-co-nota">↔️ <b>' + esc(comunes.map(function (o) { return o.n; }).join(', ')) +
        '</b> ' + plural(comunes.length, 'aparece', 'aparecen') + ' en los dos sexenios: su costo está en ambas columnas. <a href="#mxNota">Por qué</a>.</p>';
    }
    $('mxCoSalida').innerHTML = h;
    if (escribirAncla) ancla('#comparar-' + A.k + '-' + B.k);
  }

  /* ---------- Ancla ---------- */
  function leerAncla(mover) {
    var h = decodeURIComponent((location.hash || '').slice(1));
    var m = /^sexenio-(.+)$/.exec(h);
    if (m) { seleccionar(m[1], mover); return; }
    var c = /^comparar-(.+)$/.exec(h);
    if (c) {
      var ks = D.sx.map(function (x) { return x.k; });
      for (var i = 0; i < ks.length; i++) {
        var pre = ks[i] + '-';
        if (c[1].indexOf(pre) === 0 && porK[c[1].slice(pre.length)]) {
          est.a = ks[i]; est.b = c[1].slice(pre.length);
          comparar(false);
          if (mover) $('mxComparar').scrollIntoView({ block: 'start' });
          break;
        }
      }
    }
  }

  /* ---------- Eventos ---------- */
  function ponerSector(s) {
    est.sec = s;
    raiz.querySelectorAll('.mx-filtro').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-sec') === s ? 'true' : 'false');
    });
    pintarTorres(est.evaluado ? 1 : 0);
    if (!est.evaluado) evaluar();
    pintarPaneles();
    comparar(false);
    guardar();
  }
  raiz.querySelectorAll('.mx-filtro').forEach(function (b) {
    b.addEventListener('click', function () { ponerSector(b.getAttribute('data-sec')); });
  });
  raiz.querySelectorAll('.mx-med').forEach(function (b) {
    b.addEventListener('click', function () {
      est.med = b.getAttribute('data-med');
      raiz.querySelectorAll('.mx-med').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      guardar();
      evaluar();
    });
  });
  $('mxEvaluar').addEventListener('click', function () { evaluar(); });
  $('mxReiniciar').addEventListener('click', reiniciar);
  torres.forEach(function (b) {
    b.addEventListener('click', function () {
      var k = b.getAttribute('data-sx');
      seleccionar(k, true);
      ancla('#sexenio-' + k);
    });
  });
  raiz.querySelectorAll('.mx-chip').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      ev.preventDefault();
      var k = a.getAttribute('data-sx');
      seleccionar(k, false);
      ancla('#sexenio-' + k);
    });
  });
  $('mxCoA').addEventListener('change', function () { est.a = this.value; comparar(true); });
  $('mxCoB').addEventListener('change', function () { est.b = this.value; comparar(true); });
  $('mxCoInv').addEventListener('click', function () { var t = est.a; est.a = est.b; est.b = t; comparar(true); });
  $('mxCoCopiar').addEventListener('click', function () {
    var url = location.href.split('#')[0] + '#comparar-' + est.a + '-' + est.b;
    var ok = function () { $('mxCopiado').textContent = '✓ Enlace copiado'; };
    var falla = function () { $('mxCopiado').textContent = url; };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(ok, falla);
    else falla();
  });
  window.addEventListener('hashchange', function () { leerAncla(true); });

  /* ---------- Arranque ---------- */
  raiz.querySelectorAll('.mx-med').forEach(function (x) {
    x.setAttribute('aria-pressed', x.getAttribute('data-med') === est.med ? 'true' : 'false');
  });
  raiz.querySelectorAll('.mx-filtro').forEach(function (b) {
    b.setAttribute('aria-pressed', b.getAttribute('data-sec') === est.sec ? 'true' : 'false');
  });
  pintarTorres(0);
  pintarPaneles();
  seleccionar('todos', false);
  comparar(false);
  leerAncla(!!location.hash);
  /* La página abre ya contando: las torres suben solas una vez. */
  evaluar();
})();
