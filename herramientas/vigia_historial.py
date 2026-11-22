#!/usr/bin/env python3
"""El historial del Vigía de proveedores (Ronda 2, 22-11-2026, pedido del
autor: «guardar cada alta de la 69-B con su fecha para probar aviso previo»).

Uso:
    python3 herramientas/vigia_historial.py            # suma el corte de sat-69b.js
    python3 herramientas/vigia_historial.py --resumen  # solo cuenta, no escribe

Lee la copia de la lista 69-B que ya tiene la plataforma
(assets/auditor/data/sat-69b.js, que escribe actualizar_69b.py) y la suma a
docs/vigia/historial-69b.json: por cada RFC, cada situación con el día en que
la plataforma la vio por primera vez. Con eso se puede probar, con fecha, que
el Vigía avisó de un proveedor presunto antes de que el SAT lo hiciera
definitivo.

Reglas:

- **Solo se anota lo que se vio.** La fecha «vista» es la de la descarga del
  corte (`descarga` del meta de sat-69b.js), no la de hoy, para que dos
  corridas con el mismo archivo den lo mismo. Lo que ya estaba en la lista
  cuando empezó el registro va como «semilla»: no se presume que se avisó
  antes de esa fecha.
- **Las fechas del SAT son oficiales; la ventana de aviso es nuestra
  (derivado)**: días entre la publicación como presunto y como definitivo,
  de las columnas del propio SAT.
- **Las personas físicas no se guardan con su RFC** (decisión del autor,
  18-11-2026): van por la huella SHA-256 de su RFC con la misma sal del padrón
  («av-padron:», 12 caracteres), sin nombre. Las morales, con su RFC, como las
  publica el SAT; el nombre no se guarda aquí (vive en sat-69b.js).
- Un corte ya sumado (misma huella del archivo del SAT) no se vuelve a sumar.

No escribe en docs/sat69b/: la bandeja semanal sigue siendo de vigia_69b.py.
"""
import hashlib
import json
import re
import os
import statistics
import sys
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAT69B = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'sat-69b.js')
SALIDA = os.path.join(RAIZ, 'docs', 'vigia', 'historial-69b.json')
SAL = 'av-padron:'
NOMBRE = {'P': 'Presunto', 'D': 'Desvirtuado', 'F': 'Definitivo', 'S': 'Sentencia Favorable'}


def copia():
    t = open(SAT69B, encoding='utf-8').read()
    d = json.loads(t[t.index('{"meta"'):t.rindex('}') + 1])
    return d['meta'], d['r']


def llave(rfc):
    """Persona moral: su RFC. Persona física: «pf:» y la huella de su RFC."""
    if len(rfc) == 13:
        return 'pf:' + hashlib.sha256((SAL + rfc).encode('utf-8')).hexdigest()[:12]
    return rfc


def _iso(dmy):
    """dd/mm/aaaa → aaaa-mm-dd. El SAT escribe a veces dos fechas en una celda
    («12/04/2022 - 22/02/2021») o una fecha rota («13-03-206»): esas no se
    leen ni se adivinan; el renglón queda fuera de la ventana."""
    if not dmy or not re.fullmatch(r'\d\d/\d\d/\d{4}', dmy):
        return None
    d, m, a = dmy.split('/')
    return '%s-%s-%s' % (a, m, d)


def estados(regs):
    """{llave: situación}. El SAT repite algunos RFC con dos situaciones (un
    definitivo y su sentencia favorable): se guardan juntas, «F+S», y solo
    cuenta como cambio si el conjunto cambia."""
    por = {}
    for r in regs:
        por.setdefault(llave(r[0]), set()).add(r[2])
    return {k: '+'.join(sorted(v)) for k, v in por.items()}


def vacio():
    return {
        'que_es': ('El historial del Vigía de proveedores: cada situación de la lista 69-B del SAT con el día en que la plataforma la vio. '
                   'Sirve para probar con fecha que un aviso llegó antes de que el SAT volviera definitiva a una empresa.'),
        'regla': ('«visto» es la fecha de descarga del corte del SAT. «semilla» = ya estaba en la lista cuando empezó el registro: no se presume '
                  'aviso previo. «alta» = apareció en un corte posterior. «cambio» = pasó a otra situación. Las fechas del SAT son oficiales; '
                  'los días de aviso, derivados.'),
        'privacidad': 'Personas físicas: huella SHA-256 de su RFC (sal «av-padron:», 12 caracteres), sin nombre. Morales: su RFC, sin nombre.',
        'fuente': 'SAT, Listado completo de contribuyentes (Artículo 69-B del CFF)',
        'cortes': [],
        'eventos': {},
    }


def sumar(h, meta, regs):
    """Suma un corte al historial. Devuelve (altas, cambios) que agregó, o
    None si ese archivo del SAT ya estaba sumado."""
    if any(c['sha256'] == meta['sha256'] for c in h['cortes']):
        return None
    semilla = not h['cortes']
    visto = meta['descarga']
    if h['cortes'] and visto < h['cortes'][-1]['visto']:
        raise SystemExit('vigia_historial: el corte que se quiere sumar es más viejo que el último del historial')
    altas = cambios = 0
    for k, st in sorted(estados(regs).items()):
        ev = h['eventos'].get(k)
        if ev is None:
            h['eventos'][k] = [[visto, st, 'semilla' if semilla else 'alta']]
            altas += 0 if semilla else 1
        elif ev[-1][1] != st:
            ev.append([visto, st, 'cambio'])
            cambios += 1
    h['cortes'].append({'visto': visto, 'corte': meta['corte'], 'sha256': meta['sha256'], 'total': meta['total'],
                        'semilla': semilla, 'altas': altas, 'cambios': cambios})
    return altas, cambios


def ventana(regs):
    """Los días entre la publicación como presunto y como definitivo, de las
    columnas del propio SAT (derivado). Solo personas morales con las dos
    fechas y la definitiva después de la presunta."""
    dias = []
    for r in regs:
        if len(r[0]) != 12:
            continue
        p, f = _iso(r[6]), _iso(r[7])
        if p and f and f > p:
            dias.append((date.fromisoformat(f) - date.fromisoformat(p)).days)
    dias.sort()
    return {'n': len(dias), 'mediana': statistics.median(dias), 'p25': dias[len(dias) // 4], 'p75': dias[(3 * len(dias)) // 4],
            'min': dias[0], 'max': dias[-1]}


def avisos(h):
    """RFC vistos como presuntos («alta» o «cambio» a P, nunca «semilla») que
    después se vieron definitivos: los días de aviso que el Vigía dio."""
    out = []
    for k, ev in h['eventos'].items():
        p = next((e[0] for e in ev if 'P' in e[1].split('+') and e[2] != 'semilla'), None)
        f = next((e[0] for e in ev if 'F' in e[1].split('+') and p and e[0] > p), None)
        if p and f:
            out.append((k, p, f, (date.fromisoformat(f) - date.fromisoformat(p)).days))
    return out


def resumen(h, regs):
    pres = sum(1 for v in estados(regs).values() if 'P' in v.split('+'))
    v = ventana(regs)
    a = avisos(h)
    print('Historial del Vigía: %d cortes, %d RFC (desde %s). Presuntos hoy: %d.' % (
        len(h['cortes']), len(h['eventos']), h['cortes'][0]['visto'] if h['cortes'] else '—', pres))
    print('Ventana del SAT (personas morales con las dos fechas, derivado): %d casos; mediana %s días entre presunto y definitivo '
          '(cuartiles %d y %d; de %d a %d).' % (v['n'], format(v['mediana'], 'g'), v['p25'], v['p75'], v['min'], v['max']))
    print('Avisos previos probados con fecha: %d.' % len(a))


def main():
    meta, regs = copia()
    h = json.load(open(SALIDA, encoding='utf-8')) if os.path.exists(SALIDA) else vacio()
    if '--resumen' in sys.argv:
        resumen(h, regs)
        return
    r = sumar(h, meta, regs)
    if r is None:
        print('vigia_historial: el corte %s ya estaba sumado; nada que escribir.' % meta['corte'])
    else:
        os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
        with open(SALIDA, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(h, f, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
            f.write('\n')
        print('vigia_historial: corte %s sumado (%d altas, %d cambios).' % (meta['corte'], r[0], r[1]))
    resumen(h, regs)


if __name__ == '__main__':
    main()
