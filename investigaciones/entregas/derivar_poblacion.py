"""Reproduce los totales derivados de CONAPO sin modificar el CSV original.

Uso: python derivar_poblacion.py RUTA_AL_CSV_ORIGINAL [RUTA_SALIDA]
Solo biblioteca estándar. No descarga ni consulta servicios externos.
"""
import csv
import hashlib
from collections import defaultdict
from pathlib import Path
import sys

ORIGINAL_SHA256 = '89db6adc7930965fb5b5c01ad3a98765ed90afa6a151c2cfb913acc2b9e0cac6'
URL = 'https://repodatos.atdt.gob.mx/CONAPO/proyecciones/00_Pob_Mitad_1950_2070.csv'

def main():
    original = Path(sys.argv[1])
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).with_name('CONAPO_Poblacion2026_derivada.csv')
    assert hashlib.sha256(original.read_bytes()).hexdigest() == ORIGINAL_SHA256, 'El original difiere del documentado'
    totals, names, dimensions = defaultdict(int), {}, set()
    with original.open(encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            if row['ANIO'] != '2026':
                continue
            code = int(row['CVE_GEO'])
            key = (code, row['EDAD'], row['SEXO'])
            assert key not in dimensions, 'Registro repetido'
            dimensions.add(key)
            totals[code] += int(row['POBLACION'])
            names[code] = row['ENTIDAD']
    assert set(totals) == set(range(1, 33))
    assert len(dimensions) == 7040
    for code in totals:
        assert sum(k[0] == code for k in dimensions) == 220
    with output.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ANIO','CVE_GEO','ENTIDAD','POBLACION','ESTADO','OPERACION','FUENTE'])
        writer.writerow([2026,'00','Nacional (suma de 32 entidades)',sum(totals.values()),'derivado','Suma de las 32 entidades, todas las edades y ambos sexos',URL])
        for code in sorted(totals):
            writer.writerow([2026,f'{code:02}',names[code],totals[code],'derivado','Suma de 110 edades y ambos sexos; ANIO=2026',URL])
    print(f'32 entidades, 7040 registros; total nacional derivado: {sum(totals.values()):,}')

if __name__ == '__main__':
    main()
