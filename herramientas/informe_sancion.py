# -*- coding: utf-8 -*-
"""«Documentar para sancionar», el informe especial de la ASF, en el formato
con que conversa el bot y en su página de Informes oficiales (pedido del
autor, 27-10-2026: «integrarlo al proyecto como metodología de aprendizaje
para el bot y la extracción de la información importante», en la tarjeta
Informes oficiales de Datos).

El documento: Auditoría Superior de la Federación, «Documentar para
sancionar. De la irregularidad a la sanción», primera edición, julio de
2026, 69 páginas impresas (72 del PDF). Lo publica la ASF entre los
Informes Especiales de la primera entrega de la Cuenta Pública 2025. La
copia que pasó el autor y la del sitio de la ASF tienen la misma huella
SHA-256. Es de distribución gratuita, pero no se copia entero: se explica en
sencillo, con su página, y se enlaza al PDF.

Lo que se tomó de él:
- la cadena de la irregularidad a la sanción (caps. 2.4, 5 y 6);
- los cuatro elementos que debe probar un expediente y los cinco requisitos
  de cada uno (cap. 3.4, pp. 13 a 16; las láminas son imagen y se
  transcribieron a mano);
- las 20 matrices del capítulo 4 (pp. 17 a 62), en
  docs/informes/documentar-para-sancionar.json;
- los cuatro problemas que la propia ASF reconoce (cap. 2).

Lo que la plataforma agregó, cotejado con su texto vigente: la Ley General
de Responsabilidades Administrativas (última reforma DOF 15-12-2025: arts. 3,
54, 57, 63, 71, 74, 78 y 79) y la Ley de Fiscalización y Rendición de Cuentas
de la Federación (última reforma DOF 14-05-2026: art. 38, el informe
semestral de cómo van las acciones).

El documento no trae ni una cifra de cuántas observaciones terminan en
sanción: queda pendiente (asf-sanciones-efectividad, pendientes.py).

asistente-charla.js lo lee como D.san; la página se arma con pagina()
(apartados.py, ficha «especial» de Informes oficiales).
"""

import html
import json
import os

from asistente_legislativo import _chip, bloque_tema

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVO = 'informes-documentar-para-sancionar.html'
TITULO = 'Informe especial: Documentar para sancionar'
DOC = {'tx': 'ASF, «Documentar para sancionar. De la irregularidad a la sanción», primera edición, julio de 2026',
       'url': 'https://www.asf.gob.mx/Trans/Informes/Ir2025a/Documentos/Informes_Especiales/Documentar.pdf',
       'sha256': 'd1d621c8dfc9dca6fa673a8c8f39818c92b374a6ca6331b30454da19c3072a9f'}
LGRA = {'tx': 'Ley General de Responsabilidades Administrativas, texto vigente (Cámara de Diputados, última reforma DOF 15-12-2025)',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGRA.pdf',
        'sha256': '1289ec6964e48c84990572ca6080ca05c9d6210e5b0ff5af6d8c9d935fc5fcc8'}
LFRCF = {'tx': 'Ley de Fiscalización y Rendición de Cuentas de la Federación, texto vigente (Cámara de Diputados, última reforma DOF 14-05-2026)',
         'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFRCF.pdf',
         'sha256': 'cc687a4d8d9de93d2d3ec9b40b26d0273e108bb002a6f611806dc36ebce5ba2c'}
PEND = 'asf-sanciones-efectividad'


def _p(pag):
    pag = str(pag)
    return dict(DOC, tx='%s, %s %s' % (DOC['tx'], 'pp.' if (' a ' in pag or ',' in pag or ' y ' in pag) else 'p.', pag))


def _o(que, fu, e='oficial', op=None):
    d = {'que': que, 'e': e, 'fu': fu}
    if op:
        d['op'] = op
    return d


def matrices():
    with open(os.path.join(RAIZ, 'docs', 'informes', 'documentar-para-sancionar.json'), encoding='utf-8') as f:
        m = json.load(f)['matrices']
    assert len(m) == 20, 'Documentar para sancionar trae 20 matrices'
    return m


# Las tres conductas de la LGRA a las que la ASF lleva sus 20 matrices.
CONDUCTAS = {
    'desvio': ('Desvío de recursos públicos', '54',
               'Autorizar, pedir o hacer que el dinero, los bienes o el personal público se usen sin fundamento en la ley o en contra de ella.'),
    'abuso': ('Abuso de funciones', '57',
              'Ejercer facultades que no se tienen, o usar las que sí se tienen, para actos u omisiones arbitrarios que benefician a alguien o perjudican al servicio público.'),
    'desacato': ('Desacato', '63',
                 'Dar información falsa a una autoridad fiscalizadora o de control, no contestarle o retrasar sin justificación la entrega, aun después de las medidas de apremio.'),
}

# Los cuatro elementos (p. 13) y los cinco requisitos de cada uno (pp. 14 a
# 16), transcritos de las láminas del documento.
ELEMENTOS = [
    ('personal', '👤', 'Personal', 'Quién fue', 'Identifica al servidor público, proveedor o contratista responsable de la conducta.',
     ['Que el nombre coincida con el del servidor público señalado como presunto responsable',
      'La fecha de expedición del nombramiento',
      'Que el periodo sea el de la fecha en que se cometió la conducta atribuida',
      'Que el cargo tenga relación con la normatividad infringida',
      'Que obre en copia fotostática certificada'], 14),
    ('conductual', '⚖️', 'Conductual', 'Qué regla violó', 'Acredita que la acción u omisión violó normas, procedimientos o contratos vigentes.',
     ['La norma: vigente al momento de los hechos, publicada en un medio oficial (o con sus aprobaciones), con el artículo que describe la conducta, '
      'ligada a las atribuciones del cargo y con su jerarquía y fundamentación completas',
      'El contrato: nombres, cargos y firmas completos y legibles que vinculen a servidores públicos, proveedores o contratistas',
      'El contrato vigente al momento de los hechos, con cláusulas que describan la conducta o la omisión',
      'Los convenios modificatorios, formalizados antes de que venciera el contrato',
      'Que obre en copia fotostática certificada'], 15),
    ('circunstancial', '🧾', 'Circunstancial', 'Cuándo, dónde y cómo', 'Reconstruye el tiempo, el lugar y el modo de los hechos: el hecho exacto que es la irregularidad.',
     ['La documentación contable debidamente requisitada (quién elaboró, revisó y autorizó)',
      'El CFDI en estatus «Vigente» en el portal del SAT',
      'Que coincidan las cuentas y el origen del recurso',
      'Que la factura desglose conceptos, precios unitarios y cantidades',
      'Que obre en copia fotostática certificada'], 16),
    ('finalidad', '💲', 'Finalidad', 'A dónde fue el dinero', 'Demuestra el destino efectivo de los recursos y cuantifica la afectación que justifica la sanción.',
     ['Que la cuenta sea del ente fiscalizado, fondo o programa auditado',
      'Datos principales y campos de control legibles, visibles y congruentes',
      'Que la fecha de salida del recurso coincida con la conducta atribuida',
      'La plena identificación del monto atribuido en las salidas del recurso',
      'Que obre en copia fotostática certificada'], 16),
]
EL_NOMBRE = {'personal': 'Personal (servidor público)', 'personal_moral': 'Personal (empresa o persona física)',
             'conductual': 'Conductual', 'circunstancial': 'Circunstancial', 'finalidad': 'Finalidad'}

# La cadena (caps. 2.4 y 6): quién hace qué, de la auditoría a la sanción.
CADENA = [
    ('🔎', 'Fiscalizadora', 'Detecta y documenta la irregularidad. Si el ente no la solventa, arma el expediente técnico.', 'pp. 6, 12 y 63'),
    ('🗂️', 'Seguimiento', 'Revisa lo que contestó el ente y dictamina qué observaciones no se solventaron.', 'pp. 64 y 65'),
    ('🕵️', 'Investigadora', 'Analiza los hechos y, si hay mérito, redacta el Informe de Presunta Responsabilidad Administrativa.', 'pp. 65 y 66'),
    ('📋', 'Substanciadora', 'Admite el informe, emplaza al presunto responsable y en la audiencia inicial recibe sus pruebas.', 'p. 66'),
    ('⚖️', 'Resolutora', 'Admite pruebas, oye alegatos y resuelve: sanciona o declara que no hay responsabilidad.', 'p. 67'),
]

# Cómo se dice en la calle cada tipo de irregularidad. `re` es la expresión
# con que asistente-charla.js lo reconoce (texto sin acentos, minúsculas).
FAMILIAS = {
    'comprobacion': ('No comprobaron en qué se gastó', 'no (comprobaron|comprueban|justificaron) (en que|el destino|a donde|donde)|sin comprobar (el destino|en que)'),
    'sin_factura': ('Pagos sin factura o con facturas que no cumplen', 'sin factura|sin facturas|facturas? (falsas?|apocrifas?|cancelad|no valid)|sin (comprobantes?|cfdi)|no (tienen|hay|presentaron) (facturas?|comprobantes?)'),
    'pagos_exceso': ('Pagos de más o que no procedían', 'pag(aron|o|os|ar) (de mas|en exceso|indebid|improcedente)|sobreprecio|sobrecosto|aviadores?|pagos? (a|de) (personal|gente) que no (trabaja|existe)'),
    'sin_autorizacion': ('Gastos sin autorización ni justificación', '(gasto|gastos|pago|pagos|gastaron|pagaron) sin (autorizacion|justificacion|justificar|autorizar)'),
    'adquisiciones': ('Compras que no siguieron la ley', 'no (licitaron|hubo licitacion)|adjudicacion directa|compras? sin (licitar|licitacion)|licitacion (amañada|amanada|a modo)'),
    'rezago': ('Obras que no beneficiaron a quien vive en pobreza', 'no (beneficio|beneficiaron|llego) a (los )?(pobres|quien|la gente|la poblacion)|pobreza extrema|rezago social|\\bfais\\b'),
    'clausulas': ('El contratista no cumplió el contrato', '(no cumplio|incumplio|incumplieron) (el|los|con el) contrato|clausulas? del contrato'),
    'penas': ('No le cobraron la pena al contratista', 'no (le |les )?(cobr|aplic)\\w* (la |las |el |los )?(penas?|multas?|sanciones?)|penas? convencional'),
    'sin_operar': ('Obras terminadas que no funcionan', 'obras? ((terminad|concluid|nuev)\\w* )?(que )?no (opera|funciona|sirve|se usa|abrio)|elefante blanco|(hospital|clinica|planta|escuela) (sin operar|que no (opera|funciona|abre))|no (opera|funciona) la obra'),
    'otros_transferidos': ('Dinero federal que estados y municipios usaron sin seguir sus reglas', '(estado|municipio|alcaldia)s? (uso|usaron|gasto|gastaron) (mal )?(el dinero|los recursos|el ramo 33) (federal|del fondo)'),
    'reintegro': ('No regresaron el dinero que sobró, o lo regresaron tarde', 'no (reintegraron|regresaron|devolvieron)|reintegr\\w* (tarde|extemporane)|(devolver|regresar) (el dinero )?a la tesofe'),
}


def _lista(items):
    return '<ul class="pa-lista">%s</ul>' % ''.join('<li>%s</li>' % x for x in items)


def _fam_html(k, ms, n_max=None):
    nom = FAMILIAS[k][0]
    filas = []
    for m in ms:
        c = CONDUCTAS[m['conducta']]
        filas.append('<li><b>%s.</b> Conducta: <b>%s</b> (art. %s de la LGRA%s). Ejemplo de acción de la ASF: «%s» <small>(p. %d)</small></li>' % (
            html.escape(m['rubro']), c[0], c[1], ', en relación con el art. 71' if m['con_71'] else '', html.escape(m['accion']), m['pag']))
    m = ms[0]
    docs = []
    for el in ('personal', 'personal_moral', 'conductual', 'circunstancial', 'finalidad'):
        v = m['el'].get(el)
        if not v:
            continue
        if el == 'conductual':
            v = ['%s: %s' % (g['h'], '; '.join(g['docs'])) for g in v]
        docs.append('<li><b>%s:</b> %s</li>' % (EL_NOMBRE[el], html.escape(' · '.join(v[:n_max] if n_max else v))))
    return ('<p>Para la ASF, «%s» cabe en este tipo de irregularidad. Así lo trata su guía <b>Documentar para sancionar</b>:</p><ul class="pa-lista">%s</ul>'
            '<p><b>Qué documentos lo prueban</b> (matriz de %s, p. %d):</p><ul class="pa-lista">%s</ul>'
            '<p>Si falta alguno de los cuatro elementos, el caso se puede caer ante el tribunal aunque la irregularidad sea cierta.</p>') % (
        html.escape(nom.lower()), ''.join(filas), html.escape(m['rubro']), m['pag'], ''.join(docs))


def temas():
    """Los temas del bot y de la página, con el mismo texto."""
    M = matrices()
    cuenta = {k: sum(1 for m in M if m['conducta'] == k) for k in CONDUCTAS}
    rubros = sorted({m['rubro'] for m in M})
    OP_CUENTA = 'conteo de las matrices del capítulo 4 (pp. 17 a 62)'
    t = {}
    t['informe'] = {
        'tit': 'Documentar para sancionar: la guía de la ASF para que una irregularidad llegue a sanción',
        'h': '<p>Es un <b>informe especial</b> de la Auditoría Superior de la Federación (primera edición, julio de 2026), publicado entre los informes especiales de la primera entrega de la Cuenta Pública 2025. '
             'Parte de una idea: <b>detectar una irregularidad no es el final, es el principio</b>. Para que alguien termine sancionado, el expediente debe probar, desde el '
             'primer día de la auditoría, <b>quién</b> lo hizo, <b>qué regla</b> violó, <b>cuándo y cómo</b> pasó, y <b>a dónde fue el dinero</b>.</p>'
             '<p>Trae <b>20 matrices</b>, una por tipo de irregularidad, sacadas de lo que la ASF observó en las Cuentas Públicas 2023 y 2024. Cada una dice qué conducta de la ley es '
             'y qué documentos la prueban. La ASF aclara que son <b>orientadoras, no obligatorias</b>: sirven también a los órganos internos de control y a los fiscalizadores de '
             'los estados.</p>',
        'ci': [{'v': '20', 'etq': 'matrices de irregularidades', 'e': 'derivado', 'op': OP_CUENTA},
               {'v': str(len(rubros)), 'etq': 'rubros del gasto', 'e': 'derivado', 'op': OP_CUENTA},
               {'v': '4', 'etq': 'elementos que debe probar un expediente', 'e': 'oficial'}],
        'fu': [_o('Propósito, alcance y carácter orientador (cap. 1)', _p('2 a 4')),
               _o('Matrices elaboradas con las observaciones de las Cuentas Públicas 2023 y 2024; no son vinculantes', _p(17)),
               _o('Cuántas matrices hay y en qué rubros', _p('18 a 62'), 'derivado', OP_CUENTA)],
        'sug': ['¿Qué tiene que probar la ASF para que sancionen a alguien?', '¿Qué pasa después de que la ASF observa algo?', '¿Por qué casi nadie termina sancionado?']}
    t['cadena'] = {
        'tit': 'De la auditoría a la sanción, paso a paso',
        'h': '<p>Una observación de la ASF <b>no es una sanción</b>. Si el ente auditado no la aclara (no la «solventa»), empieza una cadena con cinco eslabones, cada uno con su '
             'autoridad:</p><ol class="pa-lista">%s</ol>'
             '<p>Las faltas <b>graves</b> (como el desvío de recursos o el abuso de funciones) y las de particulares las resuelve un <b>tribunal</b> (en lo federal, el Tribunal '
             'Federal de Justicia Administrativa); las <b>no graves</b>, el órgano interno de control. Para las graves hay <b>siete años</b> para sancionar, y para las no graves, '
             '<b>tres</b>. Y el procedimiento <b>no puede quedarse quieto más de seis meses</b> sin causa: si pasa, el acusado puede pedir que se cierre (caducidad).</p>' % ''.join(
                 '<li><b>%s:</b> %s</li>' % (c[1], c[2]) for c in CADENA),
        'ci': [{'v': '7 años', 'etq': 'para sancionar una falta grave', 'e': 'oficial'},
               {'v': '3 años', 'etq': 'para sancionar una no grave', 'e': 'oficial'},
               {'v': '6 meses', 'etq': 'máximo sin actuar en el procedimiento', 'e': 'oficial'}],
        'fu': [_o('Las autoridades de la cadena y lo que hace cada una (caps. 2.4 y 6)', _p('6, 7 y 65 a 67')),
               _o('Autoridades investigadora, substanciadora y resolutora (art. 3, frs. II a IV)', LGRA),
               _o('Prescripción de 3 y 7 años y caducidad a los seis meses sin actuar (art. 74)', LGRA)],
        'sug': ['¿Qué sanciones le pueden dar a un funcionario?', '¿Qué tiene que probar la ASF para que sancionen a alguien?']}
    t['elementos'] = {
        'tit': 'Los cuatro elementos que debe probar un expediente',
        'h': '<p>Para la ASF, un expediente no vale por cuántos papeles tiene, sino por probar <b>cuatro cosas</b> sin lugar a duda:</p><ul class="pa-lista">%s</ul>'
             '<p>Y casi todo documento debe estar en <b>copia certificada</b>. Si un elemento falta, por ejemplo, el nombramiento no cubre la fecha de los hechos, el caso se puede caer '
             'aunque la irregularidad sea cierta.</p>' % ''.join(
                 '<li>%s <b>%s, %s.</b> %s</li>' % (e[1], e[2], e[3].lower(), e[4]) for e in ELEMENTOS),
        'fu': [_o('Los cuatro elementos (3.4.1) y sus requisitos mínimos (3.4.3)', _p('13 a 16')),
               _o('Qué debe permitir un expediente suficiente (2.3) y criterios de suficiencia documental (5.1)', _p('6 y 63'))],
        'sug': ['¿Qué documentos prueban una obra que no funciona?', '¿Qué es el desvío de recursos?']}
    t['conductas'] = {
        'tit': 'Las tres faltas graves a las que la ASF lleva sus casos',
        'h': '<p>Las 20 matrices caben en tres faltas administrativas <b>graves</b> de la Ley General de Responsabilidades Administrativas:</p><ul class="pa-lista">%s</ul>'
             '<p>Cuando quien recibió el dinero es una <b>empresa o un particular</b>, la ASF suma el <b>artículo 71</b>: el uso indebido de recursos públicos por un particular.</p>' % ''.join(
                 '<li><b>%s (art. %s):</b> %s <small>%d de las 20 matrices.</small></li>' % (c[0], c[1], c[2], cuenta[k]) for k, c in CONDUCTAS.items()),
        'ci': [{'v': str(cuenta[k]), 'etq': CONDUCTAS[k][0].lower(), 'e': 'derivado', 'op': OP_CUENTA} for k in CONDUCTAS],
        'fu': [_o('Desvío de recursos (art. 54), abuso de funciones (art. 57), desacato (art. 63) y uso indebido por particulares (art. 71)', LGRA),
               _o('Tipo de conducta de cada matriz', _p('18 a 62'), 'derivado', OP_CUENTA)],
        'sug': ['¿Qué sanciones le pueden dar a un funcionario?', '¿Qué tipos de irregularidad detecta la ASF?']}
    t['sanciones'] = {
        'tit': 'Qué sanciones puede imponer el tribunal por una falta grave',
        'h': '<p>Si el tribunal encuentra responsable a un servidor público de una falta grave, puede imponerle, solas o juntas:</p><ul class="pa-lista">'
             '<li><b>Suspensión</b> del cargo, de 30 a 90 días.</li><li><b>Destitución.</b></li>'
             '<li><b>Sanción económica:</b> si se benefició, hasta <b>dos veces</b> lo que obtuvo, y nunca menos de eso. Además debe <b>reparar todo el daño</b> al erario.</li>'
             '<li><b>Inhabilitación</b> para trabajar en el gobierno y para venderle o construirle: de 1 a 10 años si el daño no pasa de 200 veces la UMA diaria, y de <b>10 a 20 años</b> '
             'si pasa. Sin daño ni beneficio, de 3 meses a 1 año.</li></ul>'
             '<p>Es una sanción <b>administrativa</b>: si además hay delito, la denuncia penal va por su lado.</p>',
        'ci': [{'v': '20 años', 'etq': 'máximo de inhabilitación', 'e': 'oficial'},
               {'v': '2 tantos', 'etq': 'del beneficio, como sanción económica máxima', 'e': 'oficial'}],
        'fu': [_o('Suspensión, destitución, sanción económica e inhabilitación por faltas graves (art. 78)', LGRA),
               _o('Sanción económica de hasta dos tantos del beneficio e indemnización del daño (art. 79)', LGRA)],
        'sug': ['¿Qué pasa después de que la ASF observa algo?', '¿Por qué casi nadie termina sancionado?']}
    t['diagnostico'] = {
        'tit': 'Por qué tantas irregularidades no terminan en sanción, según la propia ASF',
        'h': '<p>La ASF escribió esta guía porque reconoce <b>cuatro problemas</b> entre lo que detecta y lo que se sanciona:</p><ul class="pa-lista">'
             '<li><b>Capacitación:</b> el personal auditor necesita conocer, desde la planeación, lo que exige un juicio de responsabilidades, no solo la técnica de auditoría.</li>'
             '<li><b>Tiempo:</b> sin criterios claros, los equipos juntan papeles que luego no sirven para el procedimiento.</li>'
             '<li><b>Expedientes débiles:</b> no prueban con precisión el tiempo, el lugar, el modo, el monto y a la persona responsable.</li>'
             '<li><b>Coordinación:</b> la cadena pasa por varias autoridades, y si cada una no sabe lo que necesita la siguiente, la prueba se pierde en el camino.</li></ul>'
             '<p><b>Lo que la guía no dice:</b> cuántas observaciones terminan, de verdad, en sanción firme. Ese dato existe: por ley, la ASF informa cada semestre (al 1 de mayo y al '
             '1 de noviembre) cómo van los procedimientos de responsabilidad que promovió, y lo publica en datos abiertos. La plataforma aún no lo integra. %s</p>' % _chip('pendiente', PEND),
        'fu': [_o('Las cuatro áreas de oportunidad (cap. 2)', _p('5 a 7')),
               _o('Informe semestral del estado de la solventación, con los procedimientos de responsabilidad promovidos, en datos abiertos (art. 38)', LFRCF),
               _o('Cuántas observaciones terminan en sanción firme', {'tx': 'Registro de pendientes', 'url': ''}, 'pendiente')],
        'sug': ['¿Qué pasa después de que la ASF observa algo?', '¿Qué tiene que probar la ASF para que sancionen a alguien?']}
    t['diagnostico']['fu'][-1]['p'] = PEND
    por_rubro = {r: [m for m in M if m['rubro'] == r] for r in rubros}
    t['matrices'] = {
        'tit': 'Los tipos de irregularidad que detecta la ASF',
        'h': '<p>La guía ordena lo que la ASF observó en las Cuentas Públicas 2023 y 2024 en <b>%d tipos de irregularidad</b>, repartidos en 20 matrices:</p>%s'
             '<p>Cuéntame qué pasó, por ejemplo, «pagaron una obra que no funciona», y te digo qué tipo es, qué falta de la ley sería y qué documentos la prueban.</p>' % (
                 len(FAMILIAS), _lista(['%s <small>(%d)</small>' % (html.escape(FAMILIAS[k][0]), sum(1 for m in M if m['fam'] == k)) for k in FAMILIAS])),
        'fu': [_o('Las 20 matrices, por tipo de conducta irregular', _p('17 a 62'), 'derivado', 'agrupación de las matrices por su título')],
        'sug': ['¿Qué documentos prueban una obra que no funciona?', '¿Qué pasa si no le cobran la pena al contratista?']}
    for k, (nom, _re) in FAMILIAS.items():
        ms = [m for m in M if m['fam'] == k]
        t['fam_' + k] = {
            'tit': '%s: cómo lo documenta la ASF' % nom,
            'h': _fam_html(k, ms),
            'fu': [_o('Matriz «%s»' % ms[0]['tit'], _p(', '.join(str(m['pag']) for m in ms)))],
            'sug': ['¿Qué sanciones le pueden dar a un funcionario?', '¿Qué pasa después de que la ASF observa algo?']}
    for k, x in t.items():
        x['ir'] = [ARCHIVO + '#san-' + (k if not k.startswith('fam_') else 'matrices'), TITULO]
        x['aqui'] = x['ir']
    assert sum(1 for m in M if m['fam'] in FAMILIAS) == 20
    return t


def bot():
    """Lo que lee asistente-charla.js (D.san): los temas y cómo se dice cada
    tipo de irregularidad en la calle."""
    return {'t': temas(), 'fam': {k: v[1] for k, v in FAMILIAS.items()}, 'pag': [ARCHIVO, TITULO]}


def _cadena_html():
    return ('<section class="camino" aria-labelledby="sanCadTit"><h2 class="camino-tit" id="sanCadTit">De la irregularidad a la sanción, en cinco eslabones</h2>'
            '<p class="camino-txt">Cada eslabón es una autoridad distinta. Lo que no se documentó en el primero no se puede probar en el último.</p>'
            '<ol class="camino-pasos">%s</ol></section>') % ''.join(
        '<li class="camino-paso"><span class="camino-num" aria-hidden="true">%d</span><span class="camino-ico" aria-hidden="true">%s</span>'
        '<b class="camino-que">%s</b><span class="camino-det">%s</span><small class="camino-det">%s</small></li>' % (i, c[0], c[1], c[2], c[3])
        for i, c in enumerate(CADENA, 1))


def _elementos_tabla():
    filas = ''.join('<tr><th scope="row">%s %s<br><small>%s</small></th><td>%s</td></tr>' % (
        e[1], e[2], e[3], _lista([html.escape(r) for r in e[5]])) for e in ELEMENTOS)
    return ('<div class="leg-tabla-caja"><table class="leg-tabla san-tabla"><caption>Los requisitos mínimos de cada elemento %s</caption>'
            '<thead><tr><th scope="col">Elemento</th><th scope="col">Qué debe cumplir el documento</th></tr></thead><tbody>%s</tbody></table></div>') % (
        _chip('oficial'), filas)


def _matrices_html(M):
    out = []
    for r in sorted({m['rubro'] for m in M}):
        out.append('<h3 class="san-rubro">%s</h3>' % html.escape(r))
        for m in [x for x in M if x['rubro'] == r]:
            c = CONDUCTAS[m['conducta']]
            els = []
            for el in ('personal', 'personal_moral', 'conductual', 'circunstancial', 'finalidad'):
                v = m['el'].get(el)
                if not v:
                    continue
                if el == 'conductual':
                    v = ['<b>%s:</b> %s' % (html.escape(g['h']), '; '.join(html.escape(d) for d in g['docs'])) for g in v]
                else:
                    v = [html.escape(d) for d in v]
                els.append('<tr><th scope="row">%s</th><td>%s</td></tr>' % (EL_NOMBRE[el], _lista(v)))
            out.append(
                '<details class="bib-q" id="san-m%02d"><summary><span class="bib-q-ico" aria-hidden="true">📄</span><span>%s<br><small>%s · art. %s LGRA%s · p. %d</small></span></summary>'
                '<div class="leg-tema san-matriz"><p><b>Ejemplo de acción de la ASF:</b> «%s»</p>'
                '<div class="leg-tabla-caja"><table class="leg-tabla san-tabla"><caption>Documentación que acredita cada elemento %s</caption>'
                '<thead><tr><th scope="col">Elemento</th><th scope="col">Documentos</th></tr></thead><tbody>%s</tbody></table></div>'
                '<p class="pa-chico">Fuente: <a href="%s#page=%d" target="_blank" rel="noopener noreferrer">%s, p. %d ↗</a></p></div></details>' % (
                    m['n'], html.escape(m['tit']), c[0], c[1], ' y 71' if m['con_71'] else '', m['pag'], html.escape(m['accion']),
                    _chip('oficial'), ''.join(els), DOC['url'], m['pag'] + 2, html.escape(DOC['tx']), m['pag']))
    return ''.join(out)


SECCIONES = [('informe', 'Qué es este informe'), ('cadena', 'De la auditoría a la sanción'), ('elementos', 'Los cuatro elementos de la prueba'),
             ('conductas', 'Las tres faltas graves'), ('sanciones', 'Las sanciones'), ('matrices', 'Las 20 matrices, por rubro'),
             ('diagnostico', 'Lo que la ASF reconoce que falla')]


def secciones():
    """Las secciones de la página: el mismo texto con que contesta el bot."""
    T = temas()
    M = matrices()
    out = []
    for k, tit in SECCIONES:
        x = T[k]
        extra = ''
        if k == 'cadena':
            extra = _cadena_html()
        elif k == 'elementos':
            extra = _elementos_tabla()
        elif k == 'matrices':
            extra = _matrices_html(M)
        out.append({'id': 'san-' + k, 'titulo': html.escape(tit), 'texto': '', 'tarjetas': [],
                    'bloque': bloque_tema(x, extra, ARCHIVO)})
    return out


ENTRADA = ('La guía con que la Auditoría Superior de la Federación quiere que cada irregularidad que detecta termine en sanción: la cadena de autoridades, '
           'los cuatro elementos que debe probar un expediente, las tres faltas graves y las 20 matrices de documentos por tipo de irregularidad. '
           'Explicada en sencillo, con la página de cada dato, y con lo que el documento no dice. Es la misma información con que contesta Pregúntale al Auditor.')
