/* Garantías cívicas (garantias.html, 10-10-2026): la brújula de denuncia,
   las cartas de las diez garantías y el reto «¿Mito o realidad?».
   Los textos vienen de window.AUDIT_DB por herramientas/apartados.py
   (garantias()), en el JSON #grDatos: aquí no se escribe ningún texto legal. */
(function () {
  'use strict';
  var nodo = document.getElementById('grDatos');
  if (!nodo) return;
  var D;
  try { D = JSON.parse(nodo.textContent); } catch (e) { return; }

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------- La brújula ---------------- */
  var caja = document.getElementById('grBrujula');
  var estado = { que: null, prueba: null, nombre: null };

  function etapa(n) {
    caja.querySelectorAll('.gr-etapa').forEach(function (e) {
      var on = Number(e.getAttribute('data-etapa')) === n;
      e.hidden = !on;
      if (on) { e.classList.remove('gr-entra'); void e.offsetWidth; e.classList.add('gr-entra'); }
    });
    caja.querySelectorAll('.gr-pasos li').forEach(function (li, i) {
      li.classList.toggle('gr-paso-on', i === n - 1);
      li.classList.toggle('gr-paso-hecho', i < n - 1);
    });
    var y = caja.getBoundingClientRect().top + window.scrollY - 100;
    if (Math.abs(window.scrollY - y) > 200) window.scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
    var foco = caja.querySelector('.gr-etapa:not([hidden]) .gr-preg, .gr-etapa:not([hidden]) h3');
    if (foco) { foco.setAttribute('tabindex', '-1'); foco.focus({ preventScroll: true }); }
  }

  function tarjeta(id, paso, titulo, nota) {
    var c = D.canales[id];
    if (!c) return '';
    var acceso = c.url
      ? '<a class="sz-btn sz-btn-of" href="' + esc(c.url) + '" target="_blank" rel="noopener noreferrer">Abrir el canal oficial ↗</a>'
      : '<span class="gr-sin-url">' + esc(c.notaSinUrl) + '</span>';
    return '<article class="gr-res-paso">' +
      '<span class="gr-res-num">Paso ' + paso + '</span>' +
      '<p class="gr-res-tit">' + titulo + '</p>' +
      '<div class="gr-res-canal"><span class="gr-res-ico" aria-hidden="true">' + esc(c.icono) + '</span>' +
        '<div><h4>' + esc(c.organismo) + ' <span class="gr-siglas">' + esc(c.siglas) + '</span></h4>' +
        '<span class="gr-herr">' + esc(c.herramienta) + '</span></div></div>' +
      (nota ? '<p class="gr-res-nota">' + nota + '</p>' : '') +
      '<dl class="gr-datos">' +
        '<div><dt>¿Sin dar tu nombre?</dt><dd>' + esc(c.anonimo) + '</dd></div>' +
        '<div><dt>Qué llevar</dt><dd>' + esc(c.queNecesitas) + '</dd></div>' +
        '<div><dt>Qué produce</dt><dd>' + esc(c.efecto) + '</dd></div>' +
      '</dl>' +
      '<p class="gr-res-acc">' + acceso + ' <a class="gr-ficha" href="#puerta-' + esc(id) + '">Ver su ficha ↓</a></p>' +
    '</article>';
  }

  function resultado() {
    var q = D.que.filter(function (x) { return x.id === estado.que; })[0];
    if (!q) return;
    var pasos = [], n = 1;
    if (estado.prueba === 'no') {
      pasos.push(tarjeta('ch-pnt', n++, '🔎 Primero, consigue la prueba',
        'Pide por escrito el contrato, la factura o el acta. No tienes que decir para qué la quieres.'));
    }
    var nota = '';
    if (estado.nombre === 'oculto' && q.canal === 'ch-fgr') {
      nota = '⚠️ La denuncia penal pide tus datos. Si temes represalias, la plataforma de alertadores de la SABG (abajo) está hecha para protegerte.';
    }
    pasos.push(tarjeta(q.canal, n++, estado.prueba === 'no' ? '🚪 Con la prueba, toca esta puerta' : '🚪 Esta es tu puerta', nota));
    if (estado.nombre === 'oculto' && q.canal === 'ch-fgr') {
      pasos.push(tarjeta('ch-sabg', n++, '🛡️ Si prefieres no exponerte', ''));
    }
    document.getElementById('grRuta').innerHTML =
      '<h3 class="gr-preg">Tu ruta, en ' + pasos.length + (pasos.length === 1 ? ' paso' : ' pasos') + '</h3>' +
      '<div class="gr-res-pasos">' + pasos.join('') + '</div>';
    etapa(4);
  }

  if (caja) {
    caja.addEventListener('click', function (ev) {
      var b = ev.target.closest('button');
      if (!b || !caja.contains(b)) return;
      if (b.hasAttribute('data-que')) { estado.que = b.getAttribute('data-que'); etapa(2); }
      else if (b.hasAttribute('data-prueba')) { estado.prueba = b.getAttribute('data-prueba'); etapa(3); }
      else if (b.hasAttribute('data-nombre')) { estado.nombre = b.getAttribute('data-nombre'); resultado(); }
      else if (b.hasAttribute('data-atras')) { etapa(Number(b.getAttribute('data-atras'))); }
      else if (b.id === 'grOtra') { estado = { que: null, prueba: null, nombre: null }; etapa(1); }
    });
  }

  /* Al saltar a la ficha de una puerta, se resalta un momento. */
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest('a.gr-ficha');
    if (!a) return;
    var dest = document.querySelector(a.getAttribute('href'));
    if (!dest) return;
    ev.preventDefault();
    var y = dest.getBoundingClientRect().top + window.scrollY - 90;
    window.scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
    var det = dest.querySelector('details');
    if (det) det.open = true;
    dest.classList.add('gr-destacada');
    setTimeout(function () { dest.classList.remove('gr-destacada'); }, 1600);
  });

  /* ---------------- Las cartas ---------------- */
  var cartas = document.querySelector('.gr-cartas');
  if (cartas) {
    cartas.classList.add('gr-js');
    cartas.addEventListener('click', function (ev) {
      var b = ev.target.closest('.gr-carta');
      if (!b) return;
      var on = b.getAttribute('aria-pressed') !== 'true';
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  /* ---------------- ¿Mito o realidad? ---------------- */
  var reto = document.getElementById('grReto');
  var R = D.reto || [];
  var i = 0, aciertos = 0;
  function pinta() {
    var af = document.getElementById('grRetoAf');
    var exp = document.getElementById('grRetoExp');
    document.getElementById('grRetoAvance').textContent = 'Pregunta ' + (i + 1) + ' de ' + R.length;
    document.getElementById('grRetoPuntos').textContent = 'Aciertos: ' + aciertos;
    document.getElementById('grRetoBarra').style.width = (i / R.length * 100) + '%';
    af.textContent = '«' + R[i].a + '»';
    af.classList.remove('gr-entra'); void af.offsetWidth; af.classList.add('gr-entra');
    exp.hidden = true; exp.innerHTML = '';
    reto.querySelectorAll('.gr-reto-btn').forEach(function (b) { b.disabled = false; b.classList.remove('gr-bien', 'gr-mal'); });
    reto.querySelector('.gr-reto-ops').hidden = false;
  }
  function final() {
    var msg = aciertos === R.length ? '🏆 Perfecto: conoces tus garantías.'
      : aciertos >= R.length - 2 ? '👏 Muy bien: ya sabes defenderte.'
      : '📚 Vale la pena repasar las diez garantías de arriba.';
    document.getElementById('grRetoBarra').style.width = '100%';
    document.getElementById('grRetoAvance').textContent = 'Terminaste';
    document.getElementById('grRetoPuntos').textContent = 'Aciertos: ' + aciertos + ' de ' + R.length;
    document.getElementById('grRetoAf').textContent = 'Acertaste ' + aciertos + ' de ' + R.length + '. ' + msg;
    reto.querySelector('.gr-reto-ops').hidden = true;
    var exp = document.getElementById('grRetoExp');
    exp.hidden = false;
    exp.innerHTML = '<p class="gr-reto-acc"><button type="button" class="sz-btn sz-btn-of" id="grRetoOtra">🔄 Jugar otra vez</button> ' +
      '<a class="sz-btn" href="#derechos">Repasar las diez garantías</a></p>';
  }
  if (reto && R.length) {
    reto.addEventListener('click', function (ev) {
      var b = ev.target.closest('button');
      if (!b) return;
      if (b.id === 'grRetoOtra') { i = 0; aciertos = 0; pinta(); return; }
      if (b.id === 'grRetoSig') { i++; if (i < R.length) pinta(); else final(); return; }
      if (!b.classList.contains('gr-reto-btn') || b.disabled) return;
      var item = R[i];
      var dijo = b.getAttribute('data-r') === '1';
      var bien = dijo === item.r;
      if (bien) aciertos++;
      reto.querySelectorAll('.gr-reto-btn').forEach(function (x) {
        x.disabled = true;
        if ((x.getAttribute('data-r') === '1') === item.r) x.classList.add('gr-bien');
        else if (x === b) x.classList.add('gr-mal');
      });
      document.getElementById('grRetoPuntos').textContent = 'Aciertos: ' + aciertos;
      var exp = document.getElementById('grRetoExp');
      exp.hidden = false;
      exp.innerHTML =
        '<p class="gr-reto-ver ' + (bien ? 'gr-reto-ok' : 'gr-reto-no') + '">' + (bien ? '✔ ¡Bien!' : '✘ No.') +
          ' Es <b>' + (item.r ? 'realidad' : 'mito') + '</b>.</p>' +
        '<p>' + esc(item.x) + '</p>' +
        '<p class="gr-reto-fund">📜 ' + esc(item.f) + (item.u ? ' · <a href="' + esc(item.u) + '" target="_blank" rel="noopener noreferrer">ver la ley ↗</a>' : '') + '</p>' +
        '<p class="gr-reto-de">' + esc(item.de) + '</p>' +
        '<p class="gr-reto-acc"><button type="button" class="sz-btn sz-btn-of" id="grRetoSig">' +
          (i + 1 < R.length ? 'Siguiente ➔' : 'Ver mi resultado ➔') + '</button></p>';
      var sig = document.getElementById('grRetoSig');
      if (sig) sig.focus({ preventScroll: true });
    });
    pinta();
  }
})();
