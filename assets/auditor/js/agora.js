/* Ágora cívica (agora.html; decision del autor, 10-10-2026): la red de
   replica y dialogo en su propia pagina. Antes era la primera pestana de
   Participa y la pintaba participa.js.

   Todo vive en el navegador del lector hasta que la plataforma tenga
   servidor, y la pagina lo dice. Llaves de localStorage:
   - auditavision_foro_debates: los hilos (la misma del foro anterior, asi
     que los hilos que ya existian aparecen aqui);
   - auditavision_liked_debates: los hilos que apoyaste;
   - auditavision_agora_perfil: seudonimo, lugar, linea y color;
   - auditavision_agora_fuente: los hilos donde pediste fuente.

   No hay hilos sembrados: el foro anterior traia cuatro firmados por
   usuarios que no existian y se retiraron el 27-09-2026. Las «Preguntas
   para empezar» son de la plataforma y lo dicen.

   Temas, posturas y colores llegan en #agDatos (los escribe
   herramientas/apartados.py, agora()). */
(function () {
  'use strict';

  var raiz = document.getElementById('agora');
  var datosEl = document.getElementById('agDatos');
  if (!raiz || !datosEl) return;
  var DATOS = JSON.parse(datosEl.textContent);
  var TEMAS = {};
  DATOS.temas.forEach(function (t) { TEMAS[t[0]] = { ico: t[1], nombre: t[2], url: t[3] }; });
  /* Ronda 26D: sin emojis. Íconos de trazo (los mismos de auditor_bento.py) y un punto de color por postura. */
  var TRAZO = {
    oficial: '<path d="M3 21h18"/><path d="M5 21V10M9.5 21V10M14.5 21V10M19 21V10"/><path d="M2 10l10-6 10 6"/>',
    liga: '<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
    nota: '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    voz: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    doc: '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/>',
    repite: '<path d="M17 2l4 4-4 4"/><path d="M3 11V9a3 3 0 0 1 3-3h15"/><path d="M7 22l-4-4 4-4"/><path d="M21 13v2a3 3 0 0 1-3 3H3"/>',
    personas: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9"/><path d="M16 3.1a4 4 0 0 1 0 7.8"/>',
    lugar: '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    lupa: '<circle cx="11" cy="11" r="7"/><path d="M21 21l-5-5"/>',
    apoyo: '<path d="M7 10v11H3V10z"/><path d="M7 10l4-8a3 3 0 0 1 3 3v4h6a2 2 0 0 1 2 2.3l-1.4 8a2 2 0 0 1-2 1.7H7"/>',
    datos: '<path d="M3 3v18h18"/><path d="M8 17v-5M13 17V8M18 17v-9"/>',
    borrar: '<path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/>'
  };
  function ic(n, t) {
    return '<svg class="ag-ic" width="' + (t || 16) + '" height="' + (t || 16) + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
      + 'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' + TRAZO[n] + '</svg>';
  }
  function punto(id) { return '<i class="ag-dot ag-dot-' + esc(id || 'matiz') + '" aria-hidden="true"></i>'; }
  var POSTURAS = {};
  DATOS.posturas.forEach(function (p) { POSTURAS[p[0]] = { ico: p[1], nombre: p[2] }; });

  var K_HILOS = 'auditavision_foro_debates';
  var K_APOYOS = 'auditavision_liked_debates';
  var K_PERFIL = 'auditavision_agora_perfil';
  var K_FUENTE = 'auditavision_agora_fuente';
  var SEMBRADOS = ['deb-tren-maya-subsidios', 'deb-scjn-fideicomisos-art127',
    'deb-deuda-cetes-banxico', 'deb-garcia-luna-cnpp'];
  /* Dominios de las fuentes oficiales que pide la regla editorial. */
  var OFICIALES = /(^|\.)(gob\.mx|asf\.gob\.mx|dof\.gob\.mx|inegi\.org\.mx|banxico\.org\.mx|ine\.mx|scjn\.gob\.mx|diputados\.gob\.mx|senado\.gob\.mx|transparenciapresupuestaria\.gob\.mx|conasami\.gob\.mx)$/i;

  var orden = 'recientes';
  var filtroTema = '';
  var busqueda = '';
  var abiertos = {};

  // ------------------------------------------------------------ almacen
  function leer(k, def) {
    try {
      var v = JSON.parse(localStorage.getItem(k));
      return v === null || v === undefined ? def : v;
    } catch (e) { return def; }
  }
  function guardar(k, v) {
    try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; }
  }
  function hilos() {
    var h = leer(K_HILOS, []);
    if (!Array.isArray(h)) return [];
    var propios = h.filter(function (d) { return d && d.id && SEMBRADOS.indexOf(d.id) === -1; });
    if (propios.length !== h.length) guardar(K_HILOS, propios);
    return propios;
  }
  function lista(k) { var v = leer(k, []); return Array.isArray(v) ? v : []; }
  function perfil() {
    var p = leer(K_PERFIL, null);
    return p && typeof p === 'object' ? p : { nick: '', lugar: '', bio: '', color: DATOS.colores[0] };
  }

  // ------------------------------------------------------------ utilidades
  function esc(s) {
    return String(s === undefined || s === null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function arroba(n) { n = String(n || '').trim().replace(/\s+/g, ''); return n ? (n.charAt(0) === '@' ? n : '@' + n) : ''; }
  function iniciales(n) { return (String(n || '?').replace('@', '').slice(0, 2) || '?').toUpperCase(); }
  function avatar(nick, color, clase) {
    return '<span class="ag-avatar' + (clase ? ' ' + clase : '') + '" style="background:' + esc(color || '#334155') + '" aria-hidden="true">' + esc(iniciales(nick)) + '</span>';
  }
  /* Momento de un hilo: los nuevos guardan ts; los del foro anterior, su
     id deb-<milisegundos> o, si eran de ejemplo, dias_atras. */
  function momento(d) {
    if (d.ts) return d.ts;
    var m = /^(?:deb|rep)-(\d{12,})/.exec(d.id || '');
    if (m) return Number(m[1]);
    if (typeof d.dias_atras === 'number') return Date.now() - d.dias_atras * 864e5;
    return 0;
  }
  function hace(ts) {
    if (!ts) return 'hace tiempo';
    var s = Math.max(0, (Date.now() - ts) / 1000);
    if (s < 60) return 'hace un momento';
    if (s < 3600) return 'hace ' + Math.floor(s / 60) + ' min';
    if (s < 86400) return 'hace ' + Math.floor(s / 3600) + ' h';
    var d = Math.floor(s / 86400);
    if (d < 30) return 'hace ' + d + (d === 1 ? ' día' : ' días');
    return new Date(ts).toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' });
  }
  function fechaLarga(ts) { return ts ? new Date(ts).toLocaleString('es-MX') : ''; }
  function dominio(url) {
    try { return new URL(url).hostname.replace(/^www\./, ''); } catch (e) { return ''; }
  }
  /* #EstadosYMunicipios: cada palabra con mayuscula, sin espacios. */
  function etiqueta(n) {
    return '#' + String(n).split(/\s+/).map(function (w) { return w.charAt(0).toUpperCase() + w.slice(1); }).join('');
  }
  function esUrl(u) { return /^https?:\/\/\S+\.\S+/.test(u || ''); }
  function enlaces(texto) {
    return esc(texto).replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer nofollow">$1</a>')
      .replace(/\n/g, '<br>');
  }
  function fuenteHtml(f, url) {
    if (!f && !url) return '';
    var u = url || (esUrl(f) ? f : '');
    var dom = u ? dominio(u) : '';
    var chip = u ? (OFICIALES.test(dom)
      ? '<span class="ag-chip ag-chip-of" title="El enlace es de un dominio oficial; aun así, revisa que diga lo que se afirma.">' + ic('oficial', 14) + ' dominio oficial</span>'
      : '<span class="ag-chip" title="El enlace no es de un dominio oficial.">' + ic('liga', 14) + ' otra fuente</span>')
      : '<span class="ag-chip ag-chip-sin" title="Se citó sin enlace.">' + ic('nota', 14) + ' sin enlace</span>';
    return '<div class="ag-fuente">' + chip + ' ' + (u
      ? '<a href="' + esc(u) + '" target="_blank" rel="noopener noreferrer nofollow">' + esc(dom || u) + '</a>'
      : esc(f)) + '</div>';
  }

  // ------------------------------------------------------------ perfil
  var NICK_A = ['Auditora', 'Auditor', 'Fiscalizadora', 'Observador', 'Ciudadana', 'Analista', 'Vigilante', 'VozCívica', 'Criterio'];
  var NICK_B = ['MX', 'Norte', 'Sureste', 'Regio', 'Libre', 'Federal', 'Bajío', 'Pacífico', 'Digital', 'Cívico'];
  function nickAzar() {
    return '@' + NICK_A[Math.floor(Math.random() * NICK_A.length)] + NICK_B[Math.floor(Math.random() * NICK_B.length)] + '_' + (Math.floor(Math.random() * 90) + 10);
  }
  function asegurarPerfil() {
    var p = perfil();
    if (!p.nick) { p.nick = nickAzar(); guardar(K_PERFIL, p); }
    return p;
  }
  function esMio(nick, p) { return !!nick && !!p.nick && nick.toLowerCase() === p.nick.toLowerCase(); }

  function insignias(h, p) {
    var mios = h.filter(function (d) { return d.propio || esMio(d.autor_nick, p); });
    var reps = 0;
    h.forEach(function (d) { (d.replicas || []).forEach(function (r) { if (r.propio || esMio(r.autor_nick, p)) reps++; }); });
    var conFuente = mios.filter(function (d) { return esUrl(d.fuente_url || d.fuente); });
    var oficial = conFuente.some(function (d) { return OFICIALES.test(dominio(d.fuente_url || d.fuente)); });
    var apoyos = lista(K_APOYOS).length;
    return {
      stats: [['Hilos', mios.length], ['Réplicas', reps], ['Apoyos dados', apoyos], ['Con fuente', conFuente.length]],
      lista: [
        ['voz', 'Primera voz', 'Publicaste tu primer hilo.', mios.length >= 1],
        ['doc', 'Cita su fuente', 'Un hilo tuyo enlaza su documento.', conFuente.length >= 1],
        ['oficial', 'Fuente oficial', 'Enlazaste un documento de un dominio oficial.', oficial],
        ['repite', 'Replicador', 'Escribiste tres réplicas.', reps >= 3],
        ['personas', 'Escucha activa', 'Apoyaste tres argumentos.', apoyos >= 3]
      ]
    };
  }

  function pintarPerfil() {
    var p = perfil();
    var h = hilos();
    var nick = p.nick || 'Sin seudónimo';
    document.getElementById('agAvatar').outerHTML = avatar(p.nick || '?', p.color, 'ag-avatar-xl').replace('<span ', '<span id="agAvatar" ');
    document.getElementById('agAvatarMini').outerHTML = avatar(p.nick || '?', p.color).replace('<span ', '<span id="agAvatarMini" ');
    document.getElementById('agPerfilNick').textContent = nick;
    document.getElementById('agPerfilLugar').textContent = p.lugar ? p.lugar : (p.nick ? 'Miembro del Ágora' : 'Elige cómo firmar');
    var bio = document.getElementById('agPerfilBio');
    bio.textContent = p.bio || '';
    bio.hidden = !p.bio;
    var ins = insignias(h, p);
    document.getElementById('agStats').innerHTML = ins.stats.map(function (s) {
      return '<div><dt>' + s[0] + '</dt><dd>' + s[1] + '</dd></div>';
    }).join('');
    document.getElementById('agInsignias').innerHTML = ins.lista.map(function (i) {
      return '<span class="ag-insignia' + (i[3] ? ' ag-ganada' : '') + '" title="' + esc(i[1] + ': ' + i[2] + (i[3] ? '' : ' (todavía no)')) + '">'
        + ic(i[0], 20) + '<span class="sr-only">' + esc(i[1]) + (i[3] ? ', ganada' : ', pendiente') + '</span></span>';
    }).join('');
    var f = document.getElementById('agPerfilForm');
    f.agNick.value = p.nick || '';
    f.agLugar.value = p.lugar || '';
    f.agBio.value = p.bio || '';
    Array.prototype.forEach.call(f.querySelectorAll('input[name="agColor"]'), function (r) { r.checked = r.value === (p.color || DATOS.colores[0]); });
  }

  // ------------------------------------------------------------ muro
  function pintarTemas(h) {
    var cuenta = {};
    h.forEach(function (d) { cuenta[d.tema_id] = (cuenta[d.tema_id] || 0) + 1; });
    var chips = ['<button type="button" class="ag-chip-tema" data-tema="" aria-pressed="' + (!filtroTema) + '">Todos <b>' + h.length + '</b></button>'];
    DATOS.temas.forEach(function (t) {
      chips.push('<button type="button" class="ag-chip-tema" data-tema="' + t[0] + '" aria-pressed="' + (filtroTema === t[0]) + '">' + esc(etiqueta(t[2])) + (cuenta[t[0]] ? ' <b>' + cuenta[t[0]] + '</b>' : '') + '</button>');
    });
    document.getElementById('agTemas').innerHTML = chips.join('');
    var top = Object.keys(cuenta).filter(function (k) { return TEMAS[k]; }).sort(function (a, b) { return cuenta[b] - cuenta[a]; }).slice(0, 5);
    document.getElementById('agTendencias').innerHTML = top.length ? top.map(function (k) {
      return '<li><button type="button" class="ag-tend-btn" data-tema="' + k + '"><span>' + TEMAS[k].ico + ' ' + esc(etiqueta(TEMAS[k].nombre)) + '</span><small>' + cuenta[k] + (cuenta[k] === 1 ? ' hilo' : ' hilos') + '</small></button></li>';
    }).join('') : '<li class="ag-vacio-mini">Todavía no hay conversación. Las tendencias aparecen cuando publiques.</li>';
  }

  function tarjeta(d, p, apoyos, pedidas) {
    var tema = TEMAS[d.tema_id] || TEMAS.general;
    var post = POSTURAS[d.postura] || { ico: '', nombre: d.postura_nombre || 'Postura' };
    var reps = d.replicas || [];
    var mio = d.propio || esMio(d.autor_nick, p);
    var ap = apoyos.indexOf(d.id) > -1;
    var tieneFuente = !!(d.fuente || d.fuente_url);
    var pid = pedidas.indexOf(d.id) > -1;
    var ts = momento(d);
    var abierto = !!abiertos[d.id];
    return '<article class="ag-post ag-postura-' + esc(d.postura || 'matiz') + '" id="' + esc(d.id) + '">'
      + '<header class="ag-post-cab">' + avatar(d.autor_nick, d.autor_avatar_color)
      + '<div class="ag-post-quien"><b>' + esc(d.autor_nick || '@Ciudadano') + '</b>' + (mio ? ' <span class="ag-tu">tú</span>' : '')
      + '<span class="ag-post-meta"><time datetime="' + (ts ? new Date(ts).toISOString() : '') + '" title="' + esc(fechaLarga(ts)) + '">' + hace(ts) + '</time> · '
      + '<button type="button" class="ag-link" data-acc="tema" data-tema="' + esc(d.tema_id || 'general') + '">' + esc(etiqueta(tema.nombre)) + '</button></span></div>'
      + '<span class="ag-postura-chip">' + punto(d.postura) + esc(post.nombre) + '</span></header>'
      + '<h3 class="ag-post-tesis">' + esc(d.tesis) + '</h3>'
      + '<div class="ag-post-texto">' + enlaces(d.contenido) + '</div>'
      + fuenteHtml(d.fuente, d.fuente_url)
      + (!tieneFuente && (d.pide_fuente || 0) > 0 ? '<p class="ag-pide">' + ic('lupa', 14) + ' ' + d.pide_fuente + (d.pide_fuente === 1 ? ' persona pidió' : ' personas pidieron') + ' la fuente de este hilo.</p>' : '')
      + '<footer class="ag-acciones">'
      + '<button type="button" class="ag-acc' + (ap ? ' ag-on' : '') + '" data-acc="apoyar" aria-pressed="' + ap + '">' + ic('apoyo') + ' Apoyar <b>' + (d.apoyos || 0) + '</b></button>'
      + '<button type="button" class="ag-acc" data-acc="replicar" aria-expanded="' + abierto + '" aria-controls="hilo-' + esc(d.id) + '">' + ic('voz') + ' Replicar <b>' + reps.length + '</b></button>'
      + (tieneFuente ? '' : '<button type="button" class="ag-acc' + (pid ? ' ag-on' : '') + '" data-acc="fuente" aria-pressed="' + pid + '" title="Pide al autor el documento que sostiene su argumento">' + ic('lupa') + ' Pedir fuente</button>')
      + '<button type="button" class="ag-acc" data-acc="compartir">' + ic('liga') + ' Compartir</button>'
      + '<a class="ag-acc" href="' + esc(tema.url) + '">' + ic('datos') + ' Ver los datos</a>'
      + (mio ? '<button type="button" class="ag-acc ag-borrar" data-acc="borrar" title="Borrar este hilo de tu navegador" aria-label="Borrar este hilo de tu navegador">' + ic('borrar') + '</button>' : '')
      + '</footer>'
      + '<div class="ag-hilo" id="hilo-' + esc(d.id) + '"' + (abierto ? '' : ' hidden') + '>'
      + (reps.length ? reps.map(function (r) {
        return '<div class="ag-rep">' + avatar(r.autor_nick, r.autor_avatar_color, 'ag-avatar-sm')
          + '<div class="ag-rep-cuerpo"><div class="ag-rep-cab"><b>' + esc(r.autor_nick) + '</b>'
          + ((r.propio || esMio(r.autor_nick, p)) ? ' <span class="ag-tu">tú</span>' : '')
          + ' <span class="ag-rep-tipo">' + esc(r.tipo_replica || 'Réplica') + '</span> <time>' + hace(momento(r)) + '</time></div>'
          + '<p>' + enlaces(r.contenido) + '</p>' + fuenteHtml(r.fuente, r.fuente_url) + '</div></div>';
      }).join('') : '<p class="ag-vacio-mini">Aún no hay réplicas. Sé la primera persona en responder.</p>')
      + '<form class="ag-rep-form" data-hilo="' + esc(d.id) + '">'
      + avatar(p.nick || '?', p.color, 'ag-avatar-sm')
      + '<div class="ag-rep-campos"><label class="sr-only" for="rt-' + esc(d.id) + '">Tipo de réplica</label>'
      + '<select id="rt-' + esc(d.id) + '" name="tipo"><option>Contrapunto</option><option>Coincidencia</option><option>Dato adicional</option><option>Pregunta</option></select>'
      + '<label class="sr-only" for="rx-' + esc(d.id) + '">Tu réplica</label>'
      + '<textarea id="rx-' + esc(d.id) + '" name="texto" rows="2" maxlength="800" placeholder="Replica con respeto y, si das un dato, con su fuente." required></textarea>'
      + '<label class="sr-only" for="rf-' + esc(d.id) + '">Fuente (opcional)</label>'
      + '<input id="rf-' + esc(d.id) + '" name="fuente" type="url" maxlength="400" placeholder="Fuente (opcional): https://…">'
      + '<button type="submit" class="ag-btn ag-btn-of">Replicar</button></div></form>'
      + '</div></article>';
  }

  function pintarMuro() {
    var p = perfil();
    var h = hilos();
    pintarTemas(h);
    var apoyos = lista(K_APOYOS);
    var pedidas = lista(K_FUENTE);
    var l = h.slice();
    if (filtroTema) l = l.filter(function (d) { return (d.tema_id || 'general') === filtroTema; });
    if (busqueda) {
      var q = busqueda.toLowerCase();
      l = l.filter(function (d) {
        return [d.tesis, d.contenido, d.autor_nick, d.fuente].concat((d.replicas || []).map(function (r) { return r.contenido; }))
          .join(' ').toLowerCase().indexOf(q) > -1;
      });
    }
    if (orden === 'fuente') l = l.filter(function (d) { return d.fuente || d.fuente_url; });
    if (orden === 'mios') l = l.filter(function (d) { return d.propio || esMio(d.autor_nick, p); });
    l.sort(function (a, b) {
      if (orden === 'apoyados') return (b.apoyos || 0) - (a.apoyos || 0) || momento(b) - momento(a);
      if (orden === 'replicados') return ((b.replicas || []).length - (a.replicas || []).length) || momento(b) - momento(a);
      return momento(b) - momento(a);
    });
    /* «Abrir en el Auditor» (Ronda 26D): lleva al chat la búsqueda o el tema que tienes a la vista, para contrastarlo
       con los documentos de la base. El Auditor es el centro: no es una liga entre pestañas. */
    var aud = document.getElementById('agAuditor');
    if (aud) {
      var qa = busqueda || (filtroTema && TEMAS[filtroTema] ? TEMAS[filtroTema].nombre : '');
      aud.href = 'herramienta-inspector-pregunta.html' + (qa ? '?q=' + encodeURIComponent(qa) : '');
    }
    var feed = document.getElementById('agFeed');
    if (!l.length) {
      feed.innerHTML = h.length
        ? '<div class="ag-vacio"><div class="ag-vacio-ico">' + ic('lupa', 32) + '</div><h3>Nada con ese filtro</h3><p>Prueba con otro tema u orden, o borra la búsqueda.</p></div>'
        : '<div class="ag-vacio"><div class="ag-vacio-ico">' + ic('voz', 32) + '</div><h3>El muro está esperando la primera voz</h3>'
          + '<p>Escribe arriba qué quieres poner a debate, o elige una de las <b>preguntas para empezar</b>. '
          + 'Tu primer hilo te da la insignia «Primera voz».</p>'
          + '<button type="button" class="ag-btn ag-btn-of" data-acc="escribir">' + ic('nota') + ' Escribir mi primer hilo</button></div>';
      return;
    }
    feed.innerHTML = l.map(function (d) { return tarjeta(d, p, apoyos, pedidas); }).join('');
  }

  function pintar() { pintarPerfil(); pintarMuro(); }

  // ------------------------------------------------------------ acciones
  function estado(msg, mal) {
    var e = document.getElementById('agEstado');
    var turno = e.dataset.turno = String(Date.now());
    e.textContent = msg;
    e.className = 'ag-estado' + (mal ? ' ag-mal' : ' ag-bien');
    // Se compara el turno y no el texto: iconos.js cambia los emojis del aviso.
    if (!mal) setTimeout(function () { if (e.dataset.turno === turno) e.textContent = ''; }, 5000);
  }

  function destacar(id) {
    var el = document.getElementById(id);
    if (!el) return;
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    el.classList.add('ag-destacado');
    setTimeout(function () { el.classList.remove('ag-destacado'); }, 2600);
  }

  var comp = document.getElementById('agComposer');
  var tesis = document.getElementById('agTesis');
  var texto = document.getElementById('agTexto');
  var cuenta = document.getElementById('agCuenta');
  texto.addEventListener('input', function () { cuenta.textContent = texto.value.length + ' / 1200'; });
  tesis.addEventListener('focus', function () { comp.classList.add('ag-comp-abierto'); });

  function escribir(tema, frase) {
    comp.classList.add('ag-comp-abierto');
    if (tema) document.getElementById('agTema').value = tema;
    if (frase) {
      tesis.value = frase;
      var r = comp.querySelector('input[name="agPostura"][value="matiz"]');
      if (r) r.checked = true;
    }
    comp.scrollIntoView({ behavior: 'smooth', block: 'center' });
    (frase ? texto : tesis).focus({ preventScroll: true });
  }

  comp.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var t = tesis.value.trim();
    var c = texto.value.trim();
    var f = document.getElementById('agFuente').value.trim();
    [tesis, texto].forEach(function (el) { if (el.value.trim()) el.removeAttribute('aria-invalid'); else el.setAttribute('aria-invalid', 'true'); });
    if (!t || !c) { estado('Falta tu tesis o tu argumento.', true); (t ? texto : tesis).focus(); return; }
    if (f && !esUrl(f)) { estado('La fuente debe ser un enlace que empiece con https://', true); document.getElementById('agFuente').focus(); return; }
    var p = asegurarPerfil();
    var postura = (comp.querySelector('input[name="agPostura"]:checked') || {}).value || 'matiz';
    var tema = document.getElementById('agTema').value;
    var h = hilos();
    var nuevo = {
      id: 'deb-' + Date.now(), ts: Date.now(), propio: true,
      tema_id: tema, tema_nombre: (TEMAS[tema] || TEMAS.general).nombre,
      postura: postura, postura_nombre: POSTURAS[postura].nombre, postura_icono: POSTURAS[postura].ico,
      autor_nick: p.nick, autor_avatar_color: p.color,
      tesis: t, contenido: c, fuente: f || null, fuente_url: f || null,
      apoyos: 0, pide_fuente: 0, replicas: []
    };
    h.unshift(nuevo);
    if (!guardar(K_HILOS, h)) { estado('Este navegador no dejó guardar (¿modo privado o sin espacio?). Tu texto sigue aquí.', true); return; }
    comp.reset();
    cuenta.textContent = '0 / 1200';
    comp.classList.remove('ag-comp-abierto');
    if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
    estado('Publicado en tu navegador como ' + p.nick + '.');
    orden = 'recientes'; filtroTema = ''; busqueda = '';
    document.getElementById('agBuscar').value = '';
    marcarOrden();
    pintar();
    destacar(nuevo.id);
  });

  function marcarOrden() {
    Array.prototype.forEach.call(document.querySelectorAll('.ag-orden-btn'), function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-orden') === orden));
    });
  }

  raiz.addEventListener('click', function (ev) {
    var t = ev.target.closest('button, a');
    if (!t || !raiz.contains(t)) return;
    if (t.classList.contains('ag-orden-btn')) { orden = t.getAttribute('data-orden'); marcarOrden(); pintarMuro(); return; }
    if (t.classList.contains('ag-chip-tema') || t.classList.contains('ag-tend-btn')) {
      var tm = t.getAttribute('data-tema');
      filtroTema = (filtroTema === tm && t.classList.contains('ag-tend-btn')) ? '' : tm;
      pintarMuro();
      if (t.classList.contains('ag-tend-btn')) document.getElementById('agTemas').scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }
    if (t.classList.contains('ag-preg')) { escribir(t.getAttribute('data-tema'), t.getAttribute('data-texto')); return; }
    if (t.id === 'agNickAzar') { document.getElementById('agNick').value = nickAzar(); return; }
    if (t.id === 'agDescargar') { descargar(); return; }
    var acc = t.getAttribute('data-acc');
    if (!acc) return;
    if (acc === 'escribir') { escribir(); return; }
    if (acc === 'tema') { filtroTema = t.getAttribute('data-tema'); pintarMuro(); document.getElementById('agTemas').scrollIntoView({ behavior: 'smooth', block: 'center' }); return; }
    var art = t.closest('.ag-post');
    if (!art) return;
    var id = art.id;
    var h = hilos();
    var d = h.filter(function (x) { return x.id === id; })[0];
    if (!d) return;
    if (acc === 'apoyar') {
      var ap = lista(K_APOYOS);
      var i = ap.indexOf(id);
      if (i > -1) { ap.splice(i, 1); d.apoyos = Math.max(0, (d.apoyos || 1) - 1); } else { ap.push(id); d.apoyos = (d.apoyos || 0) + 1; }
      guardar(K_APOYOS, ap); guardar(K_HILOS, h); pintar();
    } else if (acc === 'replicar') {
      abiertos[id] = !abiertos[id];
      pintarMuro();
      if (abiertos[id]) { var tx = document.getElementById('rx-' + id); if (tx) tx.focus(); }
    } else if (acc === 'fuente') {
      var pf = lista(K_FUENTE);
      var j = pf.indexOf(id);
      if (j > -1) { pf.splice(j, 1); d.pide_fuente = Math.max(0, (d.pide_fuente || 1) - 1); } else { pf.push(id); d.pide_fuente = (d.pide_fuente || 0) + 1; }
      guardar(K_FUENTE, pf); guardar(K_HILOS, h); pintarMuro();
    } else if (acc === 'compartir') {
      var url = location.href.split('#')[0] + '#' + id;
      if (navigator.share) {
        navigator.share({ title: d.tesis + ' · Ágora cívica', url: url }).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function () { t.textContent = 'Enlace copiado'; }, function () { prompt('Copia este enlace:', url); });
      } else {
        prompt('Copia este enlace:', url);
      }
    } else if (acc === 'borrar') {
      if (!confirm('¿Borrar este hilo de tu navegador? No se puede deshacer.')) return;
      guardar(K_HILOS, h.filter(function (x) { return x.id !== id; }));
      pintar();
    }
  });

  raiz.addEventListener('submit', function (ev) {
    var f = ev.target;
    if (!f.classList.contains('ag-rep-form')) return;
    ev.preventDefault();
    var txt = f.texto.value.trim();
    var fu = f.fuente.value.trim();
    if (!txt) { f.texto.setAttribute('aria-invalid', 'true'); f.texto.focus(); return; }
    if (fu && !esUrl(fu)) { f.fuente.setAttribute('aria-invalid', 'true'); f.fuente.focus(); return; }
    var p = asegurarPerfil();
    var h = hilos();
    var d = h.filter(function (x) { return x.id === f.getAttribute('data-hilo'); })[0];
    if (!d) return;
    d.replicas = d.replicas || [];
    d.replicas.push({ id: 'rep-' + Date.now(), ts: Date.now(), propio: true, autor_nick: p.nick, autor_avatar_color: p.color,
      tipo_replica: f.tipo.value, contenido: txt, fuente: fu || null, fuente_url: fu || null });
    if (!guardar(K_HILOS, h)) return;
    abiertos[d.id] = true;
    pintar();
    var tx = document.getElementById('rx-' + d.id);
    if (tx) tx.focus();
  });

  document.getElementById('agBuscar').addEventListener('input', function (ev) { busqueda = ev.target.value.trim(); pintarMuro(); });

  document.getElementById('agPerfilForm').addEventListener('submit', function (ev) {
    ev.preventDefault();
    var f = ev.target;
    var anterior = perfil();
    var nick = arroba(f.agNick.value) || anterior.nick || nickAzar();
    var color = (f.querySelector('input[name="agColor"]:checked') || {}).value || DATOS.colores[0];
    var p = { nick: nick.slice(0, 31), lugar: f.agLugar.value.trim(), bio: f.agBio.value.trim(), color: color };
    /* Si cambia el seudonimo, tus hilos y replicas lo siguen. */
    if (anterior.nick && anterior.nick !== p.nick) {
      var h = hilos();
      h.forEach(function (d) {
        if (d.propio || esMio(d.autor_nick, anterior)) { d.autor_nick = p.nick; d.autor_avatar_color = p.color; d.propio = true; }
        (d.replicas || []).forEach(function (r) {
          if (r.propio || esMio(r.autor_nick, anterior)) { r.autor_nick = p.nick; r.autor_avatar_color = p.color; r.propio = true; }
        });
      });
      guardar(K_HILOS, h);
    } else {
      var h2 = hilos();
      h2.forEach(function (d) {
        if (d.propio || esMio(d.autor_nick, p)) d.autor_avatar_color = p.color;
        (d.replicas || []).forEach(function (r) { if (r.propio || esMio(r.autor_nick, p)) r.autor_avatar_color = p.color; });
      });
      guardar(K_HILOS, h2);
    }
    guardar(K_PERFIL, p);
    document.getElementById('agEditar').open = false;
    pintar();
  });

  function descargar() {
    var p = perfil();
    var mios = hilos().filter(function (d) { return d.propio || esMio(d.autor_nick, p); });
    var blob = new Blob([JSON.stringify({ plataforma: 'Auditavisión · Ágora cívica', exportado: new Date().toISOString(), perfil: p, hilos: mios }, null, 2)],
      { type: 'application/json;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'agora-mis-hilos.json';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  window.addEventListener('storage', function (e) { if (e.key && e.key.indexOf('auditavision_') === 0) pintar(); });

  pintar();
  if (location.hash.length > 1) {
    var h0 = (function () { try { return decodeURIComponent(location.hash.slice(1)); } catch (e) { return ''; } })();
    if (document.getElementById(h0) && document.getElementById(h0).classList.contains('ag-post')) setTimeout(function () { destacar(h0); }, 400);
  }
})();
