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
  /* Dos chats, reflejo uno del otro (pedido del autor, 21-11-2026): el del Auditor, con
     tres modos, y el Inspector de Servicios (data-solo="inspector"), que contesta en
     corto; su respuesta completa abre en su propia página (#respApp), que cierra con
     «Generar dictamen». Los dos leen la misma base. */
  var resp = document.getElementById('respApp');
  var SOLO = (document.getElementById('paApp') || { getAttribute: function () { return null; } }).getAttribute('data-solo');
  var SV_CHAT = 'servicios-inspector.html', SV_RESP = 'servicios-respuesta.html', CHAT_AV = 'herramienta-inspector-pregunta.html';
  if (!B || (!dic && !resp && (!hilo || !form || !campo))) return;
  /* Los municipios salen del padrón del INEGI (municipios-efipem.js, que la
     página carga): aquí se arma la ficha de cada uno. */
  var MU = window.AUDIT_MUNICIPIOS, NOMBRE = {};
  /* Las fichas del archivo publicado; la función auditor-ia solo conoce esas. */
  var N0 = B.fichas.length;
  ((B.dat && B.dat.edo) || []).forEach(function (e) { NOMBRE[e.a] = e.n; });
  /* Homónimos (Ronda 6, 22-11-2026): cada municipio lleva su entidad en el título, y si su nombre se repite en otros
     estados, su ficha lo dice; entre homónimos que empatan en la búsqueda gana el de más habitantes (Censo 2020). */
  var HOM = {}, MPOB0 = window.AUDIT_MUN_POB || null;
  if (MU && MU.ent) Object.keys(MU.ent).forEach(function (ab) {
    MU.ent[ab].lista.forEach(function (r) { var k = r[1].toLowerCase(); (HOM[k] = HOM[k] || []).push(r[1] + ', ' + (NOMBRE[ab] || ab)); });
  });
  if (MU && MU.ent) Object.keys(MU.ent).forEach(function (ab) {
    MU.ent[ab].lista.forEach(function (r) {
      var ing = r.length > 2 ? r[2] / 1e6 : null, en = NOMBRE[ab] || ab, cve = MU.ent[ab].cve + r[0];
      var otros = (HOM[r[1].toLowerCase()] || []).filter(function (x) { return x !== r[1] + ', ' + en; });
      var pob = MPOB0 && MPOB0.mun && MPOB0.mun[cve] ? MPOB0.mun[cve][0] : 0;
      B.fichas.push({ t: 'municipio', tit: r[1] + ', ' + en, _pob: pob,
        txt: (MU.ent[ab].cve === '09' ? 'Ámbito: alcaldía de la Ciudad de México. ' : 'Ámbito municipal. ') + 'Su ficha técnica: cuentas de 2024 ante el INEGI, FAIS y FORTAMUN ante Hacienda, quién gobernó y lo que observó la ASF.',
        hom: (otros.length ? 'Ojo con los homónimos: también hay ' + (otros.length === 1 ? 'un municipio' : otros.length + ' municipios') + ' con ese nombre en otros estados (' + otros.slice(0, 5).join('; ') + (otros.length > 5 ? '…' : '') + '); si buscas otro, escribe también su estado.' : ''),
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
    /* Dos municipios homónimos empatan en la búsqueda («Juárez»): gana el de más habitantes, nunca el primero del padrón. */
    res.sort(function (a, b) { return b.s - a.s || (a.f.t === 'municipio' && b.f.t === 'municipio' ? (b.f._pob || 0) - (a.f._pob || 0) : 0); });
    return res;
  }

  function chip(c) {
    return '<span class="est-chip est-' + esc(c.e) + '"' + (c.p ? ' data-pend="' + esc(c.p) + '"' : '') + '>' + esc(c.e === 'derivado' ? 'auditada' : c.e) + '</span>';
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
  var ROMANO = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV'];
  function dictamenHtml(q, r, f, antes) {
    var t = TIPO[f.t] || ['📄', 'Ficha'], k = 0;
    function cap(tit) { return '<h3 class="dic-cap"><span>' + ROMANO[k++] + '.</span> ' + tit + '</h3>'; }
    /* Reporte ejecutivo (Ronda 1, 22-11-2026): el desglose técnico va en acordeones, que se abren
       solos al imprimir (beforeprint de armaDictamen). Mismo contenido; nada entra ni sale de la huella. */
    function capD(tit, cuerpo) { return '<details class="dic-sec"><summary>' + cap(tit) + '</summary><div class="dic-sec-c">' + cuerpo + '</div></details>'; }
    /* Las cifras van en tabla (16-11-2026): cifra, qué es, su estado y su operación. */
    var ci = (f.ci || []).map(function (c, i) {
      return '<tr><td class="dic-n">' + (i + 1) + '</td><td class="dic-v">' + esc(c.v) + '</td><td>' + esc(c.etq) +
        (c.op ? '<small class="pa-op"><b>Operación:</b> ' + esc(c.op) + '</small>' : '') + '</td><td>' + chip(c) + '</td></tr>';
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
    var ir = r.ir || f.ir, m = modoVivo(), cm = MODO_ICO[m] ? capaModo(q, r, m) : null, svDic = svDicHtml(q, r);
    var capa = cm && cm.html ? cm.html.replace(/<button\b[^>]*>[\s\S]*?<\/button>/g, '') : '';
    var resp = r.html.replace(/<details class="pa-dedonde"/g, '<details class="pa-dedonde" open');
    /* «De un vistazo» (16-11-2026): qué trae el dictamen antes de leerlo. Cuenta
       lo que ya está en la ficha; no agrega cifras ni entra a la huella. */
    var nE = { oficial: 0, derivado: 0, pendiente: 0 };
    (f.ci || []).forEach(function (c) { if (nE[c.e] != null) nE[c.e]++; });
    var xf = f.t === 'investigacion' && f.ex ? f : invToca(q, r);
    var mira = '<aside class="dic-mirada" aria-label="De un vistazo"><b class="dic-mirada-t">De un vistazo</b><dl>' +
      '<div><dt>Cifras</dt><dd>' + (f.ci || []).length + '</dd></div>' +
      ['oficial', 'derivado', 'pendiente'].filter(function (e) { return nE[e]; }).map(function (e) {
        return '<div><dt>' + chip({ e: e }) + '</dt><dd>' + nE[e] + '</dd></div>'; }).join('') +
      '<div><dt>Documentos citados</dt><dd>' + (f.fu || []).length + '</dd></div>' +
      (f.cot && f.cot.length ? '<div><dt>Afirmaciones cotejadas</dt><dd>' + f.cot.length + '</dd></div>' : '') +
      (xf ? '<div class="dic-mirada-exp"><dt>Expediente</dt><dd>' + esc(xf.exn) + (xf.ab ? ' · abierto' : ' · documentado') + '</dd></div>' : '') +
      '</dl></aside>';
    /* La tira por fuente: cada capítulo de «La revisión completa» con su estado tal como lo da su
       respuesta (sin calificar: «Sin coincidencias», «Tiene contratos publicados»…). */
    var caps = ((r.integ && r.integ.caps) || []).slice(), varios = r.integ && r.integ.rfcs.length > 1;
    /* La fuente que contestó la pregunta también va en la tira, con lo que dijo su respuesta. */
    if (r.integ && r.integ.ya) {
      var yaR = r.integ.ya, rt = textoDe(r.html);
      if (yaR.padron) caps.unshift(['🛡️', 'Listas del SAT, sancionados y sanciones internacionales', '', r.integ.rfcs[0],
        /Sin coincidencias/.test(rt) ? 'Sin coincidencias' : 'Coincidencias por revisar', !/Sin coincidencias/.test(rt)]);
      else if (yaR.cmx) caps.unshift(['🏛️', 'Contratos con el gobierno (ComprasMX)', '', r.integ.rfcs[0], 'Tiene contratos publicados', false]);
      else if (yaR.grupo) caps.unshift(['🏢', 'Su grupo empresarial', '', r.integ.rfcs[0], (r.ficha.tit || '').replace(/^Grupo empresarial: /, ''), false]);
    }
    var tira = caps.length ? '<div class="dic-tira" aria-label="Verificación por fuente">' + caps.map(function (c) {
      return '<div class="dic-tira-i' + (c[5] ? ' dic-tira-ojo' : '') + '"><span class="dic-tira-ico" aria-hidden="true">' + c[0] + '</span>' +
        '<b>' + esc(c[1]) + (varios ? ' <code>' + esc(c[3]) + '</code>' : '') + '</b><span>' + esc(c[4] || '') + '</span></div>'; }).join('') + '</div>' : '';
    /* Los hallazgos clave: las primeras cifras de la ficha, con su estado; la tabla completa sigue abajo. */
    var clave = (f.ci || []).slice(0, 4).map(function (c) {
      return '<div class="dic-clave-i"><b class="dic-clave-v">' + esc(c.v) + '</b><span>' + esc(c.etq) + '</span>' + chip(c) + '</div>'; }).join('');
    var ejecutivo = (tira || clave) ? '<section class="dic-ejecutivo" aria-label="Resumen ejecutivo">' +
      (tira ? '<p class="dic-ejecutivo-t">Verificación por fuente</p>' + tira : '') +
      (clave ? '<p class="dic-ejecutivo-t">Hallazgos clave</p><div class="dic-clave">' + clave + '</div>' +
        ((f.ci || []).length > 4 ? '<p class="dic-chico">Y ' + ((f.ci || []).length - 4) + ' cifras más en «Hallazgos: las cifras».</p>' : '') : '') + '</section>' : '';
    var expCap = xf ? '<p>Esta respuesta toca una de las grandes investigaciones de la plataforma. Su expediente, <b>' + esc(xf.exn) + ' · ' + esc(xf.tit) + '</b>, ' +
      'junta el caso en cinco preguntas, su bitácora, lo que sigue y lo que falta' + (xf.nov ? '; el último registro de su bitácora es del ' + esc(xf.nov) : '') + '. ' +
      '<a href="' + esc(xf.ex) + '">Abrir el expediente ➔</a></p>' +
      '<p>Este dictamen es una de sus piezas: el expediente junta los dictámenes del caso bajo su propio folio (<b>' + esc(xf.fo) + '</b>), como una sola investigación.</p>' +
      '<p class="dic-chico">El expediente se arma solo con la base de la plataforma; no forma parte de la huella de este dictamen.</p>' : '';
    return '<article class="pa-nota dic-doc">' +
      '<header class="dic-cab"><div class="dic-cab-marca"><img src="' + LOGO + '" alt="" width="62" height="48">' +
      '<div><b>Auditavisión</b><small>Plataforma ciudadana de fiscalización del gasto público</small></div></div>' +
      '<div class="dic-sello">' + sello(null, 'DICTAMEN') + '</div>' +
      '<div class="dic-cab-tx"><span class="pa-nota-tipo">Dictamen cívico independiente · ' + esc(t[1]) + (capa ? ' · ' + MODO_ICO[m] + ' Modo ' + MODO_NOM[m] : '') + '</span>' +
      '<dl><div class="dic-cab-q"><dt>Consulta</dt><dd>' + esc(q.length > 120 ? q.slice(0, 118) + '…' : q) + '</dd></div>' +
      '<div><dt>Folio</dt><dd class="pa-folio">calculando…</dd></div><div><dt>Expedido</dt><dd>' + esc(hoy()) + '</dd></div>' +
      '<div><dt>Huella SHA-256</dt><dd class="dic-huella-c"><code>calculando…</code></dd></div>' +
      '<div><dt>Versión de la plataforma</dt><dd>' + esc(selloSitio()) + '</dd></div></dl></div></header>' +
      '<h2 class="dic-tit"><span aria-hidden="true">' + t[0] + '</span> ' + esc(f.tit) + '</h2>' + mira + ejecutivo +
      cap('Planteamiento') + '<p class="pa-nota-q"><span>La pregunta</span> «' + esc(q) + '»</p>' +
      (antes.length ? '<p class="dic-chico">Se hizo en la plática después de: ' + antes.map(function (x) { return '«' + esc(x) + '»'; }).join(' → ') + '.</p>' : '') +
      cap('Respuesta del Auditor') + '<div class="dic-resp">' + resp + '</div>' +
      (r.integ ? capD('La revisión completa', '<p class="dic-chico">Todo lo que la base de la plataforma tiene de ' + esc(r.integ.rfcs.join(', ')) +
        ', reunido solo: sus cifras y sus fuentes están en los hallazgos y en el fundamento, y entran a la huella.</p><div class="dic-resp">' + r.integ.html.replace(/<button\b[^>]*>[\s\S]*?<\/button>/g, '') + '</div>') : '') +
      (capa ? capD('La lectura del modo ' + MODO_NOM[m],
        '<p class="dic-chico">Pediste el dictamen en el modo ' + MODO_NOM[m] + ': esta es su forma de leer la misma respuesta. El modo cambia cómo se cuenta, nunca los datos: no agrega cifras y no entra a la huella.</p>' +
        '<div class="dic-resp dic-modo">' + capa + '</div>') : '') +
      (f.txt && f.t !== 'calculo' ? '<p class="pa-nota-tx"><b>La ficha completa:</b> ' + esc(f.txt) + '</p>' : '') +
      (ci ? cap('Hallazgos: las cifras') + '<div class="dic-tabla"><table><thead><tr><th>#</th><th>Cifra</th><th>Qué es</th><th>Estado</th></tr></thead><tbody>' + ci + '</tbody></table></div>' : '') +
      (f.cot && f.cot.length && charla ? capD('Cotejo de lo que circula',
        '<p class="dic-chico">Cada afirmación que circula se comparó con el documento oficial. «Consta» quiere decir que el documento la sostiene; «con matices», que la sostiene en parte; «sin documento oficial», que solo la dice la prensa o las redes, y no la afirmamos ni la negamos.</p>' +
        charla.cotejo(f, true)) : '') +
      (f.app ? cap('La aplicación y tu resultado') + '<p>La cuenta la hace <b>«' + esc(f.app.n) + '»</b>' + (f.app.par ? ', con lo que escribiste en la plática' : '') + '. ' +
        'Para ver el resultado, o para que otra persona lo compruebe, abre la aplicación desde este enlace: <a href="' + esc(f.app.url) + '">' + esc(f.app.pag) + (f.app.par ? ' con tus datos' : '') + ' ➔</a>.</p>' +
        '<p class="dic-chico">La aplicación calcula con la base de la plataforma vigente, así que con el mismo enlace y la misma versión da el mismo resultado.</p>' : '') +
      (pend ? cap('Lo que falta') + pend : '') +
      (expCap ? capD('Expediente relacionado', expCap) : '') +
      (svDic ? cap('Lo que ya revisamos') + svDic : '') +
      capD('Fundamento documental', fu ? '<ol class="dic-fuentes">' + fu + '</ol>' + (f.app && f.app.mas ? '<p class="dic-chico">Y ' + f.app.mas + ' documentos más, citados en la página de la aplicación.</p>' : '') : '<p>Esta respuesta no cita cifras: lleva a una página de la plataforma, donde cada dato trae su fuente.</p>') +
      capD('Método', '<ol class="dic-metodo">' +
      '<li><b>Localización.</b> El Auditor buscó la respuesta en la base de la plataforma (' + B.fichas.length.toLocaleString('es-MX') + ' fichas), que solo guarda datos ya publicados con su documento.</li>' +
      '<li><b>Verificación.</b> Cada cifra se toma del documento oficial que se cita, sin estimar ni redondear a ojo. Las cuentas se hacen con cifras oficiales y se dice la operación.</li>' +
      (clas.length ? '<li><b>Clasificación.</b> Cada dato lleva su estado:<ul class="dic-clas">' + clas.join('') + '</ul></li>' : '') +
      '<li><b>Integridad.</b> La huella digital (SHA-256) se calcula sobre la ficha y la versión de la plataforma: si cambia una letra, cambia la huella.</li></ol>') +
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
        body: JSON.stringify({ pregunta: String(q).slice(0, 600), motivo: motivo === 'noera' ? 'noera' : 'sin', ficha: tit || null, version: selloSitio(),
          modo: MODO_ICO[modoVivo()] ? modoVivo() : null, modo_toca: modoSugerido(q, true) })
      }).catch(function () {});
    } catch (e) {}
  }
  /* La IA del Auditor (02-11-2026, decisión del autor). Cuando la base no
     contesta, el lector puede pedir que la IA redacte con las fichas más
     cercanas (función auditor-ia): solo ve esas fichas, cada cifra de su
     respuesta se coteja contra ellas en la función y, si una no aparece, no
     se muestra nada. Es a pedido, con botón, para cuidar el gasto. Y con un
     nombre que la plataforma no tiene, «Buscar ahora» (buscar-web) trae solo
     enlaces de sitios oficiales y de la lista de prensa, sin verificar. */
  var funcionBase = funcionBot ? funcionBot.replace(/\/pregunta-bot$/, '') : '';
  function idsIa(q) {
    return buscar(q).slice(0, 8).map(function (x) { return F.indexOf(x.f); }).filter(function (i) { return i >= 0 && i < N0; });
  }
  function iaHtml(q) {
    if (!funcionBase || !idsIa(q).length) return '';
    return '<div class="pa-rec pa-ia"><p class="pa-mas-t">Pídeselo a la IA</p>' +
      '<p class="pa-chico">Una inteligencia artificial puede redactarte una respuesta <b>solo con las fichas más cercanas de la plataforma</b>. ' +
      'Cada cifra que escriba se coteja contra ellas; si escribe una que no está, la descartamos y no te mostramos nada.</p>' +
      '<p><button type="button" class="pa-boton pa-ia-btn" data-pa-ia="' + esc(q) + '">📝 Redáctalo con las fichas</button></p>' +
      '<div class="pa-ia-sal" aria-live="polite"></div></div>';
  }
  function parrafos(t) {
    return String(t).split(/\n\s*\n/).map(function (x) { return x.trim(); }).filter(Boolean)
      .map(function (x) { return '<p>' + esc(x).replace(/\n/g, '<br>') + '</p>'; }).join('');
  }
  function postea(nombre, cuerpo) {
    return fetch(funcionBase + '/' + nombre, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) })
      .then(function (r) { return r.json().catch(function () { return { ok: false }; }); });
  }
  function pideIa(bt) {
    var q = bt.getAttribute('data-pa-ia'), sal = bt.closest('.pa-ia').querySelector('.pa-ia-sal'), ids = idsIa(q);
    if (!ids.length || !window.fetch) return;
    bt.disabled = true;
    sal.innerHTML = '<p class="pa-chico">Redactando con ' + ids.length + ' fichas de la plataforma…</p>';
    postea('auditor-ia', { pregunta: q.slice(0, 600), fichas: ids, version: selloSitio() }).then(function (j) {
      if (j && j.ok) {
        var fu = (j.fuentes || []).map(function (x) {
          var ir = x.ir && x.ir[0] ? ' · <a href="' + esc(x.ir[0]) + '">' + esc(x.ir[1] || 'Saber más') + '</a>' : '';
          return '<li><b>' + esc(x.tit) + '</b>' + ir + '</li>';
        }).join('');
        sal.innerHTML = '<div class="pa-resp">' + parrafos(j.respuesta) + '</div>' +
          (fu ? '<p class="pa-mas-t">De dónde sale</p><ul class="pa-ia-fu">' + fu + '</ul>' : '') +
          '<p class="pa-chico">📝 ' + esc(j.aviso || 'Redactado por inteligencia artificial solo con fichas de la plataforma.') + '</p>';
        bt.hidden = true;
      } else {
        var m = j && j.rechazo === 'cifra_no_respaldada' ? 'La IA escribió una cifra que no está en las fichas, así que la descartamos. Prefiero no darte nada antes que un dato sin documento.'
          : j && j.rechazo ? 'La IA no pudo darte una respuesta que cumpla nuestras reglas. Prueba con otras palabras.'
          : (j && j.error) || 'La IA no respondió ahora. El Auditor sigue contestando con su base.';
        sal.innerHTML = '<p class="pa-chico">' + esc(m) + '</p>';
        bt.disabled = false;
      }
      guarda();
    }, function () { sal.innerHTML = '<p class="pa-chico">No hubo conexión con la IA. Intenta más tarde.</p>'; bt.disabled = false; });
  }
  function webVivoHtml(nombre) {
    if (!funcionBase) return '';
    return '<p><button type="button" class="pa-boton pa-web-btn" data-pa-web="' + esc(nombre) + '">🔎 Buscar ahora en sitios oficiales y prensa</button></p>' +
      '<div class="pa-web-sal" aria-live="polite"></div>';
  }
  function pideWeb(bt) {
    var n = bt.getAttribute('data-pa-web'), sal = bt.parentNode.nextElementSibling;
    if (!window.fetch || !sal) return;
    bt.disabled = true;
    sal.innerHTML = '<p class="pa-chico">Buscando «' + esc(n) + '»…</p>';
    postea('buscar-web', { nombre: n }).then(function (j) {
      if (j && j.ok) {
        sal.innerHTML = (j.enlaces || []).length ? '<div class="pa-rec-lista">' + j.enlaces.map(function (e) {
          return '<a class="pa-rec-a" href="' + esc(e.url) + '" target="_blank" rel="noopener noreferrer"><span class="pa-rec-ico" aria-hidden="true">' + (e.tipo === 'oficial' ? '🏛️' : '📰') + '</span>' +
            '<span><b>' + esc(e.titulo) + '</b><small>' + esc(e.sitio) + (e.tipo === 'oficial' ? ' · oficial' : ' · prensa, sin verificar') + (e.fecha ? ' · ' + esc(e.fecha) : '') + ' ↗</small></span></a>';
        }).join('') + '</div><p class="pa-chico">' + esc(j.aviso || '') + '</p>' : '<p class="pa-chico">No encontré enlaces en los sitios de la lista. Usa las búsquedas de arriba.</p>';
        bt.hidden = true;
      } else {
        sal.innerHTML = '<p class="pa-chico">' + esc((j && j.error) || 'El buscador no respondió. Usa las búsquedas de arriba.') + '</p>';
        bt.disabled = false;
      }
      guarda();
    }, function () { sal.innerHTML = '<p class="pa-chico">No hubo conexión. Usa las búsquedas de arriba.</p>'; bt.disabled = false; });
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
    else { l.unshift({ q: q, m: motivo, t: tit || '', f: hoy, n: 1, mo: modoVivo() || '' }); reporta(q, motivo, tit); }
    guardaLista(l.slice(0, MAX));
    pintaLista();
  }
  function textoLista(l) {
    return 'Preguntas que el bot de Auditavisión no supo contestar\n' + l.map(function (o, i) {
      return (i + 1) + '. «' + o.q + '» · ' + (o.m === 'noera' ? 'la nota no respondía' + (o.t ? ' (dio: ' + o.t + ')' : '') : 'sin respuesta') +
        (o.mo && MODO_NOM[o.mo] ? ' · modo ' + MODO_NOM[o.mo] : '') + ' · ' + o.f + (o.n > 1 ? ' · ' + o.n + ' veces' : '');
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
  /* El dictamen sale con la forma del modo elegido (entrega c, 04-11-2026): el
     enlace lleva &modo=, la página vuelve a contestar con la misma base y suma la
     capa del modo como un capítulo. El modo no cambia los datos ni la huella. */
  function enlaceDictamen(q, previas) {
    var m = modoVivo();
    return DICTAMEN + '?q=' + encodeURIComponent(q) + previas.map(function (c) { return '&c=' + encodeURIComponent(c); }).join('') +
      (MODO_ICO[m] ? '&modo=' + m : '');
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
      (r.ficha ? '<a class="pa-boton pa-genera" href="' + esc(enlaceDictamen(q, previas || []) + (r.abre ? '&abre=' + encodeURIComponent(r.abre) : '')) + '" target="_blank" rel="noopener">🧾 Generar dictamen</a>' : '') +
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
  /* El Planisferio es la matriz de los mapas (pedido del autor, 04-11-2026:
     «que todo quedara en una misma línea… el planisferio va a ser nuestra
     matriz»). Los mapas que viven en el Planisferio (pl, que escribe
     asistente_recursos.py) no salen como tarjetas sueltas: se juntan en un
     solo renglón que abre el Planisferio en su dimensión, con las otras
     dimensiones al lado. Los que todavía no tienen par allá siguen como tarjeta. */
  function ligaPl(x, ab) { return ab && x.ple ? x.ple.replace('%s', encodeURIComponent(ab)) : x.pl; }
  function destinoRec(x, ab) { return x.pl ? ligaPl(x, ab) : ligaRec(x, ab); }
  function sinRepetirPl(lista) {
    var vistos = {};
    return lista.filter(function (o) {
      var x = o.x || o, k = x.pl ? 'pl:' + (x.plk || x.pl) : 'ir:' + x.ir;
      if (vistos[k]) return false;
      vistos[k] = 1;
      return true;
    });
  }
  function lineaPl(pls) {
    if (!pls.length) return '';
    var p = pls[0], ab = p.ab, que = p.x.pll ? 'Dimensión ' + p.x.pll.charAt(0).toLowerCase() + p.x.pll.slice(1) : p.x.n;
    return '<div class="pa-pl"><a class="pa-pl-a" href="' + esc(ligaPl(p.x, ab)) + '"><span class="pa-rec-ico" aria-hidden="true">🗺️</span>' +
      '<span><b>Ver en el Planisferio</b><small>' + esc(que) + (ab && p.x.ple ? ' · ' + esc(NOMBRE[ab]) : '') + '</small></span></a>' +
      (pls.length > 1 ? '<span class="pa-pl-mas"><span class="pa-pl-t">También ahí:</span>' + pls.slice(1).map(function (o) {
        return '<a class="pa-pl-chip" href="' + esc(ligaPl(o.x, o.ab)) + '">' + esc(o.x.pll || o.x.v) + '</a>';
      }).join('') + '</span>' : '') + '</div>';
  }
  /* Una tarjeta armada a mano (las megaobras de un estado, por ejemplo) que
     lleva a un mapa con par en el Planisferio toma ese par: se busca en el
     catálogo por su archivo y su lente (?l=), y el estado sale de su ?e=. */
  function lenteDe(u) { var m = /[?&]l=([A-Za-z]+)/.exec(String(u)); return m ? m[1] : ''; }
  function conPl(o) {
    if (!o || !o.x || o.x.pl || !o.x.ir) return o;
    var par = null;
    REC.forEach(function (r) { if (!par && r.pl && sinParam(r.ir) === sinParam(o.x.ir) && lenteDe(r.ir) === lenteDe(o.x.ir)) par = r; });
    if (!par) return o;
    var m = /[?&]e=([A-Za-z]+)/.exec(o.x.ir), ab = o.ab || (m && NOMBRE[m[1]] ? m[1] : null), x = {};
    Object.keys(o.x).forEach(function (k) { x[k] = o.x[k]; });
    ['pl', 'ple', 'pld', 'pll', 'plk'].forEach(function (k) { x[k] = par[k]; });
    return { x: x, ab: ab };
  }
  function recursosHtml(lista) {
    lista = sinRepetirPl((lista || []).map(conPl));
    var pls = lista.filter(function (o) { return o.x.pl; });
    lista = lista.filter(function (o) { return !o.x.pl; });
    var linea = lineaPl(pls);
    return linea || lista.length ? '<div class="pa-rec"><p class="pa-mas-t">Explóralo a fondo</p>' + linea + (lista.length ? '<div class="pa-rec-lista">' + lista.map(function (o) {
      return '<a class="pa-rec-a" href="' + esc(ligaRec(o.x, o.ab)) + '"><span class="pa-rec-ico" aria-hidden="true">' + o.x.ico + '</span>' +
        '<span><b>' + esc(o.x.v) + '</b><small>' + esc(o.x.n) + (o.ab && o.x.ire ? ' · ' + esc(NOMBRE[o.ab]) : '') + '</small></span></a>';
    }).join('') + '</div>' : '') + '</div>' : '';
  }
  /* La Enciclopedia es la base de datos física del Auditor (pedido del autor,
     29-10-2026): al pie de cada respuesta van las páginas de la Enciclopedia
     que tocan el tema, primero las del modo elegido. El orden cambia con el
     modo; los datos, nunca. Una página cuyo título está completo en la
     pregunta va primero; las demás, solo si tocan el tema de cerca. */
  var MODO_ICO = { inspector: '🔍', periodista: '📰', ciudadano: '🙋', ambientalista: '🌎' };
  var MODO_DIC = '';
  function modoVivo() { var a = document.getElementById('paApp'); return a ? a.getAttribute('data-modo') : MODO_DIC; }
  function enciclopediaPara(q, r) {
    if (!r || r.sin || r.plat) return [];
    var ir = r.ir || (r.ficha && r.ficha.ir), base = ir ? sinParam(ir[0]) : '', pq = plano(q), modo = modoVivo();
    var vistos = {}, out = [];
    if (base) vistos[base] = 1;
    var res = buscar(q), piso = Math.max(6, res.length ? res[0].s * 0.4 : 0);
    res.slice(0, 40).forEach(function (x) {
      var f = x.f, pg = f.ir && sinParam(f.ir[0]);
      if (!f.e || !pg || vistos[pg]) return;
      var tit = plano(f.t === 'pagina' ? f.tit : f.ir[1] || ''), exacto = tit.trim().length > 2 && pq.indexOf(tit) >= 0;
      if (!exacto && x.s < piso) return;
      vistos[pg] = 1;
      out.push({ f: f, s: x.s * (exacto ? 3 : 1) * (f.m === modo ? 1.3 : 1) });
    });
    out.sort(function (a, b) { return b.s - a.s; });
    return out.slice(0, 3).map(function (o) { return o.f; });
  }
  function enciclopediaHtml(lista) {
    return lista.length ? '<div class="pa-rec pa-enc"><p class="pa-mas-t">📚 En la Enciclopedia</p><div class="pa-rec-lista">' + lista.map(function (f) {
      var m = f.m || 'inspector';
      return '<a class="pa-rec-a" href="' + esc(f.ir[0]) + '" data-modo="' + esc(m) + '"><span class="pa-rec-ico" aria-hidden="true">' + MODO_ICO[m] + '</span>' +
        '<span><b>' + esc(f.tit) + '</b><small>' + (f.t === 'pagina' ? 'Página' : 'En «' + esc(f.ir[1]) + '»') + ' · Modo ' + esc(m.charAt(0).toUpperCase() + m.slice(1)) + '</small></span></a>';
    }).join('') + '</div></div>' : '';
  }
  /* El modo Periodista (pedido del autor, 29-10-2026: «el reportero se
     convierte como en un chismoso… te transmite información privilegiada»).
     Bajo la misma respuesta, arma su nota con lo que casi nadie cuenta, pero
     sacado de documentos: lo que la ASF dejó por aclarar, lo que ninguna
     dependencia ha publicado (con su nombre), lo que circula y qué consta, y lo
     que sigue. No agrega cifras ni rumores: todo sale de la base, y lo que no
     tiene documento se dice así. */
  function recorta(t, n) { t = String(t || ''); return t.length > n ? t.slice(0, n).replace(/\s+\S*$/, '') + '…' : t; }
  function temaDe(r) {
    var t = (r.ficha && r.ficha.tit) || '';
    t = t.split(/[:(]| — | · /)[0].replace(/^Cuánto gana\s*/i, '').trim();
    return t.split(' ').length <= 6 ? t : '';
  }
  var VER_P = window.AuditorVerifica && B.dat && B.dat.nota ? window.AuditorVerifica(B.dat.nota) : null;
  function periodista(q, r) {
    if (!r || r.sin || r.plat) return null;
    var sc = svCapa(r, 'periodista');
    if (sc) return sc;
    var f0 = r.ficha, tema = temaDe(r), res = buscar(q), piso = Math.max(5, res.length ? res[0].s * 0.35 : 0);
    var cerca = res.slice(0, 30).filter(function (x) { return x.s >= piso; }).map(function (x) { return x.f; });
    if (f0 && cerca.indexOf(f0) < 0) cerca.unshift(f0);
    /* Un concepto («¿qué es el Ramo 33?») se busca también por su nombre a secas. */
    if (tema && plano(tema) !== plano(q)) {
      var rt = buscar(tema), pt = Math.max(5, rt.length ? rt[0].s * 0.35 : 0);
      rt.slice(0, 30).forEach(function (x) { if (x.s >= pt && cerca.indexOf(x.f) < 0) cerca.push(x.f); });
    }
    /* Las columnas y los pendientes tienen que tocar el tema de cerca: la mitad del puntaje de la mejor ficha. */
    var fuerte = [];
    [res, tema && plano(tema) !== plano(q) ? buscar(tema) : []].forEach(function (rs) {
      rs.slice(0, 30).forEach(function (x) { if (x.s >= Math.max(6, rs[0].s * 0.5)) fuerte.push(x.f); });
    });
    /* Y una columna, además, tiene que traer la mitad de las palabras de la pregunta (o el tema): «oficina» no basta para el INE. */
    var ws = fichas(q).filter(function (w) { return w.length > 3; }), wt = tema ? fichas(tema) : [];
    function hablaDe(f) {
      var t = plano(f.tit + ' ' + (f.k || '') + ' ' + (f.txt || '') + ' ' + (f.cir ? f.cir.tx : ''));
      var h = ws.filter(function (w) { return t.indexOf(' ' + w + ' ') >= 0; }).length, ht = wt.filter(function (w) { return t.indexOf(' ' + w + ' ') >= 0; }).length;
      return (ws.length && h * 2 >= ws.length) || (wt.length && ht === wt.length);
    }
    var cols = cerca.filter(function (f) { return f.t === 'columna' && (f === f0 || (fuerte.indexOf(f) >= 0 && hablaDe(f))); }).slice(0, 2);
    /* Primero, lo que falta en la página misma de la respuesta. */
    var base = (r.ir || (f0 && f0.ir) || [''])[0].split('#')[0].split('?')[0];
    var pends = F.filter(function (f) { return f.t === 'pendiente' && f.pend && base && (f.pend.ap || []).indexOf(base) >= 0 && (!/^(noticias-|pendientes\.html|indice\.html)/.test(base) || hablaDe(f)); }).slice(0, 2);
    cerca.forEach(function (f) { if (pends.length < 2 && f.t === 'pendiente' && f.pend && fuerte.indexOf(f) >= 0 && pends.indexOf(f) < 0 && (!r.lect || hablaDe(f))) pends.push(f); });
    var exps = cerca.filter(function (f) { return f.t === 'expediente'; }).slice(0, 1);
    var nadie = [], iv = invDe(q, r);
    /* Nepotismo (pedido del autor, 29-10-2026): lo que la ley todavía no alcanza, y la regla del apellido. */
    if (base === 'herramienta-inspector-nepotismo.html') nadie.push('<li>🔦 <b>Los puntos ciegos:</b> la prohibición del nepotismo electoral se aplica a partir de las elecciones de 2030, el «yo contrato a tu sobrino y tú a mi hija» entre dependencias no es el caso del art. 63 Bis, y los datos de la familia en la declaración están en reserva. <a href="herramienta-inspector-nepotismo.html#puntos-ciegos">Ver los puntos ciegos ➔</a> Y ojo: <b>un apellido igual nunca es prueba de parentesco</b>; un vínculo entra a la plataforma solo si lo dice un documento oficial.</li>');
    if (base === 'periodismo-en-riesgo.html') nadie.push('<li>🛡️ <b>Lo que registran Gobernación y la FEADLE:</b> 40.7 % de los probables agresores señalados ante el Mecanismo son servidores públicos (374 de 918), y de 2000 a septiembre de 2026 la FEADLE registra 110 homicidios de periodistas, 1,940 indagatorias y 53 sentencias condenatorias. <a href="periodismo-en-riesgo.html#pr-feadle">Ver cifras de la FEADLE ➔</a></li>');
    if (iv) nadie.push('<li>📖 <b>Lo investigamos a fondo:</b> <a href="' + esc(iv.x.ir) + '">' + esc(iv.x.n) + ' ➔</a>, en Auditoría en imágenes.</li>');
    exps.forEach(function (f) {
      nadie.push('<li>📂 <b>La ASF lo dejó por aclarar.</b> ' + esc(recorta(f.txt, 220)) + ' <a href="' + esc(f.ir[0]) + '">Ver el expediente ➔</a></li>');
    });
    pends.forEach(function (f) {
      /* Si la falta es de la plataforma, se dice así, sin culpar a nadie (AGENTS.md §2). */
      var nuestra = /falta de la plataforma/i.test((f.pend.quien || '') + ' ' + (f.pend.pq || ''));
      nadie.push('<li>' + chip({ e: 'pendiente', p: f.pend.id }) + (nuestra ? ' <b>Aún no lo integramos:</b> ' : ' <b>Falta el documento:</b> ') + esc(recorta(f.tit, 140)) + '. ' +
        (f.pend.quien && !nuestra ? 'Le toca publicarlo a <b>' + esc(f.pend.quien) + '</b>. ' : '') + esc(recorta(f.pend.pq, 160)) +
        (f.pend.donde ? ' <a href="' + esc(f.pend.donde) + '" target="_blank" rel="noopener">Dónde debería estar ↗</a>' : '') + '</li>');
    });
    cols.forEach(function (f) {
      (f.cot || []).filter(function (c) { return c.r === 'no consta' || c.r === 'matiz'; }).slice(0, 1).forEach(function (c) {
        nadie.push('<li><span class="pa-cot-r">' + (c.r === 'matiz' ? '⚠️ Consta, con matices' : '❌ Sin documento oficial') + '</span> <b>Se dice que</b> «' + esc(recorta(c.d, 120)) + '». ' + esc(recorta(c.x, 200)) +
          (c.fu && c.fu.url ? ' <a href="' + esc(c.fu.url) + '" target="_blank" rel="noopener">' + esc(recorta(c.fu.tx, 70)) + ' ↗</a>' : '') + '</li>');
      });
    });
    var ruido = cols.map(function (f) {
      var n = {};
      (f.cot || []).forEach(function (c) { n[c.r] = (n[c.r] || 0) + 1; });
      var cuenta = ['consta', 'matiz', 'no consta', 'pendiente'].filter(function (k) { return n[k]; }).map(function (k) { return n[k] + ' ' + k; }).join(' · ');
      return '<li>📰 <a href="' + esc(f.ir[0]) + '"><b>' + esc(f.tit) + '</b></a>' +
        (f.cir && f.cir.tx ? '<br><small><b>Lo que circula:</b> «' + esc(recorta(f.cir.tx, 160)) + '»' + (f.cir.q ? ' (' + esc(recorta(f.cir.q, 90)) + ')' : '') + '</small>' : '') +
        (cuenta ? '<br><small><b>Nuestro cotejo:</b> ' + esc(cuenta) + '</small>' : '') + '</li>';
    });
    var sigue = [];
    cols.forEach(function (f) { (f.sigue || []).slice(0, 2 - sigue.length).forEach(function (s) { sigue.push('<li>🗓️ ' + (s.url ? '<a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.tx) + ' ↗</a>' : esc(s.tx)) + '</li>'); }); });
    if (r.lect && r.lead && r.lead.length) nadie.unshift('<li>📰 <b>La nota, en una línea:</b> ' + esc(r.lead.join(', y ')) + '. Eso es lo que casi ningún titular dice.</li>');
    var nada = !nadie.length && !ruido.length, cie = [];
    /* Sin nota (19-11-2026, afinación por modo): una herramienta o una página de la plataforma no es
       tema de nota, así que no se ofrece una; en lo demás, el Periodista enseña qué preguntar si el tema
       sale en la prensa, con los puntos ciegos (puntos_ciegos.py) que toca la respuesta. */
    if (nada && (r.app || /^(donaciones|canjea|mis-respuestas|indice|derecho-de-replica|noticias-|participa|comunidad)/.test(base) || base === 'herramienta-inspector.html' || (base === 'glosario.html' && !/#(?!terminos)/.test((r.ir || [''])[0])))) return null;
    if (nada && VER_P) {
      var vistoC = {};
      /* En un concepto (glosario, Aprende) no se acusa a nadie: ahí sobra «una acusación no es una condena». */
      var concepto = /^(glosario|aprende-)/.test(base);
      cie = VER_P.ciegos({ texto: q + '\n' + textoDe(r.html) }).filter(function (c) {
        return !(concepto && c.r.id === 'acusacion') && !vistoC[c.r.id] && (vistoC[c.r.id] = 1);
      }).slice(0, 2);
    }
    var h = '<div class="pa-reportero"><p class="pa-rep-t">📰 La nota del Periodista</p>' +
      (nadie.length ? '<p class="pa-rep-s">🕵️ Lo que casi nadie te cuenta</p><ul class="pa-lista">' + nadie.slice(0, 4).join('') + '</ul>' : '') +
      (ruido.length ? '<p class="pa-rep-s">📢 El ruido: lo que circula y lo que consta</p><ul class="pa-lista">' + ruido.join('') + '</ul>' : '') +
      (sigue.length ? '<p class="pa-rep-s">🗓️ Lo que sigue</p><ul class="pa-lista">' + sigue.join('') + '</ul>' : '') +
      (nada && cie.length ? '<p class="pa-rep-s">🔦 Si lo lees en una nota, pregunta</p><ul class="pa-lista">' + cie.map(function (c) {
        return '<li>' + esc(c.r.ico) + ' <b>' + esc(c.r.n) + '.</b> ' + esc(c.r.pr) + '</li>';
      }).join('') + '</ul><p class="pa-chico">Son los <a href="noticias-verifica.html#puntos-ciegos">puntos ciegos</a> que las notas suelen esconder: preguntas que conviene hacer, no un juicio sobre nadie. ¿Quieres que lo investiguemos? <a href="noticias-verifica.html#propon">Propón una nota ➔</a></p>' : '') +
      (nada && !cie.length ? '<p>En la redacción todavía no hay nota sobre esto: no tenemos cotejo de lo que circula ni pendientes señalados. <a href="noticias-verifica.html#propon">¿Lo investigamos? Propón una nota ➔</a></p>' : '') +
      '<p class="pa-chico">Lo que te cuento sale de documentos públicos que casi nadie lee, no de rumores. Una nota de prensa es mi punto de partida, nunca mi fuente' +
      (cols.length ? ', y <b>una acusación no es una condena</b>' : '') + '. A las personas privadas no las nombro.</p></div>';
    return { html: h, web: !r.web && tema ? tema : '' };
  }
  function periodistaHtml(q, r) {
    if (modoVivo() !== 'periodista') return '';
    var n = periodista(q, r);
    return n ? n.html + (n.web ? webHtml(n.web) : '') : '';
  }
  /* Cada modo contesta a su manera (pedido del autor, 29-10-2026, entrega b;
     hecha el 04-11-2026). Bajo la misma respuesta, cada modo suma su capa:
     el Inspector, de qué está hecha y por dónde seguir; el Ciudadano, la
     respuesta en una línea y sus palabras difíciles; el Ambientalista, los
     proyectos con alerta ambiental del tema y quién los paga. Ninguna capa
     agrega cifras: todo sale de la respuesta y de la base. */
  /* Los servicios en cada modo (19-11-2026, pedido del autor: «afinación de las
     respuestas por modo»). Bajo la respuesta de un servicio, cada modo suma lo que
     le toca, sin montos ni cifras: el Inspector, cómo revisarlo por tu cuenta y lo
     que un encargo no es; el Periodista, el compromiso de independencia de su
     familia; el Ciudadano, en una línea y con qué empezar gratis; el Ambientalista,
     dónde ver lo ambiental, porque ningún servicio lo mide. Todo viene de
     asistente_servicios.py en las respuestas srv_* de servicios_fichas.py (D.san.t), que lo leen de apartados.py. */
  var SVT = (B.dat && B.dat.san && B.dat.san.t) || {};
  function svDe(r) {
    var ir = r && (r.ir || (r.ficha && r.ficha.ir)), u = ir ? String(ir[0]) : '', m = /^servicio-([a-z]+)\.html/.exec(u);
    if (m && SVT['srv_' + m[1]] && SVT['srv_' + m[1]].fam) return SVT['srv_' + m[1]];
    if (/^servicios(-[a-z-]+)?\.html/.test(u) && !/^servicios-por-que\.html/.test(u) && SVT.srv_revision) return { todos: 1, noes: SVT.srv_revision.noes, ind: SVT.srv_revision.ind, gr: [] };
    return null;
  }
  function svLigas(gr) {
    return (gr || []).map(function (g) { return '<li>🔓 <a href="' + esc(g[0]) + '">' + esc(g[1]) + ' ➔</a> · gratis</li>'; }).join('');
  }
  function svCapa(r, m) {
    if (!r || r.sin) return null;
    var s = svDe(r);
    if (!s) return null;
    var nom = s.todos ? 'los Servicios' : '«' + esc((r.ir || [])[1] || 'este servicio') + '»', h;
    if (m === 'inspector') {
      h = '<div class="pa-capa pa-capa-inspector"><p class="pa-capa-t">🔍 La revisión del Inspector</p>' +
        '<p class="pa-rep-s">Antes de encargarlo, revísalo tú</p><ul class="pa-lista">' +
        (s.todos ? '<li>🔍 <a href="herramienta-inspector.html">Las aplicaciones del Modo Inspector ➔</a> · gratis</li>' : svLigas(s.gr)) + '</ul>' +
        (s.noes ? '<p class="pa-rep-s">Lo que un encargo no es</p><p><b>' + esc(s.noes[0]) + '</b> ' + esc(s.noes[1]) + '</p>' : '') +
        '<p class="pa-chico">Cada hallazgo de un encargo lleva su documento y una de tres etiquetas: oficial, auditada o pendiente. <a href="servicios-cotiza.html#independencia">La política de independencia ➔</a></p></div>';
    } else if (m === 'periodista') {
      h = '<div class="pa-reportero"><p class="pa-rep-t">📰 La nota del Periodista</p>' +
        '<p class="pa-rep-s">🕵️ Lo que conviene saber antes de encargar ' + nom + '</p><ul class="pa-lista">' +
        (s.ind ? '<li>⚖️ <b>' + esc(s.ind[0]) + '</b> ' + esc(s.ind[1]) + '</li>' : '') +
        (s.ind && !/^Quien encarga/.test(s.ind[0]) ? '<li>❓ <b>Quien encarga define la pregunta, no la respuesta.</b> Si los documentos no sostienen lo que esperabas, el entregable lo dice.</li>' : '') +
        (s.fam === 'electoral' ? '<li>🗓️ Cada promesa de gasto de campaña se sigue en <a href="noticias-seguimiento.html#promesas">la memoria de promesas ➔</a>, con su fecha.</li>' : '') + '</ul>' +
        '<p class="pa-chico">Lo que publica la plataforma no cambia por quién compró qué. <a href="servicios-cotiza.html#independencia">La política de independencia, completa ➔</a></p></div>';
    } else if (m === 'ciudadano') {
      h = '<div class="pa-capa pa-capa-ciudadano"><p class="pa-capa-t">🙋 En corto</p>' +
        '<p class="pa-capa-corto">' + (s.todos ? 'Los Servicios son' : 'Es') + ' trabajo de pago: una persona lo hace por ti. Lo público lo consultas gratis, siempre.</p>' +
        (s.todos ? '' : '<p class="pa-rep-s">Si quieres hacerlo tú, empieza aquí</p><ul class="pa-lista">' + svLigas(s.gr.slice(0, 2)) + '</ul>') +
        '<p>¿Dudas antes de pedirlo? Lee <a href="servicios-preguntas.html">las preguntas frecuentes ➔</a></p></div>';
    } else if (m === 'ambientalista') {
      h = '<div class="pa-capa pa-capa-ambientalista"><p class="pa-capa-t">🌎 La mirada ambiental</p>' +
        '<p>' + (s.todos ? 'Ninguno de los Servicios mide' : 'Este servicio no mide') + ' el daño ambiental: no lo vamos a presentar como si lo hiciera. Lo ambiental lo consultas gratis:</p><ul class="pa-lista">' +
        '<li>🗺️ <a href="planisferio.html?d=ambiental">La dimensión ambiental del Planisferio ➔</a>: refinerías, minas, agua del subsuelo, incendios, bosques y pesca.</li>' +
        '<li>⏱️ <a href="herramienta-ambiente-reloj.html">El reloj del daño ambiental</a> y <a href="datos-justicia-ambiental-denuncias.html">lo que resuelve la PROFEPA</a></li></ul>' +
        '<p class="pa-chico">El deterioro del ambiente también es gasto público. Si tu pregunta es ambiental, cuéntanosla en la solicitud: se cotiza como revisión o expediente.</p></div>';
    } else return null;
    return { html: h, web: '' };
  }
  function textoDe(h) { return String(h || '').replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim(); }
  function inspectorCapa(q, r) {
    if (!r || r.sin || r.plat) return null;
    var sc = svCapa(r, 'inspector');
    if (sc) return sc;
    var h = String(r.html || ''), cu = { oficial: 0, derivado: 0, pendiente: 0 };
    (h.match(/est-chip est-(oficial|derivado|pendiente)/g) || []).forEach(function (m) { cu[m.split('est-').pop()]++; });
    var f0 = r.ficha, fu = (f0 && f0.fu) || [], ab = entidadDe(q + ' ' + ((f0 && f0.tit) || ''));
    var base = (r.ir || (f0 && f0.ir) || [''])[0].split('#')[0].split('?')[0];
    var pends = F.filter(function (f) { return f.t === 'pendiente' && f.pend && base && (f.pend.ap || []).indexOf(base) >= 0; }).slice(0, 2);
    var res = buscar(q), piso = res.length ? res[0].s * 0.5 : 0;
    var exp = res.slice(0, 20).filter(function (x) { return x.f.t === 'expediente' && x.s >= piso; })[0];
    var sigue = [];
    if (ab) sigue.push('<li>🏢 <a href="herramienta-inspector-entes.html#ente=estatal:' + esc(ab) + '">La ficha técnica de ' + esc(NOMBRE[ab]) + ' en el Auditor de entes ➔</a></li>');
    if (exp) sigue.push('<li>📂 <a href="' + esc(exp.f.ir[0]) + '">Su expediente de la ASF: ' + esc(recorta(exp.f.tit, 90)) + ' ➔</a></li>');
    if (ab) sigue.push('<li>🗺️ <a href="planisferio.html?e=' + esc(ab) + '">' + esc(NOMBRE[ab]) + ' en el Planisferio, dimensión por dimensión ➔</a></li>');
    sigue.push('<li>🧾 <a href="contratos-publicos.html">Sus contratos en ComprasMX</a> y la <a href="herramienta-inspector-pregunta.html?q=' + encodeURIComponent('lista negra del SAT') + '">lista negra del SAT</a>, si hay una empresa de por medio.</li>');
    var tot = cu.oficial + cu.derivado + cu.pendiente;
    var hh = '<div class="pa-capa pa-capa-inspector"><p class="pa-capa-t">🔍 La revisión del Inspector</p>' +
      (tot ? '<p class="pa-rep-s">De qué está hecha esta respuesta</p><p>' +
        [['oficial', 'tomados de su documento'], ['derivado', 'calculados por nosotros, con su operación dicha'], ['pendiente', 'que nadie ha publicado todavía']]
          .filter(function (k) { return cu[k[0]]; }).map(function (k) { return '<b>' + cu[k[0]] + '</b> ' + chip({ e: k[0] }) + ' ' + k[1]; }).join(' · ') + '.</p>' : '') +
      (fu.length ? '<p class="pa-rep-s">Sus documentos</p><ul class="pa-lista">' + fu.slice(0, 4).map(function (d) {
        return '<li>📄 ' + (d.url ? '<a href="' + esc(d.url) + '" target="_blank" rel="noopener">' + esc(recorta(d.tx, 140)) + ' ↗</a>' : esc(recorta(d.tx, 160))) + '</li>';
      }).join('') + '</ul>' : '') +
      (pends.length ? '<p class="pa-rep-s">Lo que falta</p><ul class="pa-lista">' + pends.map(function (f) {
        return '<li>' + chip({ e: 'pendiente', p: f.pend.id }) + ' ' + esc(recorta(f.tit, 140)) + (f.pend.quien ? '. Le toca a <b>' + esc(f.pend.quien) + '</b>' : '') + '.</li>';
      }).join('') + '</ul>' : '') +
      '<p class="pa-rep-s">Para seguir investigando</p><ul class="pa-lista">' + sigue.join('') + '</ul>' +
      '<p class="pa-chico">El respaldo completo, con folio y huella, está en «Generar dictamen». Tener contratos o un expediente abierto no es una irregularidad: es por dónde se revisa.</p></div>';
    return { html: hh };
  }
  function ciudadanoCapa(q, r) {
    if (!r || r.sin || r.plat) return null;
    var sc = svCapa(r, 'ciudadano');
    if (sc) return sc;
    /* La primera oración del primer párrafo: lo demás ya está arriba. */
    var p1 = (String(r.html || '').match(/<p[^>]*>([\s\S]*?)<\/p>/) || [0, r.html])[1];
    var t = textoDe(r.html).replace(/📎.*$/, '').trim(), t1 = textoDe(p1).replace(/📎.*$/, '').trim();
    var corto = (t1.match(/^.*?[.!?](\s|$)/) || [t1])[0].trim().replace(/\s+([.,;:])/g, '$1');
    if ((r.ficha && r.ficha.t === 'glosario') || /:$/.test(corto)) corto = '';
    if (corto.length > 260) corto = recorta(corto, 240);
    var pt = ' ' + plano(t) + ' ', vistos = {}, pals = [];
    F.forEach(function (f) {
      if (pals.length >= 3 || f.t !== 'glosario') return;
      var n = plano(f.tit.split(' (')[0]).trim();
      if (n.length < 4 || vistos[n] || f === r.ficha || (' ' + plano(q) + ' ').indexOf(' ' + n + ' ') >= 0) return;
      if (pt.indexOf(' ' + n + ' ') >= 0) { vistos[n] = 1; pals.push(f); }
    });
    var hh = '<div class="pa-capa pa-capa-ciudadano"><p class="pa-capa-t">🙋 En corto</p>' +
      (corto ? '<p class="pa-capa-corto">' + esc(corto) + '</p>' : '') +
      (pals.length ? '<p class="pa-rep-s">Palabras que quizá no conoces</p><ul class="pa-lista">' + pals.map(function (f) {
        return '<li><b>' + esc(f.tit) + ':</b> ' + esc(recorta(f.txt, 150)) + ' <a href="' + esc(f.ir[0]) + '">Glosario ➔</a></li>';
      }).join('') + '</ul>' : '') +
      '<p class="pa-rep-s">¿Y a ti en qué te toca?</p><p>Con tu sueldo, tu <a href="herramienta-calculadora-ticket.html">estado de cuenta cívico</a> te dice cuánto pagas de impuestos y a dónde va cada peso. ' +
      'Si quieres ir a fondo, toca «Saber más» o cámbiame al modo Inspector.</p></div>';
    return { html: hh };
  }
  /* El puente de cada tema a su lado ambiental: [palabras, ícono, texto, página, 'q' si solo cuenta la pregunta].
     Solo páginas que ya existen. */
  var AMB_PUENTE = [
    [/ (judicial\w*|juzgad\w*|jueces|tribunal\w*|fiscalias?|denuncias?) /, '⚖️', 'La justicia ambiental: lo que la PROFEPA hace con las denuncias, su rezago y lo que lleva a la Fiscalía', 'datos-justicia-ambiental.html'],
    [/ (obras? publicas?|infraestructura|megaobras?|aeropuerto|aifa|tren|refineria|dos bocas|carreteras?|invierte\w*|inversion) /, '🏗️', 'La huella de las megaobras: cada obra con su alerta ambiental y quién la paga', 'datos-ambiente-megaobras.html'],
    [/ (presupuest\w*|ramos?|egresos|paquete economico|pef|gasto programable) /, '💰', 'El presupuesto ambiental: el Ramo 16, órgano por órgano', 'datos-ambiente-presupuesto.html'],
    [/ (pib|crecimiento|economia) /, '📉', 'El PIB que no alcanza: lo que el país produjo menos lo que le costó a la naturaleza', 'datos-ambiente-pib.html'],
    [/ (municipios?|alcald\w*|ayuntamientos?|basura|limpia) /, '🗑️', 'La basura: un servicio municipal sin dinero federal, de lo que se genera a dónde va', 'datos-ambiente-basura.html', 'q'],
    [/ (diputad\w*|senad\w*|congresos?|legislativ\w*|leyes|reformas?) /, '📜', 'Las leyes ambientales que aplican, con su texto vigente', 'datos-ambiente-leyes.html'],
    [/ (sueldo|salario|impuestos?|isr|iva|retienen|aguinaldo|deuda) /, '🧾', 'Tu estado de cuenta ambiental: tu parte del daño ambiental, junto a la de la deuda', 'herramienta-ambiente-ticket.html'],
    [/ (asf|auditoria superior|fiscalizacion|expedientes?|por aclarar|observ\w*) /, '🔎', 'El Auditor ambiental: lo que la Auditoría Superior observó a la SEMARNAT, la Conagua, la CONAFOR y la PROFEPA', 'herramienta-ambiente-auditor.html'],
    [/ (huracan\w*|inundacion\w*|sequia|crisis|desastres?|fonden) /, '🌀', 'Las crisis ambientales: cuánto cubre el fondo, cuánto se anunció y cuánto se comprobó', 'herramienta-ambiente-crisis.html']
  ];
  function ambientalistaCapa(q, r) {
    if (!r || r.sin || r.plat) return null;
    var sc = svCapa(r, 'ambientalista');
    if (sc) return sc;
    var casos = MO.casosAmb || [], ab = entidadDe(q + ' ' + ((r.ficha && r.ficha.tit) || '')), pt = ' ' + plano(q + ' ' + textoDe(r.html)) + ' ';
    var os = casos.filter(function (c) {
      if (ab && (c.edos || []).indexOf(ab) >= 0) return true;
      var w = plano(c.nombre).trim().split(' ').filter(function (x) { return x.length > 3; });
      return w.length && w.every(function (x) { return pt.indexOf(' ' + x + ' ') >= 0; });
    }).slice(0, 3);
    /* Afinación por modo (19-11-2026): si el tema ya es ambiental (por sus palabras o por el modo de su página,
       modoToca()), no se dice «no hay proyecto»; y cada tema tiende su puente a la página ambiental que le toca
       (AMB_PUENTE), sin cifras: solo a dónde ver su lado ambiental. */
    var yaAmb = modoToca(q, r) === 'ambientalista', base = sinParam((r.ir || [''])[0]).split('#')[0];
    var pt2 = ' ' + plano(q + ' ' + ((r.ir && r.ir[1]) || '')) + ' ';
    var pq2 = ' ' + plano(q) + ' ';
    var pu = AMB_PUENTE.filter(function (x) { return x[0].test(x[4] ? pq2 : pt2) && x[3].split('#')[0] !== base; }).slice(0, 2);
    var hh = '<div class="pa-capa pa-capa-ambientalista"><p class="pa-capa-t">🌎 La mirada ambiental</p>' +
      (os.length ? '<p class="pa-rep-s">Proyectos con alerta ambiental' + (ab ? ' en ' + esc(NOMBRE[ab]) : '') + ', y quién los paga</p><ul class="pa-lista">' + os.map(function (c) {
        return '<li>' + esc(c.ico) + ' <b>' + esc(c.nombre) + '</b>: ' + (c.paga === 'privado' ? '🏢 inversión privada, no es gasto público' : '🏛️ gasto público') +
          '. 🌱 ' + esc(recorta(c.alerta, 150)) + ' <a href="' + esc(c.aud) + '">Ver la investigación ➔</a></li>';
      }).join('') + '</ul>' :
        (yaAmb ? '<p>🌱 Este tema ya es ambiental: la respuesta de arriba es la mirada de este modo.</p>' :
          '<p>Sobre esto no hay un proyecto con alerta ambiental en el mapa de megaobras' + (ab ? ' que toque ' + esc(NOMBRE[ab]) : '') + '. Eso no quiere decir que no haya daño: quiere decir que no lo tenemos documentado.</p>')) +
      (pu.length ? '<p class="pa-rep-s">El lado ambiental de este tema</p><ul class="pa-lista">' + pu.map(function (x) {
        return '<li>' + x[1] + ' <a href="' + esc(x[3]) + '">' + esc(x[2]) + ' ➔</a></li>';
      }).join('') + '</ul>' : '') +
      '<p class="pa-rep-s">Para mirarlo con ojos de ambiente</p><ul class="pa-lista">' +
      '<li>🗺️ <a href="planisferio.html?d=ambiental' + (ab ? '&amp;e=' + esc(ab) : '') + '">' + (ab ? esc(NOMBRE[ab]) + ' en' : 'Los 32 estados en') + ' la dimensión ambiental del Planisferio ➔</a></li>' +
      '<li>⏱️ <a href="herramienta-ambiente-reloj.html">El reloj del daño ambiental</a> y <a href="datos-justicia-ambiental-denuncias.html">lo que resuelve la PROFEPA</a></li></ul>' +
      '<p class="pa-chico">El deterioro del ambiente también es gasto público. Solo se suma lo que paga el gobierno; la inversión privada se dice con su nombre.</p></div>';
    return { html: hh };
  }
  /* Cada modo ofrece pasarse al que le toca cuando la pregunta es de otro tema. */
  var MODO_PAL = [
    ['periodista', /\b(es cierto|dicen que|circula|rumor\w*)\b/],
    ['ambientalista', /\b(ambient\w*|contamina\w*|basura|profepa|ecolog\w*|deforest\w*|selva|manglar\w*|acuifer\w*|incendios? forestal\w*|emisiones)\b/],
    ['periodista', /\b(noticias?|nota de|que paso con|periodistas?)\b/],
    ['inspector', /\b(rfc|folio|expedientes?|diagnostico|contratos?|proveedor\w*|lista negra|69 b|nepotismo|fraccionamiento)\b/],
    ['ciudadano', /\b(me retienen|mi sueldo|gano|mi aguinaldo|mi estado de cuenta|cuanto pago)\b/]
  ];
  var MODO_NOM = { inspector: 'Inspector', periodista: 'Periodista', ciudadano: 'Ciudadano', ambientalista: 'Ambientalista' };
  function modoSugerido(q, cual) {
    var p = ' ' + plano(q) + ' ', m = modoVivo(), s = null;
    MODO_PAL.forEach(function (x) { if (!s && x[1].test(p)) s = x[0]; });
    return s && (cual || s !== m) ? s : null;
  }
  function capaModoHtml(q, r) {
    var m = modoVivo(), c = m === 'inspector' ? inspectorCapa(q, r) : m === 'ciudadano' ? ciudadanoCapa(q, r) : m === 'ambientalista' ? ambientalistaCapa(q, r) : null;
    return c ? c.html : '';
  }
  /* Cada modo contesta lo suyo y remite lo ajeno (pedido del autor, 16-11-2026:
     «en caso que corresponda a otro modo, mencionarlo y remitirlo al chat de
     aquel modo»). A qué modo le toca una respuesta sale de las palabras de la
     pregunta (MODO_PAL) o, si no, del modo con que la base clasificó su ficha
     o su página (modos.py). El Inspector es el modo por omisión de la base: por
     eso una ficha «de Inspector» no remite sola; hace falta que lo pida la
     pregunta. La remisión va arriba de la respuesta; los datos son los mismos. */
  var MODO_COMO = {
    inspector: 'allá la reviso con sus documentos, lo que falta y por dónde seguir',
    periodista: 'allá la cuento como nota, con lo que casi nadie cuenta y lo que circula',
    ciudadano: 'allá te la digo en corto, con sus palabras difíciles y lo que toca a tu bolsillo',
    ambientalista: 'allá la leo por su costo y su daño ambiental, y quién lo paga'
  };
  var MODO_DE_PAG = null;
  function modoToca(q, r) {
    if (!r || r.sin || r.plat) return null;
    var s = modoSugerido(q, true);
    if (s) return s;
    var f = r.ficha, m = f && f.m, ir = r.ir || (f && f.ir);
    if (!m && ir) {
      if (!MODO_DE_PAG) { MODO_DE_PAG = {}; B.fichas.forEach(function (x) { if (x.t === 'pagina' && x.m && x.ir) MODO_DE_PAG[sinParam(x.ir[0]).split('#')[0]] = x.m; }); }
      m = MODO_DE_PAG[sinParam(ir[0]).split('#')[0]];
    }
    return m && m !== 'inspector' && MODO_ICO[m] ? m : null;
  }
  function remiteHtml(q, r) {
    var t = modoToca(q, r), m = modoVivo();
    if (!t || t === m || !MODO_ICO[m]) return '';
    /* Entre los dos chats, la remisión es una liga al otro, con la misma pregunta. */
    if (t === 'inspector' || SOLO || resp) {
      var al = t === 'inspector' ? SV_CHAT + '?q=' + encodeURIComponent(q) : CHAT_AV + '?q=' + encodeURIComponent(q) + '&modo=' + t;
      return '<div class="pa-remite pa-remite-' + t + '"><p><span aria-hidden="true">' + MODO_ICO[t] + '</span> <b>Esto le toca al modo ' + MODO_NOM[t] + '.</b> ' +
        'Te lo contesto aquí con los mismos datos; ' + MODO_COMO[t] + '.</p>' +
        '<a class="pa-boton pa-modo-sug" href="' + esc(al) + '">' + MODO_ICO[t] + (t === 'inspector' ? ' Pasar al Inspector de Servicios' : ' Pasar al chat del Auditor, modo ' + MODO_NOM[t]) + ' ➔</a></div>';
    }
    return '<div class="pa-remite pa-remite-' + t + '"><p><span aria-hidden="true">' + MODO_ICO[t] + '</span> <b>Esto le toca al modo ' + MODO_NOM[t] + '.</b> ' +
      'Te lo contesto aquí con los mismos datos; ' + MODO_COMO[t] + '.</p>' +
      '<button type="button" class="pa-boton pa-modo-sug" data-pa-modo-sug="' + t + '" data-pa-q="' + esc(q) + '">' + MODO_ICO[t] + ' Pasar al modo ' + MODO_NOM[t] + ' ➔</button></div>';
  }
  /* Para el banco de pruebas: la capa del modo pedido, en texto. */
  function capaModo(q, r, m) {
    var f = { inspector: inspectorCapa, ciudadano: ciudadanoCapa, ambientalista: ambientalistaCapa, periodista: periodista }[m];
    return f ? f(q, r) : null;
  }
  var TIPOS_REC = { planisferio: 'mapa', mapa: 'mapa', mapas: 'mapa', reloj: 'reloj', relojes: 'reloj', contador: 'reloj', contadores: 'reloj', simulador: 'simulador', simuladores: 'simulador', tablero: 'tablero' };
  function pideRecurso(q) {
    var p = plano(q), tipo = null;
    Object.keys(TIPOS_REC).forEach(function (w) { if (p.indexOf(' ' + w + ' ') >= 0) tipo = TIPOS_REC[w]; });
    if (!tipo || / estados? de cuenta /.test(p)) return null;
    var ws = conSinon(q), ab = entidadDe(q), mejor = null, ms = 0, delTipo = REC.filter(function (x) { return x.tipo === tipo; });
    var tema = ws.filter(function (w) { return (!TIPOS_REC[w] || w === 'planisferio') && !(ab && plano(NOMBRE[ab]).indexOf(' ' + w + ' ') >= 0); });
    delTipo.forEach(function (x) { var s = comunes(x._k, tema); if (s > ms) { ms = s; mejor = x; } });
    if (!mejor && tema.length > 1) return null;
    var lista = function (xs) { return '<ul class="pa-lista">' + sinRepetirPl(xs).map(function (x) { return '<li><a href="' + esc(destinoRec(x, ab)) + '">' + x.ico + ' <b>' + esc(x.n) + '</b>' + (x.pl && x.pld ? ' · en el Planisferio' : '') + '</a></li>'; }).join('') + '</ul>'; };
    if (!mejor) return { html: '<p>Estos son los que tengo:</p>' + lista(delTipo) + '<p>Cada uno se abre en su página. Dime el tema y te llevo al que es.</p>', ir: [delTipo[0].ir, delTipo[0].n], sug: [], rec: [] };
    /* Un mapa que vive en el Planisferio se abre ahí, la matriz de los mapas (04-11-2026). */
    var k = function (x) { return x.pl ? (x.plk || x.pl) : x.ir; };
    var otros = delTipo.filter(function (x) { return x !== mejor && k(x) !== k(mejor); });
    return {
      html: '<p>' + mejor.ico + ' Aquí está: <b>' + esc(mejor.n) + '</b>' + (mejor.pl && mejor.pld ? ', en el Planisferio' : '') + (ab && (mejor.ple || mejor.ire) ? ', ya con ' + esc(NOMBRE[ab]) + ' elegido' : '') + '. Toca <b>«Saber más»</b> y se abre en su página.</p>' +
        (otros.length ? '<p class="pa-chico">También tengo:</p>' + lista(otros) : ''),
      ir: [destinoRec(mejor, ab), mejor.pl && mejor.pll ? 'el Planisferio · dimensión ' + mejor.pll.charAt(0).toLowerCase() + mejor.pll.slice(1) : mejor.n], sug: [], rec: []
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
     descargan la primera vez que se pregunta: 1.9 MB). --- */
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
    /* «¿Cuánto facturaron las empresas fantasma?» pide una cifra, no un nombre: la contesta «El fraude en números». */
    if (!rfcs.length && /\b(cuanto|monto|montos|dinero|billones|evasion|evadieron)\b/.test(p)) return null;
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
      return respApp('inspefos', liga, '<p>No pude descargar ahora la lista oficial del SAT (1.9 MB). Revisa tu conexión y vuelve a preguntarme, o búscalo en la aplicación aquí abajo.</p>');
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
  function cmxSanc() { return cargaJs('assets/auditor/data/sancionados.js', function () { return window.AUDIT_SANCIONADOS; }).catch(function () { return null; }); }
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
    /* «¿Cómo reviso a un proveedor antes de contratarlo?» pide el método, no a una empresa: lo contesta map/srv_diligencia (D.san). */
    if (!rfcs.length && /\b(antes de contratar\w*|debida diligencia)\b/.test(p)) return null;
    /* «¿Qué pasa si no le cobran la pena al contratista?» no busca a una empresa: lo contesta «Documentar para sancionar». */
    if (!rfcs.length && /\b(penas?|multas?|sancion\w*|incumpl\w*|no cumplio|clausulas?|pruebo|que documentos)\b/.test(p)) return null;
    /* «Se venció mi contrato eventual» habla de un trabajo, no de un contrato público: lo contesta el simulador laboral. */
    if (!rfcs.length && /\b(mi contrato|contrato (eventual|por tiempo|de trabajo|laboral)|me toca|finiquito|liquidacion)\b/.test(p)) return null;
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
    var prom = Promise.all([cmxIdx(), cmxInst(), cmxSanc()]).then(function (D) {
      var I = D[0], T = D[1], S = D[2];
      if (rfcs.length) return cmxProv(rfcs[0]).then(function (d) { return respProv(rfcs[0], d, I.meta, S); });
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
      if (!provs.length && S && S.n) {
        provs = Object.keys(S.n).filter(function (rfc) {
          var n = ' ' + satNorm(S.n[rfc]) + ' ';
          return ws.every(function (w) { return n.indexOf(' ' + w + ' ') >= 0; });
        }).map(function (rfc) { return [rfc, S.n[rfc]]; });
      }
      if (!provs.length) return { html: '<p>◻️ No encontré «' + esc(nombre) + '» entre los <b>' + I.meta.proveedores.toLocaleString('es-MX') + '</b> proveedores (personas morales) ni entre las <b>' + I.meta.instituciones.toLocaleString('es-MX') + '</b> instituciones con contratos en ComprasMX, en los expedientes de 2025 y 2026.</p>' +
        '<p>Eso no quiere decir que no tenga contratos: el nombre puede estar escrito distinto, sus contratos pueden ser de otros años, o la institución puede no reportar en ComprasMX. Varios órganos autónomos, como el INE, y los gobiernos que no usan la plataforma publican sus contratos en sus propios portales y en la Plataforma Nacional de Transparencia. Con el <b>RFC</b> la búsqueda es exacta.</p>',
        ir: [CMX_PAG + '?q=' + encodeURIComponent(nombre), 'Contratos públicos'], sug: [], rec: [], web: nombre };
      var exacto = provs.filter(function (r) { return satNorm(r[1]).replace(/\b(S ?A|DE|C ?V|S ?A ?P ?I|R ?L|S ?C)\b/g, '').replace(/ +/g, ' ').trim() === ws.join(' '); });
      if (provs.length === 1 || exacto.length === 1) { var r1 = provs.length === 1 ? provs[0] : exacto[0]; return cmxProv(r1[0]).then(function (d) { return respProv(r1[0], d, I.meta, S); }); }
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
  function sancChatHtml(rfc, S, ci, fuentes, deDondeList) {
    var exps = S && S.r && S.r[rfc];
    if (!exps || !exps.length) return '';
    var fuS = { tx: S.fuente + ' (corte al ' + S.corte + ')', url: S.url };
    if (fuentes) fuentes.push(fuS);
    if (deDondeList) deDondeList.push({ que: 'Directorio de Proveedores y Contratistas Sancionados', e: 'oficial', fu: fuS });
    exps.forEach(function (x) {
      if (ci) ci.push({ v: x[5] || (x[6] ? pesosCmx(x[6]) : 'Sanción'), etq: 'Expediente ' + x[0] + ' · ' + (x[1] || 'OIC') + ' (' + x[2] + ')', e: 'oficial' });
    });
    return '<p>⛔ <b>En el Directorio de Proveedores y Contratistas Sancionados</b> (' + exps.length.toLocaleString('es-MX') + ' expediente' + (exps.length === 1 ? '' : 's') + ' al corte del ' + esc(S.corte) + ') ' + chip({ e: 'oficial' }) + ':</p><ul class="pa-lista">' +
      exps.map(function (x) {
        return '<li><b>' + esc(x[0]) + '</b> · ' + esc(x[1] || 'Órgano Interno de Control') + ' (' + esc(x[2]) + ')' +
          (x[5] ? ' · inhabilitación: <b>' + esc(x[5]) + '</b> (' + esc(x[3]) + ' a ' + esc(x[4]) + ')' : (x[3] || x[4] ? ' · vigencia: ' + esc(x[3]) + ' a ' + esc(x[4]) : '')) +
          (x[6] ? ' · multa: <b>' + pesosCmx(x[6]) + '</b>' : '') + (x[7] ? ' · DOF ' + esc(x[7]) : '') + '</li>';
      }).join('') + '</ul>';
  }
  function respProv(rfc, d, M, S) {
    var ci = [], fuente = cmxFuente(M), fuentes = [fuente], deDondeList = [{ que: 'Datos relevantes de los contratos de ComprasMX', e: 'oficial', fu: fuente }];
    var sh = sancChatHtml(rfc, S, ci, fuentes, deDondeList);
    if (!d) {
      if (sh && S && S.n && S.n[rfc]) {
        var nomS = S.n[rfc];
        var hs = '<p>🏢 <b>' + esc(nomS) + '</b> (<code>' + esc(rfc) + '</code>) no tiene contratos en los expedientes de 2025 y 2026 de ComprasMX, pero aparece en el Directorio de Buen Gobierno:</p>' + sh +
          '<p class="pa-chico">⚖️ ' + esc(S.nota) + '</p>' + (charla && charla.deDonde ? charla.deDonde(deDondeList.slice(1)) : '');
        return { html: hs, ir: [CMX_PAG + '?q=' + rfc, 'Contratos públicos'], rec: [],
          ficha: { t: 'calculo', tit: 'Proveedor sancionado: ' + nomS, txt: texto(hs), ci: ci, fu: fuentes.slice(1), ir: [CMX_PAG + '?q=' + rfc, 'Contratos públicos'] },
          sug: ['¿Está en la lista negra del SAT el RFC ' + rfc + '?', '¿Qué proveedores están sancionados o inhabilitados?'] };
      }
      return { html: '<p>◻️ El RFC <code>' + esc(rfc) + '</code> no tiene contratos en los expedientes de 2025 y 2026 de ComprasMX ni aparece en el Directorio de Proveedores y Contratistas Sancionados.</p><p>Puede tenerlos en otros años o con gobiernos que no usan ComprasMX. Eso no certifica nada.</p>',
        ir: [CMX_PAG + '?q=' + rfc, 'Contratos públicos'], sug: ['¿Está en la lista negra del SAT el RFC ' + rfc + '?'], rec: [] };
    }
    var tp = d.tp || {}, mtp = d.mtp || {};
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
      h += cruceUna(rfc);
    }
    if (sh) h += sh;
    var emp = PE.per.filter(function (x) { return x.emp; }).filter(function (x) { return x.al.some(function (a) { return plano(d.n).indexOf(' ' + a + ' ') >= 0; }); })[0];
    if (emp) h += '<p>📰 La plataforma también tiene a <b>' + esc(corta(emp.n)) + '</b> en Noticias relevantes: <button type="button" class="pa-ej" data-pa-pregunta="' + esc(corta(emp.n)) + '">Ver lo que sabemos</button></p>';
    h += cmxCaveat();
    ci.push({ v: d.c.toLocaleString('es-MX') + ' contratos', etq: d.n + ' · RFC ' + rfc + ' · expedientes 2025 y 2026', e: 'oficial' });
    ci.push({ v: pesosCmx(d.m), etq: 'Importe antes de impuestos, suma de sus contratos en pesos', e: 'derivado' });
    d.k.forEach(function (k) { ci.push({ v: pesosCmx(k[3]) + (k[4] !== 'MXN' ? ' ' + k[4] : ''), etq: k[0] + ' · ' + k[1] + ' · ' + k[2], e: 'oficial' }); });
    var tit = 'Contratos en ComprasMX: ' + d.n;
    h += charla && charla.deDonde ? charla.deDonde(deDondeList) : '';
    return { html: h, ir: [CMX_PAG + '?q=' + rfc, 'Contratos públicos'], rec: [],
      ficha: { t: 'calculo', tit: tit, txt: texto(h), ci: ci, fu: fuentes, ir: [CMX_PAG + '?q=' + rfc, 'Contratos públicos'] },
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
  /* --- Grupos empresariales y sus filiales (pedido del autor, 17-11-2026: «le
     pregunté al chat por Grupo Prodi y no salió información»). Muchos grupos no
     contratan con su nombre: contrata una filial. El catálogo lo escribe
     herramientas/empresas_grupos.py, sin cifras: los contratos se leen de
     ComprasMX por el RFC de cada filial. El vínculo que solo dice la prensa va
     como pendiente, y lo que falta cotejar no lleva montos. --- */
  var GR = (B.dat && B.dat.gru) || { g: [], fig: [], nota: '' };
  function figHtml() {
    return GR.fig.length ? '<p>📑 <b>Contrato, concesión y permiso no son lo mismo:</b></p><ul class="pa-lista">' + GR.fig.map(function (f) {
      return '<li><b>' + esc(f.n) + '.</b> ' + esc(f.tx) + ' <span class="pa-chico">(' + esc(f.ley) + ')</span></li>';
    }).join('') + '</ul>' : '';
  }
  function grupoEmp(q) {
    var p = plano(q), g = GR.g.filter(function (x) { return x.al.some(function (a) { return p.indexOf(' ' + a + ' ') >= 0; }); })[0];
    if (!g || SAT_PAL.test(p) || (q.match(RFC_RE) || []).length) return null;
    var prom = cmxIdx().then(function (I) {
      return Promise.all(g.emp.map(cmxProv)).then(function (ds) { return respGrupo(g, ds, I.meta); });
    }).then(null, function () { return respGrupo(g, [], null); });
    return { espera: prom, tit: 'Grupo empresarial: ' + g.n };
  }
  function respGrupo(g, ds, M) {
    var ci = [], fu = M ? [cmxFuente(M)] : [];
    var h = '<p>🏢 <b>' + esc(g.n) + '.</b> ' + g.que + '</p>' +
      '<p>🔗 <b>El vínculo:</b> ' + esc(g.vin.tx) + ' ' + (g.vin.e === 'oficial' ? chip({ e: 'oficial' }) : chip({ e: 'pendiente', p: g.vin.p })) + '. ' + esc(g.vin.x) + '</p>';
    ds.forEach(function (d, i) {
      var rfc = g.emp[i];
      if (!d) return;
      var tp = d.tp || {}, mtp = d.mtp || {};
      var partes = ['AD', 'LP', 'I3', 'OT'].filter(function (k) { return tp[k]; }).map(function (k) {
        return '<b>' + tp[k].toLocaleString('es-MX') + '</b> por ' + TIPO_CMX[k] + (mtp[k] ? ' (' + pesosCmx(mtp[k]) + ')' : '');
      });
      h += '<p>🧾 <b>' + esc(d.n) + '</b> (<code>' + esc(rfc) + '</code>) tiene <b>' + d.c.toLocaleString('es-MX') + ' contrato' + (d.c === 1 ? '' : 's') + '</b> en ComprasMX, en los expedientes de 2025 y 2026, por <b>' + pesosCmx(d.m) + '</b> antes de impuestos ' + chip({ e: 'derivado' }) + '. Por procedimiento: ' + partes.join('; ') + '.</p>' +
        '<p>Sus contratos mayores ' + chip({ e: 'oficial' }) + ':</p><ul class="pa-lista">' + d.k.slice(0, 5).map(function (k) {
          return '<li>' + pesosCmx(k[3]) + (k[4] !== 'MXN' ? ' ' + esc(k[4]) : '') + ' · <b>' + esc(k[1]) + '</b> · ' + esc(TIPO_CMX[k[5]] || '') + (k[6] ? ' · ' + esc(k[6]) : '') + '<br><span class="pa-chico">' + esc(k[2]) + '</span>' +
            (k[7] ? ' <a href="' + esc(M.detalle.replace('%s', k[7])) + '" target="_blank" rel="noopener">Ver en ComprasMX ↗</a>' : '') + '</li>';
        }).join('') + '</ul>' +
        '<p><button type="button" class="pa-ej" data-pa-pregunta="' + esc('Contratos de ' + rfc) + '">Ver todos sus contratos</button></p>';
      ci.push({ v: d.c.toLocaleString('es-MX') + ' contratos', etq: d.n + ' · RFC ' + rfc + ' · expedientes 2025 y 2026', e: 'oficial' });
      ci.push({ v: pesosCmx(d.m), etq: 'Importe antes de impuestos, suma de sus contratos en pesos', e: 'derivado' });
      d.k.slice(0, 5).forEach(function (k) { ci.push({ v: pesosCmx(k[3]) + (k[4] !== 'MXN' ? ' ' + k[4] : ''), etq: k[0] + ' · ' + k[1] + ' · ' + k[2], e: 'oficial' }); });
    });
    if (!M) h += '<p class="pa-chico">No pude descargar ahora el catálogo de ComprasMX para decirte sus contratos. Revisa tu conexión y vuelve a preguntarme.</p>';
    if (g.asf && g.asf.length) {
      h += '<p>🔎 <b>Lo que auditó la ASF (contratos anteriores a ComprasMX 2025-2026):</b></p><ul class="pa-lista">' + g.asf.map(function (a) {
        var fuA = { tx: 'ASF, Cuenta Pública ' + a.cp + ', Auditoría ' + a.num + ' (' + a.clave + ', sha256 ' + a.sha + '…)', url: a.url };
        fu.push(fuA);
        ci.push({ v: '$' + a.tot_mdp.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp', etq: a.etq + ' · contrato ' + a.contrato + ' (original $' + a.orig_mdp.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp + convenios $' + a.conv_mdp.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp)', e: 'oficial' });
        return '<li><b>' + esc(a.etq) + '</b> (contrato <code>' + esc(a.contrato) + '</code>, firmado el ' + esc(a.fecha) + ' con <b>' + esc(a.consorcio) + '</b>, integrado por ' + esc(a.integrantes) + '): importe original <b>$' + a.orig_mdp.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp</b> ' + chip({ e: 'oficial' }) + ', convenios modificatorios por <b>+$' + a.conv_mdp.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp</b>, total contratado <b>$' + a.tot_mdp.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp</b> ' + chip({ e: 'oficial' }) + ' ($' + a.ej22_mdp.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp ejercidos en ' + a.cp + ') y <b>$' + a.aclarar_mdp.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp</b> pendientes por aclarar en la <a href="' + esc(a.url) + '" target="_blank" rel="noopener">Auditoría ' + a.num + ' de la Cuenta Pública ' + a.cp + ' ↗</a>.</li>';
      }).join('') + '</ul>';
    }
    h += figHtml();
    if (g.cot.length) h += '<p>🔎 <b>Lo que falta cotejar</b> (sin montos hasta tener el documento):</p><ul class="pa-lista">' + g.cot.map(function (c) {
      ci.push({ v: c.fig, etq: c.tx, e: 'pendiente', p: c.p });
      return '<li><b>' + esc(c.fig) + '.</b> ' + esc(c.tx) + ' ' + chip({ e: 'pendiente', p: c.p }) + '<br><span class="pa-chico">' + esc(c.x) + ' Dónde debe estar: <a href="' + esc(c.url) + '" target="_blank" rel="noopener">' + esc(c.ut) + ' ↗</a></span></li>';
    }).join('') + '</ul>';
    if (g.pr.length) h += '<p>📰 <b>Cómo lo contó la prensa</b> (sin verificar: solo titular y liga; una nota no es fuente):</p><ul class="pa-lista">' + g.pr.map(function (x) {
      return '<li><a href="' + esc(x.u) + '" target="_blank" rel="noopener">' + esc(x.t) + ' ↗</a> <span class="pa-chico">(' + esc(x.m) + ')</span></li>';
    }).join('') + '</ul>';
    h += '<p class="pa-chico">⚖️ ' + esc(GR.nota) + ' El importe es el que reportó cada institución, antes de impuestos; en un contrato abierto suele ser el máximo, no lo pagado.</p>';
    var tit = 'Grupo empresarial: ' + g.n;
    if (M) h += charla && charla.deDonde ? charla.deDonde([{ que: 'Datos relevantes de los contratos de ComprasMX', e: 'oficial', fu: fu[0] }]) : '';
    return { html: h, ir: [g.ir, 'Grupos y filiales'], rec: [],
      ficha: { t: 'calculo', tit: tit, txt: texto(h), ci: ci, fu: fu, ir: [g.ir, 'Grupos y filiales'] },
      sug: g.emp.slice(0, 2).map(function (r) { return '¿Está en la lista negra del SAT el RFC ' + r + '?'; }).concat(['¿Qué es una concesión?']) };
  }
  /* Una empresa por su nombre, sin la palabra «contratos» («Grupo Carso», «la empresa
     ICA», «X, S.A. de C.V.», «¿es concesionaria X?»): se busca en ComprasMX y, si no
     está, la pregunta sigue su camino de siempre (sinEmp evita volver a entrar). */
  var EMP_RE = /^ (?:(?:quien(?:es)? (?:es|son)|que es|que se sabe de|que hay de|dime de|busca|investiga) )?(?:a )?(?:la |el )?(?:empresa|grupo|constructora|concesionaria|consorcio|corporativo|laboratorios?|comercializadora) \S/;
  var EMP_SUF = / (?:s a de c v|sa de cv|s a p i de c v|sapi de cv|s de r l de c v|s a b de c v|sab de cv) $/;
  var EMP_CON = /^ (?:(?:que|cuales|cuantas) )?concesion(?:es)? (?:tiene|de|del|a) \S| (?:es|son) (?:una )?concesionarias? /;
  var EMP_FUERA = 'concesion concesiones concesionaria concesionarias una un se sabe consorcio corporativo'.split(' ');
  var sinEmp = false;
  function sigueSinEmp(q, previas) {
    sinEmp = true;
    try { var r = respuesta0(q, previas); return r && r.espera ? r.espera : r; } finally { sinEmp = false; }
  }
  function cmxPorNombre(I, ws) {
    var provs = I.r.filter(function (r) { var n = ' ' + satNorm(r[1]) + ' '; return ws.every(function (w) { return n.indexOf(' ' + w + ' ') >= 0; }); });
    var exacto = provs.filter(function (r) { return satNorm(r[1]).replace(/\b(S ?A|DE|C ?V|S ?A ?P ?I|R ?L|S ?C|S ?A ?B)\b/g, '').replace(/ +/g, ' ').trim() === ws.join(' '); });
    return { todos: provs, uno: provs.length === 1 ? provs[0] : exacto.length === 1 ? exacto[0] : null };
  }
  function cualEmp(provs, nombre) {
    return { html: '<p>Encontré <b>' + provs.length.toLocaleString('es-MX') + '</b> empresas con «' + esc(nombre) + '» en el nombre entre los proveedores de ComprasMX. ¿Cuál buscas?</p><p>' +
      provs.slice(0, 8).map(function (r) { return '<button type="button" class="pa-ej" data-pa-pregunta="' + esc('Contratos de ' + r[0]) + '">' + esc(r[1]) + '</button>'; }).join(' ') + '</p>' +
      (provs.length > 8 ? '<p class="pa-chico">Te muestro 8. Con el RFC la búsqueda es exacta.</p>' : ''),
      ir: [CMX_PAG + '?q=' + encodeURIComponent(nombre), 'Contratos públicos'], sug: [], rec: [] };
  }
  function empresaNombre(q, previas) {
    var p = plano(q), con = EMP_CON.test(p);
    if (sinEmp || CMX_RE.test(p) || SAT_PAL.test(p) || (q.match(RFC_RE) || []).length) return null;
    if (!EMP_RE.test(p) && !EMP_SUF.test(p) && !con) return null;
    if (/\b(fantasmas?|productivas?|parlamentarios?|vulnerables?|publicas?|paraestatal(es)?|del estado|mineras?|de agua|radio|television)\b/.test(p)) return null;
    var nombre = p.trim().split(' ').filter(function (w) { return w.length > 1 && CMX_FUERA.indexOf(w) < 0 && EMP_FUERA.indexOf(w) < 0; }).join(' ');
    var ws = satNorm(nombre).split(' ').filter(function (w) { return w; });
    if (!ws.length || ws.length > 6) return null;
    var prom = cmxIdx().then(function (I) {
      var m = cmxPorNombre(I, ws);
      if (!m.todos.length || (!m.uno && m.todos.length > 60)) return Promise.resolve(sigueSinEmp(q, previas)).then(function (r) {
        /* Si lo demás de la plataforma tampoco la tiene, se dice: no se contesta con lo que se le parece. */
        if (r && !r.sin && !r.tambien && !/^<p>Eso lo encuentras en/.test(r.html || '')) return r;
        return { html: '<p>◻️ No encontré a «' + esc(nombre) + '» entre los <b>' + I.meta.proveedores.toLocaleString('es-MX') + '</b> proveedores (personas morales) con contratos en ComprasMX, en los expedientes de 2025 y 2026, ni en el resto de la plataforma.</p>' +
          '<p>Eso no quiere decir que no tenga contratos: muchos grupos contratan con el nombre de una filial o de un consorcio, sus contratos pueden ser de otros años, o pueden ser de gobiernos que no usan ComprasMX. Y una <b>concesión</b> no aparece ahí: se acredita con su título. Con el <b>RFC</b> de la empresa la búsqueda es exacta.</p>',
          ir: [GR.pag || CMX_PAG, 'Grupos y filiales'], sug: ['¿Qué es una concesión?', '¿Qué contratistas están en la lista negra del SAT?'], rec: [], web: nombre, anota: true };
      });
      var nota = con ? '<p>📑 <b>ComprasMX trae contratos, no concesiones.</b> Una concesión se acredita con su título, que publica el gobierno que la otorga. Esto es lo que la plataforma tiene de sus contratos:</p>' : '';
      if (m.uno) return Promise.all([cmxProv(m.uno[0]), cmxSanc()]).then(function (P) { var r = respProv(m.uno[0], P[0], I.meta, P[1]); r.html = nota + r.html + (con ? figHtml() : ''); return r; });
      var r = cualEmp(m.todos, nombre); r.html = nota + r.html; return r;
    }, function () { return sigueSinEmp(q, previas); });
    return { espera: prom, tit: 'Empresa en ComprasMX: ' + nombre };
  }
  /* Un nombre propio que la plataforma no tiene («Laboratorios Pisa» a secas): antes
     de decir «no lo sé», se revisa si es una empresa con contratos en ComprasMX. */
  function quizaEmpresa(q, r) {
    if (sinEmp || !r || r.espera || !(r.sin || (r.tambien && r.web))) return r;
    var ws = satNorm(q).split(' ').filter(function (w) { return w.length > 1; });
    if (!ws.length || ws.length > 5 || /[?¿]/.test(q) || /\b(QUE|CUANTO|CUANTOS|CUANTA|CUANTAS|COMO|QUIEN|QUIENES|CUAL|CUALES|DONDE|CUANDO|POR|ES|SON|HAY)\b/.test(' ' + ws.join(' ') + ' ')) return r;
    var prom = cmxIdx().then(function (I) {
      var m = cmxPorNombre(I, ws);
      if (m.uno) return Promise.all([cmxProv(m.uno[0]), cmxSanc()]).then(function (P) { return respProv(m.uno[0], P[0], I.meta, P[1]); });
      return ws.length > 1 && m.todos.length > 1 && m.todos.length <= 8 ? cualEmp(m.todos, ws.join(' ').toLowerCase()) : r;
    }, function () { return r; });
    return { espera: prom, tit: 'Empresa en ComprasMX: ' + q };
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
  /* Directorio de Proveedores y Contratistas Sancionados (Buen Gobierno). */
  var SANC_RE = /\b(proveedor(es)?|contratistas?|empresas?)\b.*\b(sancionad\w*|inhabilitad\w*)\b|\b(sancionad\w*|inhabilitad\w*)\b.*\b(proveedor(es)?|contratistas?|comprasmx)\b|\bdirectorio de (proveedores|sancionados|contratistas)\b/;
  function sancionesCmx(q) {
    var p = plano(q);
    if (!SANC_RE.test(p) || /\b(asf|funcionarios?|servidor(es)?|nepotismo)\b/.test(p) || (q.match(RFC_RE) || []).length) return null;
    return { espera: cmxSanc().then(function (S) {
      if (!S) return { html: '<p>No pude descargar ahora el directorio de proveedores sancionados.</p>', ir: [CMX_PAG + '#sancionados', 'Contratos públicos'], sug: [], rec: [] };
      var R = S.resumen, fu = { tx: S.fuente + ' (corte al ' + S.corte + ')', url: S.url };
      var h = '<p>⛔ El <b>Directorio de Proveedores y Contratistas Sancionados</b> de la Secretaría Anticorrupción y Buen Gobierno reúne <b>' + R.expedientes.toLocaleString('es-MX') + ' expedientes de sanción</b> (' + R.expedientesMorales.toLocaleString('es-MX') + ' de <b>' + R.empresasUnicas.toLocaleString('es-MX') + ' personas morales</b> y ' + R.personasFisicasOcultas.toLocaleString('es-MX') + ' de personas físicas que no se publican por dato personal) por <b>$' + R.multasMdp.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp</b> en multas, al corte del ' + esc(S.corte) + ' ' + chip({ e: 'oficial' }) + '.</p>' +
        '<p>Al cruzarlo por RFC contra los contratos públicos de ComprasMX (expedientes de 2025 y 2026) y la lista 69-B del SAT: <b>' + R.enComprasMx + ' empresas sancionadas tienen contratos en 2025-2026</b> y <b>' + R.enSat69b + ' aparecen también en la lista 69-B</b> ' + chip({ e: 'derivado' }) + '. Algunas de las que tienen contratos:</p>' +
        '<ul class="pa-lista">' + S.cruceComprasMx.slice(0, 10).map(function (r) {
          return '<li>⛔ <button type="button" class="pa-ej" data-pa-pregunta="' + esc('Contratos de ' + r[0]) + '">' + esc(r[1]) + '</button> (<code>' + esc(r[0]) + '</code>) · ' + r[2] + ' sanción' + (r[2] === 1 ? '' : 'es') + ' (' + esc(r[3]) + ', ' + esc(r[4]) + ')' + (r[5] || r[6] ? ' · ' + esc(r[5]) + ' a ' + esc(r[6]) : '') + (r[7] ? ' · multa ' + pesosCmx(r[7]) : '') + '</li>';
        }).join('') + '</ul>' +
        '<p class="pa-chico">⚖️ ' + esc(S.nota) + '</p>' +
        (charla && charla.deDonde ? charla.deDonde([{ que: 'Directorio de Proveedores y Contratistas Sancionados', e: 'oficial', fu: fu }]) : '');
      var ci = [
        { v: R.expedientes.toLocaleString('es-MX') + ' expedientes', etq: R.empresasUnicas.toLocaleString('es-MX') + ' personas morales sancionadas (corte ' + S.corte + ')', e: 'oficial' },
        { v: '$' + R.multasMdp.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp', etq: 'Suma de multas impuestas en el Directorio', e: 'derivado' },
        { v: R.enComprasMx + ' empresas', etq: 'Sancionadas en el Directorio y con contratos en ComprasMX 2025-2026', e: 'derivado' }
      ];
      return { html: h, ir: [CMX_PAG + '#sancionados', 'Proveedores sancionados'], rec: [],
        ficha: { t: 'calculo', tit: 'Proveedores y contratistas sancionados (Buen Gobierno)', txt: texto(h), ci: ci, fu: [fu], ir: [CMX_PAG + '#sancionados', 'Proveedores sancionados'] },
        sug: ['¿Qué contratistas están en la lista negra del SAT?', 'Contratos de EYA840229LX3', '¿Cómo reviso a un proveedor antes de contratarlo?'] };
    }), tit: 'Proveedores sancionados' };
  }

  /* Señales de fraccionamiento (03-11-2026): adjudicaciones directas por monto
     de la misma unidad, empresa y partida que en 90 días rebasan el tope del
     Anexo 9 del PEF. Lo escribe herramientas/fraccionamiento.py. Es una señal
     para revisar, nunca una irregularidad, y no nombra a las empresas. */
  var FRACC_PAG = CMX_PAG + '#fraccionamiento';
  function fraccDatos() { return cargaJs('assets/auditor/data/fraccionamiento.js', function () { return window.CMX_FRACC; }); }
  function fraccPide(p) {
    if (/\bcontratos? partidos?\b/.test(p) || /\b(partir|partieron|parten|dividir|dividieron|dividen)\b.*\b(compras?|contratos?)\b/.test(p)) return true;
    return /\bfraccion(amiento|amientos|ar|ada|adas|ado|ados|an|aron)\b/.test(p) && /\b(contrat\w*|compras?|adjudica\w*|senal\w*|señal\w*|topes?|comprasmx)\b/.test(p);
  }
  function fraccCaveat() {
    return '<p class="pa-chico">⚖️ Es una <b>señal para revisar, no una irregularidad</b>: la partida junta bienes parecidos, no «exactamente los mismos»; el archivo no trae el área que los pidió, y si se pudieron prever juntos no se ve en los datos. No nombramos a las empresas: cada contrato lleva su liga a ComprasMX.</p>';
  }
  function fraccCmx(q) {
    var p = plano(q);
    if (!fraccPide(p)) return null;
    return { espera: fraccDatos().then(function (D) {
      var M = D.meta, T = D.tot, A = Object.keys(T).sort(), fu = cmxFuente(M), ci = [];
      var fuentes = [fu].concat(A.map(function (a) { return { tx: M.anexo9[a].doc, url: M.anexo9[a].url }; })).concat([{ tx: M.reglamento.texto, url: M.reglamento.url }]);
      var f = null;
      D.i.forEach(function (x) {
        if (f) return;
        var s = plano(x.s).trim();
        if (s.length > 2 && p.indexOf(' ' + s + ' ') >= 0) f = x;
      });
      if (!f) D.i.forEach(function (x) {
        if (f) return;
        var ws = plano(x.n).trim().split(' ').filter(function (w) { return w.length > 3; });
        if (ws.length > 1 && ws.every(function (w) { return p.indexOf(' ' + w + ' ') >= 0; })) f = x;
      });
      var topes = A.map(function (a) { return a + ': de ' + pesosCmx(M.anexo9[a].min) + ' a ' + pesosCmx(M.anexo9[a].max); }).join('; ');
      var h;
      if (f) {
        var nA = A.reduce(function (s, a) { return s + f[a].A[0]; }, 0);
        h = '<p>🧩 <b>' + esc(f.n) + '</b> (' + esc(f.s) + ') tiene <b>' + nA + ' grupo' + (nA === 1 ? '' : 's') + '</b> de adjudicaciones directas por monto que, con la misma unidad compradora, la misma empresa y la misma partida, suman en ' + M.ventana + ' días más que el tope más alto del Anexo 9 ' + chip({ e: 'derivado' }) + '.</p><ul class="pa-lista">' +
          A.map(function (a) { var x = f[a]; return '<li><b>' + a + '</b>: ' + x.A[0] + ' grupos, ' + x.A[1] + ' contratos, ' + pesosCmx(x.A[2]) + '. Otros ' + x.B[0] + ' grupos rebasan el tope más bajo; si son señal depende del escalón de la dependencia ' + chip({ e: 'pendiente', p: 'fracc-escalon' }) + '.' + (x.solos ? ' Además, ' + x.solos + ' contrato' + (x.solos === 1 ? '' : 's') + ' «por monto» que por sí solo' + (x.solos === 1 ? '' : 's') + ' rebasa' + (x.solos === 1 ? '' : 'n') + ' el tope más alto.' : '') + '</li>'; }).join('') + '</ul>';
        var gs = [];
        A.forEach(function (a) { f[a].g.forEach(function (g) { gs.push([a].concat(g)); }); });
        gs.sort(function (x, y) { return y[3] - x[3]; });
        if (gs.length) h += '<p>Los grupos mayores ' + chip({ e: 'oficial' }) + ' (cada contrato, con su liga):</p><ul class="pa-lista">' + gs.slice(0, 5).map(function (g) {
          return '<li><b>' + pesosCmx(g[3]) + '</b> en ' + g[6].length + ' contratos, del ' + esc(g[4]) + ' al ' + esc(g[5]) + ' · partida ' + esc(g[2]) + '<br><span class="pa-chico">' + esc(g[1]) + '</span><br>' +
            g[6].map(function (c) { return (c[3] ? '<a href="' + esc(M.detalle.replace('%s', c[3])) + '" target="_blank" rel="noopener">' + esc(c[0]) + ' ↗</a>' : esc(c[0])) + ' ' + pesosCmx(c[1]); }).join(' · ') + '</li>';
        }).join('') + '</ul>' + (gs.length > 5 ? '<p class="pa-chico">Te muestro 5 de ' + gs.length + '.</p>' : '');
        ci.push({ v: nA + ' grupos', etq: f.n + ' · señales de fraccionamiento, ' + A.join(' y '), e: 'derivado' });
        gs.slice(0, 5).forEach(function (g) { ci.push({ v: pesosCmx(g[3]), etq: g[0] + ' · ' + g[1] + ' · ' + g[6].map(function (c) { return c[0]; }).join(', '), e: 'derivado' }); });
      } else {
        h = '<p>🧩 La ley prohíbe partir una compra en varias adjudicaciones directas para no pasar del tope (LAASSP, art. 55; su Reglamento, art. 111, dice cuándo hay fraccionamiento). Revisé en ComprasMX las adjudicaciones directas por monto a empresas, con la misma unidad compradora, la misma empresa y la misma partida, en ventanas de ' + M.ventana + ' días:</p><ul class="pa-lista">' +
          A.map(function (a) { var t = T[a]; return '<li><b>' + a + '</b>: <b>' + t.A[0].toLocaleString('es-MX') + ' grupos</b> (' + t.A[1].toLocaleString('es-MX') + ' contratos, ' + pesosCmx(t.A[2]) + ') rebasan el tope más alto ' + chip({ e: 'derivado' }) + '; otros ' + t.B[0].toLocaleString('es-MX') + ' rebasan el más bajo y dependen del escalón de cada dependencia ' + chip({ e: 'pendiente', p: 'fracc-escalon' }) + '.</li>'; }).join('') + '</ul>' +
          '<p>Los topes por operación, sin IVA, según el tamaño de la dependencia (Anexo 9 del PEF) ' + chip({ e: 'oficial' }) + ': ' + topes + '.</p>' +
          '<p>Donde hay más señales:</p><ol class="pa-lista">' + D.i.slice(0, 5).map(function (x) {
            var n = A.reduce(function (s, a) { return s + x[a].A[0]; }, 0), m = A.reduce(function (s, a) { return s + x[a].A[2]; }, 0);
            return '<li><button type="button" class="pa-ej" data-pa-pregunta="' + esc('Señales de fraccionamiento de ' + x.s) + '">' + esc(x.n) + '</button> ' + n + ' grupos, ' + pesosCmx(m) + '</li>';
          }).join('') + '</ol>';
        A.forEach(function (a) { ci.push({ v: T[a].A[0].toLocaleString('es-MX') + ' grupos', etq: a + ' · rebasan el tope más alto del Anexo 9 en ' + M.ventana + ' días (' + pesosCmx(T[a].A[2]) + ')', e: 'derivado' }); });
        A.forEach(function (a) { ci.push({ v: pesosCmx(M.anexo9[a].max), etq: a + ' · tope más alto de adjudicación directa, Anexo 9 del PEF', e: 'oficial' }); });
      }
      h += fraccCaveat();
      h += charla && charla.deDonde ? charla.deDonde([{ que: 'Datos relevantes de los contratos de ComprasMX', e: 'oficial', fu: fu }, { que: 'Topes del Anexo 9 del PEF', e: 'oficial', fu: fuentes[1] }]) : '';
      var tit = f ? 'Señales de fraccionamiento: ' + f.n : 'Señales de fraccionamiento en ComprasMX';
      return { html: h, ir: [FRACC_PAG, 'Contratos públicos'], rec: [],
        ficha: { t: 'calculo', tit: tit, txt: texto(h), ci: ci, fu: fuentes, ir: [FRACC_PAG, 'Contratos públicos'] },
        sug: f ? ['¿A quién le compra ' + f.s + '?', 'Señales de fraccionamiento en ComprasMX'] : ['Señales de fraccionamiento del IMSS', '¿A quién le compra el IMSS?'] };
    }, function () { return { html: '<p>No pude descargar ahora las señales de fraccionamiento. Revisa tu conexión y vuelve a preguntarme.</p>', ir: [FRACC_PAG, 'Contratos públicos'], sug: [], rec: [] }; }),
      tit: 'Señales de fraccionamiento' };
  }
  /* --- A quién le deben los estados y los municipios (17-11-2026, pedido del autor:
     «prosigue con estos pendientes y las deudas»). El Registro Público Único de
     Hacienda, crédito por crédito (herramientas/anclar_rpu.py escribe
     assets/auditor/data/deuda-rpu.js; se descarga solo al preguntar). Cada crédito
     es «oficial»; las sumas y los órdenes, «derivado». El Sistema de Alertas dice
     cuánto debe y cuánto le pesa; el registro dice a quién, a qué tasa y para qué. --- */
  function rpuDatos() { return cargaJs('assets/auditor/data/deuda-rpu.js', function () { return window.AUDIT_RPU; }); }
  var RPU_BANCO = [['banobras', 'Banobras'], ['banorte', 'Banorte'], ['bbva', 'BBVA'], ['bancomer', 'BBVA'], ['santander', 'Santander'], ['banamex', 'Banamex'],
    ['invex', 'Invex'], ['hsbc', 'HSBC'], ['bajio', 'BanBajío'], ['bansi', 'Bansí'], ['multiva', 'Multiva'], ['mifel', 'Mifel'], ['scotiabank', 'Scotiabank'],
    ['banco azteca', 'Banco Azteca'], ['afirme', 'Afirme'], ['cibanco', 'CIBanco'], ['nafin', 'Nafin'], ['interacciones', 'Interacciones']];
  function rpuPide(p) {
    if (/ (que|q) (es|son|significa) /.test(p) && !/ (debe|deben|deuda|credit|prest)/.test(p)) return false;
    var banco = RPU_BANCO.filter(function (b) { return p.indexOf(' ' + b[0] + ' ') >= 0; })[0];
    if (banco && / (debe|deben|deuda|deudas|credito|creditos|presta|prestan|presto|prestamo|prestamos|endeud\w*) /.test(p)) return { banco: banco[1] };
    if (/ (a|con) quien(es)? (le |les )?(debe|deben|esta endeudad\w*|estan endeudad\w*)| acreedor(es)? | registro publico unico | rpu | (que|cuales|con que|cuantos) bancos? | bancos? (le |les )?(presta|prestan|prestaron|presto) /.test(p) ||
      / (sus |los |la |de )?(creditos|prestamos) (bancarios |de la deuda )?(de|del) / .test(p) && /(estado|municipi|gobierno|deuda|[a-z]{4,})/.test(p)) return { banco: null };
    return false;
  }
  function rpuMdp(v) { return '$' + Number(v).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' millones'; }
  function rpuOjo(D, L) {
    var T = D.tipo, hay = function (s) { return L.some(function (x) { return x[8] && T[x[5]] === s; }); }, n = D.meta.tipoNota, o = [];
    if (hay('Emisión bursátil')) o.push('en una <b>emisión bursátil</b> ' + esc(n['Emisión bursátil']));
    if (hay('Obligación relacionada con asociaciones público - privadas')) o.push('una <b>APP</b> es ' + esc(n['Obligación relacionada con asociaciones público - privadas']));
    if (hay('Obligación a corto plazo')) o.push('el <b>corto plazo</b> es ' + esc(n['Obligación a corto plazo']));
    if (L.some(function (x) { return D.dest[x[11]] === 'Refinanciamiento sin autorización'; })) o.push('«refinanciamiento sin autorización» es el nombre del registro para el refinanciamiento que, por mejorar las condiciones, no necesita el voto del Congreso local (LDF, art. 23): no quiere decir que sea ilegal');
    o.push('BBVA Bancomer es el nombre que BBVA México tenía hasta 2019, y el registro conserva el nombre con que se firmó cada crédito');
    return '<p class="pa-ojo">Ojo: ' + o.join('; ') + '. Tener deuda no es una irregularidad, y este registro no dice si se usó bien. El saldo es el que cada gobierno le reporta a Hacienda cada trimestre, y no se suma con el del Sistema de Alertas, que mide al cierre de 2025 solo lo que se paga con ingresos de libre disposición.</p>';
  }
  function rpuLi(D, x, conDeudor) {
    var I = D.inst[x[4]], t = D.tipo[x[5]];
    return '<li>' + (conDeudor ? '<b>' + esc(x[2]) + '</b> con ' : '') + '<b>' + esc(I[0]) + '</b>: ' + (x[8] ? 'debe <b>' + rpuMdp(x[8]) + '</b>' : 'sin saldo reportado') +
      ' de ' + rpuMdp(x[7]) + ' contratados' + (x[6] ? ' el ' + esc(x[6].split('-').reverse().join('-')) : '') + ' · ' + esc(t.toLowerCase()) +
      (x[9] != null ? ' · tasa efectiva ' + Number(x[9]).toLocaleString('es-MX') + ' %' : '') + (x[10] ? ' · vence ' + esc(x[10].split('-').reverse().join('-')) : '') +
      '<br><span class="pa-chico">Para: ' + esc(D.dest[x[11]]) + (D.fte[x[12]] !== '—' && D.fte[x[12]] !== '-' ? ' · se paga con: ' + esc(D.fte[x[12]]) : '') + '</span></li>';
  }
  function deudaRpu(q) {
    var p = plano(q), pide = rpuPide(p);
    if (!pide) return null;
    var lu = charla && charla.lugar ? charla.lugar(q) : { e: [], m: null }, e = lu.e.length === 1 ? lu.e[0] : null, m = lu.m;
    return { espera: rpuDatos().then(function (D) {
      var M = D.meta, R = D.r, h, tit, ci = [], sug = [];
      var porBanco = function (x) { return !pide.banco || D.inst[x[4]][0].indexOf(pide.banco) === 0; };
      var suma = function (L) { return L.reduce(function (s, x) { return s + (x[8] || 0); }, 0); };
      var agrupa = function (L, k) { var o = {}; L.forEach(function (x) { if (x[8]) { var c = k(x); o[c] = (o[c] || 0) + x[8]; } }); return Object.keys(o).map(function (c) { return [c, o[c]]; }).sort(function (a, b) { return b[1] - a[1] || (a[0] < b[0] ? -1 : 1); }); };
      var L;
      if (m) {
        L = R.filter(function (x) { return x[3] === m.cve && porBanco(x); }).sort(function (a, b) { return (b[8] || 0) - (a[8] || 0); });
        tit = 'A quién le debe ' + m.n + ', ' + m.en;
        if (!L.length) h = '<p>El municipio de <b>' + esc(m.n) + '</b>, ' + esc(m.en) + ', no tiene ' + (pide.banco ? 'créditos con ' + esc(pide.banco) : 'créditos ni obligaciones') + ' inscritos en el <b>Registro Público Único</b> de Hacienda ' + chip({ e: 'oficial' }) + '. Eso no quiere decir que no le deba a nadie: los adeudos con proveedores, por ejemplo, no pasan por ese registro.</p>';
        else {
          var con = L.filter(function (x) { return x[8]; });
          h = '<p>🏦 El municipio de <b>' + esc(m.n) + '</b>, ' + esc(m.en) + ', tiene <b>' + L.length + '</b> crédito' + (L.length === 1 ? '' : 's') + ' u obligaci' + (L.length === 1 ? 'ón' : 'ones') + (pide.banco ? ' con ' + esc(pide.banco) : '') + ' inscrit' + (L.length === 1 ? 'o' : 'os') + ' en el Registro Público Único ' + chip({ e: 'oficial' }) +
            (con.length ? '; con saldo al ' + esc(M.corteTxt) + ' debe <b>' + rpuMdp(suma(con)) + '</b> ' + chip({ e: 'derivado' }) : '; ninguno reporta saldo al ' + esc(M.corteTxt)) + ':</p><ol class="pa-lista">' + L.slice(0, 8).map(function (x) { return rpuLi(D, x); }).join('') + '</ol>' +
            (L.length > 8 ? '<p class="pa-chico">Te muestro 8 de ' + L.length + '.</p>' : '');
          con.slice(0, 5).forEach(function (x) { ci.push({ v: rpuMdp(x[8]), etq: m.n + ' · ' + D.inst[x[4]][0] + ' · ' + D.tipo[x[5]], e: 'oficial' }); });
        }
        sug = ['¿Cuánto debe el municipio de ' + m.n + '?', '¿A quién le debe ' + m.en + '?'];
      } else if (e) {
        L = R.filter(function (x) { return x[0] === e.a && porBanco(x); });
        var con2 = L.filter(function (x) { return x[8]; }), tot = suma(con2), k = agrupa(L, function (x) { return x[1]; }), kn = { e: e.a === 'CDMX' ? 'el gobierno de la Ciudad' : 'el gobierno del estado', m: 'sus municipios', o: 'sus organismos (agua, transporte, fideicomisos…)' };
        tit = 'A quién le debe ' + e.n + (pide.banco ? ' · ' + pide.banco : '');
        var ac = agrupa(L, function (x) { return D.inst[x[4]][0]; });
        var gob = con2.filter(function (x) { return x[1] === 'e'; }).sort(function (a, b) { return b[8] - a[8]; });
        h = '<p>🏦 En <b>' + esc(e.n) + '</b>, el Registro Público Único de Hacienda tiene <b>' + L.length + '</b> créditos y obligaciones inscritos' + (pide.banco ? ' con <b>' + esc(pide.banco) + '</b>' : '') + ' ' + chip({ e: 'oficial' }) + '; <b>' + con2.length + '</b> reportan saldo al ' + esc(M.corteTxt) + ' y suman <b>' + rpuMdp(tot) + '</b> ' + chip({ e: 'derivado' }) + '.</p>' +
          (k.length ? '<p>Lo deben ' + k.map(function (x) { return kn[x[0]] + ' (' + rpuMdp(x[1]) + ')'; }).join(', ') + '.</p>' : '') +
          (!pide.banco && ac.length ? '<p>A quién ' + chip({ e: 'derivado' }) + ':</p><ol class="pa-lista">' + ac.slice(0, 6).map(function (x) { return '<li><b>' + esc(x[0]) + '</b>: ' + rpuMdp(x[1]) + ', el ' + (x[1] / tot * 100).toLocaleString('es-MX', { maximumFractionDigits: 1 }) + ' %</li>'; }).join('') + '</ol>' : '') +
          (gob.length ? '<p>Los créditos más grandes del gobierno ' + (e.a === 'CDMX' ? 'de la Ciudad' : 'del estado') + ' ' + chip({ e: 'oficial' }) + ':</p><ol class="pa-lista">' + gob.slice(0, 5).map(function (x) { return rpuLi(D, x); }).join('') + '</ol>' : '');
        if (pide.banco && !gob.length) h += '<ol class="pa-lista">' + con2.sort(function (a, b) { return b[8] - a[8]; }).slice(0, 6).map(function (x) { return rpuLi(D, x, true); }).join('') + '</ol>';
        ci.push({ v: rpuMdp(tot), etq: e.n + ' · saldo de sus créditos inscritos en el Registro Público Único al ' + M.corteTxt, e: 'derivado' });
        ac.slice(0, 5).forEach(function (x) { ci.push({ v: rpuMdp(x[1]), etq: e.n + ' · le debe a ' + x[0], e: 'derivado' }); });
        sug = ['¿Cuánto debe ' + e.n + '?', '¿Qué municipios de ' + e.n + ' tienen deuda elevada?'];
      } else {
        L = R.filter(porBanco);
        var con3 = L.filter(function (x) { return x[8]; }), tot3 = suma(con3), en = agrupa(L, function (x) { return x[0]; });
        var nomE = function (a) { return M.ent[a] || a; };
        tit = pide.banco ? 'Lo que le deben a ' + pide.banco + ' los estados y los municipios' : 'A quién le deben los estados y los municipios';
        h = '<p>🏦 En el <b>Registro Público Único</b> de Hacienda hay <b>' + L.length.toLocaleString('es-MX') + '</b> créditos y obligaciones de estados, municipios y sus organismos' + (pide.banco ? ' con <b>' + esc(pide.banco) + '</b>' : '') + ' ' + chip({ e: 'oficial' }) + '; <b>' + con3.length.toLocaleString('es-MX') + '</b> reportan saldo al ' + esc(M.corteTxt) + ' y suman <b>' + rpuMdp(tot3) + '</b> ' + chip({ e: 'derivado' }) + '.</p>';
        if (!pide.banco) {
          var ac3 = agrupa(L, function (x) { return D.inst[x[4]][0]; });
          h += '<p>A quién le deben más ' + chip({ e: 'derivado' }) + ':</p><ol class="pa-lista">' + ac3.slice(0, 6).map(function (x) { return '<li><b>' + esc(x[0]) + '</b>: ' + rpuMdp(x[1]) + ', el ' + (x[1] / tot3 * 100).toLocaleString('es-MX', { maximumFractionDigits: 1 }) + ' %</li>'; }).join('') + '</ol>';
          ac3.slice(0, 5).forEach(function (x) { ci.push({ v: rpuMdp(x[1]), etq: 'Estados y municipios le deben a ' + x[0], e: 'derivado' }); });
        }
        h += '<p>Las entidades donde más se debe' + (pide.banco ? ' a ' + esc(pide.banco) : '') + ', sumando gobierno, municipios y organismos ' + chip({ e: 'derivado' }) + ':</p><ol class="pa-lista">' + en.slice(0, 5).map(function (x) {
          return '<li><button type="button" class="pa-ej" data-pa-pregunta="' + esc('¿A quién le debe ' + nomE(x[0]) + '?') + '">' + esc(nomE(x[0])) + '</button> ' + rpuMdp(x[1]) + '</li>'; }).join('') + '</ol>';
        ci.push({ v: rpuMdp(tot3), etq: (pide.banco ? 'Lo que le deben a ' + pide.banco : 'Saldo de los créditos de estados y municipios') + ' en el Registro Público Único al ' + M.corteTxt, e: 'derivado' });
        sug = en.slice(0, 2).map(function (x) { return '¿A quién le debe ' + nomE(x[0]) + '?'; }).concat(['¿Qué municipios tienen deuda elevada?']);
      }
      h += rpuOjo(D, L || []);
      var fu = { tx: M.fuente + ', registro diario descargado el ' + M.descarga.split('-').reverse().join('-') + ' (saldo al ' + M.corteTxt + ', sha256 ' + M.sha256.slice(0, 12) + '…)', url: M.pagina };
      var fus = [{ que: 'Cada crédito: deudor, acreedor, tipo, monto, saldo, tasa, vencimiento, destino y fuente de pago', e: 'oficial', fu: fu },
        { que: 'Totales y órdenes', e: 'derivado', op: 'sumamos el saldo de los créditos que lo reportan y los agrupamos por acreedor o por entidad; los que Hacienda publica con «-» no suman' }];
      h += charla && charla.deDonde ? charla.deDonde(fus) : '';
      var clave = e ? e.a.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase() : m ? m.a.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase() : '';
      var ir = clave ? ['planisferio-' + clave + '-deuda.html', 'la deuda de ' + (e ? e.n : m.en) + ' en el Planisferio'] : ['planisferio.html?d=deuda', 'la deuda en el Planisferio'];
      return { html: h, ir: ir, rec: [], ficha: { t: 'calculo', tit: tit, txt: texto(h), ci: ci, fu: [fu], ir: ir }, sug: sug };
    }, function () { return { html: '<p>No pude descargar ahora el Registro Público Único. Revisa tu conexión y vuelve a preguntarme.</p>', ir: ['planisferio.html?d=deuda', 'la deuda en el Planisferio'], sug: [], rec: [] }; }),
      tit: 'A quién le deben' };
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
  /* La liga sin protocolo, www, consulta ni diagonal final (liga_plana de asistente_personajes.py). */
  function ligaPlana(u) { return String(u || '').trim().toLowerCase().replace(/^https?:\/\//, '').replace(/^www\./, '').split(/[?#]/)[0].replace(/\/+$/, ''); }
  function hemeroteca(liga) {
    var H = (B.dat && B.dat.per && B.dat.per.hem) || [], u = ligaPlana(liga);
    var h = H.filter(function (x) { return x.u === u; })[0];
    var f = h && (B.fichas || []).filter(function (x) { return x.t === 'columna' && x.col === h.col; })[0];
    if (!f || !charla) return null;
    var r = charla.deFicha(f);
    r.html = '<p>🗂️ Esa nota ya está en nuestra <b>hemeroteca</b>: ' + esc(h.m) + (h.f ? ', ' + esc(h.f) : '') + ', «' + esc(h.t) + '». ' +
      (h.rol === 'origen' ? 'De ella partimos para este cotejo' : 'Es una de las notas que contaron el mismo hecho') + ', y esto es lo que consta en los documentos oficiales:</p>' + r.html +
      '<p class="pa-chico">El titular de un medio no es la fuente: lo que vale es el documento que va junto a cada afirmación. ¿Quieres revisar la nota cifra por cifra? <a href="' + esc(APP.inspnota.url + '?liga=' + encodeURIComponent(liga)) + '">Contrástala aquí</a>.</p>';
    return r;
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
    /* 2a. La hemeroteca (31-10-2026): si la liga es de una nota que ya cotejamos, se dice y se abre su cotejo. */
    var hem = liga && hemeroteca(liga);
    if (hem) return hem;
    /* 2 bis. La liga sola de una red social (08-11-2026, ejemplo del autor): Instagram, Facebook,
       X o TikTok no dejan que un lector externo abra la publicación, así que no se promete leerla:
       se pide el texto, que con la liga entra a lectura() y se lee aquí mismo. */
    var red = liga && /^https?:\/\/(?:[a-z0-9-]+\.)*(instagram\.com|facebook\.com|fb\.watch|x\.com|twitter\.com|tiktok\.com|threads\.net)\//i.exec(liga);
    if (red && t.replace(liga, '').replace(/\s+/g, ' ').trim().length < 60) {
      var rn = { 'instagram.com': 'Instagram', 'facebook.com': 'Facebook', 'fb.watch': 'Facebook', 'x.com': 'X', 'twitter.com': 'X', 'tiktok.com': 'TikTok', 'threads.net': 'Threads' }[red[1].toLowerCase()];
      return { html: '<p>🔒 <b>' + rn + ' no deja que nadie de fuera lea sus publicaciones</b>, ni nosotros: sin el texto no puedo decirte qué afirma ni compararlo con un documento, y no voy a adivinarlo.</p>' +
        '<p>📋 <b>Copia el texto de la publicación</b> (el pie de foto o lo que dice el video) y pégalo aquí <b>junto con la liga</b>. Con eso te digo lo que afirma en cifras, si ya lo cotejamos, qué promesa toca, en qué etapa va y qué preguntas le faltan.</p>' +
        '<p class="pa-chico">Revisé la liga contra nuestra hemeroteca y no está entre las notas que ya cotejamos. Si es un video sin texto, cuéntame con tus palabras qué dice y quién lo dice.</p>',
        ir: [APP.inspnota.url + '?liga=' + encodeURIComponent(liga), APP.inspnota.n], sug: [], rec: [], red: 1 };
    }
    /* 2. La liga de una nota: «Contrasta una nota» la lee aquí mismo. */
    if (liga) {
      return respApp('inspnota', APP.inspnota.url + '?liga=' + encodeURIComponent(liga),
        '<p>📰 Leo la nota aquí mismo con <b>Contrasta una nota</b>: busco sus cifras en pesos, las pongo junto a su documento oficial y te doy el veredicto, cifra por cifra, con su semáforo. Puede tardar unos segundos.</p>' +
        '<p class="pa-chico">Lo que no empata con un documento queda «sin contrastar» y no cuenta como falso. Si la página no se deja leer, ahí mismo puedes pegar el texto.</p>');
    }
    /* 2a. Un estado de resultados propio (05-11-2026): «revisa mi estado de resultados», «analiza los estados
       financieros de mi empresa». «El estado de resultados del Gobierno» no entra aquí: no dice mi, empresa ni revisa. */
    if (APP.inspresultados && /estados? de resultados|estados? financieros/.test(p) && /\b(mi|mis|nuestro|nuestros|empresa|negocio|cliente|revisa|revisar|revisame|analiza|analizar|evalua|evaluar|sube|subir)\b/.test(p) && !/gobierno|federal|nacion|del estado de\b/.test(p)) {
      return respApp('inspresultados', APP.inspresultados.url,
        '<p>📊 Te abro <b>Revisa tu estado de resultados</b> aquí abajo. Sube tu CSV o pega las celdas de Excel: lo leo en tu navegador, sin subirlo a ningún lado, y lo reviso en seis dimensiones: cuadre, estructura, rentabilidad, tendencia a 3 y 5 años, impuestos y deuda.</p>' +
        '<p class="pa-chico">Todo sale como derivado, con su operación a la vista, y lo que llama la atención va como «señal para revisar», nunca como irregularidad. No es una auditoría ni un dictamen.</p>');
    }
    /* 2b. Una factura (05-11-2026): «revisa mi factura», «tengo un XML», «¿esta factura es de una
       empresa fantasma?». Abre el Lector de facturas CFDI; un RFC suelto lo sigue contestando la lista negra. */
    if (APP.inspfactura && /\b(facturas?|cfdi|xml|comprobantes? fiscal(es)?|recibos? de nomina)\b/.test(p) && !RFC_RE.test(t) && !/^\s*(que|q) (es|son|significa)\b|que quiere decir/.test(p)) {
      RFC_RE.lastIndex = 0;
      return respApp('inspfactura', APP.inspfactura.url,
        '<p>📑 Te abro el <b>Lector de facturas CFDI</b> aquí abajo. Elige el XML de tu factura (o varios): lo leo en tu navegador, sin subirlo a ningún lado, rehago su cuenta, la reviso contra la ley (régimen fiscal, método y forma de pago, complemento de pago y retención de IVA, cada regla con su artículo) y cruzo al emisor con la lista 69-B del SAT. Si cargas también los complementos de pago, los empato con sus facturas. Si es un recibo de nómina, reviso además su ISR contra la tarifa, el subsidio para el empleo y el salario base de cotización, sin mostrar el nombre de quien trabaja.</p>' +
        '<p class="pa-chico">Separo lo que declaró el SAT (oficial) de las señales que salen de comparar fechas o de revisar el XML (derivado, «señal para revisar»). No te digo si la factura está cancelada: eso lo dice el verificador del SAT con su UUID.</p>');
    }
    RFC_RE.lastIndex = 0;
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
      else if (/\b(servicios? de investigacion|investigacion a la medida|(contratar|solicitar|pedir|encargar|encargarles|cotizar)( una| un)? (investigacion|servicio|revision|expediente)|quiero que investiguen|investiguen (esto|un caso|a)|(que )?servicios (ofrecen|tienen|dan|venden|hay)|(dan|ofrecen|tienen|imparten) (talleres|capacitacion|cursos)|talleres? (para|de) (auditores|contadores|despachos|abogados))\b/.test(p)) id = 'servicios.html';
      else if (/\b(que encontro la asf|expedientes de (la )?asf|casos de la asf|expedientes de casos)\b/.test(p)) id = 'inspasf';
      else if (/\b(modo inspector|grandes investigaciones|(seis|6) aplicaciones|que (puedo|puedes) investigar|como investigo)\b/.test(p)) id = '*';
    }
    if (!id) return null;
    /* «¿Cuánto facturaron las empresas fantasma?» pide la cifra, no la aplicación (igual que en listaNegra). */
    if (id === 'inspefos' && /\b(cuanto|monto|montos|dinero|billones|evasion|evadieron)\b/.test(p)) return null;
    /* «¿Qué es…?» lo contesta el glosario o la página; aquí, quien quiere usarla. */
    if (/^\s*(que|q) (es|son|significa|hace)\b/.test(p) && id !== '*') return null;
    if (id === '*') {
      return {
        html: '<p>🔍 El <b>Modo Inspector</b> son ' + IN.apps.length + ' aplicaciones para grandes investigaciones, y todas las usas desde aquí, sin salir del chat. Dime cuál, o pásame directo lo que traes:</p><ul class="pa-lista">' +
          IN.apps.map(function (a) { return '<li><span aria-hidden="true">' + a.ico + '</span> <b>' + esc(a.n) + '.</b> ' + esc(a.frase) + '. <span class="pa-chico">' + esc(EJ_APP[a.id] || '') + '</span></li>'; }).join('') + '</ul>',
        ir: [IN.pagina, 'el Modo Inspector'], sug: IN.apps.map(function (a) { return a.n; }), rec: []
      };
    }
    /* El tema de una investigación: lo que el lector dijo después de pedirla
       («…sobre el Tren Maya») o, si dice «esto», su pregunta anterior. */
    var tema = id !== 'servicios.html' || !/investig/i.test(t) ? '' : (/\b(sobre|de|del|acerca de|para)\s+(.{3,})$/i.exec(t.replace(/^.*?investigaci[oó]n\b/i, '').replace(/[?¿!¡.]+$/, '')) || [])[2] || '';
    if (/^(esto|eso|este caso|ese caso|lo anterior|lo mismo)$/i.test(tema.trim())) tema = '';
    if (id === 'servicios.html' && !tema && /\b(esto|eso|este caso|ese caso|lo anterior|lo mismo)\b/.test(p) && previas && previas.length) tema = previas[previas.length - 1];

    var a = APP[id];

    var url = id === 'servicios.html' && tema ? 'servicios-cotiza.html?tema=' + encodeURIComponent(tema.slice(0, 160)) + '#solicitud' : a.url;
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
    inspfactura: 'Dime «revisa mi factura» y elige el XML: lo leo sin subirlo y lo cruzo con la lista 69-B.',
    inspresultados: 'Dime «revisa mi estado de resultados» y sube tu CSV: lo leo sin subirlo y lo reviso en seis dimensiones.',
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
  /* Quien trabaja para el gobierno cotiza al ISSSTE (18-11-2026): la calculadora lo distingue con &pt=issste. */
  var GOBIERNO = /\b(issste|burocrata|servidora? publica?|trabajo (en|para) (el |la |una )?(gobierno|dependencia|federacion|secretaria)|soy del gobierno|empleado (del|de) gobierno|me paga el gobierno)\b/;
  function regimenDe(p) {
    var r = REGIMEN.filter(function (x) { return x[1].test(p); })[0], pl = null;
    if (r && r[0] === 'plataformas') pl = PLATA.filter(function (x) { return x[1].test(p); })[0][0];
    var gob = GOBIERNO.test(p) && (!r || r[0] === 'sueldos');
    return { r: r ? r[0] : (gob ? 'sueldos' : ''), pl: pl, pt: gob ? 'issste' : '' };
  }
  /* «¿Cuánto pago de predial en Vallarta?», «debo el predial en Tepatitlán»: el simulador del
     predial, con el municipio ya puesto si su ley está cotejada (19-11-2026). Va antes que la ficha
     del municipio y que Megaobras; «¿cuánto recaudó Zapopan de predial?» sigue yendo a la ficha. */
  function predialResp(q) {
    var p = plano(q), a = APP.ccpredial, C = B.dat.calc || {}, L = C.pred || [], EN = C.predEnt || {};
    if (!a || !/ predial(es)? /.test(p) || /^ (que|q) (es|son|significa) /.test(p) || / (recaud|ingres|cobr(o|aron) el municipio|cuanto (cobra|junta) el municipio)/.test(p)) return null;
    var hit = null;
    /* Gana el nombre más largo: «lagos» (Lagos de Moreno) no le gana a «san juan de los lagos». */
    var largo = 0;
    L.forEach(function (m) { m.n.forEach(function (n) { if (n.length > largo && p.indexOf(' ' + n + ' ') >= 0) { hit = m; largo = n.length; } }); });
    /* Las entidades que nombra la pregunta (homónimos, Ronda 6): «México» a secas no es ninguna, porque es el país. */
    var ents = [];
    Object.keys(EN).forEach(function (k) {
      var n = plano(EN[k]).trim();
      if (k === 'MEX') n = 'estado de mexico';
      if (p.indexOf(' ' + n + ' ') >= 0) ents.push(k);
    });
    if (/ (cdmx|df|distrito federal) /.test(p) && ents.indexOf('CDMX') < 0) ents.push('CDMX');
    if (/ edomex /.test(p) && ents.indexOf('MEX') < 0) ents.push('MEX');
    /* «Ciudad de México» no es «Estado de México». */
    if (ents.indexOf('CDMX') >= 0) ents = ents.filter(function (k) { return k !== 'MEX'; });
    var nomE = function (m) { return m.nom + ', ' + (EN[m.e] || m.e); };
    var otra = '', ent = '', cve = '', esp = null, nivel = '';
    if (hit) {
      var mismo = plano(hit.nom).trim() === plano(EN[hit.e] || '').trim();
      var fuera = ents.filter(function (k) { return k !== hit.e; });
      if (fuera.length && ents.indexOf(hit.e) < 0) {
        /* Nombra otra entidad: «predial en Hidalgo» es el estado de Hidalgo, no Hidalgo, Nuevo León; «Guadalupe, Zacatecas» no es Guadalupe, Nuevo León. */
        otra = '<p class="pa-chico">Ojo con el homónimo: el que tenemos cotejado es <b>' + esc(nomE(hit)) + '</b>' + (hit.h.indexOf(fuera[0]) >= 0 || plano(EN[fuera[0]] || '').trim() === plano(hit.nom).trim() ? ', no el de ' + esc(EN[fuera[0]]) : '') +
          '. Si es ese el tuyo, <a href="' + esc(a.url + '?mun=' + hit.id) + '">ábrelo aquí</a>.</p>';
        ent = fuera[0];
        hit = null;
      } else if (mismo) {
        nivel = '<p class="pa-chico"><b>' + esc(hit.nom) + '</b> es el nombre del estado y de su capital. El predial no lo cobra el estado: lo cobra cada municipio con su propia ley. Te abrí el <b>municipio de ' + esc(nomE(hit)) + '</b>; los demás municipios del estado de ' + esc(EN[hit.e]) + ' aún no están cotejados.</p>';
      } else if (hit.h.length && !ents.length) {
        otra = '<p class="pa-chico">Ojo con los homónimos: hay un municipio que se llama ' + esc(hit.nom) + ' en ' + esc(hit.h.map(function (k) { return EN[k] || k; }).join(', ')) +
          '. Te abrí <b>' + esc(nomE(hit)) + '</b>, el único que tenemos cotejado; si el tuyo es otro, elige su estado en la página.</p>';
      }
    }
    if (!hit) {
      /* Una ley que leímos y quedó en espera (León, Guanajuato): se dice, no se calcula. */
      (C.predEsp || []).forEach(function (w) { if (!esp && p.indexOf(' ' + w.n + ' ') >= 0 && (!ents.length || ents.indexOf(w.k.split('-')[0]) >= 0)) esp = w; });
      if (esp) { ent = esp.k.split('-')[0]; cve = esp.k.split('-')[1]; }
      else if (!ent && ents.length) ent = ents[0];
    }
    var liga = a.url + (hit ? '?mun=' + hit.id : ent ? '?ent=' + ent + (cve ? '&cve=' + cve : '') : '');
    var puse = hit ? ', y ya le puse ' + (/^cdmx/.test(hit.id) ? 'la alcaldía ' : 'el municipio ') + '<b>' + esc(nomE(hit)) + '</b>' :
      esp ? ', y ya le puse <b>' + esc(esp.nom + ', ' + (EN[ent] || ent)) + '</b>' :
      ent ? ', y ya le puse ' + (ent === 'CDMX' ? 'la Ciudad de México (la tarifa es la misma en las 16 alcaldías)' : 'el estado de <b>' + esc(EN[ent] || ent) + '</b>: elige ahí tu municipio') : '';
    return respApp('ccpredial', liga, '<p><span aria-hidden="true">' + a.ico + '</span> Esa cuenta la hace <b>' + esc(a.n) + '</b>, de la ' + esc(a.grupo) + puse +
      ': escribe el valor fiscal de tu predio (viene en tu recibo) y te dice tu predial del año con la tarifa de su ley (su Ley de Ingresos; en Nuevo León, la Ley de Hacienda para los Municipios; en la Ciudad de México, el Código Fiscal), sus descuentos y, si debes bimestres, la actualización, los recargos, la multa y los gastos de cobranza, cada uno con su artículo.</p>' +
      nivel + otra +
      (esp ? '<p class="pa-chico"><span class="est-chip est-pendiente">pendiente</span> Leímos su Ley de Ingresos, pero aún no la integramos: ' + esc(esp.m) + ' No adivinamos una tasa.</p>' : '') +
      '<p class="pa-chico">La cuenta la hace el simulador, no el chat. Cada municipio cobra con su propia ley; si el tuyo aún no está cotejado, la página te lo dice y te da cuánto recaudó de predial.</p>',
      { sug: ['Me llegó un mandamiento de ejecución por no pagar el predial', '¿Cuánto recaudó de predial mi municipio?', 'Vendes una casa o un terreno'] });
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
      var liga = 'herramienta-calculadora-ticket-retienen.html' + (m ? '?m=' + m + '&p=' + per + '&n=' + nat + (rg.r ? '&r=' + rg.r : '') + (rg.pl ? '&pl=' + rg.pl : '') + (rg.pt ? '&pt=' + rg.pt : '') : '');
      var regN = rg.r && CR.reg ? CR.reg[rg.r] : '', plN = rg.pl && CR.plat ? CR.plat[rg.pl] : '';
      var hijos = /\b(hijos?|hijas?|dependientes?|esposa|esposo|familia)\b/.test(p);
      return respApp('ccticket', liga, '<p><span aria-hidden="true">🧾</span> Esa cuenta la hace <b>' + esc(cc.n) + '</b>, de la ' + esc(cc.grupo) + ': ' +
        (m ? 'ya le puse tu ingreso de <b>$' + m.toLocaleString('es-MX') + (per === 'ano' ? ' al año' : ' al mes') + '</b>, ' + (nat === 'neto' ? 'después' : 'antes') + ' de descuentos' +
          (regN ? ', en <b>' + esc(regN) + '</b>' + (plN ? ' (' + esc(plN.toLowerCase()) + ')' : '') : '') + (rg.pt ? ', como quien trabaja para el gobierno y cotiza al <b>ISSSTE</b>' : '') + '. ' :
          sem ? 'la calculadora trabaja por mes o por año, así que escribe ahí lo que juntas al mes (no convierto semanas: los meses no tienen semanas exactas). ' : 'escribe lo que ganas. ') +
        'Te dice cuánto te retienen, con la tarifa oficial del ISR, lo que pone tu patrón ' + (rg.pt ? '(tu dependencia, al ISSSTE y al FOVISSSTE)' : '(al IMSS y al INFONAVIT)') + ' y cuánto cuesta tu plaza, y a dónde va cada peso de tu impuesto, en un documento con folio y huella.</p>' +
        (rg.pt ? '<p class="pa-chico">Las cuotas salen de la Ley del ISSSTE (10.625% de tu sueldo básico). Si tu estado o tu municipio tiene su propio instituto de seguridad social, tus cuotas son otras.</p>' : '') +
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
      { que: (o.pet || (o.resc ? 'Presentado en su momento' : 'Aprobado')) + ': ' + c.pres.vt, e: c.pres.e, p: c.pres.p, op: c.pres.op || c.pres.d },
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
    var nomP = o.pet || (o.resc ? 'Presentado en su momento' : 'Aprobado'), nomR = o.resc ? 'Pagado y debido' : 'Costo real';
    if (foco === 'amb' && o.amb) lead = '📍 Se ubica en <b>' + esc(o.amb.sede) + '</b>. Costó <b>' + esc(c.real.vt) + '</b> ' + chipE(c.real) +
      '. <br>🚨 <b>Alerta del Auditor Ambiental (' + esc(o.amb.eco) + '):</b> ' + esc(o.amb.alerta) +
      ' Permiso ambiental (MIA): ' + chip({ e: o.amb.miaEst, p: o.amb.miaPend }) + ' (' + esc(o.amb.miaTxt) + ').';
    else if (foco === 'sob') lead = o.resc ? 'Es un rescate, no una obra: su «sobrecosto» es lo que creció la deuda frente a lo que se presentó, <b>' + esc(c.sob.vt) + '</b> ' + chipE(c.sob) + '.' :
      'Su sobrecosto es de <b>' + esc(c.sob.vt) + '</b> ' + chipE(c.sob) + ': se aprobaron ' + esc(c.pres.vt) + ' y costó ' + esc(c.real.vt) + '.';
    else if (foco === 'res') lead = o.res.tipo === 'dato' ? 'Al año, ' + (o.res.v < 0 ? '<b class="pa-rojo">pierde ' : '<b class="pa-verde">gana ') + esc(o.res.vt) + '</b> por sí misma (' + o.res.anio + ', ' + esc(o.res.base) + ') ' + chipE(o.res) + '.' +
      (netaHoy(o) ? ' En pesos de ' + esc(MO.mes) + ' son ' + esc(netaHoy(o)) + ' ' + chip({ e: 'derivado' }) + '.' : '') :
      o.res.tipo === 'no_aplica' ? 'No opera, así que no tiene ganancia ni pérdida del año: ' + esc(o.res.txt) : 'No publica lo que gana o pierde al año ' + chipE({ e: 'pendiente', p: o.res.p }) + ': ' + esc(o.res.txt);
    else if (foco === 'pres') lead = (o.resc ? 'Se presentó en su momento con ' : o.pet ? 'No hay presupuesto aprobado publicado; se anunció con ' : 'Se aprobó con ') + '<b>' + esc(c.pres.vt) + '</b> ' + chipE(c.pres) + '.';
    else if (foco === 'salud') lead = 'Su salud financiera, en su estado de resultados básico: lo que ingresa, lo que gasta en operar, lo que paga de intereses y su resultado del año.' +
      (o.res.tipo === 'dato' ? ' Cierra con ' + (o.res.v < 0 ? '<b class="pa-rojo">▼ pérdida de ' : '<b class="pa-verde">▲ ganancia de ') + esc(o.res.vt) + '</b> (' + o.res.anio + ').' : '');
    else if (foco === 'asf') lead = o.asf ? '<b>Lo que dijo la ASF:</b> ' + esc(o.asf) : 'La plataforma todavía no integra un documento de la ASF sobre esta obra ' + chip({ e: 'pendiente', p: 'obra-' + o.id }) + '.';
    else lead = (o.resc ? 'Lo pagado y lo que se sigue debiendo suma ' : 'Costó ') + '<b>' + esc(c.real.vt) + '</b> ' + chipE(c.real) + (o.resc ? '' : ', contra lo ' + (o.pet ? 'anunciado' : 'aprobado') + ': ' + esc(c.pres.vt)) + '.';
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
      fila(a.pet || b.pet ? 'Aprobado o anunciado' : 'Aprobado', v(a.c.pres) + (a.pet ? ' <small>(' + esc(a.pet.toLowerCase()) + ')</small>' : ''), v(b.c.pres) + (b.pet ? ' <small>(' + esc(b.pet.toLowerCase()) + ')</small>' : '')) + fila('Costo real', v(a.c.real), v(b.c.real)) +
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
      '<li>Costo real de las ' + T.n + ' obras: <b>' + esc(T.realt) + '</b> ' + chip({ e: 'derivado' }) + ', contra ' + esc(T.presut) + ' previstos (aprobados o, si no se publicó el presupuesto, anunciados).</li>' +
      '<li>Pagado de más sobre lo previsto: <b>' + esc(T.brechat) + '</b> ' + chip({ e: 'derivado' }) + '.</li>' +
      '<li>Lo que pierden al año las que publican su resultado: <b>' + (T.neto < 0 ? '−' : '+') + esc(T.netot) + '</b> ' + chip({ e: 'derivado' }) + ' (' + T.npierde + ' pierden ' + esc(T.pierdet) + ' y ' + T.ngana + ' gana ' + esc(T.ganat) + ').</li>' +
      '<li>Sin resultado publicado: ' + T.npend + ' ' + chip({ e: 'pendiente', p: 'tema-megaobras' }) + '. No operan: ' + T.nna + '.</li></ul>' +
      '<p class="pa-chico">' + esc(T.medida) + '</p>' +
      (lista ? '<p>Y sus cinco aplicaciones las usas desde aquí:</p><ul class="pa-lista">' + MO.apps.map(function (a) {
        return '<li><span aria-hidden="true">' + a.ico + '</span> <b>' + esc(a.n) + '.</b> ' + esc(a.frase) + '. <span class="pa-chico">' + esc(MO_EJ[a.id] || '') + '</span></li>';
      }).join('') + '</ul>' : '') + portalesHtml() +
      (charla && charla.deDonde ? charla.deDonde([
        { que: 'Costo real de las ' + T.n + ' obras', e: 'derivado', op: 'suma del costo registrado de cada obra, sin los rescates' },
        { que: 'Pagado de más', e: 'derivado', op: 'costo real − lo previsto (' + T.realt + ' − ' + T.presut + ')' },
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
    // La inversión de un gobierno estatal (su obra directa o lo que pasa a sus
    // organismos) la contesta la charla con el INEGI, no el mapa ambiental.
    if (ab && !pideAmb && /invers|invierte|invirti|obra publica|organismos? de (obra|infraestructura)/.test(p)) return null;

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
      (emp ? '' : webVivoHtml(nombre)) +
      '<div class="pa-rec-lista">' + (emp ? PE.webEmp : PE.web).map(function (w) {
        var portal = w.site && w.site.indexOf('https://') === 0;
        var u = portal ? w.site : w.site ? 'https://www.google.com/search?q=' + encodeURIComponent(q + ' ' + w.site)
          : 'https://news.google.com/search?q=' + encodeURIComponent(q) + '&hl=es-419&gl=MX&ceid=MX:es-419';
        return '<a class="pa-rec-a" href="' + esc(u) + '" target="_blank" rel="noopener noreferrer"><span class="pa-rec-ico" aria-hidden="true">' + w.ico + '</span>' +
          '<span><b>' + esc(w.n) + '</b><small>' + (portal ? 'Portal oficial · escribe ahí ' + esc(q) + ' ↗' : w.e === 'oficial' ? 'Fuente oficial · se abre en otra pestaña ↗' : 'Prensa: sin verificar · se abre en otra pestaña ↗') + '</small></span></a>';
      }).join('') + '</div>' +
      '<p class="pa-chico">¿Encontraste una nota con cifras? Pégame aquí su liga y la cotejo contra los documentos oficiales, con <a href="herramienta-inspector-nota.html">Contrasta una nota</a>.</p></div>';
  }
  /* Contratos × lista 69-B × ASF (04-11-2026, herramientas/cruce_contratos.py,
     octava aplicación del Modo Inspector). El chat no rehace el cruce: solo
     menciona el hallazgo («señal para revisar»), o el antecedente si hoy no hay
     ninguno, y lleva a su sección de la página. */
  var CRU = (B.dat && B.dat.cru) || null;
  function cruceUna(rfc) {
    if (!CRU) return '';
    var hs = CRU.hall.filter(function (x) { return x.rfc === rfc; }), a = CRU.ant[rfc];
    if (hs.length) return '<p>🚩 <b>Señal para revisar</b> ' + chip({ e: 'derivado' }) + ': ' + esc(hs[0].tx.toLowerCase()) + ', ' + hs[0].dias + ' días después de su publicación en el DOF. <a href="' + esc(CRU.pag) + '#e-' + esc(rfc) + '">Ver el cruce ›</a></p>';
    if (a) return '<p>🗂️ <b>Antecedente</b>, sin señal: ' + esc(a.tx.toLowerCase()) + '. <a href="' + esc(CRU.pag) + '#e-' + esc(rfc) + '">Ver el cruce ›</a></p>';
    return '';
  }
  var CRU_LISTA = '(69 ?b|lista negra|efos|fantasmas?|factureras?)', CRU_TIEMPO = '(asf|auditoria superior|dof|fecha|antes|despues|ano por ano|por ano|historic\\w*|desde)';
  var CRU_RE = new RegExp('\\b(compranet|cruce de contratos|contratos lista 69 ?b y asf)\\b|' +
    '\\b(contrat\\w*|proveedor\\w*|empresas?|compr[oa]\\w*)\\b.*\\b' + CRU_LISTA + '\\b.*\\b' + CRU_TIEMPO + '\\b|' +
    '\\b' + CRU_TIEMPO + '\\b.*\\b' + CRU_LISTA + '\\b.*\\b(contrat\\w*|proveedor\\w*)\\b|' +
    '\\b' + CRU_LISTA + '\\b.*\\b(contrat\\w*|proveedor\\w*)\\b.*\\b' + CRU_TIEMPO + '\\b');
  function cruceAsf(q) {
    var t = plano(q);
    if (!CRU || !CRU_RE.test(t) || (q.match(RFC_RE) || []).length) return null;
    var h, ir, fu = [{ que: 'Listado del artículo 69-B del Código Fiscal (corte al ' + CRU.sat.corte + ')', e: 'oficial', fu: { tx: 'SAT', url: CRU.sat.url } },
      { que: CRU.asf.doc, e: 'oficial', fu: { tx: 'ASF', url: CRU.asf.url } }];
    if (CRU.hall.length) {
      var x = CRU.hall[0];
      h = '<p>🚩 <b>Hallazgo</b> ' + chip({ e: 'derivado' }) + ': de las ' + CRU.nEmp + ' empresas de la lista 69-B con contratos integrados, ' +
        (CRU.hall.length === 1 ? 'hay <b>1 contrato</b>' : 'hay <b>' + CRU.hall.length + ' contratos</b>') + ' hecho' + (CRU.hall.length === 1 ? '' : 's') + ' después de que el DOF publicó a la empresa. ' +
        (CRU.hall.length === 1 ? 'Es' : 'El primero') + ': <b>' + esc(x.n) + '</b>, ' + esc(x.sit.toLowerCase()) + ' desde el ' + esc(x.dof) + '; contrato de ' + esc(x.inst) + ' del ' + esc(x.f) +
        (x.campo === 'firma' ? '' : ' (fecha de publicación en ComprasMX)') + ', ' + x.dias + ' días después, por ' + pesosCmx(x.imp) + '.</p>' +
        '<p>Es una <b>señal para revisar</b>, no una irregularidad: ' + (x.sit === 'Presunto' ? 'la empresa todavía puede desvirtuar la presunción, ' : '') + 'y estar en la lista no es una condena.</p>';
      ir = [CRU.pag + '#hallazgos', 'las señales del cruce'];
    } else {
      h = '<p>🗂️ Hoy no hay ninguna señal: ningún contrato integrado se hizo con una empresa ya publicada como presunta o definitiva. Queda el <b>antecedente</b> ' + chip({ e: 'derivado' }) + ': ' +
        Object.keys(CRU.ant).length + ' empresas que estuvieron en la lista y tienen contratos, fuera del orden que levanta una señal.</p>';
      ir = [CRU.pag + '#antecedentes', 'los antecedentes del cruce'];
    }
    h += '<p class="pa-chico">' + (CRU.cnet ? '' : 'Por ahora con ComprasMX (2025 y 2026); CompraNet, de años anteriores, está pendiente. ') + 'La ASF va año por año desde la Cuenta Pública ' + CRU.asf.desde + '.</p>';
    return { html: h, ir: ir, rec: [], fu: fu, tit: 'Contratos, lista 69-B y ASF',
      ficha: { t: 'calculo', tit: 'Contratos, lista 69-B y ASF', txt: texto(h), ci: [], fu: fu, ir: ir },
      sug: ['¿Qué contratistas están en la lista negra del SAT?', '¿Qué es la lista 69-B?'] };
  }


  /* Lo que la base no tiene (30-10-2026): la misma pregunta, ya buscada en
     Banxico, el INEGI y los portales oficiales, y al final en las noticias.
     Son enlaces rotulados «sin verificar»: el chat no afirma lo que hay ahí. */
  function fueraHtml(q) {
    var t = String(q).replace(/[¿?¡!«»"]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 120);
    if (!t || !PE.webDato) return '';
    return '<div class="pa-rec pa-web"><p class="pa-mas-t">Búscalo fuera de la plataforma</p>' +
      '<p class="pa-chico">Esto ya no es nuestra base: es tu pregunta, ya buscada primero en las fuentes oficiales de cifras y al final en las noticias. ' +
      '<b>Lo que encuentres ahí no lo verificó Auditavisión.</b> Si das con el documento oficial, cuéntanos y lo integramos con su fuente.</p>' +
      '<div class="pa-rec-lista">' + PE.webDato.map(function (w) {
        var u = w.site ? 'https://www.google.com/search?q=' + encodeURIComponent(t + ' ' + w.site)
          : 'https://news.google.com/search?q=' + encodeURIComponent(t) + '&hl=es-419&gl=MX&ceid=MX:es-419';
        return '<a class="pa-rec-a" href="' + esc(u) + '" target="_blank" rel="noopener noreferrer"><span class="pa-rec-ico" aria-hidden="true">' + w.ico + '</span>' +
          '<span><b>' + esc(w.n) + '</b><small>' + (w.e === 'oficial' ? 'Fuente oficial: sin verificar por nosotros · se abre en otra pestaña ↗' : 'Prensa: sin verificar · se abre en otra pestaña ↗') + '</small></span></a>';
      }).join('') + '</div></div>';
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
  /* Las palabras del dinero («millones», «mucho dinero») no dicen de qué columna se habla: con
     ellas, «¿es cierto que Jalisco debe 50 mil millones?» se iba a la nota de Jalisco y no a
     su deuda (29-10-2026). */
  var GENERICAS = { cierto: 1, verdad: 1, dicen: 1, circula: 1, redes: 1, gobierno: 1, mexico: 1, millones: 1, pesos: 1, dinero: 1, mucho: 1,
    /* Las palabras de tendencia no son el tema (01-11-2026: «el gasto en cultura cayó 40 % en los últimos años» abría la nota de Jalisco). */
    ultimos: 1, anos: 1, meses: 1, cayo: 1, subio: 1, bajo: 1, aumento: 1, crecio: 1, record: 1, historico: 1 };
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
    /* El nombre de una megaobra no cuenta como coincidencia: «¿es cierto que el Tren Maya costó 500 mil
       millones?» se coteja contra la obra, aunque una nota hable del Tren Maya (01-11-2026). */
    var deObra = {};
    (MO.obras.length ? obrasEn(q) : []).forEach(function (o) { o._al.forEach(function (al) { al.split(' ').forEach(function (w) { deObra[w] = 1; }); }); });
    var ws = norm(q).replace(/[^a-z0-9ñ]+/g, ' ').split(' ').filter(function (w) { return w.length > 3 && !vacia[w] && !GENERICAS[w] && !deObra[w]; });
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
      ir: ['noticias-seguimiento.html#seguimientos', 'Tus seguimientos'], sug: ['Noticias relevantes', 'Nuestros pilares'], rec: []
    };
  }

  /* El dictamen y el Registro de pendientes, por su nombre (27-10-2026: las
     preguntas de prueba los mandaban al Ágora y a Crisis ambientales). */
  function propias(q) {
    var p = plano(q);
    if (/ dictamen(es)? (civico|independiente|sellado)| (generar|genero|saco|hago|pido|sirve) (un |el )?dictamen|^ (que es )?(el |un )?dictamen $/.test(p))
      return {
        html: '<p>🧾 El <b>Dictamen cívico independiente</b> respalda una respuesta mía: trae las cifras, de qué documento sale cada una, su estado (oficial, derivado o pendiente), un folio y una huella digital para comprobar que nadie lo alteró.</p>' +
          '<p>Para sacarlo, hazme una pregunta y, en la respuesta, toca <b>«🧾 Generar dictamen»</b>: se abre en otra pestaña, listo para imprimir o compartir. El enlace solo lleva tu pregunta y el modo en que la hiciste, y la página la vuelve a contestar con la misma base, así que nadie puede fabricar uno con cifras ajenas. Sale con la forma de tu modo (la revisión del Inspector, la nota del Periodista, la versión en corto del Ciudadano o la mirada ambiental), que no cambia los datos ni la huella.</p>' +
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
        ir: ['noticias-auditavision.html#al-momento', 'Noticias · Al momento'], rec: [],
        sug: am.slice(0, 2).map(function (x) { return x.tit; }).concat(['¿Cómo sigo un caso?'])
      };
    }
    /* Nepotismo y cargos públicos (28-10-2026): antes que los contratos de
       ComprasMX, que se quedaban con «contrató a su familia». */
    if (charla && charla.nepotismo) { var rnep = charla.nepotismo(q); if (rnep) return rnep; }
    /* Noticias relevantes (28-10-2026): proponer una nota para la Columna del
       Erario y las réplicas y posturas publicadas viven en su pestaña. */
    if (/ (propon\w*|proponer|mandar\w*|enviar\w*|sugerir\w*|pasar\w*|compartir\w*) (les |te )?(una |la |esta |mi )?(nota|noticia|publicacion)/.test(p) && !/ (verific|cierto|falso) /.test(p))
      return {
        html: '<p>✍️ Así llega una noticia a la <b>Columna del Erario</b>: nos mandas la liga, la desarmamos en afirmaciones, cotejamos cada una contra el documento oficial (consta, matiz, sin documento o pendiente) y se publica como nota «Al momento» o como columna, con la fecha, nuestros datos y el glosario. Citamos al medio y a quien firma; no copiamos la nota.</p>' +
          '<p>Para mandarla, toca «Cuéntanos lo que viste» › «Un tema que deberíamos investigar».</p>',
        ir: ['noticias-verifica.html#propon', 'Noticias · Propón una nota'], rec: [], sug: ['Verifica una noticia', 'Noticias de hoy', '¿Cómo sigo un caso?']
      };
    if (/ posturas? /.test(p) && !/ postura (de|del) (gobierno|partido|presidenta|presidente) /.test(p))
      return {
        html: '<p>✉️ En <b>Réplica y postura</b> de Noticias están las respuestas de quienes aludimos. La <b>réplica</b> la pide quien considera inexacto o falso un dato nuestro: se publica gratis, íntegra y sin comentarios en la misma columna. La <b>postura</b> es lo que la institución o la persona aludida dijo en su propio documento, con su liga: se publica en sus palabras y no la calificamos.</p>',
        ir: ['noticias-auditavision.html#replica', 'Noticias · Réplica y postura'], rec: [], sug: ['¿Cómo ejerzo mi derecho de réplica?', 'Noticias de hoy']
      };
    /* Noticias reestructurada (28-10-2026): la agenda del erario, la mesa de
       redacción y el seguimiento de casos tienen su sección. */
    if ((/ (agenda del erario|calendario (fiscal|presupuestal|del presupuesto|del erario)|fechas (del presupuesto|del paquete economico|fiscales)) /.test(p) ||
        / (cuando|que dia|que fecha|en que fecha) (se )?(entrega\w*|presenta\w*|aprueba\w*|llega\w*|manda\w*|envia\w*) (el |la |los )?(paquete economico|presupuesto de egresos|presupuesto|ley de ingresos|cuenta publica|informes? trimestral\w*|precriterios) /.test(p)) &&
        !/ semestral /.test(p)) {
      var AG = (B.dat && B.dat.agenda) || [], hoyA = new Date(); hoyA.setHours(0, 0, 0, 0);
      var MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
      var cuando = function (x, an) {
        if (!x.ult) return new Date(an, x.m - 1, x.d);
        var u = new Date(an, x.m, 0); while (u.getDay() === 0 || u.getDay() === 6) u.setDate(u.getDate() - 1); return u;
      };
      var prox = AG.map(function (x) { var f = cuando(x, hoyA.getFullYear()); if (f < hoyA) f = cuando(x, hoyA.getFullYear() + 1); return { x: x, f: f }; })
        .sort(function (a, b) { return a.f - b.f; }).slice(0, 5);
      if (prox.length) return {
        html: '<p>🗓️ <b>Lo que viene en la agenda del erario</b>, con los plazos que fija la ley:</p><ul class="pa-lista">' + prox.map(function (o) {
          return '<li><b>' + o.f.getDate() + ' de ' + MES[o.f.getMonth()] + (o.x.ult ? ' (último día hábil)' : '') + ':</b> ' + esc(o.x.que) + ' <small>· ' + esc(o.x.quien) + ' · <a href="' + esc(o.x.url) + '" target="_blank" rel="noopener">' + esc(o.x.ley) + ' ↗</a></small></li>';
        }).join('') + '</ul><p class="pa-chico">Son plazos máximos: el documento puede llegar antes. Las fechas que la ley da como «30 días después del trimestre» o «último día hábil» son nuestra cuenta (derivado).</p>',
        ir: ['noticias-seguimiento.html#agenda', 'Noticias · Agenda del erario'], rec: [], sug: ['Noticias de hoy', '¿Qué es la Cuenta Pública?']
      };
    }
    if (/ (mesa de redaccion|titulares (de hoy|del dia|recientes)|que dicen (hoy )?los periodicos|que publican los medios) /.test(p))
      return {
        html: '<p>📡 En la <b>Mesa de redacción</b> de Noticias juntamos titulares sobre finanzas públicas de los buscadores de noticias, por tema (presupuesto, deuda, ASF, impuestos, contratos, Pemex y CFE, salud, estados). Llegan <b>sin verificar</b>: son la materia prima, no la noticia. Cada uno lo puedes mandar al verificador con un toque.</p>',
        ir: ['noticias-verifica.html#mesa', 'Noticias · Mesa de redacción'], rec: [], sug: ['Verifica una noticia', 'Noticias de hoy']
      };
    if (/ (casos? (abiertos?|en seguimiento)|pedir (un )?seguimiento|den(le)? seguimiento|dar(le)? seguimiento|(sigo|seguir|sigan?) (un|este|el) caso|que no se olvide) /.test(p))
      return {
        html: '<p>🔔 En <b>Seguimiento</b> de Noticias están los casos abiertos, cada uno con el documento que falta para cerrarlo (un voto, un informe de la ASF, un contrato, una sentencia). Toca «Seguir este caso» y, cuando llegue el documento, verás el aviso; se guarda solo en tu navegador.</p>' +
          '<p>¿Quieres que sigamos uno nuevo? Ahí mismo, «Pedir un seguimiento»: dinos qué es y qué documento esperas.</p>',
        ir: ['noticias-seguimiento.html#seguir', 'Noticias · Seguimiento'], rec: [], sug: ['Noticias de hoy', 'Proponer una nota']
      };
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
      var fc = F.filter(function (x) { return x.ir && x.ir[0] === 'noticias-auditavision.html#col-ine-oic-auditorias-consejerias'; })[0];
      if (fc && charla) { var rc = charla.deFicha(fc); rc.sug = ['¿El órgano interno de control puede auditar a los consejeros del INE?', '¿Cuánto gasta el INE?']; return rc; }
    }
    /* Pensiones u oxígeno pagados a personas fallecidas en Sonora: la auditoría del
       ISAF al ISSSTESON vive en su columna de Verificamos (28-10-2026); sin esto,
       «Sonora» llevaba a la ficha del estado. */
    if (/ (pension\w*|jubilacion\w*|jubilad\w*|oxigeno) /.test(p) && / (fallecid\w*|muert\w*|difunt\w*|finad\w*|defuncion\w*) /.test(p) && / (sonora|isssteson|isaf) /.test(p)) {
      var fs = F.filter(function (x) { return x.ir && x.ir[0] === 'noticias-auditavision.html#col-isssteson-oxigeno-pensiones-fallecidos'; })[0];
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
      var fp = F.filter(function (x) { return x.ir && x.ir[0] === 'noticias-auditavision.html#col-seguro-popular-51-millones'; })[0];
      if (fp && charla) { var rp = charla.deFicha(fp); rp.sug = ['¿Qué pasó con el Seguro Popular?', '¿Qué sabemos del IMSS-Bienestar?']; return rp; }
    }
    if (/ seguro popular /.test(p) && charla) {
      var rt = charla.contesta(q);
      if (rt && rt.ir && rt.ir[0] === 'datos-salud-sistema.html#sal-transicion') { rt.sug = ['¿Es cierto que con el Seguro Popular se atendieron más de 51 millones?', '¿Cuánta gente se quedó sin acceso a servicios de salud?']; return rt; }
    }
    /* Saldo de la deuda financiera de Pemex: boletines nacionales 86 (30-10-2026, 3T 2026)
       y 69 (31-07-2026, 2T 2026), más el costo financiero en el PEF 2026. */
    if (/ pemex /.test(p) && (/ (debe|adeuda|deuda|endeudamiento|pasivos?) /.test(p)) && !/ (intereses|costo financiero|paga) /.test(p))
      return {
        html: '<p><b>Al cierre del tercer trimestre de 2026 (30 de septiembre de 2026), el saldo de la deuda financiera de Pemex fue de 77.6 mil millones de dólares</b> ' + chip({ e: 'oficial' }) + ' (<a href="https://www.pemex.com/saladeprensa/boletines_nacionales/Paginas/2026_86_nacional.aspx" target="_blank" rel="noopener">Pemex, Boletín nacional 86, 30 de octubre de 2026 ↗</a>).</p>' +
          '<p>Al cierre del segundo trimestre (30 de junio de 2026) se ubicaba en <b>77.5 mil millones de dólares</b>, una disminución de <b>9.1 %</b> respecto al cierre de 2025 ' + chip({ e: 'oficial' }) + ' (<a href="https://www.pemex.com/saladeprensa/boletines_nacionales/Paginas/2026_69_nacional.aspx" target="_blank" rel="noopener">Pemex, Boletín nacional 69, 31 de julio de 2026 ↗</a>). Además, en el Presupuesto de Egresos 2026 Pemex tiene aprobados <b>$190,838.8 millones de pesos</b> para su costo financiero (intereses y comisiones).</p>',
        ir: ['noticias-auditavision.html#col-pemex-3t-2026-perdida-neta', 'Pemex en el 3T 2026'], rec: [], sug: ['¿Cuánto paga Pemex de intereses?', 'Pemex en el 3T 2026: lo que dice la nota y lo que falta del reporte', 'Diagnóstico de Pemex'], anota: 1
      };
    return null;
  }

  /* El título de una columna, tal cual, abre esa columna (29-10-2026): así
     contestan los «¿Sabías esto?» y «Para retomar» del Periodista, que van
     entre las preguntas de ejemplo. */
  function tituloColumna(q) {
    var pq = plano(q).trim();
    if (pq.split(' ').length < 4 || !charla) return null;
    var f = (B.fichas || []).filter(function (x) { return x.t === 'columna' && plano(x.tit).trim() === pq; })[0];
    return f ? charla.deFicha(f) : null;
  }

  /* Una palabra propia de una nota («carnaval», campo temas de integrar_al_momento.py)
     abre esa nota aunque la pregunta nombre también a un municipio o a un estado (01-11-2026). */
  function temaColumna(q) {
    /* Una liga pegada la reconoce la hemeroteca, no las palabras de su dirección. */
    if (/https?:\/\/|www\./i.test(q)) return null;
    var pq = ' ' + plano(q) + ' ';
    var f = (B.fichas || []).filter(function (x) {
      return x.t === 'columna' && (x.tem || []).some(function (w) { return pq.indexOf(' ' + w + ' ') >= 0; });
    })[0];
    return f && charla ? charla.deFicha(f) : null;
  }

  var LEY_NIVEL = /\bley(es)? (de|del|federal|general)\b|\bperiodico oficial\b|\bgaceta oficial\b|\bboletin oficial\b/;
  function leyNivel(q) {
    var p = plano(q);
    if (!charla || !LEY_NIVEL.test(p)) return null;
    var Ls = B.fichas.filter(function (f) { return f.ir && /^marco-legal-tres-niveles\.html/.test(f.ir[0]); });
    var pre = 'Las leyes del dinero de ';
    var st = Ls.filter(function (f) { return f.tit.indexOf(pre) === 0 && p.indexOf(plano(f.tit.slice(pre.length))) >= 0; })
      .sort(function (a, b) { return b.tit.length - a.tit.length; })[0];
    if (st) return charla.deFicha(st);
    var fed = Ls.filter(function (f) {
      var m = /\(([^)]+)\)$/.exec(f.tit);
      return m && (p.indexOf(plano(f.tit.slice(0, m.index))) >= 0 || p.indexOf(plano(m[1])) >= 0);
    })[0];
    return fed ? charla.deFicha(fed) : null;
  }
  /* --- El padrón de contrapartes (18-11-2026; pedido del autor: «compliance de prevención de lavado
     de dinero»). Un RFC lo contesta con todas las listas a la vez (padron.js: las del SAT del art. 69,
     17-H Bis, 69-B y 69-B Bis, el Directorio de Sancionados, la OFAC y la ONU, y ComprasMX); un nombre
     con «OFAC», «ONU» o «lista de sanciones», en esas dos listas. De las personas físicas no dice el
     nombre. «Contratos de RFC…» lo sigue contestando ComprasMX. --- */
  var PD_URL = 'herramienta-inspector-padron.html', PD_CLS = { chico: 'pa-chico', lista: 'pa-lista' };
  var PD_INT = /\b(ofac|onu|naciones unidas|consejo de seguridad|lista clinton|listas? de sanciones|sancionad[oa]s? (por|en) (ee ?uu|estados unidos|la onu|el tesoro)|terroris\w*|lista negra de (ee ?uu|estados unidos))\b/;
  var PD_GEN = /\b(revis\w* (a )?(mi |mis |un |una |el |la |los |las )?(cliente|clientes|proveedor|proveedores|contraparte|contrapartes)|contraparte|contrapartes|padron de contrapartes|conoce a tu cliente|kyc|debida diligencia|prevencion de lavado|\bpld\b|listas? (de|para) (lavado|pld|cumplimiento)|en que listas|no localizad\w*|creditos? fiscal(es)? (firmes?|exigibles?|cancelados?)|sellos? digital(es)? sin efectos|csd sin efectos|69 ?-? ?b bis)\b/;
  var PD_FUERA = ('esta estan es son en la el los las lista listas de del sanciones sancionado sancionada sancionados ofac onu naciones unidas consejo seguridad clinton tesoro ' +
    'ee uu estados unidos negra terrorista terroristas aparece aparecen busca buscar buscame revisa revisar checa checar si que a me puedes dime quiero saber por favor ' +
    'persona empresa nombre').split(' ');
  function cargaPadron() { return cargaJs('assets/auditor/js/padron.js', function () { return window.Padron; }); }
  function padronResp(q) {
    var p = plano(q), rfcs = (q.match(RFC_RE) || []).map(function (x) { return x.toUpperCase(); }).filter(function (x, i, l) { return l.indexOf(x) === i; });
    RFC_RE.lastIndex = 0;
    if (rfcs.length) {
      if (CMX_RE.test(p)) return null;
      var liga = PD_URL + '?q=' + encodeURIComponent(rfcs.slice(0, 100).join(' '));
      return { espera: cargaPadron().then(function (P) { return Promise.all(rfcs.slice(0, 50).map(P.rfc)).then(function (fs) { return respPadron(P, fs, liga, rfcs.length); }); })
        .then(null, function () { return respApp('insppadron', liga, '<p>No pude descargar ahora las listas. Revisa tu conexión y vuelve a preguntarme, o búscalo en la aplicación aquí abajo.</p>'); }),
        tit: 'Revisa a tu contraparte: ' + rfcs.slice(0, 3).join(', ') + (rfcs.length > 3 ? '…' : '') };
    }
    if (PD_INT.test(p) && !/^\s*(que|q) (es|son|significa)\b|que quiere decir/.test(p)) {
      var nom = p.trim().split(' ').filter(function (w) { return w.length > 1 && PD_FUERA.indexOf(w) < 0; }).join(' ');
      if (nom.replace(/ /g, '').length >= 5) {
        var ln = PD_URL + '?q=' + encodeURIComponent(nom);
        return { espera: cargaPadron().then(function (P) { return P.nombre(nom); }).then(function (x) {
          var h = Padron.htmlNombre(x, PD_CLS), M = x.meta;
          var fu = M ? [{ tx: M.ofac.fuente + ', descarga del ' + M.ofac.corte + ' (sha256 ' + M.ofac.sha256.slice(0, 12) + '…)', url: M.ofac.pagina },
            { tx: M.onu.fuente + ', generada el ' + M.onu.corte + ' (sha256 ' + M.onu.sha256.slice(0, 12) + '…)', url: M.onu.pagina }] : [];
          if (charla && charla.deDonde) h += charla.deDonde(fu.map(function (f) { return { que: 'Listas de sanciones', e: 'oficial', fu: f }; }));
          return { html: h, ir: [ln, 'Revisa a tu contraparte'], app: { id: 'insppadron', url: ln }, rec: [],
            ficha: { t: 'calculo', tit: 'OFAC y ONU: ' + nom, txt: texto(h), ci: (x.r || []).slice(0, 8).map(function (z) { return { v: z.y[0].toUpperCase() + ' ' + z.y[1], etq: z.y[3] + ' · ' + z.y[5], e: 'oficial' }; }), fu: fu, ir: [ln, 'Revisa a tu contraparte'] },
            sug: ['¿Cómo reviso a mi cliente?', '¿Qué es una EFOS?', '¿Qué es una actividad vulnerable?'] };
        }, function () { return respApp('insppadron', ln, '<p>No pude descargar ahora las listas de sanciones. Búscalo en la aplicación aquí abajo.</p>'); }), tit: 'OFAC y ONU: ' + nom };
      }
    }
    /* El lote, la cadena de terceros y la matriz (18-11-2026): un archivo con muchos RFC o las facturas en XML. */
    if (APP.insppadron && /\b(lista|lote|archivo|excel|csv|cientos|todos|varios)\b.{0,25}\b(proveedores|clientes|contrapartes|rfc)\b|\b(mis|nuestros) (proveedores|clientes)\b.{0,30}\b(listas?|sat|ofac|69 ?b)\b|a cuenta de terceros|cadena de (terceros|proveedores)|matriz de (riesgo|contrapartes|coincidencias)/.test(p)) {
      return respApp('insppadron', PD_URL + '#lote',
        '<p>📂 Te abro <b>Revisa a tu contraparte</b> en su parte de lotes. Sube un <b>CSV o TXT</b> con hasta 2,000 RFC (o pega la columna desde Excel), o tus <b>facturas en XML</b>: ' +
        'con ellas te digo quién te factura, a quién le facturas y por cuenta de quién (los RFC «a cuenta de terceros» del CFDI 4.0).</p>' +
        '<p>El resultado es una <b>matriz</b>, una fila por RFC y una columna por lista (SAT, 69-B, 69-B Bis, Sancionados, OFAC y ONU), que puedes descargar en CSV. Todo se cruza en tu navegador: tus archivos no se suben a ningún lado.</p>' +
        '<p class="pa-chico">La columna «Revisar» ordena la lista, no califica: una coincidencia es una señal para revisar, nunca una acusación, y de las personas físicas solo se dice si su RFC coincide.</p>');
    }
    if (PD_GEN.test(p) && !/^\s*(que|q) (es|son|significa)\b|que quiere decir/.test(p) && APP.insppadron) {
      return respApp('insppadron', PD_URL,
        '<p>🛡️ Te abro <b>Revisa a tu contraparte</b> aquí abajo. Escribe el <b>RFC</b> de tu cliente, tu proveedor o el cliente de tu cliente (uno o varios) y te digo en una sola ficha si aparece en las listas del SAT ' +
        '(no localizados, créditos firmes, exigibles y cancelados, sentencias por delito fiscal, sellos digitales sin efectos, 69-B y 69-B Bis), en el Directorio de Sancionados, en la OFAC o en la ONU, y si tiene contratos con el gobierno.</p>' +
        '<p>También puedes preguntármelo aquí: «revisa AAA010101AAA». Con un nombre busco en la OFAC y la ONU: «¿está en la OFAC el Cártel de Sinaloa?».</p>' +
        '<p class="pa-chico">De las personas físicas te digo si su RFC coincide, nunca su nombre. Una coincidencia es una señal para revisar, no una acusación. La Lista de Personas Bloqueadas de la UIF no es pública: si tu actividad es vulnerable, consúltala en tu acceso del SAT.</p>');
    }
    return null;
  }
  function respPadron(P, fs, liga, total) {
    var ci = [], fu = [], vistos = {};
    fs.forEach(function (f) {
      (f.senales || []).forEach(function (s) {
        ci.push({ v: s.lista + (s.extra ? ', ' + s.extra : ''), etq: (f.moral && f.nombre ? f.nombre + ' · ' : '') + 'RFC ' + f.rfc + (s.fecha ? ' · publicado ' + s.fecha : ''), e: 'oficial' });
        if (!vistos[s.fuente]) { vistos[s.fuente] = 1; fu.push({ tx: s.fuente, url: s.url }); }
      });
    });
    var M = fs[0].meta;
    if (M && !fu.length) fu.push({ tx: 'SAT, datos abiertos, Contribuyentes publicados (art. 69, 17-H Bis y 69-B Bis); lista 69-B; Directorio de Sancionados; OFAC; ONU', url: M.sat.nl.pagina });
    function grupo(r) { var g = GR.g.filter(function (x) { return (x.emp || []).indexOf(r) >= 0; })[0]; return g ? g.n : ''; }
    var h;
    if (fs.length === 1) h = P.html(fs[0], { grupo: grupo(fs[0].rfc), chico: 'pa-chico', lista: 'pa-lista' });
    else {
      var con = fs.filter(function (f) { return f.senales && f.senales.length; });
      h = '<p>Revisé <b>' + fs.length + ' RFC</b>: <b>' + con.length + '</b> con alguna coincidencia y <b>' + (fs.length - con.length) + '</b> sin coincidencias.' + (total > 50 ? ' Revisé solo los primeros 50; para más, usa la aplicación aquí abajo (acepta hasta 100).' : '') + '</p>' +
        con.sort(function (a, b) { return b.nivel - a.nivel; }).slice(0, 8).map(function (f) { return P.html(f, { grupo: grupo(f.rfc), chico: 'pa-chico', lista: 'pa-lista' }).split('<p class="pa-chico">⚖️')[0]; }).join('') +
        '<p class="pa-chico">⚖️ Una coincidencia es una señal para revisar, no una acusación. No aparecer no certifica a nadie.</p>';
    }
    if (charla && charla.deDonde) h += charla.deDonde(fu.map(function (f) { return { que: 'Listas que revisa el padrón de contrapartes', e: 'oficial', fu: f }; }));
    var tit = 'Revisa a tu contraparte: ' + fs.slice(0, 3).map(function (f) { return f.rfc; }).join(', ');
    var uno = fs.length === 1 && fs[0].moral ? fs[0].rfc : '';
    return { html: h, ir: [liga, 'Revisa a tu contraparte'], app: { id: 'insppadron', url: liga }, rec: [],
      ficha: { t: 'calculo', tit: tit, txt: texto(h), ci: ci.slice(0, 12), fu: fu, ir: [liga, 'Revisa a tu contraparte'] },
      sug: [uno ? 'Contratos de ' + uno + ' en ComprasMX' : '¿Cómo reviso a mi cliente?', '¿Qué es una EFOS?', '¿Qué es una actividad vulnerable?'] };
  }

  /* El índice general cuelga del Auditor (decisión del autor, 19-11-2026): «el índice»,
     «¿qué tiene la plataforma?» o «mapa del sitio» lo abren; «índice de…» sigue siendo un tema. */
  var INDICE_RE = /^(?:(?:el|tu|su|ver|abre|abrir|dame|mu[eé]strame)\s+)*(?:[ií]ndice(?:\s+general)?|mapa del sitio)(?:\s+de\s+(?:la plataforma|auditavisi[oó]n|todo))?\s*\??$|^(?:qu[eé]|todo lo que)\s+(?:tiene|tienen|hay en|ofrece|ofrecen|contiene|sabe)(?:\s+(?:la plataforma|auditavisi[oó]n|el auditor))?\s*\??$/i;
  var MIS_RE = /^(?:(?:ver|abre|abrir|dame|mu[eé]strame)\s+)*(?:mis|tus)\s+(?:respuestas|preguntas|solicitudes|consultas)(?:\s+(?:anteriores|guardadas))?$|^mi\s+(?:caso|historial)$|^(?:qu[eé]\s+)?(?:te\s+)?(?:he\s+)?pregunt[eé](?:\s+antes)?$/i;
  /* Cómo se protege la información y qué se hace si algo falla (19-11-2026, LFPDPPP
     arts. 18 a 20): lleva a esas dos secciones del aviso de privacidad. Pide «mis datos»,
     «la información» o una fuga: «seguridad» sola es un tema (la ENVIPE), no esto. */
  var PROTEGE_RE = /(?:proteg|cuid|resguard)\w*\s+(?:(?:mis|tus|los|la|mi|nuestros?|nuestra)\s+)?(?:datos|informaci[oó]n)|(?:fuga|filtraci[oó]n|vulneraci[oó]n|robo|hackeo)\s+de\s+(?:(?:mis|tus|los)\s+)?(?:datos|informaci[oó]n)|(?:mis|tus)\s+datos\s+(?:est[aá]n|son)\s+segur|seguridad\s+de\s+(?:mis|tus|los)\s+datos/i;
  /* Cuánto tiempo se guarda un papel (19-11-2026): va antes que facturas, nómina y el calendario de Servicios, que comparten palabras. */
  var CONSERVA_RE = /(?:cu[aá]nto tiempo|cu[aá]ntos a[nñ]os|hasta cu[aá]ndo)\s+(?:[\wáéíóúñ]+\s+){0,3}(?:guard|conserv)|calendario de conservaci|plazo de conservaci|conservaci[oó]n de (?:documentos|papeles|archivos|la contabilidad|expedientes)|gobernanza documental|(?:destruir|tirar|depurar)\s+(?:[\wáéíóúñ]+\s+){0,2}(?:papeles|documentos|archivos?|expedientes|facturas)/i;
  /* El autodiagnóstico de cumplimiento (19-11-2026): «¿cumplo con…?», «¿qué me falta para cumplir?». Va antes que el calendario. */
  var CUMPLE_RE = /autodiagn[oó]stico|diagn[oó]stico de cumplimiento|(?:checklist|lista) de cumplimiento|cumplimiento documental|(?:cumplo|cumple|cumplimos|cumples|estoy cumpliendo|estamos cumpliendo)\s+(?:[\wáéíóúñ]+\s+){0,3}(?:papeles|documentos|archivos?|la ley de datos|datos personales|lfpdppp|ley general de archivos|obligaciones documentales)|qu[eé]\s+(?:me|nos)\s+falta\s+para\s+cumplir/i;
  var RIESGO_DOC_RE = /(?:matriz|mapa)(?: de calor)? de riesgos? (?:documental(?:es)?|de (?:mis |nuestros |los )?(?:papeles|documentos|archivos)|de cumplimiento(?: documental)?|de datos personales)|riesgos? documental(?:es)?|por d[oó]nde empiezo a cumplir|qu[eé] (?:atiendo|atendemos|arreglo) primero (?:de|en) (?:mis |nuestros )?(?:papeles|documentos|cumplimiento)/i;
  function respuesta(q, previas) {
    var t = String(q || '').trim().replace(/^[¿¡\s]+/, '').replace(/[?!.\s]+$/, '');
    if (RIESGO_DOC_RE.test(t)) {
      var rrg = abre(q, /servicio|cotiza|h[aá]g[ae]n|armen/i.test(t) ? 'servicio-gobernanza.html' : 'herramienta-inspector-riesgos.html');
      if (rrg) return rrg;
    }
    if (CUMPLE_RE.test(t)) {
      var rcu = abre(q, /servicio|cotiza|h[aá]g[ae]n|revisen/i.test(t) ? 'servicio-gobernanza.html' : 'herramienta-inspector-cumplimiento.html');
      if (rcu) return rcu;
    }
    if (CONSERVA_RE.test(t)) {
      var srvC = /servicio|cotiza|gobernanza|h[aá]g[ae]n|quiero un calendario|para mi empresa/i.test(t), lc = srvC ? 'servicio-gobernanza.html' : 'herramienta-inspector-conservacion.html';
      var rc = abre(q, lc);
      if (rc) return rc;
    }
    if (PROTEGE_RE.test(t)) {
      var fuga = /fuga|filtraci|vulneraci|robo|hackeo/i.test(t), lp = 'aviso-de-privacidad.html#' + (fuga ? 'vulneraciones' : 'seguridad');
      var rp = abre(q, lp) || abre(q, 'aviso-de-privacidad.html');
      if (rp) {
        rp.html = (fuga
          ? '<p><span aria-hidden="true">🔒</span> Si algo falla, hacemos cuatro cosas: <b>cerrar la puerta</b> (llaves y sesiones), <b>medir el daño</b> con la bitácora, ' +
            '<b>avisarte de inmediato</b> si te afecta, como manda la ley (LFPDPPP, art. 19), y <b>corregir y contarlo</b> en una nota pública, sin datos de nadie.</p>' +
            '<p>Si tú encuentras una falla, escríbenos antes de publicarla, para cerrarla primero.</p>'
          : '<p><span aria-hidden="true">🔒</span> Lo más importante: <b>tus facturas, tu nómina y tus listas de RFC no se suben</b>; se leen en tu navegador. ' +
            'Además, cada página trae una política de seguridad que no la deja mandar datos a otro sitio, la conexión va cifrada, la base revisa quién ve cada renglón ' +
            'y la administración entra con dos pasos (LFPDPPP, art. 18).</p>' +
            '<p>Lo que aún falta también está dicho: lo que guarda tu navegador no va cifrado, así que bórralo si compartes la computadora.</p>');
        rp.ir = [lp, fuga ? 'Si algo falla: qué hacemos' : 'Cómo protegemos la información'];
        return rp;
      }
    }
    if (MIS_RE.test(t)) {
      var rm = abre(q, 'mis-respuestas.html');
      if (rm) {
        rm.html = '<p><span aria-hidden="true">📋</span> Todo lo que me preguntas queda en <a href="mis-respuestas.html"><b>Tus respuestas</b></a>: cada respuesta en corto, ' +
          'su «Saber más», su dictamen, lo que no supe contestarte y los servicios que vienen a tu caso, ya listos para pedirlos.</p>' +
          '<p>Se arma solo en tu navegador: nada se manda a ningún servidor.</p>';
        rm.ir = ['mis-respuestas.html', 'Tus respuestas'];
        return rm;
      }
    }
    if (INDICE_RE.test(t)) {
      var ri = abre(q, 'indice.html');
      if (ri) {
        ri.html = '<p><span aria-hidden="true">🗂️</span> Todo lo que sé está en el <a href="indice.html"><b>Índice general</b></a>, en el orden de las pestañas: ' +
          'yo y mis cuatro modos, el Planisferio con el portal de cada entidad, la Enciclopedia, Comunidad, el Noticiero y los Servicios.</p>' +
          '<p>Ábrelo con «Saber más», o escríbeme aquí lo que buscas y te llevo directo.</p>';
        ri.ir = ['indice.html', 'Índice general'];
        return ri;
      }
    }
    return quizaEmpresa(q, respuesta0(q, previas));
  }
  /* Todo pasa por el Auditor (decisión del autor, 19-11-2026: «entre pestañas no se
     vinculan: todo es a través del Auditor»). Una liga de otra pestaña llega al chat
     con ?q= y ?abre=<página>: el chat contesta con esa página (o abre la aplicación en
     su marco), con su dictamen, «Saber más» y el servicio que toca. Solo acepta una
     página de la plataforma; una que el chat no conozca se contesta como pregunta. */
  var ABRE_OK = /^[a-z0-9][a-z0-9-]*\.html([?#][^\s<>"'\\]*)?$/i, abreUna = null;
  function abre(q, liga) {
    if (!liga || !ABRE_OK.test(liga)) return null;
    var base = sinParam(liga), a = appDeLiga(liga), r;
    if (a && APP[a.id]) {
      r = conApp(respApp(a.id, liga, '<p><span aria-hidden="true">' + a.ico + '</span> <b>' + esc(a.n) + '</b>' + (a.grupo ? ', de ' + esc(a.grupo) : '') + '. ' + esc(a.desc || a.frase || '') + '</p>' +
        '<p>Úsala aquí abajo, sin salir del chat, o ábrela completa con «Saber más».</p>', { sug: [] }));
    } else {
      var hit = null, pag = null;
      F.forEach(function (f) {
        if (!f.ir) return;
        if (!hit && f.ir[0] === liga) hit = f;
        if (!pag && f.t === 'pagina' && sinParam(f.ir[0]) === base) pag = f;
      });
      /* Una nota «Al momento» tiene su página propia y su ficha en la columna (#col-<id>). */
      var col = /^noticias-al-momento-(.+)\.html$/.exec(base);
      if (!hit && !pag && col) F.forEach(function (f) { if (!pag && f.ir && /#col-/.test(f.ir[0]) && f.ir[0].split('#col-')[1] === col[1]) pag = f; });
      if (!hit && !pag) F.forEach(function (f) { if (!pag && f.ir && sinParam(f.ir[0]) === base) pag = f; });
      var f = hit || pag;
      if (f && charla) {
        r = charla.deFicha(f);
        r.ir = [liga, (hit && r.ir && r.ir[1]) || f.tit];
      } else {
        /* Una página sin ficha propia (un mapa, un tablero): el chat la abre igual, sin cifras. */
        r = { html: '<p><span aria-hidden="true">📄</span> Te llevo a <b>' + esc(q) + '</b>. Ábrela con «Saber más»; si tienes una pregunta sobre lo que ves ahí, escríbemela aquí.</p>',
          ir: [liga, q], rec: [], sug: [] };
      }
    }
    r.abre = liga;
    return r;
  }
  /* La revisión ya está hecha (pedido del autor, 22-11-2026: «en la búsqueda que haga el usuario,
     ya sea mediante un RFC… una empresa, nosotros en el mismo dictamen le resolvemos todo lo que tiene
     nuestra base de datos… ya ni siquiera tiene que cotizar»). Lo que un servicio revisa con la base
     ya está en la respuesta y en su dictamen; el encargo queda solo para lo que la base no hace sola
     (seguirlo cada semana, una cartera entera, documentos que no son públicos), con un toque y la
     solicitud ya llena. Nunca un monto. */
  var SRV = (B.dat && B.dat.srv) || {};
  var SRVS = (B.dat && B.dat.srvs) || {};
  function srvDe(r) {
    if (!r || r.plat) return [];
    var u = (r.app && r.app.url) || (r.ir && r.ir[0]) || (r.ficha && r.ficha.ir && r.ficha.ir[0]) || '';
    var b = sinParam(u), m = /^servicio-([a-z-]+)\.html$/.exec(b);
    if (m && SRVS[m[1]]) return [[m[1]].concat(SRVS[m[1]])];
    if (!b || /^servicios?(-|\.html)/.test(b)) return [];
    return SRV[b] || [];
  }
  /* La solicitud ya llena: el servicio, el tema (lo que se buscó) y la pregunta. */
  function pideLiga(sid, q, tema) {
    return 'servicios-cotiza.html?servicio=' + encodeURIComponent(sid) + '&tema=' + encodeURIComponent(String(tema || q).slice(0, 160)) +
      '&pregunta=' + encodeURIComponent(String(q).slice(0, 600)) + '#solicitud';
  }
  function resueltoHtml(l, q, tema, dic) {
    if (!l.length) return '';
    /* Ronda 1 (22-11-2026): cada servicio lleva a su Inspector (servicios-revisa.html?s=), con la misma pregunta. */
    var nom = l.map(function (x) { return '<span aria-hidden="true">' + x[1] + '</span> <a href="servicios-revisa.html?s=' + encodeURIComponent(x[0]) +
      '&amp;q=' + encodeURIComponent(String(q || '').slice(0, 600)) + '"><b>' + esc(x[2]) + '</b></a>'; }).join(dic ? '; ' : ' · ');
    var pide = 'Si quieres que lo sigamos por ti (cada semana, con tu cartera completa o con documentos que no son públicos), ' +
      '<a href="' + esc(pideLiga(l[0][0], q, tema)) + '">pídelo con un toque ➔</a>: tu solicitud ya va llena; solo confirmas. El costo y el plazo te llegan por escrito antes de empezar.';
    if (dic) return '<p>Lo que revisa ' + (l.length === 1 ? 'el servicio' : 'cada servicio') + ' con la base de la plataforma (' + nom + ') ya está en este dictamen.</p>' +
      '<p class="dic-chico">' + pide + ' Este capítulo no forma parte de la huella.</p>';
    return '<div class="pa-srv pa-hecho"><p class="pa-srv-t"><span aria-hidden="true">✅</span> Ya revisamos esto por ti</p>' +
      '<p>Lo que hace ' + (l.length === 1 ? 'el servicio' : 'cada servicio') + ' con nuestra base ya está aquí, gratis: ' + nom + '.</p>' +
      '<p class="pa-chico">' + pide + '</p></div>';
  }
  function servicioHtml(r, q) { return resueltoHtml(srvDe(r), q || r.q, r.integ && r.integ.tema); }
  function svDicHtml(q, r) { return resueltoHtml(srvDe(r), q, r.integ && r.integ.tema, true); }

  /* La revisión completa de una empresa: con un RFC de persona moral, una empresa de ComprasMX o un
     grupo, la respuesta junta todo lo que la base tiene de ella (las listas del SAT, la 69-B, Sancionados,
     la OFAC y la ONU; sus contratos públicos; su grupo) aunque la pregunta haya pedido solo una parte.
     No agrega cifras propias: cada capítulo es la misma respuesta que da el chat, con sus fuentes. */
  var RFC12 = /\b[A-ZÑ&]{3}\d{6}[A-Z0-9]{3}\b/g;
  function integral(q, r) {
    if (!r || r.sin || r.plat || !r.ficha) return Promise.resolve(null);
    var tit = r.ficha.tit || '', ya = { padron: /^Revisa a tu contraparte/.test(tit), cmx: /contratos-publicos\.html/.test((r.ir || [])[0] || ''), grupo: /^Grupo empresarial/.test(tit) };
    var rfcs = [];
    function suma(x) { x = String(x).toUpperCase(); if (x.length === 12 && rfcs.indexOf(x) < 0) rfcs.push(x); }
    (String(q).match(RFC_RE) || []).forEach(suma); RFC_RE.lastIndex = 0;
    (r.ficha.ci || []).forEach(function (c) { (String(c.etq || '').match(RFC12) || []).forEach(suma); });
    if (ya.grupo) { var gg = GR.g.filter(function (g) { return 'Grupo empresarial: ' + g.n === tit; })[0]; if (gg) gg.emp.forEach(suma); }
    rfcs = rfcs.slice(0, 3);
    if (!rfcs.length) return Promise.resolve(null);
    var ci = [], fu = [], caps = [];
    function fuente(x) { if (x && !fu.some(function (y) { return y.tx === x.tx; })) fu.push(x); }
    var tareas = rfcs.map(function (rfc) {
      var t = [];
      if (!ya.padron) t.push(cargaPadron().then(function (P) { return P.rfc(rfc).then(function (f) {
        f.senales.forEach(function (sx) { ci.push({ v: sx.lista + (sx.extra ? ', ' + sx.extra : ''), etq: (f.nombre ? f.nombre + ' · ' : '') + 'RFC ' + rfc, e: 'oficial' }); fuente({ tx: sx.fuente, url: sx.url }); });
        if (!f.senales.length && f.meta) fuente({ tx: 'SAT, datos abiertos, Contribuyentes publicados (art. 69, 17-H Bis y 69-B Bis); lista 69-B; Directorio de Sancionados; OFAC; ONU', url: f.meta.sat.nl.pagina });
        return ['🛡️', 'Listas del SAT, sancionados y sanciones internacionales', P.html(f, { chico: 'pa-chico', lista: 'pa-lista' }), rfc,
          f.senales.length ? f.senales.length + (f.senales.length === 1 ? ' coincidencia por revisar' : ' coincidencias por revisar') : 'Sin coincidencias', !!f.senales.length];
      }); }).then(null, function () { return null; }));
      if (!ya.cmx && !ya.grupo) t.push(Promise.all([cmxIdx(), cmxProv(rfc), cmxSanc()]).then(function (X) {
        var rp = respProv(rfc, X[1], X[0].meta, X[2]);
        if (rp.ficha) { (rp.ficha.ci || []).forEach(function (c) { ci.push(c); }); (rp.ficha.fu || []).forEach(fuente); }
        return ['🏛️', 'Contratos con el gobierno (ComprasMX)', rp.html.replace(/<details class="pa-dedonde"[\s\S]*?<\/details>/g, ''), rfc,
          rp.ficha ? 'Tiene contratos publicados' : 'Sin contratos en ComprasMX', false];
      }).then(null, function () { return null; }));
      var g = !ya.grupo && GR.g.filter(function (x) { return (x.emp || []).indexOf(rfc) >= 0; })[0];
      if (g) t.push(Promise.resolve(['🏢', 'Su grupo empresarial', '<p>Es una de las empresas con que <b>' + esc(g.n) + '</b> aparece en ComprasMX. ' +
        '<button type="button" class="pa-ej" data-pa-pregunta="' + esc(g.n) + '">Ver todo el grupo</button></p>', rfc, g.n, false]));
      return Promise.all(t);
    });
    return Promise.all(tareas).then(function (L) {
      L.forEach(function (l) { l.forEach(function (c) { if (c) caps.push(c); }); });
      if (!caps.length) return null;
      var nombres = caps.length && rfcs.length === 1 ? rfcs[0] : rfcs.join(', ');
      var html = caps.map(function (c) {
        return '<section class="pa-int-cap"><h4><span aria-hidden="true">' + c[0] + '</span> ' + esc(c[1]) + (rfcs.length > 1 ? ' · <code>' + esc(c[3]) + '</code>' : '') + '</h4>' + c[2] + '</section>';
      }).join('');
      return { html: html, ci: ci, fu: fu, tema: 'Revisión completa de ' + nombres, rfcs: rfcs, caps: caps, ya: ya };
    });
  }
  function vistazoHtml(r, genera) {
    var caps = (r.integ && r.integ.caps) || [], varios = r.integ && r.integ.rfcs.length > 1;
    return '<section class="pa-vistazo"><h3><span aria-hidden="true">👁️</span> De un vistazo</h3>' + corto(r.html) +
      (caps.length ? '<ul class="pa-vistazo-caps">' + caps.map(function (c) {
        return '<li' + (c[5] ? ' class="pa-vistazo-ojo"' : '') + '><span aria-hidden="true">' + c[0] + '</span><b>' + esc(c[1]) + '</b>' +
          (varios ? ' <code>' + esc(c[3]) + '</code>' : '') + '<span>' + esc(c[4] || '') + '</span></li>';
      }).join('') + '</ul>' : '') + (genera ? '<p class="pa-acc">' + genera + '</p>' : '') + '</section>';
  }
  function integralHtml(x) {
    return x ? '<section class="pa-pag-sec pa-int"><h3><span aria-hidden="true">🔎</span> La revisión completa: todo lo que la base sabe de ' +
      esc(x.rfcs.join(', ')) + '</h3><p class="pa-chico">Lo juntamos solo, con la misma base: no tienes que preguntarlo por partes ni pedirlo como servicio.</p>' + x.html + '</section>' : '';
  }
  function respuesta0(q, previas) {
    /* Una liga que ya está en la hemeroteca abre su cotejo antes que cualquier palabra de su dirección
       («pemex-perdidas-…-deuda» se iba al pendiente de la deuda de Pemex, 01-11-2026). */
    var lg = (/https?:\/\/[^\s<>"']+/i.exec(String(q)) || [])[0], hm = lg && hemeroteca(lg);
    /* Una nota pegada (texto, con o sin liga) se lee entera: lo que afirma, si ya la cotejamos, la promesa que toca,
       sus puntos ciegos y lo que sigue (pedido del autor, 07-11-2026). La columna que ya la coteja va dentro. */
    if (charla && charla.esNota && charla.esNota(q)) {
      var tx0 = charla.sinLiga(q);
      return charla.lectura(q, hm || tituloColumna(tx0) || temaColumna(tx0));
    }
    if (hm) return hm;
    var ge = grupoEmp(q);
    if (ge) return ge;
    var xi = expInvResp(q);
    if (xi) return xi;
    /* La memoria de promesas (01-11-2026): «¿qué pasó con lo que prometieron…?» antes que la nota o la obra del mismo tema. */
    var pm = charla && charla.promesa && charla.promesa(q);
    if (pm) return pm;
    /* Las leyes del dinero en los tres niveles (03-11-2026): «ley de ingresos de Jalisco» pide sus leyes, no su estado de cuenta. */
    var ln = leyNivel(q);
    if (ln) return ln;
    var mp = charla && charla.mapa && charla.mapa(q);
    if (mp) return mp;
    /* El IMSS y el ISSSTE de un estado (03-11-2026): «¿qué estado tiene menos camas del IMSS?» no es la columna del IMSS. */
    var sae = charla && charla.saludEstado && charla.saludEstado(q);
    if (sae) return sae;
    var sso = charla && charla.social && charla.social(q); if (sso) return sso;
    var svi = charla && charla.vivienda && charla.vivienda(q); if (svi) return svi;
    var sap = charla && charla.administracion && charla.administracion(q); if (sap) return sap;
    var tc = tituloColumna(q);
    if (tc) return tc;
    var tm = temaColumna(q);
    if (tm) return tm;
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
    var dr = deudaRpu(q);
    if (dr) return dr;
    var pd = padronResp(q);
    if (pd) return pd;
    var cx = fraccCmx(q) || cruceAsf(q) || cruceSat(q) || sancionesCmx(q) || contratosCmx(q) || empresaNombre(q, previas);
    if (cx) return cx;
    var pe = personaje(q);
    if (pe) return pe;
    var prd = conApp(predialResp(q));
    if (prd) return prd;
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

  /* El esquema de la respuesta (pedido del autor, 16-11-2026: «que el formato de
     las respuestas… se potencialice… mejor esquematizada»). La respuesta se lee
     por pisos: de qué está hecha (su tipo y sus chips), lo esencial, el detalle
     plegado cuando es largo, sus acciones, su expediente si lo tiene, y las
     puertas en paneles que se abren. Nada de esto cambia un dato: solo ordena. */
  function cabResp(r) {
    var f = r.ficha, t = f && TIPO[f.t], est = {};
    (r.html.match(/est-chip est-(oficial|derivado|pendiente)/g) || []).forEach(function (m) { est[m.slice(13)] = 1; });
    var chs = ['oficial', 'derivado', 'pendiente'].filter(function (e) { return est[e]; });
    var mt = (r.q && modoToca(r.q, r)) || modoVivo();
    if (!t && !chs.length) return '';
    return '<p class="pa-cab">' + (t ? '<span class="pa-cab-tipo"><span aria-hidden="true">' + t[0] + '</span> ' + esc(t[1]) + '</span>' : '') +
      (MODO_ICO[mt] ? '<span class="pa-cab-modo" title="El modo al que pertenece esta respuesta">' + MODO_ICO[mt] + ' ' + MODO_NOM[mt] + '</span>' : '') +
      (chs.length ? '<span class="pa-cab-est"><span class="pa-cab-de">Hecha con datos</span> ' + chs.map(function (e) { return chip({ e: e }); }).join(' ') + '</span>' : '') + '</p>';
  }
  function esquema(html) {
    var d = document.createElement('div');
    d.innerHTML = html;
    var suelto = Array.prototype.some.call(d.childNodes, function (n) { return n.nodeType === 3 && n.textContent.trim(); });
    if (suelto || d.querySelector('iframe, form, input, textarea, .pa-app')) return html;
    var pie = [], cuerpo = [];
    Array.prototype.forEach.call(d.children, function (k) { (k.classList.contains('pa-dedonde') ? pie : cuerpo).push(k); });
    var largo = cuerpo.reduce(function (s, k) { return s + k.textContent.length; }, 0);
    if (cuerpo.length < 4 || largo < 900) return html;
    var ver = [], ac = 0;
    while (cuerpo.length > 2 && ver.length < 3 && (!ver.length || ac < 280)) { ac += cuerpo[0].textContent.length; ver.push(cuerpo.shift()); }
    if (cuerpo.length < 2) return html;
    var fuera = function (l) { return l.map(function (k) { return k.outerHTML; }).join(''); };
    return fuera(ver) + '<details class="pa-detalle"><summary><span>📋 Ver el detalle completo</span><small>' + cuerpo.length + ' apartados más</small></summary>' +
      '<div class="pa-detalle-c">' + fuera(cuerpo) + '</div></details>' + fuera(pie);
  }
  /* Las puertas de una respuesta van en paneles: se ve cuántas hay y se abren
     con un toque. Con pocas, el panel ya viene abierto. */
  function panel(h, ico, tit, abre) {
    if (!h) return '';
    var n = (h.match(/class="pa-rec-a"|class="pa-pl-a"|class="pa-pl-chip"/g) || []).length;
    return '<details class="pa-panel"' + (abre || (n && n <= 3) ? ' open' : '') + '><summary><span>' + ico + ' ' + tit + '</span>' + (n ? '<small>' + n + '</small>' : '') + '</summary>' +
      h.replace(/<p class="pa-mas-t">[^<]*<\/p>/, '') + '</details>';
  }
  /* El expediente de la investigación (16-11-2026): cuando la plática toca una de
     las grandes investigaciones, la respuesta trae la tarjeta de su expediente,
     que arma herramientas/expedientes_inv.py con la base. */
  var EXP_INDICE = 'expedientes-investigacion.html';
  function invToca(q, r) {
    var p = plano(q + ' ' + ((r && r.ficha && r.ficha.tit) || (r && r.tit) || '')), hit = null;
    INV.forEach(function (f) { if (!hit && f.ex && f._k.some(function (x) { return p.indexOf(x) >= 0; })) hit = f; });
    return hit;
  }
  function expInvHtml(q, r) {
    if (r.plat) return '';
    var f = r.ficha && r.ficha.t === 'investigacion' && r.ficha.ex ? r.ficha : invToca(q, r);
    if (!f) return '';
    var det = [f.nd + ' documento' + (f.nd === 1 ? '' : 's')];
    if (f.nb) det.push(f.nb + ' en su bitácora');
    if (f.np) det.push(f.np + ' pendiente' + (f.np === 1 ? '' : 's'));
    if (f.nov) det.push('último registro: ' + f.nov);
    return '<a class="pa-exp" href="' + esc(f.ex) + '"><span class="pa-exp-ico" aria-hidden="true">🗂️</span>' +
      '<span class="pa-exp-tx"><small>' + esc(f.exn) + ' · Expediente de investigación · ' + (f.ab ? '🟠 Abierto' : '🟢 Documentado') + '</small>' +
      '<b>' + esc(f.tit) + '</b><small>' + esc(det.join(' · ')) + '</small></span><span class="pa-exp-ir">Abrir ➔</span></a>';
  }
  function pideExpHtml() {
    return '<p class="pa-chico pa-exp-pide">🗂️ ¿Es un caso grande? Revisa los <a href="' + EXP_INDICE + '">expedientes de investigación</a> o ' +
      '<a href="servicios-cotiza.html?servicio=expediente">pide el tuyo</a>.</p>';
  }
  /* «Expediente del Tren Maya», «expedientes de investigación»: abre el de la
     Biblioteca. Los casos de la ASF («expediente de Segalmex», «casos por aclarar
     del AIFA») siguen en su aplicación. */
  function expInvResp(q) {
    var p = plano(q);
    if (!charla || !/ expedientes? /.test(p) || / (asf|casos?|pliegos?|por aclarar) /.test(p)) return null;
    /* «¿Qué me entregan si contrato el expediente…?» pide el servicio, no la Biblioteca (servicio-expediente.html). */
    if (/ (contrat\w*|encarg\w*|cotiz\w*|servicios?|me entregan) /.test(p)) return null;
    var f = invToca(q, null);
    if (f) {
      var r = charla.deFicha(f);
      r.ir = [f.ex, 'su expediente'];
      r.html = '<p>🗂️ Es el <b>expediente ' + esc(f.exn) + '</b> de la Biblioteca del Erario Público: todo lo que la plataforma sabe del caso, en un solo lugar, ' +
        (f.ab ? 'y <b>sigue abierto</b>' : 'ya <b>documentado</b>') + (f.nov ? '. El último registro de su bitácora es del ' + esc(f.nov) : '') + '.</p>' + r.html.replace(/<p>Es una de las investigaciones[\s\S]*?<\/p>/, '');
      r.sug = ['Expedientes de investigación', '¿Cómo pido un expediente?'];
      return r;
    }
    if (!/ expedientes? de (las )?(grandes )?investigacion(es)? | grandes investigaciones | expedientes? de la biblioteca | expedientes? internos? | expedientes? de control interno /.test(p)) return null;
    var ab = INV.filter(function (x) { return x.ex && x.ab; }).length, tot = INV.filter(function (x) { return x.ex; }).length;
    var nuevos = INV.filter(function (x) { return x.ex && x.nov; }).slice(0, 5);
    return { tit: 'Expedientes de control interno', ir: [EXP_INDICE, 'los Expedientes de control interno'], rec: [],
      html: '<p>🗂️ Los <b>Expedientes de control interno</b> son la quinta tarjeta de la Biblioteca del Erario Público: cada gran investigación en un solo lugar, con el caso en cinco preguntas, su bitácora, lo que sigue y lo que falta.</p>' +
        '<p>Hay <b>' + tot + '</b>: <b>' + ab + '</b> abiertos y <b>' + (tot - ab) + '</b> documentados. Se arman solos con la base de datos y se ponen al día cada día.</p>' +
        (nuevos.length ? '<p>Con registro fechado en su bitácora:</p><ul class="pa-lista">' + nuevos.map(function (x) {
          return '<li><a href="' + esc(x.ex) + '">' + esc(x.exn) + ' · ' + esc(x.tit) + '</a> · ' + esc(x.nov) + '</li>'; }).join('') + '</ul>' : '') +
        '<p>Dime «expediente del Tren Maya» y te abro el suyo. Si tu caso no está, <a href="servicios-cotiza.html?servicio=expediente">puedes pedirlo</a>.</p>',
      sug: INV.filter(function (x) { return x.ex; }).slice(0, 3).map(function (x) { return 'Expediente de ' + x.tit; }) };
  }
  /* «Tus respuestas» (pedido del autor, 19-11-2026: «la página automatizada de las respuestas
     o de los servicios a… lo que hayan hecho los usuarios»). Cada pregunta contestada se anota
     solo en este navegador (av-caso, hasta 60) con su respuesta en corto, su página, su dictamen
     y los servicios que aprovechan esa página (SRV); mis-respuestas.html la arma. Lo que no supo
     contestar queda como solicitud. Nada sale de aquí. */
  function caso(q, r, previas, sin) {
    try {
      var ir = sin ? null : (r.ir || (r.ficha && r.ficha.ir) || null), u = sin ? '' : ((r.app && r.app.url) || (ir && ir[0]) || '');
      var b = sinParam(u), l = (!b || /^servicios?(-|\.html)/.test(b)) ? [] : (SRV[b] || []);
      var d = document.createElement('div'); d.innerHTML = sin ? '' : (r.html || '');
      var t = (d.textContent || '').replace(/\s+/g, ' ').trim();
      if (t.length > 320) t = t.slice(0, 317) + '…';
      var c = JSON.parse(localStorage.getItem('av-caso') || '[]');
      if (!Array.isArray(c)) c = [];
      c = c.filter(function (x) { return x && x.q !== q; });
      c.unshift({ q: q, f: hoy(), m: modoActual(), t: t, ir: ir ? [ir[0], ir[1] || ''] : null, s: l.map(function (x) { return x[0]; }),
        d: !sin && r.ficha ? enlaceDictamen(q, previas || []) + (r.abre ? '&abre=' + encodeURIComponent(r.abre) : '') : '', sin: !!sin });
      localStorage.setItem('av-caso', JSON.stringify(c.slice(0, 60)));
    } catch (e) { /* sin almacenamiento, el chat sirve igual */ }
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
    var r = (abreUna && abre(q, abreUna)) || respuesta(q, previas);
    abreUna = null;
    /* La lista negra del SAT contesta cuando termina de descargar la lista. */
    var espera = r.espera ? r.espera.then(function (x) { r = x; }) : null;
    var pinta = function (li) {
      /* La medición de uso (18-11-2026): solo el modo y la página a la que llevó la respuesta; la pregunta no sale. */
      if (!ya && window.AvUso) window.AvUso.marca('pregunta', { modo: modoActual(), destino: r.sin ? 'sin respuesta' : String((r.ir && r.ir[0]) || (r.ficha && r.ficha.ir && r.ficha.ir[0]) || '').split(/[?#]/)[0].slice(0, 160) });
      if (r.sin) {
        li.querySelector('.pa-burbuja').innerHTML = sinRespuesta(q, r.sin) + pideExpHtml() + iaHtml(q) + (r.web ? webHtml(r.web) : fueraHtml(q));
        if (!ya) { anota(q, 'sin'); caso(q, r, previas, true); }
        return;
      }
      if (r.anota && !ya) anota(q, 'sin');
      r.q = q;
      if (SOLO) {
        li.querySelector('.pa-burbuja').innerHTML = cabResp(r) + remiteHtml(q, r) + '<div class="pa-resp pa-corto">' + corto(r.html) + '</div>' + accionesSv(q, r, previas) +
          (r.sug && r.sug.length ? '<p class="pa-mas-t">Sigue preguntando</p>' + chips(r.sug.slice(0, 4)) : '');
        if (!ya) caso(q, r, previas);
        guarda();
        return;
      }
      li.querySelector('.pa-burbuja').innerHTML = cabResp(r) + remiteHtml(q, r) + '<div class="pa-resp">' + esquema(r.html) + '</div>' + acciones(q, r, previas) +
        servicioHtml(r, q) + expInvHtml(q, r) +
        periodistaHtml(q, r) + capaModoHtml(q, r) +
        appDe(r) +
        panel(r.plat ? '' : recursosHtml(conInv(q, r, r.rec || recursosPara(q, r))), '🧭', 'Explóralo a fondo') +
        panel(enciclopediaHtml(enciclopediaPara(q, r)), '📚', 'En la Enciclopedia') +
        (r.web ? webHtml(r.web) : '') +
        (r.sug && r.sug.length ? '<p class="pa-mas-t">' + (r.tambien ? 'También te puede servir' : 'Sigue preguntando') + '</p>' + chips(r.sug) : '');
      var caja = li.querySelector('.pa-app[data-pa-abre]');
      if (caja) montaApp(caja);
      if (!ya) caso(q, r, previas);
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
  /* La respuesta en corto del Inspector de Servicios: lo primero que dice, sin
     tablas, marcos ni listas largas; lo demás vive en su página completa. */
  function corto(h) {
    var d = document.createElement('div');
    d.innerHTML = h;
    var out = [], n = 0;
    Array.prototype.some.call(d.children, function (k) {
      if (k.classList.contains('pa-dedonde') || k.querySelector('iframe, form, table, .pa-app') || /^(TABLE|FORM|IFRAME|DETAILS)$/.test(k.tagName)) return false;
      if (/^(UL|OL)$/.test(k.tagName)) {
        var c = k.cloneNode(false);
        Array.prototype.slice.call(k.children, 0, 3).forEach(function (x) { c.appendChild(x.cloneNode(true)); });
        out.push(c.outerHTML); n += c.textContent.length;
      } else { out.push(k.outerHTML); n += k.textContent.length; }
      return out.length >= 2 || n > 260;
    });
    if (!out.length) { var t = d.textContent.replace(/\s+/g, ' ').trim(); out.push('<p>' + esc(t.length > 260 ? t.slice(0, 258).replace(/\s+\S*$/, '') + '…' : t) + '</p>'); }
    return out.join('');
  }
  function enlaceResp(q, previas, abreL) {
    return SV_RESP + '?q=' + encodeURIComponent(q) + (previas || []).map(function (c) { return '&c=' + encodeURIComponent(c); }).join('') +
      (abreL ? '&abre=' + encodeURIComponent(abreL) : '');
  }
  function accionesSv(q, r, previas) {
    return '<p class="pa-acc">' +
      '<a class="pa-boton pa-ver" href="' + esc(enlaceResp(q, previas, r.abre)) + '">📄 Ver la respuesta completa ➔</a>' +
      (r.ficha ? '<a class="pa-boton pa-genera" href="' + esc(enlaceDictamen(q, previas || []) + (r.abre ? '&abre=' + encodeURIComponent(r.abre) : '')) + '" target="_blank" rel="noopener">🧾 Generar dictamen</a>' : '') +
      '<button type="button" class="pa-boton pa-noera" data-pa-q="' + esc(q) + '" data-pa-tit="' + esc(r.ficha ? r.ficha.tit : '') + '">🤔 No era lo que buscaba</button></p>';
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
  /* El dictamen que toca una investigación queda anotado en su expediente de
     control interno, solo en este navegador (av-dics): la pregunta, el folio y
     el enlace que lo vuelve a armar. Nada se manda a un servidor. */
  function guardaDic(q, r, f, fol) {
    var xf = f.t === 'investigacion' && f.ex ? f : invToca(q, r);
    if (!xf || !xf.ex) return;
    try {
      var l = JSON.parse(localStorage.getItem('av-dics') || '[]');
      if (!Array.isArray(l)) l = [];
      l = l.filter(function (x) { return x && !(x.ex === xf.ex && x.q === q); });
      l.unshift({ ex: xf.ex, q: q, fo: fol || '', f: hoy(), m: MODO_DIC || '', u: location.search.slice(0, 3000) });
      localStorage.setItem('av-dics', JSON.stringify(l.slice(0, 60)));
    } catch (e) { /* sin almacenamiento, el dictamen sirve igual */ }
  }

  function armaDictamen() {
    var ps = new URLSearchParams(location.search), q = (ps.get('q') || '').trim().slice(0, 600);
    var antes = ps.getAll('c').map(function (x) { return x.trim().slice(0, 600); }).filter(Boolean).slice(-4);
    var doc = document.getElementById('dicDoc'), chat = 'herramienta-inspector-pregunta.html';
    var pm = ps.get('modo') === 'reportero' ? 'periodista' : ps.get('modo');
    if (MODO_ICO[pm]) MODO_DIC = pm;
    if (pm === 'inspector') {
      chat = SV_CHAT;
      var vu = document.querySelector('#dicApp .dic-acc a');
      if (vu) { vu.setAttribute('href', SV_CHAT); vu.textContent = '← Volver al Inspector'; }
    }
    if (!q) {
      doc.innerHTML = '<p>El dictamen respalda una respuesta del Auditor. <a href="' + chat + '">Hazle una pregunta</a> y, en su respuesta, toca <b>«🧾 Generar dictamen»</b>.</p>';
      return;
    }
    antes.forEach(function (x) { respuesta(x); });
    var r = abre(q, ps.get('abre')) || respuesta(q, antes);
    if (r && r.espera) r.espera.then(arma0); else arma0(r);
    function arma0(r) { integral(q, r).then(function (x) { if (x) r.integ = x; arma(r); }, function () { arma(r); }); }
    function arma(r) {
    var f = r && !r.sin ? r.ficha : null;
    /* La revisión completa entra al dictamen con sus cifras y sus fuentes, y por eso a su huella. */
    if (f && r.integ) f = Object.assign({}, f, { ci: (f.ci || []).concat(r.integ.ci), fu: (f.fu || []).concat(r.integ.fu.filter(function (x) { return !(f.fu || []).some(function (y) { return y.tx === x.tx; }); })) });
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
      var hc = doc.querySelector('.dic-huella-c code');
      if (hc) { hc.textContent = hx ? hx.slice(0, 16) + '…' : 'no disponible'; if (hx) hc.title = hx; }
      Array.prototype.forEach.call(doc.querySelectorAll('.dic-sello'), function (el) { el.innerHTML = sello(fol, 'DICTAMEN'); });
      guardaDic(q, r, f, fol);
    });
    var im = document.getElementById('dicImprime'), en = document.getElementById('dicEnlace');
    im.hidden = en.hidden = false;
    /* Un solo cierre discreto (Ronda 1): con la revisión de una empresa, lo que la base no hace sola
       (el aviso cada semana o la cartera completa) se pide en el Inspector de su servicio. Nunca un monto. */
    var acc = document.querySelector('#dicApp .dic-acc');
    if (acc && r.integ && !acc.querySelector('.dic-puente')) {
      acc.insertAdjacentHTML('beforeend', '<a class="dic-puente" href="servicios-revisa.html?s=seguimiento&amp;q=' + encodeURIComponent(r.integ.rfcs[0]) +
        '">📡 ¿Seguimiento cada semana o tu cartera completa? ➔</a>');
    }
    im.addEventListener('click', function () { window.print(); });
    /* Al imprimir o guardar en PDF, el desglose va completo: se abren los acordeones y luego vuelven como estaban. */
    var cerrados = [];
    window.addEventListener('beforeprint', function () {
      cerrados = Array.prototype.filter.call(doc.querySelectorAll('details:not([open])'), function (d) { d.open = true; return true; });
    });
    window.addEventListener('afterprint', function () { cerrados.forEach(function (d) { d.open = false; }); cerrados = []; });
    en.addEventListener('click', function () {
      (navigator.clipboard ? navigator.clipboard.writeText(location.href) : Promise.reject()).then(function () {
        en.textContent = '✅ Enlace copiado';
      }, function () { en.textContent = 'Copia la dirección de tu navegador'; });
    });
    }
  }
  /* La respuesta completa del Inspector de Servicios: todo lo que la respuesta trae
     (las cifras, sus documentos, el expediente, el Planisferio y las demás partes
     de la plataforma, el servicio que toca) y, al final, «Generar dictamen». */
  function armaRespuesta() {
    var ps = new URLSearchParams(location.search), q = (ps.get('q') || '').trim().slice(0, 600);
    var antes = ps.getAll('c').map(function (x) { return x.trim().slice(0, 600); }).filter(Boolean).slice(-4);
    var doc = document.getElementById('respDoc'), vista = ps.get('vista') === '1';
    if (vista) document.documentElement.classList.add('pa-en-vista');
    MODO_DIC = 'inspector';
    if (!q) { doc.innerHTML = '<p>Esta página desglosa una respuesta del Inspector. <a href="' + SV_CHAT + '">Hazle una pregunta</a> y toca <b>«📄 Ver la respuesta completa»</b>.</p>'; return; }
    antes.forEach(function (x) { respuesta(x); });
    var r = abre(q, ps.get('abre')) || respuesta(q, antes);
    if (r && r.espera) r.espera.then(arma0); else arma0(r);
    function arma0(r) { integral(q, r).then(function (x) { if (x) r.integ = x; arma(r); }, function () { arma(r); }); }
    function arma(r) {
      if (!r || r.sin) {
        doc.innerHTML = '<h2 class="pa-pag-q">«' + esc(q) + '»</h2>' + (r ? sinRespuesta(q, r.sin) + pideExpHtml() : '') +
          '<p><a class="pa-boton" href="' + SV_CHAT + '?q=' + encodeURIComponent(q) + '">Pregúntasela de otra forma al Inspector ➔</a></p>';
        return;
      }
      r.q = q;
      var ir = r.ir || (r.ficha && r.ficha.ir), dl = enlaceDictamen(q, antes) + (r.abre ? '&abre=' + encodeURIComponent(r.abre) : '');
      var sec = function (ico, tit, h) { return h ? '<section class="pa-pag-sec"><h3><span aria-hidden="true">' + ico + '</span> ' + tit + '</h3>' + h + '</section>' : ''; };
      var genera = r.ficha ? '<a class="pa-boton pa-genera" href="' + esc(dl) + '"' + (vista ? ' target="_blank" rel="noopener"' : '') + '>🧾 Generar dictamen ➔</a>' : '';
      var cuerpo = '<div class="pa-resp">' + r.html + '</div>' + integralHtml(r.integ) +
        (ir ? '<p class="pa-acc"><a class="pa-boton pa-ver" href="' + esc(ir[0]) + '">📖 Saber más <span class="pa-ver-donde">· ' + esc(ir[1]) + '</span> ➔</a></p>' : '') +
        capaModoHtml(q, r) + appDe(r) + expInvHtml(q, r) + servicioHtml(r, q) +
        sec('🧭', 'En las demás partes de la plataforma', r.plat ? '' : recursosHtml(conInv(q, r, r.rec || recursosPara(q, r))).replace(/<p class="pa-mas-t">[^<]*<\/p>/, '')) +
        sec('📚', 'En la Enciclopedia', enciclopediaHtml(enciclopediaPara(q, r)).replace(/<p class="pa-mas-t">[^<]*<\/p>/, '')) +
        (r.web ? webHtml(r.web) : '') +
        (r.ficha ? '<section class="pa-pag-dic"><h3><span aria-hidden="true">🧾</span> Tu dictamen</h3>' +
          '<p>El respaldo de esta respuesta' + (r.integ ? ', con la revisión completa' : '') + ': tu pregunta, lo que se contestó, cada cifra con su estado, sus fuentes y el método, con folio, sello y huella digital. ' +
          'No es un documento oficial ni un peritaje.</p><p class="pa-acc">' + genera + '</p></section>' : '');
      /* La vista del mostrador de Servicios (pedido del autor, 22-11-2026): primero «De un
         vistazo» (la respuesta en corto y lo que encontró cada capítulo de la revisión), el
         dictamen a un toque y, desplegable, todo lo demás. Mismos datos; nada nuevo entra a la huella. */
      doc.innerHTML = '<h2 class="pa-pag-q">«' + esc(q) + '»</h2>' + cabResp(r) + remiteHtml(q, r) + (vista ? vistazoHtml(r, genera) +
        '<details class="pa-vista-mas"' + (/data-pa-abre/.test(cuerpo) ? ' open' : '') + '><summary>Ver la revisión completa, con sus fuentes</summary>' + cuerpo + '</details>' : cuerpo);
      document.title = (r.ficha ? r.ficha.tit : q) + ' · El Inspector · Auditavisión';
      var caja = doc.querySelector('.pa-app[data-pa-abre]');
      if (caja) montaApp(caja);
      doc.addEventListener('click', function (ev) {
        var ap = ev.target.closest ? ev.target.closest('.pa-app') : null;
        if (ap && ev.target.closest('.pa-app-usa')) montaApp(ap);
        else if (ap && ev.target.closest('.pa-app-cierra')) cierraApp(ap);
        var b = ev.target.closest ? ev.target.closest('[data-pa-pregunta]') : null;
        if (b) location.href = (vista ? SV_RESP + '?vista=1&q=' : SV_CHAT + '?q=') + encodeURIComponent(b.getAttribute('data-pa-pregunta'));
      });
    }
  }
  if (resp) {
    window.AuditorBot = { buscar: buscar, charla: charla, respuesta: respuesta, enciclopedia: enciclopediaPara, periodista: periodista, capaModo: capaModo, abre: abre, servicio: servicioHtml };
    armaRespuesta();
    return;
  }
  if (dic) {
    window.AuditorBot = { buscar: buscar, charla: charla, respuesta: respuesta, enciclopedia: enciclopediaPara, periodista: periodista, capaModo: capaModo, abre: abre, servicio: servicioHtml };
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
    var ms = ev.target.closest ? ev.target.closest('[data-pa-modo-sug]') : null;
    if (ms) { poneModo(ms.getAttribute('data-pa-modo-sug'), false); responde(ms.getAttribute('data-pa-q')); return; }
    var ia = ev.target.closest ? ev.target.closest('[data-pa-ia]') : null;
    if (ia) { if (!ia.disabled) pideIa(ia); return; }
    var wb = ev.target.closest ? ev.target.closest('[data-pa-web]') : null;
    if (wb) { if (!wb.disabled) pideWeb(wb); return; }
    var ne = ev.target.closest ? ev.target.closest('.pa-noera') : null;
    if (ne) {
      if (!ne.disabled) anota(ne.getAttribute('data-pa-q'), 'noera', ne.getAttribute('data-pa-tit'));
      ne.disabled = true;
      ne.textContent = '✅ Anotada en «Lo que aún no sé»';
      /* La respuesta no servía: se ofrece la IA, con las fichas más cercanas. */
      var bu = ne.closest('.pa-burbuja');
      if (bu && !bu.querySelector('.pa-ia')) { bu.insertAdjacentHTML('beforeend', iaHtml(ne.getAttribute('data-pa-q'))); guarda(); }
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
  /* Los cuatro modos del Auditor (29-10-2026): el botón de la cabecera, que
     antes desplegaba las herramientas, ahora elige el modo. El modo cambia el
     saludo, la franja de aplicaciones y las preguntas de ejemplo; los datos
     son los mismos en los cuatro. Se recuerda en este navegador y se puede
     pedir por la dirección (?modo=periodista). */
  var app = document.getElementById('paApp'), MODOS_OK = {};
  Array.prototype.forEach.call(app.querySelectorAll('.pa-modo-op'), function (b) { MODOS_OK[b.getAttribute('data-pa-modo')] = 1; });
  function modoActual() { return app.getAttribute('data-modo'); }
  function poneModo(m, avisa) {
    if (!MODOS_OK[m]) return;
    var antes = modoActual();
    app.setAttribute('data-modo', m);
    Array.prototype.forEach.call(app.querySelectorAll('.pa-hola-modo, .pa-modo-franja'), function (x) {
      x.hidden = x.getAttribute('data-modo') !== m;
    });
    var op = null;
    Array.prototype.forEach.call(app.querySelectorAll('.pa-modo-op'), function (b) {
      var si = b.getAttribute('data-pa-modo') === m;
      b.setAttribute('aria-pressed', si ? 'true' : 'false');
      if (si) op = b;
    });
    var et = document.getElementById('paModoActual');
    /* El ícono se copia como está: iconos.js ya cambió el emoji por su trazo. */
    var ico = op ? '<span aria-hidden="true">' + op.querySelector('.pa-modo-ico').innerHTML + '</span> ' : '';
    if (et && op) et.innerHTML = ico + esc(op.getAttribute('data-nom'));
    try { localStorage.setItem('av-modo', m); } catch (e) { /* sin almacenamiento: dura esta vista */ }
    app.dispatchEvent(new CustomEvent('pa-modo', { detail: m }));
    if (avisa && antes !== m && historial.length && op) {
      hilo.insertAdjacentHTML('beforeend', '<li class="pa-msg pa-bot pa-modo-aviso"><div class="pa-burbuja"><p>' +
        ico + 'Ahora estoy en <b>' + esc(op.getAttribute('data-nom')) + '</b>: ' + esc(op.getAttribute('data-lema')) + '.</p></div></li>');
      hilo.scrollTop = hilo.scrollHeight;
    }
  }
  (function () {
    var bt = document.getElementById('paHerrAbre'), menu = document.getElementById('paHerr');
    if (!bt || !menu || SOLO) return;
    function pon(abierto, foco) {
      menu.hidden = !abierto;
      bt.setAttribute('aria-expanded', abierto ? 'true' : 'false');
      if (abierto) { var a = menu.querySelector('[aria-pressed="true"]') || menu.querySelector('button'); if (a) a.focus({ preventScroll: true }); }
      else if (foco) bt.focus({ preventScroll: true });
    }
    bt.addEventListener('click', function () { pon(menu.hidden); });
    menu.addEventListener('click', function (ev) {
      var b = ev.target.closest ? ev.target.closest('[data-pa-modo]') : null;
      if (!b) return;
      poneModo(b.getAttribute('data-pa-modo'), true);
      pon(false, true);
    });
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
    var todas = Array.prototype.slice.call(lista.querySelectorAll('.pa-ej')), bts = todas;
    var otras = document.getElementById('paEjsOtras');
    var tanda = 0, n = 0;
    function porTanda() { return window.innerWidth < 640 ? 4 : 6; }
    function muestra(k) {
      var ini = (k * n) % bts.length;
      todas.forEach(function (b) { if (bts.indexOf(b) < 0) b.hidden = true; });
      bts.forEach(function (b, i) {
        var pos = (i - ini + bts.length) % bts.length;
        b.hidden = pos >= n;
        b.style.setProperty('--pa-i', pos);
      });
    }
    function mide() { n = Math.min(porTanda(), bts.length); otras.hidden = bts.length <= n; muestra(tanda); }
    /* Cada modo muestra solo sus preguntas de ejemplo (29-10-2026). */
    function delModo() {
      var m = modoActual();
      bts = todas.filter(function (b) { return b.getAttribute('data-modo') === m; });
      if (!bts.length) bts = todas;
      tanda = 0; mide();
    }
    app.addEventListener('pa-modo', delModo);
    delModo();
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
  var CLAVE = SOLO ? 'av-chat-sv' : 'av-chat', btReg = document.getElementById('paRegresa'), btLim = document.getElementById('paLimpia');
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
  window.AuditorBot = { buscar: buscar, charla: charla, respuesta: respuesta, enciclopedia: enciclopediaPara, periodista: periodista, capaModo: capaModo, abre: abre, servicio: servicioHtml };
  pintaLista();
  if (canal) document.getElementById('paSinRespNota').innerHTML = 'La lista se guarda solo en tu navegador y no se envía sola: con «Enviarlas a Auditavisión» nos la haces llegar tú.';
  var ps = new URLSearchParams(location.search), pre = ps.get('q'), lista = ps.get('p');
  var muda = (function () {
    /* «Reportero» se llamó así hasta el 29-10-2026 (ahora es «Periodista»): las ligas
       viejas (?modo=reportero) y lo que guardó el navegador siguen sirviendo. */
    var viejo = function (x) { return x === 'reportero' ? 'periodista' : x; };
    var m = viejo(ps.get('modo'));
    /* El modo Inspector vive en Servicios (21-11-2026): una liga vieja al Auditor con
       ?modo=inspector se muda allá con su pregunta. */
    if (m === 'inspector' && !SOLO) {
      ps.delete('modo');
      location.replace(SV_CHAT + (ps.toString() ? '?' + ps.toString() : '') + location.hash);
      return true;
    }
    if (!MODOS_OK[m]) { try { m = viejo(localStorage.getItem('av-modo')); } catch (e) { m = null; } }
    poneModo(MODOS_OK[m] ? m : modoActual());
  })();
  if (muda) return;
  abreUna = ps.get('abre');
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
