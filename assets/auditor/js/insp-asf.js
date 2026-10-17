/* Auditavisión · Modo Inspector › Qué encontró la ASF (12-10-2026).
   La página la escribe herramientas/insp_asf.py con las cifras ya puestas.
   Este archivo solo enriquece: cuenta regresiva a la próxima entrega,
   cambio de cifra en la serie, selector de estado con memoria, orden del
   ranking y descarga CSV desde el JSON embebido. Sin dependencias. */
(function () {
  'use strict';
  var nodo = document.getElementById('iaDatos');
  if (!nodo) return;
  var D;
  try { D = JSON.parse(nodo.textContent); } catch (e) { return; }
  var CLAVE = 'auditavision.inspasf.estado';

  function esc(t) {
    return String(t).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function fmt(v, d) {
    return Number(v).toLocaleString('en-US', { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 });
  }
  function mdp(p) { return '$' + fmt(p / 1e6, 1) + ' mdp'; }
  function chip(e) { return '<span class="est-chip est-' + e + '">' + e + '</span>'; }
  function barra(v, mx, sel) {
    var w = mx ? Math.max(0, Math.min(100, v / mx * 100)) : 0;
    return '<span class="ia-barra' + (sel ? ' ia-barra-sel' : '') + '" aria-hidden="true"><i style="--w:' + w.toFixed(2) + '%"></i></span>';
  }
  function fila(et, v, mx, txt, sel) {
    return '<li class="ia-fila"><span class="ia-fila-et">' + et + '</span>' + barra(v, mx, sel) + '<span class="ia-fila-v">' + txt + '</span></li>';
  }
  function fuente(clave, pagina) {
    var f = D.fuentes[clave];
    if (!f) return chip('pendiente') + ' fuente por documentar';
    var s = pagina == null ? '' : String(pagina);
    var pag = !s ? '' : (/^\d+$/.test(s) ? ', p. ' + s : (/^\d/.test(s) ? ', pp. ' : ', ') + s);
    return '<a class="ia-fuente" href="' + esc(f.url) + '" target="_blank" rel="noopener" title="' + esc(f.doc) + '">' + esc(f.corto) + esc(pag) + ' ↗</a>';
  }
  function dato(valor, rotulo, estado, pie) {
    return '<div class="ia-dato"><strong>' + valor + '</strong><span>' + rotulo + ' ' + chip(estado) + '</span>' + (pie ? '<small>' + pie + '</small>' : '') + '</div>';
  }
  function hoy() { var h = new Date(); h.setHours(0, 0, 0, 0); return h; }
  function dias(iso) {
    var p = iso.split('-').map(Number);
    return Math.round((new Date(p[0], p[1] - 1, p[2]) - hoy()) / 86400000);
  }

  /* 1. Cuenta regresiva y línea del tiempo, con la fecha de hoy */
  var lis = document.querySelectorAll('.ia-linea li[data-fecha]');
  var prox = null;
  Array.prototype.forEach.call(lis, function (li) {
    var d = dias(li.getAttribute('data-fecha'));
    li.classList.toggle('ia-hecho', d <= 0);
    li.classList.remove('ia-prox');
    if (d > 0 && !prox) { prox = li; li.classList.add('ia-prox'); }
  });
  var reloj = document.getElementById('iaReloj');
  if (reloj) {
    var n = dias(reloj.getAttribute('data-fecha'));
    var rn = document.getElementById('iaRelojN');
    if (n > 0 && rn) {
      rn.innerHTML = '<b>' + n + '</b><small>' + (n === 1 ? 'día' : 'días') + '</small>';
      rn.hidden = false;
      var est = document.getElementById('iaRelojEst');
      if (est) est.hidden = false;
    }
  }

  /* 2. La serie: cambiar la cifra que se compara */
  var met = document.getElementById('iaMetricas'), serie = document.getElementById('iaSerie');
  if (met && serie && D.serie.length) {
    met.hidden = false;
    met.addEventListener('click', function (ev) {
      var b = ev.target.closest('[data-ia-met]');
      if (!b) return;
      var k = b.getAttribute('data-ia-met');
      var m = D.met.filter(function (x) { return x.k === k; })[0];
      Array.prototype.forEach.call(met.querySelectorAll('[data-ia-met]'), function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      var mx = Math.max.apply(null, D.serie.map(function (r) { return r[k] || 0; }));
      serie.innerHTML = D.serie.map(function (r) {
        var v = r[k] || 0, e = k === 'observado' ? r.observadoEstado : 'oficial';
        return fila('CP ' + r.cp + ' <small>' + fuente(r.fuente, r.pagina) + '</small>', v, mx, (m.mdp ? mdp(v) : fmt(v)) + ' ' + chip(e));
      }).join('');
    });
  }

  /* 3. Tu estado */
  var sel = document.getElementById('iaEntSel'), panel = document.getElementById('iaEntidad'), rank = document.getElementById('iaRanking');
  var ordenBox = document.getElementById('iaOrden');
  if (!sel || !panel || !rank) return;
  var E = D.ent;
  var suma = E.reduce(function (a, e) { return a + e.t.porAclarar; }, 0);
  var sumaMu = E.reduce(function (a, e) { return a + e.t.muestra; }, 0);
  var prom = suma / E.length, nac100 = suma / sumaMu * 100;
  var porAcl = E.slice().sort(function (a, b) { return b.t.porAclarar - a.t.porAclarar; });
  var cada100 = function (e) { return e.t.muestra ? e.t.porAclarar / e.t.muestra * 100 : 0; };
  var ORD = {
    porAclarar: { tit: 'por monto por aclarar', v: function (e) { return e.t.porAclarar; }, txt: function (e) { return mdp(e.t.porAclarar); } },
    cada100: { tit: 'por lo que quedó por aclarar de cada $100 revisados', v: cada100, txt: function (e) { return '$' + fmt(cada100(e), 2) + ' de $100 ' + chip('derivado'); } },
    auditorias: { tit: 'por número de auditorías', v: function (e) { return e.t.auditorias; }, txt: function (e) { return fmt(e.t.auditorias); } },
    recuperaciones: { tit: 'por monto recuperado', v: function (e) { return e.t.recuperaciones; }, txt: function (e) { return mdp(e.t.recuperaciones); } }
  };
  var estado = { ent: E[0].e, orden: 'porAclarar' };
  try { var g = localStorage.getItem(CLAVE); if (g && E.some(function (e) { return e.e === g; })) estado.ent = g; } catch (e) { /* sin almacenamiento */ }

  function pintarPanel(e) {
    var t = e.t, pos = porAcl.indexOf(e) + 1, nom = esc(e.n);
    var c100 = cada100(e), mx = Math.max(t.porAclarar, prom);
    panel.innerHTML =
      '<p class="ia-est-tit"><b>' + nom + '</b> · lugar <b>' + pos + ' de 32</b> por monto por aclarar ' + chip('derivado') + '</p>' +
      '<div class="ia-datos">' +
        dato(fmt(t.auditorias), 'auditorías al dinero federal que recibió', 'derivado') +
        dato(fmt(t.acciones), 'acciones promovidas', 'derivado', fmt(t.PO) + ' pliegos de observaciones y ' + fmt(t.PRAS) + ' promociones de responsabilidad') +
        dato(mdp(t.porAclarar), 'por aclarar', 'derivado', 'Lugar ' + pos + ' de 32') +
        dato(mdp(t.recuperaciones), 'recuperados durante la auditoría', 'derivado') +
      '</div>' +
      '<div class="ia-compara"><h3 class="ia-sub">Tu estado contra el promedio</h3><ul class="ia-filas">' +
        fila(nom, t.porAclarar, mx, mdp(t.porAclarar), true) + fila('Promedio por estado', prom, mx, mdp(prom)) + '</ul>' +
        '<p class="ia-compara-tx">De cada <b>$100</b> que la ASF revisó en ' + nom + ', quedaron <b>$' + fmt(c100, 2) + '</b> por aclarar; en los 32 estados juntos, <b>$' + fmt(nac100, 2) +
          '</b>. Lo por aclarar es <b>' + fmt(t.porAclarar / prom, 2) + ' veces</b> el promedio por estado. ' + chip('derivado') + '</p>' +
        '<p class="ia-nota">' + chip('derivado') + ' Promedio por estado = suma de lo por aclarar en los 32 (' + mdp(suma) + ') ÷ 32. «De cada $100» = por aclarar ÷ monto revisado (muestra) × 100; el de los 32 usa las sumas de ambos. Veces = por aclarar del estado ÷ promedio por estado.</p>' +
      '</div>' +
      '<div class="ia-tabla-w"><table class="ia-tabla"><caption>Quién gastó el dinero federal en ' + nom + '</caption><thead><tr><th>Quién gastó</th><th>Auditorías</th><th>Acciones</th><th>Por aclarar</th><th>Recuperado</th></tr></thead><tbody>' +
        e.d.map(function (d) {
          return '<tr><th scope="row">' + esc(d.ente) + '</th><td>' + fmt(d.auditorias) + '</td><td>' + fmt(d.acciones) + '</td><td>' + mdp(d.porAclarar) + '</td><td>' + mdp(d.recuperaciones) + '</td></tr>';
        }).join('') + '</tbody></table></div>';
  }

  function pintarRanking() {
    var o = ORD[estado.orden];
    var lista = E.slice().sort(function (a, b) { return o.v(b) - o.v(a); });
    var mx = o.v(lista[0]);
    var tit = document.getElementById('iaRankTit');
    if (tit) tit.textContent = 'Los 32 estados, ' + o.tit;
    rank.innerHTML = lista.map(function (x, i) {
      var s = x.e === estado.ent;
      return '<li><button type="button" class="ia-rank' + (s ? ' ia-rank-sel' : '') + '" data-ia-ent="' + esc(x.e) + '"' + (s ? ' aria-current="true"' : '') + '>' +
        '<span class="ia-fila-et">' + (i + 1) + '. ' + esc(x.n) + '</span>' + barra(o.v(x), mx, s) + '<span class="ia-fila-v">' + o.txt(x) + '</span></button></li>';
    }).join('');
  }

  function elegir(nombre, guardar) {
    var e = E.filter(function (x) { return x.e === nombre; })[0];
    if (!e) return;
    estado.ent = e.e;
    sel.value = e.e;
    pintarPanel(e);
    pintarRanking();
    if (guardar) { try { localStorage.setItem(CLAVE, e.e); } catch (err) { /* sin almacenamiento */ } }
  }

  sel.addEventListener('change', function () { elegir(sel.value, true); });
  rank.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-ia-ent]');
    if (!b) return;
    elegir(b.getAttribute('data-ia-ent'), true);
    var cab = document.getElementById('ia-estado');
    var reducir = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (cab) sel.scrollIntoView({ behavior: reducir ? 'auto' : 'smooth', block: 'center' });
    sel.focus({ preventScroll: true });
  });
  if (ordenBox) {
    ordenBox.hidden = false;
    ordenBox.addEventListener('click', function (ev) {
      var b = ev.target.closest('[data-ia-orden]');
      if (!b) return;
      estado.orden = b.getAttribute('data-ia-orden');
      Array.prototype.forEach.call(ordenBox.querySelectorAll('[data-ia-orden]'), function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      pintarRanking();
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll('.ia-solojs'), function (x) { x.hidden = false; });
  if (estado.ent !== E[0].e) elegir(estado.ent, false);

  /* 4. Descarga CSV, generada aquí mismo */
  var csv = document.getElementById('iaCSV');
  if (csv) {
    csv.hidden = false;
    csv.addEventListener('click', function () {
      var celda = function (v) { var s = String(v); return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
      var lineas = ['entidad,ente,auditorias,acciones,recuperado,por_aclarar'];
      E.forEach(function (e) {
        e.d.forEach(function (d) { lineas.push([e.e, d.ente, d.auditorias, d.acciones, d.recuperaciones, d.porAclarar].map(celda).join(',')); });
      });
      lineas.push('');
      lineas.push(celda('Fuente: ' + D.csvFuente + '. Descargado de Auditavisión el ' + new Date().toLocaleDateString('es-MX') + '.'));
      var blob = new Blob(['﻿' + lineas.join('\r\n')], { type: 'text/csv;charset=utf-8' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'auditavision-asf-cp2024.csv';
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
    });
  }
})();
