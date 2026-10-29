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

  /* 8. Mapa ambiental de megaobras e infraestructura por estado (26-10-2026) */
  var mapaCaja = $('abMapaObras');
  if (mapaCaja && D.mapaObras) {
    var edos = D.mapaObras.edos || [];
    var obrasM = D.mapaObras.obras || [];
    var edosIdx = {};
    var normClave = function (s) {
      return String(s || '').trim().toUpperCase()
        .replace(/Á/g, 'A').replace(/É/g, 'E').replace(/Í/g, 'I').replace(/Ó/g, 'O').replace(/Ú/g, 'U');
    };
    var claveReal = {};
    edos.forEach(function (e) {
      edosIdx[e.a] = e;
      claveReal[normClave(e.a)] = e.a;
      claveReal[normClave(e.n)] = e.a;
    });

    var lenteM = 'obras';
    var tipoM = 'todas';
    /* ¿Quién paga? (Bloque 4, 27-10-2026): gasto público o inversión privada. */
    var pagaM = 'todas';
    var edoSel = 'TAB';

    try {
      var params = new URLSearchParams(window.location.search || '');
      var qEdo = params.get('e') || params.get('estado') || '';
      if (!qEdo && window.location.hash && window.location.hash.indexOf('#e-') === 0) {
        qEdo = decodeURIComponent(window.location.hash.slice(3));
      }
      if (qEdo && claveReal[normClave(qEdo)]) {
        edoSel = claveReal[normClave(qEdo)];
      }
      var qTipo = (params.get('tipo') || '').toLowerCase();
      if (['todas', 'trenes', 'energia', 'aeropuertos', 'agua'].indexOf(qTipo) >= 0) {
        tipoM = qTipo;
      }
      var qPaga = (params.get('paga') || '').toLowerCase();
      if (['todas', 'publico', 'privado'].indexOf(qPaga) >= 0) {
        pagaM = qPaga;
      }
      var qLente = (params.get('lente') || '').toLowerCase();
      if (['obras', 'gasto', 'asf'].indexOf(qLente) >= 0) {
        lenteM = qLente;
      }
    } catch (e) { /* sin URLSearchParams */ }

    function chipPend(e, pend) {
      if (e === 'pendiente' && pend) {
        return '<a class="est-chip est-pendiente" href="pendientes.html#' + esc(pend) + '" data-pend="' + esc(pend) + '">pendiente</a>';
      }
      return chip(e || 'oficial');
    }

    function obrasFiltradas() {
      return obrasM.filter(function (o) {
        return (tipoM === 'todas' || o.tipo === tipoM) && (pagaM === 'todas' || o.paga === pagaM);
      });
    }

    function obrasDeEstado(a, soloFiltro) {
      var lista = soloFiltro ? obrasFiltradas() : obrasM;
      return lista.filter(function (o) { return o.edos.indexOf(a) >= 0; });
    }

    function colorCuartil(v, cortes, paleta) {
      if (!v || v <= 0) return paleta[0];
      if (v <= cortes[0]) return paleta[1];
      if (v <= cortes[1]) return paleta[2];
      if (v <= cortes[2]) return paleta[3];
      return paleta[4];
    }

    function cuartiles(vals) {
      var s = vals.filter(function (x) { return x > 0; }).slice().sort(function (a, b) { return a - b; });
      if (!s.length) return [1, 2, 3];
      var q = function (p) { return s[Math.min(s.length - 1, Math.floor(s.length * p))]; };
      return [q(0.25), q(0.5), q(0.75)];
    }

    var cortesGasto = cuartiles(edos.map(function (e) { return e.gasto; }));
    var cortesAsf = cuartiles(edos.map(function (e) { return e.asf; }));
    var palObras = ['#e7efe9', '#8fd1ae', '#2e8b57', '#0f3d2a', '#082619'];
    var palGasto = ['#e7efe9', '#b8dfc8', '#68b688', '#237a4b', '#0f3d2a'];
    var palAsf = ['#e8f5ec', '#fde6b8', '#f4a261', '#e0533c', '#9e1b14'];

    function pintarMapa() {
      var ofil = obrasFiltradas();
      var edosFil = {};
      ofil.forEach(function (o) {
        o.edos.forEach(function (a) { edosFil[a] = (edosFil[a] || 0) + 1; });
      });
      var numEdos = Object.keys(edosFil).length;
      /* Solo el gasto público se suma: la inversión privada no es dinero público. */
      var sumInv = ofil.reduce(function (ac, o) { return ac + (o.paga === 'publico' ? (o.realMdp || 0) : 0); }, 0);
      var nPriv = ofil.filter(function (o) { return o.paga === 'privado'; }).length;
      var sumAsf = ofil.reduce(function (ac, o) { return ac + (o.asfMdp || 0); }, 0);

      if ($('abKpiEdos')) $('abKpiEdos').textContent = numEdos + ' de 32';
      if ($('abKpiInv')) $('abKpiInv').textContent = '$' + n(sumInv, 1) + ' mdp';
      if ($('abKpiAsf')) $('abKpiAsf').textContent = '$' + n(sumAsf, 1) + ' mdp';
      if ($('abKpiInvNota')) $('abKpiInvNota').textContent = 'Suma nacional de cada obra, sin prorratear entre estados. ' +
        (nPriv ? 'No suma ' + (nPriv === 1 ? 'el proyecto' : 'los ' + nPriv + ' proyectos') + ' de inversión privada del filtro: no es dinero público.' : 'La inversión privada no se suma: no es dinero público.');

      mapaCaja.querySelectorAll('.ab-mapa-lentes .ab-op').forEach(function (b) {
        b.setAttribute('aria-pressed', b.getAttribute('data-lente') === lenteM ? 'true' : 'false');
      });
      mapaCaja.querySelectorAll('.ab-mapa-tipos .ab-op').forEach(function (b) {
        b.setAttribute('aria-pressed', b.getAttribute('data-tipo') === tipoM ? 'true' : 'false');
      });
      mapaCaja.querySelectorAll('.ab-mapa-paga .ab-op').forEach(function (b) {
        b.setAttribute('aria-pressed', b.getAttribute('data-paga') === pagaM ? 'true' : 'false');
      });

      mapaCaja.querySelectorAll('.tt-edo').forEach(function (p) {
        var a = p.getAttribute('data-a');
        var e = edosIdx[a];
        var cnt = edosFil[a] || 0;
        var fill = palObras[0];
        if (lenteM === 'obras') {
          fill = cnt === 0 ? palObras[0] : (cnt === 1 ? palObras[1] : (cnt === 2 ? palObras[2] : palObras[3]));
        } else if (lenteM === 'gasto' && e) {
          fill = colorCuartil(e.gasto, cortesGasto, palGasto);
        } else if (lenteM === 'asf' && e) {
          fill = colorCuartil(e.asf, cortesAsf, palAsf);
        }
        p.style.fill = fill;
        p.classList.toggle('sel', a === edoSel);
        p.classList.toggle('ab-con-obra', cnt > 0);
      });

      var ley = $('abMapaLeyenda');
      if (ley) {
        if (lenteM === 'obras') {
          ley.innerHTML =
            '<span class="ab-ley-item"><i style="background:' + palObras[0] + '"></i> Sin obras en este filtro</span>' +
            '<span class="ab-ley-item"><i style="background:' + palObras[1] + '"></i> 1 megaobra o caso</span>' +
            '<span class="ab-ley-item"><i style="background:' + palObras[2] + '"></i> 2 obras o casos</span>' +
            '<span class="ab-ley-item"><i style="background:' + palObras[3] + '"></i> 3 o más obras</span>';
        } else if (lenteM === 'gasto') {
          ley.innerHTML =
            '<span class="ab-ley-item"><i style="background:' + palGasto[1] + '"></i> Hasta $' + n(cortesGasto[0], 0) + ' mdp</span>' +
            '<span class="ab-ley-item"><i style="background:' + palGasto[2] + '"></i> Hasta $' + n(cortesGasto[1], 0) + ' mdp</span>' +
            '<span class="ab-ley-item"><i style="background:' + palGasto[3] + '"></i> Hasta $' + n(cortesGasto[2], 0) + ' mdp</span>' +
            '<span class="ab-ley-item"><i style="background:' + palGasto[4] + '"></i> Más de $' + n(cortesGasto[2], 0) + ' mdp ' + chip('derivado') + '</span>';
        } else {
          ley.innerHTML =
            '<span class="ab-ley-item"><i style="background:' + palAsf[0] + '"></i> $0 mdp por aclarar</span>' +
            '<span class="ab-ley-item"><i style="background:' + palAsf[1] + '"></i> Hasta $' + n(cortesAsf[0], 0) + ' mdp</span>' +
            '<span class="ab-ley-item"><i style="background:' + palAsf[2] + '"></i> Hasta $' + n(cortesAsf[1], 0) + ' mdp</span>' +
            '<span class="ab-ley-item"><i style="background:' + palAsf[4] + '"></i> Más de $' + n(cortesAsf[1], 0) + ' mdp ' + chip('oficial') + '</span>';
        }
      }

      if ($('abMapaSel')) $('abMapaSel').value = edoSel;
      mapaCaja.querySelectorAll('.ab-edo-btn').forEach(function (b) {
        var a = b.getAttribute('data-edo');
        var cnt = edosFil[a] || 0;
        b.classList.toggle('ab-act', a === edoSel);
        b.setAttribute('aria-pressed', a === edoSel ? 'true' : 'false');
        b.classList.toggle('ab-edo-atenuado', cnt === 0);
      });

      pintarFicha();
    }

    function pintarFicha() {
      var ficha = $('abMapaFicha');
      var e = edosIdx[edoSel];
      if (!ficha || !e) return;
      var obrasFil = obrasDeEstado(edoSel, true);
      var obrasTot = obrasDeEstado(edoSel, false);
      var listaMostrar = obrasFil.length ? obrasFil : obrasTot;

      var notaFiltro = '';
      if (tipoM !== 'todas' && obrasFil.length === 0 && obrasTot.length > 0) {
        notaFiltro = '<p class="ab-ficha-aviso">En el filtro actual no hay obras para ' + esc(e.n) +
          ', pero el estado tiene <b>' + obrasTot.length + '</b> en otros rubros (mostradas abajo).</p>';
      }

      var tarjetasObra = '';
      if (listaMostrar.length > 0) {
        tarjetasObra = listaMostrar.map(function (o) {
          var multiTxt = o.multi
            ? '<p class="ab-ficha-multi"><span aria-hidden="true">🧭</span> <b>Obra multiestatal (' + esc(o.edos.join(', ')) + '):</b> la inversión mostrada es el total nacional de la obra; Hacienda no publica cuánto se ejerció dentro de cada estado.</p>'
            : '';
          var paga = o.paga === 'privado'
            ? '<p class="ab-ficha-paga ab-ficha-privado"><span aria-hidden="true">🏢</span> <b>Inversión privada.</b> ' + esc((o.pagaTxt || '').replace(/^Inversión privada: /, '')) + '</p>'
            : '<p class="ab-ficha-paga"><span aria-hidden="true">🏛️</span> <b>Gasto público.</b> ' + esc((o.pagaTxt || '').replace(/^Gasto público: /, '')) + '</p>';
          var costoFila = o.paga === 'privado'
            ? '<div><dt>Inversión</dt><dd>' + chipPend(o.estReal, o.pendReal) + ' <small>Privada: no se suma al gasto público del mapa</small></dd></div>'
            : o.realMdp != null
            ? '<div><dt>Inversión registrada</dt><dd><b class="ab-num">$' + n(o.realMdp, 1) + ' mdp</b> ' + chipPend(o.estReal, o.pendReal) +
              (o.sobrePct != null ? ' · <small>Sobrecosto: <b class="ab-num">' + (o.sobrePct >= 0 ? '+' : '') + n(o.sobrePct, 1) + ' %</b> ' + chip('derivado') + '</small>' : '') + '</dd></div>'
            : '<div><dt>Inversión y presupuesto</dt><dd>' + chipPend(o.estReal, o.pendReal) + ' <small>En revisión documental</small></dd></div>';

          return '<article class="ab-ficha-obra">' +
            '<header class="ab-ficha-ocab">' +
              '<span class="ab-ficha-oico" aria-hidden="true">' + esc(o.ico) + '</span>' +
              '<div><h4 class="ab-ficha-otit">' + esc(o.nombre) + '</h4>' +
              '<p class="ab-ficha-osede">' + esc(o.sede) + ' · <span class="ab-ficha-tag">' + esc(o.tipoNom) + '</span></p></div>' +
            '</header>' +
            paga +
            multiTxt +
            '<dl class="ab-ficha-odl">' +
              costoFila +
              '<div><dt>Fiscalización ASF / Daños</dt><dd>' + esc(o.asfTxt) + (o.asfMdp > 0 ? ' ' + chip(o.asfEst || 'oficial') : '') + '</dd></div>' +
              '<div class="ab-ficha-alerta"><dt><span aria-hidden="true">🚨</span> Alerta del Auditor Ambiental</dt>' +
                '<dd><b>Ecosistema:</b> ' + esc(o.ecosistema) + '.<br>' + esc(o.alerta) + '</dd></div>' +
              '<div><dt>Permiso ambiental (MIA / ASEA)</dt><dd>' + chipPend(o.miaEst, o.miaPend) + ' <small>' + esc(o.miaTxt) + '</small></dd></div>' +
            '</dl>' +
            '<div class="ab-ficha-olks">' +
              '<a class="ab-ficha-lk" href="' + esc(o.aud) + '"><span aria-hidden="true">🖼️</span> Auditoría en imágenes</a>' +
              '<a class="ab-ficha-lk" href="' + esc(o.ficha) + '"><span aria-hidden="true">🏭</span> Ficha y simulador</a>' +
              '<a class="ab-ficha-lk" href="' + esc(o.exp) + '"><span aria-hidden="true">📂</span> ' + esc(o.expNom) + '</a>' +
            '</div>' +
          '</article>';
        }).join('');
      } else {
        tarjetasObra = '<div class="ab-ficha-sin">' +
          '<p><b>Sin megaobras federales en este padrón para ' + esc(e.n) + '.</b></p>' +
          '<p>Las 14 megaobras físicas, refinerías y casos ambientales críticos del padrón se concentran en 15 entidades. Aquí puedes consultar el gasto federalizado que recibe ' + esc(e.n) + ' y lo que la ASF observó en su Cuenta Pública 2024.</p>' +
        '</div>';
      }

      ficha.innerHTML =
        '<div class="ab-ficha-cab">' +
          '<div><p class="ab-ficha-kicker">Ficha del Auditor Ambiental por Estado</p>' +
          '<h3 class="ab-ficha-tit"><span aria-hidden="true">📍</span> ' + esc(e.n) + ' <small>(' + esc(e.a) + ')</small></h3></div>' +
          '<span class="ab-ficha-badge">' + (obrasTot.length ? obrasTot.length + (obrasTot.length === 1 ? ' obra o alerta' : ' obras y alertas') : 'Gasto estatal') + '</span>' +
        '</div>' +
        '<dl class="ab-ficha-est">' +
          '<div><dt>Gasto federalizado 2026 (Ramos 28 y 33)</dt>' +
            '<dd><b class="ab-num">$' + n(e.gasto, 1) + ' mdp</b> ' + chip('derivado') +
            '<small>Ramo 28: $' + n(e.r28, 1) + ' mdp · Ramo 33: $' + n(e.r33, 1) + ' mdp · $' + n(e.pc, 0) + ' por habitante</small></dd></div>' +
          '<div><dt>Por aclarar ante la ASF en el estado (CP 2024)</dt>' +
            '<dd><b class="ab-num">$' + n(e.asf, 1) + ' mdp</b> ' + chip('oficial') +
            '<small>En ' + n(e.aud, 0) + ' auditorías al gasto federalizado · Deuda estatal: $' + n(e.deuda, 1) + ' mdp (semáforo ' + esc(e.sem) + ')</small></dd></div>' +
        '</dl>' +
        notaFiltro +
        '<div class="ab-ficha-obras">' + tarjetasObra + '</div>' +
        '<div class="ab-ficha-pie">' +
          '<a class="ab-ficha-lk" href="herramienta-inspector-entes.html#ente=edo-' + esc(e.a) + '"><span aria-hidden="true">🧾</span> Estado de cuenta de ' + esc(e.n) + '</a>' +
          '<a class="ab-ficha-lk" href="numeros-mapa-del-gasto-federalizado.html?e=' + esc(e.a) + '"><span aria-hidden="true">🗺️</span> Mapa del gasto federalizado</a>' +
          '<a class="ab-ficha-lk" href="herramienta-ambiente-auditor.html"><span aria-hidden="true">🌱</span> Auditar sector ambiental</a>' +
        '</div>';
    }

    mapaCaja.querySelectorAll('.ab-mapa-lentes .ab-op').forEach(function (b) {
      b.addEventListener('click', function () {
        lenteM = b.getAttribute('data-lente');
        pintarMapa();
      });
    });

    mapaCaja.querySelectorAll('.ab-mapa-paga .ab-op').forEach(function (b) {
      b.addEventListener('click', function () {
        pagaM = b.getAttribute('data-paga');
        var ofil = obrasFiltradas();
        if (ofil.length && !ofil.some(function (o) { return o.edos.indexOf(edoSel) >= 0; })) edoSel = ofil[0].edos[0];
        pintarMapa();
      });
    });

    mapaCaja.querySelectorAll('.ab-mapa-tipos .ab-op').forEach(function (b) {
      b.addEventListener('click', function () {
        tipoM = b.getAttribute('data-tipo');
        var ofil = obrasFiltradas();
        var tieneEnFiltro = ofil.some(function (o) { return o.edos.indexOf(edoSel) >= 0; });
        if (!tieneEnFiltro && ofil.length > 0) {
          edoSel = ofil[0].edos[0];
        }
        pintarMapa();
      });
    });

    mapaCaja.querySelectorAll('.tt-edo').forEach(function (p) {
      var elegir = function () {
        edoSel = p.getAttribute('data-a');
        pintarMapa();
      };
      p.addEventListener('click', elegir);
      p.addEventListener('keydown', function (ev) {
        if (ev.key === 'Enter' || ev.key === ' ') {
          ev.preventDefault();
          elegir();
        }
      });
    });

    if ($('abMapaSel')) {
      $('abMapaSel').addEventListener('change', function () {
        edoSel = $('abMapaSel').value;
        pintarMapa();
      });
    }

    mapaCaja.querySelectorAll('.ab-edo-btn').forEach(function (b) {
      b.addEventListener('click', function () {
        edoSel = b.getAttribute('data-edo');
        pintarMapa();
        var f = $('abMapaFicha');
        if (f && f.scrollIntoView && !quieto && window.innerWidth < 960) {
          f.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      });
    });

    pintarMapa();
  }
})();
