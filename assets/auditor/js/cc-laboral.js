/* Auditavisión · Calculadora Cívica › Tu finiquito o tu liquidación (20-11-2026).
   La página la escribe herramientas/cc_laboral.py con la UMA, el salario mínimo y la tarifa del art. 96 en #clDatos.
   Aquí solo se hace la cuenta de la LFT (arts. 48 a 52, 76 a 89, 162, 485 y 486), la LISR (arts. 93, 95 y 96) y el RLISR (art. 174).
   calcula() es gemela de la de cc_laboral.py (--prueba). Nada se guarda ni se envía. */
(function () {
  'use strict';

  function dia(s) { var p = String(s).split('-'); return Date.UTC(+p[0], +p[1] - 1, +p[2]); }
  var DIA = 86400000;

  function vacTabla(n) {
    if (n <= 0) return 0;
    if (n <= 5) return 12 + 2 * (n - 1);
    return 20 + 2 * (Math.floor((n - 6) / 5) + 1);
  }

  function isrTarifa(D, m) {
    if (m <= 0) return 0;
    var f = D.tarifa[0];
    D.tarifa.forEach(function (r) { if (r[0] <= m) f = r; });
    return f[2] + Math.max(0, m - f[0]) * f[3] / 100;
  }

  function p2(v) { return '$' + Number(v).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

  function calcula(D, x) {
    var ing = dia(x.ing), sal = dia(x.sal);
    if (sal < ing) return { error: 'La fecha de salida no puede ser antes de la de ingreso.' };
    var sd = +x.sd;
    var dias = Math.round((sal - ing) / DIA) + 1;
    var anios = dias / 365, comp = Math.floor(dias / 365), dcur = dias - comp * 365;
    var agd = +x.agd || 15, pv = +x.pv || 25;
    var vacAnio = vacTabla(comp + 1);
    var sdi = sd * (1 + (agd + vacAnio * pv / 100) / 365);
    var c = [], r = { dias: dias, anios: anios, sdi: sdi, vac_anio: vacAnio, conc: c };
    var dp = +x.dp || 0;
    if (dp > 0) c.push(['salario', 'Días de salario que no te han pagado (' + dp + ' × salario diario)', dp * sd, 'LFT, art. 88']);
    var vprop = Math.max(0, vacAnio * dcur / 365 - (+x.vacTom || 0));
    var vdias = vprop + (+x.vacPend || 0), vac = vdias * sd;
    if (vac > 0) {
      c.push(['vacaciones', 'Vacaciones: ' + vdias.toFixed(2) + ' días (proporcionales del año en curso y pendientes)', vac, 'LFT, arts. 76 y 79']);
      c.push(['prima_vac', 'Prima vacacional (' + pv + ' % de tus vacaciones)', vac * pv / 100, 'LFT, art. 80']);
    }
    if (!x.agPag) {
      var y = Number(String(x.sal).slice(0, 4)), ini = Math.max(ing, Date.UTC(y, 0, 1));
      var dag = Math.round((sal - ini) / DIA) + 1;
      c.push(['aguinaldo', 'Aguinaldo proporcional (' + agd + ' días × ' + dag + ' días trabajados este año ÷ 365)', agd * dag / 365 * sd, 'LFT, art. 87']);
    }
    var z = x.zona || 'gen', tope = 2 * D.sm[z], piso = D.sm[z], causa = x.causa;
    if (causa === 'justificado' || causa === 'injustificado' || causa === 'sin_reinstalar' || (causa === 'renuncia' && anios >= 15)) {
      var bpa = Math.min(Math.max(sdi, piso), tope);
      c.push(['prima_ant', 'Prima de antigüedad: 12 días × ' + anios.toFixed(2) + ' años × ' + p2(bpa) + ' de salario (entre uno y dos salarios mínimos)',
        12 * anios * bpa, 'LFT, arts. 162, 485 y 486']);
    }
    if (causa === 'injustificado' || causa === 'sin_reinstalar') c.push(['ind3', 'Indemnización: tres meses (90 días) de salario integrado', 90 * sdi, 'LFT, arts. 48, 50 (fr. III) y 89']);
    if (causa === 'sin_reinstalar') c.push(['ind20', 'Veinte días de salario integrado por cada año de servicios (' + anios.toFixed(2) + ' años)', 20 * anios * sdi, 'LFT, arts. 49 y 50, fr. II']);
    var tot = 0, val = {};
    c.forEach(function (k) { tot += k[2]; val[k[0]] = k[2]; });
    var U = D.uma, m = (+x.mens || 0) || sd * 30;
    var isrM = isrTarifa(D, m), tasaM = m ? isrM / m : 0;
    var sep = (val.prima_ant || 0) + (val.ind3 || 0) + (val.ind20 || 0);
    var aniosIsr = comp + (anios - comp > 0.5 ? 1 : 0);
    var exSep = Math.min(sep, 90 * U * aniosIsr), gSep = sep - exSep, retSep = 0;
    if (gSep > 0) retSep = gSep < m ? isrTarifa(D, gSep) : gSep * tasaM;
    function art174(g) {
      if (g <= 0) return 0;
      var R = g / 365 * 30.4;
      return g * ((isrTarifa(D, m + R) - isrM) / R);
    }
    var ag = val.aguinaldo || 0, exAg = Math.min(ag, 30 * U), pvv = val.prima_vac || 0, exPv = Math.min(pvv, 15 * U);
    var retAg = art174(ag - exAg), retPv = art174(pvv - exPv);
    var retOrd = isrTarifa(D, (val.salario || 0) + (val.vacaciones || 0));
    var isr = retSep + retAg + retPv + retOrd;
    r.total = tot; r.exento = exSep + exAg + exPv; r.isr = isr; r.neto = tot - isr; r.m = m; r.tasa_m = tasaM;
    r.isr_det = [retOrd, retAg, retPv, retSep]; r.ex_det = [exAg, exPv, exSep]; r.anios_isr = aniosIsr;
    return r;
  }

  window.AuditorLaboral = { calcula: calcula, vacTabla: vacTabla };

  var raiz = document.getElementById('clRaiz');
  if (!raiz) return;
  var D = JSON.parse(document.getElementById('clDatos').textContent);
  var $ = function (id) { return document.getElementById(id); };
  function num(id) {
    var s = ($(id).value || '').replace(/[$,\s]/g, '');
    if (s === '') return null;
    var v = Number(s);
    return isFinite(v) && v >= 0 ? v : NaN;
  }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (ch) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]; }); }
  function ley() {
    var k = $('clCausa').value;
    D.causas.forEach(function (c) { if (c[0] === k) $('clCausaLey').textContent = c[2]; });
  }

  /* Lo que llega por la dirección (?s=&p=&ing=&sal=&causa=), para que el chat abra la cuenta ya puesta. */
  try {
    var q = new URLSearchParams(location.search);
    [['s', 'clSd'], ['p', 'clPer'], ['ing', 'clIng'], ['sal', 'clSal'], ['causa', 'clCausa'], ['zona', 'clZona']].forEach(function (p) { if (q.get(p[0])) $(p[1]).value = q.get(p[0]); });
  } catch (e) { /* sin parámetros */ }
  ley();
  $('clCausa').addEventListener('change', ley);

  function pinta(e) {
    if (e) e.preventDefault();
    var s = num('clSd'), per = $('clPer').value;
    var res = $('clRes'), tot = $('clTotal');
    res.hidden = false;
    var extra = [num('clDp'), num('clVt'), num('clVp'), num('clAg'), num('clPv')];
    if (!s || isNaN(s) || !$('clIng').value || !$('clSal').value || extra.some(function (v) { return typeof v === 'number' && isNaN(v); })) {
      tot.innerHTML = '<p class="ci-error">Escribe tus dos fechas y tu salario, con números.</p>';
      $('clPasos').innerHTML = ''; $('clNota').textContent = '';
      return;
    }
    var x = { ing: $('clIng').value, sal: $('clSal').value, sd: per === 'mes' ? s / 30 : s, mens: per === 'mes' ? s : 0, zona: $('clZona').value,
      agd: num('clAg') || 15, pv: num('clPv') || 25, vacPend: num('clVp') || 0, vacTom: num('clVt') || 0, dp: num('clDp') || 0,
      causa: $('clCausa').value, agPag: $('clAgPag').checked };
    var r = calcula(D, x);
    if (r.error) { tot.innerHTML = '<p class="ci-error">' + esc(r.error) + '</p>'; $('clPasos').innerHTML = ''; $('clNota').textContent = ''; return; }
    tot.innerHTML = '<p class="ci-cifra">Te toca: <b>' + p2(r.total) + '</b> antes de impuestos</p>' +
      '<p>Retención aproximada de ISR: <b>' + p2(r.isr) + '</b> · Lo que recibirías: <b>' + p2(r.neto) + '</b></p>' +
      '<p>Antigüedad: ' + r.anios.toFixed(2) + ' años (' + r.dias + ' días) · Salario integrado: ' + p2(r.sdi) + ' al día.</p>';
    var filas = r.conc.map(function (k) { return '<tr><th scope="row">' + esc(k[1]) + '</th><td>' + p2(k[2]) + '</td><td>' + esc(k[3]) + '</td></tr>'; });
    filas.push('<tr class="ci-fuerte"><th scope="row">Total antes de impuestos</th><td>' + p2(r.total) + '</td><td>Suma</td></tr>');
    filas.push('<tr><th scope="row">Exento de ISR (aguinaldo hasta 30 UMA, prima vacacional hasta 15 y separación hasta 90 por ' + r.anios_isr + ' año' + (r.anios_isr === 1 ? '' : 's') + ')</th><td>' + p2(r.exento) + '</td><td>LISR, art. 93, fr. XIII y XIV</td></tr>');
    filas.push('<tr><th scope="row">ISR del salario y las vacaciones, con la tarifa mensual</th><td>' + p2(r.isr_det[0]) + '</td><td>LISR, art. 96</td></tr>');
    if (r.isr_det[1] + r.isr_det[2] > 0) filas.push('<tr><th scope="row">ISR del aguinaldo y la prima vacacional que pasan de lo exento</th><td>' + p2(r.isr_det[1] + r.isr_det[2]) + '</td><td>RLISR, art. 174</td></tr>');
    if (r.isr_det[3] > 0) filas.push('<tr><th scope="row">ISR de la separación: lo gravado × ' + (r.tasa_m * 100).toFixed(2) + ' % (la tasa de tu sueldo mensual de ' + p2(r.m) + ')</th><td>' + p2(r.isr_det[3]) + '</td><td>LISR, arts. 95 y 96</td></tr>');
    filas.push('<tr class="ci-fuerte"><th scope="row">Lo que recibirías, aproximado</th><td>' + p2(r.neto) + '</td><td>Total − ISR</td></tr>');
    $('clPasos').innerHTML = filas.join('');
    var av = ['Es una cuenta aproximada (derivado): lo que vale es lo que firmen ante el Centro de Conciliación o resuelva el Tribunal.'];
    if (x.causa === 'injustificado' || x.causa === 'sin_reinstalar') av.unshift('No incluye los salarios vencidos ni sus intereses (LFT, art. 48): dependen de cuánto dure el juicio.');
    if (x.causa === 'renuncia' && r.anios < 15) av.unshift('Con menos de 15 años, quien se va por su voluntad no cobra prima de antigüedad (LFT, art. 162, fr. III).');
    $('clNota').textContent = av.join(' ');
  }
  $('clForm').addEventListener('submit', pinta);
  if (num('clSd')) pinta();
})();
