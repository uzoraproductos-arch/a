/* Comunidad, primera version (propuesta de Astra, punto 11; entrega 7,
   10-10-2026): proponer temas, senalar errores y compartir el Estado de
   Cuenta Civico.

   Cada form.cm-form se arma en el navegador: revisa los campos obligatorios,
   muestra el texto tal como se mandaria y deja copiarlo o descargarlo. El
   boton de envio solo se activa si el formulario trae data-canal
   (CANAL_COMUNIDAD en herramientas/apartados.py). Nada se guarda.

   .cm-compartir[data-url][data-texto] pinta los botones de compartir: el
   menu nativo del telefono si existe, WhatsApp, X, Facebook y copiar.

   Pagina: comunidad.html (herramientas/apartados.py, comunidad()). Desde el
   10-10-2026 se carga en todas las paginas: tambien abre el cajon de
   «Cuéntanos lo que viste» (ver abajo). */
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

  /* El envío a la base de datos (paso 2.7 del plan v2, 27-10-2026). Solo si
     el formulario trae data-funcion (FUNCIONES de herramientas/apartados.py):
     manda el mismo texto que el lector ya vio a la función recibir-formulario
     de Supabase y le devuelve su folio. Si la red o el servidor fallan, el
     texto se queda en pantalla para copiarlo o descargarlo: nunca se pierde.
     El antispam (Cloudflare Turnstile) se carga solo cuando hay llave. */
  var tsCarga = null;
  function turnstile(llave, caja) {
    if (!llave) return Promise.resolve(null);
    if (!tsCarga) {
      tsCarga = new Promise(function (ok, mal) {
        var s = document.createElement('script');
        s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
        s.async = true;
        s.onload = function () { ok(window.turnstile); };
        s.onerror = mal;
        document.head.appendChild(s);
      });
    }
    return tsCarga.then(function (ts) { return ts.render(caja, { sitekey: llave }); });
  }

  function paginaActual() {
    var n = (location.pathname.split('/').pop() || 'index.html');
    return /^[a-z0-9-]+\.html$/.test(n) ? n : null;
  }

  function enviar(form, t, asunto, estado, boton, wid) {
    var url = form.getAttribute('data-funcion');
    var q = function (sel) { var el = form.querySelector(sel); return el ? el.value.trim() : ''; };
    var acepta = form.querySelector('[data-acepta]');
    var pag = q('.cm-pagina').replace(/^.*\//, '').split(/[?#]/)[0];
    var datos = {
      tipo: form.getAttribute('data-tipo'),
      asunto: asunto,
      texto: t,
      pagina: /^[a-z0-9-]+\.html$/.test(pag) ? pag : paginaActual(),
      documento: q('input[type="url"]') || null,
      correo: q('input[type="email"]') || null,
      acepta_aviso: !!(acepta && acepta.checked),
      turnstile: wid != null && window.turnstile ? window.turnstile.getResponse(wid) : null
    };
    boton.disabled = true;
    estado.textContent = 'Enviando…';
    var respaldo = ' Tu texto sigue aquí: cópialo o descárgalo para no perderlo.';
    fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(datos) })
      .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
      .then(function (j) {
        if (j && j.ok && j.folio) {
          estado.textContent = '✓ Recibido. Tu folio es ' + j.folio + ': guárdalo para darle seguimiento.';
          return;
        }
        boton.disabled = false;
        estado.textContent = ((j && j.error) || 'No pudimos recibirlo.') + respaldo;
        if (wid != null && window.turnstile) window.turnstile.reset(wid);
      })
      .catch(function () {
        boton.disabled = false;
        estado.textContent = 'No hay conexión con el servidor.' + respaldo;
      });
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
    var funcion = form.getAttribute('data-funcion') || '';
    var asunto = form.getAttribute('data-asunto') || 'Mensaje';
    var error = form.querySelector('.cm-error');
    var resumen = form.nextElementSibling;
    if (!resumen || !resumen.classList.contains('cm-resumen')) return;
    var campos = Array.prototype.slice.call(form.querySelectorAll('input:not([type="checkbox"]), textarea, select'));

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
      var cajaTs = null, wid = null;
      if (funcion) {
        var envia = boton('✉️ Enviar', 'sz-btn-of');
        envia.addEventListener('click', function () { enviar(form, t, asunto + ': ' + campos[0].value.trim(), estado, envia, wid); });
        acc.appendChild(envia);
        if (form.getAttribute('data-turnstile')) {
          cajaTs = document.createElement('div');
          cajaTs.className = 'cm-turnstile';
          turnstile(form.getAttribute('data-turnstile'), cajaTs).then(function (w) { wid = w; }, function () {
            estado.textContent = 'No cargó el antispam; si «Enviar» falla, copia o descarga tu texto.';
          });
        }
      } else if (canal) {
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
      if (cajaTs) resumen.appendChild(cajaTs);
      resumen.appendChild(acc);
      if (!canal && !funcion) {
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

  // Enlaces viejos de «¿Viste un error?» (comunidad.html?pagina=...#error).
  try {
    var pag = new URLSearchParams(location.search).get('pagina');
    var campo = document.getElementById('cmErrPagina');
    if (pag && campo && !campo.value) campo.value = pag.slice(0, 200);
  } catch (e) { /* el lector la escribe */ }

  /* «Cuéntanos lo que viste», la puerta unica (fusion del 10-10-2026 con
     «¿Viste un error?», que estaba al pie). Todo [data-puerta] abre el cajon
     #ptCajon (lo escribe herramientas/apartados.py, puerta()); su valor
     (reporta, error, tema, compartir, erratas) despliega esa ruta. Sin JavaScript, el enlace
     lleva a comunidad.html. En index.html lo abre tambien el motor
     (openAyudanosFiscalizar llama a window.Puerta). */
  var cajon = document.getElementById('ptCajon');
  var velo = document.getElementById('ptVelo');
  var previo = null;

  function abrirPuerta(ruta) {
    if (!cajon) return false;
    previo = document.activeElement;
    var pagina = document.getElementById('ptErrPagina');
    if (pagina && !pagina.value) {
      pagina.value = ((location.pathname.split('/').pop() || 'index.html') + ' · ' + document.title).slice(0, 200);
    }
    cajon.hidden = false;
    if (velo) velo.hidden = false;
    document.body.classList.add('pt-abierta');
    var d = ruta ? cajon.querySelector('.pt-ruta[data-ruta="' + ruta + '"]') : null;
    if (d) d.open = true;
    void cajon.offsetWidth;
    cajon.classList.add('pt-visible');
    if (velo) velo.classList.add('pt-visible');
    (d ? d.querySelector('summary') : cajon.querySelector('.pt-cerrar')).focus();
    return true;
  }

  function cerrarPuerta() {
    if (!cajon || cajon.hidden) return;
    cajon.classList.remove('pt-visible');
    cajon.hidden = true;
    if (velo) { velo.classList.remove('pt-visible'); velo.hidden = true; }
    document.body.classList.remove('pt-abierta');
    if (previo && previo.focus) previo.focus();
  }

  document.addEventListener('click', function (ev) {
    var t = ev.target;
    if (!t.closest) return;
    var a = t.closest('[data-puerta]');
    if (a && cajon && !ev.ctrlKey && !ev.metaKey && !ev.shiftKey) {
      ev.preventDefault();
      abrirPuerta(a.getAttribute('data-puerta'));
    } else if (t.closest('[data-pt-cerrar]') || (velo && t === velo)) {
      cerrarPuerta();
    }
  });
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') cerrarPuerta(); });
  if (cajon) {
    Array.prototype.forEach.call(cajon.querySelectorAll('.pt-ruta'), function (d) {
      d.addEventListener('toggle', function () {
        if (d.open && d.scrollIntoView) d.scrollIntoView({ block: 'nearest' });
      });
    });
  }
  window.Puerta = { abrir: abrirPuerta, cerrar: cerrarPuerta };

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
        navigator.share({ title: 'Contexto dimensional · Auditavisión', text: texto, url: url }).catch(function () {});
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
