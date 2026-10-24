"""Los estados de cuenta y los recursos interactivos que el Auditor Virtual
ofrece al contestar (pedido del autor, 24-10-2026).

Dos catalogos, escritos a mano y comprobados al generar:

- ESTADOS_CUENTA: cada estado de cuenta que la plataforma expide (el civico,
  el ambiental, el de cada presidente, el de la diputacion federal y local,
  el de la senaduria, el de la Corte, el de cada estado y el de cada
  municipio). El bot los reconoce cuando le piden «estado de cuenta de…» y
  lleva directo al documento.
- RECURSOS: los mapas, relojes, contadores, tableros y simuladores de la
  Enciclopedia y de las herramientas. El bot los ofrece al pie de una
  respuesta («Ver mapa», «Ver fiscalizacion», «Ver reloj»…) cuando la
  pregunta toca su tema, y los abre directo si se los piden («el mapa de la
  deuda»).

Un mapa, reloj o simulador nuevo no esta terminado hasta que tiene su renglon
aqui (AGENTS.md §5 ter). Ninguno lleva cifras: solo dicen que hay y donde.
Si un archivo o un ancla deja de existir, la generacion se detiene."""
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPIDE = 'radar-estado-de-cuenta.html'

# (id, pregunta de ejemplo, icono, titulo, enlace, que trae, palabras con que
# se pide). Ante un empate gana el primero: por eso el congreso local va antes
# que la diputacion federal («diputado local» lleva las dos palabras).
# El enlace con %s recibe la clave del estado (JAL, NL…); el del congreso
# local, el documento de ese congreso (dip-loc-jal), que sale de 'dl'.
ESTADOS_CUENTA = [
    ('civico', 'Dame mi estado de cuenta cívico', '🧾', 'Tu estado de cuenta cívico', 'herramienta-calculadora-ticket.html',
     'Escribe lo que ganas y ve lo que te retienen y a dónde va cada peso de tu impuesto, en un documento con folio y huella.',
     'civico mi tu personal propio impuesto impuestos isr sueldo ingreso retienen calculadora'),
    ('ambiental', 'Mi estado de cuenta ambiental', '🌎', 'Tu estado de cuenta ambiental', 'herramienta-ambiente-ticket.html',
     'Lo que ya te cargaron a tu nombre: tu parte de la deuda, de sus intereses y del daño ambiental, con tu basura del año.',
     'ambiental ambiente ecologico naturaleza contaminacion dano basura'),
    ('presidentes', 'Estado de cuenta de los presidentes', '🏛️', 'El estado de cuenta de cada presidente', EXPIDE,
     'De Salinas a Sheinbaum: lo que entró, lo que se gastó, la deuda que recibió y la que entregó y lo que la ASF dejó por aclarar, con su semáforo.',
     'presidente presidentes presidenta sexenio sexenios administracion administraciones gobierno federal ejecutivo'),
    ('dip-loc', 'Estado de cuenta de un diputado local', '🏛️', 'El estado de cuenta de un congreso local', EXPIDE + '?doc=dip-loc-%s',
     'El cargo de diputada o diputado local en cualquiera de los 32 congresos, con lo que su congreso tiene documentado.',
     'local locales congreso congresos estatal legislatura'),
    ('dip-fed', 'Estado de cuenta de un diputado', '🏛️', 'El estado de cuenta de la diputación federal', EXPIDE + '?doc=dip-fed',
     'El cargo de diputada o diputado federal: su dieta, su remuneración anual, sus asesores y lo que cuesta la Cámara.',
     'diputado diputados diputada diputadas diputacion camara federal federales curul'),
    ('senado', 'Estado de cuenta de un senador', '🏛️', 'El estado de cuenta de la senaduría', EXPIDE + '?doc=senado',
     'El cargo de senadora o senador: su dieta, su remuneración anual bruta y neta, sus asesores y la auditoría de la ASF al Senado.',
     'senador senadores senadora senadoras senado senaduria escano'),
    ('scjn', 'Estado de cuenta de la Suprema Corte', '⚖️', 'El estado de cuenta de la Suprema Corte', EXPIDE + '?doc=scjn',
     'El cargo de ministra o ministro: su remuneración, su ponencia y sus asesores.',
     'corte suprema ministro ministros ministra ministras scjn judicial'),
    ('estado', 'Estado de cuenta de mi estado', '🗺️', 'El estado de cuenta de tu estado', 'herramienta-inspector-entes.html#ente=estatal:%s',
     'La ficha técnica de cada uno de los 32 gobiernos estatales: si gastó lo que aprobó, si rindió cuentas y qué dejó por aclarar.',
     'estado estados entidad entidades estatal gobierno'),
    ('municipio', 'Estado de cuenta de mi municipio', '🏙️', 'El estado de cuenta de tu municipio', 'herramienta-inspector-entes.html?nivel=municipal',
     'La ficha técnica de cada uno de los 2,479 municipios: sus cuentas ante el INEGI, sus fondos federales y lo que observó la ASF.',
     'municipio municipios municipal alcaldia ayuntamiento'),
]

# (id, icono, verbo del boton, nombre, enlace, enlace con estado o None,
#  tipo, palabras de su tema). El tipo es lo que el lector pide («mapa»,
#  «reloj», «contador»…); las palabras deciden cuando se ofrece.
RECURSOS = [
    ('mapa-gasto', '🗺️', 'Ver mapa', 'El mapa del gasto federalizado', 'numeros-mapa-del-gasto-federalizado.html',
     'numeros-mapa-del-gasto-federalizado.html?e=%s', 'mapa',
     'estado estados entidad entidades participaciones aportaciones ramo 28 33 federalizado habitante dependencia estatal recibe llega'),
    ('circuito', '🔄', 'Ver su circuito', 'El circuito del dinero de cada estado', 'numeros-las-32-entidades.html#circuito',
     'numeros-las-32-entidades.html?e=%s#circuito', 'mapa',
     'estado estados entidad estatal recauda recaudacion propia convenios ramo 25 circuito'),
    ('padron', '🏘️', 'Ver sus municipios', 'Los municipios, uno por uno', 'numeros-los-municipios.html#padron',
     'numeros-los-municipios.html?e=%s#padron', 'mapa',
     'municipio municipios municipal alcaldia ayuntamiento predial fortamun fismdf padron'),
    ('asf-estado', '🔎', 'Ver fiscalización', 'Tu estado ante la Auditoría Superior', 'herramienta-inspector-asf-estado.html', None, 'fiscalizacion',
     'asf auditoria auditorias auditado fiscalizacion fiscaliza aclarar observaciones pliego estado estados entidad'),
    ('asf-casos', '📂', 'Ver fiscalización', 'Expedientes de casos de la ASF', 'herramienta-inspector-asf.html', None, 'fiscalizacion',
     'asf auditoria auditorias fiscalizacion aclarar observaciones pliego cuenta publica expediente caso casos recuperado'),
    ('entes', '🏢', 'Ver ficha técnica', 'Auditor de entes públicos', 'herramienta-inspector-entes.html',
     'herramienta-inspector-entes.html#ente=estatal:%s', 'fiscalizacion',
     'ente entes dependencia dependencias secretaria organismo diagnostico aprobado ejercido subejercicio rindio'),
    ('reloj-deuda', '⏱️', 'Ver reloj', 'El reloj de la deuda', 'herramienta-calculadora-reloj.html', None, 'reloj',
     'deuda intereses costo financiero debe debemos reloj contador segundo'),
    ('reloj-adm', '⏱️', 'Ver contador', 'El reloj de cada administración', 'radar-reloj.html', None, 'reloj',
     'presidente presidenta sexenio administracion amlo pena calderon fox zedillo salinas sheinbaum lopez obrador ritmo contador reloj'),
    ('reloj-amb', '⏱️', 'Ver reloj', 'El reloj del daño ambiental', 'herramienta-ambiente-reloj.html', None, 'reloj',
     'ambiental ambiente dano contaminacion agotamiento naturaleza degradacion reloj contador'),
    ('pib-amb', '📉', 'Ver contador', 'El PIB que no alcanza', 'datos-ambiente-pib.html', None, 'reloj',
     'pib crecimiento ecologico ambiental verde real'),
    ('tablero', '📊', 'Ver tablero', 'El tablero de cada administración', 'radar-tablero.html', None, 'tablero',
     'presidente presidenta sexenio administracion ingresos inversion costo gobierno deuda recibio entrego'),
    ('duelo', '⚔️', 'Comparar', 'Duelo de administraciones', 'radar-duelo.html', None, 'tablero',
     'compara comparar comparacion contra versus duelo presidente sexenio administracion'),
    ('maquina', '💱', 'Usar la máquina del tiempo', 'La máquina del tiempo del peso', 'radar-peso-maquina.html', None, 'simulador',
     'peso pesos dolar dolares euro inflacion valen vale valia hoy antes poder adquisitivo'),
    ('simulador', '🧮', 'Ver simulador', 'Reparte el presupuesto', 'simulador-presupuesto.html', None, 'simulador',
     'presupuesto egresos reparte repartir gasto simulador escenario'),
    ('expide', '🧾', 'Ver estado de cuenta', 'Estado de cuenta administrativo', EXPIDE, None, 'tablero',
     'diputado diputados diputada senador senadores senadora ministro ministros corte cargo dieta legislador legisladores presidente presidenta sexenio administracion'),
    ('obras', '🏗️', 'Ver obras', 'La cuenta de cada megaobra', 'herramienta-megaobras-pulso-cuenta.html', None, 'tablero',
     'obra obras megaobra megaobras tren maya dos bocas refineria aifa aeropuerto interoceanico inversion'),
]


def _existe(enlace):
    """El archivo existe y, si lleva ancla, la pagina tiene ese id."""
    archivo, _, ancla = enlace.partition('#')
    archivo = archivo.split('?')[0]
    ruta = os.path.join(RAIZ, archivo)
    if not os.path.exists(ruta):
        return False
    if ancla and '=' not in ancla:
        return ('id="%s"' % ancla) in open(ruta, encoding='utf-8').read()
    return True


def _docs_expide():
    s = open(os.path.join(RAIZ, EXPIDE), encoding='utf-8').read()
    C = json.loads(re.search(r'id="exCargos">(.*?)</script>', s, re.S).group(1))
    return C['docs']


def base(estados):
    """Lo que el bot recibe: {'ec': [...], 'rec': [...], 'dl': {...}}.
    estados son (clave, nombre) de las 32 entidades. El congreso local se
    busca por el nombre del estado: sus claves no son las mismas (MÉX es
    dip-loc-mex, TAM es dip-loc-tams)."""
    lista = _docs_expide()
    docs = {d['id'] for d in lista}
    por_nombre = {d.get('ent'): d['id'] for d in lista if d.get('tipo') == 'dip-loc'}
    dl = {a: por_nombre.get(n) for a, n in estados}
    malos = []
    ec = []
    for i, q, ico, tit, ir, txt, k in ESTADOS_CUENTA:
        if not _existe(ir.replace('%s', '')):
            malos.append(ir)
        for doc in re.findall(r'\?doc=([a-z-]+)(?![a-z%-])', ir):
            if doc not in docs:
                malos.append(ir)
        if 'dip-loc-%s' in ir:
            faltan = [a for a, v in dl.items() if not v]
            if faltan:
                malos.append('dip-loc de ' + ', '.join(faltan))
            ir = ir.replace('dip-loc-%s', '%s')
        ec.append({'id': i, 'q': q, 'ico': ico, 'tit': tit, 'ir': ir, 'txt': txt, 'k': k})
    rec = []
    for i, ico, verbo, nom, ir, ire, tipo, k in RECURSOS:
        for e in (ir, (ire % 'X') if ire else None):
            if e and not _existe(e):
                malos.append(e)
        rec.append({'id': i, 'q': q, 'ico': ico, 'v': verbo, 'n': nom, 'ir': ir, 'ire': ire, 'tipo': tipo, 'k': k})
    if malos:
        raise SystemExit('asistente_recursos: enlaces que no existen: ' + '; '.join(malos))
    return {'ec': ec, 'rec': rec, 'dl': dl}
