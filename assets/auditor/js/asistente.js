/* Auditavisión · Herramientas › Modo Inspector › «Pregúntale al Auditor»
   (bot interno, 11-10-2026). La página la escribe herramientas/asistente.py
   y las fichas llegan en window.AUDITOR_BASE (asistente-base.js): aquí no se
   escribe ninguna cifra. Este archivo solo busca la ficha que mejor responde
   la pregunta y la entrega como nota técnica sellada (folio + huella
   SHA-256, como el Estado de Cuenta). Si ninguna ficha responde, lo dice. */
(function () {
  'use strict';

  var B = window.AUDITOR_BASE;
  var hilo = document.getElementById('paHilo');
  var form = document.getElementById('paForm');
  var campo = document.getElementById('paPregunta');
  if (!B || !hilo || !form || !campo) return;

  var LOGO = 'assets/auditor/img/logo-auditavision.svg';
  var TIPO = {
    glosario: ['📘', 'Término del glosario'], expediente: ['📂', 'Expediente de caso'], entidad: ['🗺️', 'Ficha de entidad'],
    fuente: ['📜', 'Fuente oficial'], pendiente: ['⏳', 'Dato pendiente'], pagina: ['🧭', 'Página de la plataforma']
  };
  var VACIAS = ('a al ante bajo con contra de del desde donde dónde cual cuál cuales cuáles como cómo el en entre es esta este esto ' +
    'ha hay la las le lo los me mi mas más muy no nos o para pero por porque que qué quien quién se sea ser si sí sin sobre son su sus ' +
    'te ti tu tú un una uno unos unas y ya yo eso esa cuanto cuánto cuanta cuánta cuantos cuántos significa quiere decir dime ' +
    'explica explicame puedo puedes sabes saber ver veo encuentro encontrar busco buscar dato datos informacion tienes hay falta faltan falto').split(' ');
  /* Sinónimos de uso común: la pregunta se dice como se habla, la ficha como la ley. */
  var SINON = { gana: 'sueldo remuneracion', ganan: 'sueldo remuneracion', sueldo: 'remuneracion salario', salario: 'remuneracion sueldo',
    presidente: 'presidencia ejecutivo', diputado: 'diputados camara', senador: 'senadores senado', robo: 'aclarar observaciones',
    huachicol: 'combustible contrabando', fantasma: 'efos', factureras: 'efos', impuestos: 'tributarios recaudacion', deuda: 'deuda' };
  var vacia = {};
  VACIAS.forEach(function (w) { vacia[norm(w)] = 1; });

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function norm(s) { return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  /* Raíz sencilla: quita el plural para que «pliegos» encuentre «pliego». */
  function raiz(w) { return w.length > 4 && /es$/.test(w) && !/[aeiou]es$/.test(w) ? w.slice(0, -2) : w.length > 3 && /s$/.test(w) ? w.slice(0, -1) : w; }
  function fichas(s) {
    return norm(s).replace(/[^a-z0-9ñ]+/g, ' ').split(' ').filter(function (w) { return w && !vacia[w] && (w.length > 1 || /\d/.test(w)); }).map(raiz);
  }
  function plano(s) { return ' ' + norm(s).replace(/[^a-z0-9ñ]+/g, ' ').trim() + ' '; }

  /* Índice: palabras del título y del cuerpo de cada ficha, y su rareza (idf). */
  var F = B.fichas, df = {};
  F.forEach(function (f) {
    f._tit = {}; f._cue = {};
    fichas(f.tit).forEach(function (w) { f._tit[w] = 1; });
    fichas(f.txt + ' ' + (f.k || '') + ' ' + (f.nota || '')).forEach(function (w) { f._cue[w] = 1; });
    f._plano = plano(f.tit.split(' (')[0]);
    var abr = /\(([^)]{2,12})\)\s*$/.exec(f.tit);
    f._abr = abr ? plano(abr[1]) : '';
    /* La sigla que de verdad nombra a la ficha: sus iniciales coinciden (ASF = Auditoría Superior de la Federación). */
    f._sigla = abr && plano(f.tit.split(' (')[0]).trim().split(' ').filter(function (w) { return w.length > 2 && !vacia[w]; }).map(function (w) { return w[0]; }).join('') === abr[1].toLowerCase().replace(/[^a-z]/g, '');
    var vistas = {};
    Object.keys(f._tit).concat(Object.keys(f._cue)).forEach(function (w) { if (!vistas[w]) { vistas[w] = 1; df[w] = (df[w] || 0) + 1; } });
  });
  function idf(w) { return Math.log((F.length + 1) / ((df[w] || 0) + 1)) + 0.5; }

  function intencion(q) {
    var n = norm(q);
    if (/^\s*(que|quien|cual)\s+(es|son|significa|era)\b|definicion|significa/.test(n)) return 'glosario';
    if (/\b(donde|en que pagina|como llego)\b/.test(n)) return 'pagina';
    if (/\b(falta|faltan|pendiente|no hay|por que no|no han publicado|no se sabe)\b/.test(n)) return 'pendiente';
    if (/\b(cuanto debe|deuda de|debe )\b/.test(n)) return 'entidad';
    if (/\b(ley|articulo|decreto|codigo|reglamento)\b/.test(n)) return 'fuente';
    return '';
  }

  function buscar(q) {
    var ws = fichas(q), pq = plano(q), quiere = intencion(q);
    ws = ws.concat.apply(ws, ws.map(function (w) { return SINON[w] ? fichas(SINON[w]) : []; })).filter(function (w, i, a) { return a.indexOf(w) === i; });
    if (!ws.length) return [];
    var res = [];
    F.forEach(function (f) {
      var s = 0, tocadas = 0;
      ws.forEach(function (w) {
        var p = idf(w);
        if (f._tit[w]) { s += 3 * p; tocadas++; }
        else if (f._cue[w]) { s += p; tocadas++; }
        else if (w.length >= 5) {
          for (var t in f._tit) { if (t.length >= 5 && (t.indexOf(w) === 0 || w.indexOf(t) === 0)) { s += 1.5 * p; tocadas++; break; } }
        }
      });
      if (!tocadas) return;
      /* El título completo dentro de la pregunta («ramo 33», «Jalisco») pesa mucho. */
      if (f._plano.trim().length > 2 && pq.indexOf(f._plano) >= 0) s += 12;
      else if (f._abr && pq.indexOf(f._abr) >= 0) s += f._sigla ? 14 : 8;
      s *= 0.6 + 0.4 * tocadas / ws.length;
      if (quiere && f.t === quiere) s *= 1.5;
      if (f.t === 'pagina' && quiere !== 'pagina') s *= 0.7;
      /* El título de una fuente es su cita completa (autor, fecha, editorial): pesa menos si no se pidió una ley. */
      if (f.t === 'fuente' && quiere !== 'fuente') s *= 0.5;
      res.push({ f: f, s: s });
    });
    res.sort(function (a, b) { return b.s - a.s; });
    return res;
  }

  function chip(c) {
    return '<span class="est-chip est-' + esc(c.e) + '"' + (c.p ? ' data-pend="' + esc(c.p) + '"' : '') + '>' + esc(c.e) + '</span>';
  }
  function selloSitio() { var b = document.querySelector('.apartado-pie-txt b'); return b ? b.textContent : ''; }
  function hoy() {
    var d = new Date();
    return d.toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' }) + ', ' + d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
  }
  function sello(fol) {
    var id = 'paArco' + Math.random().toString(36).slice(2, 7);
    return '<svg class="pa-sello-svg" viewBox="0 0 120 120" role="img" aria-label="Nota técnica de Auditavisión">' +
      '<defs><path id="' + id + '" d="M60,60 m-44,0 a44,44 0 1,1 88,0 a44,44 0 1,1 -88,0"/></defs>' +
      '<circle cx="60" cy="60" r="57" fill="none" stroke="currentColor" stroke-width="2.5"/>' +
      '<circle cx="60" cy="60" r="35" fill="none" stroke="currentColor" stroke-width="1.2"/>' +
      '<text font-size="9.4" font-weight="800" letter-spacing="3.6" fill="currentColor"><textPath href="#' + id + '">AUDITAVISIÓN · NOTA TÉCNICA ·</textPath></text>' +
      '<text x="60" y="58" text-anchor="middle" font-size="22" font-weight="900" fill="currentColor">✓</text>' +
      '<text x="60" y="74" text-anchor="middle" font-size="7.5" font-weight="800" fill="currentColor">' + esc(fol ? fol.split('-').slice(-1)[0] : '········') + '</text></svg>';
  }
  /* La huella es de la ficha, no de la pregunta: la misma ficha da el mismo folio. */
  function huella(f) {
    var obj = { t: f.t, tit: f.tit, txt: f.txt, ci: f.ci || [], fu: f.fu || [], ir: f.ir, v: selloSitio() };
    if (!window.crypto || !crypto.subtle || !window.TextEncoder) return Promise.resolve(null);
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(obj))).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return ('0' + x.toString(16)).slice(-2); }).join('');
    }).catch(function () { return null; });
  }
  function folioDe(hx) {
    var d = new Date(), f = d.getFullYear() + ('0' + (d.getMonth() + 1)).slice(-2) + ('0' + d.getDate()).slice(-2);
    return 'NT-' + f + '-' + hx.slice(0, 8).toUpperCase();
  }

  function nota(q, f, otras) {
    var t = TIPO[f.t] || ['📄', 'Ficha'];
    var ci = (f.ci || []).map(function (c) {
      return '<li><b>' + esc(c.v) + '</b><span>' + esc(c.etq) + '</span>' + chip(c) + '</li>';
    }).join('');
    var fu = (f.fu || []).map(function (x, i) {
      return '<li><b>F' + (i + 1) + '.</b> ' + (x.url ? '<a href="' + esc(x.url) + '" target="_blank" rel="noopener noreferrer">' + esc(x.tx) + ' ↗</a>' : esc(x.tx)) + '</li>';
    }).join('');
    var mas = otras.length ? '<div class="pa-mas"><span>También te puede servir:</span>' + otras.map(function (o) {
      return '<button type="button" class="pa-ej" data-pa-pregunta="' + esc(o.tit.split(' (')[0]) + '"><span aria-hidden="true">' + (TIPO[o.t] || ['📄'])[0] + '</span> ' + esc(o.tit.length > 70 ? o.tit.slice(0, 68) + '…' : o.tit) + '</button>';
    }).join('') + '</div>' : '';
    return '<article class="pa-nota">' +
      '<header class="pa-nota-cab"><img src="' + LOGO + '" alt="" width="52" height="40">' +
      '<div><span class="pa-nota-tipo">Nota técnica · ' + esc(t[1]) + '</span><b>Auditavisión</b></div>' +
      '<dl><div><dt>Folio</dt><dd class="pa-folio">calculando…</dd></div><div><dt>Expedida</dt><dd>' + esc(hoy()) + '</dd></div></dl></header>' +
      '<p class="pa-nota-q"><span>Tu pregunta</span> «' + esc(q) + '»</p>' +
      '<h4><span aria-hidden="true">' + t[0] + '</span> ' + esc(f.tit) + '</h4>' +
      (f.txt ? '<p class="pa-nota-tx">' + esc(f.txt) + '</p>' : '') +
      (ci ? '<ul class="pa-cifras">' + ci + '</ul>' : '') +
      (f.nota ? '<p class="pa-nota-al"><b>Alcance:</b> ' + esc(f.nota) + '</p>' : '') +
      (fu ? '<div class="pa-fuentes"><b>Fuentes</b><ol>' + fu + '</ol></div>' : '') +
      '<p class="pa-ir"><a href="' + esc(f.ir[0]) + '">Ver completo en ' + esc(f.ir[1]) + ' ➔</a></p>' +
      '<footer class="pa-sello"><div class="pa-sello-img">' + sello(null) + '</div><div>' +
      '<b>Nota técnica de Auditavisión</b>' +
      '<p>Folio <b class="pa-folio">calculando…</b> · Versión de la plataforma <b>' + esc(selloSitio()) + '</b></p>' +
      '<p class="pa-huella">Huella digital (SHA-256 de la ficha): <code>calculando…</code></p>' +
      '<p class="pa-leyenda">La arma el bot interno con una ficha ya publicada en la plataforma; no la redacta una inteligencia artificial. ' +
      '<b>No es un documento oficial.</b> El sello certifica que el contenido viene de la ficha citada y que no se ha alterado: si cambia una letra, la huella ya no coincide.</p>' +
      '<p class="pa-acciones"><button type="button" class="pa-copiar">📋 Copiar la nota</button></p>' +
      '</div></footer></article>' + mas;
  }

  function sinRespuesta(q, cerca) {
    return '<p>No tengo una ficha verificada que responda «' + esc(q) + '». Prefiero decírtelo antes que inventarte una respuesta.</p>' +
      (cerca.length ? '<div class="pa-mas"><span>Lo más cercano que tengo:</span>' + cerca.map(function (o) {
        return '<button type="button" class="pa-ej" data-pa-pregunta="' + esc(o.tit.split(' (')[0]) + '"><span aria-hidden="true">' + (TIPO[o.t] || ['📄'])[0] + '</span> ' + esc(o.tit.length > 70 ? o.tit.slice(0, 68) + '…' : o.tit) + '</button>';
      }).join('') + '</div>' : '') +
      '<p class="pa-chico">Prueba con otras palabras, busca en el <a href="indice.html">índice general</a> o en el <a href="glosario.html">glosario</a>. ' +
      '¿Crees que la plataforma debería tenerlo? <a href="comunidad.html">Cuéntanos</a>.</p>';
  }

  function agrega(clase, html, quieto) {
    var li = document.createElement('li');
    li.className = 'pa-msg ' + clase;
    li.innerHTML = (clase === 'pa-bot' ? '<img class="pa-ava" src="' + LOGO + '" alt="" width="36" height="28">' : '') + '<div class="pa-burbuja">' + html + '</div>';
    hilo.appendChild(li);
    if (!quieto) li.scrollIntoView({ behavior: 'smooth', block: 'start' });
    return li;
  }

  function responde(q, quieto) {
    q = String(q || '').trim().slice(0, 200);
    if (!q) return;
    agrega('pa-yo', '<p>' + esc(q) + '</p>', quieto);
    var r = buscar(q);
    if (!r.length || r[0].s < 3) {
      agrega('pa-bot', sinRespuesta(q, r.slice(0, 3).map(function (x) { return x.f; })), quieto);
      return;
    }
    var f = r[0].f, vistos = {}, otras = [];
    vistos[f.tit] = 1;
    r.slice(1).forEach(function (x) { if (otras.length < 3 && !vistos[x.f.tit] && x.s > r[0].s * 0.35) { vistos[x.f.tit] = 1; otras.push(x.f); } });
    var li = agrega('pa-bot pa-con-nota', nota(q, f, otras), quieto);
    huella(f).then(function (hx) {
      var fol = hx ? folioDe(hx) : null;
      Array.prototype.forEach.call(li.querySelectorAll('.pa-folio'), function (el) { el.textContent = fol || 'no disponible en este navegador'; });
      li.querySelector('.pa-huella code').textContent = hx ? hx.replace(/(.{16})/g, '$1 ').trim() : 'no disponible en este navegador';
      li.querySelector('.pa-sello-img').innerHTML = sello(fol);
    });
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    responde(campo.value);
    campo.value = '';
  });
  document.getElementById('paApp').addEventListener('click', function (ev) {
    var b = ev.target.closest ? ev.target.closest('[data-pa-pregunta]') : null;
    if (b) { responde(b.getAttribute('data-pa-pregunta')); return; }
    var c = ev.target.closest ? ev.target.closest('.pa-copiar') : null;
    if (c) {
      var art = c.closest('.pa-nota');
      var tx = art.innerText.replace(/📋 Copiar la nota|✅ Copiada/g, '').trim() + '\n' + location.href.split('?')[0];
      (navigator.clipboard ? navigator.clipboard.writeText(tx) : Promise.reject()).then(function () {
        c.textContent = '✅ Copiada';
      }, function () { c.textContent = 'Selecciónala y cópiala a mano'; });
    }
  });
  /* Para revisar cómo puntúa una pregunta desde la consola. */
  window.AuditorBot = { buscar: buscar };
  var pre = new URLSearchParams(location.search).get('q');
  if (pre) responde(pre, true);
})();
