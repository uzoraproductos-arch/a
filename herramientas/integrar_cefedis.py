# -*- coding: utf-8 -*-
"""Megafarmacia del Bienestar (CEFEDIS) con su registro en la cartera de
Hacienda, 28-09-2026.

La clave del proyecto, 2312NEF0001, sale de las notas a los estados
financieros de Birmex al 30-09-2024 (nota 14, pp. 42-45). Con ella se
leen los cortes de seguimiento de la cartera de programas y proyectos de
inversión (Transparencia Presupuestaria), cuya huella se comprueba:

- 4T 2023: monto total de inversión $3,614.6 mdp, ejercido en 2023
  $613.0 mdp, avance físico 18 %, estatus «Vigente».
- 4T 2025: monto total de inversión $3,948.6 mdp, avance físico 78 %,
  estatus «En Proceso de Modificación»; operación y mantenimiento previstos
  $10,806.4 mdp en un horizonte de 32 años.
- No aparece en los cortes de seguimiento del 4T 2024 ni del 2T 2026.

Uso:  python3 herramientas/integrar_cefedis.py <carpeta con los CSV>
Solo toca assets/auditor/js/audit-database.js. Idempotente.
"""
import csv
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')
CLAVE = '2312NEF0001'
ARCHIVOS = {
    'SeguimientoOPA4toTrimestre2023.csv': '2e5f0315bc8ef7b68cf00bcd0fd01a838fdc2bad2a6b702ae97424668d72ede2',
    'SeguimientoOPA4toTrimestre2024.csv': '626f3d5408649883031ba87acb3556d3500209d06003f36aa4978920fd5e5e31',
    'SeguimientoOPA4toTrimestre2025.csv': '14cfa99c4e9dc001eecf78b3cc69e079f4a367dc5e85bcf299d685b25953ff75',
    'SeguimientoOPA2doTrimestre2026.csv': '67d0819f18197998a082896f24324e7d3c7af2b3b9c81c2543b31185b40fb6b4',
}
FUENTES = {
    'birmex_notas24': {
        'doc': 'Birmex, notas a los estados financieros al 30 de septiembre de 2024, nota 14 «Negocio en marcha. Megafarmacia», pp. 42-45',
        'url': 'https://datos.birmex.gob.mx/wp-content/uploads/2024/12/notas_estados_financieros.pdf',
        'sha256': 'fb3f36af96e0804a29b2c73a9207a58d21ff9d78270222375485c3da105f7e99',
    },
}


def mdp(x):
    return round(float(x) / 1e6, 1)


def fila(carpeta, nombre):
    ruta = os.path.join(carpeta, nombre)
    h = hashlib.sha256(open(ruta, 'rb').read()).hexdigest()
    if h != ARCHIVOS[nombre]:
        sys.exit('La huella de %s no coincide: %s' % (nombre, h))
    for enc in ('utf-8-sig', 'latin-1'):
        try:
            filas = list(csv.DictReader(open(ruta, encoding=enc)))
            break
        except UnicodeDecodeError:
            continue
    return next((x for x in filas if CLAVE in list(x.values())[0]), None)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    c = sys.argv[1]
    f23 = fila(c, 'SeguimientoOPA4toTrimestre2023.csv')
    f25 = fila(c, 'SeguimientoOPA4toTrimestre2025.csv')
    assert f23 and f25
    assert fila(c, 'SeguimientoOPA4toTrimestre2024.csv') is None
    assert fila(c, 'SeguimientoOPA2doTrimestre2026.csv') is None
    ini, fin = mdp(f23['MONTO_TOTAL_INVERSION']), mdp(f25['MONTO_TOTAL_INVERSION'])
    ej23 = mdp(f23['EJERCIDO'])
    om, anios = mdp(f25['MONTO_OPERACION_MANTENIMIENTO']), int(f25['ANIOS_HE'])
    assert (ini, fin, ej23, om, anios) == (3614.6, 3948.6, 613.0, 10806.4, 32)

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
    bloque = raw[j:k + 1]
    nl = '\r\n' if '\r\n' in bloque else '\n'
    sim = json.loads(bloque)
    ver = sim['verificacion']
    ver['fuentes'].update(FUENTES)
    campos = {'inversion_presupuestada_mdp': 'oficial', 'inversion_real_mdp': 'oficial', 'sobrecosto_pct': 'derivado'}
    hallazgo = ('El Centro Federal de Almacenamiento y Distribución de Insumos para la Salud (CEFEDIS), que contiene la Megafarmacia, '
                'entró a la cartera de Hacienda con la clave 2312NEF0001 (registro el 30-10-2023, autorización el 6-11-2023). '
                'Al 4T 2023 registraba $3,614.6 mdp de inversión y $613.0 mdp ejercidos ese año; al 4T 2025, $3,948.6 mdp, 78 % de avance físico '
                'y estatus «en proceso de modificación». No aparece en los cortes de seguimiento del 4T 2024 ni del 2T 2026.')
    for o in sim['obras']:
        if o['id'] != 'megafarmacia':
            continue
        o['inversion_presupuestada_mdp'] = ini
        o['inversion_real_mdp'] = fin
        o['sobrecosto_pct'] = round((fin / ini - 1) * 100, 1)
        o['estado_campos'] = dict(campos)
        o['hallazgo_asf'] = hallazgo
    ver['obras']['megafarmacia'] = {
        'clave': CLAVE,
        'campos': campos,
        'definiciones': {
            'inversion_presupuestada_mdp': 'Monto total de inversión del CEFEDIS en la cartera de Hacienda, corte 4T 2023, el primero tras su autorización: $3,614.6 mdp.',
            'inversion_real_mdp': 'Monto total de inversión registrado en el corte 4T 2025: $3,948.6 mdp. Es el costo que Hacienda reconoce, no lo pagado: el único ejercicio anual publicado en la cartera es el de 2023, $613.0 mdp.',
            'sobrecosto_pct': 'Cuánto creció el monto de inversión reconocido entre los cortes 4T 2023 y 4T 2025 (cálculo de Auditavisión).',
        },
        'hallazgo': hallazgo,
        'asfHist': [
            {'dato': 'Monto total de inversión, 4T 2023', 'valor': '$3,614.6 mdp', 'estado': 'oficial', 'pagina': 'cartera, corte 4T 2023'},
            {'dato': 'Ejercido en 2023', 'valor': '$613.0 mdp', 'estado': 'oficial', 'pagina': 'cartera, corte 4T 2023'},
            {'dato': 'Monto total de inversión, 4T 2025', 'valor': '$3,948.6 mdp', 'estado': 'oficial', 'pagina': 'cartera, corte 4T 2025'},
            {'dato': 'Operación y mantenimiento previstos en 32 años', 'valor': '$10,806.4 mdp', 'estado': 'oficial', 'pagina': 'cartera, corte 4T 2025'},
            {'dato': 'Avance físico al 4T 2025', 'valor': '78 %', 'estado': 'oficial', 'pagina': 'cartera, corte 4T 2025'},
        ],
        'fuentes': ['opa', 'birmex_notas24'],
    }
    t = sim['totales_consolidados']
    t['inversion_total_mdp'] = round(sum(o['inversion_real_mdp'] for o in sim['obras']), 1)
    t['inversion_presupuestada_total_mdp'] = round(sum(o['inversion_presupuestada_mdp'] for o in sim['obras']), 1)
    t['sobrecosto_conjunto_pct'] = round((t['inversion_total_mdp'] / t['inversion_presupuestada_total_mdp'] - 1) * 100, 1)

    nuevo = json.dumps(sim, ensure_ascii=False, indent=2)
    nuevo = nuevo[:-1] + raw[raw.rfind('\n', 0, k) + 1:k] + '}'
    raw = raw[:j] + nuevo.replace('\n', nl) + raw[k + 1:]
    open(DB, 'wb').write(raw.encode('utf-8'))
    print(json.dumps({'cefedis': [ini, fin, ej23, om, anios], 'totales': {x: t[x] for x in ('inversion_total_mdp', 'inversion_presupuestada_total_mdp', 'sobrecosto_conjunto_pct')}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
