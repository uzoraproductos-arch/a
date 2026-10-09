/* ==========================================================================
   EL EXAMEN DE LOS PRESIDENTES (09-10-2026)
   Aprende › Trivia. Se mudó aquí desde el bloque 3 del módulo de Megaobras
   («Administración presidencial»), que a su vez la trajo de la pestaña 5.1
   de la Enciclopedia.

   Cómo funciona: rondas de preguntas; cada respuesta abre su gráfica, que
   arranca en cero y sube con «Contabilizar». Hay un modo contra reloj.
   Al final: la calificación y el estado de cuenta de cada presidente, con
   su reloj de la deuda (lo que creció la deuda por segundo en su sexenio).

   Regla editorial: cada cifra trae su documento y su chip
   (oficial / derivado / pendiente). Las cifras de economía, empleo y
   fiscalización son las de la colección evaluacion_sexenal de la base del
   auditor (consulta 26-09-2026); las de deuda, las de la línea de tiempo de
   Sigue el dinero (deuda-tiempo.js): la publicación oficial más reciente
   de cada año. Si cambian allá, se cambian aquí.
   ========================================================================== */
(function () {
  'use strict';

  var raiz = document.getElementById('triviaPres');
  if (!raiz) return;

  /* ---------- Fuentes ---------- */
  var F = {
    INEGI_PIBT: { corto: 'INEGI, PIB trimestral, año base 2018', url: 'https://www.inegi.org.mx/contenidos/programas/pib/2018/tabulados/ori/PIBT_2.xlsx' },
    INEGI_EHM2014: { corto: 'INEGI, Estadísticas históricas de México 2014, cuadro 8.6', url: 'https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/HyM2014/8.%20Informacion%20economica%20agregada.pdf' },
    BANXICO_IA1994: { corto: 'Banxico, Informe Anual 1994, p. 80', url: 'https://www.banxico.org.mx/publicaciones-y-prensa/informes-anuales/%7B0F2D589F-92A4-9C48-C456-643595B46CE5%7D.pdf' },
    ASF_IR2012: { corto: 'ASF, Informe del Resultado CP 2012, Tomo Ejecutivo, p. 67', url: 'https://www.asf.gob.mx/Trans/Informes/IR2012i/Documentos/InformeEjecutivo/Tomo%20Ejecutivo%20IR%202012.pdf' },
    ASF_IGE2018: { corto: 'ASF, Informe General Ejecutivo CP 2018', url: 'https://www.asf.gob.mx/uploads/55_Informes_de_auditoria/IGE_2018_PROTEGIDO.pdf' },
    ASF_IGE2022: { corto: 'ASF, Informe General Ejecutivo CP 2022', url: 'https://www.asf.gob.mx/uploads/55_Informes_de_auditoria/2022_IGE_a.pdf' },
    ASF_MDB: { corto: 'ASF, Matrices de Datos Básicos CP 2019–2024', url: 'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Matriz/MDB_Consolidado.pdf' },
    SHCP_C4_2025: { corto: 'SHCP, Comunicado 4/2025 (30 ene. 2025)', url: 'https://www.gob.mx/shcp/prensa/comunicado-no-4-informes-sobre-la-situacion-economica-las-finanzas-publicas-y-la-deuda-publica-al-cuarto-trimestre-de-2024' },
    CGPE2027_HIST: { corto: 'SHCP, Criterios Generales de Política Económica 2027 (p. 53 del PDF)', url: 'https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-C.pdf' },
    PRES_5IG: { corto: 'Presidencia, Quinto Informe de Gobierno, Anexo Estadístico, p. 530', url: 'https://framework-gb.cdn.gob.mx/quintoinforme/5IG_ANEXO_FINAL_TGM_250818.pdf' },
    IMSS_008_2019: { corto: 'IMSS, Comunicado 008/2019', url: 'https://www.imss.gob.mx/prensa/archivo/201901/008' },
    IMSS_009_2025: { corto: 'IMSS, Comunicado 009/2025', url: 'https://www.imss.gob.mx/prensa/archivo/202501/009' },
    EHM_VIAS: { corto: 'INEGI, Estadísticas históricas de México 2014, cuadro 14.18 (p. 45 del PDF)', url: 'https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/HyM2014/14.%20Transportes%20y%20comunicaciones.pdf' },
    EHM_BAL: { corto: 'INEGI, Estadísticas históricas de México 2014, cuadro 16.3 (p. 11 del PDF)', url: 'https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/HyM2014/16.%20Finanzas%20publicas.pdf' },
    EHM_ING: { corto: 'INEGI, Estadísticas históricas de México 2014, cuadro 16.6 (p. 15 del PDF)', url: 'https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/HyM2014/16.%20Finanzas%20publicas.pdf' },
    EHM_ALF: { corto: 'INEGI, Estadísticas históricas de México 2014, cuadro 3.7 (p. 24 del PDF)', url: 'https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/HyM2014/3.%20Educacion.pdf' }
  };

  /* ---------- El Porfiriato (INEGI, Estadísticas históricas de México 2014) ---------- */
  /* Kilómetros de vía férrea (cuadro 14.18: troncales, ramales y
     particulares). Balance del gobierno federal, millones de pesos de cada
     año fiscal, de julio a junio (cuadro 16.3: ingresos efectivos menos
     egresos ejercidos). Ingresos de 1894-1895 por fuente, miles de pesos
     (cuadro 16.6). Analfabetismo (cuadro 3.7: en 1895, mayores de 6 años;
     en 1900 y 1910, mayores de 10). */
  var PORF = {
    vias: [[1876, 617], [1880, 962], [1884, 5742], [1890, 9540], [1900, 13301], [1910, 19748]],
    balance: [['1893-94', -5.5], ['1894-95', -1.2], ['1895-96', 5.4], ['1896-97', 3.0], ['1897-98', 0.9], ['1898-99', 6.6],
      ['1899-00', 6.4], ['1900-01', 4.0], ['1901-02', 3.0], ['1902-03', 8.0], ['1903-04', 10.0], ['1904-05', 13.0],
      ['1905-06', 23.0], ['1906-07', 29.0], ['1907-08', 19.0], ['1908-09', 6.0], ['1909-10', 11.0], ['1910-11', 10.0]],
    ingresos9495: [['ext', 'Impuestos al comercio exterior (aduanas)', 19871], ['fed', 'Impuestos en toda la Federación', 17600],
      ['df', 'Impuestos solo en el Distrito Federal', 3379], ['serv', 'Servicios públicos', 1885]],
    analfabetas: [[1895, 82.1], [1900, 77.7], [1910, 72.3]]
  };
  var ORO = '#b8902f';

  /* ---------- Los presidentes ---------- */
  var P = [
    { id: 'salinas', n: 'Carlos Salinas de Gortari', c: 'Salinas', a: [1989, 1994], col: '#7a8aa8' },
    { id: 'zedillo', n: 'Ernesto Zedillo', c: 'Zedillo', a: [1995, 2000], col: '#4f9be8' },
    { id: 'fox', n: 'Vicente Fox', c: 'Fox', a: [2001, 2006], col: '#23855a' },
    { id: 'calderon', n: 'Felipe Calderón', c: 'Calderón', a: [2007, 2012], col: '#a9541a' },
    { id: 'epn', n: 'Enrique Peña Nieto', c: 'Peña Nieto', a: [2013, 2018], col: '#7d3fa6' },
    { id: 'amlo', n: 'Andrés Manuel López Obrador', c: 'López Obrador', a: [2019, 2024], col: '#b3261e' }
  ];
  function pres(id) { for (var i = 0; i < P.length; i++) if (P[i].id === id) return P[i]; return null; }

  /* ---------- Las cifras de cada sexenio ---------- */
  /* pib: tasa media anual del PIB real (derivado). emp: asegurados IMSS
     creados (derivado). dIni/dFin: deuda al recibir y al entregar, % PIB.
     mIni/mFin: SHRFSP en millones de pesos corrientes. aud: auditorías de
     la ASF. rec: recuperaciones operadas (mdp). */
  var D = {
    salinas: {
      pib: { v: 3.91, f: 'INEGI_EHM2014', nota: 'Serie a precios de 1993: la de 2018 empieza en 1993.' },
      emp: { pend: 'La serie de asegurados del anexo estadístico empieza en 1997.' },
      dFin: { v: 36.9, f: 'BANXICO_IA1994', nota: 'Deuda neta económica amplia de Banxico, no el SHRFSP: para 1994 no existe.' },
      aud: { na: 'La ASF nació en 2000.' }, rec: { na: 'La ASF nació en 2000.' }
    },
    zedillo: {
      pib: { v: 3.48, f: 'INEGI_PIBT' },
      emp: { pend: 'La serie de asegurados del anexo estadístico empieza en 1997.' },
      dFin: { v: 30.7, f: 'ASF_IR2012' }, mFin: { v: 2051001.7, f: 'ASF_IR2012' },
      aud: { v: 312, f: 'ASF_IGE2018', nota: 'Solo la Cuenta Pública 2000, la primera que revisó la ASF.' },
      rec: { pend: 'La serie de recuperaciones de la ASF empieza en la Cuenta Pública 2001.' }
    },
    fox: {
      pib: { v: 1.81, f: 'INEGI_PIBT' },
      emp: { v: 1240732, f: 'PRES_5IG' },
      dIni: { v: 30.7, f: 'ASF_IR2012' }, dFin: { v: 29.1, f: 'ASF_IR2012' },
      mIni: { v: 2051001.7, f: 'ASF_IR2012' }, mFin: { v: 3135438.9, f: 'ASF_IR2012' },
      aud: { v: 2834, f: 'ASF_IGE2018' },
      rec: { pend: 'La ASF publica 2001–2008 en una sola cifra ($41,091.6 mdp), sin separar a Fox de los dos primeros años de Calderón.' }
    },
    calderon: {
      pib: { v: 1.38, f: 'INEGI_PIBT' },
      emp: { v: 2383551, f: 'PRES_5IG' },
      dIni: { v: 29.1, f: 'ASF_IR2012' }, dFin: { v: 37.2, f: 'ASF_IGE2018', nota: 'Publicada después con el PIB revisado; el informe de 2012 decía 36.8.' },
      mIni: { v: 3135438.9, f: 'ASF_IR2012' }, mFin: { v: 5890846.1, f: 'ASF_IGE2018' },
      aud: { v: 6209, f: 'ASF_IGE2018' },
      rec: { v: 56455.58, f: 'ASF_IGE2022', nota: 'Solo CP 2009–2012; 2007 y 2008 están en la cifra conjunta 2001–2008.' }
    },
    epn: {
      pib: { v: 1.94, f: 'INEGI_PIBT' },
      emp: { v: 4017322, f: 'IMSS_008_2019' },
      dIni: { v: 37.2, f: 'ASF_IGE2018' }, dFin: { v: 44.9, f: 'ASF_IGE2022' },
      mIni: { v: 5890846.1, f: 'ASF_IGE2018' }, mFin: { v: 10551718.5, f: 'ASF_IGE2022' },
      aud: { v: 10064, f: 'ASF_IGE2018' },
      rec: { v: 52264.15, f: 'ASF_IGE2022' }
    },
    amlo: {
      pib: { v: 0.82, f: 'INEGI_PIBT', nota: 'El PIB de 2023 y 2024 es preliminar.' },
      emp: { v: 2159014, f: 'IMSS_009_2025' },
      dIni: { v: 44.9, f: 'ASF_IGE2022' }, dFin: { v: 51.9, f: 'CGPE2027_HIST', nota: 'Con el PIB revisado; Hacienda informó 51.4 en enero de 2025.' },
      mIni: { v: 10551718.5, f: 'ASF_IGE2022' }, mFin: { v: 17426000, f: 'SHCP_C4_2025' },
      aud: { v: 11810, f: 'ASF_MDB', nota: 'La Cuenta Pública 2024 incluye octubre a diciembre, ya con el gobierno siguiente.' },
      rec: { v: 10008.61, f: 'ASF_IGE2022', nota: 'Solo CP 2019–2022: las de 2023 y 2024 seguían en solventación.' }
    }
  };

  /* Lo que se dejó por aclarar en cada Cuenta Pública (mdp, ASF, renglón
     Total de la Matriz de Datos Básicos). */
  var POR_ACLARAR = [
    { cp: 2019, v: 99396.5848 }, { cp: 2020, v: 60834.1346 }, { cp: 2021, v: 61840.3345 },
    { cp: 2022, v: 29765.9048 }, { cp: 2023, v: 51979.0424 }, { cp: 2024, v: 65169.0976 }
  ];

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
  function fuentes(ks) {
    var vistos = {};
    return ks.filter(function (k) { if (vistos[k] || !F[k]) return false; vistos[k] = 1; return true; }).map(fuente).join(' · ');
  }
  function num(v, d) {
    return v.toLocaleString('es-MX', { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function fmt(v, f) {
    if (f === 'pct') return num(v, 1) + '%';
    if (f === 'pct2') return num(v, 2) + '%';
    if (f === 'pp') return (v > 0 ? '+' : v < 0 ? '−' : '') + num(Math.abs(v), 1) + ' pts.';
    if (f === 'ent') return num(Math.round(v), 0);
    if (f === 'mdp') return '$' + num(v, 1) + ' mdp';
    if (f === 'bill') return '$' + num(v / 1e6, 2) + ' billones';
    if (f === 'pesos') return '$' + num(Math.round(v), 0);
    if (f === 'km') return num(Math.round(v), 0) + ' km';
    if (f === 'mill') return (v < 0 ? '−' : '') + '$' + num(Math.abs(v), 1) + ' millones';
    if (f === 'miles') return '$' + num(Math.round(v), 0) + ' mil';
    return String(v);
  }
  /* Segundos de los seis años calendario de un sexenio. */
  function segundos(a) {
    return (Date.UTC(a[1] + 1, 0, 1) - Date.UTC(a[0], 0, 1)) / 1000;
  }
  function porSegundo(id) {
    var d = D[id], p = pres(id);
    if (!d.mIni || !d.mFin) return null;
    return (d.mFin.v - d.mIni.v) * 1e6 / segundos(p.a);
  }
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Las preguntas ---------- */
  /* tipo 'pres': las opciones son presidentes con dato; gana el mayor.
     tipo 'lista': opciones propias, con la correcta marcada.
     Cada pregunta trae sus barras (datos), su lección y sus fuentes. */
  function datosDe(campo, fn) {
    return P.filter(function (p) { var o = D[p.id][campo]; return o && typeof o.v === 'number'; }).map(function (p) {
      return { id: p.id, et: p.c, sub: p.a[0] + '–' + p.a[1], col: p.col, v: fn ? fn(p.id) : D[p.id][campo].v };
    });
  }
  function fuera(campo) {
    return P.filter(function (p) { var o = D[p.id][campo]; return !o || typeof o.v !== 'number'; }).map(function (p) {
      var o = D[p.id][campo] || {};
      return '<b>' + esc(p.c) + '</b>: ' + esc(o.pend || o.na || 'sin dato comparable.');
    });
  }

  var RONDAS = [
    { k: 'porf', et: 'Antes de los sexenios: el Porfiriato', ico: '🎩' },
    { k: 'eco', et: 'La economía', ico: '📈' },
    { k: 'deuda', et: 'La deuda', ico: '💳' },
    { k: 'fisc', et: 'La fiscalización', ico: '🔎' }
  ];

  var PREGUNTAS = [
    { r: 'porf', tipo: 'lista', q: 'Al terminar el Porfiriato, en 1910, ¿cuántos kilómetros de vía férrea tenía México?',
      tit: 'Kilómetros de vía férrea en operación', fmtv: 'km', est: 'oficial', natural: true, correcta: 'k4',
      opciones: function () { return [['k1', '617 km'], ['k2', '5,742 km'], ['k3', '13,301 km'], ['k4', '19,748 km']].map(function (o) { return { id: o[0], et: o[1], sub: '', col: ORO }; }); },
      datos: function () { return PORF.vias.map(function (r) { return { id: 'v' + r[0], et: String(r[0]), sub: '', col: ORO, v: r[1] }; }); },
      fuera: function () { return []; },
      op: 'Vías troncales, ramales y particulares, según el cuadro del INEGI. No hay dato de 1907 a 1909.',
      fs: ['EHM_VIAS'],
      leccion: 'La red se multiplicó por 32 en 34 años. Pero el gran salto fue en los años ochenta del siglo XIX, con las concesiones a compañías extranjeras: dos terceras partes de la vía de 1910 ya existían en 1900. La cifra de 19,280 km que circula mucho no coincide con la del INEGI.' },
    { r: 'porf', tipo: 'lista', q: '¿En qué año fiscal empezó la racha de superávits del gobierno federal que duró hasta el final del Porfiriato?',
      tit: 'Balance del gobierno federal por año fiscal (julio a junio), millones de pesos de la época', fmtv: 'mill', est: 'oficial', natural: true, correcta: 'b1895-96',
      opciones: function () { return ['1877-78', '1894-95', '1895-96', '1906-07'].map(function (a) { return { id: 'b' + a, et: a, sub: 'año fiscal', col: ORO }; }); },
      datos: function () { return PORF.balance.map(function (r) { return { id: 'b' + r[0], et: r[0], sub: '', col: r[1] < 0 ? '#b3261e' : '#23855a', v: r[1] }; }); },
      fuera: function () { return []; },
      op: 'Ingresos efectivos menos egresos ejercidos, como los publica el INEGI.',
      fs: ['EHM_BAL'],
      leccion: 'Se repite que el primer superávit de la historia fue el de 1894-1895. Según el INEGI, ese año cerró con déficit de 1.2 millones; la racha empieza en 1895-1896, con 5.4 millones de superávit, y ni siquiera fue la primera: hubo años con superávit en 1867-1868 y en la década de 1870. Otra lección: un superávit dice que se gastó menos de lo que entró, no que el país estuviera mejor.' },
    { r: 'porf', tipo: 'lista', q: 'En 1894-1895, ¿de dónde sacaba el gobierno federal la mayor parte de su dinero?',
      tit: 'Ingresos efectivos del gobierno federal en 1894-1895 por fuente, miles de pesos de la época', fmtv: 'miles', est: 'oficial',
      datos: function () { return PORF.ingresos9495.map(function (r) { return { id: r[0], et: r[1], sub: '', col: ORO, v: r[2] }; }); },
      fuera: function () { return ['El ingreso efectivo total fue de $43,946 mil; los cuatro renglones de la gráfica son las fuentes que el cuadro desglosa.']; },
      op: 'Columnas del cuadro de ingresos por fuente. La proporción de aduanas, 45.2%, es $19,871 entre $43,946 mil (derivado).',
      fs: ['EHM_ING'],
      leccion: 'Casi la mitad del dinero venía de gravar lo que entraba y salía del país. El impuesto sobre la renta no existía: el INEGI lo registra a partir de 1925. Un Estado que vive de las aduanas recauda poco y casi no redistribuye.' },
    { r: 'porf', tipo: 'lista', q: 'En el censo de 1895, ¿cuántas personas de cada diez no sabían leer ni escribir?',
      tit: 'Población analfabeta, por ciento', fmtv: 'pct', est: 'oficial', natural: true, correcta: 'a8',
      opciones: function () { return [['a3', 'Tres de cada diez'], ['a5', 'Cinco de cada diez'], ['a8', 'Ocho de cada diez'], ['a9', 'Nueve de cada diez']].map(function (o) { return { id: o[0], et: o[1], sub: '', col: ORO }; }); },
      datos: function () { return PORF.analfabetas.map(function (r) { return { id: 'f' + r[0], et: 'Censo de ' + r[0], sub: r[0] === 1895 ? 'mayores de 6 años' : 'mayores de 10 años', col: ORO, v: r[1] }; }); },
      fuera: function () { return []; },
      op: 'Analfabetas entre la población del rango de edad de cada censo.',
      fs: ['EHM_ALF'],
      leccion: 'El analfabetismo bajó casi diez puntos en quince años: el régimen sí avanzó. Pero en 1910 siete de cada diez personas seguían sin saber leer. Los censos no miden igual (1895 cuenta desde los 6 años; los otros, desde los 10), así que la comparación es aproximada.' },
    { r: 'eco', tipo: 'pres', q: '¿Con qué presidente creció más la economía?',
      tit: 'Crecimiento del PIB real, promedio anual del sexenio', fmtv: 'pct2', est: 'derivado',
      datos: function () { return datosDe('pib'); }, fuera: function () { return fuera('pib'); },
      op: 'Tasa media anual entre el PIB del año previo al sexenio y el de su último año.',
      fs: ['INEGI_PIBT', 'INEGI_EHM2014'],
      leccion: 'Salinas tiene el promedio más alto, medido con la serie a precios de 1993. Zedillo empezó con la peor crisis (−5.9% en 1995) y aun así quedó segundo, porque la recuperación de 1996 a 2000 fue rápida. Un promedio de seis años no cuenta cómo se vivió cada uno.' },
    { r: 'eco', tipo: 'pres', q: '¿Con qué presidente se crearon más empleos formales?',
      tit: 'Asegurados en el IMSS creados en el sexenio', fmtv: 'ent', est: 'derivado',
      datos: function () { return datosDe('emp'); }, fuera: function () { return fuera('emp'); },
      op: 'Asegurados al 31 de diciembre del último año menos los del año previo al sexenio.',
      fs: ['PRES_5IG', 'IMSS_008_2019', 'IMSS_009_2025'],
      leccion: 'Es empleo afiliado al IMSS, no empleo total: cerca de la mitad de quienes trabajan en México lo hace en la informalidad y no aparece aquí.' },
    { r: 'deuda', tipo: 'pres', q: '¿Quién entregó la deuda más alta como proporción de la economía?',
      tit: 'Deuda pública al cierre del sexenio, % del PIB', fmtv: 'pct', est: 'oficial',
      datos: function () { return datosDe('dFin'); }, fuera: function () { return []; },
      op: 'Saldo histórico de los requerimientos financieros del sector público (SHRFSP) al cierre del último año. Salinas: deuda neta económica amplia de Banxico, otro indicador.',
      fs: ['BANXICO_IA1994', 'ASF_IR2012', 'ASF_IGE2018', 'ASF_IGE2022', 'CGPE2027_HIST'],
      leccion: 'Desde 2006 cada sexenio entregó una deuda mayor que la que recibió. En 2020 el PIB cayó y el cociente subió solo por eso: la deuda se mide contra el tamaño de la economía.' },
    { r: 'deuda', tipo: 'pres', q: '¿Con quién subió más la deuda, en puntos del PIB, entre lo que recibió y lo que entregó?',
      tit: 'Cambio de la deuda en el sexenio, puntos del PIB', fmtv: 'pp', est: 'derivado',
      datos: function () { return datosDe('dIni', function (id) { return Math.round((D[id].dFin.v - D[id].dIni.v) * 10) / 10; }); },
      fuera: function () { return ['<b>Salinas y Zedillo</b>: la deuda de 1988 y la de 1994 se publicaron con otro indicador (deuda neta de Banxico); restarla del SHRFSP mezclaría dos medidas.']; },
      op: 'Deuda al cierre del sexenio menos la del cierre del sexenio anterior, ambas en % del PIB.',
      fs: ['ASF_IR2012', 'ASF_IGE2018', 'ASF_IGE2022', 'CGPE2027_HIST'],
      leccion: 'Con Fox la deuda bajó 1.6 puntos. Los tres siguientes la subieron entre 7 y 8 puntos cada uno: la diferencia entre ellos es menor que lo que mueve una revisión del PIB, así que el orden entre Calderón, Peña Nieto y López Obrador no es concluyente.' },
    { r: 'deuda', tipo: 'pres', q: 'En pesos, ¿con quién creció más rápido la deuda, segundo a segundo?',
      tit: 'Lo que creció la deuda por segundo, pesos corrientes', fmtv: 'pesos', est: 'derivado',
      datos: function () { return datosDe('mIni', porSegundo); },
      fuera: function () { return ['<b>Salinas y Zedillo</b>: el SHRFSP en pesos empieza en 2000.']; },
      op: 'SHRFSP al cierre del sexenio menos el del cierre anterior, en millones de pesos corrientes, dividido entre los segundos de sus seis años.',
      fs: ['ASF_IR2012', 'ASF_IGE2018', 'ASF_IGE2022', 'SHCP_C4_2025'],
      leccion: 'En pesos corrientes el último siempre parece el peor: la inflación y el tamaño de la economía inflan la cifra con los años. Por eso la deuda se compara en % del PIB, como en la pregunta anterior. Esta cifra sirve para dimensionar, no para calificar.' },
    { r: 'fisc', tipo: 'pres', q: '¿A qué sexenio le practicó más auditorías la Auditoría Superior?',
      tit: 'Auditorías de la ASF a las Cuentas Públicas del sexenio', fmtv: 'ent', est: 'derivado',
      datos: function () { return datosDe('aud'); }, fuera: function () { return fuera('aud'); },
      op: 'Suma de las auditorías practicadas a cada Cuenta Pública del sexenio.',
      fs: ['ASF_IGE2018', 'ASF_MDB'],
      leccion: 'Más auditorías no significa más corrupción: significa más revisión. El número creció casi cada año desde que nació la ASF, en 2000.' },
    { r: 'fisc', tipo: 'pres', q: '¿De qué sexenio se ha recuperado más dinero gracias a las auditorías?',
      tit: 'Recuperaciones operadas, millones de pesos (corte al 31 de enero de 2024)', fmtv: 'mdp', est: 'derivado',
      datos: function () { return datosDe('rec'); }, fuera: function () { return fuera('rec'); },
      op: 'Suma de las recuperaciones operadas de las Cuentas Públicas del sexenio.',
      fs: ['ASF_IGE2022'],
      leccion: 'Una Cuenta Pública vieja ha tenido más años para devolver dinero, así que las recientes se ven chicas. Comparar sexenios con esta cifra favorece a los antiguos.' },
    { r: 'fisc', tipo: 'lista', q: '¿En qué Cuenta Pública dejó la Auditoría Superior más dinero por aclarar?',
      tit: 'Monto por aclarar en cada Cuenta Pública, millones de pesos', fmtv: 'mdp', est: 'oficial',
      datos: function () {
        return POR_ACLARAR.map(function (r) {
          return { id: 'cp' + r.cp, et: 'CP ' + r.cp, sub: r.cp === 2024 ? 'López Obrador y Sheinbaum' : 'López Obrador', col: '#b3261e', v: r.v };
        });
      },
      fuera: function () { return ['<b>Antes de 2019</b>: la ASF usaba otros conceptos que no se suman con este.']; },
      op: 'Renglón Total de la Matriz de Datos Básicos de cada Cuenta Pública.',
      fs: ['ASF_MDB'],
      leccion: 'Un monto por aclarar no es un desfalco comprobado: es dinero cuyo uso no se acreditó al cierre de la auditoría y puede solventarse después.' }
  ];

  /* ---------- Estado ---------- */
  var st = { fase: 'inicio', i: 0, resp: [], reloj: false, restante: 0, timer: null, contado: false, cuentas: false, vivo: null, t0: 0 };
  var SEG_PREGUNTA = 20;

  function ganador(q, datos) {
    if (q.correcta) return opcionesDe(q).filter(function (o) { return o.id === q.correcta; })[0];
    return datos.reduce(function (a, b) { return b.v > a.v ? b : a; });
  }
  function opcionesDe(q) { return q.opciones ? q.opciones() : q.datos(); }

  /* ---------- Pintar ---------- */
  function pintar() {
    if (st.fase === 'inicio') return pintarInicio();
    if (st.fase === 'pregunta') return pintarPregunta();
    return pintarFinal();
  }

  function pintarInicio() {
    var porRonda = RONDAS.map(function (r) {
      var n = PREGUNTAS.filter(function (q) { return q.r === r.k; }).length;
      return '<li><span aria-hidden="true">' + r.ico + '</span> <b>' + r.et + '</b> · ' + n + (n === 1 ? ' pregunta' : ' preguntas') + '</li>';
    }).join('');
    raiz.innerHTML =
      '<div class="tp-inicio">' +
        '<div class="tp-inicio-tx">' +
          '<span class="tp-et">🎯 Trivia · ' + PREGUNTAS.length + ' preguntas</span>' +
          '<h3 class="tp-tit">El examen de los presidentes</h3>' +
          '<p>Empieza en el Porfiriato y sigue con seis sexenios, de Carlos Salinas a Andrés Manuel López Obrador. Primero adivina; después mira la gráfica con la cifra oficial y su fuente. ' +
            'Al terminar verás tu calificación y <b>el estado de cuenta de cada presidente</b>: cuánto creció la economía, cuánta deuda recibió y entregó, y a qué velocidad, por segundo, creció la deuda en su sexenio.</p>' +
          '<ul class="tp-rondas">' + porRonda + '</ul>' +
          '<p class="tp-nota">Claudia Sheinbaum no entra: su sexenio está en curso.</p>' +
        '</div>' +
        '<div class="tp-inicio-mandos">' +
          '<button type="button" class="tp-reloj-sw" aria-pressed="' + st.reloj + '">⏱️ Contra reloj: ' + SEG_PREGUNTA + ' segundos por pregunta <span class="tp-sw" aria-hidden="true"></span></button>' +
          '<button type="button" class="tp-btn tp-empezar">▶️ Empezar el examen</button>' +
        '</div>' +
      '</div>';
    raiz.querySelector('.tp-reloj-sw').addEventListener('click', function () {
      st.reloj = !st.reloj;
      this.setAttribute('aria-pressed', String(st.reloj));
    });
    raiz.querySelector('.tp-empezar').addEventListener('click', function () {
      st.fase = 'pregunta'; st.i = 0; st.resp = []; st.contado = false;
      pintar();
      enfocar();
    });
  }

  function barras(q, datos, gana, contado) {
    var vals = datos.map(function (d) { return Math.abs(d.v); });
    var max = Math.max.apply(null, vals) || 1;
    var orden = q.natural ? datos : datos.slice().sort(function (a, b) { return b.v - a.v; });
    return '<ol class="tp-barras">' + orden.map(function (d) {
      var w = (Math.abs(d.v) / max * 100).toFixed(1);
      return '<li class="tp-fila' + (d.id === gana.id || (q.correcta && d.id === q.correcta) ? ' tp-gana' : '') + (d.v < 0 ? ' tp-neg' : '') + '">' +
        '<span class="tp-nom"><b>' + esc(d.et) + '</b><small>' + esc(d.sub) + '</small></span>' +
        '<span class="tp-riel"><span class="tp-barra" style="background:' + d.col + ';width:' + (contado ? w : 0) + '%" data-w="' + w + '"></span></span>' +
        '<span class="tp-val" data-v="' + d.v + '">' + (contado ? fmt(d.v, q.fmtv) : fmt(0, q.fmtv)) + '</span>' +
      '</li>';
    }).join('') + '</ol>';
  }

  function pintarPregunta() {
    var q = PREGUNTAS[st.i];
    var r = RONDAS.filter(function (x) { return x.k === q.r; })[0];
    var datos = q.datos();
    var gana = ganador(q, datos);
    var resp = st.resp[st.i];
    var ops = opcionesDe(q).map(function (d) {
      var cls = 'tp-op';
      if (resp) {
        if (d.id === gana.id) cls += ' correcta';
        else if (resp.id === d.id) cls += ' errada';
      }
      return '<button type="button" class="' + cls + '" style="--tp:' + d.col + '" data-id="' + d.id + '"' + (resp ? ' disabled' : '') + '>' +
        '<b>' + esc(d.et) + '</b><small>' + esc(d.sub) + '</small></button>';
    }).join('');
    var aciertos = st.resp.filter(function (x) { return x && x.ok; }).length;
    var pct = Math.round((st.i + (resp ? 1 : 0)) / PREGUNTAS.length * 100);
    var veredicto = '';
    if (resp) {
      veredicto = '<p class="tp-veredicto ' + (resp.ok ? 'ok' : 'no') + '" role="status">' +
        (resp.ok ? '✓ ¡Correcto! ' : resp.tiempo ? '⏱️ Se acabó el tiempo. ' : '✗ No fue así. ') +
        'La respuesta es <b>' + esc(gana.et) + '</b>.</p>';
    }
    var fueraL = q.fuera();
    var ultima = st.i === PREGUNTAS.length - 1;
    raiz.innerHTML =
      '<div class="tp-cab">' +
        '<span class="tp-et">' + r.ico + ' ' + r.et + ' · Pregunta ' + (st.i + 1) + ' de ' + PREGUNTAS.length + '</span>' +
        '<span class="tp-marcador" aria-live="polite">Aciertos: <b>' + aciertos + '</b></span>' +
        (st.reloj && !resp ? '<span class="tp-crono" aria-live="off"><span class="tp-crono-n">' + st.restante + '</span> s</span>' : '') +
      '</div>' +
      '<div class="tp-progreso" aria-hidden="true"><span style="width:' + pct + '%"></span></div>' +
      '<h3 class="tp-q" tabindex="-1">' + esc(q.q) + '</h3>' +
      '<div class="tp-ops">' + ops + '</div>' +
      veredicto +
      (resp ?
        '<div class="tp-res">' +
          '<div class="tp-res-cab"><h4>' + esc(q.tit) + '</h4>' +
            '<button type="button" class="tp-btn tp-btn-sec tp-contar">' + (st.contado ? '↺ Reiniciar a ceros' : '▶️ Contabilizar') + '</button></div>' +
          barras(q, datos, gana, st.contado) +
          (fueraL.length ? '<ul class="tp-fuera">' + fueraL.map(function (t) { return '<li>' + t + '</li>'; }).join('') + '</ul>' : '') +
          '<p class="tp-leccion"><b>Para leerlo bien.</b> ' + esc(q.leccion) + '</p>' +
          '<p class="tp-fuente">' + chip(q.est) + ' ' + esc(q.op) + ' Fuentes: ' + fuentes(q.fs) + '.</p>' +
          '<div class="tp-sig"><button type="button" class="tp-btn tp-siguiente">' + (ultima ? '🏁 Ver mi resultado' : 'Siguiente pregunta →') + '</button></div>' +
        '</div>' : '');

    Array.prototype.forEach.call(raiz.querySelectorAll('.tp-op'), function (b) {
      b.addEventListener('click', function () { responder(b.getAttribute('data-id'), false); });
    });
    var c = raiz.querySelector('.tp-contar');
    if (c) c.addEventListener('click', function () {
      if (st.contado) { st.contado = false; pintar(); } else contar();
    });
    var s = raiz.querySelector('.tp-siguiente');
    if (s) s.addEventListener('click', function () {
      st.contado = false;
      if (ultima) { st.fase = 'final'; st.cuentas = false; }
      else st.i++;
      pintar();
      enfocar();
    });
    if (!resp && st.reloj) arrancarCrono();
  }

  function enfocar() {
    var h = raiz.querySelector('.tp-q, .tp-final-tit');
    var cab = document.querySelector('.site-top-nav');
    var alto = cab ? cab.getBoundingClientRect().height : 0;
    var top = raiz.getBoundingClientRect().top;
    if (top < alto || top > window.innerHeight * 0.5) window.scrollTo({ top: Math.max(0, top + window.pageYOffset - alto - 12), behavior: reduce ? 'auto' : 'smooth' });
    if (h) h.focus({ preventScroll: true });
  }

  function arrancarCrono() {
    pararCrono();
    st.restante = SEG_PREGUNTA;
    var n = raiz.querySelector('.tp-crono-n');
    if (n) n.textContent = st.restante;
    st.timer = setInterval(function () {
      st.restante--;
      var e = raiz.querySelector('.tp-crono-n');
      if (e) e.textContent = Math.max(0, st.restante);
      var cr = raiz.querySelector('.tp-crono');
      if (cr) cr.classList.toggle('tp-urge', st.restante <= 5);
      if (st.restante <= 0) { pararCrono(); responder(null, true); }
    }, 1000);
  }
  function pararCrono() { if (st.timer) { clearInterval(st.timer); st.timer = null; } }

  function responder(id, tiempo) {
    if (st.resp[st.i]) return;
    pararCrono();
    var q = PREGUNTAS[st.i];
    var gana = ganador(q, q.datos());
    st.resp[st.i] = { id: id, ok: id === gana.id, tiempo: !!tiempo };
    st.contado = false;
    pintar();
    var v = raiz.querySelector('.tp-veredicto');
    if (v) v.focus && v.setAttribute('tabindex', '-1');
  }

  /* Las barras y sus cifras suben de cero a su valor. */
  function animar(zona, fmtDe, ms, fin) {
    var bs = zona.querySelectorAll('[data-w]'), vs = zona.querySelectorAll('[data-v]');
    if (reduce) {
      Array.prototype.forEach.call(bs, function (b) { b.style.width = b.getAttribute('data-w') + '%'; });
      Array.prototype.forEach.call(vs, function (e) { e.textContent = fmtDe(e, +e.getAttribute('data-v')); });
      if (fin) fin();
      return;
    }
    Array.prototype.forEach.call(bs, function (b) { b.style.transition = 'width ' + ms + 'ms ease-out'; });
    requestAnimationFrame(function () {
      Array.prototype.forEach.call(bs, function (b) { b.style.width = b.getAttribute('data-w') + '%'; });
    });
    var t0 = performance.now();
    (function paso(t) {
      var k = Math.min(1, (t - t0) / ms);
      var e = 1 - Math.pow(1 - k, 3);
      Array.prototype.forEach.call(vs, function (el) { el.textContent = fmtDe(el, +el.getAttribute('data-v') * e); });
      if (k < 1) requestAnimationFrame(paso); else if (fin) fin();
    })(t0);
  }

  function contar() {
    st.contado = true;
    var q = PREGUNTAS[st.i];
    var b = raiz.querySelector('.tp-contar');
    if (b) b.textContent = '↺ Reiniciar a ceros';
    animar(raiz.querySelector('.tp-barras'), function (el, v) { return fmt(v, q.fmtv); }, 1400);
  }

  /* ---------- Final: calificación y estados de cuenta ---------- */
  function nivel(a, n) {
    var p = a / n;
    if (p === 1) return ['🏆', 'Auditor de excelencia', 'No se te escapó ni una cifra.'];
    if (p >= 0.75) return ['🥇', 'Auditor ciudadano', 'Lees las cifras públicas mejor que la mayoría.'];
    if (p >= 0.5) return ['🥈', 'Contralor en formación', 'Vas bien: revisa las lecciones de las que fallaste.'];
    return ['📘', 'Aprendiz de la cuenta pública', 'Las cifras sorprenden a casi todos. Vuelve a intentarlo con lo que aprendiste.'];
  }

  function renglon(ico, et, v, fmtv, est, f, nota, signo) {
    var sin = typeof v !== 'number';
    return '<li class="tp-ec-r' + (signo ? ' tp-ec-' + signo : '') + '">' +
      '<span class="tp-ec-et"><span aria-hidden="true">' + ico + '</span> ' + et + '</span>' +
      '<span class="tp-ec-v"' + (sin ? '' : ' data-v="' + v + '" data-f="' + fmtv + '"') + '>' + (sin ? chip('pendiente') : (st.cuentas ? fmt(v, fmtv) : fmt(0, fmtv))) + '</span>' +
      (nota || f ? '<span class="tp-ec-n">' + (sin ? '' : chip(est) + ' ') + (nota ? esc(nota) + ' ' : '') + (f ? fuente(f) : '') + '</span>' : '') +
    '</li>';
  }

  function estadoCuenta(p) {
    var d = D[p.id];
    var dd = d.dIni && d.dFin ? Math.round((d.dFin.v - d.dIni.v) * 10) / 10 : null;
    var dm = d.mIni && d.mFin ? d.mFin.v - d.mIni.v : null;
    var ps = porSegundo(p.id);
    var filas = [
      renglon('📈', 'Crecimiento de la economía, promedio anual', d.pib.v, 'pct2', 'derivado', d.pib.f, d.pib.nota),
      renglon('👷', 'Empleo formal creado (IMSS)', d.emp.v, 'ent', 'derivado', d.emp.f, d.emp.pend),
      renglon('🏦', 'Deuda que recibió, % del PIB', d.dIni ? d.dIni.v : null, 'pct', 'oficial', d.dIni && d.dIni.f, d.dIni ? '' : 'Antes de 2000 no hay SHRFSP comparable.'),
      renglon('🏦', 'Deuda que entregó, % del PIB', d.dFin.v, 'pct', 'oficial', d.dFin.f, d.dFin.nota),
      renglon('💳', 'Cambio de la deuda en su sexenio', dd, 'pp', 'derivado', null, dd === null ? 'Sin dos cifras del mismo indicador.' : 'Lo que entregó menos lo que recibió.', dd === null ? '' : dd > 0 ? 'menos' : 'mas'),
      renglon('💸', 'Deuda nueva en pesos corrientes', dm, 'bill', 'derivado', d.mFin && d.mFin.f, dm === null ? 'El SHRFSP en pesos empieza en 2000.' : 'SHRFSP al entregar menos el que recibió.', dm === null ? '' : 'menos'),
      renglon('🧾', 'Ingresos, gasto e inversión del sexenio', null, '', 'pendiente', null, 'Sin serie oficial completa y consistente de 1989 a 2024: la ASF publica el déficit amplio por año desde 2010 y sus cuadros no siempre coinciden entre sí. No se estima.'),
      renglon('🔎', 'Auditorías de la ASF a su gasto', d.aud.v, 'ent', 'derivado', d.aud.f, d.aud.nota || d.aud.na || d.aud.pend),
      renglon('💰', 'Recuperado por las auditorías', d.rec.v, 'mdp', 'derivado', d.rec.f, d.rec.nota || d.rec.na || d.rec.pend)
    ].join('');
    var saldo = dd === null
      ? '<p class="tp-ec-saldo tp-ec-saldo-sin">Saldo de deuda: sin dos cifras comparables.</p>'
      : '<p class="tp-ec-saldo ' + (dd > 0 ? 'menos' : 'mas') + '"><span>Saldo de deuda del sexenio</span><b data-v="' + dd + '" data-f="pp">' + (st.cuentas ? fmt(dd, 'pp') : fmt(0, 'pp')) + '</b><small>del PIB</small></p>';
    var reloj = ps === null ? '' :
      '<div class="tp-ec-reloj"><span class="tp-ec-reloj-et">⏱️ Reloj de su deuda</span>' +
        '<b>' + fmt(ps, 'pesos') + ' por segundo</b>' +
        '<span class="tp-ec-reloj-vivo">Desde que abriste tu resultado, a ese ritmo: <b data-ps="' + ps + '">$0</b></span></div>';
    return '<article class="tp-ec" style="--tp:' + p.col + '">' +
      '<header class="tp-ec-cab"><b>' + esc(p.n) + '</b><span>' + p.a[0] + '–' + p.a[1] + '</span></header>' +
      '<ul class="tp-ec-lista">' + filas + '</ul>' + saldo + reloj +
    '</article>';
  }

  function pintarFinal() {
    pararCrono();
    var aciertos = st.resp.filter(function (x) { return x && x.ok; }).length;
    var nv = nivel(aciertos, PREGUNTAS.length);
    var porRonda = RONDAS.map(function (r) {
      var idx = [];
      PREGUNTAS.forEach(function (q, i) { if (q.r === r.k) idx.push(i); });
      var ok = idx.filter(function (i) { return st.resp[i] && st.resp[i].ok; }).length;
      return '<li><span aria-hidden="true">' + r.ico + '</span> ' + r.et + ': <b>' + ok + ' de ' + idx.length + '</b></li>';
    }).join('');
    raiz.innerHTML =
      '<div class="tp-final">' +
        '<div class="tp-cal">' +
          '<span class="tp-cal-ico" aria-hidden="true">' + nv[0] + '</span>' +
          '<div><h3 class="tp-final-tit" tabindex="-1">' + aciertos + ' de ' + PREGUNTAS.length + ' · ' + nv[1] + '</h3>' +
            '<p>' + nv[2] + (st.reloj ? ' Lo hiciste contra reloj.' : '') + '</p>' +
            '<ul class="tp-cal-rondas">' + porRonda + '</ul></div>' +
          '<button type="button" class="tp-btn tp-btn-sec tp-otra">↺ Volver a empezar</button>' +
        '</div>' +
        '<div class="tp-ec-cab-gral">' +
          '<div><h3>El estado de cuenta de cada presidente</h3>' +
            '<p>Todo lo que respondiste, junto, sexenio por sexenio. Pulsa «Contabilizar» y mira subir cada renglón desde cero. ' +
            'En rojo, lo que suma a la deuda; en verde, lo que la bajó. Los relojes corren al ritmo al que creció la deuda en cada sexenio.</p></div>' +
          '<button type="button" class="tp-btn tp-cuentas">' + (st.cuentas ? '↺ Reiniciar a ceros' : '▶️ Contabilizar') + '</button>' +
        '</div>' +
        '<div class="tp-ec-rejilla">' + P.map(estadoCuenta).join('') + porfiriato() + '</div>' +
        correcciones() +
        '<p class="tp-fuente">' + chip('oficial') + ' ' + chip('derivado') + ' ' + chip('pendiente') +
          ' Cada renglón trae su documento. La deuda es el saldo histórico de los requerimientos financieros del sector público (SHRFSP), la medida más amplia que publica Hacienda; los pesos son corrientes de cada año, sin ajustar por inflación. ' +
          'La serie completa, año por año, está en <a href="sigue-el-dinero.html#deuda">Sigue el dinero › Cuánto debemos</a>.</p>' +
      '</div>';
    raiz.querySelector('.tp-otra').addEventListener('click', function () {
      pararVivo();
      st.fase = 'inicio'; st.resp = []; st.cuentas = false;
      pintar(); enfocar();
    });
    raiz.querySelector('.tp-cuentas').addEventListener('click', function () {
      if (st.cuentas) { st.cuentas = false; pararVivo(); pintar(); return; }
      st.cuentas = true;
      this.textContent = '↺ Reiniciar a ceros';
      animar(raiz.querySelector('.tp-ec-rejilla'), function (el, v) { return fmt(v, el.getAttribute('data-f')); }, 1600);
    });
    arrancarVivo();
  }

  /* El Porfiriato no se mide con los mismos indicadores: va como
     referencia, con sus propias cifras del INEGI. */
  function porfiriato() {
    var b0 = PORF.balance[0], b1 = PORF.balance[PORF.balance.length - 1];
    var filas = [
      renglon('🛤️', 'Vía férrea en 1876', PORF.vias[0][1], 'km', 'oficial', 'EHM_VIAS'),
      renglon('🛤️', 'Vía férrea en 1910', PORF.vias[PORF.vias.length - 1][1], 'km', 'oficial', 'EHM_VIAS'),
      renglon('⚖️', 'Balance federal ' + b0[0], b0[1], 'mill', 'oficial', 'EHM_BAL', null, 'menos'),
      renglon('⚖️', 'Balance federal ' + b1[0], b1[1], 'mill', 'oficial', 'EHM_BAL', 'Superávit cada año desde 1895-96.', 'mas'),
      renglon('📖', 'Analfabetismo en 1895', PORF.analfabetas[0][1], 'pct', 'oficial', 'EHM_ALF'),
      renglon('📖', 'Analfabetismo en 1910', PORF.analfabetas[2][1], 'pct', 'oficial', 'EHM_ALF'),
      renglon('🏦', 'Deuda como % del PIB', null, '', 'pendiente', null, 'No hay PIB oficial del periodo comparable con el de hoy.')
    ].join('');
    return '<article class="tp-ec tp-ec-porf" style="--tp:' + ORO + '">' +
      '<header class="tp-ec-cab"><b>Porfirio Díaz</b><span>1876–1911 · para comparar</span></header>' +
      '<ul class="tp-ec-lista">' + filas + '</ul>' +
      '<p class="tp-ec-saldo tp-ec-saldo-sin">Pesos de la época y años fiscales de julio a junio: no se suman ni se comparan con los de los sexenios.</p>' +
    '</article>';
  }

  /* Lo que la verificación cambió respecto de las cifras que circulan
     (y que la Enciclopedia todavía muestra). */
  function correcciones() {
    return '<details class="tp-corr"><summary>🔍 Lo que corregimos al verificar el Porfiriato</summary>' +
      '<p>Cotejamos contra las <i>Estadísticas históricas de México 2014</i> del INEGI las cifras del Porfiriato que se repiten en redes, en blogs y en la propia Enciclopedia de esta plataforma, que está congelada y no se modificó:</p>' +
      '<ul>' +
        '<li><b>«El primer superávit fue el de 1894-1895, por $19,861».</b> El INEGI registra para ese año un déficit de $1.2 millones; la racha de superávits empieza en 1895-1896. No encontramos el documento que sostenga los $19,861: queda ' + chip('pendiente') + ' hasta revisar la Memoria de Hacienda de ese año.</li>' +
        '<li><b>«19,280 km de vía en 1910».</b> El INEGI da 19,748 km; y 617 en 1876, no 640.</li>' +
        '<li><b>«52% de los ingresos venía de las aduanas».</b> En 1894-1895 fue 45.2%; el máximo, 66.8%, fue en 1877-1878 (derivado del cuadro 16.6).</li>' +
        '<li><b>«Ingresos de 8.2%, gasto de 7.4%, deuda de 30.5% y superávit de 0.8% del PIB».</b> No encontramos fuente oficial para ninguna; por eso no aparecen aquí.</li>' +
      '</ul></details>';
  }

  /* Los relojes del estado de cuenta: corren desde que se abre el
     resultado, cada uno al ritmo de su sexenio. */
  function arrancarVivo() {
    pararVivo();
    st.t0 = performance.now();
    var els = raiz.querySelectorAll('[data-ps]');
    if (!els.length) return;
    st.vivo = setInterval(function () {
      var s = (performance.now() - st.t0) / 1000;
      Array.prototype.forEach.call(els, function (e) { e.textContent = fmt(+e.getAttribute('data-ps') * s, 'pesos'); });
    }, reduce ? 1000 : 100);
  }
  function pararVivo() { if (st.vivo) { clearInterval(st.vivo); st.vivo = null; } }

  pintar();
})();
