# -*- coding: utf-8 -*-
"""La página de venta del Vigía de proveedores, dentro de servicio-seguimiento.html
(texto aprobado por el autor el 22-11-2026: docs/BORRADOR-VIGIA-PROVEEDORES.md).

Se publica junto con el aviso del tablero (Mi Auditavisión, insp-mia.js), que
era la condición del borrador (§8): primero el tablero, el correo después.

Reglas (AGENTS.md §2 y §0 quater): **ninguna cifra se escribe aquí**. La ventana
entre presunto y definitivo la calcula `vigia_historial.ventana()` con las
columnas del SAT de `sat-69b.js` (derivado); la cita del art. 69-B es literal
del CFF cotejado (investigaciones/leyes/CFF.pdf, huella `CFF_HUELLA`). Nunca un
monto; el ejemplo es ficticio y lo dice; una coincidencia es una señal para
revisar, nunca una acusación; el Vigía no evita el fraude ni cumple por nadie.
"""
import hashlib
import os

import vigia_historial
from presupuesto_modulos import chip

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFF = os.path.join(RAIZ, 'investigaciones', 'leyes', 'CFF.pdf')
CFF_HUELLA = 'be7427b20d3552775ab42018f8f87578078770095bf8cf46322c25e36ee3aa7d'
# Párrafo quinto del art. 69-B, literal (cotejado el 22-11-2026, última reforma DOF 09-04-2026).
CITA_QUINTO = ('las operaciones contenidas en los comprobantes fiscales expedidos por el contribuyente en cuestión '
               'no producen ni produjeron efecto fiscal alguno')
COTIZA = 'servicios-cotiza.html?servicio=seguimiento#solicitud'


def revisar():
    """Si el CFF del repositorio cambia, la cita se vuelve a cotejar antes de publicarse."""
    if os.path.exists(CFF):
        h = hashlib.sha256(open(CFF, 'rb').read()).hexdigest()
        if h != CFF_HUELLA:
            raise SystemExit('vigia_venta: investigaciones/leyes/CFF.pdf cambió (huella %s…): vuelve a cotejar la cita del art. 69-B '
                             'y cambia CFF_HUELLA' % h[:12])


def _n(v):
    return format(v, ',')


def secciones():
    revisar()
    meta, regs = vigia_historial.copia()
    v = vigia_historial.ventana(regs)
    med = format(v['mediana'], 'g')
    of, de = chip('oficial'), chip('derivado')
    hero = '''<div class="sv-vigia">
          <p class="sv-vigia-tit"><span aria-hidden="true">📡</span> <b>Entérate antes de que tu proveedor sea definitivo</b></p>
          <p>El SAT publica a las empresas que presume que facturan operaciones que no existieron. Desde ese día y hasta que las vuelve
          definitivas pasan, en la mitad de los casos, <b>%(med)s días o más</b> %(de)s (la cuenta está abajo). El Vigía revisa tu lista de
          proveedores contra cada corte y te avisa el mismo día que lo ve, con el documento.</p>
          <div class="sv-fx-acc"><a class="sz-btn sz-btn-of" href="%(cotiza)s">📝 Cotiza tu Vigía</a>
          <a class="sz-btn" href="herramienta-inspector-mia.html">📌 Pruébalo gratis en tu tablero</a>
          <a class="sz-btn" href="herramienta-inspector-efos.html">🔍 Busca un RFC en la 69-B</a></div>
          <p class="sv-nota">La cotización te da la forma de cobro, nunca un monto publicado: es una suscripción mensual según cuántos RFC vigilas.</p>
        </div>''' % {'med': med, 'de': de, 'cotiza': COTIZA}
    problema = '''<p>Cuando el SAT publica a una empresa como <b>definitiva</b>, se considera, con efectos generales, que «%(cita)s»
        (Código Fiscal de la Federación, art. 69-B, párrafo quinto) %(of)s. Quien les dio efecto fiscal cuenta con treinta días siguientes a la
        publicación para acreditar que sí recibió los bienes o servicios, o para corregir su situación fiscal (párrafo octavo) %(of)s.
        Enterarse tarde cuesta tiempo y papeles.</p>
        <p class="sv-nota">Cita cotejada contra el CFF de la Cámara de Diputados, última reforma DOF 09-04-2026 (huella <code>%(h)s…</code>).</p>''' % {
        'cita': CITA_QUINTO, 'of': of, 'h': CFF_HUELLA[:12]}
    cifra = '''<div class="sv-tabla-env"><table class="sv-tabla">
          <thead><tr><th scope="col">Qué</th><th scope="col">Cifra</th><th scope="col">Estado</th><th scope="col">De dónde sale</th></tr></thead>
          <tbody>
          <tr><th scope="row">Personas morales de la lista con fecha de presunto y de definitivo</th><td>%(n)s</td><td>%(de)s</td>
          <td>Columnas «fecha de publicación como presunto» y «como definitivo» del listado completo del SAT, corte al %(corte)s (huella <code>%(sha)s…</code>). Se dejan fuera las celdas que el SAT no escribió como fecha.</td></tr>
          <tr><th scope="row">Días entre una y otra, mediana</th><td>%(med)s</td><td>%(de)s</td><td>Definitivo − presunto, por empresa; la mitad tardó %(med)s o más.</td></tr>
          <tr><th scope="row">La mitad central</th><td>de %(p25)s a %(p75)s días</td><td>%(de)s</td><td>Primer y tercer cuartil.</td></tr>
          </tbody></table></div>
        <p><b>Lo que esta cifra no dice:</b> no es un plazo de la ley ni una promesa de que habrá ese tiempo; es lo que pasó con las empresas
        que ya están en la lista. Cada caso tiene sus fechas.</p>''' % {
        'n': _n(v['n']), 'med': med, 'p25': v['p25'], 'p75': v['p75'], 'de': de, 'corte': meta['corte'], 'sha': meta['sha256'][:12]}
    pasos = '''<ol class="sv-lista">
          <li><b>Nos das tu lista de RFC.</b> Un CSV, un TXT o lo pegas de Excel. Hoy mismo, gratis, la guardas en tu tablero
          (<a href="herramienta-inspector-mia.html">Mi Auditavisión</a>, solo en tu navegador). Las personas físicas no se publican: de ellas solo se
          dice si su RFC coincide.</li>
          <li><b>Cada corte del SAT, la comparamos.</b> El flujo semanal «Base al día» baja la 69-B, la cuadra y anota en el historial del Vigía
          cada alta y cada cambio de situación con el día en que lo vio (<a href="base-al-dia.html">qué fuente se actualiza y cuándo</a>).</li>
          <li><b>Te avisamos con el documento.</b> Qué cambió (presunto, definitivo, desvirtuado, sentencia favorable), el oficio del SAT, la fecha
          y su liga. Qué hacer con tu proveedor lo decides tú.</li>
        </ol>
        <p class="sv-nota">Hoy el aviso vive en tu tablero: al abrirlo, compara tu lista con el corte más nuevo y te dice lo que cambió desde tu
        última visita. El aviso por correo es la segunda entrega y llegará con su aviso de privacidad.</p>'''
    ejemplo = '''<p class="sv-limite"><span aria-hidden="true">⚠️</span> <b>Todo en este ejemplo es inventado</b>: la empresa, su RFC y las fechas.
        No corresponde a ningún contribuyente. Así se vería un aviso real.</p>
        <div class="sv-tabla-env"><table class="sv-tabla">
          <thead><tr><th scope="col">Paso</th><th scope="col">Día (ficticio)</th><th scope="col">Qué pasa</th><th scope="col">Qué recibe el cliente</th></tr></thead>
          <tbody>
          <tr><td>1</td><td>3 de febrero</td><td>«Comercializadora Ejemplo, S.A. de C.V.» (RFC de ejemplo <code>CEJ000000XX0</code>) entra a la lista de tus proveedores vigilados.</td><td>Confirmación: 1 RFC vigilado, sin coincidencias hoy.</td></tr>
          <tr><td>2</td><td>12 de marzo</td><td>El SAT publica un corte nuevo y la empresa aparece como <b>presunta</b>.</td><td><b>Aviso del Vigía:</b> «Tu proveedor CEJ000000XX0 aparece como presunto en el corte del SAT. Oficio …, fecha …, liga al DOF. Una presunción no es una condena: la empresa puede desvirtuarla.»</td></tr>
          <tr><td>3</td><td>12 de marzo</td><td>El historial guarda: <code>[12-mar, P, alta]</code>.</td><td>Su dictamen con folio y huella, para su expediente de control interno.</td></tr>
          <tr><td>4</td><td>De marzo a septiembre</td><td>Cada corte se vuelve a comparar; mientras no cambie, no hay aviso nuevo.</td><td>Nada: el Vigía no hace ruido.</td></tr>
          <tr><td>5</td><td>8 de octubre</td><td>El SAT la vuelve <b>definitiva</b>.</td><td><b>Segundo aviso:</b> el cambio de situación, con los párrafos quinto y octavo del art. 69-B (los treinta días) y la liga. El historial guarda <code>[8-oct, F, cambio]</code>.</td></tr>
          <tr><td>6</td><td>Cuando lo pida</td><td></td><td><b>La prueba del aviso previo:</b> el cliente supo <b>210 días antes</b> de que fuera definitiva (8-oct − 12-mar, ficticio) %(de)s, con las dos fechas en el historial.</td></tr>
          </tbody></table></div>
        <p>Si en el paso 5 la empresa hubiera <b>desvirtuado</b> la presunción, el segundo aviso lo diría igual: el Vigía avisa lo que cambió, no lo califica.</p>''' % {'de': de}
    es = '''<ul class="sv-lista">
          <li><b>Es</b> una comparación por RFC contra la lista oficial del SAT, cada corte, con fecha y documento.</li>
          <li><b>No es</b> una acusación ni una calificación del proveedor: una coincidencia es una señal para revisar.</li>
          <li><b>No evita</b> el fraude ni cumple tus obligaciones por ti; tampoco sustituye la revisión de tu contador.</li>
          <li><b>No guarda</b> tus facturas ni el nombre de personas físicas. La lista se queda contigo; el aviso dice el RFC que tú registraste.</li>
        </ul>'''
    faq = [
        ('¿Cuánto cuesta?', 'Es una suscripción mensual según cuántos RFC vigilas. La cotización te da la forma de cobro; no publicamos montos mientras no haya pilotos.'),
        ('¿Qué tan rápido avisa?', 'El día que el flujo semanal integra el corte nuevo del SAT (los miércoles). El SAT publica su listado completo sin calendario fijo.'),
        ('¿Puedo comprobar que me avisaron antes?', 'Sí: el historial guarda el día en que la plataforma vio cada situación, y no se reescribe hacia atrás. Lo que ya '
         'estaba en la lista cuando empezó el registro (%s) va como «semilla»: de eso no presumimos aviso previo.' % _dmy(vigia_historial_inicio())),
        ('¿Y las otras listas?', 'El Vigía empieza por la 69-B. Las del art. 69, 17-H Bis y 69-B Bis, Sancionados, la OFAC y la ONU ya se revisan en '
         '<a href="herramienta-inspector-padron.html">«Revisa a tu contraparte»</a>; sumarlas al aviso es la siguiente entrega.'),
    ]
    preguntas = '\n'.join('        <details class="sv-faq"><summary>%s</summary><p>%s</p></details>' % q for q in faq)
    sec = lambda i, t, pre, tx, b: {'id': i, 'titulo': t, 'pre': pre, 'texto': tx, 'tarjetas': [], 'bloque': b}
    return [
        sec('vigia', 'El Vigía de proveedores', 'Avisa a tiempo', 'Tu lista de proveedores contra cada corte de la lista 69-B del SAT.', hero),
        sec('vigia-problema', 'El problema, en una línea', 'Lo que dice la ley', 'Lo que pasa cuando un proveedor tuyo queda como definitivo.', problema),
        sec('vigia-cifra', 'Por qué el aviso a tiempo vale', 'La cifra, con su cuenta', 'Cuánto tarda el SAT entre presumir y volver definitiva a una empresa.', cifra),
        sec('vigia-pasos', 'Cómo funciona, en tres pasos', 'Paso a paso', 'De tu lista al aviso, con el documento.', pasos),
        sec('vigia-ejemplo', 'Un ejemplo ficticio, paso a paso', 'Así se ve', 'Cómo se vería un aviso real, con todo inventado.', ejemplo),
        sec('vigia-es', 'Lo que el Vigía es y no es', 'Sus límites', 'Para que sepas qué esperar.', es),
        sec('vigia-preguntas', 'Preguntas frecuentes', 'Dudas', 'Lo que más nos preguntan del Vigía.', preguntas),
    ]


def vigia_historial_inicio():
    import json
    h = json.load(open(vigia_historial.SALIDA, encoding='utf-8'))
    return h['cortes'][0]['visto']


def _dmy(iso):
    a, m, d = iso.split('-')
    return '%s-%s-%s' % (d, m, a)
