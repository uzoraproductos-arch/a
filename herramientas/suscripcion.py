#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El Modo Inspector y los Servicios, con la misma regla de lo que se paga
(pedido del autor, 04-11-2026: «homologar un poco el modo inspector con los
servicios que tenemos en el sentido de un posible desbloqueo mediante
suscripción de los usuarios»).

Una sola tabla, APPS, dice para cada aplicación del Modo Inspector:
  - lo que es **gratis siempre** (la consulta);
  - lo que **desbloquearía la suscripción**, y de qué tipo es;
  - qué **Servicio** de servicios.html lleva el caso más a fondo (por encargo).
La leen la página del Modo Inspector (#suscripcion), cada aplicación (la
franja «🔓 Gratis y con suscripción» al pie), Servicios (#suscripcion) y el
chat (tema serv_suscripcion de D.san). Nunca se copia: se cambia aquí.

La regla es la de docs/LANZAMIENTO.md §4.4 y la política de independencia
(INDEPENDENCIA de apartados.py): **la información pública nunca se cobra**.
Solo puede desbloquearse con suscripción lo que es trabajo nuevo de la
plataforma, de cuatro tipos (TIPOS): la memoria (guardar y comparar), el aviso
(que te llegue cuando cambia), el cómputo (una consulta con IA, que cuesta
cada vez) y la descarga institucional. Consultar, el chat, las fichas, su PDF,
el estado de cuenta cívico, el dictamen y verificar un folio se quedan
gratis. Si un renglón nuevo pone en «desbloquea» algo que hoy es gratis, se
está rompiendo esa promesa: no se hace.

ABIERTA es el interruptor. Mientras sea False, todo lo de suscripción dice
«Próximamente» y su botón lleva a dejar el aviso en Servicios. Prenderlo no
basta para cobrar: hacen falta las cuentas, la pasarela y la tabla
`suscripciones` (fase 5 de docs/LANZAMIENTO.md), y el candado de acceso.js
solo cierra en el navegador. El precio no se escribe aquí hasta que salga de
los encargos piloto (LANZAMIENTO §4.4): no se inventa.
"""
import html

# False = la suscripción aún no se abre: se anuncia, no se cobra.
ABIERTA = False

# Los tres niveles, en el orden en que se presentan.
NIVELES = [
    ('gratis', '🎁', 'Consulta', 'Gratis, siempre',
     'Todo lo que la plataforma publica: buscar, leer, comparar, el chat, las fichas con su PDF, el dictamen y verificar un folio. '
     'Ningún dato público se esconde detrás de un pago.'),
    ('suscripcion', '🔓', 'Suscripción', 'Próximamente',
     'Lo que la plataforma haría de más por ti: recordar lo que sigues, avisarte cuando cambia, redactar a fondo con IA y '
     'descargar para tu institución. El precio saldrá de los encargos piloto; no lo vamos a inventar.'),
    ('encargo', '🧾', 'Encargo', 'Se cotiza',
     'Una investigación a la medida, hecha por personas, con la misma regla de la plataforma. Se cotiza por escrito antes de empezar.'),
]

# Lo único que puede desbloquearse (LANZAMIENTO §4.4: se paga el trabajo,
# la memoria, el aviso o el cómputo; el trabajo es el encargo).
TIPOS = {
    'aviso': ('🔔', 'Aviso'),
    'memoria': ('🗂️', 'Memoria'),
    'computo': ('🤖', 'Cómputo con IA'),
    'descarga': ('📥', 'Descarga institucional'),
}

# clave de la aplicación (HERRAMIENTAS de apartados.py) →
#   gratis: lo que ya hace y se queda gratis;
#   desbloquea: [(tipo, qué)]; vacío = no hay nada que cobrar, y se dice;
#   encargo: ids de SERVICIOS (apartados.py) que la llevan más a fondo;
#   nota: por qué no se desbloquea nada, cuando así es.
APPS = {
    'inspasf': {
        'gratis': ['Los expedientes y los montos por aclarar de la ASF', 'El buscador de casos y de autoridades que fiscalizan',
                   'La ficha de cada caso, con su documento'],
        'desbloquea': [('aviso', 'Un aviso cuando la ASF publique una entrega de tu estado o de un ente que sigues'),
                       ('memoria', 'Guardar expedientes y ver qué cambió de una entrega a otra')],
        'encargo': ['expediente', 'seguimiento'],
    },
    'inspentes': {
        'gratis': ['El diagnóstico de cualquier autoridad federal, estatal o municipal', 'Su estado de cuenta y su salud financiera, con PDF y folio',
                   'El radar de cada estado frente a los 32'],
        'desbloquea': [('aviso', 'Un aviso cuando cambie el diagnóstico de un ente que sigues'),
                       ('memoria', 'Un resumen mensual de lo que cambió en tu estado y tu municipio')],
        'encargo': ['seguimiento', 'expediente'],
    },
    'inspnota': {
        'gratis': ['Contrastar cualquier nota, cifra por cifra, contra el documento oficial', 'El veredicto y los puntos ciegos de la nota'],
        'desbloquea': [('computo', 'Consultas a fondo redactadas con IA, con su dictamen (cada una cuesta cómputo)'),
                       ('memoria', 'Guardar las notas que contrastaste y volver a ellas')],
        'encargo': ['revision'],
    },
    'inspefos': {
        'gratis': ['Buscar por RFC o por nombre en la lista 69-B del SAT', 'Su situación, su fecha y su oficio en el DOF'],
        'desbloquea': [('aviso', 'Tu lista de proveedores vigilados, con aviso si uno entra a la lista, cambia de situación o sale')],
        'encargo': ['diligencia'],
    },
    'inspcruce': {
        'gratis': ['Los hallazgos, los antecedentes y la tabla año por año', 'El método y las fuentes de cada cifra'],
        'desbloquea': [('aviso', 'Un aviso cuando una empresa que vigilas firme un contrato o cambie su situación en la lista 69-B'),
                       ('descarga', 'El cruce completo en CSV, con su folio, para tu institución')],
        'encargo': ['diligencia', 'expediente'],
    },
    'inspverifica': {
        'gratis': ['Comprobar el folio o la huella de cualquier estado de cuenta de Auditavisión'],
        'desbloquea': [],
        'nota': 'Verificar nunca se cobra: es la garantía de que lo que circula con nuestro nombre no se alteró.',
        'encargo': [],
    },
    'inspnepotismo': {
        'gratis': ['La calculadora de parentesco y el árbol de grados', 'Qué ley alcanza a cada parentesco y cómo se investiga un cargo'],
        'desbloquea': [],
        'nota': 'Todo aquí es consulta de la ley: no hay nada que desbloquear.',
        'encargo': ['expediente', 'capacitacion'],
    },
}

SERVICIOS_PAG = 'servicios.html'
ANCLA = 'suscripcion'
CHAT_PAG = 'herramienta-inspector-pregunta.html'

# Las tres puertas de cada aplicación (pedido del autor, 04-11-2026: «una
# verificación, análisis y comparativa respecto al modo inspector del
# auditor… la herramienta… y la pestaña de servicios… homologar o vincular
# todas esas partes»): su página en la herramienta, cómo se le pide al chat
# en modo Inspector y su Servicio. Cada pregunta de aquí está en
# preguntas_auditor.json con «modo»: «inspector» y debe llevar a la página
# de la aplicación: si el chat deja de abrirla, prueba_auditor.py falla.
# (pregunta de ejemplo, qué hace el chat con ella)
CHAT = {
    'inspasf': ('Expedientes de casos de la ASF', 'Abre la aplicación dentro de la respuesta'),
    'inspentes': ('Diagnóstico de Pemex', 'Abre el diagnóstico del ente dentro de la respuesta'),
    'inspnota': ('Contrasta una nota', 'Abre la aplicación; con una liga, lee la nota ahí mismo'),
    'inspefos': ('Lista negra del SAT', 'Contesta con la situación del SAT y su oficio en el DOF'),
    'inspcruce': ('Cruce de contratos con la lista 69-B y la ASF', 'Menciona el hallazgo y lleva a su sección'),
    'inspverifica': ('Verifica un estado de cuenta', 'Con un folio o una huella, lo comprueba ahí mismo'),
    'inspnepotismo': ('¿Hasta qué grado de parentesco es nepotismo?', 'Contesta con la ley que alcanza a cada parentesco'),
}


def _servicios():
    import apartados
    return {s[0]: s for s in apartados.SERVICIOS}


def validar(claves):
    """Se detiene si una aplicación del Modo Inspector no tiene su renglón,
    si un renglón sobra, si un tipo no existe o si un Servicio no existe."""
    sv = _servicios()
    faltan = [c for c in claves if c not in APPS]
    sobran = [c for c in APPS if c not in claves]
    if faltan or sobran:
        raise SystemExit('suscripcion.py: APPS no cuadra con el Modo Inspector (faltan %s, sobran %s)' % (faltan, sobran))
    for c, r in APPS.items():
        if not r['gratis']:
            raise SystemExit('suscripcion.py: %s no dice qué es gratis' % c)
        for t, _ in r['desbloquea']:
            if t not in TIPOS:
                raise SystemExit('suscripcion.py: %s pide desbloquear un tipo que no existe (%s)' % (c, t))
        if not r['desbloquea'] and not r.get('nota'):
            raise SystemExit('suscripcion.py: %s no desbloquea nada y no dice por qué' % c)
        if c not in CHAT:
            raise SystemExit('suscripcion.py: %s no dice cómo se le pide al chat (CHAT)' % c)
        for s in r['encargo']:
            if s not in sv:
                raise SystemExit('suscripcion.py: %s apunta al Servicio «%s», que no existe' % (c, s))


def _estado():
    return 'Ábrela' if ABIERTA else 'Próximamente'


def _boton():
    if ABIERTA:
        return '<a class="sus-btn" href="%s?servicio=suscripcion#solicitud">🔓 Quiero suscribirme</a>' % SERVICIOS_PAG
    return '<a class="sus-btn" href="%s?servicio=suscripcion#solicitud">🔔 Avísame cuando abra</a>' % SERVICIOS_PAG


def _lista(xs):
    return '<ul class="sus-lista">%s</ul>' % ''.join('<li>%s</li>' % html.escape(x) for x in xs)


def _desbloquea(r):
    if not r['desbloquea']:
        return '<p class="sus-nada">%s</p>' % html.escape(r['nota'])
    return '<ul class="sus-lista">%s</ul>' % ''.join(
        '<li><span class="sus-tipo">%s %s</span> %s</li>' % (TIPOS[t][0], TIPOS[t][1], html.escape(x)) for t, x in r['desbloquea'])


def _encargo(r, sv, base=''):
    if not r['encargo']:
        return '<p class="sus-nada">No aplica.</p>'
    return '<ul class="sus-lista">%s</ul>' % ''.join(
        '<li><a href="%s%s#sv-%s">%s</a></li>' % (base, SERVICIOS_PAG, s, html.escape(sv[s][2])) for s in r['encargo'])


def niveles_html():
    return '<ol class="sus-niveles">%s</ol>' % ''.join(
        '<li class="sus-nivel sus-%s"><span class="sus-ico" aria-hidden="true">%s</span><b>%s</b>'
        '<span class="sus-et">%s</span><span class="sus-tx">%s</span></li>'
        % (k, ico, nom, _estado() if k == 'suscripcion' else et, tx) for k, ico, nom, et, tx in NIVELES)


def tabla(apps, base=''):
    """apps: [(clave, ícono, nombre, archivo)] en el orden del Modo Inspector.
    Lo mismo en el Modo Inspector y en Servicios."""
    sv = _servicios()
    filas = ''.join(
        '<tr><th scope="row"><a href="%s%s">%s %s</a></th><td data-et="🎁 Gratis, siempre">%s</td>'
        '<td data-et="🔓 Con suscripción">%s</td><td data-et="🧾 Por encargo">%s</td></tr>'
        % (base, arch, ico, html.escape(nom), _lista(APPS[c]['gratis']), _desbloquea(APPS[c]), _encargo(APPS[c], sv, base))
        for c, ico, nom, arch in apps)
    return ('<div class="sus">%s\n'
            '<div class="sus-tabla" role="region" aria-label="Qué es gratis y qué desbloquea la suscripción, aplicación por aplicación" tabindex="0">'
            '<table><caption>Aplicación por aplicación: lo gratis, lo que desbloquearía la suscripción y el encargo que la lleva más a fondo</caption>'
            '<thead><tr><th scope="col">Aplicación</th><th scope="col">🎁 Gratis, siempre</th><th scope="col">🔓 Con suscripción · %s</th>'
            '<th scope="col">🧾 Por encargo</th></tr></thead><tbody>%s</tbody></table></div>\n'
            '<p class="sus-regla"><b>La regla:</b> la información pública nunca se cobra. La suscripción solo puede abrir lo que es trabajo '
            'de más de la plataforma: recordar, avisar, redactar con IA y descargar para una institución. Y no compra lo que publicamos: '
            'vale la <a href="%s%s#independencia">política de independencia</a>.</p>\n'
            '<p class="sus-acc">%s</p></div>') % (niveles_html(), _estado(), filas, base, SERVICIOS_PAG, _boton())


def puertas(apps, base=''):
    """La comparativa: cada aplicación con sus tres puertas, la herramienta,
    el chat en modo Inspector y Servicios. La leen el Modo Inspector y
    Servicios (#puertas)."""
    import urllib.parse
    sv = _servicios()
    filas = ''.join(
        '<tr><th scope="row">%s %s</th><td data-et="🔍 En la herramienta"><a href="%s%s">Abrir la aplicación</a></td>'
        '<td data-et="💬 En el chat, modo Inspector"><a href="%s%s?modo=inspector&amp;q=%s">«%s»</a><br><small>%s</small></td>'
        '<td data-et="🧾 En Servicios">%s</td></tr>'
        % (ico, html.escape(nom), base, arch, base, CHAT_PAG, urllib.parse.quote(CHAT[c][0]), html.escape(CHAT[c][0]),
           html.escape(CHAT[c][1]), ', '.join('<a href="%s%s#sv-%s">%s</a>' % (base, SERVICIOS_PAG, s, html.escape(sv[s][2])) for s in APPS[c]['encargo']) or 'No aplica')
        for c, ico, nom, arch in apps)
    return ('<div class="sus"><div class="sus-tabla" role="region" aria-label="Las tres puertas de cada aplicación" tabindex="0">'
            '<table><caption>Una misma aplicación, tres puertas: la herramienta, el chat en modo Inspector y el Servicio que la lleva más a fondo</caption>'
            '<thead><tr><th scope="col">Aplicación</th><th scope="col">🔍 En la herramienta</th><th scope="col">💬 En el chat, modo Inspector</th>'
            '<th scope="col">🧾 En Servicios</th></tr></thead><tbody>%s</tbody></table></div>\n'
            '<p class="sus-regla">Las tres usan la misma base y la misma regla: el chat no tiene cifras propias, abre la aplicación o contesta con lo que ella publica, '
            'y un Servicio parte de lo mismo para ir más a fondo. Cada pregunta de esta tabla se prueba sola en cada cambio de la plataforma.</p></div>') % filas


def chat_apps():
    """Para la revisión del Inspector en el chat (D.sus): por página de la
    aplicación, lo que abriría la suscripción y su encargo. Sin cifras."""
    import apartados
    sv = _servicios()
    h = next(x for x in apartados.HERRAMIENTAS if x[1] == 'inspector')
    out = {}
    for t in h[7]:
        if t[0] in APPS:
            r = APPS[t[0]]
            out[apartados.modulo_archivo(h[0], t[0])] = {
                'n': t[2], 's': [TIPOS[k][0] + ' ' + x for k, x in r['desbloquea']],
                'e': [[SERVICIOS_PAG + '#sv-' + s, sv[s][2]] for s in r['encargo']]}
    return {'apps': out, 'abierta': ABIERTA, 'ir': 'herramienta-inspector.html#' + ANCLA, 'sv': SERVICIOS_PAG}


def banda(clave, base=''):
    """La franja al pie de cada aplicación: lo gratis y lo que desbloquearía."""
    r = APPS[clave]
    return ('<aside class="sus-banda" aria-label="Gratis y con suscripción">\n'
            '        <p class="sus-banda-tit">🔓 Gratis y con suscripción</p>\n'
            '        <div class="sus-banda-cols"><div><b>🎁 Gratis, siempre</b>%s</div>'
            '<div><b>🔓 Con suscripción · %s</b>%s</div></div>\n'
            '        <p class="sus-acc"><a href="%sherramienta-inspector.html#%s">Lo que cada aplicación abre</a> · %s</p>\n'
            '      </aside>') % (_lista(r['gratis']), _estado(), _desbloquea(r), base, ANCLA, _boton())


def servicio():
    """El renglón de SERVICIOS (apartados.py) para la suscripción."""
    return ('suscripcion', '🔓', 'Suscripción al Modo Inspector',
            'La memoria y el aviso de las aplicaciones del Modo Inspector: lo que sigues, guardado; lo que cambia, en tu correo. La consulta sigue gratis.',
            'Alertas de tus entes, proveedores y empresas; tus expedientes guardados; tu resumen mensual. Próximamente.',
            'Quien sigue un tema, un ente o a sus proveedores de forma recurrente.')


def temas():
    """Para el chat (D.san, con el molde de informe_sancion.temas())."""
    con = [(c, r) for c, r in APPS.items() if r['desbloquea']]
    import apartados
    nom = {t[0]: t[2] for h in apartados.HERRAMIENTAS if h[1] == 'inspector' for t in h[7]}
    li = ''.join('<li><b>%s:</b> %s.</li>' % (html.escape(nom[c]), '; '.join(html.escape(x[1][0].lower() + x[1][1:]) for x in r['desbloquea']))
                 for c, r in con)
    sin = [nom[c] for c, r in APPS.items() if not r['desbloquea']]
    return {'serv_suscripcion': {
        'tit': 'Qué es gratis en el Modo Inspector y qué abriría una suscripción',
        'h': ('<p><b>La consulta es gratis y lo seguirá siendo:</b> las ocho aplicaciones, el chat, las fichas con su PDF, el dictamen y verificar un folio. '
              'Ningún dato público se esconde detrás de un pago.</p>'
              '<p>La suscripción, que todavía no abre, solo agregaría trabajo de más: recordar lo que sigues, avisarte cuando cambia, redactar con IA y descargar para tu institución:</p>'
              '<ul>%s</ul><p>En %s no hay nada que desbloquear. Y si un caso necesita ir más a fondo, eso es un encargo de Servicios, que se cotiza por escrito. '
              'El precio de la suscripción aún no existe: saldrá de los encargos piloto.</p>') % (li, ' ni en '.join(html.escape(s) for s in sin)),
        'ci': [],
        # Sin cifras: es la regla de la casa, no un dato fiscal; no lleva documento oficial.
        'fu': [],
        'sug': ['¿Qué servicios ofrece Auditavisión?', '¿Cómo reviso a un proveedor antes de contratarlo?', '¿Está en la lista negra del SAT?'],
        'ir': ['herramienta-inspector.html#' + ANCLA, 'Modo Inspector · Gratis y con suscripción']}}
