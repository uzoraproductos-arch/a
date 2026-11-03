"""Ancla la inversión pública de las entidades a la estadística de finanzas
públicas estatales del INEGI (03-11-2026, dimensión «Inversión» del
Planisferio).

Fuente: la misma de los ingresos (anclar_ingresos_entidades.py), su tema
Egresos:

    https://www.inegi.org.mx/contenidos/programas/finanzas/datosabiertos/
        conjunto_de_datos_efipem_estatal_csv.zip
        (bajado el 03-11-2026; SHA-256 c8ace2050ce22b6f88e52f36066e8d57d30dda245d725fbee1ecdd5b0560446c)
    archivo efipem_estatal_anual_tr_cifra_2024.csv, TEMA = Egresos, cifras definitivas

Qué se toma y cómo (pesos de 2024, tal como los publica el INEGI):

- egr2024  = «Total de egresos». Oficial.
- invPub   = capítulo «Inversión pública»: la obra que el gobierno del estado
  contrata o hace por su cuenta (en bienes de dominio público, en bienes
  propios y proyectos productivos). Oficial.
- invInfra = subpartida «Instituciones y programas de infraestructura», dentro
  de las transferencias: lo que el gobierno le pasa a sus organismos de obra
  (juntas de caminos, comisiones de agua, institutos de infraestructura).
  Oficial. No es todo obra: con eso también pagan su nómina y su operación.
  Por eso no se suma a invPub.

El punto ciego: en varios estados lo que se va a esos organismos es mayor que
la obra directa, así que el capítulo de inversión pública, solo, hace ver
como «sin obra» a un estado que la hace por medio de sus organismos.

La Ciudad de México no figura en el conjunto estatal: sus tres campos quedan
en nulo, con su pendiente.

Antes de escribir, comprueba que la inversión pública sea la suma de sus tres
conceptos. Con --csv <archivo> coteja además la tabla contra el archivo del
INEGI y que en cada entidad los capítulos sumen al peso el total de egresos.
Idempotente.
    python3 herramientas/anclar_egresos_entidades.py
    python3 herramientas/anclar_egresos_entidades.py --csv efipem_estatal_anual_tr_cifra_2024.csv
"""
import csv
import collections
import json
import pathlib
import re
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'auditor' / 'js' / 'audit-database.js'

# (clave INEGI, total de egresos, inversión pública, obra en bienes de dominio
#  público, obra en bienes propios, proyectos productivos y acciones de
#  fomento, transferencias a instituciones y programas de infraestructura)
EGRESOS = {
    'AGS': ('01', 35089927606, 1254633850, 972272880, 282360970, 0, 1152165643),
    'BC': ('02', 92095983118, 2318083833, 1257231030, 1060852803, 0, 1437934048),
    'BCS': ('03', 26417113629, 1157208779, 1150270472, 0, 6938307, 727038090),
    'CAM': ('04', 28284368911, 1144862880, 635807373, 509055507, 0, 216551576),
    'COAH': ('05', 72937320498, 3437226803, 3284836068, 143533131, 8857604, 412700859),
    'COL': ('06', 24612820092, 182845084, 144667353, 38177731, 0, 91289188),
    'CHIS': ('07', 136890972675, 3631579650, 3208750639, 422829011, 0, 5218721718),
    'CHIH': ('08', 108075083654, 1777556350, 1411161434, 366394916, 0, 5182930661),
    'DGO': ('10', 51191133777, 1104946038, 1018786338, 86159700, 0, 521610548),
    'GTO': ('11', 133341859020, 4589814646, 3649197893, 940616753, 0, 571252295),
    'GRO': ('12', 93437249551, 1723646684, 1700369750, 23276934, 0, 2685674104),
    'HGO': ('13', 71736069673, 4311646967, 3808205997, 503440970, 0, 1622287990),
    'JAL': ('14', 172339654567, 10212139672, 9598889147, 0, 613250525, 5114558458),
    'MÉX': ('15', 400452116981, 6279697706, 6279697706, 0, 0, 16968761830),
    'MICH': ('16', 104630740231, 3825205064, 3801877544, 23327520, 0, 2141413842),
    'MOR': ('17', 41428569362, 496566739, 0, 495626884, 939855, 1083096285),
    'NAY': ('18', 33604752344, 1166689699, 767853755, 398835944, 0, 480749661),
    'NL': ('19', 159261257459, 5338968720, 2987595989, 2351372731, 0, 8237367654),
    'OAX': ('20', 121567900693, 2172306782, 1551028874, 3501384, 617776524, 4032331902),
    'PUE': ('21', 135347841154, 12072380930, 5333023363, 6739357567, 0, 2597718235),
    'QRO': ('22', 62411488566, 3519418788, 3519418788, 0, 0, 5444564235),
    'QROO': ('23', 68207027056, 458237402, 318339923, 139897479, 0, 1260293111),
    'SLP': ('24', 66107505192, 5795185979, 3089172256, 85071076, 2620942647, 982127652),
    'SIN': ('25', 79005554998, 4190249619, 2067889644, 0, 2122359975, 2275152835),
    'SON': ('26', 95810703169, 2348052175, 2295358852, 52693323, 0, 5772398850),
    'TAB': ('27', 67274723427, 1637471176, 1135114472, 502356704, 0, 1473026283),
    'TAM': ('28', 96791364385, 2719377491, 2089132973, 471756823, 158487695, 537262798),
    'TLAX': ('29', 30422325823, 1570787561, 508983560, 1061804001, 0, 401421248),
    'VER': ('30', 173564225837, 3433274568, 2246423124, 1186851444, 0, 2933246071),
    'YUC': ('31', 55482186826, 126748041, 126748041, 0, 0, 3432445951),
    'ZAC': ('32', 42554817284, 525133830, 318608068, 206525762, 0, 473332647),
}

SIN_FUENTE = ['CDMX']
MOTIVO_CDMX = 'La Ciudad de México no figura en la estadística estatal del INEGI; su cifra sigue sin documento citado'
CAMPOS = ('egr2024', 'invPub', 'invInfra')


def mdp(p):
    return round(p / 1e6, 1)


def coteja_csv(ruta):
    E = collections.defaultdict(collections.Counter)
    for x in csv.DictReader(open(ruta, encoding='utf-8-sig')):
        if x['TEMA'] == 'Egresos' and x['ANIO'] == '2024':
            E[x['CVE_ENT']][(x['CATEGORIA'], x['DESCRIPCION_CATEGORIA'])] += int(x['VALOR'])
    for abbr, (cve, tot, inv, dom, prop, pp, infra) in EGRESOS.items():
        v = E[cve]
        cap = sum(n for (c, _), n in v.items() if c == 'Capítulo')
        if v[('Tema', 'Total de egresos')] != tot or cap != tot:
            sys.exit('%s: el total de egresos no cuadra con el archivo o con sus capítulos' % abbr)
        if (v[('Capítulo', 'Inversión pública')], v[('Concepto', 'Obra pública en bienes de dominio público')], v[('Concepto', 'Obra pública en bienes propios')],
                v[('Concepto', 'Proyectos productivos y acciones de fomento')], v[('Subpartida Genérica', 'Instituciones y programas de infraestructura')]) != (inv, dom, prop, pp, infra):
            sys.exit('%s: la tabla no coincide con el archivo del INEGI' % abbr)
    if len(E) != len(EGRESOS):
        sys.exit('el archivo trae %d entidades y la tabla %d' % (len(E), len(EGRESOS)))
    print('cotejo contra el archivo: %d entidades, capítulos y tabla al peso' % len(EGRESOS))


def campos_nuevos():
    base = {'ref': 'ref-inegi-efipem-estatal', 'anio': 2024, 'sinFuente': SIN_FUENTE, 'motivo': MOTIVO_CDMX}
    return {
        'egr2024': dict(base, estado='oficial', fuente='Total de egresos del gobierno del estado en 2024. INEGI, finanzas públicas estatales, cifras definitivas'),
        'invPub': dict(base, estado='oficial', fuente='Capítulo «Inversión pública» de 2024: la obra que el gobierno del estado contrató o hizo por su cuenta. INEGI, finanzas públicas estatales, cifras definitivas'),
        'invInfra': dict(base, estado='oficial', fuente='Subpartida «Instituciones y programas de infraestructura» de 2024, dentro de las transferencias: lo que el gobierno le pasó a sus organismos de obra, que con eso también pagan su nómina y su operación. INEGI, finanzas públicas estatales, cifras definitivas'),
    }


def main():
    if '--csv' in sys.argv:
        coteja_csv(sys.argv[sys.argv.index('--csv') + 1])
    valores = {}
    for abbr, (cve, tot, inv, dom, prop, pp, infra) in EGRESOS.items():
        if dom + prop + pp != inv:
            sys.exit('%s: la inversión pública no es la suma de sus conceptos' % abbr)
        valores[abbr] = {'egr2024': mdp(tot), 'invPub': mdp(inv), 'invInfra': mdp(infra)}
    b = BASE.read_bytes().decode('utf-8')
    ini = b.index('\r\n  "estados": [')
    cambios = 0
    for abbr in list(valores) + SIN_FUENTE:
        a = b.index('"abbr": "%s",' % abbr, ini)
        z = b.index('"gobernador"', a)
        seg = b[a:z]
        nseg = re.sub(r'\r\n\s*"(?:%s)": [\w.]+,' % '|'.join(CAMPOS), '', seg)
        m = re.search(r'("federal2024": [\w.]+,)(\r\n\s*)', nseg)
        if not m:
            sys.exit('%s: no encuentro federal2024' % abbr)
        extra = ''.join('%s"%s": %s,' % (m.group(2), k, json.dumps(valores[abbr][k]) if abbr in valores else 'null') for k in CAMPOS)
        nseg = nseg[:m.end(1)] + extra + nseg[m.end(1):]
        if nseg != seg:
            b = b[:a] + nseg + b[z:]
            cambios += 1
    a = b.index('  "fiscalEntidades": ')
    i = a + len('  "fiscalEntidades": ')
    fe, fin = json.JSONDecoder().raw_decode(b, i)
    fe['campos'].update(campos_nuevos())
    bloque = json.dumps(fe, ensure_ascii=False, indent=2).replace('\n', '\r\n  ')
    b = b[:i] + bloque + b[fin:]
    viejo = 'De ella salen la recaudación propia, los convenios (recursos federales reasignados) y el porcentaje de dependencia federal de 31 entidades en 2024.'
    nuevo = 'De ella salen la recaudación propia, los convenios (recursos federales reasignados), el porcentaje de dependencia federal y la inversión pública de 31 entidades en 2024.'
    b = b.replace(viejo, nuevo)
    BASE.write_bytes(b.encode('utf-8'))
    print('entidades: %d renglones actualizados' % cambios)
    for abbr, c in valores.items():
        print('  %-5s egresos %10.1f  inversión %9.1f  a organismos de obra %9.1f' % (abbr, c['egr2024'], c['invPub'], c['invInfra']))


if __name__ == '__main__':
    main()
