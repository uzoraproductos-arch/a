/* Auditavisión · Noticias, el periódico (28-10-2026). La página la escribe
   herramientas/noticias.py; las notas y columnas las pinta columnas.js.
   Aquí van la fecha del cabezal, la barra de secciones, la Agenda del erario
   (las fechas que fija la ley; los días que faltan son nuestra cuenta) y la
   Mesa de redacción: titulares que se traen de los buscadores de noticias
   al pedirlos, rotulados «sin verificar». De cada nota solo se muestran el
   titular, el medio, la fecha y la liga; nunca su texto. */
(function () {
  'use strict';

  var D;
  try { D = JSON.parse(document.getElementById('noticiasDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var hoy = new Date(); hoy.setHours(0, 0, 0, 0);

  /* ---------- El cabezal ---------- */
  var h = $('noticiasHoy');
  if (h) {
    var t = hoy.toLocaleDateString('es-MX', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
    h.textContent = t.charAt(0).toUpperCase() + t.slice(1);
  }

  /* ---------- La barra: marca la sección que estás leyendo ---------- */
  var ligas = [].slice.call(document.querySelectorAll('.nt-barra a'));
  if ('IntersectionObserver' in window && ligas.length) {
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (!en.isIntersecting) return;
        ligas.forEach(function (a) {
          if (a.getAttribute('href') === '#' + en.target.id) {
            a.setAttribute('aria-current', 'true');
            if (a.scrollIntoView && a.parentNode.scrollWidth > a.parentNode.clientWidth) {
              a.parentNode.scrollTo({ left: a.offsetLeft - 16, behavior: 'smooth' });
            }
          } else a.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-35% 0px -60% 0px' });
    [].forEach.call(document.querySelectorAll('.nt-sec'), function (s) { io.observe(s); });
  }

  /* La barra se pega justo debajo de la cabecera del sitio, que cambia de alto. */
  var barra = document.querySelector('.nt-barra'), cab = document.querySelector('.site-top-nav');
  function pegaBarra() {
    if (!barra) return;
    var fija = cab && getComputedStyle(cab).position === 'sticky';
    barra.style.top = (fija ? Math.round(cab.getBoundingClientRect().height) : 0) + 'px';
  }
  pegaBarra();
  window.addEventListener('scroll', pegaBarra, { passive: true });
  window.addEventListener('resize', pegaBarra);

  /* ---------- Agenda del erario ---------- */
  function ultimoHabil(anio, m) {
    var d = new Date(anio, m, 0);
    while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() - 1);
    return d;
  }
  function fechaDe(x, anio) { return x.ult ? ultimoHabil(anio, x.m) : new Date(anio, x.m - 1, x.d); }
  function proxima(x) {
    var f = fechaDe(x, hoy.getFullYear());
    return f < hoy ? fechaDe(x, hoy.getFullYear() + 1) : f;
  }
  function faltan(f) {
    var n = Math.round((f - hoy) / 86400000);
    return n === 0 ? 'Hoy' : n === 1 ? 'Mañana' : 'En ' + n.toLocaleString('es-MX') + ' días';
  }
  function tarjetaAgenda(x, f, conFalta) {
    return '<li class="nt-ag' + (conFalta && f - hoy < 15 * 86400000 ? ' nt-ag-pronto' : '') + '">' +
      '<div class="nt-ag-fecha"><b>' + f.getDate() + '</b><span>' + MESES[f.getMonth()].slice(0, 3) + '</span></div>' +
      '<div class="nt-ag-tx">' +
        (conFalta ? '<span class="nt-ag-falta">' + faltan(f) + '</span>' : '') +
        '<p class="nt-ag-que">' + esc(x.que) + '</p>' +
        '<p class="nt-ag-quien">' + esc(x.quien) + ' · ' + (x.ult ? 'el último día hábil de ' + MESES[x.m - 1] + ' · ' : '') +
          '<a href="' + esc(x.url) + '" target="_blank" rel="noopener noreferrer">' + esc(x.ley) + ' ↗</a></p>' +
        (x.cuenta ? '<p class="nt-ag-nota"><span class="est-chip est-derivado">derivado</span> La ley dice «' + esc(x.cuenta) + '»; la fecha es nuestra cuenta.</p>' : '') +
        (x.ult ? '<p class="nt-ag-nota"><span class="est-chip est-derivado">derivado</span> Contamos el último día entre semana; un día inhábil oficial puede adelantarlo.</p>' : '') +
        (x.nota ? '<p class="nt-ag-nota">' + esc(x.nota) + '</p>' : '') +
      '</div></li>';
  }
  var ag = $('noticiasAgenda');
  if (ag) {
    var prox = D.agenda.map(function (x) { return { x: x, f: proxima(x) }; }).sort(function (a, b) { return a.f - b.f; });
    var anio = D.agenda.slice().sort(function (a, b) { return (a.m - b.m) || ((a.ult ? 31 : a.d) - (b.ult ? 31 : b.d)); });
    ag.innerHTML = '<h3 class="nt-sub">⏳ Lo que viene</h3><ol class="nt-ag-lista">' +
      prox.slice(0, 6).map(function (p) { return tarjetaAgenda(p.x, p.f, true); }).join('') + '</ol>' +
      '<details class="nt-ag-anio"><summary>📅 El calendario completo del año (' + anio.length + ' fechas)</summary><ol class="nt-ag-lista nt-ag-todo">' +
      anio.map(function (x) { return tarjetaAgenda(x, fechaDe(x, hoy.getFullYear()), false); }).join('') + '</ol></details>';
  }

  /* ---------- Mesa de redacción ---------- */
  function conTiempo(p, ms) {
    return new Promise(function (ok, mal) {
      var t = setTimeout(function () { mal(new Error('tiempo')); }, ms);
      p.then(function (v) { clearTimeout(t); ok(v); }, function (e) { clearTimeout(t); mal(e); });
    });
  }
  function rssBing(q) { return 'https://www.bing.com/news/search?q=' + encodeURIComponent(q) + '&format=rss&setlang=es-MX&cc=MX'; }
  function rssGoogle(q) { return 'https://news.google.com/rss/search?q=' + encodeURIComponent(q) + '&hl=es-419&gl=MX&ceid=MX:es-419'; }
  function trae(u) {
    return conTiempo(fetch('https://api.allorigins.win/raw?url=' + encodeURIComponent(u)), 20000).then(function (r) {
      if (!r.ok) throw new Error('http ' + r.status);
      return r.text();
    });
  }
  /* Bing manda la liga envuelta (apiclick.aspx?…&url=…): se saca la del medio. */
  function ligaReal(u) {
    var m = /[?&]url=([^&]+)/.exec(u || '');
    if (m && /bing\.com/.test(u)) { try { return decodeURIComponent(m[1]); } catch (e) { /* sigue */ } }
    return u;
  }
  function texto(it, tag) {
    var el = it.getElementsByTagName(tag)[0];
    return el ? el.textContent.trim() : '';
  }
  function lee(xml) {
    var doc = new DOMParser().parseFromString(xml, 'text/xml');
    return [].slice.call(doc.getElementsByTagName('item')).map(function (it) {
      var tit = texto(it, 'title'), medio = texto(it, 'source') || texto(it, 'News:Source');
      if (!medio && / - [^-]+$/.test(tit)) { medio = tit.replace(/^.* - /, ''); tit = tit.replace(/ - [^-]+$/, ''); }
      else if (medio && tit.slice(-(medio.length + 3)) === ' - ' + medio) tit = tit.slice(0, -(medio.length + 3));
      var f = new Date(texto(it, 'pubDate'));
      return { titulo: tit, medio: medio, url: ligaReal(texto(it, 'link')), fecha: isNaN(f) ? '' : f.getDate() + ' de ' + MESES[f.getMonth()] + ' de ' + f.getFullYear(), t: isNaN(f) ? 0 : +f };
    }).filter(function (x) { return x.titulo && /^https?:\/\//.test(x.url); });
  }
  var RED = [
    ['📰', 'Noticias', function (q) { return 'https://news.google.com/search?q=' + encodeURIComponent(q) + '&hl=es-419&gl=MX&ceid=MX:es-419'; }],
    ['▶️', 'YouTube', function (q) { return 'https://www.youtube.com/results?search_query=' + encodeURIComponent(q); }],
    ['💬', 'X', function (q) { return 'https://x.com/search?q=' + encodeURIComponent(q) + '&f=live'; }],
    ['👥', 'Facebook', function (q) { return 'https://www.facebook.com/search/posts/?q=' + encodeURIComponent(q); }],
    ['📜', 'Diario Oficial', function (q) { return 'https://www.google.com/search?q=' + encodeURIComponent(q + ' site:dof.gob.mx'); }]
  ];
  function busquedas(q) {
    return '<p class="col-red-lista">' + RED.map(function (r) {
      return '<a href="' + esc(r[2](q)) + '" target="_blank" rel="noopener noreferrer"><span aria-hidden="true">' + r[0] + '</span> ' + r[1] + ' ↗</a>';
    }).join('') + '</p>';
  }
  function titular(x) {
    return '<li class="nt-tit-item"><span class="nt-sinv">Sin verificar</span>' +
      '<a class="nt-tit-a" href="' + esc(x.url) + '" target="_blank" rel="noopener noreferrer nofollow">' + esc(x.titulo) + ' ↗</a>' +
      '<small>' + esc(x.medio || 'Medio sin nombre') + (x.fecha ? ' · ' + esc(x.fecha) : '') + '</small>' +
      '<span class="nt-tit-acc"><button type="button" class="nt-btn nt-btn-chico" data-liga="' + esc(x.url) + '">⚖️ Verificar</button>' +
      '<a class="nt-btn nt-btn-chico nt-btn-sec" href="comunidad-tema.html" data-puerta="tema">💡 Proponer</a></span></li>';
  }
  var mesa = $('noticiasMesa'), tema = D.mesa[0];
  function pintaMesa() {
    mesa.innerHTML =
      '<div class="nt-mesa-temas" role="group" aria-label="Temas de la mesa">' + D.mesa.map(function (m) {
        return '<button type="button" class="nt-chip" data-tema="' + esc(m.id) + '" aria-pressed="' + (m === tema) + '">' + esc(m.t) + '</button>';
      }).join('') + '</div>' +
      '<div class="nt-mesa-cuerpo"><p class="nt-mesa-q">Buscamos: «' + esc(tema.q) + '»</p>' +
        '<p class="nt-acciones"><button type="button" class="nt-btn" id="noticiasTraer">📡 Traer los titulares de hoy</button></p>' +
        '<p class="nt-pie">Los pedimos a Bing Noticias y, si no responde, a Google Noticias, a través de un lector externo (allorigins), desde tu navegador. ' +
        'No guardamos lo que buscas. De cada nota te mostramos el titular, el medio y la liga: <b>no lo verificamos</b> hasta que pasa por el verificador.</p>' +
        '<div id="noticiasTitulares" aria-live="polite"></div></div>' +
      '<div id="noticiasBandeja"></div>';
    bandeja();
  }
  function traer() {
    var caja = $('noticiasTitulares'), btn = $('noticiasTraer');
    btn.disabled = true;
    caja.innerHTML = '<p class="nt-pie">Trayendo titulares…</p>';
    trae(rssBing(tema.q)).then(lee).then(function (l) { if (!l.length) throw new Error('vacio'); return l; })
      .catch(function () { return trae(rssGoogle(tema.q)).then(lee); })
      .then(function (l) {
        btn.disabled = false;
        var vistos = {};
        l = l.filter(function (x) { var k = x.titulo.toLowerCase(); if (vistos[k]) return false; vistos[k] = 1; return true; })
          .sort(function (a, b) { return b.t - a.t; }).slice(0, 10);
        if (!l.length) throw new Error('vacio');
        caja.innerHTML = '<ol class="nt-titulares">' + l.map(titular).join('') + '</ol>' +
          '<p class="nt-pie">Si una liga es de Google Noticias y el verificador no la abre, ábrela tú y pega la liga del medio.</p>';
      })
      .catch(function () {
        btn.disabled = false;
        caja.innerHTML = '<p class="nt-mesa-falla">No pudimos traer los titulares desde tu navegador: el lector externo no respondió. Búscalos tú, ya está armada la búsqueda:</p>' + busquedas(tema.q);
      });
  }
  /* Lo que junta la recolección automática (herramientas/recolectar_noticias.py). */
  function bandeja() {
    var el = $('noticiasBandeja');
    if (!el || !window.fetch) return;
    fetch(D.bandeja, { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (b) {
      var notas = b && b.notas ? b.notas.filter(function (x) { return x.tema === tema.id; }).slice(0, 10) : [];
      el.innerHTML = notas.length
        ? '<h3 class="nt-sub">🗃️ Lo que juntó nuestra recolección <small>(' + esc(b.actualizado) + ')</small></h3><ol class="nt-titulares">' + notas.map(titular).join('') + '</ol>'
        : '';
    }, function () { /* sin bandeja: solo la búsqueda en vivo */ });
  }
  function verificar(liga) {
    var u = $('inUrl'), f = $('inFormLiga'), t = $('inTabLiga');
    if (!u || !f) { location.href = 'herramienta-inspector-nota.html?liga=' + encodeURIComponent(liga); return; }
    if (t) t.click();
    u.value = liga;
    if (f.requestSubmit) f.requestSubmit(); else f.dispatchEvent(new Event('submit', { cancelable: true }));
    var v = $('verifica');
    if (v) v.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  if (mesa) {
    pintaMesa();
    mesa.addEventListener('click', function (e) {
      var c = e.target.closest('.nt-chip');
      if (c) {
        tema = D.mesa.filter(function (m) { return m.id === c.getAttribute('data-tema'); })[0] || tema;
        pintaMesa();
        return;
      }
      if (e.target.closest('#noticiasTraer')) { traer(); return; }
      var v = e.target.closest('[data-liga]');
      if (v) verificar(v.getAttribute('data-liga'));
    });
  }
})();
