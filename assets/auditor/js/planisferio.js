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
      if (l.fmt === 'pesos') return '$' + num(v, 0);
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
    function pinta() {
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
      var nota = document.getElementById('plDimNota'), tx = D.notas && D.notas[dimP];
      if (nota) { nota.innerHTML = tx || ''; nota.hidden = !tx; }
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
    function muestra(e, fijo) {
      if (!e) return;
      if (dimP === 'deuda') { deuda(e, fijo); return; }
      if (dimP === 'inversion') { inversion(e, fijo); return; }
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
      if (abrir && sel && sel.a === a) { location.href = e.p + (dimP === 'deuda' ? '#deuda' : dimP === 'inversion' ? '#inversion' : ''); return; }
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
    /* ?d=deuda o ?d=inversion (desde el Auditor): abre el mapa en esa dimensión. */
    var md = /[?&]d=([a-z]+)/.exec(location.search);
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
    var porC = {}, lente = D.lentes[0], sel = null, ficha = document.getElementById('plMunFicha');
    D.m.forEach(function (x) { porC[x.c] = x; });
    var paths = document.querySelectorAll('.pl-mun');
    function fmt(v) { return v == null ? '—' : lente.u === 'pct' ? num(v, 1) + '%' : mdp(v); }
    /* ?ml=inv abre el mapa con esa lente (el portal lleva así desde «Su inversión»). */
    var pedidaL = new URLSearchParams(location.search).get('ml');
    D.lentes.forEach(function (l) { if (l.id === pedidaL) lente = l; });
    Array.prototype.forEach.call(document.querySelectorAll('#mapa-municipios .pl-lente'), function (b) { b.setAttribute('aria-checked', b.getAttribute('data-l') === lente.id ? 'true' : 'false'); });
    function cortes() {
      var v = D.m.map(function (x) { return x[lente.id]; }).filter(function (x) { return x != null; }).sort(function (a, b) { return a - b; });
      return [1, 2, 3, 4].map(function (k) { return v[Math.round(k * v.length / 5)]; });
    }
    function pinta() {
      var c = cortes(), pal = PAL[lente.pal];
      Array.prototype.forEach.call(paths, function (p) {
        var x = porC[p.getAttribute('data-c')], v = x ? x[lente.id] : null, k = -1;
        if (v != null) { k = 0; while (k < 4 && v >= c[k]) k++; }
        p.style.fill = k < 0 ? '#d5dae3' : pal[k];
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
        pal.map(function (col, i) {
          var t = i === 0 ? 'menos de ' + fmt(lim[1]) : i === 4 ? fmt(lim[4]) + ' o más' : fmt(lim[i]) + ' a ' + fmt(lim[i + 1]);
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
        (x.inv == null ? '' : '<dt>Inversión pública' + (x.invp == null ? '' : ' ($' + num(x.invp, 1) + ' de cada $100 de su egreso ' + chip('derivado') + ')') + '</dt><dd>' + mdp(x.inv) + ' ' + chip('oficial') + '</dd>') + '</dl>' +
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
