# -*- coding: utf-8 -*-
"""Octava aplicación del Modo Inspector: «Contratos, lista 69-B y ASF, año por
año» (pedido del autor, 04-11-2026: «una aplicación del Modo Inspector que
cruce contratos × lista 69-B × ASF por año: distingue lo que ya declaró la
autoridad (oficial) de las señales que detectamos nosotros (derivado, “señal
para revisar”), incluida la comparación entre la fecha del contrato y la fecha
del DOF»).

De dónde sale cada pieza (nada se escribe a mano aquí):
  - Contratos 2025 y 2026: ComprasMX (actualizar_comprasmx.py). Si el catálogo
    ya trae «cruce69b», se usa la fecha de firma; si no, la de publicación que
    guardan las fichas, y se dice.
  - Contratos de años anteriores: CompraNet (actualizar_compranet.py →
    assets/auditor/data/compranet/cruce.js). Mientras no esté, cada año queda
    pendiente con su ficha («cnet-historico»).
  - Lista 69-B: sat-69b.js (actualizar_69b.py): situación, oficio y fecha de
    publicación en el DOF, y la del presunto si el archivo ya la trae.
  - ASF: las Estadísticas de la Fiscalización Superior 2002–2024
    (extraer_estadisticas_asf.py) y los montos por aclarar de las Matrices de
    Datos Básicos 2019–2024 (extraer_serie_asf.py, extraer_mdb_asf.py). La CP
    2000 y 2001 quedan pendientes («asf-cp-2000-2001»).

Lo oficial y lo nuestro, separados (AGENTS.md §2):
  oficial   lo que declaró la autoridad: la situación del SAT con su oficio y
            su fecha en el DOF, el contrato con su importe y su fecha, las
            cifras de la ASF.
  derivado  lo que calculamos: los días entre el DOF y el contrato, las sumas,
            y la clasificación en «señal para revisar» o «antecedente».
Una señal nunca es una irregularidad ni una acusación: es una pregunta que
conviene hacer. Estar en la lista 69-B es una determinación administrativa,
no una condena (Constitución, art. 20, B, fr. I).

La regla de la señal (criterio de la plataforma):
  - Contrato firmado el día de la publicación en el DOF o después, con la
    empresa como definitiva → señal (la más fuerte).
  - Igual, con la empresa como presunta → señal (el SAT todavía no resuelve).
  - Definitiva, contrato antes del definitivo pero después de su presunción → señal.
  - Desvirtuada o con sentencia favorable: nunca es señal (salió de la lista);
    se cuenta como antecedente, y se dice si el contrato fue mientras era
    presunta, si el archivo trae esa fecha.
  - Contrato anterior a toda publicación → antecedente.
  - Sin fecha → pendiente.

Lo llama apartados.insp_nativa(): construir(base, ref) -> HTML del cuerpo.
El chat lee bot() (asistente.py, dat['cru']).
"""
import datetime
import html
import json
import os
import re

from presupuesto_modulos import chip

ESTILOS = ['insp-cruce.css']
SCRIPTS = []

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(RAIZ, 'assets', 'auditor', 'data')
PAGINA = 'herramienta-inspector-cruce.html'
ESTAD = os.path.join(RAIZ, 'investigaciones', 'asf-estadisticas-2002-2024.json')
MDB_SERIE = os.path.join(RAIZ, 'investigaciones', 'asf-mdb-serie.json')
MDB_2024 = os.path.join(RAIZ, 'investigaciones', 'asf-mdb-2024.json')
CMX_DETALLE = 'https://comprasmx.buengobierno.gob.mx/sitiopublico/#/sitiopublico/detalle/%s/procedimiento'
PRIMER_ANIO, ULTIMO_ANIO = 2000, 2026
CFF = 'https://www.diputados.gob.mx/LeyesBiblio/pdf/CFF.pdf'

# Fichas del Registro de pendientes (pendientes.PROPIOS).
P_CNET = 'cnet-historico'
P_ASF0 = 'asf-cp-2000-2001'
P_FIRMA = 'cruce-fecha-firma'
P_PRES = 'cruce-fecha-presunto'
P_EMPRESA = 'cruce-asf-empresa'

TIPOS_SENAL = {
    'def': ('⛔', 'Contrato con la empresa ya publicada como definitiva'),
    'pres_def': ('⚠️', 'Contrato mientras la empresa era presunta (luego quedó definitiva)'),
    'pre': ('⚠️', 'Contrato con la empresa ya publicada como presunta'),
}
TIPOS_ANT = {
    'antes': 'El contrato es anterior a su publicación en la lista',
    'salio': 'La empresa ya había salido de la lista cuando se hizo el contrato',
    'salio_durante': 'El contrato es de cuando era presunta; después salió de la lista',
    'salio_sin_pres': 'El contrato es de antes de que saliera de la lista; falta la fecha en que entró como presunta',
}
SIT = {'F': 'Definitivo', 'P': 'Presunto', 'D': 'Desvirtuado', 'S': 'Sentencia favorable'}


def esc(t):
    return html.escape(str(t), quote=True)


def _n(v):
    return format(int(v), ',')


def _pesos(v):
    return '$' + format(v, ',.2f')


def _mdp(v):
    return '$' + format(v / 1e6, ',.1f') + ' mdp'


def _dmy(s):
    try:
        return datetime.datetime.strptime(s, '%d/%m/%Y').date()
    except (TypeError, ValueError):
        return None


def _iso(s):
    try:
        return datetime.date.fromisoformat((s or '')[:10])
    except ValueError:
        return None


def _fecha(d):
    MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    return '%d de %s de %d' % (d.day, MES[d.month - 1], d.year)


def _js(ruta, var):
    """El objeto de un archivo window.VAR = {...}; (o window.VAR[clave] = {...};)."""
    s = open(ruta, encoding='utf-8').read()
    k = s.find('window.%s[' % var)
    i = s.index('{', s.index('] = ', k) if k >= 0 else s.index('window.' + var))
    return json.loads(s[i:s.rindex('}') + 1])


def sat():
    S = _js(os.path.join(DATA, 'sat-69b.js'), 'SAT_69B')
    return S['meta'], {r[0]: r for r in S['r']}


def _cmx(S):
    """Contratos 2025-2026 de quienes están en la lista 69-B (ComprasMX)."""
    T = _js(os.path.join(DATA, 'comprasmx', 'inst.js'), 'CMX_INST')
    meta, inst = T['meta'], T['i']
    out, completo = [], True
    rico = T.get('cruce69b')
    for r in T['sat']:
        rfc = r[0]
        if rico is not None:
            for k in rico.get(rfc, []):
                f, campo = (k[5], 'firma') if k[5] else (k[6], 'publicacion')
                out.append({'rfc': rfc, 'n': r[1], 'cod': k[0], 'inst': inst.get(k[1], {}).get('s', k[1]), 'imp': k[2], 'mon': k[3],
                            'tp': k[4], 'f': f, 'campo': campo, 'liga': CMX_DETALLE % k[7] if k[7] else '', 'origen': 'ComprasMX'})
            continue
        pre = rfc[:2]
        P = _js(os.path.join(DATA, 'comprasmx', 'p-%s.js' % re.sub(r'[^A-Z0-9]', '_', pre)), 'CMX_P')
        d = P[rfc]
        if d['c'] != len(d['k']):
            completo = False
        for k in d['k']:
            out.append({'rfc': rfc, 'n': d['n'], 'cod': k[0], 'inst': inst.get(k[1], {}).get('s', k[1]), 'imp': k[3], 'mon': k[4],
                        'tp': k[5], 'f': k[6], 'campo': 'publicacion', 'liga': CMX_DETALLE % k[7] if k[7] else '', 'origen': 'ComprasMX'})
    return meta, out, completo, rico is not None


def _cnet():
    ruta = os.path.join(DATA, 'compranet', 'cruce.js')
    if not os.path.exists(ruta):
        return None, []
    T = _js(ruta, 'CNET_CRUCE')
    out = []
    for rfc, d in T['p'].items():
        for k in d['k']:
            out.append({'rfc': rfc, 'n': d['n'], 'cod': k[0], 'inst': k[1], 'imp': k[3], 'mon': k[4], 'tp': k[5],
                        'f': k[6], 'campo': 'firma', 'anio': k[7], 'por': k[8], 'liga': k[9], 'origen': 'CompraNet'})
    return T['meta'], out


def clasifica(c, r):
    """(clase, tipo, días) de un contrato frente a la publicación de su empresa."""
    f = _iso(c['f'])
    if not f:
        return 'pendiente', 'sin_fecha', None
    s, d = r[2], _dmy(r[4])
    pres = _dmy(r[6]) if len(r) > 6 else (d if s == 'P' else None)
    if s == 'F':
        if d and f >= d:
            return 'senal', 'def', (f - d).days
        if pres and f >= pres:
            return 'senal', 'pres_def', (f - pres).days
        return 'antecedente', 'antes', (f - (pres or d)).days if (pres or d) else None
    if s == 'P':
        if d and f >= d:
            return 'senal', 'pre', (f - d).days
        return 'antecedente', 'antes', (f - d).days if d else None
    # Desvirtuado o sentencia favorable: salió de la lista.
    if d and f >= d:
        return 'antecedente', 'salio', (f - d).days
    if pres:
        return ('antecedente', 'salio_durante', (f - pres).days) if f >= pres else ('antecedente', 'antes', (f - pres).days)
    return 'antecedente', 'salio_sin_pres', (f - d).days if d else None


def asf():
    E = json.load(open(ESTAD, encoding='utf-8'))
    serie = {x['cp']: x for x in E['serie']}
    montos = {}
    for x in json.load(open(MDB_SERIE, encoding='utf-8'))['serie']:
        montos[x['cp']] = {'pa': x['porAclarar'], 'rec': x['recuperaciones'], 'url': x['url']}
    m24 = json.load(open(MDB_2024, encoding='utf-8'))
    montos[2024] = {'pa': m24['total']['porAclarar'], 'rec': m24['total']['recuperaciones'],
                    'url': 'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Matriz/MDB_Consolidado.pdf'}
    return E, serie, montos


def datos():
    sm, S = sat()
    cmeta, cmx, completo, firma = _cmx(S)
    nmeta, cnet = _cnet()
    contratos = cmx + cnet
    for c in contratos:
        r = S[c['rfc']]
        c['clase'], c['tipo'], c['dias'] = clasifica(c, r)
        c['sit'] = r[2]
        c['dof'] = r[4]
        c['oficio'] = r[3]
        c['medio'] = r[5]
        c['pres'] = r[6] if len(r) > 6 else ''
        f = _iso(c['f'])
        c['anio'] = f.year if f else int(c.get('anio') or 0)
    E, serie, montos = asf()
    anios_cnet = {int(a) for a in (nmeta or {}).get('anios', {})}
    por_anio = []
    for a in range(PRIMER_ANIO, ULTIMO_ANIO + 1):
        cs = [c for c in contratos if c['anio'] == a]
        fuente = 'ComprasMX' if a >= 2025 else ('CompraNet' if a in anios_cnet else None)
        por_anio.append({'a': a, 'asf': serie.get(a), 'montos': montos.get(a), 'fuente': fuente,
                         'c': len(cs), 'm': sum(c['imp'] for c in cs if c['mon'] == 'MXN'),
                         'senal': sum(1 for c in cs if c['clase'] == 'senal'),
                         'empresas': len({c['rfc'] for c in cs})})
    senales = sorted([c for c in contratos if c['clase'] == 'senal'], key=lambda c: (c['tipo'] != 'def', -c['imp']))
    ants = sorted([c for c in contratos if c['clase'] != 'senal'], key=lambda c: (c['rfc'], c['f']))
    return {'sat': sm, 'cmx': cmeta, 'cnet': nmeta, 'contratos': contratos, 'completo': completo, 'firma': firma,
            'senales': senales, 'ants': ants, 'asf': E, 'anios': por_anio}


# ---------- La página ----------

def _empresa(c):
    return '<b>%s</b> <small>RFC <code>%s</code></small>' % (esc(c['n']), esc(c['rfc']))


def _dof(c):
    return 'publicada como <b>%s</b> en el %s el %s (oficio %s) %s' % (
        SIT[c['sit']].lower(), esc(c['medio']), _fecha(_dmy(c['dof'])), esc(c['oficio']), chip('oficial'))


def _contrato(c):
    campo = 'firmado' if c['campo'] == 'firma' else 'publicado en %s' % c['origen']
    liga = (' <a href="%s" target="_blank" rel="noopener">ver el contrato ↗</a>' % esc(c['liga'])) if c['liga'] else ''
    por = ' · coincide por <b>nombre</b> (el archivo no trae RFC)' if c.get('por') == 'nombre' else ''
    pend = '' if c['campo'] == 'firma' else ' ' + chip('pendiente', P_FIRMA)
    return ('Contrato <code>%s</code> de <b>%s</b>, %s el %s%s, por <b>%s</b>%s %s%s%s' % (
        esc(c['cod']), esc(c['inst']), campo, _fecha(_iso(c['f'])), pend, _pesos(c['imp']),
        '' if c['mon'] == 'MXN' else ' ' + esc(c['mon']), chip('oficial'), por, liga))


def _dias(c):
    if c['dias'] is None:
        return ''
    if c['dias'] >= 0:
        return '<b>%s días después</b> de esa publicación %s' % (_n(c['dias']), chip('derivado'))
    return '<b>%s días antes</b> %s' % (_n(-c['dias']), chip('derivado'))


def _fila_senal(c):
    ico, tx = TIPOS_SENAL[c['tipo']]
    ref = _dmy(c['dof']) if c['tipo'] != 'pres_def' else _dmy(c['pres'])
    return ('<li class="cr-ficha cr-%s" id="e-%s"><p class="cr-ficha-tipo"><span aria-hidden="true">%s</span> %s · '
            '<span class="cr-senal">señal para revisar</span></p>'
            '<p>%s, %s.</p><p>%s: %s.</p>'
            '<p class="cr-chico">Operación: fecha del contrato − fecha de publicación (%s) = %s días.</p></li>') % (
        c['sit'].lower(), esc(c['rfc']), ico, esc(tx), _empresa(c), _dof(c), _contrato(c), _dias(c),
        _fecha(ref), _n(c['dias']))


def _ficha_ant(cs):
    """Una ficha por empresa: lo que declaró el SAT y cada contrato con su lectura."""
    c0 = cs[0]
    items = []
    for c in cs:
        if c['tipo'] == 'sin_fecha':
            tx = 'sin fecha para comparar %s' % chip('pendiente', P_FIRMA)
        else:
            tx = TIPOS_ANT[c['tipo']].lower() + ('' if c['tipo'] != 'salio_sin_pres' else ' ' + chip('pendiente', P_PRES))
        items.append('<li>%s: %s. <small>%s.</small></li>' % (_contrato(c), _dias(c), tx[:1].upper() + tx[1:]))
    return ('<li class="cr-ficha cr-%s" id="e-%s"><p class="cr-ficha-tipo"><span aria-hidden="true">🗂️</span> Antecedente · %d contrato%s</p>'
            '<p>%s, %s.</p><ul class="cr-contratos">%s</ul></li>') % (
        c0['sit'].lower(), esc(c0['rfc']), len(cs), '' if len(cs) == 1 else 's', _empresa(c0), _dof(c0), ''.join(items))


def _ids_unicos(html_txt):
    """Una empresa con varios contratos: solo su primera ficha lleva el id e-RFC."""
    vistos = set()

    def f(m):
        if m.group(1) in vistos:
            return ''
        vistos.add(m.group(1))
        return m.group(0)
    return re.sub(r' id="(e-[A-Z0-9&Ñ]+)"', f, html_txt)


def _tabla(D):
    de, of = chip('derivado'), chip('oficial')
    filas = []
    for x in reversed(D['anios']):
        a, s, m = x['a'], x['asf'], x['montos']
        if s:
            asf_td = ''.join('<td>%s</td>' % _n(s[k]) for k in ('auditorias', 'observaciones', 'PO', 'PRAS', 'PEFCF', 'DH'))
        elif a < 2002:
            asf_td = '<td colspan="6">%s La serie oficial empieza en 2002</td>' % chip('pendiente', P_ASF0)
        elif a == 2025:
            asf_td = '<td colspan="6">En revisión: la ASF entrega su tercera tanda de informes el 20 de febrero de 2027 (LFRCF, art. 35)</td>'
        else:
            asf_td = '<td colspan="6">Aún no toca: la Cuenta Pública 2026 se entrega a la Cámara a más tardar el 30 de abril de 2027 (Constitución, art. 74, fr. VI)</td>'
        pa = '<td>%s</td>' % _mdp(m['pa']) if m else '<td>—</td>'
        if x['fuente']:
            cont = '<td>%s</td><td>%s</td><td>%s</td>' % (
                _n(x['c']), _mdp(x['m']) if x['c'] else '—', ('<b class="cr-num-senal">%s</b>' % x['senal']) if x['senal'] else '0')
        else:
            cont = '<td colspan="3">%s CompraNet aún no integrado</td>' % chip('pendiente', P_CNET)
        filas.append('<tr><th scope="row">%d</th>%s%s%s</tr>' % (a, asf_td, pa, cont))
    return ('<div class="cr-tabla" tabindex="0" role="region" aria-label="Contratos, lista 69-B y ASF por año">'
            '<table><caption>Año por año: lo que fiscalizó la ASF %s y los contratos con empresas de la lista 69-B (conteo y suma %s)</caption>'
            '<thead><tr><th scope="col">Año</th><th scope="col">Auditorías</th><th scope="col">Observaciones</th><th scope="col">Pliegos (PO)</th>'
            '<th scope="col">PRAS</th><th scope="col">Al SAT (PEFCF)</th><th scope="col">Denuncias</th><th scope="col">Por aclarar (MDB)</th>'
            '<th scope="col">Contratos con empresas 69-B</th><th scope="col">Importe</th><th scope="col">Señales</th></tr></thead>'
            '<tbody>%s</tbody></table></div>') % (of, de, ''.join(filas))


def construir(base, ref):
    D = datos()
    sm, E = D['sat'], D['asf']
    of, de = chip('oficial'), chip('derivado')
    S, A = D['senales'], D['ants']
    empresas = {c['rfc'] for c in D['contratos']}
    tot = sum(c['imp'] for c in S if c['mon'] == 'MXN')
    if S:
        hall = ('<ul class="cr-fichas">%s</ul>' % _ids_unicos(''.join(_fila_senal(c) for c in S)))
    else:
        hall = ('<p class="cr-vacio">Hoy no hay ninguna señal: ningún contrato integrado se firmó con una empresa que ya '
                'estuviera publicada como presunta o definitiva. Mira los antecedentes abajo.</p>')
    grupos = {}
    for c in A:
        grupos.setdefault(c['rfc'], []).append(c)
    ant = ('<ul class="cr-fichas">%s</ul>' % ''.join(_ficha_ant(g) for g in grupos.values())) if A else '<p class="cr-vacio">Sin antecedentes.</p>'
    fecha_nota = ('la fecha de firma de cada contrato' if D['firma'] else
                  'la fecha de publicación que guarda nuestro catálogo de ComprasMX: la de firma entra cuando se regenere con sus archivos %s'
                  % chip('pendiente', P_FIRMA))
    cnet = D['cnet']
    cnet_tx = ('integrado: %s' % ', '.join(sorted(cnet['anios']))) if cnet else (
        'todavía no: su portal (upcp-compranet.hacienda.gob.mx) no respondió desde la plataforma, y el importador ya está listo %s' % chip('pendiente', P_CNET))
    return '''
<div class="cr" id="cr">
  <section class="cr-hero" aria-labelledby="cr-tit">
    <h2 class="cr-hero-tit" id="cr-tit">¿El gobierno le compró a empresas de la lista negra del SAT?</h2>
    <p class="cr-txt">Cruzamos tres fuentes oficiales: los <b>contratos</b> (ComprasMX y CompraNet), la <b>lista 69-B</b> del SAT%(r_sat)s y lo que fiscalizó la <b>Auditoría Superior de la Federación</b>, año por año. Separamos <b>lo que ya declaró la autoridad</b> %(of)s de <b>las señales que detectamos nosotros</b> %(de)s: una señal es una pregunta que conviene hacer, nunca una acusación.</p>
    <div class="cr-cifras">
      <div><b>%(n_emp)s</b><span>empresas de la lista 69-B con contratos integrados %(de)s</span></div>
      <div class="cr-c-senal"><b>%(n_sen)s</b><span>señales para revisar: contratos con la empresa ya publicada en la lista (%(tot)s) %(de)s</span></div>
      <div><b>%(n_ant)s</b><span>antecedentes sin señal %(de)s</span></div>
      <div><b>%(aud)s</b><span>auditorías de la ASF a las Cuentas Públicas 2002–2024 %(of)s</span></div>
    </div>
    <nav class="cr-ir" aria-label="Secciones"><a href="#hallazgos">Señales</a><a href="#antecedentes">Antecedentes</a><a href="#por-anio">Año por año</a><a href="#metodo">Cómo lo cruzamos</a></nav>
  </section>

  <section class="cr-sec" id="hallazgos" aria-labelledby="cr-h-tit">
    <h2 class="cr-tit" id="cr-h-tit">🚩 Las señales que detectamos</h2>
    <p class="cr-txt">Contratos firmados el día en que el SAT publicó a la empresa en la lista, o después. La situación, el oficio y la fecha del DOF son del SAT %(of)s; el contrato y su importe, de quien contrató %(of)s; <b>los días entre una fecha y otra, y llamarlo señal, son nuestros</b> %(de)s.</p>
    %(hall)s
    <p class="cr-legal"><span aria-hidden="true">⚖️</span> Una señal no prueba nada: el contrato pudo venir de un procedimiento anterior, la empresa puede desvirtuar la presunción, y la señal no dice si la dependencia revisó la lista. Lo que sí dice el artículo 69-B del Código Fiscal%(r_cff)s es que los comprobantes de quien queda <b>definitivo</b> no producen efecto fiscal. Estar en la lista es una determinación administrativa del SAT, no una condena (Constitución, art. 20, apartado B, fr. I).</p>
  </section>

  <section class="cr-sec" id="antecedentes" aria-labelledby="cr-a-tit">
    <h2 class="cr-tit" id="cr-a-tit">🗂️ Antecedentes: lo que ya declaró la autoridad, sin señal</h2>
    <p class="cr-txt">Empresas que estuvieron o están en la lista y tienen contratos, pero no en el orden que levanta una señal: firmaron antes de ser publicadas, o después de salir de la lista. «Desvirtuado» quiere decir que demostró ante el SAT que sus operaciones existieron; «sentencia favorable», que un tribunal le dio la razón.</p>
    %(ant)s
  </section>

  <section class="cr-sec" id="por-anio" aria-labelledby="cr-y-tit">
    <h2 class="cr-tit" id="cr-y-tit">📅 Año por año</h2>
    <p class="cr-txt">De la Cuenta Pública %(primer)d a hoy. La ASF publica su serie desde 2002 con corte al %(corte_asf)s: auditorías, observaciones y cada acción que promovió. <b>PEFCF</b> es cuando la ASF le pide al SAT que use sus facultades de comprobación: el puente entre la fiscalización y la lista 69-B. La ASF no dice, en esta serie, a qué empresas observó %(pe_emp)s.</p>
    %(tabla)s
    <p class="cr-nota">ASF: %(asf_doc)s, pp. 10 y 12 %(of)s (<a href="%(asf_url)s" target="_blank" rel="noopener">PDF ↗</a>, sha256 %(asf_sha)s…). %(asf_nota)s «Por aclarar» viene de la Matriz de Datos Básicos de cada Cuenta Pública (2019 a 2024), que tiene su propio corte %(of)s. Contratos: conteo y suma de importes antes de impuestos, sin convertir monedas %(de)s; el año es el de %(fecha_nota)s.</p>
  </section>

  <section class="cr-sec" id="metodo" aria-labelledby="cr-m-tit">
    <h2 class="cr-tit" id="cr-m-tit">🧭 Cómo lo cruzamos</h2>
    <ol class="cr-pasos">
      <li><b>Contratos.</b> ComprasMX (2025 y 2026, %(cmx_c)s contratos de sus Datos Abiertos) y el histórico de CompraNet: %(cnet_tx)s.</li>
      <li><b>Lista 69-B.</b> Por RFC contra el listado del SAT (%(sat_total)s registros, corte al %(sat_corte)s) %(of)s. Solo personas morales: las personas físicas no se publican. En los archivos viejos de CompraNet, sin RFC, se compara el nombre, y solo si en la lista hay una sola empresa con ese nombre; se marca así.</li>
      <li><b>Fechas.</b> La del contrato contra la de publicación en el DOF de su situación. Usamos %(fecha_nota)s. De quienes ya salieron de la lista, el catálogo todavía no guarda la fecha en que entraron como presuntas %(pe_pres)s.</li>
      <li><b>La señal.</b> Definitiva o presunta, y contrato el día de la publicación o después: señal para revisar. Desvirtuada o con sentencia favorable: nunca es señal.</li>
      <li><b>La ASF.</b> Año por año, cuánto fiscalizó y qué promovió %(of)s. Cruzar empresa por empresa con sus informes individuales es lo que sigue %(pe_emp)s.</li>
    </ol>
    <h3 class="cr-sub">Lo que este cruce no dice</h3>
    <ul class="cr-lista">
      <li>No dice que hubo un delito ni una irregularidad: dice dónde conviene preguntar.</li>
      <li>No dice cuánto se pagó: ComprasMX y CompraNet publican el importe del contrato (en uno abierto, el máximo), no los pagos.</li>
      <li>No dice que la dependencia supiera: la fecha del DOF es pública, pero si debía revisar la lista antes de contratar, y si lo hizo, es lo que la señal pregunta, no lo que responde.</li>
      <li>Que una empresa no aparezca no la certifica: solo dice que el SAT no la incluyó al corte.</li>
    </ul>
    <p class="cr-nota">Lo arma <code>herramientas/cruce_contratos.py</code> con <code>actualizar_comprasmx.py</code>, <code>actualizar_compranet.py</code>, <code>actualizar_69b.py</code> y <code>extraer_estadisticas_asf.py</code>. Lo que falta está en el <a href="pendientes.html">Registro de pendientes</a>, con quién lo debe.</p>
  </section>

  <section class="cr-sec" aria-labelledby="cr-s-tit">
    <h2 class="cr-tit" id="cr-s-tit">➡️ Sigue la pista</h2>
    <ul class="cr-hermanas">
      <li><a href="herramienta-inspector-efos.html"><span aria-hidden="true">🧾</span><b>Lista negra del SAT</b><small>Busca cualquier RFC en la lista 69-B.</small></a></li>
      <li><a href="contratos-publicos.html"><span aria-hidden="true">📑</span><b>Contratos públicos</b><small>Todos los contratos de ComprasMX, por empresa o institución.</small></a></li>
      <li><a href="herramienta-inspector-asf.html"><span aria-hidden="true">🏛️</span><b>Expedientes de casos de la ASF</b><small>Lo que la Auditoría Superior encontró, con sus montos.</small></a></li>
      <li><a href="garantias.html"><span aria-hidden="true">🚪</span><b>Garantías cívicas</b><small>A qué puerta tocar para preguntar.</small></a></li>
    </ul>
  </section>
</div>
''' % {
        'of': of, 'de': de, 'r_sat': ref('ref-sat-69b'), 'r_cff': ref('ref-cff'),
        'n_emp': _n(len(empresas)), 'n_sen': _n(len(S)), 'n_ant': _n(len(A)), 'tot': _pesos(tot),
        'aud': _n(sum(x['auditorias'] for x in E['serie'])),
        'hall': hall, 'ant': ant, 'tabla': _tabla(D), 'primer': PRIMER_ANIO,
        'corte_asf': _fecha(_iso(E['corte'])), 'asf_doc': esc(E['doc']), 'asf_url': esc(E['url']), 'asf_sha': E['sha256'][:12],
        'asf_nota': esc(E['nota']), 'fecha_nota': fecha_nota, 'cnet_tx': cnet_tx,
        'cmx_c': _n(sum(a['contratos'] for a in D['cmx']['archivos'])),
        'sat_total': _n(sm['total']), 'sat_corte': esc(sm['corte']),
        'pe_pres': chip('pendiente', P_PRES), 'pe_emp': chip('pendiente', P_EMPRESA),
    }


# ---------- El chat ----------

def bot():
    """Lo que el chat necesita para mencionar el hallazgo (o el antecedente) y
    llevar a su sección. Sin cifras propias: las mismas de la página."""
    D = datos()
    hall = [{'rfc': c['rfc'], 'n': c['n'], 'sit': SIT[c['sit']], 'dof': _fecha(_dmy(c['dof'])), 'f': _fecha(_iso(c['f'])),
             'campo': c['campo'], 'dias': c['dias'], 'imp': c['imp'], 'mon': c['mon'], 'inst': c['inst'], 'tx': TIPOS_SENAL[c['tipo']][1]}
            for c in D['senales']]
    ant = {}
    for c in D['ants']:
        ant.setdefault(c['rfc'], {'n': c['n'], 'sit': SIT[c['sit']], 'tx': TIPOS_ANT.get(c['tipo'], 'Sin fecha para comparar'), 'c': 0})
        ant[c['rfc']]['c'] += 1
    E = D['asf']
    ult = E['serie'][-1]
    return {'pag': PAGINA, 'hall': hall, 'ant': ant, 'nEmp': len({c['rfc'] for c in D['contratos']}),
            'cnet': bool(D['cnet']), 'firma': D['firma'],
            'asf': {'desde': E['serie'][0]['cp'], 'hasta': ult['cp'], 'aud': sum(x['auditorias'] for x in E['serie']),
                    'doc': E['doc'], 'url': E['url'], 'pefcf': sum(x['PEFCF'] for x in E['serie'])},
            'sat': {'corte': D['sat']['corte'], 'url': D['sat']['url']}}
