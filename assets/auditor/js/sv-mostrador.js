/* El Inspector de tu servicio (servicios-revisa.html; pedido del autor, 22-11-2026: «cada
   vínculo nos va a dirigir… a una página autónoma independiente dentro de la plataforma
   donde va a estar nuestro inspector… manteniendo ese filtrado del servicio que escojas»).
   El recuadro lo arma sv_mostrador() de apartados.py; ?s=<id> deja elegido el servicio y
   &q= (con &abre=) ya revisa. Contesta con la respuesta del Inspector en su panel
   (servicios-respuesta.html?vista=1), en un marco «av-en-chat»; el dictamen es el
   documento que se descarga. Nunca un monto.

   Ronda 8 (22-11-2026, decisión del autor: «que no se trabe»):
   - La página se ve al instante: el motor del Inspector (su base pesa varios MB) se carga
     solo cuando lo vas a usar (al escribir, al tocar un ejemplo o al elegir otro servicio)
     y una sola vez: las siguientes revisiones se arman en el mismo marco, sin recargarlo.
   - Los servicios que reciben archivos (SV_SUELTA) traen su zona para soltarlos: se pasan a
     la aplicación del servicio, que los lee en el navegador. Nada se sube.
   - «Guardar en mi portafolio de investigaciones»: solo en este navegador (av-portafolio),
     y se ve también en los Expedientes de control interno. */
(function () {
  'use strict';
  var caja = document.getElementById('mostrador'), datosEl = document.getElementById('svMostDatos');
  if (!caja || !datosEl) return;
  var D = {};
  try { D = JSON.parse(datosEl.textContent); } catch (e) { return; }
  var ENTS = D._ents || [];
  delete D._ents;
  var RESP = 'servicios-respuesta.html', PORT = 'av-portafolio';
  var $ = function (id) { return document.getElementById(id); };
  var sel = $('svMostSrv'), q = $('svMostQ'), ay = $('svMostAy'), ej = $('svMostEj'), app = $('svMostApp'), res = $('svMostRes'),
    marco = $('svMostMarco'), carga = $('svMostCarga'), doc = $('svMostDoc'), form = caja.querySelector('form'),
    suelta = $('svMostSuelta'), arch = $('svMostArch'), sueltaTx = $('svMostSueltaTx'), guarda = $('svMostGuarda'),
    port = $('svPort'), portL = $('svPortLista'), portB = $('svPortBorra'),
    lugar = $('svMostLugar'), selE = $('svMostEnt'), selM = $('svMostMun'), rfcCaja = $('svMostRfcCaja'), rfcIn = $('svMostRfc');
  var mide = 0, listo = false, pendiente = null, ultimo = null, archivos = null;

  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* La dirección guarda el servicio y la pregunta, para compartirla o volver a ella. */
  function anota(sid, texto) {
    try { history.replaceState(null, '', location.pathname + '?s=' + sid + (texto ? '&q=' + encodeURIComponent(texto) : '')); } catch (e) { /* sin historial */ }
  }

  function pinta(sid) {
    var d = D[sid];
    if (!d) return;
    sel.value = sid;
    q.placeholder = d.ph;
    ay.textContent = d.ay;
    ej.innerHTML = d.ej.map(function (x) { return '<button type="button" class="sv-most-chip" data-q="' + esc(x) + '">' + esc(x) + '</button>'; }).join(' ');
    if (d.app) { app.hidden = false; app.textContent = d.bt; app.setAttribute('data-app', d.app); } else app.hidden = true;
    if (lugar) lugar.hidden = !d.lugar;
    if (rfcCaja) rfcCaja.hidden = !d.patri;
    var ciec = $('svMostCiec');
    if (ciec) ciec.hidden = !d.suelta;  // Ronda 26: el sello «Cero CIEC» va con los servicios que reciben archivos
    if (suelta) {
      suelta.hidden = !d.suelta;
      if (d.suelta) { sueltaTx.textContent = d.suelta.tx; arch.setAttribute('accept', d.suelta.acepta); }
    }
    document.title = 'El Inspector: ' + d.n + ' · Auditavisión';
    costoTx();
  }

  /* Ronda 30: lo que gasta la revisión se dice antes de tocar «Revisar» (la tabla es la de tokens.js; aquí no hay números). */
  function costoTx() {
    var c = $('svMostCosto'), d = D[sel.value], T = window.AvTokens;
    if (!c || !d) return;
    var lote = d.suelta && T ? ' Con tus archivos, ' + T.costo('lote') + ' tokens por lote.' : '';
    c.className = 'sv-most-costo' + (d.pago ? '' : ' sv-most-libre');
    if (!d.pago) c.textContent = 'Revisar aquí es gratis: no gasta tokens.' + lote;
    else if (!T) c.textContent = '';
    else if (T.ilimitado() || T.admin()) c.textContent = 'Tienes tokens ilimitados: esta revisión no descuenta saldo.';
    else {
      var s = T.saldo();
      c.textContent = 'Esta revisión usa ' + T.costo(d.patri ? 'semaforo' : 'servicio') + ' tokens · te ' + (s === 1 ? 'queda ' : 'quedan ') + s +
        '. La misma pregunta no se cobra dos veces.' + lote;
    }
  }
  document.addEventListener('av-tokens', costoTx);

  function alto() {
    try {
      var h = marco.contentDocument && marco.contentDocument.documentElement.scrollHeight;
      if (h && Math.abs(h - marco.offsetHeight) > 4) marco.style.height = h + 'px';
    } catch (e) { /* otro origen: se queda su alto */ }
  }
  function abreRes(baja) {
    res.hidden = false;
    if (doc) doc.hidden = false;
    clearInterval(mide);
    mide = setInterval(alto, 600);
    if (baja !== false) res.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function bot() { try { return marco.contentWindow && marco.contentWindow.AuditorBot; } catch (e) { return null; } }

  /* El motor, una sola vez: el marco carga la página de la respuesta sin pregunta y, ya lista, arma las que lleguen. */
  function calienta() {
    if (marco.getAttribute('data-es') === 'resp') return;
    marco.setAttribute('data-es', 'resp');
    listo = false;
    marco.src = RESP + '?vista=1';
  }
  function muestra(src, baja) {
    abreRes(baja);
    carga.hidden = false;
    marco.style.height = '';
    marco.setAttribute('data-es', 'app');
    listo = false;
    marco.src = src;
  }

  function revisa(texto, abreL, baja, lug) {
    var sid = sel.value, t = (texto || '').trim() || (D[sid] && D[sid].q) || '';
    if (!t) return;
    /* Ronda 27A: un servicio «Con tokens» gasta lo de una revisión avanzada (tokens.js). La misma pregunta no se cobra dos
       veces, y afinar el lugar (la entidad y luego uno de sus municipios) cuenta como una sola revisión. Sin saldo, la
       pregunta se queda escrita. */
    if (D[sid] && D[sid].pago && window.AvTokens &&
        !window.AvTokens.cobra(D[sid].patri ? 'semaforo' : 'servicio', sid + '|' + (lug && lug.ent ? 'lugar:' + lug.ent + '|' + (rfcIn ? rfcIn.value.trim().toUpperCase() : '') : t))) {
      q.value = texto || '';
      return;
    }
    q.value = texto ? texto : '';
    anota(sid, texto ? t : '');
    ultimo = null;
    if (guarda) guarda.hidden = true;
    abreRes(baja);
    var b = listo && marco.getAttribute('data-es') === 'resp' && bot();
    if (b && b.arma) { carga.hidden = true; b.arma(t, abreL || '', lug || null); setTimeout(alto, 50); return; }
    carga.hidden = false;
    pendiente = [t, abreL || '', lug || null];
    calienta();
  }

  marco.addEventListener('load', function () {
    alto();
    if (marco.getAttribute('data-es') === 'resp') {
      listo = true;
      var b = bot();
      if (pendiente && b && b.arma) { var p = pendiente; pendiente = null; b.arma(p[0], p[1], p[2]); }
      carga.hidden = true;
      return;
    }
    carga.hidden = true;
    if (archivos) pasaArchivos();
  });

  /* La página de la respuesta avisa qué se revisó (avisaPadre() de asistente.js). */
  window.svListo = function (info) {
    carga.hidden = true;
    ultimo = info && info.q ? info : null;
    if (guarda) { guarda.hidden = !ultimo; guarda.textContent = '💾 Guardar en mi portafolio de investigaciones'; guarda.disabled = false; }
    setTimeout(alto, 60);
  };

  /* Los archivos que sueltas pasan al campo de la aplicación del servicio (misma página, mismo navegador). */
  function pasaArchivos() {
    var d = D[sel.value], fs = archivos;
    archivos = null;
    if (!d || !d.suelta || !fs || !fs.length) return;
    try {
      var cd = marco.contentDocument, campo = cd && cd.getElementById(d.suelta.campo);
      if (!campo) return;
      var dt = new DataTransfer();
      Array.prototype.forEach.call(fs, function (f) { dt.items.add(f); });
      campo.files = dt.files;
      campo.dispatchEvent(new Event('change', { bubbles: true }));
      setTimeout(alto, 400);
    } catch (e) { /* el navegador no deja pasar archivos: se eligen dentro de la aplicación */ }
  }
  function recibe(fs) {
    var d = D[sel.value];
    if (!d || !d.suelta || !fs || !fs.length) return;
    /* Ronda 27A: tus archivos son un lote Cero CIEC (tokens.js); el mismo lote no se cobra dos veces. */
    var firma = Array.prototype.map.call(fs, function (f) { return f.name + ':' + (f.size || 0); }).sort().join('|');
    if (window.AvTokens && !window.AvTokens.cobra('lote', firma)) { if (arch) arch.value = ''; return; }
    archivos = fs;
    muestra(d.suelta.app);
  }
  if (suelta) {
    arch.addEventListener('change', function () { recibe(arch.files); });
    ['dragenter', 'dragover'].forEach(function (t) { suelta.addEventListener(t, function (ev) { ev.preventDefault(); suelta.classList.add('sv-most-suelta-sobre'); }); });
    ['dragleave', 'drop'].forEach(function (t) { suelta.addEventListener(t, function () { suelta.classList.remove('sv-most-suelta-sobre'); }); });
    suelta.addEventListener('drop', function (ev) { ev.preventDefault(); recibe(ev.dataTransfer && ev.dataTransfer.files); });
  }

  /* Tu portafolio de investigaciones: solo en este navegador. */
  function lee() { try { var l = JSON.parse(localStorage.getItem(PORT) || '[]'); return Array.isArray(l) ? l : []; } catch (e) { return []; } }
  function escribe(l) { try { localStorage.setItem(PORT, JSON.stringify(l.slice(0, 60))); return true; } catch (e) { return false; } }
  function pintaPort() {
    if (!port) return;
    var l = lee();
    port.hidden = !l.length;
    portL.innerHTML = l.map(function (x, i) {
      var reabre = x.u || (location.pathname.split('/').pop() + '?s=' + encodeURIComponent(x.s) + '&q=' + encodeURIComponent(x.q));
      return '<li><div><b>' + esc(x.t || x.q) + '</b><small>' + esc((x.o === 'auditoria' ? 'Auditoría en imágenes' : D[x.s] ? D[x.s].n : x.s) + ' · ' + x.f) + '</small>' +
        (x.t && x.t !== x.q ? '<small>«' + esc(x.q) + '»</small>' : '') + '</div><p>' +
        '<a href="' + esc(reabre) + '">↩️ Reabrir</a>' + (x.dic ? '<a href="' + esc(x.dic) + '" target="_blank" rel="noopener">🧾 Dictamen</a>' : '') +
        '<button type="button" data-port-borra="' + i + '">✕ Quitar</button></p></li>';
    }).join('');
  }
  if (guarda) guarda.addEventListener('click', function () {
    if (!ultimo) return;
    var l = lee().filter(function (x) { return !(x.s === sel.value && x.q === ultimo.q); });
    l.unshift({ s: sel.value, q: ultimo.q, t: ultimo.t || '', dic: ultimo.dic || '', f: new Date().toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' }) });
    guarda.textContent = escribe(l) ? '✅ Guardado en tu portafolio' : 'Tu navegador no deja guardar aquí';
    guarda.disabled = true;
    pintaPort();
  });
  if (portL) portL.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-port-borra]');
    if (!b) return;
    var l = lee();
    l.splice(+b.getAttribute('data-port-borra'), 1);
    escribe(l);
    pintaPort();
  });
  if (portB) portB.addEventListener('click', function () { try { localStorage.removeItem(PORT); } catch (e) { /* nada */ } pintaPort(); });
  window.addEventListener('storage', function (ev) { if (ev.key === PORT) pintaPort(); });

  /* El lugar (Ronda 9): entidad y municipio del padrón del INEGI, siempre «Municipio, Entidad» con su clave. El padrón se
     carga solo al elegir una entidad. La pregunta lleva la palabra «municipio» (o «alcaldía») para que el dictamen, que
     solo recibe la pregunta, encuentre el mismo lugar. */
  var padron = null;
  function traePadron() {
    if (window.AUDIT_MUNICIPIOS) return Promise.resolve(window.AUDIT_MUNICIPIOS);
    if (!padron) padron = new Promise(function (ok, mal) {
      var s = document.createElement('script'), v = /\?v=\w+/.exec((document.querySelector('script[src*="sv-mostrador.js"]') || {}).src || '');
      s.src = 'assets/auditor/js/municipios-efipem.js' + (v ? v[0] : '');
      s.onload = function () { ok(window.AUDIT_MUNICIPIOS); };
      s.onerror = mal;
      document.head.appendChild(s);
    });
    return padron;
  }
  function entDe(a) { return ENTS.filter(function (x) { return x[0] === a; })[0]; }
  function revisaLugar() {
    var e = entDe(selE.value);
    if (!e) return;
    var o = selM.options[selM.selectedIndex], mun = selM.value;
    var t = mun ? (e[0] === 'CDMX' ? 'Alcaldía ' : 'Municipio de ') + o.getAttribute('data-n') + ', ' + e[2] : e[2];
    /* El Semáforo Patrimonial (Ronda 25): la pregunta lo nombra y lleva el RFC o la razón social, si se escribió. */
    var d = D[sel.value];
    if (d && d.patri) {
      var rz = rfcIn ? rfcIn.value.trim() : '';
      t = 'Semáforo patrimonial: ' + t + (rz ? (/^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$/i.test(rz) ? ' · RFC de la desarrolladora ' + rz.toUpperCase() : ' · desarrolladora: ' + rz) : '');
    }
    calienta();
    revisa(t, '', true, { ent: e[0], mun: mun });
  }
  if (lugar) {
    selE.addEventListener('change', function () {
      var e = entDe(selE.value);
      selM.innerHTML = '<option value="">Toda la entidad</option>';
      selM.disabled = true;
      if (!e) return;
      calienta();
      traePadron().then(function (MU) {
        var L = MU && MU.ent[e[0]] ? MU.ent[e[0]].lista : [];
        selM.innerHTML = '<option value="">Toda la entidad: ' + esc(e[2]) + '</option>' + L.map(function (r) {
          return '<option value="' + e[1] + r[0] + '" data-n="' + esc(r[1]) + '">' + esc(r[1] + ', ' + e[2] + ' · ' + e[1] + r[0]) + '</option>';
        }).join('');
        selM.disabled = false;
      }, function () { selM.disabled = true; });
      revisaLugar();
    });
    selM.addEventListener('change', revisaLugar);
    if (rfcIn) rfcIn.addEventListener('change', function () { if (selE.value) revisaLugar(); });
  }

  sel.addEventListener('change', function () { pinta(sel.value); anota(sel.value, ''); q.value = ''; q.focus(); calienta(); });
  /* Al mostrar intención (escribir o tocar un ejemplo), el motor empieza a cargar en segundo plano. */
  q.addEventListener('input', function () { if (q.value.length > 1) calienta(); });
  ej.addEventListener('pointerenter', calienta, true);
  form.addEventListener('submit', function (ev) { ev.preventDefault(); revisa(q.value); });
  caja.addEventListener('click', function (ev) {
    var c = ev.target.closest('.sv-most-chip');
    if (c) { revisa(c.getAttribute('data-q')); return; }
    if (ev.target.closest('.sv-most-app')) muestra(app.getAttribute('data-app'));
  });

  /* Al llegar: el servicio de ?s= (o el primero) y, si trae ?q=, ya revisando. */
  var ps = new URLSearchParams(location.search), pide = ps.get('s'), texto = ps.get('q') || '';
  var sid = D[pide] ? pide : (D[sel.value] ? sel.value : Object.keys(D)[0]);
  pinta(sid);
  pintaPort();
  if (texto) revisa(texto, ps.get('abre') || '', false);
  else setTimeout(function () { try { q.focus({ preventScroll: true }); } catch (e) { q.focus(); } }, 300);
})();
