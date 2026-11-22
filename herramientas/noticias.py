# -*- coding: utf-8 -*-
"""La pestaña Noticias, reestructurada como periódico (pedido del autor,
28-10-2026: «una nueva reestructuración tanto de diseño como de la
información… partiendo de una metodología u objetivo»).

Objetivo: que ninguna noticia sobre el dinero público se quede sin cotejar.
La página es un diario con nueve secciones y un método de siete pasos, del
rumor al documento. Separa la noticia (lo que pasó y lo que consta) de la
opinión (la Columna del Erario, nuestro argumento), y junta en el mismo lugar
el verificador, la réplica y la postura, el seguimiento de los casos, la mesa
de redacción (titulares que jalamos, rotulados «sin verificar») y la agenda
del erario (las fechas que fija la ley).

Las columnas y las notas siguen viviendo en columnas.js (COLUMNAS), que las
reparte: «Al momento» y «Verificado» son noticia; «Personajes», «Hechos» e
«Historia», la Columna. Aquí solo va el armazón, el método, la agenda y las
búsquedas de la mesa de redacción, que leen noticias.js y
recolectar_noticias.py. Ninguna cifra se escribe en este módulo.
"""
import json

ARCHIVO = 'noticias-relevantes.html'

# Desde el 29-10-2026 (pedido del autor: «quiero que aquí existan tres
# tarjetas… y que nos desglosen a cada una de sus páginas») la pestaña es un
# índice con tres tarjetas, y el diario se reparte en tres páginas. Cada
# sección vive en una sola: (archivo, ícono, nombre, lema, entrada, secciones).
DIARIO = 'noticias-auditavision.html'
VERIFICA = 'noticias-verifica.html'
SEGUIMIENTO = 'noticias-seguimiento.html'
PARTES = [
    (DIARIO, '🗞️', 'Auditavisión Noticias', 'La columna periodística: la noticia, verificada, y la opinión, con documentos',
     'El periódico de la plataforma: la noticia, cotejada afirmación por afirmación, y la opinión, parada en documentos. Elige una sección en la barra.',
     ('portada', 'al-momento', 'columnas', 'replica')),
    (VERIFICA, '⚖️', 'Verifica una noticia', 'Del rumor al documento',
     'Pega la liga o el texto de lo que viste y lo ponemos junto al documento oficial. En la barra están también los puntos ciegos, la hemeroteca, la mesa de redacción y nuestro método.',
     ('verifica', 'puntos-ciegos', 'hemeroteca', 'mesa', 'metodo')),
    (SEGUIMIENTO, '🔔', 'Seguimiento: el caso no se olvida', 'Qué documento falta para cerrar cada caso, y cuándo debe llegar',
     'Cada caso abierto dice qué documento falta para cerrarlo. En la barra están también la memoria de promesas y la agenda del erario.',
     ('seguir', 'promesas', 'agenda')),
]
# Las anclas viejas del diario de una sola página (noticias-relevantes.html#…),
# a la página donde viven ahora. «col-*» son las columnas.
ANCLAS = dict([(sid, arch + '#' + sid) for arch, *_r, secs in PARTES for sid in secs] +
              [('propon', VERIFICA + '#propon'), ('seguimientos', SEGUIMIENTO + '#seguimientos'), ('col-*', DIARIO)])
BANDEJA = 'docs/noticias/bandeja.json'

CPEUM = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf'
LFPRH = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPRH.pdf'
LFRCF = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFRCF.pdf'

ESTILOS = ['noticias.css']
SCRIPTS = ['noticias.js']

# Las secciones del diario, en su orden: (id, ícono, nombre en la barra,
# título de la sección, entradilla). Los id «verifica», «al-momento»,
# «columnas», «replica», «seguir» y «propon» ya tenían enlaces de fuera
# (chat, preguntas de prueba, Aprende): no se cambian.
SECCIONES = [
    ('portada', '🗞️', 'Portada', 'Portada',
     'Lo más reciente, en corto: la noticia principal, lo que está pasando «Al momento» y lo último de la Columna.'),
    ('verifica', '⚖️', 'Verifica', 'El verificador: pega la nota y la cotejamos',
     'Pega la liga de una nota, un portal o un video, o el texto o la transcripción de lo que viste en redes. Leemos lo que dice, '
     'encontramos sus cifras, las ponemos junto al documento oficial y te damos nuestro dictamen, con la salud financiera de quien aparece en la nota.'),
    ('al-momento', '📰', 'Noticias', 'Noticias: lo que pasó y lo que consta',
     'Notas breves del día y el cotejo de lo que circula en redes, afirmación por afirmación. Aquí no opinamos: decimos qué consta en el '
     'documento oficial, qué tiene matices y qué falta probar.'),
    ('columnas', '✒️', 'Opinión', 'La Columna del Erario: nuestra opinión',
     'Aquí sí argumentamos: lo que pensamos del uso del dinero público y por qué, siempre parados en un documento. Personajes, hechos e historia '
     'que vale la pena conocer.'),
    ('replica', '✉️', 'Réplica y postura', 'Réplica y postura',
     'Quien es aludido puede responder, y lo que la parte aludida dijo en su propio documento se publica en sus palabras.'),
    ('seguir', '🔔', 'Casos abiertos', 'Casos abiertos: lo que falta para cerrarlos',
     'Cada caso abierto dice qué documento falta para cerrarlo. Síguelo y te avisamos cuando llegue, o pídele al Auditor que siga uno nuevo.'),
    # El detector de puntos ciegos (pedido del autor, 01-11-2026): lo que las
    # notas suelen esconder, en reglas que el verificador y el chat aplican solos.
    ('puntos-ciegos', '🔦', 'Puntos ciegos', 'Puntos ciegos: lo que una nota suele esconder',
     '%s preguntas que conviene hacerle a cualquier nota sobre el dinero público antes de creerle. El verificador y el Auditor las '
     'buscan solos en lo que pegues. Toca una para abrirla.'),
    # La hemeroteca (pedido del autor, 31-10-2026: «seguimiento como Animal
    # Político, La Jornada… vincular toda la información que gira sobre
    # finanzas públicas»): las notas de prensa que ya cotejamos, por medio.
    ('hemeroteca', '🗂️', 'Hemeroteca', 'Hemeroteca: las notas que ya cotejamos',
     'Lo que publicaron los medios sobre el dinero público y que ya pusimos junto al documento oficial: Animal Político, La Jornada, '
     'El Financiero y los demás, cada titular con su liga y con la nota donde lo cotejamos. Solo guardamos el titular, el medio y la fecha, '
     '<b>sin verificar</b>: lo que consta está en nuestro cotejo, no en el titular.'),
    ('mesa', '📡', 'Mesa de redacción', 'Mesa de redacción: lo que estamos jalando',
     'Titulares sobre finanzas públicas que juntamos de los buscadores de noticias para alimentar nuestra base. Llegan <b>sin verificar</b>: '
     'son la materia prima, no la noticia. Cualquiera la puedes mandar al verificador.'),
    # La memoria de promesas (pedido del autor, 01-11-2026): cada cifra que anuncia
    # un gobierno, seguida por Presupuesto, Cuenta Pública y ASF (promesas.py).
    ('promesas', '📣', 'Promesas', 'Memoria de promesas: lo que se anunció y lo que llegó',
     'Cada cifra que anuncia un gobierno, con su fecha y su documento, seguida hasta el Presupuesto, la Cuenta Pública y la Auditoría Superior.'),
    ('agenda', '🗓️', 'Agenda', 'Agenda del erario: lo que viene',
     'Las fechas que la ley fija para el dinero público: cuándo llega el Paquete Económico, cuándo se aprueba, cuándo informa Hacienda y cuándo entrega la Auditoría Superior.'),
    ('metodo', '🧭', 'Cómo trabajamos', 'Cómo trabajamos: del rumor al documento',
     'El método de la pestaña en siete pasos, y cómo nos puedes proponer una nota.'),
]

# El método (el objetivo de la pestaña dicho en pasos).
METODO = [
    ('📥', 'Captamos', 'Lo que circula: notas, portales, videos, transcripciones y publicaciones en redes. Llega por ti (el verificador y '
     '«Propón una nota») o por la mesa de redacción. Todo entra rotulado <b>sin verificar</b>.'),
    ('✂️', 'Desarmamos', 'Cada nota se parte en afirmaciones que se pueden comprobar y en cifras con su unidad: «se acotó», «lo paga el Estado», «mil millones».'),
    ('🔍', 'Cotejamos', 'Cada afirmación contra el documento oficial: ✅ consta, ⚠️ consta con matices, ❌ sin documento oficial o ⏳ pendiente. '
     'Lo pendiente dice a quién le toca publicarlo y entra al <a href="pendientes.html">Registro de pendientes</a>.'),
    ('📊', 'Interpretamos', 'Qué quiere decir con nuestros datos: el estado de resultados o la salud financiera de la institución, la cuenta con números '
     'redondos y las palabras del glosario que hacen falta.'),
    ('🗞️', 'Publicamos, por separado', 'La <b>noticia</b> (lo que pasó y lo que consta, sin opinión) y la <b>columna</b> (nuestro argumento, con documentos). '
     'Citamos al medio y a quien firma; no copiamos la nota.'),
    ('✉️', 'Escuchamos', 'La réplica de quien considera inexacto un dato nuestro se publica íntegra y sin comentarios; la postura de la parte aludida, en sus palabras.'),
    ('🔔', 'Seguimos', '«Lo que sigue» dice qué documento falta. Cuando llega, la nota cambia, quien la sigue recibe el aviso y el dato entra a la base '
     'que consulta el Auditor.'),
]

# La agenda del erario: fechas que fija la ley, cada una con su artículo.
# m: mes; d: día; ult: el último día hábil del mes (lo calcula noticias.js
# saltando sábados y domingos, sin días festivos, y lo dice). cuenta: la
# fecha no la dice la ley, es nuestra cuenta a partir de ella (derivado).
AGENDA = [
    {'m': 1, 'd': 30, 'que': 'Informe trimestral de Hacienda (octubre a diciembre)', 'quien': 'SHCP al Congreso',
     'ley': 'LFPRH, art. 107, fr. I', 'url': LFPRH, 'cuenta': '30 días naturales después del cierre del trimestre'},
    {'m': 2, 'd': 20, 'que': 'Informe General e informes individuales de la Cuenta Pública (tercera entrega)', 'quien': 'ASF a la Cámara de Diputados',
     'ley': 'LFRCF, arts. 33 y 35', 'url': LFRCF},
    {'m': 4, 'd': 1, 'que': 'Precriterios: objetivos y escenarios para el presupuesto del año siguiente', 'quien': 'SHCP al Congreso',
     'ley': 'LFPRH, art. 42, fr. I', 'url': LFPRH},
    {'m': 4, 'd': 30, 'que': 'Cuenta Pública del año anterior: lo que de verdad se gastó', 'quien': 'Ejecutivo a la Cámara de Diputados',
     'ley': 'Constitución, art. 74, fr. VI', 'url': CPEUM},
    {'m': 4, 'd': 30, 'que': 'Informe trimestral de Hacienda (enero a marzo)', 'quien': 'SHCP al Congreso',
     'ley': 'LFPRH, art. 107, fr. I', 'url': LFPRH, 'cuenta': '30 días naturales después del cierre del trimestre'},
    {'m': 5, 'd': 1, 'que': 'Informe semestral: cómo van las observaciones de la ASF', 'quien': 'ASF a la Cámara de Diputados',
     'ley': 'LFRCF, art. 38', 'url': LFRCF},
    {'m': 6, 'd': 30, 'que': 'Estructura programática del presupuesto que viene', 'quien': 'SHCP a la Cámara de Diputados',
     'ley': 'LFPRH, art. 42, fr. II', 'url': LFPRH},
    {'m': 6, 'ult': True, 'que': 'Informes individuales de auditoría (primera entrega)', 'quien': 'ASF a la Cámara de Diputados',
     'ley': 'LFRCF, art. 35', 'url': LFRCF},
    {'m': 7, 'd': 30, 'que': 'Informe trimestral de Hacienda (abril a junio)', 'quien': 'SHCP al Congreso',
     'ley': 'LFPRH, art. 107, fr. I', 'url': LFPRH, 'cuenta': '30 días naturales después del cierre del trimestre'},
    {'m': 9, 'd': 8, 'que': 'Paquete Económico: Ley de Ingresos, Presupuesto de Egresos y Criterios', 'quien': 'Ejecutivo al Congreso',
     'ley': 'Constitución, art. 74, fr. IV; LFPRH, art. 42, fr. III', 'url': CPEUM,
     'nota': 'El año en que cambia el Presidente, a más tardar el 15 de noviembre (Constitución, art. 74, fr. IV).'},
    {'m': 10, 'd': 20, 'que': 'Diputados aprueban la Ley de Ingresos', 'quien': 'Cámara de Diputados',
     'ley': 'LFPRH, art. 42, fr. IV', 'url': LFPRH},
    {'m': 10, 'd': 30, 'que': 'Informe trimestral de Hacienda (julio a septiembre)', 'quien': 'SHCP al Congreso',
     'ley': 'LFPRH, art. 107, fr. I', 'url': LFPRH, 'cuenta': '30 días naturales después del cierre del trimestre'},
    {'m': 10, 'ult': True, 'que': 'Informes individuales de auditoría (segunda entrega)', 'quien': 'ASF a la Cámara de Diputados',
     'ley': 'LFRCF, art. 35', 'url': LFRCF},
    {'m': 10, 'd': 31, 'que': 'El Senado aprueba la Ley de Ingresos', 'quien': 'Cámara de Senadores',
     'ley': 'LFPRH, art. 42, fr. IV', 'url': LFPRH},
    {'m': 11, 'd': 1, 'que': 'Informe semestral: cómo van las observaciones de la ASF', 'quien': 'ASF a la Cámara de Diputados',
     'ley': 'LFRCF, art. 38', 'url': LFRCF},
    {'m': 11, 'd': 15, 'que': 'Diputados aprueban el Presupuesto de Egresos', 'quien': 'Cámara de Diputados',
     'ley': 'Constitución, art. 74, fr. IV; LFPRH, art. 42, fr. V', 'url': CPEUM},
]

# Lo que jala la mesa de redacción: búsquedas en los buscadores de noticias
# (Bing Noticias y, de respaldo, Google Noticias). Solo se guardan el
# titular, el medio, la fecha y la liga; nunca el texto de la nota.
MESA = [
    ('presupuesto', '💰 Presupuesto y Paquete Económico', 'presupuesto de egresos Hacienda México'),
    ('deuda', '📉 Deuda pública', 'deuda pública México Hacienda'),
    ('asf', '🔎 Auditoría Superior', 'Auditoría Superior de la Federación'),
    ('impuestos', '🧾 Impuestos y SAT', 'SAT recaudación impuestos México'),
    ('contratos', '📑 Contratos y licitaciones', 'licitación adjudicación directa gobierno México'),
    ('empresas', '🛢️ Pemex y CFE', 'Pemex CFE finanzas deuda'),
    ('salud', '🏥 IMSS, ISSSTE y salud', 'IMSS ISSSTE presupuesto'),
    ('estados', '🗺️ Estados y municipios', 'participaciones federales estados municipios'),
    ('medios', '📰 Lo que publican los medios', 'finanzas públicas en los medios que seguimos por nombre'),
]

# Los medios que la mesa sigue por nombre (pedido del autor, 02-11-2026:
# «un agente de seguimiento de publicaciones… Animal Político, La Jornada, El
# Financiero, El Informador… Latinus»). Cada uno se busca con su dominio y
# TEMAS_MEDIOS; lo que junta va al tema «medios» de la bandeja, rotulado «sin
# verificar», y la misma historia contada por varios medios se agrupa.
MEDIOS = [
    ('Animal Político', 'animalpolitico.com'),
    ('La Jornada', 'jornada.com.mx'),
    ('El Financiero', 'elfinanciero.com.mx'),
    ('El Informador', 'informador.mx'),
    ('Latinus', 'latinus.us'),
    ('El Economista', 'eleconomista.com.mx'),
    ('Proceso', 'proceso.com.mx'),
    ('Expansión', 'expansion.mx'),
]
TEMAS_MEDIOS = 'presupuesto OR deuda OR "Auditoría Superior" OR licitación OR Hacienda OR desvío'


# El tablero del Noticiero (reestructura del autor, 16-11-2026: «verificación
# y reestructuración de la pestaña Noticiero teniendo en cuenta las novedades
# de los servicios… y el objetivo… del modo Periodista»). La pestaña es un
# tablero: cada sección tiene su tarjeta, agrupada por su página (PARTES), y
# cada página muestra una sección a la vez (pestañas de noticias.js). Una
# sección nueva necesita aquí su línea de tarjeta, o la generación se detiene.
TARJETA = {
    'portada': 'Lo más reciente, de un vistazo',
    'al-momento': 'Las notas del día y el cotejo de lo que circula',
    'columnas': 'La Columna del Erario: nuestro argumento, con documentos',
    'replica': 'Lo que responde quien fue aludido',
    'verifica': 'Pega la liga o el texto y lo cotejamos',
    'puntos-ciegos': 'Lo que una nota suele esconder',
    'hemeroteca': 'Las notas de los medios que ya cotejamos',
    'mesa': 'Los titulares que estamos jalando, sin verificar',
    'metodo': 'Del rumor al documento, en siete pasos, y propón una nota',
    'seguir': 'Qué documento falta para cerrar cada caso',
    'promesas': 'Lo que se anunció y lo que llegó',
    'agenda': 'Las fechas que la ley fija para el dinero público',
}
GRUPO = {DIARIO: '🗞️ Lee: el periódico', VERIFICA: '⚖️ Verifica: del rumor al documento', SEGUIMIENTO: '🔔 Sigue: el caso no se olvida'}
PERIODISMO = 'periodismo-en-riesgo.html'
CHAT = 'herramienta-inspector-pregunta.html'

# El puente al modo Periodista y a Servicios, al pie de cada página y en el
# tablero: (título, texto, preguntas para el modo Periodista, servicios). Las
# preguntas son de las que ya contesta el chat (preguntas_auditor.json); los
# servicios se leen de SERVICIOS y COBRO de apartados.py: nunca un monto.
PUENTE = {
    ARCHIVO: ('¿Trabajas en una redacción o investigas por tu cuenta?', None,
              ('Noticias de hoy', '¿Qué pasó con Dos Bocas?', 'Segalmex', '¿Qué obras no han publicado sus cifras?'),
              ('temporada', 'revision', 'expediente', 'seguimiento')),
    DIARIO: ('¿Tu redacción necesita esto en campaña?',
             'El verificador y la memoria de promesas, con acompañamiento, para tu equipo.',
             ('Noticias de hoy', '¿Qué pasó con Dos Bocas?', 'Tren Maya'), ('temporada',)),
    VERIFICA: ('¿Necesitas cotejar algo más grande que una nota?',
               'Una pregunta delimitada o un caso completo, revisado contra los documentos públicos que lo responden.',
               ('¿Qué es el huachicol fiscal?', 'Modalidad 40', 'Segalmex'), ('revision', 'expediente')),
    SEGUIMIENTO: ('¿Quieres que vigilemos un tema por ti?',
                  'Un tema que cambia (contratos, presupuesto, auditorías), vigilado, con aviso de cada cambio y su documento.',
                  ('¿Qué obras no han publicado sus cifras?', 'Tren Maya', 'Segalmex'), ('seguimiento', 'expediente')),
}


def _q(t):
    from urllib.parse import quote
    return '%s?modo=periodista&amp;q=%s' % (CHAT, quote(t))


def puente(archivo):
    """La franja al pie: el modo Periodista (con preguntas que ya contesta) y
    los servicios que vienen al caso, con su forma de cobro. Nunca un monto."""
    import html as h
    import apartados
    tit, tx, preguntas, servs = PUENTE[archivo]
    por_id = {x[0]: x for x in apartados.SERVICIOS}
    if tx is None:
        tx = next(p[3] for p in apartados.PERFILES if p[1].startswith('Periodismo'))
    lis = '\n'.join(
        '      <li><a class="nt-pu-serv" href="%s#sv-%s"><span aria-hidden="true">%s</span><span><b>%s</b><small>%s</small>'
        '<em>%s</em></span></a></li>' % (apartados.SV_CATALOGO, sid, por_id[sid][1], h.escape(por_id[sid][2]), h.escape(por_id[sid][3]),
                                         h.escape(apartados.COBRO[sid])) for sid in servs)
    chips = ' '.join('<a class="nt-chip" href="%s">%s</a>' % (_q(q), h.escape(q)) for q in preguntas)
    return ('<aside class="nt-puente" aria-label="El modo Periodista y los servicios">\n'
            '  <div class="nt-pu-modo">\n'
            '    <h2 class="nt-pu-tit"><span aria-hidden="true">📰</span> Pregúntaselo al Auditor en modo Periodista</h2>\n'
            '    <p>Te cuenta <b>lo que casi nadie te cuenta, con documento</b>: lo que la ASF dejó por aclarar, lo que una dependencia no ha '
            'publicado y quién lo debe, y qué consta de lo que circula. Nunca un rumor ni una filtración.</p>\n'
            '    <p class="nt-pu-chips">%s</p>\n'
            '    <p class="nt-acciones"><a class="nt-btn" href="%s?modo=periodista">📰 Abrir el modo Periodista</a></p>\n'
            '  </div>\n'
            '  <div class="nt-pu-servs">\n'
            '    <h2 class="nt-pu-tit"><span aria-hidden="true">🧰</span> %s</h2>\n'
            '    <p>%s</p>\n'
            '    <ul class="nt-pu-lista">\n%s\n    </ul>\n'
            '    <p class="nt-acciones"><a class="nt-btn nt-btn-sec" href="servicios-tu-perfil.html">👤 Servicios para periodismo</a> '
            '<a class="nt-btn nt-btn-sec" href="%s">📝 Solicita una cotización</a></p>\n'
            '    <p class="nt-pie">Leer, verificar y seguir un caso aquí es gratis. Lo de pago es el trabajo a la medida, y nunca cambia '
            'lo que publicamos.</p>\n'
            '  </div>\n'
            '</aside>') % (chips, CHAT, h.escape(tit), h.escape(tx), lis, apartados.SV_COTIZA)


def tablero():
    """Las tarjetas del índice: [(grupo, id, página, (ícono, nombre, lema))]."""
    falta = [i for i, *_r in SECCIONES if i not in TARJETA]
    if falta:
        raise SystemExit('noticias.py: falta la línea de tarjeta (TARJETA) de: %s' % ', '.join(falta))
    out = []
    for arch, *_r, secs in PARTES:
        for n, sid in enumerate(secs):
            _i, ico, nom, _t, _e = next(x for x in SECCIONES if x[0] == sid)
            out.append((GRUPO[arch] if n == 0 else '', 'ir-' + sid, arch + '#' + sid, (ico, nom, TARJETA[sid])))
    out.append(('🛡️ Quienes informan', 'ir-periodismo', PERIODISMO,
                ('🛡️', 'Periodismo en riesgo', 'Las agresiones a la prensa, con el informe del Mecanismo de Protección')))
    # Ronda 7 (22-11-2026, decisión del autor): Garantías cívicas se muda de Comunidad al Noticiero.
    out.append(('🧭 Tus garantías', 'ir-garantias', 'garantias.html',
                ('🧭', 'Garantías cívicas', 'A qué puerta tocar si viste algo raro con el dinero público, y qué te protege')))
    return out


def ultimas(n=3):
    """«Lo último, verificado» del tablero: las notas «Al momento» más nuevas,
    escritas en la página (cada una lleva a su página propia)."""
    import html as h
    import asistente_personajes
    cols = [c for c in asistente_personajes.columnas()[0] if c['seccion'] == 'Al momento']
    cols.sort(key=lambda c: tuple(reversed([int(x) for x in c['fecha'].split('-')])), reverse=True)
    def li(c):
        ct = c.get('cotejo') or []
        ok = sum(1 for x in ct if x['res'] in ('consta', 'matiz'))
        pend = sum(1 for x in ct if x['res'] == 'pendiente')
        return ('    <li><a href="%s"><time>%s</time><b>%s</b><small>✅ %d con documento · ⏳ %d por probar%s</small></a></li>'
                % (AL_MOMENTO % c['id'], h.escape(c['fecha']), h.escape(c['titulo']), ok, pend,
                   (' · a partir de ' + h.escape(c['nota']['medio'])) if c.get('nota') else ''))
    return ('<section class="nt-ix" aria-labelledby="ntUltTit">\n'
            '  <h2 class="nt-ix-tit" id="ntUltTit"><span aria-hidden="true">⏱️</span> Lo último, verificado</h2>\n'
            '  <ol class="nt-ix-ult">\n%s\n  </ol>\n'
            '  <p class="nt-acciones"><a class="nt-btn nt-btn-sec" href="%s#al-momento">Todas las noticias ➔</a></p>\n'
            '</section>') % ('\n'.join(li(c) for c in cols[:n]), DIARIO)


def cierre_indice():
    # Ronda 7: «Lo último, verificado» sube al arranque del portal (portada()); aquí queda el puente.
    return '<div class="nt-indice">\n%s\n</div>' % puente(ARCHIVO)


def portada():
    """El arranque del portal (Ronda 7, decisión del autor: «que arranque directamente desde arriba como el portal del
    periódico»): la cabeza del periódico y lo último, verificado, antes de las tarjetas."""
    return '<div class="nt-indice nt-portal">\n%s\n</div>' % ultimas()


def datos():
    return {'agenda': AGENDA, 'mesa': [{'id': i, 't': t, 'q': q} for i, t, q in MESA], 'bandeja': BANDEJA,
            'medios': [{'n': n, 'd': d} for n, d in MEDIOS], 'temasMedios': TEMAS_MEDIOS}


def _sec(id_, ico, tit, entrada, cuerpo, clase=''):
    return ('<section class="nt-sec%s" id="%s" aria-labelledby="%s-tit">\n'
            '  <header class="nt-sec-cab"><h2 class="nt-tit" id="%s-tit"><span aria-hidden="true">%s</span> %s</h2>\n'
            '  <p class="nt-entrada">%s</p></header>\n%s\n</section>') % (clase, id_, id_, id_, ico, tit, entrada, cuerpo)


def _metodo():
    pasos = '\n'.join('    <li><span class="nt-paso-n" aria-hidden="true">%s</span><div><b>%d. %s</b><p>%s</p></div></li>' % (i, n, t, x)
                      for n, (i, t, x) in enumerate(METODO, 1))
    return ('  <p class="nt-objetivo"><b>Nuestro objetivo:</b> que ninguna noticia sobre el dinero público se quede sin cotejar. '
            'Lo que circula es el punto de partida; el documento oficial, la última palabra.</p>\n'
            '  <ol class="nt-metodo">\n%s\n  </ol>\n'
            '  <div class="nt-propon" id="propon">\n'
            '    <h3 class="nt-sub" id="propon-tit">✍️ Propón una nota</h3>\n'
            '    <p>Mándanos la liga de la nota, el video o la publicación, con lo que te llamó la atención. Pasa por los siete pasos, y si '
            'tiene que ver con el dinero público, se publica como nota «Al momento», como cotejo de Verificamos o da pie a una columna.</p>\n'
            '    <p class="nt-acciones"><a class="nt-btn" href="comunidad-tema.html" data-puerta="tema">💡 Proponer una nota</a> '
            '<a class="nt-btn nt-btn-sec" href="#verifica">⚖️ Mejor la verifico yo</a></p>\n'
            '    <p class="nt-pie">No publicamos el nombre de personas privadas, y una acusación no es una condena. Las reglas completas: '
            '<a href="pilares.html">nuestros pilares</a> y <a href="https://github.com/uzoraproductos-arch/a/blob/claude/funny-turing-imtm54/docs/VERIFICAMOS.md" target="_blank" rel="noopener">el protocolo de Verificamos ↗</a>.</p>\n'
            '  </div>') % pasos


def construir(base, ref, archivo=DIARIO):
    import insp_nota
    import promesas
    import puntos_ciegos
    parte = next(p for p in PARTES if p[0] == archivo)
    mias = [x for x in SECCIONES if x[0] in parte[5]]
    nav = '\n'.join(['    <a href="#%s" data-nt-tab="%s"><span aria-hidden="true">%s</span> %s</a>' % (i, i, ico, n) for i, ico, n, _t, _e in mias] +
                    ['    <a class="nt-barra-otra" href="%s"><span aria-hidden="true">%s</span> %s ➔</a>' % (a, ico, n.split(':')[0])
                     for a, ico, n, *_r in PARTES if a != archivo] +
                    (['    <a class="nt-barra-otra" href="%s"><span aria-hidden="true">🛡️</span> Periodismo en riesgo ➔</a>' % PERIODISMO]
                     if archivo == DIARIO else []))
    cuerpos = {
        'portada': ('<div id="noticiasPortada" class="nt-portada-raiz"><noscript><p>La portada necesita JavaScript.</p></noscript></div>'),
        'verifica': insp_nota.construir(base, ref) +
                    '\n<p class="nt-pie">Es la misma aplicación «Contrasta una nota» de Herramientas y del Auditor. Para un cotejo frase por frase, '
                    'pregúntale al Auditor «¿es cierto que…?», o <a href="#propon">propón la nota</a> para que la publiquemos.</p>',
        'al-momento': '<div id="noticiasDiario" class="col-diario"><noscript><p>Las noticias necesitan JavaScript.</p></noscript></div>',
        'columnas': '<div id="columnasDiario" class="col-diario col-opinion"><noscript><p>Las columnas necesitan JavaScript.</p></noscript></div>',
        'replica': ('<div class="nt-dos">\n'
                    '  <div class="nt-caja"><h3 class="nt-sub">✉️ La réplica</h3><p>La pide quien considera que un dato nuestro sobre él es inexacto o falso. '
                    'Se publica gratis, íntegra y sin comentarios, en la misma nota o columna, y si prueba un error nuestro va además a la '
                    '<a href="comunidad-erratas.html">fe de erratas</a>.</p>'
                    '<p><a class="nt-btn" href="derecho-de-replica.html">Cómo ejercer tu derecho de réplica</a></p></div>\n'
                    '  <div class="nt-caja"><h3 class="nt-sub">🗣️ La postura</h3><p>Lo que la institución o la persona aludida dijo en su propio documento: '
                    'un comunicado, una respuesta oficial, una tarjeta informativa. Va con su liga y en sus palabras, y no la calificamos.</p></div>\n'
                    '</div>\n'
                    '<h3 class="nt-sub">Las que hemos recibido</h3>\n'
                    '<div class="col-replicas" id="columnasReplicas"><noscript><p>La lista de réplicas necesita JavaScript.</p></noscript></div>'),
        'seguir': ('<div id="noticiasSeguimiento"><noscript><p>El seguimiento necesita JavaScript.</p></noscript></div>\n'
                   '<div class="nt-caja nt-pide">\n'
                   '  <h3 class="nt-sub">🕵️ Pídele al Auditor que siga un caso</h3>\n'
                   '  <p>¿Hay un contrato, una obra, una promesa o una investigación que quieres que no se olvide? Dinos qué es y qué documento '
                   'esperas (un informe de la ASF, una votación, una sentencia, la Cuenta Pública). Si lo podemos sostener con documentos, abre su caso aquí.</p>\n'
                   '  <p class="nt-acciones"><a class="nt-btn" href="comunidad-tema.html" data-puerta="tema">🔔 Pedir un seguimiento</a></p>\n'
                   '</div>'),
        'hemeroteca': '<div id="noticiasHemeroteca" class="nt-hem"><noscript><p>La hemeroteca necesita JavaScript.</p></noscript></div>',
        'mesa': ('<div id="noticiasMesa" class="nt-mesa"><noscript><p>La mesa de redacción necesita JavaScript.</p></noscript></div>'),
        'agenda': ('<div id="noticiasAgenda" class="nt-agenda"><noscript><p>La agenda necesita JavaScript.</p></noscript></div>\n'
                   '<p class="nt-pie">Son los plazos máximos que fija la ley: el documento puede llegar antes. Cuando la fecha cae en día inhábil '
                   'o la ley prevé una prórroga, puede moverse. Los «días que faltan» son nuestra cuenta ' + insp_nota_chip('derivado') + '.</p>'),
        'metodo': _metodo(),
        'puntos-ciegos': puntos_ciegos.seccion(lambda t: __import__('html').escape(str(t or ''), quote=False)),
        'promesas': promesas.seccion(lambda t: __import__('html').escape(str(t or ''), quote=False),
                                     lambda e, p=None: '<span class="est-chip est-%s"%s>%s</span>' % (e, (' data-pend="%s"' % p) if p else '', 'auditada' if e == 'derivado' else e)),
    }
    clases = {'columnas': ' nt-sec-opinion', 'verifica': ' nt-sec-verifica', 'portada': ' nt-sec-portada'}
    cifra = {13: 'Trece'}.get(len(puntos_ciegos.REGLAS), str(len(puntos_ciegos.REGLAS)))
    partes = [_sec(i, ico, t, (e % cifra) if i == 'puntos-ciegos' else e, cuerpos[i], clases.get(i, '')) for i, ico, _n, t, e in mias]
    # El cabezal del periódico va solo en el diario: en las otras dos páginas
    # repetía el título y bajaba el contenido (16-11-2026).
    cabezal = ('<header class="nt-cabezal">\n'
               '  <p class="nt-cabezal-linea"><span id="noticiasHoy">Las finanzas públicas de México</span><span>Cada cifra, con su documento</span></p>\n'
               '  <p class="nt-nombre">Auditavisión <span>Noticias</span></p>\n'
               '  <p class="nt-lema">La noticia, verificada. La opinión, con documentos. Y el caso, en seguimiento.</p>\n'
               '</header>\n') if archivo == DIARIO else ''
    return ('<div class="nt-diario%s">\n%s'
            '<nav class="nt-barra" aria-label="Secciones de esta página y las otras dos de Noticias">\n%s\n</nav>\n%s\n%s\n'
            '<script type="application/json" id="noticiasDatos">%s</script>\n'
            '</div>') % ('' if cabezal else ' nt-sin-cabezal', cabezal, nav, '\n'.join(partes), puente(archivo),
                         json.dumps(datos(), ensure_ascii=False).replace('</', '<\\/'))


def insp_nota_chip(estado):
    return '<span class="est-chip est-%s">%s</span>' % (estado, 'auditada' if estado == 'derivado' else estado)


# Cada nota «Al momento» con su página propia (pedido del autor, 31-10-2026:
# «que el usuario, al momento de llevar a cabo una búsqueda en Google, nos
# encuentre»). El diario las pinta con JavaScript, y un buscador necesita el
# texto en la página: aquí va escrita, con su NewsArticle (schema.org) y su
# dirección estable, que entra sola a sitemap.xml. Es la misma nota de
# columnas.js (la escribe integrar_al_momento.py): no se redacta otra vez.
AL_MOMENTO = 'noticias-al-momento-%s.html'
RES_TX = {'consta': ('✅', 'Consta'), 'matiz': ('⚠️', 'Consta, con matices'), 'no consta': ('❌', 'Sin documento oficial'),
          'pendiente': ('⏳', 'Pendiente')}


def _iso(f):
    d, m, a = f.split('-')
    return '%s-%s-%s' % (a, m, d)


def _nota_html(c, sitio):
    import html as h
    e = lambda t: h.escape(str(t or ''), quote=True)
    liga = lambda u, t, rel='noopener noreferrer': '<a href="%s" target="_blank" rel="%s">%s ↗</a>' % (e(u), rel, e(t))
    partes = ['<article class="nt-nota-propia">']
    partes += ['<p%s>%s</p>' % (' class="col-capitular"' if k == 0 else '', e(p)) for k, p in enumerate(c.get('cuerpo', []))]
    if c.get('nota'):
        n = c['nota']
        partes.append('<p class="col-nota">📰 <b>De dónde salió:</b> %s · %s. Es el punto de partida: lo cotejamos contra el documento oficial.</p>'
                      % (liga(n['url'], '%s, «%s»' % (n['medio'], n['titulo'])), e(n['fecha'])))
    if c.get('cotejo'):
        partes.append('<h2 class="nt-sub" id="cotejo">🔍 Cotejo, afirmación por afirmación</h2><ol class="nt-cotejo">')
        for k, x in enumerate(c['cotejo'], 1):
            ico, tx = RES_TX[x['res']]
            chip = (' class="est-chip est-pendiente" data-pend="red-%s-%d"' % (e(c['id']), k)) if x['res'] == 'pendiente' else ''
            partes.append('<li><p class="col-dice">«%s»</p><p><span%s>%s %s</span> %s</p><small>%s</small></li>'
                          % (e(x['dice']), chip, ico, tx, e(x['explica']), liga(x['url'], x['fuente']) if x.get('url') else e(x['fuente'])))
        partes.append('</ol>')
    if c.get('medios'):
        partes.append('<h2 class="nt-sub" id="medios">🗞️ Cómo lo contaron otros medios</h2>'
                      '<p>Titulares tal como los publicaron, <b>sin verificar</b>: son el punto de partida, no la fuente.</p><ul class="nt-medios">')
        partes += ['<li><b>%s</b>%s: %s</li>' % (e(m['medio']), (' · ' + e(m['fecha'])) if m.get('fecha') else '',
                                                 liga(m['url'], m['titulo'], 'noopener noreferrer nofollow')) for m in c['medios']]
        partes.append('</ul>')
    if c.get('sigue'):
        partes.append('<h2 class="nt-sub" id="sigue">🗓️ Lo que sigue</h2><ul>')
        partes += ['<li>%s</li>' % liga(x['url'], x['que']) for x in c['sigue']]
        partes.append('</ul>')
    partes.append('<h2 class="nt-sub" id="fuentes">📎 Documentos que la sostienen</h2><ol>')
    partes += ['<li>%s</li>' % liga(f['url'], f['nombre']) for f in c.get('fuentes', [])]
    partes.append('</ol><p class="col-act">Verificado al %s.</p>' % e(c.get('actualizado', c.get('fecha'))))
    partes.append('<p class="nt-acciones"><a class="nt-btn" href="%s#col-%s">🧮 La nota completa, con la cuenta, nuestros datos y el glosario</a> '
                  '<a class="nt-btn nt-btn-sec" href="herramienta-inspector-pregunta.html?modo=periodista&amp;q=%s">💬 Pregúntale al Auditor</a></p>'
                  % (DIARIO, e(c['id']), e(c['titulo'][:120])))
    partes.append('<p class="col-replica-pie">¿Esta nota te alude con un dato inexacto o falso? <a href="derecho-de-replica.html">Ejerce tu derecho de réplica</a>: se publica gratis, íntegra y sin comentarios.</p>')
    partes.append('</article>')
    url = sitio + AL_MOMENTO % c['id']
    ld = {'@context': 'https://schema.org', '@type': 'NewsArticle', 'headline': c['titulo'][:110], 'description': c['balazo'],
          'datePublished': _iso(c['fecha']), 'dateModified': _iso(c.get('actualizado', c['fecha'])), 'inLanguage': 'es-MX',
          'mainEntityOfPage': url, 'url': url,
          'author': {'@type': 'Organization', 'name': 'Redacción Auditavisión', 'url': sitio},
          'publisher': {'@type': 'Organization', 'name': 'Auditavisión', 'url': sitio},
          'isBasedOn': [x['url'] for x in ([c['nota']] if c.get('nota') else []) + c.get('medios', [])],
          'citation': [f['url'] for f in c.get('fuentes', []) if f['url'].startswith('http')]}
    partes.append('<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'))
    return '\n'.join(partes)


def paginas_al_momento():
    import asistente_personajes
    from apartados import SITIO
    cols, _ = asistente_personajes.columnas()
    out = []
    for c in cols:
        if c['seccion'] != 'Al momento':
            continue
        out.append({
            'archivo': AL_MOMENTO % c['id'], 'menu': c['titulo'], 'menu_archivo': ARCHIVO,
            'padre': (DIARIO, 'Auditavisión Noticias'),
            'icono': c.get('icono', '⏱️'), 'titulo': c['titulo'], 'lema': 'Al momento · %s · Redacción Auditavisión' % c['fecha'],
            'entrada': c['balazo'],
            'estilos': ['columnas.css'] + ESTILOS,
            'secciones': [{'id': 'nota', 'titulo': c['titulo'], 'texto': '', 'sin_cab': True, 'tarjetas': [],
                           'bloque': _nota_html(c, SITIO)}],
        })
    return out
