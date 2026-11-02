#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""«Cómo se audita»: la metodología de auditoría, en sencillo (pedido del
autor, 02-11-2026: «con su información integra nuestra base de datos como
metodología»).

El autor subió cuatro documentos de auditoría: dos temarios de diplomados
(control interno y auditoría forense), un folleto de IA para auditores y el
informe «Documentar para sancionar» de la ASF. **Los temarios solo sirvieron
de guía de temas**, como la Enciclopedia antigua (AGENTS.md §0 bis): cada
concepto se cotejó contra el documento oficial que lo sostiene, y eso es lo
que se cita:

- ASF, Marco Integrado de Control Interno para el Sector Público (Sistema
  Nacional de Fiscalización): definición, componentes, riesgo inherente
  y residual, factores de riesgo de fraude y segregación de funciones.
- Ley Federal para la Prevención e Identificación de Operaciones con Recursos
  de Procedencia Ilícita (última reforma DOF 16-07-2025), arts. 2, 6, 17 y 18.
- Código Nacional de Procedimientos Penales (última reforma DOF 28-11-2025),
  arts. 227, 228, 368 y 369.

Un documento de doctrina o una guía es metodología: se explica con su página
y no se copia entero (AGENTS.md §5 ter). Ninguna cifra fiscal vive aquí.

La página la arma pagina() (apartados.py, tarjeta de Aprende) y el chat la
lee dentro de D.san (claves met_*), con el mismo texto.
"""

import html

from asistente_legislativo import bloque_tema

ARCHIVO = 'aprende-auditoria.html'
TITULO = 'Cómo se audita'

MICI_URL = 'https://www.asf.gob.mx/uploads/176_Marco_Integrado_de_Control/Marco_Integrado_de_Cont_Int_leyen.pdf'
MICI_TX = 'ASF, Marco Integrado de Control Interno para el Sector Público (Sistema Nacional de Fiscalización)'
LFPIORPI = {'tx': 'Ley Federal para la Prevención e Identificación de Operaciones con Recursos de Procedencia Ilícita, texto vigente '
                  '(Cámara de Diputados, última reforma DOF 16-07-2025)',
            'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPIORPI.pdf'}
CNPP = {'tx': 'Código Nacional de Procedimientos Penales, texto vigente (Cámara de Diputados, última reforma DOF 28-11-2025)',
        'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CNPP.pdf'}
SAN_URL = 'informes-documentar-para-sancionar.html'


def _mici(pag):
    return {'tx': '%s, %s' % (MICI_TX, pag), 'url': MICI_URL}


def _o(que, fu, e='oficial'):
    return {'que': que, 'e': e, 'fu': fu}


def _lista(items):
    return '<ul class="pa-lista">%s</ul>' % ''.join('<li>%s</li>' % i for i in items)


COMPONENTES = [
    ('🧱', 'Ambiente de control', 'La base: disciplina y estructura para que el personal cumpla los objetivos.'),
    ('⚠️', 'Administración de riesgos', 'Identificar, analizar y priorizar lo que puede salir mal, incluida la corrupción, y decidir cómo responder.'),
    ('🔒', 'Actividades de control', 'Las políticas y los procedimientos que responden a esos riesgos.'),
    ('📣', 'Información y comunicación', 'Información de calidad que se genera, se usa y se comunica.'),
    ('🔁', 'Supervisión', 'Vigilar y evaluar el control para mejorarlo. La apoyan la auditoría interna y, desde fuera, las entidades fiscalizadoras.'),
]

FACTORES = [
    ('💸', 'Incentivo o presión', 'alguien tiene un motivo para cometer el acto.'),
    ('🚪', 'Oportunidad', 'faltan controles, no sirven, o alguien puede saltárselos por su puesto.'),
    ('🗣️', 'Actitud o racionalización', 'la persona se convence de que lo que hace se justifica.'),
]


def temas():
    """Los temas del bot y de la página, con el mismo texto."""
    t = {}
    t['met_control'] = {
        'tit': 'Qué es el control interno y cómo se revisa',
        'h': '<p>El <b>control interno</b> es el conjunto de reglas, revisiones y hábitos con que una institución se cuida a sí misma. La ASF lo define como un <b>proceso</b> '
             'que hacen el órgano de gobierno, el titular y todo el personal para dar una <b>seguridad razonable</b> de tres cosas: que se cumplan los objetivos, que se '
             'cuiden los recursos públicos y que se <b>prevenga la corrupción</b>.</p>'
             '<p>«Razonable» quiere decir alta confianza, pero no absoluta: ningún control garantiza que nada salga mal. El primer responsable es el <b>titular</b>, pero '
             'cada servidor público responde de los controles de su tarea. El Marco lo llama <b>la primera línea de defensa</b> de los recursos públicos.</p>'
             '<p>Los objetivos se agrupan en tres: <b>operación</b> (que se haga bien y sin desperdicio), <b>información</b> (que los informes sean confiables) y '
             '<b>cumplimiento</b> (que se respete la ley). El Marco se arma con <b>5 componentes y 17 principios</b>:</p>%s'
             '<p>Lo adoptó el Sistema Nacional de Fiscalización para los tres órdenes de gobierno y los tres Poderes, con base en el modelo COSO 2013 y las normas de '
             'control del gobierno de Estados Unidos (el «Libro Verde» de la GAO). Lo que en los diplomados se enseña como COSO, en el sector público mexicano se aplica con este Marco.</p>' % _lista(
                 ['%s <b>%s.</b> %s' % c for c in COMPONENTES]),
        'ci': [{'v': '5', 'etq': 'componentes del control interno', 'e': 'oficial'},
               {'v': '17', 'etq': 'principios que los sostienen', 'e': 'oficial'}],
        'fu': [_o('Definición de control interno, objetivos y primera línea de defensa (sección 1)', _mici('p. 8')),
               _o('Seguridad razonable (definiciones)', _mici('p. 7')),
               _o('Los 5 componentes y los 17 principios (sección 2)', _mici('pp. 10 y 11')),
               _o('Base en COSO 2013 y en el «Green Book» de la GAO (nota de la portada)', _mici('portada'))],
        'sug': ['¿Qué es el riesgo inherente?', '¿Qué es el triángulo del fraude?', '¿Qué tiene que probar la ASF para que sancionen a alguien?']}
    t['met_riesgos'] = {
        'tit': 'Auditar por riesgos: inherente, residual y tolerancia cero a la corrupción',
        'h': '<p>Un auditor no revisa todo por igual: empieza por <b>lo que más puede salir mal</b>. Para eso distingue dos riesgos:</p>%s'
             '<p>Si la institución no responde a ninguno de los dos, su control interno puede tener <b>deficiencias graves</b>.</p>'
             '<p>Con los riesgos de <b>corrupción y fraude</b> no hay margen: el Marco dice que <b>no les aplica la tolerancia al riesgo</b>. Para los objetivos de '
             'cumplimiento, la tolerancia es <b>cero</b>, porque un acto corrupto ya es, por sí mismo, una falla.</p>'
             '<p>Un control básico es la <b>segregación de funciones</b>: que la misma persona no autorice, guarde y registre. Dividir la autoridad, la custodia '
             'y la contabilidad ayuda a prevenir la corrupción, el fraude y el desperdicio.</p>'
             '<p>Así trabaja la plataforma: el <a href="descarga-los-datos.html#radar">radar</a> ordena a los estados por lo que dejaron por aclarar ante la ASF, para '
             'mirar primero donde hay más riesgo. Una bandera roja no es una acusación: es una señal para revisar primero.</p>' % _lista([
                 '<b>Riesgo inherente:</b> el que enfrenta la institución si no hace nada para responderle.',
                 '<b>Riesgo residual:</b> el que queda después de que responde con sus controles.']),
        'fu': [_o('Riesgo inherente y riesgo residual (numeral 7.03)', _mici('p. 32')),
               _o('Sin tolerancia al riesgo de corrupción; tolerancia cero en cumplimiento (principio 8)', _mici('p. 35')),
               _o('Segregación de funciones (principio 3)', _mici('p. 26'))],
        'sug': ['¿Qué es el triángulo del fraude?', '¿Qué es el control interno?', '¿Qué es una bandera roja?']}
    t['met_fraude'] = {
        'tit': 'Los tres factores del fraude (el «triángulo del fraude»)',
        'h': '<p>En los cursos de auditoría se le llama <b>triángulo del fraude</b>. El Marco de la ASF lo pide como parte del principio 8: la administración debe considerar '
             'tres <b>factores de riesgo</b> de corrupción y fraude:</p>%s'
             '<p>Dos advertencias del propio Marco: los factores <b>no prueban</b> que haya un acto corrupto, solo suelen estar presentes cuando ocurre. Y el riesgo es '
             'mayor cuando están los tres, pero puede haber corrupción con uno solo.</p>'
             '<p>De los tres, la <b>oportunidad</b> es la que un control puede cerrar. Por eso la plataforma busca dónde faltan documentos, '
             'y no adivina motivos: <b>una acusación no es una condena</b>.</p>' % _lista(
                 ['%s <b>%s:</b> %s' % f for f in FACTORES]),
        'ci': [{'v': '3', 'etq': 'factores de riesgo de fraude', 'e': 'oficial'}],
        'fu': [_o('Factores de riesgo: incentivos/presiones, oportunidad y actitud/racionalización (numerales 8.04 y 8.05)', _mici('p. 34'))],
        'sug': ['¿Qué es el riesgo inherente?', '¿Qué es la cadena de custodia?', '¿Qué tipos de irregularidad detecta la ASF?']}
    t['met_forense'] = {
        'tit': 'Auditoría forense: que la prueba aguante un juicio',
        'h': '<p>La <a href="glosario.html#Auditoria-Forense">auditoría forense</a> no se queda en el hallazgo: lo documenta para que <b>sirva ante una autoridad</b>. '
             'Encontrar el desvío es una cosa; probarlo es otra. La ley pide tres cosas:</p>%s'
             '<p>En lo administrativo, la ASF pide que el expediente pruebe <b>cuatro elementos</b>: quién, qué regla violó, cuándo y cómo, y a dónde fue el dinero. '
             'Están en <a href="%s#san-elementos">«Documentar para sancionar»</a>.</p>' % (_lista([
                 '<b>Cadena de custodia.</b> Es el sistema de control y registro de cada evidencia, desde que se encuentra hasta que la autoridad ordena cerrarla: '
                 'su identidad, su estado original, cómo se recolectó, se guardó y se trasladó, dónde y cuándo estuvo, y el nombre de cada persona que la tocó.',
                 '<b>Evidencia alterada.</b> Si cambia durante la custodia, no pierde por eso su valor. Lo pierde solo si la autoridad comprueba que ya no sirve '
                 'para acreditar el hecho.',
                 '<b>Prueba pericial.</b> Se ofrece cuando hace falta un conocimiento especial, como la contabilidad. El perito debe tener <b>título oficial</b> en la '
                 'materia, si esa profesión está reglamentada.']), SAN_URL),
        'fu': [_o('Cadena de custodia y sus factores (art. 227)', CNPP),
               _o('Responsables de la cadena; la evidencia alterada no pierde por eso su valor (art. 228)', CNPP),
               _o('Prueba pericial y título oficial del perito (arts. 368 y 369)', CNPP),
               _o('Los cuatro elementos que debe probar un expediente (3.4.1)',
                  {'tx': 'ASF, «Documentar para sancionar», julio de 2026, pp. 13 a 16',
                   'url': 'https://www.asf.gob.mx/Trans/Informes/Ir2025a/Documentos/Informes_Especiales/Documentar.pdf'})],
        'sug': ['¿Qué tiene que probar la ASF para que sancionen a alguien?', '¿Qué es una actividad vulnerable?', '¿Qué es el triángulo del fraude?']}
    t['met_lavado'] = {
        'tit': 'Lavado de dinero: actividades vulnerables y avisos a Hacienda',
        'h': '<p>La ley antilavado protege al sistema financiero con un método: <b>prevenir y detectar</b> operaciones con dinero de origen ilícito, y juntar '
             'datos útiles para investigarlas. No acusa a nadie: obliga a ciertos negocios a <b>identificar y avisar</b>.</p>'
             '<p>Esos negocios hacen <b>actividades vulnerables</b>. La ley enumera 16 fracciones, entre ellas:</p>%s'
             '<p>Para cada una hay un monto, medido en veces la UMA diaria, a partir del cual hay que identificar al cliente, y otro más alto a partir del cual hay '
             'que presentar un <b>aviso a Hacienda</b>. Quien hace una actividad vulnerable debe:</p>%s'
             '<p><b>Un aviso no es una acusación:</b> es un reporte obligatorio. Por eso la plataforma no trata una operación grande como prueba de lavado.</p>' % (
                 _lista(['Juegos con apuesta, concursos y sorteos.',
                         'Construcción, desarrollo y compraventa de inmuebles.',
                         'Venta de metales y piedras preciosas, joyas y relojes; obras de arte; vehículos y blindaje.',
                         'Servicios profesionales independientes y fe pública (notarios y corredores).',
                         'Recibir <b>donativos</b>, en las asociaciones sin fines de lucro, desde 1,605 veces la UMA diaria; el aviso, desde 3,210 veces.',
                         'Intercambio de activos virtuales.']),
                 _lista(['<b>Identificar y conocer</b> al cliente, con documento oficial.',
                         'Si es una empresa o un fideicomiso, identificar a su <b>beneficiario controlador</b>: quien de verdad lo controla.',
                         '<b>Guardar y proteger</b> los documentos que permitan reconstruir cada operación.'])),
        'ci': [{'v': '16', 'etq': 'fracciones de actividades vulnerables', 'e': 'oficial'}],
        'fu': [_o('Objeto: prevenir y detectar operaciones con recursos de procedencia ilícita (art. 2)', LFPIORPI),
               _o('Hacienda recibe los avisos (arts. 3, fr. XIII, y 6, fr. I)', LFPIORPI),
               _o('Las actividades vulnerables y sus umbrales, incluidos los donativos (art. 17, frs. I a XVI)', LFPIORPI),
               _o('Identificar al cliente y al beneficiario controlador, y custodiar la documentación (art. 18, frs. I a IV)', LFPIORPI)],
        'sug': ['¿Qué es la cadena de custodia?', '¿Qué empresas fantasma tiene el SAT?', '¿Qué es el triángulo del fraude?']}
    t['met_ruta'] = {
        'tit': 'Cómo audita Auditavisión: el método, paso a paso',
        'h': '<p>Cada concepto de esta página tiene su herramienta en la plataforma:</p>%s'
             '<p>Y una regla por encima de todas: <b>un dato inventado desacredita la plataforma entera</b>. Lo que no se puede verificar se queda '
             '<a href="pendientes.html">pendiente</a>, con el nombre de quien lo debe.</p>' % _lista([
                 '⚠️ <b>Riesgo:</b> el <a href="descarga-los-datos.html#radar">radar</a> dice dónde mirar primero.',
                 '🔒 <b>Control:</b> los <a href="informes-cuenta-publica.html">informes de la ASF</a> dicen qué quedó por aclarar en cada estado.',
                 '🚪 <b>Oportunidad:</b> los <a href="expedientes.html">expedientes</a> siguen los casos donde faltan documentos.',
                 '🧾 <b>Evidencia:</b> <a href="%s">Documentar para sancionar</a> dice qué documentos prueba cada irregularidad.' % SAN_URL,
                 '🏢 <b>Empresas:</b> la <a href="contratos-publicos.html">lista 69-B del SAT y los contratos de ComprasMX</a> se cruzan solos.',
                 '📜 <b>Dictamen:</b> el <a href="herramienta-inspector-dictamen.html">dictamen cívico</a> sella lo encontrado, con cada fuente. No es un peritaje con validez ante autoridad.']),
        'fu': [],
        'sug': ['¿Qué es el control interno?', '¿Qué tiene que probar la ASF para que sancionen a alguien?', '¿Qué empresas fantasma tiene el SAT?']}
    for k, x in t.items():
        x['ir'] = [ARCHIVO + '#' + k.replace('_', '-'), TITULO]
        x['aqui'] = x['ir']
    return t


SECCIONES = [('met_control', 'El control interno'), ('met_riesgos', 'Auditar por riesgos'), ('met_fraude', 'Los tres factores del fraude'),
             ('met_forense', 'Auditoría forense y prueba'), ('met_lavado', 'Lavado de dinero'), ('met_ruta', 'Cómo audita Auditavisión')]


def secciones():
    T = temas()
    return [{'id': k.replace('_', '-'), 'titulo': html.escape(tit), 'texto': '', 'tarjetas': [],
             'bloque': bloque_tema(T[k], '', ARCHIVO)} for k, tit in SECCIONES]


ENTRADA = ('Lo que se enseña en un diplomado de auditoría, explicado en sencillo y cotejado contra el documento oficial que lo sostiene: '
           'el control interno, auditar por riesgos, los tres factores del fraude, la prueba que aguanta un juicio y la ley antilavado. '
           'Cada concepto lleva a la herramienta de la plataforma que lo aplica. Es la misma información con que contesta Pregúntale al Auditor.')


def pagina():
    """El diccionario de la página para apartados.py (tarjeta de Aprende)."""
    return {
        'archivo': ARCHIVO, 'menu': TITULO, 'menu_archivo': 'aprende.html',
        'padre': ('aprende.html', 'Aprende'),
        'icono': '🧭', 'titulo': TITULO, 'lema': 'La metodología del auditor, con su fuente oficial',
        'estilos': ['asistente.css'], 'entrada': ENTRADA, 'secciones': secciones(),
    }
