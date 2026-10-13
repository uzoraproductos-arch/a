/* Auditavisión · Calculadora Cívica › Tú contra ellos (aplicación 2,
   12-10-2026). La página la escribe herramientas/cc_compara.py con las
   tarjetas de cada cargo ya pintadas y, en JSON (#cvDatos), las cifras
   anuales y mensuales de esas tarjetas, la regla de la Ley Federal del
   Trabajo y los parámetros oficiales con que el bloque 1 del motor saca el
   neto de quien trabaja en nómina (tarifa del art. 96 de la LISR, subsidio
   para el empleo y cuotas obreras del IMSS).
   Aquí no se escribe ninguna cifra oficial: solo se divide entre el
   ingreso del lector, y todo lo que sale de esa división se marca
   «derivado». Prefijo de clases e ids: cv-. */
(function () {
  'use strict';

  var D;
  try { D = JSON.parse(document.getElementById('cvDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  var raiz = $('cvRaiz');
  if (!raiz) return;

  /* La misma clave puede leerla «Tu estado de cuenta»: guarda lo que el
     lector escribió, no lo que se calculó. */
  var CLAVE = 'auditavision_cc_sueldo';
  var porId = {};
  D.cargos.forEach(function (c) { porId[c.id] = c; });
  var est = { monto: 0, periodo: 'mes', tipo: 'bruto', grupo: 'todos', sel: 'presidencia' };

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function pesos(v) { return '$' + Math.round(v).toLocaleString('es-MX'); }
  function num(v, d) { return Number(v).toLocaleString('es-MX', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function chip(e, pend) {
    return '<span class="est-chip est-' + e + '"' + (pend ? ' data-pend="' + esc(pend) + '"' : '') + '>' + e + '</span>';
  }
  function leerNumero(t) {
    var n = parseFloat(String(t == null ? '' : t).replace(/[^0-9.\-]/g, ''));
    return isFinite(n) && n > 0 ? n : 0;
  }

  /* ---------- El neto de quien está en nómina (como ccDesdeBruto) ---------- */
  var I = D.isr;
  function tarifa(base) {
    if (!(base > 0)) return 0;
    var R = I.renglones;
    for (var i = 0; i < R.length; i++) {
      var r = R[i];
      if (r.ls === null || base <= r.ls) return Math.max(0, r.cf + (base - r.li) * r.pct / 100);
    }
    return 0;
  }
  function cuotas(sbc) {
    var tope = I.tope_uma * I.uma_diaria * 30, tres = 3 * I.uma_diaria * 30;
    var b = Math.min(Math.max(0, sbc), tope);
    return I.ramos.reduce(function (a, r) {
      return a + (r.base === 'excedente_3_uma' ? Math.max(0, b - tres) : b) * r.pct / 100;
    }, 0);
  }
  function desdeBruto(b) {
    var t = tarifa(b);
    var sub = (b > 0 && b <= I.sub_tope) ? Math.min(I.uma_mensual * I.sub_pct / 100, t) : 0;
    var r = { bruto: b, isr: Math.max(0, t - sub), cuotas: cuotas(b), exento: false };
    if (b > 0 && b <= D.sm.general + 0.005) { r.isr = 0; r.cuotas = 0; r.exento = true; }
    r.neto = b - r.isr - r.cuotas;
    return r;
  }
  function desdeNeto(n) {
    var lo = n, hi = n * 3 + 100000;
    for (var i = 0; i < 90; i++) {
      var m = (lo + hi) / 2;
      if (desdeBruto(m).neto < n) lo = m; else hi = m;
    }
    return desdeBruto((lo + hi) / 2);
  }

  function lector() {
    var ejemplo = !(est.monto > 0);
    var mes = ejemplo ? D.sm.general : (est.periodo === 'ano' ? est.monto / 12 : est.monto);
    var tipo = ejemplo ? 'bruto' : est.tipo;
    var r = tipo === 'neto' ? desdeNeto(mes) : desdeBruto(mes);
    return { ejemplo: ejemplo, tipo: tipo, mesNeto: r.neto, anual: r.neto * 12, brutoMes: r.bruto, r: r };
  }

  /* ---------- Guardar y leer el sueldo (solo en este navegador) ---------- */
  function guardar() {
    try {
      if (est.monto > 0) localStorage.setItem(CLAVE, JSON.stringify({ monto: est.monto, periodo: est.periodo, tipo: est.tipo }));
      else localStorage.removeItem(CLAVE);
    } catch (e) { /* sin almacenamiento: no se recuerda */ }
  }
  function cargar() {
    try {
      var g = JSON.parse(localStorage.getItem(CLAVE) || 'null');
      if (g && g.monto > 0) {
        est.monto = Number(g.monto);
        est.periodo = g.periodo === 'ano' ? 'ano' : 'mes';
        est.tipo = g.tipo === 'neto' ? 'neto' : 'bruto';
      }
    } catch (e) { /* nada guardado */ }
  }

  /* ---------- Paso 1 ---------- */
  var monto = $('cvMonto');
  function pintarMandos() {
    [].forEach.call(raiz.querySelectorAll('[data-periodo]'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.periodo === est.periodo)); });
    [].forEach.call(raiz.querySelectorAll('[data-tipo]'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.tipo === est.tipo)); });
  }
  function pintarLector(L) {
    var h;
    if (L.ejemplo) {
      h = '<p class="cv-l-t">Referencia mientras no escribas tu ingreso</p>' +
        '<p class="cv-l-v"><b>' + pesos(L.mesNeto) + '</b> al mes <small>el salario mínimo general 2026</small> ' + chip('oficial') + '</p>' +
        '<p class="cv-l-op">Es un ejemplo oficial, no tu sueldo. El salario mínimo no paga ISR (art. 96 de la LISR, último párrafo) ni cuota obrera del IMSS (art. 36 de la LSS): su neto es igual a su bruto.</p>';
    } else if (L.tipo === 'neto') {
      h = '<p class="cv-l-t">Tu ingreso neto</p>' +
        '<p class="cv-l-v"><b>' + pesos(L.mesNeto) + '</b> al mes · <b>' + pesos(L.anual) + '</b> al año</p>' +
        '<p class="cv-l-op">Lo escribiste neto: así se compara, neto contra neto. Para la cuenta de prestaciones estimamos tu bruto como asalariado: ' +
        pesos(L.brutoMes) + ' al mes ' + chip('derivado') + ' (el bruto cuyo neto, con la tarifa del ISR y las cuotas del IMSS, da el que escribiste).</p>';
    } else {
      var r = L.r;
      h = '<p class="cv-l-t">Tu ingreso neto, calculado</p>' +
        '<p class="cv-l-v"><b>' + pesos(L.mesNeto) + '</b> al mes · <b>' + pesos(L.anual) + '</b> al año ' + chip('derivado') + '</p>' +
        '<div class="cv-l-cuenta"><span>Bruto <b>' + pesos(r.bruto) + '</b></span><span>− ISR <b>' + pesos(r.isr) + '</b></span>' +
        '<span>− IMSS <b>' + pesos(r.cuotas) + '</b></span><span>= Neto <b>' + pesos(r.neto) + '</b></span></div>' +
        '<p class="cv-l-op">' + (r.exento
          ? 'Ganas un salario mínimo o menos: la ley no te retiene ISR (art. 96 de la LISR) y el patrón cubre tu cuota del IMSS (art. 36 de la LSS).'
          : 'Como asalariado: tarifa mensual del ISR menos el subsidio para el empleo, y cuotas obreras del IMSS, al mes. ¿Otro régimen? Escribe tu neto o saca la cuenta en <a href="herramienta-calculadora-ticket.html">Tu estado de cuenta</a>.') + '</p>';
    }
    $('cvLector').innerHTML = h;
  }

  /* ---------- Cuentas con un cargo ---------- */
  function cuentas(c, L) {
    var mesMax = c.mensual.max;
    return {
      veces: c.anual / L.anual,
      meses: mesMax / L.mesNeto,
      dias: Math.round(mesMax / (L.anual / 365)),
      rango: !!(c.mensual.min && c.mensual.min !== c.mensual.max)
    };
  }
  function vecesTx(v) {
    return v >= 1 ? 'Recibe ' + num(v, 1) + ' veces lo que tú' : 'Recibe menos que tú';
  }

  function pintarCartas(L) {
    [].forEach.call(raiz.querySelectorAll('.cv-carta'), function (b) {
      var c = porId[b.dataset.id];
      b.hidden = !(est.grupo === 'todos' || c.grupo === est.grupo);
      b.setAttribute('aria-pressed', String(b.dataset.id === est.sel));
      var v = b.querySelector('[data-veces]');
      if (v) v.textContent = c.pendiente ? '' : (c.anual / L.anual >= 1 ? '× ' + num(c.anual / L.anual, 1) + ' tú' : 'menos que tú');
    });
    [].forEach.call(raiz.querySelectorAll('.cv-filtro'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.g === est.grupo)); });
  }

  /* Meses tuyos: un cuadrito por mes, en filas de doce (un año). */
  function cuadritos(meses) {
    var tope = 120, n = Math.min(meses, tope), enteros = Math.floor(n), frac = n - enteros, h = '';
    for (var i = 0; i < enteros; i++) h += '<i></i>';
    if (frac > 0.04 && enteros < tope) h += '<i class="cv-q-frac" style="--f:' + Math.round(frac * 100) + '%"></i>';
    return '<div class="cv-q" aria-hidden="true">' + h + '</div>' +
      (meses > tope ? '<p class="cv-nota">Se dibujan solo diez años (120 meses); la cuenta completa es de ' + num(meses, 1) + ' meses.</p>' : '');
  }

  function pintarDuelo(L) {
    var c = porId[est.sel], caja = $('cvDueloCaja');
    [].forEach.call(raiz.querySelectorAll('.cv-ficha'), function (f) { f.hidden = f.dataset.id !== est.sel; });
    if (!c) { caja.innerHTML = ''; return; }
    if (c.pendiente) {
      caja.innerHTML = '<p class="cv-vacio">' + chip('pendiente') + ' Este cargo no tiene cifra documentada: no hay con qué comparar.</p>';
      return;
    }
    var k = cuentas(c, L);
    var max = Math.max(c.anual, L.anual);
    var w = function (v) { return Math.max(1.5, v / max * 100).toFixed(2) + '%'; };
    var mesesTx = k.meses >= 1
      ? '<b>' + num(k.meses, 1) + ' meses</b> de tu ingreso' + (k.meses >= 12 ? ' (' + num(k.meses / 12, 1) + ' años)' : '')
      : '<b>menos de un mes</b> de tu ingreso';
    caja.innerHTML =
      '<div class="cv-cara">' +
        '<div class="cv-lado cv-lado-tu"><span class="cv-lado-ico" aria-hidden="true">🙋</span><b>Tú</b><span>' + pesos(L.mesNeto) + ' netos al mes</span></div>' +
        '<span class="cv-vs" aria-hidden="true">VS</span>' +
        '<div class="cv-lado cv-lado-ellos"><span class="cv-lado-ico" aria-hidden="true">' + c.icono + '</span><b>' + esc(c.cargo) + '</b><span>' +
          pesos(c.mensual.max) + ' netos al mes' + (k.rango ? ' (máximo)' : '') + '</span></div>' +
      '</div>' +
      '<div class="cv-barras" role="img" aria-label="Neto al año: tú ' + pesos(L.anual) + ', ' + esc(c.cargo) + ' ' + pesos(c.anual) + '">' +
        '<div class="cv-bar"><span class="cv-bar-et">Tú</span><span class="cv-bar-pista"><span class="cv-bar-r cv-bar-tu" style="width:' + w(L.anual) + '"></span></span><b>' + pesos(L.anual) + '</b></div>' +
        '<div class="cv-bar"><span class="cv-bar-et">' + c.icono + ' Ellos</span><span class="cv-bar-pista"><span class="cv-bar-r cv-bar-ellos" style="width:' + w(c.anual) + '"></span></span><b>' + pesos(c.anual) + '</b></div>' +
        '<p class="cv-bar-pie">Neto al año' + (c.parcial ? '; el de ellos es parcial' : '') + '. Lo de ellos: ' + chip(c.anualEstado) + ' · lo tuyo: ' + chip(L.ejemplo ? 'oficial' : 'derivado') + '</p>' +
      '</div>' +
      '<div class="cv-metricas">' +
        '<div class="cv-met cv-met-1"><b>' + (k.veces >= 1 ? '×' + num(k.veces, 1) : 'menos') + '</b><span>' + vecesTx(k.veces) + ' en un año. ' +
          (k.veces >= 1 ? 'Para juntar lo que recibe en un año necesitarías <b>' + num(k.veces, 1) + ' años</b> de tu ingreso.' : '') + ' ' + chip('derivado') + '</span></div>' +
        '<div class="cv-met"><b>' + num(k.meses, 1) + '</b><span>Un mes suyo' + (k.rango ? ' (del máximo)' : '') + ' equivale a ' + mesesTx + '. ' + chip('derivado') + '</span></div>' +
        '<div class="cv-met"><b>' + num(k.dias, 0) + '</b><span><b>días de tu ingreso</b> equivalen a un solo mes' + (k.rango ? ' del máximo' : '') + ' de este cargo. ' + chip('derivado') + '</span></div>' +
      '</div>' +
      (k.meses >= 1 ? '<div class="cv-meses"><p class="cv-meses-t">Un mes suyo, en meses tuyos (cada fila es un año):</p>' + cuadritos(k.meses) + '</div>' : '') +
      '<p class="cv-op">Cómo se obtuvo: veces = su neto anual (' + pesos(c.anual) + ') ÷ tu neto anual (' + pesos(L.anual) + '); meses = su neto mensual' +
        (k.rango ? ' máximo' : '') + ' (' + pesos(c.mensual.max) + ') ÷ tu neto mensual (' + pesos(L.mesNeto) + '); días = su neto mensual ÷ (tu neto anual ÷ 365).</p>';

    var f = $('cv-f-' + c.id), t = f && f.querySelector('.cv-ficha-tuyo');
    if (t) {
      t.innerHTML = '<p class="cv-ratio">' + vecesTx(k.veces) + ' ' + chip('derivado') + '</p>' +
        '<p class="cv-pill"><b>' + num(k.dias, 0) + ' días de tu ingreso</b> equivalen a un solo mes' + (k.rango ? ' del máximo' : '') + ' de este cargo. ' + chip('derivado') + '</p>';
    }
  }

  function pintarRanking(L) {
    var lista = D.cargos.filter(function (c) { return !c.pendiente && (est.grupo === 'todos' || c.grupo === est.grupo); })
      .map(function (c) { return { c: c, v: c.anual }; });
    lista.push({ tu: true, v: L.anual });
    lista.sort(function (a, b) { return b.v - a.v; });
    var max = lista[0].v;
    $('cvRanking').innerHTML = lista.map(function (x) {
      var w = Math.max(1, x.v / max * 100).toFixed(2) + '%';
      if (x.tu) {
        return '<div class="cv-rk cv-rk-tu"><span class="cv-rk-et">🙋 Tú</span><span class="cv-rk-pista"><span class="cv-rk-r" style="width:' + w + '"></span></span><b>' + pesos(x.v) + '</b></div>';
      }
      var c = x.c;
      return '<button type="button" class="cv-rk' + (c.id === est.sel ? ' cv-rk-on' : '') + '" data-id="' + esc(c.id) + '"><span class="cv-rk-et">' + c.icono + ' ' + esc(c.cargo) +
        (c.parcial ? ' <small>(parcial)</small>' : '') + '</span><span class="cv-rk-pista"><span class="cv-rk-r" style="width:' + w + '"></span></span><b>' + pesos(c.anual) + ' ' + chip(c.anualEstado) + '</b></button>';
    }).join('');
  }

  function pintarPrest(L) {
    var Lw = D.ley, dia = L.brutoMes / 30;
    var caja = function (et, ley, ref, dl, dr) {
      return '<div class="cv-pr-caja"><span class="cv-pr-et">' + et + '</span>' +
        '<div class="cv-pr-par"><div><small>Mínimo de ley · ' + dl + ' días</small><b>' + pesos(ley) + '</b></div>' +
        '<div><small>Con la regla de ellos · ' + dr + ' días</small><b>' + pesos(ref) + '</b></div></div>' +
        '<em>' + pesos(ref - ley) + ' de diferencia</em></div>';
    };
    $('cvPrestCuenta').innerHTML =
      '<div class="cv-pr">' +
        caja('🎁 Tu aguinaldo', Lw.aguinaldoDias * dia, Lw.referencia.aguinaldoDias * dia, Lw.aguinaldoDias, Lw.referencia.aguinaldoDias) +
        caja('🏖️ Tu prima vacacional', Lw.primaVacacionalDias * dia, Lw.referencia.primaVacacionalDias * dia, Lw.primaVacacionalDias, Lw.referencia.primaVacacionalDias) +
      '</div>' +
      '<p class="cv-op">' + chip('derivado') + ' Tu sueldo bruto mensual (' + pesos(L.brutoMes) + (L.ejemplo ? ', el salario mínimo de ejemplo' : '') +
        ') entre 30, por los días de cada regla, en bruto y antes de impuestos.</p>';
  }

  /* ---------- Compartir ---------- */
  function textoDuelo(L) {
    var c = porId[est.sel];
    if (!c || c.pendiente) return '';
    var k = cuentas(c, L);
    var f = D.fuentes[c.fuente] || {};
    return 'TÚ CONTRA ELLOS (Auditavisión México)\n' +
      'Mi ingreso: ' + pesos(L.mesNeto) + ' netos al mes' + (L.ejemplo ? ' (salario mínimo 2026)' : '') + '.\n' +
      c.cargo + ': ' + pesos(c.mensual.max) + ' netos al mes' + (k.rango ? ' (máximo)' : '') + ', ' + pesos(c.anual) + ' al año' + (c.parcial ? ' (parcial)' : '') + '.\n' +
      (k.veces >= 1 ? '→ Recibe ' + num(k.veces, 1) + ' veces lo que yo.\n' : '→ Recibe menos que yo.\n') +
      '→ Un mes suyo equivale a ' + num(k.meses, 1) + ' meses de mi ingreso.\n' +
      'Fuente: ' + (f.corto || '') + (f.url ? ' ' + f.url : '') + '\n' + enlace();
  }
  function textoTodo(L) {
    var t = 'COMPARATIVA SALARIAL (Auditavisión México)\n';
    t += 'Mi ingreso: ' + pesos(L.mesNeto) + ' al mes, neto' + (L.ejemplo ? ' (salario mínimo 2026 de ejemplo)' : '') + '.\n';
    t += 'Neto anual 2026 según el PEF y los manuales de remuneraciones:\n';
    D.cargos.filter(function (c) { return !c.pendiente && (est.grupo === 'todos' || c.grupo === est.grupo); }).forEach(function (c) {
      t += '• ' + c.cargo + ': ' + pesos(c.anual) + ' al año' + (c.parcial ? ' (parcial)' : '') + (c.anualEstado === 'derivado' ? ' (calculado)' : '') +
        ', ' + num(c.anual / L.anual, 1) + ' veces lo mío\n';
    });
    t += '\nFuentes: PEF 2026, Anexo 23 (DOF 21-11-2025); manuales de remuneraciones del Senado, la Cámara de Diputados y el PJF (DOF 27-02-2026).\n' + enlace();
    return t;
  }
  function enlace() {
    return location.href.split('#')[0] + '#cargo=' + encodeURIComponent(est.sel);
  }
  function avisar(m) { var p = $('cvCopiado'); p.textContent = m; }
  function copiar(texto, ok) {
    var ta = $('cvTexto');
    var mostrar = function () {
      ta.hidden = false; ta.value = texto; ta.focus(); ta.select();
      avisar('Tu navegador no dejó copiar: selecciona el texto de abajo y cópialo.');
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(function () { ta.hidden = true; avisar(ok); }, mostrar);
    } else mostrar();
  }

  /* ---------- Pintar todo ---------- */
  function pintar() {
    var L = lector();
    pintarMandos();
    pintarLector(L);
    pintarCartas(L);
    pintarDuelo(L);
    pintarRanking(L);
    pintarPrest(L);
  }

  function elegir(id, ir) {
    if (!porId[id]) return;
    est.sel = id;
    try { history.replaceState(null, '', '#cargo=' + encodeURIComponent(id)); } catch (e) { /* sin historial */ }
    pintar();
    if (ir) {
      var d = $('cvDuelo');
      if (d && d.scrollIntoView) d.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  /* ---------- Eventos ---------- */
  var tEsc;
  monto.addEventListener('input', function () {
    est.monto = leerNumero(monto.value);
    clearTimeout(tEsc);
    tEsc = setTimeout(function () { guardar(); pintar(); }, 180);
  });
  raiz.addEventListener('click', function (ev) {
    var b = ev.target.closest ? ev.target.closest('button') : null;
    if (!b || !raiz.contains(b)) return;
    if (b.dataset.periodo) { est.periodo = b.dataset.periodo; guardar(); pintar(); }
    else if (b.dataset.tipo) { est.tipo = b.dataset.tipo; guardar(); pintar(); }
    else if (b.dataset.sm) {
      est.monto = D.sm[b.dataset.sm]; est.periodo = 'mes'; est.tipo = 'bruto';
      monto.value = num(est.monto, 2); guardar(); pintar();
    } else if (b.hasAttribute('data-borrar')) {
      est.monto = 0; monto.value = ''; guardar(); pintar(); monto.focus();
    } else if (b.classList.contains('cv-filtro')) { est.grupo = b.dataset.g; pintar(); }
    else if (b.classList.contains('cv-carta')) elegir(b.dataset.id, true);
    else if (b.classList.contains('cv-rk') && b.dataset.id) elegir(b.dataset.id, true);
    else if (b.id === 'cvCompartir') {
      var t = textoDuelo(lector());
      if (!t) return;
      if (navigator.share) {
        navigator.share({ title: 'Tú contra ellos · Auditavisión', text: t }).catch(function () { /* cancelado */ });
      } else copiar(t, '¡Listo! Tu cara a cara quedó copiado: pégalo en X, WhatsApp o donde quieras.');
    } else if (b.id === 'cvCopiarTodo') copiar(textoTodo(lector()), '¡Comparativa copiada! Lista para pegar en tus redes.');
    else if (b.id === 'cvEnlace') copiar(enlace(), 'Enlace copiado. No lleva tu sueldo: quien lo abra verá el cargo con su propio ingreso.');
  });

  /* ---------- Arranque ---------- */
  cargar();
  if (est.monto > 0) monto.value = num(est.monto, est.monto % 1 ? 2 : 0);
  var h = /cargo=([^&]+)/.exec(location.hash);
  if (h && porId[decodeURIComponent(h[1])]) est.sel = decodeURIComponent(h[1]);
  pintar();
  if (h) { var dd = $('cvDuelo'); if (dd && dd.scrollIntoView) dd.scrollIntoView({ block: 'start' }); }
  window.addEventListener('hashchange', function () {
    var m = /cargo=([^&]+)/.exec(location.hash);
    if (m && porId[decodeURIComponent(m[1])] && decodeURIComponent(m[1]) !== est.sel) elegir(decodeURIComponent(m[1]), false);
  });
})();
