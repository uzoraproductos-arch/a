/* Auditavisión · Herramientas › Modo Inspector › «Pregúntale al Auditor»
   (bot interno, 11-10-2026). La página la escribe herramientas/asistente.py
   y las fichas llegan en window.AUDITOR_BASE (asistente-base.js): aquí no se
   escribe ninguna cifra. Desde el 23-10-2026 (pedido del autor) contesta
   como un chat: asistente-charla.js entiende la pregunta y responde en
   corto; si no puede, este archivo busca la ficha que mejor responde y la
   dice en corto. La nota técnica sellada (folio + huella SHA-256, como el
   Estado de Cuenta) solo se arma si el lector toca «Generar ficha técnica».
   Si ninguna ficha responde, lo dice. Desde el 23-10-2026 (pedido del autor)
   esa nota es el «Dictamen pericial de Auditavisión» y vive en su propia
   página (herramienta-inspector-dictamen.html, que carga este mismo archivo):
   el enlace lleva solo la pregunta y la página vuelve a contestarla con la
   misma base, así que nadie puede fabricar un dictamen con cifras propias.
   Cada respuesta trae también «Saber más», que lleva a la página donde está
   la información. */
(function () {
  'use strict';

  var B = window.AUDITOR_BASE;
  var hilo = document.getElementById('paHilo');
  var form = document.getElementById('paForm');
  var campo = document.getElementById('paPregunta');
  var dic = document.getElementById('dicApp');
  if (!B || (!dic && (!hilo || !form || !campo))) return;
  /* Los municipios salen del padrón del INEGI (municipios-efipem.js, que la
     página carga): aquí se arma la ficha de cada uno. */
  var MU = window.AUDIT_MUNICIPIOS, NOMBRE = {};
  ((B.dat && B.dat.edo) || []).forEach(function (e) { NOMBRE[e.a] = e.n; });
  if (MU && MU.ent) Object.keys(MU.ent).forEach(function (ab) {
    MU.ent[ab].lista.forEach(function (r) {
      var ing = r.length > 2 ? r[2] / 1e6 : null, en = NOMBRE[ab] || ab;
      B.fichas.push({ t: 'municipio', tit: r[1] + ', ' + en,
        txt: 'Su ficha técnica: cuentas de 2024 ante el INEGI, FAIS y FORTAMUN ante Hacienda, quién gobernó y lo que observó la ASF.',
        ci: ing === null ? [] : [{ v: '$' + ing.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp', etq: 'ingresos 2024 (INEGI)', e: 'oficial' }],
        fu: ing === null ? [] : [{ tx: MU.fuente, url: MU.url }],
        ir: ['herramienta-inspector-entes.html#ente=municipal:' + MU.ent[ab].cve + r[0], 'su ficha técnica'], k: 'municipio alcaldia ayuntamiento ' + en });
    });
  });

  var LOGO = 'assets/auditor/img/logo-auditavision.svg';
  var TIPO = {
    glosario: ['📘', 'Término del glosario'], expediente: ['📂', 'Expediente de caso'], entidad: ['🗺️', 'Ficha de entidad'],
    fuente: ['📜', 'Fuente oficial'], pendiente: ['⏳', 'Dato pendiente'], pagina: ['🧭', 'Página de la plataforma'],
    cargo: ['💼', 'Remuneración de un cargo'], seccion: ['📍', 'Sección de la plataforma'],
    autoridad: ['🏛️', 'Autoridad fiscalizadora'], entrega: ['📡', 'Seguimiento de la fiscalización'],
    estado: ['🧾', 'Estado de cuenta'], ficha: ['🏢', 'Ficha técnica de un ente'], municipio: ['🏙️', 'Ficha técnica de un municipio'],
    cifra: ['📋', 'Cifra oficial del catálogo'], calculo: ['🧮', 'Respuesta con datos de la plataforma'],
    ley: ['⚖️', 'Artículo de ley'], faq: ['❓', 'Pregunta del Diccionario'],
    investigacion: ['🖼️', 'Investigación de Auditoría en imágenes']
  };
  var VACIAS = ('a al ante bajo con contra de del desde donde dónde cual cuál cuales cuáles como cómo el en entre es esta este esto ' +
    'ha hay la las le lo los me mi mas más muy no nos o para pero por porque que qué quien quién se sea ser si sí sin sobre son su sus ' +
    'te ti tu tú un una uno unos unas y ya yo eso esa cuanto cuánto cuanta cuánta cuantos cuántos significa quiere decir dime ' +
    'explica explicame puedo puedes sabes saber ver veo encuentro encontrar busco buscar dato datos informacion tienes hay falta faltan falto').split(' ');
  /* Sinónimos de uso común: la pregunta se dice como se habla, la ficha como la ley. */
  var SINON = { gana: 'sueldo remuneracion', ganan: 'sueldo remuneracion', sueldo: 'remuneracion salario', salario: 'remuneracion sueldo',
    presidente: 'presidencia ejecutivo', diputado: 'diputados camara', senador: 'senadores senado', robo: 'aclarar observaciones',
    huachicol: 'combustible contrabando', amlo: 'lopez obrador estado cuenta administracion', epn: 'pena nieto estado cuenta administracion',
    peña: 'pena nieto', fox: 'fox quesada', calderon: 'calderon hinojosa', zedillo: 'zedillo ponce', investigaciones: 'modo inspector', investigacion: 'modo inspector', fantasma: 'efos', factureras: 'efos', impuestos: 'tributarios recaudacion', deuda: 'deuda' };
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
    fichas(f.tit.replace(/^Cuánto gana: /, '')).forEach(function (w) { f._tit[w] = 1; });
    fichas(f.txt + ' ' + (f.k || '') + ' ' + (f.nota || '') + ' ' + (f.pend ? f.pend.pq + ' ' + f.pend.quien : '')).forEach(function (w) { f._cue[w] = 1; });
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
    var n = norm(q).replace(/[¿¡?!.,;:]/g, ' ');
    if (/^\s*(que|quien|cual)\s+(es|son|significa|era)\b|definicion|significa/.test(n)) return 'glosario';
    if (/\b(donde|en que pagina|como llego)\b/.test(n)) return 'pagina';
    if (/\b(falta|faltan|pendiente|no hay|por que no|no han publicado|no se sabe)\b/.test(n)) return 'pendiente';
    if (/\b(cuanto debe|deuda de|debe )\b/.test(n)) return 'entidad';
    if (/\b(gana|ganan|sueldo|salario|cobra|cobran|percibe)\b/.test(n)) return 'cargo';
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
      s *= 0.4 + 0.6 * tocadas / ws.length;
      /* Entre dos títulos que tocan lo mismo, gana el que no trae palabras de más («diputado» antes que «asesor de diputados»). */
      var nt = Object.keys(f._tit).length, enTit = ws.filter(function (w) { return f._tit[w]; }).length;
      if (nt) s *= 0.8 + 0.2 * enTit / nt;
      if (quiere && f.t === quiere) s *= 1.5;
      /* Un cargo de apoyo (asesor, secretario de estudio, proyectista) solo si se pregunta por él. */
      if (f.t === 'cargo' && /asesor|estudio y cuenta|proyectista|subsecretari/i.test(f.tit) && !/asesor|estudio|proyectista|subsecretari/.test(norm(q))) s *= 0.6;
      if (f.t === 'pagina' && quiere !== 'pagina') s *= 0.7;
      /* Si la ficha contiene todas las palabras de la pregunta, responde mejor que una que solo nombra una. */
      if (ws.length >= 2 && tocadas === ws.length) s *= 1.25;
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
  function sello(fol, rotulo) {
    var id = 'paArco' + Math.random().toString(36).slice(2, 7);
    return '<svg class="pa-sello-svg" viewBox="0 0 120 120" role="img" aria-label="Sello de Auditavisión">' +
      '<defs><path id="' + id + '" d="M60,60 m-44,0 a44,44 0 1,1 88,0 a44,44 0 1,1 -88,0"/></defs>' +
      '<circle cx="60" cy="60" r="57" fill="none" stroke="currentColor" stroke-width="2.5"/>' +
      '<circle cx="60" cy="60" r="35" fill="none" stroke="currentColor" stroke-width="1.2"/>' +
      '<text font-size="9.4" font-weight="800" letter-spacing="3.6" fill="currentColor"><textPath href="#' + id + '">AUDITAVISIÓN · ' + (rotulo || 'NOTA TÉCNICA') + ' ·</textPath></text>' +
      '<text x="60" y="58" text-anchor="middle" font-size="22" font-weight="900" fill="currentColor">✓</text>' +
      '<text x="60" y="74" text-anchor="middle" font-size="7.5" font-weight="800" fill="currentColor">' + esc(fol ? fol.split('-').slice(-1)[0] : '········') + '</text></svg>';
  }
  /* La huella es de la ficha, no de la pregunta: la misma ficha da el mismo folio. */
  function huella(f) {
    var obj = { t: f.t, tit: f.tit, txt: f.txt, ci: f.ci || [], pend: f.pend || null, fu: f.fu || [], ir: f.ir, v: selloSitio() };
    if (!window.crypto || !crypto.subtle || !window.TextEncoder) return Promise.resolve(null);
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(obj))).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return ('0' + x.toString(16)).slice(-2); }).join('');
    }).catch(function () { return null; });
  }
  function folioDe(hx, pre) {
    var d = new Date(), f = d.getFullYear() + ('0' + (d.getMonth() + 1)).slice(-2) + ('0' + d.getDate()).slice(-2);
    return (pre || 'NT') + '-' + f + '-' + hx.slice(0, 8).toUpperCase();
  }

  /* El dictamen pericial (pedido del autor, 23-10-2026): la respuesta del
     Auditor con su respaldo completo. Encabezado y pie llevan el sello. */
  var ROMANO = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX'];
  function dictamenHtml(q, r, f, antes) {
    var t = TIPO[f.t] || ['📄', 'Ficha'], k = 0;
    function cap(tit) { return '<h3 class="dic-cap"><span>' + ROMANO[k++] + '.</span> ' + tit + '</h3>'; }
    var ci = (f.ci || []).map(function (c) {
      return '<li><b>' + esc(c.v) + '</b><span>' + esc(c.etq) + '</span>' + chip(c) +
        (c.op ? '<small class="pa-op"><b>Operación:</b> ' + esc(c.op) + '</small>' : '') + '</li>';
    }).join('');
    var fu = (f.fu || []).map(function (x, i) {
      return '<li><b>F' + (i + 1) + '.</b> ' + (x.url ? '<a href="' + esc(x.url) + '" target="_blank" rel="noopener noreferrer">' + esc(x.tx) + ' ↗</a>' : esc(x.tx)) + '</li>';
    }).join('');
    /* La clasificación de la información: por qué cada cifra está como está. */
    var est = {};
    (f.ci || []).forEach(function (c) { est[c.e] = 1; });
    (r.html.match(/est-(oficial|derivado|pendiente)/g) || []).forEach(function (m) { est[m.slice(4)] = 1; });
    if (f.pend) est.pendiente = 1;
    var clas = [];
    if (est.oficial) clas.push('<li>' + chip({ e: 'oficial' }) + ' Tomada tal cual de su documento: la fuente va citada, con su enlace directo.</li>');
    if (est.derivado) clas.push('<li>' + chip({ e: 'derivado' }) + ' Calculada con cifras oficiales; la operación va junto a la cifra. Cuando solo hay aproximación, la plataforma da un rango: mínimo y máximo, cada uno de un documento oficial, y su punto medio.</li>');
    if (est.pendiente) clas.push('<li>' + chip({ e: 'pendiente', p: f.pend && f.pend.id }) + ' No hay documento oficial que lo sostenga: no se estima ni se rellena. Se dice por qué falta, a quién le toca publicarlo y dónde debería estar.</li>');
    var pend = f.pend ? '<div class="pa-pend">' +
      '<p><b>Por qué falta:</b> ' + esc(f.pend.pq) + '</p>' +
      '<p><b>A quién le toca:</b> ' + esc(f.pend.quien) + '</p>' +
      '<p><b>Dónde debería estar:</b> <a href="' + esc(f.pend.donde) + '" target="_blank" rel="noopener noreferrer">' + esc(f.pend.donde_tx) + ' ↗</a></p></div>' : '';
    var ir = r.ir || f.ir;
    var resp = r.html.replace(/<details class="pa-dedonde"/g, '<details class="pa-dedonde" open');
    return '<article class="pa-nota dic-doc">' +
      '<header class="dic-cab"><div class="dic-cab-marca"><img src="' + LOGO + '" alt="" width="62" height="48">' +
      '<div><b>Auditavisión</b><small>Plataforma ciudadana de fiscalización del gasto público</small></div></div>' +
      '<div class="dic-sello">' + sello(null, 'DICTAMEN') + '</div>' +
      '<div class="dic-cab-tx"><span class="pa-nota-tipo">Dictamen pericial · ' + esc(t[1]) + '</span>' +
      '<dl><div><dt>Folio</dt><dd class="pa-folio">calculando…</dd></div><div><dt>Expedido</dt><dd>' + esc(hoy()) + '</dd></div>' +
      '<div><dt>Versión de la plataforma</dt><dd>' + esc(selloSitio()) + '</dd></div></dl></div></header>' +
      '<h2 class="dic-tit"><span aria-hidden="true">' + t[0] + '</span> ' + esc(f.tit) + '</h2>' +
      cap('Planteamiento') + '<p class="pa-nota-q"><span>La pregunta</span> «' + esc(q) + '»</p>' +
      (antes.length ? '<p class="dic-chico">Se hizo en la plática después de: ' + antes.map(function (x) { return '«' + esc(x) + '»'; }).join(' → ') + '.</p>' : '') +
      cap('Respuesta del Auditor') + '<div class="dic-resp">' + resp + '</div>' +
      (f.txt && f.t !== 'calculo' ? '<p class="pa-nota-tx"><b>La ficha completa:</b> ' + esc(f.txt) + '</p>' : '') +
      (ci ? cap('Hallazgos: las cifras') + '<ul class="pa-cifras">' + ci + '</ul>' : '') +
      (pend ? cap('Lo que falta') + pend : '') +
      cap('Fundamento documental') + (fu ? '<ol class="dic-fuentes">' + fu + '</ol>' : '<p>Esta respuesta no cita cifras: lleva a una página de la plataforma, donde cada dato trae su fuente.</p>') +
      cap('Método') + '<ol class="dic-metodo">' +
      '<li><b>Localización.</b> El Auditor buscó la respuesta en la base de la plataforma (' + B.fichas.length.toLocaleString('es-MX') + ' fichas), que solo guarda datos ya publicados con su documento.</li>' +
      '<li><b>Verificación.</b> Cada cifra se toma del documento oficial que se cita, sin estimar ni redondear a ojo. Las cuentas se hacen con cifras oficiales y se dice la operación.</li>' +
      (clas.length ? '<li><b>Clasificación.</b> Cada dato lleva su estado:<ul class="dic-clas">' + clas.join('') + '</ul></li>' : '') +
      '<li><b>Integridad.</b> La huella digital (SHA-256) se calcula sobre la ficha y la versión de la plataforma: si cambia una letra, cambia la huella.</li></ol>' +
      cap('Alcance y limitaciones') + (f.nota ? '<p>' + esc(f.nota) + '</p>' : '') +
      '<p>Este dictamen lo arma el bot de la plataforma solo con datos ya publicados; no lo redacta una inteligencia artificial. ' +
      '<b>No es un documento oficial ni un peritaje con validez ante una autoridad:</b> es el respaldo documental de una respuesta, para que cualquiera revise de dónde sale cada dato. ' +
      'Vale para la versión de la plataforma que indica: si un documento oficial cambia, el dictamen se actualiza y su huella también.</p>' +
      (ir ? '<p class="pa-ir dic-no-imprime"><a href="' + esc(ir[0]) + '">📖 Saber más en «' + esc(ir[1]) + '» ➔</a></p>' : '') +
      '<footer class="pa-sello"><div class="pa-sello-img dic-sello">' + sello(null, 'DICTAMEN') + '</div><div>' +
      '<b>Dictamen pericial de Auditavisión</b>' +
      '<p>Folio <b class="pa-folio">calculando…</b> · Versión de la plataforma <b>' + esc(selloSitio()) + '</b></p>' +
      '<p class="pa-huella">Huella digital (SHA-256 de la ficha): <code>calculando…</code></p>' +
      '<p class="pa-leyenda">Para comprobarlo, abre el enlace de este dictamen: la plataforma lo vuelve a armar con sus datos y la huella debe coincidir. ' +
      'Enlace: <span class="dic-url">' + esc(location.href) + '</span></p>' +
      '</div></footer></article>';
  }

  function sinRespuesta(q, cerca) {
    return '<p>No tengo una ficha verificada que responda «' + esc(q) + '». Prefiero decírtelo antes que inventarte una respuesta.</p>' +
      (cerca.length ? '<div class="pa-mas"><span>Lo más cercano que tengo:</span>' + cerca.map(function (o) {
        return '<button type="button" class="pa-ej" data-pa-pregunta="' + esc(o.tit.split(' (')[0]) + '"><span aria-hidden="true">' + (TIPO[o.t] || ['📄'])[0] + '</span> ' + esc(o.tit.length > 70 ? o.tit.slice(0, 68) + '…' : o.tit) + '</button>';
      }).join('') + '</div>' : '') +
      '<p class="pa-chico">Prueba con otras palabras, busca en el <a href="indice.html">índice general</a> o en el <a href="glosario.html">glosario</a>, o revisa el <a href="pendientes.html">Registro de pendientes</a>: ahí está lo que aún no tiene documento oficial y dónde debería estar. ' +
      'Anoté tu pregunta en <a href="#paSinResp">Lo que aún no sé</a>: nos dice qué fichas agregar primero. ¿Crees que la plataforma debería tenerlo? <a href="comunidad-tema.html">Cuéntanos</a>.</p>';
  }

  /* «Lo que aún no sé» (11-10-2026): las preguntas sin respuesta, y las que
     el lector marca con «No era lo que buscaba», se anotan en su navegador
     para saber qué fichas agregar primero. No se envían solas: el lector las
     copia o, cuando la página traiga canal (CANAL_COMUNIDAD), las manda. */
  var CLAVE = 'auditavision.bot.sinRespuesta', MAX = 50;
  var app = document.getElementById('paApp');
  var canal = app ? app.getAttribute('data-canal') || '' : '';
  function leeLista() {
    try { var v = JSON.parse(localStorage.getItem(CLAVE) || '[]'); return Array.isArray(v) ? v : []; } catch (e) { return []; }
  }
  function guardaLista(l) {
    try { localStorage.setItem(CLAVE, JSON.stringify(l)); return true; } catch (e) { return false; }
  }
  function anota(q, motivo, tit) {
    var l = leeLista(), k = plano(q), hoy = new Date().toISOString().slice(0, 10), x = null;
    l.forEach(function (o) { if (plano(o.q) === k && o.m === motivo) x = o; });
    if (x) { x.n = (x.n || 1) + 1; x.f = hoy; if (tit) x.t = tit; }
    else l.unshift({ q: q, m: motivo, t: tit || '', f: hoy, n: 1 });
    guardaLista(l.slice(0, MAX));
    pintaLista();
  }
  function textoLista(l) {
    return 'Preguntas que el bot de Auditavisión no supo contestar\n' + l.map(function (o, i) {
      return (i + 1) + '. «' + o.q + '» · ' + (o.m === 'noera' ? 'la nota no respondía' + (o.t ? ' (dio: ' + o.t + ')' : '') : 'sin respuesta') +
        ' · ' + o.f + (o.n > 1 ? ' · ' + o.n + ' veces' : '');
    }).join('\n') + '\n' + location.href.split('?')[0];
  }
  function pintaLista() {
    var l = leeLista(), ol = document.getElementById('paSinRespLista');
    if (!ol) return;
    document.getElementById('paSinRespVacio').hidden = l.length > 0;
    ol.hidden = document.getElementById('paSinRespAcc').hidden = !l.length;
    ol.innerHTML = l.map(function (o) {
      return '<li><button type="button" class="pa-reintenta" data-pa-pregunta="' + esc(o.q) + '" data-pa-ya="1">' + esc(o.q) + '</button> <small>' +
        (o.m === 'noera' ? 'no era lo que buscabas' : 'sin respuesta') + (o.n > 1 ? ' · ' + o.n + ' veces' : '') + '</small></li>';
    }).join('');
    var env = document.getElementById('paSinRespEnviar');
    if (canal && l.length) {
      env.href = canal + (canal.indexOf('?') < 0 ? '?' : '&') + 'subject=' + encodeURIComponent('Preguntas sin respuesta del bot') + '&body=' + encodeURIComponent(textoLista(l));
      env.hidden = false;
    } else env.hidden = true;
  }

  function agrega(clase, html, quieto) {
    var li = document.createElement('li');
    li.className = 'pa-msg ' + clase;
    /* Sin avatar (24-10-2026): el logo ya está en la cabecera del chat. */
    li.innerHTML = '<div class="pa-burbuja">' + html + '</div>';
    hilo.appendChild(li);
    if (!quieto) li.scrollIntoView({ behavior: QUIETO ? 'auto' : 'smooth', block: 'nearest' });
    return li;
  }

  /* La conversación (asistente-charla.js) y las fichas que el lector puede
     pedir como nota técnica. */
  var charla = window.AuditorCharla ? window.AuditorCharla(B, { esc: esc, norm: norm }) : null;
  var QUIETO = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  /* «Generar dictamen» abre su página en otra pestaña, para no perder la
     plática: lleva la pregunta y las cuatro anteriores (las que siguen a otra,
     como «¿y Morelos?», necesitan su contexto). */
  var DICTAMEN = 'herramienta-inspector-dictamen.html', historial = [];
  function enlaceDictamen(q, previas) {
    return DICTAMEN + '?q=' + encodeURIComponent(q) + previas.map(function (c) { return '&c=' + encodeURIComponent(c); }).join('');
  }
  function chips(lista) {
    return lista && lista.length ? '<div class="pa-mas">' + lista.map(function (o) {
      var q = typeof o === 'string' ? o : o.tit.split(' (')[0], ico = typeof o === 'string' ? '' : '<span aria-hidden="true">' + (TIPO[o.t] || ['📄'])[0] + '</span> ';
      var tx = typeof o === 'string' ? o : (o.tit.length > 70 ? o.tit.slice(0, 68) + '…' : o.tit);
      return '<button type="button" class="pa-ej" data-pa-pregunta="' + esc(q) + '">' + ico + esc(tx) + '</button>';
    }).join('') + '</div>' : '';
  }
  function acciones(q, r, previas) {
    if (r.plat) return '';
    var ir = r.ir || (r.ficha && r.ficha.ir);
    return '<p class="pa-acc">' +
      (ir ? '<a class="pa-boton pa-ver" href="' + esc(ir[0]) + '">📖 Saber más <span class="pa-ver-donde">· ' + esc(ir[1]) + '</span> ➔</a>' : '') +
      (r.ficha ? '<a class="pa-boton pa-genera" href="' + esc(enlaceDictamen(q, previas || [])) + '" target="_blank" rel="noopener">🧾 Generar dictamen</a>' : '') +
      '<button type="button" class="pa-boton pa-noera" data-pa-q="' + esc(q) + '" data-pa-tit="' + esc(r.ficha ? r.ficha.tit : '') + '">🤔 No era lo que buscaba</button></p>';
  }

  /* La pregunta de una imagen de la portada (23-10-2026): si coincide con la
     de una investigación de Auditoría en imágenes, se contesta con ella. Se
     tolera que el lector la retoque: basta que comparta 3 de cada 4 palabras. */
  var INV = B.inv || [];
  INV.forEach(function (f) { f._qs = (f.qs || []).map(function (x) { return fichas(x); }); });
  function investigacion(q) {
    var ws = fichas(q), mejor = null, ms = 0;
    if (ws.length < 3 || !charla) return null;
    INV.forEach(function (f) {
      f._qs.forEach(function (t) {
        var comun = t.filter(function (w, i) { return t.indexOf(w) === i && ws.indexOf(w) >= 0; }).length;
        var s = comun / Math.max(t.length, ws.length);
        if (s > ms) { ms = s; mejor = f; }
      });
    });
    return ms >= 0.75 ? charla.deFicha(mejor) : null;
  }

  /* Los estados de cuenta y los mapas, relojes, tableros y simuladores
     (24-10-2026, pedido del autor): el catálogo lo escribe
     herramientas/asistente_recursos.py y comprueba que cada enlace exista.
     «Estado de cuenta de…» lleva directo al documento; «el mapa de…» abre el
     mapa; y al pie de cada respuesta van los que vienen al caso. */
  var REC = (B.rec && B.rec.rec) || [], EC = (B.rec && B.rec.ec) || [], ADM = (B.dat && B.dat.adm) || [];
  REC.forEach(function (x) { x._k = fichas(x.k + ' ' + x.n); });
  EC.forEach(function (x) { x._k = fichas(x.k); });
  function conSinon(t) {
    var ws = fichas(t);
    return ws.concat.apply(ws, ws.map(function (w) { return SINON[w] ? fichas(SINON[w]) : []; }));
  }
  function comunes(k, ws) { return k.filter(function (w, i) { return k.indexOf(w) === i && ws.indexOf(w) >= 0; }).length; }
  function entidadDe(t) {
    var p = plano(t), ab = null, largo = 0;
    Object.keys(NOMBRE).forEach(function (a) { var n = plano(NOMBRE[a]); if (p.indexOf(n) >= 0 && n.length > largo) { ab = a; largo = n.length; } });
    return ab;
  }
  function admDe(t) {
    var p = ' ' + conSinon(t).join(' ') + ' ', hay = null;
    ADM.forEach(function (a) { if (!hay && (p.indexOf(' ' + fichas(a.c).join(' ') + ' ') >= 0 || p.indexOf(' ' + fichas(a.n).join(' ') + ' ') >= 0)) hay = a; });
    return hay;
  }
  function sinParam(u) { return String(u).split('#')[0].split('?')[0]; }
  function ligaRec(x, ab) { return ab && x.ire ? x.ire.replace('%s', encodeURIComponent(ab)) : x.ir; }
  function recursosPara(q, r) {
    var tit = (r.ficha && r.ficha.tit) || r.tit || '', ir = r.ir || (r.ficha && r.ficha.ir);
    var t = (q + ' ' + tit).replace(/estados? de cuenta/gi, ' '), ws = conSinon(t), ab = entidadDe(t), base = ir ? sinParam(ir[0]) : '';
    var out = [];
    /* Con un estado de por medio, sus mapas y su circuito ya vienen al caso. */
    REC.forEach(function (x) {
      if (sinParam(x.ir) === base) return;
      var s = comunes(x._k, ws) + (ab && x.ire ? 2 : 0);
      if (s >= 2) out.push({ x: x, s: s });
    });
    out.sort(function (a, b) { return b.s - a.s; });
    return out.slice(0, 3).map(function (o) { return { x: o.x, ab: ab }; });
  }
  function recursosHtml(lista) {
    return lista && lista.length ? '<div class="pa-rec"><p class="pa-mas-t">Explóralo a fondo</p><div class="pa-rec-lista">' + lista.map(function (o) {
      return '<a class="pa-rec-a" href="' + esc(ligaRec(o.x, o.ab)) + '"><span class="pa-rec-ico" aria-hidden="true">' + o.x.ico + '</span>' +
        '<span><b>' + esc(o.x.v) + '</b><small>' + esc(o.x.n) + (o.ab && o.x.ire ? ' · ' + esc(NOMBRE[o.ab]) : '') + '</small></span></a>';
    }).join('') + '</div></div>' : '';
  }
  var TIPOS_REC = { mapa: 'mapa', mapas: 'mapa', reloj: 'reloj', relojes: 'reloj', contador: 'reloj', contadores: 'reloj', simulador: 'simulador', simuladores: 'simulador', tablero: 'tablero' };
  function pideRecurso(q) {
    var p = plano(q), tipo = null;
    Object.keys(TIPOS_REC).forEach(function (w) { if (p.indexOf(' ' + w + ' ') >= 0) tipo = TIPOS_REC[w]; });
    if (!tipo || / estados? de cuenta /.test(p)) return null;
    var ws = conSinon(q), ab = entidadDe(q), mejor = null, ms = 0, delTipo = REC.filter(function (x) { return x.tipo === tipo; });
    var tema = ws.filter(function (w) { return !TIPOS_REC[w] && !(ab && plano(NOMBRE[ab]).indexOf(' ' + w + ' ') >= 0); });
    delTipo.forEach(function (x) { var s = comunes(x._k, tema); if (s > ms) { ms = s; mejor = x; } });
    if (!mejor && tema.length > 1) return null;
    var lista = function (xs) { return '<ul class="pa-lista">' + xs.map(function (x) { return '<li><a href="' + esc(ligaRec(x, ab)) + '">' + x.ico + ' <b>' + esc(x.n) + '</b></a></li>'; }).join('') + '</ul>'; };
    if (!mejor) return { html: '<p>Estos son los que tengo:</p>' + lista(delTipo) + '<p>Cada uno se abre en su página. Dime el tema y te llevo al que es.</p>', ir: [delTipo[0].ir, delTipo[0].n], sug: [], rec: [] };
    var otros = delTipo.filter(function (x) { return x !== mejor; });
    return {
      html: '<p>' + mejor.ico + ' Aquí está: <b>' + esc(mejor.n) + '</b>' + (ab && mejor.ire ? ', ya con ' + esc(NOMBRE[ab]) + ' elegido' : '') + '. Toca <b>«Saber más»</b> y se abre en su página.</p>' +
        (otros.length ? '<p class="pa-chico">También tengo:</p>' + lista(otros) : ''),
      ir: [ligaRec(mejor, ab), mejor.n], sug: [], rec: []
    };
  }
  function estadoDeCuenta(q, r) {
    var p = plano(q);
    if (!EC.length || !/ estados? de cuenta /.test(p)) return null;
    /* Si la plática ya lo resolvió con datos (un estado, un municipio, un
       cargo) y lleva a su documento, se queda esa respuesta. */
    var resto = q.replace(/estados? de cuenta/gi, ' '), ws = fichas(resto), ab = entidadDe(resto), a = admDe(resto);
    var mejor = null, ms = 0, porId = {};
    EC.forEach(function (x) { porId[x.id] = x; var s = comunes(x._k, ws); if (s > ms) { ms = s; mejor = x; } });
    /* Un cargo («diputado local de Tamaulipas») manda sobre el estado. */
    var cargo = mejor && /^(dip-loc|dip-fed|senado|scjn|civico|ambiental)$/.test(mejor.id);
    var ir = r && !r.pasa && r.html ? (r.ir || (r.ficha && r.ficha.ir)) : null;
    if (!cargo && ir && /radar-estado-de-cuenta|herramienta-inspector-entes/.test(ir[0])) return null;
    if (a) mejor = porId.presidentes;
    else if (ab && (!mejor || mejor.id === 'estado' || mejor.id === 'presidentes')) mejor = porId.estado;
    if (!mejor && /(^| )(mi|mio)( |$)/.test(plano(resto))) mejor = porId.civico;
    var otras = function (x) { return EC.filter(function (y) { return y !== x; }).slice(0, 3).map(function (y) { return y.q; }); };
    if (!mejor) {
      return {
        html: '<p>Te puedo abrir <b>' + EC.length + ' estados de cuenta</b>, cada uno con sus cifras oficiales, su fuente y su folio:</p><ul class="pa-lista">' +
          EC.map(function (x) { return '<li><a href="' + esc(x.ir.indexOf('%s') >= 0 ? sinParam(x.ir) : x.ir) + '">' + x.ico + ' <b>' + esc(x.tit) + '</b></a></li>'; }).join('') +
          '</ul><p>Dime de quién lo quieres, por ejemplo «estado de cuenta de Jalisco» o «de un senador».</p>',
        ir: ['radar-estado-de-cuenta.html', 'el Estado de cuenta administrativo'], sug: [], rec: []
      };
    }
    var pide = mejor.ir.indexOf('%s') >= 0, liga = mejor.ir, quien = '';
    if (mejor.id === 'presidentes' && a) { liga = mejor.ir + '?adm=' + encodeURIComponent(a.id); quien = a.n; }
    else if (pide && ab) { liga = mejor.ir.replace('%s', mejor.id === 'dip-loc' ? (B.rec.dl || {})[ab] : ab); quien = NOMBRE[ab]; }
    else if (pide) liga = sinParam(mejor.ir);
    var elige = { presidentes: 'la administración', 'dip-loc': 'el congreso', estado: 'el estado', municipio: 'el municipio' }[mejor.id];
    return {
      html: '<p>' + mejor.ico + ' <b>' + esc(mejor.tit) + (quien ? ' · ' + esc(quien) : '') + '.</b> ' + esc(mejor.txt) + '</p>' +
        '<p>Toca <b>«Saber más»</b> y te llevo directo a él' + (!quien && elige ? '; ahí eliges ' + elige : '') + '.</p>',
      ir: [liga, quien ? 'el de ' + quien : 'su estado de cuenta'], sug: otras(mejor), tit: mejor.tit + (quien ? ' ' + quien : '')
    };
  }

  function respuesta(q) {
    var inv = investigacion(q);
    if (inv) return inv;
    var rc = pideRecurso(q);
    if (rc) return rc;
    var r = charla && charla.contesta(q);
    var ec = estadoDeCuenta(q, r);
    if (ec) return ec;
    /* Una afirmación sin dato con qué verificarla: se busca algo relacionado. */
    if (r && r.pasa) {
      var rel = buscar(r.claim);
      if (rel.length && rel[0].s >= 8 && charla) {
        var d = charla.deFicha(rel[0].f);
        d.html = '<p>No puedo comprobar eso directamente con un documento, pero esto es lo que la plataforma tiene relacionado:</p>' + d.html;
        d.sug = [];
        return d;
      }
      r.sug = [];
      return r;
    }
    if (r) return r;
    var res = buscar(q);
    if (!res.length || res[0].s < 3) return { sin: res.slice(0, 3).map(function (x) { return x.f; }) };
    var f = res[0].f, vistos = {}, otras = [];
    /* Un nombre a secas («Tren Maya») pide el caso, no lo que falta de él. */
    if (f.t === 'pendiente' && intencion(q) !== 'pendiente') {
      var alt = res.slice(1, 6).filter(function (x) { return x.f.t !== 'pendiente' && x.s >= res[0].s * 0.8; })[0];
      if (alt) f = alt.f;
    }
    /* «¿Qué es…?» lo contesta el glosario si tiene el término. */
    if (f.t !== 'glosario' && f.t !== 'faq' && intencion(q) === 'glosario') {
      var gl = res.slice(0, 8).filter(function (x) { return x.f.t === 'glosario' && x.s >= res[0].s * 0.4; })[0];
      if (gl) f = gl.f;
    }
    vistos[f.tit] = 1;
    res.slice(1).forEach(function (x) { if (otras.length < 3 && !vistos[x.f.tit] && x.s > res[0].s * 0.35) { vistos[x.f.tit] = 1; otras.push(x.f); } });
    r = charla ? charla.deFicha(f) : { html: '<p><b>' + esc(f.tit) + '.</b> ' + esc(f.txt) + '</p>', ficha: f, ir: f.ir };
    r.sug = otras;
    r.tambien = true;
    return r;
  }

  function responde(q, quieto, ya) {
    q = String(q || '').trim().slice(0, 600);
    if (!q) return;
    /* Ya empezó la plática: los ejemplos del arranque se guardan, como en cualquier chat. */
    var ejs = document.querySelector('.pa-ejs');
    if (ejs) ejs.hidden = true;
    agrega('pa-yo', '<p>' + esc(q) + '</p>', quieto);
    var previas = historial.slice(-4);
    historial.push(q);
    controles();
    var r = respuesta(q);
    var pinta = function (li) {
      if (r.sin) {
        li.querySelector('.pa-burbuja').innerHTML = sinRespuesta(q, r.sin);
        if (!ya) anota(q, 'sin');
        return;
      }
      if (r.anota && !ya) anota(q, 'sin');
      li.querySelector('.pa-burbuja').innerHTML = '<div class="pa-resp">' + r.html + '</div>' + acciones(q, r, previas) +
        (r.plat ? '' : recursosHtml(r.rec || recursosPara(q, r))) +
        (r.sug && r.sug.length ? '<p class="pa-mas-t">' + (r.tambien ? 'También te puede servir' : 'Sigue preguntando') + '</p>' + chips(r.sug) : '');
      guarda();
    };
    if (quieto || QUIETO) { pinta(agrega('pa-bot', '', quieto)); return; }
    var li = agrega('pa-bot pa-escribe', '<span class="pa-puntos" role="img" aria-label="Escribiendo"><i></i><i></i><i></i></span>');
    setTimeout(function () { li.classList.remove('pa-escribe'); pinta(li); li.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }, 420);
  }

  /* La página del dictamen: vuelve a contestar la pregunta del enlace (y las
     previas, para el contexto) con la misma base y arma el dictamen. */
  function armaDictamen() {
    var ps = new URLSearchParams(location.search), q = (ps.get('q') || '').trim().slice(0, 600);
    var antes = ps.getAll('c').map(function (x) { return x.trim().slice(0, 600); }).filter(Boolean).slice(-4);
    var doc = document.getElementById('dicDoc'), chat = 'herramienta-inspector-pregunta.html';
    if (!q) {
      doc.innerHTML = '<p>El dictamen respalda una respuesta del Auditor. <a href="' + chat + '">Hazle una pregunta</a> y, en su respuesta, toca <b>«🧾 Generar dictamen»</b>.</p>';
      return;
    }
    antes.forEach(function (x) { respuesta(x); });
    var r = respuesta(q), f = r && !r.sin ? r.ficha : null;
    if (!f) {
      doc.innerHTML = '<p>No pude armar el dictamen de «' + esc(q) + '»: esa respuesta no cita cifras ni fuentes que respaldar, o la plataforma ya no la contesta igual.</p>' +
        '<p><a href="' + chat + '?q=' + encodeURIComponent(q) + '">Pregúntasela de nuevo al Auditor ➔</a></p>';
      return;
    }
    doc.innerHTML = dictamenHtml(q, r, f, antes);
    document.title = 'Dictamen: ' + f.tit + ' · Auditavisión';
    huella(f).then(function (hx) {
      var fol = hx ? folioDe(hx, 'DP') : null;
      Array.prototype.forEach.call(doc.querySelectorAll('.pa-folio'), function (el) { el.textContent = fol || 'no disponible en este navegador'; });
      doc.querySelector('.pa-huella code').textContent = hx ? hx.replace(/(.{16})/g, '$1 ').trim() : 'no disponible en este navegador';
      Array.prototype.forEach.call(doc.querySelectorAll('.dic-sello'), function (el) { el.innerHTML = sello(fol, 'DICTAMEN'); });
    });
    var im = document.getElementById('dicImprime'), en = document.getElementById('dicEnlace');
    im.hidden = en.hidden = false;
    im.addEventListener('click', function () { window.print(); });
    en.addEventListener('click', function () {
      (navigator.clipboard ? navigator.clipboard.writeText(location.href) : Promise.reject()).then(function () {
        en.textContent = '✅ Enlace copiado';
      }, function () { en.textContent = 'Copia la dirección de tu navegador'; });
    });
  }
  if (dic) {
    window.AuditorBot = { buscar: buscar, charla: charla, respuesta: respuesta };
    armaDictamen();
    return;
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    responde(campo.value);
    campo.value = '';
  });
  document.getElementById('paApp').addEventListener('click', function (ev) {
    var b = ev.target.closest ? ev.target.closest('[data-pa-pregunta]') : null;
    if (b) { responde(b.getAttribute('data-pa-pregunta'), false, b.hasAttribute('data-pa-ya')); return; }
    var ne = ev.target.closest ? ev.target.closest('.pa-noera') : null;
    if (ne) {
      if (!ne.disabled) anota(ne.getAttribute('data-pa-q'), 'noera', ne.getAttribute('data-pa-tit'));
      ne.disabled = true;
      ne.textContent = '✅ Anotada en «Lo que aún no sé»';
      return;
    }
    if (ev.target.id === 'paSinRespCopiar') {
      var bc = ev.target;
      (navigator.clipboard ? navigator.clipboard.writeText(textoLista(leeLista())) : Promise.reject()).then(function () {
        bc.textContent = '✅ Copiada';
      }, function () { bc.textContent = 'No se pudo copiar'; });
      return;
    }
    if (ev.target.id === 'paSinRespBorrar') {
      if (window.confirm('¿Borrar las preguntas anotadas en este navegador?')) { guardaLista([]); pintaLista(); }
      return;
    }
  });
  /* El botón «Herramientas» despliega las cuatro herramientas (23-10-2026);
     se cierra con Escape o al tocar fuera. */
  (function () {
    var bt = document.getElementById('paHerrAbre'), menu = document.getElementById('paHerr');
    if (!bt || !menu) return;
    function pon(abierto, foco) {
      menu.hidden = !abierto;
      bt.setAttribute('aria-expanded', abierto ? 'true' : 'false');
      if (abierto) { var a = menu.querySelector('a'); if (a) a.focus({ preventScroll: true }); }
      else if (foco) bt.focus({ preventScroll: true });
    }
    bt.addEventListener('click', function () { pon(menu.hidden); });
    document.addEventListener('click', function (ev) {
      if (!menu.hidden && !menu.contains(ev.target) && !bt.contains(ev.target)) pon(false);
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !menu.hidden) pon(false, true); });
  })();
  /* «Cómo platicar conmigo» vive en un cajón lateral (23-10-2026). */
  var como = document.getElementById('paComo'), comoOv = document.getElementById('paComoOv');
  var comoBt = document.getElementById('paComoAbre'), comoDe = null;
  function abreComo(ancla) {
    comoDe = document.activeElement;
    comoOv.classList.add('abierto');
    void como.offsetWidth;
    como.classList.add('abierto');
    comoBt.setAttribute('aria-expanded', 'true');
    document.body.classList.add('glos-drawer-bloqueo');
    var cu = como.querySelector('.glos-drawer-cuerpo'), dest = ancla && document.getElementById(ancla);
    cu.scrollTop = dest ? dest.offsetTop - cu.offsetTop - 12 : 0;
    setTimeout(function () { document.getElementById('paComoX').focus({ preventScroll: true }); }, 30);
  }
  function cierraComo() {
    if (!como.classList.contains('abierto')) return;
    como.classList.remove('abierto');
    comoOv.classList.remove('abierto');
    comoBt.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('glos-drawer-bloqueo');
    if (comoDe && comoDe.focus) comoDe.focus({ preventScroll: true });
  }
  comoBt.addEventListener('click', function () { abreComo(); });
  comoOv.addEventListener('click', cierraComo);
  document.getElementById('paComoX').addEventListener('click', cierraComo);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') cierraComo(); });
  /* La liga «Lo que aún no sé» de las respuestas abre el cajón en esa sección. */
  hilo.addEventListener('click', function (ev) {
    var a = ev.target.closest ? ev.target.closest('a[href="#paSinResp"]') : null;
    if (a) { ev.preventDefault(); abreComo('paSinResp'); }
  });
  /* Las preguntas de ejemplo van por tandas (24-10-2026, pedido del autor:
     sin la barra de tiempo): se quedan quietas y cambian solo con
     «Otras preguntas». */
  (function () {
    var lista = document.getElementById('paEjsLista');
    if (!lista) return;
    var bts = Array.prototype.slice.call(lista.querySelectorAll('.pa-ej'));
    var otras = document.getElementById('paEjsOtras');
    var tanda = 0, n = 0;
    function porTanda() { return window.innerWidth < 640 ? 4 : 6; }
    function muestra(k) {
      var ini = (k * n) % bts.length;
      bts.forEach(function (b, i) {
        var pos = (i - ini + bts.length) % bts.length;
        b.hidden = pos >= n;
        b.style.setProperty('--pa-i', pos);
      });
    }
    function mide() { n = Math.min(porTanda(), bts.length); muestra(tanda); }
    if (bts.length <= porTanda()) return;
    otras.hidden = false;
    mide();
    otras.addEventListener('click', function () {
      tanda++;
      muestra(tanda);
      lista.classList.remove('pa-entra');
      void lista.offsetWidth;
      lista.classList.add('pa-entra');
    });
    var espera;
    window.addEventListener('resize', function () { clearTimeout(espera); espera = setTimeout(mide, 200); });
  })();

  /* La plática se guarda en la pestaña (sessionStorage, 24-10-2026): si el
     lector abre «Saber más» y vuelve, la encuentra como la dejó. «Regresar»
     quita la última pregunta con su respuesta y la deja escrita para
     corregirla; «Limpiar» empieza de cero. */
  var CLAVE = 'av-chat', btReg = document.getElementById('paRegresa'), btLim = document.getElementById('paLimpia');
  function guarda() {
    try {
      var lis = Array.prototype.slice.call(hilo.children, 1).filter(function (li) { return !li.classList.contains('pa-escribe'); });
      if (!historial.length) sessionStorage.removeItem(CLAVE);
      else sessionStorage.setItem(CLAVE, JSON.stringify({ h: historial, li: lis.map(function (li) { return li.outerHTML; }) }));
    } catch (e) { /* sin almacenamiento: la plática vive solo en esta vista */ }
  }
  function controles() {
    if (btReg) btReg.disabled = !historial.length;
    if (btLim) btLim.disabled = !historial.length;
  }
  function rehaceContexto() {
    if (!charla) return;
    charla.olvida();
    historial.forEach(function (x) { respuesta(x); });
  }
  function ejemplos(ver) { var e = document.getElementById('paEjs'); if (e) e.hidden = !ver; }
  function regresa() {
    var yo = hilo.querySelectorAll('.pa-yo');
    if (!yo.length || !historial.length) return;
    var ult = yo[yo.length - 1];
    while (ult.nextSibling) hilo.removeChild(ult.nextSibling);
    hilo.removeChild(ult);
    campo.value = historial.pop();
    rehaceContexto();
    if (!historial.length) ejemplos(true);
    guarda(); controles();
    campo.focus();
  }
  function limpia() {
    while (hilo.children.length > 1) hilo.removeChild(hilo.lastChild);
    historial = [];
    if (charla) charla.olvida();
    ejemplos(true);
    guarda(); controles();
    campo.value = '';
    campo.focus();
  }
  if (btReg) btReg.addEventListener('click', regresa);
  if (btLim) btLim.addEventListener('click', limpia);
  /* Un enlace de una respuesta que lleva a otra página de la plataforma deja
     la seña para que esa página ofrezca volver al Auditor (volver-auditor.js). */
  hilo.addEventListener('click', function (ev) {
    var a = ev.target.closest ? ev.target.closest('a[href]') : null;
    if (!a || a.target === '_blank' || a.origin !== location.origin || a.getAttribute('href').charAt(0) === '#') return;
    try { sessionStorage.setItem('av-volver', '1'); } catch (e) { /* nada */ }
  });
  (function () {
    var g = null;
    try { g = JSON.parse(sessionStorage.getItem(CLAVE) || 'null'); } catch (e) { g = null; }
    if (!g || !g.h || !g.h.length || !g.li) return;
    g.li.forEach(function (h) { hilo.insertAdjacentHTML('beforeend', h); });
    historial = g.h.slice();
    rehaceContexto();
    ejemplos(false);
    controles();
    var u = hilo.lastElementChild;
    if (u && hilo.scrollHeight > hilo.clientHeight) hilo.scrollTop = hilo.scrollHeight;
  })();

  /* Para revisar cómo puntúa una pregunta desde la consola. */
  window.AuditorBot = { buscar: buscar, charla: charla, respuesta: respuesta };
  pintaLista();
  if (canal) document.getElementById('paSinRespNota').innerHTML = 'La lista se guarda solo en tu navegador y no se envía sola: con «Enviarlas a Auditavisión» nos la haces llegar tú.';
  var ps = new URLSearchParams(location.search), pre = ps.get('q'), lista = ps.get('p');
  if (pre) responde(pre, true);
  /* ?p= (las imágenes de la portada, 23-10-2026): la pregunta queda escrita
     y el lector decide cuándo enviarla. */
  else if (lista) {
    campo.value = lista.trim().slice(0, 600);
    campo.classList.add('pa-lista-q');
    campo.focus({ preventScroll: true });
    form.scrollIntoView({ block: 'center' });
    campo.addEventListener('input', function () { campo.classList.remove('pa-lista-q'); }, { once: true });
  }
})();
