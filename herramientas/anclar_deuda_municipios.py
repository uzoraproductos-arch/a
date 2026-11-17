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
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from anclar_inversion_municipios import SHA_EFM, URL_EFM, ANIO, padron  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'assets' / 'auditor' / 'js' / 'municipios-deuda.js'

SHA_SDA_MUN = '30e258048a398de462a29699a3fdc9de8d1a9749b4a2049c879b6d0e544664b0'
SHA_SDA_RES = '021b95e198528f49c3cfeac15c8d0d86b9c1c5e5f8b12ebc08139811d199e6af'
URL_SDA_MUN = 'https://www.disciplinafinanciera.hacienda.gob.mx/work/models/DISCIPLINA_FINANCIERA/Documentos/SistemaAlertas/2025/Municipio/CP/Informacion%20de%20variables%20SdA%20municipios.xlsx'
URL_SDA_RES = 'https://www.disciplinafinanciera.hacienda.gob.mx/work/models/DISCIPLINA_FINANCIERA/Documentos/SistemaAlertas/2025/Municipio/CP/Resultados%20SdA%20municipios.xlsx'
PAG_SDA_MUN = 'https://www.disciplinafinanciera.hacienda.gob.mx/es/DISCIPLINA_FINANCIERA/Municipios_2025'
CAMPOS_SDA = ['sem', 'dyo', 'deuda', 'ildPct', 'sdPct', 'ocpPct', 'sdMdp', 'ildMdp']

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


def _norm(s):
    s = unicodedata.normalize('NFD', str(s or ''))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def leer_sda(ruta_xlsx):
    """Lee el archivo de variables por municipio del Sistema de Alertas de la
    SHCP (Evaluación de la Cuenta Pública 2025), comprueba su huella SHA-256 y
    que sus subtotales cuadren, y cruza los 670 municipios con el padrón."""
    datos = pathlib.Path(ruta_xlsx).read_bytes()
    h = hashlib.sha256(datos).hexdigest()
    if h != SHA_SDA_MUN:
        sys.exit('%s: la huella del Sistema de Alertas municipal no coincide (%s != %s)' % (ruta_xlsx, h, SHA_SDA_MUN))
    import planisferio
    d_ef = planisferio._padron()
    db_txt = (RAIZ / 'assets' / 'auditor' / 'js' / 'audit-database.js').read_text(encoding='utf-8')
    db = json.loads(db_txt[db_txt.index('{', db_txt.index('window.AUDIT_DB')):].rsplit(';', 1)[0])
    edo_by_norm = {_norm(e['name']): e['abbr'] for e in db['estados']}
    edo_by_norm.update({'coahuila de zaragoza': 'COAH', 'michoacan de ocampo': 'MICH',
                        'veracruz de ignacio de la llave': 'VER', 'estado de mexico': 'MÉX', 'mexico': 'MÉX'})
    mun_by_edo = {}
    for abbr, info in d_ef['ent'].items():
        cve_ent = info['cve']
        mun_by_edo[abbr] = {_norm(r[1]): (cve_ent + r[0], r[1]) for r in info['lista']}

    z = zipfile.ZipFile(io.BytesIO(datos))
    ns = {'a': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    strings = [''.join(t.text or '' for t in si.findall('.//a:t', ns))
               for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('a:si', ns)]
    sroot = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))

    m_out = {}
    verde = amarillo = rojo = sin_info = 0
    tot_dyo = tot_deuda = tot_sd = 0.0
    for row in sroot.findall('.//a:row', ns)[7:]:
        cells = {}
        for c in row.findall('a:c', ns):
            col = re.match(r'[A-Z]+', c.attrib.get('r')).group(0)
            v = c.find('a:v', ns)
            val = v.text if v is not None else ''
            if c.attrib.get('t') == 's' and val.isdigit():
                val = strings[int(val)]
            cells[col] = val.strip()
        if not (cells.get('A') and cells.get('B')):
            continue
        if cells['A'].startswith(('Importante', 'Notas', 'Las ', 'APP:', 'DyO:', 'ILD:', 'IT:', 'OCP:')):
            continue
        abbr = edo_by_norm.get(_norm(cells['A']))
        if not abbr:
            sys.exit('SdA municipal: entidad desconocida %r' % cells['A'])
        m_map = mun_by_edo[abbr]
        mn = _norm(cells['B'])
        hit = m_map.get(mn)
        if not hit:
            cand = [v for k, v in m_map.items() if k in mn or mn in k]
            if len(cand) == 1:
                hit = cand[0]
        if not hit:
            sys.exit('SdA municipal: municipio %r de %s no está en el padrón' % (cells['B'], abbr))
        cve5 = hit[0]
        res = cells.get('C', '')
        if res in ('1', '2', '3'):
            sem = int(res)
            if sem == 1:
                verde += 1
            elif sem == 2:
                amarillo += 1
            else:
                rojo += 1
            f = lambda k: float(cells.get(k) or 0.0)
            dyo = f('J')
            if abs((f('K') + f('O')) - dyo) > 0.05:
                sys.exit('%s (%s): subtotales DyO no cuadran con el total' % (cve5, cells['B']))
            sd = f('R')
            if abs((f('S') + f('W')) - sd) > 0.05:
                sys.exit('%s (%s): subtotales SDyPI no cuadran con el total' % (cve5, cells['B']))
            deuda = f('L') + f('P')
            ild_pct = round(f('D') * 100, 1)
            sd_pct = round(f('F') * 100, 1)
            ocp_pct = round(f('H') * 100, 1)
            ild_mdp = round(f('AE'), 2)
            tot_dyo += dyo
            tot_deuda += deuda
            tot_sd += sd
            m_out[cve5] = [sem, round(dyo, 2), round(deuda, 2), ild_pct, sd_pct, ocp_pct, round(sd, 2), ild_mdp]
        else:
            sin_info += 1
            m_out[cve5] = [0, None, None, None, None, None, None, None]
    if len(m_out) != 670:
        sys.exit('SdA municipal: se esperaban 670 municipios y salieron %d' % len(m_out))
    return {
        'anio': 2025,
        'corte': 'Cuenta Pública 2025',
        'fuente': 'SHCP, Sistema de Alertas de los Municipios, evaluación de la Cuenta Pública 2025 (publicada en 2026)',
        'url': URL_SDA_MUN,
        'urlResultados': URL_SDA_RES,
        'pagina': PAG_SDA_MUN,
        'sha256': SHA_SDA_MUN,
        'sha256Resultados': SHA_SDA_RES,
        'campos': CAMPOS_SDA,
        'resumen': {
            'inscritos': len(m_out),
            'medidos': verde + amarillo + rojo,
            'verde': verde,
            'amarillo': amarillo,
            'rojo': rojo,
            'sinInfo': sin_info,
            'dyoMdp': round(tot_dyo, 1),
            'deudaMdp': round(tot_deuda, 1),
            'sdMdp': round(tot_sd, 1),
        },
        'm': dict(sorted(m_out.items())),
    }


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--sda':
        sda = leer_sda(sys.argv[2])
        actual_txt = SALIDA.read_text(encoding='utf-8')
        actual = json.loads(actual_txt[actual_txt.index('{'):actual_txt.rindex('}') + 1])
        info = {k: actual[k] for k in ('anio', 'unidad', 'ref', 'fuente', 'url', 'sha256', 'campos', 'conCifra', 'nacional', 'cuantos')}
        info['sda'] = sda
        cab = json.dumps(info, ensure_ascii=False)[1:-1]
        val = actual['mun']
        filas = ',\n'.join('    "%s":%s' % (c, json.dumps(val[c])) for c in sorted(val))
        SALIDA.write_text((CABEZA % info['anio']) + 'window.AUDIT_MUN_DEUDA = {\n  ' + cab + ',\n  "mun": {\n' + filas + '\n  }\n};\n', newline='\n',
                          encoding='utf-8')
        r = sda['resumen']
        print('municipios-deuda.js + SdA 2025 CP: %d inscritos (%d medidos: %d verde, %d amarillo, %d rojo; %d sin info); saldo DyO $%s mdp (deuda directa $%s mdp)' % (
            r['inscritos'], r['medidos'], r['verde'], r['amarillo'], r['rojo'], r['sinInfo'], format(r['dyoMdp'], ',.1f'), format(r['deudaMdp'], ',.1f')))
        return
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
    SALIDA.write_text((CABEZA % ANIO) + 'window.AUDIT_MUN_DEUDA = {\n  ' + cab + ',\n  "mun": {\n' + filas + '\n  }\n};\n', newline='\n',
                      encoding='utf-8')
    print('municipios-deuda.js: %d municipios; pagaron deuda %d, pidieron prestado %d; capítulo %s, empréstitos %s, déficit %s pesos' % (
        len(val), cuantos['dp'], cuantos['emp'], format(nac['dp'], ','), format(nac['emp'], ','), format(nac['def'], ',')))


if __name__ == '__main__':
    main()
