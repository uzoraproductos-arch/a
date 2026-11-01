#!/usr/bin/env python3
"""Prueba del detector de puntos ciegos (puntos_ciegos.py y ciegos() de
verificador.js).

1. Cada nota «Al momento» de la que aprendimos una regla la sigue disparando:
   si una regla deja de ver su propio ejemplo, algo se rompió.
2. JavaScript y Python encuentran lo mismo en cada texto (las reglas se
   escriben una vez y valen en los dos).
3. Una frase oficial y neutra no dispara nada.
4. Cada regla trae ejemplo, y la página del ejemplo existe.

    python3 herramientas/prueba_puntos_ciegos.py
"""
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import puntos_ciegos as pc  # noqa: E402

# Lo que debe ver en cada nota (al menos esto).
ESPERA = {
    'imss-modalidad-40-gestores': {'porcentaje', 'acusacion'},
    'senado-ley-de-ingresos-2027': {'mas-de'},
    'jalisco-gasto-federal-pef-2027': {'porcentaje', 'comparacion', 'quien', 'periodo'},
    'asf-segunda-entrega-cp2025': {'mas-de'},
    'portacelis-permiso-diesel-sener': {'quien', 'juicio', 'acusacion'},
    'carnaval-ensenada-2026-imcudhe': {'mas-de', 'resultado'},
    'asf-nuevo-leon-triangulacion-cp2025': {'quien', 'acusacion'},
    'lfd-2027-dnr-defensa-tren-maya-aifa': {'promesa', 'porcentaje', 'mas-de', 'juicio'},
    'pemex-3t-2026-perdida-neta': {'porcentaje', 'comparacion', 'dolares', 'resultado'},
    'servidores-ia-exportaciones-contenido-nacional': {'porcentaje', 'comparacion', 'dolares', 'quien', 'proyeccion'},
    'agua-guadalajara-14500-federal': {'promesa', 'sin-costo'},
}
NEUTRAS = [
    'Según el PEF 2026, el gasto aprobado del Ramo 12 es de 1,000 millones de pesos.',
    'La Cuenta Pública 2025 reporta el gasto ejercido por ramo.',
]

JS = r'''
global.window = {};
require(process.argv[1]);
const D = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const V = window.AuditorVerifica({ cat: [], ciegos: D.reglas });
console.log(JSON.stringify(D.textos.map(t => V.ciegos({ texto: t }).map(x => [x.r.id, x.frase.toLowerCase()]))));
'''


def main():
    import integrar_al_momento as m
    mal = []
    notas = {n()['id']: n()['circula']['texto'] for n in m.NOTAS}
    for i, esp in ESPERA.items():
        if i not in notas:
            mal.append('la nota %s ya no existe' % i)
            continue
        vio = {r for r, _f in pc.detecta(notas[i])}
        if not esp <= vio:
            mal.append('%s: no ve %s' % (i, ', '.join(sorted(esp - vio))))
    for t in NEUTRAS:
        if pc.detecta(t):
            mal.append('frase neutra «%s» dispara %s' % (t, pc.detecta(t)))
    for r in pc.REGLAS:
        if not r['de']:
            mal.append('la regla %s no trae ejemplo' % r['id'])
        for i, _t in r['de']:
            if not os.path.exists(os.path.join(RAIZ, pc.AL_MOMENTO % i)):
                mal.append('la regla %s cita %s, que no existe' % (r['id'], pc.AL_MOMENTO % i))
    textos = list(notas.values()) + NEUTRAS
    out = subprocess.run(['node', '-e', JS, os.path.join(RAIZ, 'assets/auditor/js/verificador.js')],
                         input=json.dumps({'reglas': pc.datos(), 'textos': textos}), capture_output=True, text=True)
    if out.returncode:
        mal.append('node: ' + out.stderr.strip()[:300])
    else:
        js = json.loads(out.stdout)
        for t, j in zip(textos, js):
            py = [[r, pc.plano(f)] for r, f in pc.detecta(t)]
            jj = [[r, pc.plano(f)] for r, f in j]
            if py != jj:
                mal.append('JavaScript y Python no coinciden en «%s…»: %s contra %s' % (t[:40], jj, py))
    for x in mal:
        print('✗ ' + x)
    print('puntos ciegos: %d reglas, %d notas, %s' % (len(pc.REGLAS), len(ESPERA), 'bien' if not mal else '%d fallas' % len(mal)))
    return 1 if mal else 0


if __name__ == '__main__':
    sys.exit(main())
