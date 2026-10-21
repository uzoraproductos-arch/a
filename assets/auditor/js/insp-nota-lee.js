/* Auditavisión · Modo Inspector › Contrasta una nota, el lector
   (21-10-2026). Las páginas las escribe herramientas/insp_nota.py; el
   catálogo de cifras oficiales llega en JSON (#inDatos), cada renglón con
   sus palabras clave («k»): aquí no se escribe ninguna cifra.

   Paso 1 (liga): abre la nota con un lector externo (r.jina.ai y, de
   respaldo, allorigins), o toma el texto que pega el lector.
   Paso 2 (cifras): encuentra las cantidades en pesos, las empata con el
   catálogo por palabras y deja corregir el empate.
   Paso 3 (veredicto): mide cada cifra contra su documento y da el
   veredicto de conjunto.

   Reglas: solo se contrasta una cifra si la oración nombra a la entidad y
   al concepto de un renglón del catálogo. Lo que no empata queda «sin
   contrastar» y no cuenta como falso. Nada se estima: una cifra oficial
   pendiente no sirve de regla. */
(function () {
  'use strict';

  var D;
  try { D = JSON.parse(document.getElementById('inDatos').textContent); } catch (e) { return; }
  var $ = function (id) { return document.getElementById(id); };
  var raiz = $('inRaiz');
  if (!raiz) return;
  var PASO = raiz.getAttribute('data-paso') || '';
  var porId = {};
  D.cat.forEach(function (o) { porId[o.id] = o; });
  var GRUPOS = { nacional: 'Nacional', paquete: 'Paquete Económico 2027', megaobras: 'Megaobras', federal: 'Dependencias federales', estados: 'Estados' };

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  /* Minúsculas y sin acentos, sin cambiar el largo: así una posición en el
     texto normalizado es la misma en el original. */
  function plano(t) {
    return String(t || '').toLowerCase().replace(/[áàäâ]/g, 'a').replace(/[éèëê]/g, 'e').replace(/[íìïî]/g, 'i')
      .replace(/[óòöô]/g, 'o').replace(/[úùüû]/g, 'u').replace(/ñ/g, 'n');
  }
  function fmt(mdp) { return (mdp < 0 ? '−' : '') + '$' + Math.abs(Number(mdp)).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp'; }
  function pctTx(p) { return (p >= 0 ? '+' : '−') + Math.abs(p).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' %'; }
  function chip(e) { return '<span class="est-chip est-' + esc(e) + '">' + esc(e) + '</span>'; }
  function fuente(o) {
    return o.u ? '<a href="' + esc(o.u) + '" target="_blank" rel="noopener">' + esc(o.f || 'documento') + ' ↗</a>' : esc(o.f || '');
  }
  function dominio(u) { return String(u || '').replace(/^https?:\/\//i, '').split(/[\/?#]/)[0].replace(/^www\./, ''); }
  function ligaValida(v) { v = String(v || '').trim(); return /^https?:\/\/[^\s]+\.[^\s]+/i.test(v) ? v : ''; }
  function estado(t, clase) {
    var el = $('inEstado');
    if (!el) return;
    el.className = 'in-estado' + (clase ? ' ' + clase : '');
    el.innerHTML = t || '';
  }

  /* ---------- La nota guardada entre páginas ---------- */
  var CLAVE = 'auditavision-nota-lee';
  function lee() {
    try { var s = JSON.parse(sessionStorage.getItem(CLAVE)); if (s) return s; } catch (e) { /* sigue */ }
    try { if (window.name.indexOf(CLAVE + ':') === 0) return JSON.parse(window.name.slice(CLAVE.length + 1)); } catch (e) { /* nada */ }
    return null;
  }
  function guarda(n) {
    try { sessionStorage.setItem(CLAVE, JSON.stringify(n)); return; } catch (e) { /* sin almacenamiento */ }
    try { window.name = CLAVE + ':' + JSON.stringify(n); } catch (e) { /* nada */ }
  }
  function olvida() {
    try { sessionStorage.removeItem(CLAVE); } catch (e) { /* nada */ }
    try { if (window.name.indexOf(CLAVE + ':') === 0) window.name = ''; } catch (e) { /* nada */ }
  }
  var nota = lee();
  function consulta() { return nota && nota.liga && nota.origen === 'liga' ? '?liga=' + encodeURIComponent(nota.liga) : ''; }
  function enlaces() {
    [].forEach.call(document.querySelectorAll('a[data-paso]'), function (a) {
      var dest = D.pasos[a.getAttribute('data-paso')];
      if (dest) a.setAttribute('href', dest + consulta());
    });
  }

  /* ---------- Leer la liga ---------- */
  function conTiempo(p, ms) {
    return new Promise(function (ok, mal) {
      var t = setTimeout(function () { mal(new Error('tiempo')); }, ms);
      p.then(function (v) { clearTimeout(t); ok(v); }, function (e) { clearTimeout(t); mal(e); });
    });
  }
  function limpiaMarkdown(t) {
    return t.replace(/!\[[^\]]*\]\([^)]*\)/g, ' ').replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
      .replace(/https?:\/\/\S+/g, ' ').replace(/^[#>*\-\s]+/gm, '').replace(/[*_`]{1,3}/g, '')
      .replace(/[ \t]+/g, ' ').replace(/\n{3,}/g, '\n\n').trim();
  }
  function deJina(t) {
    var tit = (t.match(/^Title:\s*(.+)$/m) || [])[1] || '';
    var i = t.indexOf('Markdown Content:');
    var cuerpo = i >= 0 ? t.slice(i + 17) : t;
    return { titulo: tit.trim(), texto: limpiaMarkdown(cuerpo), lector: 'r.jina.ai' };
  }
  function deHtml(h) {
    var doc = new DOMParser().parseFromString(h, 'text/html');
    [].forEach.call(doc.querySelectorAll('script,style,noscript,nav,header,footer,aside,form,svg,iframe'), function (n) { n.remove(); });
    var og = doc.querySelector('meta[property="og:title"]');
    var tit = (og && og.getAttribute('content')) || (doc.querySelector('title') || {}).textContent || '';
    var base = doc.querySelector('article') || doc.body;
    var partes = base ? [].map.call(base.querySelectorAll('h1,h2,h3,p,li,blockquote'), function (n) { return n.textContent.replace(/\s+/g, ' ').trim(); }) : [];
    var texto = partes.filter(Boolean).join('\n');
    if (texto.length < 200 && base) texto = base.textContent.replace(/\s+/g, ' ').trim();
    return { titulo: tit.trim(), texto: texto, lector: 'allorigins' };
  }
  function suficiente(n) {
    if (!n || !n.texto || n.texto.replace(/\s+/g, ' ').length < 250) throw new Error('corto');
    return n;
  }
  function leerLiga(url) {
    return conTiempo(fetch('https://r.jina.ai/' + url), 25000)
      .then(function (r) { if (!r.ok) throw new Error('http ' + r.status); return r.text(); })
      .then(deJina).then(suficiente)
      .catch(function () {
        return conTiempo(fetch('https://api.allorigins.win/raw?url=' + encodeURIComponent(url)), 25000)
          .then(function (r) { if (!r.ok) throw new Error('http ' + r.status); return r.text(); })
          .then(deHtml).then(suficiente);
      })
      .then(function (n) {
        return { origen: 'liga', liga: url, titulo: n.titulo.slice(0, 220), texto: n.texto.slice(0, 80000), lector: n.lector, aj: {} };
      });
  }
  var REDES = /(^|\.)(x\.com|twitter\.com|facebook\.com|fb\.watch|instagram\.com|tiktok\.com|threads\.net)$/i;
  function avisoFallo(url) {
    return REDES.test(dominio(url))
      ? 'Las redes sociales no dejan que un lector externo abra sus publicaciones. Copia el texto de la publicación y pégalo abajo: la liga ya quedó anotada.'
      : 'No pudimos leer esa liga: el sitio bloqueó al lector, pide suscripción o tardó demasiado. Copia el texto de la nota y pégalo abajo; la liga ya quedó anotada.';
  }

  /* ---------- Encontrar las cifras ---------- */
  var NUM = '(\\d{1,3}(?:[.,]\\d{3})+(?:[.,]\\d+)?|\\d+(?:[.,]\\d+)?)';
  var RE_MONTO = new RegExp('(\\$\\s*)?' + NUM + '(?:\\s+mil\\s+(\\d{1,3}(?:[.,]\\d+)?))?\\s*' +
    '(billones|billon|mil\\s+millones|millones|millon|mmdp|mdp|mdd|mil\\s+pesos|pesos)' +
    '(\\s+de\\s+(?:pesos|dolares)|\\s+(?:usd|dolares|mxn|m\\.n\\.))?(?![a-z0-9])', 'g');
  var FACTOR = { billones: 1e6, billon: 1e6, 'mil millones': 1e3, mmdp: 1e3, millones: 1, millon: 1, mdp: 1, mdd: 1, 'mil pesos': 1e-3, pesos: 1e-6 };

  function numero(s) {
    s = s.replace(/\s/g, '');
    var dec = 0;
    if (/^\d{1,3}(,\d{3})+(\.\d+)?$/.test(s)) s = s.replace(/,/g, '');
    else if (/^\d{1,3}(\.\d{3})+(,\d+)?$/.test(s)) s = s.replace(/\./g, '').replace(',', '.');
    else if (/^\d+,\d+$/.test(s)) s = s.replace(',', '.');
    var m = s.match(/\.(\d+)$/);
    if (m) dec = m[1].length;
    var n = Number(s);
    return isFinite(n) ? { n: n, dec: dec } : null;
  }

  function oraciones(texto) {
    var out = [];
    texto.split(/\n+/).forEach(function (par) {
      var m = par.match(/(?:[^.!?]|[.!?](?![\s"»”]|$))+[.!?]*[»”"]?/g) || [];
      m.forEach(function (o) { o = o.trim(); if (o) out.push(o); });
    });
    return out;
  }

  function extraer(n) {
    var ors = oraciones(n.texto), cifras = [], vistos = {};
    ors.forEach(function (or, i) {
      var p = plano(or), m;
      RE_MONTO.lastIndex = 0;
      while ((m = RE_MONTO.exec(p))) {
        var unidad = m[4].replace(/\s+/g, ' ');
        var a = numero(m[2]);
        if (!a) continue;
        var val = a.n, dec = a.dec;
        if (m[3]) { var b = numero(m[3]); if (!b) continue; val = a.n * 1000 + b.n; dec = b.dec; }
        if (/^\d{4}$/.test(m[2]) && !m[1] && !m[3] && unidad === 'pesos') continue;
        var dolar = unidad === 'mdd' || /dolar|usd/.test(m[5] || '');
        var mdp = val * FACTOR[unidad];
        if (!(mdp >= 1)) continue;
        var antes = p.slice(Math.max(0, m.index - 28), m.index);
        var q = /(mas|poco mas|cerca|alrededor|casi|aproximadamente|unos|menos|hasta|superior a|inferior a)( de)?\s*\$?\s*$/.exec(antes);
        var key = i + ':' + mdp;
        if (vistos[key]) continue;
        vistos[key] = 1;
        cifras.push({
          i: cifras.length, or: i, ini: m.index, fin: m.index + m[0].length,
          bruto: or.slice(m.index, m.index + m[0].length).trim(), mdp: mdp, dolar: dolar,
          tol: 0.5 * Math.pow(10, -dec) * FACTOR[unidad], calif: q ? q[1] : ''
        });
        if (cifras.length >= 40) break;
      }
    });
    return { ors: ors, cifras: cifras };
  }

  /* ---------- Empatar con el catálogo ---------- */
  var RE_CACHE = {};
  function reAlt(alt) {
    if (!RE_CACHE[alt]) {
      RE_CACHE[alt] = new RegExp('(^|[^a-z0-9])' + alt.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + (alt.length <= 4 ? '(?![a-z0-9])' : ''));
    }
    return RE_CACHE[alt];
  }
  function toca(ctx, grupo) { for (var i = 0; i < grupo.length; i++) if (reAlt(grupo[i]).test(ctx)) return true; return false; }
  function sinX(ctx, x) { (x || []).forEach(function (f) { ctx = ctx.split(f).join(' '); }); return ctx; }
  function anios(t) { return (t.match(/(?:^|[^0-9])(19\d{2}|20\d{2})(?![0-9])/g) || []).map(function (s) { return s.replace(/\D/g, ''); }); }
  function aniosItem(o) {
    var a = String(o.a || ''), r = a.match(/(\d{4})\s*-\s*(\d{4})/);
    if (r) { var out = []; for (var y = +r[1]; y <= +r[2]; y++) out.push(String(y)); return out; }
    return anios(a);
  }

  function candidatos(c, ext, titulo) {
    var s = plano(ext.ors[c.or]);
    var e = plano((ext.ors[c.or - 1] || '') + ' ' + ext.ors[c.or] + ' ' + (titulo || ''));
    var ys = anios(s), out = [];
    /* Sin año en la oración, se toma el de sus vecinas, con menos peso. */
    var yv = ys.length ? [] : anios(plano((ext.ors[c.or - 1] || '') + ' ' + (ext.ors[c.or + 1] || '')));
    D.cat.forEach(function (o) {
      if (!o.k) return;
      var cs = sinX(s, o.x), ce = sinX(e, o.x);
      var ent = o.k[0], resto = o.k.slice(1);
      if (resto.length) { if (!toca(ce, ent)) return; } else if (!toca(cs, ent)) return;
      for (var j = 0; j < resto.length; j++) if (!toca(cs, resto[j])) return;
      var pts = 10 + (resto.length && toca(cs, ent) ? 2 : 0);
      var yi = aniosItem(o);
      if (ys.length) pts += ys.some(function (y) { return yi.indexOf(y) >= 0; }) ? 3 : -2;
      else if (yv.length) pts += yv.some(function (y) { return yi.indexOf(y) >= 0; }) ? 1 : 0;
      if (o.b && toca(cs, o.b)) pts += 2;
      var r = c.mdp / Math.abs(o.v);
      if (Math.abs(r - 1) <= 0.015) pts += 6;
      else if (Math.abs(r - 1) <= 0.1) pts += 4;
      else if (Math.abs(r - 1) <= 0.5) pts += 2;
      else if (Math.abs(r / 1000 - 1) < 0.05 || Math.abs(r * 1000 - 1) < 0.05) pts += 1;
      else if (r > 3 || r < 1 / 3) pts -= 4;
      out.push({ id: o.id, pts: pts });
    });
    return out.sort(function (a, b) { return b.pts - a.pts; }).slice(0, 5);
  }

  function analiza(n) {
    var ext = extraer(n);
    ext.cifras.forEach(function (c) {
      c.cands = c.dolar ? [] : candidatos(c, ext, n.titulo);
      var aj = n.aj && Object.prototype.hasOwnProperty.call(n.aj, c.i) ? n.aj[c.i] : null;
      c.sel = aj !== null ? (porId[aj] ? aj : '') : (c.cands[0] && c.cands[0].pts >= 8 ? c.cands[0].id : '');
      c.manual = aj !== null;
    });
    return ext;
  }

  /* ---------- Veredicto de una cifra ---------- */
  function juzga(c, o, s) {
    var ref = Math.abs(o.v), nota = c.mdp, dif = nota - ref, pct = ref ? dif / ref * 100 : 0, r = ref ? nota / ref : 0;
    var v = { dif: dif, pct: pct, tips: [] };
    var ys = anios(plano(s)), yi = aniosItem(o);
    var otroAnio = ys.length && !ys.some(function (y) { return yi.indexOf(y) >= 0; });
    if (o.e === 'pendiente') {
      v.tipo = 'gris'; v.tit = 'Sin documento para contrastar';
      v.porque = 'Nuestra propia cifra está pendiente de documento: no la usamos como regla.';
      return v;
    }
    var aprox = /cerca|alrededor|casi|aproximadamente|unos/.test(c.calif);
    if (Math.abs(dif) <= c.tol || Math.abs(pct) <= 1) {
      v.tipo = 'verde'; v.tit = 'Coincide con el documento';
      v.porque = Math.abs(pct) <= 0.05 ? 'Es la misma cifra que publica el documento.'
        : 'La nota redondea ' + fmt(ref) + ' a «' + c.bruto + '»: el redondeo es correcto (diferencia de ' + Math.abs(pct).toFixed(2) + ' %).';
    } else if (/mas|superior/.test(c.calif) && ref >= nota && ref <= nota * 1.5) {
      v.tipo = 'verde'; v.tit = 'Coincide: la nota dice «más de»';
      v.porque = 'El documento da ' + fmt(ref) + ', que sí es más de lo que dice la nota.';
    } else if (/menos|inferior|hasta/.test(c.calif) && ref <= nota && ref >= nota / 1.5) {
      v.tipo = 'verde'; v.tit = 'Coincide: la nota pone un tope';
      v.porque = 'El documento da ' + fmt(ref) + ', que no rebasa lo que dice la nota.';
    } else if (aprox && Math.abs(pct) <= 10) {
      v.tipo = 'verde'; v.tit = 'Coincide como aproximación';
      v.porque = 'La nota la da como aproximada («' + c.calif + '») y se aleja ' + Math.abs(pct).toFixed(1) + ' % del documento.';
    } else if (Math.abs(r / 1000 - 1) < 0.05 || Math.abs(r * 1000 - 1) < 0.05) {
      v.tipo = 'rojo'; v.tit = 'Error de unidades: mil veces ' + (r > 1 ? 'más' : 'menos');
      v.porque = r > 1 && /billon/.test(plano(c.bruto))
        ? 'Parece el «billion» del inglés (mil millones) traducido como billón (un millón de millones). Con la unidad corregida, la cifra coincidiría.'
        : 'Parece que la nota confunde millones con miles de millones. Con la unidad corregida, la cifra se acercaría al documento.';
      v.tips = ['unidad'];
    } else if (Math.abs(pct) <= 10) {
      v.tipo = 'ambar'; v.tit = 'Se acerca, pero no es la misma cifra';
      v.porque = 'Se aleja ' + pctTx(pct) + ' del documento. Suele deberse a otro año, a comparar lo aprobado con lo ejercido, a pesos de otro año o a un redondeo grueso.';
      v.tips = ['anio', 'etapa', 'real'];
    } else {
      v.tipo = 'rojo'; v.tit = 'No coincide con el documento';
      v.porque = 'La nota da una cifra ' + (dif > 0 ? Math.abs(pct).toFixed(1) + ' % mayor' : Math.abs(pct).toFixed(1) + ' % menor') + ' que el documento.';
      v.tips = ['anio', 'concepto', 'etapa', 'unidad'];
    }
    if (otroAnio) {
      v.porque += ' Ojo: la oración habla de ' + ys.join(', ') + ' y la cifra oficial es de ' + o.a + '; puede que midan años distintos.';
      if (v.tips.indexOf('anio') < 0) v.tips.push('anio');
    }
    if (o.v < 0 || o.s === 'negativo') { v.porque += ' El documento la publica en negativo; la comparamos en valor absoluto.'; v.tips.push('signo'); }
    if (o.op) v.porque += ' Cómo se calcula la oficial: ' + o.op;
    return v;
  }
  var PUNTOS = { verde: 1, ambar: 0.5, rojo: 0 };

  function conjunto(ext) {
    var r = { n: 0, verde: 0, ambar: 0, rojo: 0, sin: 0, dolar: 0, pts: 0, tips: {} };
    ext.cifras.forEach(function (c) {
      if (c.dolar) { r.dolar++; return; }
      var o = c.sel && porId[c.sel];
      if (!o) { r.sin++; return; }
      c.v = juzga(c, o, ext.ors[c.or]);
      if (c.v.tipo === 'gris') { r.sin++; return; }
      r.n++; r[c.v.tipo]++; r.pts += PUNTOS[c.v.tipo];
      c.v.tips.forEach(function (t) { r.tips[t] = 1; });
    });
    r.pct = r.n ? Math.round(r.pts / r.n * 100) : null;
    if (!r.n) { r.clase = 'in-v-gris'; r.tit = 'No encontramos cifras que podamos contrastar'; }
    else if (r.pct === 100) { r.clase = 'in-v-verde'; r.tit = 'Las cifras de la nota se sostienen'; }
    else if (r.pct >= 70) { r.clase = 'in-v-verde'; r.tit = 'Las cifras se sostienen en su mayoría'; }
    else if (r.pct >= 40) { r.clase = 'in-v-ambar'; r.tit = 'Las cifras se sostienen a medias'; }
    else { r.clase = 'in-v-rojo'; r.tit = 'Las cifras de la nota no se sostienen'; }
    return r;
  }

  /* ---------- Pintar ---------- */
  function cabecera(n) {
    var el = $('inCabNota');
    if (!el) return;
    el.innerHTML = '<p class="in-cn-k">' + (n.origen === 'liga' ? 'Nota leída de' : 'Texto pegado') +
      (n.liga ? ' · <a href="' + esc(n.liga) + '" target="_blank" rel="noopener noreferrer nofollow">' + esc(dominio(n.liga)) + ' ↗</a>' : '') + '</p>' +
      (n.titulo ? '<p class="in-cn-t">' + esc(n.titulo) + '</p>' : '') +
      '<p class="in-cn-m">' + n.texto.length.toLocaleString('es-MX') + ' caracteres' + (n.lector ? ' · leída con ' + esc(n.lector) : '') + '</p>';
  }
  function oracionMarcada(ext, c) {
    var s = ext.ors[c.or], a = c.ini, b = c.fin;
    var pre = s.slice(Math.max(0, a - 160), a), post = s.slice(b, b + 160);
    return (a > 160 ? '…' : '') + esc(pre) + '<mark>' + esc(s.slice(a, b)) + '</mark>' + esc(post) + (b + 160 < s.length ? '…' : '');
  }
  function opciones(c) {
    var html = '<option value=""' + (c.sel ? '' : ' selected') + '>Sin contrastar: no habla de una cifra del catálogo</option>';
    if (c.cands.length) {
      html += '<optgroup label="Las que más se parecen">' + c.cands.map(function (k) {
        var o = porId[k.id];
        return '<option value="' + esc(o.id) + '"' + (c.sel === o.id ? ' selected' : '') + '>' + esc(o.n) + ' · ' + esc(fmt(o.v)) + '</option>';
      }).join('') + '</optgroup>';
    }
    Object.keys(GRUPOS).forEach(function (g) {
      html += '<optgroup label="' + esc(GRUPOS[g]) + '">' + D.cat.filter(function (o) { return o.g === g; }).map(function (o) {
        var en = c.cands.some(function (k) { return k.id === o.id; });
        return en ? '' : '<option value="' + esc(o.id) + '"' + (c.sel === o.id ? ' selected' : '') + '>' + esc(o.n) + ' · ' + esc(fmt(o.v)) + '</option>';
      }).join('') + '</optgroup>';
    });
    return html;
  }
  function pastilla(c, ext) {
    if (c.dolar) return '<span class="in-pill in-pill-gris">En dólares: no la comparamos</span>';
    var o = c.sel && porId[c.sel];
    if (!o) return '<span class="in-pill in-pill-gris">Sin contrastar</span>';
    var v = juzga(c, o, ext.ors[c.or]);
    return '<span class="in-pill in-pill-' + v.tipo + '">' + esc(v.tit) + (v.tipo === 'gris' ? '' : ' · ' + esc(pctTx(v.pct))) + '</span>';
  }
  function tarjetaCifra(c, ext) {
    var o = c.sel && porId[c.sel];
    return '<li class="in-hall" id="inC' + c.i + '">' +
      '<p class="in-hall-or">' + oracionMarcada(ext, c) + '</p>' +
      '<p class="in-hall-lee">La nota dice <b>' + esc(c.bruto) + '</b>' + (c.dolar ? '' : ' = <b>' + fmt(c.mdp) + '</b>') + ' ' + pastilla(c, ext) + '</p>' +
      (c.dolar ? '' :
        '<label class="in-campo"><span>' + (c.manual ? 'La contrastas con' : c.sel ? 'La contrastamos con (empate automático, cámbialo si no es)' : 'No encontramos con qué contrastarla. Si sabes de qué cifra oficial habla, elígela') + '</span>' +
        '<select class="in-input in-empate" data-i="' + c.i + '">' + opciones(c) + '</select></label>' +
        (o ? '<p class="in-hall-of">Documento: <b>' + fmt(o.v) + '</b> ' + chip(o.e) + ' <small>' + esc(o.a) + '</small> · ' + fuente(o) + '</p>' : '')) +
      '</li>';
  }

  function pintaCifras(n, ext) {
    var cont = $('inCifras');
    if (!ext.cifras.length) {
      cont.innerHTML = '<p class="in-ver in-v-gris">No encontramos cantidades en pesos en esta nota (buscamos cifras con su unidad: «millones», «mil millones», «billones», «mdp»). ' +
        'Si la nota sí trae cifras, puede que el lector no haya traído el texto completo: <a href="' + esc(D.pasos.liga) + '">pega el texto en el paso 1</a>.</p>';
      return;
    }
    var con = ext.cifras.filter(function (c) { return c.sel; }).length;
    cont.innerHTML = '<p class="in-txt">Encontramos <b>' + ext.cifras.length + (ext.cifras.length === 1 ? ' cifra' : ' cifras') + ' de dinero</b>; ' +
      (con ? '<b>' + con + '</b> ' + (con === 1 ? 'habla' : 'hablan') + ' de algo que tenemos con documento.' : 'ninguna empata sola con una cifra de nuestro catálogo.') +
      ' Revisa cada empate: lo hacemos por las palabras de la oración y puede fallar.</p>' +
      '<ol class="in-hallazgos">' + ext.cifras.map(function (c) { return tarjetaCifra(c, ext); }).join('') + '</ol>';
    var ir = $('inIrVeredicto');
    if (ir) ir.hidden = false;
    cont.addEventListener('change', function (ev) {
      var s = ev.target;
      if (!s.classList || !s.classList.contains('in-empate')) return;
      var i = +s.getAttribute('data-i'), c = ext.cifras[i];
      n.aj = n.aj || {}; n.aj[i] = s.value; guarda(n);
      c.sel = s.value; c.manual = true;
      var li = $('inC' + i), tmp = document.createElement('div');
      tmp.innerHTML = tarjetaCifra(c, ext);
      li.parentNode.replaceChild(tmp.firstChild, li);
      var nuevo = $('inC' + i).querySelector('select');
      if (nuevo) nuevo.focus();
    });
  }

  function textoVeredicto(n, ext, r) {
    var L = ['Veredicto de Auditavisión: ' + r.tit + (r.pct !== null ? ' (' + r.pct + ' de 100)' : ''),
      n.liga ? 'Nota: ' + n.liga : 'Nota: texto pegado' + (n.titulo ? ' («' + n.titulo + '»)' : '')];
    ext.cifras.forEach(function (c) {
      var o = c.sel && porId[c.sel];
      if (!o || !c.v || c.v.tipo === 'gris') return;
      L.push('- La nota dice ' + c.bruto + ' (' + fmt(c.mdp) + '). Documento: ' + o.n + ' (' + o.a + ') = ' + fmt(o.v) + ' [' + o.e + ']. ' +
        c.v.tit + ', ' + pctTx(c.v.pct) + '. Fuente: ' + (o.f || '') + (o.u ? ' ' + o.u : ''));
    });
    if (r.sin) L.push('Cifras sin contrastar (sin documento en el catálogo): ' + r.sin);
    L.push('Califica las cifras, no al medio. Verifícala tú: ' + (n.liga && n.origen === 'liga' ? location.origin + location.pathname + '?liga=' + encodeURIComponent(n.liga) : location.origin + location.pathname));
    return L.join('\n');
  }

  function pintaVeredicto(n, ext) {
    var r = conjunto(ext), cont = $('inVeredicto');
    var contr = ext.cifras.filter(function (c) { return c.v && c.v.tipo !== 'gris' && !c.dolar && c.sel; });
    var sin = ext.cifras.filter(function (c) { return !c.dolar && (!c.sel || (c.v && c.v.tipo === 'gris')); });
    var dol = ext.cifras.filter(function (c) { return c.dolar; });
    var medidor = r.pct === null ? '' :
      '<div class="in-medidor" role="img" aria-label="Las cifras se sostienen ' + r.pct + ' de 100">' +
        '<div class="in-med-zonas"><span class="in-z3">No se sostienen</span><span class="in-z2">A medias</span><span class="in-z1">Se sostienen</span></div>' +
        '<div class="in-med-barra in-med-inv"><span class="in-med-marca" style="left:' + r.pct + '%"></span></div>' +
        '<div class="in-med-esc" aria-hidden="true"><span style="left:0%">0</span><span style="left:40%">40</span><span style="left:70%">70</span><span style="left:100%">100</span></div>' +
      '</div>';
    var cuenta = '<ul class="in-cuentas">' +
      (r.verde ? '<li class="in-pill in-pill-verde">' + r.verde + ' coinciden</li>' : '') +
      (r.ambar ? '<li class="in-pill in-pill-ambar">' + r.ambar + ' se acercan</li>' : '') +
      (r.rojo ? '<li class="in-pill in-pill-rojo">' + r.rojo + ' no coinciden</li>' : '') +
      (r.sin ? '<li class="in-pill in-pill-gris">' + r.sin + ' sin contrastar</li>' : '') +
      (r.dolar ? '<li class="in-pill in-pill-gris">' + r.dolar + ' en dólares</li>' : '') + '</ul>';
    var just = contr.map(function (c, k) {
      var o = porId[c.sel], ref = Math.abs(o.v), mx = Math.max(c.mdp, ref) || 1;
      return '<li class="in-just in-just-' + c.v.tipo + '">' +
        '<p class="in-just-tit"><span class="in-n">' + (k + 1) + '</span> ' + esc(c.v.tit) + ' <b>' + esc(pctTx(c.v.pct)) + '</b></p>' +
        '<p class="in-hall-or">' + oracionMarcada(ext, c) + '</p>' +
        '<div class="in-tabla">' +
          '<div><span>La nota</span><b>' + fmt(c.mdp) + '</b><small>«' + esc(c.bruto) + '»</small></div>' +
          '<div><span>El documento ' + chip(o.e) + '</span><b>' + fmt(o.v) + '</b><small>' + esc(o.n) + ' · ' + esc(o.a) + '</small></div>' +
          '<div><span>Diferencia ' + chip('derivado') + '</span><b>' + (c.v.dif >= 0 ? '+' : '−') + fmt(Math.abs(c.v.dif)) + '</b><small>Cifra de la nota menos la del documento.</small></div>' +
        '</div>' +
        '<div class="in-barras" aria-hidden="true">' +
          '<div class="in-bar"><span class="in-bar-et">La nota</span><span class="in-bar-pista"><span class="in-bar-r in-bar-nota" style="width:' + Math.max(0.5, c.mdp / mx * 100).toFixed(2) + '%"></span></span></div>' +
          '<div class="in-bar"><span class="in-bar-et">Documento</span><span class="in-bar-pista"><span class="in-bar-r in-bar-doc" style="width:' + Math.max(0.5, ref / mx * 100).toFixed(2) + '%"></span></span></div>' +
        '</div>' +
        '<p class="in-v-porque"><b>Interpretación:</b> ' + esc(c.v.porque) + '</p>' +
        '<p class="in-v-fuente">Fuente: ' + fuente(o) + '</p></li>';
    }).join('');
    var lista = function (arr, tit, txt) {
      return arr.length ? '<details class="in-sin"><summary>' + tit + ' (' + arr.length + ')</summary><p class="in-txt">' + txt + '</p><ul>' +
        arr.map(function (c) { return '<li>' + oracionMarcada(ext, c) + '</li>'; }).join('') + '</ul></details>' : '';
    };
    cont.innerHTML =
      '<div class="in-ver ' + r.clase + '">' +
        '<p class="in-v-tit">' + esc(r.tit) + '</p>' +
        (r.pct !== null ? '<p class="in-v-grande">' + r.pct + '<small> de 100 · ' + r.n + (r.n === 1 ? ' cifra contrastada' : ' cifras contrastadas') + '</small></p>' : '') +
        medidor + cuenta +
        (r.n ? '<p class="in-v-porque">Cada cifra que coincide vale 1; la que se acerca, ½; la que no coincide, 0. El resultado es el promedio sobre 100 ' + chip('derivado') + '. Califica las cifras en pesos de la nota frente a sus documentos, no al medio.</p>'
          : '<p class="in-v-porque">La nota no trae cifras en pesos que hablen de algo que tengamos con documento, así que no damos veredicto. Si sabes de qué cifra oficial habla alguna, elígela en el <a href="' + esc(D.pasos.cifras + consulta()) + '">paso 2</a> o búscala en el <a href="' + esc(D.catalogo) + '">catálogo</a>.</p>') +
      '</div>' +
      (just ? '<h3 class="in-sub">La justificación, cifra por cifra</h3><ol class="in-justs">' + just + '</ol>' : '') +
      lista(sin, 'Cifras sin contrastar', 'No tenemos documento de lo que miden, o no supimos de qué hablan. No cuentan en el veredicto: no las damos por falsas ni por ciertas.') +
      lista(dol, 'Cifras en dólares', 'Nuestro catálogo está en pesos; convertirlas exigiría un tipo de cambio que la nota no siempre dice.') +
      '<div class="in-acciones">' +
        '<button type="button" class="in-boton" id="inCopiar"><span aria-hidden="true">📋</span> Copiar el veredicto</button>' +
        '<a class="in-boton in-sec" href="' + esc(D.pasos.cifras + consulta()) + '" data-paso="cifras">Ajustar los empates</a>' +
        '<button type="button" class="in-boton in-sec" id="inOtra"><span aria-hidden="true">↺</span> Verificar otra nota</button>' +
      '</div>' +
      '<p class="in-copiado" id="inCopiado" role="status"></p>';
    [].forEach.call(raiz.querySelectorAll('.in-tips li'), function (li) { li.classList.toggle('in-tip-on', !!r.tips[li.getAttribute('data-tip')]); });
    $('inCopiar').addEventListener('click', function () { copiar(textoVeredicto(n, ext, r)); });
    $('inOtra').addEventListener('click', function () { olvida(); location.href = D.pasos.liga; });
  }

  function copiar(texto) {
    var aviso = $('inCopiado');
    function hecho() { aviso.textContent = '✓ Veredicto copiado. Pégalo donde quieras compartirlo.'; }
    function aMano() {
      var ta = document.createElement('textarea');
      ta.value = texto; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      if (ok) hecho(); else aviso.textContent = 'Tu navegador no dejó copiar. Selecciona el texto y cópialo a mano.';
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(texto).then(hecho, aMano);
    else aMano();
  }

  /* ---------- Cada página ---------- */
  function conNota(pintar) {
    var q = ligaValida(new URLSearchParams(location.search).get('liga'));
    if (q && (!nota || nota.liga !== q || nota.origen !== 'liga')) {
      estado('Leyendo la nota de <b>' + esc(dominio(q)) + '</b>… puede tardar unos segundos.', 'in-est-lee');
      leerLiga(q).then(function (n) {
        nota = n; guarda(n); estado(''); enlaces(); cabecera(n); pintar(n, analiza(n));
      }, function () {
        estado(esc(avisoFallo(q)) + ' <a href="' + esc(D.pasos.liga) + '">Ir al paso 1</a>.', 'in-est-mal');
        olvida(); nota = { origen: 'texto', liga: q, titulo: '', texto: '', aj: {} }; guarda(nota);
      });
      return;
    }
    if (!nota || !nota.texto) {
      estado('Todavía no hay nota que revisar. <a href="' + esc(D.pasos.liga) + '">Pégala en el paso 1</a>.', 'in-est-mal');
      return;
    }
    cabecera(nota);
    pintar(nota, analiza(nota));
  }

  enlaces();
  if (PASO === 'liga') {
    var url = $('inUrl'), texto = $('inTexto'), urlT = $('inUrlTexto');
    if (nota && nota.liga) { url.value = nota.liga; urlT.value = nota.liga; }
    if (nota && nota.origen === 'texto' && nota.texto) texto.value = nota.texto;
    $('inFormLiga').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var u = ligaValida(url.value);
      if (!u) { estado('Esa liga no parece completa: debe empezar con https://', 'in-est-mal'); url.focus(); return; }
      var boton = $('inLeer');
      boton.disabled = true;
      estado('Leyendo la nota de <b>' + esc(dominio(u)) + '</b>… puede tardar unos segundos.', 'in-est-lee');
      leerLiga(u).then(function (n) {
        nota = n; guarda(n);
        location.href = D.pasos.cifras + consulta();
      }, function () {
        boton.disabled = false;
        urlT.value = u;
        estado(esc(avisoFallo(u)), 'in-est-mal');
        texto.focus();
      });
    });
    $('inFormTexto').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var t = String(texto.value || '').trim();
      if (t.length < 40) { estado('Pega el texto de la nota: con unas cuantas palabras no alcanzamos a encontrar sus cifras.', 'in-est-mal'); texto.focus(); return; }
      var primera = t.split(/\n/)[0].trim();
      nota = { origen: 'texto', liga: ligaValida(urlT.value), titulo: primera.length <= 160 ? primera : '', texto: t.slice(0, 80000), aj: {} };
      guarda(nota);
      location.href = D.pasos.cifras;
    });
  } else if (PASO === 'cifras') {
    conNota(pintaCifras);
  } else if (PASO === 'veredicto') {
    conNota(pintaVeredicto);
  } else {
    var sigues = $('inSigues');
    if (sigues && nota && nota.texto) {
      sigues.hidden = false;
      sigues.innerHTML = '<b>Ya tienes una nota en revisión' + (nota.titulo ? ': «' + esc(nota.titulo) + '»' : '') + '.</b> ' +
        '<a href="' + esc(D.pasos.veredicto + consulta()) + '" data-paso="veredicto">Ve su veredicto</a> o ' +
        '<button type="button" class="in-borrar" id="inBorrar">empieza con otra</button>.';
      $('inBorrar').addEventListener('click', function () { olvida(); nota = null; sigues.hidden = true; enlaces(); });
    }
  }
})();
