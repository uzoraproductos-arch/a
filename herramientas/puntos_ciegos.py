#!/usr/bin/env python3
"""El detector de puntos ciegos (pedido del autor, 01-11-2026: «empieza con el
detector»).

Las primeras once notas «Al momento» enseñaron que las notas sobre el dinero
público suelen esconder algo en los mismos lugares: una promesa contada como
hecho, un porcentaje sin su base, «sin deuda», una comparación entre cosas que
no miden lo mismo, una acusación contada como condena… Aquí esos lugares son
reglas. El verificador de notas (verificador.js, `ciegos()`) y el chat
(«¿es cierto que…?») las aplican solos a cualquier texto.

Un punto ciego NO es un error ni un veredicto: es una pregunta que conviene
hacer antes de creerle a la nota. Se detecta por las palabras, así que puede
fallar, y así se le dice al lector. Aquí no se escribe ninguna cifra.

Cada regla: id, ícono, nombre, `re` (expresión sobre el texto en minúsculas y
sin acentos; se busca como palabra completa, y debe valer igual en Python y
en JavaScript: sin lookbehind ni grupos con nombre), `ex` (por qué importa),
`pr` (qué preguntar) y `de` (la nota «Al momento» donde lo aprendimos, con lo
que pasó ahí). Una regla nueva necesita su ejemplo en `de` y su caso en
`prueba_puntos_ciegos.py`.

    python3 herramientas/puntos_ciegos.py "texto"   # qué detecta
"""
import re
import sys
import unicodedata

PAGINA = 'noticias-verifica.html#puntos-ciegos'
AL_MOMENTO = 'noticias-al-momento-%s.html'

REGLAS = [
    {'id': 'promesa', 'ico': '🗓️', 'n': 'Una promesa contada como hecho',
     're': r'invierte|invertira|invertiran|se invertiran|destina|destinara|destinaran|se destinaran|aportara|aportaran|'
           r'garantiza|garantizara|se construira|se construiran|a partir de(l)? 20\d\d',
     'ex': 'Anunciar dinero no es gastarlo. Mientras no aparezca en el Presupuesto de Egresos con su partida, y después en la '
           'Cuenta Pública, es una promesa.',
     'pr': '¿Está en el Presupuesto con nombre y monto? ¿Quién lo gasta y cuándo? ¿Lo va a reportar la Cuenta Pública?',
     'de': [('agua-guadalajara-14500-federal', '@gobmexico escribió «invierte»; el comunicado de Presidencia dice «invertirá» y, según la prensa, '
             'el dinero no vendrá etiquetado en el Presupuesto 2027.'),
            ('lfd-2027-dnr-defensa-tren-maya-aifa', '«El gasto sería a partir del 2027»: lo aprobado fue a dónde irá lo que se cobre, no un gasto ya hecho.')]},
    {'id': 'porcentaje', 'ico': '📐', 'n': 'Un porcentaje sin su base',
     're': r'\d+([.,]\d+)? ?(%|por ciento)|mil por ciento',
     'ex': 'Un porcentaje puede ser una parte del total (cuánto le toca a alguien) o un cambio (cuánto creció). No es lo mismo, y '
           'sin la cifra de base no se sabe de cuánto dinero se habla.',
     'pr': '¿Es una parte o un aumento? ¿Frente a qué año y qué cifra? ¿En pesos de entonces o descontando la inflación?',
     'de': [('lfd-2027-dnr-defensa-tren-maya-aifa', 'El 57 % era la parte del cobro que le toca a la Defensa, no un aumento.'),
            ('pemex-3t-2026-perdida-neta', 'El «82.4 % menos» compara contra el mismo trimestre del año pasado y no dice por qué bajó la pérdida.')]},
    {'id': 'mas-de', 'ico': '🧮', 'n': '«Más de», «hasta», «casi»: la cifra con margen',
     're': r'(mas de|hasta|casi|alrededor de|cerca de|unos) \$?\d[\d.,]*',
     'ex': 'Estas palabras dan margen: «más de 18 mil millones» cabe en muchas cifras. A veces juntan dos cifras distintas que se parecen.',
     'pr': '¿Cuál es la cifra exacta del documento? ¿Es una sola cifra o la suma de varias?',
     'de': [('lfd-2027-dnr-defensa-tren-maya-aifa', 'Circulaban dos «18 mil millones» distintos, y la publicación los juntaba en uno.'),
            ('asf-segunda-entrega-cp2025', '«Más de 9 mil mdp pendientes de aclarar»: la cifra exacta está en el informe de la ASF.')]},
    {'id': 'sin-costo', 'ico': '💳', 'n': '«Sin deuda», «sin costo»: alguien paga',
     're': r'sin (adquirir |contratar |pedir )?deuda|sin endeudamiento|sin endeudar|sin costo|sin cobrar|gratis|gratuit[oa]s?|'
           r'sin (aumentar|subir|nuevos) impuestos|sin aumento de tarifas',
     'ex': 'El dinero público siempre lo paga alguien: con impuestos, con derechos o con deuda. Que un gobierno no pida prestado para '
           'una obra no quiere decir que el presupuesto de donde sale no se pague, en parte, con deuda.',
     'pr': '¿De qué presupuesto sale? ¿Ese presupuesto se paga en parte con deuda? ¿Quién paga después la operación?',
     'de': [('agua-guadalajara-14500-federal', 'Jalisco no pide prestado, pero la Ley de Ingresos 2027 incluye dinero prestado para el presupuesto federal.')]},
    {'id': 'comparacion', 'ico': '⚖️', 'n': 'Comparar cosas que no miden lo mismo',
     're': r'superando|supera a|superan a|mas que|menos que|vs\.?|versus|frente a|comparad[oa] con|en comparacion|lugar \d+ de \d+',
     'ex': 'Dos cifras solo se comparan si miden lo mismo: el mismo periodo, la misma unidad y el mismo universo. Y un lugar en una tabla '
           'depende de cómo se armó la tabla.',
     'pr': '¿Mismo periodo y misma unidad? ¿Se compara una cosa contra dos juntas? ¿Por habitante o en total?',
     'de': [('servidores-ia-exportaciones-contenido-nacional', 'Los servidores se comparaban contra autos y autopartes juntos.'),
            ('jalisco-gasto-federal-pef-2027', '«Lugar 24 de 32» depende de qué se cuente: con participaciones y aportaciones por habitante, Jalisco queda en el lugar 30.')]},
    {'id': 'dolares', 'ico': '💵', 'n': 'Cifras en dólares',
     're': r'mdd|dolares|usd',
     'ex': 'Pasar de pesos a dólares exige un tipo de cambio y una fecha. Si la nota no los dice, la cifra no se puede reproducir, y '
           'puede crecer o encoger solo porque se movió el tipo de cambio.',
     'pr': '¿Qué tipo de cambio y de qué fecha (el FIX de Banxico)? ¿La cifra original estaba en pesos o en dólares?',
     'de': [('pemex-3t-2026-perdida-neta', 'Pemex reporta en pesos; los dólares son una conversión.'),
            ('servidores-ia-exportaciones-contenido-nacional', 'Las exportaciones venían en dólares y de una empresa privada, no de la balanza del INEGI.')]},
    {'id': 'quien', 'ico': '🧾', 'n': '¿Quién lo dice? La fuente sin su documento',
     're': r'segun(?! (el |la |los |las )?(pef|dof|asf|shcp|hacienda|inegi|banxico|cuenta publica|presupuesto|ley|auditoria|diario oficial))|revelo|revela|denuncia|denuncio|acusa|acuso|dato:|se estima|estiman|expertos|especialistas|analistas|fuentes',
     'ex': 'Una investigación periodística, un partido, una consultora o un gremio pueden tener razón, pero no son el documento. La cifra '
           'vale lo que vale el documento de donde sale.',
     'pr': '¿Cuál es el documento? ¿Lo publicó una autoridad obligada a hacerlo (la ASF, Hacienda, el INEGI, el DOF) o un particular?',
     'de': [('servidores-ia-exportaciones-contenido-nacional', 'Las cifras eran de S&P Global, una empresa privada, y la otra fuente era un gremio de la industria.'),
            ('portacelis-permiso-diesel-sener', '«Según una investigación de MCCI»: el permiso se coteja en el documento de la Sener.')]},
    {'id': 'juicio', 'ico': '📢', 'n': 'Palabras que juzgan antes de probar',
     're': r'despilfarro|fracasad[oa]s?|faraonic[oa]s?|regalo|urgente|expres|al vapor|madruguete|escandal[oa]s?|escandalos[oa]s?|'
           r'narco[a-z]*|fantasma|saqueo|atraco|en solo|peligros[oa]s?',
     'ex': 'Los adjetivos son opinión. No vuelven falsa la nota, pero tampoco la prueban: el cotejo se hace sobre los hechos y las '
           'cifras, no sobre el tono.',
     'pr': 'Quítale los adjetivos: ¿qué afirmación queda y qué documento la sostiene?',
     'de': [('lfd-2027-dnr-defensa-tren-maya-aifa', '«Despilfarro exprés», «fracasados», «faraónicas»: sin los adjetivos quedaba una votación que se coteja en la Gaceta.'),
            ('portacelis-permiso-diesel-sener', '«Regalo de despedida» y «fantasma»: lo que se coteja es el permiso y a quién se dio.')]},
    {'id': 'acusacion', 'ico': '🏛️', 'n': 'Una acusación no es una condena',
     're': r'desvio|desviaron|desvio de|fraude|fraudulent[oa]s?|corrupcion|corrupt[oa]s?|lavado|contrabando|contrabandead[oa]s?|'
           r'malversacion|peculado|robo|robaron|ligad[oa]s? a|vinculad[oa]s? a',
     'ex': 'Que la ASF promueva una denuncia, que un medio publique una investigación o que alguien acuse no es una sentencia '
           '(Constitución, art. 20, apartado B, fr. I). Mientras un juez no resuelva, la persona se presume inocente.',
     'pr': '¿Quién acusa y ante quién? ¿Hay denuncia presentada, carpeta abierta o sentencia? ¿Qué dice el documento de la autoridad?',
     'de': [('asf-nuevo-leon-triangulacion-cp2025', '«Desvió» es la conclusión del titular; lo que hay, según la prensa, es una denuncia de la ASF ante la Fiscalía.'),
            ('imss-modalidad-40-gestores', '«Esquema fraudulento» lo dijo el director del IMSS; si hubo delito, lo decide un juez.')]},
    {'id': 'resultado', 'ico': '📒', 'n': 'Ganancia o pérdida sin su porqué',
     're': r'perdida neta|perdidas?|ganancias?|utilidad(es)?|deficit|superavit|numeros rojos|numeros negros',
     'ex': 'El resultado de una empresa pública o de un evento mezcla lo que vende, lo que gasta y efectos contables, como el tipo de '
           'cambio o el deterioro de activos. Una pérdida que baja puede deberse a la contabilidad y no a que se trabaje mejor, y un '
           'evento público no se mide solo por lo que «ganó».',
     'pr': '¿Qué renglón del estado de resultados lo explica? ¿Cuánto es operación y cuánto efecto contable? ¿Para qué era el gasto?',
     'de': [('pemex-3t-2026-perdida-neta', 'La pérdida por tipo de cambio fue más grande que la pérdida neta del trimestre.'),
            ('carnaval-ensenada-2026-imcudhe', 'La «ganancia» del Carnaval se pregunta junto con lo que costó y para qué era.')]},
    {'id': 'periodo', 'ico': '⏱️', 'n': '«En los últimos años»: ¿desde cuándo?',
     're': r'ultimos anos|ultimos meses|historic[oa]s?|record|nunca antes|sin precedentes|el mayor|la mayor|el peor|la peor',
     'ex': 'Una tendencia depende del año en que se empieza a contar: escoger el punto de partida puede hacer que una caída o un '
           'aumento se vea más grande o más chico.',
     'pr': '¿Desde qué año y hasta cuál? ¿La serie completa dice lo mismo? ¿Pesos de hoy o de entonces?',
     'de': [('jalisco-gasto-federal-pef-2027', '«La inversión pública cayó un 83 % en los últimos años»: el resultado depende del año de partida.')]},
    {'id': 'proyeccion', 'ico': '🔮', 'n': 'Una proyección no es un dato',
     're': r'proyeccion|se proyecta|se espera|vienen|llegaran|pronostic[a-z]*|estimad[oa]s?|a 20\d\d',
     'ex': 'Una proyección dice lo que alguien cree que va a pasar, con sus supuestos. Sirve para planear, pero no se coteja como '
           'hecho hasta que pasa.',
     'pr': '¿Quién la hizo y con qué supuestos? ¿Hay un documento oficial que la respalde?',
     'de': [('servidores-ia-exportaciones-contenido-nacional', '«Los $82,500 MDD que vienen para data centers a 2031» es una proyección de privados, no una inversión hecha.')]},
    {'id': 'condicional', 'ico': '❓', 'n': 'El condicional que esconde un rumor',
     're': r'(tendria|tendrian|seria|serian|habria|habrian|estaria|estarian)',
     'ex': ('«Tendría», «sería», «habría»: la nota no afirma un hecho, lo supone. Es la forma de publicar algo que nadie ha '
            'confirmado sin decirlo.'),
     'pr': '¿Quién lo confirma, y con qué documento? Si nadie, es una hipótesis, no una noticia.',
     'de': [('huawei-gobierno-codigo-magenta', '«Tendrían total acceso» y «sería peligroso»: la publicación supone, y los contratos de 2025 y 2026 no lo muestran.')]},
]

# Lo que el detector no puede ver con un solo texto: se dice en la página.
NO_VE = [
    ('Una cifra que cambia de una fecha a otra', 'En el agua de Guadalajara, la cifra federal pasó de «alrededor de 12 a 13 mil» a 14,500 '
     'millones en una semana. Verlo pide comparar declaraciones: lo hace la memoria de promesas (noticias-seguimiento.html#promesas).'),
    ('Lo que la nota no menciona', 'Una cifra que falta no tiene palabras que la delaten. Eso lo encuentra el cotejo contra la base, '
     'no el detector.'),
]


def plano(t):
    t = unicodedata.normalize('NFD', str(t or '').lower())
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn').replace('̃', '')


def _re(r):
    return re.compile(r'(^|[^a-z0-9])(' + r['re'] + r')(?![a-z0-9])')


def detecta(texto):
    """Lo mismo que ciegos() de verificador.js: [(id, frase)]."""
    p = plano(texto)
    out = []
    for r in REGLAS:
        m = _re(r).search(p)
        if m:
            out.append((r['id'], m.group(2)))
    return out


def datos():
    """Las reglas para el navegador (D.ciegos del verificador y del chat)."""
    return [{'id': r['id'], 'ico': r['ico'], 'n': r['n'], 're': r['re'], 'ex': r['ex'], 'pr': r['pr'],
             'de': [{'h': AL_MOMENTO % i, 't': t} for i, t in r['de']]} for r in REGLAS]


def seccion(esc):
    """El cuerpo de la sección «Puntos ciegos» de noticias-verifica.html."""
    lis = '\n'.join(
        '    <li class="nt-ciego" id="ciego-%s"><p class="nt-ciego-n"><span aria-hidden="true">%s</span> <b>%s</b></p>\n'
        '      <p>%s</p>\n      <p><b>Qué preguntar:</b> %s</p>\n'
        '      <p class="nt-ciego-de">Así lo vimos: %s</p></li>' % (
            r['id'], r['ico'], esc(r['n']), esc(r['ex']), esc(r['pr']),
            ' · '.join('<a href="%s">%s</a>' % (AL_MOMENTO % i, esc(t)) for i, t in r['de']))
        for r in REGLAS)
    no = '\n'.join('    <li><b>%s.</b> %s</li>' % (esc(t), esc(x)) for t, x in NO_VE)
    return ('  <p>Un punto ciego no es un error: es un lugar donde una nota sobre el dinero público suele esconder algo. Los aprendimos '
            'cotejando las notas «Al momento», y ahora el verificador y el Auditor los buscan solos en lo que pegues: te dicen dónde '
            'está cada uno y qué preguntar. Los encontramos por las palabras, así que pueden fallar; <b>no califican la nota</b>, la '
            'calificación es el cotejo contra el documento.</p>\n'
            '  <ol class="nt-ciegos">\n%s\n  </ol>\n'
            '  <h3 class="nt-sub">Lo que el detector todavía no ve</h3>\n  <ul class="nt-ciegos-no">\n%s\n  </ul>') % (lis, no)


if __name__ == '__main__':
    for i, f in detecta(' '.join(sys.argv[1:]) or sys.stdin.read()):
        print('%-12s %s' % (i, f))
