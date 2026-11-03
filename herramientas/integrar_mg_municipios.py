# -*- coding: utf-8 -*-
"""Los límites de los municipios de una entidad, del Marco Geoestadístico del
INEGI, para el Planisferio (pedido del autor, 03-11-2026: «sigue con el mapa
de los municipios de Jalisco»).

Se corre a mano, una entidad a la vez, con el archivo que publica el INEGI
(Marco Geoestadístico 2024, versión por área geoestadística estatal):

    pip install pyshp          # solo para este script; la generación no lo usa
    curl -O https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/marcogeo/794551132173/14_jalisco.zip
    python3 herramientas/integrar_mg_municipios.py 14_jalisco.zip

Lee la capa de municipios (conjunto_de_datos/<ent>mun.shp), en la proyección
cónica conforme de Lambert del propio INEGI (EPSG:6372), quita los vértices
que no se notan a la escala del portal (Douglas-Peucker, 400 m) y escribe
docs/geo/mg2024-mun-<ent>.json: un trazo SVG por municipio, en kilómetros,
con la huella SHA-256 del archivo de origen. planisferio.py lo lee al
generar; si las claves no coinciden con el padrón del INEGI, se detiene.

Lo que el INEGI advierte, y la página repite: estos límites son
geoestadísticos (para referenciar censos y encuestas) y no son la fuente
oficial de la división político-administrativa del país.
"""
import hashlib
import io
import json
import math
import os
import sys
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = ('https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/'
       'marcogeo/794551132173/%s')
TOL_KM = 0.4           # vértice que se aleja menos de 400 m de la línea, fuera
MIN_KM2 = 0.5          # islotes de menos de medio kilómetro cuadrado, fuera


def _dp(pts, tol):
    """Douglas-Peucker iterativo (los anillos del INEGI pasan de 10 mil puntos)."""
    if len(pts) < 4:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    pila = [(0, len(pts) - 1)]
    while pila:
        i, j = pila.pop()
        (x1, y1), (x2, y2) = pts[i], pts[j]
        dx, dy = x2 - x1, y2 - y1
        largo = math.hypot(dx, dy)
        peor, k = -1.0, None
        for m in range(i + 1, j):
            x, y = pts[m]
            d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / largo if largo else math.hypot(x - x1, y - y1)
            if d > peor:
                peor, k = d, m
        if k is not None and peor > tol:
            keep[k] = True
            pila += [(i, k), (k, j)]
    return [p for p, q in zip(pts, keep) if q]


def _area(pts):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))) / 2


def integrar(ruta_zip):
    import shapefile  # pyshp
    datos = open(ruta_zip, 'rb').read()
    huella = hashlib.sha256(datos).hexdigest()
    z = zipfile.ZipFile(io.BytesIO(datos))
    shp = [n for n in z.namelist() if n.startswith('conjunto_de_datos/') and n.endswith('mun.shp')]
    if len(shp) != 1:
        raise SystemExit('integrar_mg_municipios: no encuentro la capa de municipios en %s' % ruta_zip)
    base = shp[0][:-4]
    meta = next((z.read(n).decode('latin-1') for n in z.namelist() if n.startswith('metadatos/')), '')
    if 'Marco Geoestad' not in meta or '2024' not in meta:
        raise SystemExit('integrar_mg_municipios: el archivo no dice ser el Marco Geoestadístico 2024')
    r = shapefile.Reader(shp=io.BytesIO(z.read(base + '.shp')), shx=io.BytesIO(z.read(base + '.shx')),
                         dbf=io.BytesIO(z.read(base + '.dbf')), encoding='latin-1')
    x0, y0, x1, y1 = r.bbox
    ent = None
    muns = []
    for sr in r.iterShapeRecords():
        rec = sr.record.as_dict()
        ent = ent or rec['CVE_ENT']
        pts, partes = sr.shape.points, list(sr.shape.parts) + [len(sr.shape.points)]
        anillos = []
        for a, b in zip(partes, partes[1:]):
            # A kilómetros, con el norte arriba (y del SVG crece hacia abajo).
            anillo = [((x - x0) / 1000, (y1 - y) / 1000) for x, y in pts[a:b]]
            if _area(anillo) < MIN_KM2:
                continue
            s = _dp(anillo, TOL_KM)
            if len(s) >= 4:
                anillos.append(s)
        if not anillos:
            raise SystemExit('integrar_mg_municipios: %s se quedó sin trazo' % rec['NOMGEO'])
        d = ''.join('M' + 'L'.join('%.1f %.1f' % p for p in s[:-1]) + 'Z' for s in anillos)
        muns.append({'c': rec['CVE_MUN'], 'n': rec['NOMGEO'], 'd': d})
    muns.sort(key=lambda m: m['c'])
    salida = {
        'fuente': 'INEGI, Marco Geoestadístico 2024 (versión por área geoestadística estatal), capa de áreas geoestadísticas municipales',
        'url': URL % os.path.basename(ruta_zip), 'pagina': 'https://www.inegi.org.mx/temas/mg/',
        'licencia': 'Términos de Libre Uso de la Información del INEGI (https://www.inegi.org.mx/inegi/terminos.html)',
        'sha256': huella, 'bytes': len(datos), 'integrado': '03-11-2026',
        'proyeccion': 'Cónica conforme de Lambert del INEGI (EPSG:6372), en kilómetros; simplificada a %d m' % (TOL_KM * 1000),
        'aviso': ('El INEGI advierte que estos límites son geoestadísticos, para referenciar censos y encuestas, y que no deben '
                  'tomarse como la fuente oficial de la división político-administrativa del país.'),
        'ent': ent, 'vb': [round((x1 - x0) / 1000, 1), round((y1 - y0) / 1000, 1)], 'm': muns,
    }
    os.makedirs(os.path.join(RAIZ, 'docs', 'geo'), exist_ok=True)
    destino = os.path.join(RAIZ, 'docs', 'geo', 'mg2024-mun-%s.json' % ent)
    open(destino, 'w', encoding='utf-8').write(json.dumps(salida, ensure_ascii=False, separators=(',', ':')) + '\n')
    print('integrar_mg_municipios: %d municipios de la entidad %s en %s (%d KB; origen SHA-256 %s…)' % (
        len(muns), ent, os.path.relpath(destino, RAIZ), os.path.getsize(destino) // 1024, huella[:12]))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    integrar(sys.argv[1])
