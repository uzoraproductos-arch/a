# -*- coding: utf-8 -*-
"""Octava aplicación del Modo Inspector: «Lector de facturas CFDI»
(encargo del autor, 05-11-2026: «implementar en la plataforma el código que
lee una factura… y cruzarla contra la lista 69-B»).

La página la escribe este módulo (apartados.insp_nativa(), clave
'inspfactura') y la hace funcionar assets/auditor/js/insp-factura.js, que
lee los XML **en el navegador** con DOMParser: la factura no se sube a ningún
lado ni se guarda, porque trae datos personales (el RFC de una persona
física). La versión de Python, para despachos y para aprender, es
herramientas/lector_cfdi.py, con las mismas reglas.

Regla de la plataforma (AGENTS.md §2): lo que dice la lista 69-B es
«oficial» (situación, oficio y fecha que publicó el SAT); lo que sale de
comparar la fecha de la factura con esas publicaciones, o de rehacer su
cuenta, es «derivado» y se rotula «señal para revisar», nunca
«irregularidad». Desvirtuado y sentencia favorable se dicen como lo que son:
a favor del contribuyente.
"""
import html
import json

import insp_efos
from presupuesto_modulos import chip

ESTILOS = ['insp-efos.css', 'insp-factura.css']
SCRIPTS = ['insp-factura.js']

ANEXO20 = 'http://omawww.sat.gob.mx/tramitesyservicios/Paginas/anexo_20.htm'
XSD40 = 'http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd'
CFF = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CFF.pdf'
CFF_REFORMA = '09-04-2026'   # última reforma del CFF en el índice de Diputados (cotejo del 05-11-2026)

# Lo que dice el art. 69-B del CFF (texto vigente, cotejado el 05-11-2026),
# en sencillo y con su párrafo. Lo leen la página y el chat.
LEY = [
    ('Primer párrafo', 'Si el SAT detecta que alguien factura sin activos, personal, infraestructura o capacidad material para dar lo que factura, '
     'o que no está localizable, presume que esas operaciones no existieron.'),
    ('Segundo párrafo', 'Se lo notifica por buzón tributario y lo publica en la página del SAT y en el DOF: es el listado de «presuntos». '
     'Tiene quince días para desvirtuarlo.'),
    ('Cuarto párrafo', 'Si no lo desvirtúa, el SAT lo publica en el listado de «definitivos», nunca antes de treinta días después de notificarle la resolución.'),
    ('Quinto párrafo', 'Publicado como definitivo, las operaciones de sus comprobantes «no producen ni produjeron efecto fiscal alguno», con efectos generales: '
     'también las facturas anteriores a la publicación.'),
    ('Sexto párrafo', 'El SAT también publica, cada trimestre, a quienes desvirtuaron o ganaron una sentencia firme: salen de la presunción.'),
    ('Octavo párrafo', 'Quien dio efecto fiscal a esas facturas tiene treinta días tras la publicación del definitivo para acreditar que sí recibió el bien o el '
     'servicio, o para corregir su situación con declaraciones complementarias.'),
]

PASOS = [
    ('📂', 'Elige tus XML', 'Uno o varios a la vez (así trabaja un despacho). También puedes arrastrarlos o pegar el texto de uno.'),
    ('🔎', 'Los leemos aquí mismo', 'En tu navegador: el UUID del timbre, la fecha, el emisor, el receptor, los conceptos, los impuestos y el total.'),
    ('🧮', 'Rehacemos la cuenta', 'Subtotal menos descuento, más impuestos trasladados, menos retenidos: ¿da el total? ¿Los conceptos suman el subtotal?'),
    ('🧾', 'La cruzamos con la lista 69-B', 'Si el emisor aparece, te decimos lo que publicó el SAT y, aparte, las señales que salen de comparar fechas.'),
]


def _ext(url, texto):
    return '<a href="%s" target="_blank" rel="noopener">%s ↗</a>' % (html.escape(url), texto)


def bot():
    """Lo que el chat necesita saber de la aplicación (asistente.py)."""
    return {'ley': [{'p': p, 't': t} for p, t in LEY], 'cff': CFF, 'reforma': CFF_REFORMA}


def construir(base, ref):
    m = insp_efos.meta()
    sit = {k: {'t': (nom if k != 'S' else 'Sentencia favorable'), 'c': cl, 'i': ico, 'corto': corto}
           for k, nom, cl, ico, corto, _txt in insp_efos.SITUACIONES}
    datos = {'corte': m['corte'], 'total': m['total'], 'sit': sit, 'cff': CFF}
    pasos = ''.join('<li class="cf-paso"><span class="cf-paso-ico" aria-hidden="true">%s</span><b>%s</b><p>%s</p></li>' % p for p in PASOS)
    ley = ''.join('<li><b>%s.</b> %s</li>' % (html.escape(p), html.escape(t)) for p, t in LEY)
    return '''
<div class="ef cf" id="cf">
  <script type="application/json" id="cfDatos">%(datos)s</script>

  <section class="ef-hero" aria-labelledby="cf-tit">
    <h2 class="ef-hero-tit" id="cf-tit">¿Esta factura es de una empresa en la lista negra del SAT?</h2>
    <p class="ef-hero-txt">Elige el XML de una factura electrónica (CFDI 4.0, o 3.3 si es anterior a 2022). La leemos, rehacemos su cuenta y cruzamos al emisor con los <b>%(total)s</b> registros %(chip_of)s del listado del artículo 69-B del Código Fiscal%(r_cff)s, con corte del SAT al <b>%(corte)s</b>%(r_sat)s.</p>
    <p class="cf-privado" id="cfPrivado">🔒 <b>Tu factura no sale de tu equipo.</b> Se lee aquí, en tu navegador: no la subimos a ningún servidor ni la guardamos. Al cerrar la página, se borra.</p>

    <div class="cf-entrada">
      <label class="ef-lbl" for="cfArchivos">Tus facturas en XML (puedes elegir varias)</label>
      <div class="cf-suelta" id="cfSuelta">
        <input type="file" id="cfArchivos" class="cf-archivo" accept=".xml,text/xml,application/xml" multiple>
        <p>o arrástralas aquí</p>
      </div>
      <details class="cf-pegar">
        <summary>¿Solo tienes el texto? Pega el XML</summary>
        <label class="ef-lbl" for="cfTexto">El contenido del XML</label>
        <textarea id="cfTexto" class="ef-area" rows="6" spellcheck="false" placeholder="&lt;cfdi:Comprobante …"></textarea>
        <button type="button" class="ef-btn" id="cfLeerTexto">Leer este XML</button>
      </details>
      <p><button type="button" class="ef-btn ef-btn-sec" id="cfEjemplo">🧪 Probar con una factura ficticia</button></p>
    </div>

    <p class="ef-estado" id="cfEstado" role="status">La lista 69-B (1.9 MB) se descarga cuando eliges tu primera factura.</p>
    <noscript><p class="ef-estado">Para leer facturas aquí hace falta JavaScript. Si sabes Python, la misma revisión está en herramientas/lector_cfdi.py del repositorio.</p></noscript>
    <div class="cf-res" id="cfRes" aria-live="polite"></div>
    <div class="ef-busca-fila" id="cfAcciones" hidden>
      <button type="button" class="ef-btn" id="cfCsv">⬇️ Descargar la tabla (CSV)</button>
      <button type="button" class="ef-btn ef-btn-sec" id="cfLimpiar">🗑️ Borrar todo</button>
    </div>
  </section>

  <section class="ef-sec" aria-labelledby="cf-como">
    <h2 id="cf-como">Cómo funciona</h2>
    <ol class="cf-pasos">%(pasos)s</ol>
  </section>

  <section class="ef-sec" aria-labelledby="cf-separa">
    <h2 id="cf-separa">Lo que dice el SAT y lo que nosotros señalamos</h2>
    <ul class="cf-dos">
      <li><p class="cf-dos-t">%(chip_of)s Lo que declaró la autoridad</p><p>Si el RFC del emisor está en la lista 69-B: su situación (presunto, definitivo, desvirtuado o sentencia favorable), el oficio y la fecha en que el SAT lo publicó. Es lo que dice el listado, palabra por palabra.</p></li>
      <li><p class="cf-dos-t">%(chip_de)s Señales para revisar</p><p>Lo que sale de comparar: la factura se emitió <b>después</b> de que el emisor salió publicado como presunto o como definitivo, o su cuenta no cuadra. Es una pregunta que conviene hacer, <b>no una irregularidad</b> ni una acusación.</p></li>
      <li><p class="cf-dos-t">✅ A favor del contribuyente</p><p>Desvirtuado y sentencia favorable quieren decir lo contrario de una sospecha: demostró ante el SAT que sus operaciones existieron, o un tribunal le dio la razón.</p></li>
    </ul>
  </section>

  <section class="ef-sec" aria-labelledby="cf-ley">
    <h2 id="cf-ley">Lo que dice el artículo 69-B del Código Fiscal</h2>
    <p>En sencillo, párrafo por párrafo (texto vigente, última reforma DOF %(reforma)s; %(cff)s).</p>
    <ul class="leg-ciegos">%(ley)s</ul>
  </section>

  <section class="ef-sec" aria-labelledby="cf-no">
    <h2 id="cf-no">Lo que esta aplicación no dice</h2>
    <ul>
      <li><b>No dice si la factura está vigente o cancelada.</b> Eso solo lo sabe el SAT: consúltalo con el UUID en su verificador de comprobantes fiscales digitales.</li>
      <li><b>No valida el sello ni el certificado.</b> Leemos lo que el XML dice; un archivo alterado a mano se leería igual. La estructura del CFDI la fija el %(anexo)s (%(xsd)s).</li>
      <li><b>No califica al receptor</b> ni dice si la operación existió: eso se acredita ante el SAT con documentos (art. 69-B, octavo párrafo).</li>
      <li>La lista tiene corte al %(corte)s. Alguien que el SAT publicó después no aparece todavía.</li>
      <li>Si el emisor o el receptor es persona física, su RFC sale tapado y su nombre no se muestra: es un dato personal.</li>
    </ul>
  </section>
</div>''' % {
        'datos': json.dumps(datos, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'),
        'total': format(m['total'], ','), 'corte': html.escape(m['corte']), 'chip_of': chip('oficial'), 'chip_de': chip('derivado'),
        'r_cff': ref('ref-cff'), 'r_sat': ref('ref-sat-69b'), 'pasos': pasos, 'ley': ley, 'reforma': CFF_REFORMA,
        'cff': _ext(CFF, 'Cámara de Diputados'), 'anexo': _ext(ANEXO20, 'Anexo 20 del SAT'), 'xsd': _ext(XSD40, 'esquema del CFDI 4.0'),
    }
