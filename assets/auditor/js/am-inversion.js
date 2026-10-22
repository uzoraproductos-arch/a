/* Auditavisión · Costo Ambiental › Simulador de inversión ambiental
   (aplicación 4, 22-10-2026). La página la escribe
   herramientas/am_inversion.py con las cifras oficiales; aquí se hacen las
   dos cuentas del lector, todas derivadas e hipotéticas, y se rotulan así.
   Prefijo: ai-. Respeta prefers-reduced-motion. */
(function () {
  'use strict';

  var raiz = document.getElementById('aiRaiz');
  if (!raiz) return;
  var D;
  try { D = JSON.parse(document.getElementById('aiDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  var TOPE = 60;

  function n(v, d) {
    return v.toLocaleString('es-MX', { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 });
  }
  function mdp(v) { return '$' + n(v, v < 100 ? 1 : 0) + ' mdp'; }
  function grande(v) { return v >= 1e6 ? '$' + n(v / 1e6, 2) + ' billones' : mdp(v); }
  function chip(e) { return '<span class="est-chip est-' + e + '">' + e + '</span>'; }
  function esc(v) {
    return String(v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* 1. ¿En cuántos años alcanzaría? */
  var g = $('aiG'), d = $('aiD');
  function alcanza() {
    var cg = parseFloat(g.value) / 100, cd = parseFloat(d.value) / 100;
    $('aiGVal').textContent = n(cg * 100, 1) + ' % al año';
    $('aiDVal').textContent = (cd < 0 ? '−' : '') + n(Math.abs(cd * 100), 1) + ' % al año';
    var anios = null, brecha = 0, filas = [];
    for (var t = 0; t <= TOPE; t++) {
      var gt = D.gpa * Math.pow(1 + cg, t), dt = D.dano * Math.pow(1 + cd, t);
      filas.push({ t: t, g: gt, d: dt });
      if (gt >= dt) { anios = t; break; }
      brecha += dt - gt;
    }
    var res;
    if (anios !== null) {
      res = '<p class="ai-grande-res"><b class="ai-num">' + anios + ' años</b> ' + chip('derivado') + '</p>' +
        '<p class="ai-txt">Con estos supuestos, el gasto en proteger alcanzaría al costo del daño en ' + (D.ej + anios) +
        '. Mientras tanto se acumularía una brecha de <b class="ai-num">' + grande(brecha) + '</b> ' + chip('derivado') +
        ': el daño de esos años que el gasto no alcanzó a igualar.</p>';
    } else if (cg <= cd) {
      res = '<p class="ai-grande-res"><b>Nunca</b> ' + chip('derivado') + '</p>' +
        '<p class="ai-txt">Si el daño crece igual o más rápido que el gasto en proteger, el gasto no lo alcanza: la brecha se mantiene o se abre. En ' +
        TOPE + ' años sumaría <b class="ai-num">' + grande(brecha) + '</b> ' + chip('derivado') + '.</p>';
    } else {
      res = '<p class="ai-grande-res"><b>Más de ' + TOPE + ' años</b> ' + chip('derivado') + '</p>' +
        '<p class="ai-txt">A ese ritmo, el gasto tardaría más de ' + TOPE + ' años en alcanzar al daño. En ese tiempo, la brecha acumulada sumaría <b class="ai-num">' +
        grande(brecha) + '</b> ' + chip('derivado') + '.</p>';
    }
    $('aiAlcRes').innerHTML = res;
    // La gráfica: hasta 12 renglones repartidos entre el inicio y el final.
    var paso = Math.max(1, Math.ceil((filas.length - 1) / 11)), muestra = [];
    for (var i = 0; i < filas.length; i += paso) muestra.push(filas[i]);
    if (muestra[muestra.length - 1] !== filas[filas.length - 1]) muestra.push(filas[filas.length - 1]);
    var tope = Math.max.apply(null, muestra.map(function (f) { return Math.max(f.g, f.d); }));
    $('aiGraf').innerHTML = '<div class="ai-ley"><span class="ai-ley-g">🛡️ Gasto en proteger</span><span class="ai-ley-d">🌫️ Costo del daño</span></div>' +
      muestra.map(function (f) {
        return '<div class="ai-fila"><span class="ai-anio">' + (D.ej + f.t) + '</span><span class="ai-barras">' +
          '<span class="ai-b ai-b-g" style="--ai-w:' + (f.g / tope).toFixed(4) + '"><i>' + grande(f.g) + '</i></span>' +
          '<span class="ai-b ai-b-d" style="--ai-w:' + (f.d / tope).toFixed(4) + '"><i>' + grande(f.d) + '</i></span></span></div>';
      }).join('');
    raiz.querySelectorAll('#aiAlcanza .ai-op').forEach(function (b) {
      b.setAttribute('aria-pressed', parseFloat(b.getAttribute('data-g')) === cg * 100 && parseFloat(b.getAttribute('data-d')) === cd * 100 ? 'true' : 'false');
    });
  }
  g.addEventListener('input', alcanza);
  d.addEventListener('input', alcanza);
  raiz.querySelectorAll('#aiAlcanza .ai-op').forEach(function (b) {
    b.addEventListener('click', function () { g.value = b.getAttribute('data-g'); d.value = b.getAttribute('data-d'); alcanza(); });
  });
  alcanza();

  /* 2. Si ese dinero fuera al ambiente */
  var monto = $('aiMonto');
  function equivale() {
    var v = Number(String(monto.value).replace(/[$,\s]/g, ''));
    var res = $('aiEqRes'), lista = $('aiOrgs');
    if (!isFinite(v) || v <= 0 || monto.value.trim() === '') {
      res.innerHTML = '<p class="ai-txt">Escribe una cantidad mayor que cero, en millones de pesos.</p>';
      lista.innerHTML = '';
      return;
    }
    var dias = v / (D.dano / 365);
    res.innerHTML = '<p class="ai-txt">Con <b class="ai-num">' + mdp(v) + '</b> se cubrirían <b class="ai-num">' + n(dias, dias < 10 ? 1 : 0) +
      ' días</b> del costo del daño ambiental de ' + D.ej + ' ' + chip('derivado') + '. En años del presupuesto 2026 de cada órgano:</p>';
    var filas = D.orgs.map(function (o) { return { o: o, a: v / o.v }; });
    var tope = Math.max.apply(null, filas.map(function (f) { return f.a; }));
    lista.innerHTML = filas.map(function (f) {
      var txt = f.a >= 1 ? n(f.a, f.a < 10 ? 1 : 0) + (f.a < 1.05 ? ' año' : ' años') :
        f.a * 12 >= 1 ? n(f.a * 12, 1) + ' meses' : n(f.a * 365, f.a * 365 < 10 ? 1 : 0) + ' días';
      return '<li class="ai-org"><span class="ai-org-n" title="' + esc(f.o.n || f.o.s) + '">' + esc(f.o.s) + '</span>' +
        '<span class="ai-org-riel"><span class="ai-org-b" style="--ai-w:' + Math.max(0.01, f.a / tope).toFixed(4) + '"></span></span>' +
        '<span class="ai-org-v ai-num">' + txt + ' ' + chip('derivado') + '</span></li>';
    }).join('');
    raiz.querySelectorAll('#aiEquivale .ai-op').forEach(function (b) {
      b.setAttribute('aria-pressed', Math.abs(parseFloat(b.getAttribute('data-mdp')) - v) < 0.05 ? 'true' : 'false');
    });
  }
  monto.addEventListener('input', equivale);
  raiz.querySelectorAll('#aiEquivale .ai-op').forEach(function (b) {
    b.addEventListener('click', function () { monto.value = n(parseFloat(b.getAttribute('data-mdp')), 1); equivale(); });
  });
  var primero = raiz.querySelector('#aiEquivale .ai-op');
  if (primero) monto.value = n(parseFloat(primero.getAttribute('data-mdp')), 1);
  equivale();
})();
