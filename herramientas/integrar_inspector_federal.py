#!/usr/bin/env python3
"""Arma el nivel federal del Modo Inspector con datos oficiales.

El nivel federal tenía ocho expedientes con cifras sin documento y se retiró
el 27-09-2026. Aquí se reconstruye, ente por ente, con tres fuentes:

- Cuenta Pública 2025 (SHCP, datos abiertos): aprobado original, modificado,
  devengado, pagado y ejercido de cada ramo. Dice si el ente rindió su cuenta
  y cuánto se apartó de lo que aprobó la Cámara de Diputados.
- Avance del gasto al segundo trimestre de 2026 (SHCP, datos abiertos):
  aprobado, modificado, lo calendarizado de enero a junio y lo pagado.
- Matriz de Datos Básicos de la Cuenta Pública 2024 (ASF): auditorías,
  acciones, pliegos y montos por aclarar del sector. No se copia aquí: el
  motor la suma en vivo desde `cuenta_publica_asf.cp2024`, con los nombres de
  sector que cada ente declara en `asfSectores`.

Los dos CSV se verifican contra la huella SHA-256 que ya cita la base
(`poderes.fuentes`). Si no coincide, no escribe nada.

    python3 herramientas/integrar_inspector_federal.py CP2025.csv AVANCE_2T_2026.csv

Idempotente.
"""
import collections
import csv
import hashlib
import io
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from integrar_glosario_modulos import _cuerpo  # noqa: E402

BASE = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'auditor' / 'js' / 'audit-database.js'
SHA_CP = '973aab21969233bdfad3c4f87ccd467ab92421ea5c2cd249644c0bf2f7f1d0c0'
SHA_AV = 'faa3a3de57981aa117828d2569aa5c8144db11e3f8d290e68d97aaf73467c511'
HOST = 'https://www.transparenciapresupuestaria.gob.mx'
URL_CP = HOST + '/work/models/PTP/DatosAbiertos/BD_Cuenta_Publica/CSV/cuenta_publica_2025_gf_ecd_epe.csv'
URL_AV = HOST + '/work/models/PTP/DatosAbiertos/Bases_de_datos_presupuesto/CSV/pef_ac01_avance_2t_2026.csv'

CAPITULOS = {
    '1': 'Servicios personales', '2': 'Materiales y suministros', '3': 'Servicios generales',
    '4': 'Transferencias, asignaciones, subsidios y otras ayudas',
    '5': 'Bienes muebles, inmuebles e intangibles', '6': 'Inversión pública',
    '7': 'Inversiones financieras y otras provisiones', '8': 'Participaciones y aportaciones',
    '9': 'Deuda pública',
}

# (ramo, id, nombre corto, icono, tipo, sectores de la Matriz ASF, expedientes)
# Quedan fuera los ramos generales (19, 23, 24, 25, 28, 30, 33, 34): son
# bolsas que se transfieren, no autoridades que ejerzan; y el 47, que agrupa
# entidades distintas bajo un mismo número.
ENTES = [
    ('1', 'legislativo', 'Poder Legislativo', '🏛️', 'Poder de la Unión', ['Poder Legislativo'], []),
    ('3', 'judicial', 'Poder Judicial de la Federación', '⚖️', 'Poder de la Unión', ['Poder Judicial'], []),
    ('2', 'presidencia', 'Oficina de la Presidencia de la República', '🦅', 'Ramo administrativo', [], []),
    ('4', 'gobernacion', 'Secretaría de Gobernación', '🏢', 'Ramo administrativo', ['Gobernación'], []),
    ('5', 'sre', 'Secretaría de Relaciones Exteriores', '🌐', 'Ramo administrativo', ['Relaciones Exteriores'], []),
    ('6', 'shcp', 'Secretaría de Hacienda y Crédito Público', '💰', 'Ramo administrativo', ['Hacienda y Crédito Público'], ['deuda-estados']),
    ('7', 'defensa', 'Secretaría de la Defensa Nacional', '🪖', 'Ramo administrativo', ['Defensa Nacional'], ['aifa', 'defensa']),
    ('8', 'agricultura', 'Secretaría de Agricultura y Desarrollo Rural', '🌾', 'Ramo administrativo', ['Agricultura y Desarrollo Rural'], ['segalmex']),
    ('9', 'sict', 'Secretaría de Infraestructura, Comunicaciones y Transportes', '🛣️', 'Ramo administrativo', ['Infraestructura, Comunicaciones y Transportes'], ['tren-toluca']),
    ('10', 'economia', 'Secretaría de Economía', '📈', 'Ramo administrativo', ['Economía'], []),
    ('11', 'sep', 'Secretaría de Educación Pública', '📚', 'Ramo administrativo', ['Educación Pública'], []),
    ('12', 'salud', 'Secretaría de Salud', '🏥', 'Ramo administrativo', ['Salud'], ['salud', 'birmex']),
    ('13', 'marina', 'Secretaría de Marina', '⚓', 'Ramo administrativo', ['Marina'], []),
    ('14', 'stps', 'Secretaría del Trabajo y Previsión Social', '👷', 'Ramo administrativo', ['Trabajo y Previsión Social'], []),
    ('15', 'sedatu', 'Secretaría de Desarrollo Agrario, Territorial y Urbano', '🏘️', 'Ramo administrativo', ['Desarrollo Agrario, Territorial y Urbano'], []),
    ('16', 'semarnat', 'Secretaría de Medio Ambiente y Recursos Naturales', '🌳', 'Ramo administrativo', ['Medio Ambiente y Recursos Naturales'], ['cuchillo-ii']),
    ('18', 'energia', 'Secretaría de Energía', '⚡', 'Ramo administrativo', ['Energía'], []),
    ('20', 'bienestar', 'Secretaría de Bienestar', '🤝', 'Ramo administrativo', ['Bienestar'], []),
    ('21', 'turismo', 'Secretaría de Turismo', '🏖️', 'Ramo administrativo', ['Turismo'], ['tren-maya']),
    ('22', 'ine', 'Instituto Nacional Electoral', '🗳️', 'Órgano autónomo', ['Instituto Nacional Electoral'], []),
    ('27', 'anticorrupcion', 'Secretaría Anticorrupción y Buen Gobierno', '🔎', 'Ramo administrativo', [], []),
    ('31', 'tribunales-agrarios', 'Tribunales Agrarios', '📜', 'Tribunal administrativo', ['Tribunales Agrarios'], []),
    ('32', 'tfja', 'Tribunal Federal de Justicia Administrativa', '📜', 'Tribunal administrativo', ['Tribunal Federal de Justicia Administrativa'], []),
    ('35', 'cndh', 'Comisión Nacional de los Derechos Humanos', '🕊️', 'Órgano autónomo', ['Comisión Nacional de los Derechos Humanos'], []),
    ('36', 'sspc', 'Secretaría de Seguridad y Protección Ciudadana', '🚓', 'Ramo administrativo', ['Seguridad y Protección Ciudadana'], []),
    ('37', 'cjef', 'Consejería Jurídica del Ejecutivo Federal', '📑', 'Ramo administrativo', [], []),
    ('38', 'secihti', 'Secretaría de Ciencia, Humanidades, Tecnología e Innovación', '🔬', 'Ramo administrativo', ['Humanidades, Ciencias, Tecnologías e Innovación'], []),
    ('40', 'inegi', 'Instituto Nacional de Estadística y Geografía', '📊', 'Órgano autónomo', ['Información Nacional Estadística y Geográfica'], []),
    ('41', 'cofece', 'Comisión Federal de Competencia Económica', '⚖️', 'Órgano autónomo (extinto en 2025)', [], []),
    ('43', 'ift', 'Instituto Federal de Telecomunicaciones', '📡', 'Órgano autónomo (extinto en 2025)', [], []),
    ('44', 'inai', 'Instituto Nacional de Transparencia (INAI)', '🔓', 'Órgano autónomo (extinto en 2025)', ['Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales'], []),
    ('45', 'cre', 'Comisión Reguladora de Energía', '🔌', 'Órgano regulador', [], []),
    ('46', 'cnh', 'Comisión Nacional de Hidrocarburos', '🛢️', 'Órgano regulador', [], []),
    ('48', 'cultura', 'Secretaría de Cultura', '🎭', 'Ramo administrativo', ['Cultura'], []),
    ('49', 'fgr', 'Fiscalía General de la República', '🏛️', 'Órgano autónomo', [], []),
    ('50', 'imss', 'Instituto Mexicano del Seguro Social', '🩺', 'Entidad de control directo', ['Instituto Mexicano del Seguro Social'], []),
    ('51', 'issste', 'ISSSTE', '🩺', 'Entidad de control directo', ['Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado'], []),
    ('52', 'pemex', 'Petróleos Mexicanos', '🛢️', 'Empresa pública del Estado', ['Petróleos Mexicanos'], ['dos-bocas']),
    ('53', 'cfe', 'Comisión Federal de Electricidad', '💡', 'Empresa pública del Estado', ['Comisión Federal de Electricidad'], []),
    ('54', 'mujeres', 'Secretaría de las Mujeres', '♀️', 'Ramo administrativo', [], []),
    ('55', 'atdt', 'Agencia de Transformación Digital y Telecomunicaciones', '💻', 'Ramo administrativo', [], []),
]

REF_NUEVAS = [
    {
        'num': 109,
        'id': 'ref-shcp-cp2025-datos',
        'categoria': 'fuentes_oficiales',
        'categoria_nombre': 'Fuentes Oficiales & Datos Abiertos',
        'cita_apa': 'Secretaría de Hacienda y Crédito Público. (2026). Cuenta Pública 2025: base de datos abierta de ramos administrativos, generales y autónomos, entidades de control directo y empresas productivas del Estado [archivo CSV]. Transparencia Presupuestaria.',
        'url': URL_CP,
        'descripcion': 'Renglón por renglón, lo que cada ramo tenía aprobado, lo que se le modificó, lo que devengó, pagó y ejerció en 2025. De aquí sale el nivel federal del Modo Inspector: si el ente rindió su cuenta, cuánto se apartó de lo que aprobó la Cámara de Diputados y si sus propias cifras cuadran. Huella SHA-256 del archivo consultado: ' + SHA_CP + '.',
    },
    {
        'num': 110,
        'id': 'ref-shcp-avance-2t2026',
        'categoria': 'fuentes_oficiales',
        'categoria_nombre': 'Fuentes Oficiales & Datos Abiertos',
        'cita_apa': 'Secretaría de Hacienda y Crédito Público. (2026). Presupuesto de Egresos 2026: avance del gasto (AC01) al segundo trimestre [archivo CSV]. Transparencia Presupuestaria.',
        'url': URL_AV,
        'descripcion': 'Aprobado, modificado, calendario mensual y pagado de cada ramo al 30 de junio de 2026. Permite ver si un ente va al ritmo de lo que él mismo calendarizó. Huella SHA-256 del archivo consultado: ' + SHA_AV + '.',
    },
]


def num(x):
    x = (x or '').strip().replace(',', '')
    return float(x) if x not in ('', '-') else 0.0


def leer(ruta, sha, codif):
    datos = pathlib.Path(ruta).read_bytes()
    h = hashlib.sha256(datos).hexdigest()
    if h != sha:
        sys.exit('%s: la huella no coincide con la que cita la base (%s)' % (ruta, h))
    return datos.decode(codif)


def mdp(p):
    return round(p / 1e6, 1)


def cuenta_publica(ruta):
    r = csv.reader(io.StringIO(leer(ruta, SHA_CP, 'latin-1')))
    cab = [c.strip() for c in next(r)]
    i = {c: cab.index(c) for c in cab}
    ramos = {e[0] for e in ENTES}
    tot = collections.defaultdict(lambda: [0.0] * 5)
    cap = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0]))
    for f in r:
        ramo = f[i['R']].strip()
        if ramo not in ramos:
            continue
        v = [num(f[i[c]]) for c in ('Original_Bruto', 'Modificado_Bruto', 'Devengado', 'Pagado', 'Ejercido_Bruto')]
        t = tot[ramo]
        for k in range(5):
            t[k] += v[k]
        c = cap[ramo][f[i['PTDA']].strip()[:1]]
        c[0] += v[1]
        c[1] += v[4]
    salida = {}
    for ramo, t in tot.items():
        exceso = [{'cap': k + '000', 'concepto': CAPITULOS.get(k, k), 'modificado': mdp(m), 'ejercido': mdp(e)}
                  for k, (m, e) in sorted(cap[ramo].items()) if mdp(e) - mdp(m) >= 0.1]
        salida[ramo] = {'original': mdp(t[0]), 'modificado': mdp(t[1]), 'devengado': mdp(t[2]),
                        'pagado': mdp(t[3]), 'ejercido': mdp(t[4])}
        if exceso:
            salida[ramo]['capitulosSobreModificado'] = exceso
    return salida


def avance(ruta):
    r = csv.DictReader(io.StringIO(leer(ruta, SHA_AV, 'utf-8-sig')))
    ramos = {e[0] for e in ENTES}
    tot = collections.defaultdict(lambda: [0.0] * 4)
    for f in r:
        ramo = f['ID_RAMO'].strip()
        if ramo not in ramos:
            continue
        t = tot[ramo]
        t[0] += num(f['MONTO_APROBADO'])
        t[1] += num(f['MONTO_MODIFICADO'])
        t[2] += num(f['MONTO_MODIFICADO_MENSUAL'])
        t[3] += num(f['MONTO_PAGADO'])
    return {ramo: {'aprobado': mdp(t[0]), 'modificado': mdp(t[1]), 'calendarioAlCorte': mdp(t[2]), 'pagado': mdp(t[3])}
            for ramo, t in tot.items()}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    cp = cuenta_publica(sys.argv[1])
    av = avance(sys.argv[2])
    entes = []
    for ramo, ident, nombre, icono, tipo, sectores, exps in ENTES:
        if ramo not in cp:
            sys.exit('ramo %s sin renglones en la Cuenta Pública' % ramo)
        entes.append({'id': ident, 'ramo': ramo.zfill(2), 'nombre': nombre, 'icono': icono, 'tipo': tipo,
                      'cp2025': cp[ramo], 'av2026': av.get(ramo), 'asfSectores': sectores, 'expedientes': exps})
    bloque = {
        'consulta': '27 de septiembre de 2026',
        'nota': 'Nivel federal del Modo Inspector. Cifras en millones de pesos, sumadas por ramo desde los archivos abiertos de Hacienda; lo de la ASF se suma en el motor desde la Matriz de Datos Básicos de la Cuenta Pública 2024.',
        'fuentes': {
            'cp2025': {'ref': 'ref-shcp-cp2025-datos', 'corto': 'SHCP, Cuenta Pública 2025, datos abiertos', 'url': URL_CP, 'sha256': SHA_CP},
            'av2026': {'ref': 'ref-shcp-avance-2t2026', 'corto': 'SHCP, avance del gasto al 2.º trimestre de 2026', 'url': URL_AV, 'sha256': SHA_AV, 'corte': '30 de junio de 2026'},
            'asf2024': {'ref': 'ref-asf-mdb2024', 'corto': 'ASF, Matriz de Datos Básicos CP 2024 (feb. 2026)'},
        },
        'entes': entes,
    }
    b = BASE.read_bytes().decode('utf-8')
    texto = '  "inspector_federal": ' + json.dumps(bloque, ensure_ascii=False, indent=1).replace('\n', '\r\n  ') + ','
    if '"inspector_federal":' in b:
        a = b.index('  "inspector_federal": ')
        z = b.index('\r\n  "', a + 10)
        b = b[:a] + texto + b[z:]
    else:
        a = b.index('\r\n  "estados": [')
        b = b[:a] + '\r\n' + texto + b[a:]
    fichas = 0
    for ref in reversed(REF_NUEVAS):
        if '"id": "%s"' % ref['id'] not in b:
            ancla = b.index('"id": "ref-inegi-efipem-estatal"')
            corte = b.index('\r\n    }', ancla) + len('\r\n    }')
            b = b[:corte] + ',\r\n' + _cuerpo(ref) + b[corte:]
            fichas += 1
    BASE.write_bytes(b.encode('utf-8'))
    print('inspector federal: %d entes; %d fichas nuevas' % (len(entes), fichas))
    for e in entes:
        c = e['cp2025']
        print('  %-22s orig %12.1f  ejer %12.1f  %+6.1f%%' % (e['id'], c['original'], c['ejercido'],
                                                         (c['ejercido'] / c['original'] - 1) * 100 if c['original'] else 0))


if __name__ == '__main__':
    main()
