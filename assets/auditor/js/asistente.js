/* Auditavisión · Herramientas › Modo Inspector › «Pregúntale al Auditor»
   (bot interno, 11-10-2026). La página la escribe herramientas/asistente.py
   y las fichas llegan en window.AUDITOR_BASE (asistente-base.js): aquí no se
   escribe ninguna cifra. Desde el 23-10-2026 (pedido del autor) contesta
   como un chat: asistente-charla.js entiende la pregunta y responde en
   corto; si no puede, este archivo busca la ficha que mejor responde y la
   dice en corto. La nota técnica sellada (folio + huella SHA-256, como el
   Estado de Cuenta) solo se arma si el lector toca «Generar ficha técnica».
   Si ninguna ficha responde, lo dice. Desde el 23-10-2026 (pedido del autor)
   esa nota es el «Dictamen cívico independiente de Auditavisión» y vive en su propia
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
    investigacion: ['🖼️', 'Investigación de Auditoría en imágenes'], app: ['🧩', 'Aplicación de la plataforma'],
    columna: ['📰', 'Columna de Noticias relevantes']
  };
  var VACIAS = ('a al ante bajo con contra de del desde donde dónde cual cuál cuales cuáles como cómo el en entre es esta este esto ' +
    'ha hay la las le lo los me mi mas más muy no nos o para pero por porque que qué quien quién se sea ser si sí sin sobre son su sus ' +
    'te ti tu tú un una uno unos unas y ya yo eso esa cuanto cuánto cuanta cuánta cuantos cuántos significa quiere decir dime ' +
    'explica explicame puedo puedes sabes saber ver veo encuentro encontrar busco buscar dato datos informacion tienes hay falta faltan falto').split(' ');
  /* Sinónimos de uso común: la pregunta se dice como se habla, la ficha como la ley. */
  var SINON = { gana: 'sueldo remuneracion', ganan: 'sueldo remuneracion', sueldo: 'remuneracion salario', salario: 'remuneracion sueldo',
    presidente: 'presidencia ejecutivo', diputado: 'diputados camara', senador: 'senadores senado', robo: 'aclarar observaciones',
    huachicol: 'combustible contrabando', amlo: 'lopez obrador estado cuenta administracion', epn: 'pena nieto estado cuenta administracion',
    peña: 'pena nieto', fox: 'fox quesada', calderon: 'calderon hinojosa', zedillo: 'zedillo ponce', investigaciones: 'modo inspector', investigacion: 'modo inspector', contratar: 'servicios encargo', fantasma: 'efos', factureras: 'efos', impuestos: 'tributarios recaudacion', deuda: 'deuda',
    /* 27-10-2026: lo que las preguntas de prueba no encontraban. */
    donar: 'donaciones donativo alcancia', dono: 'donaciones donativo', donativos: 'donaciones', apoyar: 'donaciones', transparentar: 'pendientes registro', dictamen: 'dictamen sellado independiente' };
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
    /* «Investigación» lleva al Modo Inspector, salvo que se quiera contratar una: eso es Servicios (24-10-2026). */
    var encargo = /servicio|contrat|encarg|a la medida|cotiz/.test(norm(q));
    ws = ws.concat.apply(ws, ws.map(function (w) { return SINON[w] && !(encargo && w === 'investigacion') ? fichas(SINON[w]) : []; })).filter(function (w, i, a) { return a.indexOf(w) === i; });
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

  /* El dictamen cívico independiente (antes «pericial»; pedido del autor, 23-10-2026): la respuesta del
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
    (f.cot || []).forEach(function (c) { if (c.r === 'pendiente') est.pendiente = 1; });
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
      '<div class="dic-cab-tx"><span class="pa-nota-tipo">Dictamen cívico independiente · ' + esc(t[1]) + '</span>' +
      '<dl><div><dt>Folio</dt><dd class="pa-folio">calculando…</dd></div><div><dt>Expedido</dt><dd>' + esc(hoy()) + '</dd></div>' +
      '<div><dt>Versión de la plataforma</dt><dd>' + esc(selloSitio()) + '</dd></div></dl></div></header>' +
      '<h2 class="dic-tit"><span aria-hidden="true">' + t[0] + '</span> ' + esc(f.tit) + '</h2>' +
      cap('Planteamiento') + '<p class="pa-nota-q"><span>La pregunta</span> «' + esc(q) + '»</p>' +
      (antes.length ? '<p class="dic-chico">Se hizo en la plática después de: ' + antes.map(function (x) { return '«' + esc(x) + '»'; }).join(' → ') + '.</p>' : '') +
      cap('Respuesta del Auditor') + '<div class="dic-resp">' + resp + '</div>' +
      (f.txt && f.t !== 'calculo' ? '<p class="pa-nota-tx"><b>La ficha completa:</b> ' + esc(f.txt) + '</p>' : '') +
      (ci ? cap('Hallazgos: las cifras') + '<ul class="pa-cifras">' + ci + '</ul>' : '') +
      (f.cot && f.cot.length && charla ? cap('Cotejo de lo que circula') +
        '<p class="dic-chico">Cada afirmación que circula se comparó con el documento oficial. «Consta» quiere decir que el documento la sostiene; «con matices», que la sostiene en parte; «sin documento oficial», que solo la dice la prensa o las redes, y no la afirmamos ni la negamos.</p>' +
        charla.cotejo(f, true) : '') +
      (f.app ? cap('La aplicación y tu resultado') + '<p>La cuenta la hace <b>«' + esc(f.app.n) + '»</b>' + (f.app.par ? ', con lo que escribiste en la plática' : '') + '. ' +
        'Para ver el resultado, o para que otra persona lo compruebe, abre la aplicación desde este enlace: <a href="' + esc(f.app.url) + '">' + esc(f.app.pag) + (f.app.par ? ' con tus datos' : '') + ' ➔</a>.</p>' +
        '<p class="dic-chico">La aplicación calcula con la base de la plataforma vigente, así que con el mismo enlace y la misma versión da el mismo resultado.</p>' : '') +
      (pend ? cap('Lo que falta') + pend : '') +
      cap('Fundamento documental') + (fu ? '<ol class="dic-fuentes">' + fu + '</ol>' + (f.app && f.app.mas ? '<p class="dic-chico">Y ' + f.app.mas + ' documentos más, citados en la página de la aplicación.</p>' : '') : '<p>Esta respuesta no cita cifras: lleva a una página de la plataforma, donde cada dato trae su fuente.</p>') +
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
      '<b>Dictamen cívico independiente de Auditavisión</b>' +
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
  /* Con base de datos (paso 2.8 del plan v2, 27-10-2026; FUNCIONES de
     apartados.py), cada pregunta nueva sin respuesta llega también a
     pregunta-bot: solo la pregunta, el motivo, la ficha que dio y la versión.
     Ni nombre ni correo. Si falla, se queda en el navegador como siempre. */
  var funcionBot = app ? app.getAttribute('data-funcion') || '' : '';
  function reporta(q, motivo, tit) {
    if (!funcionBot || !window.fetch) return;
    try {
      fetch(funcionBot, { method: 'POST', headers: { 'Content-Type': 'application/json' }, keepalive: true,
        body: JSON.stringify({ pregunta: String(q).slice(0, 600), motivo: motivo === 'noera' ? 'noera' : 'sin', ficha: tit || null, version: selloSitio() })
      }).catch(function () {});
    } catch (e) {}
  }
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
    else { l.unshift({ q: q, m: motivo, t: tit || '', f: hoy, n: 1 }); reporta(q, motivo, tit); }
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
  function conInv(q, r, lista) {
    var iv = r.sin ? null : invDe(q, r);
    if (!iv || lista.some(function (o) { return sinParam(o.x.ir) === iv.x.ir; })) return lista;
    return [iv].concat(lista).slice(0, 5);
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

  /* ================= El Modo Inspector, dentro del chat =================
     (24-10-2026, pedido del autor): sus seis aplicaciones se usan desde la
     plática. La lista negra del SAT la contesta el chat mismo; las demás se
     abren en un marco de la respuesta con lo que el lector ya trae (la liga,
     el folio, el ente, el caso, el tema) y siguen siendo la misma página:
     una sola fuente para las dos puertas. El catálogo lo escribe
     herramientas/asistente.py (_inspector). */
  var IN = (B.dat && B.dat.insp) || { apps: [], sat: {} }, APP = {};
  IN.apps.forEach(function (a) { APP[a.id] = a; a._p = plano(a.n); a._base = sinParam(a.url).replace(/\.html$/, ''); });
  /* La aplicación a la que lleva una liga de la plataforma (para «Úsala aquí»). */
  function appDeLiga(u) {
    var b = sinParam(u || '').replace(/\.html$/, ''), hit = null;
    if (b === 'expedientes') return APP.inspasf;
    IN.apps.concat(MO.apps, HA.apps).forEach(function (a) { if (!hit && (b === a._base || b.indexOf(a._base + '-') === 0)) hit = a; });
    return hit;
  }
  function appHtml(o) {
    var a = APP[o.id];
    if (!a) return '';
    return '<div class="pa-app" data-pa-app="' + esc(o.url) + '"' + (o.abre ? ' data-pa-abre="1"' : '') + '>' +
      '<div class="pa-app-cab"><span class="pa-app-ico" aria-hidden="true">' + a.ico + '</span><span><b>' + esc(a.n) + '</b>' +
      '<small>' + esc(a.grupo || 'Modo Inspector') + ' · aplicación ' + a.k + ' de ' + (a.tot || IN.apps.length) + '</small></span></div>' +
      '<p class="pa-app-acc"><button type="button" class="pa-boton pa-primario pa-app-usa">▶️ Úsala aquí, sin salir del chat</button></p></div>';
  }
  /* El marco: crece con la aplicación hasta tres cuartos de la pantalla (lo
     demás se recorre dentro); «Verla completa» lo deja crecer entero. */
  function montaApp(caja) {
    if (!caja || caja.querySelector('.pa-app-marco')) return;
    var a = appDeLiga(caja.getAttribute('data-pa-app')) || {};
    var m = document.createElement('div');
    m.className = 'pa-app-marco';
    m.innerHTML = '<iframe name="av-en-chat" title="' + esc(a.n || 'Aplicación del Modo Inspector') + ', dentro del chat" src="' + esc(caja.getAttribute('data-pa-app')) + '"></iframe>' +
      '<p class="pa-app-acc"><button type="button" class="pa-boton pa-app-crece" aria-pressed="false">⤢ Verla completa</button>' +
      '<button type="button" class="pa-boton pa-app-cierra">✕ Cerrar la aplicación</button></p>';
    caja.appendChild(m);
    caja.classList.add('pa-app-abierta');
    var fr = m.querySelector('iframe'), ro = null;
    function mide() {
      try {
        /* Si la plática se recorre en su propio recuadro (en computadora), el marco cabe en él. */
        var d = fr.contentDocument, alto = d ? d.documentElement.scrollHeight : 0, tope = Math.round(window.innerHeight * 0.75);
        if (hilo && getComputedStyle(hilo).overflowY !== 'visible') tope = Math.min(tope, hilo.clientHeight - 40);

        if (alto) fr.style.height = Math.max(280, caja.classList.contains('pa-app-completa') ? alto : Math.min(alto, tope)) + 'px';
      } catch (e) { /* nada */ }
    }
    fr.addEventListener('load', function () {
      caja.classList.add('pa-app-lista');
      mide();
      try {
        if (ro) ro.disconnect();
        if (window.ResizeObserver) { ro = new ResizeObserver(mide); ro.observe(fr.contentDocument.body); }
      } catch (e) { /* nada */ }
    });
    m._mide = mide;
    caja.querySelector('.pa-app-usa').hidden = true;
  }
  function cierraApp(caja) {
    var m = caja.querySelector('.pa-app-marco');
    if (m) m.parentNode.removeChild(m);
    caja.classList.remove('pa-app-abierta', 'pa-app-lista', 'pa-app-completa');
    caja.querySelector('.pa-app-usa').hidden = false;
    caja.querySelector('.pa-app-usa').focus({ preventScroll: true });
  }
  /* El dictamen de una aplicación usada en el chat (24-10-2026): la cuenta
     de tu caso la hace la aplicación al abrir su enlace; el dictamen respalda
     qué hace, con qué datos y de qué documentos salen (las fuentes las junta
     herramientas/asistente.py de su página). El chat no pone cifras. */
  function conApp(r) {
    if (!r) return r;
    if (r.espera) { r.espera = r.espera.then(conApp); return r; }
    var a = r.app && APP[r.app.id];
    if (a && !r.ficha) {
      var liga = r.app.url || a.url, par = liga.indexOf('?') >= 0;
      r.ficha = { t: 'app', tit: a.n + ' · ' + (a.grupo || 'Modo Inspector'), txt: a.desc || a.frase || '', fu: a.fu || [], ir: r.ir || [liga, a.n],
        app: { n: a.n, url: liga, par: par, mas: Math.max(0, (a.fun || 0) - (a.fu || []).length), pag: sinParam(liga) },
        nota: 'La aplicación hace la cuenta en tu navegador, con sus propios datos publicados' + (par ? ' y con lo que escribiste, que va en su enlace' : '') + ': el resultado se lee en ella. Este dictamen no repite ese resultado; respalda el método y los documentos.' };
    }
    return r;
  }
  function respApp(id, liga, html, extra) {
    var a = APP[id], r = { html: html, ir: [liga, a.n], app: { id: id, url: liga, abre: true }, sug: [], rec: [] };
    Object.keys(extra || {}).forEach(function (k) { r[k] = extra[k]; });
    return r;
  }

  /* --- La lista negra del SAT, en el chat (los 14 mil registros del 69-B se
     descargan la primera vez que se pregunta: 1.5 MB). --- */
  var SAT = { p: null }, ultimaSat = null;
  function cargaSat() {
    if (window.SAT_69B) return Promise.resolve(window.SAT_69B);
    if (SAT.p) return SAT.p;
    SAT.p = new Promise(function (ok, mal) {
      var s = document.querySelector('script[src*="asistente.js"]'), v = s && /\?v=[\w.-]+/.exec(s.getAttribute('src'));
      var sc = document.createElement('script');
      sc.src = 'assets/auditor/data/sat-69b.js' + (v ? v[0] : '');
      sc.onload = function () { if (window.SAT_69B) ok(window.SAT_69B); else { SAT.p = null; mal(); } };
      sc.onerror = function () { SAT.p = null; mal(); };
      document.head.appendChild(sc);
    });
    return SAT.p;
  }
  function satNorm(s) { return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toUpperCase().replace(/[^A-Z0-9& ]/g, ' ').replace(/\s+/g, ' ').trim(); }
  var RFC_RE = /\b[a-zñ&]{3,4}\d{6}[a-z0-9]{3}\b/gi;
  var SAT_PAL = /\b(lista negra|listas negras|69 ?-? ?b|efos|edos|empresas? fantasmas?|factureras?|facturas? (falsas|apocrifas)|operaciones (inexistentes|simuladas))\b/;
  var SAT_FUERA = ('esta estan en la el los las lista listas negra negras del de sat 69 b 69b efos edos empresa empresas fantasma fantasmas facturera factureras ' +
    'proveedor proveedores mi mis es son una un unos busca buscar buscame revisa revisar checa checar aparece aparecen salio sale si que con rfc y o ' +
    'persona contribuyente contribuyentes listado articulo factura facturas falsas apocrifas operaciones inexistentes simuladas me puedes dime quiero saber ver ' +
    'cual cuales quien quienes hay cuantas cuantos tiene tienen la le lo al por para su sus nombre esta? ').split(' ');
  function listaNegra(q) {
    var p = plano(q), rfcs = (q.match(RFC_RE) || []).map(function (x) { return x.toUpperCase(); }).filter(function (x, i, l) { return l.indexOf(x) === i; });
    if (!rfcs.length && !SAT_PAL.test(p)) return null;
    var nombre = '';
    if (!rfcs.length) {
      nombre = p.trim().split(' ').filter(function (w) { return w.length > 1 && SAT_FUERA.indexOf(w) < 0; }).join(' ');
      /* «¿Qué es la lista negra?» lo contesta el glosario; una pregunta sin nombre, la aplicación. */
      if (/^(que|q) (es|son|significa)\b|^que quiere decir/.test(p.trim()) && !nombre) return null;
      if (satNorm(nombre).length < 3) {
        return respApp('inspefos', APP.inspefos.url,
          '<p>🧾 Te busco en la <b>lista negra del SAT</b>: el listado del artículo 69-B del Código Fiscal, con quienes el SAT presume o declara que facturaron operaciones que no existieron.</p>' +
          '<p>Escríbeme el <b>RFC</b> o el <b>nombre</b> de la empresa o persona (por ejemplo, «¿está en la lista negra la empresa …?») y te contesto aquí mismo. Si traes varios RFC, pégalos juntos en un mensaje, o usa la aplicación aquí abajo.</p>');
      }
    }
    var termino = rfcs.length ? rfcs.join(' ') : nombre;
    var liga = APP.inspefos.url + '?q=' + encodeURIComponent(rfcs.length ? rfcs[0] : nombre);
    return { espera: cargaSat().then(function (S) { return respSat(S, rfcs, nombre, liga); }, function () {
      return respApp('inspefos', liga, '<p>No pude descargar ahora la lista oficial del SAT (1.5 MB). Revisa tu conexión y vuelve a preguntarme, o búscalo en la aplicación aquí abajo.</p>');
    }), tit: 'Lista negra del SAT: ' + termino };
  }
  function respSat(S, rfcs, nombre, liga) {
    var R = S.r, sit = IN.sat || {}, corte = S.meta.corte, hits = [], MAX = 5;
    if (rfcs.length) {
      rfcs.slice(0, 50).forEach(function (rf) {
        var h = R.filter(function (r) { return satNorm(r[0]).replace(/ /g, '') === rf; });
        hits.push({ rfc: rf, rs: h });
      });
    } else {
      var ps = satNorm(nombre).split(' ');
      hits.push({ rs: R.filter(function (r) { var n = satNorm(r[1]); return ps.every(function (w) { return n.indexOf(w) !== -1; }); }) });
    }
    function linea(r) {
      var s = sit[r[2]] || { t: r[2], i: '', corto: '', txt: '' };
      return '<li><span aria-hidden="true">' + s.i + '</span> <b>' + esc(r[1]) + '</b> (<code>' + esc(r[0]) + '</code>): <b>' + esc(s.t) + '</b>' +
        (s.corto ? ', ' + esc(s.corto.toLowerCase()) : '') + '. <span class="pa-chico">Oficio ' + esc(r[3]) + ', publicado en ' + (r[5] === 'DOF' ? 'el DOF' : 'la página del SAT') + ' el ' + esc(r[4]) + '.</span></li>';
    }
    var h = '', ci = [], todos = [];
    hits.forEach(function (x) { todos = todos.concat(x.rs); });
    if (rfcs.length === 1) {
      var r0 = hits[0].rs;
      if (!r0.length) h = '<p>◻️ <b>No aparece</b> el RFC <code>' + esc(rfcs[0]) + '</b></code> en la lista negra del SAT (listado del artículo 69-B, corte al ' + esc(corte) + ').</p>' +
        '<p>Eso no certifica a nadie: solo significa que el SAT no lo ha incluido al corte.' + (/^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$/.test(rfcs[0]) ? '' : ' Revisa que el RFC esté completo.') + '</p>';
      else {
        var s0 = sit[r0[0][2]] || {};
        h = '<p>' + (r0[0][2] === 'F' ? '⛔' : r0[0][2] === 'P' ? '⚠️' : '✅') + ' <b>Sí aparece</b> en la lista negra del SAT (corte al ' + esc(corte) + '):</p><ul class="pa-lista">' + r0.map(linea).join('') + '</ul>' +
          (s0.txt ? '<p>' + esc(s0.txt) + '</p>' : '');
      }
    } else if (rfcs.length) {
      var no = hits.filter(function (x) { return !x.rs.length; }).map(function (x) { return x.rfc; });
      h = '<p>Revisé <b>' + rfcs.length + ' RFC</b> en la lista negra del SAT (corte al ' + esc(corte) + '): <b>' + (rfcs.length - no.length) + '</b> aparece' + (rfcs.length - no.length === 1 ? '' : 'n') + ' y <b>' + no.length + '</b> no.</p>' +
        (todos.length ? '<ul class="pa-lista">' + todos.slice(0, 12).map(linea).join('') + '</ul>' : '') +
        (no.length ? '<p class="pa-chico">No aparecen: <code>' + no.map(esc).join('</code>, <code>') + '</code>. No aparecer no certifica a nadie.</p>' : '') +
        (rfcs.length > 50 ? '<p class="pa-chico">Revisé solo los primeros 50; para más, usa la aplicación aquí abajo (acepta hasta 500).</p>' : '');
      liga = APP.inspefos.url;
    } else if (!todos.length) {
      h = '<p>◻️ <b>Nadie con «' + esc(nombre) + '» en el nombre</b> aparece en la lista negra del SAT (listado del artículo 69-B, corte al ' + esc(corte) + ').</p>' +
        '<p>Eso no certifica a nadie: el nombre puede estar escrito distinto en el listado. Con el <b>RFC</b> la búsqueda es exacta.</p>';
    } else {
      var cuenta = {};
      todos.forEach(function (r) { cuenta[r[2]] = (cuenta[r[2]] || 0) + 1; });
      h = '<p>Encontré <b>' + todos.length.toLocaleString('es-MX') + '</b> registro' + (todos.length === 1 ? '' : 's') + ' con «' + esc(nombre) + '» en el nombre, en la lista negra del SAT (corte al ' + esc(corte) + ')' +
        (todos.length > 1 ? ': ' + ['F', 'P', 'D', 'S'].filter(function (k) { return cuenta[k]; }).map(function (k) { return cuenta[k] + ' ' + esc((sit[k] || { t: k }).t.toLowerCase()); }).join(', ') : '') + '.</p>' +
        '<ul class="pa-lista">' + todos.slice(0, MAX).map(linea).join('') + '</ul>' +
        (todos.length > MAX ? '<p class="pa-chico">Te muestro ' + MAX + '. Los ' + todos.length.toLocaleString('es-MX') + ' están en la aplicación aquí abajo; con el RFC la búsqueda es exacta.</p>' : '');
    }
    /* Si la plataforma tiene a esa empresa en Noticias relevantes, lo dice. */
    var emp = nombre && PE.per.filter(function (x) { return x.emp; }).filter(function (x) { return x.al.some(function (a) { return plano(nombre).indexOf(' ' + a + ' ') >= 0; }); })[0];
    if (emp) h += '<p>📰 Además, la plataforma tiene a <b>' + esc(emp.n) + '</b> en Noticias relevantes, con lo que consta en documentos: <button type="button" class="pa-ej" data-pa-pregunta="' + esc(corta(emp.n)) + '">Ver lo que sabemos</button></p>';
    h += '<p class="pa-chico">⚖️ Aparecer en la lista es una determinación administrativa del SAT, no una condena penal. «Desvirtuado» y «sentencia favorable» significan que salió de la presunción.</p>';
    todos.slice(0, 12).forEach(function (r) { ci.push({ v: (sit[r[2]] || { t: r[2] }).t, etq: r[1] + ' · RFC ' + r[0] + ' · oficio ' + r[3] + ' (' + r[4] + ')', e: 'oficial' }); });
    var fuente = { tx: S.meta.fuente + ', corte al ' + corte, url: S.meta.url };
    var tit = 'Lista negra del SAT: ' + (rfcs.length ? rfcs.slice(0, 3).join(', ') + (rfcs.length > 3 ? '…' : '') : nombre);
    h += charla && charla.deDonde ? charla.deDonde([{ que: 'Listado del artículo 69-B del Código Fiscal', e: 'oficial', fu: fuente }]) : '';
    ultimaSat = tit;
    return {
      html: h, ir: [liga, 'la Lista negra del SAT'], app: { id: 'inspefos', url: liga }, rec: [],
      ficha: { t: 'calculo', tit: tit, txt: texto(h), ci: ci, fu: [fuente], ir: [liga, 'Lista negra del SAT'] },
      sug: [(rfcs.length === 1 || nombre) ? 'Contratos de ' + (rfcs.length === 1 ? rfcs[0] : nombre) + ' en ComprasMX' : '¿Qué contratistas están en la lista negra del SAT?', '¿Qué es una EFOS?', 'Expedientes de casos de la ASF']
    };
  }
  function texto(h) { var d = document.createElement('div'); d.innerHTML = h; return d.textContent.replace(/\s+/g, ' ').trim().slice(0, 600); }

  /* --- Contratos públicos de ComprasMX, en el chat (pedido del autor,
     26-10-2026: «integrar los contratos de ComprasMX» para seguir el dinero).
     Los catálogos los escribe herramientas/actualizar_comprasmx.py y se
     descargan solo cuando se pregunta: el índice de proveedores (1 MB), las
     instituciones (0.6 MB) y la ficha de cada proveedor, por las dos
     primeras letras de su RFC. Cada importe es «oficial» (lo reportó la
     institución, antes de impuestos); las sumas y porcentajes, «derivado».
     Las personas físicas no se publican: su RFC es un dato personal. --- */
  var CMX_DIR = 'assets/auditor/data/comprasmx/', CMX_PAG = 'contratos-publicos.html', CMXP = {};
  function cargaJs(ruta, listo) {
    var ya = listo();
    if (ya) return Promise.resolve(ya);
    if (CMXP[ruta]) return CMXP[ruta];
    CMXP[ruta] = new Promise(function (ok, mal) {
      var s = document.querySelector('script[src*="asistente.js"]'), v = s && /\?v=[\w.-]+/.exec(s.getAttribute('src'));
      var sc = document.createElement('script');
      sc.src = ruta + (v ? v[0] : '');
      sc.onload = function () { var d = listo(); if (d) ok(d); else { CMXP[ruta] = null; mal(); } };
      sc.onerror = function () { CMXP[ruta] = null; mal(); };
      document.head.appendChild(sc);
    });
    return CMXP[ruta];
  }
  function cmxIdx() { return cargaJs(CMX_DIR + 'indice.js', function () { return window.CMX_IDX; }); }
  function cmxInst() { return cargaJs(CMX_DIR + 'inst.js', function () { return window.CMX_INST; }); }
  function cmxProv(rfc) {
    var pre = rfc.slice(0, 2);
    return cargaJs(CMX_DIR + 'p-' + pre.replace(/[^A-Z0-9]/g, '_') + '.js', function () { return window.CMX_P && window.CMX_P[pre]; })
      .then(function (L) { return L[rfc] || null; });
  }
  function pesosCmx(v) {
    if (Math.abs(v) >= 1e6) return '$' + (v / 1e6).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp';
    return '$' + Math.round(v).toLocaleString('es-MX');
  }
  var TIPO_CMX = { AD: 'adjudicación directa', LP: 'licitación pública', I3: 'invitación a cuando menos tres', OT: 'otro procedimiento' };
  var CMX_RE = /\b(contratos?|contratistas?|proveedor(es)?|proveedora|licitacion(es)?|adjudicacion(es)?|comprasmx|compras mx|compranet|a quien(es)? le compra|le (ha )?(pagado|comprado)|cuanto le paga\w*)\b/;
  var CMX_FUERA = ('que cuales cual cuantos cuantas cuanto contrato contratos tiene tienen tuvo la el los las de del en a al y o con por para su sus le les ha han ' +
    'compras mx comprasmx compranet gobierno empresa empresas proveedor proveedores proveedora contratista contratistas quien quienes son es ' +
    'compra compro comprado vende vendio pagado paga pago pagan licitacion licitaciones adjudicacion adjudicaciones directa directas publica publicas ' +
    'dame dime ver muestra muestrame busca buscame revisa sabes hay me puedes quiero saber lista mayores principales grandes mas federal').split(' ');
  function contratosCmx(q) {
    var p = plano(q);
    if (!CMX_RE.test(p) || SAT_PAL.test(p) || /^ (que|q) (es|son|significa)\b/.test(p)) return null;
    var rfcs = (q.match(RFC_RE) || []).map(function (x) { return x.toUpperCase(); });
    /* «¿Qué pasa si no le cobran la pena al contratista?» no busca a una empresa: lo contesta «Documentar para sancionar». */
    if (!rfcs.length && /\b(penas?|multas?|sancion\w*|incumpl\w*|no cumplio|clausulas?|pruebo|que documentos)\b/.test(p)) return null;
    var nombre = p.trim().split(' ').filter(function (w) { return w.length > 1 && CMX_FUERA.indexOf(w) < 0; }).join(' ');
    if (rfcs.length && rfcs[0].length === 13) {
      return { html: '<p>🔒 <code>' + esc(rfcs[0]) + '</code> es el RFC de una <b>persona física</b>. La plataforma no publica a las personas físicas que le venden al gobierno: su RFC es un dato personal. Solo cuentan en los totales de cada institución.</p>' +
        '<p>Si necesitas revisarlo, la fuente oficial es el sitio público de ComprasMX.</p>', ir: [CMX_PAG, 'Contratos públicos'], sug: [], rec: [] };
    }
    if (!rfcs.length && satNorm(nombre).length < 2) {
      return { html: '<p>🧾 Tengo los <b>contratos públicos de ComprasMX</b>: los que reportaron las dependencias federales y los gobiernos que usan la plataforma, en los expedientes de 2025 y 2026. Dime una <b>empresa</b> («contratos de Laboratorios Pisa»), su <b>RFC</b> o una <b>institución</b> («¿a quién le compra el IMSS?») y te digo cuántos contratos, por cuánto, por qué procedimiento y la liga de cada uno.</p>',
        ir: [CMX_PAG, 'Contratos públicos'], sug: ['¿A quién le compra el IMSS?', 'Contratos del Tren Maya', '¿Qué contratistas están en la lista negra del SAT?'], rec: [] };
    }
    var termino = rfcs.length ? rfcs[0] : nombre;
    var prom = Promise.all([cmxIdx(), cmxInst()]).then(function (D) {
      var I = D[0], T = D[1];
      if (rfcs.length) return cmxProv(rfcs[0]).then(function (d) { return respProv(rfcs[0], d, I.meta); });
      var ws = satNorm(nombre).split(' ');
      /* Una institución por sus siglas («IMSS», «CFE») o por su nombre. */
      var claves = Object.keys(T.i), sig = null;
      if (ws.length <= 3) claves.forEach(function (k) { var s = satNorm(T.i[k].s).replace(/ /g, ''); if (!sig && s.length > 1 && ws.join('') === s) sig = k; });
      var porNom = claves.filter(function (k) { var n = satNorm(T.i[k].n); return ws.every(function (w) { return (' ' + n + ' ').indexOf(' ' + w + ' ') >= 0; }); });
      var provs = I.r.filter(function (r) { var n = ' ' + satNorm(r[1]) + ' '; return ws.every(function (w) { return n.indexOf(' ' + w + ' ') >= 0; }); });
      var pideInst = /\b(a quien(es)? le compra|proveedores (de|del)|contratistas (de|del)|le compra)\b/.test(p);
      if (sig || (porNom.length && (pideInst || !provs.length))) {
        var k = sig || porNom.sort(function (a, b) { return T.i[b].m - T.i[a].m; })[0];
        return respInst(k, T.i[k], T.meta, porNom.length > 1 && !sig ? porNom.length : 0);
      }
      if (!provs.length) return { html: '<p>◻️ No encontré «' + esc(nombre) + '» entre los <b>' + I.meta.proveedores.toLocaleString('es-MX') + '</b> proveedores (personas morales) ni entre las <b>' + I.meta.instituciones.toLocaleString('es-MX') + '</b> instituciones con contratos en ComprasMX, en los expedientes de 2025 y 2026.</p>' +
        '<p>Eso no quiere decir que no tenga contratos: el nombre puede estar escrito distinto, sus contratos pueden ser de otros años, o la institución puede no reportar en ComprasMX. Varios órganos autónomos, como el INE, y los gobiernos que no usan la plataforma publican sus contratos en sus propios portales y en la Plataforma Nacional de Transparencia. Con el <b>RFC</b> la búsqueda es exacta.</p>',
        ir: [CMX_PAG + '?q=' + encodeURIComponent(nombre), 'Contratos públicos'], sug: [], rec: [], web: nombre };
      var exacto = provs.filter(function (r) { return satNorm(r[1]).replace(/\b(S ?A|DE|C ?V|S ?A ?P ?I|R ?L|S ?C)\b/g, '').replace(/ +/g, ' ').trim() === ws.join(' '); });
      if (provs.length === 1 || exacto.length === 1) { var r1 = provs.length === 1 ? provs[0] : exacto[0]; return cmxProv(r1[0]).then(function (d) { return respProv(r1[0], d, I.meta); }); }
      return { html: '<p>Encontré <b>' + provs.length.toLocaleString('es-MX') + '</b> proveedores con «' + esc(nombre) + '» en el nombre. ¿Cuál buscas?</p><p>' +
        provs.slice(0, 8).map(function (r) { return '<button type="button" class="pa-ej" data-pa-pregunta="' + esc('Contratos de ' + r[0]) + '">' + esc(r[1]) + '</button>'; }).join(' ') + '</p>' +
        (provs.length > 8 ? '<p class="pa-chico">Te muestro 8. Con el RFC la búsqueda es exacta.</p>' : ''),
        ir: [CMX_PAG + '?q=' + encodeURIComponent(nombre), 'Contratos públicos'], sug: [], rec: [] };
    }, function () {
      return { html: '<p>No pude descargar ahora el catálogo de contratos de ComprasMX. Revisa tu conexión y vuelve a preguntarme.</p>', ir: [CMX_PAG, 'Contratos públicos'], sug: [], rec: [] };
    });
    return { espera: prom, tit: 'Contratos en ComprasMX: ' + termino };
  }
  function cmxFuente(M) {
    return { tx: M.fuente + ' (archivos ' + M.archivos.map(function (a) { return a.anio; }).join(' y ') + ', descargados el ' + M.descarga + ')', url: M.url };
  }
  function cmxCaveat() {
    return '<p class="pa-chico">⚖️ Tener contratos con el gobierno no es una irregularidad. El importe es el que reportó cada institución, antes de impuestos; en un contrato abierto suele ser el máximo, no lo pagado. ComprasMX no publica pagos: lo pagado se rinde en la Cuenta Pública.</p>';
  }
  function respProv(rfc, d, M) {
    if (!d) return { html: '<p>◻️ El RFC <code>' + esc(rfc) + '</code> no tiene contratos en los expedientes de 2025 y 2026 de ComprasMX.</p><p>Puede tenerlos en otros años o con gobiernos que no usan ComprasMX. Eso no certifica nada.</p>',
      ir: [CMX_PAG + '?q=' + rfc, 'Contratos públicos'], sug: ['¿Está en la lista negra del SAT el RFC ' + rfc + '?'], rec: [] };
    var tp = d.tp || {}, mtp = d.mtp || {}, fuente = cmxFuente(M), ci = [];
    var partes = ['AD', 'LP', 'I3', 'OT'].filter(function (k) { return tp[k]; }).map(function (k) {
      return '<b>' + tp[k].toLocaleString('es-MX') + '</b> por ' + TIPO_CMX[k] + (mtp[k] ? ' (' + pesosCmx(mtp[k]) + ')' : '');
    });
    var pctAd = d.m ? Math.round((mtp.AD || 0) / d.m * 1000) / 10 : 0;
    var h = '<p>🏢 <b>' + esc(d.n) + '</b> (<code>' + esc(rfc) + '</code>) tiene <b>' + d.c.toLocaleString('es-MX') + ' contrato' + (d.c === 1 ? '' : 's') + '</b> en ComprasMX, en los expedientes de 2025 y 2026, por <b>' + pesosCmx(d.m) + '</b> antes de impuestos ' + chip({ e: 'derivado' }) + '.</p>' +
      '<p>Por procedimiento: ' + partes.join('; ') + '.' + (d.m && mtp.AD ? ' La adjudicación directa es el ' + pctAd.toLocaleString('es-MX') + ' % de su importe ' + chip({ e: 'derivado' }) + '.' : '') + '</p>' +
      (d.o ? '<p class="pa-chico">Además, en otras monedas (no se convierten): ' + Object.keys(d.o).map(function (k) { return d.o[k].toLocaleString('es-MX', { maximumFractionDigits: 0 }) + ' ' + esc(k); }).join(', ') + '.</p>' : '') +
      '<p>Le vende a <b>' + d.ni + '</b> institucion' + (d.ni === 1 ? '' : 'es') + (d.ni > 1 ? '; las principales:' : ':') + '</p><ul class="pa-lista">' + d.i.map(function (x) {
        return '<li><b>' + esc(x[1]) + '</b>: ' + x[3].toLocaleString('es-MX') + ' contrato' + (x[3] === 1 ? '' : 's') + ', ' + pesosCmx(x[4]) + '</li>';
      }).join('') + '</ul>' +
      '<p>Sus contratos mayores ' + chip({ e: 'oficial' }) + ':</p><ul class="pa-lista">' + d.k.map(function (k) {
        return '<li>' + pesosCmx(k[3]) + (k[4] !== 'MXN' ? ' ' + esc(k[4]) : '') + ' · <b>' + esc(k[1]) + '</b> · ' + esc(TIPO_CMX[k[5]] || '') + (k[6] ? ' · ' + esc(k[6]) : '') + '<br><span class="pa-chico">' + esc(k[2]) + '</span>' +
          (k[7] ? ' <a href="' + esc(M.detalle.replace('%s', k[7])) + '" target="_blank" rel="noopener">Ver en ComprasMX ↗</a>' : '') + '</li>';
      }).join('') + '</ul>';
    if (d.sat) {
      var s = (IN.sat || {})[d.sat[0]] || { t: d.sat[0], txt: '' };
      h += '<p>' + (d.sat[0] === 'F' ? '⛔' : d.sat[0] === 'P' ? '⚠️' : 'ℹ️') + ' <b>Aparece en la lista 69-B del SAT</b> como <b>' + esc(s.t) + '</b> (oficio ' + esc(d.sat[1]) + ', ' + esc(d.sat[2]) + '). ' + esc(s.txt || '') + '</p>';
    }
    var emp = PE.per.filter(function (x) { return x.emp; }).filter(function (x) { return x.al.some(function (a) { return plano(d.n).indexOf(' ' + a + ' ') >= 0; }); })[0];
    if (emp) h += '<p>📰 La plataforma también tiene a <b>' + esc(corta(emp.n)) + '</b> en Noticias relevantes: <button type="button" class="pa-ej" data-pa-pregunta="' + esc(corta(emp.n)) + '">Ver lo que sabemos</button></p>';
    h += cmxCaveat();
    ci.push({ v: d.c.toLocaleString('es-MX') + ' contratos', etq: d.n + ' · RFC ' + rfc + ' · expedientes 2025 y 2026', e: 'oficial' });
    ci.push({ v: pesosCmx(d.m), etq: 'Importe antes de impuestos, suma de sus contratos en pesos', e: 'derivado' });
    d.k.forEach(function (k) { ci.push({ v: pesosCmx(k[3]) + (k[4] !== 'MXN' ? ' ' + k[4] : ''), etq: k[0] + ' · ' + k[1] + ' · ' + k[2], e: 'oficial' }); });
    var tit = 'Contratos en ComprasMX: ' + d.n;
    h += charla && charla.deDonde ? charla.deDonde([{ que: 'Datos relevantes de los contratos de ComprasMX', e: 'oficial', fu: fuente }]) : '';
    return { html: h, ir: [CMX_PAG + '?q=' + rfc, 'Contratos públicos'], rec: [],
      ficha: { t: 'calculo', tit: tit, txt: texto(h), ci: ci, fu: [fuente], ir: [CMX_PAG + '?q=' + rfc, 'Contratos públicos'] },
      sug: ['¿Está en la lista negra del SAT el RFC ' + rfc + '?'].concat(d.i.slice(0, 2).map(function (x) { return '¿A quién le compra ' + x[1] + '?'; })) };
  }
  function respInst(k, d, M, otras) {
    var fuente = cmxFuente(M), ci = [];
    var pc = d.c ? Math.round(d.ad / d.c * 1000) / 10 : 0, pm = d.m ? Math.round(d.mad / d.m * 1000) / 10 : 0;
    var h = '<p>🏛️ <b>' + esc(d.n) + '</b>' + (d.s && d.s !== d.n ? ' (' + esc(d.s) + ')' : '') + ' reportó <b>' + d.c.toLocaleString('es-MX') + ' contratos</b> en ComprasMX, en los expedientes de 2025 y 2026, por <b>' + pesosCmx(d.m) + '</b> antes de impuestos ' + chip({ e: 'derivado' }) + '.</p>' +
      '<p>Por <b>adjudicación directa</b>: ' + d.ad.toLocaleString('es-MX') + ' contratos (' + pc.toLocaleString('es-MX') + ' % del total) y ' + pesosCmx(d.mad) + ' (' + pm.toLocaleString('es-MX') + ' % del importe) ' + chip({ e: 'derivado' }) + '.</p>' +
      (d.ot ? '<p class="pa-chico">Además, en otras monedas (no se convierten): ' + Object.keys(d.ot).map(function (x) { return d.ot[x].toLocaleString('es-MX', { maximumFractionDigits: 0 }) + ' ' + esc(x); }).join(', ') + '.</p>' : '') +
      '<p>Le compró a <b>' + d.np.toLocaleString('es-MX') + '</b> empresas' + (d.pf ? ' y a personas físicas (' + d.pf.toLocaleString('es-MX') + ' contratos, ' + pesosCmx(d.mpf) + '; no se publican sus nombres)' : '') + '. Sus 10 proveedores mayores:</p><ol class="pa-lista">' +
      d.p.map(function (x) { return '<li><button type="button" class="pa-ej" data-pa-pregunta="' + esc('Contratos de ' + x[0]) + '">' + esc(x[1]) + '</button> ' + pesosCmx(x[3]) + ' · ' + x[2].toLocaleString('es-MX') + ' contrato' + (x[2] === 1 ? '' : 's') + '</li>'; }).join('') + '</ol>' +
      (otras ? '<p class="pa-chico">Hay ' + otras + ' instituciones con ese nombre; te muestro la de mayor importe. Escribe sus siglas para elegir otra.</p>' : '') + cmxCaveat();
    ci.push({ v: d.c.toLocaleString('es-MX') + ' contratos', etq: d.n + ' · expedientes 2025 y 2026', e: 'oficial' });
    ci.push({ v: pesosCmx(d.m), etq: 'Importe antes de impuestos, suma de sus contratos en pesos', e: 'derivado' });
    ci.push({ v: pm.toLocaleString('es-MX') + ' %', etq: 'Del importe, por adjudicación directa (' + pesosCmx(d.mad) + ' ÷ ' + pesosCmx(d.m) + ')', e: 'derivado' });
    d.p.forEach(function (x) { ci.push({ v: pesosCmx(x[3]), etq: x[1] + ' · ' + x[2] + ' contratos', e: 'derivado' }); });
    var tit = 'Contratos de ' + d.n + ' en ComprasMX';
    h += charla && charla.deDonde ? charla.deDonde([{ que: 'Datos relevantes de los contratos de ComprasMX', e: 'oficial', fu: fuente }]) : '';
    return { html: h, ir: [CMX_PAG + '?i=' + encodeURIComponent(k), 'Contratos públicos'], rec: [],
      ficha: { t: 'calculo', tit: tit, txt: texto(h), ci: ci, fu: [fuente], ir: [CMX_PAG + '?i=' + encodeURIComponent(k), 'Contratos públicos'] },
      sug: d.p.slice(0, 2).map(function (x) { return 'Contratos de ' + x[1]; }) };
  }
  /* Contratistas que también están en la lista 69-B del SAT. */
  var CRUCE_RE = /\b(contratistas?|proveedor(es)?|empresas? con contratos?)\b.*\b(lista negra|69 ?b|efos|sat)\b|\b(lista negra|69 ?b|efos)\b.*\b(contratistas?|proveedor(es)?|contratos?)\b/;
  function cruceSat(q) {
    if (!CRUCE_RE.test(plano(q)) || (q.match(RFC_RE) || []).length) return null;
    return { espera: cmxInst().then(function (T) {
      var sit = IN.sat || {}, L = T.sat;
      var h = '<p>Crucé los <b>' + T.meta.proveedores.toLocaleString('es-MX') + '</b> proveedores con contratos en ComprasMX (expedientes 2025 y 2026) contra la lista 69-B del SAT, por RFC: <b>' + L.length + '</b> aparecen ' + chip({ e: 'derivado' }) + '.</p>' +
        '<ul class="pa-lista">' + L.map(function (r) { var s = sit[r[2]] || { t: r[2], i: '' }; return '<li>' + (s.i || '') + ' <button type="button" class="pa-ej" data-pa-pregunta="' + esc('Contratos de ' + r[0]) + '">' + esc(r[1]) + '</button> · <b>' + esc(s.t) + '</b> · ' + r[3] + ' contrato' + (r[3] === 1 ? '' : 's') + ', ' + pesosCmx(r[4]) + '</li>'; }).join('') + '</ul>' +
        '<p>«Desvirtuado» y «sentencia favorable» quieren decir que salió de la presunción; solo «definitivo» es una determinación firme del SAT, y «presunto» es un proceso abierto.</p>' + cmxCaveat();
      var fuentes = [cmxFuente(T.meta)];
      return { html: h, ir: [CMX_PAG + '#cruce', 'Contratos públicos'], rec: [], sug: [],
        ficha: { t: 'calculo', tit: 'Contratistas de ComprasMX en la lista 69-B del SAT', txt: texto(h), ci: L.map(function (r) { return { v: (sit[r[2]] || { t: r[2] }).t, etq: r[1] + ' · RFC ' + r[0], e: 'oficial' }; }), fu: fuentes, ir: [CMX_PAG + '#cruce', 'Contratos públicos'] } };
    }, function () { return { html: '<p>No pude descargar ahora el catálogo de contratos.</p>', ir: [CMX_PAG, 'Contratos públicos'], sug: [], rec: [] }; }), tit: 'Contratistas en la lista 69-B' };
  }

  /* --- Las demás: qué pide el lector y con qué la abrimos. --- */
  var FOLIO_RE = /\bAV-[A-Z0-9]{2,8}-[0-9A-F]{6,}\b|\b[0-9A-F]{64}\b/i, DICT_RE = /\b(DP|NT)-\d{8}-[0-9A-F]{8}\b/i;
  function enteFederal(t) {
    var p = plano(t), hit = null;
    B.fichas.forEach(function (f) {
      if (hit || f.t !== 'ficha') return;
      var id = f.ir[0].split(':').pop().replace(/-/g, ' ');
      if (p.indexOf(' ' + id + ' ') >= 0 && id.length > 2 || p.indexOf(plano(f.tit.split(' (')[0])) >= 0) hit = f;
    });
    return hit;
  }
  function inspector(q, previas) {
    if (!IN.apps.length) return null;
    var p = plano(q), t = String(q).trim(), m;
    var liga = (/https?:\/\/[^\s<>"']+/i.exec(t) || [])[0];
    /* 1. Un folio, una huella o la liga de verificación de un documento de la plataforma. */
    if (liga && /[?&]verifica=/.test(liga) && liga.indexOf(location.host || '#') >= 0 || liga && /uzoraproductos-arch\.github\.io/.test(liga) && /[?&]verifica=/.test(liga)) {
      var pag = liga.split('?')[0].split('/').pop() || APP.inspverifica.url;
      return respApp('inspverifica', pag + '?' + liga.split('?')[1],
        '<p>🔏 Es la liga de verificación de un documento de Auditavisión. La abro aquí mismo y comparo, cifra por cifra, su huella digital con los datos vigentes de la plataforma: el resultado sale en el recuadro de abajo.</p>');
    }
    if (DICT_RE.test(t) && !FOLIO_RE.test(t)) {
      return { html: '<p>🧾 Ese es el folio de un <b>dictamen</b> del Auditor. El dictamen no se guarda en ningún servidor: se comprueba abriendo su enlace, y el Auditor vuelve a contestar la pregunta con la base vigente. Si las cifras cambiaron, el folio cambia.</p>' +
        '<p>Para los estados de cuenta y las fichas técnicas, que sí se comprueban por folio, escríbeme el folio que empieza con <code>AV-</code>.</p>', ir: [APP.inspverifica.url, APP.inspverifica.n], sug: [], rec: [] };
    }
    if ((m = FOLIO_RE.exec(t))) {
      var fo = m[0].toUpperCase();
      if (/^AV-EC-/.test(fo)) return { html: '<p>🧾 <code>' + esc(fo) + '</code> es el folio de un <b>estado de cuenta personal</b> de la Calculadora Cívica. Su huella sale de los datos que escribió quien lo expidió, así que se comprueba con su <b>liga de verificación completa</b>, la que viene impresa en el documento. Pégamela aquí y lo compruebo.</p>',
        ir: ['herramienta-calculadora-ticket.html', 'Tu estado de cuenta'], sug: [], rec: [] };
      var ft = /^AV-FT-/.test(fo);
      return respApp('inspverifica', (ft ? APP.inspentes.url : APP.inspverifica.url) + '?verifica=' + encodeURIComponent(fo),
        '<p>🔏 Compruebo ' + (/^[0-9A-F]{64}$/.test(fo) ? 'la huella digital' : 'el folio <code>' + esc(fo) + '</code>') + ' aquí mismo: recalculo la huella de ' + (ft ? 'las fichas técnicas del Auditor de entes públicos' : 'cada estado de cuenta') +
        ' con los datos vigentes de la plataforma y te digo si coincide. El resultado sale en el recuadro de abajo.</p>' +
        '<p class="pa-chico">Si no coincide, o el documento se alteró, o se expidió con datos anteriores.</p>');
    }
    /* 2. La liga de una nota: «Contrasta una nota» la lee aquí mismo. */
    if (liga) {
      return respApp('inspnota', APP.inspnota.url + '?liga=' + encodeURIComponent(liga),
        '<p>📰 Leo la nota aquí mismo con <b>Contrasta una nota</b>: busco sus cifras en pesos, las pongo junto a su documento oficial y te doy el veredicto, cifra por cifra, con su semáforo. Puede tardar unos segundos.</p>' +
        '<p class="pa-chico">Lo que no empata con un documento queda «sin contrastar» y no cuenta como falso. Si la página no se deja leer, ahí mismo puedes pegar el texto.</p>');
    }
    /* 3. La lista negra del SAT. */
    var sat = listaNegra(q);
    if (sat) return sat;
    /* 4. Un ente: «diagnóstico de Pemex», «auditor de entes: CFE». */
    var pideEnte = /\b(auditor de entes|diagnostico|ficha tecnica|salud financiera|audita|auditame|revisa)\b/.test(p);
    /* Un estado o un municipio lo contesta la plática con su ficha; aquí, los entes federales. */
    var fe = entidadDe(q) ? null : enteFederal(q.replace(/salud financiera|diagn[oó]stico|ficha t[eé]cnica|auditor de entes( p[uú]blicos)?/gi, ' '));
    if (fe && (pideEnte || /\b(dependencia|ente|entes)\b/.test(p))) {
      var rf = charla ? charla.deFicha(fe) : { html: '<p><b>' + esc(fe.tit) + '</b></p>', ficha: fe };
      rf.ir = fe.ir; rf.app = { id: 'inspentes', url: fe.ir[0], abre: true }; rf.sug = []; rf.rec = [];
      rf.html = '<p>🏢 Abro su diagnóstico en el <b>Auditor de entes públicos</b>, aquí abajo: si gastó lo que aprobó la Cámara, si rindió cuentas y qué quedó por aclarar.</p>' + rf.html;
      return rf;
    }
    if (pideEnte && /\bentes?\b|auditor de entes/.test(p) && !entidadDe(q)) {
      var resto = t.replace(/^.*?\b(auditor de entes( p[uú]blicos)?|diagn[oó]stico|ficha t[eé]cnica|salud financiera)\b\s*(de(l| la| los| las)?\s*)?/i, '').replace(/[?¿!¡.]/g, '').trim();
      if (resto.length > 2) return respApp('inspentes', APP.inspentes.url + '?q=' + encodeURIComponent(resto),
        '<p>🏢 Busco «' + esc(resto) + '» en el <b>Auditor de entes públicos</b>, aquí abajo. Elige el ente y ve su diagnóstico.</p>');
    }
    /* 5. Un caso de la ASF: «expediente de Segalmex», «casos por aclarar del AIFA». */
    if (/\b(expedientes?|casos?( por aclarar)?|pliegos?)\b/.test(p) && charla) {
      var ex = null;
      B.fichas.forEach(function (f) {
        if (ex || f.t !== 'expediente') return;
        var clave = plano(f.k.split(' ').slice(-2).join(' ')).trim(), id = f.ir[0].split('#exp-').pop().replace(/-/g, ' ');
        if (p.indexOf(' ' + id + ' ') >= 0 || (clave && p.indexOf(' ' + clave + ' ') >= 0) || p.indexOf(plano(f.tit.split(':')[0])) >= 0) ex = f;
      });
      if (ex) {
        var re = charla.deFicha(ex);
        re.app = { id: 'inspasf', url: ex.ir[0], abre: true }; re.rec = []; re.sug = ['Expedientes de casos de la ASF', '¿Qué es un pliego de observaciones?'];
        re.html = '<p>📂 Es uno de los <b>expedientes de casos de la ASF</b>. Te lo abro aquí abajo con sus documentos.</p>' + re.html;
        return re;
      }
    }
    /* 6. Las aplicaciones por su nombre o por lo que hacen. */
    var id = null;
    IN.apps.forEach(function (a) { if (!id && p.indexOf(' ' + a._p.trim() + ' ') >= 0) id = a.id; });
    if (!id) {
      if (/\bcontrast(a|ar|ame)\b.*\b(nota|noticia)|\b(verifica|verificar|checa|checar|revisa|revisar)(me)? (una|esta|la|esa) (nota|noticia|publicacion)\b/.test(p) && !/\d/.test(p)) id = 'inspnota';
      else if (/\b(verific|comprob|valid)\w* (un |una |el |la |mi |este |esta )?(estado de cuenta|folio|ficha tecnica|documento)\b|\bes (autentico|original|falso)\b.*\b(estado de cuenta|documento)\b/.test(p)) id = 'inspverifica';
      else if (/\b(servicios? de investigacion|investigacion a la medida|(contratar|solicitar|pedir|encargar|encargarles|cotizar)( una| un)? (investigacion|servicio|revision|expediente)|quiero que investiguen|investiguen (esto|un caso|a))\b/.test(p)) id = 'servicios.html';
      else if (/\b(que encontro la asf|expedientes de (la )?asf|casos de la asf|expedientes de casos)\b/.test(p)) id = 'inspasf';
      else if (/\b(modo inspector|grandes investigaciones|(seis|6) aplicaciones|que (puedo|puedes) investigar|como investigo)\b/.test(p)) id = '*';
    }
    if (!id) return null;
    /* «¿Qué es…?» lo contesta el glosario o la página; aquí, quien quiere usarla. */
    if (/^\s*(que|q) (es|son|significa|hace)\b/.test(p) && id !== '*') return null;
    if (id === '*') {
      return {
        html: '<p>🔍 El <b>Modo Inspector</b> son seis aplicaciones para grandes investigaciones, y todas las usas desde aquí, sin salir del chat. Dime cuál, o pásame directo lo que traes:</p><ul class="pa-lista">' +
          IN.apps.map(function (a) { return '<li><span aria-hidden="true">' + a.ico + '</span> <b>' + esc(a.n) + '.</b> ' + esc(a.frase) + '. <span class="pa-chico">' + esc(EJ_APP[a.id] || '') + '</span></li>'; }).join('') + '</ul>',
        ir: [IN.pagina, 'el Modo Inspector'], sug: IN.apps.map(function (a) { return a.n; }), rec: []
      };
    }
    /* El tema de una investigación: lo que el lector dijo después de pedirla
       («…sobre el Tren Maya») o, si dice «esto», su pregunta anterior. */
    var tema = id !== 'servicios.html' ? '' : (/\b(sobre|de|del|acerca de|para)\s+(.{3,})$/i.exec(t.replace(/^.*?investigaci[oó]n\b/i, '').replace(/[?¿!¡.]+$/, '')) || [])[2] || '';
    if (/^(esto|eso|este caso|ese caso|lo anterior|lo mismo)$/i.test(tema.trim())) tema = '';
    if (id === 'servicios.html' && !tema && /\b(esto|eso|este caso|ese caso|lo anterior|lo mismo)\b/.test(p) && previas && previas.length) tema = previas[previas.length - 1];

    var a = APP[id];

    var url = a.url + (id === 'servicios.html' && tema ? '?tema=' + encodeURIComponent(tema.slice(0, 160)) : '');
    return respApp(id, url, '<p><span aria-hidden="true">' + a.ico + '</span> <b>' + esc(a.n) + '.</b> ' + esc(a.desc.replace(/\s*Tiene su propia página\./, '')) + '</p>' +
      '<p>' + (tema ? 'Te abro el formulario aquí abajo, ya con el tema: «' + esc(tema.slice(0, 120)) + '». Revísalo y completa lo demás.' :
        (EJ_APP[id] ? esc(EJ_APP[id]) + ' ' : '') + 'O úsala aquí abajo, sin salir del chat.') + '</p>');

  }
  /* Lo que el lector puede escribirme para cada aplicación. */
  var EJ_APP = {
    inspasf: 'Pregúntame por un caso: «expediente de Segalmex», «casos por aclarar del AIFA».',
    inspentes: 'Pídeme un diagnóstico: «diagnóstico de Pemex», «salud financiera de Jalisco», «Zapopan».',
    inspnota: 'Pégame la liga de la nota, o «¿es cierto que…?» con la cifra que oíste.',
    inspefos: 'Escríbeme un RFC o un nombre: «¿está en la lista negra la empresa…?».',
    inspverifica: 'Pégame el folio (AV-…) o la huella digital del documento.',
    'servicios.html': 'Cuéntame el caso y te llevo al formulario, con el tema ya escrito.'
  };

  /* ================= Inversión y Megaobras, dentro del chat =================
     (24-10-2026, pedido del autor): cada obra con lo que se aprobó, lo que
     costó, su sobrecosto, lo que gana o pierde al año y lo que dijo la ASF;
     en qué invirtió cada presidente, los rankings y las cinco aplicaciones,
     que se abren en la respuesta como las del Modo Inspector. Las cifras y
     sus textos los escribe herramientas/asistente_megaobras.py con los
     mismos formatos de las páginas: aquí no se calcula ninguna. */
  var MO = (B.dat && B.dat.mo) || { obras: [], sx: [], apps: [], tot: {}, portales: [], sims: {} }, OB = {};
  var PESO_FU = ((B.dat && B.dat.datos && B.dat.datos.peso && B.dat.datos.peso.fx) || {}).BX_INPC;
  MO.apps.forEach(function (a) { a.grupo = MO.nombre; a.tot = MO.apps.length; a._p = plano(a.n); a._c = plano(a.n.split(/,| y /)[0]); a._base = sinParam(a.url).replace(/\.html$/, ''); APP[a.id] = a; });
  /* Costo Ambiental y la Calculadora Cívica, dentro del chat (24-10-2026,
     pedido del autor): sus aplicaciones se reconocen por su nombre o por como
     se dicen en la calle (ALIAS_APPS de herramientas/asistente.py) y se abren
     en el marco de la respuesta, como las del Modo Inspector. */
  var HA = { apps: [], de: {} };
  [(B.dat && B.dat.amb), (B.dat && B.dat.calc)].forEach(function (h) {
    if (!h) return;
    h._p = plano(h.nombre);
    h.apps.forEach(function (a) { a.grupo = h.nombre; a.tot = h.apps.length; a.h = h; a._al = [plano(a.n)].concat((a.al || []).map(plano)); a._base = sinParam(a.url).replace(/\.html$/, ''); APP[a.id] = a; HA.apps.push(a); });
    HA.de[h.pagina] = h;
  });
  function respHerr(h) {
    return {
      html: '<p><span aria-hidden="true">' + h.ico + '</span> <b>' + esc(h.nombre) + '</b> son ' + h.apps.length + ' aplicaciones, y todas las usas desde aquí, sin salir del chat:</p><ul class="pa-lista">' +
        h.apps.map(function (a) { return '<li><span aria-hidden="true">' + a.ico + '</span> <b>' + esc(a.n) + '.</b> ' + esc(a.frase) + '.</li>'; }).join('') + '</ul>' +
        '<p>Dime cuál quieres y la abro aquí abajo. Empiezo por la primera:</p>',
      ir: [h.pagina, h.nombre], app: { id: h.apps[0].id, url: h.apps[0].url }, rec: [],
      sug: h.apps.slice(1, 4).map(function (a) { return a.n; })
    };
  }
  /* «Gano 15 mil al mes, ¿cuánto me retienen?»: la Calculadora Cívica hace la
     cuenta con la tarifa oficial del ISR; el chat no pone cifras propias. */
  var SUELDO = /\b(gano|ganamos|mi sueldo|mi salario|mi ingreso|mis ingresos|me pagan|cobro|percibo|facturo)\b/;
  /* La cifra que se lee es la del ingreso: la primera después de «gano»,
     «me pagan»…, y nunca la que cuenta hijos, años o días («gano 15 mil y
     tengo 2 hijos» usa 15,000; «tengo 2 hijos y gano 15 mil», también). */
  var NO_ES_INGRESO = /^\s*(hijos?|hijas?|ninos?|ninas?|dependientes?|personas?|anos?|meses|semanas?|dias?|horas?|empleados?|trabajadores?|cuartos?|casas?|departamentos?|locales?|veces|%|por ciento)\b/;
  function sueldoDe(p) {
    var t = p.replace(/(\d) (?=\d{3}\b)/g, '$1'), re = /(\d[\d,]*(?:\.\d+)?)\s*(mil\b|k\b)?/g, m, cand = [], s = SUELDO.exec(t), desde = s ? s.index : 0;
    while ((m = re.exec(t))) {
      if (NO_ES_INGRESO.test(t.slice(m.index + m[0].length))) continue;
      var v = parseFloat(m[1].replace(/,/g, '')) * (m[2] ? 1000 : 1);
      if (v >= 100 && v < 1e9) cand.push({ v: Math.round(v * 100) / 100, i: m.index });
    }
    var tras = cand.filter(function (c) { return c.i >= desde; });
    return (tras[0] || cand[0] || { v: 0 }).v;
  }
  /* El régimen, si el lector lo dice; si no, sueldos y salarios (lo que la
     calculadora supone y deja cambiar). */
  var REGIMEN = [
    ['plataformas', /\b(uber|didi|rappi|cabify|indrive|airbnb|booking|mercado libre|amazon|plataformas? (digitales?|tecnologicas?)|por (una )?app)\b/],
    ['resico', /\b(resico|simplificado de confianza)\b/],
    ['arrendamiento', /\b(rento (mi|una|un)|renta de (mi|mis)|cobro (la |de )?renta|me pagan (la |de )?renta|arrendamiento|arrendador)\b/],
    ['honorarios', /\b(honorarios|freelance|independiente|por mi cuenta|negocio propio|mi negocio|actividad empresarial|profesionista)\b/],
    ['sueldos', /\b(sueldos? y salarios?|nomina|asalariad[oa]|mi patron|mi empresa me paga|empleado de)\b/]
  ];
  var PLATA = [['hospedaje', /\b(airbnb|booking|hospedaje)\b/], ['bienes', /\b(mercado libre|amazon|vendo|ventas?)\b/], ['transporte', /./]];
  function regimenDe(p) {
    var r = REGIMEN.filter(function (x) { return x[1].test(p); })[0], pl = null;
    if (r && r[0] === 'plataformas') pl = PLATA.filter(function (x) { return x[1].test(p); })[0][0];
    return { r: r ? r[0] : '', pl: pl };
  }
  function herramienta(q) {
    if (!HA.apps.length) return null;
    var p = plano(q), cc = APP.ccticket, CR = B.dat.calc || {};
    if (cc && SUELDO.test(p) && !/\b(diputad|senador|ministr|president|gobernador|alcalde|funcionari)\w*/.test(p)) {
      var m = sueldoDe(p), per = /\b(al ano|anual|anuales|por ano)\b/.test(p) ? 'ano' : 'mes', nat = /\b(neto|netos|libres?|en mano|ya sin impuestos)\b/.test(p) ? 'neto' : 'bruto';
      var rg = regimenDe(p), quin = m && /\b(quincena|quincenal|quincenales)\b/.test(p), sem = m && /\b(semana|semanal|semanales)\b/.test(p), m0 = m;
      /* Por quincena: la calculadora trabaja por mes, y un mes son dos quincenas (derivado, se dice la operación). */
      if (quin) { m = Math.round(m * 2 * 100) / 100; per = 'mes'; }
      if (sem) m = 0;
      var liga = 'herramienta-calculadora-ticket-retienen.html' + (m ? '?m=' + m + '&p=' + per + '&n=' + nat + (rg.r ? '&r=' + rg.r : '') + (rg.pl ? '&pl=' + rg.pl : '') : '');
      var regN = rg.r && CR.reg ? CR.reg[rg.r] : '', plN = rg.pl && CR.plat ? CR.plat[rg.pl] : '';
      var hijos = /\b(hijos?|hijas?|dependientes?|esposa|esposo|familia)\b/.test(p);
      return respApp('ccticket', liga, '<p><span aria-hidden="true">🧾</span> Esa cuenta la hace <b>' + esc(cc.n) + '</b>, de la ' + esc(cc.grupo) + ': ' +
        (m ? 'ya le puse tu ingreso de <b>$' + m.toLocaleString('es-MX') + (per === 'ano' ? ' al año' : ' al mes') + '</b>, ' + (nat === 'neto' ? 'después' : 'antes') + ' de descuentos' +
          (regN ? ', en <b>' + esc(regN) + '</b>' + (plN ? ' (' + esc(plN.toLowerCase()) + ')' : '') : '') + '. ' :
          sem ? 'la calculadora trabaja por mes o por año, así que escribe ahí lo que juntas al mes (no convierto semanas: los meses no tienen semanas exactas). ' : 'escribe lo que ganas. ') +
        'Te dice cuánto te retienen, con la tarifa oficial del ISR, y a dónde va cada peso de tu impuesto, en un documento con folio y huella.</p>' +
        (quin ? '<p class="pa-chico">' + chip({ e: 'derivado' }) + ' <b>Operación:</b> $' + m0.toLocaleString('es-MX') + ' a la quincena × 2 quincenas = $' + m.toLocaleString('es-MX') + ' al mes.</p>' : '') +
        (hijos ? '<p class="pa-chico">Tus hijos o tu familia no cambian lo que te retienen cada mes: la tarifa del artículo 96 de la Ley del ISR no tiene descuento por dependientes. Algunos gastos de la familia, como los médicos y hospitalarios, se deducen en la declaración anual (artículo 151), que esta cuenta no hace.</p>' : '') +
        '<p class="pa-chico">La cuenta la hace la calculadora con las tarifas publicadas. ' + (regN ? 'Si tu régimen es otro, cámbialo ahí mismo, en «1 · Tu ingreso».' : /\bfacturo\b/.test(p) ? 'Como facturas, elige en «1 · Tu ingreso» si estás en el RESICO o en actividad empresarial, porque cambia mucho lo que pagas; mientras, supuse sueldos y salarios.' : 'Supuse que trabajas con un patrón (sueldos y salarios); si no es así, cámbialo ahí mismo, en «1 · Tu ingreso».') + '</p>',
        { sug: ['¿A dónde va cada peso de mis impuestos?', '¿Cuánto gana un diputado comparado conmigo?', 'Mi estado de cuenta ambiental'] });
    }
    if (/^\s*(que|q) (es|son|significa)\b/.test(p)) return null;
    var hit = null;
    HA.apps.forEach(function (a) { if (!hit && a._al.some(function (x) { return x.trim().split(' ').length > 1 && p.indexOf(x) >= 0; })) hit = a; });
    if (hit) return respApp(hit.id, hit.url, '<p><span aria-hidden="true">' + hit.ico + '</span> <b>' + esc(hit.n) + '</b> es la aplicación ' + hit.k + ' de ' + esc(hit.grupo) + '. ' + esc(hit.desc) + '</p><p>Úsala aquí abajo, sin salir del chat, o abre su página con «Saber más».</p>',
      { sug: hit.h.apps.filter(function (a) { return a !== hit; }).slice(0, 3).map(function (a) { return a.n; }) });
    var h = null;
    Object.keys(HA.de).forEach(function (k) { if (!h && p.indexOf(HA.de[k]._p) >= 0) h = HA.de[k]; });
    /* «La calculadora», a secas, es la Calculadora Cívica: no hay otra en la plataforma. */
    if (!h && CR.apps && /(^| )calculadora( |$)/.test(p)) h = CR;
    return h ? respHerr(h) : null;
  }
  /* La investigación de Auditoría en imágenes que viene al caso, al frente de
     «Explóralo a fondo» (las frases las escribe herramientas/auditorias.py). */
  INV.forEach(function (f) { f._k = (f.k || []).map(plano); });
  function invDe(q, r) {
    var p = plano(q + ' ' + ((r.ficha && r.ficha.tit) || r.tit || '')), hit = null, ir = r.ir || (r.ficha && r.ficha.ir);
    INV.forEach(function (f) { if (!hit && f._k.some(function (x) { return p.indexOf(x) >= 0; })) hit = f; });
    if (!hit || (ir && sinParam(ir[0]) === hit.ir[0])) return null;
    return { x: { ico: '📖', v: 'Ver la investigación', n: hit.tit, ir: hit.ir[0] } };
  }
  MO.obras.forEach(function (o) { OB[o.id] = o; o._al = o.al.map(function (x) { return plano(x); }); });
  /* Nombres que también son de un municipio o de otra cosa: piden contexto de obra. */
  var MO_DEBIL = { ' tula ': 1, ' olmeca ': 1, ' texcoco ': 1, ' santa lucia ': 1, ' bunker ': 1, ' naim ': 1, ' ipab ': 1 };
  var MO_CTX = /\b(obras?|megaobras?|aeropuerto|refineria|costo|costaron|cuesta|cuestan|sobrecostos?|pierde|pierden|perdio|perdida|gana|ganancia|cancelacion|construccion|inversion|invirti\w*|presupuesto|aprobado|asf|rescate|ambiental\w*|ambiente|huella|alerta|impacto|selva|manglar)\b/;
  var MO_EJ = {
    moinvestiga: 'Elige un presidente y una pregunta, y lee la respuesta con su documento.',
    motabla: 'Pregúntame «¿en qué obras invirtió Calderón?» o «compara las obras de Peña Nieto y AMLO».',
    mosector: 'Pregúntame por una obra: «¿cuánto costó el Tren Maya?», «sobrecosto de Dos Bocas».',
    mocero: 'Pregúntame «¿cuánto han costado las megaobras?» o «¿cuánto nos cuesta el FOBAPROA?».',
    mocuenta: 'Pregúntame «¿cuánto pierde el Tren Maya al año?» o «¿qué megaobra pierde más?».'
  };
  function obrasEn(t) {
    var p = plano(t), out = [], ctx = MO_CTX.test(p);
    MO.obras.forEach(function (o) {
      var pos = -1;
      o._al.forEach(function (a) { var i = p.indexOf(a); if (i >= 0 && (ctx || !MO_DEBIL[a]) && (pos < 0 || i < pos)) pos = i; });
      if (pos >= 0) out.push({ o: o, i: pos });
    });
    out.sort(function (a, b) { return a.i - b.i; });
    return out.map(function (x) { return x.o; });
  }
  function sxDe(o) { return MO.sx.filter(function (s) { return s.ids.indexOf(o.id) >= 0; })[0]; }
  function sxEn(t) {
    var p = plano(t), out = [], a = admDe(t);
    MO.sx.forEach(function (s) {
      var i = Math.max(p.indexOf(plano(s.n)), p.indexOf(plano(s.k.replace(/-/g, ' '))));
      if (a && a.id === s.adm && i < 0) i = 999;
      if (i >= 0) out.push({ s: s, i: i });
    });
    out.sort(function (x, y) { return x.i - y.i; });
    return out.map(function (x) { return x.s; });
  }
  function enteDe(id) {
    var f = null;
    B.fichas.forEach(function (x) { if (!f && x.t === 'ficha' && x.ir && /#ente=federal:/.test(x.ir[0]) && x.ir[0].split(':').pop() === id) f = x; });
    return f;
  }
  function expDe(o) {
    var f = null;
    B.fichas.forEach(function (x) {
      if (f || x.t !== 'expediente') return;
      var id = ' ' + x.ir[0].split('#exp-').pop().replace(/-/g, ' ') + ' ', t = plano(x.tit.split(':')[0]);
      if (o._al.some(function (a) { return !MO_DEBIL[a] && (id.indexOf(a) >= 0 || t.indexOf(a) >= 0); })) f = x;
    });
    return f;
  }
  function sinNA(t) { return String(t || '').replace(/^No aplica( como [^:.]*)?[:.]\s*/i, ''); }
  function chipE(c) { return chip({ e: c.e, p: c.p }); }
  function resTxt(r, corto) {
    if (r.tipo === 'dato') return (r.v > 0 ? '<b class="pa-verde">▲ Gana ' : r.v < 0 ? '<b class="pa-rojo">▼ Pierde ' : '<b>Sin ganancia ni pérdida ') + (r.v ? esc(r.vt) : '') + ' al año</b> ' +
      (corto ? '(' + r.anio + ')' : '(' + r.anio + ', ' + esc(r.base) + ')') + ' ' + chipE(r);
    if (r.tipo === 'no_aplica') return '● <b>No aplica</b>' + (corto ? '' : ': ' + esc(sinNA(r.txt)));
    return '● <b>Sin resultado publicado</b> ' + chipE({ e: 'pendiente', p: r.p }) + (corto ? '' : ' ' + esc(r.txt));
  }
  /* La salud financiera de la obra: su estado de resultados básico (pedido
     del autor, 24-10-2026), en verde lo que suma y en rojo lo que resta, con
     cada renglón en pesos de su año y en pesos de hoy (el INPC de la máquina
     del tiempo del peso). Lo que falta dice por qué. */
  function erHtml(o) {
    if (!o.er || !o.er.length) return '';
    var sig = function (v) { return v > 0 ? 'pa-verde' : v < 0 ? 'pa-rojo' : ''; };
    var nb = function (t) { return esc(t).replace(/ mdp$/, '&nbsp;mdp'); };
    var fila = function (x) {
      var celda, hoy = '';
      if (x.k === 'cob') celda = '<b>' + x.pct.toLocaleString('es-MX', { maximumFractionDigits: 1 }) + ' %</b> ' + chipE(x) + ' <small>(' + x.anio + ')</small>';
      else if (x.v != null) {
        celda = '<b class="pa-nw ' + sig(x.v) + '">' + (x.v > 0 ? '▲&nbsp;+' : x.v < 0 ? '▼&nbsp;−' : '') + nb(x.vt) + '</b> ' + chipE(x) + ' <small>(' + x.anio + ')</small>';
        if (x.hoyt) hoy = '<b class="pa-nw ' + sig(x.v) + '">' + (x.v > 0 ? '+' : x.v < 0 ? '−' : '') + nb(x.hoyt) + '</b>';
      } else celda = x.e === 'pendiente' ? chipE(x) + ' <small>' + esc(x.txt || '') + '</small>' : '<small>No aplica. ' + esc(sinNA(x.txt)) + '</small>';
      return '<tr' + (x.k === 'bruta' || x.k === 'neta' ? ' class="pa-er-tot"' : '') + '><th scope="row">' + esc(x.et) + '</th><td data-l="En pesos de su año">' + celda + '</td><td data-l="En pesos de ' + esc(MO.mes) + '">' + (hoy || '—') + '</td></tr>';
    };
    return '<p class="pa-er-t">📊 <b>Su salud financiera</b>: el estado de resultados básico de la obra.</p>' +
      '<div class="pa-tabla pa-tabla-ajusta pa-er"><table><thead><tr><th scope="col">Renglón</th><th scope="col">En pesos de su año</th><th scope="col">En pesos de ' + esc(MO.mes) + ' ' + chip({ e: 'derivado' }) + '</th></tr></thead><tbody>' +
      o.er.map(fila).join('') +
      '<tr><th scope="row">' + (o.resc ? 'Pagado y debido' : 'Inversión: lo que costó construirla') + '</th><td data-l="En pesos de su año"><b>' + esc(o.c.real.vt) + '</b> ' + chipE(o.c.real) + '</td><td data-l="En pesos de ' + esc(MO.mes) + '">' +
      (o.chy ? '<b>' + esc(o.chy.vt) + '</b>' : '<small>Suma pagos de varios años: no se ajusta como un solo monto.</small>') + '</td></tr>' +
      '</tbody></table></div><p class="pa-chico">▲ verde suma, ▼ rojo resta. Cada renglón trae su año: no todos son del mismo. La ganancia bruta solo se calcula si ingresos y gasto son del mismo año, y el resultado neto es el que publica la obra (o el de la medida de la herramienta), no una resta nuestra. ' +
      'A pesos de hoy se lleva con el INPC, igual que en <a href="' + esc(MO.maquina) + '">la máquina del tiempo del peso</a>.</p>';
  }
  function moFuentes(o) {
    var c = o.c, l = [
      { que: (o.resc ? 'Presentado en su momento' : 'Aprobado') + ': ' + c.pres.vt, e: c.pres.e, p: c.pres.p, op: c.pres.op || c.pres.d },
      { que: (o.resc ? 'Pagado y debido' : 'Costo real') + ': ' + c.real.vt, e: c.real.e, p: c.real.p, op: c.real.op || c.real.d },
      { que: c.sob.et + ': ' + c.sob.vt, e: c.sob.e, p: c.sob.p, op: c.sob.op || c.sob.d }];
    if (o.res.tipo === 'dato') l.push({ que: 'Lo que ' + (o.res.v < 0 ? 'pierde' : 'gana') + ' al año (' + o.res.anio + ')', e: o.res.e, op: o.res.op, fu: o.res.fu[0] });
    (o.er || []).forEach(function (x) {
      if (x.v != null || x.pct != null) l.push({ que: x.et + ' (' + x.anio + ')', e: x.e, op: x.op, fu: (x.fu || [])[0] });
      if (x.hoyt) l.push({ que: x.et + ' en pesos de ' + MO.mes, e: 'derivado', op: x.hop, fu: PESO_FU });
    });
    if (o.chy) l.push({ que: 'Costo real en pesos de ' + MO.mes, e: 'derivado', op: o.chy.op, fu: PESO_FU });
    o.fu.forEach(function (f) { l.push({ que: 'Documento de la obra', e: 'oficial', fu: f }); });
    return l;
  }
  function moFicha(tit, h, ci, fus, ir) {
    var vistos = {}, fu = [];
    fus.forEach(function (f) { if (f && f.tx && !vistos[f.tx]) { vistos[f.tx] = 1; fu.push(f); } });
    return { t: 'calculo', tit: tit, txt: texto(h), ci: ci, fu: fu, ir: ir };
  }
  function moRec(o) {
    var s = sxDe(o), out = [], ex = expDe(o), en = o.ente && enteDe(o.ente);
    if (o.amb) out.push({ x: { ico: '🗺️', v: 'Ver en el mapa ambiental', n: 'Inversión y alerta ambiental en ' + o.amb.sede, ir: o.amb.mapa } });
    if (o.ir && o.ir.auditoria) out.push({ x: { ico: '🖼️', v: 'Ver investigación', n: 'Auditoría en imágenes de ' + o.n, ir: o.ir.auditoria } });
    out.push({ x: { ico: '🏭', v: 'Ver su ficha', n: 'Obra por obra, por industria', ir: o.ir.ficha } });
    out.push({ x: { ico: '⏱️', v: 'Ver simulador', n: 'Simulación en vivo de su industria y su sexenio', ir: o.sim } });
    out.push({ x: { ico: '📒', v: 'Ver su cuenta', n: 'Su estado de resultados completo', ir: o.ir.cuenta } });
    if (s && s.adm) out.push({ x: { ico: '🧾', v: 'Ver estado de cuenta', n: 'De ' + s.nom, ir: MO.expide + '?adm=' + s.adm } });
    if (en) out.push({ x: { ico: '🏢', v: 'Ver salud financiera', n: en.tit.split(' (')[0], ir: en.ir[0] } });
    if (ex) out.push({ x: { ico: '📂', v: 'Ver expediente', n: 'Su caso en la ASF', ir: ex.ir[0] } });
    out.push({ x: { ico: '💱', v: 'Usar la máquina del tiempo', n: 'Lleva cualquier cifra a pesos de hoy', ir: MO.maquina } });
    return out;
  }
  function portalesHtml(fu) {
    var l = (fu && fu.length ? fu : MO.portales).slice(0, 3);
    return l.length ? '<p class="pa-chico">🌐 Síguela en los portales oficiales: ' + l.map(function (f) {
      return '<a href="' + esc(f.url) + '" target="_blank" rel="noopener noreferrer">' + esc(f.tx.length > 70 ? f.tx.slice(0, 68).replace(/[\s,;:]+\S*$/, '') + '…' : f.tx) + ' ↗</a>';
    }).join(' · ') + '</p>' : '';
  }
  var MO_SIM = /\b(simulador\w*|simula\w*|en vivo|ritmo|contador|mientras miro|por segundo)\b/;
  var MO_FOCO = [
    ['amb', /\b(ambiental\w*|ambiente|ecologic\w*|ecosistema\w*|selva\w*|manglar\w*|cenote\w*|huella|deforest\w*|manifestacion|mia|semarnat|asea|profepa|alerta\w*|impacto|contaminacion|en que estados?|donde esta|ubicacion)\b/],
    ['salud', /\b(salud financiera|estado de resultados|finanzas|rentab\w*|ganancia bruta|ganancia neta|utilidad\w*|numeros de la obra)\b/],
    ['sob', /\b(sobrecostos?|de mas|se paso|se excedio|desfase|encarecio|cuanto mas)\b/],
    ['res', /\b(pierde|pierden|perdio|perdida|perdidas|gana|ganan|gano|ganancia|deficit|rentable|negocio|subsidio|al ano|cada ano|nos cuesta|sigue costando)\b/],
    ['asf', /\b(asf|auditoria|auditorias|auditor|irregularidad\w*|aclarar|hallazgos?|observaciones)\b/],
    ['pres', /\b(aprob\w*|presupuest\w*|prometi\w*|original|planead\w*|iba a costar)\b/],
    ['real', /\b(costo|costaron|cuesta|cuestan|cuanto se gasto|gastaron|pagaron|valio|cuanto salio)\b/]
  ];
  function focoDe(p) { var f = null; MO_FOCO.forEach(function (x) { if (!f && x[1].test(p)) f = x[0]; }); return f; }
  function netaHoy(o) { var x = (o.er || []).filter(function (y) { return y.k === 'neta'; })[0]; return x && x.hoyt; }
  function respObra(o, foco, sim) {
    var c = o.c, s = sxDe(o), lead = '';
    var nomP = o.resc ? 'Presentado en su momento' : 'Aprobado', nomR = o.resc ? 'Pagado y debido' : 'Costo real';
    if (foco === 'amb' && o.amb) lead = '📍 Se ubica en <b>' + esc(o.amb.sede) + '</b>. Costó <b>' + esc(c.real.vt) + '</b> ' + chipE(c.real) +
      '. <br>🚨 <b>Alerta del Auditor Ambiental (' + esc(o.amb.eco) + '):</b> ' + esc(o.amb.alerta) +
      ' Permiso ambiental (MIA): ' + chip({ e: o.amb.miaEst, p: o.amb.miaPend }) + ' (' + esc(o.amb.miaTxt) + ').';
    else if (foco === 'sob') lead = o.resc ? 'Es un rescate, no una obra: su «sobrecosto» es lo que creció la deuda frente a lo que se presentó, <b>' + esc(c.sob.vt) + '</b> ' + chipE(c.sob) + '.' :
      'Su sobrecosto es de <b>' + esc(c.sob.vt) + '</b> ' + chipE(c.sob) + ': se aprobaron ' + esc(c.pres.vt) + ' y costó ' + esc(c.real.vt) + '.';
    else if (foco === 'res') lead = o.res.tipo === 'dato' ? 'Al año, ' + (o.res.v < 0 ? '<b class="pa-rojo">pierde ' : '<b class="pa-verde">gana ') + esc(o.res.vt) + '</b> por sí misma (' + o.res.anio + ', ' + esc(o.res.base) + ') ' + chipE(o.res) + '.' +
      (netaHoy(o) ? ' En pesos de ' + esc(MO.mes) + ' son ' + esc(netaHoy(o)) + ' ' + chip({ e: 'derivado' }) + '.' : '') :
      o.res.tipo === 'no_aplica' ? 'No opera, así que no tiene ganancia ni pérdida del año: ' + esc(o.res.txt) : 'No publica lo que gana o pierde al año ' + chipE({ e: 'pendiente', p: o.res.p }) + ': ' + esc(o.res.txt);
    else if (foco === 'pres') lead = (o.resc ? 'Se presentó en su momento con ' : 'Se aprobó con ') + '<b>' + esc(c.pres.vt) + '</b> ' + chipE(c.pres) + '.';
    else if (foco === 'salud') lead = 'Su salud financiera, en su estado de resultados básico: lo que ingresa, lo que gasta en operar, lo que paga de intereses y su resultado del año.' +
      (o.res.tipo === 'dato' ? ' Cierra con ' + (o.res.v < 0 ? '<b class="pa-rojo">▼ pérdida de ' : '<b class="pa-verde">▲ ganancia de ') + esc(o.res.vt) + '</b> (' + o.res.anio + ').' : '');
    else if (foco === 'asf') lead = o.asf ? '<b>Lo que dijo la ASF:</b> ' + esc(o.asf) : 'La plataforma todavía no integra un documento de la ASF sobre esta obra ' + chip({ e: 'pendiente', p: 'obra-' + o.id }) + '.';
    else lead = (o.resc ? 'Lo pagado y lo que se sigue debiendo suma ' : 'Costó ') + '<b>' + esc(c.real.vt) + '</b> ' + chipE(c.real) + (o.resc ? '' : ', contra lo aprobado: ' + esc(c.pres.vt)) + '.';
    var h = '<p><span aria-hidden="true">' + o.ico + '</span> <b>' + esc(o.n) + '</b> · ' + esc(o.pres) + ' (' + esc(o.per) + ')' + (o.resc ? ' · <b>rescate: deuda, no obra</b>' : '') + '</p>' +
      '<p>' + lead + '</p><ul class="pa-lista">' +
      (o.amb ? '<li>📍 Dónde está: <b>' + esc(o.amb.sede) + '</b> · <a href="' + esc(o.amb.mapa) + '">Ver en el mapa ambiental ➔</a></li>' : '') +
      '<li>' + nomP + ': <b>' + esc(c.pres.vt) + '</b> ' + chipE(c.pres) + '</li>' +
      '<li>' + nomR + ': <b>' + esc(c.real.vt) + '</b> ' + chipE(c.real) + '</li>' +
      '<li>' + esc(c.sob.et) + ': <b>' + esc(c.sob.vt) + '</b> ' + chipE(c.sob) + '</li>' +
      '<li>' + resTxt(o.res) + '</li>' +
      (o.amb && foco !== 'amb' ? '<li>🚨 <b>Alerta ambiental:</b> ' + esc(o.amb.eco) + ' · Permiso MIA: ' + chip({ e: o.amb.miaEst, p: o.amb.miaPend }) + '</li>' : '') +
      '</ul>' + erHtml(o) +
      (o.asf && foco !== 'asf' ? '<p>🔍 <b>Lo que dijo la ASF:</b> ' + esc(o.asf) + '</p>' : '') +
      '<p class="pa-chico">' + o.sico + ' ' + esc(o.sec) + ' · Estatus: ' + esc(o.est) + '. «Gana o pierde» no descuenta lo que costó construirla.</p>' +
      portalesHtml(o.fu) + (charla && charla.deDonde ? charla.deDonde(moFuentes(o)) : '');
    var ci = [{ v: c.pres.vt, etq: nomP, e: c.pres.e }, { v: c.real.vt, etq: nomR, e: c.real.e }, { v: c.sob.vt, etq: c.sob.et, e: c.sob.e }];
    if (o.res.tipo === 'dato') ci.push({ v: (o.res.v < 0 ? '−' : '+') + o.res.vt, etq: 'Gana o pierde al año (' + o.res.anio + ')', e: o.res.e });
    var otras = MO.obras.filter(function (x) { return x !== o && !x.resc === !o.resc; });
    var irDest = foco === 'amb' && o.amb ? [o.amb.mapa, 'el mapa ambiental de megaobras en ' + o.amb.sede] : [o.ir.ficha, 'su ficha en Inversión y Megaobras'];
    return {
      html: h, ir: irDest, app: sim ? { id: 'mosector', url: o.sim, abre: true } : foco === 'salud' ? { id: 'mocuenta', url: o.ir.cuenta } : { id: 'mosector', url: o.ir.ficha }, rec: moRec(o),
      ficha: moFicha(o.n + ': lo que costó y lo que deja', h, ci, o.fu.concat(o.res.fu || []), irDest),
      sug: [foco !== 'amb' && o.amb ? '¿Cuál es el impacto ambiental de ' + o.n.split(' (')[0] + '?' : '¿Y su sobrecosto?', s && s.ids.length > 1 ? 'Obras de ' + s.n : '¿Qué megaobra tiene más sobrecosto?',
        otras.length ? 'Compara ' + o.n.split(' (')[0] + ' con ' + otras[0].n : 'Mapa ambiental de megaobras por estado']
    };
  }
  function respDuelo(a, b) {
    var fila = function (et, fa, fb) { return '<tr><th scope="row">' + et + '</th><td>' + fa + '</td><td>' + fb + '</td></tr>'; };
    var v = function (x) { return '<b>' + esc(x.vt) + '</b> ' + chipE(x); };
    var h = '<p>⚖️ <b>' + esc(a.n) + '</b> frente a <b>' + esc(b.n) + '</b>, con las mismas cifras de Inversión y Megaobras:</p>' +
      '<div class="pa-tabla pa-tabla-ajusta"><table><thead><tr><th></th><th scope="col">' + a.ico + ' ' + esc(a.n) + '</th><th scope="col">' + b.ico + ' ' + esc(b.n) + '</th></tr></thead><tbody>' +
      fila('Presidente', esc(a.pres) + ' (' + esc(a.per) + ')', esc(b.pres) + ' (' + esc(b.per) + ')') +
      fila('Aprobado', v(a.c.pres), v(b.c.pres)) + fila('Costo real', v(a.c.real), v(b.c.real)) +
      fila('Sobrecosto', v(a.c.sob), v(b.c.sob)) + fila('Al año', resTxt(a.res, 1), resTxt(b.res, 1)) +
      '</tbody></table></div>' +
      (a.resc || b.resc ? '<p class="pa-chico">Ojo: un rescate es una deuda que el Estado asumió, no una obra; su crecimiento no se compara con un sobrecosto.</p>' : '') +
      '<p class="pa-chico">Los años del resultado no son iguales para todas y las cifras son nominales, sin deflactar.</p>' +
      (charla && charla.deDonde ? charla.deDonde(moFuentes(a).concat(moFuentes(b))) : '');
    var ci = [];
    [a, b].forEach(function (o) { ci.push({ v: o.c.real.vt, etq: o.n + ': costo real', e: o.c.real.e }, { v: o.c.sob.vt, etq: o.n + ': ' + o.c.sob.et.toLowerCase(), e: o.c.sob.e }); });
    return {
      html: h, ir: [MO.apps[2] ? MO.apps[2].url : a.ir.ficha, 'Obra por obra, por industria'], app: { id: 'mosector', url: a.ir.ficha }, rec: moRec(a).slice(0, 2).concat(moRec(b).slice(0, 2)),
      ficha: moFicha(a.n + ' frente a ' + b.n, h, ci, a.fu.concat(b.fu), [a.ir.ficha, 'Inversión y Megaobras']),
      sug: ['¿Qué megaobra tiene más sobrecosto?', '¿Qué megaobra pierde más?', 'Obras de ' + (sxDe(a) || { n: 'AMLO' }).n]
    };
  }
  function respSx(s) {
    var ob = s.ids.map(function (id) { return OB[id]; }).filter(Boolean), h;
    if (!ob.length) h = '<p>🏛️ Con <b>' + esc(s.nom) + '</b> (' + s.a0 + '–' + s.a1 + '), Inversión y Megaobras no tiene obras evaluadas. Las concesiones carreteras que fracasaron se otorgaron con él, pero se rescataron y se pagaron desde 1997: ese rescate (el FARAC) se cuenta con Ernesto Zedillo, que lo hizo.</p>';
    else h = '<p>🏛️ Con <b>' + esc(s.nom) + '</b> (' + s.a0 + '–' + s.a1 + '), Inversión y Megaobras sigue <b>' + ob.length + (ob.length === 1 ? ' obra' : ' obras') + '</b>' +
      (s.resc ? ' (' + s.resc + (s.resc === 1 ? ' es un rescate' : ' son rescates') + ')' : '') + ':</p><ul class="pa-lista">' +
      ob.map(function (o) { return '<li><span aria-hidden="true">' + o.ico + '</span> <b>' + esc(o.n) + '</b>: costó ' + esc(o.c.real.vt) + ' ' + chipE(o.c.real) + ' · ' + resTxt(o.res, 1) + '</li>'; }).join('') + '</ul>' +
      '<p>Costo registrado de sus obras: <b>' + esc(s.costot) + '</b> ' + chip({ e: 'derivado' }) + (s.resc ? ', con sus rescates, solo como referencia' : '') + '.' +
      (s.nres ? ' Al año, las ' + s.nres + ' que publican su resultado ' + (s.res < 0 ? '<b>pierden ' : '<b>ganan ') + esc(s.rest) + '</b> ' + chip({ e: 'derivado' }) + '.' : ' Ninguna publica su resultado del año.') + '</p>' +
      '<p class="pa-chico">Cómo se calcula: costo del sexenio = suma del costo registrado de sus obras (donde hay rango, su punto medio); al año = suma de los resultados publicados. Cada obra, en el sexenio en que se contrató.</p>';
    var fus = [];
    ob.forEach(function (o) { fus = fus.concat(o.fu); });
    if (charla && charla.deDonde && ob.length) h += charla.deDonde([{ que: 'Costo registrado de las obras de ' + s.n, e: 'derivado', op: 'suma del costo registrado de ' + ob.map(function (o) { return o.n; }).join(', ') }]
      .concat(ob.map(function (o) { return { que: o.n + ': costo real', e: o.c.real.e, p: o.c.real.p, op: o.c.real.op || o.c.real.d, fu: o.fu[0] }; })));
    var rec = [{ x: { ico: '🏛️', v: 'Ver sus obras', n: 'En qué invirtió cada presidente', ir: s.ir } }];
    if (ob.length) rec.push({ x: { ico: '⏱️', v: 'Ver simulador', n: 'Sus obras en vivo, filtradas por su sexenio', ir: s.sim } });
    if (s.adm) rec.push({ x: { ico: '🧾', v: 'Ver estado de cuenta', n: 'De ' + s.nom, ir: MO.expide + '?adm=' + s.adm } });
    rec.push({ x: { ico: '🕰️', v: 'Ver línea del tiempo', n: 'Las megaobras de 1988 a 2024', ir: APP.motabla.url + '#mxLinea' } });
    var otro = MO.sx.filter(function (x) { return x !== s && x.ids.length; }).slice(-1)[0];
    return {
      html: h, ir: [s.ir, 'En qué invirtió cada presidente'], app: { id: 'motabla', url: s.ir }, rec: rec,
      ficha: ob.length ? moFicha('Las megaobras de ' + s.nom, h, ob.map(function (o) { return { v: o.c.real.vt, etq: o.n + ': costo real', e: o.c.real.e }; }).concat([{ v: s.costot, etq: 'Costo registrado del sexenio', e: 'derivado' }]), fus, [s.ir, 'Inversión y Megaobras']) : null,
      sug: [ob.length ? '¿Cuánto costó ' + ob[0].n.split(' (')[0] + '?' : '¿En qué obras invirtió Zedillo?', otro && otro !== s ? 'Compara las obras de ' + s.n + ' y ' + otro.n : '¿Qué megaobra tiene más sobrecosto?', 'Estado de cuenta de ' + s.nom]
    };
  }
  function respSxDuelo(a, b) {
    var ra = respSx(a), rb = respSx(b), url = APP.motabla.url + '#comparar-' + a.k + '-' + b.k;
    var lin = function (s) {
      var ob = s.ids.map(function (id) { return OB[id]; }).filter(Boolean);
      return '<li><b>' + esc(s.nom) + '</b> (' + s.a0 + '–' + s.a1 + '): ' + ob.length + (ob.length === 1 ? ' obra' : ' obras') +
        (ob.length ? ' (' + ob.map(function (o) { return esc(o.n); }).join(', ') + '), costo registrado ' + esc(s.costot) + ' ' + chip({ e: 'derivado' }) +
          (s.nres ? '; al año ' + (s.res < 0 ? 'pierden ' : 'ganan ') + esc(s.rest) + ' (' + s.nres + ' con dato)' : '; ninguna publica su resultado') : '') + '.</li>';
    };
    var h = '<p>⚖️ Las megaobras de dos sexenios, frente a frente:</p><ul class="pa-lista">' + lin(a) + lin(b) + '</ul>' +
      '<p class="pa-chico">Los costos son nominales, de años distintos: compáralos con cuidado. Aquí abajo ves los dos sexenios lado a lado.</p>';
    return {
      html: h, ir: [url, 'Dos sexenios frente a frente'], app: { id: 'motabla', url: url, abre: true }, rec: (ra.rec || []).slice(0, 1).concat((rb.rec || []).slice(0, 1)),
      ficha: ra.ficha && rb.ficha ? moFicha('Las megaobras de ' + a.n + ' y de ' + b.n, h, (ra.ficha.ci || []).concat(rb.ficha.ci || []), ra.ficha.fu.concat(rb.ficha.fu), [url, 'Inversión y Megaobras']) : (ra.ficha || rb.ficha),
      sug: ['Obras de ' + a.n, 'Obras de ' + b.n, '¿Qué megaobra pierde más?']
    };
  }
  function respTodosSx() {
    var h = '<p>🏛️ <b>En qué invirtió cada presidente</b>, de 1988 a 2024, según Inversión y Megaobras:</p><div class="pa-tabla pa-tabla-ajusta"><table><thead><tr>' +
      '<th scope="col">Sexenio</th><th scope="col">Obras</th><th scope="col">Costo registrado ' + chip({ e: 'derivado' }) + '</th><th scope="col">Al año ' + chip({ e: 'derivado' }) + '</th></tr></thead><tbody>' +
      MO.sx.map(function (s) {
        return '<tr><th scope="row">' + esc(s.n) + ' <small>' + s.a0 + '–' + s.a1 + '</small></th><td>' + s.ids.length + '</td><td>' + (s.ids.length ? esc(s.costot) : '—') + '</td><td>' +
          (s.nres ? (s.res < 0 ? '▼ pierden ' : '▲ ganan ') + esc(s.rest) : s.ids.length ? 'sin dato' : '—') + '</td></tr>';
      }).join('') + '</tbody></table></div>' +
      '<p class="pa-chico">Cada obra cuenta en el sexenio en que se contrató; los rescates (FOBAPROA y FARAC) van con Zedillo y su costo se suma solo como referencia. «Al año» suma solo las obras que publican su resultado.</p>';
    return { html: h, ir: [APP.motabla.url, 'En qué invirtió cada presidente'], app: { id: 'motabla', url: APP.motabla.url }, rec: [
      { x: { ico: '🕰️', v: 'Ver línea del tiempo', n: 'Las megaobras de 1988 a 2024', ir: APP.motabla.url + '#mxLinea' } },
      { x: { ico: '⚖️', v: 'Comparar', n: 'Dos sexenios frente a frente', ir: APP.motabla.url + '#mxComparar' } }],
      ficha: moFicha('En qué invirtió cada presidente', h, MO.sx.filter(function (s) { return s.ids.length; }).map(function (s) { return { v: s.costot, etq: s.nom + ': costo registrado', e: 'derivado' }; }), MO.portales, [APP.motabla.url, 'Inversión y Megaobras']),
      sug: ['¿En qué obras invirtió AMLO?', 'Compara las obras de Calderón y Peña Nieto', '¿Qué megaobra pierde más?'] };
  }
  function respRank(cual, asc) {
    var l, et, val, nota = '';
    if (cual === 'sob' || cual === 'real') {
      l = MO.obras.filter(function (o) { return !o.resc; });
      val = function (o) { return o.c[cual].v; };
      et = cual === 'sob' ? 'sobrecosto' : 'costo real';
      nota = 'Sin los dos rescates (FOBAPROA y FARAC), que son deudas y no obras.';
    } else {
      l = MO.obras.filter(function (o) { return o.res.tipo === 'dato' && (cual === 'pierde' ? o.res.v < 0 : o.res.v > 0); });
      val = function (o) { return Math.abs(o.res.v); };
      et = cual === 'pierde' ? 'lo que pierde al año' : 'lo que gana al año';
      nota = 'Solo las ' + MO.tot.ndato + ' que publican su resultado; ' + MO.tot.npend + ' no lo publican y ' + MO.tot.nna + ' no operan. Los años no son iguales para todas.';
    }
    l = l.slice().sort(function (a, b) { return asc ? val(a) - val(b) : val(b) - val(a); });
    if (!l.length) return null;
    var top = l[0], dato = function (o) { return cual === 'sob' || cual === 'real' ? '<b>' + esc(o.c[cual].vt) + '</b> ' + chipE(o.c[cual]) : resTxt(o.res, 1); };
    var verbo = cual === 'sob' ? 'sobrecosto tiene' : cual === 'real' ? 'costó' : cual === 'pierde' ? 'pierde al año' : 'gana al año';
    var h = '<p>' + (cual === 'gana' ? '▲' : '📈') + ' ' + (l.length === 1 ? 'Solo una ' + verbo.replace('sobrecosto tiene', 'tiene sobrecosto') + ': ' : 'La que ' + (asc ? 'menos' : 'más') + ' ' + verbo + ' es ') +
      '<b>' + esc(top.n) + '</b> (' + esc(top.pres) + '): ' + dato(top) + '.</p><ol class="pa-lista">' +
      l.slice(0, 6).map(function (o) { return '<li><span aria-hidden="true">' + o.ico + '</span> <b>' + esc(o.n) + '</b>' + (o.resc ? ' <span class="pa-chico">(rescate)</span>' : '') + ': ' + dato(o) + '</li>'; }).join('') + '</ol>' +
      '<p class="pa-chico">Ordenadas por ' + et + '. ' + nota + '</p>' +
      (charla && charla.deDonde ? charla.deDonde(l.slice(0, 6).map(function (o) {
        var c = cual === 'sob' || cual === 'real' ? o.c[cual] : o.res;
        return { que: o.n + ': ' + et, e: c.e, p: c.p, op: c.op || c.d, fu: (c.fu && c.fu[0]) || o.fu[0] };
      })) : '');
    var app = cual === 'pierde' || cual === 'gana' ? 'mocuenta' : 'mosector';
    return {
      html: h, ir: [APP[app].url, APP[app].n], app: { id: app, url: APP[app].url },
      rec: [{ x: { ico: '📊', v: 'Ver simulador', n: 'La comparativa, ordenada así', ir: MO.sims.orden.replace('%s', { sob: 'sobrecosto', real: 'inversion', pierde: 'perdida', gana: 'perdida' }[cual]) } }].concat(moRec(top).slice(0, 1)),
      ficha: moFicha('Megaobras ordenadas por ' + et, h, l.slice(0, 6).map(function (o) { return { v: cual === 'sob' || cual === 'real' ? o.c[cual].vt : o.res.vt, etq: o.n + ': ' + et, e: (cual === 'sob' || cual === 'real' ? o.c[cual] : o.res).e }; }),
        [].concat.apply([], l.slice(0, 6).map(function (o) { return o.fu.slice(0, 1); })), [APP[app].url, 'Inversión y Megaobras']),
      sug: ['¿Cuánto costó ' + top.n.split(' (')[0] + '?', cual !== 'pierde' ? '¿Qué megaobra pierde más?' : '¿Qué megaobra tiene más sobrecosto?', '¿En qué invirtió cada presidente?']
    };
  }
  function respMoTodo(lista) {
    var T = MO.tot;
    var h = '<p>🏗️ <b>' + esc(MO.nombre) + '</b> sigue ' + T.n + ' megaobras y ' + T.nresc + ' rescates, de 1988 a 2024. Sus cuatro cifras:</p><ul class="pa-lista">' +
      '<li>Costo real de las ' + T.n + ' obras: <b>' + esc(T.realt) + '</b> ' + chip({ e: 'derivado' }) + ', contra ' + esc(T.presut) + ' aprobados.</li>' +
      '<li>Pagado de más sobre lo aprobado: <b>' + esc(T.brechat) + '</b> ' + chip({ e: 'derivado' }) + '.</li>' +
      '<li>Lo que pierden al año las que publican su resultado: <b>' + (T.neto < 0 ? '−' : '+') + esc(T.netot) + '</b> ' + chip({ e: 'derivado' }) + ' (' + T.npierde + ' pierden ' + esc(T.pierdet) + ' y ' + T.ngana + ' gana ' + esc(T.ganat) + ').</li>' +
      '<li>Sin resultado publicado: ' + T.npend + ' ' + chip({ e: 'pendiente', p: 'tema-megaobras' }) + '. No operan: ' + T.nna + '.</li></ul>' +
      '<p class="pa-chico">' + esc(T.medida) + '</p>' +
      (lista ? '<p>Y sus cinco aplicaciones las usas desde aquí:</p><ul class="pa-lista">' + MO.apps.map(function (a) {
        return '<li><span aria-hidden="true">' + a.ico + '</span> <b>' + esc(a.n) + '.</b> ' + esc(a.frase) + '. <span class="pa-chico">' + esc(MO_EJ[a.id] || '') + '</span></li>';
      }).join('') + '</ul>' : '') + portalesHtml() +
      (charla && charla.deDonde ? charla.deDonde([
        { que: 'Costo real de las ' + T.n + ' obras', e: 'derivado', op: 'suma del costo registrado de cada obra, sin los rescates' },
        { que: 'Pagado de más', e: 'derivado', op: 'costo real − lo aprobado (' + T.realt + ' − ' + T.presut + ')' },
        { que: 'Lo que pierden al año', e: 'derivado', op: 'suma del resultado del año más reciente de cada obra que lo publica (' + T.anios.join(', ') + ')' }].concat(MO.portales.map(function (f) { return { que: 'Portal oficial', e: 'oficial', fu: f }; }))) : '');
    return {
      html: h, ir: [MO.pagina, MO.nombre], app: { id: 'mocero', url: APP.mocero.url }, rec: [
        { x: { ico: '⏱️', v: 'Ver simulador', n: 'Simulación en vivo, obra por obra', ir: MO.sims.vivo } },
        { x: { ico: '📆', v: 'Ver simulador', n: 'El ritmo de la pérdida: por día, mes o año', ir: MO.sims.ritmo } },
        { x: { ico: '👛', v: 'Ver simulador', n: 'De la cifra agregada a tu bolsillo', ir: MO.sims.bolsillo } },
        { x: { ico: '🚦', v: 'Ver contador', n: 'Lo que gana o pierde cada obra, en vivo', ir: APP.motabla.url } },
        { x: { ico: '💱', v: 'Usar la máquina del tiempo', n: 'Lleva cualquier cifra a pesos de hoy', ir: MO.maquina } }],
      ficha: moFicha('Las cuatro cifras de las megaobras', h, [{ v: T.realt, etq: 'Costo real de las obras', e: 'derivado' }, { v: T.brechat, etq: 'Pagado de más', e: 'derivado' },
        { v: (T.neto < 0 ? '−' : '+') + T.netot, etq: 'Ganancia o pérdida del año', e: 'derivado' }], MO.portales, [MO.pagina, MO.nombre]),
      sug: ['¿En qué invirtió cada presidente?', '¿Qué megaobra tiene más sobrecosto?', '¿Cuánto costó el Tren Maya?']
    };
  }
  function respMapaAmb(q, p) {
    var casos = MO.casosAmb || [], edosAmb = MO.edosAmb || [];
    if (!casos.length) return null;
    var ab = entidadDe(q);
    var pideAmb = /\b(ambiental\w*|ambiente|ecologic\w*|ecosistema\w*|selva\w*|manglar\w*|cenote\w*|huella|deforest\w*|manifestacion|mia|semarnat|asea|profepa|alerta\w*|impacto|contaminacion)\b/.test(p);
    var pideObra = /\b(megaobras?|obras?|infraestructura|refineria\w*|tren\w*|aeropuerto\w*|acueducto\w*|presa\w*|gas|gnl)\b/.test(p);
    var pideMapa = /\b(mapa|estados|entidades|donde estan|en que estados)\b/.test(p);
    if (!ab && !((pideAmb && (pideObra || pideMapa)) || (pideMapa && pideObra))) return null;
    if (ab && !pideObra && !(pideAmb && pideMapa)) return null;

    var fmtMdp = function (v) { return '$' + Number(v || 0).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp'; };
    if (ab) {
      var ed = edosAmb.filter(function (x) { return x.a === ab; })[0];
      if (!ed) return null;
      var os = casos.filter(function (c) { return (c.edos || []).indexOf(ab) >= 0; });
      var urlEdo = 'datos-ambiente-megaobras.html?e=' + encodeURIComponent(ab) + '#abMapaObras';
      var h = '<p>🗺️ <b>' + esc(ed.n) + ' (' + esc(ed.a) + ')</b> en el <b>Mapa ambiental de megaobras e infraestructura</b>:</p>' +
        '<ul class="pa-lista">' +
        '<li>🏛️ <b>Gasto federalizado 2026 (Ramos 28 y 33):</b> <b>' + fmtMdp(ed.gasto) + '</b> ' + chip({ e: 'derivado' }) + ' (Ramo 28: ' + fmtMdp(ed.r28) + ' · Ramo 33: ' + fmtMdp(ed.r33) + ').</li>' +
        '<li>🔍 <b>Por aclarar ante la ASF en el estado (CP 2024):</b> <b>' + fmtMdp(ed.asf) + '</b> ' + chip({ e: 'oficial' }) + ' en ' + ed.aud + ' auditorías.</li>' +
        '</ul>';
      if (os.length) {
        h += '<p>🚨 <b>' + os.length + (os.length === 1 ? ' megaobra o caso con alerta ambiental' : ' megaobras y casos con alerta ambiental') + ' en ' + esc(ed.n) + ':</b></p><ul class="pa-lista">' +
          os.map(function (c) {
            var costo = c.paga === 'privado' ? ' · 🏢 <b>Inversión privada</b>: no es gasto público ' + chip({ e: c.estReal, p: c.pendReal }) : c.realMdp != null ? ' · 🏛️ Gasto público registrado: <b>' + fmtMdp(c.realMdp) + '</b> ' + chip({ e: c.estReal, p: c.pendReal }) + (c.multi ? ' <i>(total nacional en ' + c.edos.join(', ') + ')</i>' : '') : '';
            return '<li><span aria-hidden="true">' + esc(c.ico) + '</span> <b>' + esc(c.nombre) + '</b> (' + esc(c.sede) + ')' + costo + '.<br>' +
              '🌱 <b>Alerta ambiental (' + esc(c.ecosistema) + '):</b> ' + esc(c.alerta) + ' · Permiso: ' + chip({ e: c.miaEst, p: c.miaPend }) + ' <a href="' + esc(c.aud) + '">Ver su Auditoría en imágenes ➔</a></li>';
          }).join('') + '</ul>';
      } else {
        h += '<p>En el padrón actual de 14 megaobras federales y casos ambientales críticos no hay una megaobra ubicada en <b>' + esc(ed.n) + '</b> (se concentran en 15 entidades). En el mapa puedes revisar su gasto federalizado, su deuda estatal (' + fmtMdp(ed.deuda) + ', semáforo ' + esc(ed.sem) + ') y sus auditorías de la ASF.</p>';
      }
      var recs = [
        { x: { ico: '🗺️', v: 'Abrir el mapa ambiental', n: 'Con ' + ed.n + ' seleccionado en La huella de las megaobras', ir: urlEdo } },
        { x: { ico: '🏛️', v: 'Ver mapa del gasto federalizado', n: 'Ramos 28 y 33 en ' + ed.n, ir: 'numeros-mapa-del-gasto-federalizado.html?e=' + encodeURIComponent(ab) } },
        { x: { ico: '🧾', v: 'Ver estado de cuenta', n: 'De ' + ed.n, ir: 'herramienta-inspector-entes.html#ente=estatal:' + encodeURIComponent(ab) } },
        { x: { ico: '🌱', v: 'Auditar sector ambiental', n: 'SEMARNAT, Conagua y PROFEPA', ir: 'herramienta-ambiente-auditor.html' } }
      ];
      if (os.length && os[0].aud) recs.unshift({ x: { ico: '🖼️', v: 'Ver investigación', n: os[0].nombre, ir: os[0].aud } });
      return {
        html: h, ir: [urlEdo, 'el mapa ambiental de megaobras en ' + ed.n], rec: recs,
        ficha: moFicha('Mapa ambiental y megaobras en ' + ed.n, h, [
          { v: fmtMdp(ed.gasto), etq: ed.n + ': Ramos 28 y 33 (2026)', e: 'derivado' },
          { v: fmtMdp(ed.asf), etq: ed.n + ': por aclarar ante la ASF (2024)', e: 'oficial' }
        ], MO.portales, [urlEdo, 'La huella de las megaobras']),
        sug: ['Mapa ambiental de megaobras por estado', os.length ? '¿Cuánto costó ' + os[0].nombre.split(' (')[0] + '?' : '¿Qué megaobras hay en Tabasco?', 'Estado de cuenta de ' + ed.n]
      };
    }

    var tipo = null, tipoTit = 'todas las megaobras y casos ambientales';
    if (/\b(tren\w*|selva\w*|ferroviari\w*)\b/.test(p)) { tipo = 'trenes'; tipoTit = 'trenes y selvas'; }
    else if (/\b(refineria\w*|petroleo|pemex|energia|gas|gnl|fertiliz\w*)\b/.test(p)) { tipo = 'energia'; tipoTit = 'refinerías, energía e industria'; }
    else if (/\b(aeropuerto\w*|aifa|texcoco|bodega|megafarmacia)\b/.test(p)) { tipo = 'aeropuertos'; tipoTit = 'aeropuertos y equipamiento'; }
    else if (/\b(agua|acueducto\w*|presa\w*|huracan|otis|desastre\w*)\b/.test(p)) { tipo = 'agua'; tipoTit = 'agua y desastres'; }

    var lista = tipo ? casos.filter(function (c) { return c.tipo === tipo; }) : casos;
    var edosSet = {};
    lista.forEach(function (c) { (c.edos || []).forEach(function (a) { edosSet[a] = 1; }); });
    var nEdos = Object.keys(edosSet).length;
    /* Solo el gasto público se suma (Bloque 4, 27-10-2026). */
    var sumInv = lista.reduce(function (ac, c) { return ac + (c.paga === 'privado' ? 0 : (c.realMdp || 0)); }, 0);
    var nPriv = lista.filter(function (c) { return c.paga === 'privado'; }).length;
    var sumAsf = lista.reduce(function (ac, c) { return ac + (c.asfMdp || 0); }, 0);
    var urlMapa = 'datos-ambiente-megaobras.html' + (tipo ? '?tipo=' + tipo : '') + '#abMapaObras';

    var h = '<p>🗺️ <b>Mapa ambiental de megaobras e infraestructura por estado</b> (' + esc(tipoTit) + '): concentra <b>' + lista.length + ' obras y casos</b> en <b>' + nEdos + ' de las 32 entidades</b> ' + chip({ e: 'derivado' }) + '.</p>' +
      '<ul class="pa-lista">' +
      '<li>💰 <b>Gasto público registrado en estas obras:</b> <b>' + fmtMdp(sumInv) + '</b> ' + chip({ e: 'derivado' }) + ' (suma nacional sin prorratear entre estados' +
        (nPriv ? '; no incluye ' + (nPriv === 1 ? 'el proyecto' : 'los ' + nPriv + ' proyectos') + ' de inversión privada, que no es dinero público' : '') + ').</li>' +
      '<li>🔍 <b>Por aclarar ante la ASF en estas obras:</b> <b>' + fmtMdp(sumAsf) + '</b> ' + chip({ e: 'derivado' }) + ' (más $113,327.7 mdp auditados en la cancelación de Texcoco).</li>' +
      '<li>⏳ <b>Permisos ambientales (MIA) integrados:</b> <b>0 de 11 obras de construcción</b> ' + chip({ e: 'pendiente', p: 'ambiente-0' }) + ' (SEMARNAT y ASEA).</li>' +
      '</ul>' +
      '<p><b>Dónde están y qué alerta ambiental tienen:</b></p><ul class="pa-lista">' +
      lista.slice(0, 8).map(function (c) {
        return '<li><span aria-hidden="true">' + esc(c.ico) + '</span> <b>' + esc(c.nombre) + '</b> (' + esc(c.edos.join(', ')) + '): ' +
          (c.paga === 'privado' ? '🏢 <b>inversión privada</b> · ' : c.realMdp != null ? '<b>' + fmtMdp(c.realMdp) + '</b> ' + chip({ e: c.estReal, p: c.pendReal }) + ' · ' : '') +
          '🌱 <i>' + esc(c.ecosistema) + '</i>. <a href="datos-ambiente-megaobras.html?e=' + encodeURIComponent(c.edos[0]) + '#abMapaObras">Ver en mapa ➔</a></li>';
      }).join('') + '</ul>' +
      '<p class="pa-chico">Toca <b>«Saber más»</b> para abrir el mapa interactivo en la Enciclopedia (Medio ambiente › La huella de las megaobras), con tres lentes: Megaobras y alerta ambiental, Gasto federalizado 2026 (Ramos 28 y 33) y Por aclarar ante la ASF.</p>';

    return {
      html: h, ir: [urlMapa, 'el mapa ambiental de megaobras por estado'],
      rec: [
        { x: { ico: '🗺️', v: 'Abrir el mapa ambiental', n: 'La huella de las megaobras por estado', ir: urlMapa } },
        { x: { ico: '🌱', v: 'Auditar sector ambiental', n: 'SEMARNAT, Conagua, PROFEPA y ASEA', ir: 'herramienta-ambiente-auditor.html' } },
        { x: { ico: '⏱️', v: 'Ver simulador', n: 'Simulación en vivo de las megaobras', ir: MO.sims.vivo } },
        { x: { ico: '🌀', v: 'Ver crisis ambientales', n: 'Otis, agua en Jalisco y desastres', ir: 'herramienta-ambiente-crisis.html' } }
      ],
      ficha: moFicha('Mapa ambiental de megaobras por estado', h, [
        { v: nEdos + ' de 32', etq: 'Entidades con megaobras o alertas', e: 'derivado' },
        { v: fmtMdp(sumInv), etq: 'Inversión registrada en el filtro', e: 'derivado' },
        { v: fmtMdp(sumAsf), etq: 'Por aclarar ante la ASF en estas obras', e: 'derivado' }
      ], MO.portales, [urlMapa, 'La huella de las megaobras']),
      sug: ['¿Qué megaobras hay en Tabasco?', '¿Cuál es el impacto ambiental del Tren Maya?', 'Impacto ambiental de las refinerías']
    };
  }
  function cotejaObra(q, p) {
    var obs = obrasEn(q);
    if (obs.length !== 1 || !charla || !charla.juzga) return null;
    var o = obs[0], c = o.c;
    /* En dólares no se coteja: la plataforma no convierte monedas. */
    if (/\b(dolar\w*|usd|mdd)\b/.test(p)) {
      var rd = respObra(o, '', false);
      rd.html = '<p>⚪ <b>No lo puedo cotejar en dólares.</b> ' + esc(MO.nombre) + ' lleva la obra en pesos, como la reportan sus documentos, y no convierte monedas. ' +
        (o.resc ? 'Lo pagado y debido' : 'Su costo real') + ' es <b>' + esc(c.real.vt) + '</b> ' + chipE(c.real) + '.</p>' + rd.html;
      return rd;
    }
    var sob = /\b(sobrecosto|sobreprecio|se encarecio|de mas)\b/.test(p), apr = /\b(aprob\w*|presupuest\w*|se presento)\b/.test(p);
    var cual = sob ? c.sob : apr ? c.pres : c.real, val = sob ? { v: cual.v, u: 'pct' } : { v: cual.v, u: 'mdp' };
    var jz = cual.e !== 'pendiente' && charla.juzga(q, val);
    if (!jz) return null;
    var etq = sob ? c.sob.et : apr ? (o.resc ? 'lo que se presentó' : 'lo aprobado') : (o.resc ? 'lo pagado y debido' : 'su costo real');
    var r = respObra(o, sob ? 'sob' : apr ? 'pres' : '', false);
    r.html = '<p>' + { verde: '✅', ambar: '⚠️', rojo: '❌' }[jz.v.tipo] + ' <b>' + esc(jz.v.tit) + '.</b> Dices «' + esc(jz.dicho.bruto) + '»; ' + esc(etq) + ', según ' + esc(MO.nombre) +
      ', es <b>' + esc(cual.vt) + '</b> ' + chipE(cual) + '. ' + esc(jz.v.porque) + '</p>' +
      '<p class="pa-chico">Veredicto ' + chip({ e: 'derivado' }) + ': diferencia entre la cifra que dices y la de la plataforma; se acepta el redondeo.</p>' + r.html;
    r.tit = 'Verificación: ' + o.n;
    return r;
  }
  function megaobras(q, previas) {
    if (!MO.obras.length) return null;
    var p = plano(q);
    /* Lo que contestan otros: el Paquete 2027, un expediente. */
    if (/\b(2027|paquete|se propone|propuesta|propone)\b/.test(p) || /\b(expedientes?|pliegos?)\b/.test(p)) return null;
    /* «¿Es cierto que el Tren Maya costó 500 mil millones?» se coteja contra el
       costo de la obra, no contra otra cifra que comparta su nombre (27-10-2026). */
    if (/\b(es cierto|es verdad|dicen que|escuche|lei que|vi que)\b/.test(p)) return cotejaObra(q, p);
    /* Si pregunta por una obra específica (incluso su huella o alerta ambiental), o por el mapa ambiental / megaobras en un estado. */
    var obs0 = obrasEn(q);
    if (!obs0.length) {
      var rAmb = respMapaAmb(q, p);
      if (rAmb) return rAmb;
      if (/\b(ambiental|ambiente|selva|huella|deforest\w*|manifestacion)\b/.test(p)) return null;
    }
    var defin = /^\s*(que|q) (es|son|fue|significa)\b/.test(p);
    /* 1. Las aplicaciones por su nombre, o qué hay en la herramienta. */
    var id = null;
    MO.apps.forEach(function (a) { if (!id && (p.indexOf(a._p) >= 0 || a._c.trim().split(' ').length > 2 && p.indexOf(a._c) >= 0)) id = a.id; });
    var pideTodo = /\b(inversion y megaobras|megaobras?|las grandes obras|obras de cada sexenio)\b/.test(p);
    if (id === 'motabla' || /\b(cada presidente|todos los presidentes|cada sexenio|los sexenios|los seis sexenios)\b/.test(p) && /\b(obras?|megaobras?|invirti\w*)\b/.test(p)) return respTodosSx();
    if (id) {
      var a = APP[id];
      return respApp(id, a.url, '<p><span aria-hidden="true">' + a.ico + '</span> <b>' + esc(a.n) + '</b> es la aplicación ' + a.k + ' de ' + esc(MO.nombre) + '. ' + esc(a.desc) + '</p><p>' + esc(MO_EJ[id] || '') + ' O úsala aquí abajo, sin salir del chat.</p>');
    }
    /* 2. Una o dos obras, por su nombre (o la de la pregunta anterior: «¿y su sobrecosto?»). */
    var obs = obrasEn(q), foco = focoDe(p);
    if (!obs.length && foco && /^\s*(y|¿y)\b|\b(su|sus)\b/.test(p) && previas && previas.length) {
      var ant = obrasEn(previas[previas.length - 1]);
      if (ant.length === 1) obs = ant;
    }
    if (obs.length) {
      /* «¿Qué es el FOBAPROA?» lo contesta el glosario. */
      if (defin && obs[0].resc) return null;
      if (obs.length > 1) return respDuelo(obs[0], obs[1]);
      return respObra(obs[0], foco, MO_SIM.test(p));
    }
    /* 2 a. Un proyecto de inversión privada del mapa ambiental («¿cuánto costó la
       terminal de gas de Guaymas?»): no es gasto público y se dice (Bloque 4). */
    var priv = (MO.casosAmb || []).filter(function (c) { return c.paga === 'privado' && (c.al || []).some(function (a) { return p.indexOf(' ' + a + ' ') >= 0; }); })[0];
    if (priv && !defin) {
      var urlP = 'datos-ambiente-megaobras.html?e=' + encodeURIComponent(priv.edos[0]) + '&paga=privado#abMapaObras';
      return {
        html: '<p>' + priv.ico + ' <b>' + esc(priv.nombre) + '</b> (' + esc(priv.sede) + ')</p>' +
          '<p>🏢 <b>Es inversión privada, no gasto público</b> ' + chip({ e: priv.estReal, p: priv.pendReal }) + '. ' + esc(priv.pagaTxt.replace(/^Inversión privada: /, '')) + '</p>' +
          '<p>🌱 <b>Alerta ambiental:</b> ' + esc(priv.alerta) + '</p>',
        ir: [priv.ficha || urlP, 'lo que verificamos del caso'], rec: [{ x: { ico: '🗺️', v: 'Ver en el mapa ambiental', n: 'Con los proyectos privados', ir: urlP } }],
        sug: ['¿Es cierto que prestaron 54 hectáreas en Guaymas?', 'Mapa ambiental de megaobras por estado']
      };
    }
    /* 2 bis. El costo de una obra que no sigue la herramienta («¿cuánto costó el
       Tren Interoceánico?»): se dice que no está, en vez de contestar con otra obra. */
    if (!defin && /\b(cuanto|costo|cuesta|costaron|vale)\b/.test(p) && /\b(tren|refineria|aeropuerto|presa|autopista|carretera|puerto|corredor|acueducto|hospital)\b/.test(p)) {
      var nObras = MO.obras.filter(function (x) { return !x.resc; });
      return {
        html: '<p>⚪ <b>Esa obra no está entre las que sigue ' + esc(MO.nombre) + '.</b> Su costo total no lo tengo con documento, así que no te doy una cifra. Sigo estas ' + nObras.length + ':</p>' +
          '<p>' + nObras.map(function (x) { return '<button type="button" class="pa-ej" data-pa-pregunta="' + esc('¿Cuánto costó ' + x.n + '?') + '">' + x.ico + ' ' + esc(x.n) + '</button>'; }).join(' ') + '</p>' +
          '<p class="pa-chico">Si la obra trae dinero en el Paquete Económico 2027, pregúntame «¿cuánto propone el Paquete 2027 para…?».</p>',
        ir: ['herramienta-megaobras.html', MO.nombre], rec: [], sug: [], anota: 1
      };
    }
    /* 3. En qué invirtió un presidente (o dos, frente a frente). */
    if (/\b(obras?|megaobras?|invirti\w*|construy\w*|proyectos?|inversiones)\b/.test(p) && !/\binversion fisica\b/.test(p)) {
      var sxs = sxEn(q);
      if (sxs.length > 1) return respSxDuelo(sxs[0], sxs[1]);
      if (sxs.length) return respSx(sxs[0]);
      var ad = admDe(q);
      if (ad && /\b(obras?|megaobras?)\b/.test(p)) return { html: '<p>🏛️ ' + esc(MO.nombre) + ' sigue los seis sexenios de 1988 a 2024. De la administración de ' + esc(ad.n) + ' todavía no evalúa ninguna obra.</p>',
        ir: [APP.motabla.url, 'En qué invirtió cada presidente'], app: { id: 'motabla', url: APP.motabla.url }, rec: [], sug: ['¿En qué invirtió cada presidente?', 'Estado de cuenta de ' + ad.n] };
    }
    /* 4. Los rankings: la de más sobrecosto, la que más pierde, la más cara. */
    if (/\b(megaobras?|obras?)\b/.test(p) && /\b(mas|mayor|menos|menor|peor|mejor|cual|cuales|ranking|top|que)\b/.test(p)) {
      var asc = /\b(menos|menor|mejor)\b/.test(p) && !/\b(gana|ganancia)\b/.test(p);
      if (/\bsobrecostos?\b|\bse paso\b|\bde mas\b/.test(p)) return respRank('sob', asc);
      if (/\b(gana|ganan|ganancia|rentable)\b/.test(p)) return respRank('gana');
      if (/\b(pierde|pierden|perdida|perdidas|deficit)\b/.test(p)) return respRank('pierde', asc);
      if (/\b(cara|caras|costosa|costosas|costo|costaron|cuesta)\b/.test(p)) return respRank('real', asc);
    }
    /* 5. Las megaobras en conjunto. */
    if ((pideTodo || /\bobras?\b/.test(p)) && MO_SIM.test(p) && !defin) {
      var rs = respMoTodo(false);
      rs.app = { id: 'mosector', url: MO.sims.vivo, abre: true };
      rs.html = '<p>⏱️ Te abro aquí abajo la <b>simulación en vivo</b> de «Obra por obra»: lo que cada megaobra gana o pierde mientras miras, filtrable por industria y por presidente. También tienes el ritmo de la pérdida (por día, mes o año) y «de la cifra a tu bolsillo», en «Explóralo a fondo».</p>' + rs.html;
      return rs;
    }
    if (pideTodo && !defin) return respMoTodo(/\b(que puedo|aplicaciones|que hay|como uso|que hace)\b/.test(p) || /^\s*(inversion y megaobras|megaobras)\s*$/.test(p));
    return null;
  }

  /* ============ Noticias relevantes y personajes, dentro del chat ===========
     (24-10-2026, pedido del autor): el nombre de un personaje abre lo que la
     plataforma pudo sostener de él (las columnas de Noticias relevantes, con
     sus documentos) y lo menos evidente: lo que circula y no se pudo probar,
     con el motivo. Lo que hay en internet no lo afirma el chat: ofrece las
     búsquedas ya armadas en los portales oficiales y en las noticias, como
     «sin verificar», y lleva a Contrasta una nota. El índice lo escribe
     herramientas/asistente_personajes.py. */
  var PE = (B.dat && B.dat.per) || { per: [], web: [] }, COLF = {};
  F.forEach(function (f) { if (f.t === 'columna') COLF[f.col] = f; });
  var PER_CTX = /\b(quien es|quien fue|quienes son|quien era|noticias?|que se sabe|que paso con|que hizo|que hay de|que dicen de|datos? curiosos?|columnas?|historia de|biografia|trayectoria|procesos?|juicios?|sentencias?|sentenciad\w*|condena\w*|denuncia\w*|acusa\w*|investigad\w*|escandalos?|polemica\w*|corrupcion|carpetas?|detenid\w*|preso|presa|carcel|prision|rumor\w*|chismes?|contratos?|contratista\w*|proveedor\w*|empresa)\b/;
  var NOTICIAS_RE = /^\s*(las |unas |dame |muestrame |ver |quiero |que )*(noticias( relevantes)?|columnas?( del erario)?|la columna del erario|datos curiosos)\s*$/;
  var PARTICULA = { de: 1, del: 1, la: 1, las: 1, los: 1, y: 1 };
  function personaDe(p) {
    var hay = null, largo = 0;
    PE.per.forEach(function (x) { x.al.forEach(function (a) { if (p.indexOf(' ' + a + ' ') >= 0 && a.length > largo) { hay = x; largo = a.length; } }); });
    return hay;
  }
  /* Lo que queda de la pregunta sin el nombre ni las palabras vacías. */
  function sobra(p, quita, nombre) {
    var suyo = plano(nombre);
    quita.forEach(function (a) { p = p.split(' ' + a + ' ').join(' '); });
    return p.trim().split(/\s+/).filter(function (w) { return w && suyo.indexOf(' ' + w + ' ') < 0 && !vacia[w] && !PARTICULA[w] && !/^(sobre|acerca|algo|cosas?|todo|informacion|info|dato|datos)$/.test(w); });
  }
  /* Un nombre que la plataforma no tiene («¿quién es Fulana Pérez?»): se toma
     tal como lo escribió el lector, para buscarlo fuera. */
  function nombreDe(q) {
    var t = String(q).replace(/[¿?¡!.,;:«»"]/g, ' ').replace(/\s+/g, ' ').trim();
    var m = /^(?:dime |dame |busca |investiga )?(?:quien es|quién es|quien fue|quién fue|noticias de|noticias sobre|que se sabe de|qué se sabe de|que hizo|qué hizo|que hay de|qué hay de|que dicen de|qué dicen de|que paso con|qué pasó con)\s+(.+)$/i.exec(t);
    var n = (m ? m[1] : t).replace(/^(el|la|los|las)\s+/i, '').trim(), ws = n.split(' ');
    if (ws.length < 2 || ws.length > 6 || n.length > 70 || /\d/.test(n)) return null;
    var propias = ws.filter(function (w) { return /^[A-ZÁÉÍÓÚÑ]/.test(w); }).length;
    var todas = ws.every(function (w) { return /^[A-ZÁÉÍÓÚÑ]/.test(w) || PARTICULA[norm(w)]; });
    /* Sin «quién es…», solo si cada palabra va con mayúscula: «Rocío Nahle». */
    if (!m && (!todas || propias < 2)) return null;
    if (m && propias < 1 && ws.length > 4) return null;
    return n;
  }
  /* El nombre corto de una empresa: sin «, S.A. de C.V.» y parecidos. */
  function corta(n) { return String(n).replace(/\s*\([^)]*\)\s*$/, '').replace(/,?\s+(S\.?\s?A\.?|S\.?\s?de\s?R\.?\s?L\.?|S\.?\s?C\.?|S\.?\s?A\.?\s?P\.?\s?I\.?).*$/i, '').trim(); }
  function webHtml(nombre, emp) {
    var q = '"' + (emp ? corta(nombre) : nombre) + '"';
    return '<div class="pa-rec pa-web"><p class="pa-mas-t">Búscalo en internet</p>' +
      '<p class="pa-chico">Esto ya no es la plataforma: son búsquedas ya armadas con el nombre, primero en portales oficiales y al final en las noticias. ' +
      '<b>Lo que encuentres ahí no lo verificó Auditavisión</b>: una nota de prensa no es un documento oficial, y un proceso no es una condena.</p>' +
      '<div class="pa-rec-lista">' + (emp ? PE.webEmp : PE.web).map(function (w) {
        var portal = w.site && w.site.indexOf('https://') === 0;
        var u = portal ? w.site : w.site ? 'https://www.google.com/search?q=' + encodeURIComponent(q + ' ' + w.site)
          : 'https://news.google.com/search?q=' + encodeURIComponent(q) + '&hl=es-419&gl=MX&ceid=MX:es-419';
        return '<a class="pa-rec-a" href="' + esc(u) + '" target="_blank" rel="noopener noreferrer"><span class="pa-rec-ico" aria-hidden="true">' + w.ico + '</span>' +
          '<span><b>' + esc(w.n) + '</b><small>' + (portal ? 'Portal oficial · escribe ahí ' + esc(q) + ' ↗' : w.e === 'oficial' ? 'Fuente oficial · se abre en otra pestaña ↗' : 'Prensa: sin verificar · se abre en otra pestaña ↗') + '</small></span></a>';
      }).join('') + '</div>' +
      '<p class="pa-chico">¿Encontraste una nota con cifras? Pégame aquí su liga y la cotejo contra los documentos oficiales, con <a href="herramienta-inspector-nota.html">Contrasta una nota</a>.</p></div>';
  }
  function colHtml(f, grande) {
    var ci = (f.ci || []).slice(0, grande ? 3 : 2);
    return '<div class="pa-col"><p class="pa-col-t">📰 <a href="' + esc(f.ir[0]) + '"><b>' + esc(f.tit) + '</b></a></p>' +
      (f.txt ? '<p>' + esc(f.txt) + '</p>' : '') +
      (ci.length ? '<ul class="pa-lista">' + ci.map(function (c) { return '<li><b>' + esc(c.v) + '</b> · ' + esc(c.etq) + ' ' + chip(c) + '</li>'; }).join('') + '</ul>' : '') +
      (grande && f.dc ? '<p class="pa-col-dc"><b>💡 Dato curioso:</b> ' + esc(f.dc) + '</p>' : '') +
      (grande && charla && f.cot ? charla.cotejo(f, false) : '') + '</div>';
  }
  function descHtml(per, abierto) {
    if (!per.desc.length) return '';
    return '<details class="pa-desc"' + (abierto ? ' open' : '') + '><summary>🧺 Lo que circula y no pudimos sostener <small>(' + per.descn + ')</small></summary>' +
      '<p class="pa-chico">Esto se dice en prensa o en redes, pero la plataforma no encontró el documento oficial que lo pruebe. No lo afirmamos ni lo negamos: te decimos por qué se quedó fuera.</p><ul>' +
      per.desc.map(function (d) { return '<li><b>' + esc(d.tema) + '.</b> ' + esc(d.af) + ' <span class="pa-desc-mo"><b>Por qué no:</b> ' + esc(d.mo) + '</span></li>'; }).join('') +
      '</ul>' + (per.descn > per.desc.length ? '<p class="pa-chico">Y ' + (per.descn - per.desc.length) + ' más en <a href="' + esc(PE.pag) + '">Noticias relevantes</a>, al pie: «Lo que dejamos fuera y por qué».</p>' : '') + '</details>';
  }
  function respPersona(per) {
    var cols = per.col.map(function (id) { return COLF[id]; }).filter(Boolean), f = cols[0];
    var a = admDe(per.n), h, fu = [];
    if (f) {
      h = '<p>Sobre ' + (per.emp ? 'la empresa ' : '') + '<b>' + esc(per.n) + '</b>, ' + (cols.every(function (c) { return c.cot && c.cot.length; })
          ? 'esto es lo que la plataforma cotejó contra documentos oficiales de lo que circula, en ' + (cols.length > 1 ? cols.length + ' columnas' : 'la columna') + ' de <b>Verificamos</b>:</p>'
          : 'esto es lo que la plataforma pudo sostener con documentos, en ' + (cols.length > 1 ? 'sus ' + cols.length + ' columnas' : 'su columna') + ' de <b>Noticias relevantes</b>:</p>') +
        cols.slice(0, 3).map(function (c, i) { return colHtml(c, i === 0); }).join('');
      (f.ci || []).slice(0, 4).forEach(function (c) { fu.push({ que: c.etq, e: c.e, fu: c.fu || (f.fu || [])[0] }); });
    } else {
      h = '<p>Sobre <b>' + esc(per.n) + '</b>, la plataforma todavía no tiene una columna verificada. Lo que sí tengo es lo que circula y no se pudo sostener con un documento oficial, y por qué:</p>';
    }
    h += descHtml(per, !f);
    if (a) h += '<p>' + esc(a.n) + ' también tiene el <a href="radar-estado-de-cuenta.html?adm=' + encodeURIComponent(a.id) + '"><b>estado de cuenta de su administración</b></a>: deuda, gasto y lo que observó la ASF.</p>';
    h += '<p class="pa-chico">⚖️ ' + esc((f && f.nota) || 'Un proceso no es una condena: aquí solo va lo que consta en documentos, con presunción de inocencia.') + '</p>';
    if (f && charla) h += charla.deDonde(fu.length ? fu : (f.fu || []).slice(0, 3).map(function (x) { return { que: 'Documento', e: 'oficial', fu: x }; }));
    if (per.emp) h += '<p>🏢 Es una empresa que contrata o contrató con el gobierno. Abajo te dejo dónde ver sus contratos, si está sancionada o inhabilitada y si la autoridad la ha señalado; y pregúntame si está en la <b>lista negra del SAT</b>.</p>';
    h += webHtml(per.n, per.emp);
    /* Lo que la plataforma tiene de esa persona fuera de las columnas. */
    var vistos = {}, sug = [];
    cols.slice(3).forEach(function (c) { sug.push(c); vistos[c.tit] = 1; });
    buscar(per.n).slice(0, 25).forEach(function (x) {
      var t = plano(x.f.tit + ' ' + (x.f.k || '') + ' ' + (x.f.txt || ''));
      if (sug.length < 4 && x.f.t !== 'columna' && x.f.t !== 'fuente' && !vistos[x.f.tit] && per.al.some(function (w) { return t.indexOf(' ' + w + ' ') >= 0; })) { vistos[x.f.tit] = 1; sug.push(x.f); }
    });
    if (per.emp) sug.unshift('¿Está en la lista negra del SAT la empresa ' + corta(per.n) + '?');
    if (per.emp) sug.unshift('Contratos de ' + corta(per.n) + ' en ComprasMX');
    PE.per.forEach(function (o) {
      if (sug.length < 5 && o !== per && o.col.some(function (id) { return per.col.indexOf(id) >= 0; })) sug.push(o.emp ? corta(o.n) : '¿Quién es ' + o.n + '?');
    });
    return {
      html: h, ficha: f || null, tit: per.n,
      ir: f ? (cols.length === 1 ? f.ir : [PE.pag, 'Noticias relevantes']) : [PE.pag, 'Noticias relevantes'],
      sug: sug, rec: []
    };
  }
  function personaje(q) {
    if (!PE.per.length) return null;
    var p = plano(q), n = ' ' + norm(q).replace(/[^a-z0-9ñ]+/g, ' ') + ' ';
    if (NOTICIAS_RE.test(n.trim())) {
      var conCol = PE.per.filter(function (x) { return x.col.length; });
      return {
        html: '<p>📰 <b>Noticias relevantes</b> reúne ' + PE.n + ' columnas con datos poco conocidos de personajes y hechos del dinero público. Solo entra lo que se pudo verificar con un documento oficial, y cada columna cita los suyos.</p>' +
          '<p>Pregúntame por un personaje y te digo lo que consta y lo que circula sin pruebas. Tengo columnas de:</p><p>' +
          conCol.map(function (x) { return '<button type="button" class="pa-ej" data-pa-pregunta="' + esc('¿Quién es ' + x.n + '?') + '">' + esc(x.n) + '</button>'; }).join(' ') + '</p>',
        ir: [PE.pag, 'Noticias relevantes'], sug: [], rec: []
      };
    }
    var per = personaDe(p);
    if (!per) return null;
    if (SAT_PAL.test(n)) return null;  // «¿está en la lista negra…?» lo contesta el SAT
    var ctx = PER_CTX.test(n), nada = !sobra(p, per.al, per.n).length;
    /* Un presidente a secas lo sigue contestando su estado de cuenta, y un
       nombre que también es lugar (Benito Juárez) solo si se habla de personas. */
    if ((per.pres || per.lugar) ? !ctx : !(ctx || nada)) return null;
    return respPersona(per);
  }

  /* Lo que circula y ya cotejamos en Verificamos gana sobre la ficha de un
     lugar cuando la pregunta trae varias palabras de la columna: «¿es cierto
     que prestaron 54 hectáreas en Guaymas?» pide el cotejo, no las finanzas
     del municipio (26-10-2026). */
  var GENERICAS = { cierto: 1, verdad: 1, dicen: 1, circula: 1, redes: 1, gobierno: 1, mexico: 1 };
  /* Una pregunta por un dato («¿cuántos ministros tiene la Corte?») o por un
     estado de cuenta no es un cotejo, aunque comparta palabras con la columna:
     la contesta la plática (27-10-2026). */
  var PIDE_DATO = /^ *(cuant[oa]s?|cual(es)?|quien(es)?|donde|cuando|que es|que son) /, PIDE_COTEJO = / (cierto|verdad|falso|dicen|circula|redes) /;
  function verificado(q) {
    var pq = plano(q);
    if (/ estados? de cuenta /.test(pq) || (PIDE_DATO.test(pq) && !PIDE_COTEJO.test(pq))) return null;
    var col = buscar(q).slice(0, 12).filter(function (x) { return x.f.t === 'columna' && x.f.cot; })[0];
    if (!col || !charla) return null;
    var f = col.f, t = plano(f.tit + ' ' + (f.k || '') + ' ' + (f.txt || '') + ' ' + (f.cir ? f.cir.tx : ''));
    var ws = norm(q).replace(/[^a-z0-9ñ]+/g, ' ').split(' ').filter(function (w) { return w.length > 3 && !vacia[w] && !GENERICAS[w]; });
    var hits = ws.filter(function (w) { return t.indexOf(' ' + w + ' ') >= 0; }).length;
    /* Con «¿es cierto…?» basta que coincidan dos palabras: el lector ya pidió el cotejo. */
    if (hits < (PIDE_COTEJO.test(pq) ? 2 : 3) || hits * 2 < ws.length) return null;
    return charla.deFicha(f);
  }

  /* Alarmas: seguir un caso (26-10-2026). El seguimiento vive en las
     columnas de Noticias relevantes y se guarda en el navegador. */
  var ALARMA_RE = /\b(alarmas?|avisame|avisarme|notificac\w*|sigo (un|el|este) caso|seguir (un|el|este|los) casos?|mis seguimientos|seguir casos)\b/;
  function alarma(q) {
    if (!ALARMA_RE.test(norm(q))) return null;
    return {
      html: '<p>🔔 <b>Sí: puedes seguir un caso.</b> Abre su columna en Noticias relevantes y toca «🔔 Seguir este caso». ' +
        'Cuando la actualicemos con un documento nuevo (el voto, el informe, el contrato o la sentencia de «🗓️ Lo que sigue»), ' +
        'al volver verás el aviso «🆕 Novedades» y la lista de «Tus seguimientos» al inicio del diario.</p>' +
        '<p>Se guarda solo en este navegador: no pedimos correo ni cuenta, y nadie más lo ve. Los avisos por correo o al celular todavía no existen.</p>',
      ir: [PE.pag + '#seguimientos', 'Tus seguimientos'], sug: ['Noticias relevantes', 'Nuestros pilares'], rec: []
    };
  }

  /* El dictamen y el Registro de pendientes, por su nombre (27-10-2026: las
     preguntas de prueba los mandaban al Ágora y a Crisis ambientales). */
  function propias(q) {
    var p = plano(q);
    if (/ dictamen(es)? (civico|independiente|sellado)| (generar|genero|saco|hago|pido|sirve) (un |el )?dictamen|^ (que es )?(el |un )?dictamen $/.test(p))
      return {
        html: '<p>🧾 El <b>Dictamen cívico independiente</b> respalda una respuesta mía: trae las cifras, de qué documento sale cada una, su estado (oficial, derivado o pendiente), un folio y una huella digital para comprobar que nadie lo alteró.</p>' +
          '<p>Para sacarlo, hazme una pregunta y, en la respuesta, toca <b>«🧾 Generar dictamen»</b>: se abre en otra pestaña, listo para imprimir o compartir. El enlace solo lleva tu pregunta y la página la vuelve a contestar con la misma base, así que nadie puede fabricar uno con cifras ajenas.</p>' +
          '<p class="pa-chico">No es un documento oficial ni un peritaje con validez ante una autoridad.</p>',
        ir: ['herramienta-inspector-dictamen.html', 'Dictamen cívico independiente'], rec: [], sug: ['¿Cuánto debe Jalisco?', 'Verifica un estado de cuenta']
      };
    if (/ (falta|faltan) (por )?(transparentar|publicar)| no (han )?(transparentado|publicado) | datos pendientes /.test(p) && !/ ambient| crisis /.test(p)) {
      var f = F.filter(function (x) { return x.ir && x.ir[0] === 'pendientes.html'; })[0];
      if (f && charla) { var r = charla.deFicha(f); r.sug = ['¿Qué no dice el informe semestral?', '¿Cuánto dejó por aclarar la ASF?']; return r; }
    }
    /* «Al momento» (28-10-2026): las notas breves de Noticias, de la más nueva a
       la más vieja. Sin esto, «noticias de hoy» llevaba a una columna cualquiera. */
    if (/ (noticias? (de hoy|del dia|recientes|de ultima hora|de la semana)|ultimas noticias|al momento|que (esta|estan) pasando|que hay de nuevo|que paso hoy) /.test(p)) {
      var fn = function (d) { var x = String(d || '').split('-'); return x.length === 3 ? +(x[2] + x[1] + x[0]) : 0; };
      var am = F.filter(function (x) { return x.t === 'columna' && / columna al momento /.test(plano(x.k)); })
        .sort(function (x, y) { return fn(y.act) - fn(x.act); }).slice(0, 5);
      if (am.length) return {
        html: '<p>⏱️ <b>Al momento</b>, lo más reciente que verificamos contra los documentos oficiales:</p><ul class="pa-lista">' + am.map(function (x) {
          return '<li><a href="' + esc(x.ir[0]) + '"><b>' + esc(x.tit) + '</b></a> <small>(' + esc(x.act) + ')</small><br>' + esc(x.txt) + '</li>';
        }).join('') + '</ul><p class="pa-chico">Cada nota dice de qué nota de prensa salió, qué consta en el documento oficial y qué falta probar. Lo que dice la red, al pie de cada una, va rotulado «sin verificar».</p>',
        ir: ['noticias-relevantes.html#al-momento', 'Noticias · Al momento'], rec: [],
        sug: am.slice(0, 2).map(function (x) { return x.tit; }).concat(['¿Cómo sigo un caso?'])
      };
    }
    /* Quien fue aludido y quiere aclarar: la página del derecho de réplica, no
       la columna que comparte sus palabras (Bloque 4, 27-10-2026). «¿Qué es…?»
       lo sigue contestando el glosario. */
    if (!/^ que es /.test(p) && (/ (replica|rectificacion|rectificar) /.test(p) || / (corregir|aclarar|desmentir|responder) (lo|algo) (que )?(dicen|dijeron|publicaron|publican|escribieron) (de|sobre) mi /.test(p) ||
        / me (aludieron|aluden|mencionaron|mencionan|nombraron|nombran|exhibieron) /.test(p))) {
      var fr = F.filter(function (x) { return x.ir && x.ir[0] === 'derecho-de-replica.html'; })[0];
      if (fr && charla) { var rr = charla.deFicha(fr); rr.sug = ['¿Qué es el derecho de réplica?', 'Fe de erratas']; return rr; }
    }
    /* La confianza en el INE (ENCIG del INEGI) vive en la columna de Verificamos
       sobre su Órgano Interno de Control (28-10-2026): sin esto, «INE» llevaba a su presupuesto. */
    if (/ confian\w* /.test(p) && / (ine|instituto nacional electoral|institutos? electorales?) /.test(p)) {
      var fc = F.filter(function (x) { return x.ir && x.ir[0] === 'noticias-relevantes.html#col-ine-oic-auditorias-consejerias'; })[0];
      if (fc && charla) { var rc = charla.deFicha(fc); rc.sug = ['¿El órgano interno de control puede auditar a los consejeros del INE?', '¿Cuánto gasta el INE?']; return rc; }
    }
    /* Pensiones u oxígeno pagados a personas fallecidas en Sonora: la auditoría del
       ISAF al ISSSTESON vive en su columna de Verificamos (28-10-2026); sin esto,
       «Sonora» llevaba a la ficha del estado. */
    if (/ (pension\w*|jubilacion\w*|jubilad\w*|oxigeno) /.test(p) && / (fallecid\w*|muert\w*|difunt\w*|finad\w*|defuncion\w*) /.test(p) && / (sonora|isssteson|isaf) /.test(p)) {
      var fs = F.filter(function (x) { return x.ir && x.ir[0] === 'noticias-relevantes.html#col-isssteson-oxigeno-pensiones-fallecidos'; })[0];
      if (fs && charla) { var rs = charla.deFicha(fs); rs.sug = ['¿Cuánto debe Sonora?', 'Biosistemas y Seguridad Privada']; return rs; }
    }
    /* La investigación del Seguro Popular en Auditoría en imágenes (28-10-2026):
       «la auditoría del Seguro Popular», «qué le observó la ASF». */
    if (/ seguro popular /.test(p) && / (auditoria\w*|investigacion\w*|imagen\w*|asf|observ\w*|exito|logro\w*) /.test(p) && charla) {
      var fi = INV.filter(function (x) { return x.ir && x.ir[0] === 'auditoria-seguro-popular.html'; })[0];
      if (fi) { var ri = charla.deFicha(fi); ri.sug = ['¿Es cierto que con el Seguro Popular se atendieron más de 51 millones?', '¿Qué pasó con el Seguro Popular?']; return ri; }
    }
    /* Lo que el Seguro Popular cubría y cuánta gente se quedó sin acceso a la salud
       vive en su columna de Verificamos (28-10-2026); «¿qué pasó con el Seguro Popular?»
       sigue llevando a la transición de Datos · Salud pública. */
    if ((/ seguro popular /.test(p) && / (\d+ millones|millones|atend\w*|afiliad\w*|quitaron|quito|mejor|malestar) /.test(p)) ||
        (/ (sin acceso|carencia\w*|se quedaron sin|perdieron) /.test(p) && / (salud|servicios de salud|servicios medicos) /.test(p) && / (cuant\w*|millones|gente|personas|mexicanos) /.test(p))) {
      var fp = F.filter(function (x) { return x.ir && x.ir[0] === 'noticias-relevantes.html#col-seguro-popular-51-millones'; })[0];
      if (fp && charla) { var rp = charla.deFicha(fp); rp.sug = ['¿Qué pasó con el Seguro Popular?', '¿Qué sabemos del IMSS-Bienestar?']; return rp; }
    }
    if (/ seguro popular /.test(p) && charla) {
      var rt = charla.contesta(q);
      if (rt && rt.ir && rt.ir[0] === 'datos-salud-sistema.html#sal-transicion') { rt.sug = ['¿Es cierto que con el Seguro Popular se atendieron más de 51 millones?', '¿Cuánta gente se quedó sin acceso a servicios de salud?']; return rt; }
    }
    /* La deuda de Pemex no la tiene la plataforma: se dice, con su pendiente,
       en vez de contestar con su presupuesto (27-10-2026). */
    if (/ pemex /.test(p) && (/ (debe|adeuda|deuda|endeudamiento|pasivos?) /.test(p)) && !/ (intereses|costo financiero|paga) /.test(p))
      return {
        html: '<p>⚪ <b>Cuánto debe Pemex, todavía no lo tengo con documento</b> ' + chip({ e: 'pendiente', p: 'pemex-deuda' }) + '. Pemex publica su deuda en sus reportes trimestrales; la plataforma aún no la coteja ni la integra, así que no te doy una cifra.</p>' +
          '<p>Lo que sí tengo: lo que Pemex paga de intereses en 2026. Pregúntame «¿cuánto paga Pemex de intereses?».</p>',
        ir: ['pendientes.html#pemex-deuda', 'Registro de pendientes'], rec: [], sug: ['¿Cuánto paga Pemex de intereses?', 'Diagnóstico de Pemex'], anota: 1
      };
    return null;
  }

  function respuesta(q, previas) {
    var inv = investigacion(q);
    if (inv) return inv;
    var al = alarma(q);
    if (al) return al;
    var pr = propias(q);
    if (pr) return pr;
    /* «¿Es cierto que la UIF congeló cuentas de contratistas?» pide el cotejo de una
       columna de Verificamos, no una búsqueda en ComprasMX (27-10-2026). */
    var sa = charla && charla.salud && PIDE_COTEJO.test(plano(q)) && (charla.salud(q) || (charla.ambiente && charla.ambiente(q)));
    if (sa) return sa;
    var vc = PIDE_COTEJO.test(plano(q)) && verificado(q);
    if (vc) return vc;
    var cx = cruceSat(q) || contratosCmx(q);
    if (cx) return cx;
    var pe = personaje(q);
    if (pe) return pe;
    var ins = conApp(inspector(q, previas));
    if (ins) return ins;
    var mo = conApp(megaobras(q, previas));
    if (mo) return mo;
    var he = conApp(herramienta(q));
    if (he) return he;

    var rc = pideRecurso(q);
    if (rc) return rc;
    var vf = verificado(q);
    if (vf) return vf;
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
    if (!res.length || res[0].s < 3) return { sin: res.slice(0, 3).map(function (x) { return x.f; }), web: nombreDe(q) };
    var f = res[0].f, vistos = {}, otras = [];
    /* Un nombre propio que la plataforma no tiene («Ricardo Monreal Ávila»)
       no se contesta con lo que se le parece (un municipio «de Ávila»): se
       dice que no está y se ofrece buscarlo fuera. */
    var nom = nombreDe(q);
    if (nom) {
      var nws = fichas(nom), tt = plano(f.tit);
      if (nws.filter(function (w) { return tt.indexOf(' ' + w + ' ') >= 0; }).length * 2 < nws.length) return { sin: res.slice(0, 3).map(function (x) { return x.f; }), web: nom };
    }
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
    /* Un nombre que la plataforma no tiene: lo que encontró se queda, y se
       ofrece buscarlo fuera, si lo encontrado no lo nombra. */
    if (nom && plano(f.tit + ' ' + (f.txt || '')).indexOf(plano(nom)) < 0) r.web = nom;
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
    var r = respuesta(q, previas);
    /* La lista negra del SAT contesta cuando termina de descargar la lista. */
    var espera = r.espera ? r.espera.then(function (x) { r = x; }) : null;
    var pinta = function (li) {
      if (r.sin) {
        li.querySelector('.pa-burbuja').innerHTML = sinRespuesta(q, r.sin) + (r.web ? webHtml(r.web) : '');
        if (!ya) anota(q, 'sin');
        return;
      }
      if (r.anota && !ya) anota(q, 'sin');
      li.querySelector('.pa-burbuja').innerHTML = '<div class="pa-resp">' + r.html + '</div>' + acciones(q, r, previas) +
        appDe(r) +
        (r.plat ? '' : recursosHtml(conInv(q, r, r.rec || recursosPara(q, r)))) +
        (r.web ? webHtml(r.web) : '') +
        (r.sug && r.sug.length ? '<p class="pa-mas-t">' + (r.tambien ? 'También te puede servir' : 'Sigue preguntando') + '</p>' + chips(r.sug) : '');
      var caja = li.querySelector('.pa-app[data-pa-abre]');
      if (caja) montaApp(caja);
      guarda();
    };
    if (quieto || QUIETO) {
      var l0 = agrega('pa-bot', '', quieto);
      if (espera) espera.then(function () { pinta(l0); }); else pinta(l0);
      return;
    }
    var li = agrega('pa-bot pa-escribe', '<span class="pa-puntos" role="img" aria-label="Escribiendo"><i></i><i></i><i></i></span>');
    Promise.all([new Promise(function (ok) { setTimeout(ok, 420); }), espera]).then(function () {
      li.classList.remove('pa-escribe'); pinta(li); li.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
  }
  /* La tarjeta de la aplicación del Modo Inspector que viene al caso: la que
     pidió el lector (abierta) o la de la página a la que lleva «Saber más». */
  function appDe(r) {
    if (r.sin || r.plat) return '';
    if (r.app) return appHtml(r.app);
    var ir = r.ir || (r.ficha && r.ficha.ir), a = ir && appDeLiga(ir[0]);
    return a ? appHtml({ id: a.id, url: ir[0] }) : '';
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
    var r = respuesta(q, antes);
    if (r && r.espera) r.espera.then(function (x) { arma(x); }); else arma(r);
    function arma(r) {
    var f = r && !r.sin ? r.ficha : null;
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
    /* La aplicación del Modo Inspector, en el marco de la respuesta. */
    var ap = ev.target.closest ? ev.target.closest('.pa-app') : null;
    if (ap && ev.target.closest('.pa-app-usa')) { montaApp(ap); return; }
    if (ap && ev.target.closest('.pa-app-cierra')) { cierraApp(ap); return; }
    var cr = ap && ev.target.closest('.pa-app-crece');
    if (cr) {
      var toda = ap.classList.toggle('pa-app-completa');
      cr.setAttribute('aria-pressed', toda ? 'true' : 'false');
      cr.textContent = toda ? '⤡ Verla en recuadro' : '⤢ Verla completa';
      var mm = ap.querySelector('.pa-app-marco');
      if (mm && mm._mide) mm._mide();
      return;
    }
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
      else sessionStorage.setItem(CLAVE, JSON.stringify({ h: historial, li: lis.map(function (li) {
        /* Las aplicaciones abiertas se guardan cerradas: al volver, se abren con «Úsala aquí». */
        var c = li.cloneNode(true);
        Array.prototype.forEach.call(c.querySelectorAll('.pa-app-marco'), function (m) { m.parentNode.removeChild(m); });
        Array.prototype.forEach.call(c.querySelectorAll('.pa-app'), function (x) {
          x.removeAttribute('data-pa-abre'); x.className = 'pa-app';
          var u = x.querySelector('.pa-app-usa'); if (u) u.hidden = false;
        });
        return c.outerHTML;
      }) }));

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
