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
                    'ir': ['expedientes.html#exp-' + f['id'], 'Expedientes de casos'],
                    'k': limpio(f.get('ente')) + ' ' + f['id'].replace('-', ' ')})

    # 3. Las 32 entidades: deuda (SHCP) y lo que la ASF dejo por aclarar.
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
        if not ci:
            continue
        out.append({'t': 'entidad', 'tit': e['name'],
                    'txt': ('Lo que la plataforma tiene verificado de %s: su deuda pública según el Sistema de Alertas de Hacienda '
                            'y lo que la Auditoría Superior dejó por aclarar del dinero federal que recibió en 2024. '
                            'Un monto por aclarar no es un desfalco comprobado: es lo que carecía de documentación al cierre de la auditoría.') % e['name'],
                    'ci': ci, 'fu': fu, 'ir': ['herramienta-inspector-entes.html#ente=estatal:' + e['abbr'], 'el Auditor de entes públicos'],
                    'k': '%s %s estado entidad deuda asf' % (e['abbr'], e.get('capital', ''))})

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

    # 5. Las fuentes oficiales (leyes, informes, decretos).
    for r in d['referencias_legales']:
        out.append({'t': 'fuente', 'tit': limpio(r['cita_apa'])[:180], 'txt': limpio(r.get('descripcion')),
                    'fu': [{'tx': limpio(r['cita_apa']), 'url': r.get('url')}],
                    'ir': ['fuentes-oficiales.html#' + r['id'], 'Fuentes oficiales · [%02d]' % r['num']],
                    'k': limpio(r.get('categoria_nombre'))})
    return out


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
    cuenta = {}
    for f in fichas:
        cuenta[f['t']] = cuenta.get(f['t'], 0) + 1
    js = ('/* Auditavisión · Base de fichas de «Pregúntale al Auditor». La escribe\r\n'
          '   herramientas/asistente.py desde window.AUDIT_DB, el Registro de\r\n'
          '   pendientes y las páginas generadas: no se edita a mano. */\r\n'
          'window.AUDITOR_BASE = ' + json.dumps({'fichas': fichas, 'cuenta': cuenta}, ensure_ascii=False, separators=(',', ':')) + ';\r\n')
    open(BASE_JS, 'wb').write(js.encode('utf-8'))
    return cuenta


EJEMPLOS = [
    ('¿Qué es un pliego de observaciones?', '📘'),
    ('¿Cuánto debe Jalisco?', '🗺️'),
    ('Tren Maya', '🚅'),
    ('¿Cuánto gana la presidenta?', '💰'),
    ('¿Qué falta saber del huracán Otis?', '⏳'),
    ('¿Dónde veo la lista negra del SAT?', '🧾'),
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
