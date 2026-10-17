/* Auditavisión · Costo Ambiental › El reloj y el año (aplicación 1,
   16-10-2026). La página la escribe herramientas/am_reloj.py con todas
   las cifras, tablas, notas y remates ya puestos; aquí solo se mueven los
   contadores y se anima la simulación. En #arDatos van el daño por
   milisegundo y la basura por milisegundo (cifras anuales del INEGI y de
   la SEMARNAT repartidas en el tiempo, derivadas).
   El reloj se mide contra el reloj del sistema, no contando pulsos; la
   pausa congela el contador «desde que abriste» y Reiniciar lo devuelve a
   cero. Con prefers-reduced-motion el reloj avanza cada cinco segundos,
   las barras no se animan y «Simular un año» salta al cierre (como el
   motor). La vista elegida se recuerda en localStorage (av-am-reloj). */
(function () {
  'use strict';

  var D;
  try { D = JSON.parse(document.getElementById('arDatos').textContent); } catch (e) { return; }
  var raiz = document.getElementById('arRaiz');
  if (!raiz) return;
  var $ = function (id) { return document.getElementById(id); };
  var todos = function (sel, el) { return [].slice.call((el || raiz).querySelectorAll(sel)); };
  var quieto = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  if (quieto) raiz.classList.add('ar-quieta');

  /* ---------- formato (el mismo del motor) ---------- */
  function n(v, d) { return v.toLocaleString('es-MX', { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 }); }
  function pesos(v) { return '$' + Math.round(v).toLocaleString('es-MX'); }
  function mdpFijo(v) { var r = Math.round(v); return (r < 0 ? '-$' : '$') + Math.abs(r).toLocaleString('es-MX') + ' mdp'; }
  function pdMdp(p, d) { return '$' + n(p / 1e6, d == null ? 1 : d) + ' mdp'; }
  function lapso(s) {
    s = Math.floor(s);
    var h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60;
    return (h ? h + ' h ' : '') + (h || m ? m + ' min ' : '') + x + ' s';
  }

  /* ---------- 1. El reloj ---------- */
  var rel = { previo: 0, inicio: Date.now(), pausa: false, id: 0 };
  function segundos() { return rel.previo + (rel.pausa ? 0 : (Date.now() - rel.inicio) / 1000); }
  function pintarReloj() {
    var ms = segundos() * 1000;
    $('arDano').textContent = pesos(ms * D.porMs);
    $('arBasura').textContent = n(ms * D.kgMs, 0) + ' kg';
    var hoy = new Date();
    var ini = new Date(hoy.getFullYear(), 0, 1).getTime();
    $('arAnioActual').textContent = String(hoy.getFullYear());
    $('arAnioAcum').textContent = pdMdp((hoy.getTime() - ini) * D.porMs, 1);
    $('arLapso').textContent = lapso(ms / 1000);
  }
  function arrancar() {
    if (rel.id) clearInterval(rel.id);
    pintarReloj();
    rel.id = setInterval(pintarReloj, quieto ? 5000 : 100);
  }
  var bPausa = $('arRelPausa');
  bPausa.addEventListener('click', function () {
    if (rel.pausa) { rel.inicio = Date.now(); rel.pausa = false; }
    else { rel.previo = segundos(); rel.pausa = true; }
    bPausa.textContent = rel.pausa ? '▶ Seguir' : '❚❚ Pausa';
    bPausa.setAttribute('aria-pressed', String(rel.pausa));
    $('arEstado').textContent = rel.pausa ? '(en pausa)' : '';
    $('arPantalla').classList.toggle('ar-pausada', rel.pausa);
    pintarReloj();
  });
  $('arRelCero').addEventListener('click', function () {
    rel.previo = 0; rel.inicio = Date.now();
    pintarReloj();
  });
  /* En segundo plano el navegador frena los intervalos; al volver, se
     repinta de inmediato contra el reloj del sistema. */
  document.addEventListener('visibilitychange', function () { if (!document.hidden) pintarReloj(); });
  arrancar();

  /* ---------- 2. Un año en veinte segundos ---------- */
  var sim = { t: 0, raf: 0, vista: D.vistas[0] };
  var bPlay = $('arPlay'), dia = $('arDia');
  function panel() { return $('arVista-' + sim.vista); }

  function fechaDe(t) {
    if (t >= 1) return '31 de diciembre · año completo';
    var d = Math.min(364, Math.floor(t * 365));
    var f = new Date(2026, 0, 1 + d);
    return f.toLocaleDateString('es-MX', { day: 'numeric', month: 'long' }) + ' · día ' + (d + 1);
  }

  function pintar(t) {
    var p = panel();
    todos('.ar-fila', p).forEach(function (li) {
      var w = parseFloat(li.getAttribute('data-w')), v = parseFloat(li.getAttribute('data-v'));
      li.querySelector('.ar-barra').style.width = (w * t).toFixed(3) + '%';
      li.querySelector('.ar-val').textContent = mdpFijo(v * t);
    });
    var txt = fechaDe(t);
    $('arFecha').textContent = txt;
    dia.value = String(Math.round(t * 365));
    dia.setAttribute('aria-valuetext', txt.replace(' · ', ', '));
    dia.style.setProperty('--ar-avance', (t * 100).toFixed(2) + '%');
    var r = p.querySelector('[data-remate]');
    if (r) r.hidden = t < 1;
  }

  function boton(txt) { bPlay.textContent = txt; }
  function parar() { if (sim.raf) { cancelAnimationFrame(sim.raf); sim.raf = 0; } }

  function play() {
    if (sim.raf) { parar(); boton('▶ Seguir'); return; }
    if (quieto) { fin(); return; }
    if (sim.t >= 1) sim.t = 0;
    var ini = performance.now() - sim.t * D.durMs;
    boton('❚❚ Pausa');
    var paso = function (ahora) {
      sim.t = Math.min(1, (ahora - ini) / D.durMs);
      pintar(sim.t);
      if (sim.t < 1) sim.raf = requestAnimationFrame(paso);
      else { sim.raf = 0; boton('↻ Simular otra vez'); }
    };
    sim.raf = requestAnimationFrame(paso);
  }
  function fin() { parar(); sim.t = 1; pintar(1); boton('↻ Simular otra vez'); }
  function cero() { parar(); sim.t = 0; pintar(0); boton('▶ Simular un año'); }

  bPlay.addEventListener('click', play);
  $('arFin').addEventListener('click', fin);
  $('arCero').addEventListener('click', cero);
  dia.addEventListener('input', function () {
    parar();
    sim.t = Math.max(0, Math.min(1, parseInt(dia.value, 10) / 365));
    pintar(sim.t);
    boton(sim.t >= 1 ? '↻ Simular otra vez' : sim.t > 0 ? '▶ Seguir' : '▶ Simular un año');
  });

  /* Pestañas: cambiar de vista conserva el día en que va la simulación. */
  var tabs = todos('.ar-tab');
  function elegir(v, foco) {
    if (D.vistas.indexOf(v) < 0) v = D.vistas[0];
    sim.vista = v;
    tabs.forEach(function (b) {
      var si = b.getAttribute('data-vista') === v;
      b.setAttribute('aria-selected', String(si));
      b.tabIndex = si ? 0 : -1;
      if (si && foco) b.focus();
    });
    todos('.ar-vista').forEach(function (el) { el.hidden = el.getAttribute('data-vista') !== v; });
    pintar(sim.t);
    try { localStorage.setItem('av-am-reloj', JSON.stringify({ vista: v })); } catch (e) { /* sin memoria */ }
  }
  tabs.forEach(function (b, i) {
    b.addEventListener('click', function () { elegir(b.getAttribute('data-vista')); });
    b.addEventListener('keydown', function (ev) {
      var k = ev.key, j = -1;
      if (k === 'ArrowRight' || k === 'ArrowDown') j = (i + 1) % tabs.length;
      else if (k === 'ArrowLeft' || k === 'ArrowUp') j = (i - 1 + tabs.length) % tabs.length;
      else if (k === 'Home') j = 0;
      else if (k === 'End') j = tabs.length - 1;
      if (j < 0) return;
      ev.preventDefault();
      elegir(tabs[j].getAttribute('data-vista'), true);
    });
  });

  var inicial = new URLSearchParams(location.search).get('vista');
  if (!inicial) {
    try { inicial = (JSON.parse(localStorage.getItem('av-am-reloj') || '{}') || {}).vista; } catch (e) { inicial = null; }
  }
  elegir(inicial || D.vistas[0]);
})();
