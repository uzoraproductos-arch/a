"""La inversión pública de cada municipio, 2024 (INEGI, EFIPEM municipal).

El padrón municipal (municipios-efipem.js) se lee por posición en muchos
módulos, así que la inversión no se le agrega: vive en su propio archivo,
assets/auditor/js/municipios-inversion.js (window.AUDIT_MUN_INV), con la
misma clave INEGI de cinco dígitos.

Sale del mismo archivo que usa integrar_rendicion.py (conjunto_de_datos_efipem_municipal_csv.zip,
huella SHA-256 verificada antes de leerlo), año 2024, tema Egresos:

    inv   capítulo «Inversión pública»
    dom   concepto «Obra pública en bienes de dominio público»
    prop  concepto «Obra pública en bienes propios»
    proy  concepto «Proyectos productivos y acciones de fomento»
    disp  capítulo «Disponibilidad final» (lo que quedó en caja al cierre;
          cuenta dentro del egreso total)

En pesos, como los publica el INEGI. Un municipio que rindió su cuenta y no
trae renglón de inversión pública reportó $0 y va con ceros; el que no rindió
cuenta no aparece (sin cifra, no en cero). Se detiene si los tres conceptos no
suman el capítulo, si un municipio no está en el padrón o si el egreso total
no coincide con el del padrón. Idempotente.

    python3 herramientas/anclar_inversion_municipios.py conjunto_de_datos_efipem_municipal_csv.zip
"""
import collections
import csv
import hashlib
import io
import json
import pathlib
import re
import sys
import zipfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'assets' / 'auditor' / 'js' / 'municipios-inversion.js'
PADRON = RAIZ / 'assets' / 'auditor' / 'js' / 'municipios-efipem.js'

SHA_EFM = '6fca09ef2d0529cf93553499a0c7505c12f0d7c2d0dd0bc432acc9687a66b30c'
URL_EFM = 'https://www.inegi.org.mx/contenidos/programas/finanzas/datosabiertos/conjunto_de_datos_efipem_municipal_csv.zip'
ANIO = 2024

CAMPOS = [
    ('inv', 'Capítulo', 'Inversión pública'),
    ('dom', 'Concepto', 'Obra pública en bienes de dominio público'),
    ('prop', 'Concepto', 'Obra pública en bienes propios'),
    ('proy', 'Concepto', 'Proyectos productivos y acciones de fomento'),
    ('disp', 'Capítulo', 'Disponibilidad final'),
]

CABEZA = """/* ===================================================================
   AUDITAVISION - Inversion publica de cada municipio, %d
   -------------------------------------------------------------------
   Generado por herramientas/anclar_inversion_municipios.py. No se edita
   a mano. INEGI, EFIPEM municipal, cifras definitivas, tema Egresos.
   Por clave INEGI de cinco digitos, en pesos:
     [inversion publica, obra en bienes de dominio publico, obra en
      bienes propios, proyectos productivos, disponibilidad final]
   Los municipios que no rindieron su cuenta no aparecen.
   =================================================================== */
"""


def padron():
    """Clave de cinco dígitos → egreso total, de los municipios con cifra."""
    t = PADRON.read_text(encoding='utf-8')
    out = {}
    for m in re.finditer(r'cve: "(\d\d)", n: \d+, conCifra: \d+,[\s\S]*?lista: \[([\s\S]*?)\] \}', t):
        for r in re.findall(r'\[([^\[\]]*)\]', m.group(2)):
            x = json.loads('[' + r + ']')
            out[m.group(1) + x[0]] = x[9] if len(x) >= 10 else None
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    datos = pathlib.Path(sys.argv[1]).read_bytes()
    h = hashlib.sha256(datos).hexdigest()
    if h != SHA_EFM:
        sys.exit('%s: la huella no coincide (%s)' % (sys.argv[1], h))
    z = zipfile.ZipFile(io.BytesIO(datos))
    busca = {(c, d): k for k, c, d in CAMPOS}
    val = collections.defaultdict(lambda: dict.fromkeys([k for k, _c, _d in CAMPOS] + ['egr'], 0))
    with z.open('conjunto_de_datos/efipem_municipal_anual_tr_cifra_%d.csv' % ANIO) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8')):
            if r['TEMA'] != 'Egresos':
                continue
            if r['ESTATUS'] != 'Cifras Definitivas':
                sys.exit('%s: estatus inesperado %r' % (r['CVEGEO'], r['ESTATUS']))
            if (r['CATEGORIA'], r['DESCRIPCION_CATEGORIA']) == ('Tema', 'Total de egresos'):
                val[r['CVEGEO']]['egr'] += int(r['VALOR'])
            k = busca.get((r['CATEGORIA'], r['DESCRIPCION_CATEGORIA']))
            if k:
                val[r['CVEGEO']][k] += int(r['VALOR'])
    pad = padron()
    for c, v in val.items():
        if c not in pad:
            sys.exit('%s: no está en el padrón municipal' % c)
        if pad[c] != v['egr']:
            sys.exit('%s: el egreso total (%s) no es el del padrón (%s)' % (c, v['egr'], pad[c]))
        if v['dom'] + v['prop'] + v['proy'] != v['inv']:
            sys.exit('%s: los tres conceptos no suman la inversión pública' % c)
    con = sum(1 for e in pad.values() if e is not None)
    if len(val) != con:
        sys.exit('El INEGI trae %d municipios con egresos y el padrón %d con cifra' % (len(val), con))
    nac = {k: sum(v[k] for v in val.values()) for k, _c, _d in CAMPOS}
    nac['egr'] = sum(v['egr'] for v in val.values())
    cero = sorted(c for c, v in val.items() if v['inv'] == 0)
    info = {
        'anio': ANIO, 'unidad': 'pesos', 'ref': 'ref-inegi-efipem',
        'fuente': 'INEGI. Estadística de Finanzas Públicas Estatales y Municipales (EFIPEM). Cifras definitivas %d, egresos municipales, datos abiertos.' % ANIO,
        'url': URL_EFM, 'sha256': SHA_EFM,
        'campos': [k for k, _c, _d in CAMPOS], 'conCifra': len(val), 'enCero': len(cero), 'nacional': nac,
    }
    cab = json.dumps(info, ensure_ascii=False)[1:-1]
    filas = ',\n'.join('    "%s":%s' % (c, json.dumps([val[c][k] for k, _c, _d in CAMPOS]))
                       for c in sorted(val))
    SALIDA.write_text((CABEZA % ANIO) + 'window.AUDIT_MUN_INV = {\n  ' + cab + ',\n  "mun": {\n' + filas + '\n  }\n};\n',
                      encoding='utf-8')
    print('municipios-inversion.js: %d municipios, %d en $0; inversión %s de %s pesos de egreso' % (
        len(val), len(cero), format(nac['inv'], ','), format(nac['egr'], ',')))


if __name__ == '__main__':
    main()
