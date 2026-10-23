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
      return '<details class="pa-dedonde"><summary><span>📎 De dónde sale</span> ' +
        ['oficial', 'derivado', 'pendiente'].filter(function (e) { return est[e]; }).map(function (e) { return chip(e); }).join(' ') +
        '</summary><ul>' + li.join('') + '</ul></details>';
    }
    function texto(h) { var d = document.createElement('div'); d.innerHTML = h; return d.textContent.replace(/\s+/g, ' ').trim(); }
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
    if (MU && MU.ent) {
      (MU.campos || []).forEach(function (c, i) { MCAMPO[c] = i - 1; });
      Object.keys(MU.ent).forEach(function (ab) {
        var est = porA[ab] || porA[ab.replace('É', 'E')] || { n: ab, a: ab };
        MU.ent[ab].lista.forEach(function (r) {
          var m = { cve: MU.ent[ab].cve + r[0], n: r[1], a: est.a, en: est.n, v: r.length > 2 ? r.slice(1) : null };
          MUN.push(m);
          var k = plano(r[1]).trim(), ks = [k];
          if (/ de /.test(k) && k.split(' de ')[0].length >= 6) ks.push(k.split(' de ')[0]);
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
          if (!quiere && (COMUN.indexOf(' ' + k.replace(/^(la|el|los|las|san|santa) /, '') + ' ') >= 0 || k.length < 5)) continue;
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
    var POR_HAB = /por (habitante|persona|cabeza|cabecita)|per ?capita|a cada (quien|persona|habitante|uno)|por cada (habitante|persona)/;
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
        return { html: h, fu: fu, ci: [{ v: '$' + n(ph), etq: m.n + ' por habitante', e: 'derivado', op: fmt(v, m.u) + ' ÷ ' + n(e.pob) + ' habitantes' }], tit: e.n + ': ' + m.n + ' por habitante' };
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
      return { html: h, fu: fu, ci: [{ v: fmt(v, m.u) || e.sem, etq: m.n, e: m.e, op: m.op }], tit: e.n + ': ' + m.n };
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
      return { html: h + mas, fu: fu, tit: m.n + ', ' + m.en + ': ' + MUN_NOM[k || 'ing'], ci: [{ v: grande(mv(m, k || 'ing'), 1), etq: MUN_NOM[k || 'ing'], e: 'oficial' }] };
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
      return { html: h, fu: fu, tit: 'Cuánto gana: ' + c.n, ci: [{ v: '$' + n(c.max), etq: 'al mes, neto', e: c.e }, { v: '$' + n(c.anual), etq: 'al año, neto', e: c.ea, op: c.op }] };
    }
    function art(nom) {
      var t = nom.split(' (')[0];
      if (/^Presidenta de la Rep/.test(t)) return 'La ' + t.charAt(0).toLowerCase() + t.slice(1);
      if (/^(Presidenta|Ministra|Senadora|Diputada|Jueza|Magistrada)/.test(t)) return 'Una ' + t.charAt(0).toLowerCase() + t.slice(1).replace(/^presidenta de la república/i, 'presidenta de la República');
      return (/^(Las |Los |La |El )/.test(t) ? t : 'Un ' + t.charAt(0).toLowerCase() + t.slice(1)).replace(/^Una presidenta/, 'La presidenta');
    }
    function cargosRanking() {
      var l = (D.cargos || []).slice().sort(function (a, b) { return b.max - a.max; });
      return { html: '<p>Así quedan los sueldos mensuales netos de 2026, de mayor a menor:</p><ol class="pa-lista">' + l.map(function (c) { return '<li><b>' + esc(c.n) + '</b>: $' + n(c.max) + '</li>'; }).join('') + '</ol>',
        fu: [{ que: 'Sueldos', e: 'oficial', fu: l[0].fu }, { que: 'Orden', e: 'derivado', op: 'de mayor a menor sueldo mensual' }], tit: 'Quién gana más',
        ci: l.slice(0, 6).map(function (c) { return { v: '$' + n(c.max), etq: c.n, e: c.e }; }) };
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
    function av(a, k) { return a.v[k]; }
    function admFu(a, k) { var x = av(a, k); return x ? { que: D.admet[k].n, e: x.e, fu: x.fu, op: x.op } : null; }
    function admResp(a, tema) {
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
      if (tema === 'gasto' || !tema) { var g = v('gasto_pib'); if (g) h += '<p>El gasto neto total promedió ' + g + ' al año.</p>'; }
      if (tema === 'ingresos') { var ig = v('ingresos_pib'); if (ig) h += '<p>Con ' + nom + ', los ingresos del sector público promediaron ' + ig + ' al año.</p>'; }
      if (tema === 'inversion') { var iv = v('inversion_pib'); if (iv) h += '<p>Con ' + nom + ', la inversión física promedió ' + iv + ' al año.</p>'; }
      if (tema === 'asf' || !tema) {
        var au = v('asf_aud'), ac = v('asf_acl'), re = tema === 'asf' ? v('asf_rec') : null;
        if (au || ac) h += '<p>La ASF le practicó ' + (au || 'varias') + ' auditorías' + (ac ? ' y dejó ' + ac + ' por aclarar' : '') + (re ? '; se recuperaron ' + re : '') + '.</p>' +
          (tema === 'asf' ? '<p class="pa-ojo">Ojo: «por aclarar» no es daño comprobado; es lo que, al corte, no tenía documentos que acreditaran el gasto.</p>' : '');
      }
      if (!h) h = '<p>De ' + nom + ' no tengo ese dato en su estado de cuenta.</p>';
      if (a.curso && a.aviso) h += '<p class="pa-chico">' + esc(a.aviso) + '</p>';
      return { html: h, fu: fu, ci: ci, tit: 'Estado de cuenta de ' + a.n + (tema ? ': ' + tema : '') };
    }
    function admTema(t) {
      if (/interes|costo financiero/.test(t)) return 'intereses';
      if (/deud|debe|endeud|prest/.test(t)) return 'deuda';
      if (/inversion|obra/.test(t)) return 'inversion';
      if (/ingres|recaud|cobr/.test(t)) return 'ingresos';
      if (/gast/.test(t)) return 'gasto';
      if (/asf|aclarar|rob|auditor|corrup|desvi|transa|chingaron|clavaron/.test(t)) return 'asf';
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
      return { html: h, fu: fu, tit: 'El país: ' + tema, ficha: a.f, ir: a.f.ir,
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
        tit: nom + ': presupuesto 2026', ficha: f, ir: fed ? fed.ir : f.ir };
    }

    /* ---------- Cuántos municipios tiene cada estado ---------- */
    function cuentaMun(e, dir) {
      if (!MU) return null;
      var ab = e ? Object.keys(MU.ent).filter(function (x) { return (porA[x] || porA[x.replace('É', 'E')] || {}).a === e.a || x === e.a; })[0] : null;
      var fu = [{ que: 'Municipios', e: 'oficial', fu: { tx: 'INEGI, Catálogo Único de Claves de Áreas Geoestadísticas', url: MU.url } }];
      if (e && ab) return { html: '<p><b>' + esc(e.n) + '</b> tiene <b>' + n(MU.ent[ab].n) + ' municipios</b>' + (e.a === 'CDMX' ? ' (en la Ciudad de México se llaman alcaldías)' : '') + '. En todo el país hay ' + n(MU.catalogo) + '.</p>', fu: fu, tit: e.n + ': municipios' };
      var l = Object.keys(MU.ent).map(function (x) { return { n: (porA[x] || {}).n || x, c: MU.ent[x].n }; }).sort(function (a, b) { return dir === 'min' ? a.c - b.c : b.c - a.c; });
      return { html: '<p>En México hay <b>' + n(MU.catalogo) + ' municipios</b>. Los estados con ' + (dir === 'min' ? 'menos' : 'más') + ':</p><ol class="pa-lista">' + l.slice(0, 5).map(function (x) { return '<li><b>' + esc(x.n) + '</b>: ' + n(x.c) + '</li>'; }).join('') + '</ol>',
        fu: fu.concat([{ que: 'Orden', e: 'derivado', op: 'ordenamos los estados por número de municipios' }]), tit: 'Municipios por estado' };
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
    function contesta(q) {
      var t = plano(q);
      ultima = q;
      var r = platica(t);
      if (r) { r.plat = 1; return fin(r, { tipo: '' }); }
      var sigue = /^\s*(y|e|ahora|tambien|y que tal|y en|y de|y el|y la|y los|y las|y si)\b/.test(t) || t.trim().split(/\s+/).length <= 3;

      var ES = estados(t), es = ES.e, resto = ES.resto;
      var porHab = POR_HAB.test(t);
      var dir = /\b(menos|menor|minimo|ultimo|ultimos)\b/.test(t) ? 'min' : 'max';
      var cuantos = (/\btop ?(\d+)|\blos (\d+)|\b(\d+) (estados|municipios|que)/.exec(t) || []).slice(1).filter(Boolean)[0];
      cuantos = cuantos ? Math.min(+cuantos, 32) : (/\b(los|cuales|que estados|estados que|municipios que|lista|ranking|top)\b/.test(t) ? 5 : 1);

      /* Los sueldos. */
      var cg = cargoDe(t);
      if (cg && (GANA.test(t) || sigue) && !admsDe(t.replace(/sheinbaum|claudia|la presidenta/g, '')).length) return fin(cargoResp(cg), { tipo: 'cargo', cargo: cg });
      if (/quien gana mas|quienes ganan mas|cargo (que )?gana mas|ganan mas|mejor pagad|mas ganan|sueldos mas altos/.test(t) && !es.length) return fin(cargosRanking(), { tipo: 'cargo' });

      /* Lo que la plataforma todavía no tiene: los sueldos de gobernadores y alcaldes. */
      if (/gobernador|gobernadora|alcalde|alcaldesa|presidente municipal|presidenta municipal|regidor|sindic/.test(t) && GANA.test(t)) {
        var gob = /gobernador|gobernadora/.test(t);
        return fin({ html: '<p>Todavía no tengo ' + (gob ? 'el sueldo de los gobernadores' : 'el sueldo de alcaldes, regidores y síndicos') + '. Lo fija cada ' + (gob ? 'estado en su propio presupuesto de egresos' : 'ayuntamiento en su presupuesto de egresos') + ', y la plataforma aún no integra esos documentos. Prefiero decírtelo antes que darte una cifra que no puedo respaldar.</p>' +
          '<p>Lo que sí tengo son los sueldos federales: la presidenta, las y los legisladores, la Corte y los jueces.</p>', fu: [], tit: '' }, { tipo: 'cargo' });
      }

      /* Cuántos municipios. */
      if (/cuantos municipios|mas municipios|menos municipios|numero de municipios/.test(t)) { var cm = cuentaMun(es[0], /menos/.test(t) ? 'min' : 'max'); if (cm) return fin(cm, { tipo: '' }); }

      /* Las administraciones. */
      var ads = admsDe(t);
      if (ads.length && !es.length && !(cg && GANA.test(t))) {
        var tema = admTema(t) || (sigue && ctx.tipo === 'adm' ? ctx.tema : '');
        if (ads.length > 1) {
          var dos = ads.slice(0, 3).map(function (a) { return admResp(a, tema || 'deuda'); });
          return fin({ html: dos.map(function (x) { return x.html; }).join(''), fu: [].concat.apply([], dos.map(function (x) { return x.fu; })), ci: [].concat.apply([], dos.map(function (x) { return x.ci; })),
            tit: 'Comparación de administraciones', ir: [D.expide, 'el Estado de cuenta administrativo'] }, { tipo: 'adm', tema: tema || 'deuda', adm: ads[0] });
        }
        var ra = admResp(ads[0], tema);
        ra.ir = [D.expide + '?adm=' + ads[0].id, 'su estado de cuenta completo'];
        ra.ficha = B.fichas.filter(function (f) { return f.t === 'estado' && f.tit.indexOf(ads[0].n) >= 0; })[0];
        return fin(ra, { tipo: 'adm', tema: tema, adm: ads[0] });
      }

      /* Una dependencia federal: lo que le aprobaron. */
      var dp = !es.length && !define0(t) && /presupuesto|dieron|dan|aprobaron|tiene|recibe|gasta|le toca|cuanto|lana|dinero|varo/.test(t) ? dependencia(t) : null;
      if (dp) return fin(depResp(dp), { tipo: 'dep' });

      /* El país: si no se habla de un estado ni de un sexenio. */
      var nt = !es.length && nacTema(t);
      if (nt && (NAC.test(t) || nt === 'intereses' || nt === 'nueva' || /presupuesto (de |del )?(2026|este ano|federal)|cuanto (se )?gasta el gobierno/.test(t))) { var na = nacional(nt); if (na) return fin(na, { tipo: 'nac' }); }

      /* La calculadora: solo si no se habla de un estado o un municipio. */
      if (!es.length && /\d/.test(t)) { var c = calcula(q); if (c) return fin(c, { tipo: 'calc' }); }

      /* «¿Qué es…?»: eso lo contesta el glosario (la búsqueda de asistente.js). */
      var define = /^\s*(que|q|k) (es|son|significa|significan|quiere decir)\b|que significa|definicion de|\bexplica(me)? (que|el|la|los|las|un|una)\b|a que se refiere/.test(t);
      var pideOrden = RANK.test(t) && /\b(el|la|los|las) que\b|\bcual|\bquien|que estados?\b|que municipios?\b|\b(estados|municipios) que\b|\btop\b|ranking|\blista\b|lugares/.test(t);

      /* Los municipios. */
      var quiereMun = MUN_KW.test(t);
      var mm = !define && (quiereMun || !es.length) ? municipio(resto, quiereMun, es, pideOrden || /cuales|que municipios/.test(t)) : null;
      if (!mm && !es.length && ctx.tipo === 'mun' && ctx.mun && sigue && !pideOrden && metrica(t, MET_MUN)) mm = { m: ctx.mun, otros: [] };
      if (mm || (quiereMun && (pideOrden || /cuales|que municipios|municipios (de|del) .* (mas|menos)/.test(t)))) {
        var km = metrica(t, MET_MUN) || (sigue && ctx.tipo === 'mun' ? ctx.met : '');
        if (!mm) return fin(conLiga(munRanking(km, dir, cuantos, es[0]), 'numeros-baja-al-territorio.html', 'Baja al territorio'), { tipo: 'mun', met: km });
        var rm = munMet(mm.m, km, mm.otros);
        rm.ir = ['herramienta-inspector-entes.html#ente=municipal:' + mm.m.cve, 'su ficha técnica en el Auditor de entes públicos'];
        rm.ficha = B.fichas.filter(function (f) { return f.t === 'municipio' && f.ir[0].slice(-5) === mm.m.cve; })[0];
        return fin(rm, { tipo: 'mun', met: km, mun: mm.m });
      }
      if (define && !es.length) return null;

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
      return { html: html, ficha: ficha, ir: r.ir, plat: r.plat, sug: (r.sug || sugerir(ctx)).filter(function (x) { return plano(x) !== plano(ultima); }) };
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
      return [];
    }

    /* Una respuesta con una ficha encontrada por la búsqueda: dicha en corto. */
    function deFicha(f) {
      var h, fu = [];
      if (f.t === 'glosario') {
        h = '<p><b>' + esc(f.tit) + ':</b> ' + esc(corto(f.txt, 320)) + '</p>' + (f.fu && f.fu[0] ? '<p class="pa-chico">📖 Lo dice: ' + esc(f.fu[0].tx) + '</p>' : '');
        return { html: h, ficha: f, ir: f.ir, sug: [] };
      }
      if (f.t === 'pendiente') {
        h = '<p>Ese dato todavía no tiene documento oficial: <b>' + esc(f.tit) + '</b>.</p><p><b>Por qué falta:</b> ' + esc(corto(f.pend.pq, 260)) + '</p><p><b>Le toca publicarlo a:</b> ' + esc(f.pend.quien) + '. ' +
          '<a href="' + esc(f.pend.donde) + '" target="_blank" rel="noopener noreferrer">Ahí debería estar ↗</a></p>';
        return { html: h + deDonde([{ que: f.tit, e: 'pendiente', p: f.pend.id, fu: { tx: f.pend.donde_tx, url: f.pend.donde } }]), ficha: f, ir: f.ir, sug: [] };
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

    return {
      contesta: function (q) { try { return contesta(q); } catch (e) { if (window.console) console.warn('AuditorCharla', e); return null; } },
      deFicha: deFicha, olvida: function () { ctx = {}; }, ctx: function () { return ctx; }
    };
  };
})();
