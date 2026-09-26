#!/usr/bin/env python3
"""Pone en DB.estados las cifras de la ASF por estado tomadas de la Matriz
de Datos Básicos de la Cuenta Pública 2024 (colección cuenta_publica_asf).

Uso:
    python3 herramientas/integrar_asf_estados.py

Los campos asfMontoObservado, asfAuditorias y asfTipologia de cada estado
traían montos que no coincidían con la matriz oficial (Aguascalientes decía
$428 mdp; la ASF dice $343.3 mdp) y una descripción sin fuente. Este script
los reemplaza por:
- asfMontoObservado: monto por aclarar del estado, en millones de pesos;
- asfAuditorias: auditorías practicadas al dinero federal del estado;
- asfTipologia: una frase armada sólo con cifras de la matriz;
- asfFuente: el documento y sus páginas.

Es idempotente: vuelve a escribir los mismos valores.
"""
import json
import pathlib
import re
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BASE = RAIZ / 'assets' / 'js' / 'audit-database.js'


def norm(t):
    t = unicodedata.normalize('NFD', t)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'^estado de ', '', t)


def mdp(pesos):
    return '${:,.1f} mdp'.format(pesos / 1e6)


def num(n):
    return '{:,}'.format(n)


def main():
    b = BASE.read_bytes().decode('utf-8')
    db, _ = json.JSONDecoder().raw_decode(b[b.index('{', b.index('window.AUDIT_DB')):])
    cp = db['cuenta_publica_asf']
    fuente = 'ASF, Matriz de Datos Básicos de la Cuenta Pública 2024 (corte febrero de 2026), pp. %s' % cp['cp2024']['paginaEntidades']
    entidades = cp['cp2024']['entidades']
    cambios = 0
    for st in db['estados']:
        n = norm(st['name'])
        e = next((x for x in entidades if norm(x['entidad']) == n or norm(x['entidad']).startswith(n + ' ')), None)
        if not e:
            sys.exit('Sin renglón en la matriz para %s; no toco nada.' % st['name'])
        t = e['total']
        frase = ('La ASF practicó %s auditorías al dinero federal que recibió el estado y promovió %s acciones, '
                 'entre ellas %s pliegos de observaciones y %s promociones de responsabilidad administrativa. '
                 'Quedaron %s por aclarar y se recuperaron %s durante las auditorías.') % (
            num(t['auditorias']), num(t['acciones']), num(t['PO']), num(t['PRAS']), mdp(t['porAclarar']), mdp(t['recuperaciones']))
        nuevos = {'asfMontoObservado': round(t['porAclarar'] / 1e6, 1), 'asfAuditorias': t['auditorias'],
                  'asfTipologia': frase, 'asfFuente': fuente}
        ini = b.index('"abbr": %s' % json.dumps(st['abbr'], ensure_ascii=False))
        fin = b.index('"asfTipologia"', ini)
        fin = b.index('\r\n', fin)
        bloque = b[ini:fin]
        m = re.search(r'\r\n( +)"asfMontoObservado": .*?\r\n +"asfAuditorias": .*?\r\n +"asfTipologia": .*$', bloque, re.S)
        if not m:
            sys.exit('No reconozco los campos ASF de %s; no toco nada.' % st['name'])
        sang = m.group(1)
        # Si ya existe asfFuente (segunda corrida), se reescribe también.
        cola = b[fin:]
        ultima = bloque
        if cola.startswith('\r\n' + sang + '"asfFuente"'):
            corte = cola.index('\r\n', 2)
            ultima = cola[:corte]
            cola = cola[corte:]
        coma = ',' if ultima.rstrip().endswith(',') else ''
        linea = ',\r\n'.join('%s"%s": %s' % (sang, k, json.dumps(v, ensure_ascii=False)) for k, v in nuevos.items()) + coma
        b = b[:ini] + bloque[:m.start()] + '\r\n' + linea + cola
        cambios += 1
    BASE.write_bytes(b.encode('utf-8'))
    print('estados actualizados: %d' % cambios)


if __name__ == '__main__':
    main()
