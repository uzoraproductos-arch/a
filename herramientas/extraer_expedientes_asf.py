#!/usr/bin/env python3
"""Expedientes de casos por aclarar: extrae de los informes individuales de
la ASF y del Sistema de Alertas de la SHCP los datos de las seis fichas de
Búsqueda Forense.

Uso:
    python3 herramientas/extraer_expedientes_asf.py CARPETA

CARPETA contiene los PDF tal como los publica la ASF (p. ej. 2022_0107_a.pdf),
la portada de cada entrega del Informe del Resultado guardada con su nombre
(IR2022c.html, de https://www.asf.gob.mx/Trans/Informes/IR2022c/index.html),
de donde se toma el título oficial de cada auditoría, y el libro del Sistema de Alertas «Información Variables SdA Entidades
Federativas.xlsx» de la Cuenta Pública 2025 guardado como sda_var_2025cp.xlsx.
Las ligas de cada documento se arman abajo.

De cada informe se lee, sin interpretar:
  - la entidad fiscalizada, el título y la clave de la auditoría (portada);
  - el universo seleccionado y la muestra auditada (miles de pesos);
  - el párrafo de montos: lo determinado, lo recuperado y lo pendiente de
    aclarar (pesos);
  - el «Resumen de Resultados», y de ahí el número de cada tipo de acción.
Escribe investigaciones/expedientes-asf.json; integrar_expedientes.py lo lee.
"""
import hashlib
import json
import logging
import pathlib
import re
import sys

import html

import openpyxl
import pypdf

logging.disable(logging.WARNING)
RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'investigaciones' / 'expedientes-asf.json'
ASF = 'https://www.asf.gob.mx/Trans/Informes/%s/Documentos/Auditorias/%s'
SDA_URL = ('https://www.disciplinafinanciera.hacienda.gob.mx/work/models/DISCIPLINA_FINANCIERA/Documentos/'
           'SistemaAlertas/2025/CP/Informaci%C3%B3n%20Variables%20SdA%20Entidades%20Federativas.xlsx')

# (entrega del Informe del Resultado, número de auditoría)
AUDITORIAS = {
    'IR2022a': [303],
    'IR2022b': [77],
    'IR2022c': [107, 111, 112, 113, 114, 115, 116, 117, 118, 2111, 2112,
                215, 216, 217, 218, 219, 220, 221, 2123, 140, 164, 173,
                307, 308, 329, 341, 342, 2121, 2122],
    'IR2023b': [371, 336, 101],
    'IR2023c': [145, 244, 246, 247, 248, 249, 400, 191, 341, 353, 234],
    'IR2024a': [338, 340, 95],
    'IR2024b': [126, 353, 360, 418, 419, 420, 350],
    'IR2024c': [9, 125, 247, 356, 367, 429],
}

ACCIONES = [
    ('R', r'Recomendaci(?:ón|ones)(?! al Desempeño)'),
    ('RD', r'Recomendaci(?:ón|ones) al Desempeño'),
    ('SA', r'Solicitud(?:es)? de Aclaración'),
    ('PEFCF', r'Promoci(?:ón|ones) del Ejercicio de la Facultad de Comprobación Fiscal'),
    ('PRAS', r'Promoci(?:ón|ones) de Responsabilidad Administrativa Sancionatoria'),
    ('PO', r'Pliegos? de Observaciones'),
    ('DH', r'Denuncias? de Hechos'),
]


# Cifras puntuales que se citan en Auditoría en imágenes. Se leen del texto
# del informe con su frase literal; si la frase no aparece, el script se
# detiene en lugar de dejar un hueco. (clave, patrón, multiplicador a pesos).
EXTRACTOS = {
    (2023, 234): [  # Birmex: almacén de Huehuetoca (CEFEDIS), resultado 4
        ('cefedisPrecio', r'se pactó por un monto de ([\d,\.]+) miles de pesos más IVA', 1e3),
        ('cefedisInmuebleConIva', r'Perinorte, S\.A de C\.V\. Contrato vía civil \S+ No aplica ([\d,\.]+) [\d,\.]+', 1e3),
        ('cefedisInmueblePagado', r'Perinorte, S\.A de C\.V\. Contrato vía civil \S+ No aplica [\d,\.]+ ([\d,\.]+)', 1e3),
        ('cefedisEquipamiento', r'SEASA Nuevo León, S\.A\. de C\.V\. A-043/2023 \S+ Del \S+ al \S+ ([\d,\.]+) [\d,\.]+', 1e3),
        ('cefedisEquipamientoPagado', r'SEASA Nuevo León, S\.A\. de C\.V\. A-043/2023 \S+ Del \S+ al \S+ [\d,\.]+ ([\d,\.]+)', 1e3),
        ('cefedisInversion', r'el costo de inversión de esta alternativa ascendió a ([\d,\.]+) millones de pesos sin IVA', 1e6),
        ('cefedisConstruir', r'El costo de inversión de esta alternativa ascendía a ([\d,\.]+) millones de pesos sin IVA', 1e6),
        ('almacenAvior', r'pagó ([\d,\.]+) miles de pesos al proveedor Almacenaje y Distribución Avior', 1e3),
        ('almacenMaypo', r'pagó ([\d,\.]+) miles de pesos al proveedor Farmacéuticos Maypo', 1e3),
    ],
    (2023, 101): [  # Conagua: El Cuchillo II
        ('longitudKm', r'con una longitud de ([\d,\.]+) kilómetros, un desnivel', 1),
        ('usuarios', r'Monterrey y su Zona Conurbada, en beneficio de un total de ([\d,]+) usuarios', 1),
    ],
}

def pesos(t):
    return float(t.replace(',', ''))


def titulos(carpeta):
    """Titulo de cada auditoria segun el indice oficial de cada entrega."""
    t = {}
    for ir in AUDITORIAS:
        pagina = (carpeta / (ir + '.html')).read_text(encoding='utf-8', errors='replace')
        for pdf, texto in re.findall(r'<td width="\d+px"><a href="Documentos/Auditorias/([^"]+)"[^>]*>(.*?)</a>', pagina, re.S):
            t[(ir, pdf)] = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', texto))).strip()
    return t


def plano_min(t):
    return re.sub(r'[\s-]+', '', t).lower()


def leer_informe(ruta, ir, num, titulo):
    lector = pypdf.PdfReader(str(ruta))
    paginas = [p.extract_text() or '' for p in lector.pages]
    plano = re.sub(r'\s+', ' ', '\n'.join(paginas))
    # Encabezados y pies de pagina que parten los parrafos.
    plano = re.sub(r' (?:Gasto Federalizado|Grupo Funcional [A-Za-zÁÉÍÓÚáéíóúñ ]+?) \d+(?= )', '', plano)
    plano = re.sub(r' Informe Individual del Resultado de la Fiscalización Superior de la Cuenta Pública \d{4} \d+', '', plano)
    portada = re.sub(r'\s+', ' ', paginas[0])
    m = re.search(r'(?:Grupo Funcional [A-Za-zÁÉÍÓÚáéíóúñ ]+?|Gasto Federalizado) 1 (.+?) (Auditoría [Dd]e [^:]+): (\S+)', portada)
    if not m:
        sys.exit('No reconozco la portada de %s' % ruta.name)
    ente_titulo, tipo, clave = m.group(1), m.group(2).replace('Auditoría De', 'Auditoría de'), m.group(3)
    uni = re.search(r'Universo Seleccionado ([\d,\.]+) Muestra Auditada ([\d,\.]+)', plano)
    res = re.search(r'Resumen de Resultados[^S]*(Se determinaron[\s\S]{0,600}?)(?= Consideraciones| Dictamen| Adicionalmente)', plano)
    resumen = res.group(1).strip() if res else ''
    acciones = {}
    for clave_acc, patron in ACCIONES:
        for n, _ in re.findall(r'(\d+) (%s)' % patron, resumen):
            acciones[clave_acc] = acciones.get(clave_acc, 0) + int(n)
    montos = {'determinado': None, 'recuperado': 0.0, 'porAclarar': 0.0}
    m1 = re.search(r'Se determinaron ([\d,\.]+) pesos pendientes por aclarar', plano)
    m2 = re.search(r'Se determinó un monto por ([\d,\.]+) pesos, en el transcurso de la revisión se recuperaron recursos por ([\d,\.]+) pesos', plano)
    m3 = re.search(r'([\d,\.]+) pesos están pendientes de aclaración', plano)
    m4 = re.search(r'se recuperaron recursos por ([\d,\.]+) pesos', plano)
    if m1:
        montos['porAclarar'] = pesos(m1.group(1))
    if m2:
        montos['determinado'] = pesos(m2.group(1))
        montos['recuperado'] = pesos(m2.group(2))
    elif m4:
        montos['recuperado'] = pesos(m4.group(1))
    if m3:
        montos['porAclarar'] = pesos(m3.group(1))
    dictamen = re.search(r'Dictamen El presente dictamen se emite el ([^,]+?), fecha', plano)
    # El ente es lo que antecede al titulo oficial en la portada.
    ente = ente_titulo
    corto = plano_min(titulo)
    for k in range(len(ente_titulo)):
        if plano_min(ente_titulo[k:]) == corto:
            ente = ente_titulo[:k].strip()
            break
    else:
        # En el gasto federalizado el indice trae al ente y no el titulo: el
        # titulo es lo que sigue al ente en la portada.
        for k in range(1, len(ente_titulo) + 1):
            if plano_min(ente_titulo[:k]) == corto:
                ente, titulo = ente_titulo[:k].strip(), ente_titulo[k:].strip()
                break
        else:
            sys.exit('No separo ente y titulo en %s' % ruta.name)
    ente = re.sub(r'(\w) - (\w)', r'\1-\2', ente)
    extractos = {}
    for clave_x, patron, factor in EXTRACTOS.get((int(ir[2:6]), num), []):
        mx = re.search(patron, plano)
        if not mx:
            sys.exit('No encuentro «%s» en %s' % (clave_x, ruta.name))
        extractos[clave_x] = round(pesos(mx.group(1)) * factor, 2)
    return {
        'ir': ir, 'cp': int(ir[2:6]), 'num': num, 'claveAuditoria': clave, 'tipo': tipo,
        'ente': ente, 'titulo': titulo,
        'universoMiles': pesos(uni.group(1)) if uni else None,
        'muestraMiles': pesos(uni.group(2)) if uni else None,
        'resumen': resumen, 'acciones': acciones,
        'determinado': montos['determinado'], 'recuperado': montos['recuperado'], 'porAclarar': montos['porAclarar'],
        'fechaDictamen': dictamen.group(1) if dictamen else None,
        'paginas': len(paginas),
        'extractos': extractos,
        'url': ASF % (ir, ruta.name),
        'sha256': hashlib.sha256(ruta.read_bytes()).hexdigest(),
    }


def leer_sda(ruta):
    ws = openpyxl.load_workbook(str(ruta), data_only=True).worksheets[0]
    filas = [r for r in list(ws.iter_rows(values_only=True))[7:45] if r[0] and isinstance(r[1], (int, float))]
    niveles = {1: 'Endeudamiento Sostenible', 2: 'Endeudamiento en Observación', 3: 'Endeudamiento Elevado'}
    entidades = [{'entidad': r[0], 'resultado': niveles[int(r[1])], 'dyoIld': r[2], 'sdIld': r[4], 'ocpIt': r[6],
                  'dyo': round(r[8] * 1e6, 2), 'ild': round(r[29] * 1e6, 2)} for r in filas]
    assert len(entidades) == 31, 'Se esperaban 31 entidades medidas (Tlaxcala no se mide)'
    return {'url': SDA_URL, 'sha256': hashlib.sha256(ruta.read_bytes()).hexdigest(),
            'corte': 'Cuenta Pública 2025', 'publicado': '2026-06-29', 'entidades': entidades}


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    carpeta = pathlib.Path(sys.argv[1])
    informes = []
    tit = titulos(carpeta)
    for ir, nums in AUDITORIAS.items():
        for num in nums:
            ruta = carpeta / ('%s_%04d_a.pdf' % (ir[2:6], num))
            if not ruta.exists():
                sys.exit('Falta %s' % ruta)
            informes.append(leer_informe(ruta, ir, num, tit[(ir, ruta.name)]))
    salida = {'informes': informes, 'sistemaAlertas': leer_sda(carpeta / 'sda_var_2025cp.xlsx')}
    SALIDA.write_text(json.dumps(salida, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('%d informes y %d entidades del Sistema de Alertas -> %s' % (
        len(informes), len(salida['sistemaAlertas']['entidades']), SALIDA.relative_to(RAIZ)))


if __name__ == '__main__':
    main()
