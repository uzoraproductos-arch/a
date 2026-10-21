/* Auditavisión · Modo Inspector › Contrasta una nota, el verificador
   (21-10-2026). La página la escribe herramientas/insp_nota.py; el
   catálogo de cifras oficiales llega en JSON (#inDatos), cada renglón con
   sus palabras clave («k»): aquí no se escribe ninguna cifra.

   Todo pasa en una sola página (pedido del autor, 21-10-2026): el lector
   pega la liga (r.jina.ai y, de respaldo, allorigins) o el texto; aquí se
   encuentran las cantidades en pesos, se empatan con el catálogo por
   palabras y, debajo del portal, sale el veredicto con su semáforo y la
   justificación de cada cifra, que el lector puede reempatar ahí mismo.
   Si la nota no habla de dinero público (D.fiscal), se dice y no se
   califica.

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
  var REDES = /(^|\.)(x\.com|twitter\.com|facebook\.com|fb\.watch|instagram\.com|tiktok\.com|threads\.net)$/i;
  var VIDEO = /(^|\.)(youtube\.com|youtu\.be|vimeo\.com)$/i;
  function leerLiga(url) {
    var minimo = VIDEO.test(dominio(url)) ? 80 : 250;
    function suficiente(n) {
      if (!n || !n.texto || n.texto.replace(/\s+/g, ' ').length < minimo) throw new Error('corto');
      return n;
    }
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
  function avisoFallo(url) {
    var d = dominio(url);
    if (REDES.test(d)) return 'Las redes sociales no dejan que un lector externo abra sus publicaciones. Copia el texto de la publicación y pégalo aquí: la liga ya quedó anotada.';
    if (VIDEO.test(d)) return 'No pudimos leer ese video. Pega aquí su transcripción (en YouTube: «…Más» › «Mostrar transcripción») o lo que dice su descripción: la liga ya quedó anotada.';
    return 'No pudimos leer esa liga: el sitio bloqueó al lector, pide suscripción o tardó demasiado. Copia el texto de la nota y pégalo aquí; la liga ya quedó anotada.';
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

  /* ---------- ¿Es una nota de dinero público? ---------- */
  function relevancia(n) {
    var t = ' ' + plano((n.titulo || '') + ' ' + n.texto) + ' ', pts = 0, temas = [];
    Object.keys(D.fiscal || {}).forEach(function (peso) {
      D.fiscal[peso].forEach(function (w) { if (reAlt(w).test(t)) pts += +peso; });
    });
    (D.temas || []).forEach(function (x) { if (temas.length < 6 && toca(t, x.k)) temas.push(x); });
    return { pts: pts, temas: temas };
  }

  /* ---------- El sello de Auditavisión (como los estados de cuenta) ---------- */
  var LOGO = 'assets/auditor/img/logo-auditavision.svg';
  function selloSitio() { var b = document.querySelector('.apartado-pie-txt b'); return b ? b.textContent : ''; }
  function hoyFecha() {
    var d = new Date();
    return d.toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' }) + ', ' + d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
  }
  function sello(fol) {
    var id = 'inArco' + Math.random().toString(36).slice(2, 7);
    return '<svg class="in-sello-svg" viewBox="0 0 120 120" role="img" aria-label="Sello del verificador de notas de Auditavisión">' +
      '<defs><path id="' + id + '" d="M60,60 m-44,0 a44,44 0 1,1 88,0 a44,44 0 1,1 -88,0"/></defs>' +
      '<circle cx="60" cy="60" r="57" fill="none" stroke="currentColor" stroke-width="2.5"/>' +
      '<circle cx="60" cy="60" r="35" fill="none" stroke="currentColor" stroke-width="1.2"/>' +
      '<text font-size="9.4" font-weight="800" letter-spacing="2.2" fill="currentColor"><textPath href="#' + id + '">AUDITAVISIÓN · VERIFICADOR DE NOTAS ·</textPath></text>' +
      '<text x="60" y="58" text-anchor="middle" font-size="22" font-weight="900" fill="currentColor">✓</text>' +
      '<text x="60" y="74" text-anchor="middle" font-size="7.5" font-weight="800" fill="currentColor">' + esc(fol ? fol.split('-').slice(-1)[0] : '········') + '</text></svg>';
  }
  var LEYENDA = 'Lo expide Auditavisión, plataforma ciudadana de fiscalización del gasto público. No es un documento oficial del gobierno, de la Auditoría Superior ni del medio que publicó la nota. Califica las cifras de la nota frente a sus documentos oficiales, no al medio ni a quien la escribió.';
  /* La huella es del veredicto: la nota, cada empate y cada resultado. Si
     cambia un empate, cambian la huella y el folio. */
  function huella(n, ext, r) {
    var obj = {
      nota: n.liga || n.titulo || n.texto.slice(0, 200), v: selloSitio(), pct: r.pct, tit: r.tit,
      cifras: ext.cifras.map(function (c) { return [c.bruto, c.mdp, c.sel || '', c.v ? c.v.tipo : ''] })
    };
    if (!(window.crypto && crypto.subtle && window.TextEncoder)) return Promise.resolve(null);
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(obj))).then(function (b) {
      return [].map.call(new Uint8Array(b), function (x) { return ('0' + x.toString(16)).slice(-2); }).join('');
    }).catch(function () { return null; });
  }
  function folioDe(hx) {
    var d = new Date();
    return 'VN-' + d.getFullYear() + ('0' + (d.getMonth() + 1)).slice(-2) + ('0' + d.getDate()).slice(-2) + '-' + hx.slice(0, 8).toUpperCase();
  }
  function dictamenCab() {
    return '<header class="in-dic-cab">' +
      '<div class="in-dic-marca"><img src="' + LOGO + '" alt="" width="62" height="48"><div><b>Auditavisión</b><small>Verificador de notas · dictamen ciudadano</small></div></div>' +
      '<dl class="in-dic-meta"><div><dt>Folio</dt><dd class="in-folio">calculando…</dd></div><div><dt>Expedido</dt><dd>' + esc(hoyFecha()) + '</dd></div></dl>' +
      '<p class="in-dic-aviso"><b>No es un documento oficial.</b> Es el dictamen de Auditavisión sobre las cifras de la nota; cada cifra oficial lleva su documento.</p>' +
      '</header>';
  }
  function dictamenPie() {
    return '<footer class="in-dic-pie"><div class="in-dic-sello">' + sello(null) + '</div><div class="in-dic-tx">' +
      '<b>Dictamen del verificador de notas de Auditavisión</b>' +
      '<p>Folio <b class="in-folio">calculando…</b> · Versión de la plataforma <b>' + esc(selloSitio()) + '</b></p>' +
      '<p class="in-huella">Huella digital (SHA-256 del veredicto): <code id="inHuella">calculando…</code></p>' +
      '<p class="in-leyenda">' + esc(LEYENDA).replace('No es un documento oficial', '<b>No es un documento oficial</b>') +
      ' El sello certifica que cada cifra oficial proviene de la fuente citada y que el veredicto no se ha alterado: si cambia una cifra o un empate, la huella ya no coincide.</p>' +
      '</div></footer>';
  }
  var firmado = { folio: '', huella: '' };
  function firma(n, ext, r) {
    var cont = $('inVeredicto');
    huella(n, ext, r).then(function (hx) {
      var fol = hx ? folioDe(hx) : null;
      firmado = { folio: fol || '', huella: hx || '' };
      [].forEach.call(cont.querySelectorAll('.in-folio'), function (el) { el.textContent = fol || 'no disponible en este navegador'; });
      var h = $('inHuella');
      if (h) h.textContent = hx ? hx.replace(/(.{16})/g, '$1 ').trim() : 'no disponible en este navegador';
      var s = cont.querySelector('.in-dic-sello');
      if (s) s.innerHTML = sello(fol);
    });
  }

  /* ---------- Pintar ---------- */
  function cabecera(n) {
    var el = $('inCabNota');
    var video = n.liga && VIDEO.test(dominio(n.liga)) && n.origen === 'liga';
    el.innerHTML = '<p class="in-cn-k">' + (n.origen === 'liga' ? 'Nota leída de' : 'Texto pegado') +
      (n.liga ? ' · <a href="' + esc(n.liga) + '" target="_blank" rel="noopener noreferrer nofollow">' + esc(dominio(n.liga)) + ' ↗</a>' : '') + '</p>' +
      (n.titulo ? '<p class="in-cn-t">' + esc(n.titulo) + '</p>' : '') +
      '<p class="in-cn-m">' + n.texto.length.toLocaleString('es-MX') + ' caracteres' + (n.lector ? ' · leída con ' + esc(n.lector) : '') + '</p>' +
      (video ? '<p class="in-cn-m">De un video leemos el título y la descripción, no lo que se dice en él. Si las cifras están en lo que se habla, pega su transcripción en «Pegar el texto».</p>' : '');
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
  function selector(c, rotulo) {
    return '<label class="in-campo"><span>' + rotulo + '</span>' +
      '<select class="in-input in-empate" data-i="' + c.i + '">' + opciones(c) + '</select></label>';
  }
  function luz(tipo) {
    return '<span class="in-semaforo in-sem-chico" aria-hidden="true">' + ['rojo', 'ambar', 'verde'].map(function (t) {
      return '<span class="in-luz in-luz-' + t + (t === tipo ? ' on' : '') + '"></span>';
    }).join('') + '</span>';
  }
  var SIGNIFICA = {
    100: 'Todo lo que pudimos revisar coincide con los documentos oficiales.',
    70: 'Lo esencial se sostiene, pero hay cifras que no cuadran: revísalas abajo.',
    40: 'Hay cifras ciertas y cifras que no cuadran con el documento: léela con cuidado.',
    0: 'La mayoría de sus cifras no coinciden con los documentos oficiales.'
  };
  function significa(p) { return p === 100 ? SIGNIFICA[100] : p >= 70 ? SIGNIFICA[70] : p >= 40 ? SIGNIFICA[40] : SIGNIFICA[0]; }
  function enN(k, uno, varios) { return k + ' ' + (k === 1 ? uno : varios); }

  function justificacion(c, ext, k) {
    var o = porId[c.sel], ref = Math.abs(o.v), mx = Math.max(c.mdp, ref) || 1;
    return '<li class="in-just in-just-' + c.v.tipo + '" data-tipo="' + c.v.tipo + '">' +
      '<p class="in-just-tit">' + luz(c.v.tipo) + '<span class="in-n">' + (k + 1) + '</span> ' + esc(c.v.tit) + ' <b>' + esc(pctTx(c.v.pct)) + '</b></p>' +
      '<p class="in-hall-or">' + oracionMarcada(ext, c) + '</p>' +
      '<div class="in-tabla">' +
        '<div><span>Lo que dice la nota</span><b>' + fmt(c.mdp) + '</b><small>«' + esc(c.bruto) + '»</small></div>' +
        '<div><span>Lo que dice el documento ' + chip(o.e) + '</span><b>' + fmt(o.v) + '</b><small>' + esc(o.n) + ' · ' + esc(o.a) + '</small></div>' +
        '<div><span>Diferencia ' + chip('derivado') + '</span><b>' + (c.v.dif >= 0 ? '+' : '−') + fmt(Math.abs(c.v.dif)) + '</b><small>La nota menos el documento.</small></div>' +
      '</div>' +
      '<div class="in-barras" aria-hidden="true">' +
        '<div class="in-bar"><span class="in-bar-et">La nota</span><span class="in-bar-pista"><span class="in-bar-r in-bar-nota" style="width:' + Math.max(0.5, c.mdp / mx * 100).toFixed(2) + '%"></span></span></div>' +
        '<div class="in-bar"><span class="in-bar-et">Documento</span><span class="in-bar-pista"><span class="in-bar-r in-bar-doc" style="width:' + Math.max(0.5, ref / mx * 100).toFixed(2) + '%"></span></span></div>' +
      '</div>' +
      '<p class="in-v-porque"><b>Qué quiere decir:</b> ' + esc(c.v.porque) + '</p>' +
      '<p class="in-v-fuente">Documento oficial: ' + fuente(o) + '</p>' +
      '<details class="in-ajusta"><summary>¿No es esta la cifra oficial? Cámbiala</summary>' +
        selector(c, 'Empatamos esta cifra por las palabras de la oración. Si habla de otra cosa, elige la correcta o déjala sin contrastar.') +
      '</details></li>';
  }

  function pinta(n) {
    var ext = analiza(n), r = conjunto(ext), rel = relevancia(n), cont = $('inVeredicto');
    var contr = ext.cifras.filter(function (c) { return c.v && c.v.tipo !== 'gris' && !c.dolar && c.sel; });
    var sin = ext.cifras.filter(function (c) { return !c.dolar && (!c.sel || (c.v && c.v.tipo === 'gris')); });
    var dol = ext.cifras.filter(function (c) { return c.dolar; });
    var tema = r.n > 0 || rel.pts >= 2;
    var cab, tipo = r.pct === null ? 'gris' : r.pct >= 70 ? 'verde' : r.pct >= 40 ? 'ambar' : 'rojo';
    if (r.n) {
      cab = '<p class="in-v-tit">' + esc(r.tit) + '</p>' +
        '<p class="in-v-grande">' + r.pct + '<small> de 100</small></p>' +
        '<p class="in-v-sig">' + esc(significa(r.pct)) + '</p>';
    } else if (!tema) {
      r.tit = 'Esta nota no se identifica dentro de los supuestos ni de las investigaciones de la plataforma';
      cab = '<p class="in-v-tit">' + esc(r.tit) + '</p>' +
        '<p class="in-v-sig">No habla de dinero público: presupuesto, deuda, impuestos, contratos, obras o lo que revisa la Auditoría Superior. ' +
        'El verificador solo califica cifras de finanzas públicas que podamos sostener con un documento oficial' +
        (ext.cifras.length ? '; las ' + enN(ext.cifras.length, 'cifra de dinero', 'cifras de dinero') + ' que trae no son de ese tipo.' : '.') + '</p>';
    } else if (!ext.cifras.length) {
      r.tit = 'Habla de dinero público, pero no trae cifras que contrastar';
      cab = '<p class="in-v-tit">' + esc(r.tit) + '</p>' +
        '<p class="in-v-sig">No encontramos cantidades con su unidad («millones», «mil millones», «billones», «mdp»). Si la nota sí las trae, puede que el lector no haya traído el texto completo: pégalo en «Pegar el texto». Abajo está lo que la plataforma tiene sobre el tema.</p>';
    } else {
      r.tit = 'Sus cifras no están entre las que tenemos con documento';
      cab = '<p class="in-v-tit">' + esc(r.tit) + '</p>' +
        '<p class="in-v-sig">La nota habla de dinero público, pero ninguna de sus cifras empata con nuestro catálogo de cifras oficiales, así que no damos veredicto: no las damos por falsas ni por ciertas. Si sabes de qué cifra oficial habla alguna, elígela abajo.</p>';
    }
    var semaforo = '<div class="in-semaforo" aria-hidden="true">' + ['rojo', 'ambar', 'verde'].map(function (t) {
      return '<span class="in-luz in-luz-' + t + (t === tipo ? ' on' : '') + '"></span>';
    }).join('') + '</div>';
    var medidor = r.pct === null ? '' :
      '<div class="in-medidor" role="img" aria-label="Las cifras se sostienen ' + r.pct + ' de 100">' +
        '<div class="in-med-barra in-med-inv"><span class="in-med-marca" data-pct="' + r.pct + '" style="left:0%"></span></div>' +
        '<div class="in-med-esc in-med-zonas3" aria-hidden="true"><span style="left:20%">No se sostienen</span><span style="left:55%">A medias</span><span style="left:85%">Se sostienen</span></div>' +
      '</div>';
    var filtro = function (t, k, et) { return k ? '<button type="button" class="in-pill in-pill-' + t + ' in-filtra" data-f="' + t + '" aria-pressed="false">' + k + ' ' + et + '</button>' : ''; };
    var cuenta = r.n ? '<div class="in-cuentas" role="group" aria-label="Filtra las cifras por resultado">' +
      filtro('verde', r.verde, r.verde === 1 ? 'coincide' : 'coinciden') +
      filtro('ambar', r.ambar, r.ambar === 1 ? 'se acerca' : 'se acercan') +
      filtro('rojo', r.rojo, r.rojo === 1 ? 'no coincide' : 'no coinciden') +
      (r.sin ? '<span class="in-pill in-pill-gris">' + r.sin + ' sin contrastar</span>' : '') +
      (r.dolar ? '<span class="in-pill in-pill-gris">' + r.dolar + ' en dólares</span>' : '') + '</div>' : '';
    var just = contr.map(function (c, k) { return justificacion(c, ext, k); }).join('');
    var sinHtml = sin.length && tema ? '<details class="in-sin"' + (r.n ? '' : ' open') + '><summary>Cifras sin contrastar (' + sin.length + ')</summary>' +
      '<p class="in-txt">No tenemos documento de lo que miden, o no supimos de qué hablan. No cuentan en el veredicto. Si sabes de qué cifra oficial habla alguna, elígela y entra al veredicto.</p><ul>' +
      sin.map(function (c) { return '<li>' + oracionMarcada(ext, c) + selector(c, 'Contrastarla con') + '</li>'; }).join('') + '</ul></details>' : '';
    var dolHtml = dol.length && tema ? '<details class="in-sin"><summary>Cifras en dólares (' + dol.length + ')</summary><p class="in-txt">Nuestro catálogo está en pesos; convertirlas exigiría un tipo de cambio que la nota no siempre dice.</p><ul>' +
      dol.map(function (c) { return '<li>' + oracionMarcada(ext, c) + '</li>'; }).join('') + '</ul></details>' : '';
    var temas = rel.temas.length && tema ? '<section class="in-temas"><h3 class="in-sub">Lo que tenemos sobre este tema</h3><ul>' +
      rel.temas.map(function (x) { return '<li><a href="' + esc(x.h) + '"><small>' + esc(x.s) + '</small><span>' + esc(x.t) + ' <span aria-hidden="true">→</span></span></a></li>'; }).join('') + '</ul></section>' : '';
    cont.innerHTML =
      '<article class="in-dictamen">' + dictamenCab() +
      '<div class="in-ver in-v-' + tipo + '">' +
        '<div class="in-v-cab">' + semaforo + '<div>' + cab + '</div></div>' +
        medidor + cuenta +
        (r.n ? '<p class="in-v-porque">De ' + enN(r.n, 'cifra que pudimos', 'cifras que pudimos') + ' poner junto a su documento: ' +
          [r.verde ? enN(r.verde, 'coincide', 'coinciden') : '', r.ambar ? enN(r.ambar, 'se acerca', 'se acercan') : '', r.rojo ? enN(r.rojo, 'no coincide', 'no coinciden') : ''].filter(Boolean).join(', ') +
          '. Cada una que coincide vale 1; la que se acerca, ½; la que no coincide, 0. El resultado es el promedio sobre 100 ' + chip('derivado') + '.</p>' : '') +
      '</div>' +
      (just ? '<h3 class="in-sub">Por qué, cifra por cifra</h3><ol class="in-justs" id="inJusts">' + just + '</ol>' : '') +
      sinHtml + dolHtml + temas + dictamenPie() + '</article>' +
      '<div class="in-acciones">' +
        '<button type="button" class="in-boton" id="inCopiar"><span aria-hidden="true">📋</span> Copiar el veredicto</button>' +
        '<button type="button" class="in-boton in-sec" id="inOtra"><span aria-hidden="true">↺</span> Verificar otra nota</button>' +
      '</div>' +
      '<p class="in-copiado" id="inCopiado" role="status"></p>';
    var revisa = $('inRevisa');
    if (revisa) {
      revisa.hidden = !r.n;
      [].forEach.call(revisa.querySelectorAll('.in-tips li'), function (li) { li.classList.toggle('in-tip-on', !!r.tips[li.getAttribute('data-tip')]); });
      revisa.open = Object.keys(r.tips).length > 0;
    }
    var marca = cont.querySelector('.in-med-marca');
    if (marca) requestAnimationFrame(function () { requestAnimationFrame(function () { marca.style.left = marca.getAttribute('data-pct') + '%'; }); });
    $('inCopiar').addEventListener('click', function () { copiar(textoVeredicto(n, ext, r)); });
    $('inOtra').addEventListener('click', otra);
    firma(n, ext, r);
    $('inResultado').hidden = false;
    return ext;
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
    if (r.sin && r.n) L.push('Cifras sin contrastar (sin documento en el catálogo): ' + r.sin);
    if (firmado.folio) L.push('Folio ' + firmado.folio + ' · huella SHA-256 ' + firmado.huella + ' · versión ' + selloSitio());
    L.push(LEYENDA);
    L.push('Verifícala tú: ' + (n.liga && n.origen === 'liga' ? location.origin + location.pathname + '?liga=' + encodeURIComponent(n.liga) : location.origin + location.pathname));
    return L.join('\n');
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

  /* ---------- El portal ---------- */
  var url = $('inUrl'), texto = $('inTexto'), urlT = $('inUrlTexto');
  var tabs = { liga: $('inTabLiga'), texto: $('inTabTexto') }, forms = { liga: $('inFormLiga'), texto: $('inFormTexto') };
  function modo(m, enfoca) {
    Object.keys(tabs).forEach(function (k) {
      var on = k === m;
      tabs[k].setAttribute('aria-selected', on ? 'true' : 'false');
      tabs[k].tabIndex = on ? 0 : -1;
      forms[k].hidden = !on;
    });
    if (enfoca) (m === 'liga' ? url : texto).focus();
  }
  Object.keys(tabs).forEach(function (k) {
    tabs[k].addEventListener('click', function () { modo(k, true); });
    tabs[k].addEventListener('keydown', function (ev) {
      if (ev.key === 'ArrowRight' || ev.key === 'ArrowLeft') { var o = k === 'liga' ? 'texto' : 'liga'; modo(o); tabs[o].focus(); ev.preventDefault(); }
    });
  });
  function direccion(n) {
    try {
      history.replaceState(null, '', location.pathname + (n && n.origen === 'liga' && n.liga ? '?liga=' + encodeURIComponent(n.liga) : ''));
    } catch (e) { /* nada */ }
  }
  function muestra(n, baja) {
    nota = n; guarda(n); estado(''); direccion(n);
    cabecera(n); pinta(n);
    if (baja) $('inResultado').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function otra() {
    olvida(); nota = null; direccion(null);
    $('inResultado').hidden = true;
    $('inVeredicto').innerHTML = ''; $('inCabNota').innerHTML = '';
    url.value = ''; texto.value = ''; urlT.value = '';
    modo('liga');
    window.scrollTo({ top: $('inRaiz').offsetTop - 20, behavior: 'smooth' });
    url.focus({ preventScroll: true });
  }
  function leeYMuestra(u) {
    var boton = $('inLeer');
    boton.disabled = true;
    estado('Leyendo la nota de <b>' + esc(dominio(u)) + '</b>… puede tardar unos segundos.', 'in-est-lee');
    leerLiga(u).then(function (n) {
      boton.disabled = false;
      muestra(n, true);
    }, function () {
      boton.disabled = false;
      url.value = u; urlT.value = u;
      modo('texto');
      estado(esc(avisoFallo(u)), 'in-est-mal');
      texto.focus();
    });
  }
  forms.liga.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var u = ligaValida(url.value);
    if (!u) { estado('Esa liga no parece completa: debe empezar con https://', 'in-est-mal'); url.focus(); return; }
    leeYMuestra(u);
  });
  forms.texto.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var t = String(texto.value || '').trim();
    if (t.length < 40) { estado('Pega el texto de la nota: con unas cuantas palabras no alcanzamos a encontrar sus cifras.', 'in-est-mal'); texto.focus(); return; }
    var primera = t.split(/\n/)[0].trim();
    muestra({ origen: 'texto', liga: ligaValida(urlT.value), titulo: primera.length <= 160 ? primera : '', texto: t.slice(0, 80000), aj: {} }, true);
  });
  /* Reempatar una cifra o filtrar por resultado, ahí mismo. */
  $('inVeredicto').addEventListener('change', function (ev) {
    var s = ev.target;
    if (!s.classList || !s.classList.contains('in-empate')) return;
    var i = s.getAttribute('data-i');
    nota.aj = nota.aj || {}; nota.aj[i] = s.value; guarda(nota);
    pinta(nota);
    var li = $('inVeredicto').querySelector('select[data-i="' + i + '"]');
    var tarjeta = li && li.closest('li');
    if (tarjeta) { tarjeta.scrollIntoView({ block: 'center' }); li.focus({ preventScroll: true }); }
  });
  $('inVeredicto').addEventListener('click', function (ev) {
    var b = ev.target.closest && ev.target.closest('.in-filtra');
    if (!b) return;
    var on = b.getAttribute('aria-pressed') !== 'true';
    [].forEach.call($('inVeredicto').querySelectorAll('.in-filtra'), function (x) { x.setAttribute('aria-pressed', x === b && on ? 'true' : 'false'); });
    [].forEach.call($('inVeredicto').querySelectorAll('.in-just'), function (li) { li.hidden = on && li.getAttribute('data-tipo') !== b.getAttribute('data-f'); });
  });

  /* Al abrir: una liga compartida (?liga=) se lee de nuevo; si no, se
     retoma la nota que dejaste en revisión. */
  var q = ligaValida(new URLSearchParams(location.search).get('liga'));
  if (q && (!nota || nota.liga !== q || nota.origen !== 'liga' || !nota.texto)) {
    url.value = q;
    leeYMuestra(q);
  } else if (nota && nota.texto) {
    if (nota.origen === 'liga') url.value = nota.liga;
    else { modo('texto'); texto.value = nota.texto; urlT.value = nota.liga || ''; }
    muestra(nota, false);
  }
})();
