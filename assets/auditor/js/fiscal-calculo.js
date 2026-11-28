/* El Auditor calcula al vuelo (Ola 4, entrega A, Ronda 41).
   Lee los montos de una pregunta escrita en lenguaje natural, decide qué cuenta pide y la hace con las
   fórmulas de fiscal-simulador.js (FiscalSim): aquí no hay ninguna fórmula ni ninguna cifra fiscal.
   Las tasas, las tarifas y los topes llegan en D.fis.calc.K, que herramientas/fiscal_calculo.py arma
   desde docs/fiscal-2027/; sus fundamentos y sus fuentes llegan ya escritos desde ahí.
   Todo corre en el navegador: los montos de la pregunta no se envían a ningún servidor.
   También vive aquí el anonimizador del buzón de aprendizaje: quita RFC, CURP, correos, teléfonos y
   montos antes de que una pregunta salga del navegador.
   Las expresiones van como cadenas (new RegExp) para que la prueba pueda leer los números escritos. */
(function (raiz) {
  'use strict';
  var S = raiz.FiscalSim || (typeof require === 'function' ? require('./fiscal-simulador.js') : null);
  var MESES = 12, MIL = 1e3, MILLON = 1e6, DOS = 2;

  function rx(s, f) { return new RegExp(s, f || ''); }
  function plano(q) { return String(q).normalize('NFC').toLowerCase().normalize('NFD').replace(rx('[\\u0300-\\u036f]', 'g'), '').normalize('NFC'); }
  function esc(s) { return String(s).replace(rx('[&<>"]', 'g'), function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function pesos(n) { return n.toLocaleString('es-MX', { style: 'currency', currency: 'MXN' }); }
  function pct(n) { return String(S.r2(n)) + ' %'; }

  /* ------------------------------------------------------------ los montos de un texto */
  var NUM = '\\d{1,3}(?:,\\d{3})+(?:\\.\\d+)?|\\d+(?:\\.\\d+)?';
  var MONTO = '(\\$\\s?)?(' + NUM + ')(?:\\s?(mil millones|millones|millon|mdp|mil|k)\\b)?(\\s?(?:de\\s)?(?:pesos|mxn)\\b)?(\\s?(?:%|por ciento))?';
  var ANIO = rx('^(19|20)\\d\\d$'), LARGO = rx('^\\d{4,}');
  /* Los grupos de MONTO, por su nombre. */
  var G = {};
  ['todo', 'signo', 'num', 'escala', 'pesos', 'pct'].forEach(function (k, n) { G[k] = n; });
  var ESCALA = { mil: MIL, k: MIL, millon: MILLON, millones: MILLON, mdp: MILLON, 'mil millones': MIL * MILLON };

  /* Cada monto de un texto ya en plano: dónde empieza, dónde acaba y cuánto vale.
     Cuenta como monto lo que lleva «$», «pesos», «mil» o «millones», y el número de cuatro cifras o más
     que no es un año. Un porcentaje («7 %») nunca es un monto. */
  function montos(t) {
    var out = [], re = rx(MONTO, 'g'), m;
    while ((m = re.exec(t))) {
      if (!m[0]) { re.lastIndex++; continue; }
      var crudo = m[G.num].replace(rx(',', 'g'), ''), marcado = !!(m[G.signo] || m[G.escala] || m[G.pesos]);
      var antes = m.index ? t.charAt(m.index - 1) : ' ';
      if (m[G.pct] || rx('[a-z\\d_-]').test(antes)) continue;
      if (!marcado && (!LARGO.test(crudo) || ANIO.test(crudo))) continue;
      out.push({ i: m.index, f: m.index + m[0].length, v: parseFloat(crudo) * (m[G.escala] ? ESCALA[m[G.escala]] : 1) });
    }
    return out;
  }

  /* ------------------------------------------------------------ el anonimizador del buzón */
  var DATOS = [
    ['[\\w.+-]+@[\\w-]+(?:\\.[\\w-]+)+', '[CORREO]'],
    ['(^|[^A-Za-z\\d])[A-Za-zÑñ]{4}\\d{6}[HMhm][A-Za-zÑñ]{5}[A-Za-z\\d]\\d(?![A-Za-z\\d])', '$1[CURP]'],
    ['(^|[^A-Za-z\\d])[A-Za-zÑñ&]{3,4}-?\\d{6}-?[A-Za-z\\d]{3}(?![A-Za-z\\d])', '$1[RFC]'],
    ['(^|[^\\d$,.])(?:\\+?\\d{1,3}[ .-]?)?\\(?\\d{2,3}\\)?[ .-]?\\d{3,4}[ .-]?\\d{4}(?!\\d|[,.]\\d)', '$1[TELEFONO]']
  ];
  /* Lo que sale del navegador: sin RFC, CURP, correo ni teléfono, y con cada monto cambiado por [MONTO]. */
  function anonimiza(q) {
    var s = String(q == null ? '' : q).normalize('NFC').replace(rx('\\s+', 'g'), ' ').trim();
    DATOS.forEach(function (d) { s = s.replace(rx(d[0], 'g'), d[1]); });
    var ms = montos(plano(s)), out = '', p = 0;
    ms.forEach(function (m) { out += s.slice(p, m.i) + '[MONTO]'; p = m.f; });
    return out + s.slice(p);
  }

  /* ------------------------------------------------------------ qué es cada monto */
  /* De lo más particular a lo más general: gana la primera que aparezca pegada al monto. */
  var ROLES = [
    ['retenido', 'retuv|retien|retenid|retencion'],
    ['funeral', 'funeral|funerari'],
    ['retiro', 'retiro|afore|\\bppr\\b|plan personal'],
    ['colegio', 'colegiatura|escuela|kinder|preescolar|primaria|secundaria|preparatoria|bachillerato'],
    ['deduccion', 'medic|dental|dentista|hospital|doctor|lentes|psicolog|nutriolog|seguro de gastos|hipotec|donativ|deduccion|deducible'],
    ['gasto', 'gast|compr|pagu|pago de|invert|invier|egres|costos?\\b|insumo'],
    ['ingreso', 'gan|cobr|factur|ingres|sueld|salari|vend|recib|percib|honorari|rent(?:o|a|as)\\b|nomina']
  ];
  var PEGADO = rx('^\\s*(?:de|en|por|con)\\s'), CORTE = rx('[,;.?!]| y | e | pero | mas ');
  var MES = rx('\\b(?:al mes|mensual(?:es|mente)?|cada mes|por mes)\\b'), ANO = rx('\\b(?:al ano|anual(?:es|mente)?|por ano|en el ano|del ano|este ano)\\b'), QUIN = rx('\\bquincen');

  function rolDespues(tx) {
    if (!PEGADO.test(tx)) return null;
    for (var i = 0; i < ROLES.length; i++) if (rx(ROLES[i][1]).test(tx)) return ROLES[i][0];
    return null;
  }
  function rolAntes(tx) {
    var mejor = null, donde = -1;
    ROLES.forEach(function (r) {
      var re = rx(r[1], 'g'), m;
      while ((m = re.exec(tx))) { if (m.index > donde) { donde = m.index; mejor = r[0]; } if (!m[0]) re.lastIndex++; }
    });
    return mejor;
  }
  function periodo(tx) { return QUIN.test(tx) ? 'quincena' : MES.test(tx) ? 'mes' : ANO.test(tx) ? 'ano' : null; }

  /* La pregunta leída: su texto en plano y cada monto con su papel y su periodo. */
  function lee(q) {
    var t = plano(q), ms = montos(t);
    ms.forEach(function (m, n) {
      var antes = t.slice(n ? ms[n - 1].f : 0, m.i), despues = t.slice(m.f, n + 1 < ms.length ? ms[n + 1].i : t.length);
      var frase = despues.split(CORTE)[0];
      m.rol = rolDespues(frase) || rolAntes(antes);
      m.per = periodo(frase) || periodo(antes.split(CORTE).pop());
    });
    var libre = ms.filter(function (m) { return !m.rol; })[0];
    if (libre && !ms.some(function (m) { return m.rol === 'ingreso'; })) libre.rol = 'ingreso';
    return { t: t, m: ms, per: periodo(t.replace(rx('declaracion anual|isr anual|la anual|mi anual', 'g'), ' ')) };
  }
  /* La suma de los montos de un papel, llevada al periodo que pide la cuenta. En la anual, un «al mes» dicho
     para el sueldo no se le pega a las deducciones: cada monto vale por año salvo que diga otra cosa. */
  function suma(L, roles, a, defecto) {
    var hay = false, total = 0;
    L.m.forEach(function (m) {
      if (roles.indexOf(m.rol) < 0) return;
      var per = m.per || (a === 'mes' ? L.per : null) || defecto, v = m.v;
      if (per === 'quincena') { v = v * DOS; per = 'mes'; }
      if (per !== a) v = a === 'ano' ? v * MESES : v / MESES;
      total += v; hay = true;
    });
    return hay ? S.r2(total) : null;
  }

  /* ------------------------------------------------------------ qué cuenta pide */
  var PIDE = {
    iva: rx('\\biva\\b|(?:convien|convendr).*(?:7 ?%|siete por ciento)'),
    anual: rx('declaracion anual|la anual|mi anual|saldo a (?:favor|cargo)|devuelv|devolv|devolucion|regres|retuvieron|isr retenido|deduc|gastos medicos'),
    reg: rx('regimen.*(?:convien|convendr|mejor|eleg|elij|compar)|(?:convien|convendr|mejor|compar).*regimen|(?:convien|convendr).*(?:resico|simplificado de confianza)|(?:resico|simplificado de confianza).*(?:convien|sale mejor| o | vs | contra | versus )'),
    resico: rx('resico|simplificado de confianza')
  };
  var NO = rx('predial|catastr|tenencia|municip|ayuntamiento|\\b(?:diputad|senador|ministr|president|gobernador|alcalde|funcionari)');
  var PERFIL = [
    { p: 'plataformas', s: 'hospedaje', rx: 'airbnb|hosped|booking' },
    { p: 'plataformas', s: 'transporte_y_entrega', rx: 'uber|didi|rappi|repart|chofer de plataforma|indrive' },
    { p: 'plataformas', s: 'enajenacion_y_servicios', rx: 'plataforma|mercado ?libre|amazon|aplicacion' },
    { p: 'arrendamiento', s: '', rx: 'arrend|\\brento\\b|doy en renta|rentas?\\b|inquilin|alquil' }
  ];
  function intencion(L) {
    if (!S || !L.m.length || NO.test(L.t)) return null;
    if (PIDE.iva.test(L.t)) return 'iva';
    if (PIDE.anual.test(L.t)) return 'anual';
    if (PIDE.reg.test(L.t)) return 'reg';
    if (PIDE.resico.test(L.t)) return 'resico';
    return null;
  }

  /* ------------------------------------------------------------ las respuestas */
  var AUD = '<span class="est-chip est-derivado">auditada</span>';
  function mos(v, etq) { return '<div class="pa-clave-i"><b class="pa-clave-v">' + esc(v) + '</b><span>' + etq + '</span>' + AUD + '</div>'; }
  function mosaicos(l) { return '<div class="pa-clave fc-clave" role="group" aria-label="Tu resultado">' + l.join('') + '</div>'; }
  function p(tx, clase) { return '<p' + (clase ? ' class="' + clase + '"' : '') + '>' + tx + '</p>'; }
  function rige(C) { return 'La opción ' + esc(C.K.rige) + '. ' + C.hasta; }
  function isrResico(C, x, anio, cuando) {
    if (x.isr === null) return 'En ' + cuando + ', lo que cobras al mes pasa del último renglón de la tabla mensual del RESICO.';
    return 'En ' + cuando + ', tu ISR del RESICO sería de <b>' + pesos(x.isr) + ' al mes</b> (tasa de ' + pct(x.tasa) + ' sobre lo cobrado).';
  }
  function tope(C, x, anio) {
    return x.dentro ? '' : p('Ojo: con ese ritmo cobrarías <b>' + pesos(x.ing) + '</b> al año, más que el tope del RESICO de ' + anio + ' (' + pesos(x.tope) + '): saldrías del régimen.', 'fc-ojo');
  }

  function respIva(C, L) {
    var K = C.K, c = suma(L, ['ingreso'], 'mes', 'mes'), g = suma(L, ['gasto', 'deduccion'], 'mes', 'mes');
    if (!c) return { falta: 'lo que cobras al mes, sin IVA', tema: 'sim_iva' };
    var v = S.iva(K, c, g || 0, 0), a = S.resico(K, '2026', c, 0), b = S.resico(K, '2027', c, 0), ver;
    if (v.conviene === 'opcion') ver = 'Con estos números, la opción de ' + pct(K.iva.op) + ' te haría pagar <b>' + pesos(v.dif) + ' menos de IVA al mes</b> (' + pesos(v.difA) + ' al año) que el régimen general.';
    else if (v.conviene === 'general') ver = 'Con estos números, la opción de ' + pct(K.iva.op) + ' te haría pagar <b>' + pesos(-v.dif) + ' más de IVA al mes</b> (' + pesos(-v.difA) + ' al año): te conviene más el régimen general, que sí acredita el IVA de tus gastos.';
    else ver = 'Con estos números, las dos formas de pagar el IVA dan lo mismo: estás justo en el punto de equilibrio.';
    var h = mosaicos([
      mos(v.general < 0 ? pesos(-v.general) + ' a favor' : pesos(v.general), 'IVA en el régimen general, al mes'),
      mos(pesos(v.opcion), 'IVA con la opción de ' + pct(K.iva.op) + ', al mes'),
      mos(pesos(Math.abs(v.difA)), 'diferencia al año'),
      mos(a.isr === null ? 'Fuera de la tabla' : pesos(a.isr), 'ISR del RESICO, al mes')]);
    h += p('En el régimen general trasladas ' + pesos(v.tras) + ' (' + pct(K.iva.gen) + ' de lo cobrado) y acreditas ' + pesos(v.acred) + ' de tus gastos. Tu IVA acreditable es el <b>' + pct(v.prop) +
      '</b> del que trasladas; el punto de equilibrio es <b>' + pct(v.eq) + '</b>: por debajo conviene la opción y por arriba, el régimen general.');
    h += p(isrResico(C, a, '2026', '2026') + ' ' + (b.isr === a.isr ? 'Desde 2027, con la tabla nueva, sale igual.' : isrResico(C, b, '2027', '2027')));
    h += tope(C, a, '2026');
    h += p('Lo que tomé de tu pregunta: cobras <b>' + pesos(c) + '</b> al mes, sin IVA' + (g === null ? ', y <b>no me dijiste tus gastos con IVA</b>: hice la cuenta sin gastos. Con gastos, el IVA del régimen general baja.' :
      ', y gastas <b>' + pesos(g) + '</b> al mes en compras con IVA de ' + pct(K.iva.gen) + ', antes del IVA.') + ' Supuse que no le cobras a personas morales; si lo haces, hay retenciones y el simulador las cuenta.', 'pa-chico');
    return { mod: 'iva', x: { iva: v, a: a, b: b }, args: { c: c, g: g }, ver: ver + ' ' + rige(C), html: h };
  }

  function respResico(C, L) {
    var K = C.K, mensual = !L.m.some(function (m) { return m.rol === 'ingreso' && (m.per || L.per) === 'ano'; });
    var c = suma(L, ['ingreso'], 'mes', 'mes');
    if (!c) return { falta: 'lo que cobras, al mes o al año', tema: 'resico_pf' };
    var a = S.resico(K, '2026', c, 0), b = S.resico(K, '2027', c, 0), h, ver;
    var anualTx = function (x, cuando) {
      return x.isrA === null ? 'En ' + cuando + ', ese ingreso pasa del último renglón de la tabla anual del RESICO.'
        : 'En ' + cuando + ', con la tabla anual: <b>' + pesos(x.isrA) + '</b> de ISR sobre ' + pesos(x.ing) + ' cobrados en el año (tasa de ' + pct(x.tasaA) + ').';
    };
    if (mensual) {
      h = mosaicos([
        mos(a.isr === null ? 'Fuera de la tabla' : pesos(a.isr), 'ISR al mes en 2026'),
        mos(b.isr === null ? 'Fuera de la tabla' : pesos(b.isr), 'ISR al mes desde 2027'),
        mos(pesos(a.ing), 'lo que cobrarías en el año'),
        mos(a.isrA === null ? 'Fuera de la tabla' : pesos(a.isrA), 'ISR del año, tabla anual de 2026')]);
      ver = isrResico(C, a, '2026', '2026') + ' ' + (b.isr === a.isr ? 'Desde 2027, con la tabla nueva, sale igual.' : isrResico(C, b, '2027', '2027'));
      h += p(anualTx(a, '2026') + ' ' + (b.isrA === a.isrA ? '' : anualTx(b, '2027')));
    } else {
      h = mosaicos([
        mos(a.isrA === null ? 'Fuera de la tabla' : pesos(a.isrA), 'ISR del año en 2026'),
        mos(b.isrA === null ? 'Fuera de la tabla' : pesos(b.isrA), 'ISR del año desde 2027')]);
      ver = anualTx(a, '2026') + ' ' + (b.isrA === a.isrA ? 'Desde 2027, con la tabla nueva, sale igual.' : anualTx(b, '2027'));
    }
    h += tope(C, a, '2026') + (!a.dentro && b.dentro ? p('Desde 2027 el tope sube a ' + pesos(b.tope) + ', y con ese ingreso sí cabrías. Esto ' + esc(K.rige) + '.') : '');
    h += p('En el RESICO la tasa se aplica a todo lo cobrado, sin deducciones. Lo que tomé de tu pregunta: cobras <b>' + pesos(mensual ? c : a.ing) + '</b> ' + (mensual ? 'al mes' : 'al año') +
      ', sin IVA, y supuse que no te retienen personas morales. Lo de 2027 ' + esc(K.rige) + '. ' + C.hasta, 'pa-chico');
    return { mod: 'resico', x: { a: a, b: b }, args: { c: c, mensual: mensual }, ver: ver, html: h };
  }

  function respAnual(C, L) {
    var K = C.K, i = suma(L, ['ingreso'], 'ano', 'ano'), ret = suma(L, ['retenido'], 'ano', 'ano');
    var g = suma(L, ['deduccion', 'gasto'], 'ano', 'ano') || 0, f = suma(L, ['funeral'], 'ano', 'ano') || 0, ap = suma(L, ['retiro'], 'ano', 'ano') || 0;
    var col = L.m.some(function (m) { return m.rol === 'colegio'; });
    if (!i) return { falta: 'tu ingreso del año (o tu sueldo al mes)', tema: 'sim_anual' };
    var x = S.anual(K, i, ret || 0, g, f, ap, []), ob = S.obligado(K, i, 0), h, ver;
    var l = [mos(pesos(x.isr), 'ISR del año, con la tarifa anual de 2026'), mos(pesos(S.r2(x.glob + x.ret)), 'deducciones que sí cuentan'), mos(pesos(x.base), 'base del impuesto')];
    if (ret !== null) l.unshift(mos(pesos(Math.abs(x.saldo)), x.saldo < 0 ? 'saldo a favor' : (x.saldo > 0 ? 'saldo a cargo' : 'ni a favor ni a cargo')));
    h = mosaicos(l);
    if (ret === null) {
      ver = ('<b>Me falta un dato para decirte si te devuelven:</b> el ISR que te retuvieron en el año. Con lo que sí me diste, tu ISR del año sería de <b>' + pesos(x.isr) +
        '</b>: si te retuvieron más que eso, la diferencia es tu saldo a favor; si te retuvieron menos, es tu saldo a cargo. El simulador hace la cuenta completa.');
    } else if (x.saldo < 0) ver = ('Con estos números tendrías un <b>saldo a favor de ' + pesos(-x.saldo) + '</b>: tu ISR del año es de ' + pesos(x.isr) + ' y te retuvieron ' + pesos(ret) + '.');
    else if (x.saldo > 0) ver = ('Con estos números tendrías un <b>saldo a cargo de ' + pesos(x.saldo) + '</b>: tu ISR del año es de ' + pesos(x.isr) + ' y te retuvieron ' + pesos(ret) + '.');
    else ver = ('Con estos números no sale saldo a favor ni a cargo: tu ISR del año es igual a lo que te retuvieron (' + pesos(ret) + ').');
    h += p('El tope global de tus deducciones es de <b>' + pesos(x.tope) + '</b>: lo menor entre ' + K.ded.veces + ' veces la UMA anual y el ' + pct(K.ded.pct) + ' de tus ingresos.' +
      (S.r2(g + x.fun) > x.glob ? ' De tus deducciones quedan fuera <b>' + pesos(S.r2(g + x.fun - x.glob)) + '</b> por ese tope.' : '') +
      (f > x.fun ? ' De tus gastos funerarios solo cuentan ' + pesos(x.fun) + '.' : '') +
      (ap > x.ret ? ' De tus aportaciones de retiro solo se deducen ' + pesos(x.ret) + ', que van aparte del tope global.' : ''));
    if (col) h += p('Las colegiaturas tienen un límite por nivel escolar y van aparte del tope global: no las metí a esta cuenta. Ponlas en el simulador, con su nivel.', 'fc-ojo');
    h += p(ob ? 'Con ingresos por sueldos de más de ' + pesos(K.anualDesde) + ' en el año, <b>sí estás obligado</b> a presentar la declaración anual.'
      : 'Tus sueldos no pasan de ' + pesos(K.anualDesde) + ' en el año: por el monto no estás obligado a presentarla, aunque la ley trae otros casos que el simulador te pregunta.');
    h += p('Lo que tomé de tu pregunta: ingresos por <b>' + pesos(i) + '</b> en el año' + (ret !== null ? ', ISR retenido por <b>' + pesos(ret) + '</b>' : '') +
      (g ? ', deducciones personales por <b>' + pesos(g) + '</b>' : '') + (f ? ', gastos funerarios por <b>' + pesos(f) + '</b>' : '') + (ap ? ', aportaciones de retiro por <b>' + pesos(ap) + '</b>' : '') +
      '. Se usa la tarifa anual de 2026; no cuenta el subsidio para el empleo ni otros ingresos.', 'pa-chico');
    return { mod: 'anual', x: x, args: { i: i, ret: ret, g: g, f: f, ap: ap }, ver: ver, html: h };
  }

  function respReg(C, L) {
    var K = C.K, m = suma(L, ['ingreso'], 'mes', 'mes'), g = suma(L, ['gasto', 'deduccion'], 'mes', 'mes');
    if (!m) return { falta: 'lo que cobras, al mes o al año', tema: 'sim_reg' };
    var perfil = 'servicios', sub = '';
    for (var n = 0; n < PERFIL.length; n++) if (rx(PERFIL[n].rx).test(L.t)) { perfil = PERFIL[n].p; sub = PERFIL[n].s; break; }
    var x = S.compara(K, perfil, sub, m, g || 0), filas = [], h, ver = '', cabe = x.ing <= K.resico['2026'].tope;
    var fila = function (nombre, monto, nota) { filas.push({ v: monto, n: nombre, h: '<li><b>' + nombre + ':</b> ' + (monto === null ? 'fuera de su tabla' : '<b>' + pesos(monto) + '</b> de ISR en el año') + (nota ? ' <span class="pa-chico">(' + nota + ')</span>' : '') + ' ' + AUD + '</li>' }); };
    if (perfil === 'plataformas') {
      fila('Con la tarifa anual sobre tu utilidad', x.general, 'utilidad de ' + pesos(x.util));
      h = mosaicos([mos(pesos(x.ret), 'ISR que te retiene la plataforma en el año (' + pct(K.plat[sub]) + ')'), mos(pesos(x.general), 'ISR del año con la tarifa anual'),
        mos(pesos(Math.abs(x.saldo)), x.saldo > 0 ? 'te faltaría pagar en la anual' : 'retenido de más')]);
      h += '<ul class="pa-lista">' + filas.map(function (f) { return f.h; }).join('') + '</ul>';
      ver = (x.definitivo ? 'Tus ingresos del año (' + pesos(x.ing) + ') no pasan de ' + pesos(K.plat.definitivo) + ': la ley te deja optar por que la retención sea tu pago definitivo.'
        : 'Tus ingresos del año (' + pesos(x.ing) + ') pasan de ' + pesos(K.plat.definitivo) + ': la retención no puede ser tu pago definitivo y presentas la anual.');
    } else {
      fila('Actividad empresarial o servicios profesionales', x.general, 'tarifa anual sobre tu utilidad de ' + pesos(x.util));
      if (cabe) fila('RESICO en 2026', x.resico2026, 'sobre todo lo cobrado, sin deducciones');
      fila('RESICO desde 2027', x.ing <= K.resico['2027'].tope ? x.resico2027 : null, x.ing <= K.resico['2027'].tope ? 'con la tabla nueva' : 'rebasas su tope');
      if (perfil === 'arrendamiento') fila('Arrendamiento con la deducción sin comprobantes de ' + pct(K.ciega), x.ciega, 'tarifa anual sobre ' + pesos(x.baseCiega));
      var vivos = filas.filter(function (f) { return f.v !== null; }).sort(function (u, w) { return u.v - w.v; });
      h = mosaicos(filas.filter(function (f) { return f.v !== null; }).map(function (f) { return mos(pesos(f.v), f.n); }));
      h += '<ul class="pa-lista">' + filas.map(function (f) { return f.h; }).join('') + '</ul>';
      if (vivos.length > 1) ver = ('Con estos números, el ISR del año más bajo sale en <b>' + vivos[0].n + '</b>: ' + pesos(S.r2(vivos[1].v - vivos[0].v)) + ' menos que la opción que le sigue. Es solo el ISR: el IVA, las retenciones y tus obligaciones cambian de un régimen a otro.');
      if (!cabe) h += p('Con ' + pesos(x.ing) + ' al año rebasas el tope del RESICO de 2026 (' + pesos(K.resico['2026'].tope) + ').', 'fc-ojo');
    }
    h += p('Lo que tomé de tu pregunta: cobras <b>' + pesos(m) + '</b> al mes' + (g === null ? ' y <b>no me dijiste tus gastos</b>: hice la cuenta sin deducciones, así que el régimen general puede salirte más bajo.' : ' y tienes gastos deducibles por <b>' + pesos(g) + '</b> al mes.') +
      ' El régimen general se estima con la tarifa anual de 2026 sobre doce meses iguales. Lo de 2027 ' + esc(K.rige) + '. ' + C.hasta, 'pa-chico');
    return { mod: 'reg', x: x, args: { m: m, g: g, perfil: perfil, sub: sub }, ver: ver, html: h };
  }

  var RESP = { iva: respIva, resico: respResico, anual: respAnual, reg: respReg };

  /* La respuesta calculada de una pregunta, o null si no pide una cuenta. C es D.fis.calc. */
  function responde(C, q) {
    if (!C || !C.K || !S) return null;
    var L = lee(q), k = intencion(L);
    if (!k) return null;
    var r = RESP[k](C, L);
    if (r.falta) return { falta: r.falta, tema: r.tema, mod: k };
    var M = C.m[r.mod];
    r.tit = M.tit; r.ir = M.ir; r.fu = M.fu; r.sug = M.sug; r.calc = true;
    /* Arriba, a la vista: el aviso de que nada sale del navegador y el veredicto; luego los mosaicos, y el detalle se pliega. */
    r.html = '<div class="fc-cab"><p><b>Hice la cuenta con tus números</b>, aquí en tu navegador: tus montos no se envían ni se guardan en ningún servidor.</p>' +
      (r.ver ? '<p class="fc-ver">' + r.ver + '</p>' : '') + '</div>' + r.html + M.fund + '<p class="pa-chico">' + C.no + '</p>';
    return r;
  }

  var API = { plano: plano, montos: montos, anonimiza: anonimiza, lee: lee, intencion: function (q) { return intencion(lee(q)); }, responde: responde };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  raiz.FiscalCalc = API;
})(typeof window !== 'undefined' ? window : globalThis);
