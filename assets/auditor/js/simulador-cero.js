/* Simulador «Reparte el presupuesto, desde cero» (propuesta de Astra,
   punto 6; entrega 4, 10-10-2026).

   Todo arranca en $0. El lector agrega entradas y destinos, reparte, carga
   un ejemplo oficial identificado (cuadro II.6 de los Criterios Generales
   de Politica Economica 2027), compara dos escenarios, reinicia en cero y
   descarga la cuenta. Reglas:
   - Un cero escrito por el lector no es un dato oficial igual a cero.
   - Toda cifra lleva su origen: «tuya» u «oficial» con su renglon.
   - Si una operacion no se puede hacer (dividir entre cero), se dice por que.
   - No predice resultados sociales: solo suma y resta lo que se escribe.

   Pagina: simulador-presupuesto.html (herramientas/simulador.py). Los datos
   del ejemplo vienen en <script type="application/json" id="simEjemplo">. */
(function () {
  'use strict';

  var raiz = document.getElementById('simCero');
  var datos = document.getElementById('simEjemplo');
  if (!raiz || !datos) return;
  var EJ = JSON.parse(datos.textContent);

  var cuenta = 0;
  var st = nuevo();

  function nuevo() {
    return {
      unidad: 'pesos', origen: null,
      entradas: [fila('Ingreso 1')],
      salidas: [fila('Destino 1')],
      esc: st ? st.esc : { A: null, B: null }
    };
  }

  function fila(nombre, oficial) {
    cuenta += 1;
    return { k: 'f' + cuenta, nombre: nombre, monto: oficial ? oficial.valor : 0, oficial: oficial || null };
  }

  /* ---------- utilidades ---------- */
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function num(x) {
    return (Math.round(x * 10) / 10).toLocaleString('es-MX', { minimumFractionDigits: 0, maximumFractionDigits: 1 });
  }
  function dinero(x) {
    return (x < 0 ? '−$' : '$') + num(Math.abs(x)) + (st.unidad === 'mdp' ? ' mdp' : '');
  }
  function leer(txt) {
    var n = parseFloat(String(txt == null ? '' : txt).replace(/[^0-9.]/g, ''));
    return isFinite(n) && n > 0 ? n : 0;
  }
  function suma(lista) {
    return lista.reduce(function (a, f) { return a + f.monto; }, 0);
  }
  function chipOficial(f) {
    return '<span class="est-chip est-oficial" title="' + esc(EJ.fuente + ' · renglón «' + f.oficial.renglon + '»') + '">oficial</span>';
  }
  function chipOrigen(f) {
    if (f.oficial && Math.abs(f.monto - f.oficial.valor) < 0.05) return chipOficial(f);
    return '<span class="sz-tuyo" title="Lo escribiste tú: es una simulación, no un dato oficial">' +
      (f.oficial ? 'cambiado por ti' : 'tuyo') + '</span>';
  }

  /* ---------- pintura ---------- */
  function pintar() {
    raiz.innerHTML =
      '<div class="sz-aviso"><span class="sz-et">Simulación</span> ' +
        'Todo empieza en $0. Lo que escribes es tuyo y no un dato oficial: un $0 tuyo no quiere decir que la cifra oficial sea cero. ' +
        'Si quieres partir de cifras reales, carga el ejemplo oficial.</div>' +
      '<div class="sz-barra" role="group" aria-label="Acciones del simulador">' +
        '<button type="button" class="sz-btn" data-acc="entrada">➕ Agregar entrada</button>' +
        '<button type="button" class="sz-btn" data-acc="salida">➕ Agregar destino</button>' +
        '<button type="button" class="sz-btn" data-acc="repartir" title="Divide lo que entra entre los destinos, en partes iguales">⚖️ Repartir en partes iguales</button>' +
        '<span class="sz-ejemplo"><label for="szEjemplo" class="sz-oculto">Ejemplo oficial</label>' +
          /* sort(): el navegador pone primero las claves que parecen numero
             («2027» antes que «2026a»); el orden es el del calendario. */
          '<select id="szEjemplo">' + Object.keys(EJ.escenarios).sort().map(function (k) {
            return '<option value="' + k + '">' + esc(EJ.escenarios[k]) + '</option>';
          }).join('') + '</select>' +
          '<button type="button" class="sz-btn sz-btn-of" data-acc="ejemplo">📄 Cargar ejemplo oficial</button></span>' +
        '<button type="button" class="sz-btn" data-acc="cero">↺ Reiniciar en cero</button>' +
      '</div>' +
      (st.origen ? '<p class="sz-origen">Cargaste el ejemplo oficial: <b>' + esc(EJ.escenarios[st.origen]) + '</b>, en ' + esc(EJ.unidad) + '. ' +
        'Fuente: <a href="' + esc(EJ.url) + '" target="_blank" rel="noopener noreferrer">' + esc(EJ.fuente) + ' ↗</a></p>' : '') +
      '<div class="sz-cols">' +
        columna('entradas', '💰 Lo que entra', 'Ingresos y otras entradas') +
        columna('salidas', '🧾 A dónde va', 'Destinos del gasto') +
      '</div>' +
      '<section class="sz-res" aria-live="polite" id="szRes"></section>' +
      '<section class="sz-graf" id="szGraf"></section>' +
      '<section class="sz-esc">' +
        '<h3 class="sz-tit">🔀 Compara escenarios</h3>' +
        '<p class="sz-nota">Guarda lo que tienes en pantalla como escenario A, cámbialo y guárdalo como B. La tabla compara concepto por concepto, por nombre.</p>' +
        '<div class="sz-barra"><button type="button" class="sz-btn" data-acc="escA">💾 Guardar como escenario A</button>' +
        '<button type="button" class="sz-btn" data-acc="escB">💾 Guardar como escenario B</button>' +
        '<button type="button" class="sz-btn" data-acc="escBorrar">🗑️ Borrar escenarios</button></div>' +
        '<div id="szComp"></div>' +
      '</section>' +
      '<section class="sz-calc">' +
        '<details id="szCalc"><summary>🧮 Consulta el cálculo, operación por operación</summary><div id="szOps"></div></details>' +
        '<div class="sz-barra"><button type="button" class="sz-btn" data-acc="csv">⬇️ Descarga el cálculo (CSV)</button></div>' +
      '</section>' +
      '<p class="sz-nota sz-limite"><b>Qué no hace este simulador.</b> No predice cuántas personas se atienden ni qué resultados sociales tendría un reparto: ' +
        'para eso hace falta un modelo documentado, y aquí solo se suman y se restan las cifras que escribes o cargas.</p>';
    if (st.origen) document.getElementById('szEjemplo').value = st.origen;
    recalcular();
  }

  function columna(clave, titulo, sub) {
    var filas = st[clave].map(function (f, i) {
      return '<div class="sz-fila" data-lista="' + clave + '" data-i="' + i + '">' +
        '<input class="sz-nombre" type="text" value="' + esc(f.nombre) + '" aria-label="Concepto" data-campo="nombre">' +
        '<span class="sz-caja"><b aria-hidden="true">$</b><input class="sz-monto" type="text" inputmode="decimal" autocomplete="off" ' +
          'value="' + (f.monto ? num(f.monto) : '') + '" placeholder="0" aria-label="Importe de ' + esc(f.nombre) + '" data-campo="monto"></span>' +
        '<span class="sz-chip" data-chip>' + chipOrigen(f) + '</span>' +
        '<button type="button" class="sz-quitar" data-acc="quitar" aria-label="Quitar ' + esc(f.nombre) + '">✕</button>' +
      '</div>';
    }).join('');
    return '<section class="sz-col"><h3 class="sz-tit">' + titulo + '</h3><p class="sz-nota">' + sub + '</p>' +
      (filas || '<p class="sz-nota">Sin renglones. Agrega uno con el botón de arriba.</p>') + '</section>';
  }

  function recalcular() {
    var e = suma(st.entradas), s = suma(st.salidas), b = e - s;
    var res = document.getElementById('szRes');
    var oficialIntacto = st.origen && st.entradas.concat(st.salidas).every(function (f) {
      return f.oficial && Math.abs(f.monto - f.oficial.valor) < 0.05;
    }) && st.entradas.length === EJ.entradas.length && st.salidas.length === EJ.salidas.length;
    var cotejo = '';
    if (oficialIntacto) {
      var bo = EJ.totales.balance[st.origen], dif = Math.round((b - bo) * 10) / 10;
      cotejo = '<p class="sz-cotejo"><span class="est-chip est-derivado">derivado</span> Entradas menos salidas da ' + dinero(b) +
        '. El cuadro publica un balance presupuestario de ' + dinero(bo) + ' <span class="est-chip est-oficial">oficial</span>' +
        (dif ? ': la diferencia de ' + num(Math.abs(dif)) + ' es de redondeo, como advierte el propio cuadro («las sumas parciales pueden no coincidir»).' : ', igual.') +
        ' Ese faltante es el déficit, y se cubre con deuda.</p>';
    }
    res.innerHTML =
      '<div class="sz-tot"><span>Entra</span><strong>' + dinero(e) + '</strong></div>' +
      '<div class="sz-tot"><span>Sale</span><strong>' + dinero(s) + '</strong></div>' +
      '<div class="sz-tot sz-bal ' + (b < 0 ? 'sz-neg' : b > 0 ? 'sz-pos' : '') + '"><span>' +
        (b < 0 ? 'Falta (déficit)' : b > 0 ? 'Sobra' : 'Balance') + '</span><strong>' + dinero(b) + '</strong></div>' +
      '<p class="sz-nota sz-op">Balance = entradas − salidas = ' + dinero(e) + ' − ' + dinero(s) + ' = ' + dinero(b) + '. ' +
        (b < 0 ? 'Sale más de lo que entra: ese hueco se tendría que pedir prestado.' :
          b > 0 ? 'Entra más de lo que sale: queda un remanente sin destino.' :
            (e === 0 ? 'Todo está en ceros: escribe o carga cifras para empezar.' : 'Lo que entra y lo que sale son iguales.')) + '</p>' + cotejo;

    var graf = document.getElementById('szGraf');
    if (s === 0) {
      graf.innerHTML = '<h3 class="sz-tit">📊 Cómo se reparte lo que sale</h3><p class="sz-nota sz-div0">No se puede calcular qué parte se lleva cada destino: ' +
        'el total que sale es $0 y dividir entre cero no tiene resultado. La gráfica aparece en cuanto escribas un importe.</p>';
    } else {
      graf.innerHTML = '<h3 class="sz-tit">📊 Cómo se reparte lo que sale</h3>' + st.salidas.map(function (f) {
        var p = f.monto / s * 100;
        return '<div class="sz-bar"><span class="sz-bar-n">' + esc(f.nombre) + '</span>' +
          '<span class="sz-bar-t"><span class="sz-bar-r" style="width:' + p.toFixed(2) + '%"></span></span>' +
          '<span class="sz-bar-v">' + p.toFixed(1) + ' %</span></div>';
      }).join('') + '<p class="sz-nota">Porcentaje = importe del destino ÷ total que sale (' + dinero(s) + ') × 100. <span class="est-chip est-derivado">derivado</span></p>';
    }

    document.getElementById('szOps').innerHTML = operaciones().map(function (o) {
      return '<div class="sz-opfila"><span>' + esc(o[0]) + '</span><code>' + esc(o[1]) + '</code></div>';
    }).join('');
    pintarComparacion();
  }

  function operaciones() {
    var e = suma(st.entradas), s = suma(st.salidas), ops = [];
    st.entradas.forEach(function (f) { ops.push(['Entrada: ' + f.nombre, dinero(f.monto) + (f.oficial && Math.abs(f.monto - f.oficial.valor) < 0.05 ? ' (oficial)' : ' (tuyo)')]); });
    ops.push(['Total que entra', st.entradas.map(function (f) { return num(f.monto); }).join(' + ') + ' = ' + num(e)]);
    st.salidas.forEach(function (f) { ops.push(['Destino: ' + f.nombre, dinero(f.monto) + (f.oficial && Math.abs(f.monto - f.oficial.valor) < 0.05 ? ' (oficial)' : ' (tuyo)')]); });
    ops.push(['Total que sale', st.salidas.map(function (f) { return num(f.monto); }).join(' + ') + ' = ' + num(s)]);
    ops.push(['Balance', num(e) + ' − ' + num(s) + ' = ' + num(e - s)]);
    st.salidas.forEach(function (f) {
      ops.push(['Parte de ' + f.nombre, s ? num(f.monto) + ' ÷ ' + num(s) + ' × 100 = ' + (f.monto / s * 100).toFixed(1) + ' %' : 'no se calcula: el total que sale es 0']);
    });
    return ops;
  }

  /* ---------- escenarios ---------- */
  function foto() {
    return {
      origen: st.origen, unidad: st.unidad,
      filas: st.entradas.map(function (f) { return ['Entra', f.nombre, f.monto]; })
        .concat(st.salidas.map(function (f) { return ['Sale', f.nombre, f.monto]; })),
      e: suma(st.entradas), s: suma(st.salidas)
    };
  }

  function pintarComparacion() {
    var c = document.getElementById('szComp'), A = st.esc.A, B = st.esc.B;
    if (!A && !B) { c.innerHTML = '<p class="sz-nota">Aún no guardas escenarios.</p>'; return; }
    if (!A || !B) { c.innerHTML = '<p class="sz-nota">Guardaste el escenario ' + (A ? 'A' : 'B') + '. Guarda el otro para comparar.</p>'; return; }
    if (A.unidad !== B.unidad) {
      c.innerHTML = '<p class="sz-nota sz-div0">No se comparan: un escenario está en pesos y el otro en millones de pesos. Guarda los dos en la misma unidad.</p>';
      return;
    }
    var claves = [], mapa = {};
    [A, B].forEach(function (x, j) {
      x.filas.forEach(function (f) {
        var k = f[0] + '|' + f[1];
        if (!mapa[k]) { mapa[k] = [f[0], f[1], 0, 0]; claves.push(k); }
        mapa[k][2 + j] += f[2];
      });
    });
    var u = A.unidad === 'mdp' ? ' (millones de pesos)' : ' (pesos)';
    c.innerHTML = '<div class="sz-tabla-env"><table class="sz-tabla"><thead><tr><th>Concepto</th><th>A' + u + '</th><th>B' + u + '</th><th>B − A</th><th>Cambio</th></tr></thead><tbody>' +
      claves.map(function (k) {
        var r = mapa[k], d = r[3] - r[2];
        return '<tr><td>' + r[0] + ' · ' + esc(r[1]) + '</td><td>' + num(r[2]) + '</td><td>' + num(r[3]) + '</td><td>' + num(d) + '</td><td>' +
          (r[2] ? (d / r[2] * 100).toFixed(1) + ' %' : '<span title="A vale 0: dividir entre cero no tiene resultado">sin base</span>') + '</td></tr>';
      }).join('') +
      '<tr class="sz-tabla-tot"><td>Balance</td><td>' + num(A.e - A.s) + '</td><td>' + num(B.e - B.s) + '</td><td>' + num((B.e - B.s) - (A.e - A.s)) + '</td><td></td></tr>' +
      '</tbody></table></div><p class="sz-nota">Cambio = (B − A) ÷ A × 100. Si A vale 0 no se calcula: dividir entre cero no tiene resultado.</p>';
  }

  /* ---------- descarga ---------- */
  function csv() {
    var u = st.unidad === 'mdp' ? 'millones de pesos' : 'pesos';
    var lineas = [['tipo', 'concepto', 'importe', 'unidad', 'origen', 'fuente']];
    function origen(f) { return f.oficial && Math.abs(f.monto - f.oficial.valor) < 0.05 ? 'oficial' : 'simulación (escrito por la persona)'; }
    function fuente(f) { return f.oficial && Math.abs(f.monto - f.oficial.valor) < 0.05 ? EJ.fuente + ', renglón «' + f.oficial.renglon + '» · ' + EJ.url : ''; }
    st.entradas.forEach(function (f) { lineas.push(['entrada', f.nombre, f.monto, u, origen(f), fuente(f)]); });
    st.salidas.forEach(function (f) { lineas.push(['destino', f.nombre, f.monto, u, origen(f), fuente(f)]); });
    var e = suma(st.entradas), s = suma(st.salidas);
    lineas.push(['total', 'Total que entra', e, u, 'derivado', 'suma de las entradas']);
    lineas.push(['total', 'Total que sale', s, u, 'derivado', 'suma de los destinos']);
    lineas.push(['total', 'Balance', e - s, u, 'derivado', 'entradas − salidas']);
    lineas.push(['nota', 'Simulación de Auditavisión. No predice resultados sociales.', '', '', '', new Date().toISOString().slice(0, 10)]);
    var texto = '﻿' + lineas.map(function (l) {
      return l.map(function (c) { c = String(c); return /[",\n]/.test(c) ? '"' + c.replace(/"/g, '""') + '"' : c; }).join(',');
    }).join('\r\n') + '\r\n';
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([texto], { type: 'text/csv;charset=utf-8' }));
    a.download = 'simulacion-presupuesto.csv';
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  /* ---------- acciones ---------- */
  function cargarEjemplo(k) {
    st.origen = k; st.unidad = 'mdp';
    st.entradas = EJ.entradas.map(function (x) { return fila(x.nombre, { valor: x.mdp[k], renglon: x.renglon }); });
    st.salidas = EJ.salidas.map(function (x) { return fila(x.nombre, { valor: x.mdp[k], renglon: x.renglon }); });
    pintar();
  }

  raiz.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-acc]');
    if (!b) return;
    var acc = b.getAttribute('data-acc');
    if (acc === 'entrada') { st.entradas.push(fila('Ingreso ' + (st.entradas.length + 1))); pintar(); }
    else if (acc === 'salida') { st.salidas.push(fila('Destino ' + (st.salidas.length + 1))); pintar(); }
    else if (acc === 'quitar') {
      var f = b.closest('.sz-fila');
      st[f.getAttribute('data-lista')].splice(+f.getAttribute('data-i'), 1); pintar();
    } else if (acc === 'repartir') {
      var e = suma(st.entradas);
      if (!st.salidas.length) { aviso('No hay destinos entre los cuales repartir: agrega al menos uno.'); return; }
      if (!e) { aviso('Lo que entra suma $0: no hay nada que repartir.'); return; }
      var parte = e / st.salidas.length;
      st.salidas.forEach(function (x) { x.monto = parte; });
      pintar();
    } else if (acc === 'ejemplo') { cargarEjemplo(document.getElementById('szEjemplo').value); }
    else if (acc === 'cero') { st = nuevo(); pintar(); }
    else if (acc === 'escA' || acc === 'escB') { st.esc[acc.slice(3)] = foto(); pintarComparacion(); }
    else if (acc === 'escBorrar') { st.esc = { A: null, B: null }; pintarComparacion(); }
    else if (acc === 'csv') { csv(); }
  });

  function aviso(txt) {
    var res = document.getElementById('szRes');
    var p = document.createElement('p');
    p.className = 'sz-nota sz-div0';
    p.textContent = txt;
    res.appendChild(p);
  }

  raiz.addEventListener('input', function (ev) {
    var el = ev.target, f = el.closest('.sz-fila');
    if (!f) return;
    var reg = st[f.getAttribute('data-lista')][+f.getAttribute('data-i')];
    if (el.getAttribute('data-campo') === 'nombre') reg.nombre = el.value;
    else reg.monto = leer(el.value);
    f.querySelector('[data-chip]').innerHTML = chipOrigen(reg);
    recalcular();
  });

  raiz.addEventListener('change', function (ev) {
    if (ev.target.getAttribute('data-campo') !== 'monto') return;
    var f = ev.target.closest('.sz-fila');
    var reg = st[f.getAttribute('data-lista')][+f.getAttribute('data-i')];
    ev.target.value = reg.monto ? num(reg.monto) : '';
  });

  pintar();
})();
