/* =========================================================================
   Biblioteca del auditor (09-10-2026): las Preguntas frecuentes, el Marco
   legal y el Catálogo de fuentes en páginas propias. Antes se abrían en un
   marco con la portada entera (motor, mapas y padrón municipal, unos 4 MB)
   solo para mostrar texto, y el lector se quedaba viendo «Cargando el
   módulo». Aquí se leen directo de window.AUDIT_DB, la misma base del
   auditor, como el glosario (glosario.js).

   Cada página trae su raíz: #bibPreguntas, #bibMarco o #bibFuentes.
   Anclas: preguntas-frecuentes.html#p-<casilla>-<n>,
   marco-legal.html#precepto-<id>, fuentes-oficiales.html#ref-<id>.
   ========================================================================= */
(function () {
  'use strict';
  var DB = window.AUDIT_DB;
  if (!DB) return;

  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function norm(s) { return String(s || '').replace(/<[^>]+>/g, ' ').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/\s+/g, ' ').trim(); }
  function chip(e) { var t = (e === 'oficial' || e === 'pendiente') ? e : 'derivado'; return '<span class="est-chip est-' + t + '">' + t + '</span>'; }
  function nf(n) { return Number(n).toLocaleString('es-MX'); }

  var REFS = {};
  (DB.referencias_legales || []).forEach(function (r) { REFS[r.id] = r; });
  /* El título corto de una ficha: lo que sigue al autor y al año en las
     citas «Autor. (2026). Título. Editor.», o al nombre de la institución
     que firma; si no hay ni uno ni otro, lo que va antes del primer punto. */
  function refCorto(r) {
    var c = String(r.cita_apa || '').replace(/<[^>]+>/g, '');
    var m = c.match(/^.{0,200}?\((?:[^()]*\d[^()]*|s\. f\.)\)\.\s+/) ||
      c.match(/^(?:Secretar[ií]a|Auditor[ií]a Superior|Instituto|Congreso|Suprema Corte|Ejecutivo Federal|Presidencia|C[aá]mara de|Comisi[oó]n|Servicio de Administraci|Banco de M|Consejo|[OÓ]rgano de|Poder Judicial|Fiscal[ií]a)[^.]*\.\s+/);
    if (m) c = c.slice(m[0].length);
    var t = c.match(/^(.{8,160}?)(?:(?<!\b(?:v|No))\.\s+(?=[A-ZÁÉÍÓÚÑ¿«\[(])|\s\[|\.?$)/);
    return t ? t[1] : c.slice(0, 140);
  }
  function refEnlace(id) {
    var r = REFS[id];
    if (!r) return '';
    return '<a class="bib-ref" href="fuentes-oficiales.html#' + esc(id) + '" title="' + esc(refCorto(r)) + '">[' + r.num + '] ' + esc(refCorto(r)) + '</a>';
  }

  /* La barra se queda pegada bajo la cabecera, que cambia de alto. */
  function pegarBarra(raiz) {
    function tope() {
      var nav = document.querySelector('.site-top-nav');
      raiz.style.setProperty('--gl-tope', (nav ? Math.max(0, nav.getBoundingClientRect().bottom) : 0) + 'px');
    }
    tope();
    window.addEventListener('scroll', tope, { passive: true });
    window.addEventListener('resize', tope);
  }

  function destacar(el) {
    if (!el) return;
    el.classList.add('bib-destacado');
    setTimeout(function () { el.classList.remove('bib-destacado'); }, 2600);
  }

  /* Filtro común: buscador + botones de grupo + cuenta. */
  function filtro(raiz, opts) {
    var busca = raiz.querySelector('.gl-busca input');
    var cuenta = raiz.querySelector('.gl-cuenta');
    var grupo = 'todas';
    function aplicar() {
      var q = norm(busca.value), n = 0;
      opts.fichas().forEach(function (f) {
        var ok = (grupo === 'todas' || f.getAttribute('data-grupo') === grupo) && (!q || f.getAttribute('data-q').indexOf(q) !== -1);
        f.hidden = !ok;
        if (ok) n++;
      });
      if (opts.despues) opts.despues(q, grupo);
      cuenta.textContent = n === 1 ? '1 ' + opts.singular : n + ' ' + opts.plural;
    }
    busca.addEventListener('input', aplicar);
    raiz.addEventListener('click', function (e) {
      var b = e.target.closest('[data-filtro]');
      if (!b) return;
      grupo = b.getAttribute('data-filtro');
      Array.prototype.forEach.call(raiz.querySelectorAll('[data-filtro]'), function (x) {
        var on = x.getAttribute('data-filtro') === grupo;
        x.classList.toggle('on', on);
        x.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      aplicar();
      if (b.hasAttribute('data-subir')) {
        var lista = raiz.querySelector('.bib-lista');
        if (lista) window.scrollTo({ top: Math.max(0, lista.getBoundingClientRect().top + window.pageYOffset - 220), behavior: 'smooth' });
      }
    });
    aplicar();
    return { limpiar: function () { busca.value = ''; grupo = 'todas'; raiz.querySelector('[data-filtro="todas"]').click(); } };
  }

  function barra(placeholder, botones) {
    return '<div class="gl-barra bib-barra">' +
      '<label class="gl-busca"><span class="sr-only">Buscar</span><input type="search" placeholder="' + esc(placeholder) + '" autocomplete="off"></label>' +
      '<div class="gl-cats" role="group" aria-label="Filtrar">' +
        botones.map(function (b, i) {
          return '<button type="button" class="gl-cat' + (i ? '' : ' on') + '" data-filtro="' + esc(b[0]) + '" aria-pressed="' + (i ? 'false' : 'true') + '">' + b[1] + '</button>';
        }).join('') +
      '</div>' +
      '<p class="gl-cuenta" role="status"></p>' +
    '</div>';
  }

  /* Al llegar con un ancla: se limpia el filtro si la escondía, se abre
     y se ilumina. Se acomoda bajo la cabecera y la barra pegada, y después
     del salto de apartados.js (load + 350 ms), que no cuenta la barra. */
  function irAlAncla(raiz, f) {
    function ir(conLoad) {
      var id = decodeURIComponent(location.hash.slice(1));
      if (!id) return;
      var el = document.getElementById(id);
      if (!el || !raiz.contains(el)) return;
      if (el.hidden && f) f.limpiar();
      if (el.tagName === 'DETAILS') el.open = true;
      var det = el.querySelector('details');
      if (det) det.open = true;
      function acomodar() {
        var nav = document.querySelector('.site-top-nav');
        var barra = raiz.querySelector('.gl-barra');
        var tope = nav ? Math.max(0, nav.getBoundingClientRect().bottom) : 0;
        if (barra && getComputedStyle(barra).position === 'sticky') tope += barra.getBoundingClientRect().height;
        window.scrollTo({ top: Math.max(0, el.getBoundingClientRect().top + window.pageYOffset - tope - 16), behavior: 'instant' });
        destacar(el);
      }
      if (conLoad && document.readyState !== 'complete') window.addEventListener('load', function () { setTimeout(acomodar, 450); });
      else setTimeout(acomodar, conLoad ? 450 : 30);
    }
    ir(true);
    window.addEventListener('hashchange', function () { ir(false); });
  }

  /* ---------------------------------------------------------------------
     1. Preguntas frecuentes
     --------------------------------------------------------------------- */
  function preguntas(raiz) {
    var bloques = DB.preguntas_casillas || [];
    var total = bloques.reduce(function (s, b) { return s + b.items.length; }, 0);
    raiz.innerHTML =
      barra('Busca una palabra: deuda, predial, Ramo 33, pliego…', [['todas', 'Todas (' + total + ')']].concat(
        bloques.map(function (b) { return [b.casilla_id, esc(b.icono + ' ' + b.bloque.replace(/^\d+\.\s*/, '')) + ' (' + b.items.length + ')']; }))) +
      '<div class="bib-acciones"><button type="button" class="bib-b" data-todas="1">Abrir todas</button><button type="button" class="bib-b" data-todas="0">Cerrar todas</button></div>' +
      '<div class="bib-lista bib-faq">' + bloques.map(function (b) {
        return '<section class="bib-bloque" data-bloque="' + esc(b.casilla_id) + '">' +
          '<h2 class="bib-bloque-tit"><span aria-hidden="true">' + esc(b.icono) + '</span> ' + esc(b.bloque) + '</h2>' +
          b.items.map(function (it, i) {
            var id = 'p-' + b.casilla_id + '-' + (i + 1);
            return '<details class="bib-q" id="' + esc(id) + '" data-grupo="' + esc(b.casilla_id) + '" data-q="' + esc(norm(it.q + ' ' + it.a)) + '">' +
              '<summary><span class="bib-q-ico" aria-hidden="true">💬</span><span class="bib-q-tx">' + esc(it.q) + '</span></summary>' +
              '<div class="bib-a">' + it.a +
                ((it.refs && it.refs.length) ? '<p class="bib-fuentes"><b>Fuentes:</b> ' + it.refs.map(refEnlace).filter(Boolean).join(' · ') + '</p>' : '') +
                '<p class="bib-enlace"><a href="#' + esc(id) + '">🔗 Enlace a esta pregunta</a></p>' +
              '</div></details>';
          }).join('') +
        '</section>';
      }).join('') + '</div>';
    var qs = Array.prototype.slice.call(raiz.querySelectorAll('.bib-q'));
    var f = filtro(raiz, {
      fichas: function () { return qs; }, singular: 'pregunta', plural: 'preguntas',
      despues: function (q) {
        Array.prototype.forEach.call(raiz.querySelectorAll('.bib-bloque'), function (s) {
          s.hidden = !s.querySelector('.bib-q:not([hidden])');
        });
        if (q) qs.forEach(function (d) { if (!d.hidden) d.open = true; });
      }
    });
    raiz.addEventListener('click', function (e) {
      var b = e.target.closest('[data-todas]');
      if (!b) return;
      var abrir = b.getAttribute('data-todas') === '1';
      qs.forEach(function (d) { if (!d.hidden) d.open = abrir; });
    });
    pegarBarra(raiz);
    irAlAncla(raiz, f);
  }

  /* ---------------------------------------------------------------------
     2. Marco legal
     --------------------------------------------------------------------- */
  var GRUPOS = [
    ['Constitucion', '🏛️ Constitución'],
    ['Ingresos', '📜 Ley de Ingresos 2026'],
    ['Presupuesto', '📊 Ley de Presupuesto (LFPRH)'],
    ['Coordinacion', '🤝 Coordinación Fiscal'],
    ['Disciplina', '🚦 Disciplina Financiera'],
    ['Judicial', '⚖️ Poder Judicial']
  ];
  var ETAPAS = [
    ['planea', '🧭', 'Se planea', 'El Estado fija el rumbo'],
    ['ingreso', '🧾', 'Se cobra', 'Impuestos y deuda'],
    ['aprueba', '🗳️', 'Se aprueba', 'Ley de Ingresos y Presupuesto'],
    ['ejerce', '💸', 'Se gasta', 'Con reglas y topes'],
    ['revisa', '🔍', 'Se revisa', 'Auditoría y alertas']
  ];

  function marco(raiz) {
    var ps = DB.preceptos_legales || [];
    var porGrupo = {}, porEtapa = {};
    ps.forEach(function (p) {
      porGrupo[p.grupo] = (porGrupo[p.grupo] || 0) + 1;
      porEtapa[p.etapa] = (porEtapa[p.etapa] || 0) + 1;
    });
    var leyes = {};
    ps.forEach(function (p) { leyes[p.ley] = 1; });

    raiz.innerHTML =
      '<section class="bib-ciclo" aria-labelledby="cicloTit">' +
        '<h2 class="bib-ciclo-tit" id="cicloTit">El ciclo del dinero público, artículo por artículo</h2>' +
        '<p class="bib-ciclo-tx">Cada peso pasa por cinco momentos y cada momento tiene sus reglas. Toca una etapa para ver solo sus preceptos.</p>' +
        '<ol class="bib-etapas">' + ETAPAS.map(function (e, i) {
          return '<li><button type="button" class="bib-etapa" data-filtro="e:' + e[0] + '" aria-pressed="false" data-subir="1">' +
            '<span class="bib-etapa-num">' + (i + 1) + '</span><span class="bib-etapa-ico" aria-hidden="true">' + e[1] + '</span>' +
            '<b>' + e[2] + '</b><small>' + e[3] + '</small><span class="bib-etapa-n">' + (porEtapa[e[0]] || 0) + ' preceptos</span></button></li>';
        }).join('') + '</ol>' +
        '<div class="bib-kpis">' +
          '<div class="bib-kpi"><b>' + ps.length + '</b><span>preceptos, con su texto vigente</span></div>' +
          '<div class="bib-kpi"><b>' + Object.keys(leyes).length + '</b><span>leyes y documentos oficiales</span></div>' +
          '<div class="bib-kpi"><b>' + (porGrupo.Constitucion || 0) + '</b><span>vienen de la Constitución</span></div>' +
        '</div>' +
      '</section>' +
      barra('Busca un artículo o un tema: 134, deuda, licitación, Ramo 33…', [['todas', 'Todos (' + ps.length + ')']].concat(
        GRUPOS.filter(function (g) { return porGrupo[g[0]]; }).map(function (g) { return [g[0], g[1] + ' (' + porGrupo[g[0]] + ')']; }))) +
      '<div class="bib-lista bib-preceptos">' + ps.map(function (p) {
        var cifras = (p.cifras || []).map(function (c) {
          return '<li><span>' + esc(c.etiqueta) + '</span><b>' + esc(c.valor) + '</b>' + chip(c.estado) + '<small>' + esc(c.fuente) + '</small></li>';
        }).join('');
        return '<article class="bib-p" id="precepto-' + esc(p.id) + '" data-grupo="' + esc(p.grupo) + '" data-etapa="' + esc(p.etapa) + '" data-q="' + esc(norm([p.ley, p.precepto, p.denominacion, p.precepto_resumen, p.texto_oficial, p.analisis_civico].join(' '))) + '">' +
          '<header class="bib-p-cab"><span class="bib-p-ico" aria-hidden="true">' + esc(p.icono) + '</span>' +
            '<span class="bib-p-ley">' + esc(p.ley) + '</span></header>' +
          '<h3 class="bib-p-tit">' + esc(p.denominacion) + '</h3>' +
          '<p class="bib-p-art">' + esc(p.precepto) + '</p>' +
          '<p class="bib-p-res">' + esc(p.precepto_resumen) + '</p>' +
          (cifras ? '<ul class="bib-p-cifras">' + cifras + '</ul>' : '') +
          '<details class="bib-p-mas"><summary>📜 Leer el texto vigente</summary>' +
            '<blockquote class="bib-p-texto">' + esc(p.texto_oficial) + '</blockquote>' +
            '<p class="bib-p-vig">' + chip('oficial') + ' ' + esc(p.vigencia || '') + ' Los corchetes […] marcan lo que se omite.</p>' +
          '</details>' +
          '<div class="bib-p-por"><b>Por qué te importa.</b> ' + esc(p.analisis_civico) + '</div>' +
          (p.pendiente ? '<p class="bib-p-pend">' + chip('pendiente') + ' ' + esc(p.pendiente) + '</p>' : '') +
          '<footer class="bib-p-pie"><a href="' + esc(p.url_oficial) + '" target="_blank" rel="noopener noreferrer">Texto íntegro ↗</a>' +
            (p.ref && REFS[p.ref] ? '<a href="fuentes-oficiales.html#' + esc(p.ref) + '">Ficha [' + REFS[p.ref].num + '] en el catálogo</a>' : '') +
          '</footer>' +
        '</article>';
      }).join('') + '</div>';

    var fichas = Array.prototype.slice.call(raiz.querySelectorAll('.bib-p'));
    /* Las etapas filtran por data-etapa; los botones de ley, por grupo.
       Se marca data-grupo-activo para que el filtro común compare con el
       atributo correcto. */
    fichas.forEach(function (f) { f.setAttribute('data-grupo-ley', f.getAttribute('data-grupo')); });
    var f = filtro(raiz, {
      fichas: function () {
        var activo = raiz.querySelector('[data-filtro].on');
        var etapa = activo && /^e:/.test(activo.getAttribute('data-filtro'));
        fichas.forEach(function (x) {
          x.setAttribute('data-grupo', etapa ? 'e:' + x.getAttribute('data-etapa') : x.getAttribute('data-grupo-ley'));
        });
        return fichas;
      },
      singular: 'precepto', plural: 'preceptos'
    });
    pegarBarra(raiz);
    irAlAncla(raiz, f);
  }

  /* ---------------------------------------------------------------------
     3. Catálogo de fuentes
     --------------------------------------------------------------------- */
  var FAMILIAS = [
    ['leyes', '⚖️', 'Constitución y leyes', ['constitucional', 'leyes_federales', 'coordinacion_fiscal', 'hacendario_fiscal', 'tributario', 'contabilidad_gubernamental', 'adquisiciones_compras', 'banca_central']],
    ['paquete', '📦', 'Paquete económico y presupuesto', ['leyes_anuales']],
    ['fiscalizacion', '🔍', 'Fiscalización y auditoría', ['fiscalizacion_auditoria']],
    ['datos', '🗂️', 'Portales y datos abiertos', ['fuentes_oficiales']],
    ['estadistica', '📈', 'Estadística oficial', ['estadistica_oficial']],
    ['judicial', '🏛️', 'Poder Judicial', ['judicial']],
    ['otras', '📚', 'Investigación, doctrina y otras', ['investigacion_civica', 'doctrina', 'internacional']]
  ];
  var FAM_DE = {};
  FAMILIAS.forEach(function (f) { f[3].forEach(function (c) { FAM_DE[c] = f[0]; }); });
  /* Documento del Estado mexicano: un dominio de gobierno o de un órgano
     público. Lo demás (centros de investigación, prensa, una corte de otro
     país) es fuente complementaria. */
  function dominio(u) { var m = String(u || '').match(/^https?:\/\/([^/]+)/i); return m ? m[1].replace(/^www\./, '').toLowerCase() : ''; }
  function esEstatal(d) { return /\.gob\.mx$/.test(d) || /^(banxico|inegi|fgr|plataformadetransparencia)\.org\.mx$/.test(d); }

  function fuentes(raiz) {
    var refs = (DB.referencias_legales || []).slice().sort(function (a, b) { return (a.num || 0) - (b.num || 0); });
    var n = {}, estatales = 0;
    refs.forEach(function (r) {
      var fam = FAM_DE[r.categoria] || 'otras';
      r._fam = fam;
      n[fam] = (n[fam] || 0) + 1;
      r._dom = dominio(r.url);
      r._estatal = r._dom && esEstatal(r._dom);
      if (r._estatal) estatales++;
    });
    var max = Math.max.apply(null, FAMILIAS.map(function (f) { return n[f[0]] || 0; }));
    raiz.innerHTML =
      '<section class="bib-cita" aria-labelledby="citaTit">' +
        '<h2 id="citaTit">Cómo citamos</h2>' +
        '<p>Cada cifra de la plataforma lleva junto a ella un número de referencia, como <b>[11]</b>, que abre su ficha en este catálogo, y un estado:</p>' +
        '<ul class="bib-cita-est">' +
          '<li>' + chip('oficial') + ' tomada tal cual de su documento.</li>' +
          '<li>' + chip('derivado') + ' calculada con datos oficiales; te decimos la operación.</li>' +
          '<li>' + chip('pendiente') + ' sin documento oficial todavía; te decimos por qué y, si aplica, quién debía publicarlo.</li>' +
        '</ul>' +
      '</section>' +
      '<section class="bib-graf" aria-labelledby="grafTit">' +
        '<h2 id="grafTit">De qué está hecho el catálogo</h2>' +
        '<p class="bib-graf-tx"><b>' + refs.length + '</b> fichas. <b>' + estatales + '</b> son documentos de una dependencia u órgano del Estado mexicano ' + chip('derivado') + ' (cuenta por el dominio de su liga); las demás son de centros de investigación, prensa, doctrina o de otro país, y se marcan como complementarias.</p>' +
        '<div class="bib-barras">' + FAMILIAS.map(function (f) {
          var v = n[f[0]] || 0;
          return '<button type="button" class="bib-barra-f" data-filtro="' + f[0] + '" aria-pressed="false" data-subir="1">' +
            '<span class="bib-barra-et"><span aria-hidden="true">' + f[1] + '</span> ' + esc(f[2]) + '</span>' +
            '<span class="bib-barra-pista"><span class="bib-barra-val" style="width:' + (max ? Math.round(v / max * 100) : 0) + '%"></span></span>' +
            '<b class="bib-barra-n">' + v + '</b></button>';
        }).join('') + '</div>' +
      '</section>' +
      barra('Busca un documento, una ley o una dependencia: DOF, ASF, INEGI, PEF…', [['todas', 'Todas (' + refs.length + ')']].concat(
        FAMILIAS.filter(function (f) { return n[f[0]]; }).map(function (f) { return [f[0], f[1] + ' ' + esc(f[2]) + ' (' + n[f[0]] + ')']; }))) +
      '<ol class="bib-lista bib-refs">' + refs.map(function (r) {
        return '<li class="bib-r" id="' + esc(r.id) + '" data-grupo="' + r._fam + '" data-q="' + esc(norm([r.num, r.cita_apa, r.descripcion, r.categoria_nombre, r._dom].join(' '))) + '">' +
          '<span class="bib-r-num">[' + r.num + ']</span>' +
          '<div class="bib-r-cuerpo">' +
            '<p class="bib-r-cita">' + esc(String(r.cita_apa || '').replace(/<[^>]+>/g, '')) + '</p>' +
            (r.descripcion ? '<p class="bib-r-desc">' + esc(String(r.descripcion).replace(/<[^>]+>/g, '')) + '</p>' : '') +
            '<p class="bib-r-pie"><span class="bib-r-cat">' + esc(r.categoria_nombre || '') + '</span>' +
              (r.url ? '<a href="' + esc(r.url) + '" target="_blank" rel="noopener noreferrer">' + esc(r._dom) + ' ↗</a>' : '<span class="bib-r-sin">Obra impresa, sin liga</span>') +
              (r.url && !r._estatal ? '<span class="bib-r-comp">complementaria</span>' : '') +
              '<a href="#' + esc(r.id) + '" class="bib-r-ancla" aria-label="Enlace a la ficha ' + r.num + '">🔗</a>' +
            '</p>' +
          '</div></li>';
      }).join('') + '</ol>';
    var fichas = Array.prototype.slice.call(raiz.querySelectorAll('.bib-r'));
    var f = filtro(raiz, { fichas: function () { return fichas; }, singular: 'ficha', plural: 'fichas' });
    pegarBarra(raiz);
    irAlAncla(raiz, f);
  }

  var r;
  if ((r = document.getElementById('bibPreguntas'))) preguntas(r);
  if ((r = document.getElementById('bibMarco'))) marco(r);
  if ((r = document.getElementById('bibFuentes'))) fuentes(r);
})();
