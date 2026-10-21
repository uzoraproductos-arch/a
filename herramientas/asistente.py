# -*- coding: utf-8 -*-
"""«Pregúntale al Auditor»: el bot interno de Auditavision (pedido del autor,
11-10-2026). Vive en el Modo Inspector, aparte de las seis aplicaciones de
«Grandes investigaciones».

Es un bot interno, no una IA generativa: no redacta cifras. Cada respuesta
sale de una ficha que ya esta publicada y verificada en la plataforma
(glosario, expedientes, entidades, fuentes oficiales, pendientes y las
paginas mismas). Si la pregunta no tiene ficha, el bot lo dice: inventar una
respuesta es inventar un dato (AGENTS.md, §2).

Este modulo escribe dos cosas:
  - assets/auditor/js/asistente-base.js: la base de fichas
    (window.AUDITOR_BASE), armada desde window.AUDIT_DB, el Registro de
    pendientes y las paginas generadas;
  - el bloque de la pagina (el chat), que apartados.generar() monta con
    herramienta_modulo.
La busqueda y la nota tecnica sellada viven en assets/auditor/js/asistente.js.
"""
import glob
import html
import json
import os
import re

from apartados import RAIZ, glosario_ancla

ARCHIVO = 'herramienta-inspector-pregunta.html'
ASF_INFORMES = 'https://www.asf.gob.mx/Section/58_Informes_de_auditoria'
ALERTAS = 'https://www.disciplinafinanciera.hacienda.gob.mx/'
BASE_JS = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'asistente-base.js')


def limpio(t):
    return html.unescape(re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', str(t or '')))).strip()


def _fichas(d):
    out = []

    # 1. El glosario (246 terminos, cada uno con su ley).
    for g in d['glosario']:
        out.append({'t': 'glosario', 'tit': limpio(g['termino']), 'txt': limpio(g['definicion']),
                    'fu': [{'tx': limpio(g['ley'])}] if g.get('ley') else [],
                    'ir': ['glosario.html#' + glosario_ancla(g['termino']), 'Glosario'],
                    'k': limpio(g.get('categoria'))})

    # 2. Los expedientes de casos por aclarar (cifras con su estado).
    for f in d['expedientes']['fichas']:
        out.append({'t': 'expediente', 'tit': limpio(f['titulo']), 'txt': limpio(f['hallazgo']),
                    'ci': [{'v': c['valor'], 'etq': c['etq'], 'e': c['estado']} for c in f.get('cifras', [])],
                    'fu': [{'tx': limpio(f['fuente']), 'url': ASF_INFORMES}], 'nota': limpio(f.get('alcance')),
                    'ir': ['expedientes.html#exp-' + f['id'], 'Expedientes de casos de la ASF'],
                    'k': limpio(f.get('ente')) + ' ' + f['id'].replace('-', ' ')})

    # 3. Las 32 entidades: deuda (SHCP), lo que la ASF dejo por aclarar y su
    # radar (21-10-2026): por cada $100 revisados y su lugar entre los 32.
    import insp_radar
    rad = insp_radar.datos(d['cuenta_publica_asf'])
    for e in d['estados']:
        ci, fu = [], []
        if e.get('deuda') is not None and e.get('deudaFuente'):
            ci.append({'v': '$' + format(e['deuda'], ',.1f') + ' mdp', 'etq': 'deuda pública', 'e': 'oficial'})
            if e.get('deudaIld') is not None:
                ci.append({'v': format(e['deudaIld'], '.1f') + '%', 'etq': 'deuda entre ingresos de libre disposición', 'e': 'oficial'})
            if e.get('semaforoDeuda'):
                ci.append({'v': e['semaforoDeuda'], 'etq': 'semáforo del Sistema de Alertas', 'e': 'oficial'})
            fu.append({'tx': limpio(e['deudaFuente']), 'url': ALERTAS})
        if e.get('asfMontoObservado') is not None and e.get('asfFuente'):
            ci.append({'v': '$' + format(e['asfMontoObservado'], ',.1f') + ' mdp', 'etq': 'por aclarar ante la ASF (Cuenta Pública 2024)', 'e': 'oficial'})
            if e.get('asfAuditorias') is not None:
                ci.append({'v': str(e['asfAuditorias']), 'etq': 'auditorías de la ASF', 'e': 'oficial'})
            fu.append({'tx': limpio(e['asfFuente']), 'url': d['cuenta_publica_asf']['fuentes']['MDB2024']['url']})
        r = rad['est'].get(e['abbr'])
        if r:
            ci.append({'v': '$%.2f de cada $100 revisados (lugar %d de 32; promedio nacional $%.2f)' % (r['v'][0], r['l'][0], rad['prom']),
                       'etq': 'por aclarar en proporción a lo auditado: %s' % rad['sem'][r['s']][1].lower(), 'e': 'derivado'})
        if not ci:
            continue
        out.append({'t': 'entidad', 'tit': e['name'],
                    'txt': ('Lo que la plataforma tiene verificado de %s: su deuda pública según el Sistema de Alertas de Hacienda, '
                            'lo que la Auditoría Superior dejó por aclarar del dinero federal que recibió en 2024 y su lugar en el radar de los 32 estados. '
                            'Un monto por aclarar no es un desfalco comprobado: es lo que carecía de documentación al cierre de la auditoría.') % e['name'],
                    'ci': ci, 'fu': fu, 'ir': ['herramienta-inspector-entes.html#ente=estatal:' + e['abbr'], 'el Auditor de entes públicos'],
                    'k': '%s %s estado entidad deuda asf radar bandera roja ficha tecnica' % (e['abbr'], e.get('capital', ''))})

    # 4. Lo que gana cada cargo (Tu contra ellos): neto mensual y anual, con
    #    su estado; el derivado dice su operacion.
    cs = d['comparador_salarial']
    for c in cs['cargos']:
        m = c['mensual']
        mens = ('$' + format(m['max'], ',.2f').replace('.00', '') if m.get('min') in (None, m['max']) else
                'de $%s a $%s' % (format(m['min'], ',.2f').replace('.00', ''), format(m['max'], ',.2f').replace('.00', '')))
        ci = [{'v': mens, 'etq': 'al mes · ' + limpio(c['mensualConcepto']), 'e': c['mensualEstado']},
              {'v': '$' + format(c['anual'], ',.2f').replace('.00', ''), 'etq': 'al año · ' + limpio(c.get('anualConcepto') or 'remuneración neta anual'),
               'e': c['anualEstado'], 'op': limpio(c.get('anualOperacion'))}]
        fx = cs['fuentes'].get(c['fuente'], {})
        out.append({'t': 'cargo', 'tit': 'Cuánto gana: ' + c['cargo'], 'txt': limpio(c.get('detalle')) + '. ' + limpio(c.get('nota')),
                    'ci': ci, 'fu': [{'tx': limpio(fx.get('corto', c['fuente'])) + ' · ' + limpio(c.get('pagina')), 'url': fx.get('url')}],
                    'ir': ['herramienta-calculadora-compara.html', 'Tú contra ellos'],
                    'k': 'sueldo salario gana remuneracion ' + c['id'].replace('_', ' ') + ' ' + c['grupo']})

    # 6. Quien fiscaliza (21-10-2026): las diez autoridades de «Expedientes de
    # casos de la ASF», con su fundamento y su expediente oficial.
    import fiscalizadores as fz
    for a in fz.AUTORIDADES:
        clave, grupo, ico, nom, fund, que, exp, url, rid, integ, plat = a
        g = next(x for x in fz.GRUPOS if x[0] == grupo)
        out.append({'t': 'autoridad', 'tit': nom, 'txt': '%s Su expediente oficial: %s En Auditavisión: %s' % (que, exp, limpio(plat)),
                    'fu': [{'tx': fund + (' · portal oficial' if url else ''), 'url': url}],
                    'nota': limpio(plat),
                    'ir': ['herramienta-inspector-asf-autoridades.html#fz-' + clave, 'Quién fiscaliza'],
                    'k': '%s %s fiscaliza fiscalizacion autoridad sanciona investiga corrupcion %s' % (g[2], limpio(g[3]), fund)})

    # 7. El seguimiento de 2024 a 2027: lo que vio el agente en su ultima vuelta.
    rep = fz.reporte() or {}
    hoy = rep.get('fecha') or ''
    for cp in (2024, 2025, 2026, 2027):
        filas = []
        for e in (x for x in fz.ENTREGAS if x[1] == cp):
            st = fz.estado_entrega(e, rep.get('entregas', {}), hoy) if hoy else 'esperada'
            filas.append('%s (%s): %s' % (e[3], fz.fecha(e[4]), fz.ESTADOS[st][2].lower()))
        out.append({'t': 'entrega', 'tit': 'Cuenta Pública %d: el seguimiento de su fiscalización' % cp,
                    'txt': '. '.join(filas) + '.' + ((' Lo revisó el agente de seguimiento el %s; las cifras de una entrega nueva entran a la plataforma solo al extraerlas de su documento oficial.' % fz.fecha(hoy)) if hoy else ''),
                    'fu': [{'tx': 'LFRCF, art. 35, y CPEUM, art. 74, fr. VI', 'url': None}],
                    'nota': ('Revisado por el agente de seguimiento el %s.' % fz.fecha(hoy)) if hoy else '',
                    'ir': ['herramienta-inspector-asf-calendario.html#ia-seguimiento', 'El seguimiento 2024–2027'],
                    'k': 'cuenta publica %d entrega entregas asf informe calendario seguimiento agente' % cp})
    prox = next((e for e in fz.ENTREGAS if e[4] > (hoy or '0') and e[6]), None)
    if prox:
        out.append({'t': 'entrega', 'tit': 'La próxima entrega de la Auditoría Superior',
                    'txt': ('La próxima es la %s de la Cuenta Pública %d: la ley la fija para el %s. En cuanto aparezca, el agente de seguimiento la marca '
                            'y sus cifras entran a la plataforma al extraerlas de su documento oficial.') % (prox[3][0].lower() + prox[3][1:], prox[1], fz.fecha(prox[4])),
                    'fu': [{'tx': prox[5], 'url': None}],
                    'ir': ['herramienta-inspector-asf-calendario.html#ia-seguimiento', 'El seguimiento 2024–2027'],
                    'k': 'proxima siguiente cuando sale saldra publica entrega asf auditoria superior informe fecha'})

    # 8. Los estados de cuenta que expide la plataforma (pedido del autor,
    # 21-10-2026: «el bot debe identificar cualquier dato que obre en su
    # contenido»): de cada administracion, de 1989 a la fecha, y de cada
    # cargo (diputaciones, Senado, Suprema Corte). Las cifras salen del mismo
    # JSON con que radar-estado-de-cuenta.html los expide, ya generado.
    out += _estados_de_cuenta()

    # 9. Las fichas tecnicas del Auditor de entes publicos: cada ente federal
    # y cada municipio (los estados ya estan en el punto 3).
    fichas, _ = _fichas_tecnicas(d)
    out += fichas

    # 10. El catalogo de cifras oficiales (Contrasta una nota): cada cifra,
    # con su documento.
    import insp_nota
    for c in insp_nota.catalogo(d):
        if c.get('v') is None:
            continue
        out.append({'t': 'cifra', 'tit': limpio(c['n']), 'txt': 'Cifra del catálogo de cifras oficiales de Auditavisión (%s).' % c['a'],
                    'ci': [{'v': '$' + format(c['v'], ',.1f') + ' mdp', 'etq': limpio(c['n']), 'e': c['e']}],
                    'fu': [{'tx': limpio(c['f']), 'url': c.get('u')}],
                    'ir': [insp_nota.CATALOGO, 'Catálogo de cifras oficiales'],
                    'k': '%s %s cifra dato monto' % (c['g'], c['a'])})

    # 5. Las fuentes oficiales (leyes, informes, decretos).
    for r in d['referencias_legales']:
        out.append({'t': 'fuente', 'tit': limpio(r['cita_apa'])[:180], 'txt': limpio(r.get('descripcion')),
                    'fu': [{'tx': limpio(r['cita_apa']), 'url': r.get('url')}],
                    'ir': ['fuentes-oficiales.html#' + r['id'], 'Fuentes oficiales · [%02d]' % r['num']],
                    'k': limpio(r.get('categoria_nombre'))})
    return out


EXPIDE = 'radar-estado-de-cuenta.html'


def _num_ec(v, u):
    """Una cifra de un estado de cuenta, en su unidad."""
    if u in ('$', '$g'):
        return '$' + (format(v, ',.0f') if abs(v) >= 1000 else format(v, ',.2f'))
    if u == 'mdp':
        return '$' + format(v, ',.1f') + ' mdp'
    if u == 'pib':
        return format(v, '.1f') + ' % del PIB'
    if u == 'pp':
        return ('+' if v > 0 else '') + format(v, '.1f') + ' puntos del PIB'
    if u in ('pct100', 'pct'):
        return format(v, '.1f') + ' %'
    if u == 'ent':
        return format(v, ',.0f')
    return None


def _estados_de_cuenta():
    s = open(os.path.join(RAIZ, EXPIDE), encoding='utf-8').read()
    D = json.loads(re.search(r'id="rdDatos">(.*?)</script>', s, re.S).group(1))
    C = json.loads(re.search(r'id="exCargos">(.*?)</script>', s, re.S).group(1))
    out = []
    claves = ['ingresos_pib', 'gasto_pib', 'inversion_pib', 'costo_financiero_pib', 'deuda_ini', 'deuda_fin', 'deuda_cambio',
              'asf_aud', 'asf_acl', 'asf_rec']
    for a in D['admins']:
        V = D['valores'].get(a['id'], {})
        ci, fu = [], []
        for k in claves:
            x, m = V.get(k), D['metricas'].get(k)
            t = x and x.get('v') is not None and _num_ec(x['v'], m.get('u'))
            if not t:
                continue
            ci.append({'v': t, 'etq': m['tit'], 'e': x.get('est') or 'oficial'})
            for f in x.get('f') or []:
                g = D['fuentes'].get(f)
                if g and not any(z['tx'] == g['corto'] for z in fu):
                    fu.append({'tx': g['corto'], 'url': g.get('url')})
        out.append({'t': 'estado', 'tit': 'Estado de cuenta de la administración de %s (%d–%d)' % (a['n'], a['a'][0], a['a'][1]),
                    'txt': 'Las cuentas de la administración %s: lo que entró, lo que se gastó, la deuda que recibió y la que entregó, y lo que la ASF dejó por aclarar. %s%s'
                           % (a['periodo'], a.get('aviso') or '', ' Está en curso.' if a.get('curso') else ''),
                    'ci': ci, 'fu': fu[:6], 'ir': ['%s?adm=%s' % (EXPIDE, a['id']), 'Expide su estado de cuenta'],
                    'k': '%s %s %s presidente presidenta sexenio administracion gobierno estado de cuenta' % (a['c'], a['n'], a['ini'])})
    for d in C['docs']:
        ci, fu = [], []
        filas = [x['x'] for x in d.get('senales', [])] + [f for sec in d.get('secciones', []) for f in sec.get('filas', [])]
        for x in filas:
            t = x.get('v') is not None and _num_ec(x['v'], x.get('u'))
            if not t or len(ci) >= 8:
                continue
            ci.append({'v': t, 'etq': limpio(x.get('t')), 'e': x.get('est') or 'oficial'})
            g = C['fuentes'].get(x.get('f'))
            if g and not any(z['tx'] == g['corto'] for z in fu):
                fu.append({'tx': g['corto'], 'url': g.get('url')})
        out.append({'t': 'estado', 'tit': '%s: %s' % (d['tipoTx'], d['n']), 'txt': '%s. %s' % (limpio(d['sub']), limpio(d.get('aviso'))),
                    'ci': ci, 'fu': fu[:6], 'ir': ['%s?doc=%s' % (EXPIDE, d['id']), 'Expide su estado de cuenta'],
                    'k': '%s %s cargo sueldo gana remuneracion legislador estado de cuenta' % (d['id'].replace('-', ' '), limpio(d['n']))})
    return out


def _fichas_tecnicas(d):
    import insp_entes
    E = insp_entes.datos(d)
    F = d['inspector_federal']['fuentes']
    out = []
    for f in E['fed']:
        cp = f.get('cp2025') or {}
        ci = [{'v': '$' + format(cp[k], ',.1f') + ' mdp', 'etq': et, 'e': 'oficial'}
              for k, et in (('original', 'aprobado 2025'), ('ejercido', 'ejercido 2025'), ('pagado', 'pagado 2025')) if cp.get(k) is not None]
        out.append({'t': 'ficha', 'tit': limpio(f['nombre']),
                    'txt': '%s · Ramo %s. Su ficha técnica en el Auditor de entes públicos dice si gastó lo que aprobó la Cámara, si rindió cuentas y qué quedó por aclarar ante la ASF.'
                           % (limpio(f.get('tipo')), f.get('ramo')),
                    'ci': ci, 'fu': [{'tx': F['cp2025']['corto'], 'url': F['cp2025'].get('url')}],
                    'ir': ['herramienta-inspector-entes.html#ente=federal:' + f['id'], 'su ficha técnica'],
                    'k': '%s ramo %s %s ficha tecnica dependencia ente federal' % (f['id'], f.get('ramo'), f.get('poder', ''))})
    s = open(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'municipios-efipem.js'), encoding='utf-8').read()
    nombres = {e['abbr']: e['name'] for e in d['estados']}
    # Los 2,479 municipios van compactos ([clave, nombre, estado, ingresos
    # 2024 en mdp o None]); asistente.js arma su ficha al cargar.
    mun = []
    for m in re.finditer(r'"([A-ZÉ]+)": \{ cve: "(\d\d)".*?lista: \[(.*?)\] \}', s, re.S):
        ab, cve = m.group(1), m.group(2)
        for r in re.finditer(r'\["(\d{3})","([^"]+)"((?:,\d+)*)\]', m.group(3)):
            ing = r.group(3).split(',')[1] if r.group(3) else None
            mun.append([cve + r.group(1), r.group(2), nombres.get(ab, ab), round(int(ing) / 1e6, 1) if ing else None])
    return out, mun


def _pendientes():
    import pendientes
    out = []
    for x in pendientes.recolectar():
        out.append({'t': 'pendiente', 'tit': limpio(x['que']), 'txt': '',
                    'pend': {'pq': limpio(x['porque']), 'quien': x['responsable'], 'donde': x['enlace'], 'donde_tx': x['enlace_txt'], 'id': x['id']},
                    'ir': ['pendientes.html#' + x['id'], 'Registro de pendientes'],
                    'k': limpio(x['tema']) + ' falta pendiente'})
    return out


def _paginas():
    """Cada pagina de la plataforma, por su titulo y su descripcion: para las
    preguntas de «¿donde encuentro...?»."""
    out = []
    for p in sorted(glob.glob(os.path.join(RAIZ, '*.html'))):
        n = os.path.basename(p)
        if n in ('enciclopedia.html', ARCHIVO):
            continue
        s = open(p, encoding='utf-8').read()
        if 'http-equiv="refresh"' in s:
            continue
        t = re.search(r'<title>(.*?)</title>', s, re.S)
        m = re.search(r'<meta name="description" content="(.*?)"', s, re.S)
        if not t or not m:
            continue
        tit = limpio(t.group(1)).split(' · ')[0].split(' | ')[0]
        out.append({'t': 'pagina', 'tit': tit, 'txt': limpio(m.group(1)), 'ir': [n, tit], 'k': n[:-5].replace('-', ' ')})
        # Cada seccion con titulo propio: lleva al lugar exacto de la pagina.
        vistos = set()
        for h in re.finditer(r'<h([23])[^>]*\bid="([^"]+)"[^>]*>(.*?)</h\1>', s, re.S):
            # La ventana de «Cuéntanos lo que viste» (ids pt*) se repite en todas las paginas.
            if 'sr-only' in h.group(3) or h.group(2).startswith('pt'):
                continue
            ht = limpio(h.group(3))
            if len(ht) < 4 or ht in vistos or ht == tit:
                continue
            vistos.add(ht)
            resto = s[h.end():h.end() + 60000]
            sig = re.search(r'<h2[^>]*\bid="|<footer|class="herr-mod-nav|class="herr-otras', resto)
            cuerpo = limpio(re.sub(r'<(script|style|svg)[^>]*>.*?</\1>', ' ', resto[:sig.start()] if sig else resto, flags=re.S))[:6000]
            # Solo las palabras distintas: la busqueda no necesita el orden y la base pesa menos.
            unicas = []
            for w in re.findall(r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]{3,}', cuerpo):
                if w.lower() not in unicas:
                    unicas.append(w.lower())
            cuerpo = ' '.join(unicas)
            pm = re.search(r'<p[^>]*>(.*?)</p>', resto, re.S)
            tx = limpio(pm.group(1)) if pm else ''
            if len(tx) > 420:
                tx = tx[:420].rsplit(' ', 1)[0] + '…'
            # k lleva el texto de toda la seccion: se busca en el, se muestra el primer parrafo.
            out.append({'t': 'seccion', 'tit': ht, 'txt': tx, 'ir': ['%s#%s' % (n, h.group(2)), tit], 'k': tit + ' ' + cuerpo})
    return out


def escribir_base():
    import pendientes
    d = pendientes.db()
    fichas = _fichas(d) + _pendientes() + _paginas()
    mun = _fichas_tecnicas(d)[1]
    cuenta = {}
    for f in fichas:
        cuenta[f['t']] = cuenta.get(f['t'], 0) + 1
    cuenta['municipio'] = len(mun)
    js = ('/* Auditavisión · Base de fichas de «Pregúntale al Auditor». La escribe\r\n'
          '   herramientas/asistente.py desde window.AUDIT_DB, el Registro de\r\n'
          '   pendientes y las páginas generadas: no se edita a mano. */\r\n'
          'window.AUDITOR_BASE = ' + json.dumps({'fichas': fichas, 'mun': mun, 'munFuente': 'INEGI, Estadística de Finanzas Públicas Estatales y Municipales (EFIPEM), ejercicio 2024', 'cuenta': cuenta}, ensure_ascii=False, separators=(',', ':')) + ';\r\n')
    open(BASE_JS, 'wb').write(js.encode('utf-8'))
    return cuenta


EJEMPLOS = [
    ('¿Qué es un pliego de observaciones?', '📘'),
    ('¿Cuánto debe Jalisco?', '🗺️'),
    ('Tren Maya', '🚅'),
    ('¿Cuánto gana la presidenta?', '💰'),
    ('¿Qué falta saber del huracán Otis?', '⏳'),
    ('¿Dónde veo la lista negra del SAT?', '🧾'),
    ('¿Quién sanciona la corrupción?', '⚖️'),
    ('¿Cuándo sale la próxima entrega de la ASF?', '📡'),
]


def pagina(cuenta, canal=''):
    total = sum(cuenta.values())
    ej = '\n'.join('            <button type="button" class="pa-ej" data-pa-pregunta="%s"><span aria-hidden="true">%s</span> %s</button>'
                   % (html.escape(q, quote=True), i, html.escape(q)) for q, i in EJEMPLOS)
    return '''<div class="pa" id="paApp" data-canal="%s">
        <div class="pa-chat">
          <div class="pa-chat-cab">
            <img src="assets/auditor/img/logo-auditavision.svg" alt="" width="52" height="40">
            <div><b>Pregúntale al Auditor</b><small>Bot interno de Auditavisión · responde con %s fichas verificadas</small></div>
          </div>
          <ol class="pa-hilo" id="paHilo" aria-live="polite">
            <li class="pa-msg pa-bot">
              <img class="pa-ava" src="assets/auditor/img/logo-auditavision.svg" alt="" width="36" height="28">
              <div class="pa-burbuja">
                <p>¡Hola! Pregúntame lo que quieras sobre el dinero público: <b>un término</b>, <b>un estado</b>, <b>un caso</b>, <b>una ley</b> o <b>dónde encontrar algo</b> en la plataforma.</p>
                <p>Te contesto con una <b>nota técnica sellada</b>, armada solo con datos que ya verificamos, con su fuente y su estado. Si no lo tengo, te lo digo: aquí no se inventa nada.</p>
              </div>
            </li>
          </ol>
          <div class="pa-ejs" aria-label="Preguntas de ejemplo">
%s
          </div>
          <form class="pa-form" id="paForm" autocomplete="off">
            <label class="sr-only" for="paPregunta">Tu pregunta</label>
            <input id="paPregunta" type="text" maxlength="200" placeholder="Escribe tu pregunta…" required>
            <button type="submit">Preguntar ➔</button>
          </form>
        </div>
        <aside class="pa-como">
          <p class="pa-beta"><b>🛠️ En mejora continua.</b> El bot crece con la plataforma: cada ficha, cifra y página que integramos la vuelve más precisa. Si algo no lo encuentra, <a href="comunidad.html">cuéntanos</a> y lo agregamos.</p>
          <h3>Cómo responde</h3>
          <ol>
            <li><b>Busca</b> tu pregunta entre %s fichas de la plataforma: %d términos del glosario, %d expedientes, %d entidades, %d sueldos de cargos públicos, %d fuentes oficiales, %d pendientes, %d páginas y %d secciones.</li>
            <li><b>Arma la nota técnica</b> con la ficha que mejor responde: el texto, las cifras con su estado (<span class="est-chip est-oficial">oficial</span> <span class="est-chip est-derivado">derivado</span> <span class="est-chip est-pendiente">pendiente</span>) y sus fuentes.</li>
            <li><b>Justifica cada cifra</b> por su clasificación: si es <b>oficial</b>, de qué documento sale; si es <b>derivada</b>, con qué operación (y, cuando solo hay aproximación, el rango: mínimo, máximo y punto medio, cada cota con su fuente); si está <b>pendiente</b>, por qué falta, a quién le toca publicarla y el enlace donde debería estar.</li>
            <li><b>La sella</b> con un folio y una huella digital (SHA-256), como el Estado de Cuenta: si alguien cambia una letra, la huella ya no coincide.</li>
          </ol>
          <section class="pa-pendq" id="paSinResp" aria-labelledby="paSinRespT">
            <h3 id="paSinRespT">Lo que aún no sé</h3>
            <p>Cuando no encuentro respuesta, o me dices que la nota no era lo que buscabas, anoto tu pregunta aquí. Esa lista nos dice qué fichas agregar primero.</p>
            <p class="pa-chico" id="paSinRespVacio">Todavía no hay preguntas anotadas en este navegador.</p>
            <ol id="paSinRespLista" hidden></ol>
            <p class="pa-pendq-acc" id="paSinRespAcc" hidden>
              <a class="pa-copiar" id="paSinRespEnviar" hidden>✉️ Enviarlas a Auditavisión</a>
              <button type="button" class="pa-copiar" id="paSinRespCopiar">📋 Copiar la lista</button>
              <button type="button" class="pa-copiar" id="paSinRespBorrar">🗑️ Borrar</button>
            </p>
            <p class="pa-chico" id="paSinRespNota">La lista se guarda solo en tu navegador: nadie más la ve y no se envía sola. Para hacérnosla llegar, cópiala y pégala en <a href="comunidad-tema.html">Comunidad › Un tema que deberíamos investigar</a>.</p>
          </section>
          <p class="pa-aviso"><b>Es un bot interno, no una inteligencia artificial generativa.</b> No escribe cifras por su cuenta ni consulta servicios de fuera: tu pregunta no sale de tu navegador. Solo encuentra y ordena lo que la plataforma ya publicó con su documento.</p>
        </aside>
      </div>''' % (html.escape(canal, quote=True), format(total, ','), ej, format(total, ','), cuenta.get('glosario', 0), cuenta.get('expediente', 0),
                   cuenta.get('entidad', 0), cuenta.get('cargo', 0), cuenta.get('fuente', 0), cuenta.get('pendiente', 0),
                   cuenta.get('pagina', 0), cuenta.get('seccion', 0))
