#!/usr/bin/env python3
"""Las listas de riesgo del padrón de contrapartes (18-11-2026).

Pedido del autor: «que nuestra base de datos quede muy bien integrada… para
llevar a cabo todo este compliance de prevención de lavado de dinero… verificar
a los clientes de nuestros clientes… que no estén en estas listas». Entrega 2
del plan: las listas públicas que faltaban, con su huella y su cuadre.

Del SAT (datos abiertos, «Contribuyentes publicados»):
  - artículo 69 del Código Fiscal: no localizados, créditos firmes, créditos
    exigibles, créditos cancelados y sentencias condenatorias por delito fiscal;
  - artículo 17-H Bis: certificados de sello digital (CSD) sin efectos;
  - artículo 69-B Bis: transmisión indebida de pérdidas fiscales.
De fuera:
  - la lista SDN de la OFAC (Departamento del Tesoro de EE. UU.), con sus
    alias, domicilios y los RFC que trae en sus observaciones;
  - la lista consolidada del Consejo de Seguridad de la ONU (en español).

No entran (no son señal de riesgo): las condonaciones, las reducciones de
multas del art. 74 ni los entes públicos omisos.

Uso:
    python3 herramientas/anclar_listas.py            # descarga todo
    python3 herramientas/anclar_listas.py <carpeta>  # usa los archivos ya bajados

Escribe:
  - docs/listas/listas.json: de dónde sale cada lista, su huella SHA-256, su
    corte y sus cuentas;
  - assets/auditor/data/padron/meta.js: lo mismo, para el navegador;
  - assets/auditor/data/padron/s-XX.js: las listas del SAT por RFC, en 256
    partes (las dos primeras letras de la huella del RFC). **Las personas físicas no se publican** (decisión del autor,
    18-11-2026): ni su nombre ni su RFC en claro. Cada RFC se guarda con su
    huella SHA-256 (sal «av-padron:», 12 caracteres); el navegador saca la
    huella del RFC que el lector escribe y solo dice si coincide. De las
    personas morales sí va su razón social, como la publica el SAT;
  - assets/auditor/data/sanciones-int.js: la OFAC y la ONU, para buscar por
    nombre o por RFC. Son personas y entidades que un gobierno hizo públicas
    en un documento oficial (AGENTS.md §2 bis).

Se detiene si:
  - una lista del SAT cambia sus columnas;
  - más de 1 de cada 10,000 renglones trae un RFC que no tiene forma de RFC;
  - el tipo de persona que dice el SAT no es el que da el largo del RFC;
  - un alias o un domicilio de la OFAC no es de alguien de su lista;
  - la ONU no trae número de referencia en un registro.
"""
import collections
import csv
import datetime
import hashlib
import io
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(RAIZ, 'docs', 'listas', 'listas.json')
DIR_P = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'padron')
SANC = os.path.join(RAIZ, 'assets', 'auditor', 'data', 'sanciones-int.js')
SAL = 'av-padron:'
BLOB = 'https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/'
PAG_SAT = 'https://www.sat.gob.mx/minisitio/DatosAbiertos/contribuyentes_publicados.html'
RFC_RE = re.compile(r'^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$')
# Los RFC genéricos (público en general y residentes en el extranjero) no son de
# nadie: aparecen en las listas por errores de captura y no se guardan.
GENERICOS = {'XAXX010101000', 'XEXX010101000'}

# clave: (archivo, ruta en el almacenamiento del SAT, nombre, fundamento, qué quiere decir, columnas)
C6 = ['RFC', 'RAZON SOCIAL', 'TIPO PERSONA', 'SUPUESTO', 'FECHA DE PRIMERA PUBLICACION', 'ENTIDAD FEDERATIVA']
SAT = collections.OrderedDict([
    ('nl', ('No_localizados.csv', 'Documents_AGR/No_localizados.csv', 'No localizado', 'CFF, art. 69, párrafo 12, fr. IV',
            'El SAT no lo encontró en el domicilio fiscal que dio.', C6)),
    ('fi', ('Firmes.csv', 'Documents_AGR/Firmes.csv', 'Crédito fiscal firme', 'CFF, art. 69, párrafo 12, fr. I',
            'Tiene un adeudo con el SAT que ya no se puede impugnar y no lo ha pagado ni garantizado.', C6)),
    ('ex', ('Exigibles.csv', 'Documents_AGR/Exigibles.csv', 'Crédito fiscal exigible', 'CFF, art. 69, párrafo 12, fr. II',
            'Tiene un adeudo exigible con el SAT que no ha pagado ni garantizado.', C6)),
    ('ca', ('Cancelados.csv', 'Documents_AGR/Cancelados.csv', 'Crédito fiscal cancelado', 'CFF, art. 69, párrafo 12, fr. III, y art. 146-A',
            'El SAT canceló el cobro de un adeudo suyo, por incosteable o porque no tenía con qué pagar. Cancelar el cobro no es perdonar la deuda.',
            ['RFC', 'RAZON SOCIAL', 'TIPO PERSONA', 'SUPUESTO', 'FECHA DE CANCELACION', 'MONTO', 'FECHA DE PUBLICACION', 'ENTIDAD FEDERATIVA'])),
    ('se', ('Sentencias.csv', 'Documents_AGR/Sentencias.csv', 'Sentencia por delito fiscal', 'CFF, art. 69, párrafo 12, fr. V',
            'Un juez lo condenó por un delito fiscal con sentencia firme.',
            ['RFC', 'RAZÓN SOCIAL', 'TIPO PERSONA', 'SUPUESTO', 'FECHAS DE PRIMERA PUBLICACION', 'ENTIDAD FEDERATIVA'])),
    ('csd', ('CSDsinefectos.csv', 'Documents_AGR/CSDsinefectos.csv', 'Sello digital sin efectos', 'CFF, art. 17-H Bis',
             'El SAT le dejó sin efectos el certificado con el que sella sus facturas: mientras no lo resuelva, no puede facturar.',
             ['RFC', 'NOMBRE O RAZON SOCIAL', 'SUPUESTO DE CANCELACION CSD', 'FECHA DE CANCELACION CSD',
              'ADMINISTRACION GENERAL RESPONSABLE DE LA CANCELACION', 'FECHA DE PUBLICACION'])),
    ('bb', ('Listado_69_B_Bis_Completo.csv', 'Documents_AGGC/Listado_69_B_Bis_Completo.csv', 'Transmisión indebida de pérdidas fiscales',
            'CFF, art. 69-B Bis', 'El SAT determinó que transmitió pérdidas fiscales de forma indebida (por ejemplo, en una fusión o escisión sin razón de negocios).',
            None)),
])
# Fecha que se guarda de cada lista: la de publicación.
FECHA = {'nl': 'FECHA DE PRIMERA PUBLICACION', 'fi': 'FECHA DE PRIMERA PUBLICACION', 'ex': 'FECHA DE PRIMERA PUBLICACION',
         'ca': 'FECHA DE PUBLICACION', 'se': 'FECHAS DE PRIMERA PUBLICACION', 'csd': 'FECHA DE PUBLICACION'}
CANCELADO = {'CANCELADOS POR INSOLVENCIA': 'I', 'CANCELADOS POR INCOSTEABILIDAD': 'C', 'CANCELADOS': ''}
SITUACION_BB = {'Definitivo': 'F', 'Sentencia Favorable': 'S'}

OFAC = {'sdn': 'https://www.treasury.gov/ofac/downloads/sdn.csv', 'alt': 'https://www.treasury.gov/ofac/downloads/alt.csv',
        'add': 'https://www.treasury.gov/ofac/downloads/add.csv'}
OFAC_PAG = 'https://sanctionslist.ofac.treas.gov/Home/SdnList'
ONU = 'https://scsanctions.un.org/resources/xml/sp/consolidated.xml'
ONU_PAG = 'https://www.un.org/securitycouncil/es/content/un-sc-consolidated-list'


def alto(m):
    raise SystemExit('anclar_listas: ' + m)


def bajar(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Auditavision)'})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def leer(carpeta, archivo, url):
    if carpeta:
        return open(os.path.join(carpeta, archivo), 'rb').read()
    return bajar(url)


def huella(b):
    return hashlib.sha256(b).hexdigest()


def clave(rfc):
    return hashlib.sha256((SAL + rfc).encode('utf-8')).hexdigest()[:12]


def fecha(s):
    s = (s or '').strip()
    m = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', s)
    return m.group(3) + m.group(2) + m.group(1) if m else ''


def texto(b):
    for enc in ('utf-8', 'latin-1'):
        try:
            return b.decode(enc).lstrip('﻿')
        except UnicodeDecodeError:
            pass


def sat(carpeta):
    """{rfc: {'n': razón social (solo morales), lista: valor}} y la ficha de cada lista."""
    regs = collections.defaultdict(dict)
    fichas = collections.OrderedDict()
    for k, (arch, ruta, nom, fund, que, cols) in SAT.items():
        url = BLOB + ruta
        b = leer(carpeta, arch, url)
        t = texto(b)
        filas = list(csv.reader(io.StringIO(t)))
        corte = ''
        if k == 'bb':
            m = re.search(r'actualizada al (\d{1,2} de \w+ de \d{4})', filas[0][0])
            corte = m.group(1) if m else ''
            h = [x.strip() for x in filas[2]]
            if h[:4] != ['No.', 'RFC', 'Nombre del Contribuyente', 'Situación del contribuyente']:
                alto('el 69-B Bis cambió sus columnas: %s' % h[:4])
            datos = [r for r in filas[3:] if r and r[0].strip()]
            ir, iname, isit = 1, 2, 3
        else:
            h = [x.strip() for x in filas[0]]
            if h != cols:
                alto('la lista %s cambió sus columnas: %s' % (arch, h))
            datos = [r for r in filas[1:] if r and r[0].strip()]
            ir, iname = 0, 1
        malos, genericos, vistos = 0, 0, set()
        mor = fis = 0
        for r in datos:
            rfc = r[ir].strip().upper()
            if not RFC_RE.match(rfc):
                malos += 1
                continue
            if rfc in GENERICOS:
                genericos += 1
                continue
            moral = len(rfc) == 12
            if 'TIPO PERSONA' in h and r[h.index('TIPO PERSONA')].strip() != ('M' if moral else 'F'):
                alto('%s: el SAT dice que %s es persona %s' % (arch, '*' * len(rfc), r[h.index('TIPO PERSONA')]))
            if k == 'bb':
                s = SITUACION_BB.get(r[isit].strip())
                if s is None:
                    alto('69-B Bis: situación desconocida %r' % r[isit])
                fechas = [fecha(x) for x in r[5:] if fecha(x)]
                v = s + (fechas[-1] if fechas else '')
            else:
                v = fecha(r[h.index(FECHA[k])])
                if k == 'ca':
                    sup = r[h.index('SUPUESTO')].strip()
                    if sup not in CANCELADO:
                        alto('cancelados: supuesto desconocido %r' % sup)
                    v += CANCELADO[sup]
            reg = regs[rfc]
            if moral and 'n' not in reg:
                reg['n'] = re.sub(r'\s+', ' ', r[iname]).strip()
            # Un RFC puede venir más de una vez en la misma lista (varios
            # créditos o varias sentencias): se guarda la publicación más vieja.
            if k not in reg or v < reg[k]:
                reg[k] = v
            if rfc not in vistos:
                vistos.add(rfc)
                mor += moral
                fis += not moral
        if malos * 10000 > len(datos):
            alto('%s: %d de %d renglones no traen un RFC válido' % (arch, malos, len(datos)))
        fichas[k] = {'n': nom, 'fund': fund, 'que': que, 'fuente': 'SAT, datos abiertos, Contribuyentes publicados: ' + nom.lower(),
                     'url': url, 'pagina': PAG_SAT, 'sha256': huella(b), 'archivo': arch, 'corte': corte,
                     'descarga': datetime.date.today().isoformat(),
                     'renglones': len(datos), 'rechazados': malos, 'genericos': genericos, 'rfc': len(vistos), 'morales': mor, 'fisicas': fis}
    return regs, fichas


def ofac(carpeta):
    b = {k: leer(carpeta, k + '.csv', u) for k, u in OFAC.items()}
    sdn = {}
    for r in csv.reader(io.StringIO(texto(b['sdn']))):
        if not r or not r[0].strip().isdigit():
            continue
        r = [x.strip() for x in r]
        x = lambda v: '' if v == '-0-' else v
        sdn[r[0]] = {'n': x(r[1]), 't': 'i' if x(r[2]).lower() == 'individual' else ('v' if x(r[2]).lower() in ('vessel', 'aircraft') else 'e'),
                     'p': x(r[3]), 'obs': x(r[11]) if len(r) > 11 else '', 'al': [], 'pa': []}
    for r in csv.reader(io.StringIO(texto(b['alt']))):
        if not r or not r[0].strip().isdigit():
            continue
        if r[0].strip() not in sdn:
            alto('la OFAC trae un alias de alguien que no está en su lista (%s)' % r[0])
        a = r[3].strip()
        if a and a != '-0-':
            sdn[r[0].strip()]['al'].append(a)
    for r in csv.reader(io.StringIO(texto(b['add']))):
        if not r or not r[0].strip().isdigit():
            continue
        if r[0].strip() not in sdn:
            alto('la OFAC trae un domicilio de alguien que no está en su lista (%s)' % r[0])
        p = r[4].strip()
        if p and p != '-0-' and p not in sdn[r[0].strip()]['pa']:
            sdn[r[0].strip()]['pa'].append(p)
    reg = []
    for i, x in sorted(sdn.items(), key=lambda kv: int(kv[0])):
        rfcs = sorted(set(re.findall(r'R\.F\.C\. ([A-Z0-9&Ñ]{9,13})', x['obs'])))
        if x['t'] == 'v':
            continue
        reg.append(['ofac', i, x['t'], x['n'], x['al'], ', '.join(p.strip('[] ') for p in x['p'].split('] [')), x['pa'], rfcs])
    ficha = {'n': 'Lista SDN de la OFAC', 'fund': 'Departamento del Tesoro de los Estados Unidos, Oficina de Control de Activos Extranjeros',
             'que': 'Personas y entidades con las que nadie en EE. UU. puede hacer negocios: narcotráfico, terrorismo, lavado y otros programas de sanciones.',
             'fuente': 'OFAC, Specially Designated Nationals and Blocked Persons List (sdn.csv, alt.csv y add.csv)', 'url': OFAC['sdn'], 'pagina': OFAC_PAG,
             'sha256': huella(b['sdn']), 'sha256_alt': huella(b['alt']), 'sha256_add': huella(b['add']), 'archivo': 'sdn.csv',
             'corte': datetime.date.today().isoformat(), 'registros': len(reg),
             'mexico': sum(1 for r in reg if 'Mexico' in r[6]), 'conRfc': sum(1 for r in reg if r[7])}
    return reg, ficha


def onu(carpeta):
    b = leer(carpeta, 'onu.xml', ONU)
    raiz = ET.fromstring(b)
    reg = []
    for tipo, tag, alias in (('i', 'INDIVIDUAL', 'INDIVIDUAL_ALIAS'), ('e', 'ENTITY', 'ENTITY_ALIAS')):
        for x in raiz.iter(tag):
            ref = (x.findtext('REFERENCE_NUMBER') or '').strip()
            if not ref:
                alto('la ONU trae un registro sin número de referencia')
            nom = ' '.join((x.findtext(k) or '').strip() for k in ('FIRST_NAME', 'SECOND_NAME', 'THIRD_NAME', 'FOURTH_NAME')).split()
            al = [(a.findtext('ALIAS_NAME') or '').strip() for a in x.iter(alias)]
            pa = sorted({(a.findtext('COUNTRY') or '').strip() for a in x.iter(tag + '_ADDRESS')} - {''})
            nac = [(v.text or '').strip() for n in x.iter('NATIONALITY') for v in n.iter('VALUE')]
            reg.append(['onu', ref, tipo, ' '.join(nom), [a for a in al if a], (x.findtext('UN_LIST_TYPE') or '').strip(),
                        sorted(set(pa + [n for n in nac if n])), []])
    reg.sort(key=lambda r: r[1])
    ficha = {'n': 'Lista consolidada del Consejo de Seguridad de la ONU', 'fund': 'Consejo de Seguridad de las Naciones Unidas (resoluciones de sus comités de sanciones)',
             'que': 'Personas y entidades sujetas a sanciones del Consejo de Seguridad: terrorismo y su financiamiento, proliferación de armas y otros regímenes.',
             'fuente': 'ONU, Lista consolidada del Consejo de Seguridad (XML en español)', 'url': ONU, 'pagina': ONU_PAG,
             'sha256': huella(b), 'archivo': 'consolidated.xml', 'corte': (raiz.get('dateGenerated') or '')[:10], 'registros': len(reg),
             'personas': sum(1 for r in reg if r[2] == 'i'), 'entidades': sum(1 for r in reg if r[2] == 'e')}
    return reg, ficha


def escribe(ruta, t):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8', newline='\n') as f:
        f.write(t)


def main():
    carpeta = sys.argv[1] if len(sys.argv) > 1 else None
    regs, fichas = sat(carpeta)
    ro, fo = ofac(carpeta)
    ru, fu = onu(carpeta)
    partes = collections.defaultdict(dict)
    mor = fis = 0
    for rfc in sorted(regs):
        r = regs[rfc]
        # Una sola cadena por RFC: «razón social|fi140101|ca190528I» (empresas)
        # o «fi140101|nl140101» (personas físicas, sin nombre). Las fechas van
        # como AAMMDD; la 69-B Bis lleva su situación delante (F o S).
        for k in SAT:
            if k in r and r[k] and not r[k].lstrip('FS')[:2] == '20':
                alto('una fecha de %s no es de este siglo: %s' % (k, r[k]))
        v = '|'.join(([r['n'].replace('|', '/')] if 'n' in r else []) +
                     [k + (r[k][0] + r[k][3:] if k == 'bb' and r[k] else r[k][2:]) for k in SAT if k in r])
        c = clave(rfc)
        if c in partes[c[:2]]:
            alto('dos RFC dan la misma huella (%s): hay que alargarla' % c)
        partes[c[:2]][c] = v
        mor += len(rfc) == 12
        fis += len(rfc) == 13
    if len(partes) != 256:
        alto('el padrón no llenó sus 256 partes (%d)' % len(partes))
    for p, d in partes.items():
        escribe(os.path.join(DIR_P, 's-%s.js' % p), '/* Generado por herramientas/anclar_listas.py. No editar a mano. */\n'
                '(window.PADRON_S = window.PADRON_S || {})[%s] = %s;\n' % (json.dumps(p), json.dumps(dict(sorted(d.items())), ensure_ascii=False, separators=(',', ':'))))
    # La OFAC no fecha su archivo: su corte es el día en que se bajó por primera
    # vez esa versión. Si la huella no cambió, se queda el corte anterior.
    if os.path.exists(DOCS):
        ant = json.load(open(DOCS, encoding='utf-8'))
        for k, f in (('ofac', fo), ('onu', fu)):
            if ant.get(k, {}).get('sha256') == f['sha256'] and k == 'ofac':
                f['corte'] = ant[k]['corte']
        for k, f in fichas.items():
            if ant.get('sat', {}).get(k, {}).get('sha256') == f['sha256']:
                f['descarga'] = ant['sat'][k].get('descarga', f['descarga'])
    meta = {'sal': SAL, 'rfc': len(regs), 'morales': mor, 'fisicas': fis, 'orden': list(SAT), 'sat': fichas, 'ofac': fo, 'onu': fu}
    escribe(DOCS, json.dumps(meta, ensure_ascii=False, indent=1) + '\n')
    escribe(os.path.join(DIR_P, 'meta.js'), '/* Generado por herramientas/anclar_listas.py. No editar a mano. */\n'
            'window.PADRON_META = %s;\n' % json.dumps(meta, ensure_ascii=False, separators=(',', ':')))
    escribe(SANC, '/* Generado por herramientas/anclar_listas.py. No editar a mano. */\n'
            'window.SANC_INT = %s;\n' % json.dumps({'r': ro + ru}, ensure_ascii=False, separators=(',', ':')))
    print('anclar_listas: %s RFC del SAT (%s empresas, %s personas físicas), %s de la OFAC (%s con domicilio en México), %s de la ONU.' % (
        format(len(regs), ','), format(mor, ','), format(fis, ','), format(len(ro), ','), fo['mexico'], format(len(ru), ',')))
    for k, f in fichas.items():
        print('  %-4s %-42s %8s RFC  %s…%s' % (k, f['n'], format(f['rfc'], ','), f['sha256'][:12], '  (%d rechazados)' % f['rechazados'] if f['rechazados'] else ''))


if __name__ == '__main__':
    main()
