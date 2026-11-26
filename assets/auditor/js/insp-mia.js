/* Modo Inspector › Mi Auditavisión, el tablero (05-11-2026, herramientas/insp_mia.py).

   Todo vive en el navegador del lector: localStorage, clave «av-mia», con la
   forma { prov: [RFC...], rev: [{tipo, fecha, titulo, lineas, senales, ir}] }.
   El Lector de facturas y «Revisa tu estado de resultados» escriben ahí con
   su miaGuardar(). Si el navegador no deja guardar, la página sigue sirviendo:
   lo dice y no pierde lo que se ve en pantalla.

   El aviso del Vigía (22-11-2026, docs/BORRADOR-VIGIA-PROVEEDORES.md §8):
   «vig» guarda, solo aquí, la situación que viste de cada proveedor y el corte
   del SAT de tu última visita: { corte, st: {RFC: "F" | "P" | "F+S" | ""} }.
   Al abrir, compara con el corte de hoy y dice lo que cambió; «Ya lo vi» lo
   da por visto. El historial (D.vig, de vigia_historial.py) dice desde
   cuándo la plataforma vio cada situación. */
(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  if (!$('mia')) return;
  const D = JSON.parse($('miaDatos').textContent);
  const CLAVE = 'av-mia';
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const fisica = rfc => rfc.length === 13;
  const tapa = rfc => fisica(rfc) ? rfc.slice(0, 4) + '••••••' + rfc.slice(10) : rfc;
  const RFC_RE = /\b[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}\b/g;
  let lista = null;
  const OFI = '<span class="est-chip est-oficial">oficial</span>';

  function leerTablero() {
    try { const t = JSON.parse(localStorage.getItem(CLAVE) || '{}'); return { prov: t.prov || [], rev: t.rev || [], vig: t.vig || null }; }
    catch (e) { return { prov: [], rev: [], vig: null }; }
  }
  function guardar(t) {
    try { localStorage.setItem(CLAVE, JSON.stringify(t)); return true; }
    catch (e) { $('miaEstado').textContent = 'Tu navegador no deja guardar aquí (modo privado o datos bloqueados): lo que ves se pierde al cerrar.'; return false; }
  }

  function cargarLista() {
    if (lista) return Promise.resolve(lista);
    return new Promise((ok, mal) => {
      if (window.SAT_69B) { ok(); return; }
      const s = document.querySelector('script[src*="insp-mia.js"]');
      const v = s && s.getAttribute('src').match(/\?v=([\w.-]+)/);
      const sc = document.createElement('script');
      sc.src = 'assets/auditor/data/sat-69b.js' + (v ? '?v=' + v[1] : '');
      sc.onload = ok; sc.onerror = mal;
      document.head.appendChild(sc);
    }).then(() => {
      // El SAT repite algunos RFC con dos situaciones (un definitivo y su sentencia favorable): se guardan juntas.
      lista = new Map();
      window.SAT_69B.r.forEach(r => { const v = lista.get(r[0]); if (!v || r[2] === 'F' || r[2] === 'P') lista.set(r[0], r); });
      situ = new Map();
      window.SAT_69B.r.forEach(r => { const v = situ.get(r[0]) || []; if (v.indexOf(r[2]) < 0) v.push(r[2]); situ.set(r[0], v); });
      return lista;
    });
  }
  let situ = null;
  const estado = rfc => (situ.get(rfc) || []).slice().sort().join('+');
  const nomSit = st => st ? st.split('+').map(k => D.sit[k] ? D.sit[k].t : k).join(' y ') : 'fuera de la lista';

  // Llave del historial: la moral por su RFC; la física por la huella de su RFC (vigia_historial.llave()).
  function llave(rfc) {
    if (!fisica(rfc)) return Promise.resolve(rfc);
    if (!(window.crypto && crypto.subtle && window.TextEncoder)) return Promise.resolve(null);
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode('av-padron:' + rfc)).then(b =>
      'pf:' + Array.from(new Uint8Array(b)).map(x => x.toString(16).padStart(2, '0')).join('').slice(0, 12));
  }
  const fecha = iso => { const p = String(iso).split('-'); return p.length === 3 ? p[2] + '-' + p[1] + '-' + p[0] : iso; };
  const dias = (a, b) => Math.round((Date.parse(b) - Date.parse(a)) / 86400000);

  // Lo que el historial dice de un RFC: desde cuándo lo vimos así y, si lo vimos presunto antes que definitivo, los días de aviso.
  function historia(k, st) {
    const V = D.vig;
    if (!V || !k) return '';
    const ev = V.ev[k];
    if (!ev) return st ? 'Así desde que empezó el registro del Vigía (' + fecha(V.inicio) + '): de antes no presumimos aviso previo.' : '';
    const u = ev[ev.length - 1];
    let t = 'Visto ' + (u[2] === 'alta' ? 'por primera vez' : u[2] === 'cambio' ? 'en esta situación' : 'desde el inicio del registro') + ' el ' + fecha(u[0]) + '.';
    const p = ev.find(e => e[1].split('+').indexOf('P') >= 0 && e[2] !== 'semilla');
    const f = p && ev.find(e => e[1].split('+').indexOf('F') >= 0 && e[0] > p[0]);
    if (p && f) t += ' Aviso previo: presunto el ' + fecha(p[0]) + ', definitivo el ' + fecha(f[0]) + ': ' + dias(p[0], f[0]) + ' días (auditada: resta de las dos fechas del historial).';
    return t;
  }

  // El aviso: lo que cambió desde tu última visita. Un RFC que no tenía situación guardada (recién agregado) entra sin aviso.
  function aviso(t) {
    const caja = $('miaAviso');
    const vig = t.vig || { corte: null, st: {} };
    const cambios = [];
    let nuevos = 0;
    t.prov.forEach(rfc => {
      const ahora = estado(rfc);
      if (!(rfc in vig.st)) { vig.st[rfc] = ahora; nuevos++; return; }
      if (vig.st[rfc] !== ahora) cambios.push({ rfc: rfc, antes: vig.st[rfc], ahora: ahora });
    });
    Object.keys(vig.st).forEach(rfc => { if (t.prov.indexOf(rfc) < 0) delete vig.st[rfc]; });
    const primera = !t.vig;
    if (primera || nuevos) { if (!vig.corte) vig.corte = D.corte; t.vig = vig; guardar(t); }
    const corteNuevo = vig.corte && vig.corte !== D.corte;
    if (!t.prov.length) { caja.hidden = true; return; }
    if (!cambios.length) {
      caja.hidden = false;
      caja.className = 'mia-aviso mia-aviso-ok';
      caja.innerHTML = '<p><b>📡 Vigía de proveedores:</b> ' + (primera ? 'desde hoy comparamos tu lista con cada corte del SAT cada vez que abres este tablero.' :
        corteNuevo ? 'hay un corte nuevo del SAT (' + esc(D.corte) + '; tu visita anterior fue con el de ' + esc(vig.corte) + ') y <b>ninguno de tus proveedores cambió</b>.' :
        'sin cambios en tus proveedores desde tu última visita (corte del ' + esc(D.corte) + ').') + '</p>' +
        (corteNuevo ? '<p class="ef-busca-fila"><button type="button" class="ef-btn ef-btn-sec" id="miaVisto">✓ Ya lo vi</button></p>' : '');
      return;
    }
    const conF = cambios.some(c => c.ahora.split('+').indexOf('F') >= 0 && c.antes.split('+').indexOf('F') < 0);
    caja.hidden = false;
    caja.className = 'mia-aviso mia-aviso-alerta';
    caja.innerHTML = '<h3>📡 Aviso del Vigía: ' + (cambios.length === 1 ? '1 proveedor cambió' : cambios.length + ' proveedores cambiaron') + ' desde tu última visita</h3>' +
      '<p class="cf-nota">Comparamos la situación que viste' + (vig.corte ? ' (corte del ' + esc(vig.corte) + ')' : '') + ' con el corte del ' + esc(D.corte) + ' ' + OFI + '.</p><ul>' +
      cambios.map(c => {
        const r = lista.get(c.rfc);
        return '<li data-vig="' + esc(c.rfc) + '"><code>' + esc(tapa(c.rfc)) + '</code>' + (r && !fisica(c.rfc) ? ' ' + esc(r[1]) : '') + ': de <b>' + esc(nomSit(c.antes)) + '</b> a <b>' + esc(nomSit(c.ahora)) + '</b>' +
          (r ? '. Oficio ' + esc(r[3]) + ' del ' + esc(r[4]) + ' (' + esc(r[5] || 'DOF') + ')' : '. Ya no aparece en el corte: revisa el documento del SAT') +
          '. <span class="mia-hist"></span> <a href="herramienta-inspector-efos.html?q=' + encodeURIComponent(c.rfc) + '">Ver en la lista 69-B</a></li>';
      }).join('') + '</ul>' +
      (conF ? '<p>Cuando el SAT publica a una empresa como <b>definitiva</b>, se considera, con efectos generales, que «las operaciones contenidas en los comprobantes fiscales expedidos por el contribuyente en cuestión no producen ni produjeron efecto fiscal alguno» (CFF, art. 69-B, párrafo quinto). Quien les dio efecto fiscal cuenta con treinta días siguientes a la publicación para acreditar que sí recibió los bienes o servicios, o para corregir su situación fiscal (párrafo octavo).</p>' : '') +
      '<p class="cf-nota">Una presunción no es una condena: la empresa puede desvirtuarla. El aviso dice lo que cambió; qué hacer con tu proveedor lo decides tú.</p>' +
      '<p class="ef-busca-fila"><button type="button" class="ef-btn" id="miaVisto">✓ Ya lo vi</button></p>';
    caja.querySelectorAll('[data-vig]').forEach(li => llave(li.getAttribute('data-vig')).then(k => {
      li.querySelector('.mia-hist').textContent = historia(k, estado(li.getAttribute('data-vig')));
    }));
  }

  function visto() {
    const t = leerTablero();
    const st = {};
    t.prov.forEach(rfc => { st[rfc] = estado(rfc); });
    t.vig = { corte: D.corte, st: st };
    if (guardar(t)) $('miaEstado').textContent = '✓ Aviso visto. Te avisaremos del siguiente cambio aquí mismo.';
    aviso(t);
  }

  function pintarProv() {
    const t = leerTablero(), caja = $('miaProv');
    if (!t.prov.length) { caja.innerHTML = '<p class="cf-nota">Todavía no agregas proveedores.</p>'; return; }
    caja.innerHTML = '<p class="cf-nota">⏳ Cruzando con la lista 69-B…</p>';
    cargarLista().then(l => {
      const filas = t.prov.map(rfc => ({ rfc: rfc, r: l.get(rfc) }));
      const orden = { F: 0, P: 1, S: 2, D: 3 };
      filas.sort((a, b) => ((a.r ? orden[a.r[2]] : 9) - (b.r ? orden[b.r[2]] : 9)) || a.rfc.localeCompare(b.rfc));
      const en = filas.filter(f => f.r && (f.r[2] === 'F' || f.r[2] === 'P')).length;
      caja.innerHTML = '<p><b>' + filas.length + '</b> proveedores · <b>' + en + '</b> en la lista 69-B como definitivo o presunto.</p>' +
        '<div class="cf-tabla-caja"><table class="cf-tabla"><thead><tr><th scope="col">RFC</th><th scope="col">Lista 69-B</th><th scope="col">Revisa</th><th scope="col">Quitar</th></tr></thead><tbody>' +
        filas.map(f => {
          const s = f.r ? D.sit[f.r[2]] : null;
          return '<tr data-fila="' + esc(f.rfc) + '"><td><code>' + esc(tapa(f.rfc)) + '</code>' + (f.r && !fisica(f.rfc) ? '<br>' + esc(f.r[1]) : '') + '</td><td>' +
            (s ? '<span class="cf-badge cf-' + s.c + '">' + s.i + ' ' + esc(s.t) + '</span><br><small>Oficio ' + esc(f.r[3]) + ' del ' + esc(f.r[4]) + '</small>' : 'No aparece') + '<br><small class="mia-hist"></small>' +
            '</td><td><a href="herramienta-inspector-efos.html?q=' + encodeURIComponent(f.rfc) + '">Lista 69-B</a> · <a href="contratos-publicos.html?q=' + encodeURIComponent(f.rfc) + '">Contratos públicos</a></td>' +
            '<td><button type="button" class="ef-btn ef-btn-sec" data-quita="' + esc(f.rfc) + '">Quitar</button></td></tr>';
        }).join('') + '</tbody></table></div>' +
        '<p class="cf-nota">No aparecer no prueba que las operaciones existieron: dice que el SAT no lo ha publicado (corte al ' + esc(D.corte) + ').</p>';
      caja.querySelectorAll('tr[data-fila]').forEach(tr => llave(tr.getAttribute('data-fila')).then(k => {
        const h = historia(k, estado(tr.getAttribute('data-fila')));
        if (h) tr.querySelector('.mia-hist').textContent = h;
      }));
      aviso(t);
    }, () => { caja.innerHTML = '<p class="cf-nota">No pudimos traer la lista 69-B. Revisa tu conexión.</p>'; });
  }

  function pintarRev() {
    const t = leerTablero(), caja = $('miaRev');
    if (!t.rev.length) { caja.innerHTML = '<p class="cf-nota">Todavía no guardas revisiones.</p>'; return; }
    caja.innerHTML = t.rev.map((r, i) => '<article class="cf-fac' + (r.senales ? ' cf-fac-mal' : '') + '"><h3>' + (r.tipo === 'facturas' ? '📑' : '📊') + ' ' + esc(r.titulo) + '</h3>' +
      '<p class="cf-nota">Guardado el ' + esc(r.fecha) + ' · ' + (r.senales ? '<b>' + r.senales + (r.senales === 1 ? ' señal para revisar' : ' señales para revisar') + '</b>' : 'sin señales') + '</p>' +
      '<ul>' + (r.lineas || []).slice(0, 8).map(x => '<li>' + esc(x) + '</li>').join('') + '</ul>' +
      '<p class="ef-busca-fila"><a class="ef-btn ef-btn-sec" href="' + esc(r.ir) + '">Abrir la herramienta</a> <button type="button" class="ef-btn ef-btn-sec" data-quita-rev="' + i + '">Quitar</button></p></article>').join('');
  }

  /* El seguimiento de hallazgos (Ronda 26, 26-11-2026): localStorage «av-hallazgos», una lista de
     { id, o, t, d, u: [UUID], alta, st: 'revisar' | 'aclarado' | 'descartado', f: AAAA-MM-DD, n: nota }.
     La escribe el Lector de facturas (hallGuardar() de insp-factura.js) o el lector a mano; aquí se cambia el estado,
     la fecha y la nota. Nunca un XML; nunca sale del navegador. Hasta 200. */
  const HALL = 'av-hallazgos';
  const ESTADOS = [['revisar', 'Por revisar'], ['aclarado', 'Aclarado'], ['descartado', 'Descartado']];
  const hoy = () => new Date().toISOString().slice(0, 10);
  function leerHall() { try { const l = JSON.parse(localStorage.getItem(HALL) || '[]'); return Array.isArray(l) ? l : []; } catch (e) { return []; } }
  function guardarHall(l) {
    try { localStorage.setItem(HALL, JSON.stringify(l.slice(0, 200))); return true; }
    catch (e) { $('miaEstado').textContent = 'Tu navegador no deja guardar aquí (modo privado o datos bloqueados).'; return false; }
  }
  function pintarHall() {
    const l = leerHall(), caja = $('miaHall');
    if (!l.length) { caja.innerHTML = '<p class="cf-nota">Todavía no tienes hallazgos. Lee tus facturas en el Lector y guarda el resumen, o anota uno arriba.</p>'; return; }
    const cuenta = ESTADOS.map(e => '<b>' + l.filter(h => h.st === e[0]).length + '</b> ' + e[1].toLowerCase()).join(' · ');
    caja.innerHTML = '<p>' + cuenta + '.</p><ol class="mia-hall">' + l.map((h, i) =>
      '<li class="mia-hall-it mia-hall-' + esc(h.st) + '" data-hall="' + i + '"><p><b>' + esc(h.t) + '</b>' + (h.d ? '<br>' + esc(h.d) : '') + '</p>' +
      (h.u && h.u.length ? '<p class="cf-nota">Folios: <code>' + h.u.slice(0, 5).map(esc).join('</code>, <code>') + '</code>' + (h.u.length > 5 ? ' y ' + (h.u.length - 5) + ' más' : '') + '</p>' : '') +
      '<p class="cf-nota">' + (h.o === 'facturas' ? 'Del Lector de facturas' : 'Anotado a mano') + ' el ' + esc(fecha(h.alta)) + '.</p>' +
      '<div class="mia-hall-campos"><div><label for="miaHallSt' + i + '">Estado</label><select id="miaHallSt' + i + '" data-campo="st">' +
      ESTADOS.map(e => '<option value="' + e[0] + '"' + (h.st === e[0] ? ' selected' : '') + '>' + e[1] + '</option>').join('') + '</select></div>' +
      '<div><label for="miaHallF' + i + '">Fecha</label><input type="date" id="miaHallF' + i + '" data-campo="f" value="' + esc(h.f || '') + '"></div>' +
      '<div class="mia-hall-nota"><label for="miaHallN' + i + '">Nota breve</label><input type="text" id="miaHallN' + i + '" data-campo="n" maxlength="200" value="' + esc(h.n || '') + '" placeholder="Por ejemplo: mandó el complemento el día 12"></div></div>' +
      '<p class="ef-busca-fila"><button type="button" class="ef-btn" data-hall-guarda="' + i + '">Guardar</button> <button type="button" class="ef-btn ef-btn-sec" data-hall-quita="' + i + '">Quitar</button></p></li>').join('') + '</ol>' +
      '<p class="ef-busca-fila"><button type="button" class="ef-btn ef-btn-sec" id="miaHallBorra">Borrar todo mi seguimiento</button></p>';
  }
  $('miaHallAgregar').addEventListener('click', () => {
    const t = $('miaHallNuevo').value.trim();
    if (!t) return;
    const l = leerHall();
    l.unshift({ id: 'mano:' + Date.now(), o: 'mano', t: t.slice(0, 200), d: '', u: [], alta: hoy(), st: 'revisar', f: hoy(), n: '' });
    if (guardarHall(l)) $('miaEstado').textContent = 'Hallazgo anotado «Por revisar». Se guarda solo en este navegador.';
    $('miaHallNuevo').value = '';
    pintarHall();
  });
  $('miaHall').addEventListener('click', ev => {
    if (ev.target.closest('#miaHallBorra')) {
      try { localStorage.removeItem(HALL); } catch (e) { /* nada que borrar */ }
      $('miaEstado').textContent = 'Borrado. Tu seguimiento quedó vacío.';
      pintarHall();
      return;
    }
    const g = ev.target.closest('[data-hall-guarda]'), q = ev.target.closest('[data-hall-quita]');
    if (!g && !q) return;
    const l = leerHall(), i = parseInt((g || q).getAttribute(g ? 'data-hall-guarda' : 'data-hall-quita'), 10);
    if (!l[i]) return;
    if (q) { l.splice(i, 1); guardarHall(l); pintarHall(); return; }
    const li = g.closest('[data-hall]'), v = c => li.querySelector('[data-campo="' + c + '"]').value;
    const st = v('st');
    l[i].st = ESTADOS.some(e => e[0] === st) ? st : 'revisar';
    l[i].f = /^\d{4}-\d\d-\d\d$/.test(v('f')) ? v('f') : hoy();
    l[i].n = v('n').trim().slice(0, 200);
    if (guardarHall(l)) $('miaEstado').textContent = 'Guardado: «' + l[i].t + '» quedó ' + ESTADOS.filter(e => e[0] === l[i].st)[0][1].toLowerCase() + ' al ' + fecha(l[i].f) + '.';
    pintarHall();
  });

  $('miaAgregar').addEventListener('click', () => {
    const nuevos = ($('miaRfc').value.toUpperCase().match(RFC_RE) || []);
    if (!nuevos.length) { $('miaEstado').textContent = 'No encontramos RFC: uno de empresa tiene 12 caracteres (3 letras, 6 números de la fecha y 3 de homoclave).'; return; }
    const t = leerTablero();
    const antes = t.prov.length;
    t.prov = Array.from(new Set(t.prov.concat(nuevos))).slice(0, 500);
    if (guardar(t)) $('miaEstado').textContent = '✓ ' + (t.prov.length - antes === 1 ? '1 agregado' : (t.prov.length - antes) + ' agregados') + '. Se guarda solo en este navegador.';
    $('miaRfc').value = '';
    pintarProv();
  });
  $('mia').addEventListener('click', ev => {
    if (ev.target.closest('#miaVisto')) { visto(); return; }
    const q = ev.target.closest('[data-quita]'), qr = ev.target.closest('[data-quita-rev]');
    if (!q && !qr) return;
    const t = leerTablero();
    if (q) t.prov = t.prov.filter(x => x !== q.getAttribute('data-quita'));
    else t.rev.splice(parseInt(qr.getAttribute('data-quita-rev'), 10), 1);
    guardar(t);
    q ? pintarProv() : pintarRev();
  });
  $('miaBorrar').addEventListener('click', () => {
    try { localStorage.removeItem(CLAVE); } catch (e) { /* nada que borrar */ }
    $('miaEstado').textContent = 'Borrado. Tu tablero quedó vacío (tu seguimiento de hallazgos se borra con su propio botón).';
    pintarProv(); pintarRev();
  });
  pintarProv();
  pintarRev();
  pintarHall();
})();
