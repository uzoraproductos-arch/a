/* Auditavisión · Costo Ambiental › Basura y protección (aplicación 3,
   16-10-2026). La página la escribe herramientas/am_basura.py con todas
   las cifras ya puestas; en JSON (#abDatos) van los pocos números que este
   archivo necesita para las cuentas que hace el lector: la basura de su
   casa, la serie que se toca, la calculadora de la balanza y el
   presupuesto por órgano con sus cinco medidas. Todo lo que calcula aquí es
   «derivado» y dice su operación. No carga el motor ni la base.
   Prefijo: ab-. Preferencias en localStorage: av-am-basura. */
(function () {
  'use strict';

  var D;
  try { D = JSON.parse(document.getElementById('abDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  var raiz = $('abRaiz');
  if (!raiz) return;
  var CLAVE = 'av-am-basura';
  var quieto = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var pref = { p: 3, d: 365, med: 'aprobado' };
  try {
    var g = JSON.parse(localStorage.getItem(CLAVE) || '{}');
    if (g.p >= 1 && g.p <= 12) pref.p = Math.round(g.p);
    if ([1, 7, 30, 365].indexOf(g.d) >= 0) pref.d = g.d;
    if (['aprobado', 'pagado', 'proyecto2027', 'avance', 'cambio'].indexOf(g.med) >= 0) pref.med = g.med;
  } catch (e) { /* sin almacenamiento: valores de fábrica */ }
  function guardar() {
    try { localStorage.setItem(CLAVE, JSON.stringify(pref)); } catch (e) { /* nada */ }
  }

  function n(v, d) {
    return v.toLocaleString('es-MX', { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 });
  }
  function pct(v, d) { return n(v, d == null ? 1 : d) + ' %'; }
  function mdp(pesos) { return '$' + n(pesos / 1e6, 1) + ' mdp'; }
  function chip(e) { return '<span class="est-chip est-' + e + '">' + e + '</span>'; }
  function esc(v) {
    return String(v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function pulsar(grupo, btn) {
    grupo.querySelectorAll('.ab-op').forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
  }

  /* 1. ¿Cuánto crees? */
  var rango = $('abAdivinaR');
  if (rango) {
    rango.addEventListener('input', function () { $('abAdivinaV').textContent = rango.value; });
    $('abAdivinaB').addEventListener('click', function () {
      var t = Number(rango.value), r = D.relPct, dif = Math.abs(t - r);
      var juicio = dif <= 3 ? '🎯 ¡Casi exacto!' : (t > r ? '😬 Fuiste optimista.' : '🔎 Fuiste más pesimista que la realidad.');
      var res = $('abAdivinaRes');
      res.hidden = false;
      res.innerHTML = juicio + ' Dijiste <b>' + t + '</b>; la respuesta es <b>' + n(r, 1) + ' kilos de cada 100</b> ' + chip('oficial') +
        '. Son ' + n(D.relT, 1) + ' toneladas al día en 52 rellenos sanitarios, de ' + n(D.sitT) +
        ' que llegan a disposición final. El resto va a sitios no controlados.';
    });
  }

  /* 2. El camino de la basura, paso por paso */
  var camino = $('abCamino');
  var timers = [];
  function caminoTodo(on) {
    timers.forEach(clearTimeout); timers = [];
    camino.querySelectorAll('.ab-paso').forEach(function (li) { li.classList.toggle('ab-on', on); });
  }
  if (camino) {
    camino.classList.add('ab-js');
    caminoTodo(true);
    $('abCaminoB').addEventListener('click', function () {
      caminoTodo(false);
      var pasos = camino.querySelectorAll('.ab-paso');
      pasos.forEach(function (li, i) {
        timers.push(setTimeout(function () {
          li.classList.add('ab-on');
          if (i === 0 && li.scrollIntoView && !quieto) li.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, quieto ? 0 : 250 + i * 1100));
      });
    });
    $('abCaminoT').addEventListener('click', function () { caminoTodo(true); });
  }

  /* 3. La basura de tu casa */
  function casa() {
    var kg = pref.p * D.per * pref.d;
    var noRec = kg * (100 - D.recPct) / 100;
    var per = { 1: 'en un día', 7: 'en una semana', 30: 'en 30 días', 365: 'en un año' }[pref.d];
    $('abPersonas').textContent = pref.p;
    $('abPersonasL').textContent = pref.p === 1 ? 'persona' : 'personas';
    $('abCasaRes').innerHTML =
      '<div class="ab-casa-c"><span>Tu casa genera ' + per + '</span><b class="ab-num">' + n(kg, kg < 100 ? 1 : 0) + ' kg</b>' + chip('derivado') + '</div>' +
      '<div class="ab-casa-c ab-casa-r"><span>Al promedio nacional, no se recolectaría</span><b class="ab-num">' + n(noRec, noRec < 100 ? 1 : 0) + ' kg</b>' + chip('derivado') + '</div>';
    document.querySelectorAll('#abCasa .ab-op').forEach(function (b) {
      b.setAttribute('aria-pressed', Number(b.getAttribute('data-dias')) === pref.d ? 'true' : 'false');
    });
    $('abMenos').disabled = pref.p <= 1;
    $('abMas').disabled = pref.p >= 12;
  }
  if ($('abCasa')) {
    $('abMenos').addEventListener('click', function () { if (pref.p > 1) { pref.p--; guardar(); casa(); } });
    $('abMas').addEventListener('click', function () { if (pref.p < 12) { pref.p++; guardar(); casa(); } });
    document.querySelectorAll('#abCasa .ab-op').forEach(function (b) {
      b.addEventListener('click', function () { pref.d = Number(b.getAttribute('data-dias')); guardar(); casa(); });
    });
    casa();
  }

  /* 4. La serie que se toca */
  function serieVer(i) {
    var a = D.serie.a, t = D.serie.t;
    document.querySelectorAll('#abSerie .ab-s-b').forEach(function (b) {
      var on = Number(b.getAttribute('data-i')) === i;
      b.classList.toggle('ab-act', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    var h = '<b>' + a[i] + ':</b> ' + n(t[i]) + ' toneladas recolectadas al día ' + chip('oficial') + '.';
    if (i > 0) {
      var d = t[i] - t[i - 1];
      h += ' Contra ' + a[i - 1] + ': ' + (d >= 0 ? '+' : '−') + n(Math.abs(d)) + ' t (' + (d >= 0 ? '+' : '−') + pct(Math.abs(d / t[i - 1] * 100)) + ') ' + chip('derivado') + '.';
      var d0 = t[i] - t[0];
      if (i > 1) h += ' Contra ' + a[0] + ': ' + (d0 >= 0 ? '+' : '−') + pct(Math.abs(d0 / t[0] * 100)) + ' ' + chip('derivado') + '.';
    } else {
      h += ' Es el primer año de la serie.';
    }
    $('abSerieDet').innerHTML = h;
  }
  if ($('abSerie')) {
    document.querySelectorAll('#abSerie .ab-s-b').forEach(function (b) {
      b.addEventListener('click', function () { serieVer(Number(b.getAttribute('data-i'))); });
    });
    serieVer(D.serie.a.length - 1);
  }

  /* 5. La balanza: cuánto daño por lo que se gasta en proteger */
  var calcIn = $('abCalcIn');
  function calc() {
    var v = Number(String(calcIn.value).replace(/[$,\s]/g, ''));
    var out = $('abCalcRes');
    if (!isFinite(v) || v < 0 || calcIn.value.trim() === '') {
      out.innerHTML = 'Escribe una cantidad en pesos, por ejemplo 100.';
      return;
    }
    var dano = v * D.dano / D.gpa;
    out.innerHTML = 'el país resintió <b class="ab-num">$' + n(dano, dano < 1000 ? 2 : 0) + '</b> de daño ambiental ' + chip('derivado');
    document.querySelectorAll('#abCalc .ab-op').forEach(function (b) {
      b.setAttribute('aria-pressed', Number(b.getAttribute('data-m')) === v ? 'true' : 'false');
    });
  }
  if (calcIn) {
    calcIn.addEventListener('input', calc);
    document.querySelectorAll('#abCalc .ab-op').forEach(function (b) {
      b.addEventListener('click', function () { calcIn.value = n(Number(b.getAttribute('data-m'))); calc(); });
    });
    calc();
  }

  /* 6. El presupuesto, órgano por órgano */
  var MED = {
    aprobado: { tit: 'Aprobado 2026', val: function (u) { return u.aprobado; }, fmt: mdp, e: 'oficial',
      nota: function () { return chip('oficial') + ' Lo aprobado en el Presupuesto de Egresos 2026. ' + liga('PEF'); } },
    pagado: { tit: 'Pagado al 30 de junio', val: function (u) { return u.pagado; }, fmt: mdp, e: 'oficial',
      nota: function () { return chip('oficial') + ' Lo pagado al 30 de junio de 2026. ' + liga('AV2T2026'); } },
    proyecto2027: { tit: 'Proyecto 2027', val: function (u) { return u.proyecto2027; }, fmt: mdp, e: 'oficial',
      nota: function () { return chip('oficial') + ' Lo que el Ejecutivo propone para 2027; la Cámara de Diputados aún puede cambiarlo. ' + liga('PPEF2027'); } },
    avance: { tit: 'Avance del pago', val: function (u) { return u.modificado > 0 ? u.pagado / u.modificado * 100 : 0; }, fmt: function (v) { return pct(v); }, e: 'derivado',
      nota: function () { return chip('derivado') + ' Pagado al 30 de junio ÷ presupuesto modificado × 100. A medio año, un ritmo parejo daría cerca del 50 %. ' + liga('AV2T2026'); } },
    cambio: { tit: 'Cambio 2027 contra 2026', val: function (u) { return u.aprobado > 0 ? (u.proyecto2027 / u.aprobado - 1) * 100 : 0; },
      fmt: function (v) { return (v >= 0 ? '+' : '−') + pct(Math.abs(v)); }, e: 'derivado',
      nota: function () { return chip('derivado') + ' (Proyecto 2027 ÷ aprobado 2026 − 1) × 100, en pesos nominales: no descuenta la inflación. ' + liga('PEF') + ' · ' + liga('PPEF2027'); } }
  };
  function liga(k) {
    var f = D.fu[k];
    return f ? '<a class="ab-fu" href="' + esc(f.url) + '" target="_blank" rel="noopener noreferrer">' + esc(f.doc) + ' ↗</a>' : '';
  }
  var orgSel = null;
  function org() {
    var m = MED[pref.med], lista = $('abOrg');
    var filas = D.org.map(function (u, i) { return { u: u, i: i, v: m.val(u) }; })
      .sort(function (a, b) { return b.v - a.v; });
    var tope = Math.max.apply(null, filas.map(function (f) { return Math.abs(f.v); })) || 1;
    if (pref.med === 'avance') tope = 100;
    lista.innerHTML = filas.map(function (f) {
      var w = Math.max(0.01, Math.abs(f.v) / tope);
      return '<li><button type="button" class="ab-org-b' + (orgSel === f.i ? ' ab-act' : '') + '" data-i="' + f.i + '" aria-pressed="' + (orgSel === f.i) + '">' +
        '<span class="ab-org-n">' + esc(f.u.n) + '</span>' +
        '<span class="ab-org-riel"><span class="ab-org-barra' + (f.v < 0 ? ' ab-neg' : '') + '" style="--ab-w:' + w.toFixed(4) + '"></span></span>' +
        '<span class="ab-org-v ab-num">' + m.fmt(f.v) + '</span></button></li>';
    }).join('');
    $('abOrgNota').innerHTML = m.nota();
    document.querySelectorAll('.ab-med .ab-op').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-med') === pref.med ? 'true' : 'false');
    });
    lista.querySelectorAll('.ab-org-b').forEach(function (b) {
      b.addEventListener('click', function () {
        var i = Number(b.getAttribute('data-i'));
        orgSel = orgSel === i ? null : i;
        org();
      });
    });
    detalle();
  }
  function detalle() {
    var det = $('abOrgDet');
    if (orgSel === null) { det.hidden = true; det.innerHTML = ''; return; }
    var u = D.org[orgSel];
    var av = MED.avance.val(u), cb = MED.cambio.val(u), peso = u.aprobado / D.tot.aprobado * 100;
    det.hidden = false;
    det.innerHTML = '<p class="ab-org-dt">' + esc(u.n) + '</p><dl class="ab-org-dl">' +
      '<div><dt>Aprobado 2026</dt><dd><b class="ab-num">' + mdp(u.aprobado) + '</b> ' + chip('oficial') + '</dd></div>' +
      '<div><dt>Modificado 2026</dt><dd><b class="ab-num">' + mdp(u.modificado) + '</b> ' + chip('oficial') + '</dd></div>' +
      '<div><dt>Pagado al 30 de junio</dt><dd><b class="ab-num">' + mdp(u.pagado) + '</b> ' + chip('oficial') + '</dd></div>' +
      '<div><dt>Proyecto 2027</dt><dd><b class="ab-num">' + mdp(u.proyecto2027) + '</b> ' + chip('oficial') + '</dd></div>' +
      '<div><dt>Avance del pago</dt><dd><b class="ab-num">' + pct(av) + '</b> ' + chip('derivado') + '<small>pagado ÷ modificado × 100</small></dd></div>' +
      '<div><dt>Cambio 2027</dt><dd><b class="ab-num">' + MED.cambio.fmt(cb) + '</b> ' + chip('derivado') + '<small>(proyecto ÷ aprobado − 1) × 100</small></dd></div>' +
      '<div><dt>Peso en el ramo</dt><dd><b class="ab-num">' + pct(peso) + '</b> ' + chip('derivado') + '<small>aprobado del órgano ÷ aprobado del Ramo ' + esc(D.ramo) + ' × 100</small></dd></div>' +
      '</dl><button type="button" class="ab-boton ab-sec" id="abOrgCerrar">Cerrar</button>';
    $('abOrgCerrar').addEventListener('click', function () { orgSel = null; org(); });
  }
  if ($('abOrg')) {
    document.querySelectorAll('.ab-med .ab-op').forEach(function (b) {
      b.addEventListener('click', function () { pref.med = b.getAttribute('data-med'); guardar(); org(); });
    });
    org();
  }

  /* CSV del presupuesto, armado en el navegador */
  if ($('abCsv')) {
    $('abCsv').addEventListener('click', function () {
      var c = function (v) { return '"' + String(v).replace(/"/g, '""') + '"'; };
      var filas = [['Unidad responsable', 'Órgano', 'Aprobado 2026 (pesos)', 'Modificado 2026 (pesos)', 'Pagado al 30-jun-2026 (pesos)', 'Proyecto 2027 (pesos)',
        'Avance del pago % (derivado: pagado / modificado x 100)', 'Cambio 2027 % (derivado: (proyecto / aprobado - 1) x 100)']];
      D.org.forEach(function (u) {
        filas.push([u.ur, u.n, u.aprobado, u.modificado, u.pagado, u.proyecto2027,
          MED.avance.val(u).toFixed(2), MED.cambio.val(u).toFixed(2)]);
      });
      filas.push(['', 'Total del Ramo ' + D.ramo, D.tot.aprobado, D.tot.modificado, D.tot.pagado, D.tot.proyecto2027,
        (D.tot.pagado / D.tot.modificado * 100).toFixed(2), ((D.tot.proyecto2027 / D.tot.aprobado - 1) * 100).toFixed(2)]);
      filas.push([]);
      Object.keys(D.fu).forEach(function (k) { filas.push(['Fuente', D.fu[k].doc, D.fu[k].url]); });
      var txt = '﻿' + filas.map(function (f) { return f.map(c).join(','); }).join('\r\n');
      var a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([txt], { type: 'text/csv;charset=utf-8' }));
      a.download = 'auditavision-ramo-' + D.ramo + '-ambiente-2026-2027.csv';
      document.body.appendChild(a);
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
    });
  }

  /* 7. Filtros: leyes por tema, quién lo mide por estado */
  function filtro(sel, attr, items, campo) {
    var grupo = document.querySelector(sel);
    if (!grupo) return;
    grupo.querySelectorAll('.ab-op').forEach(function (b) {
      b.addEventListener('click', function () {
        var v = b.getAttribute(attr);
        pulsar(grupo, b);
        document.querySelectorAll(items).forEach(function (li) {
          li.hidden = !(v === 'todas' || v === 'todo' || li.getAttribute(campo) === v);
        });
      });
    });
  }
  filtro('#abLeyes .ab-grupo', 'data-tema', '#abLeyesL .ab-ley', 'data-tema');
  filtro('#abQuien .ab-grupo', 'data-q', '#abQuienL .ab-q', 'data-est');

  /* Copiar la huella SHA-256 completa */
  document.querySelectorAll('.ab-sha').forEach(function (b) {
    b.addEventListener('click', function () {
      var sha = b.getAttribute('data-sha'), aviso = $('abCopiado');
      var ok = function () { aviso.textContent = '✅ Huella copiada: ' + sha; };
      var no = function () { aviso.textContent = 'Huella completa: ' + sha; };
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(sha).then(ok, no);
        else no();
      } catch (e) { no(); }
    });
  });
})();
