"""Ancla la recaudación propia, los convenios y la dependencia federal de las
entidades a la estadística de finanzas públicas estatales del INEGI.

Los tres campos venían en la base como cifras redondas sin documento. La
fuente que desciende a cada gobierno estatal es la «Estadística de Finanzas
Públicas Estatales y Municipales» (EFIPEM), conjunto de datos estatal, que el
INEGI arma con la cuenta pública de cada entidad. Se usa el ejercicio 2024,
el último con cifras definitivas (el de 2025 es preliminar):

    https://www.inegi.org.mx/contenidos/programas/finanzas/datosabiertos/
        conjunto_de_datos_efipem_estatal_csv.zip   (versión del 13-08-2026)
    archivo efipem_estatal_anual_tr_cifra_2024.csv, TEMA = Ingresos

Qué se toma y cómo:

- convenios  = concepto «Recursos federales reasignados», dentro del capítulo
  de aportaciones federales. Se lee tal cual: oficial.
- recaudacionPropia = impuestos + cuotas y aportaciones de seguridad social +
  contribuciones de mejoras + derechos + productos + aprovechamientos. Es una
  suma de capítulos publicados: derivado.
- dep = (participaciones federales + aportaciones federales) entre el total
  de ingresos sin el financiamiento, por cien. Se quita la deuda del
  denominador porque un préstamo no es autonomía: con ella, Quintana Roo, que
  en 2024 contrató $19,306.8 mdp, saldría como la entidad menos dependiente.
  Derivado.
- federal2024 = participaciones + aportaciones federales del mismo año, para
  que la razón «por cada peso propio recibe» compare cifras de un solo año.

La Ciudad de México no figura en el conjunto estatal en ningún año; sus tres
campos se quedan como estaban y con el chip pendiente, y federal2024 en nulo.

Antes de escribir, comprueba que en cada entidad los capítulos sumen al peso el
total de ingresos. Idempotente.
    python3 herramientas/anclar_ingresos_entidades.py
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from integrar_glosario_modulos import _cuerpo  # noqa: E402

BASE = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'js' / 'audit-database.js'

# Pesos de 2024, tal como los publica el INEGI:
# (clave, total de ingresos, impuestos, cuotas de seguridad social,
#  contribuciones de mejoras, derechos, productos, aprovechamientos,
#  participaciones federales, aportaciones federales, otros ingresos,
#  financiamiento, recursos federales reasignados)
INGRESOS = {
    'AGS': ('01', 35089927606, 2215854330, 0, 0, 1062930927, 136817687, 616646847, 13763599439, 16738284872, 0, 555793504, 2352900557),
    'BC': ('02', 92095983118, 12880138034, 0, 22844671, 3701574310, 667188014, 245028228, 39542369465, 33911840396, 0, 1125000000, 8978277953),
    'BCS': ('03', 26417113629, 2389405801, 0, 0, 859624328, 27033731, 91913928, 9525286956, 12973848885, 0, 550000000, 2917463416),
    'CAM': ('04', 28284368911, 2604028621, 0, 0, 693457826, 668582218, 144518311, 10231988456, 13941793479, 0, 0, 3215653839),
    'COAH': ('05', 72937320498, 6916823689, 0, 17058859, 5340846947, 337963896, 78445658, 28218608733, 30027572716, 0, 2000000000, 5908338991),
    'COL': ('06', 24612820092, 1301575109, 0, 0, 574978909, 77553236, 60569673, 7540284594, 11757638082, 0, 3300220489, 3634812374),
    'CHIS': ('07', 136890972675, 2746172170, 1835943868, 0, 1989875777, 1181781466, 1901600728, 49559841243, 74277972228, 212893486, 3184891709, 11582671066),
    'CHIH': ('08', 108075083654, 10261425938, 0, 0, 11203877703, 331128450, 6313777945, 39248945555, 36862017452, 0, 3853910611, 6858658577),
    'DGO': ('10', 51191133777, 4103336240, 0, 0, 1613536828, 194296576, 464400611, 16210761396, 23750237147, 0, 4854564979, 4360064958),
    'GTO': ('11', 133341859020, 11011110884, 0, 0, 2632564909, 3378587639, 2084162355, 56471860033, 49994191607, 0, 7769381593, 9110699844),
    'GRO': ('12', 93437249551, 1991319862, 0, 0, 398630270, 137290089, 19924115, 28663037202, 58290360684, 6687329, 3930000000, 10727250340),
    'HGO': ('13', 71736069673, 2910754408, 0, 52522997, 1353170228, 1436672974, 437622355, 26557401529, 38987925182, 0, 0, 5995425237),
    'JAL': ('14', 172339654567, 13716411396, 0, 0, 5677914086, 947514826, 2806024708, 84880463270, 62671941151, 0, 1639385130, 13581084704),
    'MÉX': ('15', 400452116981, 31207428133, 28271610509, 764185923, 16337100535, 4685811519, 3088849831, 162137140389, 120653940632, 17648366967, 15657682543, 18956557648),
    'MICH': ('16', 104630740231, 3689840089, 0, 53510595, 3219640271, 426443372, 630923291, 41419487648, 54880764745, 0, 310130220, 13359692591),
    'MOR': ('17', 41428569362, 1169133233, 0, 0, 1549771500, 72525437, 282140680, 16604037404, 20947245454, 99436257, 704279397, 3968228258),
    'NAY': ('18', 33604752344, 1956160967, 0, 0, 824716933, 36075177, 135063844, 12389195556, 18145343947, 118195920, 0, 5825020083),
    'NL': ('19', 159261257459, 20453096363, 0, 0, 2493341000, 505763000, 8260386096, 68536146000, 46582525000, 0, 12430000000, 11148196000),
    'OAX': ('20', 121567900693, 2141687266, 0, 0, 2684562621, 1140111057, 746384332, 36527750028, 66273671548, 0, 12053733841, 8151896989),
    'PUE': ('21', 135347841154, 7541099629, 0, 0, 3291668669, 1383079035, 541758862, 55822848530, 61689122429, 5078264000, 0, 12494407654),
    'QRO': ('22', 62411488566, 7200733909, 0, 0, 2734257057, 1036905400, 2617891442, 25941926790, 20820742203, 0, 2059031765, 3715120085),
    'QROO': ('23', 68207027056, 10086781441, 0, 0, 2321969669, 550424625, 649315897, 18826641922, 16465127689, 0, 19306765813, 2986186384),
    'SLP': ('24', 66107505192, 3542996684, 0, 0, 2220491590, 262244169, 27426000, 25312350542, 33950389367, 471602000, 320004840, 7115056554),
    'SIN': ('25', 79005554998, 3859432095, 0, 0, 4957253719, 232152278, 2682499174, 29924475850, 37349741882, 0, 0, 12684258993),
    'SON': ('26', 95810703169, 6551439878, 0, 0, 3181140732, 156828353, 899881085, 31279110098, 34201617764, 10537463486, 9003221773, 13315869192),
    'TAB': ('27', 67274723427, 3071323258, 0, 0, 1631428951, 428876563, 810446906, 32165804449, 29166843300, 0, 0, 9165055455),
    'TAM': ('28', 96791364385, 6984595420, 0, 0, 3331765359, 717238833, 1214483704, 33187154238, 36309865276, 0, 15046261555, 8455626463),
    'TLAX': ('29', 30422325823, 1019913323, 0, 0, 682063967, 410925330, 15315671, 12375894105, 15781963871, 136249556, 0, 2639384326),
    'VER': ('30', 173564225837, 7462294357, 0, 0, 3191302201, 1628758801, 361856692, 71531101565, 83365736877, 3390028440, 2633146904, 11915624377),
    'YUC': ('31', 55482186826, 4030083064, 0, 0, 2146970185, 302256441, 274462748, 22376137404, 24719276984, 0, 1633000000, 6018788010),
    'ZAC': ('32', 42554817284, 2197349032, 0, 16645230, 1263696848, 214031598, 528325857, 14804833710, 23483726470, 0, 46208539, 7032009571),
}

REF = {
    'num': 108,
    'id': 'ref-inegi-efipem-estatal',
    'categoria': 'estadistica_oficial',
    'categoria_nombre': 'Estadística Oficial del Estado Mexicano',
    'cita_apa': 'Instituto Nacional de Estadística y Geografía. (2026). Estadística de Finanzas Públicas Estatales y Municipales (EFIPEM). Conjunto de datos estatal, 1989-2025; ejercicio 2024, cifras definitivas. INEGI (México).',
    'url': 'https://www.inegi.org.mx/programas/finanzas/',
    'descripcion': 'La misma estadística del padrón municipal, en su conjunto estatal: lo que ingresó y gastó cada gobierno estatal, capítulo por capítulo, según su cuenta pública. De ella salen la recaudación propia, los convenios (recursos federales reasignados) y el porcentaje de dependencia federal de 31 entidades en 2024. La Ciudad de México no forma parte del conjunto estatal en ningún año.',
}

SIN_FUENTE = ['CDMX']
MOTIVO_CDMX = 'La Ciudad de México no figura en la estadística estatal del INEGI; su cifra sigue sin documento citado'


def mdp(p):
    return round(p / 1e6, 1)


def calcula(v):
    _, ing, imp, cuo, mej, der, prod, aprov, part, aport, otros, fin, reasig = v
    if imp + cuo + mej + der + prod + aprov + part + aport + otros + fin != ing:
        return None
    propia = imp + cuo + mej + der + prod + aprov
    return {
        'convenios': mdp(reasig),
        'recaudacionPropia': mdp(propia),
        'dep': round((part + aport) / (ing - fin) * 100, 1),
        'federal2024': mdp(part + aport),
    }


def campos_nuevos():
    return {
        'convenios': {'estado': 'oficial', 'ref': REF['id'], 'anio': 2024, 'sinFuente': SIN_FUENTE, 'motivo': MOTIVO_CDMX,
                      'fuente': 'Recursos federales reasignados en 2024 (convenios con dependencias federales), dentro de las aportaciones federales. INEGI, finanzas públicas estatales, cifras definitivas'},
        'recaudacionPropia': {'estado': 'derivado', 'ref': REF['id'], 'anio': 2024, 'sinFuente': SIN_FUENTE, 'motivo': MOTIVO_CDMX,
                              'fuente': 'Suma de 2024: impuestos, cuotas de seguridad social, contribuciones de mejoras, derechos, productos y aprovechamientos. INEGI, finanzas públicas estatales, cifras definitivas'},
        'dep': {'estado': 'derivado', 'ref': REF['id'], 'anio': 2024, 'sinFuente': SIN_FUENTE, 'motivo': MOTIVO_CDMX,
                'fuente': 'Participaciones más aportaciones federales, entre el total de ingresos de 2024 sin contar el financiamiento (deuda). INEGI, finanzas públicas estatales, cifras definitivas'},
        'federal2024': {'estado': 'derivado', 'ref': REF['id'], 'anio': 2024, 'sinFuente': SIN_FUENTE, 'motivo': MOTIVO_CDMX,
                        'fuente': 'Participaciones más aportaciones federales que la entidad registró como ingreso en 2024. INEGI, finanzas públicas estatales, cifras definitivas'},
    }


def main():
    valores = {}
    for abbr, v in INGRESOS.items():
        c = calcula(v)
        if c is None:
            sys.exit('%s: los capítulos no suman el total de ingresos' % abbr)
        valores[abbr] = c
    b = BASE.read_bytes().decode('utf-8')
    ini = b.index('\r\n  "estados": [')
    cambios = 0
    for abbr in list(valores) + SIN_FUENTE:
        a = b.index('"abbr": "%s",' % abbr, ini)
        z = b.index('"gobernador"', a)
        seg = b[a:z]
        nseg = seg
        if abbr in valores:
            for campo in ('convenios', 'recaudacionPropia', 'dep'):
                nseg = re.sub(r'"%s": [\d.]+,' % campo, '"%s": %s,' % (campo, json.dumps(valores[abbr][campo])), nseg, count=1)
        fed = json.dumps(valores[abbr]['federal2024']) if abbr in valores else 'null'
        if '"federal2024"' in nseg:
            nseg = re.sub(r'"federal2024": [\w.]+,', '"federal2024": %s,' % fed, nseg, count=1)
        else:
            nseg = re.sub(r'("dep": [\d.]+,)(\r\n\s*)', r'\1\2"federal2024": %s,\2' % fed, nseg, count=1)
        if nseg != seg:
            b = b[:a] + nseg + b[z:]
            cambios += 1

    a = b.index('  "fiscalEntidades": ')
    z = b.index('\r\n  "estados": [', a)
    fe = json.loads(b[a + len('  "fiscalEntidades": '):z].rstrip().rstrip(','))
    fe['campos'].update(campos_nuevos())
    fe['nota'] = ('Las cifras por entidad del Ramo 28 y del Ramo 33 salen de los anexos del acuerdo de distribución que Hacienda publica en el Diario Oficial. '
                  'Sumadas a los renglones que el acuerdo no asigna a ninguna entidad, cuadran al peso con el total aprobado de cada ramo. '
                  'La recaudación propia, los convenios y la dependencia federal salen de la estadística estatal del INEGI para 2024, el último año con cifras definitivas.')
    bloque = json.dumps(fe, ensure_ascii=False, indent=2)
    bloque = '  "fiscalEntidades": ' + bloque.replace('\n', '\r\n  ') + ','
    b = b[:a] + bloque + b[z:]

    fichas = 0
    if '"id": "%s"' % REF['id'] not in b:
        ancla = b.index('"id": "ref-dof-distribucion-2026-mod"')
        corte = b.index('\r\n    }', ancla) + len('\r\n    }')
        b = b[:corte] + ',\r\n' + _cuerpo(REF) + b[corte:]
        fichas = 1
    BASE.write_bytes(b.encode('utf-8'))
    print('entidades: %d renglones actualizados; %d ficha nueva' % (cambios, fichas))
    for abbr, c in valores.items():
        print('  %-5s propia %10.1f  convenios %9.1f  dep %5.1f' % (abbr, c['recaudacionPropia'], c['convenios'], c['dep']))


if __name__ == '__main__':
    main()
