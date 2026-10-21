/* Auditavisión · Inversión y Megaobras › De cero al resultado (módulo 4,
   13-10-2026). La página la escribe herramientas/mo_cero.py con las tres
   mesas ya calculadas y, en JSON (#mcDatos), las mismas obras con su chip
   y su documento: aquí no se escribe ninguna cifra nueva, solo se vuelve a
   sumar cuando el lector recorta por industria o mandato.
   Hace cuatro cosas: recorrer cada mesa renglón por renglón (con la
   operación de cada renglón a la vista), decir de qué documento sale cada
   número al pulsar una obra, rehacer la cuenta en otro orden y descargar
   cada mesa en CSV. Sin el motor. Desde el 21-10-2026 no hay filtro de
   industria ni de mandato (el único de la herramienta está en Sector e
   industria) y la mesa 2 usa la medida única de ganancia o pérdida
   (res: + gana, − pierde; perd = −res). Preferencias en localStorage
   (av-mo-cero). */
(function () {
  'use strict';

  var D;
  try { D = JSON.parse(document.getElementById('mcDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  var raiz = $('mcRaiz');
  if (!raiz) return;

  var CLAVE = 'av-mo-cero';
  var porId = {};
  D.obras.forEach(function (o) { porId[o.id] = o; });
  var pendObra = {};
  D.pendObra.forEach(function (id) { pendObra[id] = true; });
  var ORDENES = {
    perdida: function (a, b) {
      /* Las que no publican su resultado o no operan, al final. */
      if ((a.res == null) !== (b.res == null)) return a.res == null ? 1 : -1;
      return b.perd - a.perd;
    },
    sobrecosto: function (a, b) { return b.sob - a.sob; },
    inversion: function (a, b) { return b.real - a.real; },
    brecha: function (a, b) { return (b.real - b.presu) - (a.real - a.presu); },
    cronologia: function (a, b) { return String(a.per).localeCompare(String(b.per)); }
  };
  var DEF = { orden: 'perdida' };
  var est = leer();
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function leer() {
    var o = {};
    try { o = JSON.parse(localStorage.getItem(CLAVE) || '{}') || {}; } catch (e) { o = {}; }
    return { orden: ORDENES[o.orden] ? o.orden : DEF.orden };
  }
  function guardar() { try { localStorage.setItem(CLAVE, JSON.stringify(est)); } catch (e) { /* sin almacenamiento */ } }

  /* ---------- Formato: el mismo de la página escrita en Python ---------- */
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function fnum(n) { return Number(n).toLocaleString('es-MX'); }
  function smdp(n) {
    var a = Math.abs(n);
    if (a >= 1000000) return '$' + (n / 1000000).toFixed(2) + ' billones';
    if (a >= 1000) return '$' + fnum(Math.round(n / 100) / 10) + ' mil millones';
    return '$' + fnum(Math.round(n * 100) / 100) + ' millones';
  }
  function pesos(v) { return '$' + fnum(Math.round(v)); }
  function sg(x) { return x > 0 ? '+' : ''; }
  function chip(e, pend) {
    return '<span class="est-chip est-' + e + '"' + (pend ? ' data-pend="' + esc(pend) + '"' : '') + '>' + e + '</span>';
  }
  function chC(o, campo) {
    var e = (o.ec || {})[campo] || 'pendiente';
    return chip(e, e === 'pendiente' ? 'obra-' + o.id : null);
  }
  function pendDoc(o) { return !!pendObra[o.id]; }
  function corto(n) { return String(n).split(' (')[0]; }

  /* ---------- Las obras que entran ---------- */
  function filtradas() {
    return D.obras.slice().sort(ORDENES[est.orden]);
  }
  function ag(l) {
    var real = l.reduce(function (a, o) { return a + o.real; }, 0);
    var presu = l.reduce(function (a, o) { return a + o.presu; }, 0);
    var anual = l.reduce(function (a, o) { return a + o.perd; }, 0);
    return { n: l.length, real: real, presu: presu, brecha: real - presu,
      sob: presu > 0 ? (real / presu - 1) * 100 : 0, anual: anual, seg: anual * 1000000 / (365 * 86400) };
  }

  /* ---------- Las tres mesas ---------- */
  var vista = [], A = null, pasos = { 1: [], 2: [], 3: [] };

  function nom(o, mesa) {
    return '<button type="button" class="mc-lupa" data-id="' + esc(o.id) + '" data-mesa="' + mesa + '" aria-label="De dónde sale cada cifra de ' + esc(o.n) + '">' +
      '<span class="mc-ico" aria-hidden="true">' + o.ico + '</span><span class="mc-nom-tx">' + esc(o.n) + '</span>' +
      '<span class="mc-lupa-i" aria-hidden="true">🔎</span></button>';
  }

  function filas1(l) {
    var acum = 0;
    pasos[1] = [{ acum: 0 }];
    return l.map(function (o, k) {
      var i = k + 1, dif = o.real - o.presu, antes = acum;
      acum += dif;
      pasos[1].push({ id: o.id, dif: dif, antes: antes, acum: acum });
      return '<tr class="mc-fila" data-i="' + i + '" data-id="' + esc(o.id) + '"><td class="mc-n" data-et="#">' + i + '</td><td class="mc-nom">' + nom(o, 1) + '</td>' +
        '<td class="mc-num" data-et="Aprobado (mdp)" data-k="presu">' + fnum(o.presu) + ' ' + chC(o, 'inversion_presupuestada_mdp') + '</td>' +
        '<td class="mc-num" data-et="Erogado (mdp)" data-k="real">' + fnum(o.real) + ' ' + chC(o, 'inversion_real_mdp') + '</td>' +
        '<td class="mc-num mc-dif" data-et="Diferencia" data-k="dif">' + sg(dif) + fnum(dif) + (pendDoc(o) ? ' ' + chip('pendiente', 'obra-' + o.id) : '') + '</td>' +
        '<td class="mc-num mc-acum" data-et="Acumulado" data-k="acum">' + fnum(Math.round(acum)) + '</td></tr>';
    }).join('\n');
  }

  function celdaRes(o) {
    if (o.pe === 'pendiente') return 'no lo publica ' + chip('pendiente', 'cuenta-' + o.id);
    if (o.pe === 'no_aplica') return 'no opera';
    return '<span class="' + (o.res > 0 ? 'mc-gana' : 'mc-pierde') + '">' + sg(o.res) + fnum(o.res) + '</span> ' + chip(o.pe);
  }

  function filas2(l) {
    var acum = 0;
    pasos[2] = [{ acum: 0 }];
    return l.map(function (o, k) {
      var i = k + 1, antes = acum;
      acum += o.res || 0;
      pasos[2].push({ id: o.id, antes: antes, acum: acum });
      var nula = o.pe === 'pendiente' || o.pe === 'no_aplica';
      return '<tr class="mc-fila' + (nula ? ' mc-nula' : '') + '" data-i="' + i + '" data-id="' + esc(o.id) + '"><td class="mc-n" data-et="#">' + i + '</td><td class="mc-nom">' + nom(o, 2) + '</td>' +
        '<td class="mc-num" data-et="Año del dato" data-k="anio">' + (o.anio || '—') + '</td>' +
        '<td class="mc-num mc-dif" data-et="Gana o pierde (mdp)" data-k="res">' + celdaRes(o) + '</td>' +
        '<td class="mc-num mc-acum" data-et="Acumulado" data-k="acum">' + fnum(Math.round(acum * 10) / 10) + '</td></tr>';
    }).join('\n');
  }

  function filas3(a) {
    var pad = D.padron.n, bc = a.brecha * 1000000 / pad, pc = a.anual * 1000000 / pad;
    pasos[3] = [{ v: '$0' }, { v: smdp(a.brecha) }, { v: pesos(bc) }, { v: smdp(a.anual) }, { v: pesos(pc) }];
    return '<tr class="mc-fila" data-i="1"><td class="mc-n" data-et="Paso">1</td><td class="mc-nom">Pesos pagados de más sobre lo aprobado <small>(saldo de 2000 a 2024)</small></td>' +
        '<td class="mc-op" data-et="Operación">resultado de la mesa 1</td><td class="mc-num mc-acum" data-et="Resultado">' + smdp(a.brecha) + '</td></tr>\n' +
      '<tr class="mc-fila mc-div" data-i="2"><td class="mc-n" data-et="Paso">2</td><td class="mc-nom">Entre cada contribuyente con RFC activo</td>' +
        '<td class="mc-op" data-et="Operación">' + fnum(Math.round(a.brecha * 10) / 10) + ' mdp × 1,000,000 ÷ ' + fnum(pad) + '</td><td class="mc-num mc-acum" data-et="Resultado">' + pesos(bc) + ' <small>por contribuyente</small></td></tr>\n' +
      '<tr class="mc-fila" data-i="3"><td class="mc-n" data-et="Paso">3</td><td class="mc-nom">Pérdida neta de un año <small>(cada obra con su año más reciente publicado)</small></td>' +
        '<td class="mc-op" data-et="Operación">resultado de la mesa 2</td><td class="mc-num mc-acum" data-et="Resultado">' + smdp(a.anual) + '</td></tr>\n' +
      '<tr class="mc-fila mc-div" data-i="4"><td class="mc-n" data-et="Paso">4</td><td class="mc-nom">Entre cada contribuyente con RFC activo</td>' +
        '<td class="mc-op" data-et="Operación">' + fnum(Math.round(a.anual * 10) / 10) + ' mdp × 1,000,000 ÷ ' + fnum(pad) + '</td><td class="mc-num mc-acum" data-et="Resultado">' + pesos(pc) + ' <small>por contribuyente, cada año</small></td></tr>';
  }

  var CADENA = [['Un año', 1, 'cifra base'], ['Un semestre', 2, '÷ 2 semestres'], ['Un trimestre', 4, '÷ 4 trimestres'],
    ['Un mes', 12, '÷ 12 meses'], ['Un día', 365, '÷ 365 días'], ['Un segundo', 31536000, '÷ 31,536,000 segundos']];

  function cierre1(l, a) {
    var p = l.filter(pendDoc);
    var dp = p.reduce(function (s, o) { return s + (o.real - o.presu); }, 0);
    var t = 'Se aprobaron <strong>' + smdp(a.presu) + '</strong> y se erogaron <strong>' + smdp(a.real) + '</strong>. La diferencia es de <strong>' +
      smdp(a.brecha) + '</strong>, un <strong>' + sg(a.sob) + a.sob.toFixed(1) + '%</strong> sobre lo autorizado ' + chip('derivado') + '.';
    if (p.length) {
      t += ' <span class="mc-ojo">Ojo: <strong>' + smdp(dp) + '</strong> de esa diferencia salen de ' + p.length + (p.length === 1 ? ' obra' : ' obras') +
        ' con alguna cifra pendiente (' + esc(p.map(function (o) { return corto(o.n); }).join(', ')) + '). Cuentan en el inventario, no como dato auditado.</span>';
    } else {
      t += ' <span class="mc-ojo mc-ojo-ok">Todas las cifras de esta cuenta tienen documento.</span>';
    }
    return t;
  }

  function render() {
    vista = filtradas();
    A = ag(vista);
    /* La mesa 1 mide las obras; los rescates van aparte (decisión del
       autor, 17-10-2026). La mesa 2 sí suma los rescates. */
    var vista1 = vista.filter(function (o) { return !o.resc; });
    var A1 = ag(vista1);
    var A3 = { brecha: A1.brecha, anual: A.anual };
    var t1 = $('mcT1'), t2 = $('mcT2'), t3 = $('mcT3');
    var cero1 = t1.tBodies[0].rows[0] && t1.tBodies[0].rows[0].classList.contains('mc-cero') ? t1.tBodies[0].rows[0].outerHTML : '';
    var cero2 = t2.tBodies[0].rows[0] && t2.tBodies[0].rows[0].classList.contains('mc-cero') ? t2.tBodies[0].rows[0].outerHTML : '';
    var cero3 = t3.tBodies[0].rows[0] && t3.tBodies[0].rows[0].classList.contains('mc-cero') ? t3.tBodies[0].rows[0].outerHTML : '';
    render.ceros = render.ceros || [cero1, cero2, cero3];
    var c = render.ceros;
    t1.tBodies[0].innerHTML = c[0] + '\n' + filas1(vista1);
    $('mcPie1').innerHTML = '<tr><td></td><td class="mc-nom">Total de las obras</td><td class="mc-num" data-et="Aprobado (mdp)">' + fnum(A1.presu) +
      '</td><td class="mc-num" data-et="Erogado (mdp)">' + fnum(A1.real) + '</td><td class="mc-num mc-dif" data-et="Diferencia">' + sg(A1.brecha) + fnum(A1.brecha) +
      '</td><td class="mc-num mc-acum" data-et="Acumulado">' + fnum(A1.brecha) + '</td></tr>';
    $('mcCierre1').innerHTML = cierre1(vista1, A1);
    t2.tBodies[0].innerHTML = c[1] + '\n' + filas2(vista);
    var an = fnum(Math.round(-A.anual * 10) / 10);
    $('mcPie2').innerHTML = '<tr><td></td><td class="mc-nom">Ganancia o pérdida neta del año</td><td></td><td class="mc-num mc-dif" data-et="Gana o pierde (mdp)">' + an +
      '</td><td class="mc-num mc-acum" data-et="Acumulado">' + an + '</td></tr>';
    $('mcCadena').innerHTML = CADENA.map(function (x) {
      var v = A.anual / x[1];
      return '<li class="mc-cad-p"><span class="mc-cad-et">' + x[0] + '</span><span class="mc-cad-op">' + x[2] + '</span><span class="mc-cad-v">' +
        (v >= 1 ? smdp(v) : '$' + fnum(Math.round(v * 1000000)) + ' pesos') + '</span></li>';
    }).join('');
    $('mcSeg').textContent = '$' + A.seg.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    t3.tBodies[0].innerHTML = c[2] + '\n' + filas3(A3);
    var pad = D.padron.n;
    $('mcBolsillo').innerHTML =
      '<div class="mc-bol"><span class="mc-bol-et">Sobrecosto histórico por contribuyente</span><b class="mc-bol-v">' + pesos(A3.brecha * 1000000 / pad) + '</b>' +
        '<span class="mc-bol-sub">acumulado de 2000 a 2024 (inversión de capital en exceso) ' + chip('derivado') + '</span></div>' +
      '<div class="mc-bol mc-bol-alto"><span class="mc-bol-et">Conciliación temporal de cuentas</span><b class="mc-bol-v">No se suman</b>' +
        '<span class="mc-bol-sub">un sobrecosto de varias décadas no se suma a un flujo de un año</span></div>' +
      '<div class="mc-bol"><span class="mc-bol-et">Pérdida neta anual por contribuyente</span><b class="mc-bol-v">' + pesos(A.anual * 1000000 / pad) + '</b>' +
        '<span class="mc-bol-sub">cada año (el resultado publicado más reciente de cada obra) ' + chip('derivado') + '</span></div>';
    [1, 2, 3].forEach(function (m) { st[m] = total(m); pintar(m); });
    vivoReinicia();
  }

  /* Lee los pasos de la página escrita en Python, sin volver a pintarla. */
  function leerPasos() {
    vista = filtradas();
    A = ag(vista);
    filas1(vista); filas2(vista); filas3(A);
  }

  /* ---------- Renglón por renglón ---------- */
  var st = { 1: 0, 2: 0, 3: 0 }, auto = { 1: null, 2: null, 3: null };
  function total(m) { return pasos[m].length - 1; }

  function pintar(m) {
    var t = $('mcT' + m), i = st[m], n = total(m);
    [].forEach.call(t.tBodies[0].rows, function (r) {
      var k = Number(r.getAttribute('data-i'));
      r.classList.toggle('mc-oculta', !isNaN(k) && k > i);
      r.classList.toggle('mc-actual', !isNaN(k) && k === i && i < n);
      r.classList.remove('mc-sel');
    });
    limpiaFuentes(t);
    var fin = i >= n;
    if (t.tFoot) t.tFoot.classList.toggle('mc-oculta', !fin);
    var cierre = m === 1 ? $('mcCierre1') : m === 2 ? $('mcCadena') : $('mcBolsillo');
    if (cierre) cierre.classList.toggle('mc-oculta', !fin);
    var p = pasos[m][i] || pasos[m][0];
    $('mcMarc' + m).textContent = m === 3 ? p.v : (m === 1 ? fnum(Math.round(p.acum)) : fnum(Math.round(p.acum * 10) / 10)) + ' mdp';
    $('mcPaso' + m).textContent = n === 0 ? 'Sin renglones' : (fin ? 'Cuenta completa · ' + n + ' de ' + n : 'Renglón ' + i + ' de ' + n);
    $('mcRiel' + m).style.width = (n ? (i / n) * 100 : 0) + '%';
    var bSig = raiz.querySelector('.mc-b[data-acc="sig"][data-mesa="' + m + '"]');
    if (bSig) bSig.innerHTML = fin && n ? '<span aria-hidden="true">↺</span> Recórrela desde cero' : '<span aria-hidden="true">▶</span> Siguiente renglón';
    if (bSig) bSig.disabled = n === 0;
    if (fin && auto[m]) para(m);
    if (i > 0 && !fin) {
      var fila = t.tBodies[0].querySelector('tr[data-i="' + i + '"]');
      if (fila) { fila.classList.add('mc-sel'); resalta(m, i); }
      explica(m, i);
    } else if (fin) {
      $('mcExp' + m).innerHTML = n ? finTexto(m) : '';
    } else {
      $('mcExp' + m).innerHTML = '<b>Renglón 0 · Punto de partida.</b> Todo arranca en cero. Pulsa «Siguiente renglón» y mira cómo cada obra mueve el acumulado.';
    }
  }

  function finTexto(m) {
    if (m === 1) return '<b>Cuenta completa.</b> La última celda del acumulado, <b>' + fnum(A.brecha) + ' mdp</b>, es el sobrecosto del conjunto: erogado total (' + fnum(A.real) + ') menos aprobado total (' + fnum(A.presu) + '). Pulsa una obra para ver su documento.';
    if (m === 2) return '<b>Cuenta completa.</b> Solo entran las obras que publican su resultado: lo que pierden menos lo que ganan da una pérdida neta de <b>' + fnum(Math.round(A.anual * 10) / 10) + ' mdp</b> al año. Abajo, la misma cifra partida en el tiempo.';
    return '<b>Cuenta completa.</b> Dos divisiones separadas, con el mismo divisor oficial. No se suman: una es un saldo de décadas y la otra el flujo de un año.';
  }

  function limpiaFuentes(t) {
    [].forEach.call(t.querySelectorAll('.mc-fuente, .mc-res'), function (c) { c.classList.remove('mc-fuente', 'mc-res'); });
  }
  function celda(t, i, k) {
    var r = t.tBodies[0].querySelector('tr[data-i="' + i + '"]');
    return r ? (k ? r.querySelector('[data-k="' + k + '"]') : r.querySelector('.mc-acum')) : null;
  }
  function marca(c, cls) { if (c) c.classList.add(cls); }

  /* Resalta de dónde sale el número del renglón i: las celdas que entran
     en la operación y la celda que resulta. */
  function resalta(m, i) {
    var t = $('mcT' + m);
    limpiaFuentes(t);
    if (m === 1) { marca(celda(t, i, 'presu'), 'mc-fuente'); marca(celda(t, i, 'real'), 'mc-fuente'); marca(celda(t, i, 'dif'), 'mc-fuente'); marca(celda(t, i - 1), 'mc-fuente'); marca(celda(t, i, 'acum'), 'mc-res'); }
    else if (m === 2) { marca(celda(t, i, 'anio'), 'mc-fuente'); marca(celda(t, i, 'res'), 'mc-fuente'); marca(celda(t, i - 1), 'mc-fuente'); marca(celda(t, i, 'acum'), 'mc-res'); }
    else {
      if (i === 2 || i === 4) marca(celda(t, i - 1), 'mc-fuente');
      marca(celda(t, i), 'mc-res');
    }
  }

  function fuentesHtml(o) {
    var f = (o.fu || []).map(function (x) { return '<li><a href="' + esc(x.u) + '" target="_blank" rel="noopener noreferrer">' + esc(x.d) + ' ↗</a></li>'; }).join('');
    return f ? '<p class="mc-exp-t">Documentos cotejados de esta obra</p><ul class="mc-exp-fu">' + f + '</ul>' : '';
  }
  function defsHtml(o, campos) {
    var et = { inversion_presupuestada_mdp: 'Aprobado', inversion_real_mdp: 'Erogado', sobrecosto_pct: 'Sobrecosto' };
    return campos.map(function (k) {
      var e = (o.ec || {})[k] || 'pendiente';
      var d = (o.defs || {})[k] || (e === 'pendiente' ? 'Cifra del registro sin documento oficial localizado todavía.' : '');
      return d ? '<li><b>' + et[k] + '</b> ' + chC(o, k) + ' ' + esc(d) + '</li>' : '';
    }).join('');
  }

  function explica(m, i) {
    var box = $('mcExp' + m), p = pasos[m][i];
    if (m === 3) {
      var a = A, pad = fnum(D.padron.n);
      var tx = {
        1: 'Se toma el resultado de la mesa 1: <b>' + smdp(a.brecha) + '</b> pagados de más sobre lo aprobado. Es un saldo: se acumuló a lo largo de décadas.',
        2: 'Ese saldo, en pesos (' + fnum(Math.round(a.brecha * 10) / 10) + ' mdp × 1,000,000), entre <b>' + pad + '</b> contribuyentes con RFC activo = <b>' + pasos[3][2].v + '</b> por contribuyente ' + chip('derivado') + '.',
        3: 'Aparte, el resultado de la mesa 2: <b>' + smdp(a.anual) + '</b> de pérdida neta en un año. Es un flujo: se repite cada año mientras las obras operen igual.',
        4: 'Ese flujo, en pesos, entre los mismos <b>' + pad + '</b> contribuyentes = <b>' + pasos[3][4].v + '</b> por contribuyente, cada año ' + chip('derivado') + '.'
      };
      box.innerHTML = '<b>Paso ' + i + '.</b> ' + tx[i];
      return;
    }
    var o = porId[p.id];
    box.innerHTML = '<b>Renglón ' + i + ' · ' + esc(o.n) + '.</b> ' + (m === 1 ? op1(o, p) : op2(o, p));
  }

  function op1(o, p) {
    return 'Erogado ' + fnum(o.real) + ' − aprobado ' + fnum(o.presu) + ' = <b>' + sg(p.dif) + fnum(p.dif) + ' mdp</b>. ' +
      'Acumulado: ' + fnum(Math.round(p.antes)) + ' ' + (p.dif < 0 ? '−' : '+') + ' ' + fnum(Math.abs(p.dif)) + ' = <b>' + fnum(Math.round(p.acum)) + ' mdp</b>.' +
      (pendDoc(o) ? ' ' + chip('pendiente', 'obra-' + o.id) + ' Esta obra trae al menos una cifra sin documento: cuenta en el inventario, no como dato auditado.' : '');
  }

  function op2(o, p) {
    var acum = ' El acumulado queda en <b>' + fnum(Math.round(p.acum * 10) / 10) + ' mdp</b>.';
    var doc = o.op && o.op.u ? ' Documento: <a href="' + esc(o.op.u) + '" target="_blank" rel="noopener noreferrer">' + esc(o.op.d) + ' ↗</a>.' : '';
    if (o.pe === 'pendiente') return chip('pendiente', 'cuenta-' + o.id) + ' No publica su ganancia o pérdida del año: ' + esc(o.por) + ' No se estima: no entra en la suma.' + acum;
    if (o.pe === 'no_aplica') return 'No aplica: ' + esc(o.por) + ' No entra en la suma.' + acum;
    return (o.res > 0 ? '<b>Gana ' : '<b>Pierde ') + fnum(Math.abs(o.res)) + ' mdp</b> en ' + o.anio + ' ' + chip(o.pe) + ', ' +
      (o.base === 'sin_apoyo' ? 'antes del apoyo del presupuesto' : 'resultado del ejercicio publicado') + '. ' + esc(o.opx) + acum + doc;
  }

  /* La lupa: todo lo que se sabe de una obra, con su documento. */
  function lupa(id, mesa) {
    var o = porId[id];
    if (!o) return;
    var box = $('mcExp' + mesa);
    if (mesa === 'inv') {
      var t = raiz.querySelector('.mc-t-sec');
      [].forEach.call(t.querySelectorAll('tr.mc-sel'), function (r) { r.classList.remove('mc-sel'); });
      var r = t.querySelector('tr[data-id="' + id + '"]');
      if (r) r.classList.add('mc-sel');
      var sec = D.sectores[o.s] || {};
      var dif = o.real - o.presu;
      box.innerHTML = '<span class="mc-exp-cab"><span aria-hidden="true">' + o.ico + '</span> <b>' + esc(o.n) + '</b></span>' +
        '<span class="mc-exp-meta">' + esc(sec.ico || '') + ' ' + esc(sec.n || '') + ' · ' + esc(o.p) + ' · ' + esc(o.per) + (o.clave ? ' · clave de cartera ' + esc(o.clave) : '') + '</span>' +
        '<span class="mc-exp-op">Diferencia: ' + fnum(o.real) + ' − ' + fnum(o.presu) + ' = <b>' + sg(dif) + fnum(dif) + ' mdp</b>; sobrecosto registrado: <b>' + sg(o.sob) + fnum(o.sob) + '%</b>.</span>' +
        '<ul class="mc-exp-defs">' + defsHtml(o, ['inversion_presupuestada_mdp', 'inversion_real_mdp', 'sobrecosto_pct']) + '</ul>' + fuentesHtml(o) +
        '<span class="mc-exp-acc"><a href="herramienta-megaobras-sector.html#obra-' + encodeURIComponent(id) + '">Ver su ficha completa en Obra por obra, por industria →</a>' +
        '<button type="button" class="mc-b mc-b-mini" data-cerrar="inv">Cerrar</button></span>';
      box.classList.add('mc-exp-on');
      return;
    }
    var m = Number(mesa), tb = $('mcT' + m);
    var r2 = tb.tBodies[0].querySelector('tr[data-id="' + id + '"]');
    if (!r2) return;
    var i = Number(r2.getAttribute('data-i'));
    if (i > st[m]) { st[m] = i; pintar(m); }
    [].forEach.call(tb.tBodies[0].rows, function (x) { x.classList.remove('mc-sel'); });
    r2.classList.add('mc-sel');
    resalta(m, i);
    var p = pasos[m][i];
    box.innerHTML = '<b>Renglón ' + i + ' · ' + esc(o.n) + '.</b> ' + (m === 1 ? op1(o, p) : op2(o, p)) +
      (m === 1 ? '<ul class="mc-exp-defs">' + defsHtml(o, ['inversion_presupuestada_mdp', 'inversion_real_mdp']) + '</ul>' + fuentesHtml(o) : '');
  }

  function para(m) {
    clearInterval(auto[m]); auto[m] = null;
    var b = raiz.querySelector('.mc-b[data-acc="auto"][data-mesa="' + m + '"]');
    if (b) { b.setAttribute('aria-pressed', 'false'); b.innerHTML = '<span aria-hidden="true">⏯</span> Reproducir'; }
  }
  function reproduce(m) {
    if (auto[m]) { para(m); return; }
    if (st[m] >= total(m)) st[m] = 0;
    pintar(m);
    var b = raiz.querySelector('.mc-b[data-acc="auto"][data-mesa="' + m + '"]');
    if (b) { b.setAttribute('aria-pressed', 'true'); b.innerHTML = '<span aria-hidden="true">⏸</span> Pausar'; }
    auto[m] = setInterval(function () {
      if (st[m] >= total(m)) { para(m); return; }
      st[m] += 1; pintar(m);
    }, reduce ? 2200 : 1500);
  }

  /* ---------- CSV ---------- */
  function csv(nombre, filas) {
    var txt = '﻿' + filas.map(function (f) {
      return f.map(function (c) { var s = String(c == null ? '' : c); return /[",\n;]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; }).join(',');
    }).join('\r\n');
    var url = URL.createObjectURL(new Blob([txt], { type: 'text/csv;charset=utf-8' }));
    var a = document.createElement('a');
    a.href = url; a.download = nombre; document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(url); a.remove(); }, 500);
  }
  function filtroTxt() { return 'las ' + D.obras.length + ' obras; orden: ' + est.orden; }
  function descarga(k) {
    var pie = ['Fuente', 'Auditavisión, De cero al resultado (herramienta-megaobras-cero.html), con AUDIT_DB.simulador_megaobras; ' + filtroTxt()];
    var e = function (o, c) { return (o.ec || {})[c] || 'pendiente'; };
    if (k === '1') {
      var acum = 0;
      csv('mesa-1-aprobado-erogado.csv', [['#', 'Obra', 'Aprobado (mdp)', 'Estado aprobado', 'Erogado (mdp)', 'Estado erogado', 'Diferencia (mdp)', 'Acumulado (mdp)']]
        .concat(vista.map(function (o, i) { var d = o.real - o.presu; acum += d; return [i + 1, o.n, o.presu, e(o, 'inversion_presupuestada_mdp'), o.real, e(o, 'inversion_real_mdp'), Math.round(d * 10) / 10, Math.round(acum * 10) / 10]; }))
        .concat([['', 'Total del filtro', Math.round(A.presu * 10) / 10, 'derivado', Math.round(A.real * 10) / 10, 'derivado', Math.round(A.brecha * 10) / 10, Math.round(A.brecha * 10) / 10], pie]));
    } else if (k === '2') {
      var ac = 0;
      csv('mesa-2-gana-o-pierde-en-un-ano.csv', [['#', 'Obra', 'Año del dato', 'Gana (+) o pierde (−) (mdp)', 'Estado', 'Acumulado (mdp)', 'Documento o por qué falta']]
        .concat(vista.map(function (o, i) {
          ac += o.res || 0;
          return [i + 1, o.n, o.anio || '', o.res == null ? '' : o.res, o.pe, Math.round(ac * 10) / 10, o.op ? o.op.d + ' ' + o.op.u : (o.por || '')];
        }))
        .concat([['', 'Ganancia o pérdida neta del año', '', Math.round(-A.anual * 10) / 10, 'derivado', Math.round(-A.anual * 10) / 10, ''], pie]));
    } else if (k === '3') {
      var pad = D.padron.n;
      csv('mesa-3-por-contribuyente.csv', [['Paso', 'Concepto', 'Operación', 'Resultado', 'Estado'],
        [1, 'Pesos pagados de más sobre lo aprobado (mdp)', 'resultado de la mesa 1', Math.round(A.brecha * 10) / 10, 'derivado'],
        [2, 'Por contribuyente con RFC activo (pesos)', 'mesa 1 × 1,000,000 ÷ ' + pad, Math.round(A.brecha * 1000000 / pad), 'derivado'],
        [3, 'Pérdida neta de un año (mdp)', 'resultado de la mesa 2', Math.round(A.anual * 10) / 10, 'derivado'],
        [4, 'Por contribuyente con RFC activo, cada año (pesos)', 'mesa 2 × 1,000,000 ÷ ' + pad, Math.round(A.anual * 1000000 / pad), 'derivado'],
        ['Divisor', D.padron.d, D.padron.u, pad, 'oficial'], pie]);
    } else {
      var tot = D.obras.reduce(function (s, o) { return s + o.real; }, 0);
      csv('inventario-megaobras-por-sector.csv', [['Sector', 'Obra', 'Presidente', 'Periodo', 'Aprobado (mdp)', 'Estado aprobado', 'Erogado (mdp)', 'Estado erogado', 'Diferencia (mdp)', 'Sobrecosto (%)', 'Estado sobrecosto', '% del total erogado', 'Documentos']]
        .concat(D.obras.map(function (o) {
          return [D.sectores[o.s].n, o.n, o.p, o.per, o.presu, e(o, 'inversion_presupuestada_mdp'), o.real, e(o, 'inversion_real_mdp'), Math.round((o.real - o.presu) * 10) / 10,
            o.sob, e(o, 'sobrecosto_pct'), (o.real / tot * 100).toFixed(1), (o.fu || []).map(function (f) { return f.d + ' ' + f.u; }).join(' | ')];
        })).concat([['Fuente', 'Auditavisión, De cero al resultado, con AUDIT_DB.simulador_megaobras (las ' + D.obras.length + ' obras, sin filtro)']]));
    }
  }

  /* ---------- Contador en vivo ---------- */
  var t0 = Date.now(), pausado = false, acumVivo = 0, reloj = null;
  function vivoReinicia() { acumVivo = 0; t0 = Date.now(); vivoPinta(); }
  function vivoPinta() {
    var seg = (Date.now() - t0) / 1000;
    var v = acumVivo + (pausado ? 0 : seg * (A ? A.seg : 0));
    $('mcVivo').textContent = '$' + v.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function vivoArranca() { if (!reloj) reloj = setInterval(vivoPinta, reduce ? 1000 : 250); }
  $('mcVivoB').addEventListener('click', function () {
    var b = this;
    if (!pausado) {
      acumVivo += (Date.now() - t0) / 1000 * A.seg; pausado = true; clearInterval(reloj); reloj = null;
      b.setAttribute('aria-pressed', 'true'); b.innerHTML = '<span aria-hidden="true">▶</span> Seguir';
    } else {
      pausado = false; t0 = Date.now(); vivoArranca();
      b.setAttribute('aria-pressed', 'false'); b.innerHTML = '<span aria-hidden="true">⏸</span> Pausar';
    }
    vivoPinta();
  });

  /* ---------- Controles ---------- */
  var selO = $('mcOrden');
  function sincroniza() { selO.value = est.orden; }
  function cambia() { [1, 2, 3].forEach(para); guardar(); sincroniza(); render(); }
  selO.addEventListener('change', function () { est.orden = selO.value; cambia(); });

  raiz.addEventListener('click', function (ev) {
    var b = ev.target.closest ? ev.target.closest('button') : null;
    if (!b || !raiz.contains(b)) return;
    var m = b.getAttribute('data-mesa');
    if (b.classList.contains('mc-lupa')) { lupa(b.getAttribute('data-id'), m); return; }
    if (b.hasAttribute('data-csv')) { descarga(b.getAttribute('data-csv')); return; }
    if (b.hasAttribute('data-cerrar')) { var x = $('mcExpinv'); x.innerHTML = ''; x.classList.remove('mc-exp-on'); [].forEach.call(raiz.querySelectorAll('.mc-t-sec tr.mc-sel'), function (r) { r.classList.remove('mc-sel'); }); return; }
    var acc = b.getAttribute('data-acc');
    if (!acc || !m) return;
    m = Number(m);
    if (acc === 'sig') { para(m); st[m] = st[m] >= total(m) ? 0 : st[m] + 1; pintar(m); }
    else if (acc === 'cero') { para(m); st[m] = 0; pintar(m); }
    else if (acc === 'todo') { para(m); st[m] = total(m); pintar(m); }
    else if (acc === 'auto') reproduce(m);
  });

  $('mcEmpezar').addEventListener('click', function () {
    para(1); st[1] = 0; pintar(1);
    $('mcMesa1').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    setTimeout(function () { var b = raiz.querySelector('.mc-b[data-acc="sig"][data-mesa="1"]'); if (b) b.focus({ preventScroll: true }); }, reduce ? 0 : 450);
  });

  /* Arranque: si el lector dejó otro orden, se rehace la cuenta; si no, se
     leen los pasos de lo que ya escribió Python y se deja la cuenta completa. */
  sincroniza();
  if (est.orden !== DEF.orden) render();
  else { leerPasos(); [1, 2, 3].forEach(function (m) { st[m] = total(m); pintar(m); }); }
  vivoArranca();
})();
