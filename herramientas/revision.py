#!/usr/bin/env python3
"""Revisión automática de un cambio (Bloque 3 del plan, 27-10-2026).

Corre de una vez lo que AGENTS.md §5 pide antes de dar un cambio por hecho,
para que no dependa de que alguien se acuerde. La usa GitHub en cada envío
(.github/workflows/revision.yml) y sirve igual en tu copia:

    python3 herramientas/revision.py                 # todo
    python3 herramientas/revision.py --rapida        # sin navegador
    python3 herramientas/revision.py --base origin/main   # el sello, contra esa rama

Revisa:
  1. node --check de cada .js de assets/auditor/.
  2. Los CR sueltos que deben conservarse (AGENTS.md §4).
  3. Que el sello haya subido si el cambio tocó assets/ (con --base).
  4. El inventario: enlaces rotos y cotejos sin evidencia.
  5. Las preguntas de prueba del Auditor (prueba_auditor.py) y que cada
     página de la Enciclopedia esté en el Auditor, en su modo
     (cobertura_auditor.py).
  6. La guardia de legibilidad, en la fase vigente (GUARDIA_FASE, 0 por omisión).
  7. La base de datos, si el cambio tocó supabase/ y hay PostgreSQL.

Se detiene con error si una sola revisión falla, y al final dice cuáles.
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERR = os.path.join(RAIZ, 'herramientas')

# AGENTS.md §4: CR sueltos que deben conservarse.
CR_SUELTOS = {'index.html': 56, 'assets/auditor/js/audit-engine.js': 2,
              'assets/auditor/js/audit-database.js': 2, 'assets/auditor/css/auditavision.css': 1}


def git(*a):
    return subprocess.run(['git'] + list(a), cwd=RAIZ, capture_output=True, text=True).stdout


def sello_de(texto):
    m = re.search(r'\?v=(\d{8}[a-z]?)', texto)
    return m.group(1) if m else None


def r_node():
    if not shutil.which('node'):
        return 'falta node'
    mal = []
    for f in sorted(glob.glob(os.path.join(RAIZ, 'assets', 'auditor', '**', '*.js'), recursive=True)):
        p = subprocess.run(['node', '--check', f], capture_output=True, text=True)
        if p.returncode:
            mal.append('%s: %s' % (os.path.relpath(f, RAIZ), p.stderr.strip().splitlines()[-1] if p.stderr.strip() else 'error'))
    return '; '.join(mal) or None


def r_cr():
    mal = []
    for f, n in CR_SUELTOS.items():
        b = open(os.path.join(RAIZ, f), 'rb').read()
        sueltos = b.count(b'\r') - b.count(b'\r\n')
        if sueltos != n:
            mal.append('%s tiene %d CR sueltos y debe tener %d' % (f, sueltos, n))
    return '; '.join(mal) or None


def r_sello(base):
    cambios = git('diff', '--name-only', base + '...HEAD').split()
    if not any(c.startswith('assets/') for c in cambios):
        return None
    antes, ahora = sello_de(git('show', base + ':index.html')), sello_de(open(os.path.join(RAIZ, 'index.html'), encoding='utf-8').read())
    if not ahora or (antes and ahora <= antes):
        return 'el cambio toca assets/ y el sello no subió (%s → %s): python3 herramientas/sello.py --siguiente' % (antes, ahora)
    return None


def corre(script, *args, env=None):
    p = subprocess.run([sys.executable, os.path.join(HERR, script)] + list(args), cwd=RAIZ, env=env,
                       capture_output=True, text=True)
    salida = (p.stdout + p.stderr).strip()
    print('   ' + '\n   '.join(salida.splitlines()[-6:]))
    return None if p.returncode == 0 else '%s terminó con error' % script


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--rapida', action='store_true', help='sin navegador (no corre el Auditor ni la guardia)')
    ap.add_argument('--base', help='rama o commit contra el que se revisa el sello y si se tocó supabase/')
    a = ap.parse_args()

    revisiones = [('node --check', r_node), ('CR sueltos', r_cr)]
    if a.base:
        revisiones.append(('sello', lambda: r_sello(a.base)))
    revisiones.append(('inventario', lambda: corre('inventario.py')))
    if not a.rapida:
        revisiones.append(('preguntas del Auditor', lambda: corre('prueba_auditor.py')))
        revisiones.append(('la Enciclopedia en el Auditor', lambda: corre('cobertura_auditor.py')))
        revisiones.append(('guardia de legibilidad', lambda: corre('guardia_legibilidad.py', '--fase', os.environ.get('GUARDIA_FASE', '0'))))
    if a.base and any(c.startswith('supabase/') for c in git('diff', '--name-only', a.base + '...HEAD').split()):
        revisiones.append(('base de datos', lambda: corre('prueba_base_datos.py')))

    fallas = []
    for nombre, fn in revisiones:
        print('▸ %s' % nombre, flush=True)
        r = fn()
        print('   %s' % ('✗ ' + r if r else '✓'), flush=True)
        if r:
            fallas.append(nombre)
    print('revisión: %d de %d bien%s' % (len(revisiones) - len(fallas), len(revisiones),
                                         ('; fallaron: ' + ', '.join(fallas)) if fallas else ''))
    return 1 if fallas else 0


if __name__ == '__main__':
    raise SystemExit(main())
