/* El expediente visual del Inspector (Ronda 9, pedido del autor, 22-11-2026: «un expediente ejecutivo visual e
   inmediato dentro del mismo recuadro»). Cuando la revisión toca una entidad o un municipio, el panel de
   servicios-revisa.html y el dictamen suman una miniatura del mapa y unas gráficas en SVG, sin librerías.

   No trae cifras propias: lee lo que la página ya cargó o lo que la base ya publica.
   - El contorno: el Marco Geoestadístico 2024 del INEGI (docs/geo/mg2024-mun-<cve>.json, el mismo del Planisferio).
   - La entidad: D.edo y D.met de la base del chat (Ramos 28 y 33, lo que recaudó, deuda y Sistema de Alertas, ASF),
     con el estado y la fuente que ya dice cada métrica.
   - El municipio: el padrón EFIPEM 2024 (AUDIT_MUNICIPIOS) y lo que pagó de deuda en el año (AUDIT_MUN_DEUDA).
   - La deuda inscrita: el Registro Público Único (AUDIT_RPU); las sumas por acreedor son derivado.
   - El fraude: las carpetas del SESNSP por municipio y entidad (AUDIT_MUN_FRAUDE).
   - Las obras con alerta ambiental: los casos de Inversión y Megaobras (D.mo.casosAmb).
   Las barras se miden contra la más grande de su propio cuadro: nunca se comparan cifras de años distintos como
   un todo ni se suman. Nada de esto entra a la huella del dictamen, que se calcula sobre la ficha. */
(function () {
  'use strict';
  var GEO = {}, CARGA = {};

  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function n(v, d) { return Number(v).toLocaleString('es-MX', { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 }); }
  function mdp(v) { return '$' + n(v, 1) + ' mdp'; }
  function chip(e) { return '<span class="est-chip est-' + e + '">' + (e === 'derivado' ? 'auditada' : e) + '</span>'; }
  function version() {
    var s = document.querySelector('script[src*="asistente.js"]'), m = s && /\?v=([\w]+)/.exec(s.getAttribute('src'));
    return m ? '?v=' + m[1] : '';
  }
  /* Un archivo de datos que la página no cargó: una sola vez, solo al usarlo. */
  function script(src, nombre) {
    if (window[nombre]) return Promise.resolve(window[nombre]);
    if (!CARGA[src]) CARGA[src] = new Promise(function (ok, mal) {
      var s = document.createElement('script');
      s.src = src + version();
      s.onload = function () { ok(window[nombre]); };
      s.onerror = mal;
      document.head.appendChild(s);
    });
    return CARGA[src];
  }
  function geo(cve) {
    if (!GEO[cve]) GEO[cve] = fetch('docs/geo/mg2024-mun-' + cve + '.json').then(function (r) { if (!r.ok) throw r; return r.json(); });
    return GEO[cve];
  }

  /* La miniatura: todos los municipios de la entidad; el elegido, resaltado (o la entidad entera). */
  function mapa(G, mun, nombre) {
    var vb = G.vb || [100, 100], sel = null;
    var ps = G.m.map(function (x) {
      var es = mun && x.c === mun;
      if (es) sel = x;
      return '<path class="' + (mun ? (es ? 'pv-sel' : 'pv-mun') : 'pv-ent') + '" d="' + x.d + '"><title>' + esc(x.n) + '</title></path>';
    });
    if (sel) ps.push(ps.splice(G.m.indexOf(sel), 1)[0]);
    return '<figure class="pv-mapa"><svg viewBox="0 0 ' + vb[0] + ' ' + vb[1] + '" role="img" aria-label="' + esc('Mapa de ' + nombre) + '" preserveAspectRatio="xMidYMid meet">' + ps.join('') + '</svg>' +
      '<figcaption>' + esc(nombre) + '. Límites del <a href="' + esc(G.pagina || 'https://www.inegi.org.mx/temas/mg/') + '" target="_blank" rel="noopener">Marco Geoestadístico 2024 del INEGI</a>: geoestadísticos, no la fuente oficial de la división político-administrativa.</figcaption></figure>';
  }

  /* Un cuadro de barras: f = [{et, v, tx, e}]; cada barra contra la más grande del cuadro. */
  function barras(tit, f, pie) {
    f = f.filter(function (x) { return x.v != null && x.v >= 0; });
    if (!f.length) return '';
    var max = Math.max.apply(null, f.map(function (x) { return x.v; })) || 1;
    return '<section class="pv-caja"><h4>' + tit + '</h4><ul class="pv-barras">' + f.map(function (x) {
      var w = Math.max(0.5, Math.round(x.v / max * 1000) / 10);
      return '<li><span class="pv-et">' + esc(x.et) + ' ' + chip(x.e) + '</span><span class="pv-bar"><svg viewBox="0 0 100 10" preserveAspectRatio="none" aria-hidden="true">' +
        '<rect class="pv-fondo" x="0" y="0" width="100" height="10" rx="2"></rect><rect class="pv-lleno' + (x.cls ? ' ' + x.cls : '') + '" x="0" y="0" width="' + w + '" height="10" rx="2"></rect></svg>' +
        '<b>' + esc(x.tx) + '</b></span></li>';
    }).join('') + '</ul>' + (pie ? '<p class="pv-pie">' + pie + '</p>' : '') + '</section>';
  }
  function fuente(fu) { return fu ? (fu.url ? '<a href="' + esc(fu.url) + '" target="_blank" rel="noopener">' + esc(fu.tx) + '</a>' : esc(fu.tx)) : ''; }

  /* La deuda inscrita en el Registro Público Único: saldo por acreedor (suma derivada), los tres mayores. */
  function rpu(R, filtro, quien) {
    var L = R.r.filter(filtro), o = {}, tot = 0;
    L.forEach(function (x) { if (x[8]) { var k = R.inst[x[4]][0]; o[k] = (o[k] || 0) + x[8]; tot += x[8]; } });
    var top = Object.keys(o).map(function (k) { return [k, o[k]]; }).sort(function (a, b) { return b[1] - a[1] || (a[0] < b[0] ? -1 : 1); });
    var M = R.meta, fu = '<a href="' + esc(M.pagina) + '" target="_blank" rel="noopener">' + esc(M.fuente) + '</a>, saldo al ' + esc(M.corteTxt) + ' (sha256 ' + esc(M.sha256.slice(0, 12)) + '…)';
    if (!L.length) return '<section class="pv-caja"><h4>🏦 Deuda inscrita en el Registro Público Único</h4><p>' + esc(quien) + ' no tiene créditos ni obligaciones inscritos ' + chip('oficial') +
      '. Eso no quiere decir que no le deba a nadie: los adeudos con proveedores no pasan por ese registro.</p><p class="pv-pie">' + fu + '</p></section>';
    return barras('🏦 Deuda inscrita en el Registro Público Único: ' + L.length + ' crédito' + (L.length > 1 ? 's' : '') + ' u obligaci' + (L.length > 1 ? 'ones' : 'ón') +
      (tot ? ', saldo ' + mdp(tot) : ''), top.slice(0, 3).map(function (x) { return { et: x[0], v: x[1], tx: mdp(x[1]), e: 'derivado', cls: 'pv-deuda' }; }),
      (top.length > 3 ? 'Los tres acreedores con más saldo, de ' + top.length + '. ' : '') + 'Cada crédito es oficial; las sumas por acreedor son nuestras. En una emisión bursátil el registro anota al fiduciario. ' + fu);
  }

  function fraude(F, k, quien) {
    var v = k ? (k.length === 2 ? F.ent[k] : F.mun[k]) : null;
    if (!v) return '';
    return barras('🚨 Carpetas por fraude (SESNSP)', [{ et: 'Enero a diciembre de 2025', v: v[0], tx: n(v[0]), e: 'oficial', cls: 'pv-fraude' },
      { et: 'Enero a ' + (F.corte2026 || '').replace(/^enero-/, '').replace(/ (\d{4})$/, ' de $1'), v: v[1], tx: n(v[1]), e: 'oficial', cls: 'pv-fraude' }],
      'Carpetas de investigación abiertas en ' + esc(quien) + '. Una carpeta no es una víctima ni un fraude probado, y más carpetas no quiere decir más fraude. ' +
      '<a href="' + esc(F.pagina) + '" target="_blank" rel="noopener">' + esc(F.fuente) + '</a>.');
  }

  function obras(D, a, en) {
    var C = (D.mo && D.mo.casosAmb) || [], L = C.filter(function (x) { return (x.edos || []).indexOf(a) >= 0; });
    if (!L.length) return '';
    return '<section class="pv-caja"><h4>🏗️ Megaobras con alerta ambiental en ' + esc(en) + '</h4><ul class="pv-obras">' + L.map(function (x) {
      return '<li><span aria-hidden="true">' + esc(x.ico) + '</span> <b>' + esc(x.nombre) + '</b> <small>' + esc(x.tipoNom || '') + '</small>' +
        (x.asfMdp ? '<span>Por aclarar ante la ASF: ' + mdp(x.asfMdp) + ' ' + chip('derivado') + '</span>' : '') + '</li>';
    }).join('') + '</ul><p class="pv-pie">De la herramienta Inversión y Megaobras, por entidad: no quiere decir que la obra pase por cada municipio. Lo «por aclarar» es la suma de las auditorías de su expediente de la ASF.</p></section>';
  }

  /* Los rangos del semáforo con su Acuerdo del DOF (Ronda 14, D.sda de sistema_alertas.py): leyenda, sin cifras nuevas.
     El rango de cada indicador es la cifra oficial puesta junto al límite del Acuerdo (auditada). */
  function leyendaSda(S, e) {
    if (!S || !S.e) return '';
    var N = ['Deuda ÷ ingresos de libre disposición', 'Pago de la deuda ÷ esos ingresos', 'Corto plazo menos caja ÷ ingresos totales'], V = [e.ild, e.sd, e.ocp];
    var r = function (v, L) { return v <= L[0] ? 'bajo' : (v <= L[1] ? 'medio' : 'alto'); };
    return '<span class="pv-sda"><b>Rangos del Sistema de Alertas</b> (bajo / medio / alto): ' + S.e.map(function (L, i) {
      return esc(N[i]) + ' ≤ ' + n(L[0], L[0] % 1 ? 1 : 0) + ' % / hasta ' + n(L[1], L[1] % 1 ? 1 : 0) + ' % / más' + (V[i] == null ? '' : ' (aquí: rango ' + r(V[i], L) + ')');
    }).join('; ') + ' ' + chip('derivado') + '. ' + fuente(S.fe) + '.</span>';
  }

  /* Ronda 26 (Plan Maestro del autor, 26-11-2026): el Indicador 3 del Sistema de Alertas, para quien le vende o le
     construye a ese gobierno. La cifra es la de la base (D.edo de la entidad o AUDIT_MUN_DEUDA.sda del municipio) y su
     rango sale de los límites del Acuerdo (D.sda, Ronda 14): auditada. Sin cifras nuevas y fuera de la huella del dictamen.
     Un rango alto es una señal para revisar el plazo de pago, nunca un pronóstico de que no pagará. */
  function ind3(v, L, fu, quien) {
    if (v == null || !L) return '';
    var rg = v <= L[0] ? 'bajo' : (v <= L[1] ? 'medio' : 'alto'), cls = { bajo: 'pv-verde', medio: 'pv-amarillo', alto: 'pv-rojo' }[rg];
    var top = Math.max(L[1] * 1.5, v, 1), x = function (p) { return Math.max(0, Math.min(100, p / top * 100)); };
    var regla = '<svg class="pv-i3-regla" viewBox="0 0 100 14" preserveAspectRatio="none" role="img" aria-label="Rango ' + rg + ' del indicador 3">' +
      '<rect x="0" y="3" width="' + x(L[0]) + '" height="8" class="pv-i3-b"/><rect x="' + x(L[0]) + '" y="3" width="' + (x(L[1]) - x(L[0])) + '" height="8" class="pv-i3-m"/>' +
      '<rect x="' + x(L[1]) + '" y="3" width="' + (100 - x(L[1])) + '" height="8" class="pv-i3-a"/><rect x="' + Math.max(0, x(v) - 0.8) + '" y="0" width="1.6" height="14" class="pv-i3-v"/></svg>';
    return '<section class="pv-caja pv-i3"><h4>Si le vendes o le construyes: el indicador 3 del Sistema de Alertas</h4>' +
      '<p><b>' + esc(quien) + '</b>: obligaciones a corto plazo y con proveedores y contratistas, menos lo que tiene en caja, entre sus ingresos totales: <b class="' + cls + '">' + n(v, 1) + ' %</b> ' + chip('oficial') +
      ', <b>rango ' + rg + '</b> ' + chip('derivado') + ' (bajo hasta ' + n(L[0], 1) + ' %, medio hasta ' + n(L[1], 1) + ' %, alto arriba).</p>' + regla +
      '<p class="pv-pie">' + (v < 0 ? 'Negativo quiere decir que tenía en caja más de lo que debía a corto plazo. ' : '') +
      'Un rango alto es una señal para revisar el plazo y la forma de pago de tu contrato, nunca un pronóstico de que no te pagará. ' + fu + '</p></section>';
  }

  function entidad(D, MU, e) {
    var M = D.met || {}, h = [];
    var fi = [{ k: 'r28', et: 'Participaciones (Ramo 28), 2026' }, { k: 'r33', et: 'Aportaciones (Ramo 33), 2026' }, { k: 'propia', et: 'Lo que recaudó por su cuenta, 2024' }]
      .map(function (x) { var m = M[x.k] || {}; return { et: x.et, v: e[x.k], tx: e[x.k] == null ? '' : mdp(e[x.k]), e: m.e || 'oficial' }; });
    h.push(barras('💰 Lo que le entra al gobierno del estado', fi, 'Años distintos: las tres barras no se suman. ' + fuente((M.r28 || {}).fu) + '; ' + fuente((M.propia || {}).fu) + '.'));
    if (e.deuda != null) {
      var semC = { verde: 'pv-verde', amarillo: 'pv-amarillo', rojo: 'pv-rojo' }[String(e.sem || '').toLowerCase()] || '';
      h.push(barras('📉 Su deuda frente a lo que puede gastar libremente', [
        { et: 'Deuda entre ingresos de libre disposición', v: e.ild, tx: e.ild == null ? '' : n(e.ild, 1) + ' %', e: 'oficial', cls: semC },
        { et: 'Pago de la deuda entre ingresos de libre disposición', v: e.sd, tx: e.sd == null ? '' : n(e.sd, 1) + ' %', e: 'oficial', cls: semC }],
        'Deuda pública: <b>' + mdp(e.deuda) + '</b> ' + chip('oficial') + (e.sem ? '; semáforo <b>' + esc(e.sem) + '</b> del Sistema de Alertas' : '') + '. ' + fuente((M.deuda || {}).fu) + '.' + leyendaSda(D.sda, e)));
    }
    if (e.ocp != null && D.sda && D.sda.e) h.push(ind3(e.ocp, D.sda.e[2], fuente((M.deuda || {}).fu) + '; límites: ' + fuente(D.sda.fe) + '.', e.n));
    if (e.asf != null) h.push(barras('🔎 Lo que dejó la ASF (Cuenta Pública 2024)', [{ et: 'Monto por aclarar', v: e.asf, tx: mdp(e.asf), e: 'oficial', cls: 'pv-asf' }],
      (e.aud != null ? n(e.aud) + ' auditorías. ' : '') + 'Por aclarar no quiere decir desviado: la entidad puede solventarlo. ' + fuente((M.asf || {}).fu) + '.'));
    return h;
  }

  function municipio(MU, MD, m) {
    var c = MU.campos, r = m.v ? [m.cve.slice(2)].concat(m.v) : null, h = [];
    if (r && r.length >= c.length) {
      var x = {}; c.forEach(function (k, i) { x[k] = r[i]; });
      var mp = function (v) { return mdp(v / 1e6); };
      h.push(barras('💰 Cómo se financió en ' + MU.anio + ' (ingreso total ' + mp(x.ing) + ')', [
        { et: 'Lo que cobra por su cuenta', v: x.propios, tx: mp(x.propios), e: 'oficial' },
        { et: 'de eso, predial', v: x.predial, tx: mp(x.predial), e: 'oficial', cls: 'pv-sub' },
        { et: 'Participaciones federales', v: x.part, tx: mp(x.part), e: 'oficial' },
        { et: 'Aportaciones federales', v: x.aport, tx: mp(x.aport), e: 'oficial' }],
        'Lo demás de su ingreso (convenios, financiamiento y otros) no va en las barras. <a href="' + esc(MU.url) + '" target="_blank" rel="noopener">' + esc(MU.fuente) + '</a>'));
    } else h.push('<section class="pv-caja"><h4>💰 Sus finanzas</h4><p>' + esc(m.n) + ' no rindió su cuenta de ' + MU.anio + ' al INEGI ' + chip('pendiente') + ': sin cifra, no en cero.</p></section>');
    var d = MD && MD.mun ? MD.mun[m.cve] : null;
    if (d && d.length >= 6 && !d[1] && !d[2] && !d[5]) h.push('<section class="pv-caja"><h4>📉 Lo que pagó y pidió prestado en ' + (MD.anio || MU.anio) + '</h4><p>' + esc(m.n) +
      ' no reportó al INEGI pagos de capital ni de intereses, ni préstamos recibidos, en ' + (MD.anio || MU.anio) + ' ' + chip('oficial') + '. Eso no dice lo que debe. ' + esc(MD.fuente || '') + '</p></section>');
    else if (d && d.length >= 6) h.push(barras('📉 Lo que pagó y pidió prestado en ' + (MD.anio || MU.anio), [
      { et: 'Pagó de capital (amortización)', v: d[1], tx: mdp(d[1] / 1e6), e: 'oficial', cls: 'pv-deuda' },
      { et: 'Pagó de intereses', v: d[2], tx: mdp(d[2] / 1e6), e: 'oficial', cls: 'pv-deuda' },
      { et: 'Préstamos que recibió', v: d[5], tx: mdp(d[5] / 1e6), e: 'oficial', cls: 'pv-deuda' }],
      'Es lo que pagó y pidió prestado en el año, no lo que debe. ' + esc(MD.fuente || 'INEGI, EFIPEM')));
    var S = MD && MD.sda, sm = S && S.m && S.m[m.cve], D3 = ((window.AUDITOR_BASE || {}).dat || {}).sda;
    if (sm && D3 && D3.m && S.campos) {
      var i3 = sm[S.campos.indexOf('ocpPct')];
      if (i3 != null && sm[S.campos.indexOf('sem')] > 0) h.push(ind3(i3, D3.m[2], '<a href="' + esc(S.pagina || S.url || '') + '" target="_blank" rel="noopener">' + esc(S.fuente || 'SHCP, Sistema de Alertas') + '</a>; límites: ' + fuente(D3.fm) + '.', m.n));
    }
    return h;
  }

  /* lu = { e: [entidad de D.edo], m: municipio de la charla o null }. Devuelve una promesa con el HTML, o '' si no hay lugar. */
  function arma(lu) {
    var B = window.AUDITOR_BASE, D = (B && B.dat) || {}, MU = window.AUDIT_MUNICIPIOS;
    var m = lu && lu.m, e = m ? (D.edo || []).filter(function (x) { return x.a === m.a; })[0] : lu && lu.e && lu.e.length === 1 ? lu.e[0] : null;
    if (!e || !MU || !MU.ent[e.a]) return Promise.resolve('');
    var cve = MU.ent[e.a].cve, nombre = m ? m.n + ', ' + m.en : e.n;
    var datos = [geo(cve).catch(function () { return null; }),
      script('assets/auditor/data/deuda-rpu.js', 'AUDIT_RPU').catch(function () { return null; }),
      script('assets/auditor/js/municipios-fraude.js', 'AUDIT_MUN_FRAUDE').catch(function () { return null; })];
    return Promise.all(datos).then(function (x) {
      var G = x[0], R = x[1], F = x[2], h = [];
      if (m) h = h.concat(municipio(MU, window.AUDIT_MUN_DEUDA, m));
      else h = h.concat(entidad(D, MU, e));
      if (R) h.push(m ? rpu(R, function (y) { return y[3] === m.cve; }, 'El municipio de ' + m.n) : rpu(R, function (y) { return y[0] === e.a; }, e.n));
      if (F) h.push(fraude(F, m ? m.cve : cve, nombre));
      h.push(obras(D, e.a, e.n));
      return '<section class="pv" aria-label="Expediente visual">' + '<h3><span aria-hidden="true">🗺️</span> El expediente visual: ' + esc(nombre) + '</h3>' +
        '<div class="pv-rejilla">' + (G ? mapa(G, m ? m.cve.slice(2) : null, nombre) : '') + '<div class="pv-graf">' + h.join('') + '</div></div>' +
        '<p class="pv-pie">Lo mismo que trae la base, dibujado: ninguna cifra nueva. Cada barra se mide contra la más grande de su cuadro.</p></section>';
    });
  }

  window.InspVisual = { arma: arma };
})();
