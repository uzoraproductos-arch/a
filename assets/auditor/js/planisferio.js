/* Auditavisión · Planisferio (02-11-2026, pedido del autor).
   Las páginas llegan escritas por herramientas/planisferio.py, con sus
   cifras en JSON dentro de la página: aquí no se escribe ninguna cifra.
   Este archivo solo las mueve:
   1. los contadores (cifra anual ÷ 31,536,000 s: derivado, no dinero en
      tiempo real),
   2. el mapa: dimensiones, los tres presupuestos, colores, ficha y portal,
   3. en cada portal, el buscador y el orden de sus municipios. */
(function () {
  'use strict';

  var SEG = 31536000;
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function num(v, d) { return v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function mdp(v) { return v == null ? '—' : '$' + num(v, 1) + ' mdp'; }
  function chip(e, pend) {
    return '<span class="est-chip est-' + e + '"' + (pend ? ' data-pend="' + esc(pend) + '"' : '') + '>' + e + '</span>';
  }
  function plano(t) { return String(t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }

  /* 1 · Los contadores ------------------------------------------------ */
  (function () {
    var cs = document.querySelectorAll('.pl-cont[data-anual]');
    if (!cs.length) return;
    var t0 = Date.now(), quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var items = Array.prototype.map.call(cs, function (c) {
      return { s: parseFloat(c.getAttribute('data-anual')) * 1e6 / SEG, n: c.querySelector('.pl-vivo') };
    });
    function paso() {
      var seg = (Date.now() - t0) / 1000;
      items.forEach(function (x) { if (x.n) x.n.textContent = '$' + num(Math.round(x.s * seg), 0); });
    }
    paso();
    setInterval(paso, quieto ? 1000 : 200);
  })();

  /* 2 · El mapa -------------------------------------------------------- */
  (function () {
    var nodo = document.getElementById('plDatos');
    if (!nodo) return;
    var D;
    try { D = JSON.parse(nodo.textContent); } catch (e) { return; }
    var PAL = {
      oro: ['#fbf3dc', '#f0d98f', '#d9b34f', '#a8801f', '#6b4f0c'],
      azul: ['#e3ecf8', '#b4c9ea', '#6f95d2', '#2f5fa8', '#0b2a63'],
      verde: ['#e4f3e8', '#b3dcbd', '#6dba82', '#2e8a4c', '#0f5128'],
      rojo: ['#fbe5e2', '#f2b3aa', '#e06f60', '#b3261e', '#6e1510']
    };
    var porA = {}, lente = D.lentes[0], sel = null, dimP = lente.dim, ultima = {};
    function fmt(v, l) {
      l = l || lente;
      if (v == null) return '—';
      if (l.fmt === 'pct') return num(v, 1) + '%';
      if (l.fmt === 'pct2') return num(v, 2) + '%';
      if (l.fmt === 'pesos') return '$' + num(v, 0);
      if (l.fmt === 'n') return num(v, 0);
      if (l.fmt === 'mbd') return num(v, 0) + ' mil b/d';
      if (l.fmt === 'mbd1') return num(v, 1) + ' mil b/d';
      if (l.fmt === 'ha') return num(v, 0) + ' ha';
      if (l.fmt === 'hm3') return num(v, 1) + ' hm³';
      if (l.fmt === 't') return num(v, 0) + ' t';
      if (l.fmt === 'dec2') return num(v, 2);
      return mdp(v);
    }
    D.e.forEach(function (e) { porA[e.a] = e; });
    var paths = document.querySelectorAll('.pl-edo');
    var ficha = document.getElementById('plFicha'), aviso = document.getElementById('plDimAviso');

    function cortes() {
      var v = D.e.map(function (e) { return e[lente.id]; }).filter(function (x) { return x != null; }).sort(function (a, b) { return a - b; });
      return [1, 2, 3, 4].map(function (k) { return v[Math.round(k * v.length / 5)]; });
    }
    function clase(v, c) {
      if (v == null) return -1;
      var i = 0;
      while (i < 4 && v >= c[i]) i++;
      return i;
    }
    /* Las refinerías se marcan con un punto en el centro de su entidad (no en
       el sitio exacto); el punto se toca igual que la entidad. */
    var svg = document.querySelector('.pl-svg'), marcas = null;
    function marca() {
      if (!svg) return;
      if (!marcas) {
        marcas = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        marcas.setAttribute('class', 'pl-marcas');
        Array.prototype.forEach.call(paths, function (p) {
          var e = porA[p.getAttribute('data-a')];
          if (!e || !e.ref) return;
          /* El centro del recuadro puede caer fuera de una entidad curva
             (Veracruz): se busca el punto más cercano a él que sí esté dentro. */
          var b = p.getBBox(), c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
          var cx = b.x + b.width / 2, cy = b.y + b.height / 2, mejor = null;
          if (p.isPointInFill && svg.createSVGPoint) {
            var pt = svg.createSVGPoint();
            for (var i = 0; i <= 20; i++) for (var j = 0; j <= 20; j++) {
              pt.x = b.x + b.width * i / 20; pt.y = b.y + b.height * j / 20;
              var dd = (pt.x - cx) * (pt.x - cx) + (pt.y - cy) * (pt.y - cy);
              if ((!mejor || dd < mejor[2]) && p.isPointInFill(pt)) mejor = [pt.x, pt.y, dd];
            }
          }
          if (mejor) { cx = mejor[0]; cy = mejor[1]; }
          c.setAttribute('cx', cx.toFixed(1));
          c.setAttribute('cy', cy.toFixed(1));
          c.setAttribute('r', '7');
          c.setAttribute('class', 'pl-ind');
          c.setAttribute('tabindex', '0');
          c.setAttribute('role', 'button');
          c.setAttribute('aria-label', e.ref.n + ', ' + e.n + ': ' + num(e.ref.jun, 0) + ' mil barriles diarios en junio de 2026');
          var t = document.createElementNS('http://www.w3.org/2000/svg', 'title');
          t.textContent = e.ref.n + ' · ' + e.ref.sede;
          c.appendChild(t);
          c.addEventListener('click', function () { elige(e.a, true); });
          c.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); elige(e.a, true); } });
          marcas.appendChild(c);
        });
        svg.appendChild(marcas);
      }
      marcas.style.display = dimP === 'ambiental' && /^ref/.test(lente.id) ? '' : 'none';
    }
    function pinta() {
      marca();
      var c = cortes(), pal = PAL[lente.pal];
      Array.prototype.forEach.call(paths, function (p) {
        var e = porA[p.getAttribute('data-a')], k = e ? clase(e[lente.id], c) : -1;
        p.style.fill = k < 0 ? '#d5dae3' : pal[k];
        p.classList.toggle('sel', !!sel && sel.a === p.getAttribute('data-a'));
        if (e) p.setAttribute('aria-label', e.n + ': ' + (e[lente.id] == null ? (lente.falta ? lente.falta.gris : 'sin cifra') : fmt(e[lente.id])) + '. Toca para ver su ficha.');
      });
      var lim = [null].concat(c).concat([null]);
      document.getElementById('plLeyenda').innerHTML = '<span class="pl-ley-tit">' + esc(lente.nom) + ' (' + lente.anio + ')</span><span class="pl-ley-cls">' +
        pal.map(function (col, i) {
          var t = i === 0 ? 'menos de ' + fmt(lim[1]) : i === 4 ? fmt(lim[4]) + ' o más' : fmt(lim[i]) + ' a ' + fmt(lim[i + 1]);
          return '<span><i style="background:' + col + '"></i>' + t + '</span>';
        }).join('') + (lente.falta && lente.falta.a.length ? '<span><i style="background:#d5dae3"></i>' + esc(lente.falta.gris) + '</span>' : '') + '</span>';
      document.getElementById('plQue').textContent = lente.que;
      document.getElementById('plFuente').innerHTML = lente.fuente;
      var f = lente.falta;
      document.getElementById('plFalta').innerHTML = f && f.a.length ? (f.pend ? 'Sin cifra: ' + f.a.map(function (a) { return esc(porA[a].n); }).join(', ') + ' ' + chip('pendiente', f.pend) + '. ' : '') + esc(f.txt) : '';
      /* «Cómo leerla» y «Lo que este mapa no dice» abren en la ventana lateral
         (apartados.js, button[data-cajon]): solo se ven los de la dimensión elegida. */
      Array.prototype.forEach.call(document.querySelectorAll('.pl-cajones [data-dim]'), function (b) { b.hidden = b.getAttribute('data-dim') !== dimP; });
    }
    function fila(nom, v, est, anio, pend) {
      return '<dt>' + nom + ' · ' + anio + '</dt><dd>' + (v == null ? 'Sin cifra ' + chip('pendiente', pend) : '<b class="num-tabular">' + mdp(v) + '</b> ' + chip(est)) + '</dd>';
    }
    function lenteDe(id) { return D.lentes.filter(function (l) { return l.id === id; })[0]; }
    function deuda(e, fijo) {
      var med = e.ild != null, d = function (id, nom) {
        var l = lenteDe(id);
        return '<dt>' + nom + '</dt><dd>' + (e[id] == null ? esc(l.falta.gris) : '<b class="num-tabular">' + fmt(e[id], l) + '</b> ' + chip(l.est)) + '</dd>';
      };
      ficha.innerHTML = '<h3>' + esc(e.n) + '</h3><p class="pl-ficha-sub">Su deuda al cierre de 2025 · Sistema de Alertas</p>' +
        '<dl class="pl-ficha-dl">' + d('deuda', 'Lo que debe') + d('dpc', 'Por habitante') + d('ild', 'Deuda ÷ ingresos libres') +
        d('sd', 'Lo que se va en pagarla') + d('ocp', 'Deudas de corto plazo') +
        '<dt>Semáforo de Hacienda</dt><dd>' + esc(e.sem) + ' ' + chip('oficial') + '</dd></dl>' +
        (med ? '' : '<p class="pl-ficha-mun">' + esc(lenteDe('ild').falta.txt) + '</p>') +
        '<a class="pl-ficha-ir" href="' + esc(e.p) + '#deuda">Ver su deuda en su portal ➔</a>' +
        (fijo ? '' : '<p class="pl-ficha-pista">Toca la entidad para fijarla; tócala otra vez para entrar.</p>');
    }
    /* La inversión: la obra directa y lo de sus organismos van separadas
       (no se suman), y lo que dejó la ASF. */
    function inversion(e, fijo) {
      var d = function (id, nom) {
        var l = lenteDe(id);
        return '<dt>' + nom + '</dt><dd>' + (e[id] == null ? 'Sin cifra ' + chip('pendiente', l.falta && l.falta.pend) : '<b class="num-tabular">' + fmt(e[id], l) + '</b> ' + chip(l.est)) + '</dd>';
      };
      var mas = e.inv != null && e.invt > e.inv;
      ficha.innerHTML = '<h3>' + esc(e.n) + '</h3><p class="pl-ficha-sub">La obra de su gobierno en 2024 · INEGI y ASF</p>' +
        '<dl class="pl-ficha-dl">' + d('inv', 'Obra que hizo el estado') + d('invp', 'De cada $100 de su egreso') + d('invt', 'A sus organismos de obra') +
        '<dt>Por aclarar ante la ASF</dt><dd><b class="num-tabular">' + mdp(e.asf) + '</b> · ' + e.aud + ' auditorías ' + chip('oficial') + '</dd></dl>' +
        (mas ? '<p class="pl-ficha-mun">Les pasó a sus organismos más que la obra que hizo él mismo: las dos cifras no se suman.</p>' : '') +
        '<a class="pl-ficha-ir" href="' + esc(e.p) + '#inversion">Ver su inversión en su portal ➔</a>' +
        (fijo ? '' : '<p class="pl-ficha-pista">Toca la entidad para fijarla; tócala otra vez para entrar.</p>');
    }
    /* Su congreso: lo que gastó, cuántos lo integran, por curul y la
       referencia contra el tope del 0.70 % (art. 116, fr. II). */
    function legislativa(e, fijo) {
      var d = function (id, nom) {
        var l = lenteDe(id);
        return '<dt>' + nom + '</dt><dd>' + (e[id] == null ? 'Sin cifra ' + chip('pendiente', l.falta && l.falta.pend) : '<b class="num-tabular">' + fmt(e[id], l) + '</b> ' + chip(l.est)) + '</dd>';
      };
      ficha.innerHTML = '<h3>Congreso de ' + esc(e.n) + '</h3><p class="pl-ficha-sub">Su gasto de 2024 · censo de los congresos del INEGI</p>' +
        '<dl class="pl-ficha-dl">' + d('leg', 'Lo que gastó') + d('legn', 'Personas legisladoras') + d('legx', 'Por curul') + d('legp', 'Frente al tope del 0.70 %') + '</dl>' +
        (e.legp != null && e.legp > 0.70 ? '<p class="pl-ficha-mun">Arriba del 0.70 % como referencia: el tope es de 2026 y su gasto, de 2024; no es un incumplimiento.</p>' : '') +
        '<a class="pl-ficha-ir" href="' + esc(e.p) + '#legislativa">Ver su congreso en su portal ➔</a>' +
        (fijo ? '' : '<p class="pl-ficha-pista">Toca la entidad para fijarla; tócala otra vez para entrar.</p>');
    }
    /* Su Poder Judicial: el dinero junto a lo que concluyó con él, el
       rezago penal y sus personas juzgadoras (CNIJF-E 2025). */
    function judicial(e, fijo) {
      var d = function (id, nom) {
        var l = lenteDe(id);
        return '<dt>' + nom + '</dt><dd><b class="num-tabular">' + fmt(e[id], l) + '</b> ' + chip(l.est) + '</dd>';
      };
      ficha.innerHTML = '<h3>Poder Judicial de ' + esc(e.n) + '</h3><p class="pl-ficha-sub">Primera instancia, 2024 · censo de impartición de justicia del INEGI</p>' +
        '<dl class="pl-ficha-dl">' + d('jud', 'Lo que ejerció') +
        '<dt>Le entraron · concluyó</dt><dd><b class="num-tabular">' + num(e.judi, 0) + ' · ' + num(e.judk, 0) + '</b> ' + chip('oficial') + '</dd>' +
        d('judc', 'Concluyó de cada 100') + d('juda', 'Por asunto concluido') + d('judr', 'Causas penales pendientes') + d('judj', 'Personas juzgadoras') + '</dl>' +
        '<p class="pl-ficha-mun">Concluir no es lo mismo que no deber: el rezago civil, familiar y mercantil no lo publica el censo.</p>' +
        '<a class="pl-ficha-ir" href="' + esc(e.p) + '#judicial">Ver su Poder Judicial en su portal ➔</a>' +
        (fijo ? '' : '<p class="pl-ficha-pista">Toca la entidad para fijarla; tócala otra vez para entrar.</p>');
    }
    /* Su salud pública: el IMSS con su Memoria Estadística 2025 (por OOAD) y el
       ISSSTE con el registro de la DGIS; las dos fuentes no se mezclan. */
    function salud(e, fijo) {
      var s = e.sal, d = function (id, nom) {
        var l = lenteDe(id);
        return '<dt>' + nom + '</dt><dd><b class="num-tabular">' + fmt(e[id], l) + '</b> ' + chip(l.est) + '</dd>';
      };
      var imss = '<p class="pl-ficha-sub">🩺 El IMSS · Memoria Estadística 2025</p><dl class="pl-ficha-dl">' + d('imA', 'Personas adscritas') +
        '<dt>Consultas</dt><dd><b class="num-tabular">' + num(s.con, 0) + '</b> ' + chip('oficial') + '</dd>' +
        d('imX', 'Por persona adscrita') + d('imQ', 'Cirugías') + d('imK', 'Camas por cada mil adscritos') + '</dl>' +
        (s.oo.length ? '<p class="pl-ficha-mun">Suma de sus dos OOAD: ' + esc(s.oo.join(' y ')) + '.</p>' : '');
      var iss = '<p class="pl-ficha-sub">🏥 El ISSSTE · registro de la DGIS 2025</p><dl class="pl-ficha-dl">' + d('isM', 'Médicos') + d('isK', 'Camas de hospital') + d('isU', 'Unidades') +
        '<dt>Médicos del IMSS, mismo registro</dt><dd><b class="num-tabular">' + num(e.imM, 0) + '</b> ' + chip('oficial') + '</dd>' +
        '<dt>Personas que atiende</dt><dd>Sin cifra ' + chip('pendiente', 'salud-issste-servicios') + '</dd></dl>';
      ficha.innerHTML = '<h3>' + esc(e.n) + '</h3>' + (/^is/.test(lente.id) ? iss + imss : imss + iss) +
        '<p class="pl-ficha-mun">Cuentan cuánto se hizo y con qué, no cuánto se esperó ni si alcanzó.</p>' +
        '<a class="pl-ficha-ir" href="' + esc(e.p) + '#salud">Ver su salud pública en su portal ➔</a>' +
        (fijo ? '' : '<p class="pl-ficha-pista">Toca la entidad para fijarla; tócala otra vez para entrar.</p>');
    }
    /* Sus recursos naturales: sus acuíferos (CONAGUA, DOF 09-11-2023, corte 2022), sus incendios (CONAFOR, cierre 2025), sus concesiones mineras (DGM, marzo de 2024) y su
       refinería de PEMEX, si tiene (Segundo Informe 2026, Anuario 2024 y estados
       financieros de PEMEX 2025). */
    function mdps(v) { return v == null ? 'no figura en la nota' : '<b class="num-tabular">' + (v < 0 ? '−' : '+') + '$' + num(Math.abs(v), 1) + ' mdp</b> ' + chip('oficial'); }
    var PROD = { mayor: 'Una de las diez que dan el 94.9 % de la producción minera', menor: 'Entre las 17 que dan el 5.2 % de la producción minera' };
    function ambiental(e, fijo) {
      var r = e.ref, m = e.min, w = e.acu, z = e.inc, b = e.sf, refL = /^ref/.test(lente.id), minL = /^min/.test(lente.id), incL = /^inc|^sf/.test(lente.id), q = e.pe, peL = /^pe/.test(lente.id);
      var sg = function (v) { return (v > 0 ? '+' : v < 0 ? '−' : '') + num(Math.abs(v), 1) + '%'; };
      var pesc = q ? (e.peT != null ?
        '<p class="pl-ficha-sub">🐟 Su pesca y su acuacultura · 2025</p><dl class="pl-ficha-dl">' +
        '<dt>Toneladas en peso vivo</dt><dd><b class="num-tabular">' + num(e.peT, 0) + ' t</b> ' + chip('oficial') + ' · lugar ' + q.lt + '</dd>' +
        '<dt>Su valor, a precio de playa</dt><dd><b class="num-tabular">' + mdp(e.peV) + '</b> ' + chip('oficial') + ' · lugar ' + q.lv + '</dd>' +
        '<dt>De cultivo, de cada 100 t</dt><dd><b class="num-tabular">' + num(q.pacu, 1) + '</b> ' + chip('derivado') + '</dd>' +
        '<dt>Contra 2024</dt><dd>toneladas ' + sg(q.ct) + ' · valor ' + sg(q.cv) + ' ' + chip('derivado') + '</dd></dl>' +
        '<p class="pl-ficha-mun">Es lo que se declaró en los avisos de arribo y de cosecha, no todo lo que se pescó, y no dice si las especies aguantan.</p>' :
        '<p class="pl-ficha-sub">🐟 No registró pesca ni acuacultura en 2025</p><p class="pl-ficha-mun">En 2024 registró ' + num(q.t24, 0) + ' t. No registrar no es lo mismo que no tener pesca.</p>') : '';
      var agua = w ?
        '<p class="pl-ficha-sub">💧 Sus acuíferos · corte dic 2022</p><dl class="pl-ficha-dl">' +
        '<dt>Sin agua para concesionar</dt><dd><b class="num-tabular">' + w.sin + ' de ' + w.n + '</b> ' + chip('oficial') + ' · ' + num(e.acuP, 1) + '% ' + chip('derivado') + '</dd>' +
        '<dt>Suma de sus déficits</dt><dd>' + (e.acuD > 0 ? '<b class="num-tabular">' + num(e.acuD, 1) + ' hm³</b> al año ' + chip('derivado') + ' · lugar ' + w.lug : 'ninguno en déficit') + '</dd>' +
        (w.s27.length ? '<dt>Sobreexplotados medidos con pozos</dt><dd>' + esc(w.s27.join(', ')) + ' ' + chip('oficial') + '</dd>' : '') + '</dl>' +
        '<p class="pl-ficha-mun">La disponibilidad es el agua que aún se puede concesionar, no la que queda, y no mide su calidad.</p>' : '';
      var fuego = z ?
        '<p class="pl-ficha-sub">' + (/^sf/.test(lente.id) ? '🌲 Sus bosques y sus incendios forestales' : '🔥 Sus incendios forestales · 2025') + '</p><dl class="pl-ficha-dl">' +
        '<dt>Superficie afectada</dt><dd><b class="num-tabular">' + num(e.incH, 0) + ' ha</b> ' + chip('oficial') + ' · lugar ' + z.lh + ' de 32</dd>' +
        '<dt>Incendios</dt><dd><b class="num-tabular">' + num(e.incN, 0) + '</b> ' + chip('oficial') + ' · lugar ' + z.ln + ' de 32</dd>' +
        '<dt>De árboles, de cada 100 ha</dt><dd><b class="num-tabular">' + num(z.parb, 1) + '</b> ' + chip('derivado') + '</dd>' +
        '<dt>Contra 2024</dt><dd>' + (z.cam > 0 ? '+' : z.cam < 0 ? '−' : '') + num(Math.abs(z.cam), 1) + '% ' + chip('derivado') + '</dd>' +
        (b ? '<dt>Su superficie forestal · mapa de 2018</dt><dd><b class="num-tabular">' + num(e.sfT, 0) + ' ha</b> ' + chip('oficial') + ' · lugar ' + b.lug + ' de 32</dd>' +
        '<dt>Lo afectado, de cada 100 ha forestales</dt><dd><b class="num-tabular">' + (e.incP >= 0.05 ? num(e.incP, 1) : 'menos de 0.1') + '</b> ' + chip('derivado') + ' · lugar ' + b.lq + ' de 32</dd>' : '') + '</dl>' +
        '<p class="pl-ficha-mun">Superficie afectada no es bosque perdido: la mayor parte del fuego corre por pasto y matorral, y «forestal» incluye el matorral.</p>' : '';
      var minas = m ?
        '<p class="pl-ficha-sub">⛏️ Concesiones mineras · marzo 2024</p><dl class="pl-ficha-dl">' +
        '<dt>Títulos vigentes</dt><dd><b class="num-tabular">' + num(e.minT, 0) + '</b> ' + chip('oficial') + ' · lugar ' + m.lug + ' de 30</dd>' +
        '<dt>Hectáreas que amparan</dt><dd><b class="num-tabular">' + num(e.minH, 0) + ' ha</b> ' + chip('oficial') + '</dd>' +
        (m.t26 != null ? '<dt>Al 30 de junio de 2026</dt><dd><b class="num-tabular">' + num(m.t26, 0) + '</b> ' + chip('oficial') + '</dd>' : '') + '</dl>' +
        '<p class="pl-ficha-mun">' + (PROD[m.prod] || 'No aparece entre las entidades con producción minera: tener concesiones no es tener minas trabajando') + '.</p>' :
        '<p class="pl-ficha-sub">⛏️ No figura en el cuadro de concesiones mineras</p>';
      var refi = r ?
        '<p class="pl-ficha-sub">🛢️ ' + esc(r.n) + ' · ' + esc(r.sede) + '</p><dl class="pl-ficha-dl">' +
        '<dt>Crudo procesado · junio 2026</dt><dd><b class="num-tabular">' + num(r.jun, 0) + ' mil b/d</b> ' + chip('oficial') + ' · lugar ' + r.lug + ' de 7</dd>' +
        '<dt>Promedio sep-25 a jun-26</dt><dd><b class="num-tabular">' + num(r.prom, 1) + ' mil b/d</b> ' + chip('derivado') + '</dd>' +
        '<dt>Capacidad · uso promedio</dt><dd><b class="num-tabular">' + num(r.cap, 0) + ' mil b/d · ' + num(r.uso, 1) + '%</b> ' + chip('derivado') + '</dd>' +
        '<dt>Valor ganado o perdido en libros · 2025</dt><dd>' + (r.id === 'olmeca' ? 'es de una filial y PEMEX la arrienda' : mdps(r.d25)) + '</dd></dl>' +
        '<p class="pl-ficha-mun">Procesar no es producir gasolina, y el valor en libros es una estimación, no dinero que salió de la caja.</p>' :
        '<p class="pl-ficha-sub">🛢️ Sin refinería de PEMEX</p>';
      ficha.innerHTML = '<h3>' + esc(e.n) + '</h3>' + (refL ? refi + agua + fuego + pesc + minas : minL ? minas + agua + fuego + pesc + refi : incL ? fuego + agua + pesc + minas + refi : peL ? pesc + agua + fuego + minas + refi : agua + fuego + pesc + minas + refi) +
        '<a class="pl-ficha-ir" href="' + esc(e.p) + '#ambiental">Ver sus recursos naturales en su portal ➔</a>' +
        (fijo ? '' : '<p class="pl-ficha-pista">Toca la entidad para fijarla; tócala otra vez para entrar.</p>');
    }
    function muestra(e, fijo) {
      if (!e) return;
      if (dimP === 'ambiental') { ambiental(e, fijo); return; }
      if (dimP === 'judicial') { judicial(e, fijo); return; }
      if (dimP === 'salud') { salud(e, fijo); return; }
      if (dimP === 'deuda') { deuda(e, fijo); return; }
      if (dimP === 'inversion') { inversion(e, fijo); return; }
      if (dimP === 'legislativa') { legislativa(e, fijo); return; }
      ficha.innerHTML = '<h3>' + esc(e.n) + '</h3><p class="pl-ficha-sub">Capital: ' + esc(e.cap) + ' · ' + num(e.pob, 0) + ' habitantes</p>' +
        '<dl class="pl-ficha-dl">' +
        fila('Le baja de la Federación', e.fed, 'derivado', 2026) +
        fila('Cobra el estado por su cuenta', e.est, 'derivado', 2024, lenteDe('est').falta.pend) +
        fila('Ingresan sus municipios', e.mun, 'derivado', 2024, lenteDe('mun').falta.pend) +
        '</dl><p class="pl-ficha-mun">' + e.mn + (e.a === 'CDMX' ? ' demarcaciones' : ' municipios') + (e.mc ? ', ' + e.mc + ' con cuenta de 2024' : ', sin cuenta municipal') + '.</p>' +
        (e.mm ? '<p class="pl-ficha-mun">🗺️ Su portal ya trae el mapa de sus municipios.</p>' : '') +
        '<a class="pl-ficha-ir" href="' + esc(e.p) + '">Entrar al portal de ' + esc(e.n) + ' ➔</a>' +
        (fijo ? '' : '<p class="pl-ficha-pista">Toca la entidad para fijarla; tócala otra vez para entrar.</p>');
    }
    function elige(a, abrir) {
      var e = porA[a];
      if (!e) return;
      if (abrir && sel && sel.a === a) { location.href = e.p + (dimP === 'financiera' ? '' : '#' + dimP); return; }
      sel = e;
      pinta();
      muestra(e, true);
      avisa();
    }
    Array.prototype.forEach.call(paths, function (p) {
      var a = p.getAttribute('data-a');
      p.addEventListener('click', function () { elige(a, true); });
      p.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); elige(a, true); } });
      p.addEventListener('mouseenter', function () { if (!sel) muestra(porA[a], false); });
      p.addEventListener('focus', function () { if (!sel) muestra(porA[a], false); });
    });
    var botones = document.querySelectorAll('.pl-lentes .pl-lente[data-dim]');
    function ponLente(id) {
      lente = lenteDe(id) || lente;
      ultima[lente.dim] = lente.id;
      Array.prototype.forEach.call(botones, function (x) {
        x.setAttribute('aria-checked', x.getAttribute('data-l') === lente.id ? 'true' : 'false');
        x.hidden = x.getAttribute('data-dim') !== lente.dim;
      });
      pinta();
      if (sel) muestra(sel, true);
    }
    Array.prototype.forEach.call(botones, function (b) {
      b.addEventListener('click', function () { ponLente(b.getAttribute('data-l')); });
    });
    /* Una dimensión que ya se pinta cambia el mapa con su primera lente (o
       la última que se eligió en ella). */
    function ponDim(id) {
      dimP = id;
      ponLente(ultima[id] || D.lentes.filter(function (l) { return l.dim === id; })[0].id);
      if (!sel) ficha.innerHTML = '<p class="pl-ficha-vacia"><b>Toca una entidad.</b> Verás sus cifras de la dimensión que elegiste y la puerta a su portal, con sus municipios.</p>';
    }
    /* Las dimensiones que todavía no se pintan llevan a donde ya viven. */
    var dim = null;
    function avisa() {
      if (!dim || !aviso) return;
      var d = D.dims[dim], liga = d.ire && sel && d.ire.indexOf('%s') >= 0 && dim !== 'legislativa' ? d.ire.replace('%s', encodeURIComponent(sel.a)) : d.ir;
      aviso.innerHTML = '<b>La dimensión ' + esc(d.n.toLowerCase()) + ' llega al Planisferio en una próxima entrega.</b> Mientras, ya está en la Enciclopedia' +
        (sel && liga !== d.ir ? ', con ' + esc(sel.n) + ' elegido' : '') + ': <a href="' + esc(liga) + '">ábrela ➔</a>. El mapa de abajo sigue en la dimensión ' + esc(D.dims[dimP].n.toLowerCase()) + '.';
      aviso.hidden = false;
    }
    Array.prototype.forEach.call(document.querySelectorAll('.pl-dim'), function (b) {
      b.addEventListener('click', function () {
        eligeDim(b.getAttribute('data-dim'));
      });
    });
    function eligeDim(id) {
      if (!D.dims[id]) return;
      Array.prototype.forEach.call(document.querySelectorAll('.pl-dim'), function (x) { x.setAttribute('aria-selected', x.getAttribute('data-dim') === id ? 'true' : 'false'); });
      if (D.dims[id].pinta) { dim = null; if (aviso) aviso.hidden = true; ponDim(id); return; }
      dim = id;
      avisa();
    }
    var m = /[?&]e=([^&#]+)/.exec(location.search), pedida = null;
    try { pedida = m ? decodeURIComponent(m[1]) : null; } catch (err) { pedida = null; }
    /* ?d=deuda, ?d=inversion, ?d=ambiental, ?d=legislativa o ?d=judicial (desde el Auditor): abre el mapa en esa dimensión (y &l=, en esa lente). */
    var md = /[?&]d=([a-z]+)/.exec(location.search);
    /* &l=minT (desde el Auditor o la Enciclopedia): la lente con que abre esa dimensión. */
    var ml = /[?&]l=([A-Za-z]+)/.exec(location.search), lp = ml && lenteDe(ml[1]);
    if (lp) ultima[lp.dim] = lp.id;
    if (md && D.dims[md[1]]) eligeDim(md[1]); else pinta();
    /* ?e=JAL&m=1 (desde el Auditor): si la entidad ya tiene el mapa de sus
       municipios, se va directo a él; si no, se queda con su ficha. */
    if (pedida && porA[pedida] && porA[pedida].mm && /[?&]m=1/.test(location.search)) { location.replace(porA[pedida].p + '#mapa-municipios'); return; }
    if (pedida && porA[pedida]) elige(pedida, false);
    else if (pedida) {
      var p = plano(pedida);
      D.e.forEach(function (e) { if (plano(e.n) === p) elige(e.a, false); });
    }
  })();

  /* 3 · El mapa de los municipios (Marco Geoestadístico 2024 del INEGI) */
  (function () {
    var nodo = document.getElementById('plMunDatos');
    if (!nodo) return;
    var D;
    try { D = JSON.parse(nodo.textContent); } catch (e) { return; }
    var PAL = {
      verde: ['#e4f3e8', '#b3dcbd', '#6dba82', '#2e8a4c', '#0f5128'],
      azul: ['#e3ecf8', '#b4c9ea', '#6f95d2', '#2f5fa8', '#0b2a63'],
      rojo: ['#fbe5e2', '#f2b3aa', '#e06f60', '#b3261e', '#6e1510']
    };
    var porC = {}, lente = D.lentes[0], sel = null, ficha = document.getElementById('plMunFicha'), CERO = '#eeede6';
    D.m.forEach(function (x) { porC[x.c] = x; });
    var paths = document.querySelectorAll('.pl-mun');
    function fmt(v) { return v == null ? '—' : lente.u === 'pct' ? num(v, 1) + '%' : mdp(v); }
    /* ?ml=inv abre el mapa con esa lente (el portal lleva así desde «Su inversión»). */
    var pedidaL = new URLSearchParams(location.search).get('ml');
    D.lentes.forEach(function (l) { if (l.id === pedidaL) lente = l; });
    Array.prototype.forEach.call(document.querySelectorAll('#mapa-municipios .pl-lente'), function (b) { b.setAttribute('aria-checked', b.getAttribute('data-l') === lente.id ? 'true' : 'false'); });
    function cortes() {
      /* En las lentes donde el $0 es lo común, los cortes salen de los que sí reportaron algo. */
      var v = D.m.map(function (x) { return x[lente.id]; }).filter(function (x) { return x != null && (!lente.cero || x > 0); }).sort(function (a, b) { return a - b; });
      return [1, 2, 3, 4].map(function (k) { return v[Math.round(k * v.length / 5)]; });
    }
    function pinta() {
      var c = cortes(), pal = PAL[lente.pal];
      Array.prototype.forEach.call(paths, function (p) {
        var x = porC[p.getAttribute('data-c')], v = x ? x[lente.id] : null, k = -1;
        if (v != null) { k = 0; while (k < 4 && v >= c[k]) k++; }
        p.style.fill = k < 0 ? '#d5dae3' : (lente.cero && v === 0) ? CERO : pal[k];
        p.classList.toggle('sel', !!sel && sel.c === p.getAttribute('data-c'));
        if (x) p.setAttribute('aria-label', x.n + ': ' + (v == null ? (D.sin ? 'sin cuenta municipal' : 'sin cuenta de ' + D.anio) : fmt(v)));
      });
      var lim = [null].concat(c);
      if (D.sin) {
        document.getElementById('plMunLeyenda').innerHTML = '<span class="pl-ley-cls"><span><i style="background:#d5dae3"></i>sin cuenta municipal</span></span>';
        document.getElementById('plMunQue').textContent = '';
        return;
      }
      document.getElementById('plMunLeyenda').innerHTML = '<span class="pl-ley-tit">' + esc(lente.nom) + ' (' + D.anio + ')</span><span class="pl-ley-cls">' +
        (lente.cero ? '<span><i style="background:' + CERO + '"></i>$0 reportado</span>' : '') +
        pal.map(function (col, i) {
          var t = i === 0 ? (lente.cero ? 'más de $0 y ' : '') + 'menos de ' + fmt(lim[1]) : i === 4 ? fmt(lim[4]) + ' o más' : fmt(lim[i]) + ' a ' + fmt(lim[i + 1]);
          return '<span><i style="background:' + col + '"></i>' + t + '</span>';
        }).join('') + '<span><i style="background:#d5dae3"></i>' + (D.sin ? 'sin cuenta municipal' : 'sin cuenta') + '</span></span>';
      document.getElementById('plMunQue').textContent = lente.que;
    }
    function muestra(x) {
      var ente = 'herramienta-inspector-entes.html#ente=municipal:' + D.cve + x.c;
      if (x.ing == null) {
        ficha.innerHTML = '<h3>' + esc(x.n) + '</h3><p>' + (D.sin ? esc(D.sin) + ' ' + chip('pendiente', D.pend) :
          'No rindió su cuenta de ' + D.anio + ' al INEGI ' + chip('pendiente', D.pend) + ': sigue en el padrón, sin cifra.') + ' Ponerle cero falsearía la cifra.</p><a class="pl-ficha-ir" href="' + ente + '">Su ficha en el Auditor de entes ➔</a>';
        return;
      }
      ficha.innerHTML = '<h3>' + esc(x.n) + '</h3><p class="pl-ficha-sub">Clave INEGI ' + D.cve + x.c + ' · cuentas de ' + D.anio + '</p><dl class="pl-ficha-dl">' +
        '<dt>Ingreso total</dt><dd><b class="num-tabular">' + mdp(x.ing) + '</b> ' + chip('oficial') + '</dd>' +
        '<dt>Participaciones</dt><dd>' + mdp(x.part) + ' ' + chip('oficial') + '</dd>' +
        '<dt>Aportaciones (FORTAMUN ' + mdp(x.fort) + ' · FISMDF ' + mdp(x.fis) + ')</dt><dd>' + mdp(x.aport) + ' ' + chip('oficial') + '</dd>' +
        '<dt>Predial cobrado</dt><dd>' + mdp(x.predial) + ' ' + chip('oficial') + '</dd>' +
        '<dt>Dependencia de transferencias</dt><dd>' + (x.dep == null ? '—' : num(x.dep, 1) + '%') + ' ' + chip('derivado') + '</dd>' +
        (x.inv == null ? '' : '<dt>Inversión pública' + (x.invp == null ? '' : ' ($' + num(x.invp, 1) + ' de cada $100 de su egreso ' + chip('derivado') + ')') + '</dt><dd>' + mdp(x.inv) + ' ' + chip('oficial') + '</dd>') +
        (x.dpag == null ? '' : '<dt>Pagó por sus créditos (capital, intereses y comisiones)</dt><dd>' + mdp(x.dpag) + ' ' + chip('derivado') + '</dd>' +
          '<dt>Pidió prestado en el año</dt><dd>' + mdp(x.emp) + ' ' + chip('oficial') + '</dd>' +
          '<dt>Adeudos de años anteriores (ADEFAS)</dt><dd>' + mdp(x.adef) + ' ' + chip('oficial') + '</dd>') + '</dl>' +
        (x.dpag == null ? '' : '<p class="pl-ficha-sub">Es lo que pagó y pidió en el año, no lo que debe: su saldo lo publica Hacienda y sigue ' + chip('pendiente', 'deuda-municipios') + '.</p>') +
        '<a class="pl-ficha-ir" href="' + ente + '">Su estado de cuenta y salud financiera ➔</a>';
    }
    function elige(c) {
      var x = porC[c];
      if (!x) return;
      sel = x;
      pinta();
      // El seleccionado se dibuja al final, para que sus vecinos no le tapen el borde.
      var p = document.querySelector('.pl-mun[data-c="' + c + '"]');
      if (p) { var foco = document.activeElement === p; p.parentNode.appendChild(p); if (foco) p.focus(); }
      muestra(x);
      Array.prototype.forEach.call(document.querySelectorAll('#plMun tr[data-c]'), function (r) { r.classList.toggle('sel', r.getAttribute('data-c') === c); });
    }
    Array.prototype.forEach.call(paths, function (p) {
      var c = p.getAttribute('data-c');
      p.addEventListener('click', function () { elige(c); });
      p.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); elige(c); } });
      p.addEventListener('mouseenter', function () { if (!sel) muestra(porC[c]); });
    });
    Array.prototype.forEach.call(document.querySelectorAll('#mapa-municipios .pl-lente'), function (b) {
      b.addEventListener('click', function () {
        lente = D.lentes.filter(function (l) { return l.id === b.getAttribute('data-l'); })[0] || lente;
        Array.prototype.forEach.call(document.querySelectorAll('#mapa-municipios .pl-lente'), function (x) { x.setAttribute('aria-checked', x === b ? 'true' : 'false'); });
        pinta();
      });
    });
    /* Desde la tabla: tocar el nombre de un municipio lo ilumina en el mapa. */
    Array.prototype.forEach.call(document.querySelectorAll('#plMun tr[data-c] th'), function (th) {
      th.classList.add('pl-th-ir');
      th.setAttribute('tabindex', '0');
      th.addEventListener('click', function () {
        elige(th.parentNode.getAttribute('data-c'));
        document.getElementById('plMunMapa').scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
    pinta();
  })();

  /* 4 · Los municipios de cada portal ---------------------------------- */
  (function () {
    var t = document.getElementById('plMun');
    if (!t) return;
    var tb = t.tBodies[0], filas = Array.prototype.slice.call(tb.rows);
    var busca = document.getElementById('plMunBusca'), orden = document.getElementById('plMunOrden');
    function aplica() {
      var q = plano(busca.value).trim(), o = orden.value;
      filas.forEach(function (r) { r.hidden = !!q && plano(r.getAttribute('data-n')).indexOf(q) < 0; });
      var ord = filas.slice().sort(function (a, b) {
        if (o === 'n') return plano(a.getAttribute('data-n')).localeCompare(plano(b.getAttribute('data-n')));
        var x = parseFloat(a.getAttribute('data-' + o)), y = parseFloat(b.getAttribute('data-' + o));
        if (isNaN(x)) x = -Infinity;
        if (isNaN(y)) y = -Infinity;
        return y - x;
      });
      ord.forEach(function (r) { tb.appendChild(r); });
    }
    busca.addEventListener('input', aplica);
    orden.addEventListener('change', aplica);
  })();
})();
