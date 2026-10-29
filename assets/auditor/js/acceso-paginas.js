/* Las dos páginas de los códigos de acceso (pedido del autor, 29-10-2026):
   el canje con sus ocho casillas (canjea-tu-codigo.html) y el panel de la
   administración (administracion-codigos.html). La configuración y el pase
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
      A.guardar({ pase: p.pase, hasta: p.hasta, visto: Date.now() });
      estado.innerHTML = '✅ ' + texto + ' Tienes acceso hasta el <b>' + esc(fecha(p.hasta)) + '</b>.';
      muestraTuyo();
      setTimeout(function () { location.replace(volver); }, 2500);
    }
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!C.funciones) { estado.textContent = 'El canje todavía no está encendido: por ahora la entrada es libre.'; return; }
      var actual = A.leer();
      boton.disabled = true; estado.textContent = 'Revisando tu código…';
      A.pide({ accion: 'canjear', codigo: codigo(), pase: actual && actual.pase }).then(function (j) {
        if (j && j.ok) return listo(j, 'Listo.');
        if (j && j.motivo === 'ya_canjeado' && j.hasta && Date.parse(j.hasta) > Date.now()) return listo(j, 'Ese código ya estaba canjeado en este navegador.');
        estado.textContent = MOTIVO[j && j.motivo] || 'No pudimos revisar tu código. Intenta de nuevo.';
        revisa();
      }).catch(function () { estado.textContent = 'No hubo conexión. Intenta de nuevo.'; revisa(); });
    });

    function muestraTuyo() {
      var p = A.leer(), caja = $('acTuyo');
      if (!caja) return;
      if (!A.vigente(p)) { caja.hidden = true; return; }
      caja.hidden = false;
      caja.innerHTML = '<p>Tu acceso en este navegador vence el <b>' + esc(fecha(p.hasta)) + '</b>. Si canjeas otro código, se suma.</p>' +
        '<p><a class="sz-btn" href="' + esc(volver) + '">Seguir a la plataforma</a></p>';
    }
    muestraTuyo();
    var pega = new URLSearchParams(location.search).get('c');
    if (pega) reparte(0, pega);
  }

  /* ---------------- El panel de la administración ---------------- */
  function panel() {
    var raiz = $('acPanel'); if (!raiz) return;
    var CLAVE = 'av-admin', s = null, lista = [];
    var DUR = { '1 day': '1 día', '3 days': '3 días', '5 days': '5 días', '7 days': '1 semana', '14 days': '2 semanas',
                '1 mon': '1 mes', '3 mons': '3 meses', '6 mons': '6 meses', '1 year': '1 año' };
    var EST = { en_uso: 'En uso', sin_usar: 'Sin usar', vencido: 'Vencido', terminado: 'Terminado', revocado: 'Revocado' };
    function duracion(t) {
      if (DUR[t]) return DUR[t];
      var m = /^(\d+) days?$/.exec(t); if (m) return m[1] + ' días';
      return t.replace('mons', 'meses').replace('mon', 'mes').replace('years', 'años').replace('year', 'año').replace(':00:00', ' h');
    }
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
    function carga() {
      return rpc('codigos_lista').then(function (j) { lista = j || []; pinta(); });
    }
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

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { canje(); panel(); });
  else { canje(); panel(); }
})();
