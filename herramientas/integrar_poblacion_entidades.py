# -*- coding: utf-8 -*-
"""Población de las 32 entidades a mitad de 2026 (CONAPO), 28-09-2026.

Lee investigaciones/entregas/CONAPO_Poblacion2026_derivada.csv (huella
comprobada; se reproduce con derivar_poblacion.py sobre el original
00_Pob_Mitad_1950_2070.csv) y, en assets/auditor/js/audit-database.js:

- pone en cada entidad su población (`pob`, millones con dos decimales, y
  `pobPersonas`, exacta);
- recalcula `pc`, los Ramos 28 y 33 por habitante: `gasto` × 1e6 ÷
  `pobPersonas`, redondeado al peso;
- marca `fiscalEntidades.campos.pob` y `.pc` como derivados, con la fuente.

Uso:  python3 herramientas/integrar_poblacion_entidades.py
Idempotente.
"""
import csv
import hashlib
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
CSV = os.path.join(RAIZ, 'investigaciones', 'entregas', 'CONAPO_Poblacion2026_derivada.csv')
CSV_SHA = '23700b367c585f6791ba6d47e7dc140cf3623593831a58d73321d8517846a36a'
NOMBRE_DB = {'México': 'Estado de México'}


def main():
    h = hashlib.sha256(open(CSV, 'rb').read()).hexdigest()
    if h != CSV_SHA:
        sys.exit('La huella del CSV no coincide: ' + h)
    filas = list(csv.DictReader(open(CSV, encoding='utf-8-sig', newline='')))[1:]
    assert len(filas) == 32
    pob = {NOMBRE_DB.get(x['ENTIDAD'], x['ENTIDAD']): int(x['POBLACION']) for x in filas}
    assert sum(pob.values()) == 134407258

    raw = open(DB, 'rb').read().decode('utf-8')
    ini = raw.index('"estados": [')
    cambios = []
    for nombre, personas in pob.items():
        k = raw.index('"name": "%s",' % nombre, ini)
        fin = raw.index('"municipios"', k)
        tramo = raw[k:fin]
        gasto = float(re.search(r'"gasto": ([\d.]+),', tramo).group(1))
        pc = round(gasto * 1e6 / personas)
        m = re.search(r'( *)"pob": [\d.]+,\r\n(?: *"pobPersonas": \d+,\r\n)?', tramo)
        sang = m.group(1)
        nuevo = tramo[:m.start()] + '%s"pob": %s,\r\n%s"pobPersonas": %d,\r\n' % (sang, round(personas / 1e6, 2), sang, personas) + tramo[m.end():]
        nuevo, n = re.subn(r'"pc": \d+,', '"pc": %d,' % pc, nuevo, count=1)
        assert n == 1
        raw = raw[:k] + nuevo + raw[fin:]
        cambios.append((nombre, personas, pc))

    # Estado y fuente de los dos campos.
    a = raw.index('"fiscalEntidades": {')
    for campo, texto in (
        ('pob', {'estado': 'derivado', 'ref': None,
                 'fuente': 'CONAPO, Proyecciones de la Población de México y de las Entidades Federativas 2020-2070: población a mitad de 2026, suma de las 110 edades y ambos sexos de cada entidad en el archivo de datos abiertos 00_Pob_Mitad_1950_2070.csv'}),
        ('pc', {'estado': 'derivado', 'ref': None,
                'fuente': 'Ramos 28 y 33 de 2026 de la entidad (anexos del acuerdo de distribución, DOF) entre su población a mitad de 2026 según el CONAPO'}),
    ):
        i = raw.index('"%s": {' % campo, a)
        j = raw.index('}', i) + 1
        sang = ' ' * 6
        cuerpo = {'estado': texto['estado'], 'fuente': texto['fuente'],
                  'url': 'https://repodatos.atdt.gob.mx/CONAPO/proyecciones/00_Pob_Mitad_1950_2070.csv'}
        txt = json.dumps(cuerpo, ensure_ascii=False, indent=2)
        txt = ('\n' + sang).join(txt.split('\n')).replace('\n', '\r\n')
        raw = raw[:i] + '"%s": ' % campo + txt + raw[j:]

    open(DB, 'wb').write(raw.encode('utf-8'))
    print(json.dumps(cambios, ensure_ascii=False))


if __name__ == '__main__':
    main()
