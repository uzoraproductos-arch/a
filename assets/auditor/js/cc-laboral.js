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
    var B = (x.reg || 'A') === 'B';
    var agd = +x.agd || (B ? 40 : 15), pv = +x.pv || (B ? 30 : 25);
    var vacAnio = B ? 20 : vacTabla(comp + 1);
    var sdi = sd * (1 + (agd + vacAnio * pv / 100) / 365);
    var c = [], r = { dias: dias, anios: anios, sdi: sdi, vac_anio: vacAnio, conc: c, reg: B ? 'B' : 'A' };
    var dp = +x.dp || 0;
    if (dp > 0) c.push(['salario', 'Días de salario que no te han pagado (' + dp + ' × salario diario)', dp * sd, B ? 'LFTSE, arts. 32 y 43' : 'LFT, art. 88']);
    if (!B) {
      var vprop = Math.max(0, vacAnio * dcur / 365 - (+x.vacTom || 0));
      var vdias = vprop + (+x.vacPend || 0), vac = vdias * sd;
      if (vac > 0) {
        c.push(['vacaciones', 'Vacaciones: ' + vdias.toFixed(2) + ' días (proporcionales del año en curso y pendientes)', vac, 'LFT, arts. 76 y 79']);
        c.push(['prima_vac', 'Prima vacacional (' + pv + ' % de tus vacaciones)', vac * pv / 100, 'LFT, art. 80']);
      }
    }
    if (!x.agPag) {
      var y = Number(String(x.sal).slice(0, 4)), ini = Math.max(ing, Date.UTC(y, 0, 1));
      var dag = Math.round((sal - ini) / DIA) + 1;
      c.push(['aguinaldo', 'Aguinaldo proporcional (' + agd + ' días × ' + dag + ' días trabajados este año ÷ 365)', agd * dag / 365 * sd, B ? 'LFTSE, art. 42 Bis' : 'LFT, art. 87']);
    }
    var z = x.zona || 'gen', tope = 2 * D.sm[z], piso = D.sm[z], causa = x.causa;
    if (!B && (causa === 'justificado' || causa === 'injustificado' || causa === 'sin_reinstalar' || (causa === 'renuncia' && anios >= 15))) {
      var bpa = Math.min(Math.max(sdi, piso), tope);
      c.push(['prima_ant', 'Prima de antigüedad: 12 días × ' + anios.toFixed(2) + ' años × ' + p2(bpa) + ' de salario (entre uno y dos salarios mínimos)',
        12 * anios * bpa, 'LFT, arts. 162, 485 y 486']);
    }
    if (!B && (causa === 'injustificado' || causa === 'sin_reinstalar')) c.push(['ind3', 'Indemnización: tres meses (90 días) de salario integrado', 90 * sdi, 'LFT, arts. 48, 50 (fr. III) y 89']);
    if (!B && causa === 'sin_reinstalar') c.push(['ind20', 'Veinte días de salario integrado por cada año de servicios (' + anios.toFixed(2) + ' años)', 20 * anios * sdi, 'LFT, arts. 49 y 50, fr. II']);
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
    var sub = 0;
    if (m <= D.sub.tope) sub = Math.min(D.umam * D.sub.pct / 100, retOrd + retAg + retPv);
    var isr = retSep + retAg + retPv + retOrd - sub;
    r.total = tot; r.exento = exSep + exAg + exPv; r.isr = isr; r.neto = tot - isr; r.m = m; r.tasa_m = tasaM; r.sub = sub;
    r.isr_det = [retOrd, retAg, retPv, retSep]; r.ex_det = [exAg, exPv, exSep]; r.anios_isr = aniosIsr;
    /* Escenario de juicio (LFT, art. 48): fuera del total. */
    var mj = Math.floor(+x.mj || 0);
    r.juicio = [];
    if (B && mj > 0 && (causa === 'injustificado' || causa === 'sin_reinstalar'))
      r.juicio.push(['caidos', 'Salarios caídos: ' + mj + ' meses × 30 días × tu salario, sin tope (corren hasta que se cumpla el laudo)', mj * 30 * sd, 'LFTSE, art. 43, fr. III y IV; SCJN, 2a./J. 34/2017']);
    if (!B && mj > 0 && (causa === 'injustificado' || causa === 'sin_reinstalar')) {
      r.juicio.push(['vencidos', 'Salarios vencidos: ' + Math.min(mj, 12) + ' meses × 30 días × salario integrado (hasta 12 meses)', Math.min(mj, 12) * 30 * sdi, 'LFT, art. 48, segundo párrafo']);
      if (mj > 12) r.juicio.push(['intereses', 'Intereses: 2 % mensual sobre quince meses de salario, por ' + (mj - 12) + ' meses después del mes 12',
        15 * 30 * sdi * 0.02 * (mj - 12), 'LFT, art. 48, tercer párrafo']);
    }
    r.total_juicio = tot;
    var v = 0;
    r.juicio.forEach(function (k) { r.total_juicio += k[2]; if (k[0] === 'vencidos' || k[0] === 'caidos') v += k[2]; });
    /* ISR de los vencidos o caídos: prestación por la terminación (SCJN, 2a. XXVIII/2017), mecánica del art. 95, sin exención. */
    r.isr_juicio = v > 0 ? (v < m ? isrTarifa(D, v) : v * tasaM) : 0;
    r.neto_juicio = r.total_juicio - isr - r.isr_juicio;
    /* Reparto de utilidades (LFT, arts. 123, 124 y 127, fr. VIII): aparte. */
    r.ptu = null;
    var pu = +x.ptuU || 0, pdt = +x.ptuDT || 0, pst = +x.ptuST || 0, pd = +x.ptuD || 0;
    if (!B && pu > 0 && pdt > 0 && pst > 0 && pd > 0) {
      var ps = (+x.ptuS || 0) || sd * pd;
      var pD = pu / 2 * pd / pdt, pS = pu / 2 * ps / pst, bruto = pD + pS;
      var topeP = Math.max(90 * sd, +x.ptuP || 0), ptu = Math.min(bruto, topeP);
      var exP = Math.min(ptu, 15 * U), retP = art174(ptu - exP);
      r.ptu = { dias: pD, sal: pS, bruto: bruto, tope: topeP, ptu: ptu, ex: exP, isr: retP, neto: ptu - retP };
    }
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
    if ($('clReg') && $('clReg').value === 'B') {
      $('clCausaLey').textContent = k === 'renuncia' ? 'LFTSE, art. 46, fr. I: la renuncia termina el nombramiento.' :
        'LFTSE, art. 46: nadie puede ser cesado sino por justa causa; si el Tribunal declara injustificado el cese, reinstalación o indemnización y salarios caídos (art. 43, fr. III y IV).';
      return;
    }
    D.causas.forEach(function (c) { if (c[0] === k) $('clCausaLey').textContent = c[2]; });
  }

  /* Lo que llega por la dirección (?s=&p=&ing=&sal=&causa=), para que el chat abra la cuenta ya puesta. */
  try {
    var q = new URLSearchParams(location.search);
    [['s', 'clSd'], ['p', 'clPer'], ['mj', 'clMj'], ['ing', 'clIng'], ['sal', 'clSal'], ['causa', 'clCausa'], ['zona', 'clZona']].forEach(function (p) { if (q.get(p[0])) $(p[1]).value = q.get(p[0]); });
  } catch (e) { /* sin parámetros */ }
  /* Apartado A o B: cambia los mínimos de la ley y apaga lo que solo es del A. */
  var REG = { A: ['15', '25', 'Ley Federal del Trabajo: aguinaldo de 15 días y prima vacacional de 25 % por lo menos (arts. 80 y 87).'],
              B: ['40', '30', 'Ley Federal de los Trabajadores al Servicio del Estado: aguinaldo de 40 días (art. 42 Bis); la indemnización la fija el laudo (art. 43).'] };
  function reg(cambio) {
    var k = $('clReg').value, o = k === 'A' ? 'B' : 'A';
    if (cambio) {
      if ($('clAg').value === REG[o][0] || !$('clAg').value) $('clAg').value = REG[k][0];
      if ($('clPv').value === REG[o][1] || !$('clPv').value) $('clPv').value = REG[k][1];
    }
    $('clRegLey').textContent = REG[k][2];
    $('clPtuCaja').hidden = k === 'B';
  }
  try { var qr = new URLSearchParams(location.search).get('reg'); if (qr === 'B' || qr === 'A') $('clReg').value = qr; } catch (e) { /* sin parámetros */ }
  reg(true);
  ley();
  $('clCausa').addEventListener('change', ley);
  $('clReg').addEventListener('change', function () { reg(true); ley(); });

  function pinta(e) {
    if (e) e.preventDefault();
    var s = num('clSd'), per = $('clPer').value;
    var res = $('clRes'), tot = $('clTotal');
    res.hidden = false;
    var extra = [num('clDp'), num('clVt'), num('clVp'), num('clAg'), num('clPv'), num('clMj'), num('clPtuU'), num('clPtuD'), num('clPtuDT'), num('clPtuST'), num('clPtuS'), num('clPtuP')];
    if (!s || isNaN(s) || !$('clIng').value || !$('clSal').value || extra.some(function (v) { return typeof v === 'number' && isNaN(v); })) {
      tot.innerHTML = '<p class="ci-error">Escribe tus dos fechas y tu salario, con números.</p>';
      $('clPasos').innerHTML = ''; $('clNota').textContent = ''; $('clExtra').innerHTML = '';
      return;
    }
    var x = { ing: $('clIng').value, sal: $('clSal').value, sd: per === 'mes' ? s / 30 : s, mens: per === 'mes' ? s : 0, zona: $('clZona').value,
      agd: num('clAg') || ($('clReg').value === 'B' ? 40 : 15), pv: num('clPv') || ($('clReg').value === 'B' ? 30 : 25), vacPend: num('clVp') || 0, vacTom: num('clVt') || 0, dp: num('clDp') || 0,
      causa: $('clCausa').value, agPag: $('clAgPag').checked, reg: $('clReg').value, mj: num('clMj') || 0,
      ptuU: num('clPtuU') || 0, ptuD: num('clPtuD') || 0, ptuDT: num('clPtuDT') || 0, ptuST: num('clPtuST') || 0, ptuS: num('clPtuS') || 0, ptuP: num('clPtuP') || 0 };
    var r = calcula(D, x);
    if (r.error) { tot.innerHTML = '<p class="ci-error">' + esc(r.error) + '</p>'; $('clPasos').innerHTML = ''; $('clNota').textContent = ''; $('clExtra').innerHTML = ''; return; }
    tot.innerHTML = '<p class="ci-cifra">Te toca: <b>' + p2(r.total) + '</b> antes de impuestos</p>' +
      '<p>Retención aproximada de ISR: <b>' + p2(r.isr) + '</b> · Lo que recibirías: <b>' + p2(r.neto) + '</b></p>' +
      '<p>Antigüedad: ' + r.anios.toFixed(2) + ' años (' + r.dias + ' días)' + (r.reg === 'A' ? ' · Salario integrado: ' + p2(r.sdi) + ' al día.' : ' · Apartado B.') + '</p>';
    var filas = r.conc.map(function (k) { return '<tr><th scope="row">' + esc(k[1]) + '</th><td>' + p2(k[2]) + '</td><td>' + esc(k[3]) + '</td></tr>'; });
    filas.push('<tr class="ci-fuerte"><th scope="row">Total antes de impuestos</th><td>' + p2(r.total) + '</td><td>Suma</td></tr>');
    filas.push('<tr><th scope="row">Exento de ISR (aguinaldo hasta 30 UMA, prima vacacional hasta 15 y separación hasta 90 por ' + r.anios_isr + ' año' + (r.anios_isr === 1 ? '' : 's') + ')</th><td>' + p2(r.exento) + '</td><td>LISR, art. 93, fr. XIII y XIV</td></tr>');
    filas.push('<tr><th scope="row">ISR del salario y las vacaciones, con la tarifa mensual</th><td>' + p2(r.isr_det[0]) + '</td><td>LISR, art. 96</td></tr>');
    if (r.isr_det[1] + r.isr_det[2] > 0) filas.push('<tr><th scope="row">ISR del aguinaldo y la prima vacacional que pasan de lo exento</th><td>' + p2(r.isr_det[1] + r.isr_det[2]) + '</td><td>RLISR, art. 174</td></tr>');
    if (r.isr_det[3] > 0) filas.push('<tr><th scope="row">ISR de la separación: lo gravado × ' + (r.tasa_m * 100).toFixed(2) + ' % (la tasa de tu sueldo mensual de ' + p2(r.m) + ')</th><td>' + p2(r.isr_det[3]) + '</td><td>LISR, arts. 95 y 96</td></tr>');
    if (r.sub > 0) filas.push('<tr><th scope="row">Menos el subsidio para el empleo (' + D.sub.pct + ' % de la UMA mensual; tu sueldo no pasa de ' + p2(D.sub.tope) + ')</th><td>−' + p2(r.sub) + '</td><td>Decreto DOF 31-12-2025</td></tr>');
    filas.push('<tr class="ci-fuerte"><th scope="row">Lo que recibirías, aproximado</th><td>' + p2(r.neto) + '</td><td>Total − ISR</td></tr>');
    $('clPasos').innerHTML = filas.join('');
    var ex = '';
    function tabla(cap, rows) {
      return '<div class="ci-tabla-caja"><table class="ci-tabla"><caption>' + cap + '</caption><thead><tr><th scope="col">Concepto</th><th scope="col">Pesos</th><th scope="col">Regla</th></tr></thead><tbody>' +
        rows.map(function (k) { return '<tr' + (k[4] ? ' class="ci-fuerte"' : '') + '><th scope="row">' + esc(k[1]) + '</th><td>' + p2(k[2]) + '</td><td>' + esc(k[3]) + '</td></tr>'; }).join('') + '</tbody></table></div>';
    }
    if (r.juicio.length) {
      var j = r.juicio.slice();
      j.push(['', (r.reg === 'B' ? 'Lo del finiquito más los salarios caídos' : 'Tu liquidación más lo del juicio') + ', antes de impuestos', r.total_juicio, 'Suma', 1]);
      j.push(['', 'ISR de los salarios ' + (r.reg === 'B' ? 'caídos' : 'vencidos') + ': como lo de la separación, con la tasa de tu sueldo mensual y sin exención', r.isr_juicio, 'LISR, art. 95; SCJN, 2a. XXVIII/2017']);
      j.push(['', 'Lo que recibirías con el juicio, aproximado (menos todo el ISR)', r.neto_juicio, 'Suma − ISR', 1]);
      ex += '<h3 class="ci-tit">⚖️ Si el juicio dura ' + x.mj + ' meses (escenario)</h3>' + tabla('Lo que sumaría el juicio, si ' + (r.reg === 'B' ? 'el Tribunal declara injustificado el cese' : 'el patrón no prueba la causa'), j) +
        '<p class="ci-nota">Es un escenario: lo que vale es lo que resuelva el Tribunal. ' + (r.reg === 'B' ? 'En el apartado B no hay tope de doce meses ni interés del 2 % (SCJN, 2a./J. 34/2017).' : 'El ISR de los intereses no lo calculamos.') +
        ' Hay criterios encontrados sobre si a estos salarios les toca la exención de la separación: la cuenta no se la aplica.</p>';
    } else if (x.mj > 0) {
      ex += '<p class="ci-nota">Los salarios ' + (r.reg === 'B' ? 'caídos' : 'vencidos') + ' solo se pagan si te despidieron y en el juicio se demuestra que fue sin causa (' + (r.reg === 'B' ? 'LFTSE, art. 43, fr. III' : 'LFT, art. 48') + '): elige esa causa para verlos.</p>';
    }
    if (r.ptu) {
      var t = r.ptu;
      ex += '<h3 class="ci-tit">🤝 Tu reparto de utilidades (se paga aparte)</h3>' + tabla('Cómo se llega a tu parte', [
        ['', 'Mitad por días trabajados: utilidad ÷ 2 × tus días ÷ los días de todos', t.dias, 'LFT, art. 123'],
        ['', 'Mitad por salarios: utilidad ÷ 2 × tus salarios ÷ los salarios de todos', t.sal, 'LFT, arts. 123 y 124'],
        ['', 'Tope: tres meses de tu salario (90 días) o el promedio de tus últimos tres años, lo que te convenga más', t.tope, 'LFT, art. 127, fr. VIII'],
        ['', 'Tu reparto', t.ptu, t.bruto > t.tope ? 'Topado' : 'Sin tope', 1],
        ['', 'Exento de ISR (hasta 15 UMA)', t.ex, 'LISR, art. 93, fr. XIV'],
        ['', 'Retención aproximada de ISR', t.isr, 'RLISR, art. 174'],
        ['', 'Lo que recibirías del reparto, aproximado', t.neto, 'Reparto − ISR', 1]]);
    }
    $('clExtra').innerHTML = ex;
    var av = ['Es una cuenta aproximada (derivado): lo que vale es lo que firmen ante el Centro de Conciliación o resuelva el Tribunal.'];
    if (r.reg === 'B') av.unshift('En el apartado B la indemnización y la prima vacacional que se deba los fija el laudo (LFTSE, art. 43, fr. III y IV); aquí va lo que la ley ya da: el salario pendiente, el aguinaldo de ' + x.agd + ' días en proporción y, si escribes cuánto dura el juicio, los salarios caídos.');
    if (!r.juicio.length && (x.causa === 'injustificado' || x.causa === 'sin_reinstalar')) av.unshift(r.reg === 'B' ? 'Sin los salarios caídos (LFTSE, art. 43): dependen de cuánto dure el juicio; escribe un escenario en el paso 3.' : 'Sin los salarios vencidos ni sus intereses (LFT, art. 48): dependen de cuánto dure el juicio; escribe un escenario en el paso 3.');
    if (r.reg === 'A' && x.causa === 'renuncia' && r.anios < 15) av.unshift('Con menos de 15 años, quien se va por su voluntad no cobra prima de antigüedad (LFT, art. 162, fr. III).');
    $('clNota').textContent = av.join(' ');
  }
  $('clForm').addEventListener('submit', pinta);
  if (num('clSd')) pinta();
})();
