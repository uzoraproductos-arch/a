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

   Rondas de la balanza (09-10-2026): los rubros del tablero 5.4 de la
   Enciclopedia («Versus General Don Porfirio Díaz»: balance, deuda,
   aduanas, rieles y Sheinbaum) se volvieron preguntas. La Enciclopedia
   está congelada y marca ese tablero «en revisión, sin fuente», así que
   no se copió ninguna de sus cifras: cada una se rehízo con el INEGI
   (Estadísticas históricas de México 2014) y con Hacienda (Criterios
   Generales de Política Económica 2027). Lo que no se encontró se dice en
   correcciones().
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
    EHM_ALF: { corto: 'INEGI, Estadísticas históricas de México 2014, cuadro 3.7 (p. 24 del PDF)', url: 'https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/HyM2014/3.%20Educacion.pdf' },
    EHM_BAL_XIX: { corto: 'INEGI, Estadísticas históricas de México 2014, cuadro 16.3 (pp. 10 y 11 del PDF)', url: 'https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/HyM2014/16.%20Finanzas%20publicas.pdf' },
    EHM_FUENTES: { corto: 'INEGI, Estadísticas históricas de México 2014, cuadro 16.5 (p. 14 del PDF)', url: 'https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/HyM2014/16.%20Finanzas%20publicas.pdf' },
    EHM_DEUDA: { corto: 'INEGI, Estadísticas históricas de México 2014, cuadro 16.16 (p. 48 del PDF)', url: 'https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/HyM2014/16.%20Finanzas%20publicas.pdf' },
    EHM_VIAS_SIGLO: { corto: 'INEGI, Estadísticas históricas de México 2014, cuadro 14.18 (pp. 45 a 47 del PDF)', url: 'https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/HyM2014/14.%20Transportes%20y%20comunicaciones.pdf' },
    CGPE2027_IG: { corto: 'SHCP, Criterios Generales de Política Económica 2027, cuadro «Ingresos y gasto del Sector Público» (p. 56 del PDF)', url: 'https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-C.pdf' }
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

  /* ---------- La balanza: siglo XIX y hoy ---------- */
  /* Cuadro 16.3: balance del gobierno federal, millones de pesos de cada
     año fiscal, de 1823 a 1845 (falta 1832-1833: no hay egresos). Cuadro
     16.16: deuda total del gobierno federal, miles de pesos, en los años
     que tienen total. Cuadro 14.18: pasajeros por ferrocarril y kilómetros
     de vía. CGPE 2027: ingresos y gasto del sector público, % del PIB. */
  var SANTA = '#7a5a2e', JUAREZ = '#1f5f8b', SHEIN = '#0f7f7a', GRIS = '#7a8aa8';
  var XIX = {
    balance: [['1823', -1.6], ['1825', -5.2, 'ocho meses'], ['1825-26', -1.2, 'diez meses'], ['1826-27', -1.2], ['1827-28', -0.6], ['1828-29', -1.2],
      ['1829-30', -2.2], ['1830-31', -3.1], ['1831-32', -3.9], ['1833-34', -7.1], ['1835-36', -11.1], ['1836-37', 0.9],
      ['1837-38', -1.5, 'dieciocho meses'], ['1839', 1.8], ['1840', 0.0], ['1841', 1.0], ['1842', 0.1], ['1843', 0.1], ['1844', -9.5], ['1845', 0.8]],
    deuda: [[1837, 128240], [1846, 138708], [1850, 126208], [1852, 98144], [1856, 109583], [1861, 75208], [1870, 120000],
      [1890, 126951], [1893, 222132], [1900, 373420], [1903, 446992], [1911, 589686]],
    pasajeros: [[1988, 18487000], [1991, 14901000], [1994, 7189000], [1997, 5092000], [1998, 1576000], [1999, 801000],
      [2000, 334000], [2006, 261000], [2008, 8915000], [2012, 43830000]],
    km: [[1876, 617], [1884, 5742], [1890, 9540], [1900, 13301], [1910, 19748], [1930, 23345], [1950, 23332], [1970, 24468], [1990, 26360], [2012, 26727]]
  };
  var HOY = {
    balance: [[2020, -2.7], [2021, -2.9], [2022, -3.2], [2023, -3.4], [2024, -5.0], [2025, -3.9]],
    ingresos2025: [['isr', 'ISR', 'Impuesto sobre la renta', 8.2], ['iva', 'IVA', 'Impuesto al valor agregado', 4.2], ['ieps', 'IEPS', 'Impuesto especial (gasolinas, tabaco, bebidas…)', 1.9],
      ['imp', 'Importación', 'Impuestos al comercio exterior', 0.5], ['otros', 'Otros impuestos', '', 0.3], ['notrib', 'No tributarios', 'Cuotas del IMSS e ISSSTE, ventas de la CFE, derechos', 4.7], ['petro', 'Petroleros', 'Gobierno federal y Pemex', 3.5]],
    gasto2025: [['sp', 'Servicios personales', 'Sueldos del sector público', 5.1], ['pens', 'Pensiones y jubilaciones', '', 4.6], ['part', 'Participaciones', 'Lo que se reparte a estados y municipios', 3.8],
      ['cf', 'Costo financiero', 'Intereses y comisiones de la deuda', 3.7], ['sub', 'Subsidios', '', 2.8], ['inv', 'Inversión física', 'Obra pública y equipamiento', 2.2]],
    deuda: [[2000, 30.7, 'zedillo'], [2006, 29.1, 'fox'], [2012, 37.2, 'calderon'], [2018, 44.9, 'epn'], [2020, 50.2, 'amlo'], [2024, 51.9, 'amlo'], [2025, 52.6, 'sheinbaum']]
  };
  function colorDe(id) { var p = pres(id); return id === 'sheinbaum' ? SHEIN : p ? p.col : GRIS; }
  function opcionesLista(l, col) { return l.map(function (o) { return { id: o[0], et: o[1], sub: o[2] || '', col: o[3] || col || ORO }; }); }

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
    if (f === 'pib') return (v < 0 ? '−' : '') + num(Math.abs(v), 1) + '% del PIB';
    return String(v);
  }
  /* Rótulos cortos de la gráfica lineal: la unidad va en el título. */
  function corto(v, f) {
    var s = v < 0 ? '−' : '', a = Math.abs(v);
    if (f === 'ent') return s + (a >= 1e6 ? num(a / 1e6, 1) + ' M' : a >= 1e3 ? num(a / 1e3, 0) + ' mil' : num(Math.round(a), 0));
    if (f === 'km') return s + num(Math.round(a), 0);
    if (f === 'pct2') return s + num(a, 2);
    return s + num(a, 1);
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
    { k: 'balanza', et: 'La gran balanza: Santa Anna, Juárez y Díaz', ico: '⚖️' },
    { k: 'rieles', et: 'Los rieles, de 1876 a 2012', ico: '🛤️' },
    { k: 'eco', et: 'La economía', ico: '📈' },
    { k: 'deuda', et: 'La deuda', ico: '💳' },
    { k: 'fisc', et: 'La fiscalización', ico: '🔎' },
    { k: 'hoy', et: 'Hoy: el primer año de Claudia Sheinbaum', ico: '🇲🇽' }
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
    { r: 'balanza', tipo: 'lista', serie: true, q: 'Se repite que el primer superávit de México fue el de Limantour. Según el INEGI, ¿en qué año fiscal cerró con superávit el gobierno federal por primera vez?',
      tit: 'Balance del gobierno federal, 1823 a 1845, millones de pesos de la época', fmtv: 'mill', est: 'oficial', natural: true, correcta: 'x1836-37',
      opciones: function () { return opcionesLista([['x1836-37', '1836-1837', 'años de Santa Anna'], ['j1867-68', '1867-1868', 'Juárez'], ['p1894-95', '1894-1895', 'Díaz y Limantour'], ['p1895-96', '1895-1896', 'Díaz y Limantour']]); },
      datos: function () { return XIX.balance.map(function (r) { return { id: 'x' + r[0], et: r[0], sub: r[2] || '', col: r[1] < 0 ? '#b3261e' : '#23855a', v: r[1] }; }); },
      fuera: function () { return ['<b>1832-1833 y 1834-1835</b>: el cuadro no tiene los egresos de esos años, así que no se sabe cómo cerraron.']; },
      op: 'Ingresos efectivos menos egresos ejercidos de cada año fiscal, como los publica el INEGI.',
      fs: ['EHM_BAL_XIX'],
      leccion: 'El primer superávit que registra el INEGI es el de 1836-1837: $0.9 millones. Hubo más en 1839, 1841, 1842, 1843 y 1845, y con Juárez cerraron con superávit cuatro de los cinco años fiscales de 1867 a 1872. Lo que sí distingue al Porfiriato es la racha: 16 años seguidos con superávit, de 1895-1896 a 1910-1911. Santa Anna entró y salió de la presidencia muchas veces en esos años: las cifras son del gobierno federal de cada año, no de un solo mandatario.' },
    { r: 'balanza', tipo: 'lista', q: 'Midiendo el déficit contra lo que entraba a la caja, ¿en qué época fue más grande el hoyo?',
      tit: 'Déficit del año contra los ingresos del mismo año, por ciento', fmtv: 'pct', est: 'derivado', correcta: 'di',
      opciones: function () { return opcionesLista([['sa', 'Santa Anna', '1835-1836', SANTA], ['ju', 'Juárez', '1868-1869', JUAREZ], ['di', 'Porfirio Díaz', '1888-1889', ORO], ['am', 'López Obrador', '2024', colorDe('amlo')]]); },
      datos: function () {
        return [['sa', 'Santa Anna', '1835-1836', SANTA, 80.4], ['ju', 'Juárez', '1868-1869', JUAREZ, 57.3], ['di', 'Porfirio Díaz', '1888-1889', ORO, 114.8],
          ['di2', 'Porfirio Díaz', '1889-1890', ORO, 102.6], ['am', 'López Obrador', '2024', colorDe('amlo'), 22.4], ['sh', 'Sheinbaum', '2025', SHEIN, 16.7]]
          .map(function (r) { return { id: r[0], et: r[1], sub: r[2], col: r[3], v: r[4] }; });
      },
      fuera: function () { return []; },
      op: 'Siglo XIX: déficit del gobierno federal entre sus ingresos efectivos, en pesos de la época (por ejemplo, 39.5 entre 34.4 millones en 1888-1889). 2024 y 2025: balance presupuestario del sector público entre sus ingresos presupuestarios, ambos en % del PIB; esa cobertura es más amplia, así que compara órdenes de magnitud, no décimas.',
      fs: ['EHM_BAL_XIX', 'EHM_BAL', 'CGPE2027_IG'],
      leccion: 'El peor hoyo fue del Porfiriato: en 1888-1889 el gobierno gastó $73.9 millones con ingresos de $34.4; por cada peso que entró, salieron $2.15. Los grandes déficits del régimen son de la década de 1880; la disciplina de Limantour llegó después, de 1895 en adelante. Que un déficit de hoy se vea menor no lo hace pequeño: se mide contra un Estado mucho más grande.' },
    { r: 'balanza', tipo: 'lista', serie: true, q: 'En 1870, con Juárez, la deuda del gobierno federal sumaba $120 millones de pesos. En 1911, cuando Díaz dejó el poder, ¿cuánto sumaba?',
      tit: 'Deuda total del gobierno federal, millones de pesos de la época', fmtv: 'mill', est: 'oficial', natural: true, correcta: 'o4',
      opciones: function () { return opcionesLista([['o1', 'Unos $60 millones', 'la redujo a la mitad'], ['o2', 'Unos $120 millones', 'la dejó igual'], ['o3', 'Unos $250 millones', 'la duplicó'], ['o4', 'Casi $590 millones', 'casi cinco veces más']]); },
      datos: function () { return XIX.deuda.map(function (r) { return { id: 'd' + r[0], et: String(r[0]), sub: '', col: r[0] >= 1876 ? ORO : r[0] >= 1858 ? JUAREZ : SANTA, v: r[1] / 1000 }; }); },
      fuera: function () { return ['<b>1876 a 1889</b>: el cuadro solo trae la deuda externa, y de 1886 a 1888 en libras esterlinas; no se suman aquí.', '<b>Sin PIB oficial de la época</b>: se sabe cuánto se debía, no qué tanto pesaba en la economía.']; },
      op: 'Deuda interna más externa del gobierno federal, en los años que el cuadro trae completos. «Casi cinco veces» es 589.7 entre 120.0 millones (derivado).',
      fs: ['EHM_DEUDA'],
      leccion: 'En pesos, Díaz entregó casi cinco veces la deuda de 1870, y la externa pasó de $52.5 millones en 1890 a $453.0 millones en 1911. El tablero de la Enciclopedia dice que la deuda porfiriana era de 30.5% del PIB: no encontramos documento oficial que lo sostenga. Ordenar las finanzas no es lo mismo que dejar de deber.' },
    { r: 'balanza', tipo: 'pres', q: '¿En qué época dependía más el gobierno de lo que cobraba en las aduanas?',
      tit: 'Impuestos al comercio exterior, por ciento de los ingresos', fmtv: 'pct', est: 'derivado',
      datos: function () {
        return [['sa', 'Santa Anna', '1833-1834', SANTA, 76.3], ['ju', 'Juárez', '1870-1871', JUAREZ, 67.9], ['di', 'Porfirio Díaz', '1894-1895', ORO, 45.2], ['sh', 'Sheinbaum', '2025', SHEIN, 2.1]]
          .map(function (r) { return { id: r[0], et: r[1], sub: r[2], col: r[3], v: r[4] }; });
      },
      fuera: function () { return []; },
      op: 'Impuestos al comercio exterior entre ingresos totales de cada año (8,786,396 entre 11,512,969 pesos en 1833-1834; 10,884,953 entre 16,033,649 en 1870-1871; 19,871 entre 43,946 miles en 1894-1895). 2025: impuestos a la importación entre ingresos presupuestarios del sector público, 0.5 entre 23.3% del PIB; con cifras redondeadas a un decimal, el resultado puede moverse unas décimas.',
      fs: ['EHM_FUENTES', 'EHM_ING', 'CGPE2027_IG'],
      leccion: 'Durante el siglo XIX el Estado vivió de las aduanas: tres de cada cuatro pesos en la época de Santa Anna, dos de cada tres con Juárez, casi la mitad con Díaz. Por eso el tablero marca «0% de ISR» para el Porfiriato: el impuesto sobre la renta todavía no existía. Hoy las aduanas aportan dos de cada cien pesos; el dinero sale del ingreso y del consumo de la gente.' },
    { r: 'rieles', tipo: 'lista', serie: true, q: 'Con la privatización de los ferrocarriles, a finales de los noventa, ¿qué se desplomó?',
      tit: 'Pasajeros transportados por ferrocarril en el año', fmtv: 'ent', est: 'oficial', natural: true, correcta: 'r2',
      opciones: function () { return opcionesLista([['r1', 'Los kilómetros de vía', 'se levantó la red'], ['r2', 'Los pasajeros', 'el tren dejó de llevar gente'], ['r3', 'La carga', 'dejó de moverse mercancía'], ['r4', 'Nada', 'todo siguió creciendo']], GRIS); },
      datos: function () { return XIX.pasajeros.map(function (r) { return { id: 'q' + r[0], et: String(r[0]), sub: r[0] === 2008 ? 'abre el Suburbano' : '', col: r[0] <= 2000 && r[0] >= 1995 ? colorDe('zedillo') : GRIS, v: r[1] }; }); },
      fuera: function () { return []; },
      op: 'Pasajeros transportados cada año. El salto de 2008 se debe a la Línea 1 del Ferrocarril Suburbano del Valle de México, según la nota del propio cuadro.',
      fs: ['EHM_VIAS_SIGLO'],
      leccion: 'Entre 1994 y 2000 los pasajeros cayeron de 7.2 millones a 334 mil: 95% menos. La vía no desapareció: la red pasó de 26,477 a 26,656 km, y la carga subió de 52.1 a 77.2 millones de toneladas. El tablero de la Enciclopedia anota «−19,000 km» para Zedillo; según el INEGI no se perdió ningún kilómetro: se perdió el tren de pasajeros.' },
    { r: 'rieles', tipo: 'lista', serie: true, q: 'De 1910 a 2012, en más de un siglo, ¿cuántos kilómetros de vía férrea se sumaron a la red?',
      tit: 'Kilómetros de vía férrea en operación', fmtv: 'km', est: 'oficial', natural: true, correcta: 'k2',
      opciones: function () { return opcionesLista([['k1', 'Unos 2,000 km', ''], ['k2', 'Unos 7,000 km', ''], ['k3', 'Unos 15,000 km', ''], ['k4', 'Unos 19,000 km', '']]); },
      datos: function () { return XIX.km.map(function (r) { return { id: 'm' + r[0], et: String(r[0]), sub: '', col: r[0] <= 1910 ? ORO : GRIS, v: r[1] }; }); },
      fuera: function () { return ['<b>Después de 2013</b>: el Tren Maya, el Interoceánico y El Insurgente no están en esta serie del INEGI, que termina en 2013. La Agencia Reguladora del Transporte Ferroviario publica su anuario, pero la plataforma aún no lo integra: su kilometraje queda ' + chip('pendiente') + '.']; },
      op: 'Vía principal, secundaria y particular. 26,727 menos 19,748 km son 6,979 km (derivado).',
      fs: ['EHM_VIAS_SIGLO'],
      leccion: 'De 1876 a 1910 se sumaron 19,131 km en 34 años; de 1910 a 2012, 6,979 km en 102 años. La red ferroviaria de hoy es, en lo esencial, la del Porfiriato. Ojo: el tablero de la Enciclopedia dice 19,280 km en 1910; el INEGI da 19,748.' },
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
      leccion: 'Un monto por aclarar no es un desfalco comprobado: es dinero cuyo uso no se acreditó al cierre de la auditoría y puede solventarse después.' },
    { r: 'hoy', tipo: 'lista', serie: true, q: 'En 2025, el primer año completo de Claudia Sheinbaum, ¿cómo cerró el balance del presupuesto del sector público?',
      tit: 'Balance presupuestario del sector público, % del PIB', fmtv: 'pib', est: 'oficial', natural: true, correcta: 'h2025',
      opciones: function () { return opcionesLista([['hs', 'Con superávit', 'entró más de lo que salió'], ['h1', 'Déficit de 1.0% del PIB', ''], ['h2025', 'Déficit de 3.9% del PIB', ''], ['h5', 'Déficit de 5.0% del PIB', '']], SHEIN); },
      datos: function () { return HOY.balance.map(function (r) { return { id: 'h' + r[0], et: String(r[0]), sub: r[0] === 2025 ? 'Sheinbaum' : 'López Obrador', col: r[0] === 2025 ? SHEIN : colorDe('amlo'), v: r[1] }; }); },
      fuera: function () { return ['La medida más amplia, los requerimientos financieros del sector público (RFSP), fue de 4.3% del PIB en 2025 y de 5.8% en 2024.']; },
      op: 'Ingresos presupuestarios menos gasto neto pagado, como proporción del PIB.',
      fs: ['CGPE2027_IG', 'CGPE2027_HIST'],
      leccion: 'El déficit bajó de 5.0% a 3.9% del PIB entre 2024 y 2025: se gastó menos en proporción, pero se siguió gastando más de lo que entró. El tablero de la Enciclopedia pone −3.9% como «meta»; hoy ya es la cifra observada por Hacienda. Ningún año de esta serie tuvo superávit; los del Porfiriato se midieron en pesos, no en % del PIB, así que no caben en la misma regla.' },
    { r: 'hoy', tipo: 'lista', q: 'En 1894-1895 casi la mitad del dinero de Díaz venía de las aduanas. En 2025, ¿de dónde sacó más dinero el sector público?',
      tit: 'Ingresos presupuestarios del sector público en 2025, % del PIB', fmtv: 'pib', est: 'oficial', correcta: 'isr',
      opciones: function () { return opcionesLista([['isr', 'Del ISR', 'impuesto sobre la renta'], ['iva', 'Del IVA', 'impuesto al consumo'], ['petro', 'Del petróleo', 'Pemex y derechos'], ['imp', 'De las aduanas', 'impuestos a la importación']], SHEIN); },
      datos: function () { return HOY.ingresos2025.map(function (r) { return { id: r[0], et: r[1], sub: r[2], col: SHEIN, v: r[3] }; }); },
      fuera: function () { return ['<b>Total</b>: 23.3% del PIB. Las sumas pueden no coincidir por el redondeo, como advierte el propio cuadro.']; },
      op: 'Renglones del cuadro de ingresos de 2025. ISR más IVA son 12.4 de 15.2 puntos de impuestos: 81.6% (derivado).',
      fs: ['CGPE2027_IG'],
      leccion: 'El ISR, que en el Porfiriato no existía, es hoy la mayor fuente de dinero público: 8.2% del PIB. ISR e IVA juntos son el 81.6% de los impuestos, no «más del 88%» como dice el tablero de la Enciclopedia. Y las aduanas, que sostenían al Estado del siglo XIX, aportan 0.5% del PIB.' },
    { r: 'hoy', tipo: 'lista', q: 'En 2025, ¿qué fue mayor: lo que se pagó por la deuda o lo que se invirtió en obra física?',
      tit: 'Algunos renglones del gasto del sector público en 2025, % del PIB', fmtv: 'pib', est: 'oficial', correcta: 'cf',
      opciones: function () { return opcionesLista([['cf', 'Lo que se pagó por la deuda', 'costo financiero'], ['inv', 'La inversión física', 'obra pública'], ['igual', 'Fueron iguales', '']], SHEIN); },
      datos: function () { return HOY.gasto2025.map(function (r) { return { id: r[0], et: r[1], sub: r[2], col: r[0] === 'cf' ? '#b3261e' : r[0] === 'inv' ? '#23855a' : SHEIN, v: r[3] }; }); },
      fuera: function () { return ['<b>Gasto neto pagado total</b>: 27.2% del PIB. La gráfica muestra solo seis renglones.']; },
      op: 'Renglones del cuadro de gasto de 2025. $1.68 por peso es 3.7 entre 2.2 (derivado).',
      fs: ['CGPE2027_IG'],
      leccion: 'Por cada peso de inversión física se pagaron $1.68 de costo financiero. En 2020 estaban casi parejos: 2.8 contra 2.7% del PIB. La deuda acumulada se paga con intereses, y ese dinero ya no está para escuelas, hospitales ni carreteras.' },
    { r: 'hoy', tipo: 'lista', serie: true, q: 'De 2000 a 2025, ¿en qué cierre de año fue más alta la deuda amplia del sector público?',
      tit: 'Deuda amplia al cierre del año (SHRFSP), % del PIB', fmtv: 'pct', est: 'oficial', natural: true, correcta: 'y2025',
      opciones: function () {
        return [['y2018', '2018', 'Peña Nieto', 'epn'], ['y2020', '2020', 'la pandemia', 'amlo'], ['y2024', '2024', 'López Obrador', 'amlo'], ['y2025', '2025', 'Sheinbaum', 'sheinbaum']]
          .map(function (o) { return { id: o[0], et: o[1], sub: o[2], col: colorDe(o[3]) }; });
      },
      datos: function () { return HOY.deuda.map(function (r) { var p = pres(r[2]); return { id: 'y' + r[0], et: String(r[0]), sub: p ? p.c : 'Sheinbaum', col: colorDe(r[2]), v: r[1] }; }); },
      fuera: function () { return []; },
      op: 'Saldo histórico de los requerimientos financieros del sector público (SHRFSP), la publicación oficial más reciente de cada año, como en Números › Cuánto debemos.',
      fs: ['ASF_IR2012', 'ASF_IGE2018', 'ASF_IGE2022', 'CGPE2027_HIST'],
      leccion: 'El cierre de 2025, 52.6% del PIB, es el más alto de la serie: en el primer año de Sheinbaum la deuda subió 0.7 puntos. Hacienda estima 54.0% para el cierre de 2026 y proyecta 55.0% para 2027 (Criterios 2027).' }
  ];

  /* ---------- Estado ---------- */
  var st = { fase: 'inicio', i: 0, resp: [], reloj: false, restante: 0, timer: null, contado: false, cuentas: false, vivo: null, t0: 0, vista: 'barras' };
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
          '<p>Empieza en el siglo XIX, con Santa Anna, Juárez y Porfirio Díaz; sigue con seis sexenios, de Carlos Salinas a Andrés Manuel López Obrador, y termina con el primer año de Claudia Sheinbaum. Primero adivina; después mira la gráfica, en barras o en línea, con la cifra oficial y su fuente. ' +
            'Al terminar verás tu calificación y <b>el estado de cuenta de cada presidente</b>: cuánto creció la economía, cuánta deuda recibió y entregó, y a qué velocidad, por segundo, creció la deuda en su sexenio.</p>' +
          '<ul class="tp-rondas">' + porRonda + '</ul>' +
          '<p class="tp-nota">Las rondas de la balanza vienen del tablero «Versus General Don Porfirio Díaz» de la Enciclopedia, con cada cifra verificada de nuevo contra el INEGI y Hacienda. El sexenio de Claudia Sheinbaum sigue en curso: entra con su primer año completo, 2025, para medirlo, no para calificarlo.</p>' +
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

  /* La misma serie en línea: la traza se dibuja y los puntos aparecen al
     contabilizar. Solo en las preguntas con serie (q.serie). */
  function linea(q, datos, gana, contado) {
    var W = 640, H = 250, iz = 26, de = 26, ar = 30, n = datos.length, gira = n > 9;
    var vs = datos.map(function (d) { return d.v; });
    var mx = Math.max(0, Math.max.apply(null, vs)), mn = Math.min(0, Math.min.apply(null, vs));
    /* Con negativos, el rótulo va bajo el punto: se deja aire antes de los años. */
    var ex = mn < 0 ? 20 : 0, ab = (gira ? 58 : 34) + ex, yx = H - ab + ex + 14;
    if (mx === mn) mx = 1;
    function x(i) { return n === 1 ? W / 2 : iz + i * (W - iz - de) / (n - 1); }
    function y(v) { return ar + (mx - v) / (mx - mn) * (H - ar - ab); }
    var traza = datos.map(function (d, i) { return (i ? 'L' : 'M') + x(i).toFixed(1) + ' ' + y(d.v).toFixed(1); }).join(' ');
    var cero = y(0).toFixed(1);
    var pts = datos.map(function (d, i) {
      var g = d.id === gana.id || (q.correcta && d.id === q.correcta);
      var cx = x(i).toFixed(1), cy = y(d.v), ty = d.v < 0 ? cy + 17 : cy - 9;
      var rot = gira ? ' transform="rotate(-40 ' + cx + ' ' + yx + ')" text-anchor="end"' : ' text-anchor="middle"';
      return '<circle class="tp-lin-pt' + (g ? ' tp-lin-gana' : '') + '" cx="' + cx + '" cy="' + cy.toFixed(1) + '" r="' + (g ? 7 : 5) + '" fill="' + d.col + '" style="transition-delay:' + Math.round(i / Math.max(1, n - 1) * 1100) + 'ms"><title>' + esc(d.et + ': ' + fmt(d.v, q.fmtv)) + '</title></circle>' +
        '<text class="tp-lin-v' + (d.v < 0 ? ' tp-lin-neg' : '') + '" x="' + cx + '" y="' + ty.toFixed(1) + '" text-anchor="middle" data-v="' + d.v + '" data-c="1">' + (contado ? corto(d.v, q.fmtv) : corto(0, q.fmtv)) + '</text>' +
        '<text class="tp-lin-x' + (g ? ' tp-lin-x-gana' : '') + '" x="' + cx + '" y="' + yx + '"' + rot + '>' + esc(d.et) + '</text>';
    }).join('');
    return '<div class="tp-lin"><svg class="tp-lin-svg' + (contado ? ' tp-lin-on' : '') + '" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + esc(q.tit) + '">' +
      '<line class="tp-lin-cero" x1="' + iz / 2 + '" x2="' + (W - de / 2) + '" y1="' + cero + '" y2="' + cero + '"></line>' +
      '<path class="tp-lin-traza" d="' + traza + '" pathLength="1"></path>' + pts +
    '</svg></div>';
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
            '<div class="tp-mandos">' +
              (q.serie ? '<div class="tp-vista" role="group" aria-label="Tipo de gráfica">' +
                '<button type="button" class="tp-vista-b" data-vista="barras" aria-pressed="' + (vistaDe(q) === 'barras') + '">📊 Barras</button>' +
                '<button type="button" class="tp-vista-b" data-vista="linea" aria-pressed="' + (vistaDe(q) === 'linea') + '">📈 Lineal</button></div>' : '') +
              '<button type="button" class="tp-btn tp-btn-sec tp-contar">' + (st.contado ? '↺ Reiniciar a ceros' : '▶️ Contabilizar') + '</button></div></div>' +
          (vistaDe(q) === 'linea' ? linea(q, datos, gana, st.contado) : barras(q, datos, gana, st.contado)) +
          (fueraL.length ? '<ul class="tp-fuera">' + fueraL.map(function (t) { return '<li>' + t + '</li>'; }).join('') + '</ul>' : '') +
          '<p class="tp-leccion"><b>Para leerlo bien.</b> ' + esc(q.leccion) + '</p>' +
          '<p class="tp-fuente">' + chip(q.est) + ' ' + esc(q.op) + ' Fuentes: ' + fuentes(q.fs) + '.</p>' +
          '<div class="tp-sig"><button type="button" class="tp-btn tp-siguiente">' + (ultima ? '🏁 Ver mi resultado' : 'Siguiente pregunta →') + '</button></div>' +
        '</div>' : '');

    Array.prototype.forEach.call(raiz.querySelectorAll('.tp-op'), function (b) {
      b.addEventListener('click', function () { responder(b.getAttribute('data-id'), false); });
    });
    Array.prototype.forEach.call(raiz.querySelectorAll('.tp-vista-b'), function (b) {
      b.addEventListener('click', function () {
        if (st.vista === b.getAttribute('data-vista')) return;
        st.vista = b.getAttribute('data-vista');
        st.contado = false;
        pintar();
      });
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

  function vistaDe(q) { return q.serie ? st.vista : 'barras'; }

  function contar() {
    st.contado = true;
    var q = PREGUNTAS[st.i];
    var b = raiz.querySelector('.tp-contar');
    if (b) b.textContent = '↺ Reiniciar a ceros';
    var svg = raiz.querySelector('.tp-lin-svg');
    if (svg) {
      svg.getBoundingClientRect();
      svg.classList.add('tp-lin-on');
      animar(svg, function (el, v) { return corto(v, q.fmtv); }, 1400);
      return;
    }
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
        '<div class="tp-ec-rejilla">' + P.map(estadoCuenta).join('') + sheinbaum() + porfiriato() + juarez() + santaAnna() + '</div>' +
        correcciones() +
        '<p class="tp-fuente">' + chip('oficial') + ' ' + chip('derivado') + ' ' + chip('pendiente') +
          ' Cada renglón trae su documento. La deuda es el saldo histórico de los requerimientos financieros del sector público (SHRFSP), la medida más amplia que publica Hacienda; los pesos son corrientes de cada año, sin ajustar por inflación. ' +
          'La serie completa, año por año, está en <a href="sigue-el-dinero.html#deuda">Números › Cuánto debemos</a>.</p>' +
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
      renglon('🏦', 'Deuda del gobierno federal en 1890', 126.951, 'mill', 'oficial', 'EHM_DEUDA'),
      renglon('🏦', 'Deuda del gobierno federal en 1911', 589.686, 'mill', 'oficial', 'EHM_DEUDA', null, 'menos'),
      renglon('🏦', 'Deuda como % del PIB', null, '', 'pendiente', null, 'No hay PIB oficial del periodo comparable con el de hoy.')
    ].join('');
    return '<article class="tp-ec tp-ec-porf" style="--tp:' + ORO + '">' +
      '<header class="tp-ec-cab"><b>Porfirio Díaz</b><span>1876–1911 · para comparar</span></header>' +
      '<ul class="tp-ec-lista">' + filas + '</ul>' +
      '<p class="tp-ec-saldo tp-ec-saldo-sin">Pesos de la época y años fiscales de julio a junio: no se suman ni se comparan con los de los sexenios.</p>' +
    '</article>';
  }

  /* El primer año de Sheinbaum: se mide, no se califica. */
  function sheinbaum() {
    var filas = [
      renglon('🏦', 'Deuda que recibió (cierre de 2024), % del PIB', 51.9, 'pct', 'oficial', 'CGPE2027_HIST'),
      renglon('🏦', 'Deuda al cierre de 2025, % del PIB', 52.6, 'pct', 'oficial', 'CGPE2027_HIST'),
      renglon('💳', 'Cambio de la deuda en su primer año', 0.7, 'pp', 'derivado', null, '52.6 menos 51.9.', 'menos'),
      renglon('⚖️', 'Balance presupuestario de 2025', -3.9, 'pib', 'oficial', 'CGPE2027_IG', null, 'menos'),
      renglon('💵', 'Ingresos presupuestarios de 2025', 23.3, 'pib', 'oficial', 'CGPE2027_IG'),
      renglon('🏛️', 'Gasto neto pagado de 2025', 27.2, 'pib', 'oficial', 'CGPE2027_IG'),
      renglon('💸', 'Costo financiero de la deuda en 2025', 3.7, 'pib', 'oficial', 'CGPE2027_IG', 'Más que la inversión física (2.2%).', 'menos')
    ].join('');
    return '<article class="tp-ec" style="--tp:' + SHEIN + '">' +
      '<header class="tp-ec-cab"><b>Claudia Sheinbaum Pardo</b><span>2025– · en curso</span></header>' +
      '<ul class="tp-ec-lista">' + filas + '</ul>' +
      '<p class="tp-ec-saldo tp-ec-saldo-sin">Solo su primer año completo: el sexenio sigue en curso y no se califica.</p>' +
    '</article>';
  }

  /* El siglo XIX, como el Porfiriato: pesos de la época, para comparar. */
  function juarez() {
    var filas = [
      renglon('⚖️', 'Años fiscales con superávit, 1867-1872', 4, 'ent', 'derivado', 'EHM_BAL_XIX', 'De cinco.', 'mas'),
      renglon('⚖️', 'Balance federal 1868-1869', -9.8, 'mill', 'oficial', 'EHM_BAL_XIX', null, 'menos'),
      renglon('🚢', 'Ingresos que venían de aduanas, 1870-1871', 67.9, 'pct', 'derivado', 'EHM_FUENTES'),
      renglon('🏦', 'Deuda del gobierno federal en 1870', 120.0, 'mill', 'oficial', 'EHM_DEUDA')
    ].join('');
    return '<article class="tp-ec tp-ec-porf" style="--tp:' + JUAREZ + '">' +
      '<header class="tp-ec-cab"><b>Benito Juárez</b><span>República Restaurada, 1867–1872 · para comparar</span></header>' +
      '<ul class="tp-ec-lista">' + filas + '</ul>' +
      '<p class="tp-ec-saldo tp-ec-saldo-sin">Pesos de la época y años fiscales de julio a junio: no se suman con los de los sexenios.</p>' +
    '</article>';
  }
  function santaAnna() {
    var filas = [
      renglon('⚖️', 'Balance federal 1835-1836, el peor de sus años', -11.1, 'mill', 'oficial', 'EHM_BAL_XIX', null, 'menos'),
      renglon('📉', 'Ese déficit contra lo que ingresó', 80.4, 'pct', 'derivado', null, '11.1 entre 13.8 millones.', 'menos'),
      renglon('🚢', 'Ingresos que venían de aduanas, 1833-1834', 76.3, 'pct', 'derivado', 'EHM_FUENTES'),
      renglon('🏦', 'Deuda del gobierno federal en 1850', 126.208, 'mill', 'oficial', 'EHM_DEUDA')
    ].join('');
    return '<article class="tp-ec tp-ec-porf" style="--tp:' + SANTA + '">' +
      '<header class="tp-ec-cab"><b>Antonio López de Santa Anna</b><span>1833–1855 · para comparar</span></header>' +
      '<ul class="tp-ec-lista">' + filas + '</ul>' +
      '<p class="tp-ec-saldo tp-ec-saldo-sin">Entró y salió de la presidencia muchas veces en esos años: las cifras son del gobierno federal de cada año, no solo suyas.</p>' +
    '</article>';
  }

  /* Lo que la verificación cambió respecto de las cifras que circulan
     (y que la Enciclopedia todavía muestra). */
  function correcciones() {
    return '<details class="tp-corr"><summary>🔍 Lo que corregimos al verificar el Porfiriato y el tablero 5.4 de la Enciclopedia</summary>' +
      '<p>Cotejamos contra las <i>Estadísticas históricas de México 2014</i> del INEGI las cifras del Porfiriato que se repiten en redes, en blogs y en la propia Enciclopedia de esta plataforma, que está congelada y no se modificó:</p>' +
      '<ul>' +
        '<li><b>«El primer superávit fue el de 1894-1895, por $19,861».</b> El INEGI registra para ese año un déficit de $1.2 millones; la racha de superávits empieza en 1895-1896. No encontramos el documento que sostenga los $19,861: queda ' + chip('pendiente') + ' hasta revisar la Memoria de Hacienda de ese año.</li>' +
        '<li><b>«19,280 km de vía en 1910».</b> El INEGI da 19,748 km; y 617 en 1876, no 640.</li>' +
        '<li><b>«52% de los ingresos venía de las aduanas».</b> En 1894-1895 fue 45.2%; el máximo, 66.8%, fue en 1877-1878 (derivado del cuadro 16.6).</li>' +
        '<li><b>«Ingresos de 8.2%, gasto de 7.4%, deuda de 30.5% y superávit de 0.8% del PIB».</b> No encontramos fuente oficial para ninguna; por eso no aparecen aquí.</li>' +
        '<li><b>«El primer superávit de México fue el de Limantour».</b> El INEGI registra superávit desde 1836-1837, y en cuatro de los cinco años fiscales de Juárez, de 1867 a 1872.</li>' +
        '<li><b>Los porcentajes del PIB del tablero para Santa Anna y Juárez</b> (crecimiento, deuda, ingresos y gasto). No hay PIB oficial del siglo XIX que los sostenga: aquí se usan pesos de la época.</li>' +
        '<li><b>«Zedillo: −19,000 km de vía».</b> La red no se redujo: 26,477 km en 1994 y 26,656 en 2000. Lo que cayó 95% fueron los pasajeros.</li>' +
        '<li><b>«ISR e IVA aportan más del 88% de los impuestos».</b> En 2025 fueron 81.6% (derivado de los Criterios 2027).</li>' +
        '<li><b>Las cifras del tablero para los sexenios de 1988 a 2026</b> (ingresos, gasto y balance en % del PIB). No traen documento que las sostenga: aquí se usan las de los Criterios 2027 para 2020 a 2025 y, para la deuda de los sexenios anteriores, las de la ASF.</li>' +
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
