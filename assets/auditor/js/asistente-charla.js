/* Auditavisión · «Pregúntale al Auditor» › la conversación (pedido del autor,
   23-10-2026: «que funcione literalmente como un chat… que responda a
   cualquier pregunta sobre márgenes, porcentajes, estados, municipios», en
   lenguaje coloquial). Entiende la pregunta como se habla, contesta en corto
   y deja la ficha técnica para quien la pida con su botón (asistente.js).
   No escribe cifras propias: toma las de window.AUDITOR_BASE.dat (las arma
   herramientas/asistente.py) y las de window.AUDIT_MUNICIPIOS (INEGI). Lo
   que calcula (lugares, diferencias, porcentajes, sumas) lo marca como
   derivado y dice la operación. */
(function () {
  'use strict';

  window.AuditorCharla = function (B, U) {
    var D = B.dat || {}, M = D.met || {}, EDO = D.edo || [], MU = window.AUDIT_MUNICIPIOS || null;
    var esc = U.esc, norm = U.norm;

    /* ---------- Formato ---------- */
    function n(v, d) { return Number(v).toLocaleString('es-MX', { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 }); }
    function mdp(v) { if (v === 0) return '$0'; return Math.abs(v) >= 1e6 ? '$' + n(v / 1e6, 2) + ' billones' : '$' + n(v, 1) + ' millones'; }
    function fmt(v, u) {
      if (v == null) return '';
      if (u === 'mdp') return mdp(v);
      if (u === 'pesos') return '$' + n(v);
      if (u === 'pesos2') return '$' + n(v, 2);
      if (u === 'pct') return n(v, 1) + ' %';
      if (u === 'ent') return n(v);
      if (u === 'gente') return n(v) + ' personas';
      if (u === 'pib') return n(v, 1) + ' % del PIB';
      if (u === 'pp') return (v > 0 ? '+' : '') + n(v, 1) + ' puntos del PIB';
      return String(v);
    }
    /* Pesos sueltos (la calculadora y los municipios): la escala que se lee. */
    function grande(v, peso) {
      var s = peso ? '$' : '', a = Math.abs(v);
      var h = function (x) { return x.toLocaleString('es-MX', { maximumFractionDigits: 2 }); };
      if (a >= 1e12) return s + h(v / 1e12) + ' billones';
      if (a >= 1e9) return s + h(v / 1e9) + ' mil millones';
      if (a >= 1e6) return s + h(v / 1e6) + ' millones';
      return s + h(v);
    }
    function chip(e, p) { return '<span class="est-chip est-' + esc(e) + '"' + (p ? ' data-pend="' + esc(p) + '"' : '') + '>' + esc(e) + '</span>'; }
    function liga(f) { return f && f.url ? '<a href="' + esc(f.url) + '" target="_blank" rel="noopener noreferrer">' + esc(f.tx) + ' ↗</a>' : esc(f && f.tx || ''); }
    /* «De dónde sale»: los chips a la vista y las fuentes a un toque. */
    function deDonde(lista) {
      var est = {}, vistos = {}, li = [];
      lista.forEach(function (x) {
        if (!x) return;
        est[x.e] = 1;
        var k = x.que + '|' + (x.fu && x.fu.tx);
        if (vistos[k]) return;
        vistos[k] = 1;
        li.push('<li>' + chip(x.e, x.p) + ' <b>' + esc(x.que) + '.</b> ' + (x.op ? 'Cuenta: ' + esc(x.op) + '. ' : '') + (x.fu && x.fu.tx ? liga(x.fu) : '') + '</li>');
      });
      var prim = lista.filter(function (x) { return x && x.fu && x.fu.tx; }), nf = {};
      prim.forEach(function (x) { nf[x.fu.tx] = 1; });
      var cuantas = Object.keys(nf).length, tx0 = prim.length ? prim[0].fu.tx.split(' (')[0] : '';
      if (tx0.length > 60) tx0 = tx0.slice(0, 58).replace(/[\s,;:]+\S*$/, '') + '…';
      return '<details class="pa-dedonde"><summary><span>📎 ' + (tx0 ? 'Fuente: ' + esc(tx0) + (cuantas > 1 ? ' y ' + (cuantas - 1) + ' más' : '') : 'De dónde sale') + '</span> ' +
        ['oficial', 'derivado', 'pendiente'].filter(function (e) { return est[e]; }).map(function (e) { return chip(e); }).join(' ') +
        '</summary><ul>' + li.join('') + '</ul></details>';
    }
    function texto(h) { var d = document.createElement('div'); d.innerHTML = String(h).replace(/<li[^>]*>/g, '$& • ').replace(/<\/(li|p|ol|ul|tr|td|th)>/g, '$& '); return d.textContent.replace(/\s+/g, ' ').trim(); }
    function corto(t, max) {
      t = String(t || '').trim();
      max = max || 280;
      if (t.length <= max) return t;
      var frases = t.split(/(?<=[.!?»])\s+(?=[A-ZÁÉÍÓÚÑ¿¡«(])/), out = '';
      for (var i = 0; i < frases.length; i++) {
        if ((out + ' ' + frases[i]).length > max && out) break;
        out += (out ? ' ' : '') + frases[i];
      }
      return out.length > max + 80 ? out.slice(0, max).replace(/\s\S*$/, '') + '…' : out.trim();
    }
    function plano(s) { return ' ' + norm(s).replace(/[^a-z0-9ñ]+/g, ' ').trim() + ' '; }

    /* ---------- Los estados: nombres, siglas y apodos ---------- */
    var ALIAS = [], porA = {};
    EDO.forEach(function (e) { porA[e.a] = e; if (norm(e.n) !== 'estado de mexico') ALIAS.push([plano(e.n).trim(), e.a]); });
    [['cdmx', 'CDMX'], ['df', 'CDMX'], ['d f', 'CDMX'], ['distrito federal', 'CDMX'], ['chilangolandia', 'CDMX'], ['chilango', 'CDMX'], ['chilangos', 'CDMX'], ['capitalino', 'CDMX'], ['capitalinos', 'CDMX'],
      ['estado de mexico', 'MÉX'], ['edomex', 'MÉX'], ['edo mex', 'MÉX'], ['edo de mexico', 'MÉX'], ['mexiquense', 'MÉX'],
      ['nl', 'NL'], ['bcs', 'BCS'], ['baja sur', 'BCS'], ['qroo', 'QROO'], ['q roo', 'QROO'], ['slp', 'SLP'], ['san luis', 'SLP'], ['potosi', 'SLP'],
      ['coahuila de zaragoza', 'COAH'], ['michoacan de ocampo', 'MICH'], ['veracruz de ignacio de la llave', 'VER'], ['jalisciense', 'JAL'],
      ['regio', 'NL'], ['regios', 'NL'], ['tapatio', 'JAL'], ['yucateco', 'YUC'], ['oaxaqueño', 'OAX'], ['poblano', 'PUE'], ['chiapaneco', 'CHIS'],
      ['sonorense', 'SON'], ['sinaloense', 'SIN'], ['veracruzano', 'VER'], ['guanajuatense', 'GTO'], ['queretano', 'QRO'], ['hidalguense', 'HGO'],
      ['guerrerense', 'GRO'], ['tabasqueño', 'TAB'], ['tamaulipeco', 'TAM'], ['zacatecano', 'ZAC'], ['duranguense', 'DGO'], ['chihuahuense', 'CHIH'],
      ['coahuilense', 'COAH'], ['michoacano', 'MICH'], ['campechano', 'CAM'], ['colimense', 'COL'], ['nayarita', 'NAY'], ['tlaxcalteca', 'TLAX'],
      ['morelense', 'MOR'], ['ags', 'AGS'], ['gto', 'GTO'], ['qro', 'QRO'], ['chih', 'CHIH'], ['tamps', 'TAM'], ['yuc', 'YUC'], ['zac', 'ZAC'], ['oax', 'OAX'],
      ['chis', 'CHIS'], ['mich', 'MICH'], ['hgo', 'HGO'], ['dgo', 'DGO'], ['coah', 'COAH'], ['tlax', 'TLAX'], ['jal', 'JAL'], ['pue', 'PUE'], ['nay', 'NAY']
    ].forEach(function (x) { if (porA[x[1]]) ALIAS.push([norm(x[0]), x[1]]); });
    ALIAS.sort(function (a, b) { return b[0].length - a[0].length; });
    /* Devuelve los estados en el orden en que aparecen y el texto sin ellos. */
    function estados(t) {
      var hall = [];
      ALIAS.forEach(function (x) {
        var i = t.indexOf(' ' + x[0] + ' ');
        while (i >= 0) {
          if (!hall.some(function (h) { return h.a === x[1]; })) hall.push({ a: x[1], i: i, txt: x[0] });
          t = t.slice(0, i) + ' ' + Array(x[0].length + 1).join('#') + ' ' + t.slice(i + x[0].length + 2);
          i = t.indexOf(' ' + x[0] + ' ');
        }
      });
      hall.sort(function (a, b) { return a.i - b.i; });
      return { e: hall.map(function (h) { return porA[h.a]; }), resto: t, txt: hall.map(function (h) { return h.txt; }) };
    }

    /* ---------- Los municipios (INEGI, EFIPEM 2024) ---------- */
    var MUN = [], MIDX = {}, MCAMPO = {};
    var MUN_NOM = { ing: 'ingresos totales de 2024', part: 'participaciones federales (Ramo 28)', aport: 'aportaciones federales (Ramo 33)',
      fortamun: 'FORTAMUN, la aportación para fortalecer al municipio', fismdf: 'FAIS municipal, para obras en zonas de pobreza',
      predial: 'lo que cobró de predial', propios: 'ingresos propios, lo que cobró por su cuenta', egr: 'egresos de 2024',
      dep: 'dependencia de la Federación' };
    /* Nombres de municipio que también son palabras comunes: solo cuentan si se dice «municipio». */
    var COMUN = ' centro reforma progreso victoria solidaridad libres union la union paz la paz general nacional independencia hidalgo morelos guerrero juarez allende zaragoza madero obregon mexico tabasco colima durango aguascalientes campeche chihuahua oaxaca puebla queretaro tlaxcala zacatecas tepic jalisco nuevo nombre jesus maria santiago san pedro trinidad libertad ';
    /* Nombres cortos que la gente dice sin su apellido («Tula» por Tula de Allende). */
    var MUN_CORTO = { tula: 1 };
    if (MU && MU.ent) {
      (MU.campos || []).forEach(function (c, i) { MCAMPO[c] = i - 1; });
      Object.keys(MU.ent).forEach(function (ab) {
        var est = porA[ab] || porA[ab.replace('É', 'E')] || { n: ab, a: ab };
        MU.ent[ab].lista.forEach(function (r) {
          var m = { cve: MU.ent[ab].cve + r[0], n: r[1], a: est.a, en: est.n, v: r.length > 2 ? r.slice(1) : null };
          MUN.push(m);
          var k = plano(r[1]).trim(), ks = [k];
          if (/ de /.test(k) && (k.split(' de ')[0].length >= 6 || MUN_CORTO[k.split(' de ')[0]])) ks.push(k.split(' de ')[0]);
          if (k === 'juarez' && ab === 'CHIH') ks.push('ciudad juarez');
          ks.forEach(function (x) { (MIDX[x] = MIDX[x] || []).push(m); });
        });
      });
    }
    function mv(m, k) {
      if (!m.v) return null;
      if (k === 'dep') return m.v[MCAMPO.ing] ? (m.v[MCAMPO.part] + m.v[MCAMPO.aport]) / m.v[MCAMPO.ing] * 100 : null;
      return m.v[MCAMPO[k]];
    }
    function municipio(t, quiere, edos, orden) {
      var ws = t.trim().split(/\s+/), mejor = null;
      for (var l = Math.min(6, ws.length); l >= 1 && !mejor; l--) {
        for (var i = 0; i + l <= ws.length; i++) {
          var k = ws.slice(i, i + l).join(' ');
          if (!MIDX[k] || k.length < 4) continue;
          if (!quiere && (COMUN.indexOf(' ' + k.replace(/^(la|el|los|las|san|santa) /, '') + ' ') >= 0 || k.length < 5 && !MUN_CORTO[k])) continue;
          mejor = k;
          break;
        }
      }
      /* «municipio de Durango»: el estado se llevó la palabra; se busca el municipio que se llama como él. */
      if (!mejor && quiere && edos.length && !orden) {
        var c = MIDX[plano(edos[0].n).trim()] || MIDX[plano(edos[0].n.replace(/^Estado de /, '')).trim()];
        if (c) return { m: c.filter(function (x) { return x.a === edos[0].a; })[0] || c[0], otros: [] };
      }
      if (!mejor) return null;
      var cand = MIDX[mejor];
      var enEdo = edos.length ? cand.filter(function (x) { return edos.some(function (e) { return e.a === x.a; }); }) : [];
      var lista = (enEdo.length ? enEdo : cand).slice().sort(function (a, b) { return (mv(b, 'ing') || 0) - (mv(a, 'ing') || 0); });
      return { m: lista[0], otros: enEdo.length ? [] : cand.filter(function (x) { return x !== lista[0]; }) };
    }

    /* ---------- Qué se pregunta ---------- */
    var MET_EDO = [
      ['radar', /de cada (100|cien)|radar|bandera roja|proporcion a lo auditado/],
      ['sem', /semaforo|alerta/],
      ['ild', /libre disposicion|ingresos de libre/],
      ['aud', /cuantas auditorias|numero de auditorias|auditorias (le )?(hizo|hicieron|practic)/],
      ['asf', /aclarar|\basf\b|auditoria superior|robo|robaron|roban|transa|desfalc|desvi|chingaron|clavaron|embols|volaron|moche|corrup|irregular|observ|huec|fiscaliz|perdio|perdieron|desapareci/],
      ['deuda', /deud|debe\b|deben\b|adeud|endeud|prestamo|prestado|credito|empenad/],
      ['dep', /depend|mantenid|vive de|viven de|colgad|autonom|de la federacion vive/],
      ['propia', /recaud|cobra por su cuenta|sus propios|ingresos propios|impuestos propios|cobran ellos|genera(n)? (su|sus)/],
      ['r28', /participacion|ramo 28/],
      ['r33', /aportacion|ramo 33/],
      ['pob', /poblacion|habitantes tiene|cuanta gente|cuantas personas|cuantos habitantes|cuantos viven/],
      ['gasto', /recib|le (dan|mandan|llega|llegan|toca|tocan|manda|pasan|da)|les (dan|mandan|llega|toca)|transfer|federaliz|ramos? 28 y 33|presupuesto|cuanto dinero|cuanta (lana|feria)|cuanto (varo|baro)|dinero (le|les)|lana|varo|feria|cuanto tiene/]
    ];
    var MET_MUN = [['predial', /predial/], ['fortamun', /fortamun|fortalecimiento/], ['fismdf', /\bfais\b|fismdf|infraestructura social/],
      ['dep', /depend|mantenid|vive de|colgad|autonom/], ['propios', /propio|recaud|cobra por su cuenta|cobran ellos|genera/],
      ['part', /participacion|ramo 28/], ['aport', /aportacion|ramo 33/], ['egr', /gast|egres/],
      ['ing', /ingres|recib|dinero|presupuesto|lana|varo|feria|tiene|maneja|le (dan|llega|toca)/]];
    function metrica(t, tabla) { for (var i = 0; i < tabla.length; i++) if (tabla[i][1].test(t)) return tabla[i][0]; return ''; }
    var POR_HAB = /por (habitante|persona|cabeza|cabecita)|per ?capita|a cada (quien|persona|habitante|uno)|por cada (habitante|persona)|cada (habitante|persona|mexican[oa])/;
    var MUN_KW = /municipio|alcaldia|ayuntamiento|alcalde|presidente municipal|presidenta municipal|cabildo|predial|fortamun|\bfais\b|fismdf/;
    var RANK = /\b(mas|menos|mayor|menor|top|ranking|primero|primeros|peor|peores|mejor|mejores|ultimo|ultimos|lugar|lugares|maximo|minimo)\b/;
    var TOTAL = /todos los estados|los 32|las 32|en total|total de los estados|juntos|suman|en conjunto|todo el pais|a nivel nacional|nacional/;
    var COMPARA = /compar|\bvs\b|\bversus\b|contra|frente a|diferencia entre|o (el|la) |quien (debe|recibe|tiene|gana) mas|cual (debe|recibe|tiene) mas/;
    var PCT = /porcentaje|que parte|cuanto representa|proporcion|del total|tajada|rebanada|que tanto/;

    /* ---------- Las respuestas sobre estados ---------- */
    function lugar(k, e) {
      var l = EDO.filter(function (x) { return x[k] != null; }).sort(function (a, b) { return b[k] - a[k]; });
      return { l: l.indexOf(e) + 1, de: l.length };
    }
    function fuenteDe(k, e, extra) {
      var m = M[k] || {};
      return { que: extra || (m.n ? m.n.charAt(0).toUpperCase() + m.n.slice(1) : k), e: m.e, fu: m.fu, op: m.op, p: e && m.sin && m.sin.indexOf(e.a) >= 0 ? m.pend : '' };
    }
    var LUGAR = { que: 'Lugar entre los estados', e: 'derivado', op: 'ordenamos de mayor a menor los estados que tienen la cifra' };
    function pendEdo(e, k) {
      var m = M[k];
      return '<p>Ese dato de <b>' + esc(e.n) + '</b> está ' + chip('pendiente', m.pend) + ': la Ciudad de México no figura en la estadística estatal del INEGI, que es de donde sale. ' +
        'En el <a href="pendientes.html">Registro de pendientes</a> está por qué falta y dónde debería estar.</p>';
    }
    function pendFu(e, k) { var f = fuenteDe(k, e); f.e = 'pendiente'; f.op = ''; f.que += ' de ' + e.n; return f; }
    function semTxt(s) {
      var S = { verde: 'endeudamiento sostenible', amarillo: 'endeudamiento en observación', rojo: 'endeudamiento elevado' };
      return S[norm(s)] ? ' (' + S[norm(s)] + ', según la Ley de Disciplina Financiera)' : '';
    }
    function lugarTxt(k, e, palabra) {
      var L = lugar(k, e);
      return L.l ? ' Es el lugar <b>' + L.l + ' de ' + L.de + '</b> ' + palabra + '.' : '';
    }

    function edoMet(e, k, porHab) {
      var m = M[k] || {}, v = e[k], fu = [fuenteDe(k, e)], h = '';
      if (v == null && k !== 'sem') return { html: pendEdo(e, k), fu: [pendFu(e, k)], ci: [], tit: e.n + ': ' + m.n };
      if (porHab && (k === 'deuda' || k === 'asf' || k === 'propia' || k === 'r28' || k === 'r33')) {
        var ph = v * 1e6 / e.pob;
        var todos = EDO.filter(function (x) { return x[k] != null && x.pob; }).map(function (x) { return { e: x, v: x[k] * 1e6 / x.pob }; }).sort(function (a, b) { return b.v - a.v; });
        var lu = todos.map(function (x) { return x.e; }).indexOf(e) + 1;
        h = '<p>Si repartimos ' + esc(m.n) + ' de <b>' + esc(e.n) + '</b> entre sus habitantes, salen <b>$' + n(ph) + ' por persona</b>.' +
          (lu ? ' Es el lugar <b>' + lu + ' de ' + todos.length + '</b> de mayor a menor.' : '') + '</p>';
        fu.push(fuenteDe('pob', e), { que: 'Por habitante', e: 'derivado', op: m.n + ' (' + fmt(v, m.u) + ') ÷ ' + n(e.pob) + ' habitantes' }, LUGAR);
        return { html: h, fu: fu, val: { v: ph, u: 'pesos' }, ci: [{ v: '$' + n(ph), etq: m.n + ' por habitante', e: 'derivado', op: fmt(v, m.u) + ' ÷ ' + n(e.pob) + ' habitantes' }], tit: e.n + ': ' + m.n + ' por habitante' };
      }
      var V = '<b>' + fmt(v, m.u) + '</b>';
      if (k === 'deuda' && v === 0) {
        h = '<p><b>' + esc(e.n) + '</b> no tiene deuda registrada en el Sistema de Alertas de Hacienda: debe <b>$0</b>. Es el único caso así entre los 32.</p>';
        if (EDO.filter(function (x) { return x.deuda === 0; }).length > 1) h = h.replace(' Es el único caso así entre los 32.', '');
      } else if (k === 'deuda') {
        h = '<p><b>' + esc(e.n) + '</b> debe ' + V + '.' + (e.ild != null ? ' Eso es el <b>' + fmt(e.ild, 'pct') + '</b> de sus ingresos de libre disposición (el dinero que puede gastar en lo que quiera)' : '') +
          (e.sem ? (e.ild != null ? ', y' : '') + ' Hacienda lo tiene en semáforo <b>' + esc(e.sem.toLowerCase()) + '</b>' + semTxt(e.sem) : '') + '.' + lugarTxt('deuda', e, 'entre los que más deben') + '</p>';
        if (e.ild != null) fu.push(fuenteDe('ild', e));
        fu.push(LUGAR);
      } else if (k === 'ild') {
        h = '<p>La deuda de <b>' + esc(e.n) + '</b> equivale al ' + V + ' de sus ingresos de libre disposición, es decir, del dinero que puede gastar en lo que quiera. En pesos, debe <b>' + fmt(e.deuda, 'mdp') + '</b>.' + lugarTxt('ild', e, 'de mayor a menor') + '</p>';
        fu.push(fuenteDe('deuda', e), LUGAR);
      } else if (k === 'sem') {
        h = '<p>Hacienda tiene a <b>' + esc(e.n) + '</b> en semáforo <b>' + esc((e.sem || '').toLowerCase()) + '</b>' + semTxt(e.sem) + '. Debe <b>' + fmt(e.deuda, 'mdp') + '</b>' + (e.ild != null ? ', el ' + fmt(e.ild, 'pct') + ' de sus ingresos de libre disposición' : '') + '.</p>';
        fu = [fuenteDe('deuda', e, 'Semáforo y deuda')];
      } else if (k === 'asf') {
        h = '<p>La Auditoría Superior de la Federación dejó a <b>' + esc(e.n) + '</b> ' + V + ' por aclarar del dinero federal de 2024' + (e.aud != null ? ', en <b>' + n(e.aud) + ' auditorías</b>' : '') + '.' + lugarTxt('asf', e, 'entre los que más tienen por aclarar') + '</p>' +
          '<p class="pa-ojo">Ojo: no es un robo comprobado. Es dinero que, cuando cerró la auditoría, no tenía los papeles que justificaran en qué se gastó.</p>';
        if (e.radar != null) { h += '<p>En proporción: de cada $100 que revisó la ASF, quedaron <b>$' + n(e.radar, 2) + '</b> por aclarar (el promedio nacional es $' + n(M.radar.prom, 2) + ').</p>'; fu.push(fuenteDe('radar', e)); }
        fu.push(LUGAR);
      } else if (k === 'aud') {
        h = '<p>A <b>' + esc(e.n) + '</b> la ASF le practicó ' + V + ' auditorías por el dinero federal de 2024, y dejó <b>' + fmt(e.asf, 'mdp') + '</b> por aclarar.</p>';
        fu.push(fuenteDe('asf', e));
      } else if (k === 'radar') {
        h = '<p>De cada $100 que la ASF revisó en <b>' + esc(e.n) + '</b>, quedaron <b>$' + n(v, 2) + '</b> por aclarar. El promedio nacional es de $' + n(M.radar.prom, 2) + '.' + lugarTxt('radar', e, 'de mayor a menor') + '</p>';
        fu.push(LUGAR);
      } else if (k === 'gasto') {
        h = '<p>En 2026, <b>' + esc(e.n) + '</b> recibe de la Federación ' + V + ' por las dos vías grandes: <b>' + fmt(e.r28, 'mdp') + '</b> de participaciones (Ramo 28, lo gasta en lo que decida) y <b>' + fmt(e.r33, 'mdp') + '</b> de aportaciones (Ramo 33, llega con destino fijado por ley). ' +
          'Por habitante son <b>' + fmt(e.pc, 'pesos') + '</b>.' + lugarTxt('gasto', e, 'entre los que más reciben') + '</p>';
        fu.push(fuenteDe('r28', e), fuenteDe('r33', e), fuenteDe('pc', e), LUGAR);
      } else if (k === 'r28') {
        h = '<p>Las participaciones (Ramo 28) de <b>' + esc(e.n) + '</b> para 2026 son ' + V + '. Es dinero que el estado gasta en lo que decida.' + lugarTxt('r28', e, 'de mayor a menor') + '</p>';
        fu.push(LUGAR);
      } else if (k === 'r33') {
        h = '<p>Las aportaciones (Ramo 33) de <b>' + esc(e.n) + '</b> para 2026 son ' + V + '. Llegan con destino fijado por la Ley de Coordinación Fiscal: educación, salud, infraestructura social, seguridad y más.' + lugarTxt('r33', e, 'de mayor a menor') + '</p>';
        fu.push(LUGAR);
      } else if (k === 'pc') {
        h = '<p>A cada habitante de <b>' + esc(e.n) + '</b> le tocan ' + V + ' de los Ramos 28 y 33 en 2026.' + lugarTxt('pc', e, 'de mayor a menor') + '</p>';
        fu.push(LUGAR);
      } else if (k === 'dep') {
        h = '<p>De cada $100 que ingresó el gobierno de <b>' + esc(e.n) + '</b> en 2024 (sin contar deuda), <b>$' + n(v, 1) + '</b> llegaron de la Federación. Los otros $' + n(100 - v, 1) + ' salieron de lo que cobra por su cuenta y de otras fuentes, como los convenios.' + lugarTxt('dep', e, 'entre los más dependientes') + '</p>';
        fu.push(LUGAR);
      } else if (k === 'propia') {
        h = '<p>En 2024, <b>' + esc(e.n) + '</b> recaudó por su cuenta ' + V + ': impuestos estatales, derechos, cuotas y otros cobros.' + lugarTxt('propia', e, 'de mayor a menor') + '</p>';
        fu.push(LUGAR);
      } else if (k === 'pob') {
        h = '<p><b>' + esc(e.n) + '</b> tiene ' + V + ' a mitad de 2026, según el CONAPO.' + lugarTxt('pob', e, 'de mayor a menor') + '</p>';
        fu.push(LUGAR);
      }
      return { html: h, fu: fu, val: k === 'sem' ? null : { v: v, u: m.u }, ci: [{ v: fmt(v, m.u) || e.sem, etq: m.n, e: m.e, op: m.op }], tit: e.n + ': ' + m.n };
    }

    function edoResumen(e) {
      var li = [], fu = [];
      if (e.deuda != null) { li.push('Debe <b>' + fmt(e.deuda, 'mdp') + '</b>' + (e.sem ? ', en semáforo <b>' + esc(e.sem.toLowerCase()) + '</b> de Hacienda' : '') + '.'); fu.push(fuenteDe('deuda', e)); }
      li.push('Recibe <b>' + fmt(e.gasto, 'mdp') + '</b> de la Federación en 2026 por los Ramos 28 y 33: <b>' + fmt(e.pc, 'pesos') + '</b> por habitante.'); fu.push(fuenteDe('gasto', e), fuenteDe('pc', e));
      if (e.dep != null) { li.push('De cada $100 que ingresó en 2024, <b>$' + n(e.dep, 1) + '</b> vinieron de la Federación.'); fu.push(fuenteDe('dep', e)); }
      if (e.asf != null) { li.push('La ASF le dejó <b>' + fmt(e.asf, 'mdp') + '</b> por aclarar de la Cuenta Pública 2024.'); fu.push(fuenteDe('asf', e)); }
      return { html: '<p><b>' + esc(e.n) + '</b>, en corto:</p><ul class="pa-lista">' + li.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>', fu: fu };
    }

    /* Cómo se dice cada cifra en «el estado con más…». */
    var RK = { deuda: 'deuda', ild: 'deuda frente a sus ingresos de libre disposición', asf: 'dinero por aclarar ante la ASF', aud: 'auditorías de la ASF',
      radar: 'dinero por aclarar de cada $100 revisados', gasto: 'dinero federal en 2026 (Ramos 28 y 33)', r28: 'participaciones', r33: 'aportaciones',
      pc: 'dinero federal por habitante', dep: 'dependencia de la Federación', propia: 'recaudación propia', pob: 'población' };
    var RKM = { ing: 'ingresos', part: 'participaciones', aport: 'aportaciones', fortamun: 'FORTAMUN', fismdf: 'FAIS municipal', predial: 'cobro de predial',
      propios: 'ingresos propios', egr: 'egresos', dep: 'dependencia de la Federación' };
    function ranking(k, dir, cuantos, porHab) {
      var m = M[k], rk = RK[k] || m.n;
      var val = function (x) { return porHab && k !== 'pc' ? (x[k] != null && x.pob ? x[k] * 1e6 / x.pob : null) : x[k]; };
      var l = EDO.filter(function (x) { return val(x) != null; }).sort(function (a, b) { return dir === 'min' ? val(a) - val(b) : val(b) - val(a); });
      var top = l.slice(0, cuantos), u = porHab && k !== 'pc' ? 'pesos' : m.u;
      var tit = (dir === 'min' ? 'Los que menos' : 'Los que más') + ': ' + m.n + (porHab && k !== 'pc' ? ' por habitante' : '');
      var h = cuantos === 1 ?
        '<p>El estado con ' + (dir === 'min' ? 'menos' : 'más') + ' ' + esc(rk) + (porHab && k !== 'pc' ? ' por habitante' : '') + ' es <b>' + esc(top[0].n) + '</b>, con <b>' + fmt(val(top[0]), u) + '</b>.</p>' +
        '<p>Le siguen: ' + l.slice(1, 5).map(function (x) { return esc(x.n) + ' (' + fmt(val(x), u) + ')'; }).join(', ') + '.</p>' :
        '<p>Los ' + cuantos + ' estados con ' + (dir === 'min' ? 'menos' : 'más') + ' ' + esc(rk) + (porHab && k !== 'pc' ? ' por habitante' : '') + ':</p><ol class="pa-lista">' + top.map(function (x) { return '<li><b>' + esc(x.n) + '</b>: ' + fmt(val(x), u) + '</li>'; }).join('') + '</ol>';
      var fu = [fuenteDe(k), LUGAR];
      if (m.suma && !porHab && !(cuantos === 1 && dir === 'min')) {
        var tot = l.reduce(function (s, x) { return s + x[k]; }, 0), parte = top.reduce(function (s, x) { return s + x[k]; }, 0);
        h += '<p>Entre los ' + l.length + ' suman <b>' + fmt(tot, m.u) + '</b>; ' + (cuantos === 1 ? esc(top[0].n) + ' solo' : 'estos ' + cuantos) + ' concentra' + (cuantos === 1 ? '' : 'n') + ' el <b>' + n(parte / tot * 100, 1) + ' %</b>.</p>';
        fu.push({ que: 'Suma y porcentaje', e: 'derivado', op: 'suma de los estados con cifra; porcentaje = parte ÷ suma × 100' });
      }
      if (porHab && k !== 'pc') fu.push(fuenteDe('pob'), { que: 'Por habitante', e: 'derivado', op: 'cifra del estado ÷ su población' });
      if (m.sin && m.sin.length) h += '<p class="pa-chico">Sin ' + m.sin.map(function (a) { return porA[a] ? porA[a].n : a; }).join(', ') + ': su dato está ' + chip('pendiente', m.pend) + '.</p>';
      return { html: h, fu: fu, tit: tit, ci: top.map(function (x) { return { v: fmt(val(x), u), etq: x.n, e: porHab && k !== 'pc' ? 'derivado' : m.e }; }) };
    }

    function compara(es, k) {
      var cols = es.slice(0, 4);
      if (!k) {
        var ks = ['deuda', 'gasto', 'pc', 'dep', 'asf'];
        var h = '<p>Así se ven lado a lado:</p><div class="pa-tabla"><table><thead><tr><th></th>' + cols.map(function (e) { return '<th>' + esc(e.n) + '</th>'; }).join('') + '</tr></thead><tbody>' +
          ks.map(function (k) {
            return '<tr><th>' + esc(CORTO[k]) + '</th>' + cols.map(function (e) { return '<td>' + (e[k] == null ? chip('pendiente', M[k].pend) : fmt(e[k], M[k].u)) + '</td>'; }).join('') + '</tr>';
          }).join('') + '</tbody></table></div>';
        return { html: h, fu: ks.map(function (k) { return fuenteDe(k); }), tit: 'Comparación: ' + cols.map(function (e) { return e.n; }).join(' y '),
          ci: [].concat.apply([], cols.map(function (e) { return ks.filter(function (k) { return e[k] != null; }).map(function (k) { return { v: fmt(e[k], M[k].u), etq: e.n + ' · ' + M[k].n, e: M[k].e }; }); })) };
      }
      var m = M[k], a = cols[0], b = cols[1];
      if (a[k] == null || b[k] == null) {
        var falta = a[k] == null ? a : b;
        return { html: pendEdo(falta, k), fu: [pendFu(falta, k)], tit: m.n, ci: [] };
      }
      var mayor = a[k] >= b[k] ? a : b, menor = mayor === a ? b : a;
      var h2 = '<p><b>' + esc(a.n) + '</b>: ' + fmt(a[k], m.u) + ' · <b>' + esc(b.n) + '</b>: ' + fmt(b[k], m.u) + '.</p>';
      if (m.u === 'pct' || m.u === 'pesos2') h2 += '<p>La diferencia es de <b>' + n(mayor[k] - menor[k], m.u === 'pct' ? 1 : 2) + (m.u === 'pct' ? ' puntos' : ' pesos') + '</b> a favor de ' + esc(mayor.n) + '.</p>';
      else h2 += '<p><b>' + esc(mayor.n) + '</b> tiene <b>' + n(mayor[k] / menor[k], 1) + ' veces</b> lo de ' + esc(menor.n) + ': una diferencia de <b>' + fmt(mayor[k] - menor[k], m.u) + '</b>.</p>';
      if (cols[2]) h2 += '<p>' + cols.slice(2).map(function (e) { return '<b>' + esc(e.n) + '</b>: ' + (e[k] == null ? chip('pendiente', m.pend) : fmt(e[k], m.u)); }).join(' · ') + '.</p>';
      return { html: h2, fu: [fuenteDe(k), { que: 'Diferencia y veces', e: 'derivado', op: 'mayor − menor; mayor ÷ menor' }], tit: 'Comparación: ' + m.n,
        ci: cols.map(function (e) { return { v: fmt(e[k], m.u), etq: e.n, e: m.e }; }) };
    }
    var CORTO = { deuda: 'Deuda', gasto: 'Recibe en 2026 (Ramos 28 y 33)', pc: 'Por habitante', dep: 'Dependencia federal 2024', asf: 'Por aclarar ante la ASF' };

    function total(k) {
      var m = M[k], l = EDO.filter(function (x) { return x[k] != null; });
      var tot = l.reduce(function (s, x) { return s + x[k]; }, 0);
      return { html: '<p>Entre los ' + l.length + ' estados, ' + esc(m.n) + ' suma <b>' + fmt(tot, m.u) + '</b>.</p>', tit: 'Total: ' + m.n,
        fu: [fuenteDe(k), { que: 'Suma', e: 'derivado', op: 'suma de los ' + l.length + ' estados con cifra' }], ci: [{ v: fmt(tot, m.u), etq: m.n + ', suma de los estados', e: 'derivado' }] };
    }
    function parte(e, k) {
      var m = M[k], l = EDO.filter(function (x) { return x[k] != null; });
      if (e[k] == null) return { html: pendEdo(e, k), fu: [pendFu(e, k)], tit: m.n, ci: [] };
      var tot = l.reduce(function (s, x) { return s + x[k]; }, 0), p = e[k] / tot * 100;
      return { html: '<p><b>' + esc(e.n) + '</b> concentra el <b>' + n(p, 1) + ' %</b> de ' + esc(m.n) + ' de los ' + l.length + ' estados: ' + fmt(e[k], m.u) + ' de ' + fmt(tot, m.u) + '.</p>',
        tit: e.n + ': su parte del total', fu: [fuenteDe(k), { que: 'Porcentaje del total', e: 'derivado', op: fmt(e[k], m.u) + ' ÷ ' + fmt(tot, m.u) + ' × 100' }],
        ci: [{ v: n(p, 1) + ' %', etq: 'parte de ' + e.n + ' en ' + m.n, e: 'derivado', op: fmt(e[k], m.u) + ' ÷ ' + fmt(tot, m.u) + ' × 100' }] };
    }

    /* ---------- Las respuestas sobre municipios ---------- */
    var MFU = MU ? { tx: 'INEGI, Estadística de Finanzas Públicas Estatales y Municipales (EFIPEM), cifras definitivas 2024', url: MU.url } : null;
    function munFu(k) { return { que: MUN_NOM[k].charAt(0).toUpperCase() + MUN_NOM[k].slice(1), e: k === 'dep' ? 'derivado' : 'oficial', fu: MFU, op: k === 'dep' ? '(participaciones + aportaciones) ÷ ingresos totales × 100' : '' }; }
    function munLugar(m, k) {
      var l = MUN.filter(function (x) { return x.a === m.a && mv(x, k) != null; }).sort(function (a, b) { return mv(b, k) - mv(a, k); });
      return { l: l.indexOf(m) + 1, de: l.length };
    }
    function munMet(m, k, otros) {
      var nom = esc(m.n) + ', ' + esc(m.en);
      var mas = otros && otros.length ? '<p class="pa-chico">Hay otro' + (otros.length > 1 ? 's' : '') + ' municipio' + (otros.length > 1 ? 's' : '') + ' con ese nombre: ' +
        otros.slice(0, 4).map(function (o) { return '<button type="button" class="pa-enlace" data-pa-pregunta="municipio ' + esc(o.n) + ' ' + esc(o.en) + '">' + esc(o.n) + ', ' + esc(o.en) + '</button>'; }).join(' · ') + '.</p>' : '';
      if (!m.v) return { html: '<p><b>' + nom + '</b> no reportó sus cifras de 2024 a la estadística de finanzas municipales del INEGI, así que no tengo sus números. Puedes revisar su ficha técnica en el Auditor de entes públicos.</p>' + mas,
        fu: [{ que: 'Municipios sin cifra', e: 'pendiente', fu: MFU }], tit: m.n, ci: [] };
      var ing = mv(m, 'ing'), h, fu = [munFu(k || 'ing')], L;
      if (!k || k === 'ing') {
        L = munLugar(m, 'ing');
        h = '<p><b>' + nom + '</b> tuvo ingresos por <b>' + grande(ing, 1) + '</b> en 2024. De cada $100, <b>$' + n(mv(m, 'dep'), 1) + '</b> llegaron de la Federación (participaciones y aportaciones) y <b>$' + n(mv(m, 'propios') / ing * 100, 1) + '</b> los cobró por su cuenta.' +
          (mv(m, 'predial') ? ' Solo de predial juntó <b>' + grande(mv(m, 'predial'), 1) + '</b>.' : '') + (L.de > 1 ? ' Es el lugar <b>' + L.l + ' de ' + L.de + '</b> en ingresos de ' + esc(m.en) + '.' : '') + '</p>';
        fu.push(munFu('dep'), munFu('propios'), { que: 'Porcentajes y lugar', e: 'derivado', op: 'parte ÷ ingresos totales × 100; lugar entre los municipios del estado con cifra' });
      } else if (k === 'dep') {
        h = '<p>De cada $100 que ingresó <b>' + nom + '</b> en 2024, <b>$' + n(mv(m, 'dep'), 1) + '</b> llegaron de la Federación (participaciones y aportaciones). Lo que cobró por su cuenta fue $' + n(mv(m, 'propios') / ing * 100, 1) + ' de cada $100.</p>';
        fu.push(munFu('propios'));
      } else {
        L = munLugar(m, k);
        h = '<p>En 2024, <b>' + nom + '</b> tuvo <b>' + grande(mv(m, k), 1) + '</b> de ' + esc(MUN_NOM[k]) + '. Es el <b>' + n(mv(m, k) / ing * 100, 1) + ' %</b> de sus ingresos' + (k === 'egr' ? '' : '') + '.' +
          (L.de > 1 ? ' Lugar <b>' + L.l + ' de ' + L.de + '</b> en ' + esc(m.en) + '.' : '') + '</p>';
        fu.push({ que: 'Porcentaje y lugar', e: 'derivado', op: 'cifra ÷ ingresos totales × 100; lugar entre los municipios del estado con cifra' });
      }
      return { html: h + mas, fu: fu, val: k === 'dep' ? { v: mv(m, 'dep'), u: 'pct' } : { v: mv(m, k || 'ing'), u: 'pesos' }, tit: m.n + ', ' + m.en + ': ' + MUN_NOM[k || 'ing'], ci: [{ v: grande(mv(m, k || 'ing'), 1), etq: MUN_NOM[k || 'ing'], e: 'oficial' }] };
    }
    function munRanking(k, dir, cuantos, e) {
      k = k || 'ing';
      var l = MUN.filter(function (x) { return (!e || x.a === e.a) && mv(x, k) != null; }).sort(function (a, b) { return dir === 'min' ? mv(a, k) - mv(b, k) : mv(b, k) - mv(a, k); });
      var top = l.slice(0, Math.max(cuantos, 5)), u = k === 'dep' ? 'pct' : '';
      var h = '<p>' + (dir === 'min' ? 'Los municipios con menos' : 'Los municipios con más') + ' ' + esc(RKM[k]) + (e ? ' en <b>' + esc(e.n) + '</b>' : ' del país') + ':</p><ol class="pa-lista">' +
        top.map(function (x) { return '<li><b>' + esc(x.n) + '</b>' + (e ? '' : ', ' + esc(x.en)) + ': ' + (u ? n(mv(x, k), 1) + ' %' : grande(mv(x, k), 1)) + '</li>'; }).join('') + '</ol>' +
        '<p class="pa-chico">Entre ' + n(l.length) + ' municipios con cifras de 2024.</p>';
      return { html: h, fu: [munFu(k), { que: 'Orden', e: 'derivado', op: 'ordenamos los municipios con cifra' }], tit: 'Municipios: ' + MUN_NOM[k],
        ci: top.map(function (x) { return { v: u ? n(mv(x, k), 1) + ' %' : grande(mv(x, k), 1), etq: x.n + ', ' + x.en, e: k === 'dep' ? 'derivado' : 'oficial' }; }) };
    }

    /* ---------- Sueldos de los cargos ---------- */
    var CARGO_RE = [
      ['diputado_local', /diputad[oa]s? local|diputad[oa]s? (del|de la) (congreso|estado)|congreso local/],
      ['asesor_diputados', /asesor(es)? de (los )?diputad/], ['asesor_senado', /asesor(es)? de(l| los)? senad/], ['asesor_scjn', /asesor(es)? de (la )?(corte|scjn|ministr)/],
      ['secretario_estudio', /secretari[oa]s? de estudio/], ['proyectista_tribunal', /proyectista(s)? de tribunal/], ['proyectista_juzgado', /proyectista/],
      ['subsecretario', /subsecretari/],
      ['presidencia', /presidenta de la republica|presidente de la republica|la presidenta|el presidente|\bpresi\b|presidencia|sheinbaum|claudia/],
      ['diputados', /diputad/], ['senado', /senador|senado/], ['ministro', /ministr|suprema corte|\bscjn\b/], ['magistrado', /magistrad/],
      ['juez', /\bjuez|jueza|jueces/], ['secretario', /secretari[oa]s? de estado|secretari[oa] de (hacienda|gobernacion|salud|educacion|economia|energia)|un secretario|los secretarios/]
    ];
    var GANA = /gana|ganan|sueldo|salario|cobra|cobran|percibe|perciben|le pagan|les pagan|paga|pagan|remuner|lana|varo|billete|cuanto se lleva|cuanto se llevan|ingreso/;
    var CARGO = {};
    (D.cargos || []).forEach(function (c) { CARGO[c.id] = c; });
    function cargoDe(t) {
      if (/presidente municipal|presidenta municipal|alcalde/.test(t)) return null;
      for (var i = 0; i < CARGO_RE.length; i++) if (CARGO_RE[i][1].test(t) && CARGO[CARGO_RE[i][0]]) return CARGO[CARGO_RE[i][0]];
      return null;
    }
    function cargoResp(c) {
      var sm = D.smin, mens = c.min != null && c.min !== c.max ? 'entre <b>$' + n(c.min) + ' y $' + n(c.max) + '</b>' : '<b>$' + n(c.max) + '</b>';
      var veces = sm ? c.max / sm.mes : null;
      var h = '<p>' + esc(art(c.n)) + ' gana ' + mens + ' al mes, netos (ya sin impuestos). Al año son <b>$' + n(c.anual) + '</b>.</p>' +
        (veces ? '<p>Para darte una idea: eso es <b>' + n(veces, 1) + ' veces</b> el salario mínimo general de un mes ($' + n(sm.mes, 2) + ').</p>' : '');
      var fu = [{ que: 'Sueldo mensual', e: c.e, fu: c.fu }, { que: 'Sueldo anual', e: c.ea, fu: c.fu, op: c.op }];
      if (veces) fu.push({ que: 'Salario mínimo general 2026', e: 'oficial', fu: sm.fu, op: '$' + n(sm.dia, 2) + ' diarios × 30' }, { que: 'Veces el salario mínimo', e: 'derivado', op: 'sueldo mensual neto ÷ salario mínimo mensual. El sueldo del cargo es neto y el mínimo es bruto: la comparación se queda corta' });
      return { html: h, fu: fu, val: { v: c.max, u: 'pesos', min: c.min, anual: c.anual }, tit: 'Cuánto gana: ' + c.n, ir: SUELDOS, ci: [{ v: '$' + n(c.max), etq: 'al mes, neto', e: c.e }, { v: '$' + n(c.anual), etq: 'al año, neto', e: c.ea, op: c.op }] };
    }
    function art(nom) {
      var t = nom.split(' (')[0];
      if (/^Presidenta de la Rep/.test(t)) return 'La ' + t.charAt(0).toLowerCase() + t.slice(1);
      if (/^(Presidenta|Ministra|Senadora|Diputada|Jueza|Magistrada)/.test(t)) return 'Una ' + t.charAt(0).toLowerCase() + t.slice(1).replace(/^presidenta de la república/i, 'presidenta de la República');
      return (/^(Las |Los |La |El )/.test(t) ? t : 'Un ' + t.charAt(0).toLowerCase() + t.slice(1)).replace(/^Una presidenta/, 'La presidenta');
    }
    /* «Saber más» de los sueldos: Tú contra ellos, donde están todos los cargos. */
    var SUELDOS = ['herramienta-calculadora-compara.html', 'Tú contra ellos'];
    function cargosRanking() {
      var l = (D.cargos || []).slice().sort(function (a, b) { return b.max - a.max; });
      return { html: '<p>Así quedan los sueldos mensuales netos de 2026, de mayor a menor:</p><ol class="pa-lista">' + l.map(function (c) { return '<li><b>' + esc(c.n) + '</b>: $' + n(c.max) + '</li>'; }).join('') + '</ol>',
        fu: [{ que: 'Sueldos', e: 'oficial', fu: l[0].fu }, { que: 'Orden', e: 'derivado', op: 'de mayor a menor sueldo mensual' }], tit: 'Quién gana más',
        ci: l.slice(0, 6).map(function (c) { return { v: '$' + n(c.max), etq: c.n, e: c.e }; }), ir: SUELDOS };
    }

    /* ---------- Las administraciones ---------- */
    var ADM_RE = [['salinas', /salinas/], ['zedillo', /zedillo/], ['fox', /\bfox\b|vicente fox/], ['calderon', /calderon|felipe calderon/],
      ['epn', /\bepn\b|pena nieto|enrique pena|\bpena\b/], ['amlo', /\bamlo\b|lopez obrador|andres manuel|\bobrador\b|el peje|\bpeje\b/],
      ['sheinbaum', /sheinbaum|claudia|\bcsp\b|la presidenta actual|este sexenio|sexenio actual/]];
    var ADM = {};
    (D.adm || []).forEach(function (a) { ADM[a.id] = a; });
    function admsDe(t) {
      var out = [];
      ADM_RE.forEach(function (x) { var i = t.search(x[1]); if (i >= 0 && ADM[x[0]]) out.push({ a: ADM[x[0]], i: i }); });
      return out.sort(function (a, b) { return a.i - b.i; }).map(function (x) { return x.a; });
    }
    function av(a, k) { var x = a.v[k]; return x && x.v != null ? x : null; }
    function admFu(a, k) { var x = av(a, k); return x ? { que: D.admet[k].n, e: x.e, fu: x.fu, op: x.op } : null; }
    function admResp(a, tema, sub, mon) {
      var nom = '<b>' + esc(a.n) + '</b> (' + a.a[0] + '–' + a.a[1] + ')', h = '', fu = [], ci = [];
      function v(k) { var x = av(a, k); if (!x) return null; fu.push(admFu(a, k)); ci.push({ v: fmt(x.v, D.admet[k].u), etq: D.admet[k].n, e: x.e, op: x.op }); return '<b>' + fmt(x.v, D.admet[k].u) + '</b>'; }
      if (tema === 'deuda' || !tema) {
        var i = v('deuda_ini'), f = v('deuda_fin'), c = v('deuda_cambio');
        if (i && f) h += '<p>Con ' + nom + ', la deuda pasó de ' + i + ' al recibir a ' + f + ' al entregar' + (c ? ': un cambio de ' + c : '') + '.</p>';
      }
      if (tema === 'intereses') {
        var ip = v('costo_financiero_pib'), im = v('costo_financiero_mdp');
        if (ip) h += '<p>Con ' + nom + ', en intereses de la deuda (el costo financiero) se fue en promedio ' + ip + ' al año' + (im ? '; sumados, ' + im + ' en pesos de cada año' : '') + '.</p>';
      }
      if (tema === 'gasto' || !tema) { var g = v('gasto_pib'); if (g) h += '<p>' + (tema ? 'Con ' + nom + ', el' : 'El') + ' gasto neto total promedió ' + g + ' al año.</p>'; }
      if (tema === 'ingresos') { var ig = v('ingresos_pib'); if (ig) h += '<p>Con ' + nom + ', los ingresos del sector público promediaron ' + ig + ' al año.</p>'; }
      if (tema === 'inversion') { var iv = v('inversion_pib'); if (iv) h += '<p>Con ' + nom + ', la inversión física promedió ' + iv + ' al año.</p>'; }
      /* La suma del sexenio, en pesos de cada año y en pesos de hoy (o en dólares o euros). */
      var SUMA = { gasto: 'gasto_mdp', ingresos: 'ingresos_mdp', inversion: 'inversion_mdp' }[tema];
      if (SUMA) h += admSuma(a, SUMA, mon, fu, ci);
      if (tema === 'intereses' && mon) h += admSuma(a, 'costo_financiero_mdp', mon, fu, ci, 1);
      if (tema === 'seg') h += admRitmo(a, sub, fu, ci);
      if (tema === 'peso') h += admPeso(a, fu, ci);
      if (tema === 'asf' || !tema) {
        var au = v('asf_aud'), ac = v('asf_acl'), re = tema === 'asf' ? v('asf_rec') : null;
        if (re && a.v.asf_rec.nota) fu[fu.length - 1].op += ' ' + a.v.asf_rec.nota;
        if (au || ac) h += '<p>La ASF le practicó ' + (au || 'varias') + ' auditorías' + (ac ? ' y dejó ' + ac + ' por aclarar' : '') + (re ? '; se recuperaron ' + re : '') + '.</p>' +
          (tema === 'asf' ? '<p class="pa-ojo">Ojo: «por aclarar» no es daño comprobado; es lo que, al corte, no tenía documentos que acreditaran el gasto.</p>' : '');
      }
      if (!h) h = '<p>De ' + nom + ' no tengo ese dato en su estado de cuenta.</p>';
      if (a.curso && a.aviso) h += '<p class="pa-chico">' + esc(a.aviso) + '</p>';
      return { html: h, fu: fu, ci: ci, tit: 'Estado de cuenta de ' + a.n + (tema ? ': ' + tema : '') };
    }
    /* La suma de un sexenio: pesos de cada año, de hoy, dólares o euros (el Radar). */
    function admSuma(a, k, mon, fu, ci, ya) {
      var x = a.v[k], m = D.admet[k];
      if (!x) return '';
      if (x.v == null) {
        var p = x.parcial, h = '<p class="pa-chico">' + esc(x.na) + '</p>';
        if (p) {
          h += '<p>Con los ' + (p.ys[1] - p.ys[0] + 1) + ' años con dato (' + p.ys[0] + ' a ' + p.ys[1] + ') suman <b>' + mdp(p.v) + '</b> en pesos de cada año' +
            (p.hoy ? ' (<b>' + mdp(p.hoy.v) + '</b> en pesos de ' + esc(PSO ? PSO.ref.mes : 'hoy') + ')' : '') + '.</p>';
          fu.push({ que: m.n + ' (años con dato)', e: p.e, fu: p.fu, op: p.op });
          if (p.hoy) fu.push({ que: 'En pesos de hoy', e: 'derivado', op: p.hoy.op });
        }
        return h;
      }
      var alt = mon && x[mon] ? x[mon] : x.hoy, et = alt === x.usd ? 'millones de dólares' : alt === x.eur ? 'millones de euros' : null;
      fu.push({ que: m.n, e: x.e, fu: x.fu, op: x.op });
      ci.push({ v: mdp(x.v), etq: m.n, e: x.e });
      var h2 = '<p>' + (ya ? 'En pesos de cada año suman' : 'Sumados, son') + ' <b>' + mdp(x.v) + '</b>' + (ya ? '' : ' en pesos de cada año');
      if (alt) {
        h2 += et ? ': unos <b>' + n(alt.v / 1e3, 1) + ' mil ' + et + '</b>' : ', que en pesos de ' + esc(PSO ? PSO.ref.mes : 'hoy') + ' equivalen a <b>' + mdp(alt.v) + '</b>';
        fu.push({ que: m.n + (et ? ', en ' + et.replace('millones de ', '') : ', en pesos de hoy'), e: 'derivado', op: alt.op });
      }
      return h2 + '.</p>';
    }
    /* El reloj: lo de un sexenio repartido entre sus segundos. */
    function admRitmo(a, sub, fu, ci) {
      var k = sub || 'deuda_seg', x = a.v[k], m = D.admet[k];
      if (!x) return '';
      if (x.v == null) return '<p>' + esc(x.na) + '</p>';
      var ys = [a.a[0], a.a[1]];
      var dias = 0; for (var y = ys[0]; y <= ys[1]; y++) dias += (y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0)) ? 366 : 365;
      var seg = k === 'deuda_seg' ? x.v : x.v * 1e6 / (dias * 86400);
      var que = { deuda_seg: 'la deuda creció', costo_financiero_mdp: 'se pagaron de intereses', inversion_mdp: 'se invirtieron', ingresos_mdp: 'entraron', gasto_mdp: 'se gastaron' }[k];
      fu.push({ que: m.n + ', por segundo', e: 'derivado', fu: x.fu, op: k === 'deuda_seg' ? x.op : x.op + ' Luego, entre los ' + n(dias * 86400) + ' segundos de esos años.' });
      ci.push({ v: '$' + n(seg), etq: 'Por segundo', e: 'derivado' });
      return '<p>Al ritmo de ' + esc(a.n) + ', ' + que + ' <b>$' + n(seg) + ' por segundo</b>: ' + mdp(seg * 3600 / 1e6) + ' por hora y ' + mdp(seg * 86400 / 1e6) + ' al día.</p>' +
        '<p class="pa-chico">Es una equivalencia en pesos de cada año (lo del sexenio entre sus segundos), no dinero que se mueva hoy.</p>';
    }
    /* El peso en el sexenio: inflación acumulada, dólar y euro. */
    function admPeso(a, fu, ci) {
      var x = PSO && PSO.adm[a.id];
      if (!x) return '';
      var h = '<p>Con ' + esc(a.n) + ' (' + esc(x.rec) + ' → ' + esc(x.ent) + (x.curso ? ', en curso' : '') + '), los precios subieron <b>' + n(x.infl.v, 1) + ' %</b>: $100 al recibir compraban al final lo que <b>$' + n(x.cien.v, 2) + '</b>.';
      fu.push({ que: 'Inflación acumulada', e: 'derivado', fu: PSO.fx.BX_INPC, op: x.infl.op + ' ' + x.cien.op });
      ci.push({ v: n(x.infl.v, 1) + ' %', etq: 'Inflación acumulada', e: 'derivado' });
      if (x.usd) { h += ' El dólar pasó de $' + n(x.usd.rec, 2) + ' a $' + n(x.usd.ent, 2) + ' (' + (x.usd.v > 0 ? '+' : '') + n(x.usd.v, 1) + ' %)'; fu.push({ que: 'El dólar', e: 'derivado', fu: PSO.fx.BX_USD, op: x.usd.op }); }
      if (x.eur && x.eur.rec != null) { h += ' y el euro, de $' + n(x.eur.rec, 2) + ' a $' + n(x.eur.ent, 2) + ' (' + (x.eur.v > 0 ? '+' : '') + n(x.eur.v, 1) + ' %)'; fu.push({ que: 'El euro', e: 'derivado', fu: PSO.fx.BX_EUR, op: x.eur.op }); }
      h += x.usd ? '.</p>' : '</p>';
      if (!x.eur || x.eur.rec == null) h += '<p class="pa-chico">Del euro no hay serie: ' + esc(PSO.eur_antes) + '</p>';
      return h;
    }
    function admTema(t) {
      if (/por segundo|por hora|cada segundo|ritmo|reloj|al dia|por dia/.test(t)) return 'seg';
      if (/interes|costo financiero/.test(t)) return 'intereses';
      if (/deud|debe|endeud|prest/.test(t)) return 'deuda';
      if (/inversion|\bobras?\b/.test(t)) return 'inversion';
      if (/ingres|recaud|cobr/.test(t)) return 'ingresos';
      if (/gast/.test(t)) return 'gasto';
      if (/inflacion|dolar|euro|tipo de cambio|precios|poder adquisitivo|devalu|el peso\b/.test(t)) return 'peso';
      if (/asf|aclarar|rob|auditor|corrup|desvi|transa|chingaron|clavaron|recuper/.test(t)) return 'asf';
      return '';
    }

    /* ---------- La calculadora: porcentajes y márgenes ---------- */
    var NUM = '\\$?\\s*(\\d[\\d,]*(?:\\.\\d+)?)\\s*(billones?|mil millones|millones?|mdp|mil|k)?';
    function valor(num, esc_) {
      var v = parseFloat(String(num).replace(/,/g, ''));
      var e = String(esc_ || '');
      if (/^billon/.test(e)) v *= 1e12; else if (e === 'mil millones') v *= 1e9; else if (/^millon|^mdp/.test(e)) v *= 1e6; else if (e === 'mil' || e === 'k') v *= 1e3;
      return v;
    }
    function calcula(q) {
      var t = norm(q).replace(/por ?ciento/g, '%').replace(/[¿?¡!]/g, ' ').replace(/\s+/g, ' ');
      var peso = /\$|peso|millon|mdp|billon/.test(t), m, a, b, r, op, h;
      /* Un folio o una fecha no son una división: INE/CG564/2025, 15/06/2025. */
      if (/[a-z]\d+\/\d|\b\d{1,2}\/\d{1,2}\/\d{2,4}\b/.test(t)) return null;
      if ((m = new RegExp('(\\d[\\d,]*(?:\\.\\d+)?)\\s*%\\s*(?:de|del|sobre)\\s*' + NUM).exec(t))) {
        a = parseFloat(m[1].replace(/,/g, '')); b = valor(m[2], m[3]); r = b * a / 100;
        h = '<b>El ' + n(a, a % 1 ? 2 : 0) + ' % de ' + grande(b, peso) + ' es ' + grande(r, peso) + '.</b>'; op = grande(b, peso) + ' × ' + a + ' ÷ 100';
      } else if ((m = new RegExp('(?:que|cuanto) (?:porcentaje|%|parte|por ciento)\\s*(?:es|son|representa|representan|equivale a)?\\s*' + NUM + '\\s*(?:de|del total de|sobre|respecto a|frente a)\\s*' + NUM).exec(t))) {
        a = valor(m[1], m[2]); b = valor(m[3], m[4]); r = a / b * 100;
        h = '<b>' + grande(a, peso) + ' es el ' + grande(r) + ' % de ' + grande(b, peso) + '.</b>'; op = grande(a, peso) + ' ÷ ' + grande(b, peso) + ' × 100';
      } else if ((m = new RegExp('(?:de|desde)\\s*' + NUM + '\\s*(?:a|hasta)\\s*' + NUM).exec(t)) && /aument|subi|creci|baj|cambi|variacion|diferencia|margen|cuanto (es|fue)|porcentaje|%/.test(t)) {
        a = valor(m[1], m[2]); b = valor(m[3], m[4]); r = (b - a) / a * 100;
        h = '<b>De ' + grande(a, peso) + ' a ' + grande(b, peso) + ' hay un cambio de ' + (r >= 0 ? '+' : '') + grande(r) + ' %</b> (' + (b - a >= 0 ? '+' : '−') + grande(Math.abs(b - a), peso) + ').'; op = '(' + grande(b, peso) + ' − ' + grande(a, peso) + ') ÷ ' + grande(a, peso) + ' × 100';
      } else if ((m = new RegExp(NUM + '\\s*(?:entre|dividido entre|/)\\s*' + NUM).exec(t))) {
        a = valor(m[1], m[2]); b = valor(m[3], m[4]); r = a / b;
        h = '<b>' + grande(a, peso) + ' entre ' + grande(b, false) + ' da ' + grande(r, peso) + '.</b>'; op = grande(a, peso) + ' ÷ ' + grande(b, false);
      } else if ((m = new RegExp(NUM + '\\s*(?:por|x|\\*|multiplicado por)\\s*' + NUM).exec(t))) {
        a = valor(m[1], m[2]); b = valor(m[3], m[4]); r = a * b;
        h = '<b>' + grande(a, peso) + ' por ' + grande(b, false) + ' da ' + grande(r, peso) + '.</b>'; op = grande(a, peso) + ' × ' + grande(b, false);
      } else if ((m = new RegExp(NUM + '\\s*(mas|\\+|menos|-)\\s*' + NUM).exec(t))) {
        a = valor(m[1], m[2]); b = valor(m[4], m[5]); var suma = /mas|\+/.test(m[3]); r = suma ? a + b : a - b;
        h = '<b>' + grande(a, peso) + (suma ? ' más ' : ' menos ') + grande(b, peso) + ' da ' + grande(r, peso) + '.</b>'; op = grande(a, peso) + (suma ? ' + ' : ' − ') + grande(b, peso);
      } else return null;
      if (!isFinite(r)) return { html: '<p>Esa cuenta no se puede hacer: hay una división entre cero.</p>', fu: [], tit: 'Cuenta' };
      return { html: '<p>' + h + '</p><p class="pa-chico">La cuenta: ' + esc(op) + '. Si quieres, pregúntame por una cifra de la plataforma y la uso en la cuenta.</p>', fu: [], tit: 'Cuenta', calc: 1 };
    }

    /* ---------- El país: deuda, intereses, ingresos y gasto federales ---------- */
    function cifra(tit) {
      var f = B.fichas.filter(function (x) { return x.t === 'cifra' && x.tit === tit; })[0];
      return f && f.ci && f.ci[0] ? { v: parseFloat(f.ci[0].v.replace(/[$,]/g, '')), e: f.ci[0].e, fu: (f.fu || [])[0], f: f } : null;
    }
    var NAC = /gobierno federal|del pais|el pais|de mexico|\bmexico\b|la federacion|nacional|\bpais\b|\bnacion\b|federal/;
    function nacTema(t) {
      if (/interes|costo financiero/.test(t)) return 'intereses';
      if (/deuda nueva|se endeud|nueva deuda|pide prestado|pedir prestado|endeudamiento (nuevo|neto|autorizado)/.test(t)) return 'nueva';
      if (/deud|debe\b|deben\b|adeud/.test(t)) return 'deuda';
      if (/impuesto|tributari|recaud|ingres|cobra/.test(t)) return 'ingresos';
      if (/gast|presupuesto|egres/.test(t)) return 'gasto';
      return '';
    }
    function nacional(tema) {
      var a, b, h, fu = [], dia;
      var que = function (x, q) { if (x) fu.push({ que: q, e: x.e, fu: x.fu }); return x; };
      if (tema === 'deuda') {
        a = que(cifra('Deuda pública (SHRFSP) (aprobado 2026)'), 'Deuda pública aprobada para 2026'); b = que(cifra('Deuda pública (SHRFSP) (propuesta 2027)'), 'Deuda pública propuesta para 2027');
        if (!a) return null;
        h = '<p>La deuda del país, medida en su forma más amplia (el Saldo Histórico de los Requerimientos Financieros del Sector Público, SHRFSP), es de <b>' + mdp(a.v) + '</b> en lo aprobado para 2026.' + (b ? ' Para 2027, el Paquete Económico propone <b>' + mdp(b.v) + '</b>.' : '') + '</p>';
      } else if (tema === 'intereses') {
        a = que(cifra('Costo financiero de la deuda (aprobado 2026)'), 'Costo financiero aprobado para 2026'); b = que(cifra('Costo financiero de la deuda (propuesta 2027)'), 'Costo financiero propuesto para 2027');
        if (!a) return null;
        dia = a.v / 365;
        h = '<p>Solo en intereses de la deuda (el costo financiero), en 2026 se van <b>' + mdp(a.v) + '</b>. Eso es como <b>' + mdp(dia) + ' al día</b>.' + (b ? ' Para 2027 se proponen <b>' + mdp(b.v) + '</b>.' : '') + '</p>';
        fu.push({ que: 'Al día', e: 'derivado', op: mdp(a.v) + ' ÷ 365' });
      } else if (tema === 'nueva') {
        a = que(cifra('Deuda nueva autorizada para 2026'), 'Deuda nueva autorizada para 2026');
        if (!a) return null;
        dia = a.v / 365;
        h = '<p>Para 2026, el Congreso autorizó contratar <b>' + mdp(a.v) + '</b> de deuda nueva. Repartido en el año, son <b>' + mdp(dia) + ' al día</b>.</p>';
        fu.push({ que: 'Al día', e: 'derivado', op: mdp(a.v) + ' ÷ 365' });
      } else if (tema === 'ingresos') {
        a = que(cifra('Ingresos presupuestarios (aprobado 2026)'), 'Ingresos presupuestarios aprobados para 2026'); b = que(cifra('Ingresos tributarios (aprobado 2026)'), 'Ingresos tributarios aprobados para 2026');
        var c = que(cifra('Ingresos presupuestarios (propuesta 2027)'), 'Ingresos presupuestarios propuestos para 2027');
        if (!a) return null;
        h = '<p>Para 2026 se aprobaron ingresos por <b>' + mdp(a.v) + '</b>' + (b ? '; de ellos, <b>' + mdp(b.v) + '</b> son impuestos (el ' + n(b.v / a.v * 100, 1) + ' %)' : '') + '.' + (c ? ' Para 2027 se proponen <b>' + mdp(c.v) + '</b>.' : '') + '</p>';
        if (b) fu.push({ que: 'Parte de los impuestos', e: 'derivado', op: 'ingresos tributarios ÷ ingresos presupuestarios × 100' });
      } else if (tema === 'gasto') {
        a = que(cifra('Gasto neto pagado (aprobado 2026)'), 'Gasto neto pagado aprobado para 2026'); b = que(cifra('Gasto neto pagado (propuesta 2027)'), 'Gasto neto pagado propuesto para 2027');
        if (!a) return null;
        h = '<p>Para 2026 se aprobó un gasto de <b>' + mdp(a.v) + '</b> (gasto neto pagado).' + (b ? ' Para 2027, el Paquete Económico propone <b>' + mdp(b.v) + '</b>.' : '') + '</p>';
      } else return null;
      return { html: h, fu: fu, val: { v: a.v, u: 'mdp', dia: dia }, tit: 'El país: ' + tema, ficha: a.f, ir: a.f.ir,
        sug: ['¿Cuánto se paga de intereses al día?', '¿Cuánta deuda dejó AMLO?', '¿Qué estado debe más?'] };
    }

    /* ---------- Lo que se aprobó a cada dependencia en 2026 ---------- */
    var DEP_ALIAS = { 'sedena': 'Secretaría de la Defensa Nacional', 'defensa': 'Secretaría de la Defensa Nacional', 'ejercito': 'Secretaría de la Defensa Nacional',
      'semar': 'Secretaría de Marina', 'marina': 'Secretaría de Marina', 'sep': 'Secretaría de Educación Pública', 'educacion': 'Secretaría de Educación Pública',
      'ssa': 'Secretaría de Salud', 'salud': 'Secretaría de Salud', 'bienestar': 'Secretaría de Bienestar', 'sict': 'Secretaría de Infraestructura, Comunicaciones y Transportes',
      'sener': 'Secretaría de Energía', 'energia': 'Secretaría de Energía', 'semarnat': 'Secretaría de Medio Ambiente y Recursos Naturales',
      'shcp': 'Secretaría de Hacienda y Crédito Público', 'hacienda': 'Secretaría de Hacienda y Crédito Público', 'segob': 'Secretaría de Gobernación', 'gobernacion': 'Secretaría de Gobernación',
      'sre': 'Secretaría de Relaciones Exteriores', 'cancilleria': 'Secretaría de Relaciones Exteriores', 'sader': 'Secretaría de Agricultura y Desarrollo Rural', 'agricultura': 'Secretaría de Agricultura y Desarrollo Rural',
      'stps': 'Secretaría del Trabajo y Previsión Social', 'sedatu': 'Secretaría de Desarrollo Agrario, Territorial y Urbano', 'sectur': 'Secretaría de Turismo', 'turismo': 'Secretaría de Turismo',
      'economia': 'Secretaría de Economía', 'se': '', 'sspc': 'Secretaría de Seguridad y Protección Ciudadana', 'seguridad': 'Secretaría de Seguridad y Protección Ciudadana',
      'ine': 'Instituto Nacional Electoral', 'inegi': 'Instituto Nacional de Estadística y Geografía', 'imss': 'Instituto Mexicano del Seguro Social', 'seguro social': 'Instituto Mexicano del Seguro Social',
      'issste': 'ISSSTE', 'pemex': 'Petróleos Mexicanos', 'cfe': 'Comisión Federal de Electricidad', 'fgr': 'Fiscalía General de la República', 'fiscalia': 'Fiscalía General de la República',
      'cndh': 'Comision Nacional de los Derechos Humanos', 'secihti': 'Secretaría de Ciencia, Humanidades, Tecnología e Innovación', 'cultura': 'Secretaría de Cultura',
      'congreso': 'Poder Legislativo', 'poder legislativo': 'Poder Legislativo', 'poder judicial': 'Poder Judicial de la Federación', 'mujeres': 'Secretaría de las Mujeres',
      'anticorrupcion': 'Secretaría Anticorrupción y Buen Gobierno', 'buen gobierno': 'Secretaría Anticorrupción y Buen Gobierno', 'presidencia': 'Oficina de la Presidencia de la República' };
    var DEPS = B.fichas.filter(function (f) { return f.t === 'cifra' && /: presupuesto aprobado para 2026$/.test(f.tit); });
    function dependencia(t) {
      var hall = null, largo = 0;
      DEPS.forEach(function (f) {
        var nom = f.tit.split(':')[0], k = plano(nom).trim(), corto_ = k.replace(/^(secretaria|instituto|comision|tribunal(es)?|agencia|consejeria|fiscalia) (de (la |los |las )?|del |federal de |nacional de )?/, '');
        [k, corto_].forEach(function (x) { if (x.length >= 4 && t.indexOf(' ' + x + ' ') >= 0 && x.length > largo) { hall = f; largo = x.length; } });
      });
      Object.keys(DEP_ALIAS).forEach(function (a) {
        if (DEP_ALIAS[a] && t.indexOf(' ' + a + ' ') >= 0 && a.length > largo) {
          var f = DEPS.filter(function (x) { return plano(x.tit.split(':')[0]) === plano(DEP_ALIAS[a]); })[0];
          if (f) { hall = f; largo = a.length; }
        }
      });
      return hall;
    }
    function depResp(f) {
      var v = parseFloat(f.ci[0].v.replace(/[$,]/g, '')), nom = f.tit.split(':')[0];
      var l = DEPS.map(function (x) { return parseFloat(x.ci[0].v.replace(/[$,]/g, '')); }).sort(function (a, b) { return b - a; });
      var fed = B.fichas.filter(function (x) { return x.t === 'ficha' && plano(x.tit) === plano(nom); })[0];
      var art_ = /^(Secretar|Comisi|Fiscal|Consejer|Agencia|Oficina)/.test(nom) ? 'a la' : /^(Instituto|Poder|Tribunal |ISSSTE)/.test(nom) ? 'al' : /^Tribunales/.test(nom) ? 'a los' : 'a';
      return { html: '<p>Para 2026, ' + art_ + ' <b>' + esc(nom) + '</b> le aprobaron <b>' + mdp(v) + '</b>. Son unos <b>' + mdp(v / 365) + ' al día</b>.' +
          ' Entre las ' + l.length + ' instituciones de mi catálogo, es la <b>número ' + (l.indexOf(v) + 1) + '</b> con más presupuesto.</p>',
        fu: [{ que: 'Presupuesto aprobado 2026', e: f.ci[0].e, fu: (f.fu || [])[0] }, { que: 'Al día y lugar', e: 'derivado', op: 'aprobado ÷ 365; orden entre las instituciones del catálogo de cifras oficiales' }],
        val: { v: v, u: 'mdp' }, tit: nom + ': presupuesto 2026', ficha: f, ir: fed ? fed.ir : f.ir };
    }

    /* ---------- Cuántos municipios tiene cada estado ---------- */
    var MUNIS = ['numeros-los-municipios.html', 'Los municipios, en Números'];
    function cuentaMun(e, dir) {
      if (!MU) return null;
      var ab = e ? Object.keys(MU.ent).filter(function (x) { return (porA[x] || porA[x.replace('É', 'E')] || {}).a === e.a || x === e.a; })[0] : null;
      var fu = [{ que: 'Municipios', e: 'oficial', fu: { tx: 'INEGI, Catálogo Único de Claves de Áreas Geoestadísticas', url: MU.url } }];
      if (e && ab) return { html: '<p><b>' + esc(e.n) + '</b> tiene <b>' + n(MU.ent[ab].n) + ' municipios</b>' + (e.a === 'CDMX' ? ' (en la Ciudad de México se llaman alcaldías)' : '') + '. En todo el país hay ' + n(MU.catalogo) + '.</p>', fu: fu, tit: e.n + ': municipios', ir: MUNIS };
      var l = Object.keys(MU.ent).map(function (x) { return { n: (porA[x] || {}).n || x, c: MU.ent[x].n }; }).sort(function (a, b) { return dir === 'min' ? a.c - b.c : b.c - a.c; });
      return { html: '<p>En México hay <b>' + n(MU.catalogo) + ' municipios</b>. Los estados con ' + (dir === 'min' ? 'menos' : 'más') + ':</p><ol class="pa-lista">' + l.slice(0, 5).map(function (x) { return '<li><b>' + esc(x.n) + '</b>: ' + n(x.c) + '</li>'; }).join('') + '</ol>',
        fu: fu.concat([{ que: 'Orden', e: 'derivado', op: 'ordenamos los estados por número de municipios' }]), tit: 'Municipios por estado', ir: MUNIS };
    }

    /* ---------- La pestaña Números: ingresos, gasto, ramos, Paquete 2027 (asistente_numeros.py) ---------- */
    var NU = D.num || {}, NF = NU.filas || [], NG = NU.grupos || {}, NPAR = {};
    /* La pestaña Datos (asistente_datos.py) suma sus renglones a los mismos: ambiente, basura, Ramo 16 y la ASF. */
    var DT = D.datos || {}, PSO = DT.peso;
    var NORD = ['ing26', 'egr26', 'tres26', 'mun26', 'fed26', 'munp', 'ramo26', 'func27', 'pq27', 'soc27', 'inv27', 'colchon', 'cf24', 'cp25', 'r16', 'amb24', 'basura', 'asf', 'asfg', 'asfs'];
    NF.forEach(function (f) { f.alp = (f.al || []).map(function (a) { return ' ' + a + ' '; }); if (f.par) (NPAR[f.par] = NPAR[f.par] || []).push(f); });
    var NQUIERE = /cuant|monto|cifra|presupuest|recaud|cobr|gast|cuesta|cuestan|costo|asign|aprob|toca|lana|dinero|varo|porcentaje|parte|de cada|que tanto|propon|recibe|reciben|tiene|vale|suma|ingres|deja|aporta|sale|entra|billon|millon|dime|dato|ejerc|reparte|da |dan |le dan|se va|se van|va a|van a/;
    var NLISTA = /\b(cuales|lista|desglose|desglosa|reparte|se divide|se compone|en que se (gasta|va|van)|a donde va|de donde (sale|viene|vienen|entra)|renglones|rubros|todos los|todas las)\b/;
    function numFila(t) {
      var mejor = null, ml = -1e9, mo = 99;
      NF.forEach(function (f) {
        f.alp.forEach(function (a) {
          if (t.indexOf(a) < 0) return;
          var o = NORD.indexOf(f.g), L = a.length - (f.tot ? 100 : f.sut ? 50 : 0);
          if (L > ml || (L === ml && o < mo)) { mejor = f; ml = L; mo = o; }
        });
      });
      if (!mejor) return null;
      var anio = (/\b(19[89]\d|20[0-3]\d)\b/.exec(t) || [])[1];
      /* «El presupuesto de 2027» todavía es propuesta: su cifra es la del Paquete Económico. */
      if (anio === '2027' && (mejor.id === 'egr-total' || mejor.id === 'ing-total')) return NF.filter(function (x) { return x.id === (mejor.id === 'egr-total' ? 'pq-f-gasto' : 'pq-f-ing'); })[0] || mejor;
      if (anio && mejor.y !== anio && mejor.par) { var otro = (NPAR[mejor.par] || []).filter(function (x) { return x.y === anio; })[0]; if (otro) mejor = otro; }
      return mejor;
    }
    function nv(f, v) {
      if (f.vt && (v == null || v === f.v)) return f.vt;
      v = v == null ? f.v : v;
      if (f.un) return n(v, f.dec || 0) + (f.un === '%' ? ' %' : ' ' + f.un);
      if (f.u === 'mdd') return '$' + n(Math.abs(v), 1) + ' millones de dólares';
      return (v < 0 ? '−' : '') + mdp(Math.abs(v));
    }
    function aDe(f) {
      var nom = f.n;
      if (/^ramo-\d/.test(f.id) && f.sg === 'Ramos generales') return 'al <b>Ramo ' + f.id.slice(5, 7) + '</b> (' + esc(nom) + ')';
      var a = /^(Secretar|Comisi|Fiscal|Consejer|Agencia|Oficina|C[aá]mara|Auditor|Suprema)/.test(nom) ? 'a la' : /^(Instituto|Poder|Tribunal |[OÓ]rgano|ISSSTE|Servicio)/.test(nom) ? 'al' :
        /^Tribunales/.test(nom) ? 'a los' : /^Entidades/.test(nom) ? 'a las' : 'a';
      return a + ' <b>' + esc(nom) + '</b>';
    }
    function del(s) { return s.replace(/^el /, 'del ').replace(/^(?!del )/, 'de '); }
    function numFrase(f, V) {
      if (f.fr) return esc(f.fr).replace('{V}', '<b>' + V + '</b>');
      var N = '<b>' + esc(f.n) + '</b>', C = '<b>' + esc(f.c || f.n) + '</b>';
      switch (f.g) {
        case 'ing26': return f.tot ? 'Para 2026, la Ley de Ingresos autoriza a la Federación a recibir <b>' + V + '</b> en total.' :
          f.sub && !f.pad ? 'Para 2026, en la Ley de Ingresos, ' + N + ' suman <b>' + V + '</b>.' : 'Para 2026, la Ley de Ingresos espera recibir <b>' + V + '</b> por ' + C + (f.c && f.c !== f.n ? ' (' + esc(f.n) + ')' : '') + (f.pad ? ', dentro del renglón ' + esc(f.pad.replace('ing-', '').toUpperCase() === 'IEPS' ? 'del IEPS' : 'de ' + (NF.filter(function (x) { return x.id === f.pad; })[0] || {}).n) : '') + '.';
        case 'egr26': return f.tot ? 'Para 2026, la Cámara de Diputados aprobó un gasto neto total de <b>' + V + '</b>.' :
          f.sub && !f.pad ? 'Para 2026, ' + (/^Gastos/.test(f.n) ? 'los ' : 'el ') + '<b>' + esc(f.n.charAt(0).toLowerCase() + f.n.slice(1)) + '</b> ' + (/^Gastos/.test(f.n) ? 'suman' : 'suma') + ' <b>' + V + '</b>.' : 'Para 2026, el Presupuesto de Egresos asigna <b>' + V + '</b> a ' + N + '.';
        case 'fed26': return f.tot ? 'Para 2026, el gasto federalizado —lo que baja a estados y municipios— es de <b>' + V + '</b>.' : 'Para 2026, por ' + N + ' se transfieren <b>' + V + '</b> a estados y municipios.';
        case 'mun26': return f.tot ? 'Para 2026, el Presupuesto etiqueta <b>' + V + '</b> como recursos de origen municipal.' : 'Para 2026, el ' + C + ' reparte <b>' + V + '</b> entre los municipios.';
        case 'ramo26': return 'Para 2026, el Presupuesto le aprobó <b>' + V + '</b> ' + aDe(f) + '.';
        case 'cp25': return 'En 2025, ' + aDe(f).replace(/^a la /, 'la ').replace(/^al /, 'el ').replace(/^a los /, 'los ').replace(/^a /, '') + ' ejerció <b>' + V + '</b>, según la Cuenta Pública.';
        case 'pq27': return (f.y === '2027' ? 'Para 2027, el Paquete Económico propone: ' : 'En lo aprobado para 2026: ') + N + ', <b>' + V + '</b>' + (f.pib != null ? ' (' + n(f.pib, 1) + ' % del PIB)' : '') + '.' + (f.v < 0 ? ' El signo menos indica faltante.' : '');
        case 'func27': return 'Para 2027, el Paquete Económico propone <b>' + V + '</b> para ' + N + '. En 2026 se aprobaron <b>' + nv(f, f.v26) + '</b>; según los Criterios, el cambio es de <b>' + (f['var'] > 0 ? '+' : '') + n(f['var'], 1) + ' % real</b>.';
        case 'soc27': case 'inv27': return 'Para 2027, el Paquete Económico propone <b>' + V + '</b> para ' + N + '.';
        case 'colchon': return N + ': <b>' + V + '</b>' + (f.pib != null ? ' (' + n(f.pib, 1) + ' % del PIB)' : '') + (f.tipo === 'contingente' ? '. Es un pasivo contingente: no cuenta como deuda pública, pero puede volverse gasto.' : '.');
        case 'munp': return 'En 2024, los municipios del país reportaron ' + C + ': <b>' + V + '</b>, según el INEGI.';
        case 'mir24': return 'En 2024, el programa ' + N + ' ejerció <b>' + V + '</b>, según la Cuenta Pública.';
        case 'cf24': return 'En 2024, según la Cuenta Pública, el Gobierno Federal registró en ' + N + ' <b>' + V + '</b>.';
      }
      return N + ': <b>' + V + '</b>.';
    }
    function numResp(f, t, porHab) {
      var PAD = f.pad ? NF.filter(function (x) { return x.id === f.pad; })[0] : null;
      var G = PAD ? { n: 'lo que deja ' + (PAD.c || PAD.n), tot: PAD.v } : NG[f.g] || {}, V = nv(f), fu = [{ que: f.n + ' (' + f.y + ')', e: f.e, fu: f.fu, op: f.op }], h = '', ops = [];
      var pide = PCT.test(t) || /de cada (peso|\$? ?100|cien)/.test(t);
      if (PAD && PAD.gn) G = { n: PAD.gn, tot: PAD.v };
      var p = !f.tot && G.tot && f.u !== 'mdd' && !f.un && !f.st && f.v > 0 && f.v <= G.tot ? f.v / G.tot * 100 : null;
      if (PAD && f.g === 'egr26') G.n = 'el ' + PAD.n.charAt(0).toLowerCase() + PAD.n.slice(1);
      if (PAD && f.g === 'fed26') G.n = 'el ' + (PAD.c || PAD.n);
      if (p != null && pide) h += '<p>De cada $100 ' + esc(del(G.n)) + ', <b>$' + n(p, 2) + '</b> son ' + esc(f.c || f.n) + '.</p>';
      h += '<p>' + numFrase(f, V);
      if (p != null && !pide) h += ' Es el <b>' + n(p, p < 1 ? 2 : 1) + ' %</b> ' + esc(del(G.n)) + ' (' + mdp(G.tot) + ').';
      if (p != null) ops.push(mdp(f.v) + ' ÷ ' + mdp(G.tot) + ' × 100');
      var dia = !f.st && !f.un && f.u !== 'mdd' && f.v > 365 ? f.v / 365 : null;
      if (dia && !porHab) { h += ' Son unos <b>' + mdp(dia) + ' al día</b>.'; ops.push(mdp(f.v) + ' ÷ 365'); }
      if (porHab && NU.pob && f.u !== 'mdd' && !f.un && f.v > 0) {
        var ph = f.v * 1e6 / NU.pob.v;
        h += ' Repartido entre los ' + n(NU.pob.v) + ' habitantes, son <b>$' + n(ph, ph < 100 ? 2 : 0) + ' por persona</b>.';
        ops.push(mdp(f.v) + ' ÷ ' + n(NU.pob.v) + ' habitantes (CONAPO)');
        fu.push({ que: 'Población a mitad de 2026', e: 'derivado', fu: NU.pob.fu });
      }
      h += '</p>';
      /* En qué se va, por capítulo de gasto, y lo pagado en lo que va de 2026. */
      var CAPS = [['1000', /sueldo|nomina|salario|personal|plaza|servicios personales/], ['2000', /material|suministro/], ['3000', /servicios generales|renta|viatic|asesori|luz|telefon/],
        ['4000', /transferencia|subsidio|ayuda/], ['5000', /bienes muebles|mueble|vehicul|equipo/], ['6000', /inversion publica|obra/]];
      if (f.caps) {
        var tc = f.caps.l.reduce(function (s, x) { return s + x[2]; }, 0), cq = CAPS.filter(function (z) { return z[1].test(t); })[0];
        var cx = cq ? f.caps.l.filter(function (x) { return x[0] === cq[0]; })[0] : null;
        if (cx) h = '<p>En ' + f.caps.y + ' (' + f.caps.et + '), ' + aDe(f).replace(/^a la /, 'la ').replace(/^al /, 'el ').replace(/^a los /, 'los ').replace(/^a /, '') + ' destina a <b>' + esc(cx[1]) + '</b> (capítulo ' + cx[0] + ') <b>' + mdp(cx[2]) + '</b>: el <b>' + n(cx[2] / tc * 100, 1) + ' %</b> de su gasto por capítulo.</p>' + h;
        else if (/capitulo|en que (gasta|se va|se le va)|desglose|en que lo gasta/.test(t)) h += '<p>Por capítulo de gasto (' + f.caps.y + ', ' + f.caps.et + '):</p><ul class="pa-lista">' + f.caps.l.map(function (x) { return '<li>' + esc(x[1]) + ': <b>' + mdp(x[2]) + '</b> (' + n(x[2] / tc * 100, 1) + ' %)</li>'; }).join('') + '</ul>';
        if (cx || /capitulo|en que (gasta|se va|se le va)|desglose|en que lo gasta/.test(t)) { fu.push({ que: 'Por capítulo de gasto (' + f.caps.y + ')', e: 'oficial', fu: f.caps.fu }); ops.push('cada capítulo ÷ ' + mdp(tc) + ' × 100'); }
      }
      if (f.av) {
        var ab = f.av.mod || f.v;
        h += '<p>Al ' + esc(f.av.corte) + ' había pagado <b>' + mdp(f.av.v) + '</b>, el ' + n(f.av.v / ab * 100, 1) + ' % de lo ' + (f.av.mod ? 'modificado (' + mdp(f.av.mod) + ')' : 'aprobado') + '.</p>';
        fu.push({ que: 'Pagado al ' + f.av.corte, e: 'oficial', fu: f.av.fu }); ops.push(mdp(f.av.v) + ' ÷ ' + mdp(ab) + ' × 100');
      }
      /* El mismo dinero en otro año: lo aprobado, lo propuesto o lo ejercido. */
      var her = f.sx ? [] : (NPAR[f.par] || []).filter(function (x) { return x !== f && x.y !== f.y && x.g !== 'func27'; });
      var fn = f.g === 'egr26' ? (NPAR[f.id] || []).filter(function (x) { return x.g === 'func27'; })[0] : null;
      her.forEach(function (x) {
        if (x.fr) { h += '<p>' + numFrase(x, nv(x)) + '</p>'; fu.push({ que: x.n + ' (' + x.y + ')', e: x.e, fu: x.fu }); if (x.op) ops.push(x.op); return; }
        h += '<p>' + (x.y === '2025' ? 'En 2025 ejerció <b>' + nv(x) + '</b> (Cuenta Pública).' : x.y === '2027' ? 'Para 2027, el Paquete Económico propone <b>' + nv(x) + '</b>' + (x.pib != null ? ' (' + n(x.pib, 1) + ' % del PIB)' : '') + '.' :
          x.y === '2026' && x.g === 'ramo26' ? 'Para 2026 le aprobaron <b>' + nv(x) + '</b>.' : 'En lo aprobado para 2026: <b>' + nv(x) + '</b>' + (x.pib != null ? ' (' + n(x.pib, 1) + ' % del PIB)' : '') + '.') + '</p>';
        fu.push({ que: x.n + ' (' + x.y + ')', e: x.e, fu: x.fu });
      });
      if (fn) { h += '<p>Para 2027, el Paquete Económico propone <b>' + nv(fn) + '</b> (' + (fn['var'] > 0 ? '+' : '') + n(fn['var'], 1) + ' % real, según los Criterios).</p>'; fu.push({ que: fn.n + ' (2027)', e: fn.e, fu: fn.fu }); }
      /* Los totales: la otra medida oficial que también circula. */
      var cg = NU.cgpe || {};
      if (f.id === 'egr-total' && cg.gasto) {
        h += '<p class="pa-chico">Ojo: Hacienda también publica el <b>gasto neto pagado</b> (lo que de verdad sale de caja): ' + mdp(cg.gasto.m26) + ' en 2026 y ' + mdp(cg.gasto.m) + ' propuestos para 2027. Son dos medidas oficiales distintas; por eso a veces leerás una u otra.</p>';
        fu.push({ que: 'Gasto neto pagado', e: 'oficial', fu: CGPE_FU() });
      }
      if (f.id === 'ing-total' && cg.ing) {
        var deu = NF.filter(function (x) { return x.id === 'ing-deuda'; })[0];
        if (deu) { h += '<p>De eso, <b>' + mdp(deu.v) + '</b> son deuda nueva (el ' + n(deu.v / f.v * 100, 1) + ' %): la Ley la cuenta como ingreso y por eso cuadra con el gasto.</p>'; ops.push(mdp(deu.v) + ' ÷ ' + mdp(f.v) + ' × 100'); }
        h += '<p class="pa-chico">Sin la deuda, los <b>ingresos presupuestarios</b> de 2026 son ' + mdp(cg.ing.m26) + '; para 2027 se proponen ' + mdp(cg.ing.m) + '.</p>';
        fu.push({ que: 'Ingresos presupuestarios', e: 'oficial', fu: CGPE_FU() });
      }
      if (f.d) h += '<p class="pa-chico">' + esc(corto(f.d, 320)) + (f.ley ? ' 📖 ' + esc(f.ley) + '.' : '') + '</p>';
      if (f.op && f.e === 'derivado') fu[0].op = f.op;
      if (ops.length) fu.push({ que: 'Porcentaje, al día o por persona', e: 'derivado', op: ops.join('; ') });
      var otros = NF.filter(function (x) { return x.g === f.g && x !== f && !x.tot && x.alp.length && (f.pad ? x.pad === f.pad : f.sub ? x.sub && !x.pad && x.d === f.d : !x.sub); }).sort(function (a, b) { return b.v - a.v; }).slice(0, 2);
      var sug = otros.map(function (x) { return '¿Y ' + (x.c || x.n).replace(/ \((Cuenta Pública )?\d{4}\)$/, '') + '?'; });
      if (f.sx && f.par) {
        var ya = (NPAR[f.par] || []).map(function (x) { return x.y; }).filter(function (y) { return y < f.y; }).sort();
        if (ya.length) sug.unshift('¿Y en ' + ya[ya.length - 1] + '?');
      }
      if ((NG[f.g] || {}).sug) sug = NG[f.g].sug.filter(function (x) { return plano(x) !== plano(t); }).slice(0, 3);
      else if (G.lista) sug.push(f.g === 'ing26' ? '¿Qué impuesto deja más?' : f.g === 'ramo26' ? '¿Qué dependencias tienen más presupuesto?' : f.g === 'egr26' ? '¿En qué se gasta el presupuesto?' : '¿Cuáles son todos?');
      return { html: h, fu: fu, ci: [{ v: V, etq: f.n + ' (' + f.y + ')', e: f.e }], val: f.u === 'mdd' || f.un || f.vt ? null : { v: f.v, u: 'mdp', dia: dia },
        tit: f.n + ' (' + f.y + ')', ir: f.ir, sug: sug };
    }
    function CGPE_FU() { var x = NF.filter(function (z) { return z.g === 'pq27'; })[0]; return x ? x.fu : null; }
    function numGrupo(t) {
      if (/ramo 16|presupuesto ambiental|sector ambiental|organos? (del sector )?ambiental|organos? de (la )?semarnat/.test(t)) return ['r16'];
      if (/costo ambiental|dano ambiental|ctada|deterioro ambiental|cuenta ambiental|costos ambientales/.test(t)) return ['amb24'];
      if (/aclarar|asf|auditoria superior/.test(t) && /renglones|dependencias|temas|diez/.test(t)) return ['asfs'];
      if (/aclarar|asf|auditoria superior/.test(t) && /concentra|grupo|sector|rubro/.test(t)) return ['asfg'];
      if (/programas? sociales?|apoyos sociales|programas del bienestar|becas y pensiones/.test(t)) return ['soc27'];
      if (/\b(obras|proyectos|inversion)\b/.test(t) && /2027|prioritari|paquete|propon/.test(t)) return ['inv27'];
      if (/tres (grandes )?presupuestos|presupuesto (social|nacional)\b.*presupuesto/.test(t)) return ['tres26'];
      if (/finalidad|funcional/.test(t)) return ['func27'];
      if (/federalizado/.test(t)) return ['fed26'];
      if (/\bimpuestos?\b/.test(t)) return ['ing26', 'Impuestos'];
      if (/\bramos?\b|secretarias?\b|dependencias?\b|instituciones\b/.test(t)) return ['ramo26'];
      if (/ingreso|origen|de donde (sale|viene|vienen|entra)|recaud|entra el dinero/.test(t)) return ['ing26'];
      if (/gast|egreso|presupuesto|en que se (gasta|va|van)|a donde va/.test(t)) return ['egr26'];
      return null;
    }
    function numLista(gr, dir, cuantos) {
      var G = NG[gr[0]] || {};
      var l = NF.filter(function (x) { return x.g === gr[0] && (G.li ? x.li : !x.sub && !x.tot) && (!gr[1] || x.sg === gr[1]); }).sort(function (a, b) { return dir === 'min' ? a.v - b.v : b.v - a.v; });
      if (!l.length) return null;
      var top = cuantos > 1 ? l.slice(0, cuantos) : l.length > 12 ? l.slice(0, 10) : l;
      var tot = G.tot || null, sumaGr = gr[1] ? l.reduce(function (s, x) { return s + x.v; }, 0) : null;
      var h = '<p>' + esc(gr[1] ? 'Los impuestos de 2026, según la Ley de Ingresos' : G.lista) + (dir === 'min' ? ', de menor a mayor' : ', de mayor a menor') + ':</p><ol class="pa-lista">' +
        top.map(function (x) { return '<li><b>' + esc(x.c || x.n) + '</b>: ' + nv(x) + (tot && !x.st ? ' <span class="pa-chico">(' + n(x.v / tot * 100, 1) + ' %)</span>' : '') + '</li>'; }).join('') + '</ol>';
      if (top.length < l.length) h += '<p class="pa-chico">Son ' + l.length + ' en total; te muestro ' + top.length + '. Pregúntame por cualquiera.</p>';
      if (sumaGr) h += '<p>Juntos suman <b>' + mdp(sumaGr) + '</b>' + (tot ? ', el ' + n(sumaGr / tot * 100, 1) + ' % ' + esc(del(G.n)) : '') + '.</p>';
      else if (tot) h += '<p>El total es <b>' + mdp(tot) + '</b>.</p>';
      var fu = [{ que: G.lista || 'Lista', e: 'oficial', fu: top[0].fu }];
      if (tot) fu.push({ que: 'Porcentajes y orden', e: 'derivado', op: 'cada renglón ÷ ' + mdp(tot) + ' × 100; ordenados por monto' });
      return { html: h, fu: fu, ci: top.slice(0, 8).map(function (x) { return { v: nv(x), etq: x.c || x.n, e: x.e }; }), tit: gr[1] ? 'Los impuestos de 2026' : G.lista, ir: G.ir,
        sug: top.slice(0, 2).map(function (x) { return '¿Cuánto es ' + (x.c || x.n) + '?'; }) };
    }
    /* El Paquete Económico 2027, en corto. */
    function pqResumen() {
      var by = {}; NF.forEach(function (x) { by[x.id] = x; });
      var ids = ['pq-f-gasto', 'pq-f-ing', 'pq-f-trib', 'pq-f-balance', 'pq-f-rfsp', 'pq-f-costofin', 'pq-f-shrfsp'], li = [], fu = [];
      ids.forEach(function (k) {
        var x = by[k], y = by[k.replace('pq-', 'pq26-')];
        if (!x) return;
        li.push('<li><b>' + esc(x.n) + ':</b> ' + nv(x) + (x.pib != null ? ' (' + n(x.pib, 1) + ' % del PIB)' : '') + (y ? '; en 2026 se aprobó ' + nv(y) : '') + '.</li>');
      });
      if (!li.length) return null;
      fu.push({ que: 'Paquete Económico 2027', e: 'oficial', fu: by['pq-f-gasto'].fu });
      return { html: '<p>El Paquete Económico 2027 llegó a la Cámara de Diputados el 8 de septiembre de 2026. <b>Todavía es propuesta</b>: los diputados pueden cambiarlo. En corto, propone:</p><ul class="pa-lista">' + li.join('') + '</ul>' +
          '<p class="pa-chico">El signo menos indica faltante (déficit).</p>', fu: fu, tit: 'El Paquete Económico 2027, en corto', ir: ['numeros-paquete-2027.html', 'El Paquete Económico 2027'],
        ci: ids.filter(function (k) { return by[k]; }).map(function (k) { return { v: nv(by[k]), etq: by[k].n + ' (2027)', e: 'oficial' }; }),
        sug: ['¿Cuáles son los programas sociales?', '¿Cuánto es el déficit 2027?', '¿A cuánto va a estar el dólar en 2027?'] };
    }
    /* Las series de 1990 a 2025 (Radar hacendario). */
    function serieResp(t, anio) {
      var S = NU.serie || {}, k = ['costo_financiero', 'inversion', 'ingresos', 'gasto'].filter(function (x) { return S[x] && new RegExp(S[x].re).test(t); })[0];
      if (!k) return null;
      var x = S[k].a[anio];
      if (!x) return null;
      return { html: '<p>En <b>' + anio + '</b>, ' + esc(S[k].n) + (k === 'ingresos' ? ' sumaron' : ' sumó') + ' <b>' + mdp(x[0]) + '</b>' + (x[1] != null ? ', el <b>' + n(x[1], 1) + ' % del PIB</b>' : '') + '.</p>' +
          '<p class="pa-chico">Son pesos de ese año (sin ajustar por inflación). Para comparar años, mira el porcentaje del PIB.</p>',
        fu: [{ que: S[k].n + ' ' + anio, e: 'oficial', fu: S[k].fu }], ci: [{ v: mdp(x[0]), etq: S[k].n + ' ' + anio, e: 'oficial' }], val: { v: x[0], u: 'mdp' },
        tit: S[k].n + ' en ' + anio, ir: ['radar-hacendario.html', 'el Radar hacendario'], serie: k,
        sug: [S[k].a[anio - 10] ? '¿Y en ' + (anio - 10) + '?' : '¿Y en ' + (+anio + 5) + '?', '¿Cuánto es el presupuesto 2026?'] };
    }
    /* El marco macroeconómico del Paquete 2027 (supuestos, no pesos). */
    function marcoResp(t) {
      var m = null, ml = 0;
      (NU.marco || []).forEach(function (x) { x.al.forEach(function (a) { if (t.indexOf(' ' + a + ' ') >= 0 && a.length > ml) { m = x; ml = a.length; } }); });
      if (!m) return null;
      return { html: '<p>Para 2027, el Paquete Económico supone: <b>' + esc(m.n) + '</b>, <b>' + esc(m.p27) + '</b> (' + esc(m.u) + '). Para 2026 se aprobó con ' + esc(m.a26) + ' y el cierre estimado es ' + esc(m.e26) + '.</p>' +
          (m.nota ? '<p class="pa-chico">' + esc(m.nota) + '</p>' : '') + '<p class="pa-chico">Es un supuesto de Hacienda para calcular el presupuesto, no un pronóstico garantizado.</p>',
        fu: [{ que: 'Marco macroeconómico 2027', e: 'oficial', fu: CGPE_FU() }], ci: [{ v: m.p27 + ' ' + m.u, etq: m.n + ' (supuesto 2027)', e: 'oficial' }],
        tit: m.n + ': supuesto 2027', ir: ['numeros-paquete-2027-cifras.html', 'Las cifras del Paquete 2027'] };
    }

    /* ---------- La pestaña Datos: el peso en el tiempo, las descargas, los plazos y la lista 69-B ---------- */
    function pesoResp(t, q) {
      if (!PSO) return null;
      var R = PSO.ref, F = PSO.fx, yrs = (t.match(/\b(19[89]\d|20[0-3]\d)\b/g) || []).map(Number);
      var pasado = yrs.filter(function (y) { return PSO.inpc[y]; })[0], futuro = yrs.filter(function (y) { return y > 2027 && y <= 2032; })[0];
      var dolar = /\b(dolar|dolares|tipo de cambio)\b/.test(t), euro = /\beuros?\b/.test(t), infl = /inflacion|carestia|suben los precios|subieron los precios/.test(t);
      var maquina = (/\b(hoy|ahora|actualmente|actuales)\b/.test(t) && /\b(valen|vale|valdrian|valdria|equivalen?|serian|seria|son|alcanzan?|alcanzaria)\b/.test(t)) || /pesos (de|del) (19[89]\d|20[0-3]\d)|de (19[89]\d|20[0-3]\d) (a|en) pesos de hoy|(valen|vale|valdrian|valdria|equivalen?|serian|seria|alcanzan?) (hoy|ahora|actualmente)|en pesos de hoy|a pesos de hoy|hoy (valen|vale|equivalen?)|poder adquisitivo/.test(t);
      if (maquina && pasado) {
        var nums = (q.replace(/\b(19[89]\d|20[0-3]\d)\b/g, ' ').match(/\$?\s*\d[\d,]*(\.\d+)?\s*(mil millones|millones|millon|mil)?/g) || []).filter(function (x) { return /\d/.test(x); });
        var m = nums.length ? valor(nums[0].replace(/[$\s]/g, '').replace(/(mil millones|millones|millon|mil)$/, ''), (/(mil millones|millones|millon|mil)\s*$/.exec(nums[0]) || [])[1]) : 100;
        var hoy = m * R.inpc / PSO.inpc[pasado], usd = PSO.usd[pasado] ? m / PSO.usd[pasado] : null;
        var mm = function (v) { return v >= 1e6 ? grande(v, true) : '$' + n(v, 2); };
        return { html: '<p><b>' + mm(m) + '</b> de ' + pasado + ' equivalen hoy a <b>' + mm(hoy) + '</b> (pesos de ' + esc(R.mes) + ').' +
            (usd ? ' En dólares de ese año eran <b>US' + mm(usd) + '</b>.' : '') + '</p><p class="pa-chico">Es la misma capacidad de compra: a la cifra se le quita la inflación con el INPC. No cuenta intereses ni rendimientos.</p>',
          fu: [{ que: 'En pesos de hoy', e: 'derivado', fu: F.BX_INPC, op: mm(m) + ' × INPC de ' + R.mes + ' (' + n(R.inpc, 3) + ') ÷ INPC promedio de ' + pasado + ' (' + n(PSO.inpc[pasado], 3) + ')' }]
            .concat(usd ? [{ que: 'En dólares de ' + pasado, e: 'derivado', fu: F.BX_USD, op: mm(m) + ' ÷ ' + n(PSO.usd[pasado], 4) + ', el dólar promedio de ' + pasado }] : []),
          ci: [{ v: mm(hoy), etq: mm(m) + ' de ' + pasado + ' en pesos de hoy', e: 'derivado' }], tit: 'El peso de ' + pasado + ' en pesos de hoy',
          ir: [PSO.ir.maquina, 'La máquina del tiempo del peso'], sug: ['¿A cuánto estaba el dólar en ' + pasado + '?', '¿Cuál es la inflación?', '¿Cuánta inflación hubo con AMLO?'] };
      }
      if (/supuesto|paquete|presupuesto/.test(t)) return null;
      if (futuro && (dolar || infl)) {
        var pr = PSO.proy.filter(function (x) { return x.y === futuro; })[0];
        if (!pr) return null;
        return { html: '<p>Para ' + futuro + ', Hacienda proyecta ' + (dolar ? 'un dólar promedio de <b>$' + n(pr.usd, 1) + '</b>' : '') + (dolar && infl ? ' y ' : '') + (infl ? 'una inflación de <b>' + n(pr.infl, 1) + ' %</b> de diciembre a diciembre' : '') + '.</p>' +
            '<p class="pa-chico">' + esc(PSO.proy_aviso) + (euro ? ' ' + esc(PSO.proy_eur) : '') + '</p>',
          fu: [{ que: 'Proyección ' + futuro, e: 'oficial', fu: F.CGPE2027_MACRO }], ci: [{ v: dolar ? '$' + n(pr.usd, 1) : n(pr.infl, 1) + ' %', etq: (dolar ? 'Dólar' : 'Inflación') + ' proyectado ' + futuro, e: 'oficial' }],
          tit: 'Proyección de Hacienda para ' + futuro, ir: [PSO.ir.monedas, 'El peso frente al dólar, el euro y la inflación'] };
      }
      if (yrs.some(function (y) { return y >= 2026; })) return null;
      if ((dolar || euro) && pasado) {
        var eu = euro && PSO.eur[pasado], du = PSO.usd[pasado];
        if (euro && !eu) return { html: '<p>De ' + pasado + ' no hay cotización del euro. ' + esc(PSO.eur_antes) + '</p>', fu: [], tit: '' };
        return { html: '<p>En ' + pasado + ', ' + (euro ? 'el euro costó en promedio <b>$' + n(eu, 4) + '</b>' : 'el dólar costó en promedio <b>$' + n(du, 4) + '</b>') + ' pesos.</p>' +
            '<p class="pa-chico">Es el promedio de los doce meses de ese año que publica el Banco de México. Hoy cuesta $' + n(euro ? PSO.hoy.eur : PSO.hoy.usd, 4) + '.</p>',
          fu: [{ que: (euro ? 'Euro' : 'Dólar') + ' promedio ' + pasado, e: 'derivado', fu: euro ? F.BX_EUR : F.BX_USD, op: 'promedio de los 12 meses de ' + pasado }], tit: (euro ? 'El euro' : 'El dólar') + ' en ' + pasado,
          ci: [{ v: '$' + n(euro ? eu : du, 4), etq: (euro ? 'Euro' : 'Dólar') + ' promedio ' + pasado, e: 'derivado' }], ir: [PSO.ir.monedas, 'El peso frente al dólar, el euro y la inflación'] };
      }
      if (infl && pasado && PSO.infl[pasado] != null) {
        return { html: '<p>En ' + pasado + ', los precios subieron <b>' + n(PSO.infl[pasado], 1) + ' %</b> de diciembre a diciembre.</p>',
          fu: [{ que: 'Inflación ' + pasado, e: 'derivado', fu: F.BX_INPC, op: 'INPC de diciembre de ' + pasado + ' ÷ INPC de diciembre de ' + (pasado - 1) + ' − 1' }], tit: 'La inflación de ' + pasado,
          ci: [{ v: n(PSO.infl[pasado], 1) + ' %', etq: 'Inflación ' + pasado, e: 'derivado' }], ir: [PSO.ir.monedas, 'El peso frente al dólar, el euro y la inflación'], sug: ['¿Cuánta inflación hubo con AMLO?', '¿Cuánto valen 100 pesos de ' + pasado + ' hoy?'] };
      }
      if ((dolar || euro) && !/2027|va a estar|estar[aá]|estimad|pronostic|proyec/.test(t)) {
        return { html: '<p>Hoy (' + esc(PSO.hoy.fecha) + ') ' + (euro && !dolar ? 'un <b>euro</b> cuesta <b>$' + n(PSO.hoy.eur, 4) + '</b> y un <b>dólar</b>, <b>$' + n(PSO.hoy.usd, 4) + '</b>.' :
            'un <b>dólar</b> cuesta <b>$' + n(PSO.hoy.usd, 4) + '</b> y un <b>euro</b>, <b>$' + n(PSO.hoy.eur, 4) + '</b>.') + '</p>' +
            '<p class="pa-chico">El del dólar es el FIX que publica el Banco de México.</p>',
          fu: [{ que: 'Dólar y euro de hoy', e: 'oficial', fu: F.BX_DIARIO }], tit: 'El dólar y el euro hoy',
          ci: [{ v: '$' + n(PSO.hoy.usd, 4), etq: 'Dólar (FIX)', e: 'oficial' }, { v: '$' + n(PSO.hoy.eur, 4), etq: 'Euro', e: 'oficial' }],
          ir: [PSO.ir.monedas, 'El peso frente al dólar, el euro y la inflación'], sug: ['¿A cuánto estaba el dólar en 2000?', '¿Cuánto subió el dólar con Peña Nieto?', '¿A cuánto va a estar el dólar en 2027?'] };
      }
      if (infl && !/2027|va a estar|estimad|esperad|pronostic|proyec|supuesto/.test(t)) {
        var p26 = PSO.proy.filter(function (x) { return x.y === 2026; })[0], p27 = PSO.proy.filter(function (x) { return x.y === 2027; })[0];
        return { html: '<p>En los últimos 12 meses (a ' + esc(R.mes) + '), los precios subieron <b>' + n(R.infl12, 1) + ' %</b>.</p>' +
            (p26 ? '<p>Para todo 2026, Hacienda estima ' + n(p26.infl, 1) + ' % de diciembre a diciembre' + (p27 ? ', y ' + n(p27.infl, 1) + ' % al año desde 2027' : '') + '.</p>' : '') +
            '<p class="pa-chico">' + esc(PSO.proy_aviso) + '</p>',
          fu: [{ que: 'Inflación de 12 meses', e: 'derivado', fu: F.BX_INPC, op: 'INPC de ' + R.mes + ' (' + n(R.inpc, 3) + ') ÷ INPC de un año antes (' + n(R.inpc12, 3) + ') − 1' },
            { que: 'Lo que proyecta Hacienda', e: 'oficial', fu: F.CGPE2027_MACRO }], tit: 'La inflación hoy',
          ci: [{ v: n(R.infl12, 1) + ' %', etq: 'Inflación de 12 meses', e: 'derivado' }], ir: [PSO.ir.monedas, 'El peso frente al dólar, el euro y la inflación'],
          sug: ['¿Cuánta inflación hubo con Zedillo?', '¿Cuánto valen 1,000 pesos de 2000 hoy?', '¿Cuánto vale hoy el dólar?'] };
      }
      return null;
    }
    function leyesAmb(t) {
      var L = DT.leyes, num = (/articulo (\d+)/.exec(t) || [])[1];
      var l = num ? L.l.filter(function (x) { return new RegExp('art[ií]culo ' + num + '\\b|art[ií]culo ' + num + 'º').test(x.n); }) : [];
      if (!l.length) l = L.l;
      return { html: (l.length === 1 ? '<p><b>' + esc(l[0].n) + ':</b> ' + esc(l[0].d) + '</p>' : '<p>Las normas que aplican al medio ambiente, con su texto vigente:</p><ul class="pa-lista">' +
          l.map(function (x) { return '<li><b>' + esc(x.n) + ':</b> ' + esc(x.d) + '</li>'; }).join('') + '</ul>'),
        fu: l.slice(0, 3).map(function (x) { return { que: x.n, e: 'oficial', fu: x.fu }; }), tit: l.length === 1 ? l[0].n : 'Las leyes que aplican al medio ambiente', ir: L.ir,
        sug: ['¿Quién recoge la basura?', '¿Cuánto cuesta el daño ambiental?'] };
    }
    function quienMide(t) {
      var M = DT.mide, cl = [[/ecolog|dano|costo ambiental|pib/, 0], [/genera|residuo|manejo/, 1], [/municipio|servicio de basura|basura/, 2], [/impacto ambiental|permiso|obra|mia\b/, 3], [/presupuesto/, 4], [/transparencia|informacion|inai/, 5], [/compras|contrataciones|compranet/, 6]];
      var k = cl.filter(function (x) { return x[0].test(t); }).map(function (x) { return x[1]; })[0];
      var l = k != null ? [M.l[k]] : M.l;
      return { html: (l.length === 1 ? '<p><b>' + esc(l[0].d) + '</b>: lo mide ' + esc(l[0].q) + (l[0].e === 'cambió' ? ' (cambió con las reformas)' : '') + '. ' + esc(l[0].n) + '</p>' :
          '<p>Quién mide cada dato del medio ambiente, tras las reformas de 2024 y 2025:</p><ul class="pa-lista">' + l.map(function (x) { return '<li><b>' + esc(x.d) + ':</b> ' + esc(x.q) + (x.n ? ' <span class="pa-chico">(' + esc(x.n) + ')</span>' : '') + '</li>'; }).join('') + '</ul>') +
          (k === 0 ? '<p class="pa-chico">' + esc(M.falta[2]) + '</p>' : ''),
        fu: [], tit: 'Quién mide cada dato del medio ambiente', ir: M.ir };
    }
    function descargas(t) {
      var mun = /municipi/.test(t), l = DT.desc || [];
      return { html: '<p>' + (mun ? 'La base de los municipios (EFIPEM del INEGI, 2024) se descarga en CSV en <a href="datos-municipios.html">Base de Datos Municipal</a>; ahí mismo puedes consultar un estado sin descargar nada. ' : '') +
          'En <a href="datos-descargas.html"><b>Datos abiertos</b></a> hay ' + l.length + ' bases que se descargan en CSV y abren directo en Excel, cada una con su fuente al final del archivo:</p><ul class="pa-lista">' +
          l.map(function (x) { return '<li><b>' + esc(x.n) + '</b> <span class="pa-chico">(' + esc(x.fu) + ')</span></li>'; }).join('') + '</ul>' +
          '<p class="pa-chico">En el <a href="informes-diccionario.html">Diccionario de Datos</a> está qué significa cada columna.</p>',
        fu: [], tit: 'Las bases que puedes descargar', ir: mun ? ['datos-municipios.html', 'la Base de Datos Municipal'] : ['datos-descargas.html', 'Descarga en CSV'] };
    }
    function plazosAsf() {
      var P = DT.plazos || { l: [] };
      return { html: '<p>Los plazos que fija la ley después de que la ASF entrega sus informes:</p><ul class="pa-lista">' +
          P.l.map(function (x) { return '<li><b>' + esc(x.p) + '</b> ' + esc(x.q) + ' <span class="pa-chico">(' + esc(x.f) + ')</span></li>'; }).join('') + '</ul>',
        fu: [{ que: 'Plazos de la fiscalización', e: 'oficial', fu: P.fu }], tit: 'Los plazos de la ASF', ir: ['informes-cuenta-publica.html', 'Informes de la Cuenta Pública (ASF)'],
        sug: ['¿Cuándo sale la siguiente entrega de la ASF?', '¿Cuántos pliegos de observaciones hubo en 2024?'] };
    }
    /* ---------- El Poder Legislativo y las elecciones (23-10-2026) ---------- */
    var LEG = D.leg || null;
    var DINERO = /gasta|gastan|cuesta|cuestan|costo|presupuesto|gana|ganan|sueldo|dieta|dinero|lana|varo|millones|pesos|aprobaron|ejerci/;
    function legTema(k, extra) {
      var x = LEG.t[k];
      return { html: x.h + (extra || ''), fu: x.fu, ci: x.ci || [], tit: x.tit, ir: x.ir, sug: x.sug };
    }
    /* Si hoy el Congreso está en periodo ordinario o en receso: la fecha del navegador contra los arts. 65 y 66. */
    function hoySesion() {
      var d = new Date(), m = d.getMonth() + 1, dia = d.getDate(), md = m * 100 + dia;
      var p = md >= 901 && md <= 1215 ? 'en su <b>primer periodo ordinario</b>, que termina a más tardar el 15 de diciembre' :
        md >= 201 && md <= 430 ? 'en su <b>segundo periodo ordinario</b>, que termina a más tardar el 30 de abril' :
        'en <b>receso</b>: trabaja la Comisión Permanente';
      return '<p>Hoy, ' + d.toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' }) + ', el Congreso está ' + p + '.</p>';
    }
    function congresoLocal(e) {
      var v = LEG.cong[e.a], l = Object.keys(LEG.cong).sort(function (a, b) { return LEG.cong[b] - LEG.cong[a]; });
      var lu = l.filter(function (a) { return LEG.cong[a] > v; }).length + 1;
      return { html: '<p>El Congreso de <b>' + esc(e.n) + '</b> tenía <b>' + v + ' personas legisladoras en activo</b>, según el último censo del INEGI. ' +
          (lu === 1 ? 'Es el más grande del país.' : 'Es el lugar <b>' + lu + ' de 32</b> por tamaño.') + '</p>' +
          (e.a === 'CDMX' ? '<p class="pa-chico">El INEGI aclara que el Congreso de la Ciudad de México debe tener 66: una persona suplente tomó protesta después del corte.</p>' : ''),
        fu: [{ que: 'Personas legisladoras en activo (tabla 8)', e: 'oficial', fu: LEG.cnple }, { que: 'Lugar entre los 32 congresos', e: 'derivado', op: 'ordenamos los 32 congresos de mayor a menor', fu: LEG.cnple }],
        ci: [{ v: String(v), etq: 'legisladores del Congreso de ' + e.n, e: 'oficial' }], tit: 'Congreso de ' + e.n, ir: LEG.pag,
        sug: ['¿Cuánto gasta el Congreso de ' + e.n + '?', '¿Cuál es el congreso más grande?', '¿Cuántos diputados hay?'] };
    }
    function congresosLista(dir, cuantos) {
      var l = EDO.filter(function (e) { return LEG.cong[e.a] != null; }).sort(function (a, b) { return dir === 'min' ? LEG.cong[a.a] - LEG.cong[b.a] : LEG.cong[b.a] - LEG.cong[a.a]; }).slice(0, Math.max(cuantos, 5));
      return { html: '<p>Los congresos locales ' + (dir === 'min' ? 'más chicos' : 'más grandes') + ', por personas legisladoras en activo:</p><ol class="pa-lista">' +
          l.map(function (e) { return '<li><b>' + esc(e.n) + '</b>: ' + LEG.cong[e.a] + '</li>'; }).join('') + '</ol><p class="pa-chico">Entre los 32 suman ' + n(LEG.congTot) + '.</p>',
        fu: [{ que: 'Personas legisladoras en activo por congreso (tabla 8)', e: 'oficial', fu: LEG.cnple }], tit: 'El tamaño de los congresos locales', ir: LEG.pag,
        sug: [dir === 'min' ? '¿Cuál es el congreso más grande?' : '¿Cuál es el congreso más chico?', '¿Cuántos diputados hay?'] };
    }
    function legResp(t, es, dir, cuantos) {
      if (!LEG) return null;
      if (/cuando se (aprueba|vota|entrega|presenta|discute)|fecha (limite|para)|a mas tardar|calendario/.test(t) && /presupuesto|paquete|ley de ingresos|\bpef\b|\blif\b/.test(t)) return legTema('paquete');
      if (/(evaluar|evaluo|conocer|investigar|revisar|reviso|checar|checo|en que me fijo|como (escojo|elijo|saber)).*(candidat|aspirante)|(candidat|aspirante)s?.*(confiable|evaluar|puede ser|declaracion)|requisitos para ser (diputad|candidat)|(puede|pueden) ser candidat|deudor(es)? alimentari|topes? de (gasto|campana)/.test(t)) return legTema('candidatos');
      if (DINERO.test(t)) return null;
      var cuenta = /cuant[oa]s|numero de|integrantes|integra|tamano|grande|chico|pequeno|\bmas (diputad|legislador)|\bmenos (diputad|legislador)/;
      var local = /congresos? (local|locales|estatal|estatales|de los estados)|diputad[oa]s? locales?|legislaturas? (local|locales|estatal|estatales)|legisladores locales/.test(t);
      if (!local && !/union|federal|camara|senado/.test(t) && /congreso|legislatura/.test(t) && /mas grande|mas chico|mas pequeno|mas diputados|menos diputados/.test(t)) local = true;
      if ((local || (es.length && /congreso|diputad|legislador|legislatura|curul/.test(t))) && cuenta.test(t)) {
        if (es.length === 1) return congresoLocal(es[0]);
        if (/grande|chico|pequeno|\bmas\b|\bmenos\b|ranking|cuales/.test(t)) return congresosLista(/chico|pequeno|\bmenos\b/.test(t) ? 'min' : dir, cuantos);
        return legTema('locales');
      }
      if (/judicial|juezas?|jueces|magistrad|ministr[oa]s? de la corte/.test(t) && /eleccion|elegir|votar|vota|eligen|elige|2027|2028|cuando/.test(t)) return legTema('judicial');
      if (/reele[cg]|reelig|reelij|nepotismo/.test(t)) return legTema('reeleccion');
      if (/comision permanente/.test(t)) return legTema('permanente');
      if (/plan b|reformas? (electoral|recientes?|a la constitucion)|que cambio en la constitucion|nacionalidad unica/.test(t)) return legTema('reformas');
      if (/regidur|regidor|sindicatura|sindic[oa]s?\b|cabildo|como se integra (un|el) ayuntamiento|integracion del ayuntamiento/.test(t)) return legTema('ayuntamientos');
      if (/periodos? (ordinario|de sesiones)|cuando sesiona|sesiones del congreso|receso|esta sesionando|en sesiones|sesiona el congreso/.test(t)) return legTema('sesiones', hoySesion());
      if (/etapas? del proceso electoral|proceso electoral (paso a paso|por etapas)|como es el proceso electoral|ruta (critica|del proceso)|computos? distrital|cuando (se cuentan|cuentan) los votos|constancia de mayoria|cuando termina el proceso electoral/.test(t)) return legTema('ruta');
      if (/elecci|votacion|votar|vota\b|votamos|votan\b|jornada electoral|comicios|proceso electoral|precampa|campanas? electoral|veda electoral|urnas/.test(t) &&
          /proxim|cuando|2027|que se (elige|vota)|que vamos a votar|cuales|fecha|siguiente|viene/.test(t)) return legTema('elecciones');
      if (/plurinominal|pluris\b|representacion proporcional|mayoria relativa|primera minoria/.test(t)) return legTema('pluris');
      if (/distritos? (electoral|electorales|uninominal|uninominales|federal|federales)|cuantos distritos/.test(t) && !/local|locales/.test(t)) return legTema('diputados');
      var fed = cuenta.test(t) || /curul|escan|como se (integra|compone|forma)|integracion|composicion/.test(t);
      if (fed && /senad|camara alta/.test(t)) return legTema('senado');
      if (fed && /diputad|camara de diputados|san lazaro|camara baja|curul/.test(t)) return legTema('diputados');
      if (fed && /congreso|legislador|legislativo/.test(t)) return legTema('congreso');
      return null;
    }

    /* ---------- El Poder Judicial de la Federación (23-10-2026) ---------- */
    var JUD = D.jud || null;
    function judTema(k, antes) {
      var x = JUD.t[k];
      return { html: (antes || '') + x.h, fu: x.fu, ci: x.ci || [], tit: x.tit, ir: x.ir, sug: x.sug };
    }
    function judResp(t) {
      if (!JUD) return null;
      var pj = /judicial|judicatura|\bpjf\b|suprema corte|\bscjn\b|la corte\b|\bjuez|\bjueces|juezas?\b|magistrad|ministr[oa]s?\b/;
      if (/fideicomis/.test(t) && pj.test(t)) return judTema('fideicomisos');
      if (/haber(es)? de retiro|pension(es)? (vitalicia|de (los )?ministr)|liquidacion(es)? de (los )?(jueces|ministr|magistrad)/.test(t)) return judTema('retiro');
      if (/eleccion|elegir|elegimos|votar|vota\b|votamos|votaron|eligen|elige|eligieron|votacion|comicios|urnas/.test(t) &&
          /judicial|juez|jueces|juezas|magistrad|ministr|la corte|suprema corte/.test(t)) {
        if (/2028|proxim|siguiente|segunda|2027|cuando (sera|es|toca|va a ser|vuelve)|falta/.test(t)) return judTema('eleccion2028');
        return judTema('eleccion2025');
      }
      if (/(cuanto|cuantos).*(lleva|ha|han|llevan) (gastado|ejercido)|avance del gasto/.test(t) && /corte|scjn/.test(t)) return judTema('scjn_gasto');
      if (/en que se (va|gasta|usa)|como se reparte|a donde va/.test(t) && /poder judicial|judicatura|ramo 03/.test(t)) return judTema('presupuesto');
      if (/(gana|ganan|sueldo|sueldos).*(mas que|arriba de|tope).*(president|127)|tope (del|de los) (sueldos|127)|articulo 127|sueldos del poder judicial|tabulador del poder judicial/.test(t)) return judTema('sueldos');
      if (DINERO.test(t)) return null;
      if (/quien(es)? (preside|encabeza|dirige)|president[ea] de la (suprema )?corte|quien es (el|la) president[ea]/.test(t) && /corte|scjn|ministr/.test(t)) return judTema('corte', JUD.t.corte.lider);
      if (/quienes son (los|las) ministr|quienes (integran|forman|estan en) la (suprema )?corte|nombres? de (los|las) ministr|ministr[oa]s (actuales|electos|electas)|quien(es)? (gano|ganaron) .*corte/.test(t)) return judTema('ministros');
      if (/requisitos?|que se necesita|como (llego|llegar|puedo ser)|para ser/.test(t) && /ministr|juez|jueza|magistrad/.test(t)) return judTema('requisitos');
      if (/cuant[oa]s (ministr|integrantes)|ministr[oa]s (tiene|hay)|como (esta|se) (integra|compone|forma) la (suprema )?corte|como funciona la (suprema )?corte|salas de la corte|cuanto dura(n)? (un|una|el|la|los|las) ministr|integracion de la (suprema )?corte/.test(t)) return judTema('corte');
      if (/cuant[oa]s circuitos|circuitos judiciales|que es un circuito judicial|mapa judicial/.test(t)) return judTema('circuitos');
      if (/tribunal de disciplina|denunci\w* a (un|una|los) (juez|jueza|jueces|magistrad|ministr)|queja contra (un|una) (juez|jueza|magistrad)|quien (castiga|sanciona) a (los )?(jueces|juezas|magistrad|ministr)/.test(t)) return judTema('disciplina');
      if (/organo de administracion judicial|\boaj\b/.test(t)) return judTema('oaj');
      if (/tribunal electoral|\btepjf\b|sala superior/.test(t)) return judTema('tepjf');
      if (/consejo de la judicatura|\bcjf\b|reforma judicial|(quien|como) .*(forma|integra|compone|estructura).*poder judicial|estructura del poder judicial|organos? del poder judicial|organigrama del poder judicial|que es el poder judicial/.test(t)) return judTema('estructura');
      if (/recursos? (de|del|en el) (juicio de )?amparo|recurso de (revision|queja|reclamacion|inconformidad)|que recursos? (hay|procede|existe)|que procede contra|\b(queja|reclamacion|inconformidad) en (el )?amparo|como (impugno|recurro|apelo) (una|la|un|el) (sentencia|resolucion|suspension)/.test(t)) return judTema('recursos');
      if (/(cuando|como) (llega|sube|llego|se llega|puedo llegar|puede llegar) .*corte|facultad de atraccion|atrae (un|el|los) caso|amparo directo en revision|contradiccion de (criterios|tesis)|que casos (ve|revisa|resuelve|atiende) la (suprema )?corte/.test(t)) return judTema('llegar_corte');
      if (/medios de control|defender la constitucion|defiende la constitucion|instrumentos (para|de) (defensa|control)|control (constitucional|de (la )?constitucionalidad)/.test(t)) return judTema('medios');
      if (/(que es|en que consiste|como funciona|como (pido|presento|promuevo)) (el |un )?(juicio de )?amparo|amparo (directo|indirecto)|juicio de amparo|ampararme|me puedo amparar/.test(t)) return judTema('amparo');
      if (/acci(on|ones) de inconstitucionalidad|controversias? constitucional/.test(t)) return judTema('controversias');
      if (/jurisprudencia|declaratoria general|obliga a (todos )?los (jueces|tribunales)/.test(t)) return judTema('jurisprudencia');
      if (/(cuanto|cuando) (tarda|dura|debe tardar)|plazo (para|de)/.test(t) && /juicio|sentencia|amparo|jueces|juez/.test(t)) return judTema('plazos');
      return null;
    }

    function lista69(t) {
      var pag = B.fichas.filter(function (f) { return f.t === 'pagina' && f.ir && f.ir[0] === 'herramienta-inspector-efos.html'; })[0];
      var d = (DT.desc || []).filter(function (x) { return /69-B/.test(x.n); })[0];
      return { html: '<p>La <b>lista 69-B</b> es el listado que publica el SAT de contribuyentes que facturaron operaciones que no existieron (las llamadas «empresas fantasma» o EFOS), según el artículo 69-B del Código Fiscal de la Federación. ' +
          'Cada uno aparece como presunto, definitivo, desvirtuado o con sentencia favorable.</p><p><b>Estar en la lista no es una condena penal.</b> Puedes buscar a un proveedor en <a href="herramienta-inspector-efos.html">Lista negra del SAT</a> y descargar la lista completa en <a href="datos-descargas.html">Datos abiertos</a>.</p>',
        fu: d ? [{ que: 'Lista 69-B', e: 'oficial', fu: { tx: d.fu } }] : [], tit: 'La lista 69-B del SAT', ficha: pag, ir: ['herramienta-inspector-efos.html', 'Lista negra del SAT'],
        sug: ['¿Dónde descargo los datos?', '¿Qué es un pliego de observaciones?'] };
    }

    /* ---------- ¿Es cierto que…? El verificador de cifras (verificador.js) ---------- */
    var VER = window.AuditorVerifica && D.nota ? window.AuditorVerifica(D.nota) : null;
    var PIDE_VER = /^\s*(es cierto|es verdad|sera cierto|sera verdad|neta que|en serio que|dicen que|verifica|verificame|verificar|checa|checame|confirma|confirmame|desmiente|lei que|vi que|escuche que|me dijeron que|me contaron que|segun|es falso|es mentira|fake)\b/;
    var LIGA = /https?:\/\/[^\s]+\.[^\s]+/i;
    var VEMO = { verde: '✅', ambar: '⚠️', rojo: '❌' };
    /* La cifra que trae una afirmación, en pesos (o en %). */
    function cifraDicha(t) {
      var re = /(\$\s*)?(\d[\d,]*(?:\.\d+)?)\s*(billones|billon|mil millones|millones|millon|mdp|mil pesos|mil|pesos|%|por ciento)?/g, m, mejor = null;
      while ((m = re.exec(t))) {
        var u = m[3] || '', num = m[2].replace(/,/g, '');
        if (!u && !m[1]) continue;
        if (/^(19|20)\d\d$/.test(num) && !m[1] && u !== 'pesos') continue;
        var f = /^billon/.test(u) ? 1e12 : u === 'mil millones' ? 1e9 : /^millon|mdp/.test(u) ? 1e6 : /^mil/.test(u) ? 1e3 : 1;
        var dec = (num.split('.')[1] || '').length, antes = t.slice(Math.max(0, m.index - 26), m.index);
        var q = /(mas|cerca|alrededor|casi|aproximadamente|unos|menos|hasta|superior a|inferior a)( de)?\s*$/.exec(antes);
        mejor = { v: parseFloat(num) * f, pct: u === '%' || u === 'por ciento', tol: 0.5 * Math.pow(10, -dec) * f, bruto: m[0].trim(), calif: q ? q[1] : '' };
        break;
      }
      return mejor;
    }
    /* El mismo criterio de «Contrasta una nota» (verificador.js, juzga). */
    function juzgaDicho(c, val) {
      var ref = val.u === 'mdp' ? val.v * 1e6 : val.v, dicho = c.v;
      if (val.u === 'pct' !== c.pct) return null;
      if (val.min != null && val.min !== val.v && dicho >= val.min * 0.99 && dicho <= val.v * 1.01) return { tipo: 'verde', tit: 'Coincide con el documento', porque: 'Está dentro del rango oficial.' };
      var dif = dicho - ref, pct = ref ? dif / ref * 100 : 0, r = ref ? dicho / ref : 0, aprox = /cerca|alrededor|casi|aproximadamente|unos/.test(c.calif);
      var pt = function (x) { return Math.abs(x).toLocaleString('es-MX', { maximumFractionDigits: 1 }) + ' %'; };
      if ((Math.abs(dif) <= c.tol && Math.abs(pct) <= 10) || Math.abs(pct) <= 1) return { tipo: 'verde', tit: 'Coincide con el documento', porque: Math.abs(pct) <= 0.05 ? 'Es la misma cifra.' : 'Es un redondeo correcto (diferencia de ' + pt(pct) + ').' };
      if (/mas|superior/.test(c.calif) && ref >= dicho && ref <= dicho * 1.5) return { tipo: 'verde', tit: 'Coincide: dices «más de»', porque: 'El dato oficial sí es mayor.' };
      if (/menos|inferior|hasta/.test(c.calif) && ref <= dicho && ref >= dicho / 1.5) return { tipo: 'verde', tit: 'Coincide: pones un tope', porque: 'El dato oficial no lo rebasa.' };
      if (aprox && Math.abs(pct) <= 10) return { tipo: 'verde', tit: 'Coincide como aproximación', porque: 'Se aleja ' + pt(pct) + ' del dato oficial.' };
      if (!c.pct && (Math.abs(r / 1000 - 1) < 0.05 || Math.abs(r * 1000 - 1) < 0.05)) return { tipo: 'rojo', tit: 'Error de unidades: mil veces ' + (r > 1 ? 'más' : 'menos'), porque: 'Parece una confusión entre millones y miles de millones (o el «billion» del inglés).' };
      if (Math.abs(dif) <= c.tol) return { tipo: 'ambar', tit: 'Redondeo demasiado grueso', porque: 'Redondear así es válido, pero se aleja ' + pt(pct) + ' del dato oficial.' };
      if (Math.abs(pct) <= 10) return { tipo: 'ambar', tit: 'Se acerca, pero no es la misma cifra', porque: 'Se aleja ' + pt(pct) + '. Suele ser otro año, otra etapa (aprobado contra ejercido) o un redondeo grueso.' };
      return { tipo: 'rojo', tit: 'No coincide con el documento', porque: 'Lo que dices es ' + pt(pct) + (dif > 0 ? ' mayor' : ' menor') + ' que el dato oficial.' };
    }
    function verifica(q, t) {
      var url = (LIGA.exec(q) || [])[0];
      if (url) return { html: '<p>Para revisar una nota completa, la leo con el verificador de notas: encuentra cada cifra en pesos, la empata con su documento oficial y te da un veredicto con semáforo.</p>' +
          '<p><a class="pa-boton pa-primario" href="' + esc(D.nota.pagina + '?liga=' + encodeURIComponent(url)) + '">🔎 Verificar esta nota</a></p>' +
          '<p class="pa-chico">Si solo quieres revisar un dato, pégame la frase: «¿es cierto que…?».</p>', fu: [], tit: '', plat: 1 };
      var claim = q.replace(/^\s*[¿¡]?\s*/, '').replace(/^(es cierto|es verdad|sera cierto|sera verdad|neta|en serio|dicen|verifica(me)?|verificar|checa(me)?|confirma(me)?|desmiente|le[ií]|vi|escuch[eé]|me dijeron|me contaron|seg[uú]n|es falso|es mentira|fake)\s*(que|si|lo de|esto|esta)?\s*[:,]?\s*/i, '').replace(/[?¿]/g, '').trim();
      var ext = VER ? VER.analiza({ texto: claim, titulo: '' }) : { cifras: [] }, r = VER ? VER.conjunto(ext) : null;
      var juzgadas = ext.cifras.filter(function (c) { return c.v && c.v.tipo !== 'gris'; });
      if (juzgadas.length) {
        var fu = [], ci = [];
        var h = '<p>' + (r.clase === 'in-v-verde' ? '✅' : r.clase === 'in-v-ambar' ? '⚠️' : '❌') + ' <b>' + esc(r.tit.replace('de la nota', 'de lo que dices').replace('Las cifras', 'Las cifras')) + '.</b></p><ul class="pa-lista">' +
          juzgadas.map(function (c) {
            var o = VER.porId[c.sel];
            fu.push({ que: o.n, e: o.e, fu: { tx: o.f || 'documento', url: o.u } });
            ci.push({ v: VER.fmt(o.v), etq: o.n + (o.a ? ' (' + o.a + ')' : ''), e: o.e });
            return '<li>' + VEMO[c.v.tipo] + ' <b>' + esc(c.v.tit) + '.</b> Tú dices «' + esc(c.bruto) + '»; el documento dice <b>' + esc(VER.fmt(o.v)) + '</b> (' + esc(o.n) + (o.a ? ', ' + esc(o.a) : '') + '). ' + esc(corto(c.v.porque.replace(/La nota/g, 'Tu cifra').replace(/la nota/g, 'tu cifra'), 260)) + '</li>';
          }).join('') + '</ul>';
        var sin = ext.cifras.length - juzgadas.length;
        if (sin) h += '<p class="pa-chico">' + sin + ' cifra' + (sin > 1 ? 's' : '') + ' no tuvo con qué documento contrastarse: queda sin calificar, no cuenta como falsa.</p>';
        fu.push({ que: 'Veredicto', e: 'derivado', op: 'diferencia entre la cifra que dices y la del documento; se acepta el redondeo' });
        return { html: h, fu: fu, ci: ci, tit: 'Verificación: ' + claim.slice(0, 80), ir: [D.nota.pagina, 'el verificador de notas'] };
      }
      /* Sin cifra que contrastar: lo que dicen los datos sobre lo mismo. */
      var dentro = claim && plano(claim) !== t ? contesta(claim, true) : null;
      var dicho = cifraDicha(norm(claim).replace(/[¿?¡!]/g, ' ')), val = dentro && dentro.val;
      if (val && val.dia && /diari|al dia|por dia|cada dia/.test(t)) val = { v: val.dia, u: 'mdp' };
      if (val && val.anual && /al ano|anual|por ano|cada ano/.test(t)) val = { v: val.anual, u: 'pesos' };
      var jz = val && dicho ? juzgaDicho(dicho, val) : null;
      if (jz) {
        dentro.listo = 1;
        dentro.html = '<p>' + VEMO[jz.tipo] + ' <b>' + esc(jz.tit) + '.</b> Dices «' + esc(dicho.bruto) + '». ' + esc(jz.porque) + ' Esto es lo que dice el dato oficial:</p>' + dentro.html;
        dentro.html = dentro.html.replace('<details class="pa-dedonde">', '<p class="pa-chico">Veredicto ' + chip('derivado') + ': diferencia entre la cifra que dices y la oficial; se acepta el redondeo.</p><details class="pa-dedonde">');
        return dentro;
      }
      if (dentro) {
        dentro.listo = 1;
        dentro.html = '<p>' + (ext.cifras.length ? 'No encontré con qué documento contrastar esa cifra' : 'No hay una cifra que contrastar') + ', pero esto es lo que dicen los datos oficiales para que lo juzgues:</p>' + dentro.html;
        return dentro;
      }
      var rel = VER ? VER.relevancia({ texto: claim, titulo: '' }) : { pts: 1 };
      return { pasa: 1, claim: claim, html: '<p>Todavía no tengo un documento con qué verificar eso. No te digo que sea falso: te digo que no lo puedo comprobar.</p>' +
          (rel.pts < 2 ? '<p>Por ahora verifico cifras de finanzas públicas (presupuestos, deuda, impuestos, sueldos, auditorías) contra su documento oficial. Las noticias de otros temas entrarán cuando pueda consultar portales externos.</p>' : '') +
          '<p class="pa-chico">Lo anoté en «Lo que aún no sé» para buscar su fuente.</p>', fu: [], tit: '', sinDato: 1 };
    }

    /* ---------- Plática ---------- */
    var SUG_INICIO = ['¿Cuánto debe mi estado?', '¿Qué estado debe más?', '¿Cuánto gana un diputado?', '¿Cuánta lana le llega a Zapopan?'];
    function platica(t) {
      if (/^\s*(hola|holi|ola|buen(os|as)? (dias|tardes|noches)|buen dia|que (onda|tal|hubo|hubole|pex|pedo)|quiubo|hey|saludos|buenas)\b/.test(t) && t.trim().split(/\s+/).length <= 5)
        return { html: '<p>¡Hola! ¿Qué quieres saber del dinero público? Pregúntame como le preguntarías a un amigo: cuánto debe tu estado, cuánta lana le llega a tu municipio, cuánto gana un diputado o qué significa algún término.</p>', sug: SUG_INICIO };
      if (/^\s*(gracias|grax|muchas gracias|mil gracias|chido|perfecto|excelente|genial|ok|okay|va|vale|sale|orale|de pelos|que padre|buenisimo)\b/.test(t) && t.trim().split(/\s+/).length <= 5)
        return { html: '<p>¡Con gusto! Aquí sigo por si se te ocurre otra pregunta.</p>', sug: ['¿Qué estado recibe más por habitante?', '¿Cuánta deuda dejó AMLO?'] };
      if (/(quien eres|que eres|como te llamas|que puedes hacer|que sabes|en que me (ayudas|puedes ayudar)|como funcionas|ayuda|que te puedo preguntar|eres (un )?(bot|robot|ia|inteligencia))/.test(t))
        return { html: '<p>Soy el Auditor, el bot de Auditavisión. Contesto preguntas sobre el dinero público con los datos que la plataforma ya verificó. Por ejemplo:</p><ul class="pa-lista">' +
          '<li><b>Estados:</b> cuánto debe, cuánto recibe, cuánto por habitante, qué tanto depende de la Federación, qué le observó la ASF. También los ordeno y los comparo.</li>' +
          '<li><b>Municipios:</b> sus ingresos de 2024, predial, FORTAMUN, FAIS y qué tanto dependen de la Federación.</li>' +
          '<li><b>Sueldos:</b> cuánto ganan la presidenta, un diputado, un ministro o un juez.</li>' +
          '<li><b>Números:</b> lo que entra (ISR, IVA, IEPS…), en qué se gasta, cada ramo y dependencia, el gasto federalizado, lo que cuestan los Poderes, el Paquete 2027 y las series desde 1990.</li>' +
          '<li><b>Datos:</b> el peso frente al dólar y la inflación, cada sexenio por segundo, lo que revisó la ASF de 2019 a 2025, el daño ambiental, la basura, el presupuesto ambiental y las bases que se descargan.</li>' +
          '<li><b>El Congreso y las elecciones:</b> cuántas curules hay, los plurinominales, los periodos de sesiones, las fechas del presupuesto, las elecciones de 2027, la elección judicial, la reelección y los 32 congresos locales.</li>' +
          '<li><b>Sexenios:</b> la deuda, el gasto y las auditorías de cada administración desde 1989.</li>' +
          '<li><b>Cuentas:</b> porcentajes, diferencias y márgenes («¿cuánto es el 16 % de 2,500 millones?»).</li>' +
          '<li><b>Términos y leyes:</b> qué es un pliego de observaciones, qué es el Ramo 33, dónde encuentro algo.</li></ul>' +
          '<p>No soy una inteligencia artificial que redacta: no invento ni adivino. Si algo no lo tengo, te lo digo.</p>', sug: SUG_INICIO };
      return null;
    }

    /* ---------- La memoria de la plática ---------- */
    var ctx = {};

    /* ---------- Responder ---------- */
    var ultima = '';
    function contesta(q, crudo) {
      var t = plano(q);
      if (!crudo) ultima = q;
      var r = !crudo && platica(t);
      if (r) { r.plat = 1; return fin(r, { tipo: '' }); }
      /* «¿Es cierto que…?», una liga o un párrafo con montos: se verifica. */
      if (!crudo && (PIDE_VER.test(t) || LIGA.test(q) || (q.length > 160 && /\d/.test(q) && /peso|millon|billon|mdp/.test(t)))) {
        var vr = verifica(q, t);
        return vr.listo ? vr : fin(vr, { tipo: vr.plat || vr.sinDato || vr.pasa ? '' : 'ver' });
      }
      var sigue = /^\s*(y|e|ahora|tambien|y que tal|y en|y de|y el|y la|y los|y las|y si)\b/.test(t) || t.trim().split(/\s+/).length <= 3;

      var ES = estados(t), es = ES.e, resto = ES.resto;
      var porHab = POR_HAB.test(t);
      var dir = /\b(menos|menor|minimo|ultimo|ultimos)\b/.test(t) ? 'min' : 'max';
      var cuantos = (/\btop ?(\d+)|\blos (\d+)|\b(\d+) (estados|municipios|que)/.exec(t) || []).slice(1).filter(Boolean)[0];
      cuantos = cuantos ? Math.min(+cuantos, 32) : (/\b(los|cuales|que estados|estados que|municipios que|lista|ranking|top)\b/.test(t) ? 5 : 1);

      /* El Poder Legislativo y las elecciones: curules, sesiones, fechas y reformas. */
      /* El Poder Judicial: la Corte, los circuitos, la elección, el amparo. */
      var rj = judResp(t);
      if (rj) return fin(rj, { tipo: 'jud' });
      if (LEG && sigue && ctx.tipo === 'legcong' && es.length === 1 && !DINERO.test(t)) return fin(congresoLocal(es[0]), { tipo: 'legcong' });
      var rl = legResp(t, es, dir, cuantos);
      if (rl) return fin(rl, { tipo: rl.tit && rl.tit.indexOf('Congreso de ') === 0 ? 'legcong' : 'leg' });

      /* Los sueldos. */
      var cg = cargoDe(t);
      var gastaUnidad = /\b(gasta|gastan|destina|destinan|en sueldos|en nomina|nomina|capitulo|presupuesto)\b/.test(t) && numFila(t);
      if (gastaUnidad && !gastaUnidad.caps) gastaUnidad = null;
      if (cg && !gastaUnidad && (GANA.test(t) || sigue) && !admsDe(t.replace(/sheinbaum|claudia|la presidenta/g, '')).length) return fin(cargoResp(cg), { tipo: 'cargo', cargo: cg });
      if (/quien gana mas|quienes ganan mas|cargo (que )?gana mas|ganan mas|mejor pagad|mas ganan|sueldos mas altos/.test(t) && !es.length) return fin(cargosRanking(), { tipo: 'cargo' });

      /* Lo que la plataforma todavía no tiene: los sueldos de gobernadores y alcaldes. */
      if (/gobernador|gobernadora|alcalde|alcaldesa|presidente municipal|presidenta municipal|regidor|sindic/.test(t) && GANA.test(t)) {
        var gob = /gobernador|gobernadora/.test(t);
        return fin({ html: '<p>Todavía no tengo ' + (gob ? 'el sueldo de los gobernadores' : 'el sueldo de alcaldes, regidores y síndicos') + '. Lo fija cada ' + (gob ? 'estado en su propio presupuesto de egresos' : 'ayuntamiento en su presupuesto de egresos') + ', y la plataforma aún no integra esos documentos. Prefiero decírtelo antes que darte una cifra que no puedo respaldar.</p>' +
          '<p>Lo que sí tengo son los sueldos federales: la presidenta, las y los legisladores, la Corte y los jueces.</p>', fu: [], tit: '' }, { tipo: 'cargo' });
      }

      /* Cuántos municipios. */
      if (/cuantos municipios|mas municipios|menos municipios|numero de municipios/.test(t) && !/basura|recoleccion|servicio|agua|predial|aclarar/.test(t)) { var cm = cuentaMun(es[0], /menos/.test(t) ? 'min' : 'max'); if (cm) return fin(cm, { tipo: '' }); }

      /* Las administraciones. */
      var ads = admsDe(t);
      if (ads.length && !es.length && !(cg && GANA.test(t))) {
        var tema = admTema(t) || (sigue && ctx.tipo === 'adm' ? ctx.tema : '');
        var aSub = tema === 'seg' ? (/interes/.test(t) ? 'costo_financiero_mdp' : /invers|obra/.test(t) ? 'inversion_mdp' : /ingres|entr/.test(t) ? 'ingresos_mdp' : /gast/.test(t) ? 'gasto_mdp' : 'deuda_seg') : null;
        var aMon = /dolar/.test(t) ? 'usd' : /euro/.test(t) ? 'eur' : /pesos de hoy|de hoy|sin inflacion|reales|sumad|en total|todo el sexenio|en el sexenio|cuanto dinero/.test(t) ? 'hoy' : null;
        if (ads.length > 1) {
          var dos = ads.slice(0, 3).map(function (a) { return admResp(a, tema || 'deuda', aSub, aMon); });
          return fin({ html: dos.map(function (x) { return x.html; }).join(''), fu: [].concat.apply([], dos.map(function (x) { return x.fu; })), ci: [].concat.apply([], dos.map(function (x) { return x.ci; })),
            tit: 'Comparación de administraciones', ir: [D.expide, 'el Estado de cuenta administrativo'] }, { tipo: 'adm', tema: tema || 'deuda', adm: ads[0] });
        }
        var ra = admResp(ads[0], tema, aSub, aMon);
        ra.ir = [D.expide + '?adm=' + ads[0].id, 'su estado de cuenta completo'];
        ra.ficha = B.fichas.filter(function (f) { return f.t === 'estado' && f.tit.indexOf(ads[0].n) >= 0; })[0];
        if (tema === 'peso') ra.ir = ['radar-peso-sexenios.html', 'El peso en cada sexenio'];
        if (tema === 'seg') ra.ir = ['radar-reloj.html', 'El reloj de cada administración'];
        return fin(ra, { tipo: 'adm', tema: tema, adm: ads[0] });
      }

      /* La pestaña Datos: la lista 69-B, las descargas, los plazos de la ASF y el peso. */
      if (/\b69 ?b\b|\befos\b|lista negra del sat|empresas fantasma|factureras|operaciones (simuladas|inexistentes)/.test(t) && !/\bdonde\b/.test(t)) { var r69 = lista69(t); if (r69) return fin(r69, { tipo: '' }); }
      if (/descarg|\bcsv\b|excel|datos abiertos|bases? de datos|bajar (los )?datos/.test(t) && !es.length) return fin(descargas(t), { tipo: '' });
      if (/plazo|cuanto tiempo|cuantos dias/.test(t) && /asf|auditoria|observac|pliego|solvent|respond|aclarar|informe individual/.test(t)) return fin(plazosAsf(), { tipo: '' });
      if (!es.length) { var rp = pesoResp(t, q); if (rp) return fin(rp, { tipo: 'peso' }); }
      if (DT.leyes && /articulo|\bley\b|leyes|norma|constitucion|derecho a/.test(t) && /ambient|basura|residuo|clima|impacto ambiental|ecolog|carbono|medio ambiente/.test(t)) return fin(leyesAmb(t), { tipo: '' });
      if (DT.mide && /quien (mide|calcula|publica|lleva|cuenta)|de donde salen? (los|las|el|la) (dato|cifra)/.test(t) && /ambient|basura|residuo|ecolog|pib ecologico|presupuesto ambiental|transparencia|compras|contrataciones|impacto ambiental/.test(t)) return fin(quienMide(t), { tipo: '' });
      /* Lo que revisó la ASF en todo el país, Cuenta Pública por Cuenta Pública. */
      if (!es.length && !/\b(estados?|entidad(es)?|municipios?|alcaldias?)\b/.test(t) && !define0(t) && !municipio(resto, MUN_KW.test(t), es, false)) {
        var nfA = numFila(t);
        if (/aclarar|asf|auditoria superior/.test(t) && /donde se concentra|concentra|por grupo|por sector|en que (grupo|sector|rubro)|renglones|que dependencias|diez/.test(t)) { var gA = numGrupo(t) || ['asfg'], lA = numLista(gA, 'max', 0); if (lA) return fin(lA, { tipo: 'num', g: gA[0] }); }
        if (nfA && /^asf/.test(nfA.g) && !/^\s*(quien|como|por que|porque|para que)\b/.test(t)) return fin(numResp(nfA, t, false), { tipo: 'num', f: nfA });
      }

      /* Una dependencia federal: lo que le aprobaron. */
      var nf0 = numFila(t), dp = !es.length && !define0(t) && !(nf0 && !nf0.tot && !nf0.sut && nf0.g !== 'ramo26' && nf0.g !== 'cp25') && /presupuesto|dieron|dan|aprobaron|tiene|recibe|gasta|le toca|cuanto|lana|dinero|varo/.test(t) ? dependencia(t) : null;
      if (dp) return fin(depResp(dp), { tipo: 'dep' });

      /* El país: si no se habla de un estado ni de un sexenio. La deuda y los
         intereses van primero; el gasto y los ingresos, después de Números. */
      var nt = !es.length && nacTema(t), pideParte = PCT.test(t) || /de cada (peso|\$? ?100|cien)/.test(t);
      var ntOk = nt && (NAC.test(t) || nt === 'intereses' || nt === 'nueva' || /presupuesto (de |del )?(2026|este ano|federal)|cuanto (se )?gasta el gobierno/.test(t));
      var anioH = (/\b(199\d|20[01]\d|202[0-5])\b/.exec(t) || [])[1];
      if (ntOk && /intereses|nueva|deuda/.test(nt) && !pideParte && !anioH) { var na = nacional(nt); if (na) return fin(na, { tipo: 'nac', tema: nt }); }

      /* La pestaña Números: un renglón del ingreso, del gasto, de un ramo, del
         Paquete 2027 o de la Cuenta Pública; una lista, o un año de la serie. */
      var hayEdo = es.length || (/\b(estados?|entidad(es)?|municipios?)\b/.test(t) && RANK.test(t));
      var noCifra = /^\s*(quien|quienes|como|cuando|por que|porque|donde|para que)\b/.test(t) && !/cuant/.test(t);
      var munN = MUN_KW.test(t) && municipio(resto, true, es, false);
      if (!hayEdo && !munN && !noCifra && !/por aclarar|observac|pliego|recuper|irregular|cuantas veces/.test(t) && !define0(t)) {
        var nfila = numFila(t), anioS = (/\b(199\d|20[01]\d|202[0-5])\b/.exec(t) || [])[1], anioN = (/\b(202[4-7])\b/.exec(t) || [])[1];
        /* «¿Y en 2021?» después de una cifra con serie (la ASF, la basura). */
        var anioY = (/\b(19[89]\d|20[0-3]\d)\b/.exec(t) || [])[1], sibY = !nfila && sigue && ctx.tipo === 'num' && ctx.f && anioY ? (NPAR[ctx.f.par] || []).filter(function (x) { return x.y === anioY; })[0] : null;
        if (sibY) return fin(numResp(sibY, t, porHab), { tipo: 'num', f: sibY });
        if (!nfila && sigue && ctx.tipo === 'num' && ctx.f && (anioN || porHab || pideParte || /al dia|diario|por dia/.test(t))) {
          nfila = ctx.f;
          if (anioS && !(NPAR[nfila.par] || []).some(function (x) { return x.y === anioS; })) { var sr1 = serieResp(t + ' ' + (nfila.al || [''])[0], anioS); if (sr1) return fin(sr1, { tipo: 'num' }); }
          if (anioN && nfila.y !== anioN && nfila.par) nfila = (NPAR[nfila.par] || []).filter(function (x) { return x.y === anioN; })[0] || nfila;
          if (anioN && nfila.y !== anioN) {
            var sin = numResp(nfila, t, porHab);
            sin.html = '<p>Para ' + anioN + ' todavía no tengo esa cifra renglón por renglón' + (anioN === '2027' ? ': la iniciativa de Ley de Ingresos y el proyecto de Presupuesto 2027 aún no entran a la plataforma con ese detalle. Lo que sí tengo es el resumen del Paquete Económico (pregúntame «¿qué propone el paquete 2027?»)' : '') + '. Te doy la de ' + nfila.y + ':</p>' + sin.html;
            return fin(sin, { tipo: 'num', f: nfila });
          }
        }
        if (/paquete( economico)?( 2027)?|presupuesto (de |del )?2027|propuesta (de |del )?2027/.test(t) && /que (propone|trae|dice|contiene|hay)|resumen|en corto|de que se trata|^ *(el )?paquete( economico)?( 2027)? *$/.test(t)) { var pr = pqResumen(); if (pr) return fin(pr, { tipo: 'num' }); }
        if (!nfila && sigue && ctx.tipo === 'num' && ctx.g === 'egr26' && anioN === '2027') { var l27 = numLista(['func27'], dir, 0); if (l27) return fin(l27, { tipo: 'num', g: 'func27' }); }
        var nCuantos = +((/\btop ?(\d+)|\blos (\d+)|\blas (\d+)|\b(\d+) (impuestos|ramos|dependencias|programas|secretarias|obras|proyectos)/.exec(t) || []).slice(1).filter(Boolean)[0] || 0);
        var listaQ = NLISTA.test(t) || (RANK.test(t) && /\b(cual|cuales|que|quien|quienes)\b/.test(t)) || /\bcuant[oa]s (obras|proyectos|programas|impuestos|ramos|dependencias|secretarias)\b/.test(t) || (RANK.test(t) && (!nfila || nfila.tot || nfila.sub) && nCuantos > 0);
        if (listaQ && (!nfila || nfila.tot || nfila.sub)) { var gr = numGrupo(t); if (gr) { var nl = numLista(gr, dir, nCuantos); if (nl) return fin(nl, { tipo: 'num', g: gr[0] }); } }
        if (nfila && anioS && nfila.y !== anioS && !(NPAR[nfila.par] || []).some(function (x) { return x.y === anioS; })) { var sr0 = serieResp(t, anioS); if (sr0) return fin(sr0, { tipo: 'num' }); }
        if (nfila && !nfila.tot && (NQUIERE.test(t) || pideParte || porHab || (sigue && ctx.tipo === 'num') || (nfila.fr && /\bcual (es|fue|era)\b/.test(t)))) return fin(numResp(nfila, t, porHab), { tipo: 'num', f: nfila });
        if (anioS && !admsDe(t).length) {
          var sk = sigue && (ctx.serie || { intereses: 'interes', gasto: 'gasto', ingresos: 'ingresos' }[ctx.tema]) || '';
          var sr = serieResp(t, anioS) || (sk ? serieResp(t + ' ' + sk.replace('costo_financiero', 'interes'), anioS) : null);
          if (sr) return fin(sr, { tipo: 'num', serie: sr.serie });
        }
        var mr = /2027|supuesto|paquete|va a estar|estimad|pronostic|dolar|inflacion|petroleo|barril|cetes|crecimiento/.test(t) ? marcoResp(t) : null;
        if (mr) return fin(mr, { tipo: 'num' });
        if (nfila && nfila.tot && (/cuant|monto|cifra|billon|millon|de a cuanto|que tanto/.test(t) || pideParte || porHab)) return fin(numResp(nfila, t, porHab), { tipo: 'num', f: nfila });
      }
      if (ntOk) { var na2 = nacional(nt); if (na2) return fin(na2, { tipo: 'nac', tema: nt }); }

      /* La calculadora: solo si no se habla de un estado o un municipio. */
      if (!es.length && /\d/.test(t)) { var c = calcula(q); if (c) return fin(c, { tipo: 'calc' }); }

      /* «¿Qué es…?»: eso lo contesta el glosario (la búsqueda de asistente.js). */
      var define = /^\s*(que|q|k) (es|son|significa|significan|quiere decir)\b|que significa|definicion de|\bexplica(me)? (que|el|la|los|las|un|una)\b|a que se refiere/.test(t);
      var pideOrden = RANK.test(t) && /\b(el|la|los|las) que\b|\bcual|\bquien|que estados?\b|que municipios?\b|\b(estados|municipios) que\b|\btop\b|ranking|\blista\b|lugares/.test(t);

      /* Los municipios. */
      var quiereMun = MUN_KW.test(t);
      var mm = !define && (quiereMun || !es.length) ? municipio(resto, quiereMun, es, pideOrden || /cuales|que municipios/.test(t)) : null;
      if (!mm && !es.length && ctx.tipo === 'mun' && ctx.mun && sigue && !pideOrden && metrica(t, MET_MUN)) mm = { m: ctx.mun, otros: [] };
      /* «Zapopan, Jalisco»: un municipio de ese mismo estado cuenta aunque no se diga «municipio» (24-10-2026). */
      if (!mm && !define && !quiereMun && es.length === 1 && !pideOrden) { var me = municipio(resto, false, es, false); if (me && me.m.a === es[0].a) mm = me; }
      if (mm || (quiereMun && (pideOrden || /cuales|que municipios|municipios (de|del) .* (mas|menos)/.test(t)))) {
        var km = metrica(t, MET_MUN) || (sigue && ctx.tipo === 'mun' ? ctx.met : '');
        if (!mm) return fin(conLiga(munRanking(km, dir, cuantos, es[0]), 'numeros-baja-al-territorio.html', 'Baja al territorio'), { tipo: 'mun', met: km });
        var rm = munMet(mm.m, km, mm.otros);
        rm.ir = ['herramienta-inspector-entes.html#ente=municipal:' + mm.m.cve, 'su ficha técnica en el Auditor de entes públicos'];
        rm.ficha = B.fichas.filter(function (f) { return f.t === 'municipio' && f.ir[0].slice(-5) === mm.m.cve; })[0];
        return fin(rm, { tipo: 'mun', met: km, mun: mm.m });
      }
      if (define && !es.length) return null;

      /* El congreso de un estado (INEGI, Censo de Poderes Legislativos). */
      var CG = NU.congresos;
      if (CG && es.length === 1 && /congreso|legislatura|diputados locales|diputadas locales|poder legislativo/.test(t) && !GANA.test(t)) {
        var cgl = Object.keys(CG.v).sort(function (a, b) { return CG.v[b] - CG.v[a]; }), cgn = cgl.filter(function (x) { return plano(x) === plano(es[0].n) || (es[0].a === 'MEX' && /mexico/.test(plano(x)) && !/ciudad/.test(plano(x))); })[0];
        if (cgn) return fin({ html: '<p>En ' + CG.y + ', el Congreso de <b>' + esc(es[0].n) + '</b> ejerció <b>' + mdp(CG.v[cgn]) + '</b>. Es el lugar <b>' + (cgl.indexOf(cgn) + 1) + ' de ' + cgl.length + '</b> entre los congresos estatales.</p>',
          fu: [{ que: 'Gasto ejercido del congreso estatal ' + CG.y, e: 'oficial', fu: CG.fu }, { que: 'Lugar', e: 'derivado', op: 'ordenamos los congresos de mayor a menor gasto' }],
          ci: [{ v: mdp(CG.v[cgn]), etq: 'Congreso de ' + es[0].n + ' (' + CG.y + ')', e: 'oficial' }], tit: 'Congreso de ' + es[0].n + ': lo que gastó en ' + CG.y,
          ir: ['numeros-lo-que-cuestan-los-poderes.html', 'Lo que cuestan el Congreso y la Judicatura'], sug: ['¿Cuánto cuesta la Cámara de Diputados?', '¿Cuánto gana un diputado?'] }, { tipo: '' });
      }

      /* Los estados. */
      var k = metrica(t, MET_EDO);
      var sinTema = !k, sigueY = /^\s*(y|e|ahora|tambien)\b/.test(t);
      if (!k && ctx.tipo === 'edo' && ctx.met && (sigueY || es.length)) k = ctx.met;
      if (!k && porHab) k = 'pc';
      if (k === 'gasto' && porHab) { k = 'pc'; porHab = false; }
      if (!es.length && ctx.tipo === 'edo' && sigue && !pideOrden && ctx.es && ctx.es.length && (!sinTema || porHab || sigueY)) es = ctx.es;
      if (es.length === 1 && /compar|contra|\bvs\b|frente a/.test(t) && ctx.tipo === 'edo' && ctx.es && ctx.es[0] && ctx.es[0] !== es[0]) es = [ctx.es[0], es[0]];
      if (!k && !es.length) return null;
      var MAPA = [D.mapa, 'el mapa del gasto federalizado'];
      var deContexto = /^\s*(y|e|ahora|tambien)\b|comparal[oa]s?\b|\by (con|contra)\b/.test(t);
      if (es.length >= 2) { k = sinTema && !deContexto ? '' : k; return fin(conLiga(compara(es, k), MAPA[0], MAPA[1]), { tipo: 'edo', met: k, es: es }); }
      if (k === 'sem' && !es.length) k = 'ild';
      if (!es.length) {
        if (!pideOrden && !TOTAL.test(t) && !/\b(estados?|entidad(es)?|estatal(es)?|gobiernos? de los estados)\b/.test(t)) return null;
        if (TOTAL.test(t) && M[k].suma && !RANK.test(t)) return fin(conLiga(total(k), MAPA[0], MAPA[1]), { tipo: 'edo', met: k });
        if (/peor/.test(t)) dir = M[k].peor || 'max';
        if (/mejor/.test(t)) dir = (M[k].peor || 'max') === 'max' ? 'min' : 'max';
        return fin(conLiga(ranking(k, dir, pideOrden || /\b(estados?|entidad(es)?)\b/.test(t) ? cuantos : 5, porHab), MAPA[0], MAPA[1]), { tipo: 'edo', met: k, es: [] });
      }
      var e = es[0];
      if (k && PCT.test(t) && M[k] && M[k].suma && !porHab) return fin(conLiga(parte(e, k), MAPA[0], MAPA[1]), { tipo: 'edo', met: k, es: es });
      var re2 = k ? edoMet(e, k, porHab) : edoResumen(e);
      re2.ir = ['herramienta-inspector-entes.html#ente=estatal:' + e.a, 'su ficha técnica en el Auditor de entes públicos'];
      re2.ficha = B.fichas.filter(function (f) { return f.t === 'entidad' && f.tit === e.n; })[0];
      re2.tit = re2.tit || e.n;
      if (!k) re2.sug = ['¿Qué lugar ocupa ' + e.n + ' en deuda?', '¿Cuánto recibe ' + e.n + ' por habitante?', 'Municipios de ' + e.n + ' que más ingresan'];
      return fin(re2, { tipo: 'edo', met: k, es: es });
    }
    function define0(t) { return /^\s*(que|q|k) (es|son|significa|significan|quiere decir)\b|que significa|definicion de/.test(t); }
    function conLiga(r, url, tx) { r.ir = [url, tx]; return r; }
    /* Cierra la respuesta: sus fuentes, su ficha (la de la plataforma o una
       armada con lo que se contestó) y la memoria para la siguiente pregunta. */
    function fin(r, nuevo) {
      if (nuevo && nuevo.tipo !== undefined && nuevo.tipo !== '') ctx = nuevo;
      var html = r.html + (r.fu && r.fu.length ? deDonde(r.fu) : '');
      var ficha = r.ficha || (r.tit && !r.calc && r.fu && r.fu.length ? {
        t: 'calculo', tit: r.tit, txt: texto(r.html), ci: r.ci || [],
        fu: r.fu.filter(function (x) { return x && x.fu && x.fu.tx; }).map(function (x) { return x.fu; }).filter(function (f, i, a) { return a.map(function (z) { return z.tx; }).indexOf(f.tx) === i; }),
        ir: r.ir || ['indice.html', 'el índice general']
      } : null);
      return { html: html, ficha: ficha, ir: r.ir, plat: r.plat, tit: r.tit, anota: r.sinDato, val: r.val, pasa: r.pasa, claim: r.claim, sug: (r.sug || sugerir(ctx)).filter(function (x) { return plano(x) !== plano(ultima); }) };
    }
    function sugerir(c) {
      if (c.tipo === 'edo' && c.es && c.es.length === 1) {
        var otro = EDO.filter(function (x) { return x !== c.es[0]; }).sort(function (a, b) { return Math.abs(a.pob - c.es[0].pob) - Math.abs(b.pob - c.es[0].pob); })[0];
        return [c.met !== 'deuda' ? '¿Y su deuda?' : '¿Y por habitante?', 'Compáralo con ' + otro.n, 'Municipios de ' + c.es[0].n + ' que más ingresan'];
      }
      if (c.tipo === 'edo' && c.met) return ['¿Y el que menos?', '¿Y por habitante?', '¿Cuánto suman todos los estados?'];
      if (c.tipo === 'mun' && c.mun) return ['¿Y su predial?', '¿Qué tanto depende de la Federación?', 'Municipios de ' + c.mun.en + ' que más ingresan'];
      if (c.tipo === 'cargo') return ['¿Quién gana más?', '¿Cuánto gana un ministro de la Corte?', '¿Cuánto gana un senador?'];
      if (c.tipo === 'adm') return ['¿Y los intereses?', '¿Y la ASF?', 'Compara AMLO con Peña Nieto'];
      if (c.tipo === 'num') return ['¿En qué se gasta el presupuesto?', '¿De dónde sale el dinero?', '¿Qué propone el Paquete 2027?'];
      return [];
    }

    /* Una respuesta con una ficha encontrada por la búsqueda: dicha en corto. */
    function deFicha(f) {
      var h, fu = [];
      if (f.t === 'glosario') {
        h = '<p><b>' + esc(f.tit) + ':</b> ' + esc(corto(f.txt, 320)) + '</p>' + (f.fu && f.fu[0] ? '<p class="pa-chico">📖 Lo dice: ' + esc(f.fu[0].tx) + '</p>' : '');
        return { html: h, ficha: f, ir: f.ir, sug: [] };
      }
      if (f.t === 'ley') {
        h = '<p><b>' + esc(f.tit) + '.</b> ' + esc(corto(f.txt, 380)) + '</p>' + (f.nota ? '<p class="pa-chico">' + esc(f.nota) + '</p>' : '');
        return { html: h + deDonde([{ que: 'Texto de la ley', e: 'oficial', fu: (f.fu || [])[0] }]), ficha: f, ir: f.ir, sug: [] };
      }
      if (f.t === 'faq') {
        h = '<p>' + esc(corto(f.txt, 460)) + '</p>';
        return { html: h + (f.fu && f.fu.length ? deDonde(f.fu.map(function (x) { return { que: 'Referencia', e: 'oficial', fu: x }; })) : ''), ficha: f, ir: f.ir, sug: [] };
      }
      if (f.t === 'pendiente') {
        h = '<p>Ese dato todavía no tiene documento oficial: <b>' + esc(f.tit) + '</b>.</p><p><b>Por qué falta:</b> ' + esc(corto(f.pend.pq, 260)) + '</p><p><b>Le toca publicarlo a:</b> ' + esc(f.pend.quien) + '. ' +
          '<a href="' + esc(f.pend.donde) + '" target="_blank" rel="noopener noreferrer">Ahí debería estar ↗</a></p>';
        return { html: h + deDonde([{ que: f.tit, e: 'pendiente', p: f.pend.id, fu: { tx: f.pend.donde_tx, url: f.pend.donde } }]), ficha: f, ir: f.ir, sug: [] };
      }
      if (f.t === 'investigacion') {
        var cv = (f.ci || []).slice(0, 4);
        h = '<p>Es una de las investigaciones de <b>Auditoría en imágenes</b>: <b>' + esc(f.tit) + '</b>.</p><p>' + esc(corto(f.txt, 360)) + '</p>' +
          (cv.length ? '<ul class="pa-lista">' + cv.map(function (c) { return '<li><b>' + esc(c.v) + '</b> · ' + esc(c.etq) + '</li>'; }).join('') + '</ul>' : '') +
          '<p>Toca <b>«Saber más»</b> y te llevo a su página: el dinero paso a paso, quién interviene y qué falta saber, con cada cifra y su fuente.' +
          (f.exp ? ' Los documentos de la Auditoría Superior están en <a href="' + esc(f.exp) + '">su expediente</a>.' : '') + '</p>';
        cv.forEach(function (c) { fu.push({ que: c.etq, e: c.e, p: c.p, fu: (f.fu || [])[0] }); });
        return { html: h + deDonde(fu), ficha: f, ir: f.ir, sug: [] };
      }
      if (f.t === 'columna' && f.cot && f.cot.length) {
        h = '<p>🔍 Lo verificamos en <b>Noticias relevantes</b>: <b>' + esc(f.tit) + '</b>.</p><p>' + esc(corto(f.txt, 360)) + '</p>' + cotejo(f, true) +
          (f.nota ? '<p class="pa-chico">⚖️ ' + esc(f.nota) + '</p>' : '') +
          '<p>Toca <b>«Saber más»</b> y te abro la columna completa; con <b>«Generar dictamen»</b> te llevas el cotejo con cada documento.</p>';
        f.cot.forEach(function (x) { fu.push({ que: x.d, e: x.r === 'pendiente' ? 'pendiente' : (x.r === 'no consta' ? 'pendiente' : 'oficial'), p: x.p, fu: x.fu }); });
        return { html: h + deDonde(fu.filter(function (x) { return x.fu && x.fu.url; })), ficha: f, ir: f.ir, sug: [] };
      }
      if (f.t === 'columna') {
        var cc = (f.ci || []).slice(0, 3);
        h = '<p>📰 En <b>Noticias relevantes</b>: <b>' + esc(f.tit) + '</b>.</p><p>' + esc(corto(f.txt, 360)) + '</p>' +
          (cc.length ? '<ul class="pa-lista">' + cc.map(function (c) { return '<li><b>' + esc(c.v) + '</b> · ' + esc(c.etq) + ' ' + chip(c.e) + '</li>'; }).join('') + '</ul>' : '') +
          (f.dc ? '<p class="pa-col-dc"><b>💡 Dato curioso:</b> ' + esc(f.dc) + '</p>' : '') +
          (f.nota ? '<p class="pa-chico">⚖️ ' + esc(f.nota) + '</p>' : '') +
          '<p>Toca <b>«Saber más»</b> y te abro la columna completa, con cada documento que la sostiene.</p>';
        cc.forEach(function (c) { fu.push({ que: c.etq, e: c.e, fu: c.fu || (f.fu || [])[0] }); });
        if (!cc.length && f.fu && f.fu[0]) fu.push({ que: 'Documento', e: 'oficial', fu: f.fu[0] });
        return { html: h + (fu.length ? deDonde(fu) : ''), ficha: f, ir: f.ir, sug: [] };
      }
      if (f.t === 'pagina' || f.t === 'seccion') {
        h = '<p>Eso lo encuentras en <a href="' + esc(f.ir[0]) + '"><b>' + esc(f.tit) + '</b></a>' + (f.t === 'seccion' ? ' (en ' + esc(f.ir[1]) + ')' : '') + '.' + (f.txt ? ' ' + esc(corto(f.txt, 240)) : '') + '</p>';
        return { html: h, ficha: f, ir: f.ir, sug: [] };
      }
      var ci = (f.ci || []).slice(0, 4);
      if (f.t === 'cifra' && ci[0]) {
        var an = /\(([^)]*)\)\.?$/.exec(f.txt);
        return { html: '<p><b>' + esc(f.tit) + ':</b> <b>' + esc(ci[0].v) + '</b>' + (an ? ' (' + esc(an[1]) + ')' : '') + '.</p>' + deDonde([{ que: f.tit, e: ci[0].e, fu: (f.fu || [])[0] }]), ficha: f, ir: f.ir, sug: [] };
      }
      h = '<p><b>' + esc(f.tit) + '.</b> ' + esc(corto(f.txt, 300)) + '</p>' +
        (ci.length ? '<ul class="pa-lista">' + ci.map(function (c) { return '<li><b>' + esc(c.v) + '</b> · ' + esc(c.etq) + '</li>'; }).join('') + '</ul>' : '');
      ci.forEach(function (c) { fu.push({ que: c.etq, e: c.e, op: c.op, fu: (f.fu || [])[0] }); });
      if (!ci.length && f.fu && f.fu[0]) fu.push({ que: 'Fuente', e: 'oficial', fu: f.fu[0] });
      return { html: h + (fu.length ? deDonde(fu) : ''), ficha: f, ir: f.ir, sug: [] };
    }

    /* Verificamos (26-10-2026): lo que circula en redes y su cotejo contra
       el documento oficial, afirmación por afirmación. */
    var RES = { 'consta': ['✅', 'Consta'], 'matiz': ['⚠️', 'Consta, con matices'], 'no consta': ['❌', 'Sin documento oficial'], 'pendiente': ['⏳', 'Pendiente'] };
    function cotejo(f, abierto) {
      if (!f.cot || !f.cot.length) return '';
      return (f.cir ? '<blockquote class="pa-cir"><b>📣 Lo que circula</b><p>«' + esc(f.cir.tx) + '»</p><small>' + esc(f.cir.q) + '</small></blockquote>' : '') +
        '<details class="pa-cot"' + (abierto ? ' open' : '') + '><summary>🔍 Cotejo, afirmación por afirmación <small>(' + f.cot.length + ')</small></summary><ol>' +
        f.cot.map(function (x) {
          var r = RES[x.r] || RES.pendiente;
          return '<li class="pa-cot-' + esc(x.r.replace(' ', '-')) + '"><p class="pa-cot-d">«' + esc(x.d) + '»</p>' +
            '<p>' + (x.r === 'pendiente' ? chip('pendiente', x.p) : '<span class="pa-cot-r">' + r[0] + ' ' + r[1] + '</span>') + ' ' + esc(x.x) + '</p>' +
            '<small>' + (x.fu.url ? '<a href="' + esc(x.fu.url) + '" target="_blank" rel="noopener noreferrer">' + esc(x.fu.tx) + ' ↗</a>' : esc(x.fu.tx)) + '</small></li>';
        }).join('') + '</ol></details>' +
        (f.sigue && f.sigue.length ? '<div class="pa-sigue"><p class="pa-mas-t">🗓️ Lo que sigue para seguir el dinero</p><ul>' + f.sigue.map(function (x) {
          return '<li><a href="' + esc(x.url) + '" target="_blank" rel="noopener noreferrer">' + esc(x.tx) + ' ↗</a></li>';
        }).join('') + '</ul></div>' : '');
    }

    return {
      cotejo: cotejo,
      contesta: function (q) { try { return contesta(q); } catch (e) { if (window.console) console.warn('AuditorCharla', e); return null; } },
      deFicha: deFicha, deDonde: deDonde, olvida: function () { ctx = {}; }, ctx: function () { return ctx; }

    };
  };
})();
