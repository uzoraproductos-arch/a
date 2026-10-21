# -*- coding: utf-8 -*-
"""Sexta aplicacion del Modo Inspector: «Lista negra del SAT» en pagina
propia (12-10-2026).

Antes la pagina cargaba la portada entera en un marco. Ahora trae escrito
desde Python lo principal (las cifras del corte, por situacion, con su
barra de proporciones; la guia en pasos) y un JS pequeno
(assets/auditor/js/insp-efos.js) que descarga la lista oficial
(assets/auditor/data/sat-69b.js, la genera actualizar_69b.py) en segundo
plano y busca por RFC o por nombre, uno o varios a la vez.

Regla de la plataforma (AGENTS.md, §2): las cifras salen del bloque «meta»
del archivo del SAT (oficial); las proporciones son derivadas y dicen su
operacion. Aparecer en la lista es una determinacion administrativa, no una
condena penal, y dos de sus cuatro situaciones significan lo contrario.
"""
import html
import json
import os

from presupuesto_modulos import chip

ESTILOS = ['insp-efos.css']
SCRIPTS = ['insp-efos.js']

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'sat-69b.js')

# Orden de lectura: primero lo que sigue señalado, luego lo que salio.
SITUACIONES = [
    ('F', 'Definitivo', 'def', '⛔', 'Señal fuerte',
     'El SAT determinó en definitiva que sus comprobantes amparan operaciones inexistentes. '
     'Esas facturas no tienen efectos fiscales para nadie (art. 69-B del CFF).'),
    ('P', 'Presunto', 'pre', '⚠️', 'Sospecha en curso',
     'El SAT presume que sus operaciones son inexistentes y se lo notificó. Todavía puede '
     'desvirtuarlo: no es una determinación final.'),
    ('D', 'Desvirtuado', 'des', '✅', 'Salió de la presunción',
     'Demostró ante el SAT que sus operaciones sí existieron. Salió de la presunción.'),
    ('S', 'Sentencia Favorable', 'sen', '⚖️', 'Le dieron la razón',
     'Un tribunal le dio la razón frente al SAT. No se le considera EFOS.'),
]

URL_COMPRASMX = 'https://comprasmx.buengobierno.gob.mx/'


def meta():
    """Lee el bloque meta del archivo oficial (no lo modifica)."""
    t = open(DATOS, 'rb').read().decode('utf-8')
    i = t.index('{')
    j = t.rindex('}')
    return json.loads(t[i:j + 1])['meta']


def n(v):
    return format(v, ',')


def ext(url, texto):
    return '<a href="%s" target="_blank" rel="noopener">%s ↗</a>' % (html.escape(url), texto)


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def construir(base, ref):
    m = meta()
    total = m['total']
    c = m['porSituacion']
    assert sum(c.values()) == total, 'porSituacion no suma el total'
    corte = html.escape(m['corte'])
    r_sat = ref('ref-sat-69b')
    r_cff = ref('ref-cff')
    fuente_sat = ext(m['url'], 'SAT, listados del artículo 69-B')
    fuente_csv = ext(m['csv'], 'archivo completo en CSV')

    senal = c['Definitivo'] + c['Presunto']
    salio = c['Desvirtuado'] + c['Sentencia Favorable']

    def pc(v):
        return format(v * 100 / total, '.1f')

    segs, tarjetas = [], []
    for k, nom, cl, ico, corto, txt in SITUACIONES:
        v = c[nom]
        segs.append('<span class="ef-seg ef-%s" style="--w:%s%%" title="%s: %s"></span>'
                    % (cl, format(v * 100 / total, '.3f'), nom, n(v)))
        tarjetas.append(
            '<li class="ef-sit ef-%s">'
            '<button type="button" class="ef-sit-btn" data-sit="%s" aria-pressed="false">'
            '<span class="ef-sit-cab"><span aria-hidden="true">%s</span> <b>%s</b> <small>%s</small></span>'
            '<span class="ef-sit-num">%s</span>'
            '<span class="ef-sit-pc">%s %% del listado %s</span>'
            '</button>'
            '<p>%s</p></li>'
            % (cl, k, ico, nom.capitalize() if k != 'S' else 'Sentencia favorable', corto,
               n(v), pc(v), chip('derivado'), txt))

    sit_js = {k: {'t': (nom if k != 'S' else 'Sentencia favorable'), 'c': cl, 'i': ico,
                  'corto': corto, 'txt': txt} for k, nom, cl, ico, corto, txt in SITUACIONES}
    datos = {'corte': m['corte'], 'total': total, 'sit': sit_js}

    return ('''
<div class="ef" id="ef">
  <script type="application/json" id="efDatos">%(datos)s</script>

  <section class="ef-hero" aria-labelledby="ef-q-tit">
    <h2 class="ef-hero-tit" id="ef-q-tit">¿Tu proveedor está en la lista negra del SAT?</h2>
    <p class="ef-hero-txt">Escribe el RFC o el nombre. Buscamos en los <b>%(total)s</b> registros %(chip_of)s del listado oficial del artículo 69-B del Código Fiscal%(r_cff)s, con corte del SAT al <b>%(corte)s</b>%(r_sat)s.</p>

    <div class="ef-modos" role="group" aria-label="Cómo quieres buscar">
      <button type="button" class="ef-modo" data-modo="uno" aria-pressed="true">🔍 Uno por uno</button>
      <button type="button" class="ef-modo" data-modo="varios" aria-pressed="false">📋 Varios RFC a la vez</button>
    </div>

    <div class="ef-panel" id="efPanelUno">
      <form class="ef-busca" id="efForm" role="search" action="herramienta-inspector-efos.html" method="get">
        <label class="ef-lbl" for="efQ">RFC o nombre de la empresa o persona</label>
        <div class="ef-busca-fila">
          <input type="search" id="efQ" name="q" class="ef-input" autocomplete="off" autocapitalize="characters" spellcheck="false"
                 placeholder="p. ej. ABC123456XY0 o «consultoría integral»" aria-describedby="efAviso efEstado">
          <button type="submit" class="ef-btn">Buscar</button>
        </div>
      </form>
      <p class="ef-aviso" id="efAviso" aria-live="polite"></p>
      <div class="ef-filtros" id="efFiltros" role="group" aria-label="Filtrar los resultados por situación" hidden>
        <button type="button" class="ef-filtro" data-f="" aria-pressed="true">Todas</button>
        <button type="button" class="ef-filtro ef-def" data-f="F" aria-pressed="false">⛔ Definitivo</button>
        <button type="button" class="ef-filtro ef-pre" data-f="P" aria-pressed="false">⚠️ Presunto</button>
        <button type="button" class="ef-filtro ef-des" data-f="D" aria-pressed="false">✅ Desvirtuado</button>
        <button type="button" class="ef-filtro ef-sen" data-f="S" aria-pressed="false">⚖️ Sentencia favorable</button>
      </div>
      <div class="ef-res" id="efRes" aria-live="polite"></div>
      <button type="button" class="ef-btn ef-btn-sec" id="efCompartir" hidden>🔗 Copiar el enlace de esta búsqueda</button>
    </div>

    <div class="ef-panel" id="efPanelVarios" hidden>
      <label class="ef-lbl" for="efLista">Pega los RFC, uno por renglón (o separados por comas). Hasta 500.</label>
      <textarea id="efLista" class="ef-area" rows="6" spellcheck="false" autocapitalize="characters"
                placeholder="ABC123456XY0&#10;XYZ9901011A2&#10;…"></textarea>
      <div class="ef-busca-fila">
        <button type="button" class="ef-btn" id="efRevisar">Revisar la lista</button>
        <button type="button" class="ef-btn ef-btn-sec" id="efCopiar" hidden>📋 Copiar el resumen</button>
      </div>
      <div class="ef-lote" id="efLote" aria-live="polite"></div>
    </div>

    <p class="ef-estado" id="efEstado" role="status">La lista oficial (1.5 MB) se descarga sola en cuanto la página está lista; si no tienes JavaScript, consúltala en el %(fuente_sat)s.</p>
    <noscript><p class="ef-estado">Para buscar aquí hace falta JavaScript. Puedes descargar el %(fuente_csv)s del SAT.</p></noscript>
  </section>

  <section class="ef-sec" id="ef-corte" aria-labelledby="ef-corte-tit">
    <h2 class="ef-tit" id="ef-corte-tit">📊 Qué hay en la lista</h2>
    <p class="ef-txt">El listado del 69-B no es solo de culpables. Reúne cuatro situaciones, y <b>dos de ellas significan lo contrario de culpa</b>: quien demostró que sus operaciones sí existieron y quien ganó en tribunales. Toca una situación para buscar solo en ella.</p>
    <div class="ef-grandes">
      <div class="ef-grande ef-g-senal"><span class="ef-g-num">%(senal)s</span><span class="ef-g-tx">siguen señalados (definitivos + presuntos) %(chip_der)s</span></div>
      <div class="ef-grande ef-g-salio"><span class="ef-g-num">%(salio)s</span><span class="ef-g-tx">salieron de la presunción (desvirtuados + sentencia favorable) %(chip_der)s</span></div>
    </div>
    <div class="ef-barra" role="img" aria-label="Proporción por situación: definitivos %(pc_f)s %%, presuntos %(pc_p)s %%, desvirtuados %(pc_d)s %%, sentencia favorable %(pc_s)s %%">%(segs)s</div>
    <ul class="ef-sits">%(tarjetas)s</ul>
    <p class="ef-nota">Total y conteo por situación: %(chip_of)s SAT, listado completo del artículo 69-B, corte al %(corte)s (descargado por la plataforma el %(descarga)s; %(fuente_csv)s). Sumas y porcentajes: %(chip_der)s conteo por situación ÷ %(total)s registros × 100, a un decimal.</p>
  </section>

  <section class="ef-sec" id="ef-guia" aria-labelledby="ef-guia-tit">
    <h2 class="ef-tit" id="ef-guia-tit">🧭 Cómo usarlo en una auditoría ciudadana</h2>
    <ol class="ef-pasos">
      <li><span class="ef-paso-n" aria-hidden="true">1</span><div><h3>Consigue el RFC</h3><p>Viene en el contrato, en la factura o en %(comprasmx)s, la plataforma oficial de contrataciones que sustituyó a CompraNet en abril de 2025. El RFC es más preciso que el nombre: dos empresas pueden llamarse casi igual.</p></div></li>
      <li><span class="ef-paso-n" aria-hidden="true">2</span><div><h3>Búscalo aquí</h3><p><b>Definitivo</b> es la señal fuerte; <b>presunto</b> es una sospecha en curso; <b>desvirtuado</b> y <b>sentencia favorable</b> significan que el contribuyente salió de la lista. Si tienes muchos proveedores, usa «Varios RFC a la vez».</p></div></li>
      <li><span class="ef-paso-n" aria-hidden="true">3</span><div><h3>Pregunta formalmente</h3><p>Si un ente público le pagó a un proveedor definitivo, esa compra merece una pregunta formal: presenta una solicitud de información o acude a los canales de denuncia. En %(garantias)s te decimos a qué puerta tocar.</p></div></li>
    </ol>
    <p class="ef-legal"><span aria-hidden="true">⚖️</span> Aparecer en la lista es una <b>determinación administrativa del SAT, no una condena penal</b>. Y no aparecer no certifica a nadie: solo significa que el SAT no lo ha incluido al corte. Fuente: %(fuente_sat)s%(r_sat)s.</p>
  </section>

  <section class="ef-sec" aria-labelledby="ef-sig-tit">
    <h2 class="ef-tit" id="ef-sig-tit">➡️ Sigue la pista</h2>
    <ul class="ef-hermanas">
      <li><a href="herramienta-inspector-entes.html"><span aria-hidden="true">🏢</span><b>Auditor de entes públicos</b><small>Qué dependencia contrató y cuánto gastó.</small></a></li>
      <li><a href="herramienta-inspector-asf.html"><span aria-hidden="true">🏛️</span><b>Expedientes de casos de la ASF</b><small>Observaciones de la Auditoría Superior y de las demás autoridades.</small></a></li>
      <li><a href="expedientes.html"><span aria-hidden="true">📂</span><b>Expedientes de casos</b><small>Casos por aclarar, con sus documentos.</small></a></li>
      <li><a href="garantias.html"><span aria-hidden="true">🚪</span><b>Garantías cívicas</b><small>A qué puerta tocar para preguntar o denunciar.</small></a></li>
    </ul>
  </section>
</div>
''' % {
        'datos': _json(datos), 'total': n(total), 'corte': corte, 'r_sat': r_sat, 'r_cff': r_cff,
        'chip_of': chip('oficial'), 'chip_der': chip('derivado'),
        'senal': n(senal), 'salio': n(salio),
        'pc_f': pc(c['Definitivo']), 'pc_p': pc(c['Presunto']), 'pc_d': pc(c['Desvirtuado']),
        'pc_s': pc(c['Sentencia Favorable']),
        'segs': ''.join(segs), 'tarjetas': ''.join(tarjetas),
        'descarga': html.escape(m['descarga']), 'fuente_sat': fuente_sat, 'fuente_csv': fuente_csv,
        'comprasmx': ext(URL_COMPRASMX, 'ComprasMX'),
        'garantias': '<a href="garantias.html">Garantías cívicas</a>',
    })
