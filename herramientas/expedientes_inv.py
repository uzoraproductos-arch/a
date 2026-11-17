"""Los Expedientes de investigación: la quinta tarjeta de la Biblioteca del
Erario Público (pedido del autor, 16-11-2026: «expedientes serán aquellas
grandes investigaciones que se irán dando seguimiento de forma autónoma,
automatizada e independiente, alimentándose de nuestra base de datos y al
día», y «que el usuario también nos puede solicitar»).

Un expediente junta, en una sola página, todo lo que la plataforma ya sabe
de una gran investigación. **No trae datos propios ni se escribe a mano**: se
arma solo, cada vez que se regenera el sitio, cruzando por sus palabras
(`auditorias.TEMA_BOT`) lo que ya está cotejado en otros módulos:

- el caso en cinco preguntas (`auditorias._datos`, la misma lectura breve de
  Auditoría en imágenes);
- la bitácora: las notas y columnas del Noticiero que lo tocan, con su fecha
  (`columnas.js`), y las etapas de la memoria de promesas (`promesas.py`);
- lo que sigue: los «Lo que sigue» de esas columnas;
- lo que falta: las fichas del Registro de pendientes que lo nombran;
- sus puertas: la investigación en imágenes, su caso en la ASF, el chat y el
  dictamen.

Los titulares del día los suma el navegador desde la bandeja de la Mesa de
redacción (`docs/noticias/bandeja.json`, que el flujo «Mesa de redacción»
actualiza cada día): solo titular, medio, fecha y liga, rotulados «sin
verificar». Un titular nunca es fuente (§2 bis de AGENTS.md).

Una investigación nueva de Auditoría en imágenes tiene su expediente sola.
"""
import html
import json
import os
import re
import unicodedata
from urllib.parse import quote

import auditorias

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = 'expedientes-investigacion.html'
ESTILOS = ['expedientes-inv.css']
SCRIPTS = ['expedientes-inv.js']
CHAT = 'herramienta-inspector-pregunta.html'
DICTAMEN = 'herramienta-inspector-dictamen.html'
BANDEJA = 'docs/noticias/bandeja.json'
# El servicio de la plataforma con el que se pide un expediente a la medida.
SERVICIO = 'expediente'


# El archivero (pedido del autor, 16-11-2026: «ir armando, construyendo nuestras
# grandes investigaciones… así como las que nos soliciten, en nuestro archivero
# digital»). Un expediente pasa por cuatro etapas. Los de Auditoría en imágenes
# ya están publicados; uno pedido entra aquí cuando se acepta y avanza de etapa.
ETAPAS = [
    ('recibido', '📥', 'Recibido', 'Llegó la solicitud y se revisó que el caso se pueda sostener con documentos públicos.'),
    ('cotejo', '🔎', 'En cotejo', 'Se buscan los documentos oficiales y se coteja cada afirmación contra ellos.'),
    ('armado', '🧱', 'En construcción', 'Las cifras cotejadas entran a la base, con su chip y su fuente, y el expediente se arma.'),
    ('publicado', '🗂️', 'Publicado', 'Tiene su página, su bitácora y su sello; desde aquí se le da seguimiento solo.'),
]
# Los expedientes pedidos que la plataforma aceptó. Cada uno:
#   {'id', 'tit', 'fecha' (dd-mm-aaaa en que se aceptó), 'etapa' (clave de
#    ETAPAS), 'que' (una línea, sin cifras), 'ex' (id del expediente publicado,
#    si ya lo está)}.
# Nunca se escribe quién lo pidió (§2 bis: a las personas privadas no se les
# nombra) ni una cifra: las cifras entran por su módulo, ya cotejadas. La lista
# empieza vacía: no se inventa una solicitud.
SOLICITADOS = []


def _valida_solicitados():
    claves = {e[0] for e in ETAPAS}
    for x in SOLICITADOS:
        if x.get('etapa') not in claves or not _fecha(x.get('fecha')) or not x.get('tit') or not x.get('que'):
            raise SystemExit('expedientes_inv.py: el solicitado %r necesita tit, que, fecha dd-mm-aaaa y una etapa de ETAPAS' % x.get('id'))
        if re.search(r'\$\s?\d|\d\s?(mdp|millones|%)', x['que'] + x['tit']):
            raise SystemExit('expedientes_inv.py: el solicitado %r trae una cifra; las cifras entran por su módulo' % x.get('id'))
        if x.get('ex') and x['ex'] not in auditorias.TEMA_BOT:
            raise SystemExit('expedientes_inv.py: el solicitado %r apunta a un expediente que no existe' % x.get('id'))


def archivo(id_):
    return 'expediente-%s.html' % id_


def pregunta(id_):
    """La pregunta con la que el chat abre el expediente (modos.PREGUNTA)."""
    return 'Expediente de ' + auditorias.TEMA_BOT[id_][0]


def _plano(s):
    s = unicodedata.normalize('NFD', str(s or '').lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return ' ' + re.sub(r'[^a-z0-9ñ]+', ' ', s).strip() + ' '


def _toca(id_, texto):
    p = _plano(texto)
    return any(_plano(k) in p for k in auditorias.TEMA_BOT[id_])


def _fecha(s):
    """'dd-mm-aaaa' → (aaaa, mm, dd) para ordenar; None si no es una fecha."""
    m = re.match(r'^(\d{2})-(\d{2})-(\d{4})$', str(s or ''))
    return (int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None


MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
         'septiembre', 'octubre', 'noviembre', 'diciembre']


def _fecha_tx(s):
    f = _fecha(s)
    return '%d de %s de %d' % (f[2], MESES[f[1] - 1], f[0]) if f else ''


_COLS = None


def _columnas():
    global _COLS
    if _COLS is None:
        import asistente_personajes
        _COLS = asistente_personajes.columnas()[0]
    return _COLS


def _liga_col(c):
    if c.get('seccion') == 'Al momento':
        return 'noticias-al-momento-%s.html' % c['id']
    return 'noticias-auditavision.html#col-%s' % c['id']


_PEND = None


def _pendientes():
    global _PEND
    if _PEND is None:
        import pendientes
        _PEND = pendientes.recolectar()
    return _PEND


def expediente(id_):
    """Todo lo que la plataforma sabe de una investigación, ya cruzado."""
    a = next(x for x in auditorias.AUDITORIAS if x[0] == id_)
    d = auditorias._datos(id_)
    tit = re.sub('<[^>]+>', '', a[5])
    bit, sigue = [], []
    for c in _columnas():
        if not _toca(id_, ' '.join([c.get('titulo', ''), ' '.join(c.get('temas') or [])])):
            continue
        f = c.get('actualizado') or c.get('fecha') or ''
        bit.append({'f': f, 'ico': c.get('icono') or '📰', 'que': c.get('seccion', 'Noticiero'),
                    'tit': c.get('titulo', ''), 'url': _liga_col(c),
                    'act': bool(c.get('actualizado') and c.get('fecha') and c['actualizado'] != c['fecha'])})
        for s in c.get('sigue') or []:
            sigue.append({'que': s.get('que', ''), 'url': s.get('url', ''), 'de': c.get('titulo', ''), 'col': _liga_col(c)})
    import promesas
    for p in promesas.todas():
        if not _toca(id_, ' '.join([p.get('tit', ''), ' '.join(p.get('temas') or [])])):
            continue
        for e in p.get('etapas') or []:
            if _fecha(e.get('fecha')):
                bit.append({'f': e['fecha'], 'ico': '🗓️', 'que': 'Memoria de promesas · ' + e.get('et', ''),
                            'tit': p['tit'], 'url': 'noticias-seguimiento.html#promesa-' + p['id'], 'act': False})
    bit.sort(key=lambda x: _fecha(x['f']) or (0, 0, 0), reverse=True)
    pend = [p for p in _pendientes()
            if _toca(id_, ' '.join([p.get('que', ''), p.get('tema', '')]))]
    # Los pendientes que la propia lectura breve ya señala (chip con su ficha).
    ids = {p['id'] for p in pend}
    for v, etq, e, pid in d['cuanto']:
        if pid and pid not in ids:
            hit = [p for p in _pendientes() if p['id'] == pid]
            if hit:
                pend.append(hit[0])
                ids.add(pid)
    abierto = bool(pend or sigue or any(e == 'pendiente' for _, _, e, _ in d['cuanto']))
    return {'id': id_, 'tit': tit, 'img': a[1], 'alt': a[3], 'etq': a[4], 'preg': a[6],
            'tema': auditorias.tema_de(id_), 'd': d, 'bit': bit, 'sigue': sigue, 'pend': pend,
            'abierto': abierto, 'nov': bit[0]['f'] if bit and _fecha(bit[0]['f']) else '',
            'asf': ('expedientes.html#exp-' + auditorias.EXPEDIENTE[id_]) if id_ in auditorias.EXPEDIENTE else ''}


def _huella(e):
    """SHA-256 del contenido del expediente: si cambia una cifra, un documento,
    la bitácora o un pendiente, cambia la huella."""
    import hashlib
    d = e['d']
    obj = {'id': e['id'], 'que': d['que'], 'cuanto': [list(x) for x in d['cuanto']], 'quien': d['quien'],
           'docs': d['docs'], 'falta': d['falta'], 'bit': [[x['f'], x['tit'], x['url']] for x in e['bit']],
           'sigue': [[x['que'], x['url']] for x in e['sigue']], 'pend': [p['id'] for p in e['pend']]}
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def _dictamenes(e):
    """Las preguntas cuyo dictamen compone el expediente: la del caso y la de
    cada nota de su bitácora que el chat contesta por su título."""
    qs = [(e['preg'], 'El caso')]
    vistos = {e['preg']}
    for x in e['bit']:
        if x['que'].startswith('Memoria de promesas') or x['tit'] in vistos:
            continue
        vistos.add(x['tit'])
        qs.append((x['tit'], x['que']))
    return qs[:7]


def _sello(e):
    hx = e['hx']
    dics = ''.join(
        '<li><a href="%s?q=%s&amp;modo=inspector" target="_blank" rel="noopener"><span class="xi-dic-de">%s</span>%s <span aria-hidden="true">➔</span></a></li>'
        % (DICTAMEN, quote(q), _esc(de), _esc(q)) for q, de in _dictamenes(e))
    return ('<div class="xi-dics">\n'
            '          <p>Cada pregunta del caso tiene su <b>dictamen cívico</b>, con folio y huella. Juntos forman el expediente:</p>\n'
            '          <ol class="xi-dics-lista">%s</ol>\n'
            '        </div>\n'
            '        <div class="xi-sello">\n'
            '          <div>\n'
            '            <b>Dictamen integrado del expediente</b>\n'
            '            <p>Folio <b class="xi-folio">%s-%s</b> · %d dictámenes · %d cifras · %d documentos</p>\n'
            '            <p class="xi-huella">Huella digital (SHA-256 del expediente): <code>%s</code></p>\n'
            '            <p class="xi-chico">La huella se calcula sobre las cifras, los documentos, la bitácora y los pendientes: si cambia uno, cambia la huella y el folio. '
            '<b>No es un documento oficial ni un peritaje con validez ante una autoridad</b>: es el respaldo documental de una investigación, para que cualquiera revise de dónde sale cada dato.</p>\n'
            '          </div>\n'
            '          <button type="button" class="xi-boton xi-imprime" id="xiImprime">🖨️ Imprimir o guardar PDF</button>\n'
            '        </div>') % (dics, e['num'], hx[:8].upper(), len(_dictamenes(e)), len(e['d']['cuanto']), len(e['d']['docs']),
                                 ' '.join(hx[i:i + 16] for i in range(0, 64, 16)))


_TODOS = None


def todos():
    global _TODOS
    if _TODOS is None:
        _TODOS = [expediente(a[0]) for a in auditorias.AUDITORIAS]
        for n, e in enumerate(_TODOS, 1):
            e['num'] = 'EXP-%03d' % n
            e['hx'] = _huella(e)
        _valida_solicitados()
    return _TODOS


def de(id_):
    return next(e for e in todos() if e['id'] == id_)


def para_bot(id_):
    """Lo que el chat necesita para ofrecer el expediente (auditorias.bot_fichas)."""
    e = de(id_)
    return {'ex': archivo(id_), 'exn': e['num'], 'nov': _fecha_tx(e['nov']), 'ab': 1 if e['abierto'] else 0,
            'nd': len(e['d']['docs']), 'nb': len(e['bit']), 'np': len(e['pend']),
            'qn': e['d']['quien'], 'fal': e['d']['falta'], 'fo': e['num'] + '-' + e['hx'][:8].upper()}


def _chip(e, pend=None):
    return auditorias._chip(e, pend)


def _estado(e):
    return ('<span class="xi-estado xi-abierto">🟠 Abierto: hay cosas por saber</span>' if e['abierto']
            else '<span class="xi-estado xi-doc">🟢 Documentado</span>')


def _esc(s):
    return html.escape(str(s or ''), quote=True)


def _caratula(e):
    d = e['d']
    datos = [('Expediente', e['num']), ('Tema', '%s %s' % (e['tema'][0], e['tema'][1])),
             ('Último registro fechado', _fecha_tx(e['nov']) or 'Sin registros fechados todavía'),
             ('Cifras', str(len(d['cuanto']))), ('Documentos', str(len(d['docs']))),
             ('En la bitácora', str(len(e['bit']))), ('Pendientes', str(len(e['pend'])))]
    return ('<div class="xi-caratula">\n'
            '          <img class="xi-img" src="%s" alt="%s" loading="lazy" width="480" height="270">\n'
            '          <div class="xi-car-tx">\n'
            '            <p class="xi-car-etq">%s</p>\n'
            '            <p class="xi-car-preg">%s</p>\n'
            '            <p>%s</p>\n'
            '            <dl class="xi-ficha">%s</dl>\n'
            '          </div>\n        </div>') % (
        e['img'], _esc(e['alt']), e['etq'], _esc(e['preg']), _estado(e),
        ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (k, _esc(v)) for k, v in datos))


def _caso(e):
    d = e['d']
    filas = ''.join('<tr><td class="xi-cifra">%s</td><td>%s</td><td>%s</td></tr>' % (_esc(v), _esc(etq), _chip(est, pend))
                    for v, etq, est, pend in d['cuanto'])
    tabla = ('<div class="xi-tabla"><table><thead><tr><th>Cifra</th><th>Qué es</th><th>Estado</th></tr></thead>'
             '<tbody>%s</tbody></table></div>' % filas) if filas else '<p>Este caso no trae cifras propias: lleva a las de su página.</p>'
    docs = ''.join('<li>%s</li>' % x for x in d['docs'])
    return ('<div class="xi-caso">\n'
            '          <div class="xi-bloque"><h3>🔎 Qué pasó</h3><p>%s</p></div>\n'
            '          <div class="xi-bloque"><h3>💰 Cuánto dinero</h3>%s</div>\n'
            '          <div class="xi-bloque"><h3>🏛️ Quién interviene</h3><p>%s</p></div>\n'
            '          <div class="xi-bloque"><h3>📄 Qué documento lo acredita</h3><ol class="xi-docs">%s</ol></div>\n'
            '          <div class="xi-bloque xi-falta"><h3>❓ Qué falta saber</h3><p>%s</p></div>\n'
            '        </div>') % (_esc(d['que']), tabla, _esc(d['quien']), docs, _esc(d['falta']))


def _bitacora(e):
    if not e['bit']:
        return ('<p class="xi-vacio">Todavía no hay notas ni promesas fechadas sobre este caso en la plataforma. '
                'Cuando una nota del Noticiero lo toque, aparecerá aquí sola.</p>')
    return '<ol class="xi-bitacora">%s</ol>' % ''.join(
        '<li><time>%s</time><div><span class="xi-bit-que">%s %s%s</span><a href="%s">%s ➔</a></div></li>' % (
            _fecha_tx(x['f']) or 'Sin fecha', x['ico'], _esc(x['que']),
            ' · actualizada' if x['act'] else '', _esc(x['url']), _esc(x['tit']))
        for x in e['bit'])


def _sigue(e):
    partes = []
    if e['sigue']:
        partes.append('<h3>🧭 Lo que sigue</h3><p>Lo que falta revisar para seguir el dinero, tomado de las notas del caso.</p><ul class="xi-sigue">%s</ul>' % ''.join(
            '<li>%s%s <small>De: <a href="%s">%s</a></small></li>' % (
                _esc(s['que']),
                (' <a href="%s" target="_blank" rel="noopener noreferrer">Dónde buscarlo ↗</a>' % _esc(s['url'])) if s['url'] else '',
                _esc(s['col']), _esc(s['de']))
            for s in e['sigue']))
    if e['pend']:
        partes.append('<h3>⏳ Lo que falta y quién lo debe</h3><p>Fichas del <a href="pendientes.html">Registro de pendientes</a> que tocan este caso.</p><ul class="xi-pend">%s</ul>' % ''.join(
            '<li><a href="pendientes.html#%s">%s</a> %s</li>' % (_esc(p['id']), _esc(p.get('que', '')[:220]), _chip('pendiente', p['id']))
            for p in e['pend']))
    if not partes:
        partes.append('<p class="xi-vacio">La plataforma no tiene anotado ningún pendiente ni un «lo que sigue» para este caso. '
                      'Eso no quiere decir que esté cerrado: quiere decir que lo publicado ya está integrado.</p>')
    return '\n          '.join(partes)


def _puertas(e):
    q = pregunta(e['id'])
    p = [(auditorias.archivo(e['id']), '📖', 'La investigación en imágenes', 'Las cuentas paso a paso')]
    if e['asf']:
        p.append((e['asf'], '📂', 'Su caso en la ASF', 'Las auditorías y lo que quedó por aclarar'))
    p += [('%s?modo=inspector&amp;q=%s' % (CHAT, quote(q)), '💬', 'Pregúntale al Auditor', 'El expediente, en la plática'),
          ('%s?q=%s&amp;modo=inspector' % (DICTAMEN, quote(q)), '🧾', 'Generar dictamen', 'El respaldo con folio y huella'),
          ('servicios-cotiza.html?servicio=%s&amp;tema=%s' % (SERVICIO, quote(e['tit'])), '✍️', 'Pide una ampliación', 'Un expediente a la medida de tu pregunta')]
    return '<nav class="xi-puertas" aria-label="Puertas del expediente">%s</nav>' % ''.join(
        '<a class="xi-puerta" href="%s"><span aria-hidden="true">%s</span><span><b>%s</b><small>%s</small></span></a>' % x for x in p)


AL_DIA = ('<div class="xi-aldia">\n'
          '          <h3>🔄 Cómo se mantiene al día</h3>\n'
          '          <ul>\n'
          '            <li><b>Se arma solo.</b> Nadie lo escribe a mano: cada día, y cada vez que la plataforma publica, el expediente se vuelve a armar con lo que la base tiene de este caso. Si nada cambió en la base, queda igual, con el mismo folio.</li>\n'
          '            <li><b>Se alimenta de la base.</b> Las cifras, los documentos, las notas y los pendientes son los mismos de sus módulos: si cambian allá, cambian aquí.</li>\n'
          '            <li><b>Vigila cada día.</b> La Mesa de redacción junta titulares a diario; los de este caso salen abajo, <b>sin verificar</b>, como aviso de que hay algo por cotejar.</li>\n'
          '            <li><b>Nada entra sin cotejo.</b> Un titular nunca es fuente: una cifra entra al expediente solo cuando se coteja contra su documento oficial.</li>\n'
          '          </ul>\n        </div>')


def _radar(e):
    return ('<div class="xi-radar" id="xiRadar" data-bandeja="%s" data-k="%s">\n'
            '          <p class="xi-vacio" role="status">⏳ Buscando titulares de este caso en la recolección del día…</p>\n'
            '          <noscript><p>Los titulares del día necesitan JavaScript.</p></noscript>\n'
            '        </div>') % (BANDEJA, _esc(json.dumps([_plano(k).strip() for k in auditorias.TEMA_BOT[e['id']]], ensure_ascii=False)))


def _migas():
    return {'menu_archivo': 'aprende.html', 'padre': ('aprende.html', 'Aprende'),
            'padre2': ('diccionario.html', 'Biblioteca del Erario Público')}


def pagina(e):
    def sec(id_, titulo, texto, bloque):
        return {'id': id_, 'titulo': titulo, 'texto': texto, 'tarjetas': [], 'bloque': bloque}
    return dict(_migas(), **{
        'archivo': archivo(e['id']), 'menu': 'Expediente: ' + e['tit'], 'padre3': (INDICE, 'Expedientes internos'),
        'icono': '🗂️', 'titulo': 'Expediente: ' + e['tit'],
        'lema': '%s · %s' % (e['num'], 'abierto, en seguimiento' if e['abierto'] else 'documentado'),
        'entrada': ('Todo lo que la plataforma sabe de este caso, en un solo lugar: el caso en cinco preguntas, su bitácora, '
                    'lo que sigue y lo que falta. Se arma solo con la base de datos, y cada cifra lleva su documento.'),
        'estilos': ESTILOS, 'scripts': SCRIPTS, 'sin_saltos': True,
        'secciones': [
            sec('caratula', '🗂️ Carátula', 'El caso de un vistazo.', _caratula(e) + '\n        ' + _puertas(e)),
            sec('caso', '📝 El caso en cinco preguntas', 'Con las mismas cifras y documentos de su investigación.', _caso(e)),
            sec('bitacora', '🕰️ Bitácora', 'Lo que la plataforma ha publicado sobre el caso, de lo más nuevo a lo más viejo.', _bitacora(e)),
            sec('sigue', '🧭 Lo que sigue y lo que falta', 'El caso no se olvida: esto es lo que queda por revisar.',
                '<div class="xi-sigue-caja">\n          %s\n        </div>' % _sigue(e)),
            sec('dictamenes', '🧾 Los dictámenes del expediente', 'El expediente es una gran investigación hecha de dictámenes.', _sello(e)),
            sec('radar', '📡 En el radar: titulares por cotejar', 'Lo que juntó hoy la recolección automática. Sin verificar.',
                _radar(e) + '\n        ' + AL_DIA),
        ],
    })


def _tarjeta(e):
    return ('<a class="xi-tarjeta" href="%s" data-xi-tx="%s" data-xi-ab="%d">'
            '<img src="%s" alt="" loading="lazy" width="480" height="270">'
            '<span class="xi-t-tx"><span class="xi-t-num">%s</span><b>%s</b>'
            '<small>%s</small>%s'
            '<span class="xi-t-pie">%d cifras · %d documentos · %d en bitácora%s</span></span></a>') % (
        archivo(e['id']), _esc(_plano(e['tit'] + ' ' + e['preg'] + ' ' + ' '.join(auditorias.TEMA_BOT[e['id']])).strip()),
        1 if e['abierto'] else 0, e['img'], e['num'], _esc(e['tit']), _esc(e['preg']), _estado(e),
        len(e['d']['cuanto']), len(e['d']['docs']), len(e['bit']),
        (' · último registro: ' + _fecha_tx(e['nov'])) if e['nov'] else '')


PIDE = ('<div class="xi-pide">\n'
        '          <h3>✍️ ¿Tu caso no está? Pídelo</h3>\n'
        '          <p>Los expedientes también se abren a pedido. Hay dos caminos:</p>\n'
        '          <div class="xi-pide-acc">\n'
        '            <a class="xi-boton xi-boton-pri" href="servicios-cotiza.html?servicio=%s">🗂️ Pedir un expediente a la medida</a>\n'
        '            <a class="xi-boton" href="noticias-verifica.html#propon">💡 Proponer un caso para investigar</a>\n'
        '          </div>\n'
        '          <p class="xi-chico">El expediente a la medida es un servicio de la plataforma y se cotiza; proponer un caso no cuesta. '
        'En los dos, la regla es la misma: solo documentos públicos, cada cifra con su fuente y nunca datos de personas privadas.</p>\n'
        '        </div>') % SERVICIO


def _archivero():
    pasos = ''.join('<li class="xi-etapa"><span class="xi-etapa-ico" aria-hidden="true">%s</span><b>%s</b><span>%s</span></li>' % x[1:] for x in ETAPAS)
    nom = {x[0]: x for x in ETAPAS}
    if SOLICITADOS:
        filas = ''.join(
            '<li><span class="xi-estado xi-abierto">%s %s</span> <b>%s</b><small>%s · aceptado el %s</small>%s</li>' % (
                nom[x['etapa']][1], nom[x['etapa']][2], _esc(x['tit']), _esc(x['que']), _fecha_tx(x['fecha']),
                (' <a href="%s">Abrir su expediente ➔</a>' % archivo(x['ex'])) if x.get('ex') else '')
            for x in sorted(SOLICITADOS, key=lambda x: _fecha(x['fecha']), reverse=True))
        lista = '<ul class="xi-solicitados">%s</ul>' % filas
    else:
        lista = ('<p class="xi-vacio">Todavía no hay expedientes pedidos en construcción. Cuando aceptemos uno, aparecerá aquí con su etapa, '
                 'sin decir quién lo pidió. <a href="#pide">Pide el tuyo</a>.</p>')
    return ('<ol class="xi-etapas">%s</ol>\n        <h3 class="xi-grupo">📥 Pedidos, en construcción <small>%d</small></h3>\n        %s'
            % (pasos, len(SOLICITADOS), lista))


def indice():
    ex = todos()
    grupos = []
    for ico, nom, ids in auditorias.TEMAS:
        lista = sorted([e for e in ex if e['id'] in ids], key=lambda e: _fecha(e['nov']) or (0, 0, 0), reverse=True)
        grupos.append('<h3 class="xi-grupo">%s %s <small>%d</small></h3>\n          <div class="xi-rejilla">%s</div>' % (
            ico, nom, len(lista), ''.join(_tarjeta(e) for e in lista)))
    abiertos = sum(1 for e in ex if e['abierto'])
    barra = ('<div class="xi-barra">\n'
             '          <label class="sr-only" for="xiBusca">Busca un expediente</label>\n'
             '          <input type="search" id="xiBusca" class="xi-busca" placeholder="Busca un caso: tren, deuda, medicamentos…" autocomplete="off">\n'
             '          <div class="xi-filtros" role="group" aria-label="Filtra por estado">\n'
             '            <button type="button" class="xi-filtro" data-xi-f="" aria-pressed="true">Todos · %d</button>\n'
             '            <button type="button" class="xi-filtro" data-xi-f="1" aria-pressed="false">🟠 Abiertos · %d</button>\n'
             '            <button type="button" class="xi-filtro" data-xi-f="0" aria-pressed="false">🟢 Documentados · %d</button>\n'
             '          </div>\n'
             '          <p class="xi-vacio" id="xiNada" hidden>Ningún expediente coincide. Prueba con otra palabra o <a href="#pide">pide el tuyo</a>.</p>\n'
             '        </div>') % (len(ex), abiertos, len(ex) - abiertos)
    return dict(_migas(), **{
        'archivo': INDICE, 'menu': 'Expedientes internos', 'icono': '🗂️', 'titulo': 'Expedientes internos',
        'lema': 'Las grandes investigaciones, con seguimiento',
        'entrada': ('El archivero digital de la plataforma: aquí se arman y se guardan las grandes investigaciones, las nuestras y las que '
                    'nos piden. Cada expediente junta el caso en cinco preguntas, su bitácora, sus dictámenes, lo que sigue y lo que falta. '
                    '<b>Se arman solos con la base de datos</b> y se ponen al día cada día, sin esperar a una publicación.'),
        'estilos': ESTILOS, 'scripts': SCRIPTS, 'sin_saltos': True,
        'pie_extra': None,
        'secciones': [
            {'id': 'expedientes', 'titulo': '🗂️ Los expedientes', 'texto': 'Toca uno para abrirlo. Los que tienen el registro más reciente en su bitácora van primero.',
             'tarjetas': [], 'bloque': barra + '\n        <div id="xiLista">\n          ' + '\n          '.join(grupos) + '\n        </div>'},
            {'id': 'archivero', 'titulo': '🗃️ El archivero: cómo se construye un expediente',
             'texto': 'Las investigaciones propias y las que nos piden pasan por las mismas cuatro etapas.', 'tarjetas': [], 'bloque': _archivero()},
            {'id': 'pide', 'titulo': '✍️ Pide un expediente', 'texto': 'También investigamos a pedido.', 'tarjetas': [], 'bloque': PIDE},
            {'id': 'al-dia', 'titulo': '🔄 Seguimiento automático', 'texto': 'Qué quiere decir que un expediente esté «al día».',
             'tarjetas': [], 'bloque': AL_DIA},
        ],
    })


def paginas():
    return [indice()] + [pagina(e) for e in todos()]


def radar(e, bandeja):
    """Los titulares de la bandeja que tocan el caso, con la misma regla que
    expedientes-inv.js: solo se cuentan; nunca entran al expediente."""
    ks = [_plano(k).strip() for k in auditorias.TEMA_BOT[e['id']]]
    vistos = set()
    for x in (bandeja or {}).get('notas') or []:
        g = x.get('grupo') or x.get('url')
        if g in vistos or not re.match(r'https?://', x.get('url') or ''):
            continue
        t = _plano(x.get('titulo'))
        if any(' ' + k + ' ' in t for k in ks):
            vistos.add(g)
    return len(vistos)


def resumen(cambiaron=()):
    """El reporte del flujo «Expedientes al día» (Markdown): cómo quedó cada
    expediente y cuántos titulares sin verificar esperan cotejo."""
    try:
        bandeja = json.load(open(os.path.join(RAIZ, BANDEJA), encoding='utf-8'))
    except (OSError, ValueError):
        bandeja = {}
    ex = todos()
    cambiaron = set(cambiaron)
    out = ['## Expedientes al día', '',
           '%d expedientes: %d abiertos y %d documentados. Cambiaron hoy: %d.' % (
               len(ex), sum(1 for e in ex if e['abierto']), sum(1 for e in ex if not e['abierto']),
               sum(1 for e in ex if archivo(e['id']) in cambiaron)), '',
           '| Folio | Expediente | Estado | Último registro | Pendientes | Titulares por cotejar | Cambió hoy |',
           '|---|---|---|---|---|---|---|']
    for e in ex:
        out.append('| %s-%s | %s | %s | %s | %d | %d | %s |' % (
            e['num'], e['hx'][:8].upper(), e['tit'], 'abierto' if e['abierto'] else 'documentado', e['nov'] or 'sin fecha',
            len(e['pend']), radar(e, bandeja), 'sí' if archivo(e['id']) in cambiaron else 'no'))
    out += ['', 'Los titulares son de la Mesa de redacción%s: **sin verificar**. Solo se cuentan; ninguno entra al expediente sin cotejo.' % (
        (' del ' + bandeja['actualizado']) if bandeja.get('actualizado') else '')]
    return '\n'.join(out)


if __name__ == '__main__':
    import sys
    print(resumen(sys.argv[1:]))
