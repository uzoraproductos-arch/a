# -*- coding: utf-8 -*-
"""Las leyes del dinero en los tres niveles de gobierno (pedido del autor,
03-11-2026: «integrar en nuestras bases de datos las leyes de ingresos de los
tres niveles… así como las leyes de responsabilidades y adquisiciones
patrimoniales de los 3 niveles y alguna otra vinculante»).

Es la segunda página del Marco Legal Hacendario (Aprende › Biblioteca). No
copia leyes: dice cuál rige, quién la aprueba, dónde se publica y desde
cuándo, con la liga al texto vigente.

- Nivel federal: cada ley con su fecha de publicación y de última reforma,
  tal como las da el índice de Leyes Federales Vigentes de la Cámara de
  Diputados (consultado el 03-11-2026). Lo que se dice de cada una sale de su
  artículo 1 (o del que se cita), leído en el texto vigente.
- Nivel estatal: el periódico oficial y el congreso de cada entidad. Solo
  lleva liga la dirección que respondió al cotejo del 03-11-2026 (VERIFICADO);
  la que no respondió va con su nombre y sin liga, nunca inventada. El texto
  de cada ley estatal aún no se integra: es un pendiente de la plataforma.
- Nivel municipal: lo dice la Constitución (art. 115, fr. IV): el ayuntamiento
  propone y el congreso del estado aprueba. Las 2,462 leyes, una por una, son
  un pendiente de la plataforma.

Los puntos ciegos (PUNTOS) salen de cotejar lo que circula sobre estas leyes
contra su texto: cada uno cita el artículo que lo sostiene.

Lo usan apartados.generar() (pagina()), pendientes.py (pendientes()),
asistente.py (fichas()) y planisferio.py (estado(), para el portal).
"""
import html

ARCHIVO = 'marco-legal-tres-niveles.html'
TITULO = 'Las leyes del dinero en los tres niveles'
COTEJO = '03-11-2026'
LB = 'https://www.diputados.gob.mx/LeyesBiblio/'
INDICE = LB + 'index.htm'
OJN = 'https://www.ordenjuridico.gob.mx/ambest.php'
CPEUM = LB + 'pdf/CPEUM.pdf'
SDA_PAGINA = 'https://www.disciplinafinanciera.hacienda.gob.mx/es/DISCIPLINA_FINANCIERA/Entidades_Federativas_2025'

TEMAS = [
    ('ingresos', '💵', 'Ingresos', 'Lo que se cobra y cómo se reparte'),
    ('presupuesto', '📒', 'Presupuesto', 'Cómo se aprueba y se ejerce el gasto'),
    ('deuda', '🏦', 'Deuda', 'Cuándo y cuánto se puede pedir prestado'),
    ('adquisiciones', '🛒', 'Adquisiciones y obra pública', 'Cómo se compra y se construye con dinero público'),
    ('patrimonio', '🏛️', 'Patrimonio', 'Los bienes públicos y los daños que causa el Estado'),
    ('responsabilidades', '⚖️', 'Responsabilidades', 'Qué pasa cuando un servidor público falla'),
    ('cuentas', '🔎', 'Contabilidad, fiscalización y transparencia', 'Cómo se rinde cuenta del dinero'),
]

# (id, tema, nombre, siglas, pdf, publicada, última reforma o None, qué hace,
# a quién alcanza). Fechas del índice de la Cámara de Diputados (COTEJO).
FEDERALES = [
    ('lif', 'ingresos', 'Ley de Ingresos de la Federación para el Ejercicio Fiscal de 2026', 'LIF 2026', 'LIF_2026.pdf', '07-11-2025', None,
     'Lo que la Federación estima recibir en 2026: $10,193,683.7 millones de pesos, en «cantidades estimadas» (art. 1o.).',
     'federal'),
    ('cff', 'ingresos', 'Código Fiscal de la Federación', 'CFF', 'CFF.pdf', '31-12-1981', '09-04-2026',
     'Las reglas comunes de los impuestos federales: quién paga, cómo se cobra, las multas y los medios para defenderse.',
     'federal'),
    ('lcf', 'ingresos', 'Ley de Coordinación Fiscal', 'LCF', 'LCF.pdf', '27-12-1978', '03-01-2024',
     'Cómo se reparten con los estados y los municipios las participaciones (Ramo 28) y las aportaciones (Ramo 33).',
     'tres'),
    ('lih', 'ingresos', 'Ley de Ingresos sobre Hidrocarburos', 'LIH', 'LIH.pdf', '11-08-2014', '28-12-2025',
     'Lo que el Estado recibe por la exploración y extracción de petróleo y gas.',
     'federal'),
    ('lfprh', 'presupuesto', 'Ley Federal de Presupuesto y Responsabilidad Hacendaria', 'LFPRH', 'LFPRH.pdf', '30-03-2006', '09-04-2026',
     'Cómo se programa, aprueba, ejerce y evalúa el gasto federal, con sus plazos.',
     'federal'),
    ('lfar', 'presupuesto', 'Ley Federal de Austeridad Republicana', 'LFAR', 'LFAR.pdf', '19-11-2019', '16-04-2025',
     'Los límites al gasto de operación del gobierno federal.',
     'federal'),
    ('lfdp', 'deuda', 'Ley Federal de Deuda Pública', 'LFDP', '136_300118.pdf', '31-12-1976', '30-01-2018',
     'La deuda del Ejecutivo Federal y de sus entidades (art. 1o.). La de los estados y los municipios no está aquí: está en la LDF.',
     'federal'),
    ('ldf', 'deuda', 'Ley de Disciplina Financiera de las Entidades Federativas y los Municipios', 'LDF', 'LDFEFM.pdf', '27-04-2016', '10-05-2022',
     'El equilibrio del gasto y las reglas de deuda de estados y municipios: el Sistema de Alertas (arts. 43 a 45) y el techo de financiamiento neto que '
     'fija a cada nivel: hasta 15 %, 5 % o 0 % de sus ingresos de libre disposición (art. 46).',
     'estados'),
    ('laassp', 'adquisiciones', 'Ley de Adquisiciones, Arrendamientos y Servicios del Sector Público', 'LAASSP', 'LAASSP.pdf', '16-04-2025', None,
     'Cómo compra y renta el gobierno federal. Es una ley nueva: abrogó la del 4 de enero de 2000 (transitorio segundo).',
     'recursos'),
    ('lopsrm', 'adquisiciones', 'Ley de Obras Públicas y Servicios Relacionados con las Mismas', 'LOPSRM', 'LOPSRM.pdf', '04-01-2000', '14-11-2025',
     'Cómo contrata obra pública el gobierno federal.',
     'recursos'),
    ('lapp', 'adquisiciones', 'Ley de Asociaciones Público Privadas', 'LAPP', 'LAPP.pdf', '16-01-2012', '14-11-2025',
     'Los contratos de largo plazo en que un privado construye u opera y el gobierno paga por el servicio.',
     'federal'),
    ('lgbn', 'patrimonio', 'Ley General de Bienes Nacionales', 'LGBN', 'LGBN.pdf', '20-05-2004', '14-11-2025',
     'Los bienes que forman el patrimonio de la Nación y el régimen de los bienes de la Federación (art. 1).',
     'federal'),
    ('lfrpe', 'patrimonio', 'Ley Federal de Responsabilidad Patrimonial del Estado', 'LFRPE', 'LFRPE.pdf', '31-12-2004', '29-12-2023',
     'La indemnización a quien sufre un daño en sus bienes o derechos por la actividad administrativa irregular del Estado (art. 1).',
     'federal'),
    ('lgra', 'responsabilidades', 'Ley General de Responsabilidades Administrativas', 'LGRA', 'LGRA.pdf', '18-07-2016', '15-12-2025',
     'Las obligaciones de los servidores públicos, las faltas y sus sanciones, en toda la República (art. 1), y las declaraciones patrimonial y de intereses (art. 32).',
     'tres'),
    ('lgsna', 'responsabilidades', 'Ley General del Sistema Nacional Anticorrupción', 'LGSNA', 'LGSNA_200521.pdf', '18-07-2016', '20-05-2021',
     'Cómo se coordinan los tres niveles para prevenir, detectar y sancionar la corrupción.',
     'tres'),
    ('lfrsp', 'responsabilidades', 'Ley Federal de Responsabilidades de los Servidores Públicos', 'LFRSP', 'LFRSP.pdf', '31-12-1982', '01-04-2024',
     'Hoy solo rige el juicio político y la declaración de procedencia: su título primero se derogó el 18-07-2016, cuando entró la LGRA.',
     'federal'),
    ('lgcg', 'cuentas', 'Ley General de Contabilidad Gubernamental', 'LGCG', 'LGCG.pdf', '31-12-2008', '14-05-2026',
     'La contabilidad igual para los tres niveles, y la obligación de publicar en internet las leyes de ingresos y los presupuestos (arts. 60, 63 y 65).',
     'tres'),
    ('lfrcf', 'cuentas', 'Ley de Fiscalización y Rendición de Cuentas de la Federación', 'LFRCF', 'LFRCF.pdf', '18-07-2016', '15-05-2026',
     'Cómo revisa la Auditoría Superior de la Federación la Cuenta Pública, también el dinero federal que gastan estados y municipios.',
     'tres'),
    ('lgtaip', 'cuentas', 'Ley General de Transparencia y Acceso a la Información Pública', 'LGTAIP', 'LGTAIP.pdf', '20-03-2025', None,
     'Lo que todo ente público debe publicar y cómo se pide información.',
     'tres'),
]

ALCANCE = {
    'federal': 'Federación',
    'tres': 'Los tres niveles',
    'estados': 'Estados y municipios',
    'recursos': 'Federación, y estados y municipios cuando gastan dinero federal por convenio (no el Ramo 33)',
}

# Lo que dice la Constitución de quién aprueba cada ley de ingresos.
QUIEN = [
    ('Federal', 'Ley de Ingresos de la Federación', 'El Congreso de la Unión: empieza en la Cámara de Diputados y pasa al Senado (art. 72, inciso H, y art. 73, fr. VII).',
     'Diario Oficial de la Federación'),
    ('Estatal', 'Ley de Ingresos del estado', 'El congreso del estado, a propuesta del gobernador, según la constitución de cada entidad. La LDF (art. 5) fija lo que debe traer.',
     'El periódico oficial del estado'),
    ('Municipal', 'Ley de Ingresos de cada municipio', 'El ayuntamiento propone las cuotas y tarifas, y el congreso del estado las aprueba (art. 115, fr. IV). La LDF (art. 18) fija lo que debe traer.',
     'El periódico oficial del estado, y la página de internet del municipio (LGCG, arts. 60 y 65)'),
]

# Puntos ciegos: (título, lo que suele decirse, lo que dice la ley).
PUNTOS = [
    ('La obligación de publicarlas en internet no está en la LDF',
     'Se suele atribuir a la Ley de Disciplina Financiera.',
     'Está en la Ley General de Contabilidad Gubernamental: la iniciativa (art. 63) y la ley aprobada, con sus dictámenes y actas (art. 65), van a la página de internet de '
     'cada gobierno. La LDF dice qué deben contener (arts. 5 y 18).'),
    ('Una ley de ingresos es un cálculo, no lo cobrado',
     'Se lee como lo que el gobierno tiene.',
     'La LIF 2026 habla de «cantidades estimadas» (art. 1o.). Lo que de verdad se cobró se sabe en la Cuenta Pública, más de un año después.'),
    ('El municipio no fija sus impuestos',
     'Se dice que «el municipio aprobó su ley de ingresos».',
     'El ayuntamiento propone las cuotas, las tarifas y las tablas de valores del predial; quien las aprueba es el congreso del estado (Constitución, art. 115, fr. IV).'),
    ('La ley federal de compras no alcanza al Ramo 33',
     'Se cree que todo dinero federal se compra con la ley federal.',
     'Estados y municipios usan la LAASSP o la ley de obra federal solo con dinero federal entregado por convenio. Los fondos del capítulo V de la Ley de Coordinación '
     'Fiscal, el Ramo 33, quedan fuera (LAASSP, art. 1, fr. V; LOPSRM, art. 1, fr. VI): esas compras siguen la ley del estado.'),
    ('La ley federal de adquisiciones es nueva',
     'Notas y guías siguen citando artículos de la ley de 2000.',
     'La LAASSP vigente se publicó el 16-04-2025 y abrogó la anterior (transitorio segundo): un número de artículo citado antes de esa fecha puede ya no decir lo mismo.'),
    ('La ley de responsabilidades ya es una sola para todos',
     'Se busca una ley distinta para cada nivel.',
     'La LGRA es general: rige en toda la República y reparte las competencias entre los órdenes de gobierno (art. 1). La vieja ley federal de 1982 solo conserva el juicio '
     'político y la declaración de procedencia.'),
    ('El Sistema de Alertas mide con lo que le entregan',
     'Se lee el semáforo de la deuda como una auditoría.',
     'Hacienda evalúa «única y exclusivamente» con la información que dan los propios gobiernos y la del Registro Público Único, y no responde de su veracidad (LDF, art. 43).'),
    ('Un estado no puede endeudarse para cualquier cosa',
     'La deuda se discute solo por su monto.',
     'Estados y municipios solo pueden endeudarse para inversión pública productiva y su refinanciamiento, nunca con acreedores extranjeros ni en moneda extranjera '
     '(Constitución, art. 117, fr. VIII).'),
]

# Cada entidad: (clave, nombre del periódico oficial, liga del periódico o None,
# liga del congreso o None). Solo entra la liga que respondió el COTEJO.
ESTADOS = {
    'AGS': ('Periódico Oficial del Estado de Aguascalientes', 'https://eservicios2.aguascalientes.gob.mx/periodicooficial/', 'https://congresoags.gob.mx/'),
    'BC': ('Periódico Oficial del Estado de Baja California', 'https://periodicooficial.ebajacalifornia.gob.mx/', 'https://www.congresobc.gob.mx/'),
    'BCS': ('Boletín Oficial del Gobierno del Estado de Baja California Sur', None, None),
    'CAM': ('Periódico Oficial del Estado de Campeche', 'https://periodicooficial.campeche.gob.mx/', 'https://www.congresocam.gob.mx/'),
    'COAH': ('Periódico Oficial del Gobierno del Estado de Coahuila', 'https://periodico.segobcoahuila.gob.mx/', None),
    'COL': ('Periódico Oficial «El Estado de Colima»', 'https://periodicooficial.col.gob.mx/', 'https://congresocol.gob.mx/'),
    'CHIS': ('Periódico Oficial del Estado de Chiapas', None, 'https://www.congresochiapas.gob.mx/'),
    'CHIH': ('Periódico Oficial del Estado de Chihuahua', 'https://chihuahua.gob.mx/periodico-oficial', 'https://www.congresochihuahua.gob.mx/'),
    'CDMX': ('Gaceta Oficial de la Ciudad de México', None, 'https://www.congresocdmx.gob.mx/'),
    'DGO': ('Periódico Oficial del Gobierno del Estado de Durango', 'https://periodicooficial.durango.gob.mx/', 'https://congresodurango.gob.mx/'),
    'GTO': ('Periódico Oficial del Gobierno del Estado de Guanajuato', 'https://periodico.guanajuato.gob.mx/', None),
    'GRO': ('Periódico Oficial del Gobierno del Estado de Guerrero', None, 'https://congresogro.gob.mx/'),
    'HGO': ('Periódico Oficial del Estado de Hidalgo', 'https://periodico.hidalgo.gob.mx/', 'https://www.congresohidalgo.gob.mx/'),
    'JAL': ('Periódico Oficial «El Estado de Jalisco»', 'https://periodicooficial.jalisco.gob.mx/', 'https://www.congresojal.gob.mx/'),
    'MÉX': ('Periódico Oficial del Gobierno del Estado de México, «Gaceta del Gobierno»', None, 'https://www.legislativoedomex.gob.mx/'),
    'MICH': ('Periódico Oficial del Gobierno Constitucional del Estado de Michoacán de Ocampo', None, None),
    'MOR': ('Periódico Oficial «Tierra y Libertad»', 'https://periodico.morelos.gob.mx/', 'https://www.congresomorelos.gob.mx/'),
    'NAY': ('Periódico Oficial, Órgano del Gobierno del Estado de Nayarit', 'https://periodicooficial.nayarit.gob.mx/', 'https://www.congresonayarit.gob.mx/'),
    'NL': ('Periódico Oficial del Estado de Nuevo León', None, 'https://www.hcnl.gob.mx/'),
    'OAX': ('Periódico Oficial del Gobierno del Estado de Oaxaca', None, 'https://www.congresooaxaca.gob.mx/'),
    'PUE': ('Periódico Oficial del Estado de Puebla', 'https://periodicooficial.puebla.gob.mx/', 'https://www.congresopuebla.gob.mx/'),
    'QRO': ('Periódico Oficial del Gobierno del Estado de Querétaro, «La Sombra de Arteaga»', 'https://lasombradearteaga.segobqueretaro.gob.mx/', None),
    'QROO': ('Periódico Oficial del Estado de Quintana Roo', None, 'https://www.congresoqroo.gob.mx/'),
    'SLP': ('Periódico Oficial del Gobierno del Estado «Plan de San Luis»', 'https://periodicooficial.slp.gob.mx/', 'https://congresosanluis.gob.mx/'),
    'SIN': ('Periódico Oficial «El Estado de Sinaloa»', None, 'https://www.congresosinaloa.gob.mx/'),
    'SON': ('Boletín Oficial del Gobierno del Estado de Sonora', 'https://boletinoficial.sonora.gob.mx/', 'https://congresoson.gob.mx/'),
    'TAB': ('Periódico Oficial del Estado de Tabasco', None, 'https://congresotabasco.gob.mx/'),
    'TAM': ('Periódico Oficial del Estado de Tamaulipas', 'https://po.tamaulipas.gob.mx/', 'https://www.congresotamaulipas.gob.mx/'),
    'TLAX': ('Periódico Oficial del Gobierno del Estado de Tlaxcala', None, 'https://congresodetlaxcala.gob.mx/'),
    'VER': ('Gaceta Oficial del Estado de Veracruz', None, None),
    'YUC': ('Diario Oficial del Gobierno del Estado de Yucatán', 'https://www.yucatan.gob.mx/gobierno/diario_oficial.php', 'https://www.congresoyucatan.gob.mx/'),
    'ZAC': ('Periódico Oficial, Órgano del Gobierno del Estado de Zacatecas', None, 'https://www.congresozac.gob.mx/'),
}

# Lo que falta integrar de cada estado (pendiente de la plataforma).
FALTA_ESTADO = ('su Ley de Ingresos 2026, su ley de hacienda, su ley de adquisiciones, su ley de obra pública, su ley de deuda pública y, si su congreso '
                'expidió una, su ley de responsabilidades')


MUNICIPIOS = 2462   # del padrón del INEGI, sin las 16 alcaldías ni la clave «No especificado»: municipios() lo comprueba


def municipios(padron, abbr=None):
    """Los municipios de verdad: sin claves 990 y más («No especificado») ni alcaldías."""
    ents = [abbr] if abbr else [a for a in padron['ent'] if a != 'CDMX']
    n = sum(1 for a in ents for x in padron['ent'][a]['lista'] if int(x[0]) < 990)
    if abbr is None and n != MUNICIPIOS:
        raise SystemExit('leyes_niveles: el padrón tiene %d municipios, no %d' % (n, MUNICIPIOS))
    return n


def _chip(e, pend=None):
    p = ' data-pend="%s"' % pend if pend else ''
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, p, 'calculada' if e == 'derivado' else e)


def _a(url, tx):
    return '<a href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>' % (html.escape(url, quote=True), html.escape(tx))


def pdf(f):
    return LB + 'pdf/' + f


def federales():
    return [dict(zip(('id', 'tema', 'nom', 'sig', 'pdf', 'pub', 'ult', 'que', 'alc'), x)) for x in FEDERALES]


def pendientes():
    """Para el Registro de pendientes (pendientes.py)."""
    import pendientes as P
    ap = [(ARCHIVO, 'Aprende · ' + TITULO)]
    return [
        {'id': 'leyes-estatales', 'tema': 'Marco legal', 'que': 'El texto de las leyes del dinero de los 32 estados',
         'porque': ('Las leyes del dinero de cada entidad (%s) existen y se publican en su periódico oficial; falta cotejarlas e integrarlas. En el cotejo del %s '
                    'no respondieron algunas direcciones de periódicos oficiales y congresos: van con su nombre y sin liga.') % (FALTA_ESTADO, COTEJO),
         'responsable': P.PLATAFORMA, 'enlace': OJN, 'enlace_txt': 'Orden Jurídico Nacional (Gobernación), ámbito estatal',
         'aparece': ap + [('planisferio.html', 'Planisferio · cada portal, «Sus leyes del dinero»')]},
        {'id': 'leyes-municipales', 'tema': 'Marco legal', 'que': 'Las leyes de ingresos de los %s municipios, una por una' % format(MUNICIPIOS, ','),
         'porque': 'Las aprueba el congreso de cada estado y se publican en su periódico oficial; la plataforma aún no las integra municipio por municipio.',
         'responsable': P.PLATAFORMA, 'enlace': OJN, 'enlace_txt': 'Orden Jurídico Nacional (Gobernación), ámbito estatal',
         'aparece': ap},
        {'id': 'deuda-municipios', 'tema': 'Deuda', 'que': 'El saldo de la deuda de cada municipio (lo que debe) en el Sistema de Alertas, municipio por municipio',
         'porque': ('Hacienda mide también a los municipios con deuda inscrita (LDF, art. 43). Lo que cada municipio pagó por sus créditos y pidió prestado en 2024 ya '
                    'está integrado, con su cuenta pública al INEGI (anclar_deuda_municipios.py); lo que debe al cierre, no: el archivo del Sistema de Alertas no se pudo '
                    'descargar en el cotejo del %s (el portal de disciplina financiera no respondió) y no se escribe una cifra sin su documento.') % COTEJO,
         'responsable': P.PLATAFORMA, 'enlace': SDA_PAGINA, 'enlace_txt': 'Sistema de Alertas (SHCP)',
         'aparece': [('planisferio.html', 'Planisferio · cada portal, «Su deuda» y el mapa de sus municipios')]},
    ]


def estado(e, n_mun):
    """El bloque «Sus leyes del dinero» del portal del Planisferio."""
    nom = e['name']
    po, url_po, url_co = ESTADOS[e['abbr']]
    lpo = _a(url_po, po) if url_po else '%s <small>(liga por cotejar)</small>' % html.escape(po)
    lco = _a(url_co, 'Congreso de ' + nom) if url_co else 'el congreso del estado <small>(liga por cotejar)</small>'
    if e['abbr'] == 'CDMX':
        mun = ('Sus 16 alcaldías no son municipios ni tienen ley de ingresos propia: la Ciudad tiene una sola, que aprueba su Congreso.')
    else:
        mun = ('Las leyes de ingresos de sus %d municipios las propone cada ayuntamiento y las aprueba el congreso del estado (Constitución, art. 115, fr. IV); '
               'se publican en el mismo periódico oficial.' % n_mun)
    return ('<ul class="leg-niveles">'
            '<li><b>Dónde se publican sus leyes:</b> %s</li>'
            '<li><b>Quién las aprueba:</b> %s, que también reúne su legislación vigente.</li>'
            '<li><b>Sus municipios:</b> %s</li>'
            '<li><b>Lo que aún no integramos:</b> el texto de %s %s</li></ul>'
            '<p><a href="%s#edo-%s">⚖️ Las leyes del dinero en los tres niveles, con %s</a></p>') % (
        lpo, lco, mun, FALTA_ESTADO, _chip('pendiente', 'leyes-estatales'), ARCHIVO, _clave(e['abbr']), nom)


def _clave(a):
    import unicodedata
    return unicodedata.normalize('NFKD', a).encode('ascii', 'ignore').decode().lower()


def _fed_tabla(tema):
    filas = []
    for f in federales():
        if f['tema'] != tema:
            continue
        filas.append('<li id="ley-%s"><b>%s</b> <span class="leg-sig">(%s)</span><br>%s<small>A quién alcanza: %s · publicada en el DOF el %s · %s</small></li>' % (
            f['id'], _a(pdf(f['pdf']), f['nom']), f['sig'], html.escape(f['que']), ALCANCE[f['alc']], f['pub'],
            'última reforma DOF %s' % f['ult'] if f['ult'] else 'sin reforma'))
    return '<ul class="leg-leyes">%s</ul>' % ''.join(filas)


def _estados_tabla(base, padron):
    filas = []
    for e in sorted(base['estados'], key=lambda x: _clave(x['name'])):
        po, url_po, url_co = ESTADOS[e['abbr']]
        n = municipios(padron, e['abbr'])
        filas.append('<li id="edo-%s"><b>%s</b><br>Se publican en: %s<br>Las aprueba: %s<br><small>%s</small></li>' % (
            _clave(e['abbr']), html.escape(e['name']),
            _a(url_po, po) if url_po else '%s <small>(liga por cotejar)</small>' % html.escape(po),
            _a(url_co, 'su congreso') if url_co else 'su congreso <small>(liga por cotejar)</small>',
            '16 alcaldías, sin ley de ingresos propia' if e['abbr'] == 'CDMX' else 'Leyes de ingresos municipales: %d municipios' % n))
    return ('<p class="pa-chico">Las ligas respondieron el %s; la que no respondió va sin liga.</p><ul class="leg-leyes leg-estados">%s</ul>'
            % (COTEJO, ''.join(filas)))


# Reformas recientes: lo que junta el vigía legislativo (vigia_legislativo.py,
# 05-11-2026). La lista la pinta vigia-legislativo.js al abrir la página,
# leyendo la bandeja que el flujo de GitHub actualiza cada día; así no hay que
# regenerar la página para ver lo nuevo. Todo va «por cotejar»: el vigía
# detecta y propone, nunca escribe en la base (AGENTS.md §2).
BANDEJA = 'docs/legislativo/bandeja.json'
REFORMAS = {
    'id': 'reformas-recientes', 'titulo': '🛰️ Reformas recientes, por cotejar',
    'texto': ('Cada día, nuestro vigía legislativo lee el sumario del Diario Oficial de la Federación y el índice de Leyes Federales Vigentes de la '
              'Cámara de Diputados, y apunta lo que toca a las leyes del dinero: el Código Fiscal, los impuestos, el presupuesto, la deuda, las compras, '
              'la fiscalización, las responsabilidades, el antilavado, la Ley Fintech y los datos personales. Lo que aparece aquí está <b>sin verificar</b>: '
              'es el título, la fecha y la liga a su documento, nunca el texto de la reforma. Entra a la plataforma solo después de cotejarse, con su vigencia.'),
    'tarjetas': [],
    'bloque': ('<div id="vigiaLegislativo" data-bandeja="%s"><p>La lista se carga al abrir la página. Si no aparece, consulta el %s y el %s.</p></div>'
               '<p class="pa-chico">El Senado no está en la lista: su portal no da un índice que se pueda leer sin adivinar. Lo que aprueba llega '
               'igual al DOF cuando se publica, que es cuando obliga.</p>') % (
        BANDEJA, _a('https://dof.gob.mx/', 'Diario Oficial de la Federación'), _a(INDICE, 'índice de Leyes Federales Vigentes')),
}


def pagina(base, padron):
    """El diccionario de la página para apartados.py."""
    for a in (e['abbr'] for e in base['estados']):
        if a not in ESTADOS:
            raise SystemExit('leyes_niveles: falta %s en ESTADOS' % a)
    quien = ''.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td></tr>' % tuple(html.escape(x) for x in q) for q in QUIEN)
    t_quien = ('<div class="leg-tabla-caja"><table class="leg-tabla"><thead><tr><th scope="col">Nivel</th><th scope="col">Ley</th>'
               '<th scope="col">Quién la aprueba</th><th scope="col">Dónde se publica</th></tr></thead><tbody>%s</tbody></table></div>' % quien)
    puntos = ''.join('<li><b>%s.</b> <i>Lo que suele decirse:</i> %s<br><i>Lo que dice la ley:</i> %s</li>' % tuple(html.escape(x) for x in p) for p in PUNTOS)
    secc = [
        {'id': 'quien', 'titulo': 'Quién aprueba cada ley de ingresos y dónde se publica',
         'texto': 'Lo dice la Constitución (%s), y lo completan la LDF y la Ley General de Contabilidad Gubernamental.' % _a(CPEUM, 'texto vigente'),
         'tarjetas': [], 'bloque': t_quien},
        {'id': 'puntos-ciegos', 'titulo': 'Lo que casi nadie te cuenta de estas leyes',
         'texto': 'Cotejamos lo que suele decirse contra el texto vigente. Cada punto cita el artículo que lo sostiene.',
         'tarjetas': [], 'bloque': '<ol class="leg-ciegos">%s</ol>' % puntos},
    ]
    for t, ico, nom, lema in TEMAS:
        secc.append({'id': 'fed-' + t, 'titulo': '%s Federal · %s' % (ico, nom), 'texto': lema + '.', 'tarjetas': [], 'bloque': _fed_tabla(t)})
    secc.append(REFORMAS)
    secc += [
        {'id': 'estatal', 'titulo': 'Los 32 estados: dónde están sus leyes',
         'texto': ('Cada estado tiene sus propias leyes de ingresos, hacienda, adquisiciones, obra pública y deuda; la LGRA, la LDF y la LGCG ya los obligan '
                   'a todos. Aún no integramos el texto de cada ley estatal %s: aquí está dónde se publica y quién la aprueba.') % _chip('pendiente', 'leyes-estatales'),
         'tarjetas': [], 'bloque': _estados_tabla(base, padron)},
        {'id': 'municipal', 'titulo': 'Los municipios: su ley de ingresos la aprueba el estado',
         'texto': '', 'tarjetas': [],
         'bloque': ('<p>Cada uno de los %s municipios tiene su propia ley de ingresos cada año: la propone su ayuntamiento y la aprueba el congreso del '
                    'estado (Constitución, art. 115, fr. IV). Se publica en el periódico oficial del estado (tabla de arriba) y, ya aprobada, con sus dictámenes y '
                    'actas, en la página de internet del municipio (LGCG, art. 65). Sus compras y obras siguen la ley del estado, salvo cuando gastan dinero federal '
                    'entregado por convenio.</p><p>Las %s leyes, una por una, aún no las integramos %s. Mientras, en el %s están los ingresos que cada '
                    'municipio reportó al INEGI.</p>') % (format(municipios(padron), ','), format(MUNICIPIOS, ','), _chip('pendiente', 'leyes-municipales'), '<a href="planisferio.html">Planisferio</a>')},
        {'id': 'no-dice', 'titulo': 'Lo que esta página no dice', 'texto': '', 'tarjetas': [],
         'bloque': ('<ul><li>No reproduce las leyes: lleva a su texto vigente. Si una reforma cambia una fecha, manda el texto oficial.</li>'
                    '<li>Las fechas federales son las del %s, consultado el %s.</li>'
                    '<li>La Ley de Ingresos de la Federación para 2027 aún no aparece en ese índice al %s.</li>'
                    '<li>Los preceptos clave, con su texto palabra por palabra, están en el <a href="marco-legal.html">Marco legal hacendario</a>.</li></ul>')
         % (_a(INDICE, 'índice de Leyes Federales Vigentes de la Cámara de Diputados'), COTEJO, COTEJO)},
    ]
    return {
        'archivo': ARCHIVO, 'menu': TITULO, 'menu_archivo': 'aprende.html',
        'padre': ('aprende.html', 'Aprende'), 'padre2': ('marco-legal.html', 'Marco Legal Hacendario'),
        'icono': '⚖️', 'titulo': TITULO, 'lema': 'Ingresos, deuda, compras, patrimonio y responsabilidades: federal, estatal y municipal',
        'estilos': ['asistente.css'], 'scripts': ['vigia-legislativo.js'],
        'entrada': ('Cada nivel de gobierno cobra, gasta, compra, se endeuda y rinde cuentas con sus propias leyes. Aquí está cuál rige, quién la aprueba, '
                    'dónde se publica y desde cuándo, con la liga a su texto vigente: %d leyes federales, los periódicos oficiales y congresos de las 32 '
                    'entidades y la regla de los municipios.') % len(FEDERALES),
        'secciones': secc,
    }


def fichas(base):
    """Fichas del chat: una por ley federal, una por estado y las de los niveles."""
    out = []
    pal = {'ingresos': ' ley de ingresos cobrar impuestos recaudacion', 'presupuesto': ' presupuesto gasto',
           'deuda': ' deuda prestamos endeudamiento credito', 'adquisiciones': ' adquisiciones compras licitacion contratos obra publica proveedores',
           'patrimonio': ' patrimonio bienes nacionales inmuebles indemnizacion responsabilidad patrimonial', 'responsabilidades': ' responsabilidades sanciones faltas servidores publicos corrupcion declaracion patrimonial',
           'cuentas': ' contabilidad fiscalizacion transparencia auditoria'}
    for f in federales():
        out.append({'t': 'ficha', 'tit': '%s (%s)' % (f['nom'], f['sig']),
                    'txt': '%s A quién alcanza: %s. Publicada en el DOF el %s; %s.' % (
                        f['que'], ALCANCE[f['alc']], f['pub'], 'última reforma DOF ' + f['ult'] if f['ult'] else 'sin reforma'),
                    'ci': [], 'fu': [{'tx': 'Cámara de Diputados, Leyes Federales Vigentes: ' + f['sig'], 'url': pdf(f['pdf'])}],
                    'ir': ['%s#ley-%s' % (ARCHIVO, f['id']), TITULO],
                    # «¿Cuándo se reformó…?» (05-11-2026, vigía legislativo): la ficha también contesta la fecha.
                    'k': '%s %s ley federal cuando se reformo ultima reforma%s' % (f['nom'], f['sig'], pal[f['tema']])})
    out.append({'t': 'ficha', 'tit': 'Reformas recientes: qué leyes cambiaron (vigía legislativo)',
                'txt': ('Cada día, nuestro vigía legislativo lee el sumario del Diario Oficial de la Federación y el índice de Leyes Federales Vigentes '
                        'de la Cámara de Diputados, y apunta las reformas que tocan las leyes del dinero. La lista está en la sección «Reformas '
                        'recientes», sin verificar hasta su cotejo; también dice qué partes de Auditavisión citan una reforma anterior a la vigente.'),
                'ci': [], 'fu': [{'tx': 'Diario Oficial de la Federación, sumario del día', 'url': 'https://dof.gob.mx/'},
                                 {'tx': 'Cámara de Diputados, Leyes Federales Vigentes', 'url': INDICE}],
                'ir': ['%s#reformas-recientes' % ARCHIVO, TITULO],
                'k': ('reformas recientes leyes cambiaron cambio esta semana hoy nuevas reformas ultimas reformas publicadas dof diario oficial '
                      'vigia legislativo decreto reforma ley camara de diputados senado')})
    for e in base['estados']:
        po, url_po, url_co = ESTADOS[e['abbr']]
        fu = [{'tx': po, 'url': url_po}] if url_po else []
        if url_co:
            fu.append({'tx': 'Congreso de ' + e['name'], 'url': url_co})
        out.append({'t': 'ficha', 'tit': 'Las leyes del dinero de %s' % e['name'],
                    'txt': ('Las leyes de %s (ingresos, hacienda, adquisiciones, obra pública, deuda) las aprueba su congreso y se publican en el %s. '
                            '%s El texto de cada ley aún no lo integramos.') % (
                        e['name'], po, 'Sus alcaldías no tienen ley de ingresos propia.' if e['abbr'] == 'CDMX' else
                        'Las leyes de ingresos de sus municipios también las aprueba el congreso del estado (Constitución, art. 115, fr. IV).'),
                    'ci': [], 'pend': 'leyes-estatales', 'fu': fu or [{'tx': 'Orden Jurídico Nacional', 'url': OJN}],
                    'ir': ['%s#edo-%s' % (ARCHIVO, _clave(e['abbr'])), TITULO],
                    'k': 'leyes ley de ingresos estatal periodico oficial congreso local adquisiciones deuda responsabilidades %s %s' % (e['name'], po)})
    out.append({'t': 'ficha', 'tit': 'La ley de ingresos de un municipio: quién la aprueba y dónde se publica',
                'txt': ('La propone el ayuntamiento y la aprueba el congreso del estado (Constitución, art. 115, fr. IV); se publica en el periódico oficial del estado '
                        'y, ya aprobada, en la página de internet del municipio (Ley General de Contabilidad Gubernamental, art. 65).'),
                'ci': [], 'pend': 'leyes-municipales', 'fu': [{'tx': 'Constitución Política, art. 115', 'url': CPEUM}, {'tx': 'Ley General de Contabilidad Gubernamental', 'url': pdf('LGCG.pdf')}],
                'ir': ['%s#municipal' % ARCHIVO, TITULO],
                'k': 'ley de ingresos municipal municipio ayuntamiento cabildo quien aprueba donde se publica predial tarifas cuotas'})
    return out
