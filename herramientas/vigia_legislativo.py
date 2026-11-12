# -*- coding: utf-8 -*-
"""Vigía legislativo (encargo del autor, 05-11-2026: «un agente que esté al
pendiente de todas las publicaciones de leyes y reformas… para estar a lo
último actualizado y así ir llenando nuestra base de datos»).

Qué hace, en tres pasos:

1. Lee el **sumario del DOF** del día (https://dof.gob.mx/sumario.xml, un RSS)
   y se queda con los decretos que tocan alguna ley de LEYES.
2. Lee el **índice de Leyes Federales Vigentes** de la Cámara de Diputados
   (LeyesBiblio/index.htm): cada ley con su fecha de publicación y de última
   reforma. Si una fecha cambió desde la corrida anterior, también es hallazgo.
3. **El cruce que más vale:** busca en el código de la plataforma cada «última
   reforma DOF dd-mm-aaaa» que citamos y la compara con la que dice
   Diputados. Si citamos una más vieja, es un aviso: ese módulo quedó viejo.

Lo escribe todo en docs/legislativo/bandeja.json, rotulado «por cotejar».
**El vigía detecta y propone; nunca escribe en la base** (AGENTS.md §2): de
cada publicación guarda solo el título, la fecha y la liga, nunca el texto de
la reforma. Lo aprueba una persona, y la aprobada pasa a su módulo con su
vigencia.

El Senado no está: su portal respondió 403 al construir esto (05-11-2026) y
no da una lista que se pueda leer sin adivinar. Lo que aprueba el Senado
llega igual al DOF cuando se publica, que es cuando obliga.

    python3 herramientas/vigia_legislativo.py            # baja y guarda
    python3 herramientas/vigia_legislativo.py --prueba   # sin red, con ejemplos
    python3 herramientas/vigia_legislativo.py --citas    # solo el cruce, con el índice guardado

Corre a mano o desde GitHub (.github/workflows/vigia-legislativo.yml).

Para quien aprende Python, lo que se usa aquí:
- urllib.request: bajar una página sin instalar nada (la plataforma no usa
  «pip install»; todo es de la biblioteca estándar).
- xml.etree.ElementTree: leer el RSS del DOF, que es XML bien formado.
- re (expresiones regulares): el índice de Diputados es HTML de los años 2000,
  sin estructura limpia; se parte por renglones de tabla (<tr>) y en cada uno
  se buscan patrones fijos («DOF dd/mm/aaaa», «ref/clave.htm»).
- unicodedata: quitar acentos para comparar nombres sin que «Código» y
  «codigo» parezcan distintos.
"""
import datetime
import glob
import html
import json
import os
import re
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'legislativo', 'bandeja.json')
DOF_RSS = 'https://dof.gob.mx/sumario.xml'
LB = 'https://www.diputados.gob.mx/LeyesBiblio/'
INDICE = LB + 'index.htm'
MAXIMO = 300        # hallazgos que se conservan en la bandeja
AGENTE = 'Auditavision-vigia/1.0 (+https://github.com/uzoraproductos-arch/a)'

# Las leyes que vigila. Cada renglón: (clave, nombre, clave en LeyesBiblio,
# expresiones con que la nombramos en el texto). La clave de LeyesBiblio es la
# del enlace «ref/<clave>.htm» del índice (cotejada el 05-11-2026). None
# quiere decir que no está en ese índice (el PEF es un decreto, no una ley):
# entonces solo se vigila en el DOF.
# Las expresiones van sin acentos y en minúsculas, porque el texto se compara
# ya «aplanado» (ver plano()). \b es «borde de palabra»: evita que
# «constitucion» se encuentre dentro de «constitucional».
LEYES = [
    # Las que pidió el autor para empezar (encargo, §1)
    ('cpeum', 'Constitución Política de los Estados Unidos Mexicanos', 'cpeum', [r'\bconstitucion politica\b', r'\bconstitucion\b(?!al)', r'\bcpeum\b']),
    ('cff', 'Código Fiscal de la Federación', 'cff', [r'codigo fiscal de la federacion', r'\bcff\b']),
    ('lisr', 'Ley del Impuesto sobre la Renta', 'lisr', [r'impuesto sobre la renta', r'\blisr\b']),
    ('liva', 'Ley del Impuesto al Valor Agregado', 'liva', [r'impuesto al valor agregado', r'\bliva\b']),
    ('lieps', 'Ley del Impuesto Especial sobre Producción y Servicios', 'lieps', [r'impuesto especial sobre produccion', r'ley del ieps', r'\blieps\b']),
    ('lfd', 'Ley Federal de Derechos', 'lfd', [r'ley federal de derechos', r'\blfd\b']),
    ('lif', 'Ley de Ingresos de la Federación (del año)', 'lif_*', [r'ley de ingresos de la federacion', r'\blif\b']),
    ('pef', 'Presupuesto de Egresos de la Federación (del año)', None, [r'presupuesto de egresos de la federacion', r'\bpef\b']),
    ('lfprh', 'Ley Federal de Presupuesto y Responsabilidad Hacendaria', 'lfprh', [r'presupuesto y responsabilidad hacendaria', r'\blfprh\b']),
    ('ldf', 'Ley de Disciplina Financiera de las Entidades Federativas y los Municipios', 'ldfefm', [r'disciplina financiera', r'\bldf\b']),
    ('lgcg', 'Ley General de Contabilidad Gubernamental', 'lgcg', [r'contabilidad gubernamental', r'\blgcg\b']),
    ('lfrcf', 'Ley de Fiscalización y Rendición de Cuentas de la Federación', 'lfrcf', [r'fiscalizacion y rendicion de cuentas', r'\blfrcf\b']),
    ('lgra', 'Ley General de Responsabilidades Administrativas', 'lgra', [r'responsabilidades administrativas', r'\blgra\b']),
    ('laassp', 'Ley de Adquisiciones, Arrendamientos y Servicios del Sector Público', 'laassp', [r'ley de adquisiciones, arrendamientos', r'\blaassp\b']),
    ('lopsrm', 'Ley de Obras Públicas y Servicios Relacionados con las Mismas', 'lopsrm', [r'ley de obras publicas y servicios', r'\blopsrm\b']),
    ('lritf', 'Ley para Regular las Instituciones de Tecnología Financiera (Ley Fintech)', 'lritf', [r'instituciones de tecnologia financiera', r'ley fintech', r'\blritf\b']),
    # ¿Quién responde por tu ahorro? (ahorro_protegido.py, 12-11-2026)
    ('lpab', 'Ley de Protección al Ahorro Bancario', 'lpab', [r'proteccion al ahorro bancario', r'\blpab\b']),
    ('lacp', 'Ley de Ahorro y Crédito Popular', 'lacp', [r'ahorro y credito popular', r'\blacp\b']),
    ('lmv', 'Ley del Mercado de Valores', 'lmv', [r'ley del mercado de valores', r'\blmv\b']),
    ('lfpiorpi', 'Ley Federal para la Prevención e Identificación de Operaciones con Recursos de Procedencia Ilícita (antilavado)', 'lfpiorpi',
     [r'recursos de procedencia ilicita', r'\blfpiorpi\b']),
    ('lfpdppp', 'Ley Federal de Protección de Datos Personales en Posesión de los Particulares', 'lfpdppp',
     [r'datos personales en posesion de los particulares', r'\blfpdppp\b']),
    # Las que la plataforma ya cita en sus módulos (para el cruce)
    ('lcf', 'Ley de Coordinación Fiscal', 'lcf', [r'ley de coordinacion fiscal', r'\blcf\b']),
    ('lih', 'Ley de Ingresos sobre Hidrocarburos', 'lih', [r'ingresos sobre hidrocarburos', r'\blih\b']),
    ('lgtaip', 'Ley General de Transparencia y Acceso a la Información Pública', 'lgtaip', [r'ley general de transparencia', r'\blgtaip\b']),
    ('lgpdppso', 'Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados', 'lgpdppso', [r'datos personales en posesion de sujetos', r'\blgpdppso\b']),
    ('lamp', 'Ley de Amparo', 'lamp', [r'ley de amparo']),
    ('lgipe', 'Ley General de Instituciones y Procedimientos Electorales', 'lgipe', [r'instituciones y procedimientos electorales', r'\blgipe\b']),
    ('lgpp', 'Ley General de Partidos Políticos', 'lgpp', [r'partidos politicos', r'\blgpp\b']),
    ('lss', 'Ley del Seguro Social', 'lss', [r'ley del seguro social', r'\blss\b']),
    ('lgs', 'Ley General de Salud', 'lgs', [r'ley general de salud', r'\blgs\b']),
    ('lft', 'Ley Federal del Trabajo', 'lft', [r'ley federal del trabajo', r'\blft\b']),
    ('loapf', 'Ley Orgánica de la Administración Pública Federal', 'loapf', [r'organica de la administracion publica federal', r'\bloapf\b']),
    ('lgeepa', 'Ley General del Equilibrio Ecológico y la Protección al Ambiente', 'lgeepa', [r'equilibrio ecologico', r'\blgeepa\b']),
    ('lgpgir', 'Ley General para la Prevención y Gestión Integral de los Residuos', 'lgpgir', [r'gestion integral de los residuos', r'\blgpgir\b']),
    ('replica', 'Ley Reglamentaria del artículo 6o. constitucional en materia del Derecho de Réplica', 'lrart6_mdr', [r'derecho de replica']),
    ('cpf', 'Código Penal Federal', 'cpf', [r'codigo penal federal', r'\bcpf\b']),
    ('ccf', 'Código Civil Federal', 'ccf', [r'codigo civil federal', r'\bccf\b']),
    ('cnpp', 'Código Nacional de Procedimientos Penales', 'cnpp', [r'codigo nacional de procedimientos penales', r'\bcnpp\b']),
]

# Palabras que dicen que una publicación del DOF cambia una ley (y no solo la
# menciona, como un convenio que «con fundamento en la Ley de…» hace otra cosa).
CAMBIA = re.compile(r'\b(decreto|reforma|reforman|adiciona|adicionan|deroga|derogan|abroga|expide|aclaracion|fe de erratas)\b')

# Cómo citamos una reforma en el texto: «última reforma DOF 15-12-2025»,
# «ultima reforma, 28 de noviembre de 2025», «última reforma DOF 14/11/2025».
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
CITA = re.compile(r'ultima reforma[^0-9a-z]{0,6}(?:publicada )?(?:en el )?(?:del )?(?:dof[^0-9a-z]{0,3})?'
                  r'(\d{1,2})(?:[-/](\d{1,2})[-/]| de (' + '|'.join(MESES) + r') de )(\d{4})')
# Los archivos que no se revisan: este (sus ejemplos no son citas) y los que
# arman la frase con una variable («última reforma DOF %s»).
NO_REVISAR = {'vigia_legislativo.py'}


def plano(t):
    """Sin acentos y en minúsculas: «Código» y «codigo» se vuelven iguales.
    NFKD separa la letra de su acento («ó» → «o» + «´») y luego se tira el acento.
    Ojo: la ñ también se vuelve n; para comparar nombres de leyes no estorba."""
    t = unicodedata.normalize('NFKD', t)
    return ''.join(c for c in t if not unicodedata.combining(c)).lower()


def ddmmaaaa(d, m, a):
    return '%02d-%02d-%04d' % (int(d), int(m), int(a))


def orden(f):
    """«15-12-2025» → (2025, 12, 15), para comparar fechas como tuplas: Python
    compara tuplas elemento por elemento, así que el año manda, luego el mes."""
    d, m, a = f.split('-')
    return (int(a), int(m), int(d))


def bajar(url):
    pet = urllib.request.Request(url, headers={'User-Agent': AGENTE})
    with urllib.request.urlopen(pet, timeout=40) as r:
        return r.read()


# --- 1. El sumario del DOF ---------------------------------------------------

def de_que_ley(texto):
    """Las claves de LEYES que nombra un texto (ya aplanado)."""
    return [c for c, _n, _r, al in LEYES if any(re.search(a, texto) for a in al)]


def articulos(titulo):
    """«…se reforman los artículos 17-H, 69-B y 82 del…» → «17-H, 69-B y 82».
    Solo si el título lo dice; si no, queda vacío (no se adivina)."""
    m = re.search(r'art[ií]culos? ((?:\d+[\w-]*(?:, | y | e )?)+)', titulo)
    return m.group(1).strip(' ,') if m else ''


def leer_dof(xml):
    """Del RSS del DOF: cada publicación que cambia una ley vigilada."""
    raiz = ET.fromstring(xml)
    out = []
    for it in raiz.iter('item'):
        # El DOF pone el título del decreto en <description>, con acentos
        # escritos como entidades HTML (&oacute;): html.unescape los vuelve letras.
        tit = ' '.join(html.unescape(it.findtext('description') or '').split())
        url = (it.findtext('link') or '').strip()
        f = (it.findtext('valueDate') or '').strip()
        p = plano(tit)
        leyes = de_que_ley(p)
        if not tit or not leyes or not CAMBIA.search(p) or not re.match(r'https://', url):
            continue
        m = re.match(r'(\d\d)/(\d\d)/(\d{4})$', f)
        out.append({'id': 'dof-' + (re.search(r'codigo=(\d+)', url) or re.search(r'(.*)', url)).group(1),
                    'fuente': 'dof', 'leyes': leyes, 'fecha': ddmmaaaa(*m.groups()) if m else '',
                    'titulo': tit, 'articulos': articulos(tit), 'liga': url,
                    'seccion': ' '.join(html.unescape(it.findtext('title') or '').split())})
    return out


# --- 2. El índice de Diputados -----------------------------------------------

def leer_indice(texto):
    """Del índice de Leyes Federales Vigentes: {clave LeyesBiblio: datos}.
    Cada ley es un renglón <tr> con cuatro celdas <td>: número, nombre (y su
    fecha de publicación), fecha de la última reforma y las ligas al PDF."""
    leyes = {}
    for fila in re.split(r'<tr[\s>]', texto):
        ref = re.search(r'href="ref/([a-z0-9_]+)\.htm"', fila)
        celdas = re.split(r'<td[\s>]', fila)
        if not ref or len(celdas) < 5:
            continue
        nom = re.search(r'href="ref/[^"]+"[^>]*>(.*?)</a>', fila, re.S)
        nom = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', nom.group(1))).split()) if nom else ''
        pub = re.findall(r'DOF\s+(\d\d)/(\d\d)/(\d{4})', celdas[2])
        ref_ = re.findall(r'DOF\s+(\d\d)/(\d\d)/(\d{4})', celdas[3])
        pdf = re.search(r'href="pdf/([^"]+)"', fila)
        if not pub:
            continue
        clave = ref.group(1)
        if clave in leyes:      # la Constitución sale dos veces (encabezado y renglón)
            continue
        leyes[clave] = {'nombre': nom, 'publicada': ddmmaaaa(*pub[0]),
                        # Sin fecha en la tercera celda: la ley no se ha reformado
                        # desde que se publicó (la LAASSP de 2025, por ejemplo).
                        'reforma': ddmmaaaa(*ref_[-1]) if ref_ else None,
                        'pdf': pdf.group(1) if pdf else None}
    return leyes


def vigente(indice, ref):
    """La entrada del índice para una clave de LEYES. «lif_*» toma la Ley de
    Ingresos del año más reciente que tenga el índice."""
    if ref is None:
        return None, None
    if ref.endswith('_*'):
        anios = sorted(k for k in indice if re.match(ref[:-1] + r'\d{4}$', k))
        return (anios[-1], indice[anios[-1]]) if anios else (None, None)
    return ref, indice.get(ref)


def ultima(e):
    """La fecha que cuenta: la de la última reforma o, si nunca se reformó, la de publicación."""
    return e['reforma'] or e['publicada']


def cambios_indice(indice, previo):
    """Lo que cambió en el índice desde la corrida anterior: también es hallazgo
    (a veces Diputados actualiza el texto vigente antes de que lo veamos en el DOF)."""
    out = []
    for c, nom, ref, _al in LEYES:
        k, e = vigente(indice, ref)
        if not e:
            continue
        p = (previo or {}).get(c)
        if p and p.get('reforma') != ultima(e):
            out.append({'id': 'dip-%s-%s' % (c, ultima(e)), 'fuente': 'diputados', 'leyes': [c], 'fecha': ultima(e),
                        'titulo': '%s: la Cámara de Diputados registra una reforma del %s (antes decía %s).' % (e['nombre'] or nom, ultima(e), p.get('reforma')),
                        'articulos': '', 'liga': LB + 'ref/%s.htm' % k, 'seccion': 'Leyes Federales Vigentes'})
    return out


# --- 3. El cruce: lo que citamos contra lo que dice Diputados ---------------

def citas(raiz=RAIZ):
    """Cada «última reforma …» que la plataforma escribe en herramientas/*.py,
    con la ley a la que se refiere. Devuelve (archivo, renglón, clave, fecha).

    Cómo sabe de qué ley habla: mira el texto justo antes de la cita. Primero
    el tramo desde la última comilla o el último salto de línea (la cita suele
    ir dentro de una cadena: 'Ley del Seguro Social (última reforma DOF …)'), y
    ahí toma la PRIMERA ley que aparece, porque es el sujeto («Ley de Amparo,
    reglamentaria de los artículos 103 y 107 de la Constitución» es la de
    Amparo, no la Constitución). Si ese tramo no nombra ninguna, mira 250
    caracteres atrás, con los renglones juntos, y toma la ÚLTIMA (la más
    cercana a la cita)."""
    out = []
    for ruta in sorted(glob.glob(os.path.join(raiz, 'herramientas', '*.py'))):
        nombre = os.path.basename(ruta)
        if nombre in NO_REVISAR:
            continue
        t = plano(open(ruta, encoding='utf-8').read())
        for m in CITA.finditer(t):
            antes = t[max(0, m.start() - 250):m.start()]
            corte = max(antes.rfind("'"), antes.rfind('"'), antes.rfind('\n'))
            cerca = antes[corte + 1:]
            # En el respaldo se juntan los renglones: un nombre partido entre
            # dos líneas («Derecho de\nRéplica») también se encuentra.
            clave = _primera(cerca) or _ultima(' '.join(antes.split()))
            if not clave:
                continue
            d, mm, mes, a = m.groups()
            mm = mm or MESES.index(mes) + 1
            out.append((nombre, t.count('\n', 0, m.start()) + 1, clave, ddmmaaaa(d, mm, a)))
    return out


def _primera(t):
    pos = [(m.start(), c) for c, _n, _r, al in LEYES for a in al for m in [re.search(a, t)] if m]
    return min(pos)[1] if pos else None


def _ultima(t):
    pos = [(m.start(), c) for c, _n, _r, al in LEYES for a in al for m in re.finditer(a, t)]
    return max(pos)[1] if pos else None


def citas_marco():
    """Las fechas de la tabla del Marco Legal (leyes_niveles.FEDERALES), que no
    se escriben como «última reforma DOF…» sino en columnas: se cruzan por el
    nombre del PDF, que es el mismo en el índice de Diputados."""
    import leyes_niveles
    return [(f['pdf'], f['sig'], f['ult'] or f['pub']) for f in leyes_niveles.federales()]


def avisos(indice, lista=None, marco=None):
    """Compara cada cita con el índice. Dos clases de aviso:
    - «vieja»: citamos una reforma anterior a la que ya registra Diputados.
      Ese módulo puede estar diciendo algo que la ley ya no dice.
    - «adelantada»: citamos una fecha que Diputados no registra (más nueva).
      Puede ser una errata nuestra o que Diputados aún no actualiza; se coteja."""
    claves = {c: (nom, ref) for c, nom, ref, _al in LEYES}
    out = []
    for archivo, renglon, c, fecha in (citas() if lista is None else lista):
        nom, ref = claves[c]
        k, e = vigente(indice, ref)
        if not e or c in ('lif', 'pef'):     # la LIF y el PEF cambian cada año: no se citan como «última reforma»
            continue
        v = ultima(e)
        if orden(fecha) < orden(v):
            tipo = 'vieja'
        elif orden(fecha) > orden(v):
            tipo = 'adelantada'
        else:
            continue
        out.append({'archivo': 'herramientas/' + archivo, 'renglon': renglon, 'ley': c, 'nombre': nom,
                    'cita': fecha, 'vigente': v, 'tipo': tipo, 'liga': LB + 'ref/%s.htm' % k})
    por_pdf = {e['pdf']: (k, e) for k, e in indice.items() if e.get('pdf')}
    for pdf, sig, fecha in (citas_marco() if marco is None else marco):
        k, e = por_pdf.get(pdf, (None, None))
        if not e or orden(fecha) == orden(ultima(e)):
            continue
        out.append({'archivo': 'herramientas/leyes_niveles.py', 'renglon': None, 'ley': sig.lower(), 'nombre': e['nombre'],
                    'cita': fecha, 'vigente': ultima(e), 'tipo': 'vieja' if orden(fecha) < orden(ultima(e)) else 'adelantada',
                    'liga': LB + 'ref/%s.htm' % k})
    return out


# --- La bandeja --------------------------------------------------------------

EJEMPLO_DOF = '''<?xml version="1.0" encoding="ISO-8859-1"?><rss version="2.0"><channel>
<item><title>PODER EJECUTIVO SECRETARIA DE HACIENDA Y CREDITO PUBLICO</title>
<link><![CDATA[https://dof.gob.mx/nota_detalle.php?codigo=9999001&fecha=05/11/2026]]></link>
<description><![CDATA[DECRETO por el que se reforman los art&iacute;culos 17-H, 69-B y 82 del C&oacute;digo Fiscal de la Federaci&oacute;n.]]></description>
<valueDate>05/11/2026</valueDate></item>
<item><title>PODER EJECUTIVO SECRETARIA DE MARINA</title>
<link><![CDATA[https://dof.gob.mx/nota_detalle.php?codigo=9999002&fecha=05/11/2026]]></link>
<description><![CDATA[Acuerdo de delimitaci&oacute;n del recinto portuario de Puerto San Blas.]]></description>
<valueDate>05/11/2026</valueDate></item>
</channel></rss>'''.encode('latin-1')

EJEMPLO_INDICE = '''<table><tr><td>006</td><td><a href="ref/cff.htm"><font>C&Oacute;DIGO Fiscal de la Federaci&oacute;n</font></a>
<p><font>DOF 31/12/1981</font></p></td><td><font>DOF
 09/04/2026</font></td><td><a href="pdf/CFF.pdf">pdf</a></td></tr>
<tr><td>016</td><td><a href="ref/laassp.htm">LEY de Adquisiciones</a><p>DOF 16/04/2025</p></td><td>&nbsp;</td><td><a href="pdf/LAASSP.pdf">pdf</a></td></tr>
<tr><td>100</td><td><a href="ref/lss.htm">LEY del Seguro Social</a><p>DOF 21/12/1995</p></td><td>DOF 15/01/2026</td><td><a href="pdf/LSS.pdf">pdf</a></td></tr></table>'''


def prueba():
    """Sin red: revisa que cada pieza lea lo que debe. La corre revision.py."""
    fallas = []
    dof = leer_dof(EJEMPLO_DOF)
    if len(dof) != 1 or dof[0]['leyes'] != ['cff'] or dof[0]['articulos'] != '17-H, 69-B y 82' or dof[0]['fecha'] != '05-11-2026':
        fallas.append('DOF: %r' % dof)
    ind = leer_indice(EJEMPLO_INDICE)
    if ind.get('cff', {}).get('reforma') != '09-04-2026' or ind.get('laassp', {}).get('reforma') is not None or ultima(ind['laassp']) != '16-04-2025':
        fallas.append('índice: %r' % ind)
    citas_ej = [('x.py', 1, 'lss', '15-01-2026'), ('y.py', 2, 'cff', '01-01-2025'), ('z.py', 3, 'cff', '10-04-2026')]
    av = avisos(ind, citas_ej, [])
    if [(a['archivo'], a['tipo']) for a in av] != [('herramientas/y.py', 'vieja'), ('herramientas/z.py', 'adelantada')]:
        fallas.append('avisos: %r' % av)
    # El sujeto de la cita: la Ley de Amparo, no la Constitución que nombra después.
    t = plano("'Ley de Amparo, Reglamentaria de los artículos 103 y 107 de la Constitución (última reforma DOF 16-10-2025)'")
    m = CITA.search(t)
    a = t[:m.start()]
    if _primera(a[max(a.rfind("'"), a.rfind('\n')) + 1:]) != 'lamp':
        fallas.append('sujeto de la cita')
    if not CITA.search(plano('última reforma, 28 de noviembre de 2025')):
        fallas.append('cita con mes en letra')
    cambio = cambios_indice(ind, {'cff': {'reforma': '01-01-2026'}})
    if len(cambio) != 1 or cambio[0]['fecha'] != '09-04-2026':
        fallas.append('cambios del índice: %r' % cambio)
    # Y que las citas reales se puedan leer (sin red: no compara, solo lee).
    if len(citas()) < 20:
        fallas.append('se esperaban más de 20 citas en herramientas/')
    for f in fallas:
        print('vigía legislativo: FALLA', f)
    print('vigía legislativo: prueba %s' % ('bien' if not fallas else 'con fallas'))
    return 1 if fallas else 0


def main():
    if '--prueba' in sys.argv:
        return prueba()
    hoy = datetime.date.today().strftime('%d-%m-%Y')
    try:
        previa = json.load(open(SALIDA, encoding='utf-8'))
    except (OSError, ValueError):
        previa = {}
    fallas, nuevos = [], []
    indice = None
    if '--citas' not in sys.argv:
        try:
            nuevos += leer_dof(bajar(DOF_RSS))
        except Exception as e:  # el DOF no respondió: se intenta mañana
            fallas.append('DOF: %s' % e)
        try:
            # El índice viene en ISO-8859-1 (latin-1), no en UTF-8.
            indice = leer_indice(bajar(INDICE).decode('latin-1'))
            if len(indice) < 200:
                raise ValueError('el índice trajo solo %d leyes; ¿cambió la página?' % len(indice))
        except Exception as e:
            fallas.append('Diputados: %s' % e)
            indice = None
    leyes = {}
    if indice:
        for c, nom, ref, _al in LEYES:
            k, e = vigente(indice, ref)
            if e:
                leyes[c] = {'nombre': e['nombre'], 'publicada': e['publicada'], 'reforma': ultima(e), 'liga': LB + 'ref/%s.htm' % k,
                            'pdf': LB + 'pdf/' + e['pdf'] if e['pdf'] else None}
        nuevos += cambios_indice(indice, previa.get('leyes'))
    elif previa.get('leyes'):
        leyes = previa['leyes']   # sin red: el cruce se hace con el último índice guardado
        indice = {v['liga'].rsplit('/', 1)[1][:-4]: {'nombre': v['nombre'], 'publicada': v['publicada'], 'reforma': v['reforma'],
                                                    'pdf': (v.get('pdf') or '').rsplit('/', 1)[-1] or None} for v in leyes.values()}
    viejos = previa.get('hallazgos') or []
    vistos = {h['id'] for h in viejos}
    frescos = []
    for h in nuevos:
        if h['id'] in vistos:
            continue
        vistos.add(h['id'])
        h['estado'] = 'por cotejar'
        h['visto'] = hoy
        frescos.append(h)
    datos = {
        'actualizado': hoy,
        'nota': ('Lo que junta herramientas/vigia_legislativo.py del sumario del DOF y del índice de Leyes Federales Vigentes de la Cámara de '
                 'Diputados, sin verificar: solo título, fecha y liga, nunca el texto de la reforma. Cada hallazgo queda «por cotejar» hasta que una '
                 'persona lo revisa; los avisos dicen qué módulo de Auditavisión cita una reforma anterior a la vigente.'),
        'fuentes': {'dof': DOF_RSS, 'diputados': INDICE},
        'hallazgos': (frescos + viejos)[:MAXIMO],
        'leyes': leyes,
        'avisos': avisos(indice) if indice else previa.get('avisos', []),
        'fallas': fallas,
    }
    # Si nada cambió, se conserva la fecha anterior: así el flujo de GitHub no
    # hace un commit diario solo por la fecha.
    if previa.get('actualizado') and {k: v for k, v in datos.items() if k != 'actualizado'} == {k: v for k, v in previa.items() if k != 'actualizado'}:
        datos['actualizado'] = previa['actualizado']
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('vigía legislativo: %d hallazgos nuevos, %d en la bandeja, %d avisos de citas viejas%s' % (
        len(frescos), len(datos['hallazgos']), sum(1 for a in datos['avisos'] if a['tipo'] == 'vieja'),
        ('; fallas: ' + '; '.join(fallas)) if fallas else ''))
    return 0


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main())
