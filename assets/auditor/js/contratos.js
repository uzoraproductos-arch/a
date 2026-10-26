/* Contratos públicos (contratos-publicos.html, 26-10-2026).
   Buscador de los contratos de ComprasMX por empresa, RFC o institución, y
   el cruce de sus proveedores con la lista 69-B del SAT. Los catálogos los
   escribe herramientas/actualizar_comprasmx.py y se cargan aquí bajo demanda.
   Cada importe es «oficial» (lo reportó la institución, antes de impuestos);
   las sumas y porcentajes, «derivado». Las personas físicas no se publican. */
(function () {
  'use strict';
  var raiz = document.getElementById('cmxApp');
  if (!raiz) return;
  var DIR = 'assets/auditor/data/comprasmx/';
  var yo = document.querySelector('script[src*="contratos.js"]');
  var V = (yo && /\?v=[\w.-]+/.exec(yo.getAttribute('src')) || [''])[0];
  var cargas = {};
  var TIPO = { AD: 'adjudicación directa', LP: 'licitación pública', I3: 'invitación a cuando menos tres', OT: 'otro procedimiento' };
  var SIT = { P: ['⚠️', 'Presunto', 'El SAT presume que facturó operaciones inexistentes; el proceso sigue abierto.'],
              F: ['⛔', 'Definitivo', 'El SAT determinó en definitiva que facturó operaciones inexistentes.'],
              D: ['ℹ️', 'Desvirtuado', 'Desvirtuó la presunción ante el SAT.'],
              S: ['ℹ️', 'Sentencia favorable', 'Un tribunal le dio la razón frente al SAT.'] };

  function carga(ruta, listo) {
    var ya = listo();
    if (ya) return Promise.resolve(ya);
    if (cargas[ruta]) return cargas[ruta];
    cargas[ruta] = new Promise(function (ok, mal) {
      var s = document.createElement('script');
      s.src = DIR + ruta + V;
      s.onload = function () { var d = listo(); if (d) ok(d); else mal(); };
      s.onerror = function () { cargas[ruta] = null; mal(); };
      document.head.appendChild(s);
    });
    return cargas[ruta];
  }
  function idx() { return carga('indice.js', function () { return window.CMX_IDX; }); }
  function inst() { return carga('inst.js', function () { return window.CMX_INST; }); }
  function prov(rfc) {
    var pre = rfc.slice(0, 2);
    return carga('p-' + pre.replace(/[^A-Z0-9]/g, '_') + '.js', function () { return window.CMX_P && window.CMX_P[pre]; })
      .then(function (L) { return L[rfc] || null; });
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function norm(s) { return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toUpperCase().replace(/[^A-Z0-9& ]/g, ' ').replace(/\s+/g, ' ').trim(); }
  function pesos(v) {
    if (Math.abs(v) >= 1e6) return '$' + (v / 1e6).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp';
    return '$' + Math.round(v).toLocaleString('es-MX');
  }
  function chip(e) { return '<span class="est-chip est-' + e + '">' + e + '</span>'; }
  function n(v) { return Number(v).toLocaleString('es-MX'); }
  function pct(a, b) { return b ? (Math.round(a / b * 1000) / 10).toLocaleString('es-MX') : '0'; }
  var RFC = /^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$/;

  var caja = raiz.querySelector('#cmxQ'), sal = raiz.querySelector('#cmxSal');
  function pinta(h) { sal.innerHTML = h; }
  function aviso() {
    return '<p class="cmx-nota">⚖️ Tener contratos con el gobierno no es una irregularidad. El importe es el que reportó cada institución, antes de impuestos; en un contrato abierto suele ser el máximo, no lo pagado.</p>';
  }

  function fichaProv(rfc, d, M) {
    if (!d) return '<p>◻️ El RFC <code>' + esc(rfc) + '</code> no tiene contratos en los expedientes de 2025 y 2026 de ComprasMX. Eso no certifica nada: puede tenerlos en otros años o con gobiernos que no usan ComprasMX.</p>';
    var tp = d.tp || {}, mtp = d.mtp || {};
    var h = '<article class="cmx-ficha"><h3>🏢 ' + esc(d.n) + ' <small><code>' + esc(rfc) + '</code></small></h3>' +
      '<div class="cmx-cifras">' +
        '<div><b>' + n(d.c) + '</b><span>contratos</span>' + chip('oficial') + '</div>' +
        '<div><b>' + pesos(d.m) + '</b><span>importe en pesos, antes de impuestos (suma)</span>' + chip('derivado') + '</div>' +
        '<div><b>' + pct(mtp.AD || 0, d.m) + ' %</b><span>del importe, por adjudicación directa</span>' + chip('derivado') + '</div>' +
        '<div><b>' + n(d.ni) + '</b><span>instituciones le compran</span>' + chip('derivado') + '</div>' +
      '</div>' +
      '<p>Por procedimiento: ' + ['AD', 'LP', 'I3', 'OT'].filter(function (k) { return tp[k]; }).map(function (k) { return '<b>' + n(tp[k]) + '</b> por ' + TIPO[k] + (mtp[k] ? ' (' + pesos(mtp[k]) + ')' : ''); }).join('; ') + '.</p>' +
      (d.o ? '<p class="cmx-nota">En otras monedas, sin convertir: ' + Object.keys(d.o).map(function (k) { return n(Math.round(d.o[k])) + ' ' + esc(k); }).join(', ') + '.</p>' : '') +
      (d.sat ? '<p class="cmx-sat">' + (SIT[d.sat[0]] || ['', d.sat[0], ''])[0] + ' <b>En la lista 69-B del SAT: ' + esc((SIT[d.sat[0]] || ['', d.sat[0]])[1]) + '</b> (oficio ' + esc(d.sat[1]) + ', ' + esc(d.sat[2]) + '). ' + esc((SIT[d.sat[0]] || ['', '', ''])[2]) + '</p>' : '') +
      '<h4>A quién le vende</h4><ul class="cmx-lista">' + d.i.map(function (x) {
        return '<li><button type="button" class="cmx-ir" data-i="' + esc(x[0]) + '">' + esc(x[1]) + '</button> ' + n(x[3]) + ' contrato' + (x[3] === 1 ? '' : 's') + ', ' + pesos(x[4]) + '</li>';
      }).join('') + '</ul>' +
      '<h4>Sus contratos mayores ' + chip('oficial') + '</h4><ul class="cmx-lista cmx-contratos">' + d.k.map(function (k) {
        return '<li><b>' + pesos(k[3]) + (k[4] !== 'MXN' ? ' ' + esc(k[4]) : '') + '</b> · ' + esc(k[1]) + ' · ' + esc(TIPO[k[5]] || '') + (k[6] ? ' · ' + esc(k[6]) : '') +
          '<br><span>' + esc(k[2]) + '</span>' + (k[7] ? ' <a href="' + esc(M.detalle.replace('%s', k[7])) + '" target="_blank" rel="noopener">Ver en ComprasMX ↗</a>' : '') + ' <small>' + esc(k[0]) + '</small></li>';
      }).join('') + '</ul>' + aviso() + '</article>';
    return h;
  }
  function fichaInst(k, d) {
    return '<article class="cmx-ficha"><h3>🏛️ ' + esc(d.n) + (d.s && d.s !== d.n ? ' <small>' + esc(d.s) + '</small>' : '') + '</h3>' +
      '<div class="cmx-cifras">' +
        '<div><b>' + n(d.c) + '</b><span>contratos</span>' + chip('oficial') + '</div>' +
        '<div><b>' + pesos(d.m) + '</b><span>importe en pesos, antes de impuestos (suma)</span>' + chip('derivado') + '</div>' +
        '<div><b>' + pct(d.ad, d.c) + ' %</b><span>de los contratos, por adjudicación directa</span>' + chip('derivado') + '</div>' +
        '<div><b>' + pct(d.mad, d.m) + ' %</b><span>del importe, por adjudicación directa</span>' + chip('derivado') + '</div>' +
      '</div>' +
      '<p>Le compró a <b>' + n(d.np) + '</b> empresas' + (d.pf ? ' y a personas físicas (' + n(d.pf) + ' contratos, ' + pesos(d.mpf) + '; no se publican sus nombres)' : '') + '.</p>' +
      (d.ot ? '<p class="cmx-nota">En otras monedas, sin convertir: ' + Object.keys(d.ot).map(function (x) { return n(Math.round(d.ot[x])) + ' ' + esc(x); }).join(', ') + '.</p>' : '') +
      '<h4>Sus 10 proveedores mayores</h4><ol class="cmx-lista">' + d.p.map(function (x) {
        return '<li><button type="button" class="cmx-ir" data-r="' + esc(x[0]) + '">' + esc(x[1]) + '</button> ' + pesos(x[3]) + ' · ' + n(x[2]) + ' contrato' + (x[2] === 1 ? '' : 's') + '</li>';
      }).join('') + '</ol>' + aviso() + '</article>';
  }

  function verRfc(rfc) {
    pinta('<p class="cmx-cargando">Buscando…</p>');
    if (rfc.length === 13) { pinta('<p>🔒 Es el RFC de una <b>persona física</b>. La plataforma no publica a las personas físicas que le venden al gobierno: su RFC es un dato personal.</p>'); return; }
    Promise.all([prov(rfc), idx()]).then(function (D) { pinta(fichaProv(rfc, D[0], D[1].meta)); }, falla);
  }
  function verInst(k) {
    pinta('<p class="cmx-cargando">Buscando…</p>');
    inst().then(function (T) { pinta(T.i[k] ? fichaInst(k, T.i[k]) : '<p>No encontré esa institución.</p>'); }, falla);
  }
  function falla() { pinta('<p>No pude descargar el catálogo. Revisa tu conexión y vuelve a intentarlo.</p>'); }

  function buscar(q) {
    q = String(q || '').trim();
    if (!q) return;
    var up = q.toUpperCase().replace(/\s+/g, '');
    if (RFC.test(up)) { verRfc(up); return; }
    pinta('<p class="cmx-cargando">Buscando…</p>');
    Promise.all([idx(), inst()]).then(function (D) {
      var ws = norm(q).split(' '), I = D[0], T = D[1];
      var ins = Object.keys(T.i).filter(function (k) {
        var s = norm(T.i[k].s).replace(/ /g, ''), nn = ' ' + norm(T.i[k].n) + ' ';
        return s === ws.join('') || ws.every(function (w) { return nn.indexOf(' ' + w + ' ') >= 0; });
      }).sort(function (a, b) { return T.i[b].m - T.i[a].m; });
      var ps = I.r.filter(function (r) { var nn = ' ' + norm(r[1]) + ' '; return ws.every(function (w) { return nn.indexOf(' ' + w + ' ') >= 0; }); });
      var exacta = ins.filter(function (k) { return norm(T.i[k].s).replace(/ /g, '') === ws.join(''); });
      if (exacta.length === 1) { verInst(exacta[0]); return; }
      if (ps.length === 1 && !ins.length) { verRfc(ps[0][0]); return; }
      if (ins.length === 1 && !ps.length) { verInst(ins[0]); return; }
      if (!ps.length && !ins.length) {
        pinta('<p>◻️ No encontré «' + esc(q) + '» entre los ' + n(I.meta.proveedores) + ' proveedores ni las ' + n(I.meta.instituciones) + ' instituciones. El nombre puede estar escrito distinto; con el RFC la búsqueda es exacta.</p>');
        return;
      }
      pinta((ins.length ? '<h4>Instituciones (' + n(ins.length) + ')</h4><ul class="cmx-lista">' + ins.slice(0, 10).map(function (k) {
        return '<li><button type="button" class="cmx-ir" data-i="' + esc(k) + '">' + esc(T.i[k].n) + '</button> ' + esc(T.i[k].s) + ' · ' + n(T.i[k].c) + ' contratos</li>';
      }).join('') + '</ul>' : '') +
        (ps.length ? '<h4>Empresas (' + n(ps.length) + ')</h4><ul class="cmx-lista">' + ps.slice(0, 20).map(function (r) {
          return '<li><button type="button" class="cmx-ir" data-r="' + esc(r[0]) + '">' + esc(r[1]) + '</button> <code>' + esc(r[0]) + '</code></li>';
        }).join('') + '</ul>' + (ps.length > 20 ? '<p class="cmx-nota">Te muestro 20; escribe más del nombre o el RFC.</p>' : '') : ''));
    }, falla);
  }

  raiz.querySelector('#cmxForma').addEventListener('submit', function (e) { e.preventDefault(); buscar(caja.value); });
  raiz.addEventListener('click', function (e) {
    var b = e.target.closest('.cmx-ir');
    if (!b) return;
    if (b.getAttribute('data-r')) verRfc(b.getAttribute('data-r'));
    else verInst(b.getAttribute('data-i'));
    raiz.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  /* El cruce con la lista 69-B. */
  var cruce = document.getElementById('cmxCruce');
  if (cruce) inst().then(function (T) {
    cruce.innerHTML = '<p>De los ' + n(T.meta.proveedores) + ' proveedores (personas morales) con contratos, <b>' + T.sat.length + '</b> aparecen en la lista 69-B del SAT, por RFC ' + chip('derivado') + '.</p>' +
      '<ul class="cmx-lista">' + T.sat.map(function (r) {
        var s = SIT[r[2]] || ['', r[2], ''];
        return '<li>' + s[0] + ' <button type="button" class="cmx-ir" data-r="' + esc(r[0]) + '">' + esc(r[1]) + '</button> <b>' + esc(s[1]) + '</b> · ' + n(r[3]) + ' contrato' + (r[3] === 1 ? '' : 's') + ', ' + pesos(r[4]) + '</li>';
      }).join('') + '</ul>' +
      '<p class="cmx-nota">«Desvirtuado» y «sentencia favorable» quieren decir que salió de la presunción; «presunto» es un proceso abierto y solo «definitivo» es una determinación firme del SAT.</p>';
    cruce.addEventListener('click', function (e) { var b = e.target.closest('.cmx-ir'); if (b) { verRfc(b.getAttribute('data-r')); raiz.scrollIntoView({ behavior: 'smooth' }); } });
  }, function () { cruce.innerHTML = '<p>No pude descargar el cruce.</p>'; });

  var pr = new URLSearchParams(location.search);
  if (pr.get('i')) verInst(pr.get('i'));
  else if (pr.get('q')) { caja.value = pr.get('q'); buscar(pr.get('q')); }
})();
