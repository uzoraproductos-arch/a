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
    ('verifica', '⚖️', 'Verifica', 'Verifica una noticia',
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
    ('seguir', '🔔', 'Seguimiento', 'Seguimiento: el caso no se olvida',
     'Cada caso abierto dice qué documento falta para cerrarlo. Síguelo y te avisamos cuando llegue, o pídele al Auditor que siga uno nuevo.'),
    ('mesa', '📡', 'Mesa de redacción', 'Mesa de redacción: lo que estamos jalando',
     'Titulares sobre finanzas públicas que juntamos de los buscadores de noticias para alimentar nuestra base. Llegan <b>sin verificar</b>: '
     'son la materia prima, no la noticia. Cualquiera la puedes mandar al verificador.'),
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
]


def datos():
    return {'agenda': AGENDA, 'mesa': [{'id': i, 't': t, 'q': q} for i, t, q in MESA], 'bandeja': BANDEJA}


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


def construir(base, ref):
    import insp_nota
    nav = '\n'.join('    <a href="#%s"><span aria-hidden="true">%s</span> %s</a>' % (i, ico, n) for i, ico, n, _t, _e in SECCIONES)
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
        'mesa': ('<div id="noticiasMesa" class="nt-mesa"><noscript><p>La mesa de redacción necesita JavaScript.</p></noscript></div>'),
        'agenda': ('<div id="noticiasAgenda" class="nt-agenda"><noscript><p>La agenda necesita JavaScript.</p></noscript></div>\n'
                   '<p class="nt-pie">Son los plazos máximos que fija la ley: el documento puede llegar antes. Cuando la fecha cae en día inhábil '
                   'o la ley prevé una prórroga, puede moverse. Los «días que faltan» son nuestra cuenta ' + insp_nota_chip('derivado') + '.</p>'),
        'metodo': _metodo(),
    }
    clases = {'columnas': ' nt-sec-opinion', 'verifica': ' nt-sec-verifica', 'portada': ' nt-sec-portada'}
    partes = [_sec(i, ico, t, e, cuerpos[i], clases.get(i, '')) for i, ico, _n, t, e in SECCIONES]
    return ('<div class="nt-diario">\n'
            '<header class="nt-cabezal">\n'
            '  <p class="nt-cabezal-linea"><span id="noticiasHoy">Las finanzas públicas de México</span><span>Cada cifra, con su documento</span></p>\n'
            '  <p class="nt-nombre">Auditavisión <span>Noticias</span></p>\n'
            '  <p class="nt-lema">La noticia, verificada. La opinión, con documentos. Y el caso, en seguimiento.</p>\n'
            '</header>\n'
            '<nav class="nt-barra" aria-label="Secciones del diario">\n%s\n</nav>\n%s\n'
            '<script type="application/json" id="noticiasDatos">%s</script>\n'
            '</div>') % (nav, '\n'.join(partes), json.dumps(datos(), ensure_ascii=False).replace('</', '<\\/'))


def insp_nota_chip(estado):
    return '<span class="est-chip est-%s">%s</span>' % (estado, estado)
