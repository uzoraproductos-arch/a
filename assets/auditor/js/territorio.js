/* Auditavisión · Números › Baja al territorio, páginas de sus tres módulos
   (11-10-2026). Las páginas llegan ya escritas por
   herramientas/territorio_modulos.py, y las cifras en JSON dentro de cada
   página: aquí no se escribe ninguna cifra. Este archivo solo las mueve:
   1. el mapa del gasto federalizado (lentes, colores, cuadro de las 32),
   2. el circuito de cada estado (selector),
   3. el padrón municipal (selector, buscador y orden), que lee
      window.AUDIT_MUNICIPIOS de municipios-efipem.js. */
(function () {
  'use strict';

  function datos(id) {
    var n = document.getElementById(id);
    if (!n) return null;
    try { return JSON.parse(n.textContent); } catch (e) { return null; }
  }
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function num(v, d) { return v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function mdp(v) { return '$' + num(v, 1) + ' mdp'; }
  function fmt(v, f) {
    if (v == null) return '—';
    if (f === 'pesos') return '$' + num(Math.round(v), 0);
    if (f === 'pct') return num(v, 1) + '%';
    return mdp(v);
  }
  function chip(e, pend) {
    return '<span class="est-chip est-' + e + '"' + (pend ? ' data-pend="' + esc(pend) + '"' : '') + '>' + e + '</span>';
  }
  /* El estado que llega en ?e=AGS (desde el mapa) o en #e-AGS. */
  function pedida() {
    var m = /[?&]e=([^&#]+)/.exec(location.search) || /#e-([^&#]+)/.exec(location.hash);
    try { return m ? decodeURIComponent(m[1]) : null; } catch (err) { return null; }
  }

  /* ------------------------------------------------------------------
     1 · El mapa del gasto federalizado
     ------------------------------------------------------------------ */
  (function () {
    var D = datos('ttMapaDatos'), raiz = document.getElementById('ttMapa');
    if (!D || !raiz) return;
    var PAL = {
      oro: ['#fbf3dc', '#f0d98f', '#d9b34f', '#a8801f', '#6b4f0c'],
      azul: ['#e3ecf8', '#b4c9ea', '#6f95d2', '#2f5fa8', '#0b2a63'],
      rojo: ['#fbe5e2', '#f2b3aa', '#e06f60', '#b3261e', '#6e1510']
    };
    var lente = D.lentes[0], sel = null;
    var porA = {};
    D.e.forEach(function (e) { porA[e.a] = e; });

    function orden() {
      return D.e.filter(function (e) { return e[lente.id] != null; })
        .sort(function (a, b) { return b[lente.id] - a[lente.id]; });
    }
    /* Cinco clases con el mismo número de entidades (quintiles): así el
       color compara posiciones, no lo deforma un solo estado enorme. */
    function cortes(o) {
      var v = o.map(function (e) { return e[lente.id]; }).sort(function (a, b) { return a - b; });
      return [1, 2, 3, 4].map(function (k) { return v[Math.round(k * v.length / 5)]; });
    }
    function clase(v, c) {
      if (v == null) return -1;
      var i = 0;
      while (i < 4 && v >= c[i]) i++;
      return i;
    }

    function pinta() {
      var o = orden(), c = cortes(o), pal = PAL[lente.pal];
      Array.prototype.forEach.call(raiz.querySelectorAll('.tt-edo'), function (p) {
        var e = porA[p.getAttribute('data-a')], k = e ? clase(e[lente.id], c) : -1;
        p.style.fill = k < 0 ? 'url(#ttRaya)' : pal[k];
        p.classList.toggle('sel', !!sel && p.getAttribute('data-a') === sel);
        if (e) p.setAttribute('aria-label', e.n + ': ' + (e[lente.id] == null ? 'pendiente' : fmt(e[lente.id], lente.fmt)));
      });
      var lim = [o[o.length - 1][lente.id]].concat(c);
      document.getElementById('ttLeyenda').innerHTML =
        '<span class="tt-ley-tit">' + esc(lente.nom) + '</span><span class="tt-ley-cls">' +
        pal.map(function (col, i) {
          return '<span><i style="background:' + col + '"></i>' + (i ? 'desde ' : '') + fmt(lim[i], lente.fmt) + '</span>';
        }).join('') + '</span><span class="tt-ley-pie">De menos a más: cada color agrupa a seis o siete entidades.' +
        (lente.falta ? ' Con rayas, sin dato.' : '') + '</span>';
      document.getElementById('ttQue').innerHTML = esc(lente.que) + ' ' + chip(lente.est);
      document.getElementById('ttFuente').innerHTML = '<b>Fuente:</b> ' + lente.fuente +
        (lente.falta ? ' ' + esc(lente.falta_txt) + ' ' + chip('pendiente', lente.falta_pend) : '');
      var cu = document.getElementById('ttCuadre');
      cu.innerHTML = lente.cuadre || '';
      cu.hidden = !lente.cuadre;
      resumen(o);
      ranking(o);
      ficha();
    }

    function caja(k, v, pie) {
      return '<div class="pm-kpi"><span class="pm-kpi-k">' + k + '</span><b class="pm-kpi-v num-tabular">' + v + '</b>' +
        (pie ? '<small>' + pie + '</small>' : '') + '</div>';
    }
    function resumen(o) {
      var v = o.map(function (e) { return e[lente.id]; });
      var s = v.reduce(function (a, b) { return a + b; }, 0);
      var cre = v.slice().sort(function (a, b) { return a - b; });
      var n = cre.length, med = n % 2 ? cre[(n - 1) / 2] : (cre[n / 2 - 1] + cre[n / 2]) / 2;
      /* Sumar pesos por habitante o porcentajes no significa nada: ahí van
         el promedio y la mediana. */
      document.getElementById('ttRes').innerHTML = '<div class="pm-kpis tt-kpis">' +
        (lente.suma ? caja('Suma de las ' + n + ' ' + chip('derivado'), fmt(s, lente.fmt)) : caja('Promedio de las ' + n + ' ' + chip('derivado'), fmt(s / n, lente.fmt))) +
        (lente.suma ? caja('Promedio por entidad ' + chip('derivado'), fmt(s / n, lente.fmt)) : caja('Mediana ' + chip('derivado'), fmt(med, lente.fmt))) +
        caja('La mayor', fmt(o[0][lente.id], lente.fmt), esc(o[0].n)) +
        caja('La menor', fmt(o[n - 1][lente.id], lente.fmt), esc(o[n - 1].n)) + '</div>';
    }

    function ranking(o) {
      var mayor = o[0][lente.id] || 1;
      document.getElementById('ttRankTxt').textContent = 'Las 32 entidades por ' + lente.nom.toLowerCase() +
        '. ' + (lente.id === 'gasto' ? 'Cada barra se parte en sus dos ramos: el 28, que el estado gasta con libertad, y el 33, que llega etiquetado. ' : '') +
        'Toca una para ver su ficha.';
      var faltan = D.e.filter(function (e) { return e[lente.id] == null; });
      document.getElementById('ttRank').innerHTML = o.map(function (e, i) {
        var w = Math.max(0.8, e[lente.id] / mayor * 100), barra;
        if (lente.id === 'gasto') {
          barra = '<span class="tt-rank-b"><span class="tt-r28" style="width:' + (e.r28 / mayor * 100).toFixed(2) + '%"></span>' +
            '<span class="tt-r33" style="width:' + (e.r33 / mayor * 100).toFixed(2) + '%"></span></span>';
        } else {
          barra = '<span class="tt-rank-b"><span style="width:' + w.toFixed(2) + '%;background:' + PAL[lente.pal][3] + '"></span></span>';
        }
        return '<li><button type="button" class="tt-rank-f' + (e.a === sel ? ' sel' : '') + '" data-a="' + e.a + '">' +
          '<span class="tt-rank-n">' + (i + 1) + '</span><span class="tt-rank-nom">' + esc(e.n) + '</span>' + barra +
          '<b class="num-tabular">' + fmt(e[lente.id], lente.fmt) + '</b></button></li>';
      }).join('') + faltan.map(function (e) {
        return '<li><button type="button" class="tt-rank-f tt-rank-sin" data-a="' + e.a + '"><span class="tt-rank-n">—</span>' +
          '<span class="tt-rank-nom">' + esc(e.n) + '</span><span class="tt-rank-b"></span><b>' + chip('pendiente', lente.falta_pend) + '</b></button></li>';
      }).join('');
    }

    function ficha() {
      var f = document.getElementById('ttFicha');
      var e = sel && porA[sel];
      if (!e) {
        f.innerHTML = '<p class="tt-ficha-vacia">👆 Toca un estado en el mapa o en el cuadro de abajo para ver su ficha.</p>' +
          '<p class="tt-ficha-ley"><span class="tt-r28"></span> Ramo 28 · participaciones<br><span class="tt-r33"></span> Ramo 33 · aportaciones</p>';
        return;
      }
      var pos = orden().map(function (x) { return x.a; }).indexOf(e.a) + 1;
      f.innerHTML = '<h3>' + esc(e.n) + '</h3>' +
        '<p class="tt-ficha-v"><small>' + esc(lente.nom) + '</small><b class="num-tabular">' +
        (e[lente.id] == null ? chip('pendiente', lente.falta_pend) : fmt(e[lente.id], lente.fmt)) + '</b>' +
        (pos ? '<small>Lugar ' + pos + ' de ' + orden().length + '</small>' : '') + '</p>' +
        '<dl class="tt-ficha-dl">' +
        '<dt>Ramo 28 · participaciones</dt><dd>' + mdp(e.r28) + ' ' + chip('oficial') + '</dd>' +
        '<dt>Ramo 33 · aportaciones</dt><dd>' + mdp(e.r33) + ' ' + chip('oficial') + '</dd>' +
        '<dt>Por aclarar ante la ASF (2024)</dt><dd>' + mdp(e.asf) + ' · ' + e.aud + ' auditorías ' + chip('oficial') + '</dd>' +
        '<dt>Deuda registrada</dt><dd>' + mdp(e.deuda) + ' · semáforo ' + esc(e.sem.toLowerCase()) + ' ' + chip('oficial') + '</dd>' +
        '</dl><p class="tt-ficha-ir"><a href="' + D.ent + '?e=' + encodeURIComponent(e.a) + '#circuito">Su circuito: de dónde viene cada peso ➔</a>' +
        '<a href="' + D.mun + '?e=' + encodeURIComponent(e.a) + '#padron">Sus municipios, uno por uno ➔</a></p>';
    }

    function elige(a) { sel = a; pinta(); }

    raiz.querySelector('.tt-lentes').addEventListener('click', function (ev) {
      var b = ev.target.closest('.tt-lente');
      if (!b) return;
      D.lentes.forEach(function (l) { if (l.id === b.getAttribute('data-l')) lente = l; });
      Array.prototype.forEach.call(raiz.querySelectorAll('.tt-lente'), function (x) {
        x.setAttribute('aria-checked', x === b ? 'true' : 'false');
      });
      pinta();
    });
    var svg = raiz.querySelector('.tt-svg');
    svg.insertAdjacentHTML('afterbegin', '<defs><pattern id="ttRaya" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">' +
      '<rect width="6" height="6" fill="#eef2f8"/><line x1="0" y1="0" x2="0" y2="6" stroke="#a8b3c7" stroke-width="2"/></pattern></defs>');
    svg.addEventListener('click', function (ev) {
      var p = ev.target.closest('.tt-edo');
      if (p) elige(p.getAttribute('data-a'));
    });
    svg.addEventListener('keydown', function (ev) {
      var p = ev.target.closest('.tt-edo');
      if (p && (ev.key === 'Enter' || ev.key === ' ')) { ev.preventDefault(); elige(p.getAttribute('data-a')); }
    });
    document.getElementById('ttRank').addEventListener('click', function (ev) {
      var b = ev.target.closest('.tt-rank-f');
      if (!b) return;
      elige(b.getAttribute('data-a'));
      raiz.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    sel = pedida();
    pinta();
  })();

  /* ------------------------------------------------------------------
     2 · El circuito de cada estado
     ------------------------------------------------------------------ */
  (function () {
    var D = datos('ttEntDatos'), s = document.getElementById('ttEntSel'), caja = document.getElementById('ttCirc');
    if (!D || !s || !caja) return;
    function pinta(a) {
      var e = D.e.filter(function (x) { return x.a === a; })[0] || D.e[0];
      s.value = e.a;
      var sinDato = e.propia == null;
      var filas = [
        ['Ramo 28 · participaciones', 'De libre disposición', e.r28, 'tt-r28', 'oficial'],
        ['Ramo 33 · aportaciones', 'Etiquetado por ley', e.r33, 'tt-r33', 'oficial'],
        ['Convenios (2024)', 'Reasignados por las secretarías, caso por caso', e.conv, 'tt-conv', 'oficial'],
        ['Recaudación propia (2024)', 'Lo que el estado cobró por su cuenta', e.propia, 'tt-propia', 'derivado']
      ];
      var mayor = Math.max.apply(null, filas.map(function (f) { return f[2] || 0; })) || 1;
      var baja = e.r28 + e.r33;
      var razon = (e.fed24 && e.propia) ? num(e.fed24 / e.propia, 1) + ' pesos' : null;
      caja.innerHTML =
        '<div class="tt-circ-cab"><div><h3>' + esc(e.n) + '</h3><p>' + esc(e.cap) + ' · ' + num(e.pob, 2) + ' millones de habitantes ' + chip('derivado') +
        ' · gobierna ' + esc(e.gob) + '</p></div>' +
        '<div class="tt-dep"><b class="num-tabular">' + (e.dep == null ? '—' : num(e.dep, 1) + '%') + '</b>' +
        '<span>de dependencia federal en 2024 ' + (e.dep == null ? chip('pendiente', D.pend) : chip('derivado')) + '</span>' +
        (e.dep == null ? '' : '<span class="tt-dep-b"><span style="width:' + Math.min(100, e.dep).toFixed(1) + '%"></span></span>') + '</div></div>' +
        '<div class="tt-circ-filas">' + filas.map(function (f) {
          return '<div class="tt-circ-f"><span class="tt-circ-n"><b>' + f[0] + '</b><small>' + f[1] + '</small></span>' +
            '<span class="tt-circ-b"><span class="' + f[3] + '" style="width:' + (f[2] == null ? 0 : Math.max(0.8, f[2] / mayor * 100)).toFixed(2) + '%"></span></span>' +
            '<b class="num-tabular">' + (f[2] == null ? chip('pendiente', D.pend) : mdp(f[2]) + ' ' + chip(f[4])) + '</b></div>';
        }).join('') + '</div>' +
        '<div class="pm-kpis tt-kpis">' +
        '<div class="pm-kpi"><span class="pm-kpi-k">Le bajan por los Ramos 28 y 33 ' + chip('derivado') + '</span><b class="pm-kpi-v num-tabular">' + mdp(baja) + '</b><small>2026</small></div>' +
        '<div class="pm-kpi pm-green"><span class="pm-kpi-k">Cobró por su cuenta ' + (sinDato ? chip('pendiente', D.pend) : chip('derivado')) + '</span><b class="pm-kpi-v num-tabular">' + (sinDato ? '—' : mdp(e.propia)) + '</b><small>2024</small></div>' +
        '<div class="pm-kpi"><span class="pm-kpi-k">Por cada peso propio recibió de la Federación ' + (razon ? chip('derivado') : chip('pendiente', D.pend)) + '</span><b class="pm-kpi-v num-tabular">' + (razon || '—') + '</b><small>' + (razon ? 'Federal 2024 ÷ propio 2024' : 'Sin cifras de 2024') + '</small></div>' +
        '<div class="pm-kpi pm-red"><span class="pm-kpi-k">Deuda registrada ' + chip('oficial') + '</span><b class="pm-kpi-v num-tabular">' + mdp(e.deuda) + '</b><small>Semáforo ' + esc(e.sem.toLowerCase()) + ' del Sistema de Alertas</small></div>' +
        '</div>' +
        (sinDato ? '<p class="pm-ciego">La Ciudad de México no figura en la estadística estatal del INEGI: sus convenios, su recaudación propia y su dependencia de 2024 siguen pendientes.</p>' : '') +
        '<p class="tt-circ-ir"><a href="' + D.mapa + '?e=' + encodeURIComponent(e.a) + '">📍 Verlo en el mapa ➔</a><a href="' + D.mun + '?e=' + encodeURIComponent(e.a) + '#padron">🏘️ Sus municipios, uno por uno ➔</a></p>';
    }
    s.addEventListener('change', function () {
      pinta(s.value);
      try { history.replaceState(null, '', '?e=' + encodeURIComponent(s.value) + '#circuito'); } catch (err) { /* sin historial */ }
    });
    pinta(pedida() || s.value);
  })();

  /* ------------------------------------------------------------------
     3 · El padrón municipal
     ------------------------------------------------------------------ */
  (function () {
    var D = datos('ttMunDatos'), cont = document.getElementById('ttMun');
    var F = window.AUDIT_MUNICIPIOS;
    if (!D || !cont) return;
    if (!F || !F.ent) {
      cont.innerHTML = '<p class="pm-ciego">No se pudo cargar el padrón municipal del INEGI. Recarga la página.</p>';
      return;
    }
    var s = document.getElementById('ttMunSel'), busca = document.getElementById('ttMunBusca'), ord = document.getElementById('ttMunOrden');
    /* Los nombres de las entidades llegan con los datos de la pagina. */
    var NOM = D.nom || {};
    var claves = Object.keys(F.ent).sort(function (a, b) { return (NOM[a] || a).localeCompare(NOM[b] || b, 'es'); });
    s.innerHTML = claves.map(function (a) { return '<option value="' + a + '">' + esc(NOM[a] || a) + '</option>'; }).join('');
    function plano(t) { return String(t).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
    function filas(a) {
      var e = F.ent[a];
      return e.lista.map(function (f) {
        var hay = f.length === 10, ing = hay ? f[2] / 1e6 : null;
        return { cve: e.cve + f[0], nom: f[1], hay: hay, ing: ing, part: hay ? f[3] / 1e6 : null,
          fortamun: hay ? f[5] / 1e6 : null, fismdf: hay ? f[6] / 1e6 : null, predial: hay ? f[7] / 1e6 : null,
          dep: (hay && ing > 0) ? (f[3] + f[4]) / f[2] * 100 : null };
      });
    }
    function celda(v) { return v == null ? '<td class="tt-nada">—</td>' : '<td>$' + num(v, 1) + '</td>'; }
    function pinta() {
      var a = s.value, e = F.ent[a], q = plano(busca.value || ''), c = ord.value;
      var cdmx = a === 'CDMX', voz = cdmx ? 'demarcaciones territoriales' : 'municipios';
      var l = filas(a).filter(function (m) { return !q || plano(m.nom).indexOf(q) !== -1; });
      l.sort(function (x, y) {
        if (c === 'nombre') return x.nom.localeCompare(y.nom, 'es');
        if (x.hay !== y.hay) return x.hay ? -1 : 1;
        return (y[c] || 0) - (x[c] || 0);
      });
      var t = e.tot || {}, sinRep = e.n - e.conCifra;
      var depEnt = t.ing > 0 ? (t.part + t.aport) / t.ing * 100 : null;
      var h = '<div class="tt-mun-res"><h3>' + esc(NOM[a] || a) + '</h3><p>' + e.n + ' ' + voz + ' en el catálogo del INEGI' +
        (e.conCifra ? ' · <b>' + e.conCifra + '</b> rindieron cuenta en ' + F.anio : '') +
        (e.conCifra && sinRep ? ' · <span class="tt-falta">' + sinRep + ' sin reporte</span> ' + chip('pendiente', D.pend) : '') + '</p>';
      if (cdmx && !e.conCifra) {
        h += '<p class="pm-ciego"><b>La Ciudad de México no tiene municipios.</b> Tiene dieciséis demarcaciones territoriales a cargo de alcaldías, ' +
          'y el artículo 122, apartado A, fracción VI de la Constitución dispone que la Legislatura de la Ciudad apruebe su presupuesto. ' +
          'No tienen la hacienda propia que el artículo 115 reconoce a los municipios; por eso el INEGI no las levanta en su estadística municipal, ' +
          'y aquí aparecen sin cifra en lugar de en ceros.</p>';
      } else if (e.conCifra) {
        h += '<div class="pm-kpis tt-kpis">' + [['Ingreso total', t.ing], ['Participaciones', t.part], ['Predial cobrado', t.predial],
          ['FORTAMUN', t.fortamun], ['FISMDF', t.fismdf]].map(function (k) {
          return '<div class="pm-kpi"><span class="pm-kpi-k">' + k[0] + ' ' + chip('derivado') + '</span><b class="pm-kpi-v num-tabular">$' + num(k[1] / 1e6, 1) + '</b><small>mdp, suma de sus municipios</small></div>';
        }).join('') + '</div>' +
        '<p class="tt-mun-dep">Dependencia de transferencias de sus municipios: <b>' + num(depEnt, 1) + '%</b> ' + chip('derivado') +
        '<span class="tt-dep-b"><span style="width:' + Math.min(100, depEnt).toFixed(1) + '%"></span></span></p>';
      }
      h += '</div>';
      if (!l.length) {
        cont.innerHTML = h + '<p class="pm-ciego">Ningún municipio de ' + esc(NOM[a] || a) + ' coincide con «' + esc(busca.value) + '».</p>';
        return;
      }
      h += '<div class="tt-tabla-marco"><table class="tt-tabla"><caption class="sr-only">Ingresos de los ' + voz + ' de ' + esc(NOM[a] || a) +
        ' en ' + F.anio + ', en millones de pesos</caption><thead><tr><th scope="col">Municipio</th><th scope="col">Ingreso total</th>' +
        '<th scope="col">Participaciones</th><th scope="col">Predial</th><th scope="col">FORTAMUN</th><th scope="col">FISMDF</th>' +
        '<th scope="col">Dependencia</th></tr></thead><tbody>' + l.map(function (m) {
          if (!m.hay) {
            return '<tr class="tt-sin"><th scope="row"><small>' + m.cve + '</small>' + esc(m.nom) + '</th><td colspan="6">' +
              (cdmx ? 'Su presupuesto lo aprueba el Congreso de la Ciudad' : 'No rindió cuenta pública ' + F.anio + ' ante el INEGI') + '</td></tr>';
          }
          return '<tr><th scope="row"><small>' + m.cve + '</small>' + esc(m.nom) + '</th>' + celda(m.ing) + celda(m.part) + celda(m.predial) +
            celda(m.fortamun) + celda(m.fismdf) + '<td class="tt-dep-c"><span class="tt-dep-b"><span style="width:' + Math.min(100, m.dep || 0).toFixed(1) +
            '%"></span></span>' + (m.dep == null ? '—' : num(m.dep, 1) + '%') + '</td></tr>';
        }).join('') + '</tbody></table></div>' +
        '<p class="pm-pie">' + esc(F.fuente) + ' Cifras en millones de pesos. La <b>dependencia</b> es cuánto de cada $100 que ingresó el municipio vino de participaciones y aportaciones, no de lo que cobró por su cuenta ' + chip('derivado') + '.</p>' +
        '<p class="tt-circ-ir"><a href="' + D.ent + '?e=' + encodeURIComponent(a) + '#circuito">🗺️ El circuito del estado ➔</a><a href="' + D.mapa + '?e=' + encodeURIComponent(a) + '">📍 Verlo en el mapa ➔</a></p>';
      cont.innerHTML = h;
    }
    s.addEventListener('change', function () {
      busca.value = '';
      pinta();
      try { history.replaceState(null, '', '?e=' + encodeURIComponent(s.value) + '#padron'); } catch (err) { /* sin historial */ }
    });
    busca.addEventListener('input', pinta);
    ord.addEventListener('change', pinta);
    var p = pedida();
    if (p && F.ent[p]) s.value = p;
    pinta();
  })();
})();
