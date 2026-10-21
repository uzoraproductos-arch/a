/* Auditavisión · Inversión y Megaobras › El pulso del gasto (aplicación 1,
   13-10-2026). La página la escribe herramientas/mo_pulso.py con las cifras
   ya puestas y, en JSON (#mpDatos), los mismos agregados con su estado:
   aquí no se inventa ninguna cifra, solo se reparte en la cadencia elegida
   y se ordenan las obras. No carga el motor. Prefijo: mp-. */
(function () {
  'use strict';

  var D;
  try { D = JSON.parse(document.getElementById('mpDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  var raiz = $('mpRaiz');
  if (!raiz) return;
  /* Desde el 17-10-2026 cada parte vive en su página: las anclas viejas
     (#mpCifras…) llevan a ella sin dejar un paso de más en el historial. */
  var PARTES = { mpCifras: 'herramienta-megaobras-cero.html#mpCifras', mpRitmo: 'herramienta-megaobras-pulso-cuenta.html#mpRitmo', mpCompo: 'herramienta-megaobras-sector.html#mpCompo', mpComo: 'herramienta-megaobras-cero.html#como-se-calcula', mpCuenta: 'herramienta-megaobras-pulso-cuenta.html#mpCuenta' };
  var vieja = PARTES[location.hash.slice(1)];
  if (vieja && !$(location.hash.slice(1))) { location.replace(vieja); return; }
  /* Escribe solo si el elemento está en esta página. */
  function pon(id, prop, v) { var el = $(id); if (el) el[prop] = v; }

  var LS = 'av-mo-pulso-';
  function lee(k, def) { try { return localStorage.getItem(LS + k) || def; } catch (e) { return def; } }
  function guarda(k, v) { try { localStorage.setItem(LS + k, v); } catch (e) { /* sin almacenamiento */ } }

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function num(n) { return Number(n).toLocaleString('es-MX'); }
  /* simMdp() del motor. */
  function simMdp(n) {
    var a = Math.abs(n);
    if (a >= 1000000) return '$' + (n / 1000000).toFixed(2) + ' billones';
    if (a >= 1000) return '$' + num(Math.round(n / 100) / 10) + ' mil millones';
    return '$' + num(Math.round(n * 100) / 100) + ' millones';
  }
  function mdp(v, d) {
    d = d == null ? 1 : d;
    return (v < 0 ? '−' : '') + '$' + Math.abs(v).toLocaleString('es-MX', { minimumFractionDigits: d, maximumFractionDigits: d }) + ' mdp';
  }
  function pesos2(v) { return '$' + v.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function chip(e, pend) {
    return '<span class="est-chip est-' + e + '"' + (pend ? ' data-pend="' + esc(pend) + '"' : '') + '>' + e + '</span>';
  }
  var FACTOR_TX = { dia: '1/365', mes: '1/12', trimestre: '1/4', semestre: '1/2', ano: '1' };

  /* ---------- 1. La cadencia ---------- */
  var periodo = D.periodos[lee('periodo', 'dia')] ? lee('periodo', 'dia') : 'dia';
  var dialBs = [].slice.call(raiz.querySelectorAll('.mp-dial-b'));
  var filasComp = [].slice.call(raiz.querySelectorAll('#mpComps tbody tr[data-v]'));

  function pintaPeriodo() {
    var p = D.periodos[periodo];
    var v = D.anual * p.factor;
    dialBs.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.per === periodo ? 'true' : 'false'); });
    pon('mpKPerEt', 'textContent', '(' + p.label + ')');
    pon('mpKPer', 'textContent', simMdp(v) + p.sufijo);
    pon('mpKPerMdp', 'textContent', mdp(v, 2) + p.sufijo);
    pon('mpCompsEt', 'textContent', p.sufijo);
    pon('mpFactorTx', 'textContent', FACTOR_TX[periodo] || String(p.factor));
    pon('mpCompsTot', 'textContent', simMdp(v) + p.sufijo);
    /* La medida única (21-10-2026): v > 0 pierde, v < 0 gana. */
    filasComp.forEach(function (tr) {
      var v = Number(tr.dataset.v);
      tr.querySelector('.mp-c-v').textContent = (v > 0 ? 'Pierde ' : 'Gana ') + simMdp(Math.abs(v) * p.factor) + p.sufijo;
    });
    var hora = D.anual * 1e6 / (365 * 24), minuto = hora / 60;
    if ($('mpEquiv')) $('mpEquiv').innerHTML = 'Lo leas como lo leas, el ritmo es el mismo: <b class="mp-num">' + esc(pesos2(Math.round(hora * 100) / 100)) +
      '</b> cada hora y <b class="mp-num">' + esc(pesos2(Math.round(minuto * 100) / 100)) + '</b> cada minuto ' + chip('derivado') +
      ' (cifra anual ÷ 8,760 horas o ÷ 525,600 minutos de un año de 365 días).';
  }
  dialBs.forEach(function (b) {
    b.addEventListener('click', function () { periodo = b.dataset.per; guarda('periodo', periodo); pintaPeriodo(); });
  });

  /* ---------- 2. Todo lo registrado o solo con documento ----------
     Se quitó el 21-10-2026 (pedido del autor: un solo filtro en toda la
     herramienta); las cuatro cifras miden siempre el universo completo. */

  /* ---------- 3. Las obras, ordenadas ---------- */
  var ORDENES = {
    real: function (o) { return o.real; },
    sobre: function (o) { return o.sobre; },
    brecha: function (o) { return o.real - o.presu; },
    perd: function (o) { return o.perd; }
  };
  var orden = ORDENES[lee('orden', 'real')] ? lee('orden', 'real') : 'real';
  var ordenBs = [].slice.call(raiz.querySelectorAll('.mp-orden-b'));
  var lista = $('mpObras');

  function cifra(o) {
    if (orden === 'sobre') return { t: (o.sobre > 0 ? '+' : '') + o.sobre + '%', e: o.es };
    if (orden === 'brecha') { var b = o.real - o.presu; return { t: (b > 0 ? '+' : '') + mdp(b), e: o.er === 'pendiente' || o.ep === 'pendiente' ? 'pendiente' : 'derivado' }; }
    if (orden === 'perd') {
      if (o.epd === 'pendiente') return { t: 'no lo publica', e: 'pendiente', pend: 'cuenta-' + o.id };
      if (o.epd === 'no_aplica') return { t: 'no opera', e: 'na' };
      return { t: (o.perd > 0 ? 'pierde ' : 'gana ') + mdp(Math.abs(o.perd)) + '/año', e: o.epd };
    }
    return { t: mdp(o.real), e: o.er };
  }
  function pintaObras() {
    if (!lista) return;
    ordenBs.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.orden === orden ? 'true' : 'false'); });
    var f = ORDENES[orden];
    var obras = D.obras.slice().sort(function (a, b) {
      var pa = orden === 'perd' && (a.epd === 'pendiente' || a.epd === 'no_aplica'), pb = orden === 'perd' && (b.epd === 'pendiente' || b.epd === 'no_aplica');
      if (pa !== pb) return pa ? 1 : -1;
      return f(b) - f(a);
    });
    var max = Math.max.apply(null, obras.map(function (o) { return Math.abs(f(o)); })) || 1;
    lista.innerHTML = obras.map(function (o) {
      var c = cifra(o);
      var pend = c.pend || (c.e === 'pendiente' ? 'obra-' + o.id : '');
      var ancho = Math.max(0, f(o)) / max * 100;
      return '<li class="mp-obra mp-obra-' + c.e + '">' +
        '<div class="mp-obra-cab"><span class="mp-obra-ico" aria-hidden="true">' + esc(o.ico) + '</span>' +
          '<span class="mp-obra-n">' + esc(o.n) + '<small>' + esc(o.pres) + ' · ' + esc(o.per) + '</small></span>' +
          '<span class="mp-obra-v"><b class="mp-num">' + esc(c.t) + '</b> ' + (c.e === 'na' ? '' : chip(c.e, pend)) + '</span></div>' +
        '<span class="mp-riel" aria-hidden="true"><span class="mp-barra" style="width:' + ancho.toFixed(1) + '%"></span></span>' +
        '<p class="mp-obra-pie">Aprobado ' + esc(mdp(o.presu)) + ' ' + chip(o.ep, o.ep === 'pendiente' ? 'obra-' + o.id : '') +
          ' · erogado ' + esc(mdp(o.real)) + ' ' + chip(o.er, o.er === 'pendiente' ? 'obra-' + o.id : '') +
          (o.u ? ' · <a href="' + esc(o.u) + '" target="_blank" rel="noopener">' + esc(o.f.length > 70 ? o.f.slice(0, 68) + '…' : o.f) + ' ↗</a>' : '') + '</p>' +
      '</li>';
    }).join('');
  }
  ordenBs.forEach(function (b) {
    b.addEventListener('click', function () { orden = b.dataset.orden; guarda('orden', orden); pintaObras(); });
  });

  /* ---------- 4. CSV en el navegador ---------- */
  if ($('mpCsv')) $('mpCsv').addEventListener('click', function () {
    var q = function (v) { return '"' + String(v == null ? '' : v).replace(/"/g, '""') + '"'; };
    var filas = [['obra', 'presidente', 'periodo', 'aprobado_mdp', 'estado_aprobado', 'erogado_mdp', 'estado_erogado',
      'sobrecosto_pct', 'estado_sobrecosto', 'ganancia_o_perdida_anual_mdp', 'estado_ganancia_o_perdida', 'fuente', 'url']];
    D.obras.forEach(function (o) {
      var sin = o.epd === 'pendiente' || o.epd === 'no_aplica';
      filas.push([o.n, o.pres, o.per, o.presu, o.ep, o.real, o.er, o.sobre, o.es, sin ? '' : -o.perd, o.epd, o.f, o.u]);
    });
    var csv = '﻿' + filas.map(function (r) { return r.map(q).join(','); }).join('\r\n');
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    a.download = 'auditavision-pulso-megaobras.csv';
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  });

  /* ---------- 5. El contador en vivo ---------- */
  var vivo = $('mpVivo'), pausaB = $('mpPausa');
  if (!vivo || !pausaB) { pintaPeriodo(); pintaObras(); return; }
  var acumulado = 0, desde = Date.now(), pausado = false;
  var flota = document.createElement('a');
  flota.className = 'mp-flota';
  flota.href = '#mpPantalla';
  flota.hidden = true;
  flota.innerHTML = '<span class="mp-punto" aria-hidden="true"></span><span class="mp-flota-et">Desde que llegaste</span> <b class="mp-num" id="mpFlotaV"></b>';
  raiz.appendChild(flota);
  /* Volver al contador sin sumar un paso al historial (botón Atrás). */
  flota.addEventListener('click', function (ev) {
    ev.preventDefault();
    $('mpPantalla').scrollIntoView({ behavior: 'smooth', block: 'start' });
    pausaB.focus({ preventScroll: true });
  });
  var flotaV = $('mpFlotaV');

  function segundos() { return acumulado + (pausado ? 0 : (Date.now() - desde) / 1000); }
  function tic() {
    var t = '+' + pesos2(segundos() * D.seg);
    vivo.textContent = t;
    flotaV.textContent = t;
  }
  pausaB.addEventListener('click', function () {
    if (pausado) { desde = Date.now(); pausado = false; }
    else { acumulado = segundos(); pausado = true; }
    pausaB.setAttribute('aria-pressed', pausado ? 'true' : 'false');
    pausaB.querySelector('span[aria-hidden]').textContent = pausado ? '▶️' : '⏸️';
    pausaB.lastElementChild.textContent = pausado ? 'Reanudar' : 'Pausar';
    tic();
  });
  $('mpCero').addEventListener('click', function () { acumulado = 0; desde = Date.now(); tic(); });
  tic();
  setInterval(tic, 250);

  if (typeof IntersectionObserver === 'function') {
    new IntersectionObserver(function (ents) {
      flota.hidden = ents[0].isIntersecting || ents[0].boundingClientRect.top > 0;
    }, { threshold: 0 }).observe($('mpPantalla'));
  }

  pintaPeriodo();
  pintaObras();
})();
