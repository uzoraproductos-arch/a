/* Modo Inspector › Mi Auditavisión, el tablero (05-11-2026, herramientas/insp_mia.py).

   Todo vive en el navegador del lector: localStorage, clave «av-mia», con la
   forma { prov: [RFC...], rev: [{tipo, fecha, titulo, lineas, senales, ir}] }.
   El Lector de facturas y «Revisa tu estado de resultados» escriben ahí con
   su miaGuardar(). Si el navegador no deja guardar, la página sigue sirviendo:
   lo dice y no pierde lo que se ve en pantalla. */
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

  function leerTablero() {
    try { const t = JSON.parse(localStorage.getItem(CLAVE) || '{}'); return { prov: t.prov || [], rev: t.rev || [] }; }
    catch (e) { return { prov: [], rev: [] }; }
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
    }).then(() => { lista = new Map(window.SAT_69B.r.map(r => [r[0], r])); return lista; });
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
          return '<tr><td><code>' + esc(tapa(f.rfc)) + '</code>' + (f.r && !fisica(f.rfc) ? '<br>' + esc(f.r[1]) : '') + '</td><td>' +
            (s ? '<span class="cf-badge cf-' + s.c + '">' + s.i + ' ' + esc(s.t) + '</span><br><small>Oficio ' + esc(f.r[3]) + ' del ' + esc(f.r[4]) + '</small>' : 'No aparece') +
            '</td><td><a href="herramienta-inspector-efos.html?q=' + encodeURIComponent(f.rfc) + '">Lista 69-B</a> · <a href="contratos-publicos.html?q=' + encodeURIComponent(f.rfc) + '">Contratos públicos</a></td>' +
            '<td><button type="button" class="ef-btn ef-btn-sec" data-quita="' + esc(f.rfc) + '">Quitar</button></td></tr>';
        }).join('') + '</tbody></table></div>' +
        '<p class="cf-nota">No aparecer no prueba que las operaciones existieron: dice que el SAT no lo ha publicado (corte al ' + esc(D.corte) + ').</p>';
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
    $('miaEstado').textContent = 'Borrado. Tu tablero quedó vacío.';
    pintarProv(); pintarRev();
  });
  pintarProv();
  pintarRev();
})();
