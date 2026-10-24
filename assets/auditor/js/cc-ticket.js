/* Auditavisión · Calculadora Cívica › Tu estado de cuenta (aplicación 1,
   12-10-2026). La página la escribe herramientas/cc_ticket.py con las tablas
   oficiales ya pintadas y, en JSON (#ctDatos), los mismos parámetros que usa
   el motor (calculadora_civica, panoramaErario y poderes de AUDIT_DB).
   Aquí solo se calcula con la cifra del lector, que no sale del navegador:
   las reglas son las de ccDesdeBruto, ccDesdeNeto, ccCalcularResultado,
   ccReparto y eccDatos de audit-engine.js.

   Corrección frente al motor: en actividad empresarial, la deducción
   escrita «al año» se divide entre doce antes de restarla al mes.
   El folio sale de la huella SHA-256 de las cifras y de la entrada; la liga
   ?verifica= de esta misma página la recalcula. */
(function () {
  'use strict';

  /* La aplicacion 1 solo presenta las cuatro cuentas (22-10-2026): una liga
     de verificacion o un ancla vieja (#ctPaso3) va a la pagina de su cuenta. */
  var portada = document.getElementById('ctPortada');
  if (portada) {
    var ancla = /^#ctPaso([1-4])$/.exec(location.hash);
    if (/[?&]verifica=/.test(location.search)) location.replace(portada.getAttribute('data-paso4') + location.search);
    else if (ancla) location.replace(portada.getAttribute('data-paso' + ancla[1]));
    return;
  }

  var D;
  try { D = JSON.parse(document.getElementById('ctDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  if (!$('ctRaiz')) return;

  var DIAS_MES = 30, CLAVE = 'av-ct-cuenta';
  var par = D.par;
  var regPorId = {};
  D.regimenes.forEach(function (r) { regPorId[r.id] = r; });

  var est = { m: 0, per: 'mes', nat: 'bruto', reg: 'sueldos', plat: 'transporte', ded: 0, iva: 50, rper: 'ano',
              calculado: false, res: null, folio: null, huella: null, verifica: null };

  /* ---------------- utilerías ---------------- */
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function pesos(v) { return '$' + Math.round(v).toLocaleString('es-MX'); }
  function pesos2(v) {
    return '$' + (Math.round(v * 100) / 100).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function finos(v) { return Math.abs(v) < 1000 ? pesos2(v) : pesos(v); }
  function chip(e) { return '<span class="est-chip est-' + e + '">' + e + '</span>'; }
  function leer(txt) {
    var n = parseFloat(String(txt == null ? '' : txt).replace(/[^0-9.\-]/g, ''));
    return isFinite(n) && n > 0 ? n : 0;
  }
  var reducido = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------- el cálculo (mismo del motor) ---------------- */
  function regimen(id) { return regPorId[id || est.reg] || D.regimenes[0]; }
  function efectivo() { var r = regimen(); return r.hereda ? regimen(r.hereda) : r; }

  function tarifa(base) {
    var t = D.tarifa;
    if (!(base > 0)) return { isr: 0, renglon: null, i: -1 };
    for (var i = 0; i < t.length; i++) {
      var r = t[i];
      if (r.ls === null || base <= r.ls) return { isr: Math.max(0, r.cf + (base - r.li) * r.pct / 100), renglon: r, i: i };
    }
    var u = t[t.length - 1];
    return { isr: Math.max(0, u.cf + (base - u.li) * u.pct / 100), renglon: u, i: t.length - 1 };
  }

  function cuotasIMSS(sbc) {
    var topeMes = D.imss.tope * par.uma.diaria * DIAS_MES, tresUma = 3 * par.uma.diaria * DIAS_MES;
    var base = Math.min(Math.max(0, sbc), topeMes);
    var det = D.imss.ramos.map(function (r) {
      var b = r.base === 'excedente_3_uma' ? Math.max(0, base - tresUma) : base;
      return { ramo: r.ramo, pct: r.pct, ley: r.ley, base: b, monto: b * r.pct / 100 };
    });
    return { detalle: det, total: det.reduce(function (a, x) { return a + x.monto; }, 0), base: base, topeMes: topeMes, topado: sbc > topeMes };
  }

  function subsidio(m) {
    if (!(m > 0) || m > par.sub.tope) return 0;
    return par.uma.mensual * par.sub.pct / 100;
  }

  function resicoRenglon(m) {
    var t = D.resico;
    for (var i = 0; i < t.length; i++) if (m <= t[i].hasta) return t[i];
    return t[t.length - 1];
  }

  /* Deducción mensual: la que se escribe «al año» se divide entre doce. */
  function dedMes() { return est.per === 'ano' ? est.ded / 12 : est.ded; }

  function desdeBruto(bruto) {
    var reg = efectivo();
    var r = { bruto: bruto, regimen: reg, base: bruto, deducido: 0, motivo: null, isrTarifa: 0, subsidio: 0, isr: 0,
              tasa: null, renglon: null, ri: -1, cuotas: null, cuotasTotal: 0, retCliente: 0 };
    var t;
    if (reg.id === 'sueldos') {
      t = tarifa(bruto);
      r.renglon = t.renglon; r.ri = t.i; r.isrTarifa = t.isr;
      r.subsidio = Math.min(subsidio(bruto), t.isr);
      r.isr = Math.max(0, t.isr - r.subsidio);
      r.cuotas = cuotasIMSS(bruto);
      r.salarioMinimo = bruto > 0 && bruto <= par.sm.mensual_general + 0.005;
      if (r.salarioMinimo) {
        r.isr = 0; r.subsidio = 0;
        r.cuotas.detalle.forEach(function (x) { x.monto = 0; });
        r.cuotas.total = 0; r.cuotas.exenta = true;
      }
    } else if (reg.id === 'resico') {
      var tr = resicoRenglon(bruto);
      r.tasa = tr.tasa; r.isr = bruto * tr.tasa / 100; r.isrTarifa = r.isr;
    } else if (reg.id === 'honorarios') {
      var ded = Math.min(Math.max(0, dedMes() || 0), bruto);
      r.deducido = ded; r.motivo = 'Deducciones autorizadas que declaraste';
      r.base = bruto - ded;
      t = tarifa(r.base);
      r.renglon = t.renglon; r.ri = t.i; r.isr = t.isr; r.isrTarifa = t.isr;
      r.retCliente = bruto * 0.10;
    } else if (reg.id === 'arrendamiento') {
      r.deducido = bruto * 0.35;
      r.motivo = 'Deducción opcional del 35% del artículo 115, sin comprobar gasto alguno';
      r.base = bruto - r.deducido;
      t = tarifa(r.base);
      r.renglon = t.renglon; r.ri = t.i; r.isr = t.isr; r.isrTarifa = t.isr;
      r.retCliente = bruto * 0.10;
    } else if (reg.id === 'plataformas') {
      var op = (reg.tasas || []).filter(function (x) { return x.id === est.plat; })[0] || reg.tasas[0];
      r.plataforma = op; r.tasa = op.pct; r.isr = bruto * op.pct / 100; r.isrTarifa = r.isr;
    }
    r.cuotasTotal = r.cuotas ? r.cuotas.total : 0;
    r.retenido = r.isr + r.cuotasTotal;
    r.neto = bruto - r.retenido;
    r.pctRetenido = bruto > 0 ? r.retenido / bruto * 100 : 0;
    r.pctIsr = bruto > 0 ? r.isr / bruto * 100 : 0;
    r.marginal = r.renglon ? r.renglon.pct : (r.tasa || 0);
    return r;
  }

  function desdeNeto(neto) {
    if (!(neto > 0)) return desdeBruto(0);
    var lo = neto, hi = neto * 3 + 100000;
    for (var i = 0; i < 90; i++) {
      var m = (lo + hi) / 2;
      if (desdeBruto(m).neto < neto) lo = m; else hi = m;
    }
    return desdeBruto((lo + hi) / 2);
  }

  function reparto(isrAnual) {
    var total = D.egresos.reduce(function (a, e) { return a + e.m; }, 0);
    return D.egresos.map(function (e) {
      return { id: e.id, nombre: e.nombre, icono: e.icono, pct: total ? e.m / total * 100 : 0, monto: total ? isrAnual * e.m / total : 0 };
    }).sort(function (a, b) { return b.monto - a.monto; });
  }

  function resultado() {
    var mensual = est.per === 'ano' ? est.m / 12 : est.m;
    var mes = est.nat === 'neto' ? desdeNeto(mensual) : desdeBruto(mensual);
    var x = function (v) { return v * 12; };
    return {
      mes: mes,
      ano: { bruto: x(mes.bruto), isr: x(mes.isr), cuotasTotal: x(mes.cuotasTotal), subsidio: x(mes.subsidio),
             retenido: x(mes.retenido), neto: x(mes.neto), base: x(mes.base), deducido: x(mes.deducido), retCliente: x(mes.retCliente) },
      reparto: reparto(x(mes.isr))
    };
  }

  /* ---------------- animación de cifras ---------------- */
  var anims = {};
  function contar(el, hasta, fmt, ms) {
    if (!el) return;
    var desde = parseFloat(el.dataset.v || '0') || 0;
    el.dataset.v = hasta;
    if (anims[el.id || el.dataset.k]) cancelAnimationFrame(anims[el.id || el.dataset.k]);
    if (reducido || !ms || desde === hasta) { el.textContent = fmt(hasta); return; }
    var t0 = null, k = el.id || el.dataset.k;
    function paso(t) {
      if (!t0) t0 = t;
      var p = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(desde + (hasta - desde) * e);
      if (p < 1) anims[k] = requestAnimationFrame(paso);
    }
    anims[k] = requestAnimationFrame(paso);
  }

  /* ---------------- paso 1: el formulario ---------------- */
  var inMonto = $('ctMonto'), rango = $('ctRango'), inDed = $('ctDed');

  /* La barra es logarítmica: de $1,000 a $500,000 al mes (o doce veces eso
     al año), para que lo mismo se pueda afinar un sueldo chico que uno alto. */
  var RMIN = 1000, RMAX = 500000;
  function factorPer() { return est.per === 'ano' ? 12 : 1; }
  function rangoAMonto(v) {
    if (v <= 0) return 0;
    var m = RMIN * Math.pow(RMAX / RMIN, v / 1000) * factorPer();
    var paso = m < 20000 ? 50 : m < 100000 ? 100 : m < 1000000 ? 500 : 1000;
    return Math.round(m / paso) * paso;
  }
  function montoARango(m) {
    if (!(m > 0)) return 0;
    var v = Math.log(m / factorPer() / RMIN) / Math.log(RMAX / RMIN) * 1000;
    return Math.max(1, Math.min(1000, Math.round(v)));
  }

  function pintarControles() {
    [].forEach.call(document.querySelectorAll('[data-per]'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.per === est.per)); });
    [].forEach.call(document.querySelectorAll('[data-nat]'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.nat === est.nat)); });
    [].forEach.call(document.querySelectorAll('[data-reg]'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.reg === est.reg)); });
    [].forEach.call(document.querySelectorAll('[data-plat]'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.plat === est.plat)); });
    var efe = efectivo();
    $('ctOpHon').hidden = efe.id !== 'honorarios';
    $('ctOpPlat').hidden = efe.id !== 'plataformas';
    $('ctOpNose').hidden = est.reg !== 'nose';
    $('ctDedPer').textContent = est.per === 'ano' ? 'al año' : 'al mes';
    [].forEach.call(document.querySelectorAll('.ct-preset'), function (b) {
      b.setAttribute('aria-pressed', String(est.per === 'mes' && Math.abs(parseFloat(b.dataset.monto) - est.m) < 0.005));
    });
    $('ctCalcTx').textContent = est.calculado ? 'Rehacer la cuenta' : 'Sacar la cuenta';
    $('ctEstado').textContent = est.calculado
      ? '✅ Cuenta hecha con el régimen de ' + efe.nombre.toLowerCase() + '. Cambia cualquier dato y se rehace sola.'
      : '⚪ Todo está en ceros ($0). Escribe tu ingreso, elige tu régimen y pulsa «Sacar la cuenta».';
  }

  function escribirMonto() {
    inMonto.value = est.m > 0 ? est.m.toLocaleString('es-MX', { maximumFractionDigits: 2 }) : '';
  }

  /* El sueldo se comparte con «Tú contra ellos» (herramienta-calculadora-
     compara.html) bajo una sola clave: {monto, periodo: 'mes'|'anio',
     tipo: 'bruto'|'neto'}. Lo propio de esta página (régimen, plataforma,
     deducción y escenario del IVA) va en su clave aparte. */
  var COMPARTIDA = 'auditavision_cc_sueldo';
  function guardar() {
    if (est.verifica) return;   /* una liga ajena no pisa lo que este equipo recuerda */
    try {
      if (est.m > 0) {
        localStorage.setItem(COMPARTIDA, JSON.stringify({ monto: est.m, periodo: est.per === 'ano' ? 'anio' : 'mes', tipo: est.nat }));
        localStorage.setItem(CLAVE, JSON.stringify({ reg: est.reg, plat: est.plat, ded: est.ded, iva: est.iva }));
      } else {
        localStorage.removeItem(COMPARTIDA);
        localStorage.removeItem(CLAVE);
      }
    } catch (e) { /* sin almacenamiento: no pasa nada */ }
  }
  function recuperar() {
    try {
      var s = JSON.parse(localStorage.getItem(COMPARTIDA) || 'null');
      var g = JSON.parse(localStorage.getItem(CLAVE) || 'null') || {};
      if (!s || !(leer(s.monto) > 0)) return false;
      g.m = s.monto; g.per = s.periodo === 'anio' ? 'ano' : 'mes'; g.nat = s.tipo;
      aplicar(g);
      return true;
    } catch (e) { return false; }
  }
  function aplicar(g) {
    est.m = leer(g.m);
    if (g.per === 'mes' || g.per === 'ano') est.per = g.per;
    if (g.nat === 'bruto' || g.nat === 'neto') est.nat = g.nat;
    if (regPorId[g.reg]) est.reg = g.reg;
    var pl = (regPorId.plataformas || {}).tasas || [];
    if (pl.some(function (x) { return x.id === g.plat; })) est.plat = g.plat;
    est.ded = leer(g.ded);
    var iv = parseInt(g.iva, 10);
    if (iv >= 0 && iv <= 100) est.iva = iv;
  }

  var tCalc = null;
  function programar(ms) {
    clearTimeout(tCalc);
    tCalc = setTimeout(function () { if (est.m > 0) calcular(false); else ceros(false); }, ms == null ? 160 : ms);
  }

  /* En cuanto el lector toca algo, la liga de verificacion deja de mandar. */
  function usuario() {
    if (!est.verifica) return;
    est.verifica = null; $('ctVerif').hidden = true;
    history.replaceState(null, '', location.pathname);
  }

  inMonto.addEventListener('input', function () {
    usuario();
    est.m = leer(inMonto.value);
    rango.value = montoARango(est.m);
    if (est.calculado || est.m > 0) programar(); else pintarControles();
  });
  inMonto.addEventListener('keydown', function (e) { if (e.key === 'Enter') calcular(true); });
  inMonto.addEventListener('blur', escribirMonto);
  rango.addEventListener('input', function () {
    usuario();
    est.m = rangoAMonto(parseInt(rango.value, 10));
    escribirMonto();
    programar(40);
  });
  inDed.addEventListener('input', function () { usuario(); est.ded = leer(inDed.value); if (est.calculado) programar(); });
  inDed.addEventListener('keydown', function (e) { if (e.key === 'Enter') calcular(true); });

  $('ctRaiz').addEventListener('click', function (ev) {
    var b = ev.target.closest('button');
    if (!b) return;
    var d = b.dataset;
    if (d.per || d.nat || d.reg || d.plat || d.monto) usuario();
    if (d.per) { est.per = d.per; rango.value = montoARango(est.m); }
    else if (d.nat) est.nat = d.nat;
    else if (d.reg) est.reg = d.reg;
    else if (d.plat) est.plat = d.plat;
    else if (d.monto) {
      est.m = parseFloat(d.monto); est.per = 'mes';
      if (d.oficial) { est.nat = 'bruto'; est.reg = 'sueldos'; }
      escribirMonto(); rango.value = montoARango(est.m);
      calcular(false); return;
    } else if (d.rper) { est.rper = d.rper; pintarReparto(); return; }
    else return;
    pintarControles();
    if (est.calculado) calcular(false);
  });

  $('ctCalcular').addEventListener('click', function () { usuario(); est.m = leer(inMonto.value); calcular(true); });
  $('ctEjemplo').addEventListener('click', function () {
    usuario();
    est.m = par.sm.mensual_general; est.per = 'mes'; est.nat = 'bruto'; est.reg = 'sueldos';
    escribirMonto(); rango.value = montoARango(est.m);
    calcular(true);
  });
  $('ctReiniciar').addEventListener('click', function () {
    usuario();
    est.m = 0; est.ded = 0; inDed.value = '0'; escribirMonto(); rango.value = 0;
    ceros(true);
  });

  /* ---------------- paso 2: lo que te retienen ---------------- */
  function caja(cls, rot, v, nota, id) {
    return '<div class="ct-caja-res ' + cls + '"><span class="ct-res-et">' + rot + '</span>' +
      '<b class="ct-res-v" id="' + id + '">$0.00</b>' + (nota ? '<span class="ct-res-sub">' + nota + '</span>' : '') + '</div>';
  }

  function pintarRetencion() {
    var res = est.res, m = res.mes, a = res.ano, reg = efectivo(), elegido = regimen();
    var anual = est.per === 'ano', per = anual ? 'al año' : 'al mes', v = anual ? a : m, f = anual ? 12 : 1;

    $('ctRetSub').innerHTML = (elegido.id === 'nose' ? 'Calculado como sueldos y salarios, que es el supuesto que aceptaste al no saber tu régimen. ' : '') +
      esc(reg.quien_es) + ' <b>Retiene:</b> ' + esc(reg.retiene);

    $('ctResumen').innerHTML =
      caja('ct-r-bruto', 'Ingreso bruto ' + per, v.bruto, 'Antes de cualquier descuento', 'ctRB') +
      caja('ct-r-isr', 'Impuesto sobre la renta', v.isr, 'Tasa efectiva sobre el bruto: <b>' + m.pctIsr.toFixed(2) + '%</b>', 'ctRI') +
      (m.cuotas ? caja('ct-r-imss', 'Cuotas al Seguro Social', v.cuotasTotal, 'Cuota obrera: 2.375% del salario base más 0.40% del excedente de tres UMA', 'ctRS')
                : caja('ct-r-imss ct-r-nula', 'Cuotas al Seguro Social', 0, 'Este régimen no cotiza por sí mismo', 'ctRS')) +
      caja('ct-r-neto', 'Te queda ' + per, v.neto, 'Se te va el <b>' + m.pctRetenido.toFixed(2) + '%</b> de lo que ganas', 'ctRN');
    contar($('ctRB'), v.bruto, pesos2, 700);
    contar($('ctRI'), v.isr, pesos2, 700);
    contar($('ctRS'), v.cuotasTotal, pesos2, 700);
    contar($('ctRN'), v.neto, pesos2, 700);

    var filas = [];
    filas.push({ k: 'Ingreso bruto ' + per, v: v.bruto, t: 'base', d: est.nat === 'neto' ? 'Calculado hacia atrás desde el neto que escribiste.' : 'La cifra que escribiste.' });
    if (v.deducido > 0) {
      filas.push({ k: m.motivo, v: v.deducido, t: 'fiscal', d: 'No es dinero que pierdas: te lo quedas. Lo único que hace es achicar la cantidad sobre la que corre la tarifa.' });
      filas.push({ k: 'Base gravable', v: v.base, t: 'subtotal', d: 'Sobre esta cantidad, y no sobre el ingreso, corre la tarifa. Es un subtotal: no se suma aparte, resume los dos renglones de arriba.' });
    }
    if (m.renglon) {
      filas.push({ k: 'Impuesto de la tarifa', v: -(m.isrTarifa * f), t: 'impuesto',
                   d: 'Cuota fija de ' + pesos2(m.renglon.cf) + ' más ' + m.renglon.pct + '% sobre lo que excede ' + pesos2(m.renglon.li) + ' mensuales.' });
    } else if (m.tasa !== null) {
      filas.push({ k: 'Impuesto sobre la renta', v: -(m.isr * f), t: 'impuesto', d: 'Tasa única de ' + m.tasa + '% sobre el ingreso, sin deducción alguna.' });
    }
    if (m.salarioMinimo && m.isrTarifa > 0) {
      filas.push({ k: 'Exención por salario mínimo', v: m.isrTarifa * f, t: 'suma',
                   d: 'Último párrafo del artículo 96 de la Ley del ISR: no se efectúa retención a quien en el mes únicamente percibe un salario mínimo general.' });
    }
    if (m.subsidio > 0) {
      filas.push({ k: 'Subsidio para el empleo', v: v.subsidio, t: 'suma',
                   d: 'El valor mensual de la UMA por ' + par.sub.pct + '%. Se resta del impuesto; si lo rebasa, no se entrega la diferencia.' });
    }
    if (m.cuotas && m.cuotas.exenta) {
      filas.push({ k: 'Cuota obrera del Seguro Social', v: 0, t: 'suma',
                   d: 'Artículo 36 de la Ley del Seguro Social: cuando el trabajador percibe como cuota diaria el salario mínimo, el patrón paga íntegramente también la cuota que normalmente le tocaría a él.' });
    } else if (m.cuotas) {
      m.cuotas.detalle.forEach(function (x) { if (x.monto > 0) filas.push({ k: x.ramo, v: -(x.monto * f), t: 'cuota', d: x.ley }); });
    }
    filas.push({ k: 'Te queda ' + per, v: v.neto, t: 'neto', d: est.nat === 'neto' ? 'La cifra que escribiste.' : 'Lo que efectivamente recibes.' });
    var mayor = Math.max.apply(null, filas.map(function (x) { return Math.abs(x.v); })) || 1;

    $('ctCascTit').textContent = 'Renglón por renglón, ' + per;
    $('ctCascada').innerHTML = filas.map(function (x, i) {
      var sig = x.t === 'fiscal' ? '·' : (x.t === 'base' || x.t === 'subtotal' || x.t === 'neto') ? '=' : (x.v < 0 ? '−' : '+');
      return '<li class="ct-casc ct-casc-' + x.t + '" style="--ct-i:' + i + '">' +
        '<span class="ct-casc-k"><span class="ct-casc-sig" aria-hidden="true">' + sig + '</span>' + esc(x.k) + '</span>' +
        '<span class="ct-casc-v">' + pesos2(Math.abs(x.v)) + '</span>' +
        '<span class="ct-casc-riel" aria-hidden="true"><span class="ct-casc-barra" style="--ct-w:' + (Math.abs(x.v) / mayor * 100).toFixed(2) + '%"></span></span>' +
        '<span class="ct-casc-d">' + esc(x.d) + '</span></li>';
    }).join('');

    /* El escalón: la operación de la tarifa con tus números. */
    var esca = '';
    if (m.renglon) {
      esca = '<p><b>Así se calcula tu ISR del mes:</b> cuota fija ' + pesos2(m.renglon.cf) + ' + ' + m.renglon.pct + '% × (' + pesos2(m.base) +
        ' − ' + pesos2(m.renglon.li) + ') = <b>' + pesos2(m.isrTarifa) + '</b>' +
        (m.subsidio > 0 ? '; menos el subsidio de ' + pesos2(m.subsidio) + ' = <b>' + pesos2(m.isr) + '</b>' : '') + '.</p>';
    } else if (m.tasa !== null) {
      esca = '<p><b>Así se calcula tu ISR del mes:</b> ' + pesos2(m.bruto) + ' × ' + m.tasa + '% = <b>' + pesos2(m.isr) + '</b>.</p>';
    }
    $('ctEscalon').innerHTML = esca;

    /* Tablas: se marca tu renglón. */
    var esResico = reg.id === 'resico';
    $('ctTarifaDet').hidden = !m.renglon;
    $('ctResicoDet').hidden = !esResico;
    $('ctImssDet').hidden = !m.cuotas;
    [].forEach.call($('ctTarifa').querySelectorAll('tbody tr'), function (tr) {
      var si = parseInt(tr.dataset.i, 10) === m.ri;
      tr.classList.toggle('ct-tr-tuyo', si);
      tr.classList.toggle('ct-tr-lejos', m.ri >= 0 && Math.abs(parseInt(tr.dataset.i, 10) - m.ri) > 2);
    });
    [].forEach.call($('ctResico').querySelectorAll('tbody tr'), function (tr) {
      tr.classList.toggle('ct-tr-tuyo', esResico && parseFloat(tr.dataset.tasa) === m.tasa);
    });

    pintarIva();

    /* Avisos */
    var h = '<p class="ct-aviso"><b>Efectiva y marginal no son lo mismo.</b> Tu tasa <em>efectiva</em> de impuesto sobre la renta es <b>' +
      m.pctIsr.toFixed(2) + '%</b>: lo que pagas entre lo que ganas. Tu tasa <em>marginal</em> es <b>' + m.marginal.toFixed(2) +
      '%</b>: lo que pagarías por el siguiente peso que ganaras. La segunda siempre es mayor en una tarifa progresiva, y confundirlas es el error más frecuente al leer un cuadro como el de la tarifa.</p>';
    if (m.retCliente > 0) {
      h += '<p class="ct-aviso"><b>Ojo con la retención del cliente.</b> Si quien te paga es una persona moral, te retendrá ' + pesos2(m.retCliente * f) + ' ' + per +
        ' —el 10% de lo facturado, sin deducción alguna—. <b>Eso no es el impuesto: es un anticipo</b> que se acredita contra lo que aquí aparece. ' + esc(reg.punto_ciego) + '</p>';
    }
    if (m.salarioMinimo) {
      h += '<p class="ct-aviso ct-aviso-bueno"><b>No te retienen nada, y por dos leyes distintas.</b> Tu ingreso equivale a un salario mínimo general, hoy ' + pesos2(par.sm.general) +
        ' diarios. El último párrafo del artículo 96 de la Ley del ISR prohíbe retener el impuesto a quien en el mes únicamente percibe un salario mínimo, y el artículo 36 de la Ley del Seguro Social ordena que en ese caso el patrón pague íntegramente también la cuota obrera. <b>Lo bruto y lo neto coinciden.</b> En la Zona Libre de la Frontera Norte el mínimo es ' +
        pesos2(par.sm.frontera_norte) + ' diarios y la misma regla opera a partir de ' + pesos2(par.sm.mensual_frontera) + ' al mes; esta cuenta usa el mínimo general del resto del país.</p>';
    }
    if (m.cuotas && m.cuotas.topado) {
      h += '<p class="ct-aviso"><b>Tu salario rebasa el tope de cotización.</b> El artículo 28 de la Ley del Seguro Social fija el límite superior en veinticinco veces la referencia diaria, hoy ' +
        pesos2(m.cuotas.topeMes) + ' al mes. De ahí hacia arriba el sueldo sube y la cuota ya no: por eso la carga de seguridad social pesa proporcionalmente más sobre los salarios bajos.</p>';
    }
    if (esResico && D.resicoTope && a.bruto > D.resicoTope) {
      h += '<p class="ct-aviso ct-aviso-error"><b>Rebasas el tope del RESICO.</b> El artículo 113-E de la Ley del ISR lo limita a quien no pasa de ' + pesos(D.resicoTope) +
        ' al año, y tu ingreso equivale a ' + pesos(a.bruto) + ' al año: con ese ingreso tributarías en otro régimen.</p>';
    }
    h += '<p class="ct-pie-reg">' + esc(reg.punto_ciego) + '</p>';
    $('ctAvisos').innerHTML = h;
  }

  function pintarIva() {
    if (!est.res) return;
    var a = est.res.ano, gastado = a.neto * est.iva / 100;
    var iva = gastado - gastado / (1 + par.iva / 100);
    var sobre = a.bruto > 0 ? iva / a.bruto * 100 : 0;
    $('ctIvaPct').textContent = est.iva + '%';
    $('ctIvaAno').textContent = pesos(iva);
    $('ctIvaSobre').textContent = sobre.toFixed(2) + '%';
    $('ctIvaSuma').textContent = (est.res.mes.pctRetenido + sobre).toFixed(2) + '%';
  }
  var ivaR = $('ctIvaRango');
  ivaR.addEventListener('input', function () { est.iva = parseInt(ivaR.value, 10) || 0; pintarIva(); guardar(); });

  /* ---------------- paso 3: a dónde va cada peso ---------------- */
  function pintarReparto() {
    var res = est.res, isr = res ? res.ano.isr : 0;
    var div = est.rper === 'mes' ? 12 : est.rper === 'dia' ? 365 : 1;
    var etq = est.rper === 'mes' ? 'al mes' : est.rper === 'dia' ? 'al día' : 'al año';
    [].forEach.call(document.querySelectorAll('[data-rper]'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.rper === est.rper)); });
    $('ctRepSub').firstChild.nodeValue = res
      ? 'Tus ' + pesos(isr) + ' de impuesto sobre la renta al año, repartidos con las mismas proporciones del Presupuesto de Egresos aprobado para 2026 '
      : 'Tu impuesto sobre la renta, repartido con las mismas proporciones del Presupuesto de Egresos aprobado para 2026 ';
    var mayor = 0;
    var por = {};
    (res ? res.reparto : reparto(0)).forEach(function (x) { por[x.id] = x; if (x.pct > mayor) mayor = x.pct; });
    [].forEach.call(document.querySelectorAll('.ct-rub'), function (li, i) {
      var x = por[li.dataset.id];
      if (!x) return;
      var b = li.querySelector('[data-tuyo]');
      b.dataset.k = 'rub' + i;
      contar(b, x.monto / div, finos, 600);
      li.querySelector('[data-tuyo-largo]').textContent = pesos2(x.monto / div) + ' ' + etq;
      li.querySelector('.ct-rub-barra').style.setProperty('--ct-w', (res && isr > 0 ? x.pct / mayor * 100 : 0).toFixed(2) + '%');
    });
    $('ctAparte').hidden = !(res && res.ano.cuotasTotal > 0);
    if (res) $('ctAparteV').textContent = pesos(res.ano.cuotasTotal);
  }

  document.getElementById('ctReparto').addEventListener('click', function (ev) {
    var b = ev.target.closest('.ct-rub-b');
    if (!b) return;
    var abierto = b.getAttribute('aria-expanded') === 'true';
    b.setAttribute('aria-expanded', String(!abierto));
    $(b.getAttribute('aria-controls')).hidden = abierto;
    b.parentNode.classList.toggle('ct-rub-on', !abierto);
  });

  /* ---------------- paso 4: el estado de cuenta ---------------- */
  function hoy() { return new Date().toLocaleDateString('es-MX', { day: '2-digit', month: '2-digit', year: 'numeric' }); }

  function datosDoc() {
    var res = est.res;
    if (!res || !est.calculado) return null;
    var anual = est.per === 'ano', p = anual ? res.ano : res.mes;
    if (!res.reparto.length || !(p.isr > 0)) return null;
    var factor = anual ? 1 : 1 / 12;
    var P = D.poderes;
    var poderes = P ? P.ramos.map(function (r) {
      return { k: r.k, icono: r.k === 'legislativo' ? '🏛️' : '⚖️', nombre: r.nombre, ramo: r.ramo,
               monto: p.isr * r.aprobado / P.gnt, pct: r.aprobado / P.gnt * 100 };
    }) : [];
    var reg = efectivo();
    return {
      cad: anual ? 'al año' : 'al mes',
      periodo: anual ? 'Ejercicio 2026 · anual' : 'Ejercicio 2026 · mensual',
      regimen: reg.nombre,
      bruto: p.bruto, isr: p.isr, cuotas: p.cuotasTotal, neto: p.neto,
      movimientos: res.reparto.map(function (x) { return { id: x.id, icono: x.icono, nombre: x.nombre, pct: x.pct, monto: x.monto * factor }; }),
      poderes: poderes,
      ellos: D.dip && res.ano.neto > 0 ? { cargo: D.dip.cargo, veces: D.dip.netoAnual / res.ano.neto, netoAnual: D.dip.netoAnual, pagina: D.dip.pagina } : null,
      emitido: hoy()
    };
  }

  /* Lo que firma la huella: la entrada y las cifras del documento, en un
     orden fijo y con centavos. La fecha no entra: los mismos datos dan
     siempre el mismo folio. */
  function entrada() {
    var e = { m: Math.round(est.m * 100) / 100, p: est.per, n: est.nat, r: est.reg };
    if (efectivo().id === 'plataformas') e.pl = est.plat;
    if (efectivo().id === 'honorarios') e.d = Math.round(est.ded * 100) / 100;
    return e;
  }
  function firmable(d) {
    var c2 = function (v) { return (Math.round(v * 100) / 100).toFixed(2); };
    return {
      doc: 'Auditavisión · Estado de cuenta cívico', v: 1, entrada: entrada(),
      cifras: [['bruto', c2(d.bruto)], ['isr', c2(d.isr)], ['cuotas', c2(d.cuotas)], ['neto', c2(d.neto)]],
      movimientos: d.movimientos.map(function (x) { return [x.id, c2(x.monto)]; }),
      poderes: d.poderes.map(function (x) { return [x.k, c2(x.monto)]; }),
      ellos: d.ellos ? [d.ellos.cargo, d.ellos.veces.toFixed(1)] : null
    };
  }
  function huellaDe(obj) {
    if (!(window.crypto && crypto.subtle && window.TextEncoder)) return Promise.resolve(null);
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(obj))).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return ('0' + x.toString(16)).slice(-2); }).join('');
    }, function () { return null; });
  }
  function folioDe(h) { return 'AV-EC-' + h.slice(0, 8).toUpperCase(); }
  function ligaVerifica() {
    var e = entrada(), q = new URLSearchParams();
    q.set('verifica', est.folio || '');
    q.set('m', e.m); q.set('p', e.p); q.set('n', e.n); q.set('r', e.r);
    if (e.pl) q.set('pl', e.pl);
    if (e.d != null) q.set('d', e.d);
    return location.origin + location.pathname + '?' + q.toString();
  }

  function sello(fecha, folio) {
    var k = 'ctsl' + Math.random().toString(36).slice(2, 8);
    return '<div class="sello-av ct-sello" role="img" aria-label="Sello de emisión de Auditavisión, ' + esc(fecha) + (folio ? ', folio ' + esc(folio) : '') + '">' +
      '<svg viewBox="0 0 200 200" aria-hidden="true" focusable="false"><defs>' +
      '<path id="' + k + 'a" d="M 28,100 A 72,72 0 0,1 172,100"/><path id="' + k + 'b" d="M 22,100 A 78,78 0 0,0 178,100"/></defs>' +
      '<circle cx="100" cy="100" r="95" class="sello-disco"/>' +
      '<circle cx="100" cy="100" r="95" fill="none" stroke="currentColor" stroke-width="3.5"/>' +
      '<circle cx="100" cy="100" r="88" fill="none" stroke="currentColor" stroke-width="1"/>' +
      '<circle cx="100" cy="100" r="62" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="2 3"/>' +
      '<text class="sello-arco"><textPath href="#' + k + 'a" startOffset="50%" text-anchor="middle">AUDITAVISIÓN</textPath></text>' +
      '<text class="sello-arco sello-arco-b"><textPath href="#' + k + 'b" startOffset="50%" text-anchor="middle">SISTEMA CÍVICO DE FISCALIZACIÓN</textPath></text>' +
      '<text x="21" y="104" class="sello-estrella" text-anchor="middle">★</text><text x="179" y="104" class="sello-estrella" text-anchor="middle">★</text>' +
      '<image href="assets/auditor/img/logo-auditavision.svg" x="68" y="44" width="64" height="50"/>' +
      '<text x="100" y="110" text-anchor="middle" class="sello-emitido">EMITIDO</text>' +
      '<text x="100" y="127" text-anchor="middle" class="sello-fecha">' + esc(fecha) + '</text>' +
      (folio ? '<text x="100" y="142" text-anchor="middle" class="sello-folio ct-sello-folio">' + esc(folio) + '</text>' : '') +
      '</svg></div>';
  }

  var docPrevio = '';
  function pintarDoc() {
    var d = datosDoc(), marco = $('ctDocMarco'), acc = $('ctAcciones');
    if (!d) {
      marco.hidden = true; acc.hidden = true; est.folio = null; est.huella = null; docPrevio = '';
      $('ctDocSub').textContent = est.calculado
        ? 'Con este ingreso no pagas impuesto sobre la renta, así que no hay nada que repartir ni estado de cuenta que emitir. Lo que sí pagas es el IVA que va dentro del precio de lo que compras: míralo en el escenario del paso 2.'
        : 'Lo que ganaste, lo que te retuvieron y a dónde fue tu impuesto, en un solo documento con folio y huella. Aparece aquí en cuanto saques la cuenta.';
      return;
    }
    $('ctDocSub').textContent = 'Lo que ganaste, lo que te retuvieron y a dónde fue tu impuesto, en un solo documento que puedes descargar, imprimir o copiar.';
    var max = Math.max.apply(null, d.movimientos.map(function (x) { return x.monto; })) || 1;
    var movs = d.movimientos.map(function (x, i) {
      return '<div class="ct-mov" style="--ct-i:' + i + '"><span class="ct-mov-con">' + x.icono + ' ' + esc(x.nombre) + '</span>' +
        '<span class="ct-mov-bar"><i style="--ct-w:' + (x.monto / max * 100).toFixed(1) + '%"></i></span>' +
        '<span class="ct-mov-pct">' + x.pct.toFixed(1) + '%</span><span class="ct-mov-mon">' + pesos(x.monto) + '</span></div>';
    }).join('');
    var pod = d.poderes.length ? '<div class="ct-doc-sec"><p class="ct-doc-sec-tit">De ahí, lo que llega a los Poderes <small>(ya incluido arriba; no se suma)</small> ' + chip('derivado') + '</p>' +
      d.poderes.map(function (x) {
        return '<div class="ct-mov ct-mov-sub"><span class="ct-mov-con">' + x.icono + ' ' + esc(x.nombre) + ' · Ramo ' + esc(x.ramo) + '</span><span class="ct-mov-bar"></span>' +
          '<span class="ct-mov-pct">' + x.pct.toFixed(2) + '%</span><span class="ct-mov-mon">' + finos(x.monto) + '</span></div>';
      }).join('') + '<p class="ct-doc-liga"><a href="numeros-lo-que-cuestan-los-poderes.html">Ver en qué lo gastan →</a></p></div>' : '';
    var ellos = d.ellos ? '<div class="ct-ellos"><div class="ct-ellos-num">' + d.ellos.veces.toFixed(1) + '×</div><div class="ct-ellos-tx"><b>' + esc(d.ellos.cargo) +
      '</b>: recibe ' + d.ellos.veces.toFixed(1) + ' veces tu ingreso neto ' + chip('derivado') + ', ' + pesos(d.ellos.netoAnual) +
      ' netos al año según el Anexo 23 del PEF 2026' + (d.ellos.pagina ? ' (' + esc(d.ellos.pagina) + ')' : '') + ' ' + chip('oficial') +
      '. <a href="herramienta-calculadora-compara.html">Compárate con más cargos →</a></div></div>' : '';

    var html =
      '<header class="ct-doc-cab">' + sello(d.emitido, est.folio || '') +
        '<p class="ct-doc-marca">AUDITAVISIÓN · SISTEMA CÍVICO DE FISCALIZACIÓN</p>' +
        '<h3 class="ct-doc-tit" id="ctDocTit">Estado de Cuenta Cívico</h3>' +
        '<dl class="ct-doc-meta"><div><dt>Titular</dt><dd>Contribuyente</dd></div><div><dt>Periodo</dt><dd>' + d.periodo + '</dd></div>' +
        '<div><dt>Folio</dt><dd class="ct-folio">' + esc(est.folio || 'calculando…') + '</dd></div><div><dt>Emitido</dt><dd>' + d.emitido + '</dd></div></dl>' +
      '</header>' +
      '<div class="ct-doc-kpis">' +
        '<div class="ct-kpi"><span>Ingreso bruto</span><b>' + pesos(d.bruto) + '</b><small>' + d.cad + ' · ' + esc(d.regimen) + '</small></div>' +
        '<div class="ct-kpi ct-kpi-isr"><span>ISR pagado</span><b>' + pesos(d.isr) + '</b><small>impuesto: se reparte abajo</small></div>' +
        '<div class="ct-kpi ct-kpi-imss"><span>Cuotas IMSS</span><b>' + pesos(d.cuotas) + '</b><small>aportación con destino propio</small></div>' +
        '<div class="ct-kpi ct-kpi-neto"><span>Te queda</span><b>' + pesos(d.neto) + '</b><small>ingreso neto ' + d.cad + '</small></div>' +
      '</div>' +
      '<div class="ct-doc-sec"><p class="ct-doc-sec-tit">Movimientos: a dónde fue tu ISR ' + chip('derivado') + '</p><div class="ct-movs">' + movs + '</div></div>' +
      pod + ellos +
      '<footer class="ct-doc-pie">' +
        '<p><b>Cómo se calculó.</b> ISR con las tarifas del Anexo 8 de la Resolución Miscelánea Fiscal 2026; reparto con los renglones del Presupuesto de Egresos 2026. Los montos por renglón son derivados: tu ISR multiplicado por el peso de cada renglón en el gasto aprobado.</p>' +
        '<p class="ct-doc-huella">Huella digital (SHA-256 de tus datos y de estas cifras): <code class="ct-huella">' + esc(est.huella || 'calculando…') + '</code></p>' +
        '<p class="ct-doc-legal">Este documento es un ejercicio de divulgación. No es un comprobante fiscal ni sustituye tu constancia de retenciones.</p>' +
      '</footer>';
    var nuevo = JSON.stringify(firmable(d));
    var doc = $('ctDoc');
    doc.innerHTML = html;
    var cambio = nuevo !== docPrevio;
    docPrevio = nuevo;
    marco.hidden = false; acc.hidden = false;
    if (cambio && !reducido) { doc.classList.remove('ct-imprime'); void doc.offsetWidth; doc.classList.add('ct-imprime'); }

    var obj = firmable(d);
    huellaDe(obj).then(function (h) {
      if (JSON.stringify(obj) !== docPrevio) return;   /* llegó tarde: ya cambió la cuenta */
      est.huella = h; est.folio = h ? folioDe(h) : null;
      [].forEach.call(doc.querySelectorAll('.ct-folio'), function (el) { el.textContent = est.folio || 'no disponible en este navegador'; });
      [].forEach.call(doc.querySelectorAll('.ct-sello-folio'), function (el) { el.textContent = est.folio || ''; });
      var hu = doc.querySelector('.ct-huella');
      if (hu) hu.textContent = h || 'este navegador no calcula huellas SHA-256';
      if (!doc.querySelector('.ct-sello-folio') && est.folio) {
        var s = doc.querySelector('.ct-sello'); if (s) s.outerHTML = sello(d.emitido, est.folio);
      }
      comprobar();
    });
  }

  /* La verificación: ?verifica=AV-EC-…&m=…&p=…&n=…&r=… */
  function comprobar() {
    var v = est.verifica, out = $('ctVerif');
    if (!v) { out.hidden = true; return; }
    out.hidden = false;
    if (!est.calculado || !datosDoc()) {
      out.className = 'ct-verif ct-verif-no';
      out.innerHTML = '<b>❌ No se puede comprobar.</b> La liga no trae datos con los que se pague impuesto sobre la renta, así que no corresponde a ningún estado de cuenta cívico.';
      return;
    }
    if (!est.huella) {
      out.className = 'ct-verif ct-verif-no';
      out.innerHTML = 'Este navegador no puede calcular huellas SHA-256. Ábrelo en uno actualizado.';
      return;
    }
    var ok = v.toUpperCase() === est.folio || v.toLowerCase() === est.huella;
    out.className = 'ct-verif ' + (ok ? 'ct-verif-si' : 'ct-verif-no');
    out.innerHTML = ok
      ? '<b>✅ Auténtico.</b> El folio <b>' + esc(est.folio) + '</b> corresponde a estos datos y sus cifras coinciden con las tarifas y el presupuesto vigentes en la plataforma. Abajo está el documento, recalculado en tu navegador.'
      : '<b>❌ No coincide.</b> Con los datos de la liga, el folio sería <b>' + esc(est.folio) + '</b>, no ' + esc(v) +
        '. O el documento se alteró, o se emitió con datos anteriores de la plataforma: compara las cifras con las de abajo.';
  }

  /* ---------------- copiar, imprimir, imagen ---------------- */
  function avisar(t) {
    var el = $('ctCopiado'); el.textContent = t;
    clearTimeout(avisar.t); avisar.t = setTimeout(function () { el.textContent = ''; }, 4000);
  }
  function copiar(texto, ok) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(function () { avisar(ok); }, function () { window.prompt('Cópialo de aquí:', texto); });
    } else window.prompt('Cópialo de aquí:', texto);
  }

  $('ctCopiar').addEventListener('click', function () {
    var d = datosDoc(); if (!d) return;
    var t = '🇲🇽 MI ESTADO DE CUENTA CÍVICO 2026 (Auditavisión)\n';
    t += 'De mi sueldo de ' + pesos(d.bruto) + ' ' + d.cad + ', Hacienda me retiene ' + pesos(d.isr) + ' de ISR.\n';
    t += 'Así se reparte cada peso de mi esfuerzo en el Presupuesto Federal:\n';
    d.movimientos.forEach(function (x) { t += '• ' + x.icono + ' ' + x.nombre + ': ' + pesos(x.monto) + ' (' + x.pct.toFixed(1) + '%)\n'; });
    d.poderes.forEach(function (x) { t += '   de ahí, ' + x.nombre + ': ' + finos(x.monto) + '\n'; });
    if (d.ellos) t += '\n' + d.ellos.cargo + ': recibe ' + d.ellos.veces.toFixed(1) + ' veces mi ingreso neto (PEF 2026, Anexo 23).\n';
    t += '\nISR que pagué: ' + pesos(d.isr) + ' ' + d.cad + '. Montos por renglón derivados del PEF 2026.\n';
    if (est.folio) t += 'Folio ' + est.folio + '. Compruébalo: ' + ligaVerifica() + '\n';
    t += 'Fiscaliza el tuyo y audita a tu gobierno en: Auditavisión México';
    copiar(t, '✓ Copiado. Listo para pegar en X, WhatsApp o tus redes. Ojo: lleva tu ingreso.');
  });
  $('ctLiga').addEventListener('click', function () {
    if (!est.folio) return;
    copiar(ligaVerifica(), '✓ Liga copiada. Lleva tu ingreso escrito: compártela solo si quieres que se vea.');
  });
  $('ctImprimir').addEventListener('click', function () { window.print(); });

  function texto(g, t, x, y, fuente, color, al) { g.font = fuente; g.fillStyle = color; g.textAlign = al || 'left'; g.fillText(t, x, y); }
  function aleatorio(s) { s = s >>> 0; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  function horizonte(g, W, y0, alto, noche) {
    var rnd = aleatorio(20260926), cielo = g.createLinearGradient(0, 0, 0, y0 + alto);
    if (noche) { cielo.addColorStop(0, '#070b1a'); cielo.addColorStop(1, '#1d2650'); } else { cielo.addColorStop(0, '#9fd3f7'); cielo.addColorStop(1, '#fbe9c8'); }
    g.fillStyle = cielo; g.fillRect(0, 0, W, y0 + alto);
    var base = y0 + alto;
    [[0.55, noche ? '#141b3a' : '#9fb3c8'], [1, noche ? '#0b1026' : '#5d7390']].forEach(function (c, capa) {
      var x = -10;
      while (x < W) {
        var w = 40 + rnd() * 70, h = (40 + rnd() * 90) * c[0] + capa * 16;
        g.fillStyle = c[1]; g.fillRect(x, base - h, w, h);
        x += w + 4 + rnd() * 10;
      }
    });
  }
  function arco(g, t, rad, arriba, fuente) {
    g.font = fuente; g.textAlign = 'center'; g.textBaseline = 'middle';
    var l = Array.from(t), an = l.map(function (ch) { return g.measureText(ch).width; });
    var tot = an.reduce(function (a, b) { return a + b; }, 0) / rad, dir = arriba ? 1 : -1;
    var ang = (arriba ? -Math.PI / 2 : Math.PI / 2) - dir * tot / 2;
    l.forEach(function (ch, i) {
      var w = an[i] / rad; ang += dir * w / 2;
      g.save(); g.translate(rad * Math.cos(ang), rad * Math.sin(ang)); g.rotate(arriba ? ang + Math.PI / 2 : ang - Math.PI / 2); g.fillText(ch, 0, 0); g.restore();
      ang += dir * w / 2;
    });
  }
  function selloCanvas(g, cx, cy, r, color, fondo, fecha, folio, logo) {
    var s = r / 95, mono = "'JetBrains Mono', Consolas, monospace";
    g.save(); g.translate(cx, cy); g.rotate(-0.21); g.scale(s, s); g.globalAlpha = 0.93;
    if (fondo) { g.beginPath(); g.arc(0, 0, 95, 0, Math.PI * 2); g.fillStyle = fondo; g.fill(); }
    g.strokeStyle = color; g.fillStyle = color;
    g.lineWidth = 3.5; g.beginPath(); g.arc(0, 0, 95, 0, Math.PI * 2); g.stroke();
    g.lineWidth = 1; g.beginPath(); g.arc(0, 0, 88, 0, Math.PI * 2); g.stroke();
    g.setLineDash([2, 3]); g.beginPath(); g.arc(0, 0, 62, 0, Math.PI * 2); g.stroke(); g.setLineDash([]);
    arco(g, 'AUDITAVISIÓN', 76, true, '700 15px ' + mono);
    arco(g, 'SISTEMA CÍVICO DE FISCALIZACIÓN', 74, false, '700 10.5px ' + mono);
    g.textAlign = 'center'; g.textBaseline = 'alphabetic';
    g.font = '12px ' + mono; g.fillText('★', -79, 4); g.fillText('★', 79, 4);
    if (logo) g.drawImage(logo, -32, -56, 64, 50);
    g.font = '700 9px ' + mono; g.fillText('EMITIDO', 0, 10);
    g.font = '700 13px ' + mono; g.fillText(fecha, 0, 27);
    if (folio) { g.font = '600 8.5px ' + mono; g.fillText(folio, 0, 42); }
    g.restore();
  }
  function imagen(src) {
    return new Promise(function (ok) { var im = new Image(); im.onload = function () { ok(im); }; im.onerror = function () { ok(null); }; im.src = src; });
  }

  $('ctImagen').addEventListener('click', function () {
    var d = datosDoc(); if (!d) return;
    var noche = $('ctNoche').checked;
    var C = noche
      ? { fondo: '#0c1122', tarjeta: '#131a33', linea: '#27305a', txt: '#eef1fa', suave: '#9aa3c7', oro: '#f2c14e', cian: '#4fd1e8', barra: '#f2c14e' }
      : { fondo: '#f7f5ef', tarjeta: '#ffffff', linea: '#ddd6c6', txt: '#16203a', suave: '#5d6680', oro: '#a8740a', cian: '#0b7a8f', barra: '#c9921a' };
    var W = 1080, H = 1350, M = 64;
    var serif = "'Playfair Display', Georgia, serif", sans = "Inter, 'Segoe UI', Arial, sans-serif", mono = "'JetBrains Mono', Consolas, monospace";
    var listo = (document.fonts && document.fonts.ready) ? document.fonts.ready.catch(function () {}) : Promise.resolve();
    listo.then(function () {
      return Promise.all([imagen('assets/img/' + (noche ? 'city_night.jpg' : 'city_day.jpg')), imagen('assets/auditor/img/logo-auditavision.svg')]);
    }).then(function (ims) {
      var foto = ims[0], logo = ims[1];
      var cv = document.createElement('canvas'); cv.width = W; cv.height = H;
      var g = cv.getContext('2d');
      g.fillStyle = C.fondo; g.fillRect(0, 0, W, H);
      if (foto) {
        var hH = 330, e = Math.max(W / foto.width, hH / foto.height), sw = W / e, sh = hH / e;
        g.drawImage(foto, (foto.width - sw) / 2, (foto.height - sh) * 0.35, sw, sh, 0, 0, W, hH);
        g.fillStyle = noche ? 'rgba(6,9,20,0.45)' : 'rgba(255,255,255,0.30)'; g.fillRect(0, 0, W, hH);
      } else horizonte(g, W, 60, 250, noche);
      var velo = g.createLinearGradient(0, 150, 0, 330);
      velo.addColorStop(0, 'rgba(0,0,0,0)'); velo.addColorStop(1, C.fondo);
      g.fillStyle = velo; g.fillRect(0, 120, W, 212);

      texto(g, 'AUDITAVISIÓN · SISTEMA CÍVICO DE FISCALIZACIÓN', M, 70, '600 20px ' + mono, noche ? '#ffffff' : '#16203a');
      texto(g, 'Estado de Cuenta Cívico', M, 150, '700 64px ' + serif, noche ? '#ffffff' : '#16203a');
      selloCanvas(g, W - M - 96, 158, 92, noche ? '#ecc767' : '#8a6512', noche ? 'rgba(8,12,26,0.55)' : 'rgba(255,255,255,0.6)', d.emitido, est.folio, logo);

      [['PERIODO', d.periodo], ['FOLIO', est.folio || '—'], ['EMITIDO', d.emitido]].forEach(function (m, i) {
        var x = M + i * 330;
        texto(g, m[0], x, 298, '600 16px ' + mono, C.suave);
        texto(g, m[1], x, 326, '600 22px ' + sans, C.txt);
      });
      var kpis = [['INGRESO BRUTO', d.bruto, C.txt], ['ISR PAGADO', d.isr, C.oro], ['CUOTAS IMSS', d.cuotas, C.cian], ['TE QUEDA', d.neto, C.txt]];
      var kw = (W - 2 * M - 3 * 16) / 4;
      kpis.forEach(function (k, i) {
        var x = M + i * (kw + 16), y = 356;
        g.fillStyle = C.tarjeta; g.fillRect(x, y, kw, 112);
        g.fillStyle = k[2]; g.fillRect(x, y, kw, 4);
        texto(g, k[0], x + 18, y + 40, '600 15px ' + mono, C.suave);
        texto(g, pesos(k[1]), x + 18, y + 84, '700 30px ' + sans, k[2]);
      });
      texto(g, 'Montos ' + d.cad + ' · ' + d.regimen, M, 500, '400 18px ' + sans, C.suave);
      texto(g, 'A DÓNDE FUE TU ISR', M, 552, '700 20px ' + mono, C.oro);
      var movs = d.movimientos.slice(0, 8), max = Math.max.apply(null, movs.map(function (m) { return m.monto; })) || 1;
      movs.forEach(function (m, i) {
        var y = 596 + i * 46;
        texto(g, m.nombre.length > 34 ? m.nombre.slice(0, 33) + '…' : m.nombre, M, y, '500 21px ' + sans, C.txt);
        g.fillStyle = C.linea; g.fillRect(M + 420, y - 16, 330, 14);
        g.fillStyle = C.barra; g.fillRect(M + 420, y - 16, 330 * m.monto / max, 14);
        texto(g, m.pct.toFixed(1) + '%', M + 830, y, '500 19px ' + mono, C.suave, 'right');
        texto(g, pesos(m.monto), W - M, y, '700 21px ' + sans, C.txt, 'right');
      });
      var y = 596 + movs.length * 46 + 6;
      g.fillStyle = C.linea; g.fillRect(M, y, W - 2 * M, 2);
      y += 40;
      d.poderes.forEach(function (p) {
        texto(g, 'de ahí, ' + p.nombre, M, y, 'italic 400 20px ' + sans, C.suave);
        texto(g, finos(p.monto), W - M, y, '600 20px ' + sans, C.txt, 'right');
        y += 36;
      });
      if (d.ellos) {
        y += 14;
        g.fillStyle = C.tarjeta; g.fillRect(M, y, W - 2 * M, 118);
        g.fillStyle = C.oro; g.fillRect(M, y, 6, 118);
        texto(g, d.ellos.veces.toFixed(1) + '×', M + 36, y + 80, '700 62px ' + serif, C.oro);
        texto(g, d.ellos.cargo + ': ' + d.ellos.veces.toFixed(1) + ' veces tu ingreso', M + 230, y + 50, '600 24px ' + sans, C.txt);
        texto(g, 'Neto contra neto. Anexo 23, PEF 2026: ' + pesos(d.ellos.netoAnual) + ' al año', M + 230, y + 86, '400 19px ' + sans, C.suave);
      }
      if (est.huella) texto(g, 'Huella SHA-256: ' + est.huella, M, H - 120, '400 13px ' + mono, C.suave);
      texto(g, 'Fuentes: tarifas ISR, Anexo 8 RMF 2026 · PEF 2026. Montos por renglón: derivados.', M, H - 92, '400 16px ' + sans, C.suave);
      texto(g, 'Ejercicio de divulgación. No es un comprobante fiscal.', M, H - 64, '400 16px ' + sans, C.suave);
      texto(g, 'uzoraproductos-arch.github.io/a', W - M, H - 64, '700 18px ' + mono, C.oro, 'right');
      var a = document.createElement('a');
      a.download = 'estado-de-cuenta-civico-' + (est.folio || 'AV') + '.png';
      a.href = cv.toDataURL('image/png');
      document.body.appendChild(a); a.click(); a.remove();
      avisar('✓ Imagen descargada.');
    });
  });

  /* ---------------- vista rápida y orquestación ---------------- */
  function pintarVivo() {
    var res = est.res, viv = $('ctVivo');
    if (!res) { viv.hidden = true; return; }
    viv.hidden = false;
    var v = est.per === 'ano' ? res.ano : res.mes;
    contar($('ctVBruto'), v.bruto, pesos, 400);
    contar($('ctVIsr'), v.isr, pesos, 400);
    contar($('ctVImss'), v.cuotasTotal, pesos, 400);
    contar($('ctVNeto'), v.neto, pesos, 400);
    var b = v.bruto || 1;
    $('ctVbIsr').style.width = (v.isr / b * 100).toFixed(2) + '%';
    $('ctVbImss').style.width = (v.cuotasTotal / b * 100).toFixed(2) + '%';
    $('ctVbNeto').style.width = (Math.max(0, v.neto) / b * 100).toFixed(2) + '%';
  }

  function calcular(desplazar) {
    clearTimeout(tCalc);
    if (!(est.m > 0)) {
      ceros(false);
      $('ctEstado').textContent = 'Escribe una cantidad mayor que cero para sacar la cuenta. Puede usarse con o sin separador de miles.';
      return;
    }
    est.res = resultado();
    est.calculado = true;
    $('ctVacio2').hidden = true; $('ctRet').hidden = false;
    pintarControles(); pintarVivo(); pintarRetencion(); pintarReparto(); pintarDoc(); pintarFalta();
    guardar();
    /* En la pagina de tu ingreso, la cuenta 2 vive en otra pagina: se baja al
       boton que lleva a ella. */
    var dest = $('ctPaso2').hidden ? $('ctSigue') : $('ctPaso2');
    if (desplazar && dest) dest.scrollIntoView({ behavior: reducido ? 'auto' : 'smooth', block: 'start' });
  }

  function ceros(borrar) {
    est.calculado = false; est.res = null;
    $('ctVacio2').hidden = false; $('ctRet').hidden = true;
    pintarControles(); pintarVivo(); pintarReparto(); pintarDoc(); pintarFalta();
    if (borrar) guardar();
  }

  /* Cuentas 2 a 4 en su pagina: sin ingreso, el aviso para escribirlo; con
     ingreso, la cifra que usa la cuenta y la liga para cambiarla. */
  function pintarFalta() {
    var falta = $('ctFalta'), tuya = $('ctTuIng');
    if (!falta || !tuya) return;
    falta.hidden = est.calculado;
    tuya.hidden = !est.calculado;
    if (!est.calculado) return;
    var a = falta.querySelector('a');
    tuya.innerHTML = 'Esta cuenta usa tu ingreso de <b>' + pesos2(est.m) + (est.per === 'ano' ? ' al año' : ' al mes') + '</b>, ' +
      (est.nat === 'neto' ? 'después de descuentos' : 'antes de descuentos') + ', en <b>' + esc(regimen().nombre) + '</b>. ' +
      '<a href="' + a.getAttribute('href') + '">Cámbialo en 1 · Tu ingreso</a>';
  }

  /* ---------------- arranque ---------------- */
  var q = new URLSearchParams(location.search);
  if (q.get('verifica')) {
    est.verifica = q.get('verifica').trim();
    aplicar({ m: q.get('m'), per: q.get('p'), nat: q.get('n'), reg: q.get('r'), plat: q.get('pl'), ded: q.get('d') });
  } else if (q.get('m')) {
    /* El Auditor Virtual trae el ingreso que le dijeron (?m=&p=&n=, 24-10-2026). */
    aplicar({ m: q.get('m'), per: q.get('p'), nat: q.get('n') });
  } else {
    recuperar();
  }
  ivaR.value = est.iva;
  inDed.value = est.ded ? est.ded.toLocaleString('es-MX') : '0';
  escribirMonto();
  rango.value = montoARango(est.m);
  if (est.m > 0) calcular(false); else { ceros(false); comprobar(); }
  if (est.verifica) setTimeout(function () { $('ctPaso4').scrollIntoView({ block: 'start' }); }, 60);
})();
