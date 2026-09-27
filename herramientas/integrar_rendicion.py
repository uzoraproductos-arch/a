"""Rendición de cuentas de estados y municipios para el Modo Inspector.

El inspector responde, de cada autoridad, cuatro preguntas: de qué vive, si
rindió cuentas, si sus cifras cuadran con las de otra fuente oficial y qué le
encontró la Auditoría Superior. Para los niveles estatal y municipal se cruzan
aquí cinco documentos oficiales, sin estimar nada:

1. SHCP, Cuenta Pública 2024, base de datos abierta (cuenta_publica_2024_gf_ecd_epe.csv):
   lo que la Federación pagó a cada entidad por los Ramos 28 y 33. Se contrasta
   con lo que la propia entidad reportó al INEGI como recibido
   (herramientas/anclar_ingresos_entidades.py, tabla INGRESOS).
2. INEGI, EFIPEM municipal 1989-2025 (conjunto_de_datos_efipem_municipal_csv.zip,
   versión del 13-08-2026): qué años, de 2016 a 2025, cada municipio entregó su
   cuenta al INEGI, y, para quien no entregó la de 2024, la última que sí entregó.
   2025 es preliminar: no haber aparecido todavía no es haber incumplido.
3. SHCP, Sistema de Recursos Federales Transferidos, informe definitivo 2024
   (ejercicio_del_gasto_2024.zip, archivo ejercicio_del_gasto.csv): lo que cada
   municipio le informó a Hacienda haber recibido y pagado del FAIS municipal
   (I004) y del FORTAMUN (I005) de 2024. El FAIS se informa además obra por
   obra en el componente «Destino del gasto» (ef2024.zip): un municipio que
   no llenó el primero puede haber llenado el segundo, y entonces sí informó.
4. INAFED, «Presidentas y presidentes municipales» (datos.gob.mx): quién gobernó
   cada municipio, con qué partido o coalición y en qué periodo.
5. ASF, Matriz de Datos Básicos de la CP 2024 (investigaciones/datos-matriz-asf2024.json):
   las 1,056 auditorías integrales a municipios y alcaldías.

Escribe assets/auditor/js/municipios-rendicion.js (window.AUDIT_MUN_RENDICION), el
bloque "inspector_estatal" de audit-database.js y las referencias 111 a 113.
Verifica la huella SHA-256 de cada archivo antes de leerlo. Idempotente.

    python3 herramientas/integrar_rendicion.py CP2024.csv EFIPEM_MUN.zip SRFT_EJERCICIO.csv INAFED.csv SRFT_DESTINO.zip
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
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from integrar_glosario_modulos import _cuerpo  # noqa: E402
from anclar_ingresos_entidades import INGRESOS  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BASE = RAIZ / 'assets' / 'auditor' / 'js' / 'audit-database.js'
SALIDA = RAIZ / 'assets' / 'auditor' / 'js' / 'municipios-rendicion.js'
MATRIZ = RAIZ / 'investigaciones' / 'datos-matriz-asf2024.json'

SHA_CP = '94cd87dfb1f0dbcb27886d5792046c9c6d96eeab2878f898c8a9813ef1fdf6de'
SHA_EFM = '6fca09ef2d0529cf93553499a0c7505c12f0d7c2d0dd0bc432acc9687a66b30c'
SHA_SRFT = '091307f00884a6caa35a0dc53eb314a961a61d26894b21bcec5b3a1e68c434f8'
SHA_DESTINO = '63656106a607d59fcf74e92574a95ac46c44b2beef7d328acf4959e416f39c34'
SHA_INAFED = '919f5ceaa81e3a4d64f846c5603271284d6f4b813e879b786139206f93bc9e99'

URL_CP = 'https://www.transparenciapresupuestaria.gob.mx/work/models/PTP/DatosAbiertos/BD_Cuenta_Publica/CSV/cuenta_publica_2024_gf_ecd_epe.csv'
URL_EFM = 'https://www.inegi.org.mx/contenidos/programas/finanzas/datosabiertos/conjunto_de_datos_efipem_municipal_csv.zip'
URL_SRFT = 'https://www.transparenciapresupuestaria.gob.mx/work/models/PTP/DatosAbiertos/Entidades_Federativas/2024/ejercicio_del_gasto_2024.zip'
URL_DESTINO = 'https://www.transparenciapresupuestaria.gob.mx/work/models/PTP/DatosAbiertos/Entidades_Federativas/2024/ef2024.zip'
URL_INAFED = 'https://www.datos.gob.mx/dataset/presidentas_presidentes_municipales'

ANIOS = list(range(2016, 2026))

REF_NUEVAS = [
    {
        'num': 111,
        'id': 'ref-shcp-cp2024-datos',
        'categoria': 'fuentes_oficiales',
        'categoria_nombre': 'Fuentes Oficiales & Datos Abiertos',
        'cita_apa': 'Secretaría de Hacienda y Crédito Público. (2025). Cuenta Pública 2024: base de datos abierta de ramos administrativos, generales y autónomos, entidades de control directo y empresas productivas del Estado [archivo CSV]. Transparencia Presupuestaria.',
        'url': URL_CP,
        'descripcion': 'Incluye la clasificación geográfica del gasto: lo que la Federación pagó a cada entidad por participaciones (Ramo 28) y aportaciones (Ramo 33) en 2024. El Modo Inspector lo contrasta con lo que cada gobierno estatal reportó haber recibido. Huella SHA-256 del archivo consultado: ' + SHA_CP + '.',
    },
    {
        'num': 112,
        'id': 'ref-shcp-srft-2024',
        'categoria': 'fuentes_oficiales',
        'categoria_nombre': 'Fuentes Oficiales & Datos Abiertos',
        'cita_apa': 'Secretaría de Hacienda y Crédito Público. (2025). Gasto federalizado: ejercicio del gasto, informe definitivo 2024 (Sistema de Recursos Federales Transferidos) [archivo CSV]. Transparencia Presupuestaria.',
        'url': URL_SRFT,
        'descripcion': 'Lo que cada estado y cada municipio le informa a Hacienda sobre el dinero federal que recibió y cómo lo gastó, como manda el artículo 85 de la Ley Federal de Presupuesto y Responsabilidad Hacendaria. De aquí sale, municipio por municipio, lo recibido y lo pagado del FAIS municipal y del FORTAMUN de 2024 (componente Ejercicio del gasto) y el monto de las obras que registró con esos fondos (componente Destino del gasto, ' + URL_DESTINO + '). Huellas SHA-256: ejercicio_del_gasto.csv ' + SHA_SRFT + '; ef2024.zip ' + SHA_DESTINO + '.',
    },
    {
        'num': 113,
        'id': 'ref-inafed-presidencias',
        'categoria': 'fuentes_oficiales',
        'categoria_nombre': 'Fuentes Oficiales & Datos Abiertos',
        'cita_apa': 'Instituto Nacional para el Federalismo y el Desarrollo Municipal. (2025). Presidentas y presidentes municipales [conjunto de datos]. datos.gob.mx.',
        'url': URL_INAFED,
        'descripcion': 'Quién encabeza cada ayuntamiento, con qué partido, coalición o sistema normativo llegó y el periodo de su gobierno. La versión consultada registra, en casi todos los municipios, a la administración que gobernó la mayor parte de 2024, no a la que entró en el otoño de ese año. Huella SHA-256 del archivo: ' + SHA_INAFED + '.',
    },
]


def huella(ruta, sha):
    datos = pathlib.Path(ruta).read_bytes()
    h = hashlib.sha256(datos).hexdigest()
    if h != sha:
        sys.exit('%s: la huella no coincide (%s)' % (ruta, h))
    return datos


def num(x):
    x = (x or '').strip().replace(',', '')
    return float(x) if x not in ('', '-') else 0.0


def norm(x):
    x = unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z ]', ' ', x)).strip()


def mdp(p):
    return round(p / 1e6, 1)


# --- 1. Estados: lo que reportaron contra lo que la Federación pagó ---------
def estados(ruta):
    texto = huella(ruta, SHA_CP).decode('latin-1')
    pag = collections.defaultdict(float)
    for r in csv.DictReader(io.StringIO(texto)):
        ramo = r['ID_RAMO'].strip()
        if ramo in ('28', '33'):
            pag[(int(r['ID_ENTIDAD_FEDERATIVA']), ramo)] += num(r['MONTO_PAGADO'])
    out = {}
    for abbr, v in INGRESOS.items():
        cve = int(v[0])
        part, aport, reasig = v[8], v[9], v[12]
        out[abbr] = {
            'inegiPart': mdp(part), 'inegiAportSinConvenios': mdp(aport - reasig),
            'cpR28': mdp(pag[(cve, '28')]), 'cpR33': mdp(pag[(cve, '33')]),
        }
    out['CDMX'] = {'inegiPart': None, 'inegiAportSinConvenios': None,
                   'cpR28': mdp(pag[(9, '28')]), 'cpR33': mdp(pag[(9, '33')])}
    return out


# --- 2. INEGI: historial de entrega, 2016-2025 -------------------------------
def historial(ruta):
    z = zipfile.ZipFile(io.BytesIO(huella(ruta, SHA_EFM)))
    rep = collections.defaultdict(dict)   # cvegeo -> anio -> [ing, part, aport]
    for anio in ANIOS:
        nom = 'conjunto_de_datos/efipem_municipal_anual_tr_cifra_%d.csv' % anio
        with z.open(nom) as f:
            for r in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8')):
                if r['TEMA'] != 'Ingresos':
                    continue
                d = r['DESCRIPCION_CATEGORIA']
                i = {'Total de ingresos': 0, 'Participaciones federales': 1,
                     'Aportaciones federales y estatales': 2}.get(d)
                if i is None or r['CATEGORIA'] not in ('Tema', 'Capítulo'):
                    continue
                rep[r['CVEGEO']].setdefault(anio, [0, 0, 0])[i] = int(r['VALOR'])
    return rep


# --- 3. SRFT: lo que el municipio le dijo a Hacienda -------------------------
def srft(ruta):
    texto = huella(ruta, SHA_SRFT).decode('latin-1')
    s = collections.defaultdict(lambda: [0.0] * 4)   # recibido FAIS, recibido FORTAMUN, pagado FAIS, pagado FORTAMUN
    nombres = {}
    for r in csv.DictReader(io.StringIO(texto)):
        if r['ID_MUNICIPIO'] == '0' or r['CICLO_RECURSO'] != '2024' or r['TRIMESTRE'] != '5':
            continue
        if r['MODALIDAD_PP'] not in ('I004', 'I005'):
            continue
        cve = '%02d%03d' % (int(r['ID_ENTIDAD_FEDERATIVA']), int(r['ID_MUNICIPIO']))
        j = 0 if r['MODALIDAD_PP'] == 'I004' else 1
        s[cve][j] += num(r['MONTO_RECAUDADO'])
        s[cve][j + 2] += num(r['MONTO_PAGADO'])
        nombres[cve] = r['MUNICIPIO']
    return s, nombres


def destino(ruta):
    """FAIS y FORTAMUN 2024 de las obras y acciones que cada municipio
    registró en el componente Destino del gasto (monto modificado)."""
    z = zipfile.ZipFile(io.BytesIO(huella(ruta, SHA_DESTINO)))
    fol = {}
    with z.open('ef2024/fuentes_financiamiento.csv') as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding='latin-1', newline='')):
            if r['CICLO_RECURSO'] == '2024' and r['ID_RAMO'] == '33' and r['ID_MODALIDAD'] == 'I' and r['ID_PP'] in ('4', '5'):
                fol.setdefault(r['FOLIO'], []).append((0 if r['ID_PP'] == '4' else 1, num(r['MONTO_MODIFICADO'])))
    out = collections.defaultdict(lambda: [0.0, 0.0])
    vistos = set()
    with z.open('ef2024/ef2024.csv') as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding='latin-1', newline='')):
            if r['FOLIO'] not in fol or r['FOLIO'] in vistos or r['TRIMESTRE'] != '5':
                continue
            vistos.add(r['FOLIO'])
            try:
                cve = '%02d%03d' % (int(r['ID_ENTIDAD_FEDERATIVA']), int(r['ID_MUNICIPIO_RESPONSABLE']))
            except ValueError:
                continue
            if cve.endswith('000'):
                continue
            for j, m in fol[r['FOLIO']]:
                out[cve][j] += m
    return out


# --- 4. INAFED: quién gobernó ------------------------------------------------
MINUS = {'de', 'del', 'la', 'las', 'los', 'y', 'e'}


def titulo(x):
    x = re.sub(r'\s+', ' ', x or '').strip()
    return ' '.join(p.lower() if (i and p.lower() in MINUS) else p[:1].upper() + p[1:].lower()
                    for i, p in enumerate(x.split(' '))).replace(' De ', ' de ') if x else ''


def arregla(x):
    x = (x or '').replace('Ãš', 'Ú').replace('\x81', '').replace('Ã‘', 'Ñ')
    return re.sub(r'\s+', ' ', x).strip().strip('.').strip()


def partido(r):
    p, integ, desc = arregla(r['partido']), arregla(r['integrantes']), arregla(r['descripcion'])
    if p in ('', '-', '--'):
        return None
    if p == 'UYC':
        return 'Usos y costumbres'
    if p.startswith('C.I'):
        return 'Candidatura independiente'
    if p.startswith('C.C'):
        return 'Candidatura común ' + integ if integ else 'Candidatura común'
    if p.startswith('COAL') or p in ('ALIANZA', 'JHHEBCS') or (integ and '-' in integ):
        miembros = integ or (desc if '-' in desc else '')
        return 'Coalición ' + miembros if miembros else 'Coalición (' + titulo(desc) + ')'
    return 'MC' if p == 'PMC' else p


def inafed(ruta):
    texto = huella(ruta, SHA_INAFED).decode('utf-8')
    out = {}
    for r in csv.DictReader(io.StringIO(texto)):
        cve = str(r['cve_inegi']).zfill(5)
        nombre = titulo(' '.join(arregla(r[k]) for k in ('nombre', 'ap_paterno', 'ap_materno')))
        if nombre.replace('-', '').strip() == '':
            nombre = None
        out[cve] = [nombre, partido(r), r['fecha_pdo_gob_ini'] or None, r['fecha_pdo_gob_fin'] or None,
                    r['sexo'] if r['sexo'] in ('H', 'M') else None]
    # La misma persona registrada en dos municipios: no se afirma ninguno de
    # los dos; se anota la otra clave para que el motor lo diga.
    vistos = collections.defaultdict(list)
    for cve, v in out.items():
        if v[0]:
            vistos[norm(v[0])].append(cve)
    for claves in vistos.values():
        if len(claves) > 1:
            for c in claves:
                out[c].append([x for x in claves if x != c])
    return out


# --- 5. ASF: auditorías integrales a municipios ------------------------------
# Nombres que la Matriz escribe distinto que el catálogo del INEGI. San Pedro
# Mixtepec hay dos en Oaxaca; el del distrito de Juquila es la clave 318, según
# el domicilio que el propio INAFED registra para cada uno.
ASF_ALIAS = {
    'Magdalena Contreras': 'La Magdalena Contreras',
    'Ahualulco del Sonido 13': 'Ahualulco',
    'Cintalapa de Figueroa': 'Cintalapa',
    'Cosamaloapan': 'Cosamaloapan de Carpio',
    'Ozuluama': 'Ozuluama de Mascareñas',
}
ASF_CLAVE = {'Municipio de San Pedro Mixtepec, Distrito de Juquila, Oaxaca': '20318'}


def asf(padron):
    d = json.loads(MATRIZ.read_text(encoding='utf-8'))['auditorias_integrales_municipales']
    ents = {norm(e['n']): cve for cve, e in padron.items()}
    ents[norm('Estado de México')] = '15'
    idx, repetidos = {}, set()
    for cve2, e in padron.items():
        for c, nom in e['lista']:
            if (cve2, norm(nom)) in idx:
                repetidos.add((cve2, norm(nom)))
            idx[(cve2, norm(nom))] = cve2 + c
    for k in repetidos:
        del idx[k]
    out, sin = {}, []
    for a in d:
        inst, est = a['institucion'].rsplit(', ', 1)
        nom = re.sub(r'^(Municipio de |Municipio |Alcaldía )', '', inst)
        nom = ASF_ALIAS.get(nom, nom)
        e = ents.get(norm(est))
        cve = ASF_CLAVE.get(a['institucion']) or (idx.get((e, norm(nom))) if e else None)
        if not cve:
            sin.append(a['institucion'])
            continue
        out[cve] = [a['auditoria_numero'], a['entrega'], a['acciones_total'], a['resultados_con_observaciones'],
                    round(float(a['por_aclarar_miles']) / 1000, 1), round(float(a['recuperaciones_miles']) / 1000, 1)]
    return out, sin


def padron_inegi():
    """Claves y nombres del catálogo, desde municipios-efipem.js."""
    t = (RAIZ / 'assets' / 'auditor' / 'js' / 'municipios-efipem.js').read_text(encoding='utf-8')
    out = {}
    for m in re.finditer(r'"([A-ZÉ]+)": \{ cve: "(\d\d)", n: \d+, conCifra: \d+,[\s\S]*?lista: \[([\s\S]*?)\] \}', t):
        lista = re.findall(r'\["(\d{3})","([^"]+)"', m.group(3))
        out[m.group(2)] = {'abbr': m.group(1), 'lista': lista}
    return out


def main():
    if len(sys.argv) != 6:
        sys.exit(__doc__)
    est = estados(sys.argv[1])
    hist = historial(sys.argv[2])
    sr, sr_nom = srft(sys.argv[3])
    gob = inafed(sys.argv[4])
    dst = destino(sys.argv[5])
    pad = padron_inegi()
    # Nombres de entidad (los del INAFED) para cruzar la Matriz de la ASF
    ent_nom = {}
    texto_inafed = huella(sys.argv[4], SHA_INAFED).decode('utf-8')
    for r in csv.DictReader(io.StringIO(texto_inafed)):
        ent_nom[str(r['cve_inegi']).zfill(5)[:2]] = r['estado']
    ent_nom['09'] = 'Ciudad de México'
    for cve2 in pad:
        pad[cve2]['n'] = ent_nom.get(cve2, '')
    au, sin_asf = asf(pad)

    mun = {}
    malos_srft = []
    for cve2, e in sorted(pad.items()):
        for c, nom in e['lista']:
            k = cve2 + c
            h = ''.join('1' if a in hist.get(k, {}) else '0' for a in ANIOS)
            x = {'h': h}
            if k in gob:
                x['g'] = gob[k]
            if k in sr:
                x['s'] = [round(v) for v in sr[k]]
                if norm(sr_nom[k])[:6] != norm(nom)[:6]:
                    malos_srft.append((k, nom, sr_nom[k]))
            if k in dst and (dst[k][0] or dst[k][1]):
                x['p'] = [round(v) for v in dst[k]]
            if k in au:
                x['a'] = au[k]
            if 2024 not in hist.get(k, {}):
                prev = [a for a in ANIOS if a < 2024 and a in hist.get(k, {})]
                if prev:
                    u = prev[-1]
                    x['u'] = [u] + hist[k][u]
            mun[k] = x

    cab = ('/* ===================================================================\r\n'
           '   AUDITAVISION - Rendicion de cuentas municipio por municipio\r\n'
           '   -------------------------------------------------------------------\r\n'
           '   Generado por herramientas/integrar_rendicion.py. No se edita a mano.\r\n'
           '   Por clave INEGI de cinco digitos:\r\n'
           '     h  anios 2016-2025 en que el municipio entrego su cuenta al INEGI\r\n'
           '        (1 = entrego); 2025 es preliminar.\r\n'
           '     u  si no entrego la de 2024: [ultimo anio entregado, ingresos,\r\n'
           '        participaciones, aportaciones], en pesos (INEGI).\r\n'
           '     s  SRFT 2024 (SHCP): [recibido FAIS, recibido FORTAMUN,\r\n'
           '        pagado FAIS, pagado FORTAMUN], en pesos, segun el municipio.\r\n'
           '     p  SRFT 2024, destino del gasto: [FAIS, FORTAMUN] modificado de\r\n'
           '        las obras y acciones que registro, en pesos.\r\n'
           '     g  INAFED: [nombre, partido, inicio, fin, sexo, (otras claves con\r\n'
           '        la misma persona, si el INAFED la repite)].\r\n'
           '     a  ASF CP 2024, auditoria integral: [numero, entrega, acciones,\r\n'
           '        resultados con observacion, por aclarar mdp, recuperado mdp].\r\n'
           '   =================================================================== */\r\n')
    meta = {
        'anios': ANIOS, 'preliminar': 2025,
        'fuentes': {
            'inegi': {'ref': 'ref-inegi-efipem', 'corto': 'INEGI, EFIPEM municipal 2016-2025', 'url': URL_EFM, 'sha256': SHA_EFM},
            'srft': {'ref': 'ref-shcp-srft-2024', 'corto': 'SHCP, SRFT, informe definitivo 2024', 'url': URL_SRFT, 'sha256': SHA_SRFT,
                     'destino': URL_DESTINO, 'sha256Destino': SHA_DESTINO},
            'inafed': {'ref': 'ref-inafed-presidencias', 'corto': 'INAFED, presidencias municipales', 'url': URL_INAFED, 'sha256': SHA_INAFED},
            'asf': {'ref': 'ref-asf-mdb2024', 'corto': 'ASF, Matriz de Datos Básicos CP 2024'},
        },
    }
    lineas = ['window.AUDIT_MUN_RENDICION = {']
    for k, v in meta.items():
        lineas.append('  %s: %s,' % (k, json.dumps(v, ensure_ascii=False)))
    lineas.append('  mun: {')
    ks = sorted(mun)
    for i, k in enumerate(ks):
        lineas.append('    "%s":%s%s' % (k, json.dumps(mun[k], ensure_ascii=False, separators=(',', ':')), ',' if i < len(ks) - 1 else ''))
    lineas.append('  }')
    lineas.append('};')
    SALIDA.write_bytes((cab + '\r\n'.join(lineas) + '\r\n').encode('utf-8'))

    # Bloque estatal y referencias en la base
    bloque = {
        'nota': 'Participaciones y aportaciones de 2024 en millones de pesos: lo que cada gobierno estatal reportó al INEGI como recibido, contra lo que la Cuenta Pública 2024 registra como pagado por la Federación a esa entidad. Las aportaciones del INEGI se toman sin los convenios (recursos reasignados), que en la Cuenta Pública no son Ramo 33.',
        'fuentes': {
            'cp2024': {'ref': 'ref-shcp-cp2024-datos', 'corto': 'SHCP, Cuenta Pública 2024, datos abiertos', 'url': URL_CP, 'sha256': SHA_CP},
            'inegi2024': {'ref': 'ref-inegi-efipem-estatal', 'corto': 'INEGI, finanzas públicas estatales 2024'},
        },
        'entidades': est,
    }
    b = BASE.read_bytes().decode('utf-8')
    texto = '  "inspector_estatal": ' + json.dumps(bloque, ensure_ascii=False, indent=1).replace('\n', '\r\n  ') + ','
    if '"inspector_estatal":' in b:
        a = b.index('  "inspector_estatal": ')
        z = b.index('\r\n  "', a + 10)
        b = b[:a] + texto + b[z:]
    else:
        a = b.index('\r\n  "estados": [')
        b = b[:a] + '\r\n' + texto + b[a:]
    fichas = 0
    for ref in reversed(REF_NUEVAS):
        marca = '"id": "%s"' % ref['id']
        if marca in b:
            i = b.index(marca)
            ini = b.rindex('\r\n    {\r\n', 0, i) + 2
            fin = b.index('\r\n    }', i) + len('\r\n    }')
            b = b[:ini] + _cuerpo(ref) + b[fin:]
            continue
        if True:
            ancla = b.index('"id": "ref-shcp-avance-2t2026"')
            corte = b.index('\r\n    }', ancla) + len('\r\n    }')
            b = b[:corte] + ',\r\n' + _cuerpo(ref) + b[corte:]
            fichas += 1
    BASE.write_bytes(b.encode('utf-8'))

    tot = len(mun)
    no24 = [k for k in mun if mun[k]['h'][8] == '0' and not k.startswith('09')]
    print('municipios: %d; sin cuenta 2024 al INEGI (sin CDMX): %d; con SRFT: %d; con INAFED: %d; con ASF: %d'
          % (tot, len(no24), sum('s' in v for v in mun.values()), sum('g' in v for v in mun.values()),
             sum('a' in v for v in mun.values())))
    print('ASF sin cruzar: %d %s' % (len(sin_asf), sin_asf[:8]))
    print('SRFT con nombre distinto: %d %s' % (len(malos_srft), malos_srft[:8]))
    print('fichas nuevas: %d' % fichas)


if __name__ == '__main__':
    main()
