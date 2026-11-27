/* El padrón de contrapartes (18-11-2026): una sola ficha por RFC con todo lo
   que la plataforma sabe de esa empresa o persona. Pedido del autor: «que
   nuestra base de datos quede muy bien integrada… para el compliance de
   prevención de lavado de dinero».

   No trae datos propios: lee, solo cuando se pregunta, lo que ya escriben
   los scripts de herramientas/ (cada archivo con su huella y su corte):
     - las listas del SAT del art. 69, del 17-H Bis y del 69-B Bis
       (assets/auditor/data/padron/, anclar_listas.py);
     - la lista 69-B (sat-69b.js, actualizar_69b.py);
     - el Directorio de Sancionados (sancionados.js, anclar_sancionados.py);
     - la OFAC y la ONU (sanciones-int.js, anclar_listas.py);
     - los contratos de ComprasMX (comprasmx/, actualizar_comprasmx.py).

   Las personas físicas no se publican (decisión del autor, 18-11-2026): de
   ellas solo se dice si su RFC coincide, nunca su nombre. Las listas del SAT
   las guardan por la huella SHA-256 de su RFC, no por el RFC.

   Una coincidencia es una señal para revisar, nunca una calificación ni una
   acusación: así lo dice cada respuesta. */
(function () {
  'use strict';
  var DATA = 'assets/auditor/data/';
  var RFC_RE = /^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$/;
  var GENERICO = ['XAXX010101000', 'XEXX010101000'];
  var prom = {};

  function version() {
    var s = document.querySelector('script[src*="padron.js"]') || document.querySelector('script[src*="asistente.js"]');
    var v = s && /\?v=[\w.-]+/.exec(s.getAttribute('src'));
    return v ? v[0] : '';
  }
  function carga(ruta, listo) {
    var ya = listo();
    if (ya) return Promise.resolve(ya);
    if (prom[ruta]) return prom[ruta];
    prom[ruta] = new Promise(function (ok, mal) {
      var sc = document.createElement('script');
      sc.src = DATA + ruta + version();
      sc.onload = function () { var d = listo(); if (d) ok(d); else { prom[ruta] = null; mal(new Error(ruta)); } };
      sc.onerror = function () { prom[ruta] = null; mal(new Error(ruta)); };
      document.head.appendChild(sc);
    });
    return prom[ruta];
  }
  function opcional(p) { return p.then(function (x) { return x; }, function () { return null; }); }

  function meta() { return carga('padron/meta.js', function () { return window.PADRON_META; }); }
  function sat69b() { return carga('sat-69b.js', function () { return window.SAT_69B; }); }
  function sancionados() { return carga('sancionados.js', function () { return window.AUDIT_SANCIONADOS; }); }
  function internacionales() { return carga('sanciones-int.js', function () { return window.SANC_INT; }); }
  function comprasmx(rfc) {
    var pre = rfc.slice(0, 2);
    return carga('comprasmx/p-' + pre.replace(/[^A-Z0-9]/g, '_') + '.js', function () { return window.CMX_P && window.CMX_P[pre]; })
      /* false: el índice cargó y el RFC no trae contratos (se dice en la ficha); null queda para «no se pudo cargar». */
      .then(function (L) { return L[rfc] || false; });
  }

  function hex(buf) { return Array.prototype.map.call(new Uint8Array(buf), function (b) { return ('0' + b.toString(16)).slice(-2); }).join(''); }
  function huella(sal, rfc) {
    if (!(window.crypto && crypto.subtle)) return Promise.reject(new Error('sin crypto'));
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(sal + rfc)).then(function (b) { return hex(b).slice(0, 12); });
  }
  function listasSat(M, rfc) {
    return huella(M.sal, rfc).then(function (k) {
      return carga('padron/s-' + k.slice(0, 2) + '.js', function () { return window.PADRON_S && window.PADRON_S[k.slice(0, 2)]; })
        .then(function (P) { return P[k] || ''; });
    });
  }
  /* «razón social|fi140101|ca190528I» → {n, l: [{k, f, x}]}. */
  function lee(v, M) {
    if (!v) return { n: '', l: [] };
    var p = v.split('|'), n = '', l = [];
    p.forEach(function (x) {
      var k = (/^[a-z]+/.exec(x) || [''])[0];
      if (!k || M.orden.indexOf(k) < 0 || !/^\d{6}|^[FS]\d{6}/.test(x.slice(k.length))) { n = n ? n + '|' + x : x; return; }
      var r = x.slice(k.length), sit = '';
      if (k === 'bb') { sit = r[0]; r = r.slice(1); }
      var f = r.slice(0, 6), ex = r.slice(6);
      l.push({ k: k, f: '20' + f.slice(0, 2) + '-' + f.slice(2, 4) + '-' + f.slice(4, 6), x: k === 'ca' ? ({ I: 'por insolvencia', C: 'por incosteable' }[ex] || '') : (sit === 'S' ? 'sentencia favorable' : sit === 'F' ? 'definitivo' : '') });
    });
    return { n: n, l: l };
  }
  function norm(s) {
    return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toUpperCase().replace(/[^A-Z0-9& ]/g, ' ')
      .replace(/\b(S ?A|S ?A ?B|S ?A ?P ?I|S ?DE ?R ?L|S ?C|A ?C|DE ?C ?V|DE|C ?V|SAB|SAPI|SRL|CV|LTD|LLC|INC|CORP|CO|THE|LA|EL|LOS|LAS|Y)\b/g, ' ')
      .replace(/\s+/g, ' ').trim();
  }

  var B69 = {
    P: 'El SAT presume que factura operaciones que no existieron; todavía puede desvirtuarlo.',
    F: 'El SAT determinó en definitiva que facturó operaciones inexistentes: esas facturas no tienen efectos fiscales.',
    D: 'Desvirtuó la presunción del SAT y salió de la lista.',
    S: 'Un tribunal le dio la razón frente al SAT.'
  };
  /* Las señales, de la más seria a la más leve. Nunca se suman en una calificación. */
  var PESO = { ofac: 3, onu: 3, b69F: 3, b69P: 2, se: 3, san: 2, csd: 2, nl: 2, fi: 2, ex: 2, bbF: 2, ca: 1, b69D: 0, b69S: 0, bbS: 0 };

  function rfc(q) {
    var r = String(q || '').toUpperCase().replace(/\s+/g, '');
    if (!RFC_RE.test(r)) return Promise.resolve({ rfc: r, valido: false });
    /* Los RFC genéricos (público en general y extranjeros) no son de nadie: el SAT los
       pide en las facturas sin cliente identificado. anclar_listas.py no los guarda. */
    if (GENERICO.indexOf(r) >= 0) return Promise.resolve({ rfc: r, valido: true, generico: true, senales: [], nivel: 0 });
    var moral = r.length === 12;
    return meta().then(function (M) {
      return Promise.all([
        opcional(listasSat(M, r)), opcional(sat69b()), opcional(sancionados()), opcional(internacionales()),
        moral ? opcional(comprasmx(r)) : Promise.resolve(null)
      ]).then(function (x) {
        var sat = lee(x[0], M), B = x[1], S = x[2], I = x[3], C = x[4];
        var f = { rfc: r, valido: true, moral: moral, nombre: moral ? sat.n : '', senales: [], cmx: null, corte: {}, faltan: [] };
        sat.l.forEach(function (s) {
          var L = M.sat[s.k];
          f.senales.push({ k: s.k + (s.k === 'bb' ? (s.x === 'definitivo' ? 'F' : 'S') : ''), lista: L.n, fund: L.fund, que: L.que, fecha: s.f, extra: s.x, fuente: L.fuente, url: L.pagina });
        });
        if (x[0] === null) f.faltan.push('las listas del artículo 69 del SAT');
        if (B) {
          f.corte.b69 = B.meta.corte;
          B.r.filter(function (y) { return y[0] === r; }).forEach(function (y) {
            if (moral && !f.nombre) f.nombre = y[1];
            f.senales.push({ k: 'b69' + y[2], lista: 'Lista 69-B: ' + String((B.meta.situaciones || {})[y[2]] || y[2]).toLowerCase(), fund: 'CFF, art. 69-B',
              que: B69[y[2]] || '', fecha: y[4], extra: 'oficio ' + y[3], fuente: B.meta.fuente + ', corte al ' + B.meta.corte, url: B.meta.url });
          });
        } else f.faltan.push('la lista 69-B');
        if (S) {
          f.corte.san = S.corte;
          (S.r[r] || []).forEach(function (y) {
            if (!f.nombre) f.nombre = S.n[r];
            var vig = y[4] ? (y[4] >= new Date().toISOString().slice(0, 10) ? 'vigente hasta el ' + y[4] : 'terminó el ' + y[4]) : 'sin plazo en el directorio';
            f.senales.push({ k: 'san', lista: 'Directorio de Proveedores y Contratistas Sancionados', fund: y[2] || 'sanción administrativa',
              que: 'Una dependencia lo sancionó como proveedor o contratista (' + y[1] + ', expediente ' + y[0] + '); ' + vig + '.', fecha: y[7] || y[3] || '', extra: '', fuente: S.fuente, url: S.url, vigente: !y[4] || y[4] >= new Date().toISOString().slice(0, 10) });
          });
        } else f.faltan.push('el Directorio de Sancionados');
        if (I) {
          I.r.filter(function (y) { return y[7].some(function (z) { return z === r || (z.length === 10 && r.slice(0, 10) === z); }); }).forEach(function (y) {
            var L = y[0] === 'ofac' ? M.ofac : M.onu;
            if (moral && !f.nombre) f.nombre = y[3];
            f.senales.push({ k: y[0], lista: L.n, fund: L.fund, que: L.que, fecha: '', extra: (y[0] === 'ofac' ? 'programa ' : 'régimen ') + y[5] + ', registro ' + y[1] + (y[7].indexOf(r) < 0 ? ' (la lista trae el RFC sin homoclave: confirma que sea la misma persona)' : ''), fuente: L.fuente, url: L.pagina });
          });
        } else f.faltan.push('las listas de la OFAC y de la ONU');
        if (C) { f.cmx = C; if (!f.nombre) f.nombre = C.n; }
        f.sinCmx = moral && C === false;
        f.senales.sort(function (a, b) { return (PESO[b.k] || 0) - (PESO[a.k] || 0); });
        f.nivel = f.senales.reduce(function (m, s) { return Math.max(m, PESO[s.k] || 0); }, 0);
        f.meta = M;
        return f;
      });
    });
  }

  /* Por nombre, en la OFAC y la ONU: todas las palabras de lo buscado deben
     estar en el nombre o en un alias. Coincidir en el nombre no es ser la
     misma persona. */
  function nombre(q) {
    var t = norm(q).split(' ').filter(function (w) { return w.length > 1; });
    if (!t.length || t.join('').length < 5) return Promise.resolve({ q: q, r: [], corto: true });
    return Promise.all([meta(), internacionales()]).then(function (x) {
      var M = x[0], I = x[1], out = [];
      I.r.forEach(function (y) {
        var nombres = [y[3]].concat(y[4]);
        for (var i = 0; i < nombres.length; i++) {
          var n = ' ' + norm(nombres[i]) + ' ';
          if (t.every(function (w) { return n.indexOf(' ' + w + ' ') >= 0; })) { out.push({ y: y, como: i ? nombres[i] : '' }); break; }
        }
      });
      return { q: q, r: out, meta: M };
    });
  }

  function esc(x) { return String(x == null ? '' : x).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function n(v) { return Number(v).toLocaleString('es-MX'); }
  function fechaMx(f) { var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(f || ''); return m ? m[3] + '/' + m[2] + '/' + m[1] : (f || ''); }
  var ICONO = { 3: '⛔', 2: '⚠️', 1: 'ℹ️', 0: '✅' };
  function pesos(v) { return v >= 1e6 ? '$' + (v / 1e6).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp' : '$' + Math.round(v).toLocaleString('es-MX'); }

  /* Las listas que se revisan, con su corte: para decir siempre contra qué se buscó. */
  function revisadas(f) {
    var M = f.meta, out = M.orden.map(function (k) { return M.sat[k].n; });
    out.push('lista 69-B' + (f.corte.b69 ? ' (corte al ' + f.corte.b69 + ')' : ''));
    out.push('Directorio de Sancionados' + (f.corte.san ? ' (corte al ' + fechaMx(f.corte.san) + ')' : ''));
    out.push('OFAC (' + fechaMx(M.ofac.corte) + ')', 'ONU (' + fechaMx(M.onu.corte) + ')');
    return out;
  }

  /* La ficha en HTML: la misma en la aplicación y en el chat. */
  function html(f, opc) {
    opc = opc || {};
    var CH = opc.chico || 'pd-chico', LI = opc.lista || 'pd-lista';
    if (!f.valido) return '<p>«' + esc(f.rfc) + '» no tiene forma de RFC: son 3 letras (empresa) o 4 (persona), 6 números de su fecha y 3 caracteres de homoclave.</p>';
    if (f.generico) return '<p><code>' + esc(f.rfc) + '</code> es un <b>RFC genérico</b>: el que se pone en una factura cuando no se identifica al cliente (público en general o extranjero). No es de nadie, así que no se revisa.</p>';
    var quien = f.moral ? (f.nombre ? '<b>' + esc(f.nombre) + '</b> (<code>' + esc(f.rfc) + '</code>)' : 'la empresa con RFC <code>' + esc(f.rfc) + '</code>')
      : 'la persona física con RFC <code>' + esc(f.rfc) + '</code> <span class="' + CH + '">(no publicamos el nombre de personas físicas)</span>';
    var h = '', vivas = f.senales.filter(function (s) { return (PESO[s.k] || 0) > 0; });
    if (!f.senales.length) {
      h += '<p>◻️ <b>Sin coincidencias</b> para ' + quien + ' en las ' + revisadas(f).length + ' listas que revisamos.</p>' +
        '<p class="' + CH + '">No aparecer no certifica a nadie: solo dice que, al corte de cada lista, la autoridad no lo había publicado.</p>';
    } else {
      h += '<p>' + ICONO[f.nivel] + ' ' + (vivas.length ? '<b>' + vivas.length + ' señal' + (vivas.length === 1 ? '' : 'es') + ' para revisar</b>' : '<b>Aparece, pero salió de la lista</b>') + ' sobre ' + quien + ':</p><ul class="' + LI + '">' +
        f.senales.map(function (s) {
          return '<li><span aria-hidden="true">' + ICONO[PESO[s.k] || 0] + '</span> <b>' + esc(s.lista) + '</b>' + (s.extra ? ', ' + esc(s.extra) : '') +
            (s.fecha ? ' <span class="' + CH + '">(publicado el ' + esc(fechaMx(s.fecha)) + ')</span>' : '') + '. ' + esc(s.que) +
            ' <span class="' + CH + '">' + esc(s.fund) + ' · <a href="' + esc(s.url) + '" target="_blank" rel="noopener">fuente ↗</a></span></li>';
        }).join('') + '</ul>';
    }
    if (f.cmx) h += '<p>🏛️ <b>Contratos públicos:</b> ' + n(f.cmx.c) + ' contrato' + (f.cmx.c === 1 ? '' : 's') + ' en ComprasMX por ' + pesos(f.cmx.m) + ' (importe reportado por cada institución, antes de impuestos). <a href="contratos-publicos.html?q=' + encodeURIComponent(f.rfc) + '">Verlos ➔</a></p>';
    /* Sin contratos en lo integrado (27-11-2026, pedido del autor: «tiene tratos con el gobierno y no salió»): se dice, con lo
       que la base no cubre, para que el silencio no se lea como «no tiene contratos». La cobertura vive en Contratos públicos. */
    else if (f.sinCmx) h += '<p>🏛️ <b>Contratos públicos:</b> no encontramos contratos de este RFC en los expedientes federales de ComprasMX que tenemos integrados (<a href="contratos-publicos.html?q=' + encodeURIComponent(f.rfc) + '">ve qué años cubren ➔</a>). Eso no quiere decir que no tenga tratos con el gobierno: puede tenerlos en años anteriores, con gobiernos estatales o municipales que no usan ComprasMX, o bajo otra figura (una concesión o un permiso no son un contrato). Lo que no está integrado, no lo afirmamos ni lo negamos.</p>';
    if (opc.grupo) h += '<p>🏢 <b>Grupo:</b> ' + esc(opc.grupo) + '.</p>';
    if (f.faltan.length) h += '<p class="' + CH + '">⚠️ No pude cargar ' + esc(f.faltan.join(', ')) + ': revisa tu conexión y vuelve a buscar.</p>';
    h += '<p class="' + CH + '">⚖️ Una coincidencia es una <b>señal para revisar</b>, no una acusación: la lista 69-B y las del artículo 69 son determinaciones administrativas del SAT, no condenas (salvo la sentencia por delito fiscal, que la dicta un juez), y la OFAC y la ONU sancionan, no juzgan.</p>';
    /* La respuesta en cuatro tiempos (Ronda 32, pedido del autor): tras el veredicto, lo que se revisó con su corte, lo que la
       base no cubre y qué sigue. No agrega cifras: los cortes salen de cada lista y la cobertura de contratos vive en su página. */
    var M = f.meta, R = revisadas(f), nSat = M.orden.length, cq = 'contratos-publicos.html?q=' + encodeURIComponent(f.rfc);
    h += '<div class="pd-tiempo"><p><b>Lo que revisamos</b> <span class="' + CH + '">(' + R.length + ' listas, cada una al corte que publicó su autoridad)</span></p><ul class="' + LI + '">' +
      '<li><b>Las ' + nSat + ' listas del SAT</b> (datos abiertos): ' + esc(R.slice(0, nSat).join(' · ')) + '.</li>' +
      R.slice(nSat).map(function (x) { return '<li>' + esc(x.charAt(0).toUpperCase() + x.slice(1)) + '.</li>'; }).join('') + '</ul></div>';
    var no = [['La Lista de Personas Bloqueadas de la UIF', 'No es pública. Si tu actividad es vulnerable, consúltala en tu acceso del SAT.']];
    if (f.moral && f.cmx) no.push(
      ['Sus contratos de años anteriores', 'Solo traemos los expedientes federales de ComprasMX que están integrados (<a href="' + cq + '">ve qué años cubren ➔</a>).'],
      ['Contratos con gobiernos estatales o municipales', 'Los que no usan ComprasMX los publican en su propio portal.'],
      ['Concesiones y permisos', 'No son contratos: se acreditan con su título.']);
    if (f.moral) no.push(['Quiénes son sus socios o su beneficiario controlador', 'No está en estas listas: consta en su acta y en el Registro Público de Comercio.']);
    else no.push(['Su nombre', 'De una persona física solo decimos si su RFC coincide; no publicamos quién es.']);
    h += '<div class="pd-tiempo"><p><b>Lo que la base no cubre</b></p><div class="pd-cubre"><table><thead><tr><th scope="col">Qué</th><th scope="col">Por qué, y dónde está</th></tr></thead><tbody>' +
      no.map(function (x) { return '<tr><th scope="row">' + x[0] + '</th><td>' + x[1] + '</td></tr>'; }).join('') + '</tbody></table></div>' +
      '<p class="' + CH + '">Lo que no está integrado, no lo afirmamos ni lo negamos.</p></div>';
    h += '<div class="pd-tiempo"><p><b>Qué sigue</b></p><ul class="' + LI + '">' +
      (vivas.length ? '<li><b>Antes de firmar o de pagar</b>, abre la fuente de cada señal y pide a tu contraparte el documento que la aclare.</li>'
        : '<li><b>Guarda la fecha de esta revisión:</b> vale al corte de hoy, y las listas cambian cada semana.</li>') +
      '<li><b>¿Son varios?</b> Revisa tu cartera completa de una vez, con tus RFC o tus facturas, sin subir nada: <a href="herramienta-inspector-padron.html#lote">la matriz por lote ➔</a></li>' +
      '<li><b>Para enterarte si entra a una lista:</b> el aviso cada semana es el servicio de <a href="servicio-seguimiento.html">Seguimiento ➔</a></li></ul></div>';
    return h;
  }
  function htmlNombre(x, opc) {
    opc = opc || {};
    var CH = opc.chico || 'pd-chico', LI = opc.lista || 'pd-lista';
    if (x.corto) return '<p>Escribe un nombre más completo (al menos cinco letras) para buscar en las listas de la OFAC y de la ONU.</p>';
    var M = x.meta;
    if (!x.r.length) return '<p>◻️ <b>Nadie llamado «' + esc(x.q) + '»</b> en la lista SDN de la OFAC (corte al ' + esc(fechaMx(M.ofac.corte)) + ') ni en la lista consolidada de la ONU (' + esc(fechaMx(M.onu.corte)) + ').</p>' +
      '<p class="' + CH + '">Buscamos el nombre y sus alias. El nombre puede estar escrito de otra forma; con el RFC, las listas del SAT la búsqueda es exacta.</p>';
    return '<p>⛔ <b>' + x.r.length + ' coincidencia' + (x.r.length === 1 ? '' : 's') + '</b> con «' + esc(x.q) + '» en las listas de sanciones:</p><ul class="' + LI + '">' +
      x.r.slice(0, 8).map(function (z) {
        var y = z.y, L = y[0] === 'ofac' ? M.ofac : M.onu;
        return '<li><b>' + esc(y[3]) + '</b>' + (z.como ? ' <span class="' + CH + '">(como «' + esc(z.como) + '»)</span>' : '') + ' · ' + esc(y[0] === 'ofac' ? 'OFAC' : 'ONU') +
          ', ' + (y[2] === 'i' ? 'persona' : 'entidad') + ', ' + (y[0] === 'ofac' ? 'programa ' : 'régimen ') + esc(y[5]) + ', registro ' + esc(y[1]) +
          (y[6].length ? ' · ' + esc(y[6].slice(0, 3).join(', ')) : '') + (y[7].length ? ' · RFC ' + esc(y[7].join(', ')) : '') +
          ' <span class="' + CH + '"><a href="' + esc(L.pagina) + '" target="_blank" rel="noopener">fuente ↗</a></span></li>';
      }).join('') + '</ul>' + (x.r.length > 8 ? '<p class="' + CH + '">Te muestro 8 de ' + x.r.length + '; escribe el nombre más completo.</p>' : '') +
      '<p class="' + CH + '">⚖️ Coincidir en el nombre no es ser la misma persona: confírmalo con la fecha de nacimiento, la nacionalidad, el domicilio o el RFC que trae la lista.</p>';
  }

  window.Padron = { rfc: rfc, nombre: nombre, meta: meta, norm: norm, html: html, htmlNombre: htmlNombre, RFC_RE: RFC_RE, GENERICO: GENERICO, PESO: PESO };
})();
