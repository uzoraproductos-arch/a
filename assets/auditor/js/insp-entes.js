/* Auditavisión · Modo Inspector › Auditor de entes públicos (12-10-2026).
   La página la escribe herramientas/insp_entes.py; este guion hace lo que
   hacía el explorador del motor (audit-engine.js: inspEntes, inspEjes,
   inspDiagnostico, inspExpedienteFederal/Local, inspCopiarFicha) sin
   cargar el motor ni la base completa.

   Mismos pesos, mismos umbrales y mismas salvaguardas: una señal no es una
   acusación, «por aclarar» no es «robado», el índice es una construcción
   de Auditavisión. Los municipios se cargan al vuelo de los archivos que ya
   existen (municipios-efipem.js y municipios-rendicion.js). */
(function () {
  'use strict';
  var raiz = document.getElementById('ie');
  var nodoDatos = document.getElementById('ieDatos');
  if (!raiz || !nodoDatos) return;
  var D = JSON.parse(nodoDatos.textContent);
  var P = D.pesos, UF = D.uf, UL = D.ul;
  var reducido = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------- Formato (el mismo del motor) ---------------- */
  function fmt(n) { return Number(n).toLocaleString('es-MX'); }
  function simMdp(n) {
    var a = Math.abs(n);
    if (a >= 1000000) return '$' + (n / 1000000).toFixed(2) + ' billones';
    if (a >= 1000) return '$' + fmt(Math.round(n / 100) / 10) + ' mil millones';
    return '$' + fmt(Math.round(n * 100) / 100) + ' millones';
  }
  /* En incongruencias, la cifra completa: redondear esconde lo señalado. */
  function mdpF(n) { return '$' + n.toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mdp'; }
  function pctTxt(x) { return (x >= 0 ? '+' : '') + x.toFixed(1) + ' %'; }
  function acot(x) { return Math.max(0, Math.min(100, x)); }
  function esc(t) {
    return String(t == null ? '' : t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function plano(t) { return String(t).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function chip(e, pend) {
    var t = (e === 'oficial' || e === 'pendiente') ? e : 'derivado';
    return '<span class="est-chip est-' + t + '"' + (pend ? ' data-pend="' + pend + '"' : '') + '>' + t + '</span>';
  }
  /* La llamada [nn] a fuentes-oficiales.html, como la pinta apartados.py. */
  function ref(rid) {
    var r = rid && D.refs[rid];
    if (!r) return '';
    return '<sup class="apartado-libro-llamado"><a href="fuentes-oficiales.html#' + rid + '" title="' + esc(r[1]) + '">[' +
      (r[0] < 10 ? '0' : '') + r[0] + ']</a></sup>';
  }
  function refFed(k) { var x = D.fF[k] || D.fP[k]; return x && x.ref ? ref(x.ref) : ''; }
  function refEst(k) { var x = D.fE[k]; return x ? ref(x.ref) : ''; }
  function refMun(k) { var R = window.AUDIT_MUN_RENDICION; return R && R.fuentes[k] ? ref(R.fuentes[k].ref) : ''; }
  function sinFuente(campo, abbr) { var c = D.fe[campo]; return !!(c && c.sinFuente && c.sinFuente.indexOf(abbr) !== -1); }
  function chipCampo(campo, abbr) {
    var c = D.fe[campo];
    if (!c) return '';
    if (sinFuente(campo, abbr)) return ' <span title="' + esc(c.motivo || c.fuente) + '">' + chip('pendiente', 'entidades-' + abbr.toLowerCase()) + '</span>';
    return ' <span title="' + esc(c.fuente) + '">' + chip(c.estado) + '</span>';
  }
  function fecha(iso) {
    if (!iso) return '';
    var p = iso.slice(0, 10).split('-');
    var m = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
    return parseInt(p[2], 10) + ' de ' + m[parseInt(p[1], 10) - 1] + ' de ' + p[0];
  }

  var SEM = {
    ok: { ico: '🟢', t: 'Sin señal' },
    alerta: { ico: '🟠', t: 'Señal a revisar' },
    grave: { ico: '🔴', t: 'Señal fuerte' },
    sin: { ico: '⚪', t: 'Sin dato' }
  };
  function peor(a, b) { var o = { sin: 0, ok: 1, alerta: 2, grave: 3 }; return o[b] > o[a] ? b : a; }
  function inc(tema, docA, vA, docB, vB, e, nota) {
    var dif = vB - vA;
    return { tema: tema, a: [docA, vA], b: [docB, vB], dif: dif, pct: vA ? dif / vA * 100 : null, e: e, nota: nota || '' };
  }

  /* ---------------- El universo de entes ---------------- */
  var cache = {}, cacheDiag = {};
  function entes(nivel) {
    if (cache[nivel]) return cache[nivel];
    var out = [];
    if (nivel === 'federal') {
      out = D.fed.map(function (f) {
        var pe = D.poderes[f.poder][0];
        return { nivel: 'federal', id: f.id, nombre: f.nombre, icono: f.icono, poder: f.poder, sub: f.tipo + ' · Ramo ' + f.ramo,
          buscar: plano(f.nombre + ' ' + f.id + ' ramo ' + f.ramo + ' ' + f.tipo + ' ' + pe), fed: f };
      });
    } else if (nivel === 'estatal') {
      out = D.est.map(function (e) {
        return { nivel: 'estatal', id: e.abbr, nombre: e.name, icono: '🗺️', sub: 'Gobierno de ' + e.name + ' · ' + e.partido + ' · ' + e.gobernador,
          buscar: plano(e.name + ' ' + e.abbr + ' ' + e.gobernador + ' ' + e.partido + ' ' + e.capital + ' estado'), est: e };
      });
    } else {
      var M = window.AUDIT_MUNICIPIOS;
      if (!M) return [];
      Object.keys(M.ent).forEach(function (ab) {
        var ent = M.ent[ab];
        var est = D.est.filter(function (x) { return x.abbr === ab; })[0];
        var nomEst = est ? est.name : ab;
        ent.lista.forEach(function (r) {
          var k = ent.cve + r[0];
          var rd = munRend(k);
          var g = rd && rd.g;
          var quien = g && g[0] ? g[0] + (g[1] ? ' (' + g[1] + ')' : '') : '';
          out.push({ nivel: 'municipal', id: k, nombre: r[1], icono: ab === 'CDMX' ? '🏛️' : '🏙️', abbr: ab,
            sub: nomEst + (quien ? ' · ' + quien : ''), buscar: plano(r[1] + ' ' + nomEst + ' ' + ab + ' ' + k + ' ' + quien + ' municipio'),
            pad: r, rd: rd, est: est });
        });
      });
    }
    cache[nivel] = out;
    return out;
  }
  function munRend(k) { var R = window.AUDIT_MUN_RENDICION; return (R && R.mun[k]) || null; }
  function buscarEnte(nivel, id) { return entes(nivel).filter(function (x) { return x.id === id; })[0] || null; }

  /* Carga al vuelo de los municipios, con el mismo sello de la página. */
  var munPromesa = null;
  function cargarMun() {
    if (window.AUDIT_MUNICIPIOS && window.AUDIT_MUN_RENDICION) return Promise.resolve();
    if (munPromesa) return munPromesa;
    var yo = document.querySelector('script[src*="insp-entes.js"]');
    var v = yo && /\?v=([^&]+)/.exec(yo.getAttribute('src'));
    var base = yo ? yo.getAttribute('src').replace(/insp-entes\.js.*$/, '') : 'assets/auditor/js/';
    avisoMun('⏳ Cargando el padrón de ' + (D.mun.n ? fmt(D.mun.n) : 'los') + ' municipios del INEGI…');
    munPromesa = Promise.all(D.mun.src.map(function (s) {
      return new Promise(function (ok, mal) {
        var el = document.createElement('script');
        el.src = base + s + (v ? '?v=' + v[1] : '');
        el.onload = ok;
        el.onerror = function () { mal(new Error(s)); };
        document.head.appendChild(el);
      });
    })).then(function () {
      cache.municipal = null;
      avisoMun('');
    }, function () {
      munPromesa = null;
      avisoMun('No se pudo cargar el padrón municipal. Revisa tu conexión y vuelve a intentarlo.');
      throw new Error('municipios');
    });
    return munPromesa;
  }
  function avisoMun(t) {
    var n = document.getElementById('ieQnota');
    if (n) n.textContent = t || 'Busca por nombre; también encuentras municipios y a quien los gobernó.';
  }

  /* Cifras municipales del padrón, en millones. null si no rindió 2024. */
  function munCifras(ente) {
    var r = ente.pad;
    if (!r || r.length < 3) return null;
    var m = function (v) { return v / 1e6; };
    return { ing: m(r[2]), part: m(r[3]), aport: m(r[4]), fortamun: m(r[5]), fismdf: m(r[6]),
      predial: m(r[7]), propios: m(r[8]), dep: r[2] > 0 ? (r[3] + r[4]) / r[2] * 100 : null };
  }

  /* ---------------- Los tres ejes del índice ---------------- */
  function ejes(ente) {
    if (ente.nivel === 'estatal') {
      var e = ente.est;
      var obsPct = e.gasto > 0 ? e.asfMontoObservado / e.gasto * 100 : 0;
      var deudaPct = e.gasto > 0 ? e.deuda / e.gasto * 100 : 0;
      return [
        { et: 'Autonomía financiera', ico: '🪙', v: acot(100 - e.dep),
          crudo: e.dep.toFixed(1) + '% de dependencia federal en 2024' + (sinFuente('dep', e.abbr) ? ' (dato pendiente de fuente)' : ' (INEGI)'),
          expl: 'De cada 100 pesos que ingresó en 2024, sin contar deuda, ' + e.dep.toFixed(1) + ' llegaron de la Federación por participaciones, aportaciones y convenios. ' +
            'El eje mide lo contrario: lo que el estado recauda por su cuenta.' },
        { et: 'Limpieza en la cuenta', ico: '⚠️', v: acot(100 - obsPct * 20),
          crudo: simMdp(e.asfMontoObservado) + ' observados en ' + e.asfAuditorias + ' auditorías',
          expl: 'Lo observado por la ASF equivale al ' + obsPct.toFixed(2) + '% de lo que recibe en un año por los Ramos 28 y 33. ' +
            'Observado no es robado: es dinero cuyo destino no quedó acreditado y que hay que aclarar.' },
        { et: 'Holgura frente a la deuda', ico: '⚖️', v: acot(100 - deudaPct * 2),
          crudo: simMdp(e.deuda) + ' de deuda · semáforo ' + e.semaforoDeuda,
          expl: 'Su deuda equivale al ' + deudaPct.toFixed(1) + '% de lo que recibe en un año por los Ramos 28 y 33. ' +
            'El semáforo es el del Sistema de Alertas de la SHCP, no nuestro.' }
      ];
    }
    if (ente.nivel === 'municipal') {
      var c = munCifras(ente);
      var a = ente.rd && ente.rd.a;
      if (!c || !a || !(c.ing > 0)) return null;
      var obs = a[4] + a[5];
      var oPct = obs / c.ing * 100;
      var predPct = c.predial / c.ing * 100;
      return [
        { et: 'Autonomía financiera', ico: '🪙', v: acot(100 - c.dep),
          crudo: c.dep.toFixed(1) + '% de su ingreso de 2024 vino de participaciones y aportaciones (INEGI)',
          expl: 'De cada 100 pesos que ingresó en 2024, ' + c.dep.toFixed(1) + ' le llegaron de la Federación y del estado. ' +
            'El eje mide lo contrario: lo que el municipio recauda por su cuenta.' },
        { et: 'Limpieza en la cuenta', ico: '⚠️', v: acot(100 - oPct * 20),
          crudo: simMdp(obs) + ' observados por la ASF (por aclarar más recuperado)',
          expl: 'Equivale al ' + oPct.toFixed(2) + '% de su ingreso de 2024. Sale de su auditoría integral n.º ' + a[0] + ' de la Cuenta Pública 2024.' },
        { et: 'Esfuerzo recaudatorio', ico: '🏠', v: acot(predPct * 4),
          crudo: simMdp(c.predial) + ' de predial, el ' + predPct.toFixed(1) + '% de su ingreso',
          expl: 'El predial es el impuesto que un municipio sí controla. Cuanto más pesa, menos depende de que le manden dinero. ' +
            'No hay dato oficial de deuda municipal por municipio, así que este eje mide esfuerzo propio en su lugar.' }
      ];
    }
    return null;
  }
  function indice(ej) {
    if (!ej) return null;
    return (ej[0].v * P.autonomia + ej[1].v * P.observado + ej[2].v * P.holgura) / (P.autonomia + P.observado + P.holgura);
  }
  function veredicto(n) {
    if (n >= 75) return { c: 'v1', ico: '🟢', t: 'Salud financiera sólida', d: 'Se sostiene en buena medida con lo suyo y lo observado es marginal frente a su tamaño.' };
    if (n >= 55) return { c: 'v2', ico: '🟢', t: 'Salud financiera aceptable', d: 'Sin focos rojos evidentes, pero con margen claro de mejora en alguno de los tres ejes.' };
    if (n >= 40) return { c: 'v3', ico: '🟡', t: 'Salud financiera frágil', d: 'Depende demasiado de lo que le transfieren, o arrastra observaciones que no ha aclarado.' };
    if (n >= 25) return { c: 'v4', ico: '🟠', t: 'Salud financiera comprometida', d: 'Dos de los tres ejes están por debajo de lo razonable. Conviene revisar su cuenta pública con calma.' };
    return { c: 'v5', ico: '🔴', t: 'Salud financiera crítica', d: 'Sobrevive de transferencias y con un volumen de observaciones alto para su tamaño.' };
  }

  /* ---------------- Las preguntas: estatal ---------------- */
  function diagEstatal(ente) {
    var e = ente.est, U = UL, x = e.x;
    var sinInegi = sinFuente('dep', e.abbr);
    var out = [];
    out.push({ k: 'vive', ico: '🪙', q: '¿De qué vive?', pend: sinInegi ? 'entidades-' + e.abbr.toLowerCase() : '',
      e: sinInegi ? 'sin' : e.dep > U.depAlerta ? 'alerta' : 'ok',
      v: sinInegi ? 'Sin dato del INEGI' : e.dep.toFixed(1) + ' % de su ingreso vino de la Federación',
      d: sinInegi
        ? 'La Ciudad de México no figura en la estadística estatal del INEGI en ningún año, así que no hay cifra oficial con que medir su dependencia.'
        : 'En 2024, sin contar deuda, ' + e.dep.toFixed(1) + ' de cada 100 pesos que ingresó el gobierno del estado fueron participaciones, aportaciones o convenios federales; ' +
          'recaudó por su cuenta ' + simMdp(e.recaudacionPropia) + '. Depender mucho no es una irregularidad: es fragilidad, porque su gasto se decide en buena parte fuera del estado.',
      f: sinInegi ? '' : refEst('inegi2024') });

    var p2 = [], e2 = 'ok';
    if (sinInegi) p2.push('No figura en la estadística estatal del INEGI (es un hueco de cobertura de esa estadística, no un incumplimiento que se le pueda atribuir).');
    else p2.push('Entregó su cuenta de 2024 a la estadística de finanzas estatales del INEGI' + refEst('inegi2024') + '.');
    if (e.asfAuditorias > 0) p2.push('La Auditoría Superior le practicó ' + e.asfAuditorias + ' auditorías al dinero federal de la Cuenta Pública 2024.');
    else { e2 = 'alerta'; p2.push('No aparece con auditorías de la ASF en la Cuenta Pública 2024.'); }
    if (e.semaforoDeuda) p2.push('Hacienda evaluó su deuda en el Sistema de Alertas.');
    out.push({ k: 'cuentas', ico: '📒', q: '¿Rindió cuentas?', e: e2,
      v: e2 === 'ok' ? 'Reportó y fue auditado' : 'Reportó; sin auditoría registrada', d: p2.join(' '), f: '' });

    var lista = [], e3 = 'sin', v3 = 'Sin dos cifras que contrastar', d3 = '';
    if (x && x.inegiPart !== null) {
      e3 = 'ok';
      [['Participaciones (Ramo 28)', x.inegiPart, x.cpR28], ['Aportaciones (Ramo 33)', x.inegiAportSinConvenios, x.cpR33]].forEach(function (t) {
        var pc = t[2] ? (t[1] / t[2] - 1) * 100 : 0, a = Math.abs(pc);
        var ei = a > U.estCuadreGrave ? 'grave' : a > U.estCuadreAlerta ? 'alerta' : 'ok';
        if (ei !== 'ok') {
          e3 = peor(e3, ei);
          lista.push(inc(t[0] + ' de 2024', 'Pagado por la Federación (Cuenta Pública 2024)', t[2], 'Recibido según el estado (INEGI)', t[1], ei));
        }
      });
      v3 = lista.length ? lista.length + (lista.length === 1 ? ' incongruencia' : ' incongruencias') : 'Cuadran';
      d3 = 'Se compara lo que el gobierno del estado reportó al INEGI como recibido en 2024 con lo que la Cuenta Pública registra como pagado por la Federación a la entidad. ' +
        'Participaciones: ' + simMdp(x.inegiPart) + ' según el estado, ' + simMdp(x.cpR28) + ' según la Federación. ' +
        'Aportaciones (sin convenios): ' + simMdp(x.inegiAportSinConvenios) + ' según el estado, ' + simMdp(x.cpR33) + ' según la Federación. ' +
        (lista.length ? 'Una diferencia puede tener explicación (retenciones de participaciones por adeudos, pagos directos a un fideicomiso de deuda, registros en otro año), ' +
          'pero esa explicación tiene que darla el gobierno: el ciudadano no tiene por qué adivinarla.' : 'Las dos fuentes coinciden dentro del margen de ±' + U.estCuadreAlerta + ' %.');
    } else if (x) {
      d3 = 'La Cuenta Pública registra ' + simMdp(x.cpR28) + ' de participaciones y ' + simMdp(x.cpR33) + ' de aportaciones pagadas a la Ciudad de México en 2024, ' +
        'pero no hay cifra de la Ciudad en el INEGI con que contrastarlas.';
    }
    out.push({ k: 'cuadre', ico: '🧮', q: '¿Cuadra lo que dice haber recibido con lo que la Federación dice haberle pagado?', e: e3, v: v3, d: d3,
      pend: e3 === 'sin' && sinInegi ? 'entidades-' + e.abbr.toLowerCase() : '',
      f: refEst('cp2024') + refEst('inegi2024'), inc: lista });

    var obsPct = e.gasto > 0 ? e.asfMontoObservado / e.gasto * 100 : 0;
    out.push({ k: 'asf', ico: '🔍', q: '¿Qué encontró la Auditoría Superior?',
      e: e.asfMontoObservado <= 0 ? 'ok' : obsPct >= U.asfGravePct ? 'grave' : 'alerta',
      v: e.asfMontoObservado > 0 ? simMdp(e.asfMontoObservado) + ' por aclarar' : 'Nada por aclarar',
      d: e.asfTipologia + ' Equivale al ' + obsPct.toFixed(2) + ' % de lo que recibe en un año por los Ramos 28 y 33. Por aclarar no es robado: es dinero cuyo destino no quedó acreditado.',
      f: ref('ref-asf-mdb2024') });

    var sem = (e.semaforoDeuda || '').toLowerCase();
    out.push({ k: 'deuda', ico: '⚖️', q: '¿Puede con su deuda?',
      e: sem === 'verde' ? 'ok' : sem === 'amarillo' ? 'alerta' : sem === 'rojo' ? 'grave' : 'sin',
      v: e.semaforoDeuda ? 'Semáforo ' + sem + ' de Hacienda' : 'Sin evaluación',
      d: 'Debe ' + simMdp(e.deuda) + '. ' + (e.deudaIld ? 'Su deuda equivale al ' + e.deudaIld + ' % de sus ingresos de libre disposición. ' : '') +
        'El color no es de Auditavisión: es el que asigna el Sistema de Alertas de la SHCP (' + (e.deudaFuente || 'SHCP') + ').', f: '' });
    return out;
  }

  /* ---------------- Las preguntas: municipal ---------------- */
  function munAsf(a, c) {
    var U = UL;
    if (!a) {
      return { k: 'asf', ico: '🔍', q: '¿Qué encontró la Auditoría Superior?', e: 'sin', v: 'Sin auditoría integral en la CP 2024',
        d: 'La ASF no le practicó auditoría integral en la Cuenta Pública 2024. Sus fondos federales pudieron revisarse dentro de auditorías al gobierno del estado, que la Matriz no desglosa por municipio.',
        f: refMun('asf') };
    }
    var pc = c && c.ing > 0 ? a[4] / c.ing * 100 : null;
    var e = a[4] > 0 ? ((pc !== null && pc >= U.munAsfGravePct) || a[4] >= U.munAsfGraveMdp ? 'grave' : 'alerta') : a[2] > 0 ? 'alerta' : 'ok';
    return { k: 'asf', ico: '🔍', q: '¿Qué encontró la Auditoría Superior?', e: e,
      v: a[4] > 0 ? simMdp(a[4]) + ' por aclarar' : a[2] > 0 ? a[2] + (a[2] === 1 ? ' acción' : ' acciones') + ', nada por aclarar' : 'Sin observaciones',
      d: 'Auditoría integral n.º ' + a[0] + ' de la Cuenta Pública 2024 (entrega ' + a[1] + '): ' + a[3] + ' resultados con observación y ' + a[2] +
        ' acciones promovidas; ' + simMdp(a[4]) + ' por aclarar y ' + simMdp(a[5]) + ' recuperados durante la auditoría' +
        (pc !== null ? ' (lo por aclarar equivale al ' + pc.toFixed(2) + ' % de su ingreso de 2024)' : '') +
        '. Por aclarar no es robado: es dinero cuyo destino no quedó acreditado.',
      f: refMun('asf') };
  }

  function diagMunicipal(ente) {
    var U = UL, rd = ente.rd || {}, c = munCifras(ente), R = window.AUDIT_MUN_RENDICION;
    var out = [], h = rd.h || '', anios = R ? R.anios : [];
    if (ente.abbr === 'CDMX') {
      out.push({ k: 'cuentas', ico: '📒', q: '¿Rindió cuentas?', e: 'sin', v: 'No rinde cuenta municipal', d: D.cdmx, f: '' });
      if (rd.a) out.push(munAsf(rd.a, null));
      return out;
    }
    if (c) {
      out.push({ k: 'vive', ico: '🪙', q: '¿De qué vive?', e: c.dep > U.depAlerta ? 'alerta' : 'ok',
        v: c.dep.toFixed(1) + ' % de su ingreso vino de fuera',
        d: 'En 2024 ingresó ' + simMdp(c.ing) + ': ' + simMdp(c.part) + ' de participaciones y ' + simMdp(c.aport) + ' de aportaciones ' +
          '(entre ellas ' + simMdp(c.fortamun) + ' del FORTAMUN y ' + simMdp(c.fismdf) + ' del FAIS). Recaudó ' + simMdp(c.propios) +
          ' por su cuenta, ' + simMdp(c.predial) + ' de ellos de predial. Depender mucho no es irregular: es fragilidad.',
        f: refMun('inegi') });
    } else if (rd.u) {
      var dep = rd.u[1] > 0 ? (rd.u[2] + rd.u[3]) / rd.u[1] * 100 : 0;
      out.push({ k: 'vive', ico: '🪙', q: '¿De qué vive?', e: 'sin', pend: 'municipios-sin-cuenta',
        v: 'Último dato: ' + rd.u[0],
        d: 'No hay cifra de 2024. En su última cuenta entregada al INEGI, la de <b>' + rd.u[0] + '</b>, declaró ingresos por ' + simMdp(rd.u[1] / 1e6) +
          ', de los cuales ' + simMdp((rd.u[2] + rd.u[3]) / 1e6) + ' (' + dep.toFixed(1) + ' %) fueron participaciones y aportaciones. ' +
          'Es el último dato oficial de sus finanzas; no se proyecta a 2024.',
        f: refMun('inegi') });
    } else {
      out.push({ k: 'vive', ico: '🪙', q: '¿De qué vive?', e: 'sin', pend: 'municipios-sin-cuenta', v: 'Sin ningún dato del INEGI',
        d: 'No aparece con cifras en la estadística municipal del INEGI en ninguno de los años de ' + anios[0] + ' a ' + anios[anios.length - 1] +
          '. Si es un municipio de creación reciente, puede que aún no le toque reportar; si no, es un municipio del que no hay cuentas públicas en la estadística nacional.',
        f: refMun('inegi') });
    }

    var i24 = anios.indexOf(2024);
    var entrego24 = h.charAt(i24) === '1';
    var faltas = [];
    anios.forEach(function (a, i) { if (a < 2024 && h.charAt(i) === '0') faltas.push(a); });
    var s = rd.s, pr = rd.p, informo = !!(s || pr);
    var hac = function (j) {
      if (s && s[j] > 0) return [s[j] / 1e6, 'Recibido según su informe a Hacienda (SRFT)'];
      if (pr && pr[j] > 0) return [pr[j] / 1e6, 'Obras registradas ante Hacienda (SRFT, destino del gasto)'];
      return null;
    };
    var omitidos = informo ? ['FAIS', 'FORTAMUN'].filter(function (n, j) { return !hac(j); }) : [];
    var p2 = [];
    if (entrego24) p2.push('Entregó su cuenta de 2024 al INEGI' + refMun('inegi') + '.');
    else {
      var ult = anios.filter(function (a, i) { return a < 2024 && h.charAt(i) === '1'; });
      p2.push('<b>No entregó su cuenta de 2024 al INEGI</b>' + refMun('inegi') + (ult.length ? '; la última que entregó fue la de ' + ult[ult.length - 1] + '.' : ', ni ninguna otra desde ' + anios[0] + '.'));
    }
    if (faltas.length) p2.push('De ' + anios[0] + ' a 2023 faltó ' + faltas.length + (faltas.length === 1 ? ' año' : ' años') + ': ' + faltas.join(', ') + '.');
    else p2.push('No faltó ningún año de ' + anios[0] + ' a 2023.');
    p2.push(h.charAt(anios.indexOf(R ? R.preliminar : 2025)) === '1'
      ? 'Ya aparece en las cifras preliminares de 2025.'
      : 'Aún no aparece en las cifras preliminares de 2025 (el INEGI sigue integrándolas: todavía no es una falta).');
    if (!s && pr) {
      p2.push('No llenó el componente de ejercicio del gasto del Sistema de Recursos Federales Transferidos, pero sí registró ahí obras y acciones financiadas con el FAIS (' +
        simMdp(pr[0] / 1e6) + ') y el FORTAMUN (' + simMdp(pr[1] / 1e6) + ') de 2024' + refMun('srft') + '.');
      if (!entrego24) p2.push('<b>Ese dinero federal no quedó registrado en la estadística del INEGI</b>, porque no entregó su cuenta.');
    } else if (s) {
      p2.push('Informó a Hacienda lo que recibió y pagó del FAIS y del FORTAMUN de 2024' + refMun('srft') + '.');
      if (!entrego24) p2.push('<b>Por su propio informe a Hacienda, en 2024 recibió ' + simMdp((s[0] + s[1]) / 1e6) + '</b> de esos dos fondos federales (' +
        simMdp(s[0] / 1e6) + ' del FAIS y ' + simMdp(s[1] / 1e6) + ' del FORTAMUN): dinero que no quedó registrado en la estadística del INEGI porque no entregó su cuenta.');
    } else {
      p2.push('<b>No aparece informando a Hacienda</b> lo que recibió y gastó del FAIS y del FORTAMUN de 2024 (Sistema de Recursos Federales Transferidos' +
        refMun('srft') + '), como pide el artículo 85 de la Ley Federal de Presupuesto y Responsabilidad Hacendaria.');
    }
    if (omitidos.length) p2.push('<b>Del ' + omitidos.join(' ni del ') + ' no le informó nada a Hacienda</b>: ni lo recibido ni una sola obra.');
    var e2 = !entrego24 && !informo ? 'grave' : (!entrego24 || !informo || omitidos.length || faltas.length >= 2) ? 'alerta' : 'ok';
    out.push({ k: 'cuentas', ico: '📒', q: '¿Rindió cuentas?', e: e2,
      v: entrego24 && informo ? 'Sí, al INEGI y a Hacienda' : !entrego24 && !informo ? 'Ni al INEGI ni a Hacienda' : !entrego24 ? 'No al INEGI; sí a Hacienda' : 'Al INEGI sí; a Hacienda no',
      d: p2.join(' '), f: '' });

    var lista = [], e3 = 'sin', v3 = 'Sin dos reportes que contrastar',
      d3 = 'Para contrastar hacen falta sus dos reportes de 2024, al INEGI y a Hacienda, y ' + (entrego24 ? 'no informó a Hacienda.' : 'no entregó su cuenta al INEGI.');
    if (c && informo) {
      e3 = 'ok';
      var dichos = [];
      [['FAIS municipal', c.fismdf, hac(0)], ['FORTAMUN', c.fortamun, hac(1)]].forEach(function (t) {
        if (!t[2]) { dichos.push(simMdp(t[1]) + ' del ' + t[0] + ' al INEGI y nada a Hacienda'); return; }
        var hv = t[2][0], dif = hv - t[1];
        dichos.push(simMdp(t[1]) + ' del ' + t[0] + ' al INEGI y ' + simMdp(hv) + ' a Hacienda');
        var ei = 'ok';
        if (t[1] > 0 && Math.abs(dif) >= U.munMinimo) {
          var a = Math.abs(dif / t[1] * 100);
          ei = a > U.munCuadreGrave ? 'grave' : a > U.munCuadreAlerta ? 'alerta' : 'ok';
        }
        if (ei !== 'ok') { e3 = peor(e3, ei); lista.push(inc(t[0] + ' 2024', 'Declarado al INEGI', t[1], t[2][1], hv, ei)); }
      });
      v3 = lista.length ? lista.length + (lista.length === 1 ? ' incongruencia' : ' incongruencias') : 'Cuadran';
      d3 = 'Los dos reportes los hizo el propio ayuntamiento: ' + dichos.join('; ') + '. ' +
        (lista.length ? 'Son el mismo dinero del mismo año: la diferencia la debe explicar el municipio.' : 'Coinciden dentro de ±' + U.munCuadreAlerta + ' %.');
    }
    out.push({ k: 'cuadre', ico: '🧮', q: '¿Cuadra lo que le dijo al INEGI con lo que le dijo a Hacienda?', e: e3, v: v3, d: d3,
      pend: e3 === 'sin' && !entrego24 ? 'municipios-sin-cuenta' : '',
      f: c && informo ? refMun('inegi') + refMun('srft') : '', inc: lista });
    out.push(munAsf(rd.a, c));
    return out;
  }

  /* ---------------- Las preguntas: federal ---------------- */
  function diagFederal(f) {
    var U = UF, cp = f.cp2025, av = f.av2026, asf = f.asfS, out = [];
    var desvio = cp.original ? (cp.ejercido / cp.original - 1) * 100 : 0, d1 = Math.abs(desvio);
    if (!cp.original && cp.ejercido > 0) {
      out.push({ k: 'aprobado', ico: '🏛️', q: '¿Gastó lo que aprobó la Cámara de Diputados?', e: 'alerta',
        v: 'Sin presupuesto aprobado por la Cámara',
        d: 'El Presupuesto de Egresos de 2025 no le asignó nada: todavía no existía cuando se votó. Los ' + simMdp(cp.ejercido) +
          ' que ejerció le llegaron por adecuaciones que autoriza Hacienda (Ley Federal de Presupuesto, art. 58), sin pasar por el voto de los diputados.',
        f: refFed('cp2025') });
    } else out.push({ k: 'aprobado', ico: '🏛️', q: '¿Gastó lo que aprobó la Cámara de Diputados?',
      e: d1 > U.desvioGrave ? 'grave' : d1 > U.desvioAlerta ? 'alerta' : 'ok',
      v: pctTxt(desvio) + ' frente a lo aprobado',
      d: 'Para 2025 la Cámara le aprobó ' + simMdp(cp.original) + '. Ejerció ' + simMdp(cp.ejercido) + '. ' +
        'En el camino, Hacienda le autorizó un presupuesto modificado de ' + simMdp(cp.modificado) +
        ': la Ley Federal de Presupuesto (art. 58) permite esas adecuaciones sin volver a la Cámara, pero la diferencia ' +
        'dice cuánto se apartó el gasto real del que votaron los diputados.',
      f: refFed('cp2025') });

    var partes = ['Reportó su ejercicio de 2025 en la Cuenta Pública' + refFed('cp2025') + '.'];
    if (av) partes.push('Reportó su avance de 2026 al 30 de junio' + refFed('av2026') + '.');
    var e2 = av ? 'ok' : 'alerta';
    if (asf) {
      partes.push('La Auditoría Superior le practicó ' + asf.auditorias + ' auditoría' + (asf.auditorias === 1 ? '' : 's') +
        (asf.propias ? ' a su nombre' : '') + ' en la Cuenta Pública 2024' + refFed('asf2024') + '.');
    } else if (f.asfNoAplica === 'uec') {
      partes.push('La Auditoría Superior no se audita a sí misma: su gasto lo revisa la Unidad de Evaluación y Control de la Comisión de Vigilancia ' +
        'de la Cámara de Diputados, por sí o con auditores externos (art. 104, fr. II, de la Ley de Fiscalización' + refFed('lfrcf') + '). ' +
        'Los resultados de esa revisión todavía no están integrados aquí.');
    } else if (f.asfNoAplica === 'nuevo') {
      partes.push('Empezó a operar en 2025: no tuvo Cuenta Pública 2024 que auditarle. Su primer año llegará con la fiscalización de la Cuenta Pública 2025.');
    } else {
      e2 = 'alerta';
      partes.push('En la Matriz de la Cuenta Pública 2024 no aparece un sector a su nombre: su gasto de ese año no ' +
        'tuvo, al menos con ese rótulo, revisión externa de la Auditoría Superior. No es una irregularidad; es un hueco.');
    }
    out.push({ k: 'cuentas', ico: '📒', q: '¿Rindió cuentas?', e: e2,
      v: asf ? 'Reportó y fue auditado' : f.asfNoAplica === 'uec' ? 'Reportó; lo revisa la Cámara, no la ASF'
        : f.asfNoAplica === 'nuevo' ? 'Reportó; aún sin año auditable' : 'Reportó; sin auditoría a su nombre',
      d: partes.join(' '), f: '' });

    var hall = [], lista = [], e3 = 'ok';
    var exceso = cp.ejercido - cp.modificado;
    if (exceso >= 0.1) {
      e3 = 'grave';
      var caps = (cp.capitulosSobreModificado || []).filter(function (c) { return c.ejercido - c.modificado >= Math.max(100, c.modificado * 0.01); })
        .map(function (c) { return c.concepto + ' (' + simMdp(c.ejercido) + ' ejercidos contra ' + simMdp(c.modificado) + ' modificados)'; }).join('; ');
      hall.push('Registra un ejercido de ' + simMdp(cp.ejercido) + ', <b>' + simMdp(exceso) + ' más que su presupuesto modificado</b>' +
        (caps ? '. Por capítulo: ' + caps : '') + '. La base de Hacienda no explica la diferencia: es una pregunta que el ente debe responder.');
      lista.push(inc('Gasto de 2025 por encima de su presupuesto', 'Presupuesto modificado (Cuenta Pública 2025)', cp.modificado,
        'Ejercido (Cuenta Pública 2025)', cp.ejercido, 'grave', 'Un ente no debería ejercer más de lo que tiene autorizado.'));
    }
    var sinPagar = cp.ejercido - cp.pagado;
    if (cp.ejercido > 0 && sinPagar / cp.ejercido * 100 > U.pagoAlerta) {
      if (e3 === 'ok') e3 = 'alerta';
      hall.push('De lo ejercido, ' + simMdp(sinPagar) + ' (' + (sinPagar / cp.ejercido * 100).toFixed(1) + ' %) no figura como pagado al cierre de 2025.');
      lista.push(inc('Ejercido que no figura como pagado', 'Ejercido (Cuenta Pública 2025)', cp.ejercido,
        'Pagado (Cuenta Pública 2025)', cp.pagado, 'alerta', 'Lo ejercido y no pagado queda como deuda del ejercicio con proveedores o contratistas (adefas).'));
    }
    if (av && av.calendarioAlCorte > 0) {
      var ritmo = av.pagado / av.calendarioAlCorte * 100;
      if (ritmo < U.ritmoBajo || ritmo > U.ritmoAlto) {
        if (e3 === 'ok') e3 = 'alerta';
        hall.push('En 2026 pagó ' + simMdp(av.pagado) + ' de ' + simMdp(av.calendarioAlCorte) +
          ' que su calendario modificado marcaba de enero a junio: ' + ritmo.toFixed(1) + ' % de su propio calendario' + refFed('av2026') + '.');
      }
    }
    var coinciden = [];
    (f.cotejos || []).forEach(function (c) {
      var dif = c.b[1] - c.a[1];
      if (Math.abs(dif) > c.tol) {
        if (e3 === 'ok') e3 = 'alerta';
        hall.push(c.tema + ': ' + c.a[0] + ' registra ' + mdpF(c.a[1]) + refFed(c.a[2]) + '; ' + c.b[0] + ', ' + mdpF(c.b[1]) + refFed(c.b[2]) + '.');
        lista.push(inc(c.tema, c.a[0], c.a[1], c.b[0], c.b[1], 'alerta', c.nota));
      } else {
        coinciden.push(c.tema.charAt(0).toLowerCase() + c.tema.slice(1) + ', ' + mdpF(c.a[1]) + ' en ' + c.a[0] + refFed(c.a[2]) + ' y en ' + c.b[0] + refFed(c.b[2]));
      }
    });
    out.push({ k: 'cuadre', ico: '🧮', q: '¿Cuadran sus propias cifras?', e: e3,
      v: hall.length ? hall.length + (hall.length === 1 ? ' contradicción o desfase' : ' contradicciones o desfases') : 'Sin contradicciones',
      d: (hall.length ? hall.join(' ') : 'Lo ejercido no rebasa lo modificado, casi todo lo ejercido figura como pagado y en 2026 va al ritmo de su calendario.') +
        (coinciden.length ? ' <b>Coinciden</b> ' + coinciden.join('; ') + '.' : ''),
      f: refFed('cp2025'), inc: lista });

    var e4 = 'sin', v4 = 'Sin sector en la Matriz', d4 = 'La Matriz de la Cuenta Pública 2024 no tiene un sector con este nombre.';
    if (f.asfNoAplica) { v4 = f.asfNoAplica === 'uec' ? 'No la audita la ASF' : 'No existía en 2024'; d4 = f.nota || ''; }
    if (asf) {
      e4 = asf.porAclarar <= 0 && asf.PO === 0 ? 'ok' : (asf.PO > 0 && asf.porAclarar >= 100e6 ? 'grave' : 'alerta');
      v4 = asf.porAclarar > 0 ? simMdp(asf.porAclarar / 1e6) + ' por aclarar' : 'Nada por aclarar';
      d4 = (asf.acciones
        ? 'En la Cuenta Pública 2024 la ASF le promovió ' + fmt(asf.acciones) + ' acciones, ' + asf.PO + ' de ellas pliegos de observaciones; quedaron ' + simMdp(asf.porAclarar / 1e6) + ' por aclarar'
        : 'En la Cuenta Pública 2024 la ASF no le promovió acciones y no quedó nada por aclarar') +
        (asf.recuperaciones > 0 ? '; se recuperaron ' + simMdp(asf.recuperaciones / 1e6) + ' durante las auditorías. ' : '. ') +
        'Por aclarar no es robado: es dinero cuyo destino no quedó acreditado. ' +
        '<span class="ie-grupos">' + (asf.propias ? 'Auditorías' : 'Grupos de la Matriz') + ': ' + asf.grupos.join(' · ') + '.</span>';
    }
    out.push({ k: 'asf', ico: '🔍', q: '¿Qué encontró la Auditoría Superior?', e: e4, v: v4, d: d4, f: refFed('asf2024') });
    return out;
  }

  function diag(ente) {
    var k = ente.nivel + ':' + ente.id;
    if (!cacheDiag[k]) cacheDiag[k] = ente.nivel === 'federal' ? diagFederal(ente.fed) : ente.nivel === 'estatal' ? diagEstatal(ente) : diagMunicipal(ente);
    return cacheDiag[k];
  }
  function incs(dg) { var o = []; dg.forEach(function (x) { (x.inc || []).forEach(function (i) { o.push(i); }); }); return o; }
  function magnitud(ente) { return incs(diag(ente)).reduce(function (s, i) { return s + Math.abs(i.dif); }, 0); }
  function cuenta(dg) {
    var c = { grave: 0, alerta: 0, ok: 0, sin: 0 };
    dg.forEach(function (x) { c[x.e]++; });
    return c;
  }
  function munRecibido(x) {
    var s = x.rd && x.rd.s, p = x.rd && x.rd.p;
    return s ? s[0] + s[1] : p ? p[0] + p[1] : -1;
  }

  /* ---------------- El radar de la ASF (estados) ---------------- */
  /* El Radar por entidad, que fue la aplicación 2 del Modo Inspector, se
     fusionó con la ficha estatal (pedido del autor, 21-10-2026): cada estado
     trae su radar en su ficha técnica, y los 32 se ordenan con sus tres
     criterios en el directorio. Las cifras las calcula insp_radar.py. */
  var RAD = D.radar;
  var COLOR_ENTE = { gob: '#1d4f91', mun: '#c2571a', otr: '#7b8597' };
  var SEM_CLASE = { rojo: 'ie-rad-rojo', ambar: 'ie-rad-ambar', verde: 'ie-rad-verde' };
  function radOrden(i) {
    return function (a, b) { var A = RAD.est[a.id], B = RAD.est[b.id]; return (B ? B.v[i] : -1) - (A ? A.v[i] : -1); };
  }
  function radValor(r, i) { return i === 0 ? '$' + r.v[0].toFixed(2) : i === 1 ? mdpF(r.v[1] / 1e6) : r.v[2].toFixed(1) + ' %'; }
  function radFuente() {
    return '<a href="' + esc(RAD.fuente.url) + '" target="_blank" rel="noopener">' + esc(RAD.fuente.corto) + ', pp. ' + esc(RAD.fuente.pags) + ' ↗</a>' + ref('ref-asf-mdb2024');
  }
  function radarHtml(e) {
    var r = RAD.est[e.abbr];
    if (!r) return '';
    var t = r.t, x = r.v[0], prom = RAD.prom, s = RAD.sem[r.s], tope = Math.max(x, prom);
    var comp = x >= prom
      ? 'Es <b>' + (x / prom).toFixed(1) + ' veces</b> el promedio nacional ($' + prom.toFixed(2) + ').'
      : 'Está <b>$' + (prom - x).toFixed(2) + ' por debajo</b> del promedio nacional ($' + prom.toFixed(2) + ').';
    var seg = '', filas = '';
    r.d.forEach(function (d) {
      var w = t[7] ? d[3] / t[7] * 100 : 0;
      if (w > 0) seg += '<span class="ie-rad-seg" style="width:' + w.toFixed(3) + '%;background:' + COLOR_ENTE[d[1]] + '" title="' + esc(d[0]) + ': ' + w.toFixed(1) + ' %"></span>';
      filas += '<tr><th scope="row"><span class="ie-rad-pto" style="background:' + COLOR_ENTE[d[1]] + '" aria-hidden="true"></span>' + esc(d[0]) + '</th>' +
        '<td data-etq="Por aclarar">' + mdpF(d[3] / 1e6) + '</td><td data-etq="Parte">' + w.toFixed(1) + ' %</td>' +
        '<td data-etq="Auditorías">' + fmt(d[2]) + '</td><td data-etq="Acciones">' + fmt(d[4]) + '</td></tr>';
    });
    var lugares = RAD.crit.map(function (c, i) {
      return '<li><span class="ie-rad-l-n"><b>' + r.l[i] + '.º</b><small>de 32</small></span><span class="ie-rad-l-tx"><b>' + c[2] + ' ' + esc(c[1]) + '</b> ' +
        radValor(r, i) + ' ' + chip(c[5]) + '<small>' + esc(c[3]) + '</small></span></li>';
    }).join('');
    var matriz = e.name === r.ent ? '' : ' En la Matriz figura como «' + esc(r.ent) + '».';
    return '<section class="ie-rad ' + SEM_CLASE[r.s] + '" aria-labelledby="ieRadTit">' +
      '<h3 class="ie-h3" id="ieRadTit">🚩 Su radar de la Auditoría Superior: su lugar entre los 32 estados</h3>' +
      '<p class="ie-rad-sem"><span aria-hidden="true">' + s[0] + '</span> <b>' + esc(s[1]) + '</b>: por cada $100 revisados quedó ' + esc(s[2]) + '. ' + chip('derivado') + '</p>' +
      '<div class="ie-rad-cifras">' +
        '<div><small>Por aclarar ' + chip('oficial') + '</small><b>' + mdpF(t[7] / 1e6) + '</b></div>' +
        '<div><small>De cada $100 revisados ' + chip('derivado') + '</small><b>$' + x.toFixed(2) + '</b></div>' +
        '<div><small>Auditorías · acciones ' + chip('oficial') + '</small><b>' + fmt(t[0]) + ' · ' + fmt(t[3]) + '</b></div></div>' +
      '<div class="ie-rad-comp"><p>' + comp + '</p>' +
        '<div class="ie-rad-b"><span>' + esc(e.name) + '</span><span class="ie-rad-barra"><span class="' + SEM_CLASE[r.s] + '" style="width:' + (x / tope * 100).toFixed(2) + '%"></span></span><b>$' + x.toFixed(2) + '</b></div>' +
        '<div class="ie-rad-b"><span>Promedio nacional</span><span class="ie-rad-barra"><span class="ie-rad-prom" style="width:' + (prom / tope * 100).toFixed(2) + '%"></span></span><b>$' + prom.toFixed(2) + '</b></div>' +
        '<p class="ie-rad-op">Operación: ' + mdpF(t[7] / 1e6) + ' por aclarar ÷ ' + mdpF(t[2] / 1e6) + ' de muestra auditada × 100.</p></div>' +
      '<h4 class="ie-h4">Su lugar entre los 32 ' + chip('derivado') + '</h4><ol class="ie-rad-lug">' + lugares + '</ol>' +
      '<h4 class="ie-h4">¿Quién tiene que aclararlo? ' + chip('oficial') + '</h4>' +
      '<div class="ie-rad-pila" role="img" aria-label="Reparto de lo que quedó por aclarar entre los entes del estado">' + (seg || '<span class="ie-rad-vacia">Sin monto por aclarar</span>') + '</div>' +
      '<div class="ie-rad-tabla-caja"><table class="ie-rad-tabla"><thead><tr><th scope="col">Ente</th><th scope="col">Por aclarar</th><th scope="col">Parte ' + chip('derivado') + '</th><th scope="col">Auditorías</th><th scope="col">Acciones</th></tr></thead>' +
        '<tbody>' + filas + '</tbody></table></div>' +
      '<p class="ie-rad-op">La parte de cada ente divide su monto por aclarar entre el del estado (' + mdpF(t[7] / 1e6) + ') × 100. «Otros» es como la Matriz agrupa a los entes que no son el gobierno estatal ni los municipios.' + matriz + '</p>' +
      '<h4 class="ie-h4">Más de la Matriz ' + chip('oficial') + '</h4>' +
      celdas([['Universo seleccionado', mdpF(t[1] / 1e6)], ['Muestra auditada', mdpF(t[2] / 1e6)], ['Pliegos de observaciones (PO)', fmt(t[4])],
        ['Promociones de responsabilidad (PRAS)', fmt(t[5])], ['Recuperado durante la auditoría', mdpF(t[6] / 1e6)]]) +
      '<p class="ie-rad-op">Fuente: ' + radFuente() + '. ' + esc(RAD.nota) + ' Los criterios y el semáforo son de Auditavisión: <a href="#ie-metodo-radar">cómo se calculan</a>.</p>' +
      '</section>';
  }

  /* ---------------- Filtros y orden ---------------- */
  var VISTAS = {
    todos: { et: 'Todos', niv: ['federal', 'estatal', 'municipal'] },
    pEjecutivo: { et: '🦅 Poder Ejecutivo', niv: ['federal'], f: function (x) { return x.poder === 'ejecutivo'; },
      d: 'Presidencia, secretarías, órganos reguladores, IMSS, ISSSTE, Pemex y CFE.' },
    pLegislativo: { et: '🏛️ Poder Legislativo', niv: ['federal'], f: function (x) { return x.poder === 'legislativo'; },
      d: 'El Congreso en su conjunto (Ramo 01) y, cada uno con su expediente, la Cámara de Diputados, el Senado y la Auditoría Superior de la Federación.' },
    pJudicial: { et: '⚖️ Poder Judicial', niv: ['federal'], f: function (x) { return x.poder === 'judicial'; },
      d: 'El Poder Judicial de la Federación en su conjunto (Ramo 03) y, cada uno con su expediente, la Suprema Corte, el Órgano de Administración Judicial (antes Consejo de la Judicatura), el Tribunal Electoral y el Tribunal de Disciplina.' },
    pAutonomo: { et: '🛡️ Autónomos', niv: ['federal'], f: function (x) { return x.poder === 'autonomo'; },
      d: 'Órganos constitucionales autónomos (INE, INEGI, CNDH, FGR y los extintos en 2025) y los tribunales agrarios y de justicia administrativa, que no forman parte del Poder Judicial.' },
    incongruencias: { et: '⚖️ Con incongruencias', niv: ['federal', 'estatal', 'municipal'],
      f: function (x) { return incs(diag(x)).length > 0; }, orden: function (a, b) { return magnitud(b) - magnitud(a); },
      d: 'Dos documentos oficiales dicen cosas distintas sobre el mismo dinero. Ordenados de mayor a menor diferencia en pesos.' },
    graves: { et: '🔴 Con señal fuerte', niv: ['federal', 'estatal', 'municipal'],
      f: function (x) { return diag(x).some(function (d) { return d.e === 'grave'; }); } },
    bandera: { et: '🚩 Bandera roja de la ASF', niv: ['estatal'], radar: true,
      f: function (x) { return !!(RAD.est[x.id] && RAD.est[x.id].s === 'rojo'); }, orden: radOrden(0),
      d: 'De cada $100 que la Auditoría Superior revisó del dinero federal de los estados en la Cuenta Pública 2024, quedaron <b>$' + RAD.prom.toFixed(2) + '</b> por aclarar ' + chip('derivado') +
        ' (promedio nacional). Bandera roja: el estado dejó 1.5 veces el promedio o más (≥ $' + (RAD.prom * 1.5).toFixed(2) + '). Ordenados por cada $100 revisados. Por aclarar no es robado.' },
    nocuentas: { et: '📒 No rindieron cuentas en 2024', niv: ['municipal'],
      f: function (x) { return x.abbr !== 'CDMX' && !(x.pad && x.pad.length > 2); },
      orden: function (a, b) { return munRecibido(b) - munRecibido(a); },
      d: 'Municipios que no entregaron su cuenta de 2024 al INEGI. Ordenados por lo que ellos mismos le informaron a Hacienda haber recibido del FAIS y el FORTAMUN; las dieciséis alcaldías de la Ciudad de México no cuentan aquí porque no rinden cuenta municipal.' },
    nohacienda: { et: '📭 Sin informe a Hacienda', niv: ['municipal'],
      f: function (x) { return x.abbr !== 'CDMX' && !(x.rd && (x.rd.s || x.rd.p)); },
      d: 'Municipios que no aparecen en el Sistema de Recursos Federales Transferidos de 2024 con el FAIS ni con el FORTAMUN: ni lo recibido, ni una sola obra.' }
  };
  var ORDENES = {
    catalogo: { et: 'Como en el catálogo' },
    senales: { et: 'Más señales primero', f: function (a, b) {
      var A = cuenta(diag(a)), B = cuenta(diag(b));
      return (B.grave * 10 + B.alerta) - (A.grave * 10 + A.alerta);
    } },
    peor: { et: 'Índice: el más bajo primero', local: true, f: function (a, b) { return idxOrden(a, 1) - idxOrden(b, 1); } },
    mejor: { et: 'Índice: el más alto primero', local: true, f: function (a, b) { return idxOrden(b, -1) - idxOrden(a, -1); } },
    nombre: { et: 'Por nombre (A-Z)', f: function (a, b) { return a.nombre.localeCompare(b.nombre, 'es'); } },
    /* Los tres criterios del Radar por entidad, solo para los estados. */
    radInt: { et: 'ASF: por cada $100 revisados, mayor primero', est: 0, f: radOrden(0) },
    radMonto: { et: 'ASF: más dinero por aclarar primero', est: 1, f: radOrden(1) },
    radMun: { et: 'ASF: mayor peso de los municipios primero', est: 2, f: radOrden(2) }
  };
  function ordenVale(k) {
    var o = ORDENES[k];
    return !!o && !(o.local && st.nivel === 'federal') && !('est' in o && st.nivel !== 'estatal');
  }
  var cacheIdx = {};
  function idxDe(x) {
    var k = x.nivel + ':' + x.id;
    if (!(k in cacheIdx)) cacheIdx[k] = indice(ejes(x));
    return cacheIdx[k];
  }
  /* Los que no tienen índice van al final en los dos sentidos. */
  function idxOrden(x, s) { var i = idxDe(x); return i === null ? (s > 0 ? 1e9 : -1e9) : i; }

  var st = { nivel: 'federal', q: '', vista: 'todos', orden: 'catalogo', tope: 60, sel: null };
  /* Un solo navegador (pedido del autor, 21-10-2026): los niveles, el
     buscador, los filtros y el directorio están en la misma página. */

  /* ---------------- El directorio ---------------- */
  function tarjeta(x) {
    var dg = diag(x), c = cuenta(dg), i = idxDe(x), v = i === null ? null : veredicto(i);
    var extra = '';
    if (st.vista === 'nocuentas') {
      var r = munRecibido(x);
      extra = r >= 0 ? (x.rd.s ? 'Recibió ' : 'Registró obras por ') + simMdp(r / 1e6) + ' del FAIS y FORTAMUN (su informe a Hacienda)' : 'Tampoco informó a Hacienda';
    } else if (st.vista === 'incongruencias') {
      extra = 'Diferencia entre documentos: ' + simMdp(magnitud(x)) + ' ' + chip('derivado');
    } else if (x.nivel === 'federal') {
      extra = 'Ejerció ' + simMdp(x.fed.cp2025.ejercido) + ' en 2025 ' + chip('oficial');
    } else if (x.nivel === 'estatal' && RAD.est[x.id] && (st.vista === 'bandera' || 'est' in ORDENES[st.orden])) {
      var rr = RAD.est[x.id], ci = 'est' in ORDENES[st.orden] ? ORDENES[st.orden].est : 0;
      extra = RAD.sem[rr.s][0] + ' ' + esc(RAD.crit[ci][1]) + ': ' + radValor(rr, ci) + ' · ' + rr.l[ci] + '.º de 32 ' + chip(RAD.crit[ci][5]);
    } else if (x.nivel === 'estatal') {
      extra = 'Ramos 28 y 33 en 2026: ' + simMdp(x.est.gasto) + ' ' + chip(D.fe.gasto.estado);
    } else {
      var cf = munCifras(x);
      extra = cf ? 'Ingresó ' + simMdp(cf.ing) + ' en 2024 ' + chip('oficial') : (x.abbr === 'CDMX' ? 'Alcaldía: no rinde cuenta municipal' : 'Sin cuenta de 2024 ante el INEGI');
    }
    var sem = (c.grave ? '<span class="s-grave">🔴 ' + c.grave + ' fuerte' + (c.grave > 1 ? 's' : '') + '</span>' : '') +
      (c.alerta ? '<span class="s-alerta">🟠 ' + c.alerta + ' a revisar</span>' : '') +
      (!c.grave && !c.alerta ? '<span class="s-ok">🟢 sin señales</span>' : '');
    var abierto = st.sel && st.sel.nivel === x.nivel && st.sel.id === x.id;
    return '<li><a class="ie-tarj' + (abierto ? ' activo' : '') + '" href="#ente=' + x.nivel + ':' + encodeURIComponent(x.id) + '"' + (abierto ? ' aria-current="true"' : '') + '>' +
      '<span class="ie-tarj-ico" aria-hidden="true">' + x.icono + '</span>' +
      '<span class="ie-tarj-tx"><b>' + esc(x.nombre) + '</b><small>' + esc(x.sub) + '</small>' +
      '<small class="ie-tarj-cifra">' + extra + '</small>' +
      '<small class="ie-tarj-sem">' + sem + '</small></span>' +
      (i === null ? '<span class="ie-tarj-ir" aria-hidden="true">›</span>'
        : '<span class="ie-tarj-idx ' + v.c + '" title="Índice de salud financiera (construcción de Auditavisión)"><b>' + Math.round(i) + '</b><small>índice</small></span>') +
      '</a></li>';
  }

  function filtrar(nivel, q) {
    var todos = entes(nivel);
    if (!q) return todos;
    var partes = plano(q).trim().split(/\s+/);
    return todos.filter(function (x) { return partes.every(function (w) { return x.buscar.indexOf(w) !== -1; }); });
  }

  function pintarNiveles() {
    [].forEach.call(raiz.querySelectorAll('.ie-nivel'), function (b) {
      var k = b.getAttribute('data-nivel'), act = k === st.nivel;
      b.classList.toggle('activo', act);
      b.setAttribute('aria-selected', act ? 'true' : 'false');
      b.tabIndex = act ? 0 : -1;
      var n = b.querySelector('.ie-nivel-n');
      var listo = k !== 'municipal' || window.AUDIT_MUNICIPIOS;
      if (st.q && listo) n.textContent = fmt(filtrar(k, st.q).length) + ' de ' + fmt(entes(k).length);
      else n.textContent = k === 'municipal' && !listo ? (D.mun.n ? fmt(D.mun.n) : '—') : fmt(entes(k).length);
    });
    var panel = document.getElementById('ieDir');
    if (panel) panel.setAttribute('aria-labelledby', 'ieTab-' + st.nivel);
  }

  function pintarControles(todos) {
    var cont = document.getElementById('ieCtl');
    if (VISTAS[st.vista].niv.indexOf(st.nivel) === -1) st.vista = 'todos';
    if (!ordenVale(st.orden)) st.orden = 'catalogo';
    var V = VISTAS[st.vista];
    var chips = Object.keys(VISTAS).filter(function (k) { return VISTAS[k].niv.indexOf(st.nivel) > -1; }).map(function (k) {
      var n = k === 'todos' ? todos.length : todos.filter(VISTAS[k].f).length;
      return '<button type="button" class="ie-vista' + (k === st.vista ? ' activo' : '') + '" aria-pressed="' + (k === st.vista) + '" data-vista="' + k + '">' +
        VISTAS[k].et + ' <b>' + fmt(n) + '</b></button>';
    }).join('');
    var ord = Object.keys(ORDENES).filter(ordenVale).map(function (k) {
      return '<option value="' + k + '"' + (k === st.orden ? ' selected' : '') + '>' + ORDENES[k].et + '</option>';
    }).join('');
    cont.innerHTML = '<div class="ie-vistas" role="group" aria-label="Filtrar la lista">' + chips + '</div>' +
      '<div class="ie-orden"><label for="ieOrden">Ordenar</label><select id="ieOrden">' + ord + '</select></div>' +
      (V.d ? '<p class="ie-vista-d">' + V.d + '</p>' : '') +
      ('est' in ORDENES[st.orden] ? '<p class="ie-vista-d"><b>' + RAD.crit[ORDENES[st.orden].est][2] + ' ' + esc(RAD.crit[ORDENES[st.orden].est][1]) + ':</b> ' +
        esc(RAD.crit[ORDENES[st.orden].est][3]) + ' ' + chip(RAD.crit[ORDENES[st.orden].est][5]) + ' Fuente: ' + radFuente() + '.</p>' : '');
  }

  function pintarLista() {
    var lista = document.getElementById('ieLista'), conteo = document.getElementById('ieConteo'), mas = document.getElementById('ieMas');
    if (st.nivel === 'municipal' && !window.AUDIT_MUNICIPIOS) {
      document.getElementById('ieCtl').innerHTML = '';
      conteo.textContent = '';
      lista.innerHTML = '<li class="ie-cargando" role="status">⏳ Cargando el padrón de ' + (D.mun.n ? fmt(D.mun.n) : 'los') + ' municipios del INEGI y su rendición de cuentas…</li>';
      mas.innerHTML = '';
      cargarMun().then(pintarTodo, function () {
        lista.innerHTML = '<li class="ie-cargando">No se pudo cargar el padrón municipal. <button type="button" class="ie-btn" data-reintentar="1">Reintentar</button></li>';
      });
      return;
    }
    var todos = filtrar(st.nivel, st.q);
    pintarControles(todos);
    var V = VISTAS[st.vista];
    var l = V.f ? todos.filter(V.f) : todos;
    var O = st.orden !== 'catalogo' ? ORDENES[st.orden].f : V.orden;
    if (O) l = l.slice().sort(O);
    if (!l.length) {
      conteo.innerHTML = 'Nadie coincide en el nivel <b>' + st.nivel + '</b>' + (st.q ? ' con «' + esc(st.q) + '»' : '') + '. Prueba en otro nivel o ' +
        '<button type="button" class="ie-enlace" data-limpiar="1">ve la lista completa</button>.';
      lista.innerHTML = '';
      mas.innerHTML = '';
      return;
    }
    var vis = l.slice(0, st.tope);
    conteo.innerHTML = fmt(l.length) + (l.length === 1 ? ' ente' : ' entes') + (st.q ? ' coinciden con «' + esc(st.q) + '»' : '') +
      '. Pulsa uno para abrir su ficha técnica.' + (l.length > vis.length ? ' Se muestran ' + fmt(vis.length) + '; escribe en el buscador para encontrar el tuyo.' : '') +
      (st.q ? ' <button type="button" class="ie-enlace" data-limpiar="1">Quitar la búsqueda</button>' : '');
    lista.innerHTML = vis.map(tarjeta).join('');
    mas.innerHTML = l.length > vis.length
      ? '<button type="button" class="ie-btn ie-mas" data-mas="1">Mostrar más (' + fmt(Math.min(120, l.length - vis.length)) + ' de ' + fmt(l.length - vis.length) + ' restantes)</button>' : '';
  }

  function pintarTodo() { pintarNiveles(); pintarLista(); }

  function ponerNivel(k, enfocar) {
    if (!VISTAS.todos.niv.includes(k)) return;
    st.nivel = k; st.tope = 60;
    if (k === 'municipal' && !window.AUDIT_MUNICIPIOS) cargarMun().catch(function () {});
    pintarTodo();
    if (enfocar) { var t = document.getElementById('ieTab-' + k); if (t) t.focus(); }
  }

  /* ---------------- El expediente ---------------- */
  function resumenHtml(dg) {
    var c = cuenta(dg);
    var cl = c.grave ? 's-grave' : c.alerta ? 's-alerta' : 's-ok';
    var t = (c.grave ? c.grave + ' señal' + (c.grave > 1 ? 'es' : '') + ' fuerte' + (c.grave > 1 ? 's' : '') : '') +
      (c.grave && c.alerta ? ' y ' : '') + (c.alerta ? c.alerta + ' a revisar' : '') +
      (!c.grave && !c.alerta ? 'Sin señales en las ' + dg.length + ' preguntas' : '');
    return '<div class="ie-resumen ' + cl + '">' +
      '<p class="ie-resumen-t">' + (c.grave ? '🔴 ' : c.alerta ? '🟠 ' : '🟢 ') + t + '</p>' +
      '<ol class="ie-mini">' + dg.map(function (x) {
        return '<li><a href="#ie-q-' + x.k + '" class="s-' + x.e + '"><span class="ie-pt s-' + x.e + '" aria-hidden="true"></span>' +
          '<span class="ie-mini-q">' + x.q + '</span><span class="ie-mini-v">' + SEM[x.e].t + '</span></a></li>';
      }).join('') + '</ol>' +
      '<p class="ie-resumen-d">Preguntas que cualquiera puede hacerle a una autoridad, respondidas con sus propios reportes y con lo que encontró la Auditoría Superior. ' +
      'Una señal no es una acusación: es algo que la autoridad debe explicar.</p></div>';
  }

  function senalesHtml(dg) {
    return '<ol class="ie-senales">' + dg.map(function (x) {
      return '<li class="ie-senal s-' + x.e + '" id="ie-q-' + x.k + '">' +
        '<p class="ie-senal-q"><span aria-hidden="true">' + x.ico + '</span> ' + x.q + '</p>' +
        '<p class="ie-senal-v"><span class="ie-sem-et">' + SEM[x.e].ico + ' ' + SEM[x.e].t + ':</span> <b>' + x.v + '</b> ' +
        chip(x.e === 'sin' ? 'pendiente' : 'derivado', x.e === 'sin' ? x.pend : '') + '</p>' +
        '<p class="ie-senal-d">' + x.d + (x.f ? ' ' + x.f : '') + '</p></li>';
    }).join('') + '</ol>';
  }

  function incHtml(dg, resp) {
    var l = incs(dg);
    if (!l.length) return '';
    return '<section class="ie-inc" aria-label="Incongruencias en su rendición de cuentas">' +
      '<h4 class="ie-inc-tit">⚖️ Incongruencias en su rendición de cuentas</h4>' +
      '<p class="ie-inc-intro">Dos documentos oficiales dicen cosas distintas sobre el mismo dinero. <b>Explicar la diferencia le corresponde ' +
      ('a ' + resp).replace(/^a el /, 'al ') + '</b>, no a quien la consulta: mientras no lo haga, cualquiera de las dos cifras puede estar mal.</p>' +
      '<ul class="ie-inc-lista">' + l.map(function (i) {
        var mx = Math.max(Math.abs(i.a[1]), Math.abs(i.b[1])) || 1;
        return '<li class="ie-inc-it s-' + i.e + '"><p class="ie-inc-tema">' + SEM[i.e].ico + ' ' + i.tema + '</p>' +
          '<div class="ie-inc-par"><span class="ie-inc-doc">' + i.a[0] + '</span><b>' + mdpF(i.a[1]) + '</b>' +
          '<span class="ie-inc-barra" aria-hidden="true"><span style="width:' + (Math.abs(i.a[1]) / mx * 100).toFixed(1) + '%"></span></span></div>' +
          '<div class="ie-inc-par"><span class="ie-inc-doc">' + i.b[0] + '</span><b>' + mdpF(i.b[1]) + '</b>' +
          '<span class="ie-inc-barra b" aria-hidden="true"><span style="width:' + (Math.abs(i.b[1]) / mx * 100).toFixed(1) + '%"></span></span></div>' +
          '<p class="ie-inc-dif">Diferencia: <b>' + (i.dif >= 0 ? '+' : '−') + mdpF(Math.abs(i.dif)) + '</b>' +
          (i.pct !== null && isFinite(i.pct) ? ' (' + pctTxt(i.pct) + ')' : '') + ' ' + chip('derivado') +
          ' <small>segunda cifra menos la primera</small></p>' +
          (i.nota ? '<p class="ie-inc-nota">' + i.nota + '</p>' : '') + '</li>';
      }).join('') + '</ul></section>';
  }

  function celdas(lista) {
    return '<div class="ie-ident">' + lista.map(function (p) {
      return '<div class="ie-ident-c"><span class="ie-ident-k">' + p[0] + '</span><span class="ie-ident-v">' + p[1] + '</span></div>';
    }).join('') + '</div>';
  }

  function circuloSVG(valor, v) {
    var R = 54, C = 2 * Math.PI * R;
    return '<svg class="ie-circ ' + v.c + '" viewBox="0 0 140 140" role="img" aria-label="Índice de salud financiera: ' + Math.round(valor) + ' de 100">' +
      '<circle class="ie-circ-fondo" cx="70" cy="70" r="' + R + '" fill="none" stroke-width="13"/>' +
      '<circle class="ie-circ-aro" cx="70" cy="70" r="' + R + '" fill="none" stroke-width="13" stroke-linecap="round" transform="rotate(-90 70 70)" ' +
      'stroke-dasharray="' + C.toFixed(1) + '" stroke-dashoffset="' + C.toFixed(1) + '" data-fin="' + (C * (1 - valor / 100)).toFixed(2) + '"/>' +
      '<text x="70" y="76" text-anchor="middle" class="ie-circ-num">' + Math.round(valor) + '</text>' +
      '<text x="70" y="96" text-anchor="middle" class="ie-circ-pie">de 100</text></svg>';
  }

  function circuloHtml(ej, i, esEstado) {
    if (!ej) {
      return '<div class="ie-nota"><b>Sin círculo de salud financiera.</b> El índice necesita, del mismo año, su cuenta ante el INEGI y una auditoría integral de la ASF; ' +
        'a este expediente le falta al menos una. No se dibuja con supuestos: arriba están las preguntas que sí se pueden responder.</div>';
    }
    var v = veredicto(i), pesos = [P.autonomia, P.observado, P.holgura];
    return '<section class="ie-salud" aria-label="Círculo de salud financiera">' +
      '<div class="ie-salud-circ">' + circuloSVG(i, v) +
      '<div class="ie-vered ' + v.c + '"><b>' + v.ico + ' ' + v.t + '</b><span>' + v.d + '</span></div></div>' +
      '<div class="ie-salud-ejes"><h4 class="ie-h4">Los tres ejes que forman ese número ' + chip('derivado') + '</h4><ol class="ie-ejes">' +
      ej.map(function (e, k) {
        return '<li class="ie-eje"><div class="ie-eje-cab"><span class="ie-eje-et">' + e.ico + ' ' + e.et + '</span>' +
          '<span class="ie-eje-peso">' + pesos[k] + '% del índice</span><span class="ie-eje-v">' + Math.round(e.v) + '/100</span></div>' +
          '<div class="ie-eje-riel"><span class="ie-eje-barra" style="width:0%" data-w="' + e.v.toFixed(1) + '"></span></div>' +
          '<p class="ie-eje-crudo">' + e.crudo + '</p><p class="ie-eje-expl">' + e.expl + '</p></li>';
      }).join('') + '</ol>' +
      '<p class="ie-formula">Índice = autonomía × ' + P.autonomia + '% + limpieza × ' + P.observado + '% + ' + (esEstado ? 'holgura frente a la deuda' : 'esfuerzo recaudatorio') +
      ' × ' + P.holgura + '%. <a href="#ie-metodo-local" data-abre-det="1">Ver la fórmula completa y los umbrales</a>. <em>Es una construcción de Auditavisión, no una calificación crediticia, ni una sanción, ni un dictamen de la Auditoría Superior.</em></p>' +
      '</div></section>';
  }

  function munGobierno(ente) {
    var g = ente.rd && ente.rd.g;
    if (ente.abbr === 'CDMX') {
      return g && g[0] ? esc(g[0]) + (g[1] ? ' (' + esc(g[1]) + ')' : '') + ' ' + chip('oficial') + refMun('inafed') +
        '<br><small>Alcaldía de ' + fecha(g[2]) + ' a ' + fecha(g[3]) + '.</small>' : 'Sin registro en el padrón del INAFED ' + chip('pendiente', 'alcaldes-inafed');
    }
    if (!g || !g[0]) return 'Sin registro en el padrón del INAFED ' + chip('pendiente', 'alcaldes-inafed') + refMun('inafed');
    var t = esc(g[0]) + (g[1] ? ' (' + esc(g[1]) + ')' : ' (partido no registrado)') + ' ' + chip(g[5] ? 'pendiente' : 'oficial') + refMun('inafed');
    if (g[2] && g[3]) t += '<br><small>Periodo de ' + fecha(g[2]) + ' a ' + fecha(g[3]) + '.' +
      (g[3] < '2024-12-31' ? ' Gobernó la mayor parte de 2024; el padrón del INAFED consultado aún no registra a quien le sucedió.' : '') + '</small>';
    if (g[5]) t += '<br><small><b>Dato por confirmar:</b> el INAFED registra a esta misma persona en otro municipio (clave ' + g[5].join(', ') + '). Es una incongruencia de la fuente oficial.</small>';
    return t;
  }

  function estPoderes(e) {
    var lugar = function (vals, v) { return 1 + vals.filter(function (x) { return x > v; }).length; };
    var asfTxt = 'Esta base no registra auditorías de la ASF a su nombre en la Cuenta Pública 2024.';
    if (e.asfC && e.asfC.length) {
      var rid = (D.fP.asfCongresos || {})['Congreso de ' + e.name];
      asfTxt = 'La ASF le auditó en la Cuenta Pública 2024 las participaciones federales que ejerció (auditoría ' + e.asfC[0][0] + ')' + ref(rid) + ': ' +
        e.asfC.filter(function (x) { return !/Universo|Muestra|incluidas/.test(x[1]); }).map(function (x) { return x[1].toLowerCase() + ', ' + mdpF(x[2] / 1e6); }).join('; ') + '.';
    }
    return '<section class="ie-poderes" aria-label="Los tres poderes del estado"><h4 class="ie-h4">🏛️ Los tres poderes del estado</h4>' +
      celdas([
        ['🦅 Poder Ejecutivo', 'Gobierno del estado: ' + esc(e.gobernador) + ' (' + esc(e.partido) + ') ' + chip('pendiente') +
          '<br><small>El nombre aún no cita documento. Su dinero es el que revisan las preguntas de arriba.</small>'],
        ['🏛️ Poder Legislativo', e.cong != null
          ? 'El Congreso ejerció ' + mdpF(e.cong) + ' en 2024 ' + chip('oficial') + refFed('cnple') +
            '<br><small>El ' + lugar(D.congresos, e.cong) + '.º que más gastó de los 32 congresos locales. ' + asfTxt + '</small>'
          : 'Sin dato ' + chip('pendiente')],
        ['⚖️ Poder Judicial', e.jud != null
          ? 'El Poder Judicial del estado ejerció ' + mdpF(e.jud) + ' en 2024 ' + chip('oficial') + refFed('cnije') +
            '<br><small>El ' + lugar(D.juds, e.jud) + '.º que más gastó de los 32 poderes judiciales estatales.</small>'
          : 'Sin dato ' + chip('pendiente')]
      ]) +
      '<p class="ie-nota-p">Las cifras del Congreso y del Poder Judicial las reporta cada órgano al INEGI en sus censos de gobierno. ' +
      'A los congresos y tribunales locales los fiscaliza sobre todo la auditoría superior de cada estado; la ASF sólo revisa el dinero federal que reciben. ' +
      'Integrar esos informes estatales está pendiente.</p></section>';
  }

  function fedAuditorias(f) {
    if (!f.asf || !f.asf.length) return '';
    var et = [['recomendación', 'recomendaciones'], ['recomendación al desempeño', 'recomendaciones al desempeño'],
      ['promoción del ejercicio de la facultad de comprobación fiscal', 'promociones del ejercicio de la facultad de comprobación fiscal'],
      ['solicitud de aclaración', 'solicitudes de aclaración'],
      ['promoción de responsabilidad administrativa sancionatoria', 'promociones de responsabilidad administrativa sancionatoria'],
      ['pliego de observaciones', 'pliegos de observaciones']];
    return '<section class="ie-nota"><h4 class="ie-h4">Auditorías de la ASF a su nombre, Cuenta Pública 2024 ' + chip('oficial') + refFed('asf2024') + '</h4>' +
      '<ul class="ie-asf-lista">' + f.asf.map(function (a) {
        var acc = a.acc.slice(0, 6).map(function (n, i) { return n ? n + ' ' + et[i][n === 1 ? 0 : 1] : ''; }).filter(Boolean);
        return '<li><b>Auditoría ' + a.num + '</b> · ' + a.titulo + ' · ' + a.tipo + ' · ' + a.entrega + '.ª entrega. ' +
          'Revisó el ' + a.repr.toFixed(2) + ' % del universo que seleccionó. ' +
          (a.res[0] ? a.res[0] + ' resultado' + (a.res[0] === 1 ? '' : 's') + ' con observación ya solventada o atendida. ' : '') +
          (a.res[1] ? a.res[1] + ' resultado' + (a.res[1] === 1 ? '' : 's') + ' con observaciones y acciones. ' : '') +
          (acc.length ? 'Acciones: ' + acc.join(', ') + '. ' : 'Sin acciones. ') +
          (a.recuperaciones > 0 ? 'Recuperado durante la auditoría: ' + mdpF(a.recuperaciones / 1e6) + '. ' : '') +
          (a.porAclarar > 0 ? '<b>Por aclarar: ' + mdpF(a.porAclarar / 1e6) + '.</b>' : 'Nada por aclarar.') + '</li>';
      }).join('') + '</ul></section>';
  }

  /* ---------------- La ficha técnica: encabezado y sello ---------------- */
  /* Pedido del autor (21-10-2026): el expediente se emite como ficha técnica
     de Auditavisión, con el mismo encabezado y el mismo sello que el Estado
     de Cuenta (estado-administracion.js) y la nota técnica del bot: arriba la
     banda, el logo, el folio y la fecha; abajo el sello, la huella SHA-256 y
     la leyenda. La huella firma el texto de la ficha (textoFicha sin el
     enlace): la misma ficha con las mismas cifras da el mismo folio. */
  var BANDA = document.getElementById('ieExp').getAttribute('data-cabecera');
  var CORTE = { federal: 'Cuenta Pública 2025 y avance de 2026', estatal: 'Ejercicio 2024; Ramos 28 y 33 de 2026', municipal: 'Ejercicio 2024' };
  function hoyFecha() {
    var d = new Date();
    return d.toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' }) + ', ' + d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
  }
  function selloSitio() { var b = document.querySelector('.apartado-pie-txt b'); return b ? b.textContent : ''; }
  function enlaceEnte(ente) { return location.href.split('#')[0] + '#ente=' + ente.nivel + ':' + encodeURIComponent(ente.id); }
  function huellaDe(txt) {
    if (!(window.crypto && crypto.subtle && window.TextEncoder)) return Promise.resolve(null);
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(txt)).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return ('0' + x.toString(16)).slice(-2); }).join('');
    }).catch(function () { return null; });
  }
  function folio(h) { return 'AV-FT-' + h.slice(0, 8).toUpperCase(); }
  function sello(fol) {
    var id = 'ieArco' + Math.random().toString(36).slice(2, 7);
    return '<svg class="ie-ft-sello-svg" viewBox="0 0 120 120" role="img" aria-label="Ficha técnica de Auditavisión">' +
      '<defs><path id="' + id + '" d="M60,60 m-44,0 a44,44 0 1,1 88,0 a44,44 0 1,1 -88,0"/></defs>' +
      '<circle cx="60" cy="60" r="57" fill="none" stroke="currentColor" stroke-width="2.5"/>' +
      '<circle cx="60" cy="60" r="35" fill="none" stroke="currentColor" stroke-width="1.2"/>' +
      '<text font-size="9.4" font-weight="800" letter-spacing="3.5" fill="currentColor"><textPath href="#' + id + '">AUDITAVISIÓN · FICHA TÉCNICA ·</textPath></text>' +
      '<text x="60" y="58" text-anchor="middle" font-size="22" font-weight="900" fill="currentColor">✓</text>' +
      '<text x="60" y="74" text-anchor="middle" font-size="7.5" font-weight="800" fill="currentColor">' + esc(fol ? fol.split('-').slice(-1)[0] : '········') + '</text></svg>';
  }
  /* Los botones van fuera de la hoja: no se imprimen ni entran en la huella. */
  function acciones() {
    return '<div class="ie-exp-acc">' +
      '<button type="button" class="ie-btn ie-btn-p" data-pdf="1"><span aria-hidden="true">🖨️</span> Descargar en PDF</button>' +
      '<button type="button" class="ie-btn" data-copiar="ficha"><span aria-hidden="true">📋</span> Copiar ficha</button>' +
      '<button type="button" class="ie-btn" data-copiar="enlace"><span aria-hidden="true">🔗</span> Copiar enlace</button>' +
      '<button type="button" class="ie-btn ie-cerrar" data-cerrar="1" aria-label="Cerrar el expediente y volver al directorio">✕ <span>Cerrar</span></button>' +
      '</div>';
  }

  function cabecera(ente, nivelTxt, sub) {
    return (BANDA ? '<div class="ie-ft-banda"><img src="' + esc(BANDA) + '" alt=""></div>' : '') +
      '<header class="ie-ft-cab">' +
      '<div class="ie-ft-marca"><img src="assets/auditor/img/logo-auditavision.svg" alt="" width="104" height="81" decoding="sync"><div><b>Auditavisión</b><small>El gasto público, a la vista</small></div></div>' +
      '<div class="ie-ft-tit"><span class="ie-ft-tipo">Ficha técnica · ' + nivelTxt + '</span>' +
      '<h2 class="ie-exp-nom" id="ieExpTit" tabindex="-1"><span class="ie-exp-ico" aria-hidden="true">' + ente.icono + '</span> ' + esc(ente.nombre) + '</h2>' +
      '<p class="ie-exp-sub">' + esc(sub) + '</p></div>' +
      '<dl class="ie-ft-meta"><div><dt>Folio</dt><dd class="ie-ft-folio">calculando…</dd></div><div><dt>Expedida</dt><dd>' + esc(hoyFecha()) + '</dd></div>' +
      '<div><dt>Cifras de</dt><dd>' + esc(CORTE[ente.nivel]) + '</dd></div></dl></header>';
  }

  function pie(fuentes, ente) {
    return '<footer class="ie-exp-pie"><p class="ie-fu">🔗 Fuentes: ' + fuentes + '</p>' +
      '<p class="ie-fu">Los umbrales de los semáforos y el índice son de Auditavisión y se pueden discutir; los datos son oficiales. <a href="#ie-metodo">Cómo se lee</a>.</p>' +
      '<div class="ie-ft-sello"><div class="ie-ft-sello-img">' + sello(null) + '</div><div class="ie-ft-sello-tx">' +
      '<b>Ficha técnica de Auditavisión</b>' +
      '<p>Folio <b class="ie-ft-folio">calculando…</b> · Versión de la plataforma <b>' + esc(selloSitio()) + '</b></p>' +
      '<p class="ie-ft-huella">Huella digital (SHA-256 de la ficha): <code>calculando…</code></p>' +
      '<p>Compruébala en <span class="ie-ft-liga">' + esc(enlaceEnte(ente)) + '</span>: al abrirla se vuelve a calcular la huella, y si coincide, las cifras no han cambiado.</p>' +
      '<p class="ie-ft-leyenda">Lo expide Auditavisión, plataforma ciudadana de fiscalización del gasto público. <b>No es un documento oficial</b> del gobierno, del Congreso ni de la Auditoría Superior. ' +
      'El sello certifica dos cosas: que cada cifra proviene de la fuente oficial citada, y que el contenido no se ha alterado desde que se expidió. Si cambia una sola cifra, la huella ya no coincide. ' +
      'Los semáforos y el índice son una construcción de Auditavisión, no un dictamen: una señal no es una acusación.</p>' +
      '</div></div></footer>';
  }
  function firma(doc) {
    huellaDe(cuerpoFicha()).then(function (hx) {
      if (!doc.isConnected) return;
      var fol = hx ? folio(hx) : null;
      st.folio = fol; st.huella = hx;
      Array.prototype.forEach.call(doc.querySelectorAll('.ie-ft-folio'), function (el) { el.textContent = fol || 'no disponible en este navegador'; });
      doc.querySelector('.ie-ft-huella code').textContent = hx ? hx.replace(/(.{16})/g, '$1 ').trim() : 'no disponible en este navegador';
      doc.querySelector('.ie-ft-sello-img').innerHTML = sello(fol);
    });
  }

  function expFederal(ente) {
    var f = ente.fed, dg = diag(ente);
    var hijos = D.fed.filter(function (o) { return o.padre === f.id; });
    var padre = f.padre ? buscarEnte('federal', f.padre) : null;
    var enl = function (o, txt) { return '<a class="ie-chipa" href="#ente=federal:' + o.id + '">' + o.icono + ' ' + txt + '</a>'; };
    var rel = hijos.length
      ? '<div class="ie-nota"><b>Órganos que lo integran.</b> Cada uno tiene presupuesto propio y su propio expediente: <span class="ie-chipas">' +
        hijos.map(function (o) { return enl(o, esc(o.nombre) + ' · ' + simMdp(o.cp2025.ejercido) + ' en 2025'); }).join('') + '</span></div>'
      : padre
        ? '<div class="ie-nota"><b>Forma parte del ' + esc(padre.nombre) + '.</b> ' + (f.nota && !f.asfNoAplica ? f.nota + ' ' : '') +
          '<span class="ie-chipas">' + enl(padre.fed, 'Ver el ' + esc(padre.nombre) + ' completo') + '</span></div>'
        : '';
    var c = [['Aprobado 2025', simMdp(f.cp2025.original)], ['Modificado 2025', simMdp(f.cp2025.modificado)],
      ['Ejercido 2025', simMdp(f.cp2025.ejercido)], ['Pagado 2025', simMdp(f.cp2025.pagado)],
      ['Aprobado 2026', f.av2026 ? simMdp(f.av2026.aprobado) : '—'], ['Pagado a junio de 2026', f.av2026 ? simMdp(f.av2026.pagado) : '—']];
    if (f.cp2024) c.unshift(['Ejercido 2024', simMdp(f.cp2024.ejercido)]);
    if (f.id === 'scjn' && D.scjnAgo) c.push(['Ejercido al 31 de agosto de 2026, según la propia Corte', simMdp(D.scjnAgo.ejercido / 1e6) + ref('ref-scjn-ejercicio2026')]);
    c = c.map(function (p) { return [p[0] + ' ' + (p[1] === '—' ? '' : chip('oficial')), p[1]]; });
    var exps = (f.exps || []).map(function (x) { return '<a class="ie-chipa" href="expedientes.html#exp-' + encodeURIComponent(x[0]) + '">' + x[1] + ' ' + esc(x[2]) + '</a>'; }).join('');
    var usadas = [];
    if (f.padre) {
      if (f.cp2024) usadas.push('cp2024');
      (f.cotejos || []).forEach(function (cj) { [cj.a[2], cj.b[2]].forEach(function (k) { if (usadas.indexOf(k) === -1 && !D.fF[k]) usadas.push(k); }); });
    }
    return cabecera(ente, 'Expediente federal · ' + D.poderes[ente.poder][0] + ' · Ramo ' + f.ramo, f.tipo) +
      resumenHtml(dg) +
      incHtml(dg, f.padre ? 'el propio órgano, que es quien reporta las dos cifras' : 'el propio ente, que reporta ambas cifras a Hacienda') +
      '<h3 class="ie-h3">Su dinero, en millones de pesos</h3>' + celdas(c) +
      rel +
      '<h3 class="ie-h3">Las preguntas, una por una</h3>' + senalesHtml(dg) +
      fedAuditorias(f) +
      (exps ? '<div class="ie-nota"><b>Expedientes de la ASF sobre este ente.</b> Informe por informe, con sus claves de auditoría: <span class="ie-chipas">' + exps + '</span></div>' : '') +
      pie(esc(D.fF.cp2025.corto) + refFed('cp2025') + ' · ' + esc(D.fF.av2026.corto) + refFed('av2026') + ' · ' + esc(D.fF.asf2024.corto) + refFed('asf2024') +
        usadas.map(function (k) { return ' · ' + esc(D.fP[k].corto) + refFed(k); }).join('') + '.', ente);
  }

  function expLocal(ente) {
    var esEstado = ente.nivel === 'estatal', e = ente.est, dg = diag(ente), ej = ejes(ente), i = indice(ej);
    var ident;
    if (esEstado) {
      ident = [['Quien gobierna', esc(e.gobernador) + ' (' + esc(e.partido) + ') ' + chip('pendiente')],
        ['Capital', esc(e.capital)],
        ['Población a mitad de 2026', fmt(e.pobPersonas || Math.round(e.pob * 1e6)) + ' personas (CONAPO)' + chipCampo('pob', e.abbr)],
        ['Ramos 28 y 33 (2026)', simMdp(e.gasto) + chipCampo('gasto', e.abbr)],
        ['Ramos 28 y 33 por habitante', '$' + fmt(e.pc) + chipCampo('pc', e.abbr)],
        ['Recaudación propia en 2024', simMdp(e.recaudacionPropia) + (sinFuente('recaudacionPropia', e.abbr) ? ' (pendiente de fuente)' : ' (INEGI)') + chipCampo('recaudacionPropia', e.abbr)]];
    } else {
      var c = munCifras(ente), s = ente.rd && ente.rd.s, pr = ente.rd && ente.rd.p;
      ident = [['Quién gobernó', munGobierno(ente)],
        ['Estado', e ? esc(e.name) : ente.abbr],
        ['Clave INEGI', ente.id],
        ['Ingresos 2024 (INEGI)', c ? simMdp(c.ing) + ' ' + chip('oficial') : (ente.abbr === 'CDMX' ? 'No rinde cuenta municipal' : 'No entregó su cuenta ' + chip('pendiente', 'municipios-sin-cuenta'))],
        ['FAIS + FORTAMUN 2024 recibidos (su informe a Hacienda)', s ? simMdp((s[0] + s[1]) / 1e6) + ' ' + chip('derivado') + ' <small>suma de los dos fondos</small>' : 'Sin informe ' + chip('pendiente')],
        ['FAIS + FORTAMUN 2024 en obras registradas ante Hacienda', pr ? simMdp((pr[0] + pr[1]) / 1e6) + ' ' + chip('derivado') + ' <small>suma de los dos fondos</small>' : 'Ninguna ' + chip('pendiente')]];
    }
    var fuentes = esEstado
      ? 'INEGI, finanzas públicas estatales 2024' + refEst('inegi2024') + ' · SHCP, Cuenta Pública 2024' + refEst('cp2024') +
        ' · ASF, Matriz de Datos Básicos CP 2024' + ref('ref-asf-mdb2024') + ' · SHCP, Sistema de Alertas.'
      : 'INEGI, EFIPEM municipal 2016-2025' + refMun('inegi') + ' · SHCP, Sistema de Recursos Federales Transferidos 2024' + refMun('srft') +
        ' · INAFED, presidencias municipales' + refMun('inafed') + ' · ASF, Matriz de Datos Básicos CP 2024' + refMun('asf') + '.';
    var verMas = esEstado
      ? '<div class="ie-nota"><b>Para seguir:</b> <span class="ie-chipas"><a class="ie-chipa" href="?nivel=estatal&amp;orden=radInt#ie-dir">🚩 Los 32 estados, por lo que quedó por aclarar</a>' +
        '<a class="ie-chipa" href="numeros-las-32-entidades.html">🗺️ Las 32 entidades</a></span></div>'
      : '<div class="ie-nota"><b>Para seguir:</b> <span class="ie-chipas">' + (e ? '<a class="ie-chipa" href="#ente=estatal:' + e.abbr + '">🗺️ El gobierno de ' + esc(e.name) + '</a>' : '') +
        '<a class="ie-chipa" href="numeros-los-municipios.html">🏙️ Los municipios, en Números</a></span></div>';
    return cabecera(ente, 'Expediente ' + (esEstado ? 'estatal' : 'municipal'), ente.sub) +
      resumenHtml(dg) +
      incHtml(dg, esEstado ? 'el gobierno del estado y a Hacienda, que deben conciliar sus registros' : 'el ayuntamiento, que firmó los dos reportes') +
      '<h3 class="ie-h3">Ficha</h3>' + celdas(ident) +
      (esEstado ? estPoderes(e) : '') +
      '<h3 class="ie-h3">Las preguntas, una por una</h3>' + senalesHtml(dg) +
      (esEstado ? radarHtml(e) : '') +
      '<h3 class="ie-h3">El círculo de salud financiera</h3>' + circuloHtml(ej, i, esEstado) +
      verMas + pie(fuentes, ente);
  }

  function animar(cont) {
    var aro = cont.querySelector('.ie-circ-aro');
    var barras = cont.querySelectorAll('.ie-eje-barra');
    var fin = function () {
      if (aro) aro.setAttribute('stroke-dashoffset', aro.getAttribute('data-fin'));
      [].forEach.call(barras, function (b) { b.style.width = b.getAttribute('data-w') + '%'; });
    };
    if (reducido) fin(); else requestAnimationFrame(function () { requestAnimationFrame(fin); });
  }

  function abrir(nivel, id, desdeHash) {
    var cont = document.getElementById('ieExp');
    if (nivel === 'municipal' && !window.AUDIT_MUNICIPIOS) {
      cont.hidden = false;
      cont.innerHTML = '<p class="ie-cargando" role="status">⏳ Cargando el expediente municipal…</p>';
      cargarMun().then(function () { abrir(nivel, id, desdeHash); pintarTodo(); }, function () {
        cont.innerHTML = '<p class="ie-cargando">No se pudo cargar el padrón municipal. Revisa tu conexión.</p>';
      });
      return;
    }
    var ente = buscarEnte(nivel, id);
    if (!ente) {
      cont.hidden = false;
      cont.innerHTML = '<p class="ie-cargando">No encontramos ese ente en el directorio. <button type="button" class="ie-enlace" data-cerrar="1">Volver al directorio</button></p>';
      return;
    }
    st.sel = { nivel: nivel, id: id };
    if (st.nivel !== nivel) { st.nivel = nivel; st.tope = 60; }
    st.folio = st.huella = null;
    cont.innerHTML = acciones() + '<article class="ie-exp-marco">' + (nivel === 'federal' ? expFederal(ente) : expLocal(ente)) + '</article>';
    cont.hidden = false;
    firma(cont.querySelector('.ie-exp-marco'));
    animar(cont);
    pintarTodo();
    document.title = ente.nombre + ' · Auditor de entes públicos · Auditavisión';
    var t = document.getElementById('ieExpTit');
    if (t) {
      t.focus({ preventScroll: true });
      irA(cont);
    }
  }

  /* Sube hasta el elemento sin dejarlo debajo de la cabecera fija. */
  function irA(el) {
    var cab = document.querySelector('.site-top-nav');
    var alto = cab && getComputedStyle(cab).position.match(/fixed|sticky/) ? cab.getBoundingClientRect().height : 0;
    window.scrollTo({ top: el.getBoundingClientRect().top + window.pageYOffset - alto - 12, behavior: reducido ? 'auto' : 'smooth' });
  }

  var tituloOriginal = document.title;
  function cerrar() {
    var sel = st.sel;
    st.sel = null;
    var cont = document.getElementById('ieExp');
    cont.hidden = true;
    cont.innerHTML = '';
    document.title = tituloOriginal;
    if (/^#ente=/.test(location.hash)) history.pushState(null, '', location.pathname + location.search);
    pintarLista();
    var vuelta = sel && document.querySelector('#ieLista a[href="#ente=' + sel.nivel + ':' + encodeURIComponent(sel.id) + '"]');
    irA(vuelta || document.getElementById('ie-dir') || raiz);
    if (vuelta) vuelta.focus({ preventScroll: true });
  }

  function leerHash() {
    var m = /^#ente=(federal|estatal|municipal):(.+)$/.exec(location.hash);
    if (m) abrir(m[1], decodeURIComponent(m[2]), true);
    else if (st.sel) {
      st.sel = null;
      var cont = document.getElementById('ieExp');
      cont.hidden = true; cont.innerHTML = '';
      document.title = tituloOriginal;
      pintarLista();
    }
  }

  /* ---------------- La ficha para copiar ---------------- */
  /* El cuerpo es lo que firma la huella; la ficha copiada le suma el sello y el enlace. */
  function textoFicha() {
    var ente = st.sel && buscarEnte(st.sel.nivel, st.sel.id);
    if (!ente) return '';
    return cuerpoFicha(ente) + '\n\nFicha técnica de Auditavisión · Folio ' + (st.folio || 'no disponible') +
      (st.huella ? '\nHuella digital (SHA-256 de la ficha): ' + st.huella : '') +
      '\nNo es un documento oficial. Compruébala en: ' + enlaceEnte(ente);
  }
  function cuerpoFicha(ente) {
    ente = ente || (st.sel && buscarEnte(st.sel.nivel, st.sel.id));
    if (!ente) return '';
    var limpio = function (s) { return String(s).replace(/<br>/g, ' ').replace(/<[^>]+>/g, '').replace(/\s*\[\d+\]/g, '').replace(/\s+/g, ' ').trim(); };
    var t = 'AUDITAVISIÓN · Ficha técnica · Auditor de entes públicos\n' + ente.nombre + '\n' + ente.sub + '\n\n';
    if (ente.nivel === 'municipal') t += 'Quién gobernó: ' + limpio(munGobierno(ente)) + '\n\n';
    var dg = diag(ente), l = incs(dg);
    if (l.length) {
      t += 'INCONGRUENCIAS EN SU RENDICIÓN DE CUENTAS\n';
      l.forEach(function (i) {
        t += '• ' + i.tema + ': ' + i.a[0] + ' ' + mdpF(i.a[1]) + '; ' + i.b[0] + ' ' + mdpF(i.b[1]) + '; diferencia ' + (i.dif >= 0 ? '+' : '−') + mdpF(Math.abs(i.dif)) + (i.nota ? '. ' + i.nota : '') + '\n';
      });
      t += '\n';
    }
    dg.forEach(function (x) { t += '• ' + x.q + ' ' + SEM[x.e].t + ': ' + limpio(x.v) + '\n  ' + limpio(x.d) + '\n'; });
    var ej = ejes(ente), i = indice(ej);
    if (i !== null) {
      t += '\nÍndice de salud financiera: ' + Math.round(i) + '/100 — ' + veredicto(i).t + '\n';
      ej.forEach(function (e, k) { t += '• ' + e.et + ' (' + [P.autonomia, P.observado, P.holgura][k] + '%): ' + Math.round(e.v) + '/100 — ' + limpio(e.crudo) + '\n'; });
    }
    t += '\nLos umbrales de los semáforos y el índice son de Auditavisión; los datos son oficiales. Una señal no es una acusación: es algo que la autoridad debe explicar.\n';
    t += ente.nivel === 'federal'
      ? 'Fuentes: SHCP, Cuenta Pública 2025 y avance del gasto 2026 (datos abiertos); ASF, Matriz de Datos Básicos CP 2024.'
      : ente.nivel === 'estatal'
        ? 'Fuentes: INEGI, finanzas públicas estatales 2024; SHCP, Cuenta Pública 2024 y Sistema de Alertas; ASF, Matriz de Datos Básicos CP 2024.'
        : 'Fuentes: INEGI, EFIPEM municipal 2016-2025; SHCP, Sistema de Recursos Federales Transferidos 2024; INAFED, presidencias municipales; ASF, Matriz de Datos Básicos CP 2024.';
    return t;
  }
  function avisar(t) {
    var a = document.getElementById('ieAviso');
    if (!a) return;
    a.textContent = t;
    a.classList.add('visible');
    clearTimeout(avisar.t);
    avisar.t = setTimeout(function () { a.classList.remove('visible'); }, 3200);
  }
  function copiar(texto, ok) {
    var reserva = function () {
      var ta = document.createElement('textarea');
      ta.value = texto; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      var hecho = false;
      try { hecho = document.execCommand('copy'); } catch (e) { hecho = false; }
      document.body.removeChild(ta);
      avisar(hecho ? ok : 'Tu navegador no dejó copiar. Selecciona el texto a mano.');
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(texto).then(function () { avisar(ok); }, reserva);
    else reserva();
  }

  /* ---------------- El buscador con sugerencias ---------------- */
  var q = document.getElementById('ieQ'), sug = document.getElementById('ieSug'), qx = document.getElementById('ieQx');
  var sugSel = -1, tSug = null;
  function sugerencias() {
    var v = q.value.trim();
    qx.hidden = !v;
    if (plano(v).length < 2) { cerrarSug(); return; }
    if (!window.AUDIT_MUNICIPIOS && plano(v).length >= 3) cargarMun().then(function () { if (q.value.trim() === v) sugerencias(); }, function () {});
    var grupos = [['federal', 'Federal'], ['estatal', 'Estatal'], ['municipal', 'Municipal']];
    var html = '', n = 0;
    grupos.forEach(function (g) {
      if (g[0] === 'municipal' && !window.AUDIT_MUNICIPIOS) return;
      var l = filtrar(g[0], v);
      if (!l.length) return;
      var tope = g[0] === 'municipal' ? 6 : 4;
      html += '<li class="ie-sug-g" role="presentation">' + g[1] + ' · ' + fmt(l.length) + '</li>' +
        l.slice(0, tope).map(function (x) {
          return '<li role="option" id="ieSug' + (n++) + '" aria-selected="false"><a href="#ente=' + x.nivel + ':' + encodeURIComponent(x.id) + '" tabindex="-1">' +
            '<span aria-hidden="true">' + x.icono + '</span><span><b>' + esc(x.nombre) + '</b><small>' + esc(x.sub) + '</small></span></a></li>';
        }).join('');
    });
    if (!html) html = '<li class="ie-sug-g" role="presentation">Sin coincidencias' + (window.AUDIT_MUNICIPIOS ? '' : ' (aún cargando municipios…)') + '</li>';
    html += '<li class="ie-sug-pie" role="presentation">Enter: ver todos los resultados en la lista</li>';
    sug.innerHTML = html;
    sug.hidden = false;
    q.setAttribute('aria-expanded', 'true');
    sugSel = -1;
  }
  function cerrarSug() { sug.hidden = true; sug.innerHTML = ''; q.setAttribute('aria-expanded', 'false'); q.removeAttribute('aria-activedescendant'); sugSel = -1; }
  function moverSug(d) {
    var ops = sug.querySelectorAll('[role="option"]');
    if (!ops.length) return;
    if (ops[sugSel]) ops[sugSel].setAttribute('aria-selected', 'false');
    sugSel = (sugSel + d + ops.length) % ops.length;
    ops[sugSel].setAttribute('aria-selected', 'true');
    q.setAttribute('aria-activedescendant', ops[sugSel].id);
    ops[sugSel].scrollIntoView({ block: 'nearest' });
  }
  function aplicarBusqueda() {
    st.q = q.value.trim(); st.tope = 60;
    /* Si en el nivel actual nadie coincide, se pasa al primero que sí. */
    if (st.q && !filtrar(st.nivel, st.q).length) {
      var otro = ['federal', 'estatal', 'municipal'].filter(function (k) { return (k !== 'municipal' || window.AUDIT_MUNICIPIOS) && filtrar(k, st.q).length; })[0];
      if (otro) st.nivel = otro;
    }
    pintarTodo();
  }
  q.addEventListener('input', function () {
    clearTimeout(tSug);
    tSug = setTimeout(function () { sugerencias(); aplicarBusqueda(); }, 120);
  });
  q.addEventListener('keydown', function (ev) {
    if (ev.key === 'ArrowDown') { ev.preventDefault(); if (sug.hidden) sugerencias(); moverSug(1); }
    else if (ev.key === 'ArrowUp') { ev.preventDefault(); moverSug(-1); }
    else if (ev.key === 'Escape') { cerrarSug(); }
    else if (ev.key === 'Enter') {
      ev.preventDefault();
      var op = sug.querySelectorAll('[role="option"]')[sugSel];
      if (op) { location.hash = op.querySelector('a').getAttribute('href').slice(1); cerrarSug(); }
      else {
        aplicarBusqueda(); cerrarSug();
        irA(document.getElementById('ie-dir'));
      }
    }
  });
  q.addEventListener('blur', function () { setTimeout(cerrarSug, 180); });
  sug.addEventListener('mousedown', function (ev) { ev.preventDefault(); });
  sug.addEventListener('click', function (ev) { if (ev.target.closest('a')) setTimeout(cerrarSug, 0); });
  qx.addEventListener('click', function () { q.value = ''; cerrarSug(); aplicarBusqueda(); q.focus(); });

  /* ---------------- Eventos de la página ---------------- */
  raiz.addEventListener('click', function (ev) {
    var b = ev.target.closest('button, a');
    if (!b || !raiz.contains(b)) return;
    if (b.classList.contains('ie-nivel')) { ponerNivel(b.getAttribute('data-nivel')); return; }
    if (b.hasAttribute('data-ir-nivel')) { ev.preventDefault(); ponerNivel(b.getAttribute('data-ir-nivel')); irA(document.getElementById('ie-dir')); return; }
    if (b.hasAttribute('data-vista')) { st.vista = b.getAttribute('data-vista'); st.tope = 60; pintarLista(); return; }
    if (b.hasAttribute('data-mas')) { st.tope += 120; pintarLista(); return; }
    if (b.hasAttribute('data-limpiar')) { q.value = ''; st.q = ''; st.vista = 'todos'; qx.hidden = true; pintarTodo(); return; }
    if (b.hasAttribute('data-reintentar')) { pintarLista(); return; }
    if (b.hasAttribute('data-cerrar')) { cerrar(); return; }
    if (b.hasAttribute('data-pdf')) { window.print(); return; }
    if (b.getAttribute('data-copiar') === 'ficha') { copiar(textoFicha(), '✓ Ficha del expediente copiada. Pégala donde quieras.'); return; }
    if (b.getAttribute('data-copiar') === 'enlace') { copiar(location.href, '✓ Enlace copiado: abre directo este expediente.'); return; }
  });
  /* El método vive en la ventana lateral (botón 📖): los enlaces #ie-metodo
     de la ficha la abren y, si apuntan a un apartado, lo despliegan. */
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest('a[href^="#ie-metodo"]'), btn = document.getElementById('ieComoBtn');
    if (!a || !btn) return;
    ev.preventDefault();
    btn.click();
    var id = a.getAttribute('href').slice(1);
    var det = id !== 'ie-metodo' && document.querySelector('.glos-drawer #' + id);
    if (det) { det.open = true; setTimeout(function () { det.scrollIntoView({ block: 'start' }); }, 60); }
  });
  raiz.addEventListener('change', function (ev) {
    if (ev.target.id === 'ieOrden') { st.orden = ev.target.value; st.tope = 60; pintarLista(); }
  });
  /* Flechas entre las pestañas de nivel. */
  raiz.querySelector('.ie-niveles').addEventListener('keydown', function (ev) {
    var orden = ['federal', 'estatal', 'municipal'], i = orden.indexOf(st.nivel);
    if (ev.key === 'ArrowRight') { ev.preventDefault(); ponerNivel(orden[(i + 1) % 3], true); }
    else if (ev.key === 'ArrowLeft') { ev.preventDefault(); ponerNivel(orden[(i + 2) % 3], true); }
  });
  window.addEventListener('hashchange', leerHash);

  /* ---------------- Verificar una ficha técnica (folio AV-FT) ---------------- */
  /* El verificador del Modo Inspector manda aquí los folios AV-FT-…
     (?verifica=). Se recalcula, en el navegador, la huella de la ficha de
     cada ente con los datos vigentes: primero los federales y los estados,
     y si no aparece, los municipios (se cargan al vuelo). */
  function verificar(v) {
    var out = document.getElementById('ieVer');
    if (!out) return;
    var Q = String(v).trim().replace(/\s+/g, '').toUpperCase();
    out.hidden = false;
    out.innerHTML = '<p class="ie-ver-c">⏳ Comprobando el folio <b>' + esc(Q) + '</b> contra las fichas de todos los entes…</p>';
    function probar(l) {
      return Promise.all(l.map(function (x) { return huellaDe(cuerpoFicha(x)).then(function (h) { return { x: x, h: h }; }); })).then(function (rs) {
        if (rs.length && !rs[0].h) throw new Error('sin-sha');
        return rs.filter(function (r) { return folio(r.h) === Q || r.h.toUpperCase() === Q; })[0] || null;
      });
    }
    probar(entes('federal').concat(entes('estatal'))).then(function (hit) {
      return hit || cargarMun().then(function () { return probar(entes('municipal')); });
    }).then(function (hit) {
      out.innerHTML = hit
        ? '<div class="ie-ver-si"><b>✅ Auténtica.</b> El folio corresponde a la ficha técnica de <b>' + esc(hit.x.nombre) + '</b>, y sus cifras coinciden con los datos vigentes de la plataforma.' +
          '<br><small>Huella: <code>' + hit.h + '</code></small><br><a class="ie-btn ie-btn-p" href="#ente=' + hit.x.nivel + ':' + encodeURIComponent(hit.x.id) + '">Ver la ficha</a></div>'
        : '<div class="ie-ver-no"><b>❌ No coincide</b> con ninguna ficha técnica de los datos vigentes. O la ficha se alteró, o se expidió con datos anteriores: ábrela de nuevo desde el ' +
          '<a href="#ie-dir">directorio</a> y compara las cifras.</div>';
    }, function (e) {
      out.innerHTML = '<div class="ie-ver-no">' + (e && e.message === 'sin-sha'
        ? 'Este navegador no puede calcular huellas SHA-256. Ábrelo en uno actualizado.'
        : 'No se pudo cargar el padrón municipal para terminar la comprobación. Revisa tu conexión y vuelve a intentarlo.') + '</div>';
    });
  }

  /* ?nivel= y ?q= (los enlaces del antiguo directorio, que redirige aquí). */
  var params = new URLSearchParams(location.search);
  {
    var pn = params.get('nivel'), pq = params.get('q'), po = params.get('orden'), pv = params.get('vista');
    if (pn && VISTAS.todos.niv.indexOf(pn) > -1) { st.nivel = pn; if (pn === 'municipal') cargarMun().catch(function () {}); }
    if (po && ordenVale(po)) st.orden = po;
    if (pv && VISTAS[pv] && VISTAS[pv].niv.indexOf(st.nivel) > -1) st.vista = pv;
    if (pq) { q.value = pq; qx.hidden = false; st.q = pq.trim(); }
  }
  avisoMun('');
  if (st.q) aplicarBusqueda(); else pintarTodo();
  if (/^#ente=/.test(location.hash)) leerHash();
  if (params.get('verifica')) verificar(params.get('verifica'));
})();
