/* Auditavisión · «Volver al Auditor» (24-10-2026, pedido del autor).
   Cuando el lector sale del chat por un enlace de una respuesta («Saber
   más», un expediente, una página de la plataforma), la página a la que
   llega le ofrece regresar: un botón flotante abajo a la izquierda. La
   plática lo espera tal como la dejó (asistente.js la guarda en la pestaña).
   La seña vive en sessionStorage y se borra al volver al chat o con la equis. Desde la Ronda 26C sale en toda página
   fuera del Auditor (ver pon()). */
(function () {
  'use strict';
  var CHAT = 'herramienta-inspector-pregunta.html', SENA = 'av-volver';
  var aqui = location.pathname.split('/').pop();
  /* Dentro del chat (24-10-2026, pedido del autor): el Auditor abre las seis
     aplicaciones del Modo Inspector en un marco de su respuesta. La página se
     muestra sola, sin cabecera, menú ni pie, y sus enlaces a otras páginas
     salen a la pestaña entera (con la seña para volver). El marco se llama
     «av-en-chat»: el nombre sobrevive a las navegaciones dentro de él. */
  var enChat = false;
  try { enChat = window.self !== window.top && window.top.location.origin === location.origin && window.name === 'av-en-chat'; } catch (e) { enChat = false; }
  if (enChat) {
    document.documentElement.classList.add('av-en-chat');
    document.addEventListener('click', function (ev) {
      var a = ev.target.closest ? ev.target.closest('a[href]') : null;
      if (!a || ev.defaultPrevented || a.target) return;
      if (a.origin === location.origin && a.pathname === location.pathname) return;
      a.target = '_top';
      try { sessionStorage.setItem(SENA, '1'); } catch (e) { /* nada */ }
    });
    return;
  }
  /* Todo pasa por el Auditor (decisión del autor, 19-11-2026: «entre pestañas no se
     vinculan: todo es a través del Auditor»). Las ligas de las páginas ya llegan
     mudadas al chat (servicios_fichas.por_auditor_html); esta es la red para las que
     arma el navegador (la ficha del Planisferio, por ejemplo): al tocar una liga a
     otra pestaña, se cambia por la del chat con la pregunta y ?abre=. La regla de
     cada pestaña es la de pestana_de() en servicios_fichas.py. */
  var EXC = { 'periodismo-en-riesgo.html': 'Noticiero', 'indice.html': 'Auditor', 'pendientes.html': 'Auditor', 'base-al-dia.html': 'Auditor', 'mis-respuestas.html': 'Auditor', 'administracion-codigos.html': 'Administración' };
  /* traslado */
  /* La Enciclopedia se volvió Planisferio (Ronda 7, 22-11-2026): la regla gemela de
     herramientas/traslado.py (la prueba con `traslado.py --prueba`). */
  var TR_PRIV = ["enciclopedia-auditavision.html", "sigue-el-dinero.html", "descarga-los-datos.html", "aprende.html"], TR_BIB = /^(diccionario|glosario|fuentes-oficiales|marco-legal|preguntas-frecuentes|expedientes-investigacion|expediente-[a-z0-9-]+)\.html$/, TR_NOT = /^garantias(-[a-z0-9-]+)?\.html$/, TR_AUD = ["herramienta-inspector-pregunta.html", "herramienta-inspector-dictamen.html"];
  var TR_REGLAS = [
    [/^(numeros-egreso-(adefas|costo-financiero)|numeros-la-deuda)\.html$/, 'deuda'],
    [/^(herramienta-megaobras(-[a-z0-9-]+)?|contratos-publicos)\.html$/, 'inversion'],
    [/^(herramienta-ambiente(-[a-z0-9-]+)?|datos-(medio-ambiente|ambiente-[a-z0-9-]+|justicia-ambiental(-[a-z0-9-]+)?)|aprende-recursos-naturales|contexto-dimensional-ambiental)\.html$/, 'ambiental'],
    [/^(datos-(poder-legislativo|legislativo-[a-z0-9-]+)|marco-legal-tres-niveles)\.html$/, 'legislativa'],
    [/^datos-(poder-judicial|judicial-[a-z0-9-]+)\.html$/, 'judicial'],
    [/^datos-salud(-[a-z0-9-]+)?\.html$/, 'salud'],
    [/^contexto-dimensional-social\.html$/, 'social'],
    [/^aprende-fraude-en-numeros\.html$/, 'penal'],
    [/^(herramienta-inspector(-[a-z0-9-]+)?|expedientes|informes-[a-z0-9-]+|datos-administracion-publica(-[a-z0-9-]+)?|aprende-auditoria|numeros-herramientas-del-auditor)\.html$/, 'administracion'],
    [/^(numeros-[a-z0-9-]+|datos-[a-z0-9-]+|radar-[a-z0-9-]+|contexto-dimensional-[a-z0-9-]+|herramienta-calculadora(-[a-z0-9-]+)?|simulador-presupuesto)\.html$/, 'financiera']
  ];
  function traslado(f) {
    if (TR_PRIV.indexOf(f) >= 0) return 'Administración';
    if (TR_BIB.test(f)) return 'Comunidad';
    if (TR_NOT.test(f)) return 'Noticiero';
    if (TR_AUD.indexOf(f) >= 0) return null;
    for (var i = 0; i < TR_REGLAS.length; i++) if (TR_REGLAS[i][0].test(f)) return 'Planisferio';
    return null;
  }
  /* fin traslado */
  function pestana(f) {
    if (EXC[f]) return EXC[f];
    if (f === CHAT || f === 'herramienta-inspector-dictamen.html') return 'Auditor';
    if (!f || f === 'index.html') return null;
    if (traslado(f)) return traslado(f);
    if (/^servicios?(-|\.html)/.test(f)) return 'Servicios';
    if (f.indexOf('planisferio') === 0) return 'Planisferio';
    if (f.indexOf('noticias') === 0) return 'Noticiero';
    return 'Comunidad';
  }
  var mia = pestana(aqui || 'index.html');
  if (mia && mia !== 'Auditor') {
    document.addEventListener('click', function (ev) {
      var a = ev.target.closest ? ev.target.closest('a[href]') : null;
      if (!a || a.origin !== location.origin || !a.closest('main') || a.closest('.pt-cajon, .apartado-migas, .site-top-nav')) return;
      var f = a.pathname.split('/').pop(), t = pestana(f);
      if (!/\.html$/.test(f) || !t || t === mia || t === 'Auditor') return;
      /* Una página propia del Planisferio que liga a su original se queda en ella
         (planisferio_espejo.py, 19-11-2026). */
      if (aqui === 'planisferio-ficha-' + f) { a.href = aqui + a.search + a.hash; return; }
      var b = a.querySelector('b'), q = ((b || a).textContent || '').replace(/\s+/g, ' ').replace(/[➔→›»]/g, '').trim();
      if (q.length < 4 || q.length > 140) q = f.replace(/\.html$/, '').replace(/-/g, ' ');
      a.href = CHAT + '?q=' + encodeURIComponent(q) + '&abre=' + encodeURIComponent(f + a.search + a.hash);
    }, true);
  }
  /* Ronda 26C (26-11-2026): el botón flotante sale en toda página fuera del Auditor, no solo al llegar desde una
     respuesta. Si la pestaña guarda una plática (av-chat), invita a volver a ella; si no, es un acceso discreto para
     preguntar. Se oculta con la equis por lo que dure la pestaña (av-volver-oculto). Nunca en la entrada, el dictamen,
     el panel de la administración ni dentro de un marco. */
  var SIN_VOLVER = ['canjea-tu-codigo.html', 'herramienta-inspector-dictamen.html', 'administracion-codigos.html'];
  var platica = false;
  try {
    if (aqui === CHAT || aqui === '' ) { sessionStorage.removeItem(SENA); return; }
    if (SIN_VOLVER.indexOf(aqui) >= 0 || window.self !== window.top) return;
    if (sessionStorage.getItem('av-volver-oculto')) return;
    platica = !!sessionStorage.getItem('av-chat') || !!sessionStorage.getItem(SENA);
  } catch (e) { return; }
  var SVG = '<svg viewBox="0 0 24 24" width="%s" height="%s" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">';
  function svg(n, d) { return SVG.replace(/%s/g, String(n)) + d + '</svg>'; }
  var ICO_VUELVE = svg(22, '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M12 9l-3 3 3 3"/><path d="M9 12h6"/>');
  var ICO_PREGUNTA = svg(22, '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M10 9.5a2 2 0 1 1 2.8 1.8c-.5.3-.8.7-.8 1.2"/><path d="M12 15.5h.01"/>');
  var ICO_X = svg(18, '<path d="M6 6l12 12"/><path d="M18 6L6 18"/>');
  function pon() {
    if (document.querySelector('.av-volver')) return;
    var caja = document.createElement('div');
    caja.className = 'av-volver' + (platica ? '' : ' av-volver-sutil');
    caja.innerHTML = '<a class="av-volver-ir" href="' + CHAT + '">' +
      '<span class="av-volver-ico">' + (platica ? ICO_VUELVE : ICO_PREGUNTA) + '</span>' +
      (platica ? '<span><b>Volver a tu plática en el Auditor</b><small>Sigue tal como la dejaste</small></span>'
               : '<span><b>Preguntar al Auditor</b></span>') + '</a>' +
      '<button type="button" class="av-volver-x" aria-label="Ocultar este botón">' + ICO_X + '</button>';
    caja.querySelector('.av-volver-ir').addEventListener('click', function (ev) {
      /* Si se llegó directo del chat, «atrás» lo recupera con todo y su lugar. */
      if (document.referrer && document.referrer.split('?')[0].split('#')[0].slice(-CHAT.length) === CHAT && history.length > 1) {
        ev.preventDefault();
        history.back();
      }
    });
    caja.querySelector('.av-volver-x').addEventListener('click', function () {
      try { sessionStorage.removeItem(SENA); sessionStorage.setItem('av-volver-oculto', '1'); } catch (e) { /* nada */ }
      caja.parentNode.removeChild(caja);
    });
    document.body.appendChild(caja);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', pon);
  else pon();
})();

/* La carcasa unificada (Ronda 26B, 26-11-2026): la barra lateral de todas las páginas (auditor_bento.lado). En el
   celular se pliega bajo «Menú»; fuera del Auditor, «Tu portafolio» lista los tres últimos de av-portafolio (en el
   Auditor lo hace auditor-bento.js). Nada sale del navegador. */
(function () {
  'use strict';
  function pon() {
    var lado = document.getElementById('avbLado');
    if (!lado) return;
    var btn = document.getElementById('avbLadoMenu');
    if (btn) btn.addEventListener('click', function () {
      var abre = !lado.classList.contains('avb-lado-abierto');
      lado.classList.toggle('avb-lado-abierto', abre);
      btn.setAttribute('aria-expanded', abre ? 'true' : 'false');
      btn.querySelector('span').textContent = abre ? 'Cerrar' : 'Menú';
    });
    var angosta = window.matchMedia && window.matchMedia('(max-width: 980px)').matches;
    var pd = document.getElementById('avbPort');
    if (pd && angosta) pd.open = false;
    if (document.getElementById('avb')) return;
    var lista = document.getElementById('avbPortLista'), vacio = document.getElementById('avbPortVacio');
    if (!lista || !vacio) return;
    function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
    var DOC = '<svg class="avb-i" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" ' +
      'stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/></svg>';
    function port() {
      var l = [];
      try { l = JSON.parse(localStorage.getItem('av-portafolio') || '[]'); } catch (e) { l = []; }
      if (!Array.isArray(l)) l = [];
      l = l.filter(function (x) { return x && x.q; }).slice(0, 3);
      lista.hidden = !l.length;
      vacio.hidden = !!l.length;
      lista.innerHTML = l.map(function (x) {
        var u = x.o === 'auditor' ? 'herramienta-inspector-pregunta.html?q=' + encodeURIComponent(x.q)
          : 'servicios-revisa.html?s=' + encodeURIComponent(x.s || '') + '&q=' + encodeURIComponent(x.q);
        return '<li><a href="' + esc(u) + '" title="' + esc((x.t || x.q) + (x.f ? ' · ' + x.f : '')) + '">' + DOC + '<span>' + esc(x.t || x.q) + '</span></a></li>';
      }).join('');
    }
    port();
    window.addEventListener('storage', function (ev) { if (ev.key === 'av-portafolio') port(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', pon);
  else pon();
})();
