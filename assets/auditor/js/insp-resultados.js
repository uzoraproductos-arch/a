/* Modo Inspector › Revisa tu estado de resultados (05-11-2026, herramientas/insp_resultados.py).

   Lee el estado de resultados EN EL NAVEGADOR: no se sube ni se guarda. Aplica
   las mismas reglas que su gemelo de Python, herramientas/lector_resultados.py
   (los patrones con que se reconoce cada renglón llegan de ahí, en #erDatos):
   si cambias una regla aquí, cámbiala allá, donde está la prueba.

   Todo lo que sale es «derivado» (una cuenta con las cifras del lector) y lo
   que llama la atención se dice «señal para revisar», nunca «irregularidad». */
(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const datos = $('erDatos');
  if (!datos) return;
  const D = JSON.parse(datos.textContent);
  const CON = D.conceptos.map(c => ({ c: c[0], n: c[1], rx: new RegExp(c[2]) }));
  const NOMBRE = {};
  CON.forEach(x => { NOMBRE[x.c] = x.n; });
  const SUMAN = { gop: true };
  const TASA = D.tasa;

  function esc(t) {
    return String(t).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[ch]);
  }
  function normal(t) {
    t = t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    t = t.replace(/^[\s\d.)\-]+/, '').replace(/[:*]/g, ' ');
    return t.replace(/\s+/g, ' ').trim();
  }
  function concepto(et) {
    const e = normal(et);
    for (const x of CON) if (x.rx.test(e)) return x.c;
    return null;
  }
  function numero(t) {
    t = (t || '').trim().replace(/\$/g, '').replace(/ /g, '').replace(/,/g, '');
    if (t === '' || t === '-' || t === '—') return null;
    const neg = t.charAt(0) === '(' && t.charAt(t.length - 1) === ')';
    t = t.replace(/^\(+|\)+$/g, '');
    if (!/^[+-]?(\d+\.?\d*|\.\d+)(e[+-]?\d+)?$/i.test(t)) return null;
    const v = parseFloat(t);
    return neg ? -v : v;
  }
  function filas(texto) {
    texto = texto.replace(/^﻿/, '');
    const linea = texto.split('\n')[0];
    const sep = linea.indexOf('\t') >= 0 ? '\t' : ((linea.split(';').length > linea.split(',').length) ? ';' : ',');
    const out = [];
    let f = [], c = '', q = false;
    for (let i = 0; i < texto.length; i++) {
      const ch = texto[i];
      if (q) {
        if (ch === '"') { if (texto[i + 1] === '"') { c += '"'; i++; } else q = false; } else c += ch;
      } else if (ch === '"') q = true;
      else if (ch === sep) { f.push(c); c = ''; }
      else if (ch === '\n') { f.push(c.replace(/\r$/, '')); out.push(f); f = []; c = ''; }
      else c += ch;
    }
    if (c || f.length) { f.push(c.replace(/\r$/, '')); out.push(f); }
    return out.filter(r => r.some(x => x.trim()));
  }

  function leer(texto) {
    const fs = filas(texto);
    if (!fs.length) throw new Error('El archivo está vacío.');
    let cols = [];
    fs[0].forEach((x, i) => { const m = /(19|20)\d{2}/.exec(x); if (i > 0 && m) cols.push([parseInt(m[0], 10), i]); });
    if (!cols.length) throw new Error('No encontramos los años: la primera fila debe decir, por ejemplo, «Concepto, 2023, 2024, 2025».');
    cols = cols.sort((a, b) => a[0] - b[0] || a[1] - b[1]).slice(-6);
    const v = {}, sin = [];
    fs.slice(1).forEach(f => {
      if (!f.length || !f[0].trim()) return;
      const c = concepto(f[0]);
      if (!c) { sin.push(f[0].trim()); return; }
      cols.forEach(([a, i]) => {
        const x = i < f.length ? numero(f[i]) : null;
        if (x === null) return;
        const d = v[c] = v[c] || {};
        if (SUMAN[c]) d[a] = (d[a] || 0) + x;
        else if (!(a in d)) d[a] = x;
      });
    });
    return { anios: cols.map(x => x[0]), v: v, sin: sin };
  }

  const r1 = x => Math.round(x * 10) / 10;
  const pct = (a, b) => (a === null || a === undefined || !b) ? null : r1(100 * a / b);
  const vari = (a, b) => (a === null || a === undefined || b === null || b === undefined || b <= 0) ? null : r1(100 * (a - b) / b);
  const fmt = x => (x < 0 ? '-$' : '$') + Math.abs(Math.round(x)).toLocaleString('en-US');
  const fp = x => x.toFixed(1);
  function mov(x, plural) {
    if (x === 0) return plural ? 'no cambiaron' : 'no cambió';
    const v = x > 0 ? (plural ? 'subieron' : 'subió') : (plural ? 'bajaron' : 'bajó');
    return v + ' ' + fp(Math.abs(x)) + ' %';
  }

  function analizar(texto) {
    const e = leer(texto);
    const anios = e.anios, v = e.v;
    const g = (c, a) => (v[c] && a in v[c]) ? v[c][a] : null;
    const senales = [], cuadre = [], deriv = {};
    const otros = e.sin.length ? ' Puede deberse a renglones que no reconocimos (' + e.sin.slice(0, 4).join(', ') + ').' : '';
    const tol = base => Math.max(1, 0.005 * Math.abs(base || 0));
    anios.forEach(a => {
      const ing = g('ing', a), cos = g('cos', a), gop = g('gop', a), fin = g('fin', a), pfin = g('pfin', a) || 0, isr = g('isr', a);
      const pasos = [['ub', 'la utilidad bruta', ing !== null && cos !== null ? ing - cos : null]];
      const ub = g('ub', a) !== null ? g('ub', a) : pasos[0][2];
      pasos.push(['uo', 'la utilidad de operación', ub !== null && gop !== null ? ub - gop : null]);
      const uo = g('uo', a) !== null ? g('uo', a) : pasos[1][2];
      pasos.push(['uai', 'la utilidad antes de impuestos', uo !== null && fin !== null ? uo - fin + pfin : null]);
      const uai = g('uai', a) !== null ? g('uai', a) : pasos[2][2];
      pasos.push(['un', 'la utilidad neta', uai !== null && isr !== null ? uai - isr : null]);
      pasos.forEach(([c, nom, calc]) => {
        if (calc === null) return;
        const dice = g(c, a);
        if (dice === null) { (deriv[c] = deriv[c] || {})[a] = calc; return; }
        const dif = dice - calc, ok = Math.abs(dif) <= tol(ing);
        cuadre.push({ anio: a, c: c, dice: dice, calc: calc, ok: ok });
        if (!ok) senales.push({ dim: 'Cuadre', anio: a, txt: 'En ' + a + ' ' + nom + ' dice ' + fmt(dice) + ', pero la resta da ' + fmt(calc) + ' (diferencia de ' + fmt(dif) + ').' + otros });
      });
    });
    const val = (c, a) => g(c, a) !== null ? g(c, a) : ((deriv[c] && a in deriv[c]) ? deriv[c][a] : null);
    const estructura = {}, rent = {}, imp = {}, deuda = {};
    anios.forEach(a => {
      const ing = g('ing', a);
      estructura[a] = {};
      ['cos', 'gop', 'fin', 'isr'].forEach(c => { estructura[a][c] = pct(val(c, a), ing); });
      rent[a] = { bruto: pct(val('ub', a), ing), operacion: pct(val('uo', a), ing), neto: pct(val('un', a), ing) };
      if (rent[a].operacion !== null && rent[a].operacion < 0) {
        senales.push({ dim: 'Rentabilidad', anio: a, txt: 'En ' + a + ' hubo pérdida de operación: por cada $100 vendidos, se perdieron $' + fp(-rent[a].operacion) + ' antes de intereses e impuestos.' });
      }
      const uai = val('uai', a), isr = g('isr', a);
      if (uai !== null && uai > 0 && isr !== null) {
        const t = pct(isr, uai);
        imp[a] = t;
        if (t < TASA - 10 || t > TASA + 10) {
          senales.push({ dim: 'Impuestos', anio: a, txt: 'En ' + a + ' el ISR fue el ' + fp(t) + ' % de la utilidad antes de impuestos; la tasa de las personas morales es ' + TASA + ' % (LISR, art. 9). Puede tener explicación (pérdidas de años anteriores, partidas no deducibles, diferencias entre lo contable y lo fiscal), pero conviene preguntar.' });
        }
      }
      const uo = val('uo', a), fin = g('fin', a);
      if (fin !== null && fin > 0 && uo !== null) {
        const cob = Math.round(uo / fin * 100) / 100;
        deuda[a] = cob;
        if (cob < 1) senales.push({ dim: 'Deuda', anio: a, txt: 'En ' + a + ' la utilidad de operación (' + fmt(uo) + ') no alcanzó para pagar los gastos financieros (' + fmt(fin) + '): los cubrió ' + cob.toFixed(2) + ' veces.' });
      }
    });
    const tendencia = {};
    for (let i = 1; i < anios.length; i++) {
      const a = anios[i], b = anios[i - 1];
      const t = {};
      ['ing', 'cos', 'gop', 'un'].forEach(c => { t[c] = vari(val(c, a), val(c, b)); });
      tendencia[a] = t;
      if (t.ing !== null) {
        [['cos', 'el costo de ventas', false], ['gop', 'los gastos de operación', true]].forEach(([c, nom, pl]) => {
          if (t[c] !== null && t[c] > t.ing + 2) senales.push({ dim: 'Tendencia', anio: a, txt: 'En ' + a + ' ' + nom + ' ' + mov(t[c], pl) + ' y las ventas ' + mov(t.ing, true) + ': cada peso vendido deja menos.' });
        });
        if (t.ing < -10) senales.push({ dim: 'Tendencia', anio: a, txt: 'En ' + a + ' las ventas cayeron ' + fp(-t.ing) + ' %.' });
        if (t.un !== null && t.un > 0 && t.ing < 0) senales.push({ dim: 'Tendencia', anio: a, txt: 'En ' + a + ' la utilidad neta subió ' + fp(t.un) + ' % mientras las ventas bajaron ' + fp(-t.ing) + ' %: conviene ver de dónde salió.' });
      }
    }
    const compuesto = [], ult = anios[anios.length - 1];
    Array.from(new Set([3, 5, ult - anios[0]])).sort((a, b) => a - b).forEach(h => {
      const ini = ult - h, x0 = val('ing', ini), x1 = val('ing', ult);
      if (h >= 2 && x0 && x1 && x0 > 0 && x1 > 0) compuesto.push({ anios: h, de: ini, a: ult, tasa: r1((Math.pow(x1 / x0, 1 / h) - 1) * 100) });
    });
    return { anios: anios, v: v, deriv: deriv, sin: e.sin, cuadre: cuadre, estructura: estructura, rentabilidad: rent,
             tendencia: tendencia, compuesto: compuesto, impuestos: imp, deuda: deuda, senales: senales };
  }

  /* ---------- Pintar ---------- */
  const celda = x => (x === null || x === undefined) ? '<td>—</td>' : '<td>' + x + '</td>';
  function tabla(cap, anios, renglones) {
    return '<div class="cf-tabla-caja"><table class="cf-tabla"><caption>' + cap + '</caption><thead><tr><th scope="col">Concepto</th>' +
      anios.map(a => '<th scope="col">' + a + '</th>').join('') + '</tr></thead><tbody>' +
      renglones.map(([nom, f]) => '<tr><th scope="row">' + esc(nom) + '</th>' + anios.map(a => celda(f(a))).join('') + '</tr>').join('') +
      '</tbody></table></div>';
  }
  function dim(ico, tit, que, cuerpo, sen) {
    const s = sen.length ? '<div class="cf-69b"><p><b>Señales para revisar</b> ' + D.chipDe + '</p><ul>' + sen.map(x => '<li>' + esc(x.txt) + '</li>').join('') + '</ul></div>'
      : '<p class="cf-nota">✓ Sin señales en esta dimensión.</p>';
    return '<section class="cf-fac' + (sen.length ? ' cf-fac-mal' : '') + '"><h3>' + ico + ' ' + tit + ' ' + D.chipDe + '</h3><p class="cf-nota">' + que + '</p>' + cuerpo + s + '</section>';
  }
  const pc = x => (x === null || x === undefined) ? null : fp(x) + ' %';

  function pintar(r, nombre, ejemplo) {
    const A = r.anios, S = d => r.senales.filter(s => s.dim === d);
    let h = '<p class="cf-nota">📄 <b>' + esc(nombre) + '</b>' + (ejemplo ? ' <small>(ficticio)</small>' : '') + ': leímos ' + A.length + ' años (' + A[0] + '–' + A[A.length - 1] + '). ' +
      (r.senales.length ? '<b>' + r.senales.length + ' señales para revisar.</b>' : '<b>Sin señales para revisar.</b>') + ' Nada salió de tu equipo.</p>';
    const fallos = r.cuadre.filter(x => !x.ok);
    h += dim('🧮', 'Cuadre', '¿Las restas dan lo que dice el estado? Ventas − costo = utilidad bruta; − gastos de operación = de operación; − gastos financieros + productos financieros = antes de impuestos; − ISR = neta.',
      r.cuadre.length ? '<p>' + (r.cuadre.length - fallos.length) + ' de ' + r.cuadre.length + ' restas cuadran.' +
        (Object.keys(r.deriv).length ? ' Calculamos los subtotales que no venían: ' + Object.keys(r.deriv).map(c => esc(NOMBRE[c])).join(', ') + '.' : '') + '</p>'
        : '<p>Faltan renglones para rehacer las restas.</p>', S('Cuadre'));
    h += dim('🧱', 'Estructura (análisis vertical)', 'De cada $100 vendidos, cuánto se va en cada renglón.',
      tabla('De cada $100 de ventas', A, [['Costo de ventas', a => pc(r.estructura[a].cos)], ['Gastos de operación', a => pc(r.estructura[a].gop)],
        ['Gastos financieros', a => pc(r.estructura[a].fin)], ['ISR', a => pc(r.estructura[a].isr)]]), []);
    h += dim('📈', 'Rentabilidad', 'Lo que queda de cada $100 vendidos después de cada nivel de costos.',
      tabla('Márgenes', A, [['Margen bruto', a => pc(r.rentabilidad[a].bruto)], ['Margen de operación', a => pc(r.rentabilidad[a].operacion)],
        ['Margen neto', a => pc(r.rentabilidad[a].neto)]]), S('Rentabilidad'));
    const A2 = A.slice(1);
    h += dim('⏳', 'Tendencia (análisis horizontal)', 'Cuánto cambió cada renglón frente al año anterior y cuánto crecieron las ventas al año, en promedio compuesto, en 3 y 5 años.',
      (A2.length ? tabla('Cambio frente al año anterior', A2, [['Ventas', a => pc(r.tendencia[a].ing)], ['Costo de ventas', a => pc(r.tendencia[a].cos)],
        ['Gastos de operación', a => pc(r.tendencia[a].gop)], ['Utilidad neta', a => pc(r.tendencia[a].un)]]) : '<p>Hace falta más de un año.</p>') +
      (r.compuesto.length ? '<ul class="cf-datos">' + r.compuesto.map(c => '<li>Ventas de ' + c.de + ' a ' + c.a + ' (' + c.anios + ' años): <b>' + fp(c.tasa) + ' % al año</b><br><small>Operación: (ventas ' + c.a + ' ÷ ventas ' + c.de + ')<sup>1/' + c.anios + '</sup> − 1</small></li>').join('') + '</ul>' : ''),
      S('Tendencia'));
    h += dim('🏛️', 'Impuestos', 'La tasa efectiva del ISR: ISR ÷ utilidad antes de impuestos, frente a la tasa de ' + TASA + ' % de las personas morales (LISR, art. 9).',
      tabla('Tasa efectiva del ISR', A, [['ISR ÷ utilidad antes de impuestos', a => pc(r.impuestos[a])]]), S('Impuestos'));
    h += dim('🏦', 'Deuda', 'Cuántas veces la utilidad de operación paga los gastos financieros. Menos de 1 quiere decir que no alcanza.',
      tabla('Cobertura de intereses', A, [['Utilidad de operación ÷ gastos financieros', a => (r.deuda[a] === undefined ? null : r.deuda[a].toFixed(2) + ' veces')]]), S('Deuda'));
    const conceptos = CON.map(x => x.c).filter(c => r.v[c] || r.deriv[c]);
    h += '<details class="cf-con"><summary>Lo que leímos de tu archivo</summary>' +
      tabla('Tus cifras', A, conceptos.map(c => [NOMBRE[c], a => (r.v[c] && a in r.v[c]) ? fmt(r.v[c][a]) : ((r.deriv[c] && a in r.deriv[c]) ? fmt(r.deriv[c][a]) + ' <small>(calculado)</small>' : null)])) +
      (r.sin.length ? '<p class="cf-nota">No reconocimos: ' + r.sin.map(esc).join(', ') + '. No entran a las cuentas.</p>' : '') + '</details>';
    $('erRes').innerHTML = h;
    $('erAcciones').hidden = false;
  }

  function estado(t) { $('erEstado').textContent = t; }
  function usar(texto, nombre, ejemplo) {
    try {
      pintar(analizar(texto), nombre, ejemplo);
      estado('Listo. Se leyó en tu navegador: no se subió ni se guardó.');
    } catch (err) {
      $('erRes').innerHTML = '';
      estado('No pudimos leerlo: ' + err.message);
    }
  }
  function archivo(f) {
    if (!f) return;
    if (/\.xlsx?$/i.test(f.name)) { estado('Ese es un archivo de Excel. Guárdalo como CSV (Archivo › Guardar como › CSV) o copia las celdas y pégalas abajo.'); return; }
    const rd = new FileReader();
    rd.onload = () => usar(String(rd.result), f.name, false);
    rd.readAsText(f, 'utf-8');
  }
  $('erArchivo').addEventListener('change', ev => archivo(ev.target.files[0]));
  const suelta = $('erSuelta');
  suelta.addEventListener('dragover', ev => { ev.preventDefault(); suelta.classList.add('cf-sobre'); });
  suelta.addEventListener('dragleave', () => suelta.classList.remove('cf-sobre'));
  suelta.addEventListener('drop', ev => { ev.preventDefault(); suelta.classList.remove('cf-sobre'); archivo(ev.dataTransfer.files[0]); });
  $('erLeerTexto').addEventListener('click', () => usar($('erTexto').value, 'Lo que pegaste', false));
  $('erEjemplo').addEventListener('click', () => {
    fetch(D.ejemplo).then(r => r.ok ? r.text() : Promise.reject()).then(t => usar(t, 'Empresa ficticia, S.A. de C.V.', true),
      () => estado('No pudimos traer el ejemplo. Revisa tu conexión.'));
  });
  $('erPlantilla').addEventListener('click', () => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob(['﻿' + D.plantilla], { type: 'text/csv;charset=utf-8' }));
    a.download = 'plantilla-estado-de-resultados.csv';
    document.body.appendChild(a); a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  });
  $('erLimpiar').addEventListener('click', () => {
    $('erRes').innerHTML = ''; $('erTexto').value = ''; $('erArchivo').value = ''; $('erAcciones').hidden = true;
    estado('Borrado.');
  });
})();
