/* Las dos páginas de los códigos de acceso (pedido del autor, 29-10-2026):
   la entrada con sus ocho casillas, «¡Felicidades!» y «Obtén uno»
   (canjea-tu-codigo.html), y el panel de la administración, con las
   solicitudes y el acceso del administrador (administracion-codigos.html). La configuración y el pase
   los da acceso.js (window.AvAcceso). Lo genera herramientas/acceso.py. */
(function () {
  var A = window.AvAcceso, C = A && A.config;
  if (!C) return;
  var ALFA = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
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
    function revisa() {
      boton.disabled = codigo().length !== 8;
      cajas.forEach(function (c) { c.classList.toggle('llena', !!c.value); });
    }
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
      formato: 'Revisa el código: son ocho números o letras.',
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
        if (j && j.ok && j.admin) return maestro(j.token_hash);
        if (j && j.ok) return listo(j, (A.vigente(actual) && actual.pase === j.pase) ? 'Se sumó al tiempo que te quedaba' : '');
        if (j && j.motivo === 'ya_canjeado' && j.hasta && Date.parse(j.hasta) > Date.now()) return listo({ pase: j.pase, hasta: j.hasta }, '');
        estado.textContent = MOTIVO[j && j.motivo] || 'No pudimos revisar tu código. Intenta de nuevo.';
        revisa();
      }).catch(function () { estado.textContent = 'No hubo conexión. Intenta de nuevo.'; revisa(); });
    });

    // El código maestro (30-10-2026): la función devuelve un enlace de un solo
    // uso que aquí se cambia por la sesión de la administración, y el panel abre.
    function maestro(hash) {
      estado.textContent = 'Te reconocimos: abriendo tu panel de administración…';
      return fetch(C.supabase + '/auth/v1/verify', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'apikey': C.anon },
        body: JSON.stringify({ type: 'magiclink', token_hash: hash })
      }).then(function (r) { return r.json().then(function (j) { if (!r.ok || !j.access_token) throw j; return j; }); })
        .then(function (j) {
          try {
            sessionStorage.setItem('av-admin', JSON.stringify({ token: j.access_token, refresh: j.refresh_token,
              vence: Date.now() + (+j.expires_in || 3600) * 1000 }));
          } catch (e) {}
          location.href = C.panel + '?maestro=1';
        });
    }

    function muestraTuyo() {
      var p = A.leer(), caja = $('acTuyo');
      if (!caja) return;
      if (!p || !p.hasta) { caja.hidden = true; return; }
      caja.hidden = false;
      if (!A.vigente(p)) {
        // Se le acabó el tiempo: que pida otro (pedido del autor).
        caja.className = 'ac-tuyo ac-tuyo-fin';
        if (p.admin) {
          // El código de la administración cambió (cada lunes): el aviso lo manda al panel por el nuevo.
          caja.innerHTML = '<p>🔑 <b>Tu código de administración cambió</b> el ' + esc(fecha(p.hasta)) + ', como cada semana. ' +
            'Entra al panel con tu correo para ver el nuevo.</p><p><a class="sz-btn sz-btn-of" href="' + 'administracion-codigos.html' + '">Ver mi código nuevo</a></p>';
          return;
        }
        caja.innerHTML = '<p>Tu acceso terminó el <b>' + esc(fecha(p.hasta)) + '</b>. ¿Quieres seguir? Pide otro código en la pestaña «Solicitar código».</p>';
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

  /* ---------------- «Tengo código» / «Solicitar código» (Ronda 12) ----------------
     Dos pestañas accesibles en la tarjeta de la entrada: las flechas cambian de pestaña y
     cada botón [data-pide-codigo] lleva a la tarjeta con «Solicitar código» abierta. */
  function pedir() {
    var f = $('acPedir'); if (!f) return;
    var tabs = [$('tabTengo'), $('tabPedir')].filter(Boolean);
    function activa(tab, foco) {
      tabs.forEach(function (x) {
        var si = x === tab;
        x.setAttribute('aria-selected', String(si)); x.tabIndex = si ? 0 : -1;
        var pan = $(x.getAttribute('aria-controls')); if (pan) pan.hidden = !si;
      });
      if (foco) tab.focus();
    }
    tabs.forEach(function (x, i) {
      x.addEventListener('click', function () { activa(x, false); });
      x.addEventListener('keydown', function (e) {
        var k = { ArrowRight: 1, ArrowLeft: -1, Home: -9, End: 9 }[e.key]; if (!k) return;
        e.preventDefault();
        var j = k === -9 ? 0 : k === 9 ? tabs.length - 1 : (i + k + tabs.length) % tabs.length;
        activa(tabs[j], true);
      });
    });
    var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    Array.prototype.forEach.call(document.querySelectorAll('[data-pide-codigo]'), function (x) {
      x.addEventListener('click', function () {
        if ($('tabPedir')) activa($('tabPedir'), false);
        var t = $('acTarjeta') || f;
        t.scrollIntoView({ behavior: quieto ? 'auto' : 'smooth', block: 'center' });
        setTimeout(function () { if (f.correo) f.correo.focus({ preventScroll: true }); }, quieto ? 0 : 450);
      });
    });
    // Un acceso vencido abre de una vez «Solicitar código».
    var p = A.leer && A.leer();
    if (p && p.hasta && !p.admin && A.vigente && !A.vigente(p) && $('tabPedir')) activa($('tabPedir'), false);
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
        .then(function (r) {
          // Una función que no devuelve nada contesta sin cuerpo (204).
          return r.text().then(function (t) { var j = t ? JSON.parse(t) : null; if (!r.ok) throw j; return j; });
        });
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

    // El registro: activos o archivados, con buscador, y cada renglón con sus
    // acciones (editar, revocar, archivar y eliminar). El código de la semana
    // solo se copia: se cambia arriba, con «Cambiarlo ahora».
    var vista = 'activos', editando = null, uso = null;
    // Cuánto tiempo, dicho en días u horas: «3 días», «5 h».
    function lapso(ms) {
      if (ms < 36e5) return 'menos de 1 h';
      if (ms < 864e5) return Math.floor(ms / 36e5) + ' h';
      var d = Math.floor(ms / 864e5); return d + (d === 1 ? ' día' : ' días');
    }
    // El registro de uso de un código: una línea por persona que lo canjeó.
    function registro(k) {
      if (!uso || uso.id !== k.id) return '';
      var filas = uso.filas;
      var cuerpo = !filas ? '<p>Cargando el registro…</p>' : !filas.length ? '<p>Nadie lo ha canjeado todavía.</p>' :
        '<table class="ac-tabla ac-uso"><thead><tr><th>Quién</th><th>Lo canjeó</th><th>Lo lleva usando</th><th>Le queda</th><th>Última vez</th><th>Días que entró</th><th>Minutos de uso</th><th>Páginas vistas</th></tr></thead><tbody>' +
        filas.map(function (u) {
          var ahora = Date.now(), ini = Date.parse(u.canjeado), fin = u.hasta ? Date.parse(u.hasta) : ini;
          var quien = u.nombre || u.correo ? esc(u.nombre || '') + (u.correo ? ' <span class="ac-ayuda">' + esc(u.correo) + '</span>' : '') : 'Persona ' + u.persona;
          var queda = fin > ahora ? (esIlimitado(u.hasta) ? 'Ilimitado' : lapso(fin - ahora)) : 'Se le acabó el ' + fecha(u.hasta);
          return '<tr><td>' + quien + (u.renovado ? ' <span class="ac-chip ac-en_uso">renovado</span>' : '') + '</td><td>' + fecha(u.canjeado) + '</td><td>' + lapso(Math.min(ahora, fin) - ini) + '</td>' +
            '<td>' + queda + '</td><td>' + (u.ultimo ? new Date(u.ultimo + 'T12:00:00').toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' }) : '—') + '</td><td>' + u.dias + '</td>' +
            '<td>' + num(u.minutos) + '</td><td>' + num(u.vistas) + '</td></tr>';
        }).join('') + '</tbody></table>';
      return '<tr class="ac-editor"><td colspan="6"><div class="ac-tabla-caja"><p class="ac-ancho"><b>Uso del ' + esc(bonito(k.codigo)) + '</b> · ' + k.usos + ' de ' + k.usos_max + ' personas</p>' + cuerpo +
        '<p class="ac-ayuda">«Días que entró» cuenta los días distintos en que abrió la plataforma. «Minutos de uso» suma el tiempo con una página a la vista y «Páginas vistas», ' +
        'las que abrió (de lo medido desde el 18-11-2026, últimos 12 meses; no cuenta si su navegador pide no ser medido). Nada dice quién es: ' +
        'el nombre y el correo solo salen si el código vino de una solicitud.</p>' +
        '<p class="ac-acciones">' + boton('Cerrar', 'data-cerraruso="1"') + '</p></div></td></tr>';
    }
    function fechaCampo(iso) {
      if (!iso) return '';
      var d = new Date(iso); return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
    }
    function boton(txt, datos, clase) {
      return '<button class="sz-btn ac-chico ' + (clase || 'ac-claro') + '" type="button" ' + datos + '>' + txt + '</button>';
    }
    function editor(k) {
      var ops = Object.keys(DUR).map(function (d) { return '<option value="' + d + '"' + (d === k.duracion ? ' selected' : '') + '>' + DUR[d] + '</option>'; }).join('');
      if (!DUR[k.duracion]) ops = '<option value="' + esc(k.duracion) + '" selected>' + esc(duracion(k.duracion)) + '</option>' + ops;
      return '<tr class="ac-editor"><td colspan="6"><form class="ac-fila" data-editar="' + k.id + '">' +
        '<p class="ac-ancho"><b>Editar ' + esc(bonito(k.codigo)) + '</b>' + (k.usos ? ' · ya lo usaron ' + k.usos + ': si cambias la duración, cambia también su tiempo.' : '') + '</p>' +
        '<label>Duración <select class="ac-campo" name="duracion">' + ops + '</select></label>' +
        '<label>Personas por código <input class="ac-campo" name="usos" type="number" min="' + Math.max(1, k.usos) + '" max="10000" value="' + k.usos_max + '" required></label>' +
        '<label>Canjear antes del <input class="ac-campo" name="antes" type="date" value="' + fechaCampo(k.canjear_antes) + '"></label>' +
        '<label class="ac-ancho">Nota <input class="ac-campo" name="nota" type="text" maxlength="120" value="' + esc(k.nota || '') + '"></label>' +
        '<p class="ac-acciones ac-ancho"><button class="sz-btn sz-btn-of" type="submit">Guardar</button>' +
        boton('Cancelar', 'data-cancelar="1"') + '</p></form></td></tr>';
    }
    // Renovar (18-11-2026): devuelve la vida al código y, si quieres, más tiempo a quien ya lo canjeó.
    var renovando = null;
    function renovador(k) {
      var ops = '<option value="">Sin tiempo extra</option>' + Object.keys(DUR).map(function (d) { return '<option value="' + d + '"' + (d === k.duracion ? ' selected' : '') + '>' + DUR[d] + '</option>'; }).join('');
      var antes = k.canjear_antes && Date.parse(k.canjear_antes) <= Date.now();
      return '<tr class="ac-editor"><td colspan="6"><form class="ac-fila" data-renovar="' + k.id + '">' +
        '<p class="ac-ancho"><b>Renovar ' + esc(bonito(k.codigo)) + '</b>' + (k.revocado ? ' · está revocado: al renovarlo vuelve a abrir.' : '') +
        (k.archivado ? ' · vuelve a Activos.' : '') + (antes ? ' · su fecha para canjear ya pasó: si no pones otra, queda sin fecha.' : '') + '</p>' +
        '<label>Tiempo extra para quien ya lo canjeó (' + k.usos + ') <select class="ac-campo" name="lapso">' + ops + '</select></label>' +
        '<label>Personas de más <input class="ac-campo" name="mas" type="number" min="0" max="10000" value="' + (k.usos >= k.usos_max ? 1 : 0) + '"></label>' +
        '<label>Nueva fecha para canjear <input class="ac-campo" name="antes" type="date"></label>' +
        '<p class="ac-ayuda ac-ancho">El tiempo extra se suma al final de lo que le quede a cada persona, o desde hoy si ya se le había acabado. Queda anotado en la Bitácora.</p>' +
        '<p class="ac-acciones ac-ancho"><button class="sz-btn sz-btn-of" type="submit">Renovar</button>' +
        boton('Cancelar', 'data-cancelar="1"') + '</p></form></td></tr>';
    }
    function pinta() {
      var cuenta = {}, act = 0, arc = 0;
      lista.forEach(function (k) {
        if (k.archivado) { arc++; return; }
        act++; cuenta[k.estado] = (cuenta[k.estado] || 0) + 1;
      });
      $('acResumen').innerHTML = Object.keys(EST).map(function (e) {
        return '<span class="ac-chip ac-' + e + '">' + EST[e] + ': <b>' + (cuenta[e] || 0) + '</b></span>';
      }).join(' ');
      $('acNAct').textContent = act; $('acNArc').textContent = arc;
      raiz.querySelectorAll('[data-vista]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.vista === vista)); });
      var q = limpiaBusca($('acBusca').value), qc = q.replace(/[^0-9A-Z]/g, '');
      var ver = lista.filter(function (k) {
        if (!!k.archivado !== (vista === 'archivados')) return false;
        return !q || (qc && k.codigo.indexOf(qc) >= 0) || limpiaBusca(k.nota).indexOf(q) >= 0;
      });
      $('acTabla').querySelector('tbody').innerHTML = ver.map(function (k) {
        var est = EST[k.estado] + (k.estado === 'en_uso' && k.hasta ? ' hasta el ' + fecha(k.hasta) : '') +
          (k.estado === 'sin_usar' && k.canjear_antes ? ' (canjear antes del ' + fecha(k.canjear_antes) + ')' : '');
        var acc = k.semanal ? boton('Uso' + (k.usos ? ' (' + k.usos + ')' : ''), 'data-accion="uso" data-id="' + k.id + '"') + '<span class="ac-ayuda">Código de la semana: se cambia arriba.</span>'
          : boton('Uso' + (k.usos ? ' (' + k.usos + ')' : ''), 'data-accion="uso" data-id="' + k.id + '"') +
            boton('Editar', 'data-accion="editar" data-id="' + k.id + '"') +
            boton('Renovar', 'data-accion="renovar" data-id="' + k.id + '"', k.estado === 'en_uso' || k.estado === 'sin_usar' ? 'ac-claro' : 'sz-btn-of') +
            boton(k.revocado ? 'Devolver' : 'Revocar', 'data-accion="revocar" data-id="' + k.id + '" data-revocar="' + (k.revocado ? '0' : '1') + '"') +
            boton(k.archivado ? 'Desarchivar' : 'Archivar', 'data-accion="archivar" data-id="' + k.id + '" data-archivar="' + (k.archivado ? '0' : '1') + '"') +
            boton('Eliminar', 'data-accion="eliminar" data-id="' + k.id + '"', 'ac-peligro');
        return '<tr' + (k.semanal ? ' class="ac-fila-semana"' : '') + '><td><button class="ac-cod" type="button" data-copia="' + esc(bonito(k.codigo)) + '" title="Copiar">' + esc(bonito(k.codigo)) + '</button></td>' +
          '<td>' + esc(duracion(k.duracion)) + '</td><td>' + k.usos + ' de ' + k.usos_max + '</td>' +
          '<td><span class="ac-chip ac-' + k.estado + '">' + esc(est) + '</span></td><td>' + esc(k.nota || '') + '</td>' +
          '<td><div class="ac-acciones">' + acc + '</div></td></tr>' + (editando === k.id ? editor(k) : '') + (renovando === k.id ? renovador(k) : '') + registro(k);
      }).join('') || '<tr><td colspan="6">' + (q ? 'Ningún código coincide con la búsqueda.' : vista === 'archivados' ? 'No hay códigos archivados.' : 'Todavía no hay códigos.') + '</td></tr>';
    }
    function limpiaBusca(t) { return String(t || '').toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim(); }
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
        rpc('codigos_lista').then(function (j) { lista = j || []; pinta(); estados(); }),
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
    // El código de la administración (pedido del autor, 30-10-2026): solo
    // suyo, cambia cada lunes y abre la plataforma hasta ese lunes.
    var sem = null;
    function semana(cambiar) {
      return rpc('codigo_admin_semana', { p_cambiar: !!cambiar }).then(function (j) {
        sem = j;
        var b = $('acSemCod'); b.textContent = bonito(j.codigo); b.dataset.copia = bonito(j.codigo);
        $('acSemVence').innerHTML = 'Es solo tuyo y cambia solo el <b>' + esc(fecha(j.hasta)) + '</b> (hora de tu dispositivo). ' +
          'Cuando cambie, tu acceso termina y la entrada te manda aquí por el nuevo.';
      });
    }
    $('acSemCod').addEventListener('click', function () {
      var b = $('acSemCod'); if (!b.dataset.copia || !navigator.clipboard) return;
      navigator.clipboard.writeText(b.dataset.copia).then(function () { b.classList.add('ac-copiado'); setTimeout(function () { b.classList.remove('ac-copiado'); }, 1200); });
    });
    $('acSemCambiar').addEventListener('click', function () {
      if (!confirm('¿Cambiar tu código ahora? El actual deja de abrir en todos tus dispositivos.')) return;
      var p = A.leer(); if (p && p.admin) A.guardar(null);
      semana(true).then(carga).catch(function () { alert('No se pudo cambiar. Intenta de nuevo.'); });
    });
    // El pase de este navegador con el código de la semana (para el candado).
    function paseAdmin() {
      var p = A.leer();
      if (p && p.admin && A.vigente(p)) return Promise.resolve();
      return (sem ? Promise.resolve(sem) : semana()).then(function (k) { return A.pide({ accion: 'canjear', codigo: k.codigo, pase: p && p.pase }); })
        .then(function (j) {
          if (j && j.motivo === 'ya_canjeado' && j.hasta && Date.parse(j.hasta) > Date.now()) j.ok = true;
          if (!j || !j.ok) throw j;
          A.guardar({ pase: j.pase, hasta: j.hasta, visto: Date.now(), admin: true });
        });
    }
    $('acComoAdmin').addEventListener('click', function () {
      var est = $('acComoAdminEstado');
      est.textContent = 'Preparando tu acceso…';
      paseAdmin().then(function () { location.href = 'index.html'; })
        .catch(function () { est.textContent = 'No se pudo preparar tu acceso. Intenta de nuevo.'; });
    });

    // El código maestro (pedido del autor, 30-10-2026): con él, la entrada te
    // reconoce sin correo. No cambia solo: lo cambias aquí cuando quieras.
    function maestroInfo() {
      return rpc('codigo_admin_info').then(function (j) {
        $('acMaeEstado').innerHTML = j.puesto
          ? 'Ya tienes código maestro. Lo cambiaste el <b>' + esc(fecha(j.cambiado)) + '</b>.'
          : 'Aún no pones tu código maestro: mientras, entras con tu correo.';
        var e = j.entradas || [];
        $('acMaeEntradas').innerHTML = e.length
          ? 'Últimas entradas con él: ' + e.map(function (x) { return esc(fecha(x)); }).join(' · ') + '. Si ves una que no fue tuya, cámbialo.'
          : '';
      });
    }
    $('acMaestro').addEventListener('submit', function (e) {
      e.preventDefault();
      var f = $('acMaestro'), est = $('acMaeGuardar'), a = limpia(f.nuevo.value), b = limpia(f.otra.value);
      if (a.length !== 8 || f.nuevo.value.replace(/[\s-]/g, '').length !== 8) { est.textContent = 'Son 8 caracteres: números y letras de la A a la Z.'; return; }
      if (a !== b) { est.textContent = 'Los dos no coinciden: escríbelo igual en las dos casillas.'; return; }
      est.textContent = 'Guardando…';
      rpc('fijar_codigo_admin', { p_codigo: a }).then(function () {
        f.reset(); est.textContent = 'Listo: desde ahora la entrada te reconoce con ese código. El anterior ya no abre.';
        return maestroInfo();
      }).catch(function (x) { est.textContent = (x && x.message) ? 'No se guardó: ' + x.message + '.' : 'No se pudo guardar. Intenta de nuevo.'; });
    });

    // ---------------------------------------------------------------------
    // Las pestañas del panel (18-11-2026). La elegida se recuerda en la pestaña
    // del navegador y en la dirección (#tablero, #codigos…).
    var HOJAS = ['tablero', 'codigos', 'solicitudes', 'bitacora', 'acceso'], cargado = {};
    function hoja(id, foco) {
      if (HOJAS.indexOf(id) < 0) id = 'tablero';
      raiz.querySelectorAll('[data-hoja]').forEach(function (b) {
        var si = b.dataset.hoja === id;
        b.setAttribute('aria-selected', String(si)); b.tabIndex = si ? 0 : -1;
        $('ac-hoja-' + b.dataset.hoja).hidden = !si;
        if (si && foco) b.focus();
      });
      try { sessionStorage.setItem('av-admin-hoja', id); } catch (e) {}
      if (location.hash.slice(1) !== id) history.replaceState(null, '', '#' + id);
      if (s && !admin.hidden) { if (id === 'tablero' && !cargado.tablero) tablero(); if (id === 'bitacora' && !cargado.bitacora) bitacora(); }
    }
    raiz.querySelectorAll('[data-hoja]').forEach(function (b, i, todas) {
      b.addEventListener('click', function () { hoja(b.dataset.hoja); });
      b.addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0; if (!d) return;
        e.preventDefault(); hoja(todas[(i + d + todas.length) % todas.length].dataset.hoja, true);
      });
    });
    function hojaInicial() {
      var h0 = location.hash.slice(1); if (HOJAS.indexOf(h0) >= 0) return h0;
      try { return sessionStorage.getItem('av-admin-hoja') || 'tablero'; } catch (e) { return 'tablero'; }
    }

    // ---------------------------------------------------------------------
    // El tablero de uso: lo cuenta la base (uso_tablero) y aquí se dibuja.
    function num(n) { return (+n || 0).toLocaleString('es-MX'); }
    var periodo = 30, tab = null;
    function barras(filas, et, val, extra, vacio) {
      if (!filas || !filas.length) return '<p class="ac-ayuda">' + (vacio || 'Todavía no hay datos en este periodo.') + '</p>';
      var max = Math.max.apply(null, filas.map(function (f) { return +f[val] || 0; })) || 1;
      return '<ol class="ac-barras">' + filas.map(function (f) {
        var v = +f[val] || 0;
        return '<li><span class="ac-barra-et" title="' + esc(et(f)) + '">' + esc(et(f)) + '</span>' +
          '<span class="ac-barra-pista" aria-hidden="true"><i style="width:' + Math.max(1, Math.round(v / max * 100)) + '%"></i></span>' +
          '<b>' + num(v) + '</b>' + (extra ? '<small>' + esc(extra(f)) + '</small>' : '') + '</li>';
      }).join('') + '</ol>';
    }
    function columnas(filas, val, etiqueta, titulo, resumen) {
      if (!filas || !filas.length) return '<p class="ac-ayuda">Todavía no hay datos en este periodo.</p>';
      var n = filas.length, max = Math.max.apply(null, filas.map(function (f) { return +f[val] || 0; })) || 1;
      var w = 100 / n, h = 120;
      var rects = filas.map(function (f, i) {
        var v = +f[val] || 0, alto = v ? Math.max(1.5, v / max * (h - 6)) : 0;
        return '<rect x="' + (i * w + w * 0.12).toFixed(2) + '" y="' + (h - alto).toFixed(2) + '" width="' + (w * 0.76).toFixed(2) + '" height="' + alto.toFixed(2) + '">' +
          '<title>' + esc(titulo(f)) + '</title></rect>';
      }).join('');
      return '<svg class="ac-cols" viewBox="0 0 100 ' + h + '" preserveAspectRatio="none" role="img" aria-label="' + esc(resumen) + '">' +
        '<line x1="0" y1="' + h + '" x2="100" y2="' + h + '"></line>' + rects + '</svg>' +
        '<p class="ac-cols-eje"><span>' + esc(etiqueta(filas[0])) + '</span><span>Máximo: ' + num(max) + '</span><span>' + esc(etiqueta(filas[n - 1])) + '</span></p>';
    }
    function diaCorto(d) { return new Date(d + 'T12:00:00').toLocaleDateString('es-MX', { day: 'numeric', month: 'short' }); }
    function graf(id, html) { var g = $('acG-' + id); if (g) g.querySelector('.ac-graf-cuerpo').innerHTML = html; }
    var MODO_N = { inspector: 'Inspector', periodista: 'Periodista', ciudadano: 'Ciudadano', ambientalista: 'Ambientalista', 'sin modo': 'Sin modo' };
    function pintaTablero() {
      var t = tab; if (!t) return;
      var r = t.resumen || {}, ses = +r.sesiones || 0;
      var kp = [
        ['Personas', r.personas, 'navegadores con pase distintos'],
        ['Visitas', ses, 'sesiones (una por pestaña abierta)'],
        ['Páginas vistas', r.vistas, ses ? 'unas ' + (r.vistas / ses).toFixed(1) + ' por visita (auditada)' : ''],
        ['Minutos de uso', r.minutos, ses ? 'unos ' + (r.minutos / ses).toFixed(1) + ' por visita (auditada)' : 'con la página a la vista'],
        ['Clics', r.clics, 'ligas, botones y pestañas'],
        ['Preguntas al Auditor', r.preguntas, 'solo el modo y a dónde llevó'],
        ['Sin respuesta', t.sin_respuesta, 'preguntas que el chat no supo contestar'],
        ['Canjes', t.canjes, 'códigos canjeados en el periodo']
      ];
      $('acKpis').innerHTML = kp.map(function (k) {
        return '<div class="ac-kpi"><span>' + esc(k[0]) + '</span><b>' + num(k[1]) + '</b><small>' + esc(k[2]) + '</small></div>';
      }).join('');
      // Lo que conviene mirar: tres lecturas de las mismas cifras, sin calificar.
      var mir = [], sec = (t.secciones || []).filter(function (x) { return x.minutos > 0; });
      if (sec.length) mir.push('El tema con más tiempo es <b>' + esc(sec[0].seccion) + '</b>: ' + num(sec[0].minutos) + ' minutos' + (sec[1] ? '; le sigue ' + esc(sec[1].seccion) + ' con ' + num(sec[1].minutos) + '.' : '.'));
      var rapidas = (t.paginas || []).filter(function (p) { return p.vistas >= 10 && p.minutos / p.vistas < 0.25; });
      if (rapidas.length) mir.push('Se abren mucho y se dejan rápido (menos de 15 segundos por vista): ' + rapidas.slice(0, 3).map(function (p) { return '<a href="' + esc(p.pagina) + '">' + esc(p.pagina) + '</a>'; }).join(', ') + '. Conviene revisar si su entrada contesta lo que se busca.');
      if (+t.sin_respuesta) mir.push(num(t.sin_respuesta) + ' preguntas al chat se quedaron sin respuesta en el periodo: son las fichas que faltan en la base (tabla <code>preguntas_bot</code> de Supabase).');
      var hz = (t.horas || []).slice().sort(function (a, b) { return b.vistas - a.vistas; })[0];
      if (hz && hz.vistas) mir.push('La hora con más visitas es de las ' + hz.hora + ':00 a las ' + hz.hora + ':59.');
      $('acMirar').hidden = !mir.length;
      $('acMirar').innerHTML = '<b>Lo que conviene mirar</b><ul>' + mir.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>';
      graf('dia', columnas(t.por_dia, 'vistas', function (f) { return diaCorto(f.dia); },
        function (f) { return diaCorto(f.dia) + ': ' + num(f.vistas) + ' páginas, ' + num(f.personas) + ' personas, ' + num(f.minutos) + ' min'; },
        'Páginas vistas por día, del ' + diaCorto(t.desde) + ' a hoy'));
      graf('secciones', barras(t.secciones, function (f) { return f.seccion; }, 'minutos', function (f) { return num(f.vistas) + ' vistas'; }));
      graf('paginas', barras(t.paginas, function (f) { return f.pagina; }, 'vistas', function (f) { return num(f.minutos) + ' min · ' + f.seccion; }));
      graf('clics', barras(t.clics, function (f) { return f.destino.charAt(0) === '[' ? (f.etiqueta || f.destino) + ' (botón)' : f.etiqueta ? f.etiqueta + ' → ' + f.destino : f.destino; }, 'n'));
      graf('chat', barras(t.modos, function (f) { return MODO_N[f.modo] || f.modo; }, 'n', null, 'Nadie le ha preguntado al Auditor en este periodo.') +
        (t.destinos_chat && t.destinos_chat.length ? '<p class="ac-ayuda">A dónde llevaron las respuestas:</p>' + barras(t.destinos_chat, function (f) { return f.destino; }, 'n') : ''));
      graf('horas', columnas(t.horas, 'vistas', function (f) { return f.hora + ':00'; }, function (f) { return f.hora + ':00 a ' + f.hora + ':59: ' + num(f.vistas) + ' páginas'; },
        'Páginas vistas por hora del día'));
      graf('codigos', barras(t.codigos, function (f) { return bonito(f.codigo) + (f.nota ? ' · ' + f.nota : ''); }, 'minutos',
        function (f) { return num(f.personas) + (f.personas == 1 ? ' persona · ' : ' personas · ') + num(f.vistas) + ' vistas'; }, 'Ningún código con uso medido en este periodo.'));
      estados();
    }
    function estados() {
      var cuenta = {};
      lista.forEach(function (k) { if (!k.archivado && !k.semanal) cuenta[k.estado] = (cuenta[k.estado] || 0) + 1; });
      graf('estados', barras(Object.keys(EST).map(function (e) { return { e: EST[e], n: cuenta[e] || 0 }; }).filter(function (x) { return x.n; }),
        function (f) { return f.e; }, 'n', null, 'Todavía no hay códigos.'));
    }
    function tablero() {
      cargado.tablero = true;
      $('acTabEstado').textContent = 'Cargando el tablero…';
      return rpc('uso_tablero', { p_dias: periodo }).then(function (j) {
        tab = j; $('acTabEstado').textContent = 'Del ' + diaCorto(j.desde) + ' a hoy (' + j.dias + ' días).'; pintaTablero();
      }).catch(function (e) {
        cargado.tablero = false;
        $('acTabEstado').textContent = 'No se pudo cargar el tablero' + (e && e.message ? ': ' + e.message : '') + '. Si es la primera vez, falta subir la migración del control interno.';
      });
    }
    raiz.querySelectorAll('[data-periodo]').forEach(function (b) {
      b.addEventListener('click', function () {
        periodo = +b.dataset.periodo;
        raiz.querySelectorAll('[data-periodo]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        tablero();
      });
    });
    $('acTabRecargar').addEventListener('click', tablero);
    $('acTabCsv').addEventListener('click', function () {
      if (!tab) return;
      var f = [['parte', 'concepto', 'valor', 'detalle']], r = tab.resumen || {};
      Object.keys(r).forEach(function (k) { f.push(['resumen', k, r[k], '']); });
      f.push(['resumen', 'canjes', tab.canjes, ''], ['resumen', 'sin_respuesta', tab.sin_respuesta, '']);
      (tab.por_dia || []).forEach(function (x) { f.push(['por_dia', x.dia, x.vistas, 'personas ' + x.personas + ' · sesiones ' + x.sesiones + ' · minutos ' + x.minutos]); });
      (tab.secciones || []).forEach(function (x) { f.push(['tema', x.seccion, x.minutos, 'minutos · ' + x.vistas + ' vistas']); });
      (tab.paginas || []).forEach(function (x) { f.push(['pagina', x.pagina, x.vistas, 'vistas · ' + x.minutos + ' min']); });
      (tab.clics || []).forEach(function (x) { f.push(['clic', x.destino, x.n, x.etiqueta || '']); });
      (tab.modos || []).forEach(function (x) { f.push(['chat_modo', x.modo, x.n, '']); });
      (tab.destinos_chat || []).forEach(function (x) { f.push(['chat_destino', x.destino, x.n, '']); });
      (tab.horas || []).forEach(function (x) { f.push(['hora', x.hora, x.vistas, 'vistas']); });
      (tab.codigos || []).forEach(function (x) { f.push(['codigo', bonito(x.codigo), x.minutos, 'minutos · ' + x.personas + ' personas · ' + x.vistas + ' vistas']); });
      bajaCsv('tablero-de-uso-' + tab.dias + '-dias.csv', f);
    });

    // ---------------------------------------------------------------------
    // La bitácora: lo anota la base sola; aquí solo se lee, filtra y baja.
    var bit = [];
    var CAMPO = { duracion: 'duración', personas: 'personas', canjear_antes: 'canjear antes del', nota: 'nota', tiempo_extra: 'tiempo extra',
      personas_con_mas_tiempo: 'personas con más tiempo', personas_mas: 'personas de más', estaba: 'estaba', lo_habian_usado: 'lo habían usado', codigo: 'código' };
    function valor(k, v) {
      if (v == null || v === '') return '—';
      if (/^\d{4}-\d{2}-\d{2}T/.test(String(v))) return fecha(v);
      if (k === 'duracion' || k === 'tiempo_extra') return duracion(String(v));
      if (k === 'codigo') return bonito(String(v));
      return String(v);
    }
    function detalle(d) {
      return Object.keys(d || {}).map(function (k) {
        var v = d[k];
        return esc(CAMPO[k] || k) + ': ' + (Array.isArray(v) ? esc(valor(k, v[0])) + ' → <b>' + esc(valor(k, v[1])) + '</b>' : '<b>' + esc(valor(k, v)) + '</b>');
      }).join(' · ');
    }
    function objeto(o) { return o && /^[0-9A-Z]{8}$/.test(o) ? bonito(o) : (o || ''); }
    function pintaBit() {
      var que = $('acBitQue').value, q = limpiaBusca($('acBitBusca').value);
      var ver = bit.filter(function (x) {
        if (que && x.accion !== que) return false;
        return !q || limpiaBusca([x.quien, x.accion, x.objeto, JSON.stringify(x.detalle)].join(' ')).indexOf(q) >= 0;
      });
      $('acBit').querySelector('tbody').innerHTML = ver.map(function (x) {
        return '<tr><td>' + esc(fecha(x.en)) + '</td><td>' + esc(x.quien) + '</td><td><span class="ac-chip">' + esc(x.accion) + '</span></td>' +
          '<td>' + esc(objeto(x.objeto)) + '</td><td>' + detalle(x.detalle) + '</td></tr>';
      }).join('') || '<tr><td colspan="5">' + (bit.length ? 'Nada coincide con el filtro.' : 'Todavía no hay movimientos anotados.') + '</td></tr>';
    }
    function bitacora() {
      cargado.bitacora = true;
      return rpc('bitacora_lista', { p_limite: 2000 }).then(function (j) {
        bit = j || [];
        var cuenta = {};
        bit.forEach(function (x) { cuenta[x.accion] = (cuenta[x.accion] || 0) + 1; });
        var sel = $('acBitQue'), elegido = sel.value;
        sel.innerHTML = '<option value="">Todo (' + bit.length + ')</option>' + Object.keys(cuenta).sort().map(function (a) {
          return '<option value="' + esc(a) + '"' + (a === elegido ? ' selected' : '') + '>' + esc(a) + ' (' + cuenta[a] + ')</option>';
        }).join('');
        var hoy = bit.filter(function (x) { return Date.now() - Date.parse(x.en) < 864e5 * 7; }).length;
        $('acBitResumen').innerHTML = '<span class="ac-chip">Movimientos: <b>' + bit.length + '</b></span> <span class="ac-chip">En los últimos 7 días: <b>' + hoy + '</b></span>';
        pintaBit();
      }).catch(function (e) {
        cargado.bitacora = false;
        $('acBit').querySelector('tbody').innerHTML = '<tr><td colspan="5">No se pudo leer la bitácora' + (e && e.message ? ': ' + esc(e.message) : '') + '.</td></tr>';
      });
    }
    $('acBitQue').addEventListener('change', pintaBit);
    $('acBitBusca').addEventListener('input', pintaBit);
    $('acBitCsv').addEventListener('click', function () {
      bajaCsv('bitacora-auditavision.csv', [['cuando', 'quien', 'accion', 'sobre', 'detalle']].concat(bit.map(function (x) {
        return [x.en, x.quien, x.accion, objeto(x.objeto), JSON.stringify(x.detalle || {})];
      })));
    });
    /* El doble factor (19-11-2026, LFPDPPP art. 18). La sesión del correo o del
       código maestro es de un paso (aal1); la base solo reconoce a la
       administración con la de dos (aal2: es_admin() de la migración
       20261119000001_doble_factor.sql). Aquí se da de alta la aplicación de
       autenticación la primera vez, o se pide su código de seis números. */
    function nivel(t) {
      try {
        var p = t.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
        return JSON.parse(atob(p + '==='.slice((p.length + 3) % 4))).aal || 'aal1';
      } catch (e) { return 'aal1'; }
    }
    function segundoPaso(t) {
      return auth('/auth/v1/user', null, t, 'GET').then(function (u) {
        s.correo = u.email; pon(s);
        var fs = (u.factors || []).filter(function (f) { return f.factor_type === 'totp'; });
        var listo = fs.filter(function (f) { return f.status === 'verified'; })[0];
        // Un alta que se quedó a medias se borra para empezar limpio.
        var sueltos = listo ? [] : fs.filter(function (f) { return f.status !== 'verified'; });
        return Promise.all(sueltos.map(function (f) { return auth('/auth/v1/factors/' + f.id, null, t, 'DELETE').catch(function () {}); }))
          .then(function () {
            if (listo) return listo;
            return auth('/auth/v1/factors', { factor_type: 'totp', friendly_name: 'Panel Auditavisión ' + Date.now() }, t)
              .catch(function () { throw { message: 'factor' }; });
          });
      }).then(function (f) {
        var caja = $('acFactor'), est = $('acFactorEstado'), cod = $('acFactorCodigo');
        entrar.hidden = true; caja.hidden = false;
        $('acFactorAlta').hidden = !f.totp;
        if (f.totp) {
          // Supabase manda el QR como SVG sin codificar («data:image/svg+xml;utf-8,<svg…>»):
          // un «#» o un salto de línea lo rompen y la imagen sale vacía. Se vuelve a codificar.
          var qr = String(f.totp.qr_code || ''), coma = qr.indexOf(','), img = $('acFactorQr');
          if (/^data:image\/svg\+xml/.test(qr) && !/;base64,/.test(qr.slice(0, coma + 1))) {
            var svg = qr.slice(coma + 1);
            try { if (/%3C/i.test(svg.slice(0, 12))) svg = decodeURIComponent(svg); } catch (e) { /* ya venía en claro */ }
            qr = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
          } else if (/^\s*<svg|^\s*<\?xml/.test(qr)) {
            qr = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(qr);
          }
          img.onerror = function () { est.textContent = 'Tu navegador no pudo dibujar el código QR: usa la clave de abajo o el botón «Ábrelo en tu aplicación».'; };
          img.src = qr;
          $('acFactorSecreto').textContent = f.totp.secret;
          var abrir = $('acFactorUri');
          if (abrir && f.totp.uri) { abrir.href = f.totp.uri; abrir.hidden = false; }
        }
        cod.focus();
        return new Promise(function (ok) {
          caja.onsubmit = function (e) {
            e.preventDefault();
            var n = cod.value.replace(/\D/g, '');
            if (n.length !== 6) { est.textContent = 'Escribe los seis números que te da tu aplicación.'; return; }
            est.textContent = 'Revisando…';
            auth('/auth/v1/factors/' + f.id + '/challenge', {}, t).then(function (ch) {
              return auth('/auth/v1/factors/' + f.id + '/verify', { challenge_id: ch.id, code: n }, t);
            }).then(function (j) {
              pon({ token: j.access_token, refresh: j.refresh_token, vence: Date.now() + j.expires_in * 1000, correo: s.correo });
              caja.hidden = true; est.textContent = ''; cod.value = '';
              ok(j.access_token);
            }).catch(function () { est.textContent = 'El código no coincide o ya cambió: escribe el que se ve ahora.'; cod.select(); });
          };
        });
      });
    }
    function abre() {
      token().then(function (t) { return nivel(t) === 'aal2' ? t : segundoPaso(t); })
        .then(function (t) { return auth('/auth/v1/user', null, t, 'GET'); }).then(function (u) {
        s.correo = u.email; pon(s);
        $('acQuien').textContent = 'Entraste como ' + u.email + '.';
        return Promise.all([carga(), semana(), maestroInfo()]);
      }).then(function () {
        entrar.hidden = true; admin.hidden = false;
        hoja(hojaInicial());
        if (/[?&]maestro=1/.test(location.search)) {
          history.replaceState(null, '', location.pathname);
          $('acQuien').textContent += ' Te reconocimos con tu código maestro.';
        }
        // Entraste a tu panel (con el correo o con el código maestro): este
        // navegador queda como de la administración y sale la pestaña.
        paseAdmin().then(function () { if (A.pestana) A.pestana(); }).catch(function () {});
      })
        .catch(function (e) {
          var no = e && /administraci/.test(e.message || ''), fa = e && e.message === 'factor';
          entrar.hidden = false; $('acFactor').hidden = true;
          $('acEntrarEstado').textContent = fa ? 'No se pudo dar de alta el segundo factor: revisa que la autenticación de dos pasos (TOTP) esté encendida en Supabase.'
            : no ? 'Esta cuenta no está dada de alta en la administración.' : 'Tu sesión venció: vuelve a pedir el enlace.';
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
      var propio = g.propio.value.trim();
      est.textContent = 'Generando…';
      // Con código propio se crea solo ese (crear_codigo); sin él, salen al azar.
      var pide = propio
        ? rpc('crear_codigo', { p_codigo: propio, p_duracion: dur, p_usos: +g.usos.value || 1, p_antes: antes, p_nota: g.nota.value || null })
            .then(function (k) { g.propio.value = ''; return 'Listo: el código ' + bonito(k.codigo) + ' de ' + duracion(dur) + ' está arriba de la lista.'; })
        : rpc('generar_codigos', { p_cantidad: +g.cantidad.value, p_duracion: dur, p_usos: +g.usos.value || 1, p_antes: antes, p_nota: g.nota.value || null })
            .then(function (nuevos) { return 'Listo: ' + nuevos.length + ' códigos nuevos de ' + duracion(dur) + '. Están arriba de la lista.'; });
      pide.then(function (msj) {
          est.textContent = msj;
          return carga();
        }).catch(function (e2) { est.textContent = 'No se pudieron generar: ' + ((e2 && e2.message) || 'intenta de nuevo') + '.'; });
    });
    $('acRecargar').addEventListener('click', function () { carga(); });
    function falla(e2) { $('acTablaEstado').textContent = 'No se pudo: ' + ((e2 && e2.message) || 'intenta de nuevo') + '.'; }
    function hecho(txt) { return function () { $('acTablaEstado').textContent = txt; cargado.bitacora = false; return carga(); }; }
    raiz.querySelectorAll('[data-vista]').forEach(function (b) {
      b.addEventListener('click', function () { vista = b.dataset.vista; editando = null; pinta(); });
    });
    $('acBusca').addEventListener('input', function () { pinta(); });
    $('acArchInact').addEventListener('click', function () {
      if (!confirm('¿Archivar todos los códigos revocados, terminados y vencidos? No se borran: los ves en «Archivados».')) return;
      rpc('archivar_inactivos').then(function (n) { $('acTablaEstado').textContent = n ? 'Listo: ' + n + ' códigos archivados.' : 'No había códigos por archivar.'; return carga(); }).catch(falla);
    });
    $('acTabla').addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      if (b.dataset.copia) {
        navigator.clipboard && navigator.clipboard.writeText(b.dataset.copia).then(function () { b.classList.add('ac-copiado'); setTimeout(function () { b.classList.remove('ac-copiado'); }, 1200); });
        return;
      }
      if (b.dataset.cancelar) { editando = null; renovando = null; pinta(); return; }
      if (b.dataset.cerraruso) { uso = null; pinta(); return; }
      var id = +b.dataset.id, a = b.dataset.accion; if (!a) return;
      var k = lista.filter(function (x) { return x.id === id; })[0]; if (!k) return;
      var nom = bonito(k.codigo);
      if (a === 'uso') {
        if (uso && uso.id === id) { uso = null; pinta(); return; }
        uso = { id: id, filas: null }; pinta();
        rpc('codigo_uso', { p_id: id }).then(function (f) { if (uso && uso.id === id) { uso.filas = f || []; pinta(); } })
          .catch(function (e2) { uso = null; pinta(); falla(e2); });
      } else if (a === 'renovar') {
        renovando = renovando === id ? null : id; editando = null; pinta();
        var fr = $('acTabla').querySelector('[data-renovar="' + id + '"]'); if (fr) fr.lapso.focus();
      } else if (a === 'editar') {
        editando = editando === id ? null : id; renovando = null; pinta();
        var f = $('acTabla').querySelector('[data-editar="' + id + '"]'); if (f) f.duracion.focus();
      } else if (a === 'revocar') {
        var revoca = b.dataset.revocar === '1';
        if (revoca && !confirm('¿Revocar el ' + nom + '? Quien lo canjeó pierde su tiempo.')) return;
        rpc('revocar_codigo', { p_id: id, p_revocado: revoca }).then(hecho(nom + (revoca ? ' revocado.' : ' devuelto.'))).catch(falla);
      } else if (a === 'archivar') {
        var archiva = b.dataset.archivar === '1';
        rpc('archivar_codigo', { p_id: id, p_archivado: archiva }).then(hecho(nom + (archiva ? ' archivado.' : ' de vuelta en Activos.'))).catch(falla);
      } else if (a === 'eliminar') {
        if (!confirm('¿Eliminar el ' + nom + ' para siempre?' + (k.usos ? ' Ya lo usaron ' + k.usos + ' y perderán su tiempo.' : '') + ' Esto no se puede deshacer.')) return;
        rpc('eliminar_codigo', { p_id: id }).then(hecho(nom + ' eliminado.')).catch(falla);
      }
    });
    $('acTabla').addEventListener('submit', function (e) {
      var fr = e.target.closest('[data-renovar]');
      if (fr) {
        e.preventDefault();
        var rid = +fr.dataset.renovar, rk = lista.filter(function (x) { return x.id === rid; })[0];
        var nomr = rk ? bonito(rk.codigo) : 'El código';
        rpc('renovar_codigo', {
          p_id: rid, p_lapso: fr.lapso.value || null, p_usos_mas: Math.max(0, +fr.mas.value || 0),
          p_antes: fr.antes.value ? new Date(fr.antes.value + 'T23:59:59').toISOString() : null
        }).then(function (n) {
          renovando = null;
          return hecho(nomr + ' renovado' + (fr.lapso.value ? ': ' + n + (n === 1 ? ' persona recibió' : ' personas recibieron') + ' ' + duracion(fr.lapso.value).toLowerCase() + ' más.' : '.'))();
        }).catch(falla);
        return;
      }
      var f = e.target.closest('[data-editar]'); if (!f) return;
      e.preventDefault();
      var id = +f.dataset.editar, k = lista.filter(function (x) { return x.id === id; })[0];
      rpc('editar_codigo', {
        p_id: id, p_nota: f.nota.value, p_usos_max: +f.usos.value || 1, p_duracion: f.duracion.value,
        p_antes: f.antes.value ? new Date(f.antes.value + 'T23:59:59').toISOString() : null
      }).then(function () { editando = null; return hecho((k ? bonito(k.codigo) : 'El código') + ' guardado.')(); }).catch(falla);
    });
    function bajaCsv(nombre, filas) {
      var csv = filas.map(function (f) { return f.map(function (x) { return '"' + String(x == null ? '' : x).replace(/"/g, '""') + '"'; }).join(','); }).join('\r\n');
      var a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' }));
      a.download = nombre; a.click();
    }
    $('acCsv').addEventListener('click', function () {
      bajaCsv('codigos-auditavision.csv', [['codigo', 'duracion', 'usos', 'usos_max', 'estado', 'hasta', 'canjear_antes', 'nota', 'creado', 'archivado']].concat(lista.map(function (k) {
        return [bonito(k.codigo), duracion(k.duracion), k.usos, k.usos_max, EST[k.estado], k.hasta || '', k.canjear_antes || '', k.nota || '', k.creado, k.archivado ? 'sí' : 'no'];
      })));
    });
    $('acCsvUso').addEventListener('click', function () {
      rpc('codigo_uso', { p_id: null }).then(function (f) {
        bajaCsv('uso-de-codigos-auditavision.csv', [['codigo', 'persona', 'nombre', 'correo', 'canjeado', 'hasta', 'ultimo_dia', 'dias_que_entro', 'minutos_de_uso', 'paginas_vistas', 'renovado']].concat((f || []).map(function (u) {
          return [bonito(u.codigo), u.persona, u.nombre, u.correo, u.canjeado, u.hasta, u.ultimo, u.dias, u.minutos, u.vistas, u.renovado ? 'sí' : 'no'];
        })));
      }).catch(falla);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { pedir(); canje(); panel(); });
  else { pedir(); canje(); panel(); }
})();
