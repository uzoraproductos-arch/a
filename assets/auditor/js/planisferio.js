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
      verde: ['#e4f3e8', '#b3dcbd', '#6dba82', '#2e8a4c', '#0f5128']
    };
    var porA = {}, lente = D.lentes[0], sel = null;
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
        if (e) p.setAttribute('aria-label', e.n + ': ' + (e[lente.id] == null ? 'sin cifra' : mdp(e[lente.id])) + '. Toca para ver su ficha.');
      });
      var lim = [null].concat(c).concat([null]);
      document.getElementById('plLeyenda').innerHTML = '<span class="pl-ley-tit">' + esc(lente.nom) + ' (' + lente.anio + ')</span><span class="pl-ley-cls">' +
        pal.map(function (col, i) {
          var t = i === 0 ? 'menos de ' + mdp(lim[1]) : i === 4 ? mdp(lim[4]) + ' o más' : mdp(lim[i]) + ' a ' + mdp(lim[i + 1]);
          return '<span><i style="background:' + col + '"></i>' + t + '</span>';
        }).join('') + '<span><i style="background:#d5dae3"></i>sin cifra</span></span>';
      document.getElementById('plQue').textContent = lente.que;
      document.getElementById('plFuente').innerHTML = lente.fuente;
      var falta = D.falta[lente.id] || [];
      document.getElementById('plFalta').innerHTML = falta.length ? 'Sin cifra en este piso: ' + falta.map(function (a) { return esc(porA[a].n); }).join(', ') + ' ' + chip('pendiente', D.pend[lente.id]) +
        (lente.id === 'mun' ? '. Las alcaldías de la Ciudad de México no rinden cuenta municipal al INEGI.' : '. La Ciudad de México no figura en la estadística estatal del INEGI.') : '';
    }
    function fila(nom, v, est, anio, pend) {
      return '<dt>' + nom + ' · ' + anio + '</dt><dd>' + (v == null ? 'Sin cifra ' + chip('pendiente', pend) : '<b class="num-tabular">' + mdp(v) + '</b> ' + chip(est)) + '</dd>';
    }
    function muestra(e, fijo) {
      if (!e) return;
      ficha.innerHTML = '<h3>' + esc(e.n) + '</h3><p class="pl-ficha-sub">Capital: ' + esc(e.cap) + ' · ' + num(e.pob, 0) + ' habitantes</p>' +
        '<dl class="pl-ficha-dl">' +
        fila('Le baja de la Federación', e.fed, 'derivado', 2026) +
        fila('Cobra el estado por su cuenta', e.est, 'derivado', 2024, D.pend.est) +
        fila('Ingresan sus municipios', e.mun, 'derivado', 2024, D.pend.mun) +
        '</dl><p class="pl-ficha-mun">' + e.mn + (e.a === 'CDMX' ? ' demarcaciones' : ' municipios') + (e.mc ? ', ' + e.mc + ' con cuenta de 2024' : ', sin cuenta municipal') + '.</p>' +
        (e.mm ? '<p class="pl-ficha-mun">🗺️ Su portal ya trae el mapa de sus municipios.</p>' : '') +
        '<a class="pl-ficha-ir" href="' + esc(e.p) + '">Entrar al portal de ' + esc(e.n) + ' ➔</a>' +
        (fijo ? '' : '<p class="pl-ficha-pista">Toca la entidad para fijarla; tócala otra vez para entrar.</p>');
    }
    function elige(a, abrir) {
      var e = porA[a];
      if (!e) return;
      if (abrir && sel && sel.a === a) { location.href = e.p; return; }
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
    Array.prototype.forEach.call(document.querySelectorAll('.pl-lente'), function (b) {
      b.addEventListener('click', function () {
        lente = D.lentes.filter(function (l) { return l.id === b.getAttribute('data-l'); })[0] || lente;
        Array.prototype.forEach.call(document.querySelectorAll('.pl-lente'), function (x) { x.setAttribute('aria-checked', x === b ? 'true' : 'false'); });
        pinta();
      });
    });
    /* Las dimensiones que todavía no se pintan llevan a donde ya viven. */
    var dim = null;
    function avisa() {
      if (!dim || !aviso) return;
      var d = D.dims[dim], liga = d.ire && sel && d.ire.indexOf('%s') >= 0 && dim !== 'legislativa' ? d.ire.replace('%s', encodeURIComponent(sel.a)) : d.ir;
      aviso.innerHTML = '<b>La dimensión ' + esc(d.n.toLowerCase()) + ' llega al Planisferio en una próxima entrega.</b> Mientras, ya está en la Enciclopedia' +
        (sel && liga !== d.ir ? ', con ' + esc(sel.n) + ' elegido' : '') + ': <a href="' + esc(liga) + '">ábrela ➔</a>. El mapa de abajo sigue en la dimensión financiera.';
      aviso.hidden = false;
    }
    Array.prototype.forEach.call(document.querySelectorAll('.pl-dim'), function (b) {
      b.addEventListener('click', function () {
        var id = b.getAttribute('data-dim');
        Array.prototype.forEach.call(document.querySelectorAll('.pl-dim'), function (x) { x.setAttribute('aria-selected', x === b ? 'true' : 'false'); });
        dim = D.dims[id] && D.dims[id].ir ? id : null;
        if (dim) avisa(); else if (aviso) aviso.hidden = true;
      });
    });
    var m = /[?&]e=([^&#]+)/.exec(location.search), pedida = null;
    try { pedida = m ? decodeURIComponent(m[1]) : null; } catch (err) { pedida = null; }
    pinta();
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
    function fmt(v) { return v == null ? '—' : lente.id === 'dep' ? num(v, 1) + '%' : mdp(v); }
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
        '<dt>Dependencia de transferencias</dt><dd>' + (x.dep == null ? '—' : num(x.dep, 1) + '%') + ' ' + chip('derivado') + '</dd></dl>' +
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
