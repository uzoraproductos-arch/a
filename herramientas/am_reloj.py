# -*- coding: utf-8 -*-
"""Primera aplicacion de Costo Ambiental: «El reloj y el año» en pagina
propia (16-10-2026). Sustituye al marco que cargaba la portada entera
(index.html?ir=ambiente&ancla=eb-amreloj).

Reproduce dos piezas del motor (audit-engine.js) con los mismos datos:

* el reloj del dano ambiental (renderCostoAmbiental, seccion 1, y
  amArrancarReloj): el costo anual del INEGI (cuentas_ecologicas.ctada)
  entre los 31,536,000 segundos de un ano de 365 dias, y la basura diaria
  de la SEMARNAT (ambiente.residuos.generacionTdia) entre 86,400 segundos;
* la simulacion «Un año de cuentas en veinte segundos» (renderAmCarrera,
  amSeries, amItems, amNota y amCarreraPintar), con sus cinco vistas.

Todas las cifras, las tablas, las notas y los remates de cierre se
escriben aqui; el JS (am-reloj.js) solo mueve los contadores, cambia de
vista y anima las barras. Los datos que necesita van en #arDatos.

Correcciones frente al motor (se dicen en el reporte y en la pagina):
* El renglon «Gasto en protección ambiental, todo el país» es solo del
  sector publico consolidado (la propia base lo dice: excluye al sector
  privado y a los hogares). Se rotula asi.
* En el remate del huachicol, el motor ponia el chip oficial despues de la
  tasa por segundo ($175.13/s), que es una division. Aqui la recaudacion y
  los litros llevan oficial; la tasa y el anualizado, derivado, con su
  operacion; las cifras salen de la base (ritmo_vistas.huachicol), no van
  escritas a mano.
* El reloj del ano en curso dice el ano del calendario del lector, no un
  2026 fijo.

Regla de la plataforma (AGENTS.md, §2): nada se estima. La cifra de
$600,000 mdp del huachicol va rayada, con su chip pendiente y su ficha del
Registro (huachicol-est-1), y no entra en ninguna cuenta.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['amreloj']).
"""
import html
import json
from decimal import Decimal, ROUND_HALF_UP

from presupuesto_modulos import chip

ESTILOS = ['am-reloj.css']
SCRIPTS = ['am-reloj.js']

SEG_ANO = 31536000  # 365 dias, la misma base que el motor (CC_SEG_ANO)
DUR_MS = 20000      # la simulacion dura veinte segundos, como AM_CAR_MS

VISTAS = [
    ('ambiental', '🌿', 'Deuda y ambiente'),
    ('poderes', '🏛️', 'Los Poderes de la Unión'),
    ('obras', '🏗️', 'Obra pública por sector'),
    ('huachicol', '⛽', 'Huachicol fiscal'),
    ('todos', '🌐', 'Todo junto'),
]

IDS = {
    'ambiental': ['intereses', 'dano', 'gpa', 'ramo16'],
    'poderes': ['ejecutivo', 'autonomos', 'judicial', 'legislativo'],
    'obras': ['obra_energia', 'obra_transporte', 'obra_ramo33', 'obra_agua', 'obra_salud', 'obra_otros'],
    'huachicol': ['declarado', 'obra_energia', 'obra_ramo33', 'judicial', 'ramo16', 'legislativo', 'recaudacion'],
    'todos': ['ejecutivo', 'intereses', 'dano', 'declarado', 'obra_energia', 'gpa', 'obra_transporte', 'obra_ramo33',
              'judicial', 'autonomos', 'ramo16', 'obra_agua', 'legislativo', 'obra_salud', 'recaudacion'],
}


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def esc(t):
    return html.escape(str(t if t is not None else ''), quote=True)


def _r(v, d=0):
    """Redondeo como Math.round / toLocaleString del motor (mitades hacia arriba)."""
    q = Decimal(1).scaleb(-d)
    return float(Decimal(repr(v)).quantize(q, rounding=ROUND_HALF_UP))


def num(v, d=0):
    """amNum() del motor."""
    return format(_r(v, d), ',.%df' % d)


def pesos(v):
    """pdPesos() del motor."""
    return '$' + format(int(_r(v)), ',')


def mdp_fijo(v):
    """formatMdpFijo() del motor: mdp sin decimales."""
    n = int(_r(v))
    return ('-$' if n < 0 else '$') + format(abs(n), ',') + ' mdp'


def pd_mdp(p, d=1):
    """pdMdp() del motor: recibe pesos."""
    return '$' + format(_r(p / 1e6, d), ',.%df' % d) + ' mdp'


def liga(url, texto):
    if not url:
        return esc(texto)
    return '<a class="ar-fuente" href="%s" target="_blank" rel="noopener noreferrer">%s ↗</a>' % (esc(url), esc(texto))


def items(base, refs):
    """amItems() + los cuatro renglones que agrega amSeries()."""
    A, C = base['ambiente'], base['cuentas_ecologicas']
    R = base['ritmo_vistas']
    F, H = R['fuentes'], base.get('huachicol_fiscal') or {}
    HF = H.get('fuentes') or {}
    P, O, HU = R['poderes'], R['obra'], R['huachicol']

    def fte(f):
        return liga(f.get('url'), f.get('doc')) if f else ''

    def amref(rid, texto):
        r = refs.get(rid)
        return liga(r['url'], texto) if r else chip('pendiente') + ' ' + esc(texto)

    def amfuente(clave, pagina):
        f = A['fuentes'].get(clave)
        if not f:
            return chip('pendiente') + ' fuente por documentar'
        pag = '' if pagina in (None, '') else (', p. %s' % pagina if str(pagina).isdigit() else ', %s' % pagina)
        return liga(f['url'], (f.get('corto') or f['doc']) + pag)

    csv = fte(F['pef26csv'])
    ceem = amref('ref-ceem-2024', 'INEGI, Cuentas Económicas y Ecológicas 2024')
    it = {}
    it['ejecutivo'] = dict(nom='Poder Ejecutivo, con los ramos generales que administra', anio='2026', mdp=P['ejecutivo'],
                           estado='derivado', c=2, fuente=fte(F['pef26dof']) + ' · ' + csv, que=P['operacion_ejecutivo'])
    it['autonomos'] = dict(nom='Órganos autónomos (INE, CNDH, INEGI y Fiscalía)', anio='2026', mdp=P['autonomos'],
                           estado='derivado', c=4, fuente=csv,
                           que='Suma de sus ramos: ' + ', '.join('%s %s' % (k, mdp_fijo(v)) for k, v in P['autonomos_desglose'].items()) + '.')
    it['judicial'] = dict(nom='Poder Judicial de la Federación', anio='2026', mdp=P['judicial'], estado='oficial', c=4,
                          fuente=csv, que='Lo aprobado al ramo 03.')
    it['legislativo'] = dict(nom='Poder Legislativo (Cámaras y Auditoría Superior)', anio='2026', mdp=P['legislativo'],
                             estado='oficial', c=4, fuente=csv, que='Lo aprobado al ramo 01.')
    for x in O['sectores']:
        it[x['id']] = dict(nom='Obra pública · ' + x['nom'], anio='2026', mdp=x['mdp'], estado='derivado', c=2, fuente=csv,
                           que=x['como'] + '. ' + O['definicion'])
    it['recaudacion'] = dict(nom='Huachicol: lo recaudado al detectar combustible no declarado', anio='sep 2025–jun 2026',
                             mdp=HU['recaudacion_mdp'], estado='oficial', c=3, fuente=fte(F.get(HU['fuente'])), que=HU['texto'])
    it['declarado'] = dict(nom='Huachicol: la cifra que se mencionó en 2025', anio='2025', mdp=HU['declarado_mdp'],
                           estado='pendiente', pend='huachicol-est-1', c=0,
                           fuente=' · '.join(fte(HF.get(k) or F.get(k)) for k in HU['declarado_fuentes']), que=HU['declarado_texto'])
    rel = next((x for x in ((base.get('calculadora_civica') or {}).get('relojes') or {}).get('fuentes') or [] if x['id'] == 'intereses'), None)
    if rel:
        it['intereses'] = dict(nom='Intereses de la deuda pública', anio='2026', mdp=rel['anual_mdp'], estado=rel['estado'], c=1,
                               fuente=amref(rel['refKey'], 'PEF 2026, Anexo 8'),
                               que='Lo que el presupuesto paga por lo prestado en años anteriores.')
    it['dano'] = dict(nom='Daño ambiental del país', anio='2024', mdp=C['ctada']['total_mdp'], estado=C['ctada']['estado'], c=3,
                      fuente=ceem, que='Lo que costó agotar los recursos y ensuciar aire, agua y suelo.')
    gpa = C['gasto_proteccion_ambiental']
    # Correccion: el motor decia «todo el país»; la cifra es solo del sector publico.
    it['gpa'] = dict(nom='Gasto público en protección ambiental (sector público consolidado)', anio='2024', mdp=gpa['monto_mdp'],
                     estado=gpa.get('estado') or 'oficial', c=3, fuente=ceem,
                     que='Gasto en protección ambiental ejercido exclusivamente por el sector público consolidado (INEGI CEEM 2024, pág. 2); no incluye lo que gastan empresas privadas ni hogares.')
    ap = A['presupuesto']['aprobado2026']
    it['ramo16'] = dict(nom='Presupuesto federal de Medio Ambiente (Ramo 16)', anio='2026', mdp=ap['valor'] / 1e6, estado=ap['estado'],
                        c=2, fuente=amfuente('PEF', ap.get('pagina')), que='Lo aprobado a la SEMARNAT, la Conagua y sus órganos.')
    for k, v in it.items():
        v['id'] = k
    return it


def remate(v, S, it, base):
    """El texto que aparece al cerrar el año (amCarreraPintar con t = 1)."""
    por = {x['id']: x['mdp'] for x in S}
    g = lambda k: por.get(k, 0)  # noqa: E731
    if v == 'poderes':
        tot = g('ejecutivo') + g('autonomos') + g('judicial') + g('legislativo')
        return ('Al cerrar el año, de cada $100 del Presupuesto 2026, <b>$%s</b> los ejerció el Ejecutivo con sus ramos generales, '
                '<b>$%s</b> el Poder Judicial, <b>$%s</b> los órganos autónomos y <b>$%s</b> el Legislativo. %s'
                % (num(g('ejecutivo') / tot * 100, 2), num(g('judicial') / tot * 100, 2), num(g('autonomos') / tot * 100, 2),
                   num(g('legislativo') / tot * 100, 2), chip('derivado')),
                'Cada parte ÷ la suma de las cuatro × 100.')
    if v == 'obras':
        tot = sum(x['mdp'] for x in S)
        ener = g('obra_energia')
        t = 'Al cerrar el año, el Presupuesto 2026 habrá destinado <b>%s</b> a obra pública. De cada $100, <b>$%s</b> son de Pemex y CFE.' % (
            mdp_fijo(tot), num(ener / tot * 100, 1))
        op = 'Suma de los seis sectores; Pemex y CFE ÷ esa suma × 100'
        if 'intereses' in it:
            i = it['intereses']['mdp']
            t += ' Los intereses de la deuda del mismo año (%s) equivalen a <b>%s veces</b> toda esa obra.' % (mdp_fijo(i), num(i / tot, 1))
            op += '; intereses ÷ obra total'
        return t + ' ' + chip('derivado'), op + '.'
    if v == 'huachicol':
        HU = base['ritmo_vistas']['huachicol']
        rec, dec, ener = g('recaudacion'), g('declarado'), g('obra_energia')
        dias, seg = HU['dias_documentados'], HU['segundos_documentados']
        tasa = rec * 1e6 / seg
        anual = rec / dias * 365
        t = ('Lo único documentado oficialmente: <b>%s</b> cobrados del %s al detectar %s millones de litros no declarados %s. '
             'Son %s días: una tasa de $%s por segundo y, a ese ritmo, %s en un año completo %s; equivalen al %s %% de la obra anual de Pemex y CFE %s. '
             'La cifra aislada de %s que se mencionó en tribuna en 2025 carece de estudio metodológico oficial publicado por Hacienda %s.'
             % (mdp_fijo(rec), esc(HU['periodo']), num(HU['litros_millones'], 1), chip('oficial'), num(dias), num(tasa, 2),
                mdp_fijo(anual), chip('derivado'), num(rec / ener * 100, 1), chip('derivado'), mdp_fijo(dec),
                chip('pendiente', 'huachicol-est-1')))
        return t, 'Tasa: recaudación ÷ %s segundos del periodo. Anualizado: recaudación ÷ %s días × 365. Porcentaje: recaudación ÷ obra de Pemex y CFE × 100.' % (
            num(seg), num(dias))
    if v == 'todos':
        obra = base['ritmo_vistas']['obra']['total']
        return ('Al cerrar el año, la cifra más grande es el gasto del Ejecutivo (%s). Los intereses de la deuda (%s) y el daño ambiental de 2024 (%s) '
                'rebasan, cada uno, toda la obra pública del año (%s). %s'
                % (mdp_fijo(g('ejecutivo')), mdp_fijo(g('intereses')), mdp_fijo(g('dano')), mdp_fijo(obra), chip('derivado')),
                'Comparación directa de las cifras anuales; no se suman entre sí.')
    r16 = g('ramo16')
    return ('Al cerrar el año, por cada peso del presupuesto federal de Medio Ambiente, el país pagó <b>$%s</b> de intereses de su deuda '
            'y perdió <b>$%s</b> por daño ambiental. %s' % (num(g('intereses') / r16, 1), num(g('dano') / r16, 1), chip('derivado')),
            'Intereses ÷ Ramo 16; daño ÷ Ramo 16.')


def nota(v, base):
    HU = base['ritmo_vistas']['huachicol']
    reparto = ' La simulación reparte cada cifra en partes iguales entre los 365 días; el gasto real sigue su calendario.'
    if v == 'poderes':
        return chip('derivado') + ' Las cuatro barras son partes del mismo presupuesto 2026 y suman su gasto neto total. La del Ejecutivo se obtiene por diferencia e incluye la deuda, lo que se reparte a estados y municipios y las pensiones: no es solo el gasto de las secretarías.' + reparto
    if v == 'obras':
        return chip('derivado') + ' ' + esc(base['ritmo_vistas']['obra']['definicion']) + ' Los sectores son una agrupación de Auditavisión; la cifra de cada ramo es la del CSV oficial.' + reparto
    if v == 'huachicol':
        return (chip('pendiente', 'huachicol-evasion') + ' Ni el SAT ni Hacienda han publicado cuánto se evade por huachicol fiscal: está pendiente por falta de transparencia de esas dependencias. '
                'La barra rayada es la cifra que se mencionó en octubre de 2025 y que la Presidencia aclaró que no es oficial: se muestra para dimensionar lo que se discutió, no entra en ninguna cuenta. '
                'La única cifra con documento es la recaudación del Segundo Informe (%s, diez meses). La Ley de Ingresos 2027 obliga al SAT a publicar su estudio de evasión (art. 30). '
                '<a href="auditoria-huachicol-fiscal.html">Lo que se sabe y lo que falta del huachicol fiscal ➔</a>' % esc(HU['periodo']))
    if v == 'todos':
        return chip('derivado') + ' Mezcla cifras de 2024 (INEGI) y 2026 (presupuesto aprobado), y una pendiente (rayada). Sirve para ver órdenes de magnitud, no para sumar.' + reparto
    return chip('derivado') + ' La simulación reparte cada cifra anual en partes iguales entre los 365 días; en la realidad los intereses se pagan en fechas fijas y el daño no es parejo. Dos cifras son de 2026 (presupuesto aprobado) y dos de 2024 (lo último que publicó el INEGI): se comparan por su orden de magnitud, no como si fueran del mismo año.'


def _chip_it(x):
    return chip(x['estado'], x.get('pend'))


def vista_html(v, ico, et, S, it, base, activa):
    mx = max(x['mdp'] for x in S)
    filas = []
    for x in S:
        cls = 'ar-c%d' % x['c'] if x['c'] else 'ar-pend'
        w = max(0.6, x['mdp'] / mx * 100)
        filas.append(
            '<li class="ar-fila" data-v="%s" data-w="%.3f">'
            '<span class="ar-nom"><i class="ar-sw %s" aria-hidden="true"></i><span>%s <small>%s</small>%s</span></span>'
            '<span class="ar-riel" aria-hidden="true"><span class="ar-barra %s"></span></span>'
            '<span class="ar-val ar-num" data-fin="%s">$0 mdp</span>'
            '<details class="ar-que"><summary>¿Qué es?</summary><p>%s</p><p class="ar-que-f">%s · %s al año · %s</p></details>'
            '</li>'
            % (repr(x['mdp']), w, cls, esc(x['nom']), esc(x['anio']), (' ' + _chip_it(x)) if x['estado'] == 'pendiente' else '',
               cls, mdp_fijo(x['mdp']), esc(x['que']), _chip_it(x), mdp_fijo(x['mdp']), x['fuente']))
    tabla = ''.join(
        '<tr><td>%s</td><td>%s</td><td class="ar-num">%s</td><td class="ar-num">%s</td><td>%s %s</td></tr>'
        % (esc(x['nom']), esc(x['anio']), mdp_fijo(x['mdp']), pesos(x['mdp'] * 1e6 / SEG_ANO), _chip_it(x), x['fuente'])
        for x in S)
    rem, op = remate(v, S, it, base)
    return ('<div class="ar-vista" id="arVista-%s" data-vista="%s" role="tabpanel" aria-labelledby="arTab-%s"%s>\n'
            '  <h3 class="ar-vista-tit"><span aria-hidden="true">%s</span> %s</h3>\n'
            '  <ol class="ar-barras">\n    %s\n  </ol>\n'
            '  <div class="ar-remate" data-remate hidden><p>%s</p><p class="ar-op">Operación: %s</p></div>\n'
            '  <details class="ar-tabla-d"><summary>Ver las cifras en tabla, con su documento</summary>'
            '<div class="ar-tabla-w"><table class="ar-tabla"><thead><tr><th>Concepto</th><th>Año</th><th>Al año</th><th>Por segundo</th><th>Documento</th></tr></thead>'
            '<tbody>%s</tbody></table></div>'
            '<p class="ar-nota">Por segundo: cifra anual ÷ %s segundos (365 días) %s.</p></details>\n'
            '  <p class="ar-nota">%s</p>\n'
            '</div>'
            % (v, v, v, '' if activa else ' hidden', ico, esc(et), '\n    '.join(filas), rem, esc(op), tabla, num(SEG_ANO),
               chip('derivado'), nota(v, base)))


def construir(base, ref):
    refs = {r['id']: r for r in base.get('referencias_legales', [])}
    A, C = base['ambiente'], base['cuentas_ecologicas']
    R = A['residuos']
    dano_anual = C['ctada']['total_mdp'] * 1e6
    por_seg = dano_anual / SEG_ANO
    tdia = R['generacionTdia']['valor']
    kg_seg = tdia * 1000 / 86400
    ceem_r = refs.get('ref-ceem-2024')
    ceem = liga(ceem_r['url'], 'INEGI, Cuentas Económicas y Ecológicas 2024') if ceem_r else chip('pendiente') + ' INEGI'
    dbgir = A['fuentes']['DBGIR']
    dbgir_l = liga(dbgir['url'], dbgir['corto'] + ', p. %s' % R['generacionTdia']['pagina'])

    # El mismo ritmo en otras escalas (derivado, salvo la basura diaria,
    # que es la cifra que publica la SEMARNAT).
    escalas = [('segundo', 1), ('minuto', 60), ('hora', 3600), ('día', 86400)]
    filas_esc = []
    for nom, s in escalas:
        d = por_seg * s
        kg = kg_seg * s
        dano_t = pesos(d) if d < 1e8 else pd_mdp(d, 1)
        bas_t = (num(kg, 0) + ' kg') if kg < 10000 else (num(kg / 1000, 0) + ' toneladas')
        bas_chip = chip('oficial') if s == 86400 else chip('derivado')
        filas_esc.append('<tr><th scope="row">Cada %s</th><td class="ar-num">%s %s</td><td class="ar-num">%s %s</td></tr>'
                         % (nom, dano_t, chip('derivado'), bas_t, bas_chip))

    it = items(base, refs)
    tabs, vistas = [], []
    for k, (v, ico, et) in enumerate(VISTAS):
        S = [it[i] for i in IDS[v] if i in it]
        tabs.append('<button type="button" class="ar-tab" role="tab" id="arTab-%s" data-vista="%s" aria-controls="arVista-%s" aria-selected="%s"%s>'
                    '<span aria-hidden="true">%s</span> %s</button>'
                    % (v, v, v, 'true' if k == 0 else 'false', '' if k == 0 else ' tabindex="-1"', ico, esc(et)))
        vistas.append(vista_html(v, ico, et, S, it, base, k == 0))

    datos = {'porMs': dano_anual / (SEG_ANO * 1000), 'kgMs': tdia * 1000 / 86400000, 'durMs': DUR_MS,
             'vistas': [v for v, _, _ in VISTAS]}

    return '''<div class="ar" id="arRaiz">
  <section class="ar-arranque" aria-labelledby="arArrTit">
    <p class="ar-kicker">Costo Ambiental · aplicación 2</p>
    <h2 class="ar-grande" id="arArrTit">Mientras lees, el país pierde dinero. Mira cuánto, y cómo se ve un año entero.</h2>
    <p class="ar-txt">Dos piezas: un <b>reloj</b> que reparte por segundo el costo del daño ambiental que calcula el INEGI y la basura que cuenta la SEMARNAT, y una <b>simulación</b> que acumula, día por día, las grandes cifras del erario en veinte segundos.</p>
    <ol class="ar-indice" aria-label="En esta página">
      <li><a href="#arReloj"><span class="ar-n">1</span> El reloj del daño</a></li>
      <li><a href="#arAnio"><span class="ar-n">2</span> Un año en veinte segundos</a></li>
      <li><a href="#arDocs"><span class="ar-n">3</span> Los documentos</a></li>
    </ol>
  </section>

  <section class="ar-panel" id="arReloj" aria-labelledby="arRelTit">
    <h2 class="ar-tit" id="arRelTit"><span aria-hidden="true">🌎</span> El reloj del daño ambiental</h2>
    <p class="ar-txt">El INEGI calcula cuánto le cuesta al país agotar sus recursos y dañar su ambiente: <b>{dano}</b> en 2024 {c_of}, el <b>{pib} % del PIB</b> {c_of}. Repartido en el tiempo, se ve así:</p>
    <div class="ar-pantalla" id="arPantalla">
      <div class="ar-cont"><span class="ar-cont-t">Desde que abriste esta página, daño ambiental</span><strong class="ar-num" id="arDano">$0</strong></div>
      <div class="ar-cont"><span class="ar-cont-t">Basura generada en el país en ese mismo tiempo</span><strong class="ar-num" id="arBasura">0 kg</strong></div>
      <div class="ar-cont"><span class="ar-cont-t">En lo que va de <span id="arAnioActual">2026</span>, al ritmo de 2024</span><strong class="ar-num" id="arAnioAcum">$0</strong></div>
      <p class="ar-lleva" aria-live="off">Llevas <b class="ar-num" id="arLapso">0 s</b> en la página <span id="arEstado"></span></p>
    </div>
    <div class="ar-mandos" role="group" aria-label="Mandos del reloj">
      <button type="button" class="ar-boton" id="arRelPausa" aria-pressed="false">❚❚ Pausa</button>
      <button type="button" class="ar-boton ar-boton-2" id="arRelCero">↺ Reiniciar</button>
    </div>
    <p class="ar-nota">{c_der} {porseg} por segundo (costo anual ÷ {seg} segundos del año) y {kgseg} kg de basura por segundo ({tdia} toneladas diarias ÷ 86,400 segundos). Fuentes: {ceem} y {dbgir}. El dato de 2025 lo publica el INEGI en diciembre de 2026; mientras, el reloj usa el ritmo de 2024.</p>
    <details class="ar-tabla-d"><summary>El mismo ritmo, en otras escalas</summary>
      <div class="ar-tabla-w"><table class="ar-tabla ar-escalas"><thead><tr><th>Al ritmo de 2024</th><th>Daño ambiental</th><th>Basura</th></tr></thead><tbody>
        {escalas}
      </tbody></table></div>
      <p class="ar-nota">Daño: costo anual del INEGI ÷ segundos del año × segundos de cada lapso. Basura: la SEMARNAT publica las {tdia} toneladas diarias; el resto la reparte ÷ 86,400 segundos.</p>
    </details>
  </section>

  <section class="ar-panel" id="arAnio" aria-labelledby="arAnioTit">
    <h2 class="ar-tit" id="arAnioTit"><span aria-hidden="true">📊</span> Un año de cuentas en veinte segundos</h2>
    <p class="ar-txt">Pulsa «Simular un año» y ve cómo se acumulan, día por día, las grandes cifras del erario: los intereses de la deuda y el daño ambiental, los tres Poderes de la Unión, la obra pública de 2026 por sector y lo que se sabe del huachicol fiscal. Elige qué comparar; todas van en la misma escala, en pesos. También puedes arrastrar el día.</p>
    <div class="ar-tabs" role="tablist" aria-label="Qué comparar">
      {tabs}
    </div>
    <div class="ar-sim">
      <div class="ar-mandos">
        <button type="button" class="ar-boton ar-play" id="arPlay">▶ Simular un año</button>
        <button type="button" class="ar-boton ar-boton-2" id="arFin">⏭ Ver el cierre del año</button>
        <button type="button" class="ar-boton ar-boton-2" id="arCero">↺ Reiniciar</button>
      </div>
      <p class="ar-fecha"><span class="ar-num" id="arFecha" aria-live="polite">1 de enero · día 1</span></p>
      <label class="ar-dia" for="arDia"><span class="ar-dia-t">Día del año</span>
        <input type="range" id="arDia" min="0" max="365" step="1" value="0" aria-valuetext="1 de enero, día 1"></label>
      {vistas}
    </div>
  </section>

  <section class="ar-panel" id="arDocs" aria-labelledby="arDocsTit">
    <h2 class="ar-tit" id="arDocsTit"><span aria-hidden="true">📚</span> Los documentos</h2>
    <ul class="ar-docs">
      <li>Daño ambiental y gasto público en protección ambiental: {ceem} {r_ceem}</li>
      <li>Basura generada al día: {dbgir}</li>
      <li>Intereses de la deuda y presupuesto 2026: Presupuesto de Egresos de la Federación 2026 {r_pef}; Poderes, órganos autónomos y obra pública: {csv}</li>
      <li>Huachicol fiscal: {ig2}</li>
    </ul>
    <p class="ar-nota">Las cifras con chip <b>derivado</b> son cuentas sobre cifras oficiales, con la operación dicha. Lo que todavía nos deben las dependencias está en el <a href="pendientes.html">Registro de pendientes</a>. Si encuentras un error, <a href="comunidad-erratas.html">repórtalo</a>.</p>
    <p class="ar-hermanas">Sigue en Costo Ambiental: <a href="herramienta-ambiente-ticket.html">🧾 Tu estado de cuenta ambiental</a> · <a href="herramienta-ambiente-pib.html">📈 ¿Cuánto del crecimiento es real?</a> · <a href="herramienta-ambiente-inversion.html">🌱 Simulador de inversión ambiental</a> · <a href="herramienta-ambiente-auditor.html">🔍 Auditor ambiental</a> · <a href="herramienta-ambiente-crisis.html">🌀 Crisis ambientales</a></p>
    <p class="ar-hermanas">Otros relojes y cuentas: <a href="herramienta-calculadora-reloj.html">⏱️ El reloj de la deuda</a> · <a href="numeros-lo-que-cuestan-los-poderes.html">🏛️ Lo que cuestan los Poderes</a> · <a href="herramienta-megaobras-sector.html">🏗️ Megaobras por sector</a> · <a href="auditoria-huachicol-fiscal.html">⛽ Huachicol fiscal</a></p>
  </section>
  <script type="application/json" id="arDatos">{datos}</script>
</div>'''.format(
        dano=pd_mdp(dano_anual), pib=num(C['ctada']['pct_pib'], 1), c_of=chip('oficial'), c_der=chip('derivado'),
        porseg=pesos(por_seg), seg=num(SEG_ANO), kgseg=num(kg_seg, 0), tdia=num(tdia), ceem=ceem, dbgir=dbgir_l,
        escalas='\n        '.join(filas_esc), tabs='\n      '.join(tabs), vistas='\n      '.join(vistas),
        r_ceem=ref('ref-ceem-2024'), r_pef=ref('ref-pef2026'),
        csv=liga(base['ritmo_vistas']['fuentes']['pef26csv']['url'], base['ritmo_vistas']['fuentes']['pef26csv']['doc']),
        ig2=liga(base['ritmo_vistas']['fuentes']['ig2']['url'], base['ritmo_vistas']['fuentes']['ig2']['doc']),
        datos=_json(datos))
