#!/usr/bin/env python3
"""«Al momento»: notas breves de Noticias relevantes (pedido del autor,
28-10-2026: «notas más pequeñas, donde el usuario pueda tener conocimiento de
lo que está pasando, fechado con nuestros datos, verificado, nuestra salud
financiera, estado de resultados… y si un concepto no está bien claro,
describírselo a través de nuestro glosario»).

Uso:
    python3 herramientas/integrar_al_momento.py

Escribe (o reescribe) cada nota de NOTAS en el arreglo COLUMNAS de
assets/auditor/js/columnas.js, al principio, con la sección «Al momento».
Es idempotente: una nota que ya está se reemplaza, no se duplica. Conserva
los CRLF del archivo.

Una nota breve es una columna con el mismo cotejo de Verificamos (la nota de
prensa es lo que se coteja, nunca la fuente) y cuatro campos más:
    fecha     día de la noticia (DD-MM-AAAA), para ordenar «Al momento».
    nota      {medio, titulo, fecha, url, firma?}: la nota que la originó.
    ejemplo   {tit, txt, filas[[etq, valor, operacion]], nota}: la cuenta
              con números redondos, siempre como derivado.
    datos     [{ico, tx, url, de}]: lo que dice la plataforma (estado de
              resultados, salud financiera, herramientas).
    glosario  [{t, url}]: los conceptos, con su ficha del glosario.
    red       la búsqueda que se arma en buscadores y redes, sin verificar.

Nota 1 · La Modalidad 40 del IMSS (28-10-2026). Documentos cotejados:
- DOF 21-10-2026, Acuerdo ACDO.AS2.HCT.101026/302.P.DG del H. Consejo
  Técnico del IMSS (sesión extraordinaria del 10-10-2026), texto íntegro
  leído en SIDOF (nota 5801708). Rige desde el día hábil siguiente a su
  publicación: el jueves 22-10-2026.
- Ley del Seguro Social, texto vigente, última reforma DOF 15-01-2026
  (Cámara de Diputados): arts. 28 y 218 y transitorio duodécimo.
- PEF 2026, Anexo 1, pp. 33-34: Ramo 19 (ya en la base, anexo1PEF2026).
- INEGI, UMA 2026 (DOF 09-01-2026): $117.31 diarios, $3,566.22 al mes.
- IMSS, Memoria Estadística 2025, cuadro XIII.45 (ya en gestion_salud.py,
  misma huella SHA-256).
La nota de La Jornada (28-10-2026) es el punto de partida: su sitio no
respondió desde el servidor de la sesión, así que su firma queda por
confirmar y se cita al medio.

Nota 2 · El Senado aprueba la Ley de Ingresos 2027 (29-10-2026). Pieza que
pasó el autor: publicación de @elfinanciero_mx en Instagram (28-10-2026).
Documentos cotejados:
- Canal del Congreso, noticia 10338 (28-10-2026): el Senado aprueba la LIF
  2027, 75 a 34 en lo general y 73 a 33 en lo particular, «en sus términos»
  y enviada al Ejecutivo; 10,636,488.1 mdp, 6,263,886.8 de impuestos, techo
  de deuda interna de 1.7 billones, ISR, IVA e IEPS.
- Canal del Congreso, noticia 10318 (14-10-2026): Diputados aprueba la Ley
  Federal de Derechos 2027 (329 a 117; 339 a 113 en lo particular); la cuota
  de visitantes extranjeros sin actividad remunerada sube 17.8 % y se fija
  en 1,158 pesos.
- La base: paquete_2027 (f-ing, f-trib y simBase.gastoNeto), cotejada con
  los Criterios Generales y la iniciativa del 08-09-2026.
No se pudo abrir: el voto del Senado sobre la Ley Federal de Derechos y la
reserva al ISR (automotrices y gasolineras), que solo traen los medios. El
portal de Comunicación Social del Senado responde 403 a la sesión: es falta
de la plataforma, no del Senado.
"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
COLUMNAS_JS = RAIZ / 'assets' / 'auditor' / 'js' / 'columnas.js'
sys.path.insert(0, str(RAIZ / 'herramientas'))
import gestion_salud as gs  # noqa: E402

DOF_M40 = 'https://sidof.segob.gob.mx/notas/5801708'
LSS = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LSS.pdf'
PEF = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/PEF_2026.pdf'
INEGI_UMA = 'https://www.inegi.org.mx/temas/uma/'
# Donde deberían estar los informes, el análisis y las denuncias: el portal
# de transparencia del IMSS (el «donde» de un pendiente es su enlace oficial).
IMSS_TRANSP = 'https://www.imss.gob.mx/transparencia'
ACUERDO = 'DOF 21-10-2026, Acuerdo ACDO.AS2.HCT.101026/302.P.DG del Consejo Técnico del IMSS'

UMA_MES = 3566.22
RAMO19 = 1541518693444
SUELDO = 10000


def _p(v):
    return '$' + format(v, ',.2f')


def _mdp(v):
    return '$%s millones' % format(round(v / 1e6, 1), ',.1f')


def _base():
    """El ramo 19 se lee de la base, no se copia a mano."""
    t = (RAIZ / 'assets' / 'auditor' / 'js' / 'audit-database.js').read_text(encoding='utf-8')
    i = t.index('"anexo1PEF2026"')
    j = t.index('"ramo": "19"', i)
    k = t.index('"pesos":', j)
    v = int(t[k + 8:t.index(',', k)].strip())
    if v != RAMO19:
        raise SystemExit('integrar_al_momento: el Ramo 19 de la base cambió (%s); revisa la nota de la Modalidad 40' % v)
    return v


def modalidad_40():
    tope_ley = 25 * UMA_MES
    tope_hoy = SUELDO + UMA_MES
    sem = gs.SEM
    return {
        'id': 'imss-modalidad-40-gestores',
        'seccion': 'Al momento',
        'icono': '⏱️',
        'fecha': '28-10-2026',
        'titulo': 'El IMSS acota la Modalidad 40: lo que dice el Diario Oficial y lo que falta probar',
        'balazo': ('Desde el 22 de octubre, quien entre a la Modalidad 40 cotiza con su último salario o, cuando mucho, con una UMA más. '
                   'El esquema de gestores y empresas fantasma que describió el director del IMSS todavía no tiene un documento público.'),
        'nota': {'medio': 'La Jornada', 'titulo': 'Cambios a la modalidad 40, para frenar «abusos y fraudes»: Robledo',
                 'fecha': '28-10-2026', 'url': 'https://www.jornada.com.mx/2026/10/28/politica/012n2pol'},
        'circula': {'red': 'La Jornada (prensa)', 'cuenta': 'Zoé Robledo, director general del IMSS, citado por La Jornada',
                    'fecha': '28 de octubre de 2026',
                    'texto': ('La Modalidad 40 del IMSS se acotó tras detectarse un esquema fraudulento de gestores que financiaban a los asegurados '
                              'para pagar sus cotizaciones. En realidad se trataba de créditos que terminaba pagando el Estado mexicano, con pensiones '
                              'que llegaban a incrementarse hasta mil por ciento. En otros casos, se les inscribía a empresas fantasma para seguir '
                              'cotizando y cubrir las semanas requeridas, para luego incorporarse a la Modalidad 40.')},
        'cuerpo': [
            ('Qué pasó. El 10 de octubre, el Consejo Técnico del IMSS aprobó un acuerdo que se publicó en el Diario Oficial el 21 de octubre '
             'y rige desde el día hábil siguiente, el 22. La Modalidad 40 (la ley la llama «continuación voluntaria en el régimen obligatorio») '
             'no desaparece: quien ya estaba inscrito sigue en las mismas condiciones hasta que termine el periodo que contrató, y conserva '
             'las semanas y los salarios que efectivamente pagó.'),
            ('Qué cambió para quien se inscriba ahora. La ley dice que te inscribes «con el último salario o superior al que tenía en el momento '
             'de la baja» (art. 218), hasta el tope general de 25 veces (art. 28). El acuerdo pone, como medida temporal, un techo mucho más bajo: '
             'tu último salario registrado o hasta ese salario más una UMA (%s al mes en 2026), nunca menos de un salario mínimo. Además, ya no se '
             'puede pagar hacia atrás, porque el aseguramiento cuenta desde la fecha de la solicitud; la inscripción será solo digital, y quien '
             'se asegura por su cuenta como trabajador independiente (art. 13, fracción I) ya no puede contratarla.' % _p(UMA_MES)),
            ('Por qué es dinero público. Las pensiones de quienes eligen el régimen de la ley de 1973 las paga el Gobierno Federal, no un fondo '
             'propio de cada trabajador (Ley del Seguro Social, transitorio duodécimo). Por eso una pensión más alta, lograda con cotizaciones '
             'altas en los últimos años, la termina pagando el erario. En el Presupuesto 2026 ese gasto pasa por el Ramo 19, Aportaciones a '
             'Seguridad Social, con %s; el presupuesto no separa cuánto de eso corresponde a la Modalidad 40.' % _mdp(_base())),
            ('Lo que falta probar. El acuerdo no habla de fraudes, gestores ni empresas fantasma: dice que el Consejo «tomó conocimiento» de los '
             'informes de tres direcciones del IMSS, que no se han publicado. Los casos, el «mil por ciento» y las denuncias de las que habló el '
             'director general del IMSS, Zoé Robledo, son, por ahora, declaraciones. Una acusación no es una condena, y quien pagó su Modalidad 40 con su propio dinero no hizo '
             'nada indebido.'),
            ('El punto ciego. La ley dice «último salario o superior» y el acuerdo le pone techo. Si un acuerdo del Consejo Técnico puede acotar '
             'lo que dice una ley del Congreso lo decidiría, en su caso, un tribunal. Mientras tanto, la medida vale hasta que el IMSS tenga su '
             'análisis financiero, que el propio acuerdo pide a más tardar seis meses después de emitido.'),
        ],
        'ejemplo': {
            'tit': 'La cuenta, con números redondos',
            'txt': 'Si tu último salario registrado ante el IMSS era de %s al mes, esto es lo más alto con lo que podrías cotizar en la Modalidad 40:' % _p(SUELDO),
            'filas': [['Antes: la ley (arts. 218 y 28)', _p(tope_ley), '25 × %s (UMA mensual 2026)' % _p(UMA_MES)],
                      ['Desde el 22-10-2026: el acuerdo', _p(tope_hoy), '%s + %s' % (_p(SUELDO), _p(UMA_MES))]],
            'nota': 'Es un ejemplo derivado con la UMA mensual de 2026. Tu caso depende de tu historial de semanas y salarios.',
        },
        'cotejo': [
            {'dice': 'La Modalidad 40 del IMSS se acotó', 'res': 'consta',
             'explica': ('El punto cuarto del acuerdo limita a los nuevos inscritos a su último salario registrado o hasta ese salario más una UMA, '
                         'sin pagos hacia atrás. Es una medida temporal: dura hasta que el IMSS tenga su análisis financiero. Quien ya estaba '
                         'inscrito conserva sus condiciones.'),
             'fuente': ACUERDO + ', puntos cuarto y séptimo', 'url': DOF_M40},
            {'dice': 'Se acotó tras detectarse un esquema fraudulento de gestores que financiaban a los asegurados para pagar sus cotizaciones',
             'res': 'pendiente',
             'explica': ('El acuerdo solo dice que el Consejo tomó conocimiento de los informes de las direcciones de Incorporación y Recaudación, '
                         'de Prestaciones Económicas y Sociales y Jurídica; no los publica ni menciona a gestores. La ley pide que el asegurado '
                         'pague sus cuotas por mes adelantado (art. 218), pero no dice de dónde debe salir el dinero: si un préstamo así fue '
                         'fraude, lo tiene que probar una investigación.'),
             'fuente': ACUERDO + ', punto primero', 'url': DOF_M40,
             'quien': 'IMSS: su H. Consejo Técnico y su Dirección Jurídica (los informes de la sesión del 10-10-2026 y las denuncias)',
             'donde': IMSS_TRANSP},
            {'dice': 'En realidad se trataba de créditos que terminaba pagando el Estado mexicano', 'res': 'matiz',
             'explica': ('Consta que el Gobierno Federal paga las pensiones de quienes eligen el régimen de 1973: por eso una pensión más alta la '
                         'paga el erario. Que esas cotizaciones se pagaran con préstamos de gestores no tiene, por ahora, documento público.'),
             'fuente': 'Ley del Seguro Social, transitorio duodécimo (texto vigente, última reforma DOF 15-01-2026)', 'url': LSS},
            {'dice': 'Pensiones que llegaban a incrementarse hasta mil por ciento', 'res': 'pendiente',
             'explica': ('Ningún documento público trae los casos ni cómo se calculó ese porcentaje. Sin los casos no se puede comprobar ni '
                         'descartar. El acuerdo ordena que la Dirección de Finanzas analice el efecto de la Modalidad 40 en la situación '
                         'financiera del IMSS a más tardar seis meses después de emitido: ahí debería estar.'),
             'fuente': ACUERDO + ', punto segundo', 'url': DOF_M40,
             'quien': 'IMSS: Dirección de Finanzas, Unidad de Riesgos Financieros y Actuariales (el análisis financiero, a más tardar el 10-04-2027)',
             'donde': IMSS_TRANSP},
            {'dice': 'Se les inscribía a empresas fantasma para seguir cotizando y cubrir las semanas requeridas', 'res': 'pendiente',
             'explica': ('El IMSS no ha dicho qué empresas ni cuántos casos. Una empresa que factura operaciones simuladas aparece en la lista 69-B '
                         'del SAT, que puedes consultar en nuestra Lista negra del SAT; dar de alta trabajadores que no existen se ve en los '
                         'registros del propio IMSS, que no son públicos.'),
             'fuente': ACUERDO + ', puntos primero y quinto', 'url': DOF_M40,
             'quien': 'IMSS: Dirección de Incorporación y Recaudación (qué patrones y cuántos casos)',
             'donde': IMSS_TRANSP},
        ],
        'cifras': [
            {'valor': '+1 UMA', 'etq': 'lo más que puede subir tu salario de cotización al entrar a la Modalidad 40 desde el 22-10-2026',
             'estado': 'oficial', 'fuente': ACUERDO + ', punto cuarto', 'url': DOF_M40},
            {'valor': '25 veces', 'etq': 'el tope general de cotización de la ley, al que antes podía llegar la Modalidad 40 (desde 2016 se mide en UMA)',
             'estado': 'oficial', 'fuente': 'Ley del Seguro Social, arts. 28 y 218', 'url': LSS},
            {'valor': _p(UMA_MES), 'etq': 'una UMA al mes en 2026', 'estado': 'oficial',
             'fuente': 'INEGI, UMA 2026 (DOF 09-01-2026)', 'url': INEGI_UMA},
            {'valor': _mdp(RAMO19), 'etq': 'Ramo 19, Aportaciones a Seguridad Social, en 2026: por ahí pasan las pensiones que paga el Gobierno Federal',
             'estado': 'oficial', 'fuente': 'PEF 2026, Anexo 1, pp. 33-34', 'url': PEF},
            {'valor': '10-04-2027', 'etq': 'a más tardar, el análisis financiero del IMSS (10-10-2026 + 6 meses)', 'estado': 'derivado',
             'fuente': ACUERDO + ', punto segundo', 'url': DOF_M40},
        ],
        'datos': [
            {'ico': '📊', 'tx': 'El estado de resultados del IMSS en 2025', 'url': 'datos-salud-imss.html#sal-imss_dinero',
             'de': ('El seguro de Invalidez y Vida, uno de los dos a los que cotiza la Modalidad 40, cerró con un excedente de %s; '
                    'el de Enfermedad y Maternidad gastó %s más de lo que ingresó, y todo el IMSS cerró con un faltante de %s '
                    '(Memoria Estadística 2025, cuadro XIII.45).' % (_mdp(gs.IV_RESULTADO), _mdp(-sem['resultado']), _mdp(-gs.IMSS_RESULTADO)))},
            {'ico': '🏛️', 'tx': 'La salud financiera del IMSS', 'url': 'herramienta-inspector-entes.html#ente=federal:imss',
             'de': 'Su gasto en la Cuenta Pública 2025 y su ficha en el Auditor de entes, con sus documentos.'},
            {'ico': '🧾', 'tx': 'Busca una empresa en la lista negra del SAT', 'url': 'herramienta-inspector-efos.html',
             'de': 'Por RFC o por nombre: las empresas que el SAT presume que facturan operaciones simuladas (art. 69-B del Código Fiscal).'},
            {'ico': '🔍', 'tx': 'Contrasta otra nota de este tema', 'url': 'herramienta-inspector-nota.html',
             'de': 'Pega la liga de una nota y la cotejamos contra los documentos oficiales.'},
        ],
        'glosario': [
            {'t': 'Continuación voluntaria (Modalidad 40)', 'url': 'glosario.html#Continuacion-Voluntaria'},
            {'t': 'UMA', 'url': 'glosario.html#UMA'},
            {'t': 'Cuota obrera del IMSS', 'url': 'glosario.html#Cuota-Obrera-del-IMSS'},
            {'t': 'Empresa fantasma', 'url': 'glosario.html#Empresa-Fantasma'},
            {'t': 'IMSS', 'url': 'glosario.html#Instituto-Mexicano-del-Seguro-Social'},
        ],
        'red': 'Modalidad 40 IMSS',
        'sigue': [
            {'que': 'El análisis financiero de la Modalidad 40 que el acuerdo pide al IMSS (a más tardar el 10-04-2027)', 'url': IMSS_TRANSP},
            {'que': 'La propuesta de cambio a las reglas que la Dirección Jurídica debe llevar al Consejo Técnico (hasta 6 meses después del análisis)', 'url': DOF_M40},
            {'que': 'Las denuncias que el IMSS dice haber presentado: en qué fiscalía y en qué etapa van', 'url': 'https://www.gob.mx/fgr'},
            {'que': 'Si un tribunal revisa si un acuerdo del Consejo Técnico puede acotar el art. 218 de la ley', 'url': 'https://www.scjn.gob.mx'},
        ],
        'fuentes': [
            {'nombre': ACUERDO + ' (texto íntegro en SIDOF)', 'url': DOF_M40},
            {'nombre': 'Ley del Seguro Social, texto vigente (última reforma DOF 15-01-2026): arts. 28, 218 y transitorio duodécimo', 'url': LSS},
            {'nombre': 'Presupuesto de Egresos de la Federación 2026, Anexo 1, pp. 33-34 (Ramo 19)', 'url': PEF},
            {'nombre': 'INEGI, Unidad de Medida y Actualización 2026', 'url': INEGI_UMA},
            {'nombre': 'IMSS, Memoria Estadística 2025, cap. XIII, cuadro XIII.45', 'url': gs.MEM['XIII']['url']},
            {'nombre': 'Punto de partida: La Jornada, «Cambios a la modalidad 40, para frenar “abusos y fraudes”: Robledo» (28-10-2026)',
             'url': 'https://www.jornada.com.mx/2026/10/28/politica/012n2pol'},
        ],
        'actualizado': '28-10-2026',
    }


CANAL_LIF = 'https://www.canaldelcongreso.gob.mx/noticias/10338'
CANAL_LFD = 'https://www.canaldelcongreso.gob.mx/noticias/10318'
CANAL_LIF_DIP = 'https://www.canaldelcongreso.gob.mx/noticias/10320'
SENADO_GACETA = 'https://www.senado.gob.mx/66/gaceta_del_senado'
LIF26 = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LIF_2026.pdf'
EF_NOTA = 'https://www.elfinanciero.com.mx/nacional/2026/10/28/senado-aprueba-cambios-al-isr-y-aumentos-en-cuotas-de-servicios-y-tramites-para-2027/'
ISR_2027 = 3288975.3   # Canal del Congreso, 10338
IVA_2027 = 1768717.3
IEPS_2027 = 828256.0
DNR_2027 = 1158
DNR_SUBE = 17.8        # Canal del Congreso, 10318


def _paquete():
    """Las cifras del Paquete 2027 se leen de la base, no se copian a mano."""
    t = (RAIZ / 'assets' / 'auditor' / 'js' / 'audit-database.js').read_text(encoding='utf-8')
    i = t.index('"paquete_2027"')

    def campo(marca, clave):
        j = t.index(marca, i)
        k = t.index('"%s":' % clave, j) + len(clave) + 3
        return float(t[k:t.index(',', k)].strip())
    return {'total': campo('"simBase"', 'gastoNeto'), 'ing': campo('"id": "f-ing"', 'm'), 'trib': campo('"id": "f-trib"', 'm')}


def _mmdp(v):
    return '$%s millones' % format(v, ',.1f')


def senado_lif_2027():
    P = _paquete()
    deuda = P['total'] - P['ing']
    return {
        'id': 'senado-ley-de-ingresos-2027',
        'seccion': 'Al momento',
        'icono': '🏛️',
        'fecha': '28-10-2026',
        'titulo': 'El Senado aprueba la Ley de Ingresos 2027: de sus 10.6 billones, casi 1.5 son dinero prestado',
        'balazo': ('El pleno del Senado la aprobó 75 a 34 y sin cambios, así que va al Ejecutivo para publicarse. De los 10.6 billones de pesos '
                   'que «prevé obtener», 9.2 billones son ingresos y el resto es dinero prestado. Lo que pagan los turistas extranjeros '
                   'por entrar a México sube a 1,158 pesos, y el cambio al ISR para automotrices y gasolineras todavía no tiene un '
                   'documento oficial que podamos abrir.'),
        'nota': {'medio': 'El Financiero', 'titulo': 'Senado aprueba cambios al ISR y aumentos en cuotas de servicios y trámites para 2027',
                 'fecha': '28-10-2026', 'url': EF_NOTA},
        'circula': {'red': 'Instagram', 'cuenta': '@elfinanciero_mx (El Financiero)', 'fecha': '28 de octubre de 2026',
                    'texto': ('El Senado aprobó la Ley de Ingresos y la Ley Federal de Derechos para 2027, que contemplan una recaudación de más de '
                              '10.6 billones de pesos… el pago de visitantes extranjeros pasará de 983 a mil 158 pesos… cambios al ISR para excluir '
                              'a determinadas empresas automotrices y gasolineras de las restricciones a las deducciones… más de 6.2 billones '
                              'provendrían de impuestos… endeudamiento de hasta 1.7 billones.')},
        'cuerpo': [
            ('Qué pasó. Según el Canal del Congreso (28 de octubre), el pleno del Senado aprobó la Ley de Ingresos de la Federación para 2027 '
             'con 75 votos a favor y 34 en contra en lo general, y 73 a 33 en lo particular. Quedó «en sus términos», como la mandó la Cámara de '
             'Diputados el 15 de octubre, y se envió al Ejecutivo. La ley manda publicarla en el Diario Oficial a más tardar 20 días naturales '
             'después de aprobada (LFPRH, art. 42, fr. VI).'),
            ('El punto ciego: no son 10.6 billones de «recaudación». La ley estima %s en total, pero esa suma incluye el dinero que el gobierno '
             'pedirá prestado. Los ingresos que entran sin endeudarse, los presupuestarios, son %s; la diferencia, %s, son los ingresos por financiamiento, que la ley suma en su total. Y los '
             '1.7 billones de deuda interna son un techo: lo máximo que puede contratar en el año, no deuda ya contratada.'
             % (_mmdp(P['total']), _mmdp(P['ing']), _mmdp(deuda))),
            ('De dónde sale el dinero. Los impuestos aportan %s, el 58.9 %% del total: %s del ISR, %s del IVA y %s del IEPS, según expuso en '
             'tribuna el presidente de la Comisión de Hacienda del Senado. Pemex y la CFE tienen sus propios techos de deuda.'
             % (_mmdp(P['trib']), _mmdp(ISR_2027), _mmdp(IVA_2027), _mmdp(IEPS_2027))),
            ('Los derechos. La Cámara de Diputados aprobó el 14 de octubre la Ley Federal de Derechos: la cuota que paga quien visita México sin '
             'trabajar aquí (el turista extranjero) sube %s %% y queda en %s pesos, y lo que se recaude se reparte 57 %% para la Defensa, 15 %% '
             'para el Instituto Nacional de Migración y 28 %% para la Tesorería. Que el Senado también la aprobó lo dicen los medios; el documento '
             'del Senado todavía no lo pudimos abrir.' % (DNR_SUBE, format(DNR_2027, ','))),
            ('Lo que falta probar. Los medios dicen que el Senado cambió la reforma al ISR para que la industria automotriz y quienes venden '
             'gasolina y diésel no tengan el nuevo límite a las deducciones de quien ingresa más de 50 millones de pesos, y que por eso esa ley '
             'regresa a la Cámara de Diputados. Hasta leer la minuta del Senado, eso va como pendiente: la falta es nuestra, porque el portal '
             'del Senado no abre desde la plataforma.'),
        ],
        'ejemplo': {
            'tit': 'La cuenta, con números redondos',
            'txt': 'Si la Ley de Ingresos 2027 fueran 100 pesos:',
            'filas': [['Impuestos', '$%.0f' % (100 * P['trib'] / P['total']), '%s ÷ %s × 100' % (_mmdp(P['trib']), _mmdp(P['total']))],
                      ['Otros ingresos (petroleros, cuotas, derechos, organismos…)', '$%.0f' % (100 * (P['ing'] - P['trib']) / P['total']),
                       '(%s − %s) ÷ %s × 100' % (_mmdp(P['ing']), _mmdp(P['trib']), _mmdp(P['total']))],
                      ['Dinero prestado (financiamiento)', '$%.0f' % (100 * deuda / P['total']),
                       '(%s − %s) ÷ %s × 100' % (_mmdp(P['total']), _mmdp(P['ing']), _mmdp(P['total']))]],
            'nota': 'Es un ejemplo derivado con las cifras del Paquete Económico 2027 que la Ley de Ingresos aprobó sin cambios.',
        },
        'cotejo': [
            {'dice': 'El Senado aprobó la Ley de Ingresos para 2027', 'res': 'consta',
             'explica': ('75 a 34 en lo general y 73 a 33 en lo particular; quedó en sus términos y se envió al Ejecutivo. Falta su publicación '
                         'en el Diario Oficial.'),
             'fuente': 'Canal del Congreso, «Senado aprueba Ley de Ingresos 2027 por 10.6 billones de pesos» (28-10-2026)', 'url': CANAL_LIF},
            {'dice': 'Contemplan una recaudación de más de 10.6 billones de pesos', 'res': 'matiz',
             'explica': ('La cifra, %s, consta, pero no es recaudación: es el total de la ley e incluye %s de financiamiento. Lo que entra sin '
                         'endeudarse son %s.' % (_mmdp(P['total']), _mmdp(deuda), _mmdp(P['ing']))),
             'fuente': 'Canal del Congreso (28-10-2026) y Paquete Económico 2027 en la base de la plataforma', 'url': CANAL_LIF},
            {'dice': 'Más de 6.2 billones provendrían del cobro de impuestos', 'res': 'consta',
             'explica': 'Son %s, el 58.9 %% de los ingresos estimados.' % _mmdp(P['trib']),
             'fuente': 'Canal del Congreso (28-10-2026)', 'url': CANAL_LIF},
            {'dice': 'El endeudamiento previsto podría alcanzar hasta 1.7 billones de pesos', 'res': 'consta',
             'explica': ('La ley autoriza deuda interna neta hasta por 1 billón 700 mil millones de pesos. Es un techo, no deuda contratada; '
                         'Pemex y la CFE tienen techos aparte.'),
             'fuente': 'Canal del Congreso (28-10-2026)', 'url': CANAL_LIF},
            {'dice': 'El pago de visitantes extranjeros al ingresar a México pasará de 983 a 1,158 pesos', 'res': 'matiz',
             'explica': ('Constan los 1,158 pesos y la subida de 17.8 %, en la versión que aprobó la Cámara de Diputados; es la cuota de quien '
                         'entra sin permiso para trabajar, el turista. Los 983 pesos de hoy no vienen en la nota oficial, aunque cuadran con '
                         'esa subida (1,158 ÷ 1.178 ≈ 983, derivado).'),
             'fuente': 'Canal del Congreso, «Cámara de Diputados aprueba Ley Federal de Derechos 2027» (14-10-2026)', 'url': CANAL_LFD},
            {'dice': 'El Senado aprobó también la Ley Federal de Derechos', 'res': 'pendiente',
             'explica': 'La nota oficial del Senado que leímos solo trae la Ley de Ingresos. El voto de la Ley de Derechos no lo pudimos abrir.',
             'fuente': 'Canal del Congreso (28-10-2026)', 'url': CANAL_LIF,
             'quien': 'Falta de la plataforma: el dictamen y su votación están en la Gaceta del Senado, que no abre desde nuestra sesión',
             'donde': SENADO_GACETA},
            {'dice': 'Se excluye a automotrices y gasolineras de las restricciones a las deducciones de quien ingresa más de 50 millones, y la '
                     'ley del ISR regresa a Diputados', 'res': 'pendiente',
             'explica': ('Ningún documento oficial que pudimos abrir trae la reserva ni su votación. Cuando la Cámara de Diputados reciba la '
                         'minuta, su texto quedará en la Gaceta Parlamentaria.'),
             'fuente': 'El Financiero y otros medios (28-10-2026)', 'url': EF_NOTA,
             'quien': 'Falta de la plataforma: la minuta del Senado no abre desde nuestra sesión; después la publicará la Gaceta de Diputados',
             'donde': 'https://gaceta.diputados.gob.mx/'},
        ],
        'cifras': [
            {'valor': _mmdp(P['total']), 'etq': 'Ley de Ingresos 2027: el total, con financiamiento', 'estado': 'oficial',
             'fuente': 'Canal del Congreso (28-10-2026)', 'url': CANAL_LIF},
            {'valor': _mmdp(P['ing']), 'etq': 'Ingresos presupuestarios 2027: lo que entra sin endeudarse', 'estado': 'oficial',
             'fuente': 'Criterios Generales de Política Económica 2027 (en la base)', 'url': 'numeros-paquete-2027-cifras.html'},
            {'valor': _mmdp(deuda), 'etq': 'Financiamiento dentro del total (total − ingresos presupuestarios)', 'estado': 'derivado',
             'fuente': 'Operación con las dos cifras anteriores', 'url': 'numeros-paquete-2027-cifras.html'},
            {'valor': _mmdp(P['trib']), 'etq': 'Impuestos estimados para 2027', 'estado': 'oficial',
             'fuente': 'Canal del Congreso (28-10-2026)', 'url': CANAL_LIF},
            {'valor': '75 a 34', 'etq': 'Votación en lo general en el pleno del Senado (73 a 33 en lo particular)', 'estado': 'oficial',
             'fuente': 'Canal del Congreso (28-10-2026)', 'url': CANAL_LIF},
            {'valor': '$%s' % format(DNR_2027, ','), 'etq': 'Cuota del visitante extranjero sin actividad remunerada en 2027 (+17.8 %)',
             'estado': 'oficial', 'fuente': 'Canal del Congreso (14-10-2026)', 'url': CANAL_LFD},
        ],
        'datos': [
            {'ico': '📊', 'tx': 'Cómo se ve 2027: las cifras del Paquete Económico', 'url': 'numeros-paquete-2027-cifras.html',
             'de': 'Ingresos, gasto, déficit y deuda de 2027 junto a 2026, con los Criterios Generales.'},
            {'ico': '🧾', 'tx': 'Los impuestos del Paquete 2027', 'url': 'numeros-paquete-2027-impuestos.html',
             'de': 'Qué impuestos cambian y cuánto se espera de cada uno.'},
            {'ico': '🗓️', 'tx': 'El itinerario que manda la ley', 'url': 'numeros-paquete-2027-itinerario.html',
             'de': 'Diputados a más tardar el 20 de octubre, el Senado el 31 y la publicación 20 días después.'},
            {'ico': '📉', 'tx': 'La deuda', 'url': 'numeros-la-deuda.html',
             'de': 'Cuánto debe el país y quién autoriza cada peso prestado.'},
            {'ico': '🔍', 'tx': 'El cotejo de la Ley de Ingresos en Diputados: el techo de deuda y el perdón de multas',
             'url': 'noticias-auditavision.html#col-lif-2027-deuda-y-multas', 'de': 'Lo que circuló el 15 de octubre, afirmación por afirmación.'},
        ],
        'glosario': [
            {'t': 'LIF (Ley de Ingresos de la Federación)', 'url': 'glosario.html#LIF'},
            {'t': 'Ingresos presupuestarios', 'url': 'glosario.html#Ingresos-Presupuestarios'},
            {'t': 'Techo de endeudamiento neto', 'url': 'glosario.html#Techo-de-Endeudamiento-Neto'},
            {'t': 'ISR', 'url': 'glosario.html#ISR'},
            {'t': 'Derechos (contribución)', 'url': 'glosario.html#Derechos'},
        ],
        'red': 'Senado Ley de Ingresos 2027 ISR automotrices gasolineras',
        'sigue': [
            {'que': 'La publicación de la Ley de Ingresos 2027 en el Diario Oficial (a más tardar 20 días naturales después de aprobada)',
             'url': 'https://www.dof.gob.mx/'},
            {'que': 'El voto del Senado sobre la Ley Federal de Derechos y su publicación en el Diario Oficial', 'url': SENADO_GACETA},
            {'que': 'La minuta del ISR que regresa a la Cámara de Diputados: el texto de la excepción para automotrices y gasolineras y su votación',
             'url': 'https://gaceta.diputados.gob.mx/'},
            {'que': 'El Presupuesto de Egresos 2027, que la Cámara de Diputados debe aprobar a más tardar el 15 de noviembre', 'url': 'https://gaceta.diputados.gob.mx/'},
        ],
        'fuentes': [
            {'nombre': 'Canal del Congreso: Senado aprueba Ley de Ingresos 2027 por 10.6 billones de pesos (28-10-2026)', 'url': CANAL_LIF},
            {'nombre': 'Canal del Congreso: Cámara de Diputados aprueba Ley Federal de Derechos 2027 (14-10-2026)', 'url': CANAL_LFD},
            {'nombre': 'Canal del Congreso: Aprueban en San Lázaro Ley de Ingresos 2027 (15-10-2026)', 'url': CANAL_LIF_DIP},
            {'nombre': 'Paquete Económico 2027: Criterios Generales de Política Económica (en la base de la plataforma)', 'url': 'numeros-paquete-2027-cifras.html'},
            {'nombre': 'Punto de partida: El Financiero, «Senado aprueba cambios al ISR y aumentos en cuotas de servicios y trámites para 2027» (28-10-2026)',
             'url': EF_NOTA},
        ],
        'actualizado': '29-10-2026',
    }


NOTAS = [modalidad_40, senado_lif_2027]


def main():
    raw = COLUMNAS_JS.read_bytes().decode('utf-8')
    cab = '  var COLUMNAS = [\r\n'
    i = raw.index(cab) + len(cab)
    for hacer in reversed(NOTAS):
        n = hacer()
        # Mismo sangrado que las columnas a mano: « {» y «  "id"».
        txt = '\r\n'.join(' ' + l for l in json.dumps(n, ensure_ascii=False, indent=1).split('\n')) + ',\r\n'
        marca = ' {\r\n  "id": "%s",' % n['id']
        if marca in raw:
            a = raw.index(marca)
            b = raw.index('\r\n },\r\n', a) + len('\r\n },\r\n')
            raw = raw[:a] + txt + raw[b:]
        else:
            raw = raw[:i] + txt + raw[i:]
    COLUMNAS_JS.write_bytes(raw.encode('utf-8'))
    print('columnas.js: %d nota(s) de «Al momento»' % len(NOTAS))


if __name__ == '__main__':
    main()
