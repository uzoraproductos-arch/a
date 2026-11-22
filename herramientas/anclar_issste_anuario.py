#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ancla los servicios médicos y la población derechohabiente del ISSSTE 2025
por entidad federativa desde el Anuario Estadístico 2025 del ISSSTE
(http://www.issste.gob.mx/datosabiertos/anuarios/anuarios2025.html).

Cuadros oficiales que integra (cada uno se cuadra contra su total nacional;
si difiere en una sola persona o evento, el script se detiene):
- 1.2_2025.xlsx: población derechohabiente, afiliada y usuaria por entidad
  federativa (más «En el extranjero»: 996 personas).
- 18.6_2025.xlsx: consultas externas por representación estatal.
- 22.1_2025.xlsx: egresos hospitalarios (propios + subrogados) por entidad.
- 23.5_2025.xlsx: urgencias reales y sentidas por representación estatal.
- 25.1_2025.xlsx: procedimientos quirúrgicos (propios + subrogados) por entidad.

Escribe docs/salud/issste-anuario-2025.json en LF puro. Idempotente.

Uso:
    python3 herramientas/anclar_issste_anuario.py <carpeta con los 5 ZIPs>
"""
import hashlib
import io
import json
import pathlib
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'docs' / 'salud' / 'issste-anuario-2025.json'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
URL_ANUARIO = 'http://www.issste.gob.mx/datosabiertos/anuarios/anuarios2025.html'
URL_BASE = 'https://www.issste.gob.mx/images/downloads/instituto/finanzas/anuarios/2025/'

ENT_ORDEN = [
    'AGS', 'BC', 'BCS', 'CAM', 'COAH', 'COL', 'CHIS', 'CHIH', 'CDMX', 'DGO',
    'GTO', 'GRO', 'HGO', 'JAL', 'MÉX', 'MICH', 'MOR', 'NAY', 'NL', 'OAX',
    'PUE', 'QRO', 'QROO', 'SLP', 'SIN', 'SON', 'TAB', 'TAM', 'TLAX', 'VER',
    'YUC', 'ZAC',
]

ENT_MAP = {
    'aguascalientes': 'AGS', 'baja california': 'BC', 'baja california sur': 'BCS',
    'campeche': 'CAM', 'coahuila': 'COAH', 'coahuila de zaragoza': 'COAH', 'colima': 'COL',
    'chiapas': 'CHIS', 'chihuahua': 'CHIH', 'ciudad de mexico': 'CDMX', 'durango': 'DGO',
    'guanajuato': 'GTO', 'guerrero': 'GRO', 'hidalgo': 'HGO', 'jalisco': 'JAL',
    'mexico': 'MÉX', 'estado de mexico': 'MÉX', 'michoacan': 'MICH', 'michoacan de ocampo': 'MICH',
    'morelos': 'MOR', 'nayarit': 'NAY', 'nuevo leon': 'NL', 'oaxaca': 'OAX',
    'puebla': 'PUE', 'queretaro': 'QRO', 'quintana roo': 'QROO', 'san luis potosi': 'SLP',
    'sinaloa': 'SIN', 'sonora': 'SON', 'tabasco': 'TAB', 'tamaulipas': 'TAM',
    'tlaxcala': 'TLAX', 'veracruz': 'VER', 'veracruz de ignacio de la llave': 'VER',
    'yucatan': 'YUC', 'zacatecas': 'ZAC',
}


def norm(s):
    s = unicodedata.normalize('NFD', str(s or ''))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'\s+', ' ', s).strip()


def read_xlsx(zpath, member):
    with zipfile.ZipFile(zpath) as z:
        data = z.read(member)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        sst = []
        if 'xl/sharedStrings.xml' in z.namelist():
            root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in root.findall('s:si', NS):
                sst.append(''.join(t.text or '' for t in si.findall('.//s:t', NS)))
        sheets = sorted([n for n in z.namelist() if n.startswith('xl/worksheets/sheet') and n.endswith('.xml')])
        root = ET.fromstring(z.read(sheets[0]))
        rows = []
        for row in root.findall('.//s:sheetData/s:row', NS):
            r = {}
            for c in row.findall('s:c', NS):
                ref = ''.join(ch for ch in (c.get('r') or '') if ch.isalpha())
                t = c.get('t')
                v = c.find('s:v', NS)
                if v is not None and v.text is not None:
                    r[ref] = sst[int(v.text)] if t == 's' else v.text
            if r:
                rows.append(r)
        return rows


def find_zip(carpeta, nombre):
    for cand in (carpeta / nombre, carpeta / ('issste2025_' + nombre)):
        if cand.exists():
            return cand
    raise SystemExit('anclar_issste_anuario: falta %s en %s' % (nombre, carpeta))


def main():
    if len(sys.argv) < 2:
        raise SystemExit('Uso: python3 herramientas/anclar_issste_anuario.py <carpeta_zips>')
    carpeta = pathlib.Path(sys.argv[1])
    zips = {
        'derechohabientes': ('01_Poblacion_derechohabiente.zip', '01 Población derechohabiente/1.2_2025.xlsx'),
        'consultas': ('18_Consulta_externa.zip', '18 Consulta externa/18.6_2025.xlsx'),
        'hospitalarios': ('22_Servicios_hospitalarios.zip', '22 Servicios hospitalarios/22.1_2025.xlsx'),
        'urgencias': ('23_Urgencias.zip', '23 Urgencias/23.5_2025.xlsx'),
        'cirugias': ('25_Procedimientos_quirurgicos.zip', '25 Procedimientos quirúrgicos/25.1_2025.xlsx'),
    }
    fuentes = {}
    parsed = {}
    for k, (zn, xf) in zips.items():
        zp = find_zip(carpeta, zn)
        b = zp.read_bytes()
        fuentes[k] = {
            'archivo': zn,
            'cuadro': xf,
            'url': URL_BASE + zn,
            'bytes': len(b),
            'sha256': hashlib.sha256(b).hexdigest(),
        }
        parsed[k] = read_xlsx(zp, xf)

    estados = {e: {} for e in ENT_ORDEN}
    extranjero = {}
    totales = {}

    # 1.2 Derechohabientes, afiliados, usuarios
    for r in parsed['derechohabientes']:
        a = norm(r.get('A'))
        if a == 'total':
            totales['derechohabientes'] = int(float(r['D']))
            totales['afiliados'] = int(float(r['G']))
            totales['usuarios'] = int(float(r['J']))
        elif a == 'en el extranjero':
            extranjero['derechohabientes'] = int(float(r['D']))
            extranjero['afiliados'] = int(float(r['G']))
        elif a in ENT_MAP:
            e = ENT_MAP[a]
            estados[e]['derechohabientes'] = int(float(r['D']))
            estados[e]['afiliados'] = int(float(r['G']))
            estados[e]['usuarios'] = int(float(r['J']))

    # 18.6 Consultas externas
    for r in parsed['consultas']:
        a = norm(r.get('A'))
        if a == 'total':
            totales['consultas'] = int(float(r['N']))
        elif a in ENT_MAP:
            estados[ENT_MAP[a]]['consultas'] = int(float(r['N']))

    # 22.1 Egresos hospitalarios (total = propios + subrogados, col Y)
    for r in parsed['hospitalarios']:
        a, b = norm(r.get('A')), norm(r.get('B'))
        if a == 'total' and b == 'total':
            totales['egresos'] = int(float(r['Y']))
        elif a in ENT_MAP and b == 'total':
            estados[ENT_MAP[a]]['egresos'] = int(float(r['Y']))

    # 23.5 Urgencias (reales col Z + sentidas col AA)
    for r in parsed['urgencias']:
        a = norm(r.get('A'))
        if a == 'total':
            totales['urgenciasReales'] = int(float(r['Z']))
            totales['urgenciasSentidas'] = int(float(r['AA']))
            totales['urgencias'] = totales['urgenciasReales'] + totales['urgenciasSentidas']
        elif a in ENT_MAP:
            e = ENT_MAP[a]
            estados[e]['urgenciasReales'] = int(float(r['Z']))
            estados[e]['urgenciasSentidas'] = int(float(r['AA']))
            estados[e]['urgencias'] = estados[e]['urgenciasReales'] + estados[e]['urgenciasSentidas']

    # 25.1 Procedimientos quirúrgicos (total col Q)
    for r in parsed['cirugias']:
        a, b = norm(r.get('A')), norm(r.get('B'))
        if a == 'total' and b == 'total':
            totales['cirugias'] = int(float(r['Q']))
        elif a in ENT_MAP and b == 'total':
            estados[ENT_MAP[a]]['cirugias'] = int(float(r['Q']))

    # Cuadres estrictos (AGENTS.md §2)
    checks = [
        ('derechohabientes', sum(v['derechohabientes'] for v in estados.values()) + extranjero.get('derechohabientes', 0), totales['derechohabientes']),
        ('afiliados', sum(v['afiliados'] for v in estados.values()) + extranjero.get('afiliados', 0), totales['afiliados']),
        ('usuarios', sum(v['usuarios'] for v in estados.values()), totales['usuarios']),
        ('consultas', sum(v['consultas'] for v in estados.values()), totales['consultas']),
        ('egresos', sum(v['egresos'] for v in estados.values()), totales['egresos']),
        ('urgenciasReales', sum(v['urgenciasReales'] for v in estados.values()), totales['urgenciasReales']),
        ('urgenciasSentidas', sum(v['urgenciasSentidas'] for v in estados.values()), totales['urgenciasSentidas']),
        ('cirugias', sum(v['cirugias'] for v in estados.values()), totales['cirugias']),
    ]
    for nombre, suma, tot in checks:
        if suma != tot:
            raise SystemExit('anclar_issste_anuario: %s no cuadra (%d vs %d)' % (nombre, suma, tot))

    salida = {
        'fuente': 'ISSSTE, Anuario Estadístico 2025 (DEISE-JSEI)',
        'url': URL_ANUARIO,
        'anio': 2025,
        'nota': ('Cada cifra proviene de los cuadros oficiales del Anuario Estadístico 2025 del ISSSTE. '
                 'Las 32 entidades suman exactamente el total nacional de cada cuadro '
                 '(en derechohabientes y afiliados se incluye el renglón oficial «En el extranjero»: 996 personas). '
                 'Las unidades de tercer nivel atienden también a derechohabientes de otras entidades.'),
        'fuentes': fuentes,
        'totales': totales,
        'extranjero': extranjero,
        'estados': estados,
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_bytes((json.dumps(salida, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print('issste-anuario-2025.json: 32 entidades cuadradas al 100 %% | DH=%s | consultas=%s | egresos=%s | urgencias=%s | cirugias=%s' % (
        format(totales['derechohabientes'], ','), format(totales['consultas'], ','),
        format(totales['egresos'], ','), format(totales['urgencias'], ','), format(totales['cirugias'], ',')))


if __name__ == '__main__':
    main()
