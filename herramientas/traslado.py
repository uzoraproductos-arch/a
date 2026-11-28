#!/usr/bin/env python3
"""La Enciclopedia se vuelve Planisferio (Ronda 7, decisión del autor, 22-11-2026).

«La antigua Enciclopedia se convierte en Planisferio»: lo que vivía en Números,
Datos y Aprende se reparte en las diez dimensiones del Planisferio, cada página
autónoma, con sus migas «Planisferio › <Dimensión> › …» y la pestaña Planisferio
marcada. La Biblioteca del Erario (el diccionario, el glosario, las fuentes, el
marco legal, las preguntas frecuentes y los expedientes de control interno) se
queda en Comunidad; Garantías cívicas se muda al Noticiero, y las cuatro portadas
de la Enciclopedia quedan solo para la administración.

Ningún archivo cambia de nombre (las ligas viejas siguen sirviendo) y ninguna
cifra se mueve: cambian la pestaña, las migas y por dónde se llega.

La regla va por el nombre del archivo, porque la usan tres lugares que deben dar
lo mismo: servicios_fichas.pestana_de() (Python), volver-auditor.js (el
navegador) y vinculos_auditor.py (la revisión). `python3 traslado.py --prueba`
compara la regla de Python con la de volver-auditor.js sobre todas las páginas.
"""
import glob
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Las cuatro portadas de la Enciclopedia: solo para la administración (acceso.js las cierra a quien no lo es).
PRIVADAS = ('enciclopedia-auditavision.html', 'sigue-el-dinero.html', 'descarga-los-datos.html', 'aprende.html')
# A dónde lleva hoy una liga pública que apuntaba a una portada privada.
SUSTITUTA = {'enciclopedia-auditavision.html': 'planisferio.html', 'sigue-el-dinero.html': 'planisferio-dim-financiera.html',
             'descarga-los-datos.html': 'planisferio.html', 'aprende.html': 'diccionario.html'}
# Una liga vieja con ancla o ?abrir= que ya tiene su página propia.
ANCLAS = {'aprende.html#trivia': 'numeros-trivia-presidentes.html', 'sigue-el-dinero.html?abrir=eb-cuenta-federal': 'numeros-estado-de-resultados.html'}
# La Biblioteca del Erario se queda en Comunidad (su portada es diccionario.html).
BIBLIOTECA = r'^(diccionario|glosario|fuentes-oficiales|marco-legal|preguntas-frecuentes|expedientes-investigacion|expediente-[a-z0-9-]+)\.html$'
# Garantías cívicas va al Noticiero.
NOTICIERO = r'^garantias(-[a-z0-9-]+)?\.html$'
# Cada página de la antigua Enciclopedia, a su dimensión. La primera regla que coincide gana (van de lo particular a lo general).
REGLAS = [
    (r'^(numeros-egreso-(adefas|costo-financiero)|numeros-la-deuda)\.html$', 'deuda'),
    (r'^(herramienta-megaobras(-[a-z0-9-]+)?|contratos-publicos)\.html$', 'inversion'),
    (r'^(herramienta-ambiente(-[a-z0-9-]+)?|datos-(medio-ambiente|ambiente-[a-z0-9-]+|justicia-ambiental(-[a-z0-9-]+)?)|aprende-recursos-naturales|contexto-dimensional-ambiental)\.html$', 'ambiental'),
    (r'^(datos-(poder-legislativo|legislativo-[a-z0-9-]+)|marco-legal-tres-niveles)\.html$', 'legislativa'),
    (r'^datos-(poder-judicial|judicial-[a-z0-9-]+)\.html$', 'judicial'),
    (r'^datos-salud(-[a-z0-9-]+)?\.html$', 'salud'),
    (r'^contexto-dimensional-social\.html$', 'social'),
    (r'^aprende-fraude-en-numeros\.html$', 'penal'),
    (r'^(herramienta-inspector(-[a-z0-9-]+)?|expedientes|informes-[a-z0-9-]+|datos-administracion-publica(-[a-z0-9-]+)?|aprende-auditoria|numeros-herramientas-del-auditor)\.html$', 'administracion'),
    (r'^fiscal-[a-z0-9-]+\.html$', 'financiera'),
    (r'^(numeros-[a-z0-9-]+|datos-[a-z0-9-]+|radar-[a-z0-9-]+|contexto-dimensional-[a-z0-9-]+|herramienta-calculadora(-[a-z0-9-]+)?|simulador-presupuesto)\.html$', 'financiera'),
]
# Las del Auditor que empiezan como herramienta del Inspector, pero son del chat.
DEL_AUDITOR = ('herramienta-inspector-pregunta.html', 'herramienta-inspector-dictamen.html')

# Lo que dice cada dimensión de sí misma en su página (las mismas de planisferio.DIMENSIONES, con su índice de páginas).
DIM_PAG = 'planisferio-dim-%s.html'


def dim_de(archivo):
    """La dimensión del Planisferio de una página de la antigua Enciclopedia, o None."""
    a = archivo.split('#')[0].split('?')[0]
    if a in DEL_AUDITOR or a in PRIVADAS:
        return None
    for rx, d in REGLAS:
        if re.match(rx, a):
            return d
    return None


def pestana(archivo):
    """La pestaña que manda el traslado, o None si la página no es de la antigua Enciclopedia."""
    a = archivo.split('#')[0].split('?')[0]
    if a in PRIVADAS:
        return 'Administración'
    if re.match(BIBLIOTECA, a):
        return 'Comunidad'
    if re.match(NOTICIERO, a):
        return 'Noticiero'
    if dim_de(a):
        return 'Planisferio'
    return None


def js():
    """La misma regla para el navegador (volver-auditor.js la lleva escrita; la prueba compara)."""
    return {'priv': list(PRIVADAS), 'bib': BIBLIOTECA, 'not': NOTICIERO, 'reglas': REGLAS, 'aud': list(DEL_AUDITOR)}


def sin_privadas(texto):
    """Ninguna liga pública a las portadas de la Enciclopedia: cada una va a su sustituta (Planisferio o la Biblioteca).
    Las anclas se conservan solo si la sustituta las tiene; si no, se quitan."""
    def cambia(m):
        f, resto = m.group(3), m.group(4) or ''
        return '%s%s="%s"' % (m.group(1), m.group(2), ANCLAS.get(f + resto) or _resuelve(f, resto) or SUSTITUTA[f])
    return re.sub(r'(\s)(href|data-numeros)="(%s)([?#][^"]*)?"' % '|'.join(re.escape(p) for p in PRIVADAS), cambia, texto)


_MAPAS = {}


def _resuelve(f, resto):
    """Una liga vieja con ?abrir= o #ancla, a la página que ya tiene su portada (abrir_a_pagina y hash_a_pagina de apartados.py)."""
    if not resto:
        return None
    if f not in _MAPAS:
        import apartados
        a = next((x for x in apartados.APARTADOS if x['archivo'] == f), {})
        _MAPAS[f] = (a.get('abrir_a_pagina') or {}, a.get('hash_a_pagina') or {})
    ab, ha = _MAPAS[f]
    q = re.search(r'[?&]abrir=([A-Za-z0-9_-]+)', resto)
    h = resto.split('#', 1)[1] if '#' in resto else ''
    return (q and ab.get(q.group(1))) or (h and ha.get(h)) or None


def _txt(t):
    import html as _h
    return _h.unescape(re.sub(r'<[^>]+>', '', t or '')).strip()


def paginas_dim():
    """Las diez páginas del Planisferio con todo lo que trae cada dimensión (planisferio-dim-<id>.html). Se arman con las
    páginas ya generadas: su título, su entrada y su sección (la miga que va antes de ella). No traen cifras."""
    import html as _h
    import planisferio
    por = {}
    for f in sorted(glob.glob(os.path.join(RAIZ, '*.html'))):
        b = os.path.basename(f)
        d = dim_de(b)
        if not d:
            continue
        s = open(f, encoding='utf-8', errors='ignore').read()
        if re.search(r'http-equiv="refresh"|location\.replace\(\'[^\']+\'\);\s*</script>\s*</head>', s[:3000]) or '<h1' not in s:
            continue  # una redirección
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
        de = re.search(r'<meta name="description" content="([^"]*)"', s)
        mg = re.search(r'<nav class="apartado-migas".*?</nav>', s, re.S)
        cr = re.findall(r'<a href="([^"]+)">([^<]+)</a>', mg.group(0)) if mg else []
        grupo = cr[-1][1] if cr and cr[-1][0] not in (DIM_PAG % d, 'planisferio.html', 'index.html') else ''
        tit = _txt(h1.group(1)) if h1 else b
        desc = _txt(_h.unescape(de.group(1))) if de else ''
        por.setdefault(d, {}).setdefault(grupo, []).append((tit, desc[:170] + ('…' if len(desc) > 170 else ''), b))
    out = []
    for d, ico, nom, que, *_ in planisferio.DIMENSIONES:
        G = por.get(d, {})
        n = sum(len(v) for v in G.values())
        secs = []
        for g in sorted(G, key=lambda g: (g != '', -len(G[g]), g)):
            secs.append({'id': 'g-' + (re.sub(r'[^a-z0-9]+', '-', g.lower()).strip('-') or 'principal'),
                         'titulo': g or 'Lo principal', 'texto': '%d %s' % (len(G[g]), 'página' if len(G[g]) == 1 else 'páginas'),
                         'tarjetas': [(ico, _h.escape(t), _h.escape(x), f, '', '') for t, x, f in G[g]]})
        out.append({
            'archivo': DIM_PAG % d, 'menu': '%s · todo lo de esta dimensión' % nom, 'menu_archivo': 'planisferio.html',
            'padre': ('planisferio.html', 'Planisferio'), 'icono': ico, 'lema': 'Planisferio · dimensión %s' % nom.lower(),
            'titulo': 'Dimensión %s: todo lo que trae' % nom.lower(),
            'entrada': ('%s Aquí está todo lo de esta dimensión: %d páginas, cada una autónoma y con sus fuentes. Antes vivían en la '
                        'Enciclopedia; desde la Ronda 7 viven en el Planisferio. Las cifras son las mismas: solo cambió por dónde se llega.') % (_h.escape(que), n),
            'secciones': secs or [{'id': 'g-vacia', 'titulo': 'Por ahora, solo el mapa', 'texto': 'Esta dimensión aún no tiene páginas propias fuera del mapa y los portales.', 'tarjetas': []}],
            'sin_saltos': True})
    return out


def prueba():
    archivos = sorted(os.path.basename(f) for f in glob.glob(os.path.join(RAIZ, '*.html')))
    py = {f: pestana(f) for f in archivos}
    prog = ("global.window={location:{pathname:'/x.html',search:''}};global.document={addEventListener:function(){},querySelector:function(){return null}};"
            "global.sessionStorage={getItem:function(){return null},setItem:function(){}};"
            "var s=require('fs').readFileSync(%s,'utf8');var m=s.match(/\\/\\* traslado \\*\\/([\\s\\S]*?)\\/\\* fin traslado \\*\\//);"
            "eval(m[1]);console.log(JSON.stringify(%s.map(function(f){return traslado(f)})));"
            % (json.dumps(os.path.join(RAIZ, 'assets', 'auditor', 'js', 'volver-auditor.js')), json.dumps(archivos)))
    r = subprocess.run(['node', '-e', prog], capture_output=True, text=True)
    if r.returncode:
        print('✗ traslado: no corrió la regla de volver-auditor.js', r.stderr[:400])
        return 1
    nav = dict(zip(archivos, json.loads(r.stdout)))
    mal = [(f, py[f], nav[f]) for f in archivos if py[f] != nav[f]]
    for f, a, b in mal[:20]:
        print('✗ traslado: %s es %s en Python y %s en el navegador' % (f, a, b))
    cuenta = {}
    for f in archivos:
        d = dim_de(f)
        if d:
            cuenta[d] = cuenta.get(d, 0) + 1
    if mal:
        return 1
    print('✓ traslado: %d páginas al Planisferio (%s), la misma regla en Python y en el navegador'
          % (sum(cuenta.values()), ', '.join('%s %d' % kv for kv in sorted(cuenta.items()))))
    return 0


if __name__ == '__main__':
    if '--prueba' in sys.argv:
        sys.exit(prueba())
    print(json.dumps(js(), ensure_ascii=False, indent=1))
