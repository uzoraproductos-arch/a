/* Auditavisión · Modo Inspector › Lista negra del SAT (12-10-2026).
   La página la escribe herramientas/insp_efos.py. Este archivo descarga la
   lista oficial (assets/auditor/data/sat-69b.js → window.SAT_69B) en
   segundo plano y busca por RFC o por nombre, uno o varios a la vez.
   No depende del motor de la portada. */
(function () {
  'use strict';
  const raiz = document.getElementById('ef');
  if (!raiz) return;
  const D = JSON.parse(document.getElementById('efDatos').textContent);
  const $ = id => document.getElementById(id);
  const q = $('efQ'), aviso = $('efAviso'), res = $('efRes'), estado = $('efEstado');
  const filtros = $('efFiltros'), compartir = $('efCompartir');
  const L = { estado: 'sin-cargar', norm: null, rfcs: null, mapa: null, promesa: null };
  let filtro = '', tiempo = null, ultimoResumen = '';

  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const fmt = v => Number(v).toLocaleString('es-MX');
  const chip = e => '<span class="est-chip est-' + e + '">' + e + '</span>';
  function norm(s) {
    return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '')
      .toUpperCase().replace(/[^A-Z0-9& ]/g, ' ').replace(/\s+/g, ' ').trim();
  }
  const sinEsp = s => norm(s).replace(/ /g, '');
  /* RFC: 4 letras (persona física, 13) o 3 (moral, 12), fecha AAMMDD y homoclave de 3. */
  const RFC_OK = /^[A-Z&]{3,4}\d{6}[A-Z0-9]{3}$/;
  const PARECE_RFC = /^[A-Z&]{3,4}\d{2}/;

  function sello() {
    const s = document.querySelector('script[src*="insp-efos.js"]');
    const m = s && s.getAttribute('src').match(/\?v=([\w.-]+)/);
    return m ? '?v=' + m[1] : '';
  }

  function pintarEstado() {
    if (L.estado === 'cargando') { estado.textContent = '⏳ Descargando la lista oficial del SAT (1.5 MB)…'; return; }
    if (L.estado === 'error') {
      estado.innerHTML = chip('pendiente') + ' No se pudo descargar la lista. Revisa tu conexión y <button type="button" class="ef-reintentar" id="efReintentar">vuelve a intentar</button>.';
      $('efReintentar').addEventListener('click', cargar);
      return;
    }
    if (L.estado === 'listo') {
      estado.innerHTML = '✅ Lista lista: ' + chip('oficial') + ' <b>' + fmt(window.SAT_69B.meta.total) +
        '</b> registros, corte del SAT al ' + esc(window.SAT_69B.meta.corte) + '. Las búsquedas son inmediatas.';
    }
  }

  function cargar() {
    if (L.estado === 'listo') return Promise.resolve();
    if (L.promesa) return L.promesa;
    L.estado = 'cargando';
    pintarEstado();
    L.promesa = new Promise((ok, mal) => {
      if (window.SAT_69B) { ok(); return; }
      const sc = document.createElement('script');
      sc.src = 'assets/auditor/data/sat-69b.js' + sello();
      sc.onload = () => window.SAT_69B ? ok() : mal(new Error('sin datos'));
      sc.onerror = () => mal(new Error('no cargó'));
      document.head.appendChild(sc);
    }).then(() => {
      const R = window.SAT_69B.r;
      L.norm = R.map(r => norm(r[1]));
      L.rfcs = R.map(r => sinEsp(r[0]));
      L.mapa = new Map();
      L.rfcs.forEach((r, i) => { if (!L.mapa.has(r)) L.mapa.set(r, []); L.mapa.get(r).push(i); });
      L.estado = 'listo';
      pintarEstado();
      if (q.value) buscarYa();
      if ($('efLista').value.trim() && !$('efPanelVarios').hidden && $('efLote').dataset.pide) revisar();
    }, () => { L.estado = 'error'; L.promesa = null; pintarEstado(); });
    return L.promesa;
  }

  function ficha(r) {
    const s = D.sit[r[2]] || { t: r[2], c: '', i: '', corto: '', txt: '' };
    const medio = r[5] === 'DOF' ? 'el Diario Oficial de la Federación' : 'la página del SAT';
    return '<article class="ef-ficha ef-' + s.c + '">' +
      '<div class="ef-ficha-cab"><span class="ef-ficha-sit"><span aria-hidden="true">' + s.i + '</span> ' + esc(s.t) + '</span>' +
      '<code>' + esc(r[0]) + '</code></div>' +
      '<h3>' + esc(r[1]) + '</h3>' +
      '<p class="ef-ficha-corto">' + esc(s.corto) + '</p>' +
      '<p>' + esc(s.txt) + '</p>' +
      '<p class="ef-ficha-oficio">Oficio ' + esc(r[3]) + ' · publicado en ' + medio + ' el ' + esc(r[4]) + ' ' + chip('oficial') + '</p>' +
      '</article>';
  }

  function avisoRfc(n) {
    const r = n.replace(/ /g, '');
    if (!PARECE_RFC.test(r) || n.indexOf(' ') !== -1) return '';
    if (RFC_OK.test(r)) return '';
    if (r.length < 12) return '✏️ Parece un RFC incompleto (' + r.length + ' caracteres). Te mostramos los que empiezan así; un RFC completo tiene 12 caracteres si es empresa y 13 si es persona física.';
    if (r.length > 13) return '✏️ Un RFC tiene 12 caracteres (empresa) o 13 (persona física), y este tiene ' + r.length + '. Revisa que no se haya colado otro dato.';
    return '✏️ Tiene ' + r.length + ' caracteres, pero no sigue la forma de un RFC (letras, fecha AAMMDD y homoclave de 3). Revísalo; buscamos de todos modos.';
  }

  function buscar() { clearTimeout(tiempo); tiempo = setTimeout(buscarYa, 160); }

  function buscarYa() {
    const n = norm(q.value);
    actualizarUrl(q.value.trim());
    if (n.length < 3) {
      aviso.textContent = n.length ? 'Escribe al menos 3 letras o números.' : '';
      res.innerHTML = ''; filtros.hidden = true; compartir.hidden = true;
      return;
    }
    aviso.textContent = avisoRfc(n);
    if (L.estado !== 'listo') { res.innerHTML = '<p class="ef-vacio">⏳ En cuanto termine de descargarse la lista te mostramos el resultado.</p>'; cargar(); return; }
    const R = window.SAT_69B.r;
    const rfc = n.replace(/ /g, '');
    const esRfc = PARECE_RFC.test(rfc) && n.indexOf(' ') === -1;
    const palabras = n.split(' ');
    const idx = [];
    for (let i = 0; i < R.length; i++) {
      const ok = esRfc ? L.rfcs[i].indexOf(rfc) === 0 : palabras.every(p => L.norm[i].indexOf(p) !== -1);
      if (ok) idx.push(i);
    }
    compartir.hidden = false;
    if (!idx.length) {
      filtros.hidden = true;
      res.innerHTML = '<div class="ef-vacio ef-vacio-no"><p><b>No aparece</b> en la lista 69-B con corte al ' + esc(D.corte) + '.</p>' +
        '<p>Eso no certifica a nadie: solo significa que el SAT no lo ha incluido. ' +
        (esRfc ? 'Revisa que el RFC esté completo y bien escrito.' : 'Prueba con el RFC exacto, que es más preciso que el nombre.') + '</p></div>';
      return;
    }
    const cuenta = { F: 0, P: 0, D: 0, S: 0 };
    idx.forEach(i => { cuenta[R[i][2]] = (cuenta[R[i][2]] || 0) + 1; });
    filtros.hidden = idx.length < 2 && !filtro;
    filtros.querySelectorAll('.ef-filtro').forEach(b => {
      const f = b.dataset.f;
      b.setAttribute('aria-pressed', String(f === filtro));
      const base = b.dataset.base || (b.dataset.base = b.textContent);
      b.textContent = base + ' · ' + fmt(f ? (cuenta[f] || 0) : idx.length);
    });
    raiz.querySelectorAll('.ef-sit-btn').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.sit === filtro)));
    let vis = filtro ? idx.filter(i => R[i][2] === filtro) : idx;
    const vacioFiltro = filtro && !vis.length;
    if (vacioFiltro) vis = idx;
    const MAX = 40;
    let cab = '<p class="ef-cuenta"><b>' + fmt(idx.length) + '</b> ' + (idx.length === 1 ? 'registro coincide' : 'registros coinciden') +
      (vacioFiltro ? '. Ninguno en «' + esc(D.sit[filtro].t) + '», así que te mostramos todos' : filtro ? ' · ' + fmt(vis.length) + ' en «' + esc(D.sit[filtro].t) + '»' : '') + '.';
    if (vis.length > MAX) cab += ' Te mostramos los primeros ' + MAX + ': escribe el RFC o más palabras del nombre para afinar.';
    cab += '</p>';
    res.innerHTML = cab + '<div class="ef-fichas">' + vis.slice(0, MAX).map(i => ficha(R[i])).join('') + '</div>';
  }

  function actualizarUrl(v) {
    try {
      const u = new URL(location.href);
      if (v) u.searchParams.set('q', v); else u.searchParams.delete('q');
      history.replaceState(null, '', u.pathname + u.search + u.hash);
    } catch (e) { /* sin historial: no pasa nada */ }
  }

  function copiar(texto, btn, listo) {
    const fin = () => { const t = btn.dataset.t || (btn.dataset.t = btn.textContent); btn.textContent = listo; setTimeout(() => { btn.textContent = t; }, 2200); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(texto).then(fin, () => window.prompt('Copia:', texto));
    else window.prompt('Copia:', texto);
  }

  /* --- Varios RFC a la vez --- */
  function revisar() {
    const lote = $('efLote');
    const crudos = $('efLista').value.split(/[\s,;|]+/).map(s => s.trim()).filter(Boolean);
    const vistos = new Set(), lista = [];
    crudos.forEach(s => { const r = sinEsp(s); if (r && !vistos.has(r)) { vistos.add(r); lista.push(r); } });
    if (!lista.length) { lote.innerHTML = '<p class="ef-vacio">Pega al menos un RFC.</p>'; return; }
    const recorte = lista.length > 500;
    const L500 = lista.slice(0, 500);
    if (L.estado !== 'listo') { lote.dataset.pide = '1'; lote.innerHTML = '<p class="ef-vacio">⏳ En cuanto termine de descargarse la lista revisamos tus ' + fmt(L500.length) + ' RFC.</p>'; cargar(); return; }
    delete lote.dataset.pide;
    const R = window.SAT_69B.r;
    const grupos = { F: [], P: [], D: [], S: [], no: [], mal: [] };
    L500.forEach(r => {
      const hall = L.mapa.get(r);
      if (hall) hall.forEach(i => (grupos[R[i][2]] || grupos.F).push(R[i]));
      else (RFC_OK.test(r) ? grupos.no : grupos.mal).push(r);
    });
    const orden = ['F', 'P', 'D', 'S'];
    let h = '<div class="ef-resumen">' +
      '<p class="ef-resumen-tit">Revisaste <b>' + fmt(L500.length) + '</b> RFC distintos' + (recorte ? ' (solo los primeros 500)' : '') + ':</p><ul>' +
      orden.map(k => '<li class="ef-' + D.sit[k].c + '"><span aria-hidden="true">' + D.sit[k].i + '</span> ' + esc(D.sit[k].t) + ' <b>' + fmt(grupos[k].length) + '</b></li>').join('') +
      '<li class="ef-no"><span aria-hidden="true">◻️</span> No aparecen <b>' + fmt(grupos.no.length) + '</b></li>' +
      (grupos.mal.length ? '<li class="ef-mal"><span aria-hidden="true">✏️</span> Con formato dudoso <b>' + fmt(grupos.mal.length) + '</b></li>' : '') +
      '</ul></div>';
    if (grupos.F.length) h += '<p class="ef-alerta">⛔ ' + fmt(grupos.F.length) + (grupos.F.length === 1 ? ' proveedor tiene' : ' proveedores tienen') + ' situación <b>definitiva</b>: si un ente público le pagó, esa compra merece una pregunta formal.</p>';
    const filas = orden.flatMap(k => grupos[k]);
    if (filas.length) h += '<div class="ef-fichas">' + filas.map(ficha).join('') + '</div>';
    if (grupos.mal.length) h += '<p class="ef-nota-lote">✏️ No parecen RFC completos (12 caracteres si es empresa, 13 si es persona física) y no los encontramos: <code>' + grupos.mal.map(esc).join('</code>, <code>') + '</code>. Revísalos.</p>';
    h += '<p class="ef-nota-lote">Los que no aparecen no quedan certificados: solo no están en la lista con corte al ' + esc(D.corte) + '.</p>';
    lote.innerHTML = h;
    ultimoResumen = 'Revisión en la lista 69-B del SAT (corte al ' + D.corte + '), ' + L500.length + ' RFC:\n' +
      orden.map(k => '- ' + D.sit[k].t + ': ' + grupos[k].length + (grupos[k].length ? ' (' + grupos[k].map(r => r[0]).join(', ') + ')' : '')).join('\n') +
      '\n- No aparecen: ' + grupos.no.length + (grupos.mal.length ? '\n- Formato dudoso: ' + grupos.mal.join(', ') : '') +
      '\nFuente: SAT, listado del artículo 69-B del CFF. Aparecer en la lista es una determinación administrativa, no una condena penal.\n' + location.origin + location.pathname;
    $('efCopiar').hidden = false;
  }

  function modo(m) {
    raiz.querySelectorAll('.ef-modo').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.modo === m)));
    $('efPanelUno').hidden = m !== 'uno';
    $('efPanelVarios').hidden = m !== 'varios';
    (m === 'uno' ? q : $('efLista')).focus();
    cargar();
  }

  /* --- Eventos --- */
  q.addEventListener('input', buscar);
  q.addEventListener('focus', cargar, { once: true });
  $('efForm').addEventListener('submit', e => { e.preventDefault(); clearTimeout(tiempo); buscarYa(); });
  raiz.querySelectorAll('.ef-modo').forEach(b => b.addEventListener('click', () => modo(b.dataset.modo)));
  filtros.addEventListener('click', e => {
    const b = e.target.closest('.ef-filtro'); if (!b) return;
    filtro = b.dataset.f; buscarYa();
  });
  compartir.addEventListener('click', () => copiar(location.href, compartir, '✅ Enlace copiado'));
  $('efRevisar').addEventListener('click', revisar);
  $('efCopiar').addEventListener('click', () => copiar(ultimoResumen, $('efCopiar'), '✅ Resumen copiado'));
  /* Las tarjetas de situación: filtran la búsqueda y llevan arriba. */
  raiz.querySelectorAll('.ef-sit-btn').forEach(b => b.addEventListener('click', () => {
    filtro = b.dataset.sit;
    modo('uno');
    raiz.querySelectorAll('.ef-sit-btn').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    if (norm(q.value).length < 3) {
      aviso.textContent = 'Filtro puesto: «' + D.sit[filtro].t + '». Escribe un RFC o un nombre para buscar solo en esa situación.';
    } else buscarYa();
    const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    $('ef-q-tit').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
  }));

  /* ?q= en la dirección: la búsqueda llega hecha. */
  const inicial = new URLSearchParams(location.search).get('q');
  if (inicial) { q.value = inicial; buscarYa(); }

  /* Precarga en segundo plano: la primera búsqueda es inmediata. */
  const ocioso = window.requestIdleCallback || (f => setTimeout(f, 1200));
  ocioso(() => cargar(), { timeout: 2500 });
})();
