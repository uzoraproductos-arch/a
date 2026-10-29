/* Las dos páginas de los códigos de acceso (pedido del autor, 29-10-2026):
   la entrada con sus ocho casillas, «¡Felicidades!» y «Obtén uno»
   (canjea-tu-codigo.html), y el panel de la administración, con las
   solicitudes y el acceso del administrador (administracion-codigos.html). La configuración y el pase
   los da acceso.js (window.AvAcceso). Lo genera herramientas/acceso.py. */
(function () {
  var A = window.AvAcceso, C = A && A.config;
  if (!C) return;
  var ALFA = '23456789ABCDEFGHJKMNPQRSTUVWXYZ';
  var $ = function (id) { return document.getElementById(id); };
  function fecha(iso) {
    var d = new Date(iso);
    return isNaN(d) ? '' : d.toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' }) + ', ' +
      d.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: false }) + ' h';
  }
  function limpia(t) { return String(t || '').toUpperCase().split('').filter(function (c) { return ALFA.indexOf(c) >= 0; }).join(''); }
  function bonito(c) { return c.slice(0, 4) + '-' + c.slice(4); }
  // Cómo se leen las duraciones de PostgreSQL. «100 years» es el ilimitado.
  var DUR = { '1 day': '1 día', '3 days': '3 días', '5 days': '5 días', '7 days': '1 semana', '14 days': '2 semanas',
              '1 mon': '1 mes', '3 mons': '3 meses', '6 mons': '6 meses', '1 year': '1 año', '100 years': 'Ilimitado' };
  function duracion(t) {
    t = String(t || '');
    if (DUR[t]) return DUR[t];
    var m = /^(\d+) days?$/.exec(t); if (m) return m[1] + ' días';
    return t.replace('mons', 'meses').replace('mon', 'mes').replace('years', 'años').replace('year', 'año').replace(':00:00', ' h');
  }
  var ILIMITADO = 50 * 365 * 864e5;  // más de 50 años por delante: ilimitado
  function esIlimitado(hasta) { return Date.parse(hasta) - Date.now() > ILIMITADO; }
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* ---------------- El canje ---------------- */
  function canje() {
    var f = $('acCanje'); if (!f) return;
    if (C.funciones && $('acSinBase')) $('acSinBase').hidden = true;
    var cajas = [].slice.call(f.querySelectorAll('.ac-casilla')), boton = f.querySelector('.ac-boton'), estado = $('acEstado');
    var volver = new URLSearchParams(location.search).get('volver') || '';
    // Solo se vuelve a una página de la plataforma, nunca a otro sitio.
    if (!/^[\w.-]+\.html([?#][^\s]*)?$/.test(volver)) volver = 'index.html';

    function codigo() { return cajas.map(function (c) { return c.value; }).join(''); }
    function revisa() { boton.disabled = codigo().length !== 8; }
    function reparte(desde, texto) {
      var t = limpia(texto), i = desde;
      for (var k = 0; k < t.length && i < 8; k++, i++) cajas[i].value = t[k];
      cajas[Math.min(i, 7)].focus();
      estado.textContent = '';
      revisa();
    }
    cajas.forEach(function (c, i) {
      c.addEventListener('input', function () {
        var v = c.value; c.value = '';
        if (v.length > 1) { reparte(i, v); return; }
        var t = limpia(v);
        if (!t && v) { estado.textContent = 'La «' + v + '» no se usa en los códigos.'; revisa(); return; }
        c.value = t; estado.textContent = '';
        if (t && i < 7) cajas[i + 1].focus();
        revisa();
      });
      c.addEventListener('keydown', function (e) {
        if (e.key === 'Backspace' && !c.value && i > 0) { cajas[i - 1].value = ''; cajas[i - 1].focus(); revisa(); e.preventDefault(); }
        else if (e.key === 'ArrowLeft' && i > 0) { cajas[i - 1].focus(); e.preventDefault(); }
        else if (e.key === 'ArrowRight' && i < 7) { cajas[i + 1].focus(); e.preventDefault(); }
      });
      c.addEventListener('paste', function (e) {
        var t = (e.clipboardData || window.clipboardData).getData('text');
        if (t) { e.preventDefault(); reparte(i, t); }
      });
      c.addEventListener('focus', function () { c.select(); });
    });

    var MOTIVO = {
      formato: 'Revisa el código: son ocho letras y números.',
      no_valido: 'Ese código no existe o ya no sirve. Revisa que esté bien escrito.',
      vencido: 'Ese código ya no se puede canjear: pasó su fecha límite.',
      agotado: 'Ese código ya se usó todas las veces que permite.',
      espera: 'Fueron muchos intentos. Espera unos minutos y vuelve a probar.'
    };
    function listo(p, texto) {
      var antes = A.leer() || {};
      A.guardar({ pase: p.pase, hasta: p.hasta, visto: Date.now(), admin: !!antes.admin });
      estado.textContent = '';
      felicidades(p.duracion, p.hasta, texto);
      muestraTuyo();
    }
    // «¡Felicidades! Cuentas con…» (pedido del autor, 29-10-2026).
    function felicidades(dur, hasta, nota) {
      var d = $('acFelicidades');
      var cuanto = esIlimitado(hasta) ? 'Cuentas con <b>acceso ilimitado</b> a toda la plataforma.'
        : dur ? 'Cuentas con <b>' + esc(duracion(dur).toLowerCase()) + '</b> de acceso a toda la plataforma.'
        : 'Tu código ya estaba activo en este navegador.';
      $('acFCuanto').innerHTML = cuanto;
      $('acFHasta').innerHTML = esIlimitado(hasta) ? '' : 'Tu acceso dura hasta el <b>' + esc(fecha(hasta)) + '</b>' +
        (nota ? '. ' + esc(nota) : '') + '.';
      $('acFEntrar').setAttribute('href', volver);
      if (d && d.showModal) { d.showModal(); $('acFEntrar').focus(); } else location.replace(volver);
    }
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!C.funciones) { estado.textContent = 'El canje todavía no está encendido: por ahora la entrada es libre.'; return; }
      var actual = A.leer();
      boton.disabled = true; estado.textContent = 'Revisando tu código…';
      A.pide({ accion: 'canjear', codigo: codigo(), pase: actual && actual.pase }).then(function (j) {
        if (j && j.ok) return listo(j, (A.vigente(actual) && actual.pase === j.pase) ? 'Se sumó al tiempo que te quedaba' : '');
        if (j && j.motivo === 'ya_canjeado' && j.hasta && Date.parse(j.hasta) > Date.now()) return listo({ pase: j.pase, hasta: j.hasta }, '');
        estado.textContent = MOTIVO[j && j.motivo] || 'No pudimos revisar tu código. Intenta de nuevo.';
        revisa();
      }).catch(function () { estado.textContent = 'No hubo conexión. Intenta de nuevo.'; revisa(); });
    });

    function muestraTuyo() {
      var p = A.leer(), caja = $('acTuyo');
      if (!caja) return;
      if (!p || !p.hasta) { caja.hidden = true; return; }
      caja.hidden = false;
      if (!A.vigente(p)) {
        // Se le acabó el tiempo: que pida otro (pedido del autor).
        caja.className = 'ac-tuyo ac-tuyo-fin';
        caja.innerHTML = '<p>Tu acceso terminó el <b>' + esc(fecha(p.hasta)) + '</b>. ¿Quieres seguir? Pide otro código aquí abajo.</p>';
        var b = $('acObtener'); if (b && $('acPedir').hidden) b.click();
        return;
      }
      caja.className = 'ac-tuyo';
      caja.innerHTML = '<p>' + (p.admin ? 'Entraste como <b>administración</b>. ' : '') +
        (esIlimitado(p.hasta) ? 'Tu acceso en este navegador es <b>ilimitado</b>.' : 'Tu acceso en este navegador vence el <b>' + esc(fecha(p.hasta)) + '</b>. Si canjeas otro código, se suma.') +
        '</p><p><a class="sz-btn sz-btn-of" href="' + esc(volver) + '">Entrar a la plataforma</a></p>';
    }
    muestraTuyo();
    var pega = new URLSearchParams(location.search).get('c');
    if (pega) reparte(0, pega);
  }

  /* ---------------- «¿No tienes código? Obtén uno» ---------------- */
  function pedir() {
    var b = $('acObtener'), f = $('acPedir'); if (!b || !f) return;
    b.addEventListener('click', function () {
      f.hidden = !f.hidden; b.setAttribute('aria-expanded', String(!f.hidden));
      if (!f.hidden) f.correo.focus();
    });
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var est = $('acPEstado'), correo = f.correo.value.trim();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(correo)) { est.textContent = 'Escribe un correo válido.'; f.correo.focus(); return; }
      if (!f.acepta.checked) { est.textContent = 'Para mandarte el código necesitamos que aceptes el aviso de privacidad.'; return; }
      if (!C.funciones) { est.textContent = 'Las solicitudes se encienden cuando la plataforma tenga su base de datos.'; return; }
      var boton = f.querySelector('button[type=submit]'); boton.disabled = true; est.textContent = 'Enviando tu solicitud…';
      A.pide({ accion: 'solicitar', correo: correo, nombre: f.nombre.value.trim() || null, motivo: f.motivo.value.trim() || null, acepta_aviso: true })
        .then(function (j) {
          if (j && j.ok) {
            f.innerHTML = '<p class="ac-pedido">✅ <b>Listo, recibimos tu solicitud</b> (folio ' + esc(j.folio) + '). Te mandaremos tu código a <b>' +
              esc(correo) + '</b>. Revisa también tu carpeta de correo no deseado.</p>';
            return;
          }
          est.textContent = j && j.motivo === 'espera' ? 'Ya recibimos varias solicitudes desde aquí. Intenta más tarde.'
            : j && j.motivo === 'correo' ? 'Escribe un correo válido.' : 'No pudimos enviar tu solicitud. Intenta de nuevo.';
          boton.disabled = false;
        }).catch(function () { est.textContent = 'No hubo conexión. Intenta de nuevo.'; boton.disabled = false; });
    });
  }

  /* ---------------- El panel de la administración ---------------- */
  function panel() {
    var raiz = $('acPanel'); if (!raiz) return;
    var CLAVE = 'av-admin', s = null, lista = [];
    var EST = { en_uso: 'En uso', sin_usar: 'Sin usar', vencido: 'Vencido', terminado: 'Terminado', revocado: 'Revocado' };
    function lee() { try { s = JSON.parse(sessionStorage.getItem(CLAVE) || 'null'); } catch (e) { s = null; } }
    function pon(x) { s = x; try { if (x) sessionStorage.setItem(CLAVE, JSON.stringify(x)); else sessionStorage.removeItem(CLAVE); } catch (e) {} }
    function auth(ruta, cuerpo, token, metodo) {
      var h = { 'Content-Type': 'application/json', 'apikey': C.anon };
      if (token) h.Authorization = 'Bearer ' + token;
      return fetch(C.supabase + ruta, { method: metodo || 'POST', headers: h, body: cuerpo ? JSON.stringify(cuerpo) : undefined })
        .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw j; return j; }); });
    }
    function token() {
      if (!s) return Promise.reject({ message: 'sin sesión' });
      if (Date.now() < s.vence - 60000) return Promise.resolve(s.token);
      return auth('/auth/v1/token?grant_type=refresh_token', { refresh_token: s.refresh }).then(function (j) {
        pon({ token: j.access_token, refresh: j.refresh_token, vence: Date.now() + j.expires_in * 1000, correo: s.correo });
        return s.token;
      });
    }
    function rpc(nombre, args) {
      return token().then(function (t) { return auth('/rest/v1/rpc/' + nombre, args || {}, t); });
    }

    // Al volver del enlace mágico, la sesión llega en la dirección (#access_token=…).
    var h = new URLSearchParams(location.hash.slice(1));
    if (h.get('access_token')) {
      pon({ token: h.get('access_token'), refresh: h.get('refresh_token'), vence: Date.now() + (+h.get('expires_in') || 3600) * 1000 });
      history.replaceState(null, '', location.pathname);
    } else lee();

    var entrar = $('acEntrar'), admin = $('acAdmin');
    if (!C.supabase || !C.anon) {
      $('acEntrarEstado').textContent = 'El panel se enciende cuando la plataforma tenga su base de datos (Supabase) y su llave pública.';
      entrar.querySelector('button').disabled = true;
      return;
    }
    entrar.addEventListener('submit', function (e) {
      e.preventDefault();
      var correo = $('acCorreo').value.trim(), est = $('acEntrarEstado');
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(correo)) { est.textContent = 'Escribe un correo válido.'; return; }
      est.textContent = 'Mandando el enlace…';
      auth('/auth/v1/otp?redirect_to=' + encodeURIComponent(location.href.split('#')[0]), { email: correo, create_user: false })
        .then(function () { est.textContent = 'Listo: revisa tu correo y abre el enlace desde este mismo navegador.'; })
        .catch(function () { est.textContent = 'No se pudo mandar. Revisa que el correo sea el de la administración.'; });
    });
    $('acSalir').addEventListener('click', function () { pon(null); location.reload(); });

    function pinta() {
      var cuenta = {};
      lista.forEach(function (k) { cuenta[k.estado] = (cuenta[k.estado] || 0) + 1; });
      $('acResumen').innerHTML = Object.keys(EST).map(function (e) {
        return '<span class="ac-chip ac-' + e + '">' + EST[e] + ': <b>' + (cuenta[e] || 0) + '</b></span>';
      }).join(' ');
      $('acTabla').querySelector('tbody').innerHTML = lista.map(function (k) {
        var est = EST[k.estado] + (k.estado === 'en_uso' && k.hasta ? ' hasta el ' + fecha(k.hasta) : '') +
          (k.estado === 'sin_usar' && k.canjear_antes ? ' (canjear antes del ' + fecha(k.canjear_antes) + ')' : '');
        return '<tr><td><button class="ac-cod" type="button" data-copia="' + esc(bonito(k.codigo)) + '" title="Copiar">' + esc(bonito(k.codigo)) + '</button></td>' +
          '<td>' + esc(duracion(k.duracion)) + '</td><td>' + k.usos + ' de ' + k.usos_max + '</td>' +
          '<td><span class="ac-chip ac-' + k.estado + '">' + esc(est) + '</span></td><td>' + esc(k.nota || '') + '</td>' +
          '<td><button class="sz-btn ac-chico ac-claro" type="button" data-id="' + k.id + '" data-revocar="' + (k.revocado ? '0' : '1') + '">' +
          (k.revocado ? 'Devolver' : 'Revocar') + '</button></td></tr>';
      }).join('') || '<tr><td colspan="6">Todavía no hay códigos.</td></tr>';
    }
    var sols = [];
    var SOL = { nueva: 'Nueva', enviada: 'Enviada', descartada: 'Descartada' };
    var opciones = Object.keys(DUR).map(function (k) { return '<option value="' + k + '"' + (k === '7 days' ? ' selected' : '') + '>' + DUR[k] + '</option>'; }).join('');
    function pintaSol() {
      var nuevas = sols.filter(function (x) { return x.estado === 'nueva'; }).length;
      $('acSolCuenta').textContent = nuevas ? nuevas + (nuevas === 1 ? ' nueva' : ' nuevas') : 'sin pendientes';
      $('acSol').querySelector('tbody').innerHTML = sols.map(function (x) {
        var quien = [x.nombre, x.motivo].filter(Boolean).map(esc).join(' · ') + (x.veces > 1 ? ' <span class="ac-chip">pidió ' + x.veces + ' veces</span>' : '');
        var accion = x.estado === 'nueva'
          ? '<select class="ac-campo ac-sol-dur" data-sol="' + x.id + '" aria-label="Duración para ' + esc(x.correo) + '">' + opciones + '</select> ' +
            '<button class="sz-btn sz-btn-of ac-chico" type="button" data-asignar="' + x.id + '">Asignar código</button> ' +
            '<button class="sz-btn ac-chico ac-claro" type="button" data-descartar="' + x.id + '">Descartar</button>'
          : x.codigo ? '<a class="sz-btn ac-chico ac-claro" href="' + esc(correoA(x.correo, x.nombre, x.codigo, x.duracion)) + '">Escribirle otra vez</a>' : '';
        return '<tr><td>' + esc(x.correo) + '</td><td>' + (quien || '—') + '</td><td>' + esc(fecha(x.creado)) + '</td>' +
          '<td>' + esc(SOL[x.estado]) + (x.codigo ? ': <b>' + esc(bonito(x.codigo)) + '</b> (' + esc(duracion(x.duracion)) + ')' : '') + '</td><td>' + accion + '</td></tr>';
      }).join('') || '<tr><td colspan="5">Todavía nadie ha pedido código.</td></tr>';
    }
    // El correo lo manda el autor desde el suyo: aquí solo se arma el mensaje.
    function correoA(correo, nombre, cod, dur) {
      var sitio = location.href.replace(/[^/]*$/, '');
      var cuerpo = 'Hola' + (nombre ? ' ' + nombre : '') + ':\n\nGracias por querer probar Auditavisión, el gasto público a la vista.\n\n' +
        'Tu código de acceso es: ' + bonito(cod) + '\n' +
        (dur === '100 years' ? 'Tu acceso es ilimitado.' : 'Te da ' + duracion(dur).toLowerCase() + ' de acceso a toda la plataforma, contados desde que lo ingreses.') + '\n\n' +
        'Entra aquí: ' + sitio + 'canjea-tu-codigo.html?c=' + cod + '\n\n' +
        'Cuando se te acabe el tiempo, pide otro desde la misma página. Y si ves algo que mejorar, cuéntanos: tu opinión nos ayuda mucho.\n';
      return 'mailto:' + encodeURIComponent(correo) + '?subject=' + encodeURIComponent('Tu código de acceso a Auditavisión') + '&body=' + encodeURIComponent(cuerpo);
    }
    function carga() {
      return Promise.all([
        rpc('codigos_lista').then(function (j) { lista = j || []; pinta(); }),
        rpc('solicitudes_lista').then(function (j) { sols = j || []; pintaSol(); })
      ]);
    }
    $('acSol').addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      if (b.dataset.asignar) {
        var dur = $('acSol').querySelector('select[data-sol="' + b.dataset.asignar + '"]').value;
        b.disabled = true;
        rpc('atender_solicitud', { p_id: +b.dataset.asignar, p_duracion: dur }).then(function (r) {
          location.href = correoA(r.correo, r.nombre, r.codigo, r.duracion);
          return carga();
        }).catch(function () { b.disabled = false; alert('No se pudo asignar el código. Intenta de nuevo.'); });
      } else if (b.dataset.descartar && confirm('¿Descartar esta solicitud?')) {
        rpc('descartar_solicitud', { p_id: +b.dataset.descartar }).then(carga);
      }
    });
    // El administrador entra a la plataforma sin gastar códigos: su navegador
    // recibe un pase ilimitado y la entrada lo reconoce (pedido del autor).
    $('acComoAdmin').addEventListener('click', function () {
      var est = $('acComoAdminEstado'), p = A.leer();
      if (p && p.admin && A.vigente(p)) { location.href = 'index.html'; return; }
      est.textContent = 'Preparando tu acceso…';
      rpc('generar_codigos', { p_cantidad: 1, p_duracion: '100 years', p_usos: 1, p_antes: null, p_nota: 'Administración: ' + (s.correo || '') })
        .then(function (k) { return A.pide({ accion: 'canjear', codigo: k[0].codigo, pase: p && p.pase }); })
        .then(function (j) {
          if (!j || !j.ok) throw j;
          A.guardar({ pase: j.pase, hasta: j.hasta, visto: Date.now(), admin: true });
          location.href = 'index.html';
        }).catch(function () { est.textContent = 'No se pudo preparar tu acceso. Intenta de nuevo.'; });
    });
    function abre() {
      token().then(function (t) { return auth('/auth/v1/user', null, t, 'GET'); }).then(function (u) {
        s.correo = u.email; pon(s);
        $('acQuien').textContent = 'Entraste como ' + u.email + '.';
        return carga();
      }).then(function () { entrar.hidden = true; admin.hidden = false; })
        .catch(function (e) {
          var no = e && /administraci/.test(e.message || '');
          $('acEntrarEstado').textContent = no ? 'Esta cuenta no está dada de alta en la administración.' : 'Tu sesión venció: vuelve a pedir el enlace.';
          if (!no) pon(null);
        });
    }
    if (s) abre();

    var g = $('acGenerar');
    g.duracion.addEventListener('change', function () { g.querySelector('.ac-otra').hidden = g.duracion.value !== 'otra'; });
    g.addEventListener('submit', function (e) {
      e.preventDefault();
      var est = $('acGenerarEstado');
      var dur = g.duracion.value === 'otra' ? (Math.max(1, Math.min(1825, +g.dias.value || 0)) + ' days') : g.duracion.value;
      var antes = g.antes.value ? new Date(g.antes.value + 'T23:59:59').toISOString() : null;
      est.textContent = 'Generando…';
      rpc('generar_codigos', { p_cantidad: +g.cantidad.value, p_duracion: dur, p_usos: +g.usos.value || 1, p_antes: antes, p_nota: g.nota.value || null })
        .then(function (nuevos) {
          est.textContent = 'Listo: ' + nuevos.length + ' códigos nuevos de ' + duracion(dur) + '. Están arriba de la lista.';
          return carga();
        }).catch(function (e2) { est.textContent = 'No se pudieron generar: ' + ((e2 && e2.message) || 'intenta de nuevo') + '.'; });
    });
    $('acRecargar').addEventListener('click', function () { carga(); });
    $('acTabla').addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      if (b.dataset.copia) {
        navigator.clipboard && navigator.clipboard.writeText(b.dataset.copia).then(function () { b.classList.add('ac-copiado'); setTimeout(function () { b.classList.remove('ac-copiado'); }, 1200); });
        return;
      }
      if (b.dataset.id) {
        var revoca = b.dataset.revocar === '1';
        if (revoca && !confirm('¿Revocar este código? Quien lo canjeó pierde su tiempo.')) return;
        rpc('revocar_codigo', { p_id: +b.dataset.id, p_revocado: revoca }).then(carga);
      }
    });
    $('acCsv').addEventListener('click', function () {
      var filas = [['codigo', 'duracion', 'usos', 'usos_max', 'estado', 'hasta', 'canjear_antes', 'nota', 'creado']].concat(lista.map(function (k) {
        return [bonito(k.codigo), duracion(k.duracion), k.usos, k.usos_max, EST[k.estado], k.hasta || '', k.canjear_antes || '', k.nota || '', k.creado];
      }));
      var csv = filas.map(function (f) { return f.map(function (x) { return '"' + String(x).replace(/"/g, '""') + '"'; }).join(','); }).join('\r\n');
      var a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' }));
      a.download = 'codigos-auditavision.csv'; a.click();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { pedir(); canje(); panel(); });
  else { pedir(); canje(); panel(); }
})();
