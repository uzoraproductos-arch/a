/* Comunidad, primera version (propuesta de Astra, punto 11; entrega 7,
   10-10-2026): proponer temas, senalar errores y compartir el Estado de
   Cuenta Civico.

   Cada form.cm-form se arma en el navegador: revisa los campos obligatorios,
   muestra el texto tal como se mandaria y deja copiarlo o descargarlo. El
   boton de envio solo se activa si el formulario trae data-canal
   (CANAL_COMUNIDAD en herramientas/apartados.py). Nada se guarda.

   .cm-compartir[data-url][data-texto] pinta los botones de compartir: el
   menu nativo del telefono si existe, WhatsApp, X, Facebook y copiar.

   Pagina: comunidad.html (herramientas/apartados.py, comunidad()). */
(function () {
  'use strict';

  function fecha() {
    var d = new Date();
    function dos(n) { return (n < 10 ? '0' : '') + n; }
    return dos(d.getDate()) + '-' + dos(d.getMonth() + 1) + '-' + d.getFullYear();
  }

  function etiqueta(form, el) {
    var l = form.querySelector('label[for="' + el.id + '"]');
    if (!l) return el.id;
    var c = l.cloneNode(true);
    var r = c.querySelector('.sv-req');
    if (r) r.remove();
    return c.textContent.trim();
  }

  function boton(txt, clase, fn) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'sz-btn' + (clase ? ' ' + clase : '');
    b.textContent = txt;
    if (fn) b.addEventListener('click', fn);
    return b;
  }

  function copiarTexto(t, ok, falla) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t).then(ok, falla);
    } else {
      falla();
    }
  }

  function descargar(t, nombre) {
    var blob = new Blob(['﻿' + t.replace(/\n/g, '\r\n')], { type: 'text/plain;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = nombre;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  function valido(el) {
    var v = el.value.trim();
    if (el.required && !v) return false;
    if (v && el.type === 'email') return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
    if (v && el.type === 'url') return /^https?:\/\/\S+\.\S+/.test(v);
    return true;
  }

  function preparar(form) {
    var canal = form.getAttribute('data-canal') || '';
    var asunto = form.getAttribute('data-asunto') || 'Mensaje';
    var error = form.querySelector('.cm-error');
    var resumen = form.nextElementSibling;
    if (!resumen || !resumen.classList.contains('cm-resumen')) return;
    var campos = Array.prototype.slice.call(form.querySelectorAll('input, textarea, select'));

    function armar() {
      var r = [asunto + ' · Auditavisión', 'Fecha: ' + fecha(), ''];
      campos.forEach(function (el) {
        var v = el.value.trim();
        r.push(etiqueta(form, el) + ': ' + (v || 'sin indicar'));
      });
      return r.join('\n');
    }

    function mostrar() {
      var t = armar();
      resumen.innerHTML = '';
      var h = document.createElement('h3');
      h.className = 'sv-res-tit';
      h.id = form.id + 'ResTit';
      h.textContent = 'Así quedaría';
      var area = document.createElement('textarea');
      area.className = 'sv-res-texto';
      area.readOnly = true;
      area.rows = Math.min(16, t.split('\n').length + 1);
      area.value = t;
      area.setAttribute('aria-labelledby', h.id);
      var estado = document.createElement('p');
      estado.className = 'sv-estado';
      estado.setAttribute('role', 'status');
      var acc = document.createElement('div');
      acc.className = 'sv-acciones';
      if (canal) {
        var env = document.createElement('a');
        env.className = 'sz-btn sz-btn-of';
        env.textContent = '✉️ Enviar';
        env.href = canal + (canal.indexOf('?') < 0 ? '?' : '&') + 'subject=' + encodeURIComponent(asunto + ': ' + campos[0].value.trim()) + '&body=' + encodeURIComponent(t);
        acc.appendChild(env);
      } else {
        var b = boton('✉️ Enviar', 'sz-btn-of');
        b.disabled = true;
        acc.appendChild(b);
      }
      acc.appendChild(boton('📋 Copiar', '', function () {
        copiarTexto(t, function () { estado.textContent = '✓ Copiado.'; }, function () {
          area.focus(); area.select(); estado.textContent = 'Ya quedó seleccionado: usa Ctrl+C.';
        });
      }));
      acc.appendChild(boton('⬇️ Descargar (.txt)', '', function () {
        var n = asunto.toLowerCase().replace(/[^a-z]+/g, '-') + '-' + fecha() + '.txt';
        descargar(t, n);
        estado.textContent = '✓ Descargado como ' + n + '.';
      }));
      acc.appendChild(boton('✏️ Corregir', '', function () { resumen.hidden = true; campos[0].focus(); }));
      resumen.appendChild(h);
      resumen.appendChild(area);
      resumen.appendChild(acc);
      if (!canal) {
        var sin = document.createElement('p');
        sin.className = 'sv-sincanal';
        sin.innerHTML = '<span class="sz-et">Próximamente</span> El envío se activa con el lanzamiento. Mientras, cópialo o descárgalo.';
        resumen.appendChild(sin);
      }
      resumen.appendChild(estado);
      resumen.hidden = false;
      h.tabIndex = -1;
      h.focus();
    }

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var faltan = [];
      var primero = null;
      campos.forEach(function (el) {
        var ok = valido(el);
        if (ok) el.removeAttribute('aria-invalid'); else el.setAttribute('aria-invalid', 'true');
        if (!ok) { faltan.push(etiqueta(form, el).toLowerCase()); if (!primero) primero = el; }
      });
      if (faltan.length) {
        error.textContent = 'Falta o no es válido: ' + faltan.join(', ') + '.';
        error.hidden = false;
        resumen.hidden = true;
        primero.focus();
        return;
      }
      error.hidden = true;
      mostrar();
    });

    form.addEventListener('reset', function () {
      error.hidden = true;
      resumen.hidden = true;
      resumen.innerHTML = '';
      campos.forEach(function (el) { el.removeAttribute('aria-invalid'); });
    });
  }

  Array.prototype.forEach.call(document.querySelectorAll('form.cm-form'), preparar);

  // «¿Viste un error?» llega con la pagina: comunidad.html?pagina=...#error
  try {
    var pag = new URLSearchParams(location.search).get('pagina');
    var campo = document.getElementById('cmErrPagina');
    if (pag && campo && !campo.value) campo.value = pag.slice(0, 200);
  } catch (e) { /* el lector la escribe */ }

  Array.prototype.forEach.call(document.querySelectorAll('.cm-compartir'), function (caja) {
    var url = caja.getAttribute('data-url');
    var texto = caja.getAttribute('data-texto');
    var redes = caja.querySelector('.cm-redes');
    if (!url || !redes) return;
    var estado = document.createElement('p');
    estado.className = 'sv-estado';
    estado.setAttribute('role', 'status');
    function enlace(txt, href) {
      var a = document.createElement('a');
      a.className = 'sz-btn';
      a.textContent = txt;
      a.href = href;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      redes.appendChild(a);
    }
    if (navigator.share) {
      redes.appendChild(boton('📤 Compartir', 'sz-btn-of', function () {
        navigator.share({ title: 'Estado de Cuenta Cívico · Auditavisión', text: texto, url: url }).catch(function () {});
      }));
    }
    enlace('WhatsApp', 'https://wa.me/?text=' + encodeURIComponent(texto + ' ' + url));
    enlace('X', 'https://x.com/intent/post?text=' + encodeURIComponent(texto) + '&url=' + encodeURIComponent(url));
    enlace('Facebook', 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url));
    redes.appendChild(boton('🔗 Copiar enlace', '', function () {
      copiarTexto(url, function () { estado.textContent = '✓ Enlace copiado.'; },
        function () { estado.textContent = 'Copia esta dirección: ' + url; });
    }));
    caja.appendChild(estado);
  });
})();
