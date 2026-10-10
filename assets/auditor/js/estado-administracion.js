/* Expide el estado de cuenta de una administración (radar-estado-de-cuenta.html,
   10-10-2026). Toma las cifras del Radar hacendario (el JSON #rdDatos que arma
   herramientas/apartados.py) y las ordena en un documento descargable en PDF,
   con un semáforo de su salud financiera y un sello de verificación.
   Aquí no se escribe ninguna cifra: todo sale del JSON, y lo que se calcula
   (el balance, la deuda por año, los cortes del semáforo) dice su operación.
   El sello: la huella SHA-256 de las cifras del documento. El folio sale de
   la huella, así que el mismo contenido da siempre el mismo folio, y la
   sección «Verifica» recalcula las huellas para comprobar que un documento
   no se alteró. */
(function () {
  'use strict';
  var nodo = document.getElementById('rdDatos'), app = document.getElementById('exApp');
  if (!nodo || !app) return;
  var D;
  try { D = JSON.parse(nodo.textContent); } catch (e) { return; }
  var P = D.peso || {};

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function num(v, d) { return v.toLocaleString('es-MX', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function signo(v, d) { return (v > 0 ? '+' : v < 0 ? '−' : '') + num(Math.abs(v), d); }
  function fmt(v, u) {
    var a = Math.abs(v), s = v < 0 ? '−' : '';
    if (u === 'pib') return s + num(a, 1) + '% del PIB';
    if (u === 'pp') return signo(v, 1) + ' puntos del PIB';
    if (u === 'ppa') return signo(v, 2) + ' puntos del PIB al año';
    if (u === 'hoy') return s + (a >= 1e6 ? '$' + num(a / 1e6, 2) + ' billones' : '$' + num(a / 1e3, 1) + ' mil millones');
    if (u === 'mdp') return s + (a >= 1e6 ? '$' + num(a / 1e6, 2) + ' billones' : a >= 1e3 ? '$' + num(a / 1e3, 1) + ' mil millones' : '$' + num(a, 1) + ' millones');
    if (u === 'seg') return s + '$' + num(a, 0) + ' por segundo';
    if (u === 'ent') return num(Math.round(a), 0);
    if (u === 'pct') return signo(v, 1) + '%';
    return String(v);
  }
  function chip(e, pid) {
    var t = (e === 'oficial' || e === 'pendiente') ? e : 'derivado';
    return '<span class="est-chip est-' + t + '"' + (pid ? ' data-pend="' + esc(pid) + '"' : '') + '>' + t + '</span>';
  }
  function tieneV(x) { return x && typeof x.v === 'number'; }
  function val(a, m) { return (D.valores[a] || {})[m] || { pend: 'Sin dato.' }; }
  function adm(id) { for (var i = 0; i < D.admins.length; i++) if (D.admins[i].id === id) return D.admins[i]; return null; }
  function pesoDe(id) { for (var i = 0; i < (P.admins || []).length; i++) if (P.admins[i].id === id) return P.admins[i]; return null; }
  function unir(a, b) { var r = (a || []).slice(); (b || []).forEach(function (k) { if (r.indexOf(k) < 0) r.push(k); }); return r; }
  var cerradas = D.admins.filter(function (a) { return !a.curso; });

  /* ================= El semáforo ================= */
  function anios(a) { return a.curso ? (a.ys[1] - a.ys[0] + 1) : (a.a[1] - a.a[0] + 1); }
  function indicador(s, a) {
    if (s.excluye && s.excluye[a.id]) return { na: s.excluye[a.id] };
    var c = s.calc;
    if (c[0] === 'directo') return val(a.id, c[1]);
    if (c[0] === 'resta') {
      var x = val(a.id, c[1]), y = val(a.id, c[2]);
      if (!tieneV(x) || !tieneV(y)) return tieneV(x) ? y : x;
      return { v: Math.round((x.v - y.v) * 10) / 10, est: 'derivado', f: unir(x.f, y.f), op: num(x.v, 1) + ' − ' + num(y.v, 1) + ' = ' + signo(x.v - y.v, 1) + ' puntos del PIB.' };
    }
    if (c[0] === 'por_anio') {
      var z = val(a.id, c[1]), n = anios(a);
      if (!tieneV(z)) return z;
      return { v: Math.round(z.v / n * 100) / 100, est: 'derivado', f: z.f, op: signo(z.v, 1) + ' puntos del PIB ÷ ' + n + (n === 1 ? ' año' : ' años') + ' = ' + signo(z.v / n, 2) + ' al año.' };
    }
    return { pend: 'Sin dato.' };
  }
  /* Los cortes: el rango de las administraciones cerradas, en tres tercios. */
  var CORTES = {};
  D.semaforo.forEach(function (s) {
    var xs = cerradas.map(function (a) { return { a: a, x: indicador(s, a) }; }).filter(function (o) { return tieneV(o.x); });
    if (xs.length < 3) { CORTES[s.id] = null; return; }
    xs.sort(function (p, q) { return p.x.v - q.x.v; });
    var lo = xs[0], hi = xs[xs.length - 1], t = (hi.x.v - lo.x.v) / 3;
    var mejor = s.mejor === 'alto' ? hi : lo, peor = s.mejor === 'alto' ? lo : hi;
    CORTES[s.id] = { n: xs.length, mejor: mejor, peor: peor,
      c1: s.mejor === 'alto' ? hi.x.v - t : lo.x.v + t, c2: s.mejor === 'alto' ? hi.x.v - 2 * t : lo.x.v + 2 * t };
  });
  function color(s, v) {
    var k = CORTES[s.id];
    if (!k) return null;
    if (s.mejor === 'alto') return v >= k.c1 ? 'verde' : v >= k.c2 ? 'ambar' : 'rojo';
    return v <= k.c1 ? 'verde' : v <= k.c2 ? 'ambar' : 'rojo';
  }
  var COLOR = { verde: ['🟢', 'Verde', 'en el tercio mejor'], ambar: ['🟡', 'Ámbar', 'en el tercio de en medio'], rojo: ['🔴', 'Rojo', 'en el tercio peor'] };
  function regla(s) {
    var k = CORTES[s.id];
    if (!k) return '';
    var u = s.u === 'ppa' ? 2 : 1, alto = s.mejor === 'alto';
    return 'De las ' + k.n + ' administraciones cerradas con este dato, la mejor fue ' + k.mejor.a.c + ' (' + fmt(k.mejor.x.v, s.u) + ') y la peor, ' +
      k.peor.a.c + ' (' + fmt(k.peor.x.v, s.u) + '). Ese rango se parte en tres tercios iguales: verde si ' + (alto ? '≥ ' : '≤ ') + num(k.c1, u) +
      '; ámbar entre ' + num(Math.min(k.c1, k.c2), u) + ' y ' + num(Math.max(k.c1, k.c2), u) + '; rojo si ' + (alto ? '< ' : '> ') + num(k.c2, u) + '.';
  }

  /* ================= El contenido del documento ================= */
  /* Un solo modelo para pintar y para la huella: lo que se ve es lo que se firma. */
  function modelo(a) {
    var m = { a: a, cuenta: [], deuda: [], peso: [], asf: [], sem: [], fuentes: [] };
    function f(x) { if (x && x.f) m.fuentes = unir(m.fuentes, x.f); return x; }
    function hoyDe(serie) { var x = val(a.id, serie + '_mdp'); return x.alt ? x.alt.hoy : x; }
    var ing = hoyDe('ingresos'), gas = hoyDe('gasto');
    var bal = (tieneV(ing) && tieneV(gas)) ? { v: Math.round((ing.v - gas.v) * 10) / 10, est: 'derivado', f: unir(ing.f, gas.f),
      op: 'Ingresos en pesos de hoy menos gasto en pesos de hoy.' } : (tieneV(ing) ? gas : ing);
    var balPib = indicador(D.semaforo[0], a);
    [['💰', 'Ingresos presupuestarios', val(a.id, 'ingresos_pib'), ing],
     ['🏛️', 'Gasto neto total', val(a.id, 'gasto_pib'), gas],
     ['⚖️', 'Balance (ingresos − gasto)', balPib, bal],
     ['💸', 'Intereses de la deuda (costo financiero)', val(a.id, 'costo_financiero_pib'), hoyDe('costo_financiero')],
     ['🏗️', 'Inversión física', val(a.id, 'inversion_pib'), hoyDe('inversion')]
    ].forEach(function (r) { m.cuenta.push({ ico: r[0], tit: r[1], pib: f(r[2]), hoy: f(r[3]) }); });
    [['Deuda al recibir', val(a.id, 'deuda_ini'), 'pib'], ['Deuda al cierre', val(a.id, 'deuda_fin'), 'pib'],
     ['Cambio en el periodo', val(a.id, 'deuda_cambio'), 'pp'], ['Lo que creció por segundo', val(a.id, 'deuda_seg'), 'seg']
    ].forEach(function (r) { m.deuda.push({ tit: r[0], x: f(r[1]), u: r[2] }); });
    var pz = pesoDe(a.id);
    if (pz) {
      m.peso.push({ tit: 'Inflación acumulada (' + pz.rec + ' a ' + pz.ent + ')', x: f(pz.infl), u: 'pct' });
      m.peso.push({ tit: '$100 de ' + pz.rec + ' valían al cierre', x: f(pz.cien), u: 'cien' });
      if (tieneV(pz.usd)) m.peso.push({ tit: 'Dólar: de $' + num(pz.usd.rec, 2) + ' a $' + num(pz.usd.ent, 2), x: f(pz.usd), u: 'pct' });
      else m.peso.push({ tit: 'Dólar', x: pz.usd, u: 'pct' });
      if (tieneV(pz.eur)) m.peso.push({ tit: 'Euro: de $' + num(pz.eur.rec, 2) + ' a $' + num(pz.eur.ent, 2), x: f(pz.eur), u: 'pct' });
      else m.peso.push({ tit: 'Euro', x: pz.eur, u: 'pct' });
    }
    [['Auditorías practicadas', val(a.id, 'asf_aud'), 'ent'], ['Recuperaciones operadas', val(a.id, 'asf_rec'), 'mdp'],
     ['Monto por aclarar', val(a.id, 'asf_acl'), 'mdp']
    ].forEach(function (r) { m.asf.push({ tit: r[0], x: f(r[1]), u: r[2] }); });
    D.semaforo.forEach(function (s) {
      var x = f(indicador(s, a));
      m.sem.push({ s: s, x: x, c: tieneV(x) ? color(s, x.v) : null });
    });
    return m;
  }
  /* Las cifras que firma el sello, en un orden fijo. */
  function cifras(m) {
    function v(x) { return tieneV(x) ? x.v : 'sin dato'; }
    return {
      doc: 'Auditavisión · Estado de cuenta de la administración', adm: m.a.id, corte: D.corte,
      cuenta: m.cuenta.map(function (r) { return [r.tit, v(r.pib), v(r.hoy)]; }),
      deuda: m.deuda.map(function (r) { return [r.tit, v(r.x)]; }),
      peso: m.peso.map(function (r) { return [r.tit, v(r.x)]; }),
      asf: m.asf.map(function (r) { return [r.tit, v(r.x)]; }),
      semaforo: m.sem.map(function (r) { return [r.s.id, v(r.x), r.c || 'sin color']; })
    };
  }
  function huella(m) {
    if (!(window.crypto && crypto.subtle && window.TextEncoder)) return Promise.resolve(null);
    var txt = JSON.stringify(cifras(m));
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(txt)).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return ('0' + x.toString(16)).slice(-2); }).join('');
    });
  }
  function folio(a, h) { return 'AV-' + a.ini.replace(/[^A-Z]/gi, '').toUpperCase() + '-' + h.slice(0, 8).toUpperCase(); }

  /* ================= Pintar ================= */
  function valor(x, u) {
    if (tieneV(x)) {
      var t = u === 'cien' ? '$' + num(x.v, 2) : fmt(x.v, u);
      return '<b class="ex-v">' + t + '</b> ' + chip(x.est);
    }
    if (x && x.na) return '<span class="ex-na">' + esc(x.et || 'no aplica') + '</span>';
    return chip('pendiente', x && x.pid);
  }
  function porque(x) {
    if (tieneV(x)) return (x.op ? '<small class="ex-op">' + esc(x.op) + '</small>' : '') + (x.nota ? '<small class="ex-op">' + esc(x.nota) + '</small>' : '');
    return '<small class="ex-op">' + esc((x && (x.pend || x.na)) || '') + '</small>';
  }
  function tabla(filas, cab) {
    return '<table class="ex-t"><thead><tr>' + cab.map(function (c) { return '<th scope="col">' + c + '</th>'; }).join('') + '</tr></thead><tbody>' + filas + '</tbody></table>';
  }
  function hoyFecha() {
    var d = new Date();
    return d.toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' }) + ', ' + d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
  }
  function selloSitio() { var b = document.querySelector('.apartado-pie-txt b'); return b ? b.textContent : ''; }
  function ligaVerifica(fol) { return location.origin + location.pathname + '?verifica=' + encodeURIComponent(fol); }

  function sello(fol) {
    var id = 'exArco' + Math.random().toString(36).slice(2, 7);
    return '<svg class="ex-sello-svg" viewBox="0 0 120 120" role="img" aria-label="Sello de verificación de Auditavisión">' +
      '<defs><path id="' + id + '" d="M60,60 m-44,0 a44,44 0 1,1 88,0 a44,44 0 1,1 -88,0"/></defs>' +
      '<circle cx="60" cy="60" r="57" fill="none" stroke="currentColor" stroke-width="2.5"/>' +
      '<circle cx="60" cy="60" r="35" fill="none" stroke="currentColor" stroke-width="1.2"/>' +
      '<text font-size="9.4" font-weight="800" letter-spacing="1.3" fill="currentColor"><textPath href="#' + id + '">AUDITAVISIÓN · SELLO DE VERIFICACIÓN ·</textPath></text>' +
      '<text x="60" y="58" text-anchor="middle" font-size="22" font-weight="900" fill="currentColor">✓</text>' +
      '<text x="60" y="74" text-anchor="middle" font-size="7.5" font-weight="800" fill="currentColor">' + esc(fol ? fol.split('-').slice(-1)[0] : '········') + '</text></svg>';
  }

  var est = { adm: null };
  function pinta() {
    var a = adm(est.adm), m = modelo(a);
    var doc = document.getElementById('exDoc');
    var h = '<header class="ex-doc-cab" style="--c:' + a.col + '">' +
      '<div class="ex-marca"><img src="assets/auditor/img/logo-auditavision.svg" alt="" width="54" height="42"><div><b>Auditavisión</b><small>El gasto público, a la vista</small></div></div>' +
      '<div class="ex-doc-tit"><span class="ex-doc-tipo">Estado de cuenta de la administración</span><h3>' + esc(a.n) + '</h3>' +
      '<span>' + esc(a.periodo) + (a.ys ? ' · cifras de ' + a.ys[0] + (a.ys[1] !== a.ys[0] ? ' a ' + a.ys[1] : '') : '') + '</span></div>' +
      '<dl class="ex-meta"><div><dt>Folio</dt><dd class="ex-folio">calculando…</dd></div><div><dt>Expedido</dt><dd>' + esc(hoyFecha()) + '</dd></div>' +
      '<div><dt>Datos con corte al</dt><dd>' + esc(D.corte) + '</dd></div></dl></header>';
    if (a.aviso) h += '<p class="ex-aviso">⚠️ ' + esc(a.aviso) + (a.curso ? ' El semáforo es <b>preliminar</b>: se compara un año contra sexenios completos.' : '') + '</p>';

    /* 1. Semáforo */
    var cuenta = { verde: 0, ambar: 0, rojo: 0 };
    m.sem.forEach(function (r) { if (r.c) cuenta[r.c]++; });
    h += '<section class="ex-sec"><h4><span>1</span> Salud financiera: el semáforo' + (a.curso ? ' <em class="ex-prelim">preliminar</em>' : '') + '</h4>' +
      '<p class="ex-resumen">' + ['verde', 'ambar', 'rojo'].map(function (c) { return '<span class="ex-cuenta ex-' + c + '">' + COLOR[c][0] + ' ' + cuenta[c] + ' en ' + COLOR[c][1].toLowerCase() + '</span>'; }).join('') + '</p>' +
      '<div class="ex-sem">' + m.sem.map(function (r) {
        var c = r.c ? COLOR[r.c] : null;
        return '<div class="ex-sem-i ' + (r.c ? 'ex-' + r.c : 'ex-gris') + '"><div class="ex-sem-cab"><span class="ex-luz" aria-hidden="true">' + (c ? c[0] : '⚪') + '</span>' +
          '<b>' + r.s.ico + ' ' + esc(r.s.tit) + '</b><span class="ex-sem-c">' + (c ? c[1] + ', ' + c[2] : 'Sin color') + '</span></div>' +
          '<p class="ex-sem-v">' + valor(r.x, r.s.u) + '</p><p class="ex-sem-que">' + esc(r.s.que) + '</p>' + porque(r.x) +
          '<small class="ex-regla">' + esc(regla(r.s)) + '</small></div>';
      }).join('') + '</div>' +
      '<p class="ex-nota">El semáforo compara con reglas escritas; no es una calificación oficial ni un juicio sobre la persona. ' +
      'Más ingreso o más inversión no son por sí solos mejores, ni menos deuda peor: dependen de cómo estaba la economía. ' +
      esc(D.ley17.txt) + ' <a href="' + esc(D.ley17.url) + '" target="_blank" rel="noopener noreferrer">' + esc(D.ley17.corto) + ' ↗</a></p></section>';

    /* 2. Estado de cuenta */
    h += '<section class="ex-sec"><h4><span>2</span> Lo que entró y lo que salió</h4>' + tabla(m.cuenta.map(function (r) {
      return '<tr><th scope="row">' + r.ico + ' ' + esc(r.tit) + '</th><td>' + valor(r.pib, 'pib') + porque(r.pib) + '</td><td>' + valor(r.hoy, 'hoy') + '</td></tr>';
    }).join(''), ['Concepto', 'Promedio al año', 'Suma del periodo, en pesos de ' + esc((P.ref && P.ref.mes) || 'hoy')]) +
      '<p class="ex-nota">El % del PIB compara el tamaño contra la economía de cada año. La suma en pesos de hoy ya no tiene inflación: cada año se lleva a pesos de ' + esc((P.ref && P.ref.mes) || 'hoy') + ' con el INPC.</p></section>';

    /* 3. Deuda */
    h += '<section class="ex-sec"><h4><span>3</span> La deuda pública</h4>' + tabla(m.deuda.map(function (r) {
      return '<tr><th scope="row">' + esc(r.tit) + '</th><td>' + valor(r.x, r.u) + porque(r.x) + '</td></tr>';
    }).join(''), ['Concepto', 'Cifra']) + '</section>';

    /* 4. El peso */
    if (m.peso.length) h += '<section class="ex-sec"><h4><span>4</span> El peso durante su gobierno</h4>' + tabla(m.peso.map(function (r) {
      return '<tr><th scope="row">' + esc(r.tit) + '</th><td>' + valor(r.x, r.u) + porque(r.x) + '</td></tr>';
    }).join(''), ['Concepto', 'Cifra']) + '<p class="ex-nota">Dólar y euro: pesos por cada uno. Un porcentaje positivo es que el peso se depreció; negativo, que se apreció.</p></section>';

    /* 5. ASF */
    h += '<section class="ex-sec"><h4><span>5</span> Ante la Auditoría Superior de la Federación</h4>' + tabla(m.asf.map(function (r) {
      return '<tr><th scope="row">' + esc(r.tit) + '</th><td>' + valor(r.x, r.u) + porque(r.x) + '</td></tr>';
    }).join(''), ['Concepto', 'Cifra']) +
      '<p class="ex-nota">Sin color en el semáforo: la ASF mide el monto por aclarar con esta definición solo desde la Cuenta Pública 2019, y las cuentas viejas llevan más años de solventación. No es daño comprobado.</p></section>';

    /* 6. Fuentes */
    h += '<section class="ex-sec"><h4><span>6</span> Fuentes oficiales</h4><ol class="ex-fuentes">' + m.fuentes.map(function (k) {
      var x = D.fuentes[k];
      return x ? '<li><a href="' + esc(x.url) + '" target="_blank" rel="noopener noreferrer">' + esc(x.corto) + '</a> <small>' + esc(x.url) + '</small></li>' : '';
    }).join('') + '</ol><p class="ex-nota">Estados de cada cifra: <b>oficial</b>, tomada tal cual de su documento; <b>derivado</b>, calculada con cifras oficiales, con la operación dicha; <b>pendiente</b>, falta el documento y queda en el <a href="pendientes.html">Registro de pendientes</a>.</p></section>';

    /* Sello */
    h += '<footer class="ex-sello"><div class="ex-sello-img">' + sello(null) + '</div><div class="ex-sello-tx">' +
      '<b>Sello de verificación de Auditavisión</b>' +
      '<p>Folio <b class="ex-folio">calculando…</b> · Versión de la plataforma <b>' + esc(selloSitio()) + '</b></p>' +
      '<p class="ex-huella">Huella digital (SHA-256 de las cifras): <code id="exHuella">calculando…</code></p>' +
      '<p>Compruébalo en <span class="ex-liga" id="exLigaTx"></span></p>' +
      '<p class="ex-leyenda">Lo expide Auditavisión, plataforma ciudadana de fiscalización del gasto público. <b>No es un documento oficial</b> del gobierno ni de la Auditoría Superior. El sello certifica dos cosas: que cada cifra proviene de la fuente oficial citada, y que el contenido no se ha alterado desde que se expidió. Si cambia una sola cifra, la huella ya no coincide.</p>' +
      '</div></footer>';
    doc.innerHTML = h;
    doc.style.setProperty('--c', a.col);
    huella(m).then(function (hx) {
      var fol = hx ? folio(a, hx) : null;
      est.folio = fol;
      Array.prototype.forEach.call(doc.querySelectorAll('.ex-folio'), function (el) { el.textContent = fol || 'no disponible en este navegador'; });
      document.getElementById('exHuella').textContent = hx ? hx.replace(/(.{16})/g, '$1 ').trim() : 'no disponible en este navegador';
      document.getElementById('exLigaTx').textContent = fol ? ligaVerifica(fol) : location.origin + location.pathname;
      doc.querySelector('.ex-sello-img').innerHTML = sello(fol);
    });
  }

  function pintaAdmins() {
    document.getElementById('exAdmins').innerHTML = D.admins.map(function (a) {
      return '<button type="button" class="rd-admin" role="radio" aria-checked="' + (a.id === est.adm) + '" aria-selected="' + (a.id === est.adm) + '" data-adm="' + a.id + '" style="--c:' + a.col + '">' +
        '<span class="rd-admin-ini" aria-hidden="true">' + esc(a.ini) + '</span>' +
        '<span class="rd-admin-tx"><b>' + esc(a.c) + '</b><small>' + a.a[0] + '–' + a.a[1] + (a.curso ? ' · en curso' : '') + '</small></span></button>';
    }).join('');
  }
  function elige(id, empujar) {
    if (!adm(id)) return;
    est.adm = id;
    pintaAdmins();
    pinta();
    if (empujar) history.replaceState(null, '', location.pathname + '?adm=' + id);
  }
  document.getElementById('exAdmins').addEventListener('click', function (e) {
    var b = e.target.closest('[data-adm]');
    if (b) elige(b.getAttribute('data-adm'), true);
  });

  /* ================= Descargar en PDF ================= */
  document.getElementById('exPdf').addEventListener('click', function () {
    var viejo = document.getElementById('exPrint');
    if (viejo) viejo.remove();
    var c = document.createElement('div');
    c.id = 'exPrint';
    c.className = 'ex-print';
    c.innerHTML = '<article class="ex-doc">' + document.getElementById('exDoc').innerHTML + '</article>';
    c.firstChild.style.setProperty('--c', adm(est.adm).col);
    document.body.appendChild(c);
    var t = document.title;
    document.title = 'Estado de cuenta ' + adm(est.adm).c + (est.folio ? ' ' + est.folio : '') + ' · Auditavisión';
    window.print();
    setTimeout(function () { document.title = t; }, 500);
  });
  window.addEventListener('afterprint', function () { var c = document.getElementById('exPrint'); if (c) c.remove(); });
  document.getElementById('exLiga').addEventListener('click', function () {
    var url = location.origin + location.pathname + '?adm=' + est.adm, b = this;
    (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(function () {
      b.textContent = '✓ Enlace copiado';
    }, function () { b.textContent = url; }).then(function () { setTimeout(function () { b.textContent = '🔗 Copiar el enlace'; }, 2500); });
  });

  /* ================= Verificar ================= */
  function verifica(q) {
    var out = document.getElementById('exVerOut');
    q = String(q || '').trim().replace(/\s+/g, '');
    if (!q) { out.innerHTML = ''; return; }
    out.innerHTML = '<p class="ex-ver ex-ver-esp">⏳ Comprobando…</p>';
    Promise.all(D.admins.map(function (a) { return huella(modelo(a)).then(function (h) { return { a: a, h: h }; }); })).then(function (rs) {
      if (!rs[0].h) { out.innerHTML = '<p class="ex-ver ex-ver-no">Este navegador no puede calcular huellas SHA-256. Ábrelo en uno actualizado.</p>'; return; }
      var Q = q.toUpperCase(), hit = null;
      rs.forEach(function (r) { if (folio(r.a, r.h) === Q || r.h.toUpperCase() === Q) hit = r; });
      if (hit) {
        out.innerHTML = '<div class="ex-ver ex-ver-si"><b>✅ Auténtico.</b> Corresponde al estado de cuenta de <b>' + esc(hit.a.n) + '</b>, y sus cifras coinciden con los datos vigentes (corte al ' + esc(D.corte) + ').' +
          '<br><small>Huella: <code>' + hit.h + '</code></small> <button type="button" class="sz-btn" data-ver-adm="' + hit.a.id + '">Ver el documento</button></div>';
      } else {
        out.innerHTML = '<div class="ex-ver ex-ver-no"><b>❌ No coincide</b> con ningún estado de cuenta de los datos vigentes (corte al ' + esc(D.corte) + '). ' +
          'O el documento se alteró, o se expidió con datos anteriores: en ese caso, expídelo de nuevo y compara las cifras.</div>';
      }
    });
  }
  document.getElementById('exVerForm').addEventListener('submit', function (e) { e.preventDefault(); verifica(document.getElementById('exVerIn').value); });
  document.getElementById('exVerOut').addEventListener('click', function (e) {
    var b = e.target.closest('[data-ver-adm]');
    if (!b) return;
    elige(b.getAttribute('data-ver-adm'), true);
    document.getElementById('exDoc').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  /* ================= Arranque ================= */
  var q = new URLSearchParams(location.search);
  var ultimo = D.admins[D.admins.length - 1].id;
  elige(adm(q.get('adm')) ? q.get('adm') : ultimo, false);
  if (q.get('verifica')) {
    document.getElementById('exVerIn').value = q.get('verifica');
    verifica(q.get('verifica'));
    setTimeout(function () { document.getElementById('exVerifica').scrollIntoView({ block: 'start' }); }, 300);
  }
})();
