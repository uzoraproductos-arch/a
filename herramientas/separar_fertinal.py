# -*- coding: utf-8 -*-
"""Separa Fertinal de Agronitrogenados en el simulador de megaobras
(28-09-2026, decisión del autor). Eran dos compras distintas de Pemex,
de años distintos, en una sola ficha y con cifras en dólares.

Cifras en pesos, cotejadas en los PDF de la ASF (huellas comprobadas):

- Agronitrogenados (ProAgro), CP 2017, auditoría 492-DE:
  costo total estimado al aprobar el proyecto, $7,894.2 mdp (19-07-2013,
  p. 4); compra de los activos, $5,427.2 mdp (20-12-2013, p. 4);
  rehabilitación de las dos plantas de urea erogada de septiembre de 2014
  a diciembre de 2017, $8,271.1 mdp (pp. 43-44).
- Fertinal, CP 2016, auditoría 468-DE: compra el 28-01-2016 con 635
  millones de dólares de créditos, $13,121.6 mdp (p. 11): 209.2 millones
  por las acciones y 425.8 millones de refinanciamiento de su deuda.

Uso:  python3 herramientas/separar_fertinal.py
Solo toca assets/auditor/js/audit-database.js. Idempotente.
"""
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
PDF = {
    os.path.join(RAIZ, 'investigaciones', 'entregas', 'ASF_PemexFertilizantes_CP2017_0492.pdf'):
        'd1f61d814ce1e5dd1f2c4d2e291cddf7ba0b651e75e252a8fe163d51ce1527f5',
    os.path.join(RAIZ, 'investigaciones', 'asf-historico', '2016_0468_a.pdf'):
        '7028e6acd9ba71064179ce42229b6ad06dfcb36b349c2370d0626608bb340af3',
}
FUENTE_492 = {
    'doc': 'ASF, Cuenta Pública 2017, auditoría de desempeño 492-DE, Pemex Fertilizantes: Producción, Distribución y Comercialización de Amoniaco, Fertilizantes y sus Derivados',
    'url': 'https://www.asf.gob.mx/Trans/Informes/IR2017c/Documentos/Auditorias/2017_0492_a.pdf',
    'sha256': 'd1f61d814ce1e5dd1f2c4d2e291cddf7ba0b651e75e252a8fe163d51ce1527f5',
}

AGRO_PRES, AGRO_COMPRA, AGRO_REHAB = 7894.2, 5427.2, 8271.1
AGRO_REAL = round(AGRO_COMPRA + AGRO_REHAB, 1)
FERT = 13121.6


def main():
    for ruta, sha in PDF.items():
        h = hashlib.sha256(open(ruta, 'rb').read()).hexdigest()
        if h != sha:
            sys.exit('La huella de %s no coincide: %s' % (ruta, h))

    raw = open(DB, 'rb').read().decode('utf-8')
    i = raw.index('"simulador_megaobras": {')
    j = raw.index('{', i)
    prof = 0
    for k in range(j, len(raw)):
        if raw[k] == '{':
            prof += 1
        elif raw[k] == '}':
            prof -= 1
            if prof == 0:
                break
    sim = json.loads(raw[j:k + 1])
    ver = sim['verificacion']
    ver['fuentes']['asf_fert17'] = FUENTE_492
    obras = sim['obras']
    ag = next(o for o in obras if o['id'] == 'agronitrogenados')

    # 1. Agronitrogenados, solo la planta de Pajaritos y en pesos.
    hall_ag = ('La ASF concluyó que Pemex compró la planta de Agro Nitrogenados sin evaluar el estado de los bienes (llevaba 14 años sin operar) '
               'y que el proyecto pasó de 475 a 760 millones de dólares (CP 2015). En pesos (CP 2017): el proyecto se aprobó con un costo total estimado de '
               '$7,894.2 mdp, la compra costó $5,427.2 mdp y hasta 2017 se habían erogado $8,271.1 mdp en rehabilitar dos plantas de urea que seguían sin producir. '
               'Las otras tres se dieron de baja con una pérdida de $4,206.0 mdp.')
    ag.update({
        'nombre': 'Plantas Chatarra Agronitrogenados',
        'inversion_presupuestada_mdp': AGRO_PRES,
        'inversion_real_mdp': AGRO_REAL,
        'sobrecosto_pct': round((AGRO_REAL / AGRO_PRES - 1) * 100, 1),
        'proyeccion_resumen': 'Pérdida patrimonial. Pemex compró en 2013 cinco plantas de fertilizantes que llevaban 14 años sin operar; a fines de 2017 ninguna producía y tres se dieron de baja.',
        'hallazgo_asf': hall_ag,
        'estado_campos': {'inversion_presupuestada_mdp': 'oficial', 'inversion_real_mdp': 'derivado', 'sobrecosto_pct': 'derivado'},
    })
    campos_ag = dict(ag['estado_campos'])
    ver['obras']['agronitrogenados'] = {
        'campos': campos_ag,
        'definiciones': {
            'inversion_presupuestada_mdp': 'Costo total estimado cuando el consejo de PMI Holdings aprobó el proyecto el 19-07-2013: $7,894.2 mdp, de los que $2,960.3 mdp eran para reiniciar las plantas (ASF, CP 2017, p. 4).',
            'inversion_real_mdp': 'Compra de los activos ($5,427.2 mdp, contrato del 20-12-2013, p. 4) más lo erogado en rehabilitar las plantas de urea I y II de septiembre de 2014 a diciembre de 2017 ($8,271.1 mdp, pp. 43-44). Suma de Auditavisión; no incluye lo gastado después de 2017, que no localizamos.',
            'sobrecosto_pct': 'Cuánto supera lo pagado hasta 2017 al costo total estimado al aprobar el proyecto (cálculo de Auditavisión). Coincide en orden con lo que la ASF documentó en dólares: de 475 a 760 millones, 60.0 % más.',
        },
        'hallazgo': hall_ag,
        'asfHist': [
            {'dato': 'Costo total estimado al aprobar el proyecto (19-07-2013)', 'valor': '$7,894.2 mdp', 'estado': 'oficial', 'pagina': '4 (CP 2017)'},
            {'dato': 'Compra de los activos (20-12-2013)', 'valor': '$5,427.2 mdp', 'estado': 'oficial', 'pagina': '4 (CP 2017)'},
            {'dato': 'Inversión total aprobada, compra más rehabilitación (26-08-2015)', 'valor': '$14,998.9 mdp', 'estado': 'oficial', 'pagina': '5 (CP 2017)'},
            {'dato': 'Rehabilitación de las plantas de urea, 09-2014 a 12-2017', 'valor': '$8,271.1 mdp', 'estado': 'oficial', 'pagina': '43-44 (CP 2017)'},
            {'dato': 'Baja de tres plantas ociosas (deterioro)', 'valor': '$4,206.0 mdp', 'estado': 'oficial', 'pagina': '37 (CP 2017)'},
            {'dato': 'Costo total en dólares, autorizado → final', 'valor': '475 → 760 millones de dólares', 'estado': 'oficial', 'pagina': '26-27 (CP 2015)'},
        ],
        'fuentes': ['asf_fert17', 'asf_agro15'],
    }

    # 2. Fertinal, su propia ficha.
    hall_f = ('Pemex Fertilizantes compró Grupo Fertinal el 28-01-2016 con 635 millones de dólares de créditos ($13,121.6 mdp): 209.2 millones por las acciones '
              'y 425.8 millones para refinanciar sus deudas (ASF, CP 2016, pp. 2 y 11). La ASF dictaminó que la compra «no es un negocio rentable» (p. 38) y que en 2016 '
              'Fertinal registró una pérdida integral de 565.7 millones de dólares, $11,690.6 mdp (p. 31). En 2017 Pemex reconoció como perdidos $4,007.0 mdp '
              'del precio pagado (deterioro del crédito mercantil, CP 2017, p. 37).')
    fert = next((o for o in obras if o['id'] == 'fertinal'), None)
    if fert is None:
        fert = {}
        obras.insert(obras.index(ag) + 1, fert)
    fert.clear()
    fert.update({
        'id': 'fertinal',
        'nombre': 'Compra de Grupo Fertinal',
        'sector_id': 'energia',
        'presidente': 'Enrique Peña Nieto',
        'periodo_sexenal': '2012–2018',
        'icono': '🧪',
        'estatus': 'Filial de Pemex',
        'badge_color': ag.get('badge_color'),
        'inversion_presupuestada_mdp': FERT,
        'inversion_real_mdp': FERT,
        'sobrecosto_pct': 0.0,
        'ingresos_anuales_mdp': 0,
        'costo_operativo_anual_mdp': 0,
        'perdida_anual_mdp': 0,
        'perdida_diaria_mdp': 0,
        'perdida_segundo': 0,
        'proyeccion_tipo': 'perdida_patrimonial',
        'proyeccion_anios': 999,
        'proyeccion_resumen': 'Pérdida patrimonial. Pemex compró en 2016 una empresa de fertilizantes con una mina en Baja California Sur y una planta en Lázaro Cárdenas; la ASF dictaminó que no era un negocio rentable.',
        'desglose_costos_operacion': [],
        'hallazgo_asf': hall_f,
        'unidad_metrica': 'Tonelada de fertilizante',
        'costo_unitario_real': 'pendiente de documento',
        'estado_campos': {'inversion_presupuestada_mdp': 'oficial', 'inversion_real_mdp': 'oficial', 'sobrecosto_pct': 'derivado'},
    })
    ver['obras']['fertinal'] = {
        'campos': dict(fert['estado_campos']),
        'definiciones': {
            'inversion_presupuestada_mdp': 'Lo que Pemex contrató para comprar Fertinal: 635 millones de dólares en créditos, $13,121.6 mdp (ASF, CP 2016, p. 11). No localizamos un presupuesto previo distinto del precio pactado.',
            'inversion_real_mdp': 'Los mismos $13,121.6 mdp. Tras un ajuste de precio se pagaron 629.3 millones de dólares (p. 2); la ASF no da ese monto en pesos.',
            'sobrecosto_pct': 'Sin sobrecosto de compra documentado. Lo que Fertinal le cuesta a Pemex está en lo que perdió después, no en haber pagado más de lo pactado.',
        },
        'hallazgo': hall_f,
        'asfHist': [
            {'dato': 'Financiamiento de la compra (28-01-2016)', 'valor': '635 millones de dólares, $13,121.6 mdp', 'estado': 'oficial', 'pagina': '2 y 11 (CP 2016)'},
            {'dato': 'Precio final de las acciones', 'valor': '203.5 millones de dólares', 'estado': 'oficial', 'pagina': '2 (CP 2016)'},
            {'dato': 'Pérdida integral de 2016', 'valor': '565.7 millones de dólares ($11,690.6 mdp)', 'estado': 'oficial', 'pagina': '31 (CP 2016)'},
            {'dato': 'Deterioro del crédito mercantil', 'valor': '$4,007.0 mdp', 'estado': 'oficial', 'pagina': '37 (CP 2017)'},
        ],
        'fuentes': ['asf_fert16', 'asf_fert17'],
    }

    t = sim['totales_consolidados']
    t['inversion_total_mdp'] = round(sum(o['inversion_real_mdp'] for o in obras), 1)
    t['inversion_presupuestada_total_mdp'] = round(sum(o['inversion_presupuestada_mdp'] for o in obras), 1)
    t['sobrecosto_conjunto_pct'] = round((t['inversion_total_mdp'] / t['inversion_presupuestada_total_mdp'] - 1) * 100, 1)
    t['perdida_anual_consolidada_mdp'] = round(sum(o['perdida_anual_mdp'] for o in obras), 1)
    t['obras_evaluadas'] = len(obras)
    t['nota_totales'] = t['nota_totales'].replace('las 12 obras', 'las %d obras' % len(obras))

    nuevo = json.dumps(sim, ensure_ascii=False, indent=2)
    nuevo = nuevo[:-1] + raw[raw.rfind('\n', 0, k) + 1:k] + '}'
    raw = raw[:j] + nuevo.replace('\n', '\r\n') + raw[k + 1:]
    open(DB, 'wb').write(raw.encode('utf-8'))
    print(json.dumps({'obras': len(obras), 'agro': [AGRO_PRES, AGRO_REAL, ag['sobrecosto_pct']],
                      'totales': {x: t[x] for x in ('inversion_total_mdp', 'inversion_presupuestada_total_mdp', 'sobrecosto_conjunto_pct')}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
