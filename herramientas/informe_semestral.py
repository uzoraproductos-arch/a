# -*- coding: utf-8 -*-
"""El informe semestral de la ASF a la Cámara de Diputados («Informe sobre la
situación que guardan las observaciones, recomendaciones y acciones
promovidas», art. 38 de la LFRCF), en el formato con que conversa el bot y
en su página de Informes oficiales (pedido del autor, 27-10-2026: «integra el
informe semestral de la ASF»).

Cierra en parte el pendiente asf-sanciones-efectividad, que abrió
«Documentar para sancionar»: la guía no decía cuántas observaciones llegan a
sanción y este informe es donde la ley manda decirlo.

El documento: corte al 30 de septiembre de 2026, 628 páginas del PDF (la
página impresa es la del PDF menos 10). Integrado el 11-11-2026, cotejado
contra su PDF (huella en DOC): lo avisó el vigía de la revisión semanal del
09-11. Para el cambio en el semestre se usa el de corte al 31 de marzo de
2026, que fue el DOC anterior. El siguiente (corte al 31 de marzo de 2027)
debe entregarse a más tardar el 1 de mayo de 2027: lo espera semanal.py.

Lo que no trae, aunque el art. 38 lo pide: cuántos de los procedimientos que
la ASF mandó al Tribunal Federal de Justicia Administrativa terminaron en
sanción, ni la pena de las denuncias con sentencia. Eso sigue pendiente, y
ahora con nombre: lo debe la ASF.

asistente-charla.js lo lee dentro de D.san (claves sem_*); la página se arma
con secciones() (apartados.py, ficha «semestral» de Informes oficiales).
"""

import html

from asistente_legislativo import _chip, bloque_tema

ARCHIVO = 'informes-semestral-asf.html'
TITULO = 'Informe semestral de la ASF: qué pasó con lo que observó'
DOC = {'tx': 'ASF, «Informe sobre la situación que guardan las observaciones, recomendaciones y acciones promovidas», corte al 30 de septiembre de 2026',
       'url': 'https://www.asf.gob.mx/uploads/56_Informes_especiales_de_auditoria/IS_30_09_2026.pdf',
       'sha256': '23571df7c80b75d0c2a0e0ca67b1435ec4288cf54a233ac293d3c8f8e9995e90'}
ANT = {'tx': 'ASF, informe semestral con corte al 31 de marzo de 2026',
       'url': 'https://www.asf.gob.mx/uploads/56_Informes_especiales_de_auditoria/IS_31_03_2026.pdf',
       'sha256': '6b92cf8e5fb1f3baf82d2bc94ae8e8799a830e9511a1a09ac4f113ff393b0b37'}
LFRCF = {'tx': 'Ley de Fiscalización y Rendición de Cuentas de la Federación, texto vigente (Cámara de Diputados, última reforma DOF 15-05-2026)',
         'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFRCF.pdf'}
INDICE = 'https://www.asf.gob.mx/Section/59_Informes_especiales_de_auditoria'
PEND = 'asf-sanciones-efectividad'


def _p(pag, d=DOC):
    pag = str(pag)
    return dict(d, tx='%s, %s %s' % (d['tx'], 'pp.' if (' a ' in pag or ',' in pag or ' y ' in pag) else 'p.', pag))


def _o(que, fu, e='oficial', op=None):
    x = {'que': que, 'e': e, 'fu': fu}
    if op:
        x['op'] = op
    return x


# Estado procesal de las 1,225 denuncias de hechos (p. 35). La suma se
# comprueba abajo: si alguien cambia una cifra, la generación se detiene.
DENUNCIAS = [('En integración (el Ministerio Público aún investiga)', 601), ('No ejercicio de la acción penal (NEAP)', 455),
             ('Judicializada', 62), ('Sentencia', 32), ('Reserva', 21), ('Sobreseimiento', 18), ('Consignada', 11),
             ('Concluida por reparación del daño', 11), ('Sentencia impugnada', 5), ('Suspendida por solución alterna', 5),
             ('Concluida por competencia', 4)]
DH_TOTAL = 1225
assert sum(v for _, v in DENUNCIAS) == DH_TOTAL


def _pct(a, b):
    return '%.2f %%' % (a * 100.0 / b)


def temas():
    """Los temas del bot y de la página, con el mismo texto."""
    t = {}
    t['sem_informe'] = {
        'tit': 'El informe semestral de la ASF: cómo van las acciones que promovió',
        'h': '<p>Dos veces al año, la Auditoría Superior de la Federación le informa a la Cámara de Diputados <b>qué pasó con lo que observó</b>: si los entes aclararon, '
             'si devolvieron dinero y cómo van los procedimientos contra servidores públicos y las denuncias penales. Lo manda el <b>artículo 38</b> de la Ley de Fiscalización: '
             'se entrega a más tardar el <b>1 de mayo</b> (corte al 31 de marzo) y el <b>1 de noviembre</b> (corte al 30 de septiembre).</p>'
             '<p>El más reciente es el de <b>corte al 30 de septiembre de 2026</b>: 628 páginas. Entre la Cuenta Pública 2019 y la primera entrega de la 2025, la ASF hizo '
             '<b>11,843 auditorías</b> y emitió <b>37,424 acciones</b>; con las que salieron después, del seguimiento y de auditorías por mandato judicial o por denuncia, '
             'son <b>38,010</b>. El siguiente, con corte al 31 de marzo de 2027, debe entregarse a más tardar el 1 de mayo de 2027.</p>',
        'ci': [{'v': '11,843', 'etq': 'auditorías, Cuentas Públicas 2019 a la primera entrega de 2025', 'e': 'oficial'},
               {'v': '37,424', 'etq': 'acciones emitidas en esas auditorías', 'e': 'oficial'}],
        'fu': [_o('Informe semestral, fechas de entrega y lo que debe incluir (art. 38)', LFRCF),
               _o('Auditorías y acciones de las Cuentas Públicas 2019 a la primera entrega de 2025 (apartado I y resumen A.1)', _p('1 y 7'))],
        'sug': ['¿Cuántos funcionarios ha sancionado la ASF?', '¿Cuánto dinero ha recuperado la ASF?', '¿Cómo van las denuncias penales de la ASF?']}
    t['sem_acciones'] = {
        'tit': 'Qué pasó con las 37,424 acciones de la ASF (Cuentas Públicas 2019 a la primera entrega de 2025)',
        'h': '<p>Las acciones más fuertes son dos:</p><ul class="pa-lista">'
             '<li><b>Pliegos de observaciones (11,464):</b> cuando la ASF calcula un daño en pesos. <b>2,167</b> ya se cerraron (casi todos solventados), <b>3,520</b> siguen en '
             'revisión y <b>5,777</b> (el 50.4 %) no se aclararon y pasaron a las áreas de investigación de la propia ASF, que pueden convertirlos '
             'en un procedimiento de responsabilidad. En marzo de 2026 eran 5,392: en un semestre pasaron a investigación 385 más.</li>'
             '<li><b>Promociones de responsabilidad administrativa sancionatoria (11,071):</b> la ASF le pide al órgano interno de control del ente que investigue. '
             '<b>11,070</b> están «promovidas» (una se dio de baja antes de emitirse) y la ASF las da por concluidas desde ese momento: <b>el informe no dice qué hizo con ellas cada órgano interno de control</b>.</li></ul>'
             '<p>El resto son recomendaciones (8,051 y 4,550 al desempeño), solicitudes de aclaración (1,273) y promociones al SAT para revisar impuestos (1,015).</p>',
        'ci': [{'v': '11,464', 'etq': 'pliegos de observaciones', 'e': 'oficial'},
               {'v': '5,777', 'etq': 'pliegos no aclarados, en investigación de la ASF', 'e': 'oficial'},
               {'v': '11,071', 'etq': 'promociones a órganos internos de control', 'e': 'oficial'}],
        'fu': [_o('Acciones por tipo y Cuenta Pública (A.1)', _p(7)),
               _o('Promociones de responsabilidad administrativa sancionatoria: 11,070 promovidas y 1 baja previa a su emisión', _p(18)),
               _o('Pliegos de observaciones: 2,167 con seguimiento concluido, 5,777 en DGI y 3,520 en seguimiento', _p('22 y 23')),
               _o('Pliegos en DGI al 31 de marzo de 2026: 5,392', _p('23 y 24', ANT)),
               _o('Pliegos que pasaron a investigación en el semestre', _p(22), 'derivado', '5,777 (septiembre de 2026) − 5,392 (marzo de 2026) = 385')],
        'sug': ['¿Cuántos funcionarios ha sancionado la ASF?', '¿Qué pasa después de que la ASF observa algo?']}
    t['sem_procedimientos'] = {
        'tit': 'Cuántos casos llevó la ASF al tribunal, y lo que no dice de ellos',
        'h': '<p><b>Cuántos terminaron sancionados, el informe de la ASF no lo dice.</b> Lo que sí dice: cuando un pliego no se aclara y la investigación encuentra mérito, la ASF arma un Informe de Presunta Responsabilidad Administrativa y empieza un '
             'procedimiento bajo la Ley General de Responsabilidades Administrativas. Al 30 de septiembre de 2026 llevaba <b>2,576 procedimientos</b>, de las Cuentas Públicas 2016 a 2024: '
             '<b>2,494</b> ya están en el <b>Tribunal Federal de Justicia Administrativa</b>, que es quien sanciona las faltas graves, y <b>82</b> siguen en su área de substanciación.</p>'
             '<p>En un semestre crecieron en <b>181</b>: en marzo de 2026 eran 2,395.</p>'
             '<p><b>Lo que el informe no dice:</b> cuántos de esos 2,494 casos ya resolvió el tribunal, cuántos terminaron en <b>sanción</b> y cuántos en absolución. '
             'Todos aparecen solo como «Remitido al TFJA». El artículo 38 le pide a la ASF dar «las sanciones que al efecto hayan procedido». %s</p>' % _chip('pendiente', PEND),
        'ci': [{'v': '2,576', 'etq': 'procedimientos de responsabilidad iniciados', 'e': 'oficial'},
               {'v': '2,494', 'etq': 'enviados al tribunal', 'e': 'oficial'},
               {'v': '+181', 'etq': 'en el semestre', 'e': 'derivado', 'op': '2,576 (septiembre de 2026) − 2,395 (marzo de 2026) = 181'}],
        'fu': [_o('Procedimientos de responsabilidad administrativa: 2,494 remitidos al TFJA y 82 en la DGSUB (apartado III, D)', _p('62 a 161')),
               _o('Procedimientos al 31 de marzo de 2026: 2,395', _p(59, ANT)),
               _o('El informe debe identificar las sanciones que hayan procedido (art. 38)', LFRCF),
               _o('Cuántos procedimientos terminaron en sanción', {'tx': 'Registro de pendientes', 'url': ''}, 'pendiente')],
        'sug': ['¿Cómo van las denuncias penales de la ASF?', '¿Qué sanciones le pueden dar a un funcionario?']}
    t['sem_procedimientos']['fu'][-1]['p'] = PEND
    t['sem_denuncias'] = {
        'tit': 'Las denuncias penales de la ASF: 1,225 presentadas, 32 con sentencia',
        'h': '<p>Desde la Cuenta Pública 1998, la ASF ha presentado <b>1,225 denuncias de hechos</b> ante el Ministerio Público (1,140 de Cuentas Públicas y 85 por simular '
             'reintegros). Al 30 de septiembre de 2026 estaban así:</p>%s'
             '<p>Es decir, <b>32 tienen sentencia</b> (el 2.61 %%), y 5 más la tienen impugnada. Casi la mitad sigue <b>en integración</b>, algunas desde hace más de diez años, '
             'y más de un tercio terminó en <b>no ejercicio de la acción penal</b>: la fiscalía decidió no llevarlas ante un juez.</p>'
             '<p>En el semestre la ASF presentó <b>29 denuncias más</b>; las que tienen sentencia siguen siendo 32, las mismas que en marzo de 2026.</p>'
             '<p><b>Lo que el informe no dice:</b> si esas sentencias fueron condenatorias y qué pena se impuso, aunque el artículo 38 lo pide. Decidir si se acusa le toca '
             'solo al Ministerio Público, no a la ASF.</p>' % '',
        'ci': [{'v': '1,225', 'etq': 'denuncias penales presentadas', 'e': 'oficial'},
               {'v': '32', 'etq': 'con sentencia', 'e': 'oficial'},
               {'v': '2.61 %', 'etq': 'de las denuncias, con sentencia', 'e': 'derivado', 'op': '32 ÷ 1,225 × 100 = 2.61 %'}],
        'fu': [_o('Denuncias de hechos por Cuenta Pública y estado procesal (apartado III, C)', _p('34 y 35')),
               _o('Denuncias presentadas en el semestre: de 1,196 a 1,225, 29 más (apartado II)', _p(6)),
               _o('Denuncias al 31 de marzo de 2026: 1,196 (32 con sentencia)', _p(35, ANT)),
               _o('Proporción de cada estado procesal', _p(35), 'derivado', 'cada estado ÷ 1,225 × 100')],
        'sug': ['¿Cuántos funcionarios ha sancionado la ASF?', '¿Cuánto dinero ha recuperado la ASF?']}
    t['sem_resarcitorias'] = {
        'tit': 'Los fincamientos de responsabilidad resarcitoria (Cuentas Públicas 2001 a 2016)',
        'h': '<p>Con las Cuentas Públicas 2001 a 2016, la ASF misma podía obligar a pagar el daño: el <b>fincamiento de responsabilidad resarcitoria</b>. Lleva <b>4,787</b>: '
             '<b>3,717</b> con resolución notificada, <b>428</b> con resolución de primera instancia, <b>210</b> impugnadas, <b>413</b> sobreseídas, 16 en trámite y 3 dadas de baja '
             'por fallecimiento. Por esta vía se han recuperado <b>$3,084.6 millones</b>.</p>',
        'ci': [{'v': '4,787', 'etq': 'fincamientos resarcitorios', 'e': 'oficial'},
               {'v': '$3,084.6 millones', 'etq': 'recuperados por esta vía', 'e': 'oficial'}],
        'fu': [_o('Fincamientos de responsabilidades resarcitorias por estado de trámite (apartado III, B)', _p('29 a 31')),
               _o('Recuperaciones por fincamiento de responsabilidad resarcitoria', _p(538))],
        'sug': ['¿Cuánto dinero ha recuperado la ASF?', '¿Cómo van las denuncias penales de la ASF?']}
    t['sem_recuperaciones'] = {
        'tit': 'Cuánto dinero ha recuperado la ASF: $136,100.9 millones (Cuentas Públicas 2001 a 2024)',
        'h': '<p>Por sus auditorías, los entes han devuelto o aclarado con pago <b>$136,100.9 millones</b> en 24 Cuentas Públicas: $133,016.3 millones de la fiscalización y '
             '$3,084.6 millones de los fincamientos resarcitorios. En el semestre la cifra subió <b>$292.8 millones</b>.</p>'
             '<p>Casi dos terceras partes vienen de <b>estados y municipios</b> ($87,178.8 millones), con el Estado de México ($15,239.4 millones) y Veracruz ($15,154.4 millones) '
             'al frente. En lo federal, el sector Hacienda ($20,996.5 millones) y Pemex Exploración y Producción ($7,016.4 millones).</p>'
             '<p><b>Cómo leerla:</b> suma pesos de años distintos sin actualizarlos por inflación, así que no se puede comparar con un presupuesto de hoy. Y no incluye lo que está '
             'en juicio ni lo que reportan los fiscalizadores de los estados.</p>',
        'ci': [{'v': '$136,100.9 millones', 'etq': 'recuperados, 2001 a 2024', 'e': 'oficial'},
               {'v': '+$292.8 millones', 'etq': 'en el semestre', 'e': 'derivado', 'op': '$136,100.9 millones (septiembre de 2026) − $135,808.1 millones (marzo de 2026)'}],
        'fu': [_o('Recuperaciones por poder, sector y entidad, y lo que no incluyen (apartado VI)', _p('537 a 542')),
               _o('Recuperaciones al 31 de marzo de 2026: $135,808.1 millones', _p(560, ANT))],
        'sug': ['¿Cuántos funcionarios ha sancionado la ASF?', '¿Cómo van las denuncias penales de la ASF?']}
    t['sem_ciegos'] = {
        'tit': 'Lo que el informe semestral no dice, aunque la ley lo pide',
        'h': '<ul class="pa-lista">'
             '<li><b>Las sanciones.</b> De los 2,494 procedimientos en el Tribunal Federal de Justicia Administrativa no da ni uno resuelto: todos dicen «Remitido al TFJA». %s</li>'
             '<li><b>Lo que hicieron los órganos internos de control</b> con las 11,070 promociones que recibieron: para la ASF el asunto se cierra al promoverlo.</li>'
             '<li><b>La pena de las 32 sentencias penales</b>, ni si fueron condenatorias.</li>'
             '<li><b>Los datos abiertos.</b> El artículo 38 manda publicarlo en ese formato el mismo día. En la página de informes semestrales de la ASF solo está el PDF de 628 '
             'páginas; su consulta de auditorías (asfdatos.gob.mx) es un tablero, no un archivo que se pueda descargar.</li></ul>' % _chip('pendiente', PEND),
        'fu': [_o('Lo que debe incluir el informe y su publicación en datos abiertos (art. 38)', LFRCF),
               _o('Estado de los procedimientos: solo «Remitido al TFJA» o «Admitido por la DGSUB»', _p('62 a 161')),
               _o('Página de los informes semestrales: solo PDF', {'tx': 'ASF, Informes especiales de auditoría', 'url': INDICE}),
               _o('Cuántos procedimientos terminaron en sanción', {'tx': 'Registro de pendientes', 'url': ''}, 'pendiente')],
        'sug': ['¿Cuántos funcionarios ha sancionado la ASF?', '¿Por qué casi nadie termina sancionado?']}
    t['sem_ciegos']['fu'][-1]['p'] = PEND
    for k, x in t.items():
        x['ir'] = [ARCHIVO + '#' + k.replace('_', '-'), TITULO]
        x['aqui'] = x['ir']
    return t


def _barras_html():
    filas = ''.join(
        '<li class="sem-barra"><span class="sem-barra-que">%s</span><span class="sem-barra-pista" aria-hidden="true"><span class="sem-barra-relleno" style="width:%.1f%%"></span></span>'
        '<span class="sem-barra-num">%s <small>(%s)</small></span></li>' % (html.escape(n), v * 100.0 / DH_TOTAL, '{:,}'.format(v), _pct(v, DH_TOTAL))
        for n, v in DENUNCIAS)
    return ('<figure class="sem-grafica"><figcaption>Las 1,225 denuncias penales de la ASF, por estado procesal, al 30 de septiembre de 2026 %s %s</figcaption>'
            '<ul class="sem-barras">%s</ul><p class="pa-chico">Cada cifra es oficial (p. 35 del informe); el porcentaje es derivado: cada estado ÷ 1,225 × 100.</p></figure>') % (
        _chip('oficial'), _chip('derivado'), filas)


SECCIONES = [('sem_informe', 'Qué es este informe'), ('sem_acciones', 'Qué pasó con las acciones'),
             ('sem_procedimientos', 'Los casos en el tribunal'), ('sem_denuncias', 'Las denuncias penales'),
             ('sem_resarcitorias', 'Los fincamientos resarcitorios'), ('sem_recuperaciones', 'El dinero recuperado'),
             ('sem_ciegos', 'Lo que no dice')]


def secciones():
    """Las secciones de la página: el mismo texto con que contesta el bot."""
    T = temas()
    out = []
    for k, tit in SECCIONES:
        out.append({'id': k.replace('_', '-'), 'titulo': html.escape(tit), 'texto': '', 'tarjetas': [],
                    'bloque': bloque_tema(T[k], _barras_html() if k == 'sem_denuncias' else '', ARCHIVO)})
    return out


ENTRADA = ('Lo que la Auditoría Superior de la Federación le informa cada semestre a la Cámara de Diputados sobre lo que observó: cuántas acciones se aclararon, '
           'cuántos casos llegaron al tribunal, cómo van sus 1,225 denuncias penales y cuánto dinero se ha recuperado. Con el corte al 30 de septiembre de 2026, '
           'la página de cada dato y lo que el informe no dice aunque la ley lo pida. Es la misma información con que contesta Pregúntale al Auditor.')
