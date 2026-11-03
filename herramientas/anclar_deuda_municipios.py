"""La deuda de cada municipio en su cuenta de 2024 (INEGI, EFIPEM municipal).

Lo que se puede sostener con documento público, sin solicitud de acceso:
lo que cada municipio PAGÓ de deuda en el año y lo que PIDIÓ PRESTADO en el
año, tal como lo rindió en su cuenta pública al INEGI. El SALDO (lo que debe
al cierre) lo publica Hacienda en el Sistema de Alertas y el Registro Público
Único; mientras su portal no responda, sigue «pendiente» (ficha
deuda-municipios de leyes_niveles.py).

Como la inversión, vive en su propio archivo
(assets/auditor/js/municipios-deuda.js, window.AUDIT_MUN_DEUDA), nunca como
columna nueva del padrón, que se lee por posición. Sale del mismo archivo que
anclar_inversion_municipios.py (conjunto_de_datos_efipem_municipal_csv.zip,
huella SHA-256 verificada antes de leerlo), año 2024:

    Egresos, capítulo «Deuda pública», y sus conceptos:
      dp    el capítulo completo
      am    Amortización de la deuda pública (el capital que devolvió)
      int   Intereses de la deuda pública
      cf    Comisiones + Gastos de la deuda pública + Costo por coberturas
      adefas Adeudos de ejercicios fiscales anteriores (lo que quedó a deber
            el año anterior, sobre todo a proveedores: no es crédito bancario)
    Ingresos, capítulo «Financiamiento»:
      emp   concepto «Empréstitos» (lo que pidió prestado en el año)
    El otro concepto del capítulo, «Déficit», NO es un préstamo: es el renglón
    con que el INEGI cuadra el ingreso con el egreso. Por eso no se guarda por
    municipio y el capítulo no se presenta como «deuda nueva»; su suma nacional
    va en la cabecera para decirlo con la cifra.

En pesos, como los publica el INEGI. Un municipio que rindió su cuenta y no
trae esos renglones reportó $0; el que no rindió cuenta no aparece. Se detiene
si los conceptos no suman su capítulo, si un municipio no está en el padrón o
si el egreso total no coincide con el del padrón. Idempotente.

    python3 herramientas/anclar_deuda_municipios.py conjunto_de_datos_efipem_municipal_csv.zip
"""
import collections
import csv
import hashlib
import io
import json
import pathlib
import sys
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from anclar_inversion_municipios import SHA_EFM, URL_EFM, ANIO, padron  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'assets' / 'auditor' / 'js' / 'municipios-deuda.js'

# (campo, tema, categoría, descripción)
CAMPOS = [
    ('dp', 'Egresos', 'Capítulo', 'Deuda pública'),
    ('am', 'Egresos', 'Concepto', 'Amortización de la deuda pública'),
    ('int', 'Egresos', 'Concepto', 'Intereses de la deuda pública'),
    ('cf', 'Egresos', 'Concepto', 'Comisiones de la deuda pública'),
    ('cf', 'Egresos', 'Concepto', 'Gastos de la deuda pública'),
    ('cf', 'Egresos', 'Concepto', 'Costo por coberturas'),
    ('adefas', 'Egresos', 'Concepto', 'Adeudos de ejercicios fiscales anteriores (ADEFAS)'),
    ('emp', 'Ingresos', 'Concepto', 'Empréstitos'),
    ('fin', 'Ingresos', 'Capítulo', 'Financiamiento'),
    ('def', 'Ingresos', 'Concepto', 'Déficit'),
    ('egr', 'Egresos', 'Tema', 'Total de egresos'),
]
GUARDA = ['dp', 'am', 'int', 'cf', 'adefas', 'emp']

CABEZA = """/* ===================================================================
   AUDITAVISION - La deuda en la cuenta de cada municipio, %d
   -------------------------------------------------------------------
   Generado por herramientas/anclar_deuda_municipios.py. No se edita a
   mano. INEGI, EFIPEM municipal, cifras definitivas.
   Por clave INEGI de cinco digitos, en pesos:
     [capitulo deuda publica, amortizacion, intereses, comisiones gastos
      y coberturas, ADEFAS, emprestitos recibidos]
   Es lo que PAGO y lo que PIDIO PRESTADO en el ano, no lo que debe.
   Los municipios que no rindieron su cuenta no aparecen.
   =================================================================== */
"""


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    datos = pathlib.Path(sys.argv[1]).read_bytes()
    h = hashlib.sha256(datos).hexdigest()
    if h != SHA_EFM:
        sys.exit('%s: la huella no coincide (%s)' % (sys.argv[1], h))
    z = zipfile.ZipFile(io.BytesIO(datos))
    busca = {(t, c, d): k for k, t, c, d in CAMPOS}
    claves = sorted({k for k, _t, _c, _d in CAMPOS})
    val = collections.defaultdict(lambda: dict.fromkeys(claves, 0))
    with z.open('conjunto_de_datos/efipem_municipal_anual_tr_cifra_%d.csv' % ANIO) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8')):
            if r['TEMA'] == 'Egresos' and r['ESTATUS'] != 'Cifras Definitivas':
                sys.exit('%s: estatus inesperado %r' % (r['CVEGEO'], r['ESTATUS']))
            k = busca.get((r['TEMA'], r['CATEGORIA'], r['DESCRIPCION_CATEGORIA']))
            if k:
                val[r['CVEGEO']][k] += int(r['VALOR'])
    pad = padron()
    for c, v in val.items():
        if c not in pad:
            sys.exit('%s: no está en el padrón municipal' % c)
        if pad[c] != v['egr']:
            sys.exit('%s: el egreso total (%s) no es el del padrón (%s)' % (c, v['egr'], pad[c]))
        if v['am'] + v['int'] + v['cf'] + v['adefas'] != v['dp']:
            sys.exit('%s: los conceptos no suman el capítulo de deuda pública' % c)
        if v['emp'] + v['def'] != v['fin']:
            sys.exit('%s: empréstitos y déficit no suman el capítulo de financiamiento' % c)
    con = sum(1 for e in pad.values() if e is not None)
    if len(val) != con:
        sys.exit('El INEGI trae %d municipios con cuenta y el padrón %d con cifra' % (len(val), con))
    nac = {k: sum(v[k] for v in val.values()) for k in claves}
    cuantos = {k: sum(1 for v in val.values() if v[k]) for k in ('dp', 'am', 'int', 'adefas', 'emp')}
    cuantos['banco'] = sum(1 for v in val.values() if v['am'] or v['int'] or v['cf'])
    info = {
        'anio': ANIO, 'unidad': 'pesos', 'ref': 'ref-inegi-efipem',
        'fuente': 'INEGI. Estadística de Finanzas Públicas Estatales y Municipales (EFIPEM). Cifras definitivas %d, municipales, datos abiertos.' % ANIO,
        'url': URL_EFM, 'sha256': SHA_EFM, 'campos': GUARDA, 'conCifra': len(val),
        'nacional': nac, 'cuantos': cuantos,
    }
    cab = json.dumps(info, ensure_ascii=False)[1:-1]
    filas = ',\n'.join('    "%s":%s' % (c, json.dumps([val[c][k] for k in GUARDA])) for c in sorted(val))
    SALIDA.write_text((CABEZA % ANIO) + 'window.AUDIT_MUN_DEUDA = {\n  ' + cab + ',\n  "mun": {\n' + filas + '\n  }\n};\n',
                      encoding='utf-8')
    print('municipios-deuda.js: %d municipios; pagaron deuda %d, pidieron prestado %d; capítulo %s, empréstitos %s, déficit %s pesos' % (
        len(val), cuantos['dp'], cuantos['emp'], format(nac['dp'], ','), format(nac['emp'], ','), format(nac['def'], ',')))


if __name__ == '__main__':
    main()
