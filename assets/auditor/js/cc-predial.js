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
    return r2((vf - t[0]) * t[2] + t[1]);
  }
  function tramo(m, vf) {
    var k = 0;
    for (var i = 0; i < m.tramos.length; i++) if (vf >= m.tramos[i][0]) k = i;
    return k;
  }
  /* tipo: 'edif' (construido), 'rust' (rústico: su propia tasa al millar si la ley la da) o 'baldio'. */
  function base(m, vf, tipo) {
    if (tipo === 'rust' && m.rustico) return r2(vf * m.rustico.millar / 1000 + m.rustico.cf);
    if (tipo !== 'baldio') return bimestral(m, vf);
    var b = m.baldio;
    if (b.tipo === 'igual') return bimestral(m, vf);
    if (b.tipo === 'sobretasa') return r2(bimestral(m, vf) * (1 + b.pct / 100));
    return r2(vf * b.millar / 1000 + b.cf);
  }
  function cf2(v) { return '$' + Number(v).toLocaleString('es-MX', { minimumFractionDigits: 2 }); }

  /* x: {vf, tipo, ben, pago} */
  function calcula(D, m, x) {
    var pasos = [], avisos = [], ley = function (a) { return 'Ley de Ingresos de ' + m.nombre + ', ' + a; };
    var B = base(m, x.vf, x.tipo);
    if (x.tipo === 'rust' && m.rustico) {
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
    var A = r2(B * 6);
    var artB = x.tipo === 'rust' && m.rustico ? m.rustico.art : x.tipo === 'baldio' ? m.baldio.art : m.art_tarifa;
    pasos.push(['Impuesto del año (seis bimestres)', A, ley(artB), 'b']);
    var res = { bim: B, anual: A, pasos: pasos, avisos: avisos };

    /* El descuento: factor sobre el impuesto, a veces solo «sobre el primer» tanto del valor. */
    var ben = null, ahorroB = 0;
    if (x.ben) ben = m.beneficios.filter(function (b) { return b.id === x.ben; })[0] || null;
    if (ben && ben.hasta && x.vf > ben.hasta) {
      avisos.push('El descuento «' + ben.et + '» solo vale si el valor fiscal no rebasa $' + ben.hasta.toLocaleString('es-MX') + ' (' + ley(ben.art) + '): con tu valor no aplica.');
      ben = null;
    }
    if (ben) {
      var sobre = ben.tope && x.vf > ben.tope ? r2(base(m, ben.tope, x.tipo) * 6) : A;
      ahorroB = r2(sobre * (1 - ben.f));
      pasos.push(['Descuento: pagas ' + Math.round(ben.f * 100) + ' %' + (ben.tope && x.vf > ben.tope ? ' del impuesto que daría el primer $' + ben.tope.toLocaleString('es-MX') + ' de valor' : ''), -ahorroB, ley(ben.art)]);
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
        avisos.push(m.suma_art ? 'Tu Ley de Ingresos da solo el mayor de los dos beneficios (' + m.suma_art + ').' : 'La Ley de Ingresos de ' + m.nombre + ' no dice si se suman; aquí te damos el mayor de los dos.');
      } else {
        avisos.push(m.suma_art ? 'El descuento no se suma al pago anticipado (' + m.suma_art + '): te dejamos el descuento, que es mayor.' : 'La Ley de Ingresos de ' + m.nombre + ' no dice si el descuento se suma al pago anticipado; aquí te damos el mayor de los dos.');
      }
    }
    res.fin = r2(fin);
    res.pr = pr;
    res.ben = ben;
    pasos.push([pr ? 'Pagas por el año, en una sola exhibición' : 'Pagas por el año (en seis bimestres de ' + pesos(r2(A1 / 6)) + ')', res.fin, ley(pr ? pr.art : artB), 'b']);
    if (pr && m.pronto_nota) avisos.push(m.pronto_nota);
    if (m.tramos_nota) avisos.push(m.tramos_nota);
    if (x.tipo === 'rust' && !m.rustico) avisos.push('La Ley de Ingresos de ' + m.nombre + ' cobra a los predios rústicos con la misma tabla que a los urbanos.');
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

  function pesos(v) {
    return (v < 0 ? '−' : '') + '$' + Math.abs(Number(v)).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  window.AuditorPredial = { bimestral: bimestral, base: base, calcula: calcula, adeudo: adeudo };

  var raiz = document.getElementById('cpRaiz');
  if (!raiz) return;
  var D = JSON.parse(document.getElementById('cpDatos').textContent);
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

  function ficha() {
    var ent = $('cpEnt').value, cve = $('cpMun').value, m = ley(ent, cve), h = '';
    var e = MUN && MUN.ent[ent], r = e ? e.lista.filter(function (x) { return x[0] === cve; })[0] : null;
    var nom = r ? r[1] : (m ? m.nombre : '');
    if (r && r.length > 7) {
      var c = {}; MUN.campos.forEach(function (k, i) { c[k] = r[i]; });
      h += '<p><b>' + esc(nom) + '</b> recaudó <b>' + mdp(c.predial) + '</b> de predial en ' + MUN.anio + ': ' +
        (c.propios ? Math.round(c.predial / c.propios * 100) + ' de cada $100 de sus ingresos propios y ' : '') +
        Math.round(c.predial / c.ing * 100) + ' de cada $100 de todo lo que le entró <span class="est-chip est-oficial">oficial</span> <span class="cp-fuente">(INEGI, EFIPEM ' + MUN.anio + '; las proporciones, auditadas)</span>.</p>';
    } else if (r) {
      h += '<p><b>' + esc(nom) + '</b> no rindió cuenta al INEGI en ' + (MUN ? MUN.anio : '') + ': no sabemos cuánto recaudó de predial.</p>';
    }
    if (m) {
      h += '<p class="cp-ok">✓ Su tabla está integrada: <a href="' + esc(m.url) + '">' + esc(m.ley) + '</a>. Recargos: ' + m.recargo.pct + ' % al mes (' + esc(m.recargo.art) + ').</p>';
    } else if (D.espera && D.espera[ent + '-' + cve]) {
      var w = D.espera[ent + '-' + cve];
      h += '<p class="cp-falta"><span class="est-chip est-pendiente">pendiente</span> Leímos su <a href="' + esc(w.url) + '">Ley de Ingresos ' + D.anio + '</a>, pero no la integramos: ' + esc(w.motivo) + ' No adivinamos una tasa. Mientras, prueba con un municipio marcado con ✓.</p>';
    } else {
      h += '<p class="cp-falta"><span class="est-chip est-pendiente">pendiente</span> Aún no integramos la tabla del predial de su Ley de Ingresos ' + D.anio +
        ': es falta de esta plataforma, no del municipio. La ley la publica el congreso de su estado' +
        (ent === 'JAL' ? ' en su <a href="https://congresoweb.congresojal.gob.mx/BibliotecaVirtual/busquedasleyes/Listado%272.cfm">Biblioteca Virtual</a>' : '') +
        '. Mientras, prueba con un municipio marcado con ✓.</p>';
    }
    $('cpMunFicha').innerHTML = h;
    $('cpPredio').disabled = !m;
    if (m) {
      $('cpBen').innerHTML = '<option value="">Ninguno</option>' + m.beneficios.map(function (b) {
        return '<option value="' + esc(b.id) + '">' + esc(b.et) + ' — pagas ' + Math.round(b.f * 100) + ' %' + (b.tope ? ' sobre el primer $' + b.tope.toLocaleString('es-MX') : '') + (b.hasta ? ' (valor hasta $' + b.hasta.toLocaleString('es-MX') + ')' : '') + '</option>';
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
    compara();
    return m;
  }

  function compara() {
    var vf = num('cpVf');
    if (!(vf > 0)) vf = 2500000;
    var tipo = $('cpTipo').value;
    $('cpCompCap').textContent = 'Predial anual de un predio ' + (tipo === 'baldio' ? 'baldío' : 'construido') + ' con valor fiscal de ' + pesos(vf);
    var filas = D.mun.map(function (m) { return [m, r2(base(m, vf, tipo) * 6)]; }).sort(function (a, b) { return a[1] - b[1]; });
    $('cpComp').innerHTML = filas.map(function (f) {
      var m = f[0];
      return '<tr><th scope="row">' + esc(m.nombre) + '</th><td>' + pesos(f[1]) + '</td><td>' + m.recargo.pct + ' % · ' + (m.multa ? (m.multa.min === m.multa.max ? m.multa.min : m.multa.min + '–' + m.multa.max) + ' %' : 'no la fija') + '</td></tr>';
    }).join('');
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
    var h = '<p class="ci-cifra">Tu predial en ' + esc(m.nombre) + ': <b>' + pesos(r.fin) + ' al año</b></p>' +
      '<p>' + (r.pr ? 'En una sola exhibición.' : 'Son ' + pesos(r2(r.conBen / 6)) + ' cada bimestre, que se pagan en los primeros quince días del primer mes de cada bimestre (enero, marzo, mayo, julio, septiembre y noviembre).') +
      (r.fin < r.anual ? ' Sin descuentos serían ' + pesos(r.anual) + '.' : '') + '</p>';
    tot.innerHTML = h;
    var fila = function (p) {
      return '<tr' + (p[3] === 'b' ? ' class="ci-fuerte"' : '') + '><th scope="row">' + esc(p[0]) + '</th><td>' + (p[1] == null ? '' : pesos(p[1])) + '</td><td>' + esc(p[2]) + '</td></tr>';
    };
    $('cpPasos').innerHTML = r.pasos.map(fila).join('');
    var avisos = r.avisos.slice();
    if ($('cpDebe').checked) {
      if (!$('cpImp').value) $('cpImp').value = String(r2(r.conBen / 6));
      var imp = num('cpImp'), fs = ($('cpF').value || '').split('-').map(Number);
      var y = { imp: imp, da: +$('cpDa').value, db: +$('cpDb').value, ha: +$('cpHa').value, hb: +$('cpHb').value, f: fs, sit: $('cpSit').value, multa: +($('cpMulta').value || 0) };
      var d;
      if (!(imp > 0) || fs.length !== 3 || !fs[0]) d = { error: 'Para el adeudo escribe el impuesto de cada bimestre y el día que pagarías.' };
      else if (y.ha * 6 + y.hb < y.da * 6 + y.db) d = { error: 'El bimestre «hasta» no puede ser antes del bimestre «desde».' };
      else d = adeudo(D, m, y);
      $('cpDeudaCaja').hidden = false;
      if (d.error) {
        $('cpDeudaPasos').innerHTML = '<tr><td colspan="3" class="ci-error">' + esc(d.error) + '</td></tr>';
      } else {
        $('cpDeudaPasos').innerHTML = d.pasos.map(fila).join('');
        tot.innerHTML += '<p class="ci-cifra">Para ponerte al corriente (' + d.n + ' bimestre' + (d.n > 1 ? 's' : '') + '): <b>' + pesos(d.total) + '</b></p>';
        avisos = avisos.concat(d.avisos);
      }
    } else {
      $('cpDeudaCaja').hidden = true;
    }
    $('cpNota').textContent = avisos.concat(['Es una cuenta aproximada (auditada, no oficial). Tu adeudo oficial te lo da la tesorería de ' + m.nombre + '.']).join(' ');
  }

  /* Lo que llega por la dirección (?mun=zapopan&vf=…), para que el chat abra la cuenta ya puesta. */
  var q = null;
  try { q = new URLSearchParams(location.search); } catch (e) { /* sin parámetros */ }
  var pedido = q && q.get('mun') ? D.mun.filter(function (m) { return m.id === q.get('mun'); })[0] : null;
  if (pedido) $('cpEnt').value = pedido.ent;
  llenaMunicipios();
  $('cpMun').value = pedido ? pedido.cve : '120';
  if (!$('cpMun').value) $('cpMun').selectedIndex = 0;
  ficha();
  if (q && q.get('vf')) $('cpVf').value = q.get('vf');
  var hoy = new Date();
  $('cpF').value = hoy.toISOString().slice(0, 10);
  $('cpDb').value = '1';
  $('cpHb').value = String(Math.max(1, Math.ceil((hoy.getMonth() + 1) / 2)));
  $('cpEnt').addEventListener('change', function () { llenaMunicipios(); ficha(); $('cpRes').hidden = true; });
  $('cpMun').addEventListener('change', function () { ficha(); $('cpRes').hidden = true; });
  $('cpTipo').addEventListener('change', compara);
  $('cpVf').addEventListener('input', compara);
  $('cpDebe').addEventListener('change', function () { $('cpDeuda').hidden = !this.checked; });
  $('cpSit').addEventListener('change', function () { $('cpMultaCaja').hidden = this.value === 'esp'; });
  $('cpMultaCaja').hidden = true;
  $('cpForm').addEventListener('submit', pinta);
  if (num('cpVf') > 0) pinta();
})();
