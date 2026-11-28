#!/usr/bin/env python3
"""Las pruebas del agente lector de auditor-ia (Ola 4, entrega B, Ronda 42), sin red.

Corre con Node los mismos casos que `deno test supabase/pruebas/agente_test.ts`
(supabase/pruebas/agente_casos.ts) contra la base publicada del repositorio:
las fichas de asistente-base.js y los datos de docs/fiscal-2027/. Revisa las
tres herramientas de búsqueda, el tope de rondas y el candado de cifras
(sinDocumento) sobre las salidas del modo agente, con un modelo de guion.

Además cuenta aquí, en Python, los datos de docs/fiscal-2027/ y exige que el
agente vea exactamente los mismos: ni uno menos, ni un pendiente con valor.

    python3 herramientas/prueba_agente.py
"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVOS = ['tarifas-y-topes', 'reforma-2027', 'fiscalizacion-y-plazos', 'calendario-y-pendientes-2027']

GUION = r'''
import fs from 'node:fs';
const raiz = process.env.AV_RAIZ + '/';
const A = await import(raiz + 'supabase/functions/_comun/agente.ts');
const { casos } = await import(raiz + 'supabase/pruebas/agente_casos.ts');
const s = fs.readFileSync(raiz + 'assets/auditor/js/asistente-base.js', 'utf8');
const i = s.indexOf('window.AUDITOR_BASE = '), j = s.lastIndexOf('};');
const lee = (n) => JSON.parse(fs.readFileSync(raiz + 'docs/fiscal-2027/' + n + '.json', 'utf8'));
const base = {
  fichas: JSON.parse(s.slice(i + 'window.AUDITOR_BASE = '.length, j + 1)).fichas,
  archivos: Object.fromEntries(A.ARCHIVOS_FISCALES.map((n) => [n, lee(n)])),
  fuentes: lee('fuentes').fuentes,
};
const out = { casos: [], datos: A.datosFiscales(base.archivos).map((d) => [d.id, d.estado]), archivos: A.ARCHIVOS_FISCALES };
for (const [nombre, fn] of casos(base)) {
  try { await fn(); out.casos.push([nombre, null]); } catch (e) { out.casos.push([nombre, String(e && e.message || e)]); }
}
process.stdout.write(JSON.stringify(out));
'''


def datos_python():
    """Los datos de la base fiscal, contados sin pasar por el agente."""
    out = []
    for n in ARCHIVOS:
        with open(os.path.join(RAIZ, 'docs', 'fiscal-2027', n + '.json'), encoding='utf-8') as f:
            j = json.load(f)
        for lista in j.values():
            if isinstance(lista, list):
                out += [[x['id'], x['estado']] for x in lista if isinstance(x, dict) and 'id' in x and 'concepto' in x]
    return out


def prueba():
    try:
        v = subprocess.run(['node', '--version'], capture_output=True, text=True).stdout.strip().lstrip('v').split('.')
        if (int(v[0]), int(v[1])) < (22, 18):
            sys.exit('prueba_agente: hace falta Node 22.18 o posterior (lee TypeScript sin compilar); aquí hay %s' % '.'.join(v))
    except (OSError, ValueError, IndexError):
        sys.exit('prueba_agente: no hay Node para correr los casos')
    r = subprocess.run(['node', '--disable-warning=ExperimentalWarning', '--input-type=module', '-e', GUION],
                       capture_output=True, text=True, cwd=RAIZ, env=dict(os.environ, AV_RAIZ=RAIZ))
    if r.returncode:
        sys.exit('prueba_agente: Node no pudo correr los casos\n' + r.stderr[-3000:])
    out = json.loads(r.stdout)
    mal = [(n, e) for n, e in out['casos'] if e]
    for n, e in out['casos']:
        print('   %s  %s' % ('OK' if not e else 'MAL', n) + ('' if not e else '\n        ' + e))
    if out['archivos'] != ARCHIVOS:
        mal.append(('archivos', 'el agente lee %s y la prueba %s' % (out['archivos'], ARCHIVOS)))
    py = datos_python()
    if out['datos'] != py:
        mal.append(('datos', 'el agente ve %d datos y docs/fiscal-2027/ trae %d' % (len(out['datos']), len(py))))
    if mal:
        sys.exit('prueba_agente: %d fallas\n' % len(mal) + '\n'.join('  %s: %s' % x for x in mal))
    pend = sum(1 for _, e in py if e == 'pendiente')
    print('prueba_agente: %d casos bien; el agente ve los %d datos de la base fiscal (%d pendientes)' % (len(out['casos']), len(py), pend))


if __name__ == '__main__':
    prueba()
