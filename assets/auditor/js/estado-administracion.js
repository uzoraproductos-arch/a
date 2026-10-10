/* Expide el estado de cuenta de una administración (radar-estado-de-cuenta.html,
   10-10-2026). Toma las cifras del Radar hacendario (el JSON #rdDatos que arma
   herramientas/apartados.py) y las ordena en un documento descargable en PDF,
   con un semáforo de su salud financiera y un sello de verificación.
   Aquí no se escribe ninguna cifra: todo sale del JSON, y lo que se calcula
   (el balance, la deuda por año, los cortes del semáforo) dice su operación.
   El sello: la huella SHA-256 de las cifras del documento. El folio sale de
   la huella, así que el mismo contenido da siempre el mismo folio, y la
   sección «Verifica» recalcula las huellas para comprobar que un documento
   no se alteró. Esa sección se mudó al Modo Inspector el 10-10-2026
   (herramienta-inspector-verifica.html, pedido del autor): el mismo archivo
   la arranca sola cuando la página no trae el expedidor (#exDoc), y el
   expedidor manda ahí los enlaces ?verifica= de los PDF ya impresos.
   Desde el mismo 10-10-2026 expide también el de quienes legislan y juzgan:
   la diputación federal, la de cada congreso local y la Suprema Corte con su
   ponencia y sus asesores. Esos documentos los arma apartados.py en el JSON
   #exCargos (radar_cargos), cifra por cifra con su fuente y su página; aquí
   solo se pintan y se firman con el mismo sello.
   Desde el mismo día, el documento es una hoja oficio por los dos lados:
   anverso con el termostato y las cuentas, reverso con las notas, el
   fundamento, las fuentes y el sello. La huella no cambió: firma las mismas
   cifras, así que los folios ya expedidos siguen valiendo.
   El sello se titula «Dictamen técnico de Auditavisión» desde el
   10-10-2026 (pedido del autor); antes decía «Sello de verificación». */
(function () {
  'use strict';
  var nodo = document.getElementById('rdDatos'), app = document.getElementById('exApp');
  if (!nodo || !app) return;
  var D;
  try { D = JSON.parse(nodo.textContent); } catch (e) { return; }
  var P = D.peso || {};
  var C = null, nc = document.getElementById('exCargos');
  if (nc) { try { C = JSON.parse(nc.textContent); } catch (e) { C = null; } }
  /* La verificación tiene su página en el Modo Inspector; esta, sin #exDoc, es ella. */
  var VERIFICA = 'herramienta-inspector-verifica.html', SOLO = !document.getElementById('exDoc');

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
  function huella(m) { return huellaDe(cifras(m)); }
  function huellaDe(obj) {
    if (!(window.crypto && crypto.subtle && window.TextEncoder)) return Promise.resolve(null);
    var txt = JSON.stringify(obj);
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(txt)).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return ('0' + x.toString(16)).slice(-2); }).join('');
    });
  }
  function folio(ini, h) { return 'AV-' + ini.replace(/[^A-Z]/gi, '').toUpperCase() + '-' + h.slice(0, 8).toUpperCase(); }

  /* ================= Pintar ================= */
  /* La hoja (pedido del autor, 10-10-2026): tamaño oficio, por los dos lados.
     El anverso da lo importante de un vistazo: el termostato de la salud
     financiera y las cuentas, cifra por cifra, con los negativos en rojo.
     El reverso lo justifica por secciones: qué mide cada cifra, cómo se
     calculó, su fundamento y su fuente, y al final el sello. Cada cifra del
     anverso lleva un número que remite a su nota en el reverso. */
  function Notas(fuentes) { this.secs = []; this.n = 0; this.fs = fuentes; }
  Notas.prototype.sec = function (tit, nota) { this.cur = { tit: tit, nota: nota || '', l: [] }; this.secs.push(this.cur); };
  Notas.prototype.add = function (html) {
    if (!html) return '';
    this.n++;
    this.cur.l.push('<li value="' + this.n + '">' + html + '</li>');
    return '<sup class="ex-ref">' + this.n + '</sup>';
  };
  Notas.prototype.f = function (ks) {
    var fs = this.fs, r = [];
    (typeof ks === 'string' ? [ks] : ks || []).forEach(function (k) { var i = fs.indexOf(k); if (i >= 0 && r.indexOf('F' + (i + 1)) < 0) r.push('F' + (i + 1)); });
    return r.length ? '<span class="ex-nf">Fuente: ' + r.join(', ') + '</span>' : '';
  };
  Notas.prototype.html = function (n0) {
    return this.secs.map(function (s, i) {
      return '<section class="ex-rsec"><h4><span>' + (n0 + i) + '</span> ' + esc(s.tit) + '</h4>' +
        (s.l.length ? '<ol class="ex-notas">' + s.l.join('') + '</ol>' : '') + (s.nota ? '<p class="ex-nota">' + s.nota + '</p>' : '') + '</section>';
    }).join('');
  };
  function neg(v) { return typeof v === 'number' && v < 0; }
  function cifraV(t, v, e, pid, ref) {
    return '<b class="ex-v' + (neg(v) ? ' ex-neg' : '') + '">' + t + '</b>' + chip(e, pid) + (ref || '');
  }
  function valor(x, u, ref) {
    if (tieneV(x)) return cifraV(u === 'cien' ? '$' + num(x.v, 2) : fmt(x.v, u), x.v, x.est, null, ref);
    if (x && x.na) return '<span class="ex-na">' + esc(x.et || 'no aplica') + '</span>' + (ref || '');
    return chip('pendiente', x && x.pid) + (ref || '');
  }
  function notaA(N, x, extra) {
    var p = extra ? [extra] : [];
    if (tieneV(x)) { if (x.op) p.push(esc(x.op)); if (x.nota) p.push(esc(x.nota)); }
    else if (x && (x.pend || x.na)) p.push(esc(x.pend || x.na));
    var f = N.f(x && x.f);
    if (f) p.push(f);
    return p.join(' ');
  }
  function tabla(filas, cab) {
    return '<table class="ex-t"><thead><tr>' + cab.map(function (c) { return '<th scope="col">' + c + '</th>'; }).join('') + '</tr></thead><tbody>' + filas + '</tbody></table>';
  }
  function caja(tit, cuerpo, ancho) { return '<section class="ex-caja' + (ancho ? ' ex-caja-ancha' : '') + '"><h4>' + tit + '</h4>' + cuerpo + '</section>'; }
  /* Las cajas del anverso, repartidas en dos columnas: cada una va a la
     columna con menos renglones, en orden, para que no queden huecos. */
  function columnas(ancha, cs) {
    var col = [[], []], peso = [0, 0], largas = [];
    cs.forEach(function (c, k) {
      if (c.larga) { largas.push(c.h); return; }
      var i = peso.indexOf(Math.min.apply(null, peso));
      col[i].push(c.h.replace('<section class="ex-caja', '<section data-i="' + k + '" style="order:' + k + '" class="ex-caja'));
      peso[i] += c.n + 2;
    });
    return (ancha || '') + '<div class="ex-cajas">' + col.map(function (x) { return '<div class="ex-col">' + x.join('') + '</div>'; }).join('') + '</div>' + largas.join('');
  }
  function hoyFecha() {
    var d = new Date();
    return d.toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' }) + ', ' + d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
  }
  function selloSitio() { var b = document.querySelector('.apartado-pie-txt b'); return b ? b.textContent : ''; }
  function ligaVerifica(fol) { return new URL(VERIFICA + '?verifica=' + encodeURIComponent(fol), location.href).href; }

  function sello(fol) {
    var id = 'exArco' + Math.random().toString(36).slice(2, 7);
    return '<svg class="ex-sello-svg" viewBox="0 0 120 120" role="img" aria-label="Dictamen técnico de Auditavisión">' +
      '<defs><path id="' + id + '" d="M60,60 m-44,0 a44,44 0 1,1 88,0 a44,44 0 1,1 -88,0"/></defs>' +
      '<circle cx="60" cy="60" r="57" fill="none" stroke="currentColor" stroke-width="2.5"/>' +
      '<circle cx="60" cy="60" r="35" fill="none" stroke="currentColor" stroke-width="1.2"/>' +
      '<text font-size="9.4" font-weight="800" letter-spacing="3.15" fill="currentColor"><textPath href="#' + id + '">AUDITAVISIÓN · DICTAMEN TÉCNICO ·</textPath></text>' +
      '<text x="60" y="58" text-anchor="middle" font-size="22" font-weight="900" fill="currentColor">✓</text>' +
      '<text x="60" y="74" text-anchor="middle" font-size="7.5" font-weight="800" fill="currentColor">' + esc(fol ? fol.split('-').slice(-1)[0] : '········') + '</text></svg>';
  }

  /* La imagen del encabezado (data-cabecera de #exApp) va en todos los documentos. */
  var BANDA = document.getElementById('exApp').getAttribute('data-cabecera');
  function cabecera(col, tipo, titulo, sub, corteEt, corte) {
    return (BANDA ? '<div class="ex-banda"><img src="' + esc(BANDA) + '" alt=""></div>' : '') +
      '<header class="ex-doc-cab" style="--c:' + col + '">' +
      '<div class="ex-marca"><img src="assets/auditor/img/logo-auditavision.svg" alt="" width="104" height="81" decoding="sync"><div><b>Auditavisión</b><small>El gasto público, a la vista</small></div></div>' +
      '<div class="ex-doc-tit"><span class="ex-doc-tipo">' + esc(tipo) + '</span><h3>' + esc(titulo) + '</h3>' +
      '<span>' + esc(sub) + '</span></div>' +
      '<dl class="ex-meta"><div><dt>Folio</dt><dd class="ex-folio">calculando…</dd></div><div><dt>Expedido</dt><dd>' + esc(hoyFecha()) + '</dd></div>' +
      '<div><dt>' + esc(corteEt) + '</dt><dd>' + esc(corte) + '</dd></div></dl></header>';
  }
  /* Las dos caras de la hoja. */
  function hoja(anverso, titulo, reverso) {
    return '<div class="ex-cara ex-anverso">' + anverso +
      '<p class="ex-pag"><span>Hoja 1 de 2 · Anverso</span><span>Los números <sup class="ex-ref">1</sup> remiten a su nota en el reverso ↻</span></p></div>' +
      '<div class="ex-cara ex-reverso"><p class="ex-rev-cab"><span>Reverso · ' + esc(titulo) + '</span><span>Folio <b class="ex-folio">calculando…</b></span></p>' +
      reverso + pie() + '<p class="ex-pag"><span>Hoja 2 de 2 · Reverso</span><span>Auditavisión</span></p></div>';
  }
  function listaFuentes(ks, cat, n) {
    return '<section class="ex-rsec ex-rsec-fuentes"><h4><span>' + n + '</span> Fuentes oficiales</h4><ol class="ex-fuentes">' + ks.map(function (k, i) {
      var x = cat[k];
      return x ? '<li><b>F' + (i + 1) + '.</b> <a href="' + esc(x.url) + '" target="_blank" rel="noopener noreferrer">' + esc(x.corto) + '</a> <small>' + esc(x.url) + '</small></li>' : '';
    }).join('') + '</ol><p class="ex-nota">Estados de cada cifra: <b>oficial</b>, tomada tal cual de su documento; <b>derivado</b>, calculada con cifras oficiales, con la operación dicha; <b>pendiente</b>, falta el documento y queda en el <a href="pendientes.html">Registro de pendientes</a>. Las cifras negativas van en <b class="ex-neg">rojo</b>.</p></section>';
  }
  function pie() {
    return '<footer class="ex-sello"><div class="ex-sello-img">' + sello(null) + '</div><div class="ex-sello-tx">' +
      '<b>Dictamen técnico de Auditavisión</b>' +
      '<p>Folio <b class="ex-folio">calculando…</b> · Versión de la plataforma <b>' + esc(selloSitio()) + '</b></p>' +
      '<p class="ex-huella">Huella digital (SHA-256 de las cifras): <code id="exHuella">calculando…</code></p>' +
      '<p>Compruébalo en <span class="ex-liga" id="exLigaTx"></span></p>' +
      '<p class="ex-leyenda">Lo expide Auditavisión, plataforma ciudadana de fiscalización del gasto público. <b>No es un documento oficial</b> del gobierno, del Congreso, de la Corte ni de la Auditoría Superior. El sello certifica dos cosas: que cada cifra proviene de la fuente oficial citada, y que el contenido no se ha alterado desde que se expidió. Si cambia una sola cifra, la huella ya no coincide.</p>' +
      '</div></footer>';
  }
  function firma(doc, obj, ini) {
    huellaDe(obj).then(function (hx) {
      var fol = hx ? folio(ini, hx) : null;
      est.folio = fol;
      Array.prototype.forEach.call(doc.querySelectorAll('.ex-folio'), function (el) { el.textContent = fol || 'no disponible en este navegador'; });
      document.getElementById('exHuella').textContent = hx ? hx.replace(/(.{16})/g, '$1 ').trim() : 'no disponible en este navegador';
      document.getElementById('exLigaTx').textContent = fol ? ligaVerifica(fol) : location.origin + location.pathname;
      doc.querySelector('.ex-sello-img').innerHTML = sello(fol);
    });
  }

  /* ================= El termostato de la salud financiera ================= */
  var TONO = { verde: '#1f9d55', ambar: '#e0a800', rojo: '#d93025' };
  /* La rueda: un gajo por indicador, con su color. No suma ni promedia: no hay calificación global. */
  function rueda(cs, ics) {
    var n = cs.length, R = 42, L = 2 * Math.PI * R, g = n > 1 ? 3 : 0, cuenta = { verde: 0, ambar: 0, rojo: 0, gris: 0 };
    cs.forEach(function (c) { cuenta[c || 'gris']++; });
    var arcos = cs.map(function (c, i) {
      return '<circle cx="60" cy="60" r="' + R + '" fill="none" stroke="' + (TONO[c] || '#c9d3e6') + '" stroke-width="16" stroke-dasharray="' +
        (L / n - g).toFixed(2) + ' ' + (L - L / n + g).toFixed(2) + '" stroke-dashoffset="' + (-L * i / n).toFixed(2) + '" transform="rotate(-90 60 60)"/>';
    }).join('');
    var iconos = ics.map(function (ic, i) {
      var a = (i + 0.5) / n * 2 * Math.PI - Math.PI / 2;
      return '<text x="' + (60 + R * Math.cos(a)).toFixed(1) + '" y="' + (60 + R * Math.sin(a) + 4).toFixed(1) + '" text-anchor="middle" font-size="11">' + ic + '</text>';
    }).join('');
    return '<div class="ex-rueda"><svg viewBox="0 0 120 120" role="img" aria-label="' + cuenta.verde + ' en verde, ' + cuenta.ambar + ' en ámbar, ' + cuenta.rojo + ' en rojo y ' + cuenta.gris + ' sin color, de ' + n + '">' +
      arcos + iconos + '<text x="60" y="60" text-anchor="middle" font-size="22" font-weight="900" fill="#1f9d55">' + cuenta.verde + '/' + n + '</text>' +
      '<text x="60" y="74" text-anchor="middle" font-size="8.5" font-weight="700" fill="#5a6782">en verde</text></svg>' +
      '<p class="ex-rueda-l">' + ['verde', 'ambar', 'rojo'].map(function (c) { return '<span><i style="background:' + TONO[c] + '"></i>' + cuenta[c] + ' ' + COLOR[c][1].toLowerCase() + '</span>'; }).join('') +
      (cuenta.gris ? '<span><i style="background:#c9d3e6"></i>' + cuenta.gris + ' sin color</span>' : '') + '</p></div>';
  }
  /* El medidor: una barra de peor a mejor, en tres tercios, con la marca donde cae la cifra. */
  function medidor(pos, c, zonas) {
    var z = zonas || [['rojo', 33.34], ['ambar', 33.33], ['verde', 33.33]];
    var fuera = pos !== null && (pos < 0 || pos > 1), p = pos === null ? null : Math.max(0, Math.min(1, pos)) * 100;
    return '<span class="ex-med' + (c ? '' : ' ex-med-gris') + '">' + z.map(function (x) { return '<i style="width:' + x[1] + '%;background:' + TONO[x[0]] + '"></i>'; }).join('') +
      (p === null ? '' : '<b class="ex-med-m' + (fuera ? ' ex-med-fuera' : '') + '" style="left:' + p.toFixed(1) + '%"></b>') + '</span>';
  }

  var est = { tipo: 'adm', adm: null, doc: null, folio: null, listo: false };
  /* El documento se arma solo al presionar «Generar estado de cuenta»
     (pedido del autor, 10-10-2026); elegir otro lo vuelve a dejar en espera. */
  function pinta() {
    var doc = document.getElementById('exDoc');
    document.getElementById('exPdf').disabled = !est.listo;
    doc.classList.toggle('ex-doc-espera', !est.listo);
    if (!est.listo) {
      est.folio = null;
      doc.style.removeProperty('--c');
      doc.innerHTML = '<p class="ex-espera"><span aria-hidden="true">🧾</span>Elegiste el estado de cuenta de <b>' + esc(actual().corto) +
        '</b>.<br>Presiona «Generar estado de cuenta» para expedirlo.</p>';
      return;
    }
    if (est.tipo === 'adm') pintaAdm(); else pintaCargo(docDe(est.doc));
  }
  function genera() {
    est.listo = true;
    pinta();
    document.getElementById('exDoc').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function pintaAdm() {
    var a = adm(est.adm), m = modelo(a), N = new Notas(m.fuentes);
    var doc = document.getElementById('exDoc');
    var h = cabecera(a.col, 'Estado de cuenta de la administración', a.n,
      a.periodo + (a.ys ? ' · cifras de ' + a.ys[0] + (a.ys[1] !== a.ys[0] ? ' a ' + a.ys[1] : '') : ''), 'Datos con corte al', D.corte);
    if (a.aviso) h += '<p class="ex-aviso">⚠️ ' + esc(a.aviso) + (a.curso ? ' El semáforo es <b>preliminar</b>: se compara un año contra sexenios completos.' : '') + '</p>';

    /* El termostato */
    N.sec('El termostato: qué mide cada indicador y cómo se le pone color',
      'El termostato compara con reglas escritas; no es una calificación oficial ni un juicio sobre la persona, y no suma los colores en una nota global. ' +
      'Más ingreso o más inversión no son por sí solos mejores, ni menos deuda peor: dependen de cómo estaba la economía.');
    h += '<section class="ex-termo"><h4>🌡️ Termostato de la salud financiera' + (a.curso ? ' <em class="ex-prelim">preliminar</em>' : '') + '</h4><div class="ex-termo-in">' +
      rueda(m.sem.map(function (r) { return r.c; }), m.sem.map(function (r) { return r.s.ico; })) +
      '<div class="ex-meds"><p class="ex-meds-esc"><span>peor</span><span>mejor</span></p>' + m.sem.map(function (r) {
        var k = CORTES[r.s.id], pos = null;
        if (k && r.c && tieneV(r.x)) pos = (r.x.v - k.peor.x.v) / (k.mejor.x.v - k.peor.x.v);
        var c = r.c ? COLOR[r.c] : null;
        var ref = N.add('<b>' + esc(r.s.tit) + '.</b> ' + notaA(N, r.x, esc(r.s.que)) + (regla(r.s) ? ' <i>' + esc(regla(r.s)) + '</i>' : ''));
        return '<div class="ex-med-f"><span class="ex-med-t">' + r.s.ico + ' ' + esc(r.s.tit) + '</span>' + medidor(pos, r.c) +
          '<span class="ex-med-v">' + valor(r.x, r.s.u, ref) + ' <small>' + (c ? c[0] + ' ' + c[1] : '⚪ Sin color') + '</small></span></div>';
      }).join('') + '</div></div></section>';

    /* Las cuentas */
    N.sec('Lo que entró y lo que salió', 'El % del PIB compara el tamaño contra la economía de cada año. La suma en pesos de hoy ya no tiene inflación: cada año se lleva a pesos de ' +
      esc((P.ref && P.ref.mes) || 'hoy') + ' con el INPC.');
    var cuentas = caja('💵 Lo que entró y lo que salió', tabla(m.cuenta.map(function (r) {
      return '<tr><th scope="row">' + r.ico + ' ' + esc(r.tit) + '</th><td>' + valor(r.pib, 'pib', N.add('<b>' + esc(r.tit) + ', promedio al año.</b> ' + notaA(N, r.pib))) +
        '</td><td>' + valor(r.hoy, 'hoy', N.add('<b>' + esc(r.tit) + ', suma del periodo.</b> ' + notaA(N, r.hoy))) + '</td></tr>';
    }).join(''), ['Concepto', 'Promedio al año', 'Suma del periodo, en pesos de ' + esc((P.ref && P.ref.mes) || 'hoy')]), true);
    function simple(ico, tit, filas, nota) {
      N.sec(tit, nota ? esc(nota) : '');
      return { n: filas.length, h: caja(ico + ' ' + esc(tit), tabla(filas.map(function (r) {
        return '<tr><th scope="row">' + esc(r.tit) + '</th><td>' + valor(r.x, r.u, N.add('<b>' + esc(r.tit) + '.</b> ' + notaA(N, r.x))) + '</td></tr>';
      }).join(''), ['Concepto', 'Cifra'])) };
    }
    h += columnas(cuentas, [simple('🏦', 'La deuda pública', m.deuda)].concat(
      m.peso.length ? [simple('💱', 'El peso durante su gobierno', m.peso, 'Dólar y euro: pesos por cada uno. Un porcentaje positivo es que el peso se depreció; negativo, que se apreció.')] : [],
      [simple('🔎', 'Ante la Auditoría Superior de la Federación', m.asf,
        'Sin color en el termostato: la ASF mide el monto por aclarar con esta definición solo desde la Cuenta Pública 2019, y las cuentas viejas llevan más años de solventación. No es daño comprobado.')]));

    var rev = '<div class="ex-rev-cols">' + N.html(1) +
      '<section class="ex-rsec"><h4><span>' + (N.secs.length + 1) + '</span> Fundamento legal</h4><p class="ex-nota">' + esc(D.ley17.txt) +
      ' <a href="' + esc(D.ley17.url) + '" target="_blank" rel="noopener noreferrer">' + esc(D.ley17.corto) + ' ↗</a></p></section>' +
      listaFuentes(m.fuentes, D.fuentes, N.secs.length + 2) + '</div>';
    doc.innerHTML = hoja(h, 'Estado de cuenta de ' + a.n, rev);
    doc.style.setProperty('--c', a.col);
    firma(doc, cifras(m), a.ini);
  }

  /* ================= Diputaciones y Suprema Corte ================= */
  function docDe(id) { if (!C) return null; for (var i = 0; i < C.docs.length; i++) if (C.docs[i].id === id) return C.docs[i]; return null; }
  function pesos(v) { return (v < 0 ? '−' : '') + '$' + num(Math.abs(v), v % 1 ? 2 : 0); }
  function cifraC(r) {
    if (r.u === 'txt') return esc(r.txt);
    var f = r.u === '$g' ? function (v) { return (v < 0 ? '−' : '') + '$' + num(Math.abs(v) / 1e6, 1) + ' millones'; } :
      r.u === 'ent' ? function (v) { return num(v, 0); } :
      r.u === 'pct100' ? function (v) { return num(v, 1) + '%'; } :
      r.u === 'pct' ? function (v) { return signo(v, 1) + '%'; } : pesos;
    return typeof r.v2 === 'number' ? 'de ' + f(r.v) + ' a ' + f(r.v2) : f(r.v);
  }
  function valorC(r, ref) {
    var tiene = typeof r.v === 'number' || r.u === 'txt' && r.txt;
    if (!tiene) return chip(r.est, r.pid) + (ref || '');
    return '<b class="ex-v' + (r.u === 'txt' ? ' ex-v-tx' : '') + (neg(r.v) || neg(r.v2) ? ' ex-neg' : '') + '">' + cifraC(r) + '</b>' + chip(r.est, r.pid) + (ref || '');
  }
  function notaC(N, r, extra) {
    var p = extra ? [extra] : [], x = r.f && C.fuentes[r.f];
    if (r.op) p.push(esc(r.op));
    if (r.nota) p.push(esc(r.nota));
    if (x) p.push(N.f(r.f).replace('</span>', (r.pag ? ', ' + esc(r.pag) : '') + '.</span>'));
    return p.join(' ');
  }
  function fuentesDe(d) {
    var ks = [];
    function f(r) { if (r.f && ks.indexOf(r.f) < 0) ks.push(r.f); }
    d.senales.forEach(function (s) { f(s.x); s.extra.forEach(f); f({ f: C.senales[s.id].ley }); });
    d.secciones.forEach(function (s) { s.filas.forEach(f); });
    return ks;
  }
  /* Las cifras que firma el sello, en un orden fijo. */
  function cifrasC(d) {
    function v(r) { return typeof r.v === 'number' ? (typeof r.v2 === 'number' ? [r.v, r.v2] : r.v) : r.u === 'txt' ? r.txt || 'sin dato' : 'sin dato'; }
    return {
      doc: 'Auditavisión · ' + d.tipoTx, id: d.id, corte: d.corte,
      senales: d.senales.map(function (s) { return [s.id, v(s.x), s.c || 'sin color']; }),
      secciones: d.secciones.map(function (s) { return [s.tit, s.filas.map(function (r) { return [r.t, v(r), r.est]; })]; })
    };
  }
  function pintaCargo(d) {
    var doc = document.getElementById('exDoc'), ks = fuentesDe(d), N = new Notas(ks);
    var h = cabecera(d.col, d.tipoTx, d.n, d.sub, 'Fuentes consultadas en', d.corte);
    if (d.aviso) h += '<p class="ex-aviso">ℹ️ ' + esc(d.aviso) + '</p>';
    N.sec('Las dos señales con regla de ley', 'Las señales comparan con reglas escritas en la ley; no son una calificación oficial ni un juicio sobre ninguna persona. ' +
      'Donde la cifra es parcial o falta, la señal se queda sin color en lugar de suponer.');
    h += '<section class="ex-termo"><h4>🌡️ Termostato: dos señales con regla de ley</h4><div class="ex-termo-in">' +
      rueda(d.senales.map(function (s) { return s.c; }), d.senales.map(function (s) { return C.senales[s.id].ico; })) +
      '<div class="ex-meds ex-meds-c">' + d.senales.map(function (s) {
        var def = C.senales[s.id], ley = C.fuentes[def.ley];
        var et = { verde: '🟢 Verde', ambar: '🟡 Ámbar', rojo: '🔴 Rojo' }[s.c] || '⚪ Sin color';
        var ref = N.add('<b>' + esc(def.tit) + '.</b> ' + esc(def.que) + ' <i>' + esc(def.reglas[s.r]) + '</i>' +
          (ley ? ' <span class="ex-nf">Fundamento: ' + esc(ley.corto) + '.</span>' : '') + ' ' + notaC(N, s.x));
        var graf = '';
        if (s.id === 'tope') {
          var pr = s.extra.filter(function (r) { return r.u === 'pct100' && typeof r.v === 'number'; })[0];
          /* Escala de 0 a 120% del tope: verde hasta el 100%, rojo después. */
          if (pr) graf = medidor(pr.v / 120, s.c, [['verde', 83.33], ['rojo', 16.67]]) + '<p class="ex-meds-esc"><span>0</span><span>tope (100%)</span><span>120%</span></p>';
        } else if (s.id === 'transparencia') {
          var t = { verde: ['✓', '✓'], ambar: ['✓', '✗'] }[s.c];
          graf = '<p class="ex-checks">' + (t ? '<span class="ex-ck-' + (t[0] === '✓' ? 'si' : 'no') + '">' + t[0] + ' Bruta</span><span class="ex-ck-' + (t[1] === '✓' ? 'si' : 'no') + '">' + t[1] + ' Neta</span>'
            : '<span class="ex-ck-na">Sin documento de 2026 localizado</span>') + '</p>';
        }
        return '<div class="ex-med-f ex-med-c"><span class="ex-med-t">' + def.ico + ' ' + esc(def.tit) + ' <small>' + et + '</small></span>' + graf +
          '<span class="ex-med-v">' + valorC(s.x, ref) + '</span>' +
          s.extra.map(function (r) { return '<span class="ex-med-x">' + esc(r.t) + ': ' + valorC(r, N.add('<b>' + esc(r.t) + '.</b> ' + notaC(N, r))) + '</span>'; }).join('') + '</div>';
      }).join('') + '</div></div></section>';
    h += columnas('', d.secciones.map(function (s) {
      N.sec(s.tit, esc(s.nota === '@local' ? C.notaLocal : s.nota || ''));
      var filas = s.filas.map(function (r) {
        return '<tr><th scope="row">' + esc(r.t) + '</th><td>' + valorC(r, N.add('<b>' + esc(r.t) + '.</b> ' + notaC(N, r))) + '</td></tr>';
      });
      if (filas.length <= 8) return { n: filas.length, h: caja(esc(s.tit), tabla(filas.join(''), ['Concepto', 'Cifra'])) };
      /* Una tabla larga va a lo ancho de la hoja, partida en dos. */
      var mitad = Math.ceil(filas.length / 2);
      return { larga: true, h: caja(esc(s.tit), '<div class="ex-t2">' + tabla(filas.slice(0, mitad).join(''), ['Concepto', 'Cifra']) +
        tabla(filas.slice(mitad).join(''), ['Concepto', 'Cifra']) + '</div>', true) };
    }));
    var leyes = [];
    d.senales.forEach(function (s) { var l = C.fuentes[C.senales[s.id].ley]; if (l && leyes.indexOf(l) < 0) leyes.push(l); });
    var rev = '<div class="ex-rev-cols">' + N.html(1) +
      '<section class="ex-rsec"><h4><span>' + (N.secs.length + 1) + '</span> Fundamento legal</h4><ul class="ex-leyes">' + leyes.map(function (l) {
        return '<li><a href="' + esc(l.url) + '" target="_blank" rel="noopener noreferrer">' + esc(l.corto) + ' ↗</a></li>';
      }).join('') + '</ul></section>' +
      listaFuentes(ks, C.fuentes, N.secs.length + 2) + '</div>';
    doc.innerHTML = hoja(h, d.tipoTx + ': ' + d.n, rev);
    doc.style.setProperty('--c', d.col);
    firma(doc, cifrasC(d), d.ini);
  }

  /* ================= El selector: de quién ================= */
  function actual() {
    if (est.tipo === 'adm') { var a = adm(est.adm); return { col: a.col, corto: a.c, q: 'adm=' + a.id }; }
    var d = docDe(est.doc); return { col: d.col, corto: d.n, q: 'doc=' + d.id };
  }
  function pintaTipos() {
    var cont = document.getElementById('exTipos');
    if (!C) { cont.hidden = true; document.getElementById('exPaso2').querySelector('b').textContent = '1.'; document.getElementById('exPaso3').textContent = '2.'; return; }
    cont.innerHTML = C.tipos.map(function (t) {
      var on = t.id === est.tipo;
      return '<button type="button" class="ex-tipo" role="radio" aria-checked="' + on + '" data-tipo="' + t.id + '">' +
        '<span class="ex-tipo-ico" aria-hidden="true">' + t.ico + '</span><span><b>' + esc(t.n) + '</b><small>' + esc(t.sub) + '</small></span></button>';
    }).join('');
    var dos = est.tipo === 'adm' || est.tipo === 'dip-loc';
    document.getElementById('exPaso2').hidden = !dos;
    document.getElementById('exPaso2Tx').textContent = est.tipo === 'dip-loc' ? 'Elige el estado' : 'Elige la administración';
    document.getElementById('exAdmins').hidden = est.tipo !== 'adm';
    document.getElementById('exEnts').hidden = est.tipo !== 'dip-loc';
    document.getElementById('exPaso3').textContent = dos ? '3.' : '2.';
  }
  function pintaAdmins() {
    document.getElementById('exAdmins').innerHTML = D.admins.map(function (a) {
      return '<button type="button" class="rd-admin" role="radio" aria-checked="' + (a.id === est.adm) + '" aria-selected="' + (a.id === est.adm) + '" data-adm="' + a.id + '" style="--c:' + a.col + '">' +
        '<span class="rd-admin-ini" aria-hidden="true">' + esc(a.ini) + '</span>' +
        '<span class="rd-admin-tx"><b>' + esc(a.c) + '</b><small>' + a.a[0] + '–' + a.a[1] + (a.curso ? ' · en curso' : '') + '</small></span></button>';
    }).join('');
  }
  function pintaEnts() {
    if (!C) return;
    var locs = C.docs.filter(function (d) { return d.tipo === 'dip-loc'; });
    function ops(con) {
      return locs.filter(function (d) { return d.conDoc === con; }).map(function (d) {
        return '<option value="' + d.id + '"' + (d.id === est.doc ? ' selected' : '') + '>' + esc(d.ent) + '</option>';
      }).join('');
    }
    var n = locs.filter(function (d) { return d.conDoc; }).length;
    document.getElementById('exEnts').innerHTML = '<label class="ex-ents-l" for="exEnt">Congreso del estado</label>' +
      '<select id="exEnt"><optgroup label="Con lo que pagan en 2026 documentado (' + n + ')">' + ops(true) + '</optgroup>' +
      '<optgroup label="Aún sin ese documento (' + (locs.length - n) + ')">' + ops(false) + '</optgroup></select>' +
      '<p class="ex-pista">De ' + (locs.length - n) + ' congresos aún no localizamos el documento oficial de 2026 con lo que pagan: su estado de cuenta muestra lo que sí está documentado y dice qué falta.</p>';
  }
  function elige(id, empujar) {
    if (!adm(id)) return;
    est.tipo = 'adm';
    est.adm = id;
    est.listo = false;
    pintaTipos();
    pintaAdmins();
    pinta();
    if (empujar) history.replaceState(null, '', location.pathname + '?adm=' + id);
  }
  function eligeDoc(id, empujar) {
    var d = docDe(id);
    if (!d) return;
    est.tipo = d.tipo;
    est.doc = id;
    est.listo = false;
    pintaTipos();
    if (d.tipo === 'dip-loc') pintaEnts();
    pinta();
    if (empujar) history.replaceState(null, '', location.pathname + '?doc=' + id);
  }
  function eligeTipo(t) {
    if (t === 'adm') return elige(est.adm || ultimo, true);
    if (t === 'dip-loc') {
      var d = docDe(est.doc);
      return eligeDoc(d && d.tipo === 'dip-loc' ? d.id : C.docs.filter(function (x) { return x.tipo === 'dip-loc' && x.conDoc; })[0].id, true);
    }
    eligeDoc(t, true);
  }
  if (SOLO) { arrancaVerifica(); return; }
  document.getElementById('exTipos').addEventListener('click', function (e) {
    var b = e.target.closest('[data-tipo]');
    if (b) eligeTipo(b.getAttribute('data-tipo'));
  });
  document.getElementById('exAdmins').addEventListener('click', function (e) {
    var b = e.target.closest('[data-adm]');
    if (b) elige(b.getAttribute('data-adm'), true);
  });
  document.getElementById('exEnts').addEventListener('change', function (e) {
    if (e.target.id === 'exEnt') eligeDoc(e.target.value, true);
  });

  /* Con el ancho de la hoja ya puesto, reparte las cajas del anverso por su
     altura real, en orden de lectura (columna por columna): de todos los
     cortes posibles, el que deja la columna más alta lo más baja posible. */
  function emparejar(c) {
    var cols = c.querySelectorAll('.ex-anverso .ex-col');
    if (cols.length < 2) return;
    var cajas = [];
    Array.prototype.forEach.call(cols, function (col) { Array.prototype.forEach.call(col.children, function (x) { cajas.push(x); }); });
    cajas.sort(function (p, q) { return p.getAttribute('data-i') - q.getAttribute('data-i'); });
    var hs = cajas.map(function (x) { return x.getBoundingClientRect().height; });
    function suma(i, j) { var t = 0; for (var k = i; k < j; k++) t += hs[k] + 7; return t; }
    var n = cajas.length, mejor = null;
    for (var i = 0; i <= n; i++) {
      var m = Math.max(suma(0, i), suma(i, n));
      if (!mejor || m < mejor[0]) mejor = [m, i];
    }
    cajas.forEach(function (x, k) { cols[k < mejor[1] ? 0 : 1].appendChild(x); });
  }
  document.getElementById('exGenera').addEventListener('click', genera);

  /* ================= Descargar en PDF ================= */
  document.getElementById('exPdf').addEventListener('click', function () {
    if (!est.listo) return;
    var viejo = document.getElementById('exPrint');
    if (viejo) viejo.remove();
    var c = document.createElement('div'), x = actual();
    c.id = 'exPrint';
    c.className = 'ex-print ex-medir';
    c.innerHTML = '<article class="ex-doc">' + document.getElementById('exDoc').innerHTML + '</article>';
    c.firstChild.style.setProperty('--c', x.col);
    document.body.appendChild(c);
    emparejar(c);
    c.classList.remove('ex-medir');
    var t = document.title;
    document.title = 'Estado de cuenta ' + x.corto + (est.folio ? ' ' + est.folio : '') + ' · Auditavisión';
    window.print();
    setTimeout(function () { document.title = t; }, 500);
  });
  window.addEventListener('afterprint', function () { var c = document.getElementById('exPrint'); if (c) c.remove(); });
  document.getElementById('exLiga').addEventListener('click', function () {
    var url = location.origin + location.pathname + '?' + actual().q, b = this;
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
    var todos = D.admins.map(function (a) { return { ini: a.ini, n: a.n, q: 'adm', id: a.id, obj: cifras(modelo(a)) }; });
    if (C) C.docs.forEach(function (d) { todos.push({ ini: d.ini, n: d.n, q: 'doc', id: d.id, obj: cifrasC(d) }); });
    Promise.all(todos.map(function (t) { return huellaDe(t.obj).then(function (h) { t.h = h; return t; }); })).then(function (rs) {
      if (!rs[0].h) { out.innerHTML = '<p class="ex-ver ex-ver-no">Este navegador no puede calcular huellas SHA-256. Ábrelo en uno actualizado.</p>'; return; }
      var Q = q.toUpperCase(), hit = null;
      rs.forEach(function (r) { if (folio(r.ini, r.h) === Q || r.h.toUpperCase() === Q) hit = r; });
      if (hit) {
        out.innerHTML = '<div class="ex-ver ex-ver-si"><b>✅ Auténtico.</b> Corresponde al estado de cuenta de <b>' + esc(hit.n) + '</b>, y sus cifras coinciden con los datos vigentes.' +
          '<br><small>Huella: <code>' + hit.h + '</code></small> <a class="sz-btn" href="radar-estado-de-cuenta.html?' + hit.q + '=' + hit.id + '">Ver el documento</a></div>';
      } else {
        out.innerHTML = '<div class="ex-ver ex-ver-no"><b>❌ No coincide</b> con ningún estado de cuenta de los datos vigentes. ' +
          'O el documento se alteró, o se expidió con datos anteriores: en ese caso, expídelo de nuevo y compara las cifras.</div>';
      }
    });
  }
  function arrancaVerifica() {
    document.getElementById('exVerForm').addEventListener('submit', function (e) {
      e.preventDefault();
      var v = document.getElementById('exVerIn').value.trim();
      history.replaceState(null, '', location.pathname + (v ? '?verifica=' + encodeURIComponent(v) : ''));
      verifica(v);
    });
    var v = new URLSearchParams(location.search).get('verifica');
    if (v) { document.getElementById('exVerIn').value = v; verifica(v); }
  }

  /* ================= Arranque ================= */
  /* El «Hoy» vivió en esta página hasta el 10-10-2026: su ancla lleva a la suya. */
  if (location.hash === '#hoy') { location.replace('radar-presupuesto-en-curso.html'); return; }
  var q = new URLSearchParams(location.search);
  /* Los PDF impresos antes de la mudanza llevan esta dirección con ?verifica=. */
  if (q.get('verifica')) { location.replace(new URL(VERIFICA + location.search, location.href).href); return; }
  var ultimo = D.admins[D.admins.length - 1].id;
  /* Un enlace compartido (?doc= o ?adm=) es un documento ya expedido: se genera al abrirlo. */
  if (docDe(q.get('doc'))) { eligeDoc(q.get('doc'), false); est.listo = true; pinta(); }
  else if (adm(q.get('adm'))) { elige(q.get('adm'), false); est.listo = true; pinta(); }
  else elige(ultimo, false);
})();
