/* Auditavisión · Costo ambiental › El PIB no alcanza (aplicación 4,
   16-10-2026). La página la escribe herramientas/am_pib.py con todas las
   cifras puestas; aquí solo se anima la cascada, se mueve el simulador
   (la misma aritmética de ceeRecalcular() del motor) y se cambia la unidad
   del desglose. Prefijo: ap-. Respeta prefers-reduced-motion. */
(function () {
  'use strict';

  var raiz = document.getElementById('apRaiz');
  if (!raiz) return;
  var D;
  try { D = JSON.parse(document.getElementById('apDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  raiz.classList.add('ap-js');

  function f1(v) { return (Math.round(v * 10) / 10).toFixed(1); }
  function signo(v, suf) { return (v >= 0 ? '+' : '−') + f1(Math.abs(v)) + suf; }
  function billones(mdp) { return '$' + (mdp / 1e6).toFixed(2) + ' billones'; }

  /* ---------------- 1. Cascada ---------------- */
  var filas = Array.prototype.slice.call(raiz.querySelectorAll('.ap-casc-fila'));
  var paso = filas.length - 1, reloj = null;
  var bPlay = $('apPlay'), bPlayTx = $('apPlayTx');

  function pintaCascada() {
    filas.forEach(function (f, i) {
      f.classList.toggle('ap-on', i <= paso);
      f.classList.toggle('ap-actual', i === paso);
    });
    var f = filas[paso];
    $('apContador').textContent = f
      ? 'Paso ' + (paso + 1) + ' de ' + filas.length + ' · ' + f.getAttribute('data-et') + ': ' + f.getAttribute('data-cifra')
      : 'Pulsa «Reproducir la resta» o «Siguiente».';
    $('apPrev').disabled = paso < 0;
    $('apNext').disabled = paso >= filas.length - 1;
  }
  function para() {
    if (reloj) { clearInterval(reloj); reloj = null; }
    bPlayTx.textContent = 'Reproducir la resta';
    bPlay.firstElementChild.textContent = '▶';
  }
  function reproduce() {
    if (reloj) { para(); return; }
    if (paso >= filas.length - 1) paso = -1;
    bPlayTx.textContent = 'Pausa';
    bPlay.firstElementChild.textContent = '⏸';
    var avanza = function () {
      if (paso >= filas.length - 1) { para(); return; }
      paso++; pintaCascada();
    };
    avanza();
    reloj = setInterval(avanza, quieto ? 600 : 1200);
  }
  bPlay.addEventListener('click', reproduce);
  $('apPrev').addEventListener('click', function () { para(); if (paso > -1) paso--; pintaCascada(); });
  $('apNext').addEventListener('click', function () { para(); if (paso < filas.length - 1) paso++; pintaCascada(); });
  $('apTodo').addEventListener('click', function () { para(); paso = filas.length - 1; pintaCascada(); });

  if (!quieto && 'IntersectionObserver' in window) {
    paso = -1;
    var io = new IntersectionObserver(function (es) {
      if (es.some(function (e) { return e.isIntersecting; })) { io.disconnect(); if (paso < 0) reproduce(); }
    }, { threshold: 0.35 });
    io.observe($('apCascLista'));
  }
  pintaCascada();

  /* ---------------- 2. Simulador ---------------- */
  var ids = { g: 'apG', ct: 'apCt', cf: 'apCf' };
  var ESC = {
    base: { g: 5.0, ct: D.ctadaPct, cf: D.ccfPct },
    espejismo: { g: 5.0, ct: D.ctadaPct + 2, cf: D.ccfPct },
    limpio: { g: 5.0, ct: Math.max(0, D.ctadaPct - 2), cf: D.ccfPct }
  };
  function lee(k) { return parseFloat($(ids[k]).value); }
  function pon(k, v) {
    var el = $(ids[k]);
    var mn = parseFloat(el.min), mx = parseFloat(el.max);
    el.value = Math.min(mx, Math.max(mn, Math.round(v * 10) / 10));
  }
  function tarjeta(k, v, sub, tono) {
    return '<div class="ap-tar" data-tono="' + tono + '"><span class="ap-tar-k">' + k + '</span><span class="ap-tar-v">' + v +
      '</span><span class="ap-tar-sub">' + sub + '</span></div>';
  }
  function barra(id, v, escala) {
    var el = $(id);
    var w = Math.abs(v) / escala * 50;
    el.style.width = w.toFixed(2) + '%';
    el.style.left = (v >= 0 ? 50 : 50 - w).toFixed(2) + '%';
    el.classList.toggle('ap-neg', v < 0);
    $(id + 'V').textContent = signo(v, '%');
  }
  function recalcula() {
    var g = lee('g'), ct = lee('ct'), cf = lee('cf');
    $('apGVal').textContent = f1(g) + ' %';
    $('apCtVal').textContent = f1(ct) + ' % del PIB';
    $('apCfVal').textContent = f1(cf) + ' % del PIB';

    var pib1 = D.pib * (1 + g / 100);
    var pine1 = pib1 * (1 - cf / 100 - ct / 100);
    var gPine = (pine1 / D.pine - 1) * 100;
    var brecha = g - gPine;
    var amb1 = pib1 * (ct / 100);

    var ver, tono;
    if (gPine < 0 && g > 0) {
      ver = 'El PIB crece y la riqueza real se encoge. Es el caso que el indicador tradicional no deja ver: se anuncia expansión mientras el capital natural se consume más rápido de lo que la economía avanza.'; tono = 'malo';
    } else if (brecha > 0.15) {
      ver = 'El PIB crece más rápido que la riqueza real. Parte de lo que se anuncia como crecimiento se está pagando con capital natural que no se repone.'; tono = 'alerta';
    } else if (brecha < -0.15) {
      ver = 'La riqueza real crece más rápido que el PIB. Es lo que ocurre cuando la economía avanza y al mismo tiempo reduce el daño que causa para avanzar.'; tono = 'bueno';
    } else {
      ver = 'El PIB y la riqueza real avanzan casi al mismo paso: la cuenta ambiental se mantiene en la misma proporción del producto.'; tono = 'neutro';
    }
    var ico = { malo: '🚨', alerta: '⚠️', bueno: '🌿', neutro: '⚖️' }[tono];

    $('apRes').innerHTML =
      '<div class="ap-tars">' +
        tarjeta('Crecimiento del PIB', signo(g, '%'), 'Lo que se anunciaría', 'pib') +
        tarjeta('Crecimiento del PINE', signo(gPine, '%'), 'La riqueza que de verdad queda', gPine < 0 ? 'malo' : 'pine') +
        tarjeta('Brecha entre ambos', signo(brecha, ' pp'), 'Puntos porcentuales de diferencia', 'brecha') +
        tarjeta('Cuenta ambiental del año', billones(amb1), 'Lo que costaría el deterioro', 'costo') +
      '</div>' +
      '<p class="ap-veredicto" data-tono="' + tono + '"><span aria-hidden="true">' + ico + '</span> ' + ver + '</p>' +
      '<p class="ap-res-nota">Con estos controles, el PIB del año siguiente sería de ' + billones(pib1) + ' y el PINE de ' + billones(pine1) +
      ' (hipotéticos: resultado de la simulación, no cifras publicadas).</p>';

    var escala = Math.max(15, Math.abs(g), Math.abs(gPine));
    barra('apBarPib', g, escala);
    barra('apBarPine', gPine, escala);

    Array.prototype.forEach.call(raiz.querySelectorAll('[data-esc]'), function (b) {
      var e = ESC[b.getAttribute('data-esc')];
      var igual = Math.abs(e.g - g) < 0.05 && Math.abs(e.ct - ct) < 0.05 && Math.abs(e.cf - cf) < 0.05;
      b.setAttribute('aria-pressed', igual ? 'true' : 'false');
    });
    try {
      var h = '#g=' + f1(g) + '&ct=' + f1(ct) + '&cf=' + f1(cf);
      if (location.hash !== h && (location.hash.indexOf('#g=') === 0 || g !== 5 || ct !== D.ctadaPct || cf !== D.ccfPct)) {
        history.replaceState(null, '', location.pathname + location.search + h);
      }
    } catch (e) { /* sin historial: no pasa nada */ }
  }
  ['g', 'ct', 'cf'].forEach(function (k) { $(ids[k]).addEventListener('input', recalcula); });
  Array.prototype.forEach.call(raiz.querySelectorAll('.ap-paso'), function (b) {
    b.addEventListener('click', function () {
      var el = $(b.getAttribute('data-para'));
      el.value = Math.min(parseFloat(el.max), Math.max(parseFloat(el.min), Math.round((parseFloat(el.value) + parseFloat(b.getAttribute('data-d'))) * 10) / 10));
      recalcula();
    });
  });
  Array.prototype.forEach.call(raiz.querySelectorAll('[data-esc]'), function (b) {
    b.addEventListener('click', function () {
      var e = ESC[b.getAttribute('data-esc')];
      pon('g', e.g); pon('ct', e.ct); pon('cf', e.cf);
      recalcula();
    });
  });
  /* Un enlace con #g=…&ct=…&cf=… abre ese escenario. */
  (function () {
    var m = /^#g=(-?[\d.]+)&ct=([\d.]+)&cf=([\d.]+)$/.exec(location.hash || '');
    if (m) { pon('g', +m[1]); pon('ct', +m[2]); pon('cf', +m[3]); }
  })();
  recalcula();
  $('apCopiar').addEventListener('click', function () {
    var url = location.href.split('#')[0] + '#g=' + f1(lee('g')) + '&ct=' + f1(lee('ct')) + '&cf=' + f1(lee('cf'));
    var ok = function () { $('apCopiado').textContent = '✓ Enlace copiado'; };
    var mal = function () { $('apCopiado').textContent = url; };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(ok, mal);
      else mal();
    } catch (e) { mal(); }
  });

  /* ---------------- 3. Unidad del desglose ---------------- */
  var NOTAS = {
    pesos: 'Millones de pesos corrientes de ' + D.ej + '.',
    pib: 'Porcentaje del PIB, como lo publica el INEGI (redondeado a un decimal).',
    de100: 'De cada $100 de costo ambiental del año, cuánto se va a cada renglón (derivado: monto ÷ costo ambiental total × 100).'
  };
  var unidad = 'pesos';
  try { var u0 = localStorage.getItem('av-am-pib-unidad'); if (NOTAS[u0]) unidad = u0; } catch (e) { /* sin almacenamiento */ }
  function ponUnidad(u) {
    unidad = u;
    Array.prototype.forEach.call(raiz.querySelectorAll('.ap-comp-val'), function (el) {
      el.textContent = el.getAttribute('data-' + u);
    });
    Array.prototype.forEach.call(raiz.querySelectorAll('[data-u]'), function (b) {
      if (b.tagName === 'BUTTON') b.setAttribute('aria-pressed', b.getAttribute('data-u') === u ? 'true' : 'false');
    });
    $('apUnidadNota').textContent = NOTAS[u];
    try { localStorage.setItem('av-am-pib-unidad', u); } catch (e) { /* sin almacenamiento */ }
  }
  Array.prototype.forEach.call(raiz.querySelectorAll('button[data-u]'), function (b) {
    b.addEventListener('click', function () { ponUnidad(b.getAttribute('data-u')); });
  });
  ponUnidad(unidad);
})();
