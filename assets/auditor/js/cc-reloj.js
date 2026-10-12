/* Auditavisión · Calculadora Cívica › El reloj de la deuda y de lo
   perdido (aplicación 3, 12-10-2026). La página la escribe
   herramientas/cc_reloj.py con las cifras de arranque ya pintadas (al día,
   por habitante) y, en JSON (#crDatos), las cifras anuales con su estado:
   aquí no se escribe ninguna cifra nueva, solo se reparte la del documento
   entre la cadencia y las personas que elijas y se mueve el contador.
   El acumulado se mide contra el reloj del sistema, no contando pulsos,
   como ccTictac() del motor: cambiar un mando no lo devuelve a cero.
   Con prefers-reduced-motion el contador avanza una vez por segundo y las
   barras no se animan. */
(function () {
  'use strict';

  var D;
  try { D = JSON.parse(document.getElementById('crDatos').textContent); } catch (e) { return; }
  var raiz = document.getElementById('crRaiz');
  if (!raiz) return;
  var $ = function (id) { return document.getElementById(id); };
  var todos = function (sel) { return [].slice.call(raiz.querySelectorAll(sel)); };
  var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- formato (el mismo del motor) ---------- */
  function n(v, d) { return v.toLocaleString('es-MX', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function pesos(v) { return '$' + Math.round(v).toLocaleString('es-MX'); }
  function finos(v) { return Math.abs(v) < 1000 ? '$' + n(Math.round(v * 100) / 100, 2) : pesos(v); }
  function simMdp(v) {
    var a = Math.abs(v);
    if (a >= 1e6) return '$' + (v / 1e6).toFixed(2) + ' billones';
    if (a >= 1e3) return '$' + (Math.round(v / 100) / 10).toLocaleString('es-MX') + ' mil millones';
    return '$' + (Math.round(v * 100) / 100).toLocaleString('es-MX') + ' millones';
  }
  function vivo(v) { return '+$' + n(v, 2); }
  function lapso(s) {
    s = Math.floor(s);
    var h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60;
    return (h ? h + ' h ' : '') + (h || m ? m + ' min ' : '') + x + ' s';
  }
  function leer(txt) {
    var v = parseFloat(String(txt == null ? '' : txt).replace(/[^0-9.]/g, ''));
    return isFinite(v) && v > 0 ? v : 0;
  }

  /* ---------- estado ---------- */
  var mem = {};
  try { mem = JSON.parse(localStorage.getItem('crReloj') || '{}') || {}; } catch (e) { mem = {}; }
  var q = new URLSearchParams(location.search);
  var cadOk = function (c) { return D.cadencias.some(function (x) { return x.id === c; }); };
  var est = {
    cad: cadOk(q.get('cad')) ? q.get('cad') : cadOk(mem.cad) ? mem.cad : D.cadencias[0].id,
    den: D.den[q.get('den')] ? q.get('den') : D.den[mem.den] ? mem.den : 'habitante',
    fuera: Array.isArray(mem.fuera) ? mem.fuera.filter(function (id) { return D.relojes.some(function (r) { return r.id === id; }); }) : [],
    inicio: Date.now(), previo: 0, pausa: false
  };
  function guardar() {
    try { localStorage.setItem('crReloj', JSON.stringify({ cad: est.cad, den: est.den, fuera: est.fuera })); } catch (e) { /* sin memoria */ }
  }
  function segundos() { return est.previo + (est.pausa ? 0 : (Date.now() - est.inicio) / 1000); }
  function cadencia() { return D.cadencias.filter(function (c) { return c.id === est.cad; })[0] || D.cadencias[0]; }
  function personas() { return D.den[est.den].millones * 1e6; }
  function cuenta(r) { return est.fuera.indexOf(r.id) < 0; }
  function dentro() { return D.relojes.filter(cuenta); }
  function porSeg(lista) { return lista.reduce(function (a, r) { return a + r.anual * 1e6; }, 0) / D.segAno; }

  /* ---------- pintar lo que depende de los mandos ---------- */
  var tuIngreso = $('crNeto'), tuIsr = $('crIsr');
  function pintar() {
    var c = cadencia(), p = personas(), rot = D.den[est.den].rot, cadTx = c.nombre.toLowerCase();
    todos('[data-cad]').forEach(function (b) {
      if (b.tagName === 'BUTTON') b.setAttribute('aria-pressed', b.dataset.cad === est.cad ? 'true' : 'false');
    });
    todos('button[data-den]').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.den === est.den ? 'true' : 'false'); });
    todos('[data-cadtx]').forEach(function (el) { el.textContent = cadTx; });
    todos('[data-rotden]').forEach(function (el) { el.textContent = rot; });

    var enCad = D.relojes.map(function (r) { return r.anual * 1e6 / p * c.dias / 365; });
    var mayor = Math.max.apply(null, enCad) || 1;
    D.relojes.forEach(function (r, i) {
      var li = raiz.querySelector('.cr-card[data-id="' + r.id + '"]');
      if (!li) return;
      li.querySelector('[data-cad="' + r.id + '"]').textContent = finos(enCad[i]);
      li.querySelector('[data-rot]').textContent = cadTx + ', ' + rot;
      li.querySelector('[data-barra="' + r.id + '"]').style.width = (enCad[i] / mayor * 100).toFixed(1) + '%';
      li.querySelector('[data-anual="' + r.id + '"]').textContent = pesos(r.anual * 1e6 / p);
      var caja = li.querySelector('[data-incluye]');
      if (caja) caja.checked = cuenta(r);
      li.classList.toggle('cr-fuera', !cuenta(r));
    });

    var lista = dentro();
    var anual = lista.reduce(function (a, r) { return a + r.anual * 1e6; }, 0);
    var pers = anual / p;
    var palabras = ['ninguna', 'una', 'dos', 'tres', 'cuatro', 'cinco'];
    $('crCuantas').textContent = palabras[lista.length] || String(lista.length);
    $('crTotCad').textContent = finos(pers * c.dias / 365);
    $('crTotAno').textContent = pesos(pers);
    $('crTotPais').textContent = simMdp(anual / 1e6);
    $('crPorSeg').textContent = finos(porSeg(lista));
    $('crEqTuAno').textContent = pesos(pers);
    $('crEqTuSm').textContent = n(Math.round(pers / D.smDia * 10) / 10, 1);
    $('crSobPers').textContent = pesos(D.sobrecosto * 1e6 / p);
    personal(pers);
    tic(true);
  }

  /* ---------- puesto junto a lo tuyo ---------- */
  function personal(pers) {
    var out = $('crPersonal');
    var neto = leer(tuIngreso.value), isr = leer(tuIsr.value);
    if (!neto) {
      out.textContent = 'Cuando escribas tu ingreso, esta línea dirá a cuántos días de lo que ganas equivale tu parte.';
      return;
    }
    var anualNeto = neto * 12;
    var dias = pers / (anualNeto / 365);
    var html = '<strong>Tu parte de estas cuentas es ' + pesos(pers) + ' al año</strong> (' + D.den[est.den].rot + '). ' +
      'Con un ingreso neto de ' + pesos(anualNeto) + ' anuales, equivale a <strong>' + n(dias, 1) + ' días</strong> de todo lo que ganas';
    if (isr) html += '; y frente a los ' + pesos(isr) + ' que pagas de ISR, es <strong>' + n(pers / isr, 2) + ' veces</strong> esa cantidad.';
    else html += '.';
    out.innerHTML = html + ' <span class="est-chip est-derivado">derivado</span>';
  }
  [tuIngreso, tuIsr].forEach(function (el) {
    el.addEventListener('input', function () { personal(dentro().reduce(function (a, r) { return a + r.anual * 1e6; }, 0) / personas()); });
  });
  if (q.get('neto')) tuIngreso.value = q.get('neto');
  if (q.get('isr')) tuIsr.value = q.get('isr');

  /* ---------- el contador ---------- */
  var nodos = {
    total: $('crVivoTotal'), tuyo: $('crVivoTuyo'), tiempo: $('crTiempo'),
    sm: $('crEqSm'), uma: $('crEqUma'), anio: $('crEqAnio'),
    cards: D.relojes.map(function (r) { return raiz.querySelector('[data-vivo="' + r.id + '"]'); })
  };
  var inicioAnio = new Date(D.anioRitmo, 0, 1).getTime();
  function tic(forzar) {
    if (!forzar && (est.pausa || document.hidden)) return;
    var s = segundos(), lista = dentro(), rs = porSeg(lista), acum = s * rs;
    nodos.total.textContent = vivo(acum);
    var tu = acum / personas();
    nodos.tuyo.textContent = '+$' + n(tu, tu < 1 ? 4 : 2);
    nodos.tiempo.textContent = lapso(s);
    D.relojes.forEach(function (r, i) {
      if (nodos.cards[i]) nodos.cards[i].textContent = vivo(s * r.anual * 1e6 / D.segAno);
    });
    nodos.sm.textContent = n(acum / D.smDia, 1);
    nodos.uma.textContent = n(acum / D.umaDia, 1);
    var ahora = est.pausa ? est.congelado || Date.now() : Date.now();
    var transcurrido = Math.min(D.segAno, Math.max(0, (ahora - inicioAnio) / 1000));
    nodos.anio.textContent = simMdp(rs * transcurrido / 1e6);
  }
  var timer = setInterval(tic, quieto ? 1000 : 200);
  document.addEventListener('visibilitychange', function () { if (!document.hidden) tic(true); });

  /* ---------- mandos ---------- */
  raiz.addEventListener('click', function (ev) {
    var b = ev.target.closest ? ev.target.closest('button') : null;
    if (!b || !raiz.contains(b)) return;
    if (b.dataset.cad) { est.cad = b.dataset.cad; guardar(); pintar(); }
    else if (b.dataset.den) { est.den = b.dataset.den; guardar(); pintar(); }
  });
  raiz.addEventListener('change', function (ev) {
    var c = ev.target;
    if (!c.dataset || !c.dataset.incluye) return;
    var id = c.dataset.incluye;
    est.fuera = est.fuera.filter(function (x) { return x !== id; });
    if (!c.checked) est.fuera.push(id);
    guardar();
    pintar();
  });

  var bPausa = $('crPausa'), aviso = $('crQuieto');
  bPausa.addEventListener('click', function () {
    if (est.pausa) {
      est.pausa = false;
      est.inicio = Date.now();
      est.congelado = null;
      aviso.textContent = 'El reloj sigue corriendo.';
    } else {
      est.previo = segundos();
      est.pausa = true;
      est.congelado = Date.now();
      tic(true);
      aviso.textContent = 'En pausa: en ' + lapso(est.previo) + ' el país llevaba ' + nodos.total.textContent.replace('+', '') +
        ' y tu parte, ' + nodos.tuyo.textContent.replace('+', '') + '.';
    }
    bPausa.setAttribute('aria-pressed', est.pausa ? 'true' : 'false');
    bPausa.innerHTML = est.pausa ? '<span aria-hidden="true">▶️</span> <span>Seguir</span>' : '<span aria-hidden="true">⏸️</span> <span>Pausa</span>';
    tic(true);
  });
  $('crCero').addEventListener('click', function () {
    est.previo = 0;
    est.inicio = Date.now();
    if (est.pausa) est.congelado = Date.now();
    aviso.textContent = 'El reloj volvió a cero.';
    tic(true);
  });

  if (quieto) raiz.classList.add('cr-quieta');
  pintar();
}());
