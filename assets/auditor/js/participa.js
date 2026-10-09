/* Auditavisión · participa.html: el ágora cívica, el formulario «Ayúdanos a
   fiscalizar», los canales oficiales de denuncia y el decálogo, dentro de
   sus pestañas (decisión del autor, 09-10-2026).
   Las funciones son copia de las del motor (audit-engine.js, bloque
   «Comunidad» y «Portal público digital»), que esta página no carga: si
   cambia una, cambia la otra. Lee los datos de window.AUDIT_DB. */
(function () {
  'use strict';
  const DB = window.AUDIT_DB || {};
  /* En el auditor se le habla de tú. */
  function tuUd(ud, tu) { return tu; }
  /* Las fuentes de los canales abren su documento oficial. */
  function goToRef(refId) {
    const r = (DB.referencias_legales || []).find(function (x) { return x.id === refId; });
    if (r && r.url) window.open(r.url, '_blank', 'noopener');
  }
  /* Si el bloque vive en una pestaña cerrada, se abre primero. */
  function abrirPestanaDe(el) {
    const panel = el.closest('.apartado-panel');
    if (panel && panel.hidden) {
      const t = document.getElementById('pestana-' + panel.id);
      if (t) t.click();
    }
  }

  function escHtml(v) {
    return String(v == null ? '' : v)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /* Los debates de ejemplo guardan su antiguedad en dias, no una fecha fija:
     asi el foro no envejece mal cuando pasan semanas sin tocar el proyecto. */
  function fechaRelativa(diasAtras) {
    const d = new Date();
    d.setDate(d.getDate() - (parseInt(diasAtras, 10) || 0));
    const fecha = d.toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' });
    const n = parseInt(diasAtras, 10) || 0;
    let rel;
    if (n <= 0) rel = 'Hoy';
    else if (n === 1) rel = 'Hace 1 día';
    else if (n < 7) rel = 'Hace ' + n + ' días';
    else if (n < 30) rel = 'Hace ' + Math.floor(n / 7) + (Math.floor(n / 7) === 1 ? ' semana' : ' semanas');
    else rel = 'Hace ' + Math.floor(n / 30) + (Math.floor(n / 30) === 1 ? ' mes' : ' meses');
    return { fecha: fecha, relativo: rel };
  }

  const COM_RUTAS = [
    { id: 'aportar', n: '1', ico: '🔍', ancla: 'bloqueAportar',
      tit: 'Ayúdanos a fiscalizar',
      txt: tuUd('Comparta un dato, una obra de su municipio que no cuadra, una corrección a lo que publicamos o una pista que valga la pena seguir.', 'Comparte un dato, una obra de tu municipio que no cuadra, una corrección a lo que publicamos o una pista que valga la pena seguir.'),
      efecto: 'Alimenta el trabajo de esta plataforma',
      aviso: 'No es una denuncia legal', tono: 'gold' },
    { id: 'denunciar', n: '2', ico: '🏛️', ancla: 'bloqueCanales',
      tit: 'Canales oficiales de denuncia',
      txt: 'Las seis puertas del Estado donde un señalamiento se convierte en expediente: qué investiga cada una, si admite anonimato y qué debe tener a la mano.',
      efecto: 'La única ruta con efecto jurídico',
      aviso: 'Aquí sí hay consecuencias', tono: 'emerald' },
    { id: 'debatir', n: '3', ico: '💬', ancla: 'bloquePortal',
      tit: 'Portal público de diálogo y réplica',
      txt: 'Ágora abierta con seudónimo para contrastar posturas, citar fuentes y replicar a cualquier argumento, incluidos los nuestros.',
      efecto: 'Conversación pública argumentada',
      aviso: 'No sustituye a las dos anteriores', tono: 'cyan' }
  ];

  function irABloqueComunidad(id) {
    const el = document.getElementById(id);
    if (!el) return;
    abrirPestanaDe(el);
    const y = el.getBoundingClientRect().top + window.scrollY - 90;
    const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({ top: y, behavior: reduce ? 'instant' : 'smooth' });
    el.classList.add('pj-nivel-destacado');
    setTimeout(() => el.classList.remove('pj-nivel-destacado'), 1400);
  }

  function renderComunidadOrientacion() {
    const cont = document.getElementById('comOrientacion');
    if (!cont) return;

    const canales = (DB.comunidad && DB.comunidad.canales_denuncia_oficial) || [];
    const decalogo = (DB.comunidad && DB.comunidad.principios_contraloria_social) || [];

    cont.innerHTML =
      '<div class="pjo-wrap">' +

        '<div class="com-rutas" role="list">' +
          COM_RUTAS.map(r =>
            '<button type="button" class="com-ruta" data-tono="' + r.tono + '" role="listitem"' +
            ' onclick="window.AuditEngine.irABloqueComunidad(\'' + r.ancla + '\')">' +
              '<span class="com-ruta-num" aria-hidden="true">' + r.n + '</span>' +
              '<span class="com-ruta-ico" aria-hidden="true">' + r.ico + '</span>' +
              '<span class="com-ruta-tit">' + r.tit + '</span>' +
              '<span class="com-ruta-txt">' + r.txt + '</span>' +
              '<span class="com-ruta-efecto">' + r.efecto + '</span>' +
              '<span class="com-ruta-aviso">' + r.aviso + '</span>' +
            '</button>').join('') +
        '</div>' +

        '<div class="com-destino">' +
          tuUd('<div class="com-destino-tit">Antes de escribir: a dónde va a parar lo que escriba</div>', '<div class="com-destino-tit">Antes de escribir: a dónde va a parar lo que escribas</div>') +
          tuUd('<p class="com-destino-sub">Es la pregunta que casi ningún portal ciudadano responde, y la que decide si su esfuerzo sirve de algo. Las tres funciones de esta pestaña terminan en lugares distintos.</p>', '<p class="com-destino-sub">Es la pregunta que casi ningún portal ciudadano responde, y la que decide si tu esfuerzo sirve de algo. Las tres funciones de esta pestaña terminan en lugares distintos.</p>') +
          '<div class="com-destino-cols">' +
            '<div class="com-destino-col" data-tono="gold">' +
              '<div class="com-destino-k">El formulario «Ayúdanos a fiscalizar»</div>' +
              tuUd('<p>Se guarda <strong>únicamente en su propio navegador</strong>. Todavía no hay servidor: nadie más lo ve, y si borra los datos del sitio se pierde. Sirve para ordenar lo que quiere reportar y para llevárselo a un canal oficial con el botón de copiar.</p>', '<p>Se guarda <strong>únicamente en tu propio navegador</strong>. Todavía no hay servidor: nadie más lo ve, y si borras los datos del sitio se pierde. Sirve para ordenar lo que quieres reportar y para llevártelo a un canal oficial con el botón de copiar.</p>') +
            '</div>' +
            '<div class="com-destino-col" data-tono="emerald">' +
              '<div class="com-destino-k">Un canal oficial</div>' +
              '<p>Ahí sí se abre un expediente con número de folio ante un órgano del Estado, con plazos y con obligación de responder. Es <strong>la única vía que produce consecuencias jurídicas</strong>.</p>' +
            '</div>' +
            '<div class="com-destino-col" data-tono="cyan">' +
              '<div class="com-destino-k">El portal de debate</div>' +
              tuUd('<p>También vive <strong>en su navegador</strong> por ahora. Los hilos que vea publicados son ejemplos sembrados para mostrar cómo funcionará el ágora cuando tenga servidor.</p>', '<p>También vive <strong>en tu navegador</strong> por ahora: los hilos que ves son los que tú publicaste aquí. Nadie más los lee hasta que la plataforma tenga servidor.</p>') +
            '</div>' +
          '</div>' +
          tuUd('<div class="com-destino-pie"><strong>Lo decimos sin adornos porque es lo honesto:</strong> esta plataforma todavía no aloja lo que usted escribe. Prometer lo contrario sería exactamente el tipo de dato falso que nos descalificaría. Lo que sí está completo y verificado son los ', '<div class="com-destino-pie"><strong>Lo decimos sin adornos porque es lo honesto:</strong> esta plataforma todavía no aloja lo que escribes. Prometer lo contrario sería exactamente el tipo de dato falso que nos descalificaría. Lo que sí está completo y verificado son los ') + canales.length + ' canales oficiales y los ' + decalogo.length + ' puntos del decálogo: ahí cada enlace lleva a una institución real.</div>' +
        '</div>' +

      '</div>';
  }

  // ==========================================================================
  // GESTOR DEL FORMULARIO DE COMUNIDAD & CONTRALORÍA SOCIAL
  // ==========================================================================
  function initComunidad() {
    const textarea = document.getElementById('comMensaje');
    const counter = document.getElementById('comCharCount');
    const form = document.getElementById('comunidadForm');
    const msgStatus = document.getElementById('comStatusMsg');

    if (textarea && counter) {
      textarea.addEventListener('input', () => {
        counter.textContent = `${textarea.value.length} / 1000`;
      });
    }

    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const nombre = document.getElementById('comNombre')?.value || 'Ciudadano Auditor';
        const tipo = document.getElementById('comTipo')?.value || 'Sugerencia';
        const estado = document.getElementById('comEstadoSel')?.value || 'Nacional';
        const texto = textarea?.value || '';

        if (!texto.trim()) return;

        /* Guardar localmente. Si el navegador no deja guardar (modo privado,
           almacenamiento lleno), se dice y el texto se queda en el formulario. */
        let savedComments = [];
        try { savedComments = JSON.parse(localStorage.getItem('auditavision_comentarios') || '[]'); } catch (err) { savedComments = []; }
        if (!Array.isArray(savedComments)) savedComments = [];
        savedComments.unshift({
          id: Date.now(),
          fecha: new Date().toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' }),
          nombre: nombre,
          tipo: tipo,
          estado: estado,
          texto: texto
        });
        try {
          localStorage.setItem('auditavision_comentarios', JSON.stringify(savedComments));
        } catch (err) {
          if (msgStatus) {
            msgStatus.textContent = '✗ Este navegador no permitió guardar el texto (puede estar en modo privado o sin espacio). Tu texto sigue en el formulario: cópialo antes de salir.';
            msgStatus.style.color = 'var(--crimson-bright, #e74c3c)';
          }
          return;
        }

        if (msgStatus) {
          // Decir la verdad sobre el destino del texto: se guarda en este
          // navegador, no viaja a ningun servidor todavia.
          msgStatus.textContent = tuUd('✓ Guardado en este navegador. Use «Copiar para un canal oficial» si quiere presentarlo ante la ASF, la SABG o una contraloría.', '✓ Guardado en este navegador. Usa «Copiar para un canal oficial» si quieres presentarlo ante la ASF, la SABG o una contraloría.');
          msgStatus.style.color = 'var(--emerald-bright)';
        }
        form.reset();
        if (counter) counter.textContent = '0 / 1000';
        renderComentariosList();
      });
    }

    renderComunidadOrientacion();
    poblarSelectorEntidades();
    renderCanalesOficiales();
    renderDecalogoContraloria();
    renderComentariosList();
    initPortalDigital();
  }

  function renderCanalesOficiales() {
    const container = document.getElementById('canalesOficialesContainer');
    if (!container || !DB.comunidad || !DB.comunidad.canales_denuncia_oficial) return;

    container.innerHTML = DB.comunidad.canales_denuncia_oficial.map((c, i) => {
      const acceso = c.url
        ? '<a class="canal-cta" href="' + c.url + '" target="_blank" rel="noopener noreferrer">Abrir el canal oficial ↗</a>'
        : '<span class="canal-sin-url">' + (c.notaSinUrl || tuUd('Consulte el sitio oficial de la institución.', 'Consulta el sitio oficial de la institución.')) + '</span>';
      const cita = c.refId
        ? ' <a class="ref-link" onclick="window.AuditEngine.goToRef(\'' + c.refId + '\')">[fuente]</a>'
        : '';
      return '' +
        '<article class="canal-item-card" data-tono="' + (c.tono || 'neutro') + '">' +
          '<div class="canal-top">' +
            '<span class="canal-ico" aria-hidden="true">' + (c.icono || '🏛️') + '</span>' +
            '<div class="canal-ident">' +
              '<span class="canal-num" aria-hidden="true">Canal ' + (i + 1) + ' de ' + DB.comunidad.canales_denuncia_oficial.length + '</span>' +
              '<h4>' + c.organismo + (c.siglas ? ' <span class="canal-siglas">' + c.siglas + '</span>' : '') + '</h4>' +
              '<span class="canal-herramienta">' + c.herramienta + '</span>' +
            '</div>' +
          '</div>' +
          '<dl class="canal-datos">' +
            '<div><dt>Para qué sirve</dt><dd>' + c.paraQue + '</dd></div>' +
            '<div><dt>¿Admite anonimato?</dt><dd>' + c.anonimo + '</dd></div>' +
            '<div><dt>Qué debe tener a la mano</dt><dd>' + c.queNecesitas + '</dd></div>' +
            '<div><dt>Qué produce su denuncia</dt><dd>' + c.efecto + cita + '</dd></div>' +
          '</dl>' +
          '<div class="canal-pie">' + acceso + '</div>' +
        '</article>';
    }).join('');
  }

  function renderDecalogoContraloria() {
    const cont = document.getElementById('decalogoContainer');
    if (!cont || !DB.comunidad || !DB.comunidad.principios_contraloria_social) return;
    const lista = DB.comunidad.principios_contraloria_social;
    cont.innerHTML = lista.map(d =>
      '<article class="dec-punto">' +
        '<span class="dec-n" aria-hidden="true">' + d.n + '</span>' +
        '<div class="dec-cuerpo">' +
          '<h5 class="dec-tit">' + d.titulo + '</h5>' +
          '<p class="dec-txt">' + d.texto + '</p>' +
          '<p class="dec-fund"><span aria-hidden="true">📜</span> ' + d.fundamento + '</p>' +
        '</div>' +
      '</article>').join('');
  }

  function renderComentariosList() {
    const list = document.getElementById('comentariosListContainer');
    if (!list) return;

    let saved = [];
    try { saved = JSON.parse(localStorage.getItem('auditavision_comentarios') || '[]'); } catch (e) { saved = []; }

    if (saved.length === 0) {
      list.innerHTML =
        '<div class="com-vacio">' +
          '<span aria-hidden="true">📝</span>' +
          tuUd('<p>Todavía no ha registrado ninguna observación. Lo que escriba aquí queda guardado en este navegador y podrá copiarlo después para presentarlo en un canal oficial.</p>', '<p>Todavía no has registrado ninguna observación. Lo que escribas aquí queda guardado en este navegador y podrás copiarlo después para presentarlo en un canal oficial.</p>') +
        '</div>';
      return;
    }

    list.innerHTML = saved.slice(0, 10).map(c =>
      '<article class="com-obs">' +
        '<div class="com-obs-top">' +
          '<strong class="com-obs-autor">' + escHtml(c.nombre) + '</strong>' +
          '<span class="com-obs-meta">' + escHtml(c.fecha) + ' · <span class="com-obs-tipo">' + escHtml(c.tipo) + '</span> · ' + escHtml(c.estado) + '</span>' +
        '</div>' +
        '<p class="com-obs-txt">' + escHtml(c.texto) + '</p>' +
        '<div class="com-obs-acciones">' +
          '<button type="button" class="com-obs-btn" onclick="window.AuditEngine.copiarObservacion(' + Number(c.id) + ')">Copiar para un canal oficial</button>' +
          '<button type="button" class="com-obs-btn borrar" onclick="window.AuditEngine.borrarObservacion(' + Number(c.id) + ')">Borrar</button>' +
        '</div>' +
      '</article>').join('');
  }

  /* Puente entre la funcion 1 y la funcion 2: lo que la persona redacto aqui
     queda listo para pegarse en el formulario de la ASF, la SABG o un OIC. */
  function copiarObservacion(id) {
    let saved = [];
    try { saved = JSON.parse(localStorage.getItem('auditavision_comentarios') || '[]'); } catch (e) { return; }
    const c = saved.find(x => String(x.id) === String(id));
    if (!c) return;
    const texto =
      'Observación ciudadana\n' +
      'Fecha de registro: ' + c.fecha + '\n' +
      'Tipo: ' + c.tipo + '\n' +
      'Entidad relacionada: ' + c.estado + '\n' +
      'Presenta: ' + (c.nombre || 'Ciudadano auditor') + '\n\n' +
      'Hechos que se señalan:\n' + c.texto + '\n';
    const avisar = ok => {
      const el = document.getElementById('comStatusMsg');
      if (!el) return;
      el.textContent = ok
        ? '✓ Texto copiado. Péguelo en el formulario del canal oficial que corresponda.'
        : tuUd('No se pudo copiar automáticamente. Seleccione el texto de la tarjeta y cópielo a mano.', 'No se pudo copiar automáticamente. Selecciona el texto de la tarjeta y cópialo a mano.');
      el.style.color = ok ? 'var(--emerald-bright)' : 'var(--crimson-bright)';
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(() => avisar(true)).catch(() => avisar(false));
    } else {
      avisar(false);
    }
  }

  function borrarObservacion(id) {
    let saved = [];
    try { saved = JSON.parse(localStorage.getItem('auditavision_comentarios') || '[]'); } catch (e) { return; }
    saved = saved.filter(x => String(x.id) !== String(id));
    try {
      localStorage.setItem('auditavision_comentarios', JSON.stringify(saved));
    } catch (e) {
      alert('Este navegador no permitió borrar la observación. Sigue guardada.');
      return;
    }
    renderComentariosList();
  }

  /* El selector traia doce entidades escritas a mano. Se arma con las 32 de
     la base para que nadie quede fuera de su propio reporte. */
  function poblarSelectorEntidades() {
    const sel = document.getElementById('comEstadoSel');
    if (!sel || !Array.isArray(DB.estados)) return;
    if (sel.dataset.poblado === 'si') return;
    const previos = sel.value;
    const ordenadas = DB.estados.slice().sort((a, b) =>
      String(a.name || '').localeCompare(String(b.name || ''), 'es'));
    sel.innerHTML =
      '<option value="Nacional">Nacional / Federal</option>' +
      ordenadas.map(e =>
        '<option value="' + escHtml(e.abbr) + '">' + escHtml(e.name) + '</option>').join('');
    sel.dataset.poblado = 'si';
    if (previos) sel.value = previos;
  }

  // ==========================================================================
  // BLOQUE 3: PORTAL PÚBLICO DIGITAL · ÁGORA CÍVICA & DEBATES CIUDADANOS
  // ==========================================================================
  let activePortalForumFilter = 'todos';
  let activeStanceSelected = 'matiz';

  /* El foro dice de que pestana habla cada hilo; este mapa lo lleva alli.
     Antes el selector afirmaba que la deuda estaba en la pestana 6, que es
     el Modo Inspector: la maquinaria financiera vive en la pestana 2. */
  const PORTAL_TEMA_PESTANA = {
    'presupuesto': { tab: 'presupuesto',       etiqueta: 'Presupuesto' },
    'megaobras':   { tab: 'megaobras',         etiqueta: 'Megaobras' },
    'deuda':       { tab: 'accion-financiera', etiqueta: 'Acción Financiera' },
    'legislativo': { tab: 'legislativo',       etiqueta: 'Congreso' },
    'judicial':    { tab: 'judicial',          etiqueta: 'Poder Judicial' },
    'politicos':   { tab: 'politicos',         etiqueta: 'Enciclopedia' }
  };

  /* En la plataforma no hay pestanas de Congreso ni de Corte: su gasto vive
     en Accion Financiera (Poderes). Los personajes solo estan en la
     Enciclopedia. */
  function irAPestanaDesdeDebate(tab) {
    if (tab === 'politicos') { window.location.href = 'enciclopedia.html#politicos'; return; }
    const destino = (tab === 'legislativo' || tab === 'judicial') ? 'poderes'
      : (tab === 'megaobras' ? 'megaobras' : 'presupuesto');
    window.location.href = 'index.html?ir=' + destino;
  }


  const NICK_PREFIXES = ['@Auditor', '@Fiscalizador', '@Observador', '@Ciudadano', '@Analista', '@Constitucionalista', '@Economista', '@Vigilante', '@VozCívica', '@Criterio'];
  const NICK_SUFFIXES = ['MX', 'Norte', 'Sureste', 'Regio', 'Libre', 'Crítico', 'Informado', 'Federal', 'Poblano', 'Jalisciense', 'Digital', 'Cívico'];

  function generarRandomNick() {
    const p = NICK_PREFIXES[Math.floor(Math.random() * NICK_PREFIXES.length)];
    const s = NICK_SUFFIXES[Math.floor(Math.random() * NICK_SUFFIXES.length)];
    const num = Math.floor(Math.random() * 90) + 10;
    const nick = `${p}${s}_${num}`;
    const el = document.getElementById('portalNick');
    if (el) el.value = nick;
    return nick;
  }

  function selectStance(stance) {
    activeStanceSelected = stance;
    const input = document.getElementById('portalStanceVal');
    if (input) input.value = stance;
    document.querySelectorAll('#portalStanceGroup .stance-btn-radio').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.stance === stance);
    });
  }

  /* El foro venia sembrado con cuatro debates firmados por usuarios que no
     existen (@AuditorSureste, @CriminologiaJuridica...). Se presentaban como
     voces ciudadanas reales. Se retiraron el 27-09-2026 y, en los navegadores
     que ya los habian guardado, se purgan al leer. */
  const DEBATES_SEMBRADOS = ['deb-tren-maya-subsidios', 'deb-scjn-fideicomisos-art127',
    'deb-deuda-cetes-banxico', 'deb-garcia-luna-cnpp'];

  function getPortalDebates() {
    let raw = null;
    try { raw = localStorage.getItem('auditavision_foro_debates'); } catch (e) { raw = null; }
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          const propios = parsed.filter(d => d && DEBATES_SEMBRADOS.indexOf(d.id) === -1);
          if (propios.length !== parsed.length) savePortalDebates(propios);
          if (propios.length > 0) return propios;
        }
      } catch (e) {
        console.error('Error al leer debates locales:', e);
      }
    }
    return [];
  }

  /* Devuelve si el guardado ocurrio, para no anunciar lo que no paso. */
  function savePortalDebates(debates) {
    try { localStorage.setItem('auditavision_foro_debates', JSON.stringify(debates)); return true; } catch (e) { return false; }
  }

  function leerApoyosLocales() {
    try {
      const v = JSON.parse(localStorage.getItem('auditavision_liked_debates') || '[]');
      return Array.isArray(v) ? v : [];
    } catch (e) { return []; }
  }

  function initPortalDigital() {
    const textarea = document.getElementById('portalContenido');
    const counter = document.getElementById('portalCharCount');
    if (textarea && counter) {
      textarea.addEventListener('input', () => {
        counter.textContent = `${textarea.value.length} / 1200`;
      });
    }

    const nickInput = document.getElementById('portalNick');
    if (nickInput && !nickInput.value.trim()) {
      generarRandomNick();
    }

    renderPortalDebates();
  }

  function renderPortalDebates(filtro = null) {
    if (filtro !== null) activePortalForumFilter = filtro;
    const container = document.getElementById('portalDebatesListContainer');
    if (!container) return;

    // Actualizar botones de filtro
    document.querySelectorAll('#portalFilterBar button').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.forumFilter === activePortalForumFilter);
      btn.classList.toggle('on', btn.dataset.forumFilter === activePortalForumFilter);
    });

    const debates = getPortalDebates();
    let list = debates;
    if (activePortalForumFilter !== 'todos') {
      list = debates.filter(d => d.tema_id === activePortalForumFilter);
    }

    if (list.length === 0) {
      container.innerHTML = `
        <div style="background:var(--bg-surface); border:1px dashed var(--border-gold); padding:30px; border-radius:10px; text-align:center;">
          <div style="font-size:32px; margin-bottom:8px;">💬</div>
          <h4 style="color:var(--gold-bright); font-family:var(--font-serif); margin-bottom:6px;">No hay diálogos registrados en este eje temático</h4>
          <p style="font-size:12.5px; color:var(--text-secondary); margin:0;">Sé la primera persona en publicar un argumento o postura cívica sobre este tema.</p>
        </div>
      `;
      return;
    }

    const likedDebates = leerApoyosLocales();

    container.innerHTML = list.map(d => {
      const isLiked = likedDebates.includes(d.id);
      const stanceClass = `stance-${d.postura || 'matiz'}`;
      const repliesCount = (d.replicas && d.replicas.length) || 0;
      // Los hilos sembrados guardan antiguedad, no fecha fija: se calcula aqui.
      const fechas = (d.dias_atras !== undefined && d.dias_atras !== null)
        ? fechaRelativa(d.dias_atras)
        : { fecha: d.fecha || 'Reciente', relativo: d.tiempo_relativo || 'Reciente' };
      const destino = PORTAL_TEMA_PESTANA[d.tema_id];

      return `
        <article class="debate-post-card ${stanceClass}" id="${d.id}">
          <div class="debate-header-row">
            <div class="debate-author-info">
              <div class="user-avatar-circle" style="background:${d.autor_avatar_color || 'var(--gold)'};">
                ${escHtml((d.autor_nick || '@U').replace('@', '').substring(0, 2).toUpperCase())}
              </div>
              <div>
                <span class="user-nick-text">${escHtml(d.autor_nick)}</span>
                <div class="debate-time-text">${fechas.fecha} · ${fechas.relativo}</div>
              </div>
            </div>

            <div class="debate-badges-row">
              <span class="stance-badge ${d.postura}">
                ${escHtml(d.postura_icono || '⚖️')} ${escHtml(d.postura_nombre || 'Postura')}
              </span>
              <span class="topic-badge">${escHtml(d.tema_nombre)}</span>
            </div>
          </div>

          <h4 class="debate-title-h4">${escHtml(d.tesis)}</h4>
          <div class="debate-content-body">${escHtml(d.contenido)}</div>

          ${d.fuente ? `
            <div class="debate-source-box">
              <span>📚 <strong>Fuente citada:</strong> ${escHtml(d.fuente)}</span>
              ${d.fuente_url ? `<a href="${d.fuente_url}" target="_blank" rel="noopener noreferrer" style="color:var(--cyan); text-decoration:none;">↗ Consultar documento oficial</a>` : ''}
            </div>
          ` : ''}

          <div class="debate-actions-bar">
            <button class="action-civic-btn ${isLiked ? 'liked' : ''}" onclick="window.AuditEngine.likeDebate('${d.id}')" title="Apoyar este argumento cívico">
              <span>👍</span> <span>Apoyo Cívico (${d.apoyos || 0})</span>
            </button>

            <button class="action-civic-btn" onclick="window.AuditEngine.toggleReplyBox('${d.id}')" title="Ver réplicas o responder">
              <span>💬</span> <span>Réplicas (${repliesCount}) ▾</span>
            </button>

            <button class="action-civic-btn" onclick="window.AuditEngine.copyDebateLink('${d.id}')" title="Copiar enlace a este debate">
              <span>🔗</span> <span>Compartir</span>
            </button>

            ${destino ? `
            <button class="action-civic-btn" onclick="window.AuditEngine.irAPestanaDesdeDebate('${destino.tab}')" title="Abrir los datos que discute este hilo">
              <span>📂</span> <span>Ver los datos (${destino.etiqueta})</span>
            </button>` : ''}
          </div>

          <!-- Caja desplegable de réplicas e hilo -->
          <div id="replyContainer_${d.id}" class="debate-replies-thread" style="${repliesCount > 0 ? 'display:flex;' : 'display:none;'}">
            ${repliesCount > 0 ? d.replicas.map(r => `
              <div class="reply-item-card" id="${r.id}">
                <div class="reply-header-row">
                  <div style="display:flex; align-items:center; gap:8px;">
                    <div class="user-avatar-circle" style="width:24px; height:24px; font-size:9.5px; background:${r.autor_avatar_color || '#3b82f6'};">
                      ${escHtml((r.autor_nick || '@R').replace('@', '').substring(0, 2).toUpperCase())}
                    </div>
                    <strong style="color:var(--gold-bright); font-family:var(--font-mono); font-size:12px;">${escHtml(r.autor_nick)}</strong>
                    <span style="font-size:10.5px; color:var(--text-dim); font-family:var(--font-mono);">${fechaRelativa(r.dias_atras).fecha}</span>
                  </div>
                  <span style="font-size:10px; font-family:var(--font-mono); color:var(--cyan); background:rgba(0,180,216,0.1); padding:2px 6px; border-radius:4px; border:1px solid rgba(0,180,216,0.2);">
                    ${escHtml(r.tipo_replica || 'Réplica')}
                  </span>
                </div>
                <p style="margin:0; color:var(--text-secondary); font-size:12px; line-height:1.55;">${escHtml(r.contenido)}</p>
              </div>
            `).join('') : '<div style="font-size:11.5px; color:var(--text-dim); font-style:italic;">Aún no hay réplicas en este hilo. ¡Sé la primera persona en replicar o formular una pregunta!</div>'}

            <!-- Formulario para agregar réplica directa -->
            <div class="reply-form-wrapper">
              <div style="font-family:var(--font-mono); font-size:11px; color:var(--gold-bright); margin-bottom:8px; font-weight:700;">
                💬 Escribir Réplica a este Argumento:
              </div>
              <form onsubmit="window.AuditEngine.submitReplica('${d.id}', event)">
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:8px;">
                  <input type="text" id="replyNick_${d.id}" placeholder="Tu Nick (ej. @CiudadanoLibre)" required style="background:var(--bg-card); border:1px solid var(--border-subtle); color:#fff; padding:6px 10px; border-radius:5px; font-family:var(--font-mono); font-size:11.5px;">
                  <select id="replyType_${d.id}" style="background:var(--bg-card); border:1px solid var(--border-subtle); color:#fff; padding:6px 10px; border-radius:5px; font-size:11.5px;">
                    <option value="Contrapunto Crítico">Contrapunto Crítico</option>
                    <option value="Coincidencia Argumentativa">Coincidencia Argumentativa</option>
                    <option value="Aporte de Dato Adicional">Aporte de Dato Adicional</option>
                    <option value="Pregunta de Fiscalización">Pregunta de Fiscalización</option>
                  </select>
                </div>
                <textarea id="replyText_${d.id}" placeholder="Formula tu réplica con respeto, datos o cuestionamientos de fondo..." required style="width:100%; box-sizing:border-box; background:var(--bg-card); border:1px solid var(--border-subtle); color:#fff; padding:8px 10px; border-radius:5px; font-size:12px; min-height:60px; line-height:1.5; margin-bottom:8px;"></textarea>
                <div style="display:flex; justify-content:flex-end;">
                  <button type="submit" class="calc-btn" style="padding:6px 16px; font-size:11.5px;">
                    Publicar Réplica ↗
                  </button>
                </div>
              </form>
            </div>
          </div>
        </article>
      `;
    }).join('');
  }

  function submitNuevoDebate(e) {
    if (e) e.preventDefault();
    const nickInput = document.getElementById('portalNick');
    const temaSel = document.getElementById('portalTemaSel')?.value || 'general';
    const postura = document.getElementById('portalStanceVal')?.value || 'matiz';
    const tesisInput = document.getElementById('portalTesis');
    const contenidoInput = document.getElementById('portalContenido');
    const fuenteInput = document.getElementById('portalFuente');
    const statusMsg = document.getElementById('portalFormStatusMsg');

    const nick = nickInput?.value?.trim() || '@Ciudadano';
    const tesis = tesisInput?.value?.trim();
    const contenido = contenidoInput?.value?.trim();
    const fuente = fuenteInput?.value?.trim();

    if (!tesis || !contenido) return;

    const TEMAS_MAP = {
      'presupuesto': '📊 Presupuesto & PEF',
      'megaobras': '🏗️ Megaobras & Costos',
      'legislativo': '🏛️ Poder Legislativo',
      'judicial': '⚖️ Suprema Corte SCJN',
      'politicos': '👥 Personajes & Sexenios',
      'deuda': '📈 Deuda, CETES & Banxico',
      'general': '🌐 Debate Cívico General'
    };

    const POSTURAS_MAP = {
      'a_favor': { nombre: 'A Favor', icono: '🟢' },
      'en_contra': { nombre: 'En Contra', icono: '🔴' },
      'matiz': { nombre: 'Matiz Analítico', icono: '🟡' },
      'aporte': { nombre: 'Aporte Documental', icono: '📄' }
    };

    const AVATAR_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#00b4d8', '#e056fd'];
    const randomColor = AVATAR_COLORS[Math.floor(Math.random() * AVATAR_COLORS.length)];

    const debates = getPortalDebates();
    const newDebate = {
      id: `deb-${Date.now()}`,
      tema_id: temaSel,
      tema_nombre: TEMAS_MAP[temaSel] || '🌐 Debate General',
      postura: postura,
      postura_nombre: POSTURAS_MAP[postura]?.nombre || 'Postura',
      postura_icono: POSTURAS_MAP[postura]?.icono || '⚖️',
      autor_nick: nick.startsWith('@') ? nick : `@${nick}`,
      autor_avatar_color: randomColor,
      dias_atras: 0,
      tesis: tesis,
      contenido: contenido,
      fuente: fuente || null,
      fuente_url: (fuente && (fuente.startsWith('http://') || fuente.startsWith('https://'))) ? fuente : null,
      apoyos: 1,
      replicas: []
    };

    debates.unshift(newDebate);
    if (!savePortalDebates(debates)) {
      if (statusMsg) {
        statusMsg.textContent = '✗ Este navegador no permitió guardar el hilo (puede estar en modo privado o sin espacio). Tu texto sigue en el formulario.';
        statusMsg.style.color = 'var(--crimson-bright, #e74c3c)';
      }
      return;
    }

    if (statusMsg) {
      statusMsg.textContent = '✓ Publicado en este navegador. Cuando la plataforma tenga servidor, los hilos serán visibles para todas las personas.';
      statusMsg.style.color = '#2ecc71';
      setTimeout(() => { statusMsg.innerHTML = ''; }, 4000);
    }

    // Reset form
    tesisInput.value = '';
    contenidoInput.value = '';
    if (fuenteInput) fuenteInput.value = '';
    const charCounter = document.getElementById('portalCharCount');
    if (charCounter) charCounter.textContent = '0 / 1200';

    // Re-render
    renderPortalDebates();

    // Scroll
    setTimeout(() => {
      const target = document.getElementById(newDebate.id);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        target.style.borderColor = 'var(--gold-bright)';
        target.style.boxShadow = '0 0 24px rgba(212, 175, 55, 0.45)';
        setTimeout(() => {
          target.style.borderColor = '';
          target.style.boxShadow = '';
        }, 2500);
      }
    }, 100);
  }

  function toggleReplyBox(debateId) {
    const el = document.getElementById(`replyContainer_${debateId}`);
    if (el) {
      el.style.display = (el.style.display === 'none' || !el.style.display) ? 'flex' : 'none';
      if (el.style.display === 'flex') {
        const inp = document.getElementById(`replyNick_${debateId}`);
        const curUserNick = document.getElementById('portalNick')?.value?.trim();
        if (inp && curUserNick && !inp.value) {
          inp.value = curUserNick;
        }
      }
    }
  }

  function submitReplica(debateId, e) {
    if (e) e.preventDefault();
    const nickInput = document.getElementById(`replyNick_${debateId}`);
    const typeInput = document.getElementById(`replyType_${debateId}`);
    const textInput = document.getElementById(`replyText_${debateId}`);

    const nick = nickInput?.value?.trim() || '@Ciudadano';
    const tipo = typeInput?.value || 'Réplica';
    const text = textInput?.value?.trim();

    if (!text) return;

    const AVATAR_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#00b4d8'];
    const randomColor = AVATAR_COLORS[Math.floor(Math.random() * AVATAR_COLORS.length)];

    const debates = getPortalDebates();
    const found = debates.find(d => d.id === debateId);
    if (found) {
      if (!found.replicas) found.replicas = [];
      const newRep = {
        id: `rep-${Date.now()}`,
        autor_nick: nick.startsWith('@') ? nick : `@${nick}`,
        autor_avatar_color: randomColor,
        dias_atras: 0,
        tipo_replica: tipo,
        contenido: text
      };
      found.replicas.push(newRep);
      savePortalDebates(debates);
      renderPortalDebates();
      const repContainer = document.getElementById(`replyContainer_${debateId}`);
      if (repContainer) repContainer.style.display = 'flex';
      textInput.value = '';
    }
  }

  function likeDebate(debateId) {
    const likedDebates = leerApoyosLocales();
    const debates = getPortalDebates();
    const found = debates.find(d => d.id === debateId);
    if (!found) return;

    if (likedDebates.includes(debateId)) {
      found.apoyos = Math.max(0, (found.apoyos || 1) - 1);
      const idx = likedDebates.indexOf(debateId);
      if (idx > -1) likedDebates.splice(idx, 1);
    } else {
      found.apoyos = (found.apoyos || 0) + 1;
      likedDebates.push(debateId);
    }

    try { localStorage.setItem('auditavision_liked_debates', JSON.stringify(likedDebates)); } catch (e) { /* sin almacenamiento: el apoyo no persiste */ }
    savePortalDebates(debates);
    renderPortalDebates();
  }

  function filterPortalDebates(tema) {
    activePortalForumFilter = tema;
    renderPortalDebates(tema);
  }

  function copyDebateLink(debateId) {
    /* Solo se anuncia la copia cuando ocurrio; si el navegador la niega,
       se ofrece el enlace para copiarlo a mano. */
    const url = new URL('participa.html#agora', window.location.href).href;
    const manual = () => prompt(tuUd('Copie el enlace al Portal Digital:', 'Copia el enlace al Portal Digital:'), url);
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url)
        .then(() => alert('✓ Enlace al Portal Digital copiado al portapapeles.'))
        .catch(manual);
    } else {
      manual();
    }
  }

  window.AuditEngine = {
    irABloqueComunidad: irABloqueComunidad,
    copiarObservacion: copiarObservacion,
    borrarObservacion: borrarObservacion,
    goToRef: goToRef,
    generarRandomNick: generarRandomNick,
    selectStance: selectStance,
    submitNuevoDebate: submitNuevoDebate,
    filterPortalDebates: filterPortalDebates,
    likeDebate: likeDebate,
    toggleReplyBox: toggleReplyBox,
    submitReplica: submitReplica,
    copyDebateLink: copyDebateLink,
    irAPestanaDesdeDebate: irAPestanaDesdeDebate
  };

  initComunidad();
})();
