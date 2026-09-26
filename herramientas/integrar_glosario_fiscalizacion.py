#!/usr/bin/env python3
"""Pone al día el glosario y la bibliografía con el vocabulario que trajeron
las secciones nuevas: Informes de la Cuenta Pública (ASF), Portal Digital
(canales oficiales) y Catálogo de Fuentes.

Uso:
    python3 herramientas/integrar_glosario_fiscalizacion.py

Cada definición sale del texto de su fuente, que se cita en «ley»:
- Ley de Fiscalización y Rendición de Cuentas de la Federación, última
  reforma DOF 14-05-2026 (arts. 4, 33 a 36 y 39 a 42).
- Glosario de la Matriz de Datos Básicos de la ASF, Cuenta Pública 2024,
  corte febrero de 2026, pp. 518 y 519.
- Ley General de Transparencia y Acceso a la Información Pública, nueva ley
  DOF 20-03-2025 (arts. 3, 65 y 144).
- Constitución, art. 102, apartado A.

Además corrige citas que habían quedado viejas (la LGTAIP de 2015, que fue
abrogada, y los artículos de la LFRCF que no correspondían).

Es idempotente: no duplica términos ni fichas y las correcciones sólo se
aplican si el texto viejo sigue ahí.
"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BASE = RAIZ / 'assets' / 'js' / 'audit-database.js'

FIS = '\U0001f50d Fiscalización Superior'
MDB = 'Glosario de la Matriz de Datos Básicos de la ASF (CP 2024, p. 518)'
MDB2 = 'Glosario de la Matriz de Datos Básicos de la ASF (CP 2024, p. 519)'

TERMINOS = [
    {'termino': 'Informe Individual de Auditoría',
     'definicion': 'El informe de cada auditoría que practica la Auditoría Superior de la Federación. Dice por qué se eligió ese ente, qué se revisó y cómo, el dictamen, los resultados, las observaciones y las acciones que se promovieron, e incluye un resumen de lo que la entidad respondió durante la revisión. Es público: la ley obliga a mantenerlo en la página de la ASF en formatos abiertos. Es el documento que hay que citar cuando se habla de lo que encontró una auditoría.',
     'ley': 'Arts. 4 fr. XXII, 35 y 36 Ley de Fiscalización y Rendición de Cuentas de la Federación'},
    {'termino': 'Entregas del Informe del Resultado',
     'definicion': 'Las tres fechas en que la ASF entrega a la Cámara de Diputados, por conducto de la Comisión de Vigilancia, los informes individuales que va concluyendo: el último día hábil de junio, el último día hábil de octubre y el 20 de febrero del año siguiente al de la presentación de la Cuenta Pública. Por eso la revisión de un año se conoce por partes: un informe de junio no es el cuadro completo, y cualquier suma hecha antes de la tercera entrega es parcial.',
     'ley': 'Art. 35 Ley de Fiscalización y Rendición de Cuentas de la Federación · ' + MDB},
    {'termino': 'Informe General Ejecutivo',
     'definicion': 'El documento de conjunto que la ASF rinde a la Cámara de Diputados a más tardar el 20 de febrero del año siguiente al de la presentación de la Cuenta Pública. Resume las auditorías y sus observaciones, señala las áreas clave con riesgo, da los resultados del gasto federalizado, las participaciones y la deuda, describe qué parte del gasto se auditó y puede proponer a la Cámara cambios a las leyes. Es público, y la Cámara lo envía al Comité Coordinador del Sistema Nacional Anticorrupción y al Comité de Participación Ciudadana.',
     'ley': 'Arts. 4 fr. XX, 33 y 34 Ley de Fiscalización y Rendición de Cuentas de la Federación'},
    {'termino': 'Matriz de Datos Básicos (MDB)',
     'definicion': 'El resumen numérico que la ASF publica con cada entrega del Informe del Resultado. Cuenta, por grupo funcional, sector y entidad federativa, cuántas auditorías se hicieron, el universo seleccionado, la muestra auditada, las acciones de cada tipo, lo recuperado y lo que queda por aclarar. Dos advertencias de la propia ASF: sus montos vienen en miles de pesos, y no todas las auditorías tienen monto, porque las de desempeño o las que sólo revisan que el dinero se haya transferido no se miden en pesos.',
     'ley': 'ASF, Matriz de Datos Básicos de la Cuenta Pública 2024, introducción, notas y glosario (corte febrero de 2026)'},
    {'termino': 'Universo Seleccionado',
     'definicion': 'El monto total de lo que la ASF eligió revisar en una auditoría: el presupuesto asignado o ejercido en los capítulos, partidas, programas, fondos u obras de que se trate, los conceptos de ingreso o los rubros de balance. De ese universo se toma la muestra auditada, que es lo que de verdad se revisa documento por documento.',
     'ley': MDB + ', num. 2.1'},
    {'termino': 'Representatividad de la Muestra',
     'definicion': 'El porcentaje que la muestra auditada representa del universo seleccionado. Un porcentaje alto dice que se revisó casi todo lo elegido; uno bajo pide leer los hallazgos con cuidado, porque describen sólo esa parte. En la Cuenta Pública 2024, sumando todas las auditorías con monto, la muestra fue el 53.03 % del universo.',
     'ley': MDB + ', num. 2.3 · ASF, Matriz de Datos Básicos CP 2024, cuadro general'},
    {'termino': 'Observación Solventada',
     'definicion': 'Irregularidad o deficiencia que la entidad fiscalizada corrigió o aclaró con documentos, ya sea durante la auditoría o después, en el seguimiento. Solventar no equivale a devolver dinero: puede bastar con demostrar que el gasto estaba justificado. Tras recibir la respuesta de la entidad, la ASF tiene 120 días hábiles para decidir si la observación queda solventada, no solventada, archivada o concluida.',
     'ley': MDB + ', num. 3.1 · Art. 41 Ley de Fiscalización y Rendición de Cuentas de la Federación'},
    {'termino': 'Recomendación (R) y Recomendación al Desempeño (RD)',
     'definicion': 'Las dos acciones preventivas de la ASF: no imputan falta a nadie. La recomendación (R) pide fortalecer el control interno, los procesos administrativos y el cumplimiento de metas. La recomendación al desempeño (RD) pide que la entidad cumpla sus objetivos, ejerza el dinero para el propósito que se le asignó y mejore sus indicadores. Antes de emitirlas, la ASF las analiza con la entidad y lo acordado queda en actas que firman ambas; si no hay acuerdo, la ASF puede emitirlas de todos modos.',
     'ley': MDB + ', nums. 4.1 y 4.2 · Art. 42 Ley de Fiscalización y Rendición de Cuentas de la Federación'},
    {'termino': 'Solicitud de Aclaración (SA)',
     'definicion': 'Acción con la que la ASF pide a la entidad fiscalizada documentos adicionales que aclaren y respalden operaciones o montos que durante la revisión quedaron sin justificar o sin comprobar. Es el paso previo a un pliego de observaciones: si la entidad aclara, el asunto se cierra; si no, puede escalar.',
     'ley': 'Art. 40 fr. I Ley de Fiscalización y Rendición de Cuentas de la Federación · ' + MDB2 + ', num. 4.4'},
    {'termino': 'Promoción del Ejercicio de la Facultad de Comprobación Fiscal (PEFCF)',
     'definicion': 'Aviso que la ASF envía a la autoridad tributaria, el SAT, cuando en una auditoría detecta un posible incumplimiento fiscal o errores y omisiones en declaraciones o avisos fiscales. La ASF no cobra impuestos: le pasa el dato a quien sí puede revisarlos.',
     'ley': 'Art. 40 fr. III Ley de Fiscalización y Rendición de Cuentas de la Federación · ' + MDB2 + ', num. 4.3'},
    {'termino': 'Promoción de Responsabilidad Administrativa Sancionatoria (PRAS)',
     'definicion': 'Acción con la que la ASF da vista al órgano interno de control de la entidad cuando detecta posibles faltas administrativas no graves, para que ese órgano investigue y, en su caso, sancione. En la Cuenta Pública 2024 fue la segunda acción más frecuente: 2,203 de 6,274, sólo detrás de los pliegos de observaciones. Las faltas graves siguen otro camino: el informe de presunta responsabilidad administrativa.',
     'ley': 'Art. 40 fr. V Ley de Fiscalización y Rendición de Cuentas de la Federación · ' + MDB2 + ', num. 4.5 · ASF, Matriz de Datos Básicos CP 2024, cuadro general'},
    {'termino': 'Informe de Presunta Responsabilidad Administrativa',
     'definicion': 'El documento con el que la ASF lleva ante el Tribunal Federal de Justicia Administrativa las faltas administrativas graves que descubre en sus auditorías o investigaciones, para que se sancione a las personas servidoras públicas y a los particulares vinculados. A diferencia de las demás acciones, no se notifica con el informe individual, sino conforme a la Ley General de Responsabilidades Administrativas.',
     'ley': 'Arts. 4 fr. XXXI, 39 y 40 fr. IV Ley de Fiscalización y Rendición de Cuentas de la Federación'},
    {'termino': 'Denuncia de Hechos (ASF)',
     'definicion': 'La vía con la que la ASF hace del conocimiento de la Fiscalía Especializada en Materia de Combate a la Corrupción hechos que pueden ser delito. Puede presentarse en cualquier momento, sin esperar a que termine la auditoría. Es el único camino que lleva un hallazgo de fiscalización al terreno penal.',
     'ley': 'Arts. 4 fr. XV y 40 fr. VI Ley de Fiscalización y Rendición de Cuentas de la Federación'},
    {'termino': 'Denuncia de Juicio Político',
     'definicion': 'Acción con la que la ASF informa a la Cámara de Diputados de actos u omisiones de los altos cargos del artículo 110 constitucional que perjudican los intereses públicos fundamentales, para que se tramite el procedimiento y se resuelva sobre su responsabilidad política. No es penal ni administrativa: su sanción es la destitución y la inhabilitación.',
     'ley': 'Art. 40 fr. VII Ley de Fiscalización y Rendición de Cuentas de la Federación · Art. 110 CPEUM'},
    {'termino': 'Sugerencias a la Cámara de Diputados',
     'definicion': 'Propuestas de la ASF para que la Cámara cambie disposiciones legales y así mejore la gestión financiera y el desempeño de las entidades fiscalizadas. No obligan: la Cámara decide si las acepta. Se cuentan aparte de las acciones en la Matriz de Datos Básicos y se recogen en el Informe General Ejecutivo.',
     'ley': MDB2 + ', num. 5 · Art. 34 fr. V Ley de Fiscalización y Rendición de Cuentas de la Federación'},
    {'termino': 'Cuantificación Monetaria de las Observaciones',
     'definicion': 'El monto de las operaciones que la ASF observó porque no cumplían la ley o la norma. Se divide en lo que ya se recuperó y lo que queda por aclarar. La propia ASF advierte que no equivale a dinero perdido ni a dinero que vaya a regresar: es lo que quedó en duda.',
     'ley': MDB2 + ', num. 6'},
    {'termino': 'Recuperaciones Operadas',
     'definicion': 'Dinero que efectivamente se reintegró o resarció a la Hacienda Pública o al patrimonio de un ente público gracias a la intervención de la ASF, durante la auditoría. Es la única parte de la cuantificación monetaria que ya es dinero de vuelta; el resto sigue siendo monto por aclarar.',
     'ley': MDB2 + ', num. 6.1'},
    {'termino': 'Entidad Fiscalizada',
     'definicion': 'Todo aquel que la ASF puede auditar. No sólo los entes públicos: también fideicomisos, fondos y mandatos, públicos o privados, y en general cualquier persona física o moral, del sector privado o social, que haya recibido, manejado o ejercido recursos públicos federales o participaciones federales, incluidas las donatarias autorizadas. La regla es sencilla: quien toca dinero federal puede ser auditado.',
     'ley': 'Art. 4 fr. XI Ley de Fiscalización y Rendición de Cuentas de la Federación'},
    {'termino': 'Comisión de Vigilancia de la Auditoría Superior de la Federación',
     'definicion': 'La comisión de la Cámara de Diputados por cuyo conducto la ASF entrega los informes individuales y el Informe General. Puede pedir al Auditor Superior que presente, amplíe o aclare esos informes en sesiones, tantas veces como haga falta, siempre que no se revele información reservada.',
     'ley': 'Arts. 4 fr. VI, 33 y 35 Ley de Fiscalización y Rendición de Cuentas de la Federación'},
    {'termino': 'Autonomía Técnica y de Gestión de la ASF',
     'definicion': 'Las dos garantías que protegen a la ASF de presiones. La técnica le permite decidir por sí misma qué audita, cómo, cuándo lo informa y cómo le da seguimiento. La de gestión le permite decidir su organización, sus resoluciones y la administración de su personal y sus recursos. Depende de la Cámara de Diputados, pero la Cámara no le dicta a quién auditar.',
     'ley': 'Art. 79 CPEUM · Art. 4 frs. III y IV Ley de Fiscalización y Rendición de Cuentas de la Federación'},
    {'termino': 'Plazos del Seguimiento de las Acciones',
     'definicion': 'El reloj que corre después de cada entrega de la ASF, contado en días hábiles. La ASF tiene 10 para enviar el informe individual a la entidad; la entidad, 30 para responder y aportar pruebas; la ASF, 120 para pronunciarse sobre esas respuestas, y 90 más para mandar a investigación los pliegos de observaciones no solventados. Por eso un monto por aclarar de hoy puede tardar más de un año en resolverse.',
     'ley': 'Arts. 39 y 41 Ley de Fiscalización y Rendición de Cuentas de la Federación (reforma DOF 14-05-2026)'},
    {'termino': 'Informe de Avance de Gestión Financiera',
     'definicion': 'El informe de medio año sobre el avance físico y financiero de los programas federales, que los Poderes y los entes públicos federales rinden de forma consolidada, por medio del Ejecutivo, a la Cámara de Diputados. Viene como un apartado del segundo informe trimestral. Permite ver cómo va el gasto antes de que llegue la Cuenta Pública.',
     'ley': 'Art. 4 fr. XIX Ley de Fiscalización y Rendición de Cuentas de la Federación · Art. 107 Ley Federal de Presupuesto y Responsabilidad Hacendaria'},
    {'termino': 'Fiscalía Especializada en Materia de Combate a la Corrupción (FEMCC)',
     'definicion': 'La fiscalía de la Fiscalía General de la República que investiga los delitos de corrupción: peculado, cohecho, uso ilícito de atribuciones, enriquecimiento ilícito. La Constitución obliga a que exista. Recibe las denuncias de hechos de la ASF y también las de cualquier persona; a diferencia de otras vías, la denuncia penal pide identificarse.',
     'ley': 'Art. 102 apartado A CPEUM · Arts. 4 fr. XV y 40 fr. VI Ley de Fiscalización y Rendición de Cuentas de la Federación'},
    {'termino': 'Transparencia para el Pueblo (Autoridad Garante)',
     'definicion': 'El órgano desconcentrado de la Secretaría Anticorrupción y Buen Gobierno que, desde la nueva ley de 2025, es la autoridad garante federal del acceso a la información: la que resuelve los recursos de revisión cuando una dependencia niega o no entrega lo que se le pidió. Ocupó el lugar del extinto INAI. No es la única: el Poder Judicial, el Congreso y los órganos autónomos tienen su propia autoridad garante, y en los estados la función la tienen las contralorías u órganos equivalentes del Ejecutivo local.',
     'ley': 'Art. 3 frs. III, IV y V Ley General de Transparencia y Acceso a la Información Pública (DOF 20-03-2025)'},
]

REF_NUEVAS = [
    {'num': 82, 'id': 'ref-asf-mdb2025a', 'categoria': 'fiscalizacion_auditoria', 'categoria_nombre': 'Fiscalización Superior y Auditoría',
     'cita_apa': 'Auditoría Superior de la Federación. (2026). Matriz de Datos Básicos, Fiscalización Superior de la Cuenta Pública 2025: primera entrega. ASF.',
     'url': 'https://www.asf.gob.mx/Trans/Informes/IR2025a/Documentos/Matriz/IR2025_Entrega_a.pdf',
     'descripcion': 'Resumen numérico de la primera entrega de la revisión de la Cuenta Pública 2025, corte junio de 2026: las 33 auditorías a la distribución de las participaciones federales. Es la fuente de las cifras 2025 de la sección Informes de la Cuenta Pública.'},
    {'num': 83, 'id': 'ref-asfdatos', 'categoria': 'fuentes_oficiales', 'categoria_nombre': 'Fuentes Oficiales & Datos Abiertos',
     'cita_apa': 'Auditoría Superior de la Federación. (s. f.). Sistema Público de Consulta de Auditorías [ASF Datos]. ASF.',
     'url': 'https://www.asfdatos.gob.mx/',
     'descripcion': 'Buscador oficial de las auditorías de la ASF por año de Cuenta Pública, entidad fiscalizada y tipo de acción. Sirve para llegar del dato agregado de la matriz al informe individual de una auditoría concreta.'},
    {'num': 84, 'id': 'ref-shcp-cuentapublica', 'categoria': 'fuentes_oficiales', 'categoria_nombre': 'Fuentes Oficiales & Datos Abiertos',
     'cita_apa': 'Secretaría de Hacienda y Crédito Público. (s. f.). Cuenta Pública [portal oficial, ejercicios 1996 a 2025]. SHCP.',
     'url': 'https://www.cuentapublica.hacienda.gob.mx',
     'descripcion': 'La Cuenta Pública misma: el informe anual del gasto que Hacienda entrega a la Cámara de Diputados a más tardar el 30 de abril del año siguiente (art. 74 fr. VI constitucional). Es el documento que después revisa la ASF.'},
    {'num': 85, 'id': 'ref-asf-denuncias', 'categoria': 'investigacion_civica', 'categoria_nombre': 'Investigación & Contraloría Cívica',
     'cita_apa': 'Auditoría Superior de la Federación. (s. f.). Denuncias ciudadanas [Sistema de Denuncias Ciudadanas]. ASF.',
     'url': 'https://www.asf.gob.mx/Section/262_Denuncias_Ciudadanas',
     'descripcion': 'Canal oficial para denunciar ante la ASF el desvío o uso irregular de recursos federales, incluidos los que la Federación transfiere a estados y municipios. Admite denuncia anónima. Es el canal 1 del Portal Digital.'},
    {'num': 86, 'id': 'ref-sabg-alertadores', 'categoria': 'investigacion_civica', 'categoria_nombre': 'Investigación & Contraloría Cívica',
     'cita_apa': 'Secretaría Anticorrupción y Buen Gobierno. (s. f.). Plataforma Ciudadanos Alertadores Internos y Externos de la Corrupción. Gobierno de México.',
     'url': 'https://alertadores.buengobierno.gob.mx/',
     'descripcion': 'Plataforma para alertar actos graves de corrupción de personas servidoras públicas federales, con medidas de protección para quien alerta y una clave de seguimiento que no revela su identidad. Es el canal 2 del Portal Digital.'},
    {'num': 87, 'id': 'ref-fgr-femcc', 'categoria': 'investigacion_civica', 'categoria_nombre': 'Investigación & Contraloría Cívica',
     'cita_apa': 'Fiscalía General de la República. (s. f.). Fiscalía Especializada en Materia de Combate a la Corrupción. FGR.',
     'url': 'https://fgr.org.mx/es/FGR/FEMCC',
     'descripcion': 'Fiscalía que investiga los delitos de corrupción, prevista en el artículo 102 apartado A de la Constitución. Recibe las denuncias de hechos de la ASF y las de cualquier persona. Es el canal 3 del Portal Digital.'},
    {'num': 88, 'id': 'ref-sat-denuncias', 'categoria': 'tributario', 'categoria_nombre': 'Marco Tributario y Fiscal',
     'cita_apa': 'Servicio de Administración Tributaria. (s. f.). Denuncias [trámite en línea]. SAT.',
     'url': 'https://www.sat.gob.mx/aplicacion/operacion/50409/denuncias-sat',
     'descripcion': 'Buzón del SAT para denunciar, entre otras conductas, a las empresas que facturan operaciones simuladas. Admite denuncia anónima. Es el canal 4 del Portal Digital.'},
    {'num': 89, 'id': 'ref-transparencia-presupuestaria', 'categoria': 'fuentes_oficiales', 'categoria_nombre': 'Fuentes Oficiales & Datos Abiertos',
     'cita_apa': 'Secretaría de Hacienda y Crédito Público. (s. f.). Transparencia Presupuestaria: Observatorio del Gasto [portal de datos abiertos]. SHCP.',
     'url': 'https://www.transparenciapresupuestaria.gob.mx/',
     'descripcion': 'Portal de Hacienda con las bases de datos abiertas del presupuesto: el aprobado, su avance trimestral, los proyectos de presupuesto y los programas. De aquí salen varias de las descargas de la plataforma.'},
]

# (termino, clave, texto viejo, texto nuevo). Solo se cambia si el viejo sigue.
CORRECCIONES_GLOSARIO = [
    ('Observación, Recomendación y Promoción de Responsabilidad', 'ley',
     'Arts. 49 a 52 Ley de Fiscalización y Rendición de Cuentas de la Federación',
     'Arts. 40 y 42 Ley de Fiscalización y Rendición de Cuentas de la Federación'),
    ('Pliego de Observaciones', 'ley',
     'Ley de Fiscalización y Rendición de Cuentas de la Federación',
     'Arts. 40 fr. II y 41 Ley de Fiscalización y Rendición de Cuentas de la Federación · ' + MDB2 + ', num. 4.6'),
    ('Muestra Auditada', 'ley',
     'Ley de Fiscalización y Rendición de Cuentas de la Federación',
     MDB + ', num. 2.2 · Art. 34 fr. IV Ley de Fiscalización y Rendición de Cuentas de la Federación'),
    ('Monto por Aclarar', 'ley',
     'Ley de Fiscalización y Rendición de Cuentas de la Federación',
     MDB2 + ', num. 6.2 · Arts. 39 y 41 Ley de Fiscalización y Rendición de Cuentas de la Federación'),
    ('Transparencia Proactiva y Datos Abiertos', 'ley',
     'Arts. 70 y 71 Ley General de Transparencia y Acceso a la Información Pública',
     'Arts. 3 fr. VIII y 65 Ley General de Transparencia y Acceso a la Información Pública (DOF 20-03-2025)'),
    ('Recurso de Revisión en Transparencia', 'ley',
     'Ley General de Transparencia y Acceso a la Información Pública',
     'Arts. 144 a 148 Ley General de Transparencia y Acceso a la Información Pública (DOF 20-03-2025)'),
]

CORRECCIONES_REF = [
    ('ref-lgtaip', 'cita_apa',
     'Ley General de Transparencia y Acceso a la Información Pública [LGTAIP]. Diario Oficial de la Federación, 4 de mayo de 2015 (México). Artículos 70 a 83.',
     'Ley General de Transparencia y Acceso a la Información Pública [LGTAIP]. Diario Oficial de la Federación, 20 de marzo de 2025 (México). Nueva ley que abrogó la de 2015. Artículos 65 a 82 y 144 a 148. Cámara de Diputados.'),
]


def _valor(v):
    return json.dumps(v, ensure_ascii=False)


def _variantes(texto):
    """El archivo mezcla acentos reales y secuencias \\uXXXX."""
    crudo = json.dumps(texto, ensure_ascii=False)
    escapado = json.dumps(texto, ensure_ascii=True)
    return [crudo] if crudo == escapado else [crudo, escapado]


def _objeto(b, desde, clave, valor):
    """Devuelve (inicio, fin) del objeto que contiene "clave": valor."""
    for v in _variantes(valor):
        i = b.find('"%s": %s' % (clave, v), desde)
        if i >= 0:
            ini = b.rfind('\r\n    {', 0, i)
            fin = b.index('\r\n    }', i) + len('\r\n    }')
            return ini, fin
    return None


def corregir(b, desde, buscar_clave, buscar_valor, campo, viejo, nuevo):
    pos = _objeto(b, desde, buscar_clave, buscar_valor)
    if not pos:
        sys.exit('No encuentro %s = %s; no toco nada.' % (buscar_clave, buscar_valor))
    ini, fin = pos
    trozo = b[ini:fin]
    for v in _variantes(viejo):
        linea = '"%s": %s' % (campo, v)
        if linea in trozo:
            trozo = trozo.replace(linea, '"%s": %s' % (campo, _valor(nuevo)), 1)
            return b[:ini] + trozo + b[fin:], 1
    return b, 0


def glosario(b):
    ini = b.index('"glosario": [')
    cierre = b.index('\r\n  ]', ini)
    existentes = b[ini:cierre]
    nuevos = ''
    agregados = 0
    for t in TERMINOS:
        if any('"termino": %s' % v in existentes for v in _variantes(t['termino'])):
            continue
        entrada = dict(termino=t['termino'], definicion=t['definicion'], ley=t['ley'], categoria=FIS)
        nuevos += ',\r\n    {\r\n' + ',\r\n'.join('      "%s": %s' % (k, _valor(v)) for k, v in entrada.items()) + '\r\n    }'
        agregados += 1
    b = b[:cierre] + nuevos + b[cierre:]
    cambios = 0
    for termino, campo, viejo, nuevo in CORRECCIONES_GLOSARIO:
        b, n = corregir(b, ini, 'termino', termino, campo, viejo, nuevo)
        cambios += n
    return b, agregados, cambios


def referencias(b):
    ini = b.index('"referencias_legales": [')
    ancla = b.index('"id": "ref-asf-ir2025a"', ini)
    fin = b.index('\r\n    }', ancla) + len('\r\n    }')
    agregadas = 0
    for ref in reversed(REF_NUEVAS):
        if '"id": "%s"' % ref['id'] in b:
            continue
        cuerpo = ',\r\n    {\r\n' + ',\r\n'.join('      "%s": %s' % (k, _valor(v)) for k, v in ref.items()) + '\r\n    }'
        b = b[:fin] + cuerpo + b[fin:]
        agregadas += 1
    cambios = 0
    for rid, campo, viejo, nuevo in CORRECCIONES_REF:
        b, n = corregir(b, ini, 'id', rid, campo, viejo, nuevo)
        cambios += n
    return b, agregadas, cambios


def main():
    b = BASE.read_bytes().decode('utf-8')
    b, tg, cg = glosario(b)
    b, tr, cr = referencias(b)
    BASE.write_bytes(b.encode('utf-8'))
    print('glosario: %d terminos nuevos, %d correcciones' % (tg, cg))
    print('referencias: %d fichas nuevas, %d correcciones' % (tr, cr))


if __name__ == '__main__':
    main()
