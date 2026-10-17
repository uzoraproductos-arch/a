#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrae del texto de los Criterios Generales de Politica Economica 2027
las cifras del Estado de Cuenta Civico (entrega 3, 10-10-2026).

    pdftotext -layout "criterios generales proyecto presupuesto.pdf" cgpe.txt
    python3 herramientas/extraer_estado_cuenta.py cgpe.txt

Escribe investigaciones/estado-de-cuenta/cgpe2027-comparativo.json. Si un
renglon no aparece tal cual en el cuadro, se detiene: nada se teclea a mano.
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NUM = re.compile(r'-?\d[\d,]*\.\d')

# id, dimension, concepto, renglon en el cuadro historico (p. 55 o 52),
# pagina del historico, renglon en el cuadro II.6 (p. 67), que significa
RENGLONES = [
    ('ingresos', 'presupuestaria', 'Ingresos presupuestarios', 'Ingresos presupuestarios3/', 55, 'Ingresos presupuestarios',
     'Todo lo que entra al sector público presupuestario en el año: impuestos, derechos, ingresos petroleros y de organismos y empresas. No incluye deuda.'),
    ('tributarios', 'presupuestaria', 'Ingresos tributarios', 'Tributarios', 55, 'Tributarios',
     'Los impuestos: ISR, IVA, IEPS, importación y otros.'),
    ('petroleros', 'presupuestaria', 'Ingresos petroleros', 'Petroleros', 55, 'Petroleros',
     'Lo que aportan el petróleo y Pemex.'),
    ('gasto', 'presupuestaria', 'Gasto neto pagado', 'Gasto neto pagado3/', 55, 'Gasto neto pagado',
     'Todo lo que el sector público pagó o prevé pagar en el año.'),
    ('programable', 'presupuestaria', 'Gasto programable devengado', 'Programable devengado', 55, 'Programable devengado',
     'El gasto en programas, servicios, nómina e inversión: lo que se decide cada año.'),
    ('participaciones', 'presupuestaria', 'Participaciones a estados y municipios', 'Participaciones', 55, 'Participaciones',
     'El Ramo 28: dinero que la Federación transfiere y que los estados gastan con libertad.'),
    ('balance', 'presupuestaria', 'Balance presupuestario (déficit si es negativo)', 'Balance presupuestario', 55, 'Balance presupuestario',
     'Ingresos menos gasto. Si es negativo, es el déficit que se cubre con deuda.'),
    ('costofin', 'financiera', 'Costo financiero de la deuda', 'Costo financiero', 55, 'Costo financiero',
     'Intereses, comisiones y gastos de la deuda, más los programas de apoyo a ahorradores y deudores.'),
    ('primario', 'financiera', 'Balance primario', 'Balance primario presupuestario', 55, 'Superávit económico primario',
     'El balance sin contar los intereses de la deuda: dice si el gobierno gasta más de lo que ingresa antes de pagar a sus acreedores.'),
    ('shrfsp', 'financiera', 'Deuda amplia (SHRFSP)', 'SHRFSP', 52, 'SHRFSP',
     'El Saldo Histórico de los Requerimientos Financieros del Sector Público: la medida más amplia de la deuda.'),
]


def numeros(linea):
    return [float(x.replace(',', '')) for x in NUM.findall(linea)]


def renglon(paginas, pagina, etiqueta, desde=None):
    texto = paginas[pagina - 1]
    if desde:
        texto = texto[texto.index(desde):]
    for linea in texto.splitlines():
        if linea.strip().startswith(etiqueta + ' ') or linea.strip().startswith(etiqueta + '\t'):
            return numeros(linea[len(linea) - len(linea.lstrip()) + len(etiqueta):])
    raise SystemExit('No encontré «%s» en la página %d' % (etiqueta, pagina))


def main(ruta):
    paginas = open(ruta, encoding='utf-8').read().split('\f')
    filas = []
    for id_, dim, concepto, eh, ph, e6, desc in RENGLONES:
        h = renglon(paginas, ph, eh, 'Ingresos y gasto del Sector P' if ph == 55 else None)
        n = renglon(paginas, 67, e6)
        if len(h) < 8 or len(n) < 6:
            raise SystemExit('Renglón incompleto: %s %s %s' % (id_, h, n))
        filas.append({
            'id': id_, 'dimension': dim, 'concepto': concepto, 'que': desc,
            'pib': {'2024': h[4], '2026a': n[3], '2026e': n[4], '2027': n[5]},
            'pib_hist_2026a': h[6],
            'mdp': {'2026a': n[0], '2026e': n[1], '2027': n[2]},
            'pagina_hist': ph, 'pagina_ii6': 67,
        })
        if abs(h[6] - n[3]) > 0.11 and id_ not in ('shrfsp',):
            print('aviso: %s 2026 aprobado difiere entre cuadros (%s vs %s)' % (id_, h[6], n[3]))
    sal = os.path.join(RAIZ, 'investigaciones', 'estado-de-cuenta', 'cgpe2027-comparativo.json')
    json.dump(filas, open(sal, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for f in filas:
        print('%-15s %s %s' % (f['id'], f['pib'], f['mdp']))


if __name__ == '__main__':
    main(sys.argv[1])
