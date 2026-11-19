#!/usr/bin/env python3
"""Los servicios de Auditavisión, uno por uno, dentro del Auditor (19-11-2026).

Pedido del autor: que el chat «resuelva con maestría todo lo relacionado con
servicios». Hasta hoy el chat solo conocía la página de Servicios y una
respuesta, la de revisar a un proveedor (`serv_diligencia` de
territorio_modulos.py). Aquí cada servicio de `SERVICIOS` (apartados.py) tiene
su respuesta: qué es, qué recibes, para quién, cómo se cobra, con qué empezar
gratis hoy y su botón para cotizar, con el servicio ya elegido.

Reglas (AGENTS.md §0 quater y §2):
- **Nunca un monto**: se dice la forma de cobro de `COBRO`; las tarifas salen
  de los pilotos (monetizacion.py).
- **Nunca se dice que la plataforma evita el fraude ni que cumple por el
  cliente**: se repite `RIESGO_LIMITE`.
- Ningún texto del servicio se copia: se lee de apartados.py. Aquí solo viven
  cómo lo dice la gente (`ALIAS`) y con qué empezar gratis (`GRATIS`).

Lo lee asistente-charla.js dentro de D.san (claves `sv_<id>`, `sv_cobro`) y
los patrones de `ALIAS` en D.san.sva. **Un servicio nuevo necesita su renglón
en `ALIAS` y en `GRATIS`**, o la generación se detiene.
"""

import html
import os

import apartados as A

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cómo pide la gente cada servicio (texto ya sin acentos y en minúsculas; las
# expresiones valen igual en Python y en JavaScript: sin lookbehind).
ALIAS = {
    'diligencia': r'revision de (un |mi |una )?(proveedor|empresa|cliente)|ficha (de|del) proveedor|debida diligencia|conoce a tu cliente|\bkyc\b|lavado de dinero|antilavado|\bpld\b',
    'seguimiento': r'\bvigia\b|vigilar? (mi |mis |la |una )?(cartera|proveedores)|seguimiento periodico|monitoreo de proveedores|avis(o|en|ar)\w* (cuando|si) (un|mi) proveedor',
    'facturas': r'(revision|revisar|revisen|revisan) (de )?(mis |las |un lote de |cientos de )?(facturas|xml|cfdi)|facturas por lote|lote de facturas',
    # «Radiografía de la deuda de Jalisco» pide el dato, no el servicio.
    'radiografia': r'radiografia(?! (de|del) (la |las |los |el )?(deuda|gasto|presupuesto|inversion|ingreso|pobreza))',
    'temporada': r'licencia de temporada|temporada (para|de) (redaccion|redacciones|medios)|(redaccion|redacciones) (en|durante) (la )?campana',
    'entrega': r'entrega[ -]?recepcion|kit de entrega|gobierno (que|entrante) (entra|recibe)',
    'revision': r'revision documental|revision puntual',
    'expediente': r'expediente de investigacion|expediente a la medida|investigacion a la medida',
    # «La capacitación de la ASF» es de otra institución.
    'capacitacion': r'(talleres?|capacitacion|cursos? (de|para))(?! (de|del) (la )?(asf|sat|shcp|ine|scjn|gobierno))',
    'licencia': r'licencia de (las |sus )?herramientas|licenciar|usar (las|sus) herramientas en mi (institucion|dependencia|universidad)',
}

# Lo que se puede hacer gratis hoy, antes de contratar (archivo, texto). Cada
# archivo se coteja al generar.
GRATIS = {
    'diligencia': [('herramienta-inspector-efos.html', 'Busca su RFC en la lista 69-B del SAT'),
                   ('contratos-publicos.html', 'Sus contratos con el gobierno (ComprasMX)')],
    'seguimiento': [('herramienta-inspector-mia.html', 'Mi Auditavisión: tu cartera de proveedores, guardada en tu navegador')],
    'facturas': [('herramienta-inspector-factura.html', 'El lector de facturas: hasta 500 XML, sin subirlos')],
    'radiografia': [('planisferio.html', 'El Planisferio: tu estado y sus municipios en el mapa'),
                    ('herramienta-inspector-entes.html', 'El Auditor de entes: la salud financiera de tu municipio')],
    'temporada': [('herramienta-inspector-nota.html', 'Contrasta una nota contra el documento'),
                  ('noticias-seguimiento.html', 'La memoria de promesas')],
    'entrega': [('herramienta-inspector-entes.html', 'El Auditor de entes: el estado de cuenta de tu municipio'),
                ('planisferio.html', 'El Planisferio')],
    'revision': [('herramienta-inspector-nota.html', 'Contrasta una nota'),
                 ('enciclopedia-auditavision.html', 'La Enciclopedia')],
    'expediente': [('expedientes.html', 'Los expedientes de casos de la ASF'),
                   ('herramienta-inspector.html', 'El Modo Inspector')],
    'capacitacion': [('aprende-auditoria.html', 'Cómo se audita: control interno, riesgos y fraude'),
                     ('informes-documentar-para-sancionar.html', 'Las 20 matrices de la ASF')],
    'licencia': [('enciclopedia-auditavision.html', 'La Enciclopedia'),
                 ('herramienta-inspector.html', 'El Modo Inspector')],
}

# El fundamento que toca a cada servicio, cuando lo hay (ya cotejado en
# apartados.RIESGOS y en metodologia_auditoria.py).
CFF = {'tx': 'Código Fiscal de la Federación, art. 69-B', 'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CFF.pdf'}
LFPIORPI = {'tx': 'Ley Federal para la Prevención e Identificación de Operaciones con Recursos de Procedencia Ilícita, arts. 17 y 18',
            'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPIORPI.pdf'}
FUNDAMENTO = {
    'diligencia': [('Lista de contribuyentes con operaciones presuntamente inexistentes', CFF),
                   ('Identificar al cliente y a su beneficiario controlador en actividades vulnerables', LFPIORPI)],
    'seguimiento': [('Lista de contribuyentes con operaciones presuntamente inexistentes', CFF)],
    'facturas': [('Lista de contribuyentes con operaciones presuntamente inexistentes', CFF)],
}


# El compromiso de la política de independencia que el modo Periodista pone a
# la vista en cada familia, y lo que un encargo no es (modo Inspector). Se
# buscan por el principio de su título en apartados.INDEPENDENCIA.
IND_FAMILIA = {'electoral': 'En campaña', 'investigacion': 'Quien encarga', 'prevencion': 'Lo que no está en venta', 'formacion': 'Lo que no está en venta'}
IND_NO_ES = 'Es investigación documental'


def _ind(prefijo):
    x = [c for c in A.INDEPENDENCIA if c[0].startswith(prefijo)]
    if len(x) != 1:
        raise SystemExit('asistente_servicios.py: no encuentro en INDEPENDENCIA el compromiso «%s…»' % prefijo)
    return list(x[0])


def _esc(t):
    return html.escape(t, quote=False)


def _cotiza(i):
    return '%s?servicio=%s#solicitud' % (A.SV_COTIZA, i)


def temas():
    serv = {s[0]: s for s in A.SERVICIOS}
    fam = {x[0]: x for x in A.LINEAS}
    if set(fam) - set(IND_FAMILIA):
        raise SystemExit('asistente_servicios.py: estas familias no tienen su compromiso en IND_FAMILIA: %s' % ', '.join(sorted(set(fam) - set(IND_FAMILIA))))
    faltan = sorted(set(serv) - set(ALIAS)) + sorted(set(serv) - set(GRATIS)) + sorted(set(serv) - set(A.COBRO))
    if faltan:
        raise SystemExit('asistente_servicios.py: estos servicios no tienen su renglón en ALIAS, GRATIS o COBRO: %s' % ', '.join(faltan))
    for i, gs in GRATIS.items():
        for f, _t in gs:
            if not os.path.exists(os.path.join(RAIZ, f.split('#')[0])):
                raise SystemExit('asistente_servicios.py: la liga gratuita de «%s» no existe: %s' % (i, f))
    # Quién puede pedirlo hoy: SERVICIOS_OPERAN de apartados.py (19-11-2026).
    abre = ('Ya opera para quien tiene un código de acceso vigente: arma tu solicitud, '
            've cómo queda y envíala; te respondemos por escrito.') if A.SERVICIOS_OPERAN else \
        'Los servicios se abren con el lanzamiento: ya puedes armar tu solicitud y ver cómo queda antes de mandarla.'
    t = {}
    for i, (_, ico, nom, que, recibe, quien, linea) in serv.items():
        perfiles = [p[1] for p in A.PERFILES if i in p[4]]
        h = ('<p><span aria-hidden="true">%s</span> <b>%s</b> es un servicio de la familia «%s». %s</p><ul>'
             '<li><b>Qué recibes:</b> %s</li><li><b>Para quién:</b> %s</li>'
             '<li><b>Cómo se cobra:</b> %s. No damos un monto en el chat: las tarifas salen de los pilotos y se dicen por escrito, antes de empezar.</li>'
             '%s</ul>'
             '<p><b>Empieza gratis, hoy:</b> %s.</p>'
             '<p>%s <a href="%s">Cotiza este servicio</a>, con el servicio ya elegido.</p>'
             '<p class="pa-chico">%s</p>') % (
            ico, _esc(nom), _esc(fam[linea][2]), _esc(que), _esc(recibe), _esc(quien), _esc(A.COBRO[i]),
            ('<li><b>Lo piden sobre todo:</b> %s.</li>' % _esc(', '.join(perfiles))) if perfiles else '',
            '; '.join('<a href="%s">%s</a>' % (f, _esc(x)) for f, x in GRATIS[i]),
            _esc(abre), _cotiza(i), _esc(A.RIESGO_LIMITE))
        t['sv_' + i] = {
            'tit': nom, 'h': h, 'ci': [],
            'fu': [{'que': q, 'e': 'oficial', 'fu': f} for q, f in FUNDAMENTO.get(i, [])],
            'sug': ['¿Cómo se cobra cada servicio?', '¿Qué servicios ofrece Auditavisión?', GRATIS[i][0][1]],
            'ir': ['%s#sv-%s' % (A.SV_CATALOGO, i), nom],
            # Para la capa de cada modo (asistente.js, svCapa()): la familia y lo gratis.
            'fam': linea, 'gr': [list(g) for g in GRATIS[i]], 'ind': _ind(IND_FAMILIA[linea]), 'noes': _ind(IND_NO_ES)}
    # «¿Cuánto cuestan sus servicios?»: la forma de cobro de todos, sin montos.
    filas = ''.join('<li><span aria-hidden="true">%s</span> <b>%s:</b> %s.</li>' % (s[1], _esc(s[2]), _esc(A.COBRO[s[0]])) for s in A.SERVICIOS)
    t['sv_cobro'] = {
        'tit': 'Cómo se cobra cada servicio',
        'h': ('<p>Lo público es gratis, siempre: la consulta, buscar un RFC en la lista 69-B, leer una factura y el dictamen. '
              'Se cobra que una persona investigue, revise o enseñe por ti, que guardemos tu cartera o que te avisemos. Así se cobra cada servicio:</p>'
              '<ul>%s</ul><p><b>No damos montos todavía:</b> las tarifas salen de los pilotos y te las damos por escrito, antes de empezar. %s</p>') % (filas, _esc(abre)),
        'ci': [], 'fu': [],
        'sug': ['¿Qué servicios ofrece Auditavisión?', '¿Cómo se sostiene Auditavisión?', 'Quiero una radiografía de mi municipio'],
        'ir': ['servicios-como-se-cobra.html', 'Cómo se cobra cada servicio']}
    return t


def alias():
    """Los patrones que lee asistente-charla.js (D.san.sva): clave del tema → expresión."""
    return {'sv_' + i: p for i, p in ALIAS.items()}


if __name__ == '__main__':
    import re
    T = temas()
    for k, p in alias().items():
        re.compile(p)
    print('asistente_servicios.py: %d temas (%s)' % (len(T), ', '.join(sorted(T))))
