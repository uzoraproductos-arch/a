# -*- coding: utf-8 -*-
"""Enciclomedia y el «Búnker» con los informes de la ASF (28-09-2026).

Enciclomedia. Lo que la Cuenta Pública reportó como ejercido, año por año,
según las auditorías de la ASF (huellas comprobadas, todas en
investigaciones/asf-historico/):

- 2001-2006: $6,417,768.2 miles (CP 2006, auditoría 99, p. 586; 2001-2003
  según el Libro Blanco de la SEP, sin comprobantes).
- 2007: $7,145,765.4 miles en la partida 3414 (CP 2007, auditoría 438, p. 170).
- 2008: $5,817,685.1 miles en la partida 3414 (CP 2008, auditoría 274, p. 589).
- 2009: $3,548,447.4 miles (CP 2009, auditoría 338, p. 1).
- 2010: $4,665,484.5 miles (CP 2010, auditoría 923, p. 1).
- 2011: $4,720,579.8 miles (CP 2011, auditoría 388, p. 1).

Suma: $32,315.7 mdp («derivado»). En 2007 y 2008 es solo la partida 3414,
por la que pasa el 99.0 % del programa (CP 2009, p. 4): es un piso. Los
remanentes que un año se reportaron como ejercidos y se pagaron al
siguiente (1,024.5 y 1,300.0 mdp) se cuentan una sola vez, en el año en que
se reportaron.

Búnker. La ASF auditó en la CP 2009 (auditoría 1053) el contrato de obra
del «Edificio de Plataforma México, en el Distrito Federal» de la
Secretaría de Seguridad Pública: adjudicación directa a TRADECO por
$347,369.0 miles con IVA, reducida a $289,065.5 miles; al cierre de la
auditoría se habían erogado $206,027.9 miles más IVA y quedaban $23,416.9
miles por recuperar. Es un contrato, no el costo del edificio: la inversión
de la ficha sigue pendiente. Que este edificio sea el «búnker» es lectura
de Auditavisión: la ASF no usa esa palabra ni da la dirección.

Uso:  python3 herramientas/integrar_enciclomedia_bunker.py
Solo toca assets/auditor/js/audit-database.js. Idempotente.
"""
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
HIST = os.path.join(RAIZ, 'investigaciones', 'asf-historico')
ASF = 'https://www.asf.gob.mx/Trans/Informes/'

FUENTES = {
    'asf_encic06': ('IR2006_T5V1.pdf', 'e461b1f4b0b5ce298da8f294d824e51bad1b3d05a0797ca2a619608c21e27882',
                    'ASF, Informe del Resultado de la Cuenta Pública 2006, tomo V, vol. 1, auditoría 99, SEP: Evaluación del Programa Enciclomedia',
                    ASF + 'IR2006i/Tomos/T5V1.pdf'),
    'asf_encic07': ('IR2007_T5V2.pdf', 'f6dcf2a80b4cf212e60bca559a8b6ebee0d8c3a3acf9818327dd1662cca7e8ad',
                    'ASF, Informe del Resultado de la Cuenta Pública 2007, tomo V, vol. 2, auditoría 438, SEP: Programa Enciclomedia 5° y 6° Año de Primaria',
                    ASF + 'IR2007i/Tomos/T5V2.pdf'),
    'asf_encic08': ('IR2008_T5V2.pdf', '3a9313a388b7c2b6c1b5b8dc34343096e5ad71d857af5d549930698edbbae720',
                    'ASF, Informe del Resultado de la Cuenta Pública 2008, tomo V, vol. 2, auditoría 274, SEP: Programa E001 «Enciclomedia, 5° y 6° Año de Primaria»',
                    ASF + 'IR2008i/Tomos/T5V2.pdf'),
    'asf_encic09': ('2009_0338_a.pdf', '224c8bf22c0c92758a0c7be2b4e6c9bb689890705b545c337af24ef63546be5a',
                    'ASF, Cuenta Pública 2009, auditoría 338, SEP: Programa E001 «Enciclomedia» 5° y 6° Año de Primaria',
                    ASF + 'IR2009i/Tomos/Tomo4/2009_0338_a.pdf'),
    'asf_encic10': ('2010_0923_a.pdf', '4c1ae5003e22b015968ca84050232de1d974b1ddc7e779e3794211c828d7c6a0',
                    'ASF, Cuenta Pública 2010, auditoría 923, SEP: Programa E001 «Enciclomedia»',
                    ASF + 'IR2010i/Grupos/Desarrollo_Social/2010_0923_a.pdf'),
    'asf_encic11': ('2011_0388_a.pdf', '11ef141e8f641c2d67819b191d6945203a3dd1fdf87075d04124a1f3e04b991f',
                    'ASF, Cuenta Pública 2011, auditoría 388, SEP: Programa E001 «Enciclomedia»',
                    ASF + 'IR2011i/Grupos/Desarrollo_Social/2011_0388_a.pdf'),
    'asf_bunker09': ('2009_1053_a.pdf', 'c25fb6fac3442bd85bccdaa541edd476f0e26a7ee18309bad742d06a506d8593',
                     'ASF, Cuenta Pública 2009, auditoría de inversiones físicas 1053, Secretaría de Seguridad Pública: Edificio de Plataforma México, en el Distrito Federal',
                     ASF + 'IR2009i/Tomos/Tomo2/2009_1053_a.pdf'),
}

# Enciclomedia: ejercido según la Cuenta Pública, en miles de pesos.
ENC_ANIOS = [
    ('2001 a 2006 (2001-2003 según el Libro Blanco)', 6417768.2, '586 (CP 2006)'),
    ('2007, partida 3414', 7145765.4, '170 (CP 2007)'),
    ('2008, partida 3414', 5817685.1, '589 (CP 2008)'),
    ('2009', 3548447.4, '1 (CP 2009)'),
    ('2010', 4665484.5, '1 (CP 2010)'),
    ('2011', 4720579.8, '1 (CP 2011)'),
]
ENC_REAL = round(sum(x[1] for x in ENC_ANIOS) / 1000, 1)
ENC_PRES = 21398.3


def miles(v):
    return '$' + format(round(v / 1000, 1), ',.1f') + ' mdp'


def main():
    for k, (arch, sha, _, _) in FUENTES.items():
        h = hashlib.sha256(open(os.path.join(HIST, arch), 'rb').read()).hexdigest()
        if h != sha:
            sys.exit('La huella de %s no coincide: %s' % (arch, h))
    assert ENC_REAL == 32315.7

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
    for clave, (_, sha, doc, url) in FUENTES.items():
        ver['fuentes'][clave] = {'doc': doc, 'url': url, 'sha256': sha}
    obras = sim['obras']

    # 1. Enciclomedia.
    en = next(o for o in obras if o['id'] == 'enciclomedia')
    hall_en = ('La ASF auditó Enciclomedia casi cada año. En 2006 constató que se habían ejercido $6,417.8 mdp desde 2001 y que de 2001 a 2003 '
               'no había comprobantes de lo que el Libro Blanco decía gastado (CP 2006, pp. 585-587). En 2009 dictaminó en negativo: la SEP reportó un gasto '
               'que no correspondía a lo devengado, no tenía cómo saber si las aulas funcionaban y había aulas sin reparar durante cinco ciclos escolares: 19,650 alumnos se quedaron sin la herramienta '
               '(CP 2009, p. 24). Los 14 contratos de las aulas terminaron en 2011 y la SEP empezó a donar los equipos a los estados (CP 2011, pp. 7-9).')
    en.update({
        'inversion_real_mdp': ENC_REAL,
        'sobrecosto_pct': round((ENC_REAL / ENC_PRES - 1) * 100, 1),
        'proyeccion_resumen': 'Programa extinguido. De 2004 a 2011 la SEP pagó el equipamiento y la renta de aulas con computadora, pizarrón y proyector en 5° y 6° de primaria; al terminar los contratos, en 2011, la SEP empezó a donar los equipos a los estados.',
        'hallazgo_asf': hall_en,
        'estado_campos': {'inversion_presupuestada_mdp': 'oficial', 'inversion_real_mdp': 'derivado', 'sobrecosto_pct': 'derivado'},
    })
    previo = ver['obras'].get('enciclomedia', {})
    hist = [a for a in previo.get('asfHist', []) if 'Autorizado' in a['dato'] or 'Presupuesto original de 2005' in a['dato']]
    hist += [{'dato': 'Ejercido ' + et, 'valor': miles(v), 'estado': 'oficial', 'pagina': pg} for et, v, pg in ENC_ANIOS]
    hist.append({'dato': 'Costo total previsto en el PEF 2006, con vigencia hasta 2009', 'valor': '$17,572.6 mdp', 'estado': 'oficial', 'pagina': '585 (CP 2006)'})
    ver['obras']['enciclomedia'] = {
        'campos': dict(en['estado_campos']),
        'definiciones': {
            'inversion_presupuestada_mdp': 'Recursos que Hacienda autorizó para el servicio multianual de Enciclomedia de 2005 a 2010: $21,398,300.0 miles de pesos para 125,562 aulas (ASF, CP 2005, tomo VI, vol. 2, p. 264).',
            'inversion_real_mdp': ('Suma de Auditavisión de lo que la Cuenta Pública reportó como ejercido cada año, según la ASF: ' +
                                   '; '.join('%s, %s' % (et, miles(v)) for et, v, _ in ENC_ANIOS) +
                                   '. En 2007 y 2008 la ASF solo da la partida 3414, por la que pasa el 99.0 % del programa (CP 2009, p. 4): la suma es un piso. '
                                   'Lo que un año se reportó como ejercido y se pagó al siguiente se cuenta una sola vez. No localizamos pagos posteriores a 2011.'),
            'sobrecosto_pct': 'Cuánto supera lo ejercido de 2001 a 2011 a lo que Hacienda autorizó para el servicio multianual 2005-2010 (cálculo de Auditavisión). '
                              'Lo ejercido incluye piezas que esa autorización no cubría: la compra de las 21,434 aulas del piloto de 2004, la secundaria y la prórroga de 2011.',
        },
        'hallazgo': hall_en,
        'asfHist': hist,
        'fuentes': ['asf_encic05', 'asf_encic06', 'asf_encic07', 'asf_encic08', 'asf_encic09', 'asf_encic10', 'asf_encic11'],
    }

    # 2. Búnker: lo que documenta la ASF; la inversión sigue pendiente.
    bu = next(o for o in obras if o['id'] == 'bunker-garcia-luna')
    hall_bu = ('La ASF auditó en la Cuenta Pública 2009 el contrato de obra del «Edificio de Plataforma México» de la Secretaría de Seguridad Pública: '
               'se adjudicó sin licitación a TRADECO Infraestructura por $347.4 mdp con IVA, se redujo a $289.1 mdp y en agosto de 2010, con la obra ya en operación '
               'pero sin finiquitar, se habían pagado $206.0 mdp más IVA. Observó que la licencia de construcción y el resolutivo de impacto ambiental se obtuvieron '
               'después de iniciar la obra, y $23.4 mdp pagados de más o sin soporte (pp. 1-5).')
    bu['hallazgo_asf'] = hall_bu
    bu['estado_campos'] = {'inversion_presupuestada_mdp': 'pendiente', 'inversion_real_mdp': 'pendiente', 'sobrecosto_pct': 'pendiente'}
    ver['obras']['bunker-garcia-luna'] = {
        'campos': dict(bu['estado_campos']),
        'definiciones': {
            'inversion_presupuestada_mdp': 'Pendiente: los $1,200 mdp que trae la ficha no tienen documento. Lo único documentado es el contrato de obra civil del edificio, adjudicado por $347,369.0 miles de pesos con IVA (ASF, CP 2009, auditoría 1053, p. 1).',
            'inversion_real_mdp': 'Pendiente: los $3,346 mdp que trae la ficha no tienen documento. Del contrato de obra civil se habían erogado $206,027.9 miles de pesos más IVA en agosto de 2010 (p. 2); faltan el equipo tecnológico y los demás contratos, que la ASF no revisó en esta auditoría.',
            'sobrecosto_pct': 'No se puede calcular sin el costo total. El contrato se redujo de $347.4 a $289.1 mdp con IVA (p. 2): no hubo sobrecosto en ese contrato.',
        },
        'hallazgo': hall_bu,
        'asfHist': [
            {'dato': 'Contrato de obra civil adjudicado sin licitación (1-09-2008)', 'valor': '$347.4 mdp con IVA', 'estado': 'oficial', 'pagina': '1 (CP 2009)'},
            {'dato': 'Monto del contrato tras el convenio de reducción (6-04-2009)', 'valor': '$289.1 mdp con IVA', 'estado': 'oficial', 'pagina': '2 (CP 2009)'},
            {'dato': 'Erogado a agosto de 2010, obra en operación sin finiquitar', 'valor': '$206.0 mdp más IVA', 'estado': 'oficial', 'pagina': '2 (CP 2009)'},
            {'dato': 'Pagos de más o sin soporte por recuperar', 'valor': '$23.4 mdp', 'estado': 'oficial', 'pagina': '5 (CP 2009)'},
        ],
        'fuentes': ['asf_bunker09'],
    }

    t = sim['totales_consolidados']
    t['inversion_total_mdp'] = round(sum(o['inversion_real_mdp'] for o in obras), 1)
    t['inversion_presupuestada_total_mdp'] = round(sum(o['inversion_presupuestada_mdp'] for o in obras), 1)
    t['sobrecosto_conjunto_pct'] = round((t['inversion_total_mdp'] / t['inversion_presupuestada_total_mdp'] - 1) * 100, 1)
    t['perdida_anual_consolidada_mdp'] = round(sum(o['perdida_anual_mdp'] for o in obras), 1)

    nuevo = json.dumps(sim, ensure_ascii=False, indent=2)
    nuevo = nuevo[:-1] + raw[raw.rfind('\n', 0, k) + 1:k] + '}'
    raw = raw[:j] + nuevo.replace('\n', '\r\n') + raw[k + 1:]
    open(DB, 'wb').write(raw.encode('utf-8'))
    print(json.dumps({'enciclomedia': [ENC_PRES, ENC_REAL, en['sobrecosto_pct']],
                      'totales': {x: t[x] for x in ('inversion_total_mdp', 'inversion_presupuestada_total_mdp', 'sobrecosto_conjunto_pct')}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
