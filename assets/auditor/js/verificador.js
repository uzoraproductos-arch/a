/* Auditavisión · El verificador de cifras (23-10-2026). Es el motor de
   «Contrasta una nota» (insp-nota-lee.js) apartado para que también lo use
   «Pregúntale al Auditor» (asistente-charla.js): encuentra las cantidades en
   pesos de un texto, las empata con el catálogo de cifras oficiales por
   palabras (D.cat, cada renglón con sus claves «k») y juzga cada una contra
   su documento. Aquí no se escribe ninguna cifra.

   Reglas: solo se contrasta una cifra si la oración nombra a la entidad y
   al concepto de un renglón del catálogo. Lo que no empata queda «sin
   contrastar» y no cuenta como falso. Nada se estima: una cifra oficial
   pendiente no sirve de regla. */
(function () {
  'use strict';

  window.AuditorVerifica = function (D) {
  var porId = {};
  D.cat.forEach(function (o) { porId[o.id] = o; });

  /* Minúsculas y sin acentos, sin cambiar el largo: así una posición en el
     texto normalizado es la misma en el original. */
  function plano(t) {
    return String(t || '').toLowerCase().replace(/[áàäâ]/g, 'a').replace(/[éèëê]/g, 'e').replace(/[íìïî]/g, 'i')
      .replace(/[óòöô]/g, 'o').replace(/[úùüû]/g, 'u').replace(/ñ/g, 'n');
  }
  function fmt(mdp) { return (mdp < 0 ? '−' : '') + '$' + Math.abs(Number(mdp)).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp'; }
  function pctTx(p) { return (p >= 0 ? '+' : '−') + Math.abs(p).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' %'; }

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
    /* Un redondeo solo coincide si no esconde más de 10 % (23-10-2026: «2 billones» por 1.59 es redondeo, pero engaña). */
    if ((Math.abs(dif) <= c.tol && Math.abs(pct) <= 10) || Math.abs(pct) <= 1) {
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
    } else if (Math.abs(dif) <= c.tol) {
      v.tipo = 'ambar'; v.tit = 'Redondeo demasiado grueso';
      v.porque = 'La nota redondea ' + fmt(ref) + ' a «' + c.bruto + '»: el redondeo es válido, pero se aleja ' + pctTx(pct) + ' del documento.';
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

  return { analiza: analiza, juzga: juzga, conjunto: conjunto, relevancia: relevancia, porId: porId, plano: plano, fmt: fmt };
  };
})();
