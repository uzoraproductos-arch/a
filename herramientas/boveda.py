#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La bóveda de evidencias (paso 2.2 del plan v2, 27-10-2026).

Un cotejo que dice «consta» vale lo que vale su documento, y los documentos
oficiales cambian de dirección, se corrigen o se retiran. La bóveda guarda,
por cada dirección que respalda un dato de la plataforma, la prueba de qué
había ahí y cuándo: la huella SHA-256 del archivo, su tamaño, su tipo y la
fecha en que se consultó. Si un día la huella cambia, la anterior se queda en
el historial: así se sabe que el documento se modificó después del cotejo.

No guarda los archivos en el repositorio (ya pesa demasiado): solo su ficha,
en docs/boveda/evidencias.json. Con --descargas CARPETA conserva además una
copia local de cada archivo, nombrada por su huella, para subirla después al
almacenamiento «boveda» de Supabase (migración 20261027000001).

Qué direcciones revisa:
  - las de la Biblioteca (referencias_legales de audit-database.js);
  - las de Verificamos (columnas.js): cotejos que dicen «consta» o «matiz»,
    cifras y fuentes;
  - las fuentes de las investigaciones de Auditoría en imágenes
    (auditorias_actuales).

Uso (solo Python estándar: funciona igual en Windows):
    python3 herramientas/boveda.py                 # copia lo que falta
    python3 herramientas/boveda.py --todas         # vuelve a revisar todo
    python3 herramientas/boveda.py --url URL       # una sola dirección
    python3 herramientas/boveda.py --archivo       # pide copia a archive.org
    python3 herramientas/boveda.py --descargas C   # guarda los archivos en C
    python3 herramientas/boveda.py --sin-copia URL --motivo "..."
        Anota a mano un documento que no abre desde donde corres el script
        (por ejemplo, energy.gov desde la nube) y cómo se cotejó.
    python3 herramientas/boveda.py --revisa        # solo dice qué falta
    python3 herramientas/boveda.py --subir C       # manda fichas y archivos de C a Supabase
        Lee SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY del entorno: la llave de
        servicio nunca se escribe en un archivo ni se pega en un chat.

Una dirección que no abrió se anota con el error, nunca con una huella
inventada; --revisa la cuenta como pendiente de copia.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
COLUMNAS = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'columnas.js')
SALIDA = os.path.join(RAIZ, 'docs', 'boveda', 'evidencias.json')
AGENTE = 'Mozilla/5.0 (compatible; Auditavision-boveda/1.0; +https://uzoraproductos-arch.github.io/a/)'
LIMITE = 80 * 1024 * 1024  # un PDF de la Cuenta Pública rara vez pasa de esto
RES_CON_PRUEBA = ('consta', 'matiz')


def hoy():
    return datetime.date.today().isoformat()


def _json_de(ruta, marca):
    s = open(ruta, encoding='utf-8').read()
    i = s.index(marca) + len(marca)
    return json.JSONDecoder().raw_decode(s[i:])[0]


def direcciones():
    """{url: [usos]}: cada dirección y dónde la usa la plataforma."""
    usos = {}

    def anota(url, uso):
        if url and re.match(r'^https?://', url):
            usos.setdefault(url.strip(), set()).add(uso)

    s = open(DB, encoding='utf-8').read()
    db = json.loads(s[s.index('{'):s.rindex('}') + 1])
    for r in db.get('referencias_legales', []):
        anota(r.get('url'), 'biblioteca:%s' % r['id'])
    for cid, a in (db.get('auditorias_actuales') or {}).items():
        for f in a.get('fuentes', []):
            anota(f.get('url'), 'auditoria:%s' % cid)
    for c in _json_de(COLUMNAS, 'var COLUMNAS = '):
        for n, x in enumerate(c.get('cotejo', [])):
            if x.get('res') in RES_CON_PRUEBA:
                anota(x.get('url'), 'cotejo:%s:%d' % (c['id'], n))
        for x in c.get('cifras', []):
            anota(x.get('url'), 'cifra:%s' % c['id'])
        for x in c.get('fuentes', []):
            anota(x.get('url'), 'fuente:%s' % c['id'])
    return {u: sorted(v) for u, v in usos.items()}


def cotejos_con_prueba():
    """[(columna, qué, url)] de lo que afirma algo con un documento: los
    cotejos «consta» o «matiz» y las cifras «oficial» de Verificamos."""
    out = []
    for c in _json_de(COLUMNAS, 'var COLUMNAS = '):
        for n, x in enumerate(c.get('cotejo', [])):
            if x.get('res') in RES_CON_PRUEBA:
                out.append((c['id'], 'cotejo %d' % n, x.get('url') or ''))
        for x in c.get('cifras', []):
            if x.get('estado') == 'oficial':
                out.append((c['id'], 'cifra «%s»' % x.get('valor'), x.get('url') or ''))
    return out


def cargar():
    if os.path.exists(SALIDA):
        return json.load(open(SALIDA, encoding='utf-8'))
    return {'nota': ('Bóveda de evidencias de Auditavisión: la huella de cada documento que respalda un dato. '
                     'La genera herramientas/boveda.py; no se edita a mano.'), 'evidencias': {}}


def guardar(b):
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    b['evidencias'] = dict(sorted(b['evidencias'].items()))
    with open(SALIDA, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(b, f, ensure_ascii=False, indent=1)
        f.write('\n')


def bajar(url):
    """(bytes, tipo, http) o lanza la excepción del intento."""
    req = urllib.request.Request(url, headers={'User-Agent': AGENTE, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=60) as r:
        datos = r.read(LIMITE + 1)
        if len(datos) > LIMITE:
            raise ValueError('pasa de %d MB; se omite' % (LIMITE // 1048576))
        return datos, (r.headers.get('Content-Type') or '').split(';')[0].strip(), r.status


def pedir_archivo(url):
    """Pide a archive.org una copia; devuelve su dirección o None."""
    try:
        req = urllib.request.Request('https://web.archive.org/save/' + url, headers={'User-Agent': AGENTE})
        with urllib.request.urlopen(req, timeout=120) as r:
            loc = r.headers.get('Content-Location') or ''
            return ('https://web.archive.org' + loc) if loc.startswith('/web/') else r.geturl()
    except Exception:
        return None


def revisar(b, url, usos, descargas=None, archivo=False):
    e = b['evidencias'].get(url) or {'primera_vez': hoy(), 'historial': []}
    e['usos'] = usos
    e['consultado'] = hoy()
    try:
        datos, tipo, http = bajar(url)
    except Exception as x:  # se anota el error tal cual, sin huella
        e['estado'] = 'no abrió'
        e['error'] = (getattr(x, 'reason', None) and str(x.reason)) or str(x)
        e['error'] = e['error'][:160]
        b['evidencias'][url] = e
        return e
    h = hashlib.sha256(datos).hexdigest()
    if e.get('sha256') and e['sha256'] != h:
        # El documento cambió desde el último cotejo: la huella vieja se queda.
        e['historial'].append({'sha256': e['sha256'], 'bytes': e.get('bytes'), 'hasta': e.get('copiado')})
    e.update({'estado': 'copiado', 'sha256': h, 'bytes': len(datos), 'tipo': tipo, 'http': http, 'copiado': hoy()})
    e.pop('error', None)
    if descargas:
        os.makedirs(descargas, exist_ok=True)
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1][:6].lower()
        ext = ext if re.fullmatch(r'\.[a-z0-9]{1,5}', ext) else '.bin'
        ruta = os.path.join(descargas, h + ext)
        if not os.path.exists(ruta):
            with open(ruta, 'wb') as f:
                f.write(datos)
    if archivo and not e.get('archive_org'):
        e['archive_org'] = pedir_archivo(url)
    b['evidencias'][url] = e
    return e


def sin_copia(b, url, motivo, usos):
    if len(motivo.strip()) < 20:
        raise SystemExit('boveda.py: el motivo debe decir cómo se cotejó (20 caracteres o más)')
    e = b['evidencias'].get(url) or {'primera_vez': hoy(), 'historial': []}
    if e.get('estado') == 'copiado':
        raise SystemExit('boveda.py: esa dirección ya tiene copia con huella; no se rebaja a «sin copia»')
    e.update({'estado': 'sin copia', 'motivo': motivo.strip(), 'consultado': hoy(), 'usos': usos})
    b['evidencias'][url] = e


def faltantes(b):
    """Cotejos «consta» o «matiz» cuyo documento no tiene huella ni motivo."""
    ev = b['evidencias']
    out = []
    for col, n, url in cotejos_con_prueba():
        e = ev.get(url)
        if not url or not e or e.get('estado') == 'no abrió':
            out.append((col, n, url, (e or {}).get('error', 'sin ficha en la bóveda')))
    return out


def subir(b, carpeta):
    """Manda a Supabase los documentos copiados: el archivo al almacenamiento
    «boveda» (nombrado por su huella) y su ficha a public.evidencias. Lo que ya
    está no se toca: la base rechaza corregir una huella."""
    base = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    llave = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or ''
    if not (base.startswith('https://') or base.startswith('http://127.0.0.1')) or not llave:
        raise SystemExit('boveda.py: faltan SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY en el entorno')
    cab = {'apikey': llave, 'Authorization': 'Bearer ' + llave, 'User-Agent': AGENTE}
    archivos = {os.path.splitext(f)[0]: f for f in os.listdir(carpeta)} if carpeta and os.path.isdir(carpeta) else {}
    filas, subidos = [], 0
    for url, e in sorted(b['evidencias'].items()):
        if e.get('estado') != 'copiado':
            continue
        ruta = archivos.get(e['sha256'])
        if ruta:
            datos = open(os.path.join(carpeta, ruta), 'rb').read()
            if hashlib.sha256(datos).hexdigest() != e['sha256']:
                raise SystemExit('boveda.py: %s no coincide con su huella; no se sube' % ruta)
            req = urllib.request.Request('%s/storage/v1/object/boveda/%s' % (base, ruta), data=datos, method='POST',
                                         headers=dict(cab, **{'Content-Type': e.get('tipo') or 'application/octet-stream'}))
            try:
                urllib.request.urlopen(req, timeout=120).read()
                subidos += 1
            except urllib.error.HTTPError as x:
                if x.code not in (400, 409):  # 409 (o 400 «Duplicate»): ya estaba
                    raise
        filas.append({'url': url, 'sha256': e['sha256'], 'bytes': e['bytes'], 'tipo': e.get('tipo') or None,
                      'copiado': e['copiado'], 'ruta': ruta, 'archive_org': e.get('archive_org'), 'usos': e.get('usos', [])})
        for h in e.get('historial', []):  # las huellas viejas también, si se conocen
            if h.get('sha256') and h.get('bytes') and h.get('hasta'):
                filas.append({'url': url, 'sha256': h['sha256'], 'bytes': h['bytes'], 'tipo': None,
                              'copiado': h['hasta'], 'ruta': None, 'archive_org': None, 'usos': e.get('usos', [])})
    for i in range(0, len(filas), 200):
        req = urllib.request.Request('%s/rest/v1/evidencias?on_conflict=url,sha256' % base, method='POST',
                                     data=json.dumps(filas[i:i + 200]).encode('utf-8'),
                                     headers=dict(cab, **{'Content-Type': 'application/json',
                                                          'Prefer': 'resolution=ignore-duplicates,return=minimal'}))
        urllib.request.urlopen(req, timeout=120).read()
    print('bóveda: %d fichas enviadas a public.evidencias, %d archivos nuevos en el almacenamiento' % (len(filas), subidos))


def resumen(b):
    c = {}
    for e in b['evidencias'].values():
        c[e.get('estado')] = c.get(e.get('estado'), 0) + 1
    return ', '.join('%d %s' % (v, k) for k, v in sorted(c.items()))


def main(argv=None):
    ap = argparse.ArgumentParser(description='Bóveda de evidencias de Auditavisión')
    ap.add_argument('--todas', action='store_true', help='vuelve a revisar también lo ya copiado')
    ap.add_argument('--url', help='revisa solo esta dirección')
    ap.add_argument('--archivo', action='store_true', help='pide copia a archive.org')
    ap.add_argument('--descargas', help='carpeta donde guardar los archivos (fuera del repositorio)')
    ap.add_argument('--sin-copia', dest='sin_copia', help='anota a mano una dirección que no abre')
    ap.add_argument('--motivo', default='', help='cómo se cotejó lo que no abrió')
    ap.add_argument('--revisa', action='store_true', help='solo informa; sale con 1 si un cotejo no tiene evidencia')
    ap.add_argument('--subir', metavar='CARPETA', help='manda fichas y archivos de CARPETA a Supabase')
    a = ap.parse_args(argv)

    b = cargar()
    dirs = direcciones()
    if a.revisa:
        f = faltantes(b)
        print('bóveda: %d direcciones en uso, %s' % (len(dirs), resumen(b) or 'ninguna revisada'))
        duros = [x for x in f if x[1].startswith('cotejo')]
        for col, n, url, err in f:
            print('  %s: %s de %s → %s (%s)' % ('FALTA' if n.startswith('cotejo') else 'aviso', n, col, url, err[:80]))
        # Un cotejo «consta» o «matiz» sin evidencia detiene; una cifra
        # oficial sin copia es aviso hasta que se copie desde una
        # computadora donde su sitio abra (muchos no abren desde la nube).
        return 1 if duros else 0
    if a.subir:
        subir(b, a.subir)
        return 0
    if a.sin_copia:
        sin_copia(b, a.sin_copia, a.motivo, dirs.get(a.sin_copia, []))
        guardar(b)
        print('bóveda: anotada sin copia %s' % a.sin_copia)
        return 0
    lista = [a.url] if a.url else sorted(dirs)
    hechas = 0
    for url in lista:
        e = b['evidencias'].get(url)
        if not a.todas and not a.url and e and e.get('estado') in ('copiado', 'sin copia'):
            continue
        r = revisar(b, url, dirs.get(url, []), a.descargas, a.archivo)
        hechas += 1
        print('  %-9s %s%s' % (r['estado'], url[:110], ('  · ' + r['error']) if r.get('error') else ''))
        if hechas % 10 == 0:
            guardar(b)  # que un corte de red no tire lo ya revisado
        time.sleep(0.3)
    # Lo que ya no se usa se queda: la bóveda es memoria, no un espejo.
    guardar(b)
    print('bóveda: %d revisadas ahora; en total %s' % (hechas, resumen(b)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
