# -*- coding: utf-8 -*-
"""Noticias relevantes y personajes, dentro del chat del Auditor Virtual
(pedido del autor, 24-10-2026: «que se integre también al chat lo de
noticias relevantes que se encuentra en la tarjeta de Aprende, para que al
momento en que el usuario ingrese el nombre de algún personaje político se
le dé una información no tan evidente como podría encontrar en otros
lugares (...) así como también de cuestiones que se puedan localizar en
internet»).

No hay una sola cifra nueva. Todo sale de assets/auditor/js/columnas.js,
lo mismo que pinta noticias-relevantes.html:

- Cada columna entra a la búsqueda como una ficha («columna»), con su
  balazo, su dato curioso, sus cifras con su estado y sus documentos.
- Cada personaje lleva sus columnas y, lo menos evidente, lo que circula
  sobre él y la plataforma no pudo sostener con un documento oficial
  (DESCARTADO de columnas.js), con el motivo. Decir qué no se puede
  probar también es información.
- Lo que está en internet no lo afirma el Auditor: el chat ofrece las
  búsquedas ya armadas en los portales oficiales y en las noticias,
  rotuladas como «sin verificar», y lleva a «Contrasta una nota» para
  cotejar lo que el lector encuentre (AGENTS.md §2 y §5 ter).

Un personaje nuevo necesita su renglón en PERSONAJES. Si sus palabras no
aparecen en ninguna columna ni en lo descartado, la generación se detiene:
un nombre sin documento detrás no entra al chat.
"""
import json
import os
import re
import unicodedata

from apartados import RAIZ

COLUMNAS_JS = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'columnas.js')
PAGINA = 'noticias-relevantes.html'

# (id, nombre, cómo se dice en la calle, presidente[, columnas]). Las
# columnas se encuentran solas por sus palabras; solo se dicen a mano cuando
# la columna nombra a la persona a medias (la de 1861 dice «Juárez», que
# también es medio país de municipios). Las palabras van sin
# acentos y en minúsculas. «pres» marca a quien también tiene estado de
# cuenta de su administración: su nombre a secas lo sigue contestando el
# estado de cuenta; las columnas salen cuando se pregunta por noticias,
# procesos o «quién es».
PERSONAJES = [
    ('garcia-luna', 'Genaro García Luna', ['garcia luna', 'genaro garcia'], False),
    ('garcia-harfuch', 'Omar García Harfuch', ['garcia harfuch', 'harfuch', 'omar garcia'], False),
    ('abelina-lopez', 'Abelina López Rodríguez', ['abelina'], False, ['abelina-lopez-corte-invalida-auditoria-estatal']),
    ('cardenas-palomino', 'Luis Cárdenas Palomino', ['cardenas palomino'], False),
    ('ignacio-ovalle', 'Ignacio Ovalle Fernández', ['ovalle'], False),
    ('leonel-cota', 'Leonel Cota Montaño', ['leonel cota', 'cota montano'], False),
    ('emilio-lozoya', 'Emilio Lozoya Austin', ['lozoya'], False),
    ('rosario-robles', 'Rosario Robles Berlanga', ['rosario robles', 'robles berlanga'], False),
    ('elba-esther', 'Elba Esther Gordillo', ['elba esther', 'gordillo'], False),
    ('gomez-urrutia', 'Napoleón Gómez Urrutia', ['gomez urrutia', 'napoleon gomez'], False),
    ('romero-deschamps', 'Carlos Romero Deschamps', ['romero deschamps'], False),
    ('raul-salinas', 'Raúl Salinas de Gortari', ['raul salinas'], False),
    ('lopez-beltran', 'Andrés López Beltrán', ['lopez beltran', 'andy lopez'], False),
    ('amilcar-olan', 'Amílcar Olán', ['amilcar olan', 'olan aparicio'], False),
    ('taddei', 'Guadalupe Taddei Zavala', ['taddei', 'guadalupe taddei'], False),
    ('lorenzo-cordova', 'Lorenzo Córdova Vianello', ['lorenzo cordova', 'cordova vianello'], False),
    ('carvente', 'Víctor Hugo Carvente Contreras', ['carvente', 'victor hugo carvente'], False),
    ('bartlett', 'Manuel Bartlett Díaz', ['bartlett'], False),
    ('alfonso-durazo', 'Alfonso Durazo Montaño', ['durazo'], False),
    ('pablo-gomez', 'Pablo Gómez Álvarez', ['pablo gomez'], False),
    ('santa-anna', 'Antonio López de Santa Anna', ['santa anna', 'santanna'], False),
    ('benito-juarez', 'Benito Juárez', ['benito juarez'], False, ['juarez-suspension-de-pagos-1861']),
    ('lerdo-de-tejada', 'Sebastián Lerdo de Tejada', ['lerdo de tejada'], False),
    ('limantour', 'José Yves Limantour', ['limantour'], False),
    ('porfirio-diaz', 'Porfirio Díaz', ['porfirio diaz', 'porfirio'], False),
    ('elias-calles', 'Plutarco Elías Calles', ['plutarco', 'elias calles'], False),
    ('pena-nieto', 'Enrique Peña Nieto', ['pena nieto', 'enrique pena'], True),
    ('salinas-de-gortari', 'Carlos Salinas de Gortari', ['salinas de gortari', 'carlos salinas'], True),
    ('lopez-obrador', 'Andrés Manuel López Obrador', ['lopez obrador', 'amlo'], True),
    ('sheinbaum', 'Claudia Sheinbaum Pardo', ['sheinbaum'], True),
    ('vicente-fox', 'Vicente Fox Quesada', ['amigos de fox', 'vicente fox'], True),
]

# Las empresas contratistas que nombra un documento oficial citado en una
# columna (pedido del autor, 26-10-2026: «integrar esas empresas, esas
# contratistas, dentro de nuestro portal de búsquedas del SAT o de la UIF»).
# Mismo formato que PERSONAJES; el chat las contesta igual, con sus
# columnas, y con búsquedas armadas en los registros oficiales de
# contratistas (WEB_EMPRESA). Una empresa nueva necesita su renglón aquí, y
# si no aparece en ninguna columna ni en lo descartado, la generación se
# detiene. A los particulares (dueños, apoderados, familiares) no se les
# agrega: la empresa es la que contrata con el gobierno.
EMPRESAS = [
    ('cyber-robotic', 'Cyber Robotic Solutions, S.A. de C.V.', ['cyber robotic', 'cyber robotics'], False),
    ('cajas-graf', 'Cajas Graf, S.A. de C.V.', ['cajas graf', 'cajas graff'], False),
    ('biosistemas', 'Biosistemas y Seguridad Privada, S.A. de C.V.', ['biosistemas', 'biosistemas y seguridad privada'], False),
    ('amigo-gnl', 'AMIGO LNG (American Mexican Integrated Gas Operations)', ['amigo lng', 'amigo gnl', 'american mexican integrated', 'proyecto amigo', 'epcilon', 'epcilon lng'], False),
]

# Lo descartado se encuentra por el nombre; cuando el renglón no lo trae
# (el tema dice «Deudas de CAPAMA», no «Abelina»), se dice aquí por su tema.
# Cada tema tiene que existir en DESCARTADO, o la generación se detiene.
DESC_TEMAS = {
    'abelina-lopez': ['mas de 600 millones', 'scjn 101 2026', 'no es exoneracion', 'ministro instructor', 'capama',
                      '4 500 mdp anuales', 'otis y john', '20 000 pesos en tribuna', 'trayectoria y situacion actual',
                      'observaciones de la asf publicada en prensa'],
    'lopez-beltran': ['romedic', 'portacelis', 'balasto del tren maya', 'el clan', 'malecon de villahermosa',
                      'ninos con cancer', 'denuncia de la diputada', 'investigaciones de la fgr', 'uif'],
    'garcia-luna': ['pruebas no testimoniales', 'coimputado', 'testis unus', 'testimonios especificos',
                    'dichos sobre terceros', 'frase del juez cogan', 'testigos cooperantes', 'estado de la apelacion',
                    'red de empresas y contratos', 'reglas de evidencia'],
}

# Un nombre que también es un lugar (la alcaldía Benito Juárez, los
# municipios Juárez) solo se toma como persona si la pregunta habla de
# personas. Se dice aquí para que el chat no se adueñe del municipio.
TAMBIEN_LUGAR = {'benito-juarez', 'porfirio-diaz'}

# Las búsquedas que el chat arma en internet (24-10-2026). Son búsquedas,
# no resultados: el chat no lee lo que salga ni lo afirma. Van primero los
# portales oficiales y al final las noticias, rotuladas como prensa.
WEB = [
    ('🏛️', 'Documentos del Gobierno de México', 'oficial', 'site:gob.mx'),
    ('📜', 'Diario Oficial de la Federación', 'oficial', 'site:dof.gob.mx'),
    ('🔎', 'Auditoría Superior de la Federación', 'oficial', 'site:asf.gob.mx'),
    ('⚖️', 'Suprema Corte y Poder Judicial', 'oficial', 'site:scjn.gob.mx OR site:cjf.gob.mx'),
    ('🏛️', 'Cámara de Diputados y Senado', 'oficial', 'site:diputados.gob.mx OR site:senado.gob.mx'),
    ('🗳️', 'Instituto Nacional Electoral', 'oficial', 'site:ine.mx'),
    ('📰', 'Noticias (prensa, sin verificar)', 'prensa', None),
]

# Para una empresa: dónde se ve si contrató con el gobierno, si la
# sancionaron o si la autoridad la señaló. Las que empiezan con https se
# abren tal cual (el portal no acepta búsqueda por enlace).
WEB_EMPRESA = [
    ('🧾', 'Sus contratos con el gobierno (ComprasMX)', 'oficial', 'https://comprasmx.buengobierno.gob.mx/'),
    ('⛔', 'Directorio de proveedores y contratistas sancionados', 'oficial', 'https://directoriosancionados.buengobierno.gob.mx/'),
    ('📜', 'Diario Oficial: circulares de inhabilitación', 'oficial', 'site:dof.gob.mx'),
    ('🔎', 'Auditoría Superior de la Federación', 'oficial', 'site:asf.gob.mx'),
    ('💸', 'Unidad de Inteligencia Financiera (comunicados de Hacienda)', 'oficial', 'site:gob.mx/shcp UIF'),
    ('🇺🇸', 'Lista de sancionados del Tesoro de EE. UU. (OFAC)', 'oficial', 'https://sanctionssearch.ofac.treas.gov/'),
    ('📰', 'Noticias (prensa, sin verificar)', 'prensa', None),
]


# La regla de las columnas (columnas.js), dicha también en el chat y en el
# dictamen.
NOTA = ('Un proceso no es una condena, y una observación de la ASF «por aclarar» no es un robo probado: '
        'la columna dice lo que consta en los documentos que cita, con presunción de inocencia.')


def plano(t):
    t = unicodedata.normalize('NFD', str(t or ''))
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower()
    return ' ' + re.sub(r'[^a-z0-9ñ]+', ' ', t).strip() + ' '


def _arreglo(s, nombre):
    """Lee un arreglo JSON de columnas.js (var NOMBRE = [...])."""
    i = s.index('var %s = ' % nombre) + len('var %s = ' % nombre)
    prof = 0
    for j in range(i, len(s)):
        if s[j] == '[':
            prof += 1
        elif s[j] == ']':
            prof -= 1
            if not prof:
                return json.loads(s[i:j + 1])
    raise SystemExit('columnas.js: no se pudo leer %s' % nombre)


def columnas():
    s = open(COLUMNAS_JS, encoding='utf-8').read()
    return _arreglo(s, 'COLUMNAS'), _arreglo(s, 'DESCARTADO')


def _texto(c):
    return ' '.join([c['titulo'], c.get('balazo', '')] + c.get('cuerpo', []) + [c.get('dato_curioso', '')]
                    + [x['dice'] for x in c.get('cotejo', [])])


# Verificamos (26-10-2026): cómo se dice cada resultado del cotejo.
RES = {'consta': 'Consta', 'matiz': 'Consta, con matices', 'no consta': 'Sin documento oficial', 'pendiente': 'Pendiente'}


def _cotejo(c):
    """El cotejo de lo que circula en redes, para el chat y el dictamen."""
    out = []
    for n, x in enumerate(c.get('cotejo', []), 1):
        if x['res'] not in RES:
            raise SystemExit('asistente_personajes: «%s» trae un resultado desconocido: %s' % (c['id'], x['res']))
        if x['res'] == 'pendiente' and not (x.get('quien') and x.get('donde')):
            raise SystemExit('asistente_personajes: un pendiente del cotejo de «%s» no dice a quién le toca ni dónde '
                             'debería estar (AGENTS.md §2).' % c['id'])
        out.append({'d': x['dice'], 'r': x['res'], 'x': x['explica'], 'fu': {'tx': x['fuente'], 'url': x.get('url') or None},
                    'p': 'red-%s-%d' % (c['id'], n) if x['res'] == 'pendiente' else None})
    return out


def fichas():
    """Cada columna, como ficha de la búsqueda del chat."""
    cols, _ = columnas()
    out = []
    for c in cols:
        ci = [{'v': x['valor'], 'etq': x['etq'], 'e': x['estado'], 'fu': {'tx': x['fuente'], 'url': x.get('url')}}
              for x in c.get('cifras', [])]
        fu = [{'tx': x['nombre'], 'url': x.get('url')} for x in c.get('fuentes', [])]
        cot = _cotejo(c)
        cir = c.get('circula')
        out.append({'t': 'columna', 'tit': c['titulo'], 'txt': c.get('balazo', ''),
                    'cir': cir and {'tx': cir['texto'], 'q': '%s · %s · %s' % (cir['cuenta'], cir['red'], cir['fecha'])},
                    'cot': cot, 'sigue': [{'tx': x['que'], 'url': x['url']} for x in c.get('sigue', [])],
                    'dc': c.get('dato_curioso', ''), 'act': c.get('actualizado', ''),
                    'ci': ci, 'fu': fu, 'col': c['id'], 'nota': NOTA,
                    'ir': [PAGINA + '#col-' + c['id'], 'Noticias relevantes'],
                    'k': 'noticias columna %s %s %s' % (
                        c['seccion'] + (' verificamos redes es cierto circula' if cot else ''),
                        cir['texto'] if cir else '', ' '.join(c.get('cuerpo', []))[:900])})
    return out


def datos():
    """El índice de personajes del chat: sus columnas y lo descartado."""
    cols, desc = columnas()
    textos = [(c, plano(_texto(c)), plano(c['titulo'])) for c in cols]
    out = []
    ids = {c['id'] for c in cols}
    for renglon in PERSONAJES + EMPRESAS:
        pid, nombre, al, pres = renglon[:4]
        cs = [(0, i) for i in (renglon[4] if len(renglon) > 4 else [])]
        for _, i in cs:
            if i not in ids:
                raise SystemExit('asistente_personajes: la columna «%s» de %s no existe' % (i, nombre))
        for c, t, tit in textos:
            if c['id'] not in [i for _, i in cs] and any(' %s ' % a in t for a in al):
                # Primero las columnas que lo traen en el título.
                cs.append((0 if any(' %s ' % a in tit for a in al) else 1, c['id']))
        temas = DESC_TEMAS.get(pid, [])
        for t in temas:
            if not any(' %s ' % t in plano(d['tema']) for d in desc):
                raise SystemExit('asistente_personajes: ningún descartado tiene el tema «%s» (%s)' % (t, nombre))
        ds = [{'tema': d['tema'], 'af': d['afirmacion'], 'mo': d['motivo']} for d in desc
              if any(' %s ' % a in plano(d['tema'] + ' ' + d['afirmacion']) for a in al)
              or any(' %s ' % t in plano(d['tema']) for t in temas)]
        # Lo que circula en redes sobre él y no tiene documento (Verificamos).
        for c, t, _ in textos:
            if any(' %s ' % a in t for a in al):
                ds += [{'tema': c['titulo'], 'af': x['dice'], 'mo': x['explica']} for x in c.get('cotejo', [])
                       if x['res'] in ('no consta', 'pendiente')]
        if not cs and not ds:
            raise SystemExit('asistente_personajes: «%s» no aparece en ninguna columna ni en lo descartado: '
                             'un nombre sin documento detrás no entra al chat.' % nombre)
        out.append({'id': pid, 'n': nombre, 'al': al, 'pres': pres, 'lugar': pid in TAMBIEN_LUGAR,
                    'emp': renglon in EMPRESAS,
                    'col': [i for _, i in sorted(cs)], 'desc': ds[:10], 'descn': len(ds)})
    # Ningún personaje repetido: dos renglones con la misma palabra se pisan.
    vistas = {}
    for p in out:
        for a in p['al']:
            if a in vistas:
                raise SystemExit('asistente_personajes: «%s» está en %s y en %s' % (a, vistas[a], p['id']))
            vistas[a] = p['id']
    return {'per': out, 'web': [{'ico': i, 'n': n, 'e': e, 'site': s} for i, n, e, s in WEB],
            'webEmp': [{'ico': i, 'n': n, 'e': e, 'site': s} for i, n, e, s in WEB_EMPRESA],
            'pag': PAGINA, 'n': len(cols)}
