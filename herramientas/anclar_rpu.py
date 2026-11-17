#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A quién le deben los estados, los municipios y sus organismos: el Registro
Público Único (RPU) de Financiamientos y Obligaciones de la SHCP, crédito por
crédito, en assets/auditor/data/deuda-rpu.js (window.AUDIT_RPU).

Pedido del autor (17-11-2026): «prosigue con estos pendientes y las deudas».
El Sistema de Alertas dice CUÁNTO debe cada gobierno y cuánto le pesa; el RPU
dice A QUIÉN, a qué tasa, hasta cuándo, con qué lo paga y para qué lo pidió.

Fuente: https://www.disciplinafinanciera.hacienda.gob.mx/work/models/
DISCIPLINA_FINANCIERA/Documentos/RegistroDiario/registro_deuda.xlsx
(Hacienda lo actualiza a diario; el saldo de cada crédito es el que los
gobiernos reportan cada trimestre: el corte va en el encabezado de la hoja.)
El servidor manda una cadena de certificados incompleta: curl necesita el
intermedio YR1 de Let's Encrypt en su paquete de confianza (--cacert), nunca
desactivar la verificación.

Reglas (AGENTS.md §2):
- Cada crédito es «oficial» (como lo inscribió Hacienda); las sumas, los
  órdenes y los conteos son «derivado».
- El archivo no trae un total: no hay cuadre externo. Se detiene si una fila
  trae una entidad que no es de las 32, un monto que no es número, o un
  municipio que no está en el padrón; si el encabezado no dice el corte, o si
  el saldo dice algo distinto de un número o del guion de Hacienda.
- Un saldo «-» es como lo publica Hacienda: el crédito sigue inscrito y no
  reporta saldo (se dice así, no se convierte en cero).
- Todos los acreedores del archivo son instituciones o empresas: si un día
  aparece una persona física (sin S.A., S.N.C., S. de R.L. ni similares), se
  detiene: a los particulares no se les nombra (§2 bis).

Uso:
    python3 herramientas/anclar_rpu.py registro_deuda.xlsx
"""
import collections
import datetime
import hashlib
import json
import pathlib
import re
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'herramientas'))
SALIDA = RAIZ / 'assets' / 'auditor' / 'data' / 'deuda-rpu.js'
URL = ('https://www.disciplinafinanciera.hacienda.gob.mx/work/models/DISCIPLINA_FINANCIERA/'
       'Documentos/RegistroDiario/registro_deuda.xlsx')
PAGINA = 'https://www.disciplinafinanciera.hacienda.gob.mx/es/DISCIPLINA_FINANCIERA/Registro_Publico_Unico'
FUENTE = 'SHCP, Registro Público Único de Financiamientos y Obligaciones de Entidades Federativas y Municipios'

# Cómo se le dice a cada acreedor (el nombre legal se guarda completo).
# BBVA Bancomer es el nombre que BBVA México tuvo hasta 2019; Interacciones e
# IXE se fusionaron con Banorte, pero el registro conserva el nombre con que se
# firmó el crédito: se dice así, no se suman a mano.
CORTO = [
    (r'^Banco Nacional de Obras', 'Banobras'),
    (r'^Banco Mercantil del Norte.*/ BBVA', 'Banorte y BBVA (crédito sindicado)'),
    (r'^Banco Mercantil del Norte', 'Banorte'),
    (r'^BBVA Bancomer', 'BBVA Bancomer (hoy BBVA México)'),
    (r'^BBVA México', 'BBVA México'),
    (r'^Banco Santander', 'Santander'),
    (r'^Banco Nacional de México', 'Banamex'),
    (r'^Banco Invex', 'Invex'),
    (r'^HSBC', 'HSBC'),
    (r'^Banco del Bajío', 'BanBajío'),
    (r'^Bansí', 'Bansí'),
    (r'^Banco Multiva', 'Multiva'),
    (r'^Banca Mifel', 'Mifel'),
    (r'^Banco Interacciones', 'Interacciones'),
    (r'^Scotiabank', 'Scotiabank'),
    (r'^Banco Azteca', 'Banco Azteca'),
    (r'^Banca Afirme', 'Afirme'),
    (r'^CI ?Banco', 'CIBanco'),
    (r'^Deutsche Bank', 'Deutsche Bank'),
    (r'^Nacional Financiera', 'Nafin'),
    (r'^Value', 'Value Casa de Bolsa'),
    (r'^Monex', 'Monex'),
    (r'^Banco Regional', 'Banregio'),
    (r'^Banco Actinver', 'Actinver'),
    (r'^IXE Banco', 'IXE Banco'),
    (r'^Corporación Financiera de América del Norte', 'Cofiama'),
    (r'^Dexia', 'Dexia Crédito Local'),
    (r'^Financiera Local', 'Financiera Local'),
    (r'^Fondo de Operación y Financiamiento Bancario a la Vivienda', 'FOVI'),
    (r'^Fideicomiso Fondo Nacional de Habitaciones Populares', 'FONHAPO'),
]
# Municipios que el registro anota con el nombre de su cabecera, no con el del
# municipio (Playa del Carmen es la cabecera de Solidaridad, Q. Roo, 23008).
CABECERA = {('QROO', 'playa del carmen'): '23008'}
SOCIEDAD = re.compile(r'S\.\s?A\.|S\.N\.C\.|Sociedad|S\. de R\.L\.|S\.A\.P\.I|S\.A\.S\.|SOFOM|Fideicomiso|Fondo|Instituto|Banco|S\.A\b|S\. A\.', re.I)

# Los «tipos» del registro, como se le dicen al lector.
TIPO_NOTA = {
    'Emisión bursátil': 'certificados que se venden en la Bolsa; el registro anota al fiduciario o al representante común, no a quienes compraron los certificados',
    'Obligación relacionada con asociaciones público - privadas': 'el pago comprometido a la empresa que construyó u opera una obra o servicio: no es un préstamo de banco',
    'Obligación a corto plazo': 'préstamo para cubrir faltas de liquidez: debe pagarse en el mismo periodo de gobierno y, a más tardar, tres meses antes de que termine (LDF, art. 31)',
}


def _norm(s):
    s = unicodedata.normalize('NFD', str(s or ''))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def _fecha(v):
    if isinstance(v, datetime.datetime):
        return v.strftime('%Y-%m-%d')
    return None


def leer(ruta):
    import openpyxl
    import planisferio
    datos = pathlib.Path(ruta).read_bytes()
    sha = hashlib.sha256(datos).hexdigest()
    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    if 'SHCP' not in wb.sheetnames:
        sys.exit('RPU: el libro no trae la hoja SHCP')
    filas = list(wb['SHCP'].iter_rows(values_only=True))
    enc = filas[1]
    m = re.match(r'SALDO AL (\d+) DE (\w+) DE (\d{4})', str(enc[7] or '').upper())
    if not m:
        sys.exit('RPU: el encabezado del saldo no dice el corte (%r)' % (enc[7],))
    meses = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
    corte = '%s-%02d-%02d' % (m.group(3), meses.index(m.group(2)) + 1, int(m.group(1)))
    corte_txt = '%d de %s de %s' % (int(m.group(1)), m.group(2).lower(), m.group(3))

    db_txt = (RAIZ / 'assets' / 'auditor' / 'js' / 'audit-database.js').read_text(encoding='utf-8')
    db = json.loads(db_txt[db_txt.index('{', db_txt.index('window.AUDIT_DB')):].rsplit(';', 1)[0])
    ENT = {e['abbr']: e['name'] for e in db['estados']}
    edo = {_norm(e['name']): e['abbr'] for e in db['estados']}
    edo.update({'coahuila de zaragoza': 'COAH', 'michoacan de ocampo': 'MICH',
                'veracruz de ignacio de la llave': 'VER', 'mexico': 'MÉX', 'estado de mexico': 'MÉX'})
    padron = planisferio._padron()
    mun = {}
    for abbr, info in padron['ent'].items():
        mun[abbr] = {_norm(r[1]): info['cve'] + r[0] for r in info['lista']}

    inst, tipos, dest, fte = [], [], [], []
    def idx(lista, v):
        v = re.sub(r'\s+', ' ', str(v or '').strip()) or '—'
        if v not in lista:
            lista.append(v)
        return lista.index(v)

    R = []
    sin_mun = collections.Counter()
    for r in filas[3:]:
        if r[0] is None or r[2] is None:
            continue
        a = edo.get(_norm(r[0]))
        if not a:
            sys.exit('RPU: entidad desconocida %r' % (r[0],))
        deudor = re.sub(r'\s+', ' ', str(r[1]).strip())
        acre = re.sub(r'\s+', ' ', str(r[2]).strip())
        if not SOCIEDAD.search(acre):
            sys.exit('RPU: el acreedor %r no parece institución ni empresa; revisar antes de publicar (§2 bis)' % acre)
        if not isinstance(r[6], (int, float)):
            sys.exit('RPU: monto original que no es número en %r (%r)' % (deudor, r[6]))
        if isinstance(r[7], (int, float)):
            saldo = round(r[7] / 1e6, 4)
        elif str(r[7]).strip() == '-':
            saldo = None
        else:
            sys.exit('RPU: saldo raro en %r (%r)' % (deudor, r[7]))
        dn = _norm(deudor)
        cve = ''
        if dn.startswith('municipio de '):
            k = 'm'
            mn = dn[len('municipio de '):]
            cve = mun[a].get(mn, '') or CABECERA.get((a, mn), '')
            if not cve:
                cand = [v for kk, v in mun[a].items() if mn == kk or (len(mn) > 5 and (mn in kk or kk in mn))]
                if len(cand) == 1:
                    cve = cand[0]
            if not cve:
                sin_mun[(a, deudor)] += 1
        elif dn.startswith('estado de ') or dn.startswith('gobierno del estado') or (a == 'CDMX' and dn == 'ciudad de mexico'):
            k = 'e'
        else:
            k = 'o'
        tasa = r[13] if isinstance(r[13], (int, float)) else None
        R.append([a, k, deudor, cve, idx(inst, acre), idx(tipos, r[3]), _fecha(r[4]),
                  round(r[6] / 1e6, 4), saldo, round(tasa * 100, 2) if tasa is not None else None,
                  _fecha(r[12]), idx(dest, r[17]), idx(fte, r[15])])
    if sin_mun:
        sys.exit('RPU: municipios que no están en el padrón: %s' % ', '.join('%s (%s)' % (d, a) for (a, d) in sin_mun))
    if len({x[0] for x in R}) != 32:
        sys.exit('RPU: se esperaban las 32 entidades y salieron %d' % len({x[0] for x in R}))

    corto = []
    for nombre in inst:
        c = next((c for pat, c in CORTO if re.search(pat, nombre)), None)
        corto.append(c or re.split(r',', nombre)[0].strip())
    con = [x for x in R if x[8]]
    meta = {
        'fuente': FUENTE, 'url': URL, 'pagina': PAGINA, 'sha256': sha,
        'descarga': datetime.date.today().isoformat(), 'corte': corte, 'corteTxt': corte_txt,
        'n': len(R), 'conSaldo': len(con), 'saldoMdp': round(sum(x[8] for x in con), 1),
        'tipoNota': TIPO_NOTA,
        'campos': ['entidad', 'tipo de deudor (e estado, m municipio, o organismo)', 'deudor', 'clave INEGI del municipio',
                   'acreedor (índice)', 'tipo de obligación (índice)', 'fecha de contratación', 'monto original (mdp)',
                   'saldo al corte (mdp; null = Hacienda publica «-»)', 'tasa efectiva anual (%)', 'vencimiento',
                   'destino (índice)', 'fuente de pago (índice)'],
    }
    meta['ent'] = ENT
    return {'meta': meta, 'inst': [[c, n] for c, n in zip(corto, inst)], 'tipo': tipos, 'dest': dest, 'fte': fte, 'r': R}


def resumen_estado(D, a):
    """Lo del RPU de una entidad, para la página de su deuda en el Planisferio."""
    L = [x for x in D['r'] if x[0] == a]
    con = [x for x in L if x[8]]
    por = collections.defaultdict(float)
    for x in con:
        por[x[4]] += x[8]
    k = collections.defaultdict(float)
    for x in con:
        k[x[1]] += x[8]
    acre = sorted(por.items(), key=lambda kv: (-kv[1], kv[0]))
    return {'n': len(L), 'con': len(con), 'saldo': sum(x[8] for x in con), 'k': dict(k),
            'acre': [(D['inst'][i][0], v) for i, v in acre],
            'cp': sum(1 for x in con if D['tipo'][x[5]] == 'Obligación a corto plazo'),
            'app': sum(x[8] for x in con if D['tipo'][x[5]].startswith('Obligación relacionada con asociaciones')),
            'bur': sum(x[8] for x in con if D['tipo'][x[5]] == 'Emisión bursátil')}


def cargar():
    if not SALIDA.exists():
        return None
    t = SALIDA.read_text(encoding='utf-8')
    return json.loads(t[t.index('{'):].rsplit(';', 1)[0])


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    D = leer(sys.argv[1])
    cab = ('/* Registro Público Único de Financiamientos y Obligaciones (SHCP), crédito por crédito.\n'
           '   Lo escribe herramientas/anclar_rpu.py; no se edita a mano.\n'
           '   Saldo al %s; archivo descargado el %s, huella SHA-256 %s.\n'
           '   Cada crédito es «oficial»; las sumas y los órdenes, «derivado». */\n') % (
        D['meta']['corteTxt'], D['meta']['descarga'], D['meta']['sha256'])
    SALIDA.write_text(cab + 'window.AUDIT_RPU = ' + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + ';\n',
                      encoding='utf-8', newline='\n')
    m = D['meta']
    print('RPU: %d créditos (%d con saldo), $%s mdp al %s, %d acreedores; %s' % (
        m['n'], m['conSaldo'], format(m['saldoMdp'], ',.1f'), m['corteTxt'], len(D['inst']), SALIDA.relative_to(RAIZ)))


if __name__ == '__main__':
    main()
