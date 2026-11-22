"""La población de cada municipio (INEGI, Censo de Población y Vivienda 2020).

El padrón municipal (municipios-efipem.js) se lee por posición en muchos
módulos, así que la población no se le agrega: vive en su propio archivo,
assets/auditor/js/municipios-poblacion.js (window.AUDIT_MUN_POB), con la
misma clave INEGI de cinco dígitos.

Sale de los «Principales resultados por localidad (ITER)» del Censo 2020
(iter_00_cpv2020_csv.zip, huella SHA-256 verificada antes de leerlo): el
renglón de cada municipio (LOC 0000), con su población total, mujeres y
hombres. El Censo 2020 es el último conteo completo publicado por el INEGI.

Se detiene si los municipios de una entidad no suman el total de la
entidad, si las entidades no suman el país, o si una clave del Censo no
está en el padrón. Los municipios del padrón que no existían en el Censo
(creados después de 2020) no aparecen: sin cifra, no en cero. Idempotente.

    python3 -I herramientas/anclar_poblacion_municipios.py iter_00_cpv2020_csv.zip
"""
import csv
import hashlib
import io
import json
import pathlib
import re
import sys
import zipfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'assets' / 'auditor' / 'js' / 'municipios-poblacion.js'
PADRON = RAIZ / 'assets' / 'auditor' / 'js' / 'municipios-efipem.js'

SHA_ITER = '9342fdbd45bda5897f2b827a12904843b6f8fb85d4e72da299e09e4d2422ab60'
URL_ITER = 'https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/iter/iter_00_cpv2020_csv.zip'
PAGINA = 'https://www.inegi.org.mx/programas/ccpv/2020/#datos_abiertos'
CSV = 'iter_00_cpv2020/conjunto_de_datos/conjunto_de_datos_iter_00CSV20.csv'

CABEZA = """/* ===================================================================
   AUDITAVISION - Poblacion de cada municipio, Censo 2020
   -------------------------------------------------------------------
   Generado por herramientas/anclar_poblacion_municipios.py. No se edita
   a mano. INEGI, Censo de Poblacion y Vivienda 2020, ITER.
   Por clave INEGI de cinco digitos: [poblacion total, mujeres, hombres].
   Los municipios creados despues del Censo no aparecen.
   =================================================================== */
"""


def padron():
    t = PADRON.read_text(encoding='utf-8')
    ent = re.findall(r'"([^"]+)": \{ cve: "(\d{2})"', t)
    # Las claves se leen por entidad: el padrón repite las de tres dígitos.
    out = set()
    for ab, cve in ent:
        i = t.index('"%s": { cve: "%s"' % (ab, cve))
        j = t.find('": { cve: "', i + 10)
        bloque = t[i:j if j > 0 else len(t)]
        out.update(cve + c for c in re.findall(r'\["(\d{3})",', bloque))
    return out


def main(ruta):
    datos = pathlib.Path(ruta).read_bytes()
    sha = hashlib.sha256(datos).hexdigest()
    if sha != SHA_ITER:
        raise SystemExit('anclar_poblacion_municipios: la huella del archivo no coincide (%s)' % sha)
    z = zipfile.ZipFile(io.BytesIO(datos))
    lector = csv.reader(io.TextIOWrapper(z.open(CSV), encoding='utf-8-sig'))
    cab = next(lector)
    ix = {k: cab.index(k) for k in ('ENTIDAD', 'MUN', 'LOC', 'POBTOT', 'POBFEM', 'POBMAS')}
    mun, ent, nac = {}, {}, None
    for r in lector:
        e, m, l = r[ix['ENTIDAD']], r[ix['MUN']], r[ix['LOC']]
        if l != '0000':
            continue
        v = [int(r[ix['POBTOT']]), int(r[ix['POBFEM']]), int(r[ix['POBMAS']])]
        if e == '00':
            nac = v[0]
        elif m == '000':
            ent[e] = v[0]
        else:
            if v[1] + v[2] != v[0]:
                raise SystemExit('anclar_poblacion_municipios: mujeres + hombres no da la población de %s%s' % (e, m))
            mun[e + m] = v
    for e, tot in ent.items():
        s = sum(v[0] for k, v in mun.items() if k[:2] == e)
        if s != tot:
            raise SystemExit('anclar_poblacion_municipios: los municipios de %s suman %d y la entidad dice %d' % (e, s, tot))
    if sum(ent.values()) != nac or len(ent) != 32:
        raise SystemExit('anclar_poblacion_municipios: las 32 entidades no suman el país')
    pad = padron()
    fuera = sorted(set(mun) - pad)
    if fuera:
        raise SystemExit('anclar_poblacion_municipios: claves del Censo que no están en el padrón: %s' % fuera[:10])
    nuevos = sorted(k for k in pad - set(mun) if k[2:] < '990')
    cab = {
        'anio': 2020, 'unidad': 'personas', 'ref': 'ref-inegi-censo-2020',
        'fuente': 'INEGI. Censo de Población y Vivienda 2020. Principales resultados por localidad (ITER), datos abiertos.',
        'url': URL_ITER, 'pagina': PAGINA, 'sha256': sha, 'nacional': nac,
        'ent': dict(sorted(ent.items())), 'nuevos': nuevos,
    }
    filas = ',\n'.join('    "%s": %s' % (k, json.dumps(mun[k])) for k in sorted(mun))
    cabeza = ', '.join('"%s": %s' % (k, json.dumps(v, ensure_ascii=False)) for k, v in cab.items())
    SALIDA.write_text(CABEZA + 'window.AUDIT_MUN_POB = {\n  ' + cabeza + ',\n  "mun": {\n' + filas + '\n  }\n};\n', encoding='utf-8')
    print('municipios-poblacion.js: %d municipios, %s personas; %d del padrón sin Censo 2020 (%s)' % (
        len(mun), format(nac, ','), len(nuevos), ', '.join(nuevos)))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
