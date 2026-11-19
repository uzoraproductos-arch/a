#!/usr/bin/env python3
"""Las fichas de cada servicio: lo que la plataforma ya hace y dónde vive.

Pedido del autor, 18-11-2026: «actualiza, potencializa y mejora nuestro portal
de servicios, así como sus respectivas páginas autónomas… todo deberá estar
vinculado con el chat, la Enciclopedia, debiendo integrar debidamente nuestra
Biblioteca del Erario», y «los servicios integrando todo lo nuevo que puede
hacer la plataforma».

Cada servicio de `SERVICIOS` (apartados.py) tiene aquí su ficha, y con ella su
página (`servicio-<id>.html`) y su respuesta en el chat (`srv_<id>`):

- `hace`: lo que la plataforma ya hace y con qué empezar gratis
  (ícono, título, texto, liga, etiqueta). «Nuevo» marca lo de noviembre.
- `auditor`: preguntas que el chat ya contesta, con su modo.
- `enciclopedia`: las páginas de la Enciclopedia que explican el tema.
- `glosario`: términos del Diccionario de la Biblioteca del Erario (tal como
  vienen en la base).
- `refs`: fichas de Referencias de la Biblioteca (sus ids `ref-…`).
- `pal`: con qué palabras se pide en el chat (expresión válida en Python y en
  JavaScript, sobre el texto sin acentos y en minúsculas).
- `no`: lo que el servicio no hace, en una oración.

**Ninguna cifra se escribe aquí** (AGENTS §2) y **nunca un monto**: la forma de
cobro vive en `COBRO`. **Un servicio nuevo necesita aquí su ficha**, o la
generación se detiene; una liga, un ancla, un término o una referencia que no
existan también la detienen (`revisar()`).
"""
import html
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINA = 'servicio-%s.html'
CHAT = 'herramienta-inspector-pregunta.html'

FICHAS = {
    'diligencia': {
        'hace': [
            ('🪪', 'Revisa a tu contraparte', 'Una sola ficha por RFC: las listas del SAT (arts. 69, 17-H Bis, 69-B y 69-B Bis), '
             'el Directorio de Sancionados, la OFAC, la ONU y sus contratos de ComprasMX.', 'herramienta-inspector-padron.html', 'Nuevo'),
            ('🧾', 'La lista 69-B completa', 'Presuntos, definitivos, desvirtuados y sentencias favorables, con el oficio de cada publicación.',
             'herramienta-inspector-efos.html', 'Gratis'),
            ('🏛️', 'Sus contratos con el gobierno', 'Los contratos de ComprasMX de cada empresa, por institución, con su importe y su fecha.',
             'contratos-publicos.html', 'Gratis'),
            ('🏢', 'Los grupos y sus filiales', 'Con qué empresas aparece cada grupo en ComprasMX; el vínculo que solo dice la prensa se queda pendiente.',
             'contratos-publicos.html#grupos', 'Nuevo'),
            ('✂️', 'Señales de fraccionamiento', 'Compras directas partidas que en 90 días rebasan el tope del PEF: señal para revisar, no irregularidad.',
             'contratos-publicos.html#fraccionamiento', 'Gratis'),
        ],
        'auditor': [('¿Cómo reviso a un proveedor antes de contratarlo?', 'inspector'), ('¿Mi proveedor está en la lista negra del SAT?', 'inspector'),
                    ('Contratos de Grupo Carso', 'inspector')],
        'enciclopedia': [('aprende-auditoria.html#met-lavado', 'Cómo se audita: el lavado de dinero'),
                         ('aprende-fraude-en-numeros.html', 'El fraude en números')],
        'glosario': ['Empresa Fantasma (EFOS)', 'EFOS y EDOS (Factureras)', 'Beneficiario Controlador', 'Adjudicación Directa', 'Licitación Pública'],
        'refs': ['ref-cff', 'ref-sat-69b', 'ref-comprasmx', 'ref-laassp', 'ref-lfpiorpi'],
        'pal': r'revision de (un |una |tu |mi )?(proveedor|empresa)|debida diligencia|ficha (del|de un|de tu) proveedor',
        'no': 'No dice si la operación existió ni si hubo un delito: eso lo acredita tu soporte y lo decide la autoridad.',
    },
    'contrapartes': {
        'hace': [
            ('🗂️', 'Tu cartera completa, en una matriz', 'Hasta 2,000 RFC de un CSV, un TXT o lo pegado de Excel: una fila por RFC y una columna por lista, '
             'que se descarga en CSV. Todo en tu navegador.', 'herramienta-inspector-padron.html#lote', 'Nuevo'),
            ('🔗', 'La cadena de terceros', 'De tus facturas XML salen el emisor, el receptor y los RFC «a cuenta de terceros» del CFDI 4.0, cada uno con su papel.',
             'herramienta-inspector-padron.html#lote', 'Nuevo'),
            ('🌐', 'Las listas internacionales', 'La OFAC del Tesoro de Estados Unidos y el Consejo de Seguridad de la ONU, junto a las del SAT.',
             'herramienta-inspector-padron.html', 'Nuevo'),
            ('🔔', 'La base al día', 'La 69-B, las listas del padrón y el Directorio de Sancionados se actualizan solos cada semana, con su huella.',
             'base-al-dia.html', 'Nuevo'),
        ],
        'auditor': [('¿Cómo reviso a mi cliente en las listas de lavado?', 'inspector'), ('¿Está en la OFAC el cártel de Sinaloa?', 'inspector'),
                    ('¿Cada cuándo se actualiza la base de datos?', 'ciudadano')],
        'enciclopedia': [('aprende-auditoria.html#met-lavado', 'Cómo se audita: el lavado de dinero'),
                         ('aprende-auditoria.html#met-control', 'Cómo se audita: el control interno')],
        'glosario': ['Actividad Vulnerable', 'Beneficiario Controlador', 'Empresa Fantasma (EFOS)', 'Control Interno'],
        'refs': ['ref-lfpiorpi', 'ref-cff', 'ref-sat-69b', 'ref-sat-padron-rfc'],
        'pal': r'contrapartes?|cartera de (clientes|proveedores)|matriz de (riesgo|listas)|cadena de terceros|listas? de (lavado|sanciones|pld)|(revision|revisar|revisen) (de )?(mis |nuestros |los )?clientes|compliance|cumplimiento pld|conocer a (mi|tu|su) cliente|\bkyc\b',
        'no': 'Una coincidencia es una señal para revisar, nunca una acusación: coincidir en un nombre no es ser la misma persona, y no presentamos tus avisos.',
    },
    'seguimiento': {
        'hace': [
            ('🔔', 'La 69-B comparada cada semana', 'El Vigía 69-B anota altas, cambios de situación, bajas y cambios de razón social, por RFC.',
             'herramienta-inspector-efos.html', 'Gratis'),
            ('📌', 'Mi Auditavisión', 'Tus proveedores y tus revisiones, guardados solo en tu navegador, para volver a ellos.', 'herramienta-inspector-mia.html', 'Gratis'),
            ('🗓️', 'Qué fuente se actualiza y cuándo', 'Cada fuente de la base con quién la publica, cada cuándo y cómo entra.', 'base-al-dia.html', 'Nuevo'),
            ('🗂️', 'Los casos que no se olvidan', 'Los expedientes de control interno se ponen al día cada mañana con la base.', 'expedientes-investigacion.html', 'Nuevo'),
        ],
        'auditor': [('Lista negra del SAT', 'inspector'), ('¿Cada cuándo se actualiza la base de datos?', 'ciudadano')],
        'enciclopedia': [('pilares.html#base', 'La base de datos, pilar de transparencia')],
        'glosario': ['EFOS y EDOS (Factureras)', 'Empresa Fantasma (EFOS)'],
        'refs': ['ref-cff', 'ref-sat-69b', 'ref-comprasmx'],
        'pal': r'vigia|vigilen|vigilar (mi|mis|a mis)|seguimiento periodico|me avisen|avisos? (de|cuando)|alertas? (de|cuando)',
        'no': 'El aviso dice qué cambió y con qué documento; qué hacer con tu proveedor lo decides tú.',
    },
    'facturas': {
        'hace': [
            ('📄', 'El Lector de facturas CFDI', 'Hasta 500 XML en tu navegador, sin subirlos: régimen, método y forma de pago, retención de IVA y la lista 69-B.',
             'herramienta-inspector-factura.html', 'Gratis'),
            ('🔁', 'Los complementos de pago', 'Qué facturas PPD ya tienen pago registrado, cuánto les queda y cuáles no tienen ninguno.',
             'herramienta-inspector-factura.html', 'Gratis'),
            ('🔗', 'Los terceros de tus facturas', 'Emisor, receptor y RFC «a cuenta de terceros», revisados contra todas las listas del padrón.',
             'herramienta-inspector-padron.html#lote', 'Nuevo'),
            ('📊', 'Tu estado de resultados', 'Cuadre, estructura, rentabilidad, tendencia, impuestos y deuda, desde un CSV o lo pegado de Excel.',
             'herramienta-inspector-resultados.html', 'Gratis'),
        ],
        'auditor': [('Revisa mi recibo de nómina', 'inspector'), ('¿Mi proveedor está en la lista negra del SAT?', 'inspector')],
        'enciclopedia': [('aprende-auditoria.html#met-fraude', 'Cómo se audita: el fraude'), ('aprende-fraude-en-numeros.html', 'El fraude en números')],
        'glosario': ['EFOS y EDOS (Factureras)', 'ISR, IVA e IEPS', 'Empresa Fantasma (EFOS)'],
        'refs': ['ref-cff', 'ref-sat-69b', 'ref-rmf2026', 'ref-liva'],
        'pal': r'facturas? por lote|lote de facturas|revisen (mis |nuestras |las )?facturas|revision de (mis |las )?facturas',
        'no': 'No sustituye a tu contador ni a tu sistema: revisa lo que dice la factura frente a la ley y a las listas.',
    },
    'nomina': {
        'hace': [
            ('🧮', 'La nómina completa', 'Lo que te retienen y lo que pone el patrón: IMSS e INFONAVIT en la empresa, ISSSTE y FOVISSSTE en el gobierno, '
             'con el costo de la plaza.', 'herramienta-calculadora-ticket-retienen.html', 'Nuevo'),
            ('📄', 'El recibo de nómina', 'El XML se lee en tu navegador: que cuadre, el ISR contra la tarifa del artículo 96, el subsidio y el salario base de cotización.',
             'herramienta-inspector-factura.html', 'Nuevo'),
            ('🪪', 'Quien te maquila la nómina', 'Su RFC contra las listas del SAT, la OFAC y la ONU.', 'herramienta-inspector-padron.html', 'Nuevo'),
        ],
        'auditor': [('Revisa mi recibo de nómina', 'inspector'), ('Trabajo en el gobierno y gano 20 mil al mes, ¿cuánto me retienen?', 'ciudadano'),
                    ('¿Qué son las cuotas al ISSSTE?', 'ciudadano')],
        'enciclopedia': [('herramienta-calculadora-ticket.html', 'Tu estado de cuenta cívico'), ('aprende-auditoria.html#met-control', 'Cómo se audita: el control interno')],
        'glosario': ['Recibo de Nómina (CFDI de nómina)', 'Retención del ISR (Tarifa del Artículo 96)', 'Subsidio para el Empleo',
                     'Salario Base de Cotización', 'Cuota Patronal del IMSS', 'Cuotas al ISSSTE', 'Artículo 127 Constitucional (Tope Salarial)'],
        'refs': ['ref-lisr', 'ref-lss', 'ref-subsidio-empleo-2026', 'ref-uma2026', 'ref-cpeum-art127'],
        'pal': r'revision de (la )?nomina|(revisen|auditen|chequen) (la |mi |nuestra )?nomina|auditoria de (la )?nomina|servicio de nomina',
        'no': 'Revisamos la nómina; no la calculamos ni la timbramos por nadie, y nunca mostramos el nombre, la CURP ni el número de seguridad social de quien trabaja.',
    },
    'gobernanza': {
        'hace': [
            ('🗄️', '¿Hasta cuándo guardas tus papeles?', 'El calendario de conservación: cada papel con su plazo, desde cuándo corre y su artículo '
             '(CFF, Código de Comercio, LSS, LFT, LFPIORPI y LFPDPPP), y la fecha mínima para lo de un año.', 'herramienta-inspector-conservacion.html', 'Nuevo'),
            ('✅', '¿Cumples con tus papeles?', 'El autodiagnóstico: 25 obligaciones de la ley sobre tus documentos y tus datos personales, contestas sí, no o no sé, '
             'y ves qué falta por área, con su artículo y qué hacer.', 'herramienta-inspector-cumplimiento.html', 'Nuevo'),
            ('📊', 'Tu matriz de riesgos documentales', 'Las mismas obligaciones en una matriz de probabilidad por gravedad, con lo que prevé la ley '
             'si fallas (la infracción y su artículo), para saber por dónde empezar.', 'herramienta-inspector-riesgos.html', 'Nuevo'),
            ('📑', 'Tus facturas, leídas', 'El XML se lee en tu navegador: lo que conviene revisar antes de archivarlo.', 'herramienta-inspector-factura.html', 'Gratis'),
            ('🔒', 'Cómo cuidamos la información', 'Lo que hacemos nosotros con los datos: medidas de seguridad y qué pasa si algo falla.',
             'aviso-de-privacidad.html#seguridad', 'Nuevo'),
        ],
        'auditor': [('¿Cuántos años debo guardar mis facturas?', 'ciudadano'), ('¿Hasta cuándo guardo los recibos de nómina?', 'inspector'),
                    ('¿Cuánto tiempo se guarda el expediente de un cliente en una actividad vulnerable?', 'inspector'),
                    ('¿Mi empresa cumple con sus papeles?', 'inspector'), ('Arma mi matriz de riesgos documentales', 'inspector')],
        'enciclopedia': [('aprende-auditoria.html#met-control', 'Cómo se audita: el control interno'),
                         ('aprende-auditoria.html#met-lavado', 'Cómo se audita: el lavado de dinero')],
        'glosario': ['Plazo de Conservación', 'Bloqueo de Datos Personales', 'Plazo para que el SAT te Revise (Caducidad)',
                     'Control Interno', 'Actividad Vulnerable', 'Recibo de Nómina (CFDI de nómina)'],
        'refs': ['ref-cff', 'ref-ccom', 'ref-lft', 'ref-lss', 'ref-lfpiorpi', 'ref-lfpdppp', 'ref-lga'],
        'pal': r'gobernanza documental|conservacion de (documentos|papeles|archivos|la contabilidad)|calendario de conservacion|'
               r'destruir (mis |los |nuestros )?(papeles|documentos|archivos|expedientes)|depurar (el |mi |nuestro )?archivo',
        'no': 'No es asesoría ni sustituye a tu contador o a tu abogado: te dice qué pide cada ley y desde cuándo corre, y nunca destruimos ni custodiamos tus documentos.',
    },
    'radiografia': {
        'hace': [
            ('🗺️', 'El Planisferio', 'Tu estado y sus municipios en diez dimensiones: dinero, deuda, inversión, congreso, justicia, ambiente, salud, '
             'administración, pobreza y fraude.', 'planisferio.html', 'Gratis'),
            ('🏦', 'A quién le debe', 'El Registro Público Único de Hacienda, crédito por crédito: el acreedor, la tasa, el destino y la fuente de pago.',
             'planisferio.html?d=deuda', 'Nuevo'),
            ('💰', 'Cuánto dinero es', 'Lo que baja de la Federación, lo que cobra el estado y lo que ingresan sus municipios.', 'planisferio-dinero.html', 'Gratis'),
            ('🧭', 'El Auditor de entes', 'El estado de cuenta, la salud financiera y el dictamen de cada estado y cada municipio.',
             'herramienta-inspector-entes.html', 'Gratis'),
        ],
        'auditor': [('¿A quién le debe Nuevo León?', 'inspector'), ('Muéstrame el mapa de la deuda de los estados', 'inspector'),
                    ('¿Qué municipio recibe más?', 'ciudadano')],
        'enciclopedia': [('numeros-baja-al-territorio.html', 'Baja al territorio'), ('numeros-mapa-del-gasto-federalizado.html', 'El mapa del gasto federalizado'),
                         ('marco-legal-tres-niveles.html', 'Las leyes del dinero en los tres niveles')],
        'glosario': ['Ramo 28 (Participaciones Federales)', 'Ramo 33 (Aportaciones Federales)', 'Deuda Subnacional', 'Hacienda Municipal',
                     'Ley de Disciplina Financiera (LDF)'],
        'refs': ['ref-ldf', 'ref-lcf', 'ref-shcp-alertas', 'ref-inegi-efipem', 'ref-asf-cp'],
        'pal': r'radiografia',
        'no': 'Es un documento estándar y sin opinión, el mismo para quien lo pida: no califica a ningún gobierno ni dice su partido.',
    },
    'temporada': {
        'hace': [
            ('📰', 'Contrasta una nota', 'La cifra de una nota contra el documento oficial, con su etiqueta: oficial, derivado o pendiente.',
             'herramienta-inspector-nota.html', 'Gratis'),
            ('📌', 'La memoria de promesas', 'Cada cifra que anuncia un gobierno, seguida al Presupuesto, la Cuenta Pública y la ASF.',
             'noticias-seguimiento.html#promesas', 'Gratis'),
            ('👁️', 'Los puntos ciegos', 'Lo que las notas suelen esconder, en reglas que el verificador aplica solo.', 'noticias-verifica.html#puntos-ciegos', 'Gratis'),
            ('🗂️', 'Los expedientes de control interno', 'Cada gran investigación con su bitácora, lo que sigue y lo que falta, al día cada mañana.',
             'expedientes-investigacion.html', 'Nuevo'),
        ],
        'auditor': [('Contrasta una nota', 'periodista'), ('¿Es cierto que el Tren Maya costó 500 mil millones?', 'periodista'),
                    ('quiero proponer una nota', 'periodista')],
        'enciclopedia': [('datos-legislativo-elecciones.html', 'Las elecciones'), ('noticias-verifica.html#metodo', 'Cómo trabajamos: del rumor al documento')],
        'glosario': ['Proceso Electoral Federal 2026-2027', 'Tope de Gastos de Campaña', 'OPLE (Organismo Público Local Electoral)', 'Nepotismo electoral'],
        'refs': ['ref-lgipe', 'ref-ley-replica', 'ref-ine-cg469-2026'],
        'pal': r'licencia de temporada|para (mi|nuestra|una) redaccion|redacciones',
        'no': 'Verificamos cifras contra documentos; no opinamos de candidaturas ni investigamos por encargo a una candidatura rival.',
    },
    'entrega': {
        'hace': [
            ('🏦', 'Lo que debe el gobierno que recibes', 'Sus créditos del Registro Público Único, uno por uno, y lo que reporta el Sistema de Alertas.',
             'planisferio.html?d=deuda', 'Nuevo'),
            ('🔎', 'Lo que dejó la ASF', 'Las auditorías de cada estado y lo que quedó por aclarar.', 'herramienta-inspector-asf.html', 'Gratis'),
            ('🧭', 'Su estado de cuenta', 'Lo que le entra, lo que gasta y su salud financiera, en el Auditor de entes.', 'herramienta-inspector-entes.html', 'Gratis'),
            ('📋', 'Lo que falta por publicar', 'Cada pendiente con su porqué y quién lo debe.', 'pendientes.html', 'Gratis'),
        ],
        'auditor': [('¿A quién le debe Nuevo León?', 'inspector'), ('¿Cuánto dejó por aclarar la ASF?', 'inspector')],
        'enciclopedia': [('numeros-cuentas-quien-autoriza-la-deuda.html', 'Quién autoriza la deuda'), ('datos-administracion-publica.html', 'La administración pública')],
        'glosario': ['Hacienda Municipal', 'Deuda Subnacional', 'Cuenta Pública', 'Informe Individual de Auditoría'],
        'refs': ['ref-ldf', 'ref-lgcg', 'ref-lfrcf', 'ref-shcp-alertas'],
        'pal': r'entrega[ -]recepcion|kit de entrega|lo que recibes|gobierno (que|electo) (entra|recibe)|transicion',
        'no': 'No sustituye el acta de entrega-recepción ni la revisión del órgano de control: te dice lo que dicen los documentos públicos.',
    },
    'revision': {
        'hace': [
            ('🔎', 'El Auditor y sus cuatro modos', 'Tu pregunta, contestada con la base: la cifra, qué quiere decir y su documento.', CHAT, 'Gratis'),
            ('📜', 'El dictamen cívico', 'La respuesta sellada, con folio y huella, que cualquiera puede volver a generar.', 'herramienta-inspector-dictamen.html', 'Gratis'),
            ('✅', 'Verifica un documento', 'Comprueba el folio o la huella de un estado de cuenta o un dictamen.', 'herramienta-inspector-verifica.html', 'Gratis'),
        ],
        'auditor': [('¿Es cierto que Jalisco debe 50 mil millones?', 'inspector'), ('Dictamen cívico', 'inspector')],
        'enciclopedia': [('enciclopedia-auditavision.html', 'La Enciclopedia'), ('pilares.html#base', 'La base de datos, pilar de transparencia')],
        'glosario': ['Auditar (Auditoría Gubernamental)', 'Cuenta Pública', 'Adjudicación Directa'],
        'refs': ['ref-lgtaip', 'ref-transparencia-presupuestaria', 'ref-asfdatos'],
        'pal': r'revision (documental|puntual)',
        'no': 'Es investigación documental y análisis de indicios: no es un peritaje ni asesoría legal.',
    },
    'expediente': {
        'hace': [
            ('🗂️', 'Los expedientes de control interno', 'Cada gran investigación en un solo lugar, hecha de dictámenes, con folio y huella, al día cada mañana.',
             'expedientes-investigacion.html', 'Nuevo'),
            ('📁', 'Los casos de la ASF', 'Los expedientes de casos por aclarar, con su documento.', 'expedientes.html', 'Gratis'),
            ('🔗', 'Nepotismo y parentesco', 'Qué ley alcanza a cada parentesco en un cargo público; un apellido igual nunca es prueba.',
             'herramienta-inspector-nepotismo.html', 'Gratis'),
            ('🏢', 'Los grupos y sus filiales', 'Las empresas con que contrata cada grupo, por RFC.', 'contratos-publicos.html#grupos', 'Nuevo'),
        ],
        'auditor': [('Expediente del Tren Maya', 'inspector'), ('Expediente de Segalmex', 'inspector'), ('Contratos de Grupo Carso', 'inspector')],
        'enciclopedia': [('informes-documentar-para-sancionar.html', 'Documentar para sancionar'), ('aprende-auditoria.html#met-forense', 'Cómo se audita: la auditoría forense')],
        'glosario': ['Auditoría Forense', 'Denuncia de Hechos (ASF)', 'Promoción de Responsabilidad Administrativa Sancionatoria (PRAS)', 'Informe Individual de Auditoría'],
        'refs': ['ref-lgra', 'ref-lfrcf', 'ref-asf-documentar', 'ref-cnpp'],
        'pal': r'expediente de investigacion|(pedir|pido|solicitar|encargar) (un |mi )?expediente',
        'no': 'Ordena lo que dicen los documentos públicos; una acusación no es una condena, y así se dice.',
    },
    'capacitacion': {
        'hace': [
            ('📚', 'Cómo se audita', 'Control interno, riesgos, fraude, prueba y lavado, cotejados con el Marco Integrado de Control Interno de la ASF.',
             'aprende-auditoria.html', 'Gratis'),
            ('⚖️', 'Las 20 matrices de la ASF', 'Cómo documenta la ASF una irregularidad para que se pueda sancionar.', 'informes-documentar-para-sancionar.html', 'Gratis'),
            ('📈', 'El informe semestral de la ASF', 'Lo que ha recuperado, sancionado y denunciado, cada semestre.', 'informes-semestral-asf.html', 'Gratis'),
            ('🗂️', 'Casos reales para practicar', 'Los expedientes de control interno, con su bitácora y lo que falta.', 'expedientes-investigacion.html', 'Nuevo'),
        ],
        'auditor': [('¿Qué es el informe Documentar para sancionar?', 'inspector'), ('¿Cuántos funcionarios ha sancionado la ASF?', 'inspector')],
        'enciclopedia': [('aprende-auditoria.html', 'Cómo se audita'), ('aprende-fraude-en-numeros.html', 'El fraude en números')],
        'glosario': ['Control Interno', 'Factores de Riesgo de Fraude (Triángulo del Fraude)', 'Auditoría de Desempeño', 'Auditoría Forense'],
        'refs': ['ref-asf-mici', 'ref-asf-documentar', 'ref-asf-semestral', 'ref-lgra'],
        'pal': r'talleres?|capacitacion|capacitar|cursos?',
        'no': 'El taller enseña el método con casos públicos; no certifica ni sustituye una formación profesional.',
    },
    'licencia': {
        'hace': [
            ('🧰', 'Las herramientas del Auditor', 'Megaobras, Calculadora Cívica, Modo Inspector y Costo Ambiental.', 'numeros-herramientas-del-auditor.html', 'Gratis'),
            ('⬇️', 'Descarga los datos', 'Los datos de la plataforma en archivos abiertos, con su fuente.', 'descarga-los-datos.html', 'Gratis'),
            ('🗓️', 'La base al día', 'Cada fuente con quién la publica, cada cuándo y cómo entra.', 'base-al-dia.html', 'Nuevo'),
            ('🗺️', 'El Planisferio', 'El mapa de México en diez dimensiones, con sus 2,478 municipios y alcaldías.', 'planisferio.html', 'Gratis'),
        ],
        'auditor': [('¿Cada cuándo se actualiza la base de datos?', 'ciudadano'), ('Dame mi estado de cuenta cívico', 'ciudadano')],
        'enciclopedia': [('enciclopedia-auditavision.html', 'La Enciclopedia'), ('pilares.html', 'Nuestros pilares')],
        'glosario': ['Cuenta Pública', 'PEF (Presupuesto de Egresos de la Federación)', 'LIF (Ley de Ingresos de la Federación)'],
        'refs': ['ref-lgtaip', 'ref-lsnieg', 'ref-transparencia-presupuestaria'],
        'pal': r'licencia (de (las )?herramientas|institucional|para (mi|nuestra))|licenciar',
        'no': 'Una licencia no da control sobre lo que la plataforma publica.',
    },
}

# Con qué palabras se pide una familia o un perfil: (clave de LINEAS o número
# de PERFILES, expresión). Solo cuentan si la pregunta habla de servicios.
PAL_LINEA = {
    'prevencion': r'fraudes?|lavado|pld|antilavado|prevenir|prevencion',
    'electoral': r'temporada electoral|elecciones?|electoral|campanas?|candidat\w*',
    'formacion': r'formacion|ensenar|universidad\w*|alumnos',
    'investigacion': r'investigacion(es)? a la medida|instituciones?',
}
PAL_PERFIL = [
    r'despachos? contables?|contador\w*|contaduria|fiscalistas?',
    r'abogad\w*|juridic\w*|oficial(es)? de cumplimiento',
    r'auditor\w*|organos? internos? de control|contralor\w*',
    r'periodistas?|reporter\w*|medios',
    r'candidat\w*|equipos? de campana|partidos?',
    r'regidor\w*|regidurias?|cabildos?|diputad\w*|congresos?',
    r'universidad\w*|academi\w*|profesor\w*|estudiantes?',
    r'tesorerias?|dependencias?|gobiernos? (municipal|estatal|local)\w*',
]


def _ancla_existe(liga):
    arch, _, ancla = liga.partition('#')
    arch = arch.partition('?')[0]
    ruta = os.path.join(RAIZ, arch)
    if not os.path.exists(ruta):
        return False
    return not ancla or ('id="%s"' % ancla) in open(ruta, encoding='utf-8').read()


def revisar(servicios, base):
    """Detiene la generación si falta una ficha o algo de ella no existe."""
    ids = [s[0] for s in servicios]
    if set(ids) != set(FICHAS):
        raise SystemExit('servicios_fichas.py: cada servicio necesita su ficha, y cada ficha su servicio (faltan: %s; sobran: %s)'
                         % (', '.join(sorted(set(ids) - set(FICHAS))) or '—', ', '.join(sorted(set(FICHAS) - set(ids))) or '—'))
    glos = {g['termino'] for g in base['glosario']}
    refs = {r['id'] for r in base['referencias_legales']}
    for sid, f in FICHAS.items():
        for x in f['hace']:
            if x[4] not in ('Gratis', 'Nuevo'):
                raise SystemExit('servicios_fichas.py: «%s» de %s tiene la etiqueta %s' % (x[1], sid, x[4]))
        for liga in [x[3] for x in f['hace']] + [x[0] for x in f['enciclopedia']]:
            if not _ancla_existe(liga):
                raise SystemExit('servicios_fichas.py: %s enlaza a %s, que no existe' % (sid, liga))
        for t in f['glosario']:
            if t not in glos:
                raise SystemExit('servicios_fichas.py: %s cita «%s», que no está en el Diccionario' % (sid, t))
        for r in f['refs']:
            if r not in refs:
                raise SystemExit('servicios_fichas.py: %s cita %s, que no está en Referencias' % (sid, r))
        for k in ('auditor', 'pal', 'no'):
            if not f.get(k):
                raise SystemExit('servicios_fichas.py: a %s le falta «%s»' % (sid, k))
        re.compile(f['pal'])


def chat_liga(q, modo):
    from urllib.parse import quote
    return '%s?q=%s&amp;modo=%s' % (CHAT, quote(q), modo)


# Todo pasa por el Auditor (decisión del autor, 19-11-2026: «entre pestañas no se
# vinculan: todo es a través del Auditor»). Una liga de Servicios a otra pestaña
# abre el chat con la pregunta y `abre=`: el chat contesta en corto con esa página
# (o abre la aplicación en su marco), ofrece el dictamen, «Saber más» y el servicio
# que toca (`abre()` y `servicioHtml()` de asistente.js). herramientas/vinculos_auditor.py
# revisa que la regla de `pestana_de()` coincida con la pestaña que marca cada página.
# El índice general cuelga del Auditor (decisión del autor, 19-11-2026).
# Con él, las dos páginas que cuelgan del índice: el Registro de pendientes y la base al día.
EXCEPCIONES = {'periodismo-en-riesgo.html': 'Noticiero', 'indice.html': 'Auditor', 'pendientes.html': 'Auditor', 'base-al-dia.html': 'Auditor',
               'mis-respuestas.html': 'Auditor'}
_GENERICO = re.compile(r'^(ábrelo|abrir|abre|ver|ver más|ver la página|ver la ficha|aquí|esta página|la página|➔|saber más)\W*$', re.I)
_A = re.compile(r'<a\b([^>]*?)\bhref="([^"]+)"([^>]*)>(.*?)</a>', re.S)


def pestana_de(archivo):
    """La pestaña de una página por su nombre (la misma regla que comprueba vinculos_auditor.py)."""
    a = archivo.split('#')[0].split('?')[0]
    if a in EXCEPCIONES:
        return EXCEPCIONES[a]
    if a in (CHAT, 'herramienta-inspector-dictamen.html'):
        return 'Auditor'
    if a == 'index.html':
        return None
    if re.match(r'servicios?(-|\.html)', a):
        return 'Servicios'
    if a.startswith('planisferio'):
        return 'Planisferio'
    if a.startswith('noticias'):
        return 'Noticiero'
    return 'Comunidad'


def por_auditor(liga, q, modo=None):
    """La liga que pasa por el chat: la pregunta, el modo y la página que debe abrir."""
    from urllib.parse import quote
    return '%s?q=%s%s&amp;abre=%s' % (CHAT, quote(q), '&amp;modo=%s' % modo if modo else '', quote(html.unescape(liga), safe='/-_.'))


def _titulo(archivo):
    ruta = os.path.join(RAIZ, archivo.split('#')[0].split('?')[0])
    if not os.path.exists(ruta):
        return ''
    m = re.search(r'<title>(.*?)</title>', open(ruta, encoding='utf-8').read(), re.S)
    return html.unescape(re.split(r' [·|—-] ', m.group(1))[0]).strip() if m else ''


def por_auditor_html(texto, origen='Servicios', modo=None, modo_de=None):
    """Cambia, dentro de <main>, cada liga directa a otra pestaña por su liga al chat."""
    i, j = texto.find('<main'), texto.rfind('</main>')
    if i < 0 or j < 0:
        return texto

    def cambia(m):
        antes, liga, despues, dentro = m.groups()
        if re.match(r'[a-z]+:|#|//', liga) or not liga.split('#')[0].split('?')[0].endswith('.html'):
            return m.group(0)
        t = pestana_de(liga)
        if t in (None, origen, 'Auditor'):
            return m.group(0)
        b = re.search(r'<b>(.*?)</b>', dentro, re.S)
        q = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', b.group(1) if b else dentro))).strip(' ➔→›»')
        if len(q) < 4 or _GENERICO.match(q) or len(q) > 140:
            q = _titulo(liga) or q[:140]
        return '<a%shref="%s"%s>%s</a>' % (antes, por_auditor(liga, q, modo or (modo_de(liga.split('#')[0].split('?')[0]) if modo_de else None)), despues, dentro)
    return texto[:i] + _A.sub(cambia, texto[i:j]) + texto[j:]


def mapa_chat(servicios, cobro):
    """{página: [[id, ícono, nombre, cobro, página del servicio]]}: los servicios que
    aprovechan cada página (su `hace`). Lo lee servicioHtml() de asistente.js para
    ofrecer el servicio cuando una respuesta lleva a esa página. Nunca un monto."""
    nom = {x[0]: x for x in servicios}
    out = {}
    for sid, f in FICHAS.items():
        for _i, _t, _tx, liga, _et in f['hace']:
            b = liga.split('#')[0].split('?')[0]
            if pestana_de(b) in ('Servicios', 'Auditor'):
                continue
            l = out.setdefault(b, [])
            if len(l) < 3 and sid not in [x[0] for x in l]:
                l.append([sid, nom[sid][1], nom[sid][2], cobro[sid], PAGINA % sid])
    return dict(sorted(out.items()))


def nuevos(sid=None):
    """Lo nuevo de la plataforma, sin repetir: (ícono, título, texto, liga, servicios)."""
    vistos = {}
    for k, f in FICHAS.items():
        if sid and k != sid:
            continue
        for ico, tit, tx, liga, et in f['hace']:
            if et == 'Nuevo':
                vistos.setdefault(tit, [ico, tit, tx, liga, []])[4].append(k)
    return list(vistos.values())


def temas(servicios, cobro, lineas, perfiles, perfiles_corto, base):
    """Las respuestas del chat (D.san.t): un servicio, una familia, un perfil y
    el catálogo. Las lee mapaResp() de asistente-charla.js."""
    revisar(servicios, base)
    refs = {r['id']: r for r in base['referencias_legales']}
    nom = {s[0]: s for s in servicios}
    esc = html.escape
    out = {}
    for s in servicios:
        sid, ico, n, que, recibe, quien, _l = s
        f = FICHAS[sid]
        gratis = ''.join('<li><b>%s%s:</b> %s <a href="%s">Ábrelo</a>.</li>' % (
            esc(t), ' (nuevo)' if et == 'Nuevo' else '', esc(tx), lg) for _i, t, tx, lg, et in f['hace'])
        out['srv_' + sid] = {
            'tit': '%s: el servicio' % n,
            'h': ('<p><span aria-hidden="true">%s</span> <b>%s.</b> %s</p>'
                  '<p><b>Recibes:</b> %s <b>Para quién:</b> %s <b>Cómo se cobra:</b> %s; el costo y el plazo llegan por escrito antes de empezar.</p>'
                  '<p>Lo básico lo puedes hacer tú, gratis, con la plataforma:</p><ul>%s</ul>'
                  '<p>%s</p><p><a href="%s">Ver el servicio completo</a> · <a href="servicios-cotiza.html?servicio=%s#solicitud">Pide una cotización</a></p>') % (
                ico, esc(n), esc(que), esc(recibe), esc(quien), esc(cobro[sid]), gratis, esc(f['no']), PAGINA % sid, sid),
            'ci': [],
            'fu': [{'que': refs[r]['cita_apa'].split('. ')[0][:140], 'e': 'oficial', 'fu': {'tx': refs[r]['cita_apa'][:160], 'url': refs[r]['url']}}
                   for r in f['refs'][:3] if refs[r].get('url')],
            'sug': [q for q, _m in f['auditor'][:2]] + ['¿Qué servicios ofrece Auditavisión?'],
            'ir': [PAGINA % sid, n], 'pal': f['pal'], 'pri': 3}
    lista = lambda xs: '<ul>%s</ul>' % ''.join(
        '<li><span aria-hidden="true">%s</span> <a href="%s"><b>%s</b></a>: %s <small>(%s)</small></li>' % (
            nom[i][1], PAGINA % i, esc(nom[i][2]), esc(nom[i][3]), esc(cobro[i])) for i in xs)
    for lid, lico, ltit, ltx in lineas:
        ids = [s[0] for s in servicios if s[6] == lid]
        out['srv_fam_' + lid] = {
            'tit': ltit, 'h': '<p><span aria-hidden="true">%s</span> <b>%s.</b> %s</p>%s<p>Toca uno para ver qué hace ya la plataforma, gratis, y qué recibes por encargo.</p>' % (
                lico, esc(ltit), esc(ltx), lista(ids)),
            'ci': [], 'fu': [], 'sug': ['¿Qué servicios ofrece Auditavisión?'], 'ir': ['servicios-catalogo.html#fam-' + lid, ltit],
            'pal': PAL_LINEA[lid], 'pri': 1, 'req': r'servicios?|ofrecen|tienen|dan'}
    if len(PAL_PERFIL) != len(perfiles):
        raise SystemExit('servicios_fichas.py: PAL_PERFIL necesita una expresión por perfil de PERFILES')
    for n, (p, corto) in enumerate(zip(perfiles, perfiles_corto)):
        ico, sec, quien, reto, ids, libres = p
        out['srv_perfil_%d' % n] = {
            'tit': 'Servicios para %s' % sec.lower(),
            'h': ('<p><span aria-hidden="true">%s</span> <b>%s.</b> %s</p><p><b>Tu reto:</b> %s</p>%s'
                  '<p><b>Empieza gratis:</b> %s</p>') % (ico, esc(sec), esc(quien), reto, lista(ids),
                                                         ' · '.join('<a href="%s">%s</a>' % l for l in libres)),
            'ci': [], 'fu': [], 'sug': [q for q, _m in FICHAS[ids[0]]['auditor'][:2]], 'ir': ['servicios-tu-perfil.html', 'Tu perfil: ' + corto],
            'pal': PAL_PERFIL[n], 'pri': 2, 'req': r'servicios?|ofrecen|tienen|dan|me sirve|me conviene|que hay para'}
    out['srv_catalogo'] = {
        'tit': 'Los servicios de Auditavisión',
        'h': ('<p>La consulta es gratis y lo seguirá siendo. Cuando quieras ir más a fondo, lo hacemos por encargo, con la misma regla: '
              'cada cifra con su documento, y nunca a cambio de lo que publicamos.</p>%s'
              '<p>Cada servicio dice cómo se cobra; todavía no hay tarifas publicadas y no las vamos a inventar.</p>') % ''.join(
            '<p><b><span aria-hidden="true">%s</span> %s</b></p>%s' % (lico, esc(ltit), lista([s[0] for s in servicios if s[6] == lid]))
            for lid, lico, ltit, _x in lineas),
        'ci': [], 'fu': [], 'sug': ['¿Qué servicios ofrecen para despachos contables?', '¿Cómo reviso a un proveedor antes de contratarlo?', '¿Cómo se sostiene Auditavisión?'],
        'ir': ['servicios.html', 'Servicios'],
        'pal': r'que servicios|servicios (ofrece|ofrecen|tiene|tienen|hay|dan|venden)|catalogo de servicios|sus servicios', 'pri': 0}
    return out


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import apartados
    import auditorias
    t = temas(apartados.SERVICIOS, apartados.COBRO, apartados.LINEAS, apartados.PERFILES, apartados.PERFILES_CORTO, auditorias.db())
    print('servicios_fichas: %d servicios, %d respuestas del chat, %d novedades' % (len(FICHAS), len(t), len(nuevos())))
