#!/usr/bin/env python3
"""Ancla el Índice SHF de Precios de la Vivienda en México (Sociedad Hipotecaria Federal).

Uso (a mano, cada trimestre; se bajan los dos archivos de la página de documentos de la SHF):

    python3 herramientas/anclar_shf_vivienda.py I_ndice_SHF_T3_2026.pdf Indice_SHF_datos_abiertos_3_trim_2026.xlsx

Escribe docs/vivienda/shf-precios-vivienda.json con:
  - la distribución de los precios de 2026 por entidad (precio medio y cuartiles, pesos corrientes),
    tal como la publica el informe (su cuadro «Distribución de los precios…»);
  - el índice de cada entidad y de cada municipio seleccionado en el trimestre del corte y en el
    mismo trimestre del año anterior, de los datos abiertos;
  - la huella SHA-256 de los dos archivos.

Cuadre (si no cuadra, se detiene): la variación anual que sale de los datos abiertos, redondeada a un
decimal, debe ser la que publica el informe para cada entidad y cada municipio, con 0.1 puntos de holgura (los datos
abiertos traen el índice con dos decimales y el informe calcula con todos; se guarda la del informe); y el cuadro de precios
debe traer las 32 entidades y el país, con el cuartil 25 % ≤ mediana ≤ cuartil 75 %.

Se corre con pdftotext (poppler) y openpyxl. Lo que estos números son y no son lo dice cc_predial.py:
el índice sale de avalúos de vivienda y no es el valor de ningún predio en particular.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'vivienda', 'shf-precios-vivienda.json')
PAGINA = 'https://www.gob.mx/shf/documentos/indice-shf-de-precios-de-la-vivienda-en-mexico-2025-a-2026'
ADJ = 'https://www.gob.mx/cms/uploads/attachment/file/'
# El número de adjunto lo da la página de documentos de la SHF; cambia con cada trimestre.
URLS = {'I_ndice_SHF_T3_2026.pdf': ADJ + '1115355/I_ndice_SHF_T3_2026.pdf',
        'Indice_SHF_datos_abiertos_3_trim_2026.xlsx': ADJ + '1115356/Indice_SHF_datos_abiertos_3_trim_2026.xlsx'}
METODO = {'url': ADJ + '1100172/Nota_metodol_gica_del__ndice_SHF_de_Precios_de_la_Vivienda_en_M_xico.pdf',
          'sha256': 'd88bc982ab84b3a759480ff1c1bf02056297d445db92363514498ff7b45d373a',
          'cita': '«El IPV es un indicador que mide los cambios en la valoración económica de las propiedades inmuebles. '
                  'Las características de los avalúos evolucionan con el tiempo, por lo que los precios tienen que ser '
                  'ajustados por los cambios en su calidad.»'}
ENTIDADES = ['Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche', 'Coahuila', 'Colima', 'Chiapas',
             'Chihuahua', 'Ciudad de México', 'Durango', 'Guanajuato', 'Guerrero', 'Hidalgo', 'Jalisco', 'México',
             'Michoacán', 'Morelos', 'Nayarit', 'Nuevo León', 'Oaxaca', 'Puebla', 'Querétaro', 'Quintana Roo',
             'San Luis Potosí', 'Sinaloa', 'Sonora', 'Tabasco', 'Tamaulipas', 'Tlaxcala', 'Veracruz', 'Yucatán', 'Zacatecas']


def huella(ruta):
    with open(ruta, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def pagina(pdf, p):
    return subprocess.run(['pdftotext', '-layout', '-f', str(p), '-l', str(p), pdf, '-'],
                          capture_output=True, text=True, check=True).stdout


def num(t):
    return float(t.replace(',', ''))


def ultimo_por_nombre(texto, nombres):
    """Para cada nombre, el último número de su renglón (la variación del trimestre del corte)."""
    out = {}
    for ln in texto.splitlines():
        m = re.match(r'\s*([A-Za-zÁÉÍÓÚÑáéíóúñü .]+?)\d?(?:\s*\([^)]*\))?\s{2,}(-?[\d.]+(?:\s+-?[\d.]+)*)\s*$', ln)
        if not m:
            continue
        n = m.group(1).strip()
        if n in nombres:
            out.setdefault(n, []).append(float(m.group(2).split()[-1]))
    return out


def main(pdf, xlsx):
    import openpyxl
    errores = []
    # 1. El cuadro de precios: la página que lo trae.
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout).group(1))
    pag = next(p for p in range(1, n + 1) if 'Precio Medio' in pagina(pdf, p))
    txt = pagina(pdf, pag)
    tit = re.search(r'(Distribución de los precios[^\n]*?\d{4})', txt).group(1).strip()
    precios = {}
    for ln in txt.splitlines():
        m = re.match(r'\s*([A-Za-zÁÉÍÓÚÑáéíóú ]+?)\s{2,}([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$', ln)
        if m and m.group(1).strip() in ENTIDADES + ['Nacional']:
            precios[m.group(1).strip()] = {'medio': num(m.group(2)), 'p25': num(m.group(3)),
                                           'p50': num(m.group(4)), 'p75': num(m.group(5))}
    if len(precios) != 33:
        errores.append('el cuadro de precios trae %d renglones, no 33: %s' % (len(precios), sorted(set(ENTIDADES + ['Nacional']) - set(precios))))
    for k, v in precios.items():
        if not v['p25'] <= v['p50'] <= v['p75']:
            errores.append('%s: los cuartiles no van en orden' % k)

    # 2. Los índices de los datos abiertos.
    ws = openpyxl.load_workbook(xlsx, read_only=True).active
    cab = [c for c in next(ws.iter_rows(max_row=1, values_only=True))]
    if cab != ['Consecutivo', 'Global', 'Estado', 'Municipio', 'Trimestre', 'Año', 'Indice']:
        sys.exit('Cambiaron las columnas de los datos abiertos: %r' % cab)
    filas = list(ws.iter_rows(min_row=2, values_only=True))
    a, t = max((r[5], r[4]) for r in filas)
    idx = {}
    for r in filas:
        if (r[5], r[4]) in ((a, t), (a - 1, t)):
            clave = (r[1] or '').strip() if not r[2] else r[2].strip() + ('|' + r[3].strip() if r[3] else '')
            idx.setdefault(clave, {})['i' if r[5] == a else 'i0'] = r[6]

    # 3. Cuadre contra las variaciones que publica el informe.
    def var(c):
        return round((idx[c]['i'] / idx[c]['i0'] - 1) * 100 + 1e-9, 1)
    pe = next(p for p in range(1, n + 1) if 'Ciudad de México' in pagina(pdf, p) and re.search(r'Jalisco\s+[\d.]+\s+[\d.]+', pagina(pdf, p))
              and max(float(x) for x in re.findall(r'Jalisco\s+(.*)', pagina(pdf, p))[0].split()) < 30)
    ve = ultimo_por_nombre(pagina(pdf, pe), set(ENTIDADES))
    munis = sorted(c for c in idx if '|' in c)
    nm = set(c.split('|')[1] for c in munis)
    vm = {}
    for p in range(pe + 1, n + 1):
        tx = pagina(pdf, p)
        if 'municipios' in tx and 'Precio Medio' not in tx:
            vals = ultimo_por_nombre(tx, nm)
            if vals and all(v < 30 for vs in vals.values() for v in vs):
                vm = vals
                pm = p
                break
    estados = {}
    for e in ENTIDADES:
        if e not in idx:
            errores.append('%s: sin índice en los datos abiertos' % e)
            continue
        pub = ve.get(e, [None])[0]
        if pub is None or abs(var(e) - pub) > 0.1 + 1e-9:
            errores.append('%s: la variación de los datos abiertos (%s) no es la del informe (%s)' % (e, var(e), pub))
        estados[e] = {'i': idx[e]['i'], 'i0': idx[e]['i0'], 'var': pub, 'precios': precios.get(e)}
    municipios = []
    for c in munis:
        e, m = c.split('|')
        pubs = [v for v in vm.get(m, []) if abs(var(c) - v) <= 0.1 + 1e-9]
        if not pubs:
            errores.append('%s, %s: la variación de los datos abiertos (%s) no está entre las del informe (%s)' % (m, e, var(c), vm.get(m)))
            continue
        municipios.append({'ent': e, 'nombre': m, 'i': idx[c]['i'], 'i0': idx[c]['i0'], 'var': min(pubs, key=lambda v: abs(v - var(c)))})
    if errores:
        sys.exit('No cuadra; no se escribe nada:\n  ' + '\n  '.join(errores))

    salida = {
        'fuente': 'Sociedad Hipotecaria Federal (SHF), Índice SHF de Precios de la Vivienda en México',
        'pagina': PAGINA, 'metodo': METODO, 'corte': '%dT %d' % (t, a), 'anio': a, 'trim': t,
        'informe': {'url': URLS.get(os.path.basename(pdf), PAGINA), 'sha256': huella(pdf),
                    'precios_pag': pag, 'precios_tit': tit, 'var_pag_ent': pe, 'var_pag_mun': pm,
                    'nota': 'Cifras preliminares sujetas a revisión.', 'unidad': 'pesos corrientes'},
        'datos': {'url': URLS.get(os.path.basename(xlsx), PAGINA), 'sha256': huella(xlsx), 'base': '2017 = 100'},
        'nacional': {'precios': precios['Nacional'], 'i': idx['Nacional']['i'], 'i0': idx['Nacional']['i0']},
        'estados': estados, 'municipios': municipios}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump(salida, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('Escrito %s: corte %s, %d entidades, %d municipios; precios en la pág. %d, variaciones en las págs. %d y %d.'
          % (os.path.relpath(SALIDA, RAIZ), salida['corte'], len(estados), len(municipios), pag, pe, pm))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
