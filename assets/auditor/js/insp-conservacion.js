/* Auditavisión · Modo Inspector › ¿Hasta cuándo guardas tus papeles? (19-11-2026).
   La página la escribe herramientas/insp_conservacion.py con sus reglas en #csDatos.
   Aquí solo se sacan las fechas (gemela de vence() en Python; --prueba las compara).
   Nada se guarda ni se envía. AuditorConserva.vence() se expone para las pruebas. */
(function () {
  'use strict';

  function iso(a, m, d) { return a + '-' + (m < 10 ? '0' : '') + m + '-' + (d < 10 ? '0' : '') + d; }
  function parte(s) { var p = String(s).split('-'); return [+p[0], +p[1], +p[2]]; }
  function masAnios(s, n) {
    var p = parte(s);
    if (p[1] === 2 && p[2] === 29) return iso(p[0] + n, 2, 28);
    return iso(p[0] + n, p[1], p[2]);
  }

  /* fisica: persona física (anual en abril, LISR art. 150) o moral (dentro de los tres meses, art. 9). */
  function vence(fisica, anio, presento, fin) {
    var base = fisica ? iso(anio + 1, 4, 30) : iso(anio + 1, 3, 31);
    if (presento && presento > base) base = presento;
    return { decl: base, fiscal: masAnios(base, 5), diez: iso(anio + 10, 12, 31), anio5: iso(anio + 5, 12, 31),
      fin1: fin ? masAnios(fin, 1) : null };
  }

  window.AuditorConserva = { vence: vence };

  if (typeof document.getElementById !== 'function') return;
  var raiz = document.getElementById('csRaiz');
  if (!raiz) return;
  var D = JSON.parse(document.getElementById('csDatos').textContent);
  var $ = function (id) { return document.getElementById(id); };
  var MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  function larga(s) { var p = parte(s); return p[2] + ' de ' + MES[p[1] - 1] + ' de ' + p[0]; }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function hoyIso() { var h = new Date(); return iso(h.getFullYear(), h.getMonth() + 1, h.getDate()); }

  /* Lo que llega por la dirección (?a=2020&p=moral,patron), para que el chat abra la cuenta ya puesta. */
  try {
    var q = new URLSearchParams(location.search);
    if (q.get('a') && $('csAnio').querySelector('option[value="' + (+q.get('a')) + '"]')) $('csAnio').value = String(+q.get('a'));
    (q.get('p') || '').split(',').forEach(function (k) {
      var c = raiz.querySelector('input[name="csP"][value="' + k + '"]');
      if (c) c.checked = true;
    });
  } catch (e) { /* sin parámetros */ }

  /* La tabla de la ley se enciende según quién eres. */
  function perfil() {
    var p = { todos: true };
    raiz.querySelectorAll('input[name="csP"]').forEach(function (c) { if (c.checked) p[c.value] = true; });
    return p;
  }
  function marca(p) {
    raiz.querySelectorAll('.cs-reglas tbody tr').forEach(function (tr) {
      tr.classList.toggle('cs-aplica', !!p[tr.getAttribute('data-q')]);
    });
  }

  function pinta(e) {
    if (e) e.preventDefault();
    var p = perfil(), a = +$('csAnio').value, pres = $('csPres').value || null, fin = $('csFin').value || null;
    marca(p);
    var v = vence(!p.moral, a, pres, fin);
    var filas = [], fechas = [];
    function fila(id, que, hasta, por) {
      filas.push('<tr><th scope="row">' + esc(que) + '</th><td><b>' + esc(hasta) + '</b></td><td>' + por + ' <a href="#cs-' + id + '">ver el artículo</a></td></tr>');
    }
    var ley = function (k, art) { return '<a href="' + esc(D.leyes[k][1]) + '">' + esc(D.leyes[k][0]) + ', ' + esc(art) + '</a>'; };
    fila('fiscal', 'Tu contabilidad y tus comprobantes de ' + a, larga(v.fiscal),
      '5 años desde la anual (' + (pres && pres > (p.moral ? iso(a + 1, 3, 31) : iso(a + 1, 4, 30)) ? 'la presentaste el ' : 'vencía el ') + larga(v.decl) + '): ' + ley('cff', 'art. 30') + '.');
    fechas.push(v.fiscal);
    if (p.moral) fila('sociedad', 'Actas, movimientos de capital y declaraciones de la sociedad', 'Mientras exista la sociedad', ley('cff', 'art. 30') + '.');
    if (p.comerciante) {
      fila('comercio', 'Libros, comprobantes originales y contratos de tu negocio de ' + a, larga(v.diez), '10 años como mínimo, contados desde el último día del año: ' + ley('ccom', 'arts. 38, 46 y 49') + '.');
      fechas.push(v.diez);
    }
    if (p.patron) {
      fila('imss', 'Nóminas y listas de raya de ' + a, larga(v.anio5), 'Los 5 años siguientes al de su fecha: ' + ley('lss', 'art. 15, fr. II') + '.');
      fechas.push(v.anio5);
      if (v.fin1) {
        fila('lft_pagos', 'Contrato y recibos del trabajador que salió', larga(v.fin1), 'Un año después de terminar: ' + ley('lft', 'art. 804') + '. Sus recibos de nómina siguen además el plazo del IMSS y del SAT.');
        fechas.push(v.fin1);
      } else {
        fila('lft_contrato', 'Contratos de quienes siguen trabajando contigo', 'Mientras dure la relación y 1 año después', ley('lft', 'art. 804') + '.');
      }
    }
    if (p.pld) {
      fila('pld', 'Expedientes de tus actividades vulnerables de ' + a, larga(v.diez), '10 años desde cada operación; la última del año, a más tardar el 31 de diciembre: ' + ley('lfpiorpi', 'art. 18, fr. IV') + '.');
      fechas.push(v.diez);
    }
    fechas.sort();
    var max = fechas[fechas.length - 1], hoy = hoyIso();
    var h = '<p class="ci-cifra">Lo de ' + a + ' se guarda, como mínimo, hasta el <b>' + larga(max) + '</b></p>';
    h += max > hoy
      ? '<p>Todavía no se puede destruir. Manda el plazo más largo de las leyes que te alcanzan.</p>'
      : '<p>Ya pasó el plazo mínimo de la ley. Antes de destruir, revisa que no haya un recurso o un juicio abierto, una revisión del SAT o un acto con efectos que sigan (una depreciación, una pérdida que aún restas)' + (p.moral ? ', y que no sea un acta o una declaración de la sociedad' : '') + '. Y lo que tenga datos personales, se bloquea y después se suprime (' + ley('lfpdppp', 'arts. 10 y 24') + ').</p>';
    $('csTotal').innerHTML = h;
    $('csFechas').innerHTML = filas.join('');
    $('csNota').textContent = 'Fechas de nuestra cuenta (auditada), con la lectura de cada artículo: no recorren los plazos que caen en día inhábil ni cubren leyes de un sector. '
      + 'Si no conservas tu contabilidad el plazo de ley, el SAT puede revisarte 10 años en lugar de 5 (CFF, art. 67).';
    $('csRes').hidden = false;
  }
  raiz.querySelectorAll('input[name="csP"]').forEach(function (c) { c.addEventListener('change', function () { marca(perfil()); }); });
  marca(perfil());
  $('csForm').addEventListener('submit', pinta);
  if (location.search.indexOf('a=') >= 0) pinta();
})();
