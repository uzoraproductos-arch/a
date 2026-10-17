/* Auditavisión · Costo Ambiental › Tu ticket en negativo (aplicación 2,
   16-10-2026). La página la escribe herramientas/am_ticket.py con las
   cifras oficiales y, en JSON (#atDatos), lo que toca a cada habitante
   (mismas cuentas que amTkCuentas() del motor) y los parámetros con que se
   saca el neto de quien está en nómina (tarifa del art. 96 de la LISR,
   subsidio para el empleo y cuotas obreras del IMSS).
   Aquí no se escribe ninguna cifra oficial: solo se divide entre el
   ingreso del lector, y todo lo que sale de esa división es «derivado».
   Prefijo de clases e ids: at-. */
(function () {
  'use strict';

  var D;
  try { D = JSON.parse(document.getElementById('atDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  var raiz = $('atRaiz');
  if (!raiz) return;

  var COMPARTIDA = 'auditavision_cc_sueldo';
  var est = { m: 0, per: 'mes', tipo: 'neto', emitido: false, ajena: false, origen: '' };
  var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Formato ---------- */
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function num(v, d) { return Number(v).toLocaleString('es-MX', { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 }); }
  function pesos(v) { return '$' + Math.round(v).toLocaleString('es-MX'); }
  function pesosRef(v) { return '$' + (Math.round(v * 100) / 100).toLocaleString('es-MX'); }
  function fmt(v, f) {
    if (f === 'neg') return (Math.round(v) < 0 ? '−' : '') + '$' + Math.abs(Math.round(v)).toLocaleString('es-MX');
    if (f === 'pos') return '+$' + Math.round(v).toLocaleString('es-MX');
    if (f === 'negkg') return (Math.round(v) < 0 ? '−' : '') + Math.abs(Math.round(v)).toLocaleString('es-MX') + ' kg';
    return pesosRef(v);
  }
  function chip(e) { return '<span class="est-chip est-' + e + '">' + e + '</span>'; }
  function leer(t) {
    var s = String(t == null ? '' : t).trim().toLowerCase().replace(/\s+/g, '');
    var mult = 1;
    if (/mil$/.test(s)) { mult = 1000; s = s.replace(/mil$/, ''); }
    var n = parseFloat(s.replace(/[^0-9.]/g, ''));
    return isFinite(n) && n > 0 ? n * mult : 0;
  }

  /* ---------- El neto de quien está en nómina (como cc-compara.js) ---------- */
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
  function mesNeto() {
    if (!(est.m > 0)) return 0;
    var mes = est.per === 'anio' ? est.m / 12 : est.m;
    return est.tipo === 'bruto' ? desdeBruto(mes).neto : mes;
  }

  /* ---------- Las cuentas (amTkCuentas del motor, con el ingreso) ---------- */
  function cuentas(v) {
    var c = {
      ingreso: v, anual: v * 12, dia: v * 12 / 365,
      intereses: D.intereses, dano: D.dano, basuraPesos: D.basuraPesos, deuda: D.deuda,
      ramo16: D.ramo16, gpa: D.gpa, kg: D.kg
    };
    c.cargoAnual = c.intereses + c.dano;
    c.pct = c.cargoAnual / c.anual * 100;
    return c;
  }
  function dias(c, x) { var d = x / c.dia; return num(d, d < 10 ? 1 : 0) + ' días de tu ingreso'; }

  /* ---------- Guardar y leer el sueldo (clave compartida) ---------- */
  function guardar() {
    if (est.ajena) return;   /* una liga ajena no pisa lo que este equipo recuerda */
    try {
      if (est.m > 0) localStorage.setItem(COMPARTIDA, JSON.stringify({ monto: est.m, periodo: est.per, tipo: est.tipo }));
      else localStorage.removeItem(COMPARTIDA);
    } catch (e) { /* sin almacenamiento: no pasa nada */ }
  }
  function recuperar() {
    try {
      var s = JSON.parse(localStorage.getItem(COMPARTIDA) || 'null');
      if (!s || !(Number(s.monto) > 0)) return false;
      est.m = Number(s.monto);
      est.per = (s.periodo === 'anio' || s.periodo === 'ano') ? 'anio' : 'mes';
      est.tipo = s.tipo === 'bruto' ? 'bruto' : 'neto';
      est.origen = 'Tomado de lo que guardaste en la Calculadora Cívica de este navegador (' + est.tipo + ', ' + (est.per === 'anio' ? 'al año' : 'al mes') + '). Cámbialo si quieres.';
      return true;
    } catch (e) { return false; }
  }
  function deLiga() {
    var q;
    try { q = new URLSearchParams(location.search); } catch (e) { return false; }
    var v = leer(q.get('ingreso'));
    if (!(v > 0)) return false;
    est.m = v; est.per = q.get('p') === 'anio' ? 'anio' : 'mes'; est.tipo = q.get('t') === 'bruto' ? 'bruto' : 'neto';
    est.ajena = true;
    est.origen = 'Abriste una liga compartida con este ingreso. No se guarda en tu navegador hasta que lo cambies.';
    return true;
  }

  /* ---------- Paso 1: mandos ---------- */
  var campo = $('atIngreso'), rango = $('atRango');
  function pintarMandos() {
    [].forEach.call(raiz.querySelectorAll('[data-per]'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.per === est.per)); });
    [].forEach.call(raiz.querySelectorAll('[data-tipo]'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.tipo === est.tipo)); });
    $('atIngresoEt').textContent = 'Tu ingreso ' + est.tipo + (est.per === 'anio' ? ' al año' : ' al mes');
    rango.max = est.per === 'anio' ? 2400000 : 200000;
    rango.step = est.per === 'anio' ? 6000 : 500;
    rango.value = Math.min(est.m || 0, Number(rango.max));
    var n = $('atNeto'), v = mesNeto();
    if (!(est.m > 0)) { n.innerHTML = ''; return; }
    if (est.tipo === 'bruto') {
      var r = desdeBruto(est.per === 'anio' ? est.m / 12 : est.m);
      n.innerHTML = 'Tu neto al mes: <b>' + pesosRef(r.neto) + '</b> ' + chip('derivado') + ' <small>' +
        (r.exento ? 'Hasta el salario mínimo no se paga ISR ni cuota obrera del IMSS: el neto es igual al bruto.' :
          'Bruto ' + pesosRef(r.bruto) + ' menos ISR ' + pesosRef(r.isr) + ' y cuotas del IMSS ' + pesosRef(r.cuotas) + ', como quien trabaja en nómina.') + '</small>';
    } else if (est.per === 'anio') {
      n.innerHTML = 'Al mes: <b>' + pesosRef(v) + '</b> <small>(lo anual entre 12)</small>';
    } else n.innerHTML = '';
  }
  function origen(html) { $('atOrigenTx').innerHTML = html; }
  var ORIGEN_BASE = $('atOrigenTx').innerHTML;

  function tocar() {
    if (est.ajena) { est.ajena = false; }
    guardar();
    pintarMandos();
    if (est.emitido || est.m > 0) emitir(false);
  }
  var tTeclea = null;
  campo.addEventListener('input', function () {
    est.m = leer(campo.value);
    origen(ORIGEN_BASE);
    clearTimeout(tTeclea);
    tTeclea = setTimeout(tocar, 220);
  });
  campo.addEventListener('keydown', function (ev) { if (ev.key === 'Enter') { est.m = leer(campo.value); guardar(); pintarMandos(); emitir(true); } });
  rango.addEventListener('input', function () {
    est.m = Number(rango.value);
    campo.value = est.m ? num(est.m, 0) : '';
    origen(ORIGEN_BASE);
    tocar();
  });
  raiz.addEventListener('click', function (ev) {
    var b = ev.target.closest('button');
    if (!b || !raiz.contains(b)) return;
    if (b.dataset.per) { est.per = b.dataset.per; tocar(); }
    else if (b.dataset.tipo) { est.tipo = b.dataset.tipo; tocar(); }
    else if (b.dataset.ej) {
      var fr = b.dataset.ej === 'frontera';
      est.m = fr ? D.sm.frontera : D.sm.general; est.per = 'mes'; est.tipo = 'neto';
      campo.value = num(est.m, 2);
      guardar(); pintarMandos(); emitir(true);
      origen('Ejemplo oficial: el salario mínimo ' + (fr ? 'de la Zona Libre de la Frontera Norte' : 'general') + ' mensual de 2026 ' + chip('oficial') +
        ' (CONASAMI, DOF 9 de diciembre de 2025; el diario por 30). No paga ISR ni cuota obrera, así que su neto es igual a su bruto. Escribe el tuyo para ver tu parte.');
    }
    else if (b.id === 'atEmitir') { est.m = leer(campo.value); guardar(); pintarMandos(); emitir(true); }
    else if (b.id === 'atReiniciar') reiniciar();
    else if (b.id === 'atCopiar') copiar();
    else if (b.id === 'atLiga') compartir();
    else if (b.id === 'atImprimir') imprimir();
  });

  function reiniciar() {
    est.m = 0; est.emitido = false; est.ajena = false;
    campo.value = '';
    guardar(); pintarMandos();
    origen(ORIGEN_BASE);
    $('atSalida').innerHTML = '<p class="at-vacio">Escribe tu ingreso y pulsa «Emitir». El ticket se imprime renglón por renglón.</p>';
    $('atTkAcc').hidden = true;
    $('atCal').innerHTML = $('atMeses').innerHTML = '<p class="at-vacio">Aparece cuando escribas tu ingreso.</p>';
    campo.focus();
  }

  /* ---------- El sello de emisión (el mismo del motor) ---------- */
  function sello(fecha, folio) {
    var k = 'atsl' + Math.random().toString(36).slice(2, 8);
    return '<div class="sello-av at-sello" role="img" aria-label="Sello de emisión de Auditavisión, ' + esc(fecha) + ', folio ' + esc(folio) + '">' +
      '<svg viewBox="0 0 200 200" aria-hidden="true" focusable="false"><defs>' +
        '<path id="' + k + 'a" d="M 28,100 A 72,72 0 0,1 172,100"/>' +
        '<path id="' + k + 'b" d="M 22,100 A 78,78 0 0,0 178,100"/></defs>' +
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
        '<text x="100" y="142" text-anchor="middle" class="sello-folio">' + esc(folio) + '</text>' +
      '</svg></div>';
  }
  function fechaCorta(d) {
    return String(d.getDate()).padStart(2, '0') + '/' + String(d.getMonth() + 1).padStart(2, '0') + '/' + d.getFullYear();
  }

  /* ---------- Paso 2: el ticket ---------- */
  function emitir(animar) {
    var salida = $('atSalida');
    var v = mesNeto();
    if (!(v > 0)) {
      /* Un cero del lector no es un dato pendiente: es que aún no escribe. */
      if (est.emitido || animar) {
        salida.innerHTML = '<p class="at-vacio"><span class="at-sim">Simulación</span> Escribe un ingreso mensual mayor que cero: con $0 no hay parte que calcular.</p>';
        $('atTkAcc').hidden = true;
      }
      return;
    }
    est.emitido = true;
    var c = cuentas(v);
    var hoy = new Date();
    var folio = hoy.toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' });
    var n = 0;
    function lin(txt, val, f, nota, clase) {
      return '<div class="at-l ' + (clase || '') + '" style="--i:' + (n++) + '"><span class="at-c">' + txt + (nota ? '<small>' + nota + '</small>' : '') + '</span>' +
        '<span class="at-p" aria-hidden="true"></span><b class="at-v" data-v="' + val + '" data-f="' + f + '">' + fmt(animar && !quieto ? 0 : val, f) + '</b></div>';
    }
    function sec(t) { return '<div class="at-tk-sec" style="--i:' + (n++) + '">' + t + '</div>'; }
    var ancho = Math.min(100, c.pct), k = ancho / c.pct;

    salida.innerHTML =
      '<div class="at-tk' + (animar && !quieto ? ' at-tk-anim' : '') + '" id="atTk">' +
        '<div class="at-tk-cab" style="--i:' + (n++) + '"><b>AUDITAVISIÓN</b><span>Ticket ciudadano en negativo</span><small>Emitido el ' + esc(folio) + ' · por habitante · ' + num(D.pob, 1) + ' millones de personas (CONAPO 2026)</small></div>' +
        lin('Tu ingreso neto de referencia', v, 'pesos', 'al mes · ' + pesos(c.anual) + ' al año', 'at-ref') +
        sec('Cargos de este año a tu nombre') +
        lin('Intereses de la deuda pública', -c.intereses, 'neg', '2026 · ' + dias(c, c.intereses)) +
        lin('Daño ambiental del país', -c.dano, 'neg', '2024 · ' + dias(c, c.dano)) +
        lin('· de él, por basura mal gestionada', -c.basuraPesos, 'neg', 'incluido en el renglón anterior', 'at-subl') +
        lin('TOTAL CARGADO EN EL AÑO', -c.cargoAnual, 'neg', dias(c, c.cargoAnual) + ' · ' + num(c.pct, 1) + ' % de lo que ganas al año', 'at-total') +
        '<div class="at-graf" style="--i:' + (n++) + '" role="img" aria-label="De cada 100 pesos que ganas al año, ' + num(c.pct, 1) + ' equivalen a lo cargado a tu nombre">' +
          '<span class="at-graf-t">De cada $100 que ganas al año</span>' +
          '<span class="at-graf-r"><i class="at-c1" style="width:' + (c.intereses / c.anual * 100 * k).toFixed(2) + '%"></i><i class="at-c3" style="width:' + (c.dano / c.anual * 100 * k).toFixed(2) + '%"></i></span>' +
          '<span class="at-graf-l"><span><i class="at-sw at-c1"></i>intereses $' + num(c.intereses / c.anual * 100, 1) + '</span><span><i class="at-sw at-c3"></i>daño ambiental $' + num(c.dano / c.anual * 100, 1) + '</span>' +
            (c.pct > 100 ? '<span class="at-graf-mas">rebasa tu ingreso del año</span>' : '') + '</span>' +
        '</div>' +
        sec('Saldo acumulado a tu nombre') +
        lin('Deuda pública total (SHRFSP)', -c.deuda, 'neg', 'cierre estimado 2026 · ' + num(c.deuda / v, 1) + ' meses de tu ingreso', 'at-total') +
        sec('Lo que se abona para reparar') +
        lin('Presupuesto federal de Medio Ambiente', c.ramo16, 'pos', 'Ramo 16, aprobado 2026') +
        lin('Gasto en protección ambiental del sector público', c.gpa, 'pos', '2024 · sector público consolidado (INEGI CEEM, p. 2)') +
        sec('Tu huella física') +
        lin('Basura que generas al año', -c.kg, 'negkg', num(D.kgDia, 3) + ' kg al día × 365') +
        '<div class="at-tk-bal" style="--i:' + (n++) + '">Por cada <b>$1</b> que el presupuesto federal de Medio Ambiente abona a tu nombre, se te cargan <b>$' + num(c.intereses / c.ramo16, 0) + '</b> de intereses y <b>$' + num(c.dano / c.ramo16, 0) + '</b> de daño ambiental.</div>' +
        '<div class="at-tk-pie" style="--i:' + (n++) + '">' + chip('derivado') + ' ' + esc(D.nota) + ' Los días y los meses dividen cada cargo entre tu ingreso.</div>' +
        '<div class="at-tk-firma" style="--i:' + (n++) + '">' + sello(fechaCorta(hoy), 'TICKET AMBIENTAL') + '</div>' +
      '</div>';
    $('atTkAcc').hidden = false;
    if (animar && !quieto) contar(salida.querySelectorAll('.at-v'));
    calendario(c);
    meses(c);
  }

  /* Los importes suben de cero a su valor mientras el renglón aparece. */
  function contar(els) {
    var ini = performance.now(), dur = 900;
    [].forEach.call(els, function (el, i) {
      var meta = Number(el.dataset.v), f = el.dataset.f, retraso = i * 110 + 150;
      function paso(t) {
        var p = Math.min(1, Math.max(0, (t - ini - retraso) / dur));
        p = 1 - Math.pow(1 - p, 3);
        el.textContent = fmt(meta * p, f);
        if (p < 1 && el.isConnected) requestAnimationFrame(paso);
      }
      requestAnimationFrame(paso);
    });
  }

  /* ---------- Paso 3: el año en días ---------- */
  var MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  function fechaDelDia(d) {
    var f = new Date(2026, 0, 1);
    f.setDate(f.getDate() + Math.max(0, Math.ceil(d) - 1));
    return f.toLocaleDateString('es-MX', { day: 'numeric', month: 'long' });
  }
  function calendario(c) {
    var dI = c.intereses / c.dia, dD = c.dano / c.dia, dT = dI + dD;
    var pI = Math.min(100, dI / 365 * 100), pD = Math.min(100 - pI, dD / 365 * 100);
    var marcas = MESES.map(function (m, i) { return '<span style="left:' + (i / 12 * 100).toFixed(2) + '%">' + m + '</span>'; }).join('');
    var txt;
    if (dT <= 365) {
      txt = 'Trabajarías del 1 de enero al <b>' + fechaDelDia(dI) + '</b> para cubrir tu parte de los intereses de la deuda (' + num(dI, dI < 10 ? 1 : 0) + ' días), y hasta el <b>' + fechaDelDia(dT) + '</b> para cubrir también tu parte del daño ambiental (' + num(dT, dT < 10 ? 1 : 0) + ' días en total). ' + chip('derivado');
    } else {
      txt = 'Con este ingreso <b>no te alcanza el año</b>: tu parte de los intereses y del daño ambiental equivale a ' + num(dT, 0) + ' días de tu ingreso, es decir ' + num(dT / 365, 1) + ' años enteros de trabajo. ' + chip('derivado');
    }
    $('atCal').innerHTML =
      '<div class="at-cal" role="img" aria-label="Regla del año: intereses ' + num(dI, 0) + ' días, daño ambiental ' + num(dD, 0) + ' días">' +
        '<div class="at-cal-r"><i class="at-c1" style="width:' + pI.toFixed(2) + '%"></i><i class="at-c3" style="width:' + pD.toFixed(2) + '%"></i></div>' +
        '<div class="at-cal-m" aria-hidden="true">' + marcas + '</div>' +
      '</div>' +
      '<p class="at-cal-tx">' + txt + '</p>' +
      '<p class="at-cal-ley"><span><i class="at-sw at-c1"></i>intereses de la deuda (2026)</span><span><i class="at-sw at-c3"></i>daño ambiental (2024)</span></p>';
  }

  function meses(c) {
    var m = c.deuda / c.ingreso, enteros = Math.floor(m), max = 360;
    var celdas = '', dib = Math.min(enteros, max);
    for (var i = 0; i < dib; i++) celdas += '<i' + (i % 12 === 11 ? ' class="at-mes-a"' : '') + '></i>';
    var resto = m - enteros;
    if (enteros < max && resto > 0.05) celdas += '<i class="at-mes-p" style="--p:' + (resto * 100).toFixed(0) + '%"></i>';
    $('atMeses').innerHTML =
      '<p class="at-meses-g"><b>' + num(m, 1) + ' meses</b> de tu ingreso neto: ' + num(m / 12, 1) + ' años sin gastar un peso en otra cosa. ' + chip('derivado') + '</p>' +
      '<div class="at-meses" role="img" aria-label="' + num(m, 1) + ' meses de tu ingreso">' + celdas + '</div>' +
      (enteros > max ? '<p class="at-cal-ley">Dibujamos los primeros ' + max + ' meses (30 años); faltan ' + num(m - max, 0) + ' más.</p>' :
        '<p class="at-cal-ley">Cada fila de 12 cuadros es un año.</p>');
  }

  /* ---------- Paso 4: la basura de lo que va del año ---------- */
  (function basuraHoy() {
    var hoy = new Date(), ini = new Date(hoy.getFullYear(), 0, 1);
    var d = Math.floor((hoy - ini) / 86400000) + 1;
    $('atKgHoy').innerHTML = 'Al promedio nacional, en los <b>' + num(d, 0) + ' días</b> que van de ' + hoy.getFullYear() + ' te corresponden <b>' + num(D.kgDia * d, 0) + ' kg</b> de basura (' + num(D.kgDia, 3) + ' kg × ' + num(d, 0) + ' días). ' + chip('derivado');
  })();

  /* ---------- Copiar, compartir, imprimir ---------- */
  function aviso(t) {
    var a = $('atAvisoC'); a.textContent = t;
    clearTimeout(aviso.t); aviso.t = setTimeout(function () { a.textContent = ''; }, 3500);
  }
  function alPortapapeles(t, ok) {
    function viejo() {
      var ta = document.createElement('textarea');
      ta.value = t; ta.setAttribute('readonly', ''); ta.className = 'at-oculto';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); aviso(ok); } catch (e) { aviso('No se pudo copiar: selecciona el texto a mano.'); }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(function () { aviso(ok); }, viejo);
    else viejo();
  }
  function textoTicket() {
    var v = mesNeto(), c = cuentas(v);
    var p = function (x) { return '−' + pesos(Math.abs(x)); };
    return 'TICKET CIUDADANO EN NEGATIVO · Auditavisión\n' +
      'Ingreso neto de referencia: ' + pesos(v) + ' al mes\n\n' +
      'CARGOS DE ESTE AÑO A TU NOMBRE (por habitante)\n' +
      '- Intereses de la deuda pública 2026: ' + p(c.intereses) + '\n' +
      '- Daño ambiental del país 2024: ' + p(c.dano) + ' (de él, basura: ' + p(c.basuraPesos) + ')\n' +
      '= Total del año: ' + p(c.cargoAnual) + ', ' + num(c.cargoAnual / c.dia, 1) + ' días de tu ingreso\n\n' +
      'SALDO ACUMULADO: deuda pública total (SHRFSP, cierre estimado 2026): ' + p(c.deuda) + ', ' + num(c.deuda / v, 1) + ' meses de tu ingreso\n' +
      'ABONOS: presupuesto de Medio Ambiente 2026 +' + pesos(c.ramo16) + '; protección ambiental del país 2024 +' + pesos(c.gpa) + '\n' +
      'HUELLA: ' + num(c.kg, 0) + ' kg de basura al año\n\n' +
      'Fuentes: PEF 2026 (Anexo 8), INEGI Cuentas Económicas y Ecológicas 2024, SHCP Criterios Generales de Política Económica 2027 (p. 67), SEMARNAT Diagnóstico Básico para la Gestión Integral de los Residuos, CONAPO. Cifras oficiales repartidas por habitante (derivado).\n' +
      liga();
  }
  function liga() {
    var q = new URLSearchParams();
    q.set('ingreso', String(Math.round(est.m * 100) / 100));
    if (est.per === 'anio') q.set('p', 'anio');
    if (est.tipo === 'bruto') q.set('t', 'bruto');
    return location.origin + location.pathname + '?' + q.toString();
  }
  function copiar() { if (mesNeto() > 0) alPortapapeles(textoTicket(), 'Ticket copiado con sus fuentes.'); }
  function compartir() {
    if (!(mesNeto() > 0)) return;
    var u = liga();
    if (navigator.share) {
      navigator.share({ title: 'Mi ticket en negativo · Auditavisión', text: 'Lo que ya me cargaron a mi nombre, con cifras oficiales:', url: u })
        .catch(function () { /* el lector cerró el menú */ });
    } else alPortapapeles(u, 'Liga copiada: quien la abra verá el mismo ticket.');
  }
  function imprimir() {
    document.body.classList.add('at-print');
    var quitar = function () { document.body.classList.remove('at-print'); window.removeEventListener('afterprint', quitar); };
    window.addEventListener('afterprint', quitar);
    window.print();
    setTimeout(quitar, 1500);
  }

  /* ---------- Arranque ---------- */
  if (deLiga() || recuperar()) {
    campo.value = num(est.m, est.m % 1 ? 2 : 0);
    origen(esc(est.origen));
    pintarMandos();
    emitir(false);
  } else pintarMandos();
})();
