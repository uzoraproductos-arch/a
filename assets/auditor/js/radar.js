/* Radar hacendario (radar-hacendario.html, 10-10-2026): cada administración
   con sus números. Ingresos, inversión, costo del gobierno, deuda y lo que
   quedó por aclarar ante la ASF, con su comparativa, el reloj de cada
   sexenio y el duelo entre dos administraciones.
   Las cifras llegan en el JSON #rdDatos, que arma herramientas/apartados.py
   (radar()) con window.AUDIT_DB: aquí no se escribe ninguna cifra. */
(function () {
  'use strict';
  var nodo = document.getElementById('rdDatos');
  if (!nodo) return;
  var D;
  try { D = JSON.parse(nodo.textContent); } catch (e) { return; }
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function num(v, d) { return v.toLocaleString('es-MX', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function fmt(v, u) {
    var s = v < 0 ? '−' : '', a = Math.abs(v);
    if (u === 'pib') return s + num(a, 1) + '% del PIB';
    if (u === 'pp') return (v > 0 ? '+' : s) + num(a, 1) + ' puntos del PIB';
    if (u === 'mdp') return s + (a >= 1e6 ? '$' + num(a / 1e6, 2) + ' billones' : '$' + num(a, 1) + ' mdp');
    if (u === 'seg') return s + '$' + num(a, 0) + ' por segundo';
    if (u === 'ent') return s + num(Math.round(a), 0);
    return String(v);
  }
  function corto(v, u) {
    var s = v < 0 ? '−' : '', a = Math.abs(v);
    if (u === 'pib') return s + num(a, 1) + '%';
    if (u === 'pp') return (v > 0 ? '+' : s) + num(a, 1);
    if (u === 'mdp') return s + (a >= 1e6 ? '$' + num(a / 1e6, 2) + ' bill.' : '$' + num(a / 1e3, 1) + ' mil mdp');
    if (u === 'seg') return s + '$' + num(a, 0);
    if (u === 'ent') return s + num(Math.round(a), 0);
    return String(v);
  }
  function chip(e, pid) {
    var t = (e === 'oficial' || e === 'pendiente') ? e : 'derivado';
    return '<span class="est-chip est-' + t + '"' + (pid ? ' data-pend="' + esc(pid) + '"' : '') + '>' + t + '</span>';
  }
  /* Sin dato: «pendiente» lleva a su ficha del Registro; lo que no aplica
     (la ASF no existía, no hay serie comparable) lo dice sin chip. */
  function sinDato(x) {
    if (x && x.na) return '<span class="rd-na">' + esc(x.et || 'no aplica') + '</span>';
    return chip('pendiente', x && x.pid);
  }
  function fuente(k) {
    var f = D.fuentes[k];
    return f ? '<a href="' + esc(f.url) + '" target="_blank" rel="noopener noreferrer">' + esc(f.corto) + ' ↗</a>' : '';
  }
  function fuentes(ks) { return (ks || []).map(fuente).filter(Boolean).join(' · '); }
  function adm(id) { for (var i = 0; i < D.admins.length; i++) if (D.admins[i].id === id) return D.admins[i]; return null; }
  function val(a, m) { return (D.valores[a] || {})[m] || { pend: 'Sin dato.' }; }
  function tieneV(x) { return x && typeof x.v === 'number'; }
  function segundos(a) { return (Date.UTC(a.a[1] + 1, 0, 1) - Date.UTC(a.a[0], 0, 1)) / 1000; }

  /* Un valor con su chip y su procedencia (se abre al tocar). */
  function celda(x, u, cls) {
    if (!tieneV(x)) {
      return '<span class="rd-v rd-v-pend ' + (cls || '') + '">' + sinDato(x) + '</span>' +
        '<span class="rd-motivo">' + esc((x && (x.pend || x.na)) || 'Sin dato.') + '</span>';
    }
    return '<span class="rd-v ' + (cls || '') + '">' + fmt(x.v, u) + '</span> ' + chip(x.est) +
      '<details class="rd-de"><summary>¿De dónde sale?</summary>' +
        (x.op ? '<p>' + esc(x.op) + '</p>' : '') + (x.nota ? '<p class="rd-nota">' + esc(x.nota) + '</p>' : '') +
        '<p class="rd-fte">📄 ' + fuentes(x.f) + '</p></details>';
  }

  /* ================= Tablero ================= */
  var est = { adm: D.inicial || D.admins[D.admins.length - 1].id, dim: D.dims[0].id, met: null };
  var raiz = document.getElementById('rdTablero');

  function pintaAdmins() {
    document.getElementById('rdAdmins').innerHTML = D.admins.map(function (a) {
      return '<button type="button" class="rd-admin" role="tab" aria-selected="' + (a.id === est.adm) + '" data-adm="' + a.id + '" style="--c:' + a.col + '">' +
        '<span class="rd-admin-ini" aria-hidden="true">' + esc(a.ini) + '</span>' +
        '<span class="rd-admin-tx"><b>' + esc(a.c) + '</b><small>' + a.a[0] + '–' + a.a[1] + (a.curso ? ' · en curso' : '') + '</small></span></button>';
    }).join('');
  }

  function pintaFicha() {
    var a = adm(est.adm);
    var h = '<div class="rd-ficha-cab" style="--c:' + a.col + '"><span class="rd-admin-ini rd-ini-xl" aria-hidden="true">' + esc(a.ini) + '</span>' +
      '<div><h3>' + esc(a.n) + '</h3><span>' + esc(a.periodo) + '</span>' + (a.aviso ? '<p class="rd-aviso-adm">' + esc(a.aviso) + '</p>' : '') + '</div></div>';
    h += '<div class="rd-kpis">' + D.dims.map(function (d) {
      var m = d.kpi, x = val(a.id, m), mm = D.metricas[m];
      var sub = d.kpi2 ? val(a.id, d.kpi2) : null;
      return '<button type="button" class="rd-kpi' + (d.id === est.dim ? ' rd-kpi-on' : '') + '" data-dim="' + d.id + '" data-tono="' + d.tono + '">' +
        '<span class="rd-kpi-cab"><span aria-hidden="true">' + d.ico + '</span> ' + esc(d.tit) + '</span>' +
        '<span class="rd-kpi-v">' + (tieneV(x) ? corto(x.v, mm.u) : '—') + '</span>' +
        '<span class="rd-kpi-u">' + (tieneV(x) ? esc(mm.kpi) : (x.na ? esc(x.et || 'no aplica') : 'pendiente') + ': toca para ver por qué') + '</span>' +
        (sub && tieneV(sub) ? '<span class="rd-kpi-sub">' + esc(D.metricas[d.kpi2].kpi2) + ': ' + corto(sub.v, D.metricas[d.kpi2].u) + '</span>' : '') +
      '</button>';
    }).join('') + '</div>';
    document.getElementById('rdFicha').innerHTML = h;
  }

  function pintaDim() {
    var d = D.dims.filter(function (x) { return x.id === est.dim; })[0];
    if (!est.met || d.metricas.indexOf(est.met) < 0) est.met = d.metricas[0];
    var a = adm(est.adm);
    var h = '<div class="rd-dim-cab"><h3><span aria-hidden="true">' + d.ico + '</span> ' + esc(d.tit) + '</h3><p>' + esc(d.que) + '</p></div>';
    h += '<div class="rd-mets" role="tablist" aria-label="Qué medir">' + d.metricas.map(function (m) {
      return '<button type="button" class="rd-met" role="tab" aria-selected="' + (m === est.met) + '" data-met="' + m + '">' + esc(D.metricas[m].tit) + '</button>';
    }).join('') + '</div>';

    /* Lo de la administración elegida en esta dimensión, con su procedencia. */
    h += '<div class="rd-detalle" style="--c:' + a.col + '"><p class="rd-detalle-tit">' + esc(a.c) + ', ' + a.a[0] + '–' + a.a[1] + '</p><dl>' +
      d.metricas.map(function (m) {
        return '<div><dt>' + esc(D.metricas[m].tit) + '</dt><dd>' + celda(val(a.id, m), D.metricas[m].u) + '</dd></div>';
      }).join('') + '</dl>';
    if (d.id === 'inversion' && D.obras[a.id] && D.obras[a.id].length) {
      h += '<p class="rd-obras-tit">🏗️ Megaobras de esta administración</p><ul class="rd-obras">' + D.obras[a.id].map(function (o) {
        return '<li><a href="herramienta-megaobras-sector.html">' + esc(o.n) + '</a>' +
          (typeof o.v === 'number' ? ' <span>' + fmt(o.v, 'mdp') + ' ' + chip(o.est) + '</span>' : ' ' + chip('pendiente')) + '</li>';
      }).join('') + '</ul><p class="rd-nota">Inversión real de cada obra según su ficha en el módulo de Megaobras, en pesos de su momento.</p>';
    }
    if (d.id === 'asf') {
      h += '<p class="rd-obras-tit"><a href="descarga-los-datos.html#ficha-asf">⚖️ Lo que encontró la ASF en la Cuenta Pública 2024, estado por estado ➔</a></p>';
    }
    h += '</div>';

    /* La comparativa de todas las administraciones. */
    var mm = D.metricas[est.met];
    var vals = D.admins.map(function (x) { return { a: x, x: val(x.id, est.met) }; });
    var max = 0;
    vals.forEach(function (o) { if (tieneV(o.x)) max = Math.max(max, Math.abs(o.x.v)); });
    h += '<div class="rd-comp"><p class="rd-comp-tit">Las administraciones, lado a lado: ' + esc(mm.tit) + '</p>' +
      (mm.ojo ? '<p class="rd-ojo">⚠️ ' + esc(mm.ojo) + '</p>' : '') + '<ol class="rd-barras">' +
      vals.map(function (o) {
        var w = tieneV(o.x) && max ? Math.max(2, Math.abs(o.x.v) / max * 100) : 0;
        return '<li class="' + (o.a.id === est.adm ? 'rd-bar-on' : '') + '" style="--c:' + o.a.col + '">' +
          '<button type="button" class="rd-bar-nom" data-adm="' + o.a.id + '">' + esc(o.a.c) + ' <small>' + (o.a.curso ? o.a.a[0] + ', en curso' : o.a.a[0] + '–' + String(o.a.a[1]).slice(2)) + '</small></button>' +
          '<span class="rd-bar-pista">' + (tieneV(o.x) ? '<span class="rd-bar" data-w="' + w + '"' + (o.x.v < 0 ? ' data-neg' : '') + '></span>' : '<span class="rd-bar-pend">' + sinDato(o.x) + '</span>') + '</span>' +
          '<span class="rd-bar-v">' + (tieneV(o.x) ? corto(o.x.v, mm.u) + ' ' + chip(o.x.est) : '') + '</span></li>';
      }).join('') + '</ol></div>';
    document.getElementById('rdDim').innerHTML = h;
    crecer(document.getElementById('rdDim'));
  }

  /* Las barras arrancan en cero y crecen. */
  function crecer(cont) {
    var bars = cont.querySelectorAll('.rd-bar');
    bars.forEach(function (b) { b.style.width = reduce ? b.getAttribute('data-w') + '%' : '0'; });
    if (reduce) return;
    requestAnimationFrame(function () { requestAnimationFrame(function () {
      bars.forEach(function (b) { b.style.width = b.getAttribute('data-w') + '%'; });
    }); });
  }

  function pintaTodo() { pintaAdmins(); pintaFicha(); pintaDim(); }

  if (raiz) {
    raiz.addEventListener('click', function (ev) {
      var b = ev.target.closest('button');
      if (!b || !raiz.contains(b)) return;
      if (b.hasAttribute('data-adm')) { est.adm = b.getAttribute('data-adm'); pintaTodo(); }
      else if (b.hasAttribute('data-dim')) {
        est.dim = b.getAttribute('data-dim'); est.met = null; pintaFicha(); pintaDim();
        var dim = document.getElementById('rdDim');
        var y = dim.getBoundingClientRect().top + window.scrollY - 110;
        if (dim.getBoundingClientRect().top > window.innerHeight * 0.6) window.scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
      }
      else if (b.hasAttribute('data-met')) { est.met = b.getAttribute('data-met'); pintaDim(); }
    });
    pintaTodo();
  }

  /* ================= El reloj de cada administración ================= */
  var reloj = document.getElementById('rdReloj');
  if (reloj) {
    var selA = document.getElementById('rdRelojAdm'), selM = document.getElementById('rdRelojMet');
    selA.innerHTML = D.admins.filter(function (a) { return !a.curso; }).map(function (a) {
      return '<option value="' + a.id + '">' + esc(a.c) + ' (' + a.a[0] + '–' + a.a[1] + ')</option>';
    }).join('');
    selA.value = D.admins.filter(function (a) { return !a.curso; }).slice(-1)[0].id;
    selM.innerHTML = D.reloj.map(function (r) { return '<option value="' + r.met + '">' + esc(r.tit) + '</option>'; }).join('');
    var t0 = null, acum = 0, timer = null;
    function tasa() {
      var a = adm(selA.value), r = D.reloj.filter(function (x) { return x.met === selM.value; })[0];
      var x = val(a.id, r.met);
      if (!tieneV(x)) return { pend: x, r: r, a: a };
      var porSeg = r.porSeg ? x.v : x.v * 1e6 / segundos(a);
      return { s: porSeg, r: r, a: a, x: x };
    }
    function pinta() {
      var t = tasa();
      var out = document.getElementById('rdRelojOut');
      if (t.pend) {
        out.innerHTML = '<p class="rd-reloj-pend">' + sinDato(t.pend) + ' ' + esc(t.pend.pend || t.pend.na || 'Sin dato.') + '</p>';
        document.getElementById('rdRelojCont').textContent = '—';
        return;
      }
      var seg = acum + (t0 ? (Date.now() - t0) / 1000 : 0);
      document.getElementById('rdRelojCont').textContent = '$' + num(t.s * seg, 0);
      document.getElementById('rdRelojSeg').textContent = num(Math.floor(seg), 0) + ' s';
      out.innerHTML = '<div class="rd-reloj-tasas">' +
        '<div><span>Por segundo</span><b>$' + num(t.s, 0) + '</b></div>' +
        '<div><span>Por hora</span><b>$' + num(t.s * 3600 / 1e6, 1) + ' mdp</b></div>' +
        '<div><span>Por día</span><b>$' + num(t.s * 86400 / 1e6, 1) + ' mdp</b></div></div>' +
        '<p class="rd-reloj-op">' + esc(t.r.op) + ' ' + chip('derivado') + '</p>' +
        '<p class="rd-fte">📄 ' + fuentes(t.x.f) + '</p>';
    }
    function corre(si) {
      var b = document.getElementById('rdRelojPlay');
      if (si) { t0 = Date.now(); timer = setInterval(pinta, 100); b.textContent = '⏸ Pausar'; b.setAttribute('aria-pressed', 'true'); }
      else { if (t0) acum += (Date.now() - t0) / 1000; t0 = null; clearInterval(timer); timer = null; b.textContent = '▶ Contabilizar'; b.setAttribute('aria-pressed', 'false'); }
      pinta();
    }
    reloj.addEventListener('click', function (ev) {
      var b = ev.target.closest('button');
      if (!b) return;
      if (b.id === 'rdRelojPlay') corre(!timer);
      if (b.id === 'rdRelojCero') { corre(false); acum = 0; pinta(); }
    });
    selA.addEventListener('change', function () { acum = 0; if (timer) { t0 = Date.now(); } pinta(); });
    selM.addEventListener('change', function () { acum = 0; if (timer) { t0 = Date.now(); } pinta(); });
    pinta();
  }

  /* ================= El duelo ================= */
  var duelo = document.getElementById('rdDuelo');
  if (duelo) {
    var s1 = document.getElementById('rdDuelo1'), s2 = document.getElementById('rdDuelo2');
    var ops = D.admins.map(function (a) { return '<option value="' + a.id + '">' + esc(a.c) + ' (' + a.a[0] + '–' + a.a[1] + ')</option>'; }).join('');
    s1.innerHTML = ops; s2.innerHTML = ops;
    var cerr = D.admins.filter(function (a) { return !a.curso; });
    s1.value = cerr[cerr.length - 2].id; s2.value = cerr[cerr.length - 1].id;
    function pintaDuelo() {
      var a = adm(s1.value), b = adm(s2.value);
      var filas = D.duelo.map(function (m) {
        var mm = D.metricas[m], x = val(a.id, m), y = val(b.id, m);
        var mx = Math.max(tieneV(x) ? Math.abs(x.v) : 0, tieneV(y) ? Math.abs(y.v) : 0) || 1;
        function lado(v, c, cls) {
          return '<div class="rd-du-lado ' + cls + '">' + (tieneV(v)
            ? '<span class="rd-du-v">' + corto(v.v, mm.u) + '</span><span class="rd-du-bar" style="--c:' + c + '" data-w="' + (Math.abs(v.v) / mx * 100) + '"><span class="rd-bar" data-w="' + (Math.abs(v.v) / mx * 100) + '"></span></span>'
            : '<span class="rd-du-pend">' + sinDato(v) + '</span>') + '</div>';
        }
        return '<div class="rd-du-fila"><p class="rd-du-tit">' + esc(mm.tit) + '</p>' + lado(x, a.col, 'rd-du-izq') + lado(y, b.col, 'rd-du-der') + '</div>';
      }).join('');
      document.getElementById('rdDueloOut').innerHTML =
        '<div class="rd-du-cab"><span style="--c:' + a.col + '">' + esc(a.c) + '</span><span class="rd-du-vs">vs</span><span style="--c:' + b.col + '">' + esc(b.c) + '</span></div>' + filas +
        '<p class="rd-nota">Sin ganador: más ingreso o más inversión no es por sí solo mejor, ni menos deuda peor. Los números dicen cuánto; el juicio es tuyo. Toca una administración arriba, en el tablero, para ver de dónde sale cada cifra.</p>';
      crecer(document.getElementById('rdDueloOut'));
    }
    s1.addEventListener('change', pintaDuelo); s2.addEventListener('change', pintaDuelo);
    pintaDuelo();
  }

  /* ================= Hoy: equivalencias durante la visita ================= */
  var hoy = document.querySelectorAll('[data-tasa]');
  if (hoy.length) {
    var h0 = Date.now();
    setInterval(function () {
      var s = (Date.now() - h0) / 1000;
      hoy.forEach(function (el) { el.textContent = '+$' + num(s * parseFloat(el.getAttribute('data-tasa')), 2); });
      var t = document.getElementById('rdHoyT');
      if (t) t.textContent = Math.floor(s / 60) + ':' + ('0' + Math.floor(s % 60)).slice(-2);
    }, 250);
  }
})();
