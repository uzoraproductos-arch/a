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


NOTAS = [modalidad_40]


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
