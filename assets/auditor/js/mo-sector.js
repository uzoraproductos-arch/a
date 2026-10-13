/* Auditavisión · Inversión y Megaobras › Sector e industria (aplicación 2,
   13-10-2026). La página la escribe herramientas/mo_sector.py con las
   fichas de las 13 obras ya pintadas y, en JSON (#msDatos), las mismas
   cifras que usa el motor después de megaobrasOficialBase(): aquí no se
   escribe ninguna cifra nueva, solo se suman las obras que deja el filtro.
   Industria y mandato filtran a la vez; la comparativa se ordena por cinco
   criterios; las fichas corren en vivo; la escala divide el costo real del
   filtro entre cifras conocidas. El filtro vive en la dirección
   (?industria=&mandato=&orden=) con replaceState, para no llenar el
   historial; cada obra tiene su ancla #obra-<id>. */
(function () {
  'use strict';

  var D;
  try { D = JSON.parse(document.getElementById('msDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  var raiz = $('msRaiz');
  if (!raiz) return;
  var qsa = function (sel, r) { return [].slice.call((r || raiz).querySelectorAll(sel)); };

  var OBRAS = D.obras;
  var TOTAL = OBRAS.length;
  var PER_ET = { dia: 'al día', mes: 'al mes', trimestre: 'por trimestre', semestre: 'por semestre', ano: 'al año' };
  var PER_NOM = { dia: 'día', mes: 'mes', trimestre: 'trimestre', semestre: 'semestre', ano: 'año' };
  var reducido = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var est = { sector: 'todos', mandato: 'todos', orden: 'perdida', universo: false, auto: true, per: 'dia', evaluado: false };
  var inicio = Date.now();
  var marcos = {};

  /* ---------- formatos (los mismos del motor) ---------- */
  function n(v) { return Number(v).toLocaleString('es-MX'); }
  function simMdp(v) {
    var a = Math.abs(v);
    if (a >= 1000000) return '$' + (v / 1000000).toFixed(2) + ' billones';
    if (a >= 1000) return '$' + n(Math.round(v / 100) / 10) + ' mil millones';
    return '$' + n(Math.round(v * 100) / 100) + ' millones';
  }
  function fmt(v, f) {
    if (f === 'pct') return v.toFixed(1) + '%';
    if (f === 'pctS') return (v > 0 ? '+' : '') + v.toFixed(1) + '%';
    if (f === 'pesos') return '$' + n(Math.round(v * 100) / 100);
    return simMdp(v);
  }
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function chip(e, pend) {
    return '<span class="est-chip est-' + e + '"' + (pend ? ' data-pend="' + esc(pend) + '"' : '') + '>' + e + '</span>';
  }
  function guarda(k, v) { try { localStorage.setItem('av-mo-sector-' + k, v); } catch (e) { /* sin almacenamiento */ } }
  function lee(k) { try { return localStorage.getItem('av-mo-sector-' + k); } catch (e) { return null; } }

  /* ---------- filtro y agregados (simObrasDe, simFiltradas, simAgregados) ---------- */
  var ORDEN_F = {
    perdida: function (a, b) { return b.perd - a.perd; },
    sobrecosto: function (a, b) { return b.sob - a.sob; },
    inversion: function (a, b) { return b.real - a.real; },
    brecha: function (a, b) { return (b.real - b.presu) - (a.real - a.presu); },
    cronologia: function (a, b) { return String(a.per).localeCompare(String(b.per)); }
  };
  function valor(o, orden) {
    return { perdida: o.perd, sobrecosto: o.sob, inversion: o.real, brecha: o.real - o.presu, cronologia: o.real }[orden];
  }
  function de(sector, mandato) {
    return OBRAS.filter(function (o) {
      if (sector && sector !== 'todos' && o.s !== sector) return false;
      if (mandato && mandato !== 'todos' && o.p.toLowerCase().indexOf(mandato.toLowerCase()) < 0) return false;
      return true;
    });
  }
  function filtradas() { return de(est.sector, est.mandato).sort(ORDEN_F[est.orden]); }
  function agregados(obras) {
    var s = function (f) { return obras.reduce(function (a, o) { return a + (Number(o[f]) || 0); }, 0); };
    var real = s('real'), presu = s('presu'), anual = s('perd');
    return { n: obras.length, real: real, presu: presu, brecha: real - presu,
      sobrecosto: presu > 0 ? (real / presu - 1) * 100 : 0, perdidaAnual: anual, perdidaSegundo: anual * 1000000 / (365 * 86400) };
  }
  var AG_T = agregados(OBRAS);
  var porSector = {};
  D.sectores.forEach(function (s) { porSector[s.id] = s; });
  function sexenio(k) { return D.sexenios.filter(function (x) { return x.k === k; })[0] || null; }
  function ordenEt(id) { return D.ordenes.filter(function (x) { return x.id === id; })[0].et; }

  /* ---------- animación de cifras y barras (simAnimarZona) ---------- */
  function animar(clave, els, barras, dur, fin) {
    if (marcos[clave]) cancelAnimationFrame(marcos[clave]);
    var pinta = function (e) {
      els.forEach(function (el) { el.textContent = fmt(parseFloat(el.dataset.v) * e, el.dataset.f); });
      barras.forEach(function (b) { b.style.width = (parseFloat(b.dataset.w) * e).toFixed(2) + '%'; });
    };
    if (reducido || !dur) { pinta(1); if (fin) fin(); return; }
    var t0 = performance.now();
    var paso = function (t) {
      var x = Math.min(1, (t - t0) / dur);
      var e = (--x) * x * x + 1;
      pinta(Math.min(1, e));
      if (t - t0 < dur) marcos[clave] = requestAnimationFrame(paso);
      else { delete marcos[clave]; pinta(1); if (fin) fin(); }
    };
    pinta(0);
    marcos[clave] = requestAnimationFrame(paso);
  }

  /* ---------- pasos 1 y 2 ---------- */
  function pintaMosaico() {
    var universo = de('todos', est.mandato);
    var total = universo.reduce(function (a, o) { return a + o.real; }, 0) || 1;
    qsa('.ms-los').forEach(function (b) {
      var ob = de(b.dataset.sector, est.mandato);
      var real = ob.reduce(function (a, o) { return a + o.real; }, 0);
      var cuota = real / total * 100;
      b.querySelector('.ms-los-cif').textContent = simMdp(real);
      b.querySelector('.ms-barra').style.width = cuota.toFixed(1) + '%';
      b.querySelector('.ms-los-n').textContent = ob.length + (ob.length === 1 ? ' obra' : ' obras');
      b.querySelector('.ms-los-cuota').textContent = cuota.toFixed(1) + '% del costo real';
      b.classList.toggle('ms-vacia', ob.length === 0);
      b.setAttribute('aria-pressed', b.dataset.sector === est.sector ? 'true' : 'false');
    });
    qsa('.ms-todas').forEach(function (b) { b.setAttribute('aria-pressed', est.sector === 'todos' ? 'true' : 'false'); });
    var sx = sexenio(est.mandato);
    $('msMosaicoNota').textContent = sx ? 'bajo ' + sx.nom + ' (' + sx.ini + '–' + sx.fin + ')' : 'en los seis mandatos';
  }
  function pintaMandatos() {
    qsa('.ms-mdt').forEach(function (b) {
      var c = de(est.sector, b.dataset.mandato).length;
      b.querySelector('.ms-mdt-n').textContent = c + (c === 1 ? ' obra' : ' obras');
      b.classList.toggle('ms-vacia', c === 0);
      b.setAttribute('aria-pressed', b.dataset.mandato === est.mandato ? 'true' : 'false');
    });
  }

  /* ---------- lo que dejó el filtro (renderSimuladorDesgloseCab) ---------- */
  function pintaFiltro(obras, animado) {
    var sec = porSector[est.sector], sx = sexenio(est.mandato);
    var ag = agregados(obras);
    var cuota = AG_T.real > 0 ? ag.real / AG_T.real * 100 : 0;
    $('msFa').innerHTML =
      '<span class="ms-fa-chip">' + (sec ? sec.ico + ' ' + esc(sec.nom) : '🌐 Todas las industrias') + '</span>' +
      '<span class="ms-fa-chip">' + (sx ? '🏛️ ' + esc(sx.nom) + ' · ' + sx.ini + '–' + sx.fin : '🏛️ Todos los mandatos') + '</span>' +
      '<span class="ms-fa-n"><b>' + ag.n + '</b> de ' + TOTAL + ' obras</span>';
    $('msQuitar').hidden = !(sec || sx);
    var pares = [['msCReal', ag.real, 'mdp'], ['msCCuota', cuota, 'pct'], ['msCPresu', ag.presu, 'mdp'], ['msCBrecha', ag.brecha, 'mdp'],
      ['msCSob', ag.sobrecosto, 'pctS'], ['msCPerd', ag.perdidaAnual, 'mdp'], ['msCSeg', ag.perdidaSegundo, 'pesos']];
    var els = pares.map(function (p) { var el = $(p[0]); el.dataset.v = p[1]; el.dataset.f = p[2]; return el; });
    animar('cab', els, [], animado ? 900 : 0);
    var pr = obras.filter(function (o) { return o.pendReal; });
    var doc = obras.filter(function (o) { return !o.pend; }).length;
    $('msNotaFiltro').innerHTML = !obras.length ? '' :
      'La pérdida tiene documento en <b>' + doc + '</b> de ' + obras.length + (obras.length === 1 ? ' obra.' : ' obras.') +
      (pr.length ? ' ' + (pr.length === 1 ? 'Una obra del filtro tiene' : pr.length + ' obras del filtro tienen') +
        ' su costo real ' + chip('pendiente', 'obra-' + pr[0].id) + ' de documento y entra con la cifra que registra el simulador: ' +
        pr.map(function (o) { return '<a href="pendientes.html#obra-' + esc(o.id) + '">' + esc(o.n) + '</a>'; }).join(', ') + '.' : '');
    $('msResumen').innerHTML = 'Estás viendo <b>' + ag.n + '</b> de ' + TOTAL + ' obras' +
      (sec ? ' · ' + sec.ico + ' ' + esc(sec.nom) : '') + (sx ? ' · 🏛️ ' + esc(sx.nom) : '') +
      ' · costo real <b class="ms-num">' + simMdp(ag.real) + '</b>';
  }

  /* ---------- la comparativa (renderSimuladorRankingFiltro) ---------- */
  function estadoTexto(c) {
    return est.evaluado ? '✓ Evaluación completada: ' + (c === 1 ? 'la obra' : 'las ' + c + ' obras') + ' a escala real.'
      : '⚪ Barras en reposo. Pulsa «Evaluar» para medir la escala real.';
  }
  function pintaComparativa(delFiltro) {
    var hayFiltro = est.sector !== 'todos' || est.mandato !== 'todos';
    var obras = (est.universo ? OBRAS.slice() : delFiltro.slice()).sort(ORDEN_F[est.orden]);
    var dentro = {};
    delFiltro.forEach(function (o) { dentro[o.id] = true; });
    qsa('.ms-orden').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.orden === est.orden ? 'true' : 'false'); });
    $('msUniverso').checked = est.universo;
    var filas = $('msFilas'), aviso = $('msCompAviso');
    est.evaluado = false;
    if (!obras.length) {
      $('msCompTitTx').textContent = 'Ninguna obra en el filtro';
      $('msCompSub').textContent = '';
      filas.innerHTML = '';
      $('msRankEstado').textContent = '';
      aviso.innerHTML = '<p class="ms-aviso-in">Con estos filtros no queda <strong>ninguna obra</strong>. Quita uno de los dos filtros, o ' +
        '<button type="button" class="ms-enlace" data-accion="universo">ve las ' + TOTAL + ' obras en contexto</button>.</p>';
      return;
    }
    var sola = obras.length === 1;
    var rotulo = est.orden === 'cronologia' ? 'costo real, en orden cronológico' : ordenEt(est.orden).toLowerCase();
    var todoPend = est.orden === 'perdida' && obras.every(function (o) { return o.pend; });
    var todoCero = !todoPend && obras.every(function (o) { return !valor(o, est.orden); });
    var sobre = sola ? OBRAS : obras;
    var maximo = Math.max.apply(null, sobre.map(function (o) { return Math.abs(valor(o, est.orden)); })) || 1;
    var f = est.orden === 'sobrecosto' ? 'pctS' : 'mdp';
    var marcadas = obras.filter(function (o) { return dentro[o.id]; }).length;
    $('msCompTitTx').textContent = sola ? 'La única obra del filtro, medida por ' + rotulo
      : (est.universo ? 'Las ' + obras.length + ' obras, comparadas por ' + rotulo : 'Las ' + obras.length + ' obras del filtro, comparadas por ' + rotulo);
    $('msCompSub').innerHTML = est.universo
      ? (hayFiltro ? 'Estás viendo el universo completo. Tu selección señala <strong>' + marcadas + '</strong> de las ' + obras.length +
          ' obras; las demás siguen presentes, atenuadas, para no perder la escala de comparación. Pulsa una atenuada para ponerla en el filtro.'
        : 'Estás viendo el universo completo. Elige una industria o un mandato para que la lista resalte las obras que le tocan.')
      : (sola ? 'El filtro dejó una sola obra, así que no hay con quién compararla dentro de la lista: la barra la mide contra la obra mayor de las ' +
          TOTAL + ' del universo. Si quieres verla junto a las demás, enciende «Ver las ' + TOTAL + ' en contexto».'
        : 'La barra mide el tamaño de la cifra frente a la mayor de esta lista. Pulsa cualquier renglón para ver su ficha en la simulación en vivo.');
    filas.innerHTML = obras.map(function (o, i) {
      var v = valor(o, est.orden);
      var fuera = est.universo && hayFiltro && !dentro[o.id];
      var cuerpo = '<span class="ms-fila-n">' + (i + 1) + '</span><span class="ms-fila-ico" aria-hidden="true">' + o.ico + '</span>' +
        '<span class="ms-fila-nom">' + esc(o.n) + '<small>' + esc(o.p) + ' · ' + esc(o.per) + '</small></span>' +
        '<span class="ms-fila-riel"><span class="ms-fila-barra" data-w="' + (Math.abs(v) / maximo * 100).toFixed(2) + '" style="width:0%;--ms-c:' + esc(o.color) + '"></span></span>' +
        (est.orden === 'perdida' && o.pend ? '<span class="ms-fila-val">' + chip('pendiente', 'reloj-megaobras') + '</span>'
          : '<span class="ms-fila-val ms-num" data-v="' + v + '" data-f="' + f + '">' + fmt(0, f) + '</span>');
      return '<li class="ms-fila' + (fuera ? ' ms-fuera' : '') + '">' +
        (fuera ? '<button type="button" class="ms-fila-b" data-ir="' + esc(o.id) + '" title="Poner esta obra en el filtro e ir a su ficha">' + cuerpo + '</button>'
          : '<a class="ms-fila-b" href="#obra-' + esc(o.id) + '" data-obra="' + esc(o.id) + '">' + cuerpo + '</a>') + '</li>';
    }).join('');
    aviso.innerHTML =
      (todoPend ? '<p class="ms-aviso-in"><strong>Sin documento todavía.</strong> ' + (sola ? 'Esta obra no tiene' : 'Ninguna de estas obras tiene') +
        ' un estado financiero o informe oficial publicado que diga cuánto pierde al operar: es falta de transparencia de quien la opera, y la cifra no se estima. ' +
        '<button type="button" class="ms-enlace" data-accion="inversion">Mide por costo real</button>.</p>' : '') +
      (todoCero ? '<p class="ms-aviso-in"><strong>Sin cifra bajo este criterio, y no por falta de datos.</strong> ' + (sola ? 'Esta obra no registra ' : 'Ninguna de estas obras registra ') +
        rotulo + ': el registro es cero, no un hueco. Lo que sí costaron se ve <button type="button" class="ms-enlace" data-accion="inversion">midiendo por costo real</button>.</p>' : '');
    $('msRankEstado').textContent = estadoTexto(obras.length);
    $('msEvaluar').innerHTML = '<span aria-hidden="true">▶️</span> Evaluar ' + (sola ? 'la obra' : 'las ' + obras.length + ' obras');
    if (reducido) evaluar(0);
    else if (est.auto && enVista) evaluar();
  }
  function evaluar(dur) {
    var filas = $('msFilas');
    var c = qsa('.ms-fila', filas).length;
    if (!c) return;
    $('msRankEstado').textContent = '⚡ Escalando ' + (c === 1 ? 'la obra' : 'las ' + c + ' obras') + '…';
    animar('rank', qsa('[data-v]', filas), qsa('[data-w]', filas), dur === undefined ? 1200 : dur, function () {
      est.evaluado = true;
      $('msRankEstado').textContent = estadoTexto(c);
      $('msEvaluar').innerHTML = '<span aria-hidden="true">🔄</span> Volver a evaluar';
    });
  }
  function reiniciar() {
    if (marcos.rank) { cancelAnimationFrame(marcos.rank); delete marcos.rank; }
    var filas = $('msFilas');
    qsa('[data-w]', filas).forEach(function (b) { b.style.width = '0%'; });
    qsa('[data-v]', filas).forEach(function (el) { el.textContent = fmt(0, el.dataset.f); });
    est.evaluado = false;
    var c = qsa('.ms-fila', filas).length;
    $('msRankEstado').textContent = estadoTexto(c);
    $('msEvaluar').innerHTML = '<span aria-hidden="true">▶️</span> Evaluar ' + (c === 1 ? 'la obra' : 'las ' + c + ' obras');
  }

  /* ---------- fichas en vivo (renderSimuladorObrasGrid, simVivoTotal) ---------- */
  function pintaFichas(obras) {
    var caja = $('msFichas');
    var dentro = {};
    obras.forEach(function (o) { dentro[o.id] = true; });
    obras.forEach(function (o) { var el = $('obra-' + o.id); if (el) caja.appendChild(el); });
    qsa('.ms-ficha', caja).forEach(function (el) { el.hidden = !dentro[el.dataset.id]; });
    var vacio = $('msVacio');
    vacio.hidden = obras.length > 0;
    if (!obras.length) {
      var sec = porSector[est.sector], sx = sexenio(est.mandato);
      var ns = sec ? sec.nom : 'esa industria', nm = sx ? sx.nom : 'ese mandato';
      vacio.innerHTML = '<p class="ms-vacio-t">Esa combinación no tiene obras evaluadas</p>' +
        '<p>No hay ninguna obra de <strong>' + esc(ns) + '</strong> contratada bajo <strong>' + esc(nm) + '</strong> dentro de las ' + TOTAL +
        ' que evalúa esta plataforma. No significa que no haya existido: significa que no está en este universo.</p>' +
        '<div class="ms-vacio-b"><button type="button" class="ms-btn ms-btn-sec" data-accion="sin-sector">🏭 Ver ' + esc(nm) + ' en todas las industrias</button>' +
        '<button type="button" class="ms-btn ms-btn-sec" data-accion="sin-mandato">🏛️ Ver ' + esc(ns) + ' en todos los mandatos</button></div>';
    }
    $('msVivoTitTx').textContent = obras.length === 1 ? 'la obra del filtro' : 'las ' + obras.length + ' obras del filtro';
    // Contador conjunto: solo las obras del filtro que sí corren.
    var corren = obras.filter(function (o) { return o.vivo != null; });
    var paradas = obras.filter(function (o) { return o.parada; });
    var anual = Math.round(corren.reduce(function (a, o) { return a + o.vivo; }, 0) * 10) / 10;
    var seg = anual * 1e6 / 31536000;
    var tot = $('msVivoTot');
    tot.dataset.rate = seg;
    tot.dataset.anual = anual;
    $('msVivoTotEt').textContent = corren.length === 1 ? 'Lo que esta obra nos cuesta' : 'Lo que estas ' + corren.length + ' obras nos cuestan';
    $('msVivoTotSub').textContent = simMdp(anual) + ' al año · $' + seg.toLocaleString('es-MX', { maximumFractionDigits: 0 }) + ' por segundo' +
      (paradas.length ? ' · ' + paradas.length + ' sin datos públicos suficientes no entran' : '');
    qsa('#msVivoTabla tbody tr').forEach(function (tr) { tr.hidden = !dentro[tr.dataset.id]; });
    var pp = $('msVivoParadas');
    pp.hidden = !paradas.length;
    pp.innerHTML = paradas.length ? '<strong>No corren (' + paradas.length + '):</strong> ' + paradas.map(function (o) { return esc(o.n); }).join(', ') +
      '. Sin información pública suficiente; cada ficha dice qué lo impide.' : '';
    pintaCadencia();
    tic();
  }
  function pintaCadencia() {
    var p = D.periodos[est.per] || D.periodos.dia;
    qsa('.ms-cad').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.per === est.per ? 'true' : 'false'); });
    qsa('.ms-vivo-caja[data-anual]').forEach(function (c) {
      if (c.dataset.anual === '') return;
      c.querySelector('.ms-vivo-monto').textContent = simMdp(parseFloat(c.dataset.anual) * p.factor) + p.sufijo;
      var et = c.querySelector('.ms-per-et');
      if (et) et.textContent = PER_ET[est.per] || '';
    });
    $('msCadEt').textContent = PER_NOM[est.per] || est.per;
    $('msVivoPer').textContent = simMdp(parseFloat($('msVivoTot').dataset.anual || 0) * p.factor) + p.sufijo;
  }
  function tic() {
    var s = (Date.now() - inicio) / 1000;
    var txt = function (rate) { return '+$' + (s * rate).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
    qsa('.ms-ficha:not([hidden]) .ms-tic').forEach(function (el) { el.textContent = txt(parseFloat(el.dataset.rate) || 0); });
    var t = $('msVivoTot');
    t.textContent = txt(parseFloat(t.dataset.rate) || 0);
  }

  /* ---------- la escala (renderSimuladorEscala) ---------- */
  function pintaEscala(obras) {
    var a = agregados(obras);
    var lista = $('msEscLista');
    if (!a.n) {
      $('msEscSub').textContent = 'Sin obras en el filtro no hay monto que comparar. Elige otra combinación de industria y mandato.';
      lista.hidden = true;
      return;
    }
    lista.hidden = false;
    $('msEscSub').innerHTML = 'El costo real de las obras filtradas suma <strong class="ms-num">' + simMdp(a.real) + '</strong>. Puesto junto a cifras conocidas, equivale a:';
    var filas = qsa('.ms-esc-fila', lista);
    var mayor = Math.max.apply(null, filas.map(function (li) { return a.real / parseFloat(li.dataset.v); })) || 1;
    filas.forEach(function (li) {
      var veces = a.real / parseFloat(li.dataset.v);
      li.querySelector('.ms-esc-veces').textContent = veces >= 1 ? veces.toFixed(2) + '×' : (veces * 100).toFixed(1) + '%';
      li.querySelector('.ms-barra').style.width = (veces / mayor * 100).toFixed(1) + '%';
    });
  }

  /* ---------- todo junto ---------- */
  function direccion() {
    try {
      var u = new URL(location.href);
      ['industria', 'mandato', 'orden'].forEach(function (k) { u.searchParams.delete(k); });
      if (est.sector !== 'todos') u.searchParams.set('industria', est.sector);
      if (est.mandato !== 'todos') u.searchParams.set('mandato', est.mandato);
      if (est.orden !== 'perdida') u.searchParams.set('orden', est.orden);
      history.replaceState(history.state, '', u.pathname + u.search + u.hash);
    } catch (e) { /* sin URL */ }
  }
  function pinta(animado) {
    var obras = filtradas();
    pintaMosaico();
    pintaMandatos();
    pintaFiltro(obras, animado);
    pintaComparativa(obras);
    pintaFichas(obras);
    pintaEscala(obras);
    direccion();
  }

  function irAObra(id, suave) {
    var o = OBRAS.filter(function (x) { return x.id === id; })[0];
    if (!o) return;
    var en = filtradas().some(function (x) { return x.id === id; });
    if (!en) {
      est.sector = o.s;
      if (est.mandato !== 'todos' && o.p.toLowerCase().indexOf(est.mandato.toLowerCase()) < 0) est.mandato = 'todos';
      pinta(false);
    }
    var el = $('obra-' + id);
    if (!el) return;
    el.scrollIntoView({ behavior: suave && !reducido ? 'smooth' : 'auto', block: 'start' });
    el.classList.remove('ms-destaca');
    void el.offsetWidth;
    el.classList.add('ms-destaca');
    try { el.focus({ preventScroll: true }); } catch (e) { /* viejo */ }
    try { history.replaceState(history.state, '', location.pathname + location.search + '#obra-' + id); } catch (e) { /* nada */ }
  }

  raiz.addEventListener('click', function (ev) {
    var t = ev.target.closest ? ev.target : null;
    if (!t) return;
    var b;
    if ((b = t.closest('[data-sector]'))) { est.sector = b.dataset.sector; guarda('orden', est.orden); pinta(true); return; }
    if ((b = t.closest('.ms-mdt'))) { est.mandato = b.dataset.mandato; pinta(true); return; }
    if ((b = t.closest('.ms-orden'))) { est.orden = b.dataset.orden; pinta(false); if (!est.auto) evaluar(600); return; }
    if ((b = t.closest('.ms-cad'))) { est.per = b.dataset.per; guarda('per', est.per); pintaCadencia(); return; }
    if ((b = t.closest('a[data-obra]'))) { ev.preventDefault(); irAObra(b.dataset.obra, true); return; }
    if ((b = t.closest('[data-ir]'))) { irAObra(b.dataset.ir, true); return; }
    if ((b = t.closest('.ms-compartir'))) { compartir(b); return; }
    if ((b = t.closest('[data-accion]'))) {
      var a = b.dataset.accion;
      if (a === 'universo') { est.universo = true; pintaComparativa(filtradas()); }
      else if (a === 'inversion') { est.orden = 'inversion'; pinta(false); }
      else if (a === 'sin-sector') { est.sector = 'todos'; pinta(true); }
      else if (a === 'sin-mandato') { est.mandato = 'todos'; pinta(true); }
    }
  });
  $('msQuitar').addEventListener('click', function () { est.sector = 'todos'; est.mandato = 'todos'; pinta(true); });
  $('msContar').addEventListener('click', function () { pintaFiltro(filtradas(), true); });
  $('msEvaluar').addEventListener('click', function () { evaluar(); });
  $('msReiniciar').addEventListener('click', reiniciar);
  $('msUniverso').addEventListener('change', function () { est.universo = this.checked; pintaComparativa(filtradas()); });
  $('msAuto').addEventListener('change', function () { est.auto = this.checked; guarda('auto', est.auto ? '1' : '0'); if (est.auto && enVista && !est.evaluado) evaluar(); });

  function compartir(b) {
    var url = location.origin + location.pathname + '#obra-' + b.dataset.id;
    var aviso = b.parentNode.querySelector('.ms-copiado');
    var listo = function (ok) { aviso.textContent = ok ? '✓ Enlace copiado' : url; };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(function () { listo(true); }, function () { listo(false); });
    else listo(false);
  }

  // «Medir en cuanto la lista aparezca»: sustituye al «activar al pasar el
  // cursor» del motor, que en un celular no existe.
  var enVista = false;
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      enVista = es[0].isIntersecting;
      if (enVista && est.auto && !est.evaluado && !marcos.rank) evaluar();
    }, { threshold: 0.25 }).observe($('msFilas'));
  } else enVista = true;
  $('msFilas').addEventListener('mouseenter', function () { if (est.auto && !est.evaluado && !marcos.rank) evaluar(); });

  // Arranque: filtro desde la dirección; cadencia y medición, del navegador.
  try {
    var q = new URLSearchParams(location.search);
    if (q.get('industria') && porSector[q.get('industria')]) est.sector = q.get('industria');
    if (q.get('mandato') && sexenio(q.get('mandato'))) est.mandato = q.get('mandato');
    if (q.get('orden') && ORDEN_F[q.get('orden')]) est.orden = q.get('orden');
  } catch (e) { /* sin parámetros */ }
  var per = lee('per');
  if (per && D.periodos[per]) est.per = per;
  if (lee('auto') === '0') { est.auto = false; $('msAuto').checked = false; }
  pinta(true);
  function desdeAncla() {
    var m = /^#obra-(.+)$/.exec(location.hash);
    if (m) irAObra(decodeURIComponent(m[1]), false);
  }
  desdeAncla();
  window.addEventListener('hashchange', desdeAncla);
  setInterval(tic, 1000);
})();
