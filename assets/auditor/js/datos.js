/* ===================================================================
   AUDITAVISION - Fichas de la página de datos (descarga-los-datos.html)
   -------------------------------------------------------------------
   Desde el 09-10-2026 las fichas de «Datos abiertos» e «Informes
   oficiales» se despliegan aquí mismo, debajo de su fila, con su
   contenido completo: ya no abren la portada (AGENTS.md §5 bis).
   Las descargas en CSV y los Informes de la Cuenta Pública son copia
   del motor (audit-engine.js, DESCARGAS y renderCuentaPublica): si
   cambia uno, cambia el otro. Lee window.AUDIT_DB y
   window.AUDIT_MUNICIPIOS; la lista 69-B del SAT se baja solo cuando
   se pide su CSV.
   =================================================================== */
(function () {
  'use strict';

  const DB = window.AUDIT_DB || {};
  /* El auditor le habla de tú al lector (AGENTS.md §6). */
  function tuUd(usted, tu) { return tu; }

  /* La lista 69-B del SAT pesa cerca de 1.5 MB: se baja solo al pedir su CSV. */
  let efosPromesa = null;
  function efosCargar() {
    if (window.SAT_69B) return Promise.resolve();
    if (efosPromesa) return efosPromesa;
    const yo = document.querySelector('script[src*="datos.js"]');
    const m = yo && yo.getAttribute('src').match(/\?v=([\w.-]+)/);
    efosPromesa = new Promise((ok, mal) => {
      const sc = document.createElement('script');
      sc.src = 'assets/auditor/data/sat-69b.js' + (m ? '?v=' + m[1] : '');
      sc.onload = ok;
      sc.onerror = () => { efosPromesa = null; mal(new Error('no cargó')); };
      document.head.appendChild(sc);
    });
    return efosPromesa;
  }

  function pdEsc(t) {
    return String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function pdMdp(pesos, dec) {
    const d = (dec == null) ? 1 : dec;
    return '$' + (pesos / 1e6).toLocaleString('es-MX', { minimumFractionDigits: d, maximumFractionDigits: d }) + ' mdp';
  }

  function pdPesos(p) { return '$' + Math.round(p).toLocaleString('es-MX'); }

  function pdPct(p, d) { return p.toLocaleString('es-MX', { minimumFractionDigits: d == null ? 1 : d, maximumFractionDigits: d == null ? 1 : d }) + ' %'; }

  function pdBarra(valor, maximo, clase) {
    const w = maximo > 0 ? Math.max(0.6, valor / maximo * 100) : 0;
    return '<span class="pd-barra" aria-hidden="true"><span class="pd-barra-v ' + (clase || '') + '" style="width:' + w.toFixed(2) + '%"></span></span>';
  }

  function amNum(v, dec) {
    return v.toLocaleString('es-MX', { minimumFractionDigits: dec || 0, maximumFractionDigits: dec || 0 });
  }

  function amTarjeta(valor, rotulo, estado, pie) {
    return '<div class="am-dato"><strong class="num-tabular">' + valor + '</strong><span>' + rotulo + ' ' + chipEstado(estado) + '</span>' +
      (pie ? '<small>' + pie + '</small>' : '') + '</div>';
  }

  function chipEstado(estado) {
    /* Tres estados y no dos: hay cifras que la fuente oficial publica,
       cifras que esta plataforma deriva y datos que sencillamente no
       estan publicados. Llamar «derivado» al tercero seria fingir que
       existe un calculo detras. */
    const texto = (estado === 'oficial' || estado === 'pendiente') ? estado : 'derivado';
    return '<span class="est-chip est-' + texto + '">' + texto + '</span>';
  }

  function dlMunicipios() {
    const M = window.AUDIT_MUNICIPIOS;
    if (!M) return [];
    const filas = [];
    Object.keys(M.ent).forEach(abbr => {
      const e = M.ent[abbr];
      e.lista.forEach(m => {
        const sin = m.length <= 2;
        filas.push([e.cve + m[0], abbr, m[1]].concat(sin ? ['', '', '', '', '', '', '', ''] : m.slice(2, 10)).concat([sin ? 'sin reporte 2024' : 'oficial']));
      });
    });
    return filas;
  }

  const DESCARGAS = [
    { id: 'municipios', titulo: 'Finanzas de los 2,479 municipios, 2024',
      fuente: 'INEGI, Estadística de Finanzas Públicas Estatales y Municipales (EFIPEM), cifras definitivas 2024',
      desc: 'Lo que ingresó cada municipio del país: total, participaciones, aportaciones, FORTAMUN, FISMDF, predial e ingresos propios, y lo que egresó. En pesos.',
      campos: [['clave_inegi', 'Clave de 5 dígitos: entidad y municipio'], ['entidad', 'Abreviatura de la entidad'], ['municipio', 'Nombre oficial'],
        ['ingreso_total', 'Ingresos totales del ejercicio'], ['participaciones', 'Ramo 28, de libre disposición'], ['aportaciones', 'Ramo 33, etiquetadas por ley'],
        ['fortamun', 'Fondo de Aportaciones para el Fortalecimiento de los Municipios'], ['fismdf', 'Fondo de Aportaciones para la Infraestructura Social Municipal'],
        ['predial', 'Impuesto predial cobrado'], ['ingresos_propios', 'Impuestos, derechos, productos y aprovechamientos propios'], ['egreso_total', 'Egresos totales del ejercicio'],
        ['estado_dato', '«oficial», o «sin reporte 2024» si el municipio no rindió cuenta al INEGI']],
      filas: () => dlMunicipios() },
    { id: 'remuneraciones', titulo: 'Remuneraciones netas 2026 de los altos cargos',
      fuente: 'PEF 2026, Anexo 23 (DOF 21-11-2025) y Manual de remuneraciones del PJF 2026 (DOF 27-02-2026)',
      desc: 'Lo que recibe al año, ya descontados impuestos, cada cargo que usa el comparador «Tú contra ellos».',
      campos: [['cargo', 'Cargo'], ['ente', 'Institución'], ['neto_anual', 'Remuneración total anual neta, en pesos'], ['estado', 'oficial, derivado o parcial'], ['documento', 'Documento de origen'], ['pagina', 'Página o apartado']],
      filas: () => ((DB.poderes && DB.poderes.remuneraciones2026) || []).map(c => [c.cargo, c.ente, c.netoAnual, c.parcial ? 'parcial' : (c.netoAnualEstado || c.estado), ((DB.poderes.fuentes[c.fuente] || {}).doc || ''), c.pagina]) },
    { id: 'poderes-gasto', titulo: 'Gasto del Congreso y del Poder Judicial, 2025 y 2026',
      fuente: 'SHCP: Cuenta Pública 2025 y avance del gasto al 30 de junio de 2026 (datos abiertos)',
      desc: 'Por unidad: original y ejercido de 2025; aprobado, modificado y pagado de 2026 al 30 de junio.',
      campos: [['ramo', '01 Legislativo, 03 Judicial'], ['unidad', 'Clave de la unidad responsable'], ['nombre', 'Unidad'], ['original_2025', 'Presupuesto original 2025'], ['ejercido_2025', 'Ejercido 2025 (incluye devengado)'],
        ['aprobado_2026', 'Aprobado 2026'], ['modificado_2026', 'Modificado al 30 de junio de 2026'], ['pagado_2026', 'Pagado al 30 de junio de 2026']],
      filas: () => {
        const E = DB.poderes && DB.poderes.ejercicio;
        if (!E) return [];
        const claves = {};
        E.cp2025.unidades.concat(E.avance2026.unidades).forEach(u => { claves[u.ramo + '|' + u.ur] = u.nombre; });
        return Object.keys(claves).sort().map(k => {
          const [ramo, ur] = k.split('|');
          const a = E.cp2025.unidades.find(u => u.ramo === ramo && u.ur === ur) || {};
          const b = E.avance2026.unidades.find(u => u.ramo === ramo && u.ur === ur) || {};
          return [ramo, ur, claves[k], a.original, a.ejercido, b.aprobado, b.modificado, b.pagado];
        });
      } },
    { id: 'ambiente', titulo: 'Presupuesto ambiental (Ramo 16), 2026 y proyecto 2027',
      fuente: 'PEF 2026, avance del gasto al 30 de junio de 2026 y proyecto de PEF 2027 (SHCP, datos abiertos)',
      desc: 'Por órgano del sector ambiental: aprobado, modificado y pagado en 2026, y lo propuesto para 2027.',
      campos: [['unidad', 'Clave de la unidad responsable'], ['nombre', 'Órgano'], ['aprobado_2026', 'Aprobado 2026'], ['modificado_2026', 'Modificado al 30 de junio'], ['pagado_2026', 'Pagado al 30 de junio'], ['proyecto_2027', 'Proyecto 2027 (aún no aprobado)']],
      filas: () => ((DB.ambiente && DB.ambiente.presupuesto.unidades) || []).map(u => [u.ur, u.nombre, u.aprobado, u.modificado, u.pagado, u.proyecto2027]) },
    { id: 'asf-cp2024', titulo: 'Auditorías de la ASF al dinero federal de cada estado, Cuenta Pública 2024',
      fuente: 'ASF, Matriz de Datos Básicos del Informe del Resultado de la Cuenta Pública 2024, tres entregas (consolidado), corte febrero de 2026, pp. 19 a 23',
      desc: 'Por estado y por quién gastó (gobierno del estado, municipios o alcaldías, y otros entes): auditorías, acciones, monto recuperado y monto por aclarar. En pesos.',
      campos: [['entidad', 'Entidad federativa'], ['ente', 'Gobierno del Estado, Municipios (Alcaldías en la CDMX) u Otros'], ['auditorias', 'Auditorías practicadas'], ['acciones', 'Acciones promovidas por la ASF'],
        ['recuperado', 'Recuperaciones operadas durante la auditoría, en pesos'], ['por_aclarar', 'Montos por aclarar durante el seguimiento de las acciones, en pesos']],
      filas: () => {
        const C = DB.cuenta_publica_asf;
        if (!C) return [];
        const f = [];
        C.cp2024.entidades.forEach(e => e.desglose.forEach(d => f.push([e.entidad, d.ente, d.auditorias, d.acciones, d.recuperaciones, d.porAclarar])));
        return f;
      } },
    { id: 'sat69b', titulo: 'Lista 69-B del SAT (EFOS)',
      fuente: 'SAT, Listado completo de contribuyentes del artículo 69-B del Código Fiscal',
      desc: 'Contribuyentes presuntos, definitivos, desvirtuados o con sentencia favorable por facturar operaciones inexistentes. Estar en la lista no es una condena penal.',
      campos: [['rfc', 'RFC'], ['nombre', 'Nombre o razón social'], ['situacion', 'Presunto, Definitivo, Desvirtuado o Sentencia favorable'], ['oficio', 'Número del oficio de esa etapa'], ['fecha_publicacion', 'Fecha de publicación'], ['medio', 'DOF o página del SAT']],
      filas: async () => {
        await efosCargar();
        if (!window.SAT_69B) return [];
        return window.SAT_69B.r.map(r => [r[0], r[1], EFOS_SIT[r[2]].t, r[3], r[4], r[5]]);
      } },
    { id: 'referencias', titulo: 'Catálogo de documentos y referencias',
      fuente: 'Auditavisión, catálogo de referencias legales y documentales',
      desc: 'Cada ley, decreto, informe y base de datos que sostiene las cifras de la plataforma, con su liga oficial.',
      campos: [['numero', 'Número de la ficha'], ['id', 'Identificador interno'], ['categoria', 'Categoría'], ['cita', 'Cita en formato APA'], ['url', 'Liga al documento'], ['descripcion', 'Para qué sirve']],
      filas: () => (DB.referencias_legales || []).map(r => [r.num, r.id, r.categoria_nombre, r.cita_apa, r.url, r.descripcion]) }
  ];

  function dlCeldaCSV(v) {
    if (v === undefined || v === null) return '';
    const s = typeof v === 'number' ? String(Math.round(v * 100) / 100) : String(v);
    return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }

  async function descargarCSV(id) {
    const d = DESCARGAS.find(x => x.id === id);
    if (!d) return;
    const filas = await d.filas();
    const lineas = [d.campos.map(c => c[0]).join(',')].concat(filas.map(f => f.map(dlCeldaCSV).join(',')));
    lineas.push('');
    lineas.push(dlCeldaCSV('Fuente: ' + d.fuente + '. Descargado de Auditavisión el ' + new Date().toLocaleDateString('es-MX') + '.'));
    const blob = new Blob(['﻿' + lineas.join('\r\n')], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'auditavision-' + id + '.csv';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  }

  const capEstado = {};

  const cpEstado = { entidad: 'Aguascalientes', metrica: 'porAclarar' };

  const CP_METRICAS = [
    { k: 'porAclarar', et: 'Por aclarar', mdp: true },
    { k: 'observado', et: 'Observado', mdp: true },
    { k: 'recuperaciones', et: 'Recuperado', mdp: true },
    { k: 'auditorias', et: 'Auditorías', mdp: false },
    { k: 'PO', et: 'Pliegos', mdp: false }
  ];

  function cpSerieHtml() {
    const S = (DB.cuenta_publica_asf && DB.cuenta_publica_asf.serie) || [];
    if (!S.length) return '<p class="pd-nota">' + chipEstado('pendiente') + ' La base no trae la serie histórica.</p>';
    const m = CP_METRICAS.find(x => x.k === cpEstado.metrica) || CP_METRICAS[0];
    const max = Math.max.apply(null, S.map(r => r[m.k] || 0));
    return '<div class="cp-metricas" role="group" aria-label="Qué cifra comparar">' + CP_METRICAS.map(x =>
        '<button type="button" class="chip' + (x === m ? ' on active' : '') + '" aria-pressed="' + (x === m) + '" onclick="window.AuditEngine.cpSerieMetrica(\'' + x.k + '\')">' + x.et + '</button>').join('') + '</div>' +
      S.map(r => {
        const v = r[m.k] || 0;
        const est = (m.k === 'observado') ? r.observadoEstado : 'oficial';
        return '<div class="pd-fila cp-serie-fila"><span>CP ' + r.cp + ' <small>' + cpFuente(r.fuente, r.pagina) + '</small></span>' +
          pdBarra(v, max) + '<span class="num-tabular">' + (m.mdp ? pdMdp(v) : amNum(v)) + ' ' + chipEstado(est) + '</span></div>';
      }).join('');
  }

  function cpSerieMetrica(k) {
    cpEstado.metrica = k;
    const cont = document.getElementById('cpSerie');
    if (cont) cont.innerHTML = cpSerieHtml();
  }

  function cpFuente(clave, pagina) {
    const C = DB.cuenta_publica_asf;
    const f = C && C.fuentes[clave];
    if (!f) return '<span class="pd-fuente">' + chipEstado('pendiente') + ' fuente por documentar</span>';
    const pag = (pagina === undefined || pagina === null || pagina === '') ? '' :
      (/^\d+$/.test(String(pagina)) ? ', p. ' + pagina : (/^\d/.test(String(pagina)) ? ', pp. ' : ', ') + pagina);
    return '<a class="pd-fuente no-autolink" href="' + pdEsc(f.url) + '" target="_blank" rel="noopener noreferrer" title="' +
      pdEsc(f.doc) + '">' + pdEsc(f.corto || f.doc) + pdEsc(pag) + ' ↗</a>';
  }

  function cpMinus(t) { return t.charAt(0).toLowerCase() + t.slice(1); }

  function cpNombre(n) { return n === 'México' ? 'Estado de México' : n; }

  function cpMonto(p) {
    if (Math.abs(p) >= 1e12) return '$' + (p / 1e12).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' billones';
    return pdMdp(p);
  }

  function cpFecha(iso) {
    const [y, m, d] = iso.split('-').map(Number);
    return new Date(y, m - 1, d).toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' });
  }

  function cpDias(iso) {
    const [y, m, d] = iso.split('-').map(Number);
    const hoy = new Date(); hoy.setHours(0, 0, 0, 0);
    return Math.round((new Date(y, m - 1, d) - hoy) / 86400000);
  }

  function cpEntidadHtml() {
    const C = DB.cuenta_publica_asf;
    const lista = C.cp2024.entidades;
    const e = lista.find(x => x.entidad === cpEstado.entidad) || lista[0];
    const orden = lista.slice().sort((a, b) => b.total.porAclarar - a.total.porAclarar);
    const pos = orden.indexOf(e) + 1;
    const max = orden[0].total.porAclarar;
    const t = e.total;
    return '<div class="cp-ent-cab">' +
        tuUd('<label for="cpEntSel">Elija su estado</label>', '<label for="cpEntSel">Elige tu estado</label>') +
        '<select id="cpEntSel" onchange="window.AuditEngine.cpElegirEntidad(this.value)">' +
          lista.map(x => '<option value="' + pdEsc(x.entidad) + '"' + (x === e ? ' selected' : '') + '>' + pdEsc(cpNombre(x.entidad)) + '</option>').join('') +
        '</select>' +
      '</div>' +
      '<div class="am-datos">' +
        amTarjeta(amNum(t.auditorias), 'auditorías al dinero federal que recibió', 'derivado') +
        amTarjeta(amNum(t.acciones), 'acciones promovidas', 'derivado', amNum(t.PO) + ' pliegos de observaciones y ' + amNum(t.PRAS) + ' promociones de responsabilidad') +
        amTarjeta(pdMdp(t.porAclarar), 'por aclarar', 'derivado', 'Lugar ' + pos + ' de 32') +
        amTarjeta(pdMdp(t.recuperaciones), 'recuperados durante la auditoría', 'derivado') +
      '</div>' +
      '<div class="pd-tabla-w"><table class="pd-tabla"><thead><tr><th>Quién gastó</th><th>Auditorías</th><th>Acciones</th><th>Por aclarar</th><th>Recuperado</th></tr></thead><tbody>' +
        e.desglose.map(d => '<tr><td>' + pdEsc(d.ente) + '</td><td class="num-tabular">' + amNum(d.auditorias) + '</td><td class="num-tabular">' + amNum(d.acciones) +
          '</td><td class="num-tabular">' + pdMdp(d.porAclarar) + '</td><td class="num-tabular">' + pdMdp(d.recuperaciones) + '</td></tr>').join('') +
      '</tbody></table></div>' +
      '<p class="pd-nota">' + chipEstado('oficial') + ' Cada renglón: ' + cpFuente('MDB2024', C.cp2024.paginaEntidades) + '. ' + chipEstado('derivado') +
        ' Los totales del estado suman sus tres renglones. «Otros» agrupa organismos, universidades y demás entes locales que recibieron dinero federal.</p>' +
      '<h4 class="cp-sub">Los 32 estados, por monto por aclarar</h4>' +
      '<div class="cp-ranking">' + orden.map((x, i) =>
        '<button type="button" class="pd-fila cp-rank' + (x === e ? ' cp-rank-sel' : '') + '" onclick="window.AuditEngine.cpElegirEntidad(\'' + pdEsc(x.entidad).replace(/'/g, '\\\'') + '\')">' +
          '<span>' + (i + 1) + '. ' + pdEsc(cpNombre(x.entidad)) + '</span>' + pdBarra(x.total.porAclarar, max, x === e ? 'cp-barra-sel' : '') +
          '<span class="num-tabular">' + pdMdp(x.total.porAclarar) + '</span></button>').join('') +
      '</div>';
  }

  function cpElegirEntidad(nombre) {
    cpEstado.entidad = nombre;
    const cont = document.getElementById('cpEntidad');
    if (cont) cont.innerHTML = cpEntidadHtml();
  }

  function renderCuentaPublica() {
    const raiz = document.getElementById('cpRaiz');
    const C = DB.cuenta_publica_asf;
    if (!raiz) return;
    if (!C) {
      raiz.innerHTML = '<p class="pd-nota">' + chipEstado('pendiente') + ' La base de datos no trae la colección de la Cuenta Pública.</p>';
      return;
    }
    const T = C.cp2024.total, F = C.cp2024.federalizado, N = C.cp2025;
    const cal = C.calendario.map(c => Object.assign({}, c, { hecho: cpDias(c.fecha) <= 0 }));
    const prox = cal.find(c => !c.hecho);
    const dias = prox ? cpDias(prox.fecha) : null;
    const fedPct = F.porAclarar / T.porAclarar * 100;

    /* 1. Que es y cuando se revisa */
    const calendario =
      '<section class="pd-bloque">' +
        '<h3 class="pd-tit">🗓️ Qué es la Cuenta Pública y cuándo se revisa</h3>' +
        '<p class="pd-lead">El presupuesto dice cuánto se <b>puede</b> gastar. La <b>Cuenta Pública</b> dice cuánto se gastó de verdad: es el informe contable, presupuestario y programático de los tres Poderes, los órganos autónomos y las empresas del Estado. Hacienda la entrega a la Cámara de Diputados y la <b>Auditoría Superior de la Federación (ASF)</b> la revisa en tres entregas.</p>' +
        (prox ? '<div class="cp-cuenta"><span class="num-tabular">' + dias + '</span><div><b>' + (dias === 1 ? 'día' : 'días') + ' para la ' + pdEsc(cpMinus(prox.titulo)) + '</b><small>' + cpFecha(prox.fecha) + ' · ' + pdEsc(prox.fundamento || '') + ' ' + chipEstado('derivado') + '</small></div></div>' : '') +
        '<ol class="cp-linea">' + cal.map(c =>
          '<li class="' + (c.hecho ? 'cp-hecho' : (c === prox ? 'cp-prox' : '')) + '">' +
            '<span class="cp-fecha">' + cpFecha(c.fecha) + '</span>' +
            '<b>' + pdEsc(c.titulo) + '</b>' +
            '<span>' + pdEsc(c.texto) + '</span>' +
            (c.fundamento ? '<small>' + cpFuente(c.fuente, '') + ' · ' + pdEsc(c.fundamento) + '</small>' : '') +
          '</li>').join('') + '</ol>' +
        '<p class="pd-nota">Los datos de la Cuenta Pública de cada año están en el ' + cpFuente('CPSHCP') + '. Las fechas son las que fija la ley; si la Cámara concede prórroga a Hacienda, la ASF recorre las suyas (CPEUM, art. 74, fr. VI).</p>' +
      '</section>';

    /* 2. La Cuenta Publica 2024 en cifras */
    const acc = ['R', 'RD', 'PEFCF', 'SA', 'PRAS', 'PO'];
    const cifras =
      '<section class="pd-bloque">' +
        '<h3 class="pd-tit">🔎 Lo que encontró la ASF en la Cuenta Pública 2024</h3>' +
        '<p class="pd-lead">Es el ejercicio más reciente con sus tres entregas completas (corte: ' + pdEsc(C.cp2024.corte) + ').</p>' +
        '<div class="am-datos">' +
          amTarjeta(amNum(T.auditorias), 'auditorías practicadas', 'oficial') +
          amTarjeta(cpMonto(T.muestra), 'revisados, de ' + cpMonto(T.universo) + ' seleccionados', 'oficial', pdPct(T.representatividad, 2) + ' de lo seleccionado') +
          amTarjeta(amNum(T.acciones), 'acciones promovidas', 'oficial') +
          amTarjeta(pdMdp(T.porAclarar), 'por aclarar', 'oficial', 'Sin documentos que acreditaran el gasto al cierre de la auditoría') +
          amTarjeta(pdMdp(T.recuperaciones), 'recuperados durante la auditoría', 'oficial', 'Dinero efectivamente reintegrado') +
        '</div>' +
        '<h4 class="cp-sub">Las ' + amNum(T.acciones) + ' acciones, por tipo</h4>' +
        '<div class="cp-pila" role="img" aria-label="Acciones por tipo">' + acc.map(k =>
          '<span class="cp-pila-' + k + '" style="flex:' + T[k] + '" title="' + k + ': ' + amNum(T[k]) + '"></span>').join('') + '</div>' +
        '<ul class="cp-leyenda">' + acc.map(k => {
          const a = C.acciones.find(x => x.clave === k);
          return '<li><i class="cp-pila-' + k + '"></i><b>' + k + '</b> ' + pdEsc(a.nombre) + ' <span class="num-tabular">' + amNum(T[k]) + '</span></li>';
        }).join('') + '</ul>' +
        '<p class="pd-nota">' + chipEstado('oficial') + ' ' + cpFuente('MDB2024', C.cp2024.pagina) + '. Los informes individuales, uno por auditoría, están en el ' + cpFuente('IR2024') + '.</p>' +
        '<div class="am-alerta"><b>Por aclarar no es lo mismo que robado.</b> ' + pdEsc(C.nota.split('. ').slice(2).join('. ')) + '</div>' +
      '</section>';

    /* 2 bis. Seis años de revisiones */
    const S = C.serie || [];
    const sObs = S.reduce((a, r) => a + r.observado, 0), sRec = S.reduce((a, r) => a + r.recuperaciones, 0);
    const serie = !S.length ? '' :
      '<section class="pd-bloque">' +
        '<h3 class="pd-tit">📈 Seis años de revisiones: ' + S[0].cp + ' a ' + S[S.length - 1].cp + '</h3>' +
        '<p class="pd-lead">Cada renglón es el total de la matriz consolidada de una Cuenta Pública, con su documento y su página. En esos seis años la ASF observó ' + pdMdp(sObs) + ' y, durante las propias auditorías, se recuperaron ' + pdMdp(sRec) + ': el <b>' + pdPct(sRec / sObs * 100) + '</b>. ' + chipEstado('derivado') + '</p>' +
        '<div id="cpSerie">' + cpSerieHtml() + '</div>' +
        '<p class="pd-nota"><b>Cómo leerla.</b> Observado = recuperado + por aclarar. Desde la Cuenta Pública 2023 la matriz ya no publica el total observado: para 2023 y 2024 se suma y se marca ' + chipEstado('derivado') + '. Los montos están en pesos de cada año, sin ajustar por inflación, y el «por aclarar» es el del corte de cada matriz: lo que se solventó después no aparece aquí. La matriz de la Cuenta Pública 2018 no está publicada en el portal de la ASF ' + chipEstado('pendiente') + ': queda pendiente hasta que la ASF la transparente.</p>' +
      '</section>';

    /* 3. Donde se concentra */
    const grupos = C.cp2024.grupos;
    const maxG = Math.max.apply(null, grupos.map(g => g.subtotal.porAclarar));
    const sectores = [];
    grupos.forEach(g => g.sectores.forEach(s => sectores.push(Object.assign({ grupo: g.grupo }, s))));
    const top = sectores.filter(s => s.porAclarar > 0).sort((a, b) => b.porAclarar - a.porAclarar).slice(0, 10);
    const donde =
      '<section class="pd-bloque">' +
        '<h3 class="pd-tit">🏛️ Dónde se concentra lo que falta aclarar</h3>' +
        '<p class="pd-lead">El <b>' + pdPct(fedPct) + '</b> de lo que quedó por aclarar está en el <b>gasto federalizado</b>: el dinero federal que reciben estados y municipios (' + pdMdp(F.porAclarar) + ' en ' + amNum(F.auditorias) + ' auditorías). ' + chipEstado('derivado') + '</p>' +
        grupos.map(g => '<div class="pd-fila"><span>' + pdEsc(g.grupo) + ' <small>' + amNum(g.subtotal.auditorias) + ' auditorías</small></span>' +
          pdBarra(g.subtotal.porAclarar, maxG) + '<span class="num-tabular">' + pdMdp(g.subtotal.porAclarar) + '</span></div>').join('') +
        '<h4 class="cp-sub">Los diez renglones con más monto por aclarar</h4>' +
        top.map(s => '<div class="pd-fila"><span>' + pdEsc(s.nombre) + ' <small>' + pdEsc(s.grupo) + '</small></span>' +
          pdBarra(s.porAclarar, top[0].porAclarar) + '<span class="num-tabular">' + pdMdp(s.porAclarar) + '</span></div>').join('') +
        '<p class="pd-nota">' + chipEstado('oficial') + ' ' + cpFuente('MDB2024', '11 a 14') + '. En el gasto federalizado la ASF agrupa por tema de fiscalización (educación, salud, participaciones…), no por dependencia. Porcentaje: ' + chipEstado('derivado') + ' por aclarar del grupo ÷ total.</p>' +
      '</section>';

    /* 4. Su estado */
    const estado =
      '<section class="pd-bloque">' +
        '<h3 class="pd-tit">🗺️ Lo que la ASF le observó a tu estado</h3>' +
        '<p class="pd-lead">El dinero federal que llega a cada estado lo revisa la ASF en tres niveles: el gobierno del estado, sus municipios (alcaldías en la Ciudad de México) y otros entes locales. Aparte, ' + amNum(C.cp2024.coordinadoras.auditorias) + ' auditorías se hicieron a las dependencias federales que coordinan esos fondos.</p>' +
        '<div id="cpEntidad">' + cpEntidadHtml() + '</div>' +
      '</section>';

    /* 5. Que significa cada accion y que sigue */
    const acciones =
      '<section class="pd-bloque">' +
        '<h3 class="pd-tit">⚖️ Qué significa cada acción y qué pasa después</h3>' +
        '<p class="pd-lead">Una observación no es una sentencia. Cada acción abre un camino distinto y con plazos que marca la ley.</p>' +
        '<div class="cp-acciones">' + C.acciones.map(a =>
          '<div class="cp-accion cp-acc-' + a.tipo + '"><span class="cp-clave">' + a.clave + '</span><b>' + pdEsc(a.nombre) + '</b><p>' + pdEsc(a.que) + '</p><small>' + pdEsc(a.fundamento) + ' · ' + a.tipo + '</small></div>').join('') + '</div>' +
        '<h4 class="cp-sub">El reloj de la ley después de cada entrega</h4>' +
        '<ol class="cp-plazos">' + C.plazos.map(p => '<li><b class="num-tabular">' + pdEsc(p.plazo) + '</b> ' + pdEsc(p.que) + ' <small>' + pdEsc(p.fundamento) + '</small></li>').join('') + '</ol>' +
        '<p class="pd-nota">' + chipEstado('oficial') + ' ' + cpFuente('LFRCF', 'arts. 33 a 42') + '. Cuando un pliego no se solventa, el caso pasa a investigación y, si hay falta grave, al Tribunal Federal de Justicia Administrativa; si hay delito, a la Fiscalía Especializada (LFRCF, art. 40).</p>' +
      '</section>';

    /* 6. La Cuenta Publica 2025 */
    const nueva =
      '<section class="pd-bloque">' +
        '<h3 class="pd-tit">🆕 La Cuenta Pública 2025: lo que ya salió</h3>' +
        '<p class="pd-lead">La primera entrega (' + pdEsc(N.corte) + ') revisó un solo tema: <b>cómo se repartieron las participaciones federales</b>, el dinero de libre uso que la Federación entrega a los estados. ' + pdEsc(N.que) + '</p>' +
        '<div class="am-datos">' +
          amTarjeta(amNum(N.auditorias), 'auditorías', N.estado) +
          amTarjeta(cpMonto(N.muestra), 'revisados', N.estado, pdPct(N.representatividad, 0) + ' del universo') +
          amTarjeta(amNum(N.acciones), 'acciones', N.estado, amNum(N.R) + ' recomendaciones y ' + amNum(N.SA) + ' solicitud de aclaración') +
          amTarjeta(pdPesos(N.porAclarar), 'por aclarar', N.estado) +
          amTarjeta(pdPesos(N.recuperaciones), 'recuperados', N.estado) +
        '</div>' +
        '<p class="pd-nota">' + chipEstado('oficial') + ' ' + cpFuente(N.fuente, N.pagina) + '. Los 33 informes, en el ' + cpFuente('IR2025A') + '. ' +
          (prox ? 'Lo que viene: la ' + pdEsc(cpMinus(prox.titulo)) + ', el ' + cpFecha(prox.fecha) + '.' : '') + '</p>' +
      '</section>';

    /* 7. Fuentes y descarga */
    const fuentes =
      '<section class="pd-bloque">' +
        '<h3 class="pd-tit">📚 Documentos y descarga</h3>' +
        tuUd('<p class="pd-lead">Cada cifra de esta sección sale de estos documentos. Puede bajarlos y comprobarlos, o descargar la base por estado para abrirla en Excel.</p>', '<p class="pd-lead">Cada cifra de esta sección sale de estos documentos. Puedes bajarlos y comprobarlos, o descargar la base por estado para abrirla en Excel.</p>') +
        '<div class="cp-botones">' +
          '<button type="button" class="hero-pillar-btn hero-pillar-calc" onclick="window.AuditEngine.descargarCSV(\'asf-cp2024\')">⬇️ CSV por estado</button>' +
          '<a class="hero-pillar-btn hero-pillar-audit no-autolink" href="' + pdEsc(C.fuentes.ASFDATOS.url) + '" target="_blank" rel="noopener noreferrer">🔎 Buscar una auditoría en ASF Datos ↗</a>' +
          '<a class="hero-pillar-btn" href="fuentes-oficiales.html">📑 Ver en el Catálogo de Fuentes</a>' +
        '</div>' +
        '<ol class="pd-docs">' + Object.keys(C.fuentes).map(k => {
          const f = C.fuentes[k];
          return '<li><a class="no-autolink" href="' + pdEsc(f.url) + '" target="_blank" rel="noopener noreferrer">' + pdEsc(f.doc) + ' ↗</a>' +
            (f.sha256 ? '<code title="SHA-256">' + f.sha256.slice(0, 16) + '…</code>' : '') + '</li>';
        }).join('') + '</ol>' +
        '<p class="pd-nota">' + pdEsc(C.nota) + ' Consulta: ' + pdEsc(C.consulta) + '.</p>' +
      '</section>';

    raiz.innerHTML = calendario + cifras + serie + donde + estado + acciones + nueva + fuentes;
    raiz.querySelectorAll('.am-dato, .cp-linea, .cp-cuenta, .pd-tabla-w, .cp-ranking, .pd-docs, .cp-leyenda, .cp-accion b, .cp-ent-cab')
      .forEach(el => el.setAttribute('data-no-autolink', ''));
    capMontar(raiz, 'cuentapublica', [
      { ico: '🗓️', tit: 'Qué es y cuándo se revisa', cifra: prox ? dias + ' días' : '', cifraPie: prox ? 'para la siguiente entrega' : '', estado: prox ? 'derivado' : '', res: 'El calendario que fija la ley, de Hacienda a la ASF.' },
      { ico: '🔎', tit: 'La Cuenta Pública 2024 en cifras', cifra: amNum(T.auditorias), cifraPie: 'auditorías', estado: 'oficial', res: 'Lo revisado, las acciones y lo que falta aclarar.' },
      S.length ? { ico: '📈', tit: 'Seis años de revisiones', cifra: S.length + ' años', cifraPie: 'de matrices oficiales', estado: 'oficial', res: 'Lo observado, lo recuperado y lo por aclarar, de ' + S[0].cp + ' a ' + S[S.length - 1].cp + '.' } : null,
      { ico: '🏛️', tit: 'Dónde se concentra', cifra: pdPct(fedPct, 0), cifraPie: 'en estados y municipios', estado: 'derivado', res: 'Por grupo de gasto y los diez renglones más altos.' },
      { ico: '🗺️', tit: 'Su estado', cifra: '32', cifraPie: 'estados comparados', estado: 'oficial', res: 'Gobierno, municipios y otros entes, con su lugar nacional.' },
      { ico: '⚖️', tit: 'Qué significa cada acción', cifra: amNum(T.PO), cifraPie: 'pliegos de observaciones', estado: 'oficial', res: 'De la recomendación al pliego, y los plazos de la ley.' },
      { ico: '🆕', tit: 'La Cuenta Pública 2025', cifra: amNum(N.auditorias), cifraPie: 'auditorías en la 1.ª entrega', estado: 'oficial', res: 'Lo que ya publicó la ASF y lo que viene.' },
      { ico: '📚', tit: 'Documentos y descarga', cifra: 'CSV', cifraPie: 'por estado', estado: '', res: 'Los PDF oficiales con su huella, y la base para Excel.' }
    ].filter(Boolean));
  }

  function capMontar(raiz, clave, caps) {
    const bloques = [...raiz.children].filter(el => !el.classList.contains('cap-indice') && !el.classList.contains('cap-nav'));
    if (!bloques.length || bloques.length !== caps.length) return;
    if (!capEstado[clave]) capEstado[clave] = { i: -1, todo: false };
    bloques.forEach((b, i) => { b.classList.add('cap-bloque'); b.dataset.cap = i; });

    const indice = document.createElement('nav');
    indice.className = 'cap-indice';
    indice.setAttribute('aria-label', 'Capítulos de esta sección');
    indice.setAttribute('data-no-autolink', '');
    indice.innerHTML =
      '<div class="cap-indice-cab"><span>' + caps.length + tuUd(' capítulos · elija por dónde empezar</span>', ' capítulos · elige por dónde empezar</span>') +
        '<button type="button" class="cap-todo" onclick="window.AuditEngine.capTodo(\'' + clave + '\')">Leer todo de corrido</button></div>' +
      '<div class="cap-tarjetas">' + caps.map((c, i) =>
        '<button type="button" class="cap-tarjeta" data-i="' + i + '" onclick="window.AuditEngine.capIr(\'' + clave + '\',' + i + ')">' +
          '<span class="cap-num">' + String(i + 1).padStart(2, '0') + '</span>' +
          '<span class="cap-ico" aria-hidden="true">' + c.ico + '</span>' +
          '<span class="cap-tit">' + escHtml(c.tit) + '</span>' +
          (c.cifra ? '<span class="cap-cifra num-tabular">' + escHtml(c.cifra) + '</span>' : '') +
          (c.cifraPie ? '<span class="cap-cifra-pie">' + escHtml(c.cifraPie) + (c.estado ? ' ' + chipEstado(c.estado) : '') + '</span>' : '') +
          '<span class="cap-res">' + escHtml(c.res) + '</span>' +
        '</button>').join('') + '</div>';

    const nav = document.createElement('div');
    nav.className = 'cap-nav';
    nav.setAttribute('data-no-autolink', '');

    raiz.insertBefore(indice, raiz.firstChild);
    raiz.appendChild(nav);
    raiz.dataset.capClave = clave;
    capEstado[clave].raiz = raiz;
    capEstado[clave].caps = caps;
    capPintar(clave, false);
  }

  function capPintar(clave, desplazar) {
    const e = capEstado[clave];
    if (!e || !e.raiz) return;
    const raiz = e.raiz, n = e.caps.length;
    raiz.classList.toggle('cap-modo-todo', e.todo);
    raiz.classList.toggle('cap-modo-indice', !e.todo && e.i < 0);
    raiz.querySelectorAll('.cap-bloque').forEach(b => { b.hidden = !e.todo && +b.dataset.cap !== e.i; });
    raiz.querySelectorAll('.cap-tarjeta').forEach(t => {
      const act = +t.dataset.i === e.i && !e.todo;
      t.classList.toggle('activa', act);
      if (act) t.setAttribute('aria-current', 'step'); else t.removeAttribute('aria-current');
    });
    const btnTodo = raiz.querySelector('.cap-todo');
    if (btnTodo) btnTodo.textContent = e.todo ? 'Leer por capítulos' : 'Leer todo de corrido';
    const nav = raiz.querySelector('.cap-nav');
    if (e.todo || e.i < 0) { nav.innerHTML = ''; }
    else {
      const ant = e.i > 0 ? e.caps[e.i - 1] : null, sig = e.i < n - 1 ? e.caps[e.i + 1] : null;
      nav.innerHTML =
        '<div class="cap-avance" aria-hidden="true"><i style="width:' + ((e.i + 1) / n * 100).toFixed(1) + '%"></i></div>' +
        '<div class="cap-nav-fila">' +
          (ant ? '<button type="button" class="cap-btn" onclick="window.AuditEngine.capIr(\'' + clave + '\',' + (e.i - 1) + ')">← ' + escHtml(ant.tit) + '</button>' : '<span></span>') +
          '<span class="cap-paso">Capítulo ' + (e.i + 1) + ' de ' + n + '</span>' +
          (sig ? '<button type="button" class="cap-btn cap-btn-sig" onclick="window.AuditEngine.capIr(\'' + clave + '\',' + (e.i + 1) + ')">Siguiente: ' + escHtml(sig.tit) + ' →</button>'
               : '<button type="button" class="cap-btn" onclick="window.AuditEngine.capIr(\'' + clave + '\',-1)">Volver al índice ↑</button>') +
        '</div>';
    }
    if (desplazar) {
      const destino = (e.todo || e.i < 0) ? raiz.querySelector('.cap-indice') : raiz.querySelector('.cap-bloque[data-cap="' + e.i + '"]');
      if (destino) setTimeout(() => destino.scrollIntoView({ behavior: 'smooth', block: 'start' }), 30);
    }
  }

  function capIr(clave, i) {
    const e = capEstado[clave];
    if (!e) return;
    e.todo = false;
    e.i = i;
    capPintar(clave, true);
  }

  function capTodo(clave) {
    const e = capEstado[clave];
    if (!e) return;
    e.todo = !e.todo;
    if (!e.todo && e.i < 0) e.i = 0;
    capPintar(clave, true);
  }

  const EFOS_SIT = {
    F: { t: 'Definitivo', clase: 'efos-f', txt: 'El SAT determinó en definitiva que sus comprobantes amparan operaciones inexistentes. Esas facturas no tienen efectos fiscales para nadie (art. 69-B del CFF).' },
    P: { t: 'Presunto', clase: 'efos-p', txt: 'El SAT presume que sus operaciones son inexistentes y se lo notificó. Todavía puede desvirtuarlo: no es una determinación final.' },
    D: { t: 'Desvirtuado', clase: 'efos-d', txt: 'Demostró ante el SAT que sus operaciones sí existieron. Salió de la presunción.' },
    S: { t: 'Sentencia favorable', clase: 'efos-s', txt: 'Un tribunal le dio la razón frente al SAT. No se le considera EFOS.' }
  };

  function escHtml(v) {
    return String(v == null ? '' : v)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }


  /* ---------------------------------------------------------------
     Contenido de cada ficha
     --------------------------------------------------------------- */
  function dlArticulo(d, abierto) {
    return '<article class="dl-base" id="dl-' + d.id + '">' +
        '<div class="dl-base-cab"><h4>' + pdEsc(d.titulo) + '</h4>' +
          '<button type="button" class="hero-pillar-btn hero-pillar-calc" onclick="window.AuditEngine.descargarCSV(\'' + d.id + '\')">⬇️ CSV</button></div>' +
        '<p>' + pdEsc(d.desc) + '</p>' +
        '<p class="dl-fuente">Fuente: ' + pdEsc(d.fuente) + '</p>' +
        '<details' + (abierto ? ' open' : '') + '><summary>Diccionario: ' + d.campos.length + ' columnas</summary><table class="pd-tabla"><tbody>' +
          d.campos.map(c => '<tr><td><code>' + c[0] + '</code></td><td>' + pdEsc(c[1]) + '</td></tr>').join('') +
        '</tbody></table></details>' +
      '</article>';
  }

  function fichaDescargas() {
    return '<p class="dl-intro">Cada base se descarga en CSV y abre directo en Excel, con acentos. Al final del archivo va su fuente. Pulsa «Diccionario» para ver qué significa cada columna.</p>' +
      DESCARGAS.map(d => dlArticulo(d, false)).join('');
  }

  function fichaDiccionario() {
    return '<p class="dl-intro">Qué contiene cada archivo de datos de la plataforma, columna por columna. Cada base se descarga en CSV con el botón de su renglón y lleva su fuente al final del archivo.</p>' +
      DESCARGAS.map(d => dlArticulo(d, true)).join('');
  }

  /* Base municipal: la descarga completa y una consulta por estado, con
     las mismas cifras del INEGI que trae el CSV. */
  const munEstado = { ent: null };
  /* Nombres del Catálogo Único de Claves Geoestadísticas del INEGI, por clave. */
  const ENTIDADES = { '01': 'Aguascalientes', '02': 'Baja California', '03': 'Baja California Sur', '04': 'Campeche',
    '05': 'Coahuila de Zaragoza', '06': 'Colima', '07': 'Chiapas', '08': 'Chihuahua', '09': 'Ciudad de México', '10': 'Durango',
    '11': 'Guanajuato', '12': 'Guerrero', '13': 'Hidalgo', '14': 'Jalisco', '15': 'Estado de México', '16': 'Michoacán de Ocampo',
    '17': 'Morelos', '18': 'Nayarit', '19': 'Nuevo León', '20': 'Oaxaca', '21': 'Puebla', '22': 'Querétaro', '23': 'Quintana Roo',
    '24': 'San Luis Potosí', '25': 'Sinaloa', '26': 'Sonora', '27': 'Tabasco', '28': 'Tamaulipas', '29': 'Tlaxcala',
    '30': 'Veracruz de Ignacio de la Llave', '31': 'Yucatán', '32': 'Zacatecas' };
  function munTabla() {
    const M = window.AUDIT_MUNICIPIOS;
    const e = M.ent[munEstado.ent];
    const filas = e.lista.map(m => m.length <= 2
      ? '<tr><td>' + pdEsc(m[1]) + '</td><td colspan="4" class="dt-sin">Sin reporte 2024 ' + chipEstado('pendiente') + '</td></tr>'
      : '<tr><td>' + pdEsc(m[1]) + '</td><td class="num-tabular">' + pdMdp(m[2]) + '</td><td class="num-tabular">' + pdMdp(m[3]) +
        '</td><td class="num-tabular">' + pdMdp(m[4]) + '</td><td class="num-tabular">' + pdMdp(m[7]) + '</td></tr>').join('');
    return '<p class="pd-nota">' + amNum(e.n) + ' municipios; ' + amNum(e.conCifra) + ' rindieron cuenta al INEGI en 2024. ' + chipEstado('oficial') + '</p>' +
      '<div class="pd-tabla-w"><table class="pd-tabla"><thead><tr><th>Municipio</th><th>Ingreso total</th><th>Participaciones</th><th>Aportaciones</th><th>Predial</th></tr></thead><tbody>' +
      filas + '</tbody></table></div>';
  }
  function munElegir(abbr) {
    munEstado.ent = abbr;
    const c = document.getElementById('dtMunTabla');
    if (c) c.innerHTML = munTabla();
  }
  function fichaMunicipios() {
    const M = window.AUDIT_MUNICIPIOS;
    const d = DESCARGAS.find(x => x.id === 'municipios');
    if (!M) return '<p class="pd-nota">' + chipEstado('pendiente') + ' No cargó el padrón municipal: recarga la página. Es una falla de la plataforma, no de la fuente.</p>' + dlArticulo(d, true);
    const claves = Object.keys(M.ent).sort((a, b) => M.ent[a].cve.localeCompare(M.ent[b].cve));
    if (!munEstado.ent) munEstado.ent = claves[0];
    return dlArticulo(d, false) +
      '<h4 class="cp-sub">Consulta un estado sin descargar nada</h4>' +
      '<div class="cp-ent-cab"><label for="dtMunSel">Elige el estado</label>' +
        '<select id="dtMunSel" onchange="window.AuditEngine.munElegir(this.value)">' +
          claves.map(k => '<option value="' + k + '"' + (k === munEstado.ent ? ' selected' : '') + '>' + pdEsc(ENTIDADES[M.ent[k].cve] || k) + '</option>').join('') +
        '</select></div>' +
      '<div id="dtMunTabla">' + munTabla() + '</div>' +
      '<p class="pd-nota">' + chipEstado('oficial') + ' ' + pdEsc(M.fuente) + ' <a class="pd-fuente" href="' + pdEsc(M.url) + '" target="_blank" rel="noopener noreferrer">INEGI ↗</a>. Montos en millones de pesos de 2024, sin ajustar por inflación.</p>';
  }

  function fichaCuentaPublica() {
    return '<div class="cp-seccion" id="cuentaPublicaASF"><div id="cpRaiz"></div></div>';
  }

  const FICHAS = {
    descargas: { html: fichaDescargas },
    municipios: { html: fichaMunicipios },
    asf: { html: fichaCuentaPublica, luego: renderCuentaPublica },
    diccionario: { html: fichaDiccionario }
  };

  /* ---------------------------------------------------------------
     Despliegue: como el visor de las otras páginas, debajo de la fila
     de la ficha. Una ficha abierta a la vez por pestaña.
     --------------------------------------------------------------- */
  function ultimaDeSuFila(t) {
    let fila = t;
    t.parentNode.querySelectorAll('.dt-ficha').forEach(o => { if (o.offsetTop === t.offsetTop) fila = o; });
    return fila;
  }

  function cerrarFicha(t, devolverFoco) {
    const panel = document.getElementById('dtp-' + t.dataset.ficha);
    if (panel) panel.remove();
    t.setAttribute('aria-expanded', 'false');
    t.classList.remove('apartado-tarjeta-abierta');
    if (devolverFoco) t.focus({ preventScroll: true });
  }

  function abrirFicha(t, desplazar) {
    const rejilla = t.parentNode;
    rejilla.querySelectorAll('.dt-ficha[aria-expanded="true"]').forEach(o => cerrarFicha(o, false));
    const id = t.dataset.ficha, f = FICHAS[id];
    if (!f) return;
    t.setAttribute('aria-expanded', 'true');
    t.classList.add('apartado-tarjeta-abierta');
    const panel = document.createElement('div');
    panel.className = 'apartado-visor dt-panel';
    panel.id = 'dtp-' + id;
    panel.setAttribute('role', 'region');
    const nombre = t.querySelector('.apartado-tarjeta-nombre').textContent.trim();
    panel.setAttribute('aria-label', nombre);
    const c = getComputedStyle(t).getPropertyValue('--tarjeta');
    if (c) panel.style.setProperty('--tarjeta', c.trim());
    panel.innerHTML =
      '<div class="apartado-visor-cab">' +
        '<span class="apartado-visor-tit" tabindex="-1">' + pdEsc(t.querySelector('.apartado-tarjeta-icono').textContent + ' ' + nombre) + '</span>' +
        '<button type="button" class="apartado-visor-b apartado-visor-cerrar">✕ Cerrar</button>' +
      '</div>' +
      '<div class="dt-cuerpo">' + f.html() + '</div>';
    panel.querySelector('.apartado-visor-cerrar').addEventListener('click', () => cerrarFicha(t, true));
    const tras = ultimaDeSuFila(t);
    tras.parentNode.insertBefore(panel, tras.nextSibling);
    if (f.luego) f.luego();
    if (desplazar) {
      document.body.classList.add('cabecera-compacta');
      const nav = document.querySelector('.site-top-nav');
      const alto = nav ? nav.getBoundingClientRect().height : 0;
      setTimeout(() => {
        window.scrollTo({ top: Math.max(0, panel.getBoundingClientRect().top + window.pageYOffset - alto - 8), behavior: 'smooth' });
        const tit = panel.querySelector('.apartado-visor-tit');
        if (tit) tit.focus({ preventScroll: true });
      }, 30);
    }
  }

  document.addEventListener('click', e => {
    const t = e.target.closest && e.target.closest('.dt-ficha');
    if (!t) return;
    e.preventDefault();
    if (t.getAttribute('aria-expanded') === 'true') cerrarFicha(t, false); else abrirFicha(t, true);
  });

  /* #ficha-asf (o cualquier #ficha-<id>) abre su pestaña y su ficha: así
     enlaza el radar a los Informes de la Cuenta Pública. */
  function abrirDesdeAncla() {
    const m = location.hash.match(/^#ficha-([\w-]+)$/);
    if (!m) return;
    const t = document.querySelector('.dt-ficha[data-ficha="' + m[1] + '"]');
    if (!t) return;
    const panel = t.closest('[role="tabpanel"]');
    const pest = panel && document.getElementById('pestana-' + panel.id);
    if (pest && panel.hidden) pest.click();
    if (t.getAttribute('aria-expanded') !== 'true') abrirFicha(t, true);
  }
  window.addEventListener('hashchange', abrirDesdeAncla);
  window.addEventListener('load', () => setTimeout(abrirDesdeAncla, 400));

  window.AuditEngine = Object.assign(window.AuditEngine || {}, {
    descargarCSV: descargarCSV,
    cpSerieMetrica: cpSerieMetrica,
    cpElegirEntidad: cpElegirEntidad,
    capIr: capIr,
    capTodo: capTodo,
    munElegir: munElegir
  });
})();
