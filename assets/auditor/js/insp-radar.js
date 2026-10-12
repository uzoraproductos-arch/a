/* Auditavisión · Modo Inspector › Radar por entidad (12-10-2026).
   La página ya trae escritos los 32 estados, el mapa y las 32 fichas
   (herramientas/insp_radar.py). Esto solo reordena la lista por el criterio
   elegido, repinta el mapa y muestra la ficha del estado que eliges.
   Sin dependencias. */
(function () {
  'use strict';
  var raiz = document.getElementById('irRaiz');
  if (!raiz) return;
  var lista = document.getElementById('irLista');
  var mapa = document.getElementById('irMapa');
  var busca = document.getElementById('irBusca');
  var ordenTx = document.getElementById('irOrdenTx');
  var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var ETQ = { intensidad: 'por cada $100 revisados', monto: 'monto por aclarar', municipios: 'peso de los municipios' };
  var actual = null;

  function todos(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  /* Reordena con una transición suave (FLIP): mide, mueve y anima. */
  function ordenar(crit) {
    if (!ETQ[crit]) return;
    raiz.setAttribute('data-crit', crit);
    todos('.ir-crit').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-crit') === crit)); });
    todos('.ir-crit-exp').forEach(function (d) { d.hidden = d.getAttribute('data-crit-exp') !== crit; });

    var items = todos('.ir-li', lista);
    var antes = {};
    if (!quieto) items.forEach(function (li) { antes[li.getAttribute('data-ent')] = li.getBoundingClientRect().top; });
    items.sort(function (a, b) {
      return parseFloat(b.getAttribute('data-v-' + crit)) - parseFloat(a.getAttribute('data-v-' + crit));
    });
    items.forEach(function (li) {
      var f = li.getAttribute('data-f-' + crit), b = li.querySelector('.ir-fila');
      li.querySelector('.ir-lugar').textContent = li.getAttribute('data-l-' + crit);
      li.querySelector('.ir-val').textContent = f;
      li.querySelector('.ir-barra-v').style.setProperty('--w', li.getAttribute('data-w-' + crit) + '%');
      b.setAttribute('aria-label', li.querySelector('.ir-nom').textContent.trim() + ': ' + f);
      lista.appendChild(li);
    });
    if (!quieto) items.forEach(function (li) {
      var d = antes[li.getAttribute('data-ent')] - li.getBoundingClientRect().top;
      if (!d || !li.animate) return;
      li.animate([{ transform: 'translateY(' + d + 'px)' }, { transform: 'none' }], { duration: 420, easing: 'ease-out' });
    });

    todos('.ir-casilla', mapa).forEach(function (c) {
      c.className = c.className.replace(/\bq\d\b/, 'q' + c.getAttribute('data-q-' + crit));
      var t = c.getAttribute('aria-label').split(':')[0] + ': ' + c.getAttribute('data-f-' + crit);
      c.setAttribute('aria-label', t);
      c.title = t;
    });
    var primero = items[0];
    if (ordenTx) ordenTx.innerHTML = 'Ordenados por <b>' + ETQ[crit] + '</b>, de mayor a menor. Primero: ' +
      primero.querySelector('.ir-nom').textContent.trim() + ' (' + primero.getAttribute('data-f-' + crit) + ').';
  }

  /* Muestra la ficha de un estado y lo marca en la lista y en el mapa. */
  function elegir(ent, llevar) {
    var ficha = document.getElementById('ir-e-' + ent);
    if (!ficha) return;
    actual = ent;
    todos('.ir-ficha').forEach(function (f) { f.hidden = f !== ficha; });
    todos('.ir-fila').forEach(function (b) {
      var si = b.parentNode.getAttribute('data-ent') === ent;
      b.classList.toggle('sel', si);
      if (si) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current');
    });
    todos('.ir-casilla', mapa).forEach(function (c) { c.classList.toggle('sel', c.getAttribute('data-ent') === ent); });
    if (busca) busca.value = ent;
    if (llevar) try { history.replaceState(null, '', '#ir-e-' + ent); } catch (e) { /* sin historial */ }
    if (llevar) {
      var r = ficha.getBoundingClientRect();
      var col = ficha.closest('.ir-col-ficha');
      if (col && getComputedStyle(col).position === 'sticky') col.scrollTop = 0;
      if (r.top < 70 || r.top > window.innerHeight * 0.6) {
        ficha.scrollIntoView({ behavior: quieto ? 'auto' : 'smooth', block: 'start' });
      }
      ficha.focus({ preventScroll: true });
    }
  }

  raiz.addEventListener('click', function (ev) {
    var b = ev.target.closest('.ir-crit');
    if (b) { ordenar(b.getAttribute('data-crit')); return; }
    var f = ev.target.closest('.ir-fila');
    if (f) { elegir(f.parentNode.getAttribute('data-ent'), true); return; }
    var c = ev.target.closest('.ir-casilla');
    if (c) { elegir(c.getAttribute('data-ent'), true); return; }
    var a = ev.target.closest('[data-ir-ir]');
    if (a) { ev.preventDefault(); elegir(a.getAttribute('data-ir-ir'), true); }
  });
  if (busca) busca.addEventListener('change', function () { elegir(busca.value, true); });

  var h = (location.hash || '').replace(/^#ir-e-/, '');
  if (h && h !== location.hash && document.getElementById('ir-e-' + h)) elegir(h, true);
  else elegir(lista.querySelector('.ir-li').getAttribute('data-ent'), false);
})();
