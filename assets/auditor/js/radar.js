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
  var est = { adm: D.inicial || D.admins[D.admins.length - 1].id, dim: D.dims[0].id, met: null, mon: 'hoy', base: 'anio' };
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
      return '<button type="button" class="rd-met" role="tab" aria-selected="' + (m === est.met) + '" data-met="' + m + '">' + (D.metricas[m].mon ? '💵 ' : '') + esc(D.metricas[m].tit) + '</button>';
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
      h += '<p class="rd-obras-tit"><a href="informes-cuenta-publica.html">⚖️ Lo que encontró la ASF en la Cuenta Pública 2024, estado por estado ➔</a></p>';
    }
    h += '</div>';

    /* La comparativa de todas las administraciones. */
    var mm = D.metricas[est.met];
    var mon = mm.mon ? est.mon : null;
    if (mm.mon) {
      document.getElementById('rdDim').innerHTML = h + dinero(est.met, mon);
      crecer(document.getElementById('rdDim'));
      contarDin(document.getElementById('rdDim'));
      return;
    }
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

  /* ---- Lo que cuesta, en dinero (pedido del autor, 12-10-2026) ----
     En las dimensiones con suma en pesos, la comparativa pone primero el
     dinero: cuánto por año, en promedio, y cuánto en todo el sexenio. El
     % del PIB queda de contexto en cada renglón. El promedio por año es
     la suma entre los años con dato, para que un sexenio con cinco años
     (Salinas) o uno en curso (Sheinbaum) se comparen con los demás. */
  function fmtDin(v, mon) {
    var a = Math.abs(v), p = PRE[mon] || '$', s = v < 0 ? '−' : '';
    if (a >= 1e6) return { pre: s + p, n: a / 1e6, d: 2, suf: ' billones' };
    if (a >= 1e3) return { pre: s + p, n: a / 1e3, d: 1, suf: ' mil millones' };
    return { pre: s + p, n: a, d: 1, suf: ' millones' };
  }
  function din(v, mon, cls) {
    var f = fmtDin(v, mon);
    return '<b class="rd-din-v ' + (cls || '') + '" data-n="' + f.n + '" data-d="' + f.d + '" data-pre="' + esc(f.pre) + '" data-suf="' + esc(f.suf) + '">' +
      esc(f.pre) + num(f.n, f.d) + esc(f.suf) + '</b>';
  }
  function txtDin(v, mon) { var f = fmtDin(v, mon); return f.pre + num(f.n, f.d) + f.suf; }
  /* La suma en la moneda elegida y, si no se puede sumar el sexenio
     completo, la de los años que sí tienen dato («parcial»). */
  function sumaMon(x, mon, a) {
    var s = enMon(x, mon);
    if (tieneV(s)) return { s: s, base: s, ys: a.ys };
    var p = null, ys = null, por = '';
    if (x && x.parcial) {
      p = (mon && mon !== 'nom') ? (x.parcial.alt || {})[mon] : x.parcial;
      ys = x.parcial.ys; por = x.pend;
    } else if (s && s.parcial) {
      p = s.parcial; ys = s.parcial.ys; por = s.na;
    }
    return { s: s, base: tieneV(p) ? p : null, ys: ys, por: por };
  }
  function dinero(met, mon) {
    var mm = D.metricas[met], pib = met.replace(/_mdp$/, '_pib'), mp = D.metricas[pib];
    var filas = D.admins.map(function (a) {
      var r = sumaMon(val(a.id, met), mon, a), n = r.ys ? r.ys[1] - r.ys[0] + 1 : 0;
      r.a = a; r.n = n;
      r.anio = r.base && n ? r.base.v / n : null;
      r.pib = mp ? val(a.id, pib) : null;
      r.cmp = est.base === 'anio' ? r.anio : (tieneV(r.s) ? r.s.v : null);
      return r;
    });
    var max = 0;
    filas.forEach(function (r) { if (r.cmp != null) max = Math.max(max, Math.abs(r.cmp)); });
    var tit = mm.tit.replace(/ \(suma del sexenio\)$/, '');
    var h = '<div class="rd-comp rd-din"><p class="rd-comp-tit">💵 Cuánto dinero, administración por administración: ' + esc(tit) + ', ' + esc(moneda(mon).lee) + '</p>' +
      '<div class="rd-din-ctl"><div class="rd-mon rd-din-base" role="radiogroup" aria-label="Qué comparar">' +
        [['anio', 'Por año, en promedio'], ['sex', 'Todo el sexenio']].map(function (b) {
          return '<button type="button" role="radio" aria-checked="' + (b[0] === est.base) + '" data-base="' + b[0] + '">' + b[1] + '</button>';
        }).join('') + '</div>' + selMon(mon, 'data-mon') + '</div>' +
      (moneda(mon).ojo ? '<p class="rd-ojo">⚠️ ' + esc(moneda(mon).ojo) + '</p>' : '') +
      '<ol class="rd-din-lista">' + filas.map(function (r) {
        var a = r.a, w = r.cmp != null && max ? Math.max(2, Math.abs(r.cmp) / max * 100) : 0;
        var rango = r.ys ? (r.ys[0] === r.ys[1] ? String(r.ys[0]) : r.ys[0] + ' a ' + r.ys[1]) : '';
        var vAnio = r.anio != null ? din(r.anio, mon) : null;
        var vSex = tieneV(r.s) ? din(r.s.v, mon) : null;
        var grande, chica;
        /* Si el promedio sale de una parte del sexenio, se dice de cuál. */
        var solo = r.anio != null && !tieneV(r.s) ? ' <span class="rd-din-nota">Promedio de ' + r.n + (r.n === 1 ? ' año con dato: ' : ' años con dato: ') + rango + '.</span>' : '';
        if (est.base === 'anio') {
          grande = vAnio ? vAnio + ' <span class="rd-din-u">al año</span> ' + chip('derivado') + solo : sinDato(r.s);
          chica = vSex ? (a.curso ? 'En lo que va (' + rango + '): ' : 'En todo el sexenio: ') + vSex + ' ' + chip(r.s.est) :
            'Todo el sexenio: ' + sinDato(r.s) + (r.base ? ' <span class="rd-din-nota">' + (r.n === 1 ? 'El año' : 'Los ' + r.n + ' años') + ' con dato (' + rango + ') ' + (r.n === 1 ? 'suma ' : 'suman ') + txtDin(r.base.v, mon) + '.</span>' : '');
        } else {
          grande = vSex ? vSex + ' <span class="rd-din-u">' + (a.curso ? 'en lo que va (' + rango + ')' : 'en el sexenio') + '</span> ' + chip(r.s.est) : sinDato(r.s);
          chica = vAnio ? 'Por año, en promedio: ' + vAnio + ' ' + chip('derivado') + solo : '';
        }
        var pibTx = r.pib && tieneV(r.pib) ? '<span class="rd-din-pib">Para dar escala: ' + fmt(r.pib.v, 'pib') + ' al año, en promedio</span>' : '';
        var de = '<details class="rd-de"><summary>¿De dónde sale?</summary>' +
          (r.anio != null ? '<p><b>Por año:</b> suma de ' + rango + ' (' + txtDin(r.base.v, mon) + ') ÷ ' + r.n + (r.n === 1 ? ' año' : ' años') + ' con dato = ' + txtDin(r.anio, mon) + '.</p>' : '') +
          (r.base && r.base.op ? '<p><b>Suma:</b> ' + esc(r.base.op) + '</p>' : '') +
          (!tieneV(r.s) && r.por ? '<p class="rd-nota">' + esc(r.por) + '</p>' : '') +
          (r.pib && tieneV(r.pib) && r.pib.op ? '<p><b>% del PIB:</b> ' + esc(r.pib.op) + '</p>' : '') +
          (r.base ? '<p class="rd-fte">📄 ' + fuentes(r.base.f) + '</p>' : '') + '</details>';
        return '<li class="rd-din-fila' + (a.id === est.adm ? ' rd-bar-on' : '') + '" style="--c:' + a.col + '">' +
          '<button type="button" class="rd-bar-nom" data-adm="' + a.id + '">' + esc(a.c) + ' <small>' + (a.curso ? a.a[0] + ', en curso' : a.a[0] + '–' + String(a.a[1]).slice(2)) + '</small></button>' +
          '<p class="rd-din-grande">' + grande + '</p>' +
          '<span class="rd-bar-pista">' + (w ? '<span class="rd-bar" data-w="' + w + '"></span>' : '') + '</span>' +
          '<p class="rd-din-chica">' + chica + '</p>' + pibTx + (r.base || (r.pib && tieneV(r.pib)) ? de : '') + '</li>';
      }).join('') + '</ol>' +
      '<p class="rd-nota">«Por año» es la suma entre los años con dato: así un sexenio al que le falta un año, o uno en curso, se compara con los demás. ' +
      'El % del PIB dice qué tan grande fue ese dinero para la economía de su momento; está en la pestaña «' + esc(mp ? mp.tit : '') + '».</p></div>';
    return h;
  }
  /* Las cifras de dinero cuentan desde cero mientras crecen las barras. */
  function contarDin(cont) {
    var els = [].slice.call(cont.querySelectorAll('.rd-din-v'));
    function pon(f) {
      els.forEach(function (el) {
        el.textContent = el.getAttribute('data-pre') + num(parseFloat(el.getAttribute('data-n')) * f, +el.getAttribute('data-d')) + el.getAttribute('data-suf');
      });
    }
    if (reduce || !els.length) return;
    var t0 = performance.now();
    pon(0);
    (function paso(ahora) {
      var x = Math.min(1, (ahora - t0) / 900);
      pon(1 - Math.pow(1 - x, 3));
      if (x < 1) requestAnimationFrame(paso);
    })(t0);
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
      else if (b.hasAttribute('data-base')) { est.base = b.getAttribute('data-base'); pintaDim(); }
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
    /* Desde el 12-10-2026 (pedido del autor) el reloj también corre cuando
       al sexenio le falta un año o una moneda: usa el ritmo de los años que
       sí tienen dato («parcial», que arma apartados.py) y dice por qué. */
    function usable(y) { return tieneV(y) || !!(y && y.parcial); }
    function segAnios(ys) { return (Date.UTC(ys[1] + 1, 0, 1) - Date.UTC(ys[0], 0, 1)) / 1000; }
    function tasa() {
      var a = adm(selA.value), r = D.reloj.filter(function (x) { return x.met === selM.value; })[0];
      var x0 = val(a.id, r.met), base = !tieneV(x0) && x0.parcial ? x0.parcial : x0;
      var sinMon = [];
      Array.prototype.forEach.call(selMo.options, function (o) {
        o.disabled = !!base.alt && !usable(enMon(base, o.value));
        if (o.disabled) sinMon.push({ et: o.textContent, por: enMon(base, o.value).na || 'Sin dato.' });
      });
      if (selMo.options[selMo.selectedIndex].disabled) selMo.value = 'hoy';
      selMo.disabled = !base.alt;
      var mon = base.alt ? selMo.value : 'nom';
      var x = enMon(base, mon), just = base !== x0 ? base : null;
      if (!tieneV(x) && x && x.parcial) { x = x.parcial; just = x; }
      if (!tieneV(x)) return { pend: x, r: r, a: a };
      var porSeg = r.porSeg ? x.v : x.v * 1e6 / (just ? segAnios(just.ys) : segundos(a));
      return { s: porSeg, r: r, a: a, x: x, mon: mon, solo: !base.alt && tieneV(x0), just: just, pid: base !== x0 ? x0.pid : null, sinMon: sinMon };
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
        (t.just ? '<p class="rd-reloj-just">' + esc(t.just.just) + (t.pid ? ' ' + chip('pendiente', t.pid) : '') + '</p>' : '') +
        '<p class="rd-reloj-op">' + esc(t.just ? 'Suma de ' + (t.just.ys[0] === t.just.ys[1] ? t.just.ys[0] : t.just.ys[0] + ' a ' + t.just.ys[1]) + ' entre los segundos de ese periodo.' : t.r.op) + ' Moneda: ' + esc(t.solo ? 'pesos de cada año (esta medida no se convierte: es un saldo de deuda)' : moneda(t.mon).lee) + '. ' + chip('derivado') + '</p>' +
        (t.x.op ? '<details class="rd-de"><summary>¿De dónde sale la suma?</summary><p>' + esc(t.x.op) + '</p></details>' : '') +
        '<p class="rd-fte">📄 ' + fuentes(t.x.f) + '</p>' +
        t.sinMon.map(function (m) { return '<p class="rd-reloj-sinmon">' + esc(m.et) + ': no disponible para esta administración. ' + esc(m.por) + '</p>'; }).join('');
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
      var out = document.getElementById('rdDueloOut');
      out.innerHTML =
        '<div class="rd-du-cab"><span style="--c:' + a.col + '">' + esc(a.c) + '</span><span class="rd-du-vs">vs</span><span style="--c:' + b.col + '">' + esc(b.c) + '</span></div>' + filas +
        '<p class="rd-nota">Sin ganador: más ingreso o más inversión no es por sí solo mejor, ni menos deuda peor. Los números dicen cuánto; el juicio es tuyo. En <a href="radar-tablero.html">el tablero</a>, toca una administración para ver de dónde sale cada cifra.</p>';
      /* Cada número de cada cifra se vuelve un tramo que cuenta desde
         cero, con sus mismos decimales: «$1,234.5 mil mdp» va de $0.0 a
         $1,234.5 y el texto de alrededor no cambia. */
      dTramos = [];
      out.querySelectorAll('.rd-du-v').forEach(function (el) {
        var txt = el.textContent, re = /\d[\d,]*(?:\.\d+)?/g, m, ult = 0;
        el.textContent = '';
        while ((m = re.exec(txt))) {
          el.appendChild(document.createTextNode(txt.slice(ult, m.index)));
          var n = m[0], sp = document.createElement('span');
          sp.className = 'rd-num';
          dTramos.push({ el: sp, v: parseFloat(n.replace(/,/g, '')), d: n.indexOf('.') < 0 ? 0 : n.length - n.indexOf('.') - 1, miles: n.indexOf(',') >= 0 });
          el.appendChild(sp);
          ult = m.index + n.length;
        }
        el.appendChild(document.createTextNode(txt.slice(ult)));
      });
      dCeros();
    }
    /* El duelo arranca en ceros (pedido del autor, 12-10-2026): «Empezar
       duelo» lleva cifras y barras a su valor; el mismo botón las regresa
       a cero, y cambiar de administración también. */
    var dTramos = [], dAnim = null, dListo = false;
    var dBtn = document.getElementById('rdDueloBtn'), dTxt = document.getElementById('rdDueloTxt');
    function dPon(f) {
      dTramos.forEach(function (tr) {
        tr.el.textContent = (tr.v * f).toLocaleString('en-US', { minimumFractionDigits: tr.d, maximumFractionDigits: tr.d, useGrouping: tr.miles });
      });
    }
    function dCeros() {
      if (dAnim) { cancelAnimationFrame(dAnim); dAnim = null; }
      dListo = false;
      dPon(0);
      document.querySelectorAll('#rdDueloOut .rd-bar').forEach(function (b) { b.style.width = '0'; });
      dBtn.textContent = '▶ Empezar duelo';
      dBtn.setAttribute('aria-pressed', 'false');
      dTxt.textContent = 'Las cifras están en cero. Elige dos administraciones y presiona «Empezar duelo».';
    }
    function dEmpezar() {
      dListo = true;
      dBtn.textContent = '↺ Reiniciar en ceros';
      dBtn.setAttribute('aria-pressed', 'true');
      dTxt.textContent = 'Calculando… Cada cifra llega a su valor oficial.';
      crecer(document.getElementById('rdDueloOut'));
      var dur = reduce ? 0 : 1800, t0 = performance.now();
      function paso(ahora) {
        var x = dur ? Math.min(1, (ahora - t0) / dur) : 1;
        dPon(1 - Math.pow(1 - x, 3));
        if (x < 1) { dAnim = requestAnimationFrame(paso); return; }
        dAnim = null;
        dTxt.textContent = 'Listo: estas son las cifras de las dos administraciones. «Reiniciar en ceros» las regresa al inicio.';
      }
      dAnim = requestAnimationFrame(paso);
    }
    dBtn.addEventListener('click', function () { if (dListo) dCeros(); else dEmpezar(); });
    document.getElementById('rdDueloCuenta').hidden = false;
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

    /* Desde el 12-10-2026 (pedido del autor) cada parte vive en su página
       (radar-peso-monedas.html, radar-peso-sexenios.html y
       radar-peso-maquina.html): cada bloque arranca solo si su página lo trae. */
    /* Lo de hoy, en tarjetas */
    var u = P.proy[0], uN = P.proy[P.proy.length - 1], phHoy = document.getElementById('rdPesoHoy');
    if (phHoy) phHoy.innerHTML = [
      ['💵', 'El dólar hoy', pesos(HOY.usd, 4), 'FIX del ' + HOY.fecha + ': pesos por un dólar.', 'oficial', [P.f.hoy]],
      ['💶', 'El euro hoy', pesos(HOY.eur, 4), 'Cotización del ' + HOY.fecha + ': pesos por un euro.', 'oficial', [P.f.hoy]],
      ['🛒', 'Inflación de los últimos 12 meses', num(P.ref.infl12, 1) + '%', 'INPC de ' + P.ref.mes + ' (' + num(REF, 3) + ') ÷ INPC de un año antes (' + num(P.ref.inpc12, 3) + ') − 1.', 'derivado', [P.f.inpc]],
      ['🔮', 'Lo que proyecta Hacienda', num(u.infl, 1) + '% en ' + u.y, 'Inflación de diciembre a diciembre; ' + num(P.proy[1].infl, 1) + '% al año de ' + P.proy[1].y + ' a ' + uN.y + '. Dólar promedio: ' + pesos(u.usd, 1) + ' en ' + u.y + ' y ' + pesos(uN.usd, 1) + ' en ' + uN.y + '.', 'oficial', [P.f.proy]]
    ].map(function (c) {
      return '<div class="rd-ph"><span class="rd-ph-que"><span aria-hidden="true">' + c[0] + '</span> ' + esc(c[1]) + '</span><b>' + c[2] + '</b> ' + chip(c[4]) +
        '<small>' + esc(c[3]) + '</small><small class="rd-fte">📄 ' + fuentes(c[5]) + '</small></div>';
    }).join('');

    /* ---- Gráficas en SVG, sin bibliotecas ---- */
    if (document.getElementById('rdGraf')) {
    /* En pantallas angostas el lienzo es más estrecho, para que sus letras se lean en el celular. */
    var W = document.getElementById('rdGraf').clientWidth < 560 ? 430 : 720, H = 300, ML = 48, MR = 14, MT = 30, MB = 26, X0 = 1988, X1 = 2033;
    function sx(x) { return ML + (x - X0) / (X1 - X0) * (W - ML - MR); }
    function lienzo(y1, paso, yfmt, cuerpo) {
      function sy(y) { return MT + (1 - y / y1) * (H - MT - MB); }
      var g = '';
      D.admins.forEach(function (a, i) {
        var x0 = sx(a.a[0]), x1 = sx(Math.min(a.a[1] + 1, X1));
        g += '<rect class="rd-g-banda" data-adm="' + a.id + '" x="' + x0 + '" y="' + MT + '" width="' + (x1 - x0) + '" height="' + (H - MT - MB) + '" fill="' + a.col + '" opacity="' + (i % 2 ? .07 : .12) + '"/>' +
          '<text x="' + ((x0 + x1) / 2) + '" y="' + (MT - 9) + '" text-anchor="middle" class="rd-g-adm" fill="' + a.col + '">' + esc(a.ini) + '</text>';
      });
      for (var y = 0; y <= y1 + 1e-9; y += paso) {
        g += '<line x1="' + ML + '" x2="' + (W - MR) + '" y1="' + sy(y) + '" y2="' + sy(y) + '" class="rd-g-rej"/>' +
          '<text x="' + (ML - 6) + '" y="' + (sy(y) + 4) + '" text-anchor="end" class="rd-g-eje">' + yfmt(y) + '</text>';
      }
      for (var x = 1990; x <= 2030; x += 5) g += '<text x="' + sx(x) + '" y="' + (H - 8) + '" text-anchor="middle" class="rd-g-eje">' + x + '</text>';
      g += '<line x1="' + sx(2026.77) + '" x2="' + sx(2026.77) + '" y1="' + MT + '" y2="' + (H - MB) + '" class="rd-g-hoy"/>' +
        '<text x="' + (sx(2026.77) + 4) + '" y="' + (MT + 12) + '" class="rd-g-hoyt">hoy</text>';
      /* El simulador descubre las líneas hasta el año elegido (rdClipR). */
      return '<svg viewBox="0 0 ' + W + ' ' + H + '" class="rd-g" role="img">' + g +
        '<defs><clipPath id="rdClip"><rect id="rdClipR" x="0" y="0" width="' + ML + '" height="' + H + '"/></clipPath></defs>' +
        '<g clip-path="url(#rdClip)">' + cuerpo(sy) + '</g>' +
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
        cas: ['Lo que hoy cuesta $100, ese año', '$100 de ese año, en pesos de hoy'],
        val: function (y) {
          if (y === P.ref.y) return { v: [100, 100], hoy: 1 };
          if (proyDe[y]) return { v: [100 * proyDe[y].inpc / REF, null], sin: [null, 'Es proyección: no hay pesos de ese año todavía.'], proy: 1 };
          if (P.inpc[y]) return { v: [100 * P.inpc[y] / REF, 100 * REF / P.inpc[y]] };
          return { v: [null, null] };
        },
        fmt: function (v) { return pesos(v); },
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
        cas: ['Inflación del año, de diciembre a diciembre'],
        val: function (y) {
          if (proyDe[y]) return { v: [proyDe[y].infl], proy: 1 };
          return { v: [P.infl[y] != null ? P.infl[y] : null], sin: ['Sin dato para ese año en la serie.'] };
        },
        fmt: function (v) { return num(v, 1) + '%'; },
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
              /* En el lienzo angosto la etiqueta no cabe a la derecha: la cifra está en el marcador. */
              punto(2026.77, HOY.eur, sy, '#1a56b8', 6, W < 560 ? '' : '€ ' + pesos(HOY.eur), 1) + punto(2026.77, HOY.usd, sy, '#23855a', 6, W < 560 ? '' : 'US$ ' + pesos(HOY.usd), 1);
          });
        },
        lee: function (y) {
          if (y === P.ref.y) return 'Hoy, ' + HOY.fecha + ': el dólar en ' + pesos(HOY.usd, 4) + ' y el euro en ' + pesos(HOY.eur, 4) + '. Hacienda estima un dólar promedio de ' + pesos(proyDe[y].usd, 1) + ' para ' + y + '.';
          if (proyDe[y]) return y + ', proyección de Hacienda: dólar promedio de ' + pesos(proyDe[y].usd, 1) + '. Del euro no hay proyección oficial.';
          if (P.usd[y]) return y + ': el dólar promedió ' + pesos(P.usd[y], 2) + (P.eur[y] ? ' y el euro ' + pesos(P.eur[y], 2) : ' (el euro, sin serie de Banxico antes de ' + P.eur_desde + ')') + ' (promedio de los 12 meses).';
          return '';
        },
        cas: ['Pesos por un dólar', 'Pesos por un euro'],
        val: function (y) {
          if (y === P.ref.y) return { v: [HOY.usd, HOY.eur], hoy: 1 };
          if (proyDe[y]) return { v: [proyDe[y].usd, null], sin: [null, 'Hacienda no proyecta el euro.'], proy: 1 };
          return { v: [P.usd[y] || null, P.eur[y] || null], sin: [null, 'Banxico publica el euro desde ' + P.eur_desde + '.'] };
        },
        fmt: function (v) { return pesos(v); },
        pie: [['#23855a', 'Pesos por dólar, promedio anual'], ['#1a56b8', 'Pesos por euro, promedio anual (desde ' + P.eur_desde + ')'], ['#c98a12', 'Dólar proyectado por Hacienda', 1]],
        f: [P.f.usd, P.f.eur, P.f.hoy, P.f.proy] }
    ];
    var gAct = 'precios';
    function graf() { return GRAF.filter(function (x) { return x.id === gAct; })[0]; }
    function pintaGraf() {
      var g = graf();
      document.getElementById('rdGrafTabs').innerHTML = GRAF.map(function (x) {
        return '<button type="button" class="rd-met" role="tab" aria-selected="' + (x.id === gAct) + '" data-graf="' + x.id + '">' + esc(x.et) + '</button>';
      }).join('');
      var cont = document.getElementById('rdGrafSvg');
      cont.innerHTML = g.svg();
      cont.querySelector('svg').setAttribute('aria-label', g.et + ': toca la gráfica o mueve la barra para leer cada año.');
      document.getElementById('rdGrafPie').innerHTML = '<ul class="rd-g-ley">' + g.pie.map(function (p) {
        return '<li><span class="' + (p[2] ? 'rd-g-sw rd-g-sw-p' : 'rd-g-sw') + '" style="--c:' + p[0] + '"></span>' + esc(p[1]) + '</li>';
      }).join('') + '</ul><p class="rd-nota">' + chip('oficial') + ' los datos de Banxico y de Hacienda; ' + chip('derivado') + ' cada cuenta hecha con ellos. ' +
        esc(P.proy_aviso) + (gAct === 'cambio' ? ' ' + esc(P.proy_eur) : '') + '</p><p class="rd-fte">📄 ' + fuentes(g.f) + '</p>';
      vistos = [];
      aplica();
    }

    /* ---- El simulador (pedido del autor, 12-10-2026) ----
       Recorre los años de 1988 a la proyección de 2032, uno por uno: la
       gráfica se descubre hasta el año, el marcador dice quién gobernaba y
       cuenta hasta las cifras de ese año. Arranca en ceros; «↺ Reiniciar en
       ceros» lo regresa ahí. Las cifras son las mismas de la gráfica. */
    var ANIOS = P.anios.concat(P.proy.map(function (p) { return p.y; }))
      .filter(function (y, i, l) { return l.indexOf(y) === i; }).sort(function (a, b) { return a - b; });
    var simY = null, simT = null, vistos = [], tween = null;
    var sPlay = document.getElementById('rdSimPlay'), sCero = document.getElementById('rdSimCero'), sTxt = document.getElementById('rdSimTxt');
    var sReg = document.getElementById('rdSimAnio'), sRegTxt = document.getElementById('rdSimAnioTxt');
    sReg.min = ANIOS[0]; sReg.max = ANIOS[ANIOS.length - 1]; sReg.value = ANIOS[0];
    document.getElementById('rdSimAdms').innerHTML = D.admins.map(function (a) {
      return '<button type="button" class="rd-sim-adm" style="--c:' + a.col + '" data-ir="' + a.a[0] + '"><span class="rd-admin-ini" aria-hidden="true">' + esc(a.ini) + '</span>' +
        '<span><b>' + esc(a.c) + '</b><small>' + a.a[0] + '–' + a.a[1] + '</small></span></button>';
    }).join('');
    function quien(y) {
      var a = admDe(y);
      if (a) return '<span class="rd-sim-pres" style="--c:' + a.col + '"><span class="rd-admin-ini" aria-hidden="true">' + esc(a.ini) + '</span><span><b>' + esc(a.n) + '</b><small>' +
        a.a[0] + '–' + a.a[1] + (a.curso ? ', en curso' : '') + '</small></span></span>';
      return '<span class="rd-sim-pres rd-sim-pres-sin"><span><b>' + (y < D.admins[0].a[0] ? 'Antes de las administraciones del radar' : 'La administración siguiente') +
        '</b><small>' + (y < D.admins[0].a[0] ? 'El radar empieza en ' + D.admins[0].a[0] + '.' : 'Solo hay proyección de Hacienda.') + '</small></span></span>';
    }
    function marca() {
      var g = graf(), r = simY == null ? { v: g.cas.map(function () { return 0; }) } : g.val(simY);
      var cab = '<div class="rd-sim-cab"><span class="rd-sim-anio">' + (simY == null ? '0000' : simY) + '</span>' +
        (simY == null ? '<span class="rd-sim-pres rd-sim-pres-sin"><span><b>Las cifras están en cero</b><small>Presiona «Recorrer los sexenios».</small></span></span>' : quien(simY)) +
        (r.proy ? '<span class="rd-sim-tag rd-sim-tag-p">Proyección de Hacienda</span>' : r.hoy ? '<span class="rd-sim-tag">Hoy, ' + esc(P.ref.mes) + '</span>' : '') + '</div>';
      document.getElementById('rdSimMarca').innerHTML = cab + '<div class="rd-sim-vals">' + g.cas.map(function (c, i) {
        var v = r.v[i];
        return '<div class="rd-sim-v"><span>' + esc(c) + '</span>' + (v == null
          ? '<b class="rd-sim-sin">—</b><small>' + esc((r.sin && r.sin[i]) || 'Sin dato.') + '</small>'
          : '<b class="rd-num" data-i="' + i + '">' + g.fmt(vistos[i] || 0) + '</b>') + '</div>';
      }).join('') + '</div>';
      /* Cada cifra cuenta desde la que se veía hasta la del año. */
      if (tween) cancelAnimationFrame(tween);
      var de = g.cas.map(function (c, i) { return vistos[i] || 0; }), a = r.v, t0 = performance.now(), dur = reduce ? 0 : 320;
      function paso(ahora) {
        var x = dur ? Math.min(1, (ahora - t0) / dur) : 1, f = 1 - Math.pow(1 - x, 3);
        document.querySelectorAll('#rdSimMarca b[data-i]').forEach(function (el) {
          var i = +el.getAttribute('data-i');
          el.textContent = g.fmt(de[i] + (a[i] - de[i]) * f);
        });
        if (x < 1) { tween = requestAnimationFrame(paso); return; }
        tween = null;
      }
      vistos = a.map(function (v) { return v == null ? 0 : v; });
      tween = requestAnimationFrame(paso);
    }
    function aplica() {
      var svg = document.querySelector('#rdGrafSvg svg');
      document.getElementById('rdClipR').setAttribute('width', simY == null ? ML : sx(Math.min(simY + 1, X1)));
      var a = simY == null ? null : admDe(simY);
      svg.querySelectorAll('.rd-g-banda').forEach(function (bd) { bd.classList.toggle('rd-g-banda-on', !!a && bd.getAttribute('data-adm') === a.id); });
      var gu = svg.querySelector('.rd-g-guia');
      if (simY == null) gu.setAttribute('visibility', 'hidden');
      else { gu.setAttribute('x1', sx(simY + 0.5)); gu.setAttribute('x2', sx(simY + 0.5)); gu.setAttribute('visibility', 'visible'); }
      document.querySelectorAll('#rdSimAdms .rd-sim-adm').forEach(function (bt) {
        var on = !!a && +bt.getAttribute('data-ir') === a.a[0];
        if (on) bt.setAttribute('aria-current', 'true'); else bt.removeAttribute('aria-current');
      });
      sReg.value = simY == null ? ANIOS[0] : simY;
      sRegTxt.textContent = simY == null ? '—' : simY;
      document.getElementById('rdGrafLee').textContent = simY == null
        ? 'Presiona «Recorrer los sexenios» para ver, año por año, cómo se mueve cada cifra. También puedes mover la barra, tocar la gráfica o tocar a un presidente.'
        : graf().lee(simY);
      marca();
    }
    function irA(y) { simY = y; aplica(); }
    function pausa(fin) {
      if (simT) { clearInterval(simT); simT = null; }
      sPlay.textContent = fin ? '▶ Recorrer de nuevo' : '▶ Seguir recorriendo';
      sPlay.setAttribute('aria-pressed', 'false');
      sTxt.textContent = fin ? 'Listo: llegaste a la proyección de ' + ANIOS[ANIOS.length - 1] + '. Toca un año o a un presidente para volver.' : 'En pausa en ' + simY + '.';
    }
    function corre() {
      if (simY == null || simY === ANIOS[ANIOS.length - 1]) irA(ANIOS[0]);
      sPlay.textContent = '⏸ Pausar';
      sPlay.setAttribute('aria-pressed', 'true');
      sTxt.textContent = 'Recorriendo los sexenios…';
      simT = setInterval(function () {
        var i = ANIOS.indexOf(simY);
        if (i >= ANIOS.length - 1) { pausa(true); return; }
        irA(ANIOS[i + 1]);
        if (i + 1 === ANIOS.length - 1) pausa(true);
      }, 450);
    }
    function ceros() {
      if (simT) { clearInterval(simT); simT = null; }
      simY = null;
      sPlay.textContent = '▶ Recorrer los sexenios';
      sPlay.setAttribute('aria-pressed', 'false');
      sTxt.textContent = 'Las cifras están en cero.';
      aplica();
    }
    function elige(y) {
      if (ANIOS.indexOf(y) < 0) return;
      if (simT) pausa(false);
      irA(y);
      sTxt.textContent = 'Viendo ' + y + '.';
      if (sPlay.textContent === '▶ Recorrer los sexenios') sPlay.textContent = '▶ Seguir recorriendo';
    }
    sPlay.addEventListener('click', function () { if (simT) pausa(false); else corre(); });
    sCero.addEventListener('click', ceros);
    sReg.addEventListener('input', function () { elige(+sReg.value); });
    document.getElementById('rdSimAdms').addEventListener('click', function (ev) {
      var bt = ev.target.closest('button[data-ir]');
      if (bt) elige(+bt.getAttribute('data-ir'));
    });
    document.getElementById('rdGrafSvg').addEventListener('pointerdown', function (ev) {
      var svg = ev.currentTarget.querySelector('svg');
      if (!svg) return;
      var rc = svg.getBoundingClientRect(), x = (ev.clientX - rc.left) / rc.width * W;
      elige(Math.floor(X0 + (x - ML) / (W - ML - MR) * (X1 - X0)));
    });
    document.getElementById('rdGrafTabs').addEventListener('click', function (ev) {
      var bt = ev.target.closest('button[data-graf]');
      if (bt) { gAct = bt.getAttribute('data-graf'); pintaGraf(); }
    });
    document.getElementById('rdSimCuenta').hidden = false;
    document.getElementById('rdSimReg').hidden = false;
    pintaGraf();
    ceros();
    }

    /* ---- El peso en cada sexenio ---- */
    function tc(x, s) {
      if (!x || !tieneV(x)) return '<span class="rd-pt-v">' + sinDato(x) + '</span>' + (x && x.na ? '<small class="rd-motivo">' + esc(x.na) + '</small>' : '');
      return '<span class="rd-pt-v">' + pesos(x.rec, 2) + ' → ' + pesos(x.ent, 2) + '</span> <span class="rd-pt-d">' + (x.v > 0 ? '+' : '') + num(x.v, 1) + '%</span> ' + chip(x.est);
    }
    var ops = [], rdTabla = document.getElementById('rdPesoTabla');
    if (rdTabla) rdTabla.innerHTML = '<div class="rd-pt">' + P.admins.map(function (f) {
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
    if (document.getElementById('rdMaq')) {
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
  }
})();
