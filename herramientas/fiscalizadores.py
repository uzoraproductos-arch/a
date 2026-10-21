# -*- coding: utf-8 -*-
"""Quien fiscaliza el dinero publico y que documentos publica cada quien,
para «Expedientes de casos de la ASF» (pedido del autor, 21-10-2026: «no solo
la Superior: todas las autoridades que intervienen en la fiscalizacion de las
finanzas publicas», divididas por tipo de expediente oficial).

Aqui no hay ni una cifra: solo quien es cada autoridad, el articulo que le da
la facultad (verificado contra el texto vigente de cada ley en
diputados.gob.mx el 21-10-2026), que expediente oficial publica, donde, y que
tanto de eso ya integro Auditavision. Lo que no esta integrado se dice asi,
como falta de la plataforma.

ENTREGAS es lo que el agente (agente_fiscalizacion.py) vigila en el tiempo:
cada Cuenta Publica de 2024 a 2027, con la fecha que fija la ley para cada
documento. El agente escribe lo que encontro en
investigaciones/agente-fiscalizacion.json y esta pagina lo pinta.
"""
import datetime
import html
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTE = os.path.join(RAIZ, 'investigaciones', 'agente-fiscalizacion.json')

# (clave, icono, nombre del grupo, para que sirve)
GRUPOS = [
    ('externa', '🏛️', 'Fiscalización superior', 'Revisan el gasto después de ejercido y desde fuera del gobierno que lo gastó.'),
    ('interna', '🔍', 'Control interno', 'Vigilan desde dentro de la Administración Pública: reglas, auditorías internas e investigaciones.'),
    ('sancion', '⚖️', 'Sanción', 'Convierten un hallazgo en castigo: faltas graves, indemnizaciones y delitos.'),
    ('fiscal', '🧾', 'Fiscal', 'Siguen el dinero de los particulares que facturan al gobierno.'),
    ('coordinacion', '🔗', 'Coordinación y acceso', 'Ponen a todas las anteriores en la misma mesa y te dan acceso a sus documentos.'),
]

# Cada autoridad: clave, grupo, icono, nombre, fundamento, que hace, que
# expediente publica, portal oficial, referencia de la Biblioteca (o None),
# integracion ('si', 'parcial', 'no') y que tiene la plataforma (con enlaces
# internos).
AUTORIDADES = [
    ('asf', 'externa', '🏛️', 'Auditoría Superior de la Federación (ASF)', 'CPEUM, art. 79; LFRCF, art. 35',
     'Revisa la Cuenta Pública: el gasto de los tres Poderes, los órganos autónomos, las empresas del Estado y el dinero federal que reciben estados y municipios.',
     'Informes individuales de auditoría, en tres entregas al año (junio, octubre y 20 de febrero), su Matriz de Datos Básicos y el Informe General.',
     'https://www.asf.gob.mx/Section/58_Informes_de_auditoria', 'ref-asf-mdb2024', 'si',
     'Integrados la Cuenta Pública 2024 completa y la primera entrega de 2025: <a href="herramienta-inspector-asf-cifras.html">sus cifras</a>, <a href="herramienta-inspector-asf-estado.html">tu estado</a> y <a href="expedientes.html">los casos</a>.'),
    ('uec', 'externa', '🔎', 'Unidad de Evaluación y Control (UEC) de la Cámara de Diputados', 'LFRCF, arts. 102 a 104',
     'Vigila a la propia ASF, por encargo de la Comisión de Vigilancia: que sus auditores cumplan la ley.',
     'Evaluaciones del desempeño de la ASF y análisis de sus informes.',
     'https://www.diputados.gob.mx/UEC/', None, 'no',
     'Integrar sus evaluaciones es una falta de la plataforma, no de la UEC.'),
    ('efs', 'externa', '🗺️', 'Entidades estatales de fiscalización', 'CPEUM, art. 116, fr. II',
     'Las auditorías superiores de cada estado: revisan los fondos, los recursos locales y la deuda de estados y municipios, el dinero que la ASF no ve.',
     'Informes de auditoría de cada cuenta pública estatal; la Constitución les da carácter público.',
     None, None, 'no',
     'Cada una publica en su propio portal; integrarlos es una falta de la plataforma. Lo federal de cada estado está en su <a href="herramienta-inspector-entes.html?nivel=estatal">ficha técnica</a>.'),
    ('sabg', 'interna', '🛡️', 'Secretaría Anticorrupción y Buen Gobierno', 'LOAPF, art. 37, frs. I y IV',
     'Fija las reglas de control interno y de contrataciones de la Administración Pública Federal y hace sus propias investigaciones, revisiones y auditorías.',
     'Auditorías e investigaciones internas, los procedimientos de contratación en ComprasMX y la plataforma de alertadores de la corrupción.',
     'https://www.gob.mx/buengobierno', 'ref-comprasmx', 'parcial',
     'Enlazamos <a href="https://comprasmx.buengobierno.gob.mx/" target="_blank" rel="noopener">ComprasMX ↗</a> y su <a href="https://alertadores.buengobierno.gob.mx/" target="_blank" rel="noopener">plataforma de alertadores ↗</a>; sus auditorías y sanciones aún no están integradas.'),
    ('oic', 'interna', '🏢', 'Órganos internos de control', 'LGRA, art. 3, fr. XXI',
     'Las unidades de cada ente público que promueven y evalúan su control interno y aplican las leyes de responsabilidades a sus servidores públicos.',
     'Investigaciones y procedimientos de responsabilidad administrativa dentro de cada dependencia.',
     None, 'ref-lgra', 'no',
     'No publican en un portal común; integrarlos es una falta de la plataforma.'),
    ('tfja', 'sancion', '⚖️', 'Tribunal Federal de Justicia Administrativa (TFJA)', 'LOTFJA, art. 4',
     'Resuelve las faltas administrativas graves que le turnan la ASF, la Secretaría Anticorrupción y los órganos internos de control, y fija las indemnizaciones por el daño a la Hacienda Pública.',
     'Sentencias en materia de responsabilidades administrativas graves.',
     'https://www.tfja.gob.mx/', None, 'no',
     'Integrar sus sentencias es una falta de la plataforma, no del Tribunal.'),
    ('fgr', 'sancion', '🚨', 'Fiscalía Especializada en Materia de Combate a la Corrupción (FGR)', 'CPEUM, art. 102, apdo. A',
     'Investiga los delitos de corrupción; recibe las denuncias de hechos de la ASF y las de cualquier persona.',
     'Carpetas de investigación (son reservadas) y los comunicados de sus casos.',
     'https://fgr.org.mx/es/FGR/FEMCC', 'ref-fgr-femcc', 'no',
     'Las carpetas son reservadas por ley; integrar sus comunicados es una falta de la plataforma.'),
    ('sat', 'fiscal', '🧾', 'Servicio de Administración Tributaria (SAT)', 'CFF, art. 69-B',
     'Presume y declara qué empresas facturan operaciones inexistentes, y publica sus nombres.',
     'Los listados del artículo 69-B: presuntos, definitivos, desvirtuados y con sentencia favorable.',
     'https://www.gob.mx/sat/acciones-y-programas/notificacion-a-contribuyentes-con-operaciones-presuntamente-inexistentes-y-listados-definitivos-333336',
     'ref-sat-69b', 'si',
     'Integrado: búscalas por RFC o por nombre en la <a href="herramienta-inspector-efos.html">Lista negra del SAT</a>.'),
    ('sna', 'coordinacion', '🔗', 'Sistema Nacional Anticorrupción (SNA)', 'CPEUM, art. 113',
     'Coordina a la ASF, la Fiscalía Anticorrupción, la secretaría de control interno, el TFJA, el Tribunal de Disciplina Judicial y el Comité de Participación Ciudadana.',
     'Su Plataforma Digital Nacional, que reúne, entre otras cosas, a los servidores públicos y particulares sancionados.',
     'https://www.plataformadigitalnacional.org/', None, 'no',
     'Integrar su Plataforma Digital Nacional es una falta de la plataforma.'),
    ('pnt', 'coordinacion', '📨', 'Plataforma Nacional de Transparencia', 'Ley General de Transparencia',
     'El portal para pedir a cualquier autoridad el contrato, la factura o el acta que no publicó.',
     'Las respuestas a solicitudes de información y las obligaciones de transparencia de cada sujeto obligado.',
     'https://www.plataformadetransparencia.org.mx/', 'ref-pnt', 'parcial',
     'Te explicamos cómo usarla en <a href="garantias.html">Garantías cívicas</a>.'),
]

# Lo que el agente vigila: (clave, Cuenta Publica, autoridad, documento,
# fecha que fija la ley, fundamento, direccion donde aparece). La fecha de
# octubre es el ultimo dia habil del mes (LFRCF, art. 35).
ENTREGAS = [
    ('cp2024-asf3', 2024, 'asf', 'Tercera entrega e Informe General', '2026-02-20', 'LFRCF, art. 35',
     'https://www.asf.gob.mx/Trans/Informes/IR2024c/index.html'),
    ('cp2025-shcp', 2025, 'shcp', 'Hacienda entrega la Cuenta Pública 2025', '2026-04-30', 'CPEUM, art. 74, fr. VI', None),
    ('cp2025-asf1', 2025, 'asf', 'Primera entrega de la ASF', '2026-06-30', 'LFRCF, art. 35',
     'https://www.asf.gob.mx/Trans/Informes/IR2025a/index.html'),
    ('cp2025-asf2', 2025, 'asf', 'Segunda entrega de la ASF', '2026-10-30', 'LFRCF, art. 35',
     'https://www.asf.gob.mx/Trans/Informes/IR2025b/index.html'),
    ('cp2025-asf3', 2025, 'asf', 'Tercera entrega e Informe General', '2027-02-20', 'LFRCF, arts. 33 y 35',
     'https://www.asf.gob.mx/Trans/Informes/IR2025c/index.html'),
    ('cp2026-shcp', 2026, 'shcp', 'Hacienda entrega la Cuenta Pública 2026', '2027-04-30', 'CPEUM, art. 74, fr. VI', None),
    ('cp2026-asf1', 2026, 'asf', 'Primera entrega de la ASF', '2027-06-30', 'LFRCF, art. 35',
     'https://www.asf.gob.mx/Trans/Informes/IR2026a/index.html'),
    ('cp2026-asf2', 2026, 'asf', 'Segunda entrega de la ASF', '2027-10-29', 'LFRCF, art. 35',
     'https://www.asf.gob.mx/Trans/Informes/IR2026b/index.html'),
    ('cp2026-asf3', 2026, 'asf', 'Tercera entrega e Informe General', '2028-02-20', 'LFRCF, arts. 33 y 35',
     'https://www.asf.gob.mx/Trans/Informes/IR2026c/index.html'),
    ('cp2027-cierre', 2027, 'shcp', 'Cierra el ejercicio 2027', '2027-12-31', None, None),
    ('cp2027-shcp', 2027, 'shcp', 'Hacienda entrega la Cuenta Pública 2027', '2028-04-30', 'CPEUM, art. 74, fr. VI', None),
    ('cp2027-asf1', 2027, 'asf', 'Primera entrega de la ASF', '2028-06-30', 'LFRCF, art. 35',
     'https://www.asf.gob.mx/Trans/Informes/IR2027a/index.html'),
    ('cp2027-asf2', 2027, 'asf', 'Segunda entrega de la ASF', '2028-10-31', 'LFRCF, art. 35',
     'https://www.asf.gob.mx/Trans/Informes/IR2027b/index.html'),
    ('cp2027-asf3', 2027, 'asf', 'Tercera entrega e Informe General', '2029-02-20', 'LFRCF, arts. 33 y 35',
     'https://www.asf.gob.mx/Trans/Informes/IR2027c/index.html'),
]

# Que entregas ya tienen sus cifras en la base de la plataforma.
INTEGRADAS = {'cp2024-asf3', 'cp2025-asf1'}

MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
         'septiembre', 'octubre', 'noviembre', 'diciembre']


def esc(t):
    return html.escape(str(t), quote=True)


def fecha(iso):
    a, m, d = (int(x) for x in iso[:10].split('-'))
    return '%d de %s de %d' % (d, MESES[m - 1], a)


def reporte():
    """Lo ultimo que encontro el agente, o None si nunca ha corrido."""
    if not os.path.exists(REPORTE):
        return None
    return json.load(open(REPORTE, encoding='utf-8'))


# (clase, icono, etiqueta) por estado de una entrega.
ESTADOS = {
    'integrada': ('ok', '✅', 'Publicada e integrada'),
    'publicada': ('nueva', '🆕', 'Publicada; falta integrarla a la plataforma'),
    'esperada': ('espera', '⏳', 'Por venir'),
    'retraso': ('tarde', '⚠️', 'Ya debió publicarse y aún no aparece'),
    'sin_respuesta': ('nada', '🔌', 'El portal no respondió'),
    'cumplida': ('ok', '✅', 'Ya pasó'),
}


def estado_entrega(e, hallado, hoy):
    """Estado de una entrega: lo que el agente vio en su direccion, cruzado
    con la fecha legal y con lo que la plataforma ya integro."""
    clave, _, _, _, f, _, url = e
    if clave in INTEGRADAS:
        return 'integrada'
    if url is None:
        return 'cumplida' if f <= hoy else 'esperada'
    h = (hallado or {}).get(clave)
    if h and h.get('http') == 200:
        return 'publicada'
    if f > hoy:
        return 'esperada'
    if h and h.get('http') == 404:
        return 'retraso'
    return 'sin_respuesta'


def seguimiento_html(chip):
    """La linea de 2024 a 2027, con lo que vio el agente en su ultima vuelta."""
    rep = reporte()
    hallado = (rep or {}).get('entregas', {})
    hoy = (rep or {}).get('fecha') or datetime.date.today().isoformat()
    anios = []
    for cp in (2024, 2025, 2026, 2027):
        filas = []
        for e in (x for x in ENTREGAS if x[1] == cp):
            st = estado_entrega(e, hallado, hoy)
            cl, ico, et = ESTADOS[st]
            h = hallado.get(e[0]) or {}
            extra = ''
            if h.get('informes'):
                extra = ' <small>Su índice enlaza %s informes individuales de esa entrega %s</small>' % (format(h['informes'], ','), chip('derivado'))
            # La liga solo cuando el documento ya existe: antes, da 404.
            liga = (' <a href="%s" target="_blank" rel="noopener">ver la entrega ↗</a>' % esc(e[6])) if e[6] and h.get('http') == 200 else ''
            filas.append('<li class="fz-ent fz-%s"><span class="fz-ent-f">%s</span><span class="fz-ent-tx"><b>%s</b>'
                         '<span class="fz-ent-st"><span aria-hidden="true">%s</span> %s</span>%s<small>%s%s</small></span></li>'
                         % (cl, fecha(e[4]), esc(e[3]), ico, et, extra, esc(e[5] or 'Fin del año fiscal'), liga))
        anios.append('<section class="fz-anio" aria-label="Cuenta Pública %d"><h3 class="fz-anio-t">Cuenta Pública %d</h3><ol class="fz-linea">%s</ol></section>'
                     % (cp, cp, ''.join(filas)))
    if rep:
        vuelta = ('<p class="fz-vuelta">📡 <b>Última vuelta del agente:</b> %s. Revisó %d direcciones oficiales. '
                  'Lo que encuentra publicado y aún no integrado queda marcado 🆕 hasta que sus cifras pasan a la base, con su documento y su huella.</p>'
                  % (fecha(rep['fecha']), len(rep.get('entregas', {})) + len(rep.get('portales', {}))))
    else:
        vuelta = '<p class="fz-vuelta">📡 El agente aún no ha dado su primera vuelta.</p>'
    return vuelta + '<div class="fz-anios">%s</div>' % ''.join(anios)


def autoridades_html(ref):
    rep = reporte() or {}
    port = rep.get('portales', {})
    INT = {'si': ('ok', 'Ya está en Auditavisión.'), 'parcial': ('parcial', 'Está en parte en Auditavisión.'), 'no': ('no', 'Todavía no está en Auditavisión.')}
    out = []
    for g, gi, gn, gd in GRUPOS:
        tarj = []
        for a in (x for x in AUTORIDADES if x[1] == g):
            clave, _, ico, nom, fund, que, exp, url, rid, integ, plat = a
            p = port.get(clave)
            vivo = ''
            if url and p:
                vivo = ('<small class="fz-vivo">📡 %s el %s</small>'
                        % ('Su portal respondió' if p.get('http') == 200 else 'Su portal no respondió', fecha(rep['fecha'])))
            portal = ('<a class="fz-portal" href="%s" target="_blank" rel="noopener">Ir a su portal oficial ↗</a>' % esc(url)) if url else \
                     '<span class="fz-portal fz-portal-no">Sin portal nacional común</span>'
            c, et = INT[integ]
            tarj.append('''<article class="fz-aut" id="fz-%s">
            <h3 class="fz-aut-t"><span aria-hidden="true">%s</span> %s</h3>
            <p class="fz-fund">%s%s</p>
            <p><b>Qué hace.</b> %s</p>
            <p><b>Su expediente oficial.</b> %s</p>
            <p class="fz-int fz-int-%s"><b>%s</b> %s</p>
            <p class="fz-pie">%s %s</p>
          </article>''' % (clave, ico, esc(nom), esc(fund), ref(rid) if rid else '', esc(que), esc(exp), c, et, plat, portal, vivo))
        out.append('''<section class="fz-grupo" aria-labelledby="fzG-%s">
          <h2 class="fz-grupo-t" id="fzG-%s"><span aria-hidden="true">%s</span> %s</h2>
          <p class="fz-grupo-d">%s</p>
          <div class="fz-auts">%s</div>
        </section>''' % (g, g, gi, esc(gn), esc(gd), ''.join(tarj)))
    return ''.join(out)
