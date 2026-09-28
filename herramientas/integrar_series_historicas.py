# -*- coding: utf-8 -*-
"""Completa el sexenio de Carlos Salinas en la evaluación de los presidentes
(evaluacion_sexenal) con dos series históricas oficiales (28-09-2026):

- PIB: INEGI, Estadísticas históricas de México 2014, cap. 8, cuadro 8.6
  (serie anual 1988-2006, millones de pesos a precios de 1993, valores
  básicos), p. 20 del PDF del capítulo: 1988 = 958,230; 1994 = 1,206,135.
- Deuda: Banco de México, Informe Anual 1994, p. 80: al cierre de 1994 la
  deuda neta total económica amplia del sector público fue 36.9 % del PIB
  (saldo de fin de periodo).

El empleo IMSS de 1988 y 1994 sigue pendiente: estas fuentes solo dan
variaciones porcentuales o derechohabientes, no trabajadores asegurados.

Uso:  python3 herramientas/integrar_series_historicas.py <carpeta>
<carpeta> guarda ehm2014_cap8.pdf y banxico_ia1994.pdf; se comprueba su
huella antes de escribir. Solo toca assets/auditor/js/audit-database.js.
"""
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, 'assets', 'auditor', 'js', 'audit-database.js')

ARCHIVOS = {
    'ehm2014_cap8.pdf': 'e454376e67522481ef7ba88c190f38acc8f75367332a2f74f88cc9f7230b3009',
    'banxico_ia1994.pdf': '56044ed6d2e6f437bcb5ea69c4fb380d83abb4e86e82e23229bc0aff753651a2',
}

FUENTES = {
    'INEGI_EHM2014': {
        'corto': 'INEGI, Estadísticas históricas de México 2014, cuadro 8.6',
        'doc': 'Instituto Nacional de Estadística y Geografía, Estadísticas históricas de México 2014 (2015), capítulo 8 «Información económica agregada», cuadro 8.6 «Producto interno bruto total y por gran división de actividad económica», serie anual de 1988 a 2006, millones de pesos a precios de 1993, valores básicos (página 20 del PDF del capítulo).',
        'url': 'https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/HyM2014/8.%20Informacion%20economica%20agregada.pdf',
        'sha256': ARCHIVOS['ehm2014_cap8.pdf'],
    },
    'BANXICO_IA1994': {
        'corto': 'Banco de México, Informe Anual 1994, p. 80',
        'doc': 'Banco de México, Informe Anual 1994 (1995), apartado «Deuda Neta del Sector Público», p. 80: saldos de fin de periodo de la deuda neta total económica amplia como proporción del PIB al cierre de 1994.',
        'url': 'https://www.banxico.org.mx/publicaciones-y-prensa/informes-anuales/%7B0F2D589F-92A4-9C48-C456-643595B46CE5%7D.pdf',
        'sha256': ARCHIVOS['banxico_ia1994.pdf'],
    },
}

PIB_1988, PIB_1994 = 958230, 1206135

SALINAS_PIB = {
    'promedio': round(((PIB_1994 / PIB_1988) ** (1 / 6) - 1) * 100, 2),
    'acumulado': round((PIB_1994 / PIB_1988 - 1) * 100, 2),
    'base': 1988,
    'cierre': 1994,
    'preliminar': False,
    'estado': 'derivado',
    'fuente': 'INEGI_EHM2014',
    'operacion': 'Tasa media anual: (PIB 1994 / PIB 1988)^(1/6) − 1, con el PIB a precios de 1993: $1,206,135 y $958,230 millones de pesos.',
    'nota': 'La serie del INEGI a precios de 2018, que se usa para los demás sexenios, empieza en 1993. Para Salinas se usa la serie anterior, a precios de 1993 y en valores básicos. Como contraste, esa misma serie da a Zedillo 3.42 % anual (1994-2000), contra 3.48 % con la de 2018: la diferencia entre bases es de décimas.',
}

SALINAS_DEUDA = {
    'cierre': 36.9,
    'anio': 1994,
    'estado': 'oficial',
    'fuente': 'BANXICO_IA1994',
    'nota': 'No es el mismo indicador que el de los demás sexenios. Para 1994 no existe el saldo histórico de los requerimientos financieros (SHRFSP), que Hacienda publica desde 2000; Banxico reportó la deuda neta total «económica amplia», saldo de fin de año. Ese cierre incluye la devaluación de diciembre de 1994, que infló la deuda externa en pesos: en saldo promedio del año fue 24.8 % del PIB (misma página).',
}

ADVERTENCIA = 'La deuda de Salinas (36.9 % del PIB al cierre de 1994) es la deuda neta económica amplia que reportó Banxico, no el SHRFSP de los demás sexenios, y su PIB viene de la serie a precios de 1993. Se comparan con esa salvedad.'


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    for nombre, h in ARCHIVOS.items():
        real = sha(os.path.join(sys.argv[1], nombre))
        if real != h:
            sys.exit('La huella de %s no coincide: %s' % (nombre, real))
    raw = open(DB, 'rb').read().decode('utf-8')
    i = raw.index('"evaluacion_sexenal": {')
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
    ev = json.loads(bloque)
    ev['fuentes'].update(FUENTES)
    s = next(f for f in ev['filas'] if f['id'] == 'salinas')
    s['pib'] = SALINAS_PIB
    s['deuda'] = SALINAS_DEUDA
    if ADVERTENCIA not in ev['advertencias']:
        ev['advertencias'].append(ADVERTENCIA)
    # El bloque original está escrito con indent=2, escapes \uXXXX y dos
    # espacios de sangría extra: se reproduce igual para que el diff muestre
    # solo lo que cambia.
    nuevo = json.dumps(ev, ensure_ascii=True, indent=2)
    nuevo = '\n  '.join(nuevo.split('\n'))
    raw = raw[:j] + nuevo.replace('\n', nl) + raw[k + 1:]
    open(DB, 'wb').write(raw.encode('utf-8'))
    print('Salinas:', json.dumps({'pib': SALINAS_PIB['promedio'], 'acumulado': SALINAS_PIB['acumulado'], 'deuda': SALINAS_DEUDA['cierre']}))


if __name__ == '__main__':
    main()
