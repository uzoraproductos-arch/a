#!/usr/bin/env python3
"""Los egresos hospitalarios y las cirugías del IMSS-Bienestar en 2025, de la
base de egresos de la Secretaría de Salud (18-11-2026).

Pendiente `salud-imss-bienestar`. Ningún informe del IMSS-Bienestar trae sus
servicios de 2025, pero sus hospitales le reportan cada egreso al Subsistema
Automatizado de Egresos Hospitalarios (SAEH) de la Dirección General de
Información en Salud (DGIS), que lo publica en datos abiertos: un renglón por
egreso, con la CLUES del hospital, y otro archivo con cada procedimiento.

Uso (se corre a mano, con los dos archivos bajados de la DGIS):

    python3 herramientas/anclar_egresos_bienestar.py <ssa_egresos_2025.zip> <ssa_Catalogos_Egresos_2023_2025.zip>

Los archivos están en
http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_egresoshosp_gobmx.html
y escribe docs/salud/imss-bienestar-egresos-2025.json con sus huellas SHA-256.

Cuenta, por institución (la del catálogo de CLUES de la propia DGIS) y por
la entidad donde está el hospital:
  - egr: egresos hospitalarios;
  - egrq: egresos con al menos un procedimiento quirúrgico (tipo «Q» del
    catálogo de tipos de procedimiento);
  - q: procedimientos quirúrgicos.

Se detiene si:
  - un egreso trae una CLUES que no está en el catálogo, o una fecha de
    egreso que no es de 2025;
  - un procedimiento no corresponde a ningún egreso;
  - las entidades no suman el total de la institución;
  - el catálogo no llama «SERVICIOS DE SALUD IMSS BIENESTAR» a la clave IMB.
"""
import collections
import hashlib
import io
import json
import os
import sys
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'docs', 'salud', 'imss-bienestar-egresos-2025.json')
PAGINA = 'http://www.dgis.salud.gob.mx/contenidos/basesdedatos/da_egresoshosp_gobmx.html'
URL = 'http://www.dgis.salud.gob.mx/descargas/datosabiertos/egresos/ssa_egresos_2025.zip'
URL_CAT = 'http://www.dgis.salud.gob.mx/descargas/datosabiertos/egresos/ssa_Catalogos_Egresos_2023_2025.zip'
CLAVES = ['AGS', 'BC', 'BCS', 'CAM', 'COAH', 'COL', 'CHIS', 'CHIH', 'CDMX', 'DGO', 'GTO', 'GRO', 'HGO', 'JAL', 'MÉX', 'MICH',
          'MOR', 'NAY', 'NL', 'OAX', 'PUE', 'QRO', 'QROO', 'SLP', 'SIN', 'SON', 'TAB', 'TAM', 'TLAX', 'VER', 'YUC', 'ZAC']
NOMBRES = {'IMB': 'SERVICIOS DE SALUD IMSS BIENESTAR', 'IMO': 'INSTITUTO MEXICANO DEL SEGURO SOCIAL BIENESTAR', 'SSA': 'SECRETARIA DE SALUD'}


def alto(m):
    raise SystemExit('anclar_egresos_bienestar: ' + m)


def huella(ruta):
    return hashlib.sha256(open(ruta, 'rb').read()).hexdigest()


def renglones(z, nombre, enc='utf-8-sig'):
    with z.open(nombre) as f:
        t = io.TextIOWrapper(f, encoding=enc, newline='')
        h = t.readline().rstrip('\r\n').split('|')
        ix = {k: i for i, k in enumerate(h)}
        for l in t:
            yield ix, l.rstrip('\r\n').split('|')


def catalogo(ruta):
    z = zipfile.ZipFile(ruta)
    n = [x for x in z.namelist() if x.endswith('CATCLUES.csv')]
    if len(n) != 1:
        alto('el ZIP de catálogos no trae un solo CATCLUES.csv')
    cl, nom = {}, {}
    for ix, r in renglones(z, n[0], 'latin-1'):
        cl[r[ix['CLUES']]] = (int(r[ix['CLAVE DE LA ENTIDAD']]), r[ix['CLAVE DE LA INSTITUCION']])
        nom[r[ix['CLAVE DE LA INSTITUCION']]] = r[ix['NOMBRE DE LA INSTITUCION']].strip()
    for k, v in NOMBRES.items():
        if nom.get(k) != v:
            alto('el catálogo llama %r a la clave %s, no %r' % (nom.get(k), k, v))
    return cl, nom


def main():
    if len(sys.argv) != 3:
        alto('uso: anclar_egresos_bienestar.py <ssa_egresos_2025.zip> <ssa_Catalogos_Egresos_2023_2025.zip>')
    ruta, ruta_cat = sys.argv[1:]
    cl, nom = catalogo(ruta_cat)
    z = zipfile.ZipFile(ruta)
    de = {}
    egr = collections.defaultdict(collections.Counter)
    for ix, r in renglones(z, 'Registros/Egresos.txt'):
        c = r[ix['CLUES']]
        if c not in cl:
            alto('el egreso %s trae la CLUES %s, que no está en el catálogo' % (r[ix['ID']], c))
        if not r[ix['EGRESO']].startswith('2025-'):
            alto('el egreso %s es del %s, no de 2025' % (r[ix['ID']], r[ix['EGRESO']]))
        ent, ins = cl[c]
        if not 1 <= ent <= 32:
            alto('la CLUES %s no es de una entidad (%s)' % (c, ent))
        de[r[ix['ID']]] = (ins, ent)
        egr[ins][ent] += 1
    q = collections.defaultdict(collections.Counter)
    conq = collections.defaultdict(set)
    for ix, r in renglones(z, 'Registros/Procedimientos.txt'):
        i = r[ix['ID']]
        if i not in de:
            alto('el procedimiento del egreso %s no tiene egreso' % i)
        if r[ix['TIPO']] == 'Q':
            q[de[i][0]][de[i][1]] += 1
            conq[de[i]].add(i)
    egrq = collections.defaultdict(collections.Counter)
    for (ins, ent), s in conq.items():
        egrq[ins][ent] = len(s)
    inst = {}
    for ins in sorted(egr, key=lambda k: -sum(egr[k].values())):
        tot = {'egr': sum(egr[ins].values()), 'egrq': sum(egrq[ins].values()), 'q': sum(q[ins].values())}
        ent = {CLAVES[e - 1]: {'egr': egr[ins][e], 'egrq': egrq[ins][e], 'q': q[ins][e]} for e in range(1, 33) if egr[ins][e]}
        for k in tot:
            if sum(v[k] for v in ent.values()) != tot[k]:
                alto('%s/%s: las entidades no suman el total' % (ins, k))
        inst[ins] = {'nombre': nom[ins], 'total': tot, 'ent': ent}
    if sum(x['total']['egr'] for x in inst.values()) != len(de):
        alto('las instituciones no suman los egresos de la base')
    out = {
        'fuente': {'tx': 'Secretaría de Salud, DGIS, Subsistema Automatizado de Egresos Hospitalarios (SAEH), registros de egresos hospitalarios 2025 (datos abiertos)',
                   'url': URL, 'pagina': PAGINA, 'sha256': huella(ruta), 'archivo': os.path.basename(ruta)},
        'catalogo': {'tx': 'DGIS, catálogos de egresos hospitalarios 2023-2025 (CATCLUES)', 'url': URL_CAT, 'sha256': huella(ruta_cat)},
        'egresos': len(de),
        'inst': inst,
    }
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    b = inst['IMB']['total']
    print('anclar_egresos_bienestar: %s (%s…). IMSS-Bienestar: %s egresos, %s con cirugía, %s procedimientos quirúrgicos en %d entidades.' % (
        os.path.relpath(SALIDA, RAIZ), out['fuente']['sha256'][:12], b['egr'], b['egrq'], b['q'], len(inst['IMB']['ent'])))


if __name__ == '__main__':
    main()
