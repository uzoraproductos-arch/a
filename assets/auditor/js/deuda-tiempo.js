/* ==========================================================================
   LA DEUDA A TRAVÉS DEL TIEMPO (08-10-2026)
   Capítulo 5 de «Sigue el dinero». Línea de tiempo de la deuda pública de
   1994 a la proyección de 2027, con franjas por sexenio y los dos mandos de
   siempre: contabilizar y reiniciar a ceros.

   Regla de la serie: para cada año se usa la publicación oficial más
   reciente que se encontró. Cuando una revisión del PIB cambió la cifra,
   la versión anterior se conserva en «rev» y se muestra en la ficha.
   No se interpola ningún año: 1995-1999 no tiene serie comparable.
   ========================================================================== */
(function () {
  'use strict';

  var raiz = document.getElementById('deudaTiempo');
  if (!raiz) return;

  /* ---------- Fuentes ---------- */
  var F = {
    BANXICO_IA1994: {
      corto: 'Banxico, Informe Anual 1994, p. 80',
      url: 'https://www.banxico.org.mx/publicaciones-y-prensa/informes-anuales/%7B0F2D589F-92A4-9C48-C456-643595B46CE5%7D.pdf'
    },
    BANXICO_IA1994_EXT: {
      corto: 'Banxico, Informe Anual 1994, Anexo 6, p. 165 (176 del PDF)',
      url: 'https://www.banxico.org.mx/publicaciones-y-prensa/informes-anuales/%7B0F2D589F-92A4-9C48-C456-643595B46CE5%7D.pdf'
    },
    ASF_IR2012: {
      corto: 'ASF, Informe del Resultado CP 2012, Tomo Ejecutivo, p. 67',
      url: 'https://www.asf.gob.mx/Trans/Informes/IR2012i/Documentos/InformeEjecutivo/Tomo%20Ejecutivo%20IR%202012.pdf'
    },
    ASF_IGE2018: {
      corto: 'ASF, Informe General Ejecutivo CP 2018, p. 258 del PDF',
      url: 'https://www.asf.gob.mx/uploads/55_Informes_de_auditoria/IGE_2018_PROTEGIDO.pdf'
    },
    ASF_IGE2022: {
      corto: 'ASF, Informe General Ejecutivo CP 2022, pp. 149-150',
      url: 'https://www.asf.gob.mx/uploads/55_Informes_de_auditoria/2022_IGE_a.pdf'
    },
    SHCP_C5_2024: {
      corto: 'SHCP, Comunicado 5/2024 (30 ene. 2024)',
      url: 'https://www.gob.mx/shcp/prensa/comunicado-no-5-informes-sobre-la-situacion-economica-las-finanzas-publicas-y-la-deuda-publica-al-cuarto-trimestre-de-2023'
    },
    SHCP_C4_2025: {
      corto: 'SHCP, Comunicado 4/2025 (30 ene. 2025)',
      url: 'https://www.gob.mx/shcp/prensa/comunicado-no-4-informes-sobre-la-situacion-economica-las-finanzas-publicas-y-la-deuda-publica-al-cuarto-trimestre-de-2024'
    },
    SHCP_C9_2026: {
      corto: 'SHCP, Comunicado 9/2026 (30 ene. 2026)',
      url: 'https://www.gob.mx/shcp/prensa/comunicado-no-9-informes-sobre-la-situacion-economica-las-finanzas-publicas-y-la-deuda-publica-al-cuarto-trimestre-de-2025'
    },
    CGPE2027_HIST: {
      corto: 'SHCP, Criterios Generales de Política Económica 2027, cuadro de RFSP y SHRFSP 2020-2026 (p. 53 del PDF)',
      url: 'https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-C.pdf'
    },
    CGPE2027: {
      corto: 'SHCP, Criterios Generales de Política Económica 2027 (pp. 18 y 68 del PDF)',
      url: 'https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-C.pdf'
    }
  };

  /* ---------- Serie: % del PIB y millones de pesos corrientes ---------- */
  /* t: 'obs' observado, 'est' estimado, 'proy' proyección.
     f: fuente del % del PIB; fm: fuente de los millones de pesos. */
  var SERIE = [
    { a: 2000, pib: 30.7, mdp: 2051001.7, f: 'ASF_IR2012', fm: 'ASF_IR2012' },
    { a: 2001, pib: 32.1, mdp: 2185276.7, f: 'ASF_IR2012', fm: 'ASF_IR2012' },
    { a: 2002, pib: 33.8, mdp: 2473944.3, f: 'ASF_IR2012', fm: 'ASF_IR2012' },
    { a: 2003, pib: 34.5, mdp: 2738362.0, f: 'ASF_IR2012', fm: 'ASF_IR2012' },
    { a: 2004, pib: 31.5, mdp: 2854591.5, f: 'ASF_IR2012', fm: 'ASF_IR2012' },
    { a: 2005, pib: 30.6, mdp: 2974208.0, f: 'ASF_IR2012', fm: 'ASF_IR2012' },
    { a: 2006, pib: 29.1, mdp: 3135438.9, f: 'ASF_IR2012', fm: 'ASF_IR2012' },
    { a: 2007, pib: 27.8, mdp: 3314462.7, f: 'ASF_IR2012', fm: 'ASF_IR2012' },
    { a: 2008, pib: 33.2, mdp: 4063364.3, f: 'ASF_IR2012', fm: 'ASF_IR2012' },
    { a: 2009, pib: 34.6, mdp: 4382263.2, f: 'ASF_IR2012', fm: 'ASF_IR2012' },
    { a: 2010, pib: 34.9, mdp: 4813210.5, f: 'ASF_IR2012', fm: 'ASF_IR2012' },
    { a: 2011, pib: 35.3, mdp: 5450589.7, f: 'ASF_IR2012', fm: 'ASF_IR2012' },
    { a: 2012, pib: 37.2, mdp: 5890846.1, f: 'ASF_IGE2018', fm: 'ASF_IGE2018',
      rev: [{ pib: 36.8, f: 'ASF_IR2012' }] },
    { a: 2013, pib: 40.0, mdp: 6504318.8, f: 'ASF_IGE2018', fm: 'ASF_IGE2018' },
    { a: 2014, pib: 42.6, mdp: 7446056.4, f: 'ASF_IGE2018', fm: 'ASF_IGE2018' },
    { a: 2015, pib: 46.5, mdp: 8633480.4, f: 'ASF_IGE2018', fm: 'ASF_IGE2018' },
    { a: 2016, pib: 48.7, mdp: 9797439.6, f: 'ASF_IGE2022', fm: 'ASF_IGE2022' },
    { a: 2017, pib: 45.7, mdp: 10031832.0, f: 'ASF_IGE2022', fm: 'ASF_IGE2022',
      rev: [{ pib: 45.8, f: 'ASF_IGE2018' }] },
    { a: 2018, pib: 44.9, mdp: 10551718.5, f: 'ASF_IGE2022', fm: 'ASF_IGE2022',
      rev: [{ pib: 44.8, f: 'ASF_IGE2018' }] },
    { a: 2019, pib: 44.5, mdp: 10870037.0, f: 'ASF_IGE2022', fm: 'ASF_IGE2022' },
    { a: 2020, pib: 50.2, mdp: 12082788.6, f: 'CGPE2027_HIST', fm: 'ASF_IGE2022',
      rev: [{ pib: 51.6, f: 'ASF_IGE2022' }] },
    { a: 2021, pib: 49.1, mdp: 13103963.9, f: 'CGPE2027_HIST', fm: 'ASF_IGE2022',
      rev: [{ pib: 50.8, f: 'ASF_IGE2022' }] },
    { a: 2022, pib: 47.6, mdp: 14065536.7, f: 'CGPE2027_HIST', fm: 'ASF_IGE2022',
      rev: [{ pib: 49.4, f: 'ASF_IGE2022' }] },
    { a: 2023, pib: 46.6, mdp: 14865529, f: 'CGPE2027_HIST', fm: 'SHCP_C5_2024',
      rev: [{ pib: 46.8, f: 'SHCP_C5_2024' }] },
    { a: 2024, pib: 51.9, mdp: 17426000, f: 'CGPE2027_HIST', fm: 'SHCP_C4_2025',
      rev: [{ pib: 51.4, f: 'SHCP_C4_2025' }] },
    { a: 2025, pib: 52.6, mdp: null, f: 'CGPE2027_HIST', fm: null,
      notaMdp: 'El Comunicado 9/2026 de Hacienda da el porcentaje (52.6 %) pero no el saldo en pesos. Queda pendiente.' },
    { a: 2026, pib: 54.0, mdp: 20062321.6, f: 'CGPE2027', fm: 'CGPE2027', t: 'est',
      nota: 'Cierre estimado. Para 2026 se aprobó 52.3 % del PIB; los Criterios explican que, con la revisión del PIB de 2023 y 2024 hecha por el INEGI, ese nivel equivale a 54.5 %.' },
    { a: 2027, pib: 55.0, mdp: 21665995.8, f: 'CGPE2027', fm: 'CGPE2027', t: 'proy',
      nota: 'Proyección del Paquete Económico 2027: aún no la aprueba el Congreso.' }
  ];

  var P1994 = {
    a: 1994, pib: 36.9, f: 'BANXICO_IA1994',
    nota: 'No es el mismo indicador. Hacienda publica el saldo histórico (SHRFSP) desde 2000; para 1994 Banxico reportó la deuda neta «económica amplia». El cierre incluye la devaluación de diciembre de 1994, que infló en pesos la deuda externa: en saldo promedio del año fue 24.8 % del PIB.'
  };

  /* Convención de la evaluación sexenal: seis años calendario por mandato. */
  var SEXENIOS = [
    { id: 'salinas', n: 'Salinas de Gortari', a: [1989, 1994], c: '#7a8aa8' },
    { id: 'zedillo', n: 'Zedillo', a: [1995, 2000], c: '#4f9be8' },
    { id: 'fox', n: 'Fox', a: [2001, 2006], c: '#23855a' },
    { id: 'calderon', n: 'Calderón', a: [2007, 2012], c: '#a9541a' },
    { id: 'epn', n: 'Peña Nieto', a: [2013, 2018], c: '#7d3fa6' },
    { id: 'amlo', n: 'López Obrador', a: [2019, 2024], c: '#b3261e' },
    { id: 'sheinbaum', n: 'Sheinbaum', a: [2025, 2030], c: '#0f7f7a', curso: true }
  ];

  var HITOS = [
    { a: 1994, t: 'Devaluación de diciembre', d: 'Infló en pesos la deuda externa al cierre del año.', f: 'BANXICO_IA1994' },
    { a: 2008, t: 'Reforma de la Ley del ISSSTE', d: 'El mayor incremento real del SHRFSP entre 2000 y 2012 (15.3 %), por las obligaciones de la reforma.', f: 'ASF_IR2012' },
    { a: 2020, t: 'Pandemia de COVID-19', d: 'La ASF registra un salto de 7.1 puntos del PIB respecto de 2019 por los efectos de la pandemia en la economía.', f: 'ASF_IGE2022' }
  ];

  var A0 = 1994, A1 = 2027;

  /* ---------- Utilidades ---------- */
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function chip(e) {
    var t = (e === 'oficial' || e === 'pendiente') ? e : 'derivado';
    return '<span class="est-chip est-' + t + '">' + t + '</span>';
  }
  function fuente(k) {
    var f = F[k];
    return f ? '<a href="' + f.url + '" target="_blank" rel="noopener noreferrer">' + esc(f.corto) + ' ↗</a>' : '';
  }
  function num(v, d) {
    return v.toLocaleString('es-MX', { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function billones(mdp) { return '$' + num(mdp / 1e6, 2) + ' billones'; }
  function signo(v) { return (v > 0 ? '+' : v < 0 ? '−' : '') + num(Math.abs(v), 1); }
  function anioDe(a) {
    for (var i = 0; i < SERIE.length; i++) if (SERIE[i].a === a) return SERIE[i];
    return null;
  }
  function sexenioDe(a) {
    for (var i = 0; i < SEXENIOS.length; i++) if (a >= SEXENIOS[i].a[0] && a <= SEXENIOS[i].a[1]) return SEXENIOS[i];
    return null;
  }
  function tipoTexto(p) {
    return p.t === 'est' ? 'cierre estimado' : p.t === 'proy' ? 'proyección' : 'observado';
  }

  /* ---------- Estado ---------- */
  var st = { modo: 'pib', cursor: null, contado: false, timer: null, sexenio: null };
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Gráfica SVG ---------- */
  var W = 1000, H = 430, ML = 58, MR = 22, MT = 40, MB = 52;
  function x(a) { return ML + (a - A0 + 0.5) / (A1 - A0 + 1) * (W - ML - MR); }
  function yMax() { return st.modo === 'pib' ? 60 : 24; }
  function y(v) { return MT + (1 - v / yMax()) * (H - MT - MB); }
  function valor(p) { return st.modo === 'pib' ? p.pib : (p.mdp == null ? null : p.mdp / 1e6); }

  function fondo() {
    var s = '';
    /* Franjas por sexenio */
    SEXENIOS.forEach(function (sx, i) {
      var a0 = Math.max(sx.a[0], A0), a1 = Math.min(sx.a[1], A1);
      if (a0 > a1) return;
      var x0 = x(a0) - (x(A0 + 1) - x(A0)) / 2, x1 = x(a1) + (x(A0 + 1) - x(A0)) / 2;
      var sel = st.sexenio === sx.id;
      s += '<g class="dt-franja' + (sel ? ' activa' : '') + '" data-sx="' + sx.id + '" tabindex="0" role="button" aria-label="Sexenio de ' + esc(sx.n) + ', ' + sx.a[0] + ' a ' + sx.a[1] + '">' +
        '<rect x="' + x0.toFixed(1) + '" y="' + MT + '" width="' + (x1 - x0).toFixed(1) + '" height="' + (H - MT - MB) + '" fill="' + sx.c + '" fill-opacity="' + (sel ? 0.2 : (i % 2 ? 0.07 : 0.11)) + '"></rect>' +
        '<rect x="' + x0.toFixed(1) + '" y="' + (MT - 26) + '" width="' + (x1 - x0).toFixed(1) + '" height="22" rx="4" fill="' + sx.c + '"></rect>' +
        '<text x="' + ((x0 + x1) / 2).toFixed(1) + '" y="' + (MT - 10) + '" class="dt-franja-n">' + (x1 - x0 < 45 ? '' : esc(x1 - x0 < 70 ? sx.n.split(' ')[0] : sx.n) + (sx.curso ? ' →' : '')) + '</text></g>';
    });
    /* Rejilla y eje Y */
    var paso = st.modo === 'pib' ? 10 : 4;
    for (var v = 0; v <= yMax(); v += paso) {
      s += '<line class="dt-rejilla" x1="' + ML + '" x2="' + (W - MR) + '" y1="' + y(v) + '" y2="' + y(v) + '"></line>' +
        '<text class="dt-eje-y" x="' + (ML - 8) + '" y="' + (y(v) + 4) + '">' + v + (st.modo === 'pib' ? '%' : '') + '</text>';
    }
    s += '<text class="dt-eje-tit" x="' + ML + '" y="' + (H - 6) + '">' + (st.modo === 'pib' ? 'Porcentaje del PIB' : 'Billones de pesos de cada año (sin ajustar por inflación)') + '</text>';
    /* Eje X */
    for (var a = A0; a <= A1; a++) {
      if (a === A0 || a === A1 || (a % 2 === 0 && a !== A1 - 1)) {
        s += '<text class="dt-eje-x' + (a % 6 === 0 || a === A0 ? ' fuerte' : '') + '" x="' + x(a) + '" y="' + (H - MB + 18) + '">' + a + '</text>';
      }
    }
    /* Hueco 1995-1999 */
    if (st.modo === 'pib') {
      s += '<text class="dt-hueco" x="' + x(1997) + '" y="' + (y(0) - 12) + '">1995-1999: sin serie comparable</text>';
    }
    return s;
  }

  function trazos() {
    var hasta = st.cursor == null ? A0 - 1 : st.cursor;
    var s = '', obs = [], fut = [], ultimo = null, tramos = [];
    /* 1994: indicador distinto, punto aparte */
    if (st.modo === 'pib' && hasta >= 1994) {
      var y94 = y(P1994.pib);
      if (hasta >= 2000) s += '<line class="dt-puente" x1="' + x(1994) + '" y1="' + y94 + '" x2="' + x(2000) + '" y2="' + y(30.7) + '"></line>';
      s += '<g class="dt-punto dt-94' + (st.cursor === 1994 ? ' actual' : '') + '" data-a="1994" tabindex="0" role="button" aria-label="1994: ' + P1994.pib + ' % del PIB, deuda neta económica amplia">' +
        '<rect x="' + (x(1994) - 6) + '" y="' + (y94 - 6) + '" width="12" height="12" transform="rotate(45 ' + x(1994) + ' ' + y94 + ')"></rect></g>';
    }
    var tramo = [];
    SERIE.forEach(function (p) {
      if (p.a > hasta) return;
      var v = valor(p);
      if (v == null) { if (tramo.length) tramos.push(tramo); tramo = []; return; }
      var pt = [x(p.a), y(v), p];
      if (p.t) fut.push(pt); else tramo.push(pt);
      if (!p.t) ultimo = pt;
    });
    if (tramo.length) tramos.push(tramo);
    tramos.forEach(function (tr) {
      s += '<polyline class="dt-linea" points="' + tr.map(function (q) { return q[0].toFixed(1) + ',' + q[1].toFixed(1); }).join(' ') + '"></polyline>';
    });
    if (fut.length) {
      var ini = ultimo ? [ultimo] : [];
      s += '<polyline class="dt-linea dt-futuro" points="' + ini.concat(fut).map(function (q) { return q[0].toFixed(1) + ',' + q[1].toFixed(1); }).join(' ') + '"></polyline>';
    }
    /* Área bajo la línea observada */
    tramos.forEach(function (tr) {
      if (tr.length < 2) return;
      var d = 'M' + tr[0][0].toFixed(1) + ',' + y(0) + ' ' + tr.map(function (q) { return 'L' + q[0].toFixed(1) + ',' + q[1].toFixed(1); }).join(' ') + ' L' + tr[tr.length - 1][0].toFixed(1) + ',' + y(0) + 'Z';
      s = '<path class="dt-area" d="' + d + '"></path>' + s;
    });
    /* Puntos */
    SERIE.forEach(function (p) {
      if (p.a > hasta) return;
      var v = valor(p);
      if (v == null) {
        s += '<g class="dt-punto dt-pend" data-a="' + p.a + '" tabindex="0" role="button" aria-label="' + p.a + ': saldo en pesos pendiente"><circle cx="' + x(p.a) + '" cy="' + (y(0) - 8) + '" r="5"></circle></g>';
        return;
      }
      s += '<g class="dt-punto' + (p.t ? ' dt-p-fut' : '') + (p.rev ? ' dt-p-rev' : '') + (st.cursor === p.a ? ' actual' : '') + '" data-a="' + p.a + '" tabindex="0" role="button" aria-label="' + p.a + ': ' + (st.modo === 'pib' ? p.pib + ' % del PIB' : billones(p.mdp)) + ', ' + tipoTexto(p) + '">' +
        '<circle cx="' + x(p.a) + '" cy="' + y(v) + '" r="' + (st.cursor === p.a ? 7.5 : 4.5) + '"></circle></g>';
    });
    /* Hitos */
    HITOS.forEach(function (h) {
      if (h.a > hasta) return;
      if (st.modo !== 'pib' && h.a === 1994) return;
      s += '<g class="dt-hito" data-a="' + h.a + '"><line x1="' + x(h.a) + '" x2="' + x(h.a) + '" y1="' + (MT + 4) + '" y2="' + y(0) + '"></line>' +
        '<text x="' + (x(h.a) + 5) + '" y="' + (MT + 16) + '">' + esc(h.t) + '</text></g>';
    });
    /* Marca vertical del año actual */
    if (st.cursor != null) s += '<line class="dt-cursor" x1="' + x(st.cursor) + '" x2="' + x(st.cursor) + '" y1="' + MT + '" y2="' + y(0) + '"></line>';
    return s;
  }

  function pintarGrafica() {
    var svg = raiz.querySelector('.dt-svg');
    svg.innerHTML = '<g class="dt-fondo">' + fondo() + '</g><g class="dt-trazos">' + trazos() + '</g>';
  }

  /* ---------- Contador ---------- */
  function pintarContador() {
    var c = raiz.querySelector('.dt-contador');
    var a = st.cursor;
    if (a == null) {
      c.innerHTML = '<span class="dt-c-anio">—</span><span class="dt-c-val">$0</span>' +
        '<span class="dt-c-pie">La línea está en ceros. Pulsa «Contabilizar» o mueve la barra de años.</span>';
      return;
    }
    var sx = sexenioDe(a);
    var cab = '<span class="dt-c-anio">' + a + '</span>';
    var quien = sx ? '<span class="dt-c-sx" style="--sx:' + sx.c + '">' + esc(sx.n) + '</span>' : '';
    if (a === 1994) {
      c.innerHTML = cab + quien + (st.modo === 'pib'
        ? '<span class="dt-c-val">' + num(P1994.pib, 1) + ' %<small> del PIB</small></span><span class="dt-c-pie">' + chip('oficial') + ' Deuda neta «económica amplia», otro indicador. ' + fuente(P1994.f) + '</span>'
        : '<span class="dt-c-val">—</span><span class="dt-c-pie">' + chip('pendiente') + ' Sin saldo en pesos comparable para 1994. Cambia a «% del PIB».</span>');
      return;
    }
    var p = anioDe(a);
    if (!p) {
      c.innerHTML = cab + quien + '<span class="dt-c-val">—</span><span class="dt-c-pie">' + chip('pendiente') + ' Hacienda publica el saldo histórico (SHRFSP) desde 2000. No hay serie comparable para ' + a + '.</span>';
      return;
    }
    var tipo = p.t ? ' <b class="dt-c-tipo">' + tipoTexto(p) + '</b>' : '';
    if (st.modo === 'pib') {
      c.innerHTML = cab + quien + '<span class="dt-c-val">' + num(p.pib, 1) + ' %<small> del PIB</small></span>' +
        '<span class="dt-c-pie">' + chip('oficial') + tipo + ' ' + fuente(p.f) + '</span>';
    } else if (p.mdp == null) {
      c.innerHTML = cab + quien + '<span class="dt-c-val">—</span><span class="dt-c-pie">' + chip('pendiente') + ' ' + esc(p.notaMdp) + '</span>';
    } else {
      c.innerHTML = cab + quien + '<span class="dt-c-val">' + billones(p.mdp) + '</span>' +
        '<span class="dt-c-pie">' + chip('oficial') + tipo + ' ' + num(p.mdp, 1) + ' millones de pesos. ' + fuente(p.fm) + '</span>';
    }
  }

  function pintarEstado() {
    var e = raiz.querySelector('.dt-estado');
    var b = raiz.querySelector('.dt-btn-contar');
    if (st.timer) {
      e.textContent = '⏳ Contabilizando año por año…';
    } else if (st.contado) {
      e.textContent = '✅ Contabilizado. De 2000 a 2025 la deuda amplia pasó de 30.7 % a 52.6 % del PIB. Toca un sexenio para ver su ficha.';
    } else if (st.cursor != null) {
      e.textContent = '🧭 Vas en ' + st.cursor + '. Sigue moviendo la barra o pulsa «Contabilizar» para recorrerlo todo.';
    } else {
      e.textContent = '⚪ La línea está en ceros. Pulsa «Contabilizar» para verla crecer año por año.';
    }
    b.innerHTML = (st.contado || st.cursor != null) && !st.timer ? '<span>↺</span> Reiniciar a ceros' : (st.timer ? '<span>⏸</span> Detener' : '<span>▶️</span> Contabilizar');
    var r = raiz.querySelector('.dt-rango');
    r.value = st.cursor == null ? A0 : st.cursor;
    r.setAttribute('aria-valuetext', st.cursor == null ? 'en ceros' : String(st.cursor));
  }

  function pintar() { pintarGrafica(); pintarContador(); pintarEstado(); }

  /* ---------- Ficha del sexenio ---------- */
  function cierre(a) { var p = anioDe(a); return p ? p.pib : null; }
  function fichaSexenio(id) {
    var sx = null;
    SEXENIOS.forEach(function (s) { if (s.id === id) sx = s; });
    var box = raiz.querySelector('.dt-ficha');
    if (!sx) { box.hidden = true; return; }
    var h = '<div class="dt-ficha-cab" style="--sx:' + sx.c + '"><strong>' + esc(sx.n) + '</strong> <span>' + sx.a[0] + '–' + sx.a[1] + (sx.curso ? ' · en curso' : '') + '</span>' +
      '<button type="button" class="dt-ficha-x" aria-label="Cerrar ficha">✕</button></div><div class="dt-ficha-cuerpo">';
    if (sx.id === 'salinas') {
      h += '<p>Cerró su sexenio con la deuda neta «económica amplia» en <b>36.9 % del PIB</b> ' + chip('oficial') + ' (' + fuente('BANXICO_IA1994') + ').</p>' +
        '<p>' + esc(P1994.nota) + '</p>' +
        '<p>Ese mismo año el Congreso autorizó hasta <b>5,000 millones de dólares</b> de endeudamiento externo neto y se usaron <b>3,619 millones</b> ' + chip('oficial') + ' (' + fuente('BANXICO_IA1994_EXT') + ').</p>';
    } else if (sx.id === 'zedillo') {
      h += '<p>Recibió 36.9 % (1994, deuda neta de Banxico) y entregó <b>30.7 % del PIB</b> en 2000, ya medido como saldo histórico (SHRFSP) ' + chip('oficial') + ' (' + fuente('ASF_IR2012') + ').</p>' +
        '<p>' + chip('pendiente') + ' No se resta un dato del otro: son indicadores distintos. De 1995 a 1999 no hay serie comparable publicada; cuando la tengamos de una fuente oficial, entra aquí.</p>';
    } else {
      var ini = cierre(sx.a[0] - 1), fin = sx.curso ? cierre(2025) : cierre(sx.a[1]);
      var max = null;
      SERIE.forEach(function (p) { if (p.a >= sx.a[0] && p.a <= sx.a[1] && !p.t && (max == null || p.pib > max.pib)) max = p; });
      h += '<div class="dt-ficha-cifras">' +
        '<span><small>Recibió (' + (sx.a[0] - 1) + ')</small><b>' + num(ini, 1) + ' %</b></span>' +
        '<span><small>' + (sx.curso ? 'Último cierre (2025)' : 'Entregó (' + sx.a[1] + ')') + '</small><b>' + num(fin, 1) + ' %</b></span>' +
        '<span class="dt-dif"><small>Cambio</small><b>' + signo(fin - ini) + ' pp</b>' + chip('derivado') + '</span>' +
        '<span><small>Máximo del periodo</small><b>' + num(max.pib, 1) + ' %</b><em>' + max.a + '</em></span></div>' +
        '<p class="dt-ficha-op">Cambio = cierre de ' + (sx.curso ? 2025 : sx.a[1]) + ' − cierre de ' + (sx.a[0] - 1) + ', en puntos del PIB. Las dos cifras pueden venir de publicaciones con mediciones del PIB distintas: tómalo como orden de magnitud, no al décimo.</p>';
      var hitos = HITOS.filter(function (x2) { return x2.a >= sx.a[0] && x2.a <= sx.a[1]; });
      hitos.forEach(function (ht) { h += '<p>📌 <b>' + ht.a + ' · ' + esc(ht.t) + '.</b> ' + esc(ht.d) + ' ' + chip('oficial') + ' (' + fuente(ht.f) + ')</p>'; });
      var revs = SERIE.filter(function (p) { return p.rev && p.a >= sx.a[0] && p.a <= sx.a[1]; });
      if (revs.length) {
        h += '<p class="dt-ficha-rev">🔎 <b>Cifras que cambiaron con la revisión del PIB:</b> ' + revs.map(function (p) {
          return p.a + ' se publicó primero como ' + num(p.rev[0].pib, 1) + ' % (' + esc(F[p.rev[0].f].corto) + ') y hoy se lee ' + num(p.pib, 1) + ' %';
        }).join('; ') + '. La deuda en pesos es la misma; lo que cambió fue el tamaño estimado de la economía.</p>';
      }
      if (sx.curso) {
        h += '<p>Hacienda estima cerrar 2026 en <b>54.0 %</b> y proyecta <b>55.0 %</b> para 2027 ' + chip('oficial') + ' (' + fuente('CGPE2027') + '). ' + esc(anioDe(2026).nota) + '</p>';
      }
    }
    h += '</div>';
    box.innerHTML = h;
    box.hidden = false;
    box.style.setProperty('--sx', sx.c);
    box.querySelector('.dt-ficha-x').addEventListener('click', function () { st.sexenio = null; box.hidden = true; pintarGrafica(); pintarChips(); });
  }

  function pintarChips() {
    raiz.querySelectorAll('.dt-sx-btn').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-sx') === st.sexenio ? 'true' : 'false');
    });
  }

  function elegirSexenio(id) {
    st.sexenio = st.sexenio === id ? null : id;
    pintarGrafica(); pintarChips(); fichaSexenio(st.sexenio);
  }

  /* ---------- Mandos ---------- */
  var ANIOS = [1994].concat(SERIE.map(function (p) { return p.a; }));
  function detener() { if (st.timer) { clearInterval(st.timer); st.timer = null; } }
  function contabilizar() {
    if (st.timer) { detener(); pintarEstado(); return; }
    if (st.contado || st.cursor != null) {
      st.cursor = null; st.contado = false; pintar(); return;
    }
    if (reduce) { st.cursor = A1; st.contado = true; pintar(); return; }
    var i = 0;
    st.cursor = ANIOS[0];
    st.timer = setInterval(function () {
      i++;
      if (i >= ANIOS.length) { detener(); st.contado = true; pintar(); return; }
      st.cursor = ANIOS[i];
      pintar();
    }, 260);
    pintar();
  }

  function irAnio(a) {
    detener();
    st.cursor = a;
    st.contado = a >= A1;
    pintar();
  }

  /* ---------- Tabla completa ---------- */
  function tabla() {
    var filas = '<tr><td>1994</td><td>' + num(P1994.pib, 1) + ' %</td><td>—</td><td>' + chip('oficial') + ' otro indicador</td><td>' + fuente(P1994.f) + '</td></tr>' +
      '<tr><td>1995–1999</td><td>—</td><td>—</td><td>' + chip('pendiente') + '</td><td>Sin serie comparable publicada.</td></tr>';
    SERIE.forEach(function (p) {
      filas += '<tr><td>' + p.a + (p.t ? ' <small>(' + tipoTexto(p) + ')</small>' : '') + '</td><td>' + num(p.pib, 1) + ' %' +
        (p.rev ? '<br><small>antes ' + num(p.rev[0].pib, 1) + ' %</small>' : '') + '</td><td>' +
        (p.mdp == null ? chip('pendiente') : num(p.mdp, 1)) + '</td><td>' + chip('oficial') + '</td><td>' + fuente(p.f) +
        (p.fm && p.fm !== p.f ? '<br><small>Pesos: </small>' + fuente(p.fm) : '') +
        (p.rev ? '<br><small>Antes: </small>' + fuente(p.rev[0].f) : '') + '</td></tr>';
    });
    return '<div class="dt-tabla-w"><table class="dt-tabla"><caption>Saldo histórico de los requerimientos financieros del sector público (SHRFSP)</caption>' +
      '<thead><tr><th>Año</th><th>% del PIB</th><th>Millones de pesos</th><th>Estado</th><th>Documento</th></tr></thead><tbody>' + filas + '</tbody></table></div>';
  }

  /* ---------- Lo que mostraba el libro: deuda externa 1988-1994 ---------- */
  function libro() {
    var d = [
      { a: 1988, v: 81.0 }, { a: 1989, v: 76.1 }, { a: 1990, v: 77.8 }, { a: 1991, v: 80.0 }, { a: 1992, v: 75.8 },
      { a: 1993, v: 78.747, ok: true, libro: 78.7 }, { a: 1994, v: 85.436, ok: true, libro: 85.1 }
    ];
    var barras = d.map(function (b) {
      var alto = (b.v / 90 * 100).toFixed(1);
      return '<div class="dt-lb' + (b.ok ? ' ok' : '') + '" title="' + b.a + ': ' + num(b.v, b.ok ? 3 : 1) + ' miles de millones de dólares">' +
        '<span class="dt-lb-v">' + num(b.v, 1) + '</span><span class="dt-lb-barra" style="height:' + alto + '%"></span><span class="dt-lb-a">' + b.a + '</span></div>';
    }).join('');
    return '<div class="dt-libro-graf" role="img" aria-label="Deuda externa del sector público, 1988 a 1994, en miles de millones de dólares">' + barras + '</div>' +
      '<p class="dt-leyenda"><span class="dt-lb-muestra ok"></span> Verificado en Banxico ' + chip('oficial') + ' <span class="dt-lb-muestra"></span> Cifra del libro, por cotejar ' + chip('pendiente') + '</p>';
  }

  /* ---------- Armado ---------- */
  raiz.innerHTML =
    '<div class="dt-mandos">' +
      '<button type="button" class="dt-btn dt-btn-contar"></button>' +
      '<div class="dt-modo" role="group" aria-label="Medida">' +
        '<button type="button" class="dt-modo-btn" data-modo="pib" aria-pressed="true">% del PIB</button>' +
        '<button type="button" class="dt-modo-btn" data-modo="mdp" aria-pressed="false">Billones de pesos</button>' +
      '</div>' +
      '<p class="dt-estado" aria-live="polite"></p>' +
    '</div>' +
    '<div class="dt-tablero">' +
      '<div class="dt-contador" aria-live="polite"></div>' +
      '<div class="dt-grafica-w">' +
        '<div class="dt-svg-w"><svg class="dt-svg" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Deuda pública de México de 1994 a 2027 por sexenio. La tabla de abajo trae cada cifra con su fuente."></svg></div>' +
        '<label class="dt-rango-w"><span>Recorre los años</span><input type="range" class="dt-rango" min="' + A0 + '" max="' + A1 + '" step="1" value="' + A0 + '"></label>' +
      '</div>' +
    '</div>' +
    '<div class="dt-sx" role="group" aria-label="Sexenios">' + SEXENIOS.map(function (sx) {
      return '<button type="button" class="dt-sx-btn" data-sx="' + sx.id + '" aria-pressed="false" style="--sx:' + sx.c + '">' + esc(sx.n) + ' <small>' + sx.a[0] + '–' + (sx.curso ? 'hoy' : sx.a[1]) + '</small></button>';
    }).join('') + '</div>' +
    '<div class="dt-ficha" hidden aria-live="polite"></div>' +
    '<details class="dt-detalle"><summary>📋 Ver la serie completa, año por año, con su documento</summary>' + tabla() +
      '<p class="dt-nota">Cada año viene de la publicación oficial más reciente que encontramos. Cuando el INEGI revisa el PIB, el porcentaje cambia aunque la deuda en pesos sea la misma: por eso algunos años muestran la cifra que se publicó antes. Los pesos son de cada año, sin ajustar por inflación.</p></details>' +
    '<div class="dt-antes">' +
      '<article class="dt-antes-t">' +
        '<h4>👑 Antes: el Porfiriato</h4>' +
        '<p>Con José Yves Limantour en Hacienda, el ejercicio 1894-1895 cerró con el primer superávit de la vida independiente del país, y en 1899 se consolidó la deuda externa en bonos colocados en Londres, Berlín y París.</p>' +
        '<p>' + chip('pendiente') + ' Las cifras de esa época vienen de reconstrucciones historiográficas y todavía no tienen su fuente primaria en el auditor, así que no las mezclamos con la serie de arriba.</p>' +
        '<a class="dt-antes-link" href="glosario.html">Los conceptos de la deuda, en el glosario ➔</a>' +
      '</article>' +
      '<article class="dt-antes-t">' +
        '<h4>📘 Lo que mostraba el libro (1995)</h4>' +
        '<p>La Gráfica 1 del capítulo 7 seguía la deuda externa del sector público, en miles de millones de dólares, de 1988 a 1994.</p>' +
        libro() +
        '<p class="dt-nota">Banxico reporta 78,747 millones de dólares al cierre de 1993 y 85,436 millones al cierre de 1994 (' + fuente('BANXICO_IA1994_EXT') + '). El libro anota 85.1 para 1994, y donde dice «4.1 millones» de aumento se refiere a miles de millones de dólares.</p>' +
      '</article>' +
      '<article class="dt-antes-t">' +
        '<h4>⚖️ Las reglas: quién autoriza la deuda</h4>' +
        '<ul class="dt-reglas">' +
          '<li><b>El Congreso da las bases.</b> Artículo 73, fracción VIII de la Constitución: ningún empréstito puede celebrarse sino para obras que directamente produzcan un incremento en los ingresos públicos, salvo regulación monetaria, refinanciamiento o emergencia.</li>' +
          '<li><b>Cada año pone un tope.</b> La Ley de Ingresos fija el monto de endeudamiento neto que se autoriza (art. 2o. en la de 2026).</li>' +
          '<li><b>Hacienda la contrata.</b> Lo regula la Ley Federal de Deuda Pública. El libro la llama <em>Ley General de Deuda Pública</em>: así se llamó desde 1976 hasta que un decreto del 27 de abril de 2016 cambió su nombre.</li>' +
        '</ul>' +
        '<a class="dt-antes-link" href="https://www.diputados.gob.mx/LeyesBiblio/pdf_mov/Ley_Federal_de_Deuda_Publica.pdf" target="_blank" rel="noopener noreferrer">Ley Federal de Deuda Pública (Cámara de Diputados) ↗</a>' +
      '</article>' +
    '</div>';

  raiz.querySelector('.dt-btn-contar').addEventListener('click', contabilizar);
  raiz.querySelector('.dt-rango').addEventListener('input', function (e) { irAnio(parseInt(e.target.value, 10)); });
  raiz.querySelectorAll('.dt-modo-btn').forEach(function (b) {
    b.addEventListener('click', function () {
      st.modo = b.getAttribute('data-modo');
      raiz.querySelectorAll('.dt-modo-btn').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
      pintar();
    });
  });
  raiz.querySelectorAll('.dt-sx-btn').forEach(function (b) {
    b.addEventListener('click', function () { elegirSexenio(b.getAttribute('data-sx')); });
  });
  var svg = raiz.querySelector('.dt-svg');
  function accionSvg(t) {
    var g = t.closest && t.closest('[data-a],[data-sx]');
    if (!g) return;
    if (g.hasAttribute('data-a') && g.classList.contains('dt-punto')) irAnio(parseInt(g.getAttribute('data-a'), 10));
    else if (g.hasAttribute('data-sx')) elegirSexenio(g.getAttribute('data-sx'));
  }
  svg.addEventListener('click', function (e) { accionSvg(e.target); });
  svg.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); accionSvg(e.target); }
  });

  pintar();
})();
