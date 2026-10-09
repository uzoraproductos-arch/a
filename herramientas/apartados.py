#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera las paginas de apartado del indice de Auditavision.

Desde el 08-10-2026, seis apartados del indice (Herramientas, Busca y
verifica, Sigue el dinero, Descarga los datos, Aprende y Participa) ya no se
desglosan en un menu: cada uno abre su propia pagina, con la informacion
ordenada por secciones. Desde el 09-10-2026 «Datos de referencia» (el radar
hacendario) tambien: se fusiono con Descarga los datos en una sola pagina.

Las tarjetas de cada pagina llevan al auditor con index.html?ir=destino
(&ancla=id). El motor (audit-engine.js, funcion irDesdeApartado) solo acepta
los destinos de su lista y limpia la direccion al llegar.

Uso:
    python3 herramientas/apartados.py      # regenera las seis paginas

Toma el sello de version de index.html, asi que hay que correrlo despues de
herramientas/sello.py (sello.py ya lo llama solo). Las paginas se escriben con
saltos de linea CRLF, la convencion del proyecto. Para cambiar su contenido,
edita este archivo y vuelve a correrlo: no edites a mano los .html generados.
"""
import html
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%230c0e15'/%3E%3Cg stroke='%23c9a84c' stroke-width='3.2' stroke-linecap='round' fill='none'%3E%3Cpath d='M32 12v38'/%3E%3Cpath d='M20 50h24'/%3E%3Cpath d='M14 22h36'/%3E%3Cpath d='M14 22l-6 13a7 7 0 0 0 12 0z'/%3E%3Cpath d='M50 22l-6 13a7 7 0 0 0 12 0z'/%3E%3C/g%3E%3Ccircle cx='32' cy='12' r='3.4' fill='%23f3cf65'/%3E%3C/svg%3E")


# El radar hacendario, que vivia en el menu «Datos de referencia» de la
# portada, se muda a la pagina de datos (09-10-2026).
RADAR = open(os.path.join(RAIZ, 'herramientas', 'plantillas', 'radar.html'), encoding='utf-8').read().rstrip().replace('\n', '\n        ')


def ir(destino, ancla=None):
    """Direccion de una tarjeta: el auditor con su destino."""
    url = 'index.html?ir=' + destino
    if ancla:
        url += '&amp;ancla=' + ancla
    return url


# Cada tarjeta: (icono, nombre, descripcion, destino, nota de fuente o None,
# rubro de color o None). Un destino que empieza con http abre afuera.
# Las cifras son las mismas que tenia el menu, con la misma fuente.
APARTADOS = [
    {
        'archivo': 'herramientas.html',
        'menu': 'Herramientas',
        'icono': '🧰',
        'titulo': 'Herramientas para seguir el dinero público',
        'lema': 'El gasto público, a la vista',
        'entrada': ('Dicho fácil: <b>de dónde sale el dinero de todos, en qué se gasta y quién revisa que se use bien.</b> '
                    'Lo contamos con documentos oficiales, para que cualquier persona lo entienda y lo pueda revisar. '
                    'Aquí están los cuatro módulos del auditor; elige uno y pulsa «Comenzar».'),
        'nota': True,
        'guia': 'abajo',
        'secciones': [
            {
                'id': 'modulos',
                'titulo': 'Los cuatro módulos',
                'texto': ('Elige uno y pulsa «Comenzar»: al abrirlo te contamos qué trae. '
                          'El Circuito del Dinero ya no está aquí: se repartió, bloque por bloque, en los seis capítulos de '
                          '<a href="sigue-el-dinero.html">Sigue el dinero</a>.'),
                # Desde el 09-10-2026 la tarjeta solo lleva icono grande y
                # titulo (decision del autor): la frase y la cifra de cada
                # modulo se cuentan en su proemio, al pulsar «Comenzar».
                'modulos': True,
                'tarjetas': [
                    ('🏗️', 'Simulador de Inversión y Megaobras', '', ir('megaobras', 'moduloProemio'), None, 'obras'),
                    ('💳', 'Calculadora Cívica', '', ir('calculadora', 'moduloProemio'), None, 'calculadora'),
                    ('🔍', 'Modo Inspector', '', ir('verificador', 'moduloProemio'), None, 'inspector'),
                    ('🌎', 'Costo Ambiental', '', ir('ambiente', 'moduloProemio'), None, 'ambiente'),
                ],
            },
        ],
    },
    {
        'archivo': 'sigue-el-dinero.html',
        'menu': 'Sigue el dinero',
        'icono': '💰',
        'titulo': 'Sigue el dinero',
        'lema': 'Seis capítulos, del impuesto a la deuda',
        'entrada': ('El dinero público tiene un recorrido: se recauda, se aprueba, se gasta, baja a estados y municipios, '
                    'se pide prestado y, al final, te toca una parte. Aquí lo sigues capítulo por capítulo.'),
        'libro': ('Este apartado sigue el orden de <cite>Introducción al Derecho Económico</cite>, de Moisés Gómez Granillo y '
                  'Rosa María Gutiérrez Rosas (Editorial Esfinge, 1995), sobre todo sus capítulos 5 y 7. Cada capítulo trae una '
                  'franja <b>«Ayer y hoy»</b>: lo que explicaba el libro y cómo está hoy, con el documento oficial que lo sostiene. '
                  'Las cifras no se copian del libro: se toman de su fuente oficial vigente.'),
        'scripts': ['deuda-tiempo.js'],
        'secciones': [
            {
                'id': 'origen',
                'num': 1,
                'titulo': 'De dónde sale el dinero',
                'texto': 'Impuestos, ingresos petroleros y deuda: todo lo que autoriza la Ley de Ingresos, y su recorrido completo hasta el gasto.',
                'ayer': ('El capítulo 7 abre con la «Acción financiera del Estado para el equilibrio de la economía» (p. 96), antes de pasar al presupuesto, a la ley de gasto y a la de deuda.',
                         'Cada año la <b>Ley de Ingresos de la Federación</b> dice cuánto puede recaudar y cuánto puede pedir prestado la Federación (la de 2026 se publicó en el DOF el 7 de noviembre de 2025). Contribuir al gasto público es una obligación del artículo 31, fracción IV de la Constitución.'),
                'tarjetas': [
                    ('🏛️', 'El camino del dinero, en cuatro etapas', 'Se recauda, se aprueba, se ejerce y se revisa: cuánto mueve cada etapa y qué ley la gobierna. Pulsa «Contabilizar».', ir('presupuesto', 'eb-arquitectura'), None, 'dinero'),
                    ('💰', 'Cuánto dinero es', 'Los $10.19 billones aprobados para 2026, la cifra total antes de partirla.', ir('presupuesto', 'eb-cuanto'),
                     'Presupuesto de Egresos de la Federación 2026, art. 1', 'dinero'),
                    ('📥', 'De dónde sale cada peso', 'El ingreso federal de 2026, renglón por renglón, tal como lo enumera el artículo 1o. de la Ley de Ingresos.', ir('presupuesto', 'eb-ingresos'), None, 'dinero'),
                    ('📏', '¿A qué equivale?', 'Tres comparaciones para dimensionar las cifras, con la operación a la vista.', ir('presupuesto', 'eb-equivale'), None, 'dinero'),
                    ('🔦', 'Lo que la cifra grande no dice', 'Cinco lecturas que no aparecen en el anuncio presupuestal y que cambian el sentido del total.', ir('presupuesto', 'eb-ciegos'), None, 'inspector'),
                    ('📈', 'Paquete Económico 2027', 'La proyección de ingresos y gasto para 2027, sus supuestos, riesgos y puntos ciegos.', ir('proyeccion2027'), None, 'dinero'),
                ],
            },
            {
                'id': 'decide',
                'num': 2,
                'titulo': 'Quién lo decide',
                'texto': 'El Congreso autoriza los ingresos y la deuda; la Cámara de Diputados aprueba el gasto. Y los Poderes también cuestan.',
                'ayer': ('El capítulo 5 explica las facultades económicas del Congreso de la Unión, del Senado y de la Cámara de Diputados (pp. 74-76), y las de la Asamblea de Representantes del Distrito Federal (p. 77).',
                         'Las facultades siguen en los artículos 73 y 74 de la Constitución: la fracción IV del 74 da a los diputados la aprobación anual del Presupuesto de Egresos. El Distrito Federal es hoy la <b>Ciudad de México</b>, con su propio Congreso, desde la reforma constitucional publicada en el DOF el 29 de enero de 2016.'),
                'tarjetas': [
                    ('⚖️', 'Lo que Cuestan el Congreso y la Judicatura', 'Presupuesto 2026, gasto auditado 2024 y sueldos netos oficiales.', ir('poderes'), None, 'dinero'),
                ],
            },
            {
                'id': 'gasta',
                'num': 3,
                'titulo': 'Quién lo gasta y en qué',
                'texto': 'Cuánto recibe cada Secretaría, qué obras se pagan y qué le cuesta al ambiente.',
                'ayer': ('«Presupuesto y gasto público» (p. 97) reparte el Presupuesto de 1994 en sus Cuadros 1 y 2, y la sección 3 (p. 103) explica la Ley de Presupuesto, Contabilidad y Gasto Público Federal de 1976.',
                         'Esa ley fue abrogada: desde 2006 rige la <b>Ley Federal de Presupuesto y Responsabilidad Hacendaria</b> (DOF 30 de marzo de 2006). La clasificación funcional del gasto de 2026 la publican los Criterios Generales de Política Económica 2027 (cuadro de la p. 39).'),
                'tarjetas': [
                    ('🏢', 'En qué se va: ramos y dependencias', 'Cuánto recibe cada Secretaría, en bloques proporcionales: de la función al ramo y al programa.', ir('presupuesto', 'eb-egresos'), None, 'dinero'),
                    ('🌡️', '¿Cuánto margen tiene el presupuesto?', 'Lo que ya está comprometido antes de empezar: deuda, participaciones y gasto programable, en un termostato.', ir('presupuesto', 'eb-salud'), None, 'dinero'),
                    ('📒', 'El estado de resultados del Gobierno', 'La Cuenta Pública 2024 leída como un negocio: actividades, flujos, situación financiera y gasto social.', ir('presupuesto', 'eb-cuenta-federal'), None, 'dinero'),
                    ('🏗️', 'Inversión Pública &amp; Megaobras', 'Presupuesto, costo y pérdidas de las grandes obras, de Tren Maya y Dos Bocas al AIFA. Fuentes por obra en verificación.', ir('megaobras'), None, 'obras'),
                    ('🌎', 'Costo Ambiental', 'El daño ambiental en pesos, su promedio por habitante, el servicio municipal de basura y el presupuesto ambiental 2026-2027.', ir('ambiente'), None, 'ambiente'),
                ],
            },
            {
                'id': 'baja',
                'num': 4,
                'titulo': 'A dónde baja',
                'texto': 'El dinero federal llega a los 32 estados y a los 2,479 municipios, y ahí se suma a lo que cada uno recauda.',
                'ayer': ('El Cuadro 1 del capítulo 7 ya separaba, dentro del Presupuesto de 1994, lo que la Federación destinaba a estados y municipios.',
                         'Hoy viaja por dos vías: las <b>participaciones</b> (Ramo 28), de libre uso, y las <b>aportaciones</b> (Ramo 33), etiquetadas por la Ley de Coordinación Fiscal para salud, educación, infraestructura y seguridad.'),
                'tarjetas': [
                    ('📍', 'El mapa del gasto federalizado', 'El tramo del gasto que viaja a los 32 estados, sobre el territorio y de mayor a menor.', ir('presupuesto', 'eb-mapa'), None, 'dinero'),
                    ('🗺️', 'Las 32 Entidades: del Peso Federal al Estatal', 'Los tres pisos de la hacienda, participaciones (Ramo 28), aportaciones (Ramo 33) y el circuito de cada estado.', ir('territorio'), None, 'dinero'),
                    ('🏘️', 'Los 2,479 Municipios: Predial y Transferencias', 'Padrón INEGI EFIPEM con la ficha financiera de cada municipio: predial, participaciones, FORTAMUN y FISMDF.', ir('municipios'), None, 'dinero'),
                ],
            },
            {
                'id': 'deuda',
                'num': 5,
                'titulo': 'Cuánto debemos',
                'texto': 'La deuda pública de 1994 a la proyección de 2027, sexenio por sexenio. Pulsa «Contabilizar» y mírala crecer.',
                'ayer': ('La sección 4 del capítulo 7 (p. 104) explica la Ley General de Deuda Pública y su Gráfica 1 sigue la deuda externa de 1988 a 1994, en dólares.',
                         'La misma ley se llama hoy <b>Ley Federal de Deuda Pública</b> (decreto del DOF del 27 de abril de 2016). Y la deuda se mide con un indicador más amplio, el saldo histórico de los requerimientos financieros del sector público (SHRFSP), que Hacienda publica desde 2000.'),
                'bloque': ('<div class="dt" id="deudaTiempo">\n'
                           '          <noscript><p>La línea de tiempo necesita JavaScript. La serie, con sus fuentes, está en el auditor.</p></noscript>\n'
                           '        </div>'),
                'tarjetas': [
                    ('⏱️', 'El Reloj de la Deuda', 'Lo que el país se endeuda, paga de intereses y pierde por segundo, con su contador en vivo.', ir('calculadora', 'eb-ccreloj'), None, 'inspector'),
                ],
            },
            {
                'id': 'ati',
                'num': 6,
                'titulo': 'Y a ti, ¿cuánto te toca?',
                'texto': 'Escribe tu sueldo y mira a qué rubros, fondos y pago de deuda se van tus impuestos.',
                'tarjetas': [
                    ('🧮', 'Calculadora Cívica de Tu Sueldo', 'A qué rubros y fondos se van los impuestos de tu nómina, con tu ticket cívico.', ir('calculadora'), None, 'calculadora'),
                ],
            },
        ],
    },
    {
        'archivo': 'descarga-los-datos.html',
        'menu': 'Datos',
        'icono': '💾',
        'titulo': 'Los datos: cifras de referencia y descargas',
        'lema': 'Datos abiertos con su fuente',
        'entrada': ('Todo lo que ves en el auditor sale de documentos oficiales. Aquí están las cifras de referencia '
                    'para poner el gasto en perspectiva, con su fuente, y los archivos que abren en Excel para que '
                    'hagas tus propias cuentas.'),
        'scripts': ['radar-datos.js'],
        'secciones': [
            {
                'id': 'radar',
                'titulo': '📡 Radar hacendario: cifras en perspectiva',
                'texto': ('Las cifras grandes del erario y lo que equivalen por segundo mientras lees. '
                          'Toca una cifra para ver cómo se calcula y de dónde sale. Antes vivía en el menú «Datos de referencia».'),
                'bloque': RADAR,
                'tarjetas': [],
            },
            {
                'id': 'abiertos',
                'titulo': '💾 Datos abiertos',
                'texto': 'Bases en CSV, listas para revisar.',
                'tarjetas': [
                    ('📥', 'Descarga en CSV (abre en Excel)', 'Siete bases con fuente oficial: municipios, sueldos netos, gasto de los Poderes, presupuesto ambiental, auditorías de la ASF por estado, lista 69-B y documentos.', ir('descargas'), None, 'dinero'),
                    ('🏘️', 'Base de Datos Municipal EFIPEM (INEGI)', 'Los 2,479 municipios con sus ingresos, predial, participaciones y fondos del Ramo 33, en CSV.', ir('csv-municipios'), None, 'dinero'),
                ],
            },
            {
                'id': 'informes',
                'titulo': '📑 Informes oficiales',
                'texto': 'Lo que revisó la Auditoría Superior y qué contiene cada archivo.',
                'tarjetas': [
                    ('🔎', 'Informes de la Cuenta Pública (ASF)', 'Qué revisó la Auditoría Superior en 2024, cuánto quedó por aclarar en tu estado y cuándo sale la siguiente entrega.', ir('verificador', 'cuentaPublicaASF'), None, 'inspector'),
                    ('📋', 'Diccionario de Datos', 'Qué contiene cada archivo de datos de la plataforma, campo por campo.', ir('diccionario'), None, None),
                ],
            },
        ],
    },
    {
        'archivo': 'aprende.html',
        'menu': 'Aprende',
        'icono': '📖',
        'titulo': 'Aprende',
        'lema': 'Biblioteca y kit del auditor ciudadano',
        'entrada': ('Las palabras del presupuesto, las leyes que lo rigen y las fuentes donde se publica, '
                    'explicadas en lenguaje llano. Para leer una cifra oficial no hace falta ser especialista. '
                    'Y para ponerte a prueba, una trivia con el estado de cuenta de cada presidente.'),
        'scripts': ['trivia-presidentes.js'],
        'secciones': [
            {
                'id': 'trivia',
                'titulo': '🎯 Trivia: el examen de los presidentes',
                'texto': ('Del Porfiriato a López Obrador: adivina, comprueba con la cifra oficial y, al final, mira el estado de cuenta '
                          'de cada presidente y el reloj de su deuda. Antes vivía en el módulo de Megaobras, como «Administración presidencial».'),
                'bloque': ('<div class="tp" id="triviaPres">\n'
                           '          <noscript><p>La trivia necesita JavaScript.</p></noscript>\n'
                           '        </div>'),
                'tarjetas': [],
            },
            {
                'id': 'biblioteca',
                'titulo': '🏛️ Biblioteca hacendaria',
                'texto': 'Marco legal, glosario y preguntas frecuentes.',
                'tarjetas': [
                    ('📖', 'Glosario de Términos Hacendarios', 'Los términos del presupuesto, la deuda y la fiscalización, explicados en lenguaje llano y con buscador.', ir('faq-glosario'), None, None),
                    ('⚖️', 'Marco Legal Hacendario', 'Los artículos que rigen el ingreso y el gasto: Constitución (73, 74, 115 y 134), Ley de Ingresos, LFPRH, Ley de Disciplina Financiera y reforma judicial.', ir('faq-marco-legal'), None, None),
                    ('💡', 'Preguntas Frecuentes en Casillas Didácticas', 'Cómo funciona el gasto público, qué revisa la Auditoría Superior y cómo auditar.', ir('faq-preguntas'), None, None),
                ],
            },
            {
                'id': 'kit',
                'titulo': '🧭 Kit del auditor ciudadano',
                'texto': 'Fuentes y guías para revisar por tu cuenta.',
                'tarjetas': [
                    ('🗺️', 'Enciclopedia Hacendaria (9 Módulos)', 'El compendio completo: presupuesto, Poderes, personajes, marco legal y comunidad.', 'enciclopedia.html', None, None),
                    ('📑', 'Compendio de Fuentes Oficiales', 'DOF, SHCP, ASF, Banxico, INEGI y Transparencia Presupuestaria, con su liga directa.', ir('fuentes'), None, None),
                    ('🍺', 'Pase y Guías del Auditor Cívico', 'Herramientas independientes de fiscalización ciudadana ($79/mes · Menos que dos caguamas).', ir('pase'), None, None),
                ],
            },
        ],
    },
    {
        'archivo': 'participa.html',
        'menu': 'Participa',
        'icono': '💬',
        'titulo': 'Participa',
        'lema': 'Ágora cívica y canales oficiales',
        'entrada': ('Contrasta posturas con fuentes, publica tu argumento y, si viste algo raro con el dinero público, '
                    'llévalo al canal oficial que corresponde. Sin correos, teléfonos ni rastreo.'),
        'secciones': [
            {
                'id': 'agora',
                'titulo': '💬 Ágora cívica y diálogos',
                'texto': 'Un espacio plural para argumentar con datos.',
                'tarjetas': [
                    ('🌐', 'Portal Público Digital', 'Un espacio plural para contrastar posturas con fuentes y responder con argumentos.', ir('portal', 'bloquePortal'), None, None),
                    ('✍️', 'Iniciar Nuevo Diálogo o Postura', 'Publica tu argumento con seudónimo, tu postura y tus fuentes.', ir('portal', 'portalNuevoDebateForm'), None, None),
                    ('🗣️', 'Cuaderno de argumentos (en este navegador)', 'Consulta los argumentos ciudadanos filtrados por Presupuesto, Megaobras, Deuda y SCJN.', ir('portal', 'portalFilterBar'), None, None),
                ],
            },
            {
                'id': 'garantias',
                'titulo': '🛡️ Garantías cívicas y formación',
                'texto': 'Qué pasa con lo que escribes y a dónde llevar un señalamiento.',
                'tarjetas': [
                    ('🔒', 'Tu Privacidad: a Dónde Va lo que Escribes', 'Sin correos, teléfonos ni rastreo. Qué se guarda, dónde y quién lo ve, dicho sin adornos.', ir('portal', 'comOrientacion'), None, None),
                    ('🏛️', 'Canales Oficiales de Denuncia', 'Las seis puertas donde un señalamiento se vuelve expediente: ASF, SABG, FGR, SAT, Transparencia y contralorías internas.', ir('portal', 'bloqueCanales'), None, 'inspector'),
                    ('📜', 'Decálogo del Ciudadano Auditor', 'Diez reglas que separan una queja de una denuncia, cada una con su fundamento legal.', ir('portal', 'decalogoWrap'), None, None),
                    ('📢', 'Reporta lo que Viste', 'Arma tu reporte con qué, dónde, cuándo y con qué prueba, y llévalo ya redactado a un canal oficial.', ir('reporta'), None, 'inspector'),
                ],
            },
        ],
    },
]

GUIA = '''<section class="apartado-guia" aria-labelledby="guiaTitulo">
        <h2 class="apartado-guia-titulo" id="guiaTitulo">Cómo se usa</h2>
        <ol class="apartado-pasos">
          <li><span class="apartado-paso-num" aria-hidden="true">1</span><span><b>Elige un tema.</b> Cada color es uno: las obras, tus impuestos, lo que revisó la Auditoría y el ambiente.</span></li>
          <li><span class="apartado-paso-num" aria-hidden="true">2</span><span><b>Pulsa «Comenzar».</b> Al abrirlo te contamos qué trae; adentro hay juegos y cuentas para descubrir las cifras tú mismo.</span></li>
          <li><span class="apartado-paso-num" aria-hidden="true">3</span><span><b>Mira la etiqueta de cada cifra.</b> <span class="est-chip est-oficial">oficial</span> viene de un documento del gobierno; <span class="est-chip est-derivado">derivado</span> lo calculamos con datos oficiales y te decimos cómo; <span class="est-chip est-pendiente">pendiente</span> la dependencia responsable no lo ha transparentado en un documento oficial, y te decimos cuál.</span></li>
        </ol>
      </section>'''


def esc_attr(s):
    return html.escape(s, quote=True)


def cabecera(actual, sello):
    items = []
    for a in APARTADOS:
        cur = ' aria-current="page"' if a['archivo'] == actual else ''
        items.append('      <div class="nav-menu-item"><a class="mega-menu-trigger" href="%s"%s>%s</a></div>'
                     % (a['archivo'], cur, a['menu']))
    return '''  <nav class="site-top-nav" aria-label="Navegación principal">
    <a class="nav-brand-group" href="index.html" title="Volver al inicio de Auditavisión">
      <span class="brand-logo-btn" aria-hidden="true"><img src="assets/auditor/img/logo-auditavision.svg" alt="" width="72" height="56"></span>
      <span class="nav-brand-text">
        <span class="nav-brand-title">Auditavisión</span>
        <span class="nav-brand-sub">El gasto público, a la vista</span>
      </span>
    </a>

    <button type="button" class="nav-hamburguesa" id="navHamburguesa" aria-expanded="false" aria-controls="navIndiceMovil" aria-label="Abrir el menú">
      <span class="nav-hamb-rayas" aria-hidden="true"><span></span><span></span><span></span></span>
      <span class="nav-hamb-txt">Menú</span>
    </button>

    <div class="nav-indice" id="navIndiceMovil">
    <div class="nav-center-links">
%s
    </div>

    <div class="nav-right-container">
      <div class="nav-right-actions">
        <a class="nav-action-btn nav-feedback-btn" href="index.html?ir=reporta" title="Ayúdanos a fiscalizar: comparte lo que viste y reporta anomalías presupuestales">
          <span>📢</span>
          <span>Cuéntanos lo que viste</span>
        </a>
        <button type="button" class="nav-action-btn nav-share-btn" id="apartadoCompartir" title="Compartir esta página o copiar su enlace">
          <span>🔗</span>
          <span>Compartir</span>
        </button>
        <a href="enciclopedia.html#tab-panel-faq" class="nav-action-btn nav-creator-badge" title="Creado por Inspector Meteoro · Enciclopedias Interactivas">
          <span>🪐</span>
          <span>Inspector Meteoro</span>
        </a>
      </div>
      <div class="nav-movil-ayuda">
        <p class="nav-movil-ayuda-tit">¿Viste algo raro con el dinero público?</p>
        <p class="nav-movil-ayuda-txt">Cuéntanos qué, dónde y cuándo. Te ayudamos a ordenarlo y a llevarlo al canal oficial que corresponde.</p>
        <a class="nav-movil-ayuda-btn" href="index.html?ir=reporta">📢 Cuéntanos lo que viste</a>
      </div>
    </div>
    </div>
  </nav>''' % '\n'.join(items)


def tarjeta(t, modulo=False):
    icono, nombre, desc, destino, fuente, rubro = t[:6]
    dato = t[6] if len(t) > 6 else None
    externo = destino.startswith('http')
    clase = 'apartado-tarjeta' + (' apartado-tarjeta-modulo' if modulo else '') + (' rubro-' + rubro if rubro else '')
    extra = ' target="_blank" rel="noopener noreferrer"' if externo else ''
    titulo = ' title="%s"' % esc_attr(fuente) if fuente else ''
    accion = 'Abrir en su sitio oficial ↗' if externo else ('Comenzar ➔' if 'moduloProemio' in destino else 'Abrir ➔')
    partes = ['        <a class="%s" href="%s"%s%s>' % (clase, destino, extra, titulo),
              '          <span class="apartado-tarjeta-icono" aria-hidden="true">%s</span>' % icono,
              '          <span class="apartado-tarjeta-nombre">%s</span>' % nombre]
    if desc:
        partes.append('          <span class="apartado-tarjeta-desc">%s</span>' % desc)
    if dato:
        partes.append('          <span class="apartado-tarjeta-dato"><strong>%s</strong><span>%s</span></span>' % dato)
    partes.append('          <span class="apartado-tarjeta-accion">%s</span>' % accion)
    partes.append('        </a>')
    return '\n'.join(partes)


def pagina(a, sello):
    secciones = []
    for s in a['secciones']:
        num = ('<span class="apartado-cap-num" aria-hidden="true">%d</span>' % s['num']) if s.get('num') else ''
        titulo = ('Capítulo %d. ' % s['num'] if s.get('num') else '')
        ayer = ''
        if s.get('ayer'):
            ayer = '''
        <div class="apartado-ayer">
          <div><span class="apartado-ayer-tit">📘 En el libro (1995)</span>%s</div>
          <div><span class="apartado-ayer-tit">📍 Hoy (2026)</span>%s</div>
        </div>''' % s['ayer']
        bloque = ('\n        <div class="apartado-bloque">\n        %s\n        </div>' % s['bloque']) if s.get('bloque') else ''
        secciones.append('''      <section class="apartado-seccion%s" id="%s" aria-labelledby="%s-tit">
        <div class="apartado-seccion-cab">
          <h2 class="apartado-seccion-titulo" id="%s-tit">%s<span class="sr-only">%s</span>%s</h2>
          <p class="apartado-seccion-texto">%s</p>
        </div>%s%s%s
      </section>''' % (' apartado-seccion-modulos' if s.get('modulos') else '', s['id'], s['id'], s['id'], num, titulo, s['titulo'], s['texto'], ayer, bloque,
                       ('\n        <div class="apartado-rejilla%s">\n%s\n        </div>' % (
                           ' apartado-rejilla-modulos' if s.get('modulos') else '',
                           '\n'.join(tarjeta(t, s.get('modulos')) for t in s['tarjetas'])))
                       if s['tarjetas'] else ''))

    if len(a['secciones']) > 1:
        saltos = '\n'.join('          <a href="#%s">%s%s</a>' % (
            s['id'], ('<span class="apartado-cap-num" aria-hidden="true">%d</span>' % s['num']) if s.get('num') else '', s['titulo'])
            for s in a['secciones'])
        en_pagina = '''      <nav class="apartado-saltos" aria-label="En esta página">
          <span class="apartado-saltos-tit">En esta página:</span>
%s
      </nav>''' % saltos
    else:
        en_pagina = ''

    nota = ('<a class="apartado-nota" href="index.html?ir=nota">📖 Qué son las finanzas públicas y qué encontrarás aquí</a>'
            if a.get('nota') else '')
    guia = GUIA if a.get('guia') else ''
    guia_abajo = ''
    if a.get('guia') == 'abajo':
        guia, guia_abajo = '', '\n\n      ' + GUIA
    if a.get('libro'):
        guia = (guia + '\n      ' if guia else '') + ('<aside class="apartado-libro"><span class="apartado-libro-ico" aria-hidden="true">📘</span>'
                                                       '<p>%s</p></aside>' % a['libro'])
    scripts = ''.join('\n  <script src="assets/auditor/js/%s?v=%s"></script>' % (js, sello) for js in a.get('scripts', []))
    titulo_doc = '%s · Auditavisión' % re.sub('<[^>]+>', '', a['menu'])
    descripcion = re.sub('<[^>]+>', '', a['entrada'])

    return '''<!DOCTYPE html>
<!-- Página generada por herramientas/apartados.py: no la edites a mano. -->
<html lang="es" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo_doc}</title>
  <meta name="description" content="{descripcion}">
  <meta name="theme-color" content="#0b2a63">
  <meta name="color-scheme" content="light">
  <link rel="icon" href="{favicon}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/auditor/css/auditavision.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/civico.css?v={sello}">
  <link rel="stylesheet" href="assets/auditor/css/apartados.css?v={sello}">
</head>
<body data-pagina="apartado">
{cabecera}

  <main class="apartado" id="contenido">
    <header class="apartado-cab">
      <div class="apartado-ancho">
        <nav class="apartado-migas" aria-label="Estás en"><a href="index.html">Inicio</a> <span aria-hidden="true">›</span> <span>{menu}</span></nav>
        <span class="apartado-lema">{icono} {lema}</span>
        <h1 class="apartado-titulo">{titulo}</h1>
        <p class="apartado-entrada">{entrada}</p>
        {nota}
      </div>
    </header>

    <div class="apartado-ancho apartado-cuerpo">
{en_pagina}
      {guia}
{secciones}{guia_abajo}
    </div>
  </main>

  <footer class="apartado-pie">
    <div class="apartado-ancho">
      <a class="apartado-volver" href="index.html">← Volver al auditor</a>
      <span class="apartado-pie-txt">Auditavisión · Toda cifra lleva su fuente oficial. Versión publicada: <b>{sello}</b></span>
    </div>
  </footer>

  <script src="assets/auditor/js/apartados.js?v={sello}"></script>{scripts}
</body>
</html>
'''.format(titulo_doc=titulo_doc, descripcion=esc_attr(descripcion), favicon=FAVICON, sello=sello,
           cabecera=cabecera(a['archivo'], sello), menu=a['menu'], icono=a['icono'], lema=a['lema'],
           titulo=a['titulo'], entrada=a['entrada'], nota=nota, en_pagina=en_pagina, guia=guia, guia_abajo=guia_abajo, scripts=scripts,
           secciones='\n\n'.join(secciones))


# Paginas que dejaron de existir y redirigen a donde se mudo su contenido.
# Busca y verifica se fusiono con el Modo Inspector el 09-10-2026.
REDIRECCIONES = {
    'busca-y-verifica.html': ('index.html?ir=verificador&amp;ancla=moduloProemio', 'Busca y verifica',
                              'Ahora vive dentro del Modo Inspector, en la parte «Busca y verifica».'),
}


def redireccion(destino, nombre, texto):
    return '''<!DOCTYPE html>
<!-- Página generada por herramientas/apartados.py: no la edites a mano. -->
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{nombre} · Auditavisión</title>
  <meta name="robots" content="noindex">
  <meta http-equiv="refresh" content="0; url={destino}">
  <link rel="icon" href="{favicon}">
  <script>window.location.replace('{url}');</script>
</head>
<body style="font-family:system-ui,sans-serif;background:#ffffff;color:#1c2a44;padding:24px">
  <p><b>{nombre}</b> cambió de lugar. {texto} <a href="{destino}">Ir ahora ➔</a></p>
</body>
</html>
'''.format(nombre=nombre, destino=destino, favicon=FAVICON, url=destino.replace('&amp;', '&'), texto=texto)


def generar(sello=None):
    if sello is None:
        d = open(os.path.join(RAIZ, 'index.html'), 'rb').read().decode('utf-8')
        m = re.search(r'id="selloVersion">([0-9a-z]+)<', d)
        if not m:
            print('ERROR: no encontré el sello en index.html')
            return 1
        sello = m.group(1)
    for a in APARTADOS:
        texto = pagina(a, sello).replace('\r\n', '\n').replace('\n', '\r\n')
        open(os.path.join(RAIZ, a['archivo']), 'wb').write(texto.encode('utf-8'))
    for archivo, datos in REDIRECCIONES.items():
        texto = redireccion(*datos).replace('\n', '\r\n')
        open(os.path.join(RAIZ, archivo), 'wb').write(texto.encode('utf-8'))
    print('apartados: %d páginas generadas con el sello %s' % (len(APARTADOS), sello))
    # Las paginas de Auditoria en imagenes comparten cabecera y sello.
    import auditorias
    import expedientes
    auditorias.generar(sello)
    return expedientes.generar(sello)


if __name__ == '__main__':
    sys.exit(generar())
