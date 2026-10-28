# -*- coding: utf-8 -*-
"""Nepotismo y cargos públicos: cómo se audita el parentesco (pedido del
autor, 28-10-2026: «adentrándonos a esta parte del nepotismo... investigar
los cargos públicos, así como si hay manera de encontrar una relación entre
los personajes que ocupan estos cargos públicos, de consanguinidad o
afinidad, para poderlos nosotros también auditar»).

La séptima aplicación del Modo Inspector (y tarjeta de Aprende), con la calculadora de
parentesco, el árbol de grados, las tres leyes que lo castigan, el método
para investigar un cargo y los puntos ciegos. Cotejado contra los textos
vigentes de la Cámara de Diputados (huellas en docs/boveda/):

- LGRA, última reforma DOF 15-12-2025: arts. 3 fr. VI, 29, 58, 63 Bis
  (adicionado DOF 19-11-2019), 74, 78 y 91.
- Código Penal Federal, última reforma DOF 13-03-2026: art. 220.
- Código Civil Federal, última reforma DOF 14-11-2025: arts. 292 a 300.
- Constitución, última reforma DOF 07-10-2026: arts. 55 fr. VIII, 82 fr.
  VIII, 115 fr. I, 116 y el decreto de nepotismo electoral (DOF 01-04-2025,
  transitorio segundo: elecciones de 2030).
- Ley General de Transparencia (nueva ley DOF 20-03-2025): art. 65 fr. II,
  VI, VII, X y XI.

Regla editorial (AGENTS.md §2 bis): un apellido igual es una pista, nunca
una prueba; a los familiares que no son servidores públicos no se les nombra;
una acusación no es una condena. La calculadora no busca a nadie: dice qué
ley alcanza a un parentesco. Las reglas de cada ley viven aquí, en ALCANCE,
y la página y el chat las leen de la misma tabla.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['inspnepotismo']) y el chat lo
lee como D.nep (bot()).
"""
import html
import json

# Séptima aplicación del Modo Inspector (28-10-2026). La página que tuvo en
# Aprende ese mismo día (ANTERIOR) redirige aquí.
ARCHIVO = 'herramienta-inspector-nepotismo.html'
ANTERIOR = 'nepotismo-y-cargos-publicos.html'

LGRA = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGRA.pdf'
CPF = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CPF.pdf'
CCF = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CCF.pdf'
CPEUM = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf'
LGTAIP = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/LGTAIP.pdf'
INEGI_UMA = 'https://www.inegi.org.mx/temas/uma/'
NOMINA = 'https://nominatransparente.rhnet.gob.mx/'
PNT = 'https://www.plataformadetransparencia.org.mx/'
SANCIONADOS = 'https://directoriosancionados.buengobierno.gob.mx/'
DECLARANET = 'https://declaranet.gob.mx/'

UMA_DIA = 117.31  # INEGI, UMA 2026 (DOF 09-01-2026)

OF = '<span class="est-chip est-oficial">oficial</span>'
DER = '<span class="est-chip est-derivado">derivado</span>'


def esc(t):
    return html.escape(str(t or ''), quote=True)


def liga(url, txt):
    return '<a href="%s" target="_blank" rel="noopener">%s ↗</a>' % (esc(url), txt)


# Los parentescos de la calculadora: (id, como se dice, tipo, linea, grado,
# explicacion). tipo: cons (consanguinidad; la adopcion plena se equipara,
# CCF art. 293), afin (afinidad, CCF art. 294), vinc (matrimonio o
# concubinato: no es parentesco, CCF art. 292, pero las tres leyes lo
# nombran) y nada (la ley no reconoce parentesco).
PARENTESCOS = [
    ('padres', 'Mi padre o mi madre', 'cons', 'recta', 1, 'Una generación hacia arriba.'),
    ('hijos', 'Mi hija o mi hijo (también por adopción plena)', 'cons', 'recta', 1, 'Una generación hacia abajo. La adopción plena cuenta igual (CCF, art. 293).'),
    ('hermanos', 'Mi hermana o mi hermano', 'cons', 'colateral', 2, 'Se sube a los padres (1) y se baja al hermano (2).'),
    ('abuelos', 'Mi abuela o mi abuelo', 'cons', 'recta', 2, 'Dos generaciones hacia arriba.'),
    ('nietos', 'Mi nieta o mi nieto', 'cons', 'recta', 2, 'Dos generaciones hacia abajo.'),
    ('tios', 'Mi tía o mi tío', 'cons', 'colateral', 3, 'Se sube a los abuelos (2) y se baja al tío (3).'),
    ('sobrinos', 'Mi sobrina o mi sobrino', 'cons', 'colateral', 3, 'Se sube a los padres (1), se baja al hermano (2) y al sobrino (3).'),
    ('bisabuelos', 'Mi bisabuela o mi bisabuelo', 'cons', 'recta', 3, 'Tres generaciones hacia arriba.'),
    ('bisnietos', 'Mi bisnieta o mi bisnieto', 'cons', 'recta', 3, 'Tres generaciones hacia abajo.'),
    ('primos', 'Mi prima o mi primo hermano', 'cons', 'colateral', 4, 'Se sube a los abuelos (2) y se baja al tío (3) y al primo (4).'),
    ('tios-abuelos', 'Mi tía abuela o mi tío abuelo', 'cons', 'colateral', 4, 'Se sube a los bisabuelos (3) y se baja al tío abuelo (4).'),
    ('sobrinos-nietos', 'Mi sobrina nieta o mi sobrino nieto', 'cons', 'colateral', 4, 'Se sube a los padres (1) y se baja por el hermano (2), el sobrino (3) y el sobrino nieto (4).'),
    ('tatarabuelos', 'Mi tatarabuela o mi tatarabuelo', 'cons', 'recta', 4, 'Cuatro generaciones hacia arriba.'),
    ('primos-segundos', 'Mi prima o mi primo segundo', 'cons', 'colateral', 6, 'Se sube a los bisabuelos (3) y se baja tres generaciones (6).'),
    ('conyuge', 'Mi esposa o mi esposo', 'vinc', '', 0, 'El matrimonio no es parentesco (CCF, art. 292), pero las tres leyes lo nombran.'),
    ('concubino', 'Mi concubina o mi concubino', 'vinc', '', 0, 'El concubinato no es parentesco, pero la ley administrativa y la electoral lo nombran.'),
    ('suegros', 'Mi suegra o mi suegro', 'afin', 'recta', 1, 'Es el padre o la madre de tu cónyuge: primer grado.'),
    ('yernos', 'Mi nuera o mi yerno', 'afin', 'recta', 1, 'Es el cónyuge de tu hija o de tu hijo: primer grado.'),
    ('hijastros', 'Mi hijastra o mi hijastro', 'afin', 'recta', 1, 'Es la hija o el hijo de tu cónyuge: primer grado.'),
    ('cunados', 'Mi cuñada o mi cuñado', 'afin', 'colateral', 2, 'Es el hermano de tu cónyuge, o el cónyuge de tu hermano: segundo grado.'),
    ('abuelos-conyuge', 'Los abuelos o los nietos de mi cónyuge', 'afin', 'recta', 2, 'Segundo grado, como lo serían para tu cónyuge.'),
    ('tios-conyuge', 'Los tíos o los sobrinos de mi cónyuge', 'afin', 'colateral', 3, 'Tercer grado, como lo serían para tu cónyuge.'),
    ('primos-conyuge', 'Las primas o los primos de mi cónyuge', 'afin', 'colateral', 4, 'Cuarto grado, como lo serían para tu cónyuge.'),
    ('concunos', 'Mi concuña o mi concuño', 'nada', '', 0, 'Es el cónyuge del hermano de tu cónyuge. La afinidad no une a los parientes de un cónyuge con los del otro: no hay parentesco.'),
    ('consuegros', 'Mi consuegra o mi consuegro', 'nada', '', 0, 'Son los padres del cónyuge de tu hija o tu hijo: no hay parentesco.'),
]

# Que alcanza cada ley: (clave, nombre corto, articulo, url, regla). Las
# reglas copian el texto de la ley; «quiza» es lo que la ley deja abierto y
# decide la autoridad.
def _lgra(t, l, g, pid):
    if t == 'cons':
        return 'si' if g <= 4 else 'no'
    if t == 'afin':
        return 'si' if g <= 2 else 'no'
    if t == 'vinc':
        return 'si'
    return 'no'


def _cpf(t, l, g, pid):
    if t == 'cons':
        return 'si' if (l == 'recta' or g <= 4) else 'quiza'
    if t == 'afin':
        return 'si' if g <= 4 else 'quiza'
    if pid == 'conyuge':
        return 'si'
    return 'quiza'  # concubino, concuños, consuegros: «tercero con vínculos afectivos, económicos...»


def _ele(t, l, g, pid):
    if t == 'cons':
        return 'si' if (l == 'recta' or g <= 4) else 'no'
    if t == 'afin':
        return 'si' if g <= 2 else 'no'
    if t == 'vinc':
        return 'si'
    return 'no'


LEYES = [
    ('lgra', 'Contratarlo en tu oficina', 'Nepotismo, art. 63 Bis LGRA', LGRA, _lgra,
     'Falta administrativa grave: contratar, nombrar o intervenir para que se contrate en el ente donde trabajas.'),
    ('cpf', 'Darle un contrato o un permiso', 'Ejercicio abusivo de funciones, art. 220 CPF', CPF, _cpf,
     'Delito: otorgar ilícitamente contratos, concesiones, permisos o compras que lo beneficien económicamente.'),
    ('ele', 'Que compita por tu cargo (desde 2030)', 'Nepotismo electoral, Constitución', CPEUM, _ele,
     'Que se postule al mismo cargo de elección que tú ocupas, en la elección siguiente.'),
]

QUIZA = {
    'cpf': 'La ley no lo nombra como pariente, pero alcanza a «cualquier tercero con el que tenga vínculos afectivos, económicos o de dependencia»: lo decide la fiscalía y el juez.',
}


def alcance():
    """Tabla única: para cada parentesco, qué ley lo alcanza."""
    out = []
    for pid, nom, t, l, g, ex in PARENTESCOS:
        out.append({'id': pid, 'n': nom, 't': t, 'l': l, 'g': g, 'x': ex,
                    'r': {k: f(t, l, g, pid) for k, _, _, _, f, _ in LEYES}})
    return out


def _tipo(p):
    if p['t'] == 'cons':
        return 'Consanguinidad, línea %s, %s grado' % (p['l'], ORD[p['g']])
    if p['t'] == 'afin':
        return 'Afinidad, línea %s, %s grado' % (p['l'], ORD[p['g']])
    if p['t'] == 'vinc':
        return 'Vínculo, no parentesco'
    return 'Sin parentesco legal'


ORD = {1: 'primer', 2: 'segundo', 3: 'tercer', 4: 'cuarto', 5: 'quinto', 6: 'sexto'}
MARCA = {'si': ('✅', 'Sí lo alcanza'), 'no': ('➖', 'No lo alcanza'), 'quiza': ('⚠️', 'Depende')}


# --------------------------------------------------------------- el arbol
# Nodos del arbol de consanguinidad: (columna, fila, nombre, grado). Fila 0
# eres tu; arriba, los ascendientes. Columna 0, la linea recta; 1, la de tus
# hermanos; 2, la de tus tios. A la derecha, la afinidad.
ARBOL = [
    (0, -4, 'Tatarabuelos', 4), (0, -3, 'Bisabuelos', 3), (0, -2, 'Abuelos', 2), (0, -1, 'Padres', 1),
    (0, 0, 'Tú', 0), (0, 1, 'Hijos', 1), (0, 2, 'Nietos', 2), (0, 3, 'Bisnietos', 3), (0, 4, 'Tataranietos', 4),
    (1, 0, 'Hermanos', 2), (1, 1, 'Sobrinos', 3), (1, 2, 'Sobrinos nietos', 4),
    (2, -3, 'Tíos abuelos', 4), (2, -1, 'Tíos', 3), (2, 0, 'Primos hermanos', 4), (2, 1, 'Primos segundos', 6),
]
AFIN = [(-1, 'Suegros', 1), (0, 'Cónyuge', 0), (1, 'Hijastros · yernos y nueras', 1), (2, 'Cuñados', 2), (3, 'Tíos del cónyuge', 3)]


def arbol_svg():
    W, H = 640, 520
    cx = {0: 90, 1: 250, 2: 410}
    y0, dy = 260, 58
    bw, bh = 138, 40
    p = ['<svg class="nep-arbol" viewBox="0 0 %d %d" role="img" aria-labelledby="nepArbolTit nepArbolDesc">' % (W, H),
         '<title id="nepArbolTit">Árbol de grados de parentesco</title>',
         '<desc id="nepArbolDesc">Cada generación es un grado. En línea recta: padres e hijos 1, abuelos y nietos 2, bisabuelos y bisnietos 3, '
         'tatarabuelos y tataranietos 4. Colaterales: hermanos 2, tíos y sobrinos 3, primos hermanos, tíos abuelos y sobrinos nietos 4. '
         'Por afinidad: suegros, yernos e hijastros 1, cuñados 2. La ley de nepotismo alcanza hasta el cuarto grado de consanguinidad y el '
         'segundo de afinidad, y al cónyuge.</desc>']
    # lineas: recta vertical, y de los padres a los hermanos, de los abuelos a los tios
    p.append('<line class="nep-l" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (cx[0], y0 - 4 * dy, cx[0], y0 + 4 * dy))
    p.append('<path class="nep-l" d="M%d %d H%d V%d"/>' % (cx[0], y0 - dy, cx[1], y0 + 2 * dy))
    p.append('<path class="nep-l" d="M%d %d H%d V%d"/>' % (cx[0], y0 - 2 * dy, cx[2], y0 + dy))
    p.append('<path class="nep-l" d="M%d %d H%d"/>' % (cx[0], y0 - 3 * dy, cx[2]))
    for c, f, nom, g in ARBOL:
        x, y = cx[c] - bw / 2, y0 + f * dy - bh / 2
        cls = 'nep-yo' if g == 0 else ('nep-si' if g <= 4 else 'nep-no')
        p.append('<g class="%s"><rect x="%g" y="%g" width="%d" height="%d" rx="9"/>'
                 '<text x="%g" y="%g">%s</text>%s</g>' % (
                     cls, x, y, bw, bh, cx[c], y + 17, esc(nom),
                     '' if g == 0 else '<text class="nep-g" x="%g" y="%g">%s grado</text>' % (cx[c], y + 33, '%dº' % g)))
    xa = 560
    p.append('<text class="nep-cab" x="%d" y="%d">Afinidad</text>' % (xa, y0 - 2 * dy + 10))
    for f, nom, g in AFIN:
        y = y0 + f * dy - bh / 2
        cls = 'nep-vinc' if g == 0 else ('nep-si' if g <= 2 else 'nep-no')
        p.append('<g class="%s"><rect x="%d" y="%g" width="%d" height="%d" rx="9"/>'
                 '<text x="%d" y="%g">%s</text><text class="nep-g" x="%d" y="%g">%s</text></g>' % (
                     cls, xa - 70, y, 140, bh, xa, y + 17, esc(nom.split(' · ')[0]), xa, y + 33,
                     'vínculo' if g == 0 else '%dº grado' % g))
    p.append('<line class="nep-l nep-l-afin" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (cx[0] + bw / 2, y0, xa - 70, y0))
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------------ las secciones
def _tabla_leyes():
    filas = [
        ('Qué castiga',
         'Que el servidor público, valiéndose de su cargo, <b>designe, nombre o intervenga</b> para que se contrate a su familia en el '
         'ente público donde trabaja: personal de confianza, de estructura, de base o por honorarios.',
         'Que <b>otorgue ilícitamente</b> contratos, concesiones, permisos, licencias, autorizaciones, exenciones, compras o ventas que '
         'beneficien económicamente a él o a su familia.',
         'Que el cónyuge, la pareja o un pariente de quien ocupa un cargo de elección <b>compita por ese mismo cargo</b> en la elección '
         'siguiente: Presidencia, gubernatura, diputación federal o local, ayuntamiento y, en la Ciudad de México, jefatura de Gobierno, '
         'diputación y alcaldía.'),
        ('A quién alcanza',
         'Consanguinidad hasta el cuarto grado, afinidad hasta el segundo, matrimonio y concubinato.',
         'Cónyuge, ascendientes y descendientes, consanguinidad y afinidad hasta el cuarto grado, terceros con vínculos afectivos, '
         'económicos o de dependencia, y socios o sociedades.',
         'Línea recta sin límite, colaterales hasta el cuarto grado, afinidad hasta el segundo, parentesco civil, matrimonio, concubinato '
         'y unión de hecho, si existieron en los tres años previos a la elección.'),
        ('Quién lo decide',
         'Investiga el órgano interno de control (la denuncia puede ser anónima, art. 91) y sanciona el tribunal de justicia administrativa.',
         'Investiga la fiscalía y lo juzga un juez penal.',
         'La autoridad electoral, al revisar el registro de candidaturas.'),
        ('Qué arriesga',
         'Suspensión de 30 a 90 días, destitución, multa e inhabilitación de 1 a 10 años, o de 10 a 20 si la afectación pasa de 200 UMA '
         '(art. 78). Prescribe en siete años (art. 74).',
         'De 3 meses a 2 años de prisión si la operación no pasa de 500 UMA; de 2 a 12 años si pasa.',
         'No poder registrarse como candidata o candidato.'),
        ('Desde cuándo', 'Desde la reforma publicada en el DOF el 19-11-2019.', 'Con este texto desde la reforma publicada en el DOF el 18-07-2016.',
         'En las elecciones federales y locales de <b>2030</b> (transitorio segundo, DOF 01-04-2025). Hasta entonces, la Constitución federal no lo impide.'),
    ]
    cab = ('<th scope="col">Administrativa: nepotismo<br><small>%s</small></th>' % liga(LGRA, 'LGRA, art. 63 Bis'),
           '<th scope="col">Penal: ejercicio abusivo de funciones<br><small>%s</small></th>' % liga(CPF, 'Código Penal Federal, art. 220'),
           '<th scope="col">Electoral: nepotismo electoral<br><small>%s</small></th>' % liga(CPEUM, 'Constitución, arts. 55, 82, 115, 116 y 122'))
    return ('<div class="nep-tabla-env" tabindex="0" role="region" aria-label="Las tres leyes, lado a lado"><table class="nep-tabla">\n'
            '<thead><tr><th scope="col"><span class="sr-only">Pregunta</span></th>%s</tr></thead>\n<tbody>\n%s\n</tbody></table></div>' % (
                ''.join(cab), '\n'.join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td></tr>' % f for f in filas)))


def _calculadora():
    datos = alcance()
    opciones = '\n'.join('<option value="%s">%s</option>' % (esc(p['id']), esc(p['n'])) for p in datos)
    leyes = [{'k': k, 'n': n, 'a': a, 'u': u, 'd': d} for k, n, a, u, _, d in LEYES]
    # Sin JavaScript se lee la tabla completa.
    tabla = ('<details class="nep-todos"><summary>Ver la tabla completa de parentescos</summary>'
             '<div class="nep-tabla-env" tabindex="0" role="region" aria-label="Todos los parentescos"><table class="nep-tabla nep-tabla-p">'
             '<thead><tr><th scope="col">Parentesco</th><th scope="col">Qué dice el Código Civil</th>%s</tr></thead><tbody>%s</tbody></table></div></details>' % (
                 ''.join('<th scope="col">%s</th>' % esc(n) for _, n, _, _, _, _ in LEYES),
                 ''.join('<tr><th scope="row">%s</th><td>%s</td>%s</tr>' % (
                     esc(p['n']), esc(_tipo(p)),
                     ''.join('<td>%s <span class="sr-only">%s</span></td>' % (MARCA[p['r'][k]][0], MARCA[p['r'][k]][1]) for k, _, _, _, _, _ in LEYES))
                     for p in datos)))
    return ('<div class="nep-calc" id="nepCalc">\n'
            '<label class="nep-calc-et" for="nepRel">Si el servidor público eres tú, la persona es…</label>\n'
            '<select id="nepRel" class="nep-sel"><option value="">Elige el parentesco</option>\n%s\n</select>\n'
            '<div class="nep-res" id="nepRes" aria-live="polite"></div>\n'
            '<script type="application/json" id="nepDatos">%s</script>\n'
            '</div>\n%s' % (opciones, json.dumps({'p': datos, 'l': leyes, 'q': QUIZA, 'o': ORD}, ensure_ascii=False,
                                                    separators=(',', ':')).replace('</', '<\\/'), tabla))


def _metodo():
    pasos = [
        ('1', 'El cargo', 'Quién ocupa qué puesto, desde cuándo y cuánto gana. Toda dependencia debe publicar su directorio desde jefe de '
         'departamento (nombre, cargo, nivel y fecha de alta), la remuneración de su personal y los contratos por honorarios '
         '(Ley General de Transparencia, art. 65, fracciones VI, VII y X).',
         [(NOMINA, 'Nómina Transparente del gobierno federal'), (PNT, 'Plataforma Nacional de Transparencia')]),
        ('2', 'Quién firmó', 'El 63 Bis pide que el servidor público haya usado su cargo para nombrar o para intervenir. Hay que saber quién '
         'manda en esa área y quién firma los nombramientos: lo dice la estructura orgánica (art. 65, fr. II) y, si no, se pide por '
         'transparencia.', [(PNT, 'Pedir el nombramiento por transparencia')]),
        ('3', 'El vínculo, con documento', 'Un parentesco solo consta si lo dice un documento: una resolución del órgano de control o del '
         'tribunal, una sentencia o lo que el propio servidor público declaró. Su declaración de intereses es pública, pero los datos de '
         'su familia se quedan en reserva (LGRA, art. 29).', [(DECLARANET, 'Declaraciones de servidores públicos federales'),
                                                              (SANCIONADOS, 'Directorio de sancionados')]),
        ('4', 'La denuncia', 'Si las piezas embonan, la puerta es el órgano interno de control de esa dependencia. La denuncia puede ser '
         'anónima y la autoridad debe guardar tu identidad (LGRA, art. 91).', [('garantias.html', 'A qué puerta tocar')]),
    ]
    return '<ol class="nep-pasos">\n%s\n</ol>' % '\n'.join(
        '<li><span class="nep-paso-n" aria-hidden="true">%s</span><div><h3>%s</h3><p>%s</p><p class="nep-ligas">%s</p></div></li>' % (
            n, t, x, ' · '.join(liga(u, e) if u.startswith('http') else '<a href="%s">%s</a>' % (u, e) for u, e in ls))
        for n, t, x, ls in pasos)


PUNTOS_CIEGOS = [
    ('Un apellido igual no es un parentesco',
     'Dos personas que se apellidan igual casi nunca son familia: en México los apellidos se repiten muchísimo. Y al revés: los '
     'suegros, los cuñados y la pareja casi nunca comparten apellido. Cruzar apellidos da falsos culpables y deja ir a los parientes '
     'por afinidad. Para nosotros es una pista para pedir documentos, nunca una acusación.'),
    ('El cruce entre dependencias',
     '«Yo contrato a tu sobrino y tú a mi hija.» El artículo 63 Bis habla de contratar en el ente público donde el servidor público '
     'ejerce sus funciones. Si el intercambio entre dependencias encaja en otra falta, como la actuación bajo conflicto de interés '
     '(art. 58) o el tráfico de influencias, lo decide la autoridad.'),
    ('El nepotismo electoral espera a 2030',
     'La prohibición constitucional se aplica a partir de las elecciones de 2030. Además, solo impide competir por el mismo cargo: '
     'el texto no prohíbe que el familiar de una gobernadora busque una senaduría o una presidencia municipal. Cada estado debía '
     'adecuar su constitución (transitorio cuarto); lo que dice la de cada uno hay que leerlo aparte.'),
    ('Los datos de la familia están en reserva',
     'La declaración de intereses es pública, salvo lo que afecta la vida privada (LGRA, art. 29): el nombre de la pareja y de los '
     'dependientes lo ve el órgano de control, no el público. Por eso, desde afuera, un parentesco casi nunca se prueba: se señala y '
     'se pide que la autoridad lo revise.'),
    ('Tener un pariente en el gobierno no es delito',
     'La ley castiga usar el cargo para nombrar o beneficiar a la familia, no que dos parientes trabajen en el servicio público. '
     'Si cada uno llegó por concurso o en otra dependencia sin intervención del otro, no hay nepotismo en el sentido del 63 Bis.'),
]


def _ciegos():
    return '<ul class="nep-ciegos">\n%s\n</ul>' % '\n'.join(
        '<li><h3>%s</h3><p>%s</p></li>' % (t, x) for t, x in PUNTOS_CIEGOS)


def _reglas():
    return ('<ul class="nep-reglas">\n'
            '<li><b>No cruzamos apellidos para señalar a nadie.</b> Un parentesco entra a la plataforma solo si lo dice un documento '
            'oficial, con su liga.</li>\n'
            '<li><b>No nombramos a los familiares</b> que no son servidores públicos ni a las personas privadas, aunque circulen en redes.</li>\n'
            '<li><b>Una acusación no es una condena</b> (Constitución, art. 20, B, fr. I): un caso señalado es un caso por aclarar.</li>\n'
            '<li><b>Quien es aludido puede responder:</b> su <a href="derecho-de-replica.html">réplica</a> se publica íntegra.</li>\n'
            '</ul>')


def _cuenta():
    uma500 = round(500 * UMA_DIA, 2)
    uma200 = round(200 * UMA_DIA, 2)
    return ('<div class="nep-cuenta">\n'
            '<p><b>🧮 La cuenta con números redondos</b> %s</p>\n'
            '<ul>\n'
            '<li>El límite penal del artículo 220 es de 500 UMA: 500 × $%.2f = <b>$%s</b>. Un contrato a un pariente por más de eso puede '
            'costar de 2 a 12 años de prisión.</li>\n'
            '<li>El límite administrativo del artículo 78 es de 200 UMA: 200 × $%.2f = <b>$%s</b>. Si la afectación pasa de ahí, la '
            'inhabilitación sube a 10 o hasta 20 años.</li>\n'
            '</ul>\n'
            '<p class="nep-nota">Con la UMA diaria de 2026, $%.2f (%s). Las leyes la toman «en el momento de cometerse» la falta o el '
            'delito, así que en otro año la cifra cambia.</p>\n'
            '</div>') % (DER, UMA_DIA, format(uma500, ',.2f'), UMA_DIA, format(uma200, ',.2f'), UMA_DIA, liga(INEGI_UMA, 'INEGI'))


SIGUE = [
    ('Las leyes de responsabilidades de los 32 estados y lo que obligan a sus municipios: nepotismo, declaraciones, gastos y adjudicaciones', LGRA),
    ('Cuántas personas han sido sancionadas por nepotismo: el directorio de sancionados, por falta', SANCIONADOS),
    ('Cómo armonizaron los estados el nepotismo electoral (transitorio cuarto, DOF 01-04-2025)', CPEUM),
    ('Los casos que nos traigas: cada uno con el cargo, quién firmó y el documento del vínculo', 'comunidad-tema.html'),
]


ENTRADA = ('Nepotismo es usar un cargo público para dar trabajo, contratos o permisos a la familia. En México lo castigan tres leyes, '
           'cada una a su manera, y el parentesco se cuenta por grados, como lo dice el Código Civil. Aquí sabrás qué parientes '
           'alcanza cada ley, cómo se investiga un cargo con datos públicos y por qué un apellido igual no prueba nada %s.') % OF

ESTILOS = ['nepotismo.css']
SCRIPTS = ['nepotismo.js']


def secciones():
    """Las partes de la aplicación, en orden: (id, titulo, texto, bloque)."""
    return [(x['id'], x['titulo'], x['texto'], x['bloque']) for x in [{'id': 'calculadora', 'titulo': '🧮 ¿Esta persona cuenta como familia para la ley?',
             'texto': 'Elige el parentesco y te decimos qué grado es y qué ley lo alcanza. No busca a nadie: lee la ley.',
             'tarjetas': [], 'bloque': _calculadora()},
            {'id': 'grados', 'titulo': '🌳 Cómo se cuentan los grados',
             'texto': ('Cada generación es un grado (Código Civil Federal, art. 296). En línea recta se cuentan las generaciones; entre '
                       'colaterales se sube hasta el pariente en común y se baja por la otra línea, sin contarlo (arts. 299 y 300). '
                       'La afinidad nace del matrimonio y une a cada cónyuge con los parientes del otro (art. 294). '
                       'En color, lo que alcanza la ley de nepotismo: %s.') % liga(CCF, 'Código Civil Federal'),
             'tarjetas': [], 'bloque': ('<figure class="nep-fig" tabindex="0" aria-label="Árbol de grados de parentesco: en celular, deslízalo para verlo completo">%s<figcaption><span class="nep-ley nep-ley-si"></span> La ley de nepotismo lo '
                                        'alcanza (consanguinidad hasta el 4º, afinidad hasta el 2º y el cónyuge). '
                                        '<span class="nep-ley nep-ley-no"></span> Fuera de su alcance.</figcaption></figure>') % arbol_svg()},
            {'id': 'tres-leyes', 'titulo': '⚖️ Tres leyes, tres preguntas distintas',
             'texto': 'Contratar a un pariente, darle un contrato y heredarle el cargo no son lo mismo, ni lo castiga la misma autoridad.',
             'tarjetas': [], 'bloque': _tabla_leyes() + '\n' + _cuenta()},
            {'id': 'como-se-investiga', 'titulo': '🔎 Cómo se investiga un cargo',
             'texto': 'Cuatro piezas, en orden. Si falta una, el caso no está listo: se dice qué falta y a quién le toca publicarlo.',
             'tarjetas': [], 'bloque': _metodo()},
            {'id': 'puntos-ciegos', 'titulo': '👁️ Puntos ciegos',
             'texto': 'Lo que casi nadie dice cuando circula una lista de «familiares en el gobierno».',
             'tarjetas': [], 'bloque': _ciegos()},
            {'id': 'nuestras-reglas', 'titulo': '🛡️ Nuestras reglas para estos casos',
             'texto': 'Investigar parentescos toca la vida privada de personas que no eligieron estar en una nota.',
             'tarjetas': [], 'bloque': _reglas()},
            {'id': 'lo-que-sigue', 'titulo': '🗓️ Lo que sigue',
             'texto': 'Lo que falta revisar para seguir el dinero de la familia en la nómina.',
             'tarjetas': [], 'bloque': '<ul class="nep-sigue">\n%s\n</ul>' % '\n'.join(
                 '<li>%s</li>' % (liga(u, esc(t)) if u.startswith('http') else '<a href="%s" data-puerta="tema">%s</a>' % (u, esc(t)))
                 for t, u in SIGUE)},]]


def construir(base=None, ref=None):
    """La aplicación entera en una página (séptima del Modo Inspector desde el
    28-10-2026, pedido del autor: «que todo esto del nepotismo quede como una
    aplicación dentro de la herramienta de modo inspector»). Cada parte lleva
    su h2 con id: el chat la indexa sola y llega a su ancla."""
    ss = secciones()
    indice = '<nav class="nep-indice" aria-label="Partes de la aplicación">%s</nav>' % ''.join(
        '<a href="#%s">%s</a>' % (i, t) for i, t, _, _ in ss)
    return '<div class="nep">\n%s\n%s\n</div>' % (indice, '\n'.join(
        '<section class="nep-sec" aria-labelledby="%s"><h2 class="nep-tit" id="%s">%s</h2><p class="nep-txt">%s</p>\n%s\n</section>' % (
            i, i, t, x, bl) for i, t, x, bl in ss))


# ------------------------------------------------------------- el Auditor
# Como se dice cada parentesco en la calle (texto plano, sin acentos), del
# mas especifico al mas general: el chat toma el primero que encaja.
ALIAS = [
    ('tios-abuelos', r'\bti[oa]s? abuel[oa]s?\b'),
    ('sobrinos-nietos', r'\bsobrin[oa]s? niet[oa]s?\b'),
    ('primos-segundos', r'\bprim[oa]s? segund[oa]s?\b'),
    ('abuelos-conyuge', r'\b(abuel|niet)[oa]s? de (mi|su|tu) (esposa|esposo|conyuge|marido|mujer)\b'),
    ('tios-conyuge', r'\b(ti|sobrin)[oa]s? de (mi|su|tu) (esposa|esposo|conyuge|marido|mujer)\b'),
    ('primos-conyuge', r'\bprim[oa]s? de (mi|su|tu) (esposa|esposo|conyuge|marido|mujer)\b'),
    ('concunos', r'\bconcun[oa]s?\b'),
    ('consuegros', r'\bconsuegr[oa]s?\b'),
    ('cunados', r'\bcunad[oa]s?\b'),
    ('suegros', r'\bsuegr[oa]s?\b'),
    ('yernos', r'\b(yernos?|nueras?)\b'),
    ('hijastros', r'\b(hijastr[oa]s?|entenad[oa]s?)\b'),
    ('tatarabuelos', r'\btatarabuel[oa]s?\b'),
    ('bisabuelos', r'\bbisabuel[oa]s?\b'),
    ('bisnietos', r'\bbisniet[oa]s?\b'),
    ('concubino', r'\b(concubin[oa]s?|union libre|union de hecho)\b'),
    ('conyuge', r'\b(esposa|esposo|conyuge|marido)\b'),
    ('abuelos', r'\babuel[oa]s?\b'),
    ('nietos', r'\bniet[oa]s?\b'),
    ('primos', r'\bprim[oa]s?( hermano| hermana)?s?\b'),
    ('sobrinos', r'\bsobrin[oa]s?\b'),
    ('tios', r'\bti[oa]s?\b'),
    ('hermanos', r'\bherman[oa]s?\b'),
    ('hijos', r'\b(hij[oa]s?|adoptad[oa]s?)\b'),
    ('padres', r'\b(papa|mama|padre|madre|papas)\b'),
]


def _fu(que, url):
    return {'que': que, 'e': 'oficial', 'fu': url}


def bot():
    """Lo que lee asistente-charla.js (D.nep): la misma tabla de la
    calculadora y cuatro temas con el texto de la página."""
    pag = ARCHIVO
    t = {
        'general': {
            'tit': 'Nepotismo: cuándo darle trabajo a la familia es falta',
            'h': ('<p>Comete <b>nepotismo</b> el servidor público que, valiéndose de su cargo, <b>nombra, designa o interviene</b> para que se '
                  'contrate en el ente público donde trabaja a su cónyuge, a su concubina o concubino, o a un pariente <b>por consanguinidad '
                  'hasta el cuarto grado</b> (de padres e hijos a primos hermanos) o <b>por afinidad hasta el segundo</b> (suegros y cuñados). '
                  'Es una falta administrativa grave: la sanciona el tribunal con suspensión, destitución, multa o inhabilitación, y prescribe en siete años.</p>'
                  '<p>Si en lugar de una plaza le da un <b>contrato, una concesión o un permiso</b> que lo beneficie, puede ser delito (ejercicio abusivo de '
                  'funciones). Y desde las elecciones de <b>2030</b>, su familia no podrá competir por su mismo cargo.</p>'
                  '<p class="pa-chico">Tener un pariente en el gobierno no es falta: lo es usar el cargo para nombrarlo. Un apellido igual no prueba un parentesco.</p>'),
            'fu': [_fu('Nepotismo, falta grave (art. 63 Bis, adicionado DOF 19-11-2019)', LGRA), _fu('Sanciones (art. 78) y prescripción (art. 74)', LGRA),
                   _fu('Ejercicio abusivo de funciones (art. 220)', CPF), _fu('Grados de parentesco (arts. 292 a 300)', CCF)],
            'ir': [pag, 'Nepotismo y cargos públicos'],
            'sug': ['¿Mi cuñado puede trabajar en mi oficina?', '¿Cómo investigo si un funcionario contrató a su familia?', '¿Qué es el nepotismo electoral?']},
        'electoral': {
            'tit': 'Nepotismo electoral: la familia no podrá heredar el cargo, desde 2030',
            'h': ('<p>La reforma constitucional del <b>1 de abril de 2025</b> impide que compita por un cargo de elección quien tenga o haya tenido, '
                  'en los <b>tres años</b> anteriores a la elección, un vínculo de matrimonio, concubinato o unión de hecho, o un parentesco <b>en línea '
                  'recta sin límite</b>, <b>colateral hasta el cuarto grado</b> o <b>de afinidad hasta el segundo</b>, con quien ocupa ese cargo.</p>'
                  '<p>Vale para la Presidencia, las gubernaturas, las diputaciones federales y locales, los ayuntamientos y, en la Ciudad de México, la '
                  'jefatura de Gobierno, las diputaciones y las alcaldías. Se aplica <b>a partir de las elecciones de 2030</b>.</p>'
                  '<p class="pa-chico">Punto ciego: solo impide competir por el mismo cargo. El texto no prohíbe que el familiar de una gobernadora busque otro.</p>'),
            'fu': [_fu('Arts. 55 fr. VIII, 82 fr. VIII, 115 fr. I, 116 y 122, y transitorio segundo (DOF 01-04-2025)', CPEUM)],
            'ir': [pag + '#tres-leyes', 'Nepotismo y cargos públicos'],
            'sug': ['¿Qué es el nepotismo?', '¿Mi esposa puede ser candidata a mi cargo?', '¿Cuándo empieza la no reelección?']},
        'investigar': {
            'tit': 'Cómo se investiga si un funcionario contrató a su familia',
            'h': ('<p>Cuatro piezas, en orden:</p><ol class="pa-lista">'
                  '<li><b>El cargo:</b> quién ocupa qué puesto y desde cuándo. Toda dependencia publica su directorio, las remuneraciones y los '
                  'contratos por honorarios (Ley General de Transparencia, art. 65, fr. VI, VII y X).</li>'
                  '<li><b>Quién firmó:</b> la ley pide que el servidor público haya usado su cargo para nombrar o intervenir; la estructura orgánica '
                  'dice quién manda en esa área (fr. II), y el nombramiento se pide por transparencia.</li>'
                  '<li><b>El vínculo, con documento:</b> una resolución, una sentencia o lo que el propio servidor público declaró. Los datos de su '
                  'familia en la declaración de intereses quedan en reserva (LGRA, art. 29).</li>'
                  '<li><b>La denuncia:</b> ante el órgano interno de control; puede ser anónima (LGRA, art. 91).</li></ol>'
                  '<p class="pa-chico">Un apellido igual es una pista, nunca una prueba: los parientes por afinidad casi nunca lo comparten.</p>'),
            'fu': [_fu('Obligaciones de transparencia (art. 65)', LGTAIP), _fu('Declaraciones públicas salvo datos personales (art. 29) y denuncia anónima (art. 91)', LGRA)],
            'ir': [pag + '#como-se-investiga', 'Nepotismo y cargos públicos'],
            'sug': ['¿Por qué un apellido igual no prueba nada?', '¿Cuánto gana un funcionario federal?', '¿A dónde denuncio?']},
        'ciegos': {
            'tit': 'Por qué un apellido igual no prueba un parentesco',
            'h': ''.join('<p><b>%s.</b> %s</p>' % (a, b) for a, b in PUNTOS_CIEGOS[:2]) +
                 '<p class="pa-chico">Por eso no cruzamos apellidos para señalar a nadie: un parentesco entra a la plataforma solo si lo dice un documento oficial.</p>',
            'fu': [_fu('Nepotismo (art. 63 Bis) y conflicto de interés (art. 58)', LGRA)],
            'ir': [pag + '#puntos-ciegos', 'Nepotismo y cargos públicos'],
            'sug': ['¿Cómo investigo si un funcionario contrató a su familia?', '¿Qué es el nepotismo?']},
    }
    return {'p': alcance(), 'l': [{'k': k, 'n': n, 'a': a, 'u': u, 'd': d} for k, n, a, u, _, d in LEYES], 'q': QUIZA, 'o': ORD,
            'al': ALIAS, 't': t, 'pag': [pag, 'Nepotismo y cargos públicos']}
