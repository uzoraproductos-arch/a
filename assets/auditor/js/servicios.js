/* Servicios de investigacion: formulario «Solicita una investigacion»
   (propuesta de Astra, punto 9; entrega 6, 10-10-2026).

   La solicitud se arma en el navegador y no se envia ni se guarda sola.
   El lector la revisa, la copia o la descarga. El boton de envio solo se
   activa cuando la pagina trae un canal en data-canal (CANAL_SOLICITUD en
   herramientas/apartados.py); mientras tanto dice que se abre con el
   lanzamiento.

   Pagina: servicios.html (herramientas/apartados.py, servicios()). */
(function () {
  'use strict';

  var form = document.getElementById('svForm');
  var resumen = document.getElementById('svResumen');
  var error = document.getElementById('svError');
  if (!form || !resumen || !error) return;
  var canal = form.getAttribute('data-canal') || '';

  function $(id) { return document.getElementById(id); }
  function val(id) { var el = $(id); return el ? el.value.trim() : ''; }
  function texto(sel) { var el = $(sel); return el && el.selectedIndex >= 0 ? el.options[el.selectedIndex].text : ''; }
  function parte() { var r = form.querySelector('input[name="parte"]:checked'); return r ? r.value : ''; }

  // El tema llega escrito desde cada investigacion: servicios.html?tema=...
  try {
    var tema = new URLSearchParams(location.search).get('tema');
    if (tema && !val('svTema')) $('svTema').value = tema.slice(0, 160);
  } catch (e) { /* sin URLSearchParams: el lector lo escribe */ }

  function marcar(id, malo) {
    var el = $(id);
    if (!el) return;
    if (malo) el.setAttribute('aria-invalid', 'true'); else el.removeAttribute('aria-invalid');
  }

  function revisar() {
    var faltan = [];
    var reglas = [
      ['svTema', val('svTema') !== '', 'el tema'],
      ['svPregunta', val('svPregunta') !== '', 'tu pregunta'],
      ['svNombre', val('svNombre') !== '', 'tu nombre u organización'],
      ['svCorreo', /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val('svCorreo')), 'un correo válido'],
      ['svPolitica', $('svPolitica').checked, 'que leíste la política de independencia'],
      ['svAlcance', $('svAlcance').checked, 'que entiendes el alcance del servicio']
    ];
    var primero = null;
    reglas.forEach(function (r) {
      marcar(r[0], !r[1]);
      if (!r[1]) { faltan.push(r[2]); if (!primero) primero = $(r[0]); }
    });
    if (!parte()) {
      faltan.splice(4, 0, 'si eres parte del caso');
      if (!primero) primero = form.querySelector('input[name="parte"]');
    }
    return { faltan: faltan, primero: primero };
  }

  function fecha() {
    var d = new Date();
    function dos(n) { return (n < 10 ? '0' : '') + n; }
    return dos(d.getDate()) + '-' + dos(d.getMonth() + 1) + '-' + d.getFullYear();
  }

  function armar() {
    var renglones = [
      'Solicitud de investigación · Auditavisión',
      'Fecha: ' + fecha(),
      '',
      'Servicio: ' + texto('svServicio'),
      'Tema: ' + val('svTema'),
      'Pregunta: ' + val('svPregunta'),
      'Ámbito: ' + texto('svAmbito') + (val('svLugar') ? ' · ' + val('svLugar') : ''),
      'Periodo: ' + (val('svPeriodo') || 'sin indicar'),
      'Para cuándo: ' + (val('svPlazo') || 'sin indicar'),
      'Documentos que ya tiene: ' + (val('svDocs') || 'ninguno indicado'),
      '',
      'Solicita: ' + val('svNombre') + ' <' + val('svCorreo') + '>',
      'Uso: ' + texto('svUso'),
      '¿Es parte del caso?: ' + parte(),
      '',
      'Leyó la política de independencia (versión 1, 10-10-2026) y entiende que el servicio es',
      'investigación documental y análisis de indicios, no un dictamen pericial ni asesoría legal.'
    ];
    return renglones.join('\n');
  }

  function boton(txt, clase, fn) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'sz-btn' + (clase ? ' ' + clase : '');
    b.textContent = txt;
    if (fn) b.addEventListener('click', fn);
    return b;
  }

  function avisar(msg) {
    var p = resumen.querySelector('.sv-estado');
    if (p) p.textContent = msg;
  }

  function copiar(t) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t).then(function () { avisar('✓ Copiada. Pégala donde la quieras guardar.'); },
        function () { seleccionar(); });
    } else {
      seleccionar();
    }
  }

  function seleccionar() {
    var pre = resumen.querySelector('textarea');
    pre.focus();
    pre.select();
    avisar('Tu navegador no deja copiar solo: ya quedó seleccionada, usa Ctrl+C.');
  }

  function descargar(t) {
    var blob = new Blob(['﻿' + t.replace(/\n/g, '\r\n')], { type: 'text/plain;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'solicitud-auditavision-' + fecha() + '.txt';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
    avisar('✓ Descargada como ' + a.download + '.');
  }

  function mostrar() {
    var t = armar();
    resumen.innerHTML = '';
    var h = document.createElement('h3');
    h.className = 'sv-res-tit';
    h.id = 'svResTit';
    h.textContent = 'Tu solicitud';
    var nota = document.createElement('p');
    nota.textContent = 'Revísala. Así es exactamente como se mandaría.';
    var area = document.createElement('textarea');
    area.className = 'sv-res-texto';
    area.readOnly = true;
    area.rows = Math.min(20, t.split('\n').length + 1);
    area.value = t;
    area.setAttribute('aria-labelledby', 'svResTit');
    var acc = document.createElement('div');
    acc.className = 'sv-acciones';
    if (canal) {
      var env = document.createElement('a');
      env.className = 'sz-btn sz-btn-of';
      env.textContent = '✉️ Enviar solicitud';
      var asunto = 'Solicitud de investigación: ' + val('svTema');
      env.href = canal + (canal.indexOf('?') < 0 ? '?' : '&') + 'subject=' + encodeURIComponent(asunto) + '&body=' + encodeURIComponent(t);
      acc.appendChild(env);
    } else {
      var b = boton('✉️ Enviar solicitud', 'sz-btn-of');
      b.disabled = true;
      b.setAttribute('aria-describedby', 'svSinCanal');
      acc.appendChild(b);
    }
    acc.appendChild(boton('📋 Copiar', '', function () { copiar(t); }));
    acc.appendChild(boton('⬇️ Descargar (.txt)', '', function () { descargar(t); }));
    acc.appendChild(boton('✏️ Corregir', '', function () { resumen.hidden = true; $('svTema').focus(); }));
    resumen.appendChild(h);
    resumen.appendChild(nota);
    resumen.appendChild(area);
    resumen.appendChild(acc);
    if (!canal) {
      var sin = document.createElement('p');
      sin.className = 'sv-sincanal';
      sin.id = 'svSinCanal';
      sin.innerHTML = '<span class="sz-et">Próximamente</span> El envío se activa con el lanzamiento de la plataforma. '
        + 'Mientras tanto, copia o descarga tu solicitud para tenerla lista.';
      resumen.appendChild(sin);
    }
    var estado = document.createElement('p');
    estado.className = 'sv-estado';
    estado.setAttribute('role', 'status');
    resumen.appendChild(estado);
    resumen.hidden = false;
    h.tabIndex = -1;
    h.focus();
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var r = revisar();
    if (r.faltan.length) {
      error.textContent = 'Para armar tu solicitud falta: ' + r.faltan.join(', ') + '.';
      error.hidden = false;
      resumen.hidden = true;
      if (r.primero) r.primero.focus();
      return;
    }
    error.hidden = true;
    mostrar();
  });

  form.addEventListener('reset', function () {
    error.hidden = true;
    resumen.hidden = true;
    resumen.innerHTML = '';
    form.querySelectorAll('[aria-invalid]').forEach(function (el) { el.removeAttribute('aria-invalid'); });
  });
})();
