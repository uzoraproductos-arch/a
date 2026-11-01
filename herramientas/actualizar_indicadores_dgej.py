# -*- coding: utf-8 -*-
"""Baja y lee los Indicadores Estadísticos Judiciales de la DGEJ, por circuito
(pedido del autor, 01-11-2026: «productividad y litigiosidad de los tribunales
colegiados, unitarios, apelación y juzgados de distrito, con todos los
indicadores»).

La fuente es el sistema público de la Dirección General de Estadística
Judicial (Órgano de Administración Judicial), sin clave:
https://www.dgej.cjf.gob.mx/Indicadores/acuerd_nal_ini.asp
Por cada año, tipo de órgano y nivel (1 plantilla, 2 perfil, 3 litigiosidad,
4 acceso tecnológico, 5 productividad, 6 incidencia)
la página resumen trae los cinco primeros lugares y una liga «Ver todos los
circuitos» por indicador; esa liga da el valor de los 32 circuitos y el total
nacional. Lo que el sistema anuncia y no trae (los niveles 1, 2, 4 y 6 completos,
y algunos indicadores de 3 y 5) se guarda en «vacios». Se guarda todo, con la huella SHA-256 de cada página, en
docs/estadistica/dgej-indicadores-circuito.json, que lee
herramientas/indicadores_circuito.py.

Uso:
  python3 herramientas/actualizar_indicadores_dgej.py --certs paquete.pem
  python3 herramientas/actualizar_indicadores_dgej.py --desde carpeta   # copias ya bajadas

Certificados: www.dgej.cjf.gob.mx usa la raíz nueva de Let's Encrypt (ISRG
Root YR). Agrega al paquete de tu sistema el certificado cruzado
root-yr-by-x1.pem de letsencrypt.org/certificates; nunca apagues la
verificación.
"""

import argparse
import hashlib
import html
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.error
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, '..', 'docs', 'estadistica', 'dgej-indicadores-circuito.json')
BASE = 'https://www.dgej.cjf.gob.mx/Indicadores/'
ANOS = ['2021', '2022', '2023', '2024', '2025']
ORGANOS = {'2': 'Juzgados de Distrito', '3': 'Tribunales Unitarios de Circuito',
           '4': 'Tribunales Colegiados de Circuito', '340': 'Tribunales Colegiados de Apelación'}
NIVELES = {'1': 'Plantilla judicial', '2': 'Perfil de magistrados y jueces', '3': 'Litigiosidad', '4': 'Acceso tecnológico',
           '5': 'Productividad', '6': 'Incidencia'}


ERROR_SERVIDOR = b'error occurred on the server'


def resumen_url(ano, torid, nivel):
    # Así lo arma acuerd_nal_ini.asp: productividad tiene una página por tipo
    # de órgano, y la de apelación usa la de unitarios.
    pag = '(%s)' % nivel if nivel in '1234' else '(%s-%s)' % (nivel, '3' if torid == '340' else torid)
    return BASE + 'IndicadoresJudiciales%s.asp?torid=%s&ano=%s&nivel=%s&titulo=X' % (pag, torid, ano, nivel)


def _txt(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def _limpia(raw):
    s = raw.decode('latin-1')
    s = re.sub(r'<script.*?</script>', '', s, flags=re.S)
    return re.sub(r'<!--.*?-->', '', s, flags=re.S)


def lee_resumen(raw):
    """Las ligas «Ver todos los circuitos» y la definición de cada indicador."""
    s = _limpia(raw)
    ligas = re.findall(r'href="(IndicadoresJudicialesCircuito\.asp\?[^"]+)"', s)
    defs = [_txt(d) for d in re.findall(r'<td bgcolor="#FFFFFF" colspan="3"[^>]*>(.*?)</td>', s, flags=re.S | re.I)]
    defs = [d for d in defs if d]
    out = []
    for i, l in enumerate(ligas):
        q = dict(urllib.parse.parse_qsl(html.unescape(l).split('?', 1)[1], encoding='latin-1'))
        out.append((q, defs[i] if len(defs) == len(ligas) else ''))
    return out


def lee_circuitos(raw):
    s = _limpia(raw)
    vals = {}
    for m in re.finditer(r'circuito=(\d+)&[^>]*><strong>(.*?)</strong>.*?<font[^>]*>\s*([-\d.,]+)\s*</font>', s, flags=re.S):
        vals[m.group(1)] = float(m.group(3).replace(',', ''))
    m = re.search(r'TOTAL NACIONAL.*?<font[^>]*>\s*([-\d.,]+)\s*</font>', s, flags=re.S)
    return vals, (float(m.group(1).replace(',', '')) if m else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--certs', help='paquete de certificados con la raíz ISRG Root YR')
    ap.add_argument('--desde', help='carpeta con copias: AAAA_torid_nivel.html y circ/AAAA_torid_nivel_ind.html')
    a = ap.parse_args()
    ctx = ssl.create_default_context(cafile=a.certs) if a.certs else ssl.create_default_context()

    def baja(url, local):
        if a.desde:
            with open(os.path.join(a.desde, local), 'rb') as f:
                return f.read()
        time.sleep(0.3)
        with urllib.request.urlopen(url, context=ctx, timeout=60) as r:
            return r.read()

    datos, vacios, avisos, previo = [], {}, [], {}
    for ano in ANOS:
        for torid in ORGANOS:
            for nivel in NIVELES:
                url_res = resumen_url(ano, torid, nivel)
                try:
                    raw_res = baja(url_res, '%s_%s_%s.html' % (ano, torid, nivel))
                except urllib.error.HTTPError as e:
                    raw_res = b'error occurred on the server (HTTP %d)' % e.code
                lista = lee_resumen(raw_res)
                if ERROR_SERVIDOR in raw_res:
                    # La página que enlista los indicadores se cae a la mitad
                    # (JD 2023, productividad: error 500 tras el indicador 17).
                    # Los cuadros sí existen: se piden con la lista del año
                    # anterior y se deja dicho.
                    ya = {q['indicador'] for q, _ in lista}
                    extra = [(dict(q, ano=ano), d) for q, d in previo.get((torid, nivel), []) if q['indicador'] not in ya]
                    lista += extra
                    avisos.append({'ano': ano, 'org': torid, 'niv': nivel, 'url': url_res,
                                   'texto': 'La página resumen del sistema da error del servidor; %d cuadros se pidieron directo con la lista de %s.'
                                            % (len(extra), str(int(ano) - 1))})
                else:
                    previo[(torid, nivel)] = lista
                for q, defi in lista:
                    ind = q['indicador']
                    url = BASE + 'IndicadoresJudicialesCircuito.asp?' + urllib.parse.urlencode(q, encoding='latin-1')
                    raw = baja(url, 'circ/%s_%s_%s_%s.html' % (ano, torid, nivel, ind))
                    vals, nac = lee_circuitos(raw)
                    if not vals and nac is None:
                        # El sistema anuncia el indicador pero no trae valores.
                        v = vacios.setdefault((torid, nivel, int(ind)), {'org': torid, 'niv': nivel, 'ind': int(ind), 'nombre': q['nombre'].strip(),
                                                                          'defi': defi, 'anos': []})
                        v['anos'].append(ano)
                        continue
                    datos.append({'ano': ano, 'org': torid, 'niv': nivel, 'ind': int(ind), 'nombre': q['nombre'].strip(),
                                  'defi': defi, 'nac': nac, 'c': vals, 'url': url, 'sha256': hashlib.sha256(raw).hexdigest()})
    datos.sort(key=lambda x: (x['org'], x['niv'], x['ind'], x['ano']))
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump({'fuente': BASE + 'acuerd_nal_ini.asp', 'consulta': time.strftime('%d-%m-%Y'), 'organos': ORGANOS,
                   'niveles': NIVELES, 'datos': datos, 'avisos': avisos,
                   'vacios': sorted(vacios.values(), key=lambda x: (x['org'], x['niv'], x['ind']))}, f, ensure_ascii=False, separators=(',', ':'))
        f.write('\n')
    print('indicadores DGEJ: %d cuadros con datos y %d indicadores vacíos -> %s' % (len(datos), len(vacios), os.path.relpath(SALIDA)))


if __name__ == '__main__':
    sys.exit(main())
