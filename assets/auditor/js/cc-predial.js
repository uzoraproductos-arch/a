/* Auditavisión · Calculadora Cívica › Tu impuesto predial, según tu municipio (19-11-2026).
   La página la escribe herramientas/cc_predial.py con la ley de cada municipio en #cpDatos.
   Aquí solo se hacen las cuentas de su Ley de Ingresos 2026 y de la Ley de Hacienda
   Municipal de Jalisco (arts. 44 bis, 52 y 103). Nada se guarda ni se envía.
   AuditorPredial.bimestral() y .calcula() se exponen para las pruebas. */
(function () {
  'use strict';

  function r2(v) { return Math.round(v * 100) / 100; }

  /* ((VF − LI) × T) + CF, con el tramo donde cae el valor fiscal. */
  function bimestral(m, vf) {
    var t = m.tramos[0];
    for (var i = 0; i < m.tramos.length; i++) if (vf >= m.tramos[i][0]) t = m.tramos[i];
    /* Ciudad de México (Código Fiscal, art. 130, fr. I, último párrafo): si el valor es menor que la cuota fija del rango A, solo el porcentaje. */
    if (m.sin_cf_bajo && vf < m.sin_cf_bajo) return r2(Math.max(vf - m.tramos[0][0], 0) * m.tramos[0][2]);
    return r2((vf - t[0]) * t[2] + t[1]);
  }
  function tramo(m, vf) {
    var k = 0;
    for (var i = 0; i < m.tramos.length; i++) if (vf >= m.tramos[i][0]) k = i;
    return k;
  }
  /* tipo: 'edif' (construido), 'rust' (rústico: su propia tasa al millar si la ley la da) o 'baldio'. */
  /* El mínimo bimestral, si la ley lo pone (Tamazula: «en ningún caso… inferior a $50.00 pesos bimestrales»). */
  function base(m, vf, tipo) {
    var b = base0(m, vf, tipo);
    return m.minimo ? Math.max(b, m.minimo.pesos) : b;
  }
  function base0(m, vf, tipo) {
    if (m.anual) return r2(r2(vf * (m.anual[tipo] || m.anual.edif) / 1000) / 6);
    if (tipo === 'rust' && m.rustico) return m.rustico.tipo === 'sobretasa' ? r2(bimestral(m, vf) * (1 + m.rustico.pct / 100)) : r2(vf * m.rustico.millar / 1000 + m.rustico.cf);
    if (tipo !== 'baldio') return bimestral(m, vf);
    var b = m.baldio;
    if (b.tipo === 'igual') return bimestral(m, vf);
    if (b.tipo === 'sobretasa') return r2(bimestral(m, vf) * (1 + b.pct / 100));
    return r2(vf * b.millar / 1000 + b.cf);
  }
  /* El impuesto del año. Con 'anual' (Nuevo León: tasa al millar por año, Ley de Hacienda para los Municipios, art. 21 bis-8),
     sobre el valor y con el mínimo anual (art. 21 bis-12); en los demás, seis bimestres. Gemela de anual() de cc_predial.py. */
  function anual(m, vf, tipo) {
    if (m.anual) {
      var a = r2(vf * (m.anual[tipo] || m.anual.edif) / 1000);
      return m.minimo && m.minimo.anual ? Math.max(a, m.minimo.anual) : a;
    }
    return r2(base(m, vf, tipo) * 6);
  }
  /* El nombre de la ley que cobra: la Ley de Ingresos de cada municipio o, en Nuevo León, la Ley de Hacienda del estado. */
  function leyDe(m) { return m.ley_corta || 'Ley de Ingresos de ' + m.nombre; }
  /* Al revés: con el impuesto de un bimestre, el valor fiscal que lo daría (predio construido, tabla general).
     null si el impuesto cae en el mínimo o debajo de la primera cuota fija. */
  function inverso(m, imp) {
    if (m.minimo && imp <= m.minimo.pesos) return null;
    for (var i = m.tramos.length - 1; i >= 0; i--) {
      var t = m.tramos[i];
      if (imp >= t[1] && t[2] === 0) return null;
      if (imp >= t[1]) {
        var v = r2(t[0] + (imp - t[1]) / t[2]);
        /* Con una tabla con saltos (Saltillo), un impuesto puede caer en el hueco entre dos rangos: ningún valor lo da. */
        return v >= t[0] && (i + 1 === m.tramos.length || v < m.tramos[i + 1][0]) ? v : null;
      }
    }
    return null;
  }
  /* El valor fiscal, armado como el catastro: terreno × valor unitario de suelo + construcción × valor
     unitario de construcción × factor (demérito o conservación; 1 si tu tabla no lo da). t: {ts, vs, tc, vc, fc} */
  function valorFiscal(t) {
    var fc = t.fc > 0 ? t.fc : 1;
    return r2(t.ts * t.vs + t.tc * t.vc * fc);
  }
  /* El valor unitario oficial de la tabla de valores del municipio (T), y +% si el edificio pasa de los niveles que dice. */
  function valorConstruccion(T, uso, ical, iedad, iest, niveles) {
    var v = T.usos[uso].cal[ical][1][iedad][iest];
    if (v === null) return null;
    return niveles && T.niveles ? r2(v * (1 + T.niveles.pct / 100)) : v;
  }
  /* El valor de suelo por m² de una lista del decreto; si la lista va por hectárea, ÷ 10,000 m² (derivado). */
  function valorSuelo(T, il, ir) {
    var L = T.suelo.listas[il], v = L.filas[ir][1];
    if (v === null) return null;
    return L.un === 'ha' ? r2(v / 10000) : v;
  }
  /* En qué cuarto de los precios de avalúo SHF cae un valor: 0 (bajo el 25 %) a 3 (desde el 75 %). Gemela de cuartil() de cc_predial.py. */
  function cuartil(P, vf) { return (vf >= P.p25 ? 1 : 0) + (vf >= P.p50 ? 1 : 0) + (vf >= P.p75 ? 1 : 0); }
  function cf2(v) { return '$' + Number(v).toLocaleString('es-MX', { minimumFractionDigits: 2 }); }

  /* x: {vf, tipo, ben, pago} */
  function calcula(D, m, x) {
    var pasos = [], avisos = [], ley = function (a) { return leyDe(m) + ', ' + a; };
    var B = base(m, x.vf, x.tipo), A, artB;
    if (m.anual) {
      var t0 = m.anual[x.tipo] || m.anual.edif, a0 = r2(x.vf * t0 / 1000);
      var queEs = (m.et_anual && m.et_anual[x.tipo]) || { edif: 'Casa habitación', rust: 'Rústico (la ley no le da otra tasa)', com: 'Comercial, industrial o de servicios', baldio: 'Baldío' }[x.tipo] || 'Construido';
      artB = m.art_anual[x.tipo] || m.art_tarifa;
      pasos.push([queEs + ': ' + t0 + ' al millar al año sobre el valor catastral', a0, ley(artB), 'b']);
      A = anual(m, x.vf, x.tipo);
      if (A > a0) pasos.push(['La cuenta da menos del mínimo: la ley cobra ' + m.minimo.uma_anual + ' ' + (m.minimo.un || 'cuotas') + ' al año', A, ley(m.minimo.art), 'b']);
      B = r2(A / 6);
    } else if (x.tipo === 'rust' && m.rustico && m.rustico.tipo === 'sobretasa') {
      pasos.push(['Impuesto de un predio construido con ese valor', bimestral(m, x.vf), ley(m.art_tarifa)]);
      pasos.push(['Rústico: sobretasa de ' + m.rustico.pct + ' %' + (m.rustico.pct === 100 ? ' (el doble)' : ''), base0(m, x.vf, x.tipo), ley(m.rustico.art), 'b']);
    } else if (x.tipo === 'rust' && m.rustico) {
      pasos.push(['Rústico: ' + m.rustico.millar + ' al millar del valor + cuota fija de ' + cf2(m.rustico.cf), B, ley(m.rustico.art), 'b']);
    } else if (x.tipo === 'baldio' && m.baldio.tipo === 'igual') {
      pasos.push(['Baldío: la ley no le pone otra tasa; paga con la tabla general', B, ley(m.baldio.art), 'b']);
    } else if (x.tipo === 'baldio') {
      if (m.baldio.tipo === 'sobretasa') {
        pasos.push(['Impuesto de un predio construido con ese valor', bimestral(m, x.vf), ley(m.art_tarifa)]);
        pasos.push(['Baldío: sobretasa de ' + m.baldio.pct + ' %' + (m.baldio.pct === 100 ? ' (el doble)' : ''), B, ley(m.baldio.art)]);
      } else {
        pasos.push(['Baldío: ' + m.baldio.millar + ' al millar del valor + cuota fija de $' + m.baldio.cf.toFixed(2), B, ley(m.baldio.art), 'b']);
      }
    } else if (m.tarifa === 'millar') {
      pasos.push(['Construido: ' + m.millar + ' al millar del valor + cuota fija de ' + cf2(m.tramos[0][1]), B, ley(m.art_tarifa), 'b']);
    } else {
      var t = m.tramos[tramo(m, x.vf)];
      pasos.push(['Tu tramo: desde $' + t[0].toLocaleString('es-MX', { minimumFractionDigits: 2 }) + ', cuota fija $' + t[1].toLocaleString('es-MX', { minimumFractionDigits: 2 }) + ', tasa ' + t[2], null, ley(m.art_tarifa)]);
      pasos.push(['(Valor fiscal − límite inferior) × tasa', r2((x.vf - t[0]) * t[2]), ley(m.art_tarifa)]);
      pasos.push(['Impuesto de cada bimestre (más la cuota fija)', B, ley(m.art_tarifa), 'b']);
    }
    if (!m.anual && m.minimo && base0(m, x.vf, x.tipo) < m.minimo.pesos) {
      pasos.push(['La cuenta da menos del mínimo: la ley cobra ' + (m.minimo.anual ? cf2(m.minimo.anual) + ' al año (su sexta parte por bimestre)' : cf2(m.minimo.pesos) + ' por bimestre'), B, ley(m.minimo.art), 'b']);
    }
    if (!m.anual) {
      A = r2(B * 6);
      artB = x.tipo === 'rust' && m.rustico ? m.rustico.art : x.tipo === 'baldio' ? m.baldio.art : m.art_tarifa;
      pasos.push(['Impuesto del año (seis bimestres)', A, ley(artB), 'b']);
    }
    var res = { bim: B, anual: A, pasos: pasos, avisos: avisos };

    /* El descuento: factor sobre el impuesto, a veces solo «sobre el primer» tanto del valor. */
    var ben = null, ahorroB = 0;
    if (x.ben) ben = m.beneficios.filter(function (b) { return b.id === x.ben; })[0] || null;
    if (ben && ben.hasta && x.vf > ben.hasta) {
      avisos.push('El descuento «' + ben.et + '» solo vale si el valor fiscal no rebasa $' + ben.hasta.toLocaleString('es-MX') + ' (' + ley(ben.art) + '): con tu valor no aplica.');
      ben = null;
    }
    if (ben && ben.desde && x.vf <= ben.desde) {
      avisos.push('El descuento «' + ben.et + '» es para valores fiscales de más de ' + pesos(ben.desde) + ' (' + ley(ben.art) + '): con tu valor no aplica.');
      ben = null;
    }
    if (ben && ben.fija != null) {
      /* La tarifa única especial (Nuevo León, art. 21 bis-9: cuotas al año) o la cuota fija bimestral (Ciudad de México, arts. 281 y 282). */
      ahorroB = Math.max(0, r2(A - ben.fija));
      pasos.push([(ben.fija_bim ? 'Cuota fija: ' + pesos(ben.fija_bim) + ' por bimestre (' + pesos(ben.fija) + ' al año)' : 'Tarifa especial: ' + ben.fija_uma + ' cuotas al año (' + pesos(ben.fija) + ')'), -ahorroB, ley(ben.art)]);
    } else if (ben) {
      var sobre = ben.tope && x.vf > ben.tope ? r2(base(m, ben.tope, x.tipo) * 6) : A;
      ahorroB = r2(sobre * (1 - ben.f));
      /* Puebla (art. 91): la reducción tiene un límite en pesos. */
      var topado = ben.max_ahorro && ahorroB > ben.max_ahorro;
      if (topado) ahorroB = ben.max_ahorro;
      pasos.push(['Descuento: pagas ' + Math.round(ben.f * 100) + ' %' + (ben.tope && x.vf > ben.tope ? ' del impuesto que daría el primer $' + ben.tope.toLocaleString('es-MX') + ' de valor' : '') + (topado ? ', con el límite de ' + pesos(ben.max_ahorro) + ' de reducción' : ''), -ahorroB, ley(ben.art)]);
    }
    var A1 = r2(A - ahorroB);
    res.conBen = A1;

    /* El pago anticipado del año; si el descuento no se suma, se da el mayor. */
    var pr = null;
    if (x.pago && x.pago !== 'bim') pr = m.pronto.filter(function (p) { return p.id === x.pago; })[0] || null;
    var fin = A1;
    if (pr) {
      var conPr = r2(A1 * pr.f), soloPr = r2(A * pr.f);
      if (!ben || ben.suma) {
        fin = conPr;
        pasos.push(['Pago anticipado: pagas ' + Math.round(pr.f * 100) + ' %' + (ben ? ' de lo que queda' : ''), r2(fin - A1), ley(pr.art) + (ben ? '; se suma: ' + (m.suma_art || '') : '')]);
      } else if (soloPr < A1) {
        fin = soloPr;
        pasos.push(['Te conviene más el pago anticipado (' + Math.round(pr.f * 100) + ' %) que el descuento: no se suman', r2(fin - A1), ley(pr.art) + (m.suma_art ? ', ' + m.suma_art : '')]);
        avisos.push(m.suma_art ? 'Tu Ley de Ingresos da solo el mayor de los dos beneficios (' + m.suma_art + ').' : 'La ' + leyDe(m) + ' no dice si se suman; aquí te damos el mayor de los dos.');
      } else {
        avisos.push(m.suma_art ? 'El descuento no se suma al pago anticipado (' + m.suma_art + '): te dejamos el descuento, que es mayor.' : 'La ' + leyDe(m) + ' no dice si el descuento se suma al pago anticipado; aquí te damos el mayor de los dos.');
      }
    }
    var minA = m.minimo ? (m.minimo.anual || r2(m.minimo.pesos * 6)) : 0;
    if (m.minimo && fin < minA) {
      fin = minA;
      avisos.push('Con el descuento quedaría debajo del mínimo de ' + (m.minimo.anual ? cf2(minA) + ' al año' : cf2(m.minimo.pesos) + ' por bimestre') + ' (' + ley(m.minimo.art) + '): pagas el mínimo.');
    }
    res.fin = r2(fin);
    res.pr = pr;
    res.ben = ben;
    pasos.push([pr ? 'Pagas por el año, en una sola exhibición' : 'Pagas por el año (en seis bimestres de ' + pesos(r2(A1 / 6)) + ')', res.fin, ley(pr ? pr.art : artB), 'b']);
    if (pr && m.pronto_nota) avisos.push(m.pronto_nota);
    if (m.tramos_nota) avisos.push(m.tramos_nota);
    if (m.saltos_ley) avisos.push(m.saltos_ley);
    if (x.tipo === 'rust' && !m.rustico && !m.anual) avisos.push('La Ley de Ingresos de ' + m.nombre + ' cobra a los predios rústicos con la misma tabla que a los urbanos.');
    if (m.nota) avisos.push(m.nota);
    return res;
  }

  function inpc(D, a, mm) {
    var s = D.inpc[a];
    return s && s[mm - 1] != null ? s[mm - 1] : null;
  }
  function mesAnt(a, mm) { return mm === 1 ? [a - 1, 12] : [a, mm - 1]; }

  /* El adeudo, bimestre por bimestre: vence el día 15 del primer mes (LHM, art. 103); recargos por mes o
     fracción desde el día siguiente (art. 52); actualización con el INPC (art. 44 bis). y: {imp, da, db, ha, hb, f:[a,m,d], sit, multa} */
  function adeudo(D, m, y) {
    if (!m.recargo) return { error: m.acc_pend || 'Los recargos de este municipio aún no están integrados.' };
    if (m.recargo.anual) return adeudoAnual(D, m, y);
    if (m.recargo.cfm) return adeudoCfm(D, m, y);
    var filas = [], avisos = [], tot = { imp: 0, act: 0, rec: 0 };
    var tope = y.sit === 'esp' ? D.lhm.tope_esp : D.lhm.tope;
    var ult = D.inpc_ult, faltaInpc = false;
    for (var a = y.da; a <= y.ha; a++) {
      for (var b = (a === y.da ? y.db : 1); b <= (a === y.ha ? y.hb : 6); b++) {
        var vm = 2 * b - 1;
        var venc = [a, vm, 15];
        var n = (y.f[0] - a) * 12 + (y.f[1] - vm) + (y.f[2] > 15 ? 1 : 0);
        if (n <= 0) continue;
        var pa = mesAnt(y.f[0], y.f[1]), va = mesAnt(a, vm);
        var iA = inpc(D, pa[0], pa[1]), iB = inpc(D, va[0], va[1]);
        if (iA == null) { iA = inpc(D, ult[0], ult[1]); faltaInpc = true; }
        var F = iA && iB ? Math.max(1, Math.round(iA / iB * 10000) / 10000) : 1;
        var act = r2(y.imp * (F - 1));
        var rec = r2(Math.min(y.imp * m.recargo.pct / 100 * n, y.imp * tope / 100));
        tot.imp += y.imp; tot.act += act; tot.rec += rec;
        filas.push({ a: a, b: b, venc: venc, n: n, F: F });
      }
    }
    if (!filas.length) return { error: 'Con esa fecha de pago, ningún bimestre de ese periodo está vencido todavía (se paga en los primeros quince días del primer mes de cada bimestre).' };
    if (faltaInpc) avisos.push('El INPC del mes anterior al pago aún no está en la base: usamos el último publicado (' + ult[1] + '/' + ult[0] + '), como dice la Ley de Hacienda Municipal, art. 44 bis.');
    tot.imp = r2(tot.imp); tot.act = r2(tot.act); tot.rec = r2(tot.rec);
    var uma = D.uma, L = function (a) { return 'Ley de Ingresos de ' + m.nombre + ', ' + a; };
    var pasos = [];
    pasos.push(['Impuesto omitido: ' + filas.length + ' bimestre' + (filas.length > 1 ? 's' : '') + ' × ' + pesos(y.imp), tot.imp, 'Ley de Hacienda Municipal, art. 103']);
    pasos.push(['Actualización con el INPC (el bimestre más viejo, factor ' + filas[0].F.toFixed(4) + ')', tot.act, 'Ley de Hacienda Municipal, art. 44 bis']);
    pasos.push(['Recargos: ' + m.recargo.pct + ' % por mes o fracción (el más viejo, ' + filas[0].n + ' meses; tope ' + tope + ' %)', tot.rec, L(m.recargo.art) + '; LHM, art. 52']);
    var multa = 0, notif = 0, ejec = 0, credito = tot.imp + tot.act + tot.rec;
    if (y.sit !== 'esp') {
      if (m.multa && y.multa > 0) {
        multa = r2(tot.imp * y.multa / 100);
        pasos.push(['Multa: ' + y.multa + ' % del impuesto omitido' + (m.multa.min === m.multa.max ? '' : ' (la ley da de ' + m.multa.min + ' % a ' + m.multa.max + ' %)'), multa, L(m.multa.art)]);
      } else if (!m.multa) {
        avisos.push('La Ley de Ingresos de ' + m.nombre + ' no fija el porcentaje de la multa en sus accesorios; si te impusieron una, súmala aparte.');
      }
      credito += multa;
      var nt = m.notif, dil = y.sit === 'req' ? 1 : y.sit === 'emb' ? 2 : 0;
      /* nt.req: la ley solo cobra la notificación del requerimiento (no una notificación previa). */
      if (nt.req && !dil) nt = null;
      if (nt) {
        var tope2 = nt.max_pesos || (nt.max_uma ? nt.max_uma * uma : Infinity);
        notif = nt.pesos ? nt.pesos : nt.pct ? r2(Math.min(Math.max(credito * nt.pct / 100, (nt.min_uma || 0) * uma, nt.min_pesos || 0), tope2)) : r2(nt.uma * uma);
        pasos.push([(nt.req ? 'Notificación del requerimiento' : 'Notificación del adeudo') + (nt.pesos ? ' (cuota de la ley)' : nt.pct ? ' (' + nt.pct + ' % del crédito)' : ' (' + nt.uma + ' UMA diarias)'), notif, L(nt.art)]);
        if (nt.pesos_nota) avisos.push(nt.pesos_nota);
        if (nt.nota) avisos.push(nt.nota);
      }
      var e = m.ejec;
      /* e.emb: la ley cobra estos gastos solo por la diligencia de embargo, una vez. */
      if (e.emb) dil = y.sit === 'emb' ? 1 : 0;
      if (dil) {
        var una = e.pesos ? e.pesos : credito * e.pct / 100;
        if (e.min_uma) una = Math.max(una, e.min_uma * uma);
        if (e.max_uma) una = Math.min(una, e.max_uma * uma);
        if (e.min_pesos) una = Math.max(una, e.min_pesos);
        if (e.max_pesos) una = Math.min(una, e.max_pesos);
        ejec = r2(una * dil);
        pasos.push([e.emb ? 'Gastos de embargo: ' + (e.pesos ? 'cuota de la ley' : e.pct + ' % del crédito') : 'Gastos de ejecución: ' + e.pct + ' % del crédito por diligencia × ' + dil + (dil > 1 ? ' (requerimiento y embargo)' : ' (requerimiento)'), ejec, L(e.art)]);
      }
    } else {
      avisos.push('Pagando por tu cuenta, antes de que te requieran, no hay multa ni gastos de cobranza, y los recargos no pasan de 100 % (Ley de Hacienda Municipal, art. 52).');
    }
    var total = r2(tot.imp + tot.act + tot.rec + multa + notif + ejec);
    pasos.push(['Total a pagar (aproximado)', total, 'Suma', 'b']);
    if (y.da < D.anio) avisos.push('Para los años antes de ' + D.anio + ' usamos la tasa de recargos de ' + D.anio + ' y el impuesto que escribiste; cada año tuvo los suyos en su ley, así que el adeudo oficial puede ser distinto.');
    return { pasos: pasos, avisos: avisos, total: total, n: filas.length, multa: multa, notif: notif, ejec: ejec };
  }

  /* El adeudo de un municipio que cobra el predial por año (Tijuana): el año vence el día que dice su ley
     (m.recargo.venc = [mes, día]) y es exigible desde el día siguiente; recargos por cada mes o fracción desde ahí
     hasta el pago, sobre el impuesto sin accesorios, con el tope de meses de su ley (m.recargo.max_meses). Sin
     actualización (m.recargo.sin_act lo explica) y sin multa ni gastos de cobranza (m.recargo.pend lo explica).
     y.imp es el impuesto de cada año; y.da y y.ha, los años. */
  function adeudoAnual(D, m, y) {
    var R = m.recargo, filas = [], tot = { imp: 0, rec: 0 }, avisos = [];
    for (var a = y.da; a <= y.ha; a++) {
      /* exigible el día siguiente al vencimiento: el primer mes (o fracción) empieza ese día */
      var ex = new Date(Date.UTC(a, R.venc[0] - 1, R.venc[1] + 1)), ea = ex.getUTCFullYear(), em = ex.getUTCMonth() + 1, ed = ex.getUTCDate();
      var k = (y.f[0] - ea) * 12 + (y.f[1] - em) - (y.f[2] < ed ? 1 : 0);
      if (y.f[0] * 10000 + y.f[1] * 100 + y.f[2] < ea * 10000 + em * 100 + ed) continue;
      var n = k + 1, nc = R.max_meses ? Math.min(n, R.max_meses) : n;
      var rec = r2(y.imp * R.pct / 100 * nc);
      tot.imp += y.imp; tot.rec += rec;
      filas.push({ a: a, n: n, nc: nc });
    }
    if (!filas.length) return { error: 'Con esa fecha de pago, ningún año de ese periodo está vencido todavía (' + m.nombre + ' cobra el predial por año: ' + (m.venc || '') + ').' };
    tot.imp = r2(tot.imp); tot.rec = r2(tot.rec);
    var pasos = [], v = filas[0];
    pasos.push(['Impuesto omitido: ' + filas.length + ' año' + (filas.length > 1 ? 's' : '') + ' × ' + pesos(y.imp), tot.imp, 'Ley de Ingresos de ' + m.nombre + ', ' + R.art_venc]);
    pasos.push(['Recargos: ' + R.pct + ' % por mes o fracción desde el día siguiente al vencimiento (el más viejo, ' + v.n + ' mes' + (v.n > 1 ? 'es' : '') +
      (v.nc < v.n ? '; se cuentan ' + v.nc + ', el tope de su ley' : '') + ')', tot.rec, 'Ley de Ingresos de ' + m.nombre + ', ' + R.art + '; ' + R.ley_rec]);
    var total = r2(tot.imp + tot.rec);
    pasos.push(['Total a pagar (aproximado)', total, 'Suma', 'b']);
    if (R.sin_act) avisos.push(R.sin_act);
    if (y.sit !== 'esp' && R.pend) avisos.push(R.pend);
    if (R.nota) avisos.push(R.nota);
    if (y.da < D.anio) avisos.push('Para los años antes de ' + D.anio + ' usamos la tasa de recargos de ' + D.anio + ' y el impuesto que escribiste; cada año tuvo los suyos en su ley, así que el adeudo oficial puede ser distinto.');
    return { pasos: pasos, avisos: avisos, total: total, n: filas.length, per: 'año', multa: 0, notif: 0, ejec: 0 };
  }

  /* El adeudo de Cuernavaca (Ronda 11; m.recargo.cfm), con el Código Fiscal para el Estado de Morelos. Gemela de
     adeudo_cfm() de cc_predial.py. Cada bimestre vence al terminar su primer mes y es exigible el día 1 del siguiente;
     recargos por mes o fracción desde ahí (art. 47; tope m.recargo.max_meses) sobre el impuesto actualizado; factor del
     INPC (art. 46: mes anterior al pago ÷ mes anterior al vencimiento) truncado al diezmilésimo y nunca menor que 1.
     La multa y los gastos de ejecución no se suman: m.recargo.pend los explica. */
  function adeudoCfm(D, m, y) {
    var R = m.recargo, filas = [], avisos = [], tot = { imp: 0, act: 0, rec: 0 };
    var ult = D.inpc_ult, faltaInpc = false;
    for (var a = y.da; a <= y.ha; a++) {
      for (var b = (a === y.da ? y.db : 1); b <= (a === y.ha ? y.hb : 6); b++) {
        var vm = 2 * b - 1;
        var n = (y.f[0] - a) * 12 + (y.f[1] - (vm + 1)) + 1;
        if (n <= 0) continue;
        var nc = Math.min(n, R.max_meses);
        var pa = mesAnt(y.f[0], y.f[1]), va = mesAnt(a, vm);
        var iA = inpc(D, pa[0], pa[1]), iB = inpc(D, va[0], va[1]);
        if (iA == null) { iA = inpc(D, ult[0], ult[1]); faltaInpc = true; }
        var F = iA && iB ? Math.max(1, Math.floor(iA / iB * 10000) / 10000) : 1;
        var act = r2(y.imp * (F - 1));
        tot.imp += y.imp; tot.act += act; tot.rec += r2((y.imp + act) * R.pct / 100 * nc);
        filas.push({ a: a, b: b, n: n, nc: nc, F: F });
      }
    }
    if (!filas.length) return { error: 'Con esa fecha de pago, ningún bimestre de ese periodo está vencido todavía (' + m.nombre + ' se paga ' + (m.venc || '') + ').' };
    if (faltaInpc) avisos.push('El INPC del mes anterior al pago aún no está en la base: usamos el último publicado (' + ult[1] + '/' + ult[0] + '), como dice el ' + R.ley_rec.split(',')[0] + ', art. 46.');
    tot.imp = r2(tot.imp); tot.act = r2(tot.act); tot.rec = r2(tot.rec);
    var v = filas[0], pasos = [];
    pasos.push(['Impuesto omitido: ' + filas.length + ' bimestre' + (filas.length > 1 ? 's' : '') + ' × ' + pesos(y.imp), tot.imp, 'Ley de Ingresos de ' + m.nombre + ', art. 6']);
    pasos.push(['Actualización con el INPC (el bimestre más viejo, factor ' + v.F.toFixed(4) + ')', tot.act, R.ley_rec.split(',')[0] + ', art. 46']);
    pasos.push(['Recargos: ' + R.pct + ' % por mes o fracción sobre el impuesto actualizado (el más viejo, ' + v.n + ' mes' + (v.n > 1 ? 'es' : '') +
      (v.nc < v.n ? '; se cuentan ' + v.nc + ', cinco años' : '') + ')', tot.rec, 'Ley de Ingresos de ' + m.nombre + ', ' + R.art + '; ' + R.ley_rec.split(',')[0] + ', art. 47']);
    var total = r2(tot.imp + tot.act + tot.rec);
    pasos.push(['Total a pagar (aproximado)', total, 'Suma', 'b']);
    if (R.nota) avisos.push(R.nota);
    if (y.sit !== 'esp' && R.pend) avisos.push(R.pend);
    if (R.anio_tasa) avisos.push(R.anio_tasa);
    if (y.da < D.anio) avisos.push('Para los años antes de ' + D.anio + ' usamos la tasa de recargos de ' + D.anio + ' y el impuesto que escribiste; cada año tuvo los suyos en su ley, así que el adeudo oficial puede ser distinto.');
    return { pasos: pasos, avisos: avisos, total: total, n: filas.length, multa: 0, notif: 0, ejec: 0 };
  }

  /* Tu recibo contra la ley: c = {cobro, per: 'bim'|'anual'}; r = lo que dio calcula(). Nunca califica: si no cuadra,
     da las causas más comunes para preguntar en la tesorería. */
  function contrasta(m, x, r, c) {
    var ley = c.per === 'anual' ? r.fin : r2(r.conBen / 6);
    var sinDesc = c.per === 'anual' ? r.anual : r.bim;
    var dif = r2(c.cobro - ley), pct = ley > 0 ? Math.round(dif / ley * 1000) / 10 : 0;
    var o = { ley: ley, sinDesc: sinDesc, dif: dif, pct: pct, causas: [] };
    o.cuadra = Math.abs(dif) <= Math.max(1, ley * 0.01);
    if (!o.cuadra && Math.abs(c.cobro - sinDesc) <= Math.max(1, sinDesc * 0.01)) o.sinBen = true;
    var bimRecibo = c.per === 'anual' ? c.cobro / 6 : c.cobro;
    if (x.tipo === 'edif' && !o.cuadra) o.vfImplicito = inverso(m, bimRecibo);
    if (!o.cuadra) {
      if (dif > 0) {
        o.causas = ['Tu recibo puede sumar otros conceptos (agua, aseo, alumbrado, derechos o fondos especiales): compara solo el renglón del impuesto predial.',
          'Puede traer adeudos de años o bimestres anteriores, con sus recargos y su actualización.',
          'El catastro pudo cambiar tu valor fiscal (un revalúo, una construcción nueva o las tablas de valores del año).',
          'Tu predio puede estar registrado con otra clase (baldío o rústico) o con otra tasa.',
          'El descuento que escogiste aquí quizá no está aplicado en tu cuenta (casi todos se piden por escrito y con documentos).'];
      } else {
        o.causas = ['Te pudieron aplicar un descuento, un pago anticipado o un programa del municipio que el simulador no conoce.',
          'Tu valor fiscal registrado puede ser menor al que escribiste.',
          'Algunas leyes ponen un tope al aumento del predial frente al año anterior (lo dice la nota de tu municipio, si es el caso).'];
      }
    }
    return o;
  }

  function pesos(v) {
    return (v < 0 ? '−' : '') + '$' + Math.abs(Number(v)).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  window.AuditorPredial = { bimestral: bimestral, base: base, anual: anual, calcula: calcula, adeudo: adeudo, inverso: inverso, valorFiscal: valorFiscal, valorConstruccion: valorConstruccion, valorSuelo: valorSuelo, contrasta: contrasta, cuartil: cuartil };

  var raiz = document.getElementById('cpRaiz');
  if (!raiz) return;
  var D = JSON.parse(document.getElementById('cpDatos').textContent);
  /* Rendimiento en celular (22-11-2026): la página trae solo el núcleo. La ley, las tablas, los decretos y las leyes en
     espera de cada entidad (D.porEnt) y el INPC (D.inpcSrc) viven en su archivo, versionado por su huella, y se piden al
     usarlos; al llegar se juntan en el mismo D, así que las cuentas no cambian. */
  D.mun = D.mun || []; D.tablas = D.tablas || {}; D.espera = D.espera || {}; D.dtv = D.dtv || {};
  var pide = {};
  function trae(url) {
    if (!pide[url]) pide[url] = fetch(url).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
    return pide[url];
  }
  var yaEnt = {};
  function entDatos(ent) {
    if (yaEnt[ent] || !D.porEnt || !D.porEnt[ent]) return Promise.resolve();
    return trae(D.porEnt[ent]).then(function (x) {
      if (yaEnt[ent]) return;
      yaEnt[ent] = true;
      D.mun = D.mun.concat(x.mun);
      Object.keys(x.tablas).forEach(function (k) { D.tablas[k] = x.tablas[k]; });
      Object.keys(x.espera).forEach(function (k) { D.espera[k] = x.espera[k]; });
      if (x.dtv) D.dtv[ent] = x.dtv;
    }, function () { avisaFalla(); });
  }
  function inpcListo() {
    if (D.inpc || !D.inpcSrc) return Promise.resolve();
    return trae(D.inpcSrc).then(function (x) { D.inpc = x; }, function () { avisaFalla(); });
  }
  function avisaFalla() {
    var f = document.getElementById('cpMunFicha');
    if (f) f.innerHTML = '<p class="ci-error">No se pudieron cargar las leyes de este estado. Revisa tu conexión y vuelve a abrir la página.</p>';
  }
  var $ = function (id) { return document.getElementById(id); };
  var MUN = window.AUDIT_MUNICIPIOS || null;
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function num(id) {
    var s = ($(id).value || '').replace(/[$,\s]/g, '');
    if (s === '') return null;
    var v = Number(s);
    return isFinite(v) && v >= 0 ? v : NaN;
  }
  function ley(ent, cve) { return D.mun.filter(function (m) { return m.ent === ent && m.cve === cve; })[0] || null; }
  function mdp(v) { if (v < 1e7) return pesos(v).replace(/\.\d\d$/, ''); return '$' + (v / 1e6).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' millones'; }

  function llenaMunicipios() {
    var ent = $('cpEnt').value, sel = $('cpMun'), ops = [];
    var e = MUN && MUN.ent[ent];
    if (e) e.lista.forEach(function (r) { ops.push([r[0], r[1]]); });
    else D.mun.filter(function (m) { return m.ent === ent; }).forEach(function (m) { ops.push([m.cve, m.nombre]); });
    ops.sort(function (a, b) {
      var la = ley(ent, a[0]) ? 0 : 1, lb = ley(ent, b[0]) ? 0 : 1;
      return la - lb || a[1].localeCompare(b[1], 'es');
    });
    sel.innerHTML = ops.map(function (o) { return '<option value="' + esc(o[0]) + '">' + esc(o[1]) + (ley(ent, o[0]) ? ' ✓' : '') + '</option>'; }).join('');
  }

  /* Un municipio que cobra por año (m.recargo.anual) pide el impuesto de cada año y años, no bimestres. */
  function rotulaDeuda(m) {
    var porAnio = !!(m && m.recargo && m.recargo.anual), et = document.querySelector('label[for="cpImp"]');
    if (et) et.textContent = porAnio ? 'Impuesto de cada año que debes (pesos)' : 'Impuesto de cada bimestre que debes (pesos)';
    ['cpDb', 'cpHb'].forEach(function (id) { var c = $(id); if (c && c.parentNode) c.parentNode.hidden = porAnio; });
    if ($('cpDebeTit')) $('cpDebeTit').textContent = porAnio ? '¿Debes años?' : '¿Debes bimestres?';
  }
  function ficha() {
    var ent = $('cpEnt').value, cve = $('cpMun').value, m = ley(ent, cve), h = '';
    rotulaDeuda(m);
    var e = MUN && MUN.ent[ent], r = e ? e.lista.filter(function (x) { return x[0] === cve; })[0] : null;
    /* Homónimos (Ronda 6): el municipio siempre con su entidad, «Puebla, Puebla» o «Benito Juárez, Ciudad de México». */
    var nom = (r ? r[1] : (m ? m.nombre : '')) + (D.ent[ent] ? ', ' + D.ent[ent] : '');
    if (r && r.length > 7) {
      var c = {}; MUN.campos.forEach(function (k, i) { c[k] = r[i]; });
      h += '<p><b>' + esc(nom) + '</b> recaudó <b>' + mdp(c.predial) + '</b> de predial en ' + MUN.anio + ': ' +
        (c.propios ? Math.round(c.predial / c.propios * 100) + ' de cada $100 de sus ingresos propios y ' : '') +
        Math.round(c.predial / c.ing * 100) + ' de cada $100 de todo lo que le entró <span class="est-chip est-oficial">oficial</span> <span class="cp-fuente">(INEGI, EFIPEM ' + MUN.anio + '; las proporciones, auditadas)</span>.</p>';
    } else if (r && m && m.alcaldia) {
      h += '<p><b>' + esc(nom) + '</b> es alcaldía: no rinde cuenta municipal al INEGI, porque el predial de la Ciudad de México lo recauda la Tesorería de la Ciudad, no cada alcaldía.</p>';
    } else if (r) {
      h += '<p><b>' + esc(nom) + '</b> no rindió cuenta al INEGI en ' + (MUN ? MUN.anio : '') + ': no sabemos cuánto recaudó de predial.</p>';
    }
    if (m) {
      h += '<p class="cp-ok">✓ Su tabla está integrada: <a href="' + esc(m.url) + '">' + esc(m.ley) + '</a>. ' +
        (m.recargo ? 'Recargos: ' + m.recargo.pct + ' % al mes (' + esc(m.recargo.art) + ').' + (m.recargo.pend ? '</p><p class="cp-falta"><span class="est-chip est-pendiente">pendiente</span> ' + esc(m.recargo.pend) : '') : '</p><p class="cp-falta"><span class="est-chip est-pendiente">pendiente</span> Recargos y gastos de cobranza: ' + esc(m.acc_pend)) + '</p>';
    } else if (D.espera && D.espera[ent + '-' + cve]) {
      var w = D.espera[ent + '-' + cve];
      h += '<p class="cp-falta"><span class="est-chip est-pendiente">pendiente</span> Leímos su <a href="' + esc(w.url) + '">ley de ' + D.anio + '</a>, pero no la integramos: ' + esc(w.motivo) + ' No adivinamos una tasa. Mientras, prueba con un municipio marcado con ✓.</p>';
    } else if (D.reg && D.reg[ent] && D.reg[ent].sin_ley && D.reg[ent].sin_ley[ent + '-' + cve]) {
      var s0 = D.reg[ent].sin_ley[ent + '-' + cve];
      h += '<p class="cp-falta"><span class="est-chip est-oficial">oficial</span> <b>' + esc(s0.nombre) + ' no tiene Ley de Ingresos ' + D.anio + ' aprobada.</b> ' + esc(s0.motivo) +
        ' Fuente: <a href="' + esc(s0.doc.url) + '">' + esc(s0.doc.tx) + '</a>. Sin ley aprobada no hay tarifa del Congreso que el simulador pueda usar; con qué cobra lo debe aclarar su tesorería.</p>';
    } else if (D.reg && D.reg[ent]) {
      h += '<p class="cp-falta"><span class="est-chip est-pendiente">pendiente</span> Aún no integramos la tabla del predial de su Ley de Ingresos ' + D.anio +
        ': es falta de esta plataforma, no del municipio. ' + esc(D.reg[ent].como) + ' Se publican en: <a href="' + esc(D.reg[ent].url) + '">' + esc(D.reg[ent].donde) + '</a>. Mientras, prueba con un municipio marcado con ✓.</p>';
    } else {
      h += '<p class="cp-falta"><span class="est-chip est-pendiente">pendiente</span> Aún no integramos la tabla del predial de su Ley de Ingresos ' + D.anio +
        ': es falta de esta plataforma, no del municipio. La ley la publica el congreso de su estado' +
        (ent === 'JAL' ? ' en su <a href="https://congresoweb.congresojal.gob.mx/BibliotecaVirtual/busquedasleyes/Listado%272.cfm">Biblioteca Virtual</a>' : '') +
        '. Mientras, prueba con un municipio marcado con ✓.</p>';
    }
    var dv = D.dtv && D.dtv[ent];
    if (dv) {
      var d0 = dv.lista[cve];
      if (d0) {
        h += '<p><span class="est-chip est-oficial">oficial</span> Sus tablas de valores ' + dv.anio + ' (con las que el catastro fija tu valor fiscal): <a href="' + esc(D.poe + d0[2]) + '">Decreto ' + esc(d0[0]) +
          ' del Congreso, Periódico Oficial del ' + d0[1].split('-').reverse().join('-') + '</a>' + (m && D.tablas && D.tablas[m.id] ? '; sus valores de construcción ya están abajo, en «¿No sabes tu valor fiscal?».' : '.') + '</p>';
      } else {
        h += '<p class="cp-falta"><span class="est-chip est-pendiente">pendiente</span> No encontramos en el Periódico Oficial un decreto de tablas de valores ' + dv.anio + ' para ' + esc(nom) +
          ' (lo buscamos ejemplar por ejemplar, de ' + esc(dv.buscado) + '). Con qué valores se calcula tu predial lo debe aclarar su catastro municipal.</p>';
      }
    }
    /* Ronda 25: el Semáforo Patrimonial del municipio elegido. Va por el Auditor (§0 quinquies: entre pestañas, todo pasa por el chat),
       con la pregunta ya puesta: su predial, el precio de la vivienda, el fraude y la deuda, en tres bloques. */
    if (r && D.ent[ent]) h += '<p class="cp-patri"><a href="herramienta-inspector-pregunta.html?q=' + encodeURIComponent('Semáforo patrimonial: ' + (ent === 'CDMX' ? 'Alcaldía ' : 'Municipio de ') + r[1] + ', ' + D.ent[ent]) +
      '">Ver el Semáforo Patrimonial completo de este municipio</a> <small>(¿vas a comprar ahí? Su predial, el precio de la vivienda, el fraude y la deuda, con sus documentos)</small></p>';
    $('cpMunFicha').innerHTML = h;
    $('cpPredio').disabled = !m;
    /* «Comercial» solo donde la ley le da su propia tasa (Nuevo León, art. 21 bis-8, tercer párrafo). */
    var oc = $('cpTipo').querySelector('option[value="com"]'), conCom = !!(m && m.anual && m.anual.com);
    if (oc) { oc.hidden = !conCom; oc.disabled = !conCom; oc.textContent = (m && m.com_et) || 'Comercial, industrial o de servicios (donde la ley le da su tasa)'; if (!conCom && $('cpTipo').value === 'com') $('cpTipo').value = 'edif'; }
    if (m) {
      $('cpBen').innerHTML = '<option value="">Ninguno</option>' + m.beneficios.map(function (b) {
        if (b.fija != null) return '<option value="' + esc(b.id) + '">' + esc(b.et) + ' — pagas ' + (b.fija_bim ? pesos(b.fija_bim) + ' por bimestre' : pesos(b.fija) + ' al año (' + b.fija_uma + ' cuotas)') + (b.hasta ? ' (valor hasta ' + pesos(b.hasta) + ')' : '') + '</option>';
        return '<option value="' + esc(b.id) + '">' + esc(b.et) + ' — pagas ' + Math.round(b.f * 100) + ' %' + (b.tope ? ' sobre el primer $' + b.tope.toLocaleString('es-MX') : '') + (b.max_ahorro ? ' (reducción hasta ' + pesos(b.max_ahorro) + ')' : '') + (b.hasta ? ' (valor hasta $' + b.hasta.toLocaleString('es-MX') + ')' : '') + '</option>';
      }).join('');
      $('cpPago').innerHTML = '<option value="bim">Cada bimestre</option>' + m.pronto.map(function (p) {
        return '<option value="' + esc(p.id) + '">' + esc(p.et) + ' — pagas ' + Math.round(p.f * 100) + ' %</option>';
      }).join('');
      var ops = m.multa ? [] : ['<option value="0">La ley no fija el porcentaje</option>'];
      if (m.multa) {
        /* El mínimo, los múltiplos de 5 de en medio y el máximo (hay leyes con 3.18 % a 10.60 %). */
        var vs = [m.multa.min];
        for (var p = Math.ceil(m.multa.min / 5) * 5; p < m.multa.max; p += 5) if (p > m.multa.min) vs.push(p);
        if (m.multa.max !== m.multa.min) vs.push(m.multa.max);
        vs.forEach(function (v) { ops.push('<option value="' + v + '"' + (v === m.multa.max ? ' selected' : '') + '>' + v + ' %</option>'); });
      }
      $('cpMulta').innerHTML = ops.join('');
    }
    tabla(m);
    compara();
    return m;
  }

  /* Si el municipio tiene su tabla de valores integrada, el valor de construcción sale de ahí. */
  function tabla(m) {
    var T = m && D.tablas ? D.tablas[m.id] : null, caja = $('cpTabla');
    caja.hidden = !T;
    suelo(T);
    if (!T) return;
    $('cpTablaTit').innerHTML = '<b>' + esc(m.nombre) + ' ya tiene su tabla de valores de construcción integrada</b> <span class="est-chip est-oficial">oficial</span>: elige tu construcción y el valor por m² se pone solo. ' +
      'Fuente: <a href="' + esc(T.url) + '">' + esc(T.tx) + '</a>. ' +
      (T.escaneo ? 'El decreto se publicó escaneado: transcribimos cada celda de la copia del Periódico Oficial, y la que no se lee sin duda va como ilegible, nunca adivinada. ' : '') +
      (T.suelo ? esc(T.suelo.nota) + ' <a href="' + esc(T.suelo.url) + '">' + esc(T.suelo.tx) + '</a>. ' : '') + (T.demeritos ? esc(T.demeritos.nota) : '') + (T.atipica ? ' ' + esc(T.atipica.nota) : '') + (T.falta ? ' ' + esc(T.falta) : '');
    $('cpTUso').innerHTML = Object.keys(T.usos).map(function (k) { return '<option value="' + k + '">' + esc(T.usos[k].et) + '</option>'; }).join('');
    $('cpTEdad').innerHTML = T.edades.map(function (e, i) { return '<option value="' + i + '">' + esc(e[1]) + '</option>'; }).join('');
    $('cpTEst').innerHTML = T.estados.map(function (e, i) { return '<option value="' + i + '">' + esc(e) + '</option>'; }).join('');
    $('cpTNivL').hidden = !T.niveles;
    if (!T.niveles) $('cpTNiv').checked = false;
    calidades(T);
    pintaTabla();
  }
  /* Las tablas de suelo del decreto (rango único, rústicos): elige tu renglón y el valor por m² se pone solo. */
  function suelo(T) {
    var Ls = T && T.suelo && T.suelo.listas, caja = $('cpSuelo');
    caja.hidden = !Ls;
    if (!Ls) return;
    $('cpSueloTit').innerHTML = '<b>Sus tablas de suelo</b> <span class="est-chip est-oficial">oficial</span>: ' + Ls.map(function (L) { return esc(L.et) + ' (' + esc(L.pag) + ')'; }).join('; ') +
      '. Fuente: <a href="' + esc(T.suelo.url) + '">' + esc(T.tx.split(',')[0]) + '</a>. Si tu terreno está en una calle de la ciudad, su valor viene en los planos: escríbelo a mano.';
    $('cpSueloSel').innerHTML = '<option value="">Mi terreno no está en estas tablas</option>' + Ls.map(function (L, il) {
      return '<optgroup label="' + esc(L.et) + '">' + L.filas.map(function (f, ir) {
        return '<option value="' + il + '.' + ir + '">' + esc(f[0]) + (f[1] === null ? ' — ilegible' : ' — ' + pesos(f[1]) + (L.un === 'ha' ? ' por hectárea' : ' por m²')) + '</option>';
      }).join('') + '</optgroup>';
    }).join('');
    $('cpSueloVal').innerHTML = '';
  }
  function pintaSuelo() {
    var m = ley($('cpEnt').value, $('cpMun').value), T = m && D.tablas ? D.tablas[m.id] : null, k = $('cpSueloSel').value;
    if (!T || !k) { $('cpSueloVal').innerHTML = ''; return; }
    var il = +k.split('.')[0], ir = +k.split('.')[1], L = T.suelo.listas[il], v = valorSuelo(T, il, ir);
    if (v === null) {
      $('cpSueloVal').innerHTML = '<span class="est-chip est-pendiente">pendiente</span> Este renglón no se lee sin duda en la copia escaneada que publicó el Periódico Oficial; no lo adivinamos. Búscalo en el decreto y escribe tu valor arriba.';
      return;
    }
    $('cpVs').value = String(v);
    $('cpSueloVal').innerHTML = (L.un === 'ha'
      ? 'Valor de suelo: <b>' + pesos(L.filas[ir][1]) + ' por hectárea</b> <span class="est-chip est-oficial">oficial</span>, que son <b>' + pesos(v) + ' por m²</b> <span class="est-chip est-derivado">derivado</span> (la hectárea ÷ 10,000 m², al centavo). Escribe arriba tu terreno en m² (una hectárea son 10,000 m²).'
      : 'Valor de suelo: <b>' + pesos(v) + ' por m²</b> <span class="est-chip est-oficial">oficial</span>.') + ' Ya lo pusimos arriba. ' + (L.nota ? esc(L.nota) : '');
  }
  function calidades(T) {
    var u = T.usos[$('cpTUso').value];
    $('cpTCal').innerHTML = u.cal.map(function (c, i) { return '<option value="' + i + '"' + (c[0] === 'Medio' ? ' selected' : '') + '>' + esc(c[0]) + '</option>'; }).join('');
  }
  function pintaTabla() {
    var m = ley($('cpEnt').value, $('cpMun').value), T = m && D.tablas ? D.tablas[m.id] : null;
    if (!T) return;
    var v = valorConstruccion(T, $('cpTUso').value, +$('cpTCal').value, +$('cpTEdad').value, +$('cpTEst').value, $('cpTNiv').checked);
    if (v === null) {
      $('cpTablaVal').innerHTML = '<span class="est-chip est-pendiente">pendiente</span> Esta celda no se lee sin duda en la copia escaneada que publicó el Periódico Oficial; no la adivinamos. Búscala en el decreto o en tu recibo, y escribe tu valor abajo.';
      return;
    }
    $('cpVc').value = String(v);
    $('cpTablaVal').innerHTML = 'Valor de construcción: <b>' + pesos(v) + ' por m²</b> <span class="est-chip est-oficial">oficial</span>' + ($('cpTNiv').checked && T.niveles ? ' (con +' + T.niveles.pct + ' %: ' + esc(T.niveles.art) + ')' : '') + '. Ya lo pusimos abajo.';
  }

  function compara() {
    var vf = num('cpVf');
    if (!(vf > 0)) vf = 2500000;
    var tipo = $('cpTipo').value;
    $('cpCompCap').textContent = 'Predial anual de un predio ' + (tipo === 'baldio' ? 'baldío' : tipo === 'com' ? 'comercial' : tipo === 'rust' ? 'rústico' : 'construido') + ' con valor fiscal de ' + pesos(vf);
    var ent = $('cpEnt').value;
    var filas = D.mun.filter(function (m) { return m.ent === ent; }).map(function (m) { return [m, anual(m, vf, tipo)]; }).sort(function (a, b) { return a[1] - b[1]; });
    $('cpComp').innerHTML = filas.map(function (f) {
      var m = f[0];
      if (!m.recargo) return '<tr><th scope="row">' + esc(m.nombre) + '</th><td>' + pesos(f[1]) + '</td><td>pendientes</td></tr>';
      return '<tr><th scope="row">' + esc(m.nombre) + '</th><td>' + pesos(f[1]) + '</td><td>' + m.recargo.pct + ' % · ' + (m.multa ? (m.multa.min === m.multa.max ? m.multa.min : m.multa.min + '–' + m.multa.max) + ' %' : 'no la fija') + '</td></tr>';
    }).join('');    mercado();
  }

  /* El mercado de la vivienda junto al valor fiscal (Índice SHF, 21-11-2026). Los precios y las variaciones son
     oficiales (SHF); dónde cae tu valor y la escala, cuenta nuestra. No es un avalúo ni el valor de tu predio. */
  var TRIM = ['primer', 'segundo', 'tercer', 'cuarto'];
  function mercado() {
    var S = D.shf, ent = $('cpEnt').value, E = S.est[ent], caja = $('cpMerCuerpo');
    if (!E) { caja.innerHTML = ''; return; }
    var o = $('cpMun').options[$('cpMun').selectedIndex], nom = o ? o.textContent.replace(/ ✓$/, '') : '';
    var m = ley(ent, $('cpMun').value), mi = m ? S.mun[m.id] : null, P = E.precios, en = D.ent[ent];
    var corte = TRIM[S.trim - 1] + ' trimestre', ofi = ' <span class="est-chip est-oficial">oficial</span>', aud = ' <span class="est-chip est-derivado">auditada</span>';
    var vf = num('cpVf'), tipo = $('cpTipo').value, h = '';
    h += '<p>En <b>' + esc(en) + '</b>, la mitad de las viviendas valuadas en ' + S.anio + ' valió menos de <b>' + mdp(P.p50) + '</b> (la mediana), una de cada cuatro, menos de ' + mdp(P.p25) +
      ' y una de cada cuatro, más de ' + mdp(P.p75) + '. El precio medio fue de ' + mdp(P.medio) + ': queda arriba de la mediana porque unas pocas viviendas muy caras lo jalan.' + ofi + '</p>';
    var esc0 = Math.max(P.p75 * 1.5, vf > 0 ? vf * 1.1 : 0), pc = function (v) { return Math.min(100, v / esc0 * 100).toFixed(1) + '%'; };
    var marca = function (v, c, t, abajo) {
      var x = v / esc0, lado = x < 0.25 ? ' cp-izq' : (x > 0.7 ? ' cp-der' : '');
      return '<span class="cp-esc-m ' + c + (abajo ? ' cp-esc-ab' : '') + (c === 'cp-esc-tu' ? (x > 0.5 ? ' cp-der' : ' cp-izq') : lado) + '" style="left:' + pc(v) + '"><span>' + t + '</span></span>';
    };
    var g = '<div class="cp-esc" role="img" aria-label="Escala de precios de avalúo de vivienda en ' + esc(en) + (vf > 0 && tipo === 'edif' ? ' con tu valor fiscal marcado' : '') + '">' +
      '<div class="cp-esc-barra"><span class="cp-esc-banda" style="left:' + pc(P.p25) + ';width:' + (Math.min(100, P.p75 / esc0 * 100) - P.p25 / esc0 * 100).toFixed(1) + '%"></span></div>' +
      marca(P.p25, '', '25 %: ' + mdp(P.p25), true) + marca(P.p50, 'cp-esc-q', 'Mediana: ' + mdp(P.p50), false) + marca(P.p75, 'cp-esc-ab2', '75 %: ' + mdp(P.p75), true) +
      (vf > 0 && tipo === 'edif' ? marca(vf, 'cp-esc-tu', 'Tu valor fiscal: ' + mdp(vf), false) : '') + '</div>' +
      '<p class="ci-pista">La franja es la mitad de en medio de los avalúos de ' + esc(en) + ' (del 25 % al 75 %).</p>';
    h += g;
    if (!(vf > 0)) {
      h += '<p>Escribe arriba el valor fiscal de tu predio y lo marcamos en la escala.</p>';
    } else if (tipo !== 'edif') {
      h += '<p>El Índice SHF mide <b>vivienda</b>; para un predio ' + (tipo === 'rust' ? 'rústico' : tipo === 'com' ? 'comercial' : 'baldío') + ' no hay comparación justa, así que no lo marcamos.</p>';
    } else {
      var q = cuartil(P, vf);
      var dice = ['abajo de una de cada cuatro viviendas valuadas: al menos tres de cada cuatro valieron más que eso',
        'entre la cuarta parte más barata y la mediana: más de la mitad de las viviendas valuadas valió más',
        'entre la mediana y el 75 %: más de la mitad valió menos, pero una de cada cuatro valió más de ' + mdp(P.p75),
        'arriba del 75 %: menos de una de cada cuatro viviendas valuadas valió más que eso'][q];
      h += '<p>Tu valor fiscal de <b>' + mdp(vf) + '</b> queda ' + dice + '.' + aud + '</p>' +
        '<p class="ci-nota">Ojo: tu valor fiscal y un precio de avalúo no son la misma medida, y los precios del estado mezclan muchas ciudades, colonias y tipos de vivienda. Que tu valor fiscal quede bajo o alto en la escala no quiere decir que el catastro lo tenga mal: es una señal para preguntar, no una conclusión.</p>';
    }
    if (mi) h += '<p><b>' + esc(nom) + '</b> es uno de los municipios que mide la SHF: su índice subió <b>' + mi['var'] + ' %</b> del ' + corte + ' de ' + (S.anio - 1) + ' al de ' + S.anio + ofi + ' (en todo ' + esc(en) + ', ' + E.var + ' %).</p>';
    else h += '<p>En <b>' + esc(en) + '</b>, el índice subió <b>' + E.var + ' %</b> del ' + corte + ' de ' + (S.anio - 1) + ' al de ' + S.anio + ofi + '. ' + (nom ? 'La SHF no publica un índice propio de ' + esc(nom) + '; damos el del estado.' : '') + '</p>';
    h += '<p class="ci-nota">Subir el índice no sube tu predial: el predial cambia cuando el Congreso aprueba nuevas tablas de valores y tu Ley de Ingresos. Lo que sí dice es cuánto se movió el mercado mientras tus tablas se quedaban quietas o cambiaban.</p>';
    caja.innerHTML = h;
  }

  function pinta(e) {
    if (e) e.preventDefault();
    var m = ley($('cpEnt').value, $('cpMun').value), res = $('cpRes'), tot = $('cpTotal');
    compara();
    if (!m) return;
    var vf = num('cpVf');
    res.hidden = false;
    if (!(vf > 0)) {
      tot.innerHTML = '<p class="ci-error">Escribe, con números, el valor fiscal de tu predio.</p>';
      $('cpPasos').innerHTML = ''; $('cpNota').textContent = ''; $('cpDeudaCaja').hidden = true;
      return;
    }
    var x = { vf: vf, tipo: $('cpTipo').value, ben: $('cpBen').value, pago: $('cpPago').value };
    var r = calcula(D, m, x);
    var U = { m: m, x: x, r: r, d: null, y: null, c: null, benTx: x.ben ? opTxt('cpBen') : 'Ninguno', pagoTx: opTxt('cpPago') };
    var h = '<p class="ci-cifra">Tu predial en ' + esc(m.nombre) + ': <b>' + pesos(r.fin) + ' al año</b></p>' +
      '<p>' + (r.pr ? 'En una sola exhibición.' : 'Son ' + pesos(r2(r.conBen / 6)) + ' cada bimestre, ' + (m.venc || 'que se pagan en los primeros quince días del primer mes de cada bimestre (enero, marzo, mayo, julio, septiembre y noviembre)') + '.') +
      (r.fin < r.anual ? ' Sin descuentos serían ' + pesos(r.anual) + '.' : '') + '</p>';
    tot.innerHTML = h;
    var fila = function (p) {
      return '<tr' + (p[3] === 'b' ? ' class="ci-fuerte"' : '') + '><th scope="row">' + esc(p[0]) + '</th><td>' + (p[1] == null ? '' : pesos(p[1])) + '</td><td>' + esc(p[2]) + '</td></tr>';
    };
    $('cpPasos').innerHTML = r.pasos.map(fila).join('');
    var avisos = r.avisos.slice();
    if ($('cpDebe').checked) {
      var porAnio = !!(m.recargo && m.recargo.anual);
      if (!$('cpImp').value) $('cpImp').value = String(porAnio ? r2(r.conBen) : r2(r.conBen / 6));
      var imp = num('cpImp'), fs = ($('cpF').value || '').split('-').map(Number);
      var y = { imp: imp, da: +$('cpDa').value, db: +$('cpDb').value, ha: +$('cpHa').value, hb: +$('cpHb').value, f: fs, sit: $('cpSit').value, multa: +($('cpMulta').value || 0) };
      var d;
      if (porAnio) { y.db = 1; y.hb = 6; }
      if (!(imp > 0) || fs.length !== 3 || !fs[0]) d = { error: 'Para el adeudo escribe el impuesto de cada ' + (porAnio ? 'año' : 'bimestre') + ' y el día que pagarías.' };
      else if (y.ha * 6 + y.hb < y.da * 6 + y.db) d = { error: 'El bimestre «hasta» no puede ser antes del bimestre «desde».' };
      else d = adeudo(D, m, y);
      $('cpDeudaCaja').hidden = false;
      if (!d.error) { U.d = d; U.y = y; U.y.fs = $('cpF').value; }
      if (d.error) {
        $('cpDeudaPasos').innerHTML = '<tr><td colspan="3" class="ci-error">' + esc(d.error) + '</td></tr>';
      } else {
        $('cpDeudaPasos').innerHTML = d.pasos.map(fila).join('');
        tot.innerHTML += '<p class="ci-cifra">Para ponerte al corriente (' + d.n + ' ' + (d.per || 'bimestre') + (d.n > 1 ? 's' : '') + '): <b>' + pesos(d.total) + '</b></p>';
        avisos = avisos.concat(d.avisos);
      }
    } else {
      $('cpDeudaCaja').hidden = true;
    }
    var cobro = num('cpCobro'), cx = $('cpContraste');
    if (cobro > 0) {
      var c = contrasta(m, x, r, { cobro: cobro, per: $('cpPer').value }), per = c.per === 'anual' ? 'al año' : 'por bimestre';
      U.c = c; c.cobro = cobro;
      var t = '<h3 class="ci-tit">⚖️ Tu recibo contra la ley</h3><p>Te cobran <b>' + pesos(cobro) + ' ' + per + '</b>; con tu valor fiscal, la Ley de Ingresos de ' + esc(m.nombre) + ' da <b>' + pesos(c.ley) + '</b> <span class="est-chip est-derivado">auditada</span>.</p>';
      if (c.cuadra) t += '<p class="cp-ok">✓ Coinciden: la diferencia es de ' + pesos(c.dif) + '.</p>';
      else {
        t += '<p class="cp-falta">La diferencia es de <b>' + pesos(c.dif) + '</b> (' + (c.pct > 0 ? '+' : '') + c.pct + ' %). Es una señal para revisar, no quiere decir que te cobren mal.</p>';
        if (c.sinBen) t += '<p>Lo que te cobran es justo el impuesto <b>sin el descuento</b> que escogiste: quizá no está aplicado en tu cuenta.</p>';
        if (c.vfImplicito) t += '<p>Con lo que te cobran, la tabla de ' + esc(m.nombre) + ' corresponde a un valor fiscal de unos <b>' + pesos(Math.round(c.vfImplicito)).replace(/\.00$/, '') + '</b> <span class="est-chip est-derivado">auditada</span>: compáralo con el que trae tu recibo.</p>';
        t += '<p>Causas comunes, para preguntar en la tesorería:</p><ul class="ci-lista">' + c.causas.map(function (k) { return '<li>' + esc(k) + '</li>'; }).join('') + '</ul>';
        t += '<p>Pide el <b>desglose por escrito</b>. Si no estás de acuerdo con un cobro, la ley te da plazo para el recurso de reconsideración o el juicio ante el Tribunal de Justicia Administrativa.</p>';
      }
      cx.innerHTML = t; cx.hidden = false;
    } else {
      cx.hidden = true;
    }
    $('cpNota').textContent = avisos.concat(['Es una cuenta aproximada (auditada, no oficial). Tu adeudo oficial te lo da la tesorería de ' + m.nombre + '.']).join(' ');
    U.avisos = avisos;
    informe(U);
  }

  /* El informe de tu predial (21-11-2026): lo mismo que está en pantalla, en un documento para imprimir,
     guardar en PDF o descargar en texto, con folio y huella SHA-256 de tus datos y sus cifras (la fecha no
     entra: los mismos datos dan siempre el mismo folio). Un solo modelo (docInforme) se pinta en HTML y en
     texto. No agrega cifras, no es un documento oficial y nada sale del navegador. */
  var ULT = null, TIPOS = { edif: 'Construido (casa, departamento, local)', rust: 'Rústico (fuera de la zona urbana)', baldio: 'Baldío en zona urbana' };
  function opTxt(id) { var s = $(id), o = s.options[s.selectedIndex]; return o ? o.textContent : ''; }
  function ligaDe(U) {
    var p = new URLSearchParams();
    p.set('mun', U.m.id); p.set('vf', String(U.x.vf)); p.set('tipo', U.x.tipo);
    if (U.x.ben) p.set('ben', U.x.ben);
    if (U.x.pago && U.x.pago !== 'bim') p.set('pago', U.x.pago);
    if (U.c) { p.set('cobro', String(U.c.cobro)); p.set('per', U.c.per); }
    if (U.y) { ['imp', 'da', 'db', 'ha', 'hb', 'sit', 'multa'].forEach(function (k) { p.set(k, String(U.y[k])); }); p.set('f', U.y.fs); }
    return location.origin + location.pathname + '?' + p.toString();
  }
  function docInforme(U) {
    var m = U.m, x = U.x, r = U.r, S = D.shf, E = S.est[m.ent], mi = S.mun[m.id], sec = [];
    sec.push({ t: 'Tu predio', dl: [['Municipio', m.nombre + ', ' + D.ent[m.ent]], ['Ley con que se cobra', m.ley],
      ['Valor fiscal', pesos(x.vf) + ' (lo escribiste tú; el oficial es el que registra el catastro)'], ['Tipo de predio', TIPOS[x.tipo]],
      ['Descuento', U.benTx + (x.ben && !r.ben ? ' (no aplica con tu valor fiscal)' : '')], ['Forma de pago', U.pagoTx]] });
    sec.push({ t: 'Tu predial de ' + D.anio, est: 'derivado',
      p: ['Pagas ' + pesos(r.fin) + ' al año' + (r.pr ? ', en una sola exhibición.' : ', en seis bimestres de ' + pesos(r2(r.conBen / 6)) + '.') + (r.fin < r.anual ? ' Sin descuentos serían ' + pesos(r.anual) + '.' : '')],
      tab: { cab: ['Paso', 'Pesos', 'Regla'], filas: r.pasos } });
    if (U.c) {
      var c = U.c, cp = { t: 'Tu recibo contra la ley', est: 'derivado',
        p: ['Te cobran ' + pesos(c.cobro) + (c.per === 'anual' ? ' al año' : ' por bimestre') + '; con tu valor fiscal, la ley da ' + pesos(c.ley) + '.'] };
      if (c.cuadra) cp.p.push('Coinciden: la diferencia es de ' + pesos(c.dif) + '.');
      else {
        cp.p.push('La diferencia es de ' + pesos(c.dif) + ' (' + (c.pct > 0 ? '+' : '') + c.pct + ' %). Es una señal para pedir el desglose por escrito, no quiere decir que te cobren mal.');
        if (c.sinBen) cp.p.push('Lo que te cobran es justo el impuesto sin el descuento que escogiste: quizá no está aplicado en tu cuenta.');
        if (c.vfImplicito) cp.p.push('Con lo que te cobran, la tabla de ' + m.nombre + ' corresponde a un valor fiscal de unos ' + pesos(Math.round(c.vfImplicito)).replace(/\.00$/, '') + ': compáralo con el de tu recibo.');
        cp.li = c.causas; cp.liTit = 'Causas comunes, para preguntar en la tesorería:';
      }
      sec.push(cp);
    }
    if (U.d) sec.push({ t: 'Si te pones al corriente', est: 'derivado',
      p: ['Por ' + U.d.n + ' ' + (U.d.per || 'bimestre') + (U.d.n > 1 ? 's' : '') + ', pagando el ' + U.y.fs.split('-').reverse().join('-') + ': ' + pesos(U.d.total) + '.'],
      tab: { cab: ['Concepto', 'Pesos', 'Regla'], filas: U.d.pasos } });
    if (E) {
      var P = E.precios, mp = { t: 'Junto al mercado de la vivienda', est: 'oficial',
        p: ['En ' + D.ent[m.ent] + ', las viviendas valuadas en ' + S.anio + ' tuvieron una mediana de ' + mdp(P.p50) + '; una de cada cuatro valió menos de ' + mdp(P.p25) + ' y una de cada cuatro, más de ' + mdp(P.p75) + ' (Índice SHF, ' + S.corte + ').'] };
      if (x.tipo === 'edif') mp.p.push('Tu valor fiscal queda ' + ['abajo del 25 %', 'entre el 25 % y la mediana', 'entre la mediana y el 75 %', 'arriba del 75 %'][cuartil(P, x.vf)] + ' de esos precios (cuenta nuestra, auditada). Tu valor fiscal y un precio de avalúo no son la misma medida: no es un avalúo, no es el valor de tu predio y una diferencia no es un error del catastro.');
      else mp.p.push('El índice mide vivienda: para un terreno ' + (x.tipo === 'rust' ? 'rústico' : 'baldío') + ' no hay comparación justa.');
      mp.p.push((mi ? 'El índice de ' + m.nombre + ' subió ' + mi['var'] : 'El índice de ' + D.ent[m.ent] + ' subió ' + E['var']) + ' % en un año. Eso no sube tu predial: lo cambian las tablas de valores y la Ley de Ingresos que aprueba el Congreso.');
      sec.push(mp);
    }
    if (U.avisos.length) sec.push({ t: 'Avisos de la cuenta', li: U.avisos });
    var fu = [{ tx: m.ley + ' (' + m.art_tarifa + ' y los artículos de cada paso)', url: m.url, sha: m.sha256 },
      { tx: D.lhm.tx + ', arts. 44 bis, 52 y 103', url: D.lhm.url, sha: D.lhm.sha256 }];
    if (E) fu.push({ tx: S.fuente + ', ' + S.corte, url: S.inf.url, sha: S.inf.sha256 });
    sec.push({ t: 'Fuentes', fu: fu });
    sec.push({ t: 'Lo que este informe no es', p: ['No es un documento oficial, ni tu estado de cuenta, ni un avalúo, ni una resolución: es la cuenta de la ley con los datos que escribiste, hecha en tu navegador. Tu adeudo oficial te lo da la tesorería de ' + m.nombre + ', y cambia cada mes.',
      'Las tarifas son las de ' + D.anio + ' y los años anteriores tuvieron las suyas; no incluye derechos de agua o basura, convenios, condonaciones ni los gastos extraordinarios de un embargo.'] });
    return { municipio: m.nombre + ', ' + D.ent[m.ent], emitido: new Date().toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' }), sec: sec, liga: ligaDe(U) };
  }
  var CHIP = { oficial: '<span class="est-chip est-oficial">oficial</span>', derivado: '<span class="est-chip est-derivado">auditada</span>' };
  function infHtml(I) {
    var h = '<header class="cp-inf-cab"><p class="cp-inf-marca">Auditavisión · Calculadora Cívica</p><h3 class="cp-inf-tit">Informe de tu predial</h3>' +
      '<dl class="cp-inf-meta"><div><dt>Folio</dt><dd class="cp-inf-folio">calculando…</dd></div><div><dt>Emitido</dt><dd>' + esc(I.emitido) + '</dd></div><div><dt>Municipio</dt><dd>' + esc(I.municipio) + '</dd></div></dl></header>';
    I.sec.forEach(function (s, i) {
      h += '<section class="cp-inf-sec"><h4>' + (i + 1) + '. ' + esc(s.t) + (s.est ? ' ' + CHIP[s.est] : '') + '</h4>';
      if (s.dl) h += '<dl class="cp-inf-dl">' + s.dl.map(function (d) { return '<div><dt>' + esc(d[0]) + '</dt><dd>' + esc(d[1]) + '</dd></div>'; }).join('') + '</dl>';
      (s.p || []).forEach(function (t) { h += '<p>' + esc(t) + '</p>'; });
      if (s.tab) h += '<table class="cp-inf-tabla"><thead><tr>' + s.tab.cab.map(function (c) { return '<th scope="col">' + esc(c) + '</th>'; }).join('') + '</tr></thead><tbody>' +
        s.tab.filas.map(function (f) { return '<tr' + (f[3] === 'b' ? ' class="ci-fuerte"' : '') + '><th scope="row">' + esc(f[0]) + '</th><td>' + (f[1] == null ? '' : pesos(f[1])) + '</td><td>' + esc(f[2]) + '</td></tr>'; }).join('') + '</tbody></table>';
      if (s.li) h += (s.liTit ? '<p>' + esc(s.liTit) + '</p>' : '') + '<ul>' + s.li.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') + '</ul>';
      if (s.fu) h += '<ul>' + s.fu.map(function (f) { return '<li><a href="' + esc(f.url) + '">' + esc(f.tx) + '</a><br><span class="cp-inf-sha">SHA-256 ' + esc(f.sha) + '</span></li>'; }).join('') + '</ul>';
      h += '</section>';
    });
    return h + '<footer class="cp-inf-pie"><p>Huella digital (SHA-256 de tus datos y de estas cifras): <code class="cp-inf-huella">calculando…</code></p>' +
      '<p>Para repetir la cuenta: <a class="cp-inf-liga" href="' + esc(I.liga) + '">abre esta liga</a>. Lleva tus cifras: compártela solo si quieres.</p></footer>';
  }
  function infTexto(I, folio, huella) {
    var L = ['INFORME DE TU PREDIAL · Auditavisión, Calculadora Cívica', 'Folio: ' + (folio || 'no disponible') + ' · Emitido: ' + I.emitido, 'Municipio: ' + I.municipio, ''];
    I.sec.forEach(function (s, i) {
      L.push((i + 1) + '. ' + s.t.toUpperCase() + (s.est ? ' [' + (s.est === 'oficial' ? 'oficial' : 'auditada') + ']' : ''));
      (s.dl || []).forEach(function (d) { L.push('   ' + d[0] + ': ' + d[1]); });
      (s.p || []).forEach(function (t) { L.push('   ' + t); });
      if (s.tab) s.tab.filas.forEach(function (f) { L.push('   - ' + f[0] + (f[1] == null ? '' : ': ' + pesos(f[1])) + ' (' + f[2] + ')'); });
      if (s.liTit) L.push('   ' + s.liTit);
      (s.li || []).forEach(function (t) { L.push('   - ' + t); });
      (s.fu || []).forEach(function (f) { L.push('   - ' + f.tx + ': ' + f.url + ' (SHA-256 ' + f.sha + ')'); });
      L.push('');
    });
    L.push('Huella digital (SHA-256 de tus datos y de estas cifras): ' + (huella || 'no disponible'));
    L.push('Para repetir la cuenta: ' + I.liga);
    return L.join('\r\n') + '\r\n';
  }
  function huellaDe(U) {
    var obj = { ley: U.m.sha256, mun: U.m.id, x: U.x, pasos: U.r.pasos, fin: U.r.fin, cobro: U.c ? [U.c.cobro, U.c.per, U.c.ley] : null,
      deuda: U.d ? { y: U.y, pasos: U.d.pasos, total: U.d.total } : null };
    try {
      return crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(obj))).then(function (b) {
        return Array.prototype.map.call(new Uint8Array(b), function (v) { return ('0' + v.toString(16)).slice(-2); }).join('');
      }).catch(function () { return null; });
    } catch (e) { return Promise.resolve(null); }
  }
  function informe(U) {
    var I = docInforme(U), caja = $('cpInforme');
    ULT = { U: U, I: I, folio: null, huella: null };
    caja.innerHTML = infHtml(I);
    $('cpInfAcc').hidden = false; $('cpInfMsg').textContent = '';
    var yo = ULT;
    huellaDe(U).then(function (h) {
      if (ULT !== yo) return;
      yo.huella = h; yo.folio = h ? 'AV-PR-' + h.slice(0, 8).toUpperCase() : null;
      caja.querySelector('.cp-inf-folio').textContent = yo.folio || 'no disponible en este navegador';
      caja.querySelector('.cp-inf-huella').textContent = h || 'este navegador no calcula huellas SHA-256';
    });
  }
  function imprime() {
    if (!ULT) return;
    var raiz = document.createElement('div'), ver = $('cpInfVer');
    raiz.id = 'cpPrintRaiz'; raiz.className = 'cp-informe'; raiz.innerHTML = $('cpInforme').innerHTML;
    document.body.appendChild(raiz); document.body.classList.add('cp-print');
    var fin = function () { document.body.classList.remove('cp-print'); if (raiz.parentNode) raiz.parentNode.removeChild(raiz); window.removeEventListener('afterprint', fin); };
    window.addEventListener('afterprint', fin);
    window.print();
    setTimeout(fin, 1000);
    if (ver) ver.open = true;
  }
  function descarga() {
    if (!ULT) return;
    var b = new Blob([infTexto(ULT.I, ULT.folio, ULT.huella)], { type: 'text/plain;charset=utf-8' }), a = document.createElement('a');
    a.href = URL.createObjectURL(b); a.download = 'informe-predial-' + ULT.U.m.id + (ULT.folio ? '-' + ULT.folio : '') + '.txt';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 2000);
    $('cpInfMsg').textContent = 'Listo: se descargó tu informe en texto.';
  }
  function copiaLiga() {
    if (!ULT) return;
    var l = ULT.I.liga, ok = function () { $('cpInfMsg').textContent = 'Copiamos la liga: al abrirla, la página repite tu cuenta. Lleva tus cifras; compártela solo si quieres.'; };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(l).then(ok, function () { $('cpInfMsg').textContent = l; });
    else $('cpInfMsg').textContent = l;
  }

  /* Lo que llega por la dirección (?mun=zapopan&vf=…), para que el chat abra la cuenta ya puesta. */
  var q = null;
  try { q = new URLSearchParams(location.search); } catch (e) { /* sin parámetros */ }
  var pedidoId = q && q.get('mun') && D.munEnt && D.munEnt[q.get('mun')] ? q.get('mun') : null;
  if (pedidoId) $('cpEnt').value = D.munEnt[pedidoId];
  /* ?ent=CDMX: la entidad sin municipio (en la Ciudad de México la tarifa es la misma para las 16 alcaldías). */
  else if (q && q.get('ent') && D.ent[q.get('ent')]) $('cpEnt').value = q.get('ent');
  entDatos($('cpEnt').value).then(inicia);
  function inicia() {
  var pedido = pedidoId ? D.mun.filter(function (m) { return m.id === pedidoId; })[0] : null;
  llenaMunicipios();
  /* ?ent=GTO&cve=020: un municipio sin tabla integrada (el chat lo manda así para León, en espera). */
  $('cpMun').value = pedido ? pedido.cve : (q && q.get('ent') && q.get('cve')) || '120';
  if (!$('cpMun').value) $('cpMun').selectedIndex = 0;
  ficha();
  if (q && q.get('vf')) $('cpVf').value = q.get('vf');
  var hoy = new Date();
  $('cpF').value = hoy.toISOString().slice(0, 10);
  $('cpDb').value = '1';
  $('cpHb').value = String(Math.max(1, Math.ceil((hoy.getMonth() + 1) / 2)));
  /* La liga del informe trae además el tipo, el descuento, el pago, el recibo y el adeudo. */
  if (q) {
    var pon = function (id, k) { var v = q.get(k); if (v === null) return; var el = $(id); if (el.tagName === 'SELECT' && ![].some.call(el.options, function (o) { return o.value === v; })) return; el.value = v; };
    pon('cpTipo', 'tipo'); pon('cpBen', 'ben'); pon('cpPago', 'pago'); pon('cpCobro', 'cobro'); pon('cpPer', 'per');
    if (q.get('imp')) {
      $('cpDebe').checked = true; $('cpDeuda').hidden = false;
      pon('cpImp', 'imp'); pon('cpDa', 'da'); pon('cpDb', 'db'); pon('cpHa', 'ha'); pon('cpHb', 'hb'); pon('cpSit', 'sit'); pon('cpMulta', 'multa');
      if (/^\d{4}-\d{2}-\d{2}$/.test(q.get('f') || '')) $('cpF').value = q.get('f');
      $('cpMultaCaja').hidden = $('cpSit').value === 'esp';
    }
  }
  $('cpImprime').addEventListener('click', imprime);
  $('cpBaja').addEventListener('click', descarga);
  $('cpLiga').addEventListener('click', copiaLiga);
  $('cpEnt').addEventListener('change', function () {
    entDatos($('cpEnt').value).then(function () { llenaMunicipios(); ficha(); $('cpRes').hidden = true; mercado(); compara(); });
  });
  $('cpMun').addEventListener('change', function () { ficha(); $('cpRes').hidden = true; mercado(); });
  $('cpTipo').addEventListener('change', compara);
  $('cpVf').addEventListener('input', compara);
  $('cpDebe').addEventListener('change', function () { $('cpDeuda').hidden = !this.checked; if (this.checked) inpcListo(); });
  $('cpSit').addEventListener('change', function () { $('cpMultaCaja').hidden = this.value === 'esp'; });
  $('cpMultaCaja').hidden = $('cpSit').value === 'esp';
  $('cpForm').addEventListener('submit', function (e) {
    e.preventDefault();
    if ($('cpDebe').checked) inpcListo().then(function () { pinta(); }); else pinta();
  });
  $('cpSueloSel').addEventListener('change', pintaSuelo);
  ['cpTCal', 'cpTEdad', 'cpTEst', 'cpTNiv'].forEach(function (id) { $(id).addEventListener('change', pintaTabla); });
  $('cpTUso').addEventListener('change', function () {
    var m = ley($('cpEnt').value, $('cpMun').value);
    if (m && D.tablas[m.id]) { calidades(D.tablas[m.id]); pintaTabla(); }
  });
  $('cpVfUsa').addEventListener('click', function () {
    var t = { ts: num('cpTs'), vs: num('cpVs'), tc: num('cpTc') || 0, vc: num('cpVc') || 0, fc: num('cpFc') };
    if (!(t.ts > 0 && t.vs > 0) || (t.tc > 0 && !(t.vc > 0))) {
      $('cpVfRes').textContent = 'Escribe al menos los metros de terreno y su valor unitario; si hay construcción, también su valor unitario.';
      return;
    }
    var v = valorFiscal(t);
    $('cpVf').value = String(v);
    $('cpVfRes').innerHTML = 'Valor fiscal estimado: <b>' + pesos(v) + '</b> = ' + t.ts + ' m² × ' + pesos(t.vs) + (t.tc ? ' + ' + t.tc + ' m² × ' + pesos(t.vc) + (t.fc && t.fc !== 1 ? ' × ' + t.fc : '') : '') +
      ' <span class="est-chip est-derivado">auditada</span>. Es tu cuenta con los valores que escribiste; el oficial es el que registra el catastro. Ya lo pusimos arriba.';
    compara();
  });
  mercado();
  if (num('cpVf') > 0) { if ($('cpDebe').checked) inpcListo().then(function () { pinta(); }); else pinta(); }
  }
})();
