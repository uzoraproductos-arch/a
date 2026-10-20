/* Íconos de Auditavisión. Lo genera herramientas/iconos.py: no lo edites a mano.
 *
 * Los textos de la plataforma siguen escritos con emojis. Este archivo los
 * cambia, al pintarse la página, por íconos de trazo de un solo color que
 * toman el color del texto (decisión del autor, 20-10-2026). Se carga en el
 * <head>, antes del contenido: un observador cambia cada emoji en cuanto el
 * navegador lo agrega, también lo que el motor arma después, así que el
 * lector no alcanza a ver el emoji.
 *
 * Íconos: Lucide /*VERSION*/ (https://lucide.dev), licencia ISC.
 * Copyright (c) Lucide Contributors 2022; partes de Feather (MIT), Cole Bemis 2013-2022.
 */
(function () {
  'use strict';
  var MAPA = /*MAPA*/{};
  var TRAZOS = /*TRAZOS*/{};
  var NS = 'http://www.w3.org/2000/svg';

  // Una expresión con todos los emojis de la tabla, los largos primero; el
  // selector de variación (U+FE0F) y el tono de piel son opcionales.
  var claves = Object.keys(MAPA).sort(function (a, b) { return b.length - a.length; });
  var RE = new RegExp('(?:' + claves.map(function (k) {
    // Una clave que trae U+FE0F lo exige: sin él es un signo de texto.
    if (k.indexOf('\uFE0F') >= 0) return k;
    return Array.from(k).map(function (c) {
      return c.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\uFE0F?';
    }).join('');
  }).join('|') + ')(?:[\\u{1F3FB}-\\u{1F3FF}])?', 'gu');
  var LIMPIA = /[\uFE0F\u{1F3FB}-\u{1F3FF}]/gu;
  var TONOS = /[\u{1F3FB}-\u{1F3FF}]/gu;
  function clave(e) { var k = e.replace(TONOS, ''); return MAPA[k] ? k : e.replace(LIMPIA, ''); }

  function tiene(t) { RE.lastIndex = 0; return RE.test(t); }

  var cache = {};
  function icono(clave) {
    var d = MAPA[clave];
    if (!cache[clave]) {
      var s = document.createElementNS(NS, 'svg');
      s.setAttribute('viewBox', '0 0 24 24');
      s.setAttribute('fill', 'none');
      s.setAttribute('stroke', 'currentColor');
      s.setAttribute('stroke-width', '2');
      s.setAttribute('stroke-linecap', 'round');
      s.setAttribute('stroke-linejoin', 'round');
      s.setAttribute('class', 'ico ico-' + d[0] + (d[2] ? ' ' + d[2].split(' ').map(function (c) { return 'ico-' + c; }).join(' ') : ''));
      s.setAttribute('aria-hidden', 'true');
      s.setAttribute('focusable', 'false');
      s.setAttribute('data-emoji', clave);
      s.innerHTML = TRAZOS[d[0]];
      cache[clave] = s;
    }
    return cache[clave].cloneNode(true);
  }

  // Donde no cabe un SVG (pestaña del navegador, opciones de una lista,
  // atributos), el emoji solo se quita.
  function sinEmoji(t) {
    RE.lastIndex = 0;
    return t.replace(RE, '').replace(/^\s+/, '').replace(/\s{2,}/g, ' ');
  }

  var SALTA = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, NOSCRIPT: 1, TEMPLATE: 1 };
  var QUITA = { TITLE: 1, OPTION: 1, OPTGROUP: 1 };
  var ATRIBUTOS = ['title', 'aria-label', 'placeholder', 'alt'];

  function texto(n) {
    var p = n.parentNode;
    if (!p || SALTA[p.nodeName] || p.namespaceURI === NS || (p.isContentEditable)) return;
    var t = n.nodeValue;
    if (!t || !tiene(t)) return;
    if (QUITA[p.nodeName]) { n.nodeValue = sinEmoji(t); return; }
    var f = document.createDocumentFragment(), i = 0, m, solo = true;
    RE.lastIndex = 0;
    while ((m = RE.exec(t))) {
      if (m.index > i) f.appendChild(document.createTextNode(t.slice(i, m.index)));
      f.appendChild(icono(clave(m[0])));
      i = m.index + m[0].length;
    }
    if (i < t.length) f.appendChild(document.createTextNode(t.slice(i)));
    p.replaceChild(f, n);
    nombrar(p);
  }

  // Si el emoji era todo lo que decía un botón o un enlace, el ícono le
  // presta su nombre al lector de pantalla.
  function nombrar(p) {
    var e = p.closest ? p.closest('button, a, [role="button"]') : null;
    if (!e || e.hasAttribute('aria-label') || e.hasAttribute('aria-labelledby')) return;
    if ((e.textContent || '').trim()) return;
    var s = e.querySelector('svg.ico');
    if (s) e.setAttribute('aria-label', e.getAttribute('title') || MAPA[s.getAttribute('data-emoji')][1]);
  }

  function atributos(el) {
    for (var i = 0; i < ATRIBUTOS.length; i++) {
      var v = el.getAttribute(ATRIBUTOS[i]);
      if (v && tiene(v)) el.setAttribute(ATRIBUTOS[i], sinEmoji(v));
    }
  }

  function recorre(raiz) {
    if (raiz.nodeType === 3) { texto(raiz); return; }
    if (raiz.nodeType !== 1 || SALTA[raiz.nodeName]) return;
    atributos(raiz);
    if (raiz.querySelectorAll) {
      var con = raiz.querySelectorAll('[title],[aria-label],[placeholder],[alt]');
      for (var k = 0; k < con.length; k++) atributos(con[k]);
    }
    var w = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT, null), n, lista = [];
    while ((n = w.nextNode())) if (tiene(n.nodeValue)) lista.push(n);
    for (var j = 0; j < lista.length; j++) texto(lista[j]);
  }

  var obs = new MutationObserver(function (cambios) {
    for (var i = 0; i < cambios.length; i++) {
      var c = cambios[i];
      if (c.type === 'childList') {
        for (var j = 0; j < c.addedNodes.length; j++) recorre(c.addedNodes[j]);
      } else if (c.type === 'characterData') {
        texto(c.target);
      } else if (c.type === 'attributes') {
        atributos(c.target);
      }
    }
  });
  obs.observe(document.documentElement, {
    childList: true, subtree: true, characterData: true,
    attributes: true, attributeFilter: ATRIBUTOS
  });
  recorre(document.documentElement);
  document.addEventListener('DOMContentLoaded', function () { recorre(document.documentElement); });

  // Para quien arme HTML a mano: Iconos.svg('🔒') devuelve el <svg> como texto.
  window.Iconos = {
    svg: function (emoji) {
      var k = clave(emoji);
      return MAPA[k] ? icono(k).outerHTML : emoji;
    },
    nombre: function (emoji) { var d = MAPA[clave(emoji)]; return d ? d[1] : ''; },
    recorre: recorre
  };
})();
