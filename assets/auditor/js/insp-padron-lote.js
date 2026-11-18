/* «Revisa a tu contraparte»: el lote, la cadena de terceros y la matriz
   (18-11-2026; entregas 3, 4 y 5 del plan del padrón, pedido del autor:
   «verificar a los clientes de nuestros clientes»).

   - Lote: un CSV, un TXT o lo pegado de Excel con hasta 2,000 RFC.
   - Cadena de terceros: los CFDI en XML; de cada uno se toman el emisor, el
     receptor y los RFC «a cuenta de terceros» de sus conceptos (CFDI 4.0,
     nodo ACuentaTerceros). Se dice quién te factura, a quién le facturas y por
     cuenta de quién.
   - Matriz: una fila por RFC y una columna por lista, con el orden en que
     conviene revisarlos. Se descarga en CSV.

   Todo se lee y se cruza en el navegador, con padron.js: ningún archivo sale
   de tu computadora. Las personas físicas no se nombran (solo se dice si su
   RFC coincide), y ninguna señal se suma en una calificación: la columna
   «Revisar primero» ordena, no califica. */
(function () {
  'use strict';
  var arch = document.getElementById('pdArch'), pega = document.getElementById('pdPega'), btn = document.getElementById('pdLoteBtn'),
    out = document.getElementById('pdLote'), suelta = document.getElementById('pdSuelta');
  if (!arch || !out || !window.Padron) return;
  var RFC_G = /[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}/g, MAX = 2000, A_LA_VEZ = 12;
  var GENERICO = ['XAXX010101000', 'XEXX010101000'];

  /* Las columnas de la matriz: qué claves de señal de padron.js caen en cada una. */
  var COLS = [
    { id: 'art69', t: 'SAT, art. 69', k: ['nl', 'fi', 'ex', 'ca', 'se'] },
    { id: 'csd', t: 'Sellos sin efectos (17-H Bis)', k: ['csd'] },
    { id: 'b69', t: 'Lista 69-B', k: ['b69P', 'b69F', 'b69D', 'b69S'] },
    { id: 'bb', t: '69-B Bis', k: ['bbF', 'bbS'] },
    { id: 'san', t: 'Sancionados', k: ['san'] },
    { id: 'int', t: 'OFAC / ONU', k: ['ofac', 'onu'] }
  ];
  var CORTO = { nl: 'no localizado', fi: 'crédito firme', ex: 'crédito exigible', ca: 'crédito cancelado', se: 'sentencia por delito fiscal', csd: 'sello sin efectos',
    b69P: 'presunto', b69F: 'definitivo', b69D: 'desvirtuado', b69S: 'sentencia favorable', bbF: 'definitivo', bbS: 'sentencia favorable',
    san: 'sancionado', ofac: 'OFAC', onu: 'ONU' };
  var ORDEN = [['—', 'sin coincidencias'], ['ℹ️', 'antecedente'], ['⚠️', 'revisar'], ['⛔', 'revisar primero']];

  function esc(x) { return String(x == null ? '' : x).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function n(v) { return Number(v).toLocaleString('es-MX'); }
  function rfcDe(s) { return String(s || '').toUpperCase().replace(/\s+/g, ''); }
  function valido(r) { return /^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$/.test(r) && GENERICO.indexOf(r) < 0; }

  /* ── Lectura ─────────────────────────────────────────────────────────── */
  function leeTexto(t, R) {
    (String(t).toUpperCase().match(RFC_G) || []).forEach(function (r) { if (valido(r)) papel(R, r, 'lista'); });
  }
  function papel(R, r, p, n1) {
    var x = R.rfc[r] || (R.rfc[r] = { rfc: r, papeles: {}, cfdi: 0 });
    x.papeles[p] = (x.papeles[p] || 0) + 1;
    if (n1) x.cfdi++;
  }
  function attr(el, a) { return el ? (el.getAttribute(a) || el.getAttribute(a.toLowerCase()) || '') : ''; }
  function uno(doc, tag) { var l = doc.getElementsByTagNameNS('*', tag); return l.length ? l[0] : null; }
  function leeXml(t, R) {
    var doc = new DOMParser().parseFromString(t, 'application/xml');
    var c = uno(doc, 'Comprobante');
    if (!c || doc.getElementsByTagName('parsererror').length) { R.malos++; return; }
    var e = rfcDe(attr(uno(doc, 'Emisor'), 'Rfc')), r = rfcDe(attr(uno(doc, 'Receptor'), 'Rfc'));
    var terceros = Array.prototype.map.call(doc.getElementsByTagNameNS('*', 'ACuentaTerceros'), function (x) { return rfcDe(attr(x, 'RfcACuentaTerceros')); })
      .filter(function (x, i, l) { return valido(x) && l.indexOf(x) === i; });
    R.cfdi.push({ e: e, r: r, t: terceros, tipo: attr(c, 'TipoDeComprobante') });
  }
  /* Con facturas, «tú» es el RFC que aparece en todas (como emisor o receptor). */
  function papeles(R) {
    if (!R.cfdi.length) return;
    var cuenta = {};
    R.cfdi.forEach(function (f) { [f.e, f.r].filter(function (x, i, l) { return x && l.indexOf(x) === i; }).forEach(function (x) { cuenta[x] = (cuenta[x] || 0) + 1; }); });
    var yo = Object.keys(cuenta).filter(function (x) { return cuenta[x] === R.cfdi.length; });
    R.yo = yo.length === 1 && R.cfdi.length > 1 ? yo[0] : '';
    R.cfdi.forEach(function (f) {
      if (valido(f.e) && f.e !== R.yo) papel(R, f.e, R.yo ? 'te factura' : 'emisor', true);
      if (valido(f.r) && f.r !== R.yo) papel(R, f.r, R.yo ? 'le facturas' : 'receptor', true);
      f.t.forEach(function (t) {
        if (t === R.yo) return;
        papel(R, t, 'a cuenta de terceros', true);
        R.cadena.push({ e: f.e, t: t });
      });
    });
  }

  /* ── Revisión ────────────────────────────────────────────────────────── */
  function revisa(lista, avance) {
    var res = new Array(lista.length), i = 0, hechos = 0;
    return new Promise(function (ok) {
      function sig() {
        if (i >= lista.length) { if (hechos === lista.length) ok(res); return; }
        var k = i++;
        Padron.rfc(lista[k]).then(function (f) { res[k] = f; }, function () { res[k] = { rfc: lista[k], error: true, senales: [] }; }).then(function () {
          hechos++; avance(hechos, lista.length);
          if (hechos === lista.length) ok(res); else sig();
        });
      }
      for (var j = 0; j < Math.min(A_LA_VEZ, lista.length); j++) sig();
      if (!lista.length) ok(res);
    });
  }
  function celda(f, col) {
    var s = (f.senales || []).filter(function (x) { return col.k.indexOf(x.k) >= 0; });
    return s.map(function (x) { return CORTO[x.k] || x.k; }).filter(function (x, i, l) { return l.indexOf(x) === i; }).join(', ');
  }
  function orden(f) {
    if (f.error) return ['?', 'no se pudo revisar'];
    if (!f.senales || !f.senales.length) return ORDEN[0];
    if (!f.nivel) return ['✅', 'salió de la lista'];
    return ORDEN[Math.min(3, f.nivel)];
  }
  function nombre(f) { return f.moral ? (f.nombre || '') : (f.rfc && f.rfc.length === 13 ? 'persona física (no se nombra)' : ''); }
  function papelTxt(x) { return Object.keys(x.papeles).filter(function (p) { return p !== 'lista'; }).join(', '); }

  /* ── Pintar ──────────────────────────────────────────────────────────── */
  function pinta(R, fs) {
    var filas = fs.map(function (f, i) { return { f: f, x: R.rfc[R.lista[i]] }; });
    filas.sort(function (a, b) { return (b.f.nivel || 0) - (a.f.nivel || 0) || ((b.f.senales || []).length - (a.f.senales || []).length) || (a.f.rfc < b.f.rfc ? -1 : 1); });
    var con = filas.filter(function (y) { return y.f.senales && y.f.senales.length; }).length;
    var hayPapel = R.cfdi.length > 0;
    var h = '<div class="pd-lote-res">' +
      '<p>Revisé <b>' + n(filas.length) + ' RFC</b>' + (R.cfdi.length ? ' de <b>' + n(R.cfdi.length) + ' facturas</b>' : '') + ': <b>' + n(con) + '</b> con alguna coincidencia y <b>' +
      n(filas.length - con) + '</b> sin coincidencias.' + (R.recorte ? ' Revisé solo los primeros ' + n(MAX) + '.' : '') + (R.malos ? ' ' + n(R.malos) + ' archivo(s) no eran un CFDI que pudiera leer.' : '') + '</p>' +
      (R.yo ? '<p class="pd-chico">Tomé como tuyo el RFC <code>' + esc(R.yo) + '</code>, que aparece en todas las facturas; no lo revisé.</p>' : '') +
      '<div class="pd-matriz-caja" tabindex="0" role="region" aria-label="Matriz de coincidencias"><table class="pd-matriz"><caption>Matriz de coincidencias, de lo que conviene revisar primero a lo que no tiene ninguna</caption><thead><tr>' +
      '<th scope="col">Revisar</th><th scope="col">RFC</th>' + (hayPapel ? '<th scope="col">Papel</th>' : '') +
      COLS.map(function (c) { return '<th scope="col">' + esc(c.t) + '</th>'; }).join('') + '<th scope="col">Contratos con el gobierno</th></tr></thead><tbody>' +
      filas.map(function (y) {
        var f = y.f, o = orden(f);
        return '<tr' + (f.nivel >= 3 ? ' class="pd-m-3"' : f.nivel === 2 ? ' class="pd-m-2"' : '') + '><td title="' + esc(o[1]) + '">' + o[0] + ' <span class="pd-m-o">' + esc(o[1]) + '</span></td>' +
          '<th scope="row"><a href="herramienta-inspector-padron.html?q=' + encodeURIComponent(f.rfc) + '"><code>' + esc(f.rfc) + '</code></a>' + (nombre(f) ? '<small>' + esc(nombre(f)) + '</small>' : '') + '</th>' +
          (hayPapel ? '<td>' + esc(papelTxt(y.x)) + (y.x.cfdi ? ' <small>(' + n(y.x.cfdi) + ')</small>' : '') + '</td>' : '') +
          COLS.map(function (c) { var v = celda(f, c); return '<td' + (v ? ' class="pd-m-si"' : '') + '>' + (v ? esc(v) : '—') + '</td>'; }).join('') +
          '<td>' + (f.cmx ? 'sí' : '—') + '</td></tr>';
      }).join('') + '</tbody></table></div>' +
      '<p><button type="button" class="ef-btn" id="pdCsv">⬇️ Descargar la matriz en CSV</button></p>';
    if (R.cadena.length) {
      var vistos = {};
      var cad = R.cadena.filter(function (c) { var k = c.e + '>' + c.t; if (vistos[k]) return false; vistos[k] = 1; return true; });
      var porRfc = {}; fs.forEach(function (f) { porRfc[f.rfc] = f; });
      h += '<h3>🔗 La cadena de terceros</h3><p>En estas facturas, el emisor cobró <b>a cuenta de un tercero</b> (CFDI 4.0, nodo «ACuentaTerceros»): el dinero es de otra persona o empresa, y conviene revisar a las dos.</p><ul class="pd-cadena">' +
        cad.map(function (c) {
          var ft = porRfc[c.t] || {}, fe = porRfc[c.e] || {};
          return '<li><code>' + esc(c.e) + '</code>' + (fe.senales && fe.senales.length ? ' ' + orden(fe)[0] : '') + ' factura a cuenta de <code>' + esc(c.t) + '</code>' +
            (ft.senales && ft.senales.length ? ' ' + orden(ft)[0] + ' <span class="pd-chico">' + esc(ft.senales.map(function (s) { return CORTO[s.k] || s.k; }).join(', ')) + '</span>' : '') + '</li>';
        }).join('') + '</ul>';
    }
    h += '<p class="pd-chico">Una coincidencia es una señal para revisar, nunca una acusación ni una calificación: la columna «Revisar» solo ordena la lista. No aparecer tampoco certifica a nadie. ' +
      'Toca un RFC para ver su ficha con cada documento. Todo se cruzó en tu navegador: tus archivos no salieron de tu computadora.</p></div>';
    out.innerHTML = h;
    document.getElementById('pdCsv').addEventListener('click', function () { csv(filas, hayPapel); });
  }
  function csv(filas, hayPapel) {
    var q = function (v) { v = String(v == null ? '' : v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
    var cab = ['revisar', 'rfc', 'nombre'].concat(hayPapel ? ['papel', 'facturas'] : []).concat(COLS.map(function (c) { return c.t; })).concat(['contratos con el gobierno']);
    var L = [cab.map(q).join(',')].concat(filas.map(function (y) {
      var f = y.f;
      return [orden(f)[1], f.rfc, nombre(f)].concat(hayPapel ? [papelTxt(y.x), y.x.cfdi] : []).concat(COLS.map(function (c) { return celda(f, c); })).concat([f.cmx ? 'sí' : '']).map(q).join(',');
    }));
    L.push('', q('Fuentes: listas oficiales del SAT (arts. 69, 17-H Bis, 69-B y 69-B Bis del CFF), Directorio de Sancionados, OFAC, ONU y ComprasMX, con su corte en ' + location.origin + location.pathname + '. Una coincidencia es una señal para revisar, no una acusación.'));
    var b = new Blob(['﻿' + L.join('\r\n')], { type: 'text/csv;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(b); a.download = 'matriz-contrapartes.csv';
    document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }

  /* ── Arranque ────────────────────────────────────────────────────────── */
  function corre(archivos, texto) {
    var R = { rfc: {}, cfdi: [], cadena: [], malos: 0, yo: '' };
    out.innerHTML = '<p>Leyendo…</p>';
    Promise.all(Array.prototype.map.call(archivos || [], function (a) {
      return a.text().then(function (t) {
        if (/\.xml$/i.test(a.name) || /^\s*(<\?xml|<cfdi:Comprobante)/.test(t)) leeXml(t, R); else leeTexto(t, R);
      });
    })).then(function () {
      if (texto) leeTexto(texto, R);
      papeles(R);
      var todos = Object.keys(R.rfc);
      if (!todos.length) { out.innerHTML = '<p>No encontré ningún RFC. Revisa que el archivo traiga una columna con el RFC (12 o 13 caracteres) o que sean facturas CFDI en XML.</p>'; return; }
      R.recorte = todos.length > MAX;
      R.lista = todos.slice(0, MAX);
      return revisa(R.lista, function (h, t) { out.innerHTML = '<p>Revisando ' + n(h) + ' de ' + n(t) + ' RFC…</p>'; }).then(function (fs) { pinta(R, fs); });
    }).catch(function () { out.innerHTML = '<p>No pude leer los archivos o descargar las listas. Revisa tu conexión y vuelve a intentarlo.</p>'; });
  }
  arch.addEventListener('change', function () { if (arch.files.length) corre(arch.files, ''); });
  if (btn && pega) btn.addEventListener('click', function () { if (pega.value.trim()) corre([], pega.value); });
  if (suelta) {
    ['dragover', 'dragenter'].forEach(function (e) { suelta.addEventListener(e, function (ev) { ev.preventDefault(); suelta.classList.add('pd-encima'); }); });
    ['dragleave', 'drop'].forEach(function (e) { suelta.addEventListener(e, function () { suelta.classList.remove('pd-encima'); }); });
    suelta.addEventListener('drop', function (ev) { ev.preventDefault(); if (ev.dataTransfer.files.length) corre(ev.dataTransfer.files, ''); });
  }
})();
