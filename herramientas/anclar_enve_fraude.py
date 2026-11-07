#!/usr/bin/env python3
"""Ancla el fraude contra las empresas de la ENVE 2024 del INEGI (datos de 2023)
para «El fraude en números» (pedido del autor, 07-11-2026: «continúa con el
costo del fraude de la ENVE»).

Se corre a mano:

    python3 herramientas/anclar_enve_fraude.py <conjunto_de_datos_enve_2024_csv.zip> <enve_2024_presentacion_ejecutiva.pdf>

Los dos archivos son del INEGI (ZIP y PDF, abajo). El ZIP trae los tabulados de
la encuesta en CSV; el PDF, la presentación de resultados (se lee con
`pdftotext -layout`). De ahí salen:

- del tabulado 1.16, los fraudes contra unidades económicas y el total de
  delitos (se detiene si los renglones no suman el total);
- del 1.8, la tasa de fraude por cada 10 mil unidades económicas;
- del 3.4, los fraudes sin carpeta de investigación y su cifra negra (se
  detiene si no trae los mismos fraudes que el 1.16);
- del 6.1 y el 6.8, el costo del delito en pesos de 2023 y en pesos de julio de
  2018, sus pérdidas y su gasto en protegerse (se detiene si el deflactado no
  da los 124.3 mil millones que dice la presentación);
- de la presentación, lámina «Costo del delito según tipo de delito», lo que
  costó en promedio cada tipo de delito, en pesos de julio de 2018 (se detiene
  si no encuentra el renglón del fraude o la nota de los precios).

El INEGI no publica cuánto costó el fraude en total. Multiplicar su costo
promedio por el número de fraudes no sirve: hecho con los nueve delitos que se
llaman igual en la lámina y en el tabulado 1.16, da más que todas las pérdidas
del tabulado 6.8. El script guarda esa cuenta (`producto_9`) para que conste
por qué no se calcula.

Escribe docs/seguridad/enve-2024-fraude.json con las dos huellas SHA-256.
"""
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'seguridad', 'enve-2024-fraude.json')
PAGINA = 'https://www.inegi.org.mx/programas/enve/2024/'
ZIP = 'https://www.inegi.org.mx/contenidos/programas/enve/2024/datosabiertos/conjunto_de_datos_enve_2024_csv.zip'
PDF = 'https://www.inegi.org.mx/contenidos/programas/enve/2024/doc/enve_2024_presentacion_ejecutiva.pdf'
NAC = 'Estados Unidos Mexicanos'
# Nombre en la lámina de costos → nombre en el tabulado 1.16 (sin su número de nota).
MISMOS = {'Robo total de vehículo': 'Robo total de vehículo', 'Robo de accesorios de vehículo': 'Robo de accesorios de vehículo',
          'Robo de mercancía en tránsito': 'Robo de mercancía en tránsito', 'Robo hormiga': 'Robo hormiga',
          'Robo o asalto de mercancía, dinero, insumos o bienes': 'Robo/asalto de bienes o dinero', 'Fraude': 'Fraude',
          'Extorsión': 'Extorsión', 'Daños a instalaciones, maquinaria o equipo': 'Daños a instalaciones, maquinaria o equipo',
          'Actos de corrupción': 'Actos de corrupción'}


def _sin_nota(s):
    return re.sub(r'\d+$', '', s.strip())


def _tabla(z, nombre):
    n = [x for x in z.namelist() if x.endswith('/' + nombre + '.csv')]
    if len(n) != 1:
        sys.exit('No encuentro el tabulado %s' % nombre)
    return list(csv.reader(io.StringIO(z.read(n[0]).decode('utf-8-sig'))))


def _renglon(filas, nombre):
    r = [f for f in filas[1:] if f and _sin_nota(f[0]) == nombre]
    if len(r) != 1:
        sys.exit('El tabulado no trae un solo renglón «%s»' % nombre)
    return r[0]


def _laminas(ruta):
    t = subprocess.run(['pdftotext', '-layout', ruta, '-'], capture_output=True, text=True, check=True).stdout
    i = t.find('Costo del delito según tipo de delito')
    if i < 0:
        sys.exit('La presentación no trae la lámina «Costo del delito según tipo de delito»')
    bloque = t[i:t.find('Fuente:', i)]
    if 'Pesos a precios de la segunda quincena de julio 2018' not in bloque:
        sys.exit('La lámina de costos ya no dice en qué precios están')
    lineas = [l for l in bloque.splitlines() if l.strip()]
    costo = {}
    for j, l in enumerate(lineas):
        m = re.match(r'^\s*(.+?)\s*(\*?)\s{2,}(\d{1,3}(?: \d{3})?)\s*(?:2023|2021)?\s*$', l)
        if not m or re.match(r'^[\d ]+$', m.group(1)):
            continue
        sig = re.match(r'^\s*(\d{1,3}(?: \d{3})?)\s*(?:2023|2021)?\s*$', lineas[j + 1]) if j + 1 < len(lineas) else None
        if not sig:
            continue
        # El asterisco de la lámina: «sí existe un cambio estadísticamente significativo» frente a 2021.
        costo[m.group(1)] = {'2023': int(m.group(3).replace(' ', '')), '2021': int(sig.group(1).replace(' ', '')), 'significativo': m.group(2) == '*'}
    if 'Fraude' not in costo:
        sys.exit('La lámina de costos no trae el renglón del fraude')
    m = re.search(r'([\d.]+) mil millones de pesos, es decir, ([\d.]+)% del PIB', t)
    if not m:
        sys.exit('La presentación ya no dice el costo total del delito')
    return costo, float(m.group(1)), float(m.group(2))


def main(ruta_zip, ruta_pdf):
    with open(ruta_zip, 'rb') as f:
        crudo = f.read()
    with open(ruta_pdf, 'rb') as f:
        sha_pdf = hashlib.sha256(f.read()).hexdigest()
    with zipfile.ZipFile(io.BytesIO(crudo)) as z:
        t116, t18, t34 = _tabla(z, 't1_16'), _tabla(z, 't1_8'), _tabla(z, 't3_4')
        t61, t68 = _tabla(z, 't6_1'), _tabla(z, 't6_8')
    # 1.16: delitos ocurridos por tipo; los renglones suman el total.
    tot = float(_renglon(t116, NAC)[1])
    tipos = {_sin_nota(f[0]): float(f[1]) for f in t116[1:] if f and f[0] != NAC}
    if abs(sum(tipos.values()) - tot) > 1:
        sys.exit('Los tipos de delito del 1.16 no suman el total: %s contra %s' % (sum(tipos.values()), tot))
    fr = tipos['Fraude']
    # 3.4: cifra negra del fraude.
    r = _renglon(t34, 'Fraude')
    if abs(float(r[1]) - fr) > 0.5:
        sys.exit('El 3.4 no trae los mismos fraudes que el 1.16')
    # 1.8: tasa de incidencia por cada 10 mil unidades económicas (solo el bloque nacional, antes del primer estado).
    nac18 = t18[1:t18.index(['NA', 'NA'])] if ['NA', 'NA'] in t18 else t18[1:]
    tasa = float(_renglon([None] + nac18, 'Fraude')[1])
    # 6.1 y 6.8: costos del delito, nacional.
    n61, n68 = _renglon(t61, NAC), _renglon(t68, NAC)
    costo, total_pres, pib = _laminas(ruta_pdf)
    if round(float(n68[9]) / 1e9, 1) != total_pres:
        sys.exit('El 6.8 no da el costo total de la presentación: %s contra %s' % (float(n68[9]) / 1e9, total_pres))
    falta = [k for k in MISMOS if k not in costo]
    if falta:
        sys.exit('La lámina de costos no trae: %s' % ', '.join(falta))
    prod = sum(costo[k]['2023'] * tipos[v] for k, v in MISMOS.items())
    doc = {'fuente': 'INEGI, Encuesta Nacional de Victimización de Empresas (ENVE) 2024, datos de 2023',
           'pagina': PAGINA,
           'zip': {'url': ZIP, 'archivo': os.path.basename(ruta_zip), 'sha': hashlib.sha256(crudo).hexdigest()},
           'pdf': {'url': PDF, 'archivo': os.path.basename(ruta_pdf), 'sha': sha_pdf},
           'delitos': round(tot), 'fraudes': round(fr), 'fraude_pct': round(fr * 100.0 / tot, 1),
           'fraude_tasa': round(tasa), 'fraude_sin_carpeta': round(float(r[2])), 'fraude_cifra_negra': round(float(r[3]), 1),
           'costo_promedio': costo, 'precios_costo_promedio': 'pesos de la segunda quincena de julio de 2018',
           'costo_total_2018': round(float(n68[9])), 'perdidas_2018': round(float(n68[6])), 'prevencion_2018': round(float(n68[3])),
           'costo_total_corrientes': round(float(n61[9])), 'perdidas_corrientes': round(float(n61[6])),
           'prevencion_corrientes': round(float(n61[3])), 'pib_pct': pib,
           'producto_9': round(prod)}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('Fraudes contra empresas, 2023: %s (%s %% de %s delitos); costo promedio %s pesos de 2018; cifra negra %s %%'
          % (format(doc['fraudes'], ','), doc['fraude_pct'], format(doc['delitos'], ','), format(costo['Fraude']['2023'], ','), doc['fraude_cifra_negra']))
    print('Costo promedio × delitos (9 tipos): %.1f mil millones; pérdidas del 6.8: %.1f mil millones' % (prod / 1e9, float(n68[6]) / 1e9))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
