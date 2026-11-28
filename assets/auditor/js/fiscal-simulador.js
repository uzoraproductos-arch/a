/* Simulador y Blindaje Fiscal 2027 · Cero CIEC (Ola 3, Ronda 40).
   Todo se calcula en el navegador: nada de lo que el lector escribe se envía ni se guarda.
   Aquí no hay ninguna cifra fiscal: tasas, tarifas, topes y fechas llegan en #fsDatos, que
   herramientas/fiscal_simulador.py arma desde docs/fiscal-2027/. Las fórmulas son gemelas de
   las de ese módulo, y su prueba (--prueba, en revision.py) las compara caso por caso. */
(function (raiz) {
  'use strict';
  var CIEN = 100, MESES = 12;

  function r2(x) { return Math.round(x * CIEN) / CIEN; }

  function tarifa(K, base) {
    if (base <= 0) return 0;
    for (var i = 0; i < K.isr.length; i++) {
      var f = K.isr[i];
      if (f.sup === null || base <= f.sup) return r2(f.cuota + (base - f.inf) * f.tasa / CIEN);
    }
    return null;
  }

  function tasaResico(tabla, monto) {
    for (var i = 0; i < tabla.length; i++) if (monto <= tabla[i][0]) return tabla[i][1];
    return null;
  }

  function resico(K, anio, cobros, pm) {
    var R = K.resico[anio], ing = r2(cobros * MESES);
    var tm = tasaResico(R.men, cobros), ta = tasaResico(R.anu, ing);
    var ret = r2(cobros * pm / CIEN * K.retPm / CIEN);
    var isr = tm === null ? null : r2(cobros * tm / CIEN);
    return { tasa: tm, isr: isr, ret: ret, pagar: isr === null ? null : r2(Math.max(0, isr - ret)), ing: ing, tasaA: ta,
             isrA: ta === null ? null : r2(ing * ta / CIEN), tope: R.tope, dentro: ing <= R.tope };
  }

  function iva(K, cobros, gastos, pm) {
    var g = K.iva.gen, o = K.iva.op;
    var tras = r2(cobros * g / CIEN), acred = r2(gastos * g / CIEN);
    var general = r2(tras - acred), opcion = r2(cobros * o / CIEN), dif = r2(general - opcion);
    return { tras: tras, acred: acred, general: general, opcion: opcion, dif: dif, difA: r2(dif * MESES),
             prop: tras ? r2(acred / tras * CIEN) : 0, eq: K.iva.eq, conviene: dif > 0 ? 'opcion' : (dif < 0 ? 'general' : 'igual'),
             retPm: r2(cobros * pm / CIEN * g / CIEN * K.iva.ret[0] / K.iva.ret[1]) };
  }

  function anual(K, ingreso, retenido, generales, funerales, retiro, colegiaturas) {
    var d = K.ded, uma = K.uma;
    var tope = r2(Math.min(d.veces * uma, ingreso * d.pct / CIEN));
    var fun = r2(Math.min(funerales, d.funVeces * uma));
    var glob = r2(Math.min(generales + fun, tope));
    var ret = r2(Math.min(retiro, ingreso * d.retPct / CIEN, d.retVeces * uma));
    var suma = 0;
    colegiaturas.forEach(function (c) { suma += Math.min(c[1], K.col[c[0]]); });
    var col = r2(suma);
    var base = r2(Math.max(0, ingreso - glob - ret - col));
    var isr = tarifa(K, base);
    return { tope: tope, fun: fun, glob: glob, ret: ret, col: col, base: base, isr: isr, saldo: r2(isr - retenido) };
  }

  function obligado(K, ingreso, casos) { return ingreso > K.anualDesde || casos > 0; }

  function compara(K, perfil, sub, mensual, gastos) {
    var ing = r2(mensual * MESES), util = r2(Math.max(0, (mensual - gastos) * MESES));
    var out = { ing: ing, util: util, general: tarifa(K, util) };
    if (perfil === 'plataformas') {
      out.ret = r2(ing * K.plat[sub] / CIEN);
      out.definitivo = ing <= K.plat.definitivo;
      out.saldo = r2(out.general - out.ret);
      return out;
    }
    ['2026', '2027'].forEach(function (a) {
      var t = tasaResico(K.resico[a].anu, ing);
      out['resico' + a] = t === null ? null : r2(ing * t / CIEN);
    });
    if (perfil === 'arrendamiento') {
      out.baseCiega = r2(ing * (CIEN - K.ciega) / CIEN);
      out.ciega = tarifa(K, out.baseCiega);
    }
    return out;
  }

  var API = { r2: r2, tarifa: tarifa, tasaResico: tasaResico, resico: resico, iva: iva, anual: anual, obligado: obligado, compara: compara };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  raiz.FiscalSim = API;
  if (typeof document === 'undefined') return;

  /* ------------------------------------------------------------ la página */
  var NOMBRES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var AUD = '<span class="est-chip est-derivado">auditada</span>';
  var OFI = '<span class="est-chip est-oficial">oficial</span>';

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function num(id) {
    var el = $(id), v = el ? parseFloat(String(el.value).replace(/[^\d.\-]/g, '')) : NaN;
    return isFinite(v) && v > 0 ? v : 0;
  }
  function pesos(n) { return n.toLocaleString('es-MX', { style: 'currency', currency: 'MXN' }); }
  function pct(n) { return String(r2(n)) + ' %'; }
  function fecha(iso) { var p = iso.split('-'); return Number(p[2]) + ' de ' + NOMBRES[Number(p[1]) - 1] + ' de ' + p[0]; }
  function mosaico(etq, valor, nota, clase) {
    return '<div class="fsim-mos' + (clase ? ' ' + clase : '') + '"><span class="fsim-mos-etq">' + etq + '</span><b class="fsim-mos-val">' + valor + '</b>' +
      (nota ? '<span class="fsim-mos-nota">' + nota + '</span>' : '') + '</div>';
  }
  function tabla(titulo, cols, filas) {
    return '<div class="leg-tabla-caja"><table class="leg-tabla fis-tabla fsim-tabla"><caption>' + titulo + '</caption><thead><tr>' +
      cols.map(function (c) { return '<th scope="col">' + c + '</th>'; }).join('') + '</tr></thead><tbody>' +
      filas.map(function (f) { return '<tr><th scope="row">' + f[0] + '</th>' + f.slice(1).map(function (x) { return '<td>' + x + '</td>'; }).join('') + '</tr>'; }).join('') +
      '</tbody></table></div>';
  }
  function pinta(id, h) {
    var c = $(id);
    c.innerHTML = h ? '<h3 class="fsim-h3">Tu resultado ' + AUD + '</h3>' + h : '';
    if (h && c.scrollIntoView) c.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  function aviso(tx, clase) { return '<p class="fsim-aviso' + (clase ? ' ' + clase : '') + '">' + tx + '</p>'; }

  var K;
  try { K = JSON.parse($('fsDatos').textContent); } catch (e) { return; }

  /* ---- Módulo 1: el decisor del RESICO */
  function modulo1() {
    var c = num('fs1c'), g = num('fs1g'), pm = Math.min(CIEN, num('fs1p'));
    if (!c) return pinta('fsR1', aviso('Escribe lo que cobras al mes para hacer la cuenta.'));
    var v = iva(K, c, g, pm), a = resico(K, '2026', c, pm), b = resico(K, '2027', c, pm);
    var veredicto;
    if (v.conviene === 'opcion') veredicto = 'Con estos números, la opción de ' + pct(K.iva.op) + ' te haría pagar <b>' + pesos(v.dif) + ' menos de IVA al mes</b> (' + pesos(v.difA) + ' al año) que el régimen general.';
    else if (v.conviene === 'general') veredicto = 'Con estos números, la opción de ' + pct(K.iva.op) + ' te haría pagar <b>' + pesos(-v.dif) + ' más de IVA al mes</b> (' + pesos(-v.difA) + ' al año): te conviene más el régimen general, que sí acredita el IVA de tus gastos.';
    else veredicto = 'Con estos números, las dos formas de pagar el IVA dan lo mismo: estás justo en el punto de equilibrio.';
    var h = '<div class="fsim-mosaicos">' +
      mosaico('IVA en el régimen general, al mes', v.general < 0 ? pesos(-v.general) + ' a favor' : pesos(v.general), 'trasladas ' + pct(K.iva.gen) + ' y acreditas el de tus gastos') +
      mosaico('IVA con la opción de ' + pct(K.iva.op) + ', al mes', pesos(v.opcion), 'definitivo, sin acreditar nada') +
      mosaico('Diferencia al año', pesos(Math.abs(v.difA)), v.conviene === 'opcion' ? 'a tu favor con la opción' : (v.conviene === 'general' ? 'a tu favor con el régimen general' : 'sin diferencia'), v.conviene === 'general' ? 'fsim-mos-b' : 'fsim-mos-a') +
      mosaico('ISR del RESICO, al mes', a.isr === null ? 'Fuera de la tabla' : pesos(a.isr), a.isr === null ? 'pasas del último renglón de la tabla mensual' : 'tasa de ' + pct(a.tasa) + ' sobre lo cobrado') +
      '</div>';
    h += aviso(veredicto + ' La opción ' + esc(K.rige) + '.', 'fsim-veredicto');
    h += aviso('Tu IVA acreditable es el <b>' + pct(v.prop) + '</b> del que trasladas. El punto de equilibrio es <b>' + pct(v.eq) + '</b>: por debajo conviene la opción; por arriba, el régimen general.');
    h += tabla('El IVA del mes, paso a paso', ['Concepto', 'Monto'], [
      ['IVA que trasladas (' + pct(K.iva.gen) + ' de lo cobrado)', pesos(v.tras)],
      ['IVA acreditable de tus gastos', pesos(v.acred)],
      ['Régimen general: trasladado menos acreditable', pesos(v.general)],
      ['Opción: ' + pct(K.iva.op) + ' de lo cobrado', pesos(v.opcion)],
      ['Diferencia al mes (general menos opción)', pesos(v.dif)]]);
    if (pm) h += aviso('Por lo que le cobras a personas morales te retienen <b>' + pesos(v.retPm) + '</b> de IVA al mes en el régimen general (' + K.iva.ret[0] + '/' + K.iva.ret[1] +
      ' del IVA trasladado). Cómo convive esa retención con la opción sigue <b>pendiente</b> de la Resolución Miscelánea Fiscal de 2027: está en el fundamento, abajo.', 'fsim-pend');
    function fila(x) {
      return x.isr === null ? ['Fuera de la tabla', '—', '—', x.isrA === null ? 'Fuera de la tabla' : pesos(x.isrA)]
        : [pct(x.tasa), pesos(x.isr), pesos(x.pagar), x.isrA === null ? 'Fuera de la tabla' : pesos(x.isrA) + ' (' + pct(x.tasaA) + ')'];
    }
    h += tabla('Tu ISR del RESICO ' + OFI + ' las tasas', ['Año', 'Tasa del mes', 'ISR del mes', 'A pagar tras la retención', 'ISR del año'],
      [['2026'].concat(fila(a)), ['2027'].concat(fila(b))]);
    if (pm) h += aviso('Las personas morales te retienen el ' + pct(K.retPm) + ' de lo que te pagan: <b>' + pesos(a.ret) + '</b> al mes, que restas de tu pago mensual.');
    var tope;
    if (a.dentro) tope = 'Con ' + pesos(a.ing) + ' al año cabes en el tope del RESICO de 2026 (' + pesos(a.tope) + ') y en el de 2027 (' + pesos(b.tope) + ').';
    else if (b.dentro) tope = '<b>Atención:</b> con ' + pesos(a.ing) + ' al año rebasas el tope de 2026 (' + pesos(a.tope) + '). Sí cabes en el de ' + pesos(b.tope) + ', pero ese tope ' + esc(K.rige) + '.';
    else tope = '<b>Atención:</b> con ' + pesos(a.ing) + ' al año rebasas el tope del RESICO, tanto el de 2026 (' + pesos(a.tope) + ') como el de 2027 (' + pesos(b.tope) + '): quien lo rebasa sale del régimen.';
    h += aviso(tope + ' La ley mide el tope con los ingresos del ejercicio anterior y con los que llevas en el año.', a.dentro ? '' : 'fsim-alerta');
    pinta('fsR1', h);
  }

  /* ---- Módulo 2: la declaración anual de quien tiene sueldo */
  function colegiaturas() {
    var out = [];
    Array.prototype.forEach.call(document.querySelectorAll('.fsim-col'), function (f) {
      var n = f.querySelector('select').value, m = parseFloat(String(f.querySelector('input').value).replace(/[^\d.\-]/g, ''));
      if (n && isFinite(m) && m > 0) out.push([n, m]);
    });
    return out;
  }
  function filaCol() {
    var caja = $('fs2cols'), d = document.createElement('div');
    d.className = 'fsim-col';
    d.innerHTML = '<select class="fsim-inp" aria-label="Nivel educativo">' + caja.getAttribute('data-niveles') + '</select>' +
      '<input class="fsim-inp" type="text" inputmode="decimal" autocomplete="off" placeholder="$" aria-label="Colegiatura pagada en el año por ese alumno">' +
      '<button type="button" class="fsim-sec fsim-quita" aria-label="Quitar esta colegiatura">Quitar</button>';
    caja.appendChild(d);
  }
  function modulo2() {
    var i = num('fs2i'), ret = num('fs2r'), g = num('fs2g'), f = num('fs2f'), ap = num('fs2a'), cols = colegiaturas();
    if (!i) return pinta('fsR2', aviso('Escribe tu ingreso gravable del año para hacer la cuenta.'));
    var casos = document.querySelectorAll('[data-fs="caso"]:checked').length;
    var x = anual(K, i, ret, g, f, ap, cols), ob = obligado(K, i, casos);
    var motivo = i > K.anualDesde ? 'tus sueldos del año pasan de ' + pesos(K.anualDesde) : 'marcaste ' + (casos > 1 ? casos + ' de los casos' : 'uno de los casos') + ' que lista la ley';
    var h = aviso(ob ? '<b>Sí estás obligado a presentar la declaración anual:</b> ' + motivo + '.'
      : '<b>Con lo que marcaste no estás en ninguno de los casos que obligan:</b> tus sueldos no pasan de ' + pesos(K.anualDesde) + ' y no marcaste ningún otro. Uno de los casos de la ley es avisar por escrito a tu patrón que la presentarás.', 'fsim-veredicto');
    h += '<div class="fsim-mosaicos">' +
      mosaico('Base gravable', pesos(x.base), 'tu ingreso menos tus deducciones') +
      mosaico('ISR del año', pesos(x.isr), 'tarifa anual sobre esa base') +
      mosaico('ISR que te retuvieron', pesos(ret), 'lo que tú escribiste') +
      mosaico(x.saldo < 0 ? 'Saldo a favor' : (x.saldo > 0 ? 'Saldo a cargo' : 'Sin diferencia'), pesos(Math.abs(x.saldo)), x.saldo < 0 ? 'te retuvieron de más' : (x.saldo > 0 ? 'te falta por pagar' : 'lo retenido es igual al impuesto'), x.saldo > 0 ? 'fsim-mos-b' : 'fsim-mos-a') +
      '</div>';
    var pedidas = r2(g + x.fun);
    h += tabla('Tus deducciones, paso a paso', ['Concepto', 'Lo que escribiste', 'Lo que se deduce'], [
      ['Deducciones que entran al tope global (con los gastos funerarios)', pesos(pedidas), pesos(x.glob)],
      ['Tope global: lo menor entre ' + K.ded.veces + ' veces la UMA anual y el ' + pct(K.ded.pct) + ' de tu ingreso', '—', pesos(x.tope)],
      ['Aportaciones complementarias de retiro (aparte del tope)', pesos(ap), pesos(x.ret)],
      ['Colegiaturas (aparte del tope, con el límite de cada nivel)', pesos(cols.reduce(function (s, c) { return s + c[1]; }, 0)), pesos(x.col)],
      ['Base gravable: tu ingreso menos lo que se deduce', pesos(i), pesos(x.base)]]);
    if (pedidas > x.glob) h += aviso('De tus deducciones generales quedan fuera <b>' + pesos(r2(pedidas - x.glob)) + '</b> por el tope global.');
    if (f > x.fun) h += aviso('De tus gastos funerarios solo cuentan <b>' + pesos(x.fun) + '</b>: su límite es ' + K.ded.funVeces + ' vez la UMA anual.');
    if (ap > x.ret) h += aviso('De tus aportaciones de retiro solo se deducen <b>' + pesos(x.ret) + '</b>: su límite es el ' + pct(K.ded.retPct) + ' de tu ingreso, sin pasar de ' + K.ded.retVeces + ' veces la UMA anual.');
    h += aviso('Se usa la tarifa anual de 2026. Las tarifas de 2027 siguen <b>pendientes</b>: no se usa ninguna hasta que se publiquen.', 'fsim-pend');
    pinta('fsR2', h);
  }

  /* ---- Módulo 3: el comparador de regímenes */
  function modulo3() {
    var p = $('fs3p').value, s = $('fs3s').value, m = num('fs3m'), g = num('fs3g'), excl = $('fs3x').checked;
    if (!m) return pinta('fsR3', aviso('Escribe lo que cobras al mes para comparar.'));
    var x = compara(K, p, s, m, g), filas = [], opciones = [];
    function reg(nombre, isr, nota) {
      filas.push([nombre, isr === null ? '—' : pesos(isr), isr === null ? '—' : pesos(r2(isr / MESES)), nota]);
      if (isr !== null) opciones.push([nombre, isr]);
    }
    if (p === 'plataformas') {
      reg('La retención como pago definitivo', x.definitivo ? x.ret : null, x.definitivo
        ? 'Te retienen el ' + pct(K.plat[s]) + ' y ahí termina tu ISR; no deduces gastos. La ley mide el límite de ' + pesos(K.plat.definitivo) + ' con los ingresos del año anterior.'
        : 'No disponible: con ' + pesos(x.ing) + ' al año pasas del límite de ' + pesos(K.plat.definitivo) + '.');
      reg('Régimen general: tarifa anual sobre tu utilidad', x.general, 'Utilidad de ' + pesos(x.util) + '. Las retenciones del año (' + pesos(x.ret) + ') se acreditan: quedaría ' +
        (x.saldo < 0 ? pesos(-x.saldo) + ' a favor.' : pesos(x.saldo) + ' a cargo.'));
    } else {
      var notaR = excl ? 'No puedes: marcaste que estás en un supuesto que la ley excluye del RESICO.' : 'Tasa sobre todo lo cobrado, sin deducciones.';
      if (x.resico2026 === null && x.resico2027 !== null) {
        reg('RESICO (solo con el tope de 2027)', excl ? null : x.resico2027, excl ? notaR : 'Con ' + pesos(x.ing) + ' al año rebasas el tope de 2026; el tope nuevo ' + esc(K.rige) + '.');
      } else {
        reg('RESICO', excl ? null : x.resico2026, x.resico2026 === null ? 'Fuera del régimen: tus ingresos del año rebasan su tope.' : notaR);
      }
      if (p === 'arrendamiento') {
        reg('Arrendamiento con la deducción opcional del ' + pct(K.ciega), x.ciega, 'Sin comprobantes: base de ' + pesos(x.baseCiega) + '.');
        reg('Arrendamiento con tus gastos reales', x.general, 'Tarifa anual sobre ' + pesos(x.util) + '.');
      } else {
        reg('Actividad empresarial o servicios profesionales', x.general, 'Tarifa anual sobre tu utilidad fiscal de ' + pesos(x.util) + '.');
      }
    }
    opciones.sort(function (a, b) { return a[1] - b[1]; });
    var h = '';
    if (opciones.length) {
      h += aviso('Con estos números, el menor ISR del año es el de <b>' + esc(opciones[0][0]) + '</b>: ' + pesos(opciones[0][1]) +
        (opciones.length > 1 ? ', ' + pesos(r2(opciones[opciones.length - 1][1] - opciones[0][1])) + ' menos que la opción más cara.' : '.'), 'fsim-veredicto');
    }
    h += tabla('El ISR de un año con ' + pesos(x.ing) + ' de ingresos', ['Régimen', 'ISR del año', 'Al mes, en promedio', 'Cómo se calcula'], filas);
    if (p === 'plataformas') h += aviso('Si quien cobra por plataformas puede tributar en el RESICO por esos ingresos sigue <b>pendiente</b> de cotejo en la base: por eso aquí no se compara.', 'fsim-pend');
    h += aviso('Las tasas, las tarifas y los topes son ' + OFI + '; cada monto de esta tabla es una estimación aritmética del simulador ' + AUD + ', no tu impuesto definitivo.');
    pinta('fsR3', h);
  }

  /* ---- Módulo 4: la lista de blindaje (solo en este navegador) y el próximo vencimiento */
  function leeLista() {
    try { var v = JSON.parse(localStorage.getItem(K.llave) || '[]'); return Array.isArray(v) ? v : []; } catch (e) { return []; }
  }
  function blindaje() {
    var puntos = document.querySelectorAll('[data-fs-punto]'), marcados = leeLista();
    if (!puntos.length) return;
    function avance() {
      var n = document.querySelectorAll('[data-fs-punto]:checked').length;
      $('fsAvance').textContent = n + ' de ' + puntos.length + ' puntos resueltos';
    }
    Array.prototype.forEach.call(puntos, function (p) {
      p.checked = marcados.indexOf(p.getAttribute('data-fs-punto')) >= 0;
      p.addEventListener('change', function () {
        var ids = Array.prototype.filter.call(puntos, function (q) { return q.checked; }).map(function (q) { return q.getAttribute('data-fs-punto'); });
        try { localStorage.setItem(K.llave, JSON.stringify(ids)); } catch (e) { /* sin almacenamiento: la lista vive mientras la página esté abierta */ }
        avance();
      });
    });
    $('fsBorra').addEventListener('click', function () {
      try { localStorage.removeItem(K.llave); } catch (e) { /* nada que borrar */ }
      Array.prototype.forEach.call(puntos, function (p) { p.checked = false; });
      avance();
    });
    avance();
    var d = new Date(), hoy = d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
    var sig = K.cal.filter(function (f) { return f[1] >= hoy; })[0];
    if (sig) $('fsProx').innerHTML = 'El próximo pago mensual vence el <b>' + fecha(sig[1]) + '</b>. ' + AUD;
  }

  function formulario(id, res, calcula) {
    var f = $(id);
    if (!f) return;
    f.addEventListener('submit', function (e) { e.preventDefault(); calcula(); });
    f.addEventListener('reset', function () { pinta(res, ''); });
    var ej = f.querySelector('[data-fs-ej]');
    if (ej) ej.addEventListener('click', function () {
      var v = JSON.parse(ej.getAttribute('data-fs-ej'));
      Object.keys(v).forEach(function (k) { if ($(k)) $(k).value = v[k]; });
      calcula();
    });
  }
  formulario('fsF1', 'fsR1', modulo1);
  formulario('fsF2', 'fsR2', modulo2);
  formulario('fsF3', 'fsR3', modulo3);
  if ($('fs2cols')) {
    filaCol();
    $('fs2mas').addEventListener('click', filaCol);
    $('fs2cols').addEventListener('click', function (e) { var b = e.target.closest('.fsim-quita'); if (b) b.parentNode.remove(); });
  }
  if ($('fs3p')) {
    var perfil = function () { $('fs3sCaja').hidden = $('fs3p').value !== 'plataformas'; };
    $('fs3p').addEventListener('change', perfil);
    perfil();
  }
  blindaje();
})(typeof window !== 'undefined' ? window : this);
