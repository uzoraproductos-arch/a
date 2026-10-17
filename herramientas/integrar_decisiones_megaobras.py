#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Decisiones del autor sobre el método de Megaobras (17-10-2026).

1. Los rescates (FOBAPROA y FARAC) se cuentan aparte de las obras. No son
   obras: son deudas que el Estado asumió. Su «sobrecosto» mezcla pagos de
   décadas con saldos de hoy y no se compara con el de una obra, así que
   las cifras de conjunto (totales_consolidados) miden solo las obras y los
   rescates tienen su propio bloque (`rescates`). La suma de todo queda en
   `con_rescates`, por si alguien la busca.
2. El FARAC se asigna a Ernesto Zedillo (1994-2000): el rescate se hizo en
   1997 (ASF, CP 2015, auditoría 99; CP 2017, auditoría 96, p. 6). Las
   concesiones que fracasaron se otorgaron con Carlos Salinas: es su
   antecedente y se dice en la ficha (`antecedente`), pero la obra ya no se
   cuenta dos veces en el reparto por sexenio.
4. El contador de la pérdida anual toma del FOBAPROA lo que el rescate
   pierde antes del apoyo del presupuesto (déficit del Fondo FOBAPROA más
   las transferencias del Ramo 34 que recibió), no el Ramo 34 solo, que es
   el apoyo y no la pérdida. Se usa 2024 para que coincida con el año de
   los estados de actividades del Tren Maya y del AIFA.

(La decisión 3, la base del presupuesto, no cambia datos: las páginas
explican en un desplegable cuál es el primer monto documentado.)

Corre después de integrar_cuenta_megaobras.py, que recalcula los totales
sobre las 13. Es idempotente.

Uso:
    python3 herramientas/integrar_decisiones_megaobras.py
"""
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from integrar_costo_vivo_megaobras import bloque_json  # noqa: E402


def r1(x):
    return float(Decimal(str(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))


def r2(x):
    return float(Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


RESCATES = {
    'fobaproa': {
        'tipo': 'rescate',
        'sobrecosto_etiqueta': 'Crecimiento frente al pasivo presentado en 1998',
    },
    'farac-carretero': {
        'tipo': 'rescate',
        'sobrecosto_etiqueta': 'Crecimiento frente a las indemnizaciones de 1997',
        'presidente': 'Ernesto Zedillo Ponce de León',
        'periodo_sexenal': '1994–2000',
        'antecedente': 'El rescate se hizo en 1997, con Ernesto Zedillo: el FARAC asumió ese año la deuda bancaria y '
                       'emitió los pagarés con que se indemnizó a 23 concesionarios (ASF, Cuenta Pública 2015, '
                       'auditoría 99; Cuenta Pública 2017, auditoría 96, p. 6). Las concesiones que fracasaron se '
                       'otorgaron de 1989 a 1994, con Carlos Salinas: son el antecedente del rescate, no su costo, y '
                       'por eso la obra se cuenta una sola vez, en el sexenio que la pagó.',
    },
}

# Fondo FOBAPROA, estado de actividades (IPAB, estados financieros
# dictaminados al 31-12-2025, PDF p. 33, columna 2024): déficit del ejercicio
# (22,411,077,805) y transferencias del Programa de Apoyo a Ahorradores
# 62,489,434,983, en pesos.
FOBAPROA_2024 = {'deficit_ejercicio': -22411.1, 'transferencias_ramo34': 62489.4}
FUENTE_IPAB_EF25 = {
    'doc': 'IPAB, Estados financieros dictaminados al 31 de diciembre de 2025, Estado de actividades del Fondo FOBAPROA '
           '(columnas 2025 y 2024), PDF p. 33',
    'url': 'https://www.gob.mx/cms/uploads/attachment/file/1068974/Estados-Financieros_diciembre-2025.pdf',
    'sha256': '8be61d74726f181487eec7d60290706fb73677c7825f720cfdba7b1b4ffe6808',
}


def agregado(lista):
    real = r1(sum(o['inversion_real_mdp'] for o in lista))
    presu = r1(sum(o['inversion_presupuestada_mdp'] for o in lista))
    return {'n': len(lista), 'ids': [o['id'] for o in lista], 'inversion_total_mdp': real,
            'inversion_presupuestada_total_mdp': presu, 'sobrecosto_conjunto_pct': r1((real / presu - 1) * 100)}


def main():
    raw = open(DB, 'rb').read().decode('utf-8')
    a, b = bloque_json(raw, 'simulador_megaobras')
    sim = json.loads(raw[a:b])

    for o in sim['obras']:
        cambio = RESCATES.get(o['id'])
        if cambio:
            o.update(cambio)
        else:
            o.pop('tipo', None)

    # La definicion del FOBAPROA decia 214.1 % y el valor redondeado es 214.0.
    dfb = sim['verificacion']['obras']['fobaproa']['definiciones']
    dfb['sobrecosto_pct'] = dfb['sobrecosto_pct'].replace('= 214.1 %', '= 214.0 %')

    # 4. Perdida del FOBAPROA antes del apoyo del presupuesto.
    of = sim['operacion_oficial']
    of['fuentes']['ipab_ef25'] = FUENTE_IPAB_EF25
    fb = of['obras']['fobaproa']
    if abs(fb['ramo34_ejercido'] - FOBAPROA_2024['transferencias_ramo34']) > 0.05:
        sys.exit('El Ramo 34 de 2024 de la Cuenta Pública (%s) no coincide con el del IPAB (%s)'
                 % (fb['ramo34_ejercido'], FOBAPROA_2024['transferencias_ramo34']))
    fb['deficit_ejercicio'] = FOBAPROA_2024['deficit_ejercicio']
    fb['resultado_sin_transferencias'] = r1(FOBAPROA_2024['deficit_ejercicio'] - FOBAPROA_2024['transferencias_ramo34'])
    fb['fuente_resultado'] = 'ipab_ef25'
    perd_fb = -fb['resultado_sin_transferencias']
    for o in sim['obras']:
        if o['id'] == 'fobaproa':
            o['perdida_anual_mdp'] = perd_fb
            o['perdida_diaria_mdp'] = r2(perd_fb / 365)
            o['perdida_segundo'] = r2(perd_fb * 1e6 / 31536000)

    # 1. Las cifras de conjunto miden las obras; los rescates van aparte.
    obras = [o for o in sim['obras'] if o.get('tipo') != 'rescate']
    rescates = [o for o in sim['obras'] if o.get('tipo') == 'rescate']
    t = sim['totales_consolidados']
    ag_o, ag_r, ag_t = agregado(obras), agregado(rescates), agregado(sim['obras'])
    t['inversion_total_mdp'] = ag_o['inversion_total_mdp']
    t['inversion_presupuestada_total_mdp'] = ag_o['inversion_presupuestada_total_mdp']
    t['sobrecosto_conjunto_pct'] = ag_o['sobrecosto_conjunto_pct']
    t['obras_evaluadas'] = ag_o['n']
    t['rescates'] = dict(ag_r, nota='FOBAPROA y FARAC: deudas que el Estado asumió, no obras. Su «sobrecosto» es cuánto '
                                     'creció lo pagado y lo debido frente a lo presentado en su momento, en pesos de '
                                     'años distintos sin deflactar; no se compara con el de una obra.')
    t['con_rescates'] = dict(ag_t, nota='Las 11 obras y los 2 rescates juntos, solo como referencia.')

    # Perdida anual documentada: deficit de operacion de las empresas que
    # publican estados (sin transferencias) + perdida del FOBAPROA antes del
    # Ramo 34. Mismo calculo que megaobrasOficialBase() del motor.
    empresas = 0.0
    for oid, d in of['obras'].items():
        if oid != 'fobaproa' and d.get('resultado_sin_transferencias', 0) < 0:
            empresas += -d['resultado_sin_transferencias']
    anual = empresas + perd_fb
    t['perdida_operativa_empresas_mdp'] = r1(empresas)
    t['perdida_fobaproa_sin_transferencias_mdp'] = perd_fb
    t['apoyo_presupuestal_fobaproa_ramo34_mdp'] = fb['ramo34_ejercido']
    t['perdida_anual_consolidada_mdp'] = r1(anual)
    t['perdida_diaria_consolidada_mdp'] = r2(anual / 365)
    t['perdida_segundo_consolidada'] = r2(anual * 1e6 / 31536000)
    n_doc = len(of['obras'])
    t['cobertura_obras'] = {'total_obras': len(sim['obras']), 'con_operacion_documentada': n_doc,
                            'pendientes_operacion': len(sim['obras']) - n_doc,
                            'pct_cobertura': r1(n_doc / len(sim['obras']) * 100)}
    t['nota_totales'] = (
        'El costo, lo aprobado y el sobrecosto de conjunto suman las %d obras; los %d rescates (FOBAPROA y FARAC) van '
        'aparte, en «rescates», porque son deudas asumidas y no obras. La pérdida anual suma lo que tiene documento: el '
        'déficit de operación antes de transferencias de las empresas que publican sus estados (Tren Maya; el AIFA no '
        'registra déficit) y lo que el Fondo FOBAPROA pierde antes del apoyo del Ramo 34 (déficit 2024 más las '
        'transferencias que recibió). Las otras %d obras no publican su operación y no se asumen como cero.'
        % (ag_o['n'], ag_r['n'], len(sim['obras']) - n_doc))

    txt = json.dumps(sim, ensure_ascii=False, indent=2).replace('\n', '\r\n')
    raw = raw[:a] + txt + raw[b:]
    open(DB, 'wb').write(raw.encode('utf-8'))
    print(json.dumps({'obras': ag_o, 'rescates': ag_r, 'con_rescates': ag_t,
                      'perdida': [t['perdida_operativa_empresas_mdp'], perd_fb, t['perdida_anual_consolidada_mdp'],
                                  t['perdida_segundo_consolidada']]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
