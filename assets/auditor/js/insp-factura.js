/* Auditavisión · Modo Inspector › Lector de facturas CFDI (05-11-2026).
   La página la escribe herramientas/insp_factura.py; la misma lógica, en
   Python, está en herramientas/lector_cfdi.py.

   Todo ocurre en el navegador: DOMParser lee el XML y nada se sube ni se
   guarda (ni localStorage ni servidor), porque una factura trae datos
   personales. La lista 69-B (assets/auditor/data/sat-69b.js) se descarga
   la primera vez que se lee una factura.

   Lo que dice la lista es «oficial»; lo que sale de comparar fechas o de
   rehacer la cuenta es «derivado» y se rotula «señal para revisar». */
(function () {
  'use strict';
  const raiz = document.getElementById('cf');
  if (!raiz) return;
  const D = JSON.parse(document.getElementById('cfDatos').textContent);
  const $ = id => document.getElementById(id);
  const res = $('cfRes'), estado = $('cfEstado'), acciones = $('cfAcciones');
  /* Los espacios de nombres: la dirección manda, no el apodo «cfdi:». */
  const NS = { 'http://www.sat.gob.mx/cfd/4': '4.0', 'http://www.sat.gob.mx/cfd/3': '3.3' };
  const TFD = 'http://www.sat.gob.mx/TimbreFiscalDigital';
  const TIPOS = { I: 'Ingreso', E: 'Egreso', T: 'Traslado', N: 'Nómina', P: 'Pago' };
  const TOL = 0.01;
  const facturas = [];
  let lista = null, promesa = null;

  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const chip = e => '<span class="est-chip est-' + e + '">' + e + '</span>';
  const pesos = v => '$' + Number(v).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const num = v => { const n = parseFloat(v); return isNaN(n) ? 0 : n; };
  const fisica = rfc => rfc.length === 13;
  /* El RFC de una persona física no se muestra completo (AGENTS.md §2 bis). */
  const tapa = rfc => fisica(rfc) ? rfc.slice(0, 4) + '••••••' + rfc.slice(10) : rfc;
  const quien = (rfc, nom) => fisica(rfc) ? 'Persona física (nombre oculto)' : (nom || 'Sin nombre en el XML');

  function sello() {
    const s = document.querySelector('script[src*="insp-factura.js"]');
    const m = s && s.getAttribute('src').match(/\?v=([\w.-]+)/);
    return m ? '?v=' + m[1] : '';
  }
  function cargarLista() {
    if (lista) return Promise.resolve(lista);
    if (promesa) return promesa;
    estado.textContent = '⏳ Descargando la lista 69-B del SAT…';
    promesa = new Promise((ok, mal) => {
      if (window.SAT_69B) { ok(); return; }
      const sc = document.createElement('script');
      sc.src = 'assets/auditor/data/sat-69b.js' + sello();
      sc.onload = () => window.SAT_69B ? ok() : mal();
      sc.onerror = mal;
      document.head.appendChild(sc);
    }).then(() => {
      lista = new Map(window.SAT_69B.r.map(r => [r[0], r]));
      estado.innerHTML = '✅ Lista 69-B lista: ' + chip('oficial') + ' corte del SAT al ' + esc(D.corte) + '.';
      return lista;
    }, () => {
      promesa = null;
      estado.innerHTML = chip('pendiente') + ' No se pudo descargar la lista 69-B; la factura se lee igual, sin el cruce. Revisa tu conexión y vuelve a elegirla.';
      return null;
    });
    return promesa;
  }

  /* Lee una factura. Devuelve sus datos o lanza un Error con el motivo. */
  function leer(texto) {
    const doc = new DOMParser().parseFromString(texto, 'application/xml');
    if (doc.getElementsByTagName('parsererror').length) throw new Error('el archivo no es un XML bien formado');
    const c = doc.documentElement, version = NS[c.namespaceURI];
    if (c.localName !== 'Comprobante') throw new Error('no es un CFDI: su elemento principal no es «Comprobante»');
    if (!version) throw new Error('no reconozco su versión (' + (c.namespaceURI || 'sin espacio de nombres') + ')');
    const ns = c.namespaceURI;
    /* Solo los hijos directos: el <Impuestos> del total, no el de cada concepto. */
    const hijo = (el, n) => Array.prototype.find.call(el.children, x => x.namespaceURI === ns && x.localName === n) || null;
    const at = (el, n) => (el && el.getAttribute(n)) || '';
    const em = hijo(c, 'Emisor'), re = hijo(c, 'Receptor'), imp = hijo(c, 'Impuestos');
    const tim = doc.getElementsByTagNameNS(TFD, 'TimbreFiscalDigital')[0] || null;
    const con = hijo(c, 'Conceptos');
    const conceptos = con ? Array.prototype.filter.call(con.children, x => x.localName === 'Concepto')
      .map(x => ({ d: at(x, 'Descripcion'), n: num(at(x, 'Cantidad')), i: num(at(x, 'Importe')) })) : [];
    return {
      version: version, uuid: at(tim, 'UUID'), fecha: at(c, 'Fecha'), timbrado: at(tim, 'FechaTimbrado'),
      folio: (at(c, 'Serie') + ' ' + at(c, 'Folio')).trim(), tipo: TIPOS[at(c, 'TipoDeComprobante')] || at(c, 'TipoDeComprobante'),
      moneda: at(c, 'Moneda'), emRfc: at(em, 'Rfc').toUpperCase(), emNom: at(em, 'Nombre'), emReg: at(em, 'RegimenFiscal'),
      reRfc: at(re, 'Rfc').toUpperCase(), reNom: at(re, 'Nombre'), uso: at(re, 'UsoCFDI'),
      sub: num(at(c, 'SubTotal')), desc: num(at(c, 'Descuento')), tras: num(at(imp, 'TotalImpuestosTrasladados')),
      ret: num(at(imp, 'TotalImpuestosRetenidos')), total: num(at(c, 'Total')), conceptos: conceptos
    };
  }

  /* Rehace la cuenta (derivado). Devuelve las diferencias. */
  function cuadra(f) {
    const out = [], calc = f.sub - f.desc + f.tras - f.ret;
    if (Math.abs(calc - f.total) > TOL) out.push('el total dice ' + pesos(f.total) + ' y la cuenta da ' + pesos(calc));
    if (f.conceptos.length) {
      const s = f.conceptos.reduce((a, x) => a + x.i, 0);
      if (Math.abs(s - f.sub) > TOL) out.push('los conceptos suman ' + pesos(s) + ' y el subtotal dice ' + pesos(f.sub));
    }
    return out;
  }

  const fechaSat = s => { const m = /^(\d\d)\/(\d\d)\/(\d{4})$/.exec(s || ''); return m ? m[3] + '-' + m[2] + '-' + m[1] : ''; };

  /* La lista 69-B de un RFC: lo oficial y, aparte, las señales (derivado). */
  function cruce(rfc, fecha) {
    const r = lista && lista.get(rfc);
    if (!r) return null;
    const s = D.sit[r[2]], ff = (fecha || '').slice(0, 10), fp = fechaSat(r[6]), fd = fechaSat(r[7]), sen = [];
    if (r[2] === 'D' || r[2] === 'S') {
      sen.push(['favor', '✅ A favor del contribuyente: ' + (r[2] === 'D' ? 'desvirtuó la presunción ante el SAT.' : 'un tribunal le dio la razón frente al SAT.')]);
    } else {
      if (ff && fd && ff >= fd) sen.push(['senal', 'la factura es del ' + ff + ', posterior a su publicación como definitivo (' + r[7] + ').']);
      else if (ff && fp && ff >= fp) sen.push(['senal', 'la factura es del ' + ff + ', cuando ya estaba publicado como presunto (' + r[6] + ').']);
      if (r[2] === 'F') sen.push(['ley', 'El art. 69-B del Código Fiscal (párrafo quinto) dice que las operaciones de sus comprobantes no producen ni produjeron efecto fiscal alguno; quien la recibió tiene 30 días tras la publicación para acreditar que sí recibió el bien o servicio, o para corregir su situación (párrafo octavo).']);
    }
    return { r: r, s: s, sen: sen };
  }

  function tarjeta(x) {
    if (x.error) return '<article class="cf-fac cf-fac-mal"><h3>📄 ' + esc(x.archivo) + '</h3><p>' + chip('pendiente') + ' No se pudo leer: ' + esc(x.error) + '.</p></article>';
    const f = x.f, dif = cuadra(f), em = cruce(f.emRfc, f.fecha), rc = cruce(f.reRfc, f.fecha);
    const parte = (rol, rfc, nom, c) => '<li><b>' + rol + ':</b> ' + esc(quien(rfc, nom)) + ' · RFC <code>' + esc(tapa(rfc)) + '</code>' +
      (c ? ' <span class="cf-badge cf-' + c.s.c + '">' + c.s.i + ' ' + esc(c.s.t) + '</span>' : '') + '</li>';
    let h = '<article class="cf-fac"><h3>📄 ' + esc(x.archivo) + (x.ejemplo ? ' <small>(ficticia)</small>' : '') + '</h3>' +
      (f.version === '3.3' ? '<p class="cf-nota">Es un CFDI 3.3 (anterior a 2022): lo leo igual, con los campos que comparte con el 4.0.</p>' : '') +
      '<ul class="cf-datos"><li><b>UUID (folio fiscal):</b> <code>' + esc(f.uuid || 'sin timbre') + '</code></li>' +
      '<li><b>Fecha:</b> ' + esc(f.fecha) + (f.timbrado ? ' · timbrada el ' + esc(f.timbrado) : '') + (f.folio ? ' · serie y folio ' + esc(f.folio) : '') + '</li>' +
      '<li><b>Tipo:</b> ' + esc(f.tipo) + ' · CFDI ' + f.version + (f.moneda ? ' · ' + esc(f.moneda) : '') + '</li>' +
      parte('Emisor', f.emRfc, f.emNom, em) + parte('Receptor', f.reRfc, f.reNom, rc) + '</ul>' +
      '<table class="cf-cuenta"><tbody>' +
      '<tr><th scope="row">Subtotal</th><td>' + pesos(f.sub) + '</td></tr>' +
      (f.desc ? '<tr><th scope="row">− Descuento</th><td>' + pesos(f.desc) + '</td></tr>' : '') +
      '<tr><th scope="row">+ Impuestos trasladados</th><td>' + pesos(f.tras) + '</td></tr>' +
      (f.ret ? '<tr><th scope="row">− Impuestos retenidos</th><td>' + pesos(f.ret) + '</td></tr>' : '') +
      '<tr class="cf-total"><th scope="row">Total</th><td>' + pesos(f.total) + '</td></tr></tbody></table>' +
      '<p>' + chip('derivado') + ' ' + (dif.length ? '⚠️ <b>Señal para revisar:</b> ' + esc(dif.join('; ')) + '.' : '✅ La cuenta cuadra: subtotal − descuento + trasladados − retenidos = total' + (f.conceptos.length ? ', y los conceptos suman el subtotal' : '') + '.') + '</p>';
    if (f.conceptos.length) {
      h += '<details class="cf-con"><summary>' + f.conceptos.length + (f.conceptos.length === 1 ? ' concepto' : ' conceptos') + '</summary><ul>' +
        f.conceptos.slice(0, 50).map(k => '<li>' + esc(k.d || 'Sin descripción') + ' · ' + k.n + ' × · ' + pesos(k.i) + '</li>').join('') + '</ul></details>';
    }
    [['El emisor', em], ['El receptor', rc]].forEach(p => {
      const c = p[1];
      if (!c) return;
      h += '<div class="cf-69b"><p class="cf-dos-t">' + chip('oficial') + ' ' + p[0] + ' en la lista 69-B</p><p>' + c.s.i + ' <b>' + esc(c.s.t) + '</b>: ' + esc(c.s.corto) +
        '. Oficio ' + esc(c.r[3]) + ', publicado el ' + esc(c.r[4]) + ' (' + esc(c.r[5]) + ').</p>' +
        c.sen.map(s => s[0] === 'senal' ? '<p>' + chip('derivado') + ' ⚠️ <b>Señal para revisar:</b> ' + esc(s[1]) + ' No es una irregularidad: es lo que conviene preguntar.</p>'
          : '<p>' + (s[0] === 'ley' ? '⚖️ ' : '') + esc(s[1]) + '</p>').join('') + '</div>';
    });
    if (!em && lista) h += '<p>' + chip('oficial') + ' El emisor <b>no aparece</b> en la lista 69-B con corte al ' + esc(D.corte) + '. No aparecer no prueba que la operación existió: dice que el SAT no lo ha publicado.</p>';
    return h + '</article>';
  }

  function tabla() {
    const ok = facturas.filter(x => !x.error);
    if (ok.length < 2) return '';
    const total = ok.reduce((a, x) => a + x.f.total, 0), en = ok.filter(x => cruce(x.f.emRfc, x.f.fecha)).length;
    return '<div class="cf-tabla-caja"><p><b>' + ok.length + '</b> facturas leídas · suman ' + pesos(total) + ' ' + chip('derivado') + ' (suma de sus totales, sin convertir monedas) · ' +
      '<b>' + en + '</b> con el emisor en la lista 69-B.</p><table class="cf-tabla"><thead><tr><th scope="col">Archivo</th><th scope="col">Fecha</th><th scope="col">Emisor</th>' +
      '<th scope="col">Total</th><th scope="col">Cuenta</th><th scope="col">69-B</th></tr></thead><tbody>' +
      ok.map(x => { const c = cruce(x.f.emRfc, x.f.fecha);
        return '<tr><td>' + esc(x.archivo) + '</td><td>' + esc(x.f.fecha.slice(0, 10)) + '</td><td><code>' + esc(tapa(x.f.emRfc)) + '</code></td><td>' + pesos(x.f.total) +
          '</td><td>' + (cuadra(x.f).length ? '⚠️ no cuadra' : '✅') + '</td><td>' + (c ? c.s.i + ' ' + esc(c.s.t) : '—') + '</td></tr>'; }).join('') + '</tbody></table></div>';
  }

  /* Facturas por lote (05-11-2026, entrega B de «Mi Auditavisión»): el resumen
     por emisor, con las mismas reglas que por_proveedor() de lector_cfdi.py.
     Primero los que están en la lista 69-B y luego por monto. */
  const ORDEN = { F: 0, P: 1, S: 2, D: 3 };
  function proveedores() {
    const g = new Map();
    facturas.filter(x => !x.error).forEach(x => {
      const f = x.f;
      const p = g.get(f.emRfc) || { rfc: f.emRfc, nom: f.emNom, n: 0, total: 0, monedas: new Set(), mal: 0, sen: 0 };
      p.n += 1; p.total += f.total; p.monedas.add(f.moneda || 'MXN');
      if (cuadra(f).length) p.mal += 1;
      const c = cruce(f.emRfc, f.fecha);
      if (c) p.sen += c.sen.filter(s => s[0] === 'senal').length;
      g.set(f.emRfc, p);
    });
    return Array.from(g.values()).map(p => Object.assign(p, { c: cruce(p.rfc, '') }))
      .sort((a, b) => ((a.c ? ORDEN[a.c.r[2]] : 9) - (b.c ? ORDEN[b.c.r[2]] : 9)) || (b.total - a.total));
  }
  function tablaProv() {
    const ok = facturas.filter(x => !x.error);
    if (ok.length < 2) return '';
    const pv = proveedores(), en = pv.filter(p => p.c && (p.c.r[2] === 'F' || p.c.r[2] === 'P')).length;
    return '<div class="cf-tabla-caja"><h3>🏢 Por proveedor</h3><p><b>' + pv.length + '</b> emisores · <b>' + en + '</b> en la lista 69-B como definitivo o presunto ' + chip('oficial') +
      '. Montos: suma de los totales de sus facturas, sin convertir monedas ' + chip('derivado') + '.</p>' +
      '<table class="cf-tabla"><thead><tr><th scope="col">Emisor</th><th scope="col">Facturas</th><th scope="col">Suma</th><th scope="col">No cuadran</th>' +
      '<th scope="col">Lista 69-B</th><th scope="col">Señales de fecha</th></tr></thead><tbody>' +
      pv.map(p => '<tr><td>' + esc(quien(p.rfc, p.nom)) + '<br><code>' + esc(tapa(p.rfc)) + '</code></td><td>' + p.n + '</td><td>' + pesos(p.total) +
        (p.monedas.size > 1 || !p.monedas.has('MXN') ? ' <small>(' + esc(Array.from(p.monedas).join(', ')) + ')</small>' : '') + '</td><td>' + (p.mal ? '⚠️ ' + p.mal : '—') +
        '</td><td>' + (p.c ? p.c.s.i + ' ' + esc(p.c.s.t) : 'no aparece') + '</td><td>' + (p.sen ? '⚠️ ' + p.sen : '—') + '</td></tr>').join('') +
      '</tbody></table></div>';
  }

  /* Con muchas facturas, las tarjetas de las que no traen señal se pliegan. */
  const conSenal = x => x.error || cuadra(x.f).length || cruce(x.f.emRfc, x.f.fecha) || cruce(x.f.reRfc, x.f.fecha);
  function pintar() {
    let cuerpo;
    if (facturas.length > 20) {
      const si = facturas.filter(conSenal), no = facturas.filter(x => !conSenal(x));
      cuerpo = (si.length ? '<h3>⚠️ ' + (si.length === 1 ? 'La factura' : 'Las ' + si.length + ' facturas') + ' con algo que revisar</h3>' + si.map(tarjeta).join('') : '<p>✅ Ninguna factura trae algo que revisar.</p>') +
        (no.length ? '<details class="cf-con"><summary>Ver ' + (no.length === 1 ? 'la factura' : 'las ' + no.length + ' facturas') + ' sin señales</summary>' + no.map(tarjeta).join('') + '</details>' : '');
    } else cuerpo = facturas.map(tarjeta).join('');
    res.innerHTML = tablaProv() + tabla() + cuerpo;
    acciones.hidden = !facturas.length;
  }

  function agrega(archivo, texto, ejemplo) {
    try { facturas.push({ archivo: archivo, f: leer(texto), ejemplo: ejemplo }); }
    catch (e) { facturas.push({ archivo: archivo, error: e.message }); }
  }
  function leerArchivos(lista_) {
    const arr = Array.prototype.slice.call(lista_ || []).slice(0, 500);
    if (!arr.length) return;
    Promise.all([cargarLista()].concat(arr.map(a => a.text().then(t => [a.name, t], () => [a.name, ''])))).then(v => {
      v.slice(1).forEach(p => agrega(p[0], p[1]));
      pintar();
    });
  }

  $('cfArchivos').addEventListener('change', e => { leerArchivos(e.target.files); e.target.value = ''; });
  const suelta = $('cfSuelta');
  ['dragenter', 'dragover'].forEach(n => suelta.addEventListener(n, e => { e.preventDefault(); suelta.classList.add('cf-sobre'); }));
  ['dragleave', 'drop'].forEach(n => suelta.addEventListener(n, () => suelta.classList.remove('cf-sobre')));
  suelta.addEventListener('drop', e => { e.preventDefault(); leerArchivos(e.dataTransfer && e.dataTransfer.files); });
  $('cfLeerTexto').addEventListener('click', () => {
    const t = $('cfTexto').value.trim();
    if (!t) return;
    cargarLista().then(() => { agrega('XML pegado', t); $('cfTexto').value = ''; pintar(); });
  });
  $('cfEjemplo').addEventListener('click', () => {
    Promise.all([cargarLista(), fetch('docs/ejemplos/factura-ficticia-cfdi40.xml').then(r => r.ok ? r.text() : Promise.reject())]).then(v => {
      agrega('factura-ficticia-cfdi40.xml', v[1], true);
      pintar();
    }, () => { estado.innerHTML = chip('pendiente') + ' No se pudo traer la factura de ejemplo.'; });
  });
  $('cfLimpiar').addEventListener('click', () => { facturas.length = 0; pintar(); });
  /* Mi Auditavisión (05-11-2026): guarda el RESUMEN en el navegador del lector,
     clave «av-mia» (el formato lo lee insp-mia.js). Nunca el archivo. */
  function miaGuardar(rev, prov) {
    try {
      const t = JSON.parse(localStorage.getItem('av-mia') || '{}');
      t.prov = Array.from(new Set((t.prov || []).concat(prov || []))).slice(0, 500);
      t.rev = [rev].concat(t.rev || []).slice(0, 30);
      localStorage.setItem('av-mia', JSON.stringify(t));
      return true;
    } catch (e) { return false; }
  }
  $('cfMia').addEventListener('click', () => {
    const ok_ = facturas.filter(x => !x.error);
    if (!ok_.length) return;
    const pv = proveedores(), mal = ok_.filter(x => cuadra(x.f).length).length;
    const en = pv.filter(p => p.c && (p.c.r[2] === 'F' || p.c.r[2] === 'P'));
    const lineas = [ok_.length + ' facturas de ' + pv.length + ' emisores; ' + (mal ? mal + ' no cuadran.' : 'todas cuadran.')]
      .concat(en.map(p => quien(p.rfc, p.nom) + ' (' + tapa(p.rfc) + '): ' + p.c.s.t + ' en la lista 69-B, ' + p.n + ' facturas por ' + pesos(p.total) + '.'));
    const senales = mal + pv.reduce((a, p) => a + p.sen, 0) + en.length;
    const g = miaGuardar({ tipo: 'facturas', fecha: new Date().toISOString().slice(0, 10), titulo: 'Facturas · ' + ok_.length + ' revisadas',
      lineas: lineas, senales: senales, ir: 'herramienta-inspector-factura.html' }, pv.map(p => p.rfc).filter(r => !fisica(r)));
    estado.textContent = g ? '📌 Guardado en Mi Auditavisión, con sus emisores en «Mis proveedores» (solo en este navegador; las personas físicas no se guardan).' : 'Tu navegador no deja guardar aquí (modo privado o datos bloqueados).';
  });
  $('cfCsvProv').addEventListener('click', () => {
    const q = v => '"' + String(v == null ? '' : v).replace(/"/g, '""') + '"';
    const filas = proveedores().map(p => [tapa(p.rfc), quien(p.rfc, p.nom), p.n, p.total.toFixed(2), Array.from(p.monedas).join(', '), p.mal,
      p.c ? p.c.s.t + ' · oficio ' + p.c.r[3] + ' del ' + p.c.r[4] : 'no aparece', p.sen].map(q).join(','));
    const blob = new Blob(['\ufeff' + ['emisor_rfc,emisor_nombre,facturas,total,monedas,no_cuadran,lista_69b,senales'].concat(filas).join('\r\n')], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'proveedores-auditavision.csv';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  });
  /* La tabla en CSV se arma aquí y se descarga directo: no pasa por ningún servidor. */
  $('cfCsv').addEventListener('click', () => {
    const cols = ['archivo', 'version', 'uuid', 'fecha', 'tipo', 'emisor_rfc', 'emisor_nombre', 'receptor_rfc', 'receptor_nombre', 'subtotal', 'trasladados', 'retenidos', 'total', 'moneda', 'cuenta', 'lista_69b_emisor'];
    const q = v => '"' + String(v == null ? '' : v).replace(/"/g, '""') + '"';
    const filas = facturas.filter(x => !x.error).map(x => {
      const f = x.f, c = cruce(f.emRfc, f.fecha), d = cuadra(f);
      return [x.archivo, f.version, f.uuid, f.fecha, f.tipo, tapa(f.emRfc), quien(f.emRfc, f.emNom), tapa(f.reRfc), quien(f.reRfc, f.reNom),
        f.sub.toFixed(2), f.tras.toFixed(2), f.ret.toFixed(2), f.total.toFixed(2), f.moneda, d.length ? 'no cuadra: ' + d.join('; ') : 'cuadra',
        c ? c.s.t + ' · oficio ' + c.r[3] + ' del ' + c.r[4] : 'no aparece'].map(q).join(',');
    });
    const blob = new Blob(['﻿' + [cols.join(',')].concat(filas).join('\r\n')], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'facturas-auditavision.csv';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  });
})();
