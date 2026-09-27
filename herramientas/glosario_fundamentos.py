"""Da a 26 definiciones antiguas del glosario su artículo exacto.

Cada término citaba una ley entera, sin artículo. Aquí se reescriben contra el
texto vigente de la Cámara de Diputados (LeyesBiblio, consultado el
26-09-2026) y, de paso, se corrige lo que la ley ya no dice:

- la medición de la pobreza pasó del CONEVAL al INEGI (LGDS, DOF 16-07-2025);
- la LAASSP y la LGTAIP son leyes nuevas de 2025, con otro articulado;
- la denuncia ante la ASF no se prevé anónima (LFRCF 60): lo es ante los
  órganos internos de control (LGRA 91);
- el IEPS grava desde 2026 también videojuegos con violencia (LIF 2026, art. 1o.).

Idempotente: si el término ya tiene el texto nuevo, no lo toca.
    python3 herramientas/glosario_fundamentos.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from integrar_glosario_modulos import _objeto, _cuerpo, _limites  # noqa: E402

BASE = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'auditor' / 'js' / 'audit-database.js'

REESCRITURAS = {
    'Denuncia Ciudadana': {
        'definicion': 'Acto por el que una persona pone en conocimiento de una autoridad hechos que pueden constituir un uso irregular de recursos públicos. Hay dos puertas y no piden lo mismo. Ante el órgano interno de control de la institución, por una falta administrativa, la denuncia puede ser anónima y la autoridad guarda la identidad de quien la presenta. Ante la Auditoría Superior de la Federación —o ante la Cámara de Diputados o su Comisión de Vigilancia—, cualquier persona puede denunciar el manejo irregular de recursos federales, aun del año en curso; el escrito debe decir en qué ejercicio ocurrieron los hechos y describirlos, acompañarse de las pruebas que se tengan, y la ASF debe proteger la identidad del denunciante. En ambos casos no hace falta abogado, pero la denuncia vale lo que valen sus datos: fecha, lugar, monto, dependencia y documento.',
        'ley': 'Ley General de Responsabilidades Administrativas, arts. 91 a 93 · Ley de Fiscalización y Rendición de Cuentas de la Federación, arts. 59 a 61 (reforma DOF 14-05-2026)',
    },
    'Alertador': {
        'definicion': 'Persona que informa sobre un acto grave de corrupción. La ley protege sobre todo a quien denuncia desde dentro: el servidor público que denuncia una falta grave, o que es testigo en el procedimiento, puede pedir medidas de protección razonables al ente donde trabaja, y revelar la identidad de un denunciante anónimo protegido es obstrucción de la justicia. El mecanismo federal de alertadores opera con una plataforma que asigna una clave de seguimiento, para que quien alerta conozca el avance de su caso sin dar su nombre.',
        'ley': 'Ley General de Responsabilidades Administrativas, art. 64, fr. III y párrafos siguientes · Plataforma de Ciudadanos Alertadores Internos y Externos de la Corrupción (Secretaría Anticorrupción y Buen Gobierno)',
    },
    'Órgano Interno de Control': {
        'definicion': 'Unidad que vive dentro de cada ente público y cuida su control interno: recibe denuncias, investiga faltas administrativas de su propio personal y sustancia los procedimientos de responsabilidad. En la Administración Pública Federal sus titulares los designa la Secretaría Anticorrupción y Buen Gobierno, no la institución vigilada. Es la instancia más cercana para un hecho local, aunque su independencia frente al ente que revisa es una de las críticas recurrentes del sistema anticorrupción.',
        'ley': 'Ley General de Responsabilidades Administrativas, art. 3, fr. XXI, y art. 10 · Ley Orgánica de la Administración Pública Federal, art. 37, fr. XL, y art. 44',
    },
    'Ramo 28 (Participaciones Federales)': {
        'definicion': 'Dinero federal que se entrega a estados y municipios sin etiqueta, a cambio de que se adhieran al Sistema Nacional de Coordinación Fiscal y dejen a la Federación el cobro de los grandes impuestos. El corazón es el Fondo General de Participaciones, formado con el 20 % de la recaudación federal participable. Al ser «de libre disposición», el gobierno local decide en qué gastarlo; por lo mismo, sólo su propio congreso y su auditoría local lo fiscalizan de lleno.',
        'ley': 'Ley de Coordinación Fiscal, arts. 2o. y 10 · Ley de Disciplina Financiera, art. 2, fr. XIX (ingresos de libre disposición)',
    },
    'Ley de Disciplina Financiera (LDF)': {
        'definicion': 'Ley de 2016 que pone reglas al dinero de estados y municipios. Topa el crecimiento anual de la nómina de los estados (el menor entre 3 % real y el crecimiento del PIB previsto), exige inscribir toda deuda en un Registro Público Único y crea el Sistema de Alertas, que según el nivel de endeudamiento de cada gobierno le fija cuánto más puede pedir prestado.',
        'ley': 'Ley de Disciplina Financiera de las Entidades Federativas y los Municipios (DOF 27-04-2016), arts. 10, 43 a 46',
    },
    'ADEFAS (Adeudos de Ejercicios Fiscales Anteriores)': {
        'definicion': 'Compromisos que quedaron devengados —el bien se recibió o el servicio se prestó— pero sin pagar al cierre del año, y que se liquidan con cargo al presupuesto siguiente. La regla es estricta: lo aprobado y no devengado al 31 de diciembre ya no puede ejercerse. Desde abril de 2026 la ley añade un tope: las ADEFAS del proyecto de presupuesto no pueden pasar del monto de pagos diferidos que previó la Ley de Ingresos del año anterior.',
        'ley': 'Ley Federal de Presupuesto y Responsabilidad Hacendaria, art. 54 (párrafo adicionado DOF 09-04-2026)',
    },
    'Techo de Endeudamiento Neto (LIF)': {
        'definicion': 'Límite de deuda nueva, descontadas las amortizaciones, que el Congreso autoriza cada año al Ejecutivo en la Ley de Ingresos. Para 2026 es de hasta $1 billón 780 mil millones de pesos de endeudamiento neto interno y hasta 15 mil 500 millones de dólares de endeudamiento neto externo. La deuda interna se coloca sobre todo con CETES y Bonos que subasta el Banco de México como agente financiero del gobierno.',
        'ley': 'Ley de Ingresos de la Federación 2026 (DOF 07-11-2025), art. 2o. · Ley Federal de Deuda Pública, arts. 9 y 10',
    },
    'Subastas Primarias Banxico (CETES y Bonos M)': {
        'definicion': 'Mecanismo con el que el Gobierno Federal vende su deuda interna. El Banco de México actúa como su agente financiero y, cada semana, recibe las posturas de los intermediarios autorizados: los CETES se venden a descuento y los Bonos M pagan una tasa fija. Lo que resulte de esas subastas es, en buena parte, el costo financiero que el presupuesto pagará después.',
        'ley': 'Ley del Banco de México, art. 3o., fr. III · Ley Federal de Deuda Pública, art. 4o., fr. I',
    },
    'Tasa de Referencia de Deuda (Banxico)': {
        'definicion': 'Nombre común de la tasa objetivo para la tasa de interés interbancaria a un día, que fija la Junta de Gobierno del Banco de México para cumplir su mandato: procurar la estabilidad del poder adquisitivo de la moneda. No es una tasa «de la deuda», pero la mueve: cuando sube, el gobierno paga más por los CETES y bonos que emite, y crece el costo financiero del presupuesto.',
        'ley': 'Constitución, art. 28, párrafos sexto y séptimo · Ley del Banco de México, arts. 2o. y 3o.',
    },
    'Ingresos Presupuestarios': {
        'definicion': 'Recursos que la Federación estima captar en el año y que la Ley de Ingresos enumera concepto por concepto: impuestos (ISR, IVA, IEPS), cuotas de seguridad social, derechos, productos y aprovechamientos, los ingresos propios de organismos y empresas del Estado y, aparte, el financiamiento, es decir, la deuda. La distinción importa: un ingreso por deuda hoy es un gasto por intereses mañana.',
        'ley': 'Ley de Ingresos de la Federación 2026 (DOF 07-11-2025), art. 1o.',
    },
    'Sistema de Alertas (SHCP)': {
        'definicion': 'Evaluación con la que la Secretaría de Hacienda clasifica a cada estado y municipio con deuda inscrita según su nivel de endeudamiento: sostenible, en observación o elevado (verde, amarillo o rojo en su publicación). No es una opinión: fija el techo de financiamiento neto del año siguiente, de hasta el 15 % de sus ingresos de libre disposición si es sostenible, del 5 % si está en observación y de cero si es elevado.',
        'ley': 'Ley de Disciplina Financiera de las Entidades Federativas y los Municipios, arts. 43, 44 y 46',
    },
    'Adecuación Presupuestaria': {
        'definicion': 'Modificación al presupuesto ya aprobado durante el año: mover recursos entre partidas, cambiar calendarios, ampliar o reducir montos. Es legal y a menudo necesaria, pero es también el punto donde el presupuesto aprobado deja de parecerse al ejercido; por eso conviene leer siempre el dato modificado junto al aprobado.',
        'ley': 'Ley Federal de Presupuesto y Responsabilidad Hacendaria, art. 2, fr. II, y art. 58',
    },
    'Anexo Transversal': {
        'definicion': 'Anexo del Presupuesto que reúne, de varios ramos y programas, el dinero destinado a un mismo propósito: igualdad entre mujeres y hombres, niñas, niños y adolescentes, pueblos indígenas, jóvenes, desarrollo rural, ciencia, transición energética, grupos vulnerables y cambio climático, entre otros. El anexo no crea presupuesto nuevo: etiqueta y hace visible el que ya está disperso.',
        'ley': 'Ley Federal de Presupuesto y Responsabilidad Hacendaria, art. 2, fr. III Bis, y art. 41, fr. II',
    },
    'Programa Presupuestario (Pp)': {
        'definicion': 'Categoría de la estructura programática a la que se asigna dinero y se le puede pedir un resultado. Cada peso del Presupuesto de Egresos cuelga de un programa con clave propia, metas e indicadores, y es el nivel donde el Sistema de Evaluación del Desempeño pregunta «¿cuánto costó y qué produjo?».',
        'ley': 'Ley Federal de Presupuesto y Responsabilidad Hacendaria, art. 27, fr. I; art. 2, fr. LI, y art. 111',
    },
    'Fideicomiso Público': {
        'definicion': 'Figura en la que el Gobierno Federal —por medio de Hacienda—, una entidad, un poder o un órgano autónomo aporta recursos públicos a un patrimonio que administra una institución fiduciaria para un fin determinado. Su rasgo fiscalizable es que el dinero sale del ejercicio anual y puede permanecer años fuera del presupuesto ordinario, sin dejar de ser público.',
        'ley': 'Ley Federal de Presupuesto y Responsabilidad Hacendaria, arts. 9 y 10 · Ley Federal de las Entidades Paraestatales',
    },
    'Testigo Social': {
        'definicion': 'Persona física o moral, acreditada por la Secretaría Anticorrupción y Buen Gobierno, que vigila un procedimiento de contratación. Participa, con voz, en todas sus etapas, en las licitaciones de más de cinco millones de UMA (unos $586.6 millones de pesos en 2026), en el diálogo competitivo y donde la Secretaría lo decida. No decide ni sanciona: emite un informe final con observaciones que se publica y se integra al expediente.',
        'ley': 'Ley de Adquisiciones, Arrendamientos y Servicios del Sector Público (DOF 16-04-2025), art. 2, fr. XVIII, y art. 38 · el monto en pesos es derivado: 5,000,000 × UMA 2026 ($117.31)',
    },
    'Convenio Modificatorio': {
        'definicion': 'Instrumento que cambia el monto, el plazo o el alcance de un contrato ya adjudicado. En adquisiciones, las ampliaciones no pueden rebasar en conjunto el 20 % de lo pactado y el precio debe ser el mismo; en obra pública, la reforma de 2025 quitó el antiguo tope del 25 %. Es una figura legal y a veces inevitable, pero también el lugar donde suele alojarse el sobrecosto: un contrato que se gana barato y se termina caro casi siempre pasó por aquí.',
        'ley': 'Ley de Adquisiciones, Arrendamientos y Servicios del Sector Público (DOF 16-04-2025), art. 74 · Ley de Obras Públicas y Servicios Relacionados con las Mismas, art. 59',
    },
    'Versión Pública': {
        'definicion': 'Documento o expediente que se entrega después de eliminar u omitir las partes clasificadas como reservadas o confidenciales. Es la salida ordinaria frente a la negativa total: la regla es entregar lo que sí puede entregarse, no callar el documento entero porque una parte esté protegida.',
        'ley': 'Ley General de Transparencia y Acceso a la Información Pública (DOF 20-03-2025), art. 3, fr. XXI',
    },
    'Auditoría de Desempeño': {
        'definicion': 'Revisión que no pregunta si el dinero se gastó conforme a la norma, sino si sirvió: si el programa cumplió sus objetivos con eficiencia, eficacia y economía, y si alcanzó las metas de los indicadores aprobados en el presupuesto. Es la que responde la pregunta que más le importa a quien paga impuestos.',
        'ley': 'Ley de Fiscalización y Rendición de Cuentas de la Federación, art. 14, fr. II, incisos a) y b)',
    },
    'Pobreza Multidimensional': {
        'definicion': 'Medición que no se limita al ingreso: considera también rezago educativo y carencias de acceso a la salud, a la seguridad social, a una vivienda digna y sus servicios, y a la alimentación, además de la cohesión social. Es la metodología oficial en México y desde la reforma de julio de 2025 la hace el INEGI, que heredó esa función del extinto CONEVAL. Su virtud es que impide declarar superada la pobreza sólo porque un ingreso rebasó un umbral.',
        'ley': 'Ley General de Desarrollo Social, arts. 36 y 81 (reforma DOF 16-07-2025)',
    },
    'IVA (Impuesto al Valor Agregado)': {
        'definicion': 'Impuesto indirecto al consumo, con tasa general del 16 %, tasa del 0 % en la mayoría de los alimentos, las medicinas de patente y otros bienes que la ley enumera, y una lista de actos exentos. Funciona por traslado y acreditamiento: quien vende lo cobra por separado y lo entera, pero acredita el que pagó a sus proveedores, de modo que cada eslabón tributa sólo por el valor que añade y el consumidor final lo soporta íntegro. La tasa es la misma para todos; si pesa más en los hogares pobres o en los ricos depende de cómo se mida, y la tasa cero en alimentos y medicinas es la que inclina la balanza.',
        'ley': 'Ley del Impuesto al Valor Agregado, arts. 1o. y 2o.-A',
    },
    'IEPS (Impuesto Especial sobre Producción y Servicios)': {
        'definicion': 'Impuesto indirecto sobre consumos específicos —combustibles, bebidas alcohólicas y cerveza, tabacos, bebidas saborizadas y energetizantes, alimentos de alta densidad calórica, plaguicidas, juegos con apuestas, redes de telecomunicaciones y, desde 2026, videojuegos con violencia— cuyo fin no es sólo recaudar sino encarecer lo que impone un costo a terceros o a la salud pública. Su recaudación es la más volátil del cuadro fiscal porque la cuota de las gasolinas se reduce con estímulos fiscales que Hacienda fija cada semana según los precios internacionales.',
        'ley': 'Ley del IEPS, art. 2o. · Ley de Ingresos de la Federación 2026, art. 1o. (rubro 1.3)',
    },
    'ISAN (Impuesto Sobre Automóviles Nuevos)': {
        'definicion': 'Impuesto federal a la primera venta de un automóvil nuevo al consumidor y a su importación definitiva. Su rasgo distintivo es que, siendo federal, lo cobran los estados: si firman convenio de colaboración administrativa, se quedan con el 100 % de lo recaudado y deben dar al menos el 20 % a sus municipios. Por eso aparece a la vez en la Ley de Ingresos de la Federación y en las haciendas locales.',
        'ley': 'Ley Federal del Impuesto sobre Automóviles Nuevos, art. 1o. · Ley de Coordinación Fiscal, art. 2o.',
    },
    'Gasto Programable vs No Programable': {
        'definicion': 'Gasto programable: lo que la Federación gasta en sus programas para proveer bienes y servicios a la población —salud, escuelas, obras, seguridad—. Gasto no programable: lo que paga por obligaciones legales o del propio decreto y que no corresponde a un programa: intereses de la deuda, participaciones a estados y municipios y ADEFAS.',
        'ley': 'Ley Federal de Presupuesto y Responsabilidad Hacendaria, art. 2, frs. XXVII y XXVIII',
    },
    'Secretario(a) de Estudio y Cuenta': {
        'ley': 'Ley Orgánica del Poder Judicial de la Federación (DOF 20-12-2024), art. 15 · Manual de remuneraciones del PJF 2026 (DOF 27-02-2026)',
    },
    'Ramo Presupuestario': {
        'ley': 'Ley Federal de Presupuesto y Responsabilidad Hacendaria, art. 2, frs. XL a XLII · PEF del ejercicio correspondiente',
    },
    'Subsidio para el Empleo': {
        'definicion': 'Una cantidad que se resta del impuesto que se retiene a quien gana poco. Desde 2024 dejó de ser una tabla por tramos y es un monto fijo: el valor mensual de la UMA multiplicado por 15.02 %, para quien no rebasa $11,492.66 al mes en 2026. En enero se usó 15.59 % de la UMA de 2025 ($536.21), porque la UMA nueva rige desde febrero; de febrero a diciembre, con la UMA publicada el 9 de enero, son $535.65 al mes (el decreto los había estimado en $536.22). Si el subsidio es mayor que el impuesto, no hay impuesto a cargo, pero tampoco se entrega la diferencia.',
        'ley': 'Decreto por el que se modifica el diverso que otorga el subsidio para el empleo (DOF 31-12-2025), Artículo Segundo y transitorio segundo · el monto mensual es derivado: UMA mensual 2026 ($3,566.22) × 15.02 %',
    },
}

# Ficha nueva: el decreto del subsidio, que antes remitía a la de la UMA.
REF_NUEVAS = [
    {
        'num': 105,
        'id': 'ref-subsidio-empleo-2026',
        'categoria': 'tributario',
        'categoria_nombre': 'Marco Tributario y Fiscal',
        'cita_apa': 'Presidencia de la República. (2025, 31 de diciembre). Decreto por el que se modifica el diverso que otorga el subsidio para el empleo. Diario Oficial de la Federación.',
        'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5777649&fecha=31/12/2025',
        'descripcion': 'Fija para 2026 el subsidio en 15.02 % del valor mensual de la UMA (15.59 % de la UMA de 2025 durante enero) y el límite de ingresos en $11,492.66 mensuales. Entró en vigor el 1 de enero de 2026.',
    },
]

# Fichas bibliográficas: dos enlaces a portada que ya tienen documento, y tres
# fichas cuyas cifras no se han podido localizar en un documento oficial.
FICHAS = {
    'ref-ai-164-2024': {
        'cita_apa': 'Suprema Corte de Justicia de la Nación. (2024, 5 de noviembre). Sentencia de la acción de inconstitucionalidad 164/2024 y sus acumuladas 165/2024, 166/2024, 167/2024 y 170/2024. Tribunal Pleno (México).',
        'url': 'https://www.te.gob.mx/SAI/Documentos//704/AI%20164-2024%20y%20acumuladas.pdf',
    },
    'ref-sjf-duodecima': {
        'cita_apa': 'Suprema Corte de Justicia de la Nación. (2025, 19 de septiembre). Acuerdo General número 7/2025 (12a.), del Pleno, de 3 de septiembre de 2025, por el que se determina el inicio del tercer periodo y de la Duodécima Época del Semanario Judicial de la Federación. Diario Oficial de la Federación.',
        'url': 'https://dof.gob.mx/nota_detalle.php?codigo=5768224&fecha=19/09/2025',
    },
    'ref-asf-fideicomisos-pjf': {
        'descripcion': 'Ficha por cotejar. Remite a los informes individuales de la ASF sobre los fideicomisos del Poder Judicial, pero no enlaza ninguno, y la cifra de $15,434 millones en 13 fideicomisos no se ha localizado todavía en un informe de la ASF: debe leerse como pendiente. La extinción de esos fideicomisos no la ordenó la ASF: la dispuso el decreto que reformó la Ley Orgánica del Poder Judicial de la Federación (DOF 27-10-2023).',
    },
    'ref-pnt-asesores-scjn': {
        'descripcion': 'Ficha por cotejar. No identifica el folio de ninguna solicitud ni el formato del SIPOT consultado, de modo que las cifras que se le atribuían —de 32 a 38 plazas y 14 secretarios de estudio y cuenta por ponencia, más de 70 colaboradores por ministro y un costo de $35 a $42 millones anuales por despacho— no se han localizado en un documento oficial y deben leerse como pendientes. Cita además el art. 70 de la ley de transparencia de 2015, sustituida por la de 2025.',
    },
    'ref-ciep-pjf': {
        'descripcion': 'Ficha por cotejar. No enlaza el estudio: el título y la cifra de 54,500 plazas no se han localizado en las publicaciones del CIEP y deben leerse como pendientes. Es, además, una fuente académica, no oficial.',
    },
}

# Otros textos de la base que seguían atribuyendo la pobreza al CONEVAL.
SUSTITUCIONES = [
    ('"fuente": "Decreto que reforma el diverso por el que se otorga el subsidio para el empleo \\u00b7 DOF 31 de diciembre de 2025",',
     '"fuente": "Decreto por el que se modifica el diverso que otorga el subsidio para el empleo \\u00b7 DOF 31 de diciembre de 2025",'),
    ('la medición de pobreza del CONEVAL.',
     'la medición de pobreza, que desde la reforma de julio de 2025 hace el INEGI (Ley General de Desarrollo Social, arts. 36 y 81).'),
]


def main():
    b = BASE.read_bytes().decode('utf-8')
    reescritos = 0
    for termino, cambios in REESCRITURAS.items():
        ini, fin = _limites(b, 'glosario')
        pos = _objeto(b, ini, fin, 'termino', termino)
        if not pos:
            sys.exit('No encuentro el término «%s»; no toco nada.' % termino)
        a, z = pos
        obj = json.loads(b[a:z])
        nuevo = dict(obj)
        nuevo.update(cambios)
        if nuevo != obj:
            b = b[:a] + _cuerpo(nuevo) + b[z:]
            reescritos += 1
    ini, fin = _limites(b, 'referencias_legales')
    ancla = b.index('"id": "ref-uma2026"', ini)
    corte = b.index('\r\n    }', ancla) + len('\r\n    }')
    fichas = 0
    for ref in reversed(REF_NUEVAS):
        if '"id": "%s"' % ref['id'] not in b:
            b = b[:corte] + ',\r\n' + _cuerpo(ref) + b[corte:]
            fichas += 1
    corregidas = 0
    for rid, cambios in FICHAS.items():
        ini, fin = _limites(b, 'referencias_legales')
        pos = _objeto(b, ini, fin, 'id', rid)
        if not pos:
            sys.exit('No encuentro la ficha %s.' % rid)
        a, z = pos
        obj = json.loads(b[a:z])
        nuevo = dict(obj)
        nuevo.update(cambios)
        if nuevo != obj:
            b = b[:a] + _cuerpo(nuevo) + b[z:]
            corregidas += 1
    sust = 0
    for viejo, nuevo in SUSTITUCIONES:
        if viejo in b:
            b = b.replace(viejo, nuevo)
            sust += 1
    BASE.write_bytes(b.encode('utf-8'))
    print('glosario: %d términos con fundamento nuevo; %d fichas nuevas; %d fichas corregidas; %d sustituciones' % (reescritos, fichas, corregidas, sust))


if __name__ == '__main__':
    main()
