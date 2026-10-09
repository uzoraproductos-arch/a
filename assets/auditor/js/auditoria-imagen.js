/* ===================================================================
   AUDITAVISION - Auditoria en imagenes, una pagina por diapositiva
   -------------------------------------------------------------------
   Desde el 09-10-2026 cada imagen del carrusel abre su propia pagina
   (auditoria-<id>.html) en lugar del cuadro que se desplegaba encima de
   la portada. Este archivo arma esa pagina con las cifras de
   window.AUDIT_DB: las fichas de Expedientes (informes individuales de la
   ASF), el Panorama del Erario (PEF 2026), la matriz de la Cuenta Publica
   2024, el padron municipal del INEGI y el expediente del huachicol
   fiscal. Aqui no se escribe ni un monto: si la base cambia, la pagina
   cambia con ella.

   Cada pagina tiene cinco piezas:
   1. El dinero, paso a paso: un cuadro conceptual cuyas cifras arrancan
      en cero y suben al pulsar «Ver gasto».
   2. Una escena animada: el monito que reparte monedas entre botes, el
      reloj de los intereses o la fuga del impuesto que no entra. Las
      monedas son una regla de tres (derivado); el monto exacto va escrito
      bajo cada bote.
   3. El rastro renglon por renglon, con su enlace al informe.
   4. Lo que encontro la autoridad y lo que sigue pendiente.
   5. A donde seguir investigando dentro de la plataforma.
   =================================================================== */
(function () {
  'use strict';

  var raiz = document.getElementById('auImg');
  var DB = window.AUDIT_DB;
  if (!raiz || !DB) return;

  var QUIETO = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // --- Formato -------------------------------------------------------------
  function esc(t) {
    return String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function miles(t) {
    var s = String(t), pt = s.indexOf('.');
    var ent = pt === -1 ? s : s.slice(0, pt), dec = pt === -1 ? '' : s.slice(pt);
    var neg = ent.charAt(0) === '-', d = neg ? ent.slice(1) : ent, r = '';
    for (var i = d.length; i > 0; i -= 3) r = (i > 3 ? ',' : '') + d.slice(Math.max(0, i - 3), i) + r;
    return (neg ? '-' : '') + r + dec;
  }
  function fmt(v, f) {
    if (f === 'entero') return miles(Math.round(v).toFixed(0));
    if (f === 'pct') return v.toFixed(1) + '%';
    if (f === 'pesos2') return '$' + miles((Math.round(v * 100) / 100).toFixed(2));
    return '$' + miles(v.toFixed(1)) + ' mdp';
  }
  function mdpPesos(p) { return fmt(p / 1e6, 'mdp1'); }
  function chip(e) {
    var t = (e === 'oficial' || e === 'pendiente') ? e : 'derivado';
    return '<span class="est-chip est-' + t + '">' + t + '</span>';
  }
  function suma(l, c) { return l.reduce(function (a, x) { return a + (x[c] || 0); }, 0); }
  function acc(l, c) { return l.reduce(function (a, x) { return a + ((x.acciones && x.acciones[c]) || 0); }, 0); }
  function ficha(id) {
    return ((DB.expedientes && DB.expedientes.fichas) || []).find(function (f) { return f.id === id; }) || null;
  }
  /* Un titulo de la ASF puede pasar de las veinte palabras: en la barra se
     deja lo que distingue a cada informe. */
  function corto(t) {
    var m = String(t).match(/Paquetes? [\d, y]*\d|Tramo \d+[^,]*, [^,]+/);
    if (m) return m[0];
    var c = String(t).split(/ del Tren Interurbano| y (?:las )?Adecuaciones| de la Construcci[oó]n| del Proyecto| de la Nueva Refiner| del Aeropuerto| de Circulaci[oó]n|, de la Superestructura|, y del Viaducto| km \d|, en (?:el|la|los) /)[0];
    return c.length > 80 ? c.slice(0, 78) + '…' : c;
  }
  /* Lo que el lector ve en la etiqueta del bote: corto y sin parentesis. */
  function etqBote(t) {
    var s = String(t).replace(/\s*\([^)]*\)/g, '');
    return s.length > 42 ? s.slice(0, 40) + '…' : s;
  }

  // --- Armado de cada auditoria ---------------------------------------------
  /* Las obras con expediente comparten forma: cuantos informes, cuanto
     quedo por aclarar, que acciones se promovieron y un renglon por
     informe. Si ninguno dejo monto por aclarar, el rastro muestra lo que
     la ASF reviso en cada uno (universo seleccionado). */
  function desdeExpediente(id) {
    var f = ficha(id);
    if (!f || !f.auditorias) return null;
    var au = f.auditorias, multi = au.length > 1;
    var por = suma(au, 'porAclarar') / 1e6, rec = suma(au, 'recuperado') / 1e6;
    var cps = au.map(function (a) { return a.cp; }).filter(function (c, i, l) { return l.indexOf(c) === i; }).sort();
    var cont = [
      { ico: '🏗️', tit: 'Quién gastó', txt: f.ente },
      { ico: '🔍', tit: 'Quién revisó', v: au.length, f: 'entero', etq: 'informes de la ASF, Cuentas Públicas ' + cps.join(', '), est: 'oficial' },
      { ico: '⚠️', tit: 'Qué quedó por aclarar', v: por, f: 'mdp1', etq: multi ? 'suma de los informes' : 'en el informe', est: multi ? 'derivado' : 'oficial' },
      { ico: '⚖️', tit: 'Qué promovió la ASF', v: acc(au, 'PO'), f: 'entero', etq: 'pliegos de observaciones y ' + acc(au, 'PRAS') + ' promociones de responsabilidad administrativa', est: multi ? 'derivado' : 'oficial' }
    ];
    if (rec > 0) cont.push({ ico: '↩️', tit: 'Qué se recuperó', v: rec, f: 'mdp1', etq: 'durante las auditorías', est: multi ? 'derivado' : 'oficial' });
    var conMonto = au.filter(function (a) { return a.porAclarar > 0; });
    var rastro, tit, escTit;
    if (conMonto.length >= 2) {
      tit = 'Dónde quedó el dinero por aclarar, informe por informe';
      escTit = 'El reparto de lo que quedó por aclarar';
      rastro = conMonto.slice().sort(function (a, b) { return b.porAclarar - a.porAclarar; }).map(function (a) {
        return { k: corto(a.titulo), sub: 'CP ' + a.cp + ' · auditoría ' + a.num, v: a.porAclarar / 1e6, url: a.url };
      });
    } else {
      tit = 'Lo que la ASF revisó en cada auditoría (universo seleccionado)';
      escTit = 'El reparto de lo que la ASF revisó';
      rastro = au.filter(function (a) { return a.universo; }).sort(function (a, b) { return b.universo - a.universo; }).map(function (a) {
        return { k: corto(a.titulo), sub: 'CP ' + a.cp + ' · auditoría ' + a.num + (a.porAclarar ? ' · ' + mdpPesos(a.porAclarar) + ' por aclarar' : ' · sin monto por aclarar'), v: a.universo / 1e6, url: a.url };
      });
    }
    var principal = au.slice().sort(function (a, b) { return (b.porAclarar - a.porAclarar) || ((b.universo || 0) - (a.universo || 0)); })[0];
    return {
      cont: cont, rastroTit: tit, rastro: rastro, rastroEst: rastro.length ? 'oficial' : null,
      escena: { tipo: 'reparto', tit: escTit, caja: 'La ASF', unidad: 'mdp' },
      hallazgo: f.hallazgo,
      fuente: f.fuente + '. ' + f.alcance,
      acciones: [
        { txt: '📂 Abrir el expediente completo en Búsqueda Forense', href: 'index.html?ir=expediente&ancla=' + id },
        { txt: '🏛️ Leer el informe principal de la ASF', url: principal.url }
      ]
    };
  }

  function egreso(id) {
    var P = DB.panoramaErario;
    return P && P.egresos ? P.egresos.find(function (e) { return e.id === id; }) : null;
  }

  function deuda() {
    var e = egreso('egr-costofin'), P = DB.panoramaErario;
    if (!e || !P) return null;
    var anual = e.montoMdp;
    return {
      cont: [
        { ico: '📆', tit: 'Al año', v: anual, f: 'mdp1', etq: 'en intereses y comisiones (PEF 2026, Anexo 8)', est: e.estado },
        { ico: '🌅', tit: 'Cada día', v: anual / 365, f: 'mdp1', etq: 'el monto anual entre 365', est: 'derivado' },
        { ico: '⏱️', tit: 'Cada segundo', v: anual * 1e6 / 31536000, f: 'pesos2', etq: 'el monto anual entre los 31,536,000 segundos del año', est: 'derivado' },
        { ico: '🥧', tit: 'Del presupuesto', v: anual / P.totalPEF * 100, f: 'pct', etq: 'del Presupuesto de Egresos 2026 ($' + miles(P.totalPEF.toFixed(1)) + ' mdp)', est: 'derivado' }
      ],
      rastroTit: 'De qué se compone', rastroEst: 'oficial',
      rastro: e.componentes.filter(function (c) { return c.m > 0; }).map(function (c) { return { k: c.n, sub: c.d, v: c.m }; }),
      escena: { tipo: 'reloj', tit: 'El reloj de los intereses', porSeg: anual * 1e6 / 31536000, reparto: true, caja: 'Hacienda', unidad: 'mdp' },
      hallazgo: e.queCubre + ' La Ley Federal de Presupuesto (art. 2º, fracc. XXV) deja fuera del gasto neto total las amortizaciones: este renglón paga el precio de lo prestado, no devuelve el capital.',
      fuente: 'Presupuesto de Egresos de la Federación 2026, ' + e.clave + '. ' + e.ley + '.',
      acciones: [
        { txt: '📉 Ver el costo financiero en el Panorama del Erario', href: 'index.html?ir=flujo&ancla=egr-costofin' },
        { txt: '🧮 Calcular tu parte de los intereses en la Calculadora Cívica', href: 'index.html?ir=calculadora&ancla=cc-b4' }
      ]
    };
  }

  function ramo33() {
    var P = DB.panoramaErario;
    var r = P && P.federalizado && P.federalizado.componentes.find(function (c) { return c.id === 'fed-r33'; });
    var cp = DB.cuenta_publica_asf && DB.cuenta_publica_asf.cp2024;
    if (!r || !cp) return null;
    var mun = (P.municipal && P.municipal.fuentes) || [], fed = cp.federalizado;
    var mdb = DB.cuenta_publica_asf.fuentes.MDB2024;
    return {
      cont: [
        { ico: '🏛️', tit: 'La Federación aprueba', v: r.montoMdp, f: 'mdp1', etq: 'Ramo 33 para 2026 (' + r.clave + ' del PEF)', est: r.estado },
        { ico: '🏘️', tit: 'Llega directo a municipios', v: suma(mun, 'montoMdp'), f: 'mdp1', etq: 'FORTAMUN más FISMDF', est: 'derivado' },
        { ico: '🔍', tit: 'La ASF revisa', v: fed.auditorias, f: 'entero', etq: 'auditorías al gasto federalizado de la Cuenta Pública 2024', est: cp.estado },
        { ico: '⚠️', tit: 'Quedó por aclarar', v: fed.porAclarar / 1e6, f: 'mdp1', etq: 'en esas auditorías (CP 2024)', est: cp.estado }
      ],
      rastroTit: 'Los ocho fondos del Ramo 33 en 2026', rastroEst: 'oficial',
      rastro: r.componentes.map(function (c) { return { k: c.n, sub: c.d, v: c.m }; }),
      escena: { tipo: 'reparto', tit: 'El reparto del Ramo 33 entre sus fondos', caja: 'La Federación', unidad: 'mdp' },
      hallazgo: r.queEs + ' Las cifras de la ASF son de la Cuenta Pública 2024, la última revisada completa; las del presupuesto, de 2026. Son años distintos y se muestran juntas sólo para dar escala.',
      fuente: 'PEF 2026, ' + r.clave + ' (' + r.ley + '); ' + (mdb ? mdb.doc : 'ASF, Matriz de Datos Básicos CP 2024') + ', p. ' + cp.pagina + '.',
      acciones: [
        { txt: '🏘️ Comparar lo que recibe tu municipio en el padrón municipal', href: 'index.html?ir=municipios&ancla=munBloqueLista' },
        { txt: '🎯 Ver los ocho fondos en el Panorama del Erario', href: 'index.html?ir=flujo&ancla=fed-r33' }
      ]
    };
  }

  function munCienega() {
    var M = window.AUDIT_MUNICIPIOS, e = M && M.ent && M.ent.NL;
    if (!e) return null;
    var f = e.lista.find(function (x) { return e.cve + x[0] === '19012'; });
    if (!f || f.length !== 10) return null;
    return { ing: f[2] / 1e6, fortamun: f[5] / 1e6, fismdf: f[6] / 1e6 };
  }

  function lego() {
    var f = ficha('cuchillo-ii');
    if (!f) return null;
    var m = munCienega(), au = f.auditorias;
    var cont = [
      { ico: '💧', tit: 'El acueducto El Cuchillo II', v: suma(au, 'universo') / 1e6, f: 'mdp1', etq: 'revisados por la ASF en tres Cuentas Públicas (suma del universo seleccionado)', est: 'derivado' },
      { ico: '⚠️', tit: 'Quedó por aclarar', v: suma(au, 'porAclarar') / 1e6, f: 'mdp1', etq: 'del acueducto, suma de los tres informes', est: 'derivado' }
    ];
    if (m) {
      cont.push({ ico: '🏘️', tit: 'Ciénega de Flores recibió', v: m.ing, f: 'mdp1', etq: 'ingresos del municipio en 2024 (INEGI, EFIPEM)', est: 'oficial' });
      cont.push({ ico: '🎯', tit: 'De ellos, del Ramo 33', v: m.fortamun + m.fismdf, f: 'mdp1', etq: 'FORTAMUN más FISMDF', est: 'derivado' });
    }
    return {
      cont: cont,
      rastroTit: 'El Cuchillo II, año por año: lo que la ASF revisó', rastroEst: 'oficial',
      rastro: au.map(function (a) {
        return { k: 'Cuenta Pública ' + a.cp, sub: 'Auditoría ' + a.num + ' · ' + (a.porAclarar ? mdpPesos(a.porAclarar) + ' por aclarar' : 'sin monto por aclarar'), v: (a.universo || 0) / 1e6, url: a.url };
      }),
      escena: { tipo: 'reparto', tit: 'El reparto de lo revisado, año por año', caja: 'La ASF', unidad: 'mdp' },
      hallazgo: f.hallazgo + ' La ampliación de la planta de LEGO que se ha anunciado no tiene todavía un documento oficial en esta plataforma: su monto queda pendiente y no se suma a ninguna cifra.',
      pendiente: 'Inversión anunciada por LEGO en Ciénega de Flores: sin documento oficial verificado.',
      fuente: f.fuente + '. Padrón municipal: INEGI, Estadística de Finanzas Públicas Estatales y Municipales, 2024.',
      acciones: [
        { txt: '🏘️ Ver Ciénega de Flores en el padrón municipal', href: 'index.html?ir=municipio&ancla=NL-19012' },
        { txt: '📂 Abrir el expediente de El Cuchillo II en Búsqueda Forense', href: 'index.html?ir=expediente&ancla=cuchillo-ii' }
      ]
    };
  }

  function megafarmacia() {
    var f = ficha('birmex');
    if (!f) return null;
    var a = f.auditorias[0], x = a.extractos || {};
    var otros = a.porAclarar - x.almacenAvior - x.almacenMaypo;
    return {
      cont: [
        { ico: '🏢', tit: 'Comprar y adecuar el almacén', v: x.cefedisInversion / 1e6, f: 'mdp1', etq: 'inversión estimada, sin IVA', est: 'oficial' },
        { ico: '🏷️', tit: 'Precio del inmueble', v: x.cefedisInmuebleConIva / 1e6, f: 'mdp1', etq: 'Huehuetoca, con IVA', est: 'oficial' },
        { ico: '📦', tit: 'Equipamiento', v: x.cefedisEquipamiento / 1e6, f: 'mdp1', etq: 'adjudicado en forma directa, con IVA', est: 'oficial' },
        { ico: '💸', tit: 'Pagado en 2023', v: (x.cefedisInmueblePagado + x.cefedisEquipamientoPagado) / 1e6, f: 'mdp1', etq: 'primer abono del inmueble y anticipo del equipamiento', est: 'derivado' },
        { ico: '⚠️', tit: 'Quedó por aclarar', v: a.porAclarar / 1e6, f: 'mdp1', etq: 'en toda la auditoría a Birmex (CP 2023)', est: 'oficial' }
      ],
      rastroTit: 'Lo que Birmex dejó por aclarar en 2023', rastroEst: 'oficial',
      rastro: [
        { k: 'Almacenaje y Distribución Avior', sub: 'Almacenaje sin evidencia de que se recibió el servicio', v: x.almacenAvior / 1e6, url: a.url },
        { k: 'Farmacéuticos Maypo', sub: 'Almacenaje y distribución sin evidencia de recepción', v: x.almacenMaypo / 1e6, url: a.url },
        { k: 'Otros hallazgos de la misma auditoría', sub: 'El resto del monto por aclarar (resta del total menos los dos anteriores)', v: otros / 1e6, url: a.url, est: 'derivado' }
      ],
      escena: { tipo: 'reparto', tit: 'El reparto de lo que quedó por aclarar', caja: 'Birmex', unidad: 'mdp' },
      hallazgo: f.hallazgo,
      fuente: 'ASF, Informe Individual de la Cuenta Pública 2023, auditoría ' + a.num + ' (' + a.clave + '), resultado 4, pp. 79 a 84, y dictamen.',
      acciones: [
        { txt: '📂 Abrir el expediente de Birmex en Búsqueda Forense', href: 'index.html?ir=expediente&ancla=birmex' },
        { txt: '🏛️ Leer el informe de la ASF', url: a.url }
      ]
    };
  }

  /* Huachicol fiscal: no es gasto que sale sino impuesto que no entra. Lo
     oficial es lo que el Gobierno espera cobrar; lo que otros dicen que se
     pierde va con chip pendiente, porque ninguna autoridad ha publicado la
     cifra. Por eso aqui no hay reparto sino un escenario: el lector mueve
     el porcentaje y la cuenta es una regla de tres, no una estimacion. */
  function huachicol() {
    var H = DB.huachicol_fiscal;
    if (!H || !H.en_juego) return null;
    var J = H.en_juego, R = H.reconocimiento, A = H.anam, M = H.marco_legal;
    var ilif = H.fuentes.ilif27 || {};
    var oce = (H.estimaciones || []).find(function (e) { return e.fuente === 'oce'; });
    var cf = M && M.cuotas_federales_2026;
    var cont = [];
    if (cf) cont.push({ ico: '⛽', tit: 'En cada litro', v: cf.gasolina_menor_91, f: 'pesos2', etq: 'de IEPS federal por litro de gasolina menor a 91 octanos en 2026 ($' + cf.gasolina_menor_91.toFixed(4) + ' por ley, antes del estímulo fiscal)', est: 'oficial' });
    cont.push({ ico: '💰', tit: 'Lo que se espera cobrar', v: J.ieps_combustibles_2027_mdp, f: 'mdp1', etq: 'de IEPS de gasolinas y diésel en 2027 (Ley de Ingresos 2027, p. ' + J.pagina.split(' ')[0] + ')', est: J.estado });
    cont.push({ ico: '🕳️', tit: 'Cada 1 % que se evade', v: J.uno_por_ciento_mdp, f: 'mdp1', etq: 'el monto anterior entre 100', est: 'derivado' });
    cont.push({ ico: '❓', tit: 'Cuánto se evade', txt: 'Ninguna autoridad lo ha publicado.', est: 'pendiente' });
    var rastro = [
      { k: 'IEPS de combustibles esperado en 2027', sub: 'Lo que la Ley de Ingresos 2027 propone cobrar. Es lo que está en juego, no lo que se pierde.', v: J.ieps_combustibles_2027_mdp, url: ilif.url, est: J.estado }
    ];
    if (oce) {
      rastro.push({ k: 'Costo total estimado por el Observatorio Ciudadano de Energía, ' + oce.anio, sub: 'Organismo civil, no autoridad: ' + miles(oce.pemex_mdp.toFixed(0)) + ' mdp de afectación a Pemex más ' + miles(oce.impuestos_mdp.toFixed(0)) + ' mdp de impuestos no cobrados.', v: oce.total_mdp, url: (H.fuentes[oce.fuente] || {}).url, est: oce.estado });
      rastro.push({ k: 'De esa estimación, impuestos no cobrados', sub: 'La parte de la estimación civil que toca al erario.', v: oce.impuestos_mdp, url: (H.fuentes[oce.fuente] || {}).url, est: oce.estado });
    }
    rastro.push({ k: 'Cada 1 % del IEPS de combustibles', sub: 'Regla de tres para dar tamaño: ' + miles(J.ieps_combustibles_2027_mdp.toFixed(1)) + ' ÷ 100.', v: J.uno_por_ciento_mdp, est: 'derivado' });
    if (A) rastro.push({ k: 'Recaudación asociada a lo que detectaron las aduanas', sub: 'Del ' + A.periodo + ': ' + A.litros_millones + ' millones de litros de hidrocarburos no declarados (Segundo Informe de Gobierno, p. ' + A.pagina + '). Es lo que se cobró, no lo que se evade.', v: A.recaudacion_mdp, url: (H.fuentes[A.fuente] || {}).url, est: A.estado });
    return {
      cont: cont,
      rastroTit: 'Lo que está en juego y lo que se ha dicho', rastroEst: null, rastro: rastro,
      escena: { tipo: 'fuga', tit: 'Simula la fuga: ¿y si se evadiera…?', total: J.ieps_combustibles_2027_mdp, uno: J.uno_por_ciento_mdp },
      hallazgo: 'El Gobierno lo reconoce por escrito: en la exposición de motivos de la Ley de Ingresos 2027 dice que «' + R.cita + '». Las prácticas que nombra: ' + R.practicas + '. ' + R.medida,
      pendiente: 'Ninguna autoridad ha publicado cuánto se pierde. ' + (H.estudios ? H.estudios.texto + ' ' : '') + 'Las barras con chip pendiente son cifras que otros han dado y que aún no cotejamos en un documento oficial: se muestran para dar escala, no como dato.',
      fuente: 'Iniciativa de Ley de Ingresos de la Federación 2027 (Gaceta Parlamentaria, 8-09-2026), pp. ' + R.paginas + ' y ' + J.pagina + '; Ley del IEPS, art. 2o., fr. I, inciso D, texto vigente; Segundo Informe de Gobierno, pp. 46 y 260; estimación del Observatorio Ciudadano de Energía, pendiente de cotejo.',
      acciones: [
        { txt: '📂 Abrir el expediente completo del huachicol fiscal', href: 'index.html?ir=radar&ancla=huachicol' },
        { txt: '🧮 Ver cuánto IEPS pagas en la Calculadora Cívica', href: 'index.html?ir=calculadora' },
        { txt: '📖 Qué es el huachicol fiscal, en el glosario', href: 'index.html?ir=glosario&ancla=Huachicol-Fiscal' },
        { txt: '📜 Leer la Iniciativa de Ley de Ingresos 2027', url: ilif.url }
      ]
    };
  }

  var ARMA = {
    'tren-maya': function () { return desdeExpediente('tren-maya'); },
    'dos-bocas': function () { return desdeExpediente('dos-bocas'); },
    'deuda-soberana': deuda,
    'aifa': function () { return desdeExpediente('aifa'); },
    'ramo-33': ramo33,
    'lego-cienega': lego,
    'tren-toluca': function () { return desdeExpediente('tren-toluca'); },
    'megafarmacia': megafarmacia,
    'huachicol-fiscal': huachicol
  };

  // --- Animacion de cifras --------------------------------------------------
  function contar(zona, ms, fin) {
    var cifras = [].slice.call(zona.querySelectorAll('[data-v]'));
    var barras = [].slice.call(zona.querySelectorAll('[data-w]'));
    function pintar(e) {
      cifras.forEach(function (el) { el.textContent = fmt(parseFloat(el.dataset.v) * e, el.dataset.f); });
      barras.forEach(function (el) { el.style.width = (parseFloat(el.dataset.w) * e).toFixed(2) + '%'; });
    }
    if (QUIETO || !ms) { pintar(1); if (fin) fin(); return; }
    var t0 = null;
    function paso(t) {
      if (t0 === null) t0 = t;
      var x = Math.min(1, (t - t0) / ms);
      pintar(1 - Math.pow(1 - x, 3));
      if (x < 1) requestAnimationFrame(paso); else if (fin) fin();
    }
    requestAnimationFrame(paso);
  }

  // --- 1. El dinero, paso a paso -------------------------------------------
  function htmlMapa(p) {
    var cajas = p.cont.map(function (c, i) {
      var cifra = (c.v !== undefined)
        ? '<span class="au-paso-v num-tabular" data-v="' + c.v + '" data-f="' + c.f + '">' + fmt(0, c.f) + '</span>'
        : '<span class="au-paso-v au-paso-txt">' + esc(c.txt) + '</span>';
      return (i ? '<span class="au-flecha" aria-hidden="true">➜</span>' : '') +
        '<div class="au-paso" style="--i:' + i + '">' +
          '<span class="au-paso-ico" aria-hidden="true">' + c.ico + '</span>' +
          '<span class="au-paso-tit">' + esc(c.tit) + '</span>' + cifra +
          (c.etq ? '<span class="au-paso-etq">' + esc(c.etq) + '</span>' : '') +
          (c.est ? '<span class="au-paso-chip">' + chip(c.est) + '</span>' : '') +
        '</div>';
    }).join('');
    return '<section class="au-sec" aria-labelledby="auMapaTit">' +
      '<div class="au-sec-cab"><h2 class="au-sec-tit" id="auMapaTit"><span class="au-num" aria-hidden="true">1</span> El dinero, paso a paso</h2>' +
      '<p class="au-sec-txt">Las cuentas arrancan en cero. Pulsa «Ver gasto» y sube cada una hasta su cifra, con su fuente.</p></div>' +
      '<div class="au-mandos"><button type="button" class="au-btn" id="auVer">▶ Ver gasto</button>' +
      '<span class="au-estado" id="auVerEst" role="status">Las cuentas están en cero.</span></div>' +
      '<div class="au-mapa" id="auMapa">' + cajas + '</div></section>';
  }

  function armarMapa() {
    var btn = document.getElementById('auVer'), est = document.getElementById('auVerEst');
    var zona = document.getElementById('auMapa'), estado = 'cero';
    btn.addEventListener('click', function () {
      if (estado === 'contando') return;
      if (estado === 'listo') {
        zona.querySelectorAll('[data-v]').forEach(function (el) { el.textContent = fmt(0, el.dataset.f); });
        zona.classList.remove('au-listo');
        estado = 'cero';
        btn.textContent = '▶ Ver gasto';
        est.textContent = 'Las cuentas volvieron a cero. Pulsa «Ver gasto» para contar de nuevo.';
        return;
      }
      estado = 'contando';
      btn.disabled = true;
      btn.textContent = '⏳ Contando…';
      est.textContent = 'Siguiendo el rastro del dinero…';
      zona.classList.add('au-contando');
      contar(zona, 2200, function () {
        estado = 'listo';
        zona.classList.remove('au-contando');
        zona.classList.add('au-listo');
        btn.disabled = false;
        btn.textContent = '↺ Reiniciar a ceros';
        est.textContent = 'Cuenta terminada: cada cifra lleva su fuente y su estado.';
      });
    });
  }

  // --- 2. Escenas -----------------------------------------------------------
  var MONEDAS = 40;

  /* Los botes: los cinco renglones mayores y, si hay mas, uno que junta
     a los demas. Las monedas se reparten por residuo mayor para que sumen
     exactamente MONEDAS, y todo bote con dinero lleva al menos una. */
  function botesDe(rastro) {
    var l = rastro.filter(function (r) { return r.v > 0; }).slice().sort(function (a, b) { return b.v - a.v; });
    var b = l.slice(0, 5).map(function (r) { return { k: r.k, v: r.v }; });
    if (l.length > 5) {
      var resto = l.slice(5);
      b.push({ k: 'Los demás (' + resto.length + ')', v: suma(resto, 'v') });
    }
    var total = suma(b, 'v');
    var cuotas = b.map(function (x) { return x.v / total * MONEDAS; });
    b.forEach(function (x, i) { x.n = Math.max(1, Math.floor(cuotas[i])); });
    var faltan = MONEDAS - suma(b, 'n');
    var orden = b.map(function (x, i) { return i; }).sort(function (i, j) { return (cuotas[j] - b[j].n) - (cuotas[i] - b[i].n); });
    for (var k = 0; faltan > 0 && k < orden.length * 4; k++, faltan--) b[orden[k % orden.length]].n++;
    while (faltan < 0) {
      var mayor = b.reduce(function (m, x, i) { return (x.n - cuotas[i]) > (b[m].n - cuotas[m]) && x.n > 1 ? i : m; }, 0);
      b[mayor].n--; faltan++;
    }
    return { botes: b, total: total };
  }

  function htmlReparto(p) {
    var r = botesDe(p.rastro);
    if (!r.botes.length) return '';
    var maxN = Math.max.apply(null, r.botes.map(function (x) { return x.n; }));
    var botes = r.botes.map(function (x, i) {
      return '<button type="button" class="au-bote" data-i="' + i + '" data-n="' + x.n + '" aria-pressed="false" title="' + esc(x.k) + '">' +
          '<span class="au-bote-vaso"><span class="au-bote-lleno" data-alto="' + (x.n / maxN * 100).toFixed(1) + '"></span>' +
          '<span class="au-bote-cuenta"><span class="au-bote-mon">0</span> 🪙</span></span>' +
          '<span class="au-bote-k">' + esc(etqBote(x.k)) + '</span>' +
          '<span class="au-bote-v num-tabular" data-v="' + x.v + '" data-f="mdp1">' + fmt(0, 'mdp1') + '</span>' +
        '</button>';
    }).join('');
    return '<div class="au-reparto" id="auReparto">' +
      '<p class="au-reto" id="auReto">🎯 <b>Antes de repartir:</b> toca el bote que crees que se llevará más dinero.</p>' +
      '<div class="au-escenario" id="auEscenario">' +
        '<div class="au-caja"><span class="au-caja-ico" aria-hidden="true">🏦</span><span class="au-caja-k">' + esc(p.escena.caja) + '</span>' +
          '<span class="au-caja-v num-tabular">' + fmt(r.total, 'mdp1') + '</span></div>' +
        '<div class="au-chango" id="auChango" aria-hidden="true"><span class="au-chango-cuerpo">🐒</span><span class="au-chango-bolsa">💰</span></div>' +
        '<div class="au-botes" style="--n:' + r.botes.length + '">' + botes + '</div>' +
      '</div>' +
      '<div class="au-mandos"><button type="button" class="au-btn" id="auRepartir">🐒 Repartir el dinero</button>' +
        '<button type="button" class="au-btn au-btn-2" id="auSaltar" hidden>⏩ Saltar</button>' +
        '<span class="au-estado" id="auRepEst" role="status">Cada moneda 🪙 vale ' + fmt(r.total / MONEDAS, 'mdp1') + ': el total entre ' + MONEDAS + ' ' + chip('derivado') + '</span></div>' +
      '<p class="au-nota">Las monedas redondean para que se vean; la cifra exacta es la que va escrita bajo cada bote.</p>' +
    '</div>';
  }

  function armarReparto() {
    var cont = document.getElementById('auReparto');
    if (!cont) return;
    var esc_ = document.getElementById('auEscenario'), chango = document.getElementById('auChango');
    var btn = document.getElementById('auRepartir'), saltar = document.getElementById('auSaltar');
    var est = document.getElementById('auRepEst'), reto = document.getElementById('auReto');
    var botes = [].slice.call(cont.querySelectorAll('.au-bote'));
    var apuesta = null, corriendo = false, cancelar = false, listo = false, base = est.innerHTML;

    botes.forEach(function (b) {
      b.addEventListener('click', function () {
        if (corriendo || listo) return;
        apuesta = +b.dataset.i;
        botes.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        reto.innerHTML = '🎯 Apostaste por <b>' + esc(b.title) + '</b>. Ahora pulsa «Repartir el dinero».';
      });
    });

    function pintarBote(b, n) {
      var tot = +b.dataset.n;
      b.querySelector('.au-bote-mon').textContent = n;
      var ll = b.querySelector('.au-bote-lleno');
      ll.style.height = (parseFloat(ll.dataset.alto) * n / tot).toFixed(1) + '%';
      var v = b.querySelector('.au-bote-v');
      v.textContent = fmt(parseFloat(v.dataset.v) * n / tot, 'mdp1');
    }

    function terminar() {
      botes.forEach(function (b) { pintarBote(b, +b.dataset.n); b.classList.add('au-bote-fin'); });
      corriendo = false; listo = true;
      chango.classList.remove('au-tira');
      chango.classList.add('au-festeja');
      saltar.hidden = true;
      btn.disabled = false;
      btn.textContent = '↺ Repartir otra vez';
      est.innerHTML = base;
      var mayor = botes.reduce(function (m, b) { return parseFloat(b.querySelector('.au-bote-v').dataset.v) > parseFloat(m.querySelector('.au-bote-v').dataset.v) ? b : m; }, botes[0]);
      mayor.classList.add('au-bote-mayor');
      if (apuesta === null) reto.innerHTML = '🏆 Se llevó más: <b>' + esc(mayor.title) + '</b>.';
      else if (+mayor.dataset.i === apuesta) reto.innerHTML = '🏆 ¡Le atinaste! Se llevó más: <b>' + esc(mayor.title) + '</b>.';
      else reto.innerHTML = '🤔 Casi. Se llevó más: <b>' + esc(mayor.title) + '</b>.';
    }

    function reiniciar() {
      listo = false; apuesta = null;
      botes.forEach(function (b) { pintarBote(b, 0); b.classList.remove('au-bote-fin', 'au-bote-mayor'); b.setAttribute('aria-pressed', 'false'); });
      chango.classList.remove('au-festeja');
      btn.textContent = '🐒 Repartir el dinero';
      reto.innerHTML = '🎯 <b>Antes de repartir:</b> toca el bote que crees que se llevará más dinero.';
    }

    /* El monito avienta una moneda por vez en arco hasta su bote. La
       secuencia se arma intercalando botes, para que todos vayan
       llenandose a la par y la carrera se vea. */
    function secuencia() {
      var quedan = botes.map(function (b) { return +b.dataset.n; }), s = [];
      while (quedan.some(function (q) { return q > 0; })) {
        quedan.forEach(function (q, i) { if (q > 0) { s.push(i); quedan[i]--; } });
      }
      return s;
    }

    function tirar(i, alLlegar) {
      var b = botes[i], r0 = esc_.getBoundingClientRect();
      var rc = chango.getBoundingClientRect(), rb = b.querySelector('.au-bote-vaso').getBoundingClientRect();
      var x0 = rc.left - r0.left + rc.width * 0.55, y0 = rc.top - r0.top + rc.height * 0.2;
      var x1 = rb.left - r0.left + rb.width / 2 - 10, y1 = rb.top - r0.top + 4;
      var alto = Math.min(y0, y1) - 60;
      var m = document.createElement('span');
      m.className = 'au-moneda';
      m.textContent = '🪙';
      esc_.appendChild(m);
      var a = m.animate([
        { transform: 'translate(' + x0 + 'px,' + y0 + 'px) rotate(0deg)' },
        { transform: 'translate(' + ((x0 + x1) / 2) + 'px,' + alto + 'px) rotate(200deg)', offset: 0.5 },
        { transform: 'translate(' + x1 + 'px,' + y1 + 'px) rotate(380deg)' }
      ], { duration: 520, easing: 'cubic-bezier(.3,.6,.5,1)' });
      a.onfinish = function () { m.remove(); alLlegar(); };
    }

    btn.addEventListener('click', function () {
      if (corriendo) return;
      if (listo) reiniciar();
      if (QUIETO) { terminar(); return; }
      corriendo = true; cancelar = false;
      btn.disabled = true;
      btn.textContent = '🐒 Repartiendo…';
      saltar.hidden = false;
      chango.classList.add('au-tira');
      var s = secuencia(), llegadas = botes.map(function () { return 0; }), k = 0, vivos = 0;
      function siguiente() {
        if (cancelar) return;
        if (k >= s.length) { if (!vivos) terminar(); return; }
        var i = s[k++];
        vivos++;
        chango.classList.remove('au-salta'); void chango.offsetWidth; chango.classList.add('au-salta');
        tirar(i, function () {
          vivos--;
          if (cancelar) return;
          llegadas[i]++;
          pintarBote(botes[i], llegadas[i]);
          if (k >= s.length && !vivos) terminar();
        });
        setTimeout(siguiente, 150);
      }
      siguiente();
    });

    saltar.addEventListener('click', function () {
      cancelar = true;
      esc_.querySelectorAll('.au-moneda').forEach(function (m) { m.remove(); });
      terminar();
    });
  }

  /* El reloj: desde que se abrio la pagina, cuanto se ha ido en intereses
     a la tasa por segundo del presupuesto (derivado: anual entre segundos
     del año). Una moneda cae en la alcancia cada segundo. */
  function htmlReloj(p) {
    return '<div class="au-reloj">' +
      '<div class="au-reloj-cara"><span class="au-reloj-ico" aria-hidden="true">⏱️</span>' +
        '<span class="au-reloj-seg" id="auRelojSeg">0 s</span></div>' +
      '<div class="au-reloj-txt"><span class="au-reloj-k">Desde que abriste esta página, en intereses de la deuda se han ido</span>' +
        '<span class="au-reloj-v num-tabular" id="auRelojV">$0.00</span>' +
        '<span class="au-reloj-etq">A razón de ' + fmt(p.escena.porSeg, 'pesos2') + ' por segundo ' + chip('derivado') + '</span></div>' +
      '<div class="au-alcancia" id="auAlcancia" aria-hidden="true"><span class="au-alcancia-ico">🏦</span></div>' +
    '</div>';
  }

  function armarReloj(p) {
    var v = document.getElementById('auRelojV'), s = document.getElementById('auRelojSeg');
    var alc = document.getElementById('auAlcancia');
    if (!v) return;
    var t0 = Date.now(), ultimo = 0;
    setInterval(function () {
      var seg = (Date.now() - t0) / 1000;
      v.textContent = fmt(seg * p.escena.porSeg, 'pesos2');
      s.textContent = Math.floor(seg) + ' s';
      if (!QUIETO && Math.floor(seg) > ultimo) {
        ultimo = Math.floor(seg);
        var m = document.createElement('span');
        m.className = 'au-cae';
        m.textContent = '🪙';
        alc.appendChild(m);
        setTimeout(function () { m.remove(); }, 900);
      }
    }, 100);
  }

  /* La fuga: cien monedas son todo el IEPS de combustibles esperado en
     2027. El lector elige un porcentaje y esas monedas se caen por el
     hoyo. Es un escenario para dar tamaño, no una estimacion. */
  function htmlFuga(p) {
    var mon = '';
    for (var i = 0; i < 100; i++) mon += '<span class="au-fuga-m" data-i="' + i + '">🪙</span>';
    return '<div class="au-fuga">' +
      '<label class="au-fuga-lbl" for="auFugaR">Mueve la barra: ¿qué parte del IEPS de combustibles se evadiría?</label>' +
      '<div class="au-fuga-ctl"><input type="range" id="auFugaR" min="0" max="30" step="1" value="0">' +
        '<output class="au-fuga-pct num-tabular" id="auFugaPct" for="auFugaR">0 %</output></div>' +
      '<div class="au-fuga-tanque" id="auFugaTanque" aria-hidden="true">' + mon + '</div>' +
      '<p class="au-fuga-res">Cada moneda es el 1 % de lo que se espera cobrar en 2027. Si se evadiera el <b id="auFugaPct2">0 %</b>, el erario dejaría de cobrar ' +
        '<b class="num-tabular" id="auFugaV">$0.0 mdp</b> al año ' + chip('derivado') + '</p>' +
      '<p class="au-nota">🧪 Escenario hipotético: es una regla de tres (porcentaje × ' + fmt(p.escena.uno, 'mdp1') + '), no una estimación. ' + chip('pendiente') + ' Ninguna autoridad ha publicado cuánto se evade.</p>' +
    '</div>';
  }

  function armarFuga(p) {
    var r = document.getElementById('auFugaR');
    if (!r) return;
    var ms = [].slice.call(document.querySelectorAll('.au-fuga-m'));
    function pintar() {
      var x = +r.value;
      document.getElementById('auFugaPct').textContent = x + ' %';
      document.getElementById('auFugaPct2').textContent = x + ' %';
      document.getElementById('auFugaV').textContent = fmt(x * p.escena.uno, 'mdp1');
      ms.forEach(function (m, i) { m.classList.toggle('au-fuga-ida', i >= 100 - x); });
    }
    r.addEventListener('input', pintar);
    pintar();
  }

  function htmlEscena(p) {
    var e = p.escena, cuerpo = '', txt = '';
    if (e.tipo === 'reparto') {
      cuerpo = htmlReparto(p);
      txt = 'Un monito reparte el dinero en monedas. Cada bote es un renglón del rastro.';
    } else if (e.tipo === 'reloj') {
      cuerpo = htmlReloj(p) + htmlReparto(p);
      txt = 'El reloj corre mientras lees. Abajo, el monito reparte el costo del año entre sus componentes.';
    } else if (e.tipo === 'fuga') {
      cuerpo = htmlFuga(p);
      txt = 'Aquí no hay gasto que repartir: es un impuesto que no entra. Juega con el porcentaje y mira el tamaño.';
    }
    if (!cuerpo) return '';
    return '<section class="au-sec" aria-labelledby="auEscTit">' +
      '<div class="au-sec-cab"><h2 class="au-sec-tit" id="auEscTit"><span class="au-num" aria-hidden="true">2</span> ' + esc(e.tit) + '</h2>' +
      '<p class="au-sec-txt">' + txt + '</p></div>' + cuerpo + '</section>';
  }

  // --- 3. El rastro ---------------------------------------------------------
  function htmlRastro(p) {
    var mayor = Math.max.apply(null, p.rastro.map(function (r) { return r.v; }).concat([0])) || 1;
    var filas = p.rastro.length ? p.rastro.map(function (r) {
      var k = r.url ? '<a href="' + esc(r.url) + '" target="_blank" rel="noopener noreferrer">' + esc(r.k) + ' ↗</a>' : esc(r.k);
      return '<li class="au-fila">' +
        '<div class="au-fila-cab"><span class="au-fila-k">' + k + (r.est ? ' ' + chip(r.est) : '') + '</span>' +
        '<span class="au-fila-v num-tabular">' + fmt(r.v, 'mdp1') + '</span></div>' +
        '<span class="au-riel"><span class="au-barra" data-w="' + (r.v / mayor * 100).toFixed(2) + '" style="width:0%"></span></span>' +
        (r.sub ? '<span class="au-fila-sub">' + esc(r.sub) + '</span>' : '') +
      '</li>';
    }).join('') : '<li class="au-fila au-fila-sub">Ninguno de estos informes trae el dato.</li>';
    return '<section class="au-sec" aria-labelledby="auRasTit">' +
      '<div class="au-sec-cab"><h2 class="au-sec-tit" id="auRasTit"><span class="au-num" aria-hidden="true">3</span> ' + esc(p.rastroTit) + (p.rastroEst ? ' ' + chip(p.rastroEst) : '') + '</h2>' +
      '<p class="au-sec-txt">Renglón por renglón. Cada nombre con ↗ abre el documento oficial.</p></div>' +
      '<ul class="au-rastro" id="auRastro">' + filas + '</ul></section>';
  }

  // --- 4 y 5. Lo que se encontro y a donde seguir ----------------------------
  function htmlCierre(p) {
    var acciones = p.acciones.filter(function (a) { return a.url || a.href; }).map(function (a) {
      return a.url
        ? '<a class="au-accion au-accion-2" href="' + esc(a.url) + '" target="_blank" rel="noopener noreferrer">' + esc(a.txt) + ' ↗</a>'
        : '<a class="au-accion" href="' + esc(a.href) + '">' + esc(a.txt) + ' ➔</a>';
    }).join('');
    return '<section class="au-sec" aria-labelledby="auHallTit">' +
      '<div class="au-sec-cab"><h2 class="au-sec-tit" id="auHallTit"><span class="au-num" aria-hidden="true">4</span> Lo que se encontró</h2></div>' +
      '<div class="au-hallazgo"><span class="au-hallazgo-ico" aria-hidden="true">🔎</span><p>' + esc(p.hallazgo) + '</p></div>' +
      (p.pendiente ? '<p class="au-pendiente">' + chip('pendiente') + ' ' + esc(p.pendiente) + '</p>' : '') +
      '<p class="au-fuente"><b>Fuente:</b> ' + esc(p.fuente) + '</p></section>' +
      '<section class="au-sec" aria-labelledby="auSigTit">' +
      '<div class="au-sec-cab"><h2 class="au-sec-tit" id="auSigTit"><span class="au-num" aria-hidden="true">5</span> Sigue investigando</h2></div>' +
      '<div class="au-acciones">' + acciones + '</div></section>';
  }

  // --- Arranque -------------------------------------------------------------
  var id = raiz.dataset.id, p = null;
  try { p = ARMA[id] ? ARMA[id]() : null; } catch (err) { p = null; }
  if (!p) {
    raiz.innerHTML = '<p class="au-pendiente">' + chip('pendiente') + ' La base no trae todavía los datos de esta auditoría.</p>';
    return;
  }
  raiz.innerHTML = htmlMapa(p) + htmlEscena(p) + htmlRastro(p) + htmlCierre(p);
  armarMapa();
  armarReparto();
  if (p.escena.tipo === 'reloj') armarReloj(p);
  if (p.escena.tipo === 'fuga') armarFuga(p);

  /* Las barras del rastro crecen cuando el lector llega a ellas. */
  var rastro = document.getElementById('auRastro');
  if (rastro && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (en) {
      if (en[0].isIntersecting) { io.disconnect(); contar(rastro, 1200); }
    }, { threshold: 0.2 });
    io.observe(rastro);
  } else if (rastro) contar(rastro, 0);
})();
