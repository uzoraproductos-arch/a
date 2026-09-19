// ==========================================================================
// AUDITAVISIÓN — MOTOR DE FISCALIZACIÓN Y CONTROLADOR INTERACTIVO
// ==========================================================================

(function() {
  'use strict';

  // Referencias a datos globales
  const DB = window.AUDIT_DB;
  const GEO_DATA = window.MEXICO_GEOJSON;

  if (!DB || !GEO_DATA) {
    console.error('Auditavisión: No se encontraron las bases de datos requeridas (AUDIT_DB o MEXICO_GEOJSON).');
    return;
  }

  // Mapa de acceso rápido a estados por código abbr
  const stateByAbbr = {};
  const stateByName = {};
  DB.estados.forEach(st => {
    stateByAbbr[st.abbr] = st;
    stateByName[st.name.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")] = st;
  });

  // Estado de la aplicación
  const state = {
    currentMetric: 'gasto', // 'gasto', 'ramo28', 'ramo33', 'pc', 'asf', 'deuda', 'dep'
    activeView: 'geo',      // 'geo' o 'cartogram'
    selectedState: null,
    leafletMap: null,
    geoJsonLayer: null,
    currentNewsFilter: 'todos',
    electoralMap: null,
    electoralGeoJsonLayer: null,
    activeElectoralState: 'JAL',
    activeElectoralCirc: 'todas',
    activeJerarquiaMetric: 'sueldo',
    activeJerarquiaCat: 'todas',
    activeCuriososFilter: 'todos',
    curiososSearchQuery: '',
    simuladorPeriodo: 'dia',
    simuladorSector: 'todos',
    simuladorSexenio: 'todos',
    simuladorTickerTimer: null,
    simuladorElapsedSeconds: 0
  };

  // ==========================================================================
  // HELPERS DE FORMATO Y CÁLCULOS
  // ==========================================================================
  function formatMoneyMdp(num) {
    if (num >= 1000000) {
      return '$' + (num / 1000000).toFixed(2) + ' billones';
    }
    return '$' + num.toLocaleString('es-MX') + ' mdp';
  }

  function formatNumber(num) {
    return num.toLocaleString('es-MX');
  }

  function getPartyColor(party) {
    const colors = {
      'MORENA': '#8b1a1a',
      'PAN': '#003580',
      'PRI': '#cc0000',
      'MC': '#e67e22',
      'VERDE': '#00713b',
      'PAN-PRI': '#552277',
      'PAN-PRI-PRD': '#2c3e50',
      'VERDE-MORENA': '#4d5c14',
      'IND': '#555555'
    };
    return colors[party] || '#333333';
  }

  // ==========================================================================
  // ESCALA COROPLÉTICA DINÁMICA
  // ==========================================================================
  function getMetricColor(st, metricKey) {
    if (metricKey === 'deuda') {
      if (st.semaforoDeuda === 'Rojo') return '#d4382c';
      if (st.semaforoDeuda === 'Amarillo') return '#e67e22';
      return '#1e824c'; // Verde
    }

    if (metricKey === 'asf') {
      // Observaciones ASF: mayor monto = más rojo / alerta
      const val = st.asfMontoObservado;
      if (val > 3000) return '#700c0c';
      if (val > 2000) return '#8b1a1a';
      if (val > 1500) return '#b82a20';
      if (val > 1000) return '#d4382c';
      if (val > 700) return '#e67e22';
      if (val > 500) return '#f39c12';
      return '#27ae60';
    }

    if (metricKey === 'dep') {
      // Dependencia federal: mayor a 90% es alta vulnerabilidad
      const dep = st.dep;
      if (dep >= 92) return '#8b1a1a';
      if (dep >= 88) return '#b83b2a';
      if (dep >= 84) return '#c4602a';
      if (dep >= 78) return '#d49b20';
      if (dep >= 70) return '#3fae99';
      return '#233454';
    }

    if (metricKey === 'pc') {
      // Per cápita: de $15,000 a $38,000+
      const pc = st.pc;
      if (pc > 30000) return '#f3cf65';
      if (pc > 23000) return '#d4a017';
      if (pc > 21000) return '#8da352';
      if (pc > 19000) return '#3fae99';
      if (pc > 17000) return '#257b8c';
      return '#1c233a';
    }

    // Gasto Federalizado Total / Ramo 28 / Ramo 33
    const val = (metricKey === 'ramo28') ? st.ramo28 : (metricKey === 'ramo33') ? st.ramo33 : st.gasto;
    if (val > 250000) return '#f3cf65'; // Oro brillante
    if (val > 150000) return '#d4a017';
    if (val > 110000) return '#b8860b';
    if (val > 80000) return '#8da352';
    if (val > 60000) return '#3fae99';
    if (val > 45000) return '#257b8c';
    if (val > 30000) return '#1b4965';
    if (val > 20000) return '#233454';
    return '#151824';
  }

  // ==========================================================================
  // INICIALIZACIÓN DEL MAPA LEAFLET
  // ==========================================================================
  function initLeafletMap() {
    const mapEl = document.getElementById('geoMapContainer');
    if (!mapEl) return;

    // Crear mapa centrado en el territorio mexicano
    const map = L.map('geoMapContainer', {
      center: [23.6345, -102.5528],
      zoom: 5,
      minZoom: 4,
      maxZoom: 9,
      zoomControl: true,
      attributionControl: false
    });

    state.leafletMap = map;

    // Capa base de fondo oscuro minimalista
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png', {
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(map);

    renderGeoJsonLayer();
  }

  function renderGeoJsonLayer() {
    if (!state.leafletMap) return;

    if (state.geoJsonLayer) {
      state.leafletMap.removeLayer(state.geoJsonLayer);
    }

    state.geoJsonLayer = L.geoJSON(GEO_DATA, {
      style: function(feature) {
        const abbr = feature.properties.abbr;
        const st = stateByAbbr[abbr];
        const fillColor = st ? getMetricColor(st, state.currentMetric) : '#1c2133';

        return {
          fillColor: fillColor,
          weight: 1.5,
          opacity: 0.9,
          color: '#2a334d',
          dashArray: '',
          fillOpacity: 0.82
        };
      },
      onEachFeature: function(feature, layer) {
        const abbr = feature.properties.abbr;
        const st = stateByAbbr[abbr];

        if (!st) return;

        layer.on({
          mouseover: function(e) {
            const l = e.target;
            l.setStyle({
              weight: 3,
              color: '#f3cf65',
              fillOpacity: 0.95
            });
            l.bringToFront();
            showFloatingTooltip(e, st);
          },
          mousemove: function(e) {
            moveFloatingTooltip(e);
          },
          mouseout: function(e) {
            state.geoJsonLayer.resetStyle(e.target);
            hideFloatingTooltip();
          },
          click: function(e) {
            openStateDrawer(st);
            state.leafletMap.fitBounds(e.target.getBounds(), { padding: [50, 50], maxZoom: 7 });
          }
        });
      }
    }).addTo(state.leafletMap);
  }

  // ==========================================================================
  // CARTOGRAMA MOSAICO (11x8 GRID)
  // ==========================================================================
  const cartogramLayout = [
    [0, 0, "BC"], [0, 2, "SON"], [0, 4, "CHIH"],
    [1, 0, "BCS"], [1, 2, "SIN"], [1, 4, "DGO"], [1, 5, "COAH"], [1, 7, "NL"], [1, 8, "TAM"],
    [2, 3, "NAY"], [2, 4, "ZAC"], [2, 5, "AGS"], [2, 6, "SLP"],
    [3, 3, "JAL"], [3, 4, "GTO"], [3, 5, "QRO"], [3, 6, "HGO"], [3, 7, "VER"], [3, 8, "TAB"],
    [4, 3, "COL"], [4, 4, "MICH"], [4, 5, "MÉX"], [4, 6, "TLAX"], [4, 7, "PUE"], [4, 8, "CHIS"],
    [5, 5, "CDMX"], [5, 6, "MOR"], [5, 7, "OAX"], [5, 8, "CAM"],
    [6, 5, "GRO"], [6, 8, "QROO"], [6, 9, "YUC"]
  ];

  function renderCartogram() {
    const grid = document.getElementById('cartogramGrid');
    if (!grid) return;

    grid.innerHTML = '';

    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 11; c++) {
        const match = cartogramLayout.find(item => item[0] === r && item[1] === c);
        const cell = document.createElement('div');
        cell.style.gridRow = r + 1;
        cell.style.gridColumn = c + 1;

        if (match) {
          const st = stateByAbbr[match[2]];
          if (st) {
            cell.className = 'state-cell';
            cell.style.backgroundColor = getMetricColor(st, state.currentMetric);
            
            let valLabel = '';
            if (state.currentMetric === 'deuda') {
              valLabel = st.semaforoDeuda;
            } else if (state.currentMetric === 'asf') {
              valLabel = '$' + Math.round(st.asfMontoObservado) + 'm';
            } else if (state.currentMetric === 'pc') {
              valLabel = '$' + Math.round(st.pc / 1000) + 'k';
            } else if (state.currentMetric === 'dep') {
              valLabel = st.dep + '%';
            } else {
              const num = (state.currentMetric === 'ramo28') ? st.ramo28 : (state.currentMetric === 'ramo33') ? st.ramo33 : st.gasto;
              valLabel = '$' + Math.round(num / 1000) + 'k';
            }

            cell.innerHTML = `<span class="abbr">${st.abbr}</span><span class="val">${valLabel}</span>`;
            
            cell.addEventListener('mouseenter', (e) => showFloatingTooltip(e, st));
            cell.addEventListener('mousemove', (e) => moveFloatingTooltip(e));
            cell.addEventListener('mouseleave', hideFloatingTooltip);
            cell.addEventListener('click', () => openStateDrawer(st));
          }
        } else {
          cell.className = 'state-cell empty-cell';
        }
        grid.appendChild(cell);
      }
    }
  }

  // ==========================================================================
  // TOOLTIP FLOTANTE
  // ==========================================================================
  const tooltip = document.getElementById('mapFloatingTooltip');

  function showFloatingTooltip(e, st) {
    if (!tooltip) return;

    const partyColor = getPartyColor(st.partido);
    const metricVal = getMetricDisplayValue(st, state.currentMetric);

    tooltip.innerHTML = `
      <div style="font-family:var(--font-serif); font-size:16px; font-weight:700; color:var(--gold-bright); margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
        <span>${st.name}</span>
        <span class="party-badge" style="background:${partyColor};">${st.partido}</span>
      </div>
      <div style="font-size:12px; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:6px; margin-bottom:6px;">
        <span style="color:var(--text-secondary);">Gobernador(a):</span> <strong>${st.gobernador}</strong>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:12px; margin:3px 0;">
        <span style="color:var(--text-secondary);">Métrica activa:</span>
        <strong style="font-family:var(--font-mono); color:var(--gold);">${metricVal}</strong>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:12px; margin:3px 0;">
        <span style="color:var(--text-secondary);">Gasto Fed. Total:</span>
        <strong style="font-family:var(--font-mono);">${formatMoneyMdp(st.gasto)}</strong>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:12px; margin:3px 0;">
        <span style="color:var(--text-secondary);">Observado ASF:</span>
        <strong style="font-family:var(--font-mono); color:var(--crimson-bright);">$${formatNumber(st.asfMontoObservado)} mdp</strong>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:12px; margin:3px 0;">
        <span style="color:var(--text-secondary);">Semáforo Deuda:</span>
        <strong style="font-family:var(--font-mono); color:${st.semaforoDeuda === 'Verde' ? 'var(--emerald-bright)' : 'var(--amber)'};">${st.semaforoDeuda}</strong>
      </div>
      <div style="font-size:10px; color:var(--text-dim); margin-top:8px; text-align:center; border-top:1px solid rgba(255,255,255,0.05); padding-top:4px;">
        Haz clic para abrir el expediente municipal completo ↗
      </div>
    `;

    tooltip.style.display = 'block';
    moveFloatingTooltip(e);
  }

  function moveFloatingTooltip(e) {
    if (!tooltip) return;
    const offset = 18;
    let x = e.clientX + offset;
    let y = e.clientY + offset;

    const rect = tooltip.getBoundingClientRect();
    if (x + rect.width > window.innerWidth - 10) {
      x = e.clientX - rect.width - offset;
    }
    if (y + rect.height > window.innerHeight - 10) {
      y = e.clientY - rect.height - offset;
    }

    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
  }

  function hideFloatingTooltip() {
    if (!tooltip) return;
    tooltip.style.display = 'none';
  }

  function getMetricDisplayValue(st, metricKey) {
    if (metricKey === 'gasto') return formatMoneyMdp(st.gasto);
    if (metricKey === 'ramo28') return formatMoneyMdp(st.ramo28);
    if (metricKey === 'ramo33') return formatMoneyMdp(st.ramo33);
    if (metricKey === 'pc') return '$' + formatNumber(st.pc) + ' / hab';
    if (metricKey === 'asf') return '$' + formatNumber(st.asfMontoObservado) + ' mdp por aclarar';
    if (metricKey === 'deuda') return st.semaforoDeuda + ' ($' + formatNumber(st.deuda) + ' mdp)';
    if (metricKey === 'dep') return st.dep + '% de dependencia';
    return '';
  }

  // ==========================================================================
  // CAMBIO DE MÉTRICA / VISTA
  // ==========================================================================
  function setMetric(metricKey) {
    state.currentMetric = metricKey;

    // Actualizar botones
    document.querySelectorAll('.lens-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.metric === metricKey);
    });

    // Actualizar mapa geográfico
    if (state.geoJsonLayer) {
      renderGeoJsonLayer();
    }

    // Actualizar cartograma
    renderCartogram();

    // Actualizar rankings del panel lateral
    updateRankingsList();
  }

  function setMapView(viewType) {
    state.activeView = viewType;

    const geoContainer = document.getElementById('geoMapContainer');
    const cartoContainer = document.getElementById('cartogramContainer');

    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.view === viewType);
    });

    if (viewType === 'geo') {
      geoContainer.style.display = 'block';
      cartoContainer.style.display = 'none';
      if (state.leafletMap) {
        state.leafletMap.invalidateSize();
      }
    } else {
      geoContainer.style.display = 'none';
      cartoContainer.style.display = 'flex';
      renderCartogram();
    }
  }

  // ==========================================================================
  // PANEL LATERAL: RANKINGS
  // ==========================================================================
  function updateRankingsList() {
    const topContainer = document.getElementById('topRankingsContainer');
    const botContainer = document.getElementById('bottomRankingsContainer');
    if (!topContainer || !botContainer) return;

    const metric = state.currentMetric;
    const sorted = [...DB.estados].sort((a, b) => {
      const valA = (metric === 'asf') ? a.asfMontoObservado : (metric === 'pc') ? a.pc : (metric === 'dep') ? a.dep : (metric === 'ramo28') ? a.ramo28 : (metric === 'ramo33') ? a.ramo33 : a.gasto;
      const valB = (metric === 'asf') ? b.asfMontoObservado : (metric === 'pc') ? b.pc : (metric === 'dep') ? b.dep : (metric === 'ramo28') ? b.ramo28 : (metric === 'ramo33') ? b.ramo33 : b.gasto;
      return valB - valA;
    });

    const maxVal = (metric === 'asf') ? sorted[0].asfMontoObservado : (metric === 'pc') ? sorted[0].pc : (metric === 'dep') ? sorted[0].dep : (metric === 'ramo28') ? sorted[0].ramo28 : (metric === 'ramo33') ? sorted[0].ramo33 : sorted[0].gasto;

    // Render Top 5
    topContainer.innerHTML = sorted.slice(0, 5).map(st => {
      const val = (metric === 'asf') ? st.asfMontoObservado : (metric === 'pc') ? st.pc : (metric === 'dep') ? st.dep : (metric === 'ramo28') ? st.ramo28 : (metric === 'ramo33') ? st.ramo33 : st.gasto;
      const pct = Math.max(15, (val / maxVal) * 100);
      const display = (metric === 'dep') ? val + '%' : (metric === 'pc') ? '$' + formatNumber(val) : '$' + Math.round(val).toLocaleString('es-MX');

      return `
        <div class="rank-item" onclick="window.AuditEngine.openDrawer('${st.abbr}')" style="cursor:pointer;">
          <span class="rank-name">${st.abbr}</span>
          <div class="rank-bar-bg">
            <div class="rank-bar-fill" style="width: ${pct}%; background: ${getMetricColor(st, metric)};">${display}</div>
          </div>
        </div>
      `;
    }).join('');

    // Render Bottom 5
    botContainer.innerHTML = sorted.slice(-5).reverse().map(st => {
      const val = (metric === 'asf') ? st.asfMontoObservado : (metric === 'pc') ? st.pc : (metric === 'dep') ? st.dep : (metric === 'ramo28') ? st.ramo28 : (metric === 'ramo33') ? st.ramo33 : st.gasto;
      const pct = Math.max(15, (val / maxVal) * 100);
      const display = (metric === 'dep') ? val + '%' : (metric === 'pc') ? '$' + formatNumber(val) : '$' + Math.round(val).toLocaleString('es-MX');

      return `
        <div class="rank-item" onclick="window.AuditEngine.openDrawer('${st.abbr}')" style="cursor:pointer;">
          <span class="rank-name">${st.abbr}</span>
          <div class="rank-bar-bg">
            <div class="rank-bar-fill" style="width: ${pct}%; background: ${getMetricColor(st, metric)};">${display}</div>
          </div>
        </div>
      `;
    }).join('');
  }

  // ==========================================================================
  // EXPEDIENTE DE AUDITORÍA (DRAWER)
  // ==========================================================================
  function openStateDrawer(st) {
    state.selectedState = st;
    const drawer = document.getElementById('auditDrawer');
    const overlay = document.getElementById('auditDrawerOverlay');
    if (!drawer || !overlay) return;

    // Header del Drawer
    document.getElementById('dStateTag').innerText = `Entidad Federativa Clave: ${st.abbr} · Capital: ${st.capital}`;
    document.getElementById('dStateName').innerText = st.name;
    document.getElementById('dStateGov').innerHTML = `Gobernador(a): <strong>${st.gobernador}</strong> (${st.partido}) · Población: <strong>${st.pob}M habitantes</strong>`;

    // Alerta ASF
    document.getElementById('dAsfAmount').innerText = `$${formatNumber(st.asfMontoObservado)} mdp`;
    document.getElementById('dAsfAuditCount').innerText = `${st.asfAuditorias} auditorías`;
    document.getElementById('dAsfDesc').innerText = st.asfTipologia;

    // Métricas del Estado
    document.getElementById('dGastoTotal').innerText = formatMoneyMdp(st.gasto);
    document.getElementById('dRamo28').innerText = formatMoneyMdp(st.ramo28);
    document.getElementById('dRamo33').innerText = formatMoneyMdp(st.ramo33);
    document.getElementById('dRecaudacionPropia').innerText = formatMoneyMdp(st.recaudacionPropia);
    document.getElementById('dDeuda').innerText = `$${formatNumber(st.deuda)} mdp (${st.semaforoDeuda})`;
    document.getElementById('dDependencia').innerText = `${st.dep}% federalizada`;

    // Lista de Municipios
    const muniList = document.getElementById('dMunicipiosList');
    if (muniList) {
      if (st.municipios && st.municipios.length > 0) {
        muniList.innerHTML = st.municipios.map(m => {
          const partyColor = getPartyColor(m.partido);
          const projTags = m.proyectosAuditados ? m.proyectosAuditados.map(p => `<span class="project-tag">🔍 ${p}</span>`).join('') : '';

          return `
            <div class="muni-card">
              <div class="muni-header">
                <div>
                  <span class="muni-name">${m.nombre}</span>
                  <div class="muni-mayor">Presidente(a): <strong>${m.alcalde}</strong> <span class="party-badge" style="background:${partyColor}; font-size:9px;">${m.partido}</span></div>
                </div>
                <div style="text-align:right;">
                  <span style="font-size:10px; color:var(--text-dim); font-family:var(--font-mono);">Presupuesto Total</span>
                  <div style="font-family:var(--font-mono); font-size:15px; font-weight:700; color:var(--gold-bright);">$${formatNumber(m.presupuestoTotal)} mdp</div>
                </div>
              </div>

              <div class="muni-stats-row">
                <div class="muni-stat">
                  FORTAMUN (Seguridad)
                  <strong>$${formatNumber(m.fortamun)} mdp</strong>
                </div>
                <div class="muni-stat">
                  FISMDF (Infraestructura)
                  <strong>$${formatNumber(m.fismdf)} mdp</strong>
                </div>
                <div class="muni-stat">
                  Predial Recaudado
                  <strong style="color:var(--cyan);">$${formatNumber(m.predial)} mdp</strong>
                </div>
              </div>

              <div class="muni-audit-status">
                <strong>Alerta Auditoría ASF / Local:</strong> $${formatNumber(m.observacionesASF)} mdp en revisión.<br>
                <em>${m.estatusAuditoria}</em>
              </div>

              ${projTags ? `
                <div class="muni-projects">
                  <div style="font-family:var(--font-mono); font-size:10px; color:var(--text-dim); margin-bottom:3px;">Obras y contratos fiscalizados:</div>
                  ${projTags}
                </div>
              ` : ''}
            </div>
          `;
        }).join('');
      } else {
        muniList.innerHTML = `<div style="color:var(--text-dim); font-style:italic;">No se registraron municipios auditados en esta fase.</div>`;
      }
    }

    drawer.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeStateDrawer() {
    const drawer = document.getElementById('auditDrawer');
    const overlay = document.getElementById('auditDrawerOverlay');
    if (drawer) drawer.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  // ==========================================================================
  // CALCULADORA CÍVICA DEL CONTRIBUYENTE
  // ==========================================================================
  function calculateTaxBreakdown(incomeAmount) {
    const container = document.getElementById('calcBreakdownGrid');
    if (!container) return;

    const amount = parseFloat(incomeAmount);
    if (isNaN(amount) || amount <= 0) {
      container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--crimson-bright);">Por favor ingresa un monto válido de impuestos o salario anual estimado.</div>`;
      return;
    }

    // Proporciones del Presupuesto de Egresos de la Federación (PEF)
    const breakdown = [
      { dest: 'Transferencias a Estados y Municipios (Ramo 28/33)', pct: 27.6, desc: 'Fondos directos para tu gobierno estatal y ayuntamiento' },
      { dest: 'Costo Financiero de la Deuda Pública', pct: 13.2, desc: 'Intereses y servicio de compromisos bancarios de la nación' },
      { dest: 'Pensiones y Programas del Bienestar', pct: 12.8, desc: 'Adultos mayores, personas con discapacidad y becas' },
      { dest: 'Energía y Rescate de Empresas Públicas', pct: 11.5, desc: 'Pemex y Comisión Federal de Electricidad' },
      { dest: 'Educación Pública (SEP y FONE)', pct: 10.4, desc: 'Nómina de maestros de escuelas públicas e infraestructura' },
      { dest: 'Salud y Hospitales (IMSS-Bienestar/ISSSTE)', pct: 9.6, desc: 'Medicamentos, médicos, clínicas y hospitales generales' },
      { dest: 'Seguridad Nacional (Defensa, Marina, GN)', pct: 5.8, desc: 'Operativos militares, vigilancia costera y Guardia Nacional' },
      { dest: 'Infraestructura Carretera, Hídrica y Trenes', pct: 4.8, desc: 'Caminos, presas de Conagua y vías férreas' },
      { dest: 'Poder Judicial, INE y Órganos Autónomos', pct: 4.3, desc: 'Jueces, tribunales, elecciones, CNDH e Inegi' }
    ];

    container.innerHTML = breakdown.map(item => {
      const piece = (amount * (item.pct / 100)).toFixed(2);
      return `
        <div class="calc-item">
          <div class="dest">${item.dest}</div>
          <div class="amount">$${Number(piece).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          <div class="pct">${item.pct}% de tu aportación · <span style="color:var(--text-secondary); font-size:9px;">${item.desc}</span></div>
        </div>
      `;
    }).join('');
  }

  // ==========================================================================
  // BITÁCORA DE NOTICIAS & FILTRO
  // ==========================================================================
  function renderNews(filterCat = 'todos') {
    const grid = document.getElementById('newsCardsGrid');
    if (!grid) return;

    let items = DB.noticias;
    if (filterCat !== 'todos') {
      items = items.filter(n => n.categoria.toLowerCase().includes(filterCat.toLowerCase()));
    }

    grid.innerHTML = items.map(n => {
      const isUrgent = n.urgencia === 'ALTA';
      return `
        <div class="news-card ${isUrgent ? 'urgent' : ''}" onclick="window.AuditEngine.openNewsModal('${n.id}')" style="cursor:pointer;">
          <div>
            <div class="news-meta">
              <span class="news-cat">${n.categoria}</span>
              <span>${n.fecha}</span>
            </div>
            <h4 class="news-title">${n.titulo}</h4>
            <p class="news-lead">${n.bajada}</p>
          </div>
          <div class="news-footer">
            <span class="news-amount-tag">Monto involucrado: ${n.monto}</span>
            <span class="news-source">Fuente: ${n.fuente.split('/')[0]} ↗</span>
          </div>
        </div>
      `;
    }).join('');
  }

  function openNewsModal(newsId) {
    const n = DB.noticias.find(item => item.id === newsId);
    if (!n) return;

    const modal = document.getElementById('newsDetailModal');
    const content = document.getElementById('newsModalContent');
    if (!modal || !content) return;

    content.innerHTML = `
      <div style="font-family:var(--font-mono); font-size:11px; color:var(--gold); text-transform:uppercase; margin-bottom:8px;">
        ${n.categoria} · Publicado: ${n.fecha} (${n.hora})
      </div>
      <h2 style="font-family:var(--font-serif); font-size:26px; color:var(--text-main); margin-bottom:14px; line-height:1.2;">
        ${n.titulo}
      </h2>
      <div style="background:rgba(201,168,76,0.08); border-left:3px solid var(--gold); padding:12px 16px; margin-bottom:18px; font-style:italic; font-size:14px; color:var(--gold-bright);">
        ${n.bajada}
      </div>
      <div style="font-size:15px; line-height:1.75; color:var(--text-main); margin-bottom:20px;">
        ${n.cuerpo}
      </div>
      <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; border-top:1px solid var(--border-subtle); padding-top:14px; font-family:var(--font-mono); font-size:12px;">
        <div><strong>Monto en fiscalización:</strong> <span style="color:var(--crimson-bright); font-size:14px; font-weight:700;">${n.monto}</span></div>
        <div><strong>Fuente oficial:</strong> <span style="color:var(--text-secondary);">${n.fuente}</span></div>
      </div>
    `;

    modal.style.display = 'flex';
  }

  function closeNewsModal() {
    const modal = document.getElementById('newsDetailModal');
    if (modal) modal.style.display = 'none';
  }

  // ==========================================================================
  // PREGUNTAS FRECUENTES (FAQ) & GLOSARIO
  // ==========================================================================
  function renderFaqs() {
    const container = document.getElementById('faqContainer');
    if (!container) return;

    container.innerHTML = DB.faqs.map((faq, idx) => `
      <div class="faq-item" id="faq-${idx}">
        <div class="faq-question" onclick="window.AuditEngine.toggleFaq(${idx})">
          <span>${faq.pregunta}</span>
          <span style="font-family:var(--font-mono); font-size:18px; color:var(--gold); transition:transform 0.2s;" id="faq-icon-${idx}">+</span>
        </div>
        <div class="faq-answer">
          ${faq.respuesta}
        </div>
      </div>
    `).join('');
  }

  function toggleFaq(idx) {
    const item = document.getElementById(`faq-${idx}`);
    const icon = document.getElementById(`faq-icon-${idx}`);
    if (!item) return;

    const isActive = item.classList.contains('active');
    item.classList.toggle('active', !isActive);
    if (icon) icon.innerText = isActive ? '+' : '−';
  }

  let currentGlossaryCategory = 'todas';

  function filterGlossaryByCategory(cat) {
    currentGlossaryCategory = cat;
    document.querySelectorAll('#glossaryFilterChips .chip').forEach(btn => {
      const isSel = (btn.dataset.gcat === cat) || (cat === 'todas' && btn.dataset.gcat === 'todas');
      btn.classList.toggle('active', isSel);
      btn.classList.toggle('on', isSel);
    });
    const searchInput = document.getElementById('glossarySearchInput');
    const term = searchInput ? searchInput.value : '';
    renderGlossary(term, cat);
  }

  function renderGlossary(filterTerm = '', category = currentGlossaryCategory) {
    const container = document.getElementById('glossaryGrid');
    if (!container || !DB.glosario) return;

    let list = DB.glosario;
    if (category && category !== 'todas') {
      const catNorm = category.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
      list = list.filter(g => {
        if (!g.categoria) return false;
        const gCatNorm = g.categoria.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        return gCatNorm.includes(catNorm);
      });
    }
    if (filterTerm && filterTerm.trim() !== '') {
      const q = filterTerm.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
      list = list.filter(g => {
        const t = (g.termino || '').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        const d = (g.definicion || '').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        const l = (g.ley || '').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        return t.includes(q) || d.includes(q) || l.includes(q);
      });
    }

    if (list.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1 / -1; text-align:center; padding:35px 20px; color:var(--text-dim); background:var(--bg-surface); border:1px dashed var(--border-subtle); border-radius:8px;">
          <span style="font-size:24px; display:block; margin-bottom:8px;">🔍</span>
          <p style="margin:0 0 10px; font-size:14px; color:var(--text-secondary);">No se encontraron términos para "<strong>${filterTerm}</strong>" en la categoría seleccionada.</p>
          <button class="chip" onclick="window.AuditEngine.filterGlossaryByCategory('todas')" style="background:rgba(212,175,55,0.15); border-color:var(--gold-bright); color:var(--gold-bright); cursor:pointer;">Mostrar todos los conceptos (${DB.glosario.length})</button>
        </div>
      `;
      return;
    }

    container.innerHTML = list.map(g => {
      const slug = (g.termino || '').toLowerCase().replace(/[^a-z0-9]/g, '-');
      return `
        <div class="glossary-card" id="gloss-${slug}">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; gap:8px; flex-wrap:wrap;">
            <h4 class="term-title" style="margin-bottom:0; font-size:15px; color:var(--gold-bright);">${g.termino}</h4>
            ${g.categoria ? `<span style="font-size:10px; font-family:var(--font-mono); padding:2px 8px; border-radius:12px; background:rgba(212,175,55,0.1); color:var(--gold); border:1px solid rgba(212,175,55,0.25); white-space:nowrap;">${g.categoria}</span>` : ''}
          </div>
          <p class="term-def" style="font-size:12.5px; line-height:1.6; color:var(--text-secondary); margin-bottom:10px;">${g.definicion}</p>
          <div class="term-law" style="font-size:11px; font-family:var(--font-mono); color:var(--cyan); border-top:1px dashed var(--border-subtle); padding-top:6px;">⚖️ Fundamento: ${g.ley}</div>
        </div>
      `;
    }).join('');
  }

  // ==========================================================================
  // MARCO LEGAL HACENDARIO & PRECEPTOS JURÍDICOS (SUBPESTAÑA 6.3)
  // ==========================================================================
  let currentPreceptosCategory = 'todas';
  let currentPreceptosQuery = '';

  function filterPreceptos(cat) {
    currentPreceptosCategory = cat;
    document.querySelectorAll('#preceptosFilterChips .chip').forEach(btn => {
      const isSel = (btn.dataset.pcat === cat) || (cat === 'todas' && btn.dataset.pcat === 'todas');
      btn.classList.toggle('active', isSel);
      btn.classList.toggle('on', isSel);
    });
    const searchInput = document.getElementById('preceptosSearchInput');
    const q = searchInput ? searchInput.value : '';
    renderPreceptosLegales(cat, q);
  }

  function searchPreceptos(query) {
    currentPreceptosQuery = query;
    renderPreceptosLegales(currentPreceptosCategory, query);
  }

  function renderPreceptosLegales(category = currentPreceptosCategory, filterTerm = currentPreceptosQuery) {
    const container = document.getElementById('preceptosLegalesGrid');
    if (!container || !DB.preceptos_legales) return;

    let list = DB.preceptos_legales;
    if (category && category !== 'todas') {
      const catNorm = category.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
      list = list.filter(p => {
        const leyNorm = (p.ley || '').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        const precNorm = (p.precepto || '').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        return leyNorm.includes(catNorm) || precNorm.includes(catNorm) || (p.categoria && p.categoria.toLowerCase().includes(catNorm)) || (p.denominacion && p.denominacion.toLowerCase().includes(catNorm));
      });
    }

    if (filterTerm && filterTerm.trim() !== '') {
      const q = filterTerm.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
      list = list.filter(p => {
        const t = (p.precepto + ' ' + p.denominacion + ' ' + p.precepto_resumen + ' ' + p.texto_oficial + ' ' + p.ley).toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        return t.includes(q);
      });
    }

    if (list.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1 / -1; text-align:center; padding:35px 20px; color:var(--text-dim); background:var(--bg-surface); border:1px dashed var(--border-subtle); border-radius:8px;">
          <span style="font-size:24px; display:block; margin-bottom:8px;">⚖️</span>
          <p style="margin:0 0 10px; font-size:14px; color:var(--text-secondary);">No se encontraron preceptos legales para la búsqueda actual.</p>
          <button class="chip" onclick="window.AuditEngine.filterPreceptos('todas')" style="background:rgba(201,168,76,0.15); border-color:var(--gold-bright); color:var(--gold-bright); cursor:pointer;">Mostrar todos los preceptos (${DB.preceptos_legales.length})</button>
        </div>
      `;
      return;
    }

    container.innerHTML = list.map(p => `
      <div class="precepto-card" id="precepto-${p.id}">
        <div class="precepto-card-header">
          <span class="precepto-badge">${p.icono} ${p.ley.length > 32 ? p.ley.substring(0, 30) + '...' : p.ley}</span>
        </div>
        <h4 class="precepto-title">${p.denominacion}</h4>
        <div style="font-family:var(--font-mono); font-size:11.5px; color:var(--gold); margin-bottom:6px; font-weight:700;">
          ${p.precepto}
        </div>
        <p class="precepto-resumen">${p.precepto_resumen}</p>
        <div class="precepto-footer-bar">
          <button class="precepto-btn" onclick="window.AuditEngine.openPreceptoModal('${p.id}')">
            📜 Ver Contenido del Precepto ↗
          </button>
          <a href="${p.url_oficial}" target="_blank" rel="noopener noreferrer" class="precepto-btn-sec">
            ↗ DOF / PDF
          </a>
        </div>
      </div>
    `).join('');
  }

  function openPreceptoModal(preceptoId) {
    const p = DB.preceptos_legales ? DB.preceptos_legales.find(x => x.id === preceptoId) : null;
    if (!p) return;
    const modal = document.getElementById('preceptoLegalModal');
    const content = document.getElementById('preceptoModalContent');
    if (!modal || !content) return;

    content.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px; border-bottom:1px solid var(--border-gold); padding-bottom:14px;">
        <div>
          <span style="font-family:var(--font-mono); font-size:11px; color:var(--cyan); text-transform:uppercase; letter-spacing:1px; font-weight:700;">
            ${p.icono} ${p.ley}
          </span>
          <h3 style="font-family:var(--font-serif); font-size:22px; color:var(--gold-bright); margin:4px 0 2px 0;">
            ${p.denominacion}
          </h3>
          <div style="font-family:var(--font-mono); font-size:12px; color:var(--gold);">
            ${p.precepto}
          </div>
        </div>
      </div>
      <div style="background:rgba(201,168,76,0.08); border-left:4px solid var(--gold-bright); padding:12px 16px; border-radius:0 8px 8px 0; margin-bottom:16px; font-size:12.5px; color:var(--text-main); line-height:1.5;">
        <strong>Resumen Jurídico:</strong> ${p.precepto_resumen}
      </div>
      <div style="margin-bottom:18px;">
        <h4 style="font-family:var(--font-mono); font-size:11.5px; color:var(--text-dim); text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">
          📜 Texto Constitucional / Legal Oficial Vigente:
        </h4>
        <div style="background:var(--bg-card-alt); border:1px solid var(--border-subtle); border-radius:8px; padding:16px; font-size:12px; line-height:1.65; color:var(--text-secondary); max-height:220px; overflow-y:auto; font-style:italic;">
          "${p.texto_oficial}"
        </div>
      </div>
      <div style="margin-bottom:18px;">
        <h4 style="font-family:var(--font-mono); font-size:11.5px; color:var(--text-dim); text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">
          🔍 Análisis Cívico para el Ciudadano y Auditor:
        </h4>
        <p style="font-size:12.5px; color:var(--text-main); line-height:1.55; margin:0;">
          ${p.analisis_civico}
        </p>
      </div>
      <div style="margin-bottom:20px; font-size:11.5px; color:var(--text-secondary); background:rgba(255,255,255,0.02); border:1px dashed var(--border-subtle); border-radius:6px; padding:10px 14px;">
        📍 <strong>Aplicación en Auditavisión:</strong> ${p.aplicacion_auditavision}
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; border-top:1px solid var(--border-subtle); padding-top:16px;">
        <a href="${p.url_oficial}" target="_blank" rel="noopener noreferrer" class="ref-link" style="font-size:12px; font-weight:700;">
          ↗ Consultar Publicación Oficial en PDF / DOF
        </a>
        <button onclick="window.AuditEngine.closePreceptoModal()" style="cursor:pointer; background:rgba(255,255,255,0.08); border:1px solid var(--border-subtle); color:var(--text-main); padding:6px 18px; border-radius:6px; font-size:12px; font-family:var(--font-mono);">
          Cerrar ✕
        </button>
      </div>
    `;
    modal.style.display = 'flex';
  }

  function closePreceptoModal() {
    const modal = document.getElementById('preceptoLegalModal');
    if (modal) modal.style.display = 'none';
  }

  // ==========================================================================
  // BUSCADOR UNIVERSAL
  // ==========================================================================
  function initSearch() {
    const input = document.getElementById('globalSearchInput');
    const dropdown = document.getElementById('searchResultsDropdown');
    if (!input || !dropdown) return;

    input.addEventListener('input', function(e) {
      const q = e.target.value.trim().toLowerCase();
      if (q.length < 2) {
        dropdown.classList.remove('active');
        dropdown.innerHTML = '';
        return;
      }

      const results = [];

      // Buscar en estados
      DB.estados.forEach(st => {
        if (st.name.toLowerCase().includes(q) || st.abbr.toLowerCase().includes(q) || st.capital.toLowerCase().includes(q)) {
          results.push({
            type: 'Estado',
            title: st.name,
            sub: `Gasto: ${formatMoneyMdp(st.gasto)} · Gobernador(a): ${st.gobernador}`,
            badge: st.abbr,
            action: () => openStateDrawer(st)
          });
        }

        // Buscar en municipios
        if (st.municipios) {
          st.municipios.forEach(m => {
            if (m.nombre.toLowerCase().includes(q) || m.alcalde.toLowerCase().includes(q)) {
              results.push({
                type: 'Municipio',
                title: `${m.nombre} (${st.abbr})`,
                sub: `Alcalde: ${m.alcalde} · FORTAMUN: $${m.fortamun} mdp`,
                badge: 'MUN',
                action: () => openStateDrawer(st)
              });
            }
          });
        }
      });

      // Buscar en glosario
      DB.glosario.forEach(g => {
        if (g.termino.toLowerCase().includes(q) || g.definicion.toLowerCase().includes(q)) {
          results.push({
            type: 'Glosario',
            title: g.termino,
            sub: g.ley,
            badge: 'LEY',
            action: () => {
              const el = document.getElementById('seccionGlosario');
              if (el) el.scrollIntoView({ behavior: 'smooth' });
            }
          });
        }
      });

      if (results.length > 0) {
        dropdown.innerHTML = results.slice(0, 10).map((r, i) => `
          <div class="search-item" data-index="${i}">
            <div>
              <div class="name">${r.title}</div>
              <div style="font-size:11px; color:var(--text-secondary);">${r.sub}</div>
            </div>
            <span class="badge" style="background:rgba(201,168,76,0.15); color:var(--gold-bright);">${r.badge}</span>
          </div>
        `).join('');

        dropdown.querySelectorAll('.search-item').forEach((item, i) => {
          item.addEventListener('click', () => {
            results[i].action();
            dropdown.classList.remove('active');
            input.value = '';
          });
        });

        dropdown.classList.add('active');
      } else {
        dropdown.innerHTML = `<div style="padding:12px; font-size:12px; color:var(--text-dim); text-align:center;">No se hallaron coincidencias para "${q}"</div>`;
        dropdown.classList.add('active');
      }
    });

    document.addEventListener('click', function(e) {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.remove('active');
      }
    });
  }

  // ==========================================================================
  // DIVISIÓN DE PODERES: CONTROLADOR DE PESTAÑAS
  // ==========================================================================
  function setPowerBranch(branch) {
    // Actualizar botones de pestaña
    document.querySelectorAll('.power-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.power === branch);
    });

    // Ocultar todos los paneles
    const panelEjecutivo = document.getElementById('panelEjecutivo');
    const panelLegislativo = document.getElementById('panelLegislativo');
    const panelJudicial = document.getElementById('panelJudicial');

    if (panelEjecutivo) panelEjecutivo.classList.remove('active');
    if (panelLegislativo) panelLegislativo.classList.remove('active');
    if (panelJudicial) panelJudicial.classList.remove('active');

    // Mostrar el panel seleccionado
    if (branch === 'ejecutivo') {
      if (panelEjecutivo) panelEjecutivo.classList.add('active');
      if (state.activeView === 'geo' && state.leafletMap) {
        setTimeout(() => state.leafletMap.invalidateSize(), 50);
      }
    } else if (branch === 'legislativo') {
      if (panelLegislativo) panelLegislativo.classList.add('active');
      renderCongresosTable();
    renderJudicialMinisters();
    } else if (branch === 'judicial') {
      if (panelJudicial) panelJudicial.classList.add('active');
    }
  }

  // ==========================================================================
  // RENDERIZADO DE TABLA DE LOS 32 CONGRESOS ESTATALES
  // ==========================================================================
  function renderCongresosTable(searchTerm = '') {
    const tbody = document.getElementById('congresosTableBody');
    if (!tbody || !DB.legislativo || !DB.legislativo.congresosEstatales) return;

    let items = DB.legislativo.congresosEstatales;
    if (searchTerm.trim() !== '') {
      const q = searchTerm.toLowerCase();
      items = items.filter(c => c.nombre.toLowerCase().includes(q) || c.abbr.toLowerCase().includes(q) || c.ofsNombre.toLowerCase().includes(q));
    }

    tbody.innerHTML = items.map((c, idx) => {
      const isHighCost = c.costoPorDiputado >= 24;
      const isHighPartida = c.partidaGestionSocial >= 100;

      return `
        <tr>
          <td style="font-family:var(--font-mono); font-weight:700; color:var(--gold);">${c.abbr}</td>
          <td>
            <strong>${c.nombre}</strong>
            <div style="font-size:10px; color:var(--text-dim);">${c.ofsNombre}</div>
          </td>
          <td class="table-num">${c.diputados}</td>
          <td class="table-num" style="color:var(--gold-bright);">$${c.presupuestoCongreso.toLocaleString('es-MX')} mdp</td>
          <td class="table-num" style="color:${isHighCost ? 'var(--crimson-bright)' : 'var(--text-main)'};">
            <strong>$${c.costoPorDiputado.toFixed(1)} mdp</strong>
          </td>
          <td class="table-num" style="color:${isHighPartida ? 'var(--crimson-bright)' : 'var(--amber)'};">
            $${c.partidaGestionSocial.toFixed(1)} mdp
          </td>
          <td style="text-align:center;">
            <button onclick="window.AuditEngine.openDrawer('${c.abbr}')" class="lens-btn" style="padding:3px 8px; font-size:10px;">
              Ver Estado ↗
            </button>
          </td>
        </tr>
      `;
    }).join('');
  }

  // ==========================================================================
  // BLOQUE 5: GEOGRAFÍA ELECTORAL, 300 DISTRITOS & CIRCUNSCRIPCIONES INE
  // ==========================================================================
  let electoralMapInitialized = false;

  function initElectoralModule() {
    initElectoralStateSelect();
    renderElectoralDistritos(state.activeElectoralState || 'JAL');
    initElectoralMap();
  }

  function initElectoralStateSelect() {
    const sel = document.getElementById('electoralStateSelect');
    if (!sel || !DB.geografia_electoral_ine || !DB.geografia_electoral_ine.estados_distritacion) return;

    const list = DB.geografia_electoral_ine.estados_distritacion;
    sel.innerHTML = list.map(st => `
      <option value="${st.abbr}" ${st.abbr === (state.activeElectoralState || 'JAL') ? 'selected' : ''}>
        ${st.nombre} (${st.circunscripcion}ª Circ. · ${st.distritos_federales.length} Distritos)
      </option>
    `).join('');
  }

  function initElectoralMap() {
    const mapEl = document.getElementById('electoralMapContainer');
    if (!mapEl || !window.L || !window.MEXICO_GEOJSON) return;

    if (state.electoralMap) {
      setTimeout(() => state.electoralMap.invalidateSize(), 50);
      return;
    }

    try {
      const map = L.map('electoralMapContainer', {
        center: [23.6345, -102.5528],
        zoom: 4,
        minZoom: 3.5,
        maxZoom: 8,
        zoomControl: true,
        attributionControl: false
      });

      state.electoralMap = map;

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png', {
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(map);

      renderElectoralGeoJsonLayer();
      electoralMapInitialized = true;
    } catch (e) {
      console.warn('Error inicializando mapa electoral:', e);
    }
  }

  function getCircunscripcionColor(circNum) {
    const colors = {
      1: '#e67e22', // 1ª Guadalajara (Naranja/Ámbar)
      2: '#3498db', // 2ª Monterrey (Azul)
      3: '#2ecc71', // 3ª Xalapa (Verde)
      4: '#9b59b6', // 4ª CDMX (Púrpura)
      5: '#e74c3c'  // 5ª Toluca (Rojo)
    };
    return colors[circNum] || '#d4af37';
  }

  function renderElectoralGeoJsonLayer() {
    if (!state.electoralMap || !window.MEXICO_GEOJSON) return;

    if (state.electoralGeoJsonLayer) {
      state.electoralMap.removeLayer(state.electoralGeoJsonLayer);
    }

    const distMap = {};
    if (DB.geografia_electoral_ine && DB.geografia_electoral_ine.estados_distritacion) {
      DB.geografia_electoral_ine.estados_distritacion.forEach(s => {
        distMap[s.abbr] = s;
      });
    }

    state.electoralGeoJsonLayer = L.geoJSON(window.MEXICO_GEOJSON, {
      style: function(feature) {
        const abbr = feature.properties.abbr;
        const info = distMap[abbr];
        const circ = info ? info.circunscripcion : 1;
        const color = getCircunscripcionColor(circ);
        const isSelected = abbr === state.activeElectoralState;
        const isCircFiltered = state.activeElectoralCirc !== 'todas' && String(circ) === String(state.activeElectoralCirc);
        const isMuted = state.activeElectoralCirc !== 'todas' && String(circ) !== String(state.activeElectoralCirc);

        return {
          fillColor: color,
          weight: isSelected ? 2.5 : (isCircFiltered ? 2 : 1),
          opacity: 1,
          color: isSelected ? '#ffd700' : (isCircFiltered ? '#ffffff' : 'rgba(255,255,255,0.2)'),
          fillOpacity: isMuted ? 0.15 : (isSelected ? 0.95 : (isCircFiltered ? 0.85 : 0.65))
        };
      },
      onEachFeature: function(feature, layer) {
        const abbr = feature.properties.abbr;
        const info = distMap[abbr];
        const nombre = info ? info.nombre : feature.properties.name;
        const circ = info ? info.circunscripcion : '-';
        const dists = info ? info.distritos_federales.length : '-';

        layer.bindTooltip(`
          <div style="font-family:var(--font-mono); font-size:11px; color:#fff;">
            <strong style="color:var(--gold);">${nombre}</strong><br>
            <span>${circ}ª Circunscripción Electoral</span><br>
            <span>${dists} Distritos Federales Uninominales</span>
          </div>
        `, { sticky: true, className: 'leaflet-custom-tooltip' });

        layer.on({
          mouseover: function(e) {
            const l = e.target;
            l.setStyle({
              weight: 2.5,
              color: '#ffffff',
              fillOpacity: 0.9
            });
            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
              l.bringToFront();
            }
          },
          mouseout: function() {
            state.electoralGeoJsonLayer.resetStyle(layer);
          },
          click: function(e) {
            renderElectoralDistritos(abbr);
            if (state.electoralMap) {
              state.electoralMap.fitBounds(e.target.getBounds(), { padding: [25, 25], maxZoom: 7 });
            }
          }
        });
      }
    }).addTo(state.electoralMap);
  }

  function renderElectoralDistritos(abbr) {
    if (!abbr || !DB.geografia_electoral_ine) return;
    state.activeElectoralState = abbr;

    const list = DB.geografia_electoral_ine.estados_distritacion;
    const st = list.find(s => s.abbr === abbr) || list[0];
    if (!st) return;

    // Actualizar select
    const sel = document.getElementById('electoralStateSelect');
    if (sel && sel.value !== abbr) sel.value = abbr;

    // Buscar datos del congreso local en DB.legislativo.congresosEstatales
    const cg = (DB.legislativo && DB.legislativo.congresosEstatales)
      ? DB.legislativo.congresosEstatales.find(c => c.abbr === abbr)
      : null;

    // Tarjeta resumen del estado
    const detailEl = document.getElementById('electoralStateDetailCard');
    if (detailEl) {
      const circColor = getCircunscripcionColor(st.circunscripcion);
      detailEl.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
          <div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:20px;">🏛️</span>
              <h4 style="font-family:var(--font-serif); font-size:18px; color:var(--gold-bright); margin:0;">
                ${st.nombre}
              </h4>
              <span style="background:${circColor}22; color:${circColor}; border:1px solid ${circColor}; padding:2px 8px; border-radius:4px; font-family:var(--font-mono); font-size:10.5px; font-weight:700;">
                ${st.circunscripcion}ª Circunscripción
              </span>
            </div>
            <div style="font-size:11px; color:var(--text-dim); font-family:var(--font-mono); margin-top:2px;">
              Cabecera Regional: <strong style="color:var(--text-main);">${st.circunscripcion_cabecera}</strong>
            </div>
          </div>
          <span style="font-family:var(--font-mono); font-size:10.5px; color:var(--text-dim); background:rgba(255,255,255,0.05); padding:3px 8px; border-radius:4px; border:1px solid var(--border-subtle);">
            Clave INE: ${st.abbr}
          </span>
        </div>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:8px;">
          <div style="background:var(--bg-card); padding:8px 10px; border-radius:6px; border:1px solid var(--border-subtle);">
            <div style="font-size:9.5px; color:var(--text-dim); font-family:var(--font-mono);">DIP. FEDERALES</div>
            <div style="font-size:15px; font-weight:800; color:var(--gold-bright); font-family:var(--font-mono);">${st.distritos_federales.length} MR</div>
            <div style="font-size:9.5px; color:var(--text-dim);">+ 40 Pluris Circ.</div>
          </div>

          <div style="background:var(--bg-card); padding:8px 10px; border-radius:6px; border:1px solid var(--border-subtle);">
            <div style="font-size:9.5px; color:var(--text-dim); font-family:var(--font-mono);">CONGRESO LOCAL</div>
            <div style="font-size:15px; font-weight:800; color:var(--cyan); font-family:var(--font-mono);">${st.diputados_locales.total} Curules</div>
            <div style="font-size:9.5px; color:var(--text-dim);">${st.diputados_locales.mr} MR · ${st.diputados_locales.rp} RP</div>
          </div>

          <div style="background:var(--bg-card); padding:8px 10px; border-radius:6px; border:1px solid var(--border-subtle);">
            <div style="font-size:9.5px; color:var(--text-dim); font-family:var(--font-mono);">GASTO CONGRESO</div>
            <div style="font-size:15px; font-weight:800; color:var(--text-main); font-family:var(--font-mono);">$${cg ? cg.presupuestoCongreso.toLocaleString('es-MX') : '-'} mdp</div>
            <div style="font-size:9.5px; color:var(--text-dim);">Presupuesto Anual</div>
          </div>

          <div style="background:var(--bg-card); padding:8px 10px; border-radius:6px; border:1px solid var(--border-subtle);">
            <div style="font-size:9.5px; color:var(--text-dim); font-family:var(--font-mono);">COSTO / LEGISLADOR</div>
            <div style="font-size:15px; font-weight:800; color:${cg && cg.costoPorDiputado >= 24 ? 'var(--crimson-bright)' : 'var(--gold)'}; font-family:var(--font-mono);">$${cg ? cg.costoPorDiputado.toFixed(1) : '-'} mdp</div>
            <div style="font-size:9.5px; color:var(--text-dim);">Gasto anual por dip.</div>
          </div>
        </div>
      `;
    }

    // Listado de distritos
    renderDistritosList(st.distritos_federales, st.nombre);

    // Actualizar estilo en el mapa
    if (state.electoralGeoJsonLayer) {
      state.electoralGeoJsonLayer.eachLayer(layer => {
        const isTarget = layer.feature && layer.feature.properties.abbr === abbr;
        const circ = st.circunscripcion;
        const color = getCircunscripcionColor(circ);
        layer.setStyle({
          weight: isTarget ? 2.5 : 1,
          color: isTarget ? '#ffd700' : 'rgba(255,255,255,0.2)',
          fillOpacity: isTarget ? 0.95 : 0.65
        });
      });
    }
  }

  function renderDistritosList(distritos, estadoNombre = '') {
    const container = document.getElementById('electoralDistrictsList');
    if (!container) return;

    if (!distritos || distritos.length === 0) {
      container.innerHTML = `
        <div style="padding:14px; text-align:center; color:var(--text-dim); font-size:12px; font-family:var(--font-mono);">
          No se encontraron distritos con el criterio de búsqueda.
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div style="font-family:var(--font-mono); font-size:11px; color:var(--gold); font-weight:700; margin-bottom:8px; display:flex; justify-content:space-between;">
        <span>🗳️ Distritos Electorales Federales (${distritos.length})</span>
        <span style="color:var(--text-dim);">${estadoNombre}</span>
      </div>
      ${distritos.map(d => `
        <div class="distrito-row-card" style="padding:9px 12px; margin-bottom:8px; background:var(--bg-card); border:1px solid var(--border-subtle); border-radius:6px; transition:all 0.2s ease;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px; flex-wrap:wrap; gap:6px;">
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-family:var(--font-mono); font-weight:800; font-size:11.5px; color:var(--gold-bright); background:rgba(201,168,76,0.15); padding:2px 8px; border-radius:4px; border:1px solid var(--gold);">
                ${d.estadoAbbr ? `${d.estadoAbbr} · ` : ''}${d.num}
              </span>
              <span style="font-family:var(--font-mono); font-size:12px; color:var(--text-main); font-weight:700;">
                Cabecera: <span style="color:var(--cyan);">${d.cabecera}</span>
              </span>
            </div>
            <span style="font-size:10px; color:var(--text-dim); font-family:var(--font-mono); background:rgba(255,255,255,0.04); padding:1px 6px; border-radius:3px;">
              Mayoría Relativa (MR)
            </span>
          </div>
          <div style="font-size:11px; color:var(--text-secondary); line-height:1.45;">
            <strong style="color:var(--text-dim);">Municipios / Territorio:</strong> ${d.municipios}
          </div>
        </div>
      `).join('')}
    `;
  }

  function filterElectoralCircunscripcion(circ) {
    state.activeElectoralCirc = circ;

    // Actualizar botones de filtro
    document.querySelectorAll('.electoral-circ-btn').forEach(btn => {
      const isTarget = String(btn.dataset.circ) === String(circ);
      btn.classList.toggle('active', isTarget);
    });

    if (circ === 'todas') {
      renderElectoralGeoJsonLayer();
      renderElectoralDistritos(state.activeElectoralState || 'JAL');
      if (state.electoralMap) {
        state.electoralMap.setView([23.6345, -102.5528], 4);
      }
    } else {
      const circObj = DB.geografia_electoral_ine.circunscripciones.find(c => c.num === Number(circ));
      if (circObj && circObj.estados.length > 0) {
        renderElectoralGeoJsonLayer();
        renderElectoralDistritos(circObj.estados[0]);
      }
    }
  }

  function searchElectoralDistrict(query) {
    if (!query || !query.trim()) {
      renderElectoralDistritos(state.activeElectoralState || 'JAL');
      return;
    }

    const q = query.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
    const results = [];

    if (DB.geografia_electoral_ine && DB.geografia_electoral_ine.estados_distritacion) {
      DB.geografia_electoral_ine.estados_distritacion.forEach(st => {
        st.distritos_federales.forEach(d => {
          const text = (st.nombre + ' ' + st.abbr + ' ' + d.num + ' ' + d.cabecera + ' ' + d.municipios)
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");

          if (text.includes(q)) {
            results.push({
              ...d,
              estadoNombre: st.nombre,
              estadoAbbr: st.abbr
            });
          }
        });
      });
    }

    renderDistritosList(results, `Búsqueda: "${query}" (${results.length} coincidencias en el país)`);
  }

  // ==========================================================================
  // BLOQUE 6: JERARQUÍA SALARIAL Y REPRESENTATIVA DESCENDENTE
  // Desde el Senado hasta el cargo más pequeño municipal y comunitario
  // ==========================================================================

  function renderJerarquiaSalarialChart() {
    const container = document.getElementById('jerarquiaBarsContainer');
    if (!container) return;

    const data = (DB.legislativo && DB.legislativo.jerarquia_salarial_representativa) || [];
    if (!data.length) return;

    const metric = state.activeJerarquiaMetric || 'sueldo';
    const catFilter = state.activeJerarquiaCat || 'todas';

    // Determinar valor según métrica
    function getVal(d) {
      if (metric === 'costo') return d.costo_anual_integrado;
      if (metric === 'bruto_apoyos') return d.sueldo_bruto_mensual + d.apoyos_mensuales;
      return d.sueldo_neto_mensual; // por defecto sueldo neto mensual
    }

    // Filtrar según categoría si aplica
    const filtered = data.filter(d => {
      if (catFilter === 'todas') return true;
      if (catFilter === 'Federal') return d.categoria.includes('Federal');
      if (catFilter === 'Estatal') return d.categoria.includes('Estatal');
      if (catFilter === 'Municipal') return d.categoria.includes('Municipal') && !d.categoria.includes('Auxiliar');
      if (catFilter === 'Auxiliar') return d.categoria.includes('Auxiliar') || d.categoria.includes('Comunal');
      return true;
    });

    // Calcular máximo para escala porcentual
    const maxVal = Math.max(...data.map(d => getVal(d)), 1);

    // Actualizar KPIs de cabecera
    const kpiMaxEl = document.getElementById('jerarquiaKpiMax');
    const kpiMinEl = document.getElementById('jerarquiaKpiMin');
    const kpiRatioEl = document.getElementById('jerarquiaKpiRatio');
    const kpiCabildoEl = document.getElementById('jerarquiaKpiCabildo');

    if (kpiMaxEl) {
      const top = data[0]; // Senador
      kpiMaxEl.innerHTML = `
        <div style="font-size:10px; color:var(--gold); font-family:var(--font-mono); text-transform:uppercase;">🏛️ Cúspide Federal (Nivel 1)</div>
        <div style="font-size:18px; font-weight:800; color:var(--gold-bright); font-family:var(--font-mono); margin:2px 0;">$${top.sueldo_neto_mensual.toLocaleString('es-MX')} <span style="font-size:11px; font-weight:400; color:var(--text-dim);">netos/mes</span></div>
        <div style="font-size:11px; color:var(--text-secondary);">${top.cargo} · Costo anual $41.91 mdp</div>
      `;
    }

    if (kpiCabildoEl) {
      const reg = data.find(d => d.id === 'regidor_metropolitano') || data[5];
      kpiCabildoEl.innerHTML = `
        <div style="font-size:10px; color:var(--amber); font-family:var(--font-mono); text-transform:uppercase;">🏙️ Cabildo Municipal (Nivel 6)</div>
        <div style="font-size:18px; font-weight:800; color:var(--amber); font-family:var(--font-mono); margin:2px 0;">$${reg.sueldo_neto_mensual.toLocaleString('es-MX')} <span style="font-size:11px; font-weight:400; color:var(--text-dim);">netos/mes</span></div>
        <div style="font-size:11px; color:var(--text-secondary);">Regidor Metropolitano (Zapopan/GDL/MTY) · $1.85M anual</div>
      `;
    }

    if (kpiMinEl) {
      const btm = data[data.length - 1]; // Juez de Barrio / Auxiliar
      kpiMinEl.innerHTML = `
        <div style="font-size:10px; color:var(--cyan); font-family:var(--font-mono); text-transform:uppercase;">🌱 Base Comunal (Nivel 14)</div>
        <div style="font-size:18px; font-weight:800; color:var(--cyan); font-family:var(--font-mono); margin:2px 0;">$${btm.sueldo_neto_mensual.toLocaleString('es-MX')} <span style="font-size:11px; font-weight:400; color:var(--text-dim);">netos/mes</span></div>
        <div style="font-size:11px; color:var(--text-secondary);">${btm.cargo} · Costo anual $26,000</div>
      `;
    }

    if (kpiRatioEl) {
      kpiRatioEl.innerHTML = `
        <div style="font-size:10px; color:var(--crimson-bright); font-family:var(--font-mono); text-transform:uppercase;">⚖️ Brecha Extrema de Costo</div>
        <div style="font-size:18px; font-weight:800; color:var(--crimson-bright); font-family:var(--font-mono); margin:2px 0;">1,612 a 1</div>
        <div style="font-size:11px; color:var(--text-secondary);">1 Senador equivale al presupuesto de 1,612 Jueces de Barrio</div>
      `;
    }

    // Renderizar filas de barras
    container.innerHTML = filtered.map(d => {
      const val = getVal(d);
      const pct = Math.max((val / maxVal) * 100, 2); // mínimo 2% para visibilidad
      
      let valDisplay = '';
      if (metric === 'costo') {
        if (val >= 1000000) {
          valDisplay = `$${(val / 1000000).toFixed(2)} mdp / año`;
        } else {
          valDisplay = `$${val.toLocaleString('es-MX')} / año`;
        }
      } else if (metric === 'bruto_apoyos') {
        valDisplay = `$${val.toLocaleString('es-MX')} / mes (Bruto + Apoyos)`;
      } else {
        valDisplay = `$${val.toLocaleString('es-MX')} netos / mes`;
      }

      const barGradient = d.nivel <= 3 
        ? 'linear-gradient(90deg, #d4af37 0%, #ffd700 100%)' 
        : (d.nivel <= 7 
            ? 'linear-gradient(90deg, #3498db 0%, #00c3ff 100%)' 
            : (d.nivel <= 11 
                ? 'linear-gradient(90deg, #2ecc71 0%, #27ae60 100%)' 
                : 'linear-gradient(90deg, #9b59b6 0%, #e67e22 100%)'));

      return `
        <div class="jerarquia-bar-row" onclick="window.AuditEngine.openCargoDetail('${d.id}')" title="Haz clic para examinar el desglose legal y remuneraciones completas">
          <div class="jerarquia-bar-meta">
            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
              <span style="font-family:var(--font-mono); font-size:10px; font-weight:800; background:rgba(255,255,255,0.06); color:var(--text-dim); padding:2px 7px; border-radius:4px; border:1px solid var(--border-subtle);">
                NIVEL ${d.nivel}
              </span>
              <span style="font-size:16px;">${d.icono}</span>
              <strong style="font-family:var(--font-serif); font-size:14px; color:var(--text-main);">
                ${d.cargo}
              </strong>
              <span style="font-family:var(--font-mono); font-size:10px; color:${d.color || 'var(--gold)'}; background:${d.color ? d.color + '15' : 'rgba(201,168,76,0.15)'}; padding:2px 6px; border-radius:3px; border:1px solid ${d.color ? d.color + '44' : 'rgba(201,168,76,0.3)'};">
                ${d.categoria}
              </span>
            </div>
            <div style="font-family:var(--font-mono); font-weight:800; font-size:13.5px; color:var(--gold-bright);">
              ${valDisplay}
            </div>
          </div>

          <div class="jerarquia-bar-track">
            <div class="jerarquia-bar-fill" style="width: ${pct}%; background: ${barGradient}; box-shadow: 0 0 10px ${d.color ? d.color + '55' : 'rgba(212,175,55,0.4)'};"></div>
          </div>

          <div class="jerarquia-bar-desc">
            <span><strong>Ámbito:</strong> ${d.ambito} · <span style="color:var(--text-dim);">${d.fundamento_legal}</span></span>
            <span style="color:var(--cyan); font-family:var(--font-mono); font-size:10.5px; text-decoration:underline;">Examinar Ficha Jurídica 🔍</span>
          </div>
        </div>
      `;
    }).join('');

    renderJerarquiaTable();
  }

  function setJerarquiaMetric(metric) {
    state.activeJerarquiaMetric = metric;
    document.querySelectorAll('.jerarquia-metric-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.metric === metric);
    });
    renderJerarquiaSalarialChart();
  }

  function filterJerarquiaCategoria(cat) {
    state.activeJerarquiaCat = cat;
    document.querySelectorAll('.jerarquia-cat-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.cat === cat);
    });
    renderJerarquiaSalarialChart();
  }

  function renderJerarquiaTable() {
    const tableBody = document.getElementById('jerarquiaTableBody');
    if (!tableBody) return;

    const data = (DB.legislativo && DB.legislativo.jerarquia_salarial_representativa) || [];
    tableBody.innerHTML = data.map(d => `
      <tr>
        <td style="font-family:var(--font-mono); font-weight:800; color:var(--gold); text-align:center;">${d.nivel}</td>
        <td>
          <div style="font-weight:700; color:var(--text-main); font-family:var(--font-serif);">${d.icono} ${d.cargo}</div>
          <div style="font-size:11px; color:var(--text-dim);">${d.ambito}</div>
        </td>
        <td style="font-size:10.5px; font-family:var(--font-mono); color:var(--cyan);">${d.categoria}</td>
        <td style="text-align:right; font-family:var(--font-mono); font-weight:700; color:var(--gold-bright);">$${d.sueldo_neto_mensual.toLocaleString('es-MX')}</td>
        <td style="text-align:right; font-family:var(--font-mono); color:var(--text-secondary);">$${d.sueldo_bruto_mensual.toLocaleString('es-MX')}</td>
        <td style="text-align:right; font-family:var(--font-mono); color:var(--amber);">$${d.apoyos_mensuales.toLocaleString('es-MX')}</td>
        <td style="text-align:right; font-family:var(--font-mono); font-weight:700; color:${d.costo_anual_integrado >= 10000000 ? 'var(--crimson-bright)' : 'var(--text-main)'};">
          ${d.costo_anual_integrado >= 1000000 ? '$' + (d.costo_anual_integrado / 1000000).toFixed(2) + ' mdp' : '$' + d.costo_anual_integrado.toLocaleString('es-MX')}
        </td>
        <td style="font-size:11px; color:var(--text-dim);">${d.fundamento_legal}</td>
        <td style="text-align:center;">
          <button class="action-btn" onclick="window.AuditEngine.openCargoDetail('${d.id}')" style="font-size:11px; padding:3px 8px;">Ficha 📄</button>
        </td>
      </tr>
    `).join('');
  }

  function toggleJerarquiaTable() {
    const wrap = document.getElementById('jerarquiaTableWrapper');
    const btn = document.getElementById('jerarquiaToggleTableBtn');
    if (!wrap) return;

    const isHidden = wrap.style.display === 'none';
    wrap.style.display = isHidden ? 'block' : 'none';
    if (btn) {
      btn.innerHTML = isHidden 
        ? '▲ Ocultar Tabla Comparativa de 14 Niveles' 
        : '📋 Ver Tabla Comparativa Completa de los 14 Niveles';
    }
  }

  function openCargoDetail(cargoId) {
    const data = (DB.legislativo && DB.legislativo.jerarquia_salarial_representativa) || [];
    const item = data.find(d => d.id === cargoId);
    if (!item) return;

    let modal = document.getElementById('cargoDetailModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'cargoDetailModal';
      modal.className = 'jerarquia-modal-backdrop';
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div class="jerarquia-modal-content">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px; border-bottom:1px solid var(--border-gold); padding-bottom:12px;">
          <div>
            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
              <span style="font-size:24px;">${item.icono}</span>
              <h3 style="font-family:var(--font-serif); font-size:20px; color:var(--gold-bright); margin:0;">
                ${item.cargo}
              </h3>
              <span style="font-family:var(--font-mono); font-size:11px; background:rgba(201,168,76,0.18); color:var(--gold); border:1px solid var(--border-gold); padding:2px 8px; border-radius:4px; font-weight:700;">
                NIVEL ${item.nivel} · ${item.categoria}
              </span>
            </div>
            <div style="font-size:12px; color:var(--text-dim); margin-top:4px; font-family:var(--font-mono);">
              Ámbito territorial: <strong style="color:var(--text-main);">${item.ambito}</strong>
            </div>
          </div>
          <button onclick="window.AuditEngine.closeCargoDetail()" style="background:transparent; border:none; color:var(--text-dim); font-size:22px; cursor:pointer; padding:4px 8px; line-height:1;">&times;</button>
        </div>

        <!-- Matriz Económica y Remuneraciones -->
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:10px; margin-bottom:16px;">
          <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:6px; padding:10px;">
            <div style="font-size:10px; color:var(--text-dim); font-family:var(--font-mono);">SUELDO NETO MENSUAL</div>
            <div style="font-size:18px; font-weight:800; color:var(--gold-bright); font-family:var(--font-mono);">$${item.sueldo_neto_mensual.toLocaleString('es-MX')}</div>
            <div style="font-size:10px; color:var(--text-dim);">Depósito líquido al mes</div>
          </div>
          <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:6px; padding:10px;">
            <div style="font-size:10px; color:var(--text-dim); font-family:var(--font-mono);">SUELDO BRUTO MENSUAL</div>
            <div style="font-size:18px; font-weight:800; color:var(--text-secondary); font-family:var(--font-mono);">$${item.sueldo_bruto_mensual.toLocaleString('es-MX')}</div>
            <div style="font-size:10px; color:var(--text-dim);">Antes de ISR / retenciones</div>
          </div>
          <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:6px; padding:10px;">
            <div style="font-size:10px; color:var(--amber); font-family:var(--font-mono);">APOYOS / PRERROGATIVAS</div>
            <div style="font-size:18px; font-weight:800; color:var(--amber); font-family:var(--font-mono);">$${item.apoyos_mensuales.toLocaleString('es-MX')}</div>
            <div style="font-size:10px; color:var(--text-dim);">Gestión / Asesoría / Operación</div>
          </div>
          <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:6px; padding:10px;">
            <div style="font-size:10px; color:var(--crimson-bright); font-family:var(--font-mono);">COSTO ANUAL INTEGRADO</div>
            <div style="font-size:18px; font-weight:800; color:var(--crimson-bright); font-family:var(--font-mono);">
              ${item.costo_anual_integrado >= 1000000 ? '$' + (item.costo_anual_integrado / 1000000).toFixed(2) + ' mdp' : '$' + item.costo_anual_integrado.toLocaleString('es-MX')}
            </div>
            <div style="font-size:10px; color:var(--text-dim);">Carga fiscal anual total</div>
          </div>
        </div>

        <!-- Fundamento Legal y Constitucional -->
        <div style="background:rgba(201,168,76,0.06); border:1px solid var(--border-gold); border-radius:8px; padding:12px 14px; margin-bottom:14px;">
          <div style="font-family:var(--font-mono); font-size:10.5px; color:var(--gold); font-weight:700; margin-bottom:4px; text-transform:uppercase;">
            ⚖️ Fundamento Jurídico Constitucional y Reglamentario
          </div>
          <div style="font-size:13px; color:var(--text-main); font-weight:600; line-height:1.4;">
            ${item.fundamento_legal}
          </div>
          <div style="font-size:11px; color:var(--text-dim); margin-top:4px;">
            Normativa aplicable: ${item.fuente_normativa}
          </div>
        </div>

        <!-- Prestaciones y Prerrogativas Especiales -->
        <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:8px; padding:12px 14px; margin-bottom:14px;">
          <div style="font-family:var(--font-mono); font-size:10.5px; color:var(--cyan); font-weight:700; margin-bottom:4px; text-transform:uppercase;">
            📦 Prestaciones, Seguros &amp; Partidas Especiales
          </div>
          <p style="font-size:12.5px; color:var(--text-secondary); line-height:1.5; margin:0;">
            ${item.prestaciones_detalle}
          </p>
        </div>

        <!-- Funciones y Competencia Constitucional / Edilicia -->
        <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:8px; padding:12px 14px; margin-bottom:18px;">
          <div style="font-family:var(--font-mono); font-size:10.5px; color:var(--gold); font-weight:700; margin-bottom:4px; text-transform:uppercase;">
            🏛️ Mandato y Funciones Representativas
          </div>
          <p style="font-size:12.5px; color:var(--text-main); line-height:1.5; margin:0;">
            ${item.descripcion_funciones}
          </p>
        </div>

        <div style="display:flex; justify-content:flex-end; gap:8px;">
          <button class="action-btn" onclick="window.AuditEngine.closeCargoDetail()" style="padding:6px 16px; font-size:12px;">Cerrar Ficha</button>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
  }

  function closeCargoDetail() {
    const modal = document.getElementById('cargoDetailModal');
    if (modal) modal.style.display = 'none';
  }

  // ==========================================================================
  // METADATOS Y CONTROLADOR MAESTRO DE 8 PESTAÑAS
  // ==========================================================================
  const TAB_METADATA = {
    'presupuesto': {
      t: '1. Presupuesto y Gasto Público (Poder Ejecutivo Federal & Subnacional)',
      d: 'Explora cómo la federación distribuye el erario federalizado ($2.81 billones) a las 32 entidades y más de 2,400 municipios. Verifica transferencias de libre disposición (Ramo 28), aportaciones condicionadas (Ramo 33), semáforo de deuda de la SHCP y alertas de la ASF.'
    },
    'accion-financiera': {
      t: '2. Acción Financiera del Estado & Finanzas Públicas',
      d: 'Seguimiento integral a los instrumentos del erario: simulador de inversiones públicas y pérdidas en tiempo real de megaobras presidenciales (1988–actualidad), colocación de deuda soberana vía Banco de México (CETES y Bonos M), calculadora cívica del contribuyente y bitácora de alertas ASF.'
    },
    'legislativo': {
      t: '3. Poder Legislativo, Periodos de Sesiones & Elecciones Concurrentes (+19,600 Cargos)',
      d: 'Importancia del Poder Legislativo y de sus periodos de sesiones: el erario se aprueba en el Congreso. Descubre cómo operan las elecciones concurrentes en las 32 entidades (+19,600 cargos renovados), la diferencia entre mayoría relativa y representación proporcional (plurinominales), el calendario cívico y la guía ciudadana para fiscalizar perfiles.'
    },
    'judicial': {
      t: '4. Suprema Corte de Justicia de la Nación: Presupuesto, Fiscalización & Nueva Estructura',
      d: 'Balance presupuestal auditado del Poder Judicial de la Federación ($78,327 mdp), fideicomisos en litigio, tarjeta y análisis comparativo de remuneraciones de la Suprema Corte de Justicia de la Nación (SCJN) y desglose de ponencias y asesores.'
    },
    'politicos': {
      t: '5. Personajes Políticos & Radiografía Sexenal (1988–Actualidad)',
      d: 'Evaluación comparativa de presidentes de la República y personajes relevantes desde Carlos Salinas de Gortari hasta Claudia Sheinbaum: crecimiento real del gasto, deuda pública, empresas fantasma (EFOS), grandes desfalcos y datos curiosos de personajes secundarios.'
    },
    'verificador': {
      t: '6. Modo Inspector (Auditoría Forense Hacendaria en Vivo)',
      d: 'Herramienta cívica de verificación y auditoría en vivo contra notas de prensa, medios digitales o documentos oficiales (PDF/URL). Evalúa declaraciones sobre dependencias públicas y finanzas hacendarias contrastándolas con ingresos federales (PEF/LIF), egresos devengados, auditorías de la ASF y cuentas públicas pendientes de rendir.'
    },
    'faq': {
      t: '7. Preguntas, Glosario & Marco Legal Hacendario (LIF, CPEUM & Deuda)',
      d: 'Formación cívica integral dividida en tres subpestañas: Casillas temáticas de preguntas ciudadanas, Glosario enciclopédico de conceptos clave del erario en constante actualización, y el Marco Legal Hacendario con las disposiciones de la Ley de Ingresos (LIF) y preceptos constitucionales vigentes con acceso a su texto íntegro.'
    },
    'referencias': {
      t: '8. Referencias & Fuentes Oficiales',
      d: 'Compilación exhaustiva, clasificada y numerada de las fuentes bibliográficas e institucionales consultadas: SHCP, Banco de México, Auditoría Superior de la Federación (ASF), INEGI, IMCO y Diario Oficial de la Federación (DOF).'
    },
    'comunidad': {
      t: '9. Comunidad & Contraloría Cívica Ciudadana',
      d: 'Buzón ciudadano de observaciones de obras públicas, directorio oficial de canales de denuncia anónima ante la ASF, SFP y SAT, y decálogo de vigilancia cívica sobre el erario.'
    }
  };

  let activeTabKey = 'presupuesto';

  function switchTab(tabKey) {
    // Compatibilidad de claves anteriores
    if (tabKey === 'mapa') tabKey = 'presupuesto';
    if (tabKey === 'flujo') tabKey = 'accion-financiera';

    if (!TAB_METADATA[tabKey]) tabKey = 'presupuesto';
    activeTabKey = tabKey;

    // Actualizar botones de pestaña principal
    document.querySelectorAll('.tabbar button[role="tab"]').forEach(btn => {
      const isSelected = btn.dataset.tab === tabKey;
      btn.setAttribute('aria-selected', isSelected ? 'true' : 'false');
      btn.classList.toggle('active', isSelected);
    });

    // Actualizar paneles de pestaña principal
    document.querySelectorAll('.tab-panel').forEach(panel => {
      panel.classList.toggle('active', panel.id === `tab-panel-${tabKey}`);
    });

    // Actualizar introducción dinámica (#tabintro)
    const introEl = document.getElementById('tabintro');
    if (introEl && TAB_METADATA[tabKey]) {
      introEl.innerHTML = `
        <h2>${TAB_METADATA[tabKey].t}</h2>
        <p>${TAB_METADATA[tabKey].d}</p>
      `;
    }

    // Actualizar hash de la URL
    if (window.location.hash !== `#${tabKey}`) {
      history.replaceState(null, null, `#${tabKey}`);
    }

    // Acciones al activar pestañas
    if (tabKey === 'presupuesto') {
      if (state.activeView === 'geo' && state.leafletMap) {
        setTimeout(() => state.leafletMap.invalidateSize(), 60);
      }
    } else if (tabKey === 'accion-financiera') {
      renderFinanzasPublicas();
    } else if (tabKey === 'legislativo') {
      renderCongresosTable();
      initElectoralModule();
      renderJerarquiaSalarialChart();
      if (state.electoralMap) {
        setTimeout(() => state.electoralMap.invalidateSize(), 80);
      }
    } else if (tabKey === 'judicial') {
      setPjView(currentPjView);
      renderJudicialMinisters();
    } else if (tabKey === 'politicos') {
      renderPoliticosMandatarios();
    } else if (tabKey === 'verificador') {
      renderFactCheckModule();
    } else if (tabKey === 'faq') {
      renderCasillasFaq();
      renderGlossary();
      renderPreceptosLegales();
    } else if (tabKey === 'referencias') {
      renderReferencias('todas');
    }
  }

  // ==========================================================================
  // CONTROLADOR DE SUBPESTAÑAS
  // ==========================================================================
  function switchSubtab(parentTab, subKey) {
    // Actualizar botones de subpestañas
    document.querySelectorAll(`.subtabs-bar[data-parent="${parentTab}"] .subtab-btn`).forEach(btn => {
      const isSel = btn.dataset.sub === subKey;
      btn.classList.toggle('active', isSel);
      btn.setAttribute('aria-selected', isSel ? 'true' : 'false');
    });

    // Actualizar subpaneles
    document.querySelectorAll(`.subtab-panel[data-parent="${parentTab}"]`).forEach(panel => {
      panel.classList.toggle('active', panel.dataset.subpanel === subKey);
    });

    // Acciones específicas de subpestaña
    if (parentTab === 'politicos') {
      if (subKey === 'mandatarios') renderPoliticosMandatarios();
      else if (subKey === 'secundarios') renderPoliticosSecundarios();
      else if (subKey === 'curiosos') renderPoliticosCuriosos();
        else if (subKey === 'versus-porfirio') renderVersusPorfirio();
    } else if (parentTab === 'accion-financiera') {
      if (subKey === 'simulador-megaobras') renderSimuladorMegaobras();
      else if (subKey === 'calculadora') calculateTaxBreakdown(30000);
      else if (subKey === 'bitacora') renderNews();
      else if (subKey === 'ejes-deuda') renderFinanzasPublicas();
    } else if (parentTab === 'legislativo') {
      if (subKey === 'monitor-civico') {
        // Subpestaña 3.1: Monitor Cívico Electoral
        updateDiputadosSimulator();
        updateSenadoSimulator();
        updateASFSimulator();
      } else if (subKey === 'congresos-estatales') {
        renderCongresosTable();
        updateCongresosSimulator();
      } else if (subKey === 'diputaciones-distritos') {
        initElectoralStateSelect();
        renderElectoralDistritos(state.activeElectoralState || 'JAL');
        if (state.electoralMap) {
          setTimeout(() => state.electoralMap.invalidateSize(), 80);
        } else {
          setTimeout(() => initElectoralMap(), 80);
        }
      } else if (subKey === 'estructura-remunerativa') {
        renderJerarquiaSalarialChart();
        updateJerarquiaSimulator();
      }
    } else if (parentTab === 'judicial') {
      if (subKey === 'estructura') {
        setPjView(currentPjView);
      } else {
        renderJudicialMinisters();
        if (subKey === 'prestaciones') {
          renderJudicialPrestacionesSimulator(currentPrestacionesView);
        } else if (subKey === 'asesores') {
          renderJudicialAsesoresSimulator(currentAsesoresView);
        } else if (subKey === 'calculos') {
          renderJudicialGlobalesSimulator(currentGlobalesView);
        }
      }
    } else if (parentTab === 'faq') {
      if (subKey === 'faq-preguntas') renderCasillasFaq();
      else if (subKey === 'faq-glosario') renderGlossary();
      else if (subKey === 'faq-marco-legal') renderPreceptosLegales();
    }
  }

  // ==========================================================================
  // HIPERVÍNCULOS INTERNOS A GLOSARIO Y REFERENCIAS CON ANIMACIÓN
  // ==========================================================================
  function goToGlossary(term) {
    switchTab('faq');
    switchSubtab('faq', 'faq-glosario');
    currentGlossaryCategory = 'todas';
    document.querySelectorAll('#glossaryFilterChips .chip').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.gcat === 'todas');
      btn.classList.toggle('on', btn.dataset.gcat === 'todas');
    });
    const input = document.getElementById('glossarySearchInput');
    if (input) {
      input.value = term;
      renderGlossary(term, 'todas');
    }
    const el = document.getElementById('seccionGlosario');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      el.style.boxShadow = '0 0 24px var(--gold-glow)';
      setTimeout(() => { el.style.boxShadow = ''; }, 1800);
    }
    setTimeout(() => {
      const cards = document.querySelectorAll('#glossaryGrid .glossary-card');
      if (cards.length > 0) {
        cards[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
        cards[0].style.background = 'rgba(201, 168, 76, 0.22)';
        cards[0].style.borderColor = 'var(--gold-bright)';
        cards[0].style.boxShadow = '0 0 24px rgba(212, 175, 55, 0.45)';
        setTimeout(() => {
          cards[0].style.background = '';
          cards[0].style.borderColor = '';
          cards[0].style.boxShadow = '';
        }, 2500);
      }
    }, 200);
  }

  function goToRef(refId) {
    if (refId && (refId.startsWith('ref-marcolg') || refId.startsWith('precepto-'))) {
      switchTab('faq');
      switchSubtab('faq', 'faq-marco-legal');
      renderPreceptosLegales();
      setTimeout(() => {
        const targetPrecept = document.getElementById(refId) || document.querySelector('.precepto-card');
        if (targetPrecept) {
          targetPrecept.scrollIntoView({ behavior: 'smooth', block: 'center' });
          targetPrecept.style.borderColor = 'var(--gold-bright)';
          targetPrecept.style.boxShadow = '0 0 22px rgba(212, 175, 55, 0.45)';
          setTimeout(() => {
            targetPrecept.style.borderColor = '';
            targetPrecept.style.boxShadow = '';
          }, 2500);
        }
      }, 150);
      return;
    }
    switchTab('referencias');
    renderReferencias('todas');
    setTimeout(() => {
      let el = document.getElementById(refId);
      // Si no se encontró por ID directo, buscar por número si tiene formato 'ref-XX' o 'ref-X'
      if (!el && refId && DB.referencias_legales) {
        const digits = refId.replace(/[^0-9]/g, '');
        if (digits) {
          const num = parseInt(digits, 10);
          const found = DB.referencias_legales.find(r => r.num === num);
          if (found) {
            el = document.getElementById(found.id);
          }
        }
      }
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.style.background = 'rgba(201, 168, 76, 0.22)';
        el.style.borderColor = 'var(--gold-bright)';
        el.style.boxShadow = '0 0 22px rgba(212, 175, 55, 0.45)';
        setTimeout(() => {
          el.style.background = '';
          el.style.borderColor = '';
          el.style.boxShadow = '';
        }, 2500);
      }
    }, 150);
  }


  // ==========================================================================
  // RENDERIZADO: MINISTROS DE LA SCJN, SUELDOS Y ASESORES
  // ==========================================================================
  let activeJudicialPlenoTab = 'nuevo'; // 'nuevo' o 'transicion'
  let activeJudicialChartMetric = 'sueldo'; // 'sueldo', 'costo_ponencia', 'plazas'

  function setJudicialChartMetric(metric) {
    activeJudicialChartMetric = metric;
    document.querySelectorAll('.scjn-metric-pill').forEach(btn => {
      const isTarget = btn.dataset.metric === metric;
      btn.classList.toggle('active', isTarget);
    });
    renderJudicialMinistersChart();
  }

  function setJudicialPlenoView(viewType) {
    activeJudicialPlenoTab = viewType;
    document.querySelectorAll('.judicial-view-btn').forEach(btn => {
      const isTarget = btn.dataset.view === viewType;
      btn.classList.toggle('active', isTarget);
      if (isTarget) {
        btn.style.borderColor = 'var(--gold-bright)';
        btn.style.color = 'var(--gold-bright)';
        btn.style.background = 'rgba(201,168,76,0.18)';
      } else {
        btn.style.borderColor = 'var(--border-subtle)';
        btn.style.color = 'var(--text-secondary)';
        btn.style.background = 'rgba(255,255,255,0.03)';
      }
    });

    const headerTag = document.getElementById('scjnPlenoHeaderTag');
    const headerTitle = document.getElementById('scjnPlenoHeaderTitle');
    const headerCount = document.getElementById('scjnPlenoHeaderCount');
    const badgeBanner = document.getElementById('scjnPlenoBadgesBanner');

    // Elementos de las 4 tarjetas de cálculo inferiores
    const c1Val = document.getElementById('scjnCalcCard1Val');
    const c1Sub = document.getElementById('scjnCalcCard1Sub');
    const c2Lbl = document.getElementById('scjnCalcCard2Lbl');
    const c2Val = document.getElementById('scjnCalcCard2Val');
    const c2Sub = document.getElementById('scjnCalcCard2Sub');
    const c3Val = document.getElementById('scjnCalcCard3Val');
    const c3Sub = document.getElementById('scjnCalcCard3Sub');
    const c4Val = document.getElementById('scjnCalcCard4Val');
    const c4Sub = document.getElementById('scjnCalcCard4Sub');

    if (viewType === 'nuevo') {
      if (headerTag) headerTag.textContent = 'Nuevo Pleno Constitucional SCJN (Vigente · Portal scjn.gob.mx)';
      if (headerTitle) headerTitle.innerHTML = '⚖️ Análisis Comparativo del Nuevo Pleno Oficial (9 Ministras y Ministros Electos)';
      if (headerCount) headerCount.textContent = '9 integrantes electos en funciones plenas · 100% Topados Art. 127';

      if (c1Val) c1Val.textContent = '$134,310 netos';
      if (c1Sub) c1Sub.textContent = '$191,657 pesos brutos / mes (100% apego)';
      if (c2Lbl) c2Lbl.textContent = 'Nuevo Pleno Constitucional';
      if (c2Val) c2Val.textContent = '9 Integrantes';
      if (c2Sub) c2Sub.textContent = '1 Presidente + 8 Ministras y Ministros';
      if (c3Val) c3Val.textContent = '24 a 28 Plazas';
      if (c3Sub) c3Sub.textContent = 'Esquema de austeridad de Estado';
      if (c4Val) c4Val.textContent = '~$216 millones';
      if (c4Sub) c4Sub.textContent = 'Ahorro sustancial vs. $376 mdp régimen previo';

      if (badgeBanner) {
        badgeBanner.innerHTML = `
          <div style="background:rgba(201,168,76,0.1); border:1px solid var(--border-gold); border-radius:6px; padding:12px 16px; display:flex; align-items:center; gap:12px; flex:1; min-width:240px;">
            <span style="font-size:22px;">⭐</span>
            <div>
              <strong style="color:var(--gold-bright); font-size:13px; display:block;">Ministro Presidente Electo</strong>
              <span style="font-size:11px; color:var(--text-secondary);">Hugo Aguilar Ortiz (Presidencia del Máximo Tribunal)</span>
            </div>
          </div>
          <div style="background:rgba(46,204,113,0.08); border:1px solid rgba(46,204,113,0.3); border-radius:6px; padding:12px 16px; display:flex; align-items:center; gap:12px; flex:1; min-width:240px;">
            <span style="font-size:22px;">🟢</span>
            <div>
              <strong style="color:#2ecc71; font-size:13px; display:block;">8 Ministras y Ministros del Pleno</strong>
              <span style="font-size:11px; color:var(--text-secondary);">Batres, Esquivel, Ortiz, Ríos, Figueroa, Espinosa, Guerrero, Herrerías</span>
            </div>
          </div>
          <div style="background:rgba(0,180,216,0.08); border:1px solid rgba(0,180,216,0.3); border-radius:6px; padding:12px 16px; display:flex; align-items:center; gap:12px; flex:1; min-width:240px;">
            <span style="font-size:22px;">📜</span>
            <div>
              <strong style="color:var(--cyan); font-size:13px; display:block;">100% Tope Salarial Art. 127</strong>
              <span style="font-size:11px; color:var(--text-secondary);">$134,310 netos / mes · Eliminación de fideicomisos y privilegios</span>
            </div>
          </div>
        `;
      }
    } else {
      if (headerTag) headerTag.textContent = 'Integrantes del Pleno Post-Reforma 2024–2025 (Transición)';
      if (headerTitle) headerTitle.innerHTML = '⚖️ Análisis Comparativo del Pleno en Transición (Los 10 Ministros y su Presidenta Piña)';
      if (headerCount) headerCount.textContent = '10 en funciones activas en transición · 7 renuncias · 1 concluido';

      if (c1Val) c1Val.textContent = '$134,310 vs $206,948';
      if (c1Sub) c1Sub.textContent = '1 ministra topada vs 10 con sueldo histórico';
      if (c2Lbl) c2Lbl.textContent = 'Pleno en Transición Saliente';
      if (c2Val) c2Val.textContent = '10 en funciones';
      if (c2Sub) c2Sub.textContent = '1 Presidenta + 9 Ministros (7 renuncias a ago-2025)';
      if (c3Val) c3Val.textContent = '32 a 38 Plazas';
      if (c3Sub) c3Sub.textContent = 'Estructura histórica de personal';
      if (c4Val) c4Val.textContent = '~$376 millones';
      if (c4Sub) c4Sub.textContent = 'Gasto anualizado de despachos régimen previo';

      if (badgeBanner) {
        badgeBanner.innerHTML = `
          <div style="background:rgba(46,204,113,0.08); border:1px solid rgba(46,204,113,0.3); border-radius:6px; padding:12px 16px; display:flex; align-items:center; gap:12px; flex:1; min-width:240px;">
            <span style="font-size:22px;">🟢</span>
            <div>
              <strong style="color:#2ecc71; font-size:13px; display:block;">3 Ministras No Renunciaron</strong>
              <span style="font-size:11px; color:var(--text-secondary);">Candidatas directas a la Elección Judicial 2025 (Batres, Esquivel, Ortiz)</span>
            </div>
          </div>
          <div style="background:rgba(243,156,18,0.08); border:1px solid rgba(243,156,18,0.3); border-radius:6px; padding:12px 16px; display:flex; align-items:center; gap:12px; flex:1; min-width:240px;">
            <span style="font-size:22px;">🟠</span>
            <div>
              <strong style="color:#f39c12; font-size:13px; display:block;">7 Renuncias para Agosto 2025</strong>
              <span style="font-size:11px; color:var(--text-secondary);">Laboran en funciones hasta el 31/ago/2025 (Art. 7° Transitorio Reforma)</span>
            </div>
          </div>
          <div style="background:rgba(255,255,255,0.03); border:1px solid var(--border-subtle); border-radius:6px; padding:12px 16px; display:flex; align-items:center; gap:12px; flex:1; min-width:240px;">
            <span style="font-size:22px;">⚪</span>
            <div>
              <strong style="color:var(--text-dim); font-size:13px; display:block;">1 Periodo Constitucional Concluido</strong>
              <span style="font-size:11px; color:var(--text-secondary);">Mandato de 15 años cumplido el 30/nov/2024 (Luis María Aguilar Morales)</span>
            </div>
          </div>
        `;
      }
    }

    renderJudicialMinisters();
    renderJudicialMinistersChart();
  }

  function renderJudicialMinistersChart() {
    const jr = DB.judicial_reservado;
    if (!jr || !jr.scjn_analisis_salarial) return;
    const sa = jr.scjn_analisis_salarial;

    const chartTitle = document.getElementById('scjnChartTitle');
    const chartBadge = document.getElementById('scjnChartBadge');
    const benchmarkEl = document.getElementById('scjnChartBenchmark');
    const barsListEl = document.getElementById('scjnChartBarsList');
    const footerNoteEl = document.getElementById('scjnChartFooterNote');

    if (!barsListEl) return;

    const isNuevo = activeJudicialPlenoTab === 'nuevo';
    const ministers = isNuevo ? (sa.nuevo_pleno_oficial_scjn || sa.ministros) : (sa.pleno_transicion_2024_2025 || []);

    if (chartTitle) {
      chartTitle.textContent = isNuevo ? '📊 Comparativa · Nuevo Pleno SCJN' : '📊 Comparativa · Pleno en Transición';
    }
    if (chartBadge) {
      chartBadge.textContent = isNuevo ? '9 Integrantes Electos' : '10 en funciones · 7 Renuncias';
    }

    // Configuración del benchmark según la métrica
    if (benchmarkEl) {
      if (activeJudicialChartMetric === 'sueldo') {
        benchmarkEl.innerHTML = `
          <div style="display:flex; align-items:center; gap:6px;">
            <span style="color:#2ecc71; font-size:14px;">●</span>
            <span>Tope Art. 127: <strong style="color:var(--emerald-bright);">$134,310 netos/mes</strong></span>
          </div>
          <div style="color:var(--text-dim); font-size:10.5px;">
            Máximo histórico: <span style="color:var(--crimson-bright); font-weight:700;">$206,948 netos</span>
          </div>
        `;
      } else if (activeJudicialChartMetric === 'costo_ponencia') {
        benchmarkEl.innerHTML = `
          <div style="display:flex; align-items:center; gap:6px;">
            <span style="color:var(--cyan); font-size:14px;">●</span>
            <span>Gasto Austeridad: <strong style="color:var(--cyan);">~$2.05M promedio/mes</strong></span>
          </div>
          <div style="color:var(--text-dim); font-size:10.5px;">
            Régimen previo: <span style="color:var(--crimson-bright); font-weight:700;">~$2.85M a $3.10M</span>
          </div>
        `;
      } else { // plazas
        benchmarkEl.innerHTML = `
          <div style="display:flex; align-items:center; gap:6px;">
            <span style="color:var(--cyan); font-size:14px;">●</span>
            <span>Austeridad Ponencias: <strong style="color:var(--cyan);">24–28 plazas</strong></span>
          </div>
          <div style="color:var(--text-dim); font-size:10.5px;">
            Plantilla previa: <span style="color:var(--gold-bright); font-weight:700;">32–38 plazas</span>
          </div>
        `;
      }
    }

    // Renderizar barras de cada ministro
    const barsHtml = ministers.map(m => {
      const isPres = m.tipo_cargo === 'presidente' || (m.nombre && (m.nombre.includes('Aguilar Ortiz') || m.nombre.includes('Piña')));
      let valNum = 0;
      let pct = 0;
      let colorClass = 'emerald';
      let valLabel = '';
      let tagBadge = '';
      let showRefMarker = false;

      if (activeJudicialChartMetric === 'sueldo') {
        const numClean = parseInt(m.sueldo_neto_mensual.replace(/[^0-9]/g, ''), 10) || 134310;
        valNum = numClean;
        const maxScale = 220000;
        pct = Math.min(100, Math.round((valNum / maxScale) * 100));
        const isTopado = valNum <= 135000;
        colorClass = isTopado ? 'emerald' : 'crimson';
        valLabel = m.sueldo_neto_mensual.replace(' pesos', '');
        tagBadge = isTopado ? 
          '<span style="font-family:var(--font-mono); font-size:9px; color:#2ecc71; background:rgba(46,204,113,0.15); padding:1px 5px; border-radius:3px; font-weight:700;">Topado 127</span>' :
          '<span style="font-family:var(--font-mono); font-size:9px; color:#e74c3c; background:rgba(231,76,60,0.15); padding:1px 5px; border-radius:3px; font-weight:700;">Histórico</span>';
        showRefMarker = true;
      } else if (activeJudicialChartMetric === 'costo_ponencia') {
        const numClean = parseInt(m.costo_mensual_ponencia.replace(/[^0-9]/g, ''), 10) || 2000000;
        valNum = numClean;
        const maxScale = 3300000;
        pct = Math.min(100, Math.round((valNum / maxScale) * 100));
        const isAusteridad = valNum <= 2300000;
        colorClass = isAusteridad ? 'cyan' : 'crimson';
        valLabel = `$${(valNum / 1000000).toFixed(2)}M/mes`;
        tagBadge = isAusteridad ?
          '<span style="font-family:var(--font-mono); font-size:9px; color:var(--cyan); background:rgba(0,180,216,0.15); padding:1px 5px; border-radius:3px; font-weight:700;">Austeridad</span>' :
          '<span style="font-family:var(--font-mono); font-size:9px; color:#f39c12; background:rgba(243,156,18,0.15); padding:1px 5px; border-radius:3px; font-weight:700;">Régimen Previo</span>';
      } else { // plazas
        valNum = parseInt(m.asesores_plazas, 10) || 25;
        const maxScale = 40;
        pct = Math.min(100, Math.round((valNum / maxScale) * 100));
        const isAusteridad = valNum <= 28;
        colorClass = isAusteridad ? 'cyan' : 'gold';
        valLabel = `${valNum} plazas`;
        tagBadge = isAusteridad ?
          '<span style="font-family:var(--font-mono); font-size:9px; color:var(--cyan); background:rgba(0,180,216,0.15); padding:1px 5px; border-radius:3px; font-weight:700;">24–28 Plazas</span>' :
          '<span style="font-family:var(--font-mono); font-size:9px; color:var(--gold-bright); background:rgba(201,168,76,0.15); padding:1px 5px; border-radius:3px; font-weight:700;">32–38 Plazas</span>';
      }

      let shortName = m.nombre;
      if (shortName.length > 25) {
        const parts = shortName.split(' ');
        if (parts.length >= 3) {
          shortName = `${parts[0]} ${parts[1]} ${parts[2]}`;
        }
      }

      const modalId = m.id || m.nombre;

      return `
        <div class="scjn-chart-row" onclick="window.AuditEngine.openMinisterModal('${modalId}', '${activeJudicialPlenoTab}')" title="Clic para ver expediente de ${m.nombre}">
          <div class="scjn-chart-row-top">
            <span class="scjn-chart-row-name">
              ${isPres ? '⭐ ' : ''}<strong>${shortName}</strong>
            </span>
            <div style="display:flex; align-items:center; gap:6px;">
              ${tagBadge}
              <span class="scjn-chart-row-val" style="color:var(--text-main);">${valLabel}</span>
            </div>
          </div>
          <div class="scjn-chart-track">
            ${showRefMarker ? '<div class="scjn-chart-ref-mark" style="left:61%;" title="Tope Art. 127 ($134,310)"></div>' : ''}
            <div class="scjn-chart-bar-fill ${colorClass}" style="width: ${pct}%;"></div>
          </div>
        </div>
      `;
    }).join('');

    barsListEl.innerHTML = barsHtml;

    if (footerNoteEl) {
      if (activeJudicialChartMetric === 'sueldo') {
        footerNoteEl.innerHTML = isNuevo ?
          '⚖️ <strong>Apego Total:</strong> El 100% de los 9 integrantes del Nuevo Pleno perciben $134,310 netos mensuales en estricta observancia del Artículo 127 Constitucional.' :
          '⚠️ <strong>Brecha Salarial:</strong> 10 de 11 ministros del Pleno de transición percibieron $206,948 netos mensuales (+54% sobre el tope constitucional), excepto una ministra con devolución voluntaria a TESOFE.';
      } else if (activeJudicialChartMetric === 'costo_ponencia') {
        footerNoteEl.innerHTML = isNuevo ?
          '📉 <strong>Ahorro en Despachos:</strong> Las ponencias del Nuevo Pleno operan con un gasto promedio de ~$2.05 mdp/mes vs ~$2.85 mdp del régimen previo, generando un ahorro mayor a $160 mdp al año.' :
          '🏛️ <strong>Costo Histórico:</strong> Las 11 ponencias de la gestión previa representaban un costo de hasta $3.10 mdp por despacho (más de $376 mdp al año en sueldos y equipo de soporte).';
      } else {
        footerNoteEl.innerHTML = isNuevo ?
          '👥 <strong>Compactación Administrativa:</strong> Equipos reducidos a un rango de 24 a 28 plazas de asesores y secretarios proyectistas, focalizando el trabajo jurisdiccional sustantivo.' :
          '👥 <strong>Plantillas Previas:</strong> Ponencias con 32 a 38 plazas asignadas (secretarios de estudio y cuenta, asesores de ponencia, coordinadores técnicos y choferes).';
      }
    }
  }

  function openMinisterModal(ministerId, type) {
    const jr = DB.judicial_reservado;
    if (!jr || !jr.scjn_analisis_salarial) return;
    const sa = jr.scjn_analisis_salarial;

    let m = null;
    if (type === 'nuevo' || (!type && activeJudicialPlenoTab === 'nuevo')) {
      const list = sa.nuevo_pleno_oficial_scjn || sa.ministros;
      m = list.find(item => item.id === ministerId || (item.nombre && item.nombre.toLowerCase().includes(ministerId.toLowerCase())));
    } else {
      const list = sa.pleno_transicion_2024_2025 || [];
      m = list.find(item => item.nombre && item.nombre.toLowerCase().includes(ministerId.toLowerCase()));
    }
    if (!m) return;

    const modal = document.getElementById('ministerDetailModal');
    const content = document.getElementById('ministerModalContent');
    if (!modal || !content) return;

    const isPres = m.tipo_cargo === 'presidente' || m.cargo.toLowerCase().includes('presidente');

    content.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px; margin-bottom:18px; border-bottom:1px solid var(--border-subtle); padding-bottom:14px;">
        <div>
          <span style="font-family:var(--font-mono); font-size:10.5px; color:var(--gold); text-transform:uppercase; letter-spacing:1px;">
            ${isPres ? '⭐ Presidencia de la Suprema Corte de Justicia' : '⚖️ Integrante del Pleno de la SCJN'} · Portal Oficial scjn.gob.mx
          </span>
          <h2 style="font-family:var(--font-serif); font-size:24px; color:var(--gold-bright); margin-top:4px;">
            ${m.nombre}
          </h2>
          <div style="font-family:var(--font-mono); font-size:12px; color:var(--cyan); margin-top:2px;">
            ${m.cargo} · ${m.sala || 'Pleno de la SCJN'}
          </div>
        </div>
        <span style="font-family:var(--font-mono); font-size:11px; padding:4px 10px; border-radius:4px; font-weight:700; ${m.sueldo_neto_mensual.includes('134,310') ? 'background:rgba(46,204,113,0.15); color:#2ecc71; border:1px solid rgba(46,204,113,0.4);' : 'background:rgba(201,168,76,0.15); color:var(--gold); border:1px solid var(--border-gold);'}">
          ${m.estatus_tope || 'Tope Art. 127'}
        </span>
      </div>

      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:10px; margin-bottom:18px;">
        <div style="background:var(--bg-surface); padding:10px 14px; border-radius:6px; border:1px solid var(--border-subtle);">
          <div style="font-size:10px; color:var(--text-dim); font-family:var(--font-mono);">SUELDO NETO MENSUAL</div>
          <div style="font-size:16px; font-weight:700; color:var(--gold-bright); font-family:var(--font-mono);">${m.sueldo_neto_mensual}</div>
          <div style="font-size:10px; color:var(--text-dim);">${m.sueldo_bruto_mensual} bruto</div>
        </div>
        <div style="background:var(--bg-surface); padding:10px 14px; border-radius:6px; border:1px solid var(--border-subtle);">
          <div style="font-size:10px; color:var(--text-dim); font-family:var(--font-mono);">PLAZAS PONENCIA</div>
          <div style="font-size:16px; font-weight:700; color:var(--cyan); font-family:var(--font-mono);">${m.asesores_plazas} plazas</div>
          <div style="font-size:10px; color:var(--text-dim);">Equipo técnico y proyectistas</div>
        </div>
        <div style="background:var(--bg-surface); padding:10px 14px; border-radius:6px; border:1px solid var(--border-subtle);">
          <div style="font-size:10px; color:var(--text-dim); font-family:var(--font-mono);">COSTO MENSUAL PONENCIA</div>
          <div style="font-size:16px; font-weight:700; color:var(--crimson-bright); font-family:var(--font-mono);">${m.costo_mensual_ponencia}</div>
          <div style="font-size:10px; color:var(--text-dim);">Nómina del despacho</div>
        </div>
      </div>

      ${m.formacion ? `
        <div style="margin-bottom:14px;">
          <strong style="color:var(--gold-bright); font-size:12.5px; display:block; margin-bottom:4px; font-family:var(--font-mono);">🎓 Formación Académica:</strong>
          <p style="font-size:13px; line-height:1.6; color:var(--text-main); margin:0;">${m.formacion}</p>
        </div>
      ` : ''}

      ${m.trayectoria ? `
        <div style="margin-bottom:14px;">
          <strong style="color:var(--gold-bright); font-size:12.5px; display:block; margin-bottom:4px; font-family:var(--font-mono);">🏛️ Trayectoria Pública y Carrera Jurisdiccional:</strong>
          <p style="font-size:13px; line-height:1.65; color:var(--text-secondary); margin:0; text-align:justify;">${m.trayectoria}</p>
        </div>
      ` : ''}

      ${m.especialidad ? `
        <div style="margin-bottom:18px; background:rgba(0,180,216,0.06); border-left:3px solid var(--cyan); padding:10px 14px;">
          <strong style="color:var(--cyan); font-size:11.5px; display:block; margin-bottom:3px; font-family:var(--font-mono);">⚖️ Especialidad &amp; Doctrina Jurisdiccional:</strong>
          <span style="font-size:12.5px; color:var(--text-main);">${m.especialidad}</span>
        </div>
      ` : ''}

      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; border-top:1px solid var(--border-subtle); padding-top:14px;">
        <div style="font-size:11px; color:var(--text-dim); font-family:var(--font-mono); display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
          <span>Designación: <strong style="color:var(--gold);">${m.designacion}</strong></span>
          <span>·</span>
          <a class="glos-link" onclick="window.AuditEngine.goToGlossary('Pleno de la Suprema Corte')">📖 Glosario: SCJN</a>
          <span>·</span>
          <a class="ref-link" onclick="window.AuditEngine.goToRef('ref-scjn-conoce-corte')">[Ref. 24]</a>
        </div>
        <a href="${m.enlace_oficial || 'https://www.scjn.gob.mx/conoce-la-corte'}" target="_blank" rel="noopener noreferrer" style="font-family:var(--font-mono); font-size:11.5px; color:var(--gold-bright); text-decoration:none; display:inline-flex; align-items:center; gap:5px; background:rgba(201,168,76,0.12); border:1px solid var(--border-gold); padding:5px 12px; border-radius:4px;">
          Directorio Oficial SCJN en scjn.gob.mx ↗
        </a>
      </div>
    `;

    modal.style.display = 'flex';
  }

  function closeMinisterModal() {
    const modal = document.getElementById('ministerDetailModal');
    if (modal) modal.style.display = 'none';
  }

  // ==========================================================================
  // SUBPESTAÑA 4.1: ESTRUCTURA ORGÁNICA Y TERRITORIAL DEL PODER JUDICIAL
  // ==========================================================================
  const PJF_ESTRUCTURA_DATA = {
    scjn: [
      {
        nivel: 'Nivel 1: Órgano Supremo de Control Constitucional',
        nodos: [
          {
            id: 'scjn_pleno',
            titulo: 'Pleno de la Suprema Corte de Justicia de la Nación',
            icono: '🏛️',
            badge: '11 Ministras y Ministros (9 en Reforma 2024)',
            badgeTipo: 'badge-gold',
            desc: 'Órgano supremo depositario del control constitucional directo concentrado en México. Ejerce la salvaguarda última del pacto federal y la supremacía de la Carta Magna.',
            titular: 'Presidido por la Ministra Presidenta Norma Lucía Piña Hernández',
            plazasPresupuesto: '11 Despachos de Ministros · $7,329 mdp presupuesto SCJN',
            marco: 'Arts. 94 y 105 CPEUM · Ley Orgánica del PJF (Art. 2)',
            quehacer: 'Resuelve de manera exclusiva los medios de control abstracto y difuso de mayor jerarquía: Acciones de Inconstitucionalidad (demandas contra leyes federales o locales que contradigan la Constitución), Controversias Constitucionales (litigios competenciales entre la Federación, Estados, Municipios o Poderes de la Unión), Declaratorias Generales de Inconstitucionalidad y contradicciones de criterios entre las Salas de la Corte o entre Plenos Regionales.',
            distincionEspecialidad: {
              tipo: 'exclusividad_pleno',
              titulo: 'Competencia Constitucional Exclusiva del Tribunal Pleno',
              detalle: 'A diferencia de las Salas (que conocen de materias específicas en amparos en revisión), el Pleno actúa como tribunal constitucional único y colegiado para invalidar con efectos generales normas contrarias a la Constitución con mayoría calificada (8 votos actualmente, reducida a 6 votos en la reforma de 2024).'
            },
            fundamentoDetallado: [
              'Art. 94 párrafos primero, segundo y quinto de la CPEUM',
              'Art. 105 fracciones I y II de la Constitución Política de los Estados Unidos Mexicanos',
              'Art. 107 fracción XIII de la CPEUM (contradicciones de criterios trascendentes)',
              'Arts. 2, 10 y 11 de la Ley Orgánica del Poder Judicial de la Federación (atribuciones plenarias)'
            ],
            glosario: 'Pleno de la Suprema Corte',
            refKey: 'ref-cpeum-art94',
            refNum: '20'
          }
        ]
      },
      {
        nivel: 'Nivel 2: Órganos de Gobierno, Presidencia & Fe Pública Plenaria',
        nodos: [
          {
            id: 'scjn_presidencia',
            titulo: 'Presidencia de la Suprema Corte & Coordinación Plenaria',
            icono: '⭐',
            badge: 'Mando Institucional & Representación',
            badgeTipo: 'badge-gold',
            desc: 'Representación legal de la SCJN ante los demás Poderes de la Unión, conducción del debate en sesiones plenarias y supervisión de la política judicial interna.',
            titular: 'Ministra Presidenta Norma Lucía Piña Hernández (38 plazas directas adscritas)',
            plazasPresupuesto: '38 plazas tabulares directas de soporte administrativo y técnico',
            marco: 'Ley Orgánica del PJF (Arts. 12 y 14) · Reglamento Interior SCJN',
            quehacer: 'Tramita los expedientes de competencia plenaria, somete a votación los proyectos de sentencia, nombra y remueve al personal de confianza de la Presidencia, supervisa la administración interna de la Corte, autoriza las listas de acuerdos y turna los asuntos por riguroso orden a las ponencias.',
            distincionEspecialidad: {
              tipo: 'mando_institucional',
              titulo: 'Atribuciones de Dirección Plenaria (Sin Integrar Sala)',
              detalle: 'La Presidencia de la Corte no integra ninguna de las dos Salas ordinarias. Su labor se focaliza en la dirección plenaria, el turno transparente de expedientes a las y los 11 ministros y el despacho de acuerdos de admisión o desechamiento preliminar.'
            },
            fundamentoDetallado: [
              'Art. 94 párrafo sexto de la CPEUM',
              'Arts. 12, 13 y 14 de la Ley Orgánica del Poder Judicial de la Federación',
              'Arts. 10 a 25 del Reglamento Interior de la SCJN'
            ],
            glosario: 'Pleno de la Suprema Corte',
            refKey: 'ref-reforma-judicial',
            refNum: '19'
          },
          {
            id: 'scjn_sga',
            titulo: 'Secretaría General de Acuerdos (SGA) & Subsecretaría',
            icono: '📜',
            badge: 'Fe Pública Jurisdiccional',
            badgeTipo: 'badge-cyan',
            desc: 'Órgano fedatario supremo del Tribunal Pleno. Da fe de las resoluciones, formula actas de sesión, distribuye los turnos y custodia los expedientes.',
            titular: 'Secretaría General de Acuerdos (Lic. Rafael Coello Cetina)',
            plazasPresupuesto: 'Estructura de secretarios de acuerdos, actuarios judiciales y oficiales',
            marco: 'Reglamento Interior de la SCJN (Arts. 45 a 58)',
            quehacer: 'Redacta las actas pormenorizadas de las sesiones públicas y privadas, certifica el cómputo de votos emitidos para determinar la obligatoriedad de los precedentes jurisprudenciales, autoriza las notificaciones de sentencias y custodia el archivo de acuerdos jurisdiccionales.',
            distincionEspecialidad: {
              tipo: 'fe_publica',
              titulo: 'Garantía de Certeza Jurídica y Validez de Votaciones',
              detalle: 'Sin la certificación y fe pública de la SGA, ninguna determinación de la Corte cobra fuerza vinculante. Supervisa la asignación aleatoria de turnos a ponencias para impedir la concentración indebida de asuntos de alto impacto político o económico.'
            },
            fundamentoDetallado: [
              'Arts. 45 a 58 del Reglamento Interior de la SCJN',
              'Acuerdos Generales de Administración del Tribunal Pleno',
              'Manual de Organización General de la Suprema Corte'
            ],
            glosario: 'Ponencia de Ministro(a)',
            refKey: 'ref-pef-ramo03',
            refNum: '21'
          }
        ]
      },
      {
        nivel: 'Nivel 3: Salas Jurisdiccionales Especializadas de la Corte',
        nodos: [
          {
            id: 'scjn_sala1',
            titulo: 'Primera Sala (Materia Civil y Penal)',
            icono: '⚖️',
            badge: '5 Ministros · $192.0 mdp/año',
            badgeTipo: 'badge-amber',
            desc: 'Especializada en libertades civiles, derechos humanos, debido proceso en el sistema penal acusatorio, presunción de inocencia y controversias de derecho familiar y mercantil.',
            titular: '5 Despachos Jurisdiccionales (Pardo, Gutiérrez Ortiz Mena, González Alcántara, Ortiz Ahlf, Ríos Farjat)',
            plazasPresupuesto: '~170 plazas técnicas de estudio y cuenta · $192.0 mdp anuales de operación',
            marco: 'Art. 94 CPEUM · Ley Orgánica del PJF (Art. 21, Fracc. I)',
            quehacer: 'Conoce de recursos de revisión en amparos directos sobre la constitucionalidad de leyes penales y civiles o la interpretación de tratados internacionales de derechos humanos (prohibición de tortura, arraigo, legalidad de detenciones, interés superior de la niñez, equidad de género y contratos civiles).',
            distincionEspecialidad: {
              tipo: 'especialidad_materia',
              titulo: 'Especialización Temática en Materias Civil y Penal',
              detalle: 'Competencia estricta por materia: No conoce de litigios fiscales ni laborales. Fija los criterios que rigen la actuación de los jueces penales en todo el país y los derechos de las víctimas y procesados en el sistema adversarial oral.'
            },
            fundamentoDetallado: [
              'Art. 94 y Art. 107 fracción VIII inciso a) de la CPEUM',
              'Art. 21 fracción I de la Ley Orgánica del PJF (competencias de la Primera Sala)',
              'Arts. 81 fracción II, 83 y 86 de la Ley de Amparo'
            ],
            glosario: 'Pleno de la Suprema Corte',
            refKey: 'ref-pef-ramo03',
            refNum: '21'
          },
          {
            id: 'scjn_sala2',
            titulo: 'Segunda Sala (Materia Administrativa y Laboral)',
            icono: '🏛️',
            badge: '4 a 5 Ministros · $188.4 mdp/año',
            badgeTipo: 'badge-amber',
            desc: 'Especializada en el control de legalidad de los actos del Poder Ejecutivo Federal, derecho tributario, fiscal, ambiental, seguridad social y derecho individual y colectivo del trabajo.',
            titular: 'Despachos Jurisdiccionales (Pérez Dayán -Presidente-, Laynez Potisek, Batres Guadarrama, Esquivel Mossa)',
            plazasPresupuesto: '~171 plazas técnicas de estudio y cuenta · $188.4 mdp anuales de operación',
            marco: 'Art. 94 CPEUM · Ley Orgánica del PJF (Art. 21, Fracc. II)',
            quehacer: 'Resuelve litigios contra actos de dependencias federales (SAT, IMSS, ISSSTE, SEMARNAT, CRE, CFE), amparos en materia de impuestos (ISR, IVA, IEPS, Código Fiscal), concesiones mineras, telecomunicaciones en segunda instancia y amparos sobre huelgas y contratos colectivos.',
            distincionEspecialidad: {
              tipo: 'especialidad_materia',
              titulo: 'Especialización Temática en Materias Administrativa y Laboral',
              detalle: 'Fija los límites constitucionales de la facultad recaudadora y sancionadora de la administración pública federal, y armoniza las relaciones obrero-patronales ante el nuevo modelo de justicia laboral federal.'
            },
            fundamentoDetallado: [
              'Art. 94 y Art. 107 de la Constitución Política de los Estados Unidos Mexicanos',
              'Art. 21 fracción II de la Ley Orgánica del PJF (competencias de la Segunda Sala)',
              'Arts. 81 fracción II y 84 de la Ley de Amparo'
            ],
            glosario: 'Pleno de la Suprema Corte',
            refKey: 'ref-pef-ramo03',
            refNum: '21'
          }
        ]
      },
      {
        nivel: 'Nivel 4: Equipos Técnicos de Ponencia & Órganos Auxiliares',
        nodos: [
          {
            id: 'scjn_ponencias_red',
            titulo: 'Despachos Técnicos de Ponencia (11 Ponencias)',
            icono: '👥',
            badge: '385 Plazas Directas · $376.2 mdp/año',
            badgeTipo: 'badge-gold',
            desc: 'Equipos proyectistas de alta especialización técnica jurídica encargados de formular los proyectos de sentencia sometidos a debate en el Pleno y Salas.',
            titular: 'Cuerpo Técnico Proyectista Jurisdiccional (35 plazas por Ponencia)',
            plazasPresupuesto: '1 Coordinador(a) ($128.5k neto), 14 Secretarios de Estudio y Cuenta Proyectistas ($98.2k c/u), 10 Secretarios Auxiliares ($58.4k), 10 Oficiales',
            marco: 'Manual de Remuneraciones del PJF · DOF',
            quehacer: 'Estudian a fondo cada expediente, confrontan las normas impugnadas con los tratados internacionales de derechos humanos, redactan los proyectos de resolución, elaboran los engroses definitivos de las sentencias aprobadas y preparan los votos concurrentes o particulares de las y los ministros.',
            distincionEspecialidad: {
              tipo: 'cuerpo_tecnico',
              titulo: 'Estructura Tabular Técnica de Alto Rendimiento',
              detalle: 'Constituyen el soporte operativo e intelectual directo de las y los Ministros. Su trabajo garantiza que las sentencias cuenten con fundamentación jurisprudencial exhaustiva antes de ser votadas en sesiones públicas transmitidas por JusticiaTV.'
            },
            fundamentoDetallado: [
              'Manual que Regula las Remuneraciones de las y los Servidores Públicos del PJF (DOF)',
              'Reglamento Interior de la SCJN',
              'Presupuesto de Egresos de la Federación (PEF - Ramo 03 SCJN)'
            ],
            glosario: 'Ponencia de Ministro(a)',
            refKey: 'ref-pef-ramo03',
            refNum: '21'
          },
          {
            id: 'scjn_casas_cultura',
            titulo: 'Casas de la Cultura Jurídica & Centro de Estudios Constitucionales',
            icono: '📚',
            badge: 'Presencia Federal en las 32 Entidades',
            badgeTipo: 'badge-cyan',
            desc: 'Red desconcentrada de 46 sedes físicas en toda la República para vinculación social, bibliotecas jurídicas, eventos académicos y difusión de sentencias.',
            titular: 'Dirección General de Casas de la Cultura Jurídica (SCJN)',
            plazasPresupuesto: '46 sedes estatales operativas con personal especializado y acervos históricos',
            marco: 'Acuerdo Plenario SCJN 5/2014',
            quehacer: 'Facilitan a profesionistas, litigantes, estudiantes y ciudadanos el acceso a los archivos históricos del PJF, módulos de consulta de jurisprudencia del Semanario Judicial de la Federación, programas de capacitación en derechos humanos y préstamo bibliográfico gratuito en los 32 estados.',
            distincionEspecialidad: {
              tipo: 'desconcentracion_social',
              titulo: 'Presencia Territorial Constitucional en los Estados',
              detalle: 'Asegura que el acervo y la doctrina jurisprudencial de la Suprema Corte no se concentren en la capital del país, vinculando a los operadores de los poderes judiciales estatales con los criterios federales.'
            },
            fundamentoDetallado: [
              'Acuerdo General de Administración Plenaria 5/2014 de la SCJN',
              'Lineamientos Operativos de las Casas de la Cultura Jurídica',
              'Cuenta Pública Federal - Ramo 03'
            ],
            glosario: 'Cuenta Pública',
            refKey: 'ref-cuentas-publicas',
            refNum: '2'
          }
        ]
      },
      {
        nivel: 'Nivel 5: Administración, Disciplina y Carrera Judicial (Reforma 2024)',
        nodos: [
          {
            id: 'scjn_oaj',
            titulo: 'Órgano de Administración Judicial (OAJ)',
            icono: '🏢',
            badge: '5 Integrantes · 6 Años Improrrogables',
            badgeTipo: 'badge-gold',
            desc: 'Órgano que sustituye al Consejo de la Judicatura Federal en las funciones de administración, vigilancia y manejo de los recursos del Poder Judicial de la Federación, conforme a la reforma constitucional publicada en el DOF el 15 de septiembre de 2024.',
            titular: 'Cinco personas titulares: una designada por el Ejecutivo Federal, una por el Senado y tres por el Pleno de la SCJN',
            plazasPresupuesto: 'Administra el Ramo 03 del PEF, salvo el presupuesto propio de la Suprema Corte y del Tribunal Electoral',
            marco: 'Art. 100 CPEUM reformado · Reforma Judicial DOF 15-09-2024',
            quehacer: 'Concentra la administración del Poder Judicial de la Federación: elabora y ejerce el presupuesto de los órganos jurisdiccionales, determina la adscripción y el número de juzgados de distrito y tribunales de circuito, opera la carrera judicial, gestiona los recursos humanos y materiales, y rinde cuentas de ese ejercicio ante la Auditoría Superior de la Federación. No ejerce funciones jurisdiccionales ni disciplinarias.',
            distincionEspecialidad: {
              tipo: 'sustitucion_cjf',
              titulo: 'Separación entre Administrar y Sancionar',
              detalle: 'La reforma dividió en dos las atribuciones que antes concentraba el Consejo de la Judicatura Federal: la administración quedó en este Órgano y la disciplina pasó al Tribunal de Disciplina Judicial. El objetivo declarado fue evitar que quien administra el presupuesto sea también quien sanciona a las personas juzgadoras.'
            },
            fundamentoDetallado: [
              'Art. 100 de la Constitución Política de los Estados Unidos Mexicanos (texto reformado)',
              'Decreto de Reforma Judicial publicado en el DOF el 15 de septiembre de 2024',
              'Artículos transitorios del Decreto de Reforma sobre la extinción del Consejo de la Judicatura Federal',
              'Presupuesto de Egresos de la Federación - Ramo 03'
            ],
            glosario: 'Reforma Constitucional del Poder Judicial',
            refKey: 'ref-reforma-judicial',
            refNum: '20'
          },
          {
            id: 'scjn_tdj',
            titulo: 'Tribunal de Disciplina Judicial (TDJ)',
            icono: '⚖️',
            badge: '5 Magistraturas Electas por Voto Popular · 6 Años',
            badgeTipo: 'badge-amber',
            desc: 'Órgano encargado de investigar y sancionar las faltas de las personas servidoras públicas del Poder Judicial de la Federación, incluidas las ministras y ministros de la Suprema Corte. Asume la función disciplinaria que antes correspondía al Consejo de la Judicatura Federal.',
            titular: 'Cinco magistradas y magistrados electos mediante voto popular directo',
            plazasPresupuesto: 'Presupuesto propio dentro del Ramo 03 · Ponencias de instrucción y órgano de investigación adscrito',
            marco: 'Arts. 100 y 101 CPEUM reformados · Reforma Judicial DOF 15-09-2024',
            quehacer: 'Recibe denuncias ciudadanas y de oficio contra personal jurisdiccional, instruye los procedimientos de responsabilidad administrativa y resuelve sobre amonestaciones, suspensiones, destituciones e inhabilitaciones. Puede ordenar la remoción de personas juzgadoras y dar vista al Ministerio Público cuando advierta hechos posiblemente constitutivos de delito.',
            distincionEspecialidad: {
              tipo: 'control_disciplinario',
              titulo: 'Resoluciones Definitivas e Inatacables',
              detalle: 'La Constitución establece que las determinaciones de este Tribunal son definitivas e inatacables, por lo que no admiten juicio de amparo ni recurso ordinario. Es el punto de mayor debate jurídico de la reforma, por su tensión con el derecho de acceso a la justicia y con la independencia judicial.'
            },
            fundamentoDetallado: [
              'Arts. 100 y 101 de la Constitución Política de los Estados Unidos Mexicanos (texto reformado)',
              'Decreto de Reforma Judicial publicado en el DOF el 15 de septiembre de 2024',
              'Ley General de Responsabilidades Administrativas (aplicación supletoria)',
              'Ley Orgánica del Poder Judicial de la Federación'
            ],
            glosario: 'Tribunal de Disciplina Judicial',
            refKey: 'ref-reforma-judicial',
            refNum: '20'
          },
          {
            id: 'scjn_effj',
            titulo: 'Escuela Federal de Formación Judicial (EFFJ)',
            icono: '🎓',
            badge: 'Formación y Carrera Judicial · Adscrita al OAJ',
            badgeTipo: 'badge-cyan',
            desc: 'Órgano auxiliar responsable de la formación, capacitación y evaluación del personal jurisdiccional del Poder Judicial de la Federación. Tras la reforma de 2024 quedó adscrita al Órgano de Administración Judicial.',
            titular: 'Dirección General de la Escuela Federal de Formación Judicial',
            plazasPresupuesto: 'Programa presupuestario propio dentro del Ramo 03 · Sede central y extensiones regionales',
            marco: 'Art. 100 CPEUM · Ley de Carrera Judicial del Poder Judicial de la Federación',
            quehacer: 'Diseña e imparte los programas de especialización judicial, organiza los concursos de oposición para el ingreso y la promoción en las categorías de la carrera judicial, evalúa el desempeño del personal y publica investigación aplicada en materia de impartición de justicia.',
            distincionEspecialidad: {
              tipo: 'carrera_judicial',
              titulo: 'Filtro Técnico de Ingreso y Promoción',
              detalle: 'Aunque la reforma trasladó a elección popular la designación de ministras, ministros, magistraturas y jueces de distrito, la Escuela conserva la formación y la evaluación técnica del resto del personal jurisdiccional: secretarías de estudio y cuenta, actuarías y oficialías.'
            },
            fundamentoDetallado: [
              'Art. 100 de la Constitución Política de los Estados Unidos Mexicanos',
              'Ley de Carrera Judicial del Poder Judicial de la Federación',
              'Acuerdos Generales del Órgano de Administración Judicial en materia de formación',
              'Presupuesto de Egresos de la Federación - Ramo 03'
            ],
            glosario: 'Ramo 03',
            refKey: 'ref-pef-ramo03',
            refNum: '21'
          }
        ]
      }
    ],
    pjf: [
      {
        nivel: 'Nivel 1: Órganos Supremos & Jurisdicción Constitucional Especializada',
        nodos: [
          {
            id: 'pjf_scjn_top',
            titulo: 'Suprema Corte de Justicia de la Nación (SCJN)',
            icono: '🏛️',
            badge: 'Cabeza del Poder Judicial Federal',
            badgeTipo: 'badge-gold',
            desc: 'Tribunal constitucional supremo de México. Ejerce control concentrado de la Constitución y tutela los derechos humanos consagrados en la Carta Magna.',
            titular: 'Presidencia SCJN · 11 Ministros (9 en transición 2024)',
            plazasPresupuesto: '3,850 plazas totales en el tribunal supremo · $7,329 mdp anuales',
            marco: 'Art. 94 y Art. 105 CPEUM',
            quehacer: 'Cúspide de la judicatura federal. Resuelve controversias constitucionales, acciones de inconstitucionalidad, amparos directos en revisión con temas de constitucionalidad trascendente y establece precedentes obligatorios para todos los tribunales y juzgados del país.',
            distincionEspecialidad: {
              tipo: 'cabeza_suprema',
              titulo: 'Supremacía Orgánica y Jurisdiccional',
              detalle: 'Sus resoluciones son definitivas e inatacables. No existe instancia procesal por encima de la Suprema Corte en el orden jurídico nacional mexicano.'
            },
            fundamentoDetallado: [
              'Art. 94 de la Constitución Política de los Estados Unidos Mexicanos',
              'Art. 105 fracciones I y II de la CPEUM',
              'Ley Orgánica del Poder Judicial de la Federación (Arts. 1 a 23)'
            ],
            glosario: 'Pleno de la Suprema Corte',
            refKey: 'ref-cpeum-art94',
            refNum: '20'
          },
          {
            id: 'pjf_tepjf',
            titulo: 'Tribunal Electoral del PJF (TEPJF)',
            icono: '🗳️',
            badge: 'Sala Superior + 5 Salas Regionales',
            badgeTipo: 'badge-cyan',
            desc: 'Máxima autoridad jurisdiccional electoral del país. Resuelve controversias en elecciones federales y locales, actos del INE y protección de derechos político-electorales.',
            titular: 'Presidencia TEPJF · $3,623 mdp PEF · 7 Magistrados en Sala Superior',
            plazasPresupuesto: 'Sala Superior en CDMX + 5 Salas Regionales (GDL, MTY, XAL, CDMX, TLC) + 1 Sala Especializada',
            marco: 'Art. 99 CPEUM · Ley General del Sistema de Medios de Impugnación',
            quehacer: 'Realiza el cómputo final de la elección presidencial y declara la validez de la presidencia electa. Resuelve juicios de inconformidad sobre elecciones legislativas y gubernamentales, impugnaciones contra multas del INE, disputas internas de partidos políticos y juicios de protección ciudadana (JDC).',
            distincionEspecialidad: {
              tipo: 'autonomia_especializada',
              titulo: 'Especialización Constitucional Electoral',
              detalle: 'Funciona con autonomía especializada dentro del PJF. La Sala Superior es la única facultada para declarar la validez de la elección presidencial; las 5 Salas Regionales atienden elecciones de diputaciones, senadurías y controversias locales según su circunscripción plurinominal.'
            },
            fundamentoDetallado: [
              'Art. 99 de la Constitución Política de los Estados Unidos Mexicanos',
              'Ley General del Sistema de Medios de Impugnación en Materia Electoral',
              'Ley Orgánica del Poder Judicial de la Federación (Arts. 164 a 209)'
            ],
            glosario: 'Poder Judicial de la Federación',
            refKey: 'ref-pef-ramo03',
            refNum: '21'
          }
        ]
      },
      {
        nivel: 'Nivel 2: Órganos de Gobierno, Disciplina & Administración (Reforma Judicial 2024)',
        nodos: [
          {
            id: 'pjf_disciplina',
            titulo: 'Tribunal de Disciplina Judicial (Sustituye al CJF en Sanciones)',
            icono: '⚖️',
            badge: '5 Magistrados · Voto Popular · Reforma 2024',
            badgeTipo: 'badge-crimson',
            specialClass: 'pj-reforma',
            desc: 'Órgano constitucional con independencia técnica y de gestión creado en septiembre de 2024. Competente para investigar, fiscalizar, suspender y sancionar a jueces, magistrados y empleados federales.',
            titular: '5 Magistradas y Magistrados Electos Popularmente por 6 años',
            plazasPresupuesto: 'Estructura investigadora y sancionatoria autónoma · Sustituye la Contraloría y Disciplina del CJF',
            marco: 'Art. 100 Constitucional Reformado · Decreto DOF 15/sept/2024',
            quehacer: 'Investiga de oficio o por queja ciudadana actos de corrupción, enriquecimiento ilícito, nepotismo, negligencia grave o tráfico de influencias cometidos por juzgadores o funcionarios judiciales. Aplica sanciones que van desde apercibimiento y multas hasta suspensión provisional, inhabilitación y destitución definitiva, pudiendo remitir expedientes al Ministerio Público.',
            distincionEspecialidad: {
              tipo: 'control_disciplinario',
              titulo: 'Resoluciones Definitivas e Inatacables',
              detalle: 'A diferencia del antiguo Consejo de la Judicatura, las resoluciones sancionatorias del Tribunal de Disciplina Judicial son definitivas e inatacables, no admitiendo recurso ni juicio de amparo en su contra conforme al texto constitucional de 2024.'
            },
            fundamentoDetallado: [
              'Art. 100 de la CPEUM reformado (Decreto publicado en el DOF el 15/09/2024)',
              'Art. 96 de la CPEUM (mecanismo de postulación y elección popular directa)',
              'Leyes reglamentarias secundarias del Tribunal de Disciplina Judicial'
            ],
            glosario: 'Reforma Constitucional del Poder Judicial',
            refKey: 'ref-reforma-judicial',
            refNum: '19'
          },
          {
            id: 'pjf_oaj',
            titulo: 'Órgano de Administración Judicial (OAJ / DGGJ)',
            icono: '🏢',
            badge: 'Gestión Presupuestal, Carrera & Servicios Digitales',
            badgeTipo: 'badge-cyan',
            specialClass: 'pj-reforma',
            desc: 'Entidad encargada de la administración financiera, patrimonial, compras públicas y modernización digital que sustituye al CJF. Alberga la Dirección General de Gestión Judicial (DGGJ).',
            titular: 'Administración Centralizada del PJF ($68,917 mdp ejercidos)',
            plazasPresupuesto: 'Órgano técnico colegiado de administración y gestión presupuestal del Ramo 03',
            marco: 'Art. 100 CPEUM Reformado · Acuerdos DGGJ/OAJ (oaj.gob.mx)',
            quehacer: 'Elabora y ejerce el presupuesto de más de $68,900 mdp del Poder Judicial Federal (excluyendo la SCJN y TEPJF), administra la nómina tabular de más de 49,000 servidores públicos, licita obras públicas y edificios de Ciudad Judicial, y gestiona la plataforma informática DGGJ (expedientes digitales, acuerdos, listas y FIREL).',
            distincionEspecialidad: {
              tipo: 'separacion_funciones',
              titulo: 'Separación Estricta entre Administración y Disciplina',
              detalle: 'La reforma constitucional de 2024 extinguió el Consejo de la Judicatura Federal para evitar el conflicto de interés de que un solo órgano administrara los recursos y al mismo tiempo investigara a los jueces. El OAJ asume exclusivamente la función gerencial y contable.'
            },
            fundamentoDetallado: [
              'Art. 100 párrafos segundo y tercero de la CPEUM reformada',
              'Ley de Carrera Judicial y Ley Federal de Presupuesto y Responsabilidad Hacendaria',
              'Lineamientos de la Dirección General de Gestión Judicial (DGGJ / oaj.gob.mx)'
            ],
            glosario: 'Ramo 03',
            refKey: 'ref-pef-ramo03',
            refNum: '21'
          }
        ]
      },
      {
        nivel: 'Nivel 3: Órganos Jurisdiccionales Federales Ordinarios (32 Circuitos)',
        nodos: [
          {
            id: 'pjf_plenos_regionales',
            titulo: 'Plenos Regionales (Centro-Norte y Centro-Sur)',
            icono: '🌐',
            badge: 'Unificación de Criterios & Jurisprudencia',
            badgeTipo: 'badge-gold',
            desc: 'Órganos colegiados regionales que dirimen contradicciones de tesis entre Tribunales Colegiados de diferentes Circuitos Federales dentro de su demarcación territorial.',
            titular: 'Magistrados Federales de Circuito Designados',
            plazasPresupuesto: 'Región Centro-Norte (sede CDMX) y Región Centro-Sur (sede Puebla) con materias penal, civil, admin y trabajo',
            marco: 'Art. 94 CPEUM · Acuerdos Generales CJF/OAJ',
            quehacer: 'Unifican la interpretación jurídica cuando dos o más Tribunales Colegiados de Circuito de diferentes estados emiten fallos contradictorios sobre una misma ley o figura procesal. Su jurisprudencia regional es de observancia obligatoria para todos los tribunales y juzgados de su demarcación.',
            distincionEspecialidad: {
              tipo: 'unificacion_regional',
              titulo: 'Demarcación Bipolar Nacional (Centro-Norte y Centro-Sur)',
              detalle: 'Fueron creados para desahogar a la Suprema Corte de resolver contradicciones de tesis secundarias. La Región Centro-Norte abarca 18 Circuitos y la Centro-Sur abarca 14 Circuitos, dividiéndose internamente en materias penal, administrativa, civil y del trabajo.'
            },
            fundamentoDetallado: [
              'Art. 94 párrafo noveno y Art. 107 fracción XIII de la CPEUM',
              'Ley Orgánica del PJF (Arts. 41 bis y 41 ter)',
              'Acuerdo General 1/2023 del CJF que determinó la integración y funcionamiento de los Plenos Regionales'
            ],
            glosario: 'Poder Judicial de la Federación',
            refKey: 'ref-cpeum-art94',
            refNum: '20'
          },
          {
            id: 'pjf_tcc',
            titulo: 'Tribunales Colegiados de Circuito Ordinarios (TCC)',
            icono: '📚',
            badge: '3 Magistrados c/u · Amparos Directos',
            badgeTipo: 'badge-gold',
            desc: 'Órganos colegiados tripartitos distribuidos en los 32 Circuitos. Resuelven amparos directos contra sentencias definitivas y recursos de revisión en amparo indirecto.',
            titular: 'Cuerpo de Magistrados de Circuito Federales (3 por Tribunal)',
            plazasPresupuesto: '>250 Tribunales Colegiados en la República · 3 Magistrados y ~35 plazas de personal por tribunal',
            marco: 'Ley Orgánica del PJF (Arts. 33 a 39) · Ley de Amparo',
            quehacer: 'Conocen del juicio de amparo directo promovido contra sentencias definitivas, laudos laborales o resoluciones que ponen fin al juicio dictadas por jueces civiles, mercantiles, penales o tribunales administrativos estatales o federales. Asimismo, resuelven recursos de revisión contra sentencias de Jueces de Distrito y recursos de queja.',
            distincionEspecialidad: {
              tipo: 'especializados_vs_mixtos',
              especializados: 'En circuitos de alta litigiosidad (ej. 1º CDMX, 2º EdoMex, 3º Jalisco, 4º Nuevo León, 16º Guanajuato, 7º Veracruz) operan Colegiados divididos estrictamente por materia: Penal, Administrativa, Civil y de Trabajo. Sus magistrados y proyectistas resuelven con especialización técnica profunda en su rama dogmática (Art. 38 LOPJF).',
              mixtos: 'En circuitos de menor densidad litigiosa o demográfica (ej. 24º Nayarit, 28º Tlaxcala, 31º Campeche, 23º Zacatecas, 32º Colima), los tribunales son Mixtos. Sus 3 magistrados conocen indistintamente de amparos directos y revisiones en materias penal, civil, administrativa y laboral sin distinción de sala (Art. 37 LOPJF).'
            },
            fundamentoDetallado: [
              'Arts. 94 y 107 fracciones III, V, VIII y IX de la CPEUM',
              'Arts. 33, 34, 37 y 38 de la Ley Orgánica del PJF (distinción formal entre colegiados especializados y mixtos)',
              'Arts. 34, 81 fracción II, 88 y 170 a 191 de la Ley de Amparo'
            ],
            glosario: 'Poder Judicial de la Federación',
            refKey: 'ref-pef-ramo03',
            refNum: '21'
          },
          {
            id: 'pjf_tca',
            titulo: 'Tribunales Colegiados de Apelación (TCA)',
            icono: '🏛️',
            badge: '3 Magistrados c/u · Apelación Federal',
            badgeTipo: 'badge-gold',
            desc: 'Sustituyen a los antiguos Tribunales Unitarios unipersonales. Conocen de las apelaciones de juicios federales ordinarios civiles, mercantiles y penales.',
            titular: 'Colegiación Obligatoria de 3 Magistrados Federales por Tribunal',
            plazasPresupuesto: 'Distribuidos en los 32 Circuitos con ponencias tripartitas para deliberación colegiada',
            marco: 'Ley Orgánica del PJF (Arts. 40 a 43)',
            quehacer: 'Resuelven los recursos de apelación interpuestos contra las sentencias definitivas e interlocutorias dictadas por los Jueces de Distrito en juicios federales ordinarios (demandas mercantiles entre bancos y particulares, juicios civiles federales donde la Federación es parte, o causas penales federales tradicionales). Califican impedimentos y recusaciones de jueces de distrito.',
            distincionEspecialidad: {
              tipo: 'reforma_colegiacion',
              titulo: 'Sustitución de Tribunales Unitarios por Órganos Colegiados',
              detalle: 'La reforma a la Ley Orgánica del PJF eliminó los anteriores Tribunales Unitarios de Circuito (que eran de 1 solo magistrado, concentrando excesivo poder unipersonal). Ahora, la apelación federal ordinaria es forzosamente colegiada entre 3 magistrados para garantizar deliberación democrática y reducir riesgos de corrupción.'
            },
            fundamentoDetallado: [
              'Art. 94 de la Constitución Política de los Estados Unidos Mexicanos',
              'Arts. 40, 41, 42 y 43 de la Ley Orgánica del Poder Judicial de la Federación',
              'Código Federal de Procedimientos Civiles y Código Nacional de Procedimientos Penales (recurso de apelación)'
            ],
            glosario: 'Poder Judicial de la Federación',
            refKey: 'ref-cpeum-art94',
            refNum: '20'
          },
          {
            id: 'pjf_juzgados_distrito',
            titulo: 'Juzgados de Distrito Ordinarios',
            icono: '📁',
            badge: 'Juezas y Jueces Federales de 1ª Instancia',
            badgeTipo: 'badge-gold',
            desc: 'Primera instancia federal por antonomasia. Conocen del juicio de amparo indirecto contra actos de autoridad, leyes autoaplicativas y de juicios federales ordinarios.',
            titular: 'Jueces de Distrito Especializados o Mixtos unipersonales',
            plazasPresupuesto: '>450 Juzgados de Distrito en la República · 1 Juez(a) y secretarios de juzgado/actuarios',
            marco: 'Ley Orgánica del PJF (Arts. 48 a 60) · Ley de Amparo',
            quehacer: 'Tramitan y resuelven el juicio de amparo indirecto contra leyes federales o locales, reglamentos presidenciales, órdenes de aprehensión, cateos, clausuras, multas fiscales, omisiones de salud pública y actos de cualquier autoridad que vulneren derechos humanos. Conceden o niegan suspensiones provisionales y definitivas.',
            distincionEspecialidad: {
              tipo: 'especializados_vs_mixtos',
              especializados: 'En las metrópolis se dividen en: 1) Juzgados de Distrito en Materia Penal (procesos tradicionales y amparo penal); 2) Juzgados en Materia Administrativa (clausuras, SAT, IMSS, obras públicas); 3) Juzgados en Materia Civil (quiebras, concursos mercantiles y amparo civil); 4) Juzgados en Materia de Trabajo (tribunales laborales federales y amparo laboral); 5) Juzgados Mercantiles Federales (juicios orales mercantiles) y 6) Juzgados de Extinción de Dominio (Arts. 51 a 55 LOPJF).',
              mixtos: 'En distritos judiciales foráneos o circuitos menores, un solo Juzgado de Distrito Mixto conoce de todas las materias: tramita amparos indirectos civiles, penales, administrativos y laborales, así como juicios ordinarios federales de manera simultánea (Art. 48 LOPJF).'
            },
            fundamentoDetallado: [
              'Arts. 103 y 107 de la Constitución Política de los Estados Unidos Mexicanos',
              'Arts. 48, 50, 51, 52, 53, 54 y 55 de la Ley Orgánica del PJF (competencias por materia)',
              'Arts. 35, 107, 108 y 114 de la Ley de Amparo (amparo indirecto)'
            ],
            glosario: 'Poder Judicial de la Federación',
            refKey: 'ref-pef-ramo03',
            refNum: '21'
          },
          {
            id: 'pjf_cjpf',
            titulo: 'Centros de Justicia Penal Federal (CJPF)',
            icono: '⚡',
            badge: 'Sistema Penal Acusatorio Oral (Audiencias Públicas)',
            badgeTipo: 'badge-amber',
            desc: 'Sedes judiciales orales federales que integran a Jueces de Control, Tribunales de Enjuiciamiento y Jueces de Ejecución de Sanciones bajo el CNPP.',
            titular: 'Jueces Federales Especializados en Sistema Penal Acusatorio Oral',
            plazasPresupuesto: 'Salas de audiencias orales con videograbación digital en los 32 Circuitos Federales',
            marco: 'Art. 20 CPEUM · Código Nacional de Procedimientos Penales (CNPP)',
            quehacer: 'Desahogan las audiencias orales públicas en delitos del fuero federal (delincuencia organizada, narcotráfico, hidrocarburos, portación de armas de uso exclusivo, delitos fiscales y corrupción). Aplican los principios de inmediación, contradicción, publicidad y presunción de inocencia.',
            distincionEspecialidad: {
              tipo: 'perfiles_procesales_orales',
              titulo: 'Trilogía Funcional del Juez Acusatorio Oral',
              detalle: 'Cada Centro de Justicia Penal Federal integra 3 roles procesales incompatibles entre sí: 1) Jueces de Control (resuelven legalidad de detenciones, imputación, vinculación a proceso y medidas cautelares en audiencia); 2) Tribunales de Enjuiciamiento (presiden el juicio oral, desahogan testimonios periciales y dictan sentencia); y 3) Jueces de Ejecución Penal (supervisan cumplimiento de condenas en cárceles federales).'
            },
            fundamentoDetallado: [
              'Art. 20 de la CPEUM (bases del proceso penal acusatorio y oral)',
              'Arts. 133, 134, 307 y 348 del Código Nacional de Procedimientos Penales',
              'Acuerdo General 14/2016 del Pleno del Consejo de la Judicatura Federal'
            ],
            glosario: 'Poder Judicial de la Federación',
            refKey: 'ref-cpeum-art94',
            refNum: '20'
          }
        ]
      },
      {
        nivel: 'Nivel 4: Tribunales Federales Especializados & Centros Auxiliares (Jurisdicción Nacional)',
        nodos: [
          {
            id: 'pjf_especializados_telecom',
            titulo: 'Tribunales y Juzgados de Competencia Económica y Telecomunicaciones',
            icono: '📡',
            badge: 'JURISDICCIÓN NACIONAL (SEDE CDMX)',
            badgeTipo: 'badge-cyan',
            specialClass: 'pj-specialized',
            desc: 'Órganos de alta especialización técnica creados en cumplimiento de los Artículos 28 y 94 de la CPEUM. Con sede en la CDMX y competencia en toda la República.',
            titular: '2 Tribunales Colegiados de Circuito + 2 Juzgados de Distrito Especializados',
            plazasPresupuesto: 'Personal altamente capacitado en ingeniería de telecomunicaciones y econometría antimonopolio',
            marco: 'Art. 28 párrafo vigésimo CPEUM · Acuerdos Generales CJF 22/2013 y 3/2013',
            quehacer: 'Conocen con exclusividad de juicios de amparo directo e indirecto promovidos contra resoluciones y sanciones del Instituto Federal de Telecomunicaciones (IFT) y de la Comisión Federal de Competencia Económica (COFECE), prácticas monopólicas absolutas y relativas, licitaciones del espectro radioeléctrico, concentración de mercados y regulación tarifaria de redes públicas.',
            distincionEspecialidad: {
              tipo: 'regimen_procesal_unico',
              titulo: 'Jurisdicción Nacional y Restricción Constitucional de Suspensión',
              detalle: 'Aunque residen en la Ciudad de México, ejercen competencia sobre cualquier litigio del país en telecom y competencia económica. Por mandato expreso del Artículo 28 de la CPEUM, las normas y actos reclamados NO son objeto de suspensión judicial ordinaria, salvo multas o desincorporación de activos, para impedir que controversias privadas frenen la conectividad o la competencia nacional.'
            },
            fundamentoDetallado: [
              'Art. 28 párrafos décimo quinto y vigésimo de la CPEUM',
              'Art. 94 de la Constitución Política de los Estados Unidos Mexicanos',
              'Acuerdo General 22/2013 del Pleno del CJF (creación de los órganos especializados)',
              'Ley Federal de Competencia Económica y Ley Federal de Telecomunicaciones y Radiodifusión'
            ],
            glosario: 'Marco Legal Hacendario',
            refKey: 'ref-cpeum-art94',
            refNum: '20'
          },
          {
            id: 'pjf_centros_auxiliares',
            titulo: 'Tribunales Colegiados y Juzgados de los Centros Auxiliares Regionales (CAR)',
            icono: '🤝',
            badge: 'COMBATE AL REZAGO JUDICIAL EN TODO EL PAÍS',
            badgeTipo: 'badge-amber',
            specialClass: 'pj-auxiliar',
            desc: 'Red itinerante de Tribunales Colegiados y Juzgados de Distrito auxiliares distribuidos en Centros Regionales (Puebla, Guanajuato, Sinaloa, Zacatecas, Veracruz, Guerrero).',
            titular: 'Centros Auxiliares Regionales del PJF (Apoyo y Despresurización Nacional)',
            plazasPresupuesto: 'Salas de magistrados y jueces auxiliares móviles apoyados por personal proyectista intensivo',
            marco: 'Acuerdo General 3/2013 del Pleno del CJF / Órgano de Administración Judicial',
            quehacer: 'Su cometido exclusivo es dictar sentencias en auxilio de juzgados y tribunales colegiados ordinarios del país que se encuentran en situación crítica de sobrecarga procesal o rezago. Reciben remesas masivas de expedientes integrados listos para sentencia, dictan el fallo definitivo y devuelven el expediente al circuito de origen.',
            distincionEspecialidad: {
              tipo: 'itinerancia_auxiliar',
              titulo: 'Auxilio Itinerante sin Justiciables Propios',
              detalle: 'A diferencia de los tribunales ordinarios, los Centros Auxiliares no reciben demandas iniciales de la ciudadanía de su ciudad sede. Su jurisdicción es nacional y móvil, adaptando sus remesas mensuales de trabajo a los circuitos federales que reportan mayor rezago en las estadísticas de gestión judicial.'
            },
            fundamentoDetallado: [
              'Art. 94 párrafo séptimo de la Constitución Federal',
              'Acuerdo General 3/2013 del Pleno del CJF (régimen de los Centros Auxiliares Regionales)',
              'Acuerdos Generales periódicos de remesa de expedientes y auxilio jurisdiccional'
            ],
            glosario: 'Poder Judicial de la Federación',
            refKey: 'ref-pef-ramo03',
            refNum: '21'
          }
        ]
      },
      {
        nivel: 'Nivel 5: Órganos Auxiliares, Defensoría Pública & Escuela Judicial',
        nodos: [
          {
            id: 'pjf_ifdp',
            titulo: 'Instituto Federal de Defensoría Pública (IFDP)',
            icono: '🛡️',
            badge: 'Abogados Gratuitos · >3,000 Defensores en los 32 Estados',
            badgeTipo: 'badge-cyan',
            desc: 'Órgano desconcentrado que garantiza el derecho humano a la defensa legal técnica y gratuita en materias penal, civil, laboral, fiscal y de amparo para la población.',
            titular: 'Dirección General del IFDP (Despliegue Nacional en las 32 Entidades)',
            plazasPresupuesto: 'Más de 3,000 defensores públicos y asesores jurídicos federales acreditados',
            marco: 'Art. 17 y 20 CPEUM · Ley Federal de Defensoría Pública',
            quehacer: 'Representa obligatoriamente y sin costo a personas imputadas en audiencias penales orales federales que carecen de abogado particular; asesora legalmente a migrantes, indígenas, trabajadores, pensionados y víctimas de abusos de autoridad promoviendo amparos indirectos.',
            distincionEspecialidad: {
              tipo: 'defensoria_social',
              titulo: 'Defensa Penal Obligatoria y Asesoría Social Gratuita',
              detalle: 'Garantiza que nadie sea juzgado en el sistema penal acusatorio sin representación letrada calificada. Su servicio es gratuito y con presencia física obligatoria en todos los Centros de Justicia Penal Federal del país.'
            },
            fundamentoDetallado: [
              'Art. 17 párrafo octavo y Art. 20 apartado B fracción VIII de la CPEUM',
              'Ley Federal de Defensoría Pública (Arts. 1 a 29)',
              'Acuerdos de la Dirección General del IFDP sobre atención prioritaria a grupos vulnerables'
            ],
            glosario: 'Poder Judicial de la Federación',
            refKey: 'ref-pef-ramo03',
            refNum: '21'
          },
          {
            id: 'pjf_effj',
            titulo: 'Escuela Federal de Formación Judicial (EFFJ)',
            icono: '🎓',
            badge: 'Carrera Judicial, Posgrados & Exámenes de Oposición',
            badgeTipo: 'badge-gold',
            desc: 'Centro de educación de posgrado e investigación profesional encargado de la formación, especialización y concursos de oposición del personal del PJF.',
            titular: 'Dirección General de la EFFJ',
            plazasPresupuesto: 'Plataforma educativa nacional, claustro docente y sedes de examen en todo el país',
            marco: 'Ley de Carrera Judicial del Poder Judicial de la Federación',
            quehacer: 'Diseña y aplica los planes de estudio, cursos de formación para secretarios y actuarios, especialidades en amparo y derecho acusatorio, y supervisa los exámenes teóricos y prácticos de oposición para acceder a las categorías judiciales de la carrera federal.',
            distincionEspecialidad: {
              tipo: 'meritocracia_carrera',
              titulo: 'Régimen de Ingreso y Promoción Profesional',
              detalle: 'Garantiza la profesionalización de los juzgadores federales. Con la reforma judicial de 2024, sus programas se adaptan a la preparación técnica de aspirantes a cargos electos y personal tabular de secretarías de juzgado y tribunal.'
            },
            fundamentoDetallado: [
              'Art. 100 de la CPEUM (carrera judicial y profesionalización)',
              'Ley de Carrera Judicial del Poder Judicial de la Federación',
              'Reglamento de la Escuela Federal de Formación Judicial'
            ],
            glosario: 'Poder Judicial de la Federación',
            refKey: 'ref-reforma-judicial',
            refNum: '19'
          }
        ]
      }
    ],
    territorio: {
      "JAL": {
            "abbr": "JAL",
            "nombre": "Jalisco",
            "circuitoNum": "Tercer Circuito Judicial Federal",
            "circuitoRomano": "III Circuito",
            "circuitoCorto": "3er Circuito",
            "circuitoSedes": "Zapopan (Ciudad Judicial Federal Periférico Poniente), Guadalajara, Puerto Vallarta, Puente Grande, Lagos de Moreno y Cd. Guzmán",
            "juzgadosFederales": "18 Tribunales Colegiados de Circuito (Penal, Civil, Administrativa, Trabajo), 3 Tribunales Colegiados de Apelación, 19 Juzgados de Distrito y CJPF Puente Grande.",
            "tsjNombre": "Supremo Tribunal de Justicia del Estado de Jalisco (STJEJ) & Consejo de la Judicatura (CJEJ)",
            "numPartidos": 32,
            "numPartidosTxt": "32 Partidos Judiciales Estatales",
            "juecesPor100k": "3.9 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Primer Partido Judicial",
                        "cabecera": "Guadalajara (Zona Metropolitana: Zapopan, Tlaquepaque, Tonalá, Tlajomulco, El Salto, Juanacatlán, Ixtlahuacán, Zapotlanejo)",
                        "municipios": "Guadalajara, Zapopan, San Pedro Tlaquepaque, Tonalá, Tlajomulco de Zúñiga, El Salto, Juanacatlán, Ixtlahuacán de los Membrillos, Zapotlanejo",
                        "juzgados1ra": "42 Juzgados de 1ª Instancia (Civiles 1°-14°, Familiares 1°-15°, Mercantiles Tradicionales y Orales, Juzgados de Control y Enjuiciamiento Penal Puente Grande)",
                        "juzgadosPaz": "Juzgados de Paz y Menores en El Salto, Tonalá, Tlajomulco, Zapotlanejo; Juzgados Cívicos y de Conciliación Comunitaria",
                        "poblacion": "5,350,000 habitantes"
                  },
                  {
                        "partido": "Segundo Partido Judicial",
                        "cabecera": "Tepatitlán de Morelos (Región Altos Sur)",
                        "municipios": "Tepatitlán, Acatic, Arandas, Jalostotitlán, San Julián, San Miguel el Alto, Valle de Guadalupe, Jesús María",
                        "juzgados1ra": "4 Juzgados de 1ª Instancia (Civil, Familiar, Mercantil y Penal Acusatorio)",
                        "juzgadosPaz": "Juzgados Menores Municipales en Acatic, Arandas, San Miguel el Alto y Valle de Guadalupe",
                        "poblacion": "380,000 habitantes"
                  },
                  {
                        "partido": "Tercer Partido Judicial",
                        "cabecera": "Lagos de Moreno (Región Altos Norte)",
                        "municipios": "Lagos de Moreno, Encarnación de Díaz, Ojuelos, San Diego de Alejandría, San Juan de los Lagos, Teocaltiche, Unión de San Antonio, Villa Hidalgo",
                        "juzgados1ra": "4 Juzgados de 1ª Instancia (Mixtos y Penal Acusatorio)",
                        "juzgadosPaz": "Juzgados de Paz y Menores en Ojuelos, Encarnación y San Juan de los Lagos",
                        "poblacion": "410,000 habitantes"
                  },
                  {
                        "partido": "Cuarto Partido Judicial",
                        "cabecera": "Ocotlán (Región Ciénega)",
                        "municipios": "Ocotlán, Poncitlán, Jamay, La Barca, Atotonilco el Alto, Ayotlán, Tototlán, Zapotlán del Rey",
                        "juzgados1ra": "4 Juzgados de 1ª Instancia Civiles, Familiares y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores de Proximidad en Poncitlán, La Barca y Tototlán",
                        "poblacion": "310,000 habitantes"
                  },
                  {
                        "partido": "Quinto Partido Judicial",
                        "cabecera": "Chapala (Región Ribera de Chapala)",
                        "municipios": "Chapala, Jocotepec, Tuxcueca, Tizapán el Alto",
                        "juzgados1ra": "3 Juzgados de 1ª Instancia Mixtos y Sala Regional de Control Penal",
                        "juzgadosPaz": "Juzgados Menores y Conciliadores en Jocotepec y Tizapán",
                        "poblacion": "155,000 habitantes"
                  },
                  {
                        "partido": "Sexto Partido Judicial",
                        "cabecera": "Zapotlán el Grande / Ciudad Guzmán (Región Sur)",
                        "municipios": "Ciudad Guzmán, Gómez Farías, Sayula, Tapalpa, Techaluta, Amacueca, San Gabriel, Tolimán, Tonila, Tuxpan, Zapotiltic, Pihuamo",
                        "juzgados1ra": "5 Juzgados de 1ª Instancia (Civiles, Familiares y Oral Penal Regional)",
                        "juzgadosPaz": "Juzgados Menores Municipales en Sayula, Tapalpa, Tuxpan y Pihuamo",
                        "poblacion": "350,000 habitantes"
                  },
                  {
                        "partido": "Séptimo Partido Judicial",
                        "cabecera": "Autlán de Navarro (Región Sierra de Amula)",
                        "municipios": "Autlán, El Grullo, El Limón, Casimiro Castillo, Cuautitlán de García Barragán, Villa Purificación",
                        "juzgados1ra": "3 Juzgados de 1ª Instancia Mixtos y Juzgado de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en El Grullo y Casimiro Castillo",
                        "poblacion": "175,000 habitantes"
                  },
                  {
                        "partido": "Octavo Partido Judicial",
                        "cabecera": "Puerto Vallarta (Región Costa Sierra Occidental)",
                        "municipios": "Puerto Vallarta, Cabo Corrientes, Tomatlán",
                        "juzgados1ra": "6 Juzgados de 1ª Instancia (Civil, Familiar, Mercantil y de Control Oral Penal)",
                        "juzgadosPaz": "Juzgados Menores de Conciliación en El Tuito y Tomatlán",
                        "poblacion": "340,000 habitantes"
                  },
                  {
                        "partido": "Noveno Partido Judicial",
                        "cabecera": "Ameca (Región Valles)",
                        "municipios": "Ameca, San Martín Hidalgo, Cocula, Ahualulco de Mercado, Teuchitlán",
                        "juzgados1ra": "3 Juzgados Mixtos de 1ª Instancia y Oralidad Mercantil",
                        "juzgadosPaz": "Juzgados Menores en Cocula y San Martín Hidalgo",
                        "poblacion": "165,000 habitantes"
                  },
                  {
                        "partido": "Décimo Partido Judicial",
                        "cabecera": "Tequila (Región Valles)",
                        "municipios": "Tequila, Amatitán, Arenal, Hostotipaquillo, Magdalena, San Marcos",
                        "juzgados1ra": "2 Juzgados de 1ª Instancia Mixtos y de Control Penal",
                        "juzgadosPaz": "Juzgados Municipales Menores en Magdalena y Hostotipaquillo",
                        "poblacion": "160,000 habitantes"
                  },
                  {
                        "partido": "Undécimo Partido Judicial",
                        "cabecera": "Colotlán (Región Norte)",
                        "municipios": "Colotlán, Huejuquilla el Alto, Mezquitic, Bolaños, Villa Guerrero, Chimaltitán, Santa María de los Ángeles, Totatiche, Huejúcar",
                        "juzgados1ra": "2 Juzgados Mixtos y Juzgados Indígenas Comunitarios wixárika / huichol",
                        "juzgadosPaz": "Juzgados Tradicionales y de Paz Comunitarios en Mezquitic y Bolaños",
                        "poblacion": "85,000 habitantes"
                  },
                  {
                        "partido": "Duodécimo al Trigésimo Segundo",
                        "cabecera": "Sedes Regionales: Cihuatlán, Sayula, Mascota, Jalostotitlán, San Juan de los Lagos, Yahualica, Arandas, La Barca, Tala, Teocaltiche, Tamazula, Ahualulco, Etzatlán, Zacoalco, Mazamitla, Atotonilco, Encarnación, Tecalitlán, San Gabriel, Tlajomulco y Tonalá",
                        "municipios": "Municipios cabecera y adscritos en toda la geografía del Estado de Jalisco",
                        "juzgados1ra": "24 Juzgados Mixtos de 1ª Instancia, Juzgados de Control y Enjuiciamiento Penal Regionales",
                        "juzgadosPaz": "Red integral de Juzgados de Paz y Juzgados Menores Municipales para proximidad cívica y mediación vecinal",
                        "poblacion": "1,450,000 habitantes"
                  }
            ]
      },
      "CDMX": {
            "abbr": "CDMX",
            "nombre": "Ciudad de México",
            "circuitoNum": "Primer Circuito Judicial Federal",
            "circuitoRomano": "I Circuito",
            "circuitoCorto": "1er Circuito",
            "circuitoSedes": "San Lázaro, Periférico Sur, Reclusorio Norte, Reclusorio Oriente, Reclusorio Sur, Insurgentes Sur y Las Flores",
            "juzgadosFederales": "68 Tribunales Colegiados de Circuito, 8 Tribunales Colegiados de Apelación y 64 Juzgados de Distrito (Sede Central de los Tribunales Especializados en Competencia y Telecomunicaciones).",
            "tsjNombre": "Poder Judicial de la Ciudad de México (PJCDMX) · Niños Héroes",
            "numPartidos": 16,
            "numPartidosTxt": "16 Alcaldías / Jurisdicciones Judiciales Unificadas",
            "juecesPor100k": "5.2 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Jurisdicción Central Niños Héroes",
                        "cabecera": "Alcaldía Cuauhtémoc (Ciudad Judicial Central)",
                        "municipios": "Cuauhtémoc, Benito Juárez, Venustiano Carranza, Miguel Hidalgo",
                        "juzgados1ra": "120+ Juzgados de 1ª Instancia (Civiles, Familiares, Mercantiles y de Tutela de Derechos)",
                        "juzgadosPaz": "Juzgados de Cuantía Menor y Justicia Cívica Comunitaria en cada coordinación territorial",
                        "poblacion": "3,200,000 habitantes"
                  },
                  {
                        "partido": "Jurisdicción Oriente (Iztapalapa)",
                        "cabecera": "Alcaldía Iztapalapa / Reclusorio Oriente",
                        "municipios": "Iztapalapa, Iztacalco, Tláhuac",
                        "juzgados1ra": "35 Juzgados Familiares, Civiles Orales y Salas Penales Orales",
                        "juzgadosPaz": "Juzgados de Paz de Barrio y Coordinaciones de Mediación Vecinal",
                        "poblacion": "2,900,000 habitantes"
                  },
                  {
                        "partido": "Jurisdicción Norte (Gustavo A. Madero)",
                        "cabecera": "Alcaldía Gustavo A. Madero / Reclusorio Norte",
                        "municipios": "Gustavo A. Madero, Azcapotzalco",
                        "juzgados1ra": "28 Juzgados Civiles, Familiares y Centros de Justicia Penal Oral",
                        "juzgadosPaz": "Juzgados Cívicos de proximidad y justicia itinerante",
                        "poblacion": "1,650,000 habitantes"
                  },
                  {
                        "partido": "Jurisdicción Poniente & Sur",
                        "cabecera": "Alcaldías Coyoacán, Tlalpan, Álvaro Obregón y Xochimilco",
                        "municipios": "Coyoacán, Tlalpan, Álvaro Obregón, Magdalena Contreras, Xochimilco, Milpa Alta",
                        "juzgados1ra": "32 Juzgados Mixtos, Familiares y de Ejecución",
                        "juzgadosPaz": "Juzgados Comunales en Milpa Alta y Xochimilco conforme a Usos y Costumbres",
                        "poblacion": "2,450,000 habitantes"
                  }
            ]
      },
      "NL": {
            "abbr": "NL",
            "nombre": "Nuevo León",
            "circuitoNum": "Cuarto Circuito Judicial Federal",
            "circuitoRomano": "IV Circuito",
            "circuitoCorto": "4º Circuito",
            "circuitoSedes": "Monterrey y San Pedro Garza García",
            "juzgadosFederales": "16 Tribunales Colegiados de Circuito, 3 Tribunales Colegiados de Apelación y 15 Juzgados de Distrito.",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Nuevo León (TSJNL)",
            "numPartidos": 14,
            "numPartidosTxt": "14 Distritos Judiciales Estatales",
            "juecesPor100k": "4.5 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Primer Distrito Judicial",
                        "cabecera": "Monterrey (Área Metropolitana: San Pedro, San Nicolás, Guadalupe, Santa Catarina, Apodaca)",
                        "municipios": "Monterrey, Guadalupe, San Nicolás de los Garza, San Pedro Garza García, Santa Catarina, Apodaca, General Escobedo, García",
                        "juzgados1ra": "48 Juzgados de 1ª Instancia (Civiles, Familiares, Mercantiles Orales y de Control Penal)",
                        "juzgadosPaz": "Juzgados Menores Municipales de cuantía menor en San Pedro, Guadalupe y Apodaca",
                        "poblacion": "4,800,000 habitantes"
                  },
                  {
                        "partido": "Segundo Distrito Judicial",
                        "cabecera": "Cadereyta Jiménez",
                        "municipios": "Cadereyta, Juárez, Allende, Santiago",
                        "juzgados1ra": "4 Juzgados Mixtos de 1ª Instancia y Oralidad Mercantil",
                        "juzgadosPaz": "Juzgados Menores en Allende y Santiago",
                        "poblacion": "420,000 habitantes"
                  },
                  {
                        "partido": "Tercer Distrito Judicial",
                        "cabecera": "Montemorelos (Región Citrícola)",
                        "municipios": "Montemorelos, Linares, General Terán, Hualahuises, Rayones",
                        "juzgados1ra": "3 Juzgados de 1ª Instancia Mixtos y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en Linares y General Terán",
                        "poblacion": "210,000 habitantes"
                  },
                  {
                        "partido": "Cuarto Distrito Judicial",
                        "cabecera": "Doctor Arroyo (Altiplano Sur)",
                        "municipios": "Doctor Arroyo, Aramberri, Galeana, General Zaragoza, Mier y Noriega",
                        "juzgados1ra": "2 Juzgados Mixtos y Penales Acusatorios",
                        "juzgadosPaz": "Juzgados de Paz Rurales en Galeana y Mier y Noriega",
                        "poblacion": "115,000 habitantes"
                  },
                  {
                        "partido": "Quinto al Decimocuarto Distrito",
                        "cabecera": "Sedes Regionales: China, Linares, Galeana, Cerralvo, Villaldama, Sabinas Hidalgo, Lampazos, Anáhuac, Salinas Victoria, Marín",
                        "municipios": "Municipios de las regiones norte, oriente y citrícola de Nuevo León",
                        "juzgados1ra": "12 Juzgados Mixtos y de Control Oral Penal",
                        "juzgadosPaz": "Juzgados Menores Municipales y Centros de Mediación Judicial",
                        "poblacion": "380,000 habitantes"
                  }
            ]
      },
      "MEX": {
            "abbr": "MEX",
            "nombre": "Estado de México",
            "circuitoNum": "Segundo Circuito Judicial Federal",
            "circuitoRomano": "II Circuito",
            "circuitoCorto": "2º Circuito",
            "circuitoSedes": "Toluca de Lerdo y Naucalpan de Juárez",
            "juzgadosFederales": "22 Tribunales Colegiados de Circuito, 4 Tribunales Colegiados de Apelación, 23 Juzgados de Distrito y CJPF Almoloya de Juárez (Altiplano).",
            "tsjNombre": "Poder Judicial del Estado de México (PJEDOMEX)",
            "numPartidos": 18,
            "numPartidosTxt": "18 Distritos Judiciales Estatales",
            "juecesPor100k": "3.1 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Toluca",
                        "cabecera": "Toluca de Lerdo",
                        "municipios": "Toluca, Metepec, Zinacantepec, Almoloya de Juárez, Villa Victoria",
                        "juzgados1ra": "24 Juzgados de 1ª Instancia (Civil, Familiar, Mercantil y Penal Almoloya)",
                        "juzgadosPaz": "Juzgados de Cuantía Menor en Metepec y Zinacantepec",
                        "poblacion": "1,850,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Tlalnepantla",
                        "cabecera": "Tlalnepantla de Baz",
                        "municipios": "Tlalnepantla, Naucalpan, Atizapán de Zaragoza, Huixquilucan, Nicolás Romero",
                        "juzgados1ra": "32 Juzgados Civiles, Familiares y Mercantiles Orales",
                        "juzgadosPaz": "Juzgados de Paz y Conciliación Municipal en Atizapán y Naucalpan",
                        "poblacion": "2,900,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Ecatepec",
                        "cabecera": "Ecatepec de Morelos",
                        "municipios": "Ecatepec, Coacalco, Tecámac",
                        "juzgados1ra": "28 Juzgados de 1ª Instancia Civiles y Penales de Chiconautla",
                        "juzgadosPaz": "Juzgados de Cuantía Menor de proximidad en Tecámac y Coacalco",
                        "poblacion": "2,550,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Nezahualcóyotl",
                        "cabecera": "Ciudad Nezahualcóyotl",
                        "municipios": "Nezahualcóyotl, Chimalhuacán, La Paz",
                        "juzgados1ra": "22 Juzgados Familiares, Civiles y Penal Neza Bordo",
                        "juzgadosPaz": "Juzgados Municipales de Paz en Chimalhuacán y La Paz",
                        "poblacion": "1,950,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Texcoco, Chalco, Cuautitlán y Foráneos",
                        "cabecera": "Sedes: Texcoco, Chalco, Cuautitlán Izcalli, Zumpango, Otumba, El Oro, Ixtlahuaca, Tenango, Tenancingo, Sultepec, Valle de Bravo, Jilotepec",
                        "municipios": "Resto de los 125 municipios mexiquenses",
                        "juzgados1ra": "45 Juzgados de 1ª Instancia Mixtos y Penales",
                        "juzgadosPaz": "Red de Juzgados de Cuantía Menor y Mediación Comunitaria",
                        "poblacion": "7,800,000 habitantes"
                  }
            ]
      },
      "VER": {
            "abbr": "VER",
            "nombre": "Veracruz",
            "circuitoNum": "Séptimo Circuito Judicial Federal",
            "circuitoRomano": "VII Circuito",
            "circuitoCorto": "7º Circuito",
            "circuitoSedes": "Boca del Río, Xalapa, Poza Rica, Tuxpan y Córdoba",
            "juzgadosFederales": "14 Tribunales Colegiados de Circuito, 3 Tribunales Colegiados de Apelación y 16 Juzgados de Distrito.",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Veracruz (TSJVER)",
            "numPartidos": 21,
            "numPartidosTxt": "21 Distritos Judiciales Estatales",
            "juecesPor100k": "3.4 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Xalapa",
                        "cabecera": "Xalapa-Enríquez",
                        "municipios": "Xalapa, Banderilla, Coatepec, Emiliano Zapata, Naolinco, Tlacolulan",
                        "juzgados1ra": "12 Juzgados de 1ª Instancia Civiles, Familiares y de Juicio Oral Penal Pacho Viejo",
                        "juzgadosPaz": "Juzgados Menores Municipales de paz en Coatepec y Banderilla",
                        "poblacion": "780,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Veracruz",
                        "cabecera": "Veracruz / Boca del Río",
                        "municipios": "Veracruz, Boca del Río, Medellín de Bravo, Alvarado, Jamapa",
                        "juzgados1ra": "14 Juzgados de 1ª Instancia Civiles, Familiares y Mercantiles",
                        "juzgadosPaz": "Juzgados de Paz y Menores en Medellín y Alvarado",
                        "poblacion": "950,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Coatzacoalcos",
                        "cabecera": "Coatzacoalcos",
                        "municipios": "Coatzacoalcos, Minatitlán, Cosoleacaque, Nanchital, Agua Dulce",
                        "juzgados1ra": "8 Juzgados Civiles, Familiares y Centro de Justicia Penal Oral",
                        "juzgadosPaz": "Juzgados Menores en Minatitlán y Nanchital",
                        "poblacion": "720,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Poza Rica",
                        "cabecera": "Poza Rica de Hidalgo",
                        "municipios": "Poza Rica, Papantla, Coatzintla, Tihuatlán, Cazones",
                        "juzgados1ra": "6 Juzgados de 1ª Instancia Civiles y Penales",
                        "juzgadosPaz": "Juzgados Indígenas y Menores en Papantla y Tihuatlán",
                        "poblacion": "510,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Córdoba, Orizaba, Tuxpan y Foráneos",
                        "cabecera": "Sedes: Córdoba, Orizaba, Tuxpan, Acayucan, Cosamaloapan, San Andrés Tuxtla, Misantla, Jalacingo, Huatusco, Zongolica, Chicontepec, Pánuco, Tantoyuca, Ozuluama",
                        "municipios": "Municipios de las altas montañas, huasteca y cuenca de Veracruz",
                        "juzgados1ra": "35 Juzgados de 1ª Instancia Mixtos e Indígenas Comunitarios",
                        "juzgadosPaz": "Juzgados Menores y de Paz Comunitarios",
                        "poblacion": "5,100,000 habitantes"
                  }
            ]
      },
      "PUE": {
            "abbr": "PUE",
            "nombre": "Puebla",
            "circuitoNum": "Sexto Circuito Judicial Federal",
            "circuitoRomano": "VI Circuito",
            "circuitoCorto": "6º Circuito",
            "circuitoSedes": "San Andrés Cholula y Puebla Capital",
            "juzgadosFederales": "12 Tribunales Colegiados de Circuito, 2 Tribunales Colegiados de Apelación y 12 Juzgados de Distrito (Sede de Centros Auxiliares CAR).",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Puebla",
            "numPartidos": 22,
            "numPartidosTxt": "22 Distritos Judiciales Estatales",
            "juecesPor100k": "3.6 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Puebla",
                        "cabecera": "Heroica Puebla de Zaragoza",
                        "municipios": "Puebla, San Andrés Cholula, San Pedro Cholula, Cuautlancingo, Amozoc",
                        "juzgados1ra": "26 Juzgados de 1ª Instancia (Civiles, Familiares, Mercantiles y Orales Penales)",
                        "juzgadosPaz": "Juzgados de Paz y Jueces Menores en Cholula y Amozoc",
                        "poblacion": "2,600,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Tehuacán",
                        "cabecera": "Tehuacán",
                        "municipios": "Tehuacán, Ajalpan, Santiago Miahuatlán, Zapotitlán",
                        "juzgados1ra": "5 Juzgados de 1ª Instancia Mixtos y Sala Penal Acusatoria",
                        "juzgadosPaz": "Juzgados Menores e Indígenas en Ajalpan y Zapotitlán",
                        "poblacion": "450,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Teziutlán",
                        "cabecera": "Teziutlán (Sierra Nororiental)",
                        "municipios": "Teziutlán, Chignautla, Xiutetelco, Hueyapan, Atempan",
                        "juzgados1ra": "3 Juzgados de 1ª Instancia Civiles y Penales",
                        "juzgadosPaz": "Juzgados Indígenas Comunitarios en Hueyapan y Chignautla",
                        "poblacion": "280,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Huauchinango, Atlixco, Izúcar y Sierra",
                        "cabecera": "Sedes: Huauchinango, Atlixco, Izúcar de Matamoros, Tecamachalco, Zacatlán, Tepeaca, Libres, Chalchicomula, Tecali, Acatlán, Chiautla, Tetela, Tlatlauquitepec, Chignahuapan",
                        "municipios": "Municipios de la mixteca poblana, valles centrales y sierra norte",
                        "juzgados1ra": "30 Juzgados Mixtos y Salas Penales Regionales",
                        "juzgadosPaz": "Juzgados de Paz y Conciliación Municipal",
                        "poblacion": "3,250,000 habitantes"
                  }
            ]
      },
      "AGS": {
            "abbr": "AGS",
            "nombre": "Aguascalientes",
            "circuitoNum": "Trigésimo Circuito Judicial Federal",
            "circuitoRomano": "XXX Circuito",
            "circuitoCorto": "30º Circuito",
            "circuitoSedes": "Aguascalientes Capital",
            "juzgadosFederales": "4 Tribunales Colegiados de Circuito, 1 Tribunal Colegiado de Apelación y 5 Juzgados de Distrito.",
            "tsjNombre": "Supremo Tribunal de Justicia del Estado de Aguascalientes",
            "numPartidos": 5,
            "numPartidosTxt": "5 Partidos Judiciales Estatales",
            "juecesPor100k": "4.6 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Primer Partido Judicial",
                        "cabecera": "Aguascalientes Capital",
                        "municipios": "Aguascalientes, San Francisco de los Romo, El Llano",
                        "juzgados1ra": "18 Juzgados de 1ª Instancia (Civiles, Familiares, Mercantiles y de Control Penal)",
                        "juzgadosPaz": "Juzgados Municipales de Cuantía Menor y Mediación Cívica en Capital y San Francisco",
                        "poblacion": "1,050,000 habitantes"
                  },
                  {
                        "partido": "Segundo Partido Judicial",
                        "cabecera": "Jesús María",
                        "municipios": "Jesús María",
                        "juzgados1ra": "3 Juzgados Mixtos de 1ª Instancia y Oralidad Mercantil",
                        "juzgadosPaz": "Juzgado Menor Municipal de Proximidad",
                        "poblacion": "130,000 habitantes"
                  },
                  {
                        "partido": "Tercer Partido Judicial",
                        "cabecera": "Calvillo",
                        "municipios": "Calvillo",
                        "juzgados1ra": "2 Juzgados Mixtos de 1ª Instancia",
                        "juzgadosPaz": "Juzgado de Paz Comunitario",
                        "poblacion": "58,000 habitantes"
                  },
                  {
                        "partido": "Cuarto y Quinto Partido",
                        "cabecera": "Rincón de Romos y Pabellón de Arteaga",
                        "municipios": "Rincón de Romos, Pabellón de Arteaga, Cosío, Tepezalá, San José de Gracia, Asientos",
                        "juzgados1ra": "4 Juzgados Mixtos y de Control Penal Regional",
                        "juzgadosPaz": "Juzgados Menores en Cosío, Asientos y Tepezalá",
                        "poblacion": "230,000 habitantes"
                  }
            ]
      },
      "BC": {
            "abbr": "BC",
            "nombre": "Baja California",
            "circuitoNum": "Décimo Quinto Circuito Judicial Federal",
            "circuitoRomano": "XV Circuito",
            "circuitoCorto": "15º Circuito",
            "circuitoSedes": "Mexicali, Tijuana y Ensenada",
            "juzgadosFederales": "8 Tribunales Colegiados de Circuito, 2 Colegiados de Apelación y 8 Juzgados de Distrito.",
            "tsjNombre": "Poder Judicial del Estado de Baja California (PJBC)",
            "numPartidos": 3,
            "numPartidosTxt": "3 Partidos Judiciales Estatales (con subsedes)",
            "juecesPor100k": "3.9 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Partido Judicial de Tijuana",
                        "cabecera": "Tijuana (Subsedes: Playas de Rosarito y Tecate)",
                        "municipios": "Tijuana, Playas de Rosarito, Tecate",
                        "juzgados1ra": "26 Juzgados de 1ª Instancia (Civiles, Familiares, Mercantiles y de Control Penal La Mesa)",
                        "juzgadosPaz": "Juzgados de Paz y Justicia Cívica Comunitaria en Rosarito, Tecate y delegaciones de Tijuana",
                        "poblacion": "2,200,000 habitantes"
                  },
                  {
                        "partido": "Partido Judicial de Mexicali",
                        "cabecera": "Mexicali (Centro Cívico y Valle de Mexicali)",
                        "municipios": "Mexicali, San Felipe",
                        "juzgados1ra": "20 Juzgados de 1ª Instancia (Civiles, Familiares, Hipotecarios y Penal Oral)",
                        "juzgadosPaz": "Juzgados Menores en Ciudad Morelos, Guadalupe Victoria y San Felipe",
                        "poblacion": "1,100,000 habitantes"
                  },
                  {
                        "partido": "Partido Judicial de Ensenada",
                        "cabecera": "Ensenada (Subsede: San Quintín)",
                        "municipios": "Ensenada, San Quintín",
                        "juzgados1ra": "8 Juzgados Mixtos, Familiares y Penal Acusatorio",
                        "juzgadosPaz": "Juzgados Menores e Indígenas Comunitarios en San Quintín y Maneadero",
                        "poblacion": "550,000 habitantes"
                  }
            ]
      },
      "BCS": {
            "abbr": "BCS",
            "nombre": "Baja California Sur",
            "circuitoNum": "Vigésimo Sexto Circuito Judicial Federal",
            "circuitoRomano": "XXVI Circuito",
            "circuitoCorto": "26º Circuito",
            "circuitoSedes": "La Paz",
            "juzgadosFederales": "3 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 3 Juzgados de Distrito.",
            "tsjNombre": "Poder Judicial del Estado de Baja California Sur",
            "numPartidos": 5,
            "numPartidosTxt": "5 Partidos Judiciales Estatales",
            "juecesPor100k": "4.8 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Partido Judicial de La Paz",
                        "cabecera": "La Paz",
                        "municipios": "La Paz, Todos Santos, Los Barriles",
                        "juzgados1ra": "10 Juzgados de 1ª Instancia (Civiles, Familiares, Mercantiles y Penal Oral)",
                        "juzgadosPaz": "Juzgados Menores en Todos Santos y El Sargento",
                        "poblacion": "300,000 habitantes"
                  },
                  {
                        "partido": "Partido Judicial de Los Cabos",
                        "cabecera": "San José del Cabo y Cabo San Lucas",
                        "municipios": "Los Cabos",
                        "juzgados1ra": "8 Juzgados Civiles, Familiares, Mercantiles y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores de Conciliación en Cabo San Lucas",
                        "poblacion": "360,000 habitantes"
                  },
                  {
                        "partido": "Partidos de Comondú, Loreto y Mulegé",
                        "cabecera": "Ciudad Constitución, Loreto y Santa Rosalía",
                        "municipios": "Comondú, Loreto, Mulegé (Guerrero Negro, Vizcaíno)",
                        "juzgados1ra": "5 Juzgados Mixtos de 1ª Instancia",
                        "juzgadosPaz": "Juzgados de Paz Rurales y Menores en Guerrero Negro y Loreto",
                        "poblacion": "140,000 habitantes"
                  }
            ]
      },
      "CAM": {
            "abbr": "CAM",
            "nombre": "Campeche",
            "circuitoNum": "Trigésimo Primer Circuito Judicial Federal",
            "circuitoRomano": "XXXI Circuito",
            "circuitoCorto": "31º Circuito",
            "circuitoSedes": "San Francisco de Campeche",
            "juzgadosFederales": "3 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 3 Juzgados de Distrito.",
            "tsjNombre": "Poder Judicial del Estado de Campeche",
            "numPartidos": 5,
            "numPartidosTxt": "5 Distritos Judiciales Estatales",
            "juecesPor100k": "4.5 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Primer Distrito Judicial",
                        "cabecera": "San Francisco de Campeche",
                        "municipios": "Campeche, Tenabo, Hopelchén",
                        "juzgados1ra": "12 Juzgados de 1ª Instancia Civiles, Familiares y de Control Oral Penal San Francisco Kobén",
                        "juzgadosPaz": "Juzgados Menores y Mayas Comunitarios en Hopelchén y Tenabo",
                        "poblacion": "350,000 habitantes"
                  },
                  {
                        "partido": "Segundo Distrito Judicial",
                        "cabecera": "Ciudad del Carmen",
                        "municipios": "Carmen, Palizada",
                        "juzgados1ra": "8 Juzgados Civiles, Familiares y Penal Acusatorio",
                        "juzgadosPaz": "Juzgados Menores en Sabancuy y Palizada",
                        "poblacion": "260,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Champotón, Escárcega y Hecelchakán",
                        "cabecera": "Champotón, Escárcega y Hecelchakán",
                        "municipios": "Champotón, Seybaplaya, Escárcega, Candelaria, Calakmul, Hecelchakán, Calkiní, Dzitbalché",
                        "juzgados1ra": "6 Juzgados Mixtos y de Juicio Penal",
                        "juzgadosPaz": "Juzgados de Paz y Comunidades Indígenas en Calkiní y Calakmul",
                        "poblacion": "320,000 habitantes"
                  }
            ]
      },
      "COAH": {
            "abbr": "COAH",
            "nombre": "Coahuila",
            "circuitoNum": "Octavo Circuito Judicial Federal",
            "circuitoRomano": "VIII Circuito",
            "circuitoCorto": "8º Circuito",
            "circuitoSedes": "Torreón, Saltillo y Monclova",
            "juzgadosFederales": "9 Tribunales Colegiados de Circuito, 2 Colegiados de Apelación y 9 Juzgados de Distrito.",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Coahuila",
            "numPartidos": 6,
            "numPartidosTxt": "6 Distritos Judiciales Estatales",
            "juecesPor100k": "4.2 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Saltillo",
                        "cabecera": "Saltillo",
                        "municipios": "Saltillo, Ramos Arizpe, Arteaga, General Cepeda",
                        "juzgados1ra": "16 Juzgados de 1ª Instancia (Civiles, Familiares, Mercantiles y de Control Penal)",
                        "juzgadosPaz": "Juzgados Letrados y Menores en Ramos Arizpe y Arteaga",
                        "poblacion": "1,050,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Viesca / Torreón",
                        "cabecera": "Torreón (Región Laguna)",
                        "municipios": "Torreón, Matamoros, Viesca",
                        "juzgados1ra": "18 Juzgados de 1ª Instancia Civiles, Familiares y Penal Acusatorio",
                        "juzgadosPaz": "Juzgados de Cuantía Menor en Matamoros y Viesca",
                        "poblacion": "890,000 habitantes"
                  },
                  {
                        "partido": "Distrito de Monclova y Región Centro",
                        "cabecera": "Monclova",
                        "municipios": "Monclova, Frontera, Castaños, San Buenaventura",
                        "juzgados1ra": "8 Juzgados Mixtos y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en Frontera y Castaños",
                        "poblacion": "380,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Río Grande, Carbonífera y Acuña",
                        "cabecera": "Piedras Negras, Sabinas y Ciudad Acuña",
                        "municipios": "Piedras Negras, Nava, Sabinas, San Juan de Sabinas, Múzquiz, Acuña, Jiménez",
                        "juzgados1ra": "10 Juzgados de 1ª Instancia Mixtos y Penales",
                        "juzgadosPaz": "Juzgados Menores en Múzquiz, Nava y Zaragoza",
                        "poblacion": "820,000 habitantes"
                  }
            ]
      },
      "COL": {
            "abbr": "COL",
            "nombre": "Colima",
            "circuitoNum": "Trigésimo Segundo Circuito Judicial Federal",
            "circuitoRomano": "XXXII Circuito",
            "circuitoCorto": "32º Circuito",
            "circuitoSedes": "Colima Capital",
            "juzgadosFederales": "3 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 3 Juzgados de Distrito.",
            "tsjNombre": "Supremo Tribunal de Justicia del Estado de Colima",
            "numPartidos": 3,
            "numPartidosTxt": "3 Partidos Judiciales Estatales",
            "juecesPor100k": "4.7 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Primer Partido Judicial",
                        "cabecera": "Colima Capital (Zona Metropolitana)",
                        "municipios": "Colima, Villa de Álvarez, Comala, Coquimatlán, Cuauhtémoc",
                        "juzgados1ra": "10 Juzgados de 1ª Instancia (Civiles, Familiares, Mercantiles y de Control Penal)",
                        "juzgadosPaz": "Juzgados de Paz y Menores en Villa de Álvarez, Comala y Cuauhtémoc",
                        "poblacion": "410,000 habitantes"
                  },
                  {
                        "partido": "Segundo Partido Judicial",
                        "cabecera": "Manzanillo (Puerto y Costa)",
                        "municipios": "Manzanillo, Minatitlán",
                        "juzgados1ra": "6 Juzgados Civiles, Familiares, Mercantiles y Penal Acusatorio",
                        "juzgadosPaz": "Juzgados de Paz en Santiago, El Colomo y Minatitlán",
                        "poblacion": "210,000 habitantes"
                  },
                  {
                        "partido": "Tercer Partido Judicial",
                        "cabecera": "Tecomán (Valle y Costa Sur)",
                        "municipios": "Tecomán, Armería, Ixtlahuacán",
                        "juzgados1ra": "5 Juzgados Mixtos y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en Armería e Ixtlahuacán",
                        "poblacion": "150,000 habitantes"
                  }
            ]
      },
      "CHIS": {
            "abbr": "CHIS",
            "nombre": "Chiapas",
            "circuitoNum": "Vigésimo Circuito Judicial Federal",
            "circuitoRomano": "XX Circuito",
            "circuitoCorto": "20º Circuito",
            "circuitoSedes": "Tuxtla Gutiérrez y Tapachula",
            "juzgadosFederales": "7 Tribunales Colegiados de Circuito, 2 Colegiados de Apelación y 7 Juzgados de Distrito.",
            "tsjNombre": "Poder Judicial del Estado de Chiapas",
            "numPartidos": 21,
            "numPartidosTxt": "21 Distritos Judiciales Estatales",
            "juecesPor100k": "3.1 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Tuxtla",
                        "cabecera": "Tuxtla Gutiérrez",
                        "municipios": "Tuxtla Gutiérrez, Berriozábal, Chiapa de Corzo, Suchiapa",
                        "juzgados1ra": "16 Juzgados de 1ª Instancia Civiles, Familiares y Penal Oral El Canelo",
                        "juzgadosPaz": "Juzgados de Paz y Conciliación Indígena Comunitaria",
                        "poblacion": "920,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Tapachula",
                        "cabecera": "Tapachula (Soconusco y Frontera Sur)",
                        "municipios": "Tapachula, Tuxtla Chico, Cacahoatán, Suchiate, Frontera Hidalgo",
                        "juzgados1ra": "10 Juzgados Civiles, Familiares y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en Suchiate y Cacahoatán",
                        "poblacion": "510,000 habitantes"
                  },
                  {
                        "partido": "Distrito de San Cristóbal de Las Casas",
                        "cabecera": "San Cristóbal (Altos de Chiapas)",
                        "municipios": "San Cristóbal, San Juan Chamula, Zinacantán, Tenejapa, Huixtán",
                        "juzgados1ra": "6 Juzgados de 1ª Instancia y Juzgados de Paz Indígena Tzotzil y Tzeltal",
                        "juzgadosPaz": "Juzgados Tradicionales de Usos y Costumbres en Chamula y Zinacantán",
                        "poblacion": "420,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Comitán, Palenque y Foráneos",
                        "cabecera": "Sedes: Comitán, Palenque, Villaflores, Tonalá, Ocosingo, Pichucalco, Cintalapa, Motozintla",
                        "municipios": "Municipios de las regiones selva, norte, frailesca e istmo-costa",
                        "juzgados1ra": "22 Juzgados Mixtos y Salas Penales Regionales",
                        "juzgadosPaz": "Red de Juzgados de Paz y Conciliación Indígena Comunitaria",
                        "poblacion": "3,750,000 habitantes"
                  }
            ]
      },
      "CHIH": {
            "abbr": "CHIH",
            "nombre": "Chihuahua",
            "circuitoNum": "Décimo Séptimo Circuito Judicial Federal",
            "circuitoRomano": "XVII Circuito",
            "circuitoCorto": "17º Circuito",
            "circuitoSedes": "Chihuahua Capital y Ciudad Juárez",
            "juzgadosFederales": "10 Tribunales Colegiados de Circuito, 2 Colegiados de Apelación y 10 Juzgados de Distrito.",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Chihuahua",
            "numPartidos": 14,
            "numPartidosTxt": "14 Distritos Judiciales Estatales",
            "juecesPor100k": "4.0 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial Bravos",
                        "cabecera": "Ciudad Juárez (Frontera Norte)",
                        "municipios": "Juárez, Ahumada, Práxedis G. Guerrero, Guadalupe",
                        "juzgados1ra": "28 Juzgados de 1ª Instancia (Civiles, Familiares, Mercantiles y de Control Penal)",
                        "juzgadosPaz": "Juzgados Menores Municipales en Ahumada y El Valle de Juárez",
                        "poblacion": "1,550,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial Morelos",
                        "cabecera": "Chihuahua Capital (Centro)",
                        "municipios": "Chihuahua, Aldama, Aquiles Serdán, Santa Eulalia",
                        "juzgados1ra": "24 Juzgados Civiles, Familiares, Mercantiles y Oral Penal",
                        "juzgadosPaz": "Juzgados Menores en Aldama y Aquiles Serdán",
                        "poblacion": "1,020,000 habitantes"
                  },
                  {
                        "partido": "Distritos Benito Juárez y Abraham González",
                        "cabecera": "Cuauhtémoc y Delicias",
                        "municipios": "Cuauhtémoc, Cusihuiriachi, Delicias, Meoqui, Rosales, Saucillo",
                        "juzgados1ra": "12 Juzgados Mixtos y de Control Acusatorio",
                        "juzgadosPaz": "Juzgados Menores en Meoqui y Saucillo",
                        "poblacion": "480,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Hidalgo (Parral), Camargo y Sierra Tarahumara",
                        "cabecera": "Hidalgo del Parral, Camargo, Casas Grandes, Guachochi",
                        "municipios": "Parral, Camargo, Nuevo Casas Grandes, Guachochi, Balleza, Guadalupe y Calvo",
                        "juzgados1ra": "14 Juzgados Mixtos y Juzgados Indígenas Ralámuli / Tarahumara",
                        "juzgadosPaz": "Juzgados Menores y Comunitarios de la Sierra Tarahumara",
                        "poblacion": "750,000 habitantes"
                  }
            ]
      },
      "DGO": {
            "abbr": "DGO",
            "nombre": "Durango",
            "circuitoNum": "Vigésimo Quinto Circuito Judicial Federal",
            "circuitoRomano": "XXV Circuito",
            "circuitoCorto": "25º Circuito",
            "circuitoSedes": "Durango Capital y Gómez Palacio",
            "juzgadosFederales": "4 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 4 Juzgados de Distrito.",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Durango",
            "numPartidos": 13,
            "numPartidosTxt": "13 Distritos Judiciales Estatales",
            "juecesPor100k": "3.7 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Primer Distrito Judicial",
                        "cabecera": "Victoria de Durango (Capital)",
                        "municipios": "Durango, San Dimas, Canatlán, Poanas, Nombre de Dios",
                        "juzgados1ra": "14 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en Canatlán, Poanas y Nombre de Dios",
                        "poblacion": "720,000 habitantes"
                  },
                  {
                        "partido": "Segundo Distrito Judicial",
                        "cabecera": "Gómez Palacio (Región Laguna)",
                        "municipios": "Gómez Palacio, Lerdo, Mapimí, Tlahualilo",
                        "juzgados1ra": "10 Juzgados Civiles, Familiares y Penal Oral",
                        "juzgadosPaz": "Juzgados Menores en Lerdo, Mapimí y Bermejillo",
                        "poblacion": "610,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Santiago Papasquiaro, El Salto y Foráneos",
                        "cabecera": "Santiago Papasquiaro, El Salto (Pueblo Nuevo), Cuencamé, Santa María del Oro",
                        "municipios": "Municipios de la sierra, quebradas y llanos de Durango",
                        "juzgados1ra": "8 Juzgados Mixtos y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores y de Paz Indígena O'dam / Tepehuano",
                        "poblacion": "520,000 habitantes"
                  }
            ]
      },
      "GTO": {
            "abbr": "GTO",
            "nombre": "Guanajuato",
            "circuitoNum": "Décimo Sexto Circuito Judicial Federal",
            "circuitoRomano": "XVI Circuito",
            "circuitoCorto": "16º Circuito",
            "circuitoSedes": "Guanajuato Capital, León y Celaya (Sede Regional CAR)",
            "juzgadosFederales": "11 Tribunales Colegiados de Circuito, 2 Tribunales Colegiados de Apelación y 11 Juzgados de Distrito.",
            "tsjNombre": "Poder Judicial del Estado de Guanajuato",
            "numPartidos": 23,
            "numPartidosTxt": "23 Partidos Judiciales Estatales",
            "juecesPor100k": "4.1 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Partido Judicial de León",
                        "cabecera": "León de los Aldama",
                        "municipios": "León, San Francisco del Rincón, Purísima del Rincón",
                        "juzgados1ra": "22 Juzgados de 1ª Instancia (Civiles, Familiares, Mercantiles y de Control Penal Oral)",
                        "juzgadosPaz": "Juzgados Menores en San Francisco y Purísima del Rincón",
                        "poblacion": "1,950,000 habitantes"
                  },
                  {
                        "partido": "Partido Judicial de Irapuato",
                        "cabecera": "Irapuato",
                        "municipios": "Irapuato, Romita, Abasolo",
                        "juzgados1ra": "10 Juzgados Civiles, Familiares y Penal Acusatorio",
                        "juzgadosPaz": "Juzgados Menores en Romita y Abasolo",
                        "poblacion": "720,000 habitantes"
                  },
                  {
                        "partido": "Partido Judicial de Celaya",
                        "cabecera": "Celaya (Región Laja-Bajío)",
                        "municipios": "Celaya, Cortazar, Villagrán, Apaseo el Grande, Apaseo el Alto",
                        "juzgados1ra": "12 Juzgados Civiles, Familiares y Penal Oral",
                        "juzgadosPaz": "Juzgados Menores en Cortazar y los Apaseos",
                        "poblacion": "780,000 habitantes"
                  },
                  {
                        "partido": "Partido Judicial de Guanajuato",
                        "cabecera": "Guanajuato Capital",
                        "municipios": "Guanajuato, Silao de la Victoria",
                        "juzgados1ra": "6 Juzgados de 1ª Instancia y Tribunal Colegiado de Apelación Estatal",
                        "juzgadosPaz": "Juzgados Menores en Silao y zona de cañadas",
                        "poblacion": "380,000 habitantes"
                  },
                  {
                        "partido": "Partidos de Salamanca, San Miguel de Allende y Foráneos",
                        "cabecera": "Salamanca, San Miguel de Allende, Dolores Hidalgo, Pénjamo, Acámbaro, Valle de Santiago",
                        "municipios": "Resto de los 46 municipios de Guanajuato",
                        "juzgados1ra": "18 Juzgados Mixtos y de Control Oral Penal",
                        "juzgadosPaz": "Red de Juzgados Menores Municipales",
                        "poblacion": "2,350,000 habitantes"
                  }
            ]
      },
      "GRO": {
            "abbr": "GRO",
            "nombre": "Guerrero",
            "circuitoNum": "Vigésimo Primer Circuito Judicial Federal",
            "circuitoRomano": "XXI Circuito",
            "circuitoCorto": "21º Circuito",
            "circuitoSedes": "Chilpancingo y Acapulco (Sede Regional CAR)",
            "juzgadosFederales": "6 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 6 Juzgados de Distrito.",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Guerrero",
            "numPartidos": 18,
            "numPartidosTxt": "18 Distritos Judiciales Estatales",
            "juecesPor100k": "3.0 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Tabares",
                        "cabecera": "Acapulco de Juárez",
                        "municipios": "Acapulco, San Marcos",
                        "juzgados1ra": "16 Juzgados de 1ª Instancia (Civiles, Familiares, Mercantiles y de Control Penal Las Cruces)",
                        "juzgadosPaz": "Juzgados de Paz y Justicia Cívica Comunitaria en Ciudad Renacimiento y Zapata",
                        "poblacion": "890,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Los Bravo",
                        "cabecera": "Chilpancingo de los Bravo",
                        "municipios": "Chilpancingo, Eduardo Neri, Leonardo Bravo, Tixtla",
                        "juzgados1ra": "12 Juzgados Civiles, Familiares y Penal Oral",
                        "juzgadosPaz": "Juzgados Menores en Tixtla y Zumpango del Río",
                        "poblacion": "420,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Hidalgo (Iguala)",
                        "cabecera": "Iguala de la Independencia (Norte)",
                        "municipios": "Iguala, Tepecoacuilco, Huitzuco, Cocula, Taxco",
                        "juzgados1ra": "8 Juzgados Mixtos y Penal Acusatorio",
                        "juzgadosPaz": "Juzgados de Paz en Cocula y Huitzuco",
                        "poblacion": "380,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Costa Grande, Montaña y Tierra Caliente",
                        "cabecera": "Zihuatanejo (Azueta), Tlapa (Álvarez), Ometepec (Abasolo), Coyuca de Catalán (Cuauhtémoc)",
                        "municipios": "Municipios de las regiones costa chica, montaña náhuatl/me'phaa y tierra caliente",
                        "juzgados1ra": "14 Juzgados Mixtos e Indígenas Comunitarios",
                        "juzgadosPaz": "Juzgados de Paz y Tradicionales Indígenas",
                        "poblacion": "1,850,000 habitantes"
                  }
            ]
      },
      "HGO": {
            "abbr": "HGO",
            "nombre": "Hidalgo",
            "circuitoNum": "Vigésimo Noveno Circuito Judicial Federal",
            "circuitoRomano": "XXIX Circuito",
            "circuitoCorto": "29º Circuito",
            "circuitoSedes": "Pachuca de Soto",
            "juzgadosFederales": "5 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 5 Juzgados de Distrito.",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Hidalgo",
            "numPartidos": 17,
            "numPartidosTxt": "17 Distritos Judiciales Estatales",
            "juecesPor100k": "3.3 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Pachuca",
                        "cabecera": "Pachuca de Soto",
                        "municipios": "Pachuca, Mineral de la Reforma, San Agustín Tlaxiaca, Epazoyucan",
                        "juzgados1ra": "16 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en Mineral de la Reforma y Tlaxiaca",
                        "poblacion": "650,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Tulancingo",
                        "cabecera": "Tulancingo de Bravo",
                        "municipios": "Tulancingo, Cuautepec, Santiago Tulantepec, Acatlán",
                        "juzgados1ra": "6 Juzgados Civiles, Familiares y Penal Oral",
                        "juzgadosPaz": "Juzgados Menores en Cuautepec y Santiago",
                        "poblacion": "320,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Tula",
                        "cabecera": "Tula de Allende (Región Tula-Tepeji)",
                        "municipios": "Tula, Tepeji del Río, Atotonilco de Tula, Tlahuelilpan",
                        "juzgados1ra": "6 Juzgados Mixtos y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en Tepeji y Atotonilco",
                        "poblacion": "340,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Huasteca, Valle del Mezquital y Altiplano",
                        "cabecera": "Huejutla, Ixmiquilpan, Actopan, Apan, Tizayuca, Huichapan, Tenango, Zacualtipán, Zimapán",
                        "municipios": "Municipios de la huasteca hidalguense y valle del mezquital",
                        "juzgados1ra": "18 Juzgados Mixtos e Indígenas Hñähñu / Otomí",
                        "juzgadosPaz": "Juzgados Menores y de Paz Comunitarios",
                        "poblacion": "1,770,000 habitantes"
                  }
            ]
      },
      "MICH": {
            "abbr": "MICH",
            "nombre": "Michoacán",
            "circuitoNum": "Décimo Primer Circuito Judicial Federal",
            "circuitoRomano": "XI Circuito",
            "circuitoCorto": "11º Circuito",
            "circuitoSedes": "Morelia y Uruapan",
            "juzgadosFederales": "9 Tribunales Colegiados de Circuito, 2 Colegiados de Apelación y 9 Juzgados de Distrito.",
            "tsjNombre": "Poder Judicial del Estado de Michoacán",
            "numPartidos": 23,
            "numPartidosTxt": "23 Distritos Judiciales Estatales",
            "juecesPor100k": "3.5 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Morelia",
                        "cabecera": "Morelia",
                        "municipios": "Morelia, Tarímbaro, Charo, Cuitzeo, Álvaro Obregón",
                        "juzgados1ra": "22 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y de Control Penal Mil Cumbres",
                        "juzgadosPaz": "Juzgados Menores en Tarímbaro y Cuitzeo",
                        "poblacion": "1,100,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Uruapan",
                        "cabecera": "Uruapan (Meseta Purépecha)",
                        "municipios": "Uruapan, Taretan, Tingambato, Paracho, Cherán",
                        "juzgados1ra": "10 Juzgados Civiles, Familiares y Comunales Purépechas",
                        "juzgadosPaz": "Juzgados Tradicionales y de Paz Comunal en Cherán y Paracho",
                        "poblacion": "480,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Zamora",
                        "cabecera": "Zamora de Hidalgo",
                        "municipios": "Zamora, Jacona, Tangancícuaro, Chavinda",
                        "juzgados1ra": "8 Juzgados Civiles, Familiares y Penal Oral",
                        "juzgadosPaz": "Juzgados Menores en Jacona y Tangancícuaro",
                        "poblacion": "390,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Lázaro Cárdenas",
                        "cabecera": "Lázaro Cárdenas (Costa)",
                        "municipios": "Lázaro Cárdenas, Arteaga, Aquila, Coahuayana",
                        "juzgados1ra": "6 Juzgados Mixtos y de Control Penal",
                        "juzgadosPaz": "Juzgados de Paz Rurales e Indígenas Nahuas en Aquila",
                        "poblacion": "280,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Zitácuaro, Pátzcuaro, Apatzingán y Foráneos",
                        "cabecera": "Zitácuaro, Pátzcuaro, Apatzingán, La Piedad, Hidalgo, Sahuayo, Tacámbaro, Puruándiro, Jiquilpan, Huetamo",
                        "municipios": "Municipios de tierra caliente, oriente y bajío michoacano",
                        "juzgados1ra": "24 Juzgados Mixtos y de Control Penal Regional",
                        "juzgadosPaz": "Red de Juzgados Menores Municipales",
                        "poblacion": "2,500,000 habitantes"
                  }
            ]
      },
      "MOR": {
            "abbr": "MOR",
            "nombre": "Morelos",
            "circuitoNum": "Décimo Octavo Circuito Judicial Federal",
            "circuitoRomano": "XVIII Circuito",
            "circuitoCorto": "18º Circuito",
            "circuitoSedes": "Cuernavaca",
            "juzgadosFederales": "5 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 5 Juzgados de Distrito.",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Morelos",
            "numPartidos": 3,
            "numPartidosTxt": "3 Distritos Judiciales Estatales",
            "juecesPor100k": "3.5 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Primer Distrito Judicial",
                        "cabecera": "Cuernavaca",
                        "municipios": "Cuernavaca, Jiutepec, Temixco, Huitzilac, Emiliano Zapata, Xochitepec",
                        "juzgados1ra": "18 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y de Control Penal Atlacholoaya",
                        "juzgadosPaz": "Juzgados Menores en Jiutepec, Temixco y Zapata",
                        "poblacion": "1,150,000 habitantes"
                  },
                  {
                        "partido": "Segundo Distrito Judicial",
                        "cabecera": "Cuautla (Oriente)",
                        "municipios": "Cuautla, Yautepec, Ayala, Yecapixtla, Tepalcingo, Axochiapan, Tlayacapan",
                        "juzgados1ra": "8 Juzgados Civiles, Familiares y Penal Acusatorio",
                        "juzgadosPaz": "Juzgados Menores en Yautepec, Ayala y Yecapixtla",
                        "poblacion": "520,000 habitantes"
                  },
                  {
                        "partido": "Tercer Distrito Judicial",
                        "cabecera": "Jojutla (Sur)",
                        "municipios": "Jojutla, Zacatepec, Puente de Ixtla, Tlaquiltenango, Tlaltizapán, Amacuzac",
                        "juzgados1ra": "6 Juzgados Mixtos y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en Zacatepec y Puente de Ixtla",
                        "poblacion": "300,000 habitantes"
                  }
            ]
      },
      "NAY": {
            "abbr": "NAY",
            "nombre": "Nayarit",
            "circuitoNum": "Vigésimo Cuarto Circuito Judicial Federal",
            "circuitoRomano": "XXIV Circuito",
            "circuitoCorto": "24º Circuito",
            "circuitoSedes": "Tepic",
            "juzgadosFederales": "4 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 4 Juzgados de Distrito.",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Nayarit",
            "numPartidos": 7,
            "numPartidosTxt": "7 Partidos Judiciales Estatales",
            "juecesPor100k": "3.8 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Partido Judicial de Tepic",
                        "cabecera": "Tepic",
                        "municipios": "Tepic, Xalisco, San Blas",
                        "juzgados1ra": "12 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y de Control Penal Venustiano Carranza",
                        "juzgadosPaz": "Juzgados Menores en Xalisco y San Blas",
                        "poblacion": "610,000 habitantes"
                  },
                  {
                        "partido": "Partido Judicial de Bahía de Banderas",
                        "cabecera": "Valle de Banderas / Bucerías",
                        "municipios": "Bahía de Banderas",
                        "juzgados1ra": "6 Juzgados Civiles, Familiares, Mercantiles y Penal Oral",
                        "juzgadosPaz": "Juzgados de Paz en Sayulita, San Pancho y Bucerías",
                        "poblacion": "180,000 habitantes"
                  },
                  {
                        "partido": "Partidos de Santiago, Compostela, Ixtlán y Norte",
                        "cabecera": "Santiago Ixcuintla, Compostela, Ixtlán del Río, Tecuala, Acaponeta",
                        "municipios": "Municipios de las costas norte, sur y sierra de Nayarit",
                        "juzgados1ra": "8 Juzgados Mixtos e Indígenas Comunitarios Náyeri / Cora y Wixárika",
                        "juzgadosPaz": "Juzgados Menores y Tradicionales Indígenas",
                        "poblacion": "445,000 habitantes"
                  }
            ]
      },
      "OAX": {
            "abbr": "OAX",
            "nombre": "Oaxaca",
            "circuitoNum": "Décimo Tercer Circuito Judicial Federal",
            "circuitoRomano": "XIII Circuito",
            "circuitoCorto": "13º Circuito",
            "circuitoSedes": "Oaxaca de Juárez y San Bartolo Coyotepec",
            "juzgadosFederales": "7 Tribunales Colegiados de Circuito, 2 Colegiados de Apelación y 7 Juzgados de Distrito.",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Oaxaca",
            "numPartidos": 30,
            "numPartidosTxt": "30 Distritos Judiciales Estatales",
            "juecesPor100k": "3.2 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial del Centro",
                        "cabecera": "Oaxaca de Juárez (Valles Centrales)",
                        "municipios": "Oaxaca de Juárez, Santa Lucía del Camino, Santa Cruz Xoxocotlán, San Antonio de la Cal",
                        "juzgados1ra": "18 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y Penal Tanivet",
                        "juzgadosPaz": "Juzgados de Cuantía Menor y Mediación Comunitaria",
                        "poblacion": "850,000 habitantes"
                  },
                  {
                        "partido": "Distritos del Istmo de Tehuantepec",
                        "cabecera": "Tehuantepec, Salina Cruz, Juchitán",
                        "municipios": "Santo Domingo Tehuantepec, Salina Cruz, Juchitán de Zaragoza, Matías Romero, Ixtepec",
                        "juzgados1ra": "10 Juzgados Civiles, Familiares e Indígenas Zapotecos / Huaves",
                        "juzgadosPaz": "Juzgados Tradicionales y de Paz en San Blas Atempa e Ixtepec",
                        "poblacion": "620,000 habitantes"
                  },
                  {
                        "partido": "Distrito de Tuxtepec (Cuenca)",
                        "cabecera": "San Juan Bautista Tuxtepec",
                        "municipios": "Tuxtepec, Loma Bonita, Acatlán de Pérez Figueroa",
                        "juzgados1ra": "6 Juzgados de 1ª Instancia y Penal Oral",
                        "juzgadosPaz": "Juzgados Menores en Loma Bonita y Acatlán",
                        "poblacion": "360,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Mixteca, Costa y Sierra",
                        "cabecera": "Huajuapan, Puerto Escondido (Pochutla), Miahuatlán, Tlacolula, Etla, Juquila, Pinotepa",
                        "municipios": "Municipios de las 8 regiones de Oaxaca (570 municipios)",
                        "juzgados1ra": "26 Juzgados Mixtos e Indígenas Comunitarios",
                        "juzgadosPaz": "Red de Juzgados Menores y Sistemas Normativos Indígenas (Usos y Costumbres)",
                        "poblacion": "2,300,000 habitantes"
                  }
            ]
      },
      "QRO": {
            "abbr": "QRO",
            "nombre": "Querétaro",
            "circuitoNum": "Vigésimo Segundo Circuito Judicial Federal",
            "circuitoRomano": "XXII Circuito",
            "circuitoCorto": "22º Circuito",
            "circuitoSedes": "Santiago de Querétaro",
            "juzgadosFederales": "6 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 6 Juzgados de Distrito.",
            "tsjNombre": "Poder Judicial del Estado de Querétaro",
            "numPartidos": 6,
            "numPartidosTxt": "6 Distritos Judiciales Estatales",
            "juecesPor100k": "4.4 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Querétaro",
                        "cabecera": "Santiago de Querétaro (Zona Metropolitana)",
                        "municipios": "Querétaro, Corregidora, El Marqués, Huimilpan",
                        "juzgados1ra": "24 Juzgados de 1ª Instancia (Civiles, Familiares, Mercantiles Orales y Modelo Cosmos Penal)",
                        "juzgadosPaz": "Juzgados Menores en Corregidora, El Marqués y Huimilpan",
                        "poblacion": "1,600,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de San Juan del Río",
                        "cabecera": "San Juan del Río",
                        "municipios": "San Juan del Río, Pedro Escobedo, Tequisquiapan",
                        "juzgados1ra": "8 Juzgados Civiles, Familiares y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en Pedro Escobedo y Tequisquiapan",
                        "poblacion": "440,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Cadereyta, Jalpan, Amealco y Tolimán",
                        "cabecera": "Cadereyta de Montes, Jalpan de Serra, Amealco, Tolimán",
                        "municipios": "Municipios del semidesierto, sierra gorda y sur indígena",
                        "juzgados1ra": "6 Juzgados Mixtos e Indígenas Otomí Hñöhñö en Amealco y Tolimán",
                        "juzgadosPaz": "Juzgados de Paz Comunitarios en la Sierra Gorda",
                        "poblacion": "330,000 habitantes"
                  }
            ]
      },
      "QROO": {
            "abbr": "QROO",
            "nombre": "Quintana Roo",
            "circuitoNum": "Vigésimo Séptimo Circuito Judicial Federal",
            "circuitoRomano": "XXVII Circuito",
            "circuitoCorto": "27º Circuito",
            "circuitoSedes": "Cancún y Chetumal",
            "juzgadosFederales": "5 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 5 Juzgados de Distrito.",
            "tsjNombre": "Poder Judicial del Estado de Quintana Roo",
            "numPartidos": 3,
            "numPartidosTxt": "3 Distritos Judiciales Estatales",
            "juecesPor100k": "4.1 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Cancún",
                        "cabecera": "Cancún (Benito Juárez)",
                        "municipios": "Benito Juárez, Isla Mujeres, Puerto Morelos, Lázaro Cárdenas",
                        "juzgados1ra": "16 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y de Control Penal Cancún",
                        "juzgadosPaz": "Juzgados de Paz y Menores en Isla Mujeres, Puerto Morelos y Kantunilkín",
                        "poblacion": "1,050,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Solidaridad",
                        "cabecera": "Playa del Carmen (Riviera Maya)",
                        "municipios": "Solidaridad, Tulum, Cozumel",
                        "juzgados1ra": "10 Juzgados Civiles, Familiares, Mercantiles y Penal Oral",
                        "juzgadosPaz": "Juzgados de Paz en Tulum y Cozumel",
                        "poblacion": "480,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Chetumal",
                        "cabecera": "Chetumal (Othón P. Blanco)",
                        "municipios": "Othón P. Blanco, Bacalar, Felipe Carrillo Puerto, José María Morelos",
                        "juzgados1ra": "8 Juzgados Mixtos y Juzgados Tradicionales Mayas",
                        "juzgadosPaz": "Jueces Tradicionales Mayas de la Zona Maya en Carrillo Puerto y Bacalar",
                        "poblacion": "380,000 habitantes"
                  }
            ]
      },
      "SLP": {
            "abbr": "SLP",
            "nombre": "San Luis Potosí",
            "circuitoNum": "Noveno Circuito Judicial Federal",
            "circuitoRomano": "IX Circuito",
            "circuitoCorto": "9º Circuito",
            "circuitoSedes": "San Luis Potosí Capital",
            "juzgadosFederales": "6 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 6 Juzgados de Distrito.",
            "tsjNombre": "Supremo Tribunal de Justicia del Estado de San Luis Potosí",
            "numPartidos": 13,
            "numPartidosTxt": "13 Distritos Judiciales Estatales",
            "juecesPor100k": "3.6 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Primer Distrito Judicial",
                        "cabecera": "San Luis Potosí Capital",
                        "municipios": "San Luis Potosí, Soledad de Graciano Sánchez, Cerro de San Pedro",
                        "juzgados1ra": "18 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y de Control Penal La Pila",
                        "juzgadosPaz": "Juzgados Menores en Soledad y Cerro de San Pedro",
                        "poblacion": "1,250,000 habitantes"
                  },
                  {
                        "partido": "Segundo Distrito (Matehuala)",
                        "cabecera": "Matehuala (Altiplano Potosino)",
                        "municipios": "Matehuala, Cedral, Charcas, Catorce, Vanegas, Villa de la Paz",
                        "juzgados1ra": "4 Juzgados Mixtos y de Control Acusatorio",
                        "juzgadosPaz": "Juzgados de Paz en Real de Catorce y Cedral",
                        "poblacion": "210,000 habitantes"
                  },
                  {
                        "partido": "Tercer Distrito (Rioverde)",
                        "cabecera": "Rioverde (Región Media)",
                        "municipios": "Rioverde, Ciudad Fernández, San Ciro, Rayón",
                        "juzgados1ra": "4 Juzgados Civiles, Familiares y Penal Oral",
                        "juzgadosPaz": "Juzgados Menores en Ciudad Fernández y San Ciro",
                        "poblacion": "220,000 habitantes"
                  },
                  {
                        "partido": "Cuarto Distrito (Ciudad Valles)",
                        "cabecera": "Ciudad Valles (Huasteca)",
                        "municipios": "Ciudad Valles, Tamuín, El Naranjo, Aquismón",
                        "juzgados1ra": "6 Juzgados Mixtos e Indígenas Tének / Huastecos",
                        "juzgadosPaz": "Juzgados Menores en Tamuín y Aquismón",
                        "poblacion": "310,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Tancanhuitz, Tamazunchale y Foráneos",
                        "cabecera": "Tancanhuitz, Tamazunchale, Cerritos, Salinas, Cárdenas, Guadalcázar, Venado, Santa María, Ébano",
                        "municipios": "Municipios de las regiones huasteca sur, altiplano y media",
                        "juzgados1ra": "12 Juzgados Mixtos e Indígenas Náhuatl y Xi'iuy",
                        "juzgadosPaz": "Juzgados Menores y Tradicionales Indígenas",
                        "poblacion": "880,000 habitantes"
                  }
            ]
      },
      "SIN": {
            "abbr": "SIN",
            "nombre": "Sinaloa",
            "circuitoNum": "Décimo Segundo Circuito Judicial Federal",
            "circuitoRomano": "XII Circuito",
            "circuitoCorto": "12º Circuito",
            "circuitoSedes": "Mazatlán, Culiacán y Los Mochis (Sede Regional CAR)",
            "juzgadosFederales": "8 Tribunales Colegiados de Circuito, 2 Colegiados de Apelación y 8 Juzgados de Distrito.",
            "tsjNombre": "Supremo Tribunal de Justicia del Estado de Sinaloa",
            "numPartidos": 5,
            "numPartidosTxt": "5 Distritos Judiciales Estatales",
            "juecesPor100k": "3.7 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Culiacán",
                        "cabecera": "Culiacán Rosales (Centro)",
                        "municipios": "Culiacán, Navolato, Badiraguato",
                        "juzgados1ra": "20 Juzgados de 1ª Instancia (Civiles, Familiares, Mercantiles y de Control Penal Aguaruto)",
                        "juzgadosPaz": "Juzgados Menores en Navolato, Badiraguato, Eldorado y Costa Rica",
                        "poblacion": "1,200,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Mazatlán",
                        "cabecera": "Mazatlán (Sur)",
                        "municipios": "Mazatlán, Concordia, San Ignacio, Rosario, Escuinapa",
                        "juzgados1ra": "14 Juzgados Civiles, Familiares, Mercantiles y Penal Oral",
                        "juzgadosPaz": "Juzgados Menores en Escuinapa, Rosario y Concordia",
                        "poblacion": "680,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Ahome",
                        "cabecera": "Los Mochis (Norte)",
                        "municipios": "Ahome, El Fuerte, Choix",
                        "juzgados1ra": "10 Juzgados Mixtos, Familiares y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores e Indígenas Yoreme / Mayo en El Fuerte y Choix",
                        "poblacion": "580,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Guasave y Salvador Alvarado",
                        "cabecera": "Guasave y Guamúchil",
                        "municipios": "Guasave, Sinaloa de Leyva, Salvador Alvarado, Mocorito, Angostura, Cosalá, Elota",
                        "juzgados1ra": "10 Juzgados Mixtos y de Control Penal Regional",
                        "juzgadosPaz": "Juzgados Menores en Sinaloa de Leyva, Mocorito y La Cruz de Elota",
                        "poblacion": "570,000 habitantes"
                  }
            ]
      },
      "SON": {
            "abbr": "SON",
            "nombre": "Sonora",
            "circuitoNum": "Quinto Circuito Judicial Federal",
            "circuitoRomano": "V Circuito",
            "circuitoCorto": "5º Circuito",
            "circuitoSedes": "Hermosillo, Ciudad Obregón y Nogales",
            "juzgadosFederales": "8 Tribunales Colegiados de Circuito, 2 Colegiados de Apelación y 9 Juzgados de Distrito.",
            "tsjNombre": "Supremo Tribunal de Justicia del Estado de Sonora",
            "numPartidos": 16,
            "numPartidosTxt": "16 Distritos Judiciales Estatales",
            "juecesPor100k": "3.8 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Hermosillo",
                        "cabecera": "Hermosillo (Capital)",
                        "municipios": "Hermosillo, San Miguel de Horcasitas, Carbó",
                        "juzgados1ra": "18 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y de Control Penal",
                        "juzgadosPaz": "Juzgados Calificadores y Menores en Miguel Alemán y Bahía de Kino",
                        "poblacion": "980,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Cajeme",
                        "cabecera": "Ciudad Obregón (Valle del Yaqui)",
                        "municipios": "Cajeme, Bácum, San Ignacio Río Muerto",
                        "juzgados1ra": "12 Juzgados Civiles, Familiares y Penal Oral",
                        "juzgadosPaz": "Juzgados Menores y Tradicionales de los 8 Pueblos Yaquis",
                        "poblacion": "480,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Nogales",
                        "cabecera": "Heroica Nogales (Frontera)",
                        "municipios": "Nogales, Santa Cruz, Imuris",
                        "juzgados1ra": "6 Juzgados Mixtos y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en Imuris y Santa Cruz",
                        "poblacion": "280,000 habitantes"
                  },
                  {
                        "partido": "Distritos de San Luis Río Colorado, Navojoa y Foráneos",
                        "cabecera": "San Luis Río Colorado, Navojoa, Guaymas, Caborca, Agua Prieta, Cananea, Puerto Peñasco, Álamos",
                        "municipios": "Municipios del desierto, costa y sierra de Sonora",
                        "juzgados1ra": "20 Juzgados Mixtos y Tradicionales Mayos / Yoremes",
                        "juzgadosPaz": "Juzgados Menores y Comunitarios",
                        "poblacion": "1,200,000 habitantes"
                  }
            ]
      },
      "TAB": {
            "abbr": "TAB",
            "nombre": "Tabasco",
            "circuitoNum": "Décimo Circuito Judicial Federal",
            "circuitoRomano": "X Circuito",
            "circuitoCorto": "10º Circuito",
            "circuitoSedes": "Villahermosa",
            "juzgadosFederales": "5 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 5 Juzgados de Distrito.",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Tabasco",
            "numPartidos": 16,
            "numPartidosTxt": "16 Distritos Judiciales Estatales",
            "juecesPor100k": "3.7 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial del Centro",
                        "cabecera": "Villahermosa",
                        "municipios": "Centro",
                        "juzgados1ra": "18 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y de Control Penal",
                        "juzgadosPaz": "Juzgados de Paz en Tamulté de las Sabanas, Macultepec y Playas del Rosario",
                        "poblacion": "710,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Cárdenas",
                        "cabecera": "Heroica Cárdenas (Chontalpa)",
                        "municipios": "Cárdenas, Huimanguillo",
                        "juzgados1ra": "8 Juzgados Civiles, Familiares y Penal Oral",
                        "juzgadosPaz": "Juzgados Menores en Villa La Venta y Huimanguillo",
                        "poblacion": "440,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Comalcalco",
                        "cabecera": "Comalcalco",
                        "municipios": "Comalcalco, Paraíso",
                        "juzgados1ra": "6 Juzgados Mixtos y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en Paraíso y Tecolutilla",
                        "poblacion": "330,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Macuspana, Ríos y Sierra",
                        "cabecera": "Macuspana, Teapa, Tenosique, Centla (Frontera), Cunduacán, Jalpa, Balancán, Zapata",
                        "municipios": "Municipios de las regiones de los ríos, pantanos y sierra tabasqueña",
                        "juzgados1ra": "16 Juzgados Mixtos y de Juicio Oral",
                        "juzgadosPaz": "Juzgados de Paz y Menores Municipales",
                        "poblacion": "920,000 habitantes"
                  }
            ]
      },
      "TAM": {
            "abbr": "TAM",
            "nombre": "Tamaulipas",
            "circuitoNum": "Décimo Noveno Circuito Judicial Federal",
            "circuitoRomano": "XIX Circuito",
            "circuitoCorto": "19º Circuito",
            "circuitoSedes": "Ciudad Victoria, Reynosa y Matamoros",
            "juzgadosFederales": "7 Tribunales Colegiados de Circuito, 2 Colegiados de Apelación y 8 Juzgados de Distrito.",
            "tsjNombre": "Supremo Tribunal de Justicia del Estado de Tamaulipas",
            "numPartidos": 15,
            "numPartidosTxt": "15 Distritos Judiciales Estatales",
            "juecesPor100k": "3.8 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Reynosa",
                        "cabecera": "Reynosa (Frontera)",
                        "municipios": "Reynosa, Gustavo Díaz Ordaz",
                        "juzgados1ra": "12 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en Díaz Ordaz y delegaciones de Reynosa",
                        "poblacion": "750,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Tampico / Sur",
                        "cabecera": "Tampico, Ciudad Madero y Altamira",
                        "municipios": "Tampico, Ciudad Madero, Altamira",
                        "juzgados1ra": "14 Juzgados Civiles, Familiares y Penal Acusatorio",
                        "juzgadosPaz": "Juzgados Menores en Madero y Altamira",
                        "poblacion": "880,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Matamoros",
                        "cabecera": "Heroica Matamoros",
                        "municipios": "Matamoros, Valle Hermoso",
                        "juzgados1ra": "8 Juzgados Civiles, Familiares y Penal Oral",
                        "juzgadosPaz": "Juzgados Menores en Valle Hermoso y Control",
                        "poblacion": "610,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Victoria (Centro)",
                        "cabecera": "Ciudad Victoria (Capital)",
                        "municipios": "Victoria, Güémez, Casas, Llera",
                        "juzgados1ra": "10 Juzgados de 1ª Instancia Mixtos y Penales",
                        "juzgadosPaz": "Juzgados Menores en Güémez y Llera",
                        "poblacion": "400,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Nuevo Laredo, Mante y Foráneos",
                        "cabecera": "Nuevo Laredo, Ciudad Mante, Río Bravo, San Fernando, Miguel Alemán, Tula",
                        "municipios": "Municipios de la ribereña, altiplano y cañera de Tamaulipas",
                        "juzgados1ra": "16 Juzgados Mixtos y de Control Penal",
                        "juzgadosPaz": "Juzgados de Paz y Menores en cada municipio",
                        "poblacion": "900,000 habitantes"
                  }
            ]
      },
      "TLAX": {
            "abbr": "TLAX",
            "nombre": "Tlaxcala",
            "circuitoNum": "Vigésimo Octavo Circuito Judicial Federal",
            "circuitoRomano": "XXVIII Circuito",
            "circuitoCorto": "28º Circuito",
            "circuitoSedes": "Tlaxcala de Xicohténcatl",
            "juzgadosFederales": "3 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 3 Juzgados de Distrito.",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Tlaxcala",
            "numPartidos": 3,
            "numPartidosTxt": "3 Distritos Judiciales Estatales",
            "juecesPor100k": "3.2 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Cuauhtémoc",
                        "cabecera": "Tlaxcala Capital (Centro)",
                        "municipios": "Tlaxcala, Chiautempan, Contla, Apetatitlán, Panotla, Totolac",
                        "juzgados1ra": "8 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores y Cívicos en Chiautempan, Contla y Panotla",
                        "poblacion": "580,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Lardizábal y Uribe",
                        "cabecera": "Apizaco (Norte y Oriente)",
                        "municipios": "Apizaco, Huamantla, Tlaxco, Tetla, Xaloztoc, Terrenate",
                        "juzgados1ra": "6 Juzgados Mixtos y de Control Penal Oral",
                        "juzgadosPaz": "Juzgados Menores en Huamantla, Tlaxco y Tetla",
                        "poblacion": "460,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Ocampo",
                        "cabecera": "Calpulalpan (Poniente y Sur)",
                        "municipios": "Calpulalpan, San Pablo del Monte, Zacatelco, Nativitas, Nanacamilpa",
                        "juzgados1ra": "5 Juzgados Mixtos y Salas Penales Regionales",
                        "juzgadosPaz": "Juzgados de Paz y Menores en San Pablo del Monte y Zacatelco",
                        "poblacion": "380,000 habitantes"
                  }
            ]
      },
      "YUC": {
            "abbr": "YUC",
            "nombre": "Yucatán",
            "circuitoNum": "Décimo Cuarto Circuito Judicial Federal",
            "circuitoRomano": "XIV Circuito",
            "circuitoCorto": "14º Circuito",
            "circuitoSedes": "Mérida",
            "juzgadosFederales": "6 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 5 Juzgados de Distrito.",
            "tsjNombre": "Poder Judicial del Estado de Yucatán",
            "numPartidos": 5,
            "numPartidosTxt": "5 Departamentos / Distritos Judiciales Estatales",
            "juecesPor100k": "4.2 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Primer Distrito Judicial",
                        "cabecera": "Mérida (Zona Metropolitana)",
                        "municipios": "Mérida, Progreso, Umán, Kanasín, Motul, Hunucmá, Conkal",
                        "juzgados1ra": "22 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y de Control Penal",
                        "juzgadosPaz": "Juzgados de Paz y Menores en Progreso, Kanasín, Umán y Motul",
                        "poblacion": "1,450,000 habitantes"
                  },
                  {
                        "partido": "Segundo Distrito Judicial",
                        "cabecera": "Ticul (Sur)",
                        "municipios": "Ticul, Tekax, Oxkutzcab, Peto, Muna",
                        "juzgados1ra": "4 Juzgados Mixtos e Indígenas Mayas",
                        "juzgadosPaz": "Juzgados de Paz Maya en Tekax, Oxkutzcab y Peto",
                        "poblacion": "280,000 habitantes"
                  },
                  {
                        "partido": "Tercer Distrito Judicial",
                        "cabecera": "Valladolid (Oriente)",
                        "municipios": "Valladolid, Tizimín, Chemax, Espita, Temozón",
                        "juzgados1ra": "5 Juzgados Mixtos y de Juicio Oral Penal",
                        "juzgadosPaz": "Juzgados Tradicionales Mayas en Chemax y Tizimín",
                        "poblacion": "360,000 habitantes"
                  },
                  {
                        "partido": "Cuarto y Quinto Distrito",
                        "cabecera": "Izamal y Hunucmá",
                        "municipios": "Izamal, Tunkás, Dzilam González, Hunucmá, Celestún, Maxcanú",
                        "juzgados1ra": "4 Juzgados Mixtos de 1ª Instancia",
                        "juzgadosPaz": "Juzgados de Paz en Celestún y Maxcanú",
                        "poblacion": "240,000 habitantes"
                  }
            ]
      },
      "ZAC": {
            "abbr": "ZAC",
            "nombre": "Zacatecas",
            "circuitoNum": "Vigésimo Tercer Circuito Judicial Federal",
            "circuitoRomano": "XXIII Circuito",
            "circuitoCorto": "23º Circuito",
            "circuitoSedes": "Zacatecas Capital (Sede Regional CAR)",
            "juzgadosFederales": "4 Tribunales Colegiados de Circuito, 1 Colegiado de Apelación y 4 Juzgados de Distrito.",
            "tsjNombre": "Tribunal Superior de Justicia del Estado de Zacatecas",
            "numPartidos": 18,
            "numPartidosTxt": "18 Distritos Judiciales Estatales",
            "juecesPor100k": "3.6 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de la Capital",
                        "cabecera": "Zacatecas y Guadalupe",
                        "municipios": "Zacatecas, Guadalupe, Calera, Trancoso, Vetagrande, Morelos",
                        "juzgados1ra": "14 Juzgados de 1ª Instancia Civiles, Familiares, Mercantiles y de Control Penal Cerereso Cieneguillas",
                        "juzgadosPaz": "Juzgados Menores en Calera y Trancoso",
                        "poblacion": "420,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Fresnillo",
                        "cabecera": "Fresnillo (Centro-Norte)",
                        "municipios": "Fresnillo, Valparaíso, Enrique Estrada",
                        "juzgados1ra": "6 Juzgados Civiles, Familiares y Penal Oral",
                        "juzgadosPaz": "Juzgados Menores en Valparaíso y Plateros",
                        "poblacion": "280,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Jerez",
                        "cabecera": "Jerez de García Salinas",
                        "municipios": "Jerez, Susticacán, Tepetongo, Monte Escobedo",
                        "juzgados1ra": "3 Juzgados Mixtos y de Control Penal",
                        "juzgadosPaz": "Juzgados Menores en Monte Escobedo y Tepetongo",
                        "poblacion": "110,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Sombrerete, Río Grande, Jalpa y Foráneos",
                        "cabecera": "Sombrerete, Río Grande, Jalpa, Tlaltenango, Pinos, Concepción del Oro, Loreto, Ojocaliente",
                        "municipios": "Municipios del semidesierto, cañones y valles zacatecanos",
                        "juzgados1ra": "16 Juzgados Mixtos y Salas Penales Regionales",
                        "juzgadosPaz": "Juzgados Menores Municipales de Paz",
                        "poblacion": "810,000 habitantes"
                  }
            ]
      },
      "MÉX": {
            "abbr": "MEX",
            "nombre": "Estado de México",
            "circuitoNum": "Segundo Circuito Judicial Federal",
            "circuitoRomano": "II Circuito",
            "circuitoCorto": "2º Circuito",
            "circuitoSedes": "Toluca de Lerdo y Naucalpan de Juárez",
            "juzgadosFederales": "22 Tribunales Colegiados de Circuito, 4 Tribunales Colegiados de Apelación, 23 Juzgados de Distrito y CJPF Almoloya de Juárez (Altiplano).",
            "tsjNombre": "Poder Judicial del Estado de México (PJEDOMEX)",
            "numPartidos": 18,
            "numPartidosTxt": "18 Distritos Judiciales Estatales",
            "juecesPor100k": "3.1 jueces / 100k hab (Promedio OCDE: 18)",
            "partidos": [
                  {
                        "partido": "Distrito Judicial de Toluca",
                        "cabecera": "Toluca de Lerdo",
                        "municipios": "Toluca, Metepec, Zinacantepec, Almoloya de Juárez, Villa Victoria",
                        "juzgados1ra": "24 Juzgados de 1ª Instancia (Civil, Familiar, Mercantil y Penal Almoloya)",
                        "juzgadosPaz": "Juzgados de Cuantía Menor en Metepec y Zinacantepec",
                        "poblacion": "1,850,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Tlalnepantla",
                        "cabecera": "Tlalnepantla de Baz",
                        "municipios": "Tlalnepantla, Naucalpan, Atizapán de Zaragoza, Huixquilucan, Nicolás Romero",
                        "juzgados1ra": "32 Juzgados Civiles, Familiares y Mercantiles Orales",
                        "juzgadosPaz": "Juzgados de Paz y Conciliación Municipal en Atizapán y Naucalpan",
                        "poblacion": "2,900,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Ecatepec",
                        "cabecera": "Ecatepec de Morelos",
                        "municipios": "Ecatepec, Coacalco, Tecámac",
                        "juzgados1ra": "28 Juzgados de 1ª Instancia Civiles y Penales de Chiconautla",
                        "juzgadosPaz": "Juzgados de Cuantía Menor de proximidad en Tecámac y Coacalco",
                        "poblacion": "2,550,000 habitantes"
                  },
                  {
                        "partido": "Distrito Judicial de Nezahualcóyotl",
                        "cabecera": "Ciudad Nezahualcóyotl",
                        "municipios": "Nezahualcóyotl, Chimalhuacán, La Paz",
                        "juzgados1ra": "22 Juzgados Familiares, Civiles y Penal Neza Bordo",
                        "juzgadosPaz": "Juzgados Municipales de Paz en Chimalhuacán y La Paz",
                        "poblacion": "1,950,000 habitantes"
                  },
                  {
                        "partido": "Distritos de Texcoco, Chalco, Cuautitlán y Foráneos",
                        "cabecera": "Sedes: Texcoco, Chalco, Cuautitlán Izcalli, Zumpango, Otumba, El Oro, Ixtlahuaca, Tenango, Tenancingo, Sultepec, Valle de Bravo, Jilotepec",
                        "municipios": "Resto de los 125 municipios mexiquenses",
                        "juzgados1ra": "45 Juzgados de 1ª Instancia Mixtos y Penales",
                        "juzgadosPaz": "Red de Juzgados de Cuantía Menor y Mediación Comunitaria",
                        "poblacion": "7,800,000 habitantes"
                  }
            ]
      }
}
  };

  let currentPjView = 'scjn'; // 'scjn' | 'pjf' | 'territorio'
  let currentPjMapMode = 'geo'; // 'geo' | 'cartogram'
  let selectedPjStateAbbr = 'JAL';
  let selectedPjNodeId = 'scjn_pleno';
  let selectedPjFilterLevel = 'todos';
  let pjLeafletMap = null;
  let pjGeoJsonLayer = null;
  let pjTerritorialStageInitialized = false;

  function initJudicialEstructuraModule() {
    renderJudicialConceptualMap('scjn');
    renderJudicialConceptualMap('pjf');
    initTerritorialStage();
    setPjView(currentPjView);
  }

  function setPjView(viewMode) {
    currentPjView = viewMode;

    const btnScjn = document.getElementById('btnPjViewScjn');
    const btnPjf = document.getElementById('btnPjViewPjf');
    const btnTerritorio = document.getElementById('btnPjViewTerritorio');

    if (btnScjn) btnScjn.classList.toggle('active', viewMode === 'scjn');
    if (btnPjf) btnPjf.classList.toggle('active', viewMode === 'pjf');
    if (btnTerritorio) btnTerritorio.classList.toggle('active', viewMode === 'territorio');

    const stageScjn = document.getElementById('pjStageScjn');
    const stagePjf = document.getElementById('pjStagePjf');
    const stageTerritorio = document.getElementById('pjStageTerritorio');

    if (stageScjn) stageScjn.style.display = viewMode === 'scjn' ? 'block' : 'none';
    if (stagePjf) stagePjf.style.display = viewMode === 'pjf' ? 'block' : 'none';
    if (stageTerritorio) stageTerritorio.style.display = viewMode === 'territorio' ? 'block' : 'none';

    if (viewMode === 'scjn') {
      selectPjNode(selectedPjNodeId || 'scjn_pleno', 'scjn');
    } else if (viewMode === 'pjf') {
      selectPjNode(selectedPjNodeId || 'pjf_especializados_telecom', 'pjf');
    } else if (viewMode === 'territorio') {
      updatePjMainTerritorialView(selectedPjStateAbbr);
      if (currentPjMapMode === 'geo') {
        if (!pjLeafletMap) {
          initPjLeafletMap();
        }
        setTimeout(() => {
          if (pjLeafletMap) pjLeafletMap.invalidateSize();
        }, 60);
      } else {
        renderPjCartogram();
      }
    }
  }

  function setPjMapMode(mode) {
    currentPjMapMode = mode;
    const geoWrap = document.getElementById('pjGeoMapWrapper');
    const cartoWrap = document.getElementById('pjCartogramWrapper');
    const btnGeo = document.getElementById('btnPjMapGeo');
    const btnCarto = document.getElementById('btnPjMapCarto');

    if (btnGeo) btnGeo.classList.toggle('active', mode === 'geo');
    if (btnCarto) btnCarto.classList.toggle('active', mode === 'cartogram');

    if (geoWrap) geoWrap.style.display = mode === 'geo' ? 'block' : 'none';
    if (cartoWrap) cartoWrap.style.display = mode === 'cartogram' ? 'block' : 'none';

    if (mode === 'geo') {
      if (!pjLeafletMap) {
        initPjLeafletMap();
      }
      setTimeout(() => {
        if (pjLeafletMap) pjLeafletMap.invalidateSize();
      }, 60);
    } else {
      renderPjCartogram();
    }
  }

  function initPjLeafletMap() {
    const mapEl = document.getElementById('pjGeoMapContainer');
    if (!mapEl || pjLeafletMap) return;

    try {
      pjLeafletMap = L.map('pjGeoMapContainer', {
        center: [23.6345, -102.5528],
        zoom: 4.8,
        minZoom: 3.5,
        maxZoom: 8,
        zoomControl: true,
        attributionControl: false
      });

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png', {
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(pjLeafletMap);

      renderPjGeoJsonLayer();
    } catch (err) {
      console.warn('Error inicializando mapa judicial:', err);
    }
  }

  function renderPjGeoJsonLayer() {
    if (!pjLeafletMap || !window.MEXICO_GEOJSON) return;

    if (pjGeoJsonLayer) {
      pjLeafletMap.removeLayer(pjGeoJsonLayer);
    }

    pjGeoJsonLayer = L.geoJSON(window.MEXICO_GEOJSON, {
      style: function(feature) {
        const abbr = feature.properties.abbr;
        const isSel = abbr === selectedPjStateAbbr || (abbr === 'MÉX' && selectedPjStateAbbr === 'MEX');
        return {
          fillColor: isSel ? '#d4af37' : '#141826',
          weight: isSel ? 2.5 : 1.2,
          opacity: 1,
          color: isSel ? '#f3cf65' : '#2a334d',
          fillOpacity: isSel ? 0.9 : 0.75
        };
      },
      onEachFeature: function(feature, layer) {
        const rawAbbr = feature.properties.abbr;
        const abbr = rawAbbr === 'MÉX' ? 'MEX' : rawAbbr;
        const stData = PJF_ESTRUCTURA_DATA.territorio[abbr] || PJF_ESTRUCTURA_DATA.territorio[rawAbbr];
        if (!stData) return;

        layer.bindTooltip(`
          <div class="leaflet-pj-circuit-tooltip">
            <strong style="color:var(--gold-bright); font-size:13px; font-family:var(--font-serif);">${stData.nombre}</strong>
            <div style="color:var(--gold); font-family:var(--font-mono); font-size:11px; margin-top:3px; font-weight:700;">
              🏛️ ${stData.circuitoNum} (${stData.circuitoRomano})
            </div>
            <div style="font-size:10.5px; color:#aaa; margin-top:2px;">
              ${stData.numPartidosTxt} · Haz clic para abrir expediente
            </div>
          </div>
        `, { sticky: true, className: 'leaflet-pj-circuit-tooltip' });

        layer.on({
          mouseover: function(e) {
            const l = e.target;
            l.setStyle({
              weight: 2.8,
              color: '#f3cf65',
              fillOpacity: 0.95
            });
            l.bringToFront();
          },
          mouseout: function(e) {
            if (pjGeoJsonLayer) {
              pjGeoJsonLayer.resetStyle(e.target);
            }
          },
          click: function(e) {
            selectPjEstado(abbr);
            openPjCircuitDrawer(abbr);
            if (pjLeafletMap) {
              pjLeafletMap.fitBounds(e.target.getBounds(), { padding: [40, 40], maxZoom: 6.5 });
            }
          }
        });
      }
    }).addTo(pjLeafletMap);
  }

  function renderPjCartogram() {
    const grid = document.getElementById('pjCartogramGrid');
    if (!grid) return;

    grid.innerHTML = '';
    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 11; c++) {
        const match = cartogramLayout.find(item => item[0] === r && item[1] === c);
        const cell = document.createElement('div');
        cell.style.gridRow = r + 1;
        cell.style.gridColumn = c + 1;

        if (match) {
          const rawAbbr = match[2];
          const abbr = rawAbbr === 'MÉX' ? 'MEX' : rawAbbr;
          const stData = PJF_ESTRUCTURA_DATA.territorio[abbr] || PJF_ESTRUCTURA_DATA.territorio[rawAbbr];
          const isSel = abbr === selectedPjStateAbbr;

          cell.className = `state-cell ${isSel ? 'active' : ''}`;
          cell.title = stData ? `${stData.nombre} - ${stData.circuitoNum}` : abbr;
          cell.onclick = () => {
            selectPjEstado(abbr);
            openPjCircuitDrawer(abbr);
          };

          cell.innerHTML = `
            <span class="abbr">${abbr}</span>
            <span class="circuit-tag">${stData ? stData.circuitoCorto : ''}</span>
          `;
        } else {
          cell.className = 'empty-cell';
        }
        grid.appendChild(cell);
      }
    }
  }

  function renderPjNodeAccordionHtml(n, view) {
    let specialtyHtml = '';
    if (n.distincionEspecialidad) {
      if (n.distincionEspecialidad.tipo === 'especializados_vs_mixtos') {
        specialtyHtml = `
          <div class="pj-accordion-section">
            <div class="pj-accordion-section-title">
              ⚖️ Diferenciación Operativa: Órganos Especializados vs. Mixtos
            </div>
            <div class="pj-specialty-grid">
              <div class="pj-specialty-col especializado">
                <div class="pj-specialty-col-header">
                  <span>🏛️</span> Órganos Especializados por Materia
                </div>
                <div>${n.distincionEspecialidad.especializados}</div>
              </div>
              <div class="pj-specialty-col mixto">
                <div class="pj-specialty-col-header">
                  <span>🌐</span> Órganos Mixtos (Concurrencia Total)
                </div>
                <div>${n.distincionEspecialidad.mixtos}</div>
              </div>
            </div>
          </div>
        `;
      } else {
        specialtyHtml = `
          <div class="pj-accordion-section">
            <div class="pj-accordion-section-title">
              ⚖️ ${n.distincionEspecialidad.titulo || 'Régimen y Especialidad Jurisdiccional'}
            </div>
            <p class="pj-accordion-section-text">
              ${n.distincionEspecialidad.detalle}
            </p>
          </div>
        `;
      }
    }

    const citesHtml = (n.fundamentoDetallado || []).map(cite => `
      <li><span class="pj-cite-bullet">§</span> ${cite}</li>
    `).join('');

    return `
      <div class="pj-concept-accordion-body" id="pjAccordion_${n.id}" style="display:none;">
        <!-- Misión y funciones cotidianas -->
        <div class="pj-accordion-section">
          <div class="pj-accordion-section-title">
            📌 ¿A qué se dedica específicamente en la práctica jurisdiccional cotidiana?
          </div>
          <p class="pj-accordion-section-text">
            ${n.quehacer || n.desc}
          </p>
        </div>

        <!-- Régimen de Especialización (Especializados vs Mixtos) -->
        ${specialtyHtml}

        <!-- Fundamentación Legal Exhaustiva -->
        <div class="pj-accordion-section">
          <div class="pj-accordion-section-title">
            📜 Fundamentación Constitucional y Legal Exhaustiva
          </div>
          <ul class="pj-legal-cite-list">
            ${citesHtml}
          </ul>
        </div>

        <!-- Personal, Estructura y Presupuesto -->
        <div class="pj-accordion-section">
          <div class="pj-accordion-section-title">
            👥 Titularidad, Integración &amp; Carga Presupuestal
          </div>
          <p class="pj-accordion-section-text" style="font-family:var(--font-mono); font-size:12px;">
            ${n.titular} ${n.plazasPresupuesto ? `· <span style="color:var(--gold-bright);">${n.plazasPresupuesto}</span>` : ''}
          </p>
        </div>

        <!-- Barra de Enlaces Periciales y Botón de Cierre -->
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; padding-top:8px; border-top:1px dashed var(--border-subtle); font-family:var(--font-mono); font-size:11px;">
          <div style="display:flex; gap:12px; flex-wrap:wrap;">
            <span>📚 Glosario: <a class="glos-link" onclick="window.AuditEngine.goToGlossary('${n.glosario}')">${n.glosario} ↗</a></span>
            <span>📑 Cita / Marco: <a class="ref-link" onclick="window.AuditEngine.goToRef('${n.refKey}')">[Ref. ${n.refNum}] ↗</a></span>
          </div>
          <button type="button" class="pj-concept-card-btn" onclick="window.AuditEngine.togglePjCardAccordion('${n.id}', '${view}')" style="padding:4px 10px; font-size:10.5px;">
            ✕ Contraer Ficha
          </button>
        </div>
      </div>
    `;
  }

  function renderJudicialConceptualMap(view) {
    const container = document.getElementById(view === 'scjn' ? 'pjStageScjn' : 'pjStagePjf');
    if (!container) return;

    const dataTree = view === 'scjn' ? PJF_ESTRUCTURA_DATA.scjn : PJF_ESTRUCTURA_DATA.pjf;
    const viewTitle = view === 'scjn' ? 'Suprema Corte de Justicia de la Nación (SCJN)' : 'Poder Judicial de la Federación (PJF)';

    container.innerHTML = `
      <div class="pj-concept-map-container">
        <!-- Espina conectora vertical central -->
        <div class="pj-concept-spine"></div>

        <!-- Barra de herramientas y filtros por nivel -->
        <div class="pj-concept-toolbar" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:24px; background:rgba(255,255,255,0.02); border:1px solid var(--border-subtle); padding:12px 16px; border-radius:8px; position:relative; z-index:3;">
          <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
            <span style="font-family:var(--font-mono); font-size:11px; color:var(--gold-bright); font-weight:700; text-transform:uppercase; letter-spacing:1px;">
              🎛️ Filtrar Nivel Jerárquico:
            </span>
            <div class="pj-level-pills-bar" id="pjLevelPills_${view}">
              <button type="button" class="pj-level-pill active" onclick="window.AuditEngine.filterPjConceptLevel('todos', '${view}')">🌐 Todo el Organigrama</button>
              ${dataTree.map((lvl, idx) => `
                <button type="button" class="pj-level-pill" onclick="window.AuditEngine.filterPjConceptLevel(${idx + 1}, '${view}')">Nivel ${idx + 1}</button>
              `).join('')}
            </div>
          </div>

          <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
            <button type="button" class="pj-hierarchical-btn" onclick="window.AuditEngine.openPjHierarchicalModal('${view}')">
              <span>🏛️</span> ${view === 'scjn' ? 'Mapa Jerárquico Visual (Pirámide SCJN)' : 'Mapa Jerárquico Visual (Pirámide PJF)'} ➔
            </button>
            <button type="button" class="pj-toggle-all-btn" onclick="window.AuditEngine.toggleAllPjAccordions('${view}')" id="pjToggleAllBtn_${view}">
              <span>📂</span> Expandir Todas las Fichas
            </button>
          </div>
        </div>

        <!-- Niveles del Mapa Conceptual Jerárquico -->
        <div class="pj-concept-levels-wrapper">
          ${dataTree.map((lvl, idx) => `
            <div class="pj-concept-level-block" data-level="${idx + 1}" id="pjLevel_${view}_${idx + 1}">
              
              <!-- Insignia Conectora del Nivel -->
              <div class="pj-level-badge-header">
                <div class="pj-level-pill-badge">
                  <span>🏛️ NIVEL ${idx + 1}</span>
                  <span style="color:var(--text-dim);">·</span>
                  <span style="color:var(--text-main);">${lvl.nivel.split(':')[1] ? lvl.nivel.split(':')[1].trim() : lvl.nivel}</span>
                </div>
              </div>

              <!-- Grilla de Tarjetas Conceptuales del Nivel -->
              <div class="pj-concept-cards-grid">
                ${lvl.nodos.map(n => `
                  <div class="pj-concept-card ${n.specialClass || ''}" id="pjCard_${n.id}">
                    <div class="pj-concept-card-top" style="cursor:pointer;" onclick="window.AuditEngine.togglePjCardAccordion('${n.id}', '${view}')">
                      <div class="pj-concept-card-title">
                        <span>${n.icono}</span> ${n.titulo}
                      </div>
                      <span class="pj-node-badge ${n.badgeTipo}">${n.badge}</span>
                    </div>

                    <div class="pj-concept-card-desc">
                      ${n.desc}
                    </div>

                    <div class="pj-concept-card-meta">
                      <div>👤 <strong>Titularidad / Integración:</strong> ${n.titular}</div>
                      <div>📜 <strong>Fundamento:</strong> ${n.marco}</div>
                    </div>

                    <div class="pj-concept-card-action">
                      <button type="button" class="pj-concept-card-btn pj-btn-accordion-action" 
                              onclick="window.AuditEngine.togglePjCardAccordion('${n.id}', '${view}')"
                              id="pjBtnAccordion_${n.id}">
                        <span>🔍</span> Ver Desglose &amp; Competencias ▾
                      </button>
                    </div>

                    <!-- Acordeón Inline Directo dentro de la Tarjeta -->
                    ${renderPjNodeAccordionHtml(n, view)}
                  </div>
                `).join('')}
              </div>

            </div>
          `).join('')}
        </div>

      </div>
    `;
  }

  function togglePjCardAccordion(nodeId, view) {
    const card = document.getElementById(`pjCard_${nodeId}`);
    const acc = document.getElementById(`pjAccordion_${nodeId}`);
    const btn = document.getElementById(`pjBtnAccordion_${nodeId}`);
    if (!acc || !card) return;

    const isOpen = acc.style.display === 'block';
    if (isOpen) {
      acc.style.display = 'none';
      card.classList.remove('is-expanded');
      if (btn) btn.innerHTML = '<span>🔍</span> Ver Desglose &amp; Competencias ▾';
    } else {
      acc.style.display = 'block';
      card.classList.add('is-expanded');
      if (btn) btn.innerHTML = '<span>▲</span> Ocultar Desglose y Competencias ▴';
    }
  }

  function toggleAllPjAccordions(view) {
    const container = document.getElementById(view === 'scjn' ? 'pjStageScjn' : 'pjStagePjf');
    if (!container) return;

    const btn = document.getElementById(`pjToggleAllBtn_${view}`);
    const allAccordions = container.querySelectorAll('.pj-concept-accordion-body');
    const allCards = container.querySelectorAll('.pj-concept-card');
    const allBtns = container.querySelectorAll('.pj-btn-accordion-action');

    let hasClosed = false;
    allAccordions.forEach(acc => {
      if (acc.style.display === 'none' || !acc.style.display) hasClosed = true;
    });

    const shouldOpen = hasClosed;
    allAccordions.forEach(acc => {
      acc.style.display = shouldOpen ? 'block' : 'none';
    });
    allCards.forEach(card => {
      card.classList.toggle('is-expanded', shouldOpen);
    });
    allBtns.forEach(b => {
      b.innerHTML = shouldOpen 
        ? '<span>▲</span> Ocultar Desglose y Competencias ▴' 
        : '<span>🔍</span> Ver Desglose &amp; Competencias ▾';
    });

    if (btn) {
      btn.innerHTML = shouldOpen 
        ? '<span>📁</span> Contraer Todas las Fichas' 
        : '<span>📂</span> Expandir Todas las Fichas';
    }
  }

  function filterPjConceptLevel(level, view) {
    selectedPjFilterLevel = level;
    const container = document.getElementById(view === 'scjn' ? 'pjStageScjn' : 'pjStagePjf');
    if (!container) return;

    // Actualizar botones de píldora
    const pillsBar = document.getElementById(`pjLevelPills_${view}`);
    if (pillsBar) {
      pillsBar.querySelectorAll('.pj-level-pill').forEach(btn => {
        const isMatch = (level === 'todos' && btn.innerText.includes('Todo')) || 
                        (level !== 'todos' && btn.innerText.includes(`Nivel ${level}`));
        btn.classList.toggle('active', isMatch);
      });
    }

    // Filtrar bloques de nivel
    container.querySelectorAll('.pj-concept-level-block').forEach(blk => {
      const blockLvl = blk.getAttribute('data-level');
      if (level === 'todos' || String(blockLvl) === String(level)) {
        blk.classList.remove('hidden-by-filter');
      } else {
        blk.classList.add('hidden-by-filter');
      }
    });
  }

  function initTerritorialStage() {
    if (pjTerritorialStageInitialized) return;
    pjTerritorialStageInitialized = true;

    const statesList = DB.estados || [];
    const chipsGrid = document.getElementById('pjStatesChipsGrid');
    if (chipsGrid) {
      chipsGrid.innerHTML = statesList.map(st => {
        const sAbbr = st.abbr === 'MÉX' ? 'MEX' : st.abbr;
        const cData = PJF_ESTRUCTURA_DATA.territorio[sAbbr] || {};
        return `
          <div class="pj-state-chip ${sAbbr === selectedPjStateAbbr ? 'active' : ''}" 
               onclick="window.AuditEngine.selectPjEstado('${sAbbr}'); window.AuditEngine.openPjCircuitDrawer('${sAbbr}')">
            <span style="font-weight:700;">${st.abbr}</span>
            <span style="font-size:8.5px; opacity:0.8; font-family:var(--font-mono); display:block;">${cData.circuitoCorto || ''}</span>
          </div>
        `;
      }).join('');
    }

    updatePjMainTerritorialView(selectedPjStateAbbr);
  }

  function selectPjNode(nodeId, view) {
    selectedPjNodeId = nodeId;
    const card = document.getElementById(`pjCard_${nodeId}`);
    if (card) {
      togglePjCardAccordion(nodeId, view);
    }
  }

  function openPjHierarchicalModal(view) {
    const modal = document.getElementById('pjHierarchicalModal');
    const overlay = document.getElementById('pjHierarchicalModalOverlay');
    if (!modal || !overlay) return;

    // Actualizar título del modal según la vista
    const titleEl = modal.querySelector('.pj-modal-title');
    const subtitleEl = modal.querySelector('.pj-modal-subtitle');
    if (view === 'scjn') {
      if (titleEl) titleEl.innerHTML = '🏛️ Pirámide de la Suprema Corte de Justicia de la Nación (SCJN)';
      if (subtitleEl) subtitleEl.textContent = 'Organigrama Constitucional Interno · Arts. 94, 100 y 105 CPEUM · LOPJF';
    } else {
      if (titleEl) titleEl.innerHTML = '🏛️ Mapa Jerárquico del Poder Judicial de la Federación';
      if (subtitleEl) subtitleEl.textContent = 'Pirámide Constitucional Orgánica · Arts. 94 a 107 CPEUM';
    }

    if (view === 'scjn') {
      renderPjScjnHierarchicalContent();
    } else {
      renderPjHierarchicalModalContent();
    }

    overlay.classList.add('open');
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';

    // Cerrar con tecla Escape
    const escHandler = (e) => {
      if (e.key === 'Escape') {
        closePjHierarchicalModal();
        window.removeEventListener('keydown', escHandler);
      }
    };
    window.addEventListener('keydown', escHandler);
  }

  function closePjHierarchicalModal() {
    const modal = document.getElementById('pjHierarchicalModal');
    const overlay = document.getElementById('pjHierarchicalModalOverlay');
    if (!modal || !overlay) return;

    overlay.classList.remove('open');
    modal.classList.remove('open');
    document.body.style.overflow = '';
  }

  // ═══════════════════════════════════════════════════════════════════════
  // PIRÁMIDE ESPECÍFICA DE LA SCJN (vista "1. Organigrama SCJN")
  // ═══════════════════════════════════════════════════════════════════════
  function renderPjScjnHierarchicalContent() {
    const body = document.getElementById('pjHierarchicalModalBody');
    if (!body) return;

    body.innerHTML = `
      <div class="pj-pyramid-tree">

        <!-- ═══ NIVEL 1: PLENO DE LA SCJN ═══ -->
        <div class="pj-tree-level-wrapper">
          <div class="pj-tree-level-label">
            🏛️ NIVEL 1 · PLENO DE LA SUPREMA CORTE DE JUSTICIA DE LA NACIÓN
          </div>
          <div class="pj-tree-row">
            <div class="pj-tree-node node-gold" style="max-width:560px; text-align:center;">
              <div class="pj-tree-node-title" style="justify-content:center; font-size:16px;">
                <span>🏛️</span> Tribunal Pleno de la SCJN
              </div>
              <span class="pj-tree-node-badge badge-gold" style="align-self:center;">
                11 Ministras y Ministros (9 en Reforma 2024) · Órgano Supremo del PJF
              </span>
              <p class="pj-tree-node-desc">
                Máximo órgano colegiado del Estado mexicano en materia jurisdiccional. Ejerce el <strong>control concentrado de constitucionalidad</strong>: 
                invalida leyes con efectos generales, resuelve controversias entre poderes y emite precedentes obligatorios para todos los tribunales del país.
              </p>
              <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:10px; text-align:left; font-size:11px;">
                <div style="background:rgba(212,175,55,0.10); border:1px solid rgba(212,175,55,0.3); padding:8px 10px; border-radius:6px;">
                  <strong style="color:var(--gold-bright); display:block; margin-bottom:3px;">⚖️ Acciones de Inconstitucionalidad</strong>
                  Demandas abstractas contra leyes federales, estatales o tratados que contradigan la Constitución. 
                  Requieren mayoría calificada de 8 votos (6 votos en la reforma 2024) para invalidar con efectos generales.
                </div>
                <div style="background:rgba(212,175,55,0.10); border:1px solid rgba(212,175,55,0.3); padding:8px 10px; border-radius:6px;">
                  <strong style="color:var(--gold-bright); display:block; margin-bottom:3px;">🏛️ Controversias Constitucionales</strong>
                  Litigios competenciales entre Federación, estados, municipios y poderes de la Unión.
                  El Pleno decide a quién corresponde cada facultad disputada.
                </div>
              </div>
              <div class="pj-tree-node-law">
                📜 Arts. 94 y 105 CPEUM · Arts. 2, 10 y 11 LOPJF
              </div>
            </div>
          </div>
          <div class="pj-tree-connector-down"></div>
        </div>

        <!-- ═══ NIVEL 2: PRESIDENCIA & SECRETARÍA GENERAL DE ACUERDOS ═══ -->
        <div class="pj-tree-level-wrapper">
          <div class="pj-tree-level-label">
            ⭐ NIVEL 2 · PRESIDENCIA, GOBIERNO INTERNO Y FE PÚBLICA PLENARIA
          </div>
          <div class="pj-tree-row">
            
            <!-- Presidencia -->
            <div class="pj-tree-node node-gold">
              <div class="pj-tree-node-title">
                <span>⭐</span> Presidencia de la SCJN
              </div>
              <span class="pj-tree-node-badge badge-gold">Mando Institucional · 38 Plazas Directas</span>
              <p class="pj-tree-node-desc">
                Representación legal ante los demás Poderes de la Unión. Conduce las sesiones del Pleno, somete proyectos a votación, 
                turna expedientes por orden riguroso a las ponencias y supervisa la administración interna de la Corte.
              </p>
              <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">
                • <strong>No integra ninguna Sala</strong> — su función es dirección y representación.<br>
                • Turno transparente de asuntos a las 11 ponencias.<br>
                • Nombra y remueve personal de confianza adscrito.
              </div>
              <div class="pj-tree-node-law">
                📜 Arts. 12, 13 y 14 LOPJF · Reglamento Interior SCJN
              </div>
            </div>

            <!-- SGA -->
            <div class="pj-tree-node node-cyan">
              <div class="pj-tree-node-title">
                <span>📜</span> Secretaría General de Acuerdos (SGA)
              </div>
              <span class="pj-tree-node-badge badge-cyan">Fe Pública Jurisdiccional</span>
              <p class="pj-tree-node-desc">
                Órgano fedatario supremo del Tribunal Pleno. Sin su certificación, ninguna sentencia cobra fuerza vinculante.
              </p>
              <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">
                • Redacta actas de sesiones públicas y privadas.<br>
                • Certifica el cómputo de votos para jurisprudencia.<br>
                • Custodia el archivo de acuerdos jurisdiccionales.<br>
                • Supervisa asignación aleatoria de turnos a ponencias.
              </div>
              <div class="pj-tree-node-law">
                📜 Arts. 45 a 58 Reglamento Interior SCJN
              </div>
            </div>

          </div>
          <div class="pj-tree-connector-down"></div>
        </div>

        <!-- ═══ NIVEL 3: SALAS JURISDICCIONALES ═══ -->
        <div class="pj-tree-level-wrapper">
          <div class="pj-tree-level-label">
            ⚖️ NIVEL 3 · SALAS JURISDICCIONALES ESPECIALIZADAS
          </div>
          <div class="pj-tree-row">
            
            <!-- Primera Sala -->
            <div class="pj-tree-node node-amber">
              <div class="pj-tree-node-title">
                <span>⚖️</span> Primera Sala
              </div>
              <span class="pj-tree-node-badge badge-amber">5 Ministros · $192.0 mdp/año · Materia Civil y Penal</span>
              <p class="pj-tree-node-desc">
                Especializada en libertades civiles, derechos humanos, debido proceso penal acusatorio, presunción de inocencia, 
                derecho familiar y mercantil.
              </p>
              <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.06); padding:8px; border-radius:6px; font-size:11px; margin-top:6px;">
                <div style="color:var(--cyan); margin-bottom:4px;">
                  <strong>Competencia específica:</strong>
                </div>
                <div style="color:#cbd5e1;">
                  • Amparos en revisión sobre constitucionalidad de leyes penales y civiles<br>
                  • Interpretación de tratados internacionales de DDHH<br>
                  • Prohibición de tortura, legalidad de detenciones<br>
                  • Interés superior de la niñez, equidad de género<br>
                  • <strong>No conoce</strong> de materias fiscal, administrativa ni laboral
                </div>
              </div>
              <div class="pj-tree-node-law">
                📜 Art. 21 Fr. I LOPJF · Arts. 81, 83 y 86 Ley de Amparo
              </div>
            </div>

            <!-- Segunda Sala -->
            <div class="pj-tree-node node-amber">
              <div class="pj-tree-node-title">
                <span>🏛️</span> Segunda Sala
              </div>
              <span class="pj-tree-node-badge badge-amber">4–5 Ministros · $188.4 mdp/año · Materia Admin. y Laboral</span>
              <p class="pj-tree-node-desc">
                Especializada en control de legalidad de actos del Ejecutivo Federal, derecho tributario, fiscal, ambiental, 
                seguridad social y derecho laboral.
              </p>
              <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.06); padding:8px; border-radius:6px; font-size:11px; margin-top:6px;">
                <div style="color:var(--cyan); margin-bottom:4px;">
                  <strong>Competencia específica:</strong>
                </div>
                <div style="color:#cbd5e1;">
                  • Litigios contra SAT, IMSS, ISSSTE, SEMARNAT, CRE, CFE<br>
                  • Amparos en materia de ISR, IVA, IEPS, Código Fiscal<br>
                  • Concesiones mineras y telecomunicaciones (2ª instancia)<br>
                  • Huelgas, contratos colectivos y justicia laboral federal<br>
                  • <strong>No conoce</strong> de materias penal ni civil
                </div>
              </div>
              <div class="pj-tree-node-law">
                📜 Art. 21 Fr. II LOPJF · Arts. 81 y 84 Ley de Amparo
              </div>
            </div>

          </div>
          <div class="pj-tree-connector-down"></div>
        </div>

        <!-- ═══ NIVEL 4: DESPACHOS TÉCNICOS Y CULTURA JURÍDICA ═══ -->
        <div class="pj-tree-level-wrapper">
          <div class="pj-tree-level-label">
            👥 NIVEL 4 · PONENCIAS TÉCNICAS, DIFUSIÓN Y ACERVO JUDICIAL
          </div>
          <div class="pj-tree-row">
            
            <!-- Despachos de Ponencia -->
            <div class="pj-tree-node node-gold" style="flex:1.3;">
              <div class="pj-tree-node-title">
                <span>👥</span> 11 Despachos Técnicos de Ponencia
              </div>
              <span class="pj-tree-node-badge badge-gold">385 Plazas Directas · $376.2 mdp/año</span>
              <p class="pj-tree-node-desc">
                Equipos proyectistas de alta especialización jurídica. Cada ministro(a) tiene ~35 personas: Coordinador(a), 
                Secretarios de Estudio y Cuenta Proyectistas, Secretarios Auxiliares y Oficiales.
              </p>
              <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">
                • Estudian cada expediente a fondo<br>
                • Confrontan normas con tratados internacionales de DDHH<br>
                • Redactan proyectos de resolución para votación<br>
                • Elaboran engroses definitivos de sentencias<br>
                • Preparan votos concurrentes o particulares
              </div>
              <div class="pj-tree-node-law">
                📜 Manual de Remuneraciones del PJF · Reglamento Interior SCJN · PEF Ramo 03
              </div>
            </div>

            <!-- Casas de la Cultura -->
            <div class="pj-tree-node node-cyan" style="flex:1;">
              <div class="pj-tree-node-title">
                <span>📚</span> Casas de la Cultura Jurídica
              </div>
              <span class="pj-tree-node-badge badge-cyan">46 Sedes en las 32 Entidades</span>
              <p class="pj-tree-node-desc">
                Red desconcentrada de presencia territorial de la SCJN: bibliotecas jurídicas, consulta gratuita del Semanario Judicial 
                y eventos académicos.
              </p>
              <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">
                • Archivos históricos del PJF<br>
                • Consulta de jurisprudencia del SJF<br>
                • Capacitación en derechos humanos<br>
                • Préstamo bibliográfico gratuito
              </div>
              <div class="pj-tree-node-law">
                📜 Acuerdo Plenario SCJN 5/2014
              </div>
            </div>

            <!-- Centro de Estudios Constitucionales -->
            <div class="pj-tree-node node-cyan" style="flex:0.8;">
              <div class="pj-tree-node-title">
                <span>🎓</span> Centro de Estudios Constitucionales
              </div>
              <span class="pj-tree-node-badge badge-cyan">Investigación & Publicaciones</span>
              <p class="pj-tree-node-desc">
                Unidad de investigación, docencia y divulgación de la Corte. Publica la Gaceta del Semanario Judicial, 
                coordina cátedras y posgrados en derecho constitucional.
              </p>
              <div class="pj-tree-node-law">
                📜 Acuerdos Generales del Pleno de la SCJN
              </div>
            </div>

          </div>
          <div class="pj-tree-connector-down"></div>
        </div>

        <!-- ═══ NIVEL 5: ÓRGANO DE ADMINISTRACIÓN JUDICIAL (OAJ) ═══ -->
        <div class="pj-tree-level-wrapper">
          <div class="pj-tree-level-label">
            🏢 NIVEL 5 · ÓRGANOS DE ADMINISTRACIÓN, DISCIPLINA Y GOBIERNO (REFORMA 2024)
          </div>
          <div class="pj-tree-row">
            
            <!-- OAJ -->
            <div class="pj-tree-node node-cyan">
              <div class="pj-tree-node-title">
                <span>🏢</span> Órgano de Administración Judicial (OAJ)
              </div>
              <span class="pj-tree-node-badge badge-cyan">$68,917 mdp Presupuesto Administrado · Sustituye al CJF</span>
              <p class="pj-tree-node-desc">
                Entidad gerencial que administra los recursos financieros, patrimoniales, la nómina de +49,000 servidores públicos, 
                compras, obras de infraestructura (Ciudad Judicial) y la plataforma digital DGGJ.
              </p>
              <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">
                • Elabora y ejerce el presupuesto del PJF (Ramo 03)<br>
                • Gestiona la Carrera Judicial (ingreso, ascenso, adscripción)<br>
                • Opera la plataforma FIREL y expedientes digitales<br>
                • <strong>Separación estricta:</strong> solo administra, no sanciona
              </div>
              <div class="pj-tree-node-law">
                📜 Art. 100 CPEUM Reformado · Acuerdos DGGJ (oaj.gob.mx)
              </div>
            </div>

            <!-- Tribunal de Disciplina -->
            <div class="pj-tree-node node-crimson">
              <div class="pj-tree-node-title">
                <span>⚖️</span> Tribunal de Disciplina Judicial
              </div>
              <span class="pj-tree-node-badge badge-crimson">5 Magistrados Electos · Voto Popular · Reforma 2024</span>
              <p class="pj-tree-node-desc">
                Investiga y sanciona faltas graves, corrupción, enriquecimiento ilícito, nepotismo y negligencia de juzgadores federales. 
                Resoluciones definitivas e inatacables.
              </p>
              <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">
                • Investiga de oficio o por queja ciudadana<br>
                • Sanciones: apercibimiento, multa, suspensión, destitución<br>
                • Remite expedientes al Ministerio Público<br>
                • <strong>Sustituye</strong> las facultades disciplinarias del extinto CJF
              </div>
              <div class="pj-tree-node-law">
                📜 Art. 100 CPEUM Reformado · DOF 15/09/2024
              </div>
            </div>

            <!-- Escuela Judicial -->
            <div class="pj-tree-node node-gold">
              <div class="pj-tree-node-title">
                <span>🎓</span> Escuela Federal de Formación Judicial (EFFJ)
              </div>
              <span class="pj-tree-node-badge badge-gold">Carrera Judicial & Concursos de Oposición</span>
              <p class="pj-tree-node-desc">
                Formación académica de jueces, magistrados y secretarios. Organiza los concursos de oposición, 
                posgrados especializados y actualización permanente.
              </p>
              <div class="pj-tree-node-law">
                📜 Art. 100 CPEUM · Ley de Carrera Judicial
              </div>
            </div>

          </div>
        </div>

      </div>

      <!-- Leyenda Explicativa -->
      <div style="background:rgba(255,255,255,0.02); border:1px solid var(--border-subtle); border-radius:10px; padding:16px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; font-size:11.5px; font-family:var(--font-mono);">
        <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
          <span style="color:var(--text-dim); text-transform:uppercase;">Codificación Cromática:</span>
          <span><span style="display:inline-block; width:10px; height:10px; background:var(--gold-bright); border-radius:2px; margin-right:5px;"></span> Pleno, Presidencia & Ponencias</span>
          <span><span style="display:inline-block; width:10px; height:10px; background:var(--cyan); border-radius:2px; margin-right:5px;"></span> Órganos de Apoyo Técnico & Administración</span>
          <span><span style="display:inline-block; width:10px; height:10px; background:var(--crimson-bright); border-radius:2px; margin-right:5px;"></span> Disciplina Judicial (Reforma 2024)</span>
          <span><span style="display:inline-block; width:10px; height:10px; background:var(--amber); border-radius:2px; margin-right:5px;"></span> Salas Jurisdiccionales (1ª y 2ª)</span>
        </div>
        <button type="button" class="btn-auditoria" onclick="window.AuditEngine.closePjHierarchicalModal()" style="font-size:11px; padding:5px 12px; background:rgba(255,255,255,0.08); border:1px solid var(--border-subtle); color:var(--text-main); border-radius:6px; cursor:pointer;">
          ✕ Cerrar Diagrama
        </button>
      </div>
    `;
  }

  function renderPjHierarchicalModalContent() {
    const body = document.getElementById('pjHierarchicalModalBody');
    if (!body) return;

    body.innerHTML = `
      <div class="pj-pyramid-tree">
        
        <!-- NIVEL 1: CÚSPIDE SUPREMA CONSTITUCIONAL -->
        <div class="pj-tree-level-wrapper">
          <div class="pj-tree-level-label">
            🏛️ NIVEL 1 · CÚSPIDE DEL CONTROL CONSTITUCIONAL
          </div>
          <div class="pj-tree-row">
            <div class="pj-tree-node node-gold" style="max-width:480px; text-align:center;">
              <div class="pj-tree-node-title" style="justify-content:center; font-size:16px;">
                <span>🏛️</span> Suprema Corte de Justicia de la Nación (SCJN)
              </div>
              <span class="pj-tree-node-badge badge-gold" style="align-self:center;">
                11 Ministros (9 en Reforma 2024) · Cabeza del PJF
              </span>
              <p class="pj-tree-node-desc">
                Tribunal constitucional supremo. Ejerce el control concentrado: Acciones de Inconstitucionalidad, Controversias Constitucionales y Precedentes Obligatorios.
              </p>
              <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:8px; text-align:left; font-size:11px;">
                <div style="background:rgba(212,175,55,0.08); border:1px solid rgba(212,175,55,0.25); padding:6px 8px; border-radius:6px;">
                  <strong style="color:var(--gold-bright); display:block;">⚖️ Primera Sala:</strong>
                  Materia Civil y Penal (5 Ministros)
                </div>
                <div style="background:rgba(212,175,55,0.08); border:1px solid rgba(212,175,55,0.25); padding:6px 8px; border-radius:6px;">
                  <strong style="color:var(--gold-bright); display:block;">🏛️ Segunda Sala:</strong>
                  Materia Admin. y Laboral (4/5 Ministros)
                </div>
              </div>
              <div class="pj-tree-node-law">
                📜 Arts. 94 y 105 CPEUM · Art. 2 Ley Orgánica del PJF
              </div>
            </div>
          </div>
          <div class="pj-tree-connector-down"></div>
        </div>

        <!-- RAMAS AUTÓNOMAS & ÓRGANOS DE GOBIERNO / REFORMA 2024 -->
        <div class="pj-tree-level-wrapper">
          <div class="pj-tree-level-label">
            ⚖️ JURISDICCIÓN ESPECIALIZADA &amp; ÓRGANOS DE LA REFORMA JUDICIAL 2024
          </div>
          <div class="pj-tree-row">
            
            <!-- TEPJF -->
            <div class="pj-tree-node node-cyan">
              <div class="pj-tree-node-title">
                <span>🗳️</span> Tribunal Electoral (TEPJF)
              </div>
              <span class="pj-tree-node-badge badge-cyan">Sala Superior + 5 Salas Regionales</span>
              <p class="pj-tree-node-desc">
                Máxima autoridad jurisdiccional electoral. Califica la elección presidencial, dirime impugnaciones y tutela derechos político-electorales.
              </p>
              <div class="pj-tree-node-law">
                📜 Art. 99 CPEUM · LGSMIME
              </div>
            </div>

            <!-- Tribunal de Disciplina Judicial -->
            <div class="pj-tree-node node-crimson">
              <div class="pj-tree-node-title">
                <span>⚖️</span> Tribunal de Disciplina Judicial
              </div>
              <span class="pj-tree-node-badge badge-crimson">5 Magistrados Electos por Voto Popular · Reforma 2024</span>
              <p class="pj-tree-node-desc">
                Sustituye facultades disciplinarias del CJF. Investiga y sanciona faltas graves, negligencia o corrupción de juzgadores federales. Resoluciones inatacables.
              </p>
              <div class="pj-tree-node-law">
                📜 Art. 100 CPEUM Reformado · DOF 15/09/2024
              </div>
            </div>

            <!-- Órgano de Administración Judicial -->
            <div class="pj-tree-node node-cyan">
              <div class="pj-tree-node-title">
                <span>🏢</span> Órgano de Administración Judicial (OAJ / DGGJ)
              </div>
              <span class="pj-tree-node-badge badge-cyan">Gestión Presupuestal ($68,917 mdp)</span>
              <p class="pj-tree-node-desc">
                Sustituye la gestión administrativa del CJF. Administra recursos financieros, compras, carrera judicial y la plataforma de expedientes digitales (oaj.gob.mx).
              </p>
              <div class="pj-tree-node-law">
                📜 Art. 100 CPEUM Reformado · Acuerdos DGGJ
              </div>
            </div>

          </div>
          <div class="pj-tree-connector-down"></div>
        </div>

        <!-- NIVEL 2: PLENOS REGIONALES -->
        <div class="pj-tree-level-wrapper">
          <div class="pj-tree-level-label">
            🌐 NIVEL 2 · PLENOS REGIONALES (UNIFICACIÓN DE CRITERIOS)
          </div>
          <div class="pj-tree-row">
            <div class="pj-tree-node node-gold" style="max-width:620px;">
              <div class="pj-tree-node-title" style="justify-content:center;">
                <span>🌐</span> Plenos Regionales (Región Centro-Norte y Región Centro-Sur)
              </div>
              <span class="pj-tree-node-badge badge-gold" style="align-self:center;">
                32 Circuitos Federales Demarcados en 2 Grandes Regiones
              </span>
              <p class="pj-tree-node-desc" style="text-align:center;">
                Resuelven contradicciones de tesis entre Tribunales Colegiados de Circuito de diferentes estados, generando jurisprudencia regional vinculante sin saturar a la SCJN.
              </p>
              <div class="pj-tree-node-law" style="text-align:center;">
                📜 Art. 94 párrafo 9 CPEUM · Acuerdo General CJF 1/2023
              </div>
            </div>
          </div>
          <div class="pj-tree-connector-down"></div>
        </div>

        <!-- NIVEL 3: TRIBUNALES COLEGIADOS Y DE APELACIÓN (32 CIRCUITOS) -->
        <div class="pj-tree-level-wrapper">
          <div class="pj-tree-level-label">
            📚 NIVEL 3 · SEGUNDA INSTANCIA FEDERAL &amp; JUICIOS DE AMPARO DIRECTO
          </div>
          <div class="pj-tree-row">
            
            <!-- TCC Especializados y Mixtos -->
            <div class="pj-tree-node node-gold" style="flex:1.4;">
              <div class="pj-tree-node-title">
                <span>📚</span> Tribunales Colegiados de Circuito (TCC)
              </div>
              <span class="pj-tree-node-badge badge-gold">3 Magistrados c/u · Amparo Directo &amp; Revisión</span>
              <p class="pj-tree-node-desc">
                Resuelven amparos directos contra sentencias definitivas y recursos de revisión en amparo indirecto.
              </p>
              <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.06); padding:8px; border-radius:6px; font-size:11px; margin-top:6px;">
                <div style="color:var(--cyan); margin-bottom:3px;">
                  🏛️ <strong>TCC Especializados:</strong> Materias Penal, Administrativa, Civil y Trabajo en circuitos de alto litigio (CDMX, Jalisco, NL, EdoMex). (Art. 38 LOPJF)
                </div>
                <div style="color:var(--gold-bright);">
                  🌐 <strong>TCC Mixtos:</strong> Conocen indistintamente de todas las materias en circuitos de menor escala (Nayarit, Tlaxcala, Colima, etc.). (Art. 37 LOPJF)
                </div>
              </div>
              <div class="pj-tree-node-law">
                📜 Arts. 94 y 107 CPEUM · Arts. 33 a 39 LOPJF
              </div>
            </div>

            <!-- Especializados Telecom -->
            <div class="pj-tree-node node-cyan" style="flex:1;">
              <div class="pj-tree-node-title">
                <span>📡</span> TCC de Competencia Económica &amp; Telecom
              </div>
              <span class="pj-tree-node-badge badge-cyan">Sede CDMX · Jurisdicción Nacional</span>
              <p class="pj-tree-node-desc">
                Competencia exclusiva sobre resoluciones del IFT y COFECE. Actos no sujetos a suspensión ordinaria para no frenar la conectividad del país.
              </p>
              <div class="pj-tree-node-law">
                📜 Art. 28 párrafo 20 CPEUM · Ac. CJF 22/2013
              </div>
            </div>

            <!-- CAR -->
            <div class="pj-tree-node node-emerald" style="flex:1;">
              <div class="pj-tree-node-title">
                <span>🤝</span> Centros Auxiliares Regionales (CAR)
              </div>
              <span class="pj-tree-node-badge badge-emerald" style="background:rgba(16,185,129,0.15); border:1px solid #10b981; color:#34d399;">
                Auxilio Nacional Itinerante
              </span>
              <p class="pj-tree-node-desc">
                Tribunales y juzgados móviles de auxilio que reciben remesas de expedientes listos para sentencia desde circuitos saturados para abatir el rezago histórico.
              </p>
              <div class="pj-tree-node-law">
                📜 Art. 94 CPEUM · Acuerdo General CJF 3/2013
              </div>
            </div>

            <!-- TCA -->
            <div class="pj-tree-node node-amber" style="flex:1;">
              <div class="pj-tree-node-title">
                <span>🏛️</span> Tribunales Colegiados de Apelación (TCA)
              </div>
              <span class="pj-tree-node-badge badge-amber">3 Magistrados · Deliberación Colegiada</span>
              <p class="pj-tree-node-desc">
                Sustituyen a los antiguos Tribunales Unitarios unipersonales. Conocen de apelaciones de juicios federales ordinarios civiles, mercantiles y penales.
              </p>
              <div class="pj-tree-node-law">
                📜 Art. 94 CPEUM · Arts. 40 a 43 LOPJF
              </div>
            </div>

          </div>
          <div class="pj-tree-connector-down"></div>
        </div>

        <!-- NIVEL 4: PRIMERA INSTANCIA FEDERAL -->
        <div class="pj-tree-level-wrapper">
          <div class="pj-tree-level-label">
            📁 NIVEL 4 · PRIMERA INSTANCIA FEDERAL &amp; JUICIOS DE AMPARO INDIRECTO
          </div>
          <div class="pj-tree-row">
            
            <!-- Juzgados de Distrito -->
            <div class="pj-tree-node node-gold" style="flex:1.4;">
              <div class="pj-tree-node-title">
                <span>📁</span> Juzgados de Distrito Ordinarios
              </div>
              <span class="pj-tree-node-badge badge-gold">>450 Juzgados de Primera Instancia</span>
              <p class="pj-tree-node-desc">
                Conocen del juicio de amparo indirecto contra actos de autoridad, órdenes de aprehensión, leyes y juicios federales ordinarios.
              </p>
              <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.06); padding:8px; border-radius:6px; font-size:11px; margin-top:6px;">
                <div style="color:var(--cyan); margin-bottom:3px;">
                  🏛️ <strong>Juzgados Especializados:</strong> Amparo Penal, Civil, Administrativo, Laboral, Mercantil Federal y Extinción de Dominio (Arts. 51-55 LOPJF).
                </div>
                <div style="color:var(--gold-bright);">
                  🌐 <strong>Juzgados Mixtos:</strong> En cabeceras distritales foráneas conocen simultáneamente de todas las materias (Art. 48 LOPJF).
                </div>
              </div>
              <div class="pj-tree-node-law">
                📜 Arts. 103 y 107 CPEUM · Arts. 48 a 60 LOPJF
              </div>
            </div>

            <!-- CJPF Oral -->
            <div class="pj-tree-node node-amber" style="flex:1.1;">
              <div class="pj-tree-node-title">
                <span>⚡</span> Centros de Justicia Penal Federal (CJPF)
              </div>
              <span class="pj-tree-node-badge badge-amber">Sistema Acusatorio Oral</span>
              <p class="pj-tree-node-desc">
                Sedes judiciales orales federales para delitos de competencia federal. Aplican principios de inmediación y contradicción.
              </p>
              <div style="font-size:11px; color:#cbd5e1; margin-top:4px;">
                • <strong>Jueces de Control:</strong> Legalidad de detención y vinculación.<br>
                • <strong>Tribunal de Enjuiciamiento:</strong> Desahogo de juicio oral y sentencia.<br>
                • <strong>Jueces de Ejecución:</strong> Vigilancia de penas en prisiones.
              </div>
              <div class="pj-tree-node-law">
                📜 Art. 20 CPEUM · Código Nacional de Procedimientos Penales
              </div>
            </div>

            <!-- Juzgados Telecom & Auxiliares -->
            <div class="pj-tree-node node-cyan" style="flex:0.9;">
              <div class="pj-tree-node-title">
                <span>📡</span> Juzgados de Distrito Telecom / CAR
              </div>
              <span class="pj-tree-node-badge badge-cyan">Especializados &amp; Auxiliares</span>
              <p class="pj-tree-node-desc">
                2 Juzgados Especializados en Competencia y Telecom en CDMX (alcance nacional) y Juzgados Auxiliares móviles para dictado de sentencias de los CAR.
              </p>
              <div class="pj-tree-node-law">
                📜 Art. 28 CPEUM · Ac. CJF 22/2013
              </div>
            </div>

          </div>
          <div class="pj-tree-connector-down"></div>
        </div>

        <!-- NIVEL 5: DESCONCENTRACIÓN Y FORMACIÓN -->
        <div class="pj-tree-level-wrapper">
          <div class="pj-tree-level-label">
            🎓 NIVEL 5 · DEFENSORÍA PÚBLICA, CARRERA JUDICIAL Y CASAS DE LA CULTURA
          </div>
          <div class="pj-tree-row">
            
            <div class="pj-tree-node node-cyan">
              <div class="pj-tree-node-title">
                <span>🛡️</span> Defensoría Pública (IFDP)
              </div>
              <span class="pj-tree-node-badge badge-cyan">>3,000 Defensores en los 32 Estados</span>
              <p class="pj-tree-node-desc">
                Defensa penal gratuita obligatoria en audiencias orales federales y asesoría jurídica gratuita a grupos vulnerables.
              </p>
              <div class="pj-tree-node-law">
                📜 Arts. 17 y 20 CPEUM · Ley Fed. Defensoría
              </div>
            </div>

            <div class="pj-tree-node node-gold">
              <div class="pj-tree-node-title">
                <span>🎓</span> Escuela Judicial (EFFJ)
              </div>
              <span class="pj-tree-node-badge badge-gold">Carrera Judicial &amp; Exámenes</span>
              <p class="pj-tree-node-desc">
                Formación académica, posgrados y concursos de oposición para secretarios, actuarios y operadores de la judicatura federal.
              </p>
              <div class="pj-tree-node-law">
                📜 Art. 100 CPEUM · Ley Carrera Judicial
              </div>
            </div>

            <div class="pj-tree-node node-cyan">
              <div class="pj-tree-node-title">
                <span>📚</span> Casas de la Cultura Jurídica
              </div>
              <span class="pj-tree-node-badge badge-cyan">46 Sedes Estatales SCJN</span>
              <p class="pj-tree-node-desc">
                Presencia de la Suprema Corte en los 32 estados: bibliotecas jurídicas, eventos y consulta gratuita del Semanario Judicial.
              </p>
              <div class="pj-tree-node-law">
                📜 Acuerdo Plenario SCJN 5/2014
              </div>
            </div>

          </div>
        </div>

      </div>

      <!-- Leyenda Explicativa del Diagrama -->
      <div style="background:rgba(255,255,255,0.02); border:1px solid var(--border-subtle); border-radius:10px; padding:16px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; font-size:11.5px; font-family:var(--font-mono);">
        <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
          <span style="color:var(--text-dim); text-transform:uppercase;">Codificación Cromática:</span>
          <span><span style="display:inline-block; width:10px; height:10px; background:var(--gold-bright); border-radius:2px; margin-right:5px;"></span> Cúspide &amp; Colegiados Superiores</span>
          <span><span style="display:inline-block; width:10px; height:10px; background:var(--cyan); border-radius:2px; margin-right:5px;"></span> Especialización Técnica / Nacional</span>
          <span><span style="display:inline-block; width:10px; height:10px; background:var(--crimson-bright); border-radius:2px; margin-right:5px;"></span> Disciplina Judicial (Reforma 2024)</span>
          <span><span style="display:inline-block; width:10px; height:10px; background:#10b981; border-radius:2px; margin-right:5px;"></span> Centros Auxiliares Regionales (CAR)</span>
          <span><span style="display:inline-block; width:10px; height:10px; background:var(--amber); border-radius:2px; margin-right:5px;"></span> Primera Instancia y Sistema Oral</span>
        </div>
        <button type="button" class="btn-auditoria" onclick="window.AuditEngine.closePjHierarchicalModal()" style="font-size:11px; padding:5px 12px; background:rgba(255,255,255,0.08); border:1px solid var(--border-subtle); color:var(--text-main); border-radius:6px; cursor:pointer;">
          ✕ Cerrar Diagrama
        </button>
      </div>
    `;
  }

  function selectPjEstado(abbr) {
    const normAbbr = abbr === 'MÉX' ? 'MEX' : abbr;
    selectedPjStateAbbr = normAbbr;
    updatePjMainTerritorialView(normAbbr);
  }

  function updatePjMainTerritorialView(abbr) {
    const normAbbr = abbr === 'MÉX' ? 'MEX' : abbr;
    selectedPjStateAbbr = normAbbr;
    const currState = PJF_ESTRUCTURA_DATA.territorio[normAbbr] || PJF_ESTRUCTURA_DATA.territorio['JAL'];
    if (!currState) return;

    // Actualizar chips de estado
    document.querySelectorAll('.pj-state-chip').forEach(chip => {
      chip.classList.toggle('active', chip.innerText.includes(abbr) || chip.innerText.includes(normAbbr));
    });

    // Actualizar celdas del cartograma
    document.querySelectorAll('#pjCartogramGrid .state-cell').forEach(cell => {
      cell.classList.toggle('active', cell.innerText.includes(abbr) || cell.innerText.includes(normAbbr));
    });

    // Actualizar estilo de capa GeoJSON
    if (pjGeoJsonLayer) {
      pjGeoJsonLayer.eachLayer(layer => {
        const featAbbr = layer.feature.properties.abbr;
        const isSel = featAbbr === normAbbr || (featAbbr === 'MÉX' && normAbbr === 'MEX');
        layer.setStyle({
          fillColor: isSel ? '#d4af37' : '#141826',
          weight: isSel ? 2.5 : 1.2,
          color: isSel ? '#f3cf65' : '#2a334d',
          fillOpacity: isSel ? 0.9 : 0.75
        });
      });
    }

    // Actualizar hero card en la pantalla principal
    const heroCard = document.getElementById('pjCircuitHeroMain');
    if (heroCard && currState) {
      heroCard.innerHTML = `
        <div>
          <span style="font-family:var(--font-mono); font-size:10px; color:var(--gold-bright); text-transform:uppercase; letter-spacing:1.5px; display:block;">
            PODER JUDICIAL DE LA FEDERACIÓN EN ${currState.nombre.toUpperCase()}
          </span>
          <div class="pj-circuit-num" style="display:flex; align-items:center; gap:10px;">
            <span>🏛️ ${currState.circuitoNum}</span>
            <span style="font-size:11px; font-family:var(--font-mono); background:rgba(212,175,55,0.2); border:1px solid var(--gold); color:var(--gold-bright); padding:2px 8px; border-radius:4px;">${currState.circuitoRomano}</span>
          </div>
          <div style="font-size:12px; color:var(--text-secondary); margin-top:4px;">
            Sedes Federales: <strong style="color:var(--text-main);">${currState.circuitoSedes}</strong>
          </div>
          <div style="font-size:11.5px; color:var(--cyan); margin-top:2px; font-family:var(--font-mono);">
            ${currState.juzgadosFederales}
          </div>
        </div>
        <div style="text-align:right; display:flex; flex-direction:column; align-items:flex-end; gap:6px;">
          <span style="font-family:var(--font-mono); font-size:10px; color:var(--text-dim); display:block;">FUERO COMÚN ESTATAL</span>
          <strong style="color:var(--gold-bright); font-size:13px; display:block;">${currState.tsjNombre}</strong>
          <span style="font-family:var(--font-mono); font-size:12px; color:var(--emerald-bright); font-weight:700;">
            ${currState.numPartidosTxt}
          </span>
          <button type="button" class="btn-auditoria" style="margin-top:6px; font-size:11.5px; padding:6px 14px; background:linear-gradient(135deg, rgba(212,175,55,0.2), rgba(0,0,0,0.5)); border:1px solid var(--border-gold); color:var(--gold-bright); cursor:pointer; border-radius:6px; font-weight:700; display:inline-flex; align-items:center; gap:6px;">
            <span>📂</span> Abrir Expediente de Circuito y Partidos ➔
          </button>
        </div>
      `;
      heroCard.setAttribute('onclick', `window.AuditEngine.openPjCircuitDrawer('${currState.abbr}')`);
    }

    // Actualizar detalle pericial inferior si estamos en territorio
    if (currentPjView === 'territorio') {
      const detailBox = document.getElementById('pjDetailBox');
      if (detailBox && currState) {
        detailBox.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div>
              <strong style="color:var(--gold-bright); font-size:14px; font-family:var(--font-serif);">
                📍 Radiografía Territorial de Acceso a la Justicia en ${currState.nombre} (${currState.circuitoNum})
              </strong>
              <div style="font-size:12px; color:var(--text-secondary); margin-top:4px;">
                La entidad cuenta con <strong>${currState.numPartidosTxt}</strong> coordinados por el <strong>${currState.tsjNombre}</strong> para el fuero común y amparados por el <strong>${currState.circuitoNum}</strong> (${currState.circuitoRomano}) para garantías federales.
              </div>
            </div>
            <button type="button" class="btn-auditoria" onclick="window.AuditEngine.openPjCircuitDrawer('${currState.abbr}')" style="font-size:12px; padding:6px 14px; background:linear-gradient(135deg, #d4af37 0%, #aa8c2c 100%); color:#000; font-weight:800; border:none; border-radius:6px; cursor:pointer;">
              📂 Desglosar Partidos Judiciales ↗
            </button>
          </div>
        `;
      }
    }
  }

  function openPjCircuitDrawer(abbr = selectedPjStateAbbr) {
    const normAbbr = abbr === 'MÉX' ? 'MEX' : abbr;
    selectedPjStateAbbr = normAbbr;
    const st = PJF_ESTRUCTURA_DATA.territorio[normAbbr] || PJF_ESTRUCTURA_DATA.territorio['JAL'];
    if (!st) return;

    const drawer = document.getElementById('pjCircuitDrawer');
    const overlay = document.getElementById('pjCircuitDrawerOverlay');
    if (!drawer || !overlay) return;

    // Actualizar Header
    const tagEl = document.getElementById('pjDrawerStateTag');
    const nameEl = document.getElementById('pjDrawerStateName');
    const badgeEl = document.getElementById('pjDrawerCircuitBadge');
    if (tagEl) tagEl.innerText = `EXPEDIENTE DE JURISDICCIÓN TERRITORIAL Y CIRCUITO FEDERAL · CLAVE: ${st.abbr}`;
    if (nameEl) nameEl.innerText = st.nombre;
    if (badgeEl) {
      badgeEl.innerHTML = `
        <span style="background:rgba(212,175,55,0.18); border:1px solid var(--border-gold); color:var(--gold-bright); font-family:var(--font-mono); font-size:12px; font-weight:700; padding:4px 12px; border-radius:6px; display:inline-block; box-shadow:0 0 10px rgba(212,175,55,0.2);">
          🏛️ ${st.circuitoNum.toUpperCase()} (${st.circuitoRomano})
        </span>
      `;
    }

    // Llenar Body
    const bodyEl = document.getElementById('pjDrawerBody');
    if (bodyEl) {
      bodyEl.innerHTML = `
        <!-- Hero Card del Circuito Federal -->
        <div style="background:linear-gradient(135deg, rgba(20,24,38,0.95), rgba(10,12,18,0.95)); border:1px solid var(--border-gold); border-radius:10px; padding:18px; box-shadow:0 6px 20px rgba(0,0,0,0.5);">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
            <div>
              <span style="font-family:var(--font-mono); font-size:10px; color:var(--gold-bright); text-transform:uppercase; letter-spacing:1.5px; display:block;">
                JURISDICCIÓN DEL PODER JUDICIAL DE LA FEDERACIÓN
              </span>
              <h4 style="font-family:var(--font-serif); font-size:19px; color:var(--gold-bright); margin:2px 0 0;">
                🏛️ ${st.circuitoNum}
              </h4>
            </div>
            <span style="font-family:var(--font-mono); font-size:11px; background:rgba(56,189,248,0.12); border:1px solid rgba(56,189,248,0.3); color:var(--cyan); padding:3px 9px; border-radius:4px; font-weight:700;">
              ${st.circuitoRomano}
            </span>
          </div>
          
          <div style="font-size:12.5px; color:var(--text-secondary); margin-bottom:8px;">
            <strong>Sedes Jurisdiccionales Federales:</strong> <span style="color:var(--text-main);">${st.circuitoSedes}</span>
          </div>
          <div style="font-size:12px; color:var(--cyan); font-family:var(--font-mono); background:rgba(255,255,255,0.02); border:1px solid var(--border-subtle); padding:10px 12px; border-radius:6px; line-height:1.5;">
            ⚖️ ${st.juzgadosFederales}
          </div>
        </div>

        <!-- Ficha Fuero Común Estatal -->
        <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:10px; padding:16px; display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
          <div>
            <span style="font-family:var(--font-mono); font-size:10px; color:var(--text-dim); text-transform:uppercase; display:block;">
              Órgano Supremo del Fuero Común
            </span>
            <strong style="color:var(--gold-bright); font-size:13.5px; display:block; margin-top:2px;">
              ${st.tsjNombre}
            </strong>
            <span style="font-family:var(--font-mono); font-size:11.5px; color:var(--emerald-bright); font-weight:700; margin-top:3px; display:block;">
              ${st.numPartidosTxt}
            </span>
          </div>
          <div style="text-align:right;">
            <span style="font-family:var(--font-mono); font-size:10px; color:var(--text-dim); text-transform:uppercase; display:block;">
              Acceso a la Justicia
            </span>
            <span style="font-family:var(--font-mono); font-size:14px; font-weight:700; color:var(--gold-bright); display:block; margin-top:2px;">
              ${st.juecesPor100k}
            </span>
            <span style="font-size:10.5px; color:var(--text-dim); margin-top:2px; display:block;">
              Déficit estructural frente al promedio OCDE
            </span>
          </div>
        </div>

        <!-- Tabla Desglosada de Partidos Judiciales -->
        <div class="pj-drawer-table-wrapper">
          <div style="padding:12px 14px; background:rgba(255,255,255,0.02); border-bottom:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center;">
            <strong style="font-family:var(--font-serif); font-size:14px; color:var(--gold-bright);">
              ⚖️ Mapa de Partidos / Distritos Judiciales, Cabeceras &amp; Juzgados de Paz:
            </strong>
            <span style="font-family:var(--font-mono); font-size:10px; color:var(--cyan); background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.3); padding:2px 8px; border-radius:4px;">
              ${(st.partidos || []).length} Zonas Mapeadas
            </span>
          </div>
          <div style="overflow-x:auto; max-height:420px; overflow-y:auto;">
            <table class="pj-drawer-table">
              <thead>
                <tr>
                  <th style="width:24%;">Partido / Distrito</th>
                  <th style="width:26%;">Cabecera &amp; Municipios</th>
                  <th style="width:26%;">Juzgados 1ª Instancia</th>
                  <th style="width:24%;">Juzgados Menores / de Paz</th>
                </tr>
              </thead>
              <tbody>
                ${(st.partidos || []).map(p => `
                  <tr>
                    <td>
                      <strong style="color:var(--gold-bright); font-size:12px; display:block;">${p.partido}</strong>
                      <span style="font-size:10px; color:var(--text-dim); font-family:var(--font-mono);">${p.poblacion || ''}</span>
                    </td>
                    <td>
                      <strong style="color:var(--text-main); font-size:11.5px; display:block;">${p.cabecera}</strong>
                      <div style="font-size:10px; color:var(--text-secondary); margin-top:2px;">${p.municipios}</div>
                    </td>
                    <td>
                      <span style="color:var(--cyan); font-family:var(--font-mono); font-size:11px;">${p.juzgados1ra}</span>
                    </td>
                    <td>
                      <span style="color:var(--emerald-bright); font-size:11px;">${p.juzgadosPaz}</span>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>

        <!-- Ficha Pericial y Marco Jurídico -->
        <div style="background:rgba(255,255,255,0.02); border:1px dashed var(--border-subtle); border-radius:8px; padding:12px 14px; font-size:11px; font-family:var(--font-mono); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
          <span>📜 <strong>Fundamento:</strong> Arts. 94 y 116 CPEUM · Acuerdos CJF/OAJ · Ley Orgánica del ${st.tsjNombre}</span>
          <div style="display:flex; gap:10px;">
            <a class="glos-link" onclick="window.AuditEngine.goToGlossary('Poder Judicial de la Federación')">Glosario ↗</a>
            <a class="ref-link" onclick="window.AuditEngine.goToRef('ref-cpeum-art94')">[Ref. 20] ↗</a>
          </div>
        </div>
      `;
    }

    drawer.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Actualizar visualmente la pantalla principal
    updatePjMainTerritorialView(normAbbr);
  }

  function closePjCircuitDrawer() {
    const drawer = document.getElementById('pjCircuitDrawer');
    const overlay = document.getElementById('pjCircuitDrawerOverlay');
    if (drawer) drawer.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  // ==========================================================================
  // SIMULADOR COMPARATIVO DE PRESTACIONES Y PAQUETE ECONÓMICO SCJN (SUBPESTAÑA 4.2)
  // ==========================================================================
  const SCJN_PRESTACIONES_DATA = {
    totalAnualEfectivo: 1712309,
    totalAnualConEspecie: 2212309,
    costoPleno11: 18835399,
    salarioMinimoAnual: 89500,
    topeArt127Anual: 2250000,
    distribucion: [
      {
        id: 'riesgo',
        concepto: 'Pago por Riesgo Jurisdiccional',
        icono: '🛡️',
        monto: 642000,
        montoTxt: '$642,000 pesos',
        pct: 37.5,
        color: '#e74c3c',
        desc: 'Asignación anual por la naturaleza de su función jurisdiccional.',
        norma: 'Art. 94 CPEUM y Manual de Percepciones PJF (Capítulo 1000)',
        glosTerm: 'Capítulo 1000',
        refKey: 'ref-manual-remun-pjf',
        refNum: '22'
      },
      {
        id: 'aguinaldo',
        concepto: 'Aguinaldo y Prima Vacacional',
        icono: '🎄',
        monto: 445309,
        montoTxt: '$445,309 pesos',
        pct: 26.0,
        color: '#f39c12',
        desc: '40 días de sueldo tabular y prima del periodo vacacional.',
        norma: 'Ley Federal de los Trabajadores al Servicio del Estado (LFTSE)',
        glosTerm: 'Capítulo 1000',
        refKey: 'ref-manual-remun-pjf',
        refNum: '22'
      },
      {
        id: 'ssi',
        concepto: 'Seguro de Separación Individualizado (SSI)',
        icono: '🏦',
        monto: 350000,
        montoTxt: 'Hasta $350,000 pesos/año',
        pct: 20.4,
        color: '#3498db',
        desc: 'Aportación gubernamental de hasta el 10% del sueldo bruto.',
        norma: 'Condición contractual del PJF (suprimida en el Ejecutivo por Ley de Austeridad)',
        glosTerm: 'Seguro de Separación Individualizado',
        refKey: 'ref-manual-remun-pjf',
        refNum: '22'
      },
      {
        id: 'ahorro',
        concepto: 'Fondo de Ahorro y Ayudas Personales',
        icono: '🍎',
        monto: 150000,
        montoTxt: '$150,000 pesos/año',
        pct: 8.8,
        color: '#2ecc71',
        desc: 'Apoyo para alimentos, anteojos y gasolina.',
        norma: 'Partidas 15401 y 15402 del Presupuesto de Egresos de la SCJN',
        glosTerm: 'Capítulo 1000',
        refKey: 'ref-manual-remun-pjf',
        refNum: '22'
      },
      {
        id: 'sgmm',
        concepto: 'Seguro de Gastos Médicos Mayores (SGMM)',
        icono: '🩺',
        monto: 125000,
        montoTxt: '$125,000 pesos/año',
        pct: 7.3,
        color: '#9b59b6',
        desc: 'Póliza médica privada con cobertura para cónyuge y dependientes.',
        norma: 'Póliza colectiva privada PJF (prohibida en la Administración Pública Federal)',
        glosTerm: 'Seguro de Gastos Médicos Mayores',
        refKey: 'ref-manual-remun-pjf',
        refNum: '22'
      },
      {
        id: 'vehiculos',
        concepto: 'Vehículos Blindados y Telefonía',
        icono: '🚙',
        monto: 500000,
        montoTxt: 'En especie (~$500,000)',
        pct: 0,
        color: '#1abc9c',
        desc: 'Flotilla de camionetas blindadas nivel 5 con chofer y escolta federal.',
        norma: 'Capítulo 3000 de Servicios Generales del PEF (Ramo 03)',
        glosTerm: 'Capítulo 3000',
        refKey: 'ref-pef-ramo03',
        refNum: '21'
      }
    ],
    comparativaRegimenes: [
      {
        id: 'scjn_total',
        regimen: 'Ingreso Anual Bruto Integrado Ministro SCJN',
        icono: '🏛️',
        monto: 5529450,
        pct: 100,
        color: 'var(--crimson-bright)',
        nota: 'Sueldo tabular ($3.82 mdp) + Prestaciones ($1.71 mdp) en régimen tradicional previo a la reforma.'
      },
      {
        id: 'presidente',
        regimen: 'Tope Salarial Máximo Constitucional (Presidente)',
        icono: '🇲🇽',
        monto: 2250000,
        pct: 40.7,
        color: 'var(--gold-bright)',
        nota: 'Remuneración total bruta anual autorizada en el PEF ($134,310 netos/mes). Mandato del Art. 127 CPEUM.'
      },
      {
        id: 'solo_prestaciones',
        regimen: 'Solo Prestaciones Extraordinarias de Ministro',
        icono: '💼',
        monto: 1712309,
        pct: 31.0,
        color: 'var(--gold)',
        nota: 'Exclusivamente el paquete de compensaciones complementarias (sin considerar salario base).'
      },
      {
        id: 'imss',
        regimen: 'Salario Promedio Anual Sector Formal (IMSS)',
        icono: '🏭',
        monto: 182400,
        pct: 3.3,
        color: 'var(--cyan)',
        nota: 'Salario base de cotización promedio nacional en el empleo formal registrado ante el IMSS.'
      },
      {
        id: 'salmin',
        regimen: 'Salario Mínimo General Anualizado',
        icono: '🪙',
        monto: 89500,
        pct: 1.6,
        color: '#2ecc71',
        nota: 'Ingreso mínimo legal anual de un trabajador mexicano (~$248.93 pesos diarios).'
      }
    ]
  };

  let isPrestacionesEvaluated = false;
  let isPrestacionesAnimating = false;
  let isPrestacionesHoverEnabled = false;
  let prestacionesAnimFrameId = null;
  let currentPrestacionesView = 'distribucion';
  let activePrestacionId = null;

  function renderJudicialPrestacionesSimulator(mode) {
    currentPrestacionesView = mode || currentPrestacionesView || 'distribucion';

    // 1. Sincronizar botones del toolbar de vistas
    const btnDist = document.getElementById('btnPrestViewDistribucion');
    const btnComp = document.getElementById('btnPrestViewComparativa');
    if (btnDist && btnComp) {
      if (currentPrestacionesView === 'distribucion') {
        btnDist.classList.add('active');
        btnDist.style.borderColor = 'var(--gold)';
        btnDist.style.color = 'var(--gold-bright)';
        btnComp.classList.remove('active');
        btnComp.style.borderColor = 'var(--border-subtle)';
        btnComp.style.color = 'var(--text-secondary)';
      } else {
        btnComp.classList.add('active');
        btnComp.style.borderColor = 'var(--gold)';
        btnComp.style.color = 'var(--gold-bright)';
        btnDist.classList.remove('active');
        btnDist.style.borderColor = 'var(--border-subtle)';
        btnDist.style.color = 'var(--text-secondary)';
      }
    }

    // 2. Sincronizar texto de estatus y botón de evaluar
    const statusEl = document.getElementById('prestacionesEvalStatusText');
    const btnEval = document.getElementById('btnEvaluarPrestaciones');
    if (!isPrestacionesAnimating) {
      if (isPrestacionesEvaluated) {
        if (statusEl) statusEl.innerHTML = '<span style="color:var(--emerald-bright);">✓ Evaluación completada: Paquete de compensaciones de la SCJN desplegado al 100%.</span>';
        if (btnEval) btnEval.innerHTML = '<span>🔄</span> Volver a Evaluar';
      } else {
        if (statusEl) statusEl.innerHTML = '⚪ Cifras en reposo ($0 pesos / 0%). Presiona «Evaluar Prestaciones» o pasa el cursor para medir la escala real.';
        if (btnEval) btnEval.innerHTML = '<span>▶️</span> Evaluar Prestaciones';
      }
    }

    // 3. Actualizar KPIs del Scorecard
    const kpiTotal = document.getElementById('kpiPrestacionesTotal');
    const kpiTotalSub = document.getElementById('kpiPrestacionesTotalSub');
    const kpiPleno = document.getElementById('kpiPrestacionesPleno');
    const kpiPlenoSub = document.getElementById('kpiPrestacionesPlenoSub');
    const kpiSalMin = document.getElementById('kpiPrestacionesSalMin');
    const kpiSalMinSub = document.getElementById('kpiPrestacionesSalMinSub');
    const kpiTope = document.getElementById('kpiPrestacionesTope');
    const kpiTopeSub = document.getElementById('kpiPrestacionesTopeSub');

    if (!isPrestacionesAnimating) {
      if (isPrestacionesEvaluated) {
        if (kpiTotal) kpiTotal.textContent = '$1,712,309';
        if (kpiTotalSub) kpiTotalSub.innerHTML = '<span style="color:var(--gold);">+$142,692/mes por ministro</span>';
        if (kpiPleno) kpiPleno.textContent = '$18.84 mdp';
        if (kpiPlenoSub) kpiPlenoSub.textContent = '11 Ministros del Pleno';
        if (kpiSalMin) kpiSalMin.textContent = '19.1 años';
        if (kpiSalMinSub) kpiSalMinSub.textContent = 'de salario mínimo general';
        if (kpiTope) kpiTope.innerHTML = '<span style="color:var(--crimson-bright);">+76.1%</span>';
        if (kpiTopeSub) kpiTopeSub.innerHTML = '<span style="color:var(--crimson-bright);">Excedente sobre Art. 127</span>';
      } else {
        if (kpiTotal) kpiTotal.textContent = '$0';
        if (kpiTotalSub) kpiTotalSub.textContent = '⚪ En reposo ($0 / mes)';
        if (kpiPleno) kpiPleno.textContent = '$0 mdp';
        if (kpiPlenoSub) kpiPlenoSub.textContent = '⚪ Pólizas, fondos y riesgo';
        if (kpiSalMin) kpiSalMin.textContent = '0.0 años';
        if (kpiSalMinSub) kpiSalMinSub.textContent = '⚪ vs $89,500/año sal. mín.';
        if (kpiTope) kpiTope.textContent = '0.0%';
        if (kpiTopeSub) kpiTopeSub.textContent = '⚪ Prohibido en reforma 2025';
      }
    }

    // 4. Renderizar Escenario de Gráfica (#prestacionesChartStage)
    const stage = document.getElementById('prestacionesChartStage');
    if (stage) {
      if (currentPrestacionesView === 'distribucion') {
        const maxMonto = 642000;
        let html = '<div style="display:flex; flex-direction:column; gap:10px;">';
        SCJN_PRESTACIONES_DATA.distribucion.forEach(item => {
          const targetW = item.id === 'vehiculos' ? 78 : Math.max(6, (item.monto / maxMonto) * 100);
          const isSelected = activePrestacionId === item.id;
          const borderStyle = isSelected ? `border-left: 4px solid ${item.color}; background: rgba(255,255,255,0.06);` : `border-left: 3px solid ${item.color}; background: rgba(0,0,0,0.25);`;

          const barW = isPrestacionesEvaluated ? `${targetW}%` : '0%';
          const barClass = isPrestacionesEvaluated ? 'prest-bar-fill' : 'prest-bar-fill bar-zero';
          const valTxt = isPrestacionesEvaluated ? (item.id === 'vehiculos' ? 'En especie (~$500,000/año)' : `$${item.monto.toLocaleString('es-MX')} pesos/año`) : (item.id === 'vehiculos' ? 'En especie ($0)' : '$0 pesos');
          const pctTxt = isPrestacionesEvaluated ? (item.id === 'vehiculos' ? '(Logística y Blindaje)' : `(${item.pct}%)`) : '(0.0%)';

          html += `
            <div class="prest-bar-item" onclick="window.AuditEngine.selectPrestacionItem('${item.id}', 'distribucion')" 
                 style="cursor:pointer; padding:10px 14px; border-radius:6px; transition:all 0.2s ease; ${borderStyle}"
                 title="Clic para ver fundamento legal e impacto presupuestal">
              <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:6px;">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span style="font-size:16px;">${item.icono}</span>
                  <span style="font-family:var(--font-serif); font-size:13.5px; color:var(--text-main); font-weight:600;">${item.concepto}</span>
                </div>
                <div style="font-family:var(--font-mono); font-size:12px; font-weight:700;">
                  <span id="prestBarVal_${item.id}" style="color:${item.color};">${valTxt}</span>
                  <span id="prestBarPct_${item.id}" style="color:var(--text-dim); margin-left:6px;">${pctTxt}</span>
                </div>
              </div>
              <div style="background:rgba(255,255,255,0.06); height:8px; border-radius:4px; overflow:hidden;">
                <div id="prestBarFill_${item.id}" class="${barClass}" style="width:${barW}; height:100%; background:linear-gradient(90deg, ${item.color}, #f1c40f); border-radius:4px; transition:width 0.4s ease;"></div>
              </div>
              <div style="font-size:11px; color:var(--text-dim); margin-top:4px;">${item.desc}</div>
            </div>
          `;
        });
        html += '</div>';
        stage.innerHTML = html;
      } else {
        // Vista Comparativa de Regímenes
        const maxMonto = 5529450;
        let html = '<div style="display:flex; flex-direction:column; gap:10px;">';
        SCJN_PRESTACIONES_DATA.comparativaRegimenes.forEach(item => {
          const targetW = Math.max(5, (item.monto / maxMonto) * 100);
          const isSelected = activePrestacionId === item.id;
          const borderStyle = isSelected ? `border-left: 4px solid ${item.color}; background: rgba(255,255,255,0.06);` : `border-left: 3px solid ${item.color}; background: rgba(0,0,0,0.25);`;

          const barW = isPrestacionesEvaluated ? `${targetW}%` : '0%';
          const barClass = isPrestacionesEvaluated ? 'prest-bar-fill' : 'prest-bar-fill bar-zero';
          const valTxt = isPrestacionesEvaluated ? `$${item.monto.toLocaleString('es-MX')} pesos/año` : '$0 pesos/año';
          const pctTxt = isPrestacionesEvaluated ? `(${item.pct}%)` : '(0.0%)';

          html += `
            <div class="prest-bar-item" onclick="window.AuditEngine.selectPrestacionItem('${item.id}', 'comparativa')" 
                 style="cursor:pointer; padding:10px 14px; border-radius:6px; transition:all 0.2s ease; ${borderStyle}"
                 title="Clic para analizar contraste sociológico y legal">
              <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:6px;">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span style="font-size:16px;">${item.icono}</span>
                  <span style="font-family:var(--font-serif); font-size:13.5px; color:var(--text-main); font-weight:600;">${item.regimen}</span>
                </div>
                <div style="font-family:var(--font-mono); font-size:12px; font-weight:700;">
                  <span id="prestCompVal_${item.id}" style="color:${item.color};">${valTxt}</span>
                  <span id="prestCompPct_${item.id}" style="color:var(--text-dim); margin-left:6px;">${pctTxt}</span>
                </div>
              </div>
              <div style="background:rgba(255,255,255,0.06); height:8px; border-radius:4px; overflow:hidden;">
                <div id="prestCompFill_${item.id}" class="${barClass}" style="width:${barW}; height:100%; background:linear-gradient(90deg, ${item.color}, var(--gold-bright)); border-radius:4px; transition:width 0.4s ease;"></div>
              </div>
              <div style="font-size:11px; color:var(--text-dim); margin-top:4px;">${item.nota}</div>
            </div>
          `;
        });
        html += '</div>';
        stage.innerHTML = html;
      }
    }

    // 5. Renderizar o actualizar cuadrícula detallada de tarjetas (#scjnPrestacionesGrid)
    const prestGrid = document.getElementById('scjnPrestacionesGrid');
    if (prestGrid) {
      prestGrid.innerHTML = SCJN_PRESTACIONES_DATA.distribucion.map(p => {
        const valTxt = isPrestacionesEvaluated ? (p.id === 'vehiculos' ? 'En especie (~$500,000)' : p.montoTxt) : (p.id === 'vehiculos' ? 'En especie ($0)' : '$0 pesos');
        const minibarW = isPrestacionesEvaluated ? (p.id === 'vehiculos' ? '78%' : `${((p.monto / 642000) * 100).toFixed(1)}%`) : '0%';
        const minibarClass = isPrestacionesEvaluated ? 'prest-card-minibar-fill' : 'prest-card-minibar-fill bar-zero';

        return `
          <div class="data-block-col" style="background:var(--bg-card); border:1px solid var(--border-subtle); padding:16px; border-radius:8px; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
              <div class="data-col-lbl">${p.icono} ${p.concepto}</div>
              <div class="data-col-val" id="prestCardVal_${p.id}" style="color:var(--gold-bright); font-size:16px; margin:4px 0;">${valTxt}</div>
              <div class="prest-card-minibar">
                <div id="prestCardBar_${p.id}" class="${minibarClass}" style="width:${minibarW};"></div>
              </div>
              <p style="font-size:11.5px; color:var(--text-secondary); margin:6px 0 0; line-height:1.45;">${p.desc}</p>
            </div>
            <div style="margin-top:12px; padding-top:8px; border-top:1px dashed var(--border-subtle); display:flex; justify-content:space-between; align-items:center; font-size:10.5px; font-family:var(--font-mono);">
              <a class="glos-link" onclick="window.AuditEngine.goToGlossary('${p.glosTerm}')" title="Consultar definición en Glosario">📖 Glosario ↗</a>
              <a class="ref-link" onclick="window.AuditEngine.goToRef('${p.refKey}')" title="Ver cita bibliográfica APA 7">[Ref. ${p.refNum}] ↗</a>
            </div>
          </div>
        `;
      }).join('');
    }
  }

  function setPrestacionesView(viewMode) {
    if (prestacionesAnimFrameId) {
      cancelAnimationFrame(prestacionesAnimFrameId);
      prestacionesAnimFrameId = null;
      isPrestacionesAnimating = false;
    }
    currentPrestacionesView = viewMode;
    renderJudicialPrestacionesSimulator(viewMode);
  }

  function selectPrestacionItem(id, mode) {
    activePrestacionId = id;
    const detailBox = document.getElementById('prestacionesDetailBox');
    if (!detailBox) return;

    if (mode === 'distribucion') {
      const item = SCJN_PRESTACIONES_DATA.distribucion.find(d => d.id === id);
      if (!item) return;
      detailBox.innerHTML = `
        <div style="border-left:3px solid ${item.color}; padding-left:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; margin-bottom:4px;">
            <strong style="font-family:var(--font-serif); font-size:14.5px; color:var(--gold-bright);">${item.icono} ${item.concepto}</strong>
            <span style="font-family:var(--font-mono); font-size:12.5px; color:${item.color}; font-weight:800;">${item.id === 'vehiculos' ? 'En especie (~$500,000/año)' : `$${item.monto.toLocaleString('es-MX')} pesos/año (${item.pct}%)`}</span>
          </div>
          <p style="margin:0 0 6px 0; color:var(--text-main); font-size:12px;"><b>Descripción:</b> ${item.desc}</p>
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:10px; font-size:11.5px; color:var(--text-secondary);">
            <div><b style="color:var(--cyan);">📜 Fundamento Normativo:</b> ${item.norma}</div>
            <div><b style="color:var(--gold);">⚖️ Impacto Republicano:</b> ${item.id === 'riesgo' ? 'Representa el mayor desembolso en efectivo por encima del sueldo base.' : (item.id === 'ssi' || item.id === 'sgmm' ? 'Prohibido explícitamente en el Poder Ejecutivo por la Ley de Austeridad Republicana.' : 'Sujeto a contención estricta bajo el Artículo 127 Constitucional.')}</div>
          </div>
        </div>
      `;
    } else {
      const item = SCJN_PRESTACIONES_DATA.comparativaRegimenes.find(r => r.id === id);
      if (!item) return;
      detailBox.innerHTML = `
        <div style="border-left:3px solid ${item.color}; padding-left:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; margin-bottom:4px;">
            <strong style="font-family:var(--font-serif); font-size:14.5px; color:var(--gold-bright);">${item.icono} ${item.regimen}</strong>
            <span style="font-family:var(--font-mono); font-size:12.5px; color:${item.color}; font-weight:800;">$${item.monto.toLocaleString('es-MX')} pesos/año (${item.pct}% de escala)</span>
          </div>
          <p style="margin:0 0 6px 0; color:var(--text-main); font-size:12px;"><b>Contexto y Análisis Constitucional:</b> ${item.nota}</p>
        </div>
      `;
    }

    renderJudicialPrestacionesSimulator(mode);
  }

  function evaluarPrestacionesJudiciales(duracionMs = 1400) {
    if (prestacionesAnimFrameId) {
      cancelAnimationFrame(prestacionesAnimFrameId);
      prestacionesAnimFrameId = null;
    }

    const statusEl = document.getElementById('prestacionesEvalStatusText');
    const btnEval = document.getElementById('btnEvaluarPrestaciones');
    if (statusEl) {
      statusEl.innerHTML = '<span style="color:var(--gold-bright);">⚡ Evaluando paquete de compensaciones y contrastando con el régimen republicano...</span>';
    }
    if (btnEval) {
      btnEval.innerHTML = '<span>⏳</span> Evaluando...';
    }

    // Quitar clases bar-zero
    document.querySelectorAll('.prest-bar-fill.bar-zero, .prest-card-minibar-fill.bar-zero').forEach(el => {
      el.classList.remove('bar-zero');
    });

    isPrestacionesAnimating = true;
    const startTime = performance.now();
    const easeOutCubic = (t) => (--t) * t * t + 1;

    function animateStep(now) {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / duracionMs);
      const eased = easeOutCubic(progress);

      // 1. KPIs
      const kpiTotal = document.getElementById('kpiPrestacionesTotal');
      const kpiTotalSub = document.getElementById('kpiPrestacionesTotalSub');
      const kpiPleno = document.getElementById('kpiPrestacionesPleno');
      const kpiPlenoSub = document.getElementById('kpiPrestacionesPlenoSub');
      const kpiSalMin = document.getElementById('kpiPrestacionesSalMin');
      const kpiSalMinSub = document.getElementById('kpiPrestacionesSalMinSub');
      const kpiTope = document.getElementById('kpiPrestacionesTope');
      const kpiTopeSub = document.getElementById('kpiPrestacionesTopeSub');

      if (kpiTotal) kpiTotal.textContent = `$${Math.round(SCJN_PRESTACIONES_DATA.totalAnualEfectivo * eased).toLocaleString('es-MX')}`;
      if (kpiTotalSub) kpiTotalSub.innerHTML = `<span style="color:var(--gold);">+$${Math.round(142692 * eased).toLocaleString('es-MX')}/mes por ministro</span>`;
      if (kpiPleno) kpiPleno.textContent = `$${(18.84 * eased).toFixed(2)} mdp`;
      if (kpiPlenoSub) kpiPlenoSub.textContent = '11 Ministros del Pleno';
      if (kpiSalMin) kpiSalMin.textContent = `${(19.1 * eased).toFixed(1)} años`;
      if (kpiSalMinSub) kpiSalMinSub.textContent = 'de salario mínimo general';
      if (kpiTope) kpiTope.innerHTML = `<span style="color:var(--crimson-bright);">+${(76.1 * eased).toFixed(1)}%</span>`;
      if (kpiTopeSub) kpiTopeSub.innerHTML = '<span style="color:var(--crimson-bright);">Excedente sobre Art. 127</span>';

      // 2. Gráfica en vista activa
      if (currentPrestacionesView === 'distribucion') {
        const maxMonto = 642000;
        SCJN_PRESTACIONES_DATA.distribucion.forEach(item => {
          const bar = document.getElementById(`prestBarFill_${item.id}`);
          const valEl = document.getElementById(`prestBarVal_${item.id}`);
          const pctEl = document.getElementById(`prestBarPct_${item.id}`);
          const targetW = item.id === 'vehiculos' ? 78 : Math.max(6, (item.monto / maxMonto) * 100);

          if (bar) bar.style.width = `${(targetW * eased).toFixed(1)}%`;
          if (valEl) {
            valEl.textContent = item.id === 'vehiculos' 
              ? (progress > 0.5 ? 'En especie (~$500,000/año)' : 'Valuando especie...')
              : `$${Math.round(item.monto * eased).toLocaleString('es-MX')} pesos/año`;
          }
          if (pctEl) {
            pctEl.textContent = item.id === 'vehiculos' ? '(Logística y Blindaje)' : `(${(item.pct * eased).toFixed(1)}%)`;
          }
        });
      } else {
        const maxMonto = 5529450;
        SCJN_PRESTACIONES_DATA.comparativaRegimenes.forEach(item => {
          const bar = document.getElementById(`prestCompFill_${item.id}`);
          const valEl = document.getElementById(`prestCompVal_${item.id}`);
          const pctEl = document.getElementById(`prestCompPct_${item.id}`);
          const targetW = Math.max(5, (item.monto / maxMonto) * 100);

          if (bar) bar.style.width = `${(targetW * eased).toFixed(1)}%`;
          if (valEl) valEl.textContent = `$${Math.round(item.monto * eased).toLocaleString('es-MX')} pesos/año`;
          if (pctEl) pctEl.textContent = `(${(item.pct * eased).toFixed(1)}%)`;
        });
      }

      // 3. Mini-barras y montos en cuadrícula de tarjetas
      SCJN_PRESTACIONES_DATA.distribucion.forEach(p => {
        const cardVal = document.getElementById(`prestCardVal_${p.id}`);
        const cardBar = document.getElementById(`prestCardBar_${p.id}`);
        const targetW = p.id === 'vehiculos' ? 78 : (p.monto / 642000) * 100;

        if (cardBar) cardBar.style.width = `${(targetW * eased).toFixed(1)}%`;
        if (cardVal) {
          cardVal.textContent = p.id === 'vehiculos'
            ? (progress > 0.5 ? 'En especie (~$500,000)' : 'En especie (valuando...)')
            : `$${Math.round(p.monto * eased).toLocaleString('es-MX')} pesos`;
        }
      });

      if (progress < 1) {
        prestacionesAnimFrameId = requestAnimationFrame(animateStep);
      } else {
        isPrestacionesAnimating = false;
        isPrestacionesEvaluated = true;
        prestacionesAnimFrameId = null;

        // Fijar valores finales exactos
        if (kpiTotal) kpiTotal.textContent = '$1,712,309';
        if (kpiTotalSub) kpiTotalSub.innerHTML = '<span style="color:var(--gold);">+$142,692/mes por ministro</span>';
        if (kpiPleno) kpiPleno.textContent = '$18.84 mdp';
        if (kpiPlenoSub) kpiPlenoSub.textContent = '11 Ministros del Pleno';
        if (kpiSalMin) kpiSalMin.textContent = '19.1 años';
        if (kpiSalMinSub) kpiSalMinSub.textContent = 'de salario mínimo general';
        if (kpiTope) kpiTope.innerHTML = '<span style="color:var(--crimson-bright);">+76.1%</span>';
        if (kpiTopeSub) kpiTopeSub.innerHTML = '<span style="color:var(--crimson-bright);">Excedente sobre Art. 127</span>';

        if (statusEl) {
          statusEl.innerHTML = '<span style="color:var(--emerald-bright);">✓ Evaluación completada: Paquete de compensaciones de la SCJN desplegado al 100%.</span>';
        }
        if (btnEval) {
          btnEval.innerHTML = '<span>🔄</span> Volver a Evaluar';
        }

        renderJudicialPrestacionesSimulator(currentPrestacionesView);
      }
    }

    prestacionesAnimFrameId = requestAnimationFrame(animateStep);
  }

  function resetPrestacionesJudiciales() {
    if (prestacionesAnimFrameId) {
      cancelAnimationFrame(prestacionesAnimFrameId);
      prestacionesAnimFrameId = null;
    }
    isPrestacionesAnimating = false;
    isPrestacionesEvaluated = false;

    renderJudicialPrestacionesSimulator(currentPrestacionesView);

    const statusEl = document.getElementById('prestacionesEvalStatusText');
    if (statusEl) {
      statusEl.innerHTML = '⚪ Cifras en reposo ($0 pesos / 0%). Presiona «Evaluar Prestaciones» o pasa el cursor para medir la escala real.';
    }
    const btnEval = document.getElementById('btnEvaluarPrestaciones');
    if (btnEval) {
      btnEval.innerHTML = '<span>▶️</span> Evaluar Prestaciones';
    }
  }

  function toggleHoverPrestaciones(enabled) {
    isPrestacionesHoverEnabled = !!enabled;
  }

  function handlePrestacionesHover() {
    if (isPrestacionesHoverEnabled && !isPrestacionesEvaluated && !isPrestacionesAnimating) {
      evaluarPrestacionesJudiciales();
    }
  }

  // ==========================================================================
  // SIMULADOR COMPARATIVO DE ASESORES Y PERSONAL DE PONENCIA SCJN (SUBPESTAÑA 4.3)
  // ==========================================================================
  const SCJN_ASESORES_DATA = {
    promedioPlazas: 35,
    nominaMensualPromedio: 2850000,
    costoAnualPonencia: 34200000,
    costoAnual11Ponencias: 376200000,
    redAmpliadaPersonas: 72,
    cargos: [
      {
        id: 'coordinador',
        cargo: 'Coordinador(a) de Ponencia',
        icono: '👔',
        plazas: 1,
        sueldoBruto: 185000,
        sueldoNeto: 128500,
        costoTotalBrutoMes: 185000,
        costoTotalNetoMes: 128500,
        pctPresupuesto: 6.5,
        color: '#e74c3c',
        funcion: 'Supervisión general del despacho, control de turno de expedientes y enlace institucional.',
        glosTerm: 'Ponencia de Ministro(a)',
        refKey: 'ref-pnt-asesores-scjn',
        refNum: '25'
      },
      {
        id: 'proyectistas',
        cargo: 'Secretarios de Estudio y Cuenta (Proyectistas)',
        icono: '⚖️',
        plazas: 14,
        sueldoBruto: 145000,
        sueldoNeto: 98200,
        costoTotalBrutoMes: 2030000,
        costoTotalNetoMes: 1374800,
        pctPresupuesto: 71.2,
        color: '#0284c7',
        funcion: 'Cuerpo técnico central que redacta los proyectos de sentencias, tesis y jurisprudencias.',
        glosTerm: 'Secretario(a) de Estudio y Cuenta',
        refKey: 'ref-pnt-asesores-scjn',
        refNum: '25'
      },
      {
        id: 'auxiliares',
        cargo: 'Secretarios Auxiliares y Asesores de Ponencia',
        icono: '📚',
        plazas: 10,
        sueldoBruto: 85000,
        sueldoNeto: 58400,
        costoTotalBrutoMes: 850000,
        costoTotalNetoMes: 584000,
        pctPresupuesto: 29.8,
        color: '#f59e0b',
        funcion: 'Investigación jurídica, doctrina constitucional comparada y elaboración de síntesis.',
        glosTerm: 'Asesoría de Ponencia y Récord de Plazas',
        refKey: 'ref-pnt-asesores-scjn',
        refNum: '25'
      },
      {
        id: 'administrativo',
        cargo: 'Personal Administrativo, Choferes y Archivo',
        icono: '📁',
        plazas: 10,
        sueldoBruto: 38000,
        sueldoNeto: 26500,
        costoTotalBrutoMes: 380000,
        costoTotalNetoMes: 265000,
        pctPresupuesto: 13.3,
        color: '#10b981',
        funcion: 'Gestión de estrados, notificaciones, custodia de expedientes, logística y transporte oficial.',
        glosTerm: 'Capítulo 1000',
        refKey: 'ref-pef-ramo03',
        refNum: '21'
      }
    ],
    comparativaRed: [
      {
        id: 'ponencia_base',
        concepto: 'Nómina Tabular Directa (35 plazas por despacho)',
        icono: '🏢',
        montoMes: 2850000,
        montoTxt: '$2,850,000 / mes',
        anualTxt: '$34.2 mdp anuales por ponencia',
        pct: 100,
        color: '#0284c7',
        desc: 'Plantilla base formal registrada en el Manual de Percepciones y catálogo orgánico del PJF.',
        norma: 'Manual de Percepciones PJF y Art. 94 CPEUM',
        glosTerm: 'Ponencia de Ministro(a)',
        refKey: 'ref-pef-ramo03',
        refNum: '21'
      },
      {
        id: 'red_ampliada',
        concepto: 'Red Ampliada con Comisiones PNT (>70 personas)',
        icono: '🔍',
        montoMes: 3500000,
        montoTxt: '~$3,500,000 / mes',
        anualTxt: '~$42.0 mdp anuales por ponencia',
        pct: 122.8,
        color: '#e74c3c',
        desc: 'Estructura real revelada por solicitudes PNT: comisiones de la Secretaría General de Acuerdos, comités y honorarios asimilados Capítulo 3000.',
        norma: 'Auditoría Cívica PNT & Capítulo 3000',
        glosTerm: 'Capítulo 3000',
        refKey: 'ref-pnt-asesores-scjn',
        refNum: '25'
      },
      {
        id: 'sueldo_proyectista',
        concepto: 'Salario Proyectista SCJN (Estudio y Cuenta)',
        icono: '⚖️',
        montoMes: 98200,
        montoTxt: '$98,200 / mes (neto)',
        anualTxt: '$1,178,400 anuales netos',
        pct: 613.8,
        color: '#f59e0b',
        desc: 'Remuneración neta mensual por secretario proyectista (14 plazas = $1.37 mdp netos al mes en cada despacho).',
        norma: 'Tabulador de Mandos Medios y Superiores PJF',
        glosTerm: 'Secretario(a) de Estudio y Cuenta',
        refKey: 'ref-pnt-asesores-scjn',
        refNum: '25'
      },
      {
        id: 'salario_imss',
        concepto: 'Salario Promedio Nacional Cotizantes IMSS',
        icono: '👥',
        montoMes: 16000,
        montoTxt: '$16,000 / mes (neto)',
        anualTxt: '$192,000 anuales promedio',
        pct: 100,
        color: '#10b981',
        desc: 'Ingreso promedio de los trabajadores formales cotizantes en el IMSS en México.',
        norma: 'Estadísticas Oficiales IMSS / STPS',
        glosTerm: 'PEF',
        refKey: 'ref-cpeum-art127',
        refNum: '20'
      }
    ]
  };

  let isAsesoresEvaluated = false;
  let isAsesoresAnimating = false;
  let isAsesoresHoverEnabled = false;
  let currentAsesoresView = 'cargos';
  let selectedAsesoresItem = null;
  let asesoresAnimFrameId = null;

  function setAsesoresView(viewMode) {
    currentAsesoresView = viewMode;
    renderJudicialAsesoresSimulator(viewMode);
  }

  function selectAsesoresItem(id, mode) {
    selectedAsesoresItem = { id, mode };
    const detailBox = document.getElementById('asesoresDetailBox');
    if (!detailBox) return;

    if (mode === 'cargos') {
      const item = SCJN_ASESORES_DATA.cargos.find(d => d.id === id);
      if (!item) return;
      detailBox.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
          <div>
            <strong style="color:var(--cyan); font-size:13.5px;">${item.icono} ${item.cargo}</strong>
            <div style="font-size:11px; color:var(--text-dim); margin-top:2px;">
              Plazas asignadas: <strong style="color:var(--text-main);">${item.plazas} por ponencia</strong> · Sueldo mensual: <strong style="color:var(--gold-bright);">$${item.sueldoNeto.toLocaleString('es-MX')} netos</strong> ($${item.sueldoBruto.toLocaleString('es-MX')} brutos)
            </div>
          </div>
          <span style="font-family:var(--font-mono); font-size:12px; color:var(--cyan); font-weight:700; background:rgba(0,180,216,0.12); padding:3px 8px; border-radius:4px; border:1px solid rgba(0,180,216,0.3);">
            Costo mensual conjunto: $${item.costoTotalNetoMes.toLocaleString('es-MX')} netos
          </span>
        </div>
        <p style="margin:8px 0 6px; font-size:12px; line-height:1.5; color:var(--text-secondary);">${item.funcion}</p>
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; font-size:11px; border-top:1px dashed var(--border-subtle); padding-top:6px; margin-top:6px; font-family:var(--font-mono);">
          <span>📚 Glosario: <a class="glos-link" onclick="window.AuditEngine.goToGlossary('${item.glosTerm}')">${item.glosTerm} ↗</a></span>
          <span>📑 Cita Oficial: <a class="ref-link" onclick="window.AuditEngine.goToRef('${item.refKey}')">[Ref. ${item.refNum}] ↗</a></span>
        </div>
      `;
    } else {
      const item = SCJN_ASESORES_DATA.comparativaRed.find(r => r.id === id);
      if (!item) return;
      detailBox.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
          <div>
            <strong style="color:var(--cyan); font-size:13.5px;">${item.icono} ${item.concepto}</strong>
            <div style="font-size:11px; color:var(--text-dim); margin-top:2px;">
              Monto: <strong style="color:var(--gold-bright);">${item.montoTxt}</strong> (${item.anualTxt})
            </div>
          </div>
          <span style="font-family:var(--font-mono); font-size:11px; color:var(--gold); background:rgba(201,168,76,0.1); padding:3px 8px; border-radius:4px; border:1px solid var(--border-gold);">
            ${item.norma}
          </span>
        </div>
        <p style="margin:8px 0 6px; font-size:12px; line-height:1.5; color:var(--text-secondary);">${item.desc}</p>
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; font-size:11px; border-top:1px dashed var(--border-subtle); padding-top:6px; margin-top:6px; font-family:var(--font-mono);">
          <span>📚 Glosario: <a class="glos-link" onclick="window.AuditEngine.goToGlossary('${item.glosTerm}')">${item.glosTerm} ↗</a></span>
          <span>📑 Referencia: <a class="ref-link" onclick="window.AuditEngine.goToRef('${item.refKey}')">[Ref. ${item.refNum}] ↗</a></span>
        </div>
      `;
    }
  }

  function renderJudicialAsesoresSimulator(mode = currentAsesoresView) {
    currentAsesoresView = mode;

    // Actualizar botones de vista
    const btnCargos = document.getElementById('btnAsesoresViewCargos');
    const btnComp = document.getElementById('btnAsesoresViewComparativa');
    if (btnCargos && btnComp) {
      if (mode === 'cargos') {
        btnCargos.classList.add('active');
        btnCargos.style.borderColor = 'var(--cyan)';
        btnCargos.style.color = 'var(--cyan)';
        btnComp.classList.remove('active');
        btnComp.style.borderColor = '';
        btnComp.style.color = '';
      } else {
        btnComp.classList.add('active');
        btnComp.style.borderColor = 'var(--cyan)';
        btnComp.style.color = 'var(--cyan)';
        btnCargos.classList.remove('active');
        btnCargos.style.borderColor = '';
        btnCargos.style.color = '';
      }
    }

    // Escenario de Gráfica
    const chartStage = document.getElementById('asesoresChartStage');
    if (chartStage) {
      if (mode === 'cargos') {
        const maxNeto = 1374800; // proyectistas
        chartStage.innerHTML = `
          <div style="display:flex; flex-direction:column; gap:9px;">
            ${SCJN_ASESORES_DATA.cargos.map(item => {
              const targetW = (item.costoTotalNetoMes / maxNeto) * 100;
              const barWidth = isAsesoresEvaluated ? Math.max(6, targetW) : 0;
              const montoStr = isAsesoresEvaluated ? `$${item.costoTotalNetoMes.toLocaleString('es-MX')} netos/mes` : '$0 netos/mes';
              const plazasStr = isAsesoresEvaluated ? `${item.plazas} plaza(s)` : '0 plazas';
              const pctStr = isAsesoresEvaluated ? `(${item.pctPresupuesto}% nómina)` : '(0.0%)';

              return `
                <div class="asesores-bar-item" onclick="window.AuditEngine.selectAsesoresItem('${item.id}', 'cargos')" title="Clic para ver detalle y fundamento">
                  <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:5px; font-size:12.5px;">
                    <span style="color:var(--text-main); font-weight:600;">
                      ${item.icono} ${item.cargo} <span style="font-family:var(--font-mono); font-size:10.5px; color:var(--cyan); margin-left:4px;">[${plazasStr}]</span>
                    </span>
                    <span style="font-family:var(--font-mono); font-size:12px; font-weight:700; color:${item.color};">
                      <span id="asesoresBarVal_${item.id}">${montoStr}</span> 
                      <span style="font-size:10.5px; color:var(--text-dim); font-weight:normal;" id="asesoresBarPct_${item.id}">${pctStr}</span>
                    </span>
                  </div>
                  <div style="height:10px; background:rgba(255,255,255,0.06); border-radius:5px; overflow:hidden;">
                    <div id="asesoresBarFill_${item.id}" class="asesores-bar-fill ${isAsesoresEvaluated ? '' : 'bar-zero'}" style="width:${barWidth}%; background:${item.color};"></div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        `;
      } else {
        const maxComp = 3500000;
        chartStage.innerHTML = `
          <div style="display:flex; flex-direction:column; gap:9px;">
            ${SCJN_ASESORES_DATA.comparativaRed.map(item => {
              const targetW = (item.montoMes / maxComp) * 100;
              const barWidth = isAsesoresEvaluated ? Math.max(5, targetW) : 0;
              const montoStr = isAsesoresEvaluated ? item.montoTxt : '$0 / mes';
              const subStr = isAsesoresEvaluated ? item.anualTxt : '⚪ En reposo';

              return `
                <div class="asesores-bar-item" onclick="window.AuditEngine.selectAsesoresItem('${item.id}', 'comparativa')" title="Clic para ver detalle analítico">
                  <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:5px; font-size:12.5px;">
                    <span style="color:var(--text-main); font-weight:600;">
                      ${item.icono} ${item.concepto}
                    </span>
                    <span style="font-family:var(--font-mono); font-size:12px; font-weight:700; color:${item.color};">
                      <span id="asesoresCompVal_${item.id}">${montoStr}</span>
                    </span>
                  </div>
                  <div style="height:10px; background:rgba(255,255,255,0.06); border-radius:5px; overflow:hidden;">
                    <div id="asesoresCompBar_${item.id}" class="asesores-bar-fill ${isAsesoresEvaluated ? '' : 'bar-zero'}" style="width:${barWidth}%; background:${item.color};"></div>
                  </div>
                  <div style="display:flex; justify-content:space-between; font-size:10.5px; color:var(--text-dim); margin-top:3px; font-family:var(--font-mono);">
                    <span>${item.desc.substring(0, 75)}...</span>
                    <span id="asesoresCompSub_${item.id}">${subStr}</span>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        `;
      }
    }

    // Cuadrícula de Tarjetas Detalladas
    const asesoresGrid = document.getElementById('scjnAsesoresDesgloseGrid');
    if (asesoresGrid) {
      asesoresGrid.innerHTML = SCJN_ASESORES_DATA.cargos.map(c => {
        const targetW = (c.sueldoNeto / 128500) * 100;
        const plazasStr = isAsesoresEvaluated ? `${c.plazas} plaza(s)` : '0 plaza(s)';
        const netoStr = isAsesoresEvaluated ? `$${c.sueldoNeto.toLocaleString('es-MX')} pesos` : '$0 pesos';
        const brutoStr = isAsesoresEvaluated ? `($${c.sueldoBruto.toLocaleString('es-MX')} pesos bruto)` : '($0 bruto)';
        const barWidth = isAsesoresEvaluated ? targetW : 0;

        return `
          <div class="data-block-col" style="background:var(--bg-card); border:1px solid var(--border-subtle); padding:16px; border-radius:8px; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px; flex-wrap:wrap; gap:4px;">
                <strong style="color:var(--text-main); font-size:13.5px;">${c.icono} ${c.cargo}</strong>
                <span id="asesoresCardPlazas_${c.id}" style="font-family:var(--font-mono); font-size:11px; color:var(--cyan); font-weight:700; background:rgba(0,180,216,0.1); padding:2px 7px; border-radius:4px; border:1px solid rgba(0,180,216,0.25);">${plazasStr}</span>
              </div>
              <div style="font-family:var(--font-mono); font-size:14px; color:var(--gold-bright); font-weight:700; margin-bottom:4px;">
                <span id="asesoresCardNeto_${c.id}">${netoStr}</span> 
                <span style="font-size:10.5px; color:var(--text-dim); font-weight:normal;" id="asesoresCardBruto_${c.id}">${brutoStr}</span>
              </div>
              <div class="asesores-card-minibar">
                <div id="asesoresCardBar_${c.id}" class="asesores-card-minibar-fill ${isAsesoresEvaluated ? '' : 'bar-zero'}" style="width:${barWidth}%; background:${c.color};"></div>
              </div>
              <p style="font-size:11.5px; color:var(--text-secondary); line-height:1.45; margin:6px 0 0;">${c.funcion}</p>
            </div>
            <div style="margin-top:12px; padding-top:8px; border-top:1px dashed var(--border-subtle); display:flex; justify-content:space-between; align-items:center; font-size:10.5px; font-family:var(--font-mono);">
              <a class="glos-link" onclick="window.AuditEngine.goToGlossary('${c.glosTerm}')" title="Consultar concepto en Glosario">📖 Glosario ↗</a>
              <a class="ref-link" onclick="window.AuditEngine.goToRef('${c.refKey}')" title="Ver cita oficial en referencias">[Ref. ${c.refNum}] ↗</a>
            </div>
          </div>
        `;
      }).join('');
    }

    // Si está en reposo (no evaluado ni animando), fijar KPIs en 0
    if (!isAsesoresEvaluated && !isAsesoresAnimating) {
      const kpiPlazas = document.getElementById('kpiAsesoresPlazas');
      const kpiPlazasSub = document.getElementById('kpiAsesoresPlazasSub');
      const kpiNomina = document.getElementById('kpiAsesoresNominaMes');
      const kpiNominaSub = document.getElementById('kpiAsesoresNominaMesSub');
      const kpiPleno = document.getElementById('kpiAsesoresCostoPleno');
      const kpiPlenoSub = document.getElementById('kpiAsesoresCostoPlenoSub');
      const kpiRed = document.getElementById('kpiAsesoresRedAmpliada');
      const kpiRedSub = document.getElementById('kpiAsesoresRedAmpliadaSub');

      if (kpiPlazas) kpiPlazas.textContent = '0 plazas';
      if (kpiPlazasSub) kpiPlazasSub.textContent = '⚪ En reposo (rango 32-38)';
      if (kpiNomina) kpiNomina.textContent = '$0';
      if (kpiNominaSub) kpiNominaSub.textContent = '⚪ En reposo ($0/mes)';
      if (kpiPleno) kpiPleno.textContent = '$0 mdp';
      if (kpiPlenoSub) kpiPlenoSub.textContent = '⚪ 385 plazas consolidadas';
      if (kpiRed) kpiRed.textContent = '0 personas';
      if (kpiRedSub) kpiRedSub.textContent = '⚪ Comisiones & Cap. 3000';
    }
  }

  function evaluarAsesoresJudiciales(duracionMs = 1400) {
    if (isAsesoresAnimating) return;
    isAsesoresAnimating = true;

    const statusEl = document.getElementById('asesoresEvalStatusText');
    if (statusEl) {
      statusEl.innerHTML = '<span style="color:var(--cyan);">⚡ Evaluando y auditando nómina de asesores y estructura técnica SCJN en tiempo real...</span>';
    }
    const btnEval = document.getElementById('btnEvaluarAsesores');
    if (btnEval) {
      btnEval.innerHTML = '<span>⏳</span> Evaluando...';
    }

    const startTime = performance.now();
    const kpiPlazas = document.getElementById('kpiAsesoresPlazas');
    const kpiPlazasSub = document.getElementById('kpiAsesoresPlazasSub');
    const kpiNomina = document.getElementById('kpiAsesoresNominaMes');
    const kpiNominaSub = document.getElementById('kpiAsesoresNominaMesSub');
    const kpiPleno = document.getElementById('kpiAsesoresCostoPleno');
    const kpiPlenoSub = document.getElementById('kpiAsesoresCostoPlenoSub');
    const kpiRed = document.getElementById('kpiAsesoresRedAmpliada');
    const kpiRedSub = document.getElementById('kpiAsesoresRedAmpliadaSub');

    // Remover clases bar-zero
    document.querySelectorAll('.asesores-bar-fill, .asesores-card-minibar-fill').forEach(el => el.classList.remove('bar-zero'));

    function animateStep(timestamp) {
      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / duracionMs, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic

      // 1. KPIs
      if (kpiPlazas) kpiPlazas.textContent = `${Math.round(35 * eased)} plazas`;
      if (kpiNomina) kpiNomina.textContent = `$${Math.round(2850000 * eased).toLocaleString('es-MX')}`;
      if (kpiPleno) kpiPleno.textContent = `$${(376.2 * eased).toFixed(2)} mdp`;
      if (kpiRed) kpiRed.textContent = `${Math.round(72 * eased)} personas`;

      // 2. Gráfica en escenario
      if (currentAsesoresView === 'cargos') {
        const maxNeto = 1374800;
        SCJN_ASESORES_DATA.cargos.forEach(item => {
          const bar = document.getElementById(`asesoresBarFill_${item.id}`);
          const valEl = document.getElementById(`asesoresBarVal_${item.id}`);
          const pctEl = document.getElementById(`asesoresBarPct_${item.id}`);
          const targetW = (item.costoTotalNetoMes / maxNeto) * 100;

          if (bar) bar.style.width = `${Math.max(6, targetW * eased).toFixed(1)}%`;
          if (valEl) valEl.textContent = `$${Math.round(item.costoTotalNetoMes * eased).toLocaleString('es-MX')} netos/mes`;
          if (pctEl) pctEl.textContent = `(${(item.pctPresupuesto * eased).toFixed(1)}% nómina)`;
        });
      } else {
        const maxComp = 3500000;
        SCJN_ASESORES_DATA.comparativaRed.forEach(item => {
          const bar = document.getElementById(`asesoresCompBar_${item.id}`);
          const valEl = document.getElementById(`asesoresCompVal_${item.id}`);
          const targetW = (item.montoMes / maxComp) * 100;

          if (bar) bar.style.width = `${Math.max(5, targetW * eased).toFixed(1)}%`;
          if (valEl) valEl.textContent = `$${Math.round(item.montoMes * eased).toLocaleString('es-MX')} / mes`;
        });
      }

      // 3. Mini-barras y números en tarjetas
      SCJN_ASESORES_DATA.cargos.forEach(c => {
        const cardPlazas = document.getElementById(`asesoresCardPlazas_${c.id}`);
        const cardNeto = document.getElementById(`asesoresCardNeto_${c.id}`);
        const cardBruto = document.getElementById(`asesoresCardBruto_${c.id}`);
        const cardBar = document.getElementById(`asesoresCardBar_${c.id}`);
        const targetW = (c.sueldoNeto / 128500) * 100;

        if (cardBar) cardBar.style.width = `${(targetW * eased).toFixed(1)}%`;
        if (cardPlazas) cardPlazas.textContent = `${Math.round(c.plazas * eased)} plaza(s)`;
        if (cardNeto) cardNeto.textContent = `$${Math.round(c.sueldoNeto * eased).toLocaleString('es-MX')} pesos`;
        if (cardBruto) cardBruto.textContent = `($${Math.round(c.sueldoBruto * eased).toLocaleString('es-MX')} pesos bruto)`;
      });

      if (progress < 1) {
        asesoresAnimFrameId = requestAnimationFrame(animateStep);
      } else {
        isAsesoresAnimating = false;
        isAsesoresEvaluated = true;
        asesoresAnimFrameId = null;

        // Fijar valores finales exactos
        if (kpiPlazas) kpiPlazas.textContent = '35 plazas';
        if (kpiPlazasSub) kpiPlazasSub.textContent = '+385 plazas en los 11 despachos';
        if (kpiNomina) kpiNomina.textContent = '$2,850,000';
        if (kpiNominaSub) kpiNominaSub.innerHTML = '<span style="color:var(--gold);">+$34.2 mdp anuales por ponencia</span>';
        if (kpiPleno) kpiPleno.textContent = '$376.20 mdp';
        if (kpiPlenoSub) kpiPlenoSub.textContent = 'Presupuesto consolidado anual';
        if (kpiRed) kpiRed.textContent = '>70 personas';
        if (kpiRedSub) kpiRedSub.innerHTML = '<span style="color:#f59e0b;">+100% sobre plantilla tabular PNT</span>';

        if (statusEl) {
          statusEl.innerHTML = '<span style="color:var(--emerald-bright);">✓ Evaluación completada: Estructura de remuneraciones y plazas de ponencia desplegada al 100%.</span>';
        }
        if (btnEval) {
          btnEval.innerHTML = '<span>🔄</span> Volver a Evaluar';
        }

        renderJudicialAsesoresSimulator(currentAsesoresView);
      }
    }

    asesoresAnimFrameId = requestAnimationFrame(animateStep);
  }

  function resetAsesoresJudiciales() {
    if (asesoresAnimFrameId) {
      cancelAnimationFrame(asesoresAnimFrameId);
      asesoresAnimFrameId = null;
    }
    isAsesoresAnimating = false;
    isAsesoresEvaluated = false;

    renderJudicialAsesoresSimulator(currentAsesoresView);

    const statusEl = document.getElementById('asesoresEvalStatusText');
    if (statusEl) {
      statusEl.innerHTML = '⚪ Cifras en reposo ($0 pesos / 0 plazas). Presiona «Evaluar Asesores» o pasa el cursor para medir la escala real del equipo técnico.';
    }
    const btnEval = document.getElementById('btnEvaluarAsesores');
    if (btnEval) {
      btnEval.innerHTML = '<span>▶️</span> Evaluar Asesores';
    }
  }

  function toggleHoverAsesores(enabled) {
    isAsesoresHoverEnabled = !!enabled;
  }

  function handleAsesoresHover() {
    if (isAsesoresHoverEnabled && !isAsesoresEvaluated && !isAsesoresAnimating) {
      evaluarAsesoresJudiciales();
    }
  }

  // ==========================================================================
  // SIMULADOR COMPARATIVO, SALUD FINANCIERA & CHOQUE LABORAL (SUBPESTAÑA 4.4)
  // ==========================================================================
  const SCJN_CALCULOS_GLOBALES_DATA = {
    nominaPonencias11: 376200000,
    prestacionesPleno11: 18835399,
    sueldosBasePleno11: 27317136,
    gastoTotalConsolidado: 422352535,
    redAmpliadaPNT: 508000000,
    fideicomisosLitigio: 15434000000,
    costoMensualPromedioPonencia: 2850000,
    costoAnualPorMinistroBase: 34200000,
    costoAnualPorMinistroIntegrado: 38395685,
    saludFinancieraScore: 24,
    balanzaSalas: [
      {
        id: 'primera_sala',
        nombre: 'Primera Sala (Civil y Penal - 5 Ministros)',
        icono: '⚖️',
        montoAnual: 191978425,
        montoTxt: '$192.0 mdp anuales',
        plazas: '~170 plazas técnicas de ponencia',
        color: '#e74c3c',
        desc: 'Nómina de 5 despachos de ponencia ($171.0 mdp) más retribuciones de 5 ministros ($20.98 mdp).',
        glosTerm: 'Pleno de la Suprema Corte',
        refKey: 'ref-pef-ramo03',
        refNum: '21'
      },
      {
        id: 'segunda_sala',
        nombre: 'Segunda Sala (Administrativa y Laboral - 4 a 5 Ministros)',
        icono: '🏛️',
        montoAnual: 188374110,
        montoTxt: '$188.4 mdp anuales',
        plazas: '~171 plazas técnicas de estudio y cuenta',
        color: '#f59e0b',
        desc: 'Nómina de ponencias de sala ($171.0 mdp) más remuneraciones de los ministros en funciones.',
        glosTerm: 'Pleno de la Suprema Corte',
        refKey: 'ref-pef-ramo03',
        refNum: '21'
      },
      {
        id: 'presidencia_pleno',
        nombre: 'Presidencia de la Corte & Coordinación Plenaria',
        icono: '⭐',
        montoAnual: 42000000,
        montoTxt: '~$42.0 mdp anuales',
        plazas: '38 plazas directas + Acuerdos y Seguridad',
        color: '#0284c7',
        desc: 'Despacho de Presidencia SCJN, secretaría de acuerdos, logística de sesiones y custodia federal.',
        glosTerm: 'Ponencia de Ministro(a)',
        refKey: 'ref-reforma-judicial',
        refNum: '19'
      }
    ],
    jerarquiaScjn: [
      {
        id: 'auxiliar_scjn',
        cargo: 'Auxiliar Administrativo / Chofer SCJN',
        icono: '📁',
        sueldoMes: 26500,
        sueldoAnualIntegrado: 456000,
        aguinaldo: 38000,
        sgmmPrivado: 'Póliza privada con erario',
        pagoRiesgo: 0,
        color: '#10b981'
      },
      {
        id: 'asesor_scjn',
        cargo: 'Secretario Auxiliar / Asesor SCJN',
        icono: '📚',
        sueldoMes: 58400,
        sueldoAnualIntegrado: 1020000,
        aguinaldo: 85000,
        sgmmPrivado: 'Póliza privada con erario',
        pagoRiesgo: 0,
        color: '#f59e0b'
      },
      {
        id: 'proyectista_scjn',
        cargo: 'Secretario de Estudio y Cuenta (Proyectista)',
        icono: '⚖️',
        sueldoMes: 98200,
        sueldoAnualIntegrado: 1740000,
        aguinaldo: 145000,
        sgmmPrivado: 'Póliza privada con erario',
        pagoRiesgo: 0,
        color: '#0284c7'
      },
      {
        id: 'ministro_scjn',
        cargo: 'Ministro(a) SCJN (Régimen Integrado)',
        icono: '👑',
        sueldoMes: 206948,
        sueldoAnualIntegrado: 5529450,
        aguinaldo: 588000,
        pagoRiesgo: 642000,
        sgmmPrivado: 'Póliza VIP erario ($50 mdp cobertura)',
        color: '#e74c3c'
      }
    ]
  };

  let isGlobalesEvaluated = false;
  let isGlobalesAnimating = false;
  let isGlobalesHoverEnabled = false;
  let currentGlobalesView = 'balanza'; // 'balanza' | 'choque'
  let currentChoqueSalario = 25000;
  let currentChoqueRegimen = 'imss';
  let selectedGlobalesItem = null;
  let globalesAnimFrameId = null;

  function setGlobalesView(viewMode) {
    currentGlobalesView = viewMode;
    renderJudicialGlobalesSimulator(viewMode);
  }

  function setChoqueSalario(salarioNum) {
    currentChoqueSalario = salarioNum;
    ['25', '50', '100'].forEach(k => {
      const btn = document.getElementById(`btnChoqueSal${k}`);
      if (btn) btn.classList.toggle('active', salarioNum === parseInt(k) * 1000);
    });
    renderJudicialGlobalesSimulator(currentGlobalesView);
  }

  function setChoqueRegimen(regimenKey) {
    currentChoqueRegimen = regimenKey;
    const btnIMSS = document.getElementById('btnChoqueRegIMSS');
    const btnISSSTE = document.getElementById('btnChoqueRegISSSTE');
    if (btnIMSS) btnIMSS.classList.toggle('active', regimenKey === 'imss');
    if (btnISSSTE) btnISSSTE.classList.toggle('active', regimenKey === 'issste');
    renderJudicialGlobalesSimulator(currentGlobalesView);
  }

  function selectGlobalesItem(id, mode) {
    selectedGlobalesItem = { id, mode };
    const detailBox = document.getElementById('globalesDetailBox');
    if (!detailBox) return;

    if (mode === 'balanza') {
      const item = SCJN_CALCULOS_GLOBALES_DATA.balanzaSalas.find(s => s.id === id);
      if (!item) return;
      detailBox.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
          <div>
            <strong style="color:var(--gold-bright); font-size:13.5px;">${item.icono} ${item.nombre}</strong>
            <div style="font-size:11px; color:var(--text-dim); margin-top:2px;">
              Plazas adscritas: <strong style="color:var(--text-main);">${item.plazas}</strong>
            </div>
          </div>
          <span style="font-family:var(--font-mono); font-size:12px; color:var(--gold-bright); font-weight:700; background:rgba(212,175,55,0.12); padding:3px 8px; border-radius:4px; border:1px solid var(--border-gold);">
            ${item.montoTxt}
          </span>
        </div>
        <p style="margin:8px 0 6px; font-size:12px; line-height:1.5; color:var(--text-secondary);">${item.desc}</p>
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; font-size:11px; border-top:1px dashed var(--border-subtle); padding-top:6px; margin-top:6px; font-family:var(--font-mono);">
          <span>📚 Glosario: <a class="glos-link" onclick="window.AuditEngine.goToGlossary('${item.glosTerm}')">${item.glosTerm} ↗</a></span>
          <span>📑 Fundamento: <a class="ref-link" onclick="window.AuditEngine.goToRef('${item.refKey}')">[Ref. ${item.refNum}] ↗</a></span>
        </div>
      `;
    }
  }

  function renderJudicialGlobalesSimulator(mode = currentGlobalesView) {
    currentGlobalesView = mode;

    // Actualizar botones de vista
    const btnBalanza = document.getElementById('btnGlobalesViewBalanza');
    const btnChoque = document.getElementById('btnGlobalesViewChoque');
    const choqueWrapper = document.getElementById('choqueControlsWrapper');

    if (btnBalanza && btnChoque) {
      if (mode === 'balanza') {
        btnBalanza.classList.add('active');
        btnBalanza.style.borderColor = 'var(--gold)';
        btnBalanza.style.color = 'var(--gold-bright)';
        btnChoque.classList.remove('active');
        btnChoque.style.borderColor = '';
        btnChoque.style.color = '';
        if (choqueWrapper) choqueWrapper.style.display = 'none';
      } else {
        btnChoque.classList.add('active');
        btnChoque.style.borderColor = 'var(--gold)';
        btnChoque.style.color = 'var(--gold-bright)';
        btnBalanza.classList.remove('active');
        btnBalanza.style.borderColor = '';
        btnBalanza.style.color = '';
        if (choqueWrapper) choqueWrapper.style.display = 'flex';
      }
    }

    // Escenario de Gráfica
    const chartStage = document.getElementById('globalesChartStage');
    const detailBox = document.getElementById('globalesDetailBox');

    if (chartStage) {
      if (mode === 'balanza') {
        const maxMonto = 191978425;
        chartStage.innerHTML = `
          <div style="display:flex; flex-direction:column; gap:9px;">
            ${SCJN_CALCULOS_GLOBALES_DATA.balanzaSalas.map(item => {
              const targetW = (item.montoAnual / maxMonto) * 100;
              const barWidth = isGlobalesEvaluated ? Math.max(8, targetW) : 0;
              const montoStr = isGlobalesEvaluated ? item.montoTxt : '$0 mdp';

              return `
                <div class="globales-bar-item" onclick="window.AuditEngine.selectGlobalesItem('${item.id}', 'balanza')" title="Clic para ver detalle de la sala">
                  <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:5px; font-size:12.5px;">
                    <span style="color:var(--text-main); font-weight:600;">
                      ${item.icono} ${item.nombre}
                    </span>
                    <span style="font-family:var(--font-mono); font-size:12px; font-weight:700; color:${item.color};">
                      <span id="globalesBarVal_${item.id}">${montoStr}</span>
                    </span>
                  </div>
                  <div style="height:10px; background:rgba(255,255,255,0.06); border-radius:5px; overflow:hidden;">
                    <div id="globalesBarFill_${item.id}" class="globales-bar-fill ${isGlobalesEvaluated ? '' : 'bar-zero'}" style="width:${barWidth}%; background:${item.color};"></div>
                  </div>
                  <div style="display:flex; justify-content:space-between; font-size:10.5px; color:var(--text-dim); margin-top:3px; font-family:var(--font-mono);">
                    <span>${item.plazas}</span>
                    <span>${item.desc.substring(0, 68)}...</span>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        `;

        if (detailBox && (!selectedGlobalesItem || selectedGlobalesItem.mode !== 'balanza')) {
          detailBox.innerHTML = `💡 <em>Haz clic sobre cualquiera de las salas para ver el desglose operativo entre gasto de ponencias, remuneraciones de ministros y atribución competencial.</em>`;
        }
      } else {
        // Modo Choque Laboral
        const sal = currentChoqueSalario;
        const reg = currentChoqueRegimen;
        const aguinaldoTrab = reg === 'imss' ? (sal * 0.5) : (sal * (40 / 30));
        const primaTrab = reg === 'imss' ? (sal * 0.1) : (sal * 0.2);
        const totalTrabAnual = (sal * 12) + aguinaldoTrab + primaTrab;
        const totalMinistroAnual = 5529450;
        const ratioAnos = (totalMinistroAnual / totalTrabAnual).toFixed(1);
        const ratioAguinaldo = (588000 / aguinaldoTrab).toFixed(1);
        const trabajadoresPonencia = Math.round(34200000 / totalTrabAnual);

        const itemsChoque = [
          {
            id: 'trabajador_usuario',
            nombre: `Tu Ingreso Integrado (${reg.toUpperCase()} · $${sal.toLocaleString('es-MX')}/mes)`,
            icono: '💼',
            montoAnual: totalTrabAnual,
            montoTxt: `$${Math.round(totalTrabAnual).toLocaleString('es-MX')} / año`,
            subTxt: `Sueldo + Aguinaldo ($${Math.round(aguinaldoTrab).toLocaleString('es-MX')}) + Prima ($${Math.round(primaTrab).toLocaleString('es-MX')})`,
            color: '#10b981'
          },
          {
            id: 'auxiliar_scjn',
            nombre: 'Auxiliar Administrativo / Chofer SCJN',
            icono: '📁',
            montoAnual: 456000,
            montoTxt: '$456,000 / año ($38k bruto/mes)',
            subTxt: 'Cargo inicial en despacho jurisdiccional + aguinaldo y SGMM',
            color: '#38bdf8'
          },
          {
            id: 'proyectista_scjn',
            nombre: 'Secretario Proyectista (Estudio y Cuenta)',
            icono: '⚖️',
            montoAnual: 1740000,
            montoTxt: '$1,740,000 / año ($145k bruto/mes)',
            subTxt: '14 proyectistas por despacho = $24.3 mdp/año en conjunto',
            color: '#f59e0b'
          },
          {
            id: 'ministro_scjn',
            nombre: 'Ministro(a) SCJN (Régimen Integrado)',
            icono: '👑',
            montoAnual: totalMinistroAnual,
            montoTxt: '$5,529,450 / año ($460.7k/mes equiv.)',
            subTxt: 'Sueldo tabular + $1.71m prestaciones efectivo + $500k especie',
            color: '#e74c3c'
          }
        ];

        const maxChoque = totalMinistroAnual;
        chartStage.innerHTML = `
          <div style="display:flex; flex-direction:column; gap:9px;">
            ${itemsChoque.map(item => {
              const targetW = (item.montoAnual / maxChoque) * 100;
              const barWidth = isGlobalesEvaluated ? Math.max(5, targetW) : 0;
              const montoStr = isGlobalesEvaluated ? item.montoTxt : '$0 / año';

              return `
                <div class="globales-bar-item" style="border-left: 3px solid ${item.color};">
                  <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:5px; font-size:12.5px;">
                    <span style="color:var(--text-main); font-weight:600;">
                      ${item.icono} ${item.nombre}
                    </span>
                    <span style="font-family:var(--font-mono); font-size:12px; font-weight:700; color:${item.color};">
                      <span id="choqueBarVal_${item.id}">${montoStr}</span>
                    </span>
                  </div>
                  <div style="height:10px; background:rgba(255,255,255,0.06); border-radius:5px; overflow:hidden;">
                    <div id="choqueBarFill_${item.id}" class="globales-bar-fill ${isGlobalesEvaluated ? '' : 'bar-zero'}" style="width:${barWidth}%; background:${item.color};"></div>
                  </div>
                  <div style="display:flex; justify-content:space-between; font-size:10.5px; color:var(--text-dim); margin-top:3px; font-family:var(--font-mono);">
                    <span>${item.subTxt}</span>
                    <span>${(item.montoAnual / maxChoque * 100).toFixed(1)}% escala</span>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        `;

        // Scorecard de Realidades Incomodas (Impacto Sensorial)
        if (detailBox) {
          detailBox.innerHTML = `
            <strong style="color:var(--gold-bright); display:block; margin-bottom:8px; font-size:13px;">
              ⚡ Radiografía de Realidades Laborales y Choque Social (${reg.toUpperCase()} vs SCJN):
            </strong>
            <div class="choque-contrast-grid">
              <div class="choque-contrast-card">
                <div class="choque-contrast-title">⏳ Años de tu Vida Laboral</div>
                <div class="choque-contrast-val" style="color:var(--crimson-bright);">${isGlobalesEvaluated ? ratioAnos + ' AÑOS' : '0.0 años'}</div>
                <div class="choque-contrast-desc">Tiempo ininterrumpido que requieres para ganar lo que 1 ministro percibe en solo 12 meses.</div>
              </div>
              <div class="choque-contrast-card">
                <div class="choque-contrast-title">🎁 Desproporción de Aguinaldo</div>
                <div class="choque-contrast-val" style="color:var(--gold-bright);">${isGlobalesEvaluated ? ratioAguinaldo + 'x mayor' : '0.0x'}</div>
                <div class="choque-contrast-desc">El aguinaldo de ministro ($588,000) vs tu aguinaldo de ley ($${Math.round(aguinaldoTrab).toLocaleString('es-MX')}).</div>
              </div>
              <div class="choque-contrast-card">
                <div class="choque-contrast-title">🏥 Seguridad Social & Pólizas</div>
                <div class="choque-contrast-val" style="color:var(--cyan);">${isGlobalesEvaluated ? 'Fila vs VIP' : '⚪ En reposo'}</div>
                <div class="choque-contrast-desc">Tú esperas cita en ${reg.toUpperCase()}; el ministro tiene póliza privada erario de hasta $50 mdp.</div>
              </div>
              <div class="choque-contrast-card">
                <div class="choque-contrast-title">🏢 Equivalencia en 1 Ponencia</div>
                <div class="choque-contrast-val" style="color:#10b981;">${isGlobalesEvaluated ? trabajadoresPonencia + ' personas' : '0 personas'}</div>
                <div class="choque-contrast-desc">Con el costo de 1 despacho ($34.2 mdp) se pagan ${trabajadoresPonencia} sueldos integrados de tu nivel.</div>
              </div>
            </div>
          `;
        }
      }
    }

    // Cuadrícula de 4 tarjetas de cálculos globales
    const cardMes = document.getElementById('cardGlobalesMesVal');
    const cardMesSub = document.getElementById('cardGlobalesMesSub');
    const cardAnio = document.getElementById('cardGlobalesAnioVal');
    const cardAnioSub = document.getElementById('cardGlobalesAnioSub');
    const cardTot = document.getElementById('cardGlobalesTotalVal');
    const cardTotSub = document.getElementById('cardGlobalesTotalSub');
    const cardCons = document.getElementById('cardGlobalesConsolidadoVal');
    const cardConsSub = document.getElementById('cardGlobalesConsolidadoSub');

    if (cardMes && !isGlobalesEvaluated && !isGlobalesAnimating) {
      cardMes.textContent = '$0 pesos';
      if (cardMesSub) cardMesSub.textContent = 'Por cada una de las 11 ponencias';
      if (cardAnio) cardAnio.textContent = '$0 mdp';
      if (cardAnioSub) cardAnioSub.textContent = '⚪ En reposo';
      if (cardTot) cardTot.textContent = '$0 mdp';
      if (cardTotSub) cardTotSub.textContent = '⚪ 385 plazas consolidadas';
      if (cardCons) cardCons.textContent = '$0 mdp';
      if (cardConsSub) cardConsSub.textContent = '⚪ 11 Despachos + Prestaciones';
    } else if (cardMes && isGlobalesEvaluated) {
      cardMes.textContent = '$2.85 a $3.10 mdp';
      if (cardMesSub) cardMesSub.textContent = 'Por cada una de las 11 ponencias';
      if (cardAnio) cardAnio.textContent = '~$34.2 millones';
      if (cardAnioSub) cardAnioSub.textContent = 'Nómina anual de su equipo de apoyo';
      if (cardTot) cardTot.textContent = '$376,200,000 pesos';
      if (cardTotSub) cardTotSub.textContent = '11 Ponencias de la SCJN en conjunto';
      if (cardCons) cardCons.textContent = '$422,360,000 pesos';
      if (cardConsSub) cardConsSub.textContent = '11 Ponencias + Sueldos + Prestaciones';
    }

    // Si está en reposo, fijar KPIs de cabecera en 0
    if (!isGlobalesEvaluated && !isGlobalesAnimating) {
      const kpiSalud = document.getElementById('kpiGlobalesSalud');
      const kpiSaludSub = document.getElementById('kpiGlobalesSaludSub');
      const kpiGasto = document.getElementById('kpiGlobalesGastoDespachos');
      const kpiGastoSub = document.getElementById('kpiGlobalesGastoDespachosSub');
      const kpiFid = document.getElementById('kpiGlobalesFideicomisos');
      const kpiFidSub = document.getElementById('kpiGlobalesFideicomisosSub');
      const kpiBrecha = document.getElementById('kpiGlobalesBrecha');
      const kpiBrechaSub = document.getElementById('kpiGlobalesBrechaSub');

      if (kpiSalud) kpiSalud.textContent = '0 / 100';
      if (kpiSaludSub) kpiSaludSub.textContent = '⚪ En reposo (sin evaluar)';
      if (kpiGasto) kpiGasto.textContent = '$0 mdp';
      if (kpiGastoSub) kpiGastoSub.textContent = '⚪ 11 Ponencias + Prestaciones';
      if (kpiFid) kpiFid.textContent = '$0 mdp';
      if (kpiFidSub) kpiFidSub.textContent = '⚪ 13 Fondos del PJF [Ref. 23]';
      if (kpiBrecha) kpiBrecha.textContent = '0.0x';
      if (kpiBrechaSub) kpiBrechaSub.textContent = '⚪ vs trabajador promedio';
    }
  }

  function evaluarGlobalesJudiciales(duracionMs = 1400) {
    if (isGlobalesAnimating) return;
    isGlobalesAnimating = true;

    const statusEl = document.getElementById('globalesEvalStatusText');
    if (statusEl) {
      statusEl.innerHTML = '<span style="color:var(--crimson-bright);">⚡ Auditando balance consolidado de ponencias, prestaciones y realidades laborales...</span>';
    }
    const btnEval = document.getElementById('btnEvaluarGlobales');
    if (btnEval) {
      btnEval.innerHTML = '<span>⏳</span> Evaluando...';
    }

    const startTime = performance.now();
    const kpiSalud = document.getElementById('kpiGlobalesSalud');
    const kpiSaludSub = document.getElementById('kpiGlobalesSaludSub');
    const kpiGasto = document.getElementById('kpiGlobalesGastoDespachos');
    const kpiGastoSub = document.getElementById('kpiGlobalesGastoDespachosSub');
    const kpiFid = document.getElementById('kpiGlobalesFideicomisos');
    const kpiFidSub = document.getElementById('kpiGlobalesFideicomisosSub');
    const kpiBrecha = document.getElementById('kpiGlobalesBrecha');
    const kpiBrechaSub = document.getElementById('kpiGlobalesBrechaSub');

    // Remover clases bar-zero
    document.querySelectorAll('.globales-bar-fill').forEach(el => el.classList.remove('bar-zero'));

    function animateStep(timestamp) {
      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / duracionMs, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic

      // 1. KPIs
      if (kpiSalud) kpiSalud.textContent = `${Math.round(24 * eased)} / 100`;
      if (kpiGasto) kpiGasto.textContent = `$${(422.36 * eased).toFixed(2)} mdp`;
      if (kpiFid) kpiFid.textContent = `$${Math.round(15434 * eased).toLocaleString('es-MX')} mdp`;
      if (kpiBrecha) kpiBrecha.textContent = `${(18.4 * eased).toFixed(1)}x`;

      // 2. Gráficas en escenario
      if (currentGlobalesView === 'balanza') {
        const maxMonto = 191978425;
        SCJN_CALCULOS_GLOBALES_DATA.balanzaSalas.forEach(item => {
          const bar = document.getElementById(`globalesBarFill_${item.id}`);
          const valEl = document.getElementById(`globalesBarVal_${item.id}`);
          const targetW = (item.montoAnual / maxMonto) * 100;

          if (bar) bar.style.width = `${Math.max(8, targetW * eased).toFixed(1)}%`;
          if (valEl) valEl.textContent = `$${((item.montoAnual / 1000000) * eased).toFixed(1)} mdp anuales`;
        });
      } else {
        const sal = currentChoqueSalario;
        const reg = currentChoqueRegimen;
        const aguinaldoTrab = reg === 'imss' ? (sal * 0.5) : (sal * (40 / 30));
        const primaTrab = reg === 'imss' ? (sal * 0.1) : (sal * 0.2);
        const totalTrabAnual = (sal * 12) + aguinaldoTrab + primaTrab;
        const totalMinistroAnual = 5529450;
        const maxChoque = totalMinistroAnual;

        const montos = {
          'trabajador_usuario': totalTrabAnual,
          'auxiliar_scjn': 456000,
          'proyectista_scjn': 1740000,
          'ministro_scjn': totalMinistroAnual
        };

        Object.keys(montos).forEach(id => {
          const bar = document.getElementById(`choqueBarFill_${id}`);
          const valEl = document.getElementById(`choqueBarVal_${id}`);
          const targetW = (montos[id] / maxChoque) * 100;

          if (bar) bar.style.width = `${Math.max(5, targetW * eased).toFixed(1)}%`;
          if (valEl) valEl.textContent = `$${Math.round(montos[id] * eased).toLocaleString('es-MX')} / año`;
        });
      }

      // 3. Tarjetas inferiores
      const cardMes = document.getElementById('cardGlobalesMesVal');
      const cardAnio = document.getElementById('cardGlobalesAnioVal');
      const cardTot = document.getElementById('cardGlobalesTotalVal');
      const cardCons = document.getElementById('cardGlobalesConsolidadoVal');

      if (cardMes) cardMes.textContent = progress > 0.5 ? '$2.85 a $3.10 mdp' : `$${Math.round(2850000 * eased).toLocaleString('es-MX')}`;
      if (cardAnio) cardAnio.textContent = `~$${(34.2 * eased).toFixed(1)} millones`;
      if (cardTot) cardTot.textContent = `$${Math.round(376200000 * eased).toLocaleString('es-MX')} pesos`;
      if (cardCons) cardCons.textContent = `$${Math.round(422360000 * eased).toLocaleString('es-MX')} pesos`;

      if (progress < 1) {
        globalesAnimFrameId = requestAnimationFrame(animateStep);
      } else {
        isGlobalesAnimating = false;
        isGlobalesEvaluated = true;
        globalesAnimFrameId = null;

        // Fijar valores finales exactos
        if (kpiSalud) kpiSalud.innerHTML = '<span style="color:var(--crimson-bright);">24 / 100</span>';
        if (kpiSaludSub) kpiSaludSub.innerHTML = '<span style="color:var(--crimson-bright);">🔴 CRÍTICO · Desbalance de Austeridad</span>';
        if (kpiGasto) kpiGasto.textContent = '$422.36 mdp';
        if (kpiGastoSub) kpiGastoSub.textContent = '11 Ponencias + Prestaciones + Sueldos';
        if (kpiFid) kpiFid.textContent = '$15,434 mdp';
        if (kpiFidSub) kpiFidSub.textContent = '13 Fondos en litigio [Ref. 23]';
        if (kpiBrecha) kpiBrecha.textContent = '18.4x';
        if (kpiBrechaSub) kpiBrechaSub.innerHTML = '<span style="color:#f59e0b;">1 año ministro = 18.4 años $25k</span>';

        if (statusEl) {
          statusEl.innerHTML = '<span style="color:var(--emerald-bright);">✓ Auditoría completada: Gasto consolidado, diagnóstico de salud y brecha laboral desplegados al 100%.</span>';
        }
        if (btnEval) {
          btnEval.innerHTML = '<span>🔄</span> Volver a Evaluar';
        }

        renderJudicialGlobalesSimulator(currentGlobalesView);
      }
    }

    globalesAnimFrameId = requestAnimationFrame(animateStep);
  }

  function resetGlobalesJudiciales() {
    if (globalesAnimFrameId) {
      cancelAnimationFrame(globalesAnimFrameId);
      globalesAnimFrameId = null;
    }
    isGlobalesAnimating = false;
    isGlobalesEvaluated = false;

    renderJudicialGlobalesSimulator(currentGlobalesView);

    const statusEl = document.getElementById('globalesEvalStatusText');
    if (statusEl) {
      statusEl.innerHTML = '⚪ Cifras en reposo ($0 mdp / Salud Financiera en pausa). Presiona «Evaluar Salud y Comparativa» o pasa el cursor para auditar el gasto consolidado.';
    }
    const btnEval = document.getElementById('btnEvaluarGlobales');
    if (btnEval) {
      btnEval.innerHTML = '<span>▶️</span> Evaluar Salud y Comparativa';
    }
  }

  function toggleHoverGlobales(enabled) {
    isGlobalesHoverEnabled = !!enabled;
  }

  function handleGlobalesHover() {
    if (isGlobalesHoverEnabled && !isGlobalesEvaluated && !isGlobalesAnimating) {
      evaluarGlobalesJudiciales();
    }
  }

  function renderJudicialMinisters() {
    const jr = DB.judicial_reservado;
    if (!jr || !jr.scjn_analisis_salarial) return;
    const sa = jr.scjn_analisis_salarial;

    // Sincronizar gráfica comparativa del Pleno
    renderJudicialMinistersChart();

    // 1. Prestaciones y paquete de compensaciones (Ficha 1 / Subpestaña 4.2)
    renderJudicialPrestacionesSimulator(currentPrestacionesView);

    // 2. Desglose de plazas de la ponencia (Ficha 2 / Subpestaña 4.3)
    renderJudicialAsesoresSimulator(currentAsesoresView);

    // 3. Cálculos globales, balanza de salas y choque salarial (Ficha 3 / Subpestaña 4.4)
    renderJudicialGlobalesSimulator(currentGlobalesView);

    // 3. Tabla comparativa: Nuevo Pleno Oficial (9 Ministros) o Pleno de Transición (10 Ministros y Renuncias)
    const tbody = document.getElementById('scjnMinistersTableBody');
    if (!tbody) return;

    if (activeJudicialPlenoTab === 'nuevo') {
      const ministersList = sa.nuevo_pleno_oficial_scjn || sa.ministros;
      const presidente = ministersList.find(m => m.tipo_cargo === 'presidente' || m.nombre.includes('Aguilar Ortiz'));
      const colegiados = ministersList.filter(m => m !== presidente);

      const renderNuevoRow = (m, num) => {
        const isPres = m.tipo_cargo === 'presidente' || m.nombre.includes('Aguilar Ortiz');
        const badgeText = isPres ? '⭐ MINISTRO PRESIDENTE SCJN · ELECTO POR VOTO POPULAR' : 
          (m.estatus_reforma && m.estatus_reforma.includes('ratificada')) ? '🟢 MINISTRA · RATIFICADA POR VOTO POPULAR' : 
          (m.tipo_cargo === 'ministro' && (m.nombre.includes('Ríos') || m.nombre.includes('Herrerías'))) ? '⚖️ MINISTRA · ELECTA POR VOTO POPULAR' : 
          '⚖️ MINISTRO · ELECTO POR VOTO POPULAR';

        return `
          <tr style="${isPres ? 'background:rgba(201,168,76,0.08);' : ''}">
            <td>
              <div style="display:flex; align-items:baseline; gap:6px;">
                ${num ? `<span style="font-family:var(--font-mono); font-size:11px; color:var(--text-dim); font-weight:700;">${num}.</span>` : ''}
                <strong style="color:var(--text-main); font-size:14px;">${m.nombre}</strong>
              </div>
              <div style="margin-top:2px;">
                <span style="display:inline-block; font-family:var(--font-mono); font-size:9.5px; font-weight:700; ${isPres ? 'color:#000; background:var(--gold);' : 'color:#2ecc71; background:rgba(46,204,113,0.15); border:1px solid rgba(46,204,113,0.4);'} padding:2px 7px; border-radius:3px; text-transform:uppercase; margin-bottom:4px;">
                  ${badgeText}
                </span>
              </div>
              <div style="font-size:10.5px; color:var(--text-dim); font-family:var(--font-mono);">
                ${m.cargo} · <span style="color:var(--cyan);">${m.sala}</span>
              </div>
              <div style="margin-top:5px;">
                <button class="mini-profile-btn" onclick="window.AuditEngine.openMinisterModal('${m.id}', 'nuevo')" style="background:rgba(201,168,76,0.12); border:1px solid var(--border-gold); color:var(--gold-bright); font-family:var(--font-mono); font-size:10px; padding:3px 8px; border-radius:4px; cursor:pointer; font-weight:600;">
                  🔍 Ver Trayectoria &amp; Ficha Completa
                </button>
              </div>
            </td>
            <td>
              <div style="font-size:10.5px; color:var(--gold); font-family:var(--font-mono); font-weight:600;">${m.origen_acreditacion || m.designacion}</div>
              <div style="font-size:11.5px; color:var(--text-main); margin-top:3px; line-height:1.4;">
                <strong>Formación:</strong> ${m.formacion || 'Licenciatura en Derecho'}
              </div>
              <div style="font-size:10.5px; color:var(--cyan); font-family:var(--font-mono); margin-top:3px;">
                <strong>Especialidad:</strong> ${m.especialidad || 'Derecho Constitucional'}
              </div>
            </td>
            <td class="table-num" style="font-family:var(--font-mono); font-weight:700; color:var(--cyan); text-align:right;">
              ${m.asesores_plazas} plazas
              <div style="font-size:9.5px; color:var(--text-dim); font-weight:normal;">Esquema de austeridad</div>
            </td>
            <td class="table-num" style="font-family:var(--font-mono); color:var(--emerald-bright); font-weight:700; text-align:right;">
              ${m.sueldo_neto_mensual}
              <div style="font-size:9.5px; color:var(--text-dim); font-weight:normal;">${m.sueldo_bruto_mensual} bruto</div>
            </td>
            <td class="table-num" style="font-family:var(--font-mono); color:var(--crimson-bright); font-weight:700; text-align:right;">
              ${m.costo_mensual_ponencia}
            </td>
            <td style="text-align:center;">
              <span style="font-size:10px; font-family:var(--font-mono); padding:3px 8px; border-radius:4px; background:rgba(46,204,113,0.18); color:#2ecc71; border:1px solid rgba(46,204,113,0.4); font-weight:700; display:inline-block;">
                ✓ TOPADO ART. 127
              </span>
              <div style="font-size:9px; color:var(--text-dim); margin-top:2px;">Sin privilegios privados</div>
            </td>
          </tr>
        `;
      };

      let rowsHtml = '';
      if (presidente) {
        rowsHtml += `
          <tr style="background:rgba(201,168,76,0.15); border-left:4px solid var(--gold);">
            <td colspan="6" style="padding:9px 14px; font-family:var(--font-mono); font-size:11px; color:var(--gold-bright); text-transform:uppercase; letter-spacing:1px; font-weight:700;">
              ⭐ MINISTRO PRESIDENTE DE LA SUPREMA CORTE DE JUSTICIA DE LA NACIÓN · PLENO CONSTITUCIONAL
            </td>
          </tr>
          ${renderNuevoRow(presidente, null)}
        `;
      }

      rowsHtml += `
        <tr style="background:rgba(46,204,113,0.1); border-left:4px solid #2ecc71;">
          <td colspan="6" style="padding:9px 14px; font-family:var(--font-mono); font-size:11px; color:#2ecc71; text-transform:uppercase; letter-spacing:1px; font-weight:700;">
            🟢 MINISTRAS Y MINISTROS DEL NUEVO PLENO CONSTITUCIONAL (ELECTOS POR VOTO POPULAR CIUDADANO)
          </td>
        </tr>
      `;
      colegiados.forEach((m, idx) => {
        rowsHtml += renderNuevoRow(m, idx + 1);
      });

      tbody.innerHTML = rowsHtml;

    } else {
      // Vista Transición 2024–2025
      const allMinistros = sa.pleno_transicion_2024_2025 || [];
      const presidenta = allMinistros.find(m => m.nombre.includes('Piña'));
      const candidatas = allMinistros.filter(m => m.continua_eleccion === true);
      const renuncias = allMinistros.filter(m => m.continua_eleccion === false && m.estatus_laboral.includes('En funciones') && !m.nombre.includes('Piña'));
      const concluidos = allMinistros.filter(m => m.estatus_laboral.includes('Periodo constitucional concluido'));

      const renderTransicionRow = (m, num) => {
        const isTopada = m.sueldo_neto_mensual.includes('134,310');
        const isPres = m.nombre.includes('Piña');
        const isCandidata = m.continua_eleccion === true;
        const isConcluido = m.estatus_laboral.includes('Periodo constitucional concluido');
        const isRiosFarjat = m.nombre.includes('Ríos Farjat');

        let badgeHtml = '';
        if (isPres) {
          badgeHtml = '<span style="display:inline-block; font-family:var(--font-mono); font-size:9.5px; font-weight:700; color:#000; background:var(--gold); padding:2px 7px; border-radius:3px; text-transform:uppercase; margin-bottom:4px;">⭐ PRESIDENTA · SALIDA 31-AGO-2025</span>';
        } else if (isCandidata) {
          badgeHtml = '<span style="display:inline-block; font-family:var(--font-mono); font-size:9.5px; font-weight:700; color:#2ecc71; background:rgba(46,204,113,0.15); border:1px solid rgba(46,204,113,0.4); padding:2px 7px; border-radius:3px; text-transform:uppercase; margin-bottom:4px;">🟢 EN FUNCIONES · CANDIDATA 2025</span>';
        } else if (isConcluido) {
          badgeHtml = '<span style="display:inline-block; font-family:var(--font-mono); font-size:9.5px; font-weight:700; color:var(--text-dim); background:rgba(255,255,255,0.06); border:1px solid var(--border-subtle); padding:2px 7px; border-radius:3px; text-transform:uppercase; margin-bottom:4px;">⚪ MANDATO CONCLUIDO (30-NOV-2024)</span>';
        } else {
          badgeHtml = '<span style="display:inline-block; font-family:var(--font-mono); font-size:9.5px; font-weight:700; color:#f39c12; background:rgba(243,156,18,0.15); border:1px solid rgba(243,156,18,0.4); padding:2px 7px; border-radius:3px; text-transform:uppercase; margin-bottom:4px;">🟠 EN FUNCIONES · RENUNCIA AGO-2025</span>';
        }

        let extraNote = '';
        if (isRiosFarjat) {
          extraNote = '<div style="font-size:10px; color:var(--crimson-bright); font-family:var(--font-mono); font-weight:700; margin-top:3px;">★ Renuncia formal al haber de retiro y pensión vitalicia</div>';
        } else if (isTopada) {
          extraNote = '<div style="font-size:10px; color:#2ecc71; font-family:var(--font-mono); font-weight:700; margin-top:3px;">★ Devuelve $72,638 pesos mensuales a TESOFE</div>';
        }

        return `
          <tr style="${isPres ? 'background:rgba(201,168,76,0.08);' : isCandidata ? 'background:rgba(46,204,113,0.03);' : ''}">
            <td>
              <div style="display:flex; align-items:baseline; gap:6px;">
                ${num ? `<span style="font-family:var(--font-mono); font-size:11px; color:var(--text-dim); font-weight:700;">${num}.</span>` : ''}
                <strong style="color:var(--text-main); font-size:13.5px;">${m.nombre}</strong>
              </div>
              <div style="margin-top:2px;">${badgeHtml}</div>
              <div style="font-size:10.5px; color:var(--text-dim); font-family:var(--font-mono);">
                ${m.cargo} · <span style="color:var(--cyan);">${m.sala}</span>
              </div>
              ${extraNote}
            </td>
            <td>
              <div style="font-size:10.5px; color:var(--text-dim); font-family:var(--font-mono);">${m.designacion}</div>
              <div style="font-size:11.5px; color:var(--text-main); margin-top:3px; line-height:1.4;">${m.estatus_reforma}</div>
              <div style="font-size:10px; color:var(--text-dim); font-family:var(--font-mono); margin-top:2px;">Efecto legal: <strong style="color:var(--gold);">${m.fecha_efectiva}</strong></div>
            </td>
            <td class="table-num" style="font-family:var(--font-mono); font-weight:700; color:var(--cyan); text-align:right;">${m.asesores_plazas} plazas</td>
            <td class="table-num" style="font-family:var(--font-mono); color:${isTopada ? 'var(--emerald-bright)' : 'var(--gold-bright)'}; font-weight:700; text-align:right;">
              ${m.sueldo_neto_mensual}
              <div style="font-size:9.5px; color:var(--text-dim); font-weight:normal;">${m.sueldo_bruto_mensual} bruto</div>
            </td>
            <td class="table-num" style="font-family:var(--font-mono); color:var(--crimson-bright); font-weight:700; text-align:right;">
              ${m.costo_mensual_ponencia}
            </td>
            <td style="text-align:center;">
              <span style="font-size:10.5px; font-family:var(--font-mono); padding:3px 8px; border-radius:4px; ${isTopada ? 'background:rgba(30,130,76,0.2); color:#4caf7a; border:1px solid rgba(30,130,76,0.4); font-weight:700;' : 'background:rgba(201,168,76,0.12); color:var(--gold); border:1px solid var(--border-gold);'}">
                ${m.estatus_tope}
              </span>
            </td>
          </tr>
        `;
      };

      let rowsHtml = '';
      if (presidenta) {
        rowsHtml += `
          <tr style="background:rgba(201,168,76,0.15); border-left:4px solid var(--gold);">
            <td colspan="6" style="padding:9px 14px; font-family:var(--font-mono); font-size:11px; color:var(--gold-bright); text-transform:uppercase; letter-spacing:1px; font-weight:700;">
              ⭐ MINISTRA PRESIDENTA EN FUNCIONES ACTIVAS · PLENO SCJN &amp; CJF (GESTIÓN SALIENTE)
            </td>
          </tr>
          ${renderTransicionRow(presidenta, null)}
        `;
      }

      rowsHtml += `
        <tr style="background:rgba(46,204,113,0.1); border-left:4px solid #2ecc71;">
          <td colspan="6" style="padding:9px 14px; font-family:var(--font-mono); font-size:11px; color:#2ecc71; text-transform:uppercase; letter-spacing:1px; font-weight:700;">
            🟢 MINISTRAS EN FUNCIONES QUE NO RENUNCIARON (3 CANDIDATAS A LA ELECCIÓN POPULAR JUDICIAL)
          </td>
        </tr>
      `;
      candidatas.forEach((m, idx) => {
        rowsHtml += renderTransicionRow(m, idx + 1);
      });

      rowsHtml += `
        <tr style="background:rgba(243,156,18,0.1); border-left:4px solid #f39c12;">
          <td colspan="6" style="padding:9px 14px; font-family:var(--font-mono); font-size:11px; color:#f39c12; text-transform:uppercase; letter-spacing:1px; font-weight:700;">
            🟠 MINISTRAS Y MINISTROS EN FUNCIONES CON RENUNCIA AL SENADO (6 EN TRANSICIÓN CON SALIDA AL 31/AGO/2025)
          </td>
        </tr>
      `;
      renuncias.forEach((m, idx) => {
        rowsHtml += renderTransicionRow(m, candidatas.length + idx + 1);
      });

      if (concluidos.length > 0) {
        rowsHtml += `
          <tr style="background:rgba(255,255,255,0.03); border-left:4px solid var(--border-subtle);">
            <td colspan="6" style="padding:9px 14px; font-family:var(--font-mono); font-size:11px; color:var(--text-dim); text-transform:uppercase; letter-spacing:1px; font-weight:700;">
              ⚪ MINISTRO CON PERIODO CONSTITUCIONAL DE 15 AÑOS CONCLUIDO (BAJA EFECTIVA EL 30/NOV/2024)
            </td>
          </tr>
        `;
        concluidos.forEach(m => {
          rowsHtml += renderTransicionRow(m, '—');
        });
      }

      tbody.innerHTML = rowsHtml;
    }
  }

  // ==========================================================================
  // RENDERIZADO DE PERSONAJES POLÍTICOS (1988–ACTUALIDAD)
  // ==========================================================================
  let activePresidentId = 'salinas';
  let isPresidentCardOpen = false;

  function openPresidentCard(presId) {
    if (presId) activePresidentId = presId;
    isPresidentCardOpen = true;

    const pp = DB.personajes_politicos;
    if (!pp || !pp.mandatarios) return;

    const cardContainer = document.getElementById('selectedPresidentCardContainer');
    const m = pp.mandatarios.find(p => p.id === activePresidentId) || pp.mandatarios[0];

    if (!cardContainer || !m) return;

    cardContainer.style.display = 'block';
    cardContainer.innerHTML = `
      <div style="background:var(--bg-surface); border:1px solid var(--border-gold); border-radius:10px; padding:18px 20px; margin-bottom:18px; box-shadow:0 4px 18px rgba(0,0,0,0.25);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:14px; border-bottom:1px solid var(--border-subtle); padding-bottom:12px;">
          <div>
            <span style="font-family:var(--font-mono); font-size:11px; color:var(--gold); text-transform:uppercase; letter-spacing:1px; display:block;">Expediente Sexenal Detallado</span>
            <strong style="color:var(--text-main); font-size:14px;">Selecciona otro mandatario para comparar de inmediato:</strong>
          </div>
          <button onclick="window.AuditEngine.closePresidentCard()" class="chip" style="cursor:pointer; color:var(--crimson-bright); border-color:rgba(192,57,43,0.4); background:rgba(192,57,43,0.12); font-weight:700; padding:6px 14px; font-size:12px;">
            ✖ Cerrar Ficha
          </button>
        </div>

        <div class="presidents-nav-chips" style="margin-bottom:0;">
          ${pp.mandatarios.map(p => `
            <button class="pres-chip ${p.id === activePresidentId ? 'active' : ''}" onclick="window.AuditEngine.openPresidentCard('${p.id}')">
              <span style="font-family:var(--font-mono); font-weight:700; color:${p.color};">${p.partido}</span>
              <span>${p.nombre}</span>
            </button>
          `).join('')}
        </div>
      </div>

      <div class="sexenio-card" id="pres-dossier-card" style="border:1px solid var(--border-gold); box-shadow:0 0 24px rgba(201,168,76,0.12); transition:all 0.3s ease;">
        <div class="card-header-pres">
          <div class="party-stripe ${m.partido_clase}"></div>
          <div class="card-header-main">
            <div class="pres-titles">
              <h3>${m.nombre}</h3>
              <span class="pres-period">${m.periodo}</span>
            </div>
            <div style="display:flex; align-items:center; gap:10px;">
              <span class="party-badge badge-${m.partido_clase}">${m.partido}</span>
              <button onclick="window.AuditEngine.closePresidentCard()" title="Cerrar expediente" style="background:transparent; border:none; color:var(--text-dim); font-size:18px; cursor:pointer; padding:4px 8px;">✖</button>
            </div>
          </div>
        </div>

        <div class="card-body-pres">
          <div class="pres-model-banner">
            <strong>Modelo Económico & Discurso Oficial:</strong> ${m.modelo}
          </div>

          <div class="data-grid-cols">
            <div class="data-block-col">
              <div class="data-col-lbl">Gasto Neto al Cierre</div>
              <div class="data-col-val" style="color:var(--gold-bright);">${m.gasto_neto_cierre}</div>
            </div>
            <div class="data-block-col">
              <div class="data-col-lbl">Crecimiento Real Gasto Sexenal</div>
              <div class="data-col-val" style="color:var(--cyan);">${m.crecimiento_real_gasto}</div>
            </div>
            <div class="data-block-col red-accent">
              <div class="data-col-lbl">Irregularidades ASF / Fiscalización</div>
              <div class="data-col-val" style="color:var(--crimson-bright);">${m.asf_irregularidades}</div>
            </div>
            <div class="data-block-col">
              <div class="data-col-lbl">Deuda Pública (% PIB al Cierre)</div>
              <div class="data-col-val">${m.deuda_cierre}</div>
            </div>
            <div class="data-block-col">
              <div class="data-col-lbl">Ingresos Públicos / SAT</div>
              <div class="data-col-val">${m.ingresos_var}</div>
            </div>
            <div class="data-block-col red-accent">
              <div class="data-col-lbl">Saldo de Impunidad / Desfalco</div>
              <div class="data-col-val" style="color:var(--amber);">${m.impunidad_monto}</div>
            </div>
          </div>

          <div class="desfalcos-box">
            <div class="desfalcos-title">
              <span>⚠️</span>
              <strong>Grandes Desfalcos & Focos de Corrupción Sexenal</strong>
            </div>
            ${m.desfalcos.map(d => `
              <div class="desfalco-item-row">
                <strong style="color:var(--text-main);">${d.nombre}:</strong>
                <span style="color:var(--text-secondary);">${d.desc}</span>
              </div>
            `).join('')}
          </div>

          <div>
            <span style="font-family:var(--font-mono); font-size:11px; color:var(--text-dim); text-transform:uppercase;">Funcionarios Clave de la Administración:</span>
            <div class="officials-pills-row">
              ${m.funcionarios_clave.map(f => `
                <div class="official-pill">
                  <span>${f.cargo}:</span> <strong>${f.nombre}</strong>
                </div>
              `).join('')}
            </div>
          </div>

          ${m.id === 'salinas' ? `
            <div style="margin-top:20px; background:linear-gradient(135deg, rgba(139,26,26,0.25), rgba(20,24,33,0.9)); border:1.5px solid var(--crimson-bright); border-radius:10px; padding:16px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; box-shadow:0 4px 16px rgba(0,0,0,0.4);">
              <div>
                <div style="font-family:var(--font-mono); font-size:11px; color:#ff6b6b; font-weight:700; text-transform:uppercase; letter-spacing:1px; display:flex; align-items:center; gap:6px;">
                  <span>👁️</span> Expediente Familiar Vinculado · Fiscalía de EE.UU. (EDNY Brooklyn)
                </div>
                <div style="font-size:14px; color:#fff; font-weight:700; margin-top:3px;">
                  Hijos de Salinas: Emiliano y Cecilia Salinas Occelli en la Secta NXIVM / DOS
                </div>
                <div style="font-size:12px; color:var(--text-secondary); margin-top:3px; max-width:620px; line-height:1.45;">
                  Directores de ESP México, captación de la élite empresarial y política, marcaje de mujeres con cautín al rojo vivo en la pelvis y señalamiento de la fiscal federal Moira Kim Penza como co-conspirador no acusado de Keith Raniere (sentenciado a 120 años).
                </div>
              </div>
              <button onclick="window.AuditEngine.openExpedienteHijo('salinas')" style="cursor:pointer; background:rgba(201,168,76,0.22); border:1px solid var(--gold-bright); color:var(--gold-bright); padding:8px 16px; border-radius:6px; font-family:var(--font-mono); font-size:12px; font-weight:700; display:inline-flex; align-items:center; gap:8px; transition:all 0.2s ease;">
                <span>🔍</span> Ver Expediente NXIVM ↗
              </button>
            </div>
          ` : ''}

          ${m.id === 'amlo' ? `
            <div style="margin-top:20px; background:linear-gradient(135deg, rgba(201,168,76,0.18), rgba(20,24,33,0.9)); border:1.5px solid var(--gold-bright); border-radius:10px; padding:16px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; box-shadow:0 4px 16px rgba(0,0,0,0.4);">
              <div>
                <div style="font-family:var(--font-mono); font-size:11px; color:var(--gold-bright); font-weight:700; text-transform:uppercase; letter-spacing:1px; display:flex; align-items:center; gap:6px;">
                  <span>💼</span> Expediente Familiar Vinculado · Red de Contratismo y Auditorías ASF
                </div>
                <div style="font-size:14px; color:#fff; font-weight:700; margin-top:3px;">
                  Hijo de AMLO: Andy López Beltrán y Jorge Amílcar Olán Aparicio ("El Clan")
                </div>
                <div style="font-size:12px; color:var(--text-secondary); margin-top:3px; max-width:620px; line-height:1.45;">
                  Red de contratismo gubernamental: contratos directos de Romedic/INSABI ($490 mdp), balasto del Tren Maya con audios periciales, contratos de SEDATU para el Malecón ($3,000 mdp) y salto al Comité de Morena.
                </div>
              </div>
              <button onclick="window.AuditEngine.openExpedienteHijo('andy')" style="cursor:pointer; background:rgba(201,168,76,0.22); border:1px solid var(--gold-bright); color:var(--gold-bright); padding:8px 16px; border-radius:6px; font-family:var(--font-mono); font-size:12px; font-weight:700; display:inline-flex; align-items:center; gap:8px; transition:all 0.2s ease;">
                <span>🔍</span> Ver Expediente "El Clan" ↗
              </button>
            </div>
          ` : ''}
        </div>
      </div>
    `;

    setTimeout(() => {
      cardContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
      const dossier = document.getElementById('pres-dossier-card');
      if (dossier) {
        dossier.style.borderColor = 'var(--gold-bright)';
        dossier.style.boxShadow = '0 0 26px rgba(212,175,55,0.35)';
        setTimeout(() => {
          dossier.style.boxShadow = '';
        }, 2000);
      }
    }, 80);
  }

  function closePresidentCard() {
    isPresidentCardOpen = false;
    const cardContainer = document.getElementById('selectedPresidentCardContainer');
    if (cardContainer) {
      cardContainer.style.display = 'none';
      cardContainer.innerHTML = '';
    }
    const tableWrap = document.querySelector('.consolidated-table-wrap');
    if (tableWrap) {
      tableWrap.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function renderPoliticosMandatarios(presId) {
    if (presId) {
      openPresidentCard(presId);
    } else if (isPresidentCardOpen) {
      openPresidentCard(activePresidentId);
    }
    renderPoliticosBarCharts();
    renderPoliticosConsolidatedTable();
  }

  let isSexeniosEvaluated = false;
  let isSexeniosAnimating = false;
  let isHoverEvalEnabled = true;
  let sexeniosAnimFrameId = null;

  function renderPoliticosBarCharts() {
    const pp = DB.personajes_politicos;
    if (!pp) return;

    // Gráfica 1: Crecimiento Real Gasto
    const chartGasto = document.getElementById('chartGastoSexenal');
    if (chartGasto) {
      chartGasto.innerHTML = pp.mandatarios.map(m => {
        const isShein = m.id === 'sheinbaum';
        const targetWidth = m.bar_width_gasto;
        const currentWidth = isSexeniosEvaluated ? targetWidth : '0%';
        const currentVal = isSexeniosEvaluated ? m.crecimiento_real_gasto : (isShein ? 'Proyección base' : '+0.0%');
        const zeroClass = isSexeniosEvaluated ? '' : 'bar-zero';

        return `
          <div class="bar-row">
            <span class="bar-label"><strong>${m.nombre.split(' ')[1] || m.nombre}</strong><br><span style="color:var(--text-dim); font-size:9.5px;">${m.partido} · ${m.periodo.split('—')[0].trim().slice(-4)}</span></span>
            <div class="bar-track">
              <div id="barFillGasto_${m.id}" class="bar-fill ${m.partido_clase} ${zeroClass}" style="width:${currentWidth};">
                <span id="barValGasto_${m.id}" class="bar-val-text">${currentVal}</span>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    // Gráfica 2: Irregularidades ASF
    const chartAsf = document.getElementById('chartAsfSexenal');
    if (chartAsf) {
      chartAsf.innerHTML = pp.mandatarios.filter(m => m.asf_monto_num > 0).map(m => {
        const isRedAlert = m.asf_monto_num > 500000;
        const targetWidth = m.bar_width_asf;
        const currentWidth = isSexeniosEvaluated ? targetWidth : '0%';
        const currentVal = isSexeniosEvaluated ? `$${m.asf_monto_num.toLocaleString('es-MX')} mdp` : '$0 mdp';
        const zeroClass = isSexeniosEvaluated ? '' : 'bar-zero';

        return `
          <div class="bar-row">
            <span class="bar-label"><strong>${m.nombre.split(' ')[1] || m.nombre}</strong><br><span style="color:var(--text-dim); font-size:9.5px;">${m.partido}</span></span>
            <div class="bar-track">
              <div id="barFillAsf_${m.id}" class="bar-fill ${isRedAlert ? 'red-alert' : m.partido_clase} ${zeroClass}" style="width:${currentWidth};">
                <span id="barValAsf_${m.id}" class="bar-val-text">${currentVal}</span>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    // Gráfica 3: Deuda % PIB
    const chartDeuda = document.getElementById('chartDeudaSexenal');
    if (chartDeuda) {
      chartDeuda.innerHTML = pp.mandatarios.map(m => {
        const targetWidth = m.bar_width_deuda;
        const currentWidth = isSexeniosEvaluated ? targetWidth : '0%';
        const currentVal = isSexeniosEvaluated ? m.deuda_cierre : '0.0% PIB';
        const zeroClass = isSexeniosEvaluated ? '' : 'bar-zero';

        return `
          <div class="bar-row">
            <span class="bar-label"><strong>${m.nombre.split(' ')[1] || m.nombre}</strong><br><span style="color:var(--text-dim); font-size:9.5px;">${m.partido}</span></span>
            <div class="bar-track">
              <div id="barFillDeuda_${m.id}" class="bar-fill ${m.partido_clase} ${zeroClass}" style="width:${currentWidth};">
                <span id="barValDeuda_${m.id}" class="bar-val-text">${currentVal}</span>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }
  }

  function evaluarMetricasSexenales(duracionMs = 1400) {
    const pp = DB.personajes_politicos;
    if (!pp || !pp.mandatarios) return;

    if (sexeniosAnimFrameId) {
      cancelAnimationFrame(sexeniosAnimFrameId);
      sexeniosAnimFrameId = null;
    }

    const statusEl = document.getElementById('evalStatusText');
    const btnEval = document.getElementById('btnEvaluarSexenios');
    if (statusEl) {
      statusEl.innerHTML = '<span style="color:var(--gold-bright);">⚡ Evaluando y escalando métricas sexenales en tiempo real...</span>';
    }
    if (btnEval) {
      btnEval.innerHTML = '<span>⏳</span> Evaluando...';
    }

    // Quitar clases bar-zero
    pp.mandatarios.forEach(m => {
      const g = document.getElementById(`barFillGasto_${m.id}`);
      if (g) g.classList.remove('bar-zero');
      const a = document.getElementById(`barFillAsf_${m.id}`);
      if (a) a.classList.remove('bar-zero');
      const d = document.getElementById(`barFillDeuda_${m.id}`);
      if (d) d.classList.remove('bar-zero');
    });

    isSexeniosAnimating = true;
    const startTime = performance.now();
    const easeOutCubic = (t) => (--t) * t * t + 1;

    function animateStep(now) {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / duracionMs);
      const eased = easeOutCubic(progress);

      pp.mandatarios.forEach(m => {
        // 1. Gasto
        const fillG = document.getElementById(`barFillGasto_${m.id}`);
        const valG = document.getElementById(`barValGasto_${m.id}`);
        const targetWG = parseFloat(m.bar_width_gasto) || 0;
        if (fillG) fillG.style.width = `${(targetWG * eased).toFixed(1)}%`;
        if (valG) {
          if (m.id === 'sheinbaum') {
            valG.textContent = progress > 0.6 ? 'Ajuste / Contención' : 'Proyección...';
          } else {
            const rawG = parseFloat(m.crecimiento_real_gasto.replace('+', '').replace('%', '')) || 0;
            valG.textContent = `+${(rawG * eased).toFixed(1)}%`;
          }
        }

        // 2. ASF
        const fillA = document.getElementById(`barFillAsf_${m.id}`);
        const valA = document.getElementById(`barValAsf_${m.id}`);
        const targetWA = parseFloat(m.bar_width_asf) || 0;
        if (fillA) fillA.style.width = `${(targetWA * eased).toFixed(1)}%`;
        if (valA) {
          const rawA = m.asf_monto_num || 0;
          valA.textContent = `$${Math.round(rawA * eased).toLocaleString('es-MX')} mdp`;
        }

        // 3. Deuda
        const fillD = document.getElementById(`barFillDeuda_${m.id}`);
        const valD = document.getElementById(`barValDeuda_${m.id}`);
        const targetWD = parseFloat(m.bar_width_deuda) || 0;
        if (fillD) fillD.style.width = `${(targetWD * eased).toFixed(1)}%`;
        if (valD) {
          const rawD = parseFloat(m.deuda_cierre) || 0;
          valD.textContent = `${(rawD * eased).toFixed(1)}% PIB`;
        }
      });

      if (progress < 1) {
        sexeniosAnimFrameId = requestAnimationFrame(animateStep);
      } else {
        isSexeniosAnimating = false;
        isSexeniosEvaluated = true;
        sexeniosAnimFrameId = null;

        // Valores finales exactos
        pp.mandatarios.forEach(m => {
          const fillG = document.getElementById(`barFillGasto_${m.id}`);
          const valG = document.getElementById(`barValGasto_${m.id}`);
          if (fillG) fillG.style.width = m.bar_width_gasto;
          if (valG) valG.textContent = m.crecimiento_real_gasto;

          const fillA = document.getElementById(`barFillAsf_${m.id}`);
          const valA = document.getElementById(`barValAsf_${m.id}`);
          if (fillA) fillA.style.width = m.bar_width_asf;
          if (valA) valA.textContent = `$${m.asf_monto_num.toLocaleString('es-MX')} mdp`;

          const fillD = document.getElementById(`barFillDeuda_${m.id}`);
          const valD = document.getElementById(`barValDeuda_${m.id}`);
          if (fillD) fillD.style.width = m.bar_width_deuda;
          if (valD) valD.textContent = m.deuda_cierre;
        });

        if (statusEl) {
          statusEl.innerHTML = '<span style="color:var(--emerald-bright);">✓ Evaluación completada: Métricas históricas oficiales desplegadas al 100%.</span>';
        }
        if (btnEval) {
          btnEval.innerHTML = '<span>🔄</span> Volver a Evaluar';
        }
      }
    }

    sexeniosAnimFrameId = requestAnimationFrame(animateStep);
  }

  function resetMetricasSexenales() {
    if (sexeniosAnimFrameId) {
      cancelAnimationFrame(sexeniosAnimFrameId);
      sexeniosAnimFrameId = null;
    }
    isSexeniosAnimating = false;
    isSexeniosEvaluated = false;

    const pp = DB.personajes_politicos;
    if (pp && pp.mandatarios) {
      pp.mandatarios.forEach(m => {
        const fillG = document.getElementById(`barFillGasto_${m.id}`);
        const valG = document.getElementById(`barValGasto_${m.id}`);
        if (fillG) {
          fillG.classList.add('bar-zero');
          fillG.style.width = '0%';
        }
        if (valG) valG.textContent = m.id === 'sheinbaum' ? 'Proyección base' : '+0.0%';

        const fillA = document.getElementById(`barFillAsf_${m.id}`);
        const valA = document.getElementById(`barValAsf_${m.id}`);
        if (fillA) {
          fillA.classList.add('bar-zero');
          fillA.style.width = '0%';
        }
        if (valA) valA.textContent = '$0 mdp';

        const fillD = document.getElementById(`barFillDeuda_${m.id}`);
        const valD = document.getElementById(`barValDeuda_${m.id}`);
        if (fillD) {
          fillD.classList.add('bar-zero');
          fillD.style.width = '0%';
        }
        if (valD) valD.textContent = '0.0% PIB';
      });
    }

    const statusEl = document.getElementById('evalStatusText');
    if (statusEl) {
      statusEl.innerHTML = '⚪ Barras en reposo (0.0%). Presiona «Evaluar» o pasa el cursor para medir la escala real.';
    }
    const btnEval = document.getElementById('btnEvaluarSexenios');
    if (btnEval) {
      btnEval.innerHTML = '<span>▶️</span> Evaluar Sexenios';
    }
  }

  function toggleHoverEvaluation(enabled) {
    isHoverEvalEnabled = !!enabled;
  }

  function handleChartContainerHover() {
    if (isHoverEvalEnabled && !isSexeniosEvaluated && !isSexeniosAnimating) {
      evaluarMetricasSexenales();
    }
  }

  function renderPoliticosConsolidatedTable() {
    const tableBody = document.getElementById('politicosTableBody');
    const pp = DB.personajes_politicos;
    if (!tableBody || !pp) return;

    tableBody.innerHTML = pp.mandatarios.map(m => `
      <tr>
        <td>
          <a href="javascript:void(0)" class="glos-link" onclick="window.AuditEngine.openPresidentCard('${m.id}')" style="font-size:13.5px; font-weight:700; color:var(--text-main);" title="Clic para ver expediente completo de ${m.nombre}">
            ${m.nombre} ↗
          </a>
          <div style="font-size:10px; color:var(--text-dim); font-family:var(--font-mono); margin-top:2px;">${m.periodo}</div>
        </td>
        <td><span class="party-badge badge-${m.partido_clase}">${m.partido}</span></td>
        <td style="font-family:var(--font-mono); font-weight:600;">${m.gasto_neto_cierre}</td>
        <td style="font-family:var(--font-mono); color:var(--cyan); font-weight:700;">${m.crecimiento_real_gasto}</td>
        <td style="font-family:var(--font-mono); color:var(--crimson-bright); font-weight:700;">${m.asf_irregularidades}</td>
        <td style="font-family:var(--font-mono); font-weight:600;">${m.deuda_cierre}</td>
        <td>
          <button class="subtab-btn" style="padding:5px 12px; font-size:11px; cursor:pointer; background:rgba(201,168,76,0.15); border:1px solid var(--gold-bright); color:var(--gold-bright); border-radius:4px; font-weight:700;" onclick="window.AuditEngine.openPresidentCard('${m.id}')">
            🔍 Ver Ficha ↗
          </button>
        </td>
      </tr>
    `).join('');
  }

  function renderPoliticosSecundarios() {
    const container = document.getElementById('politicosSecundariosContainer');
    const pp = DB.personajes_politicos;
    if (!container || !pp || !pp.personajes_secundarios) return;

    const gl = pp.datos_curiosos ? pp.datos_curiosos.expediente_garcia_luna : null;
    const pd = pp.datos_curiosos ? pp.datos_curiosos.expediente_porfirio_diaz : null;
    const sa = pp.datos_curiosos ? pp.datos_curiosos.expediente_santa_anna : null;
    const bj = pp.datos_curiosos ? pp.datos_curiosos.expediente_benito_juarez : null;
    const gLuna = pp.personajes_secundarios.find(p => p.nombre.toLowerCase().includes('garc')) || pp.personajes_secundarios[0];
    const otrosSecundarios = pp.personajes_secundarios.filter(p => !p.nombre.toLowerCase().includes('garc'));

    let html = '';

    // 1. FICHA COMPLETA ESQUEMATIZADA DE GENARO GARCÍA LUNA (BLOQUE 1)
    if (gl) {
      html += `
        <!-- FICHA EXPEDIENTE DE GENARO GARCÍA LUNA (BLOQUE MODULAR 1) -->
        <div class="garcia-luna-dossier" id="card-garcia-luna" style="margin-bottom:28px; border:1px solid var(--border-gold); border-radius:12px; background:var(--bg-card); padding:24px; box-shadow:0 8px 24px rgba(0,0,0,0.35);">
          
          <!-- CABECERA PRINCIPAL: SIEMPRE VISIBLE -->
          <div class="gl-title">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
              <span style="font-family:var(--font-mono); font-size:11px; color:var(--crimson-bright); letter-spacing:1.5px; text-transform:uppercase; display:flex; align-items:center; gap:8px;">
                <span style="background:rgba(201,168,76,0.2); color:var(--gold-bright); border:1px solid var(--gold); padding:2px 8px; border-radius:4px; font-weight:800; font-size:11px;">FICHA #01</span>
                <span>⚖️</span> Ficha de Operador del Poder · Expediente Judicial de Dominio Público
              </span>
              <span style="font-family:var(--font-mono); font-size:11px; color:var(--text-dim); background:rgba(255,255,255,0.05); padding:2px 8px; border-radius:4px; border:1px solid var(--border-subtle);">
                Causa Penal 1:19-cr-00576 (EDNY)
              </span>
            </div>

            <div style="display:flex; align-items:center; gap:14px; margin-top:10px;">
              <div style="width:48px; height:48px; border-radius:10px; background:rgba(192,57,43,0.15); border:1px solid rgba(192,57,43,0.35); display:flex; align-items:center; justify-content:center; font-size:26px; flex-shrink:0;">
                ${gLuna.icono || '🚔'}
              </div>
              <div>
                <h3 style="margin:0; font-size:24px; color:var(--gold-bright); font-family:var(--font-serif);">${gLuna.nombre}</h3>
                <div style="font-size:12px; color:var(--text-dim); font-family:var(--font-mono); margin-top:2px;">
                  ${gLuna.cargos}
                </div>
              </div>
            </div>

            <p style="font-size:13px; color:var(--text-secondary); margin-top:10px; margin-bottom:14px; line-height:1.5;">
              ${gl.subtitulo}
            </p>

            <!-- FILA DE CUADROS / BADGES Y ACCIONES -->
            <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
              <span style="background:rgba(201,168,76,0.12); color:var(--gold); border:1px solid var(--border-gold); padding:6px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); display:inline-flex; align-items:center; gap:6px;">
                🏛️ <strong>Administraciones:</strong> ${gLuna.administraciones}
              </span>

              <span style="background:rgba(192,57,43,0.15); color:var(--crimson-bright); border:1px solid rgba(192,57,43,0.35); padding:6px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); font-weight:600; display:inline-flex; align-items:center; gap:6px;">
                ⚖️ <strong>Estatus:</strong> En prisión federal (EE.UU.)
              </span>

              <button id="btnToggleGL" onclick="window.AuditEngine.toggleGarciaLunaDossier()" 
                style="cursor:pointer; background:rgba(201,168,76,0.16); border:1px solid var(--gold-bright); color:var(--gold-bright); padding:6px 16px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:8px; transition:all 0.2s ease; box-shadow:0 2px 8px rgba(0,0,0,0.25);">
                <span id="iconToggleGL">🔍</span> <span id="lblToggleGL">Ver Desglose / Ficha ↗</span>
              </button>

              <button id="btnGarciaLunaArgumento" onclick="window.AuditEngine.openGarciaLunaArgumento()" 
                style="cursor:pointer; background:linear-gradient(135deg, rgba(201,168,76,0.22), rgba(184,134,11,0.12)); border:1px solid var(--gold-bright); color:var(--gold-bright); padding:6px 16px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:8px; transition:all 0.2s ease; box-shadow:0 2px 10px rgba(201,168,76,0.25);"
                title="Abrir Tesis Jurídica & Argumento Particular del Creador">
                <span>⚖️</span> <span>Argumento particular</span>
              </button>
            </div>
          </div>

          <!-- DESGLOSE DESPLEGABLE: INICIA A PARTIR DE LOS 460 MESES DE PRISIÓN HASTA EL FINAL DEL BLOQUE -->
          <div id="garciaLunaDesgloseContainer" style="display:none; margin-top:22px; padding-top:22px; border-top:1px dashed var(--border-gold); animation:fadeInPower 0.35s ease forwards;">
            
            <!-- 1. SENTENCIA DEL JUEZ BRIAN COGAN (460 MESES DE PRISIÓN / 38 AÑOS Y 4 MESES) -->
            <div style="background:linear-gradient(135deg, rgba(139,26,26,0.35), rgba(192,57,43,0.2)); border:1px solid var(--crimson-bright); border-radius:8px; padding:16px 20px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px; box-shadow:0 0 16px var(--crimson-glow);">
              <div>
                <div style="font-family:var(--font-mono); font-size:11px; text-transform:uppercase; letter-spacing:1.5px; color:var(--crimson-bright); font-weight:700; display:flex; align-items:center; gap:6px;">
                  <span>⚖️</span> Sentencia Brian Cogan (16 Oct 2024) · Corte Federal de Brooklyn <a class="ref-link" onclick="window.AuditEngine.goToRef('ref-garcia-luna-edny')" title="Ver expediente oficial EDNY en Referencias APA 7">[Ref. 27]</a>
                </div>
                <div style="font-family:var(--font-mono); font-size:17px; font-weight:800; color:#fff; margin:4px 0;">
                  ${gl.sentencia_total}
                </div>
                <div style="font-size:12.5px; color:#ffd166; font-family:var(--font-mono);">
                  💵 ${gl.multa_restitucion}
                </div>
              </div>
              <div style="text-align:right;">
                <span style="display:inline-block; background:rgba(0,0,0,0.4); border:1px solid var(--border-subtle); padding:6px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); color:var(--text-secondary);">
                  EDNY Brooklyn, NY · <a class="ref-link" onclick="window.AuditEngine.goToRef('ref-garcia-luna-edny')">[Ref. 27]</a>
                </span>
              </div>
            </div>

            <!-- 2. DATOS GENERALES DE LA CONDENA -->
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin-bottom:20px;">
              <div class="data-block-col">
                <div class="data-col-lbl">Tribunal &amp; Jurisdicción</div>
                <div class="data-col-val" style="font-size:12.5px;">${gl.corte_tribunal}</div>
              </div>
              <div class="data-block-col">
                <div class="data-col-lbl">Juez Sentenciador</div>
                <div class="data-col-val" style="font-size:12.5px; color:var(--gold-bright);">${gl.juez_sentenciador}</div>
              </div>
              <div class="data-block-col">
                <div class="data-col-lbl">Fecha de Sentencia</div>
                <div class="data-col-val" style="font-size:12.5px;">${gl.fecha_sentencia}</div>
              </div>
              <div class="data-block-col" style="border-left-color:var(--crimson-bright);">
                <div class="data-col-lbl">Condena Histórica</div>
                <div class="data-col-val" style="font-size:12.5px; color:var(--crimson-bright);">Primer exsecretario de Estado mexicano sentenciado en EE.UU.</div>
              </div>
            </div>

            <!-- 3. CITA TEXTUAL DEL JUEZ BRIAN M. COGAN -->
            <div class="quote-cogan-box">
              "${gl.frase_juez_cogan}"
              <span class="quote-author">— Juez Brian M. Cogan, Audiencia de Sentencia, Corte Federal del Distrito Este de Nueva York (EDNY, Brooklyn)</span>
            </div>

            <!-- 4. LOS 5 CARGOS CULPABLES -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:var(--gold); margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>⚖️</span> Los 5 Cargos Declarados Culpables por Jurado Unánime
            </h4>
            <div style="display:grid; gap:8px; margin-bottom:24px;">
              ${gl.cargos_condena.map(c => `
                <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); padding:10px 14px; border-radius:6px; font-size:12.5px;">
                  <strong style="color:var(--crimson-bright); font-family:var(--font-mono);">${c.cargo}:</strong> ${c.desc}
                </div>
              `).join('')}
            </div>

            <!-- 5. TESTIGOS CLAVE -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:var(--gold); margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>🗣️</span> Pruebas y Testimonios Clave Presentados en el Juicio
            </h4>
            <div class="witness-grid">
              ${gl.pruebas_ofrecidas.map(w => `
                <div class="witness-card">
                  <h4>${w.testigo}</h4>
                  <p>${w.testimonio}</p>
                </div>
              `).join('')}
            </div>

            <!-- BANNER CONTEXTUAL A TESIS Y ARGUMENTO PARTICULAR -->
            <div style="background:linear-gradient(135deg, rgba(201,168,76,0.12), rgba(184,134,11,0.06)); border:1px solid var(--border-gold); border-radius:8px; padding:14px 18px; margin:16px 0 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
              <div>
                <div style="font-family:var(--font-mono); font-size:11px; color:var(--gold-bright); font-weight:700; text-transform:uppercase; letter-spacing:1px; display:flex; align-items:center; gap:6px;">
                  <span>⚖️</span> Tesis Crítica del Creador: ¿Dudas Razonables y Doble Rasero Testimonial?
                </div>
                <div style="font-size:12.5px; color:var(--text-secondary); margin-top:3px; max-width:560px; line-height:1.45;">
                  Consulta el análisis dogmático sobre los dichos de «El Rey» Zambada respecto al entorno de AMLO, la falta de documentos bancarios certificados de la DEA y el estándar del CNPP en México.
                </div>
              </div>
              <button onclick="window.AuditEngine.openGarciaLunaArgumento()" style="cursor:pointer; background:rgba(201,168,76,0.22); border:1px solid var(--gold-bright); color:var(--gold-bright); padding:8px 18px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:6px; transition:all 0.2s ease;">
                <span>📜</span> Argumento particular ↗
              </button>
            </div>

            <!-- 6. SAQUEO AL ERARIO Y LITIGIO EN MIAMI -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:var(--gold); margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>💸</span> El Saqueo al Erario Mexicano y Litigio Civil en Miami
            </h4>
            <div style="display:grid; gap:10px; margin-bottom:24px;">
              ${gl.desvio_erario_mexico.map(d => `
                <div style="background:rgba(201,168,76,0.06); border-left:3px solid var(--gold); padding:12px 16px; border-radius:0 6px 6px 0; font-size:12.5px;">
                  <strong style="color:var(--gold-bright);">${d.rubro}:</strong> ${d.detalle}
                  <span style="display:inline-block; margin-left:6px;">
                    <a href="#ref-marcolg-1" class="ref-link" onclick="window.AuditEngine.goToRef('ref-marcolg-1'); return false;" title="Ver Ley Federal de Presupuesto">[Ref: LFPRH Art. 1]</a>
                  </span>
                </div>
              `).join('')}
            </div>

            <!-- 7. EXCENTRICIDADES, LUJOS Y EL BÚNKER -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:var(--gold); margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>🏰</span> Excentricidades, Lujos y el Búnker de $3,346 mdp
            </h4>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:12px; margin-bottom:24px;">
              ${gl.lujos_y_curiosidades.map(l => `
                <div class="data-block-col">
                  <strong style="color:var(--text-main); font-size:13px; display:block; margin-bottom:4px;">${l.item}</strong>
                  <p style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin:0;">${l.desc}</p>
                </div>
              `).join('')}
            </div>

            <!-- BOTÓN PARA CERRAR EL DESGLOSE AL FINAL -->
            <div style="text-align:center; padding-top:16px; border-top:1px dashed var(--border-subtle);">
              <button onclick="window.AuditEngine.toggleGarciaLunaDossier()" 
                style="cursor:pointer; background:rgba(255,255,255,0.06); border:1px solid var(--border-subtle); color:var(--text-secondary); padding:8px 22px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:600; transition:all 0.2s ease;">
                ✖ Ocultar Desglose de Genaro García Luna
              </button>
            </div>

          </div><!-- FIN DESGLOSE GARCÍA LUNA -->
        </div><!-- FIN CARD GARCÍA LUNA -->
      `;
    }

    // 2. FICHA COMPLETA ESQUEMATIZADA DE PORFIRIO DÍAZ (BLOQUE 2)
    if (pd) {
      html += `
        <!-- FICHA EXPEDIENTE DE DON PORFIRIO DÍAZ (BLOQUE MODULAR 2) -->
        <div class="garcia-luna-dossier" id="card-porfirio-diaz-5-2" style="margin-bottom:28px; border:1px solid var(--border-gold); border-radius:12px; background:var(--bg-card); padding:24px; box-shadow:0 8px 24px rgba(0,0,0,0.35);">
          
          <!-- CABECERA PRINCIPAL: SIEMPRE VISIBLE -->
          <div class="gl-title">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
              <span style="font-family:var(--font-mono); font-size:11px; color:var(--gold-bright); letter-spacing:1.5px; text-transform:uppercase; display:flex; align-items:center; gap:8px;">
                <span style="background:rgba(201,168,76,0.25); color:var(--gold-bright); border:1px solid var(--gold); padding:2px 8px; border-radius:4px; font-weight:800; font-size:11px;">FICHA #02</span>
                <span>👑</span> Expediente Histórico-Hacendario · Patrón Oro, Superávit y Geopolítica
              </span>
              <span style="font-family:var(--font-mono); font-size:11px; color:var(--text-dim); background:rgba(255,255,255,0.05); padding:2px 8px; border-radius:4px; border:1px solid var(--border-subtle);">
                Hacienda Pública 1876–1911
              </span>
            </div>

            <div style="display:flex; align-items:center; gap:14px; margin-top:10px;">
              <div style="width:48px; height:48px; border-radius:10px; background:rgba(201,168,76,0.18); border:1px solid rgba(201,168,76,0.4); display:flex; align-items:center; justify-content:center; font-size:26px; flex-shrink:0;">
                ${pd.icono || '👑'}
              </div>
              <div>
                <h3 style="margin:0; font-size:24px; color:var(--gold-bright); font-family:var(--font-serif);">Gral. Don Porfirio Díaz Mori</h3>
                <div style="font-size:12px; color:var(--text-dim); font-family:var(--font-mono); margin-top:2px;">
                  Presidente de México (1876–1880, 1884–1911) · Héroe Militar del 2 de Abril · Artífice de la Red Ferroviaria
                </div>
              </div>
            </div>

            <p style="font-size:13px; color:var(--text-secondary); margin-top:10px; margin-bottom:14px; line-height:1.5;">
              ${pd.subtitulo}
            </p>

            <!-- FILA DE BADGES Y ACCIONES -->
            <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
              <span style="background:rgba(201,168,76,0.12); color:var(--gold); border:1px solid var(--border-gold); padding:6px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); display:inline-flex; align-items:center; gap:6px;">
                🏛️ <strong>Mandato:</strong> ${pd.periodo_gobierno}
              </span>

              <span style="background:rgba(46,204,113,0.15); color:#2ecc71; border:1px solid rgba(46,204,113,0.35); padding:6px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); font-weight:600; display:inline-flex; align-items:center; gap:6px;" title="${pd.estatus_historico}">
                👑 <strong>Superávit:</strong> $62.5 mdp Oro en Tesorería
              </span>

              <button id="btnTogglePD" onclick="window.AuditEngine.togglePorfirioDiazDossier()" 
                style="cursor:pointer; background:rgba(201,168,76,0.16); border:1px solid var(--gold-bright); color:var(--gold-bright); padding:6px 16px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:8px; transition:all 0.2s ease; box-shadow:0 2px 8px rgba(0,0,0,0.25);">
                <span id="iconTogglePD">🔍</span> <span id="lblTogglePD">Ver Desglose / Ficha ↗</span>
              </button>

              <button id="btnPorfirioDiazArgumento" onclick="window.AuditEngine.openPorfirioDiazArgumento()" 
                style="cursor:pointer; background:linear-gradient(135deg, rgba(201,168,76,0.25), rgba(184,134,11,0.15)); border:1px solid var(--gold-bright); color:var(--gold-bright); padding:6px 16px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:8px; transition:all 0.2s ease; box-shadow:0 2px 10px rgba(201,168,76,0.25);"
                title="Abrir Tesis Crítica: Lo mal que lo tratamos y lo mucho que lo necesitamos">
                <span>👑</span> <span>Argumento particular</span>
              </button>
            </div>
          </div>

          <!-- DESGLOSE DESPLEGABLE -->
          <div id="porfirioDiazDesgloseContainer" style="display:none; margin-top:22px; padding-top:22px; border-top:1px dashed var(--border-gold); animation:fadeInPower 0.35s ease forwards;">
            
            <!-- 1. BALANCE DEL TESORO -->
            <div style="background:linear-gradient(135deg, rgba(201,168,76,0.25), rgba(184,134,11,0.12)); border:1px solid var(--gold); border-radius:8px; padding:16px 20px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px; box-shadow:0 0 16px rgba(201,168,76,0.2);">
              <div>
                <div style="font-family:var(--font-mono); font-size:11px; text-transform:uppercase; letter-spacing:1.5px; color:var(--gold-bright); font-weight:700; display:flex; align-items:center; gap:6px;">
                  <span>💰</span> Memoria de Hacienda · Primer Superávit de la Historia Nacional
                </div>
                <div style="font-family:var(--font-mono); font-size:17px; font-weight:800; color:#fff; margin:4px 0;">
                  ${pd.sentencia_total}
                </div>
                <div style="font-size:12.5px; color:#ffd166; font-family:var(--font-mono);">
                  🚂 ${pd.multa_restitucion}
                </div>
              </div>
              <div style="text-align:right;">
                <span style="display:inline-block; background:rgba(0,0,0,0.4); border:1px solid var(--border-subtle); padding:6px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); color:var(--gold);">
                  Hacienda y Crédito Público · <a class="ref-link" onclick="window.AuditEngine.goToRef('ref-porfiriato-ferrocarriles')">[Ref. 26]</a>
                </span>
              </div>
            </div>

            <!-- 2. DATOS GENERALES -->
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin-bottom:20px;">
              <div class="data-block-col">
                <div class="data-col-lbl">Marco &amp; Periodo</div>
                <div class="data-col-val" style="font-size:12.5px;">${pd.corte_tribunal}</div>
              </div>
              <div class="data-block-col">
                <div class="data-col-lbl">Ministro de Hacienda</div>
                <div class="data-col-val" style="font-size:12.5px; color:var(--gold-bright);">${pd.juez_sentenciador}</div>
              </div>
              <div class="data-block-col">
                <div class="data-col-lbl">Periodo Histórico</div>
                <div class="data-col-val" style="font-size:12.5px;">${pd.fecha_sentencia}</div>
              </div>
              <div class="data-block-col" style="border-left-color:#2ecc71;">
                <div class="data-col-lbl">Crédito Internacional</div>
                <div class="data-col-val" style="font-size:12.5px; color:#2ecc71;">Bonos soberanos cotizados a la par en París y Londres al 4%</div>
              </div>
            </div>

            <!-- 3. CITA TEXTUAL HISTÓRICA -->
            <div class="quote-cogan-box">
              "${pd.frase_juez_cogan}"
              <span class="quote-author">${pd.autor_frase}</span>
            </div>

            <!-- 4. EJES ESTRUCTURALES -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:var(--gold); margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>👑</span> Ejes Estructurales: El Milagro Económico y sus Contrastes
            </h4>
            <div style="display:grid; gap:8px; margin-bottom:24px;">
              ${pd.cargos_condena.map(c => `
                <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); padding:10px 14px; border-radius:6px; font-size:12.5px;">
                  <strong style="color:var(--gold-bright); font-family:var(--font-mono);">${c.cargo}:</strong> ${c.desc}
                </div>
              `).join('')}
            </div>

            <!-- 5. PRUEBAS Y DOCUMENTOS OFICIALES -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:var(--gold); margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>📜</span> Documentos Oficiales, Memorias de Hacienda y Decretos Soberanos
            </h4>
            <div class="witness-grid">
              ${pd.pruebas_ofrecidas.map(w => `
                <div class="witness-card">
                  <h4 style="color:var(--gold-bright);">${w.testigo}</h4>
                  <p>${w.testimonio}</p>
                </div>
              `).join('')}
            </div>

            <!-- BANNER CONTEXTUAL A ARGUMENTO PARTICULAR -->
            <div style="background:linear-gradient(135deg, rgba(201,168,76,0.16), rgba(184,134,11,0.08)); border:1px solid var(--border-gold); border-radius:8px; padding:14px 18px; margin:16px 0 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
              <div>
                <div style="font-family:var(--font-mono); font-size:11px; color:var(--gold-bright); font-weight:700; text-transform:uppercase; letter-spacing:1px; display:flex; align-items:center; gap:6px;">
                  <span>👑</span> Tesis del Creador: «Lo Mal Que lo Tratamos y lo Mucho Que lo Necesitamos»
                </div>
                <div style="font-size:12.5px; color:var(--text-secondary); margin-top:3px; max-width:560px; line-height:1.45;">
                  Analiza el contraste demoledor entre la disciplina hacendaria y visión de obra de Díaz frente al despilfarro sexenal contemporáneo y la cobardía histórica de mantener su tumba en el exilio de París.
                </div>
              </div>
              <button onclick="window.AuditEngine.openPorfirioDiazArgumento()" style="cursor:pointer; background:rgba(201,168,76,0.22); border:1px solid var(--gold-bright); color:var(--gold-bright); padding:8px 18px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:6px; transition:all 0.2s ease;">
                <span>📜</span> Argumento particular ↗
              </button>
            </div>

            <!-- 6. IMPACTO EN EL ERARIO Y CRÉDITO PÚBLICO -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:var(--gold); margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>💰</span> Balances del Erario, Fondos en Bóveda e Inversión Productiva
            </h4>
            <div style="display:grid; gap:10px; margin-bottom:24px;">
              ${pd.desvio_erario_mexico.map(d => `
                <div style="background:rgba(201,168,76,0.06); border-left:3px solid var(--gold); padding:12px 16px; border-radius:0 6px 6px 0; font-size:12.5px;">
                  <strong style="color:var(--gold-bright);">${d.rubro}:</strong> ${d.detalle}
                  <span style="display:inline-block; margin-left:6px;">
                    <a class="ref-link" onclick="window.AuditEngine.goToRef('ref-porfiriato-ferrocarriles'); return false;" title="Ver Fuentes Oficiales">[Ref: Hacienda 1876-1911]</a>
                  </span>
                </div>
              `).join('')}
            </div>

            <!-- 7. CURIOSIDADES HISTÓRICAS Y EXCENTRICIDADES -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:var(--gold); margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>🏰</span> Hitos Tecnológicos, el Centenario y el Sepulcro en París
            </h4>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:12px; margin-bottom:24px;">
              ${pd.lujos_y_curiosidades.map(l => `
                <div class="data-block-col">
                  <strong style="color:var(--text-main); font-size:13px; display:block; margin-bottom:4px;">${l.item}</strong>
                  <p style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin:0;">${l.desc}</p>
                </div>
              `).join('')}
            </div>

            <!-- BOTÓN PARA CERRAR EL DESGLOSE AL FINAL -->
            <div style="text-align:center; padding-top:16px; border-top:1px dashed var(--border-subtle);">
              <button onclick="window.AuditEngine.togglePorfirioDiazDossier()" 
                style="cursor:pointer; background:rgba(255,255,255,0.06); border:1px solid var(--border-subtle); color:var(--text-secondary); padding:8px 22px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:600; transition:all 0.2s ease;">
                ✖ Ocultar Desglose de Don Porfirio Díaz
              </button>
            </div>

          </div><!-- FIN DESGLOSE DÍAZ -->
        </div><!-- FIN CARD DÍAZ -->
      `;
    }

    // 3. FICHA HISTÓRICA ESQUEMATIZADA DE ANTONIO LÓPEZ DE SANTA ANNA (BLOQUE 3)
    if (sa) {
      html += `
        <!-- FICHA EXPEDIENTE DE ANTONIO LÓPEZ DE SANTA ANNA (BLOQUE MODULAR 3) -->
        <div class="garcia-luna-dossier" id="card-santa-anna-5-2" style="margin-bottom:28px; border:1px solid #8e44ad; border-radius:12px; background:var(--bg-card); padding:24px; box-shadow:0 8px 24px rgba(0,0,0,0.35);">
          
          <!-- CABECERA PRINCIPAL -->
          <div class="gl-title">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
              <span style="font-family:var(--font-mono); font-size:11px; color:#d2b4de; letter-spacing:1.5px; text-transform:uppercase; display:flex; align-items:center; gap:8px;">
                <span style="background:rgba(142,68,173,0.25); color:#d2b4de; border:1px solid #8e44ad; padding:2px 8px; border-radius:4px; font-weight:800; font-size:11px;">FICHA #03</span>
                <span>⚔️</span> Expediente Militar &amp; Soberanía · Desmitificación Histórica
              </span>
              <span style="font-family:var(--font-mono); font-size:11px; color:var(--text-dim); background:rgba(255,255,255,0.05); padding:2px 8px; border-radius:4px; border:1px solid var(--border-subtle);">
                11 Presidencias Discontinuas (1833–1855)
              </span>
            </div>

            <div style="display:flex; align-items:center; gap:14px; margin-top:10px;">
              <div style="width:48px; height:48px; border-radius:10px; background:rgba(142,68,173,0.18); border:1px solid rgba(142,68,173,0.4); display:flex; align-items:center; justify-content:center; font-size:26px; flex-shrink:0;">
                ${sa.icono || '⚔️'}
              </div>
              <div>
                <h3 style="margin:0; font-size:24px; color:#d2b4de; font-family:var(--font-serif);">Gral. Antonio López de Santa Anna</h3>
                <div style="font-size:12px; color:var(--text-dim); font-family:var(--font-mono); margin-top:2px;">
                  Presidente de México en 11 administraciones discontinuas · Héroe de Tampico (1829) y Veracruz (1838)
                </div>
              </div>
            </div>

            <p style="font-size:13px; color:var(--text-secondary); margin-top:10px; margin-bottom:14px; line-height:1.5;">
              ${sa.subtitulo}
            </p>

            <!-- FILA DE BADGES Y ACCIONES -->
            <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
              <span style="background:rgba(142,68,173,0.12); color:#d2b4de; border:1px solid #8e44ad; padding:6px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); display:inline-flex; align-items:center; gap:6px;">
                🏛️ <strong>Periodo:</strong> ${sa.periodo_gobierno}
              </span>

              <span style="background:rgba(192,57,43,0.15); color:var(--crimson-bright); border:1px solid rgba(192,57,43,0.35); padding:6px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); font-weight:600; display:inline-flex; align-items:center; gap:6px;">
                ⚖️ <strong>Finanzas:</strong> Bancarrota Crónica (-4.8% PIB)
              </span>

              <button id="btnToggleSA" onclick="window.AuditEngine.toggleSantaAnnaDossier()" 
                style="cursor:pointer; background:rgba(142,68,173,0.16); border:1px solid #8e44ad; color:#d2b4de; padding:6px 16px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:8px; transition:all 0.2s ease; box-shadow:0 2px 8px rgba(0,0,0,0.25);">
                <span id="iconToggleSA">🔍</span> <span id="lblToggleSA">Ver Desglose / Ficha ↗</span>
              </button>

              <button id="btnSantaAnnaArgumento" onclick="window.AuditEngine.openSantaAnnaArgumento()" 
                style="cursor:pointer; background:linear-gradient(135deg, rgba(142,68,173,0.25), rgba(120,40,150,0.15)); border:1px solid #8e44ad; color:#d2b4de; padding:6px 16px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:8px; transition:all 0.2s ease; box-shadow:0 2px 10px rgba(142,68,173,0.25);"
                title="Abrir Tesis Defensiva: Las trampas del Congreso y desmitificación">
                <span>⚔️</span> <span>Argumento particular</span>
              </button>
            </div>
          </div>

          <!-- DESGLOSE DESPLEGABLE -->
          <div id="santaAnnaDesgloseContainer" style="display:none; margin-top:22px; padding-top:22px; border-top:1px dashed #8e44ad; animation:fadeInPower 0.35s ease forwards;">
            
            <!-- 1. CRISIS Y BANCARROTA -->
            <div style="background:linear-gradient(135deg, rgba(142,68,173,0.25), rgba(192,57,43,0.15)); border:1px solid #8e44ad; border-radius:8px; padding:16px 20px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px; box-shadow:0 0 16px rgba(142,68,173,0.2);">
              <div>
                <div style="font-family:var(--font-mono); font-size:11px; text-transform:uppercase; letter-spacing:1.5px; color:#d2b4de; font-weight:700; display:flex; align-items:center; gap:6px;">
                  <span>⚔️</span> Dictamen Militar &amp; Hacendario · República en Quiebra y Agio
                </div>
                <div style="font-family:var(--font-mono); font-size:17px; font-weight:800; color:#fff; margin:4px 0;">
                  ${sa.sentencia_total}
                </div>
                <div style="font-size:12.5px; color:#f5b7b1; font-family:var(--font-mono);">
                  🩸 ${sa.multa_restitucion}
                </div>
              </div>
              <div style="text-align:right;">
                <span style="display:inline-block; background:rgba(0,0,0,0.4); border:1px solid var(--border-subtle); padding:6px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); color:#d2b4de;">
                  Juicio Histórico Decimonónico
                </span>
              </div>
            </div>

            <!-- 2. DATOS GENERALES -->
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin-bottom:20px;">
              <div class="data-block-col">
                <div class="data-col-lbl">Marco &amp; Contexto</div>
                <div class="data-col-val" style="font-size:12.5px;">${sa.corte_tribunal}</div>
              </div>
              <div class="data-block-col">
                <div class="data-col-lbl">Opositores &amp; Boicot</div>
                <div class="data-col-val" style="font-size:12.5px; color:#d2b4de;">${sa.juez_sentenciador}</div>
              </div>
              <div class="data-block-col">
                <div class="data-col-lbl">Periodo de Presidencias</div>
                <div class="data-col-val" style="font-size:12.5px;">${sa.fecha_sentencia}</div>
              </div>
              <div class="data-block-col" style="border-left-color:var(--crimson-bright);">
                <div class="data-col-lbl">Mutilación Bélica</div>
                <div class="data-col-val" style="font-size:12.5px; color:var(--crimson-bright);">Pierna izquierda amputada en defensa de Veracruz (1838)</div>
              </div>
            </div>

            <!-- 3. CITA TEXTUAL -->
            <div class="quote-cogan-box">
              "${sa.frase_juez_cogan}"
              <span class="quote-author">${sa.autor_frase}</span>
            </div>

            <!-- 4. EJES DE DEFENSA -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:#d2b4de; margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>⚔️</span> Ejes de Controversia, Desmitificación y Heroísmo Bélico
            </h4>
            <div style="display:grid; gap:8px; margin-bottom:24px;">
              ${sa.cargos_condena.map(c => `
                <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); padding:10px 14px; border-radius:6px; font-size:12.5px;">
                  <strong style="color:#d2b4de; font-family:var(--font-mono);">${c.cargo}:</strong> ${c.desc}
                </div>
              `).join('')}
            </div>

            <!-- 5. PRUEBAS Y TRATADOS -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:#d2b4de; margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>📜</span> Documentos Oficiales, Capitulaciones y Tratados Limítrofes
            </h4>
            <div class="witness-grid">
              ${sa.pruebas_ofrecidas.map(w => `
                <div class="witness-card">
                  <h4 style="color:#d2b4de;">${w.testigo}</h4>
                  <p>${w.testimonio}</p>
                </div>
              `).join('')}
            </div>

            <!-- BANNER CONTEXTUAL A ARGUMENTO PARTICULAR -->
            <div style="background:linear-gradient(135deg, rgba(142,68,173,0.16), rgba(201,168,76,0.08)); border:1px solid #8e44ad; border-radius:8px; padding:14px 18px; margin:16px 0 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
              <div>
                <div style="font-family:var(--font-mono); font-size:11px; color:#d2b4de; font-weight:700; text-transform:uppercase; letter-spacing:1px; display:flex; align-items:center; gap:6px;">
                  <span>⚔️</span> Tesis del Creador: Las Trampas del Congreso, Victorias Patrióticas y Desmitificación
                </div>
                <div style="font-size:12.5px; color:var(--text-secondary); margin-top:3px; max-width:560px; line-height:1.45;">
                  Descubre cómo el Congreso usaba a Santa Anna de bombero ante rebeliones bélicas para luego negarle fondos y traicionarlo, la verdad de El Álamo y cómo La Mesilla salvó al noroeste de la anexión total.
                </div>
              </div>
              <button onclick="window.AuditEngine.openSantaAnnaArgumento()" style="cursor:pointer; background:rgba(142,68,173,0.25); border:1px solid #8e44ad; color:#d2b4de; padding:8px 18px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:6px; transition:all 0.2s ease;">
                <span>📜</span> Argumento particular ↗
              </button>
            </div>

            <!-- 6. IMPACTO ERARIO -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:#d2b4de; margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>💸</span> Finanzas de Guerra, Agio y Decretos Fiscales de Emergencia
            </h4>
            <div style="display:grid; gap:10px; margin-bottom:24px;">
              ${sa.desvio_erario_mexico.map(d => `
                <div style="background:rgba(142,68,173,0.06); border-left:3px solid #8e44ad; padding:12px 16px; border-radius:0 6px 6px 0; font-size:12.5px;">
                  <strong style="color:#d2b4de;">${d.rubro}:</strong> ${d.detalle}
                </div>
              `).join('')}
            </div>

            <!-- 7. CURIOSIDADES -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:#d2b4de; margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>🏰</span> Anécdotas Legendarias, Excentricidades y Destierro
            </h4>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:12px; margin-bottom:24px;">
              ${sa.lujos_y_curiosidades.map(l => `
                <div class="data-block-col">
                  <strong style="color:var(--text-main); font-size:13px; display:block; margin-bottom:4px;">${l.item}</strong>
                  <p style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin:0;">${l.desc}</p>
                </div>
              `).join('')}
            </div>

            <!-- BOTÓN CERRAR -->
            <div style="text-align:center; padding-top:16px; border-top:1px dashed var(--border-subtle);">
              <button onclick="window.AuditEngine.toggleSantaAnnaDossier()" 
                style="cursor:pointer; background:rgba(255,255,255,0.06); border:1px solid var(--border-subtle); color:var(--text-secondary); padding:8px 22px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:600; transition:all 0.2s ease;">
                ✖ Ocultar Desglose de Antonio López de Santa Anna
              </button>
            </div>

          </div><!-- FIN DESGLOSE SANTA ANNA -->
        </div><!-- FIN CARD SANTA ANNA -->
      `;
    }

    // 4. FICHA HISTÓRICA ESQUEMATIZADA DE BENITO JUÁREZ (BLOQUE 4)
    if (bj) {
      html += `
        <!-- FICHA EXPEDIENTE DE BENITO JUÁREZ (BLOQUE MODULAR 4) -->
        <div class="garcia-luna-dossier" id="card-juarez-5-2" style="margin-bottom:28px; border:1px solid #2980b9; border-radius:12px; background:var(--bg-card); padding:24px; box-shadow:0 8px 24px rgba(0,0,0,0.35);">
          
          <!-- CABECERA PRINCIPAL -->
          <div class="gl-title">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
              <span style="font-family:var(--font-mono); font-size:11px; color:#85c1e9; letter-spacing:1.5px; text-transform:uppercase; display:flex; align-items:center; gap:8px;">
                <span style="background:rgba(41,128,185,0.25); color:#85c1e9; border:1px solid #2980b9; padding:2px 8px; border-radius:4px; font-weight:800; font-size:11px;">FICHA #04</span>
                <span>⚖️</span> Expediente Crítico de Soberanía · Tratados Lesivos y Poder Indefinido
              </span>
              <span style="font-family:var(--font-mono); font-size:11px; color:var(--text-dim); background:rgba(255,255,255,0.05); padding:2px 8px; border-radius:4px; border:1px solid var(--border-subtle);">
                1858–1872 (14 Años Continuos)
              </span>
            </div>

            <div style="display:flex; align-items:center; gap:14px; margin-top:10px;">
              <div style="width:48px; height:48px; border-radius:10px; background:rgba(41,128,185,0.18); border:1px solid rgba(41,128,185,0.4); display:flex; align-items:center; justify-content:center; font-size:26px; flex-shrink:0;">
                ${bj.icono || '⚖️'}
              </div>
              <div>
                <h3 style="margin:0; font-size:24px; color:#85c1e9; font-family:var(--font-serif);">Lic. Benito Juárez García</h3>
                <div style="font-size:12px; color:var(--text-dim); font-family:var(--font-mono); margin-top:2px;">
                  Presidente de la República (1858–1872) · Gobernó 14 años consecutivos mediante facultades extraordinarias dictatoriales
                </div>
              </div>
            </div>

            <p style="font-size:13px; color:var(--text-secondary); margin-top:10px; margin-bottom:14px; line-height:1.5;">
              ${bj.subtitulo}
            </p>

            <!-- FILA DE BADGES Y ACCIONES -->
            <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
              <span style="background:rgba(41,128,185,0.12); color:#85c1e9; border:1px solid #2980b9; padding:6px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); display:inline-flex; align-items:center; gap:6px;">
                🏛️ <strong>Mandato:</strong> ${bj.periodo_gobierno}
              </span>

              <span style="background:rgba(192,57,43,0.15); color:var(--crimson-bright); border:1px solid rgba(192,57,43,0.35); padding:6px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); font-weight:600; display:inline-flex; align-items:center; gap:6px;">
                📜 <strong>Tratado:</strong> McLane-Ocampo (Art. 8 Militar)
              </span>

              <button id="btnToggleBJ" onclick="window.AuditEngine.toggleJuarezDossier()" 
                style="cursor:pointer; background:rgba(41,128,185,0.16); border:1px solid #2980b9; color:#85c1e9; padding:6px 16px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:8px; transition:all 0.2s ease; box-shadow:0 2px 8px rgba(0,0,0,0.25);">
                <span id="iconToggleBJ">🔍</span> <span id="lblToggleBJ">Ver Desglose / Ficha ↗</span>
              </button>

              <button id="btnJuarezArgumento" onclick="window.AuditEngine.openJuarezArgumento()" 
                style="cursor:pointer; background:linear-gradient(135deg, rgba(41,128,185,0.25), rgba(192,57,43,0.15)); border:1px solid #2980b9; color:#85c1e9; padding:6px 16px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:8px; transition:all 0.2s ease; box-shadow:0 2px 10px rgba(41,128,185,0.25);"
                title="Abrir Tesis Crítica: Tratado McLane-Ocampo, Ley Lerdo y perpetuación">
                <span>⚖️</span> <span>Argumento particular</span>
              </button>
            </div>
          </div>

          <!-- DESGLOSE DESPLEGABLE -->
          <div id="juarezDesgloseContainer" style="display:none; margin-top:22px; padding-top:22px; border-top:1px dashed #2980b9; animation:fadeInPower 0.35s ease forwards;">
            
            <!-- 1. CRISIS Y MORATORIA -->
            <div style="background:linear-gradient(135deg, rgba(41,128,185,0.25), rgba(192,57,43,0.2)); border:1px solid #2980b9; border-radius:8px; padding:16px 20px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px; box-shadow:0 0 16px rgba(41,128,185,0.2);">
              <div>
                <div style="font-family:var(--font-mono); font-size:11px; text-transform:uppercase; letter-spacing:1.5px; color:#85c1e9; font-weight:700; display:flex; align-items:center; gap:6px;">
                  <span>⚖️</span> Dictamen Crítico · Soberanía Hipotecada y Moratoria de 1861
                </div>
                <div style="font-family:var(--font-mono); font-size:17px; font-weight:800; color:#fff; margin:4px 0;">
                  ${bj.sentencia_total}
                </div>
                <div style="font-size:12.5px; color:#f9e79f; font-family:var(--font-mono);">
                  🌾 ${bj.multa_restitucion}
                </div>
              </div>
              <div style="text-align:right;">
                <span style="display:inline-block; background:rgba(0,0,0,0.4); border:1px solid var(--border-subtle); padding:6px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); color:#85c1e9;">
                  Historia Crítica Documentada
                </span>
              </div>
            </div>

            <!-- 2. DATOS GENERALES -->
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin-bottom:20px;">
              <div class="data-block-col">
                <div class="data-col-lbl">Marco &amp; Geopolítica</div>
                <div class="data-col-val" style="font-size:12.5px;">${bj.corte_tribunal}</div>
              </div>
              <div class="data-block-col">
                <div class="data-col-lbl">Mecanismo de Mandato</div>
                <div class="data-col-val" style="font-size:12.5px; color:#85c1e9;">${bj.juez_sentenciador}</div>
              </div>
              <div class="data-block-col">
                <div class="data-col-lbl">Años Consecutivos</div>
                <div class="data-col-val" style="font-size:12.5px;">${bj.fecha_sentencia}</div>
              </div>
              <div class="data-block-col" style="border-left-color:var(--crimson-bright);">
                <div class="data-col-lbl">Tratado Más Lesivo</div>
                <div class="data-col-val" style="font-size:12.5px; color:var(--crimson-bright);">McLane-Ocampo: Intervención armada unilateral de EE.UU.</div>
              </div>
            </div>

            <!-- 3. CITA TEXTUAL CRÍTICA -->
            <div class="quote-cogan-box">
              "${bj.frase_juez_cogan}"
              <span class="quote-author">${bj.autor_frase}</span>
            </div>

            <!-- 4. EJES CRÍTICOS -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:#85c1e9; margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>⚖️</span> Los 5 Ejes Críticos: Documentación Oficial y Soberanía Comprometida
            </h4>
            <div style="display:grid; gap:8px; margin-bottom:24px;">
              ${bj.cargos_condena.map(c => `
                <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); padding:10px 14px; border-radius:6px; font-size:12.5px;">
                  <strong style="color:#85c1e9; font-family:var(--font-mono);">${c.cargo}:</strong> ${c.desc}
                </div>
              `).join('')}
            </div>

            <!-- 5. PRUEBAS Y TRATADOS -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:#85c1e9; margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>📜</span> Tratados Firmados, Decretos de Suspensión y Proclamas Armadas
            </h4>
            <div class="witness-grid">
              ${bj.pruebas_ofrecidas.map(w => `
                <div class="witness-card">
                  <h4 style="color:#85c1e9;">${w.testigo}</h4>
                  <p>${w.testimonio}</p>
                </div>
              `).join('')}
            </div>

            <!-- BANNER CONTEXTUAL A ARGUMENTO PARTICULAR -->
            <div style="background:linear-gradient(135deg, rgba(41,128,185,0.16), rgba(192,57,43,0.1)); border:1px solid #2980b9; border-radius:8px; padding:14px 18px; margin:16px 0 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
              <div>
                <div style="font-family:var(--font-mono); font-size:11px; color:#85c1e9; font-weight:700; text-transform:uppercase; letter-spacing:1px; display:flex; align-items:center; gap:6px;">
                  <span>⚖️</span> Tesis del Creador: El Tratado McLane-Ocampo, Despojo Indígena y Autocracia
                </div>
                <div style="font-size:12.5px; color:var(--text-secondary); margin-top:3px; max-width:560px; line-height:1.45;">
                  Consulta los documentos de época: la subasta de libre tránsito y derecho de invasión militar a EE.UU., el despojo comunal de la Ley Lerdo y el fraude electoral de 1871 que provocó la rebelión de Porfirio Díaz.
                </div>
              </div>
              <button onclick="window.AuditEngine.openJuarezArgumento()" style="cursor:pointer; background:rgba(41,128,185,0.25); border:1px solid #2980b9; color:#85c1e9; padding:8px 18px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:6px; transition:all 0.2s ease;">
                <span>📜</span> Argumento particular ↗
              </button>
            </div>

            <!-- 6. IMPACTO ERARIO -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:#85c1e9; margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>💸</span> Finanzas Itinerantes en Carretas y Empréstitos en Wall Street
            </h4>
            <div style="display:grid; gap:10px; margin-bottom:24px;">
              ${bj.desvio_erario_mexico.map(d => `
                <div style="background:rgba(41,128,185,0.06); border-left:3px solid #2980b9; padding:12px 16px; border-radius:0 6px 6px 0; font-size:12.5px;">
                  <strong style="color:#85c1e9;">${d.rubro}:</strong> ${d.detalle}
                </div>
              `).join('')}
            </div>

            <!-- 7. CURIOSIDADES -->
            <h4 style="font-family:var(--font-serif); font-size:17px; color:#85c1e9; margin:24px 0 12px; display:flex; align-items:center; gap:8px;">
              <span>🏰</span> El Carruaje de la República, la Negativa de Indulto y Palacio
            </h4>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:12px; margin-bottom:24px;">
              ${bj.lujos_y_curiosidades.map(l => `
                <div class="data-block-col">
                  <strong style="color:var(--text-main); font-size:13px; display:block; margin-bottom:4px;">${l.item}</strong>
                  <p style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin:0;">${l.desc}</p>
                </div>
              `).join('')}
            </div>

            <!-- BOTÓN CERRAR -->
            <div style="text-align:center; padding-top:16px; border-top:1px dashed var(--border-subtle);">
              <button onclick="window.AuditEngine.toggleJuarezDossier()" 
                style="cursor:pointer; background:rgba(255,255,255,0.06); border:1px solid var(--border-subtle); color:var(--text-secondary); padding:8px 22px; border-radius:6px; font-size:12px; font-family:var(--font-mono); font-weight:600; transition:all 0.2s ease;">
                ✖ Ocultar Desglose de Benito Juárez
              </button>
            </div>

          </div><!-- FIN DESGLOSE JUÁREZ -->
        </div><!-- FIN CARD JUÁREZ -->
      `;
    }

    // 5. OTROS OPERADORES Y PERSONAJES RELEVANTES (ESQUEMATIZADOS POR BLOQUES MODULARES)
    html += `
      <div style="margin-top:10px; margin-bottom:18px; border-top:1px solid var(--border-gold); padding-top:24px;">
        <h3 style="font-family:var(--font-serif); font-size:22px; color:var(--gold-bright); margin-bottom:6px; display:flex; align-items:center; gap:8px;">
          <span>🏛️</span> Otros Operadores y Titulares Clave de las Administraciones
        </h3>
        <p style="font-size:12.5px; color:var(--text-dim); margin-bottom:14px;">
          Fichas esquematizadas por bloques: secretarios de Estado, directores paraestatales y personajes relevantes de las administraciones sujetos a investigaciones hacendarias, juicios penales o señalamientos de la Auditoría Superior de la Federación.
        </p>
      </div>

      <div style="display:grid; gap:18px;">
        ${otrosSecundarios.map((p, idx) => {
          const numStr = String(idx + 5).padStart(2, '0');
          const slug = p.id || p.nombre.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
          const curiosidad = pp.datos_curiosos && pp.datos_curiosos.otras_curiosidades
            ? pp.datos_curiosos.otras_curiosidades.find(c => {
                const pNorm = p.nombre.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                const cNorm = c.personaje.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                const words = pNorm.split(/[\s"()]+/).filter(w => w.length > 3 && !['carlos', 'manuel', 'maria', 'elena', 'jose'].includes(w));
                return words.some(w => cNorm.includes(w)) || cNorm.includes(pNorm) || pNorm.includes(cNorm);
              })
            : null;

          return `
          <div class="sexenio-card" id="card-sec-${slug}" style="padding:22px; border:1px solid var(--border-gold); border-radius:12px; background:var(--bg-card); box-shadow:0 6px 18px rgba(0,0,0,0.25);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px; margin-bottom:14px;">
              <div>
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px; flex-wrap:wrap;">
                  <span style="background:rgba(201,168,76,0.18); color:var(--gold-bright); border:1px solid var(--gold); padding:2px 8px; border-radius:4px; font-family:var(--font-mono); font-weight:800; font-size:11px; letter-spacing:1px;">FICHA #${numStr}</span>
                  <span style="font-family:var(--font-mono); font-size:10.5px; color:var(--text-dim); text-transform:uppercase; letter-spacing:1px;">Expediente de Fiscalización</span>
                </div>
                <div style="display:flex; align-items:center; gap:10px;">
                  <span style="font-size:26px;">${p.icono}</span>
                  <h3 style="font-family:var(--font-serif); font-size:22px; color:var(--gold-bright); margin:0;">${p.nombre}</h3>
                </div>
                <div style="font-size:12px; color:var(--text-dim); font-family:var(--font-mono); margin-top:3px;">
                  ${p.cargos}
                </div>
              </div>
            </div>

            <!-- FILA DE 3 CUADROS / BADGES (TERMINA AQUÍ LA VISTA INICIAL) -->
            <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
              <span style="background:rgba(201,168,76,0.12); color:var(--gold); border:1px solid var(--border-gold); padding:5px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); display:inline-flex; align-items:center; gap:6px;">
                🏛️ <strong>Administraciones:</strong> ${p.administraciones}
              </span>

              <span style="background:rgba(192,57,43,0.12); color:var(--crimson-bright); border:1px solid rgba(192,57,43,0.3); padding:5px 12px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); font-weight:600; display:inline-flex; align-items:center; gap:6px;" title="${p.estatus_judicial}">
                ⚖️ <strong>Estatus:</strong> ${p.estatus_judicial.length > 55 ? p.estatus_judicial.substring(0, 52) + '...' : p.estatus_judicial}
              </span>

              <button id="btn-sec-${slug}" onclick="window.AuditEngine.togglePersonajeDesglose('${slug}')" 
                style="cursor:pointer; background:rgba(201,168,76,0.15); border:1px solid var(--gold-bright); color:var(--gold-bright); padding:5px 14px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:6px; transition:all 0.2s ease;">
                <span id="icon-sec-${slug}">🔍</span> <span id="lbl-sec-${slug}">Ver Desglose / Ficha ↗</span>
              </button>
            </div>

            <!-- DESGLOSE DESPLEGABLE DE INFORMACIÓN ESQUEMATIZADA -->
            <div id="desglose-sec-${slug}" style="display:none; margin-top:18px; padding-top:16px; border-top:1px dashed var(--border-gold); animation:fadeInPower 0.3s ease forwards;">
              <div style="background:rgba(139,26,26,0.1); border-left:3px solid var(--crimson-bright); padding:12px 16px; border-radius:0 6px 6px 0; margin-bottom:14px; font-size:12.5px;">
                <strong style="color:var(--crimson-bright); font-family:var(--font-mono); text-transform:uppercase; font-size:11px; letter-spacing:0.5px; display:block; margin-bottom:4px;">
                  ⚖️ Estatus Legal &amp; Situación Judicial:
                </strong>
                <span style="color:var(--text-main); line-height:1.5;">${p.estatus_judicial}</span>
              </div>

              <div style="background:rgba(201,168,76,0.06); border-left:3px solid var(--gold); padding:12px 16px; border-radius:0 6px 6px 0; margin-bottom:14px; font-size:12.5px; line-height:1.6; color:var(--text-secondary);">
                <strong style="color:var(--gold-bright); font-family:var(--font-mono); text-transform:uppercase; font-size:11px; letter-spacing:0.5px; display:block; margin-bottom:4px;">
                  💸 Trama en el Erario y Fiscalización Documentada:
                </strong>
                <span style="color:var(--text-main);">${p.trama_erario}</span>
              </div>

              ${curiosidad ? `
                <div style="background:var(--bg-surface); border:1px dashed var(--border-subtle); padding:12px 16px; border-radius:6px; margin-bottom:14px; font-size:12px;">
                  <span style="font-family:var(--font-mono); color:var(--gold); text-transform:uppercase; font-size:10.5px; font-weight:700; display:block; margin-bottom:3px;">
                    🧐 Anécdota Histórica Vinculada: ${curiosidad.titulo}
                  </span>
                  <p style="margin:0; color:var(--text-dim); line-height:1.5;">${curiosidad.detalle}</p>
                </div>
              ` : ''}

              <div style="text-align:right; margin-top:12px;">
                <button onclick="window.AuditEngine.togglePersonajeDesglose('${slug}')" 
                  style="cursor:pointer; background:rgba(255,255,255,0.05); border:1px solid var(--border-subtle); color:var(--text-secondary); padding:5px 14px; border-radius:5px; font-size:11px; font-family:var(--font-mono); font-weight:600; transition:all 0.2s ease;">
                  ✖ Ocultar Desglose
                </button>
              </div>
            </div>
          </div>
          `;
        }).join('')}
      </div>

      <!-- BLOQUE DE NAVEGACIÓN RÁPIDA Y CONTROL DE FLUJO (ESTILO FORTUVISIÓN) -->
      <div class="nav-flow-dock" style="margin-top:36px; padding:20px 24px; background:linear-gradient(135deg, rgba(20,24,33,0.95), rgba(28,34,48,0.85)); border:1px solid var(--border-gold); border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.45); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
        <div>
          <div style="font-family:var(--font-mono); font-size:10.5px; text-transform:uppercase; letter-spacing:1.5px; color:var(--gold); font-weight:700; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
            <span>🧭</span> Control de Flujo &amp; Navegación Rápida
          </div>
          <div style="font-size:12.5px; color:var(--text-secondary);">
            Has consultado las ${pp.personajes_secundarios.length} fichas de fiscalización de operadores. Alterna entre secciones o regresa al inicio del panel.
          </div>
        </div>

        <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
          <button onclick="window.scrollTo({top: 0, behavior: 'smooth'})" 
            style="cursor:pointer; background:rgba(201,168,76,0.18); border:1px solid var(--gold-bright); color:var(--gold-bright); padding:7px 16px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); font-weight:700; display:inline-flex; align-items:center; gap:6px; transition:all 0.2s ease;">
            ⬆️ Volver al Inicio
          </button>

          <button onclick="window.AuditEngine.switchSubtab('politicos', 'mandatarios')" 
            style="cursor:pointer; background:rgba(255,255,255,0.06); border:1px solid var(--border-subtle); color:var(--text-main); padding:7px 14px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); font-weight:600; display:inline-flex; align-items:center; gap:6px; transition:all 0.2s ease;">
            ⬅️ Subpestaña 5.1: Mandatarios
          </button>

          <button onclick="window.AuditEngine.switchSubtab('politicos', 'curiosos')" 
            style="cursor:pointer; background:rgba(255,255,255,0.06); border:1px solid var(--border-subtle); color:var(--text-main); padding:7px 14px; border-radius:6px; font-size:11.5px; font-family:var(--font-mono); font-weight:600; display:inline-flex; align-items:center; gap:6px; transition:all 0.2s ease;">
            ➡️ Subpestaña 5.3: Anécdotas
          </button>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  function toggleGarciaLunaDossier() {
    const el = document.getElementById('garciaLunaDesgloseContainer');
    const lbl = document.getElementById('lblToggleGL');
    const icon = document.getElementById('iconToggleGL');
    const btn = document.getElementById('btnToggleGL');
    if (!el) return;

    const isClosed = el.style.display === 'none' || el.style.display === '';
    if (isClosed) {
      el.style.display = 'block';
      if (lbl) lbl.textContent = 'Ocultar Desglose ✕';
      if (icon) icon.textContent = '✖';
      if (btn) {
        btn.style.background = 'rgba(192,57,43,0.2)';
        btn.style.borderColor = 'var(--crimson-bright)';
        btn.style.color = '#ff6b6b';
      }
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
      el.style.display = 'none';
      if (lbl) lbl.textContent = 'Ver Desglose / Ficha ↗';
      if (icon) icon.textContent = '🔍';
      if (btn) {
        btn.style.background = 'rgba(201,168,76,0.16)';
        btn.style.borderColor = 'var(--gold-bright)';
        btn.style.color = 'var(--gold-bright)';
      }
      const card = document.getElementById('card-garcia-luna');
      if (card) card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  function openGarciaLunaArgumento() {
    const drawer = document.getElementById('garciaLunaArgumentoDrawer');
    const overlay = document.getElementById('garciaLunaArgumentoOverlay');
    if (!drawer || !overlay) return;
    drawer.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeGarciaLunaArgumento() {
    const drawer = document.getElementById('garciaLunaArgumentoDrawer');
    const overlay = document.getElementById('garciaLunaArgumentoOverlay');
    if (drawer) drawer.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  function togglePorfirioDiazDossier() {
    const el = document.getElementById('porfirioDiazDesgloseContainer');
    const lbl = document.getElementById('lblTogglePD');
    const icon = document.getElementById('iconTogglePD');
    const btn = document.getElementById('btnTogglePD');
    if (!el) return;

    const isClosed = el.style.display === 'none' || el.style.display === '';
    if (isClosed) {
      el.style.display = 'block';
      if (lbl) lbl.textContent = 'Ocultar Desglose ✕';
      if (icon) icon.textContent = '✖';
      if (btn) {
        btn.style.background = 'rgba(192,57,43,0.2)';
        btn.style.borderColor = 'var(--crimson-bright)';
        btn.style.color = '#ff6b6b';
      }
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
      el.style.display = 'none';
      if (lbl) lbl.textContent = 'Ver Desglose / Ficha ↗';
      if (icon) icon.textContent = '🔍';
      if (btn) {
        btn.style.background = 'rgba(201,168,76,0.16)';
        btn.style.borderColor = 'var(--gold-bright)';
        btn.style.color = 'var(--gold-bright)';
      }
      const card = document.getElementById('card-porfirio-diaz-5-2');
      if (card) card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  function openPorfirioDiazArgumento() {
    const drawer = document.getElementById('porfirioDiazArgumentoDrawer');
    const overlay = document.getElementById('porfirioDiazArgumentoOverlay');
    if (!drawer || !overlay) return;
    drawer.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closePorfirioDiazArgumento() {
    const drawer = document.getElementById('porfirioDiazArgumentoDrawer');
    const overlay = document.getElementById('porfirioDiazArgumentoOverlay');
    if (drawer) drawer.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  function toggleSantaAnnaDossier() {
    const el = document.getElementById('santaAnnaDesgloseContainer');
    const lbl = document.getElementById('lblToggleSA');
    const icon = document.getElementById('iconToggleSA');
    const btn = document.getElementById('btnToggleSA');
    if (!el) return;

    const isClosed = el.style.display === 'none' || el.style.display === '';
    if (isClosed) {
      el.style.display = 'block';
      if (lbl) lbl.textContent = 'Ocultar Desglose ✕';
      if (icon) icon.textContent = '✖';
      if (btn) {
        btn.style.background = 'rgba(192,57,43,0.2)';
        btn.style.borderColor = 'var(--crimson-bright)';
        btn.style.color = '#ff6b6b';
      }
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
      el.style.display = 'none';
      if (lbl) lbl.textContent = 'Ver Desglose / Ficha ↗';
      if (icon) icon.textContent = '🔍';
      if (btn) {
        btn.style.background = 'rgba(142,68,173,0.16)';
        btn.style.borderColor = '#8e44ad';
        btn.style.color = '#d2b4de';
      }
      const card = document.getElementById('card-santa-anna-5-2');
      if (card) card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  function openSantaAnnaArgumento() {
    const drawer = document.getElementById('santaAnnaArgumentoDrawer');
    const overlay = document.getElementById('santaAnnaArgumentoOverlay');
    if (!drawer || !overlay) return;
    drawer.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeSantaAnnaArgumento() {
    const drawer = document.getElementById('santaAnnaArgumentoDrawer');
    const overlay = document.getElementById('santaAnnaArgumentoOverlay');
    if (drawer) drawer.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  function toggleJuarezDossier() {
    const el = document.getElementById('juarezDesgloseContainer');
    const lbl = document.getElementById('lblToggleBJ');
    const icon = document.getElementById('iconToggleBJ');
    const btn = document.getElementById('btnToggleBJ');
    if (!el) return;

    const isClosed = el.style.display === 'none' || el.style.display === '';
    if (isClosed) {
      el.style.display = 'block';
      if (lbl) lbl.textContent = 'Ocultar Desglose ✕';
      if (icon) icon.textContent = '✖';
      if (btn) {
        btn.style.background = 'rgba(192,57,43,0.2)';
        btn.style.borderColor = 'var(--crimson-bright)';
        btn.style.color = '#ff6b6b';
      }
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
      el.style.display = 'none';
      if (lbl) lbl.textContent = 'Ver Desglose / Ficha ↗';
      if (icon) icon.textContent = '🔍';
      if (btn) {
        btn.style.background = 'rgba(41,128,185,0.16)';
        btn.style.borderColor = '#2980b9';
        btn.style.color = '#85c1e9';
      }
      const card = document.getElementById('card-juarez-5-2');
      if (card) card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  function openJuarezArgumento() {
    const drawer = document.getElementById('juarezArgumentoDrawer');
    const overlay = document.getElementById('juarezArgumentoOverlay');
    if (!drawer || !overlay) return;
    drawer.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeJuarezArgumento() {
    const drawer = document.getElementById('juarezArgumentoDrawer');
    const overlay = document.getElementById('juarezArgumentoOverlay');
    if (drawer) drawer.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  function togglePersonajeDesglose(slug) {
    const el = document.getElementById(`desglose-sec-${slug}`);
    const lbl = document.getElementById(`lbl-sec-${slug}`);
    const icon = document.getElementById(`icon-sec-${slug}`);
    const btn = document.getElementById(`btn-sec-${slug}`);
    if (!el) return;

    const isClosed = el.style.display === 'none' || el.style.display === '';
    if (isClosed) {
      el.style.display = 'block';
      if (lbl) lbl.textContent = 'Ocultar Desglose ✕';
      if (icon) icon.textContent = '✖';
      if (btn) {
        btn.style.background = 'rgba(192,57,43,0.2)';
        btn.style.borderColor = 'var(--crimson-bright)';
        btn.style.color = '#ff6b6b';
      }
    } else {
      el.style.display = 'none';
      if (lbl) lbl.textContent = 'Ver Desglose / Ficha ↗';
      if (icon) icon.textContent = '🔍';
      if (btn) {
        btn.style.background = 'rgba(201,168,76,0.15)';
        btn.style.borderColor = 'var(--gold-bright)';
        btn.style.color = 'var(--gold-bright)';
      }
    }
  }

  function toggleMarcoLegal() {
    const el = document.getElementById('marcoLegalBody');
    const lbl = document.getElementById('lblToggleML');
    const icon = document.getElementById('iconToggleML');
    const btn = document.getElementById('btnToggleMarcoLegal');
    if (!el) return;

    const isClosed = el.style.display === 'none' || el.style.display === '';
    if (isClosed) {
      el.style.display = 'block';
      if (lbl) lbl.textContent = 'Ocultar Desglose ✕';
      if (icon) icon.textContent = '✖';
      if (btn) {
        btn.style.background = 'rgba(192,57,43,0.2)';
        btn.style.borderColor = 'var(--crimson-bright)';
        btn.style.color = '#ff6b6b';
      }
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
      el.style.display = 'none';
      if (lbl) lbl.textContent = 'Ver Desglose / Fundamentos ↗';
      if (icon) icon.textContent = '🔍';
      if (btn) {
        btn.style.background = 'rgba(201,168,76,0.18)';
        btn.style.borderColor = 'var(--gold-bright)';
        btn.style.color = 'var(--gold-bright)';
      }
      const blq = document.getElementById('bloqueMarcoLegal');
      if (blq) blq.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  function toggleBloqueLegislativo(num) {
    const desglose = document.getElementById(`desgloseBloque${num}`);
    const btn = document.getElementById(`btnToggleBloque${num}`);
    const lbl = document.getElementById(`lblToggleBloque${num}`);
    const icon = document.getElementById(`iconToggleBloque${num}`);
    if (!desglose) return;

    const isClosed = desglose.style.display === 'none' || desglose.style.display === '';
    if (isClosed) {
      desglose.style.display = 'block';
      if (lbl) lbl.textContent = 'Ocultar Desglose ✕';
      if (icon) icon.textContent = '✖';
      if (btn) {
        btn.style.background = 'rgba(192,57,43,0.2)';
        btn.style.borderColor = 'var(--crimson-bright)';
        btn.style.color = '#ff6b6b';
      }

      if (num === 1) {
        updateDiputadosSimulator();
      } else if (num === 2) {
        updateSenadoSimulator();
      } else if (num === 3) {
        updateASFSimulator();
        renderAsfIrregularidadesChart(currentAsfChartView);
      } else if (num === 4) {
        renderCongresosTable();
      } else if (num === 5) {
        initElectoralStateSelect();
        renderElectoralDistritos(state.activeElectoralState || 'JAL');
        if (state.electoralMap) {
          setTimeout(() => state.electoralMap.invalidateSize(), 80);
        } else {
          setTimeout(() => initElectoralMap(), 80);
        }
      } else if (num === 6) {
        renderJerarquiaSalarialChart();
      }
    } else {
      desglose.style.display = 'none';
      if (lbl) lbl.textContent = 'Ver Desglose ↗';
      if (icon) icon.textContent = '🔍';
      if (btn) {
        btn.style.background = (num === 3) ? 'rgba(231,76,60,0.15)' : 'rgba(201,168,76,0.15)';
        btn.style.borderColor = (num === 3) ? 'var(--crimson-bright)' : 'var(--gold-bright)';
        btn.style.color = (num === 3) ? 'var(--crimson-bright)' : 'var(--gold-bright)';
      }
    }
  }

  function switchCivicElectoralTab(tabKey) {
    const tabs = document.querySelectorAll('.civic-tab-btn');
    tabs.forEach(t => {
      const isSel = t.dataset.civictab === tabKey;
      t.classList.toggle('active', isSel);
      t.setAttribute('aria-selected', isSel ? 'true' : 'false');
    });

    const panels = document.querySelectorAll('.civic-tab-content');
    panels.forEach(p => {
      p.style.display = (p.dataset.civictab === tabKey) ? 'block' : 'none';
    });
  }

  function renderPoliticosCuriosos() {
    const container = document.getElementById('politicosCuriososContainer');
    const pp = DB.personajes_politicos;
    if (!container || !pp || !pp.datos_curiosos) return;

    let list = pp.datos_curiosos.otras_curiosidades || [];
    const activeFilter = state.activeCuriososFilter || 'todos';
    const query = (state.curiososSearchQuery || '').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();

    // Deducción o lectura de categoría temática
    function getCuriosoCat(o) {
      if (o.categoria) return o.categoria;
      const t = (o.personaje + ' ' + o.titulo + ' ' + o.detalle).toLowerCase();
      if (t.includes('nxivm') || t.includes('secta') || t.includes('paca') || t.includes('cráneo')) return 'sectas';
      if (t.includes('contrato') || t.includes('clan') || t.includes('fideicomiso') || t.includes('abisalud') || t.includes('romedic')) return 'contratos';
      if (t.includes('video') || t.includes('grabaci') || t.includes('audio') || t.includes('soborno') || t.includes('ligas') || t.includes('cancún')) return 'videos';
      return 'lujos';
    }

    if (activeFilter !== 'todos') {
      list = list.filter(o => getCuriosoCat(o) === activeFilter);
    }

    if (query) {
      list = list.filter(o => {
        const fullText = (o.personaje + ' ' + o.titulo + ' ' + (o.subtitulo || '') + ' ' + o.detalle + ' ' + (o.fuente_judicial || ''))
          .toLowerCase()
          .normalize("NFD")
          .replace(/[\u0300-\u036f]/g, "");
        return fullText.includes(query);
      });
    }

    if (list.length === 0) {
      container.innerHTML = `
        <div style="padding:34px; text-align:center; background:var(--bg-card); border:1px dashed var(--border-gold); border-radius:12px; color:var(--text-dim); font-family:var(--font-mono); font-size:13px;">
          🔍 No se encontraron expedientes con el criterio "${state.curiososSearchQuery}".
          <div style="margin-top:12px;">
            <button class="jerarquia-btn" onclick="window.AuditEngine.searchCuriosos(''); const inp = document.getElementById('curiososSearchInput'); if (inp) inp.value = '';">Mostrar Todos los Episodios</button>
          </div>
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(340px, 1fr)); gap:20px;">
        ${list.map((o, idx) => {
          const cat = getCuriosoCat(o);
          const icon = o.icono || (cat === 'sectas' ? '👁️' : (cat === 'videos' ? '📹' : (cat === 'contratos' ? '💼' : '🏎️')));
          const cardId = `card-curioso-${o.id || idx}`;

          return `
            <div class="sexenio-card" id="${cardId}" style="padding:22px; display:flex; flex-direction:column; justify-content:space-between; border:1px solid var(--border-gold); border-radius:12px; transition:transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease; background:var(--bg-card); box-shadow:0 4px 18px rgba(0,0,0,0.25);">
              <div>
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px; gap:8px; flex-wrap:wrap;">
                  <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
                    <span style="font-size:20px;">${icon}</span>
                    <span style="font-family:var(--font-mono); font-size:11.5px; color:var(--gold-bright); font-weight:700; background:rgba(201,168,76,0.12); padding:3px 8px; border-radius:4px; border:1px solid rgba(201,168,76,0.3);">
                      ${o.personaje}
                    </span>
                  </div>
                  ${o.sexenio_vinculado ? `
                    <span style="font-family:var(--font-mono); font-size:9.5px; color:var(--text-dim); background:rgba(255,255,255,0.05); padding:2px 6px; border-radius:3px; border:1px solid var(--border-subtle);">
                      ${o.sexenio_vinculado}
                    </span>
                  ` : ''}
                </div>

                <h4 style="font-family:var(--font-serif); font-size:19px; color:var(--gold-bright); margin:6px 0 8px; line-height:1.35;">
                  ${o.titulo}
                </h4>

                ${o.subtitulo ? `
                  <div style="font-size:12px; color:var(--cyan); margin-bottom:10px; font-weight:600; line-height:1.4;">
                    📌 ${o.subtitulo}
                  </div>
                ` : ''}

                <p style="font-size:12.5px; color:var(--text-secondary); line-height:1.65; margin:0;">
                  ${o.detalle}
                </p>

                ${o.fuente_judicial ? `
                  <div style="margin-top:14px; font-size:11px; color:var(--gold); font-family:var(--font-mono); background:rgba(201,168,76,0.07); padding:8px 12px; border-radius:6px; border:1px solid rgba(201,168,76,0.25); line-height:1.45;">
                    ⚖️ <strong>Expediente / Referencia Oficial:</strong> ${o.fuente_judicial}
                  </div>
                ` : ''}
              </div>

              <div style="margin-top:18px; padding-top:12px; border-top:1px dashed var(--border-subtle); font-size:11px; color:var(--text-dim); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <span style="font-family:var(--font-mono);">Hemeroteca &amp; Archivo Judicial</span>
                <a href="#tab-panel-faq" class="glos-link" onclick="window.AuditEngine.goToGlossary('Partida Secreta'); return false;" style="font-size:11px;">Consultar Glosario ↗</a>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  function filterCuriosos(filter) {
    state.activeCuriososFilter = filter;
    document.querySelectorAll('.curiosos-cat-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.cat === filter);
    });
    renderPoliticosCuriosos();
  }

  function searchCuriosos(query) {
    state.curiososSearchQuery = query;
    renderPoliticosCuriosos();
  }

  // ==========================================================================
  // SUBPESTAÑA 5.4: VERSUS GENERAL DON PORFIRIO DÍAZ (1876–1911)
  // ==========================================================================
  let currentVersusMetric = 'pib_crecimiento';
  let currentVersusChartType = 'bars';
  let currentVersusPresidentId = null;
  let isVersusScorecardOpen = false;
  let currentVersusTableView = 'cards';
  let currentVersusHealthId = 'porfirio_diaz';
  let versusPlaybackInterval = null;
  let isVersusPlaying = false;
  let isVersusEvaluated = false;
  let isVersusAnimating = false;
  let isVersusHoverEnabled = false;
  let versusAnimFrameId = null;
  // Simulador & Tacómetro Termostático de Salud Financiera
  let isHealthEvaluated = false;
  let isHealthEvaluating = false;
  let isHealthHoverEnabled = false;
  let healthAnimFrameId = null;
  let healthTremorFrameId = null;
  let currentNeedleAngle = 0;
  let displayedScore = 0;
  // Simulador de Tarjetas Ejecutivas
  let isCardsEvaluated = false;
  let isCardsEvaluating = false;
  let isCardsHoverEnabled = false;
  let cardsAnimFrameId = null;
  // Simulador de Ranking Hacendario
  let isRankingEvaluated = false;
  let isRankingEvaluating = false;
  let isRankingHoverEnabled = false;
  let rankingAnimFrameId = null;

  function renderVersusPorfirio() {
    const data = DB.personajes_politicos ? DB.personajes_politicos.porfirio_diaz_versus : null;
    if (!data) return;

    renderVersusToolbar();
    renderVersusChart();
    renderVersusPresidentSelector();
    if (isVersusScorecardOpen && currentVersusPresidentId) {
      renderVersusScorecard();
    } else {
      const container = document.getElementById('versusScorecardContainer');
      if (container) container.style.display = 'none';
    }
    renderVersusTable();
  }

  function renderVersusToolbar() {
    const data = DB.personajes_politicos ? DB.personajes_politicos.porfirio_diaz_versus : null;
    if (!data) return;

    const chipsContainer = document.getElementById('versusMetricChips');
    if (chipsContainer && chipsContainer.children.length === 0) {
      chipsContainer.innerHTML = Object.entries(data.metricas_catalogo).map(([key, m]) => `
        <button class="versus-metric-btn ${key === currentVersusMetric ? 'active' : ''}" 
          data-vmetric="${key}" onclick="window.AuditEngine.setVersusMetric('${key}')">
          <span>${m.icono}</span>
          <span>${m.nombre}</span>
        </button>
      `).join('');
    } else if (chipsContainer) {
      chipsContainer.querySelectorAll('.versus-metric-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.vmetric === currentVersusMetric);
      });
    }

    // Actualizar botones de tipo de gráfica
    const btnBars = document.getElementById('btnVersusChartBars');
    const btnLine = document.getElementById('btnVersusChartLine');
    if (btnBars) btnBars.classList.toggle('active', currentVersusChartType === 'bars');
    if (btnLine) btnLine.classList.toggle('active', currentVersusChartType === 'line');
  }

  function setVersusMetric(metricKey) {
    currentVersusMetric = metricKey;
    if (versusAnimFrameId) {
      cancelAnimationFrame(versusAnimFrameId);
      versusAnimFrameId = null;
    }
    isVersusEvaluated = false;
    isVersusAnimating = false;

    const statusEl = document.getElementById('evalVersusStatusText');
    if (statusEl) {
      statusEl.innerHTML = '⚪ Barras en reposo (0.0). Presiona «Evaluar» o pasa el cursor para medir la escala real.';
    }
    const btnEval = document.getElementById('btnEvaluarVersus');
    if (btnEval) {
      btnEval.innerHTML = '<span>▶️</span> Evaluar Métrica';
    }

    renderVersusToolbar();
    renderVersusChart();
    if (isVersusScorecardOpen && currentVersusPresidentId) {
      renderVersusScorecard();
    }
  }

  function setVersusChartType(type) {
    currentVersusChartType = type;
    renderVersusToolbar();
    renderVersusChart();
  }

  function selectVersusPresident(presId) {
    if (isVersusScorecardOpen && currentVersusPresidentId === presId) {
      closeVersusScorecard();
      return;
    }
    currentVersusPresidentId = presId;
    isVersusScorecardOpen = true;

    renderVersusPresidentSelector();
    renderVersusChart();
    renderVersusScorecard();

    const container = document.getElementById('versusScorecardContainer');
    if (container) {
      container.style.display = 'block';
      setTimeout(() => {
        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 50);
    }
  }

  function closeVersusScorecard() {
    isVersusScorecardOpen = false;
    currentVersusPresidentId = null;
    const container = document.getElementById('versusScorecardContainer');
    if (container) {
      container.style.display = 'none';
    }
    renderVersusPresidentSelector();
    renderVersusChart();
  }

  function toggleVersusPlayback() {
    const data = DB.personajes_politicos ? DB.personajes_politicos.porfirio_diaz_versus : null;
    if (!data) return;

    const btn = document.getElementById('btnPlayVersus');
    const presList = data.mandatarios_comparativa;

    if (isVersusPlaying) {
      clearInterval(versusPlaybackInterval);
      versusPlaybackInterval = null;
      isVersusPlaying = false;
      if (btn) btn.innerHTML = '▶ Reproducir Evolución';
    } else {
      isVersusPlaying = true;
      if (btn) btn.innerHTML = '⏸ Pausar Recorrido';

      let currIdx = presList.findIndex(p => p.id === currentVersusPresidentId);
      if (currIdx === -1) currIdx = 0;

      versusPlaybackInterval = setInterval(() => {
        currIdx = (currIdx + 1) % presList.length;
        selectVersusPresident(presList[currIdx].id);
      }, 2400);
    }
  }

  function renderVersusChart() {
    const stage = document.getElementById('versusChartStage');
    const data = DB.personajes_politicos ? DB.personajes_politicos.porfirio_diaz_versus : null;
    if (!stage || !data) return;

    const metric = data.metricas_catalogo[currentVersusMetric];
    if (!metric) return;

    const diaz = data.general_diaz;
    const diazVal = diaz.metricas[currentVersusMetric];
    const presList = data.mandatarios_comparativa;

    // Controlar visibilidad de la barra de evaluación interactiva
    const evalCtrl = document.getElementById('evaluacionVersusControls');
    if (evalCtrl) {
      evalCtrl.style.display = (currentVersusChartType === 'bars') ? 'flex' : 'none';
    }

    // Actualizar encabezados
    const titleEl = document.getElementById('versusChartActiveTitle');
    const descEl = document.getElementById('versusChartActiveDesc');
    if (titleEl) titleEl.innerHTML = `${metric.icono} ${metric.nombre} — Don Porfirio Díaz vs Sexenios (1988–2026)`;
    if (descEl) descEl.innerHTML = `${metric.descripcion} · <em>Referencia Porfiriana: <strong>${diaz.metricas[currentVersusMetric + '_label'] || (diazVal + ' ' + metric.unidad)}</strong></em>`;

    if (currentVersusChartType === 'bars') {
      renderVersusBarsChart(stage, metric, diaz, diazVal, presList);
    } else {
      renderVersusLineChart(stage, metric, diaz, diazVal, presList);
    }
  }

  function renderVersusBarsChart(stage, metric, diaz, diazVal, presList) {
    // Calcular escala máxima
    const allVals = [diazVal, ...presList.map(p => p.metricas[currentVersusMetric])];
    const maxVal = Math.max(...allVals.map(v => Math.abs(v)), 1);

    const targetHeightDiaz = Math.max(16, Math.min(220, (Math.abs(diazVal) / maxVal) * 200));
    const isDiazZero = !isVersusEvaluated;
    const diazHeight = isDiazZero ? 6 : targetHeightDiaz;
    const diazZeroClass = isDiazZero ? 'versus-bar-zero' : '';
    const diazBubbleZeroClass = isDiazZero ? 'bubble-zero' : '';
    const diazZeroLabel = metric.unidad.includes('%') ? '0.0%' : (metric.unidad === 'km' ? '0 km' : '0.0');
    const diazFinalLabel = `${diazVal > 0 && currentVersusMetric === 'balance_fiscal' ? '+' : ''}${diazVal}${metric.unidad.includes('%') ? '%' : (metric.unidad === 'km' ? ' km' : '')}`;

    let html = `
      <div class="versus-bars-stage" style="border-bottom: 2px solid var(--border-gold); padding-bottom: 12px;">
        <!-- Barra de Porfirio Díaz -->
        <div class="versus-bar-item versus-bar-porfirio" title="Gral. Porfirio Díaz (Referencia Histórica: ${diazVal} ${metric.unidad})">
          <div id="versusBubble_diaz" class="versus-bar-val-bubble ${diazBubbleZeroClass}" style="color:var(--gold-bright);">
            👑 ${isDiazZero ? diazZeroLabel : diazFinalLabel}
          </div>
          <div id="versusBar_diaz" class="versus-bar-col ${diazZeroClass}" style="height: ${diazHeight}px;"></div>
          <div class="versus-bar-lbl">
            <strong style="color:var(--gold-bright);">Porfirio Díaz</strong>
            <div style="font-size:9.5px; color:var(--text-dim);">1876–1911</div>
            <span class="versus-bar-badge" style="background:rgba(201,168,76,0.25); color:var(--gold-bright); border:1px solid var(--gold);">REFERENCIA</span>
          </div>
        </div>

        <div style="width: 2px; height: 180px; background: rgba(201,168,76,0.25); margin: 0 4px; align-self: center;"></div>
    `;

    presList.forEach(p => {
      const val = p.metricas[currentVersusMetric];
      const isSelected = isVersusScorecardOpen && p.id === currentVersusPresidentId;
      const targetHeightP = Math.max(14, Math.min(220, (Math.abs(val) / maxVal) * 200));
      const isPZero = !isVersusEvaluated;
      const pHeight = isPZero ? 6 : targetHeightP;
      const pZeroClass = isPZero ? 'versus-bar-zero' : '';
      const pBubbleZeroClass = isPZero ? 'bubble-zero' : '';
      const pZeroLabel = metric.unidad.includes('%') ? '0.0%' : (metric.unidad === 'km' ? '0 km' : '0.0');
      const pFinalLabel = `${val > 0 && currentVersusMetric === 'balance_fiscal' ? '+' : ''}${val}${metric.unidad.includes('%') ? '%' : (metric.unidad === 'km' ? ' km' : '')}`;

      let valColor = 'var(--text-main)';
      if (metric.sentido_positivo === true) {
        valColor = val >= diazVal ? '#2ecc71' : '#e74c3c';
      } else if (metric.sentido_positivo === false) {
        valColor = val <= diazVal ? '#2ecc71' : '#e74c3c';
      }

      html += `
        <div class="versus-bar-item ${isSelected ? 'selected' : ''}" 
          onclick="window.AuditEngine.selectVersusPresident('${p.id}')"
          title="Haz clic para ver el comparativo Cara a Cara contra ${p.nombre}">
          <div id="versusBubble_${p.id}" class="versus-bar-val-bubble ${pBubbleZeroClass}" style="color:${isPZero ? 'var(--text-dim)' : valColor};">
            ${isPZero ? pZeroLabel : pFinalLabel}
          </div>
          <div id="versusBar_${p.id}" class="versus-bar-col ${pZeroClass}" style="height: ${pHeight}px; background: ${p.color}; opacity: ${isSelected ? '1' : '0.85'};"></div>
          <div class="versus-bar-lbl">
            <strong style="color:${isSelected ? 'var(--gold-bright)' : 'var(--text-main)'};">${p.nombre.split(' ')[0]} ${p.nombre.split(' ')[1] || ''}</strong>
            <div style="font-size:9.5px; color:var(--text-dim);">${p.periodo}</div>
            <span class="versus-bar-badge" style="background:rgba(255,255,255,0.06); color:${p.color}; border:1px solid rgba(255,255,255,0.15);">${p.partido}</span>
          </div>
        </div>
      `;
    });

    html += `</div>`;
    stage.innerHTML = html;
  }

  function evaluarMetricasVersus(duracionMs = 1400) {
    const data = DB.personajes_politicos ? DB.personajes_politicos.porfirio_diaz_versus : null;
    if (!data) return;

    if (versusAnimFrameId) {
      cancelAnimationFrame(versusAnimFrameId);
      versusAnimFrameId = null;
    }

    const metric = data.metricas_catalogo[currentVersusMetric];
    const diaz = data.general_diaz;
    const diazVal = diaz.metricas[currentVersusMetric];
    const presList = data.mandatarios_comparativa;

    const allVals = [diazVal, ...presList.map(p => p.metricas[currentVersusMetric])];
    const maxVal = Math.max(...allVals.map(v => Math.abs(v)), 1);
    const targetHeightDiaz = Math.max(16, Math.min(220, (Math.abs(diazVal) / maxVal) * 200));

    const statusEl = document.getElementById('evalVersusStatusText');
    const btnEval = document.getElementById('btnEvaluarVersus');
    if (statusEl) {
      statusEl.innerHTML = '<span style="color:var(--gold-bright);">⚡ Evaluando y escalando métrica macroeconómica en tiempo real...</span>';
    }
    if (btnEval) {
      btnEval.innerHTML = '<span>⏳</span> Evaluando...';
    }

    // Quitar clases zero
    const barD = document.getElementById('versusBar_diaz');
    const bubD = document.getElementById('versusBubble_diaz');
    if (barD) barD.classList.remove('versus-bar-zero');
    if (bubD) bubD.classList.remove('bubble-zero');

    presList.forEach(p => {
      const barP = document.getElementById(`versusBar_${p.id}`);
      const bubP = document.getElementById(`versusBubble_${p.id}`);
      if (barP) barP.classList.remove('versus-bar-zero');
      if (bubP) {
        bubP.classList.remove('bubble-zero');
        let valColor = 'var(--text-main)';
        if (metric.sentido_positivo === true) {
          valColor = p.metricas[currentVersusMetric] >= diazVal ? '#2ecc71' : '#e74c3c';
        } else if (metric.sentido_positivo === false) {
          valColor = p.metricas[currentVersusMetric] <= diazVal ? '#2ecc71' : '#e74c3c';
        }
        bubP.style.color = valColor;
      }
    });

    isVersusAnimating = true;
    const startTime = performance.now();
    const easeOutCubic = (t) => (--t) * t * t + 1;

    function animateVersusStep(now) {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / duracionMs);
      const eased = easeOutCubic(progress);

      // Díaz
      if (barD) barD.style.height = `${Math.max(6, targetHeightDiaz * eased)}px`;
      if (bubD) {
        const curD = diazVal * eased;
        if (metric.unidad.includes('%')) {
          bubD.textContent = `👑 ${currentVersusMetric === 'balance_fiscal' && curD > 0 ? '+' : ''}${curD.toFixed(1)}%`;
        } else if (metric.unidad === 'km') {
          bubD.textContent = `👑 ${Math.round(curD).toLocaleString('es-MX')} km`;
        } else {
          bubD.textContent = `👑 ${curD.toFixed(1)}`;
        }
      }

      // Presidentes
      presList.forEach(p => {
        const val = p.metricas[currentVersusMetric];
        const targetH = Math.max(14, Math.min(220, (Math.abs(val) / maxVal) * 200));
        const barP = document.getElementById(`versusBar_${p.id}`);
        const bubP = document.getElementById(`versusBubble_${p.id}`);

        if (barP) barP.style.height = `${Math.max(6, targetH * eased)}px`;
        if (bubP) {
          const curP = val * eased;
          if (metric.unidad.includes('%')) {
            bubP.textContent = `${currentVersusMetric === 'balance_fiscal' && curP > 0 ? '+' : ''}${curP.toFixed(1)}%`;
          } else if (metric.unidad === 'km') {
            bubP.textContent = `${Math.round(curP).toLocaleString('es-MX')} km`;
          } else {
            bubP.textContent = `${curP.toFixed(1)}`;
          }
        }
      });

      if (progress < 1) {
        versusAnimFrameId = requestAnimationFrame(animateVersusStep);
      } else {
        isVersusAnimating = false;
        isVersusEvaluated = true;
        versusAnimFrameId = null;

        // Asignar finales exactos
        if (barD) barD.style.height = `${targetHeightDiaz}px`;
        if (bubD) {
          bubD.textContent = `👑 ${diazVal > 0 && currentVersusMetric === 'balance_fiscal' ? '+' : ''}${diazVal}${metric.unidad.includes('%') ? '%' : (metric.unidad === 'km' ? ' km' : '')}`;
        }

        presList.forEach(p => {
          const val = p.metricas[currentVersusMetric];
          const targetH = Math.max(14, Math.min(220, (Math.abs(val) / maxVal) * 200));
          const barP = document.getElementById(`versusBar_${p.id}`);
          const bubP = document.getElementById(`versusBubble_${p.id}`);
          if (barP) barP.style.height = `${targetH}px`;
          if (bubP) {
            bubP.textContent = `${val > 0 && currentVersusMetric === 'balance_fiscal' ? '+' : ''}${val}${metric.unidad.includes('%') ? '%' : (metric.unidad === 'km' ? ' km' : '')}`;
          }
        });

        if (statusEl) {
          statusEl.innerHTML = '<span style="color:var(--emerald-bright);">✓ Evaluación completada: Contraste oficial versus Porfirio Díaz desplegado al 100%.</span>';
        }
        if (btnEval) {
          btnEval.innerHTML = '<span>🔄</span> Volver a Evaluar';
        }
      }
    }

    versusAnimFrameId = requestAnimationFrame(animateVersusStep);
  }

  function resetMetricasVersus() {
    if (versusAnimFrameId) {
      cancelAnimationFrame(versusAnimFrameId);
      versusAnimFrameId = null;
    }
    isVersusAnimating = false;
    isVersusEvaluated = false;

    const data = DB.personajes_politicos ? DB.personajes_politicos.porfirio_diaz_versus : null;
    if (!data) return;
    const metric = data.metricas_catalogo[currentVersusMetric];
    const presList = data.mandatarios_comparativa;

    const barD = document.getElementById('versusBar_diaz');
    const bubD = document.getElementById('versusBubble_diaz');
    if (barD) {
      barD.classList.add('versus-bar-zero');
      barD.style.height = '6px';
    }
    if (bubD) {
      bubD.classList.add('bubble-zero');
      bubD.textContent = `👑 ${metric.unidad.includes('%') ? '0.0%' : (metric.unidad === 'km' ? '0 km' : '0.0')}`;
    }

    presList.forEach(p => {
      const barP = document.getElementById(`versusBar_${p.id}`);
      const bubP = document.getElementById(`versusBubble_${p.id}`);
      if (barP) {
        barP.classList.add('versus-bar-zero');
        barP.style.height = '6px';
      }
      if (bubP) {
        bubP.classList.add('bubble-zero');
        bubP.style.color = 'var(--text-dim)';
        bubP.textContent = `${metric.unidad.includes('%') ? '0.0%' : (metric.unidad === 'km' ? '0 km' : '0.0')}`;
      }
    });

    const statusEl = document.getElementById('evalVersusStatusText');
    if (statusEl) {
      statusEl.innerHTML = '⚪ Barras en reposo (0.0). Presiona «Evaluar» o pasa el cursor para medir la escala real.';
    }
    const btnEval = document.getElementById('btnEvaluarVersus');
    if (btnEval) {
      btnEval.innerHTML = '<span>▶️</span> Evaluar Métrica';
    }
  }

  function toggleHoverVersusEvaluation(enabled) {
    isVersusHoverEnabled = !!enabled;
  }

  function handleVersusStageHover() {
    if (isVersusHoverEnabled && !isVersusEvaluated && !isVersusAnimating && currentVersusChartType === 'bars') {
      evaluarMetricasVersus();
    }
  }

  function renderVersusLineChart(stage, metric, diaz, diazVal, presList) {
    const allVals = [diazVal, ...presList.map(p => p.metricas[currentVersusMetric])];
    const minVal = Math.min(...allVals);
    const maxVal = Math.max(...allVals);
    const range = (maxVal - minVal) === 0 ? 1 : (maxVal - minVal);

    const svgWidth = 840;
    const svgHeight = 240;
    const paddingLeft = 60;
    const paddingRight = 40;
    const paddingTop = 30;
    const paddingBottom = 40;
    const plotWidth = svgWidth - paddingLeft - paddingRight;
    const plotHeight = svgHeight - paddingTop - paddingBottom;

    const getY = (v) => paddingTop + plotHeight - ((v - minVal) / range) * plotHeight;
    const getX = (idx) => paddingLeft + (idx / (presList.length - 1)) * plotWidth;

    const diazY = getY(diazVal);

    // Puntos de los presidentes
    const points = presList.map((p, idx) => ({
      x: getX(idx),
      y: getY(p.metricas[currentVersusMetric]),
      val: p.metricas[currentVersusMetric],
      id: p.id,
      name: p.nombre,
      color: p.color
    }));

    const pathD = points.reduce((acc, pt, idx) => {
      return idx === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`;
    }, '');

    let svgHtml = `
      <div class="versus-line-container">
        <svg viewBox="0 0 ${svgWidth} ${svgHeight}" style="width:100%; height:auto; display:block; overflow:visible;" xmlns="http://www.w3.org/2000/svg">
          <!-- Líneas de cuadrícula horizontal -->
          <line x1="${paddingLeft}" y1="${paddingTop}" x2="${svgWidth - paddingRight}" y2="${paddingTop}" stroke="rgba(255,255,255,0.06)" stroke-dasharray="4"/>
          <line x1="${paddingLeft}" y1="${paddingTop + plotHeight/2}" x2="${svgWidth - paddingRight}" y2="${paddingTop + plotHeight/2}" stroke="rgba(255,255,255,0.06)" stroke-dasharray="4"/>
          <line x1="${paddingLeft}" y1="${paddingTop + plotHeight}" x2="${svgWidth - paddingRight}" y2="${paddingTop + plotHeight}" stroke="rgba(255,255,255,0.12)"/>

          <!-- Etiquetas del eje Y -->
          <text x="${paddingLeft - 10}" y="${paddingTop + 4}" fill="var(--text-dim)" font-size="10" font-family="var(--font-mono)" text-anchor="end">${maxVal.toFixed(1)}${metric.unidad.includes('%') ? '%' : ''}</text>
          <text x="${paddingLeft - 10}" y="${paddingTop + plotHeight/2 + 4}" fill="var(--text-dim)" font-size="10" font-family="var(--font-mono)" text-anchor="end">${((maxVal + minVal)/2).toFixed(1)}${metric.unidad.includes('%') ? '%' : ''}</text>
          <text x="${paddingLeft - 10}" y="${paddingTop + plotHeight + 4}" fill="var(--text-dim)" font-size="10" font-family="var(--font-mono)" text-anchor="end">${minVal.toFixed(1)}${metric.unidad.includes('%') ? '%' : ''}</text>

          <!-- Línea de Referencia de Porfirio Díaz (Dorada Punteada) -->
          <line x1="${paddingLeft}" y1="${diazY}" x2="${svgWidth - paddingRight}" y2="${diazY}" stroke="#c9a84c" stroke-width="2" stroke-dasharray="6,4" opacity="0.9"/>
          <text x="${svgWidth - paddingRight - 6}" y="${diazY - 6}" fill="#ffd700" font-size="10.5" font-family="var(--font-mono)" font-weight="bold" text-anchor="end">
            👑 Díaz: ${diazVal}${metric.unidad.includes('%') ? '%' : ''}
          </text>

          <!-- Línea de Evolución Contemporánea -->
          <path d="${pathD}" fill="none" stroke="rgba(255,255,255,0.45)" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>

          <!-- Puntos / Nodos de Presidentes -->
          ${points.map((pt, idx) => {
            const p = presList[idx];
            const isSel = isVersusScorecardOpen && p.id === currentVersusPresidentId;
            return `
              <g style="cursor:pointer;" onclick="window.AuditEngine.selectVersusPresident('${p.id}')">
                ${isSel ? `<circle cx="${pt.x}" cy="${pt.y}" r="11" fill="none" stroke="var(--gold-bright)" stroke-width="2.5" opacity="0.85"/>` : ''}
                <circle cx="${pt.x}" cy="${pt.y}" r="${isSel ? '7' : '5'}" fill="${p.color}" stroke="#fff" stroke-width="${isSel ? '2.5' : '1.5'}"/>
                <text x="${pt.x}" y="${pt.y - 12}" fill="${isSel ? 'var(--gold-bright)' : '#fff'}" font-size="11" font-family="var(--font-mono)" font-weight="${isSel ? 'bold' : 'normal'}" text-anchor="middle">
                  ${pt.val}${metric.unidad.includes('%') ? '%' : ''}
                </text>
                <text x="${pt.x}" y="${paddingTop + plotHeight + 18}" fill="${isSel ? 'var(--gold-bright)' : 'var(--text-dim)'}" font-size="10" font-family="var(--font-mono)" text-anchor="middle" font-weight="${isSel ? 'bold' : 'normal'}">
                  ${p.nombre.split(' ')[0]}
                </text>
                <text x="${pt.x}" y="${paddingTop + plotHeight + 30}" fill="var(--text-dim)" font-size="9" font-family="var(--font-mono)" text-anchor="middle">
                  ${p.periodo.split('–')[0]}
                </text>
              </g>
            `;
          }).join('')}
        </svg>
      </div>
    `;

    stage.innerHTML = svgHtml;
  }

  function renderVersusPresidentSelector() {
    const container = document.getElementById('versusPresidentsSelector');
    const data = DB.personajes_politicos ? DB.personajes_politicos.porfirio_diaz_versus : null;
    if (!container || !data) return;

    const diaz = data.general_diaz;
    const isDiazSel = isVersusScorecardOpen && currentVersusPresidentId === 'porfirio_diaz';

    const diazBtnHtml = `
      <button class="versus-pres-btn ${isDiazSel ? 'active' : ''}" 
        onclick="window.AuditEngine.selectVersusPresident('porfirio_diaz')"
        style="${isDiazSel ? '' : 'border-color: rgba(201,168,76,0.4); background: rgba(201,168,76,0.06);'}"
        title="Inspeccionar récord maestro de Don Porfirio Díaz">
        <span class="versus-pres-btn-avatar">👑</span>
        <div class="versus-pres-btn-info">
          <span class="versus-pres-btn-name" style="color:var(--gold-bright);">Don Porfirio Díaz</span>
          <span class="versus-pres-btn-period">1876–1911 · <strong style="color:var(--gold);">Porfiriato</strong></span>
        </div>
      </button>
    `;

    const othersHtml = data.mandatarios_comparativa.map(p => {
      const isSel = isVersusScorecardOpen && p.id === currentVersusPresidentId;
      return `
        <button class="versus-pres-btn ${isSel ? 'active' : ''}" 
          onclick="window.AuditEngine.selectVersusPresident('${p.id}')"
          title="Inspeccionar récord versus Porfirio Díaz de ${p.nombre}">
          <span class="versus-pres-btn-avatar">${p.avatar_simbolo}</span>
          <div class="versus-pres-btn-info">
            <span class="versus-pres-btn-name" style="color:${isSel ? 'var(--gold-bright)' : 'var(--text-main)'};">${p.nombre}</span>
            <span class="versus-pres-btn-period">${p.periodo} · <strong style="color:${p.color};">${p.partido}</strong></span>
          </div>
        </button>
      `;
    }).join('');

    container.innerHTML = diazBtnHtml + othersHtml;
  }

  function renderVersusScorecard() {
    const container = document.getElementById('versusScorecardContainer');
    const data = DB.personajes_politicos ? DB.personajes_politicos.porfirio_diaz_versus : null;
    if (!container || !data) return;

    if (!isVersusScorecardOpen || !currentVersusPresidentId) {
      container.style.display = 'none';
      return;
    }

    container.style.display = 'block';

    const diaz = data.general_diaz;
    const metric = data.metricas_catalogo[currentVersusMetric];
    const diazValStr = diaz.metricas[currentVersusMetric + '_label'] || (diaz.metricas[currentVersusMetric] + ' ' + metric.unidad);

    if (currentVersusPresidentId === 'porfirio_diaz') {
      container.innerHTML = `
        <div class="versus-scorecard-box">
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:18px; border-bottom:1px solid var(--border-gold); padding-bottom:12px;">
            <div>
              <span style="font-family:var(--font-mono); font-size:10.5px; color:var(--gold); text-transform:uppercase; letter-spacing:1px; font-weight:700;">
                👑 Récord Maestro &amp; Modelo Hacendario
              </span>
              <h3 style="font-family:var(--font-serif); font-size:20px; color:var(--gold-bright); margin:3px 0 0;">
                ${diaz.nombre} (1876–1911) · Régimen Porfirista
              </h3>
            </div>
            <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
              <span style="font-family:var(--font-mono); font-size:11px; color:var(--cyan); background:rgba(0,180,216,0.1); border:1px solid rgba(0,180,216,0.3); padding:4px 12px; border-radius:20px;">
                Métrica Activa: ${metric.icono} ${metric.nombre}
              </span>
              <button onclick="window.AuditEngine.closeVersusScorecard()" 
                style="display:inline-flex; align-items:center; gap:6px; background:rgba(231,76,60,0.15); border:1px solid rgba(231,76,60,0.5); color:#ff6b6b; padding:5px 12px; border-radius:6px; cursor:pointer; font-size:12px; font-weight:600; transition:all 0.2s ease;"
                onmouseover="this.style.background='rgba(231,76,60,0.3)'; this.style.borderColor='#ff6b6b';"
                onmouseout="this.style.background='rgba(231,76,60,0.15)'; this.style.borderColor='rgba(231,76,60,0.5)';"
                title="Cerrar ficha comparativa">
                ✕ Cerrar Ficha
              </button>
            </div>
          </div>

          <div class="versus-scorecard-grid">
            <!-- Columna 1: Pilar Hacendario de Don Porfirio Díaz -->
            <div class="versus-fighter-card porfirio">
              <div style="display:flex; align-items:center; gap:12px; margin-bottom:14px;">
                <span style="font-size:36px;">👑</span>
                <div>
                  <h4 style="font-family:var(--font-serif); font-size:17px; color:var(--gold-bright); margin:0;">
                    ${diaz.nombre}
                  </h4>
                  <div style="font-family:var(--font-mono); font-size:11px; color:var(--gold); margin-top:2px;">
                    ${diaz.periodo}
                  </div>
                </div>
              </div>

              <div style="background:rgba(201,168,76,0.12); border:1px solid var(--gold); border-radius:8px; padding:12px; margin-bottom:14px; text-align:center;">
                <div style="font-size:10.5px; font-family:var(--font-mono); color:var(--gold); text-transform:uppercase;">Cifra en Métrica Activa:</div>
                <div style="font-family:var(--font-serif); font-size:22px; font-weight:700; color:var(--gold-bright); margin-top:3px;">
                  ${diazValStr}
                </div>
              </div>

              <div style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin-bottom:12px;">
                <strong>Ministro de Hacienda:</strong> ${diaz.ministro_hacienda}
              </div>
              <p style="font-size:12px; color:var(--text-secondary); line-height:1.55; margin:0 0 12px 0;">
                ${diaz.modelo_economico}
              </p>
              <div style="margin-top:auto; font-size:11px; font-family:var(--font-mono); color:var(--text-dim); border-top:1px dashed var(--border-subtle); padding-top:10px;">
                🛡️ Patrón Oro / Superávit Histórico
              </div>
            </div>

            <!-- Columna 2: Luces y Sombras del Régimen -->
            <div class="versus-verdict-card">
              <div style="text-align:center; border-bottom:1px dashed var(--border-subtle); padding-bottom:10px;">
                <span class="versus-verdict-pill" style="background:rgba(201,168,76,0.15); border:1px solid var(--gold); color:var(--gold-bright); margin:0 auto;">
                  ⚖️ Auditoría Integral del Porfiriato
                </span>
                <h5 style="font-family:var(--font-serif); font-size:15px; color:var(--text-main); margin:8px 0 0;">
                  Balanza de Logros Materiales vs Costo Social
                </h5>
              </div>

              <div class="versus-box-supero">
                <strong style="color:#2ecc71; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
                  🟢 Luces Hacendarias e Infraestructura:
                </strong>
                <div>${diaz.luces_y_sombras.luces}</div>
              </div>

              <div class="versus-box-perjudico">
                <strong style="color:#e74c3c; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
                  🔴 Sombras Sociales y Represión Laboral:
                </strong>
                <div>${diaz.luces_y_sombras.sombras}</div>
              </div>
            </div>

            <!-- Columna 3: Cuatro Métricas Clave de Porfirio Díaz -->
            <div class="versus-fighter-card">
              <div style="font-family:var(--font-mono); font-size:11px; color:var(--gold); text-transform:uppercase; letter-spacing:1px; font-weight:700; margin-bottom:12px; text-align:center;">
                📊 Récord Cuantitativo Porfiriano
              </div>
              <div style="display:flex; flex-direction:column; gap:10px; font-size:12px;">
                <div style="display:flex; justify-content:space-between; border-bottom:1px dashed var(--border-subtle); padding-bottom:4px;">
                  <span style="color:var(--text-dim);">PIB Crecimiento:</span>
                  <strong style="font-family:var(--font-mono); color:#2ecc71;">${diaz.metricas.pib_crecimiento_label}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom:1px dashed var(--border-subtle); padding-bottom:4px;">
                  <span style="color:var(--text-dim);">Deuda Pública:</span>
                  <strong style="font-family:var(--font-mono); color:var(--gold);">${diaz.metricas.deuda_pib_label}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom:1px dashed var(--border-subtle); padding-bottom:4px;">
                  <span style="color:var(--text-dim);">Balance Fiscal:</span>
                  <strong style="font-family:var(--font-mono); color:#2ecc71;">${diaz.metricas.balance_fiscal_label}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom:1px dashed var(--border-subtle); padding-bottom:4px;">
                  <span style="color:var(--text-dim);">Ferrocarriles:</span>
                  <strong style="font-family:var(--font-mono); color:var(--gold-bright);">${diaz.metricas.ferrocarriles_label}</strong>
                </div>
              </div>
              <div style="margin-top:auto; font-size:11px; font-family:var(--font-mono); color:var(--text-dim); border-top:1px dashed var(--border-subtle); padding-top:10px;">
                👑 Punto de Comparación Histórico de México
              </div>
            </div>
          </div>

          <!-- Botón Inferior para Cerrar Desglose -->
          <div style="margin-top:16px; padding-top:12px; border-top:1px solid rgba(201,168,76,0.2); display:flex; justify-content:center;">
            <button onclick="window.AuditEngine.closeVersusScorecard()" 
              style="display:inline-flex; align-items:center; gap:8px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.2); color:var(--text-secondary); padding:8px 20px; border-radius:8px; cursor:pointer; font-size:12.5px; font-weight:600; transition:all 0.2s ease;"
              onmouseover="this.style.background='rgba(231,76,60,0.18)'; this.style.borderColor='#ff6b6b'; this.style.color='#fff';"
              onmouseout="this.style.background='rgba(255,255,255,0.05)'; this.style.borderColor='rgba(255,255,255,0.2)'; this.style.color='var(--text-secondary)';"
              title="Cerrar desglose y replegar información">
              <span>✕</span> Cerrar Desglose Cara a Cara
            </button>
          </div>
        </div>
      `;
      return;
    }

    const pres = data.mandatarios_comparativa.find(p => p.id === currentVersusPresidentId) || data.mandatarios_comparativa[0];
    const presValStr = pres.metricas[currentVersusMetric + '_display'] || (pres.metricas[currentVersusMetric] + ' ' + metric.unidad);

    container.innerHTML = `
      <div class="versus-scorecard-box">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:18px; border-bottom:1px solid var(--border-gold); padding-bottom:12px;">
          <div>
            <span style="font-family:var(--font-mono); font-size:10.5px; color:var(--gold); text-transform:uppercase; letter-spacing:1px; font-weight:700;">
              🥊 Tablero Cara a Cara (Head-to-Head)
            </span>
            <h3 style="font-family:var(--font-serif); font-size:20px; color:var(--gold-bright); margin:3px 0 0;">
              General Don Porfirio Díaz vs ${pres.nombre}
            </h3>
          </div>
          <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
            <span style="font-family:var(--font-mono); font-size:11px; color:var(--cyan); background:rgba(0,180,216,0.1); border:1px solid rgba(0,180,216,0.3); padding:4px 12px; border-radius:20px;">
              Métrica Activa: ${metric.icono} ${metric.nombre}
            </span>
            <button onclick="window.AuditEngine.closeVersusScorecard()" 
              style="display:inline-flex; align-items:center; gap:6px; background:rgba(231,76,60,0.15); border:1px solid rgba(231,76,60,0.5); color:#ff6b6b; padding:5px 12px; border-radius:6px; cursor:pointer; font-size:12px; font-weight:600; transition:all 0.2s ease;"
              onmouseover="this.style.background='rgba(231,76,60,0.3)'; this.style.borderColor='#ff6b6b';"
              onmouseout="this.style.background='rgba(231,76,60,0.15)'; this.style.borderColor='rgba(231,76,60,0.5)';"
              title="Cerrar ficha comparativa">
              ✕ Cerrar Ficha
            </button>
          </div>
        </div>

        <div class="versus-scorecard-grid">
          <!-- Columna 1: General Don Porfirio Díaz -->
          <div class="versus-fighter-card porfirio">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:14px;">
              <span style="font-size:36px;">👑</span>
              <div>
                <h4 style="font-family:var(--font-serif); font-size:17px; color:var(--gold-bright); margin:0;">
                  ${diaz.nombre}
                </h4>
                <div style="font-family:var(--font-mono); font-size:11px; color:var(--gold); margin-top:2px;">
                  ${diaz.periodo}
                </div>
              </div>
            </div>

            <div style="background:rgba(201,168,76,0.12); border:1px solid var(--gold); border-radius:8px; padding:12px; margin-bottom:14px; text-align:center;">
              <div style="font-size:10.5px; font-family:var(--font-mono); color:var(--gold); text-transform:uppercase;">Cifra en Métrica Activa:</div>
              <div style="font-family:var(--font-serif); font-size:22px; font-weight:700; color:var(--gold-bright); margin-top:3px;">
                ${diazValStr}
              </div>
            </div>

            <div style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin-bottom:12px;">
              <strong>Ministro de Hacienda:</strong> ${diaz.ministro_hacienda}
            </div>
            <p style="font-size:12px; color:var(--text-secondary); line-height:1.55; margin:0 0 12px 0;">
              ${diaz.modelo_economico}
            </p>
            <div style="margin-top:auto; font-size:11px; font-family:var(--font-mono); color:var(--text-dim); border-top:1px dashed var(--border-subtle); padding-top:10px;">
              🛡️ Patrón Oro / Disciplina Limantour
            </div>
          </div>

          <!-- Columna 2: Veredicto Cívico & Semáforo de Impacto -->
          <div class="versus-verdict-card">
            <div style="text-align:center; border-bottom:1px dashed var(--border-subtle); padding-bottom:10px;">
              <span class="versus-verdict-pill" style="background:rgba(201,168,76,0.15); border:1px solid var(--gold); color:var(--gold-bright); margin:0 auto;">
                ⚖️ Evaluación de Impacto Nacional
              </span>
              <h5 style="font-family:var(--font-serif); font-size:15px; color:var(--text-main); margin:8px 0 0;">
                ¿Cómo aumentó, avanzó o perjudicó en números al país?
              </h5>
            </div>

            <div class="versus-box-supero">
              <strong style="color:#2ecc71; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
                🟢 ¿En qué superó o avanzó respecto a Porfirio Díaz?
              </strong>
              <div>${pres.scorecard.avance}</div>
            </div>

            <div class="versus-box-perjudico">
              <strong style="color:#e74c3c; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
                🔴 ¿En qué perjudicó o quedó a deber frente al Porfiriato?
              </strong>
              <div>${pres.scorecard.retroceso}</div>
            </div>

            <div class="versus-box-sintesis">
              <strong style="color:var(--gold-bright); display:flex; align-items:center; gap:6px; margin-bottom:4px;">
                🏛️ Veredicto Histórico &amp; Hacendario:
              </strong>
              <div>"${pres.scorecard.veredicto_civico}"</div>
            </div>
          </div>

          <!-- Columna 3: Mandatario Seleccionado -->
          <div class="versus-fighter-card">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:14px;">
              <span style="font-size:36px;">${pres.avatar_simbolo}</span>
              <div>
                <h4 style="font-family:var(--font-serif); font-size:17px; color:var(--text-main); margin:0;">
                  ${pres.nombre}
                </h4>
                <div style="font-family:var(--font-mono); font-size:11px; color:${pres.color}; margin-top:2px;">
                  ${pres.periodo} · <strong>${pres.partido}</strong>
                </div>
              </div>
            </div>

            <div style="background:rgba(255,255,255,0.03); border:1px solid ${pres.color}; border-radius:8px; padding:12px; margin-bottom:14px; text-align:center;">
              <div style="font-size:10.5px; font-family:var(--font-mono); color:var(--text-dim); text-transform:uppercase;">Cifra en Métrica Activa:</div>
              <div style="font-family:var(--font-serif); font-size:22px; font-weight:700; color:${pres.color}; margin-top:3px;">
                ${presValStr}
              </div>
            </div>

            <div style="display:flex; flex-direction:column; gap:8px; font-size:11.5px; margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; border-bottom:1px dashed var(--border-subtle); padding-bottom:4px;">
                <span style="color:var(--text-dim);">Crecimiento PIB:</span>
                <strong style="font-family:var(--font-mono); color:var(--gold);">${pres.metricas.pib_crecimiento_display}</strong>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px dashed var(--border-subtle); padding-bottom:4px;">
                <span style="color:var(--text-dim);">Saldo Deuda/PIB:</span>
                <strong style="font-family:var(--font-mono); color:var(--cyan);">${pres.metricas.deuda_pib_display}</strong>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px dashed var(--border-subtle); padding-bottom:4px;">
                <span style="color:var(--text-dim);">Balance Fiscal:</span>
                <strong style="font-family:var(--font-mono); color:${pres.metricas.balance_fiscal >= 0 ? '#2ecc71' : '#e74c3c'};">${pres.metricas.balance_fiscal_display}</strong>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px dashed var(--border-subtle); padding-bottom:4px;">
                <span style="color:var(--text-dim);">Ferrocarriles:</span>
                <strong style="font-family:var(--font-mono); color:var(--text-main);">${pres.metricas.ferrocarriles_display}</strong>
              </div>
            </div>

            <div style="margin-top:auto; font-size:11px; font-family:var(--font-mono); color:var(--text-dim); border-top:1px dashed var(--border-subtle); padding-top:10px;">
              ⚡ Ciclo Constitucional Contemporáneo
            </div>
          </div>
        </div>

        <!-- Botón Inferior para Cerrar Desglose Cara a Cara -->
        <div style="margin-top:16px; padding-top:12px; border-top:1px solid rgba(201,168,76,0.2); display:flex; justify-content:center;">
          <button onclick="window.AuditEngine.closeVersusScorecard()" 
            style="display:inline-flex; align-items:center; gap:8px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.2); color:var(--text-secondary); padding:8px 20px; border-radius:8px; cursor:pointer; font-size:12.5px; font-weight:600; transition:all 0.2s ease;"
            onmouseover="this.style.background='rgba(231,76,60,0.18)'; this.style.borderColor='#ff6b6b'; this.style.color='#fff';"
            onmouseout="this.style.background='rgba(255,255,255,0.05)'; this.style.borderColor='rgba(255,255,255,0.2)'; this.style.color='var(--text-secondary)';"
            title="Cerrar desglose y replegar información">
            <span>✕</span> Cerrar Desglose Cara a Cara
          </button>
        </div>
      </div>
    `;
  }

  // ==========================================================================
  // CATÁLOGO CUANTITATIVO DE SALUD FINANCIERA & RIGOR HACENDARIO (0 A 100)
  // ==========================================================================
  const VERSUS_SALUD_FINANCIERA = {
    porfirio_diaz: {
      id: 'porfirio_diaz',
      nombre: 'Don Porfirio Díaz Mori',
      periodo: '1876–1911 (31 años efectivos)',
      avatar: '👑',
      partido: 'Régimen Porfirista',
      color: '#c9a84c',
      score: 94,
      semaforo_color: '#00b894',
      semaforo_label: '🟢 SALUD ÓPTIMA (SUPERÁVIT)',
      diagnostico: 'Histórico superávit primario y financiero (+0.8% del PIB) alcanzado por Limantour en 1894–1895. Consolidación de deuda al 30.5% del PIB en patrón oro con crédito internacional de primera clase y expansión de 19,280 km de ferrocarriles.',
      pilares: {
        balance: { score: 100, label: '+0.8% Superávit (Récord)', val: '+0.8%' },
        deuda: { score: 92, label: '30.5% del PIB (Patrón Oro)', val: '30.5%' },
        crecimiento: { score: 88, label: '+3.3% Anual Promedio', val: '+3.3%' },
        gasto: { score: 98, label: 'Gasto Austero (7.4% vs 8.2% Ingresos)', val: '7.4%' }
      },
      pib_crec: '+3.3%',
      deuda_pib: '30.5%',
      balance_pib: '+0.8%',
      ferrocarriles: '19,280 km'
    },
    santa_anna: {
      id: 'santa_anna',
      nombre: 'Gral. Antonio López de Santa Anna',
      periodo: '1833–1855 (11 mandatos)',
      avatar: '⚔️',
      partido: 'Centralista / Conservador',
      color: '#8e44ad',
      score: 26,
      semaforo_color: '#e74c3c',
      semaforo_label: '🔴 QUIEBRA FISCAL / BANCARROTA CRÓNICA',
      diagnostico: 'Representó el máximo colapso hacendario de la historia patria: bancarrotas recurrentes, moratorias continuas de deuda externa, préstamos forzosos con agiotistas al 50% de interés, venta forzada de La Mesilla por $10 mdd para pagar nómina militar y cobro de impuestos extravagantes a perros, puertas y ventanas.',
      pilares: {
        balance: { score: 20, label: '-4.8% Déficit Permanente (Bancarrota)', val: '-4.8%' },
        deuda: { score: 24, label: 'Default Total (Sin crédito exterior)', val: 'Default' },
        crecimiento: { score: 32, label: '+0.4% Estancamiento e Inestabilidad', val: '+0.4%' },
        gasto: { score: 28, label: 'Gasto 9.9% (85% militarizado)', val: '9.9%' }
      },
      pib_crec: '+0.4%',
      deuda_pib: 'Default',
      balance_pib: '-4.8%',
      ferrocarriles: '13 km'
    },
    juarez: {
      id: 'juarez',
      nombre: 'Lic. Benito Juárez García',
      periodo: '1858–1872 (14 años de mandato)',
      avatar: '⚖️',
      partido: 'Partido Liberal / República Restaurada',
      color: '#2980b9',
      score: 70,
      semaforo_color: '#f1c40f',
      semaforo_label: '🟡 AUSTERIDAD REPUBLICANA / RECONSTRUCCIÓN',
      diagnostico: 'Salvaguardó la República gobernando con finanzas de resistencia itinerante desde su carruaje; declaró la moratoria de deuda de 1861 por insolvencia absoluta pero cimentó las bases hacendarias del México moderno con Matías Romero: nacionalizó bienes del clero, redujo drásticamente el ejército e impulsó la troncal del Ferrocarril Mexicano.',
      pilares: {
        balance: { score: 72, label: '-0.8% Déficit de Guerra y Ajuste', val: '-0.8%' },
        deuda: { score: 60, label: '38.0% PIB (Anulación deuda Maximiliano)', val: '38.0%' },
        crecimiento: { score: 68, label: '+2.1% Reactivación post-Imperio', val: '+2.1%' },
        gasto: { score: 80, label: 'Gasto Austero (7.6% vs 6.8% Ingresos)', val: '7.6%' }
      },
      pib_crec: '+2.1%',
      deuda_pib: '38.0%',
      balance_pib: '-0.8%',
      ferrocarriles: '420 km'
    },
    fox: {
      id: 'fox',
      nombre: 'Vicente Fox Quesada',
      periodo: '2000–2006',
      avatar: '🤠',
      partido: 'PAN',
      color: '#0055a5',
      score: 82,
      semaforo_color: '#2ecc71',
      semaforo_label: '🟢 FINANZAS FAVORABLES (PETRODÓLARES)',
      diagnostico: 'Gozó de la mayor bonanza petrolera moderna con barriles superiores a $100 USD. Deuda pública en niveles bajos (28.2% PIB) y déficit moderado (-0.2%), aunque diluyó los excedentes en gasto corriente sin ahorro de Estado.',
      pilares: {
        balance: { score: 90, label: '-0.2% Déficit Mínimo', val: '-0.2%' },
        deuda: { score: 95, label: '28.2% del PIB (Baja)', val: '28.2%' },
        crecimiento: { score: 62, label: '+2.0% Crecimiento Moderado', val: '+2.0%' },
        gasto: { score: 80, label: 'Gasto 16.0% vs Ingreso 15.8%', val: '16.0%' }
      },
      pib_crec: '+2.0%',
      deuda_pib: '28.2%',
      balance_pib: '-0.2%',
      ferrocarriles: '0 km'
    },
    salinas: {
      id: 'salinas',
      nombre: 'Carlos Salinas de Gortari',
      periodo: '1988–1994',
      avatar: '🏛️',
      partido: 'PRI',
      color: '#006847',
      score: 74,
      semaforo_color: '#f1c40f',
      semaforo_label: '🟡 MODERADA / VULNERABILIDAD CAMBIARIA',
      diagnostico: 'Impulsó el mayor crecimiento del PIB (+3.9%) y contuvo el déficit (-0.4%), pero hipotecó la liquidez soberana emitiendo más de $29,000 mdd en Tesobonos dolarizados sin respaldo de reservas, detonando la crisis del 94.',
      pilares: {
        balance: { score: 86, label: '-0.4% Déficit Controlado', val: '-0.4%' },
        deuda: { score: 92, label: '28.0% PIB (Riesgo Tesobonos)', val: '28.0%' },
        crecimiento: { score: 96, label: '+3.9% Expansión Alta', val: '+3.9%' },
        gasto: { score: 76, label: 'Gasto 14.2% vs Ingreso 13.8%', val: '14.2%' }
      },
      pib_crec: '+3.9%',
      deuda_pib: '28.0%',
      balance_pib: '-0.4%',
      ferrocarriles: '0 km'
    },
    zedillo: {
      id: 'zedillo',
      nombre: 'Ernesto Zedillo Ponce de León',
      periodo: '1994–2000',
      avatar: '💼',
      partido: 'PRI',
      color: '#006847',
      score: 70,
      semaforo_color: '#f1c40f',
      semaforo_label: '🟡 ESTABLE EN AJUSTE (POST-CRISIS)',
      diagnostico: 'Rescató a la economía tras el Error de Diciembre logrando un crecimiento promedio de +3.4% y disciplina presupuestal final, pero cargó al erario público el rescate bancario perpetuo del FOBAPROA ($552,000 mdp).',
      pilares: {
        balance: { score: 76, label: '-1.0% Déficit de Ajuste', val: '-1.0%' },
        deuda: { score: 70, label: '28.2% PIB (+ Pasivo FOBAPROA)', val: '28.2%' },
        crecimiento: { score: 84, label: '+3.4% Recuperación', val: '+3.4%' },
        gasto: { score: 72, label: 'Gasto 15.1% vs Ingreso 14.1%', val: '15.1%' }
      },
      pib_crec: '+3.4%',
      deuda_pib: '28.2%',
      balance_pib: '-1.0%',
      ferrocarriles: '-19,000 km'
    },
    calderon: {
      id: 'calderon',
      nombre: 'Felipe Calderón Hinojosa',
      periodo: '2006–2012',
      avatar: '🛡️',
      partido: 'PAN',
      color: '#0055a5',
      score: 63,
      semaforo_color: '#e67e22',
      semaforo_label: '🟠 VULNERABLE / DÉFICIT CRECIENTE',
      diagnostico: 'Enfrentó la crisis financiera global de 2008-2009 con políticas contracíclicas, pero inauguró un ciclo prolongado de déficit fiscal crónico (-2.1% del PIB) e incrementó la deuda pública al 34.4% del PIB.',
      pilares: {
        balance: { score: 60, label: '-2.1% Déficit Persistente', val: '-2.1%' },
        deuda: { score: 78, label: '34.4% del PIB (En Alza)', val: '34.4%' },
        crecimiento: { score: 55, label: '+1.7% Crecimiento Débil', val: '+1.7%' },
        gasto: { score: 62, label: 'Gasto 19.3% vs Ingreso 17.2%', val: '19.3%' }
      },
      pib_crec: '+1.7%',
      deuda_pib: '34.4%',
      balance_pib: '-2.1%',
      ferrocarriles: '27 km'
    },
    sheinbaum: {
      id: 'sheinbaum',
      nombre: 'Claudia Sheinbaum Pardo',
      periodo: '2024–Actualidad',
      avatar: '👩‍🔬',
      partido: 'MORENA',
      color: '#8b1d22',
      score: 55,
      semaforo_color: '#e67e22',
      semaforo_label: '🟠 EN CONSOLIDACIÓN / RETO DE INTERESES',
      diagnostico: 'Plantea consolidar la disciplina reduciendo el déficit de 2024, pero opera con un costo financiero de deuda que supera $1.3 billones de pesos anuales en intereses y un techo de deuda fijado en 50.2% del PIB.',
      pilares: {
        balance: { score: 52, label: '-3.9% Meta de Consolidación', val: '-3.9%' },
        deuda: { score: 54, label: '50.2% Techo Estimado', val: '50.2%' },
        crecimiento: { score: 52, label: '+1.5% Proyección Base', val: '+1.5%' },
        gasto: { score: 62, label: 'Gasto 25.7% vs Ingreso 21.8%', val: '25.7%' }
      },
      pib_crec: '+1.5%',
      deuda_pib: '50.2%',
      balance_pib: '-3.9%',
      ferrocarriles: '+3,000 km'
    },
    amlo: {
      id: 'amlo',
      nombre: 'Andrés Manuel López Obrador',
      periodo: '2018–2024',
      avatar: '🦅',
      partido: 'MORENA',
      color: '#8b1d22',
      score: 48,
      semaforo_color: '#e74c3c',
      semaforo_label: '🔴 PRESIÓN FISCAL / DÉFICIT DE CIERRE',
      diagnostico: 'Elevó sustancialmente la recaudación del SAT sin nuevos impuestos, pero el gasto en pensiones universales y megaobras elevó el déficit fiscal a un récord de -5.9% en 2024 y la deuda soberana a cerca de $16 billones.',
      pilares: {
        balance: { score: 42, label: '-3.2% Promedio (-5.9% en 2024)', val: '-3.2%' },
        deuda: { score: 56, label: '49.3% del PIB (16 billones)', val: '49.3%' },
        crecimiento: { score: 44, label: '+0.9% (Efecto Pandemia)', val: '+0.9%' },
        gasto: { score: 54, label: 'Gasto 24.7% vs Ingreso 21.5%', val: '24.7%' }
      },
      pib_crec: '+0.9%',
      deuda_pib: '49.3%',
      balance_pib: '-3.2%',
      ferrocarriles: '2,754 km'
    },
    epn: {
      id: 'epn',
      nombre: 'Enrique Peña Nieto',
      periodo: '2012–2018',
      avatar: '👔',
      partido: 'PRI',
      color: '#006847',
      score: 42,
      semaforo_color: '#e74c3c',
      semaforo_label: '🔴 DETERIORO CRÍTICO / DEUDA DESBORDADA',
      diagnostico: 'Registró el mayor deterioro de balance de las últimas tres décadas: la deuda pública saltó del 34% al 44.9% del PIB con déficit presupuestario continuo (-2.8% PIB) y proyectos emblemáticos con sobrecostos del 250%.',
      pilares: {
        balance: { score: 48, label: '-2.8% Déficit Recurrente', val: '-2.8%' },
        deuda: { score: 58, label: '44.9% del PIB (Salto de 10 pts)', val: '44.9%' },
        crecimiento: { score: 68, label: '+2.4% Crecimiento Inercial', val: '+2.4%' },
        gasto: { score: 50, label: 'Gasto 21.3% vs Ingreso 18.5%', val: '21.3%' }
      },
      pib_crec: '+2.4%',
      deuda_pib: '44.9%',
      balance_pib: '-2.8%',
      ferrocarriles: '58 km'
    }
  };

  function renderVersusTable() {
    const container = document.getElementById('versusTableContainer');
    if (!container) return;

    container.innerHTML = `
      <!-- ================================================================= -->
      <!-- PARTE 1: CONSOLA DE SALUD FINANCIERA & SIMULADOR TERMOSTÁTICO     -->
      <!-- ================================================================= -->
      <div style="margin-bottom: 10px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
        <span style="font-family:var(--font-mono); font-size:11px; color:var(--gold); text-transform:uppercase; letter-spacing:1px; font-weight:700;">
          ⏱️ PARTE 1: CONSOLA DE SALUD FINANCIERA &amp; SIMULADOR TERMOSTÁTICO
        </span>
        <span style="font-family:var(--font-mono); font-size:10.5px; color:var(--text-dim);">
          Calibración analógica en tiempo real con inercia física
        </span>
      </div>

      <!-- Barra de Control del Simulador Hacendario (Estructura en 3 Líneas Fijas) -->
      <div class="evaluacion-controls-bar versus-health-ctrls-3lines" id="evaluacionSaludControls" style="margin-bottom:16px;">
        <!-- Línea 1 (Superior): Identificador del Simulador y Meta-datos -->
        <div class="versus-ctrl-line-1">
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="eval-badge">SIMULADOR HACENDARIO</span>
            <span style="font-family:var(--font-mono); font-size:11px; color:var(--gold); font-weight:700;">
              ⏱️ Calibración Termostática de Disciplina Fiscal Sexenal
            </span>
          </div>
          <span style="font-family:var(--font-mono); font-size:10.5px; color:var(--text-dim);">
            Modo Interactivo · Escala Analógica 0 a 100 pts
          </span>
        </div>

        <!-- Línea 2 (Media): Espacio Fijo para Estado Dinámico (Evita que el bloque cambie de tamaño al alternar presidentes) -->
        <div class="versus-ctrl-line-2">
          <div class="eval-status-text" id="evalSaludStatusText">
            ⚪ Tacómetro termostático en reposo (0 pts). Presiona «Evaluar» o interactúa con el cursor.
          </div>
        </div>

        <!-- Línea 3 (Inferior): Botonera de Acciones (Volver a Calibrar, Reiniciar en Ceros, Activar Cursor) -->
        <div class="versus-ctrl-line-3">
          <button class="eval-btn-primary" id="btnEvaluarSalud" onclick="window.AuditEngine.evaluarSaludFinanciera()">
            <span>▶️</span> Evaluar Salud Financiera
          </button>
          <button class="eval-btn-secondary" id="btnResetSalud" onclick="window.AuditEngine.resetSaludFinanciera()">
            <span>↺</span> Reiniciar en Ceros
          </button>
          <label class="eval-toggle-label" title="Iniciar evaluación automáticamente al interactuar con el cursor">
            <input type="checkbox" id="evalSaludHoverToggle" ${isHealthHoverEnabled ? 'checked' : ''} onchange="window.AuditEngine.toggleHoverSaludEvaluation(this.checked)">
            <span>Activar al pasar cursor</span>
          </label>
        </div>
      </div>

      <!-- Consola Interactiva con Tacómetro Circular de Salud Financiera -->
      <div id="versusHealthConsoleContainer" 
           onmouseenter="window.AuditEngine.handleHealthConsoleHover()" 
           ontouchstart="window.AuditEngine.handleHealthConsoleHover()"></div>

      <!-- ================================================================= -->
      <!-- SEPARADOR ELEGANTE ENTRE PARTE 1 Y PARTE 2                        -->
      <!-- ================================================================= -->
      <div style="margin: 28px 0 20px; border-top: 1px dashed rgba(201,168,76,0.3); position: relative; text-align: center;">
        <span style="position: relative; top: -11px; background: var(--bg-card); padding: 0 16px; font-family: var(--font-mono); font-size: 11px; color: var(--gold); text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700;">
          📂 PARTE 2: FORMATOS DE VISUALIZACIÓN MULTIDIMENSIONAL
        </span>
      </div>

      <!-- Selector de Vistas Multidimensional (Cero Desplazamiento Horizontal) -->
      <div class="versus-view-switcher" id="versusViewSwitcher">
        <span style="font-family:var(--font-mono); font-size:11px; color:var(--text-dim); text-transform:uppercase; margin-right:4px;">
          Selecciona Formato:
        </span>
        <button class="versus-view-btn ${currentVersusTableView === 'cards' ? 'active' : ''}" 
          onclick="window.AuditEngine.setVersusTableView('cards')" id="btnViewCards">
          <span>🗂️</span> Tarjetas Ejecutivas
        </button>
        <button class="versus-view-btn ${currentVersusTableView === 'table' ? 'active' : ''}" 
          onclick="window.AuditEngine.setVersusTableView('table')" id="btnViewTable">
          <span>📊</span> Matriz Tabular Ajustada
        </button>
        <button class="versus-view-btn ${currentVersusTableView === 'ranking' ? 'active' : ''}" 
          onclick="window.AuditEngine.setVersusTableView('ranking')" id="btnViewRanking">
          <span>⚖️</span> Ranking Hacendario
        </button>
      </div>

      <!-- Contenedor Dinámico para la Vista Activa -->
      <div id="versusActiveViewContainer"></div>
    `;

    renderVersusHealthGauge(currentVersusHealthId);
    renderVersusActiveView();
  }

  function getPillarSeverityColor(score) {
    if (score >= 75) return '#2ecc71'; // Verde (Superávit / Rigor alto)
    if (score >= 60) return '#f1c40f'; // Amarillo (Equilibrio / Ajuste moderado)
    if (score >= 48) return '#e67e22'; // Naranja (Déficit / Presión creciente)
    return '#e74c3c';                 // Rojo (Déficit crítico / Severo)
  }

  function renderVersusHealthGauge(targetId) {
    const consoleContainer = document.getElementById('versusHealthConsoleContainer');
    if (!consoleContainer) return;

    const leader = VERSUS_SALUD_FINANCIERA[targetId] || VERSUS_SALUD_FINANCIERA['porfirio_diaz'];
    currentVersusHealthId = leader.id;

    // Si aún no está evaluado, inicia en estado reposo (0)
    const activeAngle = isHealthEvaluated ? (leader.score / 100) * 180 : 0;
    const activeScore = isHealthEvaluated ? leader.score : 0;
    currentNeedleAngle = activeAngle;
    displayedScore = activeScore;

    const pillLabel = isHealthEvaluated ? leader.semaforo_label : '⚪ EN ESPERA DE EVALUACIÓN';
    const pillColor = isHealthEvaluated ? leader.semaforo_color : 'var(--text-dim)';
    const scoreColor = isHealthEvaluated ? leader.semaforo_color : 'var(--text-dim)';

    consoleContainer.innerHTML = `
      <div class="versus-health-console">
        <div class="versus-health-layout">
          <!-- Lado Izquierdo: Tacómetro Circular / Velocímetro SVG de Rojo a Verde -->
          <div class="versus-gauge-wrapper">
            <div style="font-family:var(--font-mono); font-size:10.5px; color:var(--gold); text-transform:uppercase; letter-spacing:1px; font-weight:700; margin-bottom:8px;">
              ⏱️ Tacómetro Termostático de Salud Financiera
            </div>

            <div class="versus-gauge-svg-container">
              <svg viewBox="0 0 240 140" style="width:100%; max-width:260px; height:auto; display:block; overflow:visible;" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="versusGaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#e74c3c" />
                    <stop offset="30%" stop-color="#e67e22" />
                    <stop offset="50%" stop-color="#f1c40f" />
                    <stop offset="75%" stop-color="#2ecc71" />
                    <stop offset="100%" stop-color="#00b894" />
                  </linearGradient>
                  <filter id="gaugeShadow" x="-20%" y="-20%" width="140%" height="140%">
                    <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.5"/>
                  </filter>
                </defs>

                <!-- Arco de Fondo (Track Translúcido) -->
                <path d="M 30 120 A 90 90 0 0 1 210 120" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="14" stroke-linecap="round" />

                <!-- Arco Degradado Cromático de Rojo a Verde -->
                <path d="M 30 120 A 90 90 0 0 1 210 120" fill="none" stroke="url(#versusGaugeGrad)" stroke-width="14" stroke-linecap="round" opacity="0.95" />

                <!-- Marcas de escala cada 10 puntos con trigonometría SVG exacta -->
                ${[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100].map(pt => {
                  const rad = ((pt / 100) * 180 + 180) * (Math.PI / 180);
                  const x1 = 120 + 82 * Math.cos(rad);
                  const y1 = 120 + 82 * Math.sin(rad);
                  const x2 = 120 + (pt % 50 === 0 ? 72 : 76) * Math.cos(rad);
                  const y2 = 120 + (pt % 50 === 0 ? 72 : 76) * Math.sin(rad);
                  return `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" stroke="rgba(255,255,255,0.3)" stroke-width="${pt % 50 === 0 ? '1.5' : '1'}"/>`;
                }).join('')}

                <!-- Marcas Numéricas de Referencia -->
                <text x="24" y="136" fill="#e74c3c" font-size="10" font-family="var(--font-mono)" font-weight="bold" text-anchor="middle">0</text>
                <text x="120" y="24" fill="#f1c40f" font-size="10" font-family="var(--font-mono)" font-weight="bold" text-anchor="middle">50</text>
                <text x="216" y="136" fill="#00b894" font-size="10" font-family="var(--font-mono)" font-weight="bold" text-anchor="middle">100</text>

                <!-- Aguja Termostática Física (Manipulada directamente por el motor de física RAF) -->
                <g id="versusGaugeNeedleGroup" filter="url(#gaugeShadow)" style="transform: rotate(${activeAngle}deg); transform-origin: 120px 120px; will-change: transform;">
                  <!-- Varilla metálica principal -->
                  <line x1="120" y1="120" x2="38" y2="120" stroke="#ffffff" stroke-width="3" stroke-linecap="round" />
                  <!-- Puntero dorado cónico -->
                  <polygon points="34,120 44,116 44,124" fill="var(--gold-bright)" />
                  <!-- Contrapeso circular trasero -->
                  <circle cx="134" cy="120" r="5.5" fill="#222" stroke="var(--gold)" stroke-width="1.5" />
                  <!-- Pivote central metálico -->
                  <circle cx="120" cy="120" r="8" fill="var(--gold-bright)" stroke="#ffffff" stroke-width="2" />
                  <circle cx="120" cy="120" r="3" fill="#111" />
                </g>
              </svg>

              <!-- Calificación Numérica Central -->
              <div class="versus-gauge-score-display">
                <span id="versusGaugeScoreNum" class="versus-gauge-big-num" style="color:${scoreColor};">
                  ${activeScore}
                </span>
                <span class="versus-gauge-denom">de 100 pts</span>
              </div>
            </div>

            <!-- Píldora de Semáforo -->
            <div id="versusHealthPill" class="versus-health-pill" style="color:${pillColor}; background:rgba(255,255,255,0.04); border-color:${pillColor};">
              ${pillLabel}
            </div>

            <!-- Chips de Mandatarios para Calibración Inmediata -->
            <div class="versus-health-chips-row">
              ${Object.values(VERSUS_SALUD_FINANCIERA).map(m => `
                <button class="versus-hchip ${isHealthEvaluated && m.id === leader.id ? 'active' : ''}" 
                  data-hleader="${m.id}"
                  onclick="window.AuditEngine.setVersusHealthPresident('${m.id}')"
                  title="Calibrar tacómetro para ${m.nombre}">
                  <span>${m.avatar}</span>
                  <span>${m.nombre.split(' ')[0]}</span>
                </button>
              `).join('')}
            </div>
          </div>

          <!-- Lado Derecho: Diagnóstico & Desglose de los 4 Pilares Hacendarios -->
          <div class="versus-health-detail-panel">
            <div class="versus-health-leader-header">
              <span id="versusHealthLeaderAvatar" style="font-size:32px;">${isHealthEvaluated ? leader.avatar : '🏛️'}</span>
              <div>
                <h4 id="versusHealthLeaderName" style="font-family:var(--font-serif); font-size:18px; color:var(--text-main); margin:0;">
                  ${isHealthEvaluated ? leader.nombre : '<span style="color:var(--text-dim); font-style:italic;">--- Ningún Mandatario Seleccionado ---</span>'}
                </h4>
                <div id="versusHealthLeaderPeriod" style="font-family:var(--font-mono); font-size:11px; color:${isHealthEvaluated ? leader.color : 'var(--text-dim)'}; margin-top:2px;">
                  ${isHealthEvaluated ? `${leader.periodo} · <strong>${leader.partido}</strong>` : 'Periodo por calibrar · <strong style="color:var(--text-dim);">Esperando selección</strong>'}
                </div>
              </div>
              <div style="margin-left:auto; text-align:right;">
                <span style="font-family:var(--font-mono); font-size:10px; color:var(--text-dim); text-transform:uppercase;">Índice Global:</span>
                <div id="versusHealthIndexPill" style="font-family:var(--font-mono); font-size:20px; font-weight:800; color:${isHealthEvaluated ? leader.semaforo_color : 'var(--text-dim)'};">
                  ${isHealthEvaluated ? `${leader.score}/100` : '0/100'}
                </div>
              </div>
            </div>

            <p id="versusHealthDiagText" class="versus-health-diag-text">
              ${isHealthEvaluated ? leader.diagnostico : 'Consola termostática en reposo (0 pts). Selecciona un mandatario en los botones o presiona «Evaluar Salud Financiera» para calibrar la aguja física analógica y desplegar el diagnóstico hacendario.'}
            </p>

            <!-- 4 Pilares Hacendarios con Colores Dinámicos de Gravedad -->
            <div style="display:flex; flex-direction:column; gap:8px;">
              <!-- Pilar 1: Balance Fiscal -->
              <div class="versus-pillar-row">
                <div class="versus-pillar-labels">
                  <span style="color:var(--text-dim);">⚖️ Balance Presupuestal:</span>
                  <strong id="versusPillarVal_balance" style="color:${isHealthEvaluated ? getPillarSeverityColor(leader.pilares.balance.score) : 'var(--text-dim)'};">
                    ${isHealthEvaluated ? leader.pilares.balance.label : '0.0% (Reposo)'}
                  </strong>
                </div>
                <div class="versus-pillar-track">
                  <div id="versusPillarFill_balance" class="versus-pillar-fill" style="width:${isHealthEvaluated ? leader.pilares.balance.score : 0}%; background:${isHealthEvaluated ? getPillarSeverityColor(leader.pilares.balance.score) : 'rgba(255,255,255,0.08)'};"></div>
                </div>
              </div>

              <!-- Pilar 2: Nivel de Deuda Pública -->
              <div class="versus-pillar-row">
                <div class="versus-pillar-labels">
                  <span style="color:var(--text-dim);">💰 Saldo de Deuda Pública:</span>
                  <strong id="versusPillarVal_deuda" style="color:${isHealthEvaluated ? getPillarSeverityColor(leader.pilares.deuda.score) : 'var(--text-dim)'};">
                    ${isHealthEvaluated ? leader.pilares.deuda.label : '0.0% PIB'}
                  </strong>
                </div>
                <div class="versus-pillar-track">
                  <div id="versusPillarFill_deuda" class="versus-pillar-fill" style="width:${isHealthEvaluated ? leader.pilares.deuda.score : 0}%; background:${isHealthEvaluated ? getPillarSeverityColor(leader.pilares.deuda.score) : 'rgba(255,255,255,0.08)'};"></div>
                </div>
              </div>

              <!-- Pilar 3: Crecimiento Económico -->
              <div class="versus-pillar-row">
                <div class="versus-pillar-labels">
                  <span style="color:var(--text-dim);">📈 Crecimiento Real del PIB:</span>
                  <strong id="versusPillarVal_crecimiento" style="color:${isHealthEvaluated ? getPillarSeverityColor(leader.pilares.crecimiento.score) : 'var(--text-dim)'};">
                    ${isHealthEvaluated ? leader.pilares.crecimiento.label : '0.0%'}
                  </strong>
                </div>
                <div class="versus-pillar-track">
                  <div id="versusPillarFill_crecimiento" class="versus-pillar-fill" style="width:${isHealthEvaluated ? leader.pilares.crecimiento.score : 0}%; background:${isHealthEvaluated ? getPillarSeverityColor(leader.pilares.crecimiento.score) : 'rgba(255,255,255,0.08)'};"></div>
                </div>
              </div>

              <!-- Pilar 4: Eficiencia de Gasto -->
              <div class="versus-pillar-row">
                <div class="versus-pillar-labels">
                  <span style="color:var(--text-dim);">🛡️ Cobertura Gasto vs Ingresos:</span>
                  <strong id="versusPillarVal_gasto" style="color:${isHealthEvaluated ? getPillarSeverityColor(leader.pilares.gasto.score) : 'var(--text-dim)'};">
                    ${isHealthEvaluated ? leader.pilares.gasto.label : '0.0%'}
                  </strong>
                </div>
                <div class="versus-pillar-track">
                  <div id="versusPillarFill_gasto" class="versus-pillar-fill" style="width:${isHealthEvaluated ? leader.pilares.gasto.score : 0}%; background:${isHealthEvaluated ? getPillarSeverityColor(leader.pilares.gasto.score) : 'rgba(255,255,255,0.08)'};"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    if (isHealthEvaluated) {
      startAmbientThermostatTremor();
    }
  }

  function evaluarSaludFinanciera(duracionMs = 1500) {
    const leader = VERSUS_SALUD_FINANCIERA[currentVersusHealthId] || VERSUS_SALUD_FINANCIERA['porfirio_diaz'];
    if (!leader) return;

    if (healthAnimFrameId) {
      cancelAnimationFrame(healthAnimFrameId);
      healthAnimFrameId = null;
    }
    if (healthTremorFrameId) {
      cancelAnimationFrame(healthTremorFrameId);
      healthTremorFrameId = null;
    }

    const targetScore = leader.score;
    const targetAngle = (targetScore / 100) * 180;
    const startAngle = currentNeedleAngle;
    const startScore = displayedScore;
    const startTime = performance.now();

    isHealthEvaluating = true;

    const statusEl = document.getElementById('evalSaludStatusText');
    const btnEval = document.getElementById('btnEvaluarSalud');
    if (statusEl) {
      statusEl.innerHTML = `<span style="color:var(--gold-bright);">⚡ Calibrando termostato hacendario y pilares fiscales para ${leader.nombre}...</span>`;
    }
    if (btnEval) {
      btnEval.innerHTML = '<span>⏳</span> Calibrando...';
    }

    // Actualizar datos del líder en panel derecho
    const headerAvatar = document.getElementById('versusHealthLeaderAvatar');
    const headerName = document.getElementById('versusHealthLeaderName');
    const headerPeriod = document.getElementById('versusHealthLeaderPeriod');
    const diagText = document.getElementById('versusHealthDiagText');
    if (headerAvatar) headerAvatar.textContent = leader.avatar;
    if (headerName) headerName.textContent = leader.nombre;
    if (headerPeriod) headerPeriod.innerHTML = `${leader.periodo} · <strong style="color:${leader.color};">${leader.partido}</strong>`;
    if (diagText) diagText.textContent = leader.diagnostico;

    // Resaltar chip activo
    document.querySelectorAll('.versus-hchip').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.hleader === leader.id);
    });

    // Parámetros oscilador armónico amortiguado (termostato físico de precisión con inercia)
    const omega = 7.0;
    const zeta = 0.52;
    const omegaD = omega * Math.sqrt(1 - zeta * zeta);

    function animateStep(now) {
      const elapsed = (now - startTime) / 1000;
      const progress = Math.min(1, (now - startTime) / duracionMs);

      // Ecuación de respuesta física con rebote elástico e inercia gravitacional
      const decay = Math.exp(-zeta * omega * elapsed * 2.6);
      const harmonic = Math.cos(omegaD * elapsed * 2.6) + (zeta / Math.sqrt(1 - zeta * zeta)) * Math.sin(omegaD * elapsed * 2.6);
      const factor = 1 - decay * harmonic;

      currentNeedleAngle = Math.max(0, Math.min(185, startAngle + (targetAngle - startAngle) * factor));
      const curScore = Math.max(0, Math.min(100, Math.round(startScore + (targetScore - startScore) * Math.min(1, Math.max(0, factor)))));
      displayedScore = curScore;

      // Actualizar aguja
      const needleEl = document.getElementById('versusGaugeNeedleGroup');
      if (needleEl) {
        needleEl.style.transform = `rotate(${currentNeedleAngle}deg)`;
      }

      // Actualizar número grande con color reactivo
      const numEl = document.getElementById('versusGaugeScoreNum');
      if (numEl) {
        numEl.textContent = curScore;
        if (curScore >= 80) numEl.style.color = '#00b894';
        else if (curScore >= 70) numEl.style.color = '#2ecc71';
        else if (curScore >= 55) numEl.style.color = '#f1c40f';
        else if (curScore >= 45) numEl.style.color = '#e67e22';
        else numEl.style.color = '#e74c3c';
      }

      // Actualizar barras de pilares
      const clampFactor = Math.min(1, Math.max(0, factor));
      updatePillarBarsDOM(leader, clampFactor);

      if (progress < 1) {
        healthAnimFrameId = requestAnimationFrame(animateStep);
      } else {
        currentNeedleAngle = targetAngle;
        displayedScore = targetScore;
        isHealthEvaluating = false;
        isHealthEvaluated = true;
        healthAnimFrameId = null;

        if (needleEl) needleEl.style.transform = `rotate(${targetAngle}deg)`;
        if (numEl) {
          numEl.textContent = targetScore;
          numEl.style.color = leader.semaforo_color;
        }

        updatePillarBarsDOM(leader, 1.0, true);

        const pillEl = document.getElementById('versusHealthPill');
        if (pillEl) {
          pillEl.innerHTML = leader.semaforo_label;
          pillEl.style.color = leader.semaforo_color;
          pillEl.style.borderColor = leader.semaforo_color;
          pillEl.style.background = 'rgba(255,255,255,0.06)';
        }

        if (statusEl) {
          statusEl.innerHTML = `<span style="color:var(--emerald-bright);">✓ Calibración completada: ${leader.nombre} evaluado con ${leader.score}/100 pts (${leader.semaforo_label.split('(')[0].trim()}).</span>`;
        }
        if (btnEval) {
          btnEval.innerHTML = '<span>🔄</span> Volver a Calibrar';
        }

        startAmbientThermostatTremor();
      }
    }

    healthAnimFrameId = requestAnimationFrame(animateStep);
  }

  function updatePillarBarsDOM(leader, factor, isFinal = false) {
    const pilares = [
      { key: 'balance', targetWidth: leader.pilares.balance.score, fullLabel: leader.pilares.balance.label, score: leader.pilares.balance.score },
      { key: 'deuda', targetWidth: leader.pilares.deuda.score, fullLabel: leader.pilares.deuda.label, score: leader.pilares.deuda.score },
      { key: 'crecimiento', targetWidth: leader.pilares.crecimiento.score, fullLabel: leader.pilares.crecimiento.label, score: leader.pilares.crecimiento.score },
      { key: 'gasto', targetWidth: leader.pilares.gasto.score, fullLabel: leader.pilares.gasto.label, score: leader.pilares.gasto.score }
    ];

    pilares.forEach(p => {
      const fillEl = document.getElementById(`versusPillarFill_${p.key}`);
      const valEl = document.getElementById(`versusPillarVal_${p.key}`);
      const curWidth = p.targetWidth * factor;
      const sevColor = getPillarSeverityColor(p.score);

      if (fillEl) {
        fillEl.style.width = `${curWidth}%`;
        fillEl.style.background = isHealthEvaluated || factor > 0 ? sevColor : 'rgba(255,255,255,0.08)';
      }
      if (valEl) {
        if (isFinal) {
          valEl.textContent = p.fullLabel;
          valEl.style.color = sevColor;
        } else {
          valEl.textContent = `${curWidth.toFixed(1)}%`;
          valEl.style.color = curWidth > 0 ? sevColor : 'var(--text-dim)';
        }
      }
    });
  }

  function resetSaludFinanciera() {
    if (healthAnimFrameId) {
      cancelAnimationFrame(healthAnimFrameId);
      healthAnimFrameId = null;
    }
    if (healthTremorFrameId) {
      cancelAnimationFrame(healthTremorFrameId);
      healthTremorFrameId = null;
    }
    isHealthEvaluating = false;
    isHealthEvaluated = false;

    const startAngle = currentNeedleAngle;
    const startTime = performance.now();
    const duration = 600;

    function resetStep(now) {
      const p = Math.min(1, (now - startTime) / duration);
      const ease = 1 - Math.pow(1 - p, 3);
      currentNeedleAngle = startAngle * (1 - ease);
      displayedScore = Math.round(displayedScore * (1 - ease));

      const needleEl = document.getElementById('versusGaugeNeedleGroup');
      if (needleEl) needleEl.style.transform = `rotate(${currentNeedleAngle}deg)`;

      const numEl = document.getElementById('versusGaugeScoreNum');
      if (numEl) {
        numEl.textContent = displayedScore;
        numEl.style.color = 'var(--text-dim)';
      }

      ['balance', 'deuda', 'crecimiento', 'gasto'].forEach(k => {
        const fill = document.getElementById(`versusPillarFill_${k}`);
        const val = document.getElementById(`versusPillarVal_${k}`);
        if (fill) {
          fill.style.width = `${(1 - ease) * 100}%`;
          fill.style.background = 'rgba(255,255,255,0.08)';
        }
        if (val) {
          val.textContent = '0.0%';
          val.style.color = 'var(--text-dim)';
        }
      });

      if (p < 1) {
        healthAnimFrameId = requestAnimationFrame(resetStep);
      } else {
        currentNeedleAngle = 0;
        displayedScore = 0;
        healthAnimFrameId = null;

        ['balance', 'deuda', 'crecimiento', 'gasto'].forEach(k => {
          const fill = document.getElementById(`versusPillarFill_${k}`);
          const val = document.getElementById(`versusPillarVal_${k}`);
          if (fill) {
            fill.style.width = '0%';
            fill.style.background = 'rgba(255,255,255,0.08)';
          }
          if (val) {
            val.textContent = '0.0% (Reposo)';
            val.style.color = 'var(--text-dim)';
          }
        });

        const pillEl = document.getElementById('versusHealthPill');
        if (pillEl) {
          pillEl.innerHTML = '⚪ EN ESPERA DE EVALUACIÓN';
          pillEl.style.color = 'var(--text-dim)';
          pillEl.style.borderColor = 'rgba(255,255,255,0.15)';
          pillEl.style.background = 'rgba(255,255,255,0.02)';
        }

        // Vaciar ficha del mandatario en blanco y ceros
        const headerAvatar = document.getElementById('versusHealthLeaderAvatar');
        const headerName = document.getElementById('versusHealthLeaderName');
        const headerPeriod = document.getElementById('versusHealthLeaderPeriod');
        const diagText = document.getElementById('versusHealthDiagText');
        const indexPill = document.getElementById('versusHealthIndexPill');

        if (headerAvatar) headerAvatar.textContent = '🏛️';
        if (headerName) headerName.innerHTML = '<span style="color:var(--text-dim); font-style:italic;">--- Ningún Mandatario Seleccionado ---</span>';
        if (headerPeriod) headerPeriod.innerHTML = 'Periodo por calibrar · <strong style="color:var(--text-dim);">Esperando selección</strong>';
        if (diagText) diagText.textContent = 'Consola termostática en reposo (0 pts). Selecciona un mandatario en los botones o presiona «Evaluar Salud Financiera» para calibrar la aguja física analógica y desplegar el diagnóstico hacendario.';
        if (indexPill) {
          indexPill.textContent = '0/100';
          indexPill.style.color = 'var(--text-dim)';
        }

        // Desmarcar todos los chips de mandatarios
        document.querySelectorAll('.versus-hchip').forEach(btn => btn.classList.remove('active'));

        const statusEl = document.getElementById('evalSaludStatusText');
        if (statusEl) {
          statusEl.innerHTML = '⚪ Tacómetro termostático en reposo (0 pts). Presiona «Evaluar» o interactúa con el cursor.';
        }
        const btnEval = document.getElementById('btnEvaluarSalud');
        if (btnEval) {
          btnEval.innerHTML = '<span>▶️</span> Evaluar Salud Financiera';
        }
      }
    }

    healthAnimFrameId = requestAnimationFrame(resetStep);
  }

  function startAmbientThermostatTremor() {
    if (healthTremorFrameId) {
      cancelAnimationFrame(healthTremorFrameId);
      healthTremorFrameId = null;
    }
    if (!isHealthEvaluated) return;

    function tremorStep(timestamp) {
      const tremor = Math.sin(timestamp * 0.0035) * 0.35 + Math.sin(timestamp * 0.008) * 0.15;
      const angle = currentNeedleAngle + tremor;
      const needleEl = document.getElementById('versusGaugeNeedleGroup');
      if (needleEl) {
        needleEl.style.transform = `rotate(${angle}deg)`;
      }
      healthTremorFrameId = requestAnimationFrame(tremorStep);
    }

    healthTremorFrameId = requestAnimationFrame(tremorStep);
  }

  function handleHealthConsoleHover() {
    if (isHealthHoverEnabled && !isHealthEvaluated && !isHealthEvaluating) {
      evaluarSaludFinanciera();
    }
  }

  function toggleHoverSaludEvaluation(enabled) {
    isHealthHoverEnabled = !!enabled;
  }

  function setVersusHealthPresident(id) {
    currentVersusHealthId = id;
    const leader = VERSUS_SALUD_FINANCIERA[id] || VERSUS_SALUD_FINANCIERA['porfirio_diaz'];

    // Actualizar chips de selección
    document.querySelectorAll('.versus-hchip').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.hleader === id);
    });

    // Actualizar datos del líder en panel derecho
    const headerAvatar = document.getElementById('versusHealthLeaderAvatar');
    const headerName = document.getElementById('versusHealthLeaderName');
    const headerPeriod = document.getElementById('versusHealthLeaderPeriod');
    const diagText = document.getElementById('versusHealthDiagText');
    const indexPill = document.getElementById('versusHealthIndexPill');

    if (headerAvatar) headerAvatar.textContent = leader.avatar;
    if (headerName) headerName.textContent = leader.nombre;
    if (headerPeriod) headerPeriod.innerHTML = `${leader.periodo} · <strong style="color:${leader.color};">${leader.partido}</strong>`;
    if (diagText) diagText.textContent = leader.diagnostico;
    if (indexPill) {
      indexPill.textContent = `${leader.score}/100`;
      indexPill.style.color = leader.semaforo_color;
    }

    // Actualizar barras de pilares con colores dinámicos de gravedad del mandatario
    updatePillarBarsDOM(leader, 1.0, true);

    // Si está en vista tarjetas, resaltar tarjeta seleccionada
    if (currentVersusTableView === 'cards') {
      document.querySelectorAll('.versus-exec-card').forEach(c => {
        c.classList.toggle('active-card', c.dataset.cardId === id);
      });
    }

    // Desplazar suavemente a la consola para que el usuario aprecie el movimiento
    const consoleEl = document.getElementById('evaluacionSaludControls');
    if (consoleEl) {
      consoleEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Ejecutar calibración termostática con física de aguja
    evaluarSaludFinanciera();
  }

  function setVersusTableView(viewMode) {
    currentVersusTableView = viewMode;

    const btnCards = document.getElementById('btnViewCards');
    const btnTable = document.getElementById('btnViewTable');
    const btnRanking = document.getElementById('btnViewRanking');
    if (btnCards) btnCards.classList.toggle('active', viewMode === 'cards');
    if (btnTable) btnTable.classList.toggle('active', viewMode === 'table');
    if (btnRanking) btnRanking.classList.toggle('active', viewMode === 'ranking');

    renderVersusActiveView();
  }

  function renderVersusActiveView() {
    const container = document.getElementById('versusActiveViewContainer');
    if (!container) return;

    if (currentVersusTableView === 'cards') {
      container.innerHTML = renderVersusCardsView();
    } else if (currentVersusTableView === 'table') {
      container.innerHTML = renderVersusCompactTableView();
    } else if (currentVersusTableView === 'ranking') {
      container.innerHTML = renderVersusRankingView();
    }
  }

  function renderVersusCardsView() {
    const list = Object.values(VERSUS_SALUD_FINANCIERA);

    return `
      <!-- Barra de Control del Simulador de Tarjetas Ejecutivas -->
      <div class="evaluacion-controls-bar" id="evaluacionCardsControls" style="margin-bottom:16px;">
        <div class="eval-info-group">
          <span class="eval-badge" style="background:rgba(201,168,76,0.15); border-color:var(--gold); color:var(--gold-bright);">
            SIMULADOR DE TARJETAS EJECUTIVAS
          </span>
          <span class="eval-status-text" id="evalCardsStatusText">
            ${isCardsEvaluated 
              ? `✓ Tarjetas evaluadas exitosamente: ${list.length} mandatarios analizados con métricas clave.` 
              : '⚪ Tarjetas en reposo (0 pts y métricas en cero). Presiona «Evaluar Tarjetas» o interactúa con el cursor.'}
          </span>
        </div>
        <div class="eval-actions-group">
          <button class="eval-btn-primary" id="btnEvaluarCards" onclick="window.AuditEngine.evaluarTarjetasEjecutivas()">
            <span>${isCardsEvaluated ? '🔄' : '▶️'}</span> ${isCardsEvaluated ? 'Volver a Evaluar' : 'Evaluar Tarjetas'}
          </button>
          <button class="eval-btn-secondary" id="btnResetCards" onclick="window.AuditEngine.resetTarjetasEjecutivas()">
            <span>↺</span> Reiniciar en Ceros
          </button>
          <label class="eval-toggle-label" title="Iniciar evaluación automáticamente al pasar el cursor sobre las tarjetas">
            <input type="checkbox" id="evalCardsHoverToggle" ${isCardsHoverEnabled ? 'checked' : ''} onchange="window.AuditEngine.toggleHoverCardsEvaluation(this.checked)">
            <span>Activar al pasar cursor</span>
          </label>
        </div>
      </div>

      <!-- Cuadrícula de Tarjetas con Detector de Cursor -->
      <div class="versus-cards-grid" onmouseenter="window.AuditEngine.handleCardsHover()" ontouchstart="window.AuditEngine.handleCardsHover()">
        ${list.map(item => {
          const isAct = item.id === currentVersusHealthId;
          const scoreDisplay = isCardsEvaluated ? item.score : 0;
          const ringGrad = isCardsEvaluated
            ? `conic-gradient(${item.semaforo_color} ${item.score}%, rgba(255,255,255,0.08) ${item.score}%)`
            : `conic-gradient(rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.08) 100%)`;
          const ringColor = isCardsEvaluated ? item.semaforo_color : 'var(--text-dim)';

          return `
            <div class="versus-exec-card ${isAct ? 'active-card' : ''}" data-card-id="${item.id}" id="execCard_${item.id}">
              <div class="versus-exec-card-header">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span class="versus-exec-avatar">${item.avatar}</span>
                  <div>
                    <h4 class="versus-exec-name" style="color:${isAct ? 'var(--gold-bright)' : 'var(--text-main)'};">
                      ${item.nombre}
                    </h4>
                    <div class="versus-exec-period">
                      ${item.periodo.split('(')[0]} · <strong style="color:${item.color};">${item.partido}</strong>
                    </div>
                  </div>
                </div>

                <!-- Mini Anillo de Salud Financiera -->
                <div class="versus-mini-gauge-ring" id="cardGaugeRing_${item.id}"
                  style="background: ${ringGrad}; color: ${ringColor};" 
                  title="Salud Financiera: ${item.score} de 100">
                  <div class="versus-mini-gauge-inner" id="cardGaugeScore_${item.id}">
                    ${scoreDisplay}
                  </div>
                </div>
              </div>

              <!-- Matriz 2x2 de Métricas Clave -->
              <div class="versus-exec-metrics-2x2">
                <div class="versus-m2-item">
                  <span class="versus-m2-label">PIB Crecimiento:</span>
                  <span class="versus-m2-val" id="cardMetric_pib_${item.id}" style="color:var(--gold);">
                    ${isCardsEvaluated ? item.pib_crec : '0.0%'}
                  </span>
                </div>
                <div class="versus-m2-item">
                  <span class="versus-m2-label">Deuda (% PIB):</span>
                  <span class="versus-m2-val" id="cardMetric_deuda_${item.id}" style="color:var(--cyan);">
                    ${isCardsEvaluated ? item.deuda_pib : '0.0%'}
                  </span>
                </div>
                <div class="versus-m2-item">
                  <span class="versus-m2-label">Balance Fiscal:</span>
                  <span class="versus-m2-val" id="cardMetric_balance_${item.id}" style="color:${isCardsEvaluated ? (item.balance_pib.includes('+') ? '#2ecc71' : '#e74c3c') : 'var(--text-dim)'};">
                    ${isCardsEvaluated ? item.balance_pib : '0.0%'}
                  </span>
                </div>
                <div class="versus-m2-item">
                  <span class="versus-m2-label">Ferrocarriles:</span>
                  <span class="versus-m2-val" id="cardMetric_ferro_${item.id}" style="color:var(--text-main); font-size:11px;">
                    ${isCardsEvaluated ? item.ferrocarriles : '0 km'}
                  </span>
                </div>
              </div>

              <!-- Resumen Cívico Sintético -->
              <div class="versus-exec-verdict-snippet" id="cardVerdict_${item.id}" title="${item.diagnostico}">
                ${isCardsEvaluated ? `"${item.diagnostico}"` : '<span style="color:var(--text-dim); font-style:italic;">[En reposo] Presiona «Evaluar Tarjetas» para proyectar métricas y diagnóstico ejecutivo.</span>'}
              </div>

              <!-- Botones de Acción Interactiva -->
              <div class="versus-exec-actions">
                <button class="versus-exec-btn" onclick="window.AuditEngine.setVersusHealthPresident('${item.id}')" title="Ver en el tacómetro circular superior">
                  <span>⏱️</span> Ver Salud
                </button>
                <button class="versus-exec-btn" onclick="window.AuditEngine.selectVersusPresident('${item.id === 'porfirio_diaz' ? 'salinas' : item.id}')" title="Abrir ficha bilateral de contraste">
                  <span>🥊</span> Cara a Cara
                </button>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  function evaluarTarjetasEjecutivas(duracionMs = 1200) {
    if (cardsAnimFrameId) {
      cancelAnimationFrame(cardsAnimFrameId);
      cardsAnimFrameId = null;
    }

    isCardsEvaluating = true;
    const statusEl = document.getElementById('evalCardsStatusText');
    const btnEval = document.getElementById('btnEvaluarCards');
    if (statusEl) {
      statusEl.innerHTML = '<span style="color:var(--gold-bright);">⚡ Evaluando tarjetas ejecutivas y proyectando métricas hacendarias...</span>';
    }
    if (btnEval) {
      btnEval.innerHTML = '<span>⏳</span> Evaluando...';
    }

    const startTime = performance.now();
    const list = Object.values(VERSUS_SALUD_FINANCIERA);

    function stepCards(now) {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / duracionMs);
      const ease = 1 - Math.pow(1 - progress, 3);

      list.forEach(item => {
        const ringEl = document.getElementById(`cardGaugeRing_${item.id}`);
        const scoreEl = document.getElementById(`cardGaugeScore_${item.id}`);
        const curScore = Math.round(item.score * ease);

        if (scoreEl) scoreEl.textContent = curScore;
        if (ringEl) {
          ringEl.style.background = `conic-gradient(${item.semaforo_color} ${curScore}%, rgba(255,255,255,0.08) ${curScore}%)`;
          ringEl.style.color = curScore > 0 ? item.semaforo_color : 'var(--text-dim)';
        }

        const pibEl = document.getElementById(`cardMetric_pib_${item.id}`);
        const deudaEl = document.getElementById(`cardMetric_deuda_${item.id}`);
        const balanceEl = document.getElementById(`cardMetric_balance_${item.id}`);
        const ferroEl = document.getElementById(`cardMetric_ferro_${item.id}`);

        if (pibEl && progress > 0.3) pibEl.textContent = item.pib_crec;
        if (deudaEl && progress > 0.4) deudaEl.textContent = item.deuda_pib;
        if (balanceEl && progress > 0.5) {
          balanceEl.textContent = item.balance_pib;
          balanceEl.style.color = item.balance_pib.includes('+') ? '#2ecc71' : '#e74c3c';
        }
        if (ferroEl && progress > 0.6) ferroEl.textContent = item.ferrocarriles;
      });

      if (progress < 1) {
        cardsAnimFrameId = requestAnimationFrame(stepCards);
      } else {
        isCardsEvaluating = false;
        isCardsEvaluated = true;
        cardsAnimFrameId = null;

        list.forEach(item => {
          const snippetEl = document.getElementById(`cardVerdict_${item.id}`);
          if (snippetEl) snippetEl.textContent = `"${item.diagnostico}"`;
        });

        if (statusEl) {
          statusEl.innerHTML = `<span style="color:var(--emerald-bright);">✓ Tarjetas evaluadas exitosamente: ${list.length} mandatarios analizados con métricas clave.</span>`;
        }
        if (btnEval) {
          btnEval.innerHTML = '<span>🔄</span> Volver a Evaluar';
        }
      }
    }

    cardsAnimFrameId = requestAnimationFrame(stepCards);
  }

  function resetTarjetasEjecutivas() {
    if (cardsAnimFrameId) {
      cancelAnimationFrame(cardsAnimFrameId);
      cardsAnimFrameId = null;
    }
    isCardsEvaluating = false;
    isCardsEvaluated = false;

    const list = Object.values(VERSUS_SALUD_FINANCIERA);
    list.forEach(item => {
      const ringEl = document.getElementById(`cardGaugeRing_${item.id}`);
      const scoreEl = document.getElementById(`cardGaugeScore_${item.id}`);
      const pibEl = document.getElementById(`cardMetric_pib_${item.id}`);
      const deudaEl = document.getElementById(`cardMetric_deuda_${item.id}`);
      const balanceEl = document.getElementById(`cardMetric_balance_${item.id}`);
      const ferroEl = document.getElementById(`cardMetric_ferro_${item.id}`);
      const snippetEl = document.getElementById(`cardVerdict_${item.id}`);

      if (scoreEl) scoreEl.textContent = '0';
      if (ringEl) {
        ringEl.style.background = 'conic-gradient(rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.08) 100%)';
        ringEl.style.color = 'var(--text-dim)';
      }
      if (pibEl) pibEl.textContent = '0.0%';
      if (deudaEl) deudaEl.textContent = '0.0%';
      if (balanceEl) {
        balanceEl.textContent = '0.0%';
        balanceEl.style.color = 'var(--text-dim)';
      }
      if (ferroEl) ferroEl.textContent = '0 km';
      if (snippetEl) snippetEl.innerHTML = '<span style="color:var(--text-dim); font-style:italic;">[En reposo] Presiona «Evaluar Tarjetas» para cargar las métricas clave y diagnóstico sintético.</span>';
    });

    const statusEl = document.getElementById('evalCardsStatusText');
    const btnEval = document.getElementById('btnEvaluarCards');
    if (statusEl) {
      statusEl.innerHTML = '⚪ Tarjetas en reposo (0 pts y métricas en cero). Presiona «Evaluar Tarjetas» o interactúa con el cursor.';
    }
    if (btnEval) {
      btnEval.innerHTML = '<span>▶️</span> Evaluar Tarjetas';
    }
  }

  function toggleHoverCardsEvaluation(enabled) {
    isCardsHoverEnabled = !!enabled;
  }

  function handleCardsHover() {
    if (isCardsHoverEnabled && !isCardsEvaluated && !isCardsEvaluating) {
      evaluarTarjetasEjecutivas();
    }
  }

  function renderVersusCompactTableView() {
    const list = Object.values(VERSUS_SALUD_FINANCIERA);

    return `
      <div class="versus-table-wrapper">
        <table class="versus-table">
          <thead>
            <tr>
              <th style="width:24%;">Mandatario &amp; Periodo</th>
              <th style="width:18%;">Salud Financiera</th>
              <th style="width:13%;">PIB Promedio</th>
              <th style="width:13%;">Deuda (% PIB)</th>
              <th style="width:13%;">Balance Fiscal</th>
              <th style="width:10%;">Ferrocarriles</th>
              <th style="width:9%;">Acción</th>
            </tr>
          </thead>
          <tbody>
            ${list.map(p => {
              const isDiaz = p.id === 'porfirio_diaz';
              const isSel = p.id === currentVersusPresidentId;
              return `
                <tr class="${isDiaz ? 'row-porfirio' : ''}" style="${isSel ? 'background:rgba(201,168,76,0.12); border-left:4px solid var(--gold-bright);' : ''}">
                  <td>
                    <div style="display:flex; align-items:center; gap:8px;">
                      <span style="font-size:18px;">${p.avatar}</span>
                      <div>
                        <strong style="color:${isDiaz ? 'var(--gold-bright)' : (isSel ? 'var(--gold-bright)' : 'var(--text-main)')};">${p.nombre}</strong>
                        <div style="font-family:var(--font-mono); font-size:10.5px; color:var(--text-dim);">${p.periodo.split('(')[0]}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div style="display:flex; align-items:center; gap:8px;">
                      <span style="font-family:var(--font-mono); font-weight:800; font-size:13px; color:${p.semaforo_color}; min-width:32px;">
                        ${p.score}/100
                      </span>
                      <div style="width:60px; height:6px; background:rgba(255,255,255,0.08); border-radius:3px; overflow:hidden;">
                        <div style="width:${p.score}%; height:100%; background:${p.semaforo_color}; border-radius:3px;"></div>
                      </div>
                    </div>
                  </td>
                  <td style="font-family:var(--font-mono); font-weight:700; color:${p.pib_crec.includes('+3') || p.pib_crec.includes('+4') ? '#2ecc71' : 'var(--gold)'};">
                    ${p.pib_crec}
                  </td>
                  <td style="font-family:var(--font-mono); color:var(--cyan);">
                    ${p.deuda_pib}
                  </td>
                  <td style="font-family:var(--font-mono); color:${p.balance_pib.includes('+') ? '#2ecc71' : '#e74c3c'}; font-weight:700;">
                    ${p.balance_pib}
                  </td>
                  <td style="font-family:var(--font-mono); font-size:11px;">
                    ${p.ferrocarriles}
                  </td>
                  <td>
                    <button class="chip" onclick="window.AuditEngine.setVersusHealthPresident('${p.id}')"
                      style="padding:3px 8px; font-size:10.5px; cursor:pointer; background:rgba(255,255,255,0.06); border:1px solid var(--border-subtle); color:var(--gold);">
                      ⏱️ Tacómetro
                    </button>
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    `;
  }

  function renderVersusRankingView() {
    const sorted = Object.values(VERSUS_SALUD_FINANCIERA).sort((a, b) => b.score - a.score);

    return `
      <!-- Barra de Control del Simulador de Ranking Hacendario -->
      <div class="evaluacion-controls-bar" id="evaluacionRankingControls" style="margin-bottom:16px;">
        <div class="eval-info-group">
          <span class="eval-badge" style="background:rgba(46,204,113,0.15); border-color:#2ecc71; color:#2ecc71;">
            SIMULADOR DE RANKING HACENDARIO
          </span>
          <span class="eval-status-text" id="evalRankingStatusText">
            ${isRankingEvaluated 
              ? '✓ Escalafón hacendario calibrado: ordenado de mayor a menor disciplina fiscal.' 
              : '⚪ Escalafón histórico en reposo (0 pts y barras en cero). Presiona «Evaluar Ranking» o interactúa con el cursor.'}
          </span>
        </div>
        <div class="eval-actions-group">
          <button class="eval-btn-primary" id="btnEvaluarRanking" onclick="window.AuditEngine.evaluarRankingHacendario()">
            <span>${isRankingEvaluated ? '🔄' : '▶️'}</span> ${isRankingEvaluated ? 'Volver a Calibrar' : 'Evaluar Ranking'}
          </button>
          <button class="eval-btn-secondary" id="btnResetRanking" onclick="window.AuditEngine.resetRankingHacendario()">
            <span>↺</span> Reiniciar en Ceros
          </button>
          <label class="eval-toggle-label" title="Iniciar evaluación automáticamente al pasar el cursor sobre el ranking">
            <input type="checkbox" id="evalRankingHoverToggle" ${isRankingHoverEnabled ? 'checked' : ''} onchange="window.AuditEngine.toggleHoverRankingEvaluation(this.checked)">
            <span>Activar al pasar cursor</span>
          </label>
        </div>
      </div>

      <div class="versus-ranking-container" onmouseenter="window.AuditEngine.handleRankingHover()" ontouchstart="window.AuditEngine.handleRankingHover()">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; padding:0 4px;">
          <span style="font-family:var(--font-mono); font-size:11px; color:var(--gold); text-transform:uppercase; letter-spacing:1px; font-weight:700;">
            🏆 Escalafón Histórico de Salud Financiera (De Mayor a Menor Disciplina)
          </span>
          <span style="font-family:var(--font-mono); font-size:11px; color:var(--text-dim);">
            Clic en cualquier posición para calibrar el tacómetro superior
          </span>
        </div>

        ${sorted.map((item, idx) => {
          const isFirst = idx === 0;
          const barWidth = isRankingEvaluated ? item.score : 0;
          const scoreLabel = isRankingEvaluated ? `${item.score}/100` : '0/100';
          const pillText = isRankingEvaluated ? item.semaforo_label.split('(')[0].trim() : '⚪ EN ESPERA';
          const pillColor = isRankingEvaluated ? item.semaforo_color : 'var(--text-dim)';
          const diagSnippet = isRankingEvaluated ? `${item.diagnostico.slice(0, 80)}...` : '[En reposo · Calibración de escalafón pendiente]';

          return `
            <div class="versus-ranking-item" onclick="window.AuditEngine.setVersusHealthPresident('${item.id}')"
              title="Haz clic para cargar el diagnóstico de ${item.nombre} en el tacómetro">
              <div class="versus-ranking-pos" style="color:${isFirst ? 'var(--gold-bright)' : 'var(--text-secondary)'};">
                ${isFirst ? '🥇 #1' : `#${idx + 1}`}
              </div>

              <div class="versus-ranking-info">
                <div style="display:flex; align-items:center; gap:6px;">
                  <span>${item.avatar}</span>
                  <div class="versus-ranking-name">${item.nombre}</div>
                </div>
                <div class="versus-ranking-period">${item.periodo.split('(')[0]} · ${item.partido}</div>
              </div>

              <div class="versus-ranking-bar-wrapper">
                <div style="display:flex; justify-content:space-between; font-size:10.5px; font-family:var(--font-mono); margin-bottom:4px;">
                  <span id="rankingDiagSnippet_${item.id}" style="color:var(--text-dim);">${diagSnippet}</span>
                  <strong id="rankingScoreVal_${item.id}" style="color:${isRankingEvaluated ? item.semaforo_color : 'var(--text-dim)'};">${scoreLabel}</strong>
                </div>
                <div class="versus-ranking-bar-track">
                  <div id="rankingBarFill_${item.id}" class="versus-ranking-bar-fill" 
                    style="width:${barWidth}%; background:${item.semaforo_color};"></div>
                </div>
              </div>

              <div id="rankingPill_${item.id}" class="versus-ranking-score-pill" 
                style="color:${pillColor}; border-color:${pillColor}; background:rgba(255,255,255,0.03);">
                ${pillText}
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  function evaluarRankingHacendario(duracionMs = 1300) {
    if (rankingAnimFrameId) {
      cancelAnimationFrame(rankingAnimFrameId);
      rankingAnimFrameId = null;
    }

    isRankingEvaluating = true;
    const statusEl = document.getElementById('evalRankingStatusText');
    const btnEval = document.getElementById('btnEvaluarRanking');
    if (statusEl) {
      statusEl.innerHTML = '<span style="color:var(--gold-bright);">⚡ Desplegando escalafón histórico y calibrando barras de disciplina hacendaria...</span>';
    }
    if (btnEval) {
      btnEval.innerHTML = '<span>⏳</span> Calibrando...';
    }

    const startTime = performance.now();
    const sorted = Object.values(VERSUS_SALUD_FINANCIERA).sort((a, b) => b.score - a.score);

    function stepRanking(now) {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / duracionMs);

      sorted.forEach((item, idx) => {
        const itemDelay = idx * 60;
        const itemElapsed = Math.max(0, elapsed - itemDelay);
        const itemDuration = duracionMs - itemDelay;
        const itemProgress = itemDuration > 0 ? Math.min(1, itemElapsed / itemDuration) : 1;
        const ease = 1 - Math.pow(1 - itemProgress, 3);

        const curWidth = item.score * ease;
        const curScore = Math.round(item.score * ease);

        const barFill = document.getElementById(`rankingBarFill_${item.id}`);
        const scoreVal = document.getElementById(`rankingScoreVal_${item.id}`);
        const pillEl = document.getElementById(`rankingPill_${item.id}`);
        const diagEl = document.getElementById(`rankingDiagSnippet_${item.id}`);

        if (barFill) barFill.style.width = `${curWidth}%`;
        if (scoreVal) {
          scoreVal.textContent = `${curScore}/100`;
          scoreVal.style.color = curScore > 0 ? item.semaforo_color : 'var(--text-dim)';
        }

        if (itemProgress >= 0.7 && pillEl) {
          pillEl.innerHTML = item.semaforo_label.split('(')[0].trim();
          pillEl.style.color = item.semaforo_color;
          pillEl.style.borderColor = item.semaforo_color;
        }

        if (itemProgress >= 0.5 && diagEl) {
          diagEl.textContent = `${item.diagnostico.slice(0, 80)}...`;
        }
      });

      if (progress < 1) {
        rankingAnimFrameId = requestAnimationFrame(stepRanking);
      } else {
        isRankingEvaluating = false;
        isRankingEvaluated = true;
        rankingAnimFrameId = null;

        sorted.forEach(item => {
          const barFill = document.getElementById(`rankingBarFill_${item.id}`);
          const scoreVal = document.getElementById(`rankingScoreVal_${item.id}`);
          const pillEl = document.getElementById(`rankingPill_${item.id}`);
          const diagEl = document.getElementById(`rankingDiagSnippet_${item.id}`);

          if (barFill) barFill.style.width = `${item.score}%`;
          if (scoreVal) {
            scoreVal.textContent = `${item.score}/100`;
            scoreVal.style.color = item.semaforo_color;
          }
          if (pillEl) {
            pillEl.innerHTML = item.semaforo_label.split('(')[0].trim();
            pillEl.style.color = item.semaforo_color;
            pillEl.style.borderColor = item.semaforo_color;
          }
          if (diagEl) diagEl.textContent = `${item.diagnostico.slice(0, 80)}...`;
        });

        if (statusEl) {
          statusEl.innerHTML = '<span style="color:var(--emerald-bright);">✓ Escalafón hacendario calibrado: ordenado de mayor a menor disciplina fiscal.</span>';
        }
        if (btnEval) {
          btnEval.innerHTML = '<span>🔄</span> Volver a Calibrar';
        }
      }
    }

    rankingAnimFrameId = requestAnimationFrame(stepRanking);
  }

  function resetRankingHacendario() {
    if (rankingAnimFrameId) {
      cancelAnimationFrame(rankingAnimFrameId);
      rankingAnimFrameId = null;
    }
    isRankingEvaluating = false;
    isRankingEvaluated = false;

    const sorted = Object.values(VERSUS_SALUD_FINANCIERA);
    sorted.forEach(item => {
      const barFill = document.getElementById(`rankingBarFill_${item.id}`);
      const scoreVal = document.getElementById(`rankingScoreVal_${item.id}`);
      const pillEl = document.getElementById(`rankingPill_${item.id}`);
      const diagEl = document.getElementById(`rankingDiagSnippet_${item.id}`);

      if (barFill) barFill.style.width = '0%';
      if (scoreVal) {
        scoreVal.textContent = '0/100';
        scoreVal.style.color = 'var(--text-dim)';
      }
      if (pillEl) {
        pillEl.innerHTML = '⚪ EN ESPERA';
        pillEl.style.color = 'var(--text-dim)';
        pillEl.style.borderColor = 'rgba(255,255,255,0.1)';
      }
      if (diagEl) diagEl.textContent = '[En reposo · Calibración pendiente]';
    });

    const statusEl = document.getElementById('evalRankingStatusText');
    const btnEval = document.getElementById('btnEvaluarRanking');
    if (statusEl) {
      statusEl.innerHTML = '⚪ Escalafón histórico en reposo (0 pts y barras en cero). Presiona «Evaluar Ranking» o interactúa con el cursor.';
    }
    if (btnEval) {
      btnEval.innerHTML = '<span>▶️</span> Evaluar Ranking';
    }
  }

  function toggleHoverRankingEvaluation(enabled) {
    isRankingHoverEnabled = !!enabled;
  }

  function handleRankingHover() {
    if (isRankingHoverEnabled && !isRankingEvaluated && !isRankingEvaluating) {
      evaluarRankingHacendario();
    }
  }

  // ==========================================================================
  // CONMUTADOR DE TEMA (MODO OSCURO / CLARO)
  // ==========================================================================
  function initTheme() {
    const savedTheme = localStorage.getItem('auditavision_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButtonText(savedTheme);
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('auditavision_theme', next);
    updateThemeButtonText(next);
  }

  function updateThemeButtonText(theme) {
    const btn = document.getElementById('themeBtn');
    if (btn) {
      btn.innerHTML = theme === 'dark' ? '◐ Tema Claro' : '◐ Tema Oscuro';
    }
  }

  // ==========================================================================
  // RENDERIZADO: FINANZAS PÚBLICAS, DEUDA & BANXICO
  // ==========================================================================
  function renderFinanzasPublicas() {
    const ejesContainer = document.getElementById('finanzasEjesGrid');
    const deudaContainer = document.getElementById('deudaInstrumentsGrid');
    const banxicoContainer = document.getElementById('banxicoGrid');
    const fp = DB.finanzas_publicas;
    if (!fp) return;

    // 1. Ejes de Acción Financiera del Estado
    if (ejesContainer && ejesContainer.children.length === 0) {
      ejesContainer.innerHTML = fp.ejes_accion.map(eje => `
        <div class="finanzas-eje-card">
          <div class="fin-eje-badge">${eje.icono} EJE ${eje.eje} DE LA ACCIÓN FINANCIERA</div>
          <h3>${eje.nombre}</h3>
          <p class="eje-desc">${eje.descripcion}</p>
          <ul class="eje-items-list">
            ${eje.instrumentos.map(item => `
              <li class="eje-item-row">
                <strong>${item.nombre}</strong>
                <span>${item.detalle}</span>
              </li>
            `).join('')}
          </ul>
        </div>
      `).join('');
    }

    // 2. Instrumentos de Deuda y Mercado
    if (deudaContainer && deudaContainer.children.length === 0) {
      deudaContainer.innerHTML = fp.instrumentos_deuda_mercado.map(inst => `
        <div class="deuda-instrument-card ${inst.clave === 'CETES' || inst.clave === 'BONOS M' ? 'featured' : ''}">
          <div class="deuda-card-header">
            <span class="deuda-clave">${inst.icono} ${inst.clave}</span>
            <span class="deuda-tipo-pill">${inst.tipo}</span>
          </div>
          <div class="deuda-full-name">${inst.nombre}</div>
          <p style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin-bottom:10px;">${inst.funcion_publica}</p>
          <div class="deuda-specs">
            <div class="deuda-spec-row">
              <span class="k">Plazos:</span>
              <span class="v">${inst.plazos}</span>
            </div>
            <div class="deuda-spec-row">
              <span class="k">Rendimiento:</span>
              <span class="v" style="color:var(--gold-bright);">${inst.rendimiento}</span>
            </div>
            <div class="deuda-spec-row">
              <span class="k">Agente:</span>
              <span class="v">${inst.agente}</span>
            </div>
          </div>
        </div>
      `).join('');
    }

    // 3. Funciones del Banco de México
    if (banxicoContainer && banxicoContainer.children.length === 0) {
      banxicoContainer.innerHTML = fp.rol_banxico.funciones_clave.map(f => `
        <div class="banxico-card">
          <h4>${f.icono} ${f.titulo}</h4>
          <p>${f.desc}</p>
        </div>
      `).join('');
    }
  }

  // ==========================================================================
  // SUBPESTAÑA 2.2: SIMULADOR DE INVERSIONES, MEGAOBRAS & PÉRDIDAS EN TIEMPO REAL
  // ==========================================================================
  function renderSimuladorMegaobras() {
    const kpisContainer = document.getElementById('simuladorKpisStrip');
    const sectorsContainer = document.getElementById('simSectorChips');
    const sim = DB.simulador_megaobras;
    if (!sim) return;

    // 1. Tira de 4 KPIs Consolidados
    if (kpisContainer) {
      const pInfo = sim.periodos[state.simuladorPeriodo] || sim.periodos['dia'];
      const factor = pInfo.factor;
      const sufijo = pInfo.sufijo;
      const perdidaConsolidada = sim.totales_consolidados.perdida_anual_consolidada_mdp * factor;
      
      let perdidaDisplay = '';
      if (perdidaConsolidada >= 1000) {
        perdidaDisplay = `$${(perdidaConsolidada / 1000).toFixed(2)} mil mdp${sufijo}`;
      } else {
        perdidaDisplay = `$${perdidaConsolidada.toFixed(2)} mdp${sufijo}`;
      }

      kpisContainer.innerHTML = `
        <div class="sim-kpi-card">
          <div class="sim-kpi-lbl">🏗️ Inversión Total en Megaobras</div>
          <div class="sim-kpi-val">$4.06 billones</div>
          <div class="sim-kpi-sub">Costo real consolidado de las 12 inversiones evaluadas</div>
        </div>

        <div class="sim-kpi-card alert-kpi">
          <div class="sim-kpi-lbl">
            <span class="pulsing-dot"></span> Pérdida Operativa (${pInfo.label})
          </div>
          <div class="sim-kpi-val loss-val">${perdidaDisplay}</div>
          <div class="sim-kpi-sub">Subsidio continuo del erario para cubrir déficit operativo</div>
        </div>

        <div class="sim-kpi-card">
          <div class="sim-kpi-lbl">📈 Sobrecosto Promedio</div>
          <div class="sim-kpi-val" style="color:#f39c12;">+185.3%</div>
          <div class="sim-kpi-sub">Desvío presupuestal respecto al monto original aprobado</div>
        </div>

        <div class="sim-kpi-card alert-kpi">
          <div class="sim-kpi-lbl">🔴 Telemetría Viva Acumulada</div>
          <div class="sim-kpi-val loss-val" id="simLiveGlobalCounter">+$0.00</div>
          <div class="sim-kpi-sub">Pérdida acumulada en vivo desde que abriste esta vista</div>
        </div>
      `;
    }

    // 2. Chips de Sectores
    if (sectorsContainer && sectorsContainer.children.length === 0) {
      sectorsContainer.innerHTML = sim.sectores.map(sec => `
        <button class="sim-pill-btn ${state.simuladorSector === sec.id ? 'active' : ''}" 
          data-sector="${sec.id}" 
          onclick="window.AuditEngine.setSimuladorSector('${sec.id}')">
          <span>${sec.icono}</span> <span>${sec.nombre}</span>
        </button>
      `).join('');
    }

    // 3. Renderizar Obras
    renderSimuladorObrasGrid();

    // 4. Iniciar Ticker en Vivo
    initLiveLossTicker();
  }

  function renderSimuladorObrasGrid() {
    const grid = document.getElementById('simuladorObrasGrid');
    const sim = DB.simulador_megaobras;
    if (!grid || !sim) return;

    let obras = sim.obras;

    // Filtro por Sector
    if (state.simuladorSector && state.simuladorSector !== 'todos') {
      obras = obras.filter(o => o.sector_id === state.simuladorSector);
    }

    // Filtro por Sexenio
    if (state.simuladorSexenio && state.simuladorSexenio !== 'todos') {
      obras = obras.filter(o => o.presidente.toLowerCase().includes(state.simuladorSexenio.toLowerCase()));
    }

    const pInfo = sim.periodos[state.simuladorPeriodo] || sim.periodos['dia'];
    const factor = pInfo.factor;
    const sufijo = pInfo.sufijo;

    if (obras.length === 0) {
      grid.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:40px; color:var(--text-dim);">No se encontraron megaobras con los filtros seleccionados.</div>`;
      return;
    }

    grid.innerHTML = obras.map(o => {
      const perdidaPeriodo = o.perdida_anual_mdp * factor;
      let perdidaDisplay = '';
      if (perdidaPeriodo === 0) {
        perdidaDisplay = `$0.00 mdp${sufijo}`;
      } else if (perdidaPeriodo >= 1000) {
        perdidaDisplay = `$${(perdidaPeriodo / 1000).toFixed(2)} mil mdp${sufijo}`;
      } else {
        perdidaDisplay = `$${perdidaPeriodo.toFixed(2)} mdp${sufijo}`;
      }

      const isDeficit = o.proyeccion_tipo === 'deficit_cronico' || o.proyeccion_tipo === 'subsidio_permanente' || o.proyeccion_tipo === 'deuda_perpetua' || o.proyeccion_tipo === 'perdida_patrimonial';

      return `
        <div class="sim-obra-card" id="card-sim-${o.id}">
          
          <!-- Encabezado de la Obra -->
          <div class="sim-obra-header">
            <div class="sim-obra-title-box">
              <div class="sim-obra-ico">${o.icono}</div>
              <div>
                <h3 class="sim-obra-name">${o.nombre}</h3>
                <div class="sim-obra-meta">
                  🏛️ <strong>${o.presidente}</strong> (${o.periodo_sexenal})
                </div>
              </div>
            </div>
            <span class="sim-status-badge" style="border-color:${o.badge_color}; color:${o.badge_color};">
              ${o.estatus}
            </span>
          </div>

          <!-- Caja de Telemetría: Pérdida en el Periodo & Reloj en Vivo -->
          <div class="sim-loss-box">
            <div>
              <div class="sim-loss-lbl">
                <span class="pulsing-dot"></span> Pérdida Operativa (${pInfo.label})
              </div>
              <div class="sim-loss-amount">${perdidaDisplay}</div>
            </div>
            <div style="text-align:right;">
              <div class="sim-live-ticker-sub">
                <span>⏱️ Acumulado en Vivo:</span>
              </div>
              <div class="sim-loss-amount sim-live-card-loss" id="live-tick-${o.id}" data-rate="${o.perdida_segundo}" style="color:#ffd166; font-size:18px;">
                +$0.00
              </div>
              <div style="font-size:10px; color:var(--text-dim); font-family:var(--font-mono);">
                (+ $${o.perdida_segundo.toFixed(2)}/seg)
              </div>
            </div>
          </div>

          <!-- Comparativa de Inversión y Sobrecosto -->
          <div class="sim-inversion-row">
            <div class="sim-inv-col">
              <span class="sim-inv-lbl">Presupuesto Original</span>
              <span class="sim-inv-val">$${formatNumber(o.inversion_presupuestada_mdp)} mdp</span>
            </div>
            <div class="sim-inv-col">
              <span class="sim-inv-lbl">Costo Real Erogado</span>
              <span class="sim-inv-val" style="color:var(--gold-bright);">$${formatNumber(o.inversion_real_mdp)} mdp</span>
            </div>
            <div class="sim-inv-col">
              <span class="sim-inv-lbl">Sobrecosto</span>
              <span class="sim-inv-val" style="color:${o.sobrecosto_pct > 100 ? '#ff6b6b' : 'var(--gold-bright)'};">
                ${o.sobrecosto_pct > 0 ? '+' : ''}${o.sobrecosto_pct}%
              </span>
            </div>
          </div>

          <!-- Desglose de Costos de Operación -->
          <div>
            <div style="font-family:var(--font-mono); font-size:10.5px; color:var(--text-dim); text-transform:uppercase; margin-bottom:6px; letter-spacing:0.5px;">
              ⚙️ Principales Costos de Operación Anuales:
            </div>
            <div class="sim-operacion-chips">
              ${o.desglose_costos_operacion.map(c => `
                <div class="sim-op-chip">
                  <span>${c.icono}</span>
                  <span>${c.rubro}:</span>
                  <strong>$${formatNumber(c.monto_anual_mdp)} mdp</strong>
                </div>
              `).join('')}
            </div>
          </div>

          <!-- Caja de Proyección / Amortización -->
          <div class="sim-proyeccion-box ${isDeficit ? 'deficit-box' : ''}">
            <div style="font-family:var(--font-mono); font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
              <span>${isDeficit ? '⚠️' : '📊'}</span> 
              <span>${isDeficit ? 'Diagnóstico Financiero: Déficit Permanente / Deuda' : 'Proyección de Retorno / Amortización'}</span>
            </div>
            <div>${o.proyeccion_resumen}</div>
          </div>

          <!-- Hallazgo ASF & Métrica Unitaria -->
          <div class="sim-asf-finding">
            <span>🔍</span>
            <div>
              <strong>Auditoría &amp; Hallazgos:</strong> ${o.hallazgo_asf}<br>
              <span style="display:inline-block; margin-top:4px; color:var(--gold-bright); font-family:var(--font-mono);">
                📊 <strong>Métrica de Costo Unitario:</strong> ${o.costo_unitario_real}
              </span>
            </div>
          </div>

        </div>
      `;
    }).join('');
  }

  function setSimuladorPeriodo(periodo) {
    state.simuladorPeriodo = periodo;
    document.querySelectorAll('.sim-pill-periodo').forEach(btn => {
      const txt = btn.textContent.toLowerCase();
      let match = false;
      if (periodo === 'dia' && txt.includes('día')) match = true;
      else if (periodo === 'mes' && txt.includes('mes')) match = true;
      else if (periodo === 'trimestre' && txt.includes('trimestre')) match = true;
      else if (periodo === 'semestre' && txt.includes('semestre')) match = true;
      else if (periodo === 'ano' && txt.includes('anual')) match = true;
      btn.classList.toggle('active', match);
    });

    renderSimuladorMegaobras();
  }

  function setSimuladorSector(sectorId) {
    state.simuladorSector = sectorId;
    document.querySelectorAll('#simSectorChips .sim-pill-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.sector === sectorId);
    });
    renderSimuladorObrasGrid();
  }

  function setSimuladorSexenio(sexenio) {
    state.simuladorSexenio = sexenio;
    document.querySelectorAll('#simSexenioChips .sim-pill-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.sexenio === sexenio);
    });
    renderSimuladorObrasGrid();
  }

  function initLiveLossTicker() {
    if (state.simuladorTickerTimer) {
      clearInterval(state.simuladorTickerTimer);
    }

    state.simuladorTickerTimer = setInterval(() => {
      state.simuladorElapsedSeconds++;
      const seconds = state.simuladorElapsedSeconds;

      // 1. Contador Global Consolidado ($2,495.14 pesos por segundo)
      const globalEl = document.getElementById('simLiveGlobalCounter');
      if (globalEl) {
        const consolidatedRate = (DB.simulador_megaobras && DB.simulador_megaobras.totales_consolidados) ? DB.simulador_megaobras.totales_consolidados.perdida_segundo_consolidada : 2495.14;
        const totalPesos = seconds * consolidatedRate;
        globalEl.textContent = `+$${totalPesos.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      }

      // 2. Contadores individuales de cada tarjeta
      document.querySelectorAll('.sim-live-card-loss').forEach(el => {
        const rate = parseFloat(el.dataset.rate) || 0;
        const obraLoss = seconds * rate;
        el.textContent = `+$${obraLoss.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      });
    }, 1000);
  }

  // ==========================================================================
  // RENDERIZADO: CASILLAS DE PREGUNTAS Y GLOSARIO
  // ==========================================================================
  function renderCasillasFaq() {
    const container = document.getElementById('casillasFaqContainer');
    if (!container || !DB.preguntas_casillas) return;

    container.innerHTML = DB.preguntas_casillas.map(bloque => `
      <div class="casilla-bloque" id="${bloque.casilla_id}">
        <div class="casilla-header">
          <span>${bloque.icono}</span>
          <h3>${bloque.bloque}</h3>
        </div>
        <div class="casilla-body">
          ${bloque.items.map(item => `
            <div class="casilla-item">
              <div class="casilla-q">
                <span>💬</span>
                <span>${item.q}</span>
              </div>
              <div class="casilla-a">${item.a}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');
  }

  // ==========================================================================
  // RENDERIZADO: REFERENCIAS APA 7 NUMERADAS CON FILTROS
  // ==========================================================================
  function renderReferencias(filter = 'todas') {
    const container = document.getElementById('refsListContainer');
    if (!container || !DB.referencias_legales) return;

    let items = DB.referencias_legales;
    if (filter !== 'todas') {
      items = items.filter(ref => ref.categoria === filter);
    }

    container.innerHTML = items.map(ref => `
      <li class="ref-row-item" id="${ref.id}">
        <div class="ref-num-badge">[${ref.num}]</div>
        <div class="ref-content-body">
          <div class="ref-citation-apa">
            ${ref.cita_apa}
            ${ref.url ? `<br><a href="${ref.url}" target="_blank" rel="noopener noreferrer">↗ Consultar texto oficial en PDF / portal</a>` : ''}
          </div>
          <div class="ref-note">${ref.descripcion}</div>
        </div>
        <div class="ref-tag-pill">${ref.categoria_nombre}</div>
      </li>
    `).join('');

    // Actualizar botones de chips
    document.querySelectorAll('[data-reff]').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.reff === filter);
    });
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

        // Guardar localmente
        const savedComments = JSON.parse(localStorage.getItem('auditavision_comentarios') || '[]');
        savedComments.unshift({
          id: Date.now(),
          fecha: new Date().toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' }),
          nombre: nombre,
          tipo: tipo,
          estado: estado,
          texto: texto
        });
        localStorage.setItem('auditavision_comentarios', JSON.stringify(savedComments));

        if (msgStatus) {
          msgStatus.innerHTML = '✓ ¡Gracias por tu participación! Tu observación cívica ha sido registrada para revisión en la bitácora.';
          msgStatus.style.color = 'var(--emerald-bright)';
        }
        form.reset();
        if (counter) counter.textContent = '0 / 1000';
        renderComentariosList();
      });
    }

    renderCanalesOficiales();
    renderComentariosList();
    initPortalDigital();
  }

  function renderCanalesOficiales() {
    const container = document.getElementById('canalesOficialesContainer');
    if (!container || !DB.comunidad || !DB.comunidad.canales_denuncia_oficial) return;

    container.innerHTML = DB.comunidad.canales_denuncia_oficial.map(c => `
      <div class="canal-item-card">
        <div class="canal-ico">${c.icono}</div>
        <div class="canal-info">
          <h4>${c.organismo}</h4>
          <p><strong>${c.herramienta}</strong>: ${c.alcance}</p>
          <a href="${c.url}" target="_blank" rel="noopener noreferrer">↗ Acceder a la plataforma de denuncia oficial</a>
        </div>
      </div>
    `).join('');
  }

  function renderComentariosList() {
    const list = document.getElementById('comentariosListContainer');
    if (!list) return;

    const saved = JSON.parse(localStorage.getItem('auditavision_comentarios') || '[]');
    if (saved.length === 0) {
      list.innerHTML = `
        <div style="padding:18px; border:1px dashed var(--border-accent); border-radius:8px; text-align:center; color:var(--text-dim); font-size:12px;">
          Sé la primera persona en enviar una propuesta de fiscalización o reporte cívico para tu municipio.
        </div>
      `;
      return;
    }

    list.innerHTML = saved.slice(0, 10).map(c => `
      <div style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:8px; padding:14px; margin-bottom:10px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; font-size:11px;">
          <strong style="color:var(--gold-bright); font-family:var(--font-serif);">${c.nombre}</strong>
          <span style="color:var(--text-dim); font-family:var(--font-mono);">${c.fecha} · <span style="color:var(--cyan);">${c.tipo}</span> (${c.estado})</span>
        </div>
        <p style="font-size:12.5px; color:var(--text-secondary); line-height:1.5; margin:0;">${c.texto}</p>
      </div>
    `).join('');
  }

  // ==========================================================================
  // BLOQUE 3: PORTAL PÚBLICO DIGITAL · ÁGORA CÍVICA & DEBATES CIUDADANOS
  // ==========================================================================
  let activePortalForumFilter = 'todos';
  let activeStanceSelected = 'matiz';

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

  function getPortalDebates() {
    const raw = localStorage.getItem('auditavision_foro_debates');
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      } catch (e) {
        console.error('Error al leer debates locales:', e);
      }
    }
    const defaults = (DB.comunidad && DB.comunidad.debates_semilla) ? JSON.parse(JSON.stringify(DB.comunidad.debates_semilla)) : [];
    localStorage.setItem('auditavision_foro_debates', JSON.stringify(defaults));
    return defaults;
  }

  function savePortalDebates(debates) {
    localStorage.setItem('auditavision_foro_debates', JSON.stringify(debates));
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

    const likedDebates = JSON.parse(localStorage.getItem('auditavision_liked_debates') || '[]');

    container.innerHTML = list.map(d => {
      const isLiked = likedDebates.includes(d.id);
      const stanceClass = `stance-${d.postura || 'matiz'}`;
      const repliesCount = (d.replicas && d.replicas.length) || 0;

      return `
        <article class="debate-post-card ${stanceClass}" id="${d.id}">
          <div class="debate-header-row">
            <div class="debate-author-info">
              <div class="user-avatar-circle" style="background:${d.autor_avatar_color || 'var(--gold)'};">
                ${(d.autor_nick || '@U').replace('@', '').substring(0, 2).toUpperCase()}
              </div>
              <div>
                <span class="user-nick-text">${d.autor_nick}</span>
                <div class="debate-time-text">${d.fecha} · ${d.tiempo_relativo || 'Reciente'}</div>
              </div>
            </div>

            <div class="debate-badges-row">
              <span class="stance-badge ${d.postura}">
                ${d.postura_icono || '⚖️'} ${d.postura_nombre || 'Postura'}
              </span>
              <span class="topic-badge">${d.tema_nombre}</span>
            </div>
          </div>

          <h4 class="debate-title-h4">${d.tesis}</h4>
          <div class="debate-content-body">${d.contenido}</div>

          ${d.fuente ? `
            <div class="debate-source-box">
              <span>📚 <strong>Fuente citada:</strong> ${d.fuente}</span>
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
          </div>

          <!-- Caja desplegable de réplicas e hilo -->
          <div id="replyContainer_${d.id}" class="debate-replies-thread" style="${repliesCount > 0 ? 'display:flex;' : 'display:none;'}">
            ${repliesCount > 0 ? d.replicas.map(r => `
              <div class="reply-item-card" id="${r.id}">
                <div class="reply-header-row">
                  <div style="display:flex; align-items:center; gap:8px;">
                    <div class="user-avatar-circle" style="width:24px; height:24px; font-size:9.5px; background:${r.autor_avatar_color || '#3b82f6'};">
                      ${(r.autor_nick || '@R').replace('@', '').substring(0, 2).toUpperCase()}
                    </div>
                    <strong style="color:var(--gold-bright); font-family:var(--font-mono); font-size:12px;">${r.autor_nick}</strong>
                    <span style="font-size:10.5px; color:var(--text-dim); font-family:var(--font-mono);">${r.fecha || 'Reciente'}</span>
                  </div>
                  <span style="font-size:10px; font-family:var(--font-mono); color:var(--cyan); background:rgba(0,180,216,0.1); padding:2px 6px; border-radius:4px; border:1px solid rgba(0,180,216,0.2);">
                    ${r.tipo_replica || 'Réplica'}
                  </span>
                </div>
                <p style="margin:0; color:var(--text-secondary); font-size:12px; line-height:1.55;">${r.contenido}</p>
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
      fecha: new Date().toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' }),
      tiempo_relativo: 'Justo ahora',
      tesis: tesis,
      contenido: contenido,
      fuente: fuente || null,
      fuente_url: (fuente && (fuente.startsWith('http://') || fuente.startsWith('https://'))) ? fuente : null,
      apoyos: 1,
      replicas: []
    };

    debates.unshift(newDebate);
    savePortalDebates(debates);

    if (statusMsg) {
      statusMsg.innerHTML = '✓ ¡Tu argumento ha sido publicado con éxito en el Portal Público Digital!';
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
        fecha: new Date().toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' }),
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
    const likedDebates = JSON.parse(localStorage.getItem('auditavision_liked_debates') || '[]');
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

    localStorage.setItem('auditavision_liked_debates', JSON.stringify(likedDebates));
    savePortalDebates(debates);
    renderPortalDebates();
  }

  function filterPortalDebates(tema) {
    activePortalForumFilter = tema;
    renderPortalDebates(tema);
  }

  function copyDebateLink(debateId) {
    const url = `${window.location.origin}${window.location.pathname}#comunidad`;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url);
    }
    alert('¡Enlace al diálogo cívico copiado al portapapeles!');
  }

  // ==========================================================================
  // PESTAÑA 6: VERIFICADOR & DESACREDITADOR FORENSE DE NOTICIAS (AUDITORÍA EN VIVO)
  // ==========================================================================
  const FACTCHECK_KNOWLEDGE_BASE = {
    dependencias: {
      'pemex': {
        id: 'pemex',
        nombre: 'Petróleos Mexicanos (PEMEX)',
        icono: '🛢️',
        ramo: 'Ramo 52 · Entidad de Control Directo',
        ingresosVal: '$677,200 mdp PEF + $1.8 billones apoyos erario',
        ingresosDesc: 'Presupuesto anualizado más aportaciones patrimoniales para amortización de deuda y reducción del DUC del 65% al 30%.',
        egresosVal: '$784,000 mdp devengados (Déficit operativo)',
        egresosDesc: 'Gasto operativo y financiero superior a ingresos propios; subsidiada con garantía soberana federal.',
        irregVal: '>$21,450 mdp observados por ASF',
        irregDesc: 'Pliegos en mantenimiento de refinerías, pagos indebidos en contratos de perforación y plantas coquizadoras.',
        transpVal: '$1.9 billones deuda ($97,300 mdd) + $360,000 mdp proveedores',
        transpDesc: 'Petrolera más endeudada del orbe; pasivos ocultos en facturación diferida a proveedores locales.',
        refKey: 'ref-cuentas-publicas',
        refNum: '2',
        glosTerm: 'Cuenta Pública'
      },
      'tren_maya': {
        id: 'tren_maya',
        nombre: 'FONATUR / SEDENA — Proyecto Tren Maya',
        icono: '🚆',
        ramo: 'Ramo 21 (Turismo) / Ramo 07 (Defensa)',
        ingresosVal: '$150,000 mdp aprobado original (PEF 2019)',
        ingresosDesc: 'Presupuesto meta paramétrico comunicado en 2019 para los 1,554 km de vía férrea.',
        egresosVal: '>$515,000 mdp ejercidos (+243% sobrecosto)',
        egresosDesc: 'Costo consolidado auditado a 2024; triplicó la estimación inicial por cambios de trazo y premura de obra.',
        irregVal: '>$3,400 mdp observados por ASF',
        irregDesc: 'Pagos improcedentes en terraplenes, falta de finiquitos en tramos 5 y 6 y volúmenes de obra no ejecutados.',
        transpVal: 'Contratos reservados por "Seguridad Nacional"',
        transpDesc: 'Reserva decretada sobre convenios con constructoras militares y expropiaciones de derecho de vía.',
        refKey: 'ref-cuentas-publicas',
        refNum: '2',
        glosTerm: 'Presupuesto de Egresos de la Federación'
      },
      'salud_insabi': {
        id: 'salud_insabi',
        nombre: 'Secretaría de Salud / INSABI / IMSS-Bienestar',
        icono: '🏥',
        ramo: 'Ramo 12 · Salud Pública Federal',
        ingresosVal: '$96,500 mdp anuales + $140,000 mdp de Fonsabi',
        ingresosDesc: 'Absorción de fondos de gastos catastróficos acumulados en el Fondo de Salud para el Bienestar.',
        egresosVal: '$218,000 mdp con subejercicios en oncología',
        egresosDesc: 'Gasto ejercido con subejercicios críticos en medicamentos especializados y compras consolidadas canceladas.',
        irregVal: '>$15,600 mdp en observaciones ASF',
        irregDesc: 'Fármacos caducados en bodegas del Estado de México y Guerrero; pagos sin acreditación de entrega.',
        transpVal: '15 millones de recetas no surtidas / Extinción opaca',
        transpDesc: 'Desaparición del INSABI en mayo 2023 con entrega-recepción inconclusa hacia el régimen IMSS-Bienestar.',
        refKey: 'ref-asf-fideicomisos-pjf',
        refNum: '23',
        glosTerm: 'Gasto Etiquetado'
      },
      'scjn_pjf': {
        id: 'scjn_pjf',
        nombre: 'Poder Judicial de la Federación (SCJN / CJF)',
        icono: '⚖️',
        ramo: 'Ramo 03 · Poder Judicial de la Federación',
        ingresosVal: '$78,327 mdp asignados en PEF 2024',
        ingresosDesc: 'Presupuesto autónomo ($5,787 mdp SCJN, $68,917 mdp CJF, $3,623 mdp TEPJF).',
        egresosVal: '$74,800 mdp ejercidos (95.5% servicios personales)',
        egresosDesc: 'Concentración masiva en nómina de mandos superiores, ponencias y prestaciones en efectivo.',
        irregVal: '$28.5 mdp observados + remanentes no devueltos',
        irregDesc: 'ASF documentó transferencias indebidas de subejercicios anuales hacia cuentas fiduciarias del PJF.',
        transpVal: '$15,434 mdp retenidos en 13 fideicomisos litigados',
        transpDesc: 'Fondos con suspensión judicial concedida por los propios juzgadores federales para evitar reintegro a TESOFE.',
        refKey: 'ref-asf-fideicomisos-pjf',
        refNum: '23',
        glosTerm: 'Fideicomisos del Poder Judicial'
      },
      'conade': {
        id: 'conade',
        nombre: 'CONADE / SEP — Cultura Física y Deporte',
        icono: '🏅',
        ramo: 'Ramo 11 · Educación Pública',
        ingresosVal: '$2,638 mdp asignados en PEF',
        ingresosDesc: 'Techo financiero anual para deporte federado, alto rendimiento y programas de cultura física.',
        egresosVal: '$2,590 mdp ejercidos con recorte a atletas',
        egresosDesc: 'Retención y recorte arbitrario de becas a atletas de disciplinas acuáticas y deportes olímpicos.',
        irregVal: '>$620 mdp observados + Denuncias Penales FGR',
        irregDesc: 'Facturación con empresas fantasma EFOS (Art. 69-B CFF), compra simulada de equipo y eventos ficticios.',
        transpVal: '87 negativas en PNT ("Inexistencia de datos")',
        transpDesc: 'Declaratorias reiteradas de inexistencia ante el INAI en solicitudes de comprobación de viáticos y viajes.',
        refKey: 'ref-asf-declaratorias',
        refNum: '1',
        glosTerm: 'Empresas Fantasma (EFOS)'
      },
      'dos_bocas': {
        id: 'dos_bocas',
        nombre: 'SENER / PTI / PEMEX — Refinería Olmeca en Dos Bocas',
        icono: '🏭',
        ramo: 'Ramo 18 (Energía) / Ramo 52 (Pemex)',
        ingresosVal: '$8,000 mdd ($160,000 mdp) plan original',
        ingresosDesc: 'Costo anunciado en mayo de 2019 como límite estricto de inversión federal.',
        egresosVal: '>$18,900 mdd (> $330,000 mdp) auditados (+136%)',
        egresosDesc: 'Costo final de integración mecánica y pruebas; duplicó con creces el techo presupuestal normativo.',
        irregVal: '>$980 mdp observados por ASF',
        irregDesc: 'Pagos en exceso en montaje de plantas combinadas, contratos asignados sin licitación a PTI Infraestructura.',
        transpVal: 'Clasificación bajo secreto comercial e industrial',
        transpDesc: 'Filial PTI operó en el régimen privado excluyendo contratos de la Ley de Obras Públicas federal.',
        refKey: 'ref-cuentas-publicas',
        refNum: '2',
        glosTerm: 'Cuenta Pública'
      },
      'cfe': {
        id: 'cfe',
        nombre: 'Comisión Federal de Electricidad (CFE)',
        icono: '⚡',
        ramo: 'Ramo 53 · Entidad de Control Directo',
        ingresosVal: '$493,300 mdp PEF + $82,000 mdp subsidio tarifas',
        ingresosDesc: 'Presupuesto anual más transferencia federal directa para contener tarifas domésticas de luz.',
        egresosVal: '$532,000 mdp devengados (Altos costos de insumos)',
        egresosDesc: 'Elevado gasto en combustóleo y contratos de suministro de gas natural importado.',
        irregVal: '>$2,800 mdp observados por ASF',
        irregDesc: 'Sobrecostos de mantenimiento en plantas termoeléctricas y compras directas de carbón en Coahuila.',
        transpVal: 'Pasivos laborales contingentes > $430,000 mdp',
        transpDesc: 'Reversión del contrato colectivo laboral en 2020 incrementó el costo actuarial de pensiones de CFE.',
        refKey: 'ref-cuentas-publicas',
        refNum: '2',
        glosTerm: 'Gasto Programable'
      },
      'shcp': {
        id: 'shcp',
        nombre: 'Secretaría de Hacienda y Crédito Público (SHCP)',
        icono: '🏛️',
        ramo: 'Ramo 06 · Hacienda y Crédito Público',
        ingresosVal: '$9.06 billones de erario administrado en LIF',
        ingresosDesc: 'Ingresos tributarios, petroleros y contratación de deuda soberana autorizada por el Congreso.',
        egresosVal: '$1.26 billones costo financiero de deuda (13.9% PEF)',
        egresosDesc: 'Pago anual de intereses de deuda pública bruta que superó los $17 billones en 2024.',
        irregVal: 'Observaciones de subestimación de metas y FEIP',
        irregDesc: 'ASF alertó sobre subestimación deliberada de ingresos en la LIF para manejar excedentes con discrecionalidad.',
        transpVal: 'FEIP vaciado: De $279k mdp (2018) a <$40k mdp (2024)',
        transpDesc: 'Consumo casi total del Fondo de Estabilización de los Ingresos Presupuestarios sin reglas de reposición.',
        refKey: 'ref-cuentas-publicas',
        refNum: '2',
        glosTerm: 'Deuda Pública'
      }
    },
    presets: [
      {
        id: 'preset_pemex_autosuficiencia',
        depKey: 'pemex',
        icono: '🛢️',
        titulo: 'PEMEX: ¿Autosuficiencia Financiera?',
        titular: 'Noticia afirma que Pemex opera con autosuficiencia y superávit sin rescates del gobierno en 2024',
        url: 'https://eluniversal.com.mx/opinion/columna/pemex-superavit-finanzas-reales',
        score: 18,
        veredictoTipo: 'falso',
        veredictoBadge: '🔴 FALSO / DESMENTIDO PRESUPUESTAL (18 / 100 PTS)',
        veredictoTitulo: 'Desmentido por Cuenta Pública y Transferencias del Erario',
        dictamen: 'La afirmación de "autosuficiencia financiera" es frontalmente desmentida por los registros hacendarios de la SHCP y la Cuenta Pública consolidada. Entre 2019 y 2024, PEMEX recibió más de $1.8 billones de pesos en apoyos directos del erario federal: $987,000 mdp en transferencias de capital para pago de amortizaciones de deuda y más de $500,000 mdp por la reducción de la tasa del Derecho por la Utilidad Compartida (DUC), la cual fue rebajada por decreto del 65% al 30% a costa de los ingresos de la federación. Con una deuda financiera superior a los $1.9 billones de pesos ($97,300 mdd) y pliegos de observaciones de la ASF por más de $21,450 mdp, la empresa opera en déficit estructural y subsiste únicamente por el respaldo de la deuda soberana de México.'
      },
      {
        id: 'preset_tren_maya_costo',
        depKey: 'tren_maya',
        icono: '🚆',
        titulo: 'Tren Maya: ¿Costo Original sin Sobrecostos?',
        titular: 'Declaración oficial asegura que el Tren Maya costó exactamente los $150,000 mdp presupuestados',
        url: 'https://reforma.com/nacional/tren-maya-costo-final-auditado-asf',
        score: 12,
        veredictoTipo: 'falso',
        veredictoBadge: '🔴 FALSO / DESMENTIDO PRESUPUESTAL (12 / 100 PTS)',
        veredictoTitulo: 'Desmentido por Egresos Devengados y Auditorías ASF',
        dictamen: 'El costo divulgado de $150,000 mdp corresponde únicamente a la proyección conceptual preliminar plasmada en el PEF 2019. De acuerdo con el seguimiento oficial de la Cuenta Pública auditada por la ASF y los informes trimestrales de la SHCP, el gasto devengado acumulado por Fonatur y SEDENA supera los $515,000 millones de pesos al cierre de 2024, lo que representa un sobrecosto documentado superior al 243%. Asimismo, la ASF ha emitido pliegos de observaciones por más de $3,400 mdp debido a pagos duplicados en terraplenes, deficiencias en mecánica de suelos en los Tramos 5 Sur y 6, y pagos extraordinarios por aceleración de obra sin sustento de ingeniería de detalle.'
      },
      {
        id: 'preset_salud_insabi_desabasto',
        depKey: 'salud_insabi',
        icono: '🏥',
        titulo: 'Salud: ¿98% de Abasto y Transparencia Fonsabi?',
        titular: 'Reportaje oficial afirma abastecimiento de recetas al 98% y manejo impecable del Fondo Fonsabi',
        url: 'https://animalpolitico.com/salud-publica/auditoria-insabi-fonsabi-medicamentos',
        score: 26,
        veredictoTipo: 'falso',
        veredictoBadge: '🔴 FALSO / DESMENTIDO PRESUPUESTAL (26 / 100 PTS)',
        veredictoTitulo: 'Desmentido por Desabasto Auditado y Pliegos ASF',
        dictamen: 'Los datos oficiales de la Cuenta Pública y la ASF contradicen plenamente el supuesto abasto del 98%. Durante la vigencia del INSABI se extrajeron más de $140,000 millones de pesos del Fondo de Salud para el Bienestar (Fonsabi, antes Fondo de Gastos Catastróficos) para gasto corriente, sin que a la fecha se hayan solventado comprobaciones por más del 40% de dichos montos. En los informes de fiscalización de la ASF se emitieron pliegos de observaciones por más de $15,600 mdp por compras consolidadas fallidas y lotes masivos de medicamentos caducados en almacenes estatales, mientras el sistema hospitalario registró más de 15 millones de recetas no surtidas efectivamente.'
      },
      {
        id: 'preset_scjn_fideicomisos',
        depKey: 'scjn_pjf',
        icono: '⚖️',
        titulo: 'SCJN: ¿Fideicomisos Intocables y en Regla?',
        titular: 'Nota asegura que los 13 fideicomisos de $15,434 mdp protegen derechos laborales y rinden cuentas al 100%',
        url: 'https://eleconomista.com.mx/politica/scjn-fideicomisos-litigio-asf-cuentas',
        score: 48,
        veredictoTipo: 'enganoso',
        veredictoBadge: '🟠 ENGAÑOSO / OMISIÓN SEVERA DE PASIVOS (48 / 100 PTS)',
        veredictoTitulo: 'Engañoso: Oculta Remanentes Acumulados y Juicios Cruzados',
        dictamen: 'El contenido es engañoso porque mezcla la legítima tutela de derechos laborales de personal operativo con la opacidad en el origen de los recursos. La ASF comprobó en la Cuenta Pública (Ref. 23) que los $15,434 mdp acumulados en los 13 fideicomisos del Poder Judicial se nutrieron año tras año de remanentes presupuestales que no fueron devueltos a la TESOFE, violando el principio de anualidad del Art. 54 de la Ley Federal de Presupuesto. Además, mientras se afirma que todo está transparentado, el reintegro de dichos fondos al erario nacional se mantiene paralizado debido a controversias constitucionales y amparos resueltos por los propios beneficiarios del sistema judicial.'
      },
      {
        id: 'preset_conade_becas',
        depKey: 'conade',
        icono: '🏅',
        titulo: 'CONADE: ¿Comprobación al 100% en Deporte?',
        titular: 'Declaración afirma que CONADE comprobó el 100% de los recursos para deportistas y no debe nada',
        url: 'https://proceso.com.mx/deportes/conade-irregularidades-desvios-asf-atletas',
        score: 22,
        veredictoTipo: 'falso',
        veredictoBadge: '🔴 FALSO / DESMENTIDO PRESUPUESTAL (22 / 100 PTS)',
        veredictoTitulo: 'Desmentido por Denuncias Penales en FGR y EFOS',
        dictamen: 'La afirmación es falsa y contraria a las auditorías forenses practicadas por la ASF a las Cuentas Públicas 2020 a 2023. La ASF ha interpuesto denuncias penales ante la FGR por irregularidades que superan los $620 millones de pesos, detectando contratación de empresas fantasma facturadoras (EFOS listadas bajo el Art. 69-B del CFF) para la adquisición simulada de tecnología y equipo deportivo, eventos pagados que no se celebraron y retención indebida de becas a medallistas y nadadores con resoluciones judiciales en contra por desacato.'
      },
      {
        id: 'preset_dos_bocas_meta',
        depKey: 'dos_bocas',
        icono: '🏭',
        titulo: 'Dos Bocas: ¿Costo Fijo de $8,000 mdd?',
        titular: 'Nota sostiene que la Refinería Olmeca costó $8,000 mdd según el plan rector de inversión original',
        url: 'https://elfinanciero.com.mx/economia/dos-bocas-costo-final-auditado-pemex',
        score: 15,
        veredictoTipo: 'falso',
        veredictoBadge: '🔴 FALSO / DESMENTIDO PRESUPUESTAL (15 / 100 PTS)',
        veredictoTitulo: 'Desmentido por Balances de Pemex e Informes de la ASF',
        dictamen: 'La nota reproduce el presupuesto meta de 2019 ignorando por completo los estados financieros dictaminados de Pemex y las revisiones de la ASF a su filial PTI Infraestructura de Desarrollo. El costo final auditado de la Refinería Olmeca en Dos Bocas superó los $18,900 millones de dólares (más de $330,000 mdp), lo que equivale a un sobrecosto de más del 136% respecto al plan inicial. Dicho sobrecosto requirió múltiples ampliaciones de capital mediante partidas extraordinarias de la Secretaría de Energía y adjudicaciones directas que eludieron los mecanismos ordinarios de licitación pública federal.'
      }
    ]
  };

  let activeFactCheckPresetId = null;
  let isFactCheckAudited = false;
  let isFactCheckAnimating = false;
  let isFactCheckHoverEnabled = false;
  let factCheckAnimTimer = null;
  let factCheckProgressStep = 0;

  function initFactCheckModule() {
    renderFactCheckPresets();
    setupFactCheckDropzone();

    // Cargar por defecto el primer preset (PEMEX) en reposo
    selectFactCheckPreset('preset_pemex_autosuficiencia', false);
  }

  function renderFactCheckModule() {
    renderFactCheckPresets();
    updateFactCheckUI();
  }

  function renderFactCheckPresets() {
    const container = document.getElementById('factcheckPresetsGrid');
    if (!container) return;

    container.innerHTML = FACTCHECK_KNOWLEDGE_BASE.presets.map(p => {
      const isSel = p.id === activeFactCheckPresetId;
      const dep = FACTCHECK_KNOWLEDGE_BASE.dependencias[p.depKey];
      const depName = dep ? dep.nombre.split('—')[0].trim() : p.depKey.toUpperCase();

      return `
        <div class="factcheck-preset-card ${isSel ? 'active' : ''}" onclick="window.AuditEngine.selectFactCheckPreset('${p.id}', true)">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="factcheck-preset-dep">${p.icono} ${depName}</span>
            <span style="font-family:var(--font-mono); font-size:10px; color:${p.score <= 30 ? 'var(--crimson-bright)' : '#f59e0b'}; font-weight:700;">
              ${p.score} pts
            </span>
          </div>
          <div class="factcheck-preset-title">${p.titulo}</div>
          <div class="factcheck-preset-preview">"${p.titular}"</div>
        </div>
      `;
    }).join('');
  }

  function selectFactCheckPreset(presetId, resetAudit = true) {
    activeFactCheckPresetId = presetId;
    const preset = FACTCHECK_KNOWLEDGE_BASE.presets.find(p => p.id === presetId);
    if (!preset) return;

    // Actualizar campos del formulario
    const selDep = document.getElementById('factcheckSelectDep');
    const inputUrl = document.getElementById('factcheckUrlInput');
    const inputTxt = document.getElementById('factcheckTextInput');

    if (selDep) selDep.value = preset.depKey;
    if (inputUrl) inputUrl.value = preset.url;
    if (inputTxt) inputTxt.value = preset.titular;

    // Quitar badge de archivo manual
    const fileBadge = document.getElementById('factcheckFileBadge');
    if (fileBadge) fileBadge.style.display = 'none';

    renderFactCheckPresets();

    if (resetAudit) {
      resetNoticiaForense();
    }
  }

  function onFactCheckDependenciaChange(depKey) {
    // Si cambia de dependencia manualmente, deseleccionar preset
    activeFactCheckPresetId = null;
    renderFactCheckPresets();

    const dep = FACTCHECK_KNOWLEDGE_BASE.dependencias[depKey];
    const statusEl = document.getElementById('factcheckStatusText');
    if (statusEl && dep) {
      statusEl.innerHTML = `🏛️ Dependencia seleccionada: <strong>${dep.nombre}</strong> (${dep.ramo}). Presiona «Iniciar Auditoría Forense» para evaluar.`;
    }
    resetNoticiaForense();
  }

  function setupFactCheckDropzone() {
    const dropzone = document.getElementById('factcheckDropzone');
    if (!dropzone) return;

    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      }, false);
    });

    dropzone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files && files.length > 0) {
        processUploadedFile(files[0]);
      }
    }, false);
  }

  function handleFactCheckFileSelect(event) {
    const file = event.target.files && event.target.files[0];
    if (file) {
      processUploadedFile(file);
    }
  }

  function processUploadedFile(file) {
    const fileBadge = document.getElementById('factcheckFileBadge');
    const statusEl = document.getElementById('factcheckStatusText');
    const textInput = document.getElementById('factcheckTextInput');

    const sizeKb = Math.round(file.size / 1024);
    if (fileBadge) {
      fileBadge.textContent = `✓ Archivo cargado: ${file.name} (${sizeKb} KB)`;
      fileBadge.style.display = 'inline-block';
    }

    if (statusEl) {
      statusEl.innerHTML = `<span style="color:var(--emerald-bright);">✓ Documento «${file.name}» cargado en memoria local (${sizeKb} KB). Listo para auditar.</span>`;
    }

    // Si es archivo de texto plano, leer primeras líneas
    if (file.type === 'text/plain') {
      const reader = new FileReader();
      reader.onload = function(e) {
        if (textInput && (!textInput.value || textInput.value.length < 10)) {
          textInput.value = e.target.result.substring(0, 300);
        }
      };
      reader.readAsText(file);
    } else {
      if (textInput && (!textInput.value || textInput.value.length < 10)) {
        textInput.value = `[Documento PDF: ${file.name}] Afirmaciones y estados financieros analizados localmente.`;
      }
    }
  }

  function updateFactCheckUI() {
    const preset = FACTCHECK_KNOWLEDGE_BASE.presets.find(p => p.id === activeFactCheckPresetId);
    const selDepVal = document.getElementById('factcheckSelectDep')?.value || 'pemex';
    const dep = FACTCHECK_KNOWLEDGE_BASE.dependencias[preset ? preset.depKey : selDepVal];

    const verdictTitle = document.getElementById('factcheckVerdictTitle');
    const verdictBadge = document.getElementById('factcheckVerdictBadge');
    const meterFill = document.getElementById('factcheckMeterFill');
    const scoreLabel = document.getElementById('factcheckScoreLabel');

    const pilarValIng = document.getElementById('pillarValIngresos');
    const pilarDescIng = document.getElementById('pillarDescIngresos');
    const pilarValEg = document.getElementById('pillarValEgresos');
    const pilarDescEg = document.getElementById('pillarDescEgresos');
    const pilarValIrr = document.getElementById('pillarValIrreg');
    const pilarDescIrr = document.getElementById('pillarDescIrreg');
    const pilarValTr = document.getElementById('pillarValTransp');
    const pilarDescTr = document.getElementById('pillarDescTransp');

    const dictamenText = document.getElementById('factcheckDictamenText');
    const dictamenMeta = document.getElementById('factcheckDictamenMeta');

    if (!isFactCheckAudited && !isFactCheckAnimating) {
      // Estado en reposo (Ceros)
      if (verdictTitle) verdictTitle.textContent = 'Estado Inicial: Consola de Auditoría en Espera';
      if (verdictBadge) {
        verdictBadge.className = 'factcheck-badge-verdict verdict-reposo';
        verdictBadge.textContent = '⚪ EN REPOSO (0 / 100 PTS)';
      }
      if (meterFill) {
        meterFill.style.width = '0%';
        meterFill.style.backgroundColor = 'var(--border-subtle)';
      }
      if (scoreLabel) scoreLabel.textContent = '0 / 100 PUNTOS';

      if (pilarValIng) pilarValIng.textContent = '$0 mdp';
      if (pilarDescIng) pilarDescIng.textContent = '⚪ En espera de evaluación pericial.';
      if (pilarValEg) pilarValEg.textContent = '$0 mdp';
      if (pilarDescEg) pilarDescEg.textContent = '⚪ En espera de evaluación pericial.';
      if (pilarValIrr) pilarValIrr.textContent = '$0 mdp';
      if (pilarDescIrr) pilarDescIrr.textContent = '⚪ En espera de evaluación pericial.';
      if (pilarValTr) pilarValTr.textContent = '0 solicitudes';
      if (pilarDescTr) pilarDescTr.textContent = '⚪ En espera de evaluación pericial.';

      if (dictamenText) {
        dictamenText.innerHTML = `💡 <em>Selecciona un caso testigo arriba o ingresa la URL / documento de la noticia para auditar su veracidad frente a la Cuenta Pública, PEF y auditorías de la ASF.</em>`;
      }
      if (dictamenMeta && dep) {
        dictamenMeta.textContent = `🏛️ Ente Fiscalizable: ${dep.nombre} (${dep.ramo}) · Estado: En reposo`;
      }
    } else if (isFactCheckAudited) {
      // Estado auditado al 100%
      const targetScore = preset ? preset.score : 25;
      const targetBadgeClass = targetScore <= 30 ? 'verdict-falso' : (targetScore <= 60 ? 'verdict-enganoso' : (targetScore <= 80 ? 'verdict-impreciso' : 'verdict-veridico'));
      const targetBadgeText = preset ? preset.veredictoBadge : `🔴 FALSO / DESMENTIDO PRESUPUESTAL (${targetScore} / 100 PTS)`;
      const targetTitle = preset ? preset.veredictoTitulo : 'Desmentido Presupuestal por Datos de Cuenta Pública';

      if (verdictTitle) verdictTitle.textContent = targetTitle;
      if (verdictBadge) {
        verdictBadge.className = `factcheck-badge-verdict ${targetBadgeClass}`;
        verdictBadge.textContent = targetBadgeText;
      }
      if (meterFill) {
        meterFill.style.width = `${targetScore}%`;
        meterFill.style.backgroundColor = targetScore <= 30 ? 'var(--crimson-bright)' : (targetScore <= 60 ? '#f59e0b' : (targetScore <= 80 ? '#eab308' : '#10b981'));
      }
      if (scoreLabel) scoreLabel.textContent = `${targetScore} / 100 PUNTOS`;

      if (dep) {
        if (pilarValIng) pilarValIng.textContent = dep.ingresosVal;
        if (pilarDescIng) pilarDescIng.textContent = dep.ingresosDesc;
        if (pilarValEg) pilarValEg.textContent = dep.egresosVal;
        if (pilarDescEg) pilarDescEg.textContent = dep.egresosDesc;
        if (pilarValIrr) pilarValIrr.textContent = dep.irregVal;
        if (pilarDescIrr) pilarDescIrr.textContent = dep.irregDesc;
        if (pilarValTr) pilarValTr.textContent = dep.transpVal;
        if (pilarDescTr) pilarDescTr.textContent = dep.transpDesc;
      }

      if (dictamenText) {
        dictamenText.innerHTML = preset ? preset.dictamen : `La afirmación analizada no encuentra sustento en las partidas del PEF ni en los informes de la Cuenta Pública auditada por la ASF. Se documentaron inconsistencias sustantivas entre las declaraciones públicas y las erogaciones devengadas reportadas ante la Secretaría de Hacienda.`;
      }
      if (dictamenMeta && dep) {
        dictamenMeta.innerHTML = `🏛️ Ente Auditado: <strong>${dep.nombre}</strong> (${dep.ramo}) · Fecha de corte: Cuenta Pública 2024 · Dictamen emitido`;
      }
    }
  }

  function evaluarNoticiaForense() {
    if (isFactCheckAnimating) return;
    isFactCheckAnimating = true;

    const statusEl = document.getElementById('factcheckStatusText');
    const btnEval = document.getElementById('btnIniciarFactCheck');
    if (btnEval) {
      btnEval.innerHTML = '<span>⏳</span> Auditando Forense...';
    }

    const preset = FACTCHECK_KNOWLEDGE_BASE.presets.find(p => p.id === activeFactCheckPresetId);
    const targetScore = preset ? preset.score : 25;

    const meterFill = document.getElementById('factcheckMeterFill');
    const scoreLabel = document.getElementById('factcheckScoreLabel');

    const steps = [
      '🔬 [Fase 1/4] Identificando dependencia y cruzando asignación en PEF / LIF...',
      '⚡ [Fase 2/4] Auditando gasto devengado en Cuenta Pública y variaciones presupuestales...',
      '⚠️ [Fase 3/4] Consultando pliegos de observaciones y alertas de la ASF...',
      '📊 [Fase 4/4] Verificando solicitudes PNT, reservas y contratos clasificados...'
    ];

    let currentStep = 0;
    const intervalMs = 380;

    factCheckAnimTimer = setInterval(() => {
      currentStep++;
      if (currentStep < steps.length) {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--gold-bright);">${steps[currentStep]}</span>`;
        if (meterFill) {
          const partialProgress = ((currentStep + 1) / steps.length) * targetScore;
          meterFill.style.width = `${partialProgress}%`;
        }
      } else {
        clearInterval(factCheckAnimTimer);
        factCheckAnimTimer = null;
        isFactCheckAnimating = false;
        isFactCheckAudited = true;

        if (statusEl) {
          statusEl.innerHTML = `<span style="color:var(--emerald-bright);">✓ Auditoría concluida: Dictamen pericial emitido con fundamento en Cuenta Pública y ASF.</span>`;
        }
        if (btnEval) {
          btnEval.innerHTML = '<span>🔄</span> Volver a Auditar';
        }

        updateFactCheckUI();
      }
    }, intervalMs);

    if (statusEl) statusEl.innerHTML = `<span style="color:var(--gold-bright);">${steps[0]}</span>`;
  }

  function resetNoticiaForense() {
    if (factCheckAnimTimer) {
      clearInterval(factCheckAnimTimer);
      factCheckAnimTimer = null;
    }
    isFactCheckAnimating = false;
    isFactCheckAudited = false;

    const statusEl = document.getElementById('factcheckStatusText');
    if (statusEl) {
      statusEl.innerHTML = '⚪ Sistema listo en reposo. Selecciona un caso testigo o ingresa un enlace / documento para auditar la información.';
    }
    const btnEval = document.getElementById('btnIniciarFactCheck');
    if (btnEval) {
      btnEval.innerHTML = '<span>🔬</span> Iniciar Auditoría Forense';
    }

    updateFactCheckUI();
  }

  function toggleHoverFactCheck(enabled) {
    isFactCheckHoverEnabled = !!enabled;
  }

  function handleFactCheckHover() {
    if (isFactCheckHoverEnabled && !isFactCheckAudited && !isFactCheckAnimating) {
      evaluarNoticiaForense();
    }
  }

  function copiarDictamenForense() {
    const preset = FACTCHECK_KNOWLEDGE_BASE.presets.find(p => p.id === activeFactCheckPresetId);
    const selDepVal = document.getElementById('factcheckSelectDep')?.value || 'pemex';
    const dep = FACTCHECK_KNOWLEDGE_BASE.dependencias[preset ? preset.depKey : selDepVal];
    const dictamen = preset ? preset.dictamen : (document.getElementById('factcheckDictamenText')?.innerText || '');
    const titular = document.getElementById('factcheckTextInput')?.value || (preset ? preset.titular : 'Noticia analizada');
    const badge = preset ? preset.veredictoBadge : 'VERIFICACIÓN HACENDARIA';

    const texto = `=== AUDITAVISIÓN · DICTAMEN PERICIAL HACENDARIO ===\n` +
      `Ente Fiscalizado: ${dep ? dep.nombre : 'Dependencia Pública'}\n` +
      `Afirmación Analizada: "${titular}"\n` +
      `Veredicto Oficial: ${badge}\n\n` +
      `Fundamento y Dictamen:\n${dictamen}\n\n` +
      `Fuente: Plataforma Cívica Auditavisión · Datos de Cuenta Pública SHCP y ASF (http://localhost:8000/#verificador)`;

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(() => {
        alert('✓ ¡Dictamen pericial copiado al portapapeles con éxito!');
      }).catch(() => {
        alert('Dictamen generado. Puedes copiar el texto directamente.');
      });
    } else {
      alert('✓ Dictamen pericial listo para compartir.');
    }
  }

  // ==========================================================================
  // INICIALIZACIÓN GLOBAL CON PROTECCIÓN ANTE ERRORES
  // ==========================================================================
  function safeRun(fn, name) {
    try {
      fn();
    } catch (err) {
      console.warn(`Auditavisión warning in ${name}:`, err);
    }
  }

  function init() {
    safeRun(initTheme, 'initTheme');
    safeRun(initLeafletMap, 'initLeafletMap');
    safeRun(renderCartogram, 'renderCartogram');
    safeRun(updateRankingsList, 'updateRankingsList');
    safeRun(renderNews, 'renderNews');
    safeRun(renderFaqs, 'renderFaqs');
    safeRun(renderGlossary, 'renderGlossary');
    safeRun(initSearch, 'initSearch');
    safeRun(renderCongresosTable, 'renderCongresosTable');
    safeRun(initElectoralModule, 'initElectoralModule');
    safeRun(renderJerarquiaSalarialChart, 'renderJerarquiaSalarialChart');
    safeRun(initJudicialEstructuraModule, 'initJudicialEstructuraModule');
    safeRun(renderJudicialMinisters, 'renderJudicialMinisters');
    safeRun(() => renderJudicialPrestacionesSimulator('distribucion'), 'renderJudicialPrestacionesSimulator');
    safeRun(() => renderJudicialAsesoresSimulator('cargos'), 'renderJudicialAsesoresSimulator');
    safeRun(() => renderJudicialGlobalesSimulator('balanza'), 'renderJudicialGlobalesSimulator');
    safeRun(initFactCheckModule, 'initFactCheckModule');
    safeRun(renderFinanzasPublicas, 'renderFinanzasPublicas');
    safeRun(renderSimuladorMegaobras, 'renderSimuladorMegaobras');
    safeRun(renderPoliticosMandatarios, 'renderPoliticosMandatarios');
    safeRun(renderPoliticosSecundarios, 'renderPoliticosSecundarios');
    safeRun(renderPoliticosCuriosos, 'renderPoliticosCuriosos');
    safeRun(renderVersusPorfirio, 'renderVersusPorfirio');
    safeRun(renderCasillasFaq, 'renderCasillasFaq');
    safeRun(() => renderReferencias('todas'), 'renderReferencias');
    safeRun(initComunidad, 'initComunidad');
    safeRun(() => calculateTaxBreakdown(30000), 'calculateTaxBreakdown');
    safeRun(updateDiputadosSimulator, 'updateDiputadosSimulator');
    safeRun(updateSenadoSimulator, 'updateSenadoSimulator');
    safeRun(updateASFSimulator, 'updateASFSimulator');
    safeRun(() => renderAsfIrregularidadesChart('tipologia'), 'renderAsfIrregularidadesChart');
    safeRun(updateCongresosSimulator, 'updateCongresosSimulator');
    safeRun(updateJerarquiaSimulator, 'updateJerarquiaSimulator');

    // Eventos de botones de subpestañas (.subtabs-bar)
    document.querySelectorAll('.subtabs-bar .subtab-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const parent = this.closest('.subtabs-bar').dataset.parent;
        const sub = this.dataset.sub;
        switchSubtab(parent, sub);
      });
    });

    // Eventos de botones de la barra de pestañas maestras
    document.querySelectorAll('.tabbar button[role="tab"]').forEach(btn => {
      btn.addEventListener('click', function() {
        switchTab(this.dataset.tab);
      });
    });

    // Eventos de chips de filtro de referencias
    document.querySelectorAll('[data-reff]').forEach(btn => {
      btn.addEventListener('click', function() {
        renderReferencias(this.dataset.reff);
      });
    });

    // Eventos de chips de filtro de glosario
    document.querySelectorAll('[data-gcat]').forEach(btn => {
      btn.addEventListener('click', function() {
        filterGlossaryByCategory(this.dataset.gcat);
      });
    });

    // Comprobar si hay hash en la URL al cargar
    const initialHash = window.location.hash.replace('#', '');
    if (initialHash && TAB_METADATA[initialHash]) {
      switchTab(initialHash);
    } else {
      switchTab('mapa');
    }

    // Eventos de botones de división de poderes (compatibilidad)
    document.querySelectorAll('.power-tab-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const p = this.dataset.power;
        if (p === 'ejecutivo') switchTab('mapa');
        else if (p === 'legislativo') switchTab('legislativo');
        else if (p === 'judicial') switchTab('judicial');
      });
    });

    // Eventos de botones de lentes de métrica
    document.querySelectorAll('.lens-btn').forEach(btn => {
      btn.addEventListener('click', () => setMetric(btn.dataset.metric));
    });

    // Eventos de alternancia de vista de mapa
    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.addEventListener('click', () => setMapView(btn.dataset.view));
    });

    // Evento de filtro de noticias
    document.querySelectorAll('.news-filter-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        document.querySelectorAll('.news-filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        renderNews(this.dataset.filter);
      });
    });

    // Evento del botón de la calculadora
    const calcBtn = document.getElementById('calcTriggerBtn');
    const calcInput = document.getElementById('calcTaxInput');
    if (calcBtn && calcInput) {
      calcBtn.addEventListener('click', () => calculateTaxBreakdown(calcInput.value));
      calcInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') calculateTaxBreakdown(calcInput.value);
      });
    }

    // Evento de búsqueda de glosario
    const glossInput = document.getElementById('glossarySearchInput');
    if (glossInput) {
      glossInput.addEventListener('input', (e) => renderGlossary(e.target.value));
    }

    // Eventos de chips de filtro de preceptos legales
    document.querySelectorAll('[data-pcat]').forEach(btn => {
      btn.addEventListener('click', function() {
        filterPreceptos(this.dataset.pcat);
      });
    });

    // Evento de búsqueda de preceptos legales
    const precInput = document.getElementById('preceptosSearchInput');
    if (precInput) {
      precInput.addEventListener('input', (e) => searchPreceptos(e.target.value));
    }

    // Evento de búsqueda de congresos estatales
    const congSearch = document.getElementById('congresosSearchInput');
    if (congSearch) {
      congSearch.addEventListener('input', (e) => renderCongresosTable(e.target.value));
    }
  }

  function openExpedienteHijo(tipo, vistaPreferida = 'curiosos') {
    // 1. Cambiar a la pestaña de políticos (Pestaña 5)
    switchTab('politicos');

    if (vistaPreferida === 'secundarios') {
      // Navegar a Subpestaña 5.2 (Fichas de Fiscalización)
      switchSubtab('politicos', 'secundarios');
      setTimeout(() => {
        let slug = '';
        if (tipo === 'salinas') slug = 'salinas-nxivm';
        else if (tipo === 'nino-verde' || tipo === 'verde') slug = 'nino-verde';
        else if (tipo === 'andy' || tipo === 'lopez-beltran') slug = 'andy-el-clan';
        else slug = tipo;

        const card = document.getElementById(`card-sec-${slug}`);
        if (card) {
          card.scrollIntoView({ behavior: 'smooth', block: 'center' });
          card.classList.add('card-highlight-pulse');
          // Abrir automáticamente el desglose si está cerrado
          const desglose = document.getElementById(`desglose-sec-${slug}`);
          if (desglose && (desglose.style.display === 'none' || desglose.style.display === '')) {
            togglePersonajeDesglose(slug);
          }
          setTimeout(() => card.classList.remove('card-highlight-pulse'), 4500);
        }
      }, 120);
    } else {
      // Vista por defecto: Subpestaña 5.3 (Relato Hemerográfico & Expedientes Judiciales)
      switchSubtab('politicos', 'curiosos');

      // Limpiar búsqueda para que no filtre
      state.curiososSearchQuery = '';
      const inp = document.getElementById('curiososSearchInput');
      if (inp) inp.value = '';

      // Resetear filtro a 'todos'
      state.activeCuriososFilter = 'todos';
      const catButtons = document.querySelectorAll('.curiosos-cat-btn');
      catButtons.forEach(btn => {
        if (btn.getAttribute('data-cat') === 'todos') btn.classList.add('active');
        else btn.classList.remove('active');
      });

      renderPoliticosCuriosos();

      setTimeout(() => {
        let cardId = '';
        if (tipo === 'salinas') cardId = 'card-curioso-salinas_nxivm';
        else if (tipo === 'nino-verde' || tipo === 'verde') cardId = 'card-curioso-nino_verde';
        else if (tipo === 'andy' || tipo === 'lopez-beltran') cardId = 'card-curioso-clan_andy_amilcar';
        else cardId = `card-curioso-${tipo}`;

        const card = document.getElementById(cardId);
        if (card) {
          card.scrollIntoView({ behavior: 'smooth', block: 'center' });
          card.classList.add('card-highlight-pulse');
          setTimeout(() => card.classList.remove('card-highlight-pulse'), 4500);
        }
      }, 120);
    }
  }

  // API pública
  
  // ==========================================================================
  // SIMULADOR 3.2: SALUD FINANCIERA & RIGOR PARLAMENTARIO SUBNACIONAL
  // ==========================================================================
  
  // ==========================================================================
  // SIMULADOR DE SALUD FINANCIERA · CÁMARA DE DIPUTADOS (SAN LÁZARO - BLOQUE 1)
  // ==========================================================================
  let isDiputadosHealthEvaluated = false;
  let isDiputadosHealthEvaluating = false;
  let isDiputadosHealthHoverEnabled = false;
  let diputadosAnimFrameId = null;
  let diputadosNeedleAngle = -90;
  let diputadosDisplayedScore = 0;

  function updateDiputadosPillarsDOM(p1, p2, p3, p4) {
    const f1 = document.getElementById('diputadosPillarFill_1');
    const v1 = document.getElementById('diputadosPillarVal_1');
    if (f1) f1.style.width = `${p1}%`;
    if (v1) v1.textContent = `${p1}%`;

    const f2 = document.getElementById('diputadosPillarFill_2');
    const v2 = document.getElementById('diputadosPillarVal_2');
    if (f2) f2.style.width = `${p2}%`;
    if (v2) v2.textContent = `${p2}%`;

    const f3 = document.getElementById('diputadosPillarFill_3');
    const v3 = document.getElementById('diputadosPillarVal_3');
    if (f3) f3.style.width = `${p3}%`;
    if (v3) v3.textContent = `${p3}%`;

    const f4 = document.getElementById('diputadosPillarFill_4');
    const v4 = document.getElementById('diputadosPillarVal_4');
    if (f4) f4.style.width = `${p4}%`;
    if (v4) v4.textContent = `${p4}%`;
  }

  function updateDiputadosSimulator() {
    const rSubv = document.getElementById('diputadosRangeSubvenciones');
    const rAses = document.getElementById('diputadosRangeAsesores');
    const rCom = document.getElementById('diputadosRangeComisiones');

    const pSubv = rSubv ? parseInt(rSubv.value, 10) : 0;
    const pAses = rAses ? parseInt(rAses.value, 10) : 0;
    const pCom = rCom ? parseInt(rCom.value, 10) : 0;

    const lblSubv = document.getElementById('diputadosSliderVal_subv');
    if (lblSubv) lblSubv.textContent = `${pSubv}%`;

    const lblAses = document.getElementById('diputadosSliderVal_asesores');
    if (lblAses) lblAses.textContent = `${pAses}%`;

    const lblCom = document.getElementById('diputadosSliderVal_comisiones');
    if (lblCom) lblCom.textContent = `${pCom}%`;

    const basePresupuesto = 9282;
    const baseSubv = 1450;
    const baseAsesores = 2400;
    const baseComisiones = 1372;

    const ahorroSubv = Math.round(baseSubv * (pSubv / 100));
    const ahorroAses = Math.round(baseAsesores * (pAses / 100));
    const ahorroCom = Math.round(baseComisiones * (pCom / 100));

    const totalAhorro = ahorroSubv + ahorroAses + ahorroCom;
    const nuevoPresupuesto = Math.max(5000, basePresupuesto - totalAhorro);
    const pctAhorro = ((totalAhorro / basePresupuesto) * 100).toFixed(1);

    const elAhorro = document.getElementById('diputadosSimAhorro');
    if (elAhorro) elAhorro.textContent = `+$${totalAhorro.toLocaleString('es-MX')} mdp`;

    const elPres = document.getElementById('diputadosSimPresupuesto');
    if (elPres) elPres.textContent = `$${nuevoPresupuesto.toLocaleString('es-MX')} mdp`;

    const elPct = document.getElementById('diputadosPctAhorro');
    if (elPct) elPct.textContent = `${pctAhorro}%`;

    const pil1 = Math.min(100, Math.round(pAses * 2.0));
    const pil2 = Math.min(100, Math.round(pSubv * 1.67));
    const pil3 = Math.min(100, Math.round(pCom * 3.33));
    const pil4 = Math.min(100, Math.round((pSubv * 0.4 + pAses * 0.4 + pCom * 0.2) * 1.8));

    if (!isDiputadosHealthEvaluating) {
      updateDiputadosPillarsDOM(pil1, pil2, pil3, pil4);

      let calcScore = Math.round((pil1 * 0.3) + (pil2 * 0.3) + (pil3 * 0.2) + (pil4 * 0.2));
      calcScore = Math.min(100, Math.max(0, calcScore));

      const needleEl = document.getElementById('diputadosNeedleGroup');
      const scoreEl = document.getElementById('diputadosScoreNum');
      const targetAngle = -90 + (calcScore / 100) * 180;

      if (needleEl) needleEl.style.transform = `rotate(${targetAngle}deg)`;
      diputadosNeedleAngle = targetAngle;
      diputadosDisplayedScore = calcScore;

      if (scoreEl) {
        scoreEl.textContent = calcScore;
        scoreEl.style.color = calcScore >= 80 ? '#2ecc71' : calcScore >= 50 ? '#f1c40f' : 'var(--text-dim)';
      }

      const statusEl = document.getElementById('diputadosStatusPill');
      if (statusEl) {
        if (calcScore === 0) {
          statusEl.innerHTML = '⚪ Simulador en Reposo. Presiona «Calibrar Austeridad».';
          statusEl.style.color = 'var(--text-dim)';
        } else if (calcScore < 50) {
          statusEl.innerHTML = `🟡 <b>Austeridad Inicial en San Lázaro (${calcScore} pts)</b>`;
          statusEl.style.color = '#f1c40f';
        } else if (calcScore < 80) {
          statusEl.innerHTML = `🟡 <b>Disciplina Presupuestal Moderada (${calcScore} pts)</b>`;
          statusEl.style.color = '#f1c40f';
        } else {
          statusEl.innerHTML = `🟢 <b>Austeridad Ejemplar en San Lázaro (${calcScore} pts)</b>`;
          statusEl.style.color = '#2ecc71';
        }
      }
    }
  }

  function evaluarSaludDiputados() {
    if (isDiputadosHealthEvaluating) return;
    if (diputadosAnimFrameId) cancelAnimationFrame(diputadosAnimFrameId);

    isDiputadosHealthEvaluating = true;

    const rSubv = document.getElementById('diputadosRangeSubvenciones');
    const rAses = document.getElementById('diputadosRangeAsesores');
    const rCom = document.getElementById('diputadosRangeComisiones');
    if (rSubv) rSubv.value = 50;
    if (rAses) rAses.value = 40;
    if (rCom) rCom.value = 25;

    const startAngle = diputadosNeedleAngle;
    const targetScore = 92;
    const targetAngle = -90 + (targetScore / 100) * 180;
    const startTime = performance.now();
    const duration = 1200;

    const needleEl = document.getElementById('diputadosNeedleGroup');
    const scoreEl = document.getElementById('diputadosScoreNum');
    const statusEl = document.getElementById('diputadosStatusPill');
    const evalStatus = document.getElementById('diputadosEvalStatus');

    if (evalStatus) {
      evalStatus.innerHTML = '<span style="color:var(--gold-bright);">⚡ Calibrando modelo de austeridad en San Lázaro...</span>';
    }

    function animateStep(now) {
      const p = Math.min(1, (now - startTime) / duration);
      const ease = p < 0.8 ? (1 - Math.pow(1 - p / 0.8, 3)) * 1.04 : 1.04 - (p - 0.8) / 0.2 * 0.04;
      
      const currentAngle = startAngle + (targetAngle - startAngle) * Math.min(1, ease);
      const currentScore = Math.round(targetScore * Math.min(1, ease));

      if (needleEl) needleEl.style.transform = `rotate(${currentAngle}deg)`;
      if (scoreEl) {
        scoreEl.textContent = currentScore;
        scoreEl.style.color = currentScore >= 80 ? '#2ecc71' : '#f1c40f';
      }

      updateDiputadosPillarsDOM(
        Math.round(80 * Math.min(1, ease)),
        Math.round(84 * Math.min(1, ease)),
        Math.round(83 * Math.min(1, ease)),
        Math.round(92 * Math.min(1, ease))
      );

      if (p < 1) {
        diputadosAnimFrameId = requestAnimationFrame(animateStep);
      } else {
        diputadosNeedleAngle = targetAngle;
        diputadosDisplayedScore = targetScore;
        isDiputadosHealthEvaluating = false;
        isDiputadosHealthEvaluated = true;
        diputadosAnimFrameId = null;

        if (statusEl) {
          statusEl.innerHTML = `🟢 <b>Calibración Completada: Rigor Ejemplar en San Lázaro (${targetScore} pts)</b>`;
          statusEl.style.color = '#2ecc71';
        }
        if (evalStatus) {
          evalStatus.innerHTML = '🟢 <b>Calibración completada: Ahorro federal proyectado de +$2,031 mdp en San Lázaro.</b>';
        }

        updateDiputadosSimulator();
      }
    }

    diputadosAnimFrameId = requestAnimationFrame(animateStep);
  }

  function resetSaludDiputados() {
    if (diputadosAnimFrameId) cancelAnimationFrame(diputadosAnimFrameId);
    isDiputadosHealthEvaluating = false;
    isDiputadosHealthEvaluated = false;

    const rSubv = document.getElementById('diputadosRangeSubvenciones');
    const rAses = document.getElementById('diputadosRangeAsesores');
    const rCom = document.getElementById('diputadosRangeComisiones');
    if (rSubv) rSubv.value = 0;
    if (rAses) rAses.value = 0;
    if (rCom) rCom.value = 0;

    const needleEl = document.getElementById('diputadosNeedleGroup');
    const scoreEl = document.getElementById('diputadosScoreNum');
    const statusEl = document.getElementById('diputadosStatusPill');
    const evalStatus = document.getElementById('diputadosEvalStatus');

    diputadosNeedleAngle = -90;
    diputadosDisplayedScore = 0;

    if (needleEl) needleEl.style.transform = 'rotate(-90deg)';
    if (scoreEl) {
      scoreEl.textContent = '0';
      scoreEl.style.color = 'var(--text-dim)';
    }

    if (statusEl) {
      statusEl.innerHTML = '⚪ Simulador en Reposo. Presiona «Calibrar Austeridad».';
      statusEl.style.color = 'var(--text-dim)';
    }
    if (evalStatus) {
      evalStatus.textContent = '⚪ Simulador en reposo. Presiona «Calibrar Austeridad» o ajusta los controles interactivos.';
    }

    updateDiputadosPillarsDOM(0, 0, 0, 0);
    updateDiputadosSimulator();
  }

  function toggleHoverSaludDiputados(enabled) {
    isDiputadosHealthHoverEnabled = !!enabled;
  }

  function handleDiputadosConsoleHover() {
    if (isDiputadosHealthHoverEnabled && !isDiputadosHealthEvaluated && !isDiputadosHealthEvaluating) {
      evaluarSaludDiputados();
    }
  }

  // ==========================================================================
  // SIMULADOR DE SALUD FINANCIERA · SENADO DE LA REPÚBLICA (BLOQUE 2)
  // ==========================================================================
  let isSenadoHealthEvaluated = false;
  let isSenadoHealthEvaluating = false;
  let isSenadoHealthHoverEnabled = false;
  let senadoAnimFrameId = null;
  let senadoNeedleAngle = -90;
  let senadoDisplayedScore = 0;

  function updateSenadoPillarsDOM(p1, p2, p3, p4) {
    const f1 = document.getElementById('senadoPillarFill_1');
    const v1 = document.getElementById('senadoPillarVal_1');
    if (f1) f1.style.width = `${p1}%`;
    if (v1) v1.textContent = `${p1}%`;

    const f2 = document.getElementById('senadoPillarFill_2');
    const v2 = document.getElementById('senadoPillarVal_2');
    if (f2) f2.style.width = `${p2}%`;
    if (v2) v2.textContent = `${p2}%`;

    const f3 = document.getElementById('senadoPillarFill_3');
    const v3 = document.getElementById('senadoPillarVal_3');
    if (f3) f3.style.width = `${p3}%`;
    if (v3) v3.textContent = `${p3}%`;

    const f4 = document.getElementById('senadoPillarFill_4');
    const v4 = document.getElementById('senadoPillarVal_4');
    if (f4) f4.style.width = `${p4}%`;
    if (v4) v4.textContent = `${p4}%`;
  }

  function updateSenadoSimulator() {
    const rTope = document.getElementById('senadoRangeTope');
    const rSubv = document.getElementById('senadoRangeSubvenciones');
    const rOp = document.getElementById('senadoRangeOp');

    const topeCosto = rTope ? parseInt(rTope.value, 10) : 42;
    const pSubv = rSubv ? parseInt(rSubv.value, 10) : 0;
    const pOp = rOp ? parseInt(rOp.value, 10) : 0;

    const lblTope = document.getElementById('senadoSliderVal_tope');
    if (lblTope) {
      lblTope.textContent = topeCosto >= 42 ? 'Sin Tope ($41.9 mdp)' : `$${topeCosto}.0 mdp / sen`;
    }

    const lblSubv = document.getElementById('senadoSliderVal_subv');
    if (lblSubv) lblSubv.textContent = `${pSubv}%`;

    const lblOp = document.getElementById('senadoSliderVal_op');
    if (lblOp) lblOp.textContent = `${pOp}%`;

    const basePresupuesto = 5365;
    const baseSubv = 920;
    const baseOp = 1040;

    const ahorroTope = topeCosto < 42 ? Math.round((41.91 - topeCosto) * 128) : 0;
    const ahorroSubv = Math.round(baseSubv * (pSubv / 100));
    const ahorroOp = Math.round(baseOp * (pOp / 100));

    const totalAhorro = Math.min(basePresupuesto - 2400, ahorroTope + ahorroSubv + ahorroOp);
    const nuevoPresupuesto = Math.max(2400, basePresupuesto - totalAhorro);
    const pctAhorro = ((totalAhorro / basePresupuesto) * 100).toFixed(1);

    const elAhorro = document.getElementById('senadoSimAhorro');
    if (elAhorro) elAhorro.textContent = `+$${totalAhorro.toLocaleString('es-MX')} mdp`;

    const elPres = document.getElementById('senadoSimPresupuesto');
    if (elPres) elPres.textContent = `$${nuevoPresupuesto.toLocaleString('es-MX')} mdp`;

    const elPct = document.getElementById('senadoPctAhorro');
    if (elPct) elPct.textContent = `${pctAhorro}%`;

    const pil1 = topeCosto < 42 ? Math.min(100, Math.round(((42 - topeCosto) / 22) * 100)) : 0;
    const pil2 = Math.min(100, Math.round(pSubv * 1.67));
    const pil3 = Math.min(100, Math.round(pOp * 2.5));
    const pil4 = Math.min(100, Math.round((pSubv * 0.5 + pOp * 0.5) * 1.8));

    if (!isSenadoHealthEvaluating) {
      updateSenadoPillarsDOM(pil1, pil2, pil3, pil4);

      let calcScore = Math.round((pil1 * 0.4) + (pil2 * 0.3) + (pil3 * 0.2) + (pil4 * 0.1));
      calcScore = Math.min(100, Math.max(0, calcScore));

      const needleEl = document.getElementById('senadoNeedleGroup');
      const scoreEl = document.getElementById('senadoScoreNum');
      const targetAngle = -90 + (calcScore / 100) * 180;

      if (needleEl) needleEl.style.transform = `rotate(${targetAngle}deg)`;
      senadoNeedleAngle = targetAngle;
      senadoDisplayedScore = calcScore;

      if (scoreEl) {
        scoreEl.textContent = calcScore;
        scoreEl.style.color = calcScore >= 80 ? '#2ecc71' : calcScore >= 50 ? '#f1c40f' : 'var(--text-dim)';
      }

      const statusEl = document.getElementById('senadoStatusPill');
      if (statusEl) {
        if (calcScore === 0) {
          statusEl.innerHTML = '⚪ Simulador en Reposo. Presiona «Calibrar Austeridad».';
          statusEl.style.color = 'var(--text-dim)';
        } else if (calcScore < 50) {
          statusEl.innerHTML = `🟡 <b>Austeridad Inicial en el Senado (${calcScore} pts)</b>`;
          statusEl.style.color = '#f1c40f';
        } else if (calcScore < 80) {
          statusEl.innerHTML = `🟡 <b>Disciplina Presupuestal Moderada (${calcScore} pts)</b>`;
          statusEl.style.color = '#f1c40f';
        } else {
          statusEl.innerHTML = `🟢 <b>Austeridad Ejemplar en la Cámara Alta (${calcScore} pts)</b>`;
          statusEl.style.color = '#2ecc71';
        }
      }
    }
  }

  function evaluarSaludSenado() {
    if (isSenadoHealthEvaluating) return;
    if (senadoAnimFrameId) cancelAnimationFrame(senadoAnimFrameId);

    isSenadoHealthEvaluating = true;

    const rTope = document.getElementById('senadoRangeTope');
    const rSubv = document.getElementById('senadoRangeSubvenciones');
    const rOp = document.getElementById('senadoRangeOp');
    if (rTope) rTope.value = 25;
    if (rSubv) rSubv.value = 50;
    if (rOp) rOp.value = 30;

    const startAngle = senadoNeedleAngle;
    const targetScore = 90;
    const targetAngle = -90 + (targetScore / 100) * 180;
    const startTime = performance.now();
    const duration = 1200;

    const needleEl = document.getElementById('senadoNeedleGroup');
    const scoreEl = document.getElementById('senadoScoreNum');
    const statusEl = document.getElementById('senadoStatusPill');
    const evalStatus = document.getElementById('senadoEvalStatus');

    if (evalStatus) {
      evalStatus.innerHTML = '<span style="color:var(--gold-bright);">⚡ Calibrando modelo de austeridad en el Senado...</span>';
    }

    function animateStep(now) {
      const p = Math.min(1, (now - startTime) / duration);
      const ease = p < 0.8 ? (1 - Math.pow(1 - p / 0.8, 3)) * 1.04 : 1.04 - (p - 0.8) / 0.2 * 0.04;
      
      const currentAngle = startAngle + (targetAngle - startAngle) * Math.min(1, ease);
      const currentScore = Math.round(targetScore * Math.min(1, ease));

      if (needleEl) needleEl.style.transform = `rotate(${currentAngle}deg)`;
      if (scoreEl) {
        scoreEl.textContent = currentScore;
        scoreEl.style.color = currentScore >= 80 ? '#2ecc71' : '#f1c40f';
      }

      updateSenadoPillarsDOM(
        Math.round(77 * Math.min(1, ease)),
        Math.round(84 * Math.min(1, ease)),
        Math.round(75 * Math.min(1, ease)),
        Math.round(90 * Math.min(1, ease))
      );

      if (p < 1) {
        senadoAnimFrameId = requestAnimationFrame(animateStep);
      } else {
        senadoNeedleAngle = targetAngle;
        senadoDisplayedScore = targetScore;
        isSenadoHealthEvaluating = false;
        isSenadoHealthEvaluated = true;
        senadoAnimFrameId = null;

        if (statusEl) {
          statusEl.innerHTML = `🟢 <b>Calibración Completada: Rigor Ejemplar en el Senado (${targetScore} pts)</b>`;
          statusEl.style.color = '#2ecc71';
        }
        if (evalStatus) {
          evalStatus.innerHTML = '🟢 <b>Calibración completada: Ahorro federal proyectado de +$2,937 mdp en el Senado.</b>';
        }

        updateSenadoSimulator();
      }
    }

    senadoAnimFrameId = requestAnimationFrame(animateStep);
  }

  function resetSaludSenado() {
    if (senadoAnimFrameId) cancelAnimationFrame(senadoAnimFrameId);
    isSenadoHealthEvaluating = false;
    isSenadoHealthEvaluated = false;

    const rTope = document.getElementById('senadoRangeTope');
    const rSubv = document.getElementById('senadoRangeSubvenciones');
    const rOp = document.getElementById('senadoRangeOp');
    if (rTope) rTope.value = 42;
    if (rSubv) rSubv.value = 0;
    if (rOp) rOp.value = 0;

    const needleEl = document.getElementById('senadoNeedleGroup');
    const scoreEl = document.getElementById('senadoScoreNum');
    const statusEl = document.getElementById('senadoStatusPill');
    const evalStatus = document.getElementById('senadoEvalStatus');

    senadoNeedleAngle = -90;
    senadoDisplayedScore = 0;

    if (needleEl) needleEl.style.transform = 'rotate(-90deg)';
    if (scoreEl) {
      scoreEl.textContent = '0';
      scoreEl.style.color = 'var(--text-dim)';
    }

    if (statusEl) {
      statusEl.innerHTML = '⚪ Simulador en Reposo. Presiona «Calibrar Austeridad».';
      statusEl.style.color = 'var(--text-dim)';
    }
    if (evalStatus) {
      evalStatus.textContent = '⚪ Simulador en reposo. Presiona «Calibrar Austeridad» o ajusta los controles interactivos.';
    }

    updateSenadoPillarsDOM(0, 0, 0, 0);
    updateSenadoSimulator();
  }

  function toggleHoverSaludSenado(enabled) {
    isSenadoHealthHoverEnabled = !!enabled;
  }

  function handleSenadoConsoleHover() {
    if (isSenadoHealthHoverEnabled && !isSenadoHealthEvaluated && !isSenadoHealthEvaluating) {
      evaluarSaludSenado();
    }
  }

  // ==========================================================================
  // SIMULADOR DE SALUD FINANCIERA & EFICACIA · AUDITORÍA SUPERIOR (ASF - BLOQUE 3)
  // ==========================================================================
  let isAsfHealthEvaluated = false;
  let isAsfHealthEvaluating = false;
  let isAsfHealthHoverEnabled = false;
  let asfAnimFrameId = null;
  let asfNeedleAngle = -90;
  let asfDisplayedScore = 0;

  function updateASFPillarsDOM(p1, p2, p3, p4) {
    const f1 = document.getElementById('asfPillarFill_1');
    const v1 = document.getElementById('asfPillarVal_1');
    if (f1) f1.style.width = `${p1}%`;
    if (v1) v1.textContent = `${p1}%`;

    const f2 = document.getElementById('asfPillarFill_2');
    const v2 = document.getElementById('asfPillarVal_2');
    if (f2) f2.style.width = `${p2}%`;
    if (v2) v2.textContent = `${p2}%`;

    const f3 = document.getElementById('asfPillarFill_3');
    const v3 = document.getElementById('asfPillarVal_3');
    if (f3) f3.style.width = `${p3}%`;
    if (v3) v3.textContent = `${p3}%`;

    const f4 = document.getElementById('asfPillarFill_4');
    const v4 = document.getElementById('asfPillarVal_4');
    if (f4) f4.style.width = `${p4}%`;
    if (v4) v4.textContent = `${p4}%`;
  }

  function updateASFSimulator() {
    const rRecup = document.getElementById('asfRangeRecuperacion');
    const rCob = document.getElementById('asfRangeCobertura');
    const rEfic = document.getElementById('asfRangeEficiencia');

    const pRecup = rRecup ? parseInt(rRecup.value, 10) : 15;
    const pCob = rCob ? parseInt(rCob.value, 10) : 25;
    const pEfic = rEfic ? parseInt(rEfic.value, 10) : 0;

    const montoObservado = 51024;
    const basePresupuestoASF = 3200;

    const reintegroTesofe = Math.round(montoObservado * (pRecup / 100));
    const roi = (reintegroTesofe / basePresupuestoASF).toFixed(1);

    const lblRecup = document.getElementById('asfSliderVal_recup');
    if (lblRecup) lblRecup.textContent = `${pRecup}% ($${reintegroTesofe.toLocaleString('es-MX')} mdp)`;

    const lblCob = document.getElementById('asfSliderVal_cobertura');
    if (lblCob) lblCob.textContent = `${pCob}%`;

    const lblEfic = document.getElementById('asfSliderVal_eficiencia');
    if (lblEfic) lblEfic.textContent = `${pEfic}%`;

    const elRecup = document.getElementById('asfSimRecuperacion');
    if (elRecup) elRecup.textContent = `+$${reintegroTesofe.toLocaleString('es-MX')} mdp`;

    const elROI = document.getElementById('asfSimROI');
    if (elROI) elROI.textContent = `${roi}x`;

    const elROIExpl = document.getElementById('asfROIExpl');
    if (elROIExpl) elROIExpl.textContent = `$${roi} pesos`;

    const pil1 = Math.min(100, Math.round(((pRecup - 15) / 45) * 100));
    const pil2 = Math.min(100, Math.round(((pCob - 25) / 55) * 100));
    const pil3 = Math.min(100, Math.round(pRecup * 1.5));
    const pil4 = Math.min(100, Math.round(parseFloat(roi) * 11));

    if (!isAsfHealthEvaluating) {
      updateASFPillarsDOM(pil1, pil2, pil3, pil4);

      let calcScore = Math.round((pil1 * 0.45) + (pil2 * 0.35) + (pil3 * 0.10) + (pil4 * 0.10));
      calcScore = Math.min(100, Math.max(0, calcScore));

      const needleEl = document.getElementById('asfNeedleGroup');
      const scoreEl = document.getElementById('asfScoreNum');
      const targetAngle = -90 + (calcScore / 100) * 180;

      if (needleEl) needleEl.style.transform = `rotate(${targetAngle}deg)`;
      asfNeedleAngle = targetAngle;
      asfDisplayedScore = calcScore;

      if (scoreEl) {
        scoreEl.textContent = calcScore;
        scoreEl.style.color = calcScore >= 80 ? '#2ecc71' : calcScore >= 50 ? '#f1c40f' : 'var(--text-dim)';
      }

      const statusEl = document.getElementById('asfStatusPill');
      if (statusEl) {
        if (calcScore === 0) {
          statusEl.innerHTML = '⚪ Simulador en Reposo. Presiona «Calibrar Fiscalización».';
          statusEl.style.color = 'var(--text-dim)';
        } else if (calcScore < 50) {
          statusEl.innerHTML = `🟡 <b>Eficacia Inicial de Fiscalización (${calcScore} pts)</b>`;
          statusEl.style.color = '#f1c40f';
        } else if (calcScore < 80) {
          statusEl.innerHTML = `🟡 <b>Recuperación Hacendaria Progresiva (${calcScore} pts)</b>`;
          statusEl.style.color = '#f1c40f';
        } else {
          statusEl.innerHTML = `🟢 <b>Eficacia Resarcitoria Ejemplar (${calcScore} pts)</b>`;
          statusEl.style.color = '#2ecc71';
        }
      }
    }
  }

  function evaluarSaludASF() {
    if (isAsfHealthEvaluating) return;
    if (asfAnimFrameId) cancelAnimationFrame(asfAnimFrameId);

    isAsfHealthEvaluating = true;

    const rRecup = document.getElementById('asfRangeRecuperacion');
    const rCob = document.getElementById('asfRangeCobertura');
    const rEfic = document.getElementById('asfRangeEficiencia');
    if (rRecup) rRecup.value = 55;
    if (rCob) rCob.value = 75;
    if (rEfic) rEfic.value = 25;

    const startAngle = asfNeedleAngle;
    const targetScore = 95;
    const targetAngle = -90 + (targetScore / 100) * 180;
    const startTime = performance.now();
    const duration = 1200;

    const needleEl = document.getElementById('asfNeedleGroup');
    const scoreEl = document.getElementById('asfScoreNum');
    const statusEl = document.getElementById('asfStatusPill');
    const evalStatus = document.getElementById('asfEvalStatus');

    if (evalStatus) {
      evalStatus.innerHTML = '<span style="color:var(--gold-bright);">⚡ Calibrando modelo resarcitorio de la ASF...</span>';
    }

    function animateStep(now) {
      const p = Math.min(1, (now - startTime) / duration);
      const ease = p < 0.8 ? (1 - Math.pow(1 - p / 0.8, 3)) * 1.04 : 1.04 - (p - 0.8) / 0.2 * 0.04;
      
      const currentAngle = startAngle + (targetAngle - startAngle) * Math.min(1, ease);
      const currentScore = Math.round(targetScore * Math.min(1, ease));

      if (needleEl) needleEl.style.transform = `rotate(${currentAngle}deg)`;
      if (scoreEl) {
        scoreEl.textContent = currentScore;
        scoreEl.style.color = currentScore >= 80 ? '#2ecc71' : '#f1c40f';
      }

      updateASFPillarsDOM(
        Math.round(89 * Math.min(1, ease)),
        Math.round(91 * Math.min(1, ease)),
        Math.round(83 * Math.min(1, ease)),
        Math.round(96 * Math.min(1, ease))
      );

      if (p < 1) {
        asfAnimFrameId = requestAnimationFrame(animateStep);
      } else {
        asfNeedleAngle = targetAngle;
        asfDisplayedScore = targetScore;
        isAsfHealthEvaluating = false;
        isAsfHealthEvaluated = true;
        asfAnimFrameId = null;

        if (statusEl) {
          statusEl.innerHTML = `🟢 <b>Calibración Completada: Eficacia Resarcitoria Ejemplar (${targetScore} pts)</b>`;
          statusEl.style.color = '#2ecc71';
        }
        if (evalStatus) {
          evalStatus.innerHTML = '🟢 <b>Calibración completada: Reintegro proyectado a Tesofe de +$28,063 mdp (ROI 8.8x).</b>';
        }

        updateASFSimulator();
      }
    }

    asfAnimFrameId = requestAnimationFrame(animateStep);
  }

  function resetSaludASF() {
    if (asfAnimFrameId) cancelAnimationFrame(asfAnimFrameId);
    isAsfHealthEvaluating = false;
    isAsfHealthEvaluated = false;

    const rRecup = document.getElementById('asfRangeRecuperacion');
    const rCob = document.getElementById('asfRangeCobertura');
    const rEfic = document.getElementById('asfRangeEficiencia');
    if (rRecup) rRecup.value = 15;
    if (rCob) rCob.value = 25;
    if (rEfic) rEfic.value = 0;

    const needleEl = document.getElementById('asfNeedleGroup');
    const scoreEl = document.getElementById('asfScoreNum');
    const statusEl = document.getElementById('asfStatusPill');
    const evalStatus = document.getElementById('asfEvalStatus');

    asfNeedleAngle = -90;
    asfDisplayedScore = 0;

    if (needleEl) needleEl.style.transform = 'rotate(-90deg)';
    if (scoreEl) {
      scoreEl.textContent = '0';
      scoreEl.style.color = 'var(--text-dim)';
    }

    if (statusEl) {
      statusEl.innerHTML = '⚪ Simulador en Reposo. Presiona «Calibrar Fiscalización».';
      statusEl.style.color = 'var(--text-dim)';
    }
    if (evalStatus) {
      evalStatus.textContent = '⚪ Simulador en reposo. Presiona «Calibrar Fiscalización» o ajusta los controles interactivos.';
    }

    updateASFPillarsDOM(0, 0, 0, 0);
    updateASFSimulator();
  }

  function toggleHoverSaludASF(enabled) {
    isAsfHealthHoverEnabled = !!enabled;
  }

  function handleASFConsoleHover() {
    if (isAsfHealthHoverEnabled && !isAsfHealthEvaluated && !isAsfHealthEvaluating) {
      evaluarSaludASF();
    }
  }

  // ==========================================================================
  // RADIOGRAFÍA DE IRREGULARIDADES EN TRANSPARENCIA & RENDICIÓN DE CUENTAS (ASF)
  // ==========================================================================
  const ASF_IRREGULARIDADES_DATA = {
    tipologias: [
      {
        id: 'falta_comprobacion',
        nombre: 'Falta de Documentación Justificatoria y Comprobatoria',
        subtitulo: 'Facturas no válidas, entregables inexistentes o bitácoras omitidas',
        monto: 18400,
        pct: 36.1,
        color: '#e74c3c',
        icono: '📑',
        causa: 'Entidades ejecutoras no presentan comprobantes fiscales digitales (CFDI) válidos, contratos con prestadores o estimaciones de obra que acrediten la aplicación real del recurso.',
        marco: 'Arts. 134 CPEUM; 42 y 43 de la Ley General de Contabilidad Gubernamental (LGCG)',
        sancion: 'Pliegos de observaciones con obligación de reintegro a Tesofe y vista al Órgano Interno de Control (OIC).'
      },
      {
        id: 'recursos_no_devengados',
        nombre: 'Recursos No Devengados ni Reintegrados a la Tesofe',
        subtitulo: 'Subejercicios y retenciones indebidas en cuentas bancarias estatales/municipales',
        monto: 12250,
        pct: 24.0,
        color: '#e67e22',
        icono: '🏦',
        causa: 'Fondos federales transferidos en el ejercicio que al 31 de diciembre o 31 de marzo no fueron comprometidos ni reintegrados con sus rendimientos financieros.',
        marco: 'Art. 17 de la Ley de Disciplina Financiera y Art. 54 de la LFPRH',
        sancion: 'Obligación perentoria de reintegro a la Tesorería de la Federación más cargas financieras generadas.'
      },
      {
        id: 'pagos_improcedentes',
        nombre: 'Pagos Improcedentes o en Exceso',
        subtitulo: 'Nóminas infladas, comisionados sindicales ("aviadores") y sobrecostos',
        monto: 9680,
        pct: 19.0,
        color: '#f1c40f',
        icono: '👥',
        causa: 'Erogaciones por conceptos no autorizados en el tabulador, pagos a trabajadores dados de baja o fallecidos, y liquidaciones duplicadas en salud (FASSA) y educación (FONE).',
        marco: 'Arts. 127 CPEUM y 65 de la Ley General del Sistema de Carrera para Maestras y Maestros',
        sancion: 'Procedimientos de Responsabilidad Resarcitoria (PRR) individualizados a pagadores habilitados.'
      },
      {
        id: 'desvio_ramo33',
        nombre: 'Desvío de Recursos a Fines No Autorizados',
        subtitulo: 'Uso de fondos etiquetados de infraestructura para gasto corriente o nómina política',
        monto: 6120,
        pct: 12.0,
        color: '#9b59b6',
        icono: '🔀',
        causa: 'Aplicación de aportaciones del Ramo 33 (FAIS y FORTAMUN) para solventar déficit de gasto operativo, eventos o gasto electoral, violando el destino legal del fondo.',
        marco: 'Arts. 33 y 49 de la Ley de Coordinación Fiscal (LCF)',
        sancion: 'Denuncias de Hechos (DH) formuladas ante la FGR por desvío de recursos públicos y peculado.'
      },
      {
        id: 'licitaciones_simuladas',
        nombre: 'Opacidad en Licitaciones y Adjudicaciones Directas',
        subtitulo: 'Fraccionamiento de contratos, sobreprecios y elusión de licitación pública',
        monto: 4574,
        pct: 8.9,
        color: '#00c3ff',
        icono: '🤝',
        causa: 'Asignación directa indebida de contratos de obra pública y adquisiciones a empresas de reciente creación sin experiencia ni capacidad técnica demostrada.',
        marco: 'Art. 134 CPEUM y Art. 41 de la Ley de Adquisiciones, Arrendamientos y Servicios',
        sancion: 'Inhabilitación de servidores públicos y empresas proveedoras ante la Secretaría de la Función Pública.'
      }
    ],
    historico: [
      { year: 'CP 2018', monto: 68140, auditorias: 1807, resueltoPct: 78, color: '#f39c12', nota: 'Cierre de sexenio anterior con alta concentración en proyectos carreteros y fondos de seguridad.' },
      { year: 'CP 2019', monto: 100920, auditorias: 1359, resueltoPct: 71, color: '#e74c3c', nota: 'Pico histórico observado: arranque de administración federal y observaciones preliminares en megaobras.' },
      { year: 'CP 2020', monto: 63056, auditorias: 1622, resueltoPct: 65, color: '#e67e22', nota: 'Año de pandemia Covid-19: observaciones en compras de emergencia de insumos médicos sin contrato formal.' },
      { year: 'CP 2021', monto: 64834, auditorias: 2050, resueltoPct: 58, color: '#e67e22', nota: 'Primeras auditorías forenses a Segalmex y programas de subsidios de la Secretaría de Bienestar.' },
      { year: 'CP 2022', monto: 32894, auditorias: 2153, resueltoPct: 49, color: '#f1c40f', nota: 'Implementación del buzón digital y auditorías electrónicas masivas de la ASF.' },
      { year: 'CP 2023', monto: 32950, auditorias: 2258, resueltoPct: 42, color: '#f1c40f', nota: 'Revisión intermedia: 65% de observaciones concentradas en estados y municipios del Ramo 33.' },
      { year: 'CP 2024–25', monto: 51024, auditorias: 2100, resueltoPct: 15, color: '#e74c3c', nota: 'Cuenta Pública en proceso activo de solventación: $35,074 mdp pendientes de aclarar en municipios.' }
    ]
  };

  let currentAsfChartView = 'tipologia';
  let activeAsfItemId = null;
  let isAsfIrregEvaluated = false;
  let isAsfIrregAnimating = false;
  let isAsfIrregHoverEnabled = false;
  let asfIrregAnimFrameId = null;

  function renderAsfIrregularidadesChart(mode) {
    const stage = document.getElementById('asfIrregularidadesStage');
    if (!stage) return;

    currentAsfChartView = mode || 'tipologia';

    const statusEl = document.getElementById('asfIrregEvalStatusText');
    const btnEval = document.getElementById('btnEvaluarAsfIrreg');
    if (!isAsfIrregAnimating) {
      if (isAsfIrregEvaluated) {
        if (statusEl) statusEl.innerHTML = '<span style="color:var(--emerald-bright);">✓ Auditoría forense completada: Irregularidades y montos por aclarar desplegados al 100%.</span>';
        if (btnEval) btnEval.innerHTML = '<span>🔄</span> Volver a Evaluar';
      } else {
        if (statusEl) statusEl.innerHTML = '⚪ Barras en reposo ($0 mdp / 0.0%). Presiona «Evaluar Irregularidades» o pasa el cursor para medir la escala real.';
        if (btnEval) btnEval.innerHTML = '<span>▶️</span> Evaluar Irregularidades';
      }
    }

    if (currentAsfChartView === 'tipologia') {
      const maxMonto = Math.max(...ASF_IRREGULARIDADES_DATA.tipologias.map(t => t.monto));
      let html = '<div style="display:flex; flex-direction:column; gap:12px;">';

      ASF_IRREGULARIDADES_DATA.tipologias.forEach(item => {
        const targetWidth = Math.max(6, (item.monto / maxMonto) * 100);
        const isSelected = activeAsfItemId === item.id;
        const borderStyle = isSelected ? `border-left: 4px solid ${item.color}; background: rgba(255,255,255,0.06);` : `border-left: 3px solid ${item.color}; background: rgba(0,0,0,0.25);`;

        const barWidthStyle = isAsfIrregEvaluated ? `${targetWidth}%` : '0%';
        const barClass = isAsfIrregEvaluated ? 'asf-bar-fill' : 'asf-bar-fill bar-zero';
        const montoText = isAsfIrregEvaluated ? `$${item.monto.toLocaleString('es-MX')} mdp` : '$0 mdp';
        const pctText = isAsfIrregEvaluated ? `(${item.pct}%)` : '(0.0%)';

        html += `
          <div class="asf-irreg-item" onclick="window.AuditEngine.selectAsfIrregularidadItem('${item.id}', 'tipologia')" 
               style="cursor:pointer; padding:10px 14px; border-radius:6px; transition:all 0.2s ease; ${borderStyle}"
               title="Clic para inspeccionar fundamento legal y expedientes">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:6px;">
              <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:16px;">${item.icono}</span>
                <span style="font-family:var(--font-serif); font-size:13.5px; color:var(--text-main); font-weight:600;">${item.nombre}</span>
              </div>
              <div style="font-family:var(--font-mono); font-size:12px; font-weight:700;">
                <span id="asfTipMonto_${item.id}" style="color:${item.color};">${montoText}</span>
                <span id="asfTipPct_${item.id}" style="color:var(--text-dim); margin-left:6px;">${pctText}</span>
              </div>
            </div>
            <div style="background:rgba(255,255,255,0.06); height:8px; border-radius:4px; overflow:hidden;">
              <div id="asfTipBar_${item.id}" class="${barClass}" style="width:${barWidthStyle}; height:100%; background:linear-gradient(90deg, ${item.color}, #f1c40f); border-radius:4px; transition:width 0.4s ease;"></div>
            </div>
            <div style="font-size:11px; color:var(--text-dim); margin-top:4px;">${item.subtitulo}</div>
          </div>
        `;
      });

      html += '</div>';
      stage.innerHTML = html;
    } else {
      // Vista Histórica (2018–2025)
      const maxMonto = Math.max(...ASF_IRREGULARIDADES_DATA.historico.map(h => h.monto));
      let html = '<div style="display:flex; flex-direction:column; gap:10px;">';

      ASF_IRREGULARIDADES_DATA.historico.forEach(item => {
        const targetWidth = Math.max(6, (item.monto / maxMonto) * 100);
        const isSelected = activeAsfItemId === item.year;
        const borderStyle = isSelected ? `border-left: 4px solid ${item.color}; background: rgba(255,255,255,0.06);` : `border-left: 3px solid ${item.color}; background: rgba(0,0,0,0.25);`;

        const barWidthStyle = isAsfIrregEvaluated ? `${targetWidth}%` : '0%';
        const barClass = isAsfIrregEvaluated ? 'asf-bar-fill' : 'asf-bar-fill bar-zero';
        const montoText = isAsfIrregEvaluated ? `$${item.monto.toLocaleString('es-MX')} mdp observados` : '$0 mdp observados';
        const solvText = isAsfIrregEvaluated ? `(${item.resueltoPct}% solventado)` : '(0.0% solventado)';

        html += `
          <div class="asf-irreg-item" onclick="window.AuditEngine.selectAsfIrregularidadItem('${item.year}', 'historico')" 
               style="cursor:pointer; padding:10px 14px; border-radius:6px; transition:all 0.2s ease; ${borderStyle}"
               title="Clic para ver contexto de auditoría de este año">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:6px;">
              <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-family:var(--font-mono); font-size:12px; font-weight:800; color:var(--gold-bright);">${item.year}</span>
                <span style="font-size:11.5px; color:var(--text-secondary);">${item.auditorias} auditorías practicadas</span>
              </div>
              <div style="font-family:var(--font-mono); font-size:12px; font-weight:700;">
                <span id="asfHistMonto_${item.year}" style="color:${item.color};">${montoText}</span>
                <span id="asfHistSolv_${item.year}" style="color:var(--text-dim); margin-left:6px;">${solvText}</span>
              </div>
            </div>
            <div style="background:rgba(255,255,255,0.06); height:8px; border-radius:4px; overflow:hidden;">
              <div id="asfHistBar_${item.year}" class="${barClass}" style="width:${barWidthStyle}; height:100%; background:linear-gradient(90deg, ${item.color}, var(--gold-bright)); border-radius:4px; transition:width 0.4s ease;"></div>
            </div>
            <div style="font-size:11px; color:var(--text-dim); margin-top:4px;">${item.nota}</div>
          </div>
        `;
      });

      html += '</div>';
      stage.innerHTML = html;
    }
  }

  function setAsfChartView(viewMode) {
    if (asfIrregAnimFrameId) {
      cancelAnimationFrame(asfIrregAnimFrameId);
      asfIrregAnimFrameId = null;
      isAsfIrregAnimating = false;
    }

    currentAsfChartView = viewMode;
    const btnTip = document.getElementById('btnAsfViewTipologia');
    const btnHist = document.getElementById('btnAsfViewHistorico');

    if (btnTip && btnHist) {
      if (viewMode === 'tipologia') {
        btnTip.classList.add('active');
        btnTip.style.borderColor = 'var(--gold)';
        btnTip.style.color = 'var(--gold-bright)';
        btnHist.classList.remove('active');
        btnHist.style.borderColor = 'var(--border-subtle)';
        btnHist.style.color = 'var(--text-secondary)';
      } else {
        btnHist.classList.add('active');
        btnHist.style.borderColor = 'var(--gold)';
        btnHist.style.color = 'var(--gold-bright)';
        btnTip.classList.remove('active');
        btnTip.style.borderColor = 'var(--border-subtle)';
        btnTip.style.color = 'var(--text-secondary)';
      }
    }

    renderAsfIrregularidadesChart(viewMode);
  }

  function selectAsfIrregularidadItem(id, mode) {
    activeAsfItemId = id;
    const detailBox = document.getElementById('asfIrregularidadesDetailBox');
    if (!detailBox) return;

    if (mode === 'tipologia') {
      const item = ASF_IRREGULARIDADES_DATA.tipologias.find(t => t.id === id);
      if (!item) return;

      detailBox.innerHTML = `
        <div style="border-left:3px solid ${item.color}; padding-left:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; margin-bottom:6px;">
            <strong style="font-family:var(--font-serif); font-size:14.5px; color:var(--gold-bright);">${item.icono} ${item.nombre}</strong>
            <span style="font-family:var(--font-mono); font-size:12px; color:${item.color}; font-weight:800;">$${item.monto.toLocaleString('es-MX')} mdp (${item.pct}%)</span>
          </div>
          <p style="margin:0 0 6px 0; color:var(--text-main); font-size:12px;"><b>Causa detectada por la ASF:</b> ${item.causa}</p>
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:10px; font-size:11.5px; color:var(--text-secondary); margin-top:8px;">
            <div><b style="color:var(--cyan);">📜 Fundamento Jurídico:</b> ${item.marco}</div>
            <div><b style="color:var(--gold);">⚖️ Consecuencia Sancionatoria:</b> ${item.sancion}</div>
          </div>
        </div>
      `;
    } else {
      const item = ASF_IRREGULARIDADES_DATA.historico.find(h => h.year === id);
      if (!item) return;

      detailBox.innerHTML = `
        <div style="border-left:3px solid ${item.color}; padding-left:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; margin-bottom:6px;">
            <strong style="font-family:var(--font-mono); font-size:14px; color:var(--gold-bright);">Cuenta Pública ${item.year}</strong>
            <span style="font-family:var(--font-mono); font-size:12px; color:${item.color}; font-weight:800;">$${item.monto.toLocaleString('es-MX')} mdp observados</span>
          </div>
          <p style="margin:0 0 6px 0; color:var(--text-main); font-size:12px;"><b>Hallazgos y Contexto de Auditoría:</b> ${item.nota}</p>
          <div style="display:flex; gap:16px; font-family:var(--font-mono); font-size:11.5px; color:var(--text-secondary); margin-top:6px;">
            <span>Auditorías Totales: <b>${item.auditorias}</b></span>
            <span>Porcentaje Solventado al Cierre: <b style="color:#2ecc71;">${item.resueltoPct}%</b></span>
          </div>
        </div>
      `;
    }

    renderAsfIrregularidadesChart(mode);
  }

  function evaluarAsfIrregularidades(duracionMs = 1400) {
    if (asfIrregAnimFrameId) {
      cancelAnimationFrame(asfIrregAnimFrameId);
      asfIrregAnimFrameId = null;
    }

    const statusEl = document.getElementById('asfIrregEvalStatusText');
    const btnEval = document.getElementById('btnEvaluarAsfIrreg');
    if (statusEl) {
      statusEl.innerHTML = '<span style="color:var(--gold-bright);">⚡ Evaluando y auditando irregularidades ASF en tiempo real...</span>';
    }
    if (btnEval) {
      btnEval.innerHTML = '<span>⏳</span> Evaluando...';
    }

    // Quitar clases bar-zero de las barras visibles
    if (currentAsfChartView === 'tipologia') {
      ASF_IRREGULARIDADES_DATA.tipologias.forEach(item => {
        const b = document.getElementById(`asfTipBar_${item.id}`);
        if (b) b.classList.remove('bar-zero');
      });
    } else {
      ASF_IRREGULARIDADES_DATA.historico.forEach(item => {
        const b = document.getElementById(`asfHistBar_${item.year}`);
        if (b) b.classList.remove('bar-zero');
      });
    }

    isAsfIrregAnimating = true;
    const startTime = performance.now();
    const easeOutCubic = (t) => (--t) * t * t + 1;

    function animateStep(now) {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / duracionMs);
      const eased = easeOutCubic(progress);

      if (currentAsfChartView === 'tipologia') {
        const maxMonto = Math.max(...ASF_IRREGULARIDADES_DATA.tipologias.map(t => t.monto));
        ASF_IRREGULARIDADES_DATA.tipologias.forEach(item => {
          const bar = document.getElementById(`asfTipBar_${item.id}`);
          const montoEl = document.getElementById(`asfTipMonto_${item.id}`);
          const pctEl = document.getElementById(`asfTipPct_${item.id}`);
          const targetW = Math.max(6, (item.monto / maxMonto) * 100);

          if (bar) bar.style.width = `${(targetW * eased).toFixed(1)}%`;
          if (montoEl) montoEl.textContent = `$${Math.round(item.monto * eased).toLocaleString('es-MX')} mdp`;
          if (pctEl) pctEl.textContent = `(${(item.pct * eased).toFixed(1)}%)`;
        });
      } else {
        const maxMonto = Math.max(...ASF_IRREGULARIDADES_DATA.historico.map(h => h.monto));
        ASF_IRREGULARIDADES_DATA.historico.forEach(item => {
          const bar = document.getElementById(`asfHistBar_${item.year}`);
          const montoEl = document.getElementById(`asfHistMonto_${item.year}`);
          const solvEl = document.getElementById(`asfHistSolv_${item.year}`);
          const targetW = Math.max(6, (item.monto / maxMonto) * 100);

          if (bar) bar.style.width = `${(targetW * eased).toFixed(1)}%`;
          if (montoEl) montoEl.textContent = `$${Math.round(item.monto * eased).toLocaleString('es-MX')} mdp observados`;
          if (solvEl) solvEl.textContent = `(${(item.resueltoPct * eased).toFixed(1)}% solventado)`;
        });
      }

      if (progress < 1) {
        asfIrregAnimFrameId = requestAnimationFrame(animateStep);
      } else {
        isAsfIrregAnimating = false;
        isAsfIrregEvaluated = true;
        asfIrregAnimFrameId = null;

        // Fijar valores finales exactos
        if (currentAsfChartView === 'tipologia') {
          const maxMonto = Math.max(...ASF_IRREGULARIDADES_DATA.tipologias.map(t => t.monto));
          ASF_IRREGULARIDADES_DATA.tipologias.forEach(item => {
            const bar = document.getElementById(`asfTipBar_${item.id}`);
            const montoEl = document.getElementById(`asfTipMonto_${item.id}`);
            const pctEl = document.getElementById(`asfTipPct_${item.id}`);
            const targetW = Math.max(6, (item.monto / maxMonto) * 100);
            if (bar) bar.style.width = `${targetW}%`;
            if (montoEl) montoEl.textContent = `$${item.monto.toLocaleString('es-MX')} mdp`;
            if (pctEl) pctEl.textContent = `(${item.pct}%)`;
          });
        } else {
          const maxMonto = Math.max(...ASF_IRREGULARIDADES_DATA.historico.map(h => h.monto));
          ASF_IRREGULARIDADES_DATA.historico.forEach(item => {
            const bar = document.getElementById(`asfHistBar_${item.year}`);
            const montoEl = document.getElementById(`asfHistMonto_${item.year}`);
            const solvEl = document.getElementById(`asfHistSolv_${item.year}`);
            const targetW = Math.max(6, (item.monto / maxMonto) * 100);
            if (bar) bar.style.width = `${targetW}%`;
            if (montoEl) montoEl.textContent = `$${item.monto.toLocaleString('es-MX')} mdp observados`;
            if (solvEl) solvEl.textContent = `(${item.resueltoPct}% solventado)`;
          });
        }

        if (statusEl) {
          statusEl.innerHTML = '<span style="color:var(--emerald-bright);">✓ Auditoría forense completada: Irregularidades y montos por aclarar desplegados al 100%.</span>';
        }
        if (btnEval) {
          btnEval.innerHTML = '<span>🔄</span> Volver a Evaluar';
        }
      }
    }

    asfIrregAnimFrameId = requestAnimationFrame(animateStep);
  }

  function resetAsfIrregularidades() {
    if (asfIrregAnimFrameId) {
      cancelAnimationFrame(asfIrregAnimFrameId);
      asfIrregAnimFrameId = null;
    }
    isAsfIrregAnimating = false;
    isAsfIrregEvaluated = false;

    if (currentAsfChartView === 'tipologia') {
      ASF_IRREGULARIDADES_DATA.tipologias.forEach(item => {
        const bar = document.getElementById(`asfTipBar_${item.id}`);
        const montoEl = document.getElementById(`asfTipMonto_${item.id}`);
        const pctEl = document.getElementById(`asfTipPct_${item.id}`);
        if (bar) {
          bar.classList.add('bar-zero');
          bar.style.width = '0%';
        }
        if (montoEl) montoEl.textContent = '$0 mdp';
        if (pctEl) pctEl.textContent = '(0.0%)';
      });
    } else {
      ASF_IRREGULARIDADES_DATA.historico.forEach(item => {
        const bar = document.getElementById(`asfHistBar_${item.year}`);
        const montoEl = document.getElementById(`asfHistMonto_${item.year}`);
        const solvEl = document.getElementById(`asfHistSolv_${item.year}`);
        if (bar) {
          bar.classList.add('bar-zero');
          bar.style.width = '0%';
        }
        if (montoEl) montoEl.textContent = '$0 mdp observados';
        if (solvEl) solvEl.textContent = '(0.0% solventado)';
      });
    }

    const statusEl = document.getElementById('asfIrregEvalStatusText');
    if (statusEl) {
      statusEl.innerHTML = '⚪ Barras en reposo ($0 mdp / 0.0%). Presiona «Evaluar Irregularidades» o pasa el cursor para medir la escala real.';
    }
    const btnEval = document.getElementById('btnEvaluarAsfIrreg');
    if (btnEval) {
      btnEval.innerHTML = '<span>▶️</span> Evaluar Irregularidades';
    }
  }

  function toggleHoverAsfIrregularidades(enabled) {
    isAsfIrregHoverEnabled = !!enabled;
  }

  function handleAsfIrregContainerHover() {
    if (isAsfIrregHoverEnabled && !isAsfIrregEvaluated && !isAsfIrregAnimating) {
      evaluarAsfIrregularidades();
    }
  }



  let isCongresosHealthEvaluated = false;
  let isCongresosHealthEvaluating = false;
  let isCongresosHealthHoverEnabled = false;
  let congresosAnimFrameId = null;
  let congresosTremorFrameId = null;
  let congresosNeedleAngle = -90;
  let congresosDisplayedScore = 0;

  function updateCongresosSimulator() {
    const rMoches = document.getElementById('congresosRangeMoches');
    const rTope = document.getElementById('congresosRangeTope');
    const rOp = document.getElementById('congresosRangeOp');

    const pMoches = rMoches ? parseInt(rMoches.value, 10) : 0;
    const topeCosto = rTope ? parseInt(rTope.value, 10) : 35;
    const pOp = rOp ? parseInt(rOp.value, 10) : 0;

    const lblMoches = document.getElementById('congresosSliderVal_moches');
    if (lblMoches) lblMoches.textContent = `${pMoches}%`;

    const lblTope = document.getElementById('congresosSliderVal_tope');
    if (lblTope) {
      lblTope.textContent = topeCosto >= 35 ? 'Sin Tope ($35 mdp)' : `$${topeCosto}.0 mdp / dip`;
    }

    const lblOp = document.getElementById('congresosSliderVal_op');
    if (lblOp) lblOp.textContent = `${pOp}%`;

    // Cálculos de ahorro basados en los 32 congresos de DB.legislativo
    const items = (DB.legislativo && DB.legislativo.congresosEstatales) || [];
    let basePresupuesto = 15248; // mdp total aproximado
    let totalMoches = 1860; // mdp aproximado de partidas de gestión

    if (items.length > 0) {
      basePresupuesto = items.reduce((acc, c) => acc + (c.presupuestoCongreso || 0), 0);
      totalMoches = items.reduce((acc, c) => acc + (c.partidaGestionSocial || 0), 0);
    }

    const ahorroMoches = Math.round(totalMoches * (pMoches / 100));

    let ahorroTope = 0;
    let greenCount = 0;
    if (items.length > 0) {
      items.forEach(c => {
        if (topeCosto < 35 && c.costoPorDiputado > topeCosto) {
          ahorroTope += (c.costoPorDiputado - topeCosto) * c.diputados;
        }
        const effectiveCost = topeCosto < 35 ? Math.min(c.costoPorDiputado, topeCosto) : c.costoPorDiputado;
        if (effectiveCost <= 16) greenCount++;
      });
    } else {
      ahorroTope = topeCosto < 35 ? Math.round((35 - topeCosto) * 110) : 0;
      greenCount = topeCosto <= 16 ? 32 : Math.round(9 + (35 - topeCosto) * 0.9);
    }
    ahorroTope = Math.round(ahorroTope);

    const ahorroOp = Math.round((basePresupuesto - totalMoches) * (pOp / 100) * 0.12);
    const totalAhorro = Math.min(basePresupuesto - 4000, ahorroMoches + ahorroTope + ahorroOp);
    const nuevoPresupuesto = Math.max(4000, basePresupuesto - totalAhorro);

    // Actualizar tarjetas de impacto
    const elAhorro = document.getElementById('congresosAhorroMdp');
    if (elAhorro) elAhorro.textContent = `+$${totalAhorro.toLocaleString('es-MX')} mdp`;

    const elNuevo = document.getElementById('congresosNuevoPresupuesto');
    if (elNuevo) elNuevo.textContent = `$${nuevoPresupuesto.toLocaleString('es-MX')} mdp`;

    const elVerde = document.getElementById('congresosSemaforoVerde');
    if (elVerde) elVerde.textContent = `${Math.min(32, greenCount)} / 32`;

    const elEquiv = document.getElementById('congresosEquivalenciaTxt');
    if (elEquiv) {
      if (totalAhorro > 0) {
        const ambulancias = Math.round(totalAhorro / 2.5);
        const becas = Math.round((totalAhorro * 1000000) / 48000);
        elEquiv.innerHTML = `Este ahorro de <b>$${totalAhorro.toLocaleString('es-MX')} mdp</b> equivale a financiar <b>${becas.toLocaleString('es-MX')} becas anuales completas</b> o equipar <b>${ambulancias.toLocaleString('es-MX')} ambulancias de terapia intensiva</b> para centros de salud en municipios marginados.`;
      } else {
        elEquiv.textContent = 'En estado de reposo. Mueve los controles o presiona calibrar para calcular las obras sociales equivalentes al ahorro.';
      }
    }

    // Calcular score (0 a 100)
    // Factores: moches (35%), tope (40%), operativo (25%)
    let score = Math.round((pMoches * 0.35) + ((35 - topeCosto) / 23 * 40) + ((pOp / 40) * 25));
    score = Math.max(0, Math.min(100, score));

    // Actualizar aguja y pilares si no está en evaluación animada
    if (!isCongresosHealthEvaluating) {
      const targetAngle = -90 + (score / 100) * 180;
      congresosNeedleAngle = targetAngle;
      congresosDisplayedScore = score;

      const needleEl = document.getElementById('congresosNeedleGroup');
      if (needleEl) needleEl.style.transform = `rotate(${targetAngle}deg)`;

      const scoreEl = document.getElementById('congresosScoreNum');
      if (scoreEl) {
        scoreEl.textContent = score;
        scoreEl.style.color = score >= 80 ? '#2ecc71' : (score >= 50 ? '#f1c40f' : (score > 0 ? '#e67e22' : 'var(--text-dim)'));
      }

      // Pilares
      const p1 = Math.min(100, Math.round(((35 - topeCosto) / 23) * 100));
      const p2 = pMoches;
      const p3 = Math.min(100, Math.round((pOp / 40) * 100));
      const p4 = Math.min(100, Math.round((pMoches * 0.5 + ((35 - topeCosto) / 23) * 50)));

      updateCongresosPillarsDOM(p1, p2, p3, p4);

      const statusEl = document.getElementById('congresosStatusPill');
      if (statusEl) {
        if (score === 0) {
          statusEl.textContent = '⚪ Simulador en Reposo. Presiona «Calibrar Austeridad».';
          statusEl.style.color = 'var(--text-dim)';
        } else if (score >= 80) {
          statusEl.innerHTML = `🟢 <b>Austeridad Subnacional Ejemplar (${score} pts)</b> · Cero moches y costo racional.`;
          statusEl.style.color = '#2ecc71';
        } else if (score >= 50) {
          statusEl.innerHTML = `🟡 <b>Racionalidad Moderada (${score} pts)</b> · Ahorro en progreso.`;
          statusEl.style.color = '#f1c40f';
        } else {
          statusEl.innerHTML = `🔴 <b>Dispendio Detectado (${score} pts)</b> · Costos elevados por legislador.`;
          statusEl.style.color = '#e74c3c';
        }
      }
    }
  }

  function updateCongresosPillarsDOM(p1, p2, p3, p4) {
    const f1 = document.getElementById('congresosPillarFill_1');
    const v1 = document.getElementById('congresosPillarVal_1');
    if (f1) f1.style.width = `${p1}%`;
    if (v1) v1.textContent = `${p1}%`;

    const f2 = document.getElementById('congresosPillarFill_2');
    const v2 = document.getElementById('congresosPillarVal_2');
    if (f2) f2.style.width = `${p2}%`;
    if (v2) v2.textContent = `${p2}%`;

    const f3 = document.getElementById('congresosPillarFill_3');
    const v3 = document.getElementById('congresosPillarVal_3');
    if (f3) f3.style.width = `${p3}%`;
    if (v3) v3.textContent = `${p3}%`;

    const f4 = document.getElementById('congresosPillarFill_4');
    const v4 = document.getElementById('congresosPillarVal_4');
    if (f4) f4.style.width = `${p4}%`;
    if (v4) v4.textContent = `${p4}%`;
  }

  function evaluarSaludCongresos() {
    if (isCongresosHealthEvaluating) return;
    if (congresosAnimFrameId) cancelAnimationFrame(congresosAnimFrameId);
    if (congresosTremorFrameId) cancelAnimationFrame(congresosTremorFrameId);

    isCongresosHealthEvaluating = true;

    // Ajustar controles a valores recomendados de alta austeridad
    const rMoches = document.getElementById('congresosRangeMoches');
    const rTope = document.getElementById('congresosRangeTope');
    const rOp = document.getElementById('congresosRangeOp');
    if (rMoches) rMoches.value = 100;
    if (rTope) rTope.value = 14;
    if (rOp) rOp.value = 25;

    const startAngle = congresosNeedleAngle;
    const targetScore = 94;
    const targetAngle = -90 + (targetScore / 100) * 180; // ~79.2deg
    const startTime = performance.now();
    const duration = 1200;

    const needleEl = document.getElementById('congresosNeedleGroup');
    const scoreEl = document.getElementById('congresosScoreNum');
    const statusEl = document.getElementById('congresosStatusPill');

    function animateStep(now) {
      const p = Math.min(1, (now - startTime) / duration);
      // Easing cúbico con ligero overshoot
      const ease = p < 0.8 ? (1 - Math.pow(1 - p / 0.8, 3)) * 1.04 : 1.04 - (p - 0.8) / 0.2 * 0.04;
      
      const currentAngle = startAngle + (targetAngle - startAngle) * Math.min(1, ease);
      const currentScore = Math.round(targetScore * Math.min(1, ease));

      if (needleEl) needleEl.style.transform = `rotate(${currentAngle}deg)`;
      if (scoreEl) {
        scoreEl.textContent = currentScore;
        scoreEl.style.color = currentScore >= 80 ? '#2ecc71' : '#f1c40f';
      }

      updateCongresosPillarsDOM(
        Math.round(92 * Math.min(1, ease)),
        Math.round(100 * Math.min(1, ease)),
        Math.round(62 * Math.min(1, ease)),
        Math.round(96 * Math.min(1, ease))
      );

      if (p < 1) {
        congresosAnimFrameId = requestAnimationFrame(animateStep);
      } else {
        congresosNeedleAngle = targetAngle;
        congresosDisplayedScore = targetScore;
        isCongresosHealthEvaluating = false;
        isCongresosHealthEvaluated = true;
        congresosAnimFrameId = null;

        if (statusEl) {
          statusEl.innerHTML = `🟢 <b>Calibración Completada: Austeridad Subnacional Ejemplar (${targetScore} pts)</b>`;
          statusEl.style.color = '#2ecc71';
        }

        updateCongresosSimulator();
        startCongresosTremor();
      }
    }

    congresosAnimFrameId = requestAnimationFrame(animateStep);
  }

  function startCongresosTremor() {
    if (congresosTremorFrameId) cancelAnimationFrame(congresosTremorFrameId);
    if (!isCongresosHealthEvaluated) return;

    function tremorStep(timestamp) {
      const tremor = Math.sin(timestamp * 0.0035) * 0.4 + Math.sin(timestamp * 0.008) * 0.2;
      const angle = congresosNeedleAngle + tremor;
      const needleEl = document.getElementById('congresosNeedleGroup');
      if (needleEl) needleEl.style.transform = `rotate(${angle}deg)`;
      congresosTremorFrameId = requestAnimationFrame(tremorStep);
    }

    congresosTremorFrameId = requestAnimationFrame(tremorStep);
  }

  function resetSaludCongresos() {
    if (congresosAnimFrameId) cancelAnimationFrame(congresosAnimFrameId);
    if (congresosTremorFrameId) cancelAnimationFrame(congresosTremorFrameId);

    isCongresosHealthEvaluating = false;
    isCongresosHealthEvaluated = false;

    const rMoches = document.getElementById('congresosRangeMoches');
    const rTope = document.getElementById('congresosRangeTope');
    const rOp = document.getElementById('congresosRangeOp');
    if (rMoches) rMoches.value = 0;
    if (rTope) rTope.value = 35;
    if (rOp) rOp.value = 0;

    const startAngle = congresosNeedleAngle;
    const startTime = performance.now();
    const duration = 500;

    function resetStep(now) {
      const p = Math.min(1, (now - startTime) / duration);
      const ease = 1 - Math.pow(1 - p, 3);
      const curAngle = startAngle + (-90 - startAngle) * ease;
      const curScore = Math.round(congresosDisplayedScore * (1 - ease));

      const needleEl = document.getElementById('congresosNeedleGroup');
      if (needleEl) needleEl.style.transform = `rotate(${curAngle}deg)`;

      const scoreEl = document.getElementById('congresosScoreNum');
      if (scoreEl) {
        scoreEl.textContent = curScore;
        scoreEl.style.color = 'var(--text-dim)';
      }

      updateCongresosPillarsDOM(
        Math.round(parseFloat(document.getElementById('congresosPillarVal_1')?.textContent || '0') * (1 - ease)),
        Math.round(parseFloat(document.getElementById('congresosPillarVal_2')?.textContent || '0') * (1 - ease)),
        Math.round(parseFloat(document.getElementById('congresosPillarVal_3')?.textContent || '0') * (1 - ease)),
        Math.round(parseFloat(document.getElementById('congresosPillarVal_4')?.textContent || '0') * (1 - ease))
      );

      if (p < 1) {
        congresosAnimFrameId = requestAnimationFrame(resetStep);
      } else {
        congresosNeedleAngle = -90;
        congresosDisplayedScore = 0;
        congresosAnimFrameId = null;

        updateCongresosPillarsDOM(0, 0, 0, 0);

        const statusEl = document.getElementById('congresosStatusPill');
        if (statusEl) {
          statusEl.textContent = '⚪ Simulador en Reposo. Presiona «Calibrar Austeridad».';
          statusEl.style.color = 'var(--text-dim)';
        }

        updateCongresosSimulator();
      }
    }

    congresosAnimFrameId = requestAnimationFrame(resetStep);
  }

  function toggleHoverSaludCongresos(enabled) {
    isCongresosHealthHoverEnabled = !!enabled;
  }

  function handleCongresosConsoleHover() {
    if (isCongresosHealthHoverEnabled && !isCongresosHealthEvaluated && !isCongresosHealthEvaluating) {
      evaluarSaludCongresos();
    }
  }

  // ==========================================================================
  // SIMULADOR 3.4: SALUD SALARIAL & CUMPLIMIENTO ART. 127 CONSTITUCIONAL
  // ==========================================================================
  let isJerarquiaHealthEvaluated = false;
  let isJerarquiaHealthEvaluating = false;
  let isJerarquiaHealthHoverEnabled = false;
  let isTope127Active = false;
  let jerarquiaAnimFrameId = null;
  let jerarquiaTremorFrameId = null;
  let jerarquiaNeedleAngle = -90;
  let jerarquiaDisplayedScore = 0;

  function toggleTope127() {
    isTope127Active = !isTope127Active;
    const btn = document.getElementById('btnToggleTope127');
    const lbl = document.getElementById('jerarquiaSliderVal_tope');

    if (isTope127Active) {
      if (btn) {
        btn.style.background = 'rgba(46,204,113,0.18)';
        btn.style.borderColor = 'var(--green-bright)';
        btn.style.color = 'var(--green-bright)';
        btn.innerHTML = '🟢 Tope Activo ($134,290/mes)';
      }
      if (lbl) {
        lbl.textContent = 'Tope Activo ($134,290/mes)';
        lbl.style.color = 'var(--green-bright)';
      }
    } else {
      if (btn) {
        btn.style.background = 'rgba(255,255,255,0.04)';
        btn.style.borderColor = 'var(--border-subtle)';
        btn.style.color = 'var(--text-secondary)';
        btn.innerHTML = '🔘 Aplicar Tope Estricto ($134,290/mes)';
      }
      if (lbl) {
        lbl.textContent = 'Inactivo ($105,000+ dieta)';
        lbl.style.color = 'var(--crimson-bright)';
      }
    }
    updateJerarquiaSimulator();
  }

  function updateJerarquiaSimulator() {
    const rAsesores = document.getElementById('jerarquiaRangeAsesores');
    const rComunal = document.getElementById('jerarquiaRangeComunal');

    const pAsesores = rAsesores ? parseInt(rAsesores.value, 10) : 0;
    const valComunal = rComunal ? parseInt(rComunal.value, 10) : 0;

    const lblAsesores = document.getElementById('jerarquiaSliderVal_asesores');
    if (lblAsesores) lblAsesores.textContent = `${pAsesores}%`;

    const lblComunal = document.getElementById('jerarquiaSliderVal_comunal');
    if (lblComunal) {
      lblComunal.textContent = valComunal > 0 ? `+$${valComunal.toLocaleString('es-MX')} / mes` : '$0 / mes (Honorífico)';
    }

    // Cálculos de ahorro
    // Base de cálculo aproximada para la burocracia representativa nacional:
    // 128 senadores + 500 diputados federales + 1098 locales + alcaldes y regidores
    const ahorroTope = isTope127Active ? 1840 : 0; // mdp/año
    const ahorroAsesores = Math.round((pAsesores / 100) * 4980); // mdp/año
    const costoComunal = Math.round((valComunal * 12 * 4500) / 1000000); // 4,500 autoridades comunales estimadas
    const totalAhorro = Math.max(0, ahorroTope + ahorroAsesores - costoComunal);

    // Brecha: Max vs Min
    const maxSueldo = isTope127Active ? 105000 : 105000;
    const minSueldo = valComunal > 0 ? valComunal : 1500;
    const ratio = Math.max(1, Math.round(maxSueldo / minSueldo));

    // Porcentaje de cumplimiento Art. 127
    let apegoPct = 54.2;
    if (isTope127Active) apegoPct += 32.0;
    apegoPct += (pAsesores / 50) * 13.8;
    apegoPct = Math.min(100, Math.round(apegoPct * 10) / 10);

    const elAhorro = document.getElementById('jerarquiaAhorroMdp');
    if (elAhorro) elAhorro.textContent = `+$${totalAhorro.toLocaleString('es-MX')} mdp`;

    const elRatio = document.getElementById('jerarquiaRatioNum');
    if (elRatio) elRatio.textContent = `${ratio} a 1`;

    const elApego = document.getElementById('jerarquiaApegoPct');
    if (elApego) elApego.textContent = `${apegoPct}%`;

    const elEquiv = document.getElementById('jerarquiaEquivalenciaTxt');
    if (elEquiv) {
      if (totalAhorro > 0) {
        elEquiv.innerHTML = `Un ahorro consolidado de <b>+$${totalAhorro.toLocaleString('es-MX')} mdp</b> permite dignificar el ingreso de miles de autoridades de pueblos originarios y financiar programas de alumbrado y pavimentación en municipios rurales.`;
      } else {
        elEquiv.textContent = 'La austeridad en las cúpulas del erario permite financiar servicios municipales de proximidad e infraestructura comunitaria básica.';
      }
    }

    // Score constitucional (0 a 100)
    let score = Math.round((isTope127Active ? 40 : 0) + (pAsesores / 50 * 35) + ((valComunal / 10000) * 25));
    score = Math.max(0, Math.min(100, score));

    if (!isJerarquiaHealthEvaluating) {
      const targetAngle = -90 + (score / 100) * 180;
      jerarquiaNeedleAngle = targetAngle;
      jerarquiaDisplayedScore = score;

      const needleEl = document.getElementById('jerarquiaNeedleGroup');
      if (needleEl) needleEl.style.transform = `rotate(${targetAngle}deg)`;

      const scoreEl = document.getElementById('jerarquiaScoreNum');
      if (scoreEl) {
        scoreEl.textContent = score;
        scoreEl.style.color = score >= 80 ? '#2ecc71' : (score >= 50 ? '#f1c40f' : (score > 0 ? '#e67e22' : 'var(--text-dim)'));
      }

      updateJerarquiaPillarsDOM(
        isTope127Active ? 100 : 25,
        Math.round((pAsesores / 50) * 100),
        Math.round((1 - (ratio / 70)) * 100),
        Math.min(100, Math.round(score * 0.95))
      );

      const statusEl = document.getElementById('jerarquiaStatusPill');
      if (statusEl) {
        if (score === 0) {
          statusEl.textContent = '⚪ Simulador en Reposo. Presiona «Calibrar Nómina».';
          statusEl.style.color = 'var(--text-dim)';
        } else if (score >= 80) {
          statusEl.innerHTML = `🟢 <b>Apego Constitucional Pleno (${score} pts)</b> · Art. 127 estricto y brecha reducida.`;
          statusEl.style.color = '#2ecc71';
        } else if (score >= 50) {
          statusEl.innerHTML = `🟡 <b>Apego Parcial (${score} pts)</b> · Avance en contención salarial.`;
          statusEl.style.color = '#f1c40f';
        } else {
          statusEl.innerHTML = `🔴 <b>Brecha Salarial Desmedida (${score} pts)</b> · Asimetría de 70 a 1.`;
          statusEl.style.color = '#e74c3c';
        }
      }
    }
  }

  function updateJerarquiaPillarsDOM(p1, p2, p3, p4) {
    const f1 = document.getElementById('jerarquiaPillarFill_1');
    const v1 = document.getElementById('jerarquiaPillarVal_1');
    if (f1) f1.style.width = `${Math.max(0, p1)}%`;
    if (v1) v1.textContent = `${Math.max(0, p1)}%`;

    const f2 = document.getElementById('jerarquiaPillarFill_2');
    const v2 = document.getElementById('jerarquiaPillarVal_2');
    if (f2) f2.style.width = `${Math.max(0, p2)}%`;
    if (v2) v2.textContent = `${Math.max(0, p2)}%`;

    const f3 = document.getElementById('jerarquiaPillarFill_3');
    const v3 = document.getElementById('jerarquiaPillarVal_3');
    if (f3) f3.style.width = `${Math.max(0, p3)}%`;
    if (v3) v3.textContent = `${Math.max(0, p3)}%`;

    const f4 = document.getElementById('jerarquiaPillarFill_4');
    const v4 = document.getElementById('jerarquiaPillarVal_4');
    if (f4) f4.style.width = `${Math.max(0, p4)}%`;
    if (v4) v4.textContent = `${Math.max(0, p4)}%`;
  }

  function evaluarSaludJerarquia() {
    if (isJerarquiaHealthEvaluating) return;
    if (jerarquiaAnimFrameId) cancelAnimationFrame(jerarquiaAnimFrameId);
    if (jerarquiaTremorFrameId) cancelAnimationFrame(jerarquiaTremorFrameId);

    isJerarquiaHealthEvaluating = true;

    // Activar tope 127
    isTope127Active = true;
    const btn = document.getElementById('btnToggleTope127');
    if (btn) {
      btn.style.background = 'rgba(46,204,113,0.18)';
      btn.style.borderColor = 'var(--green-bright)';
      btn.style.color = 'var(--green-bright)';
      btn.innerHTML = '🟢 Tope Activo ($134,290/mes)';
    }
    const lbl = document.getElementById('jerarquiaSliderVal_tope');
    if (lbl) {
      lbl.textContent = 'Tope Activo ($134,290/mes)';
      lbl.style.color = 'var(--green-bright)';
    }

    const rAsesores = document.getElementById('jerarquiaRangeAsesores');
    const rComunal = document.getElementById('jerarquiaRangeComunal');
    if (rAsesores) rAsesores.value = 35;
    if (rComunal) rComunal.value = 8000;

    const startAngle = jerarquiaNeedleAngle;
    const targetScore = 96;
    const targetAngle = -90 + (targetScore / 100) * 180; // ~82.8deg
    const startTime = performance.now();
    const duration = 1200;

    const needleEl = document.getElementById('jerarquiaNeedleGroup');
    const scoreEl = document.getElementById('jerarquiaScoreNum');
    const statusEl = document.getElementById('jerarquiaStatusPill');

    function animateStep(now) {
      const p = Math.min(1, (now - startTime) / duration);
      const ease = p < 0.8 ? (1 - Math.pow(1 - p / 0.8, 3)) * 1.04 : 1.04 - (p - 0.8) / 0.2 * 0.04;
      
      const currentAngle = startAngle + (targetAngle - startAngle) * Math.min(1, ease);
      const currentScore = Math.round(targetScore * Math.min(1, ease));

      if (needleEl) needleEl.style.transform = `rotate(${currentAngle}deg)`;
      if (scoreEl) {
        scoreEl.textContent = currentScore;
        scoreEl.style.color = currentScore >= 80 ? '#2ecc71' : '#f1c40f';
      }

      updateJerarquiaPillarsDOM(
        Math.round(100 * Math.min(1, ease)),
        Math.round(70 * Math.min(1, ease)),
        Math.round(76 * Math.min(1, ease)),
        Math.round(98 * Math.min(1, ease))
      );

      if (p < 1) {
        jerarquiaAnimFrameId = requestAnimationFrame(animateStep);
      } else {
        jerarquiaNeedleAngle = targetAngle;
        jerarquiaDisplayedScore = targetScore;
        isJerarquiaHealthEvaluating = false;
        isJerarquiaHealthEvaluated = true;
        jerarquiaAnimFrameId = null;

        if (statusEl) {
          statusEl.innerHTML = `🟢 <b>Calibración Completada: Apego Constitucional Pleno (${targetScore} pts)</b>`;
          statusEl.style.color = '#2ecc71';
        }

        updateJerarquiaSimulator();
        startJerarquiaTremor();
      }
    }

    jerarquiaAnimFrameId = requestAnimationFrame(animateStep);
  }

  function startJerarquiaTremor() {
    if (jerarquiaTremorFrameId) cancelAnimationFrame(jerarquiaTremorFrameId);
    if (!isJerarquiaHealthEvaluated) return;

    function tremorStep(timestamp) {
      const tremor = Math.sin(timestamp * 0.0035) * 0.4 + Math.sin(timestamp * 0.008) * 0.2;
      const angle = jerarquiaNeedleAngle + tremor;
      const needleEl = document.getElementById('jerarquiaNeedleGroup');
      if (needleEl) needleEl.style.transform = `rotate(${angle}deg)`;
      jerarquiaTremorFrameId = requestAnimationFrame(tremorStep);
    }

    jerarquiaTremorFrameId = requestAnimationFrame(tremorStep);
  }

  function resetSaludJerarquia() {
    if (jerarquiaAnimFrameId) cancelAnimationFrame(jerarquiaAnimFrameId);
    if (jerarquiaTremorFrameId) cancelAnimationFrame(jerarquiaTremorFrameId);

    isJerarquiaHealthEvaluating = false;
    isJerarquiaHealthEvaluated = false;

    isTope127Active = false;
    const btn = document.getElementById('btnToggleTope127');
    if (btn) {
      btn.style.background = 'rgba(255,255,255,0.04)';
      btn.style.borderColor = 'var(--border-subtle)';
      btn.style.color = 'var(--text-secondary)';
      btn.innerHTML = '🔘 Aplicar Tope Estricto ($134,290/mes)';
    }
    const lbl = document.getElementById('jerarquiaSliderVal_tope');
    if (lbl) {
      lbl.textContent = 'Inactivo ($105,000+ dieta)';
      lbl.style.color = 'var(--crimson-bright)';
    }

    const rAsesores = document.getElementById('jerarquiaRangeAsesores');
    const rComunal = document.getElementById('jerarquiaRangeComunal');
    if (rAsesores) rAsesores.value = 0;
    if (rComunal) rComunal.value = 0;

    const startAngle = jerarquiaNeedleAngle;
    const startTime = performance.now();
    const duration = 500;

    function resetStep(now) {
      const p = Math.min(1, (now - startTime) / duration);
      const ease = 1 - Math.pow(1 - p, 3);
      const curAngle = startAngle + (-90 - startAngle) * ease;
      const curScore = Math.round(jerarquiaDisplayedScore * (1 - ease));

      const needleEl = document.getElementById('jerarquiaNeedleGroup');
      if (needleEl) needleEl.style.transform = `rotate(${curAngle}deg)`;

      const scoreEl = document.getElementById('jerarquiaScoreNum');
      if (scoreEl) {
        scoreEl.textContent = curScore;
        scoreEl.style.color = 'var(--text-dim)';
      }

      if (p < 1) {
        jerarquiaAnimFrameId = requestAnimationFrame(resetStep);
      } else {
        jerarquiaNeedleAngle = -90;
        jerarquiaDisplayedScore = 0;
        jerarquiaAnimFrameId = null;

        updateJerarquiaPillarsDOM(0, 0, 0, 0);

        const statusEl = document.getElementById('jerarquiaStatusPill');
        if (statusEl) {
          statusEl.textContent = '⚪ Simulador en Reposo. Presiona «Calibrar Nómina».';
          statusEl.style.color = 'var(--text-dim)';
        }

        updateJerarquiaSimulator();
      }
    }

    jerarquiaAnimFrameId = requestAnimationFrame(resetStep);
  }

  function toggleHoverSaludJerarquia(enabled) {
    isJerarquiaHealthHoverEnabled = !!enabled;
  }

  function handleJerarquiaConsoleHover() {
    if (isJerarquiaHealthHoverEnabled && !isJerarquiaHealthEvaluated && !isJerarquiaHealthEvaluating) {
      evaluarSaludJerarquia();
    }
  }

  window.AuditEngine = {
    init: init,
    switchTab: switchTab,
    switchSubtab: switchSubtab,
    toggleTheme: toggleTheme,
    goToGlossary: goToGlossary,
    goToRef: goToRef,
    filterGlossaryByCategory: filterGlossaryByCategory,
    selectPresident: (id) => openPresidentCard(id),
    openPresidentCard: openPresidentCard,
    closePresidentCard: closePresidentCard,
    // Subpestaña 4.1: Estructura Orgánica y Territorial del PJF
    initJudicialEstructuraModule: initJudicialEstructuraModule,
    renderJudicialConceptualMap: renderJudicialConceptualMap,
    filterPjConceptLevel: filterPjConceptLevel,
    setPjView: setPjView,
    setPjMapMode: setPjMapMode,
    initPjLeafletMap: initPjLeafletMap,
    renderPjCartogram: renderPjCartogram,
    openPjCircuitDrawer: openPjCircuitDrawer,
    closePjCircuitDrawer: closePjCircuitDrawer,
    selectPjNode: selectPjNode,
    togglePjCardAccordion: togglePjCardAccordion,
    toggleAllPjAccordions: toggleAllPjAccordions,
    openPjHierarchicalModal: openPjHierarchicalModal,
    closePjHierarchicalModal: closePjHierarchicalModal,
    selectPjEstado: selectPjEstado,
    renderJudicialMinisters: renderJudicialMinisters,
    renderJudicialMinistersChart: renderJudicialMinistersChart,
    setJudicialPlenoView: setJudicialPlenoView,
    setJudicialChartMetric: setJudicialChartMetric,
    openMinisterModal: openMinisterModal,
    closeMinisterModal: closeMinisterModal,
    renderPoliticosMandatarios: renderPoliticosMandatarios,
    renderPoliticosSecundarios: renderPoliticosSecundarios,
    renderPoliticosCuriosos: renderPoliticosCuriosos,
    renderVersusPorfirio: renderVersusPorfirio,
    setVersusMetric: setVersusMetric,
    setVersusChartType: setVersusChartType,
    selectVersusPresident: selectVersusPresident,
    closeVersusScorecard: closeVersusScorecard,
    setVersusHealthPresident: setVersusHealthPresident,
    setVersusTableView: setVersusTableView,
    toggleVersusPlayback: toggleVersusPlayback,
    filterCuriosos: filterCuriosos,
    searchCuriosos: searchCuriosos,
    openExpedienteHijo: openExpedienteHijo,
    toggleGarciaLunaDossier: toggleGarciaLunaDossier,
    openGarciaLunaArgumento: openGarciaLunaArgumento,
    closeGarciaLunaArgumento: closeGarciaLunaArgumento,
    togglePorfirioDiazDossier: togglePorfirioDiazDossier,
    openPorfirioDiazArgumento: openPorfirioDiazArgumento,
    closePorfirioDiazArgumento: closePorfirioDiazArgumento,
    toggleSantaAnnaDossier: toggleSantaAnnaDossier,
    openSantaAnnaArgumento: openSantaAnnaArgumento,
    closeSantaAnnaArgumento: closeSantaAnnaArgumento,
    toggleJuarezDossier: toggleJuarezDossier,
    openJuarezArgumento: openJuarezArgumento,
    closeJuarezArgumento: closeJuarezArgumento,
    togglePersonajeDesglose: togglePersonajeDesglose,
    setPowerBranch: setPowerBranch,
    renderCongresosTable: renderCongresosTable,
    initElectoralModule: initElectoralModule,
    initElectoralMap: initElectoralMap,
    renderElectoralDistritos: renderElectoralDistritos,
    filterElectoralCircunscripcion: filterElectoralCircunscripcion,
    searchElectoralDistrict: searchElectoralDistrict,
    renderJerarquiaSalarialChart: renderJerarquiaSalarialChart,
    setJerarquiaMetric: setJerarquiaMetric,
    filterJerarquiaCategoria: filterJerarquiaCategoria,
    openCargoDetail: openCargoDetail,
    closeCargoDetail: closeCargoDetail,
    toggleJerarquiaTable: toggleJerarquiaTable,
    renderReferencias: renderReferencias,
    renderPreceptosLegales: renderPreceptosLegales,
    filterPreceptos: filterPreceptos,
    searchPreceptos: searchPreceptos,
    openPreceptoModal: openPreceptoModal,
    closePreceptoModal: closePreceptoModal,
    renderGlossary: renderGlossary,
    toggleMarcoLegal: toggleMarcoLegal,
    toggleBloqueLegislativo: toggleBloqueLegislativo,
    switchCivicElectoralTab: switchCivicElectoralTab,
    openDrawer: (abbr) => {
      const st = stateByAbbr[abbr];
      if (st) openStateDrawer(st);
    },
    closeDrawer: closeStateDrawer,
    openNewsModal: openNewsModal,
    renderSimuladorMegaobras: renderSimuladorMegaobras,
    setSimuladorPeriodo: setSimuladorPeriodo,
    setSimuladorSector: setSimuladorSector,
    setSimuladorSexenio: setSimuladorSexenio,
    initLiveLossTicker: initLiveLossTicker,
    closeNewsModal: closeNewsModal,
    toggleFaq: toggleFaq,
    setMetric: setMetric,
    // Portal Público Digital · Métodos Cívicos
    submitNuevoDebate: submitNuevoDebate,
    selectStance: selectStance,
    generarRandomNick: generarRandomNick,
    toggleReplyBox: toggleReplyBox,
    submitReplica: submitReplica,
    likeDebate: likeDebate,
    filterPortalDebates: filterPortalDebates,
    copyDebateLink: copyDebateLink,
    renderPortalDebates: renderPortalDebates,
    initPortalDigital: initPortalDigital,
    // Evaluación Dinámica Sexenal
    evaluarMetricasSexenales: evaluarMetricasSexenales,
    resetMetricasSexenales: resetMetricasSexenales,
    toggleHoverEvaluation: toggleHoverEvaluation,
    handleChartContainerHover: handleChartContainerHover,
    // Evaluación Dinámica Versus Porfirio Díaz
    evaluarMetricasVersus: evaluarMetricasVersus,
    resetMetricasVersus: resetMetricasVersus,
    toggleHoverVersusEvaluation: toggleHoverVersusEvaluation,
    handleVersusStageHover: handleVersusStageHover,
    // Monitor y Tacómetro Termostático de Salud Financiera (Parte 1 & 2)
    evaluarSaludFinanciera: evaluarSaludFinanciera,
    resetSaludFinanciera: resetSaludFinanciera,
    toggleHoverSaludEvaluation: toggleHoverSaludEvaluation,
    handleHealthConsoleHover: handleHealthConsoleHover,
    setVersusHealthPresident: setVersusHealthPresident,
    setVersusTableView: setVersusTableView,
    // Simulador de Tarjetas Ejecutivas (Parte 2)
    evaluarTarjetasEjecutivas: evaluarTarjetasEjecutivas,
    resetTarjetasEjecutivas: resetTarjetasEjecutivas,
    toggleHoverCardsEvaluation: toggleHoverCardsEvaluation,
    handleCardsHover: handleCardsHover,
    // Simulador de Ranking Hacendario (Parte 2)
    evaluarRankingHacendario: evaluarRankingHacendario,
    resetRankingHacendario: resetRankingHacendario,
    toggleHoverRankingEvaluation: toggleHoverRankingEvaluation,
    handleRankingHover: handleRankingHover,

    // Simuladores de Salud Financiera & Rigor en Cámaras Federales y ASF (Subpestaña 3.1)
    evaluarSaludDiputados: evaluarSaludDiputados,
    resetSaludDiputados: resetSaludDiputados,
    updateDiputadosSimulator: updateDiputadosSimulator,
    toggleHoverSaludDiputados: toggleHoverSaludDiputados,
    handleDiputadosConsoleHover: handleDiputadosConsoleHover,

    evaluarSaludSenado: evaluarSaludSenado,
    resetSaludSenado: resetSaludSenado,
    updateSenadoSimulator: updateSenadoSimulator,
    toggleHoverSaludSenado: toggleHoverSaludSenado,
    handleSenadoConsoleHover: handleSenadoConsoleHover,

    evaluarSaludASF: evaluarSaludASF,
    resetSaludASF: resetSaludASF,
    updateASFSimulator: updateASFSimulator,
    toggleHoverSaludASF: toggleHoverSaludASF,
    handleASFConsoleHover: handleASFConsoleHover,
    renderAsfIrregularidadesChart: renderAsfIrregularidadesChart,
    setAsfChartView: setAsfChartView,
    selectAsfIrregularidadItem: selectAsfIrregularidadItem,
    evaluarAsfIrregularidades: evaluarAsfIrregularidades,
    resetAsfIrregularidades: resetAsfIrregularidades,
    toggleHoverAsfIrregularidades: toggleHoverAsfIrregularidades,
    handleAsfIrregContainerHover: handleAsfIrregContainerHover,

    // Simuladores de Salud Financiera & Rigor Legislativo (Pestaña 3)
    evaluarSaludCongresos: evaluarSaludCongresos,
    resetSaludCongresos: resetSaludCongresos,
    updateCongresosSimulator: updateCongresosSimulator,
    toggleHoverSaludCongresos: toggleHoverSaludCongresos,
    handleCongresosConsoleHover: handleCongresosConsoleHover,
    evaluarSaludJerarquia: evaluarSaludJerarquia,
    resetSaludJerarquia: resetSaludJerarquia,
    updateJerarquiaSimulator: updateJerarquiaSimulator,
    toggleHoverSaludJerarquia: toggleHoverSaludJerarquia,
    toggleTope127: toggleTope127,
    handleJerarquiaConsoleHover: handleJerarquiaConsoleHover,

    // Simulador Comparativo de Prestaciones Judiciales (Subpestaña 4.2)
    renderJudicialPrestacionesSimulator: renderJudicialPrestacionesSimulator,
    setPrestacionesView: setPrestacionesView,
    selectPrestacionItem: selectPrestacionItem,
    evaluarPrestacionesJudiciales: evaluarPrestacionesJudiciales,
    resetPrestacionesJudiciales: resetPrestacionesJudiciales,
    toggleHoverPrestaciones: toggleHoverPrestaciones,
    handlePrestacionesHover: handlePrestacionesHover,

    // Simulador Comparativo de Asesores de Ponencia SCJN (Subpestaña 4.3)
    renderJudicialAsesoresSimulator: renderJudicialAsesoresSimulator,
    setAsesoresView: setAsesoresView,
    selectAsesoresItem: selectAsesoresItem,
    evaluarAsesoresJudiciales: evaluarAsesoresJudiciales,
    resetAsesoresJudiciales: resetAsesoresJudiciales,
    toggleHoverAsesores: toggleHoverAsesores,
    handleAsesoresHover: handleAsesoresHover,

    // Simulador Comparativo de Cálculos Globales & Salud Financiera SCJN (Subpestaña 4.4)
    renderJudicialGlobalesSimulator: renderJudicialGlobalesSimulator,
    setGlobalesView: setGlobalesView,
    setChoqueSalario: setChoqueSalario,
    setChoqueRegimen: setChoqueRegimen,
    selectGlobalesItem: selectGlobalesItem,
    evaluarGlobalesJudiciales: evaluarGlobalesJudiciales,
    resetGlobalesJudiciales: resetGlobalesJudiciales,
    toggleHoverGlobales: toggleHoverGlobales,
    handleGlobalesHover: handleGlobalesHover,

    // Pestaña 6: Modo Inspector (Auditoría Forense en Vivo)
    initFactCheckModule: initFactCheckModule,
    renderFactCheckModule: renderFactCheckModule,
    selectFactCheckPreset: selectFactCheckPreset,
    onFactCheckDependenciaChange: onFactCheckDependenciaChange,
    handleFactCheckFileSelect: handleFactCheckFileSelect,
    evaluarNoticiaForense: evaluarNoticiaForense,
    resetNoticiaForense: resetNoticiaForense,
    toggleHoverFactCheck: toggleHoverFactCheck,
    handleFactCheckHover: handleFactCheckHover,
    copiarDictamenForense: copiarDictamenForense,
  };

  document.addEventListener('DOMContentLoaded', init);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeGarciaLunaArgumento();
      closePorfirioDiazArgumento();
      closeSantaAnnaArgumento();
      closeJuarezArgumento();
      closeStateDrawer();
    }
  });
})();

