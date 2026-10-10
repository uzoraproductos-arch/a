#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrae del cuadro II.6 de los Criterios Generales de Politica Economica
2027 (p. 67) el ejemplo oficial del simulador «Reparte el presupuesto»
(propuesta de Astra, entrega 4, 10-10-2026).

    pdftotext -layout "criterios generales proyecto presupuesto.pdf" cgpe.txt
    python3 herramientas/extraer_simulador.py cgpe.txt

Escribe investigaciones/simulador/cgpe2027-cuadro-ii6.json. Toma los
renglones tal cual y comprueba que las partes sumen los totales del propio
cuadro (con 0.2 mdp de tolerancia por redondeo). Si un renglon no aparece o
la suma no cuadra, se detiene: nada se teclea a mano.
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NUM = re.compile(r'-?\d[\d,]*\.\d')

# (id, renglon en el cuadro, nombre para el lector, que es)
ENTRADAS = [
    ('tributarios', 'Tributarios', 'Impuestos (ISR, IVA, IEPS y otros)', 'Ingresos tributarios del Gobierno Federal.'),
    ('no_tributarios', 'No tributarios', 'Derechos, productos y aprovechamientos', 'Ingresos no tributarios del Gobierno Federal.'),
    ('petroleros', 'Petroleros', 'Ingresos petroleros', 'Lo que aportan el petróleo y Pemex.'),
    ('organismos', 'Organismos y empresas', 'Organismos y empresas (IMSS, ISSSTE, CFE)', 'Ingresos propios de organismos y empresas del Estado.'),
]
SALIDAS = [
    ('programable', 'Programable pagado', 'Gasto programable (programas, servicios, nómina e inversión)', 'El gasto que se decide cada año, ya pagado.'),
    ('costofin', 'Costo financiero', 'Intereses y costo de la deuda', 'Costo financiero de la deuda y apoyos a ahorradores y deudores.'),
    ('participaciones', 'Participaciones', 'Participaciones a estados y municipios (Ramo 28)', 'Lo que la Federación transfiere y los estados gastan con libertad.'),
    ('adefas', 'Adefas', 'Adeudos de ejercicios fiscales anteriores (Adefas)', 'Pagos de compromisos del año anterior.'),
]
TOTALES = [('ingresos', 'Ingresos presupuestarios'), ('gasto', 'Gasto neto pagado'), ('balance', 'Balance presupuestario')]


def cuadro(texto):
    i = texto.index('Estimación de las finanzas públicas, 2026-2027')
    return texto[i:texto.index('Fuente: SHCP.', i)]


def renglon(bloque, nombre):
    for linea in bloque.splitlines():
        if re.match(r'\s*' + re.escape(nombre) + r'\s{2,}', linea):
            n = [float(x.replace(',', '')) for x in NUM.findall(linea)]
            return {'2026a': n[0], '2027': n[2]}
    raise SystemExit('No encontré el renglón «%s» en el cuadro II.6' % nombre)


def main(ruta):
    bloque = cuadro(open(ruta, encoding='utf-8', errors='replace').read())
    out = {
        'fuente': 'SHCP, Criterios Generales de Política Económica 2027, cuadro II.6 «Estimación de las finanzas públicas, 2026-2027», p. 67',
        'url': 'https://gaceta.diputados.gob.mx/PDF/66/2026/sep/20260908-C.pdf',
        'unidad': 'millones de pesos',
        'escenarios': {'2026a': 'Presupuesto aprobado 2026', '2027': 'Paquete Económico 2027 (estimado)'},
        'entradas': [], 'salidas': [], 'totales': {},
    }
    for clave, lista in (('entradas', ENTRADAS), ('salidas', SALIDAS)):
        for id_, fila, nombre, que in lista:
            out[clave].append({'id': id_, 'renglon': fila, 'nombre': nombre, 'que': que, 'mdp': renglon(bloque, fila)})
    for id_, fila in TOTALES:
        out['totales'][id_] = renglon(bloque, fila)
    for k in ('2026a', '2027'):
        e = sum(x['mdp'][k] for x in out['entradas'])
        s = sum(x['mdp'][k] for x in out['salidas'])
        for nombre, calc, oficial in (('ingresos', e, out['totales']['ingresos'][k]), ('gasto', s, out['totales']['gasto'][k]),
                                      ('balance', e - s, out['totales']['balance'][k])):
            if abs(calc - oficial) > 0.2:
                raise SystemExit('%s %s no cuadra: %.1f contra %.1f del cuadro' % (nombre, k, calc, oficial))
    sal = os.path.join(RAIZ, 'investigaciones', 'simulador', 'cgpe2027-cuadro-ii6.json')
    os.makedirs(os.path.dirname(sal), exist_ok=True)
    json.dump(out, open(sal, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('simulador: %d entradas y %d salidas; ingresos, gasto y balance cuadran con el cuadro II.6' % (len(ENTRADAS), len(SALIDAS)))


if __name__ == '__main__':
    main(sys.argv[1])
