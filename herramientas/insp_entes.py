# -*- coding: utf-8 -*-
"""Modo Inspector, aplicacion 4: «Auditor de entes publicos» en pagina
propia (herramienta-inspector-entes.html, 12-10-2026).

Antes la pagina cargaba la portada entera en un marco (index.html con
audit-engine.js y audit-database.js, mas de 3 MB) para abrir el explorador
de los tres niveles de gobierno del motor (inspEntes, inspDiagnostico,
inspExpedienteFederal / inspExpedienteLocal). Ahora:

- Python escribe el arranque, el directorio federal ya con sus cifras
  (ejercido 2025, oficial), el metodo con los pesos y los umbrales, y las
  fuentes: se lee sin JavaScript.
- Los datos federales y estatales van embebidos como JSON compacto, con el
  resumen de la ASF ya sumado aqui (misma regla que inspFedAsf del motor).
- assets/auditor/js/insp-entes.js hace lo que hacia el motor: las cuatro
  o cinco preguntas con su semaforo, las incongruencias entre documentos,
  el circulo de salud financiera, el buscador, los filtros y la ficha para
  copiar. Los municipios (padron INEGI y rendicion de cuentas) se cargan al
  vuelo de los archivos que ya existen, solo cuando se piden.

Es un traslado: mismos pesos (40/35/25), mismos umbrales, mismos textos y
las mismas salvaguardas: «por aclarar no es robado», «una senal no es una
acusacion», el indice es una construccion de Auditavision y no un dictamen.

Lo llama apartados.insp_nativa() (INSP_NATIVAS['inspentes']).
"""
import json
import os
import re

from poderes_modulo import _loc, _fijo, esc

ESTILOS = ['insp-entes.css']
SCRIPTS = ['insp-entes.js']

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Los mismos del motor (INSP_PESOS, INSP_FED_UMBRALES, INSP_LOC_UMBRALES).
PESOS = {'autonomia': 40, 'observado': 35, 'holgura': 25}
UF = {'desvioAlerta': 10, 'desvioGrave': 25, 'pagoAlerta': 5, 'ritmoBajo': 80, 'ritmoAlto': 110}
UL = {'estCuadreAlerta': 2, 'estCuadreGrave': 5, 'munCuadreAlerta': 5, 'munCuadreGrave': 25, 'munMinimo': 1,
      'depAlerta': 75, 'asfGravePct': 1, 'munAsfGravePct': 5, 'munAsfGraveMdp': 50}

PODERES = {'ejecutivo': ('Poder Ejecutivo', '🦅'), 'legislativo': ('Poder Legislativo', '🏛️'),
           'judicial': ('Poder Judicial', '⚖️'), 'autonomo': ('Autónomos', '🛡️')}

# Texto del motor (MUN_SIN_HACIENDA.CDMX.aviso), art. 122 constitucional.
CDMX_AVISO = (
    '<b>La Ciudad de México no tiene municipios.</b> Tiene dieciséis '
    '<b>demarcaciones territoriales</b> a cargo de alcaldías, y el artículo 122, '
    'apartado A, fracción VI de la Constitución dispone que, «sujeto a las previsiones '
    'de ingresos de la hacienda pública de la Ciudad de México, la Legislatura aprobará '
    'el presupuesto de las Alcaldías, las cuales lo ejercerán de manera autónoma». No '
    'tienen la hacienda propia que el artículo 115 reconoce a los municipios: ejercen la '
    'asignación que les aprueba el Congreso capitalino. De ahí que el INEGI no las levante '
    'en su estadística municipal, y que aquí aparezcan sin cifra en lugar de en ceros.')

MUN_ARCHIVOS = ['municipios-efipem.js', 'municipios-rendicion.js']

# Un solo navegador (pedido del autor, 21-10-2026): el buscador, los tres
# niveles, los filtros y el directorio van juntos en esta pagina; la del
# directorio, que vivio aparte unas horas, redirige aqui con su ?nivel=, su
# ?q= y su #ente= (apartados.REDIRECCIONES).
PAGINA = 'herramienta-inspector-entes.html'


def _banda():
    """La imagen del encabezado del Estado de Cuenta (apartados.py la busca
    igual): la ficha tecnica de cada expediente la repite (21-10-2026)."""
    for x in ('svg', 'png', 'jpg', 'jpeg', 'webp'):
        if os.path.exists(os.path.join(RAIZ, 'assets', 'auditor', 'img', 'encabezado-estado-de-cuenta.' + x)):
            return ' data-cabecera="assets/auditor/img/encabezado-estado-de-cuenta.%s"' % x
    return ''


def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def chip(e, pend=None):
    e = e if e in ('oficial', 'pendiente') else 'derivado'
    return '<span class="est-chip est-%s"%s>%s</span>' % (e, (' data-pend="%s"' % pend) if pend else '', e)


def _num(x):
    """formatNumber del motor: toLocaleString('es-MX') sin opciones
    (hasta tres decimales, sin ceros a la derecha)."""
    t = _loc(x, 3)
    return t.rstrip('0').rstrip('.') if '.' in t else t


def sim_mdp(n):
    """simMdp del motor."""
    a = abs(n)
    if a >= 1000000:
        return '$' + _fijo(n / 1000000, 2) + ' billones'
    if a >= 1000:
        return '$' + _num(round(n / 100) / 10) + ' mil millones'
    return '$' + _num(round(n * 100) / 100) + ' millones'


def _asf_resumen(f, cp):
    """inspFedAsf del motor: lo que la Matriz de la ASF registra para el
    ente. Sin el grupo «Gasto Federalizado» (ahi «Salud» es dinero que
    ejercen los estados, no la secretaria)."""
    if isinstance(f.get('asf'), list):
        if not f['asf']:
            return None
        s = {'auditorias': len(f['asf']), 'acciones': 0, 'PO': 0, 'recuperaciones': 0, 'porAclarar': 0,
             'grupos': [], 'propias': True}
        for a in f['asf']:
            s['acciones'] += a['acc'][6]
            s['PO'] += a['acc'][5]
            s['recuperaciones'] += a['recuperaciones']
            s['porAclarar'] += a['porAclarar']
            s['grupos'].append('auditoría %s, «%s» (%s)' % (a['num'], a['titulo'], a['tipo']))
        return s
    if not cp or not f.get('asfSectores'):
        return None
    s = {'auditorias': 0, 'acciones': 0, 'PO': 0, 'recuperaciones': 0, 'porAclarar': 0, 'grupos': []}
    for g in cp['grupos']:
        if re.search('federalizado', g['grupo'], re.I):
            continue
        for x in g['sectores']:
            if x['nombre'] not in f['asfSectores']:
                continue
            for k in ('auditorias', 'acciones', 'PO', 'recuperaciones', 'porAclarar'):
                s[k] += x.get(k) or 0
            s['grupos'].append('%s (%s)' % (g['grupo'], x['auditorias']))
    return s if (s['auditorias'] or s['grupos']) else None


def _refs_usadas(base):
    """Referencias que la pagina puede citar: las de las fuentes del
    inspector, las del padron municipal y las que el motor cita a mano."""
    ids = {'ref-asf-mdb2024', 'ref-scjn-ejercicio2026', 'ref-lfrcf'}
    for col in ('inspector_federal', 'inspector_estatal', 'inspector_poderes'):
        for v in (base.get(col) or {}).get('fuentes', {}).values():
            if isinstance(v, dict):
                if v.get('ref'):
                    ids.add(v['ref'])
                else:
                    ids.update(x for x in v.values() if isinstance(x, str) and x.startswith('ref-'))
    for v in base['fiscalEntidades']['campos'].values():
        if isinstance(v, dict) and v.get('ref'):
            ids.add(v['ref'])
    try:
        rend = open(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'municipios-rendicion.js'), encoding='utf-8').read()
        ids.update(re.findall(r'"ref": *"(ref-[a-z0-9-]+)"', rend))
    except OSError:
        pass
    out = {}
    for r in base['referencias_legales']:
        if r['id'] in ids:
            out[r['id']] = [r['num'], re.sub('<[^>]+>', '', r['cita_apa'])[:160], r.get('url') or '']
    return out


def _catalogo_municipal():
    try:
        t = open(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'municipios-efipem.js'), encoding='utf-8').read(4000)
        return int(re.search(r'catalogo:\s*(\d+)', t).group(1))
    except (OSError, AttributeError):
        return None


def datos(base):
    F = base['inspector_federal']
    P = base.get('inspector_poderes') or {}
    I = base.get('inspector_estatal') or {}
    L = (base.get('poderes') or {}).get('legislativo') or {}
    cp = (base.get('cuenta_publica_asf') or {}).get('cp2024')
    fichas = {x['id']: x for x in (base.get('expedientes') or {}).get('fichas', [])}
    poder_de = P.get('poderDeEnte') or {}
    organos = P.get('organos') or []

    def fila(f, poder):
        r = {k: f[k] for k in ('id', 'ramo', 'nombre', 'icono', 'tipo', 'cp2025') if k in f}
        r['poder'] = poder
        for k in ('padre', 'nota', 'av2026', 'cp2024', 'asfNoAplica', 'cotejos'):
            if f.get(k):
                r[k] = f[k]
        if f.get('cp2025', {}).get('capitulosSobreModificado'):
            r['cp2025'] = dict(f['cp2025'])
        if isinstance(f.get('asf'), list) and f['asf']:
            r['asf'] = f['asf']
        r['asfS'] = _asf_resumen(f, cp)
        r['exps'] = [[i, fichas[i]['icono'], fichas[i]['titulo']] for i in (f.get('expedientes') or []) if i in fichas]
        return r

    fed = []
    for f in F['entes']:
        fed.append(fila(f, poder_de.get(f['id'], 'ejecutivo')))
        fed.extend(fila(o, o['poder']) for o in organos if o.get('padre') == f['id'])

    congresos = L.get('congresos2024') or []
    jud = P.get('judicialesEstatales2024') or {}
    asfc = L.get('asfCongresos2024') or []
    est = []
    for e in base['estados']:
        r = {k: e.get(k) for k in ('abbr', 'name', 'dep', 'gasto', 'pc', 'deuda', 'asfMontoObservado', 'asfAuditorias',
                                   'semaforoDeuda', 'deudaIld', 'deudaFuente', 'asfTipologia', 'recaudacionPropia',
                                   'pob', 'pobPersonas', 'gobernador', 'partido', 'capital', 'asfFuente')}
        r['x'] = (I.get('entidades') or {}).get(e['abbr'])
        c = next((x for x in congresos if x['entidad'] == e['name']), None)
        r['cong'] = c['ejercidoMdp'] if c else None
        r['jud'] = jud.get(e['abbr'])
        a = [x for x in asfc if x['congreso'] == 'Congreso de ' + e['name']]
        if a:
            r['asfC'] = [[x['auditoria'], x['concepto'], x['pesos']] for x in a]
        est.append(r)

    fe = {}
    for k in ('dep', 'pob', 'pc', 'recaudacionPropia', 'gasto'):
        c = base['fiscalEntidades']['campos'].get(k) or {}
        fe[k] = {x: c.get(x) for x in ('estado', 'fuente', 'sinFuente', 'motivo', 'ref') if c.get(x)}

    pj = (base.get('poderes') or {}).get('judicial') or {}
    return {
        'pesos': PESOS, 'uf': UF, 'ul': UL,
        'poderes': {k: list(v) for k, v in PODERES.items()},
        'refs': _refs_usadas(base),
        'fF': F['fuentes'], 'fP': P.get('fuentes') or {}, 'fE': I.get('fuentes') or {},
        'fed': fed, 'est': est, 'fe': fe,
        'congresos': [x['ejercidoMdp'] for x in congresos],
        'juds': list(jud.values()),
        'scjnAgo': pj.get('scjnAgosto'),
        'cdmx': CDMX_AVISO,
        'mun': {'n': _catalogo_municipal(), 'src': MUN_ARCHIVOS},
    }


def _tarjeta_fed(f):
    """La tarjeta del directorio, ya escrita (la misma que pinta el guion,
    sin el semaforo, que se calcula al abrir)."""
    poder = PODERES[f['poder']][0]
    return ('<li><a class="ie-tarj" href="#ente=federal:%s">'
            '<span class="ie-tarj-ico" aria-hidden="true">%s</span>'
            '<span class="ie-tarj-tx"><b>%s</b><small>%s · Ramo %s · %s</small>'
            '<small class="ie-tarj-cifra">Ejerció %s en 2025 %s</small></span>'
            '<span class="ie-tarj-ir" aria-hidden="true">›</span></a></li>'
            % (esc(f['id']), f['icono'], esc(f['nombre']), esc(f['tipo']), esc(f['ramo']), poder,
               sim_mdp(f['cp2025']['ejercido']), chip('oficial')))


def _paginas(base, ref):
    D = datos(base)
    nfed, nest, nmun = len(D['fed']), len(D['est']), D['mun']['n']
    norg = sum(1 for f in D['fed'] if f.get('padre'))
    F = base['inspector_federal']['fuentes']
    fe = D['fe']

    niveles = [
        ('federal', '🇲🇽', 'Federal', nfed, 'Los tres poderes, los autónomos y las empresas del Estado'),
        ('estatal', '🗺️', 'Estatal', nest, 'Las 32 entidades federativas'),
        ('municipal', '🏙️', 'Municipal', nmun, 'Los municipios y alcaldías del catálogo del INEGI'),
    ]
    pest = '\n'.join(
        '          <button type="button" class="ie-nivel%s" role="tab" id="ieTab-%s" aria-controls="ieDir" aria-selected="%s" data-nivel="%s">'
        '<span class="ie-nivel-ico" aria-hidden="true">%s</span><span class="ie-nivel-tx"><b>%s</b><small>%s</small></span>'
        '<span class="ie-nivel-n" data-n="%s">%s</span></button>'
        % (' activo' if k == 'federal' else '', k, 'true' if k == 'federal' else 'false', k, ico, et, d, k,
           _num(n) if n else '—')
        for k, ico, et, n, d in niveles)

    tarjetas = '\n'.join(_tarjeta_fed(f) for f in D['fed'])

    p = PESOS
    metodo = '''<section class="ie-sec ie-metodo" id="ie-metodo" aria-labelledby="ieMetTit">
        <h2 class="ie-tit" id="ieMetTit"><span aria-hidden="true">🧭</span> Cómo se lee un expediente, sin caja negra</h2>
        <p class="ie-txt">Cada expediente responde, con documentos oficiales, las mismas preguntas que cualquiera puede hacerle a una autoridad. Los <b>datos son oficiales</b>; los <b>umbrales de los semáforos y el índice son de Auditavisión</b> y se pueden discutir. Una señal no es una acusación: es algo que la autoridad debe explicar.</p>
        <ul class="ie-sem-ley" aria-label="Qué significa cada color">
          <li><span class="ie-pt s-ok" aria-hidden="true"></span><b>Sin señal</b> el documento no muestra nada que explicar.</li>
          <li><span class="ie-pt s-alerta" aria-hidden="true"></span><b>Señal a revisar</b> hay algo que la autoridad debe aclarar.</li>
          <li><span class="ie-pt s-grave" aria-hidden="true"></span><b>Señal fuerte</b> la diferencia es grande frente a su tamaño.</li>
          <li><span class="ie-pt s-sin" aria-hidden="true"></span><b>Sin dato</b> no hay documento con qué responder; no se supone.</li>
        </ul>
        <details class="ie-det" id="ie-metodo-fed">
          <summary><span aria-hidden="true">🇲🇽</span> Federal: cuándo se enciende cada semáforo</summary>
          <div class="ie-det-c">
            <p><b>¿Gastó lo que aprobó la Cámara?</b> Ejercido ÷ aprobado − 1; naranja si pasa de ±{da} %, rojo si pasa de ±{dg} %. Si la Cámara no le aprobó nada (el ente no existía al votarse el presupuesto), naranja: el dinero le llegó por adecuaciones de Hacienda (Ley Federal de Presupuesto, art. 58).</p>
            <p><b>¿Rindió cuentas?</b> Naranja si falta su avance de 2026 o si la Matriz de la ASF no tiene un sector a su nombre.</p>
            <p><b>¿Cuadran sus propias cifras?</b> Rojo si lo ejercido rebasa lo modificado; naranja si más de {pa} % de lo ejercido no figura como pagado, o si en 2026 lleva menos de {rb} % o más de {ra} % de su calendario a junio (columna MONTO_MODIFICADO_MENSUAL de la base de Hacienda, que suma el 52.7 % del modificado anual). Cuando dos documentos oficiales de emisores distintos (Hacienda, el INEGI, el propio órgano) hablan del mismo dinero, naranja si difieren en más de lo que explica el redondeo.</p>
            <p><b>¿Qué encontró la Auditoría Superior?</b> Verde si no quedó nada por aclarar ni pliegos; rojo si hay pliegos y $100 mdp o más por aclarar; naranja en otro caso.</p>
            <p>Una secretaría, una empresa del Estado y un poder autónomo no se miden con la misma regla: por eso el nivel federal <b>no lleva círculo</b> de salud financiera.</p>
          </div>
        </details>
        <details class="ie-det" id="ie-metodo-local">
          <summary><span aria-hidden="true">⭕</span> Estados y municipios: el círculo de salud financiera</summary>
          <div class="ie-det-c">
            <p><b>Índice = autonomía × {pa_}% + limpieza × {po}% + holgura (estados) o esfuerzo recaudatorio (municipios) × {ph}%.</b></p>
            <p><b>autonomía</b> = 100 − dependencia de transferencias. <b>limpieza</b> = 100 − (observado ÷ Ramos 28 y 33, o ÷ ingreso en municipios, × 100) × 20. <b>holgura</b> (estados) = 100 − (deuda ÷ Ramos 28 y 33 × 100) × 2. <b>esfuerzo</b> (municipios) = (predial ÷ ingreso × 100) × 4: no hay dato oficial de deuda municipio por municipio, así que se mide el esfuerzo propio en su lugar. Los tres se recortan al rango 0–100.</p>
            <p>En municipios el círculo necesita tres insumos oficiales del mismo año: la cuenta 2024 ante el INEGI y la auditoría integral de la ASF a la Cuenta Pública 2024. <b>Si falta uno, no se dibuja</b>: no se completa con supuestos.</p>
            <p>Veredicto: 75 o más, sólida · 55 a 74, aceptable · 40 a 54, frágil · 25 a 39, comprometida · menos de 25, crítica.</p>
            <p><b>De qué vive</b>: naranja si más de {dep} % de su ingreso vino de transferencias; nunca rojo, porque depender no es una irregularidad. <b>Cuadre estatal</b>: lo que el estado reportó al INEGI contra lo que la Cuenta Pública registra como pagado; naranja desde ±{eca} %, rojo desde ±{ecg} %. <b>ASF estatal</b>: rojo si lo por aclarar llega al {agp} % de sus Ramos 28 y 33. <b>Deuda</b>: el color del Sistema de Alertas de Hacienda, tal cual.</p>
            <p><b>Cuentas municipales</b>: rojo si no entregó su cuenta de 2024 al INEGI ni informó a Hacienda; naranja si faltó a uno de los dos, o a dos o más años de la serie. <b>Cuadre municipal</b>: lo declarado al INEGI contra lo que informó a Hacienda haber recibido, fondo por fondo; naranja desde ±{mca} %, rojo desde ±{mcg} % (se ignoran diferencias menores a $1 millones). <b>ASF municipal</b>: naranja si quedó algo por aclarar o acciones pendientes; rojo si lo por aclarar llega a $50 millones o al {mgp} % de su ingreso.</p>
            <p><em>Esto es una construcción de Auditavisión para hacer comparables cifras oficiales sueltas. No es una calificación crediticia, ni una sanción, ni un dictamen de la Auditoría Superior.</em></p>
          </div>
        </details>
      </section>'''.format(da=UF['desvioAlerta'], dg=UF['desvioGrave'], pa=UF['pagoAlerta'], rb=UF['ritmoBajo'], ra=UF['ritmoAlto'],
                           pa_=p['autonomia'], po=p['observado'], ph=p['holgura'], dep=UL['depAlerta'],
                           eca=UL['estCuadreAlerta'], ecg=UL['estCuadreGrave'], agp=UL['asfGravePct'],
                           mca=UL['munCuadreAlerta'], mcg=UL['munCuadreGrave'], mgp=UL['munAsfGravePct'])

    def fu(texto, rid, url=None):
        return '<li>%s%s%s</li>' % (esc(texto), ref(rid) if rid else '',
                                     (' <a href="%s" target="_blank" rel="noopener">documento ↗</a>' % esc(url)) if url else '')
    fe_ = base['inspector_estatal']['fuentes']
    fuentes = '\n'.join([
        fu(F['cp2025']['corto'], F['cp2025']['ref'], F['cp2025'].get('url')),
        fu(F['av2026']['corto'] + ' (corte: ' + F['av2026'].get('corte', '') + ')', F['av2026']['ref'], F['av2026'].get('url')),
        fu(F['asf2024']['corto'], F['asf2024']['ref']),
        fu(fe_['cp2024']['corto'], fe_['cp2024']['ref'], fe_['cp2024'].get('url')),
        fu(fe_['inegi2024']['corto'], fe_['inegi2024']['ref']),
        fu('INEGI, EFIPEM municipal 2016-2025; SHCP, Sistema de Recursos Federales Transferidos 2024; INAFED, presidencias municipales', 'ref-inegi-efipem'),
        fu('INEGI, censos nacionales de poderes legislativos y judiciales estatales 2025', 'ref-inegi-cnple2025'),
        fu('SHCP, Sistema de Alertas de deuda de entidades federativas', None),
    ])

    args = dict(datos=_json(D), banda=_banda(),
        nfed=_num(nfed), nraiz=nfed - norg, norg=norg, nest=nest, nmun=_num(nmun) if nmun else 'los',
        pest=pest, tarjetas=tarjetas, metodo=metodo, fuentes=fuentes,
        fgasto=esc(fe['gasto'].get('fuente', '')), rgasto=ref(fe['gasto']['ref']) if fe['gasto'].get('ref') else '', pag=PAGINA)
    cajon = _cajon(metodo, fuentes, args)
    args['cajon'] = cajon
    return {'principal': """<div class="ie" id="ie" data-auditor="{pag}">
      <script type="application/json" id="ieDatos">{datos}</script>

      <div class="ie-ver" id="ieVer" aria-live="polite" hidden></div>

      <section class="ie-arranque" aria-labelledby="ieArrTit">
        <p class="ie-kicker">Busca y verifica</p>
        <h2 class="ie-grande" id="ieArrTit">¿De quién quieres ver las cuentas?</h2>
        <p class="ie-txt">Un solo navegador para los tres niveles de gobierno: elige el nivel, escribe un nombre o filtra la lista. Cada ente abre su <b>ficha técnica de Auditavisión</b>.</p>
        <div class="ie-niveles" role="tablist" aria-label="Nivel de gobierno">
{pest}
        </div>
        <div class="ie-busca" role="search">
          <label class="ie-busca-et" for="ieQ">Busca por nombre: dependencia, ramo, estado, municipio o quien lo gobierna</label>
          <div class="ie-busca-caja">
            <span class="ie-busca-lupa" aria-hidden="true">🔎</span>
            <input id="ieQ" class="ie-busca-in" type="search" autocomplete="off" spellcheck="false"
              placeholder="Ej.: Salud, Pemex, Jalisco, Ecatepec…" role="combobox" aria-expanded="false" aria-autocomplete="list" aria-controls="ieSug">
            <button type="button" class="ie-busca-x" id="ieQx" aria-label="Borrar la búsqueda" hidden>✕</button>
          </div>
          <ul class="ie-sug" id="ieSug" role="listbox" aria-label="Sugerencias" hidden></ul>
          <p class="ie-busca-nota" id="ieQnota" aria-live="polite">Los municipios se cargan al buscar o al abrir su nivel (son {nmun}; tarda un instante).</p>
        </div>
        <ol class="ie-pasos">
          <li><b>1</b> Elige el nivel o escribe un nombre.</li>
          <li><b>2</b> Filtra y ordena la lista.</li>
          <li><b>3</b> Abre su ficha técnica: semáforos, cifras y documentos.</li>
          <li><b>4</b> Descárgala en PDF, cópiala o comparte el enlace.</li>
        </ol>
        <p class="ie-salva">⚖️ <b>Una señal no es una acusación</b>: es algo que la autoridad debe explicar. Y <b>«por aclarar» no es «robado»</b>: es dinero cuyo destino no quedó acreditado ante la Auditoría Superior.</p>
      </section>

{cajon}

      <section class="ie-exp" id="ieExp" aria-label="Ficha técnica abierta"{banda} hidden></section>

      <section class="ie-sec ie-dir" id="ie-dir" aria-labelledby="ieDirTit">
        <h2 class="ie-tit" id="ieDirTit"><span aria-hidden="true">🗂️</span> El directorio</h2>
        <div class="ie-dir-ctl" id="ieCtl"></div>
        <div id="ieDir" role="tabpanel" aria-labelledby="ieTab-federal">
          <p class="ie-conteo" id="ieConteo">{nfed} entes federales. Pulsa uno para abrir su ficha técnica.</p>
          <ul class="ie-tarjetas" id="ieLista">
{tarjetas}
          </ul>
          <div id="ieMas"></div>
        </div>
      </section>

      <nav class="ie-sec ie-hermanas" aria-label="Para seguir el hilo">
        <h2 class="ie-tit"><span aria-hidden="true">🧵</span> Para seguir el hilo</h2>
        <div class="ie-herm">
          <a href="herramienta-inspector-asf.html"><span aria-hidden="true">🏛️</span><b>Qué encontró la ASF</b><small>La Cuenta Pública 2024, sector por sector</small></a>
          <a href="herramienta-inspector-radar.html"><span aria-hidden="true">🚩</span><b>Radar por entidad</b><small>Los 32 estados, lado a lado</small></a>
          <a href="expedientes.html"><span aria-hidden="true">📂</span><b>Expedientes de casos</b><small>Informe por informe de la ASF</small></a>
          <a href="numeros-las-32-entidades.html"><span aria-hidden="true">🗺️</span><b>Las 32 entidades</b><small>Cuánto recibe cada estado</small></a>
          <a href="numeros-los-municipios.html"><span aria-hidden="true">🏙️</span><b>Los municipios</b><small>El padrón del INEGI con sus cifras</small></a>
          <a href="numeros-lo-que-cuestan-los-poderes.html"><span aria-hidden="true">⚖️</span><b>Lo que cuestan los Poderes</b><small>Congreso, Corte y autónomos</small></a>
        </div>
      </nav>
      <div class="ie-aviso" id="ieAviso" role="status" aria-live="polite"></div>
    </div>""".format(**args)}


def _cajon(metodo, fuentes, args):
    """Como se lee un expediente y de donde sale cada cifra: un boton que
    abre la ventana lateral de la plataforma, como el de Contrasta una nota
    (pedido del autor, 21-10-2026: un solo navegador arriba, el metodo a un
    clic). Con #ie-metodo en la direccion se abre al cargar; los enlaces
    #ie-metodo-fed y #ie-metodo-local de la ficha lo abren en su apartado."""
    cuerpo = ('<div class="ie ie-cajon">' + metodo +
              '<section class="ie-sec" aria-labelledby="ieFuTit"><h2 class="ie-tit" id="ieFuTit"><span aria-hidden="true">🔗</span> De dónde sale cada cifra</h2>'
              '<ul class="ie-fuentes">' + fuentes + '</ul>'
              '<p class="ie-nota-p">Los datos del Ramo 28 y 33 por entidad: ' + args['fgasto'] + args['rgasto'] + '. Cada ficha repite sus fuentes al pie, con su llamada a la lista de '
              '<a href="fuentes-oficiales.html">fuentes oficiales</a>. Lo que no tiene documento está en el <a href="pendientes.html">Registro de pendientes</a>, '
              'con el nombre de quien debe publicarlo.</p></section></div>')
    tpl = ('<template id="tplIeComo"><header class="glos-drawer-cab"><span class="glos-drawer-marca"><span aria-hidden="true">📖</span> Auditor de entes públicos</span>'
           '<button type="button" class="glos-drawer-x" aria-label="Cerrar">✕</button></header><div class="glos-drawer-cuerpo">'
           '<span class="glos-drawer-cat">Ficha técnica · Método y fuentes</span>'
           '<h3 id="ieComoTit" class="glos-drawer-tit">Cómo se lee una ficha técnica y de dónde sale cada cifra</h3>%s</div></template>' % cuerpo)
    return ('      <p class="ie-como"><button type="button" class="ie-cajon-btn" id="ieComoBtn" data-cajon="tplIeComo" data-cajon-hash="ie-metodo" '
            'data-cajon-tit="ieComoTit" aria-haspopup="dialog"><span aria-hidden="true">📖</span> Cómo se lee una ficha técnica y de dónde sale cada cifra '
            '<span aria-hidden="true">›</span></button></p>\n      ' + tpl)


def construir(base, ref):
    return _paginas(base, ref)['principal']
