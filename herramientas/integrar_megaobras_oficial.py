#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ancla el simulador de megaobras (2.2) a documentos oficiales.

Hasta ahora ninguna de las doce obras llevaba fuente. Esta herramienta no
inventa ni rellena: toma lo que Hacienda y la Auditoría Superior publican,
lo calcula y lo escribe en `simulador_megaobras.verificacion`. Donde hay
cifra oficial comparable, además corrige los campos del simulador; donde no
la hay, la obra queda marcada como pendiente, campo por campo.

Fuentes (todas se comprueban por su huella SHA-256):

- Cartera de programas y proyectos de inversión de la SHCP, publicada en
  Transparencia Presupuestaria («Obra Pública Abierta»): el monto total de
  inversión que cada proyecto tiene registrado, corte por corte.
- Cuenta Pública 2014-2025 en datos abiertos: lo ejercido cada año bajo la
  clave de cartera de cada proyecto, y el Ramo 34.
- PEF 2026 en datos abiertos: lo asignado en 2026 a cada clave y programa.
- ASF, Matriz de Datos Básicos de la Cuenta Pública 2024 (transcrita aquí,
  con su página) y el estudio «Costo del esquema de financiamiento,
  construcción y terminación anticipada de contratos del NAICM» (2021).

Uso:
    python3 herramientas/integrar_megaobras_oficial.py DIRECTORIO

DIRECTORIO contiene los archivos con el nombre con que se descargan (ver
ARCHIVOS). Es idempotente: vuelve a escribir el bloque si ya existe.
"""
import csv
import hashlib
import io
import json
import os
import re
import sys
from collections import defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')

TP = 'https://www.transparenciapresupuestaria.gob.mx/work/models/PTP/DatosAbiertos'
OPA = TP + '/OPA'
CPU = TP + '/BD_Cuenta_Publica/CSV'

# nombre -> (sha256, url)
ARCHIVOS = {
    'OPA4toTrimestre2019.csv': ('14f1d140c326b7056f775cff26ca65bb66536ed088312a58ee367f0e70e0e880', OPA + '/2019/OPA4toTrimestre2019.csv'),
    'OPA3er4toTrimestre2020.csv': ('1c90993ad6a94c85fcbfc3c5f66b70bdf9eac6bd6a007ff51d64133819b06a6c', OPA + '/2020/OPA3er4toTrimestre2020.csv'),
    'SeguimientoOPA4toTrimestre2021.csv': ('1d0d53f625e36ae9f833bb81906d4afddccf6dd0d4cdabc6014a03faa89dd3b7', OPA + '/2021/SeguimientoOPA4toTrimestre2021.csv'),
    'SeguimientoOPA4toTrimestre2022.csv': ('f9c7c5716f21233e47bee4b6e4f8c0ad477da15eb063bcf4c637dbd8aec1f584', OPA + '/2022/SeguimientoOPA4toTrimestre2022.csv'),
    'SeguimientoOPA4toTrimestre2023.csv': ('2e5f0315bc8ef7b68cf00bcd0fd01a838fdc2bad2a6b702ae97424668d72ede2', OPA + '/2023/SeguimientoOPA4toTrimestre2023.csv'),
    'SeguimientoOPA4toTrimestre2024.csv': ('626f3d5408649883031ba87acb3556d3500209d06003f36aa4978920fd5e5e31', OPA + '/2024/SeguimientoOPA4toTrimestre2024.csv'),
    'SeguimientoOPA4toTrimestre2025.csv': ('14cfa99c4e9dc001eecf78b3cc69e079f4a367dc5e85bcf299d685b25953ff75', OPA + '/2025/SeguimientoOPA4toTrimestre2025.csv'),
    'SeguimientoOPA2doTrimestre2026.csv': ('67d0819f18197998a082896f24324e7d3c7af2b3b9c81c2543b31185b40fb6b4', OPA + '/2026/SeguimientoOPA2doTrimestre2026.csv'),
    'PEF_2026.csv': ('6dec5f3ad52126c3257a74e7e177eada0c591ed8109d861becf767e959c86c03', TP + '/Bases_de_datos_presupuesto/CSV/PEF_2026.csv'),
    'cuenta_publica_2014_ra_ecd.csv': ('c878348a9724e89ad1ed435790db751694a21873e2f8674cdb6ad994673b1a55', CPU + '/cuenta_publica_2014_ra_ecd.csv'),
    'cuenta_publica_2015_ra_ecd_epe.csv': ('fc07e10ff418ddd28449cd727355aeb5753cc23bcb9e49de109386ab63606d92', CPU + '/cuenta_publica_2015_ra_ecd_epe.csv'),
    'cuenta_publica_2016_gf_ecd_epe.csv': ('30c5527e27363f7085e98bd6b47727bd5bde4cb86499dbfdde75289f33bbf83f', CPU + '/cuenta_publica_2016_gf_ecd_epe.csv'),
    'cuenta_publica_2017_gf_ecd_epe.csv': ('88f7bc16a639f7dda1b144b659d175bbfb49a7feef3ea78f0da9d076e321118a', CPU + '/cuenta_publica_2017_gf_ecd_epe.csv'),
    'cuenta_publica_2018_gf_ecd_epe.csv': ('21b4dc3d830947bfebadca25e2e7d3fe36cab6f964c6983ac73a0439e60aa3e1', CPU + '/cuenta_publica_2018_gf_ecd_epe.csv'),
    'cuenta_publica_2019_gf_ecd_epe.csv': ('c2c44d79118fea057deea1281096575ffd69d848dead8dbd90ec1eebf4ead025', CPU + '/cuenta_publica_2019_gf_ecd_epe.csv'),
    'cuenta_publica_2020_gf_ecd_epe.csv': ('c22eb5e2dc4255660a8415e4d066416d45def548190a8cea3a67fe644884060b', CPU + '/cuenta_publica_2020_gf_ecd_epe.csv'),
    'cuenta_publica_2021_gf_ecd_epe.csv': ('3b16e9d1ebe69311207378aaa4acd8441876c385b9d8b0679d32599d47e529eb', CPU + '/cuenta_publica_2021_gf_ecd_epe.csv'),
    'cuenta_publica_2022_gf_ecd_epe.csv': ('e49db45519a46ab438269ec019d62b593bcc5f94a32dd267960ee59f01f4eaac', CPU + '/cuenta_publica_2022_gf_ecd_epe.csv'),
    'cuenta_publica_2023_gf_ecd_epe.csv': ('b7ae54b404080901ae64e06cf9f8ad457be9ac4f410de6231e366428c7cf6a60', CPU + '/cuenta_publica_2023_gf_ecd_epe.csv'),
    'cuenta_publica_2024_gf_ecd_epe.csv': ('94cd87dfb1f0dbcb27886d5792046c9c6d96eeab2878f898c8a9813ef1fdf6de', CPU + '/cuenta_publica_2024_gf_ecd_epe.csv'),
    'cuenta_publica_2025_gf_ecd_epe.csv': ('973aab21969233bdfad3c4f87ccd467ab92421ea5c2cd249644c0bf2f7f1d0c0', CPU + '/cuenta_publica_2025_gf_ecd_epe.csv'),
}
CORTES_OPA = [('4T 2019', 'OPA4toTrimestre2019.csv'), ('4T 2020', 'OPA3er4toTrimestre2020.csv'),
              ('4T 2021', 'SeguimientoOPA4toTrimestre2021.csv'), ('4T 2022', 'SeguimientoOPA4toTrimestre2022.csv'),
              ('4T 2023', 'SeguimientoOPA4toTrimestre2023.csv'), ('4T 2024', 'SeguimientoOPA4toTrimestre2024.csv'),
              ('4T 2025', 'SeguimientoOPA4toTrimestre2025.csv'), ('2T 2026', 'SeguimientoOPA2doTrimestre2026.csv')]
CP_ANIOS = {2014: 'cuenta_publica_2014_ra_ecd.csv', 2015: 'cuenta_publica_2015_ra_ecd_epe.csv'}
CP_ANIOS.update({a: 'cuenta_publica_%d_gf_ecd_epe.csv' % a for a in range(2016, 2026)})

CLAVES = {'2021W3N0001': 'Proyecto Tren Maya', '13093110008': 'Tren Interurbano México-Toluca, primera etapa',
          '19071170003': 'Aeropuerto mixto civil/militar en Santa Lucía (AIFA)',
          '1409JZL0005': 'Nuevo Aeropuerto Internacional de la Ciudad de México (Texcoco)'}

# ASF, Matriz de Datos Básicos, Cuenta Pública 2024 (consolidado, feb. 2026).
# Miles de pesos en el documento; aquí millones. Los universos de varias
# auditorías se traslapan, así que no se suman: se cuentan auditorías y se
# suman recuperaciones, montos por aclarar y acciones, que sí son distintos.
# (núm, título, entrega, universo, muestra, acciones, recuperaciones, por aclarar, página)
ASF24 = {
    'tren-maya': [
        (125, 'Proyecto Tren Maya (FONATUR Tren Maya)', 3, 19542057.3, 15587979.7, 0, 0.0, 0.0, 64),
        (126, 'Erogaciones para el Proyecto Tren Maya (FONATUR Tren Maya)', 2, 19467124.4, 12381143.8, 0, 0.0, 0.0, 64),
        (137, 'Subestaciones, líneas de transmisión y catenaria del Tren Maya (CFE)', 3, 653611.1, 653611.1, 2, 2249.6, 0.0, 64),
        (138, 'Plataforma y vía, Tramo 5 Norte', 3, 6537552.8, 4130415.8, 0, 0.0, 0.0, 65),
        (139, 'Plataforma y vía, Tramo 6', 3, 33926502.0, 11557365.9, 0, 0.0, 0.0, 65),
        (140, 'Plataforma y vía, Tramo 7, y taller en Chetumal', 3, 24721716.6, 7895678.8, 0, 0.0, 0.0, 65),
        (141, 'Hotel Calakmul, Tramo 7', 3, 910491.9, 605027.4, 0, 0.0, 0.0, 65),
        (142, 'Edificaciones accesorias en Edzná, Nuevo Uxmal y Tulum', 3, 3288572.1, 3288572.1, 1, 0.0, 0.0, 65),
        (143, 'Plataforma y vía, Tramo 5 Sur', 3, 32493879.0, 11942749.5, 0, 50528.4, 0.0, 66),
        (130, 'Plataforma y vía, Tramo 1', 3, 1703091.4, 1703091.4, 0, 134458.9, 0.0, 66),
        (131, 'Plataforma y vía, Tramo 2', 3, 1879056.6, 1322262.5, 1, 0.0, 0.0, 66),
        (132, 'Plataforma y vía, Tramo 3', 3, 972326.1, 972326.1, 0, 4438.1, 0.0, 66),
        (133, 'Plataforma y vía, Tramo 4', 3, 2072105.6, 1699182.8, 5, 0.0, 85715.1, 66),
        (136, 'Seguimiento al Proyecto Tren Maya', 3, 504270.7, 504270.7, 1, 0.0, 2203.1, 66),
        (429, 'Gestión financiera de Tren Maya, S.A. de C.V.', 3, 46967804.6, 44876635.0, 0, 0.0, 0.0, 61),
    ],
    'tren-toluca': [
        (338, 'Estación Vasco de Quiroga y adecuaciones al proyecto ejecutivo', 1, 423917.0, 291686.7, 4, 0.0, 6198.6, 82),
        (340, 'Viaducto atirantado del Manantial CONAGUA y viaducto doble voladizo', 1, 634617.3, 466121.1, 5, 0.0, 13864.2, 82),
        (350, 'Material rodante y sistemas ferroviarios', 2, 2612118.0, 1230738.0, 0, 23008.0, 0.0, 84),
    ],
    'aifa-texcoco': [
        (9, 'Gestión financiera del Aeropuerto Internacional Felipe Ángeles, S.A. de C.V.', 3, 6163913.0, 3238766.2, 0, 0.0, 0.0, 61),
    ],
    'dos-bocas': [
        (247, 'Ingresos y egresos del proyecto de la Refinería Olmeca en Dos Bocas (Pemex Transformación Industrial)', 3, 84694927.4, 71511279.1, 3, 0.0, 0.0, 75),
    ],
}

FUENTES = {
    'opa': {'doc': 'SHCP, Cartera de programas y proyectos de inversión («Obra Pública Abierta»), Transparencia Presupuestaria, cortes trimestrales 2019-2026',
            'url': 'https://www.transparenciapresupuestaria.gob.mx/Obra-Publica-Abierta'},
    'cp': {'doc': 'SHCP, Cuenta Pública 2014-2025, datos abiertos (gasto por clave de cartera)',
           'url': 'https://www.transparenciapresupuestaria.gob.mx/Datos-Abiertos'},
    'pef26': {'doc': 'SHCP, PEF 2026, datos abiertos', 'url': ARCHIVOS['PEF_2026.csv'][1]},
    'pef26dof': {'doc': 'Presupuesto de Egresos de la Federación 2026, DOF 21-11-2025 (edición vespertina), Anexo 8, p. 36',
                 'url': 'https://www.diputados.gob.mx/LeyesBiblio/pdf/PEF_2026.pdf'},
    'asf24': {'doc': 'ASF, Matriz de Datos Básicos de la Cuenta Pública 2024, primera, segunda y tercera entregas (consolidado), febrero de 2026',
              'url': 'https://www.asf.gob.mx/Trans/Informes/IR2024c/Documentos/Matriz/MDB_Consolidado.pdf',
              'sha256': '49732c8da82eaafc6bdd67b0b0ce5c995773294d7e48e5412ad73e5c4fe15d66'},
    'asfnaicm': {'doc': 'ASF, Costo del esquema de financiamiento, construcción y terminación anticipada de contratos del NAICM al 31 de diciembre de 2019 (marzo de 2021)',
                 'url': 'https://www.asf.gob.mx/uploads/5210_NAICM/NAICM.pdf',
                 'sha256': 'b3f621fc8ef657e38114adb75fe2108b152fc3d87479e47353db4a88e27d5f9d'},
}


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def texto(path):
    raw = open(path, 'rb').read()
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        return raw.decode('latin-1')


def num(s):
    s = (s or '').strip().replace(',', '').replace('"', '')
    if s in ('', '-'):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def mdp(v):
    return round(v / 1e6, 1)


def cartera(d):
    """Monto total de inversión registrado, por corte, para cada clave."""
    out = defaultdict(list)
    for corte, nombre in CORTES_OPA:
        rows = csv.DictReader(io.StringIO(texto(os.path.join(d, nombre))))
        vistos = set()
        for r in rows:
            r = {k.replace('﻿', '').strip(): v for k, v in r.items() if k}
            k = r.get('CVE_CARTERA', '').strip().lstrip("'")
            if k in CLAVES and k not in vistos:
                vistos.add(k)
                out[k].append({'corte': corte, 'mti': mdp(num(r['MONTO_TOTAL_INVERSION'])),
                               'fin': r.get('FECHA_FIN_CAL_FF', ''), 'avance': r.get('AVANCE_FISICO', '')})
    return out


COLS = {'R': ['ID_RAMO', 'R'], 'PPI': ['ID_CLAVE_CARTERA', 'PPI'],
        'EJ': ['MONTO_EJERCICIO', 'EJERCICIO', 'MONTO_EJERCIDO', 'Ejercido_Bruto']}


def cuenta_publica(d):
    """Ejercido por clave de cartera y año, y total del Ramo 34 por año."""
    por_clave = defaultdict(dict)
    ramo34 = {}
    for anio, nombre in sorted(CP_ANIOS.items()):
        rd = csv.reader(io.open(os.path.join(d, nombre), encoding='latin-1'))
        hdr = [h.strip().replace('ï»¿', '').replace('﻿', '') for h in next(rd)]
        ix = {k: next(hdr.index(c) for c in v if c in hdr) for k, v in COLS.items()}
        acc = defaultdict(float)
        r34 = 0.0
        for r in rd:
            if len(r) <= ix['EJ']:
                continue
            e = num(r[ix['EJ']])
            k = r[ix['PPI']].strip().lstrip("'")
            if k in CLAVES:
                acc[k] += e
            if r[ix['R']].strip() == '34':
                r34 += e
        for k, v in acc.items():
            if abs(v) >= 1e5:
                por_clave[k][str(anio)] = mdp(v)
        ramo34[str(anio)] = mdp(r34)
        print('  Cuenta Pública %d leída' % anio, flush=True)
    return por_clave, ramo34


def pef2026(d):
    rd = csv.DictReader(io.open(os.path.join(d, 'PEF_2026.csv'), encoding='utf-8-sig', errors='replace'))
    clave = defaultdict(float)
    prog = defaultdict(float)
    for r in rd:
        v = num(r['MONTO_PEF_2026'])
        k = r['ID_CLAVE_CARTERA'].strip().lstrip("'")
        if k in CLAVES:
            clave[k] += v
        ur = r['ID_UR'].strip()
        if (ur, r['ID_MODALIDAD'] + r['ID_PP'].zfill(3)) in (('H0M', 'E015'), ('HZI', 'E014')):
            prog[ur] += v
    return {k: mdp(v) for k, v in clave.items()}, {k: mdp(v) for k, v in prog.items()}


def asf_resumen(lista):
    return {
        'auditorias': [dict(num=a[0], titulo=a[1], entrega=a[2], universo=round(a[3] / 1000, 1),
                            muestra=round(a[4] / 1000, 1), acciones=a[5], recuperaciones=round(a[6] / 1000, 1),
                            porAclarar=round(a[7] / 1000, 1), pagina=a[8]) for a in lista],
        'recuperaciones': round(sum(a[6] for a in lista) / 1000, 1),
        'porAclarar': round(sum(a[7] for a in lista) / 1000, 1),
        'acciones': sum(a[5] for a in lista),
    }


def fmt(v):
    return '{:,.1f}'.format(v)


def construir(d):
    print('Cartera de inversión...', flush=True)
    car = cartera(d)
    print('Cuenta Pública 2014-2025...', flush=True)
    cp, r34 = cuenta_publica(d)
    print('PEF 2026...', flush=True)
    pc, pp = pef2026(d)

    tm_ej = cp['2021W3N0001']
    tm_total = round(sum(tm_ej.values()), 1)
    tm_car = car['2021W3N0001']
    tm_ult = tm_car[-1]
    tl_car = car['13093110008']
    tl_ej = cp['13093110008']
    tl_total = round(sum(tl_ej.values()), 1)
    af_car = car['19071170003']
    af_ej = cp.get('19071170003', {})
    na_car = car['1409JZL0005']
    naicm = 113327.7

    assert tm_car and tl_car and af_car and na_car, 'faltan claves en la cartera'
    assert set(tm_ej) == {'2020', '2021', '2022', '2023', '2024', '2025'}, tm_ej
    assert set(tl_ej) >= {'2014', '2018', '2025'}, tl_ej

    obras = {}
    a = asf_resumen(ASF24['tren-maya'])
    obras['tren-maya'] = {
        'clave': '2021W3N0001',
        'cartera': tm_car,
        'ejercidoCP': tm_ej, 'ejercidoTotal': tm_total,
        'pef2026': {'inversion': pc.get('2021W3N0001'), 'operacion': pp.get('H0M')},
        'asf2024': a,
        'campos': {'inversion_presupuestada_mdp': 'oficial', 'inversion_real_mdp': 'derivado', 'sobrecosto_pct': 'derivado'},
        'definiciones': {
            'inversion_presupuestada_mdp': 'Último monto total de inversión que la cartera pública de Hacienda registró para la clave 2021W3N0001 (corte %s).' % tm_ult['corte'],
            'inversion_real_mdp': 'Suma de lo ejercido bajo esa clave en las Cuentas Públicas %s a %s.' % (min(tm_ej), max(tm_ej)),
        },
        'contradicciones': [
            'La clave 2021W3N0001 dejó de aparecer en la cartera pública de Hacienda después del corte %s, cuando registraba $%s mdp de monto total de inversión. Sin embargo, la Cuenta Pública siguió registrando gasto bajo esa misma clave hasta 2025 (en total, $%s mdp desde 2020), y el PEF 2026 le asigna otros $%s mdp.' % (tm_ult['corte'], fmt(tm_ult['mti']), fmt(tm_total), fmt(pc.get('2021W3N0001', 0))),
        ],
        'hallazgo': 'En la Cuenta Pública 2024 la ASF practicó %d auditorías a la obra (tramos, electrificación, edificaciones y gestión financiera): recuperó $%s mdp durante las revisiones, dejó $%s mdp por aclarar y promovió %d acciones.' % (len(a['auditorias']), fmt(a['recuperaciones']), fmt(a['porAclarar']), a['acciones']),
        'fuentes': ['opa', 'cp', 'pef26', 'asf24'],
    }
    obras['tren-maya']['valores'] = {
        'inversion_presupuestada_mdp': tm_ult['mti'],
        'inversion_real_mdp': tm_total,
    }

    a = asf_resumen(ASF24['tren-toluca'])
    tl_pri, tl_ult = tl_car[0], tl_car[-1]
    obras['tren-toluca'] = {
        'clave': '13093110008',
        'cartera': tl_car,
        'ejercidoCP': tl_ej, 'ejercidoTotal': tl_total,
        'asf2024': a,
        'campos': {'inversion_presupuestada_mdp': 'oficial', 'inversion_real_mdp': 'oficial', 'sobrecosto_pct': 'derivado'},
        'definiciones': {
            'inversion_presupuestada_mdp': 'Monto total de inversión registrado en la cartera de Hacienda en el corte más antiguo publicado en datos abiertos (%s). El registro original de 2013 no está en esa base: queda pendiente.' % tl_pri['corte'],
            'inversion_real_mdp': 'Monto total de inversión registrado en el corte %s. Es el costo que Hacienda reconoce hoy, no lo pagado: con recursos fiscales, la Cuenta Pública registra $%s mdp de %s a %s.' % (tl_ult['corte'], fmt(tl_total), min(tl_ej), max(tl_ej)),
        },
        'contradicciones': [
            'La fecha de término registrada en la cartera se movió de %s (corte %s) a %s (corte %s), y el monto total de inversión pasó de $%s a $%s mdp.' % (tl_pri['fin'], tl_pri['corte'], tl_ult['fin'], tl_ult['corte'], fmt(tl_pri['mti']), fmt(tl_ult['mti'])),
        ],
        'hallazgo': 'En la Cuenta Pública 2024 la ASF practicó %d auditorías a la obra: recuperó $%s mdp, dejó $%s mdp por aclarar y promovió %d acciones.' % (len(a['auditorias']), fmt(a['recuperaciones']), fmt(a['porAclarar']), a['acciones']),
        'fuentes': ['opa', 'cp', 'asf24'],
    }
    obras['tren-toluca']['valores'] = {
        'inversion_presupuestada_mdp': tl_pri['mti'],
        'inversion_real_mdp': tl_ult['mti'],
    }

    a = asf_resumen(ASF24['aifa-texcoco'])
    af_tot = round(sum(af_ej.values()), 1)
    obras['aifa-texcoco'] = {
        'clave': '19071170003 (AIFA) y 1409JZL0005 (NAIM)',
        'cartera': af_car, 'carteraNaim': na_car,
        'ejercidoCP': af_ej, 'ejercidoTotal': af_tot,
        'pef2026': {'operacion': pp.get('HZI')},
        'naicm': {'costo': naicm, 'faseUnoPlaneada': 169000.0, 'paginas': '12 y 46-48'},
        'asf2024': a,
        'campos': {'inversion_presupuestada_mdp': 'pendiente', 'inversion_real_mdp': 'pendiente', 'sobrecosto_pct': 'pendiente'},
        'definiciones': {
            'inversion_real_mdp': 'Suma los $%s mdp que la ASF determinó como costo de cancelar el NAIM (estudio de marzo de 2021, p. 46) y $88,107 mdp de construcción del AIFA que siguen sin fuente oficial.' % fmt(naicm),
        },
        'contradicciones': [
            'La ASF publicó en febrero de 2021 que cancelar el NAIM costó $331,996 mdp (auditoría 1394-DE, Cuenta Pública 2019) y en marzo de 2021 corrigió la cifra a $%s mdp, en un estudio que declara inconsistencias en la cuantificación original. El simulador usaba la cifra retirada.' % fmt(naicm),
            'El AIFA aparece en la cartera pública solo en el corte %s, con $%s mdp de monto total de inversión; en los cortes siguientes ya no figura. La Cuenta Pública registra bajo su clave $%s mdp entre %s y %s, y después ningún peso: el resto de la obra no se puede seguir por esa vía.' % (af_car[0]['corte'], fmt(af_car[0]['mti']), fmt(af_tot), min(af_ej), max(af_ej)),
        ],
        'hallazgo': 'La ASF (marzo de 2021) fijó el costo de cancelar el NAIM en $%s mdp al 31 de diciembre de 2019, contra los $331,996 mdp que había publicado antes. En la Cuenta Pública 2024 revisó la gestión financiera del AIFA sin observaciones.' % fmt(naicm),
        'fuentes': ['opa', 'cp', 'pef26', 'asf24', 'asfnaicm'],
    }
    obras['aifa-texcoco']['valores'] = {'inversion_real_mdp': round(naicm + 88107, 1)}

    a = asf_resumen(ASF24['dos-bocas'])
    obras['dos-bocas'] = {
        'asf2024': a,
        'campos': {'inversion_presupuestada_mdp': 'pendiente', 'inversion_real_mdp': 'pendiente', 'sobrecosto_pct': 'pendiente'},
        'contradicciones': [
            'La refinería no aparece en la cartera pública de proyectos de inversión de Hacienda en ninguno de los cortes de 2019 a 2026: la construyó una filial de Pemex, fuera del presupuesto que se publica por clave de cartera. Su costo total no se puede cotejar con esa fuente.',
        ],
        'hallazgo': 'En la Cuenta Pública 2024 la ASF revisó los ingresos y egresos del proyecto: un universo de $%s mdp en ese año, con una muestra de $%s mdp. Promovió %d recomendaciones, sin montos por aclarar ni recuperaciones.' % (fmt(a['auditorias'][0]['universo']), fmt(a['auditorias'][0]['muestra']), a['acciones']),
        'fuentes': ['opa', 'asf24'],
    }

    obras['fobaproa'] = {
        'ramo34': r34, 'pef2026Ramo34': 35553.4,
        'campos': {'inversion_presupuestada_mdp': 'pendiente', 'inversion_real_mdp': 'pendiente', 'sobrecosto_pct': 'pendiente'},
        'hallazgo': 'Lo que el rescate bancario le cuesta al presupuesto cada año sí es oficial: el Ramo 34 (programas de apoyo a ahorradores y deudores de la banca) ejerció $%s mdp en 2025 según la Cuenta Pública, y el PEF 2026 le asigna $35,553.4 mdp.' % fmt(r34['2025']),
        'fuentes': ['cp', 'pef26dof'],
    }

    return {
        'nota': 'Lo que los documentos oficiales dicen de cada obra. Donde hay cifra oficial comparable, sustituye a la del simulador; donde no, la obra queda marcada como pendiente, campo por campo. Nada de esto es una estimación.',
        'fuentes': FUENTES,
        'obras': obras,
    }


def patch(ver):
    raw = open(DB, 'rb').read().decode('utf-8')
    i = raw.index('"simulador_megaobras": {')
    j = raw.index('{', i)
    prof = 0
    for k in range(j, len(raw)):
        c = raw[k]
        if c == '{':
            prof += 1
        elif c == '}':
            prof -= 1
            if prof == 0:
                break
    bloque = raw[j:k + 1]
    nl = '\r\n' if '\r\n' in bloque else '\n'
    sim = json.loads(bloque)

    for o in sim['obras']:
        v = ver['obras'].get(o['id'])
        if not v:
            o['estado_campos'] = {'inversion_presupuestada_mdp': 'pendiente', 'inversion_real_mdp': 'pendiente', 'sobrecosto_pct': 'pendiente'}
            continue
        for campo, valor in v.get('valores', {}).items():
            o[campo] = valor
        pres, real = o['inversion_presupuestada_mdp'], o['inversion_real_mdp']
        if pres and real:
            o['sobrecosto_pct'] = round((real / pres - 1) * 100, 1)
        o['estado_campos'] = v['campos']
        if v.get('hallazgo'):
            o['hallazgo_asf'] = v['hallazgo']
        if o['id'] == 'aifa-texcoco':
            o['proyeccion_resumen'] = ('El costo que el simulador consolida suma los $113,327.7 mdp que la ASF fijó como costo de cancelar el NAIM '
                                       '(estudio de marzo de 2021) y $88,107 mdp de construcción del AIFA, cifra esta última sin fuente oficial. '
                                       'La proyección de subsidio a 25 años queda pendiente de documento.')

    t = sim['totales_consolidados']
    t['inversion_total_mdp'] = round(sum(o['inversion_real_mdp'] for o in sim['obras']), 1)
    t['inversion_presupuestada_total_mdp'] = round(sum(o['inversion_presupuestada_mdp'] for o in sim['obras']), 1)
    t['sobrecosto_conjunto_pct'] = round((t['inversion_total_mdp'] / t['inversion_presupuestada_total_mdp'] - 1) * 100, 1)
    sim['verificacion'] = ver

    # El bloque original abre su llave en la línea de la clave y sus campos
    # van a dos espacios: es justo lo que da json.dumps con indent=2, así el
    # diff muestra solo lo que cambia.
    nuevo = json.dumps(sim, ensure_ascii=False, indent=2)
    if not nuevo.endswith('}'):
        sys.exit('bloque inesperado')
    nuevo = nuevo[:-1] + raw[raw.rfind('\n', 0, k) + 1:k] + '}'
    raw = raw[:j] + nuevo.replace('\n', nl) + raw[k + 1:]
    open(DB, 'wb').write(raw.encode('utf-8'))
    return sim


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    d = sys.argv[1]
    for nombre, (h, _) in ARCHIVOS.items():
        real = sha(os.path.join(d, nombre))
        if real != h:
            sys.exit('La huella de %s no coincide: %s' % (nombre, real))
    print('Huellas verificadas (%d archivos).' % len(ARCHIVOS))
    ver = construir(d)
    sim = patch(ver)
    for o in sim['obras']:
        print('  %-18s presupuesto %12s  real %12s  sobrecosto %7s  %s' % (
            o['id'], o['inversion_presupuestada_mdp'], o['inversion_real_mdp'], o['sobrecosto_pct'],
            o['estado_campos'].get('inversion_real_mdp')))
    print('Totales:', sim['totales_consolidados'])


if __name__ == '__main__':
    main()
