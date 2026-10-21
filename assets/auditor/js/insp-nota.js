/* Auditavisión · Modo Inspector › Contrasta una nota (aplicación 5,
   12-10-2026). La página la escribe herramientas/insp_nota.py con el
   catálogo de cifras oficiales ya pintado y, en JSON (#inDatos), las mismas
   cifras con su estado y su fuente: aquí no se escribe ninguna cifra.
   Este archivo filtra el catálogo, carga al vuelo el padrón municipal del
   INEGI (municipios-efipem.js) si el lector busca un municipio, lee la
   cifra de la nota («1.5 billones», «300 mil millones») y la mide contra
   el documento. Nada se estima: si la cifra oficial está pendiente, el
   contraste no se hace.
   Desde el 21-10-2026 cada paso vive en su página (data-paso en #inRaiz:
   liga, cifra o contraste; vacío en la aplicación). Lo que el lector lleva
   escrito viaja en la dirección (?liga=…&id=…&n=…&u=…) y, por si vuelve
   por el menú, en sessionStorage.
   Desde la tarde del mismo día Contrasta una nota lee la liga por su cuenta
   (insp-nota-lee.js) y este archivo maneja solo el catálogo de cifras
   oficiales, que se mudó a Qué encontró la ASF: una sola página
   (data-paso="manual") con el catálogo, la cifra de la nota y las frases
   de prueba. */
(function () {
  'use strict';

  var D;
  try { D = JSON.parse(document.getElementById('inDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  var raiz = $('inRaiz');
  if (!raiz) return;

  var UNIDADES = {
    pesos: { et: 'pesos', f: 1e-6 },
    miles: { et: 'miles de pesos', f: 1e-3 },
    millones: { et: 'millones de pesos', f: 1 },
    milmillones: { et: 'miles de millones de pesos', f: 1e3 },
    billones: { et: 'billones de pesos (millones de millones)', f: 1e6 }
  };
  var porId = {};
  D.cat.forEach(function (o) { porId[o.id] = o; });
  var est = { sel: null, filtro: '', texto: '', muni: null, cargando: false };
  var PASO = raiz.getAttribute('data-paso') || '';

  /* ---------- Lo que pasa de un paso a otro ---------- */
  var CLAVE = PASO === 'manual' ? 'auditavision-catalogo' : 'auditavision-contrasta-nota', CAMPOS = ['liga', 'id', 'n', 'u'];
  var E = {};
  try { E = JSON.parse(sessionStorage.getItem(CLAVE)) || {}; } catch (e) { E = {}; }
  var Q = new URLSearchParams(location.search);
  if (Q.has('ver') && !Q.has('liga')) delete E.liga;
  CAMPOS.forEach(function (k) { if (Q.has(k)) E[k] = Q.get(k); });
  function consulta() {
    var q = new URLSearchParams();
    CAMPOS.forEach(function (k) { if (E[k]) q.set(k, E[k]); });
    var t = q.toString();
    return t ? '?' + t : '';
  }
  /* La consulta va antes del #ancla. */
  function ancla(dest) { var k = dest.indexOf('#'); return k < 0 ? dest + consulta() : dest.slice(0, k) + consulta() + dest.slice(k); }
  function enlaces() {
    [].forEach.call(document.querySelectorAll('a[data-paso]'), function (a) {
      var dest = D.pasos && D.pasos[a.getAttribute('data-paso')];
      if (dest) a.setAttribute('href', ancla(dest));
    });
  }
  function guarda() {
    CAMPOS.forEach(function (k) { if (!E[k]) delete E[k]; });
    try { sessionStorage.setItem(CLAVE, JSON.stringify(E)); } catch (e) { /* sin almacenamiento: queda la dirección */ }
    if (PASO && window.history && history.replaceState) {
      try { history.replaceState(null, '', location.pathname + consulta() + location.hash); } catch (e) { /* nada */ }
    }
    enlaces();
  }

  function plano(t) { return String(t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function fmt(mdp) { return (mdp < 0 ? '−' : '') + '$' + Math.abs(Number(mdp)).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp'; }
  function chip(e, pend) {
    return '<span class="est-chip est-' + e + '"' + (pend ? ' data-pend="' + esc(pend) + '"' : '') + '>' + e + '</span>';
  }
  function fuente(o) {
    return o.u ? '<a href="' + esc(o.u) + '" target="_blank" rel="noopener">' + esc(o.f || 'documento') + ' ↗</a>' : esc(o.f || '');
  }

  /* ---------- Paso 1: la liga ---------- */
  var url = $('inUrl'), urlOk = $('inUrlOk');
  function ligaValida(v) { return /^https?:\/\/[^\s]+\.[^\s]+/i.test(v) ? v : ''; }
  function leerUrl() {
    if (!url) return ligaValida(String(E.liga || ''));
    var v = String(url.value || '').trim();
    var ok = ligaValida(v);
    urlOk.textContent = !v ? '' : ok ? '✓ Nota de ' + v.replace(/^https?:\/\//i, '').split('/')[0] : 'Esa liga no parece completa: debe empezar con https://';
    E.liga = ok; guarda();
    return ok;
  }
  if (url) {
    url.value = E.liga || '';
    leerUrl();
    url.addEventListener('input', leerUrl);
  }

  /* ---------- Paso 2: buscar y elegir ---------- */
  var buscar = $('inBuscar'), cuenta = $('inCuenta'), catalogo = $('inCatalogo');
  var grupos = catalogo ? [].slice.call(catalogo.querySelectorAll('.in-grupo')) : [];
  var items = catalogo ? [].slice.call(catalogo.querySelectorAll('.in-it')) : [];
  items.forEach(function (li) { var o = porId[li.dataset.id]; li._t = plano(o.n + ' ' + D.grupos[o.g] + ' ' + (o.f || '')); });
  function avisoMuni(t) { if (muniTx) muniTx.textContent = t; }
  var muniLista = $('inMuniLista'), muniTx = $('inMuniTx');

  function cargarMunicipios(listo) {
    if (est.muni) { listo(); return; }
    if (est.cargando) return;
    est.cargando = true;
    avisoMuni('Cargando el padrón municipal del INEGI…');
    var propio = document.querySelector('script[src*="insp-nota.js"]');
    var v = propio ? (propio.getAttribute('src').split('?')[1] || '') : '';
    var s = document.createElement('script');
    s.src = 'assets/auditor/js/municipios-efipem.js' + (v ? '?' + v : '');
    s.onload = function () {
      var M = window.AUDIT_MUNICIPIOS;
      est.muni = [];
      if (M) Object.keys(M.ent).forEach(function (ab) {
        var ent = M.ent[ab];
        ent.lista.forEach(function (r) {
          if (r.length > 2) {
            var o = { id: 'mun-' + ent.cve + r[0], g: 'municipios', n: r[1] + ', ' + (D.estados[ab] || ab) + ': ingresos totales en 2024', a: '2024', v: r[2] / 1e6, e: 'oficial', f: M.fuente, u: M.url };
            o._t = plano(o.n);
            est.muni.push(o); porId[o.id] = o;
          }
        });
      });
      avisoMuni(est.muni.length.toLocaleString('es-MX') + ' municipios con cifra en el padrón del INEGI (EFIPEM 2024, cifras definitivas). Escribe el nombre en el buscador.');
      listo();
    };
    s.onerror = function () { est.cargando = false; avisoMuni('No se pudo cargar el padrón municipal. Revisa tu conexión y vuelve a escribir.'); };
    document.head.appendChild(s);
  }

  function itemMuni(o) {
    return '<li class="in-it" data-id="' + esc(o.id) + '"><button type="button" class="in-elige" data-id="' + esc(o.id) + '" aria-pressed="' + (est.sel && est.sel.id === o.id) + '">' +
      '<span class="in-it-n">' + esc(o.n) + '</span><span class="in-it-v"><b>' + fmt(o.v) + '</b> ' + chip(o.e) + ' <small>' + esc(o.a) + '</small></span></button>' +
      '<span class="in-it-f">' + fuente(o) + '</span></li>';
  }

  function filtrar() {
    var q = plano(buscar.value).trim(), partes = q ? q.split(/\s+/) : [], n = 0, f = est.filtro;
    var porGrupo = {};
    items.forEach(function (li) {
      var o = porId[li.dataset.id];
      var ok = (!f || o.g === f) && partes.every(function (w) { return li._t.indexOf(w) !== -1; });
      li.hidden = !ok;
      if (ok) { n++; porGrupo[o.g] = (porGrupo[o.g] || 0) + 1; }
    });
    var nm = 0;
    if (est.muni && (q.length >= 2) && (!f || f === 'municipios')) {
      var hits = est.muni.filter(function (o) { return partes.every(function (w) { return o._t.indexOf(w) !== -1; }); });
      nm = hits.length;
      muniLista.innerHTML = hits.slice(0, 12).map(itemMuni).join('') +
        (hits.length > 12 ? '<li class="in-mas">' + (hits.length - 12) + ' municipios más: agrega el estado para acotar.</li>' : '');
    } else muniLista.innerHTML = '';
    grupos.forEach(function (g) {
      var k = g.dataset.g, c = k === 'municipios' ? nm : (porGrupo[k] || 0);
      g.hidden = f ? k !== f : (!!q && !c && !(k === 'municipios' && !est.muni));
      if (q || f) g.open = !g.hidden && (c > 0 || k === f);
    });
    var tot = n + nm;
    cuenta.textContent = !q && !f ? '' : tot
      ? tot + (tot === 1 ? ' cifra coincide.' : ' cifras coinciden.') + ' Toca la que corresponda a la nota.'
      : 'No tenemos esa cifra con documento. Prueba con otra palabra; si no está, no la podemos contrastar y no la vamos a suponer.';
  }

  var tBuscar;
  if (buscar) buscar.addEventListener('input', function () {
    clearTimeout(tBuscar);
    tBuscar = setTimeout(function () {
      filtrar();
      if (plano(buscar.value).trim().length >= 2 && !est.muni) cargarMunicipios(filtrar);
    }, 120);
  });

  [].forEach.call(raiz.querySelectorAll('.in-filtro'), function (b) {
    b.addEventListener('click', function () {
      est.filtro = b.dataset.g;
      [].forEach.call(raiz.querySelectorAll('.in-filtro'), function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      if (est.filtro === 'municipios') { cargarMunicipios(filtrar); buscar.focus(); }
      if (!est.filtro && !buscar.value) grupos.forEach(function (g) { g.hidden = false; g.open = g.dataset.g === 'nacional'; });
      filtrar();
    });
  });

  var elegida = $('inElegida');
  function pintaElegida(o) {
    if (!elegida) return;
    elegida.hidden = false;
    elegida.innerHTML =
      '<p class="in-el-t">' + (PASO === 'cifra' ? 'Ya elegiste:' : 'Vas a contrastar contra:') + '</p>' +
      '<p class="in-el-n">' + esc(o.n) + '</p>' +
      '<p class="in-el-v"><b>' + fmt(o.v) + '</b> ' + chip(o.e) + ' <span class="in-el-a">' + esc(o.a) + '</span></p>' +
      (o.s === 'negativo' || o.v < 0 ? '<p class="in-el-nota">⚠️ El documento la publica en negativo (un déficit, un balance en contra o una pérdida): aquí se compara su valor absoluto.</p>' : '') +
      (o.op ? '<p class="in-el-nota"><b>Cómo se calcula:</b> ' + esc(o.op) + '</p>' : '') +
      (o.e === 'pendiente' ? '<p class="in-el-nota">Esta cifra está pendiente de documento: no se puede usar como regla.</p>' : '') +
      '<p class="in-el-f">Fuente: ' + fuente(o) + '</p>' +
      (PASO === 'cifra'
        ? '<a class="in-cambiar" href="' + esc(D.pasos.contraste + consulta()) + '" data-paso="contraste">Seguir al paso 3 con esta cifra <span aria-hidden="true">→</span></a>'
        : PASO === 'manual' ? '<a class="in-cambiar" href="#inPaso2">Elegir otra cifra</a>'
        : '<a class="in-cambiar" href="' + esc(D.pasos.cifra + consulta()) + '" data-paso="cifra">Elegir otra cifra</a>');
    var falta = $('inFalta');
    if (falta) falta.hidden = true;
  }
  /* En el paso 2, elegir lleva al paso 3; en el 3, cambia la regla. */
  function elegir(id, sinIr) {
    var o = porId[id];
    if (!o) return;
    est.sel = o;
    E.id = id; guarda();
    if (catalogo) [].forEach.call(catalogo.querySelectorAll('.in-elige'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.id === id)); });
    if (PASO === 'cifra' && !sinIr) { location.href = D.pasos.contraste + consulta(); return; }
    pintaElegida(o);
    if (PASO === 'manual' && !sinIr && cifra) { cifra.focus({ preventScroll: true }); irA('inPaso3'); if (salida.innerHTML) contrastar(); }
  }
  if (catalogo) catalogo.addEventListener('click', function (ev) {
    var b = ev.target.closest && ev.target.closest('.in-elige');
    if (b) elegir(b.dataset.id);
  });

  function suave() { return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'; }

  /* ---------- Paso 3: leer la cifra ---------- */
  var cifra = $('inCifra'), unidad = $('inUnidad'), lectura = $('inLectura');

  /* «1.5 billones», «300 mil millones», «$1,572,073.3 mdp», «1,6» */
  function leer(txt) {
    var t = plano(txt).trim();
    if (!t) return null;
    var u = null;
    if (/billon|trill/.test(t)) u = 'billones';
    else if (/mil\s*millon|mmdp|mmd\b|millardo|\bbn\b/.test(t)) u = 'milmillones';
    else if (/millon|mdp|\bmm\b/.test(t)) u = 'millones';
    else if (/\bmil\b|\bmiles\b/.test(t)) u = 'miles';
    else if (/peso/.test(t)) u = 'pesos';
    var m = t.match(/[0-9][0-9.,\s]*/);
    if (!m) return null;
    var s = m[0].replace(/\s/g, '').replace(/[.,]$/, '');
    if (/,\d{1,2}$/.test(s) && s.indexOf('.') !== -1 && s.lastIndexOf(',') > s.lastIndexOf('.')) s = s.replace(/\./g, '').replace(',', '.');
    else if (/^\d{1,3}(,\d{3})+(\.\d+)?$/.test(s)) s = s.replace(/,/g, '');
    else if (/^\d{1,3}(\.\d{3}){2,}$/.test(s)) s = s.replace(/\./g, '');
    else if (/^\d+,\d+$/.test(s)) s = s.replace(',', '.');
    var n = Number(s);
    return isFinite(n) ? { n: n, u: u, bruto: m[0].trim() } : null;
  }

  function lecturaActual() {
    if (!cifra) return null;
    var r = leer(cifra.value);
    if (r && r.u && unidad.value !== r.u) unidad.value = r.u;
    var u = UNIDADES[unidad.value] || UNIDADES.millones;
    if (!r || !(r.n > 0)) { lectura.textContent = cifra.value.trim() ? 'No alcanzamos a leer una cifra mayor que cero.' : ''; return null; }
    var mdp = r.n * u.f;
    E.n = cifra.value.trim(); E.u = unidad.value; guarda();
    lectura.innerHTML = 'Leemos: <b>' + esc(r.n.toLocaleString('es-MX', { maximumFractionDigits: 6 })) + ' ' + u.et + '</b> = <b>' + fmt(mdp) + '</b>';
    return { n: r.n, u: u, uid: unidad.value, mdp: mdp };
  }
  if (cifra) {
    cifra.addEventListener('input', lecturaActual);
    unidad.addEventListener('change', lecturaActual);
    cifra.addEventListener('keydown', function (ev) { if (ev.key === 'Enter') contrastar(true); });
    $('inContrastar').addEventListener('click', function () { contrastar(true); });
  }

  /* ---------- El contraste ---------- */
  var salida = $('inSalida'), vacio = $('inVacio');
  function pos(p) { return Math.min(1, Math.log10(1 + Math.abs(p)) / 3) * 100; }

  function marcaTips(claves) {
    [].forEach.call(raiz.querySelectorAll('.in-tips li'), function (li) { li.classList.toggle('in-tip-on', claves.indexOf(li.dataset.tip) !== -1); });
  }

  function contrastar(mover) {
    var o = est.sel, L = lecturaActual();
    vacio.hidden = true;
    if (!o) { salida.innerHTML = '<p class="in-ver in-v-gris">Primero elige la cifra oficial contra la que quieres contrastar: <a href="' + esc(D.pasos.cifra + consulta()) + '" data-paso="cifra">ve al paso 2</a>.</p>'; if (mover) irA('inResultado'); return; }
    if (!L) { salida.innerHTML = '<p class="in-ver in-v-gris">Escribe en el paso 3 una cifra mayor que cero, como la da la nota (por ejemplo, «1.6 billones»).</p>'; cifra.focus(); return; }
    /* Un déficit o una pérdida se publican en negativo; la nota suele darlos
       en positivo. Se comparan en valor absoluto, y se avisa. */
    var neg = o.v < 0 || o.s === 'negativo', ref = Math.abs(o.v);
    var nota = L.mdp, dif = nota - ref, pct = ref ? dif / ref * 100 : 0, razon = ref ? nota / ref : 0;
    var clase, tit, porque, tips = ['anio', 'concepto'];
    if (o.e === 'pendiente') {
      clase = 'in-v-gris'; tit = 'No se puede contrastar';
      porque = 'Nuestra propia cifra está pendiente de documento. Contrastar contra ella sería medir con una regla que no está calibrada.';
    } else if (Math.abs(pct) <= 1) {
      clase = 'in-v-verde'; tit = '✅ Coincide con el documento';
      porque = 'La diferencia es de ' + Math.abs(pct).toFixed(2) + ' %: cabe en un redondeo.';
      tips = [];
    } else if (Math.abs(razon - 1000) / 1000 < 0.05 || Math.abs(razon - 0.001) / 0.001 < 0.05) {
      clase = 'in-v-rojo'; tit = '🔴 Parece un error de unidades: mil veces ' + (razon > 1 ? 'más' : 'menos');
      porque = (L.uid === 'billones' && razon > 1
        ? 'Revisa si la nota usa «billón» en el sentido del inglés (billion = mil millones). En español un billón es un millón de millones. '
        : 'Revisa si la nota confunde millones con miles de millones, o si tú elegiste otra unidad. ') +
        'Con la unidad corregida, la cifra se acercaría al documento.';
      tips = ['unidad'];
    } else if (Math.abs(pct) <= 10) {
      clase = 'in-v-ambar'; tit = '🟡 Se acerca, pero no es la misma cifra';
      porque = 'La diferencia es de ' + pct.toFixed(1) + ' %. Suele deberse a otro año, a comparar lo aprobado con lo ejercido, a pesos de otro año (reales contra nominales) o a un redondeo muy grueso.';
      tips = ['anio', 'etapa', 'real'];
    } else {
      clase = 'in-v-rojo'; tit = '🔴 No coincide con el documento';
      porque = 'La nota da ' + (dif > 0 ? 'una cifra ' + pct.toFixed(1) + ' % mayor' : 'una cifra ' + Math.abs(pct).toFixed(1) + ' % menor') + '. Antes de concluir, revisa que hable del mismo año y del mismo concepto: a veces la nota mide otra cosa con un nombre parecido.';
      tips = ['anio', 'concepto', 'unidad', 'etapa'];
    }
    if (neg) tips.push('signo');
    marcaTips(tips);

    var liga = leerUrl();
    var difTx = (dif >= 0 ? '+' : '−') + fmt(Math.abs(dif));
    var pctTx = (pct >= 0 ? '+' : '−') + Math.abs(pct).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' %';
    est.texto = [
      'Contraste de Auditavisión',
      liga ? 'Nota: ' + liga : 'Nota: (sin liga)',
      'La nota afirma: ' + L.n.toLocaleString('es-MX', { maximumFractionDigits: 6 }) + ' ' + L.u.et + ' = ' + fmt(nota),
      'Documento oficial: ' + o.n + ' (' + o.a + ') = ' + fmt(o.v) + ' [' + o.e + ']',
      'Fuente: ' + (o.f || '') + (o.u ? ' ' + o.u : ''),
      'Diferencia [derivado: nota − documento]: ' + difTx + ' (' + pctTx + ')',
      'Veredicto: ' + tit.replace(/^[^\wÁÉÍÓÚáéíóúÑñ]+/, ''),
      'Contrástala tú: ' + location.href.split('#')[0]
    ].join('\n');

    var pendiente = o.e === 'pendiente';
    var mx = Math.max(nota, ref) || 1;
    var medidor = pendiente ? '' :
      '<div class="in-medidor" role="img" aria-label="Medidor: la nota se aleja ' + esc(Math.abs(pct).toFixed(1)) + ' por ciento del documento">' +
        '<div class="in-med-zonas"><span class="in-z1">Coincide (hasta 1 %)</span><span class="in-z2">Se acerca (hasta 10 %)</span><span class="in-z3">No coincide</span></div>' +
        '<div class="in-med-barra"><span class="in-med-marca" style="left:' + pos(pct).toFixed(1) + '%"></span></div>' +
        '<div class="in-med-esc" aria-hidden="true"><span style="left:' + pos(1).toFixed(1) + '%">1 %</span><span style="left:' + pos(10).toFixed(1) + '%">10 %</span><span style="left:' + pos(100).toFixed(1) + '%">100 %</span><span style="left:100%">1,000 %</span></div>' +
      '</div>' +
      '<div class="in-barras" aria-hidden="true">' +
        '<div class="in-bar"><span class="in-bar-et">La nota</span><span class="in-bar-pista"><span class="in-bar-r in-bar-nota" style="width:' + Math.max(0.5, nota / mx * 100).toFixed(2) + '%"></span></span></div>' +
        '<div class="in-bar"><span class="in-bar-et">Documento</span><span class="in-bar-pista"><span class="in-bar-r in-bar-doc" style="width:' + Math.max(0.5, ref / mx * 100).toFixed(2) + '%"></span></span></div>' +
      '</div>';

    /* Otras cifras del catálogo que casi igualan a la de la nota: solo
       coincidencia numérica, no prueba que la nota hable de ellas. */
    var pool = D.cat.concat(est.muni || []);
    var otras = pendiente ? [] : pool.filter(function (x) { return x.id !== o.id && x.e !== 'pendiente' && x.v && Math.abs(nota - Math.abs(x.v)) / Math.abs(x.v) <= 0.01; })
      .sort(function (a, b) { return Math.abs(nota - Math.abs(a.v)) / Math.abs(a.v) - Math.abs(nota - Math.abs(b.v)) / Math.abs(b.v); }).slice(0, 3);
    var otrasHtml = !otras.length || Math.abs(pct) <= 1 ? '' :
      '<div class="in-otras"><p><b>¿Hablará de otra cifra?</b> Estas cifras oficiales quedan a menos de 1 % de la que da la nota. Es solo una coincidencia de número: revisa si el concepto es el mismo.</p><ul>' +
      otras.map(function (x) {
        return '<li><button type="button" class="in-otra" data-id="' + esc(x.id) + '">' + esc(x.n) + ' · <b>' + fmt(x.v) + '</b> ' + chip(x.e) + '</button></li>';
      }).join('') + '</ul></div>';

    vacio.hidden = true;
    salida.innerHTML =
      '<div class="in-ver ' + clase + '">' +
        '<p class="in-v-tit">' + tit + '</p>' +
        (pendiente ? '' : '<p class="in-v-grande">' + esc(pctTx) + '<small> frente al documento</small></p>') +
        medidor +
        '<div class="in-tabla">' +
          '<div><span>La nota</span><b>' + fmt(nota) + '</b><small>' + esc(L.n.toLocaleString('es-MX', { maximumFractionDigits: 6 })) + ' ' + esc(L.u.et) +
            (liga ? ' · <a href="' + esc(liga) + '" target="_blank" rel="noopener noreferrer nofollow">' + esc(liga.replace(/^https?:\/\//i, '').split('/')[0]) + ' ↗</a>' : '') + '</small></div>' +
          '<div><span>El documento ' + chip(o.e) + '</span><b>' + fmt(o.v) + '</b><small>' + esc(o.n) + ' · ' + esc(o.a) + '</small></div>' +
          '<div><span>Diferencia ' + chip('derivado') + '</span><b>' + difTx + '</b><small>Cifra de la nota menos la del documento; ' + esc(pctTx) + ' sobre la del documento.</small></div>' +
        '</div>' +
        '<p class="in-v-porque">' + porque + '</p>' +
        (neg ? '<p class="in-v-porque">⚠️ El documento publica esta cifra en negativo (' + fmt(-ref) + '); la comparamos en valor absoluto.</p>' : '') +
        '<p class="in-v-fuente">Fuente: ' + fuente(o) + '</p>' +
        otrasHtml +
        '<div class="in-acciones">' +
          '<button type="button" class="in-boton in-copiar" id="inCopiar"><span aria-hidden="true">📋</span> Copiar el contraste</button>' +
          '<button type="button" class="in-boton in-sec" id="inOtraVez"><span aria-hidden="true">↺</span> Contrastar otra nota</button>' +
        '</div>' +
        '<p class="in-copiado" id="inCopiado" role="status"></p>' +
      '</div>';
    $('inCopiar').addEventListener('click', copiar);
    $('inOtraVez').addEventListener('click', reiniciar);
    [].forEach.call(salida.querySelectorAll('.in-otra'), function (b) {
      b.addEventListener('click', function () { elegir(b.dataset.id, true); contrastar(true); });
    });
    if (mover) irA('inResultado');
  }

  function irA(id) { var el = $(id); if (el) el.scrollIntoView({ behavior: suave(), block: 'start' }); }

  function copiar() {
    var aviso = $('inCopiado');
    function hecho() { aviso.textContent = '✓ Contraste copiado. Pégalo donde quieras compartirlo.'; }
    function aMano() {
      var ta = document.createElement('textarea');
      ta.value = est.texto; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      if (ok) hecho(); else aviso.textContent = 'Tu navegador no dejó copiar. Selecciona el texto del contraste y cópialo a mano.';
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(est.texto).then(hecho, aMano);
    else aMano();
  }

  function reiniciar() {
    E = {};
    try { sessionStorage.removeItem(CLAVE); } catch (e) { /* nada */ }
    location.href = PASO === 'manual' ? location.pathname : D.pasos.liga;
  }

  /* ---------- Al abrir cada página ---------- */
  enlaces();
  if (PASO === 'cifra' && E.id) {
    if (porId[E.id]) elegir(E.id, true);
    else if (/^mun-/.test(E.id)) cargarMunicipios(function () { elegir(E.id, true); });
  }
  if (PASO === 'contraste' || PASO === 'manual') {
    var arranca = function () {
      if (E.id && porId[E.id]) elegir(E.id, true);
      if (E.u && UNIDADES[E.u]) unidad.value = E.u;
      if (E.n) { cifra.value = E.n; lecturaActual(); }
      if (Q.has('ver') && est.sel && E.n) contrastar(PASO === 'manual');
    };
    if (E.id && !porId[E.id] && /^mun-/.test(E.id)) cargarMunicipios(arranca); else arranca();
  }
  /* En la aplicación: si dejaste un contraste a medias, te lo recuerda. */
  var sigues = $('inSigues');
  if (sigues && (E.id || E.liga || E.n)) {
    var o = E.id && porId[E.id];
    sigues.hidden = false;
    sigues.innerHTML = '<b>Llevas un contraste a medias' + (o ? ' contra «' + esc(o.n) + '»' : '') + '.</b> ' +
      '<a href="' + esc(D.pasos[o ? 'contraste' : (E.liga ? 'cifra' : 'liga')] + consulta()) + '" data-paso="' + (o ? 'contraste' : (E.liga ? 'cifra' : 'liga')) + '">Sigue donde te quedaste</a> ' +
      'o <button type="button" class="in-borrar" id="inBorrar">empieza de cero</button>.';
    $('inBorrar').addEventListener('click', function () {
      E = {};
      try { sessionStorage.removeItem(CLAVE); } catch (e) { /* nada */ }
      sigues.hidden = true; enlaces();
    });
  }
})();
