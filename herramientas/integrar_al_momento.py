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

Nota 3 · Jalisco y el gasto federal (29-10-2026). Pieza que pasó el autor:
publicación de @radioformulajalisco en Instagram (28-10-2026) sobre el
análisis del PRI Jalisco. Documentos cotejados:
- INEGI, Comunicado 156/25, PIB por Entidad Federativa 2024 (05-12-2025),
  p. 1: Jalisco aporta el 7.5 % del PIB nacional, el cuarto lugar.
- La base: estados[].ramo28, ramo33 y pobPersonas (anexos 15 y 16 del
  acuerdo de distribución 2026, DOF, y población a mitad de 2026 del CONAPO).
  El lugar por habitante se calcula aquí, con la misma cuenta que «pc».
- Presidencia, versión estenográfica del 21-10-2026: «El Gobierno Federal va
  a aportar los recursos… Todo»: «alrededor de 12 mil millones, 13 mil
  millones» para el agua de Guadalajara.
No se pudo abrir: el Proyecto de Presupuesto 2027 por entidad (el portal del
PPEF no responde a la sesión) ni las notas de Crónica y Notisistema (sus
dominios están fuera de la red de la sesión). El lugar 24, el 83 % y los
recortes en carreteras quedan como pendientes: la falta es de la plataforma.

Nota 4 · La segunda entrega de la ASF de la Cuenta Pública 2025 (31-10-2026).
Pieza que pasó el autor: publicación de @pajaropolitico (Animal Político) en
Instagram (31-10-2026). Documentos cotejados:
- LFRCF, arts. 35, 38, 39 y 41: la segunda entrega es el último día hábil de
  octubre (30-10-2026) y los plazos para aclarar (ya en la base, PLAZOS de
  integrar_cuenta_publica.py).
- La base: la primera entrega de la Cuenta Pública 2025 (MDB, p. 11, en
  cuenta_publica.cp2025 de audit-database.js) y el padrón de 2,479 municipios
  del INEGI.
No se pudo abrir: el portal de la ASF (asf.gob.mx e informe.asf.gob.mx no
resuelven desde la sesión) ni los sitios de los medios. Las cifras de la
segunda entrega quedan pendientes: la falta es de la plataforma. De los
medios solo se guardan titular, medio, fecha y liga (campo «medios»: la
hemeroteca), tal como los indexaba el buscador el 31-10-2026.

Nota 5 · Portacelis y el permiso de importación de diésel (31-10-2026). Pieza
que pasó el autor: la publicación de @derechadiariomx en Instagram («URGENTE —
REGALO DE DESPEDIDA…»), que retoma la investigación de MCCI del 05-10-2026.
El 01-11-2026 el autor dio la cuenta: se cita, sin fecha exacta («hace 3 semanas»). Documentos cotejados:
- Constitución, art. 83: el sexenio terminó el 30-09-2024.
- SAT, lista del art. 69-B del CFF (assets/auditor/data/sat-69b.js, corte al
  31-12-2025): Portacelis no aparece. Se lee del archivo, no se copia.
No se pudo abrir: el permiso de la Sener (la copia la tiene MCCI), el acuerdo
del DOF del 18-09-2024 (dof.gob.mx no resuelve desde la sesión) ni el sitio de
MCCI: el permiso, los litros y las fechas quedan pendientes, por falta de la
plataforma. La declaratoria del SAT ante la FGR no es pública: las carpetas
de investigación son reservadas (CNPP, art. 218). A la persona privada que,
según MCCI, administraba la empresa no se le nombra (AGENTS.md §2 bis).

Nota 6 · El Carnaval de Ensenada y sus 22 millones (31-10-2026). Pieza que
pasó el autor: publicación de @danielasalgadoens (la regidora Ana Daniela
García Salgado) en Instagram, tras la glosa del IMCUDHE; el 01-11-2026 dio la
liga del reel (instagram.com/reel/DfI6V7Ltsgh). Documentos cotejados:
- INEGI, EFIPEM 2024, cifras definitivas (municipios-efipem.js): lo que
  ingresó Ensenada en 2024. Se lee del archivo, no se copia.
No se pudo abrir: la glosa ni la información financiera del IMCUDHE y del
Ayuntamiento (sus portales no resuelven desde la sesión). Las cifras del
Carnaval (22.3 o 22.7 millones, 1.2 de recuperación, 16 del presupuesto y la
ampliación de 11) solo las tiene la prensa: quedan pendientes, por falta de
la plataforma. Las cuentas con números de prensa no se hacen como derivado.

Nota 7 · La ASF denuncia una presunta triangulación en Nuevo León (31-10-2026).
Pieza que pasó el autor: publicación de @lajornadaonline en Instagram, con la
nota de La Jornada del 31-10-2026. Documentos cotejados:
- Constitución, arts. 20 (presunción de inocencia) y 111 (declaración de
  procedencia para gobernadores por delitos federales).
- La base: estados[] (Ramos 28 y 33 de 2026 para Nuevo León y Sinaloa).
No se pudo abrir: el informe individual de la ASF ni su denuncia (asf.gob.mx no
resuelve desde la sesión). Las cifras (7,200; 5,851; 5,154.6; 385.3 o 928.13
millones) quedan pendientes, por falta de la plataforma. No se nombra a la
constructora, a las otras empresas ni a los familiares: ningún documento
oficial abierto los nombra (AGENTS.md §2 bis).

Nota 8 · El cobro a turistas extranjeros y la parte de la Defensa (01-11-2026).
Pieza que pasó el autor: publicación de @derechadiariomx en Instagram («18 mil
millones en subsidios para el Tren Maya y el AIFA… aumento del 57 %»), que
retoma la nota de Latinus del 12-10-2026. Documentos cotejados:
- Canal del Congreso, 14-10-2026: Ley Federal de Derechos 2027, DNR de 1,158
  pesos (+17.8 %) y reparto 57 % Defensa, 15 % INM y 28 % Tesorería.
- La base: estados de actividades 2024 del Tren Maya y del AIFA (Cuenta
  Pública, simulador_megaobras.operacion_oficial) y la inversión 2027 del Tren
  Maya (CGPE 2027, p. 33, paquete_2027.inversion). Se leen, no se copian.
No se pudo abrir: el dictamen, la reserva y la versión estenográfica (Gaceta
Parlamentaria), ni la votación del Senado. El 50 % anterior de la Defensa y
los 18 mil millones son de prensa: el 50 % solo se usa dicho así, y los 18 mil
quedan pendientes, por falta de la plataforma.

Nota 9 · Pemex y su pérdida del tercer trimestre de 2026 (01-11-2026). Pieza
que pasó el autor: publicación de un medio en Instagram («pérdida neta de 10 mil
792 millones… 82.4 % menos que los 61 mil 247»). Documentos cotejados:
- La base: Anexo 1 del PEF 2026 (gasto programable y costo financiero de
  Pemex) y el punto ciego c-pemex del Paquete 2027 (Ramo 18). Se leen.
No se pudo abrir: el reporte trimestral de Pemex (su portal y la BMV). La
pérdida (10,792 o 10,795), los dólares, la base de 2025 y las causas quedan
pendientes, por falta de la plataforma.

Nota 10 · Los servidores que México exporta y su contenido nacional
(01-11-2026). Pieza que pasó el autor: publicación en Instagram
(instagram.com/p/DfAF4OKsLkv). Documentos cotejados:
- La base: ficha de Querétaro (estados[]: recaudación propia y dependencia).
No se pudo abrir: la balanza comercial ni el valor agregado de exportación
del INEGI. Las exportaciones (S&P Global, privada), el contenido nacional
(estimación de prensa) y los 82,500 millones (proyección de MEXDC) quedan
pendientes; la estrategia es una propuesta y no se coteja.

Nota 11 · El agua de Guadalajara: 14,500 millones federales «sin deuda»
(01-11-2026). Pieza que pasó el autor: publicación de @gobmexico en Instagram.
Documentos cotejados:
- Presidencia, comunicado del 28-10-2026 (solo su título: gob.mx no abre) y la
  conferencia del 21-10-2026 (AGUA_FED, ya en la nota de Jalisco).
- La base: Paquete Económico 2027 (el financiamiento de la Ley de Ingresos) y
  el costo del acueducto en la iniciativa de Jalisco (crisis_ambientales.py).
El desglose (9,300 y 5,200), las fechas y la calidad del agua quedan
pendientes.

Campo opcional temas [palabras]: las que son propias de la nota («carnaval»); en el
chat, una pregunta que las trae abre la nota aunque también nombre a un municipio
o a un estado (temaColumna() de asistente.js).

Campo nuevo desde la nota 4: medios [{medio, titulo, fecha, url}], cómo lo
contaron otros medios. Es la hemeroteca: la página «Verifica una noticia» las
lista por medio y el chat reconoce sus ligas cuando el lector las pega.
"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
COLUMNAS_JS = RAIZ / 'assets' / 'auditor' / 'js' / 'columnas.js'
sys.path.insert(0, str(RAIZ / 'herramientas'))
import gestion_salud as gs  # noqa: E402
import auditorias  # noqa: E402

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


INEGI_PIBE = 'https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/pibent/PIBE2024_CP.pdf'
PRES_2110 = ('https://www.gob.mx/presidencia/es/articulos/version-estenografica-conferencia-de-prensa-de-la-presidenta-'
             'claudia-sheinbaum-pardo-del-21-de-octubre-de-2026')
PPEF = 'https://www.ppef.hacienda.gob.mx/'
CUENTA_PUBLICA = 'https://www.cuentapublica.hacienda.gob.mx/'
CRONICA_HARO = ('https://www.cronica.com.mx/jalisco/guadalajara/2026/10/27/'
                'lamenta-laura-haro-abandono-de-jalisco-en-presupuesto-federal-pide-reasignar-30-mil-mdp-para-2027/')
DOF_DISTRIB = 'https://dof.gob.mx/nota_detalle.php?codigo=5776006&fecha=12/12/2025'
NOTISISTEMA_83 = 'https://www.notisistema.com/noticias/acusa-pri-recorte-de-83-en-inversion-federal-para-jalisco/'
PIB_JAL = 7.5          # INEGI, PIBE 2024, p. 1
AGUA_FED = (12000, 13000)   # Presidencia, 21-10-2026 («alrededor de»)
PLANTA_JAL = 7500           # Presidencia, 21-10-2026, y Gobierno de Jalisco (crisis_ambientales.py)
REASIGNA = 30000            # lo que pide el PRI Jalisco


def _jalisco():
    """Lo que la Federación reparte a Jalisco se lee de la base, y el lugar se calcula igual que «pc»."""
    E = auditorias.db()['estados']
    j = next(e for e in E if e['abbr'] == 'JAL')
    tot = {k: sum(e[k] for e in E) for k in ('ramo28', 'ramo33', 'gasto', 'pobPersonas')}

    def lugar(f):
        return sorted(E, key=f, reverse=True).index(j) + 1
    return {
        'j': j, 'n': len(E), 'tot': tot,
        'pc_nal': tot['gasto'] * 1e6 / tot['pobPersonas'],
        'lugar': lugar(lambda e: e['pc']),
        'lugar28': lugar(lambda e: e['ramo28'] / e['pobPersonas']),
        'lugar33': lugar(lambda e: e['ramo33'] / e['pobPersonas']),
        'sh_pob': 100 * j['pobPersonas'] / tot['pobPersonas'],
        'sh_gasto': 100 * j['gasto'] / tot['gasto'],
        'sh28': 100 * j['ramo28'] / tot['ramo28'],
        'sh33': 100 * j['ramo33'] / tot['ramo33'],
    }


def jalisco_gasto_federal():
    J = _jalisco()
    j = J['j']
    pesos = lambda v: '$' + format(round(v), ',')  # noqa: E731
    pct = lambda v: format(v, '.1f') + ' %'  # noqa: E731
    veces_gasto = 100 * REASIGNA / j['gasto']
    return {
        'id': 'jalisco-gasto-federal-pef-2027',
        'seccion': 'Al momento',
        'icono': '🗺️',
        'fecha': '28-10-2026',
        'titulo': 'Jalisco y el gasto federal: aporta el 7.5 %% del PIB y recibe el %s de lo que la Federación reparte a los estados'
                  % pct(J['sh_gasto']),
        'balazo': ('El PRI Jalisco dice que el estado es el lugar 24 de 32 en gasto federal por habitante y pide reasignarle 30 mil millones '
                   'en el Presupuesto 2027. Con las participaciones y aportaciones de 2026 que tiene la plataforma, Jalisco sale todavía más '
                   'abajo: lugar %d de %d. El punto ciego es por qué: el Ramo 33 se reparte por necesidad, y ahí Jalisco cae al '
                   'lugar %d. El 83 %% de caída de la inversión es un cálculo del partido que aún no podemos cotejar.'
                   % (J['lugar'], J['n'], J['lugar33'])),
        'nota': {'medio': 'Crónica Jalisco', 'titulo': 'Lamenta Laura Haro abandono de Jalisco en presupuesto federal, pide reasignar 30 mil mdp para 2027',
                 'fecha': '27-10-2026', 'url': CRONICA_HARO},
        'circula': {'red': 'Instagram', 'cuenta': '@radioformulajalisco (Radio Fórmula Jalisco)', 'fecha': '28 de octubre de 2026',
                    'texto': ('Aunque Jalisco es de los estados que más aporta a la economía nacional, ocupa el lugar 24 de 32 en gasto federal '
                              'por habitante. El PRI Jalisco reveló que la inversión pública cayó un 83 % en los últimos años, con tijeretazos '
                              'críticos en carreteras y agua. La dirigente Laura Haro exigió reasignar 30 mil millones de pesos en el PEF 2027.')},
        'cuerpo': [
            ('Qué pasó. La dirigente del PRI en Jalisco, Laura Haro, presentó un análisis de su partido sobre lo que el Presupuesto '
             'federal le da al estado y pidió que la Cámara de Diputados le reasigne 30 mil millones de pesos en el Presupuesto de Egresos 2027, '
             'que la Cámara aprueba a más tardar el 15 de noviembre (Constitución, art. 74, fr. IV). Un análisis de partido es lo que se coteja, '
             'no una fuente: aquí va cada afirmación contra el documento.'),
            ('Lo que sí consta. Jalisco produce el %s del PIB del país, el cuarto lugar después de la Ciudad de México, el Estado de México y '
             'Nuevo León (INEGI, PIB por entidad 2024). Y en 2026 recibe %s de participaciones y aportaciones, %s por habitante, contra %s '
             'del promedio nacional: el lugar %d de %d. Tiene el %s de la población y recibe el %s de ese dinero.'
             % (pct(PIB_JAL), _mmdp(j['gasto']), pesos(j['pc']), pesos(J['pc_nal']), J['lugar'], J['n'], pct(J['sh_pob']), pct(J['sh_gasto']))),
            ('El punto ciego: no es una sola bolsa. Las participaciones (Ramo 28) se reparten con la fórmula de la Ley de Coordinación Fiscal, '
             'que pesa la población y la actividad económica: ahí Jalisco recibe el %s y queda en el lugar %d por habitante, a la par de su '
             'población. Las aportaciones (Ramo 33) se reparten por necesidad (la pobreza, los maestros y las escuelas que paga la Federación): '
             'ahí recibe el %s y cae al lugar %d. Repartir por necesidad es lo que manda la ley; si la fórmula es justa con un estado que '
             'produce mucho es la discusión de fondo del pacto fiscal, y es política, no aritmética.'
             % (pct(J['sh28']), J['lugar28'], pct(J['sh33']), J['lugar33'])),
            ('Lo que dice el lugar 24. Según la prensa, el PRI no midió esto, sino todo el gasto que el Proyecto de Presupuesto 2027 ubica en '
             'cada estado, una medida más amplia que lo que recibe el gobierno del estado. Es otra medida, y su documento todavía no '
             'lo pudimos abrir: va como pendiente. Con las dos medidas Jalisco queda en la parte baja de la tabla; el lugar exacto depende de '
             'qué se cuenta.'),
            ('El agua. El 21 de octubre la Presidenta dijo que el Gobierno Federal pondrá «todo» lo que falta para el agua de Guadalajara, '
             '«alrededor de 12 mil millones, 13 mil millones», mientras Jalisco paga una planta potabilizadora de unos %s. Es un anuncio: el '
             'dinero todavía no aparece en un presupuesto aprobado, y eso es lo que hay que seguir en el PEF 2027. Los 30 mil millones que pide '
             'el PRI equivalen al %s de lo que Jalisco recibe en un año de participaciones y aportaciones.'
             % (_mmdp(PLANTA_JAL), pct(veces_gasto))),
        ],
        'ejemplo': {
            'tit': 'La cuenta, con números redondos',
            'txt': 'De cada 100 pesos, o de cada 100 personas, del país:',
            'filas': [
                ['Lo que produce Jalisco del PIB nacional (2024)', '$%s' % format(PIB_JAL, '.1f'), 'INEGI, PIB por entidad 2024, p. 1'],
                ['Las personas que viven en Jalisco (2026)', format(J['sh_pob'], '.1f'),
                 '%s ÷ %s × 100' % (format(j['pobPersonas'], ','), format(J['tot']['pobPersonas'], ','))],
                ['Lo que le llega de participaciones (Ramo 28)', '$%s' % format(J['sh28'], '.1f'),
                 '%s ÷ %s × 100' % (_mmdp(j['ramo28']), _mmdp(J['tot']['ramo28']))],
                ['Lo que le llega de aportaciones (Ramo 33)', '$%s' % format(J['sh33'], '.1f'),
                 '%s ÷ %s × 100' % (_mmdp(j['ramo33']), _mmdp(J['tot']['ramo33']))],
            ],
            'nota': ('Es un ejemplo derivado con los anexos de distribución 2026 (DOF) y la población a mitad de 2026 del CONAPO. No incluye '
                     'convenios ni el Ramo 25.'),
        },
        'cotejo': [
            {'dice': 'Jalisco es de los estados que más aporta a la economía nacional', 'res': 'consta',
             'explica': 'Aporta el 7.5 % del PIB nacional de 2024, el cuarto lugar entre las 32 entidades.',
             'fuente': 'INEGI, Producto Interno Bruto por Entidad Federativa 2024, comunicado 156/25 (05-12-2025), p. 1', 'url': INEGI_PIBE},
            {'dice': 'Ocupa el lugar 24 de 32 en gasto federal por habitante', 'res': 'matiz',
             'explica': ('Depende de qué se cuente. En participaciones y aportaciones 2026, lo que la Federación le entrega al gobierno del estado '
                         'y a sus municipios, Jalisco recibe %s por habitante y queda en el lugar %d de %d (derivado), más abajo todavía. El '
                         'lugar 24 sale, según la prensa, del gasto que el Proyecto 2027 ubica por entidad, que aún no integramos.'
                         % (pesos(j['pc']), J['lugar'], J['n'])),
             'fuente': 'DOF 12-12-2025, acuerdo de distribución de participaciones 2026 (Anexo 15); aportaciones en el Anexo 16 modificado (DOF 09-07-2026) y población del CONAPO, en la base de la plataforma',
             'url': DOF_DISTRIB},
            {'dice': 'La inversión pública cayó un 83 % en los últimos años', 'res': 'pendiente',
             'explica': ('Es un cálculo del PRI Jalisco que la prensa atribuye a comparar promedios de años distintos. No encontramos el documento '
                         'del cálculo, y la serie oficial de inversión federal por estado de cada año está en la Cuenta Pública, que la '
                         'plataforma todavía no integra por entidad.'),
             'fuente': 'Notisistema (prensa), «Acusa PRI recorte de 83% en inversión federal para Jalisco»', 'url': NOTISISTEMA_83,
             'quien': 'Falta de la plataforma: la inversión federal por entidad de cada año viene en la Cuenta Pública y aún no la integramos',
             'donde': CUENTA_PUBLICA},
            {'dice': 'Con tijeretazos críticos en carreteras y agua', 'res': 'pendiente',
             'explica': ('La publicación no da montos ni programas. En agua, la Presidenta anunció el 21 de octubre que la Federación pondrá '
                         'alrededor de 12 a 13 mil millones para Guadalajara, pero todavía no está en un presupuesto aprobado. Las carreteras '
                         'por estado vienen en el Proyecto de Presupuesto 2027, que aún no pudimos abrir.'),
             'fuente': 'Presidencia, versión estenográfica de la conferencia del 21-10-2026', 'url': PRES_2110,
             'quien': 'Falta de la plataforma: el Proyecto de Presupuesto 2027 por entidad y por programa no abre desde nuestra sesión',
             'donde': PPEF},
        ],
        'cifras': [
            {'valor': pct(PIB_JAL), 'etq': 'Lo que aporta Jalisco al PIB nacional (2024), cuarto lugar', 'estado': 'oficial',
             'fuente': 'INEGI, PIB por entidad 2024, p. 1', 'url': INEGI_PIBE},
            {'valor': _mmdp(j['gasto']), 'etq': 'Participaciones y aportaciones de Jalisco en 2026 (Ramo 28 + Ramo 33)', 'estado': 'derivado',
             'fuente': 'Anexos 15 y 16 del acuerdo de distribución 2026 (DOF)', 'url': 'numeros-mapa-del-gasto-federalizado.html?e=JAL'},
            {'valor': pesos(j['pc']), 'etq': 'Por habitante en Jalisco: lugar %d de %d' % (J['lugar'], J['n']), 'estado': 'derivado',
             'fuente': 'Ramos 28 y 33 de 2026 entre la población a mitad de 2026 del CONAPO', 'url': 'numeros-mapa-del-gasto-federalizado.html?e=JAL'},
            {'valor': pesos(J['pc_nal']), 'etq': 'Por habitante, promedio nacional (suma de los 32 ÷ población del país)', 'estado': 'derivado',
             'fuente': 'Misma base', 'url': 'numeros-mapa-del-gasto-federalizado.html'},
            {'valor': 'Lugar %d y lugar %d' % (J['lugar28'], J['lugar33']), 'etq': 'Por habitante: en participaciones (Ramo 28) y en aportaciones (Ramo 33)',
             'estado': 'derivado', 'fuente': 'Misma base', 'url': 'numeros-mapa-del-gasto-federalizado.html?e=JAL'},
            {'valor': '$%s a $%s millones' % (format(AGUA_FED[0], ','), format(AGUA_FED[1], ',')),
             'etq': 'Lo que la Federación anunció para el agua de Guadalajara (anuncio, no presupuesto aprobado)', 'estado': 'oficial',
             'fuente': 'Presidencia, conferencia del 21-10-2026', 'url': PRES_2110},
            {'valor': pct(veces_gasto), 'etq': 'Los 30 mil millones que pide el PRI, frente a las participaciones y aportaciones 2026 de Jalisco',
             'estado': 'derivado', 'fuente': '$30,000 millones ÷ %s × 100' % _mmdp(j['gasto']), 'url': 'numeros-mapa-del-gasto-federalizado.html?e=JAL'},
        ],
        'datos': [
            {'ico': '🗺️', 'tx': 'El mapa del gasto federalizado, en Jalisco', 'url': 'numeros-mapa-del-gasto-federalizado.html?e=JAL',
             'de': 'Participaciones, aportaciones y convenios de cada estado, por habitante.'},
            {'ico': '🧾', 'tx': 'El estado de cuenta y la salud financiera de Jalisco', 'url': 'herramienta-inspector-entes.html#ente=estatal:JAL',
             'de': 'Cuánto recauda por su cuenta, cuánto depende de la Federación, su deuda y lo que la ASF dejó por aclarar.'},
            {'ico': '🚱', 'tx': 'Crisis ambientales: el agua de Guadalajara', 'url': 'herramienta-ambiente-crisis.html',
             'de': 'El Acueducto, la planta potabilizadora, El Zapotillo y lo que nadie ha publicado.'},
            {'ico': '📦', 'tx': 'Auditoría en imágenes: el Ramo 33', 'url': 'auditoria-ramo-33.html',
             'de': 'Cómo se reparten las aportaciones y qué encuentra la ASF.'},
            {'ico': '🗓️', 'tx': 'El itinerario del Paquete 2027', 'url': 'numeros-paquete-2027-itinerario.html',
             'de': 'El Presupuesto de Egresos se aprueba a más tardar el 15 de noviembre.'},
        ],
        'glosario': [
            {'t': 'Gasto federalizado', 'url': 'glosario.html#Gasto-Federalizado'},
            {'t': 'Ramo 28 (participaciones)', 'url': 'glosario.html#Ramo-28'},
            {'t': 'Ramo 33 (aportaciones)', 'url': 'glosario.html#Ramo-33'},
            {'t': 'PEF (Presupuesto de Egresos de la Federación)', 'url': 'glosario.html#PEF'},
            {'t': 'PIB (Producto Interno Bruto)', 'url': 'glosario.html#PIB'},
        ],
        'red': 'Jalisco gasto federal por habitante PEF 2027 PRI 30 mil millones',
        'sigue': [
            {'que': 'Novedad del 28-10-2026: la Federación ya habla de 14,500 millones para el agua (ver la nota «El agua de Guadalajara»)',
             'url': 'noticias-al-momento-agua-guadalajara-14500-federal.html'},
            {'que': 'El Presupuesto de Egresos 2027 aprobado (a más tardar el 15 de noviembre): si trae reasignaciones para Jalisco y cuánto',
             'url': 'https://gaceta.diputados.gob.mx/'},
            {'que': 'Que el dinero federal anunciado para el agua de Guadalajara aparezca en el Presupuesto 2027 con su programa y su monto',
             'url': PPEF},
            {'que': 'El gasto del Proyecto 2027 por entidad, para cotejar el lugar 24 de 32', 'url': PPEF},
            {'que': 'La inversión federal en Jalisco año por año en la Cuenta Pública, para cotejar el 83 %', 'url': CUENTA_PUBLICA},
        ],
        'fuentes': [
            {'nombre': 'INEGI: Producto Interno Bruto por Entidad Federativa 2024, comunicado 156/25 (05-12-2025)', 'url': INEGI_PIBE},
            {'nombre': 'Acuerdos de distribución de participaciones y aportaciones 2026 (DOF) y población del CONAPO, en la base de la plataforma',
             'url': 'numeros-mapa-del-gasto-federalizado.html'},
            {'nombre': 'Presidencia: versión estenográfica de la conferencia del 21-10-2026', 'url': PRES_2110},
            {'nombre': 'Punto de partida: Crónica Jalisco, «Lamenta Laura Haro abandono de Jalisco en presupuesto federal, pide reasignar 30 mil mdp para 2027» (27-10-2026)',
             'url': CRONICA_HARO},
            {'nombre': 'Prensa: Notisistema, «Acusa PRI recorte de 83% en inversión federal para Jalisco»', 'url': NOTISISTEMA_83},
        ],
        'actualizado': '01-11-2026',
    }


ASF_PORTAL = 'https://informe.asf.gob.mx/'
AL_MOMENTO_PAG = 'noticias-al-momento-%s.html'
ASF_MDB25A = 'https://www.asf.gob.mx/Trans/Informes/IR2025a/Documentos/Matriz/IR2025_Entrega_a.pdf'
LFRCF = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LFRCF.pdf'
PAJARO = 'https://www.instagram.com/pajaropolitico/'
FALTA_ASF = ('Falta de la plataforma: la ASF entregó a la Cámara de Diputados su segunda entrega de la Cuenta Pública 2025 (la ley '
             'la fija el último día hábil de octubre: el 30-10-2026), pero su portal no abre desde nuestro servidor y aún no integramos '
             'su Matriz de Datos Básicos.')


def _cp2025a():
    """La primera entrega 2025 se lee de la base, no se copia a mano."""
    import integrar_cuenta_publica as icp
    a = icp.CP2025A
    if a['entrega'] != 'primera' or a['auditorias'] != 33:
        raise SystemExit('integrar_al_momento: la primera entrega 2025 cambió; revisa la nota de la ASF')
    # Los plazos de la cuenta del ejemplo, tal como están en la base.
    pl = [(x['plazo'], x['fundamento']) for x in icp.PLAZOS]
    for x in (('10 días hábiles', 'LFRCF, art. 39'), ('30 días hábiles', 'LFRCF, art. 39'), ('120 días hábiles', 'LFRCF, art. 41')):
        if x not in pl:
            raise SystemExit('integrar_al_momento: el plazo %s cambió en integrar_cuenta_publica.PLAZOS' % (x,))
    return a


def _municipios():
    t = (RAIZ / 'assets' / 'auditor' / 'js' / 'municipios-efipem.js').read_text(encoding='utf-8')
    if 'Los 2,479 municipios' not in t:
        raise SystemExit('integrar_al_momento: el padrón municipal cambió; revisa la nota de la ASF')
    return 2479


def asf_segunda_entrega_2025():
    from apartados import glosario_ancla
    a = _cp2025a()
    mun = _municipios()
    pct = round(100 * 42 / mun, 1)
    acl, rec = a['porAclarar'] / 1e6, a['recuperaciones'] / 1e6
    g = lambda t: {'t': t.split(' (')[0], 'url': 'glosario.html#' + glosario_ancla(t)}
    return {
        'id': 'asf-segunda-entrega-cp2025',
        'seccion': 'Al momento',
        'icono': '🔎',
        'fecha': '30-10-2026',
        'titulo': 'La ASF y los 9 mil millones «por aclarar» de 2025: lo que se sabe, lo que falta y lo que nadie te explica',
        'balazo': ('La Auditoría Superior entregó su segunda tanda de informes de la Cuenta Pública 2025 y los medios coinciden en «más de 9 mil millones» '
                   'pendientes de aclarar, más de la mitad en 42 municipios. Antes de compartirlo: «por aclarar» no es un robo probado, 42 municipios '
                   'son menos del 2 % de los del país y las 40 denuncias no salieron todas de este informe. Las cifras exactas siguen pendientes hasta '
                   'que integremos el documento de la ASF.'),
        'nota': {'medio': 'Animal Político (@pajaropolitico, Instagram)',
                 'titulo': 'La ASF reportó más de 9 mil mdp pendientes de aclarar: 5 mil 200 mdp corresponden a 42 municipios',
                 'fecha': '31-10-2026', 'url': PAJARO},
        'circula': {'red': 'Instagram', 'cuenta': '@pajaropolitico (Animal Político)', 'fecha': '31 de octubre de 2026',
                    'texto': ('La ASF reportó más de 9 mil mdp pendientes de aclarar: 5 mil 200 mdp corresponden a 42 municipios que no acreditaron '
                              'el destino del gasto. Hay 40 denuncias por obras no hechas y equipo extraviado.')},
        'cuerpo': [
            ('Qué pasó. El 30 de octubre, último día hábil del mes, la Auditoría Superior de la Federación (ASF) entregó a la Cámara de Diputados '
             'la segunda tanda de informes individuales de su revisión de la Cuenta Pública 2025. No es una fecha que eligió: la Ley de '
             'Fiscalización la fija así (art. 35), y la tercera tanda, con el Informe General, llega el 20 de febrero de 2027.'),
            ('Lo que reportan los medios. Todos coinciden en «más de 9 mil millones de pesos» por aclarar en los tres órdenes de gobierno y en '
             'que el bloque más grande está en 42 municipios, «más de 5 mil 200 millones». En el detalle no coinciden: una nota habla de 9,008 '
             'millones; otra, de 9,600 al sumar la primera entrega de junio. Por eso aquí todavía no damos una cifra exacta: la daremos con la '
             'Matriz de Datos Básicos de la ASF, que es el documento que manda.'),
            ('Lo que casi nadie explica. «Por aclarar» quiere decir que, al cierre de la auditoría, el gobierno no presentó los papeles que '
             'prueban en qué se gastó ese dinero. No es un daño comprobado: la ley le da 30 días hábiles para responder después de recibir su '
             'informe, y a la ASF 120 días hábiles para decidir si lo aclarado basta (arts. 39 y 41). Lo que no se aclare puede volverse un '
             'pliego de observaciones y, después, una investigación.'),
            ('El tamaño de la muestra. 42 municipios son el %s %% de los %s que tiene el país. Que en esos 42 aparezca más de la mitad del monto '
             'dice mucho de esos 42, pero no permite decir cuánto «falta» en todos los municipios: la ASF revisa una muestra cada año.'
             % (pct, format(mun, ','))),
            ('Las denuncias. Las «40 denuncias» que circulan son, según la prensa, las que la ASF presentó en los seis meses de su actual '
             'titular, no las que salieron de este informe. Su estado oficial debe venir en el informe semestral de la ASF, que la ley le da '
             'hasta el 1 de noviembre (art. 38).'),
            ('Lo que sí tenemos. De la primera entrega de la Cuenta Pública 2025 (junio de 2026: 33 auditorías a la distribución de las '
             'participaciones federales), la Matriz de la ASF registra %s millones de pesos por aclarar y %s millones de recuperaciones. '
             'Esa cifra no se parece a los «600 millones» de junio que suma una de las notas: es un punto que la ASF tendrá que aclarar con '
             'su documento.' % (format(round(acl, 1), ',.1f'), format(round(rec, 1), ',.1f'))),
        ],
        'ejemplo': {
            'tit': 'Del informe a la respuesta: el reloj que corre desde el 30 de octubre',
            'txt': ('Así corren los plazos de la ley para un municipio con dinero por aclarar. Son días hábiles: sin sábados, domingos ni festivos, '
                    'así que en el calendario son bastante más.'),
            'filas': [
                ['La ASF le manda su informe', '10 días hábiles', 'LFRCF, art. 39'],
                ['El municipio responde y aporta papeles', '30 días hábiles', 'LFRCF, art. 39'],
                ['La ASF decide si lo aclarado basta', '120 días hábiles', 'LFRCF, art. 41'],
                ['En total, cuando mucho', '160 días hábiles', '10 + 30 + 120'],
            ],
            'nota': 'Es una cuenta derivada con los plazos máximos de la ley; la ASF puede resolver antes.',
        },
        'cotejo': [
            {'dice': 'La ASF reportó más de 9 mil mdp pendientes de aclarar',
             'res': 'pendiente',
             'explica': ('Varios medios lo publicaron el 30 y 31 de octubre, pero con cifras distintas (9,008 o 9,600 millones). La cifra oficial está '
                         'en la Matriz de Datos Básicos de la segunda entrega, que aún no integramos.'),
             'fuente': 'ASF, Informe del Resultado de la Cuenta Pública 2025, segunda entrega', 'url': ASF_PORTAL,
             'quien': FALTA_ASF, 'donde': ASF_PORTAL},
            {'dice': '5 mil 200 mdp corresponden a 42 municipios que no acreditaron el destino del gasto',
             'res': 'pendiente',
             'explica': ('Lo reportan varios medios (uno precisa 5,243 millones). Dos matices que sí podemos dar: «no acreditaron» significa que '
                         'al corte no presentaron documentación, y todavía tienen plazo para hacerlo; y 42 municipios son el %s %% de los %s del país '
                         '(derivado: 42 ÷ %s × 100).' % (pct, format(mun, ','), format(mun, ','))),
             'fuente': 'LFRCF, arts. 39 y 41; INEGI, padrón municipal en la base de la plataforma', 'url': LFRCF,
             'quien': FALTA_ASF, 'donde': ASF_PORTAL},
            {'dice': 'Hay 40 denuncias por obras no hechas y equipo extraviado',
             'res': 'pendiente',
             'explica': ('Según la prensa, son las denuncias que la ASF presentó en seis meses ante la Fiscalía Anticorrupción, más tres penales: '
                         'no todas salieron de este informe. Las obras no hechas y el equipo extraviado son ejemplos que dio el auditor. El estado '
                         'oficial de las denuncias va en el informe semestral de la ASF (LFRCF, art. 38).'),
             'fuente': 'ASF, informe semestral sobre la solventación de observaciones y acciones', 'url': 'informes-semestral-asf.html',
             'quien': ('Falta de la plataforma: la ASF debe publicar su informe semestral a más tardar el 1-11-2026 (LFRCF, art. 38) y '
                       'todavía no lo integramos.'), 'donde': ASF_PORTAL},
            {'dice': 'Sumados a los 600 millones de su primer paquete de informes de junio, son 9,600 millones (El Financiero)',
             'res': 'matiz',
             'explica': ('La Matriz de Datos Básicos de la primera entrega 2025 (p. 11) registra %s millones por aclarar y %s millones de '
                         'recuperaciones en sus 33 auditorías: no aparecen 600 millones. Además, el titular indexado decía «9,600 mmdp», que '
                         'serían miles de millones: mil veces más de lo que dice la propia nota.' % (format(round(acl, 1), ',.1f'), format(round(rec, 1), ',.1f'))),
             'fuente': 'ASF, Matriz de Datos Básicos de la Cuenta Pública 2025, primera entrega (jun. 2026), p. 11', 'url': ASF_MDB25A},
        ],
        'medios': [
            {'medio': 'La Jornada', 'titulo': 'Sin aclarar, 9 mil mdp de la cuenta pública 2025: ASF', 'fecha': '31-10-2026',
             'url': 'https://www.jornada.com.mx/2026/10/31/politica/006n3pol'},
            {'medio': 'El Financiero', 'titulo': 'ASF reporta gastos irregulares por 9,600 mmdp en 2025 de recursos federales; ya hay 40 denuncias',
             'fecha': '30-10-2026', 'url': 'https://www.elfinanciero.com.mx/nacional/2026/10/30/asf-reporta-gastos-irregulares-por-9600-mmdp-en-2025-de-recursos-federales-ya-hay-40-denuncias/'},
            {'medio': 'La Razón', 'titulo': 'Municipios concentran seis de cada 10 pesos pendientes de aclarar ante la ASF', 'fecha': '30-10-2026',
             'url': 'https://www.razon.com.mx/mexico/2026/10/30/municipios-concentran-seis-de-cada-10-pesos-pendientes-de-aclarar-ante-la-asf/'},
            {'medio': 'La Razón', 'titulo': 'En Cuenta Pública 2025, 9 mil mdp por aclarar; municipios, con más observaciones de ASF', 'fecha': '31-10-2026',
             'url': 'https://www.razon.com.mx/mexico/2026/10/31/en-cuenta-publica-2025-9-mil-mdp-por-aclarar-municipios-con-mas-observaciones-de-asf/'},
            {'medio': 'Excélsior', 'titulo': 'Detectan más de 5 mil 200 mdp sin comprobar en 42 municipios', 'fecha': '',
             'url': 'https://www.excelsior.com.mx/nacional/detectan-mas-5-mil-200-mdp-sin-comprobar-42-municipios'},
            {'medio': 'El Universal', 'titulo': 'Auditoría Superior identifica simulación de operaciones en gobiernos de Nuevo León y Sinaloa', 'fecha': '',
             'url': 'https://www.eluniversal.com.mx/nacion/auditoria-superior-identifica-simulacion-de-operaciones-en-nuevo-leon-y-sinaloa-funcionarios-entregan-recursos-a-familiares/'},
            {'medio': 'Infobae', 'titulo': 'Aureliano Hernández reporta 40 denuncias penales en seis meses al frente de la ASF', 'fecha': '31-10-2026',
             'url': 'https://www.infobae.com/mexico/2026/10/31/aureliano-hernandez-reporta-40-denuncias-penales-en-seis-meses-al-frente-de-la-asf-destaca-el-caso-de-nuevo-leon-y-sinaloa/'},
            {'medio': 'El Heraldo de México', 'titulo': 'La ASF ha presentado 40 denuncias en combate a la corrupción y otras tres penales en 6 meses', 'fecha': '30-10-2026',
             'url': 'https://heraldodemexico.com.mx/nacional/2026/10/30/la-asf-ha-presentado-40-denuncias-en-combate-la-corrupcion-otras-tres-penales-en-meses-919679.html'},
            {'medio': 'Político MX', 'titulo': 'ASF presenta 40 denuncias penales e indaga casos de INE y la UNAM', 'fecha': '30-10-2026',
             'url': 'https://politico.mx/2026/10/30/asf-presenta-40-denuncias-penales-e-indaga-casos-de-ine-y-la-unam/'},
            {'medio': 'MVS Noticias', 'titulo': 'ASF detecta más de 9 mil mdp por aclarar en segunda revisión de la Cuenta Pública 2025', 'fecha': '30-10-2026',
             'url': 'https://mvsnoticias.com/nacional/2026/10/30/asf-detecta-mas-de-9-mil-mdp-por-aclarar-en-segunda-revision-de-la-cuenta-publica-2025-751861.html'},
            {'medio': 'El Imparcial', 'titulo': 'La ASF detectó más de 9 mil millones de pesos pendientes de aclarar en el gasto público de 2025', 'fecha': '30-10-2026',
             'url': 'https://www.elimparcial.com/dinero/2026/10/30/la-auditoria-superior-de-la-federacion-asf-detecto-mas-de-9-mil-millones-de-pesos-pendientes-de-aclarar-en-el-gasto-publico-de-2025-el-hallazgo-mas-relevante-esta-en-los-municipios-ninguno-de-los-42-ayuntamientos-revisados-pudo-acreditar-documentalmente-el-destino-de-la-totalidad-de-los-recursos-federales-fiscalizados/'},
            {'medio': 'UnoTV', 'titulo': 'ASF detecta más de 9 mil mdp por aclarar en ejercicio 2025; investiga irregularidades en INE y OPLEs', 'fecha': '',
             'url': 'https://www.unotv.com/nacional/asf-detecta-mas-de-9-mil-mdp-por-aclarar-en-2025-investiga-irregularidades-ine-y-oples/'},
            {'medio': '24 Horas', 'titulo': 'ASF detecta más de 9 mil millones de pesos sin aclarar en los tres órdenes de gobierno', 'fecha': '',
             'url': 'https://24-horas.mx/mexico/asf-detecta-mas-de-9-mil-millones-de-pesos-sin-aclarar-en-los-tres-ordenes-de-gobierno/'},
            {'medio': 'Capital México', 'titulo': 'Detectan anomalías en el gasto público de 2025', 'fecha': '',
             'url': 'https://www.capitalmexico.com.mx/politica/detectan-anomalias-en-el-gasto-publico-de-2025/'},
        ],
        'datos': [
            {'ico': '🔎', 'tx': 'Las cifras de la ASF, entrega por entrega', 'url': 'herramienta-inspector-asf-cifras.html',
             'de': 'Auditorías, acciones, recuperaciones y montos por aclarar de la Cuenta Pública 2024 completa y la primera entrega de 2025.'},
            {'ico': '🗺️', 'tx': 'Lo que la ASF encontró en tu estado', 'url': 'herramienta-inspector-asf-estado.html',
             'de': 'El monto por aclarar de tu entidad y sus municipios, con su documento.'},
            {'ico': '📊', 'tx': 'El informe semestral de la ASF', 'url': 'informes-semestral-asf.html',
             'de': 'Cómo van las observaciones y las denuncias: el que viene se publica a más tardar el 1 de noviembre.'},
            {'ico': '📦', 'tx': 'Auditoría en imágenes: el Ramo 33', 'url': 'auditoria-ramo-33.html',
             'de': 'El dinero federal que llega a los municipios y lo que la ASF suele encontrar.'},
            {'ico': '🏘️', 'tx': 'Baja al territorio: los 2,479 municipios', 'url': 'numeros-baja-al-territorio.html',
             'de': 'Cuánto le llega a tu municipio y de qué fondos.'},
        ],
        'glosario': [g('Monto por Aclarar'), g('Informe Individual de Auditoría'), g('Pliego de Observaciones'),
                     g('Denuncia de Hechos (ASF)'), g('Auditoría Superior de la Federación (ASF)'), g('Cuenta Pública')],
        'red': 'ASF segunda entrega Cuenta Pública 2025 monto por aclarar municipios',
        'sigue': [
            {'que': 'La Matriz de Datos Básicos de la segunda entrega 2025: el monto por aclarar exacto, por entidad y por municipio', 'url': ASF_PORTAL},
            {'que': 'El informe semestral de la ASF (a más tardar el 1-11-2026): el estado de las denuncias', 'url': ASF_PORTAL},
            {'que': 'Las respuestas de los 42 municipios: lo que se aclare en los 30 días hábiles que les da la ley', 'url': LFRCF},
            {'que': 'La tercera entrega y el Informe General de la Cuenta Pública 2025 (20-02-2027)', 'url': ASF_PORTAL},
        ],
        'fuentes': [
            {'nombre': 'Ley de Fiscalización y Rendición de Cuentas de la Federación, arts. 35, 38, 39 y 41', 'url': LFRCF},
            {'nombre': 'ASF, Matriz de Datos Básicos de la Cuenta Pública 2025, primera entrega (junio de 2026), p. 11', 'url': ASF_MDB25A},
            {'nombre': 'INEGI, padrón de 2,479 municipios (EFIPEM 2024), en la base de la plataforma', 'url': 'numeros-baja-al-territorio.html'},
            {'nombre': 'ASF, portal del Informe del Resultado de la Cuenta Pública 2025', 'url': ASF_PORTAL},
            {'nombre': 'Punto de partida: @pajaropolitico (Animal Político), Instagram, 31-10-2026', 'url': PAJARO},
        ],
        'actualizado': '31-10-2026',
    }


MCCI_PORTACELIS = 'https://contralacorrupcion.mx/gobierno-de-amlo-favorecio-a-huachicolera-ligada-a-amilcar-olan/'
CPEUM = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf'
CNPP = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CNPP.pdf'
SENER = 'https://www.gob.mx/sener'
DOF_BUSCA = 'https://dof.gob.mx/'
FGR = 'https://www.gob.mx/fgr'
FALTA_SENER = ('Falta de la plataforma: MCCI dice tener copia del permiso de la Secretaría de Energía; ni esa copia ni el registro '
               'de permisos de la Sener abren desde nuestro servidor.')


def _sat69b():
    """La lista 69-B se lee de su archivo: Portacelis no debe estar."""
    t = (RAIZ / 'assets' / 'auditor' / 'data' / 'sat-69b.js').read_text(encoding='utf-8')
    meta = json.loads(t[t.index('{'):t.rindex('}') + 1])['meta']
    if 'portacelis' in t.lower():
        raise SystemExit('integrar_al_momento: Portacelis ya aparece en la lista 69-B; corrige la nota de Portacelis')
    return meta


def portacelis_diesel():
    from apartados import glosario_ancla
    m = _sat69b()
    g = lambda t: {'t': t.split(' (')[0], 'url': 'glosario.html#' + glosario_ancla(t)}
    return {
        'id': 'portacelis-permiso-diesel-sener',
        'seccion': 'Al momento',
        'icono': '🛢️',
        'fecha': '31-10-2026',
        'titulo': 'Portacelis y el permiso para importar 52 millones de litros de diésel: lo que dice MCCI, lo que consta y lo que es puro adjetivo',
        'balazo': ('Circula que el gobierno anterior dio un «permiso exprés» a una empresa «fantasma» ligada a Amílcar Olán para importar '
                   '52 millones de litros de diésel. La historia viene de una investigación de MCCI del 5 de octubre. Lo que podemos decir hoy: '
                   'el sexenio sí terminaba tres días después de la fecha del permiso; Portacelis no está en la lista de empresas fantasma del SAT; '
                   'el permiso y los litros siguen sin un documento que podamos abrir, y «narcoexpresidente» no lo sostiene ninguna acusación.'),
        'nota': {'medio': 'Mexicanos contra la Corrupción y la Impunidad (MCCI)',
                 'titulo': 'Gobierno de AMLO favoreció a huachicolera ligada a Amílcar Olán', 'fecha': '05-10-2026', 'url': MCCI_PORTACELIS},
        'circula': {'red': 'Instagram', 'cuenta': '@derechadiariomx', 'fecha': 'octubre de 2026 (unas tres semanas antes del 1 de noviembre)',
                    'texto': ('URGENTE — REGALO DE DESPEDIDA: A solo días de dejar el poder, el narcoexpresidente AMLO le otorgó un permiso exprés a la '
                              'empresa «fantasma» Portacelis, ligada al amigo íntimo de «El Andy», Amílcar Olán, para importar 52 millones de litros '
                              'de presunto diésel contrabandeado, según una investigación de MCCI.')},
        'cuerpo': [
            ('De dónde viene. La publicación de la cuenta @derechadiariomx en Instagram retoma una investigación de Mexicanos contra la Corrupción '
             'y la Impunidad (MCCI) del 5 de octubre. Según MCCI, la Secretaría de Energía autorizó el 27 de septiembre de 2024 a Portacelis Gas '
             'and Oil a importar hasta 52 millones de litros de diésel, nueve días después de endurecer sus reglas para esos permisos y cuando la '
             'empresa tenía unas semanas de creada. MCCI es una organización de periodismo de investigación: su trabajo es el punto de partida, '
             'no la fuente; el documento que manda es el permiso.'),
            ('Lo que sí consta. El sexenio terminó el 30 de septiembre de 2024: la Constitución fija que la nueva presidencia empieza el 1 de '
             'octubre (art. 83). Si el permiso es del 27, como dice MCCI, se dio a tres días del cambio. Y Portacelis no aparece en la lista del '
             'artículo 69-B del Código Fiscal, la de las empresas que el SAT considera que facturan operaciones simuladas (las llamadas «fantasma»), '
             'en nuestra copia con corte al %s.' % m['corte']),
            ('Lo que no podemos sostener todavía. El permiso mismo, su fecha, quién lo firmó y los 52 millones de litros: la copia la tiene MCCI y no '
             'abre desde nuestro servidor, ni el registro de la Sener. Tampoco los litros que la empresa habría dejado de declarar: la prensa habla de '
             '80, 83 o 90 millones, según la nota, a partir de una declaratoria del SAT ante la Fiscalía que no es pública.'),
            ('Lo que es adjetivo. «Narcoexpresidente» y «regalo de despedida» no son datos: no hay acusación, proceso ni sentencia que los sostenga, '
             'y una acusación tampoco sería una condena (Constitución, art. 20). «Fantasma», en el sentido del SAT, no consta. Y que una empresa '
             'esté «ligada» a una persona porque la administra alguien de su confianza es un vínculo que reporta MCCI, no una resolución de autoridad: '
             'según la prensa, Amílcar Olán no figura como acusado.'),
            ('Por qué importa. El llamado huachicol fiscal (meter combustible declarándolo como otra cosa, o por menos litros, para no pagar el IEPS) '
             'es dinero que deja de entrar a la hacienda pública. Si una autoridad confirma que este permiso se usó para eso, la pregunta de fondo es '
             'quién lo autorizó y con qué requisitos: eso es lo que hay que seguir.'),
        ],
        'cotejo': [
            {'dice': 'A solo días de dejar el poder… le otorgó un permiso exprés',
             'res': 'matiz',
             'explica': ('El sexenio terminó el 30-09-2024 (Constitución, art. 83), así que una fecha del 27 de septiembre sí queda a tres días. Pero el '
                         'permiso, según MCCI, lo dio la Secretaría de Energía, firmado por un director de área, no el Presidente en persona, y la '
                         'fecha misma sale de un documento que todavía no podemos abrir.'),
             'fuente': 'Constitución Política, art. 83', 'url': CPEUM},
            {'dice': 'Para importar 52 millones de litros de diésel',
             'res': 'pendiente',
             'explica': 'Es la cifra que MCCI atribuye al permiso. Sin el permiso a la vista no la podemos confirmar ni negar.',
             'fuente': 'Secretaría de Energía, permiso previo de importación de petrolíferos', 'url': MCCI_PORTACELIS,
             'quien': FALTA_SENER, 'donde': SENER},
            {'dice': 'La empresa «fantasma» Portacelis',
             'res': 'no consta',
             'explica': ('Portacelis no aparece en la lista 69-B del SAT (empresas que facturan operaciones simuladas) en nuestra copia con corte al %s, '
                         'que revisa %s contribuyentes. Que una empresa sea nueva o no tenga historial de importaciones no la vuelve «fantasma» en '
                         'el sentido de la ley.' % (m['corte'], format(m['total'], ','))),
             'fuente': m['fuente'], 'url': m['url']},
            {'dice': 'Ligada al amigo íntimo de «El Andy», Amílcar Olán',
             'res': 'no consta',
             'explica': ('Es el vínculo que reporta MCCI: la empresa la administraba una persona de confianza de Olán. No encontramos un documento '
                         'oficial (acta en el Registro Público de Comercio, resolución o acusación) que lo establezca, y según la prensa Olán no '
                         'figura como acusado.'),
             'fuente': 'MCCI, investigación del 05-10-2026 (punto de partida, no fuente)', 'url': MCCI_PORTACELIS},
            {'dice': 'Presunto diésel contrabandeado',
             'res': 'pendiente',
             'explica': ('La prensa reporta una declaratoria de perjuicio del SAT ante la FGR por litros no declarados (80, 83 o 90 millones, según el '
                         'medio). Una denuncia no es una condena. La carpeta es reservada por ley, así que nadie está obligado a publicarla todavía: '
                         'el dato público llegará con una acusación formal o una sentencia.'),
             'fuente': 'Código Nacional de Procedimientos Penales, art. 218 (reserva de la investigación)', 'url': CNPP,
             'quien': ('Nadie está obligado a publicarlo aún: las carpetas de investigación son reservadas (CNPP, art. 218). Lo hará público la FGR '
                       'si presenta una acusación formal.'), 'donde': FGR},
            {'dice': 'El narcoexpresidente AMLO',
             'res': 'no consta',
             'explica': ('Es un calificativo de quien publica. No existe una acusación, un proceso ni una sentencia por narcotráfico contra el '
                         'expresidente, y aun si existiera una acusación, no sería una condena (Constitución, art. 20, B, fr. I).'),
             'fuente': 'Constitución Política, art. 20, apartado B, fr. I (presunción de inocencia)', 'url': CPEUM},
        ],
        'medios': [
            {'medio': 'La Silla Rota', 'titulo': 'Gobierno de AMLO autorizó a firma ligada a Olán importar diesel: MCCI', 'fecha': '05-10-2026',
             'url': 'https://lasillarota.com/nacion/2026/10/5/gobierno-de-amlo-autorizo-a-firma-ligada-a-olan-importar-diesel-mcci-531479.html'},
            {'medio': 'Político MX', 'titulo': 'Gobierno de AMLO dio permiso a empresa ligada a Amílcar Olán para importar diésel', 'fecha': '05-10-2026',
             'url': 'https://politico.mx/2026/10/05/gobierno-de-amlo-dio-permiso-a-empresa-ligada-a-amilcar-olan-para-importar-diesel/'},
            {'medio': 'Aristegui Noticias', 'titulo': 'Gobierno de AMLO favoreció a presunta huachicolera ligada a Amílcar Olán', 'fecha': '05-10-2026',
             'url': 'https://aristeguinoticias.com/0510/investigaciones-especiales/gobierno-de-amlo-favorecio-a-presunta-huachicolera-ligada-a-amilcar-olan-mcci/'},
            {'medio': 'Noticaribe', 'titulo': 'Gobierno de AMLO autorizó importación de diésel a empresa ligada a Amílcar Olán pese a nuevas reglas: MCCI',
             'fecha': '05-10-2026', 'url': 'https://noticaribe.com.mx/2026/10/05/gobierno-de-amlo-autorizo-importacion-de-diesel-a-empresa-ligada-a-amilcar-olan-pese-a-nuevas-reglas-mcci/'},
            {'medio': 'Revista República', 'titulo': 'Gobierno de AMLO favoreció a presunta huachicolera ligada a Amílcar Olán', 'fecha': '06-10-2026',
             'url': 'https://revistarepublica.com/2026/10/06/gobierno-de-amlo-favorecio-a-presunta-huachicolera-ligada-a-amilcar-olan-mcci/'},
            {'medio': 'TV Azteca', 'titulo': 'A 3 días de acabar el sexenio de AMLO, la empresa ligada a Amílcar Olán obtuvo permiso irregular', 'fecha': '',
             'url': 'https://www.tvazteca.com/aztecanoticias/video-a-3-dias-acabar-el-sexenio-amlo-la-empresa-ligada-a-amilcar-olan-obtuvo-permiso-irregular'},
            {'medio': 'Forbes México', 'titulo': 'MCCI revela que empresa ligada a Amílcar Olán no declaró 80 millones de litros de diésel', 'fecha': '',
             'url': 'https://forbes.com.mx/mcci-revela-que-empresa-ligada-a-amilcar-olan-amigo-de-andy-lopez-beltran-no-declaro-80-millones-de-litros-de-diesel/'},
            {'medio': 'Político MX', 'titulo': 'Empresa ligada a Amílcar Olán, amigo de «Andy», omitió declarar 83 millones de litros de diésel', 'fecha': '07-09-2026',
             'url': 'https://politico.mx/2026/09/07/empresa-ligada-a-amilcar-olan-amigo-de-andy-omitio-declarar-83-millones-de-litros-de-diesel-sat/'},
            {'medio': 'Expreso de Tamaulipas', 'titulo': 'Destapan otro fraude millonario en las aduanas', 'fecha': '09-09-2026',
             'url': 'https://expreso.press/2026/09/09/destapan-otro-fraude-millonario-en-las-aduanas/'},
            {'medio': 'Canal 44', 'titulo': 'Señalan presuntos beneficios a huachicolera ligada a Amílcar Olán durante sexenio anterior', 'fecha': '',
             'url': 'https://canal44.com/gobierno-amlo-portacelis-presunta-huachicolera-amilcar-olan/'},
        ],
        'datos': [
            {'ico': '⛽', 'tx': 'Auditoría en imágenes: el huachicol fiscal', 'url': 'auditoria-huachicol-fiscal.html',
             'de': 'Cómo funciona el contrabando de combustible declarado como otra cosa, y lo que dicen los documentos.'},
            {'ico': '🚫', 'tx': 'La lista negra del SAT', 'url': 'herramienta-inspector-efos.html',
             'de': 'Busca cualquier empresa por nombre o RFC entre los contribuyentes del artículo 69-B.'},
            {'ico': '📑', 'tx': 'Contratos públicos', 'url': 'contratos-publicos.html',
             'de': 'Si una empresa le vendió al gobierno, ahí aparecen sus contratos de ComprasMX.'},
        ],
        'glosario': [g('Huachicol Fiscal'), g('Empresa Fantasma (EFOS)'), g('Contrabando (Delito Fiscal)'),
                     g('IEPS (Impuesto Especial sobre Producción y Servicios)')],
        'red': 'Portacelis permiso Sener diésel Amílcar Olán MCCI',
        'sigue': [
            {'que': 'El permiso previo de importación de la Sener a Portacelis: fecha, firma, volumen y requisitos', 'url': SENER},
            {'que': 'El acuerdo de la Sener publicado en el DOF el 18-09-2024 que endureció los requisitos', 'url': DOF_BUSCA},
            {'que': 'Si la FGR presenta una acusación formal por contrabando, y contra quién', 'url': FGR},
            {'que': 'La próxima actualización de la lista 69-B del SAT', 'url': m['url']},
        ],
        'fuentes': [
            {'nombre': 'Constitución Política de los Estados Unidos Mexicanos, arts. 20 y 83', 'url': CPEUM},
            {'nombre': '%s, corte al %s, en la base de la plataforma' % (m['fuente'], m['corte']), 'url': m['url']},
            {'nombre': 'Código Nacional de Procedimientos Penales, art. 218', 'url': CNPP},
            {'nombre': 'Punto de partida: MCCI, «Gobierno de AMLO favoreció a huachicolera ligada a Amílcar Olán» (05-10-2026)', 'url': MCCI_PORTACELIS},
            {'nombre': 'Lo que circula: @derechadiariomx, Instagram (octubre de 2026)', 'url': 'https://www.instagram.com/derechadiariomx/'},
        ],
        'actualizado': '01-11-2026',
    }


DSALGADO = 'https://www.instagram.com/reel/DfI6V7Ltsgh/'  # el reel del 30-10-2026 (sin el parámetro de rastreo)
ENSENADA_ENTE = 'herramienta-inspector-entes.html#ente=municipal:02001'
ENSENADA_GOB = 'https://www.ensenada.gob.mx/'
LGCG = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGCG.pdf'
FALTA_ENS = ('Falta de la plataforma: las cifras se dieron en la glosa del IMCUDHE ante el Cabildo; su desglose debe estar en la '
             'información financiera del Instituto y del Ayuntamiento (Ley General de Contabilidad Gubernamental), que no abre desde '
             'nuestro servidor.')


def _ensenada():
    """Lo que ingresó Ensenada en 2024, leído del padrón del INEGI."""
    t = (RAIZ / 'assets' / 'auditor' / 'js' / 'municipios-efipem.js').read_text(encoding='utf-8')
    i = t.index('"BC": { cve: "02"')
    j = t.index('["001","Ensenada",', i)
    r = json.loads(t[j:t.index(']', j) + 1])
    campos = ['cve', 'nombre', 'ing', 'part', 'aport', 'fortamun', 'fismdf', 'predial', 'propios', 'egr']
    if 'anio: 2024' not in t:
        raise SystemExit('integrar_al_momento: el padrón municipal ya no es de 2024; revisa la nota de Ensenada')
    return dict(zip(campos, r))


def carnaval_ensenada():
    from apartados import glosario_ancla
    e = _ensenada()
    g = lambda t: {'t': t.split(' (')[0], 'url': 'glosario.html#' + glosario_ancla(t)}
    mdp = lambda v: '$%s millones' % format(round(v / 1e6, 1), ',.1f')
    return {
        'id': 'carnaval-ensenada-2026-imcudhe',
        # Palabras propias del tema: le ganan al nombre del municipio en el chat.
        'temas': ['carnaval'],
        'seccion': 'Al momento',
        'icono': '🎭',
        'fecha': '30-10-2026',
        'titulo': 'El Carnaval de Ensenada costó más de 22 millones y recuperó 1.2: lo que se dijo ante el Cabildo y lo que falta publicar',
        'balazo': ('Una regidora cuestionó al Instituto de Cultura de Ensenada por gastar más de 22 millones de pesos en un Carnaval de seis días '
                   'que, dice, dejó 1.2 millones de «ganancia». Las cifras salieron de viva voz ante el Cabildo y todavía no tienen un documento público '
                   'que las desglose. El punto ciego: 1.2 millones no es ganancia sino lo que se recuperó, y en los 22 millones no están los '
                   'artistas estelares, que pagó un patrocinador a cambio de publicidad.'),
        'nota': {'medio': 'Ana Daniela García Salgado, regidora de Ensenada (@danielasalgadoens, Instagram)',
                 'titulo': 'Más de 22 millones de pesos en un Carnaval de seis días. ¿Y la cultura de Ensenada?',
                 'fecha': '30-10-2026', 'url': DSALGADO},
        'circula': {'red': 'Instagram (reel)', 'cuenta': '@danielasalgadoens (Ana Daniela García Salgado, regidora del Ayuntamiento de Ensenada)',
                    'fecha': '30 de octubre de 2026',
                    'texto': ('Durante la glosa del IMCUDHE, cuestionamos al director por el gasto de más de 22 millones de pesos en el Carnaval, '
                              'un evento que dejó apenas 1.2 millones de pesos de ganancia. Si el objetivo es impulsar la cultura, también hay que '
                              'hablar de prioridades. ¿Cuántos espacios culturales pudieron mejorarse? ¿Cuánto talento local pudo recibir apoyo?')},
        'cuerpo': [
            ('Qué pasó. En la glosa del informe del Instituto Municipal de Cultura y Desarrollo Humano de Ensenada (IMCUDHE) ante el Cabildo, '
             'la regidora Ana Daniela García Salgado cuestionó a su director, Rodrigo Ventura de la Cabada, por lo que costó el Carnaval 2026. '
             'Según la prensa local, el Instituto reportó alrededor de 22.7 millones de pesos de gasto; otra nota da 22.3 millones. La diferencia, '
             'de unos 400 mil pesos, no se ha explicado.'),
            ('El punto ciego de la «ganancia». Si se gastaron 22 millones y entraron 1.2, el Carnaval no dejó una ganancia: recuperó una parte '
             'pequeña de lo que costó, y el resto lo pagó el presupuesto público. La palabra importa: un evento cultural puede justificarse aunque '
             'no gane dinero, pero entonces hay que medirlo por lo que logró, y eso es lo que pide la regidora.'),
            ('Lo que no está en los 22 millones. Los artistas estelares, según el director, los pagó una empresa privada con un esquema de patrocinio, '
             'a cambio de exponer sus marcas. Cuánto valió ese patrocinio no se ha dicho, y según la regidora el procedimiento del donativo no pasó '
             'por el Cabildo. Un patrocinio con contraprestación tampoco es un regalo: es un trato que debería constar por escrito.'),
            ('El presupuesto. Según la prensa, el Presupuesto 2026 le asignó 16 millones al Carnaval y después hubo una ampliación de 11 millones, '
             'que la regidora dice haber votado porque se le informó que habría recaudación y donaciones formales. Cuando el Ayuntamiento publique '
             'su información financiera, se podrá ver cuánto se aprobó, cuánto se amplió y cuánto se gastó en realidad.'),
            ('Para darte la escala, con datos oficiales: Ensenada ingresó %s en 2024, de los cuales %s fueron ingresos propios (lo que cobra el '
             'municipio por su cuenta) y %s, predial (INEGI, finanzas municipales 2024, cifras definitivas).' % (mdp(e['ing']), mdp(e['propios']), mdp(e['predial']))),
        ],
        'ejemplo': {
            'tit': 'Así se compone el dinero de Ensenada (2024)',
            'txt': 'Lo que ingresó el municipio en un año, según el INEGI. El Carnaval se paga de esta bolsa.',
            'filas': [
                ['Ingresos totales', mdp(e['ing']), 'INEGI, EFIPEM 2024'],
                ['Ingresos propios', mdp(e['propios']), 'INEGI, EFIPEM 2024'],
                ['Participaciones federales', mdp(e['part']), 'INEGI, EFIPEM 2024'],
                ['Aportaciones federales (Ramo 33)', mdp(e['aport']), 'INEGI, EFIPEM 2024'],
                ['Predial', mdp(e['predial']), 'INEGI, EFIPEM 2024'],
            ],
            'nota': 'Pesos de 2024 redondeados a millones. Las cifras del Carnaval no entran aquí porque todavía no tienen documento.',
        },
        'cotejo': [
            {'dice': 'El gasto de más de 22 millones de pesos en el Carnaval',
             'res': 'pendiente',
             'explica': ('Lo informó el IMCUDHE ante el Cabildo, según la prensa, que da dos cifras: 22.7 y 22.3 millones. Ninguna incluye a los artistas '
                         'estelares, pagados por un patrocinador.'),
             'fuente': 'IMCUDHE, información financiera del Carnaval 2026', 'url': ENSENADA_GOB,
             'quien': FALTA_ENS, 'donde': ENSENADA_GOB},
            {'dice': 'Un evento que dejó apenas 1.2 millones de pesos de ganancia',
             'res': 'matiz',
             'explica': ('Aunque la cifra se confirme, no es una ganancia: es lo que se recuperó (taquilla, permisos, patrocinios) frente a lo que se '
                         'gastó. Una ganancia sería lo que queda después de cubrir todo el gasto, y aquí faltaron más de 20 millones. La cifra misma '
                         'la reporta una sola nota y sigue pendiente de documento.'),
             'fuente': 'Ley General de Contabilidad Gubernamental (ingresos y egresos se registran por separado)', 'url': LGCG},
            {'dice': 'Un Carnaval de seis días',
             'res': 'pendiente',
             'explica': 'Las fechas del programa oficial del Carnaval 2026 no abren desde nuestro servidor.',
             'fuente': 'Ayuntamiento de Ensenada, programa del Carnaval 2026', 'url': ENSENADA_GOB,
             'quien': 'Falta de la plataforma: el portal del Ayuntamiento de Ensenada no abre desde nuestro servidor.', 'donde': ENSENADA_GOB},
        ],
        'medios': [
            {'medio': 'El Imparcial', 'titulo': 'Ayuntamiento de Ensenada cambia versión sobre patrocinio de artistas del Carnaval 2026', 'fecha': '30-10-2026',
             'url': 'https://www.elimparcial.com/tij/ensenada/2026/10/30/ayuntamiento-de-ensenada-cambia-version-sobre-patrocinio-de-artistas-del-carnaval-2026/'},
            {'medio': 'El Vigía', 'titulo': 'Pagan artistas del Carnaval con un «donativo» privado', 'fecha': '30-10-2026',
             'url': 'https://www.elvigia.net/general/2026/10/30/pagan-artistas-del-carnaval-con-un-donativo-privado-477929.html'},
            {'medio': 'CNR Noticias', 'titulo': 'Reportan gasto de 22.7 millones en el Carnaval, pero no aclaran cuánto costaron los artistas estelares', 'fecha': '',
             'url': 'https://www.cnrnoticias.tv/noticiacnr/reportan-gasto-de-22-7-millones-en-el-carnaval-pero-no-aclaran-cu%C3%A1nto-costaron-los-artistas-estelar'},
            {'medio': 'El Imparcial', 'titulo': 'Critican presunta opacidad en 2 años de Carnaval de Ensenada', 'fecha': '07-10-2026',
             'url': 'https://www.elimparcial.com/tij/ensenada/2026/10/07/critican-presunta-opacidad-de-claudia-agaton-en-2-anos-de-carnaval-de-ensenada/'},
            {'medio': 'El Vigía', 'titulo': 'Anuncian oficialmente Carnaval de Ensenada', 'fecha': '14-02-2026',
             'url': 'https://www.elvigia.net/general/2026/2/14/anuncian-oficialmentecarnaval-de-ensenada-494893.html'},
            {'medio': 'El Imparcial (columna)', 'titulo': 'Carnaval de gastos', 'fecha': '12-03-2026',
             'url': 'https://www.elimparcial.com/tij/columnas/2026/03/12/carnaval-de-gastos/'},
            {'medio': 'AFN Tijuana (editorial)', 'titulo': 'Carnaval de dudas', 'fecha': '',
             'url': 'https://afntijuana.info/editoriales/173388_carnaval_de_dudas'},
        ],
        'datos': [
            {'ico': '🏙️', 'tx': 'Ensenada en el Auditor de entes', 'url': ENSENADA_ENTE,
             'de': 'Su estado de cuenta, su salud financiera y lo que la ASF le ha observado.'},
            {'ico': '🏘️', 'tx': 'Baja al territorio: los 2,479 municipios', 'url': 'numeros-baja-al-territorio.html',
             'de': 'Cuánto le llega a tu municipio y cuánto cobra por su cuenta.'},
        ],
        'glosario': [g('Hacienda Municipal'), g('Adecuación Presupuestaria'), g('Impuesto Predial'), g('Solicitud de Acceso a la Información')],
        'red': 'Carnaval Ensenada 2026 gasto IMCUDHE',
        'sigue': [
            {'que': 'El estado del ejercicio del presupuesto del IMCUDHE con el gasto del Carnaval 2026, partida por partida', 'url': ENSENADA_GOB},
            {'que': 'El convenio de patrocinio con la empresa que pagó a los artistas: qué dio y qué recibió a cambio', 'url': ENSENADA_GOB},
            {'que': 'El acta de Cabildo de la ampliación presupuestal del Carnaval', 'url': ENSENADA_GOB},
            {'que': 'La cuenta pública 2026 de Ensenada y su revisión por la Auditoría Superior de Baja California', 'url': 'https://www.asebc.gob.mx/'},
        ],
        'fuentes': [
            {'nombre': 'INEGI, Estadística de Finanzas Públicas Estatales y Municipales 2024, cifras definitivas (Ensenada)', 'url': 'https://www.inegi.org.mx/programas/finanzas/'},
            {'nombre': 'Ley General de Contabilidad Gubernamental', 'url': LGCG},
            {'nombre': 'Punto de partida: Ana Daniela García Salgado (@danielasalgadoens), Instagram, 30-10-2026', 'url': DSALGADO},
        ],
        'actualizado': '01-11-2026',
    }


JORNADA_NL = 'https://www.jornada.com.mx/2026/10/31/estados/021n1est'


def _estado(ab):
    E = auditorias.db()['estados']
    return next(e for e in E if e['abbr'] == ab)


def asf_nuevo_leon():
    from apartados import glosario_ancla
    nl, sin = _estado('NL'), _estado('SIN')
    g = lambda t: {'t': t.split(' (')[0], 'url': 'glosario.html#' + glosario_ancla(t)}
    m = lambda v: '$%s millones' % format(round(v, 1), ',.1f')
    return {
        'id': 'asf-nuevo-leon-triangulacion-cp2025',
        'seccion': 'Al momento',
        'icono': '🔎',
        'fecha': '31-10-2026',
        'temas': ['samuel garcia', 'triangulacion'],
        'titulo': 'La ASF denuncia una presunta triangulación de 7 mil 200 millones en Nuevo León: lo que dice, lo que falta y por qué «desvió» todavía no es un hecho',
        'balazo': ('Según la prensa, la Auditoría Superior presentó ante la Fiscalía una denuncia por una presunta triangulación de más de 7 mil millones '
                   'de pesos desde el gobierno de Nuevo León, que llegaría en parte a un despacho ligado a la familia del gobernador Samuel García. '
                   'Es una de las revisiones de la segunda entrega de la Cuenta Pública 2025. Una denuncia no es una condena, las cifras no coinciden '
                   'entre medios y el documento de la ASF todavía no lo podemos abrir.'),
        'nota': {'medio': 'La Jornada', 'titulo': 'Samuel García desvió 7 mil 200 mdp, denuncia la ASF', 'fecha': '31-10-2026', 'url': JORNADA_NL},
        'circula': {'red': 'Instagram', 'cuenta': '@lajornadaonline (La Jornada)', 'fecha': '31 de octubre de 2026',
                    'texto': ('Samuel García desvió 7 mil 200 millones de pesos, denuncia la Auditoría Superior de la Federación. La administración del '
                              'gobernador de Nuevo León transfirió 5 mil 851 millones de pesos a una constructora. García compró una propiedad de mil '
                              'millones de pesos. Reporte de cuenta pública 2025 incluye investigación contra Rubén Rocha.')},
        'cuerpo': [
            ('Qué pasó. Con la segunda entrega de la revisión de la Cuenta Pública 2025 (30 de octubre), varios medios reportaron que la ASF '
             'presentó una denuncia penal por una presunta triangulación desde el gobierno de Nuevo León: el dinero habría pasado del gobierno a una '
             'constructora, de ahí a otra empresa y, en parte, a un despacho jurídico que la prensa liga a la familia del gobernador Samuel García. '
             'Es la misma entrega de la nota sobre los 9 mil millones por aclarar.'),
            ('Las cifras no coinciden. Todos los medios dicen «7 mil 200 millones» y «5 mil 851 millones a una constructora», pero lo que habría '
             'llegado al despacho cambia según la nota: 385.3 millones en unas, 928.13 millones en otras. Hasta tener el informe individual de la ASF, '
             'esas cifras son lo que reporta la prensa.'),
            ('«Desvió» es una conclusión que todavía no existe. La ASF denuncia; quien investiga es la Fiscalía y quien decide es un juez. Mientras '
             'tanto, rige la presunción de inocencia (Constitución, art. 20). Y hay un paso más que casi nadie explica: para proceder penalmente contra '
             'un gobernador en funciones por un delito federal, la Cámara de Diputados tiene que hacer una declaración de procedencia, que se comunica '
             'al Congreso del estado (Constitución, art. 111).'),
            ('La propiedad de mil millones. Que el gobernador comprara una propiedad de ese valor con este dinero lo dice la prensa; no encontramos un '
             'documento oficial abierto que lo sostenga.'),
            ('Sinaloa. Según La Jornada, el mismo reporte incluye una investigación relacionada con el gobierno de Rubén Rocha Moya; otras notas dicen '
             'que la constructora también movió recursos hacia personas cercanas a él. No hay detalle oficial que podamos abrir.'),
            ('Para darte la escala, con datos oficiales: en 2026 la Federación le reparte a Nuevo León %s de participaciones (Ramo 28) y %s de '
             'aportaciones (Ramo 33), según los acuerdos de distribución publicados en el Diario Oficial.' % (m(nl['ramo28']), m(nl['ramo33']))),
        ],
        'ejemplo': {
            'tit': 'Lo que la Federación le reparte a Nuevo León y a Sinaloa en 2026',
            'txt': 'Participaciones y aportaciones de 2026, de los acuerdos de distribución del Diario Oficial que ya están en la plataforma.',
            'filas': [
                ['Nuevo León: participaciones (Ramo 28)', m(nl['ramo28']), 'DOF, acuerdo de distribución 2026'],
                ['Nuevo León: aportaciones (Ramo 33)', m(nl['ramo33']), 'DOF, acuerdo de distribución 2026'],
                ['Sinaloa: participaciones (Ramo 28)', m(sin['ramo28']), 'DOF, acuerdo de distribución 2026'],
                ['Sinaloa: aportaciones (Ramo 33)', m(sin['ramo33']), 'DOF, acuerdo de distribución 2026'],
            ],
            'nota': 'Millones de pesos de 2026. No es lo que se auditó: la ASF revisa el gasto de 2025.',
        },
        'cotejo': [
            {'dice': 'La ASF denuncia 7 mil 200 millones de pesos',
             'res': 'pendiente',
             'explica': ('Varios medios coinciden en que la ASF presentó una denuncia ante la Fiscalía por una presunta triangulación de esa cantidad. '
                         'El informe individual que lo sostiene es de la segunda entrega de la Cuenta Pública 2025 y todavía no lo integramos.'),
             'fuente': 'ASF, informe individual de la Cuenta Pública 2025 (Nuevo León)', 'url': ASF_PORTAL,
             'quien': FALTA_ASF, 'donde': ASF_PORTAL},
            {'dice': 'Samuel García desvió…',
             'res': 'no consta',
             'explica': ('Es la conclusión del titular, no de la ASF: lo que hay, según la prensa, es una denuncia. Una denuncia no es una condena '
                         '(Constitución, art. 20), y contra un gobernador en funciones se necesita además una declaración de procedencia de la Cámara de '
                         'Diputados (art. 111).'),
             'fuente': 'Constitución Política, arts. 20 y 111', 'url': CPEUM},
            {'dice': 'Transfirió 5 mil 851 millones de pesos a una constructora',
             'res': 'pendiente',
             'explica': 'Lo dicen todos los medios que lo citan; el detalle de las transferencias está en el informe de la ASF, que no podemos abrir.',
             'fuente': 'ASF, informe individual de la Cuenta Pública 2025 (Nuevo León)', 'url': ASF_PORTAL,
             'quien': FALTA_ASF, 'donde': ASF_PORTAL},
            {'dice': 'García compró una propiedad de mil millones de pesos',
             'res': 'no consta',
             'explica': 'Solo lo dice la prensa. No encontramos un documento oficial abierto (informe, denuncia publicada o registro) que lo sostenga.',
             'fuente': 'La Jornada, 31-10-2026 (punto de partida, no fuente)', 'url': JORNADA_NL},
            {'dice': 'Reporte de cuenta pública 2025 incluye investigación contra Rubén Rocha',
             'res': 'pendiente',
             'explica': ('Según la prensa, la misma revisión encontró operaciones ligadas al gobierno de Sinaloa. No sabemos si la ASF lo presenta como '
                         'investigación contra el gobernador o sobre recursos de su gobierno: eso lo dice el informe.'),
             'fuente': 'ASF, informes individuales de la Cuenta Pública 2025 (Sinaloa)', 'url': ASF_PORTAL,
             'quien': FALTA_ASF, 'donde': ASF_PORTAL},
        ],
        'medios': [
            {'medio': 'Norte Digital', 'titulo': 'Denuncia ASF a Samuel García por presunta triangulación de 7.2 mmdp', 'fecha': '',
             'url': 'https://nortedigital.mx/denuncia-asf-a-samuel-garcia-por-presunta-triangulacion-de-7-2-mmdp/'},
            {'medio': 'Eje Central', 'titulo': 'ASF denuncia a Samuel García por presunto desvío de 7 mil 200 millones de pesos en Nuevo León; esto se sabe', 'fecha': '',
             'url': 'https://www.ejecentral.com.mx/nuestro-eje/asf-denuncia-a-samuel-garcia-por-presunto-desvio-de-7-mil-200-millones-de-pesos-en-nuevo-leon-esto-se-sabe'},
            {'medio': 'La Jornada de Oriente', 'titulo': 'Samuel García, gobernador de Nuevo León, desvió 7 mil 200 mdp, denuncia la ASF', 'fecha': '',
             'url': 'https://www.lajornadadeoriente.com.mx/puebla/asf-denuncia-triangulacion-7200-millones-samuel-garcia/'},
            {'medio': 'SDP Noticias', 'titulo': 'ASF denuncia presunta triangulación de 7 mil 200 mdp en gobierno de Samuel García', 'fecha': '',
             'url': 'https://www.sdpnoticias.com/estados/nuevo-leon/asf-denuncia-presunta-triangulacion-de-7-mil-200-mdp-en-gobierno-de-samuel-garcia/'},
            {'medio': 'Proyecto Puente', 'titulo': 'Acusan a Samuel García por presunto desvío de 7 mil 200 mdp', 'fecha': '31-10-2026',
             'url': 'https://proyectopuente.com.mx/2026/10/31/acusan-a-samuel-garcia-por-presunto-desvio-de-7-mil-200-mdp'},
            {'medio': 'Platino News', 'titulo': 'Samuel García habría desviado 7 mil 200 MDP según la ASF', 'fecha': '',
             'url': 'https://platino.news/samuel-garcia-habria-desviado-7-mil-200-mdp-segun-la-asf/'},
            {'medio': 'Cadena Política', 'titulo': 'Samuel García, gobernador de Nuevo León, bajo investigación por la ASF', 'fecha': '31-10-2026',
             'url': 'https://cadenapolitica.com/2026/10/31/samuel-garcia-gobernador-de-nuevo-leon-denuncia-asf-desvios/'},
        ],
        'datos': [
            {'ico': '🔎', 'tx': 'La segunda entrega de la ASF: los 9 mil millones por aclarar', 'url': AL_MOMENTO_PAG % 'asf-segunda-entrega-cp2025',
             'de': 'La misma entrega, con los municipios, los plazos para aclarar y las denuncias.'},
            {'ico': '🗺️', 'tx': 'Nuevo León en el Auditor de entes', 'url': 'herramienta-inspector-entes.html#ente=estatal:NL',
             'de': 'Su estado de cuenta, su salud financiera y lo que la ASF le ha observado.'},
            {'ico': '🗺️', 'tx': 'Sinaloa en el Auditor de entes', 'url': 'herramienta-inspector-entes.html#ente=estatal:SIN',
             'de': 'Lo mismo, para Sinaloa.'},
        ],
        'glosario': [g('Denuncia de Hechos (ASF)'), g('Informe Individual de Auditoría'), g('Auditoría Superior de la Federación (ASF)'),
                     g('Ramo 28 (Participaciones Federales)'), g('Ramo 33 (Aportaciones Federales)')],
        'red': 'ASF denuncia Nuevo León triangulación Samuel García Cuenta Pública 2025',
        'sigue': [
            {'que': 'El informe individual de la ASF sobre Nuevo León: montos, empresas y el camino del dinero', 'url': ASF_PORTAL},
            {'que': 'Si la FGR pide a la Cámara de Diputados la declaración de procedencia (Constitución, art. 111)', 'url': 'https://gaceta.diputados.gob.mx/'},
            {'que': 'El informe individual sobre Sinaloa', 'url': ASF_PORTAL},
            {'que': 'La respuesta del gobierno de Nuevo León a las observaciones (30 días hábiles, LFRCF art. 39)', 'url': LFRCF},
        ],
        'fuentes': [
            {'nombre': 'Constitución Política de los Estados Unidos Mexicanos, arts. 20 y 111', 'url': CPEUM},
            {'nombre': 'Acuerdos de distribución de participaciones y aportaciones 2026 (DOF), en la base de la plataforma', 'url': 'numeros-mapa-del-gasto-federalizado.html'},
            {'nombre': 'Ley de Fiscalización y Rendición de Cuentas de la Federación, art. 39', 'url': LFRCF},
            {'nombre': 'Punto de partida: La Jornada, «Samuel García desvió 7 mil 200 mdp, denuncia la ASF» (31-10-2026)', 'url': JORNADA_NL},
        ],
        'actualizado': '01-11-2026',
    }



LATINUS_DNR = ('https://latinus.us/mexico/2026/10/12/'
               'en-dos-horas-diputados-de-la-4t-asignan-18-mil-millones-de-pesos-mas-para-tren-maya-aifa-en-2027-186856.html')
DERECHA = 'https://www.instagram.com/derechadiariomx/'
GACETA_DIP = 'https://gaceta.diputados.gob.mx/'
LFD_INICIATIVA = 'https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-D.pdf'
PAQ_GASTO = 'numeros-paquete-2027-gasto.html'
DNR_DEFENSA, DNR_INM, DNR_TESO = 57, 15, 28   # Canal del Congreso, 10318 (14-10-2026)
DNR_ANTES = 50                                 # lo que tenía la Defensa antes de la reserva: solo la prensa
FALTA_DICT = ('Falta de la plataforma: el dictamen de la Ley Federal de Derechos 2027 y su reserva están en la Gaceta '
              'Parlamentaria, que no abre desde nuestra sesión.')


def _megaobras_2027():
    """Lo que la base ya sabe del Tren Maya y del AIFA: su operación de 2024 (Cuenta Pública) y la inversión que
    el Paquete 2027 propone para el Tren Maya (CGPE 2027, p. 33). Se lee, no se copia."""
    d = auditorias.db()
    op = d['simulador_megaobras']['operacion_oficial']
    tm, af = op['obras']['tren-maya'], op['obras']['aifa-texcoco']
    inv = {f['n']: f['m'] for f in d['paquete_2027']['inversion']['filas']}
    if 'Tren Maya' not in inv:
        raise SystemExit('integrar_al_momento: el Paquete 2027 de la base ya no trae la inversión del Tren Maya')
    for o in (tm, af):
        if o['anio'] != 2024:
            raise SystemExit('integrar_al_momento: la operación del Tren Maya o del AIFA cambió de año; revisa la nota del DNR')
    return tm, af, inv['Tren Maya'], op['fuentes']


def lfd_dnr_defensa():
    from apartados import glosario_ancla
    g = lambda t: {'t': t.split(' (')[0], 'url': 'glosario.html#' + glosario_ancla(t)}
    tm, af, inv_tm, F = _megaobras_2027()
    m1 = lambda v: '$%s millones' % format(round(v, 1), ',.1f')
    par = lambda k: DNR_2027 * k / 100
    return {
        'id': 'lfd-2027-dnr-defensa-tren-maya-aifa',
        'seccion': 'Al momento',
        'icono': '✈️',
        'temas': ['tren maya y el aifa', 'tren maya y al aifa', 'tren maya y aifa', 'no residente'],
        'fecha': '01-11-2026',
        'titulo': ('¿18 mil millones «en subsidios» para el Tren Maya y el AIFA? Es el cobro a los turistas extranjeros, '
                   'y el 57 % es la parte de la Defensa, no un aumento'),
        'balazo': ('Circula que Morena aprobó en dos horas más de 18 mil millones de pesos en subsidios para el Tren Maya y el AIFA, '
                   '«un aumento del 57 %». Lo que se votó fue la Ley Federal de Derechos 2027: lo que pagan los turistas extranjeros al '
                   'entrar sube a 1,158 pesos, y de lo que se junte, el 57 % irá a la Defensa, que opera los dos proyectos. El 57 % es '
                   'una parte, no un aumento, y los 18 mil millones son un cálculo de prensa que ningún documento abierto confirma.'),
        'nota': {'medio': 'Latinus', 'titulo': 'En dos horas, diputados de la 4T asignan 18 mil millones de pesos más para Tren Maya y AIFA en 2027',
                 'fecha': '12-10-2026', 'url': LATINUS_DNR},
        'circula': {'red': 'Instagram', 'cuenta': '@derechadiariomx', 'fecha': 'octubre de 2026 (unas dos semanas antes del 1 de noviembre)',
                    'texto': ('DESPILFARRO EXPRÉS: Los diputados de Morena aprobaron, en solo dos horas, más de 18 mil millones de pesos en '
                              'subsidios para los proyectos más fracasados de AMLO: el Tren Maya y el AIFA. El gasto sería a partir del 2027 y '
                              'representa un aumento del 57 % para intentar levantar las obras faraónicas.')},
        'cuerpo': [
            ('Qué se votó. No fue el Presupuesto de Egresos: fue la Ley Federal de Derechos para 2027, la que fija lo que el Estado cobra '
             'por un servicio o por usar un bien público. La Cámara de Diputados la aprobó en el pleno el 14 de octubre, según el Canal del '
             'Congreso. Entre sus cambios, el Derecho de No Residente (lo que paga el extranjero que entra a México sin permiso para trabajar, '
             'el turista) sube %s %% y queda en %s pesos, y lo que se recaude se reparte %d %% para la Defensa, %d %% para el Instituto '
             'Nacional de Migración y %d %% para la Tesorería.' % (DNR_SUBE, format(DNR_2027, ','), DNR_DEFENSA, DNR_INM, DNR_TESO)),
            ('Las «dos horas». Lo rápido fue la sesión de la Comisión de Hacienda del 12 de octubre: ahí, según la prensa, una reserva de '
             'Morena subió la parte de la Defensa de %d %% a %d %%. Luego votó el pleno, y la prensa reporta 339 votos a favor, más de los que '
             'tiene Morena sola, y que el Senado la aprobó el 27 de octubre. La versión del pleno y la del Senado todavía no las pudimos abrir.'
             % (DNR_ANTES, DNR_DEFENSA)),
            ('El punto ciego: el 57 %% no es un aumento. Es la parte de la recaudación que le toca a la Defensa. Si antes era el %d %%, como '
             'dicen los medios, subió %d puntos: con el mismo dinero recaudado, la Defensa recibiría %d %% más (%d ÷ %d), no 57 %% más. '
             'Esa cuenta usa un dato de prensa, así que no la damos como derivado. Y no es un subsidio aprobado en el Presupuesto: es dinero que pagan los turistas extranjeros y que la '
             'ley manda a una dependencia. Cuánto llega depende de cuántos visitantes entren en 2027.'
             % (DNR_ANTES, DNR_DEFENSA - DNR_ANTES, round(100 * (DNR_DEFENSA - DNR_ANTES) / DNR_ANTES), DNR_DEFENSA - DNR_ANTES, DNR_ANTES)),
            ('Los 18 mil millones. Es una estimación de Latinus, y la prensa no dice si son todo lo que recibiría la Defensa o solo lo '
             'adicional. Ni la Ley de Ingresos ni la nota oficial del Congreso que pudimos leer traen cuánto se espera juntar con este derecho. '
             'Ojo con otro «18 mil»: la prensa también reporta unos 18 mil millones en transferencias federales para el Tren Maya en el '
             'proyecto de Presupuesto 2027, que es otra bolsa y otra ley. En la base tenemos lo que ese proyecto prevé invertir en el Tren Maya: '
             '%s, según los Criterios Generales 2027.' % m1(inv_tm)),
            ('«Los proyectos más fracasados». Es un adjetivo. Con sus propios estados de la Cuenta Pública 2024, el Tren Maya cobró %s por '
             'operar y gastó %s: sin lo que le transfirió el gobierno (%s), perdía %s. El AIFA, en cambio, cobró %s y gastó %s: sus ingresos '
             'por operar le alcanzaron, y aun así recibió %s de transferencias, con las que pagó nómina y servicios. Esos números no cuentan '
             'lo que costó construirlos.'
             % (m1(tm['ingresos_gestion']), m1(tm['gastos_totales']), m1(tm['transferencias']), m1(-tm['resultado_sin_transferencias']),
                m1(af['ingresos_gestion']), m1(af['gastos_totales']), m1(af['transferencias']))),
        ],
        'ejemplo': {
            'tit': 'La cuenta, con un turista',
            'txt': 'De cada pago de %s pesos de un turista extranjero en 2027:' % format(DNR_2027, ','),
            'filas': [['Defensa (opera el Tren Maya y el AIFA)', '$%.2f' % par(DNR_DEFENSA), '%s × %d %%' % (format(DNR_2027, ','), DNR_DEFENSA)],
                      ['Instituto Nacional de Migración', '$%.2f' % par(DNR_INM), '%s × %d %%' % (format(DNR_2027, ','), DNR_INM)],
                      ['Tesorería de la Federación', '$%.2f' % par(DNR_TESO), '%s × %d %%' % (format(DNR_2027, ','), DNR_TESO)]],
            'nota': ('Es un ejemplo derivado con la cuota y el reparto que reportó el Canal del Congreso. Cuánto suma en el año depende de '
                     'cuántos visitantes entren, y ese pronóstico no viene en ningún documento que pudimos abrir.'),
        },
        'cotejo': [
            {'dice': 'Los diputados de Morena aprobaron', 'res': 'matiz',
             'explica': ('La reserva que subió la parte de la Defensa fue de Morena, según la prensa, pero quien aprobó la ley fue el pleno de '
                         'la Cámara de Diputados el 14 de octubre, y la prensa reporta 339 votos a favor, con los de sus aliados.'),
             'fuente': 'Canal del Congreso, «Cámara de Diputados aprueba Ley Federal de Derechos 2027» (14-10-2026)', 'url': CANAL_LFD},
            {'dice': 'En solo dos horas', 'res': 'pendiente',
             'explica': ('La prensa lo dice de la sesión de la Comisión de Hacienda del 12 de octubre. La duración consta en su versión '
                         'estenográfica, que no pudimos abrir. Y no fue la única votación: después votaron el pleno y el Senado.'),
             'fuente': 'Latinus (12-10-2026), punto de partida, no fuente', 'url': LATINUS_DNR,
             'quien': FALTA_DICT, 'donde': GACETA_DIP},
            {'dice': 'Más de 18 mil millones de pesos', 'res': 'pendiente',
             'explica': ('Es un cálculo de prensa sobre lo que se recaudaría con este derecho. Ningún documento que pudimos abrir dice cuánto se '
                         'espera juntar en 2027, ni si los 18 mil millones son todo lo de la Defensa o solo lo adicional.'),
             'fuente': 'Iniciativa de reforma a la Ley Federal de Derechos 2027 (Gaceta Parlamentaria 7121, Anexo D)', 'url': LFD_INICIATIVA,
             'quien': FALTA_DICT, 'donde': GACETA_DIP},
            {'dice': 'En subsidios para el Tren Maya y el AIFA', 'res': 'matiz',
             'explica': ('No es un subsidio del Presupuesto: es la parte de un derecho que pagan los turistas extranjeros y que la ley '
                         'manda a la Defensa (%d %%), dependencia que opera los dos proyectos. Si el texto de la ley obliga a gastarlo en ellos '
                         'lo dirá el decreto publicado.' % DNR_DEFENSA),
             'fuente': 'Canal del Congreso (14-10-2026)', 'url': CANAL_LFD},
            {'dice': 'Representa un aumento del 57 %', 'res': 'no consta',
             'explica': ('El 57 %% es la parte de la recaudación que va a la Defensa, no un aumento. Si antes era el %d %%, como dice la prensa, '
                         'subió %d puntos, que son %d %% más; esa cuenta usa el dato de prensa. La cuota misma sube %s %%.'
                         % (DNR_ANTES, DNR_DEFENSA - DNR_ANTES, round(100 * (DNR_DEFENSA - DNR_ANTES) / DNR_ANTES), DNR_SUBE)),
             'fuente': 'Canal del Congreso (14-10-2026)', 'url': CANAL_LFD},
            {'dice': 'El gasto sería a partir del 2027', 'res': 'consta',
             'explica': 'Es la Ley Federal de Derechos del ejercicio 2027: rige desde el 1 de enero, una vez publicada en el Diario Oficial.',
             'fuente': 'Canal del Congreso (14-10-2026)', 'url': CANAL_LFD},
            {'dice': 'Los proyectos más fracasados de AMLO… obras faraónicas', 'res': 'matiz',
             'explica': ('Son adjetivos. Los números de 2024: el Tren Maya gastó %s y cobró %s por operar; el AIFA cobró %s y gastó %s. '
                         'Uno pierde al operar y el otro no, y ninguno de esos números incluye lo que costó construirlo.'
                         % (m1(tm['gastos_totales']), m1(tm['ingresos_gestion']), m1(af['ingresos_gestion']), m1(af['gastos_totales']))),
             'fuente': F['ef_h0m']['doc'], 'url': F['ef_h0m']['url']},
        ],
        'medios': [
            {'medio': 'Latinus', 'titulo': 'En dos horas, diputados de la 4T asignan 18 mil millones de pesos más para Tren Maya y AIFA en 2027',
             'fecha': '12-10-2026', 'url': LATINUS_DNR},
            {'medio': 'Noticaribe', 'titulo': 'Aprueban en comisiones Ley Federal de Derechos: diputados reducen alza al Derecho de No Residente, '
             'pero aún así lo elevan a mil 158 pesos para 2027', 'fecha': '12-10-2026',
             'url': 'https://noticaribe.com.mx/2026/10/12/aprueban-en-comisiones-ley-federal-de-derechos-diputados-reducen-alza-al-derecho-de-no-residente-pero-aun-asi-lo-elevan-a-mil-158-pesos-para-2027/'},
            {'medio': 'Expansión', 'titulo': 'Diputados: alzas a derechos de extranjeros y vía ferroviaria', 'fecha': '12-10-2026',
             'url': 'https://expansion.mx/economia/2026/10/12/diputados-alzas-derechos-extranjeros-via-ferroviaria'},
            {'medio': 'Expansión', 'titulo': 'Alzas en cuotas para turistas, aeronaves y trenes, y medidores de agua obligatorios avanzan en Ley de Derechos 2027',
             'fecha': '13-10-2026', 'url': 'https://expansion.mx/economia/2026/10/13/ley-derechos-2027-alzas-cuotas-turistas-aereo-vias-ferreas'},
            {'medio': 'Quadratín Chihuahua', 'titulo': 'Destinarían 18 mil millones de pesos en subsidios al Tren Maya y al AIFA durante 2027', 'fecha': '',
             'url': 'https://chihuahua.quadratin.com.mx/nacionales/destinarian-18-mil-millones-de-pesos-en-subsidios-al-tren-maya-y-al-aifa-durante-2027/'},
            {'medio': 'La Onda Oaxaca', 'titulo': 'Morena aprueba aumentar recursos para la Sedena; estiman 18 mil millones de pesos adicionales para '
             'proyectos como el Tren Maya y el AIFA', 'fecha': '',
             'url': 'https://www.laondaoaxaca.com.mx/2026/10/morena-aprueba-aumentar-recursos-para-la-sedena-estiman-18-mil-millones-de-pesos-adicionales-para-proyectos-como-el-tren-maya-y-el-aifa'},
            {'medio': 'Entorno Político', 'titulo': 'Diputados reducen cuota a turistas extranjeros y elevan recursos para Tren Maya y AIFA', 'fecha': '',
             'url': 'https://www.entornopolitico.com/nota.php?id=240128'},
            {'medio': 'Semanario ZETA', 'titulo': 'Cámara de Diputados aprueba la Ley Federal de Derechos 2027 con alzas en salud, turismo y aviación',
             'fecha': '', 'url': 'https://zetatijuana.com/2026/10/camara-de-diputados-aprueba-la-ley-federal-de-derechos-2027-con-alzas-en-salud-turismo-y-aviacion/'},
            {'medio': 'Expansión', 'titulo': 'Senado aprueba Ley de Ingresos y Ley de Derechos', 'fecha': '27-10-2026',
             'url': 'https://expansion.mx/economia/2026/10/27/senado-aprueba-ley-ingresos-derechos'},
            {'medio': 'Crónica', 'titulo': 'Aprueba Senado Ley de Derechos para 2027; alerta oposición endeudamiento para el país', 'fecha': '27-10-2026',
             'url': 'https://www.cronica.com.mx/nacional/2026/10/27/aprueba-senado-ley-de-derechos-para-2027-alerta-oposicion-endeudamiento-para-el-pais/'},
        ],
        'datos': [
            {'ico': '🚆', 'tx': 'Auditoría en imágenes: el Tren Maya', 'url': 'auditoria-tren-maya.html',
             'de': 'Lo que costó, lo que observó la ASF y lo que pierde al operar.'},
            {'ico': '🛫', 'tx': 'Auditoría en imágenes: el AIFA', 'url': 'auditoria-aifa.html',
             'de': 'Su costo, sus pasajeros y lo que el gobierno le transfiere por cada uno.'},
            {'ico': '📊', 'tx': 'Inversión y Megaobras: el estado de resultados de cada obra', 'url': 'herramienta-megaobras-sector.html#obra-tren-maya',
             'de': 'Verde lo que entra, rojo lo que sale, en pesos de su año y de hoy.'},
            {'ico': '🏗️', 'tx': 'El gasto del Paquete 2027', 'url': PAQ_GASTO,
             'de': 'Las prioridades de inversión de 2027, con el Tren Maya entre los trenes.'},
            {'ico': '🔍', 'tx': 'La Ley de Ingresos 2027 en el Senado', 'url': 'noticias-auditavision.html#col-senado-ley-de-ingresos-2027',
             'de': 'La otra mitad del paquete: cuánto entra, cuánto es deuda y la cuota del turista.'},
        ],
        'glosario': [g('Derechos (Contribución)'), g('Empresas Públicas del Estado'), g('Paquete Económico')],
        'red': 'Derecho de No Residente 2027 57 por ciento Defensa Tren Maya AIFA',
        'sigue': [
            {'que': 'El decreto de la Ley Federal de Derechos 2027 en el Diario Oficial: si obliga a gastar el 57 % en el Tren Maya y el AIFA',
             'url': DOF_BUSCA},
            {'que': 'El dictamen y la versión estenográfica de la Comisión de Hacienda del 12 de octubre: la reserva y su duración', 'url': GACETA_DIP},
            {'que': 'El Presupuesto de Egresos 2027 (a más tardar el 15 de noviembre): las transferencias al Tren Maya y al AIFA', 'url': PPEF},
            {'que': 'La Cuenta Pública 2027: cuánto juntó de verdad este derecho y cuánto recibió la Defensa', 'url': CUENTA_PUBLICA},
        ],
        'fuentes': [
            {'nombre': 'Canal del Congreso: Cámara de Diputados aprueba Ley Federal de Derechos 2027 (14-10-2026)', 'url': CANAL_LFD},
            {'nombre': 'Iniciativa de reforma a la Ley Federal de Derechos 2027, Gaceta Parlamentaria 7121, Anexo D (08-09-2026)', 'url': LFD_INICIATIVA},
            {'nombre': F['ef_h0m']['doc'], 'url': F['ef_h0m']['url']},
            {'nombre': F['ef_hzi']['doc'], 'url': F['ef_hzi']['url']},
            {'nombre': 'Criterios Generales de Política Económica 2027, p. 33 (prioridades de inversión), en la base de la plataforma', 'url': PAQ_GASTO},
            {'nombre': 'Punto de partida: Latinus, «En dos horas, diputados de la 4T asignan 18 mil millones…» (12-10-2026)', 'url': LATINUS_DNR},
            {'nombre': 'Lo que circula: @derechadiariomx, Instagram (octubre de 2026)', 'url': DERECHA},
        ],
        'actualizado': '01-11-2026',
    }



PEMEX_RI = 'https://www.pemex.com/'
BMV = 'https://www.bmv.com.mx/'
EFE_PEMEX = 'https://www.infobae.com/america/agencias/2026/10/30/pemex-pierde-605-millones-de-dolares-en-tercer-trimestre-de-2026-pese-a-mayores-ingresos/'
EXP_PEMEX = 'https://expansion.mx/empresas/2026/10/30/pemex-perdidas-tercer-trimestre-2026-ingresos-deuda'
FALTA_PEMEX = ('Falta de la plataforma: Pemex publica sus resultados trimestrales en su portal de relación con inversionistas y los '
               'entrega a la Bolsa Mexicana de Valores; ninguno de los dos abre desde nuestra sesión.')


def _pemex():
    """Lo que la base ya sabe de Pemex: su gasto y su costo financiero en el PEF 2026 (Anexo 1) y el apoyo del
    Ramo 18 de 2026 y 2027 (CGPE 2027). Se lee, no se copia."""
    d = auditorias.db()
    a1 = d['panoramaErario']['anexo1PEF2026']
    em = [g for g in a1['grupos'] if g['clave'] == 'E'][0]['ramos']
    prog = [r for r in em if r['nombre'] == 'Petróleos Mexicanos'][0]['pesos'] / 1e6
    fin = [r for r in em if r['nombre'] == 'Petróleos Mexicanos · costo financiero'][0]['pesos'] / 1e6
    cp = [c for c in d['paquete_2027']['ciegos'] if c['id'] == 'c-pemex'][0]
    if '263,476.0' not in cp['documento'] or '81,100.0' not in cp['documento']:
        raise SystemExit('integrar_al_momento: cambió el punto ciego c-pemex del Paquete 2027; revisa la nota de Pemex')
    return prog, fin, a1


def pemex_3t_2026():
    from apartados import glosario_ancla
    g = lambda t: {'t': t.split(' (')[0], 'url': 'glosario.html#' + glosario_ancla(t)}
    prog, fin, a1 = _pemex()
    m1 = lambda v: '$%s millones' % format(round(v, 1), ',.1f')
    tot = prog + fin
    return {
        'id': 'pemex-3t-2026-perdida-neta',
        'seccion': 'Al momento',
        'icono': '🛢️',
        'temas': ['tercer trimestre', 'perdio pemex', 'pierde pemex', 'perdida de pemex', 'perdida neta de pemex'],
        'fecha': '01-11-2026',
        'titulo': 'Pemex vuelve a perder en el tercer trimestre: ¿10,792 o 10,795 millones?, y lo que esa pérdida no cuenta',
        'balazo': ('Circula que Pemex perdió 10 mil 792 millones de pesos entre julio y septiembre, 82.4 %% menos que un año antes, por '
                   'más ventas y menos deterioro de activos. La mayoría de los medios da 10,795 millones, y el reporte de Pemex no abre '
                   'desde la plataforma: la cifra queda pendiente. La cuenta del 82.4 %% sí cuadra con las dos versiones, y lo que casi '
                   'nadie dice es cuánto le cuestan al erario los intereses de Pemex: %s en 2026.' % m1(fin)),
        'nota': {'medio': 'EFE (vía Infobae)', 'titulo': 'Pemex pierde 605 millones de dólares en tercer trimestre de 2026 pese a mayores ingresos',
                 'fecha': '30-10-2026', 'url': EFE_PEMEX},
        'circula': {'red': 'Instagram', 'cuenta': 'un medio que remite a «el link de nuestra bio» (la publicación no trae el nombre de la cuenta)',
                    'fecha': '30 de octubre de 2026',
                    'texto': ('La estatal Petróleos Mexicanos (Pemex) reportó este viernes una pérdida neta de 10 mil 792 millones de pesos '
                              '(605 millones de dólares) durante el tercer trimestre. Esto representa un 82.4 % menos que los 61 mil 247 millones '
                              'de pesos registrados en el mismo periodo del año pasado; esto se debió a un incremento en ventas y disminución en '
                              'deterioro de activos.')},
        'cuerpo': [
            ('Qué pasó. Pemex entregó el viernes 30 de octubre su reporte del tercer trimestre de 2026 (julio a septiembre). Según la '
             'prensa, regresó a los números rojos después de la utilidad del segundo trimestre: perdió unos 10.8 mil millones de pesos. El '
             'reporte mismo, en el portal de Pemex y en la Bolsa Mexicana de Valores, no abre desde la plataforma, así que todas las cifras '
             'de esta nota que vienen de la prensa van como pendientes.'),
            ('El primer punto ciego: ¿10,792 o 10,795? La publicación dice 10,792 millones, igual que Industry & Energy Magazine. EFE y '
             'Expansión dicen 10,795. Para el mismo trimestre de 2025 la publicación dice 61,247 millones y otros medios, 61,242. Son '
             'diferencias chicas, pero dos cifras distintas no pueden ser las dos «la de Pemex»: manda el reporte.'),
            ('La cuenta del 82.4 % cuadra. Con las cifras de la publicación, 10,792 ÷ 61,247 = 0.176: la pérdida es 82.4 % menor. Con las '
             'otras, 10,795 ÷ 61,242 también da 82.4 %. Y los dólares son una conversión: 605 millones de dólares implican unos 17.8 pesos '
             'por dólar; otro medio convirtió a 596.9 millones. Pemex reporta en pesos.'),
            ('Lo que la pérdida no cuenta. «Perdió menos» no quiere decir «ya no cuesta». En el Presupuesto de 2026, Pemex tiene %s de gasto '
             'programable y %s más de costo financiero, los intereses de su deuda: de cada 100 pesos que el Presupuesto le asigna, %.1f son '
             'intereses (derivado). Y en 2026 el Ramo 18 le dio a la política de hidrocarburos 263,476.0 millones; para 2027 se proponen '
             '81,100.0 millones, según los Criterios Generales.' % (m1(prog), m1(fin), 100 * fin / tot)),
            ('Por qué perdió, según la prensa. EFE cita a la directora de Finanzas: la pérdida cambiaria fue de 16,391 millones, porque el '
             'peso se depreció en el trimestre, y los ingresos subieron 28.5 %. Si eso es así, sin el efecto del tipo de cambio el trimestre '
             'habría salido positivo; pero es una cuenta con cifras de prensa, así que no la damos como derivado. Y «menos deterioro» quiere '
             'decir que Pemex le restó menos valor a sus activos que hace un año: es un registro contable, no dinero que entró.'),
        ],
        'ejemplo': {
            'tit': 'La cuenta, con números redondos',
            'txt': 'Si el Presupuesto 2026 de Pemex fueran 100 pesos:',
            'filas': [['Para operar e invertir (gasto programable)', '$%.0f' % (100 * prog / tot), '%s ÷ %s × 100' % (m1(prog), m1(tot))],
                      ['Para pagar intereses de su deuda (costo financiero)', '$%.0f' % (100 * fin / tot), '%s ÷ %s × 100' % (m1(fin), m1(tot))]],
            'nota': 'Es un ejemplo derivado con el Anexo 1 del Decreto de Presupuesto de Egresos 2026, que la plataforma tiene en su base.',
        },
        'cotejo': [
            {'dice': 'Pemex reportó una pérdida neta de 10 mil 792 millones de pesos en el tercer trimestre', 'res': 'pendiente',
             'explica': ('Casi todos los medios dan 10,795 millones (EFE, Expansión) y solo uno 10,792. Manda el reporte de Pemex a la Bolsa, '
                         'que no pudimos abrir.'),
             'fuente': 'Pemex, Reporte de resultados al 30 de septiembre de 2026', 'url': PEMEX_RI,
             'quien': FALTA_PEMEX, 'donde': BMV},
            {'dice': '(605 millones de dólares)', 'res': 'pendiente',
             'explica': ('Es una conversión: 605 millones de dólares equivalen a unos 17.8 pesos por dólar. Otro medio convirtió a 596.9 millones. '
                         'El tipo de cambio que usó Pemex vendrá en su reporte.'),
             'fuente': 'Pemex, Reporte de resultados al 30 de septiembre de 2026', 'url': PEMEX_RI,
             'quien': FALTA_PEMEX, 'donde': BMV},
            {'dice': 'Un 82.4 % menos que los 61 mil 247 millones del mismo periodo del año pasado', 'res': 'pendiente',
             'explica': ('La resta cuadra con las dos versiones de la prensa (10,792 contra 61,247, o 10,795 contra 61,242: 82.4 % menos en las '
                         'dos), pero las dos cifras de partida siguen sin documento abierto.'),
             'fuente': 'Pemex, reportes de resultados del tercer trimestre de 2025 y de 2026', 'url': PEMEX_RI,
             'quien': FALTA_PEMEX, 'donde': BMV},
            {'dice': 'Se debió a un incremento en ventas y disminución en deterioro de activos', 'res': 'pendiente',
             'explica': ('La prensa reporta ingresos 28.5 % más altos y una pérdida cambiaria de 16,391 millones. El deterioro de activos es un '
                         'registro contable: si baja, la pérdida se achica aunque no entre más dinero. El desglose está en el reporte.'),
             'fuente': 'Pemex, Reporte de resultados al 30 de septiembre de 2026', 'url': PEMEX_RI,
             'quien': FALTA_PEMEX, 'donde': BMV},
        ],
        'medios': [
            {'medio': 'EFE (vía Infobae)', 'titulo': 'Pemex pierde 605 millones de dólares en tercer trimestre de 2026 pese a mayores ingresos',
             'fecha': '30-10-2026', 'url': EFE_PEMEX},
            {'medio': 'Expansión', 'titulo': 'Pemex pierde 10,795 millones de pesos, aunque reduce su deuda financiera y con proveedores',
             'fecha': '30-10-2026', 'url': EXP_PEMEX},
            {'medio': 'Industry & Energy Magazine', 'titulo': 'Pemex pierde 10 mil 792 millones de pesos, pese a aumentar 28.5 % sus ingresos en el 3T',
             'fecha': '', 'url': 'https://energymagazine.mx/2026/10/pemex-pierde-10-mil-792-millones-de-pesos-pese-a-aumentar-28-5-sus-ingresos/'},
            {'medio': 'MVS Noticias', 'titulo': 'Pierde Pemex 605 millones de dólares en tercer trimestre de 2026', 'fecha': '30-10-2026',
             'url': 'https://mvsnoticias.com/economia/2026/10/30/pierde-pemex-605-millones-de-dolares-en-tercer-trimestre-de-2026-751799.html'},
            {'medio': 'Energy21', 'titulo': 'Pierde Pemex 10.8 mil mdp en el tercer trimestre de 2026', 'fecha': '',
             'url': 'https://energy21.com.mx/pierde-pemex-10-mil-mdp-en-el-tercer-trimestre-de-2026/'},
            {'medio': 'Uniradio Informa', 'titulo': 'Pemex reporta pérdida neta de 10 mil 800 mdp en tercer trimestre', 'fecha': '',
             'url': 'https://www.uniradioinforma.com/negocios/pemex-reporta-perdida-neta-10-mil-800-mdp-tercer-trimestre-n911631'},
            {'medio': 'ABC Noticias', 'titulo': 'Pierde Pemex más de 10 mil mdp en tercer trimestre de 2026', 'fecha': '30-10-2026',
             'url': 'https://abcnoticias.mx/nacional/2026/10/30/pierde-pemex-mas-de-10-mil-mdp-en-tercer-trimestre-de-2026-294001.html'},
            {'medio': 'Energía a Debate', 'titulo': 'Vuelve Pemex a resultados negativos en el 3T', 'fecha': '',
             'url': 'https://energiaadebate.com/vuelve-pemex-a-resultados-negativos-en-el-3t'},
        ],
        'datos': [
            {'ico': '💸', 'tx': 'El costo financiero: lo que se paga de intereses', 'url': 'numeros-egreso-costo-financiero.html',
             'de': 'Cuánto se va en intereses de la deuda del país, de Pemex y de la CFE.'},
            {'ico': '🔦', 'tx': 'Los puntos ciegos del Paquete 2027', 'url': 'numeros-paquete-2027-puntos-ciegos.html',
             'de': 'Entre ellos, por qué los 81 mil millones para Pemex no son un apoyo nuevo.'},
            {'ico': '🏭', 'tx': 'Auditoría en imágenes: Dos Bocas', 'url': 'auditoria-dos-bocas.html',
             'de': 'La refinería de Pemex: lo que costó, lo que pagó su filial y lo que observó la ASF.'},
            {'ico': '⛽', 'tx': 'Auditoría en imágenes: el huachicol fiscal', 'url': 'auditoria-huachicol-fiscal.html',
             'de': 'El combustible que entra sin pagar lo que debe: dinero que deja de llegar al erario.'},
        ],
        'glosario': [g('Pérdida Neta (Resultado Neto)'), g('Deterioro de Activos'), g('Costo Financiero de la Deuda'),
                     g('Empresas Públicas del Estado')],
        'red': 'Pemex pérdida neta tercer trimestre 2026 reporte de resultados',
        'sigue': [
            {'que': 'El reporte de resultados del tercer trimestre en la Bolsa: la pérdida exacta, el tipo de cambio y el deterioro', 'url': BMV},
            {'que': 'El saldo de la deuda financiera de Pemex al 30 de septiembre (lo que la plataforma todavía no tiene)',
             'url': 'pendientes.html#pemex-deuda'},
            {'que': 'El Presupuesto de Egresos 2027 (a más tardar el 15 de noviembre): cuánto queda del apoyo del Ramo 18', 'url': PPEF},
            {'que': 'La Cuenta Pública 2026: lo que Pemex ejerció y lo que pagó de intereses', 'url': CUENTA_PUBLICA},
        ],
        'fuentes': [
            {'nombre': '%s, pp. %s, en la base de la plataforma' % (a1['fuente'], a1['paginas']), 'url': a1['url']},
            {'nombre': 'Criterios Generales de Política Económica 2027 (Ramo 18), en la base de la plataforma',
             'url': 'numeros-paquete-2027-puntos-ciegos.html'},
            {'nombre': 'Pendiente: Pemex, Reporte de resultados al 30 de septiembre de 2026 (portal de Pemex y Bolsa Mexicana de Valores)',
             'url': BMV},
            {'nombre': 'Punto de partida: EFE, «Pemex pierde 605 millones de dólares en tercer trimestre de 2026…» (30-10-2026)', 'url': EFE_PEMEX},
        ],
        'actualizado': '01-11-2026',
    }



SERV_POST = 'https://www.instagram.com/p/DfAF4OKsLkv/'   # sin el parámetro de rastreo
IMAGEN_SERV = 'https://www.imagenradio.com.mx/finanzas/exportacion-servidores-podria-superar-autos-mexico-alcanza-82-mil-900-mdd'
EXC_SERV = 'https://www.excelsior.com.mx/nacional/ensamblar-futuro'
DCD_MEXDC = 'https://www.datacenterdynamics.com/es/noticias/m%C3%A9xico-prev%C3%A9-atraer-82500-millones-de-d%C3%B3lares-en-centros-de-datos/'
INEGI_BALANZA = 'https://www.inegi.org.mx/temas/balanza/'
INEGI_VAEMG = 'https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/pibval/VAEMG2024_CP.pdf'
QRO_ENTE = 'herramienta-inspector-entes.html#ente=estatal:QRO'
FALTA_INEGI = ('Falta de la plataforma: el INEGI publica la balanza comercial por producto y el valor agregado de exportación por '
               'rama; su portal no abre desde nuestra sesión.')


def servidores_exportacion():
    q = _estado('QRO')
    m1 = lambda v: '$%s millones' % format(round(v, 1), ',.1f')
    return {
        'id': 'servidores-ia-exportaciones-contenido-nacional',
        'seccion': 'Al momento',
        'icono': '🖥️',
        'temas': ['exportacion de servidores', 'exportaciones de servidores', 'exportamos servidores', 'exporta servidores',
                  'servidores de ia', 'servidores para ia', 'centros de datos', 'data centers', 'contenido nacional'],
        'fecha': '01-11-2026',
        'titulo': ('¿México ya exporta más servidores que autos? Lo dice una consultora privada, no el INEGI, y el «3 a 7 % mexicano» '
                   'no tiene documento'),
        'balazo': ('Circula que en el primer semestre de 2026 México exportó 82,900 millones de dólares en servidores, más que en autos '
                   '(74,800), pero que de cada 100 dólares solo 3 a 7 son mexicanos, contra 39 en el automotriz. Las cifras de exportación '
                   'son de S&P Global y comparan contra autos y autopartes juntos; el contenido mexicano es una estimación sin documento '
                   'oficial, y los 82,500 millones para centros de datos son la proyección de un gremio, no inversión comprometida.'),
        'nota': {'medio': 'Imagen Radio', 'titulo': 'Exportación de servidores podría superar a la de autos en México; alcanza 82 mil 900 mdd',
                 'fecha': '', 'url': IMAGEN_SERV},
        'circula': {'red': 'Instagram', 'cuenta': 'publicación con liga (la pieza no trae el nombre de la cuenta)', 'fecha': 'octubre de 2026',
                    'texto': ('Dato: en el primer semestre de 2026 exportamos $82,900 MDD en servidores, superando autos ($74,800 MDD), pero de '
                              'cada $100 del servidor solo $3-7 son mexicanos vs 39 % que ya logra el sector automotriz. 93.9 % va a un solo '
                              'cliente: EEUU. Proyección: el valor no está en la caja; está en subir ese contenido de 7 % a 30-40 %… y en '
                              'capturar los $82,500 MDD que vienen para data centers en México a 2031.')},
        'cuerpo': [
            ('De dónde salen las cifras. Los 82,900 millones de dólares de servidores en el primer semestre, los 74,800 de autos y el '
             '93.9 % que va a Estados Unidos los publicó S&P Global Market Intelligence, una consultora privada, según la prensa. La cifra '
             'oficial es la balanza comercial del INEGI por producto, y no abre desde la plataforma: por eso todas quedan pendientes.'),
            ('El primer punto ciego: «superando autos» compara contra autos y autopartes juntos, y es un semestre. La misma consultora '
             'dice que, de mantenerse el ritmo, los servidores «podrían» superar a todo el sector en el año completo: todavía no ha pasado. '
             'Y exportar mucho no es lo mismo que ganar mucho: si casi todo lo de adentro se importa, lo que se queda en el país es el '
             'ensamble.'),
            ('El segundo: el «3 a 7 % mexicano» no tiene documento. Lo publicó Excélsior como estimación. La medida oficial más cercana es el '
             'valor agregado de exportación de la manufactura global del INEGI, que para computadoras y equipo periférico ubicaría el '
             'contenido nacional en 21 % en 2024, según otra nota de prensa. Son cosas distintas: una habla de servidores de 2026 y la otra '
             'de toda la rama en 2024. El 39 % del automotriz tampoco pudimos abrirlo.'),
            ('El tercero: los 82,500 millones «que vienen» para centros de datos son la proyección de la Asociación Mexicana de Data Centers '
             '(MEXDC) para 2026 a 2031: unos 20,630 millones de inversión directa y 61,890 indirecta. Es un gremio de la industria, no un '
             'compromiso de inversión, y es dinero privado: no pasa por el Presupuesto.'),
            ('Dónde toca el dinero público. Lo que sí le cuesta al erario son la energía y el agua que esos centros necesitan, y los '
             'incentivos fiscales que se les den. Querétaro, el estado que más centros de datos concentra, recaudó %s por su cuenta y '
             'depende en %.1f %% del dinero federal, según su ficha en la plataforma. «Pasar de taller de ensamble a arquitectos de '
             'infraestructura» es una propuesta, no un dato: no se coteja.' % (m1(q['recaudacionPropia']), q['dep'])),
        ],
        'cotejo': [
            {'dice': 'En el primer semestre de 2026 exportamos 82,900 millones de dólares en servidores', 'res': 'pendiente',
             'explica': ('La cifra es de S&P Global Market Intelligence, una consultora privada, según la prensa. La oficial es la balanza '
                         'comercial del INEGI por producto, que no pudimos abrir.'),
             'fuente': 'INEGI, Balanza comercial de mercancías de México', 'url': INEGI_BALANZA,
             'quien': FALTA_INEGI, 'donde': INEGI_BALANZA},
            {'dice': 'Superando autos (74,800 millones de dólares)', 'res': 'pendiente',
             'explica': ('Según la prensa, los 74,800 son autos y autopartes juntos, y la comparación es de un semestre: la consultora dice que '
                         'podrían superarlos en el año completo. Sin la balanza del INEGI no lo podemos confirmar.'),
             'fuente': 'INEGI, Balanza comercial de mercancías de México', 'url': INEGI_BALANZA,
             'quien': FALTA_INEGI, 'donde': INEGI_BALANZA},
            {'dice': 'De cada 100 dólares del servidor solo 3 a 7 son mexicanos, contra 39 % del automotriz', 'res': 'pendiente',
             'explica': ('Es una estimación publicada por la prensa, sin documento oficial. La medida del INEGI, el valor agregado de '
                         'exportación de la manufactura global, ubicaría el contenido nacional de computadoras y periféricos en 21 % en '
                         '2024, según otra nota: es otra medida, de otro año y de toda la rama.'),
             'fuente': 'INEGI, Valor agregado de exportación de la manufactura global 2024', 'url': INEGI_VAEMG,
             'quien': FALTA_INEGI, 'donde': INEGI_VAEMG},
            {'dice': '93.9 % va a un solo cliente: Estados Unidos', 'res': 'pendiente',
             'explica': 'También es de S&P Global, según la prensa. El destino de las exportaciones por producto lo publica el INEGI.',
             'fuente': 'INEGI, Balanza comercial de mercancías de México', 'url': INEGI_BALANZA,
             'quien': FALTA_INEGI, 'donde': INEGI_BALANZA},
            {'dice': 'Los 82,500 millones de dólares que vienen para data centers en México a 2031', 'res': 'pendiente',
             'explica': ('Es la proyección de la Asociación Mexicana de Data Centers para 2026 a 2031 (directa más indirecta), no una '
                         'inversión comprometida ni un dato oficial. Lo comprometido se sabría por los anuncios registrados ante la '
                         'Secretaría de Economía y por la inversión extranjera directa que reporta.'),
             'fuente': 'Secretaría de Economía, Inversión extranjera directa', 'url': 'https://www.gob.mx/se',
             'quien': ('Ni la Secretaría de Economía ni otra dependencia publica una cifra oficial de inversión en centros de datos: la '
                       'única proyección es la de un gremio privado.'), 'donde': 'https://www.gob.mx/se'},
        ],
        'medios': [
            {'medio': 'Instagram (la publicación que circula)', 'titulo': 'Dato: H1 2026 exportamos $82,900 MDD en servidores, superando autos',
             'fecha': '', 'url': SERV_POST},
            {'medio': 'Imagen Radio', 'titulo': 'Exportación de servidores podría superar a la de autos en México; alcanza 82 mil 900 mdd', 'fecha': '',
             'url': IMAGEN_SERV},
            {'medio': 'Excélsior', 'titulo': 'México ensambla el futuro de otros; exporta más servidores para la IA que automóviles', 'fecha': '',
             'url': EXC_SERV},
            {'medio': 'Dossier Político', 'titulo': 'México ensambla el futuro de otros; exporta más servidores para la IA que automóviles',
             'fecha': '19-10-2026', 'url': 'https://dossierpolitico.com/2026/10/19/mexico-ensambla-el-futuro-de-otros-exporta-mas-servidores-para-la-ia-que-automoviles/'},
            {'medio': 'El Diario', 'titulo': 'México exporta más servidores, pero sigue dependiendo de EEUU', 'fecha': '28-09-2026',
             'url': 'https://diario.mx/opinion/2026/sep/28/mexico-exporta-mas-servidores-pero-sigue-dependiendo-de-eeuu-1140623.html'},
            {'medio': 'El Financiero (Bloomberg Businessweek)', 'titulo': 'Boom de exportaciones y crecimiento mediocre', 'fecha': '03-09-2026',
             'url': 'https://www.elfinanciero.com.mx/bloomberg-businessweek/2026/09/03/boom-de-exportaciones-y-crecimiento-mediocre/'},
            {'medio': 'El Insurgente MX', 'titulo': 'Exportaciones de equipo de cómputo crecen 182.1 %, pero contenido nacional es solo 21 %', 'fecha': '',
             'url': 'https://elinsurgentemx.mx/exportaciones-de-equipo-de-computo-crecen-182-1-pero-contenido-nacional-es-solo-21'},
            {'medio': 'Merca2.0', 'titulo': 'Mientras la industria automotriz pierde velocidad, México encuentra un nuevo motor: las exportaciones de servidores para IA',
             'fecha': '', 'url': 'https://www.merca20.com/mientras-la-industria-automotriz-pierde-velocidad-mexico-encuentra-un-nuevo-motor-para-su-economia-las-exportaciones-de-servidores-para-ia-se-disparan/'},
            {'medio': 'DCD (DatacenterDynamics)', 'titulo': 'México prevé atraer 82,500 millones de dólares en centros de datos', 'fecha': '',
             'url': DCD_MEXDC},
            {'medio': 'Mexico Business News', 'titulo': 'Mexico Targets US$82.5 Billion Data Center Buildout Through 2031', 'fecha': '',
             'url': 'https://mexicobusiness.news/cloudanddata/news/mexico-targets-us825-billion-data-center-buildout-through-2031'},
        ],
        'datos': [
            {'ico': '🏛️', 'tx': 'La ficha de Querétaro en el Auditor de entes', 'url': QRO_ENTE,
             'de': 'Su estado de cuenta, su salud financiera y lo que la ASF le observó.'},
            {'ico': '📊', 'tx': 'Las 32 entidades', 'url': 'numeros-las-32-entidades.html',
             'de': 'Cuánto recauda cada estado por su cuenta y cuánto depende de la Federación.'},
        ],
        'glosario': [],
        'red': 'exportaciones servidores México 2026 contenido nacional S&P Global INEGI',
        'sigue': [
            {'que': 'La balanza comercial del INEGI por producto: cuánto se exportó de verdad en servidores y en autos', 'url': INEGI_BALANZA},
            {'que': 'El valor agregado de exportación 2025 del INEGI: el contenido nacional de cómputo y del automotriz', 'url': INEGI_VAEMG},
            {'que': 'Los incentivos fiscales y la energía que el gobierno comprometa para centros de datos', 'url': DOF_BUSCA},
        ],
        'fuentes': [
            {'nombre': 'La base: ficha de Querétaro (recaudación propia y dependencia del dinero federal)', 'url': QRO_ENTE},
            {'nombre': 'Pendiente: INEGI, Balanza comercial de mercancías de México', 'url': INEGI_BALANZA},
            {'nombre': 'Pendiente: INEGI, Valor agregado de exportación de la manufactura global 2024', 'url': INEGI_VAEMG},
            {'nombre': 'Punto de partida: Imagen Radio, con datos de S&P Global Market Intelligence', 'url': IMAGEN_SERV},
            {'nombre': 'Lo que circula: publicación en Instagram (octubre de 2026)', 'url': SERV_POST},
        ],
        'actualizado': '01-11-2026',
    }



GOBMX_AGUA = 'https://www.instagram.com/p/DfDZtTIH9Nx/'   # sin parámetros de rastreo
PRES_2810 = ('https://www.gob.mx/presidencia/prensa/gobierno-de-mexico-invertira-14-mil-500-mdp-para-garantizar-agua-en-guadalajara-'
             'sin-deuda-ni-privatizacion-presidenta-claudia-sheinbaum')
EXP_AGUA = 'https://politica.expansion.mx/presidencia/2026/10/28/crisis-agua-guadalajara-inversion-acueductos'
JORNADA_AGUA = ('https://www.jornada.com.mx/noticia/2026/10/28/estados/gobierno-federal-invertira-14-mil-millones-y-el-de-jalisco-'
                '10-mil-200-millones-para-suministrar-agua-limpia-en-guadalajara')
CONAGUA = 'https://www.gob.mx/conagua'
AGUA_FED_2810 = 14500       # Presidencia, comunicado del 28-10-2026 (título, visto por el buscador)
CRISIS = 'herramienta-ambiente-crisis.html'
FALTA_AGUA = ('Falta de la plataforma: el comunicado de Presidencia y la versión estenográfica del 28 de octubre están en gob.mx, '
              'que no abre desde nuestra sesión; solo pudimos ver su título.')


def _acueducto_jal():
    """El costo del Acueducto Chapala–Guadalajara que el Gobierno de Jalisco puso en su iniciativa (crisis_ambientales.py)."""
    t = (RAIZ / 'herramientas' / 'crisis_ambientales.py').read_text(encoding='utf-8')
    if "('El Acueducto Chapala–Guadalajara', 11922.0" not in t:
        raise SystemExit('integrar_al_momento: cambió el costo del acueducto en crisis_ambientales.py; revisa la nota del agua')
    return 11922.0


def agua_guadalajara_federal():
    from apartados import glosario_ancla
    g = lambda t: {'t': t.split(' (')[0], 'url': 'glosario.html#' + glosario_ancla(t)}
    P = _paquete()
    acu = _acueducto_jal()
    deuda = P['total'] - P['ing']
    m0 = lambda v: '$%s millones' % format(round(v), ',')
    return {
        'id': 'agua-guadalajara-14500-federal',
        'seccion': 'Al momento',
        'icono': '🚰',
        'temas': ['agua de guadalajara', 'agua en guadalajara', 'agua potable', 'acueducto', 'chapala', 'san gaspar', 'siapa'],
        'fecha': '01-11-2026',
        'titulo': ('El agua de Guadalajara: la Federación anuncia 14,500 millones «sin deuda», pero el dinero todavía no aparece en el '
                   'Presupuesto 2027'),
        'balazo': ('El Gobierno de México dice que invertirá 14 mil 500 millones de pesos en obras de agua para la zona metropolitana de '
                   'Guadalajara sin endeudarse. El anuncio es oficial; el dinero, todavía no: según la prensa, no vendrá etiquetado en el '
                   'Presupuesto 2027. Hace una semana la cifra era de 12 a 13 mil millones, y la calidad del agua sigue sin resultados de '
                   'laboratorio publicados.'),
        'nota': {'medio': 'Presidencia de la República (comunicado)',
                 'titulo': 'Gobierno de México invertirá 14 mil 500 mdp para garantizar agua en Guadalajara sin deuda ni privatización',
                 'fecha': '28-10-2026', 'url': PRES_2810},
        'circula': {'red': 'Instagram', 'cuenta': '@gobmexico (Gobierno de México)', 'fecha': '29 de octubre de 2026 (tres días antes del 1 de noviembre)',
                    'texto': ('Reafirmamos el compromiso con la población de la zona metropolitana de Guadalajara para garantizar agua potable '
                              'de calidad; el gobierno federal invierte 14 mil 500 millones de pesos para consolidar obras hidráulicas sin '
                              'adquirir deuda.')},
        'cuerpo': [
            ('Qué se anunció. El 28 de octubre, la Presidenta y el gobernador Pablo Lemus presentaron el plan: la Federación pone 14 mil 500 '
             'millones y Jalisco unos 10 mil 200, según la prensa. Lo federal lo ejercería la Conagua: 9 mil 300 millones para el acueducto '
             'Chapala–Guadalajara y 5 mil 200 para el sistema Calderón–San Gaspar. Las obras empezarían a principios de 2027 y las grandes '
             'terminarían hacia finales de 2028; la operación seguiría con el SIAPA. El texto completo del comunicado no abre desde la '
             'plataforma: el desglose y las fechas van como pendientes.'),
            ('El primer punto ciego: «invierte» todavía es «invertirá». El comunicado oficial lo dice en futuro, y según Expansión la '
             'Presidenta explicó que los recursos no vendrán etiquetados en el Presupuesto de Egresos 2027, que la Cámara aprueba a más tardar '
             'el 15 de noviembre. Sin una partida a la vista, no se puede seguir de dónde saldrá cada peso ni compararlo después con lo '
             'ejercido.'),
            ('El segundo: la cifra creció en una semana. El 21 de octubre, en su conferencia, la Presidenta habló de «alrededor de» %s a %s; '
             'el 28, de %s. Y el acueducto que la Federación pagaría con 9 mil 300 millones lo presupuestó el Gobierno de Jalisco en %s en '
             'la iniciativa que mandó al Congreso local: con esos dos números, faltarían unos %s, y nadie ha dicho quién los pone '
             '(cuenta con una cifra de prensa, sin chip derivado).'
             % (m0(AGUA_FED[0]), m0(AGUA_FED[1]), m0(AGUA_FED_2810), m0(acu), m0(acu - 9300))),
            ('El tercero: «sin adquirir deuda» quiere decir que Jalisco no se endeuda. El Presupuesto federal sí se financia en parte con '
             'deuda: de los %s de la Ley de Ingresos 2027, %s son financiamiento. El dinero no tiene etiqueta de origen: se puede decir que '
             'el estado no pedirá prestado, no que la obra se pague sin deuda pública.' % (_mmdp(P['total']), _mmdp(deuda))),
            ('El cuarto: «agua potable de calidad» es la meta, no un dato. Salud Jalisco explicó cómo toma sus muestras, pero no ha publicado '
             'los resultados de laboratorio; ese pendiente sigue abierto en Crisis ambientales.'),
        ],
        'cotejo': [
            {'dice': 'El gobierno federal invierte 14 mil 500 millones de pesos', 'res': 'matiz',
             'explica': ('Es lo que anunció Presidencia el 28 de octubre: el título de su comunicado dice «invertirá». Es un compromiso, no un '
                         'gasto ejercido ni una partida aprobada; según la prensa, no vendrá etiquetado en el Presupuesto 2027.'),
             'fuente': 'Presidencia, comunicado del 28-10-2026', 'url': PRES_2810},
            {'dice': '9,300 millones para el acueducto Chapala–Guadalajara y 5,200 para Calderón–San Gaspar', 'res': 'pendiente',
             'explica': ('Los dos suman los 14,500, pero el desglose lo dio la prensa; el texto del comunicado no abre. El acueducto, según la '
                         'iniciativa del Gobierno de Jalisco, cuesta %s.' % m0(acu)),
             'fuente': 'Presidencia, comunicado del 28-10-2026', 'url': PRES_2810, 'quien': FALTA_AGUA, 'donde': PRES_2810},
            {'dice': 'Para consolidar obras hidráulicas', 'res': 'pendiente',
             'explica': ('Las obras empezarían en 2027 y las grandes terminarían a finales de 2028, según la prensa. Las fechas y el '
                         'expediente de cada obra los debe publicar la Conagua, que las ejecutaría.'),
             'fuente': 'Comisión Nacional del Agua', 'url': CONAGUA,
             'quien': 'La Conagua, que ejecutaría las obras, no ha publicado su expediente ni su calendario.', 'donde': CONAGUA},
            {'dice': 'Sin adquirir deuda', 'res': 'matiz',
             'explica': ('Jalisco no se endeudaría por estas obras. Pero el Presupuesto federal se financia en parte con deuda: %s de los %s '
                         'de la Ley de Ingresos 2027 son financiamiento.' % (_mmdp(deuda), _mmdp(P['total']))),
             'fuente': 'Criterios Generales de Política Económica 2027 (Gaceta Parlamentaria 7121, Anexo C), en la base de la plataforma',
             'url': 'https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-C.pdf'},
            {'dice': 'Para garantizar agua potable de calidad', 'res': 'pendiente',
             'explica': 'Salud Jalisco no ha publicado los resultados de laboratorio del agua de la zona metropolitana.',
             'fuente': 'Crisis ambientales: el agua de Guadalajara', 'url': CRISIS,
             'quien': 'Salud Jalisco: no ha publicado los resultados de laboratorio del agua.', 'donde': 'https://ssj.jalisco.gob.mx/'},
        ],
        'medios': [
            {'medio': '@gobmexico (Instagram)', 'titulo': 'El gobierno federal invierte 14 mil 500 millones de pesos para consolidar obras hidráulicas sin adquirir deuda',
             'fecha': '29-10-2026', 'url': GOBMX_AGUA},
            {'medio': 'Expansión Política', 'titulo': 'Crisis del agua en Guadalajara: la inversión en acueductos', 'fecha': '28-10-2026', 'url': EXP_AGUA},
            {'medio': 'La Jornada', 'titulo': 'Gobierno federal y el de Jalisco invertirán $25 mil millones para resolver el problema del agua en Guadalajara',
             'fecha': '28-10-2026', 'url': JORNADA_AGUA},
            {'medio': 'Excélsior', 'titulo': 'Gobierno federal y Jalisco invertirán 25 mil mdp en infraestructura hídrica para Guadalajara', 'fecha': '',
             'url': 'https://www.excelsior.com.mx/nacional/gobierno-federal-y-jalisco-invertiran-25-mil-mdp-infraestructura-hidrica-para-guadalajara'},
            {'medio': 'ADN', 'titulo': 'Invertirá Gobierno de México 14 mil 500 mdp en agua potable para Guadalajara', 'fecha': '',
             'url': 'https://www.adiario.mx/mexico/invertira-gobierno-de-mexico-14-mil-500-mdp-en-agua-potable-para-guadalajara/'},
            {'medio': 'Publimetro', 'titulo': 'Agua en Guadalajara: cuándo mejorará (2027-2028)', 'fecha': '28-10-2026',
             'url': 'https://www.publimetro.com.mx/nacional/2026/10/28/agua-guadalajara-cuando-mejorara-2027-2028/'},
            {'medio': 'N+', 'titulo': 'Presentan plan para llevar agua limpia a Guadalajara sin deuda ni aumento de tarifas', 'fecha': '',
             'url': 'https://www.nmas.com.mx/politica/presentan-plan-para-llevar-agua-limpia-guadalajara-sin-deuda-ni-aumento-de-tarifas/'},
            {'medio': 'Crónica Jalisco', 'titulo': 'Debe quedar en el presupuesto federal 2027 la promesa que hizo Sheinbaum a Jalisco', 'fecha': '21-10-2026',
             'url': 'https://www.cronica.com.mx/jalisco/guadalajara/2026/10/21/debe-quedar-en-el-presupuesto-federal-2027-la-promesa-que-hizo-sheinbaum-a-jalisco/'},
        ],
        'datos': [
            {'ico': '🚱', 'tx': 'Crisis ambientales: el agua de Guadalajara', 'url': CRISIS,
             'de': 'Lo anunciado, lo comprobado y lo que falta: el Plan Hídrico, El Zapotillo y la calidad del agua.'},
            {'ico': '🗺️', 'tx': 'Jalisco y el gasto federal', 'url': AL_MOMENTO_PAG % 'jalisco-gasto-federal-pef-2027',
             'de': 'Cuánto le da la Federación a Jalisco por habitante, y por qué sale abajo.'},
            {'ico': '📊', 'tx': 'Cómo se ve 2027: las cifras del Paquete Económico', 'url': 'numeros-paquete-2027-cifras.html',
             'de': 'Cuánto del Presupuesto 2027 se paga con dinero prestado.'},
            {'ico': '📣', 'tx': 'Memoria de promesas: el agua de Guadalajara', 'url': 'noticias-seguimiento.html#promesa-agua-guadalajara',
             'de': 'La cifra de cada fecha, y si llega al Presupuesto, a la Cuenta Pública y a la Auditoría.'},
        ],
        'glosario': [g('Paquete Económico')],
        'red': 'agua Guadalajara 14 mil 500 millones acueducto Chapala Calderón San Gaspar Conagua',
        'sigue': [
            {'que': 'El Presupuesto de Egresos 2027 (a más tardar el 15 de noviembre): si los 14,500 millones aparecen en el ramo de la Conagua', 'url': PPEF},
            {'que': 'El expediente y el calendario de cada obra en la Conagua', 'url': CONAGUA},
            {'que': 'Quién pone la diferencia entre los 9,300 federales y los 11,922 que Jalisco calculó para el acueducto', 'url': CRISIS},
            {'que': 'Los resultados de laboratorio del agua que debe publicar Salud Jalisco', 'url': 'https://ssj.jalisco.gob.mx/'},
        ],
        'fuentes': [
            {'nombre': 'Presidencia, «Gobierno de México invertirá 14 mil 500 mdp para garantizar agua en Guadalajara sin deuda ni privatización» (28-10-2026)',
             'url': PRES_2810},
            {'nombre': 'Presidencia, versión estenográfica de la conferencia del 21-10-2026', 'url': PRES_2110},
            {'nombre': 'Gobierno de Jalisco, iniciativa del Acueducto Sustituto Chapala–Guadalajara (08-10-2026), en Crisis ambientales', 'url': CRISIS},
            {'nombre': 'Paquete Económico 2027 en la base de la plataforma', 'url': 'numeros-paquete-2027-cifras.html'},
            {'nombre': 'Lo que circula: @gobmexico, Instagram (29-10-2026)', 'url': GOBMX_AGUA},
        ],
        'actualizado': '01-11-2026',
    }



# Huawei y el gobierno (bandeja 11, 01-11-2026). Lo que se coteja es una publicación de
# @derechadiariomx que resume la serie «Operación Huawei» de Código Magenta (audios
# atribuidos a un ejecutivo comercial de Huawei). La base es ComprasMX 2025–2026.
POST_HUAWEI = 'https://www.instagram.com/p/DfGNWzKCVy9/'   # sin el parámetro de rastreo
CM_GRAB = 'https://codigomagenta.com.mx/operacion-huawei-grabaciones-secretas/'
CM_WASH = 'https://codigomagenta.com.mx/operacion-huawei-alerta-en-washington/'
CM_AMLO = 'https://codigomagenta.com.mx/presume-huawei-favoritismo-de-amlo/'
FCC_LISTA = 'https://www.fcc.gov/supplychain/coveredlist'
CMX_DA = 'https://comprasmx.buengobierno.gob.mx/datos-abiertos'
COMPRANET_CM = 'https://upcp-compranet.hacienda.gob.mx/cnetassets/Publicaciones_Gob_CM/CM_Servicios_Nube_Publica/CM_SERVICIOS_DE_NUBE_2024.pdf'
CONTRATOS_PAG = 'contratos-publicos.html'
FALTA_CMX = ('Falta de la plataforma: tenemos los contratos de ComprasMX de 2025 y 2026, no el histórico de CompraNet de 2019 a 2024 ni '
             'los contratos marco; esos portales no abren desde nuestra sesión.')


def _huawei_cmx():
    """Lo que dice ComprasMX de Huawei: proveedores con ese nombre (búsqueda completa) y contratos cuyo título nombra la marca
    (solo entre los contratos más grandes de cada proveedor que guarda la plataforma). Se lee de assets/auditor/data/comprasmx/."""
    import glob
    d = RAIZ / 'assets' / 'auditor' / 'data' / 'comprasmx'
    def carga(f):
        s = f.read_text(encoding='utf-8')
        a = s.index('= {', s.index('window.CMX_')) + 2
        return json.loads(s[a:s.rindex('}') + 1])
    idx = carga(d / 'indice.js')['meta']
    inst = carga(d / 'inst.js')['i']
    prov, contr = [], []
    for f in sorted(glob.glob(str(d / 'p-*.js'))):
        for rfc, x in carga(pathlib.Path(f)).items():
            if 'HUAWEI' in x['n'].upper():
                prov.append(x['n'])
            for k in x.get('k', []):
                if 'HUAWEI' in k[2].upper():
                    contr.append({'prov': x['n'], 'cod': k[0], 'inst': inst.get(k[1], {}).get('n', k[1]), 'tit': k[2], 'imp': k[3],
                                  'mon': k[4], 'tipo': k[5], 'fecha': k[6]})
    if prov:
        raise SystemExit('integrar_al_momento: ya hay un proveedor con «Huawei» en el nombre en ComprasMX; revisa la nota de Huawei')
    if len(contr) != 2 or any(c['mon'] != 'MXN' for c in contr):
        raise SystemExit('integrar_al_momento: cambiaron los contratos con la marca Huawei en ComprasMX; revisa la nota de Huawei')
    n = sum(a['contratos'] for a in idx['archivos'])
    return idx, n, sorted(contr, key=lambda c: -c['imp'])


def huawei_gobierno():
    from apartados import glosario_ancla
    g = lambda t: {'t': t.split(' (')[0], 'url': 'glosario.html#' + glosario_ancla(t)}
    idx, n, cs = _huawei_cmx()
    p2 = lambda v: '$%s' % format(v, ',.2f')
    TIPO = {'LP': 'licitación pública', 'I3': 'invitación a cuando menos tres personas', 'AD': 'adjudicación directa'}
    suma = sum(c['imp'] for c in cs)
    tt = lambda t: t.title().replace(' De ', ' de ').replace(' Del ', ' del ').replace(' La ', ' la ')
    cap = lambda t: t.capitalize().replace('huawei', 'Huawei')
    hj = tt(cs[0]['inst'])
    return {
        'id': 'huawei-gobierno-codigo-magenta',
        'seccion': 'Al momento',
        'icono': '📡',
        'temas': ['huawei', 'codigo magenta', 'operacion huawei'],
        'fecha': '01-11-2026',
        'titulo': ('¿Huawei «digitaliza» al gobierno con acceso total al IMSS, al SAT y a Aduanas? En los contratos federales de 2025 y '
                   '2026, Huawei no aparece como proveedor'),
        'balazo': ('Circula que Morena «recurre a Huawei» y que sus ejecutivos «tendrían total acceso» a los sistemas más sensibles del '
                   'gobierno, según audios que publicó Código Magenta. Los audios son de un ejecutivo comercial que presume clientes: no '
                   'son un contrato. En los %s contratos federales de ComprasMX de 2025 y 2026, ningún proveedor se llama Huawei; lo que sí '
                   'hay son dos compras de equipo de esa marca a otras empresas, las dos del %s. Lo de años anteriores está pendiente.'
                   % (format(n, ','), hj)),
        'nota': {'medio': 'Código Magenta', 'titulo': 'Operación Huawei: Grabaciones secretas', 'fecha': '', 'url': CM_GRAB},
        'circula': {'red': 'Instagram', 'cuenta': '@derechadiariomx', 'fecha': '30 de octubre de 2026 (dos días antes del 1 de noviembre)',
                    'texto': ('MORENA RECURRE A HUAWEI PARA DIGITALIZAR AL GOBIERNO: Según grabaciones obtenidas por el medio Código Magenta, '
                              'ejecutivos chinos de alto nivel de Huawei tendrían total acceso para digitalizar los sistemas más sensibles '
                              'del gobierno mexicano. Desde IMSS, SAT, ISSSTE, Aduanas y hasta aeropuertos, el control que la multinacional '
                              'china tendría en México sería peligroso para la relación con Estados Unidos, cuyo gobierno ya calificó a '
                              'Huawei como una amenaza para la seguridad nacional.')},
        'cuerpo': [
            ('De dónde sale. Código Magenta publicó una serie, «Operación Huawei», con grabaciones que atribuye a un ejecutivo comercial de '
             'Huawei en México. Según las notas que la retoman, en ellas el ejecutivo dice que su empresa es el mayor proveedor tecnológico '
             'del IMSS, del SAT, de la Agencia Nacional de Aduanas y de la Conagua, que construyó centros de datos para el IMSS y que su '
             'gente ayudó a redactar un contrato marco de servicios tecnológicos. Es lo que dice un vendedor de sus clientes: no es un '
             'contrato, y no conocemos una autenticación de los audios. La serie no abre desde la plataforma.'),
            ('Lo que dicen los contratos. Cruzamos la base de ComprasMX que tiene la plataforma: los %s contratos que las dependencias '
             'federales reportaron en 2025 y 2026 (descarga del %s). Ningún proveedor se llama Huawei. Lo que sí aparece son dos compras '
             'de equipo de la marca a otras empresas, las dos del %s: %s por «%s» (%s, %s) y %s por «%s» (%s, %s). En total, %s antes de '
             'impuestos (derivado). Tener contratos no es una irregularidad.'
             % (format(n, ','), '26-10-2026' if idx.get('descarga') == '2026-10-26' else idx.get('descarga'), hj,
                p2(cs[0]['imp']), cap(cs[0]['tit']), cs[0]['prov'], TIPO.get(cs[0]['tipo'], cs[0]['tipo']),
                p2(cs[1]['imp']), cap(cs[1]['tit']), cs[1]['prov'], TIPO.get(cs[1]['tipo'], cs[1]['tipo']), p2(suma))),
            ('El primer punto ciego: el condicional. «Tendrían total acceso», «el control que tendría», «sería peligroso»: la publicación '
             'no afirma un hecho, lo supone. Y «total acceso» no es lo que se cita de los audios, que hablan de ser proveedor. Vender equipo '
             'o construir un centro de datos no es lo mismo que controlar un sistema: eso depende de quién lo opera y de qué dice el contrato.'),
            ('El segundo: «Morena recurre». Un partido no contrata servicios del gobierno; contratan las dependencias, y cada contrato '
             'queda en ComprasMX con su número. Los audios hablan de dependencias y de funcionarios, no de una decisión del partido.'),
            ('El tercero: lo que todavía no vemos. Nuestra búsqueda de la marca en los títulos solo cubre los cinco contratos más grandes '
             'de cada proveedor que guarda la plataforma, y no tenemos el histórico de CompraNet de 2019 a 2024 ni el contrato marco de nube '
             'de 2024: ahí podría estar lo que dice el ejecutivo. Una compra por medio de otra empresa tampoco lleva el nombre de Huawei '
             'como proveedor. Por eso lo de años anteriores queda pendiente, y una acusación no es una condena.'),
        ],
        'ejemplo': {
            'tit': 'La cuenta, con los contratos que sí aparecen',
            'txt': 'Lo que ComprasMX registra con la marca Huawei en el título (2025 y 2026):',
            'filas': [[tt(c['inst']) + ' · ' + c['cod'], p2(c['imp']),
                       '%s, %s, %s' % (c['prov'], TIPO.get(c['tipo'], c['tipo']), c['fecha'])] for c in cs] +
                     [['Total', p2(suma), ' + '.join(p2(c['imp']) for c in cs)]],
            'nota': ('Importe antes de impuestos tal como lo reportó la institución; en un contrato abierto suele ser el máximo, no lo pagado. '
                     'La suma es derivada.'),
        },
        'cotejo': [
            {'dice': 'Morena recurre a Huawei para digitalizar al gobierno', 'res': 'no consta',
             'explica': ('Ningún documento oficial muestra un contrato del gobierno, y menos de un partido, con Huawei para «digitalizar al '
                         'gobierno». En los %s contratos federales de ComprasMX de 2025 y 2026 no hay ningún proveedor llamado Huawei.'
                         % format(n, ',')),
             'fuente': 'ComprasMX, Datos Abiertos 2025 y 2026 (Secretaría Anticorrupción y Buen Gobierno), en la base de la plataforma',
             'url': CMX_DA},
            {'dice': 'Ejecutivos chinos de alto nivel de Huawei tendrían total acceso para digitalizar los sistemas más sensibles', 'res': 'pendiente',
             'explica': ('Lo dice en condicional, y se apoya en audios que el medio atribuye a un ejecutivo comercial de Huawei: '
                         'lo que dice de sus clientes no es un documento. No conocemos una autenticación de los audios, y eso no los vuelve falsos: falta ver los '
                         'contratos de esos años.'),
             'fuente': 'Código Magenta, «Operación Huawei: Grabaciones secretas»', 'url': CM_GRAB, 'quien': FALTA_CMX, 'donde': CMX_DA},
            {'dice': 'Desde IMSS, SAT, ISSSTE, Aduanas y hasta aeropuertos', 'res': 'pendiente',
             'explica': ('En 2025 y 2026 ninguna de esas dependencias le contrató directamente a Huawei. Lo que el ejecutivo dice de años '
                         'anteriores, o de compras por medio de otras empresas, se vería en el histórico de CompraNet y en los contratos '
                         'marco, que no integramos todavía. En 2025 y 2026 solo el %s compró equipo de la marca, a otras empresas.' % hj),
             'fuente': 'ComprasMX, Datos Abiertos 2025 y 2026, en la base de la plataforma', 'url': CONTRATOS_PAG,
             'quien': FALTA_CMX, 'donde': COMPRANET_CM},
            {'dice': 'Estados Unidos ya calificó a Huawei como una amenaza para la seguridad nacional', 'res': 'pendiente',
             'explica': ('Varias fuentes reportan que la Comisión Federal de Comunicaciones de EE. UU. designó a Huawei como amenaza en junio '
                         'de 2020 y la puso en su lista de equipo cubierto en 2021. Es un documento oficial de otro gobierno, y su portal no '
                         'abre desde la plataforma: lo dejamos pendiente hasta leerlo.'),
             'fuente': 'FCC, Covered List', 'url': FCC_LISTA,
             'quien': 'Falta de la plataforma: el portal de la FCC no abre desde nuestra sesión.', 'donde': FCC_LISTA},
            {'dice': 'Sería peligroso para la relación con Estados Unidos', 'res': 'no consta',
             'explica': 'Es una opinión en condicional, no un dato: no se coteja. Ningún documento oficial de los dos gobiernos lo dice así.',
             'fuente': 'Lo que circula: @derechadiariomx', 'url': POST_HUAWEI},
        ],
        'medios': [
            {'medio': '@derechadiariomx (Instagram)', 'titulo': 'Morena recurre a Huawei para digitalizar al gobierno', 'fecha': '30-10-2026',
             'url': POST_HUAWEI},
            {'medio': 'Código Magenta', 'titulo': 'Operación Huawei: Grabaciones secretas', 'fecha': '', 'url': CM_GRAB},
            {'medio': 'Código Magenta', 'titulo': 'Operación Huawei: alerta en Washington', 'fecha': '', 'url': CM_WASH},
            {'medio': 'Código Magenta', 'titulo': 'Presume Huawei favoritismo de AMLO', 'fecha': '', 'url': CM_AMLO},
            {'medio': 'Mundo Ejecutivo', 'titulo': 'Huawei en México: audios filtrados revelan presuntos vínculos con infraestructura tecnológica del gobierno',
             'fecha': '', 'url': 'https://mundoejecutivo.com.mx/actualidad/huawei-en-mexico-audios-filtrados-revelan-presuntos-vinculos-con-infraestructura-tecnologica-del-gobierno/'},
            {'medio': 'Energía Hoy', 'titulo': 'Huawei bajo la lupa: audios apuntan a infraestructura crítica de Pemex y CFE', 'fecha': '',
             'url': 'https://energiahoy.com/tech-trends/huawei-bajo-la-lupa-audios-apuntan-a-infraestructura-critica-de-pemex-y-cfe/'},
            {'medio': 'Índice Político', 'titulo': 'Audios atribuidos a Huawei describen su alcance en dependencias del gobierno mexicano', 'fecha': '',
             'url': 'https://indicepolitico.com/audios-atribuidos-a-huawei-describen-su-alcance-en-dependencias-del-gobierno-mexicano/'},
            {'medio': 'SonoraPresente', 'titulo': 'Código Magenta revela audios sobre expansión de Huawei en áreas estratégicas del gobierno mexicano',
             'fecha': '', 'url': 'https://sonorapresente.com/2026/09/codigo-magenta-revela-audios-sobre-expansion-de-huawei-en-areas-estrategicas-del-gobierno-mexicano/'},
        ],
        'datos': [
            {'ico': '📑', 'tx': 'Contratos públicos (ComprasMX)', 'url': CONTRATOS_PAG,
             'de': 'Busca a cualquier proveedor del gobierno federal: sus contratos, quién se los dio y cómo.'},
            {'ico': '🏛️', 'tx': 'Auditor de entes', 'url': 'herramienta-inspector-entes.html',
             'de': 'El estado de cuenta y la salud financiera del IMSS, el SAT, el ISSSTE y las demás dependencias.'},
        ],
        'glosario': [g('Licitación Pública'), g('Invitación a Cuando Menos Tres Personas'), g('Adjudicación Directa')],
        'red': 'Huawei gobierno México Código Magenta audios IMSS SAT Aduanas',
        'sigue': [
            {'que': 'Los contratos de 2019 a 2024 en el histórico de CompraNet: si Huawei, directamente o por medio de otras empresas, le vendió al IMSS, al SAT o a Aduanas', 'url': CMX_DA},
            {'que': 'El Anexo 4 del contrato marco de nube pública de 2024: qué proveedores quedaron acreditados', 'url': COMPRANET_CM},
            {'que': 'La respuesta de la Agencia de Transformación Digital y de las dependencias nombradas', 'url': 'https://www.gob.mx/atdt'},
            {'que': 'La designación de la FCC y la Covered List, en su documento', 'url': FCC_LISTA},
        ],
        'fuentes': [
            {'nombre': 'ComprasMX, Datos Abiertos: Datos Relevantes de los Contratos 2025 y 2026 (descarga del 26-10-2026), en la base de la plataforma',
             'url': CMX_DA},
            {'nombre': 'Pendiente: FCC, Covered List', 'url': FCC_LISTA},
            {'nombre': 'Punto de partida: Código Magenta, serie «Operación Huawei»', 'url': CM_GRAB},
            {'nombre': 'Lo que circula: @derechadiariomx, Instagram (30-10-2026)', 'url': POST_HUAWEI},
        ],
        'actualizado': '01-11-2026',
    }

NOTAS = [modalidad_40, senado_lif_2027, jalisco_gasto_federal, asf_segunda_entrega_2025, portacelis_diesel, carnaval_ensenada, asf_nuevo_leon, lfd_dnr_defensa, pemex_3t_2026, servidores_exportacion, agua_guadalajara_federal, huawei_gobierno]


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
