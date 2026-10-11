/* Radar hacendario (radar-*.html, 10-10-2026): cada administración
   con sus números. Ingresos, inversión, costo del gobierno, deuda y lo que
   quedó por aclarar ante la ASF, con su comparativa, el reloj de cada
   sexenio y el duelo entre dos administraciones. Las sumas en pesos se ven
   en pesos de cada año, en pesos de hoy, en dólares o en euros, y «El peso
   en el tiempo» grafica la inflación y el tipo de cambio con la proyección
   de Hacienda.
   Las cifras llegan en el JSON #rdDatos, que arma herramientas/apartados.py
   (radar()) con window.AUDIT_DB: aquí no se escribe ninguna cifra.
   Desde el 10-10-2026 cada parte vive en su página (radar-tablero.html,
   radar-peso.html, radar-reloj.html, radar-duelo.html y el «Hoy» de
   radar-estado-de-cuenta.html):
   cada bloque arranca solo si su página lo trae. */
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  /* ================= Hoy: el contador y las equivalencias ================= */
  /* Desde el 10-10-2026 (pedido del autor) las cifras de «Hoy» arrancan en
     cero y el botón «Contar» las lleva a su valor; el mismo botón las
     regresa a cero. «Durante tu visita» no corre hasta que se presiona.
     Las cifras siguen escritas completas en el HTML: aquí solo se animan. */
  var hoy = document.querySelectorAll('[data-tasa]');
  var vivo = document.getElementById('rdHoyVivo'), boton = document.getElementById('rdContar');
  var hTimer = null, h0 = 0, fmtH = new Intl.NumberFormat('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  function visita(si) {
    if (hTimer) { clearInterval(hTimer); hTimer = null; }
    hoy.forEach(function (el) { el.textContent = '+$0.00'; });
    var t = document.getElementById('rdHoyT');
    if (t) t.textContent = '0:00';
    if (!si) return;
    h0 = Date.now();
    hTimer = setInterval(function () {
      var s = (Date.now() - h0) / 1000;
      hoy.forEach(function (el) { el.textContent = '+$' + fmtH.format(s * parseFloat(el.getAttribute('data-tasa'))); });
      if (t) t.textContent = Math.floor(s / 60) + ':' + ('0' + Math.floor(s % 60)).slice(-2);
    }, 250);
  }
  if (boton && vivo) {
    /* Cada número de la cifra se vuelve un tramo que se anima por separado,
       con sus mismos decimales y separadores: «$1,572,073.3 mdp» cuenta de
       $0.0 a $1,572,073.3 y el texto de alrededor no cambia. */
    var tramos = [];
    document.querySelectorAll('.rd-hoy-c > b').forEach(function (b) {
      var txt = b.textContent, re = /\d[\d,]*(?:\.\d+)?/g, m, ult = 0, partes = [];
      while ((m = re.exec(txt))) {
        partes.push(document.createTextNode(txt.slice(ult, m.index)));
        var n = m[0], dec = n.indexOf('.') < 0 ? 0 : n.length - n.indexOf('.') - 1;
        var sp = document.createElement('span');
        sp.className = 'rd-num';
        tramos.push({ el: sp, v: parseFloat(n.replace(/,/g, '')), d: dec, miles: n.indexOf(',') >= 0 || n.replace(/\..*/, '').length > 4 });
        partes.push(sp);
        ult = m.index + n.length;
      }
      if (!partes.length) return;
      partes.push(document.createTextNode(txt.slice(ult)));
      b.textContent = '';
      partes.forEach(function (p) { b.appendChild(p); });
      b.setAttribute('aria-live', 'off');
    });
    function pon(tr, f) {
      tr.el.textContent = (tr.v * f).toLocaleString('en-US', { minimumFractionDigits: tr.d, maximumFractionDigits: tr.d, useGrouping: tr.miles });
    }
    var anim = null, contado = false, txt = document.getElementById('rdCuentaTxt'), candado = document.getElementById('rdCandado');
    function ceros() {
      if (anim) { cancelAnimationFrame(anim); anim = null; }
      contado = false;
      tramos.forEach(function (tr) { pon(tr, 0); });
      vivo.classList.add('rd-bloq');
      vivo.setAttribute('aria-disabled', 'true');
      candado.hidden = false;
      visita(false);
      boton.textContent = '▶ Contar';
      boton.setAttribute('aria-pressed', 'false');
      txt.textContent = 'Las cifras están en cero. Presiona «Contar» para verlas llegar a su valor oficial.';
    }
    function contar() {
      contado = true;
      boton.textContent = '↺ Reiniciar en ceros';
      boton.setAttribute('aria-pressed', 'true');
      txt.textContent = 'Contando… Cada cifra llega a su valor oficial; su fuente está debajo.';
      vivo.classList.remove('rd-bloq');
      vivo.removeAttribute('aria-disabled');
      candado.hidden = true;
      visita(true);
      var dur = reduce ? 0 : 2400, t0 = performance.now();
      function paso(ahora) {
        var x = dur ? Math.min(1, (ahora - t0) / dur) : 1, f = 1 - Math.pow(1 - x, 3);
        tramos.forEach(function (tr) { pon(tr, f); });
        if (x < 1) { anim = requestAnimationFrame(paso); return; }
        anim = null;
        txt.textContent = 'Listo: estas son las cifras de 2026, cada una con su fuente. «Reiniciar en ceros» las regresa al inicio.';
      }
      anim = requestAnimationFrame(paso);
    }
    boton.addEventListener('click', function () { if (contado) ceros(); else contar(); });
    document.getElementById('rdCuenta').hidden = false;
    ceros();
  } else if (hoy.length) {
    visita(true);
  }

  var nodo = document.getElementById('rdDatos');
  if (!nodo) return;
  var D;
  try { D = JSON.parse(nodo.textContent); } catch (e) { return; }

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function num(v, d) { return v.toLocaleString('es-MX', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  /* Signo de la moneda de una suma: pesos (de cada año o de hoy), dólares o euros. */
  var PRE = { nom: '$', hoy: '$', usd: 'US$', eur: '€' };
  function fmt(v, u, mon) {
    var s = v < 0 ? '−' : '', a = Math.abs(v), p = PRE[mon] || '$';
    if (u === 'mdp' && mon && mon !== 'nom') return s + (a >= 1e6 ? p + num(a / 1e6, 2) + ' billones' : p + num(a, 1) + ' millones');
    if (u === 'pib') return s + num(a, 1) + '% del PIB';
    if (u === 'pp') return (v > 0 ? '+' : s) + num(a, 1) + ' puntos del PIB';
    if (u === 'mdp') return s + (a >= 1e6 ? '$' + num(a / 1e6, 2) + ' billones' : '$' + num(a, 1) + ' mdp');
    if (u === 'seg') return s + '$' + num(a, 0) + ' por segundo';
    if (u === 'ent') return s + num(Math.round(a), 0);
    return String(v);
  }
  function corto(v, u, mon) {
    var s = v < 0 ? '−' : '', a = Math.abs(v), p = PRE[mon] || '$';
    if (u === 'mdp' && mon && mon !== 'nom') return s + (a >= 1e6 ? p + num(a / 1e6, 2) + ' bill.' : p + num(a / 1e3, 1) + ' mil mill.');
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
  /* El valor en la moneda elegida: las sumas en pesos traen sus conversiones en «alt». */
  function enMon(x, mon) { return (mon && mon !== 'nom' && x && x.alt) ? (x.alt[mon] || { pend: 'Sin dato.' }) : x; }
  function moneda(id) { for (var i = 0; i < D.monedas.length; i++) if (D.monedas[i].id === id) return D.monedas[i]; return D.monedas[0]; }
  function tieneV(x) { return x && typeof x.v === 'number'; }
  function segundos(a) { return (Date.UTC(a.a[1] + 1, 0, 1) - Date.UTC(a.a[0], 0, 1)) / 1000; }

  /* Un valor con su chip y su procedencia (se abre al tocar). */
  function celda(x, u, cls, mon) {
    if (!tieneV(x)) {
      return '<span class="rd-v rd-v-pend ' + (cls || '') + '">' + sinDato(x) + '</span>' +
        '<span class="rd-motivo">' + esc((x && (x.pend || x.na)) || 'Sin dato.') + '</span>';
    }
    return '<span class="rd-v ' + (cls || '') + '">' + fmt(x.v, u, mon) + '</span> ' + chip(x.est) +
      (x.pid ? ' ' + chip('pendiente', x.pid) : '') +
      '<details class="rd-de"><summary>¿De dónde sale?</summary>' +
        (x.op ? '<p>' + esc(x.op) + '</p>' : '') + (x.nota ? '<p class="rd-nota">' + esc(x.nota) + '</p>' : '') +
        '<p class="rd-fte">📄 ' + fuentes(x.f) + '</p></details>';
  }

  /* ================= Tablero ================= */
  var est = { adm: D.inicial || D.admins[D.admins.length - 1].id, dim: D.dims[0].id, met: null, mon: 'nom' };
  /* Selector de moneda para las sumas en pesos. */
  function selMon(actual, attr) {
    return '<div class="rd-mon" role="radiogroup" aria-label="En qué moneda ver las sumas">' + D.monedas.map(function (m) {
      return '<button type="button" role="radio" aria-checked="' + (m.id === actual) + '" ' + attr + '="' + m.id + '">' + esc(m.et) + '</button>';
    }).join('') + '</div>';
  }
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
      '<div><h3>' + esc(a.n) + '</h3><span>' + esc(a.periodo) + '</span>' + (a.aviso ? '<p class="rd-aviso-adm">' + esc(a.aviso) + '</p>' : '') + '</div>' +
      '<a class="rd-expide" href="radar-estado-de-cuenta.html?adm=' + a.id + '">🧾 Expide su estado de cuenta</a></div>';
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
        var mon = D.metricas[m].mon ? est.mon : null;
        return '<div><dt>' + esc(D.metricas[m].tit) + (mon ? ' <small>' + esc(moneda(mon).lee) + '</small>' : '') + '</dt><dd>' +
          celda(enMon(val(a.id, m), mon), D.metricas[m].u, '', mon) + '</dd></div>';
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
    var mon = mm.mon ? est.mon : null;
    var vals = D.admins.map(function (x) { return { a: x, x: enMon(val(x.id, est.met), mon) }; });
    var max = 0;
    vals.forEach(function (o) { if (tieneV(o.x)) max = Math.max(max, Math.abs(o.x.v)); });
    var ojo = mon ? moneda(mon).ojo : mm.ojo;
    h += '<div class="rd-comp"><p class="rd-comp-tit">Las administraciones, lado a lado: ' + esc(mm.tit) + (mon ? ', ' + esc(moneda(mon).lee) : '') + '</p>' +
      (mon ? selMon(mon, 'data-mon') : '') +
      (ojo ? '<p class="rd-ojo">⚠️ ' + esc(ojo) + '</p>' : '') + '<ol class="rd-barras">' +
      vals.map(function (o) {
        var w = tieneV(o.x) && max ? Math.max(2, Math.abs(o.x.v) / max * 100) : 0;
        return '<li class="' + (o.a.id === est.adm ? 'rd-bar-on' : '') + '" style="--c:' + o.a.col + '">' +
          '<button type="button" class="rd-bar-nom" data-adm="' + o.a.id + '">' + esc(o.a.c) + ' <small>' + (o.a.curso ? o.a.a[0] + ', en curso' : o.a.a[0] + '–' + String(o.a.a[1]).slice(2)) + '</small></button>' +
          '<span class="rd-bar-pista">' + (tieneV(o.x) ? '<span class="rd-bar" data-w="' + w + '"' + (o.x.v < 0 ? ' data-neg' : '') + '></span>' : '<span class="rd-bar-pend">' + sinDato(o.x) + '</span>') + '</span>' +
          '<span class="rd-bar-v">' + (tieneV(o.x) ? corto(o.x.v, mm.u, mon) + ' ' + chip(o.x.est) : '') + '</span></li>';
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
      else if (b.hasAttribute('data-mon')) { est.mon = b.getAttribute('data-mon'); pintaDim(); }
    });
    pintaTodo();
  }

  /* ================= El reloj de cada administración ================= */
  var reloj = document.getElementById('rdReloj');
  if (reloj) {
    var selA = document.getElementById('rdRelojAdm'), selM = document.getElementById('rdRelojMet'), selMo = document.getElementById('rdRelojMon');
    selMo.innerHTML = D.monedas.map(function (m) { return '<option value="' + m.id + '">' + esc(m.et) + '</option>'; }).join('');
    selA.innerHTML = D.admins.filter(function (a) { return !a.curso; }).map(function (a) {
      return '<option value="' + a.id + '">' + esc(a.c) + ' (' + a.a[0] + '–' + a.a[1] + ')</option>';
    }).join('');
    selA.value = D.admins.filter(function (a) { return !a.curso; }).slice(-1)[0].id;
    selM.innerHTML = D.reloj.map(function (r) { return '<option value="' + r.met + '">' + esc(r.tit) + '</option>'; }).join('');
    var t0 = null, acum = 0, timer = null;
    function tasa() {
      var a = adm(selA.value), r = D.reloj.filter(function (x) { return x.met === selM.value; })[0];
      var x0 = val(a.id, r.met);
      selMo.disabled = !x0.alt;
      var mon = x0.alt ? selMo.value : 'nom';
      var x = enMon(x0, mon);
      if (!tieneV(x)) return { pend: x, r: r, a: a };
      var porSeg = r.porSeg ? x.v : x.v * 1e6 / segundos(a);
      return { s: porSeg, r: r, a: a, x: x, mon: mon, solo: !x0.alt && tieneV(x0) };
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
      var p = PRE[t.mon] || '$', mi = t.mon === 'nom' ? ' mdp' : ' millones';
      document.getElementById('rdRelojCont').textContent = p + num(t.s * seg, 0);
      document.getElementById('rdRelojSeg').textContent = num(Math.floor(seg), 0) + ' s';
      out.innerHTML = '<div class="rd-reloj-tasas">' +
        '<div><span>Por segundo</span><b>' + p + num(t.s, 0) + '</b></div>' +
        '<div><span>Por hora</span><b>' + p + num(t.s * 3600 / 1e6, 1) + mi + '</b></div>' +
        '<div><span>Por día</span><b>' + p + num(t.s * 86400 / 1e6, 1) + mi + '</b></div></div>' +
        '<p class="rd-reloj-op">' + esc(t.r.op) + ' Moneda: ' + esc(t.solo ? 'pesos de cada año (esta medida no se convierte: es un saldo de deuda)' : moneda(t.mon).lee) + '. ' + chip('derivado') + '</p>' +
        (t.x.op ? '<details class="rd-de"><summary>¿De dónde sale la suma?</summary><p>' + esc(t.x.op) + '</p></details>' : '') +
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
    selMo.addEventListener('change', function () { acum = 0; if (timer) { t0 = Date.now(); } pinta(); });
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
      var filas = D.duelo.map(function (mk) {
        var m = mk.split(':')[0], mon = mk.split(':')[1] || null;
        var mm = D.metricas[m], x = enMon(val(a.id, m), mon), y = enMon(val(b.id, m), mon);
        var mx = Math.max(tieneV(x) ? Math.abs(x.v) : 0, tieneV(y) ? Math.abs(y.v) : 0) || 1;
        function lado(v, c, cls) {
          return '<div class="rd-du-lado ' + cls + '">' + (tieneV(v)
            ? '<span class="rd-du-v">' + corto(v.v, mm.u, mon) + '</span><span class="rd-du-bar" style="--c:' + c + '" data-w="' + (Math.abs(v.v) / mx * 100) + '"><span class="rd-bar" data-w="' + (Math.abs(v.v) / mx * 100) + '"></span></span>'
            : '<span class="rd-du-pend">' + sinDato(v) + '</span>') + '</div>';
        }
        return '<div class="rd-du-fila"><p class="rd-du-tit">' + esc(mm.tit) + (mon ? ', ' + esc(moneda(mon).et.toLowerCase()) : '') + '</p>' + lado(x, a.col, 'rd-du-izq') + lado(y, b.col, 'rd-du-der') + '</div>';
      }).join('');
      document.getElementById('rdDueloOut').innerHTML =
        '<div class="rd-du-cab"><span style="--c:' + a.col + '">' + esc(a.c) + '</span><span class="rd-du-vs">vs</span><span style="--c:' + b.col + '">' + esc(b.c) + '</span></div>' + filas +
        '<p class="rd-nota">Sin ganador: más ingreso o más inversión no es por sí solo mejor, ni menos deuda peor. Los números dicen cuánto; el juicio es tuyo. En <a href="radar-tablero.html">el tablero</a>, toca una administración para ver de dónde sale cada cifra.</p>';
      crecer(document.getElementById('rdDueloOut'));
    }
    s1.addEventListener('change', pintaDuelo); s2.addEventListener('change', pintaDuelo);
    pintaDuelo();
  }

  /* ================= El peso en el tiempo ================= */
  var P = D.peso, rdPeso = document.getElementById('rdPeso');
  if (rdPeso && P) {
    var REF = P.ref.inpc, HOY = P.hoy;
    var proyDe = {};
    P.proy.forEach(function (p) { proyDe[p.y] = p; });
    function pesos(v, d) { return '$' + num(v, d == null ? 2 : d); }
    function admDe(y) { for (var i = 0; i < D.admins.length; i++) if (y >= D.admins[i].a[0] && y <= D.admins[i].a[1]) return D.admins[i]; return null; }

    /* Lo de hoy, en tarjetas */
    var u = P.proy[0], uN = P.proy[P.proy.length - 1];
    document.getElementById('rdPesoHoy').innerHTML = [
      ['💵', 'El dólar hoy', pesos(HOY.usd, 4), 'FIX del ' + HOY.fecha + ': pesos por un dólar.', 'oficial', [P.f.hoy]],
      ['💶', 'El euro hoy', pesos(HOY.eur, 4), 'Cotización del ' + HOY.fecha + ': pesos por un euro.', 'oficial', [P.f.hoy]],
      ['🛒', 'Inflación de los últimos 12 meses', num(P.ref.infl12, 1) + '%', 'INPC de ' + P.ref.mes + ' (' + num(REF, 3) + ') ÷ INPC de un año antes (' + num(P.ref.inpc12, 3) + ') − 1.', 'derivado', [P.f.inpc]],
      ['🔮', 'Lo que proyecta Hacienda', num(u.infl, 1) + '% en ' + u.y, 'Inflación de diciembre a diciembre; ' + num(P.proy[1].infl, 1) + '% al año de ' + P.proy[1].y + ' a ' + uN.y + '. Dólar promedio: ' + pesos(u.usd, 1) + ' en ' + u.y + ' y ' + pesos(uN.usd, 1) + ' en ' + uN.y + '.', 'oficial', [P.f.proy]]
    ].map(function (c) {
      return '<div class="rd-ph"><span class="rd-ph-que"><span aria-hidden="true">' + c[0] + '</span> ' + esc(c[1]) + '</span><b>' + c[2] + '</b> ' + chip(c[4]) +
        '<small>' + esc(c[3]) + '</small><small class="rd-fte">📄 ' + fuentes(c[5]) + '</small></div>';
    }).join('');

    /* ---- Gráficas en SVG, sin bibliotecas ---- */
    var W = 720, H = 300, ML = 48, MR = 14, MT = 30, MB = 26, X0 = 1988, X1 = 2033;
    function sx(x) { return ML + (x - X0) / (X1 - X0) * (W - ML - MR); }
    function lienzo(y1, paso, yfmt, cuerpo) {
      function sy(y) { return MT + (1 - y / y1) * (H - MT - MB); }
      var g = '';
      D.admins.forEach(function (a, i) {
        var x0 = sx(a.a[0]), x1 = sx(Math.min(a.a[1] + 1, X1));
        g += '<rect x="' + x0 + '" y="' + MT + '" width="' + (x1 - x0) + '" height="' + (H - MT - MB) + '" fill="' + a.col + '" opacity="' + (i % 2 ? .07 : .12) + '"/>' +
          '<text x="' + ((x0 + x1) / 2) + '" y="' + (MT - 9) + '" text-anchor="middle" class="rd-g-adm" fill="' + a.col + '">' + esc(a.ini) + '</text>';
      });
      for (var y = 0; y <= y1 + 1e-9; y += paso) {
        g += '<line x1="' + ML + '" x2="' + (W - MR) + '" y1="' + sy(y) + '" y2="' + sy(y) + '" class="rd-g-rej"/>' +
          '<text x="' + (ML - 6) + '" y="' + (sy(y) + 4) + '" text-anchor="end" class="rd-g-eje">' + yfmt(y) + '</text>';
      }
      for (var x = 1990; x <= 2030; x += 5) g += '<text x="' + sx(x) + '" y="' + (H - 8) + '" text-anchor="middle" class="rd-g-eje">' + x + '</text>';
      g += '<line x1="' + sx(2026.77) + '" x2="' + sx(2026.77) + '" y1="' + MT + '" y2="' + (H - MB) + '" class="rd-g-hoy"/>' +
        '<text x="' + (sx(2026.77) + 4) + '" y="' + (MT + 12) + '" class="rd-g-hoyt">hoy</text>';
      return '<svg viewBox="0 0 ' + W + ' ' + H + '" class="rd-g" role="img">' + g + cuerpo(sy) +
        '<line class="rd-g-guia" x1="0" x2="0" y1="' + MT + '" y2="' + (H - MB) + '" visibility="hidden"/></svg>';
    }
    function linea(pts, sy, cls, col) {
      return '<polyline class="' + cls + '" fill="none" stroke="' + col + '" points="' + pts.map(function (p) { return sx(p[0]).toFixed(1) + ',' + sy(p[1]).toFixed(1); }).join(' ') + '"/>';
    }
    function punto(x, y, sy, col, r, et, der) {
      return '<circle cx="' + sx(x) + '" cy="' + sy(y) + '" r="' + (r || 5) + '" fill="' + col + '" stroke="#fff" stroke-width="2"/>' +
        (et ? '<text x="' + (sx(x) + (der ? 10 : -6)) + '" y="' + (sy(y) + (der ? 4 : -9)) + '" text-anchor="' + (der ? 'start' : 'end') + '" class="rd-g-et" fill="' + col + '">' + et + '</text>' : '');
    }
    function proyIni() { return P.proy[0].y; }

    var GRAF = [
      { id: 'precios', et: '🛒 Lo que cuesta lo mismo',
        svg: function () {
          var pas = P.anios.map(function (y) { return [y + 0.5, 100 * P.inpc[y] / REF]; });
          var xh = P.ref.y + (P.ref.m - 0.5) / 12;
          var fut = [[xh, 100]].concat(P.proy.map(function (p) { return [p.y + 0.96, 100 * p.inpc / REF]; }));
          return lienzo(140, 20, function (y) { return '$' + y; }, function (sy) {
            return linea(pas.concat([[xh, 100]]), sy, 'rd-g-l', '#0b2a63') + linea(fut, sy, 'rd-g-l rd-g-proy', '#c98a12') +
              punto(xh, 100, sy, '#b3261e', 6, '$100 hoy') + punto(fut[fut.length - 1][0], fut[fut.length - 1][1], sy, '#c98a12', 4);
          });
        },
        lee: function (y) {
          if (y === P.ref.y) return 'Hoy (' + P.ref.mes + '): lo que compras con $100. Es el punto de referencia de toda la gráfica.';
          if (proyDe[y]) return 'Diciembre de ' + y + ', proyección de Hacienda: lo que hoy cuesta $100 costaría ' + pesos(100 * proyDe[y].inpc / REF) +
            ' (inflación de ' + num(proyDe[y].infl, 1) + '% en ' + y + ', encadenada desde diciembre de ' + P.proy_obs + ').';
          if (P.inpc[y]) return 'En ' + y + ', lo que hoy cuesta $100 costaba ' + pesos(100 * P.inpc[y] / REF) + '. Al revés: $100 de ' + y + ' equivalen a ' +
            pesos(100 * REF / P.inpc[y]) + ' de hoy (INPC de ' + P.ref.mes + ' ÷ INPC promedio de ' + y + ').';
          return '';
        },
        pie: [['#0b2a63', 'Observado: INPC promedio de cada año ÷ INPC de ' + P.ref.mes + ' × 100'], ['#c98a12', 'Proyección de Hacienda (diciembre de cada año)', 1]],
        f: [P.f.inpc, P.f.proy] },
      { id: 'inflacion', et: '📈 Inflación año por año',
        svg: function () {
          return lienzo(55, 10, function (y) { return y + '%'; }, function (sy) {
            var b = '', w = (W - ML - MR) / (X1 - X0) * 0.72;
            P.anios.forEach(function (y) {
              if (P.infl[y] == null) return;
              var a = admDe(y), v = P.infl[y];
              b += '<rect x="' + (sx(y + 0.5) - w / 2) + '" y="' + sy(v) + '" width="' + w + '" height="' + (sy(0) - sy(v)) + '" fill="' + (a ? a.col : '#94a3b8') + '" rx="1.5"/>';
            });
            P.proy.forEach(function (p) {
              b += '<rect x="' + (sx(p.y + 0.5) - w / 2) + '" y="' + sy(p.infl) + '" width="' + w + '" height="' + (sy(0) - sy(p.infl)) + '" fill="url(#rdRayas)" stroke="#c98a12" rx="1.5"/>';
            });
            var mx = 1988, mv = 0;
            P.anios.forEach(function (y) { if ((P.infl[y] || 0) > mv) { mv = P.infl[y]; mx = y; } });
            return '<defs><pattern id="rdRayas" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#fff4dc"/><line x1="0" y1="0" x2="0" y2="5" stroke="#c98a12" stroke-width="2.4"/></pattern></defs>' +
              b + '<text x="' + (sx(mx + 0.5) + 8) + '" y="' + (sy(mv) + 4) + '" class="rd-g-et" fill="#24324d">' + num(mv, 1) + '% en ' + mx + '</text>';
          });
        },
        lee: function (y) {
          if (proyDe[y]) return y + ', proyección de Hacienda: ' + num(proyDe[y].infl, 1) + '% de diciembre a diciembre.';
          if (P.infl[y] != null) return y + ': los precios subieron ' + num(P.infl[y], 1) + '% de diciembre a diciembre (INPC de diciembre de ' + y + ' ÷ INPC de diciembre de ' + (y - 1) + ' − 1)' +
            (admDe(y) ? ', con ' + admDe(y).c + '.' : '.');
          return '';
        },
        pie: [['#7d3fa6', 'Observado, del color de cada administración'], ['#c98a12', 'Proyección de Hacienda', 1]],
        f: [P.f.inpc, P.f.proy] },
      { id: 'cambio', et: '💱 Frente al dólar y al euro',
        svg: function () {
          var us = P.anios.map(function (y) { return [y + 0.5, P.usd[y]]; });
          var eu = P.anios.filter(function (y) { return P.eur[y]; }).map(function (y) { return [y + 0.5, P.eur[y]]; });
          var last = P.anios[P.anios.length - 1];
          var fut = [[last + 0.5, P.usd[last]]].concat(P.proy.map(function (p) { return [p.y + 0.5, p.usd]; }));
          return lienzo(25, 5, function (y) { return '$' + y; }, function (sy) {
            return linea(us, sy, 'rd-g-l', '#23855a') + linea(eu, sy, 'rd-g-l', '#1a56b8') + linea(fut, sy, 'rd-g-l rd-g-proy', '#c98a12') +
              punto(2026.77, HOY.eur, sy, '#1a56b8', 6, '€ ' + pesos(HOY.eur), 1) + punto(2026.77, HOY.usd, sy, '#23855a', 6, 'US$ ' + pesos(HOY.usd), 1);
          });
        },
        lee: function (y) {
          if (y === P.ref.y) return 'Hoy, ' + HOY.fecha + ': el dólar en ' + pesos(HOY.usd, 4) + ' y el euro en ' + pesos(HOY.eur, 4) + '. Hacienda estima un dólar promedio de ' + pesos(proyDe[y].usd, 1) + ' para ' + y + '.';
          if (proyDe[y]) return y + ', proyección de Hacienda: dólar promedio de ' + pesos(proyDe[y].usd, 1) + '. Del euro no hay proyección oficial.';
          if (P.usd[y]) return y + ': el dólar promedió ' + pesos(P.usd[y], 2) + (P.eur[y] ? ' y el euro ' + pesos(P.eur[y], 2) : ' (el euro, sin serie de Banxico antes de ' + P.eur_desde + ')') + ' (promedio de los 12 meses).';
          return '';
        },
        pie: [['#23855a', 'Pesos por dólar, promedio anual'], ['#1a56b8', 'Pesos por euro, promedio anual (desde ' + P.eur_desde + ')'], ['#c98a12', 'Dólar proyectado por Hacienda', 1]],
        f: [P.f.usd, P.f.eur, P.f.hoy, P.f.proy] }
    ];
    var gAct = 'precios';
    function pintaGraf() {
      var g = GRAF.filter(function (x) { return x.id === gAct; })[0];
      document.getElementById('rdGrafTabs').innerHTML = GRAF.map(function (x) {
        return '<button type="button" class="rd-met" role="tab" aria-selected="' + (x.id === gAct) + '" data-graf="' + x.id + '">' + esc(x.et) + '</button>';
      }).join('');
      var cont = document.getElementById('rdGrafSvg');
      cont.innerHTML = g.svg();
      cont.querySelector('svg').setAttribute('aria-label', g.et + ': desliza o toca la gráfica para leer cada año.');
      document.getElementById('rdGrafLee').textContent = g.lee(P.ref.y);
      document.getElementById('rdGrafPie').innerHTML = '<ul class="rd-g-ley">' + g.pie.map(function (p) {
        return '<li><span class="' + (p[2] ? 'rd-g-sw rd-g-sw-p' : 'rd-g-sw') + '" style="--c:' + p[0] + '"></span>' + esc(p[1]) + '</li>';
      }).join('') + '</ul><p class="rd-nota">' + chip('oficial') + ' los datos de Banxico y de Hacienda; ' + chip('derivado') + ' cada cuenta hecha con ellos. ' +
        esc(P.proy_aviso) + (gAct === 'cambio' ? ' ' + esc(P.proy_eur) : '') + '</p><p class="rd-fte">📄 ' + fuentes(g.f) + '</p>';
    }
    function leeEn(ev) {
      var svg = ev.currentTarget.querySelector('svg');
      if (!svg) return;
      var r = svg.getBoundingClientRect(), x = (ev.clientX - r.left) / r.width * W;
      var y = Math.floor(X0 + (x - ML) / (W - ML - MR) * (X1 - X0));
      var g = GRAF.filter(function (z) { return z.id === gAct; })[0];
      var t = g.lee(y);
      if (!t) return;
      document.getElementById('rdGrafLee').textContent = t;
      var gu = svg.querySelector('.rd-g-guia');
      gu.setAttribute('x1', sx(y + 0.5)); gu.setAttribute('x2', sx(y + 0.5)); gu.setAttribute('visibility', 'visible');
    }
    var lz = document.getElementById('rdGrafSvg');
    lz.addEventListener('pointermove', leeEn);
    lz.addEventListener('pointerdown', leeEn);
    document.getElementById('rdGrafTabs').addEventListener('click', function (ev) {
      var b = ev.target.closest('button[data-graf]');
      if (b) { gAct = b.getAttribute('data-graf'); pintaGraf(); }
    });
    pintaGraf();

    /* ---- El peso en cada sexenio ---- */
    function tc(x, s) {
      if (!x || !tieneV(x)) return '<span class="rd-pt-v">' + sinDato(x) + '</span>' + (x && x.na ? '<small class="rd-motivo">' + esc(x.na) + '</small>' : '');
      return '<span class="rd-pt-v">' + pesos(x.rec, 2) + ' → ' + pesos(x.ent, 2) + '</span> <span class="rd-pt-d">' + (x.v > 0 ? '+' : '') + num(x.v, 1) + '%</span> ' + chip(x.est);
    }
    var ops = [];
    document.getElementById('rdPesoTabla').innerHTML = '<div class="rd-pt">' + P.admins.map(function (f) {
      var a = adm(f.id);
      ops.push('<li><b>' + esc(a.c) + ':</b> ' + esc(f.infl.op) + ' ' + esc(f.cien.op) + (f.usd.op ? ' Dólar: ' + esc(f.usd.op) : '') + (f.eur.op ? ' Euro: ' + esc(f.eur.op) : '') + '</li>');
      return '<div class="rd-pt-c" style="--c:' + a.col + '"><p class="rd-pt-cab"><span class="rd-admin-ini" aria-hidden="true">' + esc(a.ini) + '</span><span><b>' + esc(a.c) + '</b><small>' +
          esc(f.rec) + ' → ' + esc(f.ent) + (f.curso ? ', en curso' : '') + '</small></span></p>' +
        '<dl><div><dt>Inflación acumulada</dt><dd><span class="rd-pt-v">+' + num(f.infl.v, 1) + '%</span> ' + chip(f.infl.est) +
          '<small>$100 al recibir compraban al final lo que ' + pesos(f.cien.v) + '.</small></dd></div>' +
        '<div><dt>El dólar</dt><dd>' + tc(f.usd) + '</dd></div>' +
        '<div><dt>El euro</dt><dd>' + tc(f.eur) + '</dd></div></dl></div>';
    }).join('') + '</div><details class="rd-de"><summary>¿De dónde salen?</summary><ul class="rd-pt-ops">' + ops.join('') +
      '</ul><p class="rd-nota">Al recibir: diciembre del año anterior a su primer año; al entregar: diciembre de su último año. Tipo de cambio: promedio de ese mes.</p>' +
      '<p class="rd-fte">📄 ' + fuentes([P.f.inpc, P.f.usd, P.f.eur]) + '</p></details>';

    /* ---- La máquina del tiempo ---- */
    var mA = document.getElementById('rdMaqAnio'), mH = document.getElementById('rdMaqHasta'), mM = document.getElementById('rdMaqMonto');
    mA.innerHTML = '<option value="hoy">Hoy (' + esc(P.ref.mes) + ')</option>' + P.anios.slice().reverse().map(function (y) {
      return '<option value="' + y + '">' + y + '</option>';
    }).join('');
    mA.value = '2000';
    mH.innerHTML = P.proy.map(function (p) { return '<option value="' + p.y + '">Diciembre de ' + p.y + '</option>'; }).join('');
    mH.value = String(P.proy[P.proy.length - 1].y);
    function maq() {
      var m = parseFloat(mM.value), out = document.getElementById('rdMaqOut');
      if (!(m >= 0)) { out.innerHTML = '<p class="rd-nota">Escribe una cantidad en pesos.</p>'; return; }
      var y = mA.value === 'hoy' ? null : +mA.value, ph = proyDe[+mH.value];
      var hoy = y ? m * REF / P.inpc[y] : m;
      var c = [];
      if (y) c.push(['🧮', 'En pesos de hoy', pesos(hoy), pesos(m) + ' × INPC de ' + P.ref.mes + ' (' + num(REF, 3) + ') ÷ INPC promedio de ' + y + ' (' + num(P.inpc[y], 3) + ').', [P.f.inpc]]);
      c.push(['💵', y ? 'En dólares de ' + y : 'En dólares, hoy', 'US$' + num(y ? m / P.usd[y] : m / HOY.usd, 2),
        y ? pesos(m) + ' ÷ ' + pesos(P.usd[y], 4) + ', el dólar promedio de ' + y + '. Hoy, sus ' + pesos(hoy) + ' son US$' + num(hoy / HOY.usd, 2) + ' al FIX del ' + HOY.fecha + '.'
          : pesos(m) + ' ÷ ' + pesos(HOY.usd, 4) + ', el FIX del ' + HOY.fecha + '.', y ? [P.f.usd, P.f.hoy] : [P.f.hoy]]);
      if (!y || P.eur[y]) c.push(['💶', y ? 'En euros de ' + y : 'En euros, hoy', '€' + num(y ? m / P.eur[y] : m / HOY.eur, 2),
        y ? pesos(m) + ' ÷ ' + pesos(P.eur[y], 4) + ', el euro promedio de ' + y + '. Hoy, sus ' + pesos(hoy) + ' son €' + num(hoy / HOY.eur, 2) + '.'
          : pesos(m) + ' ÷ ' + pesos(HOY.eur, 4) + ', el euro del ' + HOY.fecha + '.', y ? [P.f.eur, P.f.hoy] : [P.f.hoy]]);
      else c.push(['💶', 'En euros de ' + y, '—', P.eur_antes, [P.f.eur], 1]);
      c.push(['🔮', 'En diciembre de ' + ph.y + ', según Hacienda', pesos(hoy * ph.inpc / REF),
        'Para comprar lo mismo que ' + pesos(hoy) + ' de hoy: × INPC proyectado de diciembre de ' + ph.y + ' (' + num(ph.inpc, 3) + ') ÷ INPC de ' + P.ref.mes + '. Es proyección, no dato.', [P.f.inpc, P.f.proy]]);
      out.innerHTML = '<div class="rd-maq-res">' + c.map(function (x) {
        return '<div class="rd-ph' + (x[0] === '🔮' ? ' rd-ph-proy' : '') + '"><span class="rd-ph-que"><span aria-hidden="true">' + x[0] + '</span> ' + esc(x[1]) + '</span><b>' + x[2] + '</b> ' +
          (x[5] ? '<span class="rd-na">sin serie</span>' : chip('derivado')) + '<small>' + esc(x[3]) + '</small><small class="rd-fte">📄 ' + fuentes(x[4]) + '</small></div>';
      }).join('') + '</div>';
    }
    [mA, mH].forEach(function (el) { el.addEventListener('change', maq); });
    mM.addEventListener('input', maq);
    maq();
  }
})();
